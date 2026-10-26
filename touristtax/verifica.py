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
    tutti = errori + ej + el + ef + ea + ei
    for e in tutti[:40]:
        print("  -", e)
    if tutti:
        sys.exit(1)
    print("Tutto a posto.")


if __name__ == "__main__":
    main()
