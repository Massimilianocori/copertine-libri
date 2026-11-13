"""Sezione "per diem" di Military Pay Chart: diarie federali GSA per località (CONUS, FY2026 e FY2027), calcolatore del viaggio
e pagina delle tariffe chilometriche IRS e GSA. Chiamata da genera.py (genera(G), dove G è il modulo genera).

Dati: dati/perdiem.json (scritto da raccolta/perdiem.py dai file grezzi in dati/grezzi/). Prima di scrivere qualsiasi pagina
`controlla(G)` rilegge i file grezzi (impronte, conteggi, ogni valore dell'xlsx contro il JSON e contro l'API GSA).
Pagine:
  /per-diem/                         indice: ricerca per Stato e città, tariffa standard, come funziona (frasi GSA), tabella M&IE
  /per-diem/<stato>/                 una per Stato (48 + DC): tutte le località, FY2027 e FY2026 mese per mese
  /per-diem/<stato>/<località>/      solo per le località con domanda misurata (≥ SOGLIA ricerche al mese, dati/domanda_perdiem.json)
  /per-diem/calculator/              calcolatore: località + date -> alloggio massimo + M&IE con il 75 % al primo e all'ultimo giorno
  /irs-mileage-rate/                 tariffe IRS 2026 (due periodi) e GSA per i viaggi ufficiali, calcolatore delle miglia
FAQ solo da ricerche misurate; JSON-LD = FAQ visibili (faq_blocco di genera.py).
"""
import hashlib
import importlib.util
import json
import math
from datetime import date, timedelta

SOGLIA = 300  # ricerche al mese misurate per avere una pagina di località
MAX_GIORNI = 183

# località con pagina propria: (Stato, slug GSA, ricerca misurata, nome mostrato). genera() controlla volume(ricerca) >= SOGLIA.
LOC_PAGINE = [
    ("DC", "district-of-columbia", "per diem rates washington dc", "Washington, DC"),
    ("CA", "san-diego", "per diem rates san diego", "San Diego"),
    ("CA", "san-francisco", "per diem san francisco", "San Francisco"),
    ("NY", "new-york-city", "per diem rates new york city", "New York City"),
    ("NV", "las-vegas", "per diem las vegas", "Las Vegas"),
    ("IL", "chicago", "chicago per diem", "Chicago"),
    ("CO", "denver-aurora", "per diem rates denver", "Denver"),
    ("FL", "orlando", "per diem rates orlando", "Orlando"),
    ("GA", "atlanta", "atlanta per diem", "Atlanta"),
    ("MA", "boston-cambridge", "boston per diem", "Boston"),
    ("WA", "seattle", "seattle per diem", "Seattle"),
    ("TX", "san-antonio", "san antonio per diem", "San Antonio"),
    ("CA", "los-angeles", "los angeles per diem", "Los Angeles"),
    ("LA", "new-orleans", "new orleans per diem", "New Orleans"),
    ("AZ", "phoenix-scottsdale", "phoenix per diem", "Phoenix"),
    ("TN", "nashville", "per diem nashville tn", "Nashville"),
    ("PA", "philadelphia", "philadelphia per diem", "Philadelphia"),
    ("FL", "miami", "miami per diem", "Miami"),
    ("CO", "colorado-springs", "colorado springs per diem", "Colorado Springs"),
    ("SC", "charleston", "charleston sc per diem", "Charleston, SC"),
    ("UT", "salt-lake-city", "salt lake city per diem", "Salt Lake City"),
    ("OR", "portland", "portland or per diem", "Portland, OR"),
    ("TX", "dallas", "dallas per diem", "Dallas"),
    ("TX", "houston", "houston per diem", "Houston"),
]
# ricerca misurata per Stato (FAQ della pagina dello Stato solo se il volume è > 0)
STATO_RICERCA = {"CA": "california per diem rates", "TX": "texas per diem rates", "FL": "florida per diem rates", "VA": "virginia per diem rates",
                 "NY": "new york per diem rates", "CO": "colorado per diem rates", "MD": "maryland per diem rates", "WA": "washington state per diem rates",
                 "NC": "north carolina per diem rates", "AZ": "arizona per diem rates", "OH": "ohio per diem rates", "TN": "tennessee per diem rates",
                 "MI": "michigan per diem rates", "UT": "utah per diem rates", "PA": "pennsylvania per diem", "SC": "per diem rates south carolina",
                 "LA": "louisiana per diem rates", "AL": "alabama per diem", "IN": "indiana per diem rates", "MN": "minnesota per diem rates",
                 "OR": "oregon per diem rates", "NM": "new mexico per diem", "OK": "oklahoma per diem", "MA": "massachusetts per diem"}

DISCLAIMER_PD = ("<strong>Independent site, not affiliated with the General Services Administration, the IRS, the Department of Defense or any other federal agency.</strong> "
                 "We show the GSA per diem rates and the mileage rates exactly as published, plus our own arithmetic on them. This is general information, not tax or financial advice. "
                 "Your travel authorization and your agency’s travel or finance office decide what you are actually reimbursed: check with them before you book.")
NOTA_FONTI = ('<p class="small">Rates are copied from the GSA and IRS files and pages listed above; totals, ranges and calculator results are our arithmetic on those figures. '
              'See <a href="/how-we-check/#per-diem-checks">how we check</a>.</p>')

# L'area GSA "District of Columbia" supera i confini: comprende città e contee di Virginia e Maryland (testo GSA qui sotto, uguale in FY2026 e FY2027;
# l'API GSA ripete infatti la riga sotto MD e VA). Le pagine di Maryland e Virginia la mostrano come riga in più: senza, chi va a Bethesda o ad Arlington
# leggerebbe la tariffa standard. controlla() si ferma se GSA cambia la definizione o se un'altra area nomina un altro Stato.
DC_K = "dc/district-of-columbia"
DC_CONTEE = ("Washington DC (also the cities of Alexandria, Falls Church and Fairfax, and the counties of Arlington and Fairfax, in Virginia; "
             "and the counties of Montgomery and Prince George's in Maryland)")
DC_NOME = "Washington, DC area"
DC_PARTI = {"MD": "Montgomery and Prince George’s counties",
            "VA": "the cities of Alexandria, Falls Church and Fairfax and the counties of Arlington and Fairfax"}
DC_OPZIONE = {"MD": "Washington, DC area (Montgomery, Prince George’s)", "VA": "Washington, DC area (Alexandria, Arlington, Fairfax, Falls Church)"}

G = None
PD = None
FYS = ("2027", "2026")  # prima l'anno fiscale in corso


# ---------------------------------------------------------------- utilità
def usd(x):
    return f"${x:,.2f}" if abs(x - round(x)) > 1e-9 else f"${int(round(x)):,}"


def usd2(x):
    return f"${x:,.2f}"


def cents(x):
    return f"{x:g}¢"


def fy_periodo(fy):
    a = int(fy)
    return f"October 1, {a - 1} to September 30, {a}"


def fy_corrente():
    d = date.fromisoformat(PD["letto_il"])
    return str(d.year + 1 if d.month >= 10 else d.year)


def mese_etichetta(fy, i):
    """Indice 0..11 nell'anno fiscale -> 'Oct 2026'."""
    m = PD["mesi_fy"][i]
    anno = int(fy) - 1 if i < 3 else int(fy)
    return f"{m} {anno}"


def nome_stato(st):
    return PD["stati"][st]


def slug_stato(st):
    return nome_stato(st).lower().replace(" ", "-")


def loc(fy, st, sl):
    return next((L for L in PD["fy"][fy]["localita"] if L["stato"] == st and L["slug"] == sl), None)


def std(fy):
    return PD["fy"][fy]["standard"]


def dc_in(fy, st):
    """Riga dell'area di Washington DC per le pagine di Maryland e Virginia (None per gli altri Stati)."""
    return loc(fy, "DC", "district-of-columbia") if st in DC_PARTI else None


def maiuscola(t):
    return t[:1].upper() + t[1:]


def mie_riga(fy, totale):
    return next(m for m in PD["mie_tabella"][fy] if m["totale"] == totale)


def contee_txt(L):
    c = L["contee"]
    if L["stato"] == "DC":
        return c
    return c if any(w in c.lower() for w in ("county", "counties", "city", "parish", "borough", "less the", "including", "afb")) else c + (" counties" if "/" in c else " County")


def range_txt(v):
    lo, hi = min(v), max(v)
    return usd(lo) if lo == hi else f"{usd(lo)} to {usd(hi)}"


def localita_unite():
    """Tutte le località dei due anni, per Stato: chiave stato/slug -> {FY: località}. Gli slug cambiati con le stesse contee (rinomina) si uniscono."""
    tutte = {}
    for fy in FYS:
        for L in PD["fy"][fy]["localita"]:
            tutte.setdefault(f"{L['stato'].lower()}/{L['slug']}", {})[fy] = L
    alias = {}
    solo26 = [k for k, v in tutte.items() if "2027" not in v]
    solo27 = [k for k, v in tutte.items() if "2026" not in v]
    for a in solo26:
        L26 = tutte[a]["2026"]
        cand = [b for b in solo27 if tutte[b]["2027"]["stato"] == L26["stato"] and tutte[b]["2027"]["contee"] == L26["contee"]]
        if len(cand) == 1:
            alias[a] = cand[0]
    for a, b in alias.items():
        tutte[b]["2026"] = tutte.pop(a)["2026"]
    return tutte, alias


# ---------------------------------------------------------------- controlli (prima di scrivere le pagine)
def _modulo_raccolta():
    spec = importlib.util.spec_from_file_location("raccolta_perdiem", G.RADICE / "raccolta" / "perdiem.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def controlla():
    err = []
    R = _modulo_raccolta()
    reg = G._F.get("grezzi", {})
    for nome in R.FILE:
        f = G.DATI / "grezzi" / nome
        if not f.exists():
            err.append(f"manca il file grezzo {nome}")
            continue
        if reg.get(nome, {}).get("sha256") != hashlib.sha256(f.read_bytes()).hexdigest():
            err.append(f"{nome}: impronta diversa da fonti.json")
        if reg.get(nome, {}).get("url") != R.FILE[nome]:
            err.append(f"{nome}: URL diverso da fonti.json")
    n_val = 0
    for fy in ("2026", "2027"):
        x = R.leggi_xlsx(fy, G.DATI / "grezzi" / f"gsa_fy{fy}.xlsx")
        for L in x["localita"]:
            L["slug"] = R.slug(L["nome"])
        if x != PD["fy"][fy]:
            err.append(f"FY{fy}: dati/perdiem.json diverso dal file grezzo riletto")
        a = R.ATTESI[fy]
        if x["righe"] != a["righe"] or len(x["localita"]) != a["localita"]:
            err.append(f"FY{fy}: {x['righe']} righe, {len(x['localita'])} località (attese {a})")
        api = json.loads((G.DATI / "grezzi" / f"gsa_api_lodging_{fy}.json").read_text())
        diff, extra, n_std, n_nsa = R.confronta_api(fy, x, api)
        if diff or n_std != 48 or n_nsa != len(x["localita"]) + 2 or sorted(extra) != ["MD District of Columbia", "VA District of Columbia"]:
            err.append(f"FY{fy}: xlsx ≠ API ({diff[:3]}, {n_std} standard, {n_nsa} località, solo API {extra})")
        mie_api = R.leggi_mie(json.loads((G.DATI / "grezzi" / f"gsa_api_mie_{fy}.json").read_text()))
        if mie_api != PD["mie_tabella"][fy]:
            err.append(f"FY{fy}: tabella M&IE diversa dall'API")
        livelli = {m["totale"] for m in mie_api}
        for m in mie_api:
            if abs(m["colazione"] + m["pranzo"] + m["cena"] + m["extra"] - m["totale"]) > 1e-9 or abs(m["primo_ultimo"] - 0.75 * m["totale"]) > 1e-9:
                err.append(f"FY{fy}: riga M&IE incoerente {m}")
        s = x["standard"]
        if s["mie"] not in livelli:
            err.append(f"FY{fy}: M&IE standard {s['mie']} fuori dai livelli")
        for L in x["localita"]:
            if L["stato"] not in PD["stati"]:
                err.append(f"FY{fy} {L['nome']}: Stato {L['stato']} fuori dagli Stati CONUS")
            if L["mie"] not in livelli:
                err.append(f"FY{fy} {L['nome']}: M&IE {L['mie']} fuori dai livelli {sorted(livelli)}")
            for v in L["mesi"]:
                n_val += 1
                if not (s["alloggio"] <= v <= 1000):
                    err.append(f"FY{fy} {L['nome']}: alloggio {v} fuori scala (standard {s['alloggio']})")
            n_val += 1
    for fy in ("2026", "2027"):
        dc = loc(fy, "DC", "district-of-columbia")
        if not dc or dc["contee"].replace("’", "'") != DC_CONTEE:
            err.append(f"FY{fy}: la definizione GSA dell'area di Washington DC è cambiata: rivedere DC_CONTEE, DC_PARTI e le pagine di Maryland e Virginia")
        for L in PD["fy"][fy]["localita"]:
            if L["stato"] != "DC" and any(f" in {n}" in L["contee"] for s2, n in PD["stati"].items() if s2 != L["stato"]):
                err.append(f"FY{fy} {L['stato']} {L['nome']}: l'area nomina un altro Stato ({L['contee']}): va mostrata anche nella pagina di quello Stato")
    if PD["mie_tabella"]["2026"] != PD["mie_tabella"]["2027"]:
        err.append("tabella M&IE diversa tra FY2026 e FY2027: le pagine dicono che è la stessa")
    if R.leggi_chilometri() != PD["chilometri"]:
        err.append("tariffe chilometriche diverse dai file grezzi riletti")
    # le frasi delle fonti (GSA, IRS) devono essere state ritrovate
    for fid in ("gsa_api", "gsa_pd", "gsa_faq", "gsa_mie", "gsa_mileage", "irs_n2026_10", "irs_a2026_11", "irs_smr", "irs_ir2025_128", "gsa_xlsx2026", "gsa_xlsx2027"):
        es = G.ESITI.get(fid, {})
        if es.get("http") != 200 or not all(es.get("trovate", {}).values()):
            err.append(f"fonte {fid}: HTTP {es.get('http')} o frase mancante")
    for nome, fid in (("gsa_fy2026.xlsx", "gsa_xlsx2026"), ("gsa_fy2027.xlsx", "gsa_xlsx2027"), ("irs_notice_2026-10.pdf", "irs_n2026_10")):
        if G.ESITI.get(fid, {}).get("sha256") != reg.get(nome, {}).get("sha256"):
            err.append(f"{nome}: il file riletto da fonti.py ({fid}) non è quello in dati/grezzi")
    # pagine di località: solo con domanda misurata e località esistente nel FY in corso
    for st, sl, ric, _ in LOC_PAGINE:
        if G.volume(ric) < SOGLIA:
            err.append(f"pagina {st}/{sl}: ricerca «{ric}» sotto {SOGLIA} al mese ({G.volume(ric)})")
        if not loc("2027", st, sl) or not loc("2026", st, sl):
            err.append(f"pagina {st}/{sl}: località assente in FY2026 o FY2027")
    if err:
        raise SystemExit("ERRORI NEI DATI PER DIEM:\n - " + "\n - ".join(err))
    return {"valori": n_val, "localita_2026": len(PD["fy"]["2026"]["localita"]), "localita_2027": len(PD["fy"]["2027"]["localita"])}


# ---------------------------------------------------------------- calcolo (copia Python di stile.APP_JS viaggio e miglia)
def dati_calcolo(chiavi=None):
    tutte, _ = localita_unite()
    out = {"fy": {}, "nomi": {"std": "Standard CONUS rate (any place not listed)"}, "pagine": {}}
    for fy in ("2026", "2027"):
        s = std(fy)
        F = {"std": [[s["alloggio"]] * 12, s["mie"]], "loc": {}}
        for k, per in tutte.items():
            if chiavi is not None and k not in chiavi:
                continue
            if fy in per:
                F["loc"][k] = [per[fy]["mesi"], per[fy]["mie"]]
        out["fy"][fy] = F
    for k, per in tutte.items():
        if chiavi is not None and k not in chiavi:
            continue
        L = per.get("2027") or per["2026"]
        out["nomi"][k] = f"{L['nome']}, {L['stato']}"
        out["pagine"][k] = pagina_di(k)
    out["pagine"]["std"] = "per-diem/"
    return out


def viaggio(D, k, da, a):
    try:
        x, y = date.fromisoformat(da), date.fromisoformat(a)
    except (TypeError, ValueError):
        return {"errore": "data"}
    if y < x:
        return {"errore": "ordine"}
    n = (y - x).days + 1
    if n > MAX_GIORNI:
        return {"errore": "lungo"}
    righe, tl, tm = [], 0, 0
    for i in range(n):
        d = x + timedelta(days=i)
        fy = str(d.year + 1 if d.month >= 10 else d.year)
        F = D["fy"].get(fy)
        if F is None:
            return {"errore": "fuori", "data": d.isoformat()}
        r = F["std"] if k == "std" else F["loc"].get(k)
        if r is None:
            return {"errore": "non_listata", "fy": fy, "data": d.isoformat()}
        q = 0.75 if (i == 0 or i == n - 1) else 1
        m = r[1] * q
        lo = r[0][(d.month + 2) % 12] if i < n - 1 else 0
        righe.append({"data": d.isoformat(), "fy": fy, "alloggio": lo, "mie": m, "quota": q})
        tl += lo
        tm += m
    return {"giorni": n, "notti": n - 1, "alloggio": tl, "mie": tm, "totale": tl + tm, "righe": righe}


def dati_miglia():
    km = PD["chilometri"]
    irs, pov = km["irs"], km["gsa_pov"]
    per = []
    for i in range(2):
        per.append({"dal": irs[i]["dal"], "al": irs[i]["al"],
                    "tariffe": {"business": round(irs[i]["business"] * 10), "medical": round(irs[i]["medical_moving"] * 10), "charity": round(irs[i]["charity"] * 10),
                                "gsa_auto": round(pov[i]["auto"] * 1000), "gsa_auto_gov": round(pov[i]["auto_gov_disponibile"] * 1000)}})
    return {"periodi": per}


def miglia(D, giorno, scopo, mi):
    """Tariffe in decimi di centesimo; miglia arrotondate al decimo; importo al centesimo (metà in su). Tutto in interi."""
    try:
        d = date.fromisoformat(giorno)
        mi = float(mi)
    except (TypeError, ValueError):
        return {"errore": "dati"}
    if not (0 < mi <= 100000) or math.isnan(mi):
        return {"errore": "miglia"}
    p = next((p for p in D["periodi"] if date.fromisoformat(p["dal"]) <= d <= date.fromisoformat(p["al"])), None)
    if p is None:
        return {"errore": "fuori"}
    r = p["tariffe"].get(scopo)
    if r is None:
        return {"errore": "scopo"}
    t = math.floor(mi * 10 + 0.5)
    c = (t * r + 50) // 100
    return {"tariffa": r / 10, "decimi": t, "centesimi": c, "importo": c / 100, "dal": p["dal"], "al": p["al"]}


# ---------------------------------------------------------------- percorsi
PAGINE_LOC = {}  # chiave "ca/san-diego" -> percorso


def pagina_di(k):
    if k in PAGINE_LOC:
        return PAGINE_LOC[k]
    st, sl = k.split("/")
    fy = fy_corrente()
    return f"per-diem/{slug_stato(st.upper())}/#{sl}" + ("" if loc(fy, st.upper(), sl) else f"-{int(fy) - 1}")


# ---------------------------------------------------------------- pezzi di pagina
def stagioni_txt(fy, L):
    """'$342 Oct–Dec, $179 Jan–Feb …' dai mesi (solo se la tariffa cambia)."""
    m = L["mesi"]
    if len(set(m)) == 1:
        return f"{usd(m[0])} all year"
    parti, i = [], 0
    while i < 12:
        j = i
        while j + 1 < 12 and m[j + 1] == m[i]:
            j += 1
        a, b = PD["mesi_fy"][i], PD["mesi_fy"][j]
        parti.append(f"{usd(m[i])} {a}" + (f"–{b}" if j > i else ""))
        i = j + 1
    return ", ".join(parti)


def tabella_stato(fy, st, rim, fonte):
    locs = [L for L in PD["fy"][fy]["localita"] if L["stato"] == st]
    s = std(fy)
    th = "".join(f'<th scope="col" class="n">{h(PD["mesi_fy"][i])}</th>' for i in range(12))
    righe = [f'<tr><th scope="row">Standard rate</th><td>All places not listed below</td><td class="n">{usd(s["mie"])}</td>'
             + "".join(f'<td class="n">{usd(s["alloggio"])}</td>' for _ in range(12)) + "</tr>"]
    for L in locs:
        k = f"{st.lower()}/{L['slug']}"
        nome = h(L["nome"])
        if k in PAGINE_LOC:
            nome = f'<a href="/{PAGINE_LOC[k]}">{nome}</a>'
        righe.append(f'<tr id="{h(L["slug"]) if fy == fy_corrente() else h(L["slug"]) + "-" + fy}"><th scope="row">{nome}</th><td>{h(contee_txt(L))}</td><td class="n">{usd(L["mie"])}</td>'
                     + "".join(f'<td class="n">{usd(v)}</td>' for v in L["mesi"]) + "</tr>")
    dc = dc_in(fy, st)
    if dc:
        righe.append(f'<tr id="washington-dc-area{"" if fy == fy_corrente() else "-" + fy}"><th scope="row"><a href="/{PAGINE_LOC.get(DC_K, "per-diem/district-of-columbia/")}">{h(DC_NOME)}</a></th>'
                     f'<td>{h(maiuscola(DC_PARTI[st]))}</td><td class="n">{usd(dc["mie"])}</td>' + "".join(f'<td class="n">{usd(v)}</td>' for v in dc["mesi"]) + "</tr>")
    cap = (f'{h(nome_stato(st))}, FY {fy} ({fy_periodo(fy)}): maximum lodging rate per night by month and M&amp;IE per day. '
           f'Months run from October {int(fy) - 1} to September {fy}. Source: GSA{rim.ref(fonte)}.')
    return (f'<div class="tab"><table class="dati grande"><caption>{cap}</caption><thead><tr><th scope="col">Destination</th><th scope="col">County or area</th>'
            f'<th scope="col" class="n">M&amp;IE</th>{th}</tr></thead><tbody>{"".join(righe)}</tbody></table></div>')


def tabella_mie(rim, evidenzia=None):
    fy = fy_corrente()
    righe = []
    for m in PD["mie_tabella"][fy]:
        cls = ' class="qui"' if m["totale"] == evidenzia else ""
        righe.append(f'<tr{cls}><th scope="row">{usd(m["totale"])}</th><td class="n">{usd(m["colazione"])}</td><td class="n">{usd(m["pranzo"])}</td><td class="n">{usd(m["cena"])}</td>'
                     f'<td class="n">{usd(m["extra"])}</td><td class="n">{usd2(m["primo_ultimo"])}</td></tr>')
    cap = f'M&amp;IE breakdown for the continental U.S., FY {fy} (the same five rates as FY {int(fy) - 1}). Source: GSA{rim.ref("gsa_mie,gsa_api")}.'
    return (f'<div class="tab"><table class="dati"><caption>{cap}</caption><thead><tr><th scope="col">M&amp;IE total</th><th scope="col" class="n">Breakfast</th>'
            f'<th scope="col" class="n">Lunch</th><th scope="col" class="n">Dinner</th><th scope="col" class="n">Incidentals</th><th scope="col" class="n">First &amp; last day (75%)</th></tr></thead>'
            f'<tbody>{"".join(righe)}</tbody></table></div>')


def opzioni_localita(sel, chiavi=None):
    tutte, _ = localita_unite()
    per_stato = {}
    for k, per in tutte.items():
        if chiavi is not None and k not in chiavi:
            continue
        L = per.get("2027") or per["2026"]
        per_stato.setdefault(L["stato"], []).append((L["nome"], k, "2027" not in per))
    if DC_K in tutte and (chiavi is None or DC_K in chiavi):  # la stessa area anche sotto Maryland e Virginia (stesso valore: stessa tariffa)
        for st, etichetta in DC_OPZIONE.items():
            if chiavi is None or any(k.startswith(st.lower() + "/") for k in chiavi):
                per_stato.setdefault(st, []).append((etichetta, DC_K, False))
    out = f'<option value="std"{" selected" if sel == "std" else ""}>Standard CONUS rate (any place not listed)</option>'
    for st in sorted(per_stato, key=nome_stato):
        voci = "".join(f'<option value="{h(k)}"{" selected" if k == sel and not (k == DC_K and st != "DC") else ""}>{h(n)}{" (FY 2026 only)" if solo26 else ""}</option>'
                       for n, k, solo26 in sorted(per_stato[st]))
        out += f'<optgroup label="{h(nome_stato(st))}">{voci}</optgroup>'
    return out


def calcolatore_pd(sel="std", da="2026-12-07", a="2026-12-10", titolo="Per diem calculator", chiavi=None):
    D = dati_calcolo(chiavi)
    r = viaggio(D, sel, da, a)
    statico = ""
    if "errore" not in r:
        statico = (f'<div class="tot"><div class="main"><span>Maximum per diem for the trip</span><b>{usd2(r["totale"])}</b></div>'
                   f'<div><span>Lodging, {r["notti"]} night{"s" if r["notti"] != 1 else ""} (maximum)</span><b>{usd2(r["alloggio"])}</b></div>'
                   f'<div><span>M&amp;IE, {r["giorni"]} day{"s" if r["giorni"] != 1 else ""}</span><b>{usd2(r["mie"])}</b></div></div>')
    return f"""<section class="card calc" data-pd aria-labelledby="pd-h">
<div class="calc-h"><h2 id="pd-h">{G.ico("calc")}{h(titolo)}</h2></div>
<div class="calc-g">
<form class="calc-in" onsubmit="return false">
<label>Where you stay (GSA area)<select name="l">{opzioni_localita(sel, chiavi)}</select></label>
<div class="due"><label>First day of travel<input type="date" name="da" value="{da}" min="2025-10-01" max="2027-09-30" required></label>
<label>Last day of travel<input type="date" name="a" value="{a}" min="2025-10-01" max="2027-09-30" required></label></div>
<p class="small">Dates from October 1, 2025 to September 30, 2027 (FY 2026 and FY 2027). If your city is not listed, check whether its county is; otherwise the standard rate applies.</p>
</form>
<div class="calc-out" data-out aria-live="polite">{statico}</div>
</div>
<p class="calc-f"><strong>Formula:</strong> lodging = the GSA maximum for the month of each night (one night fewer than travel days); M&amp;IE = 75% of the daily rate on the first and on the last day, 100% on every day in between; total = lodging + M&amp;IE. It runs in your browser.</p>
<script type="application/json" id="dati-pd">{json.dumps(D, separators=(",", ":"))}</script>
</section>"""


def blocco_non_coperto(rim):
    return ('<div class="nota info">' + G.ico("info") + rim.t(
        '<p><strong>What this covers:</strong> the GSA rates for official travel within the continental United States: the 48 contiguous states and the District of Columbia.[[gsa_faq]] '
        '“The U.S. Department of Defense (DOD) establishes rates for travel in non-foreign areas outside of CONUS, which includes Alaska, Hawaii, and U.S. territories and possessions.” '
        'and “The U.S. Department of State establishes rates for travel in foreign areas.”[[gsa_faq]] Those rates are not on this site.</p>'
        '<p><strong>Military travel:</strong> we could not read the Department of Defense’s Joint Travel Regulations: its travel website (travel.dod.mil) answered our check with an error (403). '
        'So this site does not say how per diem works for service members or DoD civilians, and military rates outside the continental U.S. are not covered. Use your orders and your travel office.</p>') + "</div>")


def h(x):
    return G.h(x)


# ---------------------------------------------------------------- pagine
def indice(tutte, alias):
    rim = G.Rimandi()
    fy, fyp = fy_corrente(), str(int(fy_corrente()) - 1)
    s, sp = std(fy), std(fyp)
    locs = PD["fy"][fy]["localita"]
    mie_l = [m["totale"] for m in PD["mie_tabella"][fy]]
    corpo = (f'<section class="card stats pull" aria-label="Key figures">'
             f'<div class="stat main"><b>{usd(s["alloggio"])} + {usd(s["mie"])}</b><span>Standard CONUS rate FY {fy}: lodging + M&amp;IE per day{rim.ref("gsa_xlsx" + fy)}</span></div>'
             f'<div class="stat"><b>{len(locs)}</b><span>Areas with their own rate in FY {fy}{rim.ref("gsa_xlsx" + fy)}</span></div>'
             f'<div class="stat"><b>{usd(min(mie_l))}–{usd(max(mie_l))}</b><span>The five M&amp;IE daily rates{rim.ref("gsa_mie")}</span></div>'
             f'<div class="stat"><b>75%</b><span>M&amp;IE on the first and last day of travel{rim.ref("gsa_faq")}</span></div>'
             f'<p class="asof">FY {fy} runs {fy_periodo(fy)}; FY {fyp} ({usd(sp["alloggio"])} + {usd(sp["mie"])} standard) is here too, for trips and claims before October 1, {fyp}. '
             f'GSA files read on {G.data_lunga(PD["letto_il"])}.</p></section>')
    # ricerca
    voci = []
    for k, per in sorted(tutte.items(), key=lambda kv: ((kv[1].get(fy) or kv[1][fyp])["nome"])):
        L = per.get(fy) or per[fyp]
        t = f"{L['nome']} {L['contee']} {nome_stato(L['stato'])} {L['stato']}".lower()
        extra = "" if fy in per else f" · FY {fyp} only"
        voci.append(f'<li data-t="{h(t)}" hidden><a href="/{pagina_di(k)}"><b>{h(L["nome"])}, {L["stato"]}</b><small>{h(contee_txt(L))}{extra}</small></a></li>')
    corpo += ('<h2 id="search">Find a city or county</h2>'
              '<form class="cerca card" role="search" data-cerca onsubmit="return false"><label for="q">City, county or state</label>'
              '<input id="q" type="search" name="q" autocomplete="off" placeholder="For example San Diego, Cook, Texas">'
              '<p class="small" data-conta aria-live="polite">Type at least two letters. If neither your city nor its county is listed, the standard rate applies.</p></form>'
              f'<ul class="risultati" data-elenco>{"".join(voci)}</ul>')
    # Stati
    stati = sorted(PD["stati"], key=nome_stato)
    griglia = "".join(f'<li><a href="/per-diem/{slug_stato(st)}/"><b>{h(nome_stato(st))}</b><small>{sum(1 for L in locs if L["stato"] == st) or "standard rate only"}'
                      f'{" areas" if sum(1 for L in locs if L["stato"] == st) > 1 else (" area" if sum(1 for L in locs if L["stato"] == st) == 1 else "")}</small></a></li>' for st in stati)
    corpo += f'<h2 id="states">Per diem rates by state</h2><ul class="griglia larga stati">{griglia}</ul>'
    corpo += G.AD
    corpo += ('<div class="azioni"><a class="btn" href="/per-diem/calculator/">' + G.ico("calc") + 'Per diem calculator</a>'
              '<a class="btn sec" href="/irs-mileage-rate/">IRS and GSA mileage rates</a></div>')
    pop = "".join(f'<li><a href="/{PAGINE_LOC[f"{st.lower()}/{sl}"]}"><b>{h(n)}</b><small>{usd(max(loc(fy, st, sl)["mesi"]))} max · {usd(loc(fy, st, sl)["mie"])} M&amp;IE</small></a></li>'
                  for st, sl, _, n in LOC_PAGINE)
    corpo += f'<h2 id="cities">Most searched cities</h2><ul class="griglia larga">{pop}</ul><p class="small">Highest monthly lodging rate in FY {fy} and the daily M&amp;IE.</p>'
    # come funziona
    es = viaggio(dati_calcolo([]), "std", "2026-12-07", "2026-12-10")
    corpo += '<h2 id="how-it-works">How per diem works</h2><div class="testo">' + rim.t(
        '<p>GSA: “Per diem is an allowance for lodging, meals, and incidental expenses.”[[gsa_faq]] It sets “the per diem rates that federal agencies use to reimburse their employees for lodging and meals and incidental expenses '
        'incurred while on official travel within the continental United States.” “A standard rate applies to most of CONUS.” “Individual rates apply to about 300 non-standard areas.”[[gsa_pd]]</p>'
        '<ul><li><strong>Lodging</strong> is a ceiling, not a payment: “The lodging per diem rates are a maximum amount; the traveler only receives actual lodging costs up to that maximum rate.” '
        '“Lodging taxes are not included in the CONUS per diem rate.”[[gsa_faq]] In many areas the ceiling changes with the season, so the tables show it month by month.</li>'
        '<li><strong>M&amp;IE</strong> (meals and incidental expenses) is a daily rate; it “does include taxes and tips”.[[gsa_faq]]</li>'
        '<li><strong>First and last day:</strong> “On the first and last travel day, Federal employees are only eligible for 75 percent of the total M&amp;IE rate for their temporary duty travel location '
        '(not the official duty station location).”[[gsa_faq]]</li>'
        '<li><strong>Which rate applies:</strong> “If the city is not listed, but the county is, then the per diem rate is the rate for that entire county.” '
        '“If neither the city nor county you are looking for is listed on the GSA per diem rate page, then the standard CONUS rate applies.”[[gsa_faq]]</li>'
        '<li><strong>Hotels:</strong> “Hotels are not required to honor the federal per diem rates.”[[gsa_faq]]</li></ul>'
        f'<p><strong>Example (our arithmetic):</strong> four travel days, December 7 to 10, 2026, in a standard-rate area: lodging up to 3 nights × {usd(s["alloggio"])} = {usd2(es["alloggio"])}; '
        f'M&amp;IE {usd2(0.75 * s["mie"])} + {usd(s["mie"])} + {usd(s["mie"])} + {usd2(0.75 * s["mie"])} = {usd2(es["mie"])}; at most {usd2(es["totale"])} in all.</p>') + "</div>"
    corpo += '<h2 id="mie">M&amp;IE breakdown</h2>' + tabella_mie(rim)
    corpo += '<div class="testo">' + rim.t(
        '<p>GSA publishes the breakdown so that travelers know “how much to deduct from your meals and incidental expenses allowance, or M&amp;IE, when a meal is provided by the government or included in a registration fee.” '
        '“Meals provided by a common carrier or complimentary meals provided by a hotel or motel do not affect your per diem allowance.”[[gsa_mie]]</p>') + "</div>"
    corpo += blocco_non_coperto(rim)
    corpo += ('<h2 id="dates">When the rates change</h2><div class="testo">' + rim.t(
        f'<p>Per diem rates follow the federal fiscal year, October 1 to September 30. GSA says “Rates for the coming federal government fiscal year (October 1st to September 30th) are typically announced in mid-August.”[[gsa_api]] '
        f'FY {fy} took effect on October 1, {int(fy) - 1}.[[gsa_xlsx{fy}]] '
        f'Compared with FY {fyp}, {sum(1 for k, p in tutte.items() if fy in p and fyp in p and max(p[fy]["mesi"]) > max(p[fyp]["mesi"]))} areas have a higher top lodging rate, '
        f'{sum(1 for k, p in tutte.items() if fy in p and fyp in p and max(p[fy]["mesi"]) < max(p[fyp]["mesi"]))} a lower one'
        + (f', and {", ".join(tutte_solo(tutte, fyp))} {"is" if len(tutte_solo(tutte, fyp)) == 1 else "are"} no longer listed in FY {fy} (the standard rate applies there unless the county is in another area)' if tutte_solo(tutte, fyp) else "")
        + (f'. GSA renamed {", ".join(h(PD_nome(a, fyp)) + " as " + h(PD_nome(b, fy)) for a, b in alias.items())}' if alias else "")
        + '.</p>') + "</div>")
    voci_faq = [
        ("what is per diem", "What is per diem?",
         "GSA defines per diem as “an allowance for lodging, meals, and incidental expenses”. For official travel in the continental U.S. it has two parts: a maximum lodging rate that depends on the place and the month, and a daily rate for meals and incidental expenses (M&IE).",
         "gsa_faq,gsa_api"),
        ("conus per diem rates", f"What is the standard CONUS per diem rate for FY {fy}?",
         f"{usd(s['alloggio'])} a night for lodging and {usd(s['mie'])} a day for M&IE, from {fy_periodo(fy)}. In FY {fyp} it was {usd(sp['alloggio'])} and {usd(sp['mie'])}. "
         "It applies wherever neither the city nor its county is listed by GSA.", f"gsa_xlsx{fy},gsa_xlsx{fyp},gsa_faq"),
        ("m&ie rates", "What are the M&IE rates?",
         f"In FY {fy} GSA uses five M&IE rates in the continental U.S.: " + ", ".join(usd(x) for x in mie_l[:-1]) + f" and {usd(mie_l[-1])} a day, the same as in FY {fyp}. "
         "Each area has one of them all year; the standard rate is " + usd(s["mie"]) + ".", "gsa_mie,gsa_api"),
        ("per diem first and last day", "How much M&IE do you get on the first and last day of travel?",
         f"75 percent of the M&IE rate of the place you travel to. GSA’s table gives {usd2(PD['mie_tabella'][fy][0]['primo_ultimo'])} for the {usd(mie_l[0])} rate and "
         f"{usd2(PD['mie_tabella'][fy][-1]['primo_ultimo'])} for the {usd(mie_l[-1])} rate.", "gsa_faq,gsa_mie"),
        ("how is per diem calculated", "How is per diem calculated for a trip?",
         "Lodging: what you actually pay each night, up to the GSA maximum for that place and month (taxes are claimed separately). M&IE: the full daily rate for each day between the first and the last day, "
         "and 75 percent on the first and on the last day.", "gsa_faq"),
        ("oconus per diem rates", "Does this cover OCONUS, Alaska, Hawaii or foreign per diem rates?",
         "No. GSA sets rates for the 48 contiguous states and the District of Columbia. The Department of Defense sets rates for Alaska, Hawaii and U.S. territories, and the Department of State for foreign areas; they are not on this site.",
         "gsa_faq"),
        ("gsa lodging rates", "Are lodging taxes included in the GSA lodging rate?",
         "No. GSA: “Lodging taxes are not included in the CONUS per diem rate.” The M&IE rate, on the other hand, includes taxes and tips on meals.", "gsa_faq"),
    ]
    fh, fld = G.faq_blocco(voci_faq, rim)
    corpo += fh + rim.elenco(NOTA_FONTI)
    testata = G.banda(f"GSA rates · FY {fy} and FY {fyp}", f"Per Diem Rates FY {fy} by State and City",
                      f"Federal per diem for travel in the continental U.S.: the maximum lodging rate by month and the daily M&amp;IE for every GSA area, from the official GSA files.", icona="cal")
    G.pagina("per-diem/", f"GSA Per Diem Rates FY {fy} and FY {fyp} by State and City",
             f"GSA per diem rates FY {fy} and FY {fyp}: lodging by month and M&IE for every state and GSA area in the continental U.S., the standard rate and a calculator.",
             corpo, testata, briciole=[("Home", ""), ("Per diem", "per-diem/")], jsonld=[fld], disclaimer=DISCLAIMER_PD)


def tutte_solo(tutte, fy):
    return [h(p[fy]["nome"]) + f", {p[fy]['stato']}" for k, p in tutte.items() if list(p) == [fy]]


def PD_nome(k, fy):
    st, sl = k.split("/")
    return next(L["nome"] for L in PD["fy"][fy]["localita"] if L["stato"] == st.upper() and L["slug"] == sl)


def pagina_stato(st):
    rim = G.Rimandi()
    fy, fyp = fy_corrente(), str(int(fy_corrente()) - 1)
    nome = nome_stato(st)
    locs, locsp = [L for L in PD["fy"][fy]["localita"] if L["stato"] == st], [L for L in PD["fy"][fyp]["localita"] if L["stato"] == st]
    s = std(fy)
    dc = dc_in(fy, st)  # Maryland e Virginia: parte dello Stato è nell'area GSA di Washington DC
    if locs:
        top = max(locs + ([dc] if dc else []), key=lambda L: max(L["mesi"]))
        corpo = (f'<section class="card stats pull" aria-label="Key figures">'
                 f'<div class="stat main"><b>{len(locs)}</b><span>Area{"s" if len(locs) > 1 else ""} with {"their" if len(locs) > 1 else "its"} own rate in FY {fy}'
                 f'{", plus part of the Washington, DC area" if dc else ""}{rim.ref("gsa_xlsx" + fy)}</span></div>'
                 f'<div class="stat"><b>{usd(s["alloggio"])} + {usd(s["mie"])}</b><span>Standard rate elsewhere in {h(nome)}: lodging + M&amp;IE</span></div>'
                 f'<div class="stat"><b>{usd(max(top["mesi"]))}</b><span>Highest lodging rate: {h(DC_NOME if top is dc else top["nome"])}</span></div>'
                 f'<div class="stat"><b>{range_txt([L["mie"] for L in locs] + [s["mie"]] + ([dc["mie"]] if dc else []))}</b><span>M&amp;IE per day in {h(nome)}</span></div>'
                 f'<p class="asof">FY {fy}: {fy_periodo(fy)}. FY {fyp} table below for earlier trips. GSA files read on {G.data_lunga(PD["letto_il"])}.</p></section>')
    else:
        corpo = (f'<section class="card stats pull" aria-label="Key figures">'
                 f'<div class="stat main"><b>{usd(s["alloggio"])}</b><span>Lodging per night, FY {fy}: standard rate everywhere in {h(nome)}{rim.ref("gsa_xlsx" + fy)}</span></div>'
                 f'<div class="stat"><b>{usd(s["mie"])}</b><span>M&amp;IE per day</span></div>'
                 f'<div class="stat"><b>{usd2(s["mie"] * 0.75)}</b><span>M&amp;IE on the first and last day (75%)</span></div>'
                 f'<div class="stat"><b>{usd(std(fyp)["alloggio"])} + {usd(std(fyp)["mie"])}</b><span>FY {fyp} standard rate</span></div>'
                 f'<p class="asof">GSA lists no area in {h(nome)} with its own rate in FY {fy} or FY {fyp}. GSA files read on {G.data_lunga(PD["letto_il"])}.</p></section>')
    corpo += '<div class="testo" style="margin-top:22px">' + rim.t(
        f'<p>{"Places in " + h(nome) + " not listed below" if locs else "Every place in " + h(nome)} {"get" if locs else "gets"} the standard CONUS rate. '
        'GSA: “If the city is not listed, but the county is, then the per diem rate is the rate for that entire county.”[[gsa_faq]] '
        'Lodging is a maximum per night (taxes are not included); M&amp;IE is per day, 75 percent on the first and last day of travel.[[gsa_faq]]</p>'
        + (f'<p><strong>Washington, DC area:</strong> GSA’s District of Columbia area also takes in the cities of Alexandria, Falls Church and Fairfax and the counties of Arlington and Fairfax in Virginia, '
           f'and the counties of Montgomery and Prince George’s in Maryland.[[gsa_xlsx{fy}]] In {h(nome)}, {DC_PARTI[st]} get the <a href="/{PAGINE_LOC.get(DC_K, "per-diem/district-of-columbia/")}">Washington, DC rate</a> '
           f'({range_txt(dc["mesi"])} a night for lodging depending on the month and {usd(dc["mie"])} for M&amp;IE in FY {fy}), not the standard rate. It is the last row of each table below.</p>' if dc else "")
        + ('<p>These are the federal rates GSA sets for official travel by federal employees.[[gsa_faq]] Travel rules for ' + h(nome) + ' state government employees are set by the state and are not covered here.</p>' if st != "DC" else "")) + "</div>"
    pagine_qui = [(sl, n) for s2, sl, _, n in LOC_PAGINE if s2 == st]
    if pagine_qui:
        corpo += '<div class="azioni">' + "".join(f'<a class="btn sec" href="/per-diem/{slug_stato(st)}/{sl}/">{h(n)} rates by month</a>' for sl, n in pagine_qui) + "</div>"
    corpo += f'<h2 id="fy{fy}">{h(nome)} per diem rates FY {fy}</h2>' + tabella_stato(fy, st, rim, f"gsa_xlsx{fy}")
    if locs:
        corpo += '<p class="small">On a phone, swipe the table sideways. Months are the lodging maximum per night; M&amp;IE is per day.</p>'
    corpo += G.AD
    corpo += f'<h2 id="fy{fyp}">{h(nome)} per diem rates FY {fyp}</h2>' + tabella_stato(fyp, st, rim, f"gsa_xlsx{fyp}")
    nuovi = [L["nome"] for L in locs if not any(x["slug"] == L["slug"] for x in locsp)]
    tolti = [L["nome"] for L in locsp if not any(x["slug"] == L["slug"] for x in locs)]
    if nuovi or tolti:
        corpo += ('<p class="small">' + (f'Listed in FY {fy} but not in FY {fyp}: {h(", ".join(nuovi))}. ' if nuovi else "")
                  + (f'Listed in FY {fyp} but not in FY {fy}: {h(", ".join(tolti))}.' if tolti else "") + "</p>")
    corpo += '<h2 id="calculator">Work out a trip</h2>' + calcolatore_pd(sel=(f"{st.lower()}/{locs[0]['slug']}" if locs else "std"),
                                                                           titolo=f"Per diem calculator: {nome}", chiavi=[f"{st.lower()}/{L['slug']}" for L in locs + locsp] + ([DC_K] if dc else []))
    corpo += '<h2 id="mie">M&amp;IE breakdown</h2>' + tabella_mie(rim)
    ric = STATO_RICERCA.get(st)
    voci = []
    if ric and G.volume(ric) > 0:
        if locs:
            tutti_l = [v for L in locs for v in L["mesi"]]
            a = (f"In FY {fy} ({fy_periodo(fy)}) GSA lists {len(locs)} area{'s' if len(locs) > 1 else ''} in {nome} with {'their' if len(locs) > 1 else 'its'} own rate: maximum lodging "
                 f"from {usd(min(tutti_l))} to {usd(max(tutti_l))} a night depending on place and month, and M&IE of {range_txt([L['mie'] for L in locs])} a day. "
                 + (f"{maiuscola(DC_PARTI[st])} are part of GSA’s Washington, DC area: lodging from {usd(min(dc['mesi']))} to {usd(max(dc['mesi']))} a night and M&IE of {usd(dc['mie'])} a day. " if dc else "")
                 + f"Everywhere else in {nome} the standard rate applies: {usd(s['alloggio'])} for lodging and {usd(s['mie'])} for M&IE. These are federal travel rates, not {nome}’s own rates for state employees.")
        else:
            a = f"The standard rate everywhere: {usd(s['alloggio'])} a night for lodging and {usd(s['mie'])} a day for M&IE in FY {fy}. These are federal travel rates, not {nome}’s own rates for state employees."
        voci.append((ric, f"What is the per diem rate in {nome}?", a, f"gsa_xlsx{fy},gsa_faq"))
    fh, fld = G.faq_blocco(voci, rim)
    corpo += fh
    corpo += f'<h2>Other states</h2><ul class="griglia larga stati">' + "".join(
        f'<li><a href="/per-diem/{slug_stato(x)}/"><b>{h(nome_stato(x))}</b></a></li>' for x in sorted(PD["stati"], key=nome_stato) if x != st) + "</ul>"
    corpo += rim.elenco(NOTA_FONTI)
    if locs:
        sub = (f"Maximum lodging by month and daily M&amp;IE for the {len(locs)} GSA area{'s' if len(locs) > 1 else ''} in {h(nome)}{' and the part of the state in the Washington, DC area' if dc else ''}, plus the standard rate of "
               f"<strong>{usd(s['alloggio'])} + {usd(s['mie'])}</strong> everywhere else. FY {fy} and FY {fyp}.")
    else:
        sub = f"GSA lists no separate areas in {h(nome)}: the standard rate of <strong>{usd(s['alloggio'])}</strong> lodging and <strong>{usd(s['mie'])}</strong> M&amp;IE applies everywhere in FY {fy}."
    testata = G.banda(f"Per diem · {nome}", f"{nome} Per Diem Rates FY {fy}", sub, corta=False, icona="cal")
    titolo = f"{nome} Per Diem Rates FY {fy} & {fyp} (GSA)"
    descr = (f"{nome} per diem rates FY {fy} and FY {fyp}: GSA lodging maximum by month and M&IE for {len(locs)} area{'s' if len(locs) != 1 else ''}{', the Washington DC area' if dc else ''} and the standard rate{'' if dc else ', with a trip calculator'}."
             if locs else f"{nome} per diem rates FY {fy} and FY {fyp}: the GSA standard rate of ${s['alloggio']} lodging and ${s['mie']} M&IE applies everywhere in the state.")
    G.pagina(f"per-diem/{slug_stato(st)}/", titolo, descr, corpo, testata, briciole=[("Home", ""), ("Per diem", "per-diem/"), (nome, f"per-diem/{slug_stato(st)}/")],
             jsonld=[fld] if fld else None, disclaimer=DISCLAIMER_PD)


def pagina_localita(st, sl, ric, disp):
    rim = G.Rimandi()
    fy, fyp = fy_corrente(), str(int(fy_corrente()) - 1)
    L, Lp = loc(fy, st, sl), loc(fyp, st, sl)
    k = f"{st.lower()}/{sl}"
    nome_st = nome_stato(st)
    mr = mie_riga(fy, L["mie"])
    corpo = (f'<section class="card stats pull" aria-label="Key figures">'
             f'<div class="stat main"><b>{range_txt(L["mesi"])}</b><span>Lodging maximum per night, FY {fy}{rim.ref("gsa_xlsx" + fy)}</span></div>'
             f'<div class="stat"><b>{usd(L["mie"])}</b><span>M&amp;IE per day{rim.ref("gsa_xlsx" + fy)}</span></div>'
             f'<div class="stat"><b>{usd2(mr["primo_ultimo"])}</b><span>M&amp;IE on the first and last day (75%){rim.ref("gsa_mie")}</span></div>'
             f'<div class="stat"><b>{usd(max(L["mesi"]) + L["mie"])}</b><span>Highest full day: lodging + M&amp;IE (our arithmetic)</span></div>'
             f'<p class="asof">FY {fy}: {fy_periodo(fy)}. Area defined by GSA as {h(contee_txt(L))}. GSA files read on {G.data_lunga(PD["letto_il"])}.</p></section>')
    corpo += '<div class="testo" style="margin-top:22px">' + rim.t(
        f'<p>{h(disp)} is a GSA non-standard area called <strong>{h(L["nome"])}</strong>, covering {h(contee_txt(L))}. '
        f'In FY {fy} the lodging maximum is {stagioni_txt(fy, L)}; M&amp;IE is {usd(L["mie"])} a day all year.[[gsa_xlsx{fy}]] '
        'Places outside the listed area get the rate of their own county, or the standard rate if the county is not listed.[[gsa_faq]]</p>') + "</div>"
    righe = []
    for i in range(12):
        a, b = L["mesi"][i], Lp["mesi"][i]
        diff = "–" if a == b else (f"+{usd(a - b)}" if a > b else f"−{usd(b - a)}")
        righe.append(f'<tr><th scope="row">{PD["mesi_fy"][i]}</th><td class="n">{usd(a)}</td><td class="n">{usd(b)}</td><td class="n">{diff}</td></tr>')
    cap = (f'{h(L["nome"])} ({h(nome_st)}): maximum lodging rate per night by month. FY {fy} = {mese_etichetta(fy, 0)} to {mese_etichetta(fy, 11)}; FY {fyp} = {mese_etichetta(fyp, 0)} to {mese_etichetta(fyp, 11)}. '
           f'Source: GSA{rim.ref(f"gsa_xlsx{fy},gsa_xlsx{fyp}")}. Change: our arithmetic.')
    corpo += (f'<h2 id="by-month">{h(disp)} lodging rate by month</h2><div class="tab"><table class="dati"><caption>{cap}</caption><thead><tr><th scope="col">Month</th>'
              f'<th scope="col" class="n">FY {fy}</th><th scope="col" class="n">FY {fyp}</th><th scope="col" class="n">Change</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>')
    corpo += (f'<p class="small">M&amp;IE: {usd(L["mie"])} a day in FY {fy}, {usd(Lp["mie"])} in FY {fyp}.{rim.ref(f"gsa_xlsx{fy},gsa_xlsx{fyp}")}'
              + (f' GSA defined the area in FY {fyp} as {h(contee_txt(Lp))}.' if Lp["contee"] != L["contee"] else "") + "</p>")
    corpo += G.AD
    corpo += f'<h2 id="calculator">{h(disp)} per diem calculator</h2>' + calcolatore_pd(sel=k, titolo=f"Trip to {disp}", chiavi=[k])
    corpo += (f'<h2 id="mie">M&amp;IE breakdown for {usd(L["mie"])}</h2>' + tabella_mie(rim, evidenzia=L["mie"])
              + '<p class="small">Use it to deduct a meal provided by the government or included in a registration fee; complimentary hotel breakfasts and meals on a plane do not reduce M&amp;IE.'
              + rim.ref("gsa_mie") + "</p>")
    corpo += blocco_non_coperto(rim)
    a = (f"From {fy_periodo(fy)} the GSA maximum lodging rate in {disp} is {stagioni_txt(fy, L)} a night, and M&IE is {usd(L['mie'])} a day "
         f"({usd2(mr['primo_ultimo'])} on the first and last day of travel). The area covers {contee_txt(L)}.")
    fh, fld = G.faq_blocco([(ric, f"What is the per diem rate in {disp} for FY {fy}?", a, f"gsa_xlsx{fy},gsa_mie")], rim)
    corpo += fh
    altri = [(s2, sl2, n2) for s2, sl2, _, n2 in LOC_PAGINE if (s2, sl2) != (st, sl)]
    corpo += (f'<h2>More per diem rates</h2><p><a href="/per-diem/{slug_stato(st)}/">All {h(nome_st)} areas</a> · <a href="/per-diem/">All states</a> · '
              f'<a href="/per-diem/calculator/">Per diem calculator</a> · <a href="/irs-mileage-rate/">Mileage rates</a></p>'
              '<ul class="griglia larga">' + "".join(f'<li><a href="/per-diem/{slug_stato(s2)}/{sl2}/"><b>{h(n2)}</b><small>{usd(max(loc(fy, s2, sl2)["mesi"]))} max · {usd(loc(fy, s2, sl2)["mie"])} M&amp;IE</small></a></li>'
                                                     for s2, sl2, n2 in altri) + "</ul>")
    corpo += rim.elenco(NOTA_FONTI)
    testata = G.banda(f"Per diem · {nome_st}", f"{disp} Per Diem Rates FY {fy}",
                      f"Lodging up to <strong>{range_txt(L['mesi'])}</strong> a night and <strong>{usd(L['mie'])}</strong> a day for meals and incidentals in FY {fy}, month by month, with FY {fyp} for comparison.",
                      icona="cal")
    titolo = f"{disp} Per Diem Rates FY {fy} & {fyp} (GSA)"
    descr = (f"{disp} per diem FY {fy}: lodging {range_txt(L['mesi'])} a night by month and M&IE {usd(L['mie'])} a day ({usd2(mr['primo_ultimo'])} first and last day), with FY {fyp} and a calculator.")
    G.pagina(f"per-diem/{slug_stato(st)}/{sl}/", titolo, descr, corpo, testata,
             briciole=[("Home", ""), ("Per diem", "per-diem/"), (nome_st, f"per-diem/{slug_stato(st)}/"), (disp, f"per-diem/{slug_stato(st)}/{sl}/")],
             jsonld=[fld], disclaimer=DISCLAIMER_PD)


def pagina_calcolatore():
    rim = G.Rimandi()
    fy = fy_corrente()
    corpo = '<div class="pull">' + calcolatore_pd(titolo=f"Per diem calculator, FY {int(fy) - 1} and FY {fy}") + "</div>" + G.AD
    corpo += ('<h2 id="method">How the calculator works</h2><div class="testo">' + rim.t(
        '<ol><li>It finds the GSA area you choose and, for each date, the fiscal year it falls in (FY 2026 up to September 30, 2026, FY 2027 from October 1, 2026).[[gsa_xlsx2026,gsa_xlsx2027]]</li>'
        '<li><strong>Lodging:</strong> one night for every travel day except the last, each at the GSA maximum for the month of that night. '
        '“The lodging per diem rates are a maximum amount; the traveler only receives actual lodging costs up to that maximum rate.”[[gsa_faq]]</li>'
        '<li><strong>M&amp;IE:</strong> the full daily rate for each day between the first and the last; on the first and on the last day, 75 percent of the rate of the place you travel to.[[gsa_faq]]</li>'
        '<li><strong>Total</strong> = lodging + M&amp;IE. A trip of one day, with no overnight stay, shows 75 percent of the M&amp;IE rate: GSA says travelers are entitled to it '
        '“for one day travel away from your official station if it is longer than 12 hours”.[[gsa_faq]]</li></ol>'
        '<p>What it does not include: lodging taxes (“Lodging taxes are not included in the CONUS per diem rate”[[gsa_faq]]), deductions for meals provided to you (see the M&amp;IE breakdown), '
        'actual-expense authorizations, any reduced rate your agency sets for long stays, and travel to more than one place. Your travel authorization and your agency’s rules decide the final amount.</p>') + "</div>")
    corpo += '<h2 id="mie">M&amp;IE breakdown</h2>' + tabella_mie(rim)
    corpo += blocco_non_coperto(rim)
    voci = [("per diem calculator", "How does this per diem calculator work?",
             "Choose the GSA area and the first and last day of travel. It adds the GSA lodging maximum for each night (by month) and the M&IE for each day, with 75 percent on the first and last day, using the FY 2026 and FY 2027 rates.",
             "gsa_xlsx2026,gsa_xlsx2027,gsa_faq"),
            ("gsa per diem calculator", "Is this the official GSA per diem calculator?",
             "No. It is an independent calculator that uses the rates published by GSA for FY 2026 and FY 2027. GSA publishes the rates and its own lookup on gsa.gov.", "gsa_pd")]
    fh, fld = G.faq_blocco(voci, rim)
    corpo += fh + rim.elenco(NOTA_FONTI)
    testata = G.banda("Calculator", "Per Diem Calculator",
                      "Pick a GSA area and your travel dates: the maximum lodging for each night, M&amp;IE for each day with 75% on the first and last day, and the total.", icona="calc")
    G.pagina("per-diem/calculator/", f"Per Diem Calculator FY {fy}: GSA Lodging and M&IE by Date",
             f"Free GSA per diem calculator, FY {int(fy) - 1} and FY {fy}: pick a city or county and travel dates for the lodging maximum per night and M&IE with the 75% rule.",
             corpo, testata, briciole=[("Home", ""), ("Per diem", "per-diem/"), ("Calculator", "per-diem/calculator/")],
             jsonld=[fld, {"@context": "https://schema.org", "@type": "WebApplication", "name": "Per Diem Calculator", "applicationCategory": "FinanceApplication",
                           "operatingSystem": "Any", "url": f"{G.URL_SITO}/per-diem/calculator/", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}],
             disclaimer=DISCLAIMER_PD)


def pagina_miglia():
    rim = G.Rimandi()
    km = PD["chilometri"]
    i1, i2 = km["irs"]
    p1, p2 = km["gsa_pov"]
    corpo = (f'<section class="card stats pull" aria-label="Key figures">'
             f'<div class="stat main"><b>{cents(i2["business"])}</b><span>Business, per mile, from July 1, 2026{rim.ref("irs_a2026_11")}</span></div>'
             f'<div class="stat"><b>{cents(i1["business"])}</b><span>Business, January 1 to June 30, 2026{rim.ref("irs_n2026_10")}</span></div>'
             f'<div class="stat"><b>{cents(i2["medical_moving"])}</b><span>Medical and moving from July 1 ({cents(i1["medical_moving"])} before){rim.ref("irs_a2026_11,irs_n2026_10")}</span></div>'
             f'<div class="stat"><b>{cents(i2["charity"])}</b><span>Charity, all year (set by law){rim.ref("irs_a2026_11")}</span></div>'
             f'<p class="asof">The IRS changed the 2026 rates in the middle of the year: Announcement 2026-11 raised business and medical/moving rates from July 1, 2026. Read on {G.data_lunga(PD["letto_il"])}.</p></section>')
    corpo += '<div class="testo" style="margin-top:22px">' + rim.t(
        '<p>The IRS says: “Optional standard mileage rates are used to calculate the deductible costs of operating vehicles for business, charitable, and medical purposes.”[[irs_ir2025_128]] '
        '“Use of the standard mileage rates is optional.” “The rates apply to fully-electric and hybrid automobiles, as well as gasoline and diesel-powered vehicles.”[[irs_ir2025_128]] '
        'In July the IRS said: “This modification results from recent increases in the price of fuel.”[[irs_a2026_11]]</p>') + "</div>"
    righe = (f'<tr><th scope="row">July 1 – Dec. 31, 2026</th><td class="n">{cents(i2["business"])}</td><td class="n">{cents(i2["medical_moving"])}</td><td class="n">{cents(i2["charity"])}</td><td>Announcement 2026-11{rim.ref("irs_a2026_11")}</td></tr>'
             f'<tr><th scope="row">Jan. 1 – June 30, 2026</th><td class="n">{cents(i1["business"])}</td><td class="n">{cents(i1["medical_moving"])}</td><td class="n">{cents(i1["charity"])}</td><td>Notice 2026-10{rim.ref("irs_n2026_10")}</td></tr>')
    for x in km["irs_storico"]:
        righe += f'<tr><th scope="row">{x["anno"]}</th><td class="n">{cents(x["business"])}</td><td class="n">{cents(x["medical_moving"])}</td><td class="n">{cents(x["charity"])}</td><td>IRS table{rim.ref("irs_smr")}</td></tr>'
    corpo += (f'<h2 id="irs-2026">IRS standard mileage rates 2026</h2><div class="tab"><table class="dati"><caption>IRS optional standard mileage rates, cents per mile. Sources: IRS{rim.ref("irs_n2026_10,irs_a2026_11,irs_smr")}.</caption>'
              '<thead><tr><th scope="col">Period</th><th scope="col" class="n">Business</th><th scope="col" class="n">Medical or moving*</th><th scope="col" class="n">Charity</th><th scope="col">Source</th></tr></thead>'
              f'<tbody>{righe}</tbody></table></div>')
    corpo += ('<p class="small">* Moving: for certain active-duty members of the Armed Forces and now also certain members of the intelligence community.' + rim.ref("irs_ir2025_128") + ' '
              f'The IRS had not published 2027 rates when we checked on {G.data_lunga(PD["letto_il"])}; the 2026 rates were announced on December 29, 2025.' + rim.ref("irs_smr,irs_ir2025_128") + "</p>")
    corpo += (f'<h2 id="federal-travel">Mileage reimbursement for federal employees (GSA)</h2><div class="tab"><table class="dati"><caption>GSA privately owned vehicle (POV) rates for official travel, dollars per mile. Source: GSA{rim.ref("gsa_mileage")}.</caption>'
              '<thead><tr><th scope="col">Vehicle</th><th scope="col" class="n">From July 1, 2026</th><th scope="col" class="n">Jan. 1, 2026</th></tr></thead><tbody>'
              f'<tr><th scope="row">Automobile (no government car authorized or available)</th><td class="n">${p2["auto"]:.3f}</td><td class="n">${p1["auto"]:.3f}</td></tr>'
              f'<tr><th scope="row">Automobile, when a government car was authorized and available</th><td class="n">${p2["auto_gov_disponibile"]:.3f}</td><td class="n">${p1["auto_gov_disponibile"]:.3f}</td></tr>'
              f'<tr><th scope="row">Motorcycle</th><td class="n">${p2["moto"]:.3f}</td><td class="n">${p1["moto"]:.3f}</td></tr>'
              f'<tr><th scope="row">Airplane</th><td class="n">${p2["aereo"]:.3f}</td><td class="n">${p1["aereo"]:.3f}</td></tr>'
              '</tbody></table></div>')
    corpo += '<div class="testo">' + rim.t('<p>GSA’s example: “For example, 100 miles in your own automobile at $0.76 per mile = $76.00.” '
                                           '“Check with your agency’s travel office before using a privately owned vehicle for official travel.”[[gsa_mileage]]</p>') + "</div>"
    corpo += G.AD
    D = dati_miglia()
    r = miglia(D, "2026-11-13", "business", "100")
    corpo += f"""<h2 id="calculator">Mileage calculator 2026</h2><section class="card calc" data-km aria-labelledby="km-h">
<div class="calc-h"><h2 id="km-h">{G.ico("calc")}Miles × rate</h2></div>
<div class="calc-g">
<form class="calc-in" onsubmit="return false">
<label>Date of the trip<input type="date" name="data" value="2026-11-13" min="2026-01-01" max="2026-12-31" required></label>
<label>Rate<select name="scopo"><option value="business" selected>IRS business</option><option value="medical">IRS medical or moving</option><option value="charity">IRS charity</option>
<option value="gsa_auto">GSA federal travel, own car</option><option value="gsa_auto_gov">GSA federal travel, government car was available</option></select></label>
<label>Miles<input type="number" name="miglia" value="100" min="0.1" max="100000" step="0.1" inputmode="decimal" required></label>
</form>
<div class="calc-out" data-out aria-live="polite"><div class="tot"><div class="main"><span>Amount</span><b>{usd2(r["importo"])}</b></div><div><span>Rate per mile</span><b>{cents(r["tariffa"])}</b></div></div></div>
</div>
<p class="calc-f"><strong>Formula:</strong> miles (to one decimal) × the rate in force on the date of the trip, rounded to the cent. 2026 only. It runs in your browser.</p>
<script type="application/json" id="dati-km">{json.dumps(D, separators=(",", ":"))}</script>
</section>"""
    hist = km["irs_storico"]
    voci = [("irs mileage rate", "What is the IRS mileage rate for 2026?",
             f"{cents(i1['business'])} a mile for business from January 1 to June 30, 2026 and {cents(i2['business'])} from July 1, 2026. Medical and moving: {cents(i1['medical_moving'])}, then {cents(i2['medical_moving'])}. "
             f"Charity: {cents(i1['charity'])} all year.", "irs_n2026_10,irs_a2026_11"),
            ("irs mileage rate 2025", "What was the IRS mileage rate in 2025?",
             f"{cents(hist[0]['business'])} a mile for business, {cents(hist[0]['medical_moving'])} for medical or moving and {cents(hist[0]['charity'])} for charity.", "irs_smr"),
            ("gsa mileage rate", "What is the GSA mileage rate for federal employees?",
             f"${p2['auto']:.2f} a mile in your own car for official travel on or after July 1, 2026, or ${p2['auto_gov_disponibile']:.3f} if a government car was authorized and available. "
             f"From January 1, 2026 the rates were ${p1['auto']:.3f} and ${p1['auto_gov_disponibile']:.3f}.", "gsa_mileage"),
            ("mileage reimbursement calculator", "How is mileage reimbursement calculated?",
             "Miles driven × the rate per mile in force on the date of travel. GSA’s example: “100 miles in your own automobile at $0.76 per mile = $76.00.”", "gsa_mileage"),
            ("charity mileage rate", "What is the charity mileage rate?",
             f"{cents(i2['charity'])} a mile. It is fixed by section 170(i) of the Internal Revenue Code and did not change in July 2026.", "irs_a2026_11")]
    fh, fld = G.faq_blocco(voci, rim)
    corpo += fh
    corpo += '<p><a href="/per-diem/">GSA per diem rates by state</a> · <a href="/per-diem/calculator/">Per diem calculator</a></p>'
    corpo += rim.elenco(NOTA_FONTI)
    testata = G.banda("IRS · GSA · 2026", "IRS Mileage Rate 2026",
                      f"<strong>{cents(i2['business'])}</strong> a mile for business from July 1, 2026 ({cents(i1['business'])} from January to June), medical and moving {cents(i2['medical_moving'])}, charity {cents(i2['charity'])}, "
                      "plus the GSA rates for federal travel.", icona="up")
    G.pagina("irs-mileage-rate/", f"IRS Mileage Rate 2026: {cents(i1['business'])} and {cents(i2['business'])} from July 1",
             f"IRS standard mileage rates 2026: business {cents(i1['business'])} to June 30 and {cents(i2['business'])} from July 1, medical and moving, charity 14¢, GSA federal rates and a calculator.",
             corpo, testata, briciole=[("Home", ""), ("Mileage rate", "irs-mileage-rate/")], jsonld=[fld], disclaimer=DISCLAIMER_PD)


def come_controlliamo(G_, rim):
    """Paragrafo per /how-we-check/ (chiamato da genera.come_controlliamo)."""
    global G, PD
    G = G_
    PD = PD or json.loads((G.DATI / "perdiem.json").read_text(encoding="utf-8"))
    n26, n27 = len(PD["fy"]["2026"]["localita"]), len(PD["fy"]["2027"]["localita"])
    return ('<h2 id="per-diem-checks">Per diem and mileage rates</h2><div class="testo"><ul>' + rim.t(
        f'<li>The per diem tables come from the GSA rate files for FY 2026 ({n26} areas) and FY 2027 ({n27} areas), downloaded as published.[[gsa_xlsx2026,gsa_xlsx2027]] '
        'We keep each original file with its address, date and fingerprint (SHA-256) and stop the build if a file changes or the number of rows is not the one we checked.</li>'
        '<li>Every month of every area is compared with the second official source, the GSA per diem API: all of them match.[[gsa_api]] The M&amp;IE breakdown is compared with the table on GSA’s M&amp;IE page.[[gsa_mie]]</li>'
        '<li>The sentences we quote from GSA and the IRS are re-read on the official pages; a missing sentence stops the build.[[gsa_faq,irs_n2026_10,irs_a2026_11]]</li>'
        '<li>The per diem and mileage calculators in your browser are checked against our own reference calculation on hundreds of trips.</li>') + "</ul></div>")


# ---------------------------------------------------------------- entrata
def carica(G_):
    global G, PD
    G = G_
    PD = json.loads((G.DATI / "perdiem.json").read_text(encoding="utf-8"))


def genera(G_):
    carica(G_)
    stat = controlla()
    PAGINE_LOC.clear()
    for st, sl, _, _ in LOC_PAGINE:
        PAGINE_LOC[f"{st.lower()}/{sl}"] = f"per-diem/{slug_stato(st)}/{sl}/"
    tutte, alias = localita_unite()
    indice(tutte, alias)
    pagina_calcolatore()
    for st in sorted(PD["stati"]):
        pagina_stato(st)
    for x in LOC_PAGINE:
        pagina_localita(*x)
    pagina_miglia()
    stat.update(stati=len(PD["stati"]), pagine_localita=len(LOC_PAGINE), rinomine=alias)
    return stat
