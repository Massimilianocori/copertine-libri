"""Raccolta della sezione "California home insurance crisis by ZIP: FAIR Plan policies and non-renewals" di FloodCost.

Uso (dalla radice del repository):
    python3 floodcost/raccolta/california.py                  # scarica (se cambiate) le fonti, estrae, domanda (autocomplete, cache 28 giorni)
    python3 floodcost/raccolta/california.py --senza-domanda  # come sopra, ma la domanda solo dalla cache
Poi: python3 floodcost/genera.py && python3 floodcost/verifica.py

Fonti (lette da script, nessuna chiave; i file grezzi restano in floodcost/cache/california/, fuori da git):
  1. California FAIR Plan, pagina "Key Statistics & Data" (https://www.cfpnet.com/key-statistics-data/). Da lì si prendono i
     collegamenti più recenti (il nome del file contiene l'anno fiscale e la data di caricamento, es. ...-FY26-DWE-261020.pdf):
       - CFP-5-yr-PIF-Zip-FY..-DWE-......pdf  polizze residenziali in vigore al 30/9 di 5 anni fiscali, per ZIP
       - CFP-5-yr-TIV-Zip-FY..-DWE-......pdf  valore assicurato (Total Exposure) degli stessi anni, per ZIP
       - Policies-by-category-DWE-as-of-......pdf  polizze residenziali per ZIP x gruppo di rischio (Low/Medium/High) x tipo
       - Premium-by-category-DWE-as-of-......pdf   premio delle stesse polizze (stesse righe e colonne)
     Lettura: pdftotext -layout per i primi due, pdfplumber per gli altri due (verifica.py usa i due motori al contrario).
  2. California Department of Insurance (CDI), pagina "Data and Analysis on Wildfires and Insurance"
     (https://www.insurance.ca.gov/01-consumers/200-wrr/DataAnalysisOnWildfiresAndInsurance.cfm):
       - Residential-Insurance-Voluntary-Market-New-Renew-NonRenew-by-ZIP-AAAA-AAAA.xlsx (l'intervallo più recente): contea,
         ZIP, anno, polizze nuove, rinnovate, non rinnovate (mercato volontario, cioè compagnie ordinarie; FAIR Plan escluso)
       - Fact sheet "Summary on Residential Insurance Policies and the FAIR Plan" (PDF): da qui la definizione dei non rinnovi
         (totali, "75-80% ... initiated by policyholders") e il rapporto usato dal CDI (non rinnovi / (nuove + rinnovate)).
  3. GeoNames, codici postali USA (https://download.geonames.org/export/zip/US.zip, CC BY 4.0): nome del luogo e contea dello ZIP.
  4. Google Autocomplete (gl=us, hl=en): domanda per le pagine di contea e città (dati/california-domanda.json).

Scrive dati/california.json (con "letto_il", le impronte SHA-256 dei file sorgente e "impronta" del contenuto) e
dati/california-domanda.json.
"""
import hashlib
import html
import io
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
CACHE = RADICE / "cache" / "california"
UA = "floodcost-data-refresh/1.0 (static site; yearly California insurance data)"
AUTOCOMPLETE = "https://suggestqueries.google.com/complete/search?client=firefox&gl=us&hl=en&q="
DOMANDA_VALIDA_GIORNI = 28

CFP_PAGINA = "https://www.cfpnet.com/key-statistics-data/"
CDI_PAGINA = "https://www.insurance.ca.gov/01-consumers/200-wrr/DataAnalysisOnWildfiresAndInsurance.cfm"
GEONAMES = "https://download.geonames.org/export/zip/US.zip"
# chiave -> espressione del nome del file nella pagina ufficiale (si prende il più recente)
CFP_FILE = {
    "pif_zip": r"CFP-5-yr-PIF-Zip-FY(\d\d)-DWE-(\d{6})\.pdf",
    "tiv_zip": r"CFP-5-yr-TIV-Zip-FY(\d\d)-DWE-(\d{6})\.pdf",
    "pol_cat": r"Policies-by-category-DWE-as-of-(\d{6})-DL-(\d{6})v\d+\.pdf",
    "prem_cat": r"Premium-by-category-DWE-as-of-(\d{6})-DL-(\d{6})v\d+\.pdf",
}
CDI_FILE = {
    "cdi_zip": r"Residential-Insurance-Voluntary-Market-New-Renew-NonRenew-by-ZIP-(\d{4})-(\d{4})\.xlsx",
    "cdi_fact": r"CDI-Fact-Sheet-Summary-on-Residential-Insurance-Policies-and-the-FAIR-Plan-v-(\d{6})[^\"']*\.pdf",
}
# frasi del fact sheet CDI che il sito riporta (devono esserci, parola per parola, nel PDF)
FRASI_CDI = ["Past research shows that 75-80% of non-renewals are initiated by policyholders",
             "The non-renewals presented are the total non-renewals for each year"]
CATEGORIE = ["Owner-occupied Single Family Residential", "Tenant-occupied", "Renters", "Condo unit-owners", "Other"]
RISCHI = ["Low", "Medium", "High"]


def leggi(url, tentativi=4, attesa=5):
    for i in range(tentativi):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read(), r.headers.get("Last-Modified"), r.status
        except Exception as e:
            if i == tentativi - 1:
                raise
            print(f"  riprovo ({e}) {url[:110]}", file=sys.stderr)
            time.sleep(attesa * (i + 1))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def collegamenti(pagina_url, regole):
    """Legge la pagina ufficiale e sceglie, per ogni chiave, il collegamento più recente che corrisponde all'espressione."""
    corpo, _, stato = leggi(pagina_url)
    testo = corpo.decode("utf-8", errors="replace")
    out = {}
    for k, rx in regole.items():
        trovati = []
        for href in re.findall(r'href=["\']([^"\']+)["\']', testo):
            m = re.search(rx, href)
            if m:
                trovati.append((m.groups(), urllib.parse.urljoin(pagina_url, html.unescape(href))))
        if not trovati:
            sys.exit(f"ERRORE: nessun collegamento {k} ({rx}) in {pagina_url}: la pagina è cambiata, controllare a mano")
        out[k] = sorted(trovati)[-1][1]
    return out, stato


def scarica(chiave, url, oggi):
    """Scarica il file in cache/california/ e ne registra impronta, dimensione e data."""
    CACHE.mkdir(parents=True, exist_ok=True)
    corpo, lm, stato = leggi(url)
    nome = url.rsplit("/", 1)[-1]
    (CACHE / nome).write_bytes(corpo)
    print(f"  {chiave}: {nome} ({len(corpo):,} byte, HTTP {stato})")
    return {"url": url, "file": nome, "sha256": sha(corpo), "byte": len(corpo), "last_modified": lm, "letto_il": oggi.isoformat()}


# ---------------------------------------------------------------- FAIR Plan: polizze e valore assicurato per ZIP (pdftotext)
def pdftotext(nome):
    return subprocess.run(["pdftotext", "-layout", str(CACHE / nome), "-"], check=True, capture_output=True, text=True).stdout


def numero(t):
    t = t.replace("$", "").replace(",", "").strip()
    return 0 if t in ("-", "") else int(t)


def leggi_5anni(nome):
    """Righe 'ZIP  g% n  g% n ...' (5 anni, dal più recente). Ritorna (anni, {zip: ([n x5], [g x5])}, totale)."""
    testo = pdftotext(nome)
    anni = None
    for riga in testo.splitlines():
        a = re.findall(r"9/30/(20\d\d)\b", riga)
        if len(a) == 5:
            anni = [int(x) for x in a]
            break
    righe, totale = {}, None
    for riga in testo.splitlines():
        m = re.match(r"\s*(\d{5}|Total)\s+(.*)$", riga)
        if not m:
            continue
        tok = m.group(2).replace("$", " ").split()
        if len(tok) != 10 or not all(t.endswith("%") for t in tok[0::2]):
            sys.exit(f"ERRORE: riga non riconosciuta in {nome}: {riga.strip()[:120]}")
        n = [numero(t) for t in tok[1::2]]
        g = [int(t[:-1]) for t in tok[0::2]]
        if m.group(1) == "Total":
            if totale and totale[0] != n:
                sys.exit(f"ERRORE: righe Total diverse in {nome}")
            totale = (n, g)
        else:
            if m.group(1) in righe:
                sys.exit(f"ERRORE: ZIP ripetuto in {nome}: {m.group(1)}")
            righe[m.group(1)] = (n, g)
    # l'intestazione del file TIV 2026 ha un refuso ("9/30/20256"): gli anni si prendono dal file PIF dello stesso rilascio
    return anni, righe, totale


# ---------------------------------------------------------------- FAIR Plan: polizze e premio per categoria (pdfplumber)
def leggi_categorie(nome, con_dollari):
    """Righe 'ZIP Contea 0|1 Regione' + 15 valori (Low, Medium, High x 5 tipi). Ritorna ({zip: {...}}, [15 totali])."""
    import pdfplumber
    righe, totale = {}, None
    with pdfplumber.open(str(CACHE / nome)) as pdf:
        for pg in pdf.pages:
            for riga in (pg.extract_text() or "").splitlines():
                m = re.match(r"(\d{5}|All) (.+)$", riga)
                if not m:
                    continue
                if con_dollari:
                    pezzi = riga.split("$")
                    testa, celle = pezzi[0], pezzi[1:]
                    valori = [numero(c.replace(" ", "")) for c in celle]
                else:
                    tok = riga.split()
                    valori = [numero(t) for t in tok[-15:]]
                    testa = " ".join(tok[:-15])
                if len(valori) != 15:
                    sys.exit(f"ERRORE: {len(valori)} valori invece di 15 in {nome}: {riga[:120]}")
                if m.group(1) == "All":
                    totale = valori
                    continue
                t = re.match(r"(\d{5}) (.+?) ([01]) (.+?)\s*$", testa.strip())
                if not t:
                    sys.exit(f"ERRORE: intestazione di riga non riconosciuta in {nome}: {testa[:80]}")
                z = t.group(1)
                if z in righe:
                    sys.exit(f"ERRORE: ZIP ripetuto in {nome}: {z}")
                righe[z] = {"contea": t.group(2), "dist": int(t.group(3)), "regione": t.group(4), "v": valori}
    mancano = [totale[i] - sum(r["v"][i] for r in righe.values()) for i in range(15)]
    return righe, totale, mancano


# ---------------------------------------------------------------- CDI: nuove, rinnovate, non rinnovate per ZIP (openpyxl)
def leggi_cdi(nome):
    import openpyxl
    wb = openpyxl.load_workbook(str(CACHE / nome), read_only=True, data_only=True)
    ws = wb.worksheets[0]
    righe = list(ws.iter_rows(values_only=True))
    intest = [str(x).strip() for x in righe[0]]
    if intest != ["County", "ZIP Code", "Year", "New", "Renewed", "Non-Renewed"]:
        sys.exit(f"ERRORE: intestazione XLSX CDI cambiata: {intest}")
    out, stato, anni = {}, {}, set()
    for r in righe[1:]:
        if r[1] is None:
            continue
        z = f"{int(r[1]):05d}"
        a = int(r[2])
        anni.add(a)
        v = [int(r[3] or 0), int(r[4] or 0), int(r[5] or 0)]
        d = out.setdefault(z, {"contea": (r[0] or "").strip(), "anni": {}})
        if str(a) in d["anni"]:
            sys.exit(f"ERRORE: ZIP {z} anno {a} ripetuto nell'XLSX CDI")
        d["anni"][str(a)] = v
        s = stato.setdefault(str(a), [0, 0, 0])
        for i in range(3):
            s[i] += v[i]
    return out, stato, sorted(anni), len(righe) - 1


def controlla_fact_sheet(nome):
    testo = re.sub(r"\s+", " ", subprocess.run(["pdftotext", str(CACHE / nome), "-"], check=True, capture_output=True, text=True).stdout)
    for f in FRASI_CDI:
        if f not in testo:
            sys.exit(f"ERRORE: nel fact sheet CDI non c'è più la frase: {f}")
    m = re.search(r"Published ([A-Z][a-z]+ \d{1,2}, \d{4})", testo)
    # tabella dell'appendice A: righe "anno nuove rinnovate non_rinnovate ..." del mercato volontario
    app = {}
    lay = subprocess.run(["pdftotext", "-layout", str(CACHE / nome), "-"], check=True, capture_output=True, text=True).stdout
    i = lay.find("Appendix A: Statewide Policy Counts")
    if i < 0:
        sys.exit("ERRORE: nel fact sheet CDI non c'è più l'appendice A")
    for a, n, r, nr in re.findall(r"^\s*(20\d\d)\s+([\d,]{6,})\s+([\d,]{7,})\s+([\d,]{6,})\s", lay[i:i + 3000], re.M):
        app.setdefault(a, [numero(n), numero(r), numero(nr)])
    return (m.group(1) if m else None), app


# ---------------------------------------------------------------- GeoNames: luogo e contea dello ZIP
def leggi_geonames(nome):
    with zipfile.ZipFile(CACHE / nome) as zf:
        testo = zf.read("US.txt").decode("utf-8")
    out = {}
    for riga in testo.splitlines():
        c = riga.split("\t")
        if len(c) > 6 and c[4] == "CA":
            contea = re.sub(r"^City and County of ", "", c[5])
            out[c[1]] = {"luogo": c[2], "contea": contea, "fips": "06" + c[6] if c[6] else None}
    return out


# ---------------------------------------------------------------- domanda (Google Autocomplete)
def autocomplete(q, cache, oggi, solo_cache):
    c = cache.get(q)
    if solo_cache or (c and (oggi - date.fromisoformat(c["letto"])).days < DOMANDA_VALIDA_GIORNI):
        return (c or {}).get("s") or []
    try:
        corpo, _, _ = leggi(AUTOCOMPLETE + urllib.parse.quote(q), tentativi=3, attesa=10)
        d = json.loads(corpo.decode("utf-8", errors="ignore"))
        s = d[1] if isinstance(d, list) and len(d) > 1 else []
    except Exception as e:
        print(f"  autocomplete non letto: {q} ({e})", file=sys.stderr)
        return (c or {}).get("s") or []
    cache[q] = {"letto": oggi.isoformat(), "s": s}
    time.sleep(0.35)
    return s


# Un suggerimento conta se cita il luogo E il tema (FAIR Plan, rinnovo negato, compagnie che lasciano, assicurazione casa).
TEMA = re.compile(r"\b(fair plan|non[- ]?renew\w*|nonrenew\w*|dropped|cancel\w*|leaving|pulling out)\b")
QUERY_LUOGO = ["california fair plan {l}", "fair plan {l}", "insurance non renewal {l}"]
QUERY_GENERALI = ["california fair plan cost by zip code", "fair plan cost by zip", "california fair plan by zip code",
                  "fair plan zip code", "california fair plan ", "california fair plan cost", "insurance non renewal ",
                  "home insurance non renewal california", "state farm non renewal zip codes california",
                  "which insurance companies are writing new policies in california", "home insurance companies leaving california",
                  "california fair plan rate increase by zip code", "california fair plan map by zip code",
                  "how much is the california fair plan", "california fair plan vs", "dic policy california",
                  "what does california fair plan cover", "what is a dic policy", "how does california fair plan work",
                  "is california fair plan expensive", "what to do if homeowners insurance is not renewed"]


def domanda(zipd, oggi, solo_cache):
    """Decide quali contee e città hanno una pagina: (a) un suggerimento con il nome del luogo e una parola del tema per una delle
    query QUERY_LUOGO; (b) almeno 1.000 polizze FAIR Plan residenziali al 30/9 nell'area (sotto, la pagina sarebbe sottile).
    Le città candidate sono i nomi GeoNames con almeno 1.000 polizze; le contee tutte quelle con almeno 1.000 polizze."""
    file_dom = DATI / "california-domanda.json"
    D = json.loads(file_dom.read_text(encoding="utf-8")) if file_dom.exists() else {}
    cache = D.get("query", {})

    def ac(q):
        return autocomplete(q, cache, oggi, solo_cache)
    for q in QUERY_GENERALI:
        ac(q)
    contee, citta = {}, {}
    for z, r in zipd.items():
        p = r.get("pif", [0])[-1]
        if r.get("contea"):
            contee[r["contea"]] = contee.get(r["contea"], 0) + p
        if r.get("luogo"):
            citta[r["luogo"]] = citta.get(r["luogo"], 0) + p
    pagine = {"contee": {}, "citta": {}}
    prove = {"contee": {}, "citta": {}}
    for tipo, aree, fmt in (("contee", contee, "{n} county"), ("citta", citta, "{n}")):
        for nome, pol in sorted(aree.items(), key=lambda x: -x[1]):
            if pol < 1000:
                continue
            luogo = fmt.format(n=nome.lower())
            hit = None
            for qm in QUERY_LUOGO:
                for s in ac(qm.format(l=luogo)):
                    x = s.lower()
                    if luogo in x and TEMA.search(x.replace(luogo, " ")):
                        hit = s
                        break
                if hit:
                    break
            prove[tipo][nome] = hit
            if hit:
                pagine[tipo][nome] = hit
    D = {"_nota": "Google Autocomplete (client=firefox, gl=us, hl=en), letto da raccolta/california.py. 'query': suggerimenti con la data "
                  "di lettura (riusati per 28 giorni). 'pagine': contee e città con una pagina e il suggerimento che lo giustifica.",
         "regola": "Pagina di contea o di città se l'area ha almeno 1.000 polizze FAIR Plan residenziali al 30/9 E un suggerimento, per una "
                   "delle query " + ", ".join(f"'{q}'" for q in QUERY_LUOGO) + " (luogo = '<contea> county' o il nome della città), "
                   "che contiene il luogo e una parola del tema (fair plan, non renewal, dropped, cancel, leaving, pulling out). "
                   "Città = nome del luogo GeoNames degli ZIP.",
         "generali": {q: (cache.get(q) or {}).get("s") for q in QUERY_GENERALI},
         "prove": prove, "pagine": pagine, "query": dict(sorted(cache.items()))}
    file_dom.write_text(json.dumps(D, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    return pagine


# ---------------------------------------------------------------- principale
def main():
    oggi = date.today()
    print("FAIR Plan: pagina Key Statistics ...")
    link_cfp, _ = collegamenti(CFP_PAGINA, CFP_FILE)
    print("CDI: pagina Data and Analysis ...")
    link_cdi, _ = collegamenti(CDI_PAGINA, CDI_FILE)
    fonti = {}
    for k, u in {**link_cfp, **link_cdi, "geonames": GEONAMES}.items():
        fonti[k] = scarica(k, u, oggi)
    fonti["cfp_pagina"] = {"url": CFP_PAGINA, "letto_il": oggi.isoformat()}
    fonti["cdi_pagina"] = {"url": CDI_PAGINA, "letto_il": oggi.isoformat()}

    # data di caricamento del rilascio FAIR Plan (AAMMGG nel nome del file) e data dei dati (30/9 dell'anno fiscale)
    m = re.search(r"FY(\d\d)-DWE-(\d{2})(\d{2})(\d{2})\.pdf", fonti["pif_zip"]["file"])
    pubblicato = f"20{m.group(2)}-{m.group(3)}-{m.group(4)}"
    anni, pif, pif_tot = leggi_5anni(fonti["pif_zip"]["file"])
    _, tiv, tiv_tot = leggi_5anni(fonti["tiv_zip"]["file"])
    if anni is None or anni[0] != 2000 + int(m.group(1)):
        sys.exit(f"ERRORE: anni del file PIF non riconosciuti: {anni}")
    al = f"{anni[0]}-09-30"
    if set(pif) != set(tiv):
        sys.exit(f"ERRORE: ZIP diversi tra PIF ({len(pif)}) e TIV ({len(tiv)})")
    for i in range(5):
        if sum(v[0][i] for v in pif.values()) != pif_tot[0][i]:
            print(f"  attenzione: PIF {anni[i]} somma ZIP {sum(v[0][i] for v in pif.values()):,} ≠ Total {pif_tot[0][i]:,}")
        if sum(v[0][i] for v in tiv.values()) != tiv_tot[0][i]:
            print(f"  attenzione: TIV {anni[i]} somma ZIP {sum(v[0][i] for v in tiv.values()):,} ≠ Total {tiv_tot[0][i]:,}")
    pol, pol_tot, pol_manca = leggi_categorie(fonti["pol_cat"]["file"], con_dollari=False)
    prem, prem_tot, prem_manca = leggi_categorie(fonti["prem_cat"]["file"], con_dollari=True)
    if sum(pol_tot) != pif_tot[0][0]:
        sys.exit(f"ERRORE: polizze per categoria {sum(pol_tot):,} ≠ polizze per ZIP {pif_tot[0][0]:,}")
    if any(prem_manca):
        sys.exit(f"ERRORE: le righe del file dei premi non sommano alla riga All: {prem_manca}")
    # Il PDF delle polizze per categoria del 20/10/2026 finisce prima delle ultime righe (95962 e 95972, Yuba, presenti nel
    # file dei premi): la differenza con la riga All deve essere esattamente la somma delle loro polizze nel file PIF.
    tronchi = sorted(set(prem) - set(pol))
    if sum(pol_manca) != sum(pif[z][0][0] for z in tronchi if z in pif):
        sys.exit(f"ERRORE: polizze per categoria: mancano {sum(pol_manca):,} polizze non spiegate dagli ZIP {tronchi}")
    if tronchi:
        print(f"  nota: righe assenti nel PDF delle polizze per categoria (presenti nei premi): {tronchi} ({sum(pol_manca):,} polizze)")
    cdi, cdi_stato, cdi_anni, cdi_righe = leggi_cdi(fonti["cdi_zip"]["file"])
    fact_data, fact_app = controlla_fact_sheet(fonti["cdi_fact"]["file"])
    if not fact_app:
        sys.exit("ERRORE: appendice A del fact sheet CDI non letta")
    for a, v in cdi_stato.items():
        if a in fact_app and fact_app[a] != v:
            sys.exit(f"ERRORE: totali CDI {a} dall'XLSX {v} diversi dal fact sheet {fact_app[a]}")
    geo = leggi_geonames(fonti["geonames"]["file"])
    fonti["cdi_fact"]["pubblicato"] = fact_data
    fonti["cdi_zip"]["righe"] = cdi_righe

    zipd = {}
    for z in sorted(set(pif) | set(cdi)):
        r = {}
        g = geo.get(z, {})
        c = pol.get(z) or prem.get(z)
        # contea: quella del rapporto FAIR Plan (gli ZIP a cavallo vanno alla contea più popolosa), poi CDI, poi GeoNames
        r["contea"] = (c or {}).get("contea") or (cdi.get(z) or {}).get("contea") or g.get("contea") or None
        r["luogo"] = g.get("luogo")
        if z in pif:
            r["pif"] = pif[z][0][::-1]   # dal 2022 al 2026
            r["pif_g"] = pif[z][1][::-1]  # crescita stampata nel PDF (%), stesso ordine
            r["tiv"] = tiv[z][0][::-1]
            r["tiv_g"] = tiv[z][1][::-1]
        if z in pol:
            r["dist"] = pol[z]["dist"]
            r["regione"] = pol[z]["regione"]
            r["pol"] = pol[z]["v"]
        if z in prem:
            r["prem"] = prem[z]["v"]
            if z in pol and (prem[z]["dist"], prem[z]["regione"]) != (pol[z]["dist"], pol[z]["regione"]):
                print(f"  attenzione: ZIP {z}: distressed/regione diversi tra polizze e premi")
        if z in cdi:
            r["cdi"] = cdi[z]["anni"]
        zipd[z] = r
    # FIPS della contea dai nomi GeoNames (contea -> codice), così le pagine collegano le contee di FloodCost
    fips = {}
    for g in geo.values():
        if g["fips"]:
            fips[g["contea"].lower()] = g["fips"]
    senza = sorted({r["contea"] for r in zipd.values() if r.get("contea") and r["contea"].lower() not in fips})
    if senza:
        print(f"  attenzione: contee senza codice FIPS: {senza}")
    for r in zipd.values():
        r["fips"] = fips.get((r.get("contea") or "").lower())
    print(f"FAIR Plan al {al} (rilascio {pubblicato}): {len(pif):,} ZIP, {pif_tot[0][0]:,} polizze, ${tiv_tot[0][0]:,}; "
          f"categorie: {len(pol):,} ZIP polizze, {len(prem):,} ZIP premi")
    print(f"CDI: {cdi_righe:,} righe, {len(cdi):,} ZIP, anni {cdi_anni}; fact sheet pubblicato {fact_data}")
    dom = domanda(zipd, oggi, "--senza-domanda" in sys.argv)
    print(f"Domanda: {len(dom['contee'])} contee e {len(dom['citta'])} città con pagina")
    out = {"_nota": "Generato da raccolta/california.py. zip[z].pif/tiv = polizze residenziali FAIR Plan e valore assicurato ($) al 30/9 "
                    "dal 2022 al 2026; pif_g/tiv_g = crescita annua stampata nel PDF (%). pol/prem = polizze e premio ($) per gruppo "
                    "di rischio (Low, Medium, High) x tipo (" + ", ".join(CATEGORIE) + "), 15 valori nell'ordine del PDF. "
                    "cdi[anno] = [nuove, rinnovate, non rinnovate] del mercato volontario (CDI). dist = 1 se il rapporto FAIR Plan "
                    "segna lo ZIP come distressed area.",
           "letto_il": oggi.isoformat(), "fonti": fonti,
           "fair": {"al": al, "pubblicato": pubblicato, "anni": anni[::-1], "pif_tot": pif_tot[0][::-1], "pif_tot_g": pif_tot[1][::-1],
                    "tiv_tot": tiv_tot[0][::-1], "tiv_tot_g": tiv_tot[1][::-1], "pol_tot": pol_tot, "prem_tot": prem_tot,
                    "pol_righe_assenti": tronchi,
                    "rischi": RISCHI, "categorie": CATEGORIE},
           "cdi": {"anni": cdi_anni, "stato": cdi_stato, "frasi": FRASI_CDI},
           "pagine": dom, "zip": zipd}
    corpo = json.dumps(out, ensure_ascii=False, sort_keys=True)
    out["impronta"] = hashlib.sha256(corpo.encode("utf-8")).hexdigest()
    (DATI / "california.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Scritto dati/california.json (impronta {out['impronta'][:12]}, {len(zipd):,} ZIP)")


if __name__ == "__main__":
    main()
