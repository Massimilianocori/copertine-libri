"""Legge i file ISTAT scaricati da fonti.py e scrive ateco/dati/ateco.json (struttura, note, raccordo, tabella operativa)
e ateco/dati/coefficienti.json (gruppi del regime forfetario per ogni codice ATECO 2022).

Uso (dalla radice del repository):
    python3 -I ateco/raccolta/estrai.py

Si ferma se un'intestazione di colonna cambia, se l'albero non torna (padre mancante, livello sbagliato, codici doppi)
o se un codice ATECO 2022 cade in nessuno o in più di un gruppo dei coefficienti.
Tutti i testi restano come li scrive ISTAT (si tolgono solo gli spazi in testa e in coda).
"""
import json
import re
import sys
import warnings
from pathlib import Path

import openpyxl

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
RADICE = Path(__file__).resolve().parent.parent
GREZZI = RADICE / "raccolta" / "_grezzi"
DATI = RADICE / "dati"

INTESTAZIONI = {
    "struttura": ("ATECO 2025 Struttura", ["ORDINE_CODICE_ATECO_2025", "CODICE_ATECO_2025", "TITOLO_ITALIANO_ATECO_2025", "TITOLO_INGLESE_ATECO_2025",
                                           "TITOLO_TEDESCO_ATECO_2025", "GERARCHIA_ATECO_2025", "CODICE_PADRE_ATECO_2025", "GERARCHIA_PADRE_ATECO_2025"]),
    "note": ("Note esplicative ATECO 2025", ["ORDINE_CODICE_ATECO_2025", "CODICE_ATECO_2025", "TITOLO_ITALIANO_ATECO_2025", "TITOLO_INGLESE_ATECO_2025",
                                             "GERARCHIA_ATECO_2025", "CODICE_PADRE_ATECO_2025", "GERARCHIA_PADRE_ATECO_2025", "NOTA_ITALIANO_ATECO_2025",
                                             "NOTA_INGLESE_ATECO_2025", "CODICE_TIPO_NOTA", "CODICE_SOTTOTIPO_NOTA", "CODICE_PROVENIENZA_NOTA", "ORDINE_NOTA",
                                             "CODICE_NOTA_COLLEGATO"]),
    "raccordo": ("ATECO 2025 vs ATECO 2022", ["ORDINE_CODICE_ATECO_2025", "CODICE_ATECO_2025", "TITOLO_ITALIANO_ATECO_2025", "COPERTURA_ATECO_2025",
                                              "ORDINE_CODICE_ATECO_2022", "CODICE_ATECO_2022", "TITOLO_ITALIANO_ATECO_2022", "COPERTURA_ATECO_2022", "GERARCHIA",
                                              "NUMERO_CORR_ATECO_2025", "NUMERO_CORR_ATECO_2022", "CONTENUTO_COMUNE_ITALIANO", "CODICE_PROVENIENZA",
                                              "AGGIORNAMENTO_2026"]),
    "operativa": ("Tabella operativa", ["ORDINE_CODICE_ATECO_2022", "CODICE_ATECO_2022", "TITOLO_ATECO_2022", "GERARCHIA_ATECO_2022", "NUMERO_CORR_ATECO_2022",
                                        "SOTTOTIPOLOGIA", "TIPO_RICODIFICA", "CODICE_ATECO_2025_RAPPRESENTATIVO", "TITOLO_ATECO_2025_RAPPRESENTATIVO",
                                        "CODICE_ATECO_2025_RAPPRESENTATIVO_SISTEMA_CAMERALE", "TITOLO_ATECO_2025_RAPPRESENTATIVO_SISTEMA_CAMERALE",
                                        "AGGIORNAMENTO_2026_RAPPRESENTATIVO", "AGGIORNAMENTO_2026_RAPPRESENTATIVO_SISTEMA_CAMERALE"]),
}


def s(x):
    """Testo della cella senza spazi in testa e in coda; «_x000D_» (a capo di Excel scritto come testo) diventa un a capo."""
    if x is None:
        return ""
    t = str(x).replace("_x000D_\n", "\n").replace("_x000D_", "\n").replace("\r\n", "\n").replace("\r", "\n")
    return t.strip()


def leggi(fid):
    foglio, attese = INTESTAZIONI[fid]
    wb = openpyxl.load_workbook(GREZZI / f"{fid}.xlsx", read_only=True)
    righe = list(wb[foglio].iter_rows(values_only=True))
    intest = [s(x) for x in righe[0]][:len(attese)]
    if intest != attese:
        raise SystemExit(f"{fid}: intestazioni cambiate\n  attese {attese}\n  trovate {intest}")
    return [dict(zip(attese, r)) for r in righe[1:] if any(v is not None and s(v) for v in r)]


def livello_atteso(c):
    if re.fullmatch(r"[A-V]", c):
        return 1
    return {2: 2, 4: 3, 5: 4, 7: 5, 8: 6}.get(len(c))


# ------------------------------------------------------------------ coefficienti del forfetario (allegato 4 / allegato D)
def regole_coefficienti(tabella):
    """[(progressivo, gruppo, codici, coefficiente)] -> [(progressivo, token)] dove token è ('pref', '47.81') o ('da', '46.2', '46.9')."""
    regole = []
    for n, gruppo, codici, coeff in tabella:
        for tok in re.sub(r"[()]", " ", codici).split("-"):
            tok = tok.strip()
            if not tok:
                continue
            m = re.fullmatch(r"da (\d{2}\.\d) a (\d{2}\.\d)", tok)
            if m:
                regole.append((n, ("da", m.group(1), m.group(2))))
            elif re.fullmatch(r"\d{2}(\.\d{1,2})?", tok):
                regole.append((n, ("pref", tok)))
            else:
                raise SystemExit(f"coefficienti: voce non capita «{tok}» nel gruppo {n}")
    return regole


def gruppi_di(codice, regole):
    out = set()
    for n, r in regole:
        # i codici hanno la forma 47, 47.9, 47.91, 47.91.1, 47.91.10: un prefisso del testo di legge li contiene tutti
        if r[0] == "pref" and codice.startswith(r[1]):
            out.add(n)
        elif r[0] == "da" and len(codice) >= 4 and r[1] <= codice[:4] <= r[2]:
            out.add(n)
    return out


def main():
    fonti = json.loads((DATI / "fonti.json").read_text(encoding="utf-8"))
    st = leggi("struttura")
    codici = {}
    for r in st:
        c = s(r["CODICE_ATECO_2025"])
        if c in codici:
            raise SystemExit(f"codice doppio {c}")
        liv = int(r["GERARCHIA_ATECO_2025"])
        if liv != livello_atteso(c):
            raise SystemExit(f"{c}: livello {liv} non coerente con la forma del codice")
        codici[c] = {"o": int(r["ORDINE_CODICE_ATECO_2025"]), "l": liv, "p": s(r["CODICE_PADRE_ATECO_2025"]) or None,
                     "it": s(r["TITOLO_ITALIANO_ATECO_2025"]), "en": s(r["TITOLO_INGLESE_ATECO_2025"]), "de": s(r["TITOLO_TEDESCO_ATECO_2025"]),
                     "note": []}
    for c, v in codici.items():
        if v["l"] > 1 and (v["p"] not in codici or codici[v["p"]]["l"] != v["l"] - 1):
            raise SystemExit(f"{c}: padre {v['p']} mancante o di livello sbagliato")
    note = leggi("note")
    n_note = 0
    for r in note:
        c = s(r["CODICE_ATECO_2025"])
        if c not in codici:
            raise SystemExit(f"nota per un codice che non è nella struttura: {c}")
        if s(r["TITOLO_ITALIANO_ATECO_2025"]) != codici[c]["it"]:
            raise SystemExit(f"{c}: titolo diverso tra struttura e note")
        if not s(r["NOTA_ITALIANO_ATECO_2025"]):
            continue
        rif = [x.strip() for x in s(r["CODICE_NOTA_COLLEGATO"]).split(";") if x.strip()]
        codici[c]["note"].append({"t": int(r["CODICE_TIPO_NOTA"]), "s": s(r["CODICE_SOTTOTIPO_NOTA"]), "prov": int(r["CODICE_PROVENIENZA_NOTA"]),
                                  "n": int(r["ORDINE_NOTA"]), "it": s(r["NOTA_ITALIANO_ATECO_2025"]), "rif": rif})
        n_note += 1
    rac = []
    for r in leggi("raccordo"):
        c25 = s(r["CODICE_ATECO_2025"])
        if c25 not in codici:
            raise SystemExit(f"raccordo: codice 2025 sconosciuto {c25}")
        rac.append({"c25": c25, "cop25": s(r["COPERTURA_ATECO_2025"]), "c22": s(r["CODICE_ATECO_2022"]) or None, "t22": s(r["TITOLO_ITALIANO_ATECO_2022"]),
                    "cop22": s(r["COPERTURA_ATECO_2022"]), "n25": int(r["NUMERO_CORR_ATECO_2025"] or 0), "n22": int(r["NUMERO_CORR_ATECO_2022"] or 0),
                    "comune": s(r["CONTENUTO_COMUNE_ITALIANO"]), "prov": int(r["CODICE_PROVENIENZA"]), "agg2026": s(r["AGGIORNAMENTO_2026"]) == "SI"})
    op = {}
    for r in leggi("operativa"):
        c22 = s(r["CODICE_ATECO_2022"])
        rap, cam = s(r["CODICE_ATECO_2025_RAPPRESENTATIVO"]), s(r["CODICE_ATECO_2025_RAPPRESENTATIVO_SISTEMA_CAMERALE"])
        for x in (rap, cam):
            if x != "n.d." and x not in codici:
                raise SystemExit(f"operativa: codice 2025 sconosciuto {x} per {c22}")
        op[c22] = {"t22": s(r["TITOLO_ATECO_2022"]), "l": int(r["GERARCHIA_ATECO_2022"]), "n": int(r["NUMERO_CORR_ATECO_2022"]),
                   "tipo": s(r["SOTTOTIPOLOGIA"]), "ric": s(r["TIPO_RICODIFICA"]), "rap": None if rap == "n.d." else rap,
                   "cam": None if cam == "n.d." else cam,
                   "agg": s(r["AGGIORNAMENTO_2026_RAPPRESENTATIVO"]) == "SI", "agg_cam": s(r["AGGIORNAMENTO_2026_RAPPRESENTATIVO_SISTEMA_CAMERALE"]) == "SI"}
    c22_rac = {x["c22"] for x in rac if x["c22"]}
    if c22_rac != set(op):
        raise SystemExit(f"codici 2022 diversi tra raccordo e tabella operativa: {sorted(c22_rac ^ set(op))[:10]}")
    for x in rac:
        if x["c22"] and x["t22"] != op[x["c22"]]["t22"]:
            # ISTAT scrive alcuni titoli 2022 in maiuscolo nel raccordo: si tiene quello della tabella operativa
            if x["t22"].lower() != op[x["c22"]]["t22"].lower():
                print(f"AVVISO: titolo 2022 di {x['c22']} diverso tra raccordo e tabella operativa", file=sys.stderr)
    out = {"_nota": "Scritto da raccolta/estrai.py dai file ISTAT (struttura, note esplicative, tavola di raccordo 2026, tabella operativa 2026). Testi come li scrive ISTAT.",
           "fonti": {k: fonti["file"][k]["sha256"] for k in ("struttura", "note", "raccordo", "operativa")},
           "codici": codici, "raccordo": rac, "operativa": op}
    (DATI / "ateco.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

    regole = regole_coefficienti(fonti["coefficienti"])
    gruppi = {}
    for c22, v in op.items():
        if v["l"] < 4:
            continue
        g = gruppi_di(c22, regole)
        if len(g) != 1:
            raise SystemExit(f"coefficienti: il codice ATECO 2022 {c22} cade in {sorted(g) or 'nessun'} gruppo")
        gruppi[c22] = g.pop()
    tab = {str(n): {"gruppo": g, "codici_ateco_2007": cod, "coefficiente": int(k.rstrip("%"))} for n, g, cod, k in fonti["coefficienti"]}
    (DATI / "coefficienti.json").write_text(json.dumps({
        "_nota": "Scritto da raccolta/estrai.py. Gruppo del regime forfetario (allegato 4 L. 190/2014 = allegato D D.Lgs. 117/2026) per ogni codice "
                 "ATECO 2022 di livello classe o inferiore. Il raccordo ATECO 2007 – aggiornamento 2022 non cambia divisioni, gruppi e classi rispetto ad ATECO 2007.",
        "tabella": tab, "gruppo_per_codice_2022": gruppi}, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    per_liv = {}
    for v in codici.values():
        per_liv[v["l"]] = per_liv.get(v["l"], 0) + 1
    print(f"{len(codici)} codici ATECO 2025 {per_liv}, {n_note} note, {len(rac)} righe di raccordo, {len(op)} codici 2022 nella tabella operativa, "
          f"{len(gruppi)} codici 2022 con il gruppo del forfetario")


if __name__ == "__main__":
    main()
