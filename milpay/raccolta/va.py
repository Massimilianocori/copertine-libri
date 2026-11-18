"""Raccolta della sezione "VA disability": tabelle ufficiali dell'indennità di invalidità dei veterani (va.gov) e tabella dei gradi combinati.

Uso (dalla radice del repository): python3 milpay/raccolta/va.py [--senza-rete]
Scarica i file grezzi in dati/grezzi/ (URL, data e SHA-256 nel registro "grezzi" di dati/fonti.json), li legge e scrive dati/va.json.
Con --senza-rete rilegge i file già scaricati (serve a genera.py e a chi controlla).

Fonti (tutte ufficiali, lette dal server, nessun blocco aggirato):
  va.gov  tabelle in vigore (dal 1/12/2025, "2026") e tabelle passate (dal 1/12/2024, "2025"): 108 celle ciascuna
  govinfo avvisi del VA nel Federal Register con gli importi di legge (38 U.S.C. 1114 e 1115(1)) per gli stessi due anni
  eCFR    38 CFR 4.25, Table I (gradi combinati); va.gov ripete la stessa tabella nella pagina "About disability ratings"
  Federal Register (API) ultimo avviso del VA "Cost of Living Adjustments for Service-Connected Benefits": dice se gli importi 2027 sono usciti
Controlli prima di scrivere (uno solo che fallisce ferma tutto):
  ogni cella di va.gov = importo di legge dell'avviso + quota per i familiari secondo 38 U.S.C. 1115(2) (proporzione, arrotondata per difetto al dollaro);
  Table I dell'eCFR = tabella di va.gov, cella per cella, e = formula del testo del 4.25 (efficienza residua, arrotondata all'intero, metà in su).
federalregister.gov (pagine HTML) chiede un CAPTCHA ai programmi: si usano la sua API pubblica e govinfo.gov, come dice la pagina stessa.
"""
import gzip
import hashlib
import html
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
DATI = RADICE / "dati"
GREZZI = DATI / "grezzi"
UA = {"User-Agent": "rete-siti-dati/1.0 (controllo delle fonti ufficiali)"}

FILE = {
    "va_rates_2026.html": "https://www.va.gov/disability/compensation-rates/veteran-rates/",
    "va_rates_2025.html": "https://www.va.gov/disability/compensation-rates/veteran-rates/past-rates-2025/",
    "va_fr_2026-02997.htm": "https://www.govinfo.gov/content/pkg/FR-2026-02-17/html/2026-02997.htm",
    "va_fr_2025-13484.htm": "https://www.govinfo.gov/content/pkg/FR-2025-07-18/html/2025-13484.htm",
    "ecfr_38_4_25.xml": "https://www.ecfr.gov/api/versioner/v1/full/2026-10-01/title-38.xml?part=4&section=4.25",
    "va_about_ratings.html": "https://www.va.gov/disability/about-disability-ratings/",
    "fr_api_va_cola.json": ("https://www.federalregister.gov/api/v1/documents.json?conditions%5Bagencies%5D%5B%5D=veterans-affairs-department"
                            "&conditions%5Bterm%5D=%22Cost+of+Living+Adjustments+for+Service-Connected+Benefits%22&conditions%5Btype%5D%5B%5D=NOTICE&order=newest&per_page=5"),
}
# anno delle tabelle -> (file va.gov, file dell'avviso, data di decorrenza, aumento in percentuale scritto nell'avviso)
ANNI = {"2026": ("va_rates_2026.html", "va_fr_2026-02997.htm", "2025-12-01", "2.8"),
        "2025": ("va_rates_2025.html", "va_fr_2025-13484.htm", "2024-12-01", "2.5")}
GRADI = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
# le 12 situazioni familiari delle tabelle di va.gov, nell'ordine della pagina: (chiave, coniuge, genitori, figlio, etichetta attesa senza differenze di punteggiatura)
STATI = [("alone", 0, 0, 0, "veteran alone"), ("spouse", 1, 0, 0, "with spouse"), ("spouse_p1", 1, 1, 0, "with spouse and 1 parent"), ("spouse_p2", 1, 2, 0, "with spouse and 2 parents"),
         ("p1", 0, 1, 0, "with 1 parent"), ("p2", 0, 2, 0, "with 2 parents"),
         ("child", 0, 0, 1, "veteran with"), ("child_spouse", 1, 0, 1, "with 1 child and spouse"), ("child_spouse_p1", 1, 1, 1, "with 1 child spouse and 1 parent"),
         ("child_spouse_p2", 1, 2, 1, "with 1 child spouse and 2 parents"), ("child_p1", 0, 1, 1, "with 1 child and 1 parent"), ("child_p2", 0, 2, 1, "with 1 child and 2 parents")]
REFUSI_VA = [(86, 80, 97, 91)]  # (riga, colonna, valore del 38 CFR 4.25, valore nella copia di va.gov)
AGGIUNTE = [("child_u18", "each additional child under age 18"), ("child_school", "each additional child over age 18 in a qualifying school program"),
            ("spouse_aa", "spouse receiving aid and attendance")]


def scarica():
    GREZZI.mkdir(parents=True, exist_ok=True)
    reg = {}
    for nome, url in FILE.items():
        req = urllib.request.Request(url, headers=dict(UA, **{"Accept-Encoding": "gzip"}))
        with urllib.request.urlopen(req, timeout=120) as r:
            b, http = r.read(), r.status
            if r.headers.get("Content-Encoding") == "gzip":
                b = gzip.decompress(b)
        if http != 200 or len(b) < 400:
            raise SystemExit(f"{nome}: HTTP {http}, {len(b)} byte")
        (GREZZI / nome).write_bytes(b)
        reg[nome] = {"url": url, "letto_il": date.today().isoformat(), "sha256": hashlib.sha256(b).hexdigest(), "byte": len(b), "http": http}
        print(f"{nome}: {len(b)} byte")
    return reg


def cent(s):
    """'1,132.90' -> 113290 (centesimi, interi)."""
    m = re.fullmatch(r"\$?(\d{1,3}(?:,\d{3})*|\d+)\.(\d\d)", s.strip())
    if not m:
        raise SystemExit(f"importo non leggibile: {s!r}")
    return int(m.group(1).replace(",", "")) * 100 + int(m.group(2))


def puro(x):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", x)).replace("\xa0", " ").replace("﻿", "")).strip()


def tabelle_va(testo):
    """Le <va-table> della pagina: [(titolo, [righe di celle di testo])]."""
    out = []
    for m in re.finditer(r'<va-table table-title="([^"]*)"[^>]*>(.*?)</va-table>', testo, re.S):
        righe = [[puro(c) for c in re.split(r"</span>\s*<span>", r.strip())] for r in re.findall(r"<va-table-row[^>]*>(.*?)</va-table-row>", m.group(2), re.S)]
        out.append((html.unescape(m.group(1)), righe))
    return out


def etichetta(s):
    return re.sub(r"[^a-z0-9 ]", "", re.sub(r"\(.*?\)", "", s.lower())).strip()


def leggi_va(anno, percorso):
    """Pagina va.gov delle tabelle -> base (10 gradi), righe (12 situazioni × 8 gradi), aggiunte (3 righe × 8 gradi); importi in centesimi."""
    testo = percorso.read_text(encoding="utf-8")
    eff = date.fromisoformat(ANNI[anno][2])
    frase = f"Effective {eff.strftime('%B')} {eff.day}, {eff.year}"
    if testo.count(frase) < 2:
        raise SystemExit(f"{percorso.name}: la pagina non dice «{frase}» (le tabelle sono cambiate? aggiornare ANNI e il sito)")
    tab = tabelle_va(testo)
    if len(tab) != 9:
        raise SystemExit(f"{percorso.name}: {len(tab)} tabelle (attese 9)")
    t0 = tab[0][1]
    if [r[0] for r in t0[1:]] != ["10%", "20%"]:
        raise SystemExit(f"{percorso.name}: prima tabella inattesa {t0}")
    base = {"10": cent(t0[1][1]), "20": cent(t0[2][1])}
    righe = {k: {} for k, *_ in STATI}
    agg = {k: {} for k, _ in AGGIUNTE}
    # ordine della pagina: senza figli (30-60: base, aggiunte; 70-100: base, aggiunte), con figli (lo stesso)
    piano = [("Basic", 0, [30, 40, 50, 60]), ("Added", 0, [30, 40, 50, 60]), ("Basic", 0, [70, 80, 90, 100]), ("Added", 0, [70, 80, 90, 100]),
             ("Basic", 1, [30, 40, 50, 60]), ("Added", 1, [30, 40, 50, 60]), ("Basic", 1, [70, 80, 90, 100]), ("Added", 1, [70, 80, 90, 100])]
    for (titolo, rr), (tipo, figli, gradi) in zip(tab[1:], piano):
        if not titolo.startswith(f"{tipo} ") or f"{gradi[0]}% to {gradi[-1]}%" not in titolo:
            raise SystemExit(f"{percorso.name}: tabella «{titolo}» fuori posto (attesa {tipo} {gradi[0]}-{gradi[-1]})")
        if [re.match(r"(\d+)%", c).group(1) for c in rr[0][1:]] != [str(g) for g in gradi]:
            raise SystemExit(f"{percorso.name}: intestazioni {rr[0]}")
        corpo = rr[1:]
        if tipo == "Basic":
            attese = [s for s in STATI if s[3] == figli]
            if len(corpo) != 6:
                raise SystemExit(f"{percorso.name}: «{titolo}» ha {len(corpo)} righe")
            for (k, _, _, _, et), r in zip(attese, corpo):
                if not etichetta(r[0]).startswith(et):
                    raise SystemExit(f"{percorso.name}: riga «{r[0]}» dove era attesa «{et}»")
                for g, v in zip(gradi, r[1:]):
                    righe[k][str(g)] = cent(v)
        else:
            # la pagina 2026 mette nelle tabelle "senza figli" solo la riga del coniuge; la pagina 2025 le ripete tutte e tre (e scrive una volta "receving")
            nomi = {et: k for k, et in AGGIUNTE}
            visti = []
            for r in corpo:
                k = nomi.get(etichetta(r[0]).replace("receving", "receiving"))
                if k is None:
                    raise SystemExit(f"{percorso.name}: riga inattesa «{r[0]}» in «{titolo}»")
                visti.append(k)
                for g, v in zip(gradi, r[1:]):
                    if agg[k].get(str(g), cent(v)) != cent(v):
                        raise SystemExit(f"{percorso.name}: {k} {g}% diverso tra le due tabelle delle aggiunte")
                    agg[k][str(g)] = cent(v)
            if visti not in (["spouse_aa"], [k for k, _ in AGGIUNTE]) or (figli and len(visti) != 3):
                raise SystemExit(f"{percorso.name}: «{titolo}» ha le righe {visti}")
    for g in GRADI[2:]:
        base[str(g)] = righe["alone"][str(g)]
    agg_data = re.search(r'Last updated:(?:&nbsp;|\s)*<time dateTime="(\d{4}-\d\d-\d\d)"', testo)
    return {"decorrenza": ANNI[anno][2], "pagina_aggiornata_il": agg_data.group(1) if agg_data else None, "base": base, "righe": righe, "aggiunte": agg}


def leggi_avviso(percorso, pct):
    """Avviso del VA nel Federal Register (testo GPO): importi di legge in centesimi."""
    t = html.unescape(re.sub(r"<[^>]+>", "", percorso.read_text(encoding="utf-8")))
    if not re.search(rf"there will be\s+a {re.escape(pct)}% cost-of-living increase in Social Security benefits", t):
        raise SystemExit(f"{percorso.name}: l'avviso non dice {pct}%")
    v = {}
    for riga in t.splitlines():
        m = re.match(r"\s*(.*?)\.{4,}\s+(.*)$", riga)
        if m:
            v[re.sub(r"\s+", " ", re.sub(r"38 U\.S\.C\.\s+(Sec\.\s+)?", "", m.group(1))).strip()] = [cent(x) for x in re.findall(r"\$?[\d,]+\.\d\d", m.group(2))]
    out = {"base": {str(g): v[str(g)][0] for g in GRADI}}
    for lettera in "ABCDEF":
        out[lettera] = v[f"1115(1)({lettera})"]
    if [len(out[x]) for x in "ABCDEF"] != [1, 2, 2, 1, 1, 1]:
        raise SystemExit(f"{percorso.name}: importi 1115(1) inattesi {out}")
    return out


def quota(grado, importo):
    """38 U.S.C. 1115(2): stessa proporzione del grado; se non è un multiplo di 1 $, arrotondata per difetto al dollaro. Al 100 % l'importo pieno."""
    return importo if grado == 100 else (grado * importo // 10000) * 100


def attesi(av):
    """Ricostruisce le 108 celle dagli importi di legge dell'avviso (base + quote 1115)."""
    righe = {k: {} for k, *_ in STATI}
    agg = {k: {} for k, _ in AGGIUNTE}
    for g in GRADI[2:]:
        for k, coniuge, genitori, figlio, _ in STATI:
            x = av["base"][str(g)]
            if coniuge and figlio:
                x += quota(g, av["B"][0])
            elif coniuge:
                x += quota(g, av["A"][0])
            elif figlio:
                x += quota(g, av["C"][0])
            x += genitori * quota(g, av["D"][0])
            righe[k][str(g)] = x
        agg["child_u18"][str(g)] = quota(g, av["B"][1])
        agg["child_school"][str(g)] = quota(g, av["F"][0])
        agg["spouse_aa"][str(g)] = quota(g, av["E"][0]) - quota(g, av["A"][0])
    return righe, agg


def leggi_combinati(percorso):
    """38 CFR 4.25, Table I (XML dell'eCFR): {riga 19..94: [9 valori per le colonne 10..90]} e i paragrafi del testo."""
    t = percorso.read_text(encoding="utf-8")
    righe = {}
    for tr in re.findall(r"<TR[^>]*>(.*?)</TR>", t, re.S | re.I):
        c = [puro(x) for x in re.findall(r"<T[DH][^>]*>(.*?)</T[DH]>", tr, re.S | re.I)]
        if len(c) == 10 and all(re.fullmatch(r"\d+", x) for x in c):
            righe[c[0]] = [int(x) for x in c[1:]]
    return righe


def leggi_combinati_va(percorso):
    """La stessa tabella nella pagina va.gov "About disability ratings" (divisa in più tabelle)."""
    righe = {}
    for _, rr in tabelle_va(percorso.read_text(encoding="utf-8")):
        for r in rr:
            if len(r) == 10 and all(re.fullmatch(r"\d+", x) for x in r):
                righe[r[0]] = [int(x) for x in r[1:]]
    return righe


def combina_formula(a, b):
    """Testo del 38 CFR 4.25: resta (100 − a) % di efficienza, di cui b % va persa; valore combinato all'intero più vicino, metà in su."""
    return (2 * (10000 - (100 - a) * (100 - b)) + 100) // 200


def costruisci():
    out = {"letto_il": date.today().isoformat(), "gradi": GRADI, "stati": [k for k, *_ in STATI], "anni": {}}
    n = 0
    for anno, (f_va, f_av, _, pct) in ANNI.items():
        va = leggi_va(anno, GREZZI / f_va)
        av = leggi_avviso(GREZZI / f_av, pct)
        if va["base"] != av["base"]:
            raise SystemExit(f"{anno}: i 10 importi base di va.gov sono diversi dall'avviso nel Federal Register")
        righe, agg = attesi(av)
        diff = [(k, g) for k in righe for g in righe[k] if righe[k][g] != va["righe"][k].get(g)] + [(k, g) for k in agg for g in agg[k] if agg[k][g] != va["aggiunte"][k].get(g)]
        if diff:
            raise SystemExit(f"{anno}: celle di va.gov diverse da avviso + 38 U.S.C. 1115(2): {diff[:8]}")
        n_anno = sum(len(x) for x in va["righe"].values()) + sum(len(x) for x in va["aggiunte"].values()) + 2
        if n_anno != 122:
            raise SystemExit(f"{anno}: {n_anno} celle (attese 122: 2 + 96 + 24)")
        n += n_anno
        va["aumento_pct"] = pct
        va["legge"] = {k: av[k] for k in "ABCDEF"}
        out["anni"][anno] = va
    T = leggi_combinati(GREZZI / "ecfr_38_4_25.xml")
    Tva = leggi_combinati_va(GREZZI / "va_about_ratings.html")
    if sorted(T, key=int) != [str(i) for i in range(19, 95)]:
        raise SystemExit(f"Table I: righe {sorted(T, key=int)[:3]}…{len(T)}")
    # La copia di va.gov ha un refuso letto il 15/11/2026: riga 86, colonna 80 = 91 (il regolamento dice 97, e 97 dà il metodo scritto nel testo).
    # Vale il regolamento. Qualsiasi altra differenza, o la correzione del refuso, ferma la raccolta: va riguardata.
    diff_va = sorted((int(a), b, T[a][i], Tva.get(a, [None] * 9)[i]) for a in T for i, b in enumerate(range(10, 100, 10)) if T[a][i] != Tva.get(a, [None] * 9)[i])
    if diff_va != REFUSI_VA:
        raise SystemExit(f"Table I dell'eCFR e tabella di va.gov: differenze {diff_va[:8]} (attese {REFUSI_VA}): riguardare")
    storto = [(a, b, T[a][i]) for a in T for i, b in enumerate(range(10, 100, 10)) if T[a][i] != combina_formula(int(a), b)]
    if storto:
        raise SystemExit(f"Table I diversa dalla formula del testo: {storto[:8]}")
    out["combinati"] = {"colonne": list(range(10, 100, 10)), "righe": T, "differenze_va": [list(x) for x in diff_va]}
    api = json.loads((GREZZI / "fr_api_va_cola.json").read_text(encoding="utf-8"))
    ris = [{"numero": r["document_number"], "data": r["publication_date"], "titolo": r["title"]} for r in api.get("results", [])
           if re.fullmatch(r"Cost[- ]of[- ]Living Adjustments for Service-Connected Benefits", r["title"])]
    if not ris:
        raise SystemExit("API del Federal Register: nessun avviso del VA trovato")
    out["avvisi_fr"] = ris
    return out, n


def main():
    vecchio = json.loads((DATI / "fonti.json").read_text(encoding="utf-8"))
    if "--senza-rete" not in sys.argv:
        reg = scarica()
        vecchio.setdefault("grezzi", {}).update(reg)
        (DATI / "fonti.json").write_text(json.dumps(vecchio, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    out, n = costruisci()
    if "--senza-rete" in sys.argv and (DATI / "va.json").exists():
        out["letto_il"] = json.loads((DATI / "va.json").read_text(encoding="utf-8"))["letto_il"]
    (DATI / "va.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"va.json: {n} celle di va.gov = avvisi del Federal Register + 38 U.S.C. 1115(2); Table I {len(out['combinati']['righe'])} righe × 9 = va.gov = formula; "
          f"ultimo avviso del VA: {out['avvisi_fr'][0]['numero']} ({out['avvisi_fr'][0]['data']})")


if __name__ == "__main__":
    main()
