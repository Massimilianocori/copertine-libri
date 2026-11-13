"""Legge i file ufficiali del Census Bureau (raccolta/_grezzi/) e scrive dati/naics.json, con i controlli sull'albero.

Uso (dalla radice del repository, dopo raccolta/fonti.py):
    python3 -I naics/raccolta/estrai.py

Richiede openpyxl (xlsx) e xlrd (xls delle concordanze più vecchie: `pip install xlrd`).
Si ferma (SystemExit) se: un codice non si legge, i file non hanno gli stessi codici, un codice non ha il padre giusto
(2 → 3 → 4 → 5 → 6 cifre, con i settori a intervallo 31-33, 44-45, 48-49), i conteggi per settore non sono quelli della
tabella ufficiale «Structure Summary Table», una riga dell'indice o di una concordanza punta a un codice inesistente.

Raccordo SIC: il Census pubblica una sola concordanza ufficiale tra SIC 1987 e NAICS 1997. Per arrivare ai codici 2022 si
seguono le concordanze ufficiali 1997→2002→2007→2012→2017→2022, passo per passo. «diretto» = il codice 2022 è lo stesso
codice del 1997 e a nessun passo si è diviso o ha ricevuto pezzi da altri codici: la riga SIC ufficiale vale così com'è.
Negli altri casi il collegamento è una nostra derivazione dai file ufficiali, e il sito lo dice.
"""
import json
import re
import sys
import warnings
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
try:
    import xlrd
except ImportError:  # pragma: no cover
    raise SystemExit("serve xlrd per i file .xls delle concordanze: pip install xlrd")

RADICE = Path(__file__).resolve().parent.parent
GREZZI = RADICE / "raccolta" / "_grezzi"
DATI = RADICE / "dati"
FJ = json.loads((DATI / "fonti.json").read_text(encoding="utf-8"))
# Refusi del file ufficiale (il sito usa il titolo del file della struttura). Un refuso nuovo ferma lo script.
REFUSI_NOTI = {("323120", "Support Activites for Printing")}
SETTORI_INTERVALLO = {"31": "31-33", "32": "31-33", "33": "31-33", "44": "44-45", "45": "44-45", "48": "48-49", "49": "48-49"}


def ferma(m):
    raise SystemExit("estrai.py: " + m)


def righe_xlsx(fid):
    wb = openpyxl.load_workbook(GREZZI / FJ["file"][fid]["file"], read_only=True)
    return list(wb.worksheets[0].iter_rows(values_only=True))


def righe_xls(fid, foglio=0):
    ws = xlrd.open_workbook(str(GREZZI / FJ["file"][fid]["file"])).sheet_by_index(foglio)
    return [ws.row_values(i) for i in range(ws.nrows)]


def cod(x):
    """Codice come testo: 111110.0 -> '111110'; '31-33' resta com'è; None/'' -> ''."""
    if x is None:
        return ""
    if isinstance(x, float):
        x = int(x)
    return str(x).strip()


def txt(x):
    return re.sub(r"[ \t]+", " ", str(x or "").replace("\r", "")).strip()


def titolo(x):
    """Titolo ufficiale senza la «T» finale (accordo trilaterale) e senza spazi finali."""
    t = txt(x)
    return (t[:-1].rstrip(), True) if t.endswith("T") and not t.endswith(" T") else (t, False)


def livello(c):
    return 2 if "-" in c else len(c)


def padre(c):
    l = livello(c)
    if l == 2:
        return None
    if l == 3:
        return SETTORI_INTERVALLO.get(c[:2], c[:2])
    return c[:-1]


def n6(c):
    """Codice NAICS dei file 1997→SIC: 5 cifre = industria a 6 cifre che finisce con 0."""
    c = cod(c)
    return c + "0" if len(c) == 5 else c


def main():
    # ---------------------------------------------------------------- codici e titoli
    r = righe_xlsx("codici")
    if not str(r[0][1]).startswith("2022 NAICS"):
        ferma(f"intestazione inattesa nel file dei codici: {r[0]}")
    codici, ordine = {}, []
    for x in r[2:]:
        if x[1] is None:
            continue
        c = cod(x[1])
        if not re.fullmatch(r"\d{2,6}|\d{2}-\d{2}", c):
            ferma(f"codice illeggibile «{x[1]}»")
        if c in codici:
            ferma(f"codice doppio {c}")
        t, _ = titolo(x[2])
        codici[c] = {"t": t}
        ordine.append(c)
    # struttura: indicatore di cambio e «T»
    r = righe_xlsx("struttura")
    if r[2][:3] != ("Change Indicator", "2022 NAICS Code", "2022 NAICS Title"):
        ferma(f"intestazione inattesa nella struttura: {r[2]}")
    vista = set()
    for x in r[3:]:
        if x[1] is None:
            continue
        c = cod(x[1])
        if c not in codici:
            ferma(f"struttura: codice {c} assente dal file dei codici")
        t, tri = titolo(x[2])
        if t != codici[c]["t"]:
            ferma(f"struttura: titolo di {c} diverso («{t}» / «{codici[c]['t']}»)")
        codici[c]["ind"] = txt(x[0])
        codici[c]["T"] = tri
        vista.add(c)
    if vista != set(codici):
        ferma(f"struttura e file dei codici diversi: {sorted(set(codici) ^ vista)[:5]}")
    # albero
    for i, c in enumerate(ordine):
        v = codici[c]
        v["l"], v["p"], v["o"] = livello(c), padre(c), i
        if v["p"] is not None and v["p"] not in codici:
            ferma(f"{c}: padre {v['p']} inesistente")
        if v["p"] is not None and codici[v["p"]]["l"] != v["l"] - 1:
            ferma(f"{c}: padre {v['p']} al livello sbagliato")
    figli = defaultdict(list)
    for c in ordine:
        if codici[c]["p"]:
            figli[codici[c]["p"]].append(c)
    for c in ordine:
        if codici[c]["l"] < 6 and not figli[c]:
            ferma(f"{c}: ramo senza figli prima del sesto livello")
    # conteggi ufficiali
    r = righe_xlsx("conteggi")
    if r[0][:6] != ("Sector", "Name", "Subsectors (3-digit)", "Industry Groups (4-digit)", "NAICS Industries (5-digit)", "6-digit Industries"):
        ferma(f"intestazione inattesa nella tabella dei conteggi: {r[0]}")
    ufficiali = {}
    for x in r[2:]:
        if x[1] is None:
            continue
        chiave = "Totale" if x[1] == "Total" else cod(x[0])
        ufficiali[chiave] = {"nome": txt(x[1]), "3": x[2], "4": x[3], "5": x[4], "6_dettaglio_usa": x[5], "6_come_5": x[6], "6": x[7]}

    def sotto(c):
        return [c] + [y for f in figli[c] for y in sotto(f)]
    settori = [c for c in ordine if codici[c]["l"] == 2]
    for s in settori:
        if s not in ufficiali:
            ferma(f"settore {s} assente dalla tabella dei conteggi")
        cnt = Counter(codici[y]["l"] for y in sotto(s))
        u = ufficiali[s]
        mio = {"3": cnt[3], "4": cnt[4], "5": cnt[5], "6": cnt[6]}
        sei_come5 = sum(1 for y in sotto(s) if codici[y]["l"] == 6 and len(figli[codici[y]["p"]]) == 1 and y.endswith("0"))
        if mio != {k: u[k] for k in mio} or sei_come5 != u["6_come_5"]:
            ferma(f"settore {s}: conteggi {mio} (6 come 5: {sei_come5}) diversi da quelli ufficiali {u}")
        if u["nome"] != codici[s]["t"]:
            ferma(f"settore {s}: nome «{u['nome']}» diverso dal titolo «{codici[s]['t']}»")
    tot = Counter(v["l"] for v in codici.values())
    u = ufficiali["Totale"]
    if (tot[2], tot[3], tot[4], tot[5], tot[6]) != (len(settori), u["3"], u["4"], u["5"], u["6"]) or len(settori) != 20:
        ferma(f"totali {dict(tot)} diversi da quelli ufficiali {u}")
    # ---------------------------------------------------------------- descrizioni, esempi, rimandi, indice
    r = righe_xlsx("descrizioni")
    if r[0] != ("Code", "Title", "Description"):
        ferma(f"intestazione inattesa nelle descrizioni: {r[0]}")
    viste = set()
    for x in r[1:]:
        c = cod(x[0])
        if c not in codici:
            ferma(f"descrizioni: codice {c} inesistente")
        t, _ = titolo(x[1])
        if t != codici[c]["t"]:
            ferma(f"descrizioni: titolo di {c} diverso («{t}»)")
        viste.add(c)
        d = str(x[2] or "").replace("\r", "")
        v = codici[c]
        v["d"], v["es"], v["vedi"] = [], [], ""
        if d.strip() in ("", "NULL"):
            continue
        m = re.fullmatch(r"\s*See industry description for (\d{6})\.\s*", d)
        if m:
            v["vedi"] = m.group(1)
            continue
        m = re.search(r"\n*\s*Cross-References\.(?:\s*((?:Government )?[Ee]stablishments primarily engaged in)--)?\s*$", d.rstrip())
        if m:
            v["xr_lead"] = m.group(1) or ""
            d = d.rstrip()[:m.start()]
        if "Cross-References" in d:
            ferma(f"descrizioni: {c} con «Cross-References» in un punto inatteso")
        corpo, _, esempi = d.partition("Illustrative Examples:")
        v["d"] = [txt(p) for p in re.split(r"\n\s*\n", corpo) if txt(p)]
        if v["d"] and v["d"][0] == "The Sector as a Whole":
            v["d"] = v["d"][1:]
        v["es"] = [txt(e) for e in esempi.split("\n") if txt(e)]
    if viste != set(codici):
        ferma(f"descrizioni: codici mancanti {sorted(set(codici) - viste)[:5]}")
    for c, v in codici.items():
        if v["vedi"] and (v["vedi"] not in codici or codici[v["vedi"]]["p"] != c):
            ferma(f"{c}: rimando «See industry description for {v['vedi']}» non verso il proprio figlio")
    r = righe_xlsx("rimandi")
    if r[0] != ("Code", "Cross-Reference"):
        ferma(f"intestazione inattesa nei rimandi: {r[0]}")
    for c in codici.values():
        c["xr"] = []
    for x in r[1:]:
        c = cod(x[0])
        if c not in codici:
            ferma(f"rimandi: codice {c} inesistente")
        codici[c]["xr"].append(txt(x[1]))
    n_xr = len(r) - 1
    r = righe_xlsx("indice")
    if r[0] != ("NAICS22", "INDEX ITEM DESCRIPTION"):
        ferma(f"intestazione inattesa nell'indice: {r[0]}")
    for c in codici.values():
        c["idx"] = []
    vedi_tipo = []
    for x in r[1:]:
        c = cod(x[0])
        if c == "******":
            vedi_tipo.append(txt(x[1]))
            continue
        if c not in codici or codici[c]["l"] != 6:
            ferma(f"indice: codice {c} non è un'industria a 6 cifre")
        codici[c]["idx"].append(txt(x[1]))
    n_idx = len(r) - 1 - len(vedi_tipo)
    # ---------------------------------------------------------------- concordanza 2022 ↔ 2017
    r = righe_xlsx("c22_17")
    if not (str(r[2][0]).startswith("2022 NAICS Code") and str(r[2][2]).startswith("2017 NAICS Code")):
        ferma(f"intestazione inattesa nella concordanza 2022→2017: {r[2]}")
    c22_17, refusi = [], []
    for x in r[3:]:
        if x[0] is None:
            continue
        a, b = cod(x[0]), cod(x[2])
        if a not in codici or codici[a]["l"] != 6 or not re.fullmatch(r"\d{6}", b):
            ferma(f"concordanza 2022→2017: riga illeggibile {x[:4]}")
        if txt(x[1]) != codici[a]["t"]:
            if (a, txt(x[1])) not in REFUSI_NOTI:
                ferma(f"concordanza 2022→2017: titolo di {a} diverso («{txt(x[1])}»)")
            refusi.append([a, txt(x[1]), codici[a]["t"]])
        c22_17.append([a, b, txt(x[3])])
    sei = {c for c, v in codici.items() if v["l"] == 6}
    if {x[0] for x in c22_17} != sei:
        ferma("concordanza 2022→2017: non copre tutte le industrie a 6 cifre")
    r = righe_xlsx("c17_22")
    c17_22 = []
    for x in r[3:]:
        if x[0] is None:
            continue
        a, b = cod(x[0]), cod(x[2])
        if b not in sei or not re.fullmatch(r"\d{6}", a):
            ferma(f"concordanza 2017→2022: riga illeggibile {x[:4]}")
        c17_22.append([a, txt(x[1]), b])
    if {(a, b) for a, _, b in c17_22} != {(b, a) for a, b, _ in c22_17}:
        ferma("le concordanze 2017→2022 e 2022→2017 non hanno le stesse coppie")
    # ---------------------------------------------------------------- catena verso il 1997 e SIC
    passi = []  # dal più recente: (anno_vecchio, {nuovo: {vecchi}}, {vecchio: {nuovi}})

    def coppie(righe, i_vecchio, i_nuovo, prima):
        b, f = defaultdict(set), defaultdict(set)
        for x in righe[prima:]:
            a, n = cod(x[i_vecchio]), cod(x[i_nuovo])
            if not (re.fullmatch(r"\d{6}", a) and re.fullmatch(r"\d{6}", n)):
                continue
            b[n].add(a)
            f[a].add(n)
        return b, f
    b, f = coppie([[x[1], x[0]] for x in c22_17], 0, 1, 0)
    passi.append(("2017", b, f))
    passi.append(("2012",) + coppie(righe_xlsx("c12_17"), 0, 2, 3))
    passi.append(("2007",) + coppie(righe_xls("c07_12"), 0, 2, 3))
    passi.append(("2002",) + coppie(righe_xls("c02_07"), 0, 2, 3))
    r97 = righe_xls("c97_02", 1)
    if r97[0][:3] != ["NAICS97", "1997 NAICS Title", "NAICS02"]:
        ferma(f"intestazione inattesa nella concordanza 1997→2002: {r97[0]}")
    passi.append(("1997",) + coppie(r97, 0, 2, 1))
    for anno, bb, ff in passi:
        if not bb:
            ferma(f"concordanza verso il {anno} vuota")
    # NAICS 1997 → SIC 1987
    r = righe_xls("naics97_sic")
    if r[0][:6] != ["1997 NAICS", "NAICS Part Indicator", "1997 NAICS Title", "SIC", "SIC Part Indicator", "SIC Title and Part Description"]:
        ferma(f"intestazione inattesa in 1997 NAICS → SIC: {r[0]}")
    sic_di_97 = defaultdict(list)
    for x in r[1:]:
        n = n6(x[0])
        s = cod(x[3])
        if not re.fullmatch(r"\d{6}", n) or not s:
            continue
        s = s.zfill(4)
        if not re.fullmatch(r"\d{4}", s):
            ferma(f"1997 NAICS → SIC: codice SIC illeggibile {x}")
        sic_di_97[n].append({"sic": s, "parte": txt(x[4]) == "*", "t": txt(x[5])})
    # SIC 1987 → NAICS 1997 (titoli SIC e lato SIC)
    r = righe_xls("sic_naics97")
    if r[0][:5] != ["SIC", "Part Indicator", "SIC Titles and Part Descriptions", "1997 NAICS", "1997 NAICS Titles and Part Indicators"]:
        ferma(f"intestazione inattesa in SIC → 1997 NAICS: {r[0]}")
    sic = {}
    gruppi_sic = {}
    for x in r[1:]:
        s = cod(x[0])
        if not s:
            continue
        if len(s) == 2:
            gruppi_sic[s] = txt(x[2])
            continue
        s = s.zfill(4)
        if not re.fullmatch(r"\d{4}", s):
            ferma(f"SIC → 1997 NAICS: codice illeggibile {x}")
        voce = sic.setdefault(s, {"t": "", "n97": []})
        if txt(x[1]) == "":
            if voce["t"] and voce["t"] != txt(x[2]):
                ferma(f"SIC {s}: due titoli")
            voce["t"] = txt(x[2])
            if cod(x[3]):
                voce["n97"].append({"n": n6(x[3]), "parte": "", "t97": txt(x[4])})
        else:
            voce["n97"].append({"n": n6(x[3]), "parte": re.sub(r"^\.\s*", "", txt(x[2])), "t97": txt(x[4])})
    for s, v in sic.items():
        if not v["t"]:
            ferma(f"SIC {s} senza titolo")

    def indietro(c22):
        """Codici 1997 raggiunti da un codice 2022 risalendo le concordanze; diretto = identità 1:1 a ogni passo."""
        attuali, diretto = {c22}, True
        for _, bb, ff in passi:
            nuovi = set()
            for c in attuali:
                nuovi |= bb.get(c, set())
            if diretto and not (bb.get(c22) == {c22} and ff.get(c22) == {c22}):
                diretto = False
            attuali = nuovi
        return attuali, diretto

    def avanti(c97):
        attuali = {c97}
        for _, bb, ff in reversed(passi):
            nuovi = set()
            for c in attuali:
                nuovi |= ff.get(c, set())
            attuali = nuovi
        return attuali
    sic_di_22 = {}
    for c in sorted(sei):
        v97, diretto = indietro(c)
        righe = []
        for n in sorted(v97):
            for x in sic_di_97.get(n, []):
                righe.append({"sic": x["sic"], "parte": x["parte"], "t": x["t"], "n97": n})
        visti, uniche = set(), []
        for x in sorted(righe, key=lambda y: (y["sic"], y["n97"])):
            k = (x["sic"], x["t"], x["n97"])
            if k not in visti:
                visti.add(k)
                uniche.append(x)
        sic_di_22[c] = {"diretto": diretto, "n97": sorted(v97), "righe": uniche}
    for s, v in sic.items():
        for x in v["n97"]:
            x["n22"] = sorted(avanti(x["n"])) if re.fullmatch(r"\d{6}", x["n"]) else []
            if any(y not in sei for y in x["n22"]):
                ferma(f"SIC {s}: la catena porta a un codice 2022 inesistente")
    # titoli 2017 dei codici a 6 cifre
    t17 = {}
    for a, t, _ in c17_22:
        t17.setdefault(a, re.split(r"\s*\(pt\)|\n", t)[0].strip())
    out = {
        "_nota": "Scritto da raccolta/estrai.py dai file ufficiali del Census Bureau (dati/fonti.json). Non modificare a mano.",
        "codici": codici,
        "ordine": ordine,
        "conteggi_ufficiali": ufficiali,
        "indice_vedi_tipo": vedi_tipo,
        "c22_17": c22_17,
        "c17_22": c17_22,
        "titoli_2017": t17,
        "sic_di_22": sic_di_22,
        "sic": sic,
        "gruppi_sic": gruppi_sic,
        "refusi_ufficiali": refusi,
        "numeri": {"righe_indice": n_idx, "righe_rimandi": n_xr, "righe_c22_17": len(c22_17)},
    }
    (DATI / "naics.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    dir_ = sum(1 for v in sic_di_22.values() if v["diretto"])
    con_sic = sum(1 for v in sic_di_22.values() if v["righe"])
    print(f"{len(codici)} codici NAICS 2022 ({dict(sorted(tot.items()))}), conteggi = tabella ufficiale; {n_idx} voci dell'indice "
          f"(+{len(vedi_tipo)} rimandi «see type»), {n_xr} rimandi; {len(c22_17)} righe 2022→2017; {len(sic)} codici SIC; "
          f"{con_sic} industrie 2022 con SIC ({dir_} dirette, {con_sic - dir_ if con_sic >= dir_ else 0} via catena)")


if __name__ == "__main__":
    main()
