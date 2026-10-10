"""Soglia 6 (domanda): Google Autocomplete per "affidamenti/appalti aggiudicati" per Comune.

Usa l'endpoint pubblico https://suggestqueries.google.com/complete/search
(client=firefox, hl=it, gl=it), una richiesta ogni 1,5 s, per 30 Comuni:
20 Comuni medi (15.000-60.000 abitanti, non capoluoghi) e 10 capoluoghi di
provincia, estratti a caso con seme fisso dall'anagrafica di comuni_istat.py.

Per ogni Comune X prova 5 prefissi:
    "affidamenti comune di X", "affidamento diretto comune di X",
    "appalti aggiudicati X", "gare aggiudicate comune di X", "fornitori comune di X"
Una proposta è PERTINENTE se contiene il nome del Comune e parla di esiti
(affidament*, aggiudic*, esit*, determin*, "fornitori del comune"). Sono contate
a parte: "albo fornitori" (chi vuole ISCRIVERSI all'elenco fornitori: pubblico
vicino, ma non cerca chi ha vinto) e "solo bandi" (gare aperte: il prodotto
pubblica esiti, non bandi). Un Comune "passa" se ha almeno una proposta pertinente.

Per riclassificare un file già raccolto senza rifare le richieste:
    python3 -I autocomplete.py --riclassifica USCITA.json

Uso:
    python3 -I autocomplete.py COMUNI.tsv USCITA.json [--seme 20261010]
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import time
import unicodedata
import urllib.parse

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from comuni_istat import carica, estrai_medi  # noqa: E402

PREFISSI = ["affidamenti comune di {x}", "affidamento diretto comune di {x}",
            "appalti aggiudicati {x}", "gare aggiudicate comune di {x}",
            "fornitori comune di {x}"]
RE_ESITI = re.compile(r"affidament|aggiudic|esit|fornitor|determin")
RE_BANDI = re.compile(r"\bbando|\bbandi|\bgar[ae]\b|appalt")
UA = "Mozilla/5.0 (compatible; ChiLavoraColComune-test/0.1)"


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c)).replace("'", " ")


def suggerimenti(q):
    url = ("https://suggestqueries.google.com/complete/search?client=firefox&hl=it&gl=it&q="
           + urllib.parse.quote(q))
    for attesa in (0, 5, 20):
        time.sleep(attesa)
        r = subprocess.run(["curl", "-sS", "--max-time", "20", "-A", UA, url],
                           capture_output=True)
        try:
            return json.loads(r.stdout.decode("utf-8", "replace"))[1]
        except (ValueError, IndexError):
            continue
    return None


def classifica(s, nome):
    n = norm(s)
    if norm(nome) not in n:
        return "altro comune/generico"
    if "albo fornitori" in n or "elenco fornitori" in n:
        return "albo fornitori"
    if RE_ESITI.search(n):
        return "pertinente"
    if RE_BANDI.search(n):
        return "solo bandi"
    return "altro"


def riepiloga(out):
    for rec in out["comuni"]:
        for qq in rec["query"]:
            qq["classi"] = [classifica(s, rec["comune"]) for s in (qq["proposte"] or [])]
        coppie = [(s, k) for qq in rec["query"] for s, k in zip(qq["proposte"] or [], qq["classi"])]
        rec["pertinenti"] = sorted({s for s, k in coppie if k == "pertinente"})
        rec["albo_fornitori"] = sorted({s for s, k in coppie if k == "albo fornitori"})
        rec["solo_bandi"] = sorted({s for s, k in coppie if k == "solo bandi"})
        rec["passa"] = bool(rec["pertinenti"])
    c = out["comuni"]
    out["riepilogo"] = {
        "comuni_con_proposta_pertinente": sum(r["passa"] for r in c), "su": len(c),
        "medi": sum(r["passa"] for r in c if r["gruppo"] == "medio"),
        "capoluoghi": sum(r["passa"] for r in c if r["gruppo"] == "capoluogo"),
        "comuni_con_solo_albo_fornitori": sum(1 for r in c if r["albo_fornitori"] and not r["passa"]),
        "query_senza_risposta": sum(1 for r in c for q in r["query"] if q["proposte"] is None)}
    return out


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--riclassifica":
        out = riepiloga(json.load(open(sys.argv[2], encoding="utf-8")))
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        print(json.dumps(out["riepilogo"], ensure_ascii=False))
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("comuni")
    ap.add_argument("uscita")
    ap.add_argument("--seme", type=int, default=20261010)
    a = ap.parse_args()
    rows = carica(a.comuni)
    medi = estrai_medi(rows, 20, a.seme)
    capo = [r for r in rows if r["capoluogo"]]
    capo.sort(key=lambda r: r["istat"])
    import random
    capo = random.Random(a.seme).sample(capo, 10)
    out = {"fonte": "https://suggestqueries.google.com/complete/search?client=firefox&hl=it&gl=it",
           "data_verifica": dt.date.today().isoformat(), "seme": a.seme, "comuni": []}
    for gruppo, lista in (("medio", medi), ("capoluogo", capo)):
        for c in lista:
            rec = {"comune": c["comune"], "istat": c["istat"], "provincia": c["provincia_sigla"],
                   "popolazione": c["popolazione"], "gruppo": gruppo, "query": []}
            for p in PREFISSI:
                q = p.format(x=c["comune"].lower())
                sug = suggerimenti(q)
                time.sleep(1.5)
                rec["query"].append({"q": q, "proposte": sug,
                                     "classi": [classifica(s, c["comune"]) for s in (sug or [])]})
            out["comuni"].append(rec)
            print(f'{gruppo:9} {c["comune"][:28]:28} {c["popolazione"]:>8}', flush=True)
    riepiloga(out)
    with open(a.uscita, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(out["riepilogo"], ensure_ascii=False))


if __name__ == "__main__":
    main()
