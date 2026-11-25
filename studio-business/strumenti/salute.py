#!/usr/bin/env python3
"""Controllo quotidiano di salute della rete (regola del 19/11/2026: nessun sito senza controlli).

Per ogni sito online (elenco in indexnow.py):
  1. home, robots.txt, sitemap e 5 pagine a caso della sitemap: HTTP 200, niente noindex, canonical sul proprio host, GoatCounter presente;
  2. domini propri: vecchio indirizzo .netlify.app -> 301 pagina per pagina sul dominio nuovo;
  3. la sitemap online e' uguale a quella del commit (pubblicazione non rimasta indietro);
  4. date scadute nel <title> della home ("prossima data 18 novembre", "next ... November 18"): data gia' passata = errore;
  5. freschezza dei dati: ogni campo verificato_il / controllato_il / letto_il nei file dati/*.json piu' vecchio della soglia
     (7 giorni per i calendari d'esame di EsameB1, 45 giorni per il resto) = avviso.
Controlli aggiunti il 25/11/2026 (AUDIT-25-11.md). Leggono il repository (<cartella>/sito, <cartella>/dati, git):
nessuna richiesta in rete in piu' (il n. 7 usa la home gia' scaricata). Sono tutti AVVISI, tranne il n. 9 sui titoli:
  6. piu' campi di lettura: scaricato_il, ultima_verifica, siti_verificati_il, provato_il, generato_il;
  7. promessa contro data vera: la home dice "updated weekly", "ogni giorno"... e la data scritta accanto
     ("checked on", "as of", "letti il") e' piu' vecchia della promessa (senza promessa: 45 giorni);
  8. fonte primaria caduta con la riserva in uso: campo fonte_non_raggiungibile_dal da piu' di 3 giorni;
  9. date passate in titolo e descrizione di tutte le pagine indicizzabili ("next", "prossima", "until", "entro", "fino al" + data):
     titolo con "next"/"prossima" e data passata = ERRORE (data passata presentata come futura), il resto = avviso;
 10. dati riletti ma sito non rigenerato: commit in dati/ piu' recente dell'ultimo commit di sito/ da oltre 3 giorni
     (non contano le righe che cambiano solo una data di lettura o un'impronta);
 11. date dei dati (campi dal, scadenza, prossima...) scattate dopo l'ultima generazione del sito;
 12. routine saltata: giro previsto in calendario-routine.json contro l'ultima lettura o l'ultimo commit dei dati;
 13. home con piu' di 5 link a pagine noindex;
 14. frasi a tempo ("not yet published on", "non ancora uscite", "comments until") con una data di oltre 14 giorni;
 15. campi di errore nei dati (http, stato, errore = 0 o >= 400) aumentati rispetto a 7 giorni fa;
 16. dal 2 gennaio a fine febbraio: titoli indicizzabili con l'anno vecchio e senza l'anno nuovo.
Non fatto: visite su pagine noindex (serve GoatCounter, e' un controllo settimanale).
Uscita: righe "ERRORE" / "AVVISO" e un riepilogo; codice 1 se ci sono errori.
Uso: python3 studio-business/strumenti/salute.py [--solo <cartella>]
"""
import datetime as dt, html as _html, json, pathlib, random, re, subprocess, sys, urllib.request

RADICE = pathlib.Path(__file__).resolve().parents[2]
OGGI = dt.date.today()
MESI_IT = ["gennaio","febbraio","marzo","aprile","maggio","giugno","luglio","agosto","settembre","ottobre","novembre","dicembre"]
MESI_EN = ["january","february","march","april","may","june","july","august","september","october","november","december"]
VECCHI = {"visaincomechecker.com": "visa-income-checker.netlify.app", "before-you-fly.com": "before-you-fly.netlify.app",
          "esameb1.eu": "esameb1.netlify.app", "payrolltaxbystate.com": "payroll-tax-by-state.netlify.app", "pagaccnl.com": "paga-ccnl.netlify.app"}
SOGLIE = {("esameb1", "sessioni.json"): 7}
SOGLIA_STD = 45
CAMPI = ("verificato_il", "controllato_il", "letto_il", "scaricato_il", "ultima_verifica", "siti_verificati_il", "provato_il", "generato_il")
CALENDARIO = pathlib.Path(__file__).with_name("calendario-routine.json")

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
            for k in CAMPI:
                v = x.get(k)
                if not passato and isinstance(v, str) and re.match(r"\d{4}-\d{2}-\d{2}", v):
                    out.append(v[:10])
            for v in x.values(): giro(v)
        elif isinstance(x, list):
            for v in x: giro(v)
    try:
        giro(json.loads(testo))
    except Exception:
        out = re.findall(r'"(?:' + "|".join(CAMPI) + r')"\s*:\s*"(\d{4}-\d{2}-\d{2})', testo)
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

# ---------------------------------------------------------------------------------------------------------------
# Controlli del 25/11/2026 (AUDIT-25-11.md): lavorano sui file del repository, senza richieste in rete.

_M3 = {"jan": 1, "gen": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "mag": 5, "jun": 6, "giu": 6, "jul": 7, "lug": 7, "aug": 8, "ago": 8,
       "sep": 9, "set": 9, "oct": 10, "ott": 10, "nov": 11, "dec": 12, "dic": 12}
_MESE = r"(?:" + "|".join(MESI_IT + MESI_EN) + r"|jan|gen|feb|mar|apr|mag|jun|giu|jul|lug|aug|ago|sept?|set|oct|ott|nov|dec|dic)\b\.?"
_DATA = (r"(?:\b(?P<g1>\d{1,2})(?:st|nd|rd|th|º|°)?\s+(?P<m1>" + _MESE + r")(?:,?\s+(?P<a1>20\d\d)\b)?"
         r"|\b(?P<m2>" + _MESE + r")\s+(?P<g2>\d{1,2})(?:st|nd|rd|th)?(?!\d)(?:,?\s+(?P<a2>20\d\d)\b)?)")
_DATA_RE = re.compile(_DATA, re.I)
# Solo parole che presentano la data come futura. "deadline 10 September" o "deadline was May 1" sono fatti, non promesse: fuori.
_FUTURO = r"\b(?P<parola>next|prossim[aoie]|entro|until|fino\s+al(?:l['’])?)\b"
_FUTURO_RE = re.compile(_FUTURO + r"(?:(?!\b(?:was|were|closed|ended|expired|era|erano|chius[oaie]|scadut[oaie])\b)[^.;!?|<>]){0,40}?" + _DATA, re.I)
_FRASI_RE = re.compile(r"(?:not yet (?:been )?published|non (?:era|erano|è|sono) ancora (?:stat[oaie] )?(?:pubblicat|uscit)\w+|comments until)[^<>]{0,90}?" + _DATA, re.I)
# (giorni massimi, espressione): fra piu' promesse nella stessa home vale la piu' larga. Manca apposta "ogni giorno / updated daily":
# chi lo promette aggiorna i dati nel browser (aste, Italy Strikes) e la data scritta nell'HTML e' solo quella dell'ultima generazione.
_PROMESSE = [
    (10, r"\bupdated (?:weekly|every week)\b|\baggiornat[oaie] ogni settimana\b|\ble pagine ogni settimana\b|\bevery week we\b"
         r"|\bcontrolliamo[^.]{0,40}\bogni settimana\b|\bwe (?:check|re-download)[^.]{0,40}\bevery week\b"),
    (24, r"\b(?:updated )?twice a month\b|\bdue volte al mese\b"),
    (40, r"\bupdated (?:monthly|every month)\b|\baggiornat[oaie] ogni mese\b"),
]
_LETTO_RE = re.compile(r"(?:\b(?:last )?checked(?: on)?|\blast download(?:ed)?|\bdownloaded(?: on)?|\bretrieved(?: on)?|\bas of|\bcontrollat[oaie] il"
                       r"|\bverificat[oaie] il|\blett[oaie] il|\bscaricat[oaie] il)\W{0,3}" + _DATA, re.I)

def _data(m):
    """Da una corrispondenza di _DATA: (giorno, mese, anno o None)."""
    g = int(m.group("g1") or m.group("g2")); mese = _M3.get((m.group("m1") or m.group("m2")).lower()[:3])
    a = m.group("a1") or m.group("a2")
    return g, mese, int(a) if a else None

def _passata(g, mese, anno):
    """Con l'anno: prima di oggi. Senza anno: come scaduta() (nei 120 giorni prima di oggi)."""
    if not mese: return None
    if anno is None: return scaduta(g, mese) or None
    try: d = dt.date(anno, mese, g)
    except ValueError: return None
    return d if d < OGGI else None

def _testo(pagina):
    t = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", pagina)
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", t)))

def _git(*a):
    return subprocess.run(["git", "-C", str(RADICE), *a], capture_output=True, text=True).stdout

def _calendario():
    try: return json.loads(CALENDARIO.read_text(encoding="utf-8"))
    except Exception: return {}

def promessa_home(home):
    """Controllo 7. La data di lettura piu' recente scritta nella home contro la frequenza promessa nella stessa home."""
    t = _testo(home)
    date = []
    for m in _LETTO_RE.finditer(t):
        g, mese, anno = _data(m)
        try: date.append(dt.date(anno, mese, g))
        except (TypeError, ValueError): pass
    date = [d for d in date if d <= OGGI]
    if not date: return []
    promesse = [(gg, re.search(e, t, re.I).group(0)) for gg, e in _PROMESSE if re.search(e, t, re.I)]
    soglia, frase = max(promesse) if promesse else (SOGLIA_STD, None)
    eta = (OGGI - max(date)).days
    if eta <= soglia: return []
    return [f"la home dice «{frase}» ma la data piu' recente che mostra e' il {max(date)} ({eta} giorni, soglia {soglia})" if frase
            else f"la data piu' recente scritta nella home e' il {max(date)} ({eta} giorni, soglia {soglia})"]

def fonti_cadute(cartella):
    """Controllo 8. fonte_non_raggiungibile_dal da piu' di 3 giorni: la fonte primaria e' giu' e il sito vive della riserva."""
    out, viste = [], set()
    for f in sorted((RADICE / cartella / "dati").glob("*.json")):
        try: testo = f.read_text(encoding="utf-8")
        except Exception: continue
        if "fonte_non_raggiungibile_dal" not in testo: continue
        def giro(x):
            if isinstance(x, dict):
                v = x.get("fonte_non_raggiungibile_dal")
                if isinstance(v, str) and re.match(r"\d{4}-\d{2}-\d{2}", v):
                    gg = (OGGI - dt.date.fromisoformat(v[:10])).days
                    if gg > 3 and v[:10] not in viste:  # la stessa caduta copiata in piu' file (registro.json, vista.json): una riga sola
                        viste.add(v[:10])
                        riserva = next((k for k, r in x.items() if k.startswith("riserva") and isinstance(r, dict) and r.get("usata_il")), None)
                        out.append(f"{cartella}/dati/{f.name}: fonte primaria non raggiungibile dal {v[:10]} ({gg} giorni)"
                                   + (f", in uso la riserva {riserva[8:] or riserva}" if riserva else "")
                                   + (f"; ultimo errore: {str(x['ultimo_errore'])[:90]}" if x.get("ultimo_errore") else ""))
                for v in x.values(): giro(v)
            elif isinstance(x, list):
                for v in x: giro(v)
        try: giro(json.loads(testo))
        except Exception: pass
    return out

def pagine_locali(cartella):
    """Controlli 9, 13, 14 e 16: una sola lettura dei file .html di <cartella>/sito."""
    errori, avvisi = [], []
    sito = RADICE / cartella / "sito"
    if not sito.exists(): return errori, avvisi
    noindex = set(); tit_futuro, tit_altro, descr, frasi, anno_vecchio = [], [], [], [], []
    cambio_anno = dt.date(OGGI.year, 1, 2) <= OGGI <= dt.date(OGGI.year, 2, 28)
    for f in sorted(sito.rglob("*.html")):
        try: p = f.read_text(encoding="utf-8", errors="replace")
        except Exception: continue
        rel = "/" + str(f.relative_to(sito))
        if re.search(r'name="robots"[^>]*noindex', p[:6000]) or re.search(r'http-equiv="refresh"', p[:6000], re.I):
            noindex.add(f); continue
        t = re.search(r"<title>([^<]*)", p); t = _html.unescape(t.group(1)) if t else ""
        d = re.search(r'<meta name="description" content="([^"]*)"', p); d = _html.unescape(d.group(1)) if d else ""
        for m in _FUTURO_RE.finditer(t):
            if _passata(*_data(m)):
                (tit_futuro if re.match(r"next|prossim", m.group("parola"), re.I) else tit_altro).append(f"{rel} «{t}»"); break
        for m in _FUTURO_RE.finditer(d):
            if _passata(*_data(m)):
                descr.append(f"{rel} «…{m.group(0)}…»"); break
        for m in _FRASI_RE.finditer(p):
            g, mese, anno = _data(m)
            try: quando = dt.date(anno, mese, g)
            except (TypeError, ValueError): continue
            if 14 < (OGGI - quando).days:
                frasi.append(f"{rel} «{_testo(m.group(0))}»"); break
        if cambio_anno:
            # una data intera ("Nov 16, 2026", "December 2026", "24/11/2026") e' un fatto, non l'anno della pagina
            senza_date = re.sub(rf"(?i){_MESE}\s+(?:\d{{1,2}},?\s+)?20\d\d|\b\d{{1,2}}/\d{{1,2}}/20\d\d", " ", t)
            if re.search(rf"\b{OGGI.year - 1}\b", senza_date) and not re.search(rf"\b{OGGI.year}\b|\b{OGGI.year - 1}[-–/]{OGGI.year % 100}\b", t):
                anno_vecchio.append(f"{rel} «{t}»")
    def riga(elenco, cosa):
        return f"{cartella}/sito: {len(elenco)} pagine {cosa}, es. {elenco[0]}"
    if tit_futuro: errori.append(riga(tit_futuro, "con una data passata nel titolo presentata come prossima"))
    if tit_altro: avvisi.append(riga(tit_altro, "con una scadenza passata nel titolo"))
    if descr: avvisi.append(riga(descr, "con una data passata nella descrizione per Google"))
    if frasi: avvisi.append(riga(frasi, "con una frase a tempo vecchia di oltre 14 giorni (rileggere la fonte)"))
    if anno_vecchio: avvisi.append(riga(anno_vecchio, f"con {OGGI.year - 1} nel titolo e senza {OGGI.year}"))
    # 13. link della home verso pagine noindex
    home = sito / "index.html"
    if home.exists() and noindex:
        verso = set()
        for h in set(re.findall(r'<a\b[^>]*\bhref="(/[^"#?]*)', home.read_text(encoding="utf-8", errors="replace"))):
            base = sito / h.lstrip("/")
            for c in ((base / "index.html") if h.endswith("/") or base.is_dir() else base, base.with_name(base.name + ".html")):
                if c in noindex: verso.add(h); break
        if len(verso) > 5:
            avvisi.append(f"{cartella}/sito: la home ha {len(verso)} link a pagine noindex, es. {sorted(verso)[0]}")
    return errori, avvisi

_SOLO_LETTURA = re.compile(r'"\w*(?:_il|_al|impront|sha|hash|etag|md5)\w*"\s*:')

def dati_e_sito(cartella, cal):
    """Controlli 10 e 11: dati piu' nuovi del sito da oltre 3 giorni; date dei dati scattate dopo l'ultima generazione."""
    out = []
    r = _git("log", "-1", "--format=%H %ct", "--", f"{cartella}/sito").split()
    if len(r) != 2: return out
    commit, quando = r[0], dt.date.fromtimestamp(int(r[1]))
    vivi = set(cal.get("dati_dal_vivo", {}).get(cartella, []))
    def conta(n): return not (n in vivi or re.search(r"domanda|volumi|impronte", n))
    # 10
    dopo = [x.split() for x in _git("log", "--format=%ct %cs", f"{commit}..HEAD", "--", f"{cartella}/dati").splitlines() if x.strip()]
    if dopo and (dt.datetime.now().timestamp() - int(dopo[-1][0])) / 86400 > 3:
        cambiati, f = {}, None
        for x in _git("diff", "-U0", commit, "HEAD", "--", f"{cartella}/dati/*.json").splitlines():
            if x.startswith(("+++ ", "--- ")):
                if x.startswith("+++ b/"): f = x.rsplit("/", 1)[1]
            elif x[:1] in "+-" and f and conta(f) and x[1:].strip() and not _SOLO_LETTURA.match(x[1:].strip()):
                cambiati[f] = cambiati.get(f, 0) + 1
        if cambiati:
            out.append(f"{cartella}: dati cambiati dal {dopo[-1][1]} ma sito non rigenerato (ultimo commit di sito/ il {quando}): "
                       + ", ".join(sorted(cambiati)[:4]))
    # 11
    for f in sorted((RADICE / cartella / "dati").glob("*.json")):
        if not conta(f.name) or f.stat().st_size > 40_000_000: continue
        try: d = json.loads(f.read_text(encoding="utf-8"))
        except Exception: continue
        scattate = {}
        def giro(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    if isinstance(v, str) and re.fullmatch(r"dal|scadenza|in_vigore_dal|decorrenza|prossim\w*", k) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", v) \
                       and quando.isoformat() < v < OGGI.isoformat():
                        scattate.setdefault(k, []).append(v)
                    giro(v)
            elif isinstance(x, list):
                for v in x: giro(v)
        giro(d)
        for k, v in sorted(scattate.items()):
            out.append(f"{cartella}/dati/{f.name}: {len(v)} date «{k}» scattate fra il {min(v)} e il {max(v)}, dopo l'ultima generazione del sito ({quando}): rigenerare")
    return out

_GIORNI = ["lun", "mar", "mer", "gio", "ven", "sab", "dom"]

def _giro_previsto(r, fino_a):
    """L'ultimo giorno previsto dalla regola r, non dopo fino_a (cerca indietro per 70 giorni)."""
    for i in range(70):
        d = fino_a - dt.timedelta(days=i)
        if r.get("mesi") and d.month not in r["mesi"]: continue
        if r.get("giorni") and _GIORNI[d.weekday()] not in r["giorni"]: continue
        if r.get("settimane_del_mese") and (d.day - 1) // 7 + 1 not in r["settimane_del_mese"]: continue
        if r.get("ultima_del_mese") and (d + dt.timedelta(days=7)).month == d.month: continue
        return d
    return None

def routine_saltate(cartella, cal):
    """Controllo 12: giro previsto (calendario-routine.json) contro l'ultima traccia lasciata dalla routine."""
    out = []
    for r in cal.get("routine", []):
        if r.get("cartella") != cartella: continue
        previsto = _giro_previsto(r, OGGI - dt.timedelta(days=int(r.get("tolleranza", 2))))
        if not previsto: continue
        tracce = []
        for p in r.get("percorsi", []):
            f = RADICE / cartella / p
            if not f.exists(): continue
            c = _git("log", "-1", "--format=%cs", "--", f"{cartella}/{p}").strip()
            if c: tracce.append(c)
            if f.is_file() and f.suffix == ".json":
                try: tracce += re.findall(r'"(?:' + "|".join(CAMPI) + r'|estratto_il)"\s*:\s*"(\d{4}-\d{2}-\d{2})', f.read_text(encoding="utf-8"))
                except Exception: pass
        tracce = [x for x in tracce if x <= OGGI.isoformat()]
        if tracce and max(tracce) < previsto.isoformat():
            out.append(f"routine saltata: {r.get('nome', cartella)}; giro previsto il {previsto}, ultima traccia il {max(tracce)} ({cartella}/{r['percorsi'][0]})")
    return out

def _conta_errori(d):
    n = 0
    if isinstance(d, dict):
        for k, v in d.items():
            if k in ("http", "stato", "status", "errore") and isinstance(v, int) and not isinstance(v, bool) and (v == 0 or v >= 400): n += 1
            n += _conta_errori(v)
    elif isinstance(d, list):
        for v in d: n += _conta_errori(v)
    return n

def errori_nei_dati(cartella, prima):
    """Controllo 15: i campi http/stato/errore con 0 o >= 400 sono piu' di 7 giorni fa (commit `prima`)? Una fonte e' caduta."""
    out = []
    for f in sorted((RADICE / cartella / "dati").glob("*.json")) if prima else []:
        if re.search(r"domanda|volumi", f.name) or f.stat().st_size > 40_000_000: continue
        try: testo = f.read_text(encoding="utf-8")
        except Exception: continue
        if not re.search(r'"(?:http|stato|status|errore)"\s*:\s*(?:0|[4-9]\d\d)\b', testo): continue
        try:
            ora = _conta_errori(json.loads(testo)); allora = _conta_errori(json.loads(_git("show", f"{prima}:{cartella}/dati/{f.name}")))
        except Exception: continue  # file nuovo o non leggibile: nessun confronto
        if ora > allora:
            out.append(f"{cartella}/dati/{f.name}: fonti in errore (http/stato 0 o >= 400) salite da {allora} a {ora} in 7 giorni")
    return out

def controlli_locali(cartella, cal, prima):
    errori, avvisi = pagine_locali(cartella)
    if (RADICE / cartella / "dati").exists():
        avvisi += fonti_cadute(cartella) + dati_e_sito(cartella, cal) + errori_nei_dati(cartella, prima)
    avvisi += routine_saltate(cartella, cal)
    return errori, avvisi


def main():
    solo = sys.argv[sys.argv.index("--solo") + 1] if "--solo" in sys.argv else None
    errori, avvisi = [], []
    random.seed(OGGI.toordinal())
    cal = _calendario()
    prima = _git("rev-list", "-1", "--before=7 days ago", "HEAD").strip()
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
            avvisi += [f"{host}: {x}" for x in promessa_home(home)]
        s, rob, _ = get(f"https://{host}/robots.txt")
        if re.search(r"(?im)^disallow:\s*/\s*$", rob): e.append("robots.txt blocca tutto")
        s, sm, _ = get(f"https://{host}/sitemap.xml")
        locs = re.findall(r"<loc>([^<]+)", sm)
        if "<sitemapindex" in sm:  # indice (dal 25/11/2026 su alcuni siti): le pagine stanno nelle sitemap elencate
            figli, locs = locs, []
            for fu in figli:
                fs, ft, _ = get(fu)
                if fs != 200 or "<urlset" not in ft: e.append(f"{fu}: HTTP {fs} o non è una sitemap")
                else: locs += re.findall(r"<loc>([^<]+)", ft)
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
        el, al = controlli_locali(cart, cal, prima)
        avvisi += al
        e += el
        errori += [f"{host}: {x}" for x in e]
        print(f"{host:42} {len(locs):5} URL  {'OK' if not e else 'ERRORI: ' + ' | '.join(e)}", flush=True)
    for a in avvisi: print("AVVISO", a)
    for x in errori: print("ERRORE", x)
    print(f"Riepilogo {OGGI}: {len(errori)} errori, {len(avvisi)} avvisi")
    sys.exit(1 if errori else 0)

if __name__ == "__main__":
    main()
