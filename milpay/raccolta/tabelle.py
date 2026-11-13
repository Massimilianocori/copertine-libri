"""Legge le tabelle ufficiali della paga base mensile dei militari USA (Schedule 8 dell'ordine esecutivo annuale
"Adjustments of Certain Rates of Pay", pubblicato sul Federal Register) e scrive dati/paga_<anno>.json.

Uso (dalla radice del repository; servono tesseract, pdftotext e Pillow/numpy):
    python3 milpay/raccolta/tabelle.py            # 2026 (tabella del sito) e 2025 (solo per il controllo del +3,8 %)
    python3 milpay/raccolta/tabelle.py 2027       # quando esce l'ordine esecutivo nuovo (vedi NOTE.md)

Fonti: API del Federal Register (metadati e immagini originali delle tabelle, img.federalregister.gov) e PDF ufficiale
su govinfo.gov. Le tabelle dello Schedule 8 sono IMMAGINI nel Federal Register: nessun testo da copiare. Per questo ogni
cella viene letta tre volte in modo indipendente:
  A) riconoscimento ottico (tesseract) cella per cella sull'immagine originale, scala 0,4;
  B) lo stesso alla scala 0,5 (ingrandimento diverso = lettura diversa);
  C) il livello di testo che GPO ha messo nel PDF ufficiale (un riconoscimento fatto da GPO, non da noi).
Regola: A e B devono coincidere su TUTTE le celle; C, dove è leggibile, deve coincidere con A. Ogni disaccordo ferma lo
script con l'elenco delle celle da guardare a occhio. Il JSON scritto registra per ogni anno i conteggi delle tre letture.
Nessun blocco aggirato: dfas.mil e militarypay.defense.gov rispondono 403 al server e non vengono usati.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from datetime import date
from pathlib import Path

import numpy as np
from PIL import Image

RADICE = Path(__file__).resolve().parents[1]
CACHE = RADICE / "cache" / "fonti"
DATI = RADICE / "dati"
INCHIOSTRO_TRATTINO = 400  # pixel neri: un trattino ne ha poche centinaia, una cifra intera migliaia
UA = {"User-Agent": "rete-siti-dati/1.0 (lettura delle tabelle ufficiali)"}

COLONNE = ["2 or less", "Over 2", "Over 3", "Over 4", "Over 6", "Over 8", "Over 10", "Over 12", "Over 14", "Over 16", "Over 18",
           "Over 20", "Over 22", "Over 24", "Over 26", "Over 28", "Over 30", "Over 32", "Over 34", "Over 36", "Over 38", "Over 40"]
GRADI = {
    "O": ["O-10", "O-9", "O-8", "O-7", "O-6", "O-5", "O-4", "O-3", "O-2", "O-1"],
    "OE": ["O-3E", "O-2E", "O-1E"],
    "W": ["W-5", "W-4", "W-3", "W-2", "W-1"],
    "E": ["E-9", "E-8", "E-7", "E-6", "E-5", "E-4", "E-3", "E-2", "E-1", "E-1<4"],
}

# Disposizione delle immagini dello Schedule 8: per ogni immagine, le tabelle che contiene (categoria, metà delle colonne).
ANNI = {
    2026: {"documento": "2025-23844", "griglia": True, "rigoroso": True,
           "immagini": {"ED23DE25.104": [("O", 0)], "ED23DE25.105": [("OE", 0), ("W", 0)], "ED23DE25.106": [("O", 1)],
                        "ED23DE25.107": [("OE", 1), ("W", 1)], "ED23DE25.108": [("E", 0)], "ED23DE25.109": [("E", 1)]}},
    # 2025: solo per il controllo dell'aumento (le righe E-1…E-4 sono cambiate ad aprile 2025 e non si confrontano)
    2025: {"documento": "2024-31466", "griglia": False, "rigoroso": False,
           "immagini": {"ED30DE24.010": [("O", 0), ("OE", 0), ("W", 0)], "ED30DE24.011": [("O", 1), ("OE", 1), ("W", 1)],
                        "ED30DE24.012": [("E", 0)], "ED30DE24.013": [("E", 1)]}},
}


def scarica(url, nome):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / nome
    if not f.exists():
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=90) as r:
            if r.status != 200:
                raise SystemExit(f"{url}: HTTP {r.status}")
            f.write_bytes(r.read())
    return f


def sha(f):
    return hashlib.sha256(Path(f).read_bytes()).hexdigest()


def immagine(f, ruota):
    im = Image.open(f)
    im.info.pop("transparency", None)  # il bianco è trasparente nel PNG: senza toglierlo tesseract non legge nulla
    im = im.convert("L")
    return im.rotate(-90, expand=True) if ruota else im


def _gruppi(v, salto=3):
    g = []
    for x in v:
        if g and x - g[-1][-1] <= salto:
            g[-1].append(x)
        else:
            g.append([x])
    return [(x[0], x[-1]) for x in g]


def griglie(im):
    """Tabelle con le righe e le colonne disegnate: elenco di tabelle, ognuna elenco di righe (y0, y1, linee verticali)."""
    a = np.array(im) < 128
    H, W = a.shape
    hl = _gruppi([y for y in range(H) if a[y].sum() > W * 0.5])
    bande = []
    for (_, t1), (b0, _) in zip(hl, hl[1:]):
        sub = a[t1 + 1:b0]
        if sub.shape[0] < 20:
            continue
        bande.append((t1 + 1, b0, _gruppi([x for x in range(W) if sub[:, x].sum() > sub.shape[0] * 0.95])))
    tabs, cur = [], []
    for b in bande:
        if len(b[2]) >= 12:
            if cur and cur[-1][1] + 6 < b[0]:
                tabs.append(cur)
                cur = []
            cur.append(b)
        elif cur:
            tabs.append(cur)
            cur = []
    if cur:
        tabs.append(cur)
    return tabs


def tesseract(immagini, psm, lista_bianca=None):
    d = tempfile.mkdtemp()
    files = []
    for i, x in enumerate(immagini):
        p = os.path.join(d, f"{i}.png")
        x.save(p)
        files.append(p)
    lst = os.path.join(d, "l.txt")
    Path(lst).write_text("\n".join(files))
    cmd = ["tesseract", lst, "stdout", "--psm", str(psm)]
    if lista_bianca:
        cmd += ["-c", f"tessedit_char_whitelist={lista_bianca}"]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    return [p.strip() for p in out.split("\f")][:len(files)]


def etichetta(t):
    t = t.replace(" ", "").replace("l", "1").replace("I", "1")
    t = re.sub(r"^[0o]", "O", t)
    t = t[:1].upper() + t[1:]
    stelle = t.count("*")
    t = t.replace("*", "")
    if t == "E-1" and stelle == 3:
        return "E-1<4"
    return t


def valore(t):
    t = t.strip().replace(" ", "")
    if re.fullmatch(r"[-–—_=]+", t):
        return None
    t2 = t.replace("$", "").replace(",", "").rstrip("*")  # 2025: le celle al tetto hanno un asterisco
    if not re.fullmatch(r"\d{4,5}\.\d0", t2):
        raise ValueError(t)
    return round(float(t2), 2)


def leggi_griglia(im, scala):
    tabs = griglie(im)
    celle, pos = [], []
    for ti, t in enumerate(tabs):
        for ri, (y0, y1, vl) in enumerate(t):
            for ci, ((_, a1), (b0, _)) in enumerate(zip(vl, vl[1:])):
                c = im.crop((a1 + 4, y0 + 4, b0 - 3, y1 - 3))
                c = c.resize((max(1, int(c.width * scala)), max(1, int(c.height * scala))), Image.LANCZOS)
                bg = Image.new("L", (c.width + 40, c.height + 40), 255)
                bg.paste(c, (20, 20))
                celle.append(bg)
                inchiostro = int((np.array(im.crop((a1 + 4, y0 + 4, b0 - 3, y1 - 3))) < 128).sum())
                pos.append((ti, ri, ci, inchiostro))
    testi = tesseract(celle, 7, "0123456789,.$-OEW*")
    out = {}
    for (ti, ri, ci, ink), tx in zip(pos, testi):
        if not tx and 0 < ink < INCHIOSTRO_TRATTINO:
            tx = "-"  # trattino corto che tesseract non riporta: la cella ha solo un segno piccolo
        out.setdefault(ti, {}).setdefault(ri, {})[ci] = tx
    return [[[out[ti][ri][ci] for ci in sorted(out[ti][ri])] for ri in sorted(out[ti])] for ti in sorted(out)]


def leggi_per_righe(im):
    """Tabelle senza linee (2025): ogni riga di testo ritagliata e letta da sola (psm 7), a due scale."""
    a = np.array(im) < 128
    righe = _gruppi([y for y in range(a.shape[0]) if a[y].sum() > 8], salto=2)  # > 8 pixel: i puntini delle scansioni non uniscono le righe
    ritagli = [im.crop((0, max(0, y0 - 6), im.width, y1 + 6)) for y0, y1 in righe if y1 - y0 > 15]
    out = []
    for scala in (0.4, 0.5):
        pezzi = []
        for c in ritagli:
            c = c.resize((int(c.width * scala), max(1, int(c.height * scala))), Image.LANCZOS)
            bg = Image.new("L", (c.width + 40, c.height + 40), 255)
            bg.paste(c, (20, 20))
            pezzi.append(bg)
        out.append("\n".join(tesseract(pezzi, 7)))
    return out


RIGA = re.compile(r"^\s*([0OoWwEe][-–]\s?[0-9lI]{1,2}E?\*{0,4})\s+(.*)$")


def leggi_righe(testo):
    """Righe 'grado valore valore ...' da un testo (tesseract a pagina intera o livello di testo del PDF)."""
    righe = []
    for r in testo.splitlines():
        m = RIGA.match(r)
        if not m:
            continue
        resto = re.sub(r"(\d),\s(\d{3}\.\d0)", r"\1,\2", m.group(2).strip())  # "11, 634.00" -> "11,634.00"
        tok = [x for x in re.split(r"\s{2,}|\s(?=\$)|\s(?=\d{1,2},\d{3}\.\d0)|\s(?=-(?:\s|$))", resto) if x.strip()]
        righe.append((etichetta(m.group(1)), [x.strip() for x in tok]))
    return righe


def tabella_da_righe(righe, layout):
    """Assegna le righe lette alle categorie dell'immagine: per posizione se il numero di righe è quello atteso
    (un'etichetta letta male non sposta le altre), altrimenti per etichetta."""
    attese = [(cat, meta, g) for cat, meta in layout for g in GRADI[cat]]
    if len(righe) == len(attese):
        return {k: r[1] for k, r in zip(attese, righe)}
    out = {}
    per_nome = {}
    for nome, valori in righe:
        per_nome.setdefault(nome, []).append(valori)
    for cat, meta, g in attese:
        if per_nome.get(g):
            out[(cat, meta, g)] = per_nome[g].pop(0)
    return out


def anno(a):
    cfg = ANNI[a]
    meta = json.loads(scarica(f"https://www.federalregister.gov/api/v1/documents/{cfg['documento']}.json", f"fr-{cfg['documento']}.json").read_text())
    pdf = scarica(meta["pdf_url"], f"{cfg['documento']}.pdf")
    testo_pdf = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    tab = {cat: {g: [None] * 22 for g in GRADI[cat]} for cat in GRADI}
    letto = {cat: {g: [False] * 22 for g in GRADI[cat]} for cat in GRADI}
    conti = {"celle": 0, "A_uguale_B": 0, "C_uguale": 0, "C_illeggibile": 0}
    errori, immagini = [], []
    # lettura C: livello di testo del PDF, per immagine (il testo tra due marcatori </GPH> appartiene all'immagine che chiude)
    pezzi = re.split(r"(ED\d\d[A-Z]{2}\d\d\.\d{3})</GPH>", testo_pdf)
    testo_img = {pezzi[i + 1]: pezzi[i] for i in range(0, len(pezzi) - 1, 2)}
    for img_id, layout in cfg["immagini"].items():
        url = meta["images"][img_id]["original_size"]
        f = scarica(url, f"{img_id}.png")
        immagini.append({"id": img_id, "url": url, "sha256": sha(f)})
        im = immagine(f, ruota=cfg["griglia"])
        if cfg["griglia"]:
            letture = []
            for scala in (0.4, 0.5):
                tabs = leggi_griglia(im, scala)
                if len(tabs) != len(layout):
                    raise SystemExit(f"{img_id}: {len(tabs)} tabelle trovate, attese {len(layout)}")
                d = {}
                for (cat, metà), t in zip(layout, tabs):
                    righe = t[1:]  # la prima riga è l'intestazione
                    if len(righe) != len(GRADI[cat]):
                        raise SystemExit(f"{img_id} {cat}: {len(righe)} righe, attese {len(GRADI[cat])}")
                    for g, r in zip(GRADI[cat], righe):
                        if etichetta(r[0]) != g:
                            errori.append(f"{img_id}: etichetta letta '{r[0]}' invece di {g}")
                        d[(cat, metà, g)] = r[1:]
                letture.append(d)
        else:
            letture = [tabella_da_righe(leggi_righe(t), layout) for t in leggi_per_righe(im)]
        C = tabella_da_righe(leggi_righe(testo_img.get(img_id, "")), layout)
        chiavi = [(cat, metà, g) for cat, metà in layout for g in GRADI[cat]]
        for (cat, metà, g) in chiavi:
            righe = [letture[0].get((cat, metà, g)), letture[1].get((cat, metà, g)), C.get((cat, metà, g))]
            for k in range(11):
                col = metà * 11 + k
                v = []
                for r in righe:
                    try:
                        v.append(valore(r[k]) if r and len(r) == 11 else "?")
                    except ValueError:
                        v.append("?")
                va, vb, vc = v
                conti["celle"] += 1
                if cfg["rigoroso"]:
                    # tabella del sito: le due letture dell'immagine devono coincidere; il testo GPO, se leggibile, pure
                    if va == "?" or va != vb:
                        errori.append(f"{img_id} {g} {COLONNE[col]}: A={va} B={vb} C={vc}")
                        continue
                    scelto = va
                else:
                    # anno di controllo: basta che due letture su tre coincidano
                    cand = [x for x in v if x != "?"]
                    scelto = next((x for x in cand if cand.count(x) >= 2), "?")
                    if scelto == "?":
                        conti["senza_maggioranza"] = conti.get("senza_maggioranza", 0) + 1  # cella lasciata vuota (null)
                        continue
                    if vc != "?" and vc != scelto:
                        errori.append(f"{img_id} {g} {COLONNE[col]}: maggioranza {scelto} ma testo del PDF {vc}")
                        continue
                if va == vb == scelto:
                    conti["A_uguale_B"] += 1
                if vc == "?":
                    conti["C_illeggibile"] += 1
                elif vc != scelto:
                    errori.append(f"{img_id} {g} {COLONNE[col]}: immagine {scelto} ma testo del PDF {vc}")
                    continue
                else:
                    conti["C_uguale"] += 1
                tab[cat][g][col] = scelto
                letto[cat][g][col] = True
    mancano = [f"{g} {COLONNE[i]}" for cat in GRADI for g in GRADI[cat] for i in range(22) if not letto[cat][g][i]]
    if mancano and not errori and cfg["rigoroso"]:
        errori.append(f"celle non lette: {mancano[:10]}")
    if errori:
        raise SystemExit(f"{a}: {len(errori)} problemi di lettura\n - " + "\n - ".join(errori[:60]))
    # note in calce e paga dei cadetti: dal livello di testo del PDF (frasi intere)
    t1 = re.sub(r"\s+", " ", testo_pdf)
    def cerca(rx):
        m = re.search(rx, t1)
        if not m:
            raise SystemExit(f"{a}: frase non trovata nel PDF: {rx}")
        return float(m.group(1).replace(",", ""))
    note = {
        "tetto_O7_O10": cerca(r"level II of the Executive Schedule in effect during calendar year \d{4}, which is \$([\d,]+\.\d\d)"),
        "tetto_O6_e_sotto": cerca(r"level V of the Executive Schedule in effect during calendar year \d{4}, which is \$([\d,]+\.\d\d)"),
        "E9_incarichi_speciali": cerca(r"basic pay for this grade is \$([\d,]+\.\d\d) per month") if a >= 2026 else None,
        "cadetti": cerca(r"cadet or midshipman pay authorized by 37 U\.S\.C\. 203\(c\) is \$([\d,]+\.\d\d)") if a >= 2026 else None,
    }
    m = re.search(r"Schedule 8 is effective (\w+ \d+, \d{4})", t1)
    return {
        "anno": a,
        "effettiva_dal": m.group(1) if m else None,
        "fonte": {
            "titolo": meta["title"], "ordine_esecutivo": meta["executive_order_number"], "firmato_il": meta["signing_date"],
            "pubblicato_il": meta["publication_date"], "citazione": meta["citation"], "documento": meta["document_number"],
            "pagine": [meta["start_page"], meta["end_page"]], "url": meta["html_url"], "pdf": meta["pdf_url"], "pdf_sha256": sha(pdf),
            "immagini_schedule_8": immagini,
        },
        "letto_il": date.today().isoformat(),
        "colonne": COLONNE,
        "tabelle": tab,
        "note": note,
        "letture": conti,
    }


def main():
    anni = [int(x) for x in sys.argv[1:]] or [2026, 2025]
    for a in anni:
        d = anno(a)
        (DATI / f"paga_{a}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"{a}: {d['letture']} -> dati/paga_{a}.json")


if __name__ == "__main__":
    main()
