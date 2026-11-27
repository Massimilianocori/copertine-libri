"""Controlli prima di pubblicare Tourist Tax Calculator.

Uso (dalla radice del repository, dopo python3 touristtax/genera.py):
    python3 touristtax/verifica.py

1. Esempi calcolati a mano (TEST.md): il motore Python deve dare esattamente il risultato atteso.
2. Il motore JS (lo stesso testo che va nelle pagine) deve dare gli stessi totali del Python, sugli esempi
   e su 2.000 casi casuali (serve node).
3. Nessun link interno rotto in sito/.
4. Ogni pagina di destinazione e ogni pagina comunale francese mostra una fonte ufficiale (URL) e la data del controllo.
5. Blocco "Other useful tools for your trip" in ogni pagina indicizzabile: gli stessi link di genera.ALTRI_SITI, nell'ordine,
   mai a questo sito, tutti rel="noopener" e senza nofollow o sponsored.
6. Pagina tourist-tax-changes-2027/ (fonti, date, coerenza con i dati, link, sitemap, FAQPage).
7. Destinazioni aggiunte il 26/10/2026 (fonti 200, pagina, sitemap, pagina paese, tabella Europa).
8. Titoli, descrizioni e risposte dirette delle pagine di destinazione.
9. Sezione Messico (30/10/2026): pagine in sitemap, importi del Visitax ricalcolati qui dalla formula (2,50 × UMA di dati/uma.json),
   titoli ≤ 70 caratteri con anno e importo, risposta con fonte e data, FAQPage visibile, avviso sul sito ufficiale (solo link a
   visitax.gob.mx), link di affiliazione solo DiscoverCars con il nostro a_aid, dopo le informazioni ufficiali; voce 2027 del Visitax.
11. Giappone, tasse di soggiorno in tutto il paese (31/10/2026): enti = istantanea dell'elenco del Ministero degli Affari interni
   (49 in vigore, 18 approvati, date di partenza), fonti ufficiali go.jp/lg.jp con HTTP 200 e data, fasce ben formate, esempi a mano,
   ricalcolo indipendente in frazioni, motore JS = Python, motore nuovo = pagine esistenti (Tokyo, Kyoto, Sapporo, Kutchan, Hakuba),
   pagine (titolo ≤ 70, prima frase con cifra, fonte e data, fonti linkate, calcolatore, sitemap), pagina riassuntiva e pagina 2027.
12. Belgio (31/10/2026): Bruxelles, Gand, Bruges con fonti ufficiali datate, esempi a mano, titoli e prima frase, Anversa non coperta,
   nessun importo non ufficiale per la tassa di Bruges su crocieristi e pullman, tabella Europa, cambi 2028-2029.
13. Santiago de Compostela e Napoli (4/11/2026): fonti ufficiali con impronta sha256 e data, tariffe uguali alle fonti lette, esempi a mano,
   Napoli senza tariffe oltre il 31/12/2026, titolo ≤ 70 con anno e cifra, prima frase con cifra, fonte e data, riquadro Anno Santo 2027 /
   America's Cup 2027 con fonte ufficiale (catedraldesantiago.es, comune.napoli.it), sitemap, pagina paese, tabella Europa, pagina 2027.
14. Spagna, licenza per affitti turistici (5/11/2026, sezione spain-holiday-let-licence/): sentenze del Tribunal Supremo lette sul BOE (date e numeri
   BOE), fonti ufficiali con HTTP 200, data e impronta sha256, conteggi INE e dei registri uguali agli esempi letti a mano, nessun dato personale
   (dati/spagna_numeri.json e pagine), 27 pagine in sitemap con titolo ≤ 70 e l'anno, prima frase con cifra, fonte e data, FAQPage visibile,
   frasi delle regole regionali, avviso "Not legal advice", nessun affiliato, link dalla pagina Spagna e da /about/.
15. USA, tassa sugli alberghi in Florida e Texas (7/11/2026, sezione usa/): fonti ufficiali (Florida Department of Revenue, Texas Comptroller,
   data.texas.gov, Census) con HTTP 200, data e impronta; DR-15TDT, DR-15DSS e dataset del Texas riscaricati, impronta uguale e aliquote
   rilette con un metodo diverso (pdftotext -raw, JSON riga per riga) uguali ai dati e agli esempi letti a mano; calcoli a mano e JS = Python;
   pagine in sitemap con titolo ≤ 70 e aliquota ricalcolata, prima frase con aliquota e data, FAQ visibili = JSON-LD, avviso, calcolatore,
   nessun affiliato, nessuna frase sulle piattaforme in Florida (le fonti non ne parlano), frase del Comptroller sulle piattaforme in Texas,
   link da home, elenco delle destinazioni e about. Serve la rete (riscarica i file) e node.
10. Giappone, rimborso dell'imposta sui consumi dal 1/11/2026 (pagina japan-tax-free-refund/): dati uguali alle fonti lette, fonti
   ufficiali (JTA, NTA, Dogane) con HTTP 200 e data, sitemap, link da home e pagine giapponesi, titolo ≤ 70 con l'anno, prima frase
   con risposta, fonti e data, calcolo ricontrollato (esempi a mano, frazioni esatte, JS = Python), FAQPage visibile, nessun affiliato.
Monetizzazione (30/10/2026, controllo comune di studio-business/strumenti/monetizzazione.py): i link di affiliazione sono
ammessi solo verso i domini di monetizzazione.json, con rel="sponsored noopener" e la riga di trasparenza nella pagina;
domini bloccati e link sponsorizzati verso altri domini sono errori; script AdSense, ads.txt e sezione privacy ci sono
solo se AdSense è acceso per questo sito in monetizzazione.json.
Esce con codice 1 se qualcosa non va.
"""
import hashlib
import json
import random
import re
import subprocess
import sys
import tempfile
from datetime import date
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import genera as G  # noqa: E402

SITO = G.SITO
D = {d["slug"]: d for d in G.DEST}
PARIGI = G.fr_regola("75056")

# (descrizione, regola, categoria, check-in, notti, paganti, esenti, stanze, prezzo, totale atteso calcolato a mano)
ESEMPI = [
    ("Barcelona 5 stars, 9 nights, 2 adults + 1 child of 16: 7 taxable nights × (€7 + €5) × 2", D["barcelona"], "eb1", "2026-10-15", 9, 2, 1, 1, 0, 168.00),
    ("Mallorca hotel 4* sup, 28 Oct, 10 nights, 2 adults + 1 child: 4×€8 + 4×€2 (low season -75%) + 2×€1 (day 9+, -50%)", D["mallorca"], "h4", "2026-10-28", 10, 2, 1, 1, 0, 42.00),
    ("Santorini 4* hotel, 1 room, 30 Oct, 4 nights: 2×€10 (Apr-Oct) + 2×€3 (Nov-Mar)", D["santorini"], "h4", "2026-10-30", 4, 2, 0, 1, 0, 26.00),
    ("Amsterdam, €200 per night excl. VAT, 3 nights: 12.5% × 200 × 3", D["amsterdam"], "all", "2026-11-02", 3, 2, 0, 1, 200, 75.00),
    ("Vienna, €100 per night, 29 Jun, 4 nights: 2×(3.2% × 89% × 100) + 2×(5% × 100) = 5.696 + 10", D["vienna"], "all", "2026-06-29", 4, 2, 0, 1, 100, 15.696),
    ("Edinburgh, £120 per night, 7 nights: 5 taxable nights × 5% × 120", D["edinburgh"], "all", "2026-08-10", 7, 2, 0, 1, 120, 30.00),
    ("Kyoto, ¥30,000 room for 2, 3 nights: ¥15,000 per person → ¥400 × 2 × 3", D["kyoto"], "all", "2026-11-10", 3, 2, 0, 1, 30000, 2400),
    ("Tokyo, ¥25,000 room for 2, 2 nights: ¥12,500 per person → ¥100 × 2 × 2", D["tokyo"], "all", "2026-11-01", 2, 2, 0, 1, 25000, 400),
    ("Hakuba, ¥45,000 room for 2, 3 nights: ¥22,500 per person → (¥300 village + ¥100 Nagano) × 2 × 3", D["hakuba"], "all", "2026-12-20", 3, 2, 0, 1, 45000, 2400),
    ("Paris unclassified, €150 per night, 2 adults + 2 children, 2 nights: 5% × 37.50 = 1.88 → ×3.25 = 6.11 × 2 adults × 2 (DGCL fiche 6, case 1)", PARIGI, "nc", "2026-11-05", 2, 2, 2, 1, 150, 24.44),
    ("Paris unclassified, €800 per night, 4 adults, 1 night: 5% × 200 = 10 → cap €4.90 → ×3.25 = 15.93 × 4", PARIGI, "nc", "2026-11-05", 1, 4, 0, 1, 800, 63.72),
    ("Paris 4-star hotel, 2 adults, 3 nights: €8.45 (2.60 + 225%) × 2 × 3", PARIGI, "h4", "2026-11-05", 3, 2, 0, 1, 0, 50.70),
    ("Prague, 2 adults + 1 child, 4 nights: 50 CZK × 2 × 4", D["prague"], "all", "2026-11-05", 4, 2, 1, 1, 0, 400),
    ("Prague, 61 nights: outside the fee (stays up to 60 days only)", D["prague"], "all", "2026-11-05", 61, 2, 0, 1, 0, 0),
    ("Prague, 60 nights = 61 calendar days: outside the fee", D["prague"], "all", "2026-11-05", 60, 2, 0, 1, 0, 0),
    ("Prague, 59 nights = 60 calendar days: 50 × 2 × 59", D["prague"], "all", "2026-11-05", 59, 2, 0, 1, 0, 5900),
    ("Milan short-term rental, 20 nights, 2 adults (no 15th-day exemption): €9.50 × 2 × 20", D["milan"], "str", "2026-05-01", 20, 2, 0, 1, 0, 380.00),
    ("Milan non-profit case per ferie, 20 nights, 2 adults: €7 × 2 × 14", D["milan"], "cpfnp", "2026-05-01", 20, 2, 0, 1, 0, 196.00),
    ("Milan case per ferie (other operator), 20 nights, 2 adults: €7 × 2 × 20", D["milan"], "cpf", "2026-05-01", 20, 2, 0, 1, 0, 280.00),
    ("Vienna, €100, 1 Jul - 1 Oct 2026 (92 nights = exactly 3 months): 5% × 100 × 92", D["vienna"], "all", "2026-07-01", 92, 2, 0, 1, 100, 460.00),
    ("Vienna, €100, 93 nights (more than 3 months): exempt", D["vienna"], "all", "2026-07-01", 93, 2, 0, 1, 100, 0),
    ("Vienna, €100, 100 nights: exempt", D["vienna"], "all", "2026-07-01", 100, 2, 0, 1, 100, 0),
    ("Castelldefels 5 stars, 15 Oct 2026, 3 nights, 2 adults: (€4.50 + €4.00 surcharge) × 2 × 3", D["catalonia"], "et1", "2026-10-15", 3, 2, 0, 1, 0, 51.00, "castelldefels"),
    ("Esplugues 5 stars (no surcharge listed for 5 stars): €4.50 × 2 × 3", D["catalonia"], "et1", "2026-10-15", 3, 2, 0, 1, 0, 27.00, "esplugues"),
    ("Edinburgh £100 from 22 Jul 2026, 6 nights: 2 nights before the levy, nights 3-5 taxed, night 6 over the 5-night limit", D["edinburgh"], "all", "2026-07-22", 6, 2, 0, 1, 100, 15.00),
    ("Rome 5 stars, 2 adults + child of 8, 12 nights: €10 × 2 × 10 (max)", D["rome"], "h5", "2026-11-05", 12, 2, 1, 1, 0, 200.00),
    ("Milan 5 stars, 30 Mar, 4 nights, 2 adults: 2×(€10×2) + 2×(€12×2)", D["milan"], "h5", "2026-03-30", 4, 2, 0, 1, 0, 88.00),
    ("Turkey, TRY 5,000 per night excl. VAT, 29 Apr, 4 nights: 2×2% + 2×1%", D["turkey"], "all", "2026-04-29", 4, 2, 0, 1, 5000, 300.00),
    ("Iceland hotel, 2 rooms, 3 nights: ISK 800 × 2 × 3", D["iceland"], "hotel", "2026-11-05", 3, 4, 0, 2, 0, 4800),
    ("Bali, 3 travellers: IDR 150,000 × 3", D["bali"], "all", "2026-11-05", 1, 3, 0, 1, 0, 450000),
    ("Berlin, €150 per night excl. VAT, 2 nights: 7.5% × 150 × 2", D["berlin"], "all", "2026-11-05", 2, 2, 0, 1, 150, 22.50),
    ("Florence 4 stars, 2 adults, 10 nights: €7 × 2 × 7 (max)", D["florence"], "h4", "2026-11-05", 10, 2, 0, 1, 0, 98.00),
    ("Sapporo, ¥24,000 room for 2, 3 nights: ¥12,000 per person → ¥300 × 2 × 3", D["sapporo"], "all", "2026-11-05", 3, 2, 0, 1, 24000, 1800),
    ("Kutchan, ¥60,000 per night, 3 nights: 3% × 60,000 × 3", D["kutchan-niseko"], "all", "2026-12-20", 3, 2, 0, 1, 60000, 5400),
    ("Catalonia 5 stars, 30 Mar 2027, 3 nights, 2 adults: 2×(€4.50×2) + 1×(€6×2)", D["catalonia"], "et1", "2027-03-30", 3, 2, 0, 1, 0, 30.00),
    # 26/10/2026: Tokyo dal 1/4/2027 (3% da ¥13.000 a persona), Cardiff, Malta, Porto, Tunisia
    ("Tokyo from 1 Apr 2027, ¥30,000 room for 2, 2 nights: ¥15,000 per person → 3% = ¥450 × 2 × 2", D["tokyo"], "all", "2027-04-01", 2, 2, 0, 1, 30000, 1800),
    ("Tokyo 31 Mar + 1 Apr 2027, ¥30,000 room for 2: ¥200 × 2 + ¥450 × 2", D["tokyo"], "all", "2027-03-31", 2, 2, 0, 1, 30000, 1300),
    ("Tokyo from 1 Apr 2027, ¥24,000 room for 2: ¥12,000 per person, under ¥13,000 → no tax", D["tokyo"], "all", "2027-04-10", 3, 2, 0, 1, 24000, 0),
    ("Cardiff hotel, 3 guests (2 adults + baby, all ages pay), 3 nights from 3 May 2027: £1.30 × 3 × 3", D["cardiff"], "higher", "2027-05-03", 3, 3, 0, 1, 0, 11.70),
    ("Cardiff hostel dormitory, 2 adults, 2 nights: 75p × 2 × 2", D["cardiff"], "lower", "2027-05-03", 2, 2, 0, 1, 0, 3.00),
    ("Cardiff hotel, 2 guests, 3 nights from 30 Mar 2027: 2 nights before the levy, 1 night × £1.30 × 2", D["cardiff"], "higher", "2027-03-30", 3, 2, 0, 1, 0, 2.60),
    ("Cardiff, one booking of 32 nights: not charged", D["cardiff"], "higher", "2027-05-01", 32, 2, 0, 1, 0, 0),
    ("Cardiff, 31 nights: £1.30 × 2 × 31", D["cardiff"], "higher", "2027-05-01", 31, 2, 0, 1, 0, 80.60),
    ("Malta, 2 adults + 1 child, 20 nights: 15 taxable nights × €1.50 × 2 (max €22.50 each)", D["malta"], "all", "2026-11-01", 20, 2, 1, 1, 0, 45.00),
    ("Porto, 2 adults + 1 child, 10 nights: 7 nights × €3 × 2", D["porto"], "all", "2026-11-01", 10, 2, 1, 1, 0, 42.00),
    ("Tunisia 4-5 stars, foreign guests, 2 people, 12 nights: 10 nights × TND 12 × 2", D["tunisia"], "h45f", "2026-11-01", 12, 2, 0, 1, 0, 240.00),
    ("Tunisia 3 stars, Tunisian nationals, 2 people, 3 nights: TND 2 × 2 × 3", D["tunisia"], "h3t", "2026-11-01", 3, 2, 0, 1, 0, 12.00),
    # 30/10/2026: Visitax del Quintana Roo = 2,50 UMA (INEGI: 113,14 dal 1/2/2025, 117,31 dal 1/2/2026), a persona, una volta all'ingresso
    # importo pagato = arrotondato al peso (Código Fiscal QRoo art. 18; il portale chiede MXN 293 a persona, 30/10/2026)
    ("Cancún, 3 foreign visitors arriving 5 Nov 2026: 2.50 × 117.31 = 293.275 → MXN 293 × 3", D["cancun"], "all", "2026-11-05", 7, 3, 0, 1, 0, 879.00),
    ("Tulum, 2 visitors arriving 31 Jan 2026 (UMA 2025): 2.50 × 113.14 = 282.85 → MXN 283 × 2", D["tulum"], "all", "2026-01-31", 5, 2, 0, 1, 0, 566.00),
    ("Cozumel, 4 visitors (children pay too) arriving 1 Feb 2026: MXN 293 × 4", D["cozumel"], "all", "2026-02-01", 3, 4, 0, 1, 0, 1172.00),
]


def controlla_esempi():
    errori = []
    for e in ESEMPI:
        descr, R, cat, ci, n, p, es, st, pr, atteso = e[:10]
        o = G.calcola(R, cat, ci, n, p, es, st, pr, e[10] if len(e) > 10 else "")
        if abs(o["totale"] - atteso) > 0.005:
            errori.append(f"ESEMPIO SBAGLIATO: {descr}: atteso {atteso}, calcolato {o['totale']}")
    return errori


def casi_casuali(n=2000, seme=7):
    rnd = random.Random(seme)
    regole = list(G.DEST) + [PARIGI, G.fr_regola("74056"), G.fr_regola("06029")]
    casi = []
    for _ in range(n):
        R = rnd.choice(regole)
        cat = rnd.choice(R["categorie"])["id"]
        ci = f"{rnd.choice([2026, 2027])}-{rnd.randint(1, 12):02d}-{rnd.randint(1, 28):02d}"
        zona = rnd.choice([""] + [z["id"] for z in R.get("zone", [])])
        casi.append([R, cat, ci, rnd.choice([rnd.randint(1, 70), rnd.randint(55, 100)]), rnd.randint(0, 6), rnd.randint(0, 3), rnd.randint(1, 3),
                     round(rnd.uniform(0, 120000), 2), zona])
    return casi


def controlla_js(casi):
    if subprocess.run(["which", "node"], capture_output=True).returncode != 0:
        return ["node non trovato: confronto JS saltato"]
    regole = []
    idx = {}
    righe = []
    for c in casi:
        key = id(c[0])
        if key not in idx:
            idx[key] = len(regole)
            regole.append({k: c[0][k] for k in G.CAMPI_MOTORE if k in c[0]})
        righe.append([idx[key]] + c[1:])
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "t.js"
        f.write_text(G.MOTORE_JS + "\nvar R=" + json.dumps(regole, ensure_ascii=False) + ";var C=" + json.dumps(righe) +
                     ";console.log(JSON.stringify(C.map(function(c){var o=calcola(R[c[0]],c[1],c[2],c[3],c[4],c[5],c[6],c[7],c[8]);"
                     "return [o.totale,o.righe.map(function(g){return g[0];}),o.escluse,o.sconosciute,o.fuori,o.prima,o.note];})));", encoding="utf-8")
        out = subprocess.run(["node", str(f)], capture_output=True, text=True)
    if out.returncode != 0:
        return ["errore node: " + out.stderr[:500]]
    js = json.loads(out.stdout)
    errori = []
    for c, r in zip(casi, js):
        o = G.calcola(*c)
        py = [o["totale"], [g[0] for g in o["righe"]], o["escluse"], o["sconosciute"], o["fuori"], o["prima"], o["note"]]
        if abs(py[0] - r[0]) > 1e-6 or py[1:] != r[1:]:
            errori.append(f"JS diverso da Python: {c[0]['name']} {c[1:]}: py={py} js={r}")
            if len(errori) > 5:
                break
    return errori


class Link(HTMLParser):
    def __init__(self):
        super().__init__()
        self.link = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for k in ("href", "src"):
            if k in a and a[k]:
                self.link.append(a[k])


def controlla_link():
    errori, n = [], 0
    for f in SITO.rglob("*.html"):
        p = Link()
        p.feed(f.read_text(encoding="utf-8"))
        for u in p.link:
            if u.startswith(("http://", "https://", "mailto:", "data:", "#")) or u.startswith("javascript"):
                continue
            n += 1
            u = u.split("#")[0].split("?")[0]
            if not u:
                continue
            dest = (SITO / u.lstrip("/")) if u.startswith("/") else (f.parent / u)
            dest = dest.resolve()
            if dest.is_dir():
                dest = dest / "index.html"
            if not dest.exists():
                errori.append(f"link rotto in {f.relative_to(SITO)}: {u}")
    # link usati dal JS: data-url della ricerca francese
    for f in SITO.rglob("*.html"):
        for u in re.findall(r'data-url="([^"]+)"', f.read_text(encoding="utf-8")):
            if not (f.parent / u).resolve().exists():
                errori.append(f"data-url rotto in {f.relative_to(SITO)}: {u}")
    for loc in re.findall(r"<loc>([^<]+)</loc>", (SITO / "sitemap.xml").read_text()):
        rel = loc.replace(G.URL_SITO + "/", "")
        dest = SITO / rel
        if rel == "" or rel.endswith("/"):
            dest = dest / "index.html"
        if not dest.exists():
            errori.append(f"sitemap: pagina mancante {loc}")
    return errori, n


def controlla_fonti():
    errori = []
    pagine = [SITO / d["slug"] / "index.html" for d in G.DEST] + [p for p in (SITO / "france").glob("*/index.html")]
    for p in pagine:
        t = p.read_text(encoding="utf-8")
        if not re.search(r'<p class="fonte">Official source: <a href="https?://[^"]+"', t):
            errori.append(f"manca la fonte ufficiale: {p.relative_to(SITO)}")
        if not re.search(r"checked on \d{1,2} [A-Z][a-z]+ 20\d\d", t):
            errori.append(f"manca la data del controllo: {p.relative_to(SITO)}")
    return errori, len(pagine)


def controlla_altri_siti():
    """5. Blocco "Other useful tools for your trip" in ogni pagina indicizzabile: gli stessi link di genera.ALTRI_SITI,
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


NUOVE_DEST = ("cardiff", "malta", "porto", "tunisia")  # aggiunte il 26/10/2026


def _sitemap():
    return set(re.findall(r"<loc>([^<]+)</loc>", (SITO / "sitemap.xml").read_text(encoding="utf-8")))


def controlla_pagina_2027():
    """6. Pagina tourist-tax-changes-2027/: esiste, è nella sitemap, è linkata dalla home e dalle pagine dei luoghi interessati;
    ogni voce ha fonte ufficiale (URL, HTTP, data del controllo) stampata in pagina e una data 2027 in ordine; ogni [slug, data]
    di 'verifica' corrisponde a una tariffa, un supplemento o un cambio annunciato che parte davvero in quella data;
    JSON-LD FAQPage con 3-4 domande, le stesse visibili nella pagina; ogni luogo è citato nella risposta in cima."""
    errori = []
    f = SITO / "tourist-tax-changes-2027" / "index.html"
    if not f.exists():
        return ["pagina 2027 mancante"]
    t = f.read_text(encoding="utf-8")
    if G.URL_SITO + "/tourist-tax-changes-2027/" not in _sitemap():
        errori.append("pagina 2027 non nella sitemap")
    if 'href="tourist-tax-changes-2027/"' not in (SITO / "index.html").read_text(encoding="utf-8"):
        errori.append("pagina 2027 non linkata dalla home")
    voci = G.CAMBI["voci"]
    if len(voci) < 3:
        errori.append("pagina 2027: meno di 3 voci")
    date_ = [v["dal"] for v in voci]
    if date_ != sorted(date_) or any(d[:4] != "2027" for d in date_):
        errori.append(f"pagina 2027: date non in ordine o fuori dal 2027: {date_}")
    risp = re.search(r'<p class="risposta">(.*?)</p>', t, re.S)
    for v in voci:
        fo = v["fonte"]
        if not fo["url"].startswith("https://") or not fo.get("http") or not re.match(r"\d{4}-\d\d-\d\d$", fo.get("controllato_il", "")):
            errori.append(f"pagina 2027: fonte incompleta per {v['luogo']}")
        if fo["url"].replace("&", "&amp;") not in t or f"checked on {G.data_lunga(fo['controllato_il'])}" not in t:
            errori.append(f"pagina 2027: fonte o data non stampate per {v['luogo']}")
        if not risp or v["luogo"].split(" (")[0] not in risp.group(1):
            errori.append(f"pagina 2027: {v['luogo']} non citato nella risposta in cima")
        for slug, giorno in v["verifica"]:
            if slug not in D:
                errori.append(f"pagina 2027: destinazione inesistente {slug}")
                continue
            R = D[slug]
            if not any(x.get("dal") == giorno for x in R["tariffe"] + R.get("supplementi", []) + R.get("cambi_annunciati", [])):
                errori.append(f"pagina 2027: {slug} non ha nei dati una tariffa che parte il {giorno}")
        for slug in {v["slug"]} | {s for s, _ in v["verifica"]}:
            if slug and 'href="../tourist-tax-changes-2027/"' not in (SITO / slug / "index.html").read_text(encoding="utf-8"):
                errori.append(f"pagina 2027 non linkata dalla pagina di {slug}")
    ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)]
    faq = [x for x in ld if x.get("@type") == "FAQPage"]
    if len(faq) != 1:
        errori.append("pagina 2027: JSON-LD FAQPage mancante o doppio")
    else:
        qq = faq[0]["mainEntity"]
        if not 3 <= len(qq) <= 4:
            errori.append(f"pagina 2027: FAQ con {len(qq)} domande (attese 3-4)")
        for q in qq:
            if q.get("@type") != "Question" or not q.get("acceptedAnswer", {}).get("text"):
                errori.append(f"pagina 2027: domanda FAQ incompleta: {q.get('name')}")
            elif G.escape(q["name"]) not in t or G.escape(q["acceptedAnswer"]["text"]) not in t:
                errori.append(f"pagina 2027: domanda o risposta FAQ non visibile nella pagina: {q['name']}")
    return errori


def controlla_nuove_destinazioni():
    """7. Destinazioni aggiunte il 26/10/2026: nei dati con almeno una fonte ufficiale leggibile (HTTP 200) e data del controllo,
    pagina con titolo, H1 e risposta diretta, tutte le fonti linkate nella pagina, nella sitemap, nella pagina del paese
    e (se europee) nella tabella Europa."""
    errori = []
    sm = _sitemap()
    europa = (SITO / "tourist-taxes-europe-2026" / "index.html").read_text(encoding="utf-8")
    for slug in NUOVE_DEST:
        if slug not in D:
            errori.append(f"nuova destinazione mancante nei dati: {slug}")
            continue
        R = D[slug]
        if not R["fonti"] or any(f["http"] != 200 or not f.get("controllato_il") for f in R["fonti"]):
            errori.append(f"{slug}: fonte non leggibile o senza data del controllo")
        f = SITO / slug / "index.html"
        if not f.exists():
            errori.append(f"{slug}: pagina mancante")
            continue
        t = f.read_text(encoding="utf-8")
        titolo = re.search(r"<title>(.*?)</title>", t).group(1)
        if "tourist tax" not in titolo or not re.search(r"\d", titolo):
            errori.append(f"{slug}: titolo senza cifra o senza 'tourist tax': {titolo}")
        if "<h1" not in t or '<p class="risposta">' not in t:
            errori.append(f"{slug}: manca H1 o risposta diretta")
        for fo in R["fonti"]:
            if G.escape(fo["url"]) not in t:
                errori.append(f"{slug}: fonte non linkata nella pagina: {fo['url']}")
        if f"{G.URL_SITO}/{slug}/" not in sm:
            errori.append(f"{slug}: non nella sitemap")
        paese = (SITO / "country" / R["country_slug"] / "index.html")
        if not paese.exists() or f'href="../../{slug}/"' not in paese.read_text(encoding="utf-8"):
            errori.append(f"{slug}: non elencata nella pagina del paese")
        if R["country_slug"] in G.EUROPA and f'href="../{slug}/"' not in europa:
            errori.append(f"{slug}: non nella tabella Europa")
    return errori


def controlla_titoli():
    """8. Ogni pagina di destinazione: titolo con 'tourist tax', l'anno e una cifra; descrizione e risposta diretta presenti."""
    errori = []
    for d in G.DEST:
        t = (SITO / d["slug"] / "index.html").read_text(encoding="utf-8")
        titolo = re.search(r"<title>(.*?)</title>", t).group(1)
        descr = re.search(r'<meta name="description" content="([^"]*)"', t).group(1)
        if "tourist tax" not in titolo or not re.search(r"20(26|27)", titolo) or not re.search(r"\d[%,.]?\d*\b", titolo.split(":", 1)[-1]):
            errori.append(f"titolo senza anno o cifra: {d['slug']}: {titolo}")
        if len(descr) < 60 or '<p class="risposta">' not in t:
            errori.append(f"descrizione o risposta diretta mancante: {d['slug']}")
    return errori


MX_SLUG = ("mexico", "cancun", "tulum", "playa-del-carmen", "cozumel")
MX_AID = "https://www.discovercars.com/?a_aid=Massimilianocori"


def controlla_messico():
    """9. Sezione Messico."""
    errori = []
    sm = _sitemap()
    molt = G.MX["visitax"]["moltiplicatore_uma"]
    if molt != 2.5:
        errori.append(f"Messico: moltiplicatore UMA {molt} diverso da 2,50 (art. 51-Octies)")
    # importi ricalcolati qui, indipendentemente da genera.tariffe_uma
    attese = []
    vv = sorted(G.UMA["valori"], key=lambda v: v["dal"])
    for i, v in enumerate(vv):
        if not re.match(r"https://www\.inegi\.org\.mx/.+\.pdf$", v["fonte"]["url"]) or v["fonte"]["http"] != 200:
            errori.append(f"Messico: fonte UMA {v['anno']} non INEGI o non letta")
        if v["dal"] != f"{v['anno']}-02-01":
            errori.append(f"Messico: UMA {v['anno']} non in vigore dal 1° febbraio")
        cent = round(v["diario"] * 250)  # 2,50 × UMA in centesimi (esatto a mezzo centesimo: arrotondo solo per il confronto)
        esatto = v["diario"] * 2.5
        importo = float(cent // 100 + (1 if cent % 100 > 50 else 0))  # al peso: 1-50 centavos giù, 51-99 su (CF QRoo art. 18)
        attese.append((v["dal"], importo, v["diario"], esatto))
    for slug in ("cancun", "tulum", "playa-del-carmen", "cozumel"):
        R = D.get(slug)
        if not R:
            errori.append(f"Messico: destinazione mancante {slug}")
            continue
        tt = [(t["dal"], t["valore"], t["uma"]) for t in R["tariffe"]]
        if [(a, round(b, 2)) for a, b, _ in tt] != [(a, round(b, 2)) for a, b, _, _ in attese]:
            errori.append(f"Messico: tariffe di {slug} diverse dalla formula 2,50 × UMA: {tt} vs {attese}")
    oggi = G.OGGI.isoformat()
    ora = next((x for x in reversed(attese) if x[0] <= oggi), attese[-1])
    imp = G.soldi(ora[1], "MXN")
    formula = f"2.50 × {G.soldi(ora[2], 'MXN')} = MXN {('%.4f' % ora[3]).rstrip('0').rstrip('.')}, rounded to {imp}"
    pp = G.MX["visitax"]["portale"].get("prezzo_unitario")
    if pp and pp["anno"] == int(ora[0][:4]) and pp["valore"] != ora[1]:
        errori.append(f"Messico: il portale ufficiale chiedeva {pp['valore']} nel {pp['anno']}, la formula dà {ora[1]}")
    voce = next((v for v in G.CAMBI["voci"] if v.get("uma")), None)
    if not voce or voce["dal"] != f"{voce['uma']['anno']}-02-01" or voce["slug"] != "mexico":
        errori.append("Messico: voce del Visitax nella pagina 2027 mancante o con data diversa dal 1° febbraio dell'anno della prossima UMA")
    for slug in MX_SLUG:
        f = SITO / slug / "index.html"
        if not f.exists():
            errori.append(f"Messico: pagina mancante {slug}/")
            continue
        if f"{G.URL_SITO}/{slug}/" not in sm:
            errori.append(f"Messico: {slug}/ non nella sitemap")
        t = f.read_text(encoding="utf-8")
        vis = G.MON.testo_visibile(t)
        titolo = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(titolo) > 70 or "tourist tax" not in titolo or not re.search(r"20(26|27)", titolo) or "MXN" not in titolo:
            errori.append(f"Messico: titolo oltre 70 caratteri o senza anno/importo: {slug}: {titolo} ({len(titolo)})")
        if imp not in titolo and not voce_futura_nel_titolo(titolo, attese, oggi):
            errori.append(f"Messico: il titolo di {slug} non ha l'importo in vigore {imp}")
        r = re.search(r'<p class="risposta">(.*?)</p>', t, re.S)
        prima = r.group(1).split(". ")[0] if r else ""
        if not r or imp not in prima or "article 51-Octies" not in prima or "INEGI" not in prima or not re.search(r"checked on \d{1,2} [A-Z][a-z]+ 20\d\d", prima):
            errori.append(f"Messico: la prima frase di {slug} non ha importo, fonte e data del controllo")
        if formula not in vis:
            errori.append(f"Messico: formula '{formula}' non mostrata in {slug}")
        if f"The official fee is {imp} per person; third-party sites may charge a service fee." not in vis:
            errori.append(f"Messico: avviso sul sito ufficiale mancante in {slug}")
        for u in re.findall(r'href="([^"]+)"', t):
            if "visitax" in u.lower() and not re.match(r"https://(www\.)?visitax\.gob\.mx/", u):
                errori.append(f"Messico: link a un sito Visitax non ufficiale in {slug}: {u}")
        if 'href="https://visitax.gob.mx/sitio/"' not in t:
            errori.append(f"Messico: manca il link al sito ufficiale Visitax in {slug}")
        ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)]
        faq = [x for x in ld if x.get("@type") == "FAQPage"]
        if len(faq) != 1 or len(faq[0]["mainEntity"]) < 3:
            errori.append(f"Messico: FAQPage mancante o con meno di 3 domande in {slug}")
        else:
            for q in faq[0]["mainEntity"]:
                if G.escape(q["name"]) not in t or G.escape(q["acceptedAnswer"]["text"]) not in t:
                    errori.append(f"Messico: domanda FAQ non visibile in {slug}: {q['name']}")
        dnr = G.soldi(G.MX["federali"]["dnr"]["importo"], "MXN")
        if dnr not in vis:
            errori.append(f"Messico: importo DNR {dnr} mancante in {slug}")
        # affiliazione: solo DiscoverCars con il nostro a_aid, rel sponsored noopener, dopo FAQ e fonti ufficiali
        aff = G.MON.link_affiliati(t)
        url_on = (G.AFFILIATI.get("_discovercars_messico") or {}).get("url", "")
        for href, host, rel in aff:
            if href != MX_AID or not {"sponsored", "noopener"} <= rel:
                errori.append(f"Messico: link di affiliazione non ammesso in {slug}: {href} {rel}")
        if url_on and len(aff) != 1:
            errori.append(f"Messico: atteso 1 link DiscoverCars in {slug}, trovati {len(aff)}")
        if aff:
            pos = t.find(G.escape(MX_AID))
            if pos < t.find("<h2>Official sources</h2>") or pos < t.find("<h2>Questions</h2>") or pos < t.find("mx-uff"):
                errori.append(f"Messico: riquadro DiscoverCars prima delle informazioni ufficiali in {slug}")
            if G.MON.RIGA_EN not in vis:
                errori.append(f"Messico: riga di trasparenza mancante in {slug}")
    # nessun link DiscoverCars fuori dalla sezione Messico
    for f in SITO.rglob("*.html"):
        rel = f.relative_to(SITO).parts[0]
        if rel not in MX_SLUG and "discovercars.com" in f.read_text(encoding="utf-8"):
            errori.append(f"Messico: link DiscoverCars fuori dalla sezione Messico: {f.relative_to(SITO)}")
    return errori


# 10. Giappone: rimborso dell'imposta sui consumi per i turisti dal 1/11/2026 (pagina /japan-tax-free-refund/, 30/10/2026).
# (beni al 10 %, alimenti all'8 %, importi con imposta?, rimborso massimo atteso calcolato a mano)
ESEMPI_JP = [
    (33000, 0, True, 3000),        # 33.000 con imposta = 30.000 + 3.000
    (22000, 10800, True, 2800),    # 20.000 + 2.000; 10.000 + 800
    (5400, 0, True, 0),            # 4.909 al netto: sotto la soglia di 5.000
    (5500, 0, True, 500),          # esattamente 5.000 al netto: rimborso
    (100000, 0, False, 10000),
    (3000, 2000, False, 460),      # 5.000 al netto in tutto: 300 + 160
    (0, 5399, True, 0),            # 4.999,07 al netto
    (0, 5400, True, 400),          # 5.000 al netto, 8 %
    (12345, 0, True, 1122),        # 12.345 / 11 = 1.122,27 → 1.122 (per difetto)
    (2750, 2700, True, 450),       # 2.500 + 2.500 al netto = soglia; 250 + 200
    (4999, 0, False, 0),
    (1000000, 50000, True, 94612), # 90.909 + 3.703
]


def jp_atteso(a10, a8, incl, soglia):
    """Calcolo indipendente da genera.jp_rimborso, in frazioni esatte."""
    from fractions import Fraction as F
    a10, a8 = F(int(round(a10))), F(int(round(a8)))
    if incl:
        n10, n8 = a10 * 100 / 110, a8 * 100 / 108
    else:
        n10, n8 = a10, a8
    t10, t8 = n10 * F(10, 100), n8 * F(8, 100)
    if n10 + n8 < soglia:
        return 0
    return int(t10) + int(t8)  # per difetto allo yen (importi non negativi)


def controlla_giappone():
    """10. Pagina /japan-tax-free-refund/: dati coerenti con le fonti lette (soglia 5.000 yen al netto, 10 % e 8 %, 90 giorni,
    tassa di partenza 3.000 yen dal 1/7/2026), ogni fonte ufficiale con HTTP 200 e data, linkata nella pagina; pagina in sitemap e
    linkata da home, pagina Giappone e pagine dei luoghi giapponesi; titolo ≤ 70 caratteri con l'anno; prima frase con risposta,
    fonti e data; calcolo ricontrollato (esempi a mano, calcolo indipendente in frazioni, motore JS uguale al Python su casi casuali);
    FAQPage uguale al testo visibile; nessun link di affiliazione."""
    from datetime import date, timedelta
    errori = []
    J = G.JP
    if J["soglia_yen"] != 5000 or J["aliquote"] != {"standard": 10, "ridotta": 8} or J["giorni_dogana"] != 90:
        errori.append("Giappone: soglia, aliquote o giorni diversi da quelli letti nelle fonti (5.000 yen, 10/8 %, 90 giorni)")
    if J["in_vigore_dal"] != "2026-11-01":
        errori.append("Giappone: data di inizio diversa dal 1/11/2026")
    sc = J["esempio_scadenza"]
    if date.fromisoformat(sc["acquisto"]) + timedelta(days=J["giorni_dogana"]) != date.fromisoformat(sc["ultimo_giorno"]):
        errori.append("Giappone: l'esempio della scadenza non è acquisto + 90 giorni (NTA: 1/11 → 30/1)")
    tp = J["tassa_partenza"]
    if (tp["importo"], tp["prima"], tp["dal"]) != (3000, 1000, "2026-07-01"):
        errori.append("Giappone: tassa di partenza diversa dalla fonte NTA (3.000 yen dal 1/7/2026, prima 1.000)")
    for k, fo in J["fonti"].items():
        if fo.get("http") != 200 or not re.match(r"\d{4}-\d\d-\d\d$", fo.get("controllato_il", "")) or not fo["url"].startswith("https://"):
            errori.append(f"Giappone: fonte {k} non letta (HTTP 200) o senza data")
        if not re.match(r"https://www\.(mlit\.go\.jp/kankocho|nta\.go\.jp|customs\.go\.jp)/", fo["url"]):
            errori.append(f"Giappone: fonte {k} non ufficiale (JTA, NTA, Dogane): {fo['url']}")
    # calcolo: esempi a mano, frazioni esatte, Python
    S = J["soglia_yen"]
    for a10, a8, incl, att in ESEMPI_JP:
        py, fr = G.jp_rimborso(a10, a8, incl)["tot"], jp_atteso(a10, a8, incl, S)
        if not py == fr == att:
            errori.append(f"Giappone: esempio {a10}+{a8} incl={incl}: atteso {att}, Python {py}, frazioni {fr}")
    rnd = random.Random(11)
    casi = [(a10, a8, incl) for a10, a8, incl, _ in ESEMPI_JP] + [
        (rnd.choice([0, rnd.randint(0, 9000), rnd.randint(0, 2000000)]), rnd.choice([0, rnd.randint(0, 9000), rnd.randint(0, 300000)]), rnd.random() < 0.6)
        for _ in range(1500)]
    for a10, a8, incl in casi:
        if G.jp_rimborso(a10, a8, incl)["tot"] != jp_atteso(a10, a8, incl, S):
            errori.append(f"Giappone: Python diverso dal calcolo in frazioni: {a10}+{a8} incl={incl}")
            break
    if subprocess.run(["which", "node"], capture_output=True).returncode == 0:
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "jp.js"
            f.write_text(G.JP_JS + f"\nvar C={json.dumps(casi)};console.log(JSON.stringify(C.map(function(c){{return jpRimborso(c[0],c[1],c[2],{S}).tot;}})));",
                         encoding="utf-8")
            out = subprocess.run(["node", str(f)], capture_output=True, text=True)
        if out.returncode != 0:
            errori.append("Giappone: errore node: " + out.stderr[:300])
        else:
            for c, r in zip(casi, json.loads(out.stdout)):
                if r != G.jp_rimborso(*c)["tot"]:
                    errori.append(f"Giappone: JS diverso da Python: {c} js={r}")
                    break
    else:
        errori.append("Giappone: node non trovato, confronto JS saltato")
    # pagina
    f = SITO / "japan-tax-free-refund" / "index.html"
    if not f.exists():
        return errori + ["Giappone: pagina japan-tax-free-refund/ mancante"]
    t = f.read_text(encoding="utf-8")
    vis = G.MON.testo_visibile(t)
    if G.URL_SITO + "/japan-tax-free-refund/" not in _sitemap():
        errori.append("Giappone: pagina non nella sitemap")
    titolo = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
    if len(titolo) > 70 or "2026" not in titolo or "Japan" not in titolo or "tax" not in titolo.lower():
        errori.append(f"Giappone: titolo oltre 70 caratteri o senza anno: {titolo} ({len(titolo)})")
    r = re.search(r'<p class="risposta">(.*?)</p>', t, re.S)
    prima = unescape(r.group(1)).split(". ")[0] if r else ""
    for pezzo in ("1 November 2026", "10%", "8%", "¥5,000", "90 days", "Japan Tourism Agency", "National Tax Agency",
                  f"checked on {G.data_lunga(J['controllato_il'])}"):
        if pezzo not in prima:
            errori.append(f"Giappone: la prima frase non contiene '{pezzo}'")
    for fo in J["fonti"].values():
        if G.escape(fo["url"]) not in t:
            errori.append(f"Giappone: fonte non linkata nella pagina: {fo['url']}")
    if f"checked {G.data_lunga(J['controllato_il'])}" not in vis:
        errori.append("Giappone: data del controllo delle fonti non stampata")
    for pezzo in ("up to ¥3,000 back", "= ¥2,800", "¥3,000 per departure", "data-jp", "jpRimborso"):
        if pezzo not in t and pezzo not in vis:
            errori.append(f"Giappone: manca '{pezzo}' nella pagina (esempi, tassa di partenza o calcolatore)")
    ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)]
    faq = [x for x in ld if x.get("@type") == "FAQPage"]
    if len(faq) != 1 or len(faq[0]["mainEntity"]) < 5:
        errori.append("Giappone: FAQPage mancante o con meno di 5 domande")
    else:
        for q in faq[0]["mainEntity"]:
            if G.escape(q["name"]) not in t or G.escape(q["acceptedAnswer"]["text"]) not in t:
                errori.append(f"Giappone: domanda FAQ non visibile: {q['name']}")
    if G.MON.link_affiliati(t):
        errori.append("Giappone: link di affiliazione nella pagina del rimborso")
    # collegamenti in entrata
    entrate = [("index.html", 'href="japan-tax-free-refund/"'), ("country/japan/index.html", 'href="../../japan-tax-free-refund/"')]
    entrate += [(f"{d['slug']}/index.html", 'href="../japan-tax-free-refund/"') for d in G.DEST if d["country_slug"] == "japan"]
    for pag, link in entrate:
        if link not in (SITO / pag).read_text(encoding="utf-8"):
            errori.append(f"Giappone: {pag} non linka la pagina del rimborso")
    return errori


# 11. Giappone: tasse di soggiorno in tutto il paese (31/10/2026). Esempi calcolati a mano dalle fonti:
# (descrizione, id luogo, check-in, notti, prezzo per notte per tutti, ospiti, bambini esenti per età, totale atteso in yen)
ESEMPI_JT = [
    ("Otaru, ¥30,000 for 2 (¥15,000 each), 3 nights: (¥200 city + ¥100 Hokkaido) × 2 × 3", "otaru", "2026-11-10", 3, 30000, 2, 0, 1800),
    ("Sapporo, ¥120,000 for 2 (¥60,000 each), 2 nights: (¥500 + ¥500) × 2 × 2", "sapporo", "2026-11-10", 2, 120000, 2, 0, 4000),
    ("Niseko, ¥60,000 for 2, from 30 Oct 2026, 3 nights: 2 × (¥500 town + ¥200 Hokkaido) × 2 + 3% × ¥30,000 × 2 from 1 Nov", "niseko", "2026-10-30", 3, 60000, 2, 0, 4600),
    ("Kutchan, ¥50,000 for 2, 2 nights: 3% × ¥25,000 × 2 × 2 (Hokkaido tax included)", "kutchan", "2026-12-01", 2, 50000, 2, 0, 3000),
    ("Fukuoka City, ¥50,000 for 2 (¥25,000 each), 1 night: (¥450 city + ¥50 prefecture) × 2", "fukuoka", "2026-11-01", 1, 50000, 2, 0, 1000),
    ("Kitakyushu, ¥8,000 for 1, 1 night: ¥150 + ¥50", "kitakyushu", "2026-11-01", 1, 8000, 1, 0, 200),
    ("Sendai, ¥10,000 for 2 (¥5,000 each, below ¥6,000), 1 night: no tax", "sendai", "2026-11-01", 1, 10000, 2, 0, 0),
    ("Sendai, ¥14,000 for 2 (¥7,000 each), 1 night: (¥200 + ¥100 Miyagi) × 2", "sendai", "2026-11-01", 1, 14000, 2, 0, 600),
    ("Matsumoto, ¥20,000 for 2, 1 night in 2026: (¥100 + ¥100 Nagano) × 2", "matsumoto", "2026-11-01", 1, 20000, 2, 0, 400),
    ("Matsumoto, ¥20,000 for 2, 1 night from 1 Jun 2029: (¥150 + ¥150) × 2", "matsumoto", "2029-06-01", 1, 20000, 2, 0, 600),
    ("Karuizawa, ¥250,000 for 2 (¥125,000 each), 1 night: (¥600 + ¥100) × 2", "karuizawa", "2026-11-01", 1, 250000, 2, 0, 1400),
    ("Nozawa Onsen, ¥40,000 for 2 (¥20,000 each), 2 nights: (3.5% × 20,000 = ¥700 + ¥100 Nagano) × 2 × 2", "nozawa-onsen", "2026-12-20", 2, 40000, 2, 0, 3200),
    ("Okinawa, ¥17,000 for 2 (¥8,500 each → base ¥8,000), 1 night: 2% × 8,000 = ¥160 × 2 (Okinawa's own example)", "okinawa", "2027-02-01", 1, 17000, 2, 0, 320),
    ("Ishigaki, same stay: (1.2% + 0.8%) × 8,000 = ¥96 + ¥64 per person × 2", "ishigaki", "2027-02-01", 1, 17000, 2, 0, 320),
    ("Okinawa, ¥300,000 for 1: base capped at ¥100,000 → ¥2,000", "okinawa", "2027-02-01", 1, 300000, 1, 0, 2000),
    ("Okinawa, night of 31 Jan 2027: not yet in force", "okinawa", "2027-01-31", 1, 17000, 2, 0, 0),
    ("Atami, ¥20,000 for 3 with 1 child under 12, 1 night: ¥200 × 2", "atami", "2026-11-01", 1, 20000, 3, 1, 400),
    ("Toyako, ¥30,000 for 2 with 1 child (¥15,000 each), 1 night: town ¥200 × 1 + Hokkaido ¥100 × 2", "toyako", "2026-11-01", 1, 30000, 2, 1, 400),
    ("Tomakomai, ¥20,000 for 2, 31 Mar + 1 Apr 2027: Hokkaido ¥100 × 2, then 3% × ¥10,000 × 2", "tomakomai", "2027-03-31", 2, 20000, 2, 0, 800),
    ("Nagasaki, ¥16,000 for 2 (¥8,000 each), 31 Mar + 1 Apr 2027: ¥100 × 2, then ¥300 × 2", "nagasaki", "2027-03-31", 2, 16000, 2, 0, 800),
    ("Tokyo, ¥40,000 for 2 (¥20,000 each), 1 night from 1 Apr 2027: 3% × 20,000 × 2", "tokyo", "2027-04-01", 1, 40000, 2, 0, 1200),
    ("Kyoto, ¥30,000 for 2, 1 night: ¥400 × 2", "kyoto", "2026-11-01", 1, 30000, 2, 0, 800),
    ("Hakuba, ¥50,000 for 2 (¥25,000 each), 1 night: (¥300 + ¥100) × 2", "hakuba", "2026-12-01", 1, 50000, 2, 0, 800),
    ("Shintoku, ¥8,000 for 2 (¥4,000 each), 1 night: (¥50 + ¥100) × 2", "shintoku", "2026-11-01", 1, 8000, 2, 0, 300),
    ("Akaigawa, ¥14,000 for 2 (¥7,000 each, below ¥8,000), 1 night: Hokkaido ¥100 × 2 only", "akaigawa", "2026-11-01", 1, 14000, 2, 0, 200),
    ("Wakkanai, ¥30,000 for 2, 1 night from 1 Mar 2027: (¥200 + ¥100) × 2", "wakkanai", "2027-03-01", 1, 30000, 2, 0, 600),
    ("Osaka, ¥32,000 for 2 (¥16,000 each), 1 night: ¥400 × 2", "osaka", "2026-11-01", 1, 32000, 2, 0, 800),
    ("Kanazawa, ¥9,000 for 2 (¥4,500 each), 1 night: no tax below ¥5,000", "kanazawa", "2026-11-01", 1, 9000, 2, 0, 0),
    ("Nasu, ¥240,000 for 2 (¥120,000 each), 1 night: ¥3,000 × 2", "nasu", "2026-11-01", 1, 240000, 2, 0, 6000),
    ("Oita: start date not fixed, no tax counted", "oita", "2027-06-01", 2, 30000, 2, 0, 0),
]
DOMINI_JP = re.compile(r"https://([a-z0-9-]+\.)*(go\.jp|lg\.jp|pref\.okinawa\.jp|city\.sapporo\.jp)/")


def jt_indipendente(J, eid, ci, notti, prezzo, ospiti, bambini):
    """Ricalcolo indipendente dai dati JSON (non usa genera.py): frazioni esatte, componenti del Comune e della Prefettura."""
    from datetime import date, timedelta
    from fractions import Fraction as F
    en = {e["id"]: e for e in J["enti"]}
    e = en[eid]
    pref = {x["pref"]: x for x in J["enti"] if x["livello"] == "prefecture"}
    comp = [(e["regole"], bool(e.get("eta_esente")), False)]
    if e["livello"] == "municipality" and e["pref"] in pref:
        P = pref[e["pref"]]
        comp.append((e.get("pref_regole", P["regole"]), bool(P.get("eta_esente")), True))
    pp = F(prezzo) / ospiti
    tot = F(0)
    for i in range(notti):
        d = (date.fromisoformat(ci) + timedelta(days=i)).isoformat()
        att = []
        for regole, eta, is_pref in comp:
            r = next((r for r in regole if r.get("dal", "0000") <= d <= r.get("al", "9999")), None)
            att.append((r, eta, is_pref))
        incl = any(r and r.get("include_pref") for r, _, _ in att)
        for r, eta, is_pref in att:
            if not r or (is_pref and incl):
                continue
            n = ospiti - (min(bambini, ospiti) if eta else 0)
            if r["tipo"] == "bande":
                q = next((F(v) for lo, hi, v in r["bande"] if lo <= pp and (hi is None or pp < hi)), F(0))
            elif pp < r.get("min", 0):
                q = F(0)
            else:
                base = pp
                if r.get("arrot"):
                    base = F((base // r["arrot"]) * r["arrot"])
                if r.get("base_max"):
                    base = min(base, F(r["base_max"]))
                q = base * F(str(r["valore"])) / 100
                if r.get("cap") is not None:
                    q = min(q, F(r["cap"]))
            tot += q * n
    return tot


def controlla_giappone_tasse():
    """11. Tasse di soggiorno in Giappone: dati = istantanea dell'elenco del Ministero (49 in vigore, 18 approvati, date); fonti ufficiali
    (domini go.jp / lg.jp) con HTTP 200 e data; regole ben formate; esempi a mano; ricalcolo indipendente in frazioni = Python; JS = Python;
    per Tokyo, Kyoto, Sapporo, Kutchan e Hakuba il nuovo motore dà lo stesso totale delle pagine esistenti; pagine (titolo ≤ 70 caratteri,
    prima frase con fonte e data, tutte le fonti linkate, calcolatore, sitemap), pagina riassuntiva e pagina 2027 (tutti i 18 enti con la data),
    FAQPage = testo visibile, link in entrata, nessun link di affiliazione."""
    from datetime import date, timedelta
    errori = []
    J, E = G.JT, G.JT_ELENCO
    enti = J["enti"]
    per_ja = {e["ja"]: e for e in enti}
    if E["url"] != J["fonte_elenco"]["url"] or E["alla_data"] != "2026-11-27":
        errori.append("JP tasse: istantanea dell'elenco MIC non corrisponde alla fonte (URL o data)")
    vig = {e["ja"] for e in enti if e["stato"] == "in_vigore"}
    app = {e["ja"]: e.get("inizio") for e in enti if e["stato"] == "approvato"}
    if vig != set(E["in_vigore"]):
        errori.append(f"JP tasse: enti in vigore diversi dall'elenco MIC: {sorted(vig ^ set(E['in_vigore']))}")
    if set(app) != set(E["approvati"]):
        errori.append(f"JP tasse: enti approvati diversi dall'elenco MIC: {sorted(set(app) ^ set(E['approvati']))}")
    for ja, d in E["approvati"].items():
        if ja in app and (app[ja] or "") != (d if re.match(r"\d{4}-\d\d-\d\d$", d) else ""):
            errori.append(f"JP tasse: {ja} data di partenza {app.get(ja)} diversa dall'elenco ({d})")
    for ja, d in E["partenze"].items():
        if ja in per_ja and per_ja[ja].get("inizio_da") == "mic" and per_ja[ja].get("inizio") != d:
            errori.append(f"JP tasse: {ja} partenza {per_ja[ja].get('inizio')} diversa dall'elenco ({d})")
    c = J["elenco_mic_conteggi"]
    if (len(vig), sum(1 for e in enti if e["stato"] == "in_vigore" and e["livello"] == "prefecture"), len(app)) != (c["in_vigore"], c["prefetture_in_vigore"], c["approvati"]) \
            or (c["in_vigore"], c["approvati"]) != (49, 18):
        errori.append("JP tasse: conteggi diversi da 49 in vigore (7 Prefetture) e 18 approvati")
    for e in enti:
        if not e["fonti"]:
            errori.append(f"JP tasse: {e['id']} senza fonti")
        for fo in e["fonti"]:
            if fo.get("http") != 200 or not re.match(r"\d{4}-\d\d-\d\d$", fo.get("controllato_il", "")) or not DOMINI_JP.match(fo["url"]):
                errori.append(f"JP tasse: {e['id']} fonte non ufficiale, non letta o senza data: {fo['url']}")
        for r in e["regole"] + e.get("pref_regole", []):
            if r["tipo"] == "bande":
                b = r["bande"]
                if b[0][0] != 0 or b[-1][1] is not None or any(b[i][1] != b[i + 1][0] for i in range(len(b) - 1)) or any(x[0] >= (x[1] or 1e12) for x in b):
                    errori.append(f"JP tasse: {e['id']} fasce non contigue o non crescenti: {b}")
            elif r["tipo"] != "pct" or not 0 < r["valore"] <= 10:
                errori.append(f"JP tasse: {e['id']} regola sconosciuta: {r}")
            if r.get("include_pref") and e["pref"] != "hokkaido":
                errori.append(f"JP tasse: include_pref fuori dall'Hokkaido: {e['id']}")
        if e.get("pref_regole") and e["pref"] not in G.JT_PREF:
            errori.append(f"JP tasse: {e['id']} ha pref_regole ma la Prefettura non ha la tassa")
        if e["stato"] == "in_vigore" and not e["regole"]:
            errori.append(f"JP tasse: {e['id']} in vigore senza regole")
    # calcolo
    for descr, lid, ci, n, pr, osp, bam, att in ESEMPI_JT:
        py = G.jt_calcola(G.JT_L[lid], ci, n, pr, osp, bam)["totale"]
        ind = jt_indipendente(J, lid, ci, n, pr, osp, bam)
        if abs(py - att) > 1e-6 or ind != att:
            errori.append(f"JP tasse: esempio sbagliato: {descr}: atteso {att}, Python {py}, indipendente {float(ind)}")
    rnd = random.Random(23)
    casi = []
    for _ in range(2500):
        L = rnd.choice(G.JT_LUOGHI)
        ci = (date(2026, 10, 1) + timedelta(days=rnd.randint(0, 1300))).isoformat()
        casi.append([L["id"], ci, rnd.randint(1, 30), rnd.choice([rnd.randint(0, 40000), rnd.randint(0, 400000), round(rnd.uniform(0, 250000), 2)]),
                     rnd.randint(1, 6), rnd.randint(0, 3)])
    for lid, ci, n, pr, osp, bam in casi:
        py = G.jt_calcola(G.JT_L[lid], ci, n, pr, osp, bam)["totale"]
        ind = jt_indipendente(J, lid, ci, n, pr, osp, bam)
        if abs(py - float(ind)) > 1e-6:
            errori.append(f"JP tasse: Python diverso dal ricalcolo indipendente: {lid} {ci} {n} {pr} {osp} {bam}: {py} / {float(ind)}")
            break
    if subprocess.run(["which", "node"], capture_output=True).returncode == 0:
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "jt.js"
            f.write_text(G.MOTORE_JS + G.JT_JS + "\nvar L=" + json.dumps(G.JT_L, ensure_ascii=False) + ";var C=" + json.dumps(casi) +
                         ";console.log(JSON.stringify(C.map(function(c){var o=jtCalcola(L[c[0]],c[1],c[2],c[3],c[4],c[5]);return [o.totale,o.comp,o.prima,o.inclusa];})));",
                         encoding="utf-8")
            out = subprocess.run(["node", str(f)], capture_output=True, text=True)
        if out.returncode != 0:
            errori.append("JP tasse: errore node: " + out.stderr[:300])
        else:
            for c_, r in zip(casi, json.loads(out.stdout)):
                o = G.jt_calcola(G.JT_L[c_[0]], *c_[1:])
                py = [o["totale"], o["comp"], o["prima"], o["inclusa"]]
                if abs(py[0] - r[0]) > 1e-6 or [[x[0], x[2]] for x in py[1]] != [[x[0], x[2]] for x in r[1]] or py[2:] != r[2:] \
                        or any(abs(a[1] - b[1]) > 1e-6 for a, b in zip(py[1], r[1])):
                    errori.append(f"JP tasse: JS diverso da Python: {c_}: py={py} js={r}")
                    break
    else:
        errori.append("JP tasse: node non trovato, confronto JS saltato")
    # nuovo motore = motore delle 5 pagine esistenti
    for slug, lid in (("tokyo", "tokyo"), ("kyoto", "kyoto"), ("sapporo", "sapporo"), ("kutchan-niseko", "kutchan"), ("hakuba", "hakuba")):
        R = D[slug]
        for _ in range(300):
            ci = (date(2026, 11, 1) + timedelta(days=rnd.randint(0, 1200))).isoformat()
            n, osp, pr = rnd.randint(1, 20), rnd.randint(1, 5), rnd.choice([rnd.randint(0, 300000), round(rnd.uniform(0, 60000), 2)])
            a = G.calcola(R, "all", ci, n, osp, 0, 1, pr)["totale"]
            b = G.jt_calcola(G.JT_L[lid], ci, n, pr, osp)["totale"]
            if abs(a - b) > 1e-6:
                errori.append(f"JP tasse: {slug}: pagina esistente {a} ≠ nuovo motore {b} ({ci}, {n} notti, {osp} ospiti, {pr})")
                break
    # pagine
    sm = _sitemap()
    oggi = G.OGGI.isoformat()
    for e in enti:
        p = e["pagina"]
        if not p.startswith(G.JT_HUB):
            continue
        f = SITO / p / "index.html"
        if not f.exists():
            errori.append(f"JP tasse: pagina mancante {p}")
            continue
        t = f.read_text(encoding="utf-8")
        titolo = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(titolo) > 70 or "accommodation tax" not in titolo or not re.search(r"202[67]", titolo):
            errori.append(f"JP tasse: titolo oltre 70 caratteri o senza anno: {titolo} ({len(titolo)})")
        r = re.search(r'<p class="risposta">(.*?)</p>', t, re.S)
        prima = unescape(r.group(1)).split(". ")[0] if r else ""
        if f"checked on {G.JT_CHECK}" not in prima or not re.search(r"Ministry of Internal Affairs|Government|Prefecture|City|Town|Bureau", prima) \
                or not re.search(r"¥|%", prima):
            errori.append(f"JP tasse: {p}: la prima frase non ha cifra, fonte e data del controllo")
        for fo in G.jt_fonti(e):
            if G.escape(fo["url"]) not in t:
                errori.append(f"JP tasse: {p}: fonte non linkata {fo['url']}")
        if f"{G.URL_SITO}/{p}" not in sm:
            errori.append(f"JP tasse: {p} non nella sitemap")
        if G.jt_giorno_rif(G.JT_L[e["id"]]) is not None:
            m = re.search(r'<script type="application/json" id="jt-dati">(.*?)</script>', t, re.S)
            if not m or json.loads(m.group(1).replace("<\\/", "</")) != [G.JT_L[e["id"]]] or "jtCalcola" not in t:
                errori.append(f"JP tasse: {p}: calcolatore mancante o con dati diversi")
        if G.MON.link_affiliati(t):
            errori.append(f"JP tasse: {p}: link di affiliazione")
    hub = (SITO / G.JT_HUB / "index.html").read_text(encoding="utf-8")
    p27 = (SITO / G.JT_27 / "index.html").read_text(encoding="utf-8")
    for nome, t, url in (("pagina riassuntiva", hub, G.JT_HUB), ("pagina 2027", p27, G.JT_27)):
        titolo = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(titolo) > 70 or "Japan accommodation tax" not in titolo:
            errori.append(f"JP tasse: {nome}: titolo {titolo} ({len(titolo)})")
        if f"{G.URL_SITO}/{url}" not in sm:
            errori.append(f"JP tasse: {nome} non nella sitemap")
        r = re.search(r'<p class="risposta">(.*?)</p>', t, re.S)
        if not r or f"checked on {G.JT_CHECK}" not in unescape(r.group(1)).split(". Amounts")[0].split(". Tokyo")[0] or "Ministry of Internal Affairs" not in r.group(1):
            errori.append(f"JP tasse: {nome}: prima frase senza fonte e data")
        if G.escape(J["fonte_elenco"]["url"]) not in t:
            errori.append(f"JP tasse: {nome}: elenco del Ministero non linkato")
        ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)]
        faq = [x for x in ld if x.get("@type") == "FAQPage"]
        if len(faq) != 1 or len(faq[0]["mainEntity"]) < 4:
            errori.append(f"JP tasse: {nome}: FAQPage mancante")
        else:
            for q in faq[0]["mainEntity"]:
                if G.escape(q["name"]) not in t or G.escape(q["acceptedAnswer"]["text"]) not in t:
                    errori.append(f"JP tasse: {nome}: domanda FAQ non visibile: {q['name']}")
        if G.MON.link_affiliati(t):
            errori.append(f"JP tasse: {nome}: link di affiliazione")
    for e in enti:
        link = f'href="../{e["pagina"]}"'
        if e["stato"] == "in_vigore" and link not in hub:
            errori.append(f"JP tasse: la pagina riassuntiva non linka {e['pagina']}")
        if e["stato"] == "approvato":
            if link not in p27:
                errori.append(f"JP tasse: la pagina 2027 non linka {e['pagina']}")
            quando = G.data_breve(e["inizio"]) if e.get("inizio") else e.get("inizio_breve", "Jan 2027 or later")
            if not re.search(r"<td><strong>" + re.escape(quando) + r"</strong></td><td>" + re.escape(f'<a href="../{e["pagina"]}">'), p27):
                errori.append(f"JP tasse: pagina 2027: {e['en']} senza la data {quando}")
    for pag, link in [("index.html", f'href="{G.JT_HUB}"'), ("country/japan/index.html", f'href="../../{G.JT_HUB}"'),
                      ("tourist-tax-changes-2027/index.html", f'href="../{G.JT_27}"'), ("japan-tax-free-refund/index.html", f'href="../{G.JT_HUB}"')] + \
            [(f"{d['slug']}/index.html", f'href="../{G.JT_HUB}"') for d in G.DEST if d["country_slug"] == "japan"]:
        if link not in (SITO / pag).read_text(encoding="utf-8"):
            errori.append(f"JP tasse: {pag} non linka {link}")
    return errori


# 12. Belgio (31/10/2026): Bruxelles, Gand, Bruges da fonti ufficiali. Esempi a mano:
ESEMPI_BE = [
    ("Brussels standard, 2 rooms, 3 nights: €5 × 2 × 3", "brussels", "std", "2026-11-01", 3, 2, 0, 2, 0, 30.00),
    ("Brussels homestay, 1 room, 2 nights: €4 × 2", "brussels", "home", "2026-11-01", 2, 2, 0, 1, 0, 8.00),
    ("Brussels, 91 nights: more than 90 days, not taxed", "brussels", "std", "2026-11-01", 91, 2, 0, 1, 0, 0.00),
    ("Ghent category 2, 2 adults + 1 child, 2 nights: €3.93 × 2 × 2", "ghent", "c2", "2026-11-01", 2, 2, 1, 1, 0, 15.72),
    ("Ghent category 3, 2 adults, 1 night in 2029: €6.96 × 2", "ghent", "c3", "2029-01-01", 1, 2, 0, 1, 0, 13.92),
    ("Bruges hotel, 2 adults, 31 Dec 2027 + 1 Jan 2028: €3.75 × 2 + €5 × 2", "bruges", "room", "2027-12-31", 2, 2, 0, 1, 0, 17.50),
    ("Bruges campsite, 2 adults + 2 children, 3 nights: €1.50 × 2 × 3", "bruges", "camp", "2026-07-01", 3, 2, 2, 1, 0, 9.00),
]


def controlla_belgio():
    """12. Belgio: tre destinazioni con fonti ufficiali (be.brussels, stad.gent, brugge.be) lette (HTTP 200) e datate; esempi a mano; titolo ≤ 70
    con anno e cifra; prima frase con fonte e data; pagina Belgio con Anversa non coperta e nessun importo per crocieristi e pullman di Bruges;
    tabella Europa; voci 2028-2029 nella pagina dei cambi."""
    errori = []
    domini = {"brussels": "https://be.brussels/", "ghent": "https://stad.gent/", "bruges": "https://www.brugge.be/"}
    for slug, dom in domini.items():
        if slug not in D:
            errori.append(f"Belgio: {slug} mancante nei dati")
            continue
        R = D[slug]
        if any(f["http"] != 200 or not f.get("controllato_il") or not f["url"].startswith(dom) for f in R["fonti"]):
            errori.append(f"Belgio: {slug}: fonte non ufficiale ({dom}), non letta o senza data")
        t = (SITO / slug / "index.html").read_text(encoding="utf-8")
        titolo = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(titolo) > 70:
            errori.append(f"Belgio: {slug}: titolo oltre 70 caratteri: {titolo}")
        r = re.search(r'<p class="risposta">(.*?)</p>', t, re.S)
        prima = unescape(r.group(1)).split(". ")[0] if r else ""
        if "checked on 31 October 2026" not in prima or "€" not in prima:
            errori.append(f"Belgio: {slug}: la prima frase non ha cifra, fonte e data")
    for descr, slug, cat, ci, n, p, es, st, pr, att in ESEMPI_BE:
        o = G.calcola(D[slug], cat, ci, n, p, es, st, pr)
        if abs(o["totale"] - att) > 0.005:
            errori.append(f"Belgio: esempio sbagliato: {descr}: atteso {att}, calcolato {o['totale']}")
    paese = (SITO / "country" / "belgium" / "index.html").read_text(encoding="utf-8")
    if "Antwerp is not covered" not in paese or "we show no amount" not in paese:
        errori.append("Belgio: pagina paese senza la riga su Anversa o sulla tassa di Bruges per crocieristi")
    br = G.MON.testo_visibile((SITO / "bruges" / "index.html").read_text(encoding="utf-8"))
    if re.search(r"€4(?!\d)|4 euro", br):
        errori.append("Belgio: Bruges mostra un importo per crocieristi e pullman non confermato da fonti ufficiali")
    europa = (SITO / "tourist-taxes-europe-2026" / "index.html").read_text(encoding="utf-8")
    for slug in domini:
        if f'href="../{slug}/"' not in europa:
            errori.append(f"Belgio: {slug} non nella tabella Europa")
    dopo = {x["slug"]: x["dal"] for x in G.CAMBI["dopo"]}
    if dopo.get("bruges") != "2028-01-01" or dopo.get("ghent") != "2029-01-01" \
            or not any(t.get("dal") == "2028-01-01" for t in D["bruges"]["tariffe"]) or not any(t.get("dal") == "2029-01-01" for t in D["ghent"]["tariffe"]):
        errori.append("Belgio: cambi 2028 (Bruges) e 2029 (Gand) non coerenti con i dati")
    return errori


# 13. Santiago de Compostela e Napoli (4/11/2026), dalle fonti ufficiali con impronta (sha256) e data. Esempi calcolati a mano:
# (descrizione, slug, categoria, check-in, notti, paganti, esenti, totale atteso, notti senza tariffa attese)
ESEMPI_SN = [
    ("Santiago hotel 4* superior, 2 adults + 1 child of 10, 3 nights: €2.50 × 2 × 3", "santiago-de-compostela", "h4s", "2026-11-10", 3, 2, 1, 15.00, 0),
    ("Santiago hotel 3*, 2 adults, 7 nights: only 5 days taxed, €2 × 2 × 5", "santiago-de-compostela", "h3", "2027-07-20", 7, 2, 0, 20.00, 0),
    ("Santiago albergue, 1 pilgrim, 2 nights: €1 × 1 × 2", "santiago-de-compostela", "alb", "2027-07-24", 2, 1, 0, 2.00, 0),
    ("Santiago holiday rental (VUT), 2 adults, 4 nights: €2 × 2 × 4", "santiago-de-compostela", "vut", "2026-12-30", 4, 2, 0, 16.00, 0),
    ("Santiago guest house, 29 Sep 2025, 4 nights, 2 adults: 2 nights before 1 Oct 2025, then €1.50 × 2 × 2", "santiago-de-compostela", "pen", "2025-09-29", 4, 2, 0, 6.00, 0),
    ("Naples 4* hotel, 2 adults + 1 child, 3 nights: €6 × 2 × 3", "naples", "h4", "2026-11-10", 3, 2, 1, 36.00, 0),
    ("Naples B&B (non-hotel), 2 adults, 16 nights: 14 nights × €5.50 × 2", "naples", "extra", "2026-06-01", 16, 2, 0, 154.00, 0),
    ("Naples 3* hotel, 29 Apr 2026, 3 nights, 2 adults: 2 × (€4.50 × 2) + 1 × (€5.50 × 2)", "naples", "h3", "2026-04-29", 3, 2, 0, 29.00, 0),
    ("Naples short-term rental, 30 Dec 2026, 3 nights, 2 adults: 2 × (€6 × 2); 2027 rate not published", "naples", "str", "2026-12-30", 3, 2, 0, 24.00, 1),
    ("Naples 1* hotel, 1 adult, 2 nights in February 2026: €3 × 2", "naples", "h1", "2026-02-10", 2, 1, 0, 6.00, 0),
]
SN_DOMINI = {"santiago-de-compostela": ("https://bop.dacoruna.gal/", "https://www.santiagoturismo.com/", "https://www.boe.es/"),
             "naples": ("https://www.comune.napoli.it/", "https://static-www.comune.napoli.it/")}
SN_EVENTO = {"santiago-de-compostela": (("https://catedraldesantiago.es/", "https://www.poderjudicial.es/"), ("Holy Year", "25 July", "as of 27 November 2026")),
             "naples": (("https://www.comune.napoli.it/",), ("22 May to 4 July 2027", "10 to 19 July 2027", "calculator stops at 31 December 2026"))}


def _fonte_ok(f, domini):
    return (f["http"] == 200 and f.get("controllato_il", "") >= "2026-11-04" and f["url"].startswith(domini)
            and re.fullmatch(r"sha256:[0-9a-f]{64}", f.get("impronta", "")) and f.get("impronta_di") in ("file", "testo"))


def controlla_santiago_napoli():
    """13. Santiago de Compostela e Napoli (4/11/2026): fonti ufficiali (domini attesi, HTTP 200, data, impronta sha256); tariffe uguali alle fonti
    lette (ordinanza 1.32 + legge galiziana 5/2024 art. 16; delibera di Giunta di Napoli 89/2026); esempi a mano; Napoli senza tariffe 2027;
    titolo ≤ 70 con l'anno e la cifra; prima frase con cifra, fonte e data; riquadro dell'evento con fonte ufficiale; sitemap, pagina paese, tabella Europa."""
    errori = []
    attese = {
        "santiago-de-compostela": {"h5s": 2.5, "h5": 2.5, "h4s": 2.5, "h4": 2, "h3s": 2, "h3": 2, "h2s": 2, "h2": 1.5, "h1s": 1.5, "h1": 1.5,
                                   "pen": 1.5, "alb": 1, "camp": 1, "rural": 1, "apt": 1, "vt": 1, "vut": 2},
        "naples": {("h5", "2026-01-01"): 5, ("h4", "2026-01-01"): 5, ("h3", "2026-01-01"): 4.5, ("h2", "2026-01-01"): 3.5, ("h1", "2026-01-01"): 3,
                   ("extra", "2026-01-01"): 4.5, ("str", "2026-01-01"): 5, ("h5", "2026-05-01"): 6, ("h4", "2026-05-01"): 6, ("h3", "2026-05-01"): 5.5,
                   ("h2", "2026-05-01"): 4.5, ("h1", "2026-05-01"): 4, ("extra", "2026-05-01"): 5.5, ("str", "2026-05-01"): 6},
    }
    sm = _sitemap()
    europa = (SITO / "tourist-taxes-europe-2026" / "index.html").read_text(encoding="utf-8")
    for slug, domini in SN_DOMINI.items():
        if slug not in D:
            errori.append(f"{slug}: mancante nei dati")
            continue
        R = D[slug]
        for f in R["fonti"]:
            if not _fonte_ok(f, domini):
                errori.append(f"{slug}: fonte non ufficiale, non letta, senza data (dal 4/11/2026) o senza impronta: {f['url']}")
        if slug == "santiago-de-compostela":
            got = {t["cat"]: t["valore"] for t in R["tariffe"]}
            if got != attese[slug] or any(t.get("dal") != "2025-10-01" or t.get("al") for t in R["tariffe"]):
                errori.append("Santiago: tariffe diverse dall'ordinanza 1.32 / legge 5/2024 art. 16 o con date sbagliate")
            if R.get("max_notti") != 5 or R.get("esenti_sotto_eta") != 18 or R.get("in_vigore_dal") != "2025-10-01":
                errori.append("Santiago: massimo 5 giorni, esenzione sotto i 18 anni o partenza 1/10/2025 non coerenti con le fonti")
        else:
            got = {(t["cat"], t["dal"]): t["valore"] for t in R["tariffe"]}
            if got != attese[slug] or any(t.get("al") not in ("2026-04-30", "2026-12-31") for t in R["tariffe"]):
                errori.append("Napoli: tariffe diverse dalla delibera di Giunta 89/2026 o con date sbagliate")
            if any((t.get("al") or "9999") > "2026-12-31" for t in R["tariffe"]):
                errori.append("Napoli: tariffa oltre il 31/12/2026 senza delibera")
            if R.get("max_notti") != 14 or R.get("esenti_sotto_eta") != 15:
                errori.append("Napoli: massimo 14 notti o esenzione fino a 14 anni non coerenti con il regolamento e la pagina del Comune")
        ev = R.get("evento")
        dom_ev, frasi = SN_EVENTO[slug]
        if not ev or not ev["fonti"] or any(not _fonte_ok(f, dom_ev) for f in ev["fonti"]) or any(x not in ev["testo"] for x in frasi):
            errori.append(f"{slug}: riquadro dell'evento senza fonte ufficiale ({dom_ev}) datata con impronta, o senza le date ufficiali")
        f = SITO / slug / "index.html"
        if not f.exists():
            errori.append(f"{slug}: pagina mancante")
            continue
        t = f.read_text(encoding="utf-8")
        titolo = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if slug == "naples" and ("we will add" in t or "until 31 Dec" not in titolo or "until 31 December 2026" not in (r := re.search(r'<p class="risposta">(.*?)</p>', t, re.S)).group(1).split(". ")[0]):
            errori.append("Napoli: titolo o prima frase senza il limite del 31/12/2026, o promessa sulle tariffe 2027")
        if len(titolo) > 70 or "2026" not in titolo or "tourist tax" not in titolo or "€" not in titolo:
            errori.append(f"{slug}: titolo oltre 70 caratteri o senza anno, 'tourist tax' o cifra: {titolo}")
        r = re.search(r'<p class="risposta">(.*?)</p>', t, re.S)
        prima = unescape(r.group(1)).split(". ")[0] if r else ""
        if not re.search(r"checked on \d{1,2} [A-Z][a-z]+ 20\d\d", prima) or "€" not in prima or not re.search(r"ordinance 1\.32|Giunta resolution 89", prima):
            errori.append(f"{slug}: la prima frase non ha cifra, fonte e data")
        for fo in R["fonti"] + (ev["fonti"] if ev else []):
            if G.escape(fo["url"]) not in t:
                errori.append(f"{slug}: fonte non linkata nella pagina: {fo['url']}")
        if 'class="card callout evento-box"' not in t:
            errori.append(f"{slug}: manca il riquadro dell'evento")
        if f"{G.URL_SITO}/{slug}/" not in sm:
            errori.append(f"{slug}: non nella sitemap")
        paese = (SITO / "country" / R["country_slug"] / "index.html").read_text(encoding="utf-8")
        if f'href="../../{slug}/"' not in paese:
            errori.append(f"{slug}: non nella pagina del paese")
        if f'href="../{slug}/"' not in europa:
            errori.append(f"{slug}: non nella tabella Europa")
    for descr, slug, cat, ci, n, p, es, att, sconosciute in ESEMPI_SN:
        o = G.calcola(D[slug], cat, ci, n, p, es)
        if abs(o["totale"] - att) > 0.005 or o["sconosciute"] != sconosciute:
            errori.append(f"Santiago/Napoli: esempio sbagliato: {descr}: atteso {att} ({sconosciute} notti senza tariffa), "
                          f"calcolato {o['totale']} ({o['sconosciute']})")
    na = G.MON.testo_visibile((SITO / "naples" / "index.html").read_text(encoding="utf-8"))
    if re.search(r"1[0-8] July 2027|July 10-18|10-18", na) and "10 to 19 July 2027" not in na:
        errori.append("Napoli: date dell'America's Cup diverse da quelle del Comune (10-19 luglio 2027)")
    if "2027" in G.CAMBI["non_elencati"] and "Naples" not in G.CAMBI["non_elencati"]:
        errori.append("Napoli: la pagina 2027 non dice che le tariffe 2027 non sono pubblicate")
    return errori


# 14. Spagna, licenza per affitti turistici (5/11/2026). Conteggi letti a mano il 5/11/2026 (mattina) con un codice diverso da
# raccolta/spagna.py (csv.DictReader sul CSV della Generalitat; JSON OPEN RTA con i nomi dei Comuni; aggregazione SoQL catalana; API INE):
# il registro valenciano si aggiorna ogni giorno, quindi la tolleranza è dell'1 %; INE (maggio 2026) deve essere identico.
# Barcellona: 8.231 è il Comune (codice 08019); 15.905, il numero della ricerca del 4/11, è la provincia (codice 08): letto per codice.
ESEMPI_ES_INE = {"": 341001, "03133": 3887, "29069": None, "08019": 8231}  # Spagna, Torrevieja, (Marbella: solo la %), Barcellona
ESEMPI_ES_PCT = {"": 1.28, "03133": 3.17, "29069": 6.97}
ESEMPI_ES_REG = [("gva", "03133", 10256), ("gva", "46250", 5691), ("gva", "03031", 5667), ("gva", "03047", 5554), ("gva", "03063", 5222),
                 ("gva", "03099", 4616), ("gva", "03082", 4301), ("rta", "29069", 15764), ("rta", "29067", 12609), ("rta", "41091", 9542),
                 ("rta", "29070", 10595), ("cat", "08019", 10651), ("cat", "43905", 7126)]
ESEMPI_ES_TOT = {"gva": 90015, "rta": 153476, "cat": 104502}
# 27/11/2026: gva 2026-10 = 360 (il 5/11 erano 350: iscrizioni di ottobre registrate dopo), ricontato a mano sul CSV del 26/11 (sha256 3490837f…), csv.DictReader su fecha_alta
ESEMPI_ES_MESI = [("gva", None, "2026-08", 263), ("gva", None, "2026-09", 382), ("gva", None, "2026-10", 360), ("rta", None, "2026-10", 567),
                  ("rta", None, "2026-03", 984)]
ES_DOMINI = ("https://www.boe.es/", "https://www.ine.es/", "https://servicios.ine.es/", "https://dadesobertes.gva.es/", "https://www.juntadeandalucia.es/",
             "https://analisi.transparenciacatalunya.cat/", "https://www.bocm.es/")
ES_REGOLE = {  # frasi che devono comparire nelle pagine delle Comunità, lette nei testi ufficiali il 5/11/2026
    "comunitat-valenciana": ("art. 19.1 b", "up to 10 days", "valid for 5 years", "informe municipal de compatibilidad urbanística"),
    "andalusia": ("art. 7.1", "do not set a separate rule on adverts", "art. 2.2", "expressly authorised"),
    "catalonia": ("art. 73.5", "262 municipalities", "9 November 2023", "by 9 November 2028", "between November 2027", f"updated on {G.data_lunga(G.ESN['cat']['aggiornato'])}"),  # data del registro (27/11: dal file, non più fissa)
    "balearic-islands": ("art. 28.3", "art. 120 j", "zonas aptas", "provisionally delimited", "art. 23.7", "island Consell"),
    "canary-islands": ("art. 8.6", "art. 75.16", "13 December 2025"),
    "madrid-region": ("1741/2018", "CIVUT", "voluntary", "5-day minimum stay", "regional tourism administration", "From 10 February 2027", "«la inscripción se practicará de oficio»"),
}


def controlla_spagna():
    """14. Spagna, licenza per affitti turistici (5/11/2026): sentenze del Tribunal Supremo lette sul BOE; fonti ufficiali con HTTP 200, data e impronta;
    conteggi = esempi letti a mano; nessun dato personale in dati/spagna_numeri.json né nelle pagine; pagine (indice, 6 Comunità, 20 Comuni) in sitemap,
    titolo ≤ 70 con l'anno, prima frase con risposta, fonte e data, FAQPage = testo visibile, regole regionali, nessun affiliato, link in entrata."""
    errori = []
    ES, N = G.ES, G.ESN
    # dati personali: il file dei numeri contiene solo codici, mesi, conteggi e metadati delle fonti
    testo_n = (G.DATI / "spagna_numeri.json").read_text(encoding="utf-8")
    if "@" in testo_n or re.search(r"\b[6789]\d{8}\b", testo_n):
        errori.append("Spagna: spagna_numeri.json contiene un'email o un numero di telefono")
    for reg in ("gva", "rta", "cat"):
        d = N[reg]
        if any(not re.fullmatch(r"\d{5}", k) or not isinstance(v, int) for k, v in d["per_comune"].items()):
            errori.append(f"Spagna: {reg}: per_comune con chiavi diverse da codici INE o valori non interi")
        if reg != "cat" and sum(d["per_comune"].values()) + d.get("non_abbinate", 0) != d["totale"]:
            errori.append(f"Spagna: {reg}: somma per Comune diversa dal totale")
        for k, serie in d.get("per_mese", {}).items():
            if not re.fullmatch(r"\d{5}", k) or set(serie) != set(N["mesi"]) or any(not isinstance(v, int) for v in serie.values()):
                errori.append(f"Spagna: {reg}: serie mensile malformata per {k}")
        if abs(d["totale"] - ESEMPI_ES_TOT[reg]) > ESEMPI_ES_TOT[reg] * 0.01:
            errori.append(f"Spagna: {reg}: totale {d['totale']} lontano da quello letto a mano ({ESEMPI_ES_TOT[reg]})")
    if N["rta"].get("non_abbinate", 0) > N["rta"]["totale"] * 0.01:
        errori.append(f"Spagna: troppe case andaluse senza codice INE ({N['rta']['non_abbinate']})")
    for reg, cod, att in ESEMPI_ES_REG:
        got = N[reg]["per_comune"].get(cod, 0)
        if abs(got - att) > max(5, att * 0.01):
            errori.append(f"Spagna: {reg} {cod}: {got} case, a mano {att}")
    for reg, cod, mese, att in ESEMPI_ES_MESI:
        got = (N[reg]["per_mese_totale"] if cod is None else N[reg]["per_mese"][cod]).get(mese)
        if got is None or abs(got - att) > max(3, att * 0.02):
            errori.append(f"Spagna: {reg} {mese}: {got} iscrizioni, a mano {att}")
    if N["ine"]["periodo"] != "2026-05":
        errori.append(f"Spagna: periodo INE {N['ine']['periodo']} invece di 2026-05 (se è uscito novembre 2026, rileggere e aggiornare gli esempi)")
    for cod, att in ESEMPI_ES_INE.items():
        if att is not None and G.es_ine(cod).get("case") != att:
            errori.append(f"Spagna: INE {cod or 'Spagna'}: {G.es_ine(cod).get('case')} case, a mano {att}")
    for cod, att in ESEMPI_ES_PCT.items():
        if G.es_ine(cod).get("pct") != att:
            errori.append(f"Spagna: INE {cod or 'Spagna'}: {G.es_ine(cod).get('pct')} %, a mano {att}")
    # fonti
    for k, f in ES["fonti"].items():
        if (f["http"] != 200 or f["controllato_il"] < "2026-11-05" or not f["url"].startswith(ES_DOMINI)
                or not f.get("url_impronta", f["url"]).startswith(ES_DOMINI)
                or not re.fullmatch(r"sha256:[0-9a-f]{64}", f.get("impronta", "")) or f.get("impronta_di") not in ("file", "testo")):
            errori.append(f"Spagna: fonte {k} non ufficiale, non letta, senza data (dal 5/11/2026) o senza impronta")
    s = ES["sentenze"]
    attese = {"ts_valencia": ("BOE-A-2026-12300", "2026-05-19", "2026-06-08"), "ts_apartur": ("BOE-A-2026-13893", "2026-05-21", "2026-06-26"),
              "ts_murcia": ("BOE-A-2026-15677", "2026-06-01", "2026-07-18")}
    for i, (k, (boe, giorno, bol)) in enumerate(attese.items()):
        if s["fonti"][i] != k or boe not in ES["fonti"][k]["url"] or s["date"][i] != giorno or s["bollettini"][i] != bol:
            errori.append(f"Spagna: sentenza {k} diversa dal BOE ({boe}, {giorno}, pubblicata {bol})")
    # pagine
    sm = _sitemap()
    pagine = [G.ES_SLUG] + [f"{G.ES_SLUG}{R['slug']}/" for R in ES["regioni"]] + [f"{G.ES_SLUG}{c['slug']}/" for c in ES["comuni"]]
    if len(pagine) != 27 or len(set(pagine)) != 27:
        errori.append(f"Spagna: attese 27 pagine distinte (indice, 6 Comunità, 20 Comuni), trovate {len(set(pagine))}")
    for pag in pagine:
        f = SITO / pag / "index.html"
        if not f.exists():
            errori.append(f"Spagna: pagina mancante {pag}")
            continue
        t = f.read_text(encoding="utf-8")
        vis = G.MON.testo_visibile(t)
        titolo = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(titolo) > 70 or "2026" not in titolo:
            errori.append(f"Spagna: titolo oltre 70 caratteri o senza anno in {pag}: {titolo}")
        r = re.search(r'<p class="risposta">(.*?)</p>', t, re.S)
        prima = re.split(r"(?<=\.)\s+(?=[A-Z])", unescape(r.group(1)))[0] if r else ""
        if not re.search(r"(checked|downloaded) on \d{1,2} [A-Z][a-z]+ 20\d\d", prima) or not re.search(r"\d", prima):
            errori.append(f"Spagna: la prima frase non ha risposta con cifra, fonte e data in {pag}")
        if not re.search(r'<p class="fonte">Official sources?: <a href="https://', t):
            errori.append(f"Spagna: manca la riga della fonte ufficiale in {pag}")
        if f"{G.URL_SITO}/{pag}" not in sm:
            errori.append(f"Spagna: {pag} non nella sitemap")
        ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)]
        faq = [x for x in ld if x.get("@type") == "FAQPage"]
        if len(faq) != 1 or len(faq[0]["mainEntity"]) < 3:
            errori.append(f"Spagna: FAQPage mancante o con meno di 3 domande in {pag}")
        else:
            for q in faq[0]["mainEntity"]:
                if G.escape(q["name"]) not in t or G.escape(q["acceptedAnswer"]["text"]) not in t:
                    errori.append(f"Spagna: domanda FAQ non visibile in {pag}: {q['name']}")
        if G.MON.link_affiliati(t) or "sponsored" in t:
            errori.append(f"Spagna: link di affiliazione in {pag}")
        if "@" in vis or re.search(r"\b[6789]\d{8}\b", vis):
            errori.append(f"Spagna: email o telefono nel testo di {pag}")
        if "620/2026" in vis:
            errori.append(f"Spagna: numero di sentenza 620/2026 non presente sul BOE, in {pag}")
        if "datas" in vis or "regional or island" in vis or ("madrid" in pag and "island" in vis):
            errori.append(f"Spagna: testo da correggere ('datas', 'regional or island' o isole nelle pagine di Madrid) in {pag}")
        if "Not legal advice." not in vis:
            errori.append(f"Spagna: manca l'avviso 'Not legal advice' in {pag}")
        if re.search(r"\b(guarantee|guaranteed|we will get|100% legal)\b", vis, re.I):
            errori.append(f"Spagna: promessa nel testo di {pag}")
    indice = (SITO / G.ES_SLUG / "index.html").read_text(encoding="utf-8")
    for k, fo in ES["fonti"].items():
        if G.escape(fo["url"]) not in indice:
            errori.append(f"Spagna: fonte non linkata nell'indice: {k}")
    for R in ES["regioni"]:
        vis = G.MON.testo_visibile((SITO / G.ES_SLUG / R["slug"] / "index.html").read_text(encoding="utf-8"))
        for frase in ES_REGOLE[R["slug"]]:
            if frase not in vis:
                errori.append(f"Spagna: '{frase}' manca nella pagina {R['slug']}")
    vis = G.MON.testo_visibile(indice)
    for frase in ("published in the BOE on 8 June, 26 June and 18 July 2026", "with reference dates in May and November",
                  "Where the regional law requires it", "competent authorities for the sectoral rules on tourist lets (art. 12 d)"):
        if frase not in vis:
            errori.append(f"Spagna: '{frase}' manca nell'indice")
    for c in ES["comuni"]:
        t = (SITO / G.ES_SLUG / c["slug"] / "index.html").read_text(encoding="utf-8")
        titolo = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        atteso = N[c["registro"]]["per_comune"][c["ine"]] if c["registro"] else G.es_ine(c["ine"])["case"]
        if f"{atteso:,}" not in titolo:
            errori.append(f"Spagna: {c['slug']}: il titolo non ha il conteggio dei dati ({atteso:,})")
        if f"{G.es_ine(c['ine'])['case']:,}" not in t:
            errori.append(f"Spagna: {c['slug']}: manca il numero INE")
        if c["registro"] in ("gva", "rta"):
            ult = N["mesi"][-1]
            if f"<tr><td>{G.es_mese(ult)}</td><td>{N[c['registro']]['per_mese'][c['ine']][ult]:,}</td></tr>" not in t:
                errori.append(f"Spagna: {c['slug']}: manca la riga di {ult} nella tabella mensile")
        if c["regione"] == "cat" and "262 municipalities" not in t:
            errori.append(f"Spagna: {c['slug']}: manca il riferimento al Decreto-ley 3/2023")
    if f'href="../../{G.ES_SLUG}"' not in (SITO / "country" / "spain" / "index.html").read_text(encoding="utf-8"):
        errori.append("Spagna: la pagina country/spain non linka la sezione")
    if f'href="../{G.ES_SLUG}"' not in (SITO / "about" / "index.html").read_text(encoding="utf-8"):
        errori.append("Spagna: la pagina about non cita la sezione")
    return errori


# 15. USA, tassa sugli alberghi in Florida e Texas (7/11/2026, sezione usa/).
# Aliquote lette a mano il 7/11/2026 sui file ufficiali (pdftotext del DR-15TDT R. 10/26 e del DR-15DSS 2026 R. 11/25; JSON di er34-v24h):
# contea -> (tassa turistica %, sovrimposta totale 2026 %, chi riscuote)
ESEMPI_US_FL = {"Orange": (6, 0.5, "County"), "Miami-Dade": (6, 1.0, "County"), "Bay": (5, 1.0, "County"), "Citrus": (5, 0, "DOR"),
                "Sumter": (0, 1.0, "N/A"), "Hamilton": (3, 2.0, "DOR"), "Palm Beach": (6, 0.5, "County"), "Martin": (5, 0.5, "County"),
                "Hillsborough": (6, 1.5, "County"), "Monroe": (5, 1.5, "County"), "Walton": (5, 1.0, "County"), "Okaloosa": (6, 1.0, "County"),
                "Collier": (5, 0, "County"), "Osceola": (6, 1.5, "County"), "Duval": (6, 1.5, "County"), "Liberty": (0, 1.5, "N/A"),
                "Highlands": (5, 1.5, "County"), "Levy": (4, 1.0, "DOR"), "Desoto": (3, 1.5, "DOR"), "St. Johns": (5, 0.5, "County")}
# (tipo, nome) -> (tax_rate_351, tax_rate_334) come stringhe del file
ESEMPI_US_TX = {("city", "Austin"): ("0.09", "0.02"), ("city", "Houston"): ("0.07", None), ("city", "Dallas"): ("0.07", "0.02"),
                ("city", "San Antonio"): ("0.09", None), ("city", "Galveston"): ("0.09", None), ("city", "South Padre Island"): ("0.09", "0.02"),
                ("city", "Abilene"): ("0.07", "0.02"), ("county", "Bexar"): ("0", "0.018"), ("county", "Harris"): ("0.09", "0.02"),
                ("county", "Cameron"): ("0.02", "0.02"), ("county", "Brazos"): ("0.03", None)}
# (pagina, zona, check-in, notti, prezzo, toggle accesi o None = predefiniti, totale atteso calcolato a mano)
ESEMPI_US_CALC = [
    ("usa/florida/orlando/", 0, "2026-11-10", 3, 200, None, 75.00),             # 200 × 3 × 12,5 %
    ("usa/florida/miami-beach/", 0, "2026-11-10", 3, 200, None, 84.00),         # 6 + 1 + 7 = 14 %
    ("usa/florida/miami/", 0, "2026-11-10", 2, 150, None, 39.00),               # 6 + 1 + 6 = 13 %
    ("usa/florida/bay-county/", 1, "2026-11-10", 2, 100, None, 14.00),          # resto della contea: 6 + 1 = 7 %
    ("usa/florida/brevard-county/", 0, "2026-12-30", 4, 100, None, 46.00),      # 30-31/12 al 12 %, 1-2/1/2027 all'11 % (sovrimposta scaduta)
    ("usa/florida/sumter-county/", 0, "2026-11-10", 1, 100, None, 7.00),        # nessuna tassa turistica
    ("usa/florida/walton-county/", 1, "2026-11-10", 3, 100, None, 27.00),       # resto della contea: 6 + 1 + 2 = 9 %
    ("usa/florida/orlando/", 0, "2026-11-10", 200, 100, None, None),            # oltre sei mesi: non calcolato
    ("usa/texas/austin/", 0, "2026-11-10", 3, 200, None, 102.00),               # 6 + 9 + 2 = 17 %
    ("usa/texas/houston/", 0, "2026-11-10", 40, 100, None, 510.00),             # 17 % sulle prime 30 notti
    ("usa/texas/austin/", 0, "2026-11-10", 2, 10, None, 2.20),                  # sotto 15 $: solo le tasse locali (11 %)
    ("usa/texas/austin/", 0, "2026-11-10", 2, 1, None, 0.00),                   # sotto 2 $: nessuna tassa
    ("usa/texas/san-antonio/", 0, "2026-11-10", 1, 100, None, 16.80),           # 6 + 9 + 1,8 (venue tax di Bexar, accesa di default)
    ("usa/texas/san-antonio/", 0, "2026-11-10", 1, 100, [True, True, False], 15.00),  # Bexar tolta
    ("usa/texas/harris-county/", 0, "2026-11-10", 1, 100, None, 10.00),         # 6 + 2 + 2 (esempio del Comptroller), non il 9 % del file
    ("usa/texas/austin/", 0, "2026-11-10", 1, 100, None, 17.00),                # Bastrop (7 %, porzione marginale): solo nota, non nel calcolo
    ("usa/florida/brevard-county/", 0, "2027-01-02", 1, 100, None, 11.00),      # Brevard perde tutta la sovrimposta (1 %) dal 1/1/2027
]
US_DOMINI = ("https://floridarevenue.com/", "https://comptroller.texas.gov/", "https://data.texas.gov/", "https://www2.census.gov/")


def _scarica_us(url, dest):
    r = subprocess.run(["curl", "-sS", "-L", "-m", "120", "-A", "Mozilla/5.0 (X11; Linux x86_64)", "-o", str(dest), "-w", "%{http_code}", url],
                       capture_output=True, text=True)
    return r.stdout.strip()


def controlla_usa():
    """15. USA (Florida e Texas): fonti ufficiali con impronta e data; aliquote dei dati = file ufficiali riscaricati e riletti qui con un metodo diverso
    (pdftotext -raw invece di -layout; JSON confrontato riga per riga) = esempi letti a mano; calcolatore Python = JS su casi casuali e = esempi a mano;
    titoli e prima frase con la cifra ricalcolata qui dai dati; FAQ visibili = JSON-LD; pagine in sitemap; link da home, elenco, about, menu."""
    errori = []
    U = G.US
    # fonti
    for k, f in U["fonti"].items():
        if (f["http"] != 200 or f["controllato_il"] < "2026-11-07" or not f["url"].startswith(US_DOMINI)
                or not re.fullmatch(r"sha256:[0-9a-f]{64}", f.get("impronta", "")) or f.get("impronta_di") not in ("file", "testo", "json")):
            errori.append(f"USA: fonte {k} non ufficiale, non letta, senza data o senza impronta")
    if U["fonti"]["fl_tdt"].get("revisione") != "10/26" or U["fonti"]["fl_dss"].get("anno") != 2026:
        errori.append("USA: revisione del DR-15TDT o anno del DR-15DSS diversi da quelli letti a mano (10/26, 2026): rileggere i moduli")
    # dati = esempi a mano
    FLC = {c["nome"]: c for c in U["florida"]["contee"]}
    if len(FLC) != 67:
        errori.append(f"USA: contee della Florida {len(FLC)} invece di 67")
    for n, (tdt, sur, chi) in ESEMPI_US_FL.items():
        c = FLC.get(n)
        if not c or c["aliquota"] != tdt or abs(c["surtax"]["totale"] - sur) > 1e-9 or c["riscossa_da"] != chi:
            errori.append(f"USA: {n}: dati {c and (c['aliquota'], c['surtax']['totale'], c['riscossa_da'])}, a mano {(tdt, sur, chi)}")
    TXR = {(r["tipo"], r["nome"]): r for r in U["texas"]["righe"]}
    for k, (a, b) in ESEMPI_US_TX.items():
        r = TXR.get(k)
        if not r or r["r351"] != a or r["r334"] != b:
            errori.append(f"USA: Texas {k}: dati {r and (r['r351'], r['r334'])}, a mano {(a, b)}")
    # file ufficiali riscaricati e riletti con un metodo diverso
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for k in ("fl_tdt", "fl_dss"):
            f = U["fonti"][k]
            dest = tmp / f"{k}.pdf"
            codice = _scarica_us(f["url"], dest)
            if codice != "200":
                errori.append(f"USA: {k} non scaricabile (HTTP {codice}): {f['url']}")
                continue
            imp = "sha256:" + hashlib.sha256(dest.read_bytes()).hexdigest()
            if imp != f["impronta"]:
                errori.append(f"USA: {k} è cambiato dopo la raccolta (impronta diversa): rilanciare python3 -I touristtax/raccolta/usa.py e rileggere")
            raw = re.sub(r"\s+", " ", subprocess.run(["pdftotext", "-raw", str(dest), "-"], capture_output=True, text=True).stdout)
            for c in U["florida"]["contee"]:
                nome = re.escape(c["nome"])
                if k == "fl_tdt":
                    m = re.search(rf"\b{nome}(?: \(\d\))? (\d+)% (County|DOR|N/A)", raw)
                    if not m or float(m.group(1)) != c["aliquota"] or m.group(2) != c["riscossa_da"]:
                        errori.append(f"USA: DR-15TDT riletto: {c['nome']} {m and m.groups()} invece di {(c['aliquota'], c['riscossa_da'])}")
                else:
                    alias = {"Desoto": "DeSoto"}.get(c["nome"], c["nome"])
                    m = re.search(rf"\b{re.escape(alias)} (\.?\d+(?:\.\d+)?%|None)", raw)
                    tot = float(m.group(1).rstrip("%")) if m and m.group(1) != "None" else 0.0
                    if not m or abs(tot - c["surtax"]["totale"]) > 1e-9:
                        errori.append(f"USA: DR-15DSS riletto: {c['nome']} {m and m.group(1)} invece di {c['surtax']['totale']}")
                    if abs(sum(p["aliquota"] for p in c["surtax"]["parti"]) - c["surtax"]["totale"]) > 1e-9:
                        errori.append(f"USA: {c['nome']}: parti della sovrimposta che non sommano al totale")
        f = U["fonti"]["tx_dati"]
        dest = tmp / "tx.json"
        codice = _scarica_us(f["url_dati"], dest)
        if codice != "200":
            errori.append(f"USA: dataset del Texas non scaricabile (HTTP {codice})")
        else:
            righe = json.loads(dest.read_text(encoding="utf-8"))
            ordinate = sorted(righe, key=lambda r: (r.get("type", ""), r.get("name", "")))
            imp = "sha256:" + hashlib.sha256(json.dumps(ordinate, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()
            if imp != f["impronta"]:
                errori.append("USA: il dataset del Texas è cambiato dopo la raccolta: rilanciare python3 -I touristtax/raccolta/usa.py")
            nuovi = {(r["type"], r["name"]): (r.get("tax_rate_351"), r.get("tax_rate_334")) for r in righe}
            for r in U["texas"]["righe"]:
                if nuovi.get((r["tipo"], r["nome_file"])) != (r["r351"], r["r334"]):
                    errori.append(f"USA: Texas {r['nome_file']}: dati {(r['r351'], r['r334'])}, file {nuovi.get((r['tipo'], r['nome_file']))}")
                    break
            if len(righe) != len(U["texas"]["righe"]):
                errori.append(f"USA: Texas: {len(righe)} righe nel file, {len(U['texas']['righe'])} nei dati")
    # calcolatore: esempi a mano
    voci = G.us_pagine()
    luoghi = {L["pagina"]: L for _, _, L, _, _, _ in voci}
    for pag, z, ci, notti, prezzo, on, atteso in ESEMPI_US_CALC:
        L = luoghi.get(pag)
        if not L:
            errori.append(f"USA: esempio su una pagina che non c'è: {pag}")
            continue
        on = on if on is not None else G.us_on(L["zone"][z])
        o = G.us_calcola(L, z, on, ci, notti, prezzo)
        got = None if o["fuori"] else G.r2(o["totale"])
        if got != atteso:
            errori.append(f"USA: esempio {pag} {ci} {notti} notti {prezzo} $: {got}, a mano {atteso}")
    # calcolatore: JS = Python su casi casuali
    rnd = random.Random(11)
    casi = []
    tutti = [L for _, _, L, _, _, _ in voci] + [G.fl_luogo(c) for c in G.US_FL["contee"]]
    for _ in range(1500):
        L = rnd.choice(tutti)
        z = rnd.randrange(len(L["zone"]))
        on = [bool(c["on"]) if not c.get("opz") else rnd.random() < 0.5 for c in L["zone"][z]["comp"]]
        ci = (G.date(2026, 11, 1) + G.timedelta(days=rnd.randrange(500))).isoformat()
        casi.append([L, z, on, ci, rnd.choice([1, 2, 3, 7, 29, 30, 31, 45, 181, 182, 184, 200]), rnd.choice([0, 1, 2, 10, 14.99, 15, 89.5, 200, 640])])
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "us.js"
        f.write_text(G.MOTORE_JS + G.US_JS + "\nvar C=" + json.dumps(casi) + ";console.log(JSON.stringify(C.map(function(c){"
                     "var o=usCalcola(c[0],c[1],c[2],c[3],c[4],c[5]);return [o.totale,o.fuori,o.tassate,o.dopo,o.trenta,o.righe];})));", encoding="utf-8")
        out = subprocess.run(["node", str(f)], capture_output=True, text=True)
    if out.returncode != 0:
        errori.append("USA: errore node: " + out.stderr[:300])
    else:
        for c, r in zip(casi, json.loads(out.stdout)):
            o = G.us_calcola(*c)
            py = [o["totale"], o["fuori"], o["tassate"], o["dopo"], o["trenta"], o["righe"]]
            if abs(py[0] - r[0]) > 1e-6 or py[1:5] != r[1:5] or [x[0] for x in py[5]] != [x[0] for x in r[5]] or [x[2] for x in py[5]] != [x[2] for x in r[5]]:
                errori.append(f"USA: JS diverso da Python: {c[0]['nome']} {c[1:]}: py={py[:5]} js={r[:5]}")
                break
    # pagine
    sm = _sitemap()
    oggi = G.OGGI.isoformat()
    pagine = [G.US_HUB, G.US_FLS, G.US_TXS] + list(luoghi)
    attese = 3 + sum(len(v) for v in U["pagine"].values())
    if len(set(pagine)) != attese:
        errori.append(f"USA: attese {attese} pagine distinte, trovate {len(set(pagine))}")
    for p in U["pagine"].values():
        for x in p:
            if len(x["suggerimenti"]) < 2:
                errori.append(f"USA: pagina senza ricerche vere sufficienti: {x['nome']}")
    for pag in pagine:
        f = SITO / pag / "index.html"
        if not f.exists():
            errori.append(f"USA: pagina mancante {pag}")
            continue
        t = f.read_text(encoding="utf-8")
        vis = G.MON.testo_visibile(t)
        titolo = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(titolo) > 70 or not re.search(r"\d%", titolo):
            errori.append(f"USA: titolo oltre 70 caratteri o senza aliquota in {pag}: {titolo} ({len(titolo)})")
        r = re.search(r'<p class="risposta">(.*?)</p>', t, re.S)
        prima = unescape(r.group(1)) if r else ""
        prima = re.split(r"(?<!\bSt)(?<=[a-z0-9%)])\.\s+(?=[A-Z])", prima)[0]
        if not re.search(r"\d+(\.\d+)?%", prima) or not re.search(r"checked on \d{1,2} [A-Z][a-z]+ 20\d\d", prima):
            errori.append(f"USA: la prima frase non ha aliquota e data del controllo in {pag}")
        if not re.search(r'<p class="fonte">Official sources?: <a href="https://(floridarevenue\.com|comptroller\.texas\.gov|data\.texas\.gov)', t):
            errori.append(f"USA: manca la riga della fonte ufficiale in {pag}")
        if f"{G.URL_SITO}/{pag}" not in sm:
            errori.append(f"USA: {pag} non nella sitemap")
        ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)]
        faq = [x for x in ld if x.get("@type") == "FAQPage"]
        if len(faq) != 1 or len(faq[0]["mainEntity"]) < 3:
            errori.append(f"USA: FAQPage mancante o con meno di 3 domande in {pag}")
        else:
            vis_q = re.findall(r'<details class="faq"><summary>(.*?)</summary><p>(.*?)</p></details>', t, re.S)
            ld_q = [(G.escape(q["name"]), G.escape(q["acceptedAnswer"]["text"])) for q in faq[0]["mainEntity"]]
            if vis_q != ld_q:
                errori.append(f"USA: FAQ visibili diverse dal JSON-LD in {pag}")
        if 'data-us' not in t or "usCalcola" not in t:
            errori.append(f"USA: manca il calcolatore in {pag}")
        if "Not tax advice." not in vis:
            errori.append(f"USA: manca l'avviso 'Not tax advice' in {pag}")
        if G.MON.link_affiliati(t) or "sponsored" in t:
            errori.append(f"USA: link di affiliazione in {pag} (nessun programma previsto per gli USA)")
        if pag.startswith(G.US_FLS) and re.search(r"online travel compan|Airbnb|platform", vis):
            errori.append(f"USA: frase sulle piattaforme in una pagina della Florida (le fonti lette non ne parlano): {pag}")
        if pag.startswith(G.US_TXS) and pag != G.US_TXS and G.US_FR["tx_hot"]["piattaforme"] not in G.MON.testo_visibile(t).replace("’", "'"):
            errori.append(f"USA: manca la frase del Comptroller sulle piattaforme in {pag}")
    # cifre dei titoli ricalcolate qui dai dati (non con le funzioni di genera.py)
    U_K = {r["nome"].lower(): r for r in U["texas"]["righe"] if r["tipo"] == "county"}

    def fl_tot(c, tdt):
        s = sum(p["aliquota"] for p in c["surtax"]["parti"] if (not p["dal"] or p["dal"] <= oggi) and (not p["al"] or oggi <= p["al"]))
        return 6 + s + tdt
    for tipo, _, L, _, _, extra in voci:
        t = (SITO / L["pagina"] / "index.html").read_text(encoding="utf-8")
        titolo = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if tipo == "fl_contea" and len(G.fl_zone(extra["c"])) == 1:
            c = extra["c"]
            att = G.us_pct(fl_tot(c, c["aliquota"]))
        elif tipo == "fl_citta" and len(L["zone"]) == 1:
            c = extra["c"]
            zid = (extra.get("zone") or [""])[0]
            tdt = next((z["aliquota"] for z in G.US_ZONE.get(c["id"], []) if z["id"] == zid), c["aliquota"])
            att = G.us_pct(fl_tot(c, tdt))
        elif tipo == "tx_citta":
            r = extra["r"]
            venue = sum(float(U_K[k]["r334"] or 0) * 100 for k in (x.lower() for x in r.get("contee", [])) if k in U_K and k != "harris")
            att = "17%" if r["nome"] == "Houston" else G.us_pct(6 + float(r["r351"] or 0) * 100 + float(r["r334"] or 0) * 100 + venue)
        else:
            continue
        if att not in titolo:
            errori.append(f"USA: il titolo di {L['pagina']} non ha il totale ricalcolato {att}: {titolo}")
    # revisione del 7/11/2026: Harris dalla FAQ, anomalia del file segnalata; sovrimposte in scadenza; etichette della Florida
    vh = G.MON.testo_visibile((SITO / G.US_TXS / "harris-county" / "index.html").read_text(encoding="utf-8"))
    for frase in ("2% Harris County tax and 2% Harris County - Houston Sports Authority tax", "not consistent with the Comptroller's example", "10%"):
        if frase not in vh:
            errori.append(f"USA: Harris County: manca '{frase}'")
    if "not consistent with the Comptroller's example" not in G.MON.testo_visibile((SITO / G.US_TXS / "index.html").read_text(encoding="utf-8")):
        errori.append("USA: tabella delle contee del Texas senza la nota sull'anomalia di Harris")
    vf = G.MON.testo_visibile((SITO / G.US_FLS / "index.html").read_text(encoding="utf-8"))
    for frase in ("Brevard County: the whole 1%", "Charlotte County: the whole 1%", "Liberty County: 0.5% (of 1.5%)", "Santa Rosa County: 0.5% (of 1%)"):
        if frase not in vf:
            errori.append(f"USA: Florida, cambi della sovrimposta: manca '{frase}'")
    for pag in luoghi:
        if pag.startswith(G.US_FLS) and "tourist development tax," in G.MON.testo_visibile((SITO / pag / "index.html").read_text(encoding="utf-8")).split("Questions")[0][:600]:
            errori.append(f"USA: {pag}: etichetta 'tourist development tax' nella risposta invece di 'local option transient rental tax'")
    # collegamenti in entrata
    home = (SITO / "index.html").read_text(encoding="utf-8")
    for x in (f'href="{G.US_HUB}"', f'href="{G.US_FLS}orlando/"', f'href="{G.US_TXS}houston/"'):
        if x not in home:
            errori.append(f"USA: la home non ha il link {x}")
    if f'href="../{G.US_HUB}"' not in (SITO / "about" / "index.html").read_text(encoding="utf-8"):
        errori.append("USA: la pagina about non cita la sezione")
    if 'id="lista-dest"' in home and f'href="{G.US_FLS}orlando/"' not in home.split('id="lista-dest"')[1].split("</div>")[0]:
        errori.append("USA: Orlando manca dall'elenco delle destinazioni della home")
    return errori


# 16. Canarie: c'è una tassa di soggiorno? (27/11/2026). Fatti letti a mano il 27/11/2026 nei testi ufficiali (BOP Las Palmas n. 30 del
# 10/3/2025 e n. 134 del 9/11/2026, Diario de Sesiones 61 e 74 del Parlamento delle Canarie, avviso del Cabildo di Tenerife del 18/1/2026,
# Decreto Legislativo 1/2025 art. 32.1), scritti qui una seconda volta: se dati/canarie.json cambia senza una nuova lettura, il controllo si ferma.
CN_ATTESI = {"mogan": 0.15, "la_oliva": 0.56, "voti": (25, 40), "mozione": (24, 37), "igic": 7,
             "teide": {("PNT 10", "any day"): (0, 6, 15), ("PNT 07", "working days"): (0, 3, 6), ("PNT 07", "weekends and public holidays"): (0, 5, 10)}}
CN_ESEMPI = [  # (pagina, testo atteso, calcolo a mano)
    ("gran-canaria", "2 × 7 × €0.15 = <strong>€2.10</strong>", 2 * 7 * 0.15), ("gran-canaria", "4 × 7 × €0.15 = <strong>€4.20</strong>", 4 * 7 * 0.15),
    ("fuerteventura", "2 × 7 × €0.56 = <strong>€7.84</strong>", 2 * 7 * 0.56), ("fuerteventura", "4 × 7 × €0.56 = <strong>€15.68</strong>", 4 * 7 * 0.56),
    ("tenerife", "2 × €15 = <strong>€30</strong>", 2 * 15), ("tenerife", "2 × €10 = <strong>€20</strong>", 2 * 10), ("tenerife", "2 × €6 = <strong>€12</strong>", 2 * 6),
    ("canary-islands", "2 × 7 × €0.15 = <strong>€2.10</strong>", 2.10), ("canary-islands", "2 × 7 × €0.56 = <strong>€7.84</strong>", 7.84),
    ("lanzarote", "2 × €0.56 = €1.12", 1.12),
]
CN_DOMINI = ("https://www.boplaspalmas.net/", "https://www.parcan.es/", "https://tenerifemassostenible.tenerife.es/", "https://www.boe.es/ccaa/boc/",
             "https://www.boe.es/buscar/act.php?id=BOE-A-2004-4214", "https://www.boe.es/buscar/act.php?id=BOE-A-1998-16718")
CN_PAGINE = ("canary-islands", "tenerife", "gran-canaria", "fuerteventura", "lanzarote")
CN_INIZIO = {  # inizio esatto della risposta, pagina per pagina (un «no» pieno solo dove è stato letto)
    "canary-islands": "Short answer: no, the Canary Islands have no regional tourist tax",
    "tenerife": "Short answer: no tourist tax per night in Tenerife that we could find",
    "gran-canaria": "Short answer: not for the island as a whole",
    "fuerteventura": "Short answer: no, nobody in Fuerteventura charges a tourist tax today",
    "lanzarote": "Short answer: no, Lanzarote has no tourist tax",
}
CN_SOGLIA_PAROLE_UNICHE = 110   # cancello AdSense della rete (visaincome/verifica.py): sotto questa soglia niente pubblicità
CN_MAX_FRASI_COMUNI = 0.40      # quota massima di frasi di una pagina che compaiono anche in un'altra pagina delle Canarie


def _cn_main(t):
    m = re.search(r"<main\b.*?</main>", t, re.S).group(0)
    return m[:m.find("<h2>Sources</h2>")] if "<h2>Sources</h2>" in m else m


def _cn_frasi(t):
    """Frasi del contenuto proprio (senza l'elenco delle fonti, le righe delle fonti e l'avviso), per misurare i doppioni."""
    m = re.sub(r'<p class="(fonte[^"]*|avviso)">.*?</p>', " ", _cn_main(t), flags=re.S)
    m = re.sub(r"</(p|li|td|th|h1|h2|h3|summary|small)>", ". ", m)
    x = re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", m)))
    return {f.strip().lower() for f in re.split(r"(?<=[.?!:]) ", x) if len(f.split()) >= 6}


def controlla_canarie():
    """16. Fonti (domini ufficiali, HTTP 200, data, impronta del file o frammenti letti; la stampa solo come 'stampa'); fatti = attesi letti a mano
    = numeri dentro i frammenti; esempi a mano; 5 pagine: titolo ≤ 70, H1 = domanda, prima frase = risposta con la data, ogni fonte linkata con la
    data, stampa dichiarata, nessun importo in euro fuori dai dati, FAQ = JSON-LD, sitemap, link (Spagna, Baleari, home, Europa), parole uniche,
    doppioni fra le pagine."""
    errori = []
    C, F = G.CN, G.CN_F
    oggi_dati = C["controllato_il"]
    for k, f in F.items():
        if f["tipo"] == "ufficiale":
            if not f["url"].startswith(CN_DOMINI):
                errori.append(f"Canarie: fonte ufficiale su un dominio non atteso: {k} {f['url']}")
        elif f["tipo"] != "stampa" or not f["url"].startswith("https://rtvc.es/"):
            errori.append(f"Canarie: fonte né ufficiale né stampa dichiarata: {k}")
        if f["http"] != 200 or f.get("controllato_il", "") < "2026-11-27" or not f.get("frammenti") or not f.get("breve"):
            errori.append(f"Canarie: fonte non letta, senza data, senza frammenti o senza nome breve: {k}")
        if f["impronta_di"] == "file" and not re.fullmatch(r"sha256:[0-9a-f]{64}", f.get("impronta", "")):
            errori.append(f"Canarie: PDF senza impronta sha256: {k}")
        if f["impronta_di"] not in ("file", "frammenti") or (f["url"].endswith(".pdf") != (f["impronta_di"] == "file")):
            errori.append(f"Canarie: tipo di impronta sbagliato: {k}")
    fr = lambda k: " ".join(F[k]["frammenti"])
    mg, ol, te, reg = C["mogan"], C["la_oliva"], C["teide"], C["regionale"]
    if mg["importo"] != CN_ATTESI["mogan"] or "en concreto 0,15 /día por alojamiento/día" not in fr("bop_mogan") or mg["fonte"] != "bop_mogan":
        errori.append("Canarie: importo di Mogán diverso da 0,15 (BOP n. 30 del 10/3/2025, art. 8)")
    if (mg["bop"], mg["in_vigore_dal"], mg["approvazione_definitiva"], mg["esenzioni"]) != ({"numero": 30, "data": "2025-03-10"}, "2025-03-11", "2025-02-28", 0):
        errori.append("Canarie: Mogán, bollettino, date o esenzioni diversi dal testo letto")
    if "Pleno de 28 de febrero de 2025" not in fr("bop_mogan") or "día siguiente al de su publicación íntegra" not in fr("bop_mogan"):
        errori.append("Canarie: Mogán, frammenti senza l'approvazione definitiva o l'entrata in vigore")
    if ol["importo"] != CN_ATTESI["la_oliva"] or "0,56 euros por cada pernoctación y contribuyente" not in fr("bop_la_oliva") or ol["in_vigore"] is not False:
        errori.append("Canarie: La Oliva, importo diverso da 0,56 (BOP n. 134 del 9/11/2026, art. 13) o data come 'in vigore'")
    if (ol["stato"], ol["approvazione_iniziale"], ol["bop"], ol["esenti_sotto_anni"], ol["giorni_osservazioni"]) != \
            ("approvazione_iniziale", "2026-10-29", {"numero": 134, "data": "2026-11-09"}, 3, 30):
        errori.append("Canarie: La Oliva, stato, date, esenzioni o giorni diversi dal testo letto")
    if "celebrado el 29 de octubre de 2026, acordó aprobar inicialmente" not in fr("bop_la_oliva") or "menores de 3 años" not in fr("bop_la_oliva") \
            or "TREINTA DÍAS HÁBILES" not in fr("bop_la_oliva"):
        errori.append("Canarie: La Oliva, frammenti senza approvazione iniziale, esenzione sotto i 3 anni o 30 giorni")
    P, M = reg["proposta_legge"], reg["mozione"]
    if (P["voti_si"], P["voti_no"]) != CN_ATTESI["voti"] or "sí, 25; no, 40; abstenciones, 0" not in fr("parcan_ppl") or P["dibattito"] != "2024-12-11" \
            or (P["tariffa_min"], P["tariffa_max"]) != (1.0, 3.5) or "desde el euro hasta los tres euros y medio" not in fr("parcan_ppl"):
        errori.append("Canarie: voto o tariffe proposte della PPL-0004 diversi dal Diario de Sesiones 61")
    if (M["voti_si"], M["voti_no"]) != CN_ATTESI["mozione"] or "sí, 24; no, 37" not in fr("parcan_mozione"):
        errori.append("Canarie: voto della mozione M-0039 diverso dal Diario de Sesiones 74")
    L = reg["leggi_in_corso"]
    codici = set(re.findall(r"11L/(?:DL|PL|PPL)-\d{4}", fr("parcan_leggi")))
    if codici != set(L["proposte"] + L["progetti"] + L["decreti_legge"]) or re.search(r"tur[ií]st|estancias|pernoctaci", fr("parcan_leggi"), re.I) or L["su_tassa_turistica"] != 0:
        errori.append("Canarie: elenco delle leggi in corso diverso dai frammenti letti, o una legge parla di turismo: rileggere parcan.es/leyes/")
    if reg["igic"]["aliquota_generale"] != CN_ATTESI["igic"] or "es el 7 por ciento" not in fr("boc_igic"):
        errori.append("Canarie: aliquota generale IGIC diversa dal 7 % (Decreto Legislativo 1/2025, art. 32.1)")
    got = {(s["id"], t["giorni"]): (t["tenerife"], t["altre_isole"], t["altri"]) for s in te["sentieri"] for t in s["tariffe"]}
    ft = fr("cabildo_teide")
    if got != CN_ATTESI["teide"] or te["dal"] != "2026-01-19" or "deberán abonar 6 euros, y el resto de personas usuarias, 15 euros" not in ft \
            or "3 euros para residentes en el resto de Canarias y de 6 euros para el resto de usuarios" not in ft \
            or "5 euros para residentes en el resto de las islas y 10 euros para el resto de visitantes" not in ft or "menores de 14 años" not in ft:
        errori.append("Canarie: tariffe dei sentieri del Teide diverse dall'avviso del Cabildo del 18/1/2026")
    if te["annunciato"]["importo"] is not None:
        errori.append("Canarie: importo per il parcheggio del Teide senza un atto ufficiale che lo dica")
    st = mg["stampa_annullamento"]
    if F[st["fonte"]]["tipo"] != "stampa" or st["sentenza_letta"] is not False or "nula de pleno derecho" not in fr("rtvc_mogan"):
        errori.append("Canarie: annullamento di Mogán non segnato come notizia di stampa (sentenza non letta)")
    ra = mg.get("ricerca_annullamento", {})
    if ra.get("avvisi_di_annullamento_o_abrogazione") != 0 or ra.get("fatta_il", "") < "2026-11-27" or "sentencias firmes que anulen una disposición general" not in fr("boe_ljca"):
        errori.append("Canarie: Mogán, ricerca dell'avviso di annullamento nel BOP mancante o con un avviso trovato: rileggere e riscrivere lo stato")
    if "sin necesidad de acuerdo plenario" not in fr("boe_trlhl"):
        errori.append("Canarie: La Oliva, frammento dell'art. 17.3 (approvazione definitiva senza nuovo voto) mancante")
    R = C["ricerca_bop"]
    if R["fatta_il"] > oggi_dati or [(x["bollettino"], x["data"]) for x in R["trovate"]] != [(153, "2024-12-18"), (30, "2025-03-10"), (134, "2026-11-09")]:
        errori.append("Canarie: risultati della ricerca nel BOP di Las Palmas diversi da quelli letti il 27/11/2026")
    # pagine
    sm = _sitemap()
    testi, frasi = {}, {}
    ammessi = {G.eur(v) for v in (0.15, 0.56, 1, 3.5, 3, 5, 6, 10, 15, 30, 20, 12, 2.10, 4.20, 7.84, 15.68, 1.12)}
    bal = D["mallorca"]
    ammessi |= {G.soldi_breve(t["valore"], "EUR") for t in bal["tariffe"]}
    for slug in CN_PAGINE:
        f = SITO / slug / "index.html"
        if not f.exists():
            errori.append(f"Canarie: pagina mancante {slug}")
            continue
        t = testi[slug] = f.read_text(encoding="utf-8")
        chiave = "hub" if slug == "canary-islands" else slug
        titolo = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        descr = unescape(re.search(r'<meta name="description" content="([^"]*)"', t).group(1))
        if len(descr) > 160 or not re.search(r"Checked \d{1,2} [A-Z][a-z]{2} 20\d\d\.$", descr):
            errori.append(f"Canarie: {slug}: descrizione oltre 160 caratteri o senza la data: {len(descr)}")
        if "«" in t or "»" in t:
            errori.append(f"Canarie: {slug}: virgolette « » (stile non britannico)")
        if len(titolo) > 70 or "tourist tax" not in titolo or str(G.ANNO) not in titolo or titolo != G.CN_TITOLI[chiave][0]:
            errori.append(f"Canarie: {slug}: titolo oltre 70 caratteri o senza 'tourist tax' e anno: {titolo}")
        h1 = unescape(re.sub(r"<[^>]+>", "", re.search(r"<h1>(.*?)</h1>", t, re.S).group(1)))
        if not h1.startswith("Is there a tourist tax in ") or not h1.endswith("?"):
            errori.append(f"Canarie: {slug}: l'H1 non è la domanda")
        r = re.search(r'<p class="risposta">(.*?)</p>', t, re.S)
        prima = unescape(r.group(1)).split(". ")[0] if r else ""
        r2 = re.search(r'<p class="risposta-seguito">(.*?)</p>', t, re.S)
        risposta_intera = unescape((r.group(1) if r else "") + " " + (r2.group(1) if r2 else ""))
        if not r2 or len(re.findall(r"(?<=[.)]) (?=[A-Z])", unescape(r.group(1) if r else ""))) > 2:
            errori.append(f"Canarie: {slug}: la risposta non è divisa in due paragrafi dopo la seconda frase")
        if not prima.startswith(CN_INIZIO[slug]) or f"checked on {G.CN_CHECK}" not in prima:
            errori.append(f"Canarie: {slug}: la prima frase non è la risposta con la data della lettura")
        corpo = _cn_main(t)
        for m in re.finditer(r'<p class="fonte[^"]*">(.*?)</p>', t, re.S):
            p = m.group(0)
            link = re.findall(r'href="([^"]+)"', p)
            stampa = [u for u in link if any(unescape(u) == x["url"] and x["tipo"] == "stampa" for x in F.values())]
            if not link or not re.search(r"(checked|read) on \d{1,2} [A-Z][a-z]+ 20\d\d", p):
                errori.append(f"Canarie: {slug}: riga di fonte senza link o senza data")
            if stampa and not p.startswith('<p class="fonte fonte-stampa">Press report, not an official source:'):
                errori.append(f"Canarie: {slug}: fonte di stampa non dichiarata come stampa")
            if (len(stampa) != len(link)) and stampa:
                errori.append(f"Canarie: {slug}: stampa e fonti ufficiali nella stessa riga")
        elenco = t[t.find("<h2>Sources</h2>"):]
        for k, x in F.items():
            if G.escape(x["url"]) in corpo and G.escape(x["url"]) not in elenco:
                errori.append(f"Canarie: {slug}: fonte usata ma non nell'elenco finale: {k}")
        if "rtvc.es" in t and "press report, not an official source" not in elenco:
            errori.append(f"Canarie: {slug}: la stampa nell'elenco finale non è dichiarata")
        for h2 in re.split(r"<h[23]>", corpo)[1:]:
            if re.search(r"€\d", h2) and 'class="fonte' not in h2 and "Questions" not in h2[:20] and not h2.startswith(("The other islands", "Island pages", "What other islands charge")):
                errori.append(f"Canarie: {slug}: sezione con un importo ma senza riga di fonte: {h2[:50]}")
        for v in set(re.findall(r"€\d+(?:\.\d+)?", unescape(re.sub(r"<[^>]+>", " ", corpo)))):
            if v not in ammessi:
                errori.append(f"Canarie: {slug}: importo {v} che non viene dai dati")
        if slug in ("canary-islands", "gran-canaria") and "may still be" not in risposta_intera:
            errori.append(f"Canarie: {slug}: la risposta non dice che la tassa di Mogán può essere ancora chiesta")
        faq_v = re.findall(r'<details class="faq"><summary>(.*?)</summary><p>(.*?)</p></details>', t, re.S)
        ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)]
        fp = next((x for x in ld if x.get("@type") == "FAQPage"), None)
        if not fp or len(faq_v) < 4 or [(unescape(q), unescape(a)) for q, a in faq_v] != [(x["name"], x["acceptedAnswer"]["text"]) for x in fp["mainEntity"]]:
            errori.append(f"Canarie: {slug}: FAQ visibili diverse dal JSON-LD o meno di 4")
        if f"{G.URL_SITO}/{slug}/" not in sm:
            errori.append(f"Canarie: {slug}: non nella sitemap")
        for altro in CN_PAGINE:
            if altro != slug and f'href="../{altro}/"' not in t:
                errori.append(f"Canarie: {slug}: manca il link a {altro}")
        for dest in ("mallorca", "country/spain"):
            if f'href="../{dest}/"' not in t:
                errori.append(f"Canarie: {slug}: manca il link a {dest}")
        if 'class="ad-slot"' not in t or "Not tax advice" not in t:
            errori.append(f"Canarie: {slug}: manca lo spazio pubblicitario o l'avviso")
        frasi[slug] = _cn_frasi(t)
        parole = {w for w in re.findall(r"[a-zà-ÿ0-9€.%]+", " ".join(frasi[slug]))}
        if len(parole) < CN_SOGLIA_PAROLE_UNICHE:
            errori.append(f"Canarie: {slug}: {len(parole)} parole uniche (soglia {CN_SOGLIA_PAROLE_UNICHE})")
    for slug, fs in frasi.items():
        altre = set().union(*(v for k, v in frasi.items() if k != slug))
        quota = len(fs & altre) / max(1, len(fs))
        if quota > CN_MAX_FRASI_COMUNI:
            errori.append(f"Canarie: {slug}: {quota:.0%} delle frasi è uguale a un'altra pagina delle Canarie (massimo {CN_MAX_FRASI_COMUNI:.0%})")
    for slug, atteso, mano in CN_ESEMPI:
        cifra = float(re.findall(r"€(\d+(?:\.\d+)?)", atteso)[-1])
        if abs(cifra - mano) > 0.005 or atteso not in testi.get(slug, ""):
            errori.append(f"Canarie: esempio a mano non trovato o sbagliato in {slug}: {atteso}")
    # link in entrata e pagine esistenti
    spagna = (SITO / "country" / "spain" / "index.html").read_text(encoding="utf-8")
    if 'href="../../canary-islands/"' not in spagna or any(f'href="../../{s}/"' not in spagna for s in CN_PAGINE[1:]):
        errori.append("Canarie: la pagina Spagna non linka le 5 pagine")
    for b in ("mallorca", "ibiza", "menorca", "formentera"):
        if 'href="../canary-islands/"' not in (SITO / b / "index.html").read_text(encoding="utf-8"):
            errori.append(f"Canarie: la pagina {b} non linka la pagina Canarie")
    home = (SITO / "index.html").read_text(encoding="utf-8")
    if any(f'<a href="{s}/">' not in home for s in CN_PAGINE):
        errori.append("Canarie: la home non elenca le 5 pagine")
    if 'href="../canary-islands/"' not in (SITO / "tourist-taxes-europe-2026" / "index.html").read_text(encoding="utf-8"):
        errori.append("Canarie: la pagina Europa non linka la pagina Canarie")
    about = G.MON.testo_visibile((SITO / "about" / "index.html").read_text(encoding="utf-8"))
    if re.search(r"Morocco and the Canary Islands", about):
        errori.append("Canarie: la pagina About dice ancora che le Canarie non sono pubblicate")
    return errori, {s: len({w for w in re.findall(r"[a-zà-ÿ0-9€.%]+", " ".join(f))}) for s, f in frasi.items()}, \
        {s: len(fs & set().union(*(v for k, v in frasi.items() if k != s))) / max(1, len(fs)) for s, fs in frasi.items()}


# 17. Hawaii, New York City, Manchester, Liverpool, Galles e pagina paese Regno Unito (27/11/2026). Fatti letti a mano il 27/11/2026 nei testi
# ufficiali (annunci 2025-03 e 2026-01 del Department of Taxation delle Hawaii, Act 96 SLH 2025, annuncio OTAT 2022-01 di Honolulu, pagina
# sulla county surcharge; pagina e modulo NYC-HTX 2026 del Department of Finance, TB-ST-331 e Publication 718 dello Stato di New York; sito e
# piano del Manchester Accommodation BID; avviso del voto e documento di novembre 2026 del Comune di Liverpool; testo della legge gallese su
# legislation.gov.uk e notizie del Comune di Cardiff (cardiffnewsroom.co.uk); comunicato GOV.UK del 4/11/2026), scritti qui una seconda volta: se
# dati/usa_regno_unito.json cambia senza una nuova lettura, il controllo si ferma.
UR_ATTESI = {
    "hawaii": {"tat_stato": 11.0, "tat_prima": 10.25, "dal": "2026-01-01", "fino_al": "2030-12-31", "tat_contea_max": 3.0, "get": 4.0, "get_contea": 0.5,
               "get_ricarico_max": 4.712, "giorni_transiente": 180},
    "nyc": {"vendite": 8.875, "albergo_pct": 5.875, "albergo_pct_dal": "2013-12-20", "per_stanza_min": 0.5, "per_stanza_max": 2.0, "unit_fee": 1.5,
            "esempio_ibo": {"prezzo": 200, "per_stanza": 2.0}, "residente_giorni_citta": 180, "residente_giorni_stato": 90},
    "manchester": {"importo": 1.0, "dal": "2023-04-01", "durata_anni": 5, "fine_mandato": "2028-03-31", "soglia_valore_catastale": 75000, "strutture": 83},
    "liverpool": {"importo": 2.0, "dal": "2025-06-01", "soglia_valore_catastale": 45000, "voti_si": 26, "voti_no": 18, "voti_nulli": 1, "affluenza_pct": 53, "paganti": 82,
                  "abid_dal": "2023-01-15"},
    "galles": {"alta": 1.30, "bassa": 0.75, "eta_adulto": 18, "notti_max": 31, "preavviso_mesi": 12, "date_ammesse": ["1 April", "1 October"], "assenso": "2025-09-18", "iva_pct": 20},
    "inghilterra": {"presentato": "2026-11-04", "legge": False, "tetto_sindaci_pct": 5, "sindaci": 10},
}
UR_FRAMMENTI = [  # (fonte, testo che deve essere fra i frammenti letti)
    ("hi_ann2601", "from 10.25 percent to 11 percent, shall be effective as of January 1, 2026"), ("hi_ann2601", "until December 31, 2030"),
    ("hi_ann2601", "until further notice"), ("hi_ann2503", "from 10.25% to 11.00%"), ("hi_act96", "[10.25] eleven per cent"),
    ("hi_schema", "not to exceed three per cent"), ("hon_otat", "the OTAT is levied at a rate of 3%"), ("hon_otat", "Ordinance No. 21-33"),
    ("hi_get", "City and County of Honolulu: 4.7120%"), ("hi_get", "County of Maui: 4.7120%"), ("hi_get", "County of Kauai: 4.7120%"),
    ("hi_tf962", "mandatory resort fees"), ("hi_tf962", "less than 180 consecutive days"), ("hi_tf962", "4% plus 0.5% county surcharge"),
    ("nyc_ibo", "first, a 5.875% tax on the total rent paid by the consumer; second, a daily room rate that ranges from $0.50 to $2.00 per day"),
    ("nyc_ibo", "($200 x 5.875%) + ($2.00 x 4)"), ("nyc_311", "rate of 5.875% went into effect on December 20, 2013"), ("nys_pub718", "*New York City 8⅞ 8081"),
    ("nys_tb331", "unit fee of $1.50 per unit per day"), ("nys_tb331", "at least 90 consecutive days"), ("nys_tb331", "at least 180 consecutive days"),
    ("nys_tb331", "is not subject to state and local sales taxes"), ("nys_pub848", "Bronx, Kings, New York, Queens and Richmond"),
    ("man_abid", "a supplementary £1 (plus VAT, where applicable) Charge per room/unit per night"), ("man_abid", "since April 2023"),
    ("man_zona", "rateable value of £75,000 or more"), ("man_zona", "As of September 2026, 83 accommodation establishments"),
    ("man_piano", "commence on 1st April 2023, lasting for a period of 5 years"), ("man_piano", "regardless of the trip purpose"),
    ("liv_voto", "a £2 per night levy would be payable per occupied room"), ("liv_voto", "rateable value of £45,000 or more"),
    ("liv_voto", "Votes in favour: 26 Votes against: 18 Invalid votes: 1"), ("liv_voto", "take effect from 1st June 2025"), ("liv_notizia", "53% turnout"),
    ("liv_politica", "place a £2 per night levy on occupied units"), ("liv_politica", "under both the OVL and a BID"),
    ("liv_bid", "82 BID Levy Paying Businesses"), ("liv_bid", "15th January, 2023"),
    ("car_approvazione", "approved by Full Council"), ("car_approvazione", "to charge a small fee to overnight visitors from April 2027"),
    ("car_approvazione", "£1.30 per person per night for most accommodation types 75p per person per night for campsites and shared rooms"),
    ("car_approvazione", "62% in favour , 33% opposed"), ("car_approvazione", "£3.5 million each year"), ("car_approvazione", "standard rate VAT (20% in the UK)"),
    ("car_approvazione", "more than 31 nights in a single booking"), ("car_intesa", "will be introduced in Cardiff in April 2027"),
    ("gal_testo", "(a) the lower rate is £0.75, and (b) the higher rate is £1.30"), ("gal_testo", "must be either 1 April or 1 October"),
    ("gal_testo", "period of 12 months starting with the day on which the notice was published"), ("gal_testo", "aged under 18"),
    ("gal_testo", "more than 31 nights"), ("gal_testo", "[18 September 2025]"), ("gal_atto", "2025 asc 5"),
    ("uk_legge", "introduced in the House of Commons today"), ("uk_legge", "no higher than 5%"), ("uk_risposta", "percentage of the accommodation cost"),
]
UR_DOMINI = ("https://portal.311.nyc.gov/", "https://www.ibo.nyc.gov/", "https://www.cardiffnewsroom.co.uk/", "https://files.hawaii.gov/tax/", "https://tax.hawaii.gov/", "https://data.capitol.hawaii.gov/", "https://www.honolulu.gov/bfs/",
             "https://www.tax.ny.gov/", "https://manchesterabid.com/", "https://manchester-abid.files.svdcdn.com/", "https://liverpool.gov.uk/",
             "https://liverpoolexpress.co.uk/", "https://liverpoolbidcompany.com/", "https://www.legislation.gov.uk/", "https://www.gov.uk/",
             "https://assets.publishing.service.gov.uk/")
UR_VIETATI = ("https://www.nyc.gov/", "https://www.gov.wales/")  # 27/11/2026: 403 a una richiesta senza User-Agent di browser = blocco: non sono fonti
UR_PAGINE = {"hawaii": "usa/hawaii", "nyc": "usa/new-york-city", "manchester": "manchester", "liverpool": "liverpool", "wales": "wales"}
UR_INIZIO = {  # inizio esatto della risposta, pagina per pagina
    "hawaii": "Short answer: on Oahu, taxes add up to 18.712% to a hotel or vacation rental bill in",
    "nyc": "Short answer: 14.75% of the room rate plus up to $3.50 per room per night",
    "manchester": "Short answer: yes, in practice: larger hotels and serviced apartments in central Manchester and Salford add a City Visitor Charge of £1 per room per night",
    "liverpool": "Short answer: yes, in practice: larger hotels and serviced apartments in Liverpool pay a levy of £2 per occupied room per night",
    "wales": "Short answer: not yet: the Welsh visitor levy cannot be charged anywhere before April 2027",
}
UR_PAROLA = {"hawaii": "tourist tax", "nyc": "hotel tax", "manchester": "tourist tax", "liverpool": "tourist tax", "wales": "tourism tax"}
UR_ESEMPI = [  # (pagina, testo atteso, calcolo a mano)
    ("hawaii", "$165.00 + $45.00 + $70.68 = <strong>$280.68</strong>", 1500 * 0.11 + 1500 * 0.03 + 70.68),      # 1.500 × 4,712 % = 70,68
    ("hawaii", "$189.75 + $51.75 + $81.28 = <strong>$322.78</strong>", 189.75 + 51.75 + 81.28),                   # 1.725 × 11 %, × 3 %, × 4,712 % = 81,282
    ("hawaii", "carried $11.25 less state tax", 1500 * 0.0075),
    ("nyc", "Total taxes and fees: <strong>$121.12</strong>", 66.56 + 44.06 + 6 + 4.5),                             # 750 × 8,875 % = 66,5625; × 5,875 % = 44,0625
    ("nyc", "$71.00 sales tax + $47.00 hotel tax + 4 × $2.00 = $8.00 + 4 × $1.50 = $6.00, in all <strong>$132.00</strong>", 71 + 47 + 8 + 6),  # 800 × 8,875 % = 71; × 5,875 % = 47
    ("nyc", "that comes to $40.38 a night", 22.19 + 14.69 + 2 + 1.5),                                               # 250 × 8,875 % = 22,1875; × 5,875 % = 14,6875
    ("manchester", "1 × 3 × £1 = <strong>£3</strong>", 3), ("manchester", "2 × 4 × £1 = <strong>£8</strong>", 8), ("manchester", "1 × 2 × £1 = <strong>£2</strong>", 2),
    ("liverpool", "1 × 2 × £2 = <strong>£4</strong>", 4), ("liverpool", "2 × 3 × £2 = <strong>£12</strong>", 12), ("liverpool", "1 × 7 × £2 = <strong>£14</strong>", 14),
    ("wales", "2 × 3 × £1.30 = <strong>£7.80</strong>", 7.80), ("wales", "4 × 3 × £1.30 = <strong>£15.60</strong>", 15.60), ("wales", "2 × 2 × 75p = <strong>£3</strong>", 3),
]
UR_AMMESSI = {  # ogni importo scritto nel corpo delle pagine: dai dati o da un esempio a mano
    "hawaii": {"$300", "$1,500", "$165.00", "$45.00", "$70.68", "$280.68", "$45", "$345", "$189.75", "$51.75", "$81.28", "$322.78", "$1,725", "$11.25",
               "$3.50"},   # $3.50: riga della griglia verso la pagina New York
    "nyc": {"$3.50", "$0.50", "$2.00", "$1.50", "$250", "$40.38", "$200", "$750", "$66.56", "$44.06", "$6.00", "$4.50", "$121.12", "$71.00", "$47.00", "$8.00",
            "$132.00", "$800"},
    "manchester": {"£1", "£75,000", "£3", "£8", "£2", "£6", "£1.30"},
    "liverpool": {"£2", "£45,000", "£4", "£12", "£14", "£18", "£1", "£1.30"},   # £18m: frase del sindaco nel comunicato GOV.UK del 4/11/2026
    "wales": {"£1.30", "75p", "£7.80", "£15.60", "£3", "£1", "£2", "£3.5"},   # £3.5 million: gettito stimato dal Comune di Cardiff
}
UR_SENZA_FONTE = ("Questions", "Other US hotel taxes", "Other UK pages", "What we could not read")  # sezioni senza cifre proprie
UR_SOGLIA_PAROLE_UNICHE = 110
UR_MAX_FRASI_COMUNI = 0.40


def controlla_usa_regno_unito():
    """17. Fonti (domini ufficiali, HTTP 200, data, impronta del file o frammenti letti, nessuna stampa); fatti = attesi letti a mano = frammenti;
    esempi a mano; 5 pagine: titolo ≤ 70, H1 = domanda, risposta con la data divisa dopo la seconda frase, descrizione ≤ 160 con la data, stile
    delle virgolette e delle date, ogni fonte linkata con la data, importi = dati, FAQ = JSON-LD, sitemap, link; pagina paese Regno Unito;
    parole uniche e frasi in comune (anche con Cardiff, Edimburgo, la pagina paese e la sezione USA)."""
    errori = []
    U, F = G.UR, G.UR_F
    for k, f in F.items():
        if f["tipo"] != "ufficiale" or not f["url"].startswith(UR_DOMINI):
            errori.append(f"USA/UK: fonte non ufficiale o su un dominio non atteso: {k} {f['url']}")
        if f["http"] != 200 or f.get("controllato_il", "") < "2026-11-27" or not f.get("frammenti") or not f.get("breve") or not f.get("ente"):
            errori.append(f"USA/UK: fonte non letta, senza data, senza frammenti o senza nome breve: {k}")
        if (f["formato"] == "PDF") != (f["impronta_di"] == "file") or f["impronta_di"] not in ("file", "frammenti"):
            errori.append(f"USA/UK: tipo di impronta sbagliato: {k}")
        if f["impronta_di"] == "file" and not re.fullmatch(r"sha256:[0-9a-f]{64}", f.get("impronta", "")):
            errori.append(f"USA/UK: PDF senza impronta sha256: {k}")
    for sez, attesi in UR_ATTESI.items():
        for campo, v in attesi.items():
            if U[sez].get(campo) != v:
                errori.append(f"USA/UK: {sez}.{campo} = {U[sez].get(campo)!r}, letto a mano {v!r}")
    for k, pezzo in UR_FRAMMENTI:
        if pezzo not in " ".join(F.get(k, {}).get("frammenti", [])):
            errori.append(f"USA/UK: il frammento letto non è più nei dati: {k}: {pezzo}")
    H = U["hawaii"]
    oahu = [c for c in H["contee"] if c["id"] == "honolulu"]
    if len(H["contee"]) != 4 or not oahu or (oahu[0]["tat_contea"], oahu[0]["letta"], oahu[0]["dal"], oahu[0]["fonte"]) != (3.0, True, "2021-12-14", "hon_otat"):
        errori.append("USA/UK: Hawaii, contea di Honolulu diversa dall'annuncio OTAT 2022-01 (3 % dal 14/12/2021)")
    for c in H["contee"]:
        if c["id"] != "honolulu" and (c["letta"] is not False or c["tat_contea"] is not None):
            errori.append(f"USA/UK: Hawaii, contea {c['id']}: un'aliquota senza una fonte letta")
    if H["crociere"]["stato"] != "sospesa" or H["crociere"]["ingiunzione"] != "2025-12-31" or H["crociere"]["annuncio"] != "2026-01-02":
        errori.append("USA/UK: Hawaii, stato delle crociere diverso dall'annuncio 2026-01")
    if abs(G.hi_tot() - 18.712) > 1e-9 or abs(G.ny_pct() - 14.75) > 1e-9 or abs(G.ny_fisso() - 3.5) > 1e-9:
        errori.append("USA/UK: totali (18,712 % a Oahu; 14,75 % + 3,50 $ a New York) diversi dal calcolo a mano")
    W = U["galles"]
    c0 = W["consigli"]
    if len(c0) != 1 or (c0[0]["nome"], c0[0]["dal"], c0[0]["approvato"], c0[0]["favorevoli_pct"], c0[0]["contrari_pct"], c0[0]["gettito_mln"]) != \
            ("Cardiff", "2027-04-01", "2026-03-26", 62, 33, 3.5):
        errori.append("USA/UK: Galles, Cardiff diverso dalla notizia del Comune del 26/3/2026 (aprile 2027; per legge l'inizio è il 1° aprile o il 1° ottobre)")
    card = D["cardiff"]
    if sorted(t["valore"] for t in card["tariffe"]) != [W["bassa"], W["alta"]] or min(t["dal"] for t in card["tariffe"]) != c0[0]["dal"]:
        errori.append("USA/UK: Galles, tariffe o data diverse dalla pagina Cardiff (dati/destinazioni.json)")
    for k, f in F.items():
        if f["url"].startswith(UR_VIETATI):
            errori.append(f"USA/UK: fonte su un sito che blocca le richieste normali (non è una fonte letta): {k}")
    # pagine
    sm = _sitemap()
    testi, frasi = {}, {}
    for k, perc in UR_PAGINE.items():
        f = SITO / perc / "index.html"
        if not f.exists():
            errori.append(f"USA/UK: pagina mancante {perc}")
            continue
        t = testi[k] = f.read_text(encoding="utf-8")
        us = k in G.UR_US
        rel = "../" * (perc.count("/") + 1)
        titolo = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        descr = unescape(re.search(r'<meta name="description" content="([^"]*)"', t).group(1))
        data_d = r"Checked [A-Z][a-z]{2} \d{1,2}, 20\d\d\.$" if us else r"Checked \d{1,2} [A-Z][a-z]{2} 20\d\d\.$"
        if len(descr) > 160 or not re.search(data_d, descr):
            errori.append(f"USA/UK: {k}: descrizione oltre 160 caratteri o senza la data: {len(descr)}")
        if len(titolo) > 70 or UR_PAROLA[k] not in titolo or str(G.ANNO) not in titolo or titolo != G.UR_PAG[k][1]:
            errori.append(f"USA/UK: {k}: titolo oltre 70 caratteri o senza la parola cercata e l'anno: {titolo}")
        h1 = unescape(re.sub(r"<[^>]+>", "", re.search(r"<h1>(.*?)</h1>", t, re.S).group(1)))
        if not h1.startswith(("Is there a ", "How much is the ")) or not h1.endswith("?"):
            errori.append(f"USA/UK: {k}: l'H1 non è la domanda")
        r = re.search(r'<p class="risposta">(.*?)</p>', t, re.S)
        r2_ = re.search(r'<p class="risposta-seguito">(.*?)</p>', t, re.S)
        prima_p = unescape(r.group(1)) if r else ""
        data_p = r"checked on [A-Z][a-z]+ \d{1,2}, 20\d\d" if us else r"checked on \d{1,2} [A-Z][a-z]+ 20\d\d"
        if not prima_p.startswith(UR_INIZIO[k]) or not re.search(data_p, prima_p):
            errori.append(f"USA/UK: {k}: la prima frase non è la risposta con la data della lettura")
        if not r2_ or len(re.findall(r"(?<=[.)”]) (?=[A-Z])", prima_p)) > 1:
            errori.append(f"USA/UK: {k}: la risposta non è divisa in due paragrafi dopo la seconda frase")
        if any(v in t for v in UR_VIETATI):
            errori.append(f"USA/UK: {k}: link a un sito non letto (nyc.gov o gov.wales)")
        if "«" in t or "»" in t or (us and "‘" in t) or (not us and ("“" in t or "”" in t)):
            errori.append(f"USA/UK: {k}: virgolette nello stile sbagliato")
        corpo = _cn_main(t)
        testo_corpo = unescape(re.sub(r"<[^>]+>", " ", corpo))
        if us and re.search(r"\b\d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December) 20\d\d", testo_corpo):
            errori.append(f"USA/UK: {k}: una data in stile britannico su una pagina americana")
        if not us and re.search(r"\b(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, 20\d\d", testo_corpo):
            errori.append(f"USA/UK: {k}: una data in stile americano su una pagina britannica")
        for m in re.finditer(r'<p class="fonte[^"]*">(.*?)</p>', t, re.S):
            p = m.group(0)
            if not re.findall(r'href="([^"]+)"', p) or not re.search(data_p, p):
                errori.append(f"USA/UK: {k}: riga di fonte senza link o senza data")
        elenco = t[t.find("<h2>Sources</h2>"):]
        for kk, x in F.items():
            if G.escape(x["url"]) in corpo and G.escape(x["url"]) not in elenco:
                errori.append(f"USA/UK: {k}: fonte usata ma non nell'elenco finale: {kk}")
        for h2 in re.split(r"<h2>", corpo)[1:]:
            if re.search(r"[$£]\d|\d%", h2) and 'class="fonte' not in h2 and not h2.startswith(UR_SENZA_FONTE):
                errori.append(f"USA/UK: {k}: sezione con una cifra ma senza riga di fonte: {h2[:50]}")
        for v in set(re.findall(r"[$£]\d[\d,]*(?:\.\d+)?|\b\d+p\b", testo_corpo)):
            if v not in UR_AMMESSI[k]:
                errori.append(f"USA/UK: {k}: importo {v} che non viene dai dati o da un esempio a mano")
        faq_v = re.findall(r'<details class="faq"><summary>(.*?)</summary><p>(.*?)</p></details>', t, re.S)
        ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)]
        fp = next((x for x in ld if x.get("@type") == "FAQPage"), None)
        if not fp or len(faq_v) < 4 or [(unescape(q), unescape(a)) for q, a in faq_v] != [(x["name"], x["acceptedAnswer"]["text"]) for x in fp["mainEntity"]]:
            errori.append(f"USA/UK: {k}: FAQ visibili diverse dal JSON-LD o meno di 4")
        if f"{G.URL_SITO}/{perc}/" not in sm:
            errori.append(f"USA/UK: {k}: non nella sitemap")
        attesi_link = ["usa/", "usa/florida/", "usa/texas/", "usa/hawaii/" if k == "nyc" else "usa/new-york-city/"] if us else \
            [x + "/" for x in ("manchester", "liverpool", "wales", "cardiff", "edinburgh", "country/united-kingdom") if x != k]
        for dest in attesi_link:
            if f'href="{rel}{dest}"' not in t:
                errori.append(f"USA/UK: {k}: manca il link a {dest}")
        if 'class="ad-slot"' not in t or "Not tax advice" not in t:
            errori.append(f"USA/UK: {k}: manca lo spazio pubblicitario o l'avviso")
        frasi[k] = _cn_frasi(t)
        parole = {w for w in re.findall(r"[a-zà-ÿ0-9€$£.%]+", " ".join(frasi[k]))}
        if len(parole) < UR_SOGLIA_PAROLE_UNICHE:
            errori.append(f"USA/UK: {k}: {len(parole)} parole uniche (soglia {UR_SOGLIA_PAROLE_UNICHE})")
    if "rate not read" not in testi.get("hawaii", "") or testi.get("hawaii", "").count("At most 3%") < 4:
        errori.append("USA/UK: Hawaii: la pagina non dice che l'aliquota di Maui, Hawaii e Kauai non è stata letta")
    if "is not law yet" not in testi.get("manchester", "") or "not law" not in testi.get("liverpool", ""):
        errori.append("USA/UK: Manchester o Liverpool: la pagina non dice che il disegno di legge non è legge")
    if "this table is not that list" not in testi.get("wales", "") or "we cannot say that no other council has decided" not in testi.get("wales", ""):
        errori.append("USA/UK: Galles: la pagina non dice che l'elenco ufficiale dei consigli non è stato letto")
    if "we could not read the bands" not in testi.get("nyc", "") or "plus up to" not in testi.get("nyc", ""):
        errori.append("USA/UK: New York: la pagina non dice che le fasce della parte giornaliera non sono state lette o dà il totale come completo")
    vicine = {p: _cn_frasi((SITO / p / "index.html").read_text(encoding="utf-8")) for p in ("cardiff", "edinburgh", "country/united-kingdom", "usa", "usa/florida", "usa/texas")}
    for k, fs in frasi.items():
        altre = set().union(*(v for kk, v in frasi.items() if kk != k), *vicine.values())
        quota = len(fs & altre) / max(1, len(fs))
        if quota > UR_MAX_FRASI_COMUNI:
            errori.append(f"USA/UK: {k}: {quota:.0%} delle frasi è uguale a un'altra pagina (massimo {UR_MAX_FRASI_COMUNI:.0%})")
    for k, atteso, mano in UR_ESEMPI:
        cifra = float(re.findall(r"[$£](\d[\d,]*(?:\.\d+)?)", atteso)[-1].replace(",", ""))
        if abs(cifra - mano) > 0.005 or atteso not in testi.get(k, ""):
            errori.append(f"USA/UK: esempio a mano non trovato o sbagliato in {k}: {atteso}")
    # pagina paese Regno Unito e link in entrata
    uk = (SITO / "country" / "united-kingdom" / "index.html").read_text(encoding="utf-8")
    tit_uk = unescape(re.search(r"<title>(.*?)</title>", uk).group(1))
    r_uk = re.search(r'<p class="risposta">(.*?)</p>', uk, re.S)
    if not tit_uk.startswith(f"Tourist tax UK {G.ANNO}: ") or len(tit_uk) > 70 or not r_uk or \
            not unescape(r_uk.group(1)).startswith(f"The UK has no national tourist tax in {G.ANNO}.") or "is not law yet (checked on" not in r_uk.group(1) or "https://www.gov.wales" in uk or 'class="card callout uk-box"' in uk:
        errori.append("USA/UK: pagina paese Regno Unito: titolo o prima frase diversi dal piano («tourist tax uk»)")
    for p, livello in (("country/united-kingdom", "../../"), ("cardiff", "../"), ("edinburgh", "../")):
        tt = (SITO / p / "index.html").read_text(encoding="utf-8")
        if any(f'href="{livello}{x}/"' not in tt for x in ("manchester", "liverpool", "wales")):
            errori.append(f"USA/UK: la pagina {p} non linka Manchester, Liverpool e Galles")
    # revisione del 27/11/2026: la pagina Cardiff e la voce Cardiff dei cambi 2027 hanno solo fonti lette con una richiesta normale
    # (legislation.gov.uk, cardiffnewsroom.co.uk); nessun link a gov.wales; la pagina paese ha le righe di Manchester, Liverpool e Galles
    for p in ("cardiff", "tourist-tax-changes-2027", "tourist-taxes-europe-2026", "about", "country/united-kingdom"):
        if any(v in (SITO / p / "index.html").read_text(encoding="utf-8") for v in UR_VIETATI):
            errori.append(f"USA/UK: la pagina {p} linka un sito non letto (nyc.gov o gov.wales)")
    if any(not x["url"].startswith(("https://www.legislation.gov.uk/", "https://www.cardiffnewsroom.co.uk/")) or x["controllato_il"] < "2026-11-27" for x in card["fonti"]):
        errori.append("USA/UK: Cardiff: una fonte non letta con una richiesta normale o con la data vecchia")
    if "Whitbread" in testi.get("liverpool", "") or "liv_ricorso" in F or any("28 September 2026" not in testi.get(k, "") for k in ("wales",)):
        errori.append("USA/UK: Liverpool cita ancora il ricorso senza fonte, o il Galles non dà la data delle prenotazioni (28/9/2026)")
    if uk.count("<tr><td>") < 5 or "United Kingdom<small>5 destination pages</small>" not in (SITO / "index.html").read_text(encoding="utf-8"):
        errori.append("USA/UK: pagina paese Regno Unito senza le righe di Manchester, Liverpool e Galles, o conteggio sbagliato nella home")
    hub = (SITO / "usa" / "index.html").read_text(encoding="utf-8")
    if 'href="../usa/hawaii/"' not in hub or 'href="../usa/new-york-city/"' not in hub:
        errori.append("USA/UK: la pagina USA non linka Hawaii e New York City")
    home = (SITO / "index.html").read_text(encoding="utf-8")
    if any(f'<a href="{p}/">' not in home for p in UR_PAGINE.values()):
        errori.append("USA/UK: la home non elenca le 5 pagine")
    eur = (SITO / "tourist-taxes-europe-2026" / "index.html").read_text(encoding="utf-8")
    if any(f'href="../{x}/"' not in eur for x in ("manchester", "liverpool", "wales")):
        errori.append("USA/UK: la pagina Europa non linka Manchester, Liverpool e Galles")
    conta = lambda f: len({w for w in re.findall(r"[a-zà-ÿ0-9€$£.%]+", " ".join(f))})
    return errori, {k: conta(f) for k, f in frasi.items()}, \
        {k: len(fs & set().union(*(v for kk, v in frasi.items() if kk != k), *vicine.values())) / max(1, len(fs)) for k, fs in frasi.items()}


def voce_futura_nel_titolo(titolo, attese, oggi):
    fut = [x for x in attese if x[0] > oggi]
    return bool(fut) and G.soldi(fut[0][1], "MXN") in titolo


def main():
    errori = controlla_esempi()
    print(f"Esempi a mano: {len(ESEMPI)} controllati, {len([e for e in errori if e.startswith('ESEMPIO')])} sbagliati")
    casi = [[e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8], e[10] if len(e) > 10 else ""] for e in ESEMPI] + casi_casuali()
    ej = controlla_js(casi)
    print(f"Confronto JS/Python: {len(casi)} casi, {len(ej)} differenze")
    el, n = controlla_link()
    print(f"Link interni: {n} controllati, {len(el)} rotti")
    ef, np_ = controlla_fonti()
    print(f"Pagine con fonte e data: {np_ - len(ef)}/{np_}")
    ea, na = controlla_altri_siti()
    print(f"Blocco \"Other useful tools for your trip\" ({len(G.ALTRI_SITI)} link) in {na} pagine indicizzabili: {len(ea)} errori")
    ei = controlla_indexnow()
    print(f"File chiave IndexNow {G.CHIAVE_INDEXNOW}.txt in sito/ (contenuto giusto, fuori dalla sitemap): {len(ei)} errori")
    e7 = controlla_pagina_2027()
    print(f"Pagina tourist-tax-changes-2027/ ({len(G.CAMBI['voci'])} voci, sitemap, link, fonti, FAQPage): {len(e7)} errori")
    en = controlla_nuove_destinazioni()
    print(f"Destinazioni nuove ({', '.join(NUOVE_DEST)}): {len(en)} errori")
    et = controlla_titoli()
    print(f"Titoli, descrizioni e risposte dirette di {len(G.DEST)} destinazioni: {len(et)} errori")
    ex = controlla_messico()
    print(f"Sezione Messico ({len(MX_SLUG)} pagine, Visitax = 2,50 × UMA ricalcolato, titoli, FAQ, avviso sito ufficiale, DiscoverCars): {len(ex)} errori")
    ejp = controlla_giappone()
    print(f"Giappone, rimborso dal 1/11/2026 ({len(ESEMPI_JP)} esempi a mano, frazioni, JS, sitemap, titolo, prima frase, fonti, FAQ, link): {len(ejp)} errori")
    ejt = controlla_giappone_tasse()
    print(f"Giappone, tasse di soggiorno ({len(G.JT['enti'])} enti = elenco MIC, {len(ESEMPI_JT)} esempi a mano, ricalcolo indipendente, JS, "
          f"5 pagine esistenti, {sum(1 for e in G.JT['enti'] if e['pagina'].startswith(G.JT_HUB))} pagine, riassunto, 2027): {len(ejt)} errori")
    ebe = controlla_belgio()
    print(f"Belgio (Bruxelles, Gand, Bruges: fonti, {len(ESEMPI_BE)} esempi a mano, titoli, prima frase, Anversa, Europa, cambi 2028-2029): {len(ebe)} errori")
    esn = controlla_santiago_napoli()
    print(f"Santiago de Compostela e Napoli (fonti con impronta e data, tariffe = fonti, {len(ESEMPI_SN)} esempi a mano, titoli, prima frase, "
          f"Anno Santo 2027 e America's Cup 2027, sitemap, paese, Europa): {len(esn)} errori")
    ees = controlla_spagna()
    print(f"Spagna, licenza per affitti turistici (sentenze BOE, {len(G.ES['fonti'])} fonti con impronta e data, conteggi = esempi a mano, nessun dato personale, "
          f"{2 + len(G.ES['regioni']) + len(G.ES['comuni']) - 1} pagine, titoli, prima frase, FAQ, regole regionali): {len(ees)} errori")
    eus = controlla_usa()
    print(f"USA, Florida e Texas ({len(G.US['fonti'])} fonti con impronta e data, aliquote = file riscaricati e riletti = {len(ESEMPI_US_FL) + len(ESEMPI_US_TX)} "
          f"esempi a mano, {len(ESEMPI_US_CALC)} calcoli a mano, JS = Python, {3 + sum(len(v) for v in G.US['pagine'].values())} pagine, titoli, prima frase, "
          f"FAQ = JSON-LD, sitemap, link): {len(eus)} errori")
    ecn, pu, dop = controlla_canarie()
    print(f"Canarie ({len(G.CN_F)} fonti con data e frammenti letti, fatti = letti a mano = frammenti, {len(CN_ESEMPI)} esempi a mano, 5 pagine: titolo, domanda, "
          f"risposta con data, fonti linkate, stampa dichiarata, importi = dati, FAQ = JSON-LD, sitemap, link; parole uniche "
          f"{min(pu.values()) if pu else 0}-{max(pu.values()) if pu else 0} (soglia {CN_SOGLIA_PAROLE_UNICHE}), frasi in comune fino al {max(dop.values()) if dop else 0:.0%}): {len(ecn)} errori")
    eur_, pu17, dop17 = controlla_usa_regno_unito()
    print(f"Hawaii, New York City, Manchester, Liverpool, Galles ({len(G.UR_F)} fonti con data e frammenti letti, fatti = letti a mano = frammenti, {len(UR_ESEMPI)} esempi a mano, "
          f"5 pagine: titolo, domanda, risposta con data, fonti linkate, importi = dati, FAQ = JSON-LD, sitemap, link, pagina paese Regno Unito; parole uniche "
          f"{min(pu17.values()) if pu17 else 0}-{max(pu17.values()) if pu17 else 0} (soglia {UR_SOGLIA_PAROLE_UNICHE}), frasi in comune fino al {max(dop17.values()) if dop17 else 0:.0%}): {len(eur_)} errori")
    print("  parole uniche: " + ", ".join(f"{k} {v}" for k, v in pu17.items()) + "; frasi in comune: " + ", ".join(f"{k} {v:.0%}" for k, v in dop17.items()))
    em, im = G.MON.controlla_sito(G.SITO_ID, SITO)  # controllo comune di monetizzazione (monetizzazione.py)
    print(G.MON.riepilogo(G.SITO_ID, im, em))
    tutti = errori + ej + el + ef + ea + ei + e7 + en + et + ex + ejp + ejt + ebe + esn + ees + eus + ecn + eur_ + em
    for e in tutti[:40]:
        print("  -", e)
    if tutti:
        sys.exit(1)
    print("Tutto a posto.")


if __name__ == "__main__":
    main()
