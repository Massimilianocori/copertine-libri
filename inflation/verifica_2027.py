"""Controlli delle due sezioni «cifre 2027»: /uk/…-2027/ (dati/uk_2027.json) e /rent-increase-cap/ (dati/affitti.json).

Chiamato da verifica.py (controlla(err, ok, G, SITO)). Non usa raccolta/regole2027.py né le funzioni di lettura dei due moduli:
le tabelle DWP e la tabella dei tetti locali californiani sono rilette dagli originali salvati, gli indici dai CSV e dal PDF del DIR,
e ogni cifra stampata (attributi data-uk, data-rent, data-ca, data-wa, data-on) è rifatta da qui.
"""
import csv
import hashlib
import html
import json
import random
import re
import subprocess
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent
GZ = RADICE / "dati" / "grezzi" / "regole2027"
PAGINE_UK = ["uk/rates-april-2027/", "uk/minimum-wage-2027/", "uk/state-pension-2027/", "uk/benefit-rates-2027/", "uk/statutory-sick-pay-2027/"]
CONSIGLI = re.compile(r"\b(you should|should you|we recommend|you must|you are entitled|you can refuse|illegal increase|sue your|best (landlord|lawyer|benefit)|"
                      r"claim now|apply now)\b", re.I)


def _norm(t):
    t = t.replace("­", "").replace("‑", "-").replace("‐", "-").replace(" ", " ").replace(" ", " ")
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("–", "-"), ("—", "-")):
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).strip()


def _cl(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def _frasi(x, out):
    if isinstance(x, dict):
        if isinstance(x.get("fonte"), str) and isinstance(x.get("frase"), str):
            out.append((x["fonte"], x["frase"]))
        for v in x.values():
            _frasi(v, out)
    elif isinstance(x, list):
        for v in x:
            _frasi(v, out)


def _pulita(f):
    return re.sub(r"\s+([.,:;])", r"\1", f)


def _gbp(p):
    return f"£{p // 100:,}.{p % 100:02d}"


def _usd(c):
    return f"${c // 100:,}.{c % 100:02d}"


def _pc(t):
    return f"{t / 1000:.3f}".rstrip("0").rstrip(".") + "%"


def _pct10(prima, dopo):
    """Variazione % a una cifra decimale (in decimi), con le frazioni: rifatta senza usare uk2027.variazione."""
    from fractions import Fraction
    x = Fraction((dopo - prima) * 1000, prima)
    r = int(abs(x) + Fraction(1, 2))
    return r if x >= 0 else -r


def _pctx(d):
    return "no change" if d == 0 else f"{'+' if d > 0 else '−'}{abs(d) // 10}.{abs(d) % 10}%"


def _diff(prima, dopo):
    d = dopo - prima
    return "no change" if d == 0 else ("+" if d > 0 else "−") + (_gbp(abs(d)) if abs(d) >= 100 else f"{abs(d)}p")


def _pagina(SITO, rel):
    return (SITO / rel / "index.html").read_text(encoding="utf-8")


def _celle(t, attr):
    return [(m.group(1), _cl(m.group(2))) for m in re.finditer(rf'<(?:td|span|strong|b)\b[^>]*\bdata-{attr}="([^"]+)"[^>]*>(.*?)</(?:td|span|strong|b)>', t, re.S)]


def _citazioni(t):
    return [html.unescape(m) for m in re.findall(r'<blockquote class="citaz">(?:<span class="small">.*?</span><br>)?“(.*?)”<cite>', t, re.S)]


def _volumi():
    dom = json.loads((RADICE / "dati" / "domanda.json").read_text(encoding="utf-8"))
    vol = {}
    for r in dom["richieste"]:
        vol[(r["frase"].lower(), r["paese"])] = max(vol.get((r["frase"].lower(), r["paese"]), 0), r["volume"] or 0)
    return vol


def _node(js, espr, casi, err, nome):
    p = subprocess.run(["node", "-"], input=js + "\nvar K=" + json.dumps(casi) + ";process.stdout.write(JSON.stringify(K.map(function(c){return " + espr + ";})));",
                       capture_output=True, text=True)
    if p.returncode:
        err(f"node ({nome}): " + p.stderr[:300])
        return None
    return json.loads(p.stdout)


# ---------------------------------------------------------------- fonti e frasi (comune alle due sezioni)
def fonti(err, ok, G):
    uk = json.loads((RADICE / "dati" / "uk_2027.json").read_text(encoding="utf-8"))
    aff = json.loads((RADICE / "dati" / "affitti.json").read_text(encoding="utf-8"))
    fr = []
    _frasi(uk, fr)
    _frasi(aff, fr)
    testi, n = {}, 0
    for fid, frase in fr:
        f = G.FONTI.get(fid)
        if not f or f.get("http") != 200:
            err(f"2027: fonte {fid} assente o non 200")
            continue
        if fid not in testi:
            p = RADICE / "dati" / f["testo"]
            testi[fid] = p.read_text(encoding="utf-8") if p.exists() else ""
        if _norm(frase) not in testi[fid]:
            err(f"2027: frase non trovata nel testo di {fid}: «{frase[:80]}»")
        n += 1
    ufficiali = ("gov.uk", "oag.ca.gov", "dir.ca.gov", "oregon.gov", "commerce.wa.gov", "rentguidelinesboard.cityofnewyork.us", "ontario.ca", "gov.bc.ca", "stpaul.gov", "data.bls.gov")
    n_file = 0
    for fid, f in G.FONTI.items():
        if not fid.startswith(("uk27_", "rent_", "bls_cpi_")):
            continue
        host = re.sub(r"^https://(www2?\.)?", "", f["url"]).split("/")[0]
        if not any(host == u or host.endswith("." + u) for u in ufficiali):
            err(f"2027: fonte {fid} non ufficiale ({host})")
        if f.get("originale"):
            b = (RADICE / "dati" / f["originale"]).read_bytes()
            if hashlib.sha256(b).hexdigest() != f["sha256"] or len(b) != f["byte"]:
                err(f"2027: {f['originale']} non corrisponde allo SHA-256 registrato")
            n_file += 1
        for k in ("testo", "file"):
            if f.get(k) and not (RADICE / "dati" / f[k]).exists():
                err(f"2027: manca {f[k]}")
        if (date.today() - date.fromisoformat(f["letto_il"])).days > 120:
            err(f"2027: fonte {fid} letta più di 120 giorni fa ({f['letto_il']}): rilanciare raccolta/regole2027.py")
    for k in ("uk_wms_uprating", "ca_leginfo_1947_12", "ca_sanjose_aro", "ca_la_rso", "ca_sf_rentboard"):
        if k not in G.FONTI["_non_lette"]:
            err(f"2027: {k} non è tra le fonti non lette")
    ok(f"cifre 2027: {n} frasi citate ritrovate nel testo delle fonti ufficiali ({len(testi)} documenti), {n_file} originali con lo SHA-256 registrato, solo siti ufficiali")
    return uk, aff, testi


# ---------------------------------------------------------------- A. Regno Unito
def regno_unito(err, ok, G, SITO, uk, testi):
    # 1. tabelle DWP rilette dall'originale
    doc = (GZ / "uk27_dwp.html").read_text(encoding="utf-8")
    main = re.search(r"<main\b.*?</main>", doc, re.S).group(0)
    parti = re.split(r"<h2[^>]*>(.*?)</h2>", main, flags=re.S)
    sez = {}
    for i in range(1, len(parti), 2):
        sez[_norm(_cl(parti[i]))] = [[[_cl(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)] for r in re.findall(r"<tr.*?</tr>", tb, re.S)]
                                     for tb in re.findall(r"<table.*?</table>", parti[i + 1], re.S)]
    V, n = {}, 0
    for g in uk["gruppi"]:
        for v in g["voci"]:
            V[v["k"]] = v
            try:
                t = sez[v["sezione"]][v["tabella"]]
            except (KeyError, IndexError):
                err(f"UK 2027 {v['k']}: sezione/tabella «{v['sezione']}» non trovata nel documento DWP")
                continue
            if "2026 to 2027" not in t[0][1] or "2027 to 2028" not in t[0][2] or _norm(t[0][0]) != v["intestazione"]:
                err(f"UK 2027 {v['k']}: intestazione della tabella diversa ({t[0]})")
            rr = [r for r in t[1:] if _norm(r[0]) == v["riga"]]
            if len(rr) != 1:
                err(f"UK 2027 {v['k']}: riga «{v['riga']}» non unica nella tabella")
                continue
            a, b = (int(x.replace(",", "").replace(".", "")) for x in rr[0][1:3])
            if (a, b) != (v["prima"], v["dopo"]):
                err(f"UK 2027 {v['k']}: {v['prima']}/{v['dopo']} ≠ documento DWP {a}/{b}")
            if _norm(v["frase"]) != _norm(f"{rr[0][0]} {rr[0][1]} {rr[0][2]}"):
                err(f"UK 2027 {v['k']}: la frase non è la riga della tabella")
            atteso = "month" if v["sezione"].startswith("Universal Credit") else None
            if atteso and v["periodo"] != atteso:
                err(f"UK 2027 {v['k']}: periodo {v['periodo']} ma la sezione è mensile")
            n += 1
    if "Weekly rates, unless otherwise stated." not in testi.get("uk27_dwp", "") or "Proposed benefit and pension rates 2027 to 2028" not in testi.get("uk27_dwp", ""):
        err("UK 2027: il documento DWP non dice più «Weekly rates, unless otherwise stated» o non è più «Proposed»: rivedere i testi")
    # 2. paga minima: riga GOV.UK e tabella dell'annuncio LPC
    pm = uk["paga_minima"]
    tn = testi.get("uk27_nmw", "")
    m = re.search(r"21 and over 18 to 20 Under 18 Apprentice April 2026 ((?:£[\d.]+ ?){4})April 2027 ((?:£[\d.]+ ?){4})", tn)
    if not m:
        err("UK 2027: tabella «Current rates» non trovata su GOV.UK")
    else:
        def pence(s):
            return [int(round(float(x) * 100)) for x in re.findall(r"£([\d.]+)", s)]
        p26, p27 = pence(m.group(1)), pence(m.group(2))
        for v in pm["voci"]:
            V[v["k"]] = v
            if (v["prima"], v["dopo"]) != (p26[v["colonna"]], p27[v["colonna"]]):
                err(f"UK 2027 {v['k']}: {v['prima']}/{v['dopo']} ≠ GOV.UK {p26[v['colonna']]}/{p27[v['colonna']]}")
            a = v["annuncio"]["frase"]
            if f"£{v['dopo'] / 100:.2f} {v['dopo'] - v['prima']}p {_pct10(v['prima'], v['dopo']) / 10:.1f}" not in a:
                err(f"UK 2027 {v['k']}: l'annuncio LPC («{a}») non dà la stessa cifra, lo stesso aumento e la stessa percentuale")
            n += 1
        for s in pm["storia"]:
            if pence(s["frase"]) != s["valori"]:
                err(f"UK 2027: storia {s['periodo']} ≠ frase")
    if f"£{pm['alloggio']['dopo'] / 100:.2f} {pm['alloggio']['aumento']}p" not in pm["alloggio"]["frase"]:
        err("UK 2027: accommodation offset ≠ frase")
    # 3. cifre in vigore nelle guide GOV.UK = colonna 2026-27
    for k, fid in (("sp_new", "uk27_guida_nsp_importo"), ("uc_s_u25", "uk27_guida_uc"), ("ssp", "uk27_guida_ssp")):
        if _gbp(V[k]["prima"]) not in testi.get(fid, ""):
            err(f"UK 2027 {k}: la cifra in vigore {_gbp(V[k]['prima'])} non è nella guida GOV.UK {fid}")
    # 4. pagine: ogni cifra stampata rifatta
    registrate = set()
    fr = []
    _frasi(uk, fr)
    registrate = {_pulita(f) for _, f in fr}
    n_celle, n_cit = 0, 0
    a12 = G.CPI_RATE["mensile"][G.UK_LU]
    for rel in PAGINE_UK:
        t = _pagina(SITO, rel)
        vis = re.sub(r"\s+", " ", _cl(re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S)))
        for chiave, testo in _celle(t, "uk"):
            k, campo = chiave.split("|")
            if k == "alloggio":
                atteso = _gbp(pm["alloggio"]["dopo"])
            else:
                v = V[k]
                if campo in ("prima", "dopo"):
                    atteso = _gbp(v[campo])
                elif campo == "diff":
                    atteso = _diff(v["prima"], v["dopo"])
                elif campo == "pct":
                    atteso = _pctx(_pct10(v["prima"], v["dopo"]))
                    if testo == atteso[1:]:
                        testo = atteso  # nel testo corrente la percentuale è senza segno
                elif campo == "x4":
                    atteso = _gbp(v["dopo"] * 4)
                elif campo == "x52":
                    atteso = _gbp(v["dopo"] * 52)
                elif campo == "d52":
                    atteso = _diff(v["prima"] * 52, v["dopo"] * 52)
                elif campo.startswith("storia"):
                    atteso = _gbp(pm["storia"][int(campo[6:])]["valori"][v["colonna"]])
                elif campo.startswith(("sett", "anno")):
                    od = int(campo[4:])
                    c = round(v["dopo"] * od * (52 if campo.startswith("anno") else 1) / 10 + 1e-9)
                    atteso = _gbp(c)
                    testo = testo.split(" ")[0]
                else:
                    err(f"{rel}: campo data-uk sconosciuto {chiave}")
                    continue
            if testo != atteso:
                err(f"{rel}: {chiave} stampa «{testo}», atteso «{atteso}»")
            n_celle += 1
        for td in re.findall(r'<td class="n"(?![^>]*data-uk)[^>]*>', t):
            err(f"{rel}: cella numerica senza data-uk")
        for c in _citazioni(t):
            if c not in registrate:
                err(f"{rel}: citazione non registrata in uk_2027.json: «{c[:70]}»")
            n_cit += 1
        m = re.search(r"<strong data-cpi12>([^<]+)</strong>", t)
        if not m or m.group(1) != f"{a12:.1f}%":
            err(f"{rel}: tasso CPI a 12 mesi stampato {m and m.group(1)} ≠ ONS {a12}")
        if "Contains public sector information licensed under the Open Government Licence v3.0" not in vis:
            err(f"{rel}: manca l'attribuzione OGL di GOV.UK")
        if rel != "uk/minimum-wage-2027/" and "proposed" not in vis.lower():
            err(f"{rel}: non dice che le cifre DWP sono «proposed»")
        if "not a government website" not in vis:
            err(f"{rel}: manca «not a government website»")
        if CONSIGLI.search(vis):
            err(f"{rel}: frase da consiglio «{CONSIGLI.search(vis).group(0)}»")
        if not (SITO / rel / "index.html").exists():
            err(f"{rel}: pagina assente")
    for rel, k in (("uk/minimum-wage-2027/", "nlw"), ("uk/state-pension-2027/", "sp_new"), ("uk/statutory-sick-pay-2027/", "ssp")):
        t = _pagina(SITO, rel)
        tit = html.unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        des = html.unescape(re.search(r'name="description" content="([^"]*)"', t).group(1))
        if _gbp(V[k]["dopo"]) not in tit or _gbp(V[k]["dopo"]) not in des:
            err(f"{rel}: titolo o descrizione senza la cifra {_gbp(V[k]['dopo'])}")
    # 5. calcolatore della paga: dati della pagina = dati, JS pubblicato = conto con le frazioni
    t = _pagina(SITO, "uk/minimum-wage-2027/")
    dj = json.loads(re.search(r'<script type="application/json" id="pay-dati">(.*?)</script>', t, re.S).group(1))
    for v in pm["voci"]:
        if dj["fasce"].get(v["k"], [None, None, None])[1:] != [v["prima"], v["dopo"]]:
            err(f"calcolatore paga: tariffe di {v['k']} ≠ dati")
    for sel, k, od in (("data-pay-sett", "nlw", 375),):
        m = re.search(rf"<b {sel}>([^<]+)</b>", t)
        if not m or m.group(1) != _gbp(round(V[k]["dopo"] * od / 10 + 1e-9)):
            err("calcolatore paga: risultato statico diverso")
    js_file = next((SITO / "assets").glob("pay.*.js"))
    js = js_file.read_text(encoding="utf-8")
    rnd = random.Random(27)
    casi = [[rnd.randrange(400, 2500), rnd.randrange(10, 1001)] for _ in range(3000)] + [[v[c], od] for v in pm["voci"] for c in ("prima", "dopo") for od in (10, 160, 200, 300, 375, 400, 1000, 5, 375)]
    out = _node(js[:js.index("(function(){")], "pagaMin(c[0],c[1])", casi, err, "paga")
    from fractions import Fraction
    import uk2027 as U

    def su(fr):
        return int(fr + Fraction(1, 2))
    diversi = 0
    for (r, od), j in zip(casi, out or []):
        att = {"sett": su(Fraction(r * od, 10)), "mese": su(Fraction(r * od * 52, 120)), "anno": su(Fraction(r * od * 52, 10))}
        if j != att or U.paga(r, od) != att:
            diversi += 1
            if diversi < 4:
                err(f"paga JS ≠ Python: {r}p × {od / 10} h: {j} / {U.paga(r, od)} / {att}")
    if U.paga(1321, 375)["sett"] != 49538 or U.paga(1321, 375)["anno"] != 2575950:
        err("paga: 37,5 h × £13.21 ≠ £495.38 la settimana e £25,759.50 l'anno")
    ok(f"UK aprile 2027: {n} cifre = tabelle GOV.UK rilette dagli originali (documento DWP «proposed» dell'11/11/2026, paga minima GOV.UK = annuncio LPC), "
       f"cifre in vigore delle guide GOV.UK = colonna 2026-27; {n_celle} cifre e {n_cit} citazioni stampate nelle {len(PAGINE_UK)} pagine rifatte; "
       f"calcolatore della paga ({js_file.name}) = Python su {len(casi)} casi")


# ---------------------------------------------------------------- B. affitti
def _csv(fid, G):
    with open(RADICE / "dati" / G.FONTI[fid]["file"], encoding="utf-8") as f:
        return {int(r["year"]): r for r in csv.DictReader(f)}


def affitti(err, ok, G, SITO, aff, testi):
    from fractions import Fraction
    import affitti as A
    L = {x["id"]: x for x in aff["luoghi"]}
    vol = _volumi()
    oggi = date.today()
    n = 0
    # 1. ogni tetto è nella sua frase; periodi in ordine e senza buchi; l'ultimo non è scaduto
    for x in aff["luoghi"]:
        frase, paese = A.DOMANDA_PAGINA[x["id"]]
        if vol.get((frase, paese), 0) < A.SOGLIA:
            err(f"affitti {x['id']}: la frase «{frase}» ({paese}) non arriva a {A.SOGLIA} ricerche: la pagina non ha domanda misurata")
        for v in x["voci"]:
            ps = v["periodi"]
            for i, p in enumerate(ps):
                num = _pc(p["tetto"])[:-1]
                if x["id"] == "california":
                    ok_ = _norm(p["frase"]).endswith(f"{_pc(ps[0]['tetto'])} {_pc(ps[1]['tetto'])}")
                elif x["id"] == "ontario" and i == 0:
                    ok_ = p["frase"] == f"{p['da'][:4]} {num}"
                else:
                    ok_ = re.search(rf"(?<![\d.]){re.escape(num)}%", p["frase"]) is not None
                if not ok_:
                    err(f"affitti {v['k']} periodo {i}: {num}% non è nella frase «{p['frase'][:70]}»")
                if p["da"]:
                    anno_ok = any(s in _norm(p["frase"]) + _norm(x["voci"][0]["periodi"][i]["frase"]) for s in (p["da"][:4], p["da"][2:4] + " "))
                    if x["id"] == "california":
                        anno_ok = "Increase starts between 8/1/25 and 7/31/26 Increase starts between 8/1/26 and 7/31/27" in testi["rent_ca_oag"]
                    if not anno_ok:
                        err(f"affitti {v['k']} periodo {i}: l'anno {p['da'][:4]} non è nella frase")
                    if i and (date.fromisoformat(p["da"]) - date.fromisoformat(ps[i - 1]["a"])).days != 1:
                        err(f"affitti {v['k']}: buco tra i periodi")
                n += 1
            if ps[-1]["a"] and date.fromisoformat(ps[-1]["a"]) < oggi:
                err(f"affitti {v['k']}: l'ultimo periodo è finito il {ps[-1]['a']}: leggere la cifra nuova (raccolta/regole2027.py e dati/affitti.json)")
    # 2. California rifatta dagli indici (BLS per le quattro aree, DIR per le altre contee)
    n_ca = 0
    for v in L["california"]["voci"]:
        c = v["cpi"]
        for i, anno in ((0, 2025), (1, 2026)):
            if c["fonte"] == "rent_ca_dir":
                vals = [re.search(rf"{y} April (\d+\.\d+) ", testi["rent_ca_dir"]) for y in (anno - 1, anno)]
                vals = [m.group(1) if m else None for m in vals]
            else:
                tab = _csv(c["fonte"], G)
                vals = [tab.get(y, {}).get(c["mese"]) for y in (anno - 1, anno)]
            if not all(vals) or not all(re.fullmatch(r"\d+\.\d{3}", x_) for x_ in vals):
                err(f"California {v['k']} {anno}: indice non trovato ({vals})")
                continue
            a, b = (Fraction(x_) for x_ in vals)
            var = int((b / a - 1) * 1000 + Fraction(1, 2))  # decimi di punto, mezzo per eccesso
            tetto = min(5000 + var * 100, 10000)
            if tetto != v["periodi"][i]["tetto"]:
                err(f"California {v['k']} dal 1/8/{anno}: 5 % + {var / 10} % = {tetto / 1000} % ≠ Attorney General {v['periodi'][i]['tetto'] / 1000} %")
            atteso = A.california_conto(v, anno)
            if not atteso or (atteso["prima"], atteso["dopo"], atteso["var"], atteso["tetto"]) != (vals[0], vals[1], var, tetto):
                err(f"California {v['k']} {anno}: il conto del generatore è diverso")
            n_ca += 1
    if n_ca != 10:
        err(f"California: rifatti {n_ca} tetti su 10")
    # 3. Washington: indici della pagina = BLS; 7 % + variazione, massimo 10 %
    tab = _csv("bls_cpi_seattle", G)
    for i, anno in ((0, 2025), (1, 2026)):
        a, b = tab[anno - 1]["jun"], tab[anno]["jun"]
        if f"June {anno - 1} index value: {a} June {anno} index value: {b}" not in testi["rent_wa_commerce"]:
            err(f"Washington: gli indici di giugno {anno - 1}/{anno} della pagina non sono quelli del BLS ({a}, {b})")
        grezzo = (Fraction(b) / Fraction(a) - 1) * 100 + 7
        tetto = min(int(grezzo * 1000 + Fraction(1, 2)), 10000)
        if tetto != L["washington"]["voci"][0]["periodi"][i]["tetto"]:
            err(f"Washington {anno + 1}: 7 % + CPI = {float(grezzo):.3f} % → {tetto / 1000} % ≠ pubblicato")
    # 4. Oregon: 7 % + variazione scritta nel file Excel, massimo 10 %; Ontario: storia = frasi; Saint Paul fisso
    m = re.search(r"2027 (\d\.\d+E-2) 7\.0\d*E-2 0\.1 ", testi["rent_or_xlsx"])  # riga 2027: variazione dell'indice, 7 %, massimo
    if not m or min(int((Fraction(m.group(1)) + Fraction(7, 100)) * 100000), 10000) != L["oregon"]["voci"][0]["periodi"][1]["tetto"]:
        err("Oregon 2027: il file Excel non dà 7 % + CPI ≥ 10 %")
    for s in L["ontario"]["storia"]:
        if s["frase"] != f"{s['anno']} {_pc(s['tetto'])[:-1]}" and not (s["tetto"] == 0 and s["frase"] == f"{s['anno']} 0"):
            if s["frase"] != f"{s['anno']} {s['tetto'] / 1000:.1f}":
                err(f"Ontario {s['anno']}: storia ≠ frase")
    for s, p in zip(L["ontario"]["storia"][:2], reversed(L["ontario"]["voci"][0]["periodi"])):
        if s["tetto"] != p["tetto"]:
            err("Ontario: storia e periodi diversi")
    # 5. tetti locali californiani riletti dall'originale
    t = (GZ / "rent_ca_oag.html").read_text(encoding="utf-8")
    righe = []
    for r in re.findall(r"<tr.*?</tr>", re.findall(r"<table.*?</table>", t, re.S)[1], re.S)[1:]:
        c = re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)
        righe.append((_cl(re.split(r"<br\s*/?>", c[1])[0]), _cl(c[3]), _cl(c[4])))
    loc = aff["california_locali"]["righe"]
    if [(z["comune"], z["massimo"], z["periodo"]) for z in loc] != righe or len(righe) < 30:
        err("California: la tabella dei tetti locali non è quella dell'originale salvato")
    # 6. pagine
    fr = []
    _frasi(aff, fr)
    registrate = {_pulita(f) for _, f in fr}
    V = {v["k"]: v for x in aff["luoghi"] for v in x["voci"]}
    n_celle, n_cit = 0, 0
    pagine = [A.BASE] + [A.BASE + x["slug"] + "/" for x in aff["luoghi"]]
    a_us, m_us, r12 = G.ultimo_12_mesi("us")
    for rel in pagine:
        if not (SITO / rel / "index.html").exists():
            err(f"{rel}: pagina assente")
            continue
        t = _pagina(SITO, rel)
        vis = re.sub(r"\s+", " ", _cl(re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S)))
        for chiave, testo in _celle(t, "rent"):
            k, i, campo = chiave.split("|")
            p = V[k]["periodi"][int(i)]
            if campo == "tetto":
                if testo.split(" ")[0] != _pc(p["tetto"]):
                    err(f"{rel}: {chiave} stampa «{testo}», atteso {_pc(p['tetto'])}")
            else:
                r = int(campo[3:]) * 100
                inc = int(Fraction(r * p["tetto"], 100000))
                atteso = _usd(r + inc) if campo.startswith("max") else "+" + _usd(inc)
                if testo.split(" ")[0] != atteso:
                    err(f"{rel}: {chiave} stampa «{testo}», atteso {atteso}")
            n_celle += 1
        for c in _citazioni(t):
            if c not in registrate:
                err(f"{rel}: citazione non registrata in affitti.json: «{c[:70]}»")
            n_cit += 1
        dj = json.loads(re.search(r'<script type="application/json" id="rent-dati">(.*?)</script>', t, re.S).group(1))
        for k, d in dj["voci"].items():
            if [q[1] for q in d["p"]] != [p["tetto"] for p in V[k]["periodi"]] or d["d"] != len(V[k]["periodi"]) - 1:
                err(f"{rel}: dati del calcolatore per {k} ≠ affitti.json")
        if rel != A.BASE and set(dj["voci"]) != {v["k"] for v in next(x for x in aff["luoghi"] if A.BASE + x["slug"] + "/" == rel)["voci"]}:
            err(f"{rel}: il calcolatore non ha le voci del luogo")
        m = re.search(r"<b data-rent-nuovo>([^<]+)</b>", t)
        k0 = next(iter(dj["voci"]))
        if not m or m.group(1) != _usd(200000 + int(Fraction(200000 * V[k0]["periodi"][-1]["tetto"], 100000))):
            err(f"{rel}: risultato statico del calcolatore diverso")
        for frase in ("not legal advice", "not a government website", "not financial or investment advice"):
            if frase not in vis:
                err(f"{rel}: manca «{frase}»")
        if CONSIGLI.search(vis):
            err(f"{rel}: frase da consiglio «{CONSIGLI.search(vis).group(0)}»")
        n_ = len(re.findall(r'<td class="n"(?![^>]*data-(?:rent|ca|on))[^>]*>[^–<]', t))
        if n_:
            err(f"{rel}: {n_} celle numeriche senza attributo di controllo")
    t = _pagina(SITO, A.BASE)
    m = re.search(r"<strong data-cpi-us>([^<]+)</strong>", t)
    if not m or m.group(1) != f"{r12 * 100:.1f}%":
        err(f"{A.BASE}: CPI-U a 12 mesi stampato {m and m.group(1)} ≠ {r12 * 100:.1f}%")
    t = _pagina(SITO, A.BASE + "california/")
    ca = dict(_celle(t, "ca"))
    if len(ca) != 40:
        err(f"California: {len(ca)} celle del controllo con gli indici invece di 40")
    righe_p = [tuple(_cl(c) for c in re.findall(r"<td>(.*?)</td>", r, re.S)) for r in re.findall(r'<tr data-loc="\d+">.*?</tr>', t, re.S)]
    if righe_p != [(a, b, c or "–") for a, b, c in righe]:
        err("California: la tabella dei tetti locali stampata non è quella dell'Attorney General")
    t = _pagina(SITO, A.BASE + "washington/")
    wa = dict(_celle(t, "wa"))
    a, b = tab[2025]["jun"], tab[2026]["jun"]
    g = (Fraction(b) / Fraction(a) - 1) * 100
    if wa != {"prima": a, "dopo": b, "var": f"{int(g * 1000) / 1000:.2f}%", "somma": f"{int(g * 1000 + 7000) / 1000:.2f}%"} or wa.get("somma") != "11.53%":
        err(f"Washington: conto stampato {wa} diverso da quello rifatto (o da 11.53% della pagina Commerce)")
    t = _pagina(SITO, A.BASE + "ontario/")
    if dict(_celle(t, "on")) != {str(s["anno"]): _pc(s["tetto"]) for s in L["ontario"]["storia"]}:
        err("Ontario: storia stampata ≠ dati")
    for rel, lid in ((A.BASE + "washington/", "washington"), (A.BASE + "oregon/", "oregon"), (A.BASE + "ontario/", "ontario"), (A.BASE + "british-columbia/", "bc")):
        tit = html.unescape(re.search(r"<title>(.*?)</title>", _pagina(SITO, rel)).group(1))
        if _pc(L[lid]["voci"][0]["periodi"][-1]["tetto"]) not in tit:
            err(f"{rel}: il titolo non ha il tetto dell'ultimo periodo")
    # 7. motore pubblicato = conto con le frazioni
    js_file = next((SITO / "assets").glob("rent.*.js"))
    js = js_file.read_text(encoding="utf-8")
    rnd = random.Random(58)
    tetti = sorted({p["tetto"] for v in V.values() for p in v["periodi"]})
    casi = [[rnd.randrange(100, 100000001), rnd.choice(tetti)] for _ in range(4000)] + [[c, t_] for c in (100, 199999, 200000, 123457, 99999999, 100000000) for t_ in tetti]
    out = _node(js[:js.index("(function(){")], "affittoMax(c[0],c[1])", casi, err, "affitto")
    diversi = 0
    for (c, t_), j in zip(casi, out or []):
        inc = int(Fraction(c * t_, 100000))
        if j != {"aumento": inc, "nuovo": c + inc} or A.aumento(c, t_) != (inc, c + inc):
            diversi += 1
            if diversi < 4:
                err(f"affitto JS ≠ Python: {c} × {t_}: {j} / {A.aumento(c, t_)}")
    if A.aumento(200000, 8700) != (17400, 217400) or A.aumento(123457, 9683) != (11954, 135411):
        err("affitto: $2,000 × 8.7% ≠ $174.00 o $1,234.57 × 9.683% ≠ $119.54")
    ok(f"tetti agli aumenti dell'affitto: {n} periodi con la cifra nella frase ufficiale; 10 tetti californiani rifatti dagli indici BLS/DIR = Attorney General; "
       f"Washington: indici della pagina = BLS e 7 % + CPI rifatto; Oregon dal file Excel; {len(righe)} tetti locali californiani = originale; {n_celle} cifre e {n_cit} citazioni "
       f"stampate nelle {len(pagine)} pagine rifatte; ogni pagina di luogo ha una frase misurata ≥ {A.SOGLIA}; calcolatore ({js_file.name}) = Python su {len(casi)} casi")
    return pagine


def controlla(err, ok, G, SITO):
    uk, aff, testi = fonti(err, ok, G)
    regno_unito(err, ok, G, SITO, uk, testi)
    return PAGINE_UK + affitti(err, ok, G, SITO, aff, testi)
