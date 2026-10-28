"""Guidare all'estero con la patente britannica, canadese o australiana: serve il permesso internazionale (IDP)?
Legge le fonti ufficiali, salva i grezzi in raccolta/.cache/ e scrive dati/patenti.json (sezione "driving-abroad/" del sito).

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/patenti.py              # scarica le pagine nuove o più vecchie di 20 ore (circa 460 richieste, 3-4 minuti)
    BYF_OFFLINE=1 python3 -I beforeyoufly/raccolta/patenti.py   # rilegge solo i grezzi già salvati, senza rete
    BYF_CACHE_ORE=0 python3 -I beforeyoufly/raccolta/patenti.py # riscarica tutto
    python3 -I beforeyoufly/raccolta/patenti.py --domanda    # rilegge anche l'autocompletamento di Google (dati/patenti_domanda.json)
    python3 -I beforeyoufly/raccolta/patenti.py --pagine     # ricalcola solo le coppie con pagina da dati/patenti_domanda.json (senza rete)

Fonti (SOLO ufficiali, lette il 28/10/2026):
  Regno Unito  GOV.UK "Driving abroad", parte "Check if you need an international driving permit (IDP)": tabella "Country or territory /
               Type of IDP / More information" (Content API https://www.gov.uk/api/content/driving-abroad, la pagina
               /driving-abroad/international-driving-permit risponde 303 verso la guida intera), più la parte "Get an IDP" (PayPoint, 5,50 £,
               durata); e il paragrafo "Road travel" (sezione "Safety and security") dei consigli di viaggio FCDO di ogni Paese
               (https://www.gov.uk/api/content/foreign-travel-advice/<paese>). Licenza OGL v3.
  Canada       travel.gc.ca, scheda di ogni destinazione, scheda "Laws and culture", titolo "Driving" (open data
               https://data.international.gc.ca/travel-voyage/cta-cap-<ISO>.json, campo eng.laws-culture; stessa cache e stessi file di
               raccolta/passaporti_ca.py, in raccolta/.cache/ca/), più la pagina https://travel.gc.ca/travelling/documents/international-driving-permit
               (CAA, validità 1 anno, Stati Uniti). Licenza Open Government Licence – Canada.
  Australia    smartraveller.gov.au, scheda di ogni destinazione, sezione "Travel", sottosezione "Local travel", titoli sulla patente ("Driving
               permit", "Driver's licences and International Driving permits"...). Smartraveller chiude le richieste semplici (curl: HTTP/2
               INTERNAL_ERROR, "Empty reply from server" il 28/10/2026): si rileggono le pagine salvate da raccolta/passaporti_au.py, che le legge
               con il browser (raccolta/.cache/au/); la data di lettura è quella di quei file. Licenza CC BY 4.0.

Regole (nessuna deduzione):
  - Si salva SEMPRE il testo ufficiale parola per parola (frasi della patente / del permesso), con URL e data di lettura.
  - L'esito ("si", "no", "dipende", "consigliato") si ricava SOLO da frasi che corrispondono a uno schema fisso (SCHEMI_* qui sotto); per il
    Regno Unito dalla riga della tabella GOV.UK (colonna "More information" vuota = serve l'IDP del tipo indicato; frasi fisse per i casi "no" e
    "dipende"). Se nessuna frase corrisponde, o se due frasi dicono cose diverse, l'esito viene da dati/patenti_manuali.json (scritto a mano,
    legato all'impronta del testo: se il testo cambia, il fatto manuale scade e lo script lo segnala) oppure resta "da_leggere" e il sito
    mostra solo la citazione.
  - Se la fonte non dice nulla sul permesso per quel Paese: "non_detto" (il sito scrive "Not stated by <ente>").
  - La convenzione (1926/1949/1968) si scrive SOLO se la fonte la nomina (tabella GOV.UK, o la frase stessa).
  - Se si leggono meno dell'80 % delle pagine, dati/patenti.json NON viene sovrascritto (esce con 1). I testi cambiati rispetto al file
    precedente vanno in dati/patenti_cambi.json.
"""
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from html import unescape
from pathlib import Path
from zoneinfo import ZoneInfo

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import passaporti_au as AU  # noqa: E402  (parser delle pagine Smartraveller salvate)
import passaporti_ca as CA  # noqa: E402  (parser HTML a blocchi e cache dell'open data canadese)

RADICE = QUI.parent
DATI = RADICE / "dati"
CACHE = QUI / ".cache" / "patenti"
CACHE_CA = QUI / ".cache" / "ca"
CACHE_AU = QUI / ".cache" / "au"
OFFLINE = os.environ.get("BYF_OFFLINE") == "1"
CACHE_ORE = float(os.environ.get("BYF_CACHE_ORE", "20"))
UA = "BeforeYouFly-raccolta/1.0 (+https://before-you-fly.netlify.app/about/)"
QUOTA_MINIMA = 0.8
LONDRA = ZoneInfo("Europe/London")

GOVUK_GUIDA = "https://www.gov.uk/api/content/driving-abroad"
GOVUK_IDP = "https://www.gov.uk/driving-abroad/international-driving-permit"
GOVUK_GET = "https://www.gov.uk/driving-abroad/get-an-idp"
FCDO_API = "https://www.gov.uk/api/content/foreign-travel-advice"
FCDO_PAG = "https://www.gov.uk/foreign-travel-advice"
CA_IDP = "https://travel.gc.ca/travelling/documents/international-driving-permit"
CA_DATI = "https://data.international.gc.ca/travel-voyage/"
CA_PAG = "https://travel.gc.ca/destinations/"


# ------------------------------------------------------------------ download con cache (grezzi in raccolta/.cache/)
def scarica(url, file, json_=True):
    """Corpo della risposta (testo) da url, con cache su disco: riusa il file se ha meno di CACHE_ORE ore. Ritorna (testo, data_lettura)."""
    f = Path(file)
    if f.exists() and (OFFLINE or time.time() - f.stat().st_mtime < CACHE_ORE * 3600):
        return f.read_text(encoding="utf-8"), datetime.fromtimestamp(f.stat().st_mtime).date().isoformat()
    if OFFLINE:
        raise FileNotFoundError(f"{f} non è in cache")
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json" if json_ else "text/html"})
    for tentativo in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                if r.status != 200:
                    raise RuntimeError(f"HTTP {r.status}")
                corpo = r.read()
            testo = corpo.decode("utf-8")
            if json_:
                json.loads(testo)
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(corpo)
            return testo, date.today().isoformat()
        except Exception:  # noqa: BLE001
            if tentativo == 3:
                raise
            time.sleep(3 + tentativo * 4)


def data_uk(ts):
    """Data di una pagina GOV.UK nell'ora del Regno Unito (come raccolta/passaporti.py)."""
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(LONDRA).date().isoformat()


def scarica_tutto():
    """Scarica (o riprende dalla cache) tutti i grezzi. Ritorna un dizionario con i testi e le date di lettura."""
    out = {"uk": {}, "ca": {}, "errori": []}
    t, d = scarica(GOVUK_GUIDA, CACHE / "govuk-driving-abroad.json")
    out["guida"], out["guida_letto"] = json.loads(t), d
    t, d = scarica(CA_IDP, CACHE / "travel-gc-ca-idp.html", json_=False)
    out["ca_idp"], out["ca_idp_letto"] = t, d
    t, _ = scarica(FCDO_API, CACHE / "uk" / "_indice.json")
    figli = [c["base_path"].rsplit("/", 1)[-1] for c in json.loads(t)["links"]["children"]]
    out["uk_indice"] = len(figli)
    for slug in figli:
        try:
            t, d = scarica(f"{FCDO_API}/{slug}", CACHE / "uk" / f"{slug}.json")
            out["uk"][slug] = (json.loads(t), d)
        except Exception as e:  # noqa: BLE001
            out["errori"].append(f"FCDO {slug}: {e}")
        if not OFFLINE:
            time.sleep(0.15)
    t, _ = scarica(CA_DATI + "index-alpha-eng.json", CACHE_CA / "_indice.json")
    indice = json.loads(t)
    voci = indice["data"] if isinstance(indice.get("data"), dict) else indice
    isos = sorted(k for k in voci if re.fullmatch(r"[A-Z]{2}", k))
    out["ca_indice"] = len(isos)
    for iso in isos:
        try:
            t, d = scarica(f"{CA_DATI}cta-cap-{iso}.json", CACHE_CA / f"cta-cap-{iso}.json")
            out["ca"][iso] = (json.loads(t), d)
        except Exception as e:  # noqa: BLE001
            out["errori"].append(f"Canada {iso}: {e}")
        if not OFFLINE:
            time.sleep(0.15)
    return out


# ------------------------------------------------------------------ Paesi: nomi delle fonti -> codici ISO di dati/paesi_iso.json
def chiave(s):
    s = unicodedata.normalize("NFKD", unescape(s)).encode("ascii", "ignore").decode().lower().replace("&", " and ")
    s = re.sub(r"[^a-z ]", " ", s)
    s = re.sub(r"\b(the|st|saint)\b", lambda m: "saint" if m.group(1) in ("st", "saint") else " ", s)
    return " ".join(s.split())


ISO = {p["iso2"]: p for p in json.loads((DATI / "paesi_iso.json").read_text(encoding="utf-8"))["paesi"]}
PER_CHIAVE = {}
for _p in ISO.values():
    for _n in [_p["nome"]] + _p["alias"]:
        PER_CHIAVE.setdefault(chiave(_n), _p["iso2"])
# nomi delle fonti e delle ricerche che non sono in paesi_iso.json (controllati a mano il 28/10/2026)
NOMI_EXTRA = {
    "spain including balearic and canary isles": "ES", "congo": "CG", "cote d ivoire ivory coast": "CI", "saint vincent": "VC",
    "u s": "US", "u s a": "US", "united states": "US", "us": "US", "usa": "US", "america": "US", "uk": "GB", "u k": "GB",
    "england": "GB", "scotland": "GB", "wales": "GB", "northern ireland": "GB", "dubai": "AE", "abu dhabi": "AE", "bali": "ID",
    "korea": "KR", "south korea": "KR", "holland": "NL", "czech republic": "CZ", "turkiye": "TR", "the bahamas": "BS",
    "tenerife": "ES", "mallorca": "ES", "majorca": "ES", "canary islands": "ES", "ibiza": "ES", "lanzarote": "ES", "madeira": "PT",
    "crete": "GR", "corfu": "GR", "rhodes": "GR", "zante": "GR", "sicily": "IT", "sardinia": "IT", "hawaii": "US", "florida": "US",
    "california": "US", "new york": "US", "phuket": "TH", "hong kong": "HK", "macau": "MO", "macao": "MO", "puerto rico": "PR",
    "republic of ireland": "IE", "bosnia": "BA", "kosovo": "XK", "vatican city": "VA", "east timor": "TL", "timor leste": "TL",
    "burma": "MM", "swaziland": "SZ", "eswatini": "SZ", "cabo verde": "CV",
}
for _k, _v in NOMI_EXTRA.items():
    PER_CHIAVE[chiave(_k)] = _v


def iso_di(nome):
    """Codice ISO di un nome; prova anche senza la parte tra parentesi e con la sola parte tra parentesi ("Myanmar (previously Burma)")."""
    for n in (nome, re.sub(r"\s*\(.*?\)", "", nome), *re.findall(r"\((?:previously )?(.*?)\)", nome)):
        c = PER_CHIAVE.get(chiave(n.replace("’", "'")))
        if c:
            return c
    return None


# ------------------------------------------------------------------ domanda: autocompletamento di Google
SUGGEST = "https://suggestqueries.google.com/complete/search?client=firefox&gl=%s&hl=en&q=%s"
MODELLI_DOMANDA = ["do i need an international driving permit for", "do i need an idp for", "international driving permit for",
                   "can i drive in", "do i need an international driving licence for", "driving in"]
GL_DOMANDA = ["uk", "us", "ca", "au"]
LETTERE = [""] + list("abcdefghijklmnopqrstuvwxyz")
# patente nominata nella ricerca
_LIC = r"\s+(?:driving\s+|driver'?s\s+|drivers\s+|driver\s+)?licen[cs]e"
RX_PAT = {
    "uk": re.compile(r"\b(?:uk|british|english|gb|scottish|welsh|northern irish)" + _LIC + r"|\bfrom (?:the )?(?:uk|england|scotland|wales|britain)\b|\bas a (?:brit|uk)", re.I),
    "ca": re.compile(r"\b(?:canadian|ontario|bc|alberta|quebec|g2|g)" + _LIC + r"|\bfrom canada\b|\bas an? canadian\b|\bcanadians?\b", re.I),
    "au": re.compile(r"\b(?:australian|aus|nsw|victorian|queensland|qld|vic)" + _LIC + r"|\bfrom australia\b|\bas an? australian\b|\baustralians?\b", re.I),
    "altra": re.compile(r"\b(?:us|american|usa|indian|irish|nz|new zealand|south african|eu|european|international|foreign|german|french|"
                        r"italian|spanish|dutch|filipino|philippine|pakistani|nigerian|chinese|japanese|g1|full|provisional|learner|learners|"
                        r"p|p1|p2|l|digital|expired|suspended|car|motorcycle|my|a|an)" + _LIC + r"|\bfrom (?:the )?(?:us|usa|america|india|ireland)\b|"
                        r"\bas an? (?:american|us citizen|tourist|foreigner)\b", re.I),
}
MERCATO = {"uk": "uk", "ca": "ca", "au": "au"}  # ricerca senza patente nominata: la patente del Paese da cui si cerca


def destinazione(q, prefisso):
    """Paese di destinazione della ricerca: il nome che segue il modello (dopo 'for' / 'in'), fino a 'with', 'from', 'as', 'on', 'if'..."""
    resto = q[len(prefisso):].strip() if q.startswith(prefisso) else q
    resto = re.split(r"\b(?:with|from|as|on|using|if|for|without|when|while|by|after|reddit|20\d\d|uk licen[cs]e)\b", resto)[0]
    resto = re.sub(r"\b(?:the|a|an)\b", " ", resto).strip()
    if not resto:
        return None
    return iso_di(resto)


def domanda():
    """Ricerche vere che chiedono del permesso o della patente in un Paese: (patente, Paese) -> ricerche. Scrive dati/patenti_domanda.json."""
    out = {"uk": {}, "ca": {}, "au": {}}
    lette = 0
    for m in MODELLI_DOMANDA:
        for gl in GL_DOMANDA:
            for lettera in LETTERE:
                q = m + " " + lettera
                try:
                    url = SUGGEST % (gl, urllib.parse.quote(q))
                    req = urllib.request.Request(url, headers={"User-Agent": UA})
                    with urllib.request.urlopen(req, timeout=20) as r:
                        sugg = json.loads(r.read().decode("utf-8", "replace"))[1]
                    lette += 1
                except Exception as e:  # noqa: BLE001  (una richiesta persa non ferma la raccolta)
                    print(f"  autocompletamento {gl} {q!r}: {e}")
                    continue
                for x in sugg:
                    x = x.strip().lower()
                    if not x.startswith(m + " "):
                        continue
                    if m == "driving in" and not re.search(r"licen[cs]e|permit|\bidp\b", x):
                        continue  # "driving in france" da solo parla anche di regole della strada: conta solo se nomina patente o permesso
                    c = destinazione(x, m)
                    if not c:
                        continue
                    pat = [k for k in ("uk", "ca", "au") if RX_PAT[k].search(x)]
                    if not pat and not RX_PAT["altra"].search(x) and gl in MERCATO:
                        pat = [MERCATO[gl]]
                    for k in pat:
                        if {"uk": "GB", "ca": "CA", "au": "AU"}[k] == c:
                            continue  # guidare nel proprio Paese: non è la domanda
                        lst = out[k].setdefault(c, [])
                        voce = f"{x} [gl={gl}]"
                        if voce not in lst:
                            lst.append(voce)
                time.sleep(0.25)
    doc = {"_nota": "Ricerche vere (autocompletamento di Google, client=firefox, hl=en) sul permesso internazionale o sulla patente in un Paese. "
                    "Una pagina Paese × patente esiste solo per queste coppie. Senza patente nominata, la ricerca vale per la patente del Paese "
                    "da cui si cerca (gl=uk -> britannica, gl=ca -> canadese, gl=au -> australiana; gl=us solo se la ricerca nomina la patente). "
                    "Riscritto da raccolta/patenti.py --domanda.",
           "letto_il": date.today().isoformat(), "modelli": MODELLI_DOMANDA, "gl": GL_DOMANDA, "lettere": "a-z dopo il modello",
           "richieste_lette": lette, "patenti": {k: dict(sorted(v.items())) for k, v in out.items()}}
    doc["pagine"] = pagine_domanda(doc)
    (DATI / "patenti_domanda.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("domanda:", {k: len(v) for k, v in out.items()}, "richieste:", lette, "pagine:", {k: len(v) for k, v in doc["pagine"].items()})


def pagine_domanda(doc):
    """Coppie Paese × patente con una pagina: almeno una ricerca che NOMINA quella patente ("from uk", "canadian license", "as an australian").
    Le ricerche senza patente nominata (es. "do i need an idp for kyrgyzstan" con gl=ca) tornano quasi uguali da ogni Paese: non bastano."""
    out = {}
    for pat, per in doc["patenti"].items():
        out[pat] = sorted(c for c, qq in per.items() if any(RX_PAT[pat].search(q.split(" [gl=")[0]) for q in qq))
    return out


# ------------------------------------------------------------------ testo: blocchi -> "affermazioni"
def piano(s):
    """Testo per i confronti: apostrofi e virgolette dritte, spazi singoli."""
    return re.sub(r"\s+", " ", s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')).strip()


RX_PERTINENTE = re.compile(r"\blicen[cs]es?\b(?! plates?)|\bIDPs?\b|driving permit|driver'?s permit|translation", re.I)


def affermazioni(bb):
    """Raggruppa i blocchi: un paragrafo che finisce con ':' si unisce alle voci di elenco che lo seguono ('To drive, you need both: a valid
    Australian driver's licence; an International Driving Permit (IDP)'). Ritorna [(testo_unito, [blocchi originali])]."""
    out, i = [], 0
    while i < len(bb):
        b = bb[i]
        if b["t"] in ("h2", "h3", "h4"):
            i += 1
            continue
        gruppo = [b]
        if b["x"].rstrip().endswith(":") or (not re.search(r"[.!?)]$", b["x"].rstrip()) and i + 1 < len(bb) and bb[i + 1]["t"] == "li"):
            j = i + 1
            # voci dell'elenco: <li>, o <p> dentro <li> (Smartraveller, es. Macau) che il parser registra come paragrafi senza punto finale
            while j < len(bb) and (bb[j]["t"] == "li" or (bb[j]["t"] == "p" and b["x"].rstrip().endswith(":") and len(bb[j]["x"]) < 200
                                                          and not re.search(r"[.!?:]$", bb[j]["x"].rstrip()))):
                gruppo.append(bb[j])
                j += 1
            i = j
        else:
            i += 1
        testo = gruppo[0]["x"] + ("" if len(gruppo) == 1 else " " + "; ".join(g["x"] for g in gruppo[1:]))
        out.append((testo, gruppo))
    return out


def pertinenti(bb):
    """Solo i gruppi sulla patente o sul permesso (le altre righe sulla guida: assicurazione, alcol, strade, restano fuori)."""
    return [(t, g) for t, g in affermazioni(bb) if RX_PERTINENTE.search(t) and not re.match(r"^(More information|More about)", t)
            and not (re.search(r"\btaxis?\b|\bride-hailing\b", t, re.I) and not re.search(r"\bIDPs?\b|driving permit|(?:UK|Canadian|Australian)(?: photocard)?(?: driving| driver[’']?s)? licen", t))]
    # i "licensed taxis" non sono la patente: fuori, salvo che la stessa frase parli del permesso o della patente del lettore


def frasi(testo):
    """Frasi di un gruppo (un elenco unito con ':' resta una frase sola)."""
    t = testo.replace("U.S.", "U․S․").replace("e.g.", "e․g․").replace("i.e.", "i․e․")
    return [x.strip().replace("U․S․", "U.S.").replace("e․g․", "e.g.").replace("i․e․", "i.e.")
            for x in re.split(r"(?<=[.!?])\s+(?=[A-Z])", t) if x.strip()]


# ------------------------------------------------------------------ classificazione di una frase (schemi fissi)
RX_IDP = re.compile(r"international driv(?:ing|er'?s?) (?:permit|licen[cs]e)|\bIDPs?\b", re.I)
RX_NEG = re.compile(r"(?:do not|don't|does not|doesn't|not|won't|will not|no) (?:need|require|requirement)[^.;]{0,40}?(?:international driv|\bIDP\b)|"
                    r"(?:international driv\w* \w+|\bIDP\b)(?: \(IDP\))? (?:isn't|is not|aren't|are not) (?:required|needed|necessary)|"
                    r"\b(?:can|may) (?:legally )?(?:drive|use)[^.;]{0,80}without an? (?:IDP|international driv)", re.I)
RX_OBBL = re.compile(r"\b(?:must|need|needs|needed|required|require|requires|have to|has to|will need|obligatory|mandatory)\b|'ll need|'ll require|\byou need\b", re.I)
RX_COND = re.compile(r"\bif you(?:'re| are)? (?:stay|intend to stay|plan to stay|remain)|\bfor (?:stays|periods|visits|trips) (?:of )?(?:longer|more) than|"
                     r"\b(?:longer|more) than (?:\d|one|two|three|four|six|a )|\bbeyond \d|\bafter (?:\d|one|two|three|four|six|the first|that)|\bup to (?:\d|one|two|three|four|six|twelve|a )|"
                     r"\bfirst \d+|\bfirst (?:one|two|three|four|six|month|year)|\bfor (?:\d+|one|two|three|four|six|twelve) (?:days?|months?|weeks?|years?)|\bfor (?:a|one) (?:month|year)\b|"
                     r"\bfor a period of\b|\bperiod not exceeding|\bexcept\b|"
                     r"\bwithin \d|\bexceeding|\bfor a (?:maximum|limited time)|\bmaximum of\b|\bduring (?:the|your) first|\bstaying longer|\blength of your stay|"
                     r"\bpermitted length of stay|\bshort visits?\b|\bsingle stay|\blonger stays?\b|\bbeyond this period|\bafter this period|\bstaying less than", re.I)
RX_TRAD = re.compile(r"translat|notari[sz]ed|certified (?:\w+ )?copy", re.I)
RX_NOLEGGIO = re.compile(r"\b(?:rent|rental|hire|hiring)\b", re.I)
RX_DEBOLE = re.compile(r"\b(?:should|recommend|recommended|advisable|advised|strongly|good idea|consider|helpful|useful)\b", re.I)
RX_FORSE = re.compile(r"\b(?:may|might|some|can|could|often)\b", re.I)
RX_PROPRIA = {"uk": r"(?:uk|british|great britain|gb|northern ireland)(?: photocard)?(?: driving| driver'?s)? licen[cs]e",
              "ca": r"canadian(?: driver'?s| driving| drivers| driver)? licen[cs]e", "au": r"australian(?: driver'?s| driving| drivers| driver)? licen[cs]e"}
RX_PUO = re.compile(r"\b(?:can|may) (?:legally )?(?:drive|use)\b|\bare accepted\b|\bis accepted\b|\bwill be accepted\b|\bcan be used\b|\bare valid\b|\bis valid\b", re.I)
RX_LOCALE = re.compile(r"\b(?:local|temporary|visitor'?s?|recognition|tourist|special)\b[^.;]{0,25}\b(?:permit|licen[cs]e)\b", re.I)
# frasi che riguardano altri casi (patente cartacea britannica, residenti, chi si trasferisce, assicurazione, alcol): non decidono l'esito
RX_ALTRI_CASI = re.compile(r"\bpaper (?:UK )?(?:driving )?licen|^if you(?:'re| are)? (?:a )?(?:resident|residing|living|registered as a resident|take up)|"
                           r"\bif you live\b|\bif you move\b|\bif you(?:'re| are)? moving\b|\bpermanent (?:visa|resident)|^long-term|\bresidents? (?:may|must|can|need)\b|"
                           r"\bnew residents\b|\bresidence permit|\bapplies? for residence|\bresiding in\b|\bif you become a resident|^(?:to |if you want to )?(?:drive|ride) a (?:motorbike|motorcycle|scooter|boat)|"
                           r"\bdigital (?:driver'?s )?licen", re.I)
RX_CONV = re.compile(r"\b(1926|1949|1968)\b")


RX_INSIEME = re.compile(r"(?:\band|alongside|along with|accompanied by|together with|plus)\s+(?:an?|the|your)?\s*(?:valid\s+)?(?:IDP|international driv)|"
                        r"\bwith an? (?:valid )?(?:IDP|international driv\w* \w+(?: \(IDP\))?) and\b", re.I)


def etichetta_frase(t, pat):
    """Etichetta di UNA frase: si / no / dipende / durata / consigliato / noleggio / locale / info. Solo schemi fissi; nel dubbio "info".
    "durata" = la patente propria basta per un periodo (es. "You can drive ... with your valid Canadian driver's licence for up to 6 months")."""
    t = re.sub(r"\s*\([^()]*\bdigital\b[^()]*\)", "", piano(t))  # "(digital driver's licences may not be accepted)": inciso, non un altro caso
    if RX_ALTRI_CASI.search(t):
        return "info"
    idp = bool(RX_IDP.search(t))
    propria = re.search(RX_PROPRIA[pat], t, re.I)
    if idp:
        if RX_NEG.search(t):
            return "dipende" if RX_COND.search(t) else "no"
        if re.search(r"\b(?:is|are) (?:also )?accepted\b|\bnot recogni[sz]ed\b|\bnot accepted\b|\bnot valid\b", t, re.I):
            return "info"  # IDP accettato / non riconosciuto: lo dice la citazione, l'esito lo decide un'altra frase o il fatto manuale
        if re.search(r"\brecommend", t, re.I) and not re.search(r"\bmust\b", t, re.I):
            return "dipende" if RX_COND.search(t) else "consigliato"
        if RX_NOLEGGIO.search(t) and (RX_FORSE.search(t) or re.search(r"\bto (?:rent|hire)\b|car hire|rental compan", t, re.I)) and not re.search(r"\bto (?:rent or )?drive\b|drive and rent|rent or drive", t, re.I):
            return "noleggio"
        if RX_DEBOLE.search(t) and not re.search(r"\bmust\b", t, re.I):
            return "dipende" if RX_COND.search(t) else "consigliato"
        if propria and RX_PUO.search(t):
            if RX_TRAD.search(t):
                return "dipende"
            if RX_INSIEME.search(t) and not re.search(r"\bor (?:an? |the |with an? )?(?:IDP|international)", t, re.I):
                return "si"  # "You can drive ... with your licence and an IDP for up to 6 months": per la visita serve l'IDP
            return "dipende" if RX_COND.search(t) else "info"
        if RX_OBBL.search(t) or re.search(r"\bneed both|\bneed either|\bmust hold|\bmust carry|\bmust have|\bmust get|\bmust obtain", t, re.I):
            if re.search(r"\bmay need\b|\bmight need\b|\bmay require\b|\bmay ask\b|\bcould need\b", t, re.I):
                return "dipende"
            if RX_TRAD.search(t) or RX_COND.search(t):
                return "dipende"
            if re.search(r"^(?:you must |you should |you need to |make sure you )?(?:get|obtain|buy|apply for) (?:your|an|the) (?:IDP|international)[^.]*\b(?:before|in australia|in canada|in the uk|outside)", t, re.I):
                return "info"  # dove procurarsi il permesso: non dice se serve
            return "si"
        return "info"
    if propria and RX_PUO.search(t) and not re.search(r"\bnot\b|\bcannot\b|\bcan't\b", t, re.I):
        if RX_TRAD.search(t) or re.search(r"\bif\b|\bprovided\b|\bas long as\b|\bonly\b", t, re.I):
            return "dipende"
        return "durata" if RX_COND.search(t) else "no"
    if RX_LOCALE.search(t) and RX_OBBL.search(t) and not RX_COND.search(t):
        return "locale"
    return "info"


def combina(etichette):
    """Esito della fonte per un Paese dalle etichette delle sue frasi. Combinazioni non previste -> 'da_leggere' (fatto manuale)."""
    e = set(etichette) - {"info"}
    if not etichette:
        return "non_detto"
    if not e:
        return "non_detto_frasi"  # frasi sulla patente, ma nessuna dice se serve il permesso
    if "locale" in e:
        return "da_leggere"
    e2 = e - {"noleggio"}
    if not e2:
        return "solo_noleggio"
    if e2 == {"si"}:
        return "si"
    if e2 == {"no"}:
        return "no"
    if e2 <= {"dipende", "durata"}:
        return "dipende"
    if e2 == {"consigliato"} or e2 == {"consigliato", "no"} or e2 == {"consigliato", "durata"}:
        return "consigliato"
    return "da_leggere"


# ------------------------------------------------------------------ Regno Unito: tabella GOV.UK + "Road travel" FCDO
def testo_html(s):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", s))).replace(" .", ".").replace(" ,", ",").strip()


def tabella_uk(guida):
    """Righe della tabella "Country or territory / Type of IDP / More information" della parte international-driving-permit."""
    parte = next(p for p in guida["details"]["parts"] if p["slug"] == "international-driving-permit")
    righe = []
    for r in re.findall(r"<tr>(.*?)</tr>", parte["body"], re.S):
        c = [testo_html(x) for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
        if len(c) == 3 and c[0] != "Country or territory":
            righe.append({"nome": c[0], "tipo": c[1], "nota": c[2]})
    return righe


def frasi_parte(guida, slug):
    parte = next(p for p in guida["details"]["parts"] if p["slug"] == slug)
    return [b["x"] for b in CA.blocchi(parte["body"])]


# Note della tabella GOV.UK -> esito per chi ha una patente britannica con foto (il lettore della pagina). Frasi fisse, la prima che corrisponde
# all'INIZIO della nota decide; nota vuota = il Paese è in tabella con il tipo di IDP e senza eccezioni = serve l'IDP di quel tipo.
NOTE_UK = [
    (r"^You do not need an IDP\b", "no", "nota: You do not need an IDP"),
    (r"^You can use a UK(?:, Gibraltar|, Guernsey|, Jersey|,? or Isle of Man|,? or Jersey|,? or Guernsey)* photocard (?:driving )?licence (?:to drive )?without an IDP", "no", "nota: You can use a UK photocard licence without an IDP"),
    (r"^You can use a UK(?:, Gibraltar|, Guernsey|, Jersey|,? or Isle of Man|,? or Jersey|,? or Guernsey)* photocard (?:driving )?licence (?:to drive )?(?:for )?(?:periods )?up to \d+ (?:days|months)(?: in any 180-day period)? without an IDP", "dipende", "nota: without an IDP for up to N"),
    (r"^IDP needed for stays longer than \d+ days\.", "dipende", "nota: IDP needed for stays longer than N days"),
    (r"^IDP needed for car hire(?:, and for stays longer than \d+ days)?\.", "dipende", "nota: IDP needed for car hire"),
    (r"^As well as the IDP, you must get", "si", "nota: As well as the IDP"),
    (r"^You should check if the individual state authority says you need an IDP", "dipende", "nota: check the individual state authority"),
]


def esito_tabella_uk(riga):
    if not riga["nota"]:
        return "si", "tabella: tipo di IDP senza eccezioni"
    for rx, esito, nome in NOTE_UK:
        if re.search(rx, riga["nota"]):
            return esito, nome
    return "da_leggere", None


RX_STRADA_UK = re.compile(r"^(?:Road travel|Road safety|Driving\b.*|Licen[cs]es? and (?:driving )?permits|Self-drive.*)$", re.I)


def road_travel_uk(j):
    """Blocchi sulla guida della parte "Safety and security" dei consigli FCDO: tutta la sezione h2 "Transport risks" (dove sta di solito la
    sottosezione "Road travel"; in alcune pagine, es. Qatar, il testo è direttamente sotto h2) e ogni sottosezione h3/h4 sulla guida
    ("Road travel", "Driving licence and permit requirements"...) anche fuori da quella sezione."""
    for p in j["details"].get("parts", []):
        if not p["slug"].endswith("safety-and-security"):
            continue
        bb = CA.blocchi(p["body"])
        out, in_h2, in_h3 = [], False, False
        for b in bb:
            if b["t"] == "h2":
                in_h2 = bool(re.match(r"^Transport risks?$|^Road (?:travel|safety)$|^Driving", b["x"], re.I))
                in_h3 = False
                if in_h2:
                    out.append(b)
                continue
            if b["t"] in ("h3", "h4"):
                if b["t"] == "h3":
                    in_h3 = bool(RX_STRADA_UK.match(b["x"]))
                if in_h2 or in_h3:
                    out.append(b)
                continue
            if in_h2 or in_h3:
                out.append(b)
        return out
    return []


# pagine FCDO che coprono più territori o con un nome diverso da paesi_iso.json (controllate a mano il 28/10/2026)
FCDO_ISO = {"bonaire-st-eustatius-saba": ["BQ"], "st-martin-and-st-barthelemy": ["MF", "BL"], "antarctica-british-antarctic-territory": [], "cook-islands-tokelau-and-niue": ["CK", "TK", "NU"], "st-helena-ascension-and-tristan-da-cunha": ["SH"],
            "the-occupied-palestinian-territories": ["PS"], "british-antarctic-territory": [], "antarctica": [], "south-georgia-and-the-south-sandwich-islands": ["GS"],
            "british-indian-ocean-territory": ["IO"], "pitcairn-island": ["PN"], "usa": ["US"], "democratic-republic-of-the-congo": ["CD"], "congo": ["CG"],
            "ivory-coast": ["CI"], "st-maarten": ["SX"], "st-martin": ["MF"], "st-pierre-and-miquelon": ["PM"], "st-barthelemy": ["BL"],
            "north-korea": ["KP"], "south-korea": ["KR"], "macao": ["MO"], "hong-kong": ["HK"], "timor-leste": ["TL"], "eswatini": ["SZ"],
            "the-gambia": ["GM"], "micronesia": ["FM"], "turks-and-caicos-islands": ["TC"], "british-virgin-islands": ["VG"], "kosovo": ["XK"],
            "vatican-city": ["VA"], "cape-verde": ["CV"], "laos": ["LA"], "burma": ["MM"], "syria": ["SY"], "iran": ["IR"], "russia": ["RU"],
            "moldova": ["MD"], "tanzania": ["TZ"], "venezuela": ["VE"], "bolivia": ["BO"], "brunei": ["BN"], "vietnam": ["VN"], "turkey": ["TR"],
            "czech-republic": ["CZ"], "north-macedonia": ["MK"], "st-kitts-and-nevis": ["KN"], "st-lucia": ["LC"], "st-vincent-and-the-grenadines": ["VC"],
            "taiwan": ["TW"], "palestine": ["PS"], "israel": ["IL"], "uk": ["GB"]}


def iso_fcdo(slug, nome):
    if slug in FCDO_ISO:
        return FCDO_ISO[slug]
    c = iso_di(nome) or iso_di(slug.replace("-", " "))
    return [c] if c else None


RIGHE_REGIONE = {"Malaysia (Sabah)": "MY"}


def gruppi(aff, pat):
    """Gruppi pertinenti con le loro frasi etichettate: [{"blocchi": [...], "frasi": [{"x": frase, "e": etichetta}]}]."""
    return [{"blocchi": g, "frasi": [{"x": x, "e": etichetta_frase(x, pat)} for x in frasi(t)]} for t, g in aff]


def etichette(v):
    return [f["e"] for g in v.get("gruppi", []) for f in g["frasi"]]


def leggi_uk(grezzi):
    """Per ISO: riga della tabella, frasi FCDO, esiti. Ritorna (per_iso, avvisi)."""
    avvisi = []
    guida, letto = grezzi["guida"], grezzi["guida_letto"]
    righe = tabella_uk(guida)
    tab = {}
    for r in righe:
        if r["nome"] in RIGHE_REGIONE:
            continue  # riga per una regione (Sabah): mostrata nella pagina del Paese, non come Paese
        c = iso_di(r["nome"])
        if not c:
            avvisi.append(f"tabella GOV.UK: nome non riconosciuto {r['nome']!r}")
            continue
        tab[c] = r
    out = {}
    for slug, (j, d) in grezzi["uk"].items():
        isos = iso_fcdo(slug, j.get("title", slug))
        if isos is None:
            avvisi.append(f"FCDO: pagina {slug!r} ({j.get('title')}) senza codice ISO")
            continue
        bb = road_travel_uk(j)
        aff = pertinenti(bb)
        for c in isos:
            out[c] = {"slug_fcdo": slug, "nome_fcdo": j.get("title"), "url": f"{FCDO_PAG}/{slug}/safety-and-security",
                      "aggiornata": data_uk(j["public_updated_at"]), "letto_il": d, "titolo_sezione": bb[0]["x"] if bb else None,
                      "gruppi": gruppi(aff, "uk")}
    for c, r in tab.items():
        out.setdefault(c, {"slug_fcdo": None, "nome_fcdo": None, "url": None, "aggiornata": None, "letto_il": None, "titolo_sezione": None, "gruppi": []})
        out[c]["tabella"] = r
    for r in righe:
        if r["nome"] in RIGHE_REGIONE and RIGHE_REGIONE[r["nome"]] in out:
            out[RIGHE_REGIONE[r["nome"]]]["tabella_regione"] = r
    return out, avvisi, {"guida_aggiornata": data_uk(guida["public_updated_at"]), "guida_letta": letto, "righe_tabella": len(righe),
                         "get_idp": frasi_parte(guida, "get-an-idp"), "intro_idp": frasi_parte(guida, "international-driving-permit")[:12]}


# ------------------------------------------------------------------ Canada: scheda "Laws and culture", titolo "Driving"
def driving_ca(html):
    """Blocchi dal titolo h3 "Driving" (o "Driving ...") al titolo h3 successivo, nella scheda "Laws and culture"."""
    bb = CA.blocchi(html or "")
    out, on = [], False
    for b in bb:
        if b["t"] in ("h2", "h3"):
            on = bool(re.match(r"^(?:Driving|Road travel|Drivers?'? licen)", b["x"], re.I))
            if on:
                out.append(b)
            continue
        if on:
            out.append(b)
    return out


CA_SALTA = {"IC"}  # Canary Islands: scheda canadese a parte, non un Paese ISO (la Spagna ha la sua)


def leggi_ca(grezzi):
    out, avvisi = {}, []
    for iso, (j, d) in grezzi["ca"].items():
        e = j["data"]["eng"]
        if iso in CA_SALTA:
            continue
        if iso not in ISO:
            avvisi.append(f"Canada: codice {iso} non in paesi_iso.json")
            continue
        bb = driving_ca(e.get("laws-culture"))
        aff = pertinenti(bb)
        m = re.match(r"(\w+ \d+, \d{4})", e.get("friendly-date") or "")
        agg = datetime.strptime(m.group(1), "%B %d, %Y").date().isoformat() if m else None
        out[iso] = {"nome_fonte": e["name"], "url": f"{CA_PAG}{e['url-slug']}#laws", "aggiornata": agg, "letto_il": d,
                    "titolo_sezione": bb[0]["x"] if bb else None, "gruppi": gruppi(aff, "ca")}
    return out, avvisi


# ------------------------------------------------------------------ Australia: sezione "Travel", sottosezione "Local travel"
RX_TIT_AU = re.compile(r"driv|licen[cs]|international driving", re.I)
RX_TIT_AU_NO = re.compile(r"road|safety|condition|drink|insurance|summer|winter|highland|kokoda|travel permit", re.I)


def driving_au(sez):
    """Blocchi della sottosezione "Local travel" sotto i titoli sulla patente ("Driving permit", "Driver's licence"...); se non c'è un titolo
    così, le sole righe di "Local travel" che nominano il permesso internazionale o la patente australiana."""
    lt = sez.get("Local travel", [])
    out, on = [], False
    for b in lt:
        if b["t"] == "h4":
            on = bool(RX_TIT_AU.search(b["x"])) and not RX_TIT_AU_NO.search(b["x"])
            if on:
                out.append(b)
            continue
        if on:
            out.append(b)
    if not out:
        aff = affermazioni(lt)
        for t, g in aff:
            if RX_IDP.search(t) or re.search(RX_PROPRIA["au"], piano(t), re.I):
                out.extend(g)
    return out


def leggi_au(grezzi):
    out, avvisi = {}, []
    D = json.loads((DATI / "passaporti_au.json").read_text(encoding="utf-8"))
    for p in D["paesi"]:
        f = CACHE_AU / AU.nome_file(p["url"])
        if not f.exists():
            avvisi.append(f"Australia: pagina salvata mancante per {p['nome']}")
            continue
        iso = iso_di(p["nome"]) or AU_ISO.get(p["slug_fonte"])
        if not iso:
            avvisi.append(f"Australia: {p['nome']!r} senza codice ISO")
            continue
        html = f.read_text(encoding="utf-8")
        sez = AU.sezione_travel(AU.blocchi(html)) or {}
        bb = driving_au(sez)
        aff = pertinenti(bb)
        corrente, agg = AU.date_pagina(html)
        out[iso] = {"nome_fonte": p["nome"], "url": p["url"] + "#travel", "aggiornata": agg, "ancora_valida_il": corrente,
                    "letto_il": datetime.fromtimestamp(f.stat().st_mtime).date().isoformat(),
                    "titolo_sezione": next((b["x"] for b in bb if b["t"] == "h4"), None), "gruppi": gruppi(aff, "au")}
    return out, avvisi


AU_ISO = {}  # slug Smartraveller -> ISO, dove il nome non basta (riempito dopo il primo giro di controllo)


# ------------------------------------------------------------------ esito finale per fonte e Paese
DECISIVE = {"si", "no", "dipende", "durata", "consigliato", "noleggio", "locale"}
ENTI = {"uk": "GOV.UK", "ca": "the Government of Canada", "au": "Smartraveller"}


def testo_fonte(v):
    """Testo della fonte per l'impronta: frasi pertinenti (e, per il Regno Unito, la riga della tabella)."""
    parti = [b["x"] for g in v.get("gruppi", []) for b in g["blocchi"]]
    if v.get("tabella"):
        parti = [f"TABELLA: {v['tabella']['nome']} | {v['tabella']['tipo']} | {v['tabella']['nota']}"] + parti
    return "\n".join(parti)


def impronta(v):
    return hashlib.sha256(testo_fonte(v).encode("utf-8")).hexdigest()[:16]


def frasi_chiave(v):
    """Frasi che decidono l'esito; quelle sul solo noleggio solo se non ce ne sono altre."""
    tutte = [(f["x"], f["e"]) for g in v.get("gruppi", []) for f in g["frasi"]]
    ff = [x for x, e in tutte if e in DECISIVE - {"noleggio"}]
    return ff or [x for x, e in tutte if e == "noleggio"]


def convenzione_da(testi):
    cc = sorted({m.group(1) for t in testi for m in RX_CONV.finditer(t)})
    return cc[0] if len(cc) == 1 else None


def esito_auto(pat, v):
    """(esito, regola, frasi chiave, convenzione) dai soli schemi fissi. 'da_leggere' = serve un fatto manuale."""
    fc = combina([f["e"] for g in v.get("gruppi", []) for f in g["frasi"]])
    chiave_ = frasi_chiave(v)
    if pat != "uk":
        es = {"non_detto_frasi": "non_detto", "solo_noleggio": "da_leggere"}.get(fc, fc)
        return es, f"frasi: {fc}", chiave_, convenzione_da(chiave_)
    r = v.get("tabella")
    conv = r["tipo"] if r else convenzione_da(chiave_)
    te, regola_t = esito_tabella_uk(r) if (r and r["nota"]) else (None, None)
    decisivo_f = fc in ("si", "no", "dipende", "consigliato")
    if te and te != "da_leggere":
        if decisivo_f and fc != te:
            return "da_leggere", f"tabella ({te}) e FCDO ({fc}) diversi", chiave_, conv
        nota = frasi(r["nota"])[:1]  # la prima frase della nota della tabella è quella che decide
        return te, regola_t + (f"; FCDO: {fc}" if decisivo_f else ""), nota + (chiave_ if decisivo_f else []), conv
    if te == "da_leggere":
        return "da_leggere", "nota della tabella senza schema", chiave_, conv
    if decisivo_f:
        return fc, f"FCDO: {fc}" + ("; in tabella senza nota" if r else ""), chiave_, conv
    if fc in ("non_detto", "non_detto_frasi"):
        return ("non_detto", "solo tabella: tipo di IDP, nessuna frase sull'obbligo" if r else "FCDO: nulla sul permesso", chiave_, conv)
    return "da_leggere", f"FCDO: {fc}", chiave_, conv


MANUALI_F = DATI / "patenti_manuali.json"


def applica_manuali(pat, iso, v, auto, manuali, avvisi):
    """Il fatto scritto a mano vale solo se l'impronta del testo è quella da cui è stato scritto e se la frase citata c'è ancora."""
    m = manuali.get(pat, {}).get(iso)
    if not m:
        return auto + (None,)
    imp = impronta(v)
    if m["impronta"] != imp:
        avvisi.append(f"FATTO MANUALE SCADUTO {pat} {iso}: il testo della fonte è cambiato (impronta {imp}, scritto su {m['impronta']}): rileggere")
        return ("da_leggere", "manuale scaduto", auto[2], auto[3], None)
    # come in verifica.py: anche le frasi che introducono un elenco unite alle voci ("…: voce; voce"), così la citazione resta intera
    testo = piano(testo_fonte(v) + "\n" + "\n".join(t for t, _ in affermazioni([b for g in v.get("gruppi", []) for b in g["blocchi"]])))
    for x in m["frasi"]:
        if piano(x) not in testo:
            avvisi.append(f"FATTO MANUALE {pat} {iso}: la frase citata non è nel testo: {x[:80]!r}")
            return ("da_leggere", "manuale: frase non trovata", auto[2], auto[3], None)
    return (m["esito"], "manuale", m["frasi"], m.get("convenzione", auto[3]), m["motivo"])


# ------------------------------------------------------------------ frasi generali citate nelle pagine (devono esserci parola per parola)
FRASI_GENERALI = {
    "uk_paypoint": ("guida", "get-an-idp", "You can get an IDP in person from certain shops that have PayPoint."),
    "uk_costo": ("guida", "get-an-idp", "An IDP costs £5.50."),
    "uk_durata": ("guida", "get-an-idp", "A 1926 or 1949 permit lasts for 12 months. A 1968 permit lasts for 3 years or until your UK driving licence expires, whichever comes first."),
    "uk_requisiti": ("guida", "get-an-idp", "You must:"),
    "uk_tabella": ("guida", "international-driving-permit", "Check the table to find out if you need an IDP."),
    "uk_tipi": ("guida", "international-driving-permit", "The IDP you need depends on what country you’re visiting."),
    "uk_non_in_tabella": ("guida", "international-driving-permit", "If the country you’re visiting is not included in the table, check with the embassy of the country you’re travelling to."),
    "uk_noleggio": ("guida", "international-driving-permit", "If you’re hiring a car, check with your car hire company."),
    "uk_europa": ("guida", "international-driving-permit", "You do not need an IDP to drive in the EU, Switzerland, Norway, Iceland or Liechtenstein if you have a photocard driving licence issued in the UK."),
    "uk_sempre_patente": ("guida", "international-driving-permit", "You must always have your driving licence with you, as well as your IDP."),
    "ca_caa": ("ca_idp", None, "Contact the Canadian Automobile Association for a Canadian International Driving Permit application form."),
    "ca_usa": ("ca_idp", None, "Canadians with a provincial or territorial driver’s licence do not need an IDP to drive in the U.S."),
    "ca_anno": ("ca_idp", None, "The IDP is valid for only 1 year from the date of issue."),
    "ca_noleggio": ("ca_idp", None, "Some foreign car rental agencies may require you to have an IDP to rent a car."),
    "ca_classe": ("ca_idp", None, "Your IDP will only allow you to operate a vehicle in the same class as your Canadian driver’s licence."),
    "ca_controlla": ("ca_idp", None, "Check with your destination’s embassy or consulate in Canada or look under the Laws and culture tab of the Travel Advice and Advisory for your destination to find out if an IDP is required there."),
    "au_aaa": ("au_vn", None, "The Australian Automobile Association (AAA) and its member clubs are the only authorised distributors of IDPs for Australian licence holders."),
    "au_falsi": ("au_vn", None, "Fraudulent websites may claim to issue valid IDPs."),
}


def frasi_generali(grezzi):
    """Controlla che le frasi generali ci siano parola per parola; ritorna {chiave: frase} e l'elenco di quelle mancanti."""
    testi = {"ca_idp": testo_html(re.sub(r"<script.*?</script>|<style.*?</style>", " ", grezzi["ca_idp"], flags=re.S)).replace("&nbsp;", " ")}
    f_vn = CACHE_AU / "destinations_asia_vietnam.html"
    testi["au_vn"] = testo_html(f_vn.read_text(encoding="utf-8")) if f_vn.exists() else ""
    out, mancanti = {}, []
    for k, (fonte, parte, frase) in FRASI_GENERALI.items():
        if fonte == "guida":
            t = " ".join(frasi_parte(grezzi["guida"], parte))
        else:
            t = testi[fonte]
        if piano(frase) in piano(t.replace("\xa0", " ")):
            out[k] = frase
        else:
            mancanti.append(k)
    m = re.search(r"Date modified:.{0,200}?(\d{4}-\d{2}-\d{2})", grezzi["ca_idp"], re.S)
    out["ca_idp_modificata"] = m.group(1) if m else None
    return out, mancanti


# ------------------------------------------------------------------ scrittura di dati/patenti.json
def voce(pat, iso, v, manuali, avvisi):
    auto = esito_auto(pat, v)
    esito, regola, chiave_, conv, motivo = applica_manuali(pat, iso, v, auto, manuali, avvisi)
    testo = [{"t": b["t"], "x": b["x"]} for g in v.get("gruppi", []) for b in g["blocchi"]]
    out = {"esito": esito, "regola": regola, "frasi": chiave_, "convenzione": conv, "motivo": motivo, "testo": testo,
           "url": v.get("url"), "aggiornata": v.get("aggiornata"), "letto_il": v.get("letto_il"), "nome_fonte": v.get("nome_fonte") or v.get("nome_fcdo"),
           "titolo_sezione": v.get("titolo_sezione"), "impronta": impronta(v), "auto": auto[0]}
    for k in ("tabella", "tabella_regione", "ancora_valida_il", "slug_fcdo"):
        if v.get(k):
            out[k] = v[k]
    return out


def main():
    oggi = date.today().isoformat()
    if "--domanda" in sys.argv:
        domanda()
    elif "--pagine" in sys.argv:  # ricalcola solo le coppie con pagina dal file già scritto, senza rete
        f = DATI / "patenti_domanda.json"
        doc = json.loads(f.read_text(encoding="utf-8"))
        doc["pagine"] = pagine_domanda(doc)
        f.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        print("pagine:", {k: len(v) for k, v in doc["pagine"].items()})
        return
    grezzi = scarica_tutto()
    for e in grezzi["errori"]:
        print("  ERRORE", e)
    uk, a1, meta_uk = leggi_uk(grezzi)
    ca, a2 = leggi_ca(grezzi)
    au, a3 = leggi_au(grezzi)
    avvisi = a1 + a2 + a3
    generali, mancanti = frasi_generali(grezzi)
    letti = {"uk": len(grezzi["uk"]) / max(1, grezzi["uk_indice"]), "ca": len(grezzi["ca"]) / max(1, grezzi["ca_indice"]), "au": len(au) / 179}
    if any(q < QUOTA_MINIMA for q in letti.values()) or meta_uk["righe_tabella"] < 100 or mancanti:
        print(f"Lettura incompleta {letti}, righe della tabella GOV.UK {meta_uk['righe_tabella']}, frasi generali mancanti {mancanti}: "
              "dati/patenti.json NON aggiornato.")
        sys.exit(1)
    manuali = json.loads(MANUALI_F.read_text(encoding="utf-8")) if MANUALI_F.exists() else {}
    paesi = []
    for iso in sorted(set(uk) | set(ca) | set(au), key=lambda c: chiave(ISO[c]["nome"])):
        p = {"iso2": iso, "nome": ISO[iso]["nome"]}
        for pat, src in (("uk", uk), ("ca", ca), ("au", au)):
            p[pat] = voce(pat, iso, src[iso], manuali, avvisi) if iso in src else None
        paesi.append(p)
    nuovo = {
        "_nota": "Guidare all'estero con la patente britannica, canadese o australiana: serve il permesso internazionale (IDP)? Scritto da "
                 "raccolta/patenti.py. 'esito': si / no / dipende / consigliato / locale (serve un permesso o una patente del posto) / non_detto "
                 "(la fonte non dice nulla) / da_leggere (nessuno schema fisso e nessun fatto manuale: il sito mostra solo la citazione). "
                 "'frasi' = frasi della fonte che decidono l'esito (parola per parola); 'testo' = tutte le frasi della fonte sulla patente.",
        "controllato_il": oggi,
        "fonti": {
            "uk": {"ente": "GOV.UK", "pagina_idp": GOVUK_IDP, "pagina_get": GOVUK_GET, "api": GOVUK_GUIDA, "guida_aggiornata": meta_uk["guida_aggiornata"],
                   "letto_il": meta_uk["guida_letta"], "righe_tabella": meta_uk["righe_tabella"], "fcdo_api": FCDO_API, "fcdo_pagine": len(grezzi["uk"]),
                   "licenza": "Open Government Licence v3.0", "licenza_url": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"},
            "ca": {"ente": "Government of Canada", "pagina_idp": CA_IDP, "idp_modificata": generali.pop("ca_idp_modificata"), "letto_il": grezzi["ca_idp_letto"],
                   "dati": CA_DATI, "pagine": len(grezzi["ca"]), "licenza": "Open Government Licence – Canada",
                   "licenza_url": "https://open.canada.ca/en/open-government-licence-canada"},
            "au": {"ente": "Smartraveller (Australian Government, DFAT)", "pagine": len(au), "letto_dal": min(v["letto_il"] for v in au.values()),
                   "letto_al": max(v["letto_il"] for v in au.values()), "licenza": "Creative Commons Attribution 4.0",
                   "licenza_url": "https://creativecommons.org/licenses/by/4.0/", "pagina_aaa": "https://www.smartraveller.gov.au/destinations/asia/vietnam",
                   "nota": "Smartraveller chiude le richieste semplici: pagine lette con il browser da raccolta/passaporti_au.py (raccolta/.cache/au/)."},
        },
        "frasi_generali": generali,
        "paesi": paesi,
    }
    file = DATI / "patenti.json"
    if file.exists():
        vecchio = {p["iso2"]: p for p in json.loads(file.read_text(encoding="utf-8"))["paesi"]}
        cambi_f = DATI / "patenti_cambi.json"
        storico = json.loads(cambi_f.read_text(encoding="utf-8")) if cambi_f.exists() else {"cambi": []}
        n = 0
        for p in paesi:
            q = vecchio.get(p["iso2"])
            for pat in ("uk", "ca", "au"):
                a, b = (q or {}).get(pat), p[pat]
                if a and b and (a["impronta"] != b["impronta"] or a["esito"] != b["esito"]):
                    storico["cambi"].insert(0, {"rilevato_il": oggi, "iso2": p["iso2"], "patente": pat, "esito_prima": a["esito"], "esito_dopo": b["esito"],
                                                "testo_cambiato": a["impronta"] != b["impronta"]})
                    n += 1
        if n:
            cambi_f.write_text(json.dumps(storico, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Cambi rispetto al file precedente: {n}")
    file.write_text(json.dumps(nuovo, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    for pat in ("uk", "ca", "au"):
        print(pat, dict(Counter(p[pat]["esito"] for p in paesi if p[pat])))
    for a in avvisi:
        print("  AVVISO", a)
    if any(a.startswith("FATTO MANUALE") for a in avvisi):
        sys.exit(1)


if __name__ == "__main__":
    main()
