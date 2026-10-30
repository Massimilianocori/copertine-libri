"""Classifica le città più cercate dall'autocomplete tedesco.

Per ogni città candidata (le 45 più grandi della Germania) chiede all'autocomplete
  "einbürgerungstest termine <città>"  e  "dtz prüfung termine <città>"
e in più espande le frasi base con le lettere a-z ("einbürgerungstest termine a" ...).
Punteggio di una città:
  - 3 punti se compare nell'espansione per lettera di una delle due frasi (la città è tra le prime 10 per quella lettera),
    +2 se compare nella frase base senza lettera (prime 10 in assoluto);
  - 1 punto per ogni suggerimento restituito per la frase completa con la città (max 10+10).
Scrive grezzi/autocomplete/citta.json.
Uso: python3 -I citta_autocomplete.py
"""
import json
import pathlib
import string
import time
import urllib.parse
import urllib.request

QUI = pathlib.Path(__file__).resolve().parent
OUT = QUI / "grezzi" / "autocomplete"
OUT.mkdir(parents=True, exist_ok=True)
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"

CITTA = ["berlin", "hamburg", "münchen", "köln", "frankfurt", "stuttgart", "düsseldorf", "leipzig",
         "dortmund", "essen", "bremen", "dresden", "hannover", "nürnberg", "duisburg", "bochum",
         "wuppertal", "bielefeld", "bonn", "münster", "mannheim", "karlsruhe", "augsburg", "wiesbaden",
         "mönchengladbach", "gelsenkirchen", "aachen", "braunschweig", "kiel", "chemnitz", "halle",
         "magdeburg", "freiburg", "krefeld", "mainz", "lübeck", "erfurt", "oberhausen", "rostock",
         "kassel", "hagen", "potsdam", "saarbrücken", "hamm", "ludwigshafen", "offenbach", "heidelberg",
         "darmstadt", "regensburg", "ingolstadt", "würzburg", "osnabrück", "ulm", "heilbronn", "göttingen"]

FRASI = ["einbürgerungstest termine", "dtz prüfung termine"]


def suggerisci(q):
    url = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode(
        {"client": "firefox", "gl": "de", "hl": "de", "q": q})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        dati = json.loads(r.read().decode("utf-8", "replace"))
    time.sleep(0.6)
    return dati[1]


grezzi = {}
punti = {c: 0 for c in CITTA}
dettaglio = {c: [] for c in CITTA}

for frase in FRASI:
    base = suggerisci(frase)
    grezzi[frase] = base
    for lettera in string.ascii_lowercase:
        q = f"{frase} {lettera}"
        grezzi[q] = suggerisci(q)
    for c in CITTA:
        if any(s.strip() == f"{frase} {c}" or s.startswith(f"{frase} {c} ") for s in base):
            punti[c] += 2
            dettaglio[c].append(f"top10 '{frase}'")
        q = f"{frase} {c[0]}"
        if any(s.strip() == f"{frase} {c}" or s.startswith(f"{frase} {c} ") for s in grezzi[q]):
            punti[c] += 3
            dettaglio[c].append(f"top10 '{q}'")
    for c in CITTA:
        q = f"{frase} {c}"
        s = suggerisci(q)
        grezzi[q] = s
        n = len([x for x in s if c in x])
        punti[c] += n
        dettaglio[c].append(f"{n} suggerimenti per '{q}'")

classifica = sorted(CITTA, key=lambda c: -punti[c])
(OUT / "grezzi.json").write_text(json.dumps(grezzi, ensure_ascii=False, indent=1))
(OUT / "citta.json").write_text(json.dumps(
    [{"citta": c, "punti": punti[c], "dettaglio": dettaglio[c]} for c in classifica],
    ensure_ascii=False, indent=1))
for i, c in enumerate(classifica, 1):
    print(i, c, punti[c], "; ".join(dettaglio[c]))
