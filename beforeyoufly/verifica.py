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
11. Passaporti canadese e australiano: ogni riassunto (validità e visto) è ricalcolato con raccolta/passaporti_ca.py o passaporti_au.py sul testo
    salvato, deve corrispondere a un modello fisso e i suoi numeri devono stare nella frase ufficiale; controllo indipendente: nessun "senza visto"
    se il testo d'ingresso parla di eTA/ETA/ESTA/ETIAS (salvo ETIAS "Applications are not yet open." detto nel riassunto), e-visa, arrival card,
    moduli o registrazioni prima del viaggio, tessere o tasse; nessun "serve un visto" se il visto è elettronico o all'arrivo; ogni pagina cita il
    testo ufficiale intero, mostra fonte, data della pagina ufficiale, data del controllo, licenza (OGL Canada / CC BY 4.0 con l'attribuzione
    richiesta) e dice che il sito non è del governo; indice e collegamenti con le pagine britanniche della stessa destinazione (andata e ritorno);
    pagina solo per le destinazioni con testo specifico del Paese (genera.ha_testo_specifico), le altre senza pagina e fuori dalla sitemap.
    Nel browser (punto 7) anche 4 pagine nuove (2 canadesi, 2 australiane) a 375 px, tema chiaro e scuro.
12. Bagaglio a mano (dati/bagagli.json): ogni misura ha la citazione ufficiale (i suoi numeri, in cm e pollici se la fonte li scrive, sono nella
    frase citata; i cm non ufficiali sono la conversione esatta dei pollici ufficiali), l'URL https della fonte e la data del controllo, e la
    pagina li mostra; risposta diretta in alto; FAQ (JSON-LD e testo visibile) fatte solo di citazioni ufficiali intere; il confronto
    "ordinato" di genera.entra_borsa uguale a un controllo indipendente sulle 6 rotazioni (4.000 casi casuali) e il motore JS uguale al
    Python (3.000 casi); le pagine per misura elencano esattamente le compagnie calcolate dai dati; indice con ricerca e compagnie escluse con
    il motivo; pagina UE con tutte le citazioni, le fonti ufficiali UE, le tappe dell'iter e la data; collegamenti da home e liquidi;
    nessun link affiliato attivo (affiliati.json senza URL, nessun rel="sponsored"). Nel browser (punto 7): 5 pagine nuove a 375 px e
    10 casi dello strumento "Does my bag fit?" (borsa ruotata, misure uguali, decimali con punto e virgola, pollici, valore non valido),
    confrontati compagnia per compagnia con il Python; menu e home senza scorrimento orizzontale a 820 px.
13. Documenti per chi ha la cittadinanza italiana (dati/documenti_it.json, fonte Viaggiare Sicuri): la cache delle schede (raccolta/.cache/it/,
    fuori dal repository) deve avere le stesse impronte SHA-256 dei campi da cui sono stati scritti i fatti; ogni fatto è ricalcolato con
    raccolta/documenti_it.py sul campo salvato (o è un fatto scritto a mano con l'impronta del campo ancora valida) ed è legato a un campo
    («Passaporto», «Visto di ingresso») con la data della scheda; ogni citazione è nel campo parola per parola (al massimo 20 parole) e i numeri
    delle frasi nostre sono nelle citazioni; controlli indipendenti (CIE nominata, nessuna seconda validità, nessun «non serve il visto» che taccia
    ESTA/eTA/ETA/card/moduli); nessuna pagina italiana ha più di 25 parole di fila uguali a un testo di una scheda (tutte le sezioni di tutte le
    schede); pagina solo per le schede con contenuto specifico, con lingua it, canonical, GoatCounter, fonte, data, avvertenze, citazioni, FAQ
    (JSON-LD = testo visibile = fatti); link con le pagine britanniche (andata e ritorno); indice con tutte le schede, ricerca e metodo.
    Nel browser (punto 7) anche 4 pagine italiane a 375 px, tema chiaro e scuro, e la ricerca dell'indice.
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
    for k in G.ESTERI:
        attesi.update({v["url_pag"] + "index.html": G.titoli_estero(v) for v in G.VOCI[k]})
    attesi.update({f"{G.BAG_BASE}/{C['slug']}/index.html": G.titoli_bag(C) for C in G.COMPAGNIE})
    attesi.update({f"{G.BAG_BASE}/size/{sl}/index.html": G.titoli_misura(sl) for sl, _ in G.MISURE_COMUNI})
    attesi.update({v["url_pag"] + "index.html": G.titoli_it(v) for v in G.VOCI_IT})
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


# ---------------------------------------------------------------- 11. passaporti canadese e australiano
def _carica(nome):
    spec = importlib.util.spec_from_file_location(nome, Path(__file__).resolve().parent / "raccolta" / f"{nome}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


RCA = _carica("passaporti_ca")
RAU = _carica("passaporti_au")
CODA_VAL = r"(?:, and (?:be in good condition|(?:have|must contain|contain|include|should have) [^()]+))?(?: \(the official text adds more details\))?$"
MODELLI_VAL = {
    "ca": [re.compile(x + CODA_VAL) for x in [
        r"^Valid (?:for at least |at least |for a minimum of |a minimum of |for )?\d+ (?:months?|days?) beyond the date you expect to leave .+?",
        r"^Valid (?:for at least |at least |for a minimum of |a minimum of |for )?\d+ (?:months?|days?) from the date you enter(?: .+?)?",
        r"^Valid for (?:at least )?the (?:expected )?duration of your stay(?: in .+?)?",
        r"^Valid beyond the date you expect to leave .+?"]],
    "au": [re.compile(x) for x in [r"^Valid for (?:at least )?\d+ (?:months?|days?) (?:after the date you leave|from the date you arrive in) .+$",
                                   r"^At least \d+ (?:months?|days?) of validity remaining when you enter .+$"]],
}
ETIAS_CODA = r"(?:; ETIAS will be required, but “Applications are not yet open”, says the same page)?$"
MODELLI_VIS = {
    "ca": [re.compile(x + ETIAS_CODA) for x in [
        r"^Tourist visa not required for stays (?:of )?(?:up to a maximum of|up to|less than|fewer than) (?:\d+|six) (?:days|months|weeks)"
        r"(?: in any \d+-day period| in a \d+-day period| in a 180 day period| within any \d+-day period| within a \d+-day period"
        r"| within any 180-day period)?(?:, counted across the whole Schengen area)?",
        r"^Tourist visa not required for stays of \d+ (?:days|months) or less(?: in any \d+-day period)?",
        r"^Tourist visa not required \(read the official text for how long you can stay\)",
        r"^Tourist visa required"]],
    "au": [re.compile(x) for x in [r"^You don't need a visa to visit .+ for (?:up to |less than )?\d+ (?:days|months)(?: for tourism)?$",
                                   r"^(?:Tourists can visit|You can stay in) .+ for (?:up to )?\d+ (?:days|months) without a visa$",
                                   r"^Australian tourists can enter .+ without a visa for (?:up to )?\d+ (?:days|months)$",
                                   r"^You don't need a visa to visit .+ (?:for tourism|as a tourist) \(read the official text for how long you can stay\)$",
                                   r"^You need a visa (?:to (?:visit|enter|travel to)|before you enter) .+$"]],
}
# controllo indipendente (più largo di quello della raccolta): niente "senza visto" se il testo d'ingresso parla di autorizzazioni, visti elettronici,
# moduli o registrazioni prima del viaggio, tessere o tasse d'ingresso; niente "serve un visto" se il visto è elettronico o si ottiene all'arrivo
VIETATO_SENZA = re.compile(r"\b(?:ETA|eTA|ESTA|NZeTA|K-ETA|ETIAS|EVW)\b|eVisitor|travel authori[sz]ation|electronic authori[sz]ation|\be-?visa|electronic visa|arrival card|arrival declaration|e-arrival"
                           r"|declaration form|immigration form|embarkation|landing card|tourist card|migration card|ED card|entry fee|entry tax|tourism fee|tourist tax"
                           r"|pre-?regist|pre-?arrival|register online|online registration|e-?Travel|online form|QR code|online visa|visa online", re.I)
VIETATO_RICHIESTO = re.compile(r"\b(?:ETA|eTA|ESTA|NZeTA|K-ETA)\b|eVisitor|\be-?visa|electronic visa|electronic travel|online visa|visa online|on arrival|upon arrival|"
                               r"ports? of entry|points? of entry|at the airport", re.I)
PAROLE_NUM = {"six": "6", "three": "3", "one": "1", "two": "2"}


def _numeri_ok(sintesi, frase):
    f = frase or ""
    for k, v in PAROLE_NUM.items():
        f = re.sub(r"\b" + k + r"\b", v, f)
    return all(re.search(r"\b" + n + r"\b", f) for n in re.findall(r"\b(\d+)\b", sintesi) if n not in ("180",) or "180" in f)


def _sezioni_au(p):
    sez = {"Passport": p["passaporto"]["testo"], RAU.VISTI: p["visto"]["testo"]}
    for a in p.get("altre_sezioni", []):
        sez[a["titolo"]] = a["testo"]
    return sez


def controlla_esteri():
    errori, conti = [], {}
    for k, c in G.ESTERI.items():
        D = c["dati"]
        voci = G.VOCI[k]
        conti[k] = {"pagine": 0, "val": 0, "vis": 0, "val_cit": 0, "vis_cit": 0}
        if not D:
            continue
        if len(voci) < 0.8 * D["pagine_indice"]:
            errori.append(f"{k}: solo {len(voci)} pagine su {D['pagine_indice']} destinazioni della fonte")
        t_ind = leggi(f"{c['base']}/index.html")
        for v in voci:
            p = v["p"]
            P, V = p["passaporto"], p["visto"]
            conti[k]["pagine"] += 1
            # a) i riassunti salvati sono quelli che danno gli schemi sul testo salvato
            if k == "ca":
                ss = RCA.sezioni(p["ingresso"])
                rv = RCA.calcola_validita(P["testo"], P["titolo_sezione"], p["nome"], p["iso"], p.get("schengen", False))
                if (rv[0], rv[1], rv[2], rv[3]) != (P["schema"], P["sintesi"], P["breve"], P["frase"]):
                    errori.append(f"{k} {v['slug']}: riassunto della validità diverso da quello dello schema sul testo salvato")
                visti_ss = next((b for t, b in ss if t and RCA.TITOLO_VISTI.match(t)), [])
                if [b["x"] for b in visti_ss] != [b["x"] for b in V["testo"]]:
                    errori.append(f"{k} {v['slug']}: testo dei visti diverso dalla sezione d'ingresso salvata")
                rs = RCA.sintesi_visto(V["testo"], ss)
                if (rs[0], rs[1], rs[2]) != (V["schema"], V["sintesi"], V["frase"]):
                    errori.append(f"{k} {v['slug']}: riassunto del visto diverso da quello dello schema sul testo salvato")
                etias = [(t, b) for t, b in ss if t and "ETIAS" in t and any(RCA.ETIAS_NON_APERTO in x["x"] and RCA.ETIAS_FUTURO in x["x"] for x in b)]
                resto = " ".join(x["x"] for t, b in ss if (t, b) not in etias for x in b) + " " + " ".join(t or "" for t, b in ss if (t, b) not in etias)
                tutto_visti = " ".join(b["x"] for b in V["testo"])
            else:
                sez = _sezioni_au(p)
                rv = RAU.sintesi_validita(sez, p["nome"], p["slug_fonte"])
                if (rv[0], rv[1], rv[2], rv[3]) != (P["schema"], P["sintesi"], P["breve"], P["frase"]):
                    errori.append(f"{k} {v['slug']}: riassunto della validità diverso da quello dello schema sul testo salvato")
                rs = RAU.sintesi_visto(sez, p["nome"], p["slug_fonte"])
                if (rs[0], rs[1], rs[2]) != (V["schema"], V["sintesi"], V["frase"]):
                    errori.append(f"{k} {v['slug']}: riassunto del visto diverso da quello dello schema sul testo salvato")
                etias = []
                resto = " ".join(b["x"] for t, bb in sez.items() if t != "Passport" for b in bb if not b.get("generico"))
                tutto_visti = resto
            # b) modelli fissi, numeri nella frase ufficiale, frase = inizio del testo citato
            if P["sintesi"]:
                conti[k]["val"] += 1
                if not any(m.match(P["sintesi"]) for m in MODELLI_VAL[k]):
                    errori.append(f"{k} {v['slug']}: riassunto della validità fuori dai modelli fissi: {P['sintesi']}")
                if not _numeri_ok(P["sintesi"], P["frase"]):
                    errori.append(f"{k} {v['slug']}: un numero del riassunto della validità non è nella frase ufficiale")
                if not any(b["x"].startswith(P["frase"]) or P["frase"] in b["x"] for b in P["testo"]):
                    errori.append(f"{k} {v['slug']}: la frase della validità non è nel testo citato")
            elif P["testo"]:
                conti[k]["val_cit"] += 1
            if V["sintesi"]:
                conti[k]["vis"] += 1
                if not any(m.match(V["sintesi"]) for m in MODELLI_VIS[k]):
                    errori.append(f"{k} {v['slug']}: riassunto del visto fuori dai modelli fissi: {V['sintesi']}")
                if not _numeri_ok(V["sintesi"], V["frase"]):
                    errori.append(f"{k} {v['slug']}: un numero del riassunto del visto non è nella frase ufficiale")
                if not any(b["x"].startswith(V["frase"]) for b in V["testo"]):
                    errori.append(f"{k} {v['slug']}: la frase del visto non è nel testo citato")
                senza = re.search(r"not required|don't need|without a visa", V["sintesi"])
                if senza and VIETATO_SENZA.search(resto):
                    errori.append(f"{k} {v['slug']}: 'senza visto' ma il testo d'ingresso parla di autorizzazione, e-visa, modulo, tessera o tassa: "
                                  f"{VIETATO_SENZA.search(resto).group(0)}")
                if etias and "ETIAS" not in V["sintesi"]:
                    errori.append(f"{k} {v['slug']}: il testo parla di ETIAS ma il riassunto no")
                if not senza and VIETATO_RICHIESTO.search(tutto_visti):
                    errori.append(f"{k} {v['slug']}: 'serve un visto' ma il visto è elettronico o si ottiene all'arrivo")
            elif V["testo"]:
                conti[k]["vis_cit"] += 1
            # c) la pagina: citazioni intere, riassunti solo se ci sono, fonte, date, licenza, nessuna aria di sito governativo
            t = leggi(v["url_pag"] + "index.html")
            for b in G.passaporto_da_mostrare(k, P["testo"]) + V["testo"]:
                if escape(b["x"]) not in t:
                    errori.append(f"{k} {v['slug']}: testo ufficiale mancante nella pagina: {b['x'][:60]}")
            if not (P["testo"] or V["testo"]):
                errori.append(f"{k} {v['slug']}: pagina senza nessuna citazione ufficiale")
            n_brevi = sum(1 for x in (P["sintesi"], V["sintesi"]) if x)
            if t.count("In short: <strong>") != n_brevi:
                errori.append(f"{k} {v['slug']}: {t.count('In short: <strong>')} riassunti nella pagina invece di {n_brevi}")
            for x in (P["sintesi"], V["sintesi"]):
                if x and f"In short: <strong>{escape(x)}.</strong>" not in t:
                    errori.append(f"{k} {v['slug']}: riassunto non mostrato com'è nei dati")
            if escape(p["url"]) not in t or "checked on " + G.data_lunga(D["controllato_il"]) not in t:
                errori.append(f"{k} {v['slug']}: fonte o data del controllo mancanti")
            if p.get("aggiornata") and G.data_lunga(p["aggiornata"]) not in t:
                errori.append(f"{k} {v['slug']}: data di aggiornamento della pagina ufficiale mancante")
            if k == "ca" and ("Contains information licensed under the" not in t or escape(D["licenza_url"]) not in t
                              or "not a Government of Canada site" not in t):
                errori.append(f"{k} {v['slug']}: attribuzione OGL Canada o avviso 'non governativo' mancanti")
            if k == "au" and (escape(D["attribuzione"]) not in t or D["licenza_url"] not in t or "not an Australian Government site" not in t):
                errori.append(f"{k} {v['slug']}: attribuzione Smartraveller (CC BY 4.0) o avviso 'non governativo' mancanti")
            if f"Do {c['pop']} need a visa for {escape(G.nome_frase(v))}?" not in t or 'id="passport"' not in t:
                errori.append(f"{k} {v['slug']}: domande sul visto o sulla validità mancanti")
            # d) collegamenti: indice, pagine britanniche della stessa destinazione (andata e ritorno)
            if f'href="../{v["url_pag"]}"' not in t_ind:
                errori.append(f"{k} {v['slug']}: manca nell'indice {c['base']}/")
            for s in v["uk"]:
                tu = leggi(f"passport-validity/{s}/index.html")
                if f'href="../../{v["url_pag"]}"' not in tu:
                    errori.append(f"{k} {v['slug']}: la pagina britannica {s} non collega la pagina {c['agg']}")
                if f'href="../../passport-validity/{s}/"' not in t:
                    errori.append(f"{k} {v['slug']}: manca il collegamento alla pagina britannica {s}")
        slugs = [v["slug"] for v in voci]
        if len(set(slugs)) != len(slugs):
            errori.append(f"{k}: slug duplicati")
        # e) contenuto sottile (revisione del 17/10/2026): pagina solo con testo specifico del Paese; le altre senza pagina, fuori dalla sitemap,
        #    elencate nell'indice con il link alla fonte
        sm = leggi("sitemap.xml")
        for v in voci:
            if not G.ha_testo_specifico(k, v["p"]):
                errori.append(f"{k} {v['slug']}: pagina senza testo specifico del Paese")
        for p in G.SENZA_PAGINA_ESTERI[k]:
            if escape(p["url"]) not in t_ind:
                errori.append(f"{k}: {p['nome']} senza pagina ma non elencato nell'indice con il link ufficiale")
            for cand in {p.get("slug_fonte", ""), G._chiave_nome(p["nome"]).replace(" ", "-")}:
                if cand and ((SITO / c["base"] / cand).exists() or f"/{c['base']}/{cand}/<" in sm):
                    errori.append(f"{k}: {p['nome']} non deve avere una pagina né stare nella sitemap")
    return errori, conti


# ---------------------------------------------------------------- 12. bagaglio a mano per compagnia aerea
NUM = re.compile(r"\d+(?:[.,]\d+)?")


def _numeri(testo):
    return {round(float(x.replace(",", ".")), 2) for x in NUM.findall(testo)}


def _entra_permutazioni(m, unita, b):
    """Controllo indipendente da genera.entra_borsa: la borsa entra se ALMENO UNA delle 6 rotazioni rispetta i tre limiti nell'ordine della fonte."""
    import itertools
    if unita == "in" and b.get("pollici") and b.get("pollici_ufficiali"):
        lim, mis, u = b["pollici"], m, "in"
    else:
        lim, mis, u = b["cm"], [x * 2.54 for x in m] if unita == "in" else m, "cm"
    if b.get("totale") and sum(mis) > b["totale"][u] + 1e-6:
        return False
    return any(all(p[i] <= lim[i] + 1e-6 for i in range(3)) for p in itertools.permutations(mis))


# 10 casi del controllo "Does my bag fit?" provati nel browser (valori come li scrive l'utente)
CASI_BORSA = [
    ("40x30x20 cm", ["40", "30", "20"], "cm"),
    ("ruotata 20x40x30 cm", ["20", "40", "30"], "cm"),
    ("55x40x20 cm", ["55", "40", "20"], "cm"),
    ("misure uguali 30x30x30 cm", ["30", "30", "30"], "cm"),
    ("decimale 40.5x30x20 cm", ["40.5", "30", "20"], "cm"),
    ("virgola 45,5x36x20 cm", ["45,5", "36", "20"], "cm"),
    ("pollici 22x14x9 in", ["22", "14", "9"], "in"),
    ("pollici 22x14x9.5 in", ["22", "14", "9.5"], "in"),
    ("56x45x25 cm", ["56", "45", "25"], "cm"),
    ("non valida 0x30x20", ["0", "30", "20"], "cm"),
]


def _attesi_borsa(valori, unita):
    try:
        m = [float(v.replace(",", ".")) for v in valori]
    except ValueError:
        return None
    if any(x <= 0 for x in m):
        return None
    return {C["slug"]: G.esito_compagnia(m, unita, C)[0] for C in G.COMPAGNIE}


def controlla_bagagli():
    from html import unescape
    errori, conti = [], {"compagnie": len(G.COMPAGNIE), "misure": 0, "citazioni": 0, "faq": 0}
    oggi = G.OGGI.isoformat()
    # nessun link affiliato attivo (decisione del 17/10/2026: siti solo informativi)
    for k, v in G.AFFILIATI.items():
        if isinstance(v, dict) and v.get("url"):
            errori.append(f"affiliati.json: la voce '{k}' ha un URL (link affiliato attivo: decisione del 17/10 ancora valida?)")
    if "bagagli" not in G.AFFILIATI:
        errori.append("affiliati.json: manca la voce vuota 'bagagli'")
    for f in SITO.rglob("*.html"):
        t = f.read_text(encoding="utf-8")
        if 'rel="sponsored' in t:
            errori.append(f"link affiliato attivo in {f.relative_to(SITO)}")
    for C in G.COMPAGNIE:
        rel = f"{G.BAG_BASE}/{C['slug']}/index.html"
        if not (SITO / rel).exists():
            errori.append(f"bagagli {C['slug']}: pagina mancante")
            continue
        t = leggi(rel)
        d = C["controllato_il"]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) or d > oggi:
            errori.append(f"bagagli {C['slug']}: data del controllo non valida {d}")
        if "checked on " + G.data_lunga(d) not in t:
            errori.append(f"bagagli {C['slug']}: data del controllo non mostrata")
        for k, f in C["fonti"].items():
            if not f.get("url", "").startswith("https://") or not f.get("titolo") or escape(f["url"]) not in t:
                errori.append(f"bagagli {C['slug']}: fonte {k} senza URL https, titolo o link nella pagina")
        tutte = [c for b in C["borse"] for c in b["cit"]] + [c for x in C["tariffe"] for c in x["cit"]] + C["avvisi"] + C.get("extra", [])
        for c in tutte:
            conti["citazioni"] += 1
            if c["f"] not in C["fonti"] or not c["righe"]:
                errori.append(f"bagagli {C['slug']}: citazione senza fonte o vuota")
            for r in c["righe"]:
                if escape(r) not in t:
                    errori.append(f"bagagli {C['slug']}: citazione ufficiale non mostrata: {r[:60]}")
        numeri_tutti = set().union(*[_numeri(" ".join(c["righe"])) for c in tutte])
        for b in C["borse"]:
            conti["misure"] += 1
            nb = set().union(*[_numeri(" ".join(c["righe"])) for c in b["cit"]]) if b["cit"] else set()
            if not b["cit"]:
                errori.append(f"bagagli {C['slug']}/{b['id']}: misura senza citazione ufficiale")
            if b["cm_ufficiali"] and not all(round(x, 2) in nb for x in b["cm"]):
                errori.append(f"bagagli {C['slug']}/{b['id']}: i centimetri {b['cm']} non sono tutti nella frase ufficiale")
            if b.get("pollici_ufficiali") and not all(round(x, 2) in nb for x in b["pollici"]):
                errori.append(f"bagagli {C['slug']}/{b['id']}: i pollici {b['pollici']} non sono tutti nella frase ufficiale")
            if not b["cm_ufficiali"] and (not b.get("pollici_ufficiali") or [round(x * 2.54, 2) for x in b["pollici"]] != [round(x, 2) for x in b["cm"]]):
                errori.append(f"bagagli {C['slug']}/{b['id']}: centimetri non ufficiali che non sono la conversione dei pollici ufficiali")
            if b.get("totale") and not (round(b["totale"]["cm"], 2) in nb and round(b["totale"]["in"], 2) in nb):
                errori.append(f"bagagli {C['slug']}/{b['id']}: totale non presente nella frase ufficiale")
            if b.get("peso") and not _numeri(b["peso"]) <= numeri_tutti:
                errori.append(f"bagagli {C['slug']}/{b['id']}: peso '{b['peso']}' non presente nelle frasi ufficiali")
            if escape(G.misura_testo(b, C)) not in t:
                errori.append(f"bagagli {C['slug']}/{b['id']}: misura non mostrata nella tabella")
        if escape(G.risposta_bag(C)) not in t:
            errori.append(f"bagagli {C['slug']}: risposta diretta in alto mancante")
        # FAQ: JSON-LD e testo visibile fatti solo di citazioni ufficiali intere
        ammesse = [" ".join(c["righe"]) for c in tutte]
        for blocco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t):
            x = json.loads(blocco)
            if x.get("@type") != "FAQPage":
                continue
            for q in x["mainEntity"]:
                conti["faq"] += 1
                testo = q["acceptedAnswer"]["text"]
                m = re.match(r"Quoted from (.+?) \(checked on ([^)]+)\): (.*)$", testo, re.S)
                if not m or m.group(2) != G.data_lunga(d) or any(n not in [f["titolo"] for f in C["fonti"].values()] for n in m.group(1).split("; ")):
                    errori.append(f"bagagli {C['slug']}: FAQ senza fonte o data corretta: {q['name']}")
                    continue
                if citazioni_faq(m.group(3), ammesse) is None:
                    errori.append(f"bagagli {C['slug']}: risposta FAQ con testo non ufficiale: {q['name']}")
                if escape(q["name"]) not in t:
                    errori.append(f"bagagli {C['slug']}: domanda FAQ non visibile: {q['name']}")
        if 'href="../../cabin-bags/does-my-bag-fit/"' not in t:
            errori.append(f"bagagli {C['slug']}: manca il collegamento allo strumento")
    # confronto: ordinamento (genera) contro le 6 rotazioni (indipendente) su casi casuali, in cm e pollici
    rnd = random.Random(11)
    for _ in range(4000):
        u = rnd.choice(["cm", "in"])
        m = [round(rnd.uniform(5, 70 if u == "cm" else 28), rnd.choice([0, 1, 2])) for _ in range(3)]
        for C in G.COMPAGNIE:
            for b in C["borse"]:
                if G.entra_borsa(m, u, b) != _entra_permutazioni(m, u, b):
                    errori.append(f"confronto borsa: ordinamento e rotazioni danno esiti diversi per {m} {u} su {C['slug']}/{b['id']}")
    # pagine per misura coerenti con i dati
    for sl, m in G.MISURE_COMUNI:
        rel = f"{G.BAG_BASE}/size/{sl}/index.html"
        t = leggi(rel)
        trovate = dict((s, e) for e, s in re.findall(r'<tr data-esito="(\w+)" data-slug="([\w-]+)"', t))
        atteso = {C["slug"]: G.esito_compagnia(list(m), "cm", C)[0] for C in G.COMPAGNIE}
        indip = {}
        for C in G.COMPAGNIE:
            e = "no"
            for b in C["borse"]:
                if _entra_permutazioni(list(m), "cm", b):
                    e = "gratis" if b["incluso"] == "tutte" else (e if e == "gratis" else "altre")
            indip[C["slug"]] = e
        if trovate != atteso or atteso != indip:
            errori.append(f"misura {sl}: elenco della pagina diverso dai dati ({ {k: (trovate.get(k), atteso[k], indip[k]) for k in atteso if not (trovate.get(k) == atteso[k] == indip[k])} })")
        for k in G.ESITO:
            n = sum(1 for v in atteso.values() if v == k)
            if k == "gratis" and f"<strong>{n} airline{'s' if n != 1 else ''}</strong>" not in t:
                errori.append(f"misura {sl}: conteggio 'free with every fare' sbagliato in alto")
    # indice, strumento, pagina UE, collegamenti
    ti = leggi(f"{G.BAG_BASE}/index.html")
    for C in G.COMPAGNIE:
        if f'href="../{G.BAG_BASE}/{C["slug"]}/"' not in ti:
            errori.append(f"indice bagagli: manca {C['slug']}")
    for E in G.BAG["escluse"]:
        if escape(E["nome"]) not in ti or escape(E["motivo"]) not in ti:
            errori.append(f"indice bagagli: compagnia esclusa {E['nome']} senza motivo")
    if "data-filtro-multi" not in ti:
        errori.append("indice bagagli: ricerca mancante")
    ts = leggi(G.BAG_STRUMENTO + "index.html")
    if "data-borsa" not in ts or 'id="borse-dati"' not in ts or "longest side" not in ts or "official rule decides" not in ts:
        errori.append("strumento: modulo, dati o spiegazione del confronto mancanti")
    U = G.BAG["ue"]
    tu = leggi(G.BAG_UE + "index.html")
    for c in U["citazioni"]:
        for r in c["righe"]:
            if escape(r) not in tu:
                errori.append(f"pagina UE: citazione mancante {r[:60]}")
    for k, f in U["fonti"].items():
        if escape(f["url"]) not in tu or not any(h in f["url"] for h in ("europa.eu",)):
            errori.append(f"pagina UE: fonte {k} mancante o non ufficiale UE")
    for x in U["iter"]:
        if f'{G.data_lunga(x["data"])}</td><td data-l="Step">{escape(x["evento"])}' not in tu:
            errori.append(f"pagina UE: tappa {x['data']} mancante")
    if "checked on " + G.data_lunga(U["controllato_il"]) not in tu or "It shall apply from 23 October 2027." not in tu:
        errori.append("pagina UE: data del controllo o data di applicazione mancanti")
    for a in G.AER["aeroporti"] + G.AER["nazionali"]:
        if 'href="../../cabin-bags/"' not in leggi(f"liquids/{a['slug']}/index.html"):
            errori.append(f"liquidi {a['slug']}: manca il collegamento a Cabin bag size by airline")
    th = leggi("index.html")
    if 'href="cabin-bags/"' not in th or ">Cabin bags</a>" not in th:
        errori.append("home: manca il collegamento (riquadro o menu) ai bagagli")
    return errori, conti


def controlla_js_borsa():
    """Motore JS del controllo (stesso testo delle pagine) contro Python su 3.000 casi casuali, in cm e pollici."""
    rnd = random.Random(5)
    casi = []
    for _ in range(3000):
        u = rnd.choice(["cm", "in"])
        casi.append([[round(rnd.uniform(5, 70 if u == "cm" else 28), rnd.choice([0, 1, 2])) for _ in range(3)], u])
    motore = G.BAG_JS.split("(function(){")[0]
    script = (motore + "\nvar D=" + json.dumps(G.dati_bag_client()) + ";var casi=" + json.dumps(casi) + ";\n"
              "console.log(JSON.stringify(casi.map(function(c){return D.map(function(C){return bfCompagnia(c[0],c[1],C).esito;});})));")
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(script)
    try:
        r = subprocess.run(["node", fh.name], capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        return ["node non trovato: confronto JS della borsa saltato"]
    finally:
        os.unlink(fh.name)
    if r.returncode != 0:
        return ["Errore JS borsa: " + r.stderr[:500]]
    errori = []
    for (m, u), js in zip(casi, json.loads(r.stdout)):
        py = [G.esito_compagnia(m, u, C)[0] for C in G.COMPAGNIE]
        if py != js:
            errori.append(f"borsa: JS diverso dal Python per {m} {u}")
    return errori[:20]


# ---------------------------------------------------------------- 13. documenti per chi ha la cittadinanza italiana (Viaggiare Sicuri)
RIT = _carica("documenti_it")
MAX_COPIA = 25  # nessuna pagina italiana può avere più di 25 parole di fila uguali a un testo delle schede
N_GRAM = 10
# controllo indipendente (più semplice della raccolta): parole che indicano un'autorizzazione o un modulo obbligatorio
AUT_IND = re.compile(r"\bESTA\b|\beTA\b|\bETA\b|NZeTA|K-ETA|ETA-IL|(?i:autorizzazione (?:elettronica|di viaggio|all['’]\s?ingresso|preventiva)|arrival card|"
                     r"modulo ED|e-ticket|travel authori[sz]ation|tarjeta de turista)")
ALTRO_IND = re.compile(r"transit|\bscal[oi]\b|Irlanda del Nord|residen|esent|non (?:è|e['’]) richiest|consiglia|invit|raccomand", re.I)
PROMESSE_IT = re.compile(r"aggiornat[oaie] ogni (?:settimana|mese|giorno)|ogni (?:settimana|mese) ricontroll|settimanalmente|mensilmente|ricontrolliamo ogni", re.I)
NUM_PAROLA = {"1": "un|uno|una|primo", "2": "due", "3": "tre", "5": "cinque", "6": "sei", "12": "dodici", "30": "trenta", "90": "novanta"}


def _parole_it(testo):
    return re.findall(r"\w+", testo.replace("’", "'").lower())


def _testo_visibile(html_):
    from html import unescape
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", html_, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return unescape(t)


def _testi_fonte(j):
    """Tutti i testi di una scheda (ogni sezione), senza HTML."""
    out = []

    def giro(x):
        if isinstance(x, dict):
            for y in x.values():
                giro(y)
        elif isinstance(x, list):
            for y in x:
                giro(y)
        elif isinstance(x, str) and len(x) > 40:
            out.append(_testo_visibile(x))
    giro(j)
    return out


def _ngram_fonti():
    g = set()
    for f in RIT.CACHE.glob("[A-Z][A-Z][A-Z].json"):
        for t in _testi_fonte(json.loads(f.read_text(encoding="utf-8"))):
            w = _parole_it(t)
            for i in range(len(w) - N_GRAM + 1):
                g.add(hash(tuple(w[i:i + N_GRAM])))
    return g


def _run_massimo(parole_pag, g):
    """Lunghezza della più lunga sequenza di parole della pagina uguale a una sequenza della fonte (approssimata dalle finestre di N_GRAM parole)."""
    migliore, corrente = 0, 0
    for i in range(len(parole_pag) - N_GRAM + 1):
        if hash(tuple(parole_pag[i:i + N_GRAM])) in g:
            corrente += 1
            migliore = max(migliore, corrente)
        else:
            corrente = 0
    return migliore + N_GRAM - 1 if migliore else 0


def _citazioni_fatto(f):
    qq = list(f.get("citazioni") or ([f["citazione"]] if f.get("citazione") else []))
    qq += list(f.get("citazioni_note", [])) + [x["citazione"] for x in f.get("formalita", [])]
    for c in ("condizione", "durata"):
        if f.get(c):
            qq.append(f[c])
    return qq


def _numero_in(n, testo):
    alt = str(n) + ("|" + NUM_PAROLA[str(n)] if str(n) in NUM_PAROLA else "")
    return bool(re.search(r"(?<![\d])(?:" + alt + r")(?![\d])", testo, re.I))


def controlla_italiani():
    errori, conti = [], {"pagine": 0, "senza": 0, "doc": 0, "val": 0, "vis": 0, "manuali": 0, "citazioni": 0, "faq": 0, "copia_max": 0}
    D = G.DOC_IT
    if not D:
        return ["documenti per italiani: manca dati/documenti_it.json"], conti
    if not RIT.CACHE.exists() or len(list(RIT.CACHE.glob("[A-Z][A-Z][A-Z].json"))) < 0.8 * D["schede_elenco"]:
        return [f"documenti per italiani: cache delle schede assente in {RIT.CACHE} (non è nel repository per la licenza incerta): "
                "lanciare prima `python3 -I beforeyoufly/raccolta/documenti_it.py`"], conti
    if len(D["paesi"]) < 0.8 * D["schede_elenco"]:
        errori.append(f"documenti per italiani: lette {len(D['paesi'])} schede su {D['schede_elenco']}")
    manuali = json.loads(RIT.FILE_MANUALI.read_text(encoding="utf-8"))["paesi"] if RIT.FILE_MANUALI.exists() else {}
    con_pagina = {v["p"]["iso3"]: v for v in G.VOCI_IT}
    for p in D["paesi"]:
        iso = p["iso3"]
        # a) la cache è la stessa versione della scheda da cui vengono i fatti (impronte), e i fatti sono quelli che dà la lettura sul campo salvato
        try:
            campi, j = RIT.campi_da_cache(iso)
        except FileNotFoundError:
            errori.append(f"{iso}: scheda non in cache")
            continue
        imp = {k: RIT.impronta(v) for k, v in campi.items()}
        if imp != p["impronte"]:
            errori.append(f"{iso}: la scheda in cache non è quella da cui sono stati scritti i fatti (impronte diverse): rilanciare la raccolta e genera.py")
            continue
        if p["aggiornata"] != RIT.data_scheda(j.get("updateDate", "")):
            errori.append(f"{iso}: data della scheda diversa dalla cache")
        rec, _, scaduti = RIT.leggi_paese({"Codice-3": iso, "Codice-2": p["iso2"], "Nome": p["nome_fonte"]}, j)
        for k in ("documento", "validita", "visto", "note_extra", "cronologia"):
            if rec.get(k) != p.get(k):
                errori.append(f"{iso}: fatto «{k}» diverso da quello ricalcolato sul campo salvato")
        if scaduti:
            errori.append(f"{iso}: fatti scritti a mano su una versione vecchia della scheda: {scaduti}")
        if not p["url"].startswith(RIT.PAGINA) or not p["aggiornata"]:
            errori.append(f"{iso}: link o data della scheda mancanti")
        testi = {k: RIT.testo(v) for k, v in campi.items()}
        # b) ogni fatto è legato a un campo della scheda e ogni citazione è in quel campo, parola per parola, al massimo 20 parole
        fatti = [(k, p[k]) for k in ("documento", "validita", "visto")] + [("note_extra", x) for x in p.get("note_extra", [])]
        for k, f in fatti:
            if not f.get("esito") and k != "note_extra":
                if not f.get("motivo"):
                    errori.append(f"{iso} {k}: niente riassunto ma nessun motivo")
                continue
            campo = f.get("campo")
            if campo not in testi:
                errori.append(f"{iso} {k}: fatto senza campo della scheda")
                continue
            qq = _citazioni_fatto(f)
            if not qq:
                errori.append(f"{iso} {k}: fatto senza citazione")
            for q in qq:
                conti["citazioni"] += 1
                if not RIT.in_campo(q, testi[campo]):
                    errori.append(f"{iso} {k}: citazione non trovata nel campo «{campo}»: {q[:70]}")
                if len(q.replace(RIT.ELISIONE, " ").split()) > RIT.MAX_PAROLE:
                    errori.append(f"{iso} {k}: citazione di più di {RIT.MAX_PAROLE} parole")
            for q in f.get("obblighi_pp", []):  # obblighi scritti solo nel riquadro "In primo piano": citazione breve da quel campo
                conti["citazioni"] += 1
                if not RIT.in_campo(q, testi["primo_piano"]):
                    errori.append(f"{iso} {k}: citazione del riquadro «In primo piano» non trovata: {q[:70]}")
                if len(q.replace(RIT.ELISIONE, " ").split()) > RIT.MAX_PAROLE:
                    errori.append(f"{iso} {k}: citazione del riquadro «In primo piano» di più di {RIT.MAX_PAROLE} parole")
            if f.get("manuale") and not f.get("scritto_il"):
                errori.append(f"{iso} {k}: fatto scritto a mano senza data")
            nostre = " ".join([f.get("sintesi", ""), f.get("testo", "")] + list(f.get("note", [])))
            for n in re.findall(r"\d+", nostre):
                if not any(_numero_in(n, q) for q in qq):
                    errori.append(f"{iso} {k}: il numero {n} della frase nostra non è in nessuna citazione")
            if f.get("manuale"):
                conti["manuali"] += 1
                if iso not in manuali or not imp[campo].startswith(manuali[iso]["campi"][campo]):
                    errori.append(f"{iso} {k}: fatto manuale senza impronta valida")
            # c) controlli indipendenti sui fatti automatici
            if f.get("manuale"):
                continue
            if k == "documento":
                tp = testi["passaporto"]
                if f["esito"] == "cie" and not re.search(r"\bCIE\b", tp):
                    errori.append(f"{iso}: «passaporto o CIE» ma il campo non nomina la CIE")
                if f["esito"] == "passaporto" and re.search(r"\bCIE\b|carta d['’]\s?identit[àa] (?:elettronica|valida)|carta di identit[àa] (?:elettronica|valida)", tp):
                    errori.append(f"{iso}: «serve il passaporto» ma il campo nomina la carta d'identità")
                if f["esito"] == "solo_passaporto" and not re.search(r"UNICAMENTE|soltanto|esclusivamente|Non è ammesso alcun altro documento", tp):
                    errori.append(f"{iso}: «solo passaporto» senza una frase che lo dica")
            if k == "validita" and f["esito"] == "numero":
                if not _numero_in(f["n"], f["citazione"]) or not re.search(r"validit|scadenza|valid[oa]", f["citazione"], re.I):
                    errori.append(f"{iso}: validità di {f['n']} {f['unita']} senza il numero nella citazione")
                altri = set()
                for fr in RIT.tutte_frasi(campi["passaporto"]):
                    if re.search(r"massima|residen|provvisori|variazion|modifich|per recarsi|extra-?UE|pi[ùu] di \d|oltre i \d|permesso di soggiorno", fr, re.I):
                        continue
                    for m in re.finditer(r"(\d+|tre|sei|cinque)\s*(?:\(\w+\)\s*)?(mesi|giorni)[^.;]{0,25}?validit|validit\S*\s+(?:residua\s+)?(?:\S+\s+){0,4}?(\d+|tre|sei|cinque)\s*(?:\(\w+\)\s*)?(mesi|giorni)", fr, re.I):
                        x = (m.group(1) or m.group(3)).lower()
                        altri.add(RIT.NUMERI_P.get(x) or int(x))
                if altri - {f["n"]}:
                    errori.append(f"{iso}: la scheda indica anche altre validità ({sorted(altri)}) ma la pagina ne riassume una sola")
            if k == "visto" and f["esito"] == "non_necessario":
                nomi = [x["nome"].split(" (")[0] for x in f.get("formalita", [])]
                for fr in RIT.tutte_frasi(campi["visto"]):
                    m = AUT_IND.search(fr)
                    if m and not any(nm.split()[0] in fr for nm in nomi) and not ALTRO_IND.search(fr):
                        errori.append(f"{iso}: «non serve il visto» ma la scheda parla di «{m.group(0)}» e la pagina non lo dice: {fr[:80]}")
        # d) pagina: c'è solo se la scheda ha un contenuto specifico; mostra fonte, data, avvertenze, citazioni, FAQ dai fatti
        if iso not in con_pagina:
            conti["senza"] += 1
            if (G.SITO / G.IT_BASE / G.NOMI_IT[iso]["slug"] / "index.html").exists():
                errori.append(f"{iso}: pagina pubblicata per una scheda senza contenuto da riassumere")
            continue
        v = con_pagina[iso]
        conti["pagine"] += 1
        conti["doc"] += bool(p["documento"].get("esito"))
        conti["val"] += bool(p["validita"].get("esito"))
        conti["vis"] += bool(p["visto"].get("esito"))
        t = leggi(v["url_pag"] + "index.html")
        for atteso in ('<html lang="it">', escape(p["url"]), f"scheda aggiornata {G.con_art('il', G.data_it(p['aggiornata']))}", "non è della Farnesina",
                       "controlla la scheda ufficiale prima di partire", G.GOATCOUNTER_URL, f'<link rel="canonical" href="{G.URL_SITO}/{v["url_pag"]}">',
                       'id="documento"', 'id="validita"', 'id="visto"'):
            if atteso not in t:
                errori.append(f"{iso}: nella pagina manca «{atteso[:50]}»")
        for k, f in fatti:
            for q in (_citazioni_fatto(f) if (f.get("esito") or k == "note_extra") else []):
                if escape(q) not in t:
                    errori.append(f"{iso} {k}: citazione non mostrata nella pagina: {q[:60]}")
            if not f.get("esito") and k != "note_extra" and "Consulta la scheda ufficiale" not in t:
                errori.append(f"{iso} {k}: senza riassunto ma la pagina non dice di consultare la scheda")
            for q in f.get("obblighi_pp", []):
                if escape(q) not in t:
                    errori.append(f"{iso} {k}: obbligo del riquadro «In primo piano» non mostrato nella pagina: {q[:60]}")
            if f.get("manuale") and f"Riassunto scritto a mano da noi {G.con_art('il', G.data_it(f['scritto_il']))}" not in t:
                errori.append(f"{iso} {k}: fatto scritto a mano senza la data nella pagina")
        if PROMESSE_IT.search(t):
            errori.append(f"{iso}: promessa di aggiornamento periodico")
        faq = G.faq_it(v)
        conti["faq"] += len(faq)
        ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t)]
        fq = next((x for x in ld if x.get("@type") == "FAQPage"), None)
        if faq and (not fq or [(e["name"], e["acceptedAnswer"]["text"]) for e in fq["mainEntity"]] != faq):
            errori.append(f"{iso}: FAQ JSON-LD diversa dalle domande ricavate dai fatti")
        for q, a in faq:
            if f"<h3>{escape(q)}</h3><p>{escape(a)}</p>" not in t:
                errori.append(f"{iso}: FAQ visibile diversa dal JSON-LD: {q}")
        # e) collegamenti con la pagina britannica della stessa destinazione (andata e ritorno)
        for s in v["uk"]:
            if f'passport-validity/{s}/' not in t:
                errori.append(f"{iso}: manca il link alla pagina britannica {s}")
            tuk = leggi(f"passport-validity/{s}/index.html")
            if f'{v["url_pag"]}"' not in tuk or "Italian citizens: " not in tuk:
                errori.append(f"{s}: manca il link «Italian citizens: documenti per italiani» verso {v['url_pag']}")
    # f) nessun testo lungo copiato: più di MAX_COPIA parole di fila uguali a una scheda (tutte le sezioni di tutte le schede)
    g = _ngram_fonti()
    pagine_it = list((G.SITO / "it").rglob("*.html"))
    for f in pagine_it:
        r = _run_massimo(_parole_it(_testo_visibile(f.read_text(encoding="utf-8"))), g)
        conti["copia_max"] = max(conti["copia_max"], r)
        if r > MAX_COPIA:
            errori.append(f"{f.relative_to(G.SITO)}: {r} parole di fila uguali al testo di una scheda (massimo {MAX_COPIA})")
    # g) indice: tutte le schede, ricerca, link alle pagine o alla scheda ufficiale; sezione metodo con fonte e licenza
    ti = leggi(f"{G.IT_BASE}/index.html")
    if ti.count("<tr data-voce>") != len(D["paesi"]) or 'data-filtro="lista-it"' not in ti or 'id="metodo"' not in ti:
        errori.append("indice italiano: righe, ricerca o sezione metodo mancanti")
    for v in G.SENZA_PAGINA_IT:
        if escape(v["p"]["url"]) not in ti:
            errori.append(f"indice italiano: {v['nome']} senza pagina e senza link alla scheda ufficiale")
    for v in G.VOCI_IT:
        if f'href="../../{v["url_pag"]}"' not in ti:
            errori.append(f"indice italiano: manca il link a {v['url_pag']}")
    if "non indica una licenza" not in ti:
        errori.append("indice italiano: manca la spiegazione sulla licenza dei testi")
    sm = leggi("sitemap.xml")
    for v in G.SENZA_PAGINA_IT:
        if f"/{v['url_pag']}<" in sm:
            errori.append(f"sitemap: {v['url_pag']} senza pagina")
    if "it/documenti/" not in leggi("index.html") or "documenti per italiani" not in leggi("passport-validity/index.html"):
        errori.append("home o indice britannico senza link alla sezione italiana")
    return errori, conti


# Parole vietate scritte al contrario, così questo file non le contiene in chiaro.
_AL_CONTRARIO = ["edualc", "ciporhtna", "ianepo", "tpgtahc", "inimeg", "tolipoc", "amall", "lartsim", "supo", "tennos", "ukiah"]
VIETATE = re.compile(r"\b(" + "|".join(w[::-1] for w in _AL_CONTRARIO) + r"|gpt-\d)\b", re.I)


def controlla_parole():
    errori = []
    cartelle = [SITO, SITO.parent / "dati", SITO.parent / "raccolta"]
    for c in cartelle:
        for f in c.rglob("*"):
            if ".cache" in f.parts:  # testi grezzi delle fonti ufficiali (fuori dal repository): non sono file nostri
                continue
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
    for (const u of ['/', '/passport-validity/spain/', '/liquids/', '/liquids/barcelona/', '/passport-validity/egypt/'].concat(JSON.parse(process.argv[4])).concat(JSON.parse(process.argv[6])).concat(JSON.parse(process.argv[7]))) {
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
      if (tema === 'light' && u === '/cabin-bags/does-my-bag-fit/') {
        const casi = JSON.parse(process.argv[5]);
        for (let i = 0; i < casi.length; i++) { const c = casi[i];
          await p.fill('[name=a]', c[1][0]); await p.fill('[name=b]', c[1][1]); await p.fill('[name=c]', c[1][2]); await p.selectOption('[name=unita]', c[2]);
          const r = await p.evaluate(() => { const m = {}; document.querySelectorAll('[data-gruppo] li[data-slug]').forEach(li => { m[li.dataset.slug] = li.closest('[data-gruppo]').dataset.gruppo; });
            return { mappa: m, errore: !!document.querySelector('[data-errore-borsa]'), testo: document.querySelector('[data-out]').textContent }; });
          out.prove.push({ caso: 'borsa:' + i, testo: r.testo, mappa: r.mappa, errore: r.errore });
          if (i === 0) await p.screenshot({ path: process.argv[3] + '/borsa-375.png', fullPage: false }); }
      }
      if (u.startsWith('/cabin-bags/')) {
        out.prove.push({ caso: 'bag:' + tema + ':' + u, testo: await p.textContent('main'),
                         citazioni: await p.$$eval('blockquote.cit', e => e.filter(x => x.getBoundingClientRect().height > 0).length) });
        if (tema === 'light') await p.screenshot({ path: process.argv[3] + '/' + u.split('/').filter(Boolean).join('-') + '-375.png', fullPage: true });
      }
      if (u.startsWith('/canadian-passport/') || u.startsWith('/australian-passport/')) {
        const vis = async (sel) => p.$eval(sel, e => { const r = e.getBoundingClientRect(); return r.height > 0 && r.width > 0 && r.width <= window.innerWidth; }).catch(() => false);
        out.prove.push({ caso: 'estero:' + tema + ':' + u, testo: await p.textContent('main'), visa: await vis('#visa'), passport: await vis('#passport'),
                         citazioni: await p.$$eval('blockquote.cit', e => e.filter(x => x.getBoundingClientRect().height > 0).length) });
        if (tema === 'light') await p.screenshot({ path: process.argv[3] + '/' + u.split('/').filter(Boolean).join('-') + '-375.png', fullPage: false });
      }
      if (u.startsWith('/it/documenti/')) {
        const vis = async (sel) => p.$eval(sel, e => { const r = e.getBoundingClientRect(); return r.height > 0 && r.width > 0 && r.width <= window.innerWidth; }).catch(() => false);
        const x = { caso: 'it:' + tema + ':' + u, testo: await p.textContent('main'), lang: await p.$eval('html', e => e.lang),
                    documento: await vis('#documento'), visto: await vis('#visto'), citazioni: await p.$$eval('blockquote.cit', e => e.filter(y => y.getBoundingClientRect().height > 0).length) };
        if (u === '/it/documenti/') {
          await p.fill('[data-filtro=lista-it]', 'egit');
          x.righe = await p.$$eval('#lista-it tr[data-voce]', e => e.filter(y => !y.hidden).map(y => y.textContent.trim().slice(0, 40)));
          await p.fill('[data-filtro=lista-it]', '');
        }
        out.prove.push(x);
        if (tema === 'light') await p.screenshot({ path: process.argv[3] + '/' + u.split('/').filter(Boolean).join('-') + '-375.png', fullPage: false });
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
  const largo = await b.newContext({ viewport: { width: 820, height: 900 } });
  for (const u of ['/', '/cabin-bags/', '/cabin-bags/ryanair/']) { const p = await largo.newPage(); await p.goto(base + u, { waitUntil: 'load' });
    const w = await p.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]); out.pagine.push({ url: u, tema: '820px', scroll: w[0], larghezza: w[1], errori: [] }); await p.close(); }
  await largo.close();
  await b.close(); srv.close(); console.log(JSON.stringify(out)); });
"""


def _pagine_estere():
    """4 pagine nuove per la prova a 375 px: 2 canadesi e 2 australiane (Giappone e Francia, se esistono; altrimenti le prime disponibili)."""
    out = []
    for k in G.ESTERI:
        vv = G.VOCI[k]
        scelte = [v for v in vv if v["slug"] in ("japan", "france")] or vv[:2]
        if len(scelte) < 2:
            scelte += [v for v in vv if v not in scelte][:2 - len(scelte)]
        out += ["/" + v["url_pag"] for v in scelte[:2]]
    return out


PAGINE_ESTERE_BROWSER = _pagine_estere()
PAGINE_IT_BROWSER = ["/it/documenti/", "/it/documenti/egitto/", "/it/documenti/spagna/", "/it/documenti/stati-uniti/"]
PAGINE_BAG_BROWSER = ["/cabin-bags/", "/cabin-bags/ryanair/", "/cabin-bags/does-my-bag-fit/", "/cabin-bags/size/40x30x20/", "/cabin-bags/eu-personal-item-rule/"]


def controlla_browser():
    if os.environ.get("BYF_NO_BROWSER") == "1":
        return ["controllo nel browser saltato (BYF_NO_BROWSER=1)"], None
    cartella = tempfile.mkdtemp()
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(BROWSER_JS)
    try:
        r = subprocess.run(["node", fh.name, str(SITO), cartella, json.dumps(PAGINE_ESTERE_BROWSER), json.dumps(CASI_BORSA), json.dumps(PAGINE_BAG_BROWSER),
                            json.dumps(PAGINE_IT_BROWSER)],
                           capture_output=True, text=True, timeout=600)
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
    for u in PAGINE_ESTERE_BROWSER:
        for tema in ("light", "dark"):
            x = next((y for y in o["prove"] if y["caso"] == f"estero:{tema}:{u}"), None)
            if not x:
                errori.append(f"{u} ({tema}): prova nel browser non eseguita")
                continue
            pop = "Canadians" if u.startswith("/canadian") else "Australians"
            if not x["visa"] or not x["passport"] or x["citazioni"] < 2 or f"Do {pop} need a visa for" not in x["testo"]:
                errori.append(f"{u} ({tema}): sezione visti o validità non visibile, o citazioni ufficiali mancanti a 375 px")
    if len(PAGINE_ESTERE_BROWSER) < 4:
        errori.append(f"prova nel browser su {len(PAGINE_ESTERE_BROWSER)} pagine nuove invece di 4 (mancano i dati di un passaporto?)")
    for i, (nome, valori, unita) in enumerate(CASI_BORSA):
        x = next((y for y in o["prove"] if y["caso"] == f"borsa:{i}"), None)
        atteso = _attesi_borsa(valori, unita)
        if not x:
            errori.append(f"strumento borsa: caso '{nome}' non eseguito")
        elif atteso is None:
            if not x["errore"] or x["mappa"]:
                errori.append(f"strumento borsa: caso '{nome}' doveva dare un messaggio d'errore e nessun risultato")
        elif x["mappa"] != atteso:
            diff = {k: (x["mappa"].get(k), v) for k, v in atteso.items() if x["mappa"].get(k) != v}
            errori.append(f"strumento borsa: caso '{nome}' diverso dal Python (browser, atteso): {diff}")
    p0 = next((y for y in o["prove"] if y["caso"] == "borsa:0"), {}); p1 = next((y for y in o["prove"] if y["caso"] == "borsa:1"), {})
    if not p0.get("mappa") or p0.get("mappa") != p1.get("mappa"):
        errori.append("strumento borsa: la borsa ruotata non dà lo stesso risultato")
    for u in PAGINE_BAG_BROWSER:
        for tema in ("light", "dark"):
            x = next((y for y in o["prove"] if y["caso"] == f"bag:{tema}:{u}"), None)
            if not x or (u != "/cabin-bags/does-my-bag-fit/" and u != "/cabin-bags/" and u != "/cabin-bags/size/40x30x20/" and x["citazioni"] < 2):
                errori.append(f"{u} ({tema}): pagina non provata o citazioni ufficiali non visibili a 375 px")
    rb = next((y for y in o["prove"] if y["caso"] == "bag:light:/cabin-bags/ryanair/"), {})
    if "Ryanair free bag: 40 x 30 x 20 cm under the seat" not in rb.get("testo", ""):
        errori.append("Ryanair: risposta diretta non visibile nel browser")
    for u in PAGINE_IT_BROWSER:
        for tema in ("light", "dark"):
            x = next((y for y in o["prove"] if y["caso"] == f"it:{tema}:{u}"), None)
            if not x:
                errori.append(f"{u} ({tema}): prova nel browser non eseguita")
                continue
            if x["lang"] != "it" or "Le regole cambiano" not in x["testo"]:
                errori.append(f"{u} ({tema}): lingua o avvertenza mancanti")
            if u != "/it/documenti/" and (not x["documento"] or not x["visto"] or x["citazioni"] < 2):
                errori.append(f"{u} ({tema}): sezioni documento/visto o citazioni non visibili a 375 px")
            if u == "/it/documenti/" and tema == "light" and (len(x.get("righe", [])) != 1 or "Egitto" not in x["righe"][0]):
                errori.append(f"indice italiano: la ricerca «egit» non lascia solo l'Egitto: {x.get('righe')}")
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
        n375 = sum(1 for x in o["pagine"] if x["tema"] in ("light", "dark"))
        print(f"7. Browser 375 px: {len(o['pagine'])} viste ({n375 // 2} pagine × tema chiaro e scuro + {len(o['pagine']) - n375} a 820 px; nuove: "
              f"{', '.join(PAGINE_ESTERE_BROWSER + PAGINE_BAG_BROWSER + PAGINE_IT_BROWSER)}; {len(CASI_BORSA)} casi dello strumento borsa), "
              f"{len(o['prove'])} prove, {len(e7)} errori; schermate in {cartella}")
    else:
        print(f"7. Browser 375 px: {e7[0] if e7 else ''}")
    e8, (con, solo, senza) = controlla_visti()
    print(f"8. Visti: {con} riassunti da schema riconosciuto, {solo} solo citazione, {senza} senza sezione visti: {len(e8)} errori")
    e9, n_faq = controlla_liquidi_nuovi()
    print(f"9. Liquidi: risposta diretta e {n_faq} risposte FAQ fatte solo di citazioni ufficiali: {len(e9)} errori")
    e10, lunghi = controlla_meta()
    print(f"10. Titoli <= 65 e descrizioni <= 160: {len(e10)} errori" + (f"; titoli più lunghi senza alternativa più corta prevista: {lunghi}" if lunghi else ""))
    e11, conti = controlla_esteri()
    for k, c in conti.items():
        print(f"11. Passaporto {G.ESTERI[k]['agg']}: {c['pagine']} pagine; validità {c['val']} riassunti, {c['val_cit']} solo citazione; "
              f"visto {c['vis']} riassunti, {c['vis_cit']} solo citazione")
    print(f"11. Passaporti canadese e australiano (riassunti ricalcolati, modelli fissi, citazioni, fonti, licenze, link): {len(e11)} errori")
    e12, cb = controlla_bagagli()
    e12 += controlla_js_borsa()
    print(f"12. Bagaglio a mano: {cb['compagnie']} compagnie, {cb['misure']} misure, {cb['citazioni']} citazioni, {cb['faq']} risposte FAQ, "
          f"{len(G.MISURE_COMUNI)} pagine per misura, motore JS e rotazioni, pagina UE, affiliati spenti: {len(e12)} errori")
    e13, ci = controlla_italiani()
    print(f"13. Documenti per italiani: {ci['pagine']} pagine Paese ({ci['senza']} schede senza pagina); riassunti: documento {ci['doc']}, validità {ci['val']}, "
          f"visto {ci['vis']} ({ci['manuali']} fatti scritti a mano); {ci['citazioni']} citazioni controllate sul campo della scheda; {ci['faq']} risposte FAQ; "
          f"testo uguale alla fonte al massimo {ci['copia_max']} parole di fila (limite {MAX_COPIA}): {len(e13)} errori")
    tutti = e1 + e2 + e3 + e4 + e5 + e6 + (e7 if info else []) + e8 + e9 + e10 + e11 + e12 + e13
    for e in tutti:
        print(" -", e)
    if tutti:
        sys.exit(1)
    print("TUTTO OK")


if __name__ == "__main__":
    main()
