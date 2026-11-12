"""Legge le banche ufficiali dei quiz dai PDF in raccolta/_grezzi/ e scrive una banca JSON per ogni esame in dati/banche/.

Uso (dalla radice del repository, dopo raccolta/fonti.py):
    python3 -I quiz/raccolta/estrai.py

Ogni domanda: numero ufficiale (se c'è), sezione, testo, risposte, indice della risposta esatta secondo la chiave ufficiale,
file e pagina del PDF. Il testo è quello del PDF, con i soli a capo e spazi doppi tolti. Come è segnata la risposta esatta:
- Lazio (tartufi) e Valle d'Aosta (fitosanitario): riga evidenziata in giallo nel PDF (rettangolo di colore 1,1,0);
- Sicilia utilizzatori: segno ✓ davanti alla lettera; Sicilia consulenti: asterisco davanti alla risposta;
- Palermo ed Enna (ruolo conducenti): [*] accanto alla risposta nella scheda corretta di ogni seduta; le domande segnate
  «Domanda nulla» dalla commissione si scartano; le domande uguali in più sedute si contano una volta sola;
- Sassari (ruolo conducenti): colonna «Esatta» della tabella.
Si ferma con un errore se una domanda non ha esattamente una risposta esatta o se i numeri non tornano.
verifica.py rilegge i PDF con un lettore scritto a parte e confronta.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import pdfplumber

RADICE = Path(__file__).resolve().parent.parent
GREZZI = RADICE / "raccolta" / "_grezzi"
BANCHE = RADICE / "dati" / "banche"
GIALLO = (1.0, 1.0, 0.0)


def pulisci(t):
    t = re.sub(r"\s+", " ", t).strip()
    return re.sub(r"\s+([,.;:?!])", r"\1", t)


def righe_parole(page, filtro=None, tol=2.5):
    """Parole della pagina raggruppate in righe (per 'top'), in ordine di lettura."""
    parole = page.extract_words(extra_attrs=["fontname", "size"], keep_blank_chars=False, use_text_flow=False)
    if filtro:
        parole = [w for w in parole if filtro(w)]
    parole.sort(key=lambda w: (round(w["top"]), w["x0"]))
    righe = []
    for w in parole:
        if righe and abs(righe[-1]["top"] - w["top"]) <= tol:
            righe[-1]["parole"].append(w)
        else:
            righe.append({"top": w["top"], "parole": [w]})
    for r in righe:
        r["parole"].sort(key=lambda w: w["x0"])
        r["testo"] = " ".join(w["text"] for w in r["parole"])
        r["bottom"] = max(w["bottom"] for w in r["parole"])
        r["x0"] = r["parole"][0]["x0"]
        r["x1"] = r["parole"][-1]["x1"]
        r["grassetto"] = sum("Bold" in w["fontname"] for w in r["parole"]) > len(r["parole"]) / 2
    return righe


def gialli(page, h_min=8):
    return [r for r in page.rects if r.get("non_stroking_color") == GIALLO and r["height"] >= h_min]


def evidenziata(riga, rett):
    c = (riga["top"] + riga["bottom"]) / 2
    return any(r["top"] - 1 <= c <= r["bottom"] + 1 and r["x0"] < riga["x1"] and r["x1"] > riga["x0"] for r in rett)


def chiudi(domande, file_, controlla_n=True, n_risposte=None):
    out = []
    for d in domande:
        if n_risposte and len(d["risposte"]) != n_risposte:
            raise SystemExit(f"{file_}: domanda {d.get('n')} (pag. {d['pagina']}) con {len(d['risposte'])} risposte")
        esatte = [i for i, r in enumerate(d["risposte"]) if r["esatta"]]
        if len(esatte) != 1:
            raise SystemExit(f"{file_}: domanda {d.get('n')} (pag. {d['pagina']}) con {len(esatte)} risposte esatte: {d['testo'][:80]}")
        out.append({"n": d.get("n"), "sezione": d.get("sezione", ""), "testo": pulisci(d["testo"]),
                    "risposte": [pulisci(r["testo"]) for r in d["risposte"]], "esatta": esatte[0],
                    "file": file_, "pagina": d["pagina"]})
    if controlla_n:
        nn = [d["n"] for d in out]
        if nn != list(range(1, len(nn) + 1)):
            salti = [(a, b) for a, b in zip(nn, nn[1:]) if b != a + 1]
            raise SystemExit(f"{file_}: numerazione non continua {salti[:5]}")
    return out


# ---------------------------------------------------------------- Lazio, tartufi (evidenziato in giallo, numero nella colonna a sinistra)
def lazio(nome="tart_lazio_2015.pdf", col_numero=40, salta_pagine=0):
    domande, sezione, attiva = [], "", None
    numeri = []
    with pdfplumber.open(GREZZI / nome) as pdf:
        for pn, page in enumerate(pdf.pages, 1):
            if pn <= salta_pagine:
                continue
            rett = gialli(page)
            alto = page.height - 40
            righe = righe_parole(page, lambda w: 8.5 <= w["size"] <= 11.5 and w["top"] < alto and w["x0"] >= col_numero)
            for w in page.extract_words(extra_attrs=["fontname", "size"]):
                if w["x0"] < col_numero and re.fullmatch(r"\d{1,3}", w["text"]) and "Bold" in w["fontname"] and w["top"] < alto:
                    numeri.append((pn, w["top"], int(w["text"])))
            for r in righe:
                t = r["testo"]
                if r["grassetto"] and t.upper() == t and re.search(r"[A-Z]{4}", t) and "?" not in t:
                    if re.search(r"DIREZIONE|AREA ECONOMIA|QUESITI OGGETTO|TESSERINO DI IDONEITA|art\.6|Legge", t, re.I):
                        continue
                    sezione = t.capitalize()
                    attiva = None
                    continue
                if r["grassetto"]:
                    if attiva is None or attiva["risposte"]:
                        attiva = {"testo": t, "risposte": [], "pagina": pn, "sezione": sezione, "box": [(pn, r["top"], r["bottom"])]}
                        domande.append(attiva)
                    else:
                        attiva["testo"] += " " + t
                        attiva["box"].append((pn, r["top"], r["bottom"]))
                    continue
                if attiva is None:
                    continue
                m = re.match(r"^([a-c])\)\s*(.*)$", t)
                ev = evidenziata(r, rett)
                if m:
                    attiva["risposte"].append({"testo": m.group(2), "esatta": ev})
                elif attiva["risposte"]:
                    attiva["risposte"][-1]["testo"] += " " + t
                    attiva["risposte"][-1]["esatta"] |= ev
                else:
                    attiva["testo"] += " " + t
    for d in domande:
        pn = d["box"][0][0]
        alto, basso = min(b[1] for b in d["box"]), max(b[2] for b in d["box"])
        cand = [n for (p, top, n) in numeri if p == pn and alto - 8 <= top <= basso + 8]
        if len(cand) != 1:
            raise SystemExit(f"{nome}: numero non trovato per «{d['testo'][:60]}» (pag. {pn}): {cand}")
        d["n"] = cand[0]
    return chiudi(domande, nome, n_risposte=3)


# ---------------------------------------------------------------- Valle d'Aosta, fitosanitario (giallo, «1.» in grassetto)
def vda(nome="fito_vda.pdf"):
    domande, sezione, attiva, titolo_sez = [], "", None, []
    with pdfplumber.open(GREZZI / nome) as pdf:
        for pn, page in enumerate(pdf.pages, 1):
            rett = gialli(page)
            righe = righe_parole(page, lambda w: 55 < w["top"] < page.height - 70)
            for r in righe:
                t = r["testo"]
                if re.fullmatch(r"\d{1,3}", t) and not r["grassetto"]:
                    continue  # numero di pagina
                mq = re.match(r"^(\d{1,3})\.\s+(.*)$", t)
                if r["grassetto"] and mq:
                    if titolo_sez:
                        sezione = pulisci(" ".join(titolo_sez))
                        titolo_sez = []
                    attiva = {"n": int(mq.group(1)), "testo": mq.group(2), "risposte": [], "pagina": pn, "sezione": sezione}
                    domande.append(attiva)
                    continue
                if r["grassetto"]:
                    if attiva is not None and not attiva["risposte"]:
                        attiva["testo"] += " " + t
                    else:
                        titolo_sez.append(t)
                    continue
                if attiva is None:
                    continue
                m = re.match(r"^([a-c])\)\s*(.*)$", t)
                ev = evidenziata(r, rett)
                if m:
                    attiva["risposte"].append({"testo": m.group(2), "esatta": ev})
                elif attiva["risposte"]:
                    attiva["risposte"][-1]["testo"] += " " + t
                    attiva["risposte"][-1]["esatta"] |= ev
                else:
                    attiva["testo"] += " " + t
    for d in domande:
        for r in d["risposte"]:
            r["testo"] = re.sub(r";$", "", r["testo"].strip())
        d["sezione"] = re.sub(r"^(MODULO \d+)\s*", lambda m: m.group(1).capitalize() + ": ", d["sezione"])
    return chiudi(domande, nome, n_risposte=3)


# ---------------------------------------------------------------- Sicilia (testo: «1.» domanda, «a)»/«a.» risposte, ✓ o *)
def pagine_testo(nome):
    t = subprocess.run(["pdftotext", "-layout", str(GREZZI / nome), "-"], capture_output=True, text=True).stdout
    return t.split("\f")


# Righe del PDF lette a mano perché il PDF stesso è irregolare (lo dice anche la pagina «Come lavoriamo» del sito)
CORREZIONI = {
    ("fito_sicilia_util.pdf", 85): "la terza risposta non ha la lettera «c)» nel PDF: è la riga «nessuna precauzione in assenza di vento»",
}


def chiave_tabella(nome):
    """Tabella finale «n. domanda / risposta esatta» dei PDF siciliani: {numero: indice}."""
    testo = subprocess.run(["pdftotext", "-layout", str(GREZZI / nome), "-"], capture_output=True, text=True).stdout
    coda = testo[testo.index("risposta"):]
    return {int(n): "abc".index(l) for n, l in re.findall(r"(?<!\S)(\d{1,3})\s+([abc])(?!\S)", coda)}


def sicilia(nome, segno):
    domande, sezione, attiva, in_cap = [], "", None, False
    re_q = re.compile(r"^\s{0,6}(\d{1,3})\.\s+(\S.*)$")
    re_r = re.compile(r"^\s*(✓|\*)?\s*([a-d])\s*(✓)?([\).]|\s+(?=[*A-ZÀÈÉÌÒÙ]))\s*(\*)?\s*(.*)$")
    fine = False
    for pn, pag in enumerate(pagine_testo(nome), 1):
        for riga in pag.split("\n"):
            if fine or not riga.strip() or re.fullmatch(r"\s*\d{1,3}\s*", riga):
                continue
            s = riga.strip()
            if re.match(r"^(Testo elaborato da|N\.B\. alcune domande|n\.\s+risposta)", s):
                fine = True  # note finali e tabella delle risposte (letta da chiave_tabella)
                continue
            if re.match(r"^CAPITOLO\s*\d+", s, re.I):
                sezione, in_cap, attiva = s, True, None
                continue
            if not sezione:
                continue  # premessa prima del primo capitolo
            mq = re_q.match(riga)
            mr = re_r.match(riga)
            if mq:
                in_cap = False
                attiva = {"n": int(mq.group(1)), "testo": mq.group(2), "risposte": [], "pagina": pn, "sezione": sezione}
                domande.append(attiva)
                continue
            if in_cap:
                sezione += " " + s
                continue
            if attiva is None:
                continue
            # nuova risposta: lettera attesa, oppure lettera con punto/parentesi (nel PDF dei consulenti la domanda 204 ha due «b.»)
            if mr and len(attiva["risposte"]) < 4 and (mr.group(2) == "abcd"[len(attiva["risposte"])] or mr.group(4).strip()):
                esatta = bool(mr.group(1) or mr.group(3) or mr.group(5))
                attiva["risposte"].append({"testo": mr.group(6), "esatta": esatta, "righe": [mr.group(6)]})
            elif attiva["risposte"]:
                attiva["risposte"][-1]["testo"] += " " + s
                attiva["risposte"][-1]["righe"].append(s)
            else:
                attiva["testo"] += " " + s
    for d in domande:
        d["sezione"] = pulisci(re.sub(r"^CAPITOLO\s*(\d+)\s*:?\s*", r"Capitolo \1: ", d["sezione"], flags=re.I))
        for r in d["risposte"]:
            if r["testo"].startswith("*"):
                r["esatta"], r["testo"] = True, r["testo"][1:]
        if (nome, d["n"]) in CORREZIONI and len(d["risposte"]) == 2:
            ult = d["risposte"][-1]
            terza = ult["righe"].pop()
            ult["testo"] = " ".join(ult["righe"])
            d["risposte"].append({"testo": terza, "esatta": False})
            d["nota_pdf"] = CORREZIONI[(nome, d["n"])]
    out = chiudi(domande, nome, n_risposte=3)
    for d, o in zip(domande, out):
        if d.get("nota_pdf"):
            o["nota_pdf"] = d["nota_pdf"]
    tab = chiave_tabella(nome)
    diverse = [d["n"] for d in out if tab.get(d["n"]) != d["esatta"]]
    if len(tab) != len(out) or len(diverse) > 5:
        raise SystemExit(f"{nome}: la tabella finale ({len(tab)} righe) e i segni nel testo non coincidono per le domande {diverse[:20]}")
    # Se le due chiavi ufficiali (segno nel testo e tabella finale) non coincidono, la domanda resta fuori dal quiz.
    escluse = [{"n": d["n"], "testo": d["testo"], "segno_nel_testo": "abc"[d["esatta"]], "tabella_finale": "abc"[tab[d["n"]]],
                "pagina": d["pagina"]} for d in out if d["n"] in diverse]
    return [d for d in out if d["n"] not in diverse], escluse


# ---------------------------------------------------------------- Palermo ed Enna, schede corrette delle sedute
def paen():
    fj = json.loads((RADICE / "dati" / "fonti.json").read_text(encoding="utf-8"))["file"]
    tutte, viste = [], {}
    nulle = scartate_dup = 0
    for fid in sorted(k for k in fj if re.fullmatch(r"paen_\d+", k)):
        nome = fj[fid]["file"]
        pagine = pagine_testo(nome)
        data = re.search(r"Data esame:\s*(\d{2}/\d{2}/\d{4})", pagine[0]).group(1)
        dd = []
        attiva = None
        for pn, pag in enumerate(pagine, 1):
            for riga in pag.split("\n"):
                s = riga.strip()
                if not s or "esamiQuestServlet" in s or re.search(r"Pagina \d+ di \d+$", s) or re.search(r"(^|\s)TESTATA(\s+Pagina \d+ di \d+)?$", s):
                    continue  # piè di pagina della stampa (indirizzo interno, data, «Pagina 2 di 3»)
                mq = re.match(r"^(\d{1,2})\)\s*(.*)$", s)
                mr = re.match(r"^([ABC])\s*\[([ *])\]\s*(.*)$", s)
                if mq:
                    attiva = {"n": int(mq.group(1)), "testo": mq.group(2), "risposte": [], "pagina": pn, "nulla": False}
                    dd.append(attiva)
                elif attiva is None:
                    continue
                elif mr:
                    attiva["risposte"].append({"testo": mr.group(3), "esatta": mr.group(2) == "*"})
                elif re.search(r"Domanda\s+nulla", s, re.I):
                    attiva["nulla"] = True
                    resto = re.sub(r"Domanda\s+nulla", "", s, flags=re.I).strip()
                    if resto and not attiva["risposte"]:
                        attiva["testo"] += " " + resto
                elif attiva["risposte"]:
                    attiva["risposte"][-1]["testo"] += " " + s
                else:
                    attiva["testo"] += " " + s
        nn = [d["n"] for d in dd]
        if nn != list(range(1, len(nn) + 1)) or len(dd) not in (20, 21):
            raise SystemExit(f"{nome}: domande {nn}")
        for d in dd:
            if d["nulla"]:
                nulle += 1
                continue
            q = chiudi([d], nome, controlla_n=False, n_risposte=3)[0]
            q["seduta"] = data
            q["n_seduta"] = q.pop("n")
            chiave = (q["testo"].lower(), tuple(r.lower() for r in q["risposte"]))
            if chiave in viste:
                prima = viste[chiave]
                if prima["esatta"] != q["esatta"]:
                    raise SystemExit(f"{nome}: stessa domanda con chiave diversa in due sedute: {q['testo'][:80]}")
                prima.setdefault("altre_sedute", []).append(data)
                scartate_dup += 1
                continue
            viste[chiave] = q
            tutte.append(q)
    for i, q in enumerate(tutte, 1):
        q["n"] = i
    return tutte, {"nulle": nulle, "doppie": scartate_dup}


# ---------------------------------------------------------------- Cagliari-Oristano (stampa ARCA della banca: titoli di sezione, [*])
def caor(nome="taxi_caor.pdf"):
    out, sezione, attiva = [], "", None
    for pn, pag in enumerate(pagine_testo(nome), 1):
        for riga in pag.split("\n"):
            s = riga.strip()
            if not s or "ARCA - Documento" in s or "esamiQuestServlet" in s or re.search(r"(^|\s)TESTATA(\s+Pagina \d+ di \d+)?$", s):
                continue  # intestazione e piè di pagina della stampa
            mq = re.match(r"^(\d{1,3})\)\s*(.*)$", s)
            mr = re.match(r"^([A-D])\s*\[([ *])\]\s*(.*)$", s)
            if mq:
                attiva = {"n": int(mq.group(1)), "testo": mq.group(2), "risposte": [], "pagina": pn, "sezione": sezione}
                out.append(attiva)
            elif re.fullmatch(r"[A-ZÀÈÉÌÒÙ' ’]{6,}", s) and (attiva is None or len(attiva["risposte"]) == 3):
                sezione, attiva = s.capitalize().replace("cagliari", "Cagliari").replace("oristano", "Oristano"), None
            elif attiva is None:
                continue
            elif mr:
                attiva["risposte"].append({"testo": mr.group(3), "esatta": mr.group(2) == "*"})
            elif attiva["risposte"]:
                attiva["risposte"][-1]["testo"] += " " + s
            else:
                attiva["testo"] += " " + s
    dd = chiudi(out, nome, controlla_n=False, n_risposte=3)
    for sez in dict.fromkeys(d["sezione"] for d in dd):  # numerazione continua dentro ogni sezione
        nn = [d["n"] for d in dd if d["sezione"] == sez]
        if nn != list(range(1, len(nn) + 1)):
            raise SystemExit(f"{nome}: numerazione della sezione {sez} non continua")
    for i, d in enumerate(dd, 1):
        d["n_sezione"], d["n"] = d["n"], i
    return dd


# ---------------------------------------------------------------- Patente nautica: elenco unico nazionale MIT (tabella con V/F per risposta)
# \b davanti a «figur»: «configurazione» non è un rimando a una figura (quiz vela n. 95, escluso per errore fino al 12/11/2026)
FIGURA = re.compile(r"\bfigur|raffigur|disegn|immagin|illustra|frecci|fotograf|rappresentat[oaie]\s+(in|nella|nel)", re.I)


def nautica(nome="mit/allegato_a_dd131_2022.pdf"):
    """Quiz base (tre risposte) e quiz vela (VERO/FALSO). La chiave è la colonna V/F accanto a ogni risposta.
    Restano fuori: le domande con un'immagine nella colonna IMMAGINE o che rimandano a una figura (le immagini non si riproducono),
    le righe con la chiave illeggibile o non univoca (zero o due «V») e le righe con testo che sborda nelle colonne vicine."""
    base, vela, escluse = [], [], []

    def pul(x):  # «Nord-\nOvest» a capo nella cella: si tiene il trattino senza spazio
        return pulisci(re.sub(r"(\w)-[ \t]*\n\s*(\w)", r"\1-\2", x))
    with pdfplumber.open(GREZZI / nome) as pdf:
        for pn, page in enumerate(pdf.pages, 1):
            imgs = page.images
            for tab in page.find_tables():
                for riga, r in zip(tab.rows, tab.extract()):
                    if not r or not (r[0] or "").strip().isdigit():
                        continue
                    r = [(x or "").strip() for x in r]
                    top, bot = riga.bbox[1], riga.bbox[3]
                    cella_img = riga.cells[1]
                    immagine = any(i["top"] < bot and i["bottom"] > top and (cella_img is None or i["x0"] < cella_img[2] + 2) for i in imgs)
                    if len(r) == 11:  # quiz vela: due risposte (VERO, FALSO)
                        ris, vf, prog, cap, tema, voce = [r[3], r[5]], [r[4], r[6]], r[7], r[8], r[9], r[10]
                    else:
                        ris, vf, prog, cap, tema, voce = [r[3], r[5], r[7]], [r[4], r[6], r[8]], r[9], r[10], r[11], r[12]
                    vfu = [v.upper() for v in vf]
                    d = {"n": int(r[0]), "sezione": pul(tema).capitalize() if cap == "BASE" else pul(voce).capitalize(),
                         "voce": pul(voce), "progressivo": prog, "testo": pul(r[2]), "risposte": [pul(x) for x in ris],
                         "file": nome, "pagina": pn, "capitolo": cap}
                    motivo = None
                    if immagine or FIGURA.search(r[2]):
                        motivo = "rimanda a una figura (le immagini non si riproducono)"
                    elif any(v not in ("V", "F") for v in vfu):
                        motivo = "chiave V/F illeggibile nel PDF (testo della risposta che sborda nella colonna)"
                    elif vfu.count("V") != 1:
                        motivo = f"nel PDF {vfu.count('V')} risposte segnate V"
                    elif not re.fullmatch(r"\d\.\d\.\d+[-.]\d+", prog):
                        motivo = "colonna «Progressivo» illeggibile (testo che sborda)"
                    if motivo:
                        escluse.append({"capitolo": cap, "n": d["n"], "testo": d["testo"], "pagina": pn, "motivo": motivo})
                        continue
                    d["esatta"] = vfu.index("V")
                    (base if cap == "BASE" else vela).append(d)
    for nome_cap, dd, tot in (("BASE", base, 1472), ("VELA", vela, 250)):
        nn = sorted([d["n"] for d in dd] + [e["n"] for e in escluse if e["capitolo"] == nome_cap])
        if nn != list(range(1, tot + 1)):
            raise SystemExit(f"{nome}: quiz {nome_cap} con numerazione diversa da 1-{tot}")
    for d in base + vela:
        if not d["testo"] or not all(d["risposte"]):
            raise SystemExit(f"{nome}: domanda {d['capitolo']} {d['n']} con testo vuoto")
    return base, vela, escluse


# ---------------------------------------------------------------- Sassari (tabella con colonna «Esatta»)
def sassari(nome="taxi_sassari.pdf"):
    out = []
    with pdfplumber.open(GREZZI / nome) as pdf:
        for pn, page in enumerate(pdf.pages, 1):
            for tab in page.extract_tables():
                for riga in tab:
                    if not riga or not riga[1] or not re.fullmatch(r"\d{1,3}", (riga[1] or "").strip()):
                        continue
                    cat, n, rif, dom, a, b, c, es = [(x or "").strip() for x in riga[:8]]
                    if es not in ("A", "B", "C"):
                        raise SystemExit(f"{nome}: domanda {n} senza risposta esatta leggibile ({es!r})")
                    out.append({"n": int(n), "sezione": pulisci(cat), "riferimento": pulisci(rif), "testo": pulisci(dom),
                                "risposte": [pulisci(a), pulisci(b), pulisci(c)], "esatta": "ABC".index(es),
                                "file": nome, "pagina": pn})
    nn = [d["n"] for d in out]
    if nn != list(range(1, len(nn) + 1)):
        raise SystemExit(f"{nome}: numerazione {nn[:10]}...")
    for d in out:
        if not d["testo"] or not all(d["risposte"]):
            raise SystemExit(f"{nome}: domanda {d['n']} con testo o risposta vuota")
    return out


def scrivi(id_, domande, extra=None):
    BANCHE.mkdir(parents=True, exist_ok=True)
    dati = {"_nota": "Scritto da raccolta/estrai.py dal PDF ufficiale (vedi dati/fonti.json). Non modificare a mano.",
            "id": id_, "domande": domande}
    dati.update(extra or {})
    (BANCHE / f"{id_}.json").write_text(json.dumps(dati, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"{id_:32} {len(domande)} domande")


def main():
    nb, nv, ne = nautica()
    scrivi("nautica-base", nb, {"escluse": [e for e in ne if e["capitolo"] == "BASE"], "totale_pdf": 1472})
    scrivi("nautica-vela", nv, {"escluse": [e for e in ne if e["capitolo"] == "VELA"], "totale_pdf": 250})
    lz = lazio()
    pg = pagine_testo("tart_lazio_guida.pdf")
    inizio = next(i for i, x in enumerate(pg) if "QUESITI OGGETTO DELLA PROVA" in x)  # pagine prima dei quesiti: testo della guida
    guida = lazio("tart_lazio_guida.pdf", col_numero=55, salta_pagine=inizio)
    senza_spazi = lambda d: re.sub(r"\s", "", (d["testo"] + "".join(d["risposte"])).lower())
    diff = [(a["n"], a["testo"][:50], b["testo"][:50]) for a, b in zip(lz, guida) if senza_spazi(a) != senza_spazi(b) or a["esatta"] != b["esatta"]]
    if len(lz) != len(guida) or diff:
        print(f"AVVISO Lazio: allegato 2015 {len(lz)} domande, guida 2021 {len(guida)}; differenze {len(diff)}: {diff[:5]}", file=sys.stderr)
    # Il PDF ha il titolo solo per la prima parte; la determinazione G10268 conta 64 quesiti sulle specie, 65 sulla biologia,
    # 146 sulla normativa, in quest'ordine (controllato: la 65 e la 130 aprono i nuovi argomenti).
    for d in lz:
        d["sezione"] = ("Conoscenza delle specie" if d["n"] <= 64 else "Biologia del tartufo" if d["n"] <= 129
                        else "Normativa su ricerca, raccolta e commercio")
    scrivi("tartufi-lazio", lz, {"confronto_guida_2021": {"domande": len(guida), "differenze": len(diff)}})
    scrivi("fitosanitario-valle-d-aosta", vda())
    for id_, nome in (("fitosanitario-sicilia-utilizzatori", "fito_sicilia_util.pdf"), ("fitosanitario-sicilia-consulenti", "fito_sicilia_cons.pdf")):
        dd, escl = sicilia(nome, "")
        scrivi(id_, dd, {"escluse": escl})
    pa, info = paen()
    scrivi("taxi-ncc-palermo-enna", pa, {"scartate": info})
    scrivi("taxi-ncc-sassari", sassari())
    scrivi("taxi-ncc-cagliari-oristano", caor())


if __name__ == "__main__":
    main()
