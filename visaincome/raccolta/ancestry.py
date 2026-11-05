"""UK Ancestry visa per nazionalità: visti concessi, rifiutati, ritirati e decaduti per anno (pagina /uk-ancestry-visa/, dal 5/11/2026).
Scrive visaincome/dati/ancestry.json.

Uso (dalla radice del repository):
    python3 visaincome/raccolta/ancestry.py              # legge il file del Home Office già in raccolta/_grezzi/ e la guida GOV.UK
    python3 visaincome/raccolta/ancestry.py --domanda    # rifà anche l'autocompletamento di Google

Fonti:
1. Home Office, "Entry clearance visa applications and outcomes detailed datasets" (lo stesso file di dati/rifiuti.json, controllato
   con lo SHA-256), foglio Data_Vis_D02, sottotipo "UK Ancestry" (colonna "Visa type subgroup", gruppo Work): tutti i trimestri dal 2005,
   per nazionalità, tipo di richiedente (principale o familiare) ed esito. Controllo: negli ultimi 8 trimestri, nazionalità per nazionalità,
   i concessi e i rifiutati non superano il gruppo Work di dati/rifiuti.json. OGL v3.0.
2. GOV.UK, guida "UK Ancestry visa" (Content API, /ancestry-visa): chi può fare domanda, nonno nato nel Regno Unito, 17 anni,
   5 anni, tariffa, tempi. Ogni frase usata ha il FRAMMENTO in LETTURE; se un frammento manca il JSON NON viene aggiornato.
"""
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from infermieri import FILE_HO, controllo_ho, fonte_ho, get, leggi_sottotipi, nuova_domanda, per_anno, testo_html  # noqa: E402
from rifiuti import RADICE  # noqa: E402

USCITA = RADICE / "dati" / "ancestry.json"
SOTTOTIPO = "UK Ancestry"
GUIDA = "/ancestry-visa"
API = "https://www.gov.uk/api/content"
LETTURE = {
    "chi": {"valore": ["a Commonwealth citizen", "a British overseas citizen", "a British overseas territories citizen", "a British national (overseas)", "a citizen of Zimbabwe"],
            "frammento": "You can apply for a UK Ancestry visa if you’re one of the following: a Commonwealth citizen a British overseas citizen a British overseas territories citizen a British national (overseas) a citizen of Zimbabwe"},
    "nonno": {"valore": True, "frammento": "prove one of your grandparents was born in the UK, the Channel Islands or the Isle of Man"},
    "irlanda": {"valore": "1922-03-31", "frammento": "in the UK, the Channel Islands or the Isle of Man before 31 March 1922 in what is now Ireland"},
    "patrigno": {"valore": True, "frammento": "You cannot claim UK ancestry through step-parents."},
    "eta": {"valore": 17, "frammento": "are 17 or over"},
    "lavoro": {"valore": True, "frammento": "can and plan to work in the UK"},
    "soldi": {"valore": True, "frammento": "have enough money without help from public funds to support and house yourself and any dependants"},
    "tassa": {"valore": 726, "frammento": "A UK Ancestry visa costs £726."},
    "ihs": {"valore": True, "frammento": "You may also have to pay the healthcare surcharge as part of your application."},
    "durata": {"valore": 5, "frammento": "You can stay in the UK for 5 years on this visa."},
    "tempi": {"valore": 3, "frammento": "You should get a decision on your visa within 3 weeks when you apply from outside the UK."},
    "proroga_tassa": {"valore": 1407, "frammento": "the £1,407 application fee"},
    "ilr": {"valore": True, "frammento": "You may be able to apply for indefinite leave to remain if you’ve spent 5 years in the UK on a UK Ancestry visa."},
    "ilr_cittadinanza": {"valore": True, "frammento": "You can use it to apply for British citizenship."},
}
QUERY = ["za|uk ancestry visa", "au|uk ancestry visa", "ca|uk ancestry visa", "nz|uk ancestry visa", "za|ancestry visa uk",
         "za|uk ancestry visa refused", "za|uk ancestry visa success rate", "za|uk ancestry visa requirements", "za|uk ancestry visa cost",
         "za|uk ancestry visa great grandparent", "za|uk ancestry visa statistics", "in|uk ancestry visa", "us|uk ancestry visa", "gb|ancestry visa",
         "za|can i get a uk ancestry visa"]


def main():
    oggi = date.today().isoformat()
    errori = []
    st, b, _ = get(API + GUIDA)
    fonti = {}
    if st != 200:
        errori.append(f"guida GOV.UK: HTTP {st}")
        testo = ""
    else:
        d = json.loads(b)
        testo = " ".join(f'{p["title"]}. {testo_html(p["body"])}' for p in d["details"]["parts"])
        fonti["guida"] = {"url": "https://www.gov.uk" + GUIDA, "api": API + GUIDA, "http": st, "titolo": d["title"], "aggiornata": d["public_updated_at"][:10],
                          "sha256": hashlib.sha256(testo.encode()).hexdigest(), "letto_il": oggi, "licenza": "Open Government Licence v3.0"}
    for k, v in LETTURE.items():
        if v["frammento"] not in testo:
            errori.append(f"{k}: frammento non trovato nella guida GOV.UK: {v['frammento'][:100]!r}")
    rif = json.loads((RADICE / "dati" / "rifiuti.json").read_text(encoding="utf-8"))
    fonti["ho"] = fonte_ho(rif, FILE_HO.read_bytes())
    sott, gruppi, _ = leggi_sottotipi(FILE_HO, [SOTTOTIPO])
    if gruppi[SOTTOTIPO] != [("Work", "Other work visas and exemptions")]:
        errori.append(f"Home Office: {SOTTOTIPO} in gruppi inattesi {gruppi[SOTTOTIPO]}")
    e, n_ho = controllo_ho(rif, sott[SOTTOTIPO], SOTTOTIPO)
    errori += e
    naz = {n: per_anno(q) for n, q in sott[SOTTOTIPO].items()}
    trimestri = sorted({q for v in sott[SOTTOTIPO].values() for q in v})
    vecchio = json.loads(USCITA.read_text(encoding="utf-8")) if USCITA.exists() else {}
    dom = nuova_domanda(QUERY) if "--domanda" in sys.argv else vecchio.get("domanda")
    if not dom or any(k not in dom["query"] for k in QUERY):
        errori.append("domanda: autocompletamento mancante o incompleto (lanciare con --domanda)")
    if errori:
        print("ERRORI: il file dei dati NON è stato aggiornato")
        for x in errori[:60]:
            print(" -", x)
        sys.exit(1)
    letture = {k: {"valore": v["valore"], "fonte": "guida", "frammento": v["frammento"]} for k, v in LETTURE.items()}
    contenuto = {"letture": letture, "fonti": fonti, "trimestri": trimestri, "controlli_work": n_ho, "naz": naz}
    uscita = {"_nota": "Generato da raccolta/ancestry.py: non modificare a mano. naz: nazionalità -> anno della decisione -> M (richiedenti principali) / "
                       "D (familiari) = [concessi, rifiutati, ritirati, decaduti], trimestri dell'anno presenti nel file. Home Office e GOV.UK: OGL v3.0.",
              "generato_il": oggi, "letto_il": oggi,
              "impronta": hashlib.sha256(json.dumps(contenuto, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20],
              "domanda": dom, **contenuto}
    USCITA.write_text(json.dumps(uscita, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"Scritto {USCITA}: UK Ancestry {trimestri[0]}–{trimestri[-1]}, {len(naz)} nazionalità, {n_ho} confronti con il gruppo Work; "
          f"tassa £{LETTURE['tassa']['valore']}; impronta {uscita['impronta']}.")


if __name__ == "__main__":
    main()
