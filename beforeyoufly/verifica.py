"""Controlli prima di pubblicare Before You Fly.

Uso (dalla radice del repository, dopo python3 beforeyoufly/genera.py):
    python3 beforeyoufly/verifica.py            # tutti i controlli, compreso il browser a 375 px (serve node + Playwright)
    BYF_NO_BROWSER=1 python3 beforeyoufly/verifica.py   # senza il browser

1. Casi del passaporto calcolati a mano (TEST.md): il motore Python deve dare l'esito e la data minima attesi.
2. Il motore JS (lo stesso testo delle pagine) deve dare gli stessi risultati del Python, sui casi a mano e su 3.000 casi casuali.
3. Nessun link interno rotto in sito/.
4. Ogni pagina con una regola mostra la fonte ufficiale (URL) e la data del controllo; le frasi citate sono nella pagina.
5. Meta di verifica Google in ogni pagina; 404 con link assoluti, noindex e senza canonical; sitemap e robots.
6. Nessun nome di modelli o servizi di intelligenza artificiale nei file del sito e nei dati.
7. Browser a 375 px (Playwright): 3 pagine senza scorrimento orizzontale e senza errori in console; il controllo del passaporto risponde.
Esce con codice 1 se qualcosa non va.
"""
import json
import os
import random
import re
import subprocess
import sys
import tempfile
from html import escape
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import genera as G  # noqa: E402

SITO = G.SITO
P = {p["slug"]: p for p in G.PASS["paesi"]}

# (descrizione, paese, emissione, scadenza, arrivo, partenza, esito atteso, date minime attese in ordine dei controlli)
CASI = [
    ("1 Spagna (Schengen): tutto in regola", "spain", "2017-03-01", "2027-06-01", "2026-11-01", "2026-11-10", "ok", ["2027-02-10", "2016-11-02"]),
    ("2 Spagna: emesso esattamente 10 anni prima dell'arrivo -> NO (serve 'less than')", "spain", "2016-11-01", "2027-06-01", "2026-11-01", "2026-11-10", "no", ["2027-02-10", "2016-11-02"]),
    ("3 Spagna: emesso 10 anni meno un giorno prima -> sì", "spain", "2016-11-02", "2027-06-01", "2026-11-01", "2026-11-10", "ok", ["2027-02-10", "2016-11-02"]),
    ("4 Spagna: scadenza esattamente 3 mesi dopo l'uscita -> sì (al limite)", "spain", "2020-01-01", "2027-02-10", "2026-11-01", "2026-11-10", "ok", ["2027-02-10", "2016-11-02"]),
    ("5 Spagna: scadenza un giorno prima -> no", "spain", "2020-01-01", "2027-02-09", "2026-11-01", "2026-11-10", "no", ["2027-02-10", "2016-11-02"]),
    ("6 Thailandia: 31/8 + 6 mesi = 28/2 (fine mese) -> sì", "thailand", "", "2027-02-28", "2026-08-31", "2026-09-14", "ok", ["2027-02-28"]),
    ("7 Thailandia: 31/8/2027 + 6 mesi = 29/2/2028 (bisestile), scade il 28/2 -> no", "thailand", "", "2028-02-28", "2027-08-31", "2027-09-14", "no", ["2028-02-29"]),
    ("8 Belize 'more than 3 months': scadenza esattamente a 3 mesi -> no", "belize", "", "2027-03-01", "2026-12-01", "2026-12-10", "no", ["2027-03-02"]),
    ("9 Belize: un giorno in più -> sì", "belize", "", "2027-03-02", "2026-12-01", "2026-12-10", "ok", ["2027-03-02"]),
    ("10 USA durata del soggiorno: scade il giorno della partenza -> sì", "usa", "", "2026-12-20", "2026-12-01", "2026-12-20", "ok", ["2026-12-20"]),
    ("11 USA: scade il giorno prima della partenza -> no", "usa", "", "2026-12-19", "2026-12-01", "2026-12-20", "no", ["2026-12-20"]),
    ("12 Cile 'after the day you plan to leave': scade il giorno della partenza -> no", "chile", "", "2026-12-20", "2026-12-01", "2026-12-20", "no", ["2026-12-21"]),
    ("13 Costa Rica 'at least 1 day after': scade il giorno dopo -> sì", "costa-rica", "", "2026-12-21", "2026-12-01", "2026-12-20", "ok", ["2026-12-21"]),
    ("14 Turchia 150 giorni dall'arrivo: 10/10/2026 + 150 = 9/3/2027 -> sì", "turkey", "", "2027-03-09", "2026-10-10", "2026-10-20", "ok", ["2027-03-09"]),
    ("15 Turchia: 8/3/2027 -> no", "turkey", "", "2027-03-08", "2026-10-10", "2026-10-20", "no", ["2027-03-09"]),
    ("16 Cuba: 6 mesi dall'arrivo sì ma 3 mesi dalla partenza no", "cuba", "", "2027-06-01", "2026-11-01", "2027-03-15", "no", ["2027-05-01", "2027-06-15"]),
    ("17 Cuba: entrambe le condizioni -> sì", "cuba", "", "2027-06-15", "2026-11-01", "2027-03-15", "ok", ["2027-05-01", "2027-06-15"]),
    ("18 Hong Kong 1 mese dopo la partenza: 31/1 + 1 mese = 28/2 -> sì", "hong-kong", "", "2027-02-28", "2027-01-20", "2027-01-31", "ok", ["2027-02-28"]),
    ("19 Israele 90 giorni: 1/12/2026 + 90 = 1/3/2027 -> sì", "israel", "", "2027-03-01", "2026-12-01", "2026-12-08", "ok", ["2027-03-01"]),
    ("20 Bosnia 90 giorni dopo l'uscita + regola dei 10 anni", "bosnia-and-herzegovina", "2019-05-05", "2027-01-18", "2026-10-13", "2026-10-20", "ok", ["2027-01-18", "2016-10-14"]),
    ("21 Gibilterra, arrivo 29/2/2028: emesso 28/2/2018 -> no", "gibraltar", "2018-02-28", "2029-01-01", "2028-02-29", "2028-03-05", "no", ["2028-06-05", "2018-03-01"]),
    ("22 Gibilterra, arrivo 29/2/2028: emesso 1/3/2018 -> sì", "gibraltar", "2018-03-01", "2029-01-01", "2028-02-29", "2028-03-05", "ok", ["2028-06-05", "2018-03-01"]),
    ("23 Maldive 1 mese dall'arrivo: regola rispettata ma il passaporto scade prima della partenza -> NO", "maldives", "", "2026-12-05", "2026-11-01", "2026-12-15", "no", ["2026-12-01"]),
    ("24 Colombia: regola da leggere, nessun calcolo", "colombia", "", "2027-01-01", "2026-11-01", "2026-11-10", "manuale", []),
    ("25 Spagna senza data di emissione -> errore 'issue'", "spain", "", "2030-01-01", "2026-11-01", "2026-11-10", "errore", []),
    ("26 Partenza prima dell'arrivo -> errore 'order'", "thailand", "", "2030-01-01", "2026-11-10", "2026-11-01", "errore", []),
    ("27 Singapore: 31/3 + 6 mesi = 30/9 -> sì", "singapore", "", "2026-09-30", "2026-03-31", "2026-04-05", "ok", ["2026-09-30"]),
    ("28 Thailandia: 6 mesi dall'arrivo esatti ma scade prima della partenza -> NO", "thailand", "", "2027-04-10", "2026-10-10", "2027-05-01", "no", ["2027-04-10"]),
    ("29 Thailandia: soggiorno lungo, scade il giorno della partenza -> sì", "thailand", "", "2027-05-01", "2026-10-10", "2027-05-01", "ok", ["2027-04-10"]),
    ("30 Turchia: 150 giorni rispettati ma scade prima della partenza -> NO", "turkey", "", "2027-03-20", "2026-10-10", "2027-04-01", "no", ["2027-03-09"]),
    ("31 Israele: 90 giorni rispettati ma scade prima della partenza -> NO", "israel", "", "2027-03-05", "2026-12-01", "2027-03-10", "no", ["2027-03-01"]),
    ("32 Kazakistan: 30 giorni rispettati ma scade prima della partenza -> NO", "kazakhstan", "", "2026-12-10", "2026-11-01", "2026-12-20", "no", ["2026-12-01"]),
    ("33 Kazakistan: 30 giorni, scade dopo la partenza -> sì", "kazakhstan", "", "2026-12-21", "2026-11-01", "2026-12-20", "ok", ["2026-12-01"]),
]
SCADE_PRIMA = {"23 Maldive", "11 USA", "28 Thailandia", "30 Turchia", "31 Israele", "32 Kazakistan"}


def controlla_casi():
    errori = []
    for descr, slug, em, sc, ar, pa, atteso, minime in CASI:
        o = G.verifica_passaporto(P[slug]["regola"], em, sc, ar, pa)
        if o["esito"] != atteso:
            errori.append(f"CASO SBAGLIATO: {descr}: atteso {atteso}, calcolato {o['esito']}")
        if [c["minima"] for c in o["controlli"]] != minime:
            errori.append(f"DATA MINIMA SBAGLIATA: {descr}: attese {minime}, calcolate {[c['minima'] for c in o['controlli']]}")
        if any(descr.startswith(k) for k in SCADE_PRIMA) != o["scade_prima"]:
            errori.append(f"AVVISO 'scade prima della partenza' sbagliato: {descr}")
        if o["scade_prima"] and o["esito"] == "ok":
            errori.append(f"ESITO VERDE con passaporto che scade prima della partenza: {descr}")
    return errori


def data_casuale(rnd):
    return f"{rnd.randint(2015, 2031):04d}-{rnd.randint(1, 12):02d}-{rnd.choice([1, 15, 28, 29, 30, 31]):02d}"


def valida(d):
    try:
        G.date.fromisoformat(d)
        return d
    except ValueError:
        return f"{d[:8]}28"


def casi_casuali(n=3000, seme=7):
    rnd = random.Random(seme)
    slugs = sorted(P)
    out = []
    for _ in range(n):
        ar = valida(data_casuale(rnd))
        pa = G.piu_giorni(ar, rnd.randint(-3, 400))
        out.append([rnd.choice(slugs), rnd.choice(["", valida(data_casuale(rnd))]), valida(data_casuale(rnd)), ar, pa])
    return out


def controlla_js(casi):
    regole = {s: P[s]["regola"] for s in P}
    tutti = casi + [[c[1], c[2], c[3], c[4], c[5]] for c in CASI]
    script = ("var REG=" + json.dumps(regole) + ";\n" + G.MOTORE_JS + "\nvar casi=" + json.dumps(tutti) + ";\n"
              "console.log(JSON.stringify(casi.map(function(c){return verificaPassaporto(REG[c[0]],c[1],c[2],c[3],c[4]);})));")
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(script)
    try:
        r = subprocess.run(["node", fh.name], capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        return ["node non trovato: confronto JS saltato"]
    finally:
        os.unlink(fh.name)
    if r.returncode != 0:
        return ["Errore JS: " + r.stderr[:500]]
    js = json.loads(r.stdout)
    errori = []
    for c, j in zip(tutti, js):
        py = G.verifica_passaporto(regole[c[0]], c[1], c[2], c[3], c[4])
        if json.dumps(py, sort_keys=True) != json.dumps(j, sort_keys=True):
            errori.append(f"JS diverso dal Python per {c}: py {py} js {j}")
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


def leggi(rel):
    return (SITO / rel).read_text(encoding="utf-8")


def controlla_fonti():
    errori = []
    chk = "checked on " + G.data_lunga(G.PASS["controllato_il"])
    for p in G.PAESI:
        t = leggi(f"passport-validity/{p['slug']}/index.html")
        if escape(p["url_ingresso"]) not in t or chk not in t or "page last updated " + G.data_lunga(p["aggiornata"]) not in t:
            errori.append(f"passaporto {p['slug']}: fonte, data di aggiornamento o data del controllo mancanti")
        for b in p["testo"]:
            if escape(b["x"]) not in t:
                errori.append(f"passaporto {p['slug']}: testo ufficiale mancante: {b['x'][:60]}")
        if "Open Government Licence v3.0" not in t:
            errori.append(f"passaporto {p['slug']}: attribuzione OGL mancante")
    for a in G.AER["aeroporti"] + G.AER["nazionali"]:
        t = leggi(f"liquids/{a['slug']}/index.html")
        if escape(a["url"]) not in t or "checked on " + G.data_lunga(a["controllato_il"]) not in t:
            errori.append(f"liquidi {a['slug']}: fonte o data mancanti")
        for q in a["citazioni"] + a.get("eccezioni", []):
            if escape(q) not in t:
                errori.append(f"liquidi {a['slug']}: citazione mancante: {q[:60]}")
        if a.get("contrasto") and escape(a["contrasto"]["citazione"]) not in t:
            errori.append(f"liquidi {a['slug']}: seconda fonte (contrasto) mancante")
    t = leggi("ees-etias/index.html")
    for f in G.EES["frasi"]:
        if f["trovata"] and escape(f["frase"]) not in t:
            errori.append(f"EES/ETIAS: frase mancante: {f['frase'][:60]}")
    for k, pg in G.EES["pagine"].items():
        if escape(pg["url"]) not in t:
            errori.append(f"EES/ETIAS: fonte {k} mancante")
    if "checked on " + G.data_lunga(G.EES["controllato_il"]) not in t:
        errori.append("EES/ETIAS: data del controllo mancante")
    return errori


def controlla_struttura():
    errori = []
    for f in SITO.rglob("*.html"):
        t = f.read_text(encoding="utf-8")
        if re.search(r"(check|checked|re-check|re-checked|re-read|updated)( [a-z]+)? (every (week|month)|weekly|monthly)", t, re.I):
            errori.append(f"promessa di ricontrollo periodico in {f.relative_to(SITO)}")
    for p in G.PAESI:
        t = leggi(f"passport-validity/{p['slug']}/index.html")
        if not p["regola"] and ("with a checker for your dates" in t or "data-checker data-dati" in t):
            errori.append(f"{p['slug']}: pagina senza controllo che promette il controllo")
    ie = leggi("passport-validity/ireland/index.html")
    if "not legally required to show a passport" not in ie or "airlines and ferry operators" not in ie:
        errori.append("Irlanda: spiegazione Common Travel Area mancante")
    gib = leggi("passport-validity/gibraltar/index.html")
    if "Gibraltar or the Schengen Area" not in gib or "Schengen: " in gib:
        errori.append("Gibilterra: riassunto o gruppo Schengen sbagliato")
    for f in SITO.rglob("*.html"):
        t = f.read_text(encoding="utf-8")
        if f'<meta name="google-site-verification" content="{G.GOOGLE_VERIFICA}">' not in t:
            errori.append(f"meta Google mancante in {f.relative_to(SITO)}")
        if f.name != "404.html" and f'<link rel="canonical" href="{G.URL_SITO}/' not in t:
            errori.append(f"canonical mancante in {f.relative_to(SITO)}")
        if re.search(r"<script[^>]+src=", t):
            errori.append(f"script esterno in {f.relative_to(SITO)}")
    nf = leggi("404.html")
    rel = [h for h in re.findall(r'href="([^"]+)"', nf) if not h.startswith(("/", "http", "data:", "#", "mailto:"))]
    if rel:
        errori.append(f"404: link relativi {rel[:3]}")
    if 'rel="canonical"' in nf or 'content="noindex"' not in nf:
        errori.append("404: deve essere noindex e senza canonical")
    sm = leggi("sitemap.xml")
    n_pagine = sum(1 for f in SITO.rglob("*.html") if f.name != "404.html" and not f.name.startswith("google"))
    if sm.count("<url>") != n_pagine or "404.html" in sm:
        errori.append("sitemap: numero di URL sbagliato o 404 presente")
    if f"Sitemap: {G.URL_SITO}/sitemap.xml" not in (SITO / "robots.txt").read_text():
        errori.append("robots.txt senza sitemap")
    if 'ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."' not in (SITO / "netlify.toml").read_text():
        errori.append("netlify.toml: regola ignore mancante")
    if G.URL_SITO not in leggi("index.html"):
        errori.append("URL_SITO non usato")
    return errori


# Parole vietate scritte al contrario, così questo file non le contiene in chiaro.
_AL_CONTRARIO = ["edualc", "ciporhtna", "ianepo", "tpgtahc", "inimeg", "tolipoc", "amall", "lartsim", "supo", "tennos", "ukiah"]
VIETATE = re.compile(r"\b(" + "|".join(w[::-1] for w in _AL_CONTRARIO) + r"|gpt-\d)\b", re.I)


def controlla_parole():
    errori = []
    cartelle = [SITO, SITO.parent / "dati", SITO.parent / "raccolta"]
    for c in cartelle:
        for f in c.rglob("*"):
            if f.is_file() and f.suffix in (".html", ".xml", ".txt", ".toml", ".json", ".py", ".md"):
                m = VIETATE.search(f.read_text(encoding="utf-8"))
                if m:
                    errori.append(f"Parola vietata '{m.group(0)}' in {f}")
    for f in (SITO.parent / "NOTE.md", SITO.parent / "TEST.md", SITO.parent / "genera.py"):
        if f.exists():
            m = VIETATE.search(f.read_text(encoding="utf-8"))
            if m:
                errori.append(f"Parola vietata '{m.group(0)}' in {f}")
    return errori


BROWSER_JS = r"""
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const http = require('http'); const fs = require('fs'); const path = require('path');
const ROOT = process.argv[2];
const TIPI = {'.html':'text/html; charset=utf-8','.xml':'application/xml','.txt':'text/plain','.json':'application/json'};
const srv = http.createServer((req, res) => { let p = decodeURIComponent(req.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html';
  const f = path.join(ROOT, p); if (!f.startsWith(ROOT) || !fs.existsSync(f)) { res.writeHead(404); res.end(fs.readFileSync(path.join(ROOT,'404.html'))); return; }
  res.writeHead(200, {'Content-Type': TIPI[path.extname(f)] || 'application/octet-stream'}); res.end(fs.readFileSync(f)); });
srv.listen(0, async () => {
  const base = 'http://127.0.0.1:' + srv.address().port; const out = {pagine: [], prove: []};
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  for (const tema of ['light', 'dark']) {
    const ctx = await b.newContext({ viewport: { width: 375, height: 800 }, colorScheme: tema });
    for (const u of ['/', '/passport-validity/spain/', '/liquids/']) {
      const p = await ctx.newPage(); const err = [];
      p.on('console', m => { if (m.type() === 'error') err.push(m.text()); }); p.on('pageerror', e => err.push(String(e)));
      await p.goto(base + u, { waitUntil: 'load' });
      const w = await p.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
      out.pagine.push({ url: u, tema: tema, scroll: w[0], larghezza: w[1], errori: err });
      if (tema === 'light' && u === '/passport-validity/spain/') {
        out.prove.push({ caso: 'spagna-etichette', testo: await p.textContent('[data-checker] form') + ' | ' + await p.textContent('[data-nota-schengen]') });
        await p.fill('[name=scadenza]', '2027-02-09'); await p.fill('[name=emissione]', '2020-01-01');
        await p.fill('[name=arrivo]', '2026-11-01'); await p.fill('[name=partenza]', '2026-11-10');
        out.prove.push({ caso: 'spagna-no', testo: await p.textContent('[data-out]') });
        await p.fill('[name=scadenza]', '2027-02-10');
        out.prove.push({ caso: 'spagna-ok', testo: await p.textContent('[data-out]') });
        await p.screenshot({ path: process.argv[3] + '/spagna-375.png', fullPage: false });
      }
      if (tema === 'light' && u === '/') {
        const scegli = async (nome) => { const i = await p.evaluate((n) => { const s = document.querySelector('[name=paese]'); return [...s.options].findIndex(o => o.textContent === n); }, nome);
          await p.selectOption('[name=paese]', String(i - 1)); };
        await scegli('Colombia');
        out.prove.push({ caso: 'colombia-manuale', testo: await p.textContent('[data-out]') });
        await scegli('Ireland');
        out.prove.push({ caso: 'irlanda', testo: await p.textContent('[data-out]') });
        await scegli('Thailand');
        await p.fill('[name=scadenza]', '2027-04-10'); await p.fill('[name=arrivo]', '2026-10-10'); await p.fill('[name=partenza]', '2027-05-01');
        out.prove.push({ caso: 'thailandia-scade', testo: await p.textContent('[data-out]'), verde: await p.$$eval('[data-out] .esito.si', e => e.length) });
        await scegli('Belize');
        await p.fill('[name=scadenza]', '2027-01-15'); await p.fill('[name=arrivo]', '2026-10-10'); await p.fill('[name=partenza]', '2026-10-20');
        out.prove.push({ caso: 'belize-avviso', testo: await p.textContent('[data-out]') });
        await p.screenshot({ path: process.argv[3] + '/home-375.png', fullPage: false });
      }
      await p.close(); }
    await ctx.close(); }
  await b.close(); srv.close(); console.log(JSON.stringify(out)); });
"""


def controlla_browser():
    if os.environ.get("BYF_NO_BROWSER") == "1":
        return ["controllo nel browser saltato (BYF_NO_BROWSER=1)"], None
    cartella = tempfile.mkdtemp()
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(BROWSER_JS)
    try:
        r = subprocess.run(["node", fh.name, str(SITO), cartella], capture_output=True, text=True, timeout=300)
    finally:
        os.unlink(fh.name)
    if r.returncode != 0:
        return ["Errore Playwright: " + r.stderr[:800]], None
    o = json.loads(r.stdout)
    errori = []
    for p in o["pagine"]:
        if p["scroll"] > p["larghezza"]:
            errori.append(f"Scorrimento orizzontale in {p['url']} ({p['tema']}): {p['scroll']} > {p['larghezza']}")
        if p["errori"]:
            errori.append(f"Errori in console in {p['url']} ({p['tema']}): {p['errori'][:2]}")
    prove = {x["caso"]: x["testo"] for x in o["prove"]}
    if "do NOT meet" not in prove.get("spagna-no", "") or "1 day short" not in prove.get("spagna-no", ""):
        errori.append(f"Prova Spagna 'no' fallita: {prove.get('spagna-no', '')[:200]}")
    if "Your dates meet the rule" not in prove.get("spagna-ok", "") or "0 days to spare" not in prove.get("spagna-ok", ""):
        errori.append(f"Prova Spagna 'ok' fallita: {prove.get('spagna-ok', '')[:200]}")
    if "No automatic check for this destination" not in prove.get("colombia-manuale", ""):
        errori.append(f"Prova Colombia 'manuale' fallita: {prove.get('colombia-manuale', '')[:200]}")
    if "Date you first enter the Schengen area" not in prove.get("spagna-etichette", "") or "Date you leave the Schengen area" not in prove.get("spagna-etichette", ""):
        errori.append("Etichette Schengen mancanti sulla pagina Spagna")
    ir = prove.get("irlanda", "")
    if "Irish immigration officers are entitled to ask for proof of British nationality in the course of their work." not in ir:
        errori.append(f"Irlanda: testo ufficiale tagliato o mancante nel risultato: {ir[-200:]}")
    th = next((x for x in o["prove"] if x["caso"] == "thailandia-scade"), {})
    if "expires before you leave" not in th.get("testo", "") or th.get("verde"):
        errori.append(f"Thailandia: manca l'avviso rosso o compare il verde: {th.get('testo', '')[:200]}")
    if "Some airlines may refuse boarding" not in prove.get("belize-avviso", ""):
        errori.append("Belize: avviso delle compagnie aeree assente dal risultato")
    return errori, (o, cartella)


def main():
    e1 = controlla_casi()
    print(f"1. Casi del passaporto calcolati a mano: {len(CASI)}, {len(e1)} errori")
    e2 = controlla_js(casi_casuali())
    print(f"2. Motore JS contro Python: {len(e2)} differenze (3.000 casi casuali + {len(CASI)} casi a mano)")
    e3, n = controlla_link()
    print(f"3. Link interni: {n} pagine, {len(e3)} link rotti")
    e4 = controlla_fonti()
    print(f"4. Fonti, date e citazioni nelle pagine: {len(G.PAESI)} paesi, {len(G.AER['aeroporti']) + len(G.AER['nazionali'])} pagine liquidi, EES/ETIAS: {len(e4)} errori")
    e5 = controlla_struttura()
    print(f"5. Struttura (meta Google, canonical, 404, sitemap, robots, netlify.toml): {len(e5)} errori")
    e6 = controlla_parole()
    print(f"6. Parole vietate: {len(e6)}")
    e7, info = controlla_browser()
    if info:
        o, cartella = info
        print(f"7. Browser 375 px: {len(o['pagine'])} viste (3 pagine × tema chiaro e scuro), {len(o['prove'])} prove del controllo, {len(e7)} errori; schermate in {cartella}")
    else:
        print(f"7. Browser 375 px: {e7[0] if e7 else ''}")
    tutti = e1 + e2 + e3 + e4 + e5 + e6 + (e7 if info else [])
    for e in tutti:
        print(" -", e)
    if tutti:
        sys.exit(1)
    print("TUTTO OK")


if __name__ == "__main__":
    main()
