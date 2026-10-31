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
15. Visti Schengen a ingressi multipli (30/10/2026): pagina /visa-refusal-rates/multiple-entry-schengen-visa/ in sitemap, titolo entro 70
    caratteri con l'anno, prima frase con numero, fonte e data; tabelle per Stato e per Paese e riquadro di ogni pagina per Paese
    ricalcolati da dati/rifiuti.json (visti uniformi rilasciati e MEV), soglia 500 visti; link dall'indice e dalle pagine per Paese.
16. Test di inglese per i visti UK (SELT, 30/10/2026): ricalcolo da dati/selt.json (impronta, centri per città e per Paese, totali), pagine attese
    = indice + luoghi con domanda (tutte in sitemap, nessuna in più), titoli entro 70 caratteri, prima frase con numero, fonte e data,
    data del B2 solo con la fonte HC 1691 letta, nessun prezzo, link di affiliazione solo italki (ammesso, sponsored noopener, trasparenza).
17. Irlanda, PPS assegnati per nazionalità (30/10/2026): ricalcolo da dati/ppsn.json (impronta, pagine attese, numeri del primo paragrafo,
    tabelle mese per mese e anno per anno, confronto con gli stessi mesi, riquadro "what this number is", link dall'hub e colonna dell'indice);
    10 valori a caso ricontrollati sui CSV ufficiali con un lettore proprio.
18. Thailand DTV visa (30/10/2026): ricalcolo da dati/dtv.json (impronta, pagine attese = indice + sedi con domanda e dati, titoli ≤ 70,
    prima frase con data, righe della tabella = sedi lette con costo, regola e link ufficiale, frammenti citati, avviso, nessuna promessa,
    SafetyWing solo dopo le informazioni ufficiali e con la frase che l'assicurazione non è richiesta, link dal resto del sito);
    online, 10 frammenti a caso ricontrollati sulle pagine ufficiali riscaricate.
19. US OPT e STEM OPT (30/10/2026): ricalcolo da dati/opt.json (impronta), pagine attese (indice + 5) tutte in sitemap e nessuna in più,
    titoli ≤ 70, prima frase con fonte e data di lettura, cifre ufficiali presenti (tariffe I-765, premium processing, 90/60/30 giorni,
    90/150 giorni di disoccupazione), la proposta da 70.000 $ sempre come proposta, la regola dei 30 giorni come rinviata, link alle fonti,
    calcolatori presenti con le costanti dei dati, motore JS dei calcolatori uguale a un calcolo Python indipendente (casi fissi + 400 a caso),
    nessun link sponsorizzato; online: documenti del Federal Register e pagina I-765 di USCIS riletti (tipo, date, frammenti).
20. UK Graduate visa (30/10/2026): ricalcolo da dati/graduate.json (impronta), pagine attese (indice + 3), titoli ≤ 70, prima frase con fonte
    e data, durate (2 anni fino al 31/12/2026, 18 mesi dal 1/1/2027, 3 anni PhD), tariffa e IHS, tabelle dei costi ricalcolate, calcolatore,
    stesso confronto JS/Python, OGL; online: guida GOV.UK e Appendix Graduate rilette e frammenti ricontrollati.
21. Mexico residency (31/10/2026): ricalcolo da dati/mexico.json (impronta), pagine attese (indice + reddito + costi + una per consolato) tutte in
    sitemap e nessuna in più, titoli ≤ 70, prima frase con fonte e data di lettura, costi 2026 (Anexo 4 = LFD), calcolo UMA (giorni × UMA),
    tabella dei consolati e pagine per consolato con le cifre e i frammenti ufficiali, data della pagina del consolato, consolati esclusi,
    SafetyWing solo dopo le informazioni ufficiali e con la frase che non è un requisito, nessuna promessa, link dal resto del sito,
    costanti del calcolatore = dati e motore JS = calcolo Python indipendente (casi fissi + 400 a caso); online: 10 frammenti a caso
    riletti su LFD, Anexo 4, INEGI e Lineamientos (le pagine dei consolati non si rileggono qui: il sito SRE ha una verifica anti-bot).
22. Study in Italy (31/10/2026): ricalcolo da dati/studio_italia.json (impronta), pagine attese (indice + 5 pagine tematiche + una per ente DSU)
    tutte in sitemap e nessuna in più, titoli ≤ 70, prima frase con fonte e data di lettura, cifre nazionali (mezzi per il visto, borse minime,
    limiti ISEE/ISPE, costi del permesso ricalcolati, SSN), tabella degli enti e pagine per ente con limiti, importi, scadenze e frammenti dei
    bandi, elenco dei Paesi particolarmente poveri completo, tabella delle valute ricalcolata, esempio ISEE ricalcolato, enti non letti elencati,
    tutte le fonti citate, SafetyWing solo nella pagina dell'assicurazione e dopo le informazioni ufficiali, link dal resto del sito, costanti
    del calcolatore = dati e motore JS = calcolo Python indipendente (casi fissi + 400 a caso); online: 12 frammenti a caso riletti sulle fonti.
Il controllo 8 comprende dal 28/10/2026 anche i visti UK di famiglia e del partner (coniuge).
Monetizzazione (30/10/2026, controllo comune di studio-business/strumenti/monetizzazione.py): i link di affiliazione sono
ammessi solo verso i domini di monetizzazione.json, con rel="sponsored noopener" e la riga di trasparenza nella pagina;
domini bloccati e link sponsorizzati verso altri domini sono errori; script AdSense, ads.txt e sezione privacy ci sono
solo se AdSense è acceso per questo sito in monetizzazione.json.
Esce con codice 1 se qualcosa non va.
"""
import html
import json
import random
import re
import subprocess
import sys
import time
import tempfile
import urllib.request
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
    # dal 30/10/2026 le pagine dei centri SELT (uk-english-test/chile/) nominano Santiago come città dell'elenco ufficiale: esclusa
    # dal 30/10/2026 anche l'elenco delle sedi thailandesi (thailand-dtv-visa/) nomina l'ambasciata a Santiago del Cile: esclusa
    senza_selt = "\n".join(f.read_text(encoding="utf-8") for f in SITO.rglob("*.html") if "uk-english-test" not in f.parts and "thailand-dtv-visa" not in f.parts)
    deve("Santiago" not in senza_selt, "Attribuzione a Santiago del Cile ancora presente")
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
URL_UFFICIALI_TR = ("https://ec.europa.eu/eurostat/", "https://www.ircc.canada.ca/", "https://open.canada.ca/", "https://assets.publishing.service.gov.uk/",
                    "https://www.gov.ie/", "https://assets.gov.ie/")  # gov.ie: PPS (Irlanda), dal 30/10/2026


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
    # Irlanda (30/10/2026): pagina anche con almeno 500 PPS nell'ultimo anno intero; queste pagine si controllano nel punto 17
    PP = json.loads((SITO.parent / "dati" / "ppsn.json").read_text(encoding="utf-8"))
    ult = PP["mesi"][-1]
    pieno = ult[:4] if ult.endswith("-12") else str(int(ult[:4]) - 1)
    for c, s in slug_naz.items():
        x = PP["nazionalita"].get(c)
        if (x and (x["anni"].get(pieno) or 0) >= 500) or f"{s}/ireland" in attese:
            attese[f"{s}/ireland"] = ("ie", c, "IE", None)
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
        anno_t = ult[:4] if rel.endswith("/ireland/") else y1   # pagine Irlanda: anno dei PPS
        if len(titolo.replace("&amp;", "&")) > 70 or anno_t not in titolo:
            errori.append(f"Trasferimenti: titolo di {rel} oltre 70 caratteri o senza {anno_t}: {titolo}")
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
        # link di affiliazione (dal 30/10/2026): ammessi solo come nel controllo comune 14 (domini di monetizzazione.json,
        # rel="sponsored noopener", riga di trasparenza); qui restano vietati EKTA e Travelpayouts, che non sono in elenco
        if re.search(r'ekta|travelpayouts|tp\.media', corpo, re.I):
            errori.append(f"Trasferimenti: link a una rete di affiliazione non ammessa in {rel}")
    def num(n):
        return f"{n:,}"
    # pagine nazionalità × Paese: numero principale, anno prima e serie per anno
    for k, (tipo, c, g, v) in sorted(attese.items()):
        f = base / k / "index.html"
        if not f.exists() or tipo == "ie":
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


# ---------------------------------------------------------------- 15. Visti Schengen a ingressi multipli (30/10/2026)
def controlla_mev():
    """15. Ricalcolo indipendente da dati/rifiuti.json (colonne 4 = visti uniformi rilasciati, 7 = di cui MEV): pagina riassuntiva
    in sitemap con titolo ≤ 70 e anno, prima frase con numero, fonte e data, tabelle per Stato e per Paese uguali ai dati,
    riquadro in ogni pagina per Paese (cifra e righe degli Stati con almeno 500 visti), link dall'indice e dalle pagine per Paese."""
    errori = []
    R = json.loads((SITO.parent / "dati" / "rifiuti.json").read_text(encoding="utf-8"))
    anni = sorted(R["schengen"], key=int)
    a1, a0 = anni[-1], anni[-2]
    soglia = 500
    righe = {a: R["schengen"][a] for a in (a1, a0)}
    if any(len(r) != 8 for a in righe for r in righe[a]):
        return ["MEV: righe di dati/rifiuti.json senza la colonna dei visti a ingressi multipli"], 0

    def somma(a, filtro):
        v = [0, 0]
        for r in righe[a]:
            if filtro(r):
                v[0] += r[4]
                v[1] += r[7]
        return v

    def pc(v):
        return f"{v[1] / v[0] * 100:.1f}%" if v[0] else "–"

    def leggi_righe(tabella):
        """[(nome, quota data-v, visti rilasciati, MEV)] dalle righe di una tabella MEV."""
        out = []
        for tr in re.findall(r"<tr><td>(.*?)</tr>", tabella, re.S):
            nome = re.sub(r"<[^>]+>", "", tr.split("</td>", 1)[0])
            dv = re.findall(r'data-v="([^"]*)"', tr)
            out.append((html.unescape(nome), dv[0], int(dv[3]), int(dv[4])))
        return out

    percorso = "visa-refusal-rates/multiple-entry-schengen-visa/"
    f = SITO / percorso / "index.html"
    if not f.exists():
        return [f"MEV: manca {percorso}"], 0
    t = f.read_text(encoding="utf-8")
    sitemap = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    if f"{G.URL_SITO}/{percorso}</loc>" not in sitemap:
        errori.append("MEV: pagina riassuntiva non in sitemap")
    titolo = html.unescape(re.search(r"<title>(.*?)</title>", t).group(1))
    if len(titolo) > 70 or a1 not in titolo:
        errori.append(f"MEV: titolo oltre 70 caratteri o senza l'anno: {titolo!r} ({len(titolo)})")
    tot1, tot0 = somma(a1, lambda r: True), somma(a0, lambda r: True)
    corpo = t.split('<main id="main">', 1)[1].split("</main>", 1)[0]
    prima = re.search(r'<p class="lead">(.*?)</p>', corpo, re.S).group(1)
    if (f"<strong>{pc(tot1)}</strong> of the {tot1[0]:,} uniform Schengen visas issued were multiple-entry visas ({tot1[1]:,})" not in prima
            or "European Commission" not in prima or "home-affairs.ec.europa.eu" not in prima or not RE_DATA.search(prima)):
        errori.append("MEV: prima frase senza numero ricalcolato, fonte (Commissione) o data")
    if f"<b>{pc(tot0)}</b><span>in {a0} ({tot0[1]:,} of {tot0[0]:,})</span>" not in corpo:
        errori.append(f"MEV: totale {a0} diverso dal ricalcolo")
    tabelle = re.findall(r"<table.*?</table>", corpo, re.S)
    if len(tabelle) != 2:
        errori.append(f"MEV: {len(tabelle)} tabelle nella pagina riassuntiva (attese 2)")
        return errori, 1
    # per Stato Schengen: tutti, valori uguali, ordine dalla quota più alta
    stati = sorted({r[0] for r in righe[a1]})
    lette = leggi_righe(tabelle[0])
    if sorted(x[0] for x in lette) != stati:
        errori.append(f"MEV: righe della tabella per Stato ({len(lette)}) diverse dai {len(stati)} Stati dei dati")
    for nome, dv, ril, mev in lette:
        v = somma(a1, lambda r, s=nome: r[0] == s)
        if [ril, mev] != v or abs(float(dv) - v[1] / v[0]) > 1e-6:
            errori.append(f"MEV: riga {nome} della tabella per Stato diversa dal ricalcolo ({v})")
    if [float(x[1]) for x in lette] != sorted((float(x[1]) for x in lette), reverse=True):
        errori.append("MEV: tabella per Stato non ordinata dalla quota più alta")
    # per Paese di domanda: i Paesi con almeno 10.000 domande (esclusi gli Stati Schengen), valori uguali
    dom = {}
    for r in righe[a1]:
        dom[r[1]] = dom.get(r[1], 0) + r[3]
    maiusc = {s.upper() for s in stati}
    paesi = {p for p, n in dom.items() if n >= G.SOGLIA_PAGINA and p not in maiusc}
    lette_p = leggi_righe(tabelle[1])
    if len(lette_p) != len(paesi):
        errori.append(f"MEV: {len(lette_p)} righe nella tabella per Paese, attese {len(paesi)}")
    per_nome = {html.unescape(G.nome_paese(p)): p for p in paesi}  # solo i nomi visibili (configurazione), i numeri si ricalcolano qui
    for nome, dv, ril, mev in lette_p:
        p = per_nome.get(nome)
        if not p:
            errori.append(f"MEV: Paese {nome} nella tabella ma non tra quelli con {G.SOGLIA_PAGINA:,}+ domande")
            continue
        v = somma(a1, lambda r, p=p: r[1] == p)
        if [ril, mev] != v or abs(float(dv) - v[1] / v[0]) > 1e-6:
            errori.append(f"MEV: riga {nome} della tabella per Paese diversa dal ricalcolo ({v})")
    for frase in ("FAQPage", '"@type": "Dataset"', "does not say how long", "not a long-stay visa", "Statistics, not advice."):
        if frase not in t:
            errori.append(f"MEV: manca {frase!r} nella pagina riassuntiva")
    if re.search(r"you will (get|receive|be given) a multiple|guarantee[ds]? a multiple", t, re.I):
        errori.append("MEV: promessa sul visto nella pagina riassuntiva")
    # riquadro nelle pagine per Paese
    n = 1
    for p in sorted(paesi):
        slug = G.SLUG_RIF[p]
        fp = SITO / "visa-refusal-rates" / slug / "index.html"
        tp = fp.read_text(encoding="utf-8")
        n += 1
        if 'id="multiple-entry"' not in tp or 'href="../multiple-entry-schengen-visa/"' not in tp:
            errori.append(f"MEV: riquadro o link alla pagina riassuntiva mancanti in {slug}")
            continue
        sez = tp.split('id="multiple-entry"', 1)[1].split("<h2>By consulate</h2>", 1)[0]
        v = somma(a1, lambda r, p=p: r[1] == p)
        if f"<strong>{pc(v)}</strong> were multiple-entry visas ({v[1]:,} of {v[0]:,} uniform visas issued)" not in sez:
            errori.append(f"MEV: cifra del riquadro di {slug} diversa dal ricalcolo ({pc(v)}, {v})")
        if "does not say how long" not in sez:
            errori.append(f"MEV: frase sulla durata mancante in {slug}")
        attesi = {}
        for r in righe[a1]:
            if r[1] == p:
                x = attesi.setdefault(r[0], [0, 0])
                x[0] += r[4]
                x[1] += r[7]
        attesi = {s: x for s, x in attesi.items() if x[0] >= soglia}
        tab = re.search(r"<table.*?</table>", sez, re.S)
        lette_s = leggi_righe(tab.group(0)) if tab else []
        if {x[0] for x in lette_s} != set(attesi):
            errori.append(f"MEV: Stati nella tabella di {slug} diversi da quelli con {soglia}+ visti rilasciati")
        for nome, dv, ril, mev in lette_s:
            if attesi.get(nome) != [ril, mev]:
                errori.append(f"MEV: riga {nome} di {slug} diversa dal ricalcolo ({attesi.get(nome)})")
        if [float(x[1]) for x in lette_s] != sorted((float(x[1]) for x in lette_s), reverse=True):
            errori.append(f"MEV: tabella di {slug} non ordinata dalla quota più alta")
    indice = (SITO / "visa-refusal-rates" / "index.html").read_text(encoding="utf-8")
    if 'href="multiple-entry-schengen-visa/"' not in indice or f"In {a1}, {pc(tot1)} of the {tot1[0]:,} uniform visas issued were multiple-entry visas" not in indice:
        errori.append("MEV: l'indice della sezione non rimanda alla pagina riassuntiva o ha un totale diverso")
    return errori, n


# ---------------------------------------------------------------- 16. Test di inglese per i visti UK (SELT), 30/10/2026
def controlla_selt():
    """16. Ricalcolo indipendente da dati/selt.json: impronta dei dati; pagine attese (indice + città e Paesi con domanda) tutte in
    sitemap e nessuna in più; titoli ≤ 70; prima frase con numero, fonte e data; righe delle tabelle = centri dell'elenco (nome e
    indirizzo); data del B2 solo se letta nella fonte ufficiale (HC 1691); nessun prezzo; avviso; JSON-LD; link di affiliazione
    solo italki (dominio ammesso, rel="sponsored noopener", riga di trasparenza) e solo se attivo in dati/affiliati.json."""
    import hashlib
    errori = []
    D = json.loads((SITO.parent / "dati" / "selt.json").read_text(encoding="utf-8"))
    aff = json.loads((SITO.parent / "dati" / "affiliati.json").read_text(encoding="utf-8")).get("_italki_selt", {})
    contenuto = {"centri": D["centri"], "test": D["test"]}
    if hashlib.sha256(json.dumps(contenuto, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != D["impronta"]:
        errori.append("SELT: impronta di dati/selt.json diversa dal contenuto (file modificato a mano?)")
    uk, est = D["centri"]["uk"], D["centri"]["estero"]
    if len(uk) != D["fonti"]["centri_uk"]["righe"] or len(est) != D["fonti"]["centri_estero"]["righe"]:
        errori.append("SELT: numero di centri diverso dalle righe del file ufficiale")
    soglia = D["domanda"]["soglia"]
    citta = sorted({r[2] for r in uk})
    paesi = sorted({r[2] for r in est})
    citta_pag = [c for c in citta if len(D["domanda"]["citta"].get(c, [])) >= soglia]
    paesi_pag = [p for p in paesi if len(D["domanda"]["paesi"].get(p, [])) >= soglia]
    sitemap = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    sez = SITO / "uk-english-test"
    attese = {"": None}
    attese.update({G.SLUG_SELT[c]: ("uk", c) for c in citta_pag})
    attese.update({G.SLUG_SELT[p]: ("estero", p) for p in paesi_pag})  # slug: configurazione del generatore; i numeri si ricalcolano qui
    trovate = {f.parent.relative_to(sez).as_posix().replace(".", "") for f in sez.rglob("index.html")}
    if trovate != set(attese):
        errori.append(f"SELT: pagine diverse da quelle attese (in più: {sorted(trovate - set(attese))[:5]}, mancanti: {sorted(set(attese) - trovate)[:5]})")
    hc = D["fonti"]["hc1691"]
    b2_ok = hc.get("in_vigore") == "2027-03-26" and any("come into force on 26 March 2027" in f for f in hc.get("frasi_memorandum", []))
    data_el = G.data_lunga(D["fonti"]["centri_uk"]["data_elenco"])
    url_it = aff.get("url", "")
    n = 0
    for slug, chi in attese.items():
        f = sez / slug / "index.html" if slug else sez / "index.html"
        if not f.exists():
            continue
        n += 1
        percorso = f"uk-english-test/{slug + '/' if slug else ''}"
        t = f.read_text(encoding="utf-8")
        main = t.split('<main id="main">', 1)[1].split("</main>", 1)[0]
        if f"{G.URL_SITO}/{percorso}</loc>" not in sitemap:
            errori.append(f"SELT: {percorso} non in sitemap")
        titolo = html.unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(titolo) > 70:
            errori.append(f"SELT: titolo oltre 70 caratteri in {percorso}: {titolo!r} ({len(titolo)})")
        prima = re.search(r'<p class="lead">(.*?)</p>', main, re.S).group(1)
        if data_el not in prima or not RE_DATA.search(prima):
            errori.append(f"SELT: prima frase senza la data dell'elenco in {percorso}")
        for frase in ("Not immigration or legal advice.", "FAQPage", "Open Government Licence v3.0", "list dated"):
            if frase not in t:
                errori.append(f"SELT: manca {frase!r} in {percorso}")
        if re.search(r"[£$€₹]\s?\d|\bRs\.?\s?\d|\bPKR\s?\d|\bINR\s?\d|\bGBP\s?\d", re.sub(r"<[^>]+>", " ", main)):
            errori.append(f"SELT: prezzo nella pagina {percorso} (nessuna fonte ufficiale del fornitore letta)")
        if "26 March 2027" in t and not b2_ok:
            errori.append(f"SELT: data del B2 in {percorso} senza la fonte ufficiale in dati/selt.json")
        # link di affiliazione
        sponsor = re.findall(r'<a [^>]*rel="([^"]*sponsored[^"]*)"[^>]*>', main) + re.findall(r'<a [^>]*href="([^"]*italki[^"]*)"', main)
        link_it = re.findall(r'<a [^>]*href="(https?://[^"]*italki\.com[^"]*)"[^>]*rel="([^"]*)"', main)
        if url_it:
            if len(link_it) != 1 or link_it[0][0] != html.escape(url_it) and link_it[0][0] != url_it or link_it[0][1] != "sponsored noopener":
                errori.append(f"SELT: riquadro italki assente, doppio o con rel sbagliato in {percorso}")
            if G.MON.RIGA_EN not in main:
                errori.append(f"SELT: riga di trasparenza mancante in {percorso}")
            if not G.MON.dominio_ammesso(url_it):
                errori.append("SELT: dominio del link italki non tra quelli ammessi in monetizzazione.json")
            if main.find("aff-i-h") < main.find("How to book</h2>") or main.find("How to book</h2>") < 0:
                errori.append(f"SELT: riquadro italki prima delle informazioni ufficiali in {percorso}")
        elif link_it or sponsor:
            errori.append(f"SELT: link di affiliazione in {percorso} ma _italki_selt non è attivo")
        for h, r in re.findall(r'<a [^>]*href="(https?://[^"]+)"[^>]*rel="([^"]*sponsored[^"]*)"', main):
            if "italki.com" not in h:
                errori.append(f"SELT: link sponsorizzato non ammesso in {percorso}: {h}")
        if chi is None:
            tot = f"<strong>{len(uk):,} approved centres in the UK</strong> or <strong>{len(est):,} outside the UK</strong>"
            if tot not in prima:
                errori.append("SELT: totali della prima frase dell'indice diversi dal ricalcolo")
            for tid, attesi in (("t-uk-c", {c: sum(1 for r in uk if r[2] == c) for c in citta}), ("t-est", {p: sum(1 for r in est if r[2] == p) for p in paesi})):
                tab = re.search(r'<table[^>]*id="%s".*?</table>' % tid, main, re.S)
                righe = re.findall(r'<tr><td>(.*?)</td><td class="n" data-v="(\d+)"', tab.group(0)) if tab else []
                if len(righe) != len(attesi) or sorted(int(x[1]) for x in righe) != sorted(attesi.values()) or sum(int(x[1]) for x in righe) != sum(attesi.values()):
                    errori.append(f"SELT: tabella {tid} dell'indice diversa dal ricalcolo ({len(righe)} righe, attese {len(attesi)})")
            if b2_ok and "B2 for settlement applications made on or after 26 March 2027" not in prima:
                errori.append("SELT: prima frase dell'indice senza il cambio B2 del 26 March 2027")
            continue
        dove, luogo = chi
        qui = [r for r in uk if r[2] == luogo] if dove == "uk" else [r for r in est if r[2] == luogo]
        m = len(qui)
        if f"<strong>{m:,} approved centre{'s' if m != 1 else ''}</strong>" not in prima:
            errori.append(f"SELT: numero di centri nella prima frase di {percorso} diverso da {m}")
        tab = re.search(r'<table[^>]*id="t-centri".*?</table>', main, re.S)
        righe = re.findall(r"<tr><td>", tab.group(0)) if tab else []
        if len(righe) != m:
            errori.append(f"SELT: {len(righe)} righe nella tabella di {percorso}, attesi {m} centri")
        corpo_tab = html.unescape(tab.group(0)) if tab else ""
        for r in qui:
            nome, ind = (r[1], r[3]) if dove == "uk" else (r[1], r[4])
            if nome not in corpo_tab or ind not in corpo_tab:
                errori.append(f"SELT: centro {nome!r} o indirizzo mancante in {percorso}")
                break
        if dove == "estero":
            for c in {r[3] for r in qui}:
                if f"<td>{html.escape(c)}</td>" not in tab.group(0):
                    errori.append(f"SELT: città {c} mancante in {percorso}")
    # collegamenti dal resto del sito
    for f, link in (("index.html", 'href="uk-english-test/"'), ("uk-spouse-visa/index.html", 'href="../uk-english-test/"')):
        if link not in (SITO / f).read_text(encoding="utf-8"):
            errori.append(f"SELT: {f} non rimanda alla sezione")
    return errori, n



# ---------------------------------------------------------------- 17. Irlanda: PPS assegnati per nazionalità (30/10/2026)
def _sorgente(url, nome_locale):
    """File ufficiale grezzo: da raccolta/_grezzi/ se c'è, altrimenti scaricato (None se offline o non raggiungibile)."""
    import urllib.request
    f = SITO.parent / "raccolta" / "_grezzi" / nome_locale
    if f.exists():
        return f.read_bytes()
    if "--offline" in sys.argv:
        return None
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
    except Exception:  # noqa: BLE001
        return None


def controlla_ppsn():
    """17. Ricalcolo indipendente da dati/ppsn.json: impronta; pagine 'nazionalità × Irlanda' attese (PPS ≥ 500 nell'ultimo anno intero
    o primi permessi Eurostat ≥ 500) tutte in sitemap; titoli ≤ 70 con l'anno; prima frase con il numero dell'anno in corso, quello
    dell'anno intero e la data della pagina gov.ie; tabella mese per mese e tabella anno per anno uguali ai dati; confronto con gli
    stessi mesi dell'anno prima; riquadro "what this number is" con le frasi di gov.ie; cifra Eurostat uguale a trasferimenti.json;
    blocco e link dalla pagina della nazionalità; colonna dell'indice. Più 10 valori a caso ricontrollati sui CSV ufficiali (letti qui
    con un lettore proprio, non con raccolta/ppsn.py)."""
    import csv
    import hashlib
    import io
    errori = []
    D = json.loads((SITO.parent / "dati" / "ppsn.json").read_text(encoding="utf-8"))
    TR = json.loads((SITO.parent / "dati" / "trasferimenti.json").read_text(encoding="utf-8"))
    cont = {"anni": D["anni"], "mesi": D["mesi"], "nazionalita": D["nazionalita"], "tutte": D["tutte"], "righe_sommate": D["righe_sommate"]}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != D["impronta"]:
        errori.append("PPS: impronta di dati/ppsn.json diversa dal contenuto (file modificato a mano?)")
    mesi = D["mesi"]
    ult = mesi[-1]
    ytd = ult[:4] if not ult.endswith("-12") else None
    pieno = str(int(ult[:4]) - 1) if ytd else ult[:4]
    mm = int(ult[5:])
    nomi_mesi = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    def num(n):
        return f"{n:,}"
    def var(a, b):
        x = (a - b) / b * 100
        return f"{'+' if x > 0 else '−'}{abs(x):.{2 if abs(x) < 0.05 else 1}f}%"
    sitemap = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    agg = G.data_lunga(D["fonti"]["pagina"]["aggiornata"])
    eu = TR["eurostat"]["dati"]
    y1 = TR["anni"][-1]
    n = 0
    for c, x in D["nazionalita"].items():
        s = G.NAZ_TR[c][0]
        atteso = (x["anni"].get(pieno) or 0) >= 500 or ((eu.get(c, {}).get("IE", {}).get(y1) or [0])[0] or 0) >= 500
        f = SITO / "moved-to" / s / "ireland" / "index.html"
        if f.exists() != atteso:
            errori.append(f"PPS: pagina {s}/ireland {'mancante' if atteso else 'in più'}")
        hub = (SITO / "moved-to" / s / "index.html").read_text(encoding="utf-8")
        if 'id="ireland-pps"' not in hub or (atteso and 'href="ireland/"' not in hub):
            errori.append(f"PPS: blocco o link all'Irlanda mancante nella pagina della nazionalità {s}")
        if not f.exists():
            continue
        n += 1
        percorso = f"moved-to/{s}/ireland/"
        t = f.read_text(encoding="utf-8")
        main = t.split('<main id="main">', 1)[1].split("</main>", 1)[0]
        if f"<loc>{G.URL_SITO}/{percorso}</loc>" not in sitemap:
            errori.append(f"PPS: {percorso} non in sitemap")
        titolo = html.unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(titolo) > 70 or (ytd or pieno) not in titolo:
            errori.append(f"PPS: titolo di {percorso} oltre 70 caratteri o senza l'anno: {titolo!r}")
        lead = re.search(r'<p class="lead">(.*?)</p>', main, re.S).group(1)
        n_ytd = sum(x["mesi"][f"{ytd}-{m:02d}"] for m in range(1, mm + 1)) if ytd else None
        n_ytd0 = sum(x["mesi"][f"{pieno}-{m:02d}"] for m in range(1, mm + 1)) if ytd else None
        if ytd and (f"<strong>{num(n_ytd)}</strong> PPS numbers to" not in lead or f"to {nomi_mesi[mm - 1]} {ytd}" not in lead):
            errori.append(f"PPS: numero dell'anno in corso di {percorso} diverso dai dati ({n_ytd})")
        if f"<strong>{num(x['anni'][pieno])}</strong> in {pieno}" not in lead or f"file updated on {agg}" not in lead:
            errori.append(f"PPS: numero {pieno} o data della fonte di {percorso} diversi dai dati")
        if ytd and (f"was {num(n_ytd0)}" not in lead or var(n_ytd, n_ytd0) not in lead):
            errori.append(f"PPS: confronto con gli stessi mesi del {pieno} di {percorso} diverso dai dati")
        piano = html.unescape(re.sub(r"<[^>]+>", "", main))
        if "It is not a count of people who arrived" not in piano or D["fonti"]["servizio"]["frasi"][1] not in piano:
            errori.append(f"PPS: riquadro 'what this number is' incompleto in {percorso}")
        # tabella mese per mese
        tab = re.search(r'id="t-pps-mesi">.*?<tbody>(.*?)</tbody>', main, re.S).group(1)
        anni_m = sorted({m[:4] for m in mesi})
        for i, riga in enumerate(re.findall(r'<tr><th scope="row">(\w+)</th>(.*?)</tr>', tab)):
            if riga[0] not in nomi_mesi:
                continue
            celle = re.findall(r'data-v="(\d*)"', riga[1])
            for a, v in zip(anni_m, celle):
                atteso_v = x["mesi"].get(f"{a}-{nomi_mesi.index(riga[0]) + 1:02d}")
                if (int(v) if v else None) != atteso_v:
                    errori.append(f"PPS: {percorso} {riga[0]} {a} = {v}, atteso {atteso_v}")
        # tabella anno per anno
        tab = re.search(r'id="t-pps-anni">.*?<tbody>(.*?)</tbody>', main, re.S).group(1)
        righe = re.findall(r'<tr><td>(\d{4})[^<]*</td><td class="n" data-v="(\d*)">', tab)
        if len(righe) != len(D["anni"]) or any(int(v) != x["anni"][a] for a, v in righe):
            errori.append(f"PPS: tabella anno per anno di {percorso} diversa dai dati")
        r1 = eu.get(c, {}).get("IE", {}).get(y1)
        if r1 and r1[0] and r1[0] >= 100 and f"<strong>{num(r1[0])}</strong> first residence permits" not in main:
            errori.append(f"PPS: cifra Eurostat {y1} di {percorso} diversa da trasferimenti.json")
        for frase in ("FAQPage", "Dataset", "BreadcrumbList", "CC BY 4.0", "What this number is, and what it is not"):
            if frase not in t:
                errori.append(f"PPS: manca {frase!r} in {percorso}")
    idx = (SITO / "moved-to" / "index.html").read_text(encoding="utf-8")
    if f"Ireland PPS {pieno}" not in idx or 'id="ireland"' not in idx:
        errori.append("PPS: colonna o sezione Irlanda mancanti nell'indice moved-to")
    # 10 valori a caso ricontrollati sui CSV ufficiali (lettore indipendente)
    rng = random.Random(20261030)
    grezzi = {}
    for k in ("mensile", "annuale"):
        b = _sorgente(D["fonti"][k]["url"], f"ppsn-{k}.csv")
        if b is not None and hashlib.sha256(b).hexdigest() != D["fonti"][k]["sha256"]:
            errori.append(f"PPS: il file {k} in raccolta/_grezzi/ non è quello usato per i dati (SHA-256 diverso)")
        grezzi[k] = list(csv.reader(io.StringIO(b.decode("utf-8-sig")))) if b else None
    ricontrollati = []
    if grezzi["mensile"] and grezzi["annuale"]:
        campioni = [("m", c, m) for c in D["nazionalita"] for m in mesi] + [("a", c, a) for c in D["nazionalita"] for a in D["anni"]]
        for tipo, c, k in rng.sample(campioni, 10):
            nome = D["nazionalita"][c]["nome"]
            if tipo == "m":
                etich = f"{k[:4]} {nomi_mesi[int(k[5:]) - 1]}"
                v = sum(int(r[4]) for r in grezzi["mensile"][1:] if r[2] == nome and r[1] == etich and r[4].strip().isdigit())
                dj = D["nazionalita"][c]["mesi"][k]
                pag = SITO / "moved-to" / G.NAZ_TR[c][0] / "ireland" / "index.html"
                ok_pag = True
                if pag.exists():
                    tab = re.search(r'id="t-pps-mesi">.*?<tbody>(.*?)</tbody>', pag.read_text(encoding="utf-8"), re.S).group(1)
                    riga = re.search(rf'<th scope="row">{nomi_mesi[int(k[5:]) - 1]}</th>(.*?)</tr>', tab).group(1)
                    ok_pag = re.findall(r'data-v="(\d*)"', riga)[sorted({m[:4] for m in mesi}).index(k[:4])] == str(v)
            else:
                v = sum(int(r[4]) for r in grezzi["annuale"][1:] if r[2] == nome and r[0] == k)
                dj = D["nazionalita"][c]["anni"][k]
                pag = SITO / "moved-to" / G.NAZ_TR[c][0] / "ireland" / "index.html"
                ok_pag = (not pag.exists()) or bool(re.search(rf'<tr><td>{k}[^<]*</td><td class="n" data-v="{v}">', pag.read_text(encoding="utf-8")))
            ricontrollati.append(f"{c} {k}: file {v}, dati {dj}, pagina {'ok' if ok_pag else 'DIVERSA'}")
            if v != dj or not ok_pag:
                errori.append(f"PPS: valore ricontrollato diverso dal file ufficiale: {c} {k} (file {v}, dati {dj})")
    return errori, n, ricontrollati


# ---------------------------------------------------------------- 18. Thailand DTV visa, ambasciata per ambasciata (30/10/2026)
def controlla_dtv(online=True):
    """18. Ricalcolo indipendente da dati/dtv.json: impronta; pagine attese (indice + sedi con domanda e con costo o regola sulla
    residenza) tutte in sitemap e nessuna in più; titoli ≤ 70; prima frase con risposta, fonte e data; righe della tabella = sedi lette,
    con costo e regola uguali ai dati; frammenti citati presenti; avviso "Not legal or immigration advice"; nessuna promessa
    sull'approvazione; link di affiliazione solo SafetyWing (sponsored noopener, riga di trasparenza, dopo le informazioni ufficiali,
    con la frase che l'assicurazione non è richiesta); collegamenti dal resto del sito. Online: 10 frammenti a caso ricontrollati
    sulle pagine ufficiali riscaricate (con --offline si salta)."""
    import hashlib
    errori = []
    D = json.loads((SITO.parent / "dati" / "dtv.json").read_text(encoding="utf-8"))
    aff = json.loads((SITO.parent / "dati" / "affiliati.json").read_text(encoding="utf-8")).get("_safetywing_dtv", {})
    cont = {"sedi": D["sedi"], "letture": D["letture"], "generale": D["generale"]}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != D["impronta"]:
        errori.append("DTV: impronta di dati/dtv.json diversa dal contenuto (file modificato a mano?)")
    L = D["letture"]
    con_pag = [x["id"] for x in L if x["domanda"] and ("costo" in x or "residenza" in x)]
    sez = SITO / "thailand-dtv-visa"
    trovate = {f.parent.relative_to(sez).as_posix().replace(".", "") for f in sez.rglob("index.html")}
    if trovate != set([""] + con_pag):
        errori.append(f"DTV: pagine diverse da quelle attese (in più {sorted(trovate - set([''] + con_pag))}, mancanti {sorted(set([''] + con_pag) - trovate)})")
    sitemap = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    letto = G.data_lunga(D["letto_il"])
    def costo(c):
        pre, post = {"GBP": ("£", ""), "USD": ("US$", ""), "EUR": ("€", ""), "THB": ("", " baht (THB)"), "MYR": ("RM", ""), "SGD": ("S$", ""),
                     "EGP": ("", " Egyptian pounds (EGP)"), "PLN": ("", " złoty (PLN)"), "INR": ("₹", ""), "CNY": ("", " yuan (CNY)")}[c["valuta"]]
        return f"{pre}{c['importo']:,}{post}"
    n = 0
    for slug in [""] + con_pag:
        f = sez / slug / "index.html" if slug else sez / "index.html"
        if not f.exists():
            continue
        n += 1
        percorso = f"thailand-dtv-visa/{slug + '/' if slug else ''}"
        t = f.read_text(encoding="utf-8")
        main = t.split('<main id="main">', 1)[1].split("</main>", 1)[0]
        testo_main = html.unescape(re.sub(r"<[^>]+>", " ", main))
        if f"<loc>{G.URL_SITO}/{percorso}</loc>" not in sitemap:
            errori.append(f"DTV: {percorso} non in sitemap")
        titolo = html.unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(titolo) > 70:
            errori.append(f"DTV: titolo oltre 70 caratteri in {percorso}: {titolo!r} ({len(titolo)})")
        lead = html.unescape(re.sub(r"<[^>]+>", "", re.search(r'<p class="lead">(.*?)</p>', main, re.S).group(1)))
        if letto not in lead:
            errori.append(f"DTV: prima frase senza la data di lettura in {percorso}")
        for frase in ("Not legal or immigration advice.", "FAQPage", "BreadcrumbList", "31 August 2026"):
            if frase not in t:
                errori.append(f"DTV: manca {frase!r} in {percorso}")
        if re.search(r"\b(guarantee[sd]?|will be approved|will get (?:a|the|your) visa|100% approval|easy approval)\b", testo_main, re.I):
            errori.append(f"DTV: promessa sull'approvazione in {percorso}")
        # affiliazione
        sw = re.findall(r'<a [^>]*href="([^"]*safetywing[^"]*)"[^>]*rel="([^"]*)"', main)
        altri_sp = [h for h in re.findall(r'<a [^>]*href="([^"]+)"[^>]*rel="[^"]*sponsored', main) if "safetywing.com" not in h]
        if altri_sp:
            errori.append(f"DTV: link sponsorizzati non ammessi in {percorso}: {altri_sp[:2]}")
        if aff.get("url"):
            if len(sw) != 1 or html.unescape(sw[0][0]) != aff["url"] or sw[0][1] != "sponsored noopener":
                errori.append(f"DTV: riquadro SafetyWing assente, doppio o con rel sbagliato in {percorso}")
            if G.MON.RIGA_EN not in main or "Insurance is not a DTV requirement" not in main or "does not change the decision on your visa" not in main:
                errori.append(f"DTV: riga di trasparenza o frase 'assicurazione non richiesta' mancanti in {percorso}")
            if main.find("safetywing") < main.find("What the official page says" if slug else 'id="table"'):
                errori.append(f"DTV: SafetyWing prima delle informazioni ufficiali in {percorso}")
        elif sw:
            errori.append(f"DTV: link SafetyWing in {percorso} ma voce spenta in dati/affiliati.json")
        if slug:
            x = next(y for y in L if y["id"] == slug)
            if "costo" in x and costo(x["costo"]) not in lead:
                errori.append(f"DTV: costo di {slug} nella prima frase diverso dai dati ({costo(x['costo'])})")
            for campo in ("costo", "residenza", "saldo"):
                if campo in x and html.escape(x[campo]["frammento"].rstrip("."), quote=False) not in main:
                    errori.append(f"DTV: frammento {campo} di {slug} non citato nella pagina")
            agg = G.data_lunga(max(p["modificata"] for p in x["pagine"]))
            if agg not in lead:
                errori.append(f"DTV: data di modifica della pagina ufficiale mancante nella prima frase di {slug}")
        else:
            tab = re.search(r'id="t-dtv">.*?<tbody>(.*?)</tbody>', main, re.S).group(1)
            righe = re.findall(r"<tr>(.*?)</tr>", tab, re.S)
            if len(righe) != len(L):
                errori.append(f"DTV: la tabella dell'indice ha {len(righe)} righe, attese {len(L)}")
            for x in L:
                riga = next((r for r in righe if re.search(rf'>{re.escape(html.escape(x["sede"], quote=False))}<', r)), None)
                if not riga:
                    errori.append(f"DTV: riga di {x['sede']} mancante nell'indice")
                    continue
                if ("costo" in x and costo(x["costo"]) not in html.unescape(riga)) or ("costo" not in x and "Not written on the page" not in riga):
                    errori.append(f"DTV: costo di {x['sede']} nell'indice diverso dai dati")
                if "residenza" in x and html.escape(x["residenza"]["frammento"].rstrip("."), quote=False) not in riga:
                    errori.append(f"DTV: regola sulla residenza di {x['sede']} nell'indice diversa dai dati")
                if html.escape(x["pagine"][0]["url"]) not in riga and x["pagine"][0]["url"] not in riga:
                    errori.append(f"DTV: link ufficiale di {x['sede']} mancante nell'indice")
            altre = re.search(r'id="t-altre">.*?<tbody>(.*?)</tbody>', main, re.S).group(1)
            if len(re.findall(r"<tr>", altre)) + len(L) != len(D["sedi"]):
                errori.append("DTV: sedi lette + altre sedi diverso dall'elenco ufficiale")
            for v in ("vientiane", "london", "washington-dc"):
                x = next(y for y in L if y["id"] == v)
                if costo(x["costo"]) not in lead:
                    errori.append(f"DTV: costo di {v} mancante nella prima frase dell'indice")
            if "60 countries and territories" not in main or "15 September 2026" not in main:
                errori.append("DTV: sezione sull'esenzione di 30 giorni mancante o incompleta")
    for f, link in (("index.html", 'href="thailand-dtv-visa/"'), ("digital-nomad-visa-income-requirements/index.html", 'href="../thailand-dtv-visa/"'),
                    ("how-it-works/index.html", 'href="../thailand-dtv-visa/"')):
        if link not in (SITO / f).read_text(encoding="utf-8"):
            errori.append(f"DTV: {f} non rimanda alla sezione")
    if "Thailand (DTV)," in (SITO / "digital-nomad-visa-income-requirements" / "index.html").read_text(encoding="utf-8"):
        errori.append("DTV: la pagina dei nomadi elenca ancora la Thailandia tra i visti non coperti")
    # 10 frammenti a caso ricontrollati sulle pagine ufficiali riscaricate
    ricontrollati = []
    if online:
        sys.path.insert(0, str(SITO.parent / "raccolta"))
        import dtv as R  # solo per scaricare e normalizzare il testo nello stesso modo
        rng = random.Random(20261030)
        campioni = [(x["id"], campo, v) for x in L for campo in ("costo", "residenza", "saldo") if campo in x for v in [x[campo]]]
        campioni += [(x["id"], "altre", a) for x in L for a in x.get("altre", [])]
        for sid, campo, v in rng.sample(campioni, 10):
            x = next(y for y in L if y["id"] == sid)
            u = x["pagine"][v["p"]]["url"]
            letta = R.leggi(u)
            ok = letta["ok"] and v["frammento"] in letta["_testo"]
            ricontrollati.append(f"{sid} {campo}: {'presente' if ok else 'ASSENTE'} ({v['frammento'][:50]}…)")
            if not ok:
                errori.append(f"DTV: frammento non più nella pagina ufficiale: {sid} {campo} ({u})")
    return errori, n, ricontrollati

# ---------------------------------------------------------------- 19-20. Sezioni per studenti: US OPT e UK Graduate visa (30/10/2026)
from datetime import date as _date, timedelta as _td
import calendar as _cal


def _d(s):
    try:
        return _date.fromisoformat(s) if s else None
    except ValueError:
        return None


def _am(d, n):
    """Aggiunge n mesi; se il giorno non esiste nel mese di arrivo, ultimo giorno del mese."""
    y, m = divmod(d.month - 1 + n, 12)
    y += d.year
    return _date(y, m + 1, min(d.day, _cal.monthrange(y, m + 1)[1]))


def py_finestra(fine, dso, k):
    e = _d(fine)
    if not e:
        return None
    r = {"apre": (e - _td(k["prima"])).isoformat(), "chiude": (e + _td(k["dopo"])).isoformat(), "limite": "fine",
         "inizio_max": (e + _td(k["inizio"])).isoformat(), "chiude_30": (e + _td(k["nuova"])).isoformat()}
    d = _d(dso)
    if d:
        l = (d + _td(k["dso"])).isoformat()
        r["dso_entro"] = l
        if l < r["chiude"]:
            r["chiude"], r["limite"] = l, "dso"
        r["chiude_30"] = min(r["chiude_30"], l)
        if d.isoformat() > r["apre"]:
            r["apre"], r["apre_dso"] = d.isoformat(), True
    r["impossibile"] = r["apre"] > r["chiude"]
    return r


def py_disoccupazione(inizio, limite, usati, oggi):
    s = _d(inizio)
    if not s:
        return None
    r = {"limite": limite, "ultimo": (s + _td(limite - 1)).isoformat(), "oltre": (s + _td(limite)).isoformat()}
    if usati is not None:
        u = max(0, int(usati))
        r["usati"], r["rimasti"] = u, max(0, limite - u)
        if r["rimasti"] > 0:
            r["ultimo_da_oggi"] = (_d(oggi) + _td(r["rimasti"] - 1)).isoformat()
    return r


def py_stem(scad, dso, k):
    e = _d(scad)
    if not e:
        return None
    r = {"apre": (e - _td(k["prima"])).isoformat(), "scade": e.isoformat(), "proroga_fino": (e + _td(k["proroga"])).isoformat()}
    d = _d(dso)
    if d:
        r["dso_entro"] = (d + _td(k["dso"])).isoformat()
        if d.isoformat() > r["apre"]:
            r["apre"], r["apre_dso"] = d.isoformat(), True
    r["impossibile"] = r["apre"] >= r["scade"] or bool(r.get("dso_entro") and r["dso_entro"] < r["apre"])
    return r


def py_graduate(dom, tipo, dec, scad, k):
    a = _d(dom)
    if not a:
        return None
    m = k["m_phd"] if tipo == "phd" else (k["m_prima"] if dom < k["cambio"] else k["m_dopo"])
    d8 = a + _td(k["sett"] * 7)
    r = {"mesi": m, "prima_del_cambio": dom < k["cambio"], "giorni_al_cambio": (_d(k["cambio"]) - a).days, "fine_subito": _am(a, m).isoformat(),
         "decisione_8": d8.isoformat(), "fine_8": _am(d8, m).isoformat()}
    d = _d(dec)
    if d:
        if d.isoformat() < dom:
            r["dec_errore"] = True
        else:
            r["decisione"], r["fine"] = d.isoformat(), _am(d, m).isoformat()
    s = _d(scad)
    if s:
        r["scad"], r["tardi"] = s.isoformat(), dom >= s.isoformat()
    return r


def py_costo(mesi, adulti, figli, k):
    ia, im = k["ihs_a"] * mesi / 12, k["ihs_m"] * mesi / 12
    t, i = (adulti + figli) * k["tassa"], adulti * ia + figli * im
    return {"tasse": t, "ihs": i, "totale": t + i, "ihs_adulto": ia, "ihs_figlio": im, "persone": adulti + figli}


def casi_studio(seme=30, n=400):
    rng = random.Random(seme)
    def gd(a="2026-01-01", b="2028-12-31"):
        x, y = _date.fromisoformat(a), _date.fromisoformat(b)
        return (x + _td(rng.randint(0, (y - x).days))).isoformat()
    fissi = [("finestra", ["2026-12-18", "", None]), ("finestra", ["2027-05-15", "2027-06-01", None]), ("finestra", ["2027-08-31", "2027-05-20", None]),
             ("disoccupazione", ["2026-06-01", 90, 20, "2026-10-30"]), ("disoccupazione", ["2027-01-10", 150, None, "2026-10-30"]),
             ("stem", ["2027-03-31", "", None]), ("stem", ["2026-11-15", "2026-11-20", None]),
             ("graduate", ["2026-12-31", "altro", "", "", None]), ("graduate", ["2027-01-01", "altro", "2027-02-20", "", None]),
             ("graduate", ["2028-08-31", "altro", "", "", None]), ("graduate", ["2027-03-10", "phd", "", "2027-02-01", None]),
             ("costo", [18, 2, 1, None]), ("costo", [24, 1, 0, None]), ("costo", [36, 3, 2, None])]
    casuali = []
    for _ in range(n):
        tipo = rng.choice(["finestra", "disoccupazione", "stem", "graduate", "costo"])
        if tipo == "finestra":
            f = gd()
            casuali.append((tipo, [f, rng.choice(["", (_d(f) + _td(rng.randint(-120, 90))).isoformat()]), None]))
        elif tipo == "disoccupazione":
            casuali.append((tipo, [gd(), rng.choice([90, 150]), rng.choice([None, rng.randint(0, 160)]), gd("2026-10-01", "2027-12-31")]))
        elif tipo == "stem":
            f = gd()
            casuali.append((tipo, [f, rng.choice(["", (_d(f) + _td(rng.randint(-150, 30))).isoformat()]), None]))
        elif tipo == "graduate":
            a = gd("2026-06-01", "2028-06-30")
            casuali.append((tipo, [a, rng.choice(["altro", "phd"]), rng.choice(["", (_d(a) + _td(rng.randint(-10, 200))).isoformat()]),
                                   rng.choice(["", gd("2026-06-01", "2028-06-30")]), None]))
        else:
            casuali.append((tipo, [rng.choice([18, 24, 36]), rng.randint(1, 4), rng.randint(0, 4), None]))
    return fissi + casuali


def confronta_js_studio(file_pagina, k_tutti):
    """Esegue con node il JS dei calcolatori preso dalla pagina pubblicata e lo confronta con le funzioni Python qui sopra."""
    t = (SITO / file_pagina).read_text(encoding="utf-8")
    js = next(s for s in re.findall(r"<script>(.*?)</script>", t, re.S) if "window.CALC_STUDIO=C" in s)
    casi = casi_studio()
    prog = ("var window={};var document={querySelectorAll:function(){return [];}};\n" + js +
            "\nvar K=" + json.dumps(k_tutti) + ";var CASI=" + json.dumps(casi) + ";var C=window.CALC_STUDIO;var out=CASI.map(function(c){var a=c[1];"
            "if(c[0]==='finestra')return C.finestra(a[0],a[1],K.finestra);if(c[0]==='disoccupazione')return C.disoccupazione(a[0],a[1],a[2]===null?'':a[2],a[3]);"
            "if(c[0]==='stem')return C.stem(a[0],a[1],K.stem);if(c[0]==='graduate')return C.graduate(a[0],a[1],a[2],a[3],K.graduate);"
            "return C.costo(a[0],a[1],a[2],K.graduate);});console.log(JSON.stringify(out));")
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(prog)
    r = subprocess.run(["node", f.name], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        return [f"JS dei calcolatori non eseguibile: {r.stderr[-300:]}"], 0
    ris = json.loads(r.stdout)
    errori = []
    for (tipo, a), j in zip(casi, ris):
        if tipo == "finestra":
            p = py_finestra(a[0], a[1], k_tutti["finestra"])
        elif tipo == "disoccupazione":
            p = py_disoccupazione(a[0], a[1], a[2], a[3])
        elif tipo == "stem":
            p = py_stem(a[0], a[1], k_tutti["stem"])
        elif tipo == "graduate":
            p = py_graduate(a[0], a[1], a[2], a[3], k_tutti["graduate"])
        else:
            p = py_costo(a[0], a[1], a[2], k_tutti["graduate"])
        if p != j:
            errori.append(f"calcolatore {tipo} {a}: JS {j} ≠ Python {p}")
    return errori[:10], len(casi)


def _pagine_sezione(sez, attese, errori, nome, affiliati=False):
    cart = SITO / sez.rstrip("/")
    trovate = {f.parent.relative_to(cart).as_posix().replace(".", "") for f in cart.rglob("index.html")}
    if trovate != set(attese):
        errori.append(f"{nome}: pagine diverse da quelle attese (in più {sorted(trovate - set(attese))}, mancanti {sorted(set(attese) - trovate)})")
    sitemap = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    out = {}
    for s in attese:
        f = cart / s / "index.html" if s else cart / "index.html"
        if not f.exists():
            continue
        percorso = f"{sez}{s + '/' if s else ''}"
        t = f.read_text(encoding="utf-8")
        main = t.split('<main id="main">', 1)[1].split("</main>", 1)[0]
        if f"<loc>{G.URL_SITO}/{percorso}</loc>" not in sitemap:
            errori.append(f"{nome}: {percorso} non in sitemap")
        titolo = html.unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(titolo) > 70:
            errori.append(f"{nome}: titolo oltre 70 caratteri in {percorso} ({len(titolo)})")
        for x in ("FAQPage", "BreadcrumbList", "Not legal or immigration advice.", 'rel="canonical"'):
            if x not in t:
                errori.append(f"{nome}: manca {x!r} in {percorso}")
        if not affiliati and re.search(r'rel="[^"]*sponsored', main):
            errori.append(f"{nome}: link sponsorizzato in {percorso} (nessuna affiliazione prevista in questa sezione)")
        lead = html.unescape(re.sub(r"<[^>]+>", "", re.search(r'<p class="lead">(.*?)</p>', main, re.S).group(1)))
        out[s] = (t, main, html.unescape(re.sub(r"<[^>]+>", " ", main)), lead, percorso)
    return out


def controlla_opt(online=True):
    import hashlib
    errori = []
    D = json.loads((SITO.parent / "dati" / "opt.json").read_text(encoding="utf-8"))
    cont = {k: D[k] for k in ("letture", "fonti", "federal_register", "ecfr")}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != D["impronta"]:
        errori.append("OPT: impronta di dati/opt.json diversa dal contenuto")
    L = {k: v["valore"] for k, v in D["letture"].items()}
    fr = D["federal_register"]
    letto = G.data_lunga(D["letto_il"])
    attese = ["", "opt-application-deadline-calculator", "opt-unemployment-days", "stem-opt-extension-fee", "opt-fee-proposal", "opt-grace-period"]
    P = _pagine_sezione("us-opt/", attese, errori, "OPT")
    usd = lambda n: f"${n:,}"  # noqa: E731
    k_fin = {"prima": L["finestra"]["prima"], "dopo": L["finestra"]["dopo"], "dso": L["finestra"]["dso"], "inizio": L["inizio_max"], "nuova": L["regola_30"]}
    k_stem = {"prima": L["finestra_stem"]["prima"], "dso": L["finestra_stem"]["dso"], "proroga": L["proroga_stem"]}
    k_dis = {"opt": L["disoccupazione"], "stem": L["disoccupazione_stem"]}
    if L["finestra"] != L["finestra_opt"] or L["disoccupazione_uscis"] != k_dis or L["mesi_opt"] != L["mesi_opt_uscis"] or L["finestra_stem_i765"] != L["finestra_stem"]["prima"]:
        errori.append("OPT: due fonti ufficiali danno valori diversi per la stessa regola (letture)")
    calcolatori = {"": ("finestra", "disoccupazione"), "opt-application-deadline-calculator": ("finestra",), "opt-unemployment-days": ("disoccupazione",),
                   "stem-opt-extension-fee": ("stem",), "opt-grace-period": ("finestra",), "opt-fee-proposal": ()}
    costanti = {"finestra": k_fin, "disoccupazione": k_dis, "stem": k_stem}
    for s, (t, main, testo, lead, percorso) in P.items():
        if letto not in lead or re.search(r"\. [A-Z]", lead.split(letto)[0]):
            errori.append(f"OPT: data di lettura non nella prima frase in {percorso}")
        primo = lead.split(f"{letto}")[0]
        if not re.search(r"USCIS|SEVP|Federal Register", primo):
            errori.append(f"OPT: prima frase senza la fonte prima della data in {percorso}")
        for tipo in calcolatori[s]:
            m = re.search(rf'data-studio="{tipo}" data-k=\'(.*?)\'', main)
            if not m or json.loads(m.group(1)) != costanti[tipo]:
                errori.append(f"OPT: calcolatore {tipo} assente o con costanti diverse dai dati in {percorso}")
        if calcolatori[s] and "window.CALC_STUDIO=C" not in t:
            errori.append(f"OPT: script dei calcolatori mancante in {percorso}")
        if usd(L["proposta_importi"]["iniziale"]) in testo:
            pezzi = re.split(r"[.:|]\s", html.unescape(re.sub(r"<[^>]+>", " | ", main)))
            for frase in [x for x in pezzi if "$70,000" in x]:
                if re.search(r"\b(is|are) (now )?in force|takes effect on|must pay \$70", frase) and "not in force" not in frase and "Is the" not in frase:
                    errori.append(f"OPT: frase che presenta la proposta come regola in {percorso}: {frase.strip()[:120]}")
    if "" in P:
        t, main, testo, lead, _ = P[""]
        for x in (usd(L["tassa_online"]), usd(L["tassa_carta"]), usd(L["premium"]), f'{L["finestra"]["prima"]} days', f'{L["finestra"]["dopo"]} days',
                  f'{k_dis["opt"]} days', f'{k_dis["stem"]} days', f'{L["mesi_stem"]} months', "Proposal", "Final rule on hold", "In force"):
            if x not in testo:
                errori.append(f"OPT: indice senza {x!r}")
        for u in [v["url"] for v in D["fonti"].values()] + [v["html_url"] for v in fr.values()]:
            if html.escape(u) not in main and u not in main:
                errori.append(f"OPT: fonte non citata nell'indice: {u}")
    if "stem-opt-extension-fee" in P:
        testo = P["stem-opt-extension-fee"][2]
        for x in (usd(L["tassa_online"]), usd(L["tassa_carta"]), usd(L["premium"]), f'{L["proroga_stem"]} days', usd(L["proposta_importi"]["successiva"])):
            if x not in testo:
                errori.append(f"OPT: pagina STEM senza {x!r}")
    if "opt-fee-proposal" in P:
        testo = P["opt-fee-proposal"][2]
        for x in ("$70,000", "$30,000", "not in force", G.data_lunga(fr["tasse_opt"]["comments_close_on"]), fr["tasse_opt"]["citation"], "ICEB-2026-0100", "school"):
            if x not in testo:
                errori.append(f"OPT: pagina della proposta senza {x!r}")
        if fr["tasse_opt"]["type"] != "Proposed Rule" or L["proposta_importi"] != {"iniziale": 70000, "successiva": 30000}:
            errori.append("OPT: la proposta non è più una proposta da 70.000/30.000 $: rivedere i testi (anche le domande scritte a mano)")
    if "opt-grace-period" in P:
        testo = P["opt-grace-period"][2]
        for x in ("postponed", "60 days", f'{L["regola_30"]} days', G.data_lunga(L["rinvio_regola"]), "previous regulatory provisions", D["ecfr"]["precedente"]["url"]):
            if x not in testo and html.escape(x) not in P["opt-grace-period"][1]:
                errori.append(f"OPT: pagina del periodo di grazia senza {x!r}")
    if "opt-unemployment-days" in P:
        if "Count each day without employer information" not in D["letture"]["conteggio_giorni"]["frammento"] or "each day without employer information" not in P["opt-unemployment-days"][2]:
            errori.append("OPT: regola di conteggio dei giorni di disoccupazione mancante")
    for f, link in (("index.html", 'href="us-opt/"'), ("how-it-works/index.html", 'href="../us-opt/"'), ("about/index.html", 'href="../us-opt/"')):
        if link not in (SITO / f).read_text(encoding="utf-8"):
            errori.append(f"OPT: {f} non rimanda alla sezione")
    e_js, n_js = confronta_js_studio("us-opt/index.html", {"finestra": k_fin, "stem": k_stem, "graduate": json.loads(re.search(
        r'data-studio="graduate" data-k=\'(.*?)\'', (SITO / "uk-graduate-visa/index.html").read_text(encoding="utf-8")).group(1))})
    errori += e_js
    riletti = []
    if online:
        for k, d in fr.items():
            try:
                x = json.loads(urllib.request.urlopen(f"https://www.federalregister.gov/api/v1/documents/{d['document_number']}.json", timeout=60).read())
                ok = all(x.get(c) == d.get(c) for c in ("type", "publication_date", "effective_on", "comments_close_on", "citation"))
            except Exception as e:  # noqa: BLE001
                ok, x = False, {"errore": str(e)[:80]}
            riletti.append(f"Federal Register {d['citation']}: {'uguale' if ok else 'CAMBIATO'}")
            if not ok:
                errori.append(f"OPT: documento del Federal Register cambiato o non leggibile: {d['citation']}")
        r = subprocess.run(["node", str(SITO.parent / "raccolta" / "browser.js"), D["fonti"]["i765"]["url"]], capture_output=True, text=True, timeout=300)
        try:
            tx = json.loads(r.stdout)[D["fonti"]["i765"]["url"]]["testo"]
        except (ValueError, KeyError):
            tx = ""
        for k in ("finestra", "finestra_stem_i765", "rinvio_regola", "regole_precedenti"):
            ok = D["letture"][k]["frammento"] in tx
            riletti.append(f"USCIS I-765 {k}: {'presente' if ok else 'ASSENTE'}")
            if not ok:
                errori.append(f"OPT: frammento {k} non più nella pagina I-765 di USCIS")
    return errori, len(P), n_js, riletti


def controlla_graduate(online=True):
    import hashlib
    errori = []
    D = json.loads((SITO.parent / "dati" / "graduate.json").read_text(encoding="utf-8"))
    cont = {k: D[k] for k in ("letture", "fonti", "tariffa_ods")}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != D["impronta"]:
        errori.append("Graduate: impronta di dati/graduate.json diversa dal contenuto")
    L = {k: v["valore"] for k, v in D["letture"].items()}
    letto = G.data_lunga(D["letto_il"])
    k = {"cambio": L["durata_18_mesi"]["dal"], "m_prima": L["durata_2_anni"]["mesi"], "m_dopo": L["durata_18_mesi"]["mesi"], "m_phd": L["durata_phd"]["mesi"],
         "sett": L["decisione_settimane"], "tassa": L["tassa"], "ihs_a": L["ihs_adulti"], "ihs_m": L["ihs_minori"]}
    if (k["cambio"], k["m_prima"], k["m_dopo"], k["m_phd"], L["durata_2_anni"]["fino_al"]) != ("2027-01-01", 24, 18, 36, "2026-12-31"):
        errori.append("Graduate: durate o date diverse da quelle scritte nei testi delle pagine: rivedere i testi")
    if L["ihs_anno"] != L["ihs_adulti"] or abs(L["ihs_18"] - 1.5 * L["ihs_adulti"]) > 0.001 or L["ihs_24"] != 2 * L["ihs_adulti"] or L["ihs_36"] != 3 * L["ihs_adulti"]:
        errori.append("Graduate: importi della guida e della pagina IHS non coerenti")
    if D["tariffa_ods"]["riga"][2] != f"£{L['tassa']:,}":
        errori.append("Graduate: tariffa della tabella ODS diversa dalla guida")
    P = _pagine_sezione("uk-graduate-visa/", ["", "18-months", "cost", "phd"], errori, "Graduate")
    gbp = lambda x: "£" + (f"{x:,.2f}"[:-3] if f"{x:,.2f}".endswith(".00") else f"{x:,.2f}")  # noqa: E731
    for s, (t, main, testo, lead, percorso) in P.items():
        if letto not in lead or re.search(r"\. [A-Z]", lead.split(letto)[0]):
            errori.append(f"Graduate: data di lettura non nella prima frase in {percorso}")
        if not re.search(r"GOV\.UK|Immigration Rules", lead.split(letto)[0]):
            errori.append(f"Graduate: prima frase senza fonte in {percorso}")
        m = re.search(r'data-studio="graduate" data-k=\'(.*?)\'', main)
        if not m or json.loads(m.group(1)) != k:
            errori.append(f"Graduate: calcolatore assente o con costanti diverse dai dati in {percorso}")
        if "Open Government Licence v3.0" not in testo:
            errori.append(f"Graduate: manca l'attribuzione OGL in {percorso}")
        for x in ("1 January 2027", "18 months", "3 years", gbp(L["tassa"])):
            if x not in testo:
                errori.append(f"Graduate: manca {x!r} in {percorso}")
    if "" in P:
        testo, main = P[""][2], P[""][1]
        for x in ("31 December 2026", gbp(L["ihs_adulti"]), gbp(L["ihs_minori"]), gbp(L["ihs_18"]), gbp(L["ihs_24"]), gbp(L["ihs_36"]), "8 weeks", "before your Student visa expires"):
            if x not in testo:
                errori.append(f"Graduate: indice senza {x!r}")
        for u in [v["url"] for v in D["fonti"].values()]:
            if html.escape(u) not in main and u not in main:
                errori.append(f"Graduate: fonte non citata nell'indice: {u}")
        if html.escape(D["letture"]["regola_18"]["frammento"], quote=False) not in main:
            errori.append("Graduate: citazione di GR 8.1 mancante")
    if "cost" in P:
        tab = re.search(r'id="t-famiglie-grad".*?<tbody>(.*?)</tbody>', P["cost"][1], re.S).group(1)
        for (a, f), riga in zip(((1, 0), (2, 0), (2, 1), (2, 2)), re.findall(r"<tr>(.*?)</tr>", tab, re.S)):
            for mesi in (24, 18, 36):
                v = gbp(py_costo(mesi, a, f, k)["totale"])
                if v not in riga:
                    errori.append(f"Graduate: tabella famiglie, {a} adulti {f} figli {mesi} mesi: atteso {v}")
    for f, link in (("index.html", 'href="uk-graduate-visa/"'), ("how-it-works/index.html", 'href="../uk-graduate-visa/"'),
                    ("uk-skilled-worker-visa/index.html", 'href="../uk-graduate-visa/"')):
        if link not in (SITO / f).read_text(encoding="utf-8"):
            errori.append(f"Graduate: {f} non rimanda alla sezione")
    e_js, n_js = confronta_js_studio("uk-graduate-visa/index.html", {"finestra": {"prima": 90, "dopo": 60, "dso": 30, "inizio": 60, "nuova": 30},
                                                                     "stem": {"prima": 90, "dso": 60, "proroga": 180}, "graduate": k})
    errori += e_js
    riletti = []
    if online:
        sys.path.insert(0, str(SITO.parent / "raccolta"))
        import graduate as RG
        for fonte in ("guida", "appendice", "ihs"):
            r = RG.leggi_pagina(RG.PAGINE[fonte][0])
            tx = r[1] if len(r) == 3 else ""
            for key, v in D["letture"].items():
                if v["fonte"] == fonte:
                    ok = v["frammento"] in tx
                    riletti.append(f"GOV.UK {fonte} {key}: {'presente' if ok else 'ASSENTE'}")
                    if not ok:
                        errori.append(f"Graduate: frammento {key} non più nella pagina GOV.UK ({fonte})")
    return errori, len(P), n_js, riletti


# ---------------------------------------------------------------- 21. Mexico residency (31/10/2026)
import math as _math


def _r2(x):
    return _math.floor(x * 100 + 0.5) / 100


def py_mx(importo, val, cosa, tipo, k):
    """Stesso risultato di CALC_MX.mx (MX_JS), scritto qui senza le funzioni di genera.py."""
    if importo in ("", None):
        return None
    x = float(importo)
    if not x >= 0:
        return None
    i = 1 if cosa == "saldo" else 0
    t = k["tassi"]
    righe, nok, n = [], 0, 0
    for c in k["cons"]:
        s = c[tipo]
        if not s:
            righe.append({"id": c["id"], "assente": True})
            continue
        soglia = s[i]
        tuo = x if c["val"] == val else _r2(x / t[val] * t[c["val"]])
        ok = tuo >= soglia
        n += 1
        nok += ok
        righe.append({"id": c["id"], "soglia": soglia, "val": c["val"], "tuo": tuo, "stessa": c["val"] == val, "ok": ok, "appr": c["appr"]})
    su = k["uma"][tipo][i]
    tu = x if val == "MXN" else _r2(x / t[val] * t["MXN"])
    return {"righe": righe, "uma": {"soglia": su, "tuo": tu, "ok": (tu >= su) if i == 1 else (tu > su)}, "nok": nok, "n": n}   # saldo "equivalente a", reddito "mayores al"


def casi_mx(k, seme=31, n=400):
    rng = random.Random(seme)
    casi = [[None, "USD", "reddito", "tr"], ["", "USD", "saldo", "pr"], [0, "MXN", "reddito", "tr"]]
    for c in k["cons"]:   # esattamente sulla soglia, un centesimo sotto, nella valuta del consolato
        casi += [[c["tr"][0], c["val"], "reddito", "tr"], [round(c["tr"][0] - 0.01, 2), c["val"], "reddito", "tr"], [c["tr"][1], c["val"], "saldo", "tr"]]
        if c["pr"]:
            casi += [[c["pr"][0], c["val"], "reddito", "pr"], [c["pr"][1], c["val"], "saldo", "pr"]]
    casi += [[k["uma"]["tr"][0], "MXN", "reddito", "tr"], [k["uma"]["pr"][1], "MXN", "saldo", "pr"], [k["uma"]["tr"][1], "MXN", "saldo", "tr"]]
    for _ in range(n):
        val = rng.choice(["USD", "CAD", "GBP", "EUR", "MXN"])
        cosa, tipo = rng.choice(["reddito", "saldo"]), rng.choice(["tr", "pr"])
        base = {"USD": 1, "CAD": 1.4, "GBP": 0.75, "EUR": 0.86, "MXN": 18}[val] * (4500 if cosa == "reddito" else 75000) * (1.7 if tipo == "pr" else 1) * (4 if cosa == "saldo" and tipo == "pr" else 1)
        casi.append([round(rng.uniform(0.5, 1.5) * base, rng.choice([0, 2])), val, cosa, tipo])
    return casi


def controlla_mx(online=True):
    import hashlib
    errori = []
    D = json.loads((SITO.parent / "dati" / "mexico.json").read_text(encoding="utf-8"))
    cont = {k: D[k] for k in ("letture", "fonti", "consolati", "esclusi")}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != D["impronta"]:
        errori.append("Messico: impronta di dati/mexico.json diversa dal contenuto")
    L = {k: v["valore"] for k, v in D["letture"].items()}
    letto = G.data_lunga(D["letto_il"])
    cons = D["consolati"]
    uma = L["uma_diaria"]

    def mx(x):
        return "MXN " + (f"{x:,.0f}" if float(x).is_integer() else f"{x:,.2f}")

    def imp(x, v):
        return {"USD": "US$", "CAD": "C$", "GBP": "£", "EUR": "€", "MXN": "MXN "}[v] + (f"{x:,.0f}" if float(x).is_integer() else f"{x:,.2f}")
    # costi: Anexo 4 = LFD, importo da pagare = arrotondamento
    for n_ in "1234":
        if L["a4_rt"][n_][0] != L[f"rt_{n_}"] or L["a4_rt"][n_][1] != round(L[f"rt_{n_}"]):
            errori.append(f"Messico: costo della residenza temporanea di {n_} anni diverso tra Anexo 4 e LFD")
    if L["a4_rp"] != [L["rp"], round(L["rp"])] or L["a4_visa"][0] != L["visa"] or L["a4_cambio"][0] != L["cambio"]:
        errori.append("Messico: costi della residenza permanente, del cambio o del visto diversi tra Anexo 4 e LFD")
    giorni = {"tr": (L["rt_reddito_giorni"], L["rt_saldo_giorni"]), "pr": (L["rp_reddito_giorni"], L["rp_saldo_giorni"])}
    if giorni != {"tr": (680, 11460), "pr": (1140, 45850)} or L["familiare_giorni"] != 220:
        errori.append("Messico: giorni di UMA diversi da quelli scritti nei testi (680/11.460, 1.140/45.850, 220): rivedere i testi")
    pesos = {t: [round(g * uma, 2) for g in giorni[t]] for t in giorni}
    attese = ["", "income-requirements", "fees"] + [c["id"] for c in cons]
    P = _pagine_sezione("mexico-residency/", attese, errori, "Messico", affiliati=True)
    for s, (t, main, testo, lead, percorso) in P.items():
        prima = re.split(r"(?<=[a-z0-9)])\.\s+(?=[A-Z])", lead)[0]
        if letto not in prima:
            errori.append(f"Messico: data di lettura non nella prima frase in {percorso}")
        elif not re.search(r"Annex 4|guidelines|Diario Oficial|official", prima.split(letto)[0]):
            errori.append(f"Messico: prima frase senza la fonte prima della data in {percorso}")
        if re.search(r"(?i)you will get (the|a|your) visa|guarantee[sd]? (the|a|your) visa|will be approved", testo):
            errori.append(f"Messico: promessa sul visto in {percorso}")
        m = main.find('class="card aff-r"')
        if m >= 0:
            pezzo = main[m:main.find("</section>", m)]
            if 'rel="sponsored noopener"' not in pezzo or "safetywing.com" not in pezzo or "Insurance is not a requirement" not in html.unescape(pezzo):
                errori.append(f"Messico: riquadro SafetyWing senza sponsored noopener o senza la frase sul requisito in {percorso}")
            if m < main.find("Not legal or immigration advice."):
                errori.append(f"Messico: riquadro SafetyWing prima delle informazioni ufficiali in {percorso}")
        for a in re.findall(r'<a [^>]*rel="[^"]*sponsored[^"]*"[^>]*>', main):
            if "safetywing.com" not in a:
                errori.append(f"Messico: link sponsorizzato non previsto in {percorso}")
        # calcolatore: costanti = dati
        km = re.search(r"data-mx data-rel=\"[^\"]*\" data-k='(.*?)'", main)
        if s in ("", "income-requirements") or s in [c["id"] for c in cons]:
            if not km:
                errori.append(f"Messico: calcolatore assente in {percorso}")
            else:
                k = json.loads(km.group(1))
                attesi = {"cons": [{"id": c["id"], "sede": c["sede"], "val": c["valuta"], "tr": [c["tr"]["reddito"]["importo"], c["tr"]["saldo"]["importo"]],
                                    "pr": ([c["pr"]["reddito"]["importo"], c["pr"]["saldo"]["importo"]] if "pr" in c else None), "appr": bool(c.get("approssimato"))}
                                   for c in sorted(cons, key=lambda c: c["sede"])],
                          "uma": pesos, "tassi": {v: (1 if v == "EUR" else G.CAMBI["tassi"][v]) for v in ("EUR", "USD", "GBP", "CAD", "MXN")}, "data_cambi": G.data_lunga(G.CAMBI["data"])}
                if k != attesi:
                    errori.append(f"Messico: costanti del calcolatore diverse dai dati in {percorso}")
            if "window.CALC_MX=C" not in t:
                errori.append(f"Messico: script del calcolatore mancante in {percorso}")
    if "" in P:
        t, main, testo, lead, _ = P[""]
        for x in (mx(L["a4_rt"]["1"][1]), mx(L["a4_rp"][1]), mx(pesos["tr"][0]), mx(pesos["tr"][1]), mx(pesos["pr"][0]), mx(pesos["pr"][1]), f"MXN {uma}"):
            if x not in testo:
                errori.append(f"Messico: indice senza {x!r}")
        tab = re.search(r'id="t-cons-mx".*?<tbody>(.*?)</tbody>', main, re.S)
        righe = re.findall(r"<tr>(.*?)</tr>", tab.group(1), re.S) if tab else []
        if len(righe) != len(cons):
            errori.append(f"Messico: righe della tabella dei consolati {len(righe)} invece di {len(cons)}")
        for c in cons:
            riga = next((r for r in righe if f'href="{c["id"]}/"' in r), "")
            for tipo in ("tr", "pr"):
                for cosa in ("reddito", "saldo"):
                    if tipo in c and imp(c[tipo][cosa]["importo"], c["valuta"]) not in riga:
                        errori.append(f"Messico: tabella, {c['id']} {tipo} {cosa}: manca {imp(c[tipo][cosa]['importo'], c['valuta'])}")
            if html.escape(c["pagine"][0]["url"]) not in riga:
                errori.append(f"Messico: tabella senza il link ufficiale di {c['id']}")
        for e in D["esclusi"]:
            if html.escape(e["url"]) not in main:
                errori.append(f"Messico: consolato escluso non elencato: {e['sede']}")
        for u in [f["url"] for f in D["fonti"].values()]:
            if html.escape(u) not in main:
                errori.append(f"Messico: fonte non citata nell'indice: {u}")
    if "fees" in P:
        testo = P["fees"][2]
        for x in [mx(L["a4_rt"][n_][1]) for n_ in "1234"] + [mx(L["a4_rp"][1]), mx(L["a4_cambio"][1]), mx(L["a4_repos"][1]), mx(L["a4_visa"][1]), "50%"]:
            if x not in testo:
                errori.append(f"Messico: pagina dei costi senza {x!r}")
        tab = re.search(r'id="t-esempi-mx".*?<tbody>(.*?)</tbody>', P["fees"][1], re.S).group(1)
        for (n_, c), riga in zip(((1, L["a4_rt"]["1"][1]), (2, L["a4_rt"]["1"][1]), (1, L["a4_rp"][1]), (2, L["a4_rp"][1])), re.findall(r"<tr>(.*?)</tr>", tab, re.S)):
            if mx(n_ * c) not in riga or imp(n_ * 56, "USD") not in riga:
                errori.append(f"Messico: esempio dei costi sbagliato: {n_} × {c}")
    if "income-requirements" in P:
        testo = P["income-requirements"][2]
        for x in (mx(pesos["tr"][0]), mx(pesos["tr"][1]), mx(pesos["pr"][0]), mx(pesos["pr"][1]), mx(round(220 * uma, 2))):
            if x not in testo:
                errori.append(f"Messico: pagina del reddito senza {x!r}")
    for c in cons:
        if c["id"] not in P:
            continue
        t, main, testo, lead, percorso = P[c["id"]]
        for x in (imp(c["tr"]["reddito"]["importo"], c["valuta"]), imp(c["tr"]["saldo"]["importo"], c["valuta"])):
            if x not in lead:
                errori.append(f"Messico: prima frase di {c['id']} senza {x}")
        d = c["data_pagina"]
        if d and G.data_lunga(d) not in lead:
            errori.append(f"Messico: data della pagina del consolato non nella prima frase di {c['id']}")
        if d and d < "2026-01-01":
            errori.append(f"Messico: pagina di {c['id']} prima del 2026")
        voci = [c[tp][cs] for tp in ("tr", "pr") if tp in c for cs in ("reddito", "saldo")] + ([c["tassa"]] if "tassa" in c else []) + c.get("altre", [])
        for v in voci:
            if html.escape(v["frammento"], quote=False) not in main and html.escape(v["frammento"]) not in main:
                errori.append(f"Messico: frammento ufficiale non citato nella pagina di {c['id']}: {v['frammento'][:60]}")
        for p in c["pagine"]:
            if html.escape(p["url"]) not in main:
                errori.append(f"Messico: link ufficiale mancante nella pagina di {c['id']}")
    for f, link in (("index.html", 'href="mexico-residency/"'), ("how-it-works/index.html", 'href="../mexico-residency/"'),
                    ("digital-nomad-visa-income-requirements/index.html", 'href="../mexico-residency/"'), ("about/index.html", 'href="../mexico-residency/"')):
        if link not in (SITO / f).read_text(encoding="utf-8"):
            errori.append(f"Messico: {f} non rimanda alla sezione")
    # motore JS del calcolatore (preso dalla pagina pubblicata) = calcolo Python
    n_js = 0
    if "" in P:
        t = P[""][0]
        js = next(x for x in re.findall(r"<script>(.*?)</script>", t, re.S) if "window.CALC_MX=C" in x)
        k = json.loads(re.search(r"data-mx data-rel=\"[^\"]*\" data-k='(.*?)'", P[""][1]).group(1))
        casi = casi_mx(k)
        prog = ("var window={};var document={querySelectorAll:function(){return [];}};\n" + js + "\nvar K=" + json.dumps(k) + ";var CASI=" + json.dumps(casi)
                + ";console.log(JSON.stringify(CASI.map(function(c){return window.CALC_MX.mx(c[0],c[1],c[2],c[3],K);})));")
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
            fh.write(prog)
        r = subprocess.run(["node", fh.name], capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            errori.append(f"Messico: JS del calcolatore non eseguibile: {r.stderr[-300:]}")
        else:
            diff = [(c_, j) for c_, j in zip(casi, json.loads(r.stdout)) if py_mx(*c_, k) != j]
            n_js = len(casi)
            errori += [f"Messico: calcolatore {c_}: JS {str(j)[:120]} ≠ Python {str(py_mx(*c_, k))[:120]}" for c_, j in diff[:5]]
    riletti = []
    if online:
        sys.path.insert(0, str(SITO.parent / "raccolta"))
        import mexico as RM
        testi = {}
        for k_, f in RM.FONTI.items():
            meta, tx = RM.leggi(f["url"], oggi=_date.today().isoformat())
            testi[k_] = tx if meta else ""
        rng = random.Random(20261031)
        for key in rng.sample(sorted(D["letture"]), 10):
            v = D["letture"][key]
            ok = v["frammento"] in testi.get(v["fonte"], "")
            riletti.append(f"{v['fonte']} {key}: {'presente' if ok else 'ASSENTE'}")
            if not ok:
                errori.append(f"Messico: frammento {key} non più in {v['fonte']}")
    return errori, len(P), n_js, riletti


# ---------------------------------------------------------------- 22. Study in Italy (31/10/2026)
def py_it(i, k):
    """Stesso risultato di CALC_IT.isee (ISEE_JS), scritto qui senza le funzioni di genera.py."""
    try:
        n = int(float(i["n"])) if i["n"] not in ("", None) else 0
    except ValueError:
        return None
    if not (1 <= n <= 20) or i["reddito"] in ("", None):
        return None

    def num(v):
        if v in ("", None):
            return 0.0
        x = float(v)
        return x if x >= 0 else None
    red, ris, mq, mut = num(i["reddito"]), num(i["risparmi"]), num(i["mq"]), num(i["mutuo"])
    if None in (red, ris, mq, mut):
        return None
    t = 1 if i["val"] == "EUR" else k["cambi"].get(i["anno"], {}).get(i["val"])
    if not t:
        return None
    isr, mob = _r2(red / t), _r2(ris / t)
    imm = _r2(max(0, mq * k["mq"] - _r2(mut / t)))
    isp = _r2(mob + imm)
    ise = _r2(isr + k["quota"] * isp)
    s = k["scala"]
    sc = s[str(n)] if n <= 5 else _r2(s["5"] + (n - 5) * s["oltre"])
    isee, ispe = _r2(ise / sc), _r2(isp / sc)
    righe = [{"id": e["id"], "ok_isee": isee <= e["isee"], "ok_ispe": ispe <= e["ispe"], "ok": isee <= e["isee"] and ispe <= e["ispe"],
              "top": isee <= e["isee"] and ispe <= e["ispe"] and isee <= e["fs_isee"]} for e in k["enti"]]
    return {"t": t, "isr": isr, "mob": mob, "imm": imm, "isp": isp, "ise": ise, "scala": sc, "isee": isee, "ispe": ispe, "righe": righe,
            "povero": i["paese"] in k["poveri"], "unimi_auto": i["paese"] not in ("", "other") and i["paese"] not in k["unimi"]}


def casi_it(k, seme=22, n=400):
    rng = random.Random(seme)
    base = {"n": 4, "val": "EUR", "anno": "2025", "reddito": 10000, "risparmi": 0, "mq": 0, "mutuo": 0, "paese": ""}
    casi = [dict(base, reddito=""), dict(base, n=0), dict(base, n=21), dict(base, reddito=-5), dict(base, val="XXX"), dict(base, n="2.7"),
            dict(base, paese="Bangladesh"), dict(base, paese="Pakistan"), dict(base, paese="United States"), dict(base, paese="other")]
    for e in k["enti"]:   # esattamente sul limite e un centesimo sopra (ISEE e ISPE), in euro, una persona
        casi += [dict(base, n=1, reddito=e["isee"]), dict(base, n=1, reddito=round(e["isee"] + 0.01, 2)),
                 dict(base, n=1, reddito=0, risparmi=e["ispe"]), dict(base, n=1, reddito=0, risparmi=round(e["ispe"] + 0.01, 2)),
                 dict(base, n=1, reddito=e["fs_isee"]), dict(base, n=1, reddito=round(e["fs_isee"] + 0.01, 2))]
    valute = ["EUR"] + list(k["cambi"]["2025"])
    paesi = ["", "other", "India", "Pakistan", "Nigeria", "Bangladesh", "Nepal", "Iran", "United States", "Japan", "Egypt"]
    for _ in range(n):
        v = rng.choice(valute)
        anno = rng.choice(["2024", "2025"])
        t = 1 if v == "EUR" else k["cambi"][anno][v]
        casi.append({"n": rng.randint(1, 9), "val": v, "anno": anno, "reddito": round(rng.uniform(0, 45000) * t, rng.choice([0, 2])),
                     "risparmi": round(rng.choice([0, rng.uniform(0, 90000)]) * t, 0), "mq": rng.choice([0, 0, 60, 95.5, 120, 240, 400]),
                     "mutuo": round(rng.choice([0, 0, rng.uniform(0, 80000)]) * t, 0), "paese": rng.choice(paesi)})
    return casi


def controlla_it(online=True):
    import hashlib
    errori = []
    D = json.loads((SITO.parent / "dati" / "studio_italia.json").read_text(encoding="utf-8"))
    cont = {k: D[k] for k in ("letture", "fonti", "enti", "non_letti", "poveri", "unimi_allegato1", "cambi_bdi")}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != D["impronta"]:
        errori.append("Italia: impronta di dati/studio_italia.json diversa dal contenuto")
    L = {k: v["valore"] for k, v in D["letture"].items()}
    letto = G.data_lunga(D["letto_il"])
    enti = D["enti"]

    def e_(x):
        x = float(x)
        return "€" + (f"{x:,.0f}" if x.is_integer() else f"{x:,.2f}")
    if (L["mezzi"], L["dsu_fs"], L["isee_max"], L["ispe_max"], L["ssn_minimo"]) != (10179.85, 7171.11, 28339.88, 61608.48, 700):
        errori.append("Italia: cifre nazionali diverse da quelle scritte nelle FAQ (10.179,85 / 7.171,11 / 28.339,88 / 61.608,48 / 700): rivedere i testi")
    for E in enti:
        if E["isee"]["valore"] > L["isee_max"] or E["ispe"]["valore"] > L["ispe_max"]:
            errori.append(f"Italia: {E['id']} con limiti sopra il massimo nazionale")
    tema = ["student-visa-funds", "isee-parificato", "dsu-scholarship-deadlines", "particularly-poor-countries", "health-insurance"]
    attese = [""] + tema + [E["id"] for E in enti]
    P = _pagine_sezione("study-in-italy/", attese, errori, "Italia", affiliati=True)
    tutto = ""
    for s_, (t, main, testo, lead, percorso) in P.items():
        tutto += main
        prima = re.split(r"(?<=[a-z0-9)%])\.\s+(?=[A-Z])", lead)[0]
        if letto not in prima:
            errori.append(f"Italia: data di lettura non nella prima frase in {percorso}")
        elif not re.search(r"procedures|call|decree|Normattiva|Ministry", prima.split(letto)[0]):
            errori.append(f"Italia: prima frase senza la fonte prima della data in {percorso}")
        if re.search(r"(?i)you will get (the|a|your) (visa|scholarship)|guarantee[sd]? (the|a|your) (visa|scholarship)|will be approved", testo):
            errori.append(f"Italia: promessa in {percorso}")
        m = main.find('class="card aff-r"')
        if m >= 0:
            pezzo = html.unescape(main[m:main.find("</section>", m)])
            if s_ != "health-insurance":
                errori.append(f"Italia: riquadro affiliato fuori dalla pagina dell'assicurazione ({percorso})")
            if 'rel="sponsored noopener"' not in pezzo or "safetywing.com" not in pezzo or "SSN registration is the official route" not in pezzo:
                errori.append(f"Italia: riquadro SafetyWing senza sponsored noopener o senza la frase sul SSN in {percorso}")
            if m < main.find("Not legal or immigration advice.") or m < main.find("The three options in the procedures"):
                errori.append(f"Italia: riquadro SafetyWing prima delle informazioni ufficiali in {percorso}")
        for a in re.findall(r'<a [^>]*rel="[^"]*sponsored[^"]*"[^>]*>', main):
            if "safetywing.com" not in a or s_ != "health-insurance":
                errori.append(f"Italia: link sponsorizzato non previsto in {percorso}")
        km = re.search(r"data-isee data-rel=\"[^\"]*\" data-primo=\"[^\"]*\" data-v='[^']*' data-k='(.*?)'", main)
        if s_ in ("", "isee-parificato") or s_ in [E["id"] for E in enti]:
            if not km:
                errori.append(f"Italia: calcolatore assente in {percorso}")
            else:
                k = json.loads(html.unescape(km.group(1)))
                attesi = {"enti": [{"id": E["id"], "nome": E["nome"], "isee": E["isee"]["valore"], "ispe": E["ispe"]["valore"], "fs": E["fs"]["valore"],
                                    "fs_isee": E["fs"]["fino_isee"]} for E in enti],
                          "scala": L["scala"], "mq": 500, "quota": 0.2, "cambi": D["cambi_bdi"]["anni"]}
                if {x: k[x] for x in attesi} != attesi:
                    errori.append(f"Italia: costanti del calcolatore diverse dai dati in {percorso}")
                if sorted(k["poveri"]) != sorted(G.NOMI_POVERI_IT.get(p, p) for p in D["poveri"]):
                    errori.append(f"Italia: elenco dei Paesi poveri del calcolatore diverso dal decreto in {percorso}")
                if any(G.PAESI_ALL1_IT[p] not in D["unimi_allegato1"] for p in k["unimi"]):
                    errori.append(f"Italia: Paese del calcolatore non nell'allegato 1 UNIMI in {percorso}")
            if "window.CALC_IT=C" not in t:
                errori.append(f"Italia: script del calcolatore mancante in {percorso}")
    base_ps = L["ps_marca"] + L["ps_poste"] + L["ps_documento"]
    if "" in P:
        t, main, testo, lead, _ = P[""]
        for x in (e_(L["mezzi"]), e_(L["dsu_fs"]), e_(L["isee_max"]), e_(L["ispe_max"]), G.data_lunga(L["visto_scadenza"]), e_(round(base_ps + L["ps_contributo_1"], 2))):
            if x not in testo:
                errori.append(f"Italia: indice senza {x!r}")
        tab = re.search(r'id="t-enti-it".*?<tbody>(.*?)</tbody>', main, re.S)
        righe = re.findall(r"<tr>(.*?)</tr>", tab.group(1), re.S) if tab else []
        if len(righe) != len(enti):
            errori.append(f"Italia: righe della tabella degli enti {len(righe)} invece di {len(enti)}")
        for E in enti:
            riga = html.unescape(next((r for r in righe if f'href="{E["id"]}/"' in r), ""))
            for x in (e_(E["isee"]["valore"]), e_(E["ispe"]["valore"]), e_(E["fs"]["valore"]), G.data_lunga(E["scadenza"]["valore"])):
                if x not in riga:
                    errori.append(f"Italia: tabella, {E['id']} senza {x}")
            if E["fonti"][0] and D["fonti"][E["fonti"][0]]["url"] not in riga:
                errori.append(f"Italia: tabella senza il bando di {E['id']}")
        for x in D["non_letti"]:
            if html.escape(x["url"]) not in main:
                errori.append(f"Italia: ente non letto non elencato: {x['nome']}")
    if "student-visa-funds" in P:
        t, main, testo, lead, _ = P["student-visa-funds"]
        for x in (e_(round(base_ps + L["ps_contributo_1"], 2)), e_(round(base_ps + L["ps_contributo_2"], 2)), e_(L["ps_documento"]), e_(L["ps_contributo_2"])):
            if x not in testo:
                errori.append(f"Italia: pagina dei mezzi senza {x!r}")
        tab = re.search(r'id="t-mezzi-it".*?<tbody>(.*?)</tbody>', main, re.S)
        for r in re.findall(r"<tr>(.*?)</tr>", tab.group(1) if tab else "", re.S):
            v = re.search(r'<th[^>]*>([A-Z]{3}) ', r).group(1)
            tasso = G.CAMBI["tassi"][v] if v in G.CAMBI["tassi"] else D["cambi_bdi"]["anni"]["2025"][v]
            if f"{L['mezzi'] * tasso:,.0f}" not in r:
                errori.append(f"Italia: conversione dei mezzi in {v} sbagliata")
    if "isee-parificato" in P:
        testo = P["isee-parificato"][2]
        t_ = D["cambi_bdi"]["anni"]["2025"]["PKR"]
        isr, mob = _r2(1500000 / t_), _r2(600000 / t_)
        isp = _r2(mob + 120 * 500)
        isee = _r2(_r2(isr + 0.2 * isp) / L["scala"]["4"])
        for x in (e_(isee), e_(_r2(isp / L["scala"]["4"])), "1.57", "2.46", "0.35"):
            if x not in testo:
                errori.append(f"Italia: pagina ISEE senza {x!r} (esempio o scala)")
    if "particularly-poor-countries" in P:
        testo = P["particularly-poor-countries"][2]
        if len(D["poveri"]) != 46:
            errori.append(f"Italia: {len(D['poveri'])} Paesi poveri (il decreto ne elenca 46): rivedere i testi")
        for p in D["poveri"]:
            if html.unescape(G.NOMI_POVERI_IT.get(p, p)) not in testo:
                errori.append(f"Italia: Paese povero non elencato: {p}")
        for p in ("India", "Pakistan", "Nigeria"):
            if p in D["poveri"]:
                errori.append(f"Italia: {p} è ora tra i Paesi poveri: rivedere le FAQ")
    if "health-insurance" in P and e_(L["ssn_minimo"]) not in P["health-insurance"][2]:
        errori.append("Italia: pagina dell'assicurazione senza il minimo SSN")
    if "dsu-scholarship-deadlines" in P:
        testo = P["dsu-scholarship-deadlines"][2]
        for E in enti:
            if G.data_lunga(E["scadenza"]["valore"]) not in testo:
                errori.append(f"Italia: pagina delle scadenze senza la scadenza di {E['id']}")
    for E in enti:
        if E["id"] not in P:
            continue
        t, main, testo, lead, percorso = P[E["id"]]
        for x in (e_(E["isee"]["valore"]), e_(E["ispe"]["valore"]), e_(E["fs"]["valore"]), G.data_lunga(E["scadenza"]["valore"])):
            if x not in lead:
                errori.append(f"Italia: prima frase di {E['id']} senza {x}")
        d_ = D["fonti"][E["fonti"][0]].get("data")
        if d_ and G.data_lunga(d_) not in lead:
            errori.append(f"Italia: data del bando non nella prima frase di {E['id']}")
        for c in ("isee", "ispe", "fs", "fs_cifra", "fs_fascia", "fs_base", "servizi", "scadenza", "estero", "estero_cambio", "estero_regola", "estero_scad_fr", "isee_conferma", "poveri"):
            v = E.get(c)
            if v and html.escape(v["frammento"], quote=False) not in main and html.escape(v["frammento"]) not in main:
                errori.append(f"Italia: frammento del bando non citato nella pagina di {E['id']} ({c})")
        for k_ in E["fonti"]:
            if html.escape(D["fonti"][k_]["url"]) not in main:
                errori.append(f"Italia: link al bando mancante nella pagina di {E['id']}")
    for k_, f in D["fonti"].items():
        if html.escape(f["url"]) not in tutto:
            errori.append(f"Italia: fonte non citata in nessuna pagina della sezione: {k_}")
    for f, link in (("index.html", 'href="study-in-italy/"'), ("how-it-works/index.html", 'href="../study-in-italy/"'),
                    ("italy-digital-nomad-visa/index.html", 'href="../study-in-italy/"'), ("country/italy/index.html", 'href="../../study-in-italy/"'),
                    ("about/index.html", 'href="../study-in-italy/"')):
        if link not in (SITO / f).read_text(encoding="utf-8"):
            errori.append(f"Italia: {f} non rimanda alla sezione")
    # motore JS del calcolatore (preso dalla pagina pubblicata) = calcolo Python
    n_js = 0
    if "" in P:
        t, main = P[""][0], P[""][1]
        js = next(x for x in re.findall(r"<script>(.*?)</script>", t, re.S) if "window.CALC_IT=C" in x)
        k = json.loads(html.unescape(re.search(r"data-isee data-rel=\"[^\"]*\" data-primo=\"[^\"]*\" data-v='[^']*' data-k='(.*?)'", main).group(1)))
        casi = casi_it(k)
        casi_js = [{a: ("" if b is None else (str(b) if a in ("n", "reddito", "risparmi", "mq", "mutuo") else b)) for a, b in c.items()} for c in casi]
        prog = ("var window={};var document={querySelectorAll:function(){return [];}};\n" + js + "\nvar K=" + json.dumps(k) + ";var CASI=" + json.dumps(casi_js)
                + ";console.log(JSON.stringify(CASI.map(function(c){return window.CALC_IT.isee(c,K);})));")
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
            fh.write(prog)
        r = subprocess.run(["node", fh.name], capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            errori.append(f"Italia: JS del calcolatore non eseguibile: {r.stderr[-300:]}")
        else:
            diff = [(c_, j) for c_, j in zip(casi_js, json.loads(r.stdout)) if py_it(c_, k) != j]
            n_js = len(casi)
            errori += [f"Italia: calcolatore {c_}: JS {str(j)[:160]} ≠ Python {str(py_it(c_, k))[:160]}" for c_, j in diff[:5]]
    riletti = []
    if online:
        sys.path.insert(0, str(SITO.parent / "raccolta"))
        import studio_italia as RI
        voci = [(k_, v["fonte"], v["frammento"]) for k_, v in D["letture"].items()]
        voci += [(f"{E['id']}.{c}", E[c]["fonte"], E[c]["frammento"]) for E in enti for c in ("isee", "fs", "scadenza", "estero") if E.get(c)]
        rng = random.Random(20261031)
        scelte = rng.sample(voci, 12)
        testi = {}
        for nome, fonte, fr in scelte:
            if fonte not in testi:
                _m, testi[fonte] = RI.leggi(RI.FONTI[fonte])
            ok = fr in testi[fonte]
            riletti.append(f"{fonte} {nome}: {'presente' if ok else 'ASSENTE'}")
            if not ok:
                errori.append(f"Italia: frammento {nome} non più in {fonte}")
    return errori, len(P), n_js, riletti


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
    e14, i14 = G.MON.controlla_sito(G.SITO_ID, SITO)  # controllo comune di monetizzazione (monetizzazione.py)
    print("14. " + G.MON.riepilogo(G.SITO_ID, i14, e14))
    e15, n15 = controlla_mev()
    print(f"15. Visti Schengen a ingressi multipli: {n15} pagine (riassuntiva + riquadri per Paese), numeri ricalcolati, sitemap, titolo, link: {len(e15)} errori")
    e16, n16 = controlla_selt()
    print(f"16. Test di inglese UK (SELT): {n16} pagine (indice + città e Paesi con domanda), centri ricalcolati, sitemap, titoli, fonte, B2, affiliati: {len(e16)} errori")
    e17, n17, r17 = controlla_ppsn()
    print(f"17. Irlanda, PPS per nazionalità: {n17} pagine, numeri, tabelle, fonte, link dall'hub; 10 valori ricontrollati sui CSV ufficiali: {len(r17)}: {len(e17)} errori")
    for x in r17:
        print("    ·", x)
    e18, n18, r18 = controlla_dtv(online="--offline" not in sys.argv)
    print(f"18. Thailand DTV visa: {n18} pagine (indice + sedi), costi, regole, frammenti, affiliati, link; frammenti ricontrollati online: {len(r18)}: {len(e18)} errori")
    for x in r18:
        print("    ·", x)
    e19, n19, j19, r19 = controlla_opt(online="--offline" not in sys.argv)
    print(f"19. US OPT e STEM OPT: {n19} pagine, cifre, fonti, proposta e regola rinviata, calcolatori (JS = Python su {j19} casi); riletti online: {len(r19)}: {len(e19)} errori")
    for x in r19:
        print("    ·", x)
    e20, n20, j20, r20 = controlla_graduate(online="--offline" not in sys.argv)
    print(f"20. UK Graduate visa: {n20} pagine, durate, tariffa e IHS, tabelle ricalcolate, calcolatore (JS = Python su {j20} casi); frammenti riletti online: {len(r20)}: {len(e20)} errori")
    e21, n21, j21, r21 = controlla_mx(online="--offline" not in sys.argv)
    print(f"21. Mexico residency: {n21} pagine, costi 2026, calcolo UMA, consolati e frammenti, affiliati, link, calcolatore (JS = Python su {j21} casi); riletti online: {len(r21)}: {len(e21)} errori")
    for x in r21:
        print("    ·", x)
    e22, n22, j22, r22 = controlla_it(online="--offline" not in sys.argv)
    print(f"22. Study in Italy: {n22} pagine, cifre nazionali, enti DSU e frammenti dei bandi, Paesi poveri, cambi, esempio ISEE, affiliati, link, calcolatore (JS = Python su {j22} casi); riletti online: {len(r22)}: {len(e22)} errori")
    for x in r22:
        print("    ·", x)
    tutti = errori + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9 + e10 + e11 + e12 + e13 + e14 + e15 + e16 + e17 + e18 + e19 + e20 + e21 + e22
    for e in tutti:
        print(" -", e)
    if tutti:
        sys.exit(1)
    print("TUTTO OK")


if __name__ == "__main__":
    main()
