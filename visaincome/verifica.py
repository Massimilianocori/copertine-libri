"""Controlli prima di pubblicare Visa Income Checker.

Uso (dalla radice del repository, dopo python3 visaincome/genera.py):
    python3 visaincome/verifica.py

1. Esempi calcolati a mano (TEST.md): il motore Python deve dare esattamente il risultato atteso
   (cambi fissi BCE del 9 ottobre 2026, così il test non cambia ogni giorno).
2. Il motore JS (lo stesso testo che va nelle pagine) deve dare gli stessi importi, conversioni ed esiti del Python,
   sugli esempi e su 3.000 casi casuali, anche con valori fuori scala (serve node).
3. Nessun link interno rotto in sito/.
4. Ogni pagina di programma mostra la fonte ufficiale (URL) e la data del controllo sotto la cifra.
5. Nessun nome di modelli o servizi di intelligenza artificiale nei file del sito.
6. Le correzioni della revisione indipendente del 10/10/2026 sono presenti nelle pagine.
7. Sezione "Visa refusal rates": ogni tabella e ogni cifra principale hanno sotto la fonte ufficiale (URL) e la data;
   le percentuali principali ricalcolate qui da dati/rifiuti.json coincidono con le pagine; avviso, dicitura di affiliazione,
   niente EKTA/Travelpayouts; i link esterni della sezione rispondono (HTTP 200 o 206; si salta con --offline).
8. Sezione "Easiest Schengen visa" e visti UK di studio e lavoro.
9. Blocco "Other useful tools for your trip" in ogni pagina indicizzabile: gli stessi link di genera.ALTRI_SITI, nell'ordine,
   mai a questo sito, tutti rel="noopener" e senza nofollow o sponsored.
10. File chiave IndexNow.
11. Australia, Nuova Zelanda e Canada (26/10/2026): pagine di riepilogo in sitemap con licenza, fonte, avviso e JSON-LD Dataset;
    righe della tabella australiana = nazionalità con almeno 500 decisioni; cifre di India, Pakistan, Nigeria e Filippine ricalcolate
    da dati/rifiuti_altri.json; le pagine Schengen di Australia e Canada rimandano alle pagine delle destinazioni.
12. "Who moved where" (28/10/2026): pagine nazionalità × Paese = quelle con almeno 500 nel 2025 ricalcolate qui da dati/trasferimenti.json,
    tutte in sitemap e nessuna in più; titoli entro 70 caratteri con l'anno; numero principale, serie per anno e tabella per Paese
    uguali ai dati; fonte con data sotto ogni tabella; riquadro "what this number is"; JSON-LD; nessun link interno rotto nella sezione.
13. Sitemap: ogni URL ha un lastmod vero (data valida, non nel futuro, uguale al registro dati/lastmod.json), nessun URL doppio.
Il controllo 8 comprende dal 28/10/2026 anche i visti UK di famiglia e del partner (coniuge).
Esce con codice 1 se qualcosa non va.
"""
import json
import random
import re
import subprocess
import sys
import time
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
# campo: "mensile" (importo mensile della regola, per mensilità), "annuale", "mensile12" (annuale / 12).
# Con una valuta di arrivo si usa converti_importi: si converte l'importo del periodo della regola e si ricava l'altro.
ESEMPI = [
    ("ES nomadi, 1 adulto: 200% × 1.221 = 2.442 al mese (× 14)", "spain-digital-nomad-visa", "std", 1, 0, "mensile", None, 2442.00),
    ("ES nomadi, 1 adulto, annuo: 2.442 × 14", "spain-digital-nomad-visa", "std", 1, 0, "annuale", None, 34188.00),
    ("ES nomadi, 1 adulto, su 12 mesi: 34.188 / 12", "spain-digital-nomad-visa", "std", 1, 0, "mensile12", None, 2849.00),
    ("ES nomadi, coppia: (2.442 + 75% × 1.221 = 915,75) × 14 = 47.008,50 / 12 = 3.917,375", "spain-digital-nomad-visa", "std", 2, 0, "mensile12", None, 3917.38),
    ("ES nomadi, coppia + 2 figli: 2.442 + 915,75 + 2 × 305,25", "spain-digital-nomad-visa", "std", 2, 2, "mensile", None, 3968.25),
    ("ES nomadi, coppia + 2 figli, annuo: 3.968,25 × 14", "spain-digital-nomad-visa", "std", 2, 2, "annuale", None, 55555.50),
    ("ES non lucrativo, coppia + 2 figli: 4 × 600 + 3 × 600", "spain-non-lucrative-visa", "std", 2, 2, "mensile", None, 4200.00),
    ("PT D8, 1 adulto: 4 × 920", "portugal-d8-digital-nomad-visa", "std", 1, 0, "mensile", None, 3680.00),
    ("PT D8, coppia + 1 figlio: nessun importo familiare ufficiale, resta 3.680", "portugal-d8-digital-nomad-visa", "std", 2, 1, "mensile", None, 3680.00),
    ("PT D7, coppia + 2 figli, annuo: (920 + 460 + 2 × 276) × 12", "portugal-d7-visa", "std", 2, 2, "annuale", None, 23184.00),
    ("HR nomadi, 2 adulti + 1 figlio: 2,5 × 1.449 + 2 × 10% × 1.449", "croatia-digital-nomad-visa", "std", 2, 1, "mensile", None, 3912.30),
    ("HU White Card, coppia: i familiari non contano, 3.000", "hungary-white-card", "std", 2, 0, "mensile", None, 3000.00),
    ("IT nomadi, mensile: 3 × 8.263,31 = 24.789,93 / 12 = 2.065,8275", "italy-digital-nomad-visa", "std", 1, 0, "mensile", None, 2065.83),
    ("DE Blue Card ridotta, mensile: 45.934,20 / 12", "germany-eu-blue-card", "red", 1, 0, "mensile", None, 3827.85),
    ("NL kennismigrant 30+, annuo: 5.942 × 12", "netherlands-highly-skilled-migrant", "30plus", 1, 0, "annuale", None, 71304.00),
    ("UK Skilled Worker, dottorato non STEM: soglia minima 37.500", "uk-skilled-worker-visa", "phd", 1, 0, "annuale", None, 37500.00),
    ("UK coniuge (proroga regole pre-2024), 3 figli: 18.600 + 3.800 + 2 × 2.400", "uk-spouse-visa", "legacy", 2, 3, "annuale", None, 27200.00),
    ("UK coniuge (proroga), 4 figli: 18.600 + 3.800 + 3 × 2.400 = 29.600 → tetto 29.000", "uk-spouse-visa", "legacy", 2, 4, "annuale", None, 29000.00),
    ("Valori fuori scala: 0 adulti e -3 figli diventano 1 e 0 (ES nomadi = 2.442)", "spain-digital-nomad-visa", "std", 0, -3, "mensile", None, 2442.00),
    ("Valori fuori scala: 50 adulti diventano 20 (HR: 3.622,50 + 19 × 144,90)", "croatia-digital-nomad-visa", "std", 50, 0, "mensile", None, 6375.60),
    ("ES nomadi in USD per mensilità: 2.442 × 1,1206 = 2.736,5052", "spain-digital-nomad-visa", "std", 1, 0, "mensile", "USD", 2736.51),
    ("ES nomadi in USD all'anno: 2.736,51 × 14 (coerente col mese)", "spain-digital-nomad-visa", "std", 1, 0, "annuale", "USD", 38311.14),
    ("ES nomadi in PHP su 12 mesi: 2.442 × 70,397 = 171.909,47 × 14 = 2.406.732,58 / 12", "spain-digital-nomad-visa", "std", 1, 0, "mensile12", "PHP", 200561.05),
    ("ES nomadi famiglia di 4 in USD per mensilità: 3.968,25 × 1,1206 = 4.446,82", "spain-digital-nomad-visa", "std", 2, 2, "mensile", "USD", 4446.82),
    ("PT D8 in INR: 3.680 × 108,3965", "portugal-d8-digital-nomad-visa", "std", 1, 0, "mensile", "INR", 398899.12),
    ("HR nomadi in GBP: 3.622,50 × 0,84763 = 3.070,5397", "croatia-digital-nomad-visa", "std", 1, 0, "mensile", "GBP", 3070.54),
    ("HR nomadi in GBP all'anno: 3.070,54 × 12 (non 3.622,50 × 12 convertito a parte)", "croatia-digital-nomad-visa", "std", 1, 0, "annuale", "GBP", 36846.48),
    ("UK Skilled Worker da GBP a INR: 41.700 / 0,84763 × 108,3965", "uk-skilled-worker-visa", "std", 1, 0, "annuale", "INR", 5332673.51),
    ("SE Blue Card da SEK a USD: 53.625 / 11,1675 × 1,1206", "sweden-eu-blue-card", "std", 1, 0, "mensile", "USD", 5380.99),
    ("DK pay limit da DKK a USD: 552.000 / 7,4751 × 1,1206", "denmark-pay-limit-scheme", "std", 1, 0, "annuale", "USD", 82750.89),
    ("DE Blue Card in JPY (0 decimali): 50.700 × 177,34", "germany-eu-blue-card", "std", 1, 0, "annuale", "JPY", 8991138),
    ("ES non lucrativo famiglia di 4 in AUD: 4.200 × 1,6052", "spain-non-lucrative-visa", "std", 2, 2, "mensile", "AUD", 6741.84),
]

# Confronto con il reddito: (descrizione, programma, variante, reddito al mese, mensilità, valuta, esito atteso)
ESITI = [
    ("AT Blue Card: 3.977 × 14 = 55.678 = soglia → sì", "austria-eu-blue-card", "std", 3977, 14, "EUR", "si"),
    ("AT Blue Card: 3.977 × 12 = 47.724 → no", "austria-eu-blue-card", "std", 3977, 12, "EUR", "no"),
    ("ES nomadi: 2.442 × 14 = 34.188 → sì", "spain-digital-nomad-visa", "std", 2442, 14, "EUR", "si"),
    ("ES nomadi: 2.849 × 12 = 34.188 → sì", "spain-digital-nomad-visa", "std", 2849, 12, "EUR", "si"),
    ("ES nomadi: 2.500 × 12 = 30.000 (mese sì, anno no) → parziale", "spain-digital-nomad-visa", "std", 2500, 12, "EUR", "parziale"),
    ("ES nomadi: 2.400 × 14 → no", "spain-digital-nomad-visa", "std", 2400, 14, "EUR", "no"),
    ("ES nomadi in USD: 2.736,51 USD × 14 → 2.442,00 € × 14 → sì", "spain-digital-nomad-visa", "std", 2736.51, 14, "USD", "si"),
    ("HU White Card, regola mensile: 2.600 × 14 = 36.400 > 36.000 ma 2.600 < 3.000 → no", "hungary-white-card", "std", 2600, 14, "EUR", "no"),
    ("HU White Card: 3.000 × 12 → sì", "hungary-white-card", "std", 3000, 12, "EUR", "si"),
    ("DE Blue Card: 4.225 × 12 = 50.700 → sì", "germany-eu-blue-card", "std", 4225, 12, "EUR", "si"),
    ("DE Blue Card: 4.224 × 12 → no", "germany-eu-blue-card", "std", 4224, 12, "EUR", "no"),
    ("IT nomadi: 2.100 × 12 = 25.200 ≥ 24.789,93 → sì", "italy-digital-nomad-visa", "std", 2100, 12, "EUR", "si"),
    ("UK Skilled Worker standard: nessun verdetto (conta anche il going rate)", "uk-skilled-worker-visa", "std", 5000, 12, "GBP", "nd"),
    ("UK Skilled Worker ridotto: nessun verdetto", "uk-skilled-worker-visa", "lower", 2800, 12, "GBP", "nd"),
    ("UK coniuge: nessun verdetto", "uk-spouse-visa", "std", 3000, 12, "GBP", "nd"),
]


def valore(o, campo, a):
    return o[campo] if a is None else G.converti_importi(o, a, T)[campo]


def controlla_esempi():
    errori = []
    for descr, slug, vid, ad, fi, campo, a, atteso in ESEMPI:
        v = valore(G.calcola(P[slug], vid, ad, fi), campo, a)
        if abs(v - atteso) > 0.001:
            errori.append(f"ESEMPIO SBAGLIATO: {descr}: atteso {atteso}, calcolato {v}")
    for descr, slug, vid, x, k, cur, atteso in ESITI:
        e = G.esito(P[slug], G.calcola(P[slug], vid, 1, 0), x, k, cur, T)
        if e != atteso:
            errori.append(f"ESITO SBAGLIATO: {descr}: atteso {atteso}, calcolato {e}")
    return errori


def casi_casuali(n=3000, seme=11):
    rnd = random.Random(seme)
    valute = ["EUR"] + sorted(G.CAMBI["tassi"])
    casi = []
    for _ in range(n):
        p = rnd.choice(G.PROG)
        casi.append([p["slug"], rnd.choice(p["varianti"])["id"], rnd.randint(-2, 25), rnd.randint(-3, 25), rnd.choice(valute),
                     round(rnd.uniform(0, 3000000), 2), rnd.choice([12, 13, 14, 11, 15]), rnd.choice(valute)])
    return casi


def controlla_js(casi):
    """Esegue il motore JS con node sugli stessi casi e confronta i risultati con il Python."""
    dati = {"programmi": G.PROG, "indici": G.INDICI}
    script = ("var D=" + json.dumps(dati) + ";var T=" + json.dumps(G.CAMBI["tassi"]) + ";var TT=" + json.dumps(T) + ";\n" + G.MOTORE_JS +
              "\nvar casi=" + json.dumps(casi) + ";var es=" + json.dumps([[e[1], e[2], e[3], e[4], e[5], e[6]] for e in ESEMPI]) +
              ";var esiti=" + json.dumps([[e[1], e[2], e[3], e[4], e[5]] for e in ESITI]) + ";\n"
              "function trova(s){for(var i=0;i<D.programmi.length;i++)if(D.programmi[i].slug===s)return D.programmi[i];}\n"
              "var out={casi:casi.map(function(c){var P=trova(c[0]);var o=calcola(D,P,c[1],c[2],c[3]);var cv=convertiImporti(o,c[4],T);"
              "return [o.mensile,o.annuale,o.mensile12,cv.mensile,cv.annuale,cv.mensile12,esito(P,o,c[5],c[6],c[7],T)];}),"
              "es:es.map(function(e){var o=calcola(D,trova(e[0]),e[1],e[2],e[3]);return e[5]?convertiImporti(o,e[5],TT)[e[4]]:o[e[4]];}),"
              "esiti:esiti.map(function(e){var P=trova(e[0]);return esito(P,calcola(D,P,e[1],1,0),e[2],e[3],e[4],TT);})};"
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
        cv = G.converti_importi(o, c[4], G.CAMBI["tassi"])
        py = [o["mensile"], o["annuale"], o["mensile12"], cv["mensile"], cv["annuale"], cv["mensile12"]]
        if any(abs(a - b) > 0.001 for a, b in zip(py, j[:6])) or G.esito(P[c[0]], o, c[5], c[6], c[7], G.CAMBI["tassi"]) != j[6]:
            errori.append(f"JS diverso dal Python per {c}: py {py} js {j}")
    for e, j in zip(ESEMPI, js["es"]):
        if abs(j - e[7]) > 0.001:
            errori.append(f"JS sbaglia l'esempio {e[0]}: {j}")
    for e, j in zip(ESITI, js["esiti"]):
        if j != e[6]:
            errori.append(f"JS sbaglia l'esito {e[0]}: {j}")
    return errori[:20]


def leggi(rel):
    return (SITO / rel).read_text(encoding="utf-8")


def controlla_contenuti():
    """Correzioni della revisione indipendente del 10/10/2026: devono restare."""
    errori = []
    tutto = "\n".join(f.read_text(encoding="utf-8") for f in SITO.rglob("*.html"))
    def deve(cond, msg):
        if not cond:
            errori.append(msg)
    es = leggi("spain-digital-nomad-visa/index.html")
    deve("€2,442</strong> a month × 14 payments" in es and "€2,849 a month if spread over 12 payments" in es, "ES: manca la forma ufficiale 2.442 × 14 con l'equivalente su 12")
    deve("consulados/buenosaires" in es.lower() and "HANOI" in es, "ES: mancano le fonti dei consolati (Buenos Aires, Hanoi)")
    deve("€1,221 a month × 14 payments" in es, "ES: SMI non indicato come 1.221 × 14")
    deve("Santiago" not in tutto, "Attribuzione a Santiago del Cile ancora presente")
    deve("not €2,762" not in tutto and "not €3,295" not in tutto, "Frase 'not €…' ancora in home")
    it = leggi("italy-digital-nomad-visa/index.html")
    deve("passive income such as social security, rents or stocks is not considered" in it and "consboston.esteri.it" in it, "IT: manca la regola sul reddito passivo (consolato di Boston)")
    pt = leggi("portugal-d8-digital-nomad-visa/index.html")
    deve("How much for a family" not in pt and "does not say how this combines" in pt, "PT D8: righe familiari ancora presenti o nota mancante")
    uk = leggi("uk-skilled-worker-visa/index.html")
    deve("£37,500" in uk and "70% to 90% of the going rate" in uk and "100% of the going rate" in uk and "We do not give a yes/no" in uk, "UK SW: condizioni del going rate mancanti")
    sp = leggi("uk-spouse-visa/index.html")
    deve("There is no income requirement" not in sp and "without relying on additional public funds" in sp, "UK coniuge: frase sui sussidi non corretta")
    deve("Couple (combined income)" in sp and "pre-settled status" in sp, "UK coniuge: etichetta di coppia o pre-settled mancanti")
    nf = leggi("404.html")
    hrefs = re.findall(r'href="([^"]+)"', nf)
    rel_rotti = [h for h in hrefs if not h.startswith(("/", "http", "data:", "#", "mailto:"))]
    deve(not rel_rotti, f"404: link relativi {rel_rotti[:3]}")
    deve('rel="canonical"' not in nf, "404: canonical da togliere (pagina noindex)")
    wk = leggi("work-visa-salary-thresholds/index.html")
    tb = re.search(r"<tbody>.*?</tbody>", wk, re.S).group(0)
    deve("spouse" not in tb.lower(), "Lavoro: righe del visto coniuge ancora nella tabella")
    deve("8% holiday allowance" in wk, "Lavoro: nota olandese mancante")
    deve("latest European Central Bank reference rates" in leggi("index.html") and "today's European Central Bank" not in tutto, "Home: 'today's ECB rates' da correggere")
    deve("IT specialists" in leggi("germany-eu-blue-card/index.html"), "DE: specialisti IT mancanti nella soglia ridotta")
    deve("at least one year earlier" in es, "ES: regola dell'azienda con almeno un anno mancante")
    deve("child born in Hungary" in leggi("hungary-white-card/index.html"), "HU: eccezione del figlio nato in Ungheria mancante")
    deve("podaci.dzs.hr" in leggi("croatia-digital-nomad-visa/index.html"), "HR: fonte DZS mancante")
    for s in ("netherlands-highly-skilled-migrant", "netherlands-eu-blue-card"):
        deve("8% holiday allowance" in leggi(f"{s}/index.html"), f"{s}: nota sull'indennità di ferie mancante")
    zeri = re.findall(r"(?:[€£]|\b[A-Z]{3} )\d[\d,]*\.00\b", tutto)
    deve(not zeri, f"Importi interi ancora con '.00': {sorted(set(zeri))[:5]}")
    deve('function soldi(v,c){var t=grp(v,DEC[c]===0?0:2);if(t.slice(-3)===\'.00\')t=t.slice(0,-3);' in es, "JS: soldi() non toglie '.00' dagli importi interi")
    deve('name="pagamenti"' in es, "Calcolatore: scelta 12/13/14 mensilità mancante")
    deve("italystrikes/dati/cambi-bce.json" in es, "URL dei cambi dal vivo non aggiornato")
    return errori


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


# ---------------------------------------------------------------- 7. Visa refusal rates
RE_DATA = re.compile(r"\b\d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December) 20\d\d\b")
URL_UFFICIALI = ("https://home-affairs.ec.europa.eu/", "https://assets.publishing.service.gov.uk/", "https://www.gov.uk/",
                 # Australia, Nuova Zelanda, Canada (26/10/2026)
                 "https://data.gov.au/", "https://www.homeaffairs.gov.au/", "https://www.immigration.govt.nz/", "https://www.ircc.canada.ca/",
                 "https://open.canada.ca/")


def pagine_rifiuti():
    return sorted((SITO / "visa-refusal-rates").rglob("index.html"))


def controlla_rifiuti(online=True):
    errori = []
    R = json.loads((SITO.parent / "dati" / "rifiuti.json").read_text(encoding="utf-8"))
    anni = sorted(R["schengen"], key=int)
    a1 = anni[-1]
    pagine = pagine_rifiuti()
    if len(pagine) < 60:
        errori.append(f"Rifiuti: solo {len(pagine)} pagine")
    esterni = set()
    for f in pagine:
        t = f.read_text(encoding="utf-8")
        nome = str(f.relative_to(SITO))
        corpo = t.split('<main id="main">', 1)[1].split("</main>", 1)[0]
        # ogni tabella deve avere sotto (prima della tabella dopo) una riga di fonte con URL ufficiale e data
        pezzi = corpo.split("<table")
        for i, dopo in enumerate(pezzi[1:], 1):
            m = re.match(r'.*?</table></div>\s*<p class="fonte">(.*?)</p>', dopo, re.S)  # subito sotto la tabella
            if not m or not any(u in m.group(1) for u in URL_UFFICIALI) or not RE_DATA.search(m.group(1)):
                errori.append(f"Rifiuti: tabella {i} di {nome} senza fonte ufficiale e data sotto")
        # la cifra principale (riquadro di sintesi) ha la fonte con data
        for m in re.finditer(r'<p class="cifra[^"]*">.*?</p>\s*(?:<div class="kpi">.*?</div></div>\s*)?(?:<p class="lead"[^>]*>.*?</p>\s*)?(<p class="fonte">.*?</p>|<p class="cifra)', corpo, re.S):
            blocco = m.group(1)
            if blocco.startswith('<p class="cifra'):
                continue
            if not any(u in blocco for u in URL_UFFICIALI) or not RE_DATA.search(blocco):
                errori.append(f"Rifiuti: cifra principale di {nome} senza fonte e data")
        if "Statistics, not advice." not in corpo:
            errori.append(f"Rifiuti: avviso mancante in {nome}")
        if "safetywing.com" in corpo:
            if 'rel="sponsored noopener"' not in corpo or "Affiliate" not in corpo or "affiliate link" not in corpo:
                errori.append(f"Rifiuti: link SafetyWing senza rel sponsored o dicitura in {nome}")
        if re.search(r"ekta|travelpayouts|tp\.media", t, re.I):
            errori.append(f"Rifiuti: EKTA/Travelpayouts presente in {nome}")
        esterni.update(h for h in re.findall(r'href="(https://[^"]+)"', corpo))
    # ricalcolo indipendente delle percentuali principali
    def tot(filtro):
        v = [0, 0, 0, 0]
        for r in R["schengen"][a1]:
            if filtro(r):
                for i in range(4):
                    v[i] += r[3 + i]
        d = v[1] + v[2] + v[3]
        return v, (v[3] / d if d else None)
    v, tx = tot(lambda r: True)
    p = (SITO / "visa-refusal-rates" / "index.html").read_text(encoding="utf-8")
    if f"<strong>{tx * 100:.1f}%</strong> of decisions were visas not issued" not in p or f"{v[0]:,}" not in p:
        errori.append("Rifiuti: totale Schengen della panoramica diverso dal ricalcolo")
    for paese, slug in (("INDIA", "india"), ("NIGERIA", "nigeria"), ("PAKISTAN", "pakistan"), ("TÜRKIYE", "turkiye"), ("MOROCCO", "morocco")):
        v, tx = tot(lambda r: r[1] == paese)
        p = (SITO / "visa-refusal-rates" / slug / "index.html").read_text(encoding="utf-8")
        if f"<strong>{tx * 100:.1f}%</strong> not issued ({v[3]:,} of {v[1] + v[2] + v[3]:,} decisions)" not in p:
            errori.append(f"Rifiuti: cifra principale di {slug} diversa dal ricalcolo")
    for stato in ("France", "Germany", "Spain", "Italy", "Netherlands"):
        v, tx = tot(lambda r: r[0] == stato)
        p = (SITO / "visa-refusal-rates" / "schengen" / stato.lower() / "index.html").read_text(encoding="utf-8")
        if f"<strong>{tx * 100:.1f}%</strong> of decisions were visas not issued" not in p:
            errori.append(f"Rifiuti: cifra principale di {stato} diversa dal ricalcolo")
    q4 = R["uk"]["trimestri"][-4:]
    for naz, slug in (("India", "india"), ("Nigeria", "nigeria"), ("Pakistan", "pakistan"), ("Ghana", "ghana")):
        c = sum(R["uk"]["naz"][naz]["Visitor"].get(q, [0, 0])[0] for q in q4)
        r = sum(R["uk"]["naz"][naz]["Visitor"].get(q, [0, 0])[1] for q in q4)
        p = (SITO / "visa-refusal-rates" / slug / "index.html").read_text(encoding="utf-8")
        if f"<strong>{r / (c + r) * 100:.1f}%</strong> of visitor visa decisions" not in p or f"({r:,} refused out of {c + r:,})" not in p:
            errori.append(f"Rifiuti: cifra UK di {slug} diversa dal ricalcolo")
    # link esterni della sezione
    controllati = 0
    if online:
        import urllib.request
        for u in sorted(esterni):
            u2 = u.replace("&amp;", "&")
            for _tentativo in range(4):  # ircc.canada.ca e immigration.govt.nz a volte chiudono la connessione: si riprova
                try:
                    req = urllib.request.Request(u2, headers={"User-Agent": "Mozilla/5.0", "Range": "bytes=0-2047"})
                    with urllib.request.urlopen(req, timeout=60) as r:
                        st = r.status
                except Exception as e:  # noqa: BLE001
                    st = getattr(e, "code", str(e))
                if isinstance(st, int):
                    break
                time.sleep(3)
            controllati += 1
            if st not in (200, 206):
                errori.append(f"Rifiuti: link esterno {u2} risponde {st}")
    return errori, len(pagine), controllati


# ---------------------------------------------------------------- 8. "Easiest Schengen visa" e visti UK di studio e lavoro (21/10/2026)
def controlla_facile():
    errori = []
    R = json.loads((SITO.parent / "dati" / "rifiuti.json").read_text(encoding="utf-8"))
    anni = sorted(R["schengen"], key=int)
    a1 = anni[-1]
    pagine = sorted((SITO / "visa-refusal-rates").glob("*/easiest-schengen-visa/index.html"))
    if len(pagine) < 30:
        errori.append(f"Facile: solo {len(pagine)} pagine 'easiest-schengen-visa'")
    sitemap = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    for f in pagine:
        t = f.read_text(encoding="utf-8")
        slug = f.parent.parent.name
        if f"/visa-refusal-rates/{slug}/easiest-schengen-visa/</loc>" not in sitemap:
            errori.append(f"Facile: {slug} non in sitemap")
        titolo = re.search(r"<title>(.*?)</title>", t).group(1)
        if not titolo.startswith("Easiest Schengen visa from "):
            errori.append(f"Facile: titolo di {slug}: {titolo}")
        if "Rates describe past decisions, not your chances." not in t:
            errori.append(f"Facile: frase di cautela mancante in {slug}")
        if 'class="classifica"' not in t or "FAQPage" not in t or "Statistics, not advice." not in t:
            errori.append(f"Facile: classifica, FAQ o avviso mancanti in {slug}")
        madre = (SITO / "visa-refusal-rates" / slug / "index.html").read_text(encoding="utf-8")
        if 'href="easiest-schengen-visa/"' not in madre:
            errori.append(f"Facile: la pagina {slug} non rimanda alla classifica")
    # ricalcolo per Pakistan, India e Nigeria: Stato con il tasso più basso e più alto tra quelli con almeno 500 decisioni
    for paese, slug in (("PAKISTAN", "pakistan"), ("INDIA", "india"), ("NIGERIA", "nigeria")):
        per_stato = {}
        for r in R["schengen"][a1]:
            if r[1] == paese:
                v = per_stato.setdefault(r[0], [0, 0, 0, 0])
                for i in range(4):
                    v[i] += r[3 + i]
        ok = sorted(((v[3] / (v[1] + v[2] + v[3]), s, v) for s, v in per_stato.items() if v[1] + v[2] + v[3] >= 500))
        if len(ok) < 8:
            errori.append(f"Facile: {slug} ha solo {len(ok)} Stati con 500+ decisioni ma ha la pagina")
            continue
        t = (SITO / "visa-refusal-rates" / slug / "easiest-schengen-visa" / "index.html").read_text(encoding="utf-8")
        tb, sb = ok[0][0], ok[0][1]
        ta, sa = ok[-1][0], ok[-1][1]
        if f"<strong>{sb}: {tb * 100:.1f}%</strong> not issued" not in t:
            errori.append(f"Facile: Stato più basso di {slug} diverso dal ricalcolo ({sb} {tb * 100:.1f}%)")
        if f"<b>{sa}</b><span>highest rate: {ta * 100:.1f}%</span>" not in t:
            errori.append(f"Facile: Stato più alto di {slug} diverso dal ricalcolo ({sa} {ta * 100:.1f}%)")
        prime = re.search(r'<ol class="classifica">(.*?)</ol>', t, re.S).group(1)
        if f">{sb}</a>" not in prime.split("</li>")[0]:
            errori.append(f"Facile: primo della lista 'Lowest' di {slug} non è {sb}")
        # tabella: tutte le righe in ordine crescente di tasso
        tassi = [float(x) for x in re.findall(r'<td class="n" data-v="(\d\.\d+)"><span class="tb"', t.split("All Schengen countries ranked", 1)[1].split("</table>", 1)[0])]
        tassi_a1 = tassi[0::2]  # colonne alternate: anno più recente, anno prima
        if tassi_a1 != sorted(tassi_a1) or len(tassi_a1) != len(ok):
            errori.append(f"Facile: tabella di {slug} non ordinata o incompleta ({len(tassi_a1)} righe su {len(ok)})")
    # UK: tassi di studio e lavoro nel riquadro delle pagine per nazionalità e nella pagina /uk/
    q4 = R["uk"]["trimestri"][-4:]
    uk_pag = (SITO / "visa-refusal-rates" / "uk" / "index.html").read_text(encoding="utf-8")
    for naz, slug in (("Pakistan", "pakistan"), ("India", "india"), ("Nigeria", "nigeria"), ("Japan", "japan")):
        p = (SITO / "visa-refusal-rates" / slug / "index.html").read_text(encoding="utf-8")
        for g, nome in (("Study", "study"), ("Work", "work")):
            c = sum(R["uk"]["naz"][naz][g].get(q, [0, 0])[0] for q in q4)
            r = sum(R["uk"]["naz"][naz][g].get(q, [0, 0])[1] for q in q4)
            tx = f"{r / (c + r) * 100:.1f}%"
            if f"<b>{tx}</b><span>{nome} visas refused · {c + r:,} decisions</span>" not in p and f"<strong>{tx}</strong> of {nome} visa decisions" not in p:
                errori.append(f"Rifiuti UK: tasso {nome} di {slug} ({tx}) non trovato nel riquadro")
            if f"<td>{nome.capitalize()} visas</td>" not in p or f'<td class="n">{c + r:,}</td><td class="n">{c:,}</td><td class="n">{r:,}</td>' not in p:
                errori.append(f"Rifiuti UK: riga {nome} di {slug} diversa dal ricalcolo")
            riga = re.search(rf'<tr><td>(?:<a [^>]+>)?{naz}(?:</a>)?</td>.*?</tr>', uk_pag, re.S)
            if not riga or f'<td class="n" data-v="{c + r}">{c + r:,}</td>' not in riga.group(0) or f'data-v="{r / (c + r):.6f}"' not in riga.group(0):
                errori.append(f"Rifiuti UK: pagina /uk/, riga {naz}: {nome} {tx} o {c + r} decisioni non trovati")
    if "Study visas refused" not in uk_pag or "Work visas refused" not in uk_pag:
        errori.append("Rifiuti UK: colonne studio/lavoro mancanti nella pagina /uk/")
    # famiglia e partner (28/10/2026): riquadro, riga della tabella "Visa type" e riga del partner nelle pagine per nazionalità
    def somma_uk(naz, g, qq):
        c = sum(R["uk"]["naz"].get(naz, {}).get(g, {}).get(q, [0, 0])[0] for q in qq)
        r = sum(R["uk"]["naz"].get(naz, {}).get(g, {}).get(q, [0, 0])[1] for q in qq)
        return c, r
    for naz, slug in (("Pakistan", "pakistan"), ("India", "india"), ("Nigeria", "nigeria"), ("Bangladesh", "bangladesh")):
        p = (SITO / "visa-refusal-rates" / slug / "index.html").read_text(encoding="utf-8")
        c, r = somma_uk(naz, "Family", q4)
        if c + r >= 500 and f"<b>{r / (c + r) * 100:.1f}%</b><span>family visas refused · {c + r:,} decisions</span>" not in p:
            errori.append(f"Rifiuti UK: tasso famiglia di {slug} non trovato nel riquadro")
        if f'<td>Family visas</td>' not in p or f'<td class="n">{c + r:,}</td><td class="n">{c:,}</td><td class="n">{r:,}</td>' not in p:
            errori.append(f"Rifiuti UK: riga famiglia di {slug} diversa dal ricalcolo")
        pc, pr = somma_uk(naz, "Family: Partner", q4)
        if pc + pr >= 100 and (f'<td>of which partner (spouse) visas</td>' not in p or f'<td class="n">{pc + pr:,}</td><td class="n">{pc:,}</td><td class="n">{pr:,}</td>' not in p
                               or f"the rate was {pr / (pc + pr) * 100:.1f}% ({pr:,} refused out of {pc + pr:,} decisions" not in p):
            errori.append(f"Rifiuti UK: riga o frase del partner di {slug} diversa dal ricalcolo")
        if pc > c or pr > r:
            errori.append(f"Rifiuti UK: partner oltre la famiglia per {naz}")
    fam = (SITO / "visa-refusal-rates" / "uk" / "family-visas" / "index.html")
    if not fam.exists():
        errori.append("Rifiuti UK: manca la pagina uk/family-visas/")
    else:
        ft = fam.read_text(encoding="utf-8")
        tot_p = [0, 0]
        tot_f = [0, 0]
        for naz in R["uk"]["naz"]:
            a, b = somma_uk(naz, "Family: Partner", q4)
            tot_p[0] += a; tot_p[1] += b
            a, b = somma_uk(naz, "Family", q4)
            tot_f[0] += a; tot_f[1] += b
        if f"<strong>{tot_p[1] / sum(tot_p) * 100:.1f}%</strong> refused ({tot_p[1]:,} of {sum(tot_p):,} decisions)" not in ft:
            errori.append("Rifiuti UK: tasso del partner (tutte le nazionalità) diverso dal ricalcolo")
        if f"<b>{tot_f[1] / sum(tot_f) * 100:.1f}%</b><span>all family visas refused · {sum(tot_f):,} decisions</span>" not in ft:
            errori.append("Rifiuti UK: tasso della famiglia (tutte le nazionalità) diverso dal ricalcolo")
        riga = re.search(r'<tr><td>(?:<a [^>]+>)?Pakistan(?:</a>)?</td>.*?</tr>', ft, re.S)
        c, r = somma_uk("Pakistan", "Family", q4)
        if not riga or f'data-v="{r / (c + r):.6f}"' not in riga.group(0) or f'data-v="{c + r}">{c + r:,}<' not in riga.group(0):
            errori.append("Rifiuti UK: riga Pakistan della pagina family-visas diversa dal ricalcolo")
        if "/visa-refusal-rates/uk/family-visas/</loc>" not in (SITO / "sitemap.xml").read_text(encoding="utf-8"):
            errori.append("Rifiuti UK: family-visas non in sitemap")
        if len(re.search(r"<title>(.*?)</title>", ft).group(1)) > 70 or "FAQPage" not in ft:
            errori.append("Rifiuti UK: titolo oltre 70 caratteri o FAQ mancante in family-visas")
    if 'href="family-visas/"' not in uk_pag or "partner (spouse) visas refused" not in uk_pag:
        errori.append("Rifiuti UK: la pagina /uk/ non mostra famiglia e partner o non rimanda a family-visas")
    return errori, len(pagine)


def controlla_altri_siti():
    """9. Blocco "Other useful tools for your trip" in ogni pagina indicizzabile: gli stessi link di genera.ALTRI_SITI,
    nell'ordine, da 3 a 4, mai a questo sito, tutti con rel="noopener" e senza nofollow o sponsored."""
    errori = []
    n = 0
    for f in sorted(SITO.rglob("*.html")):
        rel = f.relative_to(SITO).as_posix()
        if f.name == "404.html" or f.name.startswith("google"):
            continue
        n += 1
        t = f.read_text(encoding="utf-8")
        blocchi = re.findall(r'<div class="f-altri"><h2>(.*?)</h2><ul>(.*?)</ul></div>', t, re.S)
        if len(blocchi) != 1:
            errori.append(f"blocco altri siti mancante o doppio in {rel}")
            continue
        titolo, voci = blocchi[0]
        attesi, titolo_atteso = G.ALTRI_SITI, "Other useful tools for your trip"
        if titolo != titolo_atteso:
            errori.append(f"titolo del blocco altri siti sbagliato in {rel}: {titolo}")
        link = re.findall(r"<a ([^>]*)>", voci)
        url = [re.search(r'href="([^"]+)"', a).group(1) for a in link]
        if url != [u for u, _, _ in attesi] or not 3 <= len(url) <= 4:
            errori.append(f"link del blocco altri siti diversi da genera.py in {rel}: {url}")
        for a, u in zip(link, url):
            if u.startswith(G.URL_SITO) or 'rel="noopener"' not in a or "nofollow" in a or "sponsored" in a:
                errori.append(f"link sbagliato nel blocco altri siti in {rel}: {a}")
    return errori, n


def controlla_indexnow():
    """File chiave IndexNow in sito/: presente, con dentro solo la chiave, fuori dalla sitemap (scritto da genera.py accanto a robots.txt)."""
    errori = []
    f = SITO / f"{G.CHIAVE_INDEXNOW}.txt"
    if not f.exists():
        errori.append(f"file chiave IndexNow mancante: {f.name}")
    elif f.read_text(encoding="utf-8").strip() != G.CHIAVE_INDEXNOW:
        errori.append(f"file chiave IndexNow con contenuto sbagliato: {f.name}")
    if f.name in (SITO / "sitemap.xml").read_text(encoding="utf-8"):
        errori.append("file chiave IndexNow citato nella sitemap")
    return errori



# ---------------------------------------------------------------- 11. Australia, Nuova Zelanda, Canada (26/10/2026)
PAGINE_ALTRI = {"australia-visas": ("CC BY 2.5 AU", "data.gov.au"), "new-zealand-visas": ("CC BY 3.0 NZ", "immigration.govt.nz"),
                "canada-visas": ("Open Government Licence – Canada", "ircc.canada.ca")}


def controlla_altri():
    """Pagine di riepilogo e sezioni nelle pagine per Paese: fonte, licenza, soglia e cifre ricalcolate qui da dati/rifiuti_altri.json
    (con un codice separato da genera.py)."""
    errori = []
    R = json.loads((SITO.parent / "dati" / "rifiuti_altri.json").read_text(encoding="utf-8"))
    mappa = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    soglia = 500
    for slug, (lic, dominio) in PAGINE_ALTRI.items():
        f = SITO / "visa-refusal-rates" / slug / "index.html"
        if not f.exists():
            errori.append(f"Altri: manca la pagina {slug}")
            continue
        t = f.read_text(encoding="utf-8")
        if f"/visa-refusal-rates/{slug}/</loc>" not in mappa:
            errori.append(f"Altri: {slug} non in sitemap")
        if lic not in t or dominio not in t or "Statistics, not advice." not in t:
            errori.append(f"Altri: {slug} senza licenza, fonte o avviso")
        ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)]
        if not any(x.get("@type") == "Dataset" and x.get("license", "").startswith("https://") for x in ld) or not any(x.get("@type") == "BreadcrumbList" for x in ld):
            errori.append(f"Altri: {slug} senza JSON-LD Dataset con licenza o breadcrumb")
    # Australia: tasso dei richiedenti principali fuori dall'Australia, ultimo anno fiscale completo
    au = R["au"]
    pieni = [a for a in au["anni"] if re.fullmatch(r"\d{4}-\d{2}", a)]
    a1 = pieni[-1]
    def au_po(n, a):
        c = au["naz"].get(n, {}).get("y", {}).get(a)
        return c[0] if c else [0, 0]
    escl = {"Not Specified", "Stateless Person", "UN Convention Refugee", "Refugee", "UNMIK Travel Document", "United Nations Organisation",
            "Yugoslavia, Fed Republic of", "Serbia and Montenegro"}
    attese = {n for n in au["naz"] if n not in escl and sum(au_po(n, a1)) >= soglia}
    t = (SITO / "visa-refusal-rates" / "australia-visas" / "index.html").read_text(encoding="utf-8")
    tab = re.search(r'<table class="ord[^"]*" id="t-au">.*?<tbody>(.*?)</tbody>', t, re.S)
    righe = re.findall(r"<tr>(.*?)</tr>", tab.group(1), re.S) if tab else []
    if len(righe) != len(attese):
        errori.append(f"Altri: tabella australiana con {len(righe)} righe, attese {len(attese)} (soglia {soglia})")
    for r in righe:
        dec = re.findall(r'<td class="n" data-v="(\d+)">', r)
        if dec and int(dec[0]) < soglia:
            errori.append(f"Altri: riga australiana sotto la soglia: {re.sub('<[^>]+>', '', r)[:60]}")
    tot = [sum(au_po(n, a1)[0] for n in au["naz"]), sum(au_po(n, a1)[1] for n in au["naz"])]
    if f"<strong>{tot[1] / sum(tot) * 100:.1f}%</strong> refused ({tot[1]:,} of {sum(tot):,} decisions)" not in t:
        errori.append("Altri: cifra principale australiana diversa dal ricalcolo")
    # Nuova Zelanda: ultimo anno completo = penultimo se l'ultimo è in corso
    nz = R["nz"]
    anni_nz = nz["info"]["visitor"]["anni"]
    nz1 = anni_nz[-2] if not nz["info"]["visitor"]["periodo"][1].startswith("30 June") else anni_nz[-1]
    # Canada: ultimo anno con 12 mesi
    ca = R["ca"]
    mesi = ca["tr_processed"]["mesi"]
    ca1 = max(a for a in {m[:4] for m in mesi} if sum(1 for m in mesi if m.startswith(a)) == 12)
    def ca_sum(k, n):
        t = ca[k].get("totali", {}).get(n, {}).get(ca1)
        return t if t is not None else sum(x for m, x in ca[k]["paesi"].get(n, {}).items() if m.startswith(ca1) and x is not None)
    for slug, n_au, n_nz, n_ca in (("india", "India", "India", "India"), ("pakistan", "Pakistan", "Pakistan", "Pakistan"),
                                   ("nigeria", "Nigeria", "Nigeria", "Nigeria"), ("philippines", "Philippines", "Philippines", "Philippines")):
        t = (SITO / "visa-refusal-rates" / slug / "index.html").read_text(encoding="utf-8")
        v = au_po(n_au, a1)
        if sum(v) >= soglia:
            if (f"refused <strong>{v[1] / sum(v) * 100:.1f}%</strong> of student visa decisions for primary applicants" not in t
                    or f"({v[1]:,} refused out of {sum(v):,})" not in t or 'id="australia"' not in t):
                errori.append(f"Altri: cifra australiana di {slug} diversa dal ricalcolo")
            if "and Australia</title>" not in t:
                errori.append(f"Altri: titolo di {slug} senza Australia")
        elif "of student visa decisions for primary applicants" in t:
            errori.append(f"Altri: {slug} mostra un tasso australiano sotto la soglia")
        vz = nz["tipi"]["visitor"].get(n_nz, {}).get(nz1, [0, 0])
        if sum(vz) >= soglia and (f"declined <strong>{vz[1] / sum(vz) * 100:.1f}%</strong> of visitor visa applications" not in t or 'id="new-zealand"' not in t):
            errori.append(f"Altri: cifra neozelandese di {slug} diversa dal ricalcolo")
        ap, es = ca_sum("tr_approved", n_ca), ca_sum("tr_processed", n_ca)
        if es >= soglia and (f"approved <strong>{ap / es * 100:.1f}%</strong> of the temporary resident applications" not in t
                             or f"({ap:,} approved out of {es:,} people)" not in t or "cannot be calculated" not in t):
            errori.append(f"Altri: cifra canadese di {slug} diversa dal ricalcolo")
        for lic in ("CC BY 2.5 AU", "CC BY 3.0 NZ", "Open Government Licence – Canada"):
            if lic not in t:
                errori.append(f"Altri: {slug} senza la licenza {lic}")
    # le pagine Schengen "domande fatte in Australia / in Canada" rimandano alle pagine delle destinazioni, e non hanno la sezione su sé stesse
    for slug, dest, ancora in (("australia", "australia-visas", 'id="australia"'), ("canada", "canada-visas", 'id="canada"')):
        t = (SITO / "visa-refusal-rates" / slug / "index.html").read_text(encoding="utf-8")
        if f'href="../{dest}/"' not in t or ancora in t:
            errori.append(f"Altri: pagina {slug}: manca il rimando a {dest} o c'è la sezione su sé stessa")
    return errori

# ---------------------------------------------------------------- 12. "Who moved where" (28/10/2026)
URL_UFFICIALI_TR = ("https://ec.europa.eu/eurostat/", "https://www.ircc.canada.ca/", "https://open.canada.ca/", "https://assets.publishing.service.gov.uk/")


def controlla_trasferimenti():
    """Ricalcolo indipendente da dati/trasferimenti.json (senza le funzioni di genera.py): pagine attese, numeri, titoli, fonti, link."""
    errori = []
    D = json.loads((SITO.parent / "dati" / "trasferimenti.json").read_text(encoding="utf-8"))
    y1, y0 = D["anni"][-1], D["anni"][-2]
    eu = D["eurostat"]["dati"]
    nomi = D["eurostat"]["nomi_destinazioni"]
    slug_naz = {c: v[0] for c, v in G.NAZ_TR.items()}  # solo gli slug (configurazione), i numeri si ricalcolano qui
    def slug(n):
        import unicodedata
        n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode().lower()
        return re.sub(r"[^a-z0-9]+", "-", n).strip("-")
    attese = {}
    for c, s in slug_naz.items():
        for g, nome in nomi.items():
            if g == "EU27_2020":
                continue
            v = eu.get(c, {}).get(g, {}).get(y1)
            if v and v[0] is not None and v[0] >= 500:
                attese[f"{s}/{slug(nome)}"] = ("eu", c, g, v)
        ca = D["canada"]["cittadinanze"].get(c)
        if ca and ca["anni"][y1] >= 500:
            attese[f"{s}/canada"] = ("ca", c, None, ca)
        uk = D["uk"]["cittadinanze"].get(c)
        if uk and sum(uk["anni"][y1]) >= 500:
            attese[f"{s}/uk"] = ("uk", c, None, uk)
    base = SITO / "moved-to"
    trovate = {f.parent.relative_to(base).as_posix() for f in base.glob("*/*/index.html")}
    if trovate != set(attese):
        errori.append(f"Trasferimenti: pagine in più {sorted(trovate - set(attese))[:5]}, mancanti {sorted(set(attese) - trovate)[:5]}")
    mappa = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    pagine = sorted(base.rglob("index.html"))
    for f in pagine:
        rel = f.parent.relative_to(SITO).as_posix() + "/"
        t = f.read_text(encoding="utf-8")
        if f"<loc>{G.URL_SITO}/{rel}</loc>" not in mappa:
            errori.append(f"Trasferimenti: {rel} non in sitemap")
        titolo = re.search(r"<title>(.*?)</title>", t).group(1)
        if len(titolo.replace("&amp;", "&")) > 70 or y1 not in titolo:
            errori.append(f"Trasferimenti: titolo di {rel} oltre 70 caratteri o senza {y1}: {titolo}")
        corpo = t.split('<main id="main">', 1)[1].split("</main>", 1)[0]
        for i, dopo in enumerate(corpo.split("<table")[1:], 1):
            m = re.match(r'.*?</table></div>\s*<p class="fonte">(.*?)</p>', dopo, re.S)
            if not m or not any(u in m.group(1) for u in URL_UFFICIALI_TR) or not RE_DATA.search(m.group(1)):
                errori.append(f"Trasferimenti: tabella {i} di {rel} senza fonte ufficiale e data sotto")
        ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)]
        tipi = {x.get("@type") for x in ld}
        if "Dataset" not in tipi or "BreadcrumbList" not in tipi or (rel != "moved-to/" and "FAQPage" not in tipi):
            errori.append(f"Trasferimenti: JSON-LD mancante in {rel}: {tipi}")
        if rel != "moved-to/" and "What this number is, and what it is not" not in corpo:
            errori.append(f"Trasferimenti: riquadro 'what this number is' mancante in {rel}")
        if re.search(r'ekta|travelpayouts|tp\.media|safetywing|rel="[^"]*sponsored|>Affiliate<', corpo, re.I):
            errori.append(f"Trasferimenti: link di affiliazione in {rel}")
    def num(n):
        return f"{n:,}"
    # pagine nazionalità × Paese: numero principale, anno prima e serie per anno
    for k, (tipo, c, g, v) in sorted(attese.items()):
        f = base / k / "index.html"
        if not f.exists():
            continue
        t = f.read_text(encoding="utf-8")
        lead = re.search(r'<p class="lead">(.*?)</p>', t, re.S).group(1)
        if tipo == "eu":
            serie = eu[c][g]
            tot = serie[y1][0]
            if f"<strong>{num(tot)}</strong> first residence permits to" not in lead or "data updated on " + G.data_lunga(D["fonti"]["eurostat"]["aggiornato_il"]) not in lead:
                errori.append(f"Trasferimenti: numero principale o data di {k} diversi dai dati")
            for a, r in serie.items():
                if c == "UK" and a < "2021":
                    continue
                m = re.search(rf'<tr><td>{a}</td><td class="n" data-v="(\d+)">', t)
                if r[0] is not None and (not m or int(m.group(1)) != r[0]):
                    errori.append(f"Trasferimenti: serie {k} {a} diversa dai dati ({r[0]})")
            p0 = serie.get(y0)
            if p0 and p0[0] is not None and f"than in {y0} ({num(p0[0])})" not in lead:
                errori.append(f"Trasferimenti: confronto con {y0} di {k} diverso dai dati")
            mot = re.findall(r'<tr><td>(Family|Education|Work|Other)</td><td class="n" data-v="(\d*)">', t)
            if [int(x) if x else None for _, x in mot] != serie[y1][1:5]:
                errori.append(f"Trasferimenti: motivi {y1} di {k} diversi dai dati")
        elif tipo == "ca":
            if f"<strong>{num(v['anni'][y1])}</strong> " not in lead or f"({num(v['anni'][y0])})" not in lead:
                errori.append(f"Trasferimenti: numero canadese di {k} diverso dai dati")
            for a in D["anni"]:
                if not re.search(rf'<tr><td>{a}</td><td class="n" data-v="{v["anni"][a]}">', t):
                    errori.append(f"Trasferimenti: serie canadese {k} {a} diversa dai dati")
        else:
            tot1, tot0 = sum(v["anni"][y1]), sum(v["anni"][y0])
            if f"<strong>{num(tot1)}</strong> work, study and family visas" not in lead or f"({num(tot0)})" not in lead:
                errori.append(f"Trasferimenti: numero britannico di {k} diverso dai dati")
            for a in D["anni"]:
                x = v["anni"][a]
                if not re.search(rf'<tr><td>{a}</td><td class="n" data-v="{sum(x)}">[^<]*</td><td class="n" data-v="{x[0]}">[^<]*</td><td class="n" data-v="{x[1]}">[^<]*</td><td class="n" data-v="{x[2]}">', t):
                    errori.append(f"Trasferimenti: serie britannica {k} {a} diversa dai dati")
    # pagine della nazionalità: totale UE, righe dei Paesi
    for c, s in slug_naz.items():
        f = base / s / "index.html"
        if not f.exists():
            errori.append(f"Trasferimenti: manca la pagina {s}")
            continue
        t = f.read_text(encoding="utf-8")
        ue = eu[c]["EU27_2020"]
        if f"<strong>{num(ue[y1][0])}</strong> " not in re.search(r'<p class="lead">(.*?)</p>', t, re.S).group(1) or f"({num(ue[y0][0])})" not in t:
            errori.append(f"Trasferimenti: totale UE di {s} diverso dai dati")
        tab = re.search(r'id="t-tr">.*?<tbody>(.*?)</tbody>', t, re.S).group(1)
        righe = re.findall(r'<tr><td>(?:<a href="([^"]+)">)?([^<]+)(?:</a>)?</td><td class="n" data-v="(\d+)">', tab)
        for href, nome, x in righe:
            g = next((k for k, n in nomi.items() if n == nome), None)
            if g is None or eu[c][g][y1][0] != int(x):
                errori.append(f"Trasferimenti: riga {nome} di {s} diversa dai dati")
            if (href != "") != (f"{s}/{slug(nome)}" in attese):
                errori.append(f"Trasferimenti: link della riga {nome} di {s} non coerente con la soglia")
        attesi_ue = sum(1 for g in nomi if g != "EU27_2020" and g not in ("IS", "LI", "NO", "CH") and eu[c].get(g, {}).get(y1) and eu[c][g][y1][0] is not None)
        if len(righe) != attesi_ue:
            errori.append(f"Trasferimenti: {s} ha {len(righe)} righe UE, attese {attesi_ue}")
    # link interni della sezione (oltre al controllo 3, che copre tutto il sito)
    rotti = 0
    for f in pagine:
        pz = Link()
        pz.feed(f.read_text(encoding="utf-8"))
        for h in pz.href:
            if h.startswith(("http", "mailto:", "data:", "#", "javascript:")):
                continue
            h = h.split("#")[0].split("?")[0]
            dest = ((SITO / h.lstrip("/")) if h.startswith("/") else (f.parent / h)).resolve()
            if dest.is_dir():
                dest = dest / "index.html"
            if h and not dest.exists():
                rotti += 1
                errori.append(f"Trasferimenti: link rotto in {f.relative_to(SITO)}: {h}")
    # collegamenti dalla home e dalle pagine Paese
    if 'href="moved-to/"' not in leggi("index.html") or 'href="moved-to/americans/"' not in leggi("index.html"):
        errori.append("Trasferimenti: la home non rimanda alla sezione")
    for paese, d in (("spain", "spain"), ("germany", "germany"), ("united-kingdom", "uk")):
        if f'moved-to/americans/{d}/"' not in leggi(f"country/{paese}/index.html"):
            errori.append(f"Trasferimenti: la pagina Paese {paese} non rimanda a moved-to/americans/{d}/")
    return errori, len(pagine), len(attese)


def controlla_lastmod():
    """13. Ogni URL della sitemap ha un lastmod vero: data valida, non nel futuro, uguale al registro di genera.py; nessun doppione."""
    from datetime import date
    errori = []
    mappa = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    voci = re.findall(r"<url><loc>([^<]+)</loc>(?:<lastmod>([^<]*)</lastmod>)?</url>", mappa)
    reg = json.loads((SITO.parent / "dati" / "lastmod.json").read_text(encoding="utf-8"))["pagine"]
    if len(voci) != len({u for u, _ in voci}):
        errori.append("Sitemap: URL doppi")
    if len(voci) != len(re.findall(r"<url>", mappa)):
        errori.append("Sitemap: voci non lette")
    for u, d in voci:
        try:
            ok = date.fromisoformat(d) <= date.today()
        except ValueError:
            ok = False
        p = u[len(G.URL_SITO) + 1:]
        if not ok or reg.get(p, [None])[0] != d:
            errori.append(f"Sitemap: lastmod {d!r} non valido o diverso dal registro per {u}")
    return errori, len(voci), len({d for _, d in voci})


def main():
    errori = controlla_esempi()
    print(f"1. Esempi a mano: {len(ESEMPI)} importi e {len(ESITI)} confronti con il reddito, {len(errori)} errori")
    e2 = controlla_js(casi_casuali())
    print(f"2. Motore JS contro Python: {len(e2)} differenze")
    e3, n = controlla_link()
    print(f"3. Link interni: {n} pagine, {len(e3)} link rotti")
    e4 = controlla_fonti()
    print(f"4. Fonte e data sotto la cifra: {len(G.PROG)} programmi, {len(e4)} errori")
    e5 = controlla_parole()
    print(f"5. Parole vietate: {len(e5)}")
    e6 = controlla_contenuti()
    print(f"6. Correzioni della revisione presenti nelle pagine: {len(e6)} errori")
    e7, n7, x7 = controlla_rifiuti(online="--offline" not in sys.argv)
    print(f"7. Visa refusal rates: {n7} pagine, {x7} link esterni controllati, {len(e7)} errori")
    e8, n8 = controlla_facile()
    print(f"8. Easiest Schengen visa ({n8} pagine) e visti UK di studio, lavoro, famiglia e partner: {len(e8)} errori")
    e9, n9 = controlla_altri_siti()
    print(f"9. Blocco \"Other useful tools for your trip\" ({len(G.ALTRI_SITI)} link) in {n9} pagine indicizzabili: {len(e9)} errori")
    e10 = controlla_indexnow()
    print(f"10. File chiave IndexNow {G.CHIAVE_INDEXNOW}.txt in sito/ (contenuto giusto, fuori dalla sitemap): {len(e10)} errori")
    e11 = controlla_altri()
    print(f"11. Australia, Nuova Zelanda, Canada (3 pagine di riepilogo, sezioni per Paese, soglia e cifre ricalcolate): {len(e11)} errori")
    e12, n12, c12 = controlla_trasferimenti()
    print(f"12. Who moved where: {n12} pagine ({c12} nazionalità × Paese attese con 500+), numeri, titoli, fonti, JSON-LD e link: {len(e12)} errori")
    e13, n13, d13 = controlla_lastmod()
    print(f"13. Sitemap: {n13} URL con lastmod ({d13} date diverse, uguali al registro dati/lastmod.json): {len(e13)} errori")
    tutti = errori + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9 + e10 + e11 + e12 + e13
    for e in tutti:
        print(" -", e)
    if tutti:
        sys.exit(1)
    print("TUTTO OK")


if __name__ == "__main__":
    main()
