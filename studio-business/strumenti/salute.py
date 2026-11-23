#!/usr/bin/env python3
"""Controllo quotidiano di salute della rete (regola del 19/11/2026: nessun sito senza controlli).

Per ogni sito online (elenco in indexnow.py):
  1. home, robots.txt, sitemap e 5 pagine a caso della sitemap: HTTP 200, niente noindex, canonical sul proprio host, GoatCounter presente;
  2. domini propri: vecchio indirizzo .netlify.app -> 301 pagina per pagina sul dominio nuovo;
  3. la sitemap online e' uguale a quella del commit (pubblicazione non rimasta indietro);
  4. date scadute nel <title> della home ("prossima data 18 novembre", "next ... November 18"): data gia' passata = errore;
  5. freschezza dei dati: ogni campo verificato_il / controllato_il / letto_il nei file dati/*.json piu' vecchio della soglia
     (7 giorni per i calendari d'esame di EsameB1, 45 giorni per il resto) = avviso.
Uscita: righe "ERRORE" / "AVVISO" e un riepilogo; codice 1 se ci sono errori.
Uso: python3 studio-business/strumenti/salute.py [--solo <cartella>]
"""
import datetime as dt, json, pathlib, random, re, subprocess, sys, urllib.request

RADICE = pathlib.Path(__file__).resolve().parents[2]
OGGI = dt.date.today()
MESI_IT = ["gennaio","febbraio","marzo","aprile","maggio","giugno","luglio","agosto","settembre","ottobre","novembre","dicembre"]
MESI_EN = ["january","february","march","april","may","june","july","august","september","october","november","december"]
VECCHI = {"visaincomechecker.com": "visa-income-checker.netlify.app", "before-you-fly.com": "before-you-fly.netlify.app",
          "esameb1.eu": "esameb1.netlify.app", "payrolltaxbystate.com": "payroll-tax-by-state.netlify.app", "pagaccnl.com": "paga-ccnl.netlify.app"}
SOGLIE = {("esameb1", "sessioni.json"): 7}
SOGLIA_STD = 45

class _NoRed(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
_op = urllib.request.build_opener(_NoRed)

def get(u, segui=True):
    # 23/11/2026: un errore di rete passeggero (HTTP 0) non è un errore del sito: si riprova fino a 2 volte
    for _ in range(2):
        r = _get(u, segui)
        if r[0] != 0:
            return r
        __import__("time").sleep(3)
    return _get(u, segui)

def _get(u, segui=True):
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (compatible; controllo-rete)"})
    try:
        r = (urllib.request.urlopen if segui else _op.open)(req, timeout=25)
        return r.status, r.read().decode("utf-8", "replace"), None
    except urllib.error.HTTPError as e:
        return e.code, "", e.headers.get("Location")
    except Exception as e:  # rete
        return 0, str(e)[:80], None

def siti():
    src = (RADICE / "studio-business/strumenti/indexnow.py").read_text()
    coppie = re.findall(r'\("([a-z0-9.\-]+)",\s*"([a-z0-9_]+)"\)', src)
    m = re.search(r"NON_ONLINE\s*=\s*(\{[^}]*\}|set\(\))", src)
    fuori = set(re.findall(r'"([^"]+)"', m.group(1))) if m else set()
    return [(h, c) for h, c in coppie if h not in fuori]

def date_titolo(t):
    t = t.lower(); out = []
    for g, m in re.findall(r"\b(\d{1,2}) (" + "|".join(MESI_IT + MESI_EN) + r")\b", t):
        out.append((int(g), (MESI_IT + MESI_EN).index(m) % 12 + 1))
    for m, g in re.findall(r"\b(" + "|".join(MESI_EN) + r") (\d{1,2})\b", t):
        out.append((int(g), MESI_EN.index(m) + 1))
    return out

def scaduta(g, m):
    # una data senza anno nel titolo: passata se cade nei 120 giorni prima di oggi
    for anno in (OGGI.year, OGGI.year - 1):
        try: d = dt.date(anno, m, g)
        except ValueError: return False
        if 0 < (OGGI - d).days <= 120: return True
    return False

def date_lettura(testo):
    """Date di lettura dei dati; un elemento con "data" gia' passata (es. sessione d'esame svolta) non conta:
    l'ente lo toglie dal calendario e non si puo' piu' rileggere."""
    out = []
    def giro(x):
        if isinstance(x, dict):
            d = x.get("data")
            passato = isinstance(d, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) and d < OGGI.isoformat()
            for k in ("verificato_il", "controllato_il", "letto_il"):
                v = x.get(k)
                if not passato and isinstance(v, str) and re.match(r"\d{4}-\d{2}-\d{2}", v):
                    out.append(v[:10])
            for v in x.values(): giro(v)
        elif isinstance(x, list):
            for v in x: giro(v)
    try:
        giro(json.loads(testo))
    except Exception:
        out = re.findall(r'"(?:verificato_il|controllato_il|letto_il)"\s*:\s*"(\d{4}-\d{2}-\d{2})', testo)
    return out

def freschezza(cartella):
    avvisi = []
    for f in sorted((RADICE / cartella / "dati").glob("*.json")) if (RADICE / cartella / "dati").exists() else []:
        try: testo = f.read_text(encoding="utf-8")
        except Exception: continue
        date = date_lettura(testo)
        if not date: continue
        piu_recente = max(date); piu_vecchia = min(date)
        soglia = SOGLIE.get((cartella, f.name), SOGLIA_STD)
        eta = (OGGI - dt.date.fromisoformat(piu_vecchia)).days
        if eta > soglia:
            avvisi.append(f"{cartella}/dati/{f.name}: dato piu' vecchio letto il {piu_vecchia} ({eta} giorni, soglia {soglia}; piu' recente {piu_recente})")
    return avvisi

def main():
    solo = sys.argv[sys.argv.index("--solo") + 1] if "--solo" in sys.argv else None
    errori, avvisi = [], []
    random.seed(OGGI.toordinal())
    for host, cart in siti():
        if solo and solo not in (host, cart): continue
        e = []
        s, home, _ = get(f"https://{host}/")
        if s != 200: e.append(f"home HTTP {s}")
        else:
            t = re.search(r"<title>([^<]*)", home)
            for g, m in date_titolo(t.group(1) if t else ""):
                if scaduta(g, m): e.append(f"titolo della home con data passata: «{t.group(1)}»")
            if "goatcounter" not in home: e.append("home senza GoatCounter")
            if re.search(r'name="robots"[^>]*noindex', home): e.append("home noindex")
        s, rob, _ = get(f"https://{host}/robots.txt")
        if re.search(r"(?im)^disallow:\s*/\s*$", rob): e.append("robots.txt blocca tutto")
        s, sm, _ = get(f"https://{host}/sitemap.xml")
        locs = re.findall(r"<loc>([^<]+)", sm)
        if s != 200 or not locs: e.append(f"sitemap HTTP {s}, {len(locs)} URL")
        loc_git = subprocess.run(["git", "-C", str(RADICE), "show", f"HEAD:{cart}/sito/sitemap.xml"], capture_output=True, text=True).stdout
        if loc_git and sm and loc_git != sm: avvisi.append(f"{host}: sitemap online diversa da quella del commit (pubblicazione in corso o rimasta indietro)")
        for u in random.sample(locs, min(5, len(locs))):
            s, h, _ = get(u)
            if s != 200: e.append(f"{u}: HTTP {s}")
            elif re.search(r'name="robots"[^>]*noindex', h): e.append(f"{u}: noindex ma in sitemap")
            elif "goatcounter" not in h: e.append(f"{u}: senza GoatCounter")
            else:
                c = re.search(r'rel="canonical" href="([^"]+)"', h)
                if c and c.group(1) != u: e.append(f"{u}: canonical {c.group(1)}")
        if host in VECCHI and locs:
            for u in random.sample(locs, min(3, len(locs))):
                p = u.split(host, 1)[1]
                s, _, loc = get(f"https://{VECCHI[host]}{p}", segui=False)
                if s != 301 or loc != f"https://{host}{p}": e.append(f"vecchio indirizzo {VECCHI[host]}{p}: {s} -> {loc}")
        avvisi += freschezza(cart)
        errori += [f"{host}: {x}" for x in e]
        print(f"{host:42} {len(locs):5} URL  {'OK' if not e else 'ERRORI: ' + ' | '.join(e)}", flush=True)
    for a in avvisi: print("AVVISO", a)
    for x in errori: print("ERRORE", x)
    print(f"Riepilogo {OGGI}: {len(errori)} errori, {len(avvisi)} avvisi")
    sys.exit(1 if errori else 0)

if __name__ == "__main__":
    main()
