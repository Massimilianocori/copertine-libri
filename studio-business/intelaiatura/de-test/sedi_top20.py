"""Prende le sedi BAMF delle 20 città più cercate e assegna a ognuna un indirizzo di partenza.

Il sito si ricava dal dominio dell'email della sede; dove il dominio è quello del Comune
(o di Gmail) si usa l'indirizzo della VHS scritto a mano qui sotto.
Scrive grezzi/sedi_top20.json.  Uso: python3 -I sedi_top20.py
"""
import json
import pathlib

QUI = pathlib.Path(__file__).resolve().parent
sedi = json.loads((QUI / "grezzi" / "sedi_bamf.json").read_text())
top = [c["citta"] for c in json.loads((QUI / "grezzi" / "autocomplete" / "citta.json").read_text())[:20]]
ALIAS = {"frankfurt": "frankfurt am main"}

BERLINO = {  # dominio email -> sezione VHS sul portale berlin.de
    "ba-ts.berlin.de": "tempelhof-schoeneberg", "ba-mitte.berlin.de": "mitte",
    "charlottenburg-wilmersdorf.de": "charlottenburg-wilmersdorf", "bezirksamt-neukoelln.de": "neukoelln",
    "ba-spandau.berlin.de": "spandau", "vhssz.de": "steglitz-zehlendorf",
    "reinickendorf.berlin.de": "reinickendorf", "ba-mh.berlin.de": "marzahn-hellersdorf",
    "lichtenberg.berlin.de": "lichtenberg", "ba-tk.berlin.de": "treptow-koepenick",
    "vhs-fk.de": "friedrichshain-kreuzberg", "vhspankow.de": "pankow",
}
A_MANO = {
    "stadt-frankfurt.de": "https://vhs.frankfurt.de/",
    "stadt-koeln.de": "https://www.vhs-koeln.de/",
    "vhs.essen.de": "https://www.vhs-essen.de/",
    "leipzig.de": "https://www.vhs-leipzig.de/",
    "duesseldorf.de": "https://www.duesseldorf.de/vhs",
    "hannover-stadt.de": "https://www.vhs-hannover.de/",
    "stadt.nuernberg.de": "https://www.bz.nuernberg.de/",
    "vhs.karlsruhe.de": "https://www.vhs-karlsruhe.de/",
    "regensburg.de": "https://www.vhs-regensburg.de/",
    "stadtdo.de": "https://www.vhs.dortmund.de/",
    "ib.de": "https://www.internationaler-bund.de/",
    "berlitz.de": "https://www.berlitz.com/de-de",
    "es.koeln.eso.de": "https://www.eso.de/",
    "gmail.com": "",
    "t-onlinde.de": "",
    "": "",
}

# pagine del test trovate a mano (link dalla home non leggibili o sito su un altro dominio)
EXTRA = {
    ("berlin", "vhspankow.de"): ["https://www.berlin.de/vhs/volkshochschulen/pankow/service/einbuergerungstest-vhs-pankow-1463977.php"],
    ("köln", "stadt-koeln.de"): ["https://www.koelner-vhs.de/deutsch-integration/einbuergerungstest"],
    ("münchen", "mvhs.de"): ["https://www.mvhs.de/programm/info/sprachen/sprachpruefungen-und-zertifikate-einbuergerungstest"],
    ("düsseldorf", "studyon.de"): ["https://www.studyon.de/prufungen"],
    ("köln", "es.koeln.eso.de"): ["https://www.euro-schulen.de/koeln/pruefungen-tests"],
    ("leipzig", "eso.de"): ["https://www.euro-schulen.de/leipzig/pruefungen-tests"],
    ("hannover", "eso.de"): ["https://www.euro-schulen.de/hannover/pruefungen-tests"],
    ("wiesbaden", "eso.de"): ["https://www.euro-schulen.de/wiesbaden/pruefungen-tests"],
    ("chemnitz", "eso.de"): ["https://www.euro-schulen.de/chemnitz/pruefungen-tests"],
    ("erfurt", "miqr.de"): ["https://mitteldeutsches-institut.de/einbuergerungstest-erfurt/"],
    ("chemnitz", "miqr.de"): ["https://mitteldeutsches-institut.de/einbuergerungstest-chemnitz/"],
}

out = []
for c in top:
    t = ALIAS.get(c, c)
    for s in sedi:
        o = s["ort"].lower()
        if o == t or o.startswith(t + " ") or o.startswith(t + "-"):
            d = s["dominio_email"]
            if d in BERLINO:
                url = f"https://www.berlin.de/vhs/volkshochschulen/{BERLINO[d]}/"
            elif d in A_MANO:
                url = A_MANO[d]
            else:
                url = f"https://www.{d}/"
            out.append({**s, "citta": c, "url_partenza": url, "url_extra": EXTRA.get((c, d), [])})

(QUI / "grezzi" / "sedi_top20.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(len(out), "sedi nelle 20 città;", sum(1 for x in out if not x["url_partenza"]), "senza sito")
