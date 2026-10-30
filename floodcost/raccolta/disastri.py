"""Raccolta della sezione "Disaster declarations and IRS tax relief by county" di FloodCost.

Uso (dalla radice del repository):
    python3 floodcost/raccolta/disastri.py                  # FEMA + IRS + domanda (autocomplete, con cache di 28 giorni)
    python3 floodcost/raccolta/disastri.py --senza-domanda  # FEMA + IRS, domanda solo dalla cache
Poi: python3 floodcost/genera.py && python3 floodcost/verifica.py

Fonti (lette da script, nessuna chiave):
  1. OpenFEMA DisasterDeclarationsSummaries v2 (https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries): una riga per
     dichiarazione x area designata, dichiarazioni degli ultimi 24 mesi (declarationDate). Pubblico dominio; citazione OpenFEMA
     nel piè di pagina di ogni pagina. Metadati (versione, lastRefresh) da OpenFemaDataSets v1.
  2. IRS "Tax relief in disaster situations" (https://www.irs.gov/newsroom/tax-relief-in-disaster-situations): elenco dei
     comunicati per data con il codice (es. FL-2026-07). Si leggono i comunicati degli Stati/territori dell'anno in corso e
     dell'anno prima. Da ogni comunicato: data, frase ufficiale con la nuova scadenza ("now have until ..."), frase con le
     località ("... qualify for tax relief"). Le contee si collegano SOLO se ogni nome della frase corrisponde a una contea
     del Census (o a un'area FEMA) dello stesso Stato; altrimenti il comunicato resta a livello di Stato con la frase e il link.
  3. Google Autocomplete (suggestqueries.google.com, client=firefox, gl=us, hl=en): domanda per contea e per Stato. Risultati in
     dati/disastri-domanda.json (data di lettura per ogni query, riusati per 28 giorni).

Scrive dati/disastri.json (con "letto_il" e "impronta" SHA-256 del contenuto) e dati/disastri-domanda.json.
"""
import hashlib
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
CACHE = RADICE / "cache"
API = "https://www.fema.gov/api/open"
EP_FEMA = f"{API}/v2/DisasterDeclarationsSummaries"
IRS = "https://www.irs.gov"
IRS_INDICE = IRS + "/newsroom/tax-relief-in-disaster-situations"
CENSUS = "https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt"
AUTOCOMPLETE = "https://suggestqueries.google.com/complete/search?client=firefox&gl=us&hl=en&q="
MESI_FINESTRA = 24
DOMANDA_VALIDA_GIORNI = 28
UA = "floodcost-data-refresh/1.0 (static site, weekly)"
CAMPI = ("femaDeclarationString,disasterNumber,state,declarationType,declarationDate,incidentType,declarationTitle,"
         "ihProgramDeclared,iaProgramDeclared,paProgramDeclared,hmProgramDeclared,incidentBeginDate,incidentEndDate,"
         "fipsStateCode,fipsCountyCode,designatedArea,lastIAFilingDate,disasterCloseoutDate,id,lastRefresh")

# Codici IRS dei comunicati -> sigla postale (NMI = Isole Marianne Settentrionali)
CODICE_IRS = {"NMI": "MP"}
STATI_NOMI = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
    "AS": "American Samoa", "GU": "Guam", "MP": "Northern Mariana Islands", "PR": "Puerto Rico", "VI": "U.S. Virgin Islands",
    "FM": "Micronesia", "MH": "Marshall Islands", "PW": "Palau"}
MESI = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
SUFFISSI = (" County", " Parish", " Borough", " Census Area", " City and Borough", " Municipality", " Municipio", " city", " District",
            " Island", " Islands")


def leggi(url, tentativi=5, attesa=4):
    for i in range(tentativi):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except Exception as e:
            if i == tentativi - 1:
                raise
            print(f"  riprovo ({e}) {url[:110]}", file=sys.stderr)
            time.sleep(attesa * (i + 1))


# ---------------------------------------------------------------- Census: nomi delle contee
def contee_census():
    f = CACHE / "contee-census.txt"
    if not f.exists():
        CACHE.mkdir(exist_ok=True)
        f.write_bytes(leggi(CENSUS))
    out = {}
    for riga in f.read_text(encoding="utf-8", errors="ignore").splitlines()[1:]:
        p = riga.split("|")
        if len(p) >= 5:
            out[p[1] + p[2]] = (p[0], p[4])
    return out


# ---------------------------------------------------------------- FEMA
def fema(da):
    righe, skip = [], 0
    while True:
        q = urllib.parse.urlencode({"$filter": f"declarationDate ge '{da}'", "$select": CAMPI, "$orderby": "id",
                                    "$top": 1000, "$skip": skip, "$inlinecount": "allpages"})
        d = json.loads(leggi(f"{EP_FEMA}?{q}"))
        r = d["DisasterDeclarationsSummaries"]
        if skip == 0:
            totale = d["metadata"]["count"]
        righe += r
        if len(r) < 1000:
            break
        skip += 1000
    if len(righe) != totale:
        raise SystemExit(f"FEMA: lette {len(righe)} righe, attese {totale}")
    meta = json.loads(leggi(f"{API}/v1/OpenFemaDataSets?$filter=" + urllib.parse.quote("name eq 'DisasterDeclarationsSummaries'")))
    m = max(meta["OpenFemaDataSets"], key=lambda x: x["version"])
    return righe, {"titolo": m["title"], "versione": m["version"], "endpoint": EP_FEMA, "dizionario": m.get("dataDictionary"),
                   "lastRefresh": m.get("lastRefresh"), "righe_totali_dataset": m.get("recordCount"), "righe_lette": len(righe),
                   "filtro": f"declarationDate ge '{da}'", "ultima_riga_aggiornata": max((r.get("lastRefresh") or "") for r in righe)}


def nome_area(designata):
    """'Washington (County)' -> 'Washington County'; 'Bedford' -> 'Bedford'; 'Lexington' -> 'Lexington'."""
    m = re.match(r"^(.*?) \((County|Parish|Borough|Census Area|Municipio|Municipality|County-equivalent|City and Borough)\)$", designata)
    if not m:
        return designata
    tipo = m.group(2)
    if tipo == "County-equivalent":
        return m.group(1)
    return f"{m.group(1)} {tipo}"


def elabora_fema(righe, census):
    dich, aree, speciali = {}, {}, {}
    for r in righe:
        k = r["femaDeclarationString"]
        if k not in dich:
            dich[k] = {"n": r["disasterNumber"], "tipo": r["declarationType"], "st": r["state"], "titolo": (r["declarationTitle"] or "").strip(),
                       "incidente": r["incidentType"], "data": r["declarationDate"][:10],
                       "inizio": (r["incidentBeginDate"] or "")[:10], "fine": (r["incidentEndDate"] or "")[:10] or None,
                       "ultimo_ia": (r["lastIAFilingDate"] or "")[:10] or None, "chiuso": (r["disasterCloseoutDate"] or "")[:10] or None,
                       "ih": False, "ia": False, "pa": False, "hm": False, "aree": 0, "aree_ih": 0}
        D = dich[k]
        D["aree"] += 1
        for p, campo in (("ih", "ihProgramDeclared"), ("ia", "iaProgramDeclared"), ("pa", "paProgramDeclared"), ("hm", "hmProgramDeclared")):
            D[p] = D[p] or bool(r[campo])
        D["aree_ih"] += bool(r["ihProgramDeclared"])
        programmi = [int(bool(r[c])) for c in ("ihProgramDeclared", "iaProgramDeclared", "paProgramDeclared", "hmProgramDeclared")]
        if r["fipsCountyCode"] and r["fipsCountyCode"] != "000":
            fips = r["fipsStateCode"] + r["fipsCountyCode"]
            c = census.get(fips)
            A = aree.setdefault(fips, {"st": r["state"], "nome": c[1] if c else nome_area(r["designatedArea"]), "fema": r["designatedArea"], "d": {}})
            prec = A["d"].get(k)
            A["d"][k] = [max(a, b) for a, b in zip(prec, programmi)] if prec else programmi  # una dichiarazione può avere più righe per area
        else:
            S = speciali.setdefault(r["state"], {})
            S.setdefault(r["designatedArea"], {})[k] = programmi
    for A in aree.values():
        A["d"] = [[k] + v for k, v in sorted(A["d"].items(), key=lambda kv: (dich[kv[0]]["data"], kv[0]), reverse=True)]
    for S in speciali.values():
        for nome in list(S):
            S[nome] = [[k] + v for k, v in sorted(S[nome].items(), key=lambda kv: dich[kv[0]]["data"], reverse=True)]
    return dich, aree, speciali


# ---------------------------------------------------------------- IRS
def testo(html_):
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html_, flags=re.S)
    s = re.sub(r"<br\s*/?>|</p>|</li>|</h\d>", "\n", s)
    s = html.unescape(re.sub(r"<[^>]+>", " ", s)).replace("\xa0", " ")
    return re.sub(r"[ \t]+", " ", s)


def data_irs(s):
    """'Feb. 8, 2027' / 'Sept. 28, 2026' / 'January 7, 2027' / 'Oct.9, 2026' -> '2027-02-08'."""
    m = re.match(r"\s*([A-Z][a-z]{2,8})\.?\s*(\d{1,2}),\s*(\d{4})", s)
    if not m:
        return None
    mese = MESI.get(m.group(1)[:3].lower())
    return date(int(m.group(3)), mese, int(m.group(2))).isoformat() if mese else None


DATA_RE = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{1,2},\s*\d{4}"


def indice_irs(anni):
    t = leggi(IRS_INDICE).decode("utf-8", errors="ignore")
    voci = []
    for li in re.findall(r"<li[^>]*>(.*?)</li>", t, re.S):
        a = re.search(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', li, re.S)
        s = html.unescape(re.sub(r"<[^>]+>", "", li)).replace("\xa0", " ").strip()
        m = re.match(r"([A-Z]{2,3})-(\d{4})-(\d+)", s)
        if not (a and m) or m.group(1) == "IR" or int(m.group(2)) not in anni:
            continue
        st = CODICE_IRS.get(m.group(1), m.group(1))
        if st not in STATI_NOMI:
            continue
        url = a.group(1) if a.group(1).startswith("http") else IRS + a.group(1)
        voci.append({"codice": m.group(0), "st": st, "url": url, "titolo": html.unescape(re.sub(r"<[^>]+>", "", a.group(2))).strip()})
    return voci, len(t)


def risolvi_nomi(nomi, st, census, aree_fema, suff=""):
    """Nomi di località IRS -> FIPS dello stesso Stato, solo per corrispondenza esatta con un nome del Census o di FEMA (niente
    deduzioni). Ritorna (fips trovati, nomi non trovati): un nome che non corrisponde (errore di battitura nel comunicato, città
    indipendente, area tribale) resta solo nella frase citata e viene segnalato in pagina, le altre contee restano collegate."""
    per_nome = {}
    for fips, (s, n) in census.items():
        if s == st:
            per_nome.setdefault(n.lower(), fips)
    for fips, A in aree_fema.items():
        if A["st"] == st:
            per_nome.setdefault(A["nome"].lower(), fips)
    out, mancanti = [], []
    for n in nomi:
        n0 = n.strip().rstrip(".").strip()
        n0 = re.sub(r"^(?:in the |in |the )", "", n0, flags=re.I)
        n0 = re.sub(r"\s+(?:counties|county)$", "", n0, flags=re.I)
        cand = ([n0 + suff] if suff else []) + [n0] + [n0 + s for s in SUFFISSI]
        f = next((per_nome[c.lower()] for c in cand if c.lower() in per_nome), None)
        if f:
            out.append(f)
        else:
            mancanti.append(n0)
    return sorted(set(out)), mancanti


TRIBALE = re.compile(r"\b(Tribe|Tribes|Reservation|Pueblo|Nation|Band|Oyate|Indian|Rancheria|Community)\b")


def localita(frase, st, census, aree_fema):
    """Dalla frase '... reside or have a business in A, B and C counties qualify for tax relief' ricava le contee.
    Ritorna (fips o None, motivo se None, intero_stato, nomi non trovati). Le aree tribali citate nella stessa frase restano solo nella frase."""
    m = re.search(r"(?:reside|residing|located)(?: or hav(?:e|ing)(?: a)? business)? (?:anywhere )?(?:in|on) (?:the )?(.+?)\s+qualif(?:y|ies) for (?:disaster )?tax relief", frase)
    if not m:
        return None, "frase senza elenco", False, []
    s = re.sub(r"\s+", " ", m.group(1)).strip()
    nome_st = STATI_NOMI.get(st, "")
    if re.fullmatch(r"(?:entire )?(?:State of |state of |Commonwealth of |territory of )?" + re.escape(nome_st), s) or re.fullmatch(r"entire state", s, re.I):
        return None, "tutto lo Stato", True, []
    if re.search(r"\b(all|any|entire|every|designated area)\b", s, re.I):
        return None, "frase senza elenco di contee", False, []
    s = re.sub(r",? as well as (?:the )?[^,]*$", "", s) if re.search(r"as well as", s) and TRIBALE.search(s.split("as well as")[-1]) else s
    m2 = re.match(r"^(.*?)\s+(counties|county|parishes|parish|boroughs|borough|census areas|municipalities|municipios)$", s, re.I)
    if not m2:
        return None, "elenco non riconosciuto", False, []
    lista, tipo = m2.group(1), m2.group(2).lower()
    nomi = [x for x in re.split(r"\s*[,;]\s*(?:and\s+)?|\s+and\s+", lista) if x and not TRIBALE.search(x)]
    if not nomi:
        return None, "solo aree tribali", False, []
    suff = {"counties": " County", "county": " County", "parishes": " Parish", "parish": " Parish", "boroughs": " Borough",
            "borough": " Borough", "census areas": " Census Area", "municipalities": " Municipio", "municipios": " Municipio"}[tipo]
    fips, mancanti = risolvi_nomi(nomi, st, census, aree_fema, suff=suff)
    if not fips:
        return None, "nome non trovato tra le contee del Census", False, mancanti
    return fips, None, False, mancanti


def comunicato(v, census, aree_fema):
    t = testo(leggi(v["url"]).decode("utf-8", errors="ignore"))
    i = t.find("WASHINGTON")
    corpo = t[max(0, i - 600):] if i >= 0 else t
    corpo = corpo[:corpo.find("Covered disaster area")] if "Covered disaster area" in corpo else corpo[:6000]
    corpo = re.sub(r"\s*\n\s*", " ", corpo)
    m = re.search(re.escape(v["codice"]) + r"\s*[,—–-]\s*(" + DATA_RE + ")", corpo)
    pubblicato = data_irs(m.group(1)) if m else None
    agg = re.search(r"Updated on (\d{1,2})/(\d{1,2})/(\d{4})", corpo)
    aggiornato = date(int(agg.group(3)), int(agg.group(1)), int(agg.group(2))).isoformat() if agg else None
    protetto = re.sub(r"\b(St|Ste|Mt|Ft)\. ", lambda m: m.group(1) + "\u2024 ", corpo)  # "St. Louis" non chiude la frase
    frasi = [f.replace("\u2024", ".") for f in re.split(r"(?<=[a-z0-9)])\.\s+(?=[A-Z])", protetto)]
    f_scad = next((f.strip() + "." for f in frasi if re.search(r"(?:now )?have until " + DATA_RE, f)), None)
    scad = None
    if f_scad:
        scad = data_irs(re.search(r"have until (" + DATA_RE + ")", f_scad).group(1))
    if not scad:
        mt = re.search(r"postponed to (" + DATA_RE + ")", v["titolo"])
        scad = data_irs(mt.group(1)) if mt else None
    f_loc = next((f.strip() + "." for f in frasi if re.search(r"qualif(?:y|ies) for (?:disaster )?tax relief", f)), None)
    f_loc = re.sub(r"\s+,", ",", f_loc) if f_loc else None
    fips, motivo, intero, mancanti = localita(f_loc, v["st"], census, aree_fema) if f_loc else (None, "nessuna frase sulle località", False, [])
    md = re.search(r"disaster declaration issued by (?:the )?(Federal Emergency Management Agency|State of [A-Z][A-Za-z ]+?|Commonwealth of [A-Z][A-Za-z ]+?|Governor[^,]*?|[A-Z][A-Za-z ]+?)\s*(?:\(FEMA\))?\s*,", corpo)
    dichiarato_da = ("FEMA" if md and md.group(1).startswith("Federal") else md.group(1).strip()) if md else None
    if f_scad:
        f_scad = re.sub(r"^.*?WASHINGTON\s*[—–-]\s*", "", f_scad).strip()
    return {**v, "pubblicato": pubblicato, "aggiornato": aggiornato, "scadenza": scad, "frase_scadenza": f_scad,
            "frase_localita": f_loc, "contee": fips, "intero_stato": intero, "motivo_senza_contee": motivo,
            "nomi_non_trovati": mancanti if fips else [],
            "dichiarato_da": dichiarato_da}


# ---------------------------------------------------------------- domanda (Google Autocomplete)
def autocomplete(q, cache, oggi):
    c = cache.get(q)
    if c and (oggi - date.fromisoformat(c["letto"])).days < DOMANDA_VALIDA_GIORNI:
        return c["s"]
    try:
        d = json.loads(leggi(AUTOCOMPLETE + urllib.parse.quote(q), tentativi=3, attesa=10).decode("utf-8", errors="ignore"))
        s = d[1] if isinstance(d, list) and len(d) > 1 else []
    except Exception as e:
        print(f"  autocomplete non letto: {q} ({e})", file=sys.stderr)
        return c["s"] if c else None
    cache[q] = {"letto": oggi.isoformat(), "s": s}
    time.sleep(0.35)
    return s


# Parole che legano un suggerimento al tema (aiuti dopo un disastro, scadenze fiscali); "emergency management", "female" e simili no.
PAROLE_DOMANDA = re.compile(r"\b(fema|irs|federal disaster|disaster (?:declaration|declared|relief|assistance|area|aid|loans?|recovery|"
                            r"center|unemployment|snap|food|benefits|help)|tax (?:relief|extension)|emergency declaration|state of emergency)\b")


def base_nome(nome):
    for s in sorted(SUFFISSI, key=len, reverse=True):
        if nome.endswith(s):
            return nome[:-len(s)]
    return nome


def ha_domanda(nome, st, sugg_liste, nomi_ripetuti):
    """C'è domanda se un suggerimento contiene il nome della contea e una parola del tema. Se lo stesso nome di contea esiste in
    più Stati (es. Franklin County), il suggerimento deve citare anche lo Stato (nome o sigla)."""
    b = nome.lower()
    stn = STATI_NOMI.get(st, "").lower()
    for s in sugg_liste:
        for x in s or []:
            x = x.lower()
            if b not in x or not PAROLE_DOMANDA.search(x.replace(b, " ")) or re.search(r"flood (?:map|zone|insurance rate map)", x):
                continue  # "fema flood map" è la domanda del sito NFIP, non degli aiuti
            if nome.lower() in nomi_ripetuti and not (stn in x or re.search(r"\b" + st.lower() + r"\b", x)):
                continue
            return x
    return None


def eventi(irs):
    """Nomi degli eventi con nome proprio nei titoli IRS (Hurricane Isaias, Tropical Storm Arthur, Super Typhoon Bavi...)."""
    out = set()
    for c in irs:
        m = re.search(r"((?:Super )?(?:Hurricane|Tropical Storm|Typhoon|Winter Storm|Post-Tropical Storm) [A-Z][a-z]+)", c["titolo"])
        if m:
            out.add(m.group(1).lower())
    return sorted(out)


def domanda(aree, irs, oggi, solo_cache, census):
    """Legge (o riusa dalla cache) l'autocomplete e decide quali contee hanno una pagina. Ritorna {fips: [motivo, prova]}."""
    file_dom = DATI / "disastri-domanda.json"
    D = json.loads(file_dom.read_text(encoding="utf-8")) if file_dom.exists() else {}
    cache = D.get("query", {})

    def ac(q):
        return (autocomplete(q, cache, oggi) if not solo_cache else (cache.get(q) or {}).get("s")) or []
    generali = ["fema disaster declaration ", "fema disaster declaration by county", f"fema disaster declaration {oggi.year}",
                "federal disaster area ", "disaster declaration county", "irs disaster relief ", "irs tax extension disaster",
                "is my county a federal disaster area"]
    for q in generali:
        ac(q)
    ev = eventi(irs)
    dom_evento = {}
    for e in ev:
        dom_evento[e] = next((x for x in ac(f"{e} irs") if e in x.lower() and re.search(r"\b(irs|tax)\b", x.lower())), None)
        ac(f"{e} fema")
    stati = sorted({A["st"] for A in aree.values()} | {v["st"] for v in irs})
    query_stati, dom_irs, dom_fema = {}, {}, {}
    for st in stati:
        n = STATI_NOMI.get(st, st).lower()
        q_irs = [f"irs tax extension {n} hurricane", f"irs tax extension {n} storm", f"irs disaster relief {n}"]
        q_fema = [f"fema disaster declaration {n}"]
        query_stati[st] = q_irs + q_fema
        dom_irs[st] = next((x for q in q_irs for x in ac(q) if n in x.lower() and re.search(r"\b(irs|tax)\b", x.lower())), None)
        dom_fema[st] = next((x for q in q_fema for x in ac(q) if n in x.lower() and "fema" in x.lower()), None)
    # nomi di contea ripetuti in più Stati (Census): servono lo Stato nel suggerimento
    conta = {}
    for s_, n_ in census.values():
        conta[n_.lower()] = conta.get(n_.lower(), 0) + 1
    ripetuti = {k for k, v in conta.items() if v > 1}
    oggi_iso = oggi.isoformat()
    aperti = {f for c in irs if c["scadenza"] and c["scadenza"] >= oggi_iso for f in (c["contee"] or [])}
    aperti_evento = {}
    for c in irs:
        if c["scadenza"] and c["scadenza"] >= oggi_iso:
            e = next((e for e in ev if e in c["titolo"].lower() and dom_evento.get(e)), None)
            for f in (c["contee"] or []) if e else []:
                aperti_evento.setdefault(f, dom_evento[e])
    nominati = {f for c in irs for f in (c["contee"] or [])}
    candidati = sorted(f for f, A in aree.items() if f in nominati or any(d[1] for d in A["d"]))
    risultato, prove = {}, {}
    for fips in candidati:
        A = aree[fips]
        qs = [f"{A['nome'].lower()} fema", f"{A['nome'].lower()} disaster"]
        hit = ha_domanda(A["nome"], A["st"], [ac(q) for q in qs], ripetuti)
        prove[fips] = hit
        if hit:
            risultato[fips] = ["contea", hit]
        elif fips in aperti_evento:
            risultato[fips] = ["irs-evento", aperti_evento[fips]]
        elif fips in aperti and dom_irs.get(A["st"]):
            risultato[fips] = ["irs-stato", dom_irs[A["st"]]]
        elif any(d[1] for d in A["d"]) and dom_fema.get(A["st"]):
            risultato[fips] = ["fema-ia-stato", dom_fema[A["st"]]]
    D = {"_nota": "Google Autocomplete (client=firefox, gl=us, hl=en), letto da raccolta/disastri.py. 'query': suggerimenti per query con la "
                  "data di lettura (riusati per 28 giorni). 'pagine': contee con una pagina e il motivo.",
         "regola": "Pagina di contea se c'è una dichiarazione negli ultimi 24 mesi (FEMA, o di Stato citata dall'IRS) E domanda: "
                   "(contea) '<contea> fema' o '<contea> disaster' suggerisce il nome della contea con fema/irs/disaster declaration|relief|assistance...; "
                   "per nomi presenti in più Stati serve anche lo Stato nel suggerimento; i suggerimenti sulle mappe ('flood map', 'flood zone') non contano; oppure (irs-evento) contea in un comunicato IRS con scadenza futura per un evento con nome che ha domanda ('<evento> irs' suggerisce irs/tax); oppure (irs-stato) contea in un comunicato IRS con "
                   "scadenza futura e domanda IRS per lo Stato ('irs tax extension <stato> hurricane|storm', 'irs disaster relief <stato>'); "
                   "oppure (fema-ia-stato) assistenza individuale FEMA nella contea e domanda 'fema disaster declaration <stato>'.",
         "generali": generali, "eventi": ev, "stati": query_stati,
         "eventi_domanda_irs": dom_evento, "stati_domanda_irs": dom_irs, "stati_domanda_fema": dom_fema,
         "contee_suggerimento": prove, "pagine": risultato, "query": dict(sorted(cache.items()))}
    file_dom.write_text(json.dumps(D, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    return risultato


# ---------------------------------------------------------------- principale
def main():
    oggi = date.today()
    try:
        da = oggi.replace(year=oggi.year - MESI_FINESTRA // 12)
    except ValueError:  # 29 febbraio
        da = oggi.replace(year=oggi.year - MESI_FINESTRA // 12, day=28)
    census = contee_census()
    print(f"FEMA: dichiarazioni dal {da} ...")
    letto_alle = datetime.now(timezone.utc).strftime("%H:%M")  # ora della lettura OpenFEMA (i termini chiedono data e, se possibile, ora)
    righe, meta_fema = fema(da.isoformat())
    dich, aree, speciali = elabora_fema(righe, census)
    print(f"  {len(righe)} righe, {len(dich)} dichiarazioni, {len(aree)} contee, {sum(len(v) for v in speciali.values())} aree speciali (tribù, Stato intero)")
    print("IRS: indice ...")
    voci, peso = indice_irs({oggi.year, oggi.year - 1})
    irs = []
    for v in voci:
        try:
            c = comunicato(v, census, aree)
        except Exception as e:
            print(f"  IRS non letto {v['codice']}: {e}", file=sys.stderr)
            continue
        irs.append(c)
        time.sleep(0.8)
    # contee citate dall'IRS ma senza righe FEMA (relief dopo una dichiarazione dello Stato): aggiunte senza dichiarazioni FEMA
    for c in irs:
        for f in c["contee"] or []:
            if f not in aree:
                aree[f] = {"st": c["st"], "nome": census[f][1], "fema": None, "d": []}
    # quante contee IRS hanno l'assistenza individuale FEMA (informativo: l'IRS può seguire anche una dichiarazione dello Stato)
    for c in irs:
        if c["contee"]:
            ih = {f for f in c["contee"] if any(d[1] for d in aree.get(f, {}).get("d", []))}
            c["contee_con_ih_fema"] = len(ih)
    aperti = [c for c in irs if c["scadenza"] and c["scadenza"] >= oggi.isoformat()]
    print(f"  {len(irs)} comunicati letti, {len(aperti)} con scadenza da oggi in poi, "
          f"{sum(1 for c in irs if c['contee'])} con l'elenco delle contee collegato")
    for c in irs:
        if not c["contee"]:
            print(f"   - {c['codice']}: senza contee ({c['motivo_senza_contee']})")
        elif c.get("nomi_non_trovati"):
            print(f"   - {c['codice']}: {len(c['contee'])} contee collegate, nomi non trovati nel Census: {c['nomi_non_trovati']}")
    dom = domanda(aree, irs, oggi, "--senza-domanda" in sys.argv, census)
    for fips, d in dom.items():
        aree[fips]["pagina"] = d
    out = {"_nota": "Generato da raccolta/disastri.py. Date ISO. aree[fips].d = [dichiarazione, IH, IA, PA, HM] (1 = programma dichiarato per quella contea).",
           "letto_il": oggi.isoformat(), "letto_alle_utc": letto_alle, "finestra_da": da.isoformat(),
           "fonti": {"fema": meta_fema, "irs": {"indice": IRS_INDICE, "peso_indice": peso, "comunicati_letti": len(irs)}},
           "dichiarazioni": dict(sorted(dich.items())), "aree": dict(sorted(aree.items())), "aree_speciali": dict(sorted(speciali.items())),
           "irs": sorted(irs, key=lambda c: (c["pubblicato"] or "", c["codice"]), reverse=True)}
    corpo = json.dumps(out, ensure_ascii=False, sort_keys=True)
    out["impronta"] = hashlib.sha256(corpo.encode("utf-8")).hexdigest()
    (DATI / "disastri.json").write_text(json.dumps(out, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    motivi = {}
    for m in dom.values():
        motivi[m[0]] = motivi.get(m[0], 0) + 1
    print(f"Scritto dati/disastri.json (impronta {out['impronta'][:12]}); contee con pagina: {len(dom)} {motivi}")


if __name__ == "__main__":
    main()
