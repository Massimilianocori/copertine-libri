"""Copertura su campione largo: quanti CIG citati nelle determine dei Comuni
compaiono nei file delta ANAC.

Prende i file di atti_maggioli.py, raccoglie i CIG distinti citati negli oggetti
e tiene solo quelli generati nell'intervallo coperto dai delta scaricati (il
CIG della piattaforma PCP cresce nel tempo: l'intervallo [--min, --max] si
ricava dall'indice, es. 5° percentile di giugno e 95° percentile di agosto).
Poi li cerca nell'indice TSV di analizza_mese.py. Stampa per ente: CIG citati,
CIG nell'intervallo, trovati, quota; e salva l'elenco dei mancanti.

Ripartisce anche i CIG per procedura dichiarata nell'oggetto della determina:
"gara" (procedura aperta/negoziata/ristretta, aggiudicazione dopo gara) oppure
"affidamento diretto" (art. 50 c.1 lett. a/b, trattativa diretta, ordine MePA):
è un indicatore indiretto della fascia di importo (le gare stanno quasi sempre
sopra 40.000 euro, gli affidamenti diretti quasi sempre sotto).

Uso:
    python3 -I copertura_cig.py --atti A1.json ... --indice indice.tsv \
        --min BBDC9B85BD --max BCCC975CB6 --uscita copertura.json
"""
import argparse
import json
import re

RE_GARA = re.compile(r"PROCEDURA (APERTA|NEGOZIATA|RISTRETTA)|GARA|AGGIUDICA", re.I)
RE_DIRETTO = re.compile(r"AFFIDAMENTO DIRETTO|ART\.? ?50,? COMMA 1,? LETT|TRATTATIVA DIRETTA|ORDINE DIRETTO|ODA|MEPA|ME\.PA", re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--atti", nargs="+", required=True)
    ap.add_argument("--indice", required=True)
    ap.add_argument("--min", required=True)
    ap.add_argument("--max", required=True)
    ap.add_argument("--uscita", required=True)
    a = ap.parse_args()
    per_ente = {}
    tutti = set()
    tipo = {}
    for p in a.atti:
        d = json.load(open(p, encoding="utf-8"))
        for x in d["atti"]:
            for c in x["cig"]:
                t = "gara" if RE_GARA.search(x["oggetto"]) else ("affidamento diretto" if RE_DIRETTO.search(x["oggetto"]) else "non dichiarata")
                if tipo.get(c) in (None, "non dichiarata"):
                    tipo[c] = t
        cig = {c for x in d["atti"] for c in x["cig"]}
        dentro = {c for c in cig if a.min <= c <= a.max}
        per_ente[d["host"].split(".")[0]] = {"cig_citati": len(cig), "cig_nell_intervallo": sorted(dentro)}
        tutti |= dentro
    idx = {}
    with open(a.indice, encoding="utf-8") as f:
        intest = f.readline().rstrip("\n").split("\t")
        for line in f:
            if line[:10] in tutti:
                r = dict(zip(intest, line.rstrip("\n").split("\t")))
                idx[line[:10]] = {k: r[k] for k in ("cf_ente", "ente", "data_pubblicazione", "primo_file", "importo_lotto")}
    out = {"intervallo": [a.min, a.max], "enti": {}}
    for e, v in per_ente.items():
        dentro = v["cig_nell_intervallo"]
        trovati = [c for c in dentro if c in idx]
        enti_anac = sorted({idx[c]["ente"] for c in trovati})
        out["enti"][e] = {"cig_citati": v["cig_citati"], "cig_nell_intervallo": len(dentro), "trovati": len(trovati),
                          "quota_%": round(100 * len(trovati) / len(dentro), 1) if dentro else None,
                          "enti_anac_dei_trovati": enti_anac,
                          "mancanti": [c for c in dentro if c not in idx]}
        print(e, v["cig_citati"], len(dentro), len(trovati), out["enti"][e]["quota_%"], enti_anac[:3])
    tot_d = sum(len(v["cig_nell_intervallo"]) for v in per_ente.values())
    tot_t = sum(o["trovati"] for o in out["enti"].values())
    out["totale"] = {"cig_nell_intervallo": tot_d, "trovati": tot_t, "quota_%": round(100 * tot_t / tot_d, 1) if tot_d else None}
    out["per_procedura_dichiarata"] = {}
    for t in ("gara", "affidamento diretto", "non dichiarata"):
        cc = [c for c in tutti if tipo.get(c) == t]
        tr = sum(1 for c in cc if c in idx)
        out["per_procedura_dichiarata"][t] = {"cig": len(cc), "trovati": tr,
                                              "quota_%": round(100 * tr / len(cc), 1) if cc else None}
    print(out["totale"])
    print(out["per_procedura_dichiarata"])
    with open(a.uscita, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
