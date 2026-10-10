"""Controlli prima di pubblicare Visa Income Checker.

Uso (dalla radice del repository, dopo python3 visaincome/genera.py):
    python3 visaincome/verifica.py

1. Esempi calcolati a mano (TEST.md): il motore Python deve dare esattamente il risultato atteso
   (cambi fissi BCE del 9 ottobre 2026, così il test non cambia ogni giorno).
2. Il motore JS (lo stesso testo che va nelle pagine) deve dare gli stessi importi del Python,
   sugli esempi e su 3.000 casi casuali (serve node).
3. Nessun link interno rotto in sito/.
4. Ogni pagina di programma mostra la fonte ufficiale (URL) e la data del controllo sotto la cifra.
5. Nessun nome di modelli o servizi di intelligenza artificiale nei file del sito.
Esce con codice 1 se qualcosa non va.
"""
import json
import random
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import genera as G  # noqa: E402

SITO = G.SITO
P = {p["slug"]: p for p in G.PROG}
# Cambi BCE del 9 ottobre 2026 (1 EUR = ...), quelli usati negli esempi di TEST.md
T = {"USD": 1.1206, "GBP": 0.84763, "CAD": 1.5942, "AUD": 1.6052, "PHP": 70.397, "INR": 108.3965, "SEK": 11.1675,
     "DKK": 7.4751, "JPY": 177.34}

# (descrizione, programma, variante, adulti, figli, campo, valuta di arrivo o None, atteso calcolato a mano)
ESEMPI = [
    ("ES nomadi, 1 adulto: 2 × 1.424,50", "spain-digital-nomad-visa", "std", 1, 0, "mensile", None, 2849.00),
    ("ES nomadi, 1 adulto, annuo: 2.849 × 12", "spain-digital-nomad-visa", "std", 1, 0, "annuale", None, 34188.00),
    ("ES nomadi, coppia: 2.849 + 75% × 1.424,50 (1.068,375 → 1.068,38)", "spain-digital-nomad-visa", "std", 2, 0, "mensile", None, 3917.38),
    ("ES nomadi, coppia + 2 figli: 2.849 + 1.068,38 + 2 × 356,13", "spain-digital-nomad-visa", "std", 2, 2, "mensile", None, 4629.64),
    ("ES non lucrativo, coppia + 2 figli: 4 × 600 + 3 × 600", "spain-non-lucrative-visa", "std", 2, 2, "mensile", None, 4200.00),
    ("PT D8, 1 adulto: 4 × 920", "portugal-d8-digital-nomad-visa", "std", 1, 0, "mensile", None, 3680.00),
    ("PT D8, coppia + 1 figlio: 3.680 + 50% × 920 + 30% × 920", "portugal-d8-digital-nomad-visa", "std", 2, 1, "mensile", None, 4416.00),
    ("PT D7, coppia + 2 figli, annuo: (920 + 460 + 2 × 276) × 12", "portugal-d7-visa", "std", 2, 2, "annuale", None, 23184.00),
    ("HR nomadi, 2 adulti + 1 figlio: 2,5 × 1.449 + 2 × 10% × 1.449", "croatia-digital-nomad-visa", "std", 2, 1, "mensile", None, 3912.30),
    ("HU White Card, coppia: i familiari non contano, 3.000", "hungary-white-card", "std", 2, 0, "mensile", None, 3000.00),
    ("IT nomadi, mensile: 3 × 8.263,31 = 24.789,93 / 12 = 2.065,8275", "italy-digital-nomad-visa", "std", 1, 0, "mensile", None, 2065.83),
    ("DE Blue Card ridotta, mensile: 45.934,20 / 12", "germany-eu-blue-card", "red", 1, 0, "mensile", None, 3827.85),
    ("NL kennismigrant 30+, annuo: 5.942 × 12", "netherlands-highly-skilled-migrant", "30plus", 1, 0, "annuale", None, 71304.00),
    ("UK coniuge (proroga regole pre-2024), 3 figli: 18.600 + 3.800 + 2 × 2.400", "uk-spouse-visa", "legacy", 2, 3, "annuale", None, 27200.00),
    ("UK coniuge (proroga), 4 figli: 18.600 + 3.800 + 3 × 2.400 = 29.600 → tetto 29.000", "uk-spouse-visa", "legacy", 2, 4, "annuale", None, 29000.00),
    ("ES nomadi in USD: 2.849 × 1,1206 = 3.192,5894", "spain-digital-nomad-visa", "std", 1, 0, "mensile", "USD", 3192.59),
    ("ES nomadi in PHP: 2.849 × 70,397 = 200.561,053", "spain-digital-nomad-visa", "std", 1, 0, "mensile", "PHP", 200561.05),
    ("ES nomadi famiglia di 4 in USD: 4.629,64 × 1,1206", "spain-digital-nomad-visa", "std", 2, 2, "mensile", "USD", 5187.97),
    ("PT D8 in INR: 3.680 × 108,3965", "portugal-d8-digital-nomad-visa", "std", 1, 0, "mensile", "INR", 398899.12),
    ("HR nomadi in GBP: 3.622,50 × 0,84763", "croatia-digital-nomad-visa", "std", 1, 0, "mensile", "GBP", 3070.54),
    ("UK Skilled Worker da GBP a INR: 41.700 / 0,84763 × 108,3965", "uk-skilled-worker-visa", "std", 1, 0, "annuale", "INR", 5332673.51),
    ("SE Blue Card da SEK a USD: 53.625 / 11,1675 × 1,1206", "sweden-eu-blue-card", "std", 1, 0, "mensile", "USD", 5380.99),
    ("DK pay limit da DKK a USD: 552.000 / 7,4751 × 1,1206", "denmark-pay-limit-scheme", "std", 1, 0, "annuale", "USD", 82750.89),
    ("DE Blue Card in JPY (0 decimali): 50.700 × 177,34", "germany-eu-blue-card", "std", 1, 0, "annuale", "JPY", 8991138),
    ("ES non lucrativo famiglia di 4 in AUD: 4.200 × 1,6052", "spain-non-lucrative-visa", "std", 2, 2, "mensile", "AUD", 6741.84),
]


def valore(o, campo, a):
    x = o[campo]
    return x if a is None else G.converti(x, o["valuta"], a, T)


def controlla_esempi():
    errori = []
    for descr, slug, vid, ad, fi, campo, a, atteso in ESEMPI:
        v = valore(G.calcola(P[slug], vid, ad, fi), campo, a)
        if abs(v - atteso) > 0.001:
            errori.append(f"ESEMPIO SBAGLIATO: {descr}: atteso {atteso}, calcolato {v}")
    return errori


def casi_casuali(n=3000, seme=11):
    rnd = random.Random(seme)
    valute = ["EUR"] + sorted(G.CAMBI["tassi"])
    casi = []
    for _ in range(n):
        p = rnd.choice(G.PROG)
        casi.append([p["slug"], rnd.choice(p["varianti"])["id"], rnd.randint(1, 6), rnd.randint(0, 6), rnd.choice(valute)])
    return casi


def controlla_js(casi):
    """Esegue il motore JS con node sugli stessi casi e confronta i risultati con il Python."""
    dati = {"programmi": G.PROG, "indici": G.INDICI}
    script = ("var D=" + json.dumps(dati) + ";var T=" + json.dumps(G.CAMBI["tassi"]) + ";var TT=" + json.dumps(T) + ";\n" + G.MOTORE_JS +
              "\nvar casi=" + json.dumps(casi) + ";var es=" + json.dumps([[e[1], e[2], e[3], e[4], e[5], e[6]] for e in ESEMPI]) + ";\n"
              "function trova(s){for(var i=0;i<D.programmi.length;i++)if(D.programmi[i].slug===s)return D.programmi[i];}\n"
              "var out={casi:casi.map(function(c){var o=calcola(D,trova(c[0]),c[1],c[2],c[3]);"
              "return [o.mensile,o.annuale,converti(o.mensile,o.valuta,c[4],T),converti(o.annuale,o.valuta,c[4],T)];}),"
              "es:es.map(function(e){var o=calcola(D,trova(e[0]),e[1],e[2],e[3]);var x=o[e[4]];return e[5]?converti(x,o.valuta,e[5],TT):x;})};"
              "console.log(JSON.stringify(out));")
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(script)
        nome = fh.name
    try:
        r = subprocess.run(["node", nome], capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        return ["node non trovato: confronto JS saltato"]
    if r.returncode != 0:
        return ["Errore JS: " + r.stderr[:500]]
    js = json.loads(r.stdout)
    errori = []
    for c, j in zip(casi, js["casi"]):
        o = G.calcola(P[c[0]], c[1], c[2], c[3])
        py = [o["mensile"], o["annuale"], G.converti(o["mensile"], o["valuta"], c[4], G.CAMBI["tassi"]),
              G.converti(o["annuale"], o["valuta"], c[4], G.CAMBI["tassi"])]
        if any(abs(a - b) > 0.001 for a, b in zip(py, j)):
            errori.append(f"JS diverso dal Python per {c}: py {py} js {j}")
    for e, j in zip(ESEMPI, js["es"]):
        if abs(j - e[7]) > 0.001:
            errori.append(f"JS sbaglia l'esempio {e[0]}: {j}")
    return errori[:20]


class Link(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href = []

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k in ("href", "src") and v:
                self.href.append(v)


def controlla_link():
    errori = []
    pagine = list(SITO.rglob("*.html"))
    for f in pagine:
        p = Link()
        p.feed(f.read_text(encoding="utf-8"))
        for h in p.href:
            if h.startswith(("http://", "https://", "mailto:", "data:", "#", "javascript:")):
                continue
            h = h.split("#")[0].split("?")[0]
            if not h:
                continue
            dest = (SITO / h.lstrip("/")) if h.startswith("/") else (f.parent / h)
            dest = dest.resolve()
            if dest.is_dir():
                dest = dest / "index.html"
            if not dest.exists():
                errori.append(f"LINK ROTTO in {f.relative_to(SITO)}: {h}")
    return errori, len(pagine)


def controlla_fonti():
    errori = []
    for p in G.PROG:
        t = (SITO / p["slug"] / "index.html").read_text(encoding="utf-8")
        f = p["fonti"][0]
        blocco = re.search(r'<p class="cifra">.*?</section>', t, re.S)
        if not blocco or f["url"].replace("&", "&amp;") not in blocco.group(0) or "checked on " + G.data_lunga(f["controllato_il"]) not in blocco.group(0):
            errori.append(f"{p['slug']}: fonte o data mancanti sotto la cifra principale")
        if t.count("checked on") < 2:
            errori.append(f"{p['slug']}: date dei controlli mancanti")
    return errori


# Parole vietate scritte al contrario, così questo file non le contiene in chiaro.
_AL_CONTRARIO = ["edualc", "ciporhtna", "ianepo", "tpgtahc", "inimeg", "tolipoc", "amall", "lartsim", "supo", "tennos", "ukiah"]
VIETATE = re.compile(r"\b(" + "|".join(w[::-1] for w in _AL_CONTRARIO) + r"|gpt-\d)\b", re.I)


def controlla_parole():
    errori = []
    for f in list(SITO.rglob("*")) + list((SITO.parent / "dati").glob("*.json")):
        if f.is_file() and f.suffix in (".html", ".xml", ".txt", ".toml", ".json"):
            m = VIETATE.search(f.read_text(encoding="utf-8"))
            if m:
                errori.append(f"Parola vietata '{m.group(0)}' in {f}")
    return errori


def main():
    errori = controlla_esempi()
    print(f"1. Esempi a mano: {len(ESEMPI)} controllati, {len(errori)} errori")
    e2 = controlla_js(casi_casuali())
    print(f"2. Motore JS contro Python: {len(e2)} differenze")
    e3, n = controlla_link()
    print(f"3. Link interni: {n} pagine, {len(e3)} link rotti")
    e4 = controlla_fonti()
    print(f"4. Fonte e data sotto la cifra: {len(G.PROG)} programmi, {len(e4)} errori")
    e5 = controlla_parole()
    print(f"5. Parole vietate: {len(e5)}")
    tutti = errori + e2 + e3 + e4 + e5
    for e in tutti:
        print(" -", e)
    if tutti:
        sys.exit(1)
    print("TUTTO OK")


if __name__ == "__main__":
    main()
