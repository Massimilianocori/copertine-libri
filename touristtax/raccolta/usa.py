"""Tassa sugli alberghi negli Stati Uniti, prima parte: Florida e Texas (7/11/2026). Raccolta ripetibile dai file ufficiali.

Uso (dalla radice del repository):
    python3 -I touristtax/raccolta/usa.py                 # riscarica le fonti, rilegge i file e riscrive dati/usa.json
    python3 -I touristtax/raccolta/usa.py --domanda       # come sopra, e rifà anche le ricerche nell'autocomplete (circa 6 minuti)
    python3 -I touristtax/raccolta/usa.py --cache CARTELLA   # tiene i file scaricati in CARTELLA (per rileggerli a mano)

Fonti (tutte ufficiali):
- Florida Department of Revenue: modulo DR-15TDT «Local Option Transient Rental Tax Rates» (aliquota della tassa turistica di
  ognuna delle 67 contee, chi la riscuote, note sulle zone), modulo DR-15DSS «Discretionary Sales Surtax Information for Calendar
  Year AAAA» (sovrimposta di contea sulle vendite, che si applica anche agli affitti brevi: indirizzo preso dall'indice dei moduli,
  che cambia ogni novembre), pagine «Local Option Taxes», «Sales and Use Tax» e «Discretionary Sales Surtax» (6 % statale, ambito).
- Texas Comptroller of Public Accounts: pagina «Hotel Occupancy Tax» (6 % statale, soglie di prezzo), FAQ (esenzioni, esempio di
  Houston), pagina «Local Hotel Occupancy Tax Reporting» e il dataset data.texas.gov er34-v24h «Local Hotel Occupancy Tax Reporting
  2025» (aliquote comunali e di contea DICHIARATE dagli enti, non verificate dal Comptroller: lo dice la descrizione del dataset).
- U.S. Census Bureau, «2020 Census Place by County» (national_place_by_county2020.txt): in quali contee sta ogni città.
- Domanda (solo con --domanda): suggerimenti dell'autocomplete di Google (client=firefox, gl=us, hl=en) per «<luogo> hotel tax»,
  «<luogo> tourist tax», «<contea> county tourist tax»...: decidono quali città e contee hanno una pagina e quali domande vanno
  nelle FAQ. Senza --domanda si tengono quelli già salvati in dati/usa.json.

Lettura dei PDF: pdftotext -layout. DR-15TDT: una riga «Contea [(nota)] N% County|DOR|N/A» per contea, due colonne; le note (1)-(5)
devono essere parola per parola quelle attese (NOTE_ATTESE): se cambiano lo script si ferma, perché le zone vanno rilette a mano.
DR-15DSS: tabella a due colonne tagliata alla colonna della seconda intestazione «County»; per ogni contea la somma delle parti deve
dare il totale. Impronte: ricetta di raccolta/impronte.py (file = sha256 dei byte; testo = testo della pagina) e, per il dataset del
Texas, «json» = sha256 delle righe ordinate per tipo e nome, scritte con chiavi ordinate.
"""
import argparse
import hashlib
import html
import json
import re
import subprocess
import sys
import tempfile
import time
import unicodedata
import urllib.parse
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import impronte  # noqa: E402  (stessa ricetta delle impronte di tutto il sito)

RADICE = Path(__file__).resolve().parent.parent
USCITA = RADICE / "dati" / "usa.json"
OGGI = date.today().isoformat()

FL_INDICE_MODULI = "https://floridarevenue.com/Pages/forms_index.aspx"
TX_DATI = "https://data.texas.gov/resource/er34-v24h.json?$limit=5000&$order=type,name"
TX_META = "https://data.texas.gov/api/views/er34-v24h.json"
TX_STORICO = "https://data.texas.gov/dataset/Local-Hotel-Occupancy-Tax-HOT-Data/vmy5-jctb/about_data"
TX_META_STORICO = "https://data.texas.gov/api/views/vmy5-jctb.json"
CENSUS = "https://www2.census.gov/geo/docs/reference/codes2020/national_place_by_county2020.txt"

FONTI = {  # chiave -> (url, titolo, ente, formato)
    "fl_tdt": ("https://floridarevenue.com/Forms_library/current/dr15tdt.pdf",
               "Form DR-15TDT, Local Option Transient Rental Tax Rates (Tourist Development Tax Rates)", "Florida Department of Revenue", "PDF"),
    "fl_dss": (None, "Form DR-15DSS, Discretionary Sales Surtax Information", "Florida Department of Revenue", "PDF"),
    "fl_local": ("https://floridarevenue.com/taxes/taxesfees/Pages/local_option.aspx", "Local Option Taxes", "Florida Department of Revenue", "web page"),
    "fl_sales": ("https://floridarevenue.com/taxes/taxesfees/Pages/sales_tax.aspx", "Florida Sales and Use Tax", "Florida Department of Revenue", "web page"),
    "fl_disc": ("https://floridarevenue.com/taxes/taxesfees/Pages/discretionary.aspx", "Discretionary Sales Surtax", "Florida Department of Revenue", "web page"),
    "tx_hot": ("https://comptroller.texas.gov/taxes/hotel/", "Hotel Occupancy Tax", "Texas Comptroller of Public Accounts", "web page"),
    "tx_faq": ("https://comptroller.texas.gov/taxes/hotel/faq.php", "Hotel Occupancy Tax FAQs", "Texas Comptroller of Public Accounts", "web page"),
    "tx_report": ("https://comptroller.texas.gov/transparency/local/hotel-reporting/", "Local Hotel Occupancy Tax Reporting",
                  "Texas Comptroller of Public Accounts", "web page"),
    "tx_dati": ("https://data.texas.gov/dataset/Local-Hotel-Occupancy-Tax-Reporting-2025/er34-v24h/about_data",
                "Local Hotel Occupancy Tax Reporting 2025 (dataset er34-v24h)", "Texas Comptroller of Public Accounts, data.texas.gov", "open data (JSON)"),
    "census": (CENSUS, "2020 Census Place by County relationship file", "U.S. Census Bureau", "text file"),
}

# Note del DR-15TDT (revisione 10/26), parola per parola. Se cambiano, le zone di ZONE vanno rilette a mano.
NOTE_ATTESE = {
    "1": "Bay: Applies only to ZIP codes 32401, 32404, 32405, 32407, 32408, 32410, and Bay County portion of 32413.",
    "2": "Miami-Dade: 4% for Surfside and Bal Harbour, 7% for Miami Beach, and 6% for the rest of the county.",
    "3": "Nassau: Applies only to ZIP code 32034 for Amelia Island.",
    "4": "Okaloosa: 6% for the Okaloosa County Tourist Development Tax District and 6% for the Expansion District.",
    "5": "Walton: 5% for ZIP codes 32459, 32550, 32454, 32461, and Walton County portion of 32413; and 2% for the rest of the county.",
}
# Zone scritte dalle note qui sopra: (id, nome, aliquota della tassa turistica). La prima è quella mostrata per prima.
ZONE = {
    "bay": [("zip", "ZIP codes 32401, 32404, 32405, 32407, 32408, 32410 and the Bay County part of 32413", 5),
            ("resto", "Rest of Bay County", 0)],
    "miami-dade": [("resto", "Miami-Dade County outside Miami Beach, Surfside and Bal Harbour", 6), ("miami-beach", "Miami Beach", 7),
                   ("surfside", "Surfside and Bal Harbour", 4)],
    "nassau": [("zip", "ZIP code 32034 (Amelia Island)", 5), ("resto", "Rest of Nassau County", 0)],
    "walton": [("zip", "ZIP codes 32459, 32550, 32454, 32461 and the Walton County part of 32413", 5), ("resto", "Rest of Walton County", 2)],
}
# Città della Florida candidate a una pagina (la domanda decide). Contea dal file del Census; la zona solo se la nota la nomina.
FL_CITTA = ["orlando", "kissimmee", "miami", "miami beach", "fort lauderdale", "tampa", "st. petersburg", "clearwater", "key west", "destin",
            "panama city beach", "panama city", "fort myers", "sarasota", "daytona beach", "jacksonville", "st. augustine", "pensacola",
            "west palm beach", "boca raton", "tallahassee", "gainesville", "cocoa beach", "fort walton beach", "marco island", "fernandina beach",
            "delray beach", "ocala", "new smyrna beach", "vero beach", "bradenton", "st. pete beach", "treasure island", "islamorada", "marathon",
            "key largo", "celebration", "surfside", "bal harbour", "lake buena vista", "sunny isles beach", "lakeland", "winter park", "davenport",
            "port st. lucie", "stuart", "jupiter", "punta gorda", "cape coral", "bonita springs", "ormond beach", "palm coast", "titusville",
            "dunedin", "tarpon springs", "madeira beach", "longboat key", "sanibel", "naples", "venice", "hollywood", "melbourne"]
# Nomi che nell'autocomplete parlano di un altro luogo (stessa parola, altro Paese o Stato): nessuna pagina.
ALTRI_LUOGHI = {"naples": "Napoli (Italia)", "venice": "Venezia (Italia)", "hollywood": "Hollywood (California)", "melbourne": "Melbourne (Australia)",
                "paris": "Parigi (Francia)", "athens": "Atene (Grecia)", "victoria": "Victoria (Canada, Messico)", "edinburg": "Edimburgo (Scozia)",
                "orange": "Orange County (California, Florida)", "richmond": "Richmond (Virginia)", "buffalo": "Buffalo (New York)",
                "huntsville": "Huntsville (Alabama)", "fredericksburg": "Fredericksburg (Virginia)", "greenville": "Greenville (South Carolina)",
                "temple": "non riguarda la città"}
STATI_ALTRI = re.compile(r"\b(va|al|ny|nc|sc|bc|ca|oh|ohio|pa|ga|mexico|italy|france|greece|scotland|uk|virginia|california|alabama|bali|spain)\b")
PAROLE_TASSA = re.compile(r"\b(hotel|tourist|tourism|occupancy|lodging|resort|room|bed|transient)\b")
DOMANDE_GENERALI = ["hotel tax by state", "us hotel tax", "hotel tax usa", "florida hotel tax", "florida tourist tax", "florida tourist development tax",
                    "florida hotel tax rate", "does florida have a tourist tax", "florida sales tax on hotel rooms", "texas hotel tax",
                    "texas hotel occupancy tax", "texas state hotel tax", "texas hotel tax exemption"]


def scarica(url, dest, tentativi=4):
    """Codice HTTP (0 = connessione fallita). floridarevenue.com a volte chiude la connessione senza risposta: si riprova."""
    codice = 0
    for i in range(tentativi):
        r = subprocess.run(["curl", "-sS", "-L", "-m", "120", "-A", "Mozilla/5.0 (X11; Linux x86_64)", "-o", str(dest), "-w", "%{http_code}", url],
                           capture_output=True, text=True)
        codice = int(r.stdout.strip()) if r.stdout.strip().isdigit() else 0
        if codice in (200, 404):
            break
        time.sleep(3 * (i + 1))
    return codice


def pdf_testo(f):
    return subprocess.run(["pdftotext", "-layout", str(f), "-"], capture_output=True, text=True, check=True).stdout


def chiave(nome):
    """'St. Johns' / 'St Johns' / 'DeSoto' / 'Miami-Dade' -> 'st-johns', 'desoto', 'miami-dade'."""
    t = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().lower().replace(".", "")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def json_impronta(righe):
    righe = sorted(righe, key=lambda r: (r.get("type", ""), r.get("name", "")))
    return "sha256:" + hashlib.sha256(json.dumps(righe, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


# Frasi delle fonti che le pagine citano o riassumono: devono esserci parola per parola (spazi normalizzati). Se una manca, la fonte
# è cambiata: rileggerla e correggere qui e nelle pagine (genera.py usa il testo salvato in dati/usa.json -> "frasi").
FRASI = {
    "fl_tdt": {
        "ambito": "Individual Florida counties and certain cities may impose a local option tax on the rental or lease of living, sleeping, or housekeeping accommodations for a term of six months or less.",
        "in_aggiunta": "The local tax imposed is in addition to the 6% state sales tax and any applicable discretionary sales surtax.",
        "dor": "For the shaded counties in the chart below, the local option transient rental taxes are reported and remitted to the Florida Department of Revenue (DOR).",
        "contea": "For all other counties, the local option transient rental taxes are reported and remitted directly to the county; however, sales tax and discretionary sales surtax on transient rentals are always reported and remitted to the Department.",
        "verifica": "If the local option transient rental tax is collected by the county, contact that county to verify the tax rate.",
        "non_tutte": "Not all counties notify the Department of changes in their local option transient rental tax rate.",
    },
    "fl_local": {
        "resort": "Currently, only three municipalities in Miami-Dade County (Bal Harbour, Miami Beach, and Surfside) are eligible to impose this tax.",
        "resort_max": "They may levy up to 4% on transient rental transactions and up to 2% on the sale of food and beverages consumed in restaurants and bars.",
    },
    "fl_sales": {
        "affitti": "Renting short-term living accommodations (for example, motel/hotel rooms, beach houses, condominiums, timeshare resorts, vacation houses, or travel parks)",
    },
    "fl_disc": {
        "affitti": "The rental of living or sleeping accommodations (transient rentals) occurs in a county with a surtax",
        "tetto": "The $5,000 cap does not apply to transactions such as charges for prepaid calling arrangements, sales of admissions, transient rentals, or sales of services.",
    },
    "tx_hot": {
        "aliquota": "The state hotel occupancy tax rate is 6 percent (.06) of the cost of a room.",
        "locali": "Cities and certain counties and special purpose districts are authorized to impose an additional local hotel tax that the local taxing authority collects.",
        "piattaforme": "Property management companies, online travel companies and other third-party rental companies may also be responsible for collecting the tax.",
        "case": "Persons leasing their houses must collect hotel occupancy tax from their customers in the same way a hotel or motel collects the tax from its guests.",
    },
    "tx_faq": {
        "soglia_stato": "For the purposes of the state tax, a hotel is considered to be any building in which members of the public rent sleeping accommodations for $15 or more per day.",
        "soglia_locale": "Local hotel taxes apply to sleeping rooms costing $2 or more per day.",
        "ambito": "The tax covers hotels, motels, and bed and breakfasts, as well as condominiums, apartments and houses rented for less than 30 consecutive days.",
        "massimi": "Cities and some counties and special purpose districts can each levy local hotel taxes, generally at rates varying up to 7 percent; sports and community venue projects can levy hotel taxes at rates varying up to 2 percent, except for Dallas County which can impose a hotel venue tax at a rate of up to 3 percent.",
        "houston": "For example, in Houston there is 6 percent state tax, 7 percent Houston tax, 2 percent Harris County tax and 2 percent Harris County - Houston Sports Authority tax.",
        "chi": "The Comptroller's office collects and administers the 6 percent state hotel tax, while cities and counties are responsible for collecting their own local hotel taxes.",
        "federali": "The U.S. government and its employees traveling on official business.",
        "residenti": "Permanent residents who occupy a room for at least 30 consecutive days.",
        "trenta": "Guests who stay 30 or more days and notify the hotel in writing of their intention beforehand are exempt from the day of notification. Guests who do not notify the hotel must pay the tax the first 30 days and are exempt thereafter.",
        "religiosi": "Religious, charitable and educational organizations that have received a letter of exemption from the Comptroller's office are exempt from the 6 percent state hotel tax.",
    },
}


def testo_fonte(f):
    """Testo della fonte con gli spazi normalizzati (PDF con pdftotext -layout, pagine con la ricetta di impronte.py)."""
    b = f.read_bytes()
    if b[:4] == b"%PDF":
        return re.sub(r"\s+", " ", pdf_testo(f))
    t = b.decode("utf-8", "replace")
    m = re.search(r"<main.*?</main>", t, re.S)
    t = m.group(0) if m else t
    t = re.sub(r"<script.*?</script>|<style.*?</style>|<form.*?</form>", "", t, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).replace("\u2019", "'").replace("\u200b", "").strip()


# ---------------------------------------------------------------- Florida
def leggi_tdt(testo):
    rev = re.search(r"R\.\s*(\d{1,2}/\d{2})", testo).group(1)
    righe = re.findall(r"([A-Z][a-zA-Z.\-]+(?: [A-Z][a-zA-Z.\-]+)*)(?: \((\d)\))?\s+(\d+(?:\.\d+)?)%\s+(County|DOR|N/A)", testo)
    contee = [{"id": chiave(n), "nome": n, "aliquota": float(a), "riscossa_da": chi, "nota": nota or None} for n, nota, a, chi in righe]
    note = {n: re.sub(r"\s+", " ", t).strip() for n, t in re.findall(r"^\s*\((\d)\)\s+(\S.*)$", testo, re.M)}
    if len(contee) != 67 or len({c["id"] for c in contee}) != 67:
        raise SystemExit(f"DR-15TDT: attese 67 contee, lette {len(contee)}")
    if note != NOTE_ATTESE:
        raise SystemExit("DR-15TDT: le note sulle zone sono cambiate: rileggere il PDF e aggiornare NOTE_ATTESE e ZONE.\n" + json.dumps(note, indent=1))
    return rev, contee, note


DATA_DSS = r"[A-Z][a-z]{2} \d{1,2}, \d{4}"


def _pct(s):
    return float(s.replace("%", "")) if s and s != "None" else 0.0


def _data_iso(s):
    if not s or s == "None":
        return None
    return date(int(s[-4:]), ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].index(s[:3]) + 1,
                int(s[4:].split(",")[0])).isoformat()


def leggi_dss(testo):
    anno = int(re.search(r"Calendar Year\s+(\d{4})", re.sub(r"\s+", " ", testo)).group(1))
    rev = re.search(r"R\.\s*(\d{1,2}/\d{2})", testo).group(1)
    pag1 = testo.split("\f")[0]
    righe = pag1.splitlines()
    i_int = next(i for i, r in enumerate(righe) if r.lstrip().startswith("County") and r.count("County") >= 2)
    taglio = [m.start() for m in re.finditer(r"County", righe[i_int])][1] - 1
    lati = ([], [])
    for r in righe[i_int + 1:]:
        lati[0].append(r[:taglio])
        lati[1].append(r[taglio:])
    contee = {}
    for lato in lati:
        attuale = None
        for r in lato:
            s = r.rstrip()
            if not s.strip():
                continue
            m = re.match(rf"^\s?([A-Z][A-Za-z.\-]*(?: [A-Z][A-Za-z.\-]*)*)\s{{2,}}(\.?\d+(?:\.\d+)?%|None)(?:\s+\((\.?\d+(?:\.\d+)?)%\))?(?:\s+({DATA_DSS})\s+({DATA_DSS}|None))?\s*$", s)
            if m:
                nome, tot, parte, dal, al = m.groups()
                attuale = chiave(nome)
                contee[attuale] = {"nome": nome, "totale": _pct(tot), "parti": []}
                if dal:
                    contee[attuale]["parti"].append({"aliquota": _pct(parte) if parte else _pct(tot), "dal": _data_iso(dal), "al": _data_iso(al)})
                continue
            m = re.search(rf"\((\.?\d+(?:\.\d+)?)%\)\s+({DATA_DSS})\s+({DATA_DSS}|None)\s*$", s)
            if m and attuale:
                contee[attuale]["parti"].append({"aliquota": _pct(m.group(1)), "dal": _data_iso(m.group(2)), "al": _data_iso(m.group(3))})
                continue
            if re.search(r"\d%|\d{4}", s):
                raise SystemExit(f"DR-15DSS: riga non letta: {s!r}")
    for k, c in contee.items():
        if abs(sum(p["aliquota"] for p in c["parti"]) - c["totale"]) > 1e-9:
            raise SystemExit(f"DR-15DSS: {c['nome']}: somma delle parti diversa dal totale")
    cambi = re.sub(r"\s+", " ", testo.split("\f")[1]).split("Contact Us")[0].strip() if "\f" in testo else ""  # senza i recapiti
    return anno, rev, contee, cambi


def url_dss(cache):
    f = cache / "forms_index.html"
    if scarica(FL_INDICE_MODULI, f) != 200:
        raise SystemExit("Florida: indice dei moduli non leggibile")
    t = f.read_text(encoding="utf-8", errors="replace")
    link = sorted(set(re.findall(r'href="(/Forms_library/current/dr15dss[^"]*\.pdf)"', t)))
    if len(link) != 1:
        raise SystemExit(f"Florida: link DR-15DSS nell'indice dei moduli: {link}")
    return "https://floridarevenue.com" + link[0]


# ---------------------------------------------------------------- Texas e Census
def nome_tx(n):
    return re.sub(r"^(Town|City|Village) of ", "", n).strip()


def leggi_census(f, stati=("FL", "TX")):
    luoghi = {}
    with open(f, encoding="utf-8", errors="replace") as fh:
        next(fh)
        for riga in fh:
            p = riga.rstrip("\n").split("|")
            if p[0] not in stati:
                continue
            nome = re.sub(r" (city|town|village|CDP)$", "", p[6])
            luoghi.setdefault((p[0], chiave(nome)), []).append(p[3].replace(" County", ""))
    return luoghi


# ---------------------------------------------------------------- domanda (autocomplete)
def autocomplete(q):
    u = "https://suggestqueries.google.com/complete/search?client=firefox&gl=us&hl=en&q=" + urllib.parse.quote(q)
    for _ in range(3):
        r = subprocess.run(["curl", "-sS", "-m", "20", u], capture_output=True)
        try:
            return json.loads(r.stdout.decode("utf-8", "replace"))[1]
        except (ValueError, IndexError):
            time.sleep(2)
    return None


def pertinenti(sugg, nome):
    """Suggerimenti con il nome del luogo, una parola della tassa e 'tax'. Per una città non contano quelli di un luogo più lungo
    con lo stesso nome ('miami beach', 'panama city beach', 'midland county', 'west palm beach')."""
    altro = re.compile(rf"(\b(west|north|south|east|new) {re.escape(nome)}\b|\b{re.escape(nome)} (beach|county|dade|shores|gardens|springs)\b)")
    return [s for s in (sugg or []) if re.search(rf"\b{re.escape(nome)}\b", s) and PAROLE_TASSA.search(s) and re.search(r"\btax(es)?\b", s)
            and (nome.endswith(" county") or nome == "miami dade" or not altro.search(s))]


def query_luogo(tipo, nome):
    if tipo == "fl_contea":
        base = "miami dade" if nome == "miami-dade" else nome.replace(".", "")
        return [f"{base} county tourist tax", f"{base} county hotel tax"] if nome != "miami-dade" else ["miami dade tourist tax", "miami dade hotel tax"]
    if tipo == "fl_citta":
        n = nome.replace(".", "")
        return [f"{n} hotel tax", f"{n} tourist tax"]
    if tipo == "tx_contea":
        return [f"{nome} county hotel tax"]
    return [f"{nome} hotel tax"]


TX_GRANDI = set()  # riempito in main(): le 25 città con più entrate dichiarate (capitolo 351)


def scegli(tipo, nome, D):
    """True se il luogo ha domanda vera: almeno 2 suggerimenti pertinenti (nome + parola della tassa + 'tax'), del luogo giusto."""
    if nome.replace(".", "") in ALTRI_LUOGHI:
        return False, []
    base = {"fl_contea": ("miami dade" if nome == "miami-dade" else nome.replace(".", "") + " county"),
            "tx_contea": nome + " county"}.get(tipo, nome.replace(".", ""))
    tutti = []
    for q in query_luogo(tipo, nome):
        for s in pertinenti(D.get(q), base):
            if s not in tutti:
                tutti.append(s)
    if len(tutti) < 2:
        return False, tutti
    if tipo.startswith("fl"):
        contesto = nome == "miami-dade" or tipo == "fl_citta" or any(re.search(r"\b(florida|fl)\b|tourist development tax", s) for s in tutti)
        estranei = [s for s in tutti if STATI_ALTRI.search(s.replace(base, "")) and not re.search(r"\b(florida|fl)\b", s)]
    else:
        # una città del Texas senza «texas», «tx» o «hotel occupancy tax» nei suggerimenti conta solo se è tra i maggiori mercati
        # alberghieri del file (prime 25 per entrate dichiarate): «miami hotel tax» parla di Miami (Florida), non di Miami (Texas)
        contesto = (any(re.search(r"\b(texas|tx)\b|hotel occupancy tax", s) for s in tutti)
                    or (tipo == "tx_citta" and nome in TX_GRANDI))
        estranei = [s for s in tutti if STATI_ALTRI.search(s.replace(base, "")) and not re.search(r"\b(texas|tx)\b", s)]
        if estranei and not any(re.search(r"\b(texas|tx)\b", s) for s in tutti):
            return False, tutti
    return bool(contesto), [s for s in tutti if s not in estranei]


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache")
    ap.add_argument("--domanda", action="store_true")
    a = ap.parse_args()
    tmp = None if a.cache else tempfile.TemporaryDirectory()
    cache = Path(a.cache or tmp.name)
    cache.mkdir(parents=True, exist_ok=True)
    vecchio = json.loads(USCITA.read_text(encoding="utf-8")) if USCITA.exists() else {}

    fonti = {}

    def fonte(k, url=None, file=None, imp=None, extra=None):
        u, titolo, ente, formato = FONTI[k]
        url = url or u
        dest = cache / (file or (k + (".pdf" if formato == "PDF" else ".html")))
        codice = scarica(url, dest) if imp is None else 200
        if codice != 200:
            raise SystemExit(f"{k}: HTTP {codice} {url}")
        if imp is None:
            tipo, imp_ = impronte.impronta(dest.read_bytes())
        else:
            tipo, imp_ = imp
        fonti[k] = dict({"url": url, "titolo": titolo, "ente": ente, "formato": formato, "http": 200, "controllato_il": OGGI,
                         "impronta_di": tipo, "impronta": imp_}, **(extra or {}))
        return dest

    # Florida
    f_tdt = fonte("fl_tdt")
    rev_tdt, contee_tdt, note = leggi_tdt(pdf_testo(f_tdt))
    fonti["fl_tdt"]["revisione"] = rev_tdt
    f_dss = fonte("fl_dss", url=url_dss(cache))
    anno_dss, rev_dss, dss, cambi_dss = leggi_dss(pdf_testo(f_dss))
    fonti["fl_dss"].update({"revisione": rev_dss, "anno": anno_dss, "titolo": f"Form DR-15DSS, Discretionary Sales Surtax Information for Calendar Year {anno_dss}"})
    for k in ("fl_local", "fl_sales", "fl_disc"):
        fonte(k)
    mancanti = [c["nome"] for c in contee_tdt if c["id"] not in dss]
    if mancanti or len(dss) != 67:
        raise SystemExit(f"DR-15DSS: contee mancanti {mancanti} (lette {len(dss)})")
    florida = {"stato": 6.0, "tdt_revisione": rev_tdt, "note_tdt": note,
               "zone": {k: [{"id": i, "nome": n, "aliquota": float(r)} for i, n, r in v] for k, v in ZONE.items()},
               "contee": [dict(c, surtax=dss[c["id"]]) for c in contee_tdt], "dss_anno": anno_dss, "dss_revisione": rev_dss, "dss_cambi": cambi_dss}

    # Texas
    for k in ("tx_hot", "tx_faq", "tx_report"):
        fonte(k)
    f_tx = cache / "tx.json"
    if scarica(TX_DATI, f_tx) != 200 or scarica(TX_META, cache / "tx_meta.json") != 200:
        raise SystemExit("Texas: dataset er34-v24h non leggibile")
    righe_tx = json.loads(f_tx.read_text(encoding="utf-8"))
    meta = json.loads((cache / "tx_meta.json").read_text(encoding="utf-8"))
    aggiornato = date.fromtimestamp(meta["rowsUpdatedAt"]).isoformat()
    fonte("tx_dati", url=FONTI["tx_dati"][0], imp=("json", json_impronta(righe_tx)),
          extra={"url_dati": TX_DATI, "righe": len(righe_tx), "aggiornato_il": aggiornato, "nome_dataset": meta["name"]})
    desc = re.sub(r"\s+", " ", meta.get("description") or "")
    # Le frasi sul modulo di dichiarazione (dati non verificati, enti mancanti) stanno nella descrizione del dataset storico vmy5-jctb
    # dello stesso Comptroller («Local Hotel Occupancy Tax (HOT) Data»), che raccoglie i dati dello stesso modulo.
    if scarica(TX_META_STORICO, cache / "tx_meta_storico.json") != 200:
        raise SystemExit("Texas: descrizione del dataset vmy5-jctb non leggibile")
    meta_s = json.loads((cache / "tx_meta_storico.json").read_text(encoding="utf-8"))
    desc_s = re.sub(r"\s+", " ", meta_s.get("description") or "")
    frasi_tx = {}
    for k, f in (("mancanti", r"If local HOT data related to a specific municipality or county is not available in this dataset, it may be because that entity does not levy such a tax or that the local government failed to submit their information to the Comptroller's office within the specified reporting period\."),
                 ("non_verificati", r"The data reported through the Comptroller.s Local HOT Submission Form and available in this dataset is self-reported by submitting municipalities, counties, or third parties on their behalf and has not been independently verified by the Texas Comptroller of Public Accounts\.")):
        m = re.search(f, desc_s)
        if not m:
            raise SystemExit(f"Texas: frase attesa non trovata nella descrizione di vmy5-jctb ({k})")
        frasi_tx[k] = m.group(0)
    fonti["tx_storico"] = {"url": TX_STORICO, "titolo": "Local Hotel Occupancy Tax (HOT) Data (dataset vmy5-jctb, description)",
                           "ente": "Texas Comptroller of Public Accounts, data.texas.gov", "formato": "open data (description)", "http": 200,
                           "controllato_il": OGGI, "impronta_di": "testo",
                           "impronta": "sha256:" + hashlib.sha256(desc_s.encode("utf-8")).hexdigest(), "url_impronta": TX_META_STORICO}
    righe = []
    for r in righe_tx:
        righe.append({"tipo": r["type"], "nome": nome_tx(r["name"]), "nome_file": r["name"], "anno": r.get("fiscalyear"),
                      "r351": r.get("tax_rate_351"), "r334": r.get("tax_rate_334"), "entrate_351": r.get("total_revenue_351")})
    TX_GRANDI.update(r["nome"].lower() for r in sorted((r for r in righe if r["tipo"] != "county"), key=lambda r: -float(r["entrate_351"] or 0))[:25])
    # frasi citate dalle pagine
    frasi = {}
    for k, ff in FRASI.items():
        nome_file = {"fl_tdt": "fl_tdt.pdf"}.get(k, k + ".html")
        testo = testo_fonte(cache / nome_file)
        for kk, frase in ff.items():
            if frase not in testo:
                raise SystemExit(f"{k}: frase attesa non trovata ({kk}): rileggere la fonte {fonti[k]['url']}")
            frasi.setdefault(k, {})[kk] = frase
    # Census: contee di ogni città
    f_c = fonte("census", file="census.txt")
    luoghi = leggi_census(f_c)
    for r in righe:
        if r["tipo"] != "county":
            r["contee"] = luoghi.get(("TX", chiave(r["nome"])), [])

    # Domanda
    D = (vecchio.get("domanda") or {}).get("query", {})
    data_domanda = (vecchio.get("domanda") or {}).get("il")
    candidati = ([("fl_contea", c["id"].replace("-", " ") if c["id"] != "miami-dade" else "miami-dade") for c in contee_tdt]
                 + [("fl_citta", c) for c in FL_CITTA]
                 + [("tx_citta", r["nome"].lower()) for r in righe
                    if r["tipo"] != "county" and (float(r["r351"] or 0) + float(r["r334"] or 0)) > 0]
                 + [("tx_contea", r["nome"].lower()) for r in righe if r["tipo"] == "county" and (float(r["r351"] or 0) + float(r["r334"] or 0)) > 0])
    if a.domanda:
        D = {}
        query = DOMANDE_GENERALI + [q for t, n in candidati for q in query_luogo(t, n)]
        for i, q in enumerate(dict.fromkeys(query)):
            D[q] = autocomplete(q)
            time.sleep(0.3)
            if i % 50 == 0:
                print(f"  autocomplete: {i}/{len(query)}", file=sys.stderr)
        data_domanda = OGGI
    pagine = {"fl_contea": [], "fl_citta": [], "tx_citta": [], "tx_contea": []}
    for tipo, nome in candidati:
        ok, sugg = scegli(tipo, nome, D)
        if ok:
            pagine[tipo].append({"nome": nome, "suggerimenti": sugg})
    for p in pagine["fl_citta"]:
        p["contee"] = luoghi.get(("FL", chiave(p["nome"])), [])
        if not p["contee"]:
            raise SystemExit(f"Census: città della Florida senza contea: {p['nome']}")

    out = {"_nota": ("Dati per la sezione usa/ (Florida e Texas), scritti da raccolta/usa.py: non modificare a mano. Aliquote in percento. "
                     "Texas: aliquote dichiarate dagli enti al Comptroller (anno fiscale 2025), come nel file."),
           "controllato_il": OGGI, "fonti": fonti, "frasi": frasi, "florida": florida,
           "texas": {"stato": 6.0, "soglia_stato": 15, "soglia_locale": 2, "righe": righe, "anno_fiscale": "2025", "descrizione": desc, "frasi": frasi_tx},
           "domanda": {"il": data_domanda, "gl": "us", "client": "firefox", "query": D}, "pagine": pagine}
    USCITA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Florida: {len(contee_tdt)} contee (DR-15TDT R. {rev_tdt}, DR-15DSS {anno_dss} R. {rev_dss}); Texas: {len(righe)} righe "
          f"(aggiornato {aggiornato}); pagine: " + ", ".join(f"{k} {len(v)}" for k, v in pagine.items()) + f"; domanda del {data_domanda}")


if __name__ == "__main__":
    main()
