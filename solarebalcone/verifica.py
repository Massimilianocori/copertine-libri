"""Controlli di Balcony Solar Europe (solarebalcone/sito/) prima di pubblicare.

Uso (dalla radice del repository):
    python3 solarebalcone/verifica.py              # controlli sui file (senza rete)
    python3 solarebalcone/verifica.py --rete       # + fonti rilette (HTTP 200 e frasi presenti) e un campione PVGIS ricalcolato
    python3 solarebalcone/verifica.py --browser    # + Playwright: 375 e 1280 px, chiaro e scuro, calcolatore (verifica_browser.js)

Cosa controlla:
 1. Fonti: ogni fonte di dati/regole.json è stata letta con HTTP 200, ha l'impronta (sha256) e tutte le frasi di "cerca",
    oppure è dichiarata non letta con il motivo scritto; ogni affermazione ha fonti esistenti o è una nota nostra.
 2. PVGIS: ogni città ha i due montaggi, 12 mesi che sommano al totale annuo, URL coerente con le coordinate e impronta;
    con --rete 5 città a caso ricalcolate sull'API (scarto ammesso 0,5%).
 3. Calcolatore: la formula JS (node, file app.*.js pubblicato) dà gli stessi numeri della formula Python per ogni città,
    montaggio e diversi input; i numeri stampati nelle pagine città e nella tabella coincidono con il calcolo.
 4. FAQ: ogni domanda viene da una ricerca salvata (dati/domanda.json); il JSON-LD FAQPage è uguale al testo visibile.
 5. hreflang reciproci e verso pagine esistenti; link interni e ancore; sitemap = pagine con canonical; titoli e descrizioni.
 6. Monetizzazione: controlli comuni (monetizzazione.py); nessun link di affiliazione finché i riquadri sono spenti.
 7. Niente dati personali, niente nomi di modelli AI, niente pagine città senza domanda vera; /de/ non pubblicata.
"""
import hashlib
import json
import random
import re
import subprocess
import sys
import urllib.request
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
SITO = RADICE / "sito"
sys.path.insert(0, str(RADICE))
sys.path.insert(0, str(RADICE / "raccolta"))
import genera as G  # noqa: E402
import monetizzazione as MON  # noqa: E402

ERRORI = []


def errore(m):
    ERRORI.append(m)


def testo(html):
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", t))).strip()


def pagine():
    return sorted(SITO.rglob("*.html"))


def percorso_di(f):
    rel = f.relative_to(SITO).as_posix()
    return rel[:-len("index.html")] if rel.endswith("index.html") else rel


# ---------------------------------------------------------------- 1. fonti e affermazioni
def controlla_fonti(rete):
    fonti, esiti = G.REGOLE["fonti"], G.FONTI_ESITO
    lette = non_lette = 0
    for fid, f in fonti.items():
        e = esiti.get(fid)
        if not e:
            errore(f"fonte {fid}: nessun esito in dati/fonti.json")
            continue
        if f.get("non_letta"):
            non_lette += 1
            if not (f.get("motivo") and e.get("motivo")):
                errore(f"fonte {fid}: non letta senza motivo scritto")
            continue
        lette += 1
        if e.get("http") != 200 or not re.fullmatch(r"[0-9a-f]{64}", e.get("sha256", "")):
            errore(f"fonte {fid}: HTTP {e.get('http')} o impronta mancante")
        mancano = [c for c, ok in e.get("trovate", {}).items() if not ok]
        if mancano or set(e.get("trovate", {})) != set(f.get("cerca", [])):
            errore(f"fonte {fid}: frasi non trovate o non controllate: {mancano}")
    for l in G.LINGUE_ATTIVE:
        P = G.REGOLE["paesi"][l]
        for s in P["sezioni"]:
            for p in s["punti"]:
                if p.get("nota"):
                    if p.get("s"):
                        errore(f"{l}/{s['id']}: nota nostra con fonti (o è una nota o è un fatto)")
                    continue
                for i in p.get("s", []):
                    if i not in fonti:
                        errore(f"{l}/{s['id']}: fonte {i} inesistente")
                if not p.get("s"):
                    errore(f"{l}/{s['id']}: affermazione senza fonte")
        for q in P["faq"]:
            for i in q["s"]:
                if i not in fonti:
                    errore(f"{l} FAQ {q['q']}: fonte {i} inesistente")
    if rete:
        import fonti as RF
        for fid, f in fonti.items():
            if f.get("non_letta"):
                continue
            codice, corpo = RF.leggi_fonte(f)
            if codice != 200:
                errore(f"fonte {fid}: oggi HTTP {codice} (registrata 200): rileggere con raccolta/fonti.py")
                continue
            t = RF.testo_pdf(corpo) if (f.get("pdf") or corpo[:5] == b"%PDF-") else RF.testo_html(corpo)
            mancano = [c for c in f.get("cerca", []) if RF.normalizza(c) not in t]
            if mancano:
                errore(f"fonte {fid}: oggi mancano le frasi {mancano}: la fonte è cambiata, rileggerla")
    print(f"1. Fonti: {lette} lette con HTTP 200 e impronta, {non_lette} non lette con motivo scritto"
          f"{' (rilette oggi in rete)' if rete else ''}.")


# ---------------------------------------------------------------- 2. PVGIS
def controlla_pvgis(rete):
    import pvgis as RP
    n = 0
    for l in G.LINGUE_ATTIVE:
        for c in G.CITTA[l]:
            k = f"{l}/{c['slug']}"
            v = G.PVGIS["citta"].get(k)
            if not v:
                errore(f"PVGIS: manca {k}")
                continue
            for m, ang in RP.MONTAGGI.items():
                d = v[m]
                if len(d["E_m"]) != 12 or abs(sum(d["E_m"]) - d["E_y"]) > 0.02 * d["E_y"]:
                    errore(f"PVGIS {k} {m}: 12 mesi non coerenti col totale ({sum(d['E_m']):.1f} vs {d['E_y']})")
                if d["url"] != RP.url_pvgis(c["lat"], c["lon"], ang) or d.get("http") != 200 or len(d.get("sha256", "")) != 64:
                    errore(f"PVGIS {k} {m}: URL, codice HTTP o impronta non coerenti")
                if not (400 < d["E_y"] < 1600):
                    errore(f"PVGIS {k} {m}: {d['E_y']} kWh fuori scala per 800 Wp")
            n += 1
    msg = f"2. PVGIS: {n} città con due montaggi, mesi coerenti con il totale"
    if rete:
        campione = random.sample([(l, c) for l in G.LINGUE_ATTIVE for c in G.CITTA[l]], 5)
        for l, c in campione:
            for m, ang in RP.MONTAGGI.items():
                stato, corpo = RP.leggi(RP.url_pvgis(c["lat"], c["lon"], ang))
                nuovo = RP.estrai(corpo)["E_y"]
                vecchio = G.PVGIS["citta"][f"{l}/{c['slug']}"][m]["E_y"]
                if stato != 200 or abs(nuovo - vecchio) > 0.005 * vecchio:
                    errore(f"PVGIS ricalcolato {l}/{c['slug']} {m}: {nuovo} contro {vecchio} salvati")
        msg += f"; ricalcolate oggi sull'API: {', '.join(c['nome'] for _, c in campione)}"
    print(msg + ".")


# ---------------------------------------------------------------- 3. calcolatore
def controlla_calcolatore():
    js = next((SITO / "assets").glob("app.*.js")).read_text(encoding="utf-8")
    parte = js.split("(function(){")[0]
    casi = []
    rnd = random.Random(7)
    for l in G.LINGUE_ATTIVE:
        for c in G.CITTA[l]:
            for m in ("a35", "a90"):
                for w, q, k in [(800, 60, 500), (rnd.choice([350, 600, 1000, 2000]), rnd.choice([30, 55, 90]), rnd.choice([0, 250, 900]))]:
                    casi.append({"l": G.T[l]["html"], "ey": G.pv(l, c["slug"])[m]["E_y"], "w": w, "q": q, "p": G.prezzo(l), "k": k})
    prog = parte + "\nconst C=" + json.dumps(casi) + ";console.log(JSON.stringify(C.map(function(c){var r=calcola(c.ey,c.w,c.q,c.p,c.k);" \
        "return [fmt(r.prod,0,c.l),fmt(r.eur,0,c.l),r.anni===null?null:fmt(r.anni,1,c.l)];})));"
    r = subprocess.run(["node", "-e", prog], capture_output=True, text=True)
    if r.returncode:
        errore(f"calcolatore: node non esegue il JS: {r.stderr[:300]}")
        return
    uscite = json.loads(r.stdout)
    diversi = 0
    for c, (prod, eur, anni) in zip(casi, uscite):
        l = c["l"][:2]
        py = G.calcola(c["ey"], c["w"], c["q"], c["p"], c["k"])
        attesi = [G.fmt_num(py["prod"], l), G.fmt_num(py["eur"], l), None if py["anni"] is None else G.fmt_num(py["anni"], l, 1)]
        if [prod, eur, anni] != attesi:
            diversi += 1
            if diversi <= 5:
                errore(f"calcolatore JS ≠ Python ({c}): {[prod, eur, anni]} contro {attesi}")
    # numeri stampati nelle pagine
    stampati = 0
    for l in G.LINGUE_ATTIVE:
        for c in G.PAGINE_CITTA[l]:
            f = SITO / G.url_citta(l, c["slug"]) / "index.html"
            t = f.read_text(encoding="utf-8")
            r35 = G.risultato(l, c["slug"])
            attesi = {'class="stat main"><b>': G.fmt_num(G.pv(l, c["slug"])["a35"]["E_y"], l), 'data-o="eur">': G.fmt_num(r35["eur"], l),
                      'data-o="anni">': G.fmt_num(r35["anni"], l, 1), 'data-o="prod">': G.fmt_num(r35["prod"], l)}
            for chiave, val in attesi.items():
                m = re.search(re.escape(chiave) + r'([^<]+)<', t)
                if not m or m.group(1).strip() != val:
                    errore(f"{f.relative_to(SITO)}: {chiave} stampato {m.group(1) if m else '?'} invece di {val}")
                stampati += 1
            if f"{G.fmt_num(r35['eur'], l)} €" not in testo(t):
                errore(f"{f.relative_to(SITO)}: risparmio annuo {G.fmt_num(r35['eur'], l)} € non trovato nel testo")
            dati = json.loads(re.search(r'id="calc-dati">(.*?)</script>', t).group(1))
            for x in dati["citta"]:
                if x["a35"] != G.pv(l, x["s"])["a35"]["E_y"] or x["m90"] != G.pv(l, x["s"])["a90"]["E_m"]:
                    errore(f"{f.relative_to(SITO)}: dati del calcolatore diversi da dati/pvgis.json per {x['s']}")
    print(f"3. Calcolatore: {len(casi)} casi, JS e Python uguali in {len(casi) - diversi}; {stampati} numeri stampati controllati.")


# ---------------------------------------------------------------- 4. FAQ e JSON-LD
def controlla_faq():
    tutte = {}
    for l in G.LINGUE_ATTIVE:
        s = set()
        for v in G.DOMANDA["lingue"][l]["base"].values():
            s |= set(v or [])
        tutte[l] = s
        for q in G.REGOLE["paesi"][l]["faq"]:
            if q["ricerca"] not in s:
                errore(f"{l} FAQ «{q['q']}»: la ricerca «{q['ricerca']}» non è nell'autocompletamento salvato")
        for c in G.PAGINE_CITTA[l]:
            if not c["domanda"]:
                errore(f"{l}/{c['slug']}: pagina città senza domanda vera")
    n = 0
    for f in pagine():
        t = f.read_text(encoding="utf-8")
        for blocco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
            d = json.loads(blocco)
            if d.get("@type") != "FAQPage":
                continue
            visibile = testo(t)
            for q in d["mainEntity"]:
                n += 1
                if re.sub(r"\s+", " ", q["name"]) not in visibile:
                    errore(f"{f.relative_to(SITO)}: domanda JSON-LD non visibile: {q['name']}")
                if re.sub(r"\s+", " ", q["acceptedAnswer"]["text"]) not in re.sub(r"\s*\[\d+\](,\[\d+\])*", "", visibile):
                    errore(f"{f.relative_to(SITO)}: risposta JSON-LD diversa dal testo: {q['name']}")
        if "{" in testo(t).replace("{}", "") and re.search(r"\{(kwh|eur|anni|prezzo|periodo|c|k35|quota)\b", t):
            errore(f"{f.relative_to(SITO)}: segnaposto non sostituito")
    print(f"4. FAQ: {n} domande nei JSON-LD uguali al testo; ogni FAQ viene da una ricerca salvata.")


# ---------------------------------------------------------------- 5. hreflang, link, sitemap, titoli
def controlla_struttura():
    esistenti = {percorso_di(f) for f in pagine()}
    canonici, hl = set(), {}
    for f in pagine():
        t = f.read_text(encoding="utf-8")
        nome = str(f.relative_to(SITO))
        p = percorso_di(f)
        m = re.search(r'<link rel="canonical" href="([^"]+)"', t)
        if m:
            canonici.add(m.group(1))
            if m.group(1) != f"{G.URL_SITO}/{p}":
                errore(f"{nome}: canonical {m.group(1)} diverso dall'indirizzo")
        elif f.name != "404.html":
            errore(f"{nome}: né canonical né 404")
        tit = re.search(r"<title>(.*?)</title>", t)
        if not tit or len(unescape(tit.group(1))) > 70:
            errore(f"{nome}: titolo assente o oltre 70 caratteri ({unescape(tit.group(1)) if tit else ''})")
        des = re.search(r'<meta name="description" content="([^"]*)"', t)
        if m and (not des or not 70 <= len(unescape(des.group(1))) <= 165):
            errore(f"{nome}: descrizione assente o di lunghezza strana ({len(unescape(des.group(1))) if des else 0})")
        alt = dict((a, u) for a, u in re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', t))
        if alt:
            hl[f"{G.URL_SITO}/{p}"] = alt
        for href in re.findall(r'href="([^"]+)"', t):
            if href.startswith(("http", "mailto:", "//")):
                continue
            if href.startswith("#"):
                if f'id="{href[1:]}"' not in t:
                    errore(f"{nome}: ancora {href} inesistente")
                continue
            if not href.startswith("/"):
                errore(f"{nome}: link relativo {href}")
                continue
            path, _, anc = href[1:].partition("#")
            if path.startswith("assets/"):
                if not (SITO / path).exists():
                    errore(f"{nome}: risorsa mancante {href}")
                continue
            if path not in esistenti:
                errore(f"{nome}: link interno rotto {href}")
            elif anc:
                dest = SITO / (path + "index.html" if path.endswith("/") or path == "" else path)
                if f'id="{anc}"' not in dest.read_text(encoding="utf-8"):
                    errore(f"{nome}: ancora #{anc} inesistente in {path}")
    for url, alt in hl.items():
        if url not in alt.values():
            errore(f"{url}: hreflang senza sé stessa")
        for lang, u in alt.items():
            if u not in canonici:
                errore(f"{url}: hreflang {lang} verso una pagina inesistente {u}")
            elif hl.get(u) != alt:
                errore(f"{url}: hreflang non reciproco con {u}")
    sm = set(re.findall(r"<loc>([^<]+)</loc>", (SITO / "sitemap.xml").read_text(encoding="utf-8")))
    if sm != canonici:
        errore(f"sitemap ≠ pagine con canonical: in più {sorted(sm - canonici)[:5]}, mancano {sorted(canonici - sm)[:5]}")
    if (SITO / "de").exists():
        errore("/de/ pubblicata: la versione tedesca resta spenta finché manca l'Impressum")
    for nome in ("robots.txt", "netlify.toml", "404.html", f"{G.CHIAVE_INDEXNOW}.txt", "assets/og.png"):
        if not (SITO / nome).exists():
            errore(f"manca {nome}")
    print(f"5. Struttura: {len(esistenti)} pagine, {len(canonici)} con canonical = sitemap; hreflang reciproci su {len(hl)} pagine; link e ancore validi.")


# ---------------------------------------------------------------- 6. monetizzazione
def controlla_monetizzazione():
    err, info = MON.controlla_sito(G.SITO_ID, SITO)
    for e in err:
        errore("monetizzazione: " + e)
    accesi = {l: G.ci_sono_affiliati(l) for l in G.LINGUE_ATTIVE}
    if not any(accesi.values()) and info["link_affiliati"]:
        errore(f"affiliati spenti ma {info['link_affiliati']} link di affiliazione nel sito")
    for l, v in G.AFFILIATI.items():
        if l.startswith("_"):
            continue
        for voce in v:
            u = (voce.get("url") or "").strip()
            if u and not u.startswith("https://"):
                errore(f"affiliati.json {l}/{voce['id']}: url non valido")
    print(MON.riepilogo(G.SITO_ID, info, err) + f"; riquadri affiliati accesi: {[l for l, a in accesi.items() if a] or 'nessuno'}.")


# ---------------------------------------------------------------- 7. parole vietate
def controlla_parole():
    vietate = re.compile(r"Massimiliano|\bCori\b|@[a-z0-9-]+\.(it|com|fr|es)\b|\+39|Cl[a]ude|Anthr[o]pic|\bOp[u]s\b|\bSonn[e]t\b|\bG[P]T\b|Chat[G]PT", re.I)  # lettere tra [] per non scrivere i nomi
    for f in list(pagine()) + [RADICE / "genera.py", RADICE / "verifica.py"]:
        t = f.read_text(encoding="utf-8")
        if f.suffix == ".py":
            t = re.sub(r"vietate = re\.compile\(.*", "", t)
            t = re.sub(r"Massimiliano conferma[^\n]*|Massimiliano[^\n]*Impressum[^\n]*", "", t)
        for m in vietate.finditer(t):
            errore(f"{f.name}: parola vietata «{m.group(0)}»")
    print("7. Nessun dato personale, nessun nome di modello AI nelle pagine.")


def browser():
    r = subprocess.run(["node", str(RADICE / "verifica_browser.js")], capture_output=True, text=True, timeout=900)
    print(r.stdout.strip())
    if r.returncode:
        errore("browser: " + (r.stderr.strip() or r.stdout.strip())[-1500:])


def main():
    rete = "--rete" in sys.argv
    controlla_fonti(rete)
    controlla_pvgis(rete)
    controlla_calcolatore()
    controlla_faq()
    controlla_struttura()
    controlla_monetizzazione()
    controlla_parole()
    if "--browser" in sys.argv:
        browser()
    if ERRORI:
        print(f"\n{len(ERRORI)} ERRORI:")
        for e in ERRORI[:80]:
            print(" -", e)
        sys.exit(1)
    print("\nTutti i controlli superati.")


if __name__ == "__main__":
    main()
