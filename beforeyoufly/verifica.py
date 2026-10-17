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
7. Browser a 375 px (Playwright): 5 pagine senza scorrimento orizzontale e senza errori in console; il controllo del passaporto risponde;
   il testo del controllo nella home ha contrasto di almeno 4,5:1 in tema chiaro e scuro; sezione visti e FAQ visibili.
8. Visti: ogni riassunto di una riga deriva da uno schema riconosciuto (ricalcolato da raccolta/passaporti.py sul testo salvato e confrontato
   con modelli fissi); i numeri del riassunto sono nella frase ufficiale; senza riassunto la pagina mostra solo la citazione (o dice che manca);
   nessun "senza visto" se il testo parla di ETA, tasse, tessere o moduli online prima del viaggio; nessun "serve un visto" se il visto è un ETA/eVisitor;
   le pagine Schengen rimandano a EES/ETIAS nella sezione visti.
9. Liquidi: risposta diretta in alto; ogni risposta delle FAQ (JSON-LD FAQPage e testo visibile) è fatta solo di citazioni ufficiali intere.
10. Titoli <= 65 caratteri (salvo quando nessuna forma prevista ci sta) e descrizioni <= 160 in tutte le pagine.
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
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("raccolta_passaporti", Path(__file__).resolve().parent / "raccolta" / "passaporti.py")
RP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RP)

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
        if re.search(r'<script[^>]+src="(?!https://gc\.zgo\.at/count\.js")', t):  # ammesso solo il contatore GoatCounter
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


# Modelli fissi dei riassunti dei visti: un riassunto che non corrisponde a uno di questi è un errore.
MODELLI_VISTO = [re.compile(x) for x in [
    r"^You can visit the Schengen area \((?:including|and) [^)]+\) without a visa for up to 90 days in any 180-day period(?:, for the reasons listed in the FCDO text)?$",
    r"^You can visit .+ without a visa for (?:up to )?(?:\d+|one) (?:days?|months?|years?)(?: in any \d+-(?:day|month) period| in a \d+-(?:day|month) period"
    r"| within a \d+-(?:day|month) period| in a year)?(?: for (?:tourism or business|business or tourism|tourism|business)| as a tourist)?"
    r"(?: \(for the reasons listed in the FCDO text\))?$",
    r"^You can visit .+ without a visa \(the FCDO text says how long you can stay\)$",
    r"^You need a visa to (?:visit|enter|enter or travel through|travel to) .+?(?: as a visitor| for tourism| for tourism or business)?(?: and you must apply in advance)?$",
    r"^You need a visa before you travel to .+$"]]
SENZA_VISTO_VIETATO = re.compile(r"\b(?:ETA|eTA|ESTA|NZeTA|ETIAS)\b|travel authori[sz]ation|electronic travel|entry fee|administration fee|tourist card"
                                 r"|embarkation card|approval to travel|e-travel|form online before", re.I)
# "serve un visto" solo se il visto non è un'autorizzazione elettronica (ETA, eVisitor): altrimenti solo la citazione
VISTO_ELETTRONICO_VIETATO = re.compile(r"\b(?:ETA|eTA|ESTA|NZeTA|ETIAS)\b|eVisitor|electronic visitor visa|electronic travel authori[sz]ation", re.I)


def controlla_visti():
    errori = []
    con, solo, senza = 0, 0, 0
    for p in G.PAESI:
        V = p.get("visto")
        if V is None:
            errori.append(f"visti {p['slug']}: dati del visto mancanti (rilanciare raccolta/passaporti.py)")
            continue
        t = leggi(f"passport-validity/{p['slug']}/index.html")
        if f"Do I need a visa for {escape(p['nome'])} with a British passport?" not in t:
            errori.append(f"visti {p['slug']}: domanda sul visto mancante")
        schema, sintesi, frase, _ = RP.sintesi_visto(V["testo"], p["nome"], p["slug"])
        if (schema, sintesi, frase) != (V["schema"], V["sintesi"], V["frase"]):
            errori.append(f"visti {p['slug']}: il riassunto salvato non è quello che dà lo schema sul testo salvato")
        for b in V["testo"]:
            if escape(b["x"]) not in t:
                errori.append(f"visti {p['slug']}: testo ufficiale mancante: {b['x'][:60]}")
        if not V["testo"]:
            senza += 1
            if "had no “Visa requirements” section" not in t or "In short:" in t:
                errori.append(f"visti {p['slug']}: manca l'avviso 'nessuna sezione visti' o c'è un riassunto")
            continue
        if escape(p["url_ingresso"]) not in t:
            errori.append(f"visti {p['slug']}: fonte GOV.UK mancante")
        if not V["sintesi"]:
            solo += 1
            if "In short:" in t:
                errori.append(f"visti {p['slug']}: riassunto mostrato senza schema riconosciuto")
            continue
        con += 1
        if not any(m.match(V["sintesi"]) for m in MODELLI_VISTO):
            errori.append(f"visti {p['slug']}: riassunto fuori dai modelli fissi: {V['sintesi']}")
        if not V["frase"] or not V["testo"][0]["x"].startswith(V["frase"]):
            errori.append(f"visti {p['slug']}: la frase di partenza non è l'inizio del testo ufficiale")
        for num in re.findall(r"\b(\d+|one)\b", V["sintesi"]):
            if not re.search(r"\b" + num + r"\b", V["frase"] or ""):
                errori.append(f"visti {p['slug']}: il numero {num} del riassunto non è nella frase ufficiale")
        if V["sintesi"].startswith("You can visit") and SENZA_VISTO_VIETATO.search(" ".join(b["x"] for b in V["testo"])):
            errori.append(f"visti {p['slug']}: 'senza visto' ma il testo parla di autorizzazione, tassa o tessera")
        if V["sintesi"].startswith("You need a visa") and VISTO_ELETTRONICO_VIETATO.search(" ".join(b["x"] for b in V["testo"])):
            errori.append(f"visti {p['slug']}: 'serve un visto' ma il testo parla di ETA o visto elettronico")
        if V["schema"] == "schengen" and 'href="../../ees-etias/"' not in t.split('id="visa"')[1].split("Official source:")[0]:
            errori.append(f"visti {p['slug']}: pagina Schengen senza il rimando a EES/ETIAS nella sezione visti")
        if f"In short: <strong>{escape(V['sintesi'])}.</strong>" not in t:
            errori.append(f"visti {p['slug']}: riassunto non mostrato nella pagina")
    return errori, (con, solo, senza)


class LD(HTMLParser):
    def __init__(self):
        super().__init__()
        self.dentro, self.blocchi, self.h3 = False, [], 0

    def handle_starttag(self, tag, attrs):
        if tag == "script" and ("type", "application/ld+json") in attrs:
            self.dentro = True
            self.blocchi.append("")

    def handle_endtag(self, tag):
        if tag == "script":
            self.dentro = False

    def handle_data(self, data):
        if self.dentro:
            self.blocchi[-1] += data


def citazioni_faq(testo, ammesse):
    """Scompone '“a” “b”' in citazioni ammesse (intere); None se resta testo che non è una citazione ufficiale."""
    if not testo:
        return []
    for q in sorted(ammesse, key=len, reverse=True):
        pezzo = f"“{q}”"
        if testo.startswith(pezzo):
            resto = testo[len(pezzo):]
            if resto.startswith(" ") or not resto:
                dopo = citazioni_faq(resto[1:] if resto else "", ammesse)
                if dopo is not None:
                    return [q] + dopo
    return None


def controlla_liquidi_nuovi():
    errori, n_faq = [], 0
    for a in G.AER["aeroporti"] + G.AER["nazionali"]:
        t = leggi(f"liquids/{a['slug']}/index.html")
        naz = a in G.AER["nazionali"]
        # risposta diretta: sì/no dalla regola (o la sfumatura scritta nel file), più la sintesi del file
        attesa = (a.get("risposta") or {"2l": "Yes", "100ml": "No", "dipende": "It depends", "contraddice": "Not clear"}[a["regola"]])
        m = re.search(r"Can I take liquids over 100 ml through security at [^<]+\? <strong>([^<]+)", t)
        if not m or not m.group(1).startswith(escape(attesa)) or escape(a["sintesi"]) not in m.group(1):
            errori.append(f"liquidi {a['slug']}: risposta diretta in alto mancante o diversa dalla regola")
        if a.get("risposta") and a["regola"] in ("2l", "100ml") and not a["risposta"].startswith({"2l": "Yes", "100ml": "No"}[a["regola"]]):
            errori.append(f"liquidi {a['slug']}: 'risposta' in contrasto con la regola")
        ammesse = list(a["citazioni"]) + list(a.get("eccezioni", []))
        K = a.get("contrasto")
        if a["regola"] == "contraddice" and K and K.get("url") == a["url"]:
            ammesse.append(K["citazione"])
        p = LD()
        p.feed(t)
        faq = [json.loads(x) for x in p.blocchi if '"FAQPage"' in x]
        if len(faq) != 1:
            errori.append(f"liquidi {a['slug']}: JSON-LD FAQPage assente o doppio")
            continue
        voci = faq[0]["mainEntity"]
        if not 1 <= len(voci) <= 4 or t.count("<h3>") < len(voci):
            errori.append(f"liquidi {a['slug']}: numero di domande FAQ sbagliato ({len(voci)})")
        pref = f"Quoted from {a['titolo_fonte']} (checked on {G.data_lunga(a['controllato_il'])}): "
        for v in voci:
            n_faq += 1
            testo = v["acceptedAnswer"]["text"]
            if not testo.startswith(pref):
                errori.append(f"liquidi {a['slug']}: risposta FAQ senza la fonte: {testo[:60]}")
                continue
            cc = citazioni_faq(testo[len(pref):], ammesse)
            if not cc:
                errori.append(f"liquidi {a['slug']}: risposta FAQ con testo non citato dalla pagina ufficiale: {testo[len(pref):][:80]}")
                continue
            if escape(v["name"]) not in t:
                errori.append(f"liquidi {a['slug']}: domanda FAQ non visibile nella pagina")
            blocco = "<blockquote class=\"cit\">" + "".join(f"<p>{escape(q)}</p>" for q in cc) + "</blockquote>"
            if f"<h3>{escape(v['name'])}</h3>{blocco}" not in t:
                errori.append(f"liquidi {a['slug']}: risposta FAQ visibile diversa dal JSON-LD")
        if not naz:
            altri = [b for b in G.AER["aeroporti"] if b is not a and b["paese"] == a["paese"]]
            for b in altri:
                if f'href="../../liquids/{b["slug"]}/"' not in t:
                    errori.append(f"liquidi {a['slug']}: manca il collegamento a {b['slug']} (stesso Paese)")
    return errori, n_faq


def controlla_meta():
    errori, lunghi = [], []
    attesi = {f"passport-validity/{p['slug']}/index.html": G.titoli_passaporto(p) for p in G.PAESI}
    attesi.update({f"liquids/{a['slug']}/index.html": G.titoli_liquidi(a) for a in G.AER["aeroporti"]})
    attesi.update({f"liquids/{a['slug']}/index.html": G.titoli_liquidi(a, True) for a in G.AER["nazionali"]})
    from html import unescape
    for f in SITO.rglob("*.html"):
        if f.name.startswith("google"):
            continue
        t = f.read_text(encoding="utf-8")
        rel = str(f.relative_to(SITO))
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        des = unescape(re.search(r'<meta name="description" content="(.*?)">', t).group(1))
        if len(des) > G.LIMITE_DESCRIZIONE:
            errori.append(f"descrizione di {len(des)} caratteri (> 160) in {rel}")
        if len(tit) > G.LIMITE_TITOLO:
            if rel in attesi and all(len(c) > G.LIMITE_TITOLO for c in attesi[rel]):
                lunghi.append(rel)
            else:
                errori.append(f"titolo di {len(tit)} caratteri (> 65) in {rel}: {tit}")
        if rel in attesi and tit != G.scegli(attesi[rel], G.LIMITE_TITOLO):
            errori.append(f"titolo non scelto tra le forme previste in {rel}")
    return errori, lunghi


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
    for (const u of ['/', '/passport-validity/spain/', '/liquids/', '/liquids/barcelona/', '/passport-validity/egypt/']) {
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
      if (tema === 'light' && u === '/liquids/barcelona/') {
        out.prove.push({ caso: 'barcellona', testo: await p.textContent('main'), faq: await p.$$eval('.faq h3', e => e.filter(x => x.getBoundingClientRect().height > 0).length) });
      }
      if (tema === 'light' && u === '/passport-validity/egypt/') {
        const vis = await p.$eval('#visa', e => e.getBoundingClientRect().height > 0);
        await p.click('details.card > summary');
        out.prove.push({ caso: 'egitto', testo: await p.textContent('main'), visa: vis, aperto: await p.$eval('details.card', e => e.open) });
        await p.screenshot({ path: process.argv[3] + '/egitto-375.png', fullPage: false });
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
      if (u === '/') {
        // contrasto del risultato del controllo (dentro la fascia scura della home) in entrambi i temi
        const scegli2 = async (nome) => { const i = await p.evaluate((n) => { const s = document.querySelector('[name=paese]'); return [...s.options].findIndex(o => o.textContent === n); }, nome);
          await p.selectOption('[name=paese]', String(i - 1)); };
        await scegli2('Spain');
        await p.fill('[name=scadenza]', '2027-02-10'); await p.fill('[name=emissione]', '2017-03-01'); await p.fill('[name=arrivo]', '2026-12-20'); await p.fill('[name=partenza]', '2027-01-03');
        const minimo = await p.evaluate(() => {
          const lum = c => { const a = c.match(/[\d.]+/g).map(Number); const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return .2126 * f(a[0]) + .7152 * f(a[1]) + .0722 * f(a[2]); };
          const sfondo = el => { while (el) { const b = getComputedStyle(el).backgroundColor; const m = b.match(/[\d.]+/g); if (m && (m[3] === undefined || +m[3] > .5)) return b; el = el.parentElement; } return 'rgb(255,255,255)'; };
          let peggiore = [99, ''];
          for (const el of document.querySelectorAll('[data-checker] *')) {
            const t = [...el.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim()).map(n => n.textContent.trim()).join(' ');
            if (!t || !el.getBoundingClientRect().width) continue;
            const l1 = lum(getComputedStyle(el).color), l2 = lum(sfondo(el)); const r = (Math.max(l1, l2) + .05) / (Math.min(l1, l2) + .05);
            if (r < peggiore[0]) peggiore = [r, t.slice(0, 40)];
          }
          return peggiore; });
        out.prove.push({ caso: 'contrasto-' + tema, testo: minimo[1], rapporto: minimo[0] });
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
    for x in o["prove"]:
        if x["caso"].startswith("contrasto-") and x.get("rapporto", 0) < 4.5:
            errori.append(f"Contrasto insufficiente nel controllo della home ({x['caso'][10:]}): {x['rapporto']:.2f}:1 su “{x['testo']}”")
    bc = next((x for x in o["prove"] if x["caso"] == "barcellona"), {})
    if "Can I take liquids over 100 ml through security at Barcelona-El Prat (BCN)?" not in bc.get("testo", "") or not bc.get("faq"):
        errori.append("Barcellona: risposta diretta o FAQ non visibili nel browser")
    eg = next((x for x in o["prove"] if x["caso"] == "egitto"), {})
    if not eg.get("visa") or "normally need a visa" not in eg.get("testo", "") or not eg.get("aperto"):
        errori.append("Egitto: sezione visti non visibile o dettagli che non si aprono")
    if sum(1 for x in o["prove"] if x["caso"].startswith("contrasto-")) != 2:
        errori.append("Prova del contrasto del controllo (tema chiaro e scuro) non eseguita")
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
        print(f"7. Browser 375 px: {len(o['pagine'])} viste (5 pagine × tema chiaro e scuro), {len(o['prove'])} prove del controllo, {len(e7)} errori; schermate in {cartella}")
    else:
        print(f"7. Browser 375 px: {e7[0] if e7 else ''}")
    e8, (con, solo, senza) = controlla_visti()
    print(f"8. Visti: {con} riassunti da schema riconosciuto, {solo} solo citazione, {senza} senza sezione visti: {len(e8)} errori")
    e9, n_faq = controlla_liquidi_nuovi()
    print(f"9. Liquidi: risposta diretta e {n_faq} risposte FAQ fatte solo di citazioni ufficiali: {len(e9)} errori")
    e10, lunghi = controlla_meta()
    print(f"10. Titoli <= 65 e descrizioni <= 160: {len(e10)} errori" + (f"; titoli più lunghi senza alternativa più corta prevista: {lunghi}" if lunghi else ""))
    tutti = e1 + e2 + e3 + e4 + e5 + e6 + (e7 if info else []) + e8 + e9 + e10
    for e in tutti:
        print(" -", e)
    if tutti:
        sys.exit(1)
    print("TUTTO OK")


if __name__ == "__main__":
    main()
