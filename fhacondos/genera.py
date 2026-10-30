"""Genera il sito statico FHA Approved Condos (inglese, pubblico USA) in fhacondos/sito/ da fhacondos/dati/.

Uso (dalla radice del repository):
    python3 fhacondos/raccolta/scarica.py   # pagine HTML del modulo HUD in fhacondos/cache/ (fuori da git)
    python3 fhacondos/raccolta/estrai.py    # dati puliti in fhacondos/dati/
    python3 fhacondos/genera.py             # pagine in fhacondos/sito/
    python3 fhacondos/verifica.py --browser # controlli prima di pubblicare

Dati (tutti dal modulo HUD FHA Condominium Lookup, vedi NOTE.md):
    dati/condomini.json  un oggetto per condominio: approvati (tipo A) + scaduti (E) e ritirati (W) negli ultimi 24 mesi
    dati/conteggi.json   totali dichiarati dal modulo per Stato e tipo, data "as of" di HUD, edizione della cache
    dati/affiliati.json  riquadro affiliati: nascosto finché non c'è un URL vero (mai inventarlo)

Pagine: home con ricerca nel browser (data/search.json), elenco degli Stati, una pagina per Stato, per contea e per città
sopra soglia (SOGLIA_CONTEA, SOGLIA_CITTA), 3 guide, methodology, about, contact, privacy, 404.
Non si pubblicano il testo libero "Composition of Project" né i commenti HUD (vedi raccolta/estrai.py).
"""
import hashlib
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from html import escape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
sys.path.insert(0, str(RADICE / "raccolta"))
from scarica import STATI as NOMI_STATI, MESI_RECENTI  # noqa: E402

URL_SITO = "https://fha-approved-condos-list.netlify.app"  # unico punto da cambiare se il nome del sito su Netlify è diverso
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti): non rimuoverlo

# Contatore visite GoatCounter, account condiviso "rete-siti" della rete (nessun cookie, nessun dato personale conservato).
# Il percorso inviato comprende l'host (location.host + percorso), così nel cruscotto https://rete-siti.goatcounter.com
# ogni sito si distingue dagli altri. Da localhost, da file:// e dalle reti private count.js non invia nulla
# (allow_local resta spento): le prove in locale non contano come visite. Unico punto da cambiare per tutto il sito.
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
# IndexNow (Bing, Yandex, Naver, Seznam): chiave pubblica uguale per tutti i siti della rete. Il generatore scrive
# sito/<chiave>.txt (contenuto: la chiave) accanto a robots.txt; l'invio degli URL lo fa studio-business/strumenti/indexnow.py.
CHIAVE_INDEXNOW = "b5a26a844a465f58552debee2c8a0114"
# Monetizzazione (30/10/2026): codice editore AdSense, elenco dei siti con la pubblicità e domini di affiliazione ammessi stanno
# in un solo file comune, studio-business/strumenti/monetizzazione.json (logica in monetizzazione.py). Con il codice vuoto o con
# questo sito fuori elenco non cambia nulla: niente script nel <head>, niente ads.txt, privacy di oggi.
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402
SITO_ID = "fhacondos"  # nome del sito in monetizzazione.json ("adsense_siti")
ADSENSE_HEAD = MON.script_adsense(SITO_ID)  # "" con AdSense spento; altrimenti a capo + script ufficiale, subito dopo il meta di verifica Google


def ci_sono_affiliati():
    """True se il sito pubblica almeno un link di affiliazione (voce con "url" in dati/affiliati.json):
    accende la sezione privacy sui link di affiliazione. Domini ammessi in monetizzazione.json, controlli in verifica.py."""
    return any(isinstance(v, dict) and v.get("url") for k, v in AFFILIATI.items() if not k.startswith("_"))


def riquadro_trasparenza(corpo, lingua="en"):
    """Riga di trasparenza sui link di affiliazione in fondo al contenuto della pagina ("Some links are affiliate links: ..."):
    vuota finché la pagina non ha link rel="sponsored" o se un riquadro di affiliazione la mostra già."""
    return MON.riga_trasparenza(corpo, lingua)


NOME = "ApprovedCondos"
HUD_LOOKUP = "https://entp.hud.gov/idapp/html/condlook.cfm"
FLOODCOST = "https://flood-insurance-cost.netlify.app"  # URL_SITO di floodcost/genera.py
FLOODCOST_SITO = RADICE.parent / "floodcost" / "sito"
# Fonti ufficiali citate nelle guide (lette il 17/10/2026)
CFR_FHA = "https://www.ecfr.gov/current/title-24/section-203.43b"
FR_2019 = "https://www.govinfo.gov/content/pkg/FR-2019-08-15/html/2019-17213.htm"  # 84 FR 41846-41877 (GPO)
USC_VA = "https://www.govinfo.gov/content/pkg/USCODE-2023-title38/html/USCODE-2023-title38-partIII-chap37-subchapII-sec3710.htm"
CFR_VA = "https://www.ecfr.gov/current/title-38/section-36.4360"
VA_PURCHASE = "https://www.va.gov/housing-assistance/home-loans/loan-types/purchase-loan/"
VA_CONDO = "https://lgy.va.gov/lgyhub/condo-report"
FANNIE_PROJECT = "https://selling-guide.fanniemae.com/sel/b4-2.1-01/general-information-project-standards"
CONTROLLO_FONTI = "2026-10-17"

# Soglie delle pagine (motivate in NOTE.md): sotto soglia il luogo resta nella tabella della pagina superiore e nella ricerca.
SOGLIA_CONTEA = 10   # condomini approvati in una contea per avere una pagina
SOGLIA_CITTA = 8     # condomini approvati in una città per avere una pagina
LIMITE_LISTA_STATO = 700  # oltre questo numero la pagina dello Stato elenca solo i condomini senza pagina di contea o città (California)
MESI_SCADENZA = 6    # "expiring soon": scadenza entro 6 mesi dalla data "as of" di HUD


def carica(nome):
    return json.loads((DATI / nome).read_text(encoding="utf-8"))


CONDOMINI = carica("condomini.json")
META = carica("conteggi.json")
AFFILIATI = carica("affiliati.json") if (DATI / "affiliati.json").exists() else {}
ASOF = date.fromisoformat(META["hud_as_of"])
ESTRATTO = META["estratto_il"][:10]
OGGI = date.today()
MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
MESI_B = ["Jan.", "Feb.", "March", "April", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."]


def piu_mesi(d, n):
    m = d.month - 1 + n
    a, m = d.year + m // 12, m % 12 + 1
    giorni = [31, 29 if a % 4 == 0 and (a % 100 != 0 or a % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    return date(a, m, min(d.day, giorni))


LIMITE_SOON = piu_mesi(ASOF, MESI_SCADENZA)
INIZIO_RECENTI = piu_mesi(ASOF, -MESI_RECENTI)


# ---------------------------------------------------------------- formati
def data_lunga(iso):
    d = date.fromisoformat(iso) if isinstance(iso, str) else iso
    return f"{MESI[d.month - 1]} {d.day}, {d.year}"


def data_breve(iso):
    """Data nelle meta description, stile AP: Oct. 17, 2026."""
    d = date.fromisoformat(iso) if isinstance(iso, str) else iso
    return f"{MESI_B[d.month - 1]} {d.day}, {d.year}"


def data_tab(iso):
    """Data nelle tabelle, stile americano breve: Mar 12, 2028."""
    if not iso:
        return "–"
    d = date.fromisoformat(iso)
    return f"{MESI[d.month - 1][:3]} {d.day}, {d.year}"


def mese_anno(d):
    return f"{MESI[d.month - 1][:3]} {d.year}"


def intero(x):
    return f"{x:,}"


def h(x):
    return escape(str(x))


def slug(t):
    t = t.lower().replace("&", " and ").replace("'", "").replace(".", "")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def plur(n, uno, molti=None):
    return f"{intero(n)} {uno if n == 1 else (molti or uno + 's')}"


ROMANI = {"IIA", "IIB", "IIC", "IIIA", "IIIB"}  # fasi con lettera; i numeri romani semplici li riconosce RE_ROMANO
RE_ROMANO = re.compile(r"^(?=[IVX]{2,5}$)X{0,3}(IX|IV|V?I{0,3})$")  # II, III, IV, VI, IX, XI, XXV (non "VIA", "DIX", "LIV")
SIGLE = {"LLC", "HOA", "PUD", "USA", "COA", "LP", "YMCA", "RV", "UOA", "POA", "CDA", "HPR", "CIC", "AA", "NE", "SE"}
DIREZIONI = {"N", "S", "E", "W", "NE", "NW", "SE", "SW"}
MINUSCOLE = {"aka", "of", "at", "the", "and", "on", "in", "by", "a", "an", "to", "for", "de", "del", "la", "las", "los", "el", "y"}
# parole senza vocali che sono abbreviazioni comuni (St, Rd, Blvd...): restano "Iniziale maiuscola"; le altre senza vocali sono
# sigle (NW, DC, TH, SM, CC...) e restano tutte maiuscole
ABBREVIAZIONI = {"st", "rd", "dr", "blvd", "pl", "ctr", "pk", "twp", "sq", "ct", "cr", "ln", "bldg", "bldgs", "mgmt", "bch", "crk", "cntr",
                 "lk", "sqr", "hll", "tr", "trl", "ck", "trst", "chrtr", "tnhms", "mt", "ph", "wd", "sp", "pkwy", "hwy", "hts", "cv", "pt",
                 "rdg", "mnr", "grv", "plz", "nr", "mr", "mrs", "jr", "sr", "rss", "brk", "frst", "mdws", "twnhs", "twnhms", "hs"}


def _parola(w, prima, modo, prec="", succ="", ultima=False):
    """modo: 'nome' (nomi dei condomini), 'via' (indirizzi), 'luogo' (città e contee)."""
    if not w:
        return w
    base = w.strip(".,()#'\"/-@").upper()
    if base in ROMANI or RE_ROMANO.match(base):
        return w.upper()
    if modo == "via" and base in DIREZIONI:
        return w.upper()
    if re.fullmatch(r"\d+(ST|ND|RD|TH)", base):
        return w.lower()  # 32ND -> 32nd, 1ST -> 1st
    if re.fullmatch(r"\d+[A-Z]{1,2}", base):
        return w.upper()  # 13A, 30A, 2B: numeri di edificio o di lotto
    if modo != "luogo":
        if base in SIGLE or (len(base) == 1 and base.isalpha() and base != "A"):
            return w.upper()
        if base == "A" and (succ in ("&", "/") or re.fullmatch(r"\d+", prec)):
            return w.upper()  # "15 A & B DAVID DRIVE": lettera, non articolo
        if modo == "nome" and base.isalpha() and 2 <= len(base) <= 5 and not re.search(r"[AEIOUY]", base) and base.lower() not in ABBREVIAZIONI:
            return w.upper()  # NW, DC, TH, SM, CC: sigle
    lw = w.lower()
    if not prima and not ultima and base.lower() in MINUSCOLE and not w.startswith("("):
        return lw
    if re.match(r"^\d", w):
        return lw
    if lw.startswith("mc") and len(lw) > 3 and lw[2].isalpha():
        return "Mc" + lw[2].upper() + lw[3:]
    if lw.startswith("o'") and len(lw) > 2:
        return "O'" + lw[2].upper() + lw[3:]
    # maiuscola a inizio parola e dopo trattino, barra, parentesi, punto o chiocciola: Ken-Caryl, A/B, T.H., (The)
    return re.sub(r"(^|[-/(.@])([a-z])", lambda m: m.group(1) + m.group(2).upper(), lw)


def titolo(s, modo="nome"):
    s = re.sub(r"\s+", " ", (s or "").replace("*", " ")).strip(" ,-")
    if modo == "nome":
        s = re.sub(r"\s*@\s*", " @ ", s)                # CARRIAGE HOMES@TOWN SQUARE -> Carriage Homes @ Town Square
        s = re.sub(r"(?<=[A-Za-z]{2})\.(?=[A-Za-z]{2,})", ". ", s)  # ST.MARY'S -> St. Mary's (ma T.H. resta T.H.)
    if modo == "luogo":
        s = re.sub(r"\bMC (?=[A-Z]{3})", "MC", s)        # MC LEAN -> McLean
    parole = [w for w in s.split(" ") if w]
    out = [_parola(w, i == 0, modo, parole[i - 1] if i else "", parole[i + 1] if i + 1 < len(parole) else "", i == len(parole) - 1)
           for i, w in enumerate(parole)]
    t = " ".join(out)
    if modo == "luogo":
        t = re.sub(r"^(Saint|St\.?) ", "St. ", t)        # stile AP: St. Louis, St. Petersburg, St. George
    return t


def nome_condo(raw):
    t = titolo(re.sub(r",(?=[A-Za-z])", ", ", raw or ""))
    t = re.sub(r"\bCondo\b\.?$", "Condo", t)
    return re.sub(r"#\s+(?=\d)", "#", t)  # "SHORES # 11" -> "Shores #11"


def via_bella(raw):
    return titolo(raw, "via") if raw else ""


# ---------------------------------------------------------------- luoghi
SUFFISSI_CONTEA = (" COUNTY", " PARISH", " BOROUGH", " CITY", " MUNICIPIO", " MUNICIPALITY", " CENSUS AREA", " DISTRICT")


def chiave_contea(raw, st=""):
    k = re.sub(r"\s+", " ", (raw or "").upper()).strip()
    if not k:
        return None
    k = re.sub(r" BOROUG$", " BOROUGH", k)  # il campo HUD è lungo al massimo 24 caratteri: "MATANUSKA-SUSITNA BOROUG"
    if st == "CT" and not k.endswith(SUFFISSI_CONTEA):
        k += " COUNTY"  # HUD scrive le contee del Connecticut senza "COUNTY" (HARTFORD, NEW HAVEN, ...)
    return k


def nome_contea(k):
    """BROWARD COUNTY -> Broward County; ALEXANDRIA CITY (città indipendente) -> City of Alexandria; CARSON CITY resta Carson City."""
    if k.endswith(" CITY") and k not in ("CARSON CITY",):
        return "City of " + titolo(k[:-5], "luogo")
    return titolo(k, "luogo")


def con_articolo(nome):
    """'in the City of Alexandria', ma 'in Fairfax County'."""
    return ("the " + nome) if nome.startswith("City of ") else nome


def chiave_citta(raw):
    k = re.sub(r"\s+", " ", (raw or "").upper().replace(".", " ")).strip()
    k = re.sub(r"\s+", " ", k)
    k = re.sub(r"^(ST|STE) ", "SAINT ", k)
    k = re.sub(r"^FT ", "FORT ", k)
    k = re.sub(r"^MT ", "MOUNT ", k)
    return k or None


NOMI_VISTA = {"DC": "Washington, DC", "VI": "U.S. Virgin Islands"}  # come si scrive nelle frasi (l'indirizzo resta quello di NOMI_STATI)


def nome_stato(st):
    return NOMI_VISTA.get(st) or NOMI_STATI.get(st, st)


def url_stato(st):
    return slug(NOMI_STATI.get(st, st)) + "/"


def prepara():
    """Normalizza i condomini e costruisce Stati, contee e città."""
    for c in CONDOMINI:
        c["nome"] = nome_condo(c["nome_raw"])
        c["via"] = via_bella(c["via_raw"])
        c["ck"] = chiave_contea(c["contea_raw"], c["st"])
        c["tk"] = chiave_citta(c["citta_raw"])
        c["soon"] = c["tipo"] == "A" and bool(c["scadenza"]) and c["scadenza"] <= LIMITE_SOON.isoformat()
        c["passata"] = c["tipo"] == "A" and bool(c["scadenza"]) and c["scadenza"] < ASOF.isoformat()
    # nome della città: la variante più frequente (es. "ST PETERSBURG" e "SAINT PETERSBURG" sono la stessa città)
    varianti = defaultdict(Counter)
    for c in CONDOMINI:
        if c["tk"]:
            varianti[(c["st"], c["tk"])][c["citta_raw"]] += 1
    NOME_CITTA = {k: titolo(v.most_common(1)[0][0], "luogo") for k, v in varianti.items()}
    for c in CONDOMINI:
        c["citta"] = NOME_CITTA.get((c["st"], c["tk"]), "")
    stati, contee, citta = {}, {}, {}
    for c in CONDOMINI:
        stati.setdefault(c["st"], []).append(c)
        if c["ck"]:
            contee.setdefault((c["st"], c["ck"]), []).append(c)
        if c["tk"]:
            citta.setdefault((c["st"], c["tk"]), []).append(c)
    return stati, contee, citta, NOME_CITTA


STATI_C, CONTEE_C, CITTA_C, NOME_CITTA = prepara()


def approvati(lista):
    return [c for c in lista if c["tipo"] == "A"]


def recenti(lista):
    return [c for c in lista if c["tipo"] != "A"]


def scelte_pagine():
    """Quali contee e città hanno una pagina, con quale URL. Evita pagine doppie (stesso elenco di un'altra)."""
    url_contea, url_citta = {}, {}
    for (st, ck), lista in CONTEE_C.items():
        if len(approvati(lista)) >= SOGLIA_CONTEA:
            url_contea[(st, ck)] = url_stato(st) + slug(ck) + "/"
    for (st, tk), lista in CITTA_C.items():
        if len(approvati(lista)) >= SOGLIA_CITTA:
            s = slug(NOME_CITTA[(st, tk)])
            url_citta[(st, tk)] = url_stato(st) + s + "/"
    # collisioni di indirizzo tra città e contee dello stesso Stato
    usati = {u: k for k, u in url_contea.items()}
    for k, u in list(url_citta.items()):
        if u in usati:
            url_citta[k] = u[:-1] + "-city/"
    # pagina di contea con lo stesso elenco dello Stato (es. District of Columbia): niente pagina di contea
    ids_stato = {st: {c["id"] for c in l} for st, l in STATI_C.items()}
    for (st, ck) in list(url_contea):
        if {c["id"] for c in CONTEE_C[(st, ck)]} == ids_stato[st]:
            del url_contea[(st, ck)]
    for (st, tk) in list(url_citta):
        if {c["id"] for c in CITTA_C[(st, tk)]} == ids_stato[st]:
            del url_citta[(st, tk)]
    # città e contea quasi uguali (almeno il 90% dei condomini in comune): resta una sola pagina, quella della città
    # (le ricerche per città sono più frequenti), con il nome della contea nel titolo; la contea rimanda alla città.
    alias_contea, alias_citta = {}, {}
    for (st, tk) in list(url_citta):
        ids = {c["id"] for c in CITTA_C[(st, tk)]}
        for (st2, ck) in list(url_contea):
            if st2 != st:
                continue
            idc = {c["id"] for c in CONTEE_C[(st2, ck)]}
            if len(ids & idc) / len(ids | idc) >= 0.9:
                alias_contea[(st2, ck)] = url_citta[(st, tk)]
                del url_contea[(st2, ck)]
                break
    return url_contea, url_citta, alias_contea, alias_citta


URL_CONTEA, URL_CITTA, ALIAS_CONTEA, ALIAS_CITTA = scelte_pagine()


def link_contea(st, ck):
    return URL_CONTEA.get((st, ck)) or ALIAS_CONTEA.get((st, ck))


def link_citta(st, tk):
    return URL_CITTA.get((st, tk)) or ALIAS_CITTA.get((st, tk))


def pagina_di(c):
    """Pagina in cui il condominio compare nella tabella principale (città > contea > Stato)."""
    return URL_CITTA.get((c["st"], c["tk"])) or URL_CONTEA.get((c["st"], c["ck"])) or url_stato(c["st"])


def floodcost_contea(st, ck):
    """Pagina FloodCost della stessa contea, se esiste davvero in floodcost/sito/."""
    if not ck:
        return None
    p = url_stato(st) + slug(ck) + "/"
    return p if (FLOODCOST_SITO / p / "index.html").exists() else None


def floodcost_stato(st):
    p = url_stato(st)
    return p if (FLOODCOST_SITO / p / "index.html").exists() else None


# ---------------------------------------------------------------- stile
CSS = """
@font-face{font-family:"Lora";src:url(/assets/fonts/lora.woff2) format("woff2");font-weight:500 700;font-style:normal;font-display:swap}
@font-face{font-family:"Libre Franklin";src:url(/assets/fonts/libre-franklin.woff2) format("woff2");font-weight:300 800;font-style:normal;font-display:swap}
:root{--bg:#F5F6F2;--card:#FFFFFF;--ink:#14231F;--ink-2:#36463F;--ink-3:#56655F;--line:#DCE2DD;--line-2:#C3CCC6;
--deep:#0F2D29;--deep-2:#173F39;--on-deep:#EEF5F2;--on-deep-2:#A9C3BA;--accent:#17694F;--accent-h:#0E513C;--accent-2:#E1F0E9;--on-accent:#FFFFFF;
--brass:#D9A441;--brass-ink:#7A5200;--ok:#17694F;--ok-2:#DDF0E6;--warn:#8A4B00;--warn-2:#FFF0D6;--warn-l:#E9B35A;--bad:#A52A1F;--bad-2:#FBE5E2;
--mute:#EDF1EE;--hl:#FFF6CC;--m1:#E1F0E9;--m2:#AFD8C5;--m3:#6FB497;--m4:#237556;--m5:#125A43;--m-ink-lo:#14231F;--m-ink-hi:#FFFFFF;
--sh-1:0 1px 2px rgba(15,45,41,.06),0 1px 1px rgba(15,45,41,.04);--sh-2:0 22px 44px -24px rgba(15,45,41,.38),0 2px 8px rgba(15,45,41,.06);
--r:14px;--r-s:10px;--serif:Lora,Charter,"Iowan Old Style",Georgia,serif;--sans:"Libre Franklin",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0A1412;--card:#111F1C;--ink:#E3EDE9;--ink-2:#B5C6BF;--ink-3:#8FA39B;--line:#1F322D;--line-2:#2C443D;
--deep:#06100E;--deep-2:#0D241F;--on-deep:#E3EDE9;--on-deep-2:#9BB5AB;--accent:#6CD0A5;--accent-h:#9BE2C3;--accent-2:#123228;--on-accent:#04140E;
--brass:#E8BC63;--brass-ink:#E8BC63;--ok:#6CD0A5;--ok-2:#123228;--warn:#F2BE6B;--warn-2:#2B2112;--warn-l:#8A6420;--bad:#FF9C8F;--bad-2:#34171A;
--mute:#14251F;--hl:#3A3412;--m1:#173A2F;--m2:#1F5442;--m3:#2B7559;--m4:#53AD87;--m5:#94DDBC;--m-ink-lo:#E3EDE9;--m-ink-hi:#04140E;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 22px 44px -24px rgba(0,0,0,.8),0 2px 8px rgba(0,0,0,.4)}}
:root[data-theme="dark"]{--bg:#0A1412;--card:#111F1C;--ink:#E3EDE9;--ink-2:#B5C6BF;--ink-3:#8FA39B;--line:#1F322D;--line-2:#2C443D;
--deep:#06100E;--deep-2:#0D241F;--on-deep:#E3EDE9;--on-deep-2:#9BB5AB;--accent:#6CD0A5;--accent-h:#9BE2C3;--accent-2:#123228;--on-accent:#04140E;
--brass:#E8BC63;--brass-ink:#E8BC63;--ok:#6CD0A5;--ok-2:#123228;--warn:#F2BE6B;--warn-2:#2B2112;--warn-l:#8A6420;--bad:#FF9C8F;--bad-2:#34171A;
--mute:#14251F;--hl:#3A3412;--m1:#173A2F;--m2:#1F5442;--m3:#2B7559;--m4:#53AD87;--m5:#94DDBC;--m-ink-lo:#E3EDE9;--m-ink-hi:#04140E;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 22px 44px -24px rgba(0,0,0,.8),0 2px 8px rgba(0,0,0,.4)}
*{box-sizing:border-box}[hidden]{display:none!important}html{-webkit-text-size-adjust:100%;scroll-padding-top:16px}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:17px;line-height:1.6;overflow-wrap:break-word}
a{color:var(--accent);text-underline-offset:2px;text-decoration-thickness:1px}a:hover{color:var(--accent-h)}
:focus-visible{outline:3px solid var(--brass);outline-offset:2px;border-radius:4px}
.skip{position:absolute;left:-9999px;top:8px;background:var(--card);color:var(--ink);padding:8px 14px;border-radius:8px;z-index:50}.skip:focus{left:12px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.ico{width:1.15em;height:1.15em;flex:none;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;vertical-align:-.2em}
.wrap{max-width:1100px;margin:0 auto;padding:0 16px}
header.top{background:var(--deep);color:var(--on-deep);position:relative;z-index:20;border-bottom:1px solid rgba(255,255,255,.06)}
header.top .wrap{display:flex;align-items:center;gap:12px;min-height:64px}
.logo{display:flex;align-items:center;gap:10px;font-family:var(--serif);font-weight:700;font-size:1.2rem;color:var(--on-deep);text-decoration:none;white-space:nowrap;letter-spacing:-.01em;margin-right:auto}
.logo:hover{color:#fff}.logo img{width:34px;height:34px;flex:none;display:block}.logo b{color:var(--brass);font-weight:inherit}
nav.menu{display:flex;gap:2px;font-size:.93rem}
nav.menu a{color:var(--on-deep-2);text-decoration:none;padding:7px 11px;border-radius:8px;white-space:nowrap}
nav.menu a:hover,nav.menu a[aria-current]{color:#fff;background:rgba(255,255,255,.08)}
.tema{display:grid;place-items:center;width:42px;height:42px;border-radius:10px;border:1px solid rgba(255,255,255,.22);background:none;color:var(--on-deep);cursor:pointer;flex:none}
.tema:hover{border-color:var(--brass)}.tema .ico{width:20px;height:20px}
.tema .i-sun{display:none}:root[data-theme="dark"] .tema .i-sun{display:block}:root[data-theme="dark"] .tema .i-moon{display:none}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .tema .i-sun{display:block}:root:not([data-theme="light"]) .tema .i-moon{display:none}}
.nav-m{display:none}
.nav-m summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:8px;font-weight:600;font-size:.95rem;padding:9px 13px;border:1px solid rgba(255,255,255,.25);border-radius:10px;color:var(--on-deep);min-height:42px}
.nav-m summary::-webkit-details-marker{display:none}.nav-m[open] summary{background:rgba(255,255,255,.1);border-color:var(--brass)}
.nav-m nav{position:absolute;left:16px;right:16px;top:calc(100% + 4px);background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-2);padding:8px;display:grid}
.nav-m nav a{padding:12px 14px;border-radius:8px;color:var(--ink);text-decoration:none;font-weight:600}.nav-m nav a:hover{background:var(--accent-2)}
.band{background:var(--deep);color:var(--on-deep);position:relative;overflow:hidden}
.band::before{content:"";position:absolute;inset:0;background:radial-gradient(800px 320px at 88% -20%,rgba(217,164,65,.20),transparent 62%),radial-gradient(700px 300px at 0% 120%,rgba(108,208,165,.14),transparent 60%),linear-gradient(180deg,var(--deep) 0,var(--deep-2) 100%)}
.band::after{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:36px 36px;-webkit-mask:linear-gradient(180deg,#000,transparent 85%);mask:linear-gradient(180deg,#000,transparent 85%)}
.band-in{position:relative;z-index:1;padding:30px 16px 78px}
.band.corta .band-in{padding-bottom:40px}
.eyebrow{display:inline-flex;align-items:center;gap:8px;font-size:.78rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--brass);margin:0 0 12px}
h1,h2,h3{font-family:var(--serif);font-weight:700;letter-spacing:-.01em}
h1{font-size:clamp(1.85rem,5vw,2.8rem);line-height:1.12;margin:0 0 12px;text-wrap:balance;max-width:860px}
.band h1{color:#fff}
.sub{font-size:1.08rem;color:var(--on-deep-2);margin:0 0 16px;max-width:720px}.sub strong{color:#fff}
.trust{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:.88rem;color:var(--on-deep-2);margin:0;padding:0;list-style:none}
.trust li{display:inline-flex;align-items:center;gap:7px}.trust .ico{color:var(--brass)}
.briciole{font-size:.85rem;color:var(--on-deep-2);margin:0 0 14px}.briciole a{color:var(--on-deep)}
h2{font-size:clamp(1.35rem,3vw,1.6rem);line-height:1.22;margin:44px 0 12px;scroll-margin-top:16px}
h3{font-size:1.12rem;margin:24px 0 8px}
.lead{font-size:1.04rem;color:var(--ink-2);max-width:780px;margin:0 0 14px}
.small{font-size:.87rem;color:var(--ink-3)}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:20px;min-width:0;box-shadow:var(--sh-1)}
.pull{margin-top:-56px;position:relative;z-index:2}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0;padding:0;overflow:hidden;box-shadow:var(--sh-2)}
.stat{padding:18px 20px;border-right:1px solid var(--line);min-width:0}.stat:last-child{border-right:0}
.stat b{display:block;font-variant-numeric:lining-nums tabular-nums;font-family:var(--serif);font-size:clamp(1.6rem,4vw,2.1rem);line-height:1.08;font-variant-numeric:tabular-nums;color:var(--ink)}
.stat span{display:block;font-size:.84rem;color:var(--ink-3);line-height:1.35;margin-top:6px}
.stat.soon b{color:var(--warn)}.stat.main b{color:var(--accent)}
.asof{margin:0;display:flex;flex-wrap:wrap;align-items:center;gap:6px 14px;justify-content:space-between;padding:10px 20px;background:var(--mute);border-top:1px solid var(--line);font-size:.86rem;color:var(--ink-2);grid-column:1/-1}
.asof b{color:var(--ink)}.asof a{font-weight:600}
.nota{position:relative;background:var(--warn-2);border:1px solid color-mix(in srgb,var(--warn-l) 60%,transparent);padding:13px 16px 13px 48px;border-radius:var(--r-s);font-size:.94rem;margin:20px 0;color:var(--ink)}
.nota .ico{position:absolute;left:16px;top:15px;color:var(--warn);width:20px;height:20px}.nota p{margin:0 0 6px}.nota p:last-child{margin:0}
.nota.info{background:var(--accent-2);border-color:color-mix(in srgb,var(--accent) 35%,transparent)}.nota.info .ico{color:var(--accent)}
.tab{border:1px solid var(--line);border-radius:var(--r);background:var(--card);box-shadow:var(--sh-1);overflow:hidden}
.tab.scorre{overflow-x:auto;-webkit-overflow-scrolling:touch}
table{border-collapse:collapse;width:100%;font-size:.93rem}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}
td.n,th.n{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
th{background:var(--mute);font-size:.74rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2);vertical-align:bottom}
tbody tr:last-child td{border-bottom:0}
.ct td.cn b{display:block;font-weight:650;line-height:1.3}.ct td.cn small{display:block;color:var(--ink-3);font-size:.82rem;line-height:1.35;margin-top:2px}
.ct td.cn small i{font-style:normal;font-variant-numeric:tabular-nums;white-space:nowrap}
.ct tr:target td{background:var(--hl)}
.ct tr.soon td.ce{color:var(--warn);font-weight:700}
.badge{display:inline-flex;align-items:center;gap:5px;font-size:.72rem;font-weight:700;letter-spacing:.03em;padding:2px 8px;border-radius:999px;white-space:nowrap;vertical-align:1px}
.b-ok{background:var(--ok-2);color:var(--ok)}.b-soon{background:var(--warn-2);color:var(--warn);border:1px solid color-mix(in srgb,var(--warn-l) 55%,transparent)}
.b-bad{background:var(--bad-2);color:var(--bad)}.b-mute{background:var(--mute);color:var(--ink-2)}
.muted{color:var(--ink-3)}
.filtro-box{display:flex;flex-wrap:wrap;align-items:center;gap:8px 14px;margin:0 0 10px}
.filtro-box label{position:relative;flex:1 1 280px;max-width:440px}
.filtro-box .ico{position:absolute;left:12px;top:50%;transform:translateY(-50%);color:var(--ink-3);pointer-events:none}
.filtro{font:inherit;font-size:1rem;color:var(--ink);background:var(--card);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:10px 12px 10px 40px;width:100%;min-height:46px}
.filtro:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 22%,transparent)}
.filtro-n{font-size:.88rem;color:var(--ink-3)}
@media (max-width:700px){.ct thead{display:none}.ct,.ct tbody,.ct tr,.ct td{display:block;width:100%}
.ct tr{display:grid;gap:2px 14px;padding:12px 14px;border-bottom:1px solid var(--line);justify-content:start}.ct tbody tr:last-child{border-bottom:0}
.ct td{border:0;padding:0;text-align:left!important}
.ct tr{grid-template-columns:repeat(4,auto) 1fr}.ct td.cn,.ct td.ce{grid-column:1/-1}
.ct td.cc,.ct td.cz,.ct td.cu,.ct td.cf{display:block;width:auto;font-size:.86rem;color:var(--ink-2);white-space:nowrap}
.ct td.cz::before{content:"ZIP ";color:var(--ink-3);font-size:.8rem}.ct td.cu::before{content:"Units ";color:var(--ink-3);font-size:.8rem}
.ct td.cf::before{content:"FHA ";color:var(--ink-3);font-size:.8rem}
.ct td.ce{font-size:.9rem;margin-top:4px}.ct.ta td.ce::before{content:"Approved until ";color:var(--ink-3);font-weight:400;font-size:.8rem}
.ct tr:target{background:var(--hl)}.ct tr:target td{background:none}}
.pl td:first-child{font-weight:600}
.scad-card{padding:6px 20px 12px}.scad-card .small{margin:8px 0 0}
.scad{list-style:none;margin:0;padding:0}.scad li{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,180px) 120px;gap:2px 16px;padding:10px 0;border-bottom:1px solid var(--line);align-items:baseline}
.scad li:last-child{border-bottom:0}.scad a{font-weight:650;text-decoration:none}.scad a:hover{text-decoration:underline}.scad span{color:var(--ink-2);font-size:.92rem}
.scad b{color:var(--warn);text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
@media (max-width:560px){.scad li{grid-template-columns:minmax(0,1fr) auto}.scad a{grid-column:1/-1}.scad b{grid-column:2}}
@media (max-width:560px){.pl th.hide-s,.pl td.hide-s{display:none}}
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:10px;margin:0;padding:0;list-style:none}
.griglia a{display:flex;flex-direction:column;justify-content:flex-start;gap:2px;height:100%;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:12px 14px;text-decoration:none;color:var(--ink);font-weight:700;min-width:0;box-shadow:var(--sh-1);transition:border-color .15s,transform .15s}
.griglia a:hover{border-color:var(--accent);transform:translateY(-1px)}
.griglia a span{min-width:0;overflow-wrap:anywhere}.griglia a small{font-weight:500;color:var(--ink-3);font-size:.86rem;font-variant-numeric:tabular-nums}
.cerca-card{padding:18px 20px}
.cerca-card label{display:flex;align-items:center;gap:8px;font-family:var(--serif);font-weight:700;font-size:1.15rem;margin:0 0 10px}
.cerca-card label .ico{color:var(--accent)}
.cerca-box{position:relative}.cerca-box .ico{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:var(--ink-3);pointer-events:none}
.cerca{font:inherit;font-size:1.05rem;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:12px 14px 12px 44px;width:100%;min-height:52px}
.cerca:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 22%,transparent)}
.risultati{display:grid;gap:6px;margin-top:10px}.risultati:empty{display:none}
.risultati a{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:2px 12px;align-items:start;padding:10px 12px;border-radius:var(--r-s);border:1px solid var(--line);text-decoration:none;color:var(--ink);background:var(--card)}
.risultati a:hover,.risultati a:focus{border-color:var(--accent);background:var(--accent-2)}
.risultati a b{font-weight:700;min-width:0}.risultati a .dove{grid-column:1/-1;font-size:.86rem;color:var(--ink-3)}
.risultati .grp{font-size:.74rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);margin:8px 2px 0}
.esempi{font-size:.86rem;color:var(--ink-3);margin:10px 0 0}.esempi button{font:inherit;color:var(--accent);background:none;border:0;padding:0;text-decoration:underline;text-underline-offset:2px;cursor:pointer}
.mappa{display:grid;grid-template-columns:repeat(11,minmax(0,1fr));gap:4px;margin:6px auto 12px;max-width:760px}
.mappa a,.mappa span{aspect-ratio:1/1;border-radius:6px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-decoration:none;font-weight:800;font-size:clamp(.62rem,1.6vw,.95rem);line-height:1.1;min-width:0;color:var(--m-ink-lo)}
.mappa a small{font-weight:600;font-size:.72em;font-variant-numeric:tabular-nums}
.mappa a:hover{outline:2px solid var(--brass);outline-offset:1px}
.m1{background:var(--m1)}.m2{background:var(--m2)}.m3{background:var(--m3)}.m4{background:var(--m4);color:var(--m-ink-hi)!important}.m5{background:var(--m5);color:var(--m-ink-hi)!important}
.mappa .m0{background:var(--mute);color:var(--ink-3)}
.legenda{display:flex;flex-wrap:wrap;justify-content:center;gap:6px 14px;font-size:.82rem;color:var(--ink-2);margin:0;padding:0;list-style:none}
.legenda li{display:inline-flex;align-items:center;gap:6px}.legenda i{width:14px;height:14px;border-radius:3px;display:inline-block}
@media (max-width:560px){.mappa a small{display:none}.mappa{gap:3px}
.griglia{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.griglia a{padding:10px 12px;font-size:.94rem;line-height:1.3}.griglia a small{font-size:.8rem}
ol.passi>li{padding:14px 14px 14px 52px}ol.passi>li::before{left:12px;top:14px;width:28px;height:28px;font-size:.92rem}
.cerca-card,.card{padding:16px}.stats{padding:0}.scad-card{padding:4px 16px 10px}}
.fonti-box{margin-top:44px;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:var(--r-s);padding:16px 20px;font-size:.9rem;color:var(--ink-2)}
.fonti-box h2{display:flex;align-items:center;gap:8px;font-size:1.1rem;margin:0 0 8px;color:var(--ink)}.fonti-box h2 .ico{color:var(--accent)}
.fonti-box ul{margin:0 0 8px;padding-left:18px}.fonti-box li{margin-bottom:6px}.fonti-box p{margin:6px 0}
.fonti-box a{overflow-wrap:anywhere}
.btn{display:inline-flex;align-items:center;gap:8px;font:inherit;font-weight:700;background:var(--accent);color:var(--on-accent);border:0;border-radius:var(--r-s);padding:11px 18px;cursor:pointer;min-height:46px;text-decoration:none}
.btn:hover{background:var(--accent-h);color:var(--on-accent)}.btn:disabled{opacity:.6;cursor:wait}
.btn.sec{background:none;color:var(--accent);border:1.5px solid color-mix(in srgb,var(--accent) 55%,transparent)}.btn.sec:hover{background:var(--accent-2);color:var(--accent-h)}
.ad-slot{margin:24px 0}.ad-slot:empty{display:none}
.aff-box{margin:24px 0;display:flex;gap:16px;align-items:center;justify-content:space-between;flex-wrap:wrap;background:var(--accent-2);border:1px solid color-mix(in srgb,var(--accent) 30%,transparent);border-radius:var(--r);padding:18px 20px}
.aff-box p{margin:0;max-width:620px}
.testo p,.testo li{max-width:780px}.testo li{margin-bottom:6px}
.testo h2{margin-top:36px}
ol.passi{counter-reset:p;list-style:none;padding:0;margin:0;display:grid;gap:12px}
ol.passi>li{counter-increment:p;position:relative;padding:16px 18px 16px 62px;background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-1);max-width:none}
ol.passi>li::before{content:counter(p);position:absolute;left:16px;top:14px;width:32px;height:32px;border-radius:50%;background:var(--accent);color:var(--on-accent);font-weight:800;display:grid;place-items:center;font-family:var(--serif)}
ol.passi>li h3{margin:2px 0 6px}ol.passi>li p{margin:0 0 6px}
.cmp th:first-child,.cmp td:first-child{font-weight:700;min-width:120px}
.cmp td{min-width:170px}
.cite{font-size:.82rem;color:var(--ink-3)}
details.tutti{margin-top:10px}details.tutti summary{cursor:pointer;font-weight:700;color:var(--accent);padding:6px 0}
.cols{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px}
.cols3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.guida{display:flex;flex-direction:column;gap:6px;text-decoration:none;color:var(--ink);height:100%}
.guida b{font-family:var(--serif);font-size:1.1rem;line-height:1.25}.guida span{font-size:.92rem;color:var(--ink-2)}
.guida em{font-style:normal;font-weight:700;color:var(--accent);font-size:.9rem;margin-top:auto}
a.card.guida:hover{border-color:var(--accent)}
.altri{margin-top:40px;border-top:1px solid var(--line);padding-top:18px}
.altri h2{font-family:var(--sans);font-size:.76rem;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-3);margin:0 0 10px}
.altri ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:10px}
.altri a{display:flex;flex-direction:column;gap:2px;padding:10px 14px;border:1px solid var(--line);border-radius:var(--r-s);background:var(--card);text-decoration:none;color:var(--ink);font-weight:700;max-width:420px}
.altri a small{font-weight:500;color:var(--ink-3);font-size:.85rem}.altri a:hover{border-color:var(--accent)}
.form{display:grid;gap:14px}.form label{display:grid;gap:6px;font-weight:600;font-size:.95rem}
.form input,.form textarea{font:inherit;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:10px 12px;width:100%;min-height:46px}
.form .check{display:flex;gap:10px;align-items:flex-start;font-weight:400;font-size:.9rem;color:var(--ink-2)}.form .check input{width:auto;min-height:0;margin-top:4px}
.hp{position:absolute;left:-9999px}.ok{background:var(--accent-2);border:1px solid var(--accent);padding:14px;border-radius:var(--r-s)}.errore{color:var(--bad);font-weight:600}
footer{margin-top:56px;background:var(--deep);color:var(--on-deep-2);font-size:.88rem;padding:40px 0 34px}
footer a{color:var(--on-deep)}footer a:hover{color:var(--brass)}
footer .f-grid{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(0,1fr);gap:28px}
footer .logo{margin-bottom:12px}footer p{margin:0 0 10px;max-width:680px}footer strong{color:var(--on-deep)}
footer ul{list-style:none;margin:0;padding:0;display:grid;gap:8px}
footer h2{font-family:var(--sans);font-size:.76rem;letter-spacing:.12em;text-transform:uppercase;color:var(--brass);margin:4px 0 12px}
footer .f-base{border-top:1px solid rgba(255,255,255,.12);margin-top:24px;padding-top:16px;font-size:.82rem;max-width:none}
@media (max-width:880px){.stats{grid-template-columns:repeat(2,minmax(0,1fr))}.stat:nth-child(2){border-right:0}.stat:nth-child(-n+2){border-bottom:1px solid var(--line)}.cols,.cols3{grid-template-columns:1fr}}
@media (max-width:760px){nav.menu{display:none}.nav-m{display:block}header.top .wrap{min-height:60px}footer .f-grid{grid-template-columns:1fr}.band-in{padding-top:22px}}
@media (max-width:640px){th,td{padding:9px 9px}table{font-size:.9rem}.stat{padding:14px 14px}.asof{padding:10px 14px}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""
CSS = re.sub(r"\n", "", CSS)

ICONE = {
    "search": '<circle cx="11" cy="11" r="7.5"/><path d="M21 21l-4.5-4.5"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "moon": '<path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6 6 6M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4"/>',
    "check": '<circle cx="12" cy="12" r="9.5"/><path d="M8 12.5l2.8 2.8L16.5 9.5"/>',
    "building": '<path d="M4 21V5.5A1.5 1.5 0 0 1 5.5 4h7A1.5 1.5 0 0 1 14 5.5V21"/><path d="M14 10h4.5a1.5 1.5 0 0 1 1.5 1.5V21M2.5 21h19"/><path d="M7.5 8h3M7.5 12h3M7.5 16h3M17 14h.01M17 17.5h.01"/>',
    "calendar": '<rect x="3" y="4.5" width="18" height="17" rx="2.5"/><path d="M16 2.5v4M8 2.5v4M3 10h18"/>',
    "alert": '<path d="M12 3 2 20h20z"/><path d="M12 10v4M12 17h.01"/>',
    "info": '<circle cx="12" cy="12" r="9.5"/><path d="M12 11v6M12 7.5h.01"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "ext": '<path d="M14 4h6v6M20 4l-9 9"/><path d="M18 14v4.5A1.5 1.5 0 0 1 16.5 20h-11A1.5 1.5 0 0 1 4 18.5v-11A1.5 1.5 0 0 1 5.5 6H10"/>',
    "pin": '<path d="M12 21.5s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "db": '<ellipse cx="12" cy="5.5" rx="8" ry="3"/><path d="M4 5.5v13c0 1.7 3.6 3 8 3s8-1.3 8-3v-13M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    "shield": '<path d="M12 22s8-3.5 8-10V5.5L12 2.5 4 5.5V12c0 6.5 8 10 8 10z"/><path d="M8.5 12l2.5 2.5 4.5-4.5"/>',
    "filter": '<path d="M3.5 5h17l-6.5 8v5.5l-4 2V13z"/>',
    "doc": '<path d="M14 2.5H6.5A2 2 0 0 0 4.5 4.5v15a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V8z"/><path d="M14 2.5V8h5.5M8 13h8M8 17h5"/>',
}

SPRITE = ('<svg xmlns="http://www.w3.org/2000/svg">' +
          "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONE.items()) + "</svg>\n")
ICONS_FILE = f"icons.{hashlib.sha256(SPRITE.encode()).hexdigest()[:10]}.svg"


def ico(nome, cls="ico"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="/assets/{ICONS_FILE}#i-{nome}"/></svg>'


# Marchio: palazzina con segno di spunta, tessera verde scuro con dettagli ottone (stesso disegno in favicon e immagine Open Graph)
MARCHIO = ('<rect width="40" height="40" rx="10" fill="#17694F"/>'
           '<path d="M10 31V12.5a1.5 1.5 0 0 1 1.5-1.5h11a1.5 1.5 0 0 1 1.5 1.5V31M7.5 31h25" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
           '<path d="M14 16h6M14 20.5h6M14 25h3" stroke="#fff" stroke-width="2.2" stroke-linecap="round"/>'
           '<circle cx="28.5" cy="25.5" r="7" fill="#D9A441"/><path d="M25.3 25.6l2.2 2.2 4.2-4.4" fill="none" stroke="#0F2D29" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
FAVICON_SVG = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">{MARCHIO}</svg>\n'

TEMA_JS = "(function(){try{var t=localStorage.getItem('ac-theme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();"
APP_JS = r"""
(function(){
  var b=document.querySelector('[data-tema]');
  if(b)b.addEventListener('click',function(){var r=document.documentElement,c=r.getAttribute('data-theme');
    if(!c)c=window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
    var n=c==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem('ac-theme',n);}catch(e){}});
  var ref='';try{ref=new URLSearchParams(location.search).get('ref')||document.referrer||'direct';}catch(e){ref='direct';}
  document.querySelectorAll('input[name=source]').forEach(function(i){i.value=String(ref).slice(0,200);});
  document.querySelectorAll('form.ajax').forEach(function(form){form.addEventListener('submit',function(ev){ev.preventDefault();
    var err=form.querySelector('[data-errore]');err.hidden=true;if(!form.checkValidity()){form.reportValidity();return;}
    var bt=form.querySelector('button');bt.disabled=true;
    fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(new FormData(form)).toString()})
    .then(function(r){if(!r.ok)throw new Error(r.status);form.hidden=true;form.parentNode.querySelector('[data-ok]').hidden=false;})
    .catch(function(){err.hidden=false;bt.disabled=false;});});});
  function norm(s){return String(s==null?'':s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,' ').trim().replace(/\bsaint\b/g,'st');}
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  // filtro delle tabelle
  document.querySelectorAll('[data-filtro]').forEach(function(inp){
    var t=document.getElementById(inp.getAttribute('data-filtro'));if(!t)return;var rows=[].slice.call(t.tBodies[0].rows);
    var out=document.getElementById(inp.getAttribute('data-filtro')+'-n');rows.forEach(function(r){r._k=norm(r.textContent);});
    inp.addEventListener('input',function(){var v=norm(inp.value),n=0;rows.forEach(function(r){var ok=!v||r._k.indexOf(v)>=0;r.hidden=!ok;if(ok)n++;});
      if(out)out.textContent=v?(n+' of '+rows.length+' shown'):'';});});
  var box=document.querySelector('[data-cerca]');if(!box)return;
  var inp=box.querySelector('input'),out=box.querySelector('.risultati'),D=null,carico=false,coda=null,rel=box.getAttribute('data-rel')||'';
  var MESI=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  function dt(n){if(!n)return '';var s=String(n);return MESI[+s.slice(4,6)-1]+' '+(+s.slice(6,8))+', '+s.slice(0,4);}
  function carica(cb){if(D)return cb();coda=cb;if(carico)return;carico=true;out.innerHTML='<p class="small">Loading the list…</p>';
    fetch(box.getAttribute('data-url')).then(function(r){if(!r.ok)throw new Error(r.status);return r.json();}).then(function(d){D=d;
      d.c.forEach(function(x){x.k=' '+norm(x[0])+' ';x.t=norm(d.t[x[1]][0]);x.ts=x.t+' '+d.t[x[1]][1].toLowerCase();});d.p.forEach(function(x){x.k=norm(x[1]);});if(coda)coda();})
    .catch(function(){out.innerHTML='<p class="errore">Could not load the list. Please try again.</p>';carico=false;});}
  function stato(x){if(x[6]===0){return x[7]?'<span class="badge b-soon">Expires '+dt(x[5])+'</span>':'<span class="badge b-ok">Approved until '+dt(x[5])+'</span>';}
    if(x[6]===1)return '<span class="badge b-bad">Expired '+dt(x[5])+'</span>';if(x[6]===3)return '<span class="badge b-soon">Approval ends '+dt(x[5])+'</span>';return '<span class="badge b-mute">Withdrawn '+dt(x[5])+'</span>';}
  function riga(x){var t=D.t[x[1]],p=D.p[x[4]];return '<a href="'+esc(rel+p[0])+'#c-'+esc(x[8])+'"><b>'+esc(x[0])+'</b>'+stato(x)+
    '<span class="dove">'+esc(t[0])+', '+esc(t[1])+(x[2]?' '+esc(x[2]):'')+' · HUD ID '+esc(x[8])+'</span></a>';}
  function cerca(){var q=inp.value.trim(),v=norm(q);if(v.length<2){out.innerHTML='';return;}
    carica(function(){var r=[],luoghi=[],zip=/^\d{3,5}$/.test(v),idq=/^[a-z]\d{3,6}$/.test(v.replace(/ /g,''));
      if(!zip&&!idq){D.p.forEach(function(p){if(luoghi.length<6&&p[2]&&(p.k.indexOf(v)===0||p.k.indexOf(' '+v)>=0))luoghi.push(p);});}
      D.c.forEach(function(x){if(r.length>=40)return;var ok=false;
        if(zip)ok=String(x[2]).indexOf(v)===0;else if(idq)ok=x[8].toLowerCase().indexOf(v.replace(/ /g,''))===0;
        else ok=x.k.indexOf(' '+v)>=0||x.ts.indexOf(v)===0;if(ok)r.push(x);});
      r.sort(function(a,b){return a[6]-b[6]||(a[0]<b[0]?-1:1);});
      var html='';if(luoghi.length)html+='<p class="grp">Places</p>'+luoghi.map(function(p){return '<a href="'+esc(rel+p[0])+'"><b>'+esc(p[1])+'</b><span class="badge b-ok">'+p[3]+' approved</span></a>';}).join('');
      if(r.length)html+='<p class="grp">Condo projects'+(r.length>=40?' (first 40)':'')+'</p>'+r.slice(0,40).map(riga).join('');
      out.innerHTML=html||'<p class="small">Nothing found for “'+esc(q)+'”. Try one distinctive word of the name, the city or the 5-digit ZIP code. Not listed? It may not be approved: <a href="'+esc(rel)+'condo-not-fha-approved/">see your options</a>.</p>';});}
  inp.addEventListener('input',cerca);inp.addEventListener('focus',function(){carica(function(){});},{once:true});
  box.querySelector('form').addEventListener('submit',function(e){e.preventDefault();var a=out.querySelector('a');if(a)location.href=a.href;else cerca();});
  box.querySelectorAll('[data-es]').forEach(function(bt){bt.addEventListener('click',function(){inp.value=bt.getAttribute('data-es');inp.focus();cerca();});});
  try{var q0=new URLSearchParams(location.search).get('q');if(q0){inp.value=q0;cerca();}}catch(e){}
})();
"""


def _impronta(testo):
    return hashlib.sha256(testo.encode("utf-8")).hexdigest()[:10]


ASSET = {
    f"site.{_impronta(CSS)}.css": CSS,
    f"app.{_impronta(APP_JS)}.js": APP_JS.strip() + "\n",
    f"favicon.{_impronta(FAVICON_SVG)}.svg": FAVICON_SVG,
    ICONS_FILE: SPRITE,
}
CSS_FILE, JS_FILE, FAVICON_FILE, _ = ASSET
LOGO = f'<img src="/assets/{FAVICON_FILE}" width="34" height="34" alt="">'


def scrivi_asset():
    (SITO / "assets").mkdir(parents=True, exist_ok=True)
    for nome, testo in ASSET.items():
        (SITO / "assets" / nome).write_text(testo, encoding="utf-8")


# ---------------------------------------------------------------- scheletro di pagina
URLS = []
AD = '<div class="ad-slot" aria-hidden="true"></div>'
ORG_HUD = {"@type": "GovernmentOrganization", "name": "U.S. Department of Housing and Urban Development", "url": "https://www.hud.gov/"}


def altri_strumenti(extra=None):
    voci = list(extra or [])
    voci.append((FLOODCOST + "/", "FloodCost", "What NFIP flood insurance really costs, by ZIP code, county and flood zone"))
    li = "".join(f'<li><a href="{h(u)}" rel="noopener">{h(t)}<small>{h(s)}</small></a></li>' for u, t, s in voci)
    return f'<aside class="altri" aria-label="Other useful tools"><h2>Other useful tools</h2><ul>{li}</ul></aside>'


def pagina(percorso, titolo_p, descrizione, corpo, briciole=None, indicizza=True, assoluto=False, testata="", jsonld_extra=None, altri=None):
    file = percorso if percorso.endswith(".html") else (percorso + "index.html")
    prof = file.count("/")
    rel = "/" if assoluto else ("../" * prof or "./")
    url_pag = URL_SITO + "/" + percorso
    if indicizza:
        URLS.append(percorso)
    ld = []
    if percorso == "":
        ld.append({"@context": "https://schema.org", "@type": "WebSite", "name": NOME, "url": URL_SITO + "/",
                   "potentialAction": {"@type": "SearchAction", "target": URL_SITO + "/?q={search_term_string}",
                                       "query-input": "required name=search_term_string"}})
    bc = ""
    if briciole:
        voci = [{"@type": "ListItem", "position": 1, "name": "Home", "item": URL_SITO + "/"}]
        for i, (n, p) in enumerate(briciole, start=2):
            voci.append({"@type": "ListItem", "position": i, "name": n, "item": URL_SITO + "/" + p})
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": voci})
        bc = ('<nav class="briciole" aria-label="Breadcrumb"><a href="' + rel + '">Home</a>' +
              "".join(f' › <a href="{rel}{p}">{h(n)}</a>' for n, p in briciole[:-1]) + f" › {h(briciole[-1][0])}</nav>")
    if jsonld_extra:
        ld.append(jsonld_extra)
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    voci_menu = [("states/", "States"), ("is-my-condo-fha-approved/", "How to check"), ("condo-not-fha-approved/", "Not approved?"),
                 ("methodology/", "Methodology")]
    menu = "".join(f'<a href="{rel}{u}"' + (' aria-current="page"' if percorso.startswith(u) else "") + f'>{t}</a>' for u, t in voci_menu)
    testata = testata.replace("{bc}", bc).replace("{rel}", rel)
    corpo = corpo.replace("{rel}", rel).replace("{bc}", bc)
    testo = f"""<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="{GOOGLE_VERIFICA}">{ADSENSE_HEAD}
<title>{h(titolo_p)}</title>
<meta name="description" content="{h(descrizione)}">
{f'<link rel="canonical" href="{url_pag}">' if indicizza else '<meta name="robots" content="noindex">'}
<meta property="og:title" content="{h(titolo_p)}">
<meta property="og:description" content="{h(descrizione)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url_pag}">
<meta property="og:site_name" content="{NOME}">
<meta property="og:locale" content="en_US">
<meta property="og:image" content="{URL_SITO}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{NOME}: FHA-approved condo projects by state, county and city, from HUD's list">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0F2D29">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="/assets/{FAVICON_FILE}" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/libre-franklin.woff2" as="font" type="font/woff2" crossorigin>
<script>{TEMA_JS}</script>
<link rel="stylesheet" href="/assets/{CSS_FILE}">
{ld_html}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
<a class="logo" href="{rel}">{LOGO}<span>Approved<b>Condos</b></span></a>
<nav class="menu" aria-label="Menu">{menu}</nav>
<button type="button" class="tema" data-tema aria-label="Switch light or dark theme">{ico("moon", "ico i-moon")}{ico("sun", "ico i-sun")}</button>
<details class="nav-m"><summary aria-label="Open the menu">{ico("menu")}Menu</summary><nav aria-label="Menu">{menu}</nav></details>
</div></header>
<main id="main">
{testata}
<div class="wrap">
{corpo}{riquadro_trasparenza(corpo)}
{altri_strumenti(altri)}
</div>
</main>
<footer><div class="wrap">
<div class="f-grid"><div>
<a class="logo" href="{rel}">{LOGO}<span>Approved<b>Condos</b></span></a>
<p><strong>{NOME}</strong> republishes HUD's public list of FHA-approved condominium projects, by state, county and city. It is an independent site, not affiliated with HUD, FHA, VA or any lender.
<strong>Approval can change at any time:</strong> confirm a project's current status in the <a href="{HUD_LOOKUP}" rel="noopener">official HUD lookup</a> and with your lender before you rely on it. Nothing here is mortgage, legal or financial advice.</p>
</div><div>
<h2>Explore</h2>
<ul><li><a href="{rel}states/">All states</a></li><li><a href="{rel}is-my-condo-fha-approved/">Is my condo FHA approved?</a></li><li><a href="{rel}condo-not-fha-approved/">If a condo is not approved</a></li><li><a href="{rel}fha-vs-va-vs-warrantable-condos/">FHA vs VA vs warrantable</a></li><li><a href="{rel}methodology/">Methodology and sources</a></li><li><a href="{rel}about/">About</a></li><li><a href="{rel}contact/">Contact</a></li><li><a href="{rel}privacy.html">Privacy</a></li></ul>
</div></div>
<p class="f-base">Data: HUD FHA Condominium Lookup, as of {data_lunga(ASOF)} · Updated weekly.</p>
</div></footer>
<script src="/assets/{JS_FILE}" defer></script>
{SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")


# ---------------------------------------------------------------- componenti
def banda(eyebrow, titolo_b, sub, extra="", corta=False):
    return f"""<section class="band{' corta' if corta else ''}"><div class="wrap band-in">{{bc}}
<p class="eyebrow">{ico("check")}{h(eyebrow)}</p>
<h1>{h(titolo_b)}</h1>
<p class="sub">{sub}</p>{extra}
</div></section>"""


def avviso(luogo=""):
    return (f'<div class="nota">{ico("alert")}<p><strong>Check before you rely on this list.</strong> FHA approval can change at any time: '
            f'approvals expire, and HUD can withdraw them. Some approvals cover only certain phases or buildings of a project, '
            f'and this page is a weekly copy of HUD\'s list, not the live record.</p>'
            f'<p>Confirm the current status in the <a href="{HUD_LOOKUP}" rel="noopener">official HUD FHA Condominium Lookup</a> '
            f'and with your lender before you make an offer.</p></div>')


def fonte_box():
    return f"""<section class="fonti-box"><h2>{ico("db")}Source</h2>
<p>U.S. Department of Housing and Urban Development (HUD), <a href="{HUD_LOOKUP}" rel="noopener">FHA Condominium Lookup</a>: projects with status "Approved", plus projects whose approval expired or was withdrawn in the last {MESI_RECENTI} months. HUD data as of {data_lunga(ASOF)}; we re-download the full list every week (last download {data_lunga(ESTRATTO)}).</p>
<p class="small">HUD's list is public-domain U.S. government data. We show the project name, address, county, unit count (when HUD states one), FHA concentration and dates. <a href="{{rel}}methodology/">How we build this list</a>.</p></section>"""


def blocco_affiliati():
    a = AFFILIATI.get("mutuo") if isinstance(AFFILIATI, dict) else None
    if not a or not a.get("url"):
        return ""
    return (f'<aside class="aff-box"><p><strong>{h(a.get("titolo", ""))}</strong><br><span class="small">{h(a.get("testo", ""))} {MON.RIGA_EN}</span></p>'
            f'<a class="btn" href="{h(a["url"])}" rel="sponsored noopener" target="_blank">{h(a.get("bottone", "Compare"))}</a></aside>')


def etichetta_scadenza(c):
    if c["passata"]:
        return '<span class="badge b-bad">Past expiration date</span>'
    if c["soon"]:
        giorni = (date.fromisoformat(c["scadenza"]) - ASOF).days
        if giorni <= 14:
            testo = "Ends within 2 weeks: check HUD"
        elif giorni <= 61:
            testo = "Expires within 2 months"
        else:
            testo = "Expires within 6 months"
        return f'<span class="badge b-soon">{testo}</span>'
    return ""


def chiave_nome(c):
    """Ordine alfabetico "naturale": 9 Elm prima di 10 Main, Phase II prima di Phase 10."""
    return ([int(x) if x.isdigit() else x for x in re.split(r"(\d+)", c["nome"].lower())], c["id"])


def unita_txt(c):
    return intero(c["unita"]) if c["unita"] is not None else '<span class="muted" title="HUD does not state a unit count for this project">–</span>'


def fha_txt(c):
    return f'{c["fha_pct"]:.1f}%'.replace(".0%", "%") if c["fha_pct"] is not None else '<span class="muted">–</span>'


def cella_nome(c):
    via = f'{h(c["via"])} · ' if c["via"] else ""
    return f'<td class="cn"><b>{h(c["nome"])}</b><small>{via}<i>HUD ID {h(c["id"])}</i></small></td>'


def tabella_approvati(lista, tid, mostra_citta=True, filtro=True):
    lista = sorted(lista, key=chiave_nome)
    righe = []
    for c in lista:
        cls = ' class="soon"' if c["soon"] or c["passata"] else ""
        citta = f'<td class="cc">{h(c["citta"] or "–")}</td>' if mostra_citta else ""
        righe.append(f'<tr id="c-{h(c["id"])}"{cls}>{cella_nome(c)}{citta}<td class="cz">{h(c["cap"] or "–")}</td>'
                     f'<td class="n cu">{unita_txt(c)}</td><td class="n cf">{fha_txt(c)}</td>'
                     f'<td class="ce">{data_tab(c["scadenza"])} {etichetta_scadenza(c)}</td></tr>')
    th_citta = '<th>City</th>' if mostra_citta else ""
    filt = ""
    if filtro and len(lista) > 12:
        filt = (f'<div class="filtro-box"><label>{ico("filter")}<span class="sr">Filter this list</span>'
                f'<input class="filtro" type="search" data-filtro="{tid}" placeholder="Filter by name, street, city or ZIP" autocomplete="off"></label>'
                f'<span class="filtro-n" id="{tid}-n" aria-live="polite"></span></div>')
    return (f'{filt}<div class="tab"><table class="ct ta" id="{tid}"><thead><tr><th>Condo project</th>{th_citta}<th>ZIP</th>'
            f'<th class="n">Units</th><th class="n" title="Share of units with FHA-insured mortgages, as listed by HUD">FHA share</th>'
            f'<th>Approved until</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>')


def tabella_recenti(lista, tid, mostra_citta=True):
    lista = sorted(lista, key=lambda c: (((c["scadenza"] if c["tipo"] == "E" else c["data_stato"]) or ""), c["nome"].lower()), reverse=True)
    righe = []
    for c in lista:
        if c["tipo"] == "E" and c["stato"] == "Approved":
            st = f'<span class="badge b-soon">Approval ends</span> {data_tab(c["scadenza"])}'
        elif c["tipo"] == "E":
            st = f'<span class="badge b-bad">Expired</span> {data_tab(c["scadenza"])}'
        else:
            st = f'<span class="badge b-mute">Withdrawn</span> {data_tab(c["data_stato"])}'
        citta = f'<td class="cc">{h(c["citta"] or "–")}</td>' if mostra_citta else ""
        righe.append(f'<tr id="c-{h(c["id"])}">{cella_nome(c)}{citta}<td class="cz">{h(c["cap"] or "–")}</td>'
                     f'<td class="n cu">{unita_txt(c)}</td><td class="ce">{st}</td></tr>')
    th_citta = '<th>City</th>' if mostra_citta else ""
    filt = ""
    if len(lista) > 12:
        filt = (f'<div class="filtro-box"><label>{ico("filter")}<span class="sr">Filter this list</span>'
                f'<input class="filtro" type="search" data-filtro="{tid}" placeholder="Filter by name, street, city or ZIP" autocomplete="off"></label>'
                f'<span class="filtro-n" id="{tid}-n" aria-live="polite"></span></div>')
    return (f'{filt}<div class="tab"><table class="ct tr" id="{tid}"><thead><tr><th>Condo project</th>{th_citta}<th>ZIP</th>'
            f'<th class="n">Units</th><th>Status and date</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>')


def riquadro_stats(lista):
    A = approvati(lista)
    R = recenti(lista)
    soon = [c for c in A if c["soon"]]
    unita = [c["unita"] for c in A if c["unita"] is not None]
    tot_u = sum(unita)
    nota_u = "" if len(unita) == len(A) else f" (in {intero(len(unita))} of {intero(len(A))} projects)"
    return f"""<section class="card stats pull" aria-label="Key figures">
<div class="stat main"><b>{intero(len(A))}</b><span>FHA-approved condo {"project" if len(A) == 1 else "projects"}</span></div>
<div class="stat"><b>{intero(tot_u) if unita else "–"}</b><span>units listed by HUD{nota_u}</span></div>
<div class="stat soon"><b>{intero(len(soon))}</b><span>approvals expire in the next {MESI_SCADENZA} months</span></div>
<div class="stat"><b>{intero(len(R))}</b><span>expired or withdrawn in the last {MESI_RECENTI} months</span></div>
<p class="asof"><span>{ico("calendar")} HUD data as of <b>{data_lunga(ASOF)}</b> · updated weekly</span><a href="{HUD_LOOKUP}" rel="noopener">Official HUD lookup {ico("ext")}</a></p>
</section>"""


def griglia(voci):
    return '<ul class="griglia">' + "".join(f'<li><a href="{{rel}}{u}"><span>{h(t)}</span><small>{s}</small></a></li>' for u, t, s in voci) + "</ul>"


def tabella_luoghi(righe_luoghi, intestazione, tid):
    """righe_luoghi: [(nome, url o None, approvati, soon, recenti)]"""
    righe = "".join(
        f'<tr><td>{f"<a href=\"{{rel}}{u}\">{h(n)}</a>" if u else h(n)}</td><td class="n">{intero(a)}</td>'
        f'<td class="n hide-s">{intero(s) if s else "–"}</td><td class="n hide-s">{intero(r) if r else "–"}</td></tr>'
        for n, u, a, s, r in righe_luoghi)
    return (f'<div class="tab"><table class="pl" id="{tid}"><thead><tr><th>{intestazione}</th><th class="n">Approved</th>'
            f'<th class="n hide-s">Expire within 6 months</th><th class="n hide-s">Expired or withdrawn (24 months)</th></tr></thead>'
            f'<tbody>{righe}</tbody></table></div>')


def conta(lista):
    A = approvati(lista)
    return len(A), sum(1 for c in A if c["soon"]), len(recenti(lista))


def dataset_ld(nome_ds, descr, url_pag, luogo):
    return {"@context": "https://schema.org", "@type": "Dataset", "name": nome_ds, "description": descr, "url": URL_SITO + "/" + url_pag,
            "creator": {"@type": "Organization", "name": NOME, "url": URL_SITO + "/"}, "isBasedOn": HUD_LOOKUP,
            "sourceOrganization": ORG_HUD, "dateModified": ASOF.isoformat(), "temporalCoverage": f"{INIZIO_RECENTI.isoformat()}/{ASOF.isoformat()}",
            "spatialCoverage": {"@type": "Place", "name": luogo}, "license": "https://www.usa.gov/government-copyright",
            "isAccessibleForFree": True}


def link_guide():
    return f"""<div class="cols" style="margin-top:22px">
<a class="card guida" href="{{rel}}is-my-condo-fha-approved/"><b>Is my condo FHA approved?</b><span>How to read HUD's listing: expiration dates, phases and the FHA concentration.</span><em>How to check {ico("arrow")}</em></a>
<a class="card guida" href="{{rel}}condo-not-fha-approved/"><b>Not on the list?</b><span>Single-unit approval, asking the association to apply, and other loans.</span><em>See your options {ico("arrow")}</em></a></div>"""


def scadenze_prossime(lista, mostra_citta=True, url=None):
    """url: pagina corrente; se il condominio non è nella tabella di questa pagina, il link va alla sua pagina."""
    soon = sorted((c for c in approvati(lista) if c["soon"] or c["passata"]), key=lambda c: (c["scadenza"], chiave_nome(c)))

    def ancora(c):
        return f'#c-{h(c["id"])}' if url is None or pagina_di(c) == url else f'{{rel}}{pagina_di(c)}#c-{h(c["id"])}'
    if not soon:
        return (f'<h2 id="expiring">Approvals expiring in the next {MESI_SCADENZA} months</h2>'
                f'<p class="lead">None: every approval here runs past {data_lunga(LIMITE_SOON)}.</p>')
    voci = "".join(f'<li><a href="{ancora(c)}">{h(c["nome"])}</a><span>{h(c["citta"]) if mostra_citta and c["citta"] else ""}</span>'
                   f'<b>{data_tab(c["scadenza"])}</b></li>' for c in soon[:12])
    altro = (f'<p class="small">…and {intero(len(soon) - 12)} more, marked in the {"table below" if url is None else "tables of the county and city pages"}.</p>'
             if len(soon) > 12 else "")
    return (f'<h2 id="expiring">Approvals expiring in the next {MESI_SCADENZA} months ({intero(len(soon))})</h2>'
            f'<p class="lead">HUD usually approves a project for three years at a time. Renewal can be requested from six months before to six months after '
            f'the expiration date (<a href="{CFR_FHA}" rel="noopener">24 CFR 203.43b(h)(4)</a>), so an approval that is about to expire may be renewed, '
            f'or it may lapse. If you are buying in one of these projects, ask your lender to check the status again shortly before closing.</p>'
            f'<div class="card scad-card"><ul class="scad">{voci}</ul>{altro}</div>')


# ---------------------------------------------------------------- pagine dei luoghi
def frase_apertura(n, luogo, soon):
    if n == 0:
        return (f"No condo project in {luogo} is on HUD's FHA-approved list as of {data_lunga(ASOF)}. "
                "Below are the projects whose approval expired or was withdrawn recently.")
    s = f"<strong>{plur(n, 'condo project')}</strong> in {luogo} {'is' if n == 1 else 'are'} on HUD's FHA-approved list as of {data_lunga(ASOF)}"
    if soon:
        s += f"; {intero(soon)} of the approvals expire in the next {MESI_SCADENZA} months"
    return s + "."


def pagina_stato(st):
    lista = STATI_C[st]
    A, R = approvati(lista), recenti(lista)
    nome = nome_stato(st)
    n, soon, nr = conta(lista)
    url = url_stato(st)
    # contee e città
    cont = defaultdict(list)
    for c in lista:
        cont[c["ck"]].append(c)
    righe_c = []
    for ck, l in sorted(cont.items(), key=lambda kv: (-len(approvati(kv[1])), kv[0] or "~")):
        a, s, r = conta(l)
        if not ck:
            continue
        righe_c.append((nome_contea(ck), link_contea(st, ck), a, s, r))
    senza_contea = len(approvati(cont.get(None, [])))
    citt = defaultdict(list)
    for c in lista:
        citt[c["tk"]].append(c)
    righe_t = []
    for tk, l in sorted(citt.items(), key=lambda kv: (-len(approvati(kv[1])), kv[0] or "~")):
        if not tk:
            continue
        a, s, r = conta(l)
        righe_t.append((NOME_CITTA[(st, tk)], link_citta(st, tk), a, s, r))
    pagine_c = [(u, nm, f"{plur(a, 'approved project')}") for nm, u, a, s, r in righe_c if u and u in URL_CONTEA.values()]
    pagine_t = [(u, nm, f"{plur(a, 'approved project')}") for nm, u, a, s, r in righe_t if u]
    luogo_txt = nome
    fc = floodcost_stato(st)
    corpo = [riquadro_stats(lista), avviso()]
    if pagine_c or pagine_t:
        corpo.append(f'<h2>Browse {h(nome)} by county and city</h2>')
        if pagine_c:
            corpo.append(f'<h3>Counties with at least {SOGLIA_CONTEA} approved projects</h3>{griglia(pagine_c)}')
        if pagine_t:
            corpo.append(f'<h3>Cities with at least {SOGLIA_CITTA} approved projects</h3>{griglia(pagine_t)}')
    if A:
        corpo.append(scadenze_prossime(lista, url=None if n <= LIMITE_LISTA_STATO else url))
        if n <= LIMITE_LISTA_STATO:
            corpo.append(f'<h2 id="list">All FHA-approved condos in {h(nome)} ({intero(n)})</h2>'
                         f'<p class="lead">Sorted by name. Units and FHA share are as listed by HUD; "–" means HUD gives no figure. '
                         f'Search the HUD ID in the official lookup to see which phases or buildings are covered.</p>')
        else:
            fuori = [c for c in A if pagina_di(c) == url]
            corpo.append(f'<h2 id="list">FHA-approved condos in the rest of {h(nome)} ({intero(len(fuori))})</h2>'
                         f'<p class="lead">{h(nome)} has {intero(n)} approved projects. {intero(n - len(fuori))} of them are listed on the county and city pages above; '
                         f'here are the other {intero(len(fuori))}, in counties and cities without a page of their own. You can also search them all with the box on the '
                         f'<a href="{{rel}}">home page</a>. Units and FHA share are as listed by HUD; "–" means HUD gives no figure.</p>')
            A = fuori
        corpo.append(tabella_approvati(A, "t-a"))
    corpo.append(AD)
    if len(righe_c) > 1:
        corpo.append(f'<h2 id="counties">FHA-approved condos by county in {h(nome)}</h2>'
                     + tabella_luoghi(righe_c, "County", "t-co")
                     + (f'<p class="small">{plur(senza_contea, "approved project")} {"has" if senza_contea == 1 else "have"} no county in HUD\'s record.</p>' if senza_contea else ""))
    if len(righe_t) > 1:
        corpo.append(f'<details class="tutti"><summary>FHA-approved condos by city ({intero(len(righe_t))} cities)</summary>'
                     + tabella_luoghi(righe_t, "City", "t-ci") + "</details>")
    if R:
        corpo.append(f'<h2 id="recent">Recently expired or withdrawn in {h(nome)} ({intero(len(R))})</h2>'
                     f'<p class="lead">Projects whose FHA approval expired, or was withdrawn, between {data_lunga(INIZIO_RECENTI)} and {data_lunga(ASOF)}. '
                     f'An FHA loan in these projects needs a new or renewed project approval, or a single-unit approval.</p>')
        corpo.append(tabella_recenti(R, "t-r"))
    corpo.append(blocco_affiliati())
    corpo.append(link_guide())
    if fc:
        corpo.append(f'<p class="lead" style="margin-top:26px">{ico("info")} Buying a condo near the water? See <a href="{FLOODCOST}/{fc}" rel="noopener">what flood insurance costs in {h(nome)}</a> on FloodCost.</p>')
    corpo.append(fonte_box())
    sub = frase_apertura(n, h(luogo_txt), soon)
    testata = banda(f"FHA condo list · {nome}", f"FHA-approved condos in {nome}", sub,
                    f'<ul class="trust"><li>{ico("db")}Copied from HUD\'s official list</li><li>{ico("calendar")}Updated weekly</li>'
                    f'<li>{ico("shield")}Free, no sign-up</li></ul>')
    titolo_p = f"FHA Approved Condos in {nome}: {intero(n)} on HUD's List ({mese_anno(ASOF)})"
    descr = (f"{'All ' if n > 1 else ''}{plur(n, 'FHA-approved condo project')} in {nome} from HUD's list, by county and city, with approval "
             f"expiration dates. HUD data as of {data_breve(ASOF)}.")
    if n == 0:
        titolo_p = f"FHA Approved Condos in {nome}: None Listed Now ({mese_anno(ASOF)})"
        descr = (f"No condo project in {nome} is on HUD's FHA-approved list as of {data_lunga(ASOF)}. See the {intero(nr)} recently expired or withdrawn "
                 "projects and your options for an FHA loan.")
    altri = [(FLOODCOST + "/" + fc, f"Flood insurance cost in {nome}", "Median NFIP premiums by county and ZIP code, on FloodCost")] if fc else None
    pagina(url, titolo_p, descr, "\n".join(corpo), briciole=[(nome, url)], testata=testata,
           jsonld_extra=dataset_ld(f"FHA-approved condominium projects in {nome}", descr, url, nome), altri=altri)
    return 1


def pagina_luogo(tipo, st, k):
    """tipo 'contea' o 'citta'."""
    if tipo == "contea":
        lista = CONTEE_C[(st, k)]
        nome = nome_contea(k)
        url = URL_CONTEA[(st, k)]
    else:
        lista = CITTA_C[(st, k)]
        nome = NOME_CITTA[(st, k)]
        url = URL_CITTA[(st, k)]
    A, R = approvati(lista), recenti(lista)
    n, soon, nr = conta(lista)
    nome_st = nome_stato(st)
    luogo = f"{nome}, {st}"
    luogo_in = con_articolo(luogo)  # dopo "in": "in the City of Alexandria, VA"
    corpo = [riquadro_stats(lista), avviso()]
    fc_c = None
    if tipo == "contea":
        citt = defaultdict(list)
        for c in lista:
            citt[c["tk"]].append(c)
        righe_t = [(NOME_CITTA[(st, tk)], (link_citta(st, tk) if link_citta(st, tk) != url else None), *conta(l)) for tk, l in
                   sorted(citt.items(), key=lambda kv: (-len(approvati(kv[1])), kv[0] or "~")) if tk]
        fc_c = floodcost_contea(st, k)
    else:
        cont = Counter(c["ck"] for c in A if c["ck"])
        righe_t = []
    if tipo == "contea" and k.endswith(" CITY") and k != "CARSON CITY":
        gemella = URL_CITTA.get((st, chiave_citta(k[:-5])))
        if gemella:
            citta_n = nome[len("City of "):]
            corpo.append(f'<p class="small" style="margin-top:16px">{ico("info")} This page lists the projects that HUD records in the independent '
                         f'city of {h(citta_n)}. The <a href="{{rel}}{gemella}">{h(citta_n)} page</a> lists every project whose mailing address is in '
                         f'{h(citta_n)}, including those in neighboring counties.</p>')
    corpo.append(scadenze_prossime(lista, mostra_citta=(tipo == "contea")))
    corpo.append(f'<h2 id="list">All FHA-approved condos in {h(luogo_in)} ({intero(n)})</h2>'
                 f'<p class="lead">Sorted by name. Units and FHA share are as listed by HUD; "–" means HUD gives no figure. '
                 f'Search the HUD ID in the official lookup to see which phases or buildings are covered.</p>')
    corpo.append(tabella_approvati(A, "t-a", mostra_citta=(tipo == "contea")))
    corpo.append(AD)
    if tipo == "contea" and len(righe_t) > 1:
        corpo.append(f'<h2 id="cities">By city in {h(con_articolo(nome))}</h2>' + tabella_luoghi(righe_t, "City", "t-ci"))
    if tipo == "citta" and cont:
        voci = []
        for ck, m in cont.most_common():
            u = link_contea(st, ck)
            voci.append((f'<a href="{{rel}}{u}">{h(nome_contea(ck))}</a>' if u and u != url else h(nome_contea(ck))) + f" ({intero(m)})")
        corpo.append(f'<p class="small" style="margin-top:14px">County in HUD\'s records: {", ".join(voci)}.</p>')
    if R:
        corpo.append(f'<h2 id="recent">Recently expired or withdrawn in {h(luogo_in)} ({intero(len(R))})</h2>'
                     f'<p class="lead">Projects whose FHA approval expired, or was withdrawn, between {data_lunga(INIZIO_RECENTI)} and {data_lunga(ASOF)}.</p>')
        corpo.append(tabella_recenti(R, "t-r", mostra_citta=(tipo == "contea")))
    corpo.append(blocco_affiliati())
    corpo.append(link_guide())
    altri = None
    if fc_c:
        corpo.append(f'<p class="lead" style="margin-top:26px">{ico("info")} Buying near the water? See <a href="{FLOODCOST}/{fc_c}" rel="noopener">'
                     f'flood insurance cost in {h(con_articolo(nome))}</a> on FloodCost.</p>')
        altri = [(FLOODCOST + "/" + fc_c, f"Flood insurance cost in {con_articolo(nome)}", "Median NFIP premiums and flood claims, on FloodCost")]
    elif floodcost_stato(st):
        altri = [(FLOODCOST + "/" + floodcost_stato(st), f"Flood insurance cost in {nome_st}", "Median NFIP premiums by county and ZIP code, on FloodCost")]
    corpo.append(f'<p class="small" style="margin-top:20px">More in {h(nome_st)}: <a href="{{rel}}{url_stato(st)}">all FHA-approved condos in {h(nome_st)}</a>.</p>')
    corpo.append(fonte_box())
    # contea con quasi lo stesso elenco (si cita, salvo che sia la città indipendente con lo stesso nome: NORFOLK CITY)
    gemella = ([nome_contea(ck) for (st2, ck), u in ALIAS_CONTEA.items() if u == url and ck != f"{k} CITY"]
               if tipo == "citta" else [])
    sub = frase_apertura(n, h(luogo_in), soon)
    if gemella:
        sub += f" This list also covers {h(gemella[0])}: HUD records almost the same projects for the city and the county."
    testata = banda(f"FHA condo list · {nome_st}", f"FHA-approved condos in {luogo_in}", sub,
                    f'<ul class="trust"><li>{ico("db")}Copied from HUD\'s official list</li><li>{ico("calendar")}Updated weekly</li>'
                    f'<li>{ico("shield")}Free, no sign-up</li></ul>')
    progetti = plur(n, "Project")
    if gemella:
        titolo_p = f"FHA Approved Condos in {nome} & {gemella[0]}, {st} ({mese_anno(ASOF)})"
    else:
        titolo_p = f"FHA Approved Condos in {luogo_in}: {progetti} ({mese_anno(ASOF)})"
    if len(titolo_p) > 64:
        titolo_p = titolo_p.rsplit(" (", 1)[0]  # senza il mese: i titoli lunghi Google li taglia
    descr = (f"{plur(n, 'FHA-approved condo project')} in {luogo_in}, from HUD's list, with street, ZIP, units and expiration date. "
             f"HUD data as of {data_breve(ASOF)}.")
    pagina(url, titolo_p, descr, "\n".join(corpo), briciole=[(nome_st, url_stato(st)), (nome, url)], testata=testata,
           jsonld_extra=dataset_ld(f"FHA-approved condominium projects in {luogo}", descr, url, f"{nome}, {nome_st}"), altri=altri)
    return 1


# ---------------------------------------------------------------- home e indice degli Stati
TESSERE = {"AK": (0, 0), "ME": (0, 10), "VT": (1, 9), "NH": (1, 10), "WA": (2, 0), "ID": (2, 1), "MT": (2, 2), "ND": (2, 3), "MN": (2, 4),
           "IL": (2, 5), "WI": (2, 6), "MI": (2, 7), "NY": (2, 8), "RI": (2, 9), "MA": (2, 10), "OR": (3, 0), "NV": (3, 1), "WY": (3, 2),
           "SD": (3, 3), "IA": (3, 4), "IN": (3, 5), "OH": (3, 6), "PA": (3, 7), "NJ": (3, 8), "CT": (3, 9), "CA": (4, 0), "UT": (4, 1),
           "CO": (4, 2), "NE": (4, 3), "MO": (4, 4), "KY": (4, 5), "WV": (4, 6), "VA": (4, 7), "MD": (4, 8), "DE": (4, 9), "AZ": (5, 1),
           "NM": (5, 2), "KS": (5, 3), "AR": (5, 4), "TN": (5, 5), "NC": (5, 6), "SC": (5, 7), "DC": (5, 8), "OK": (6, 3), "LA": (6, 4),
           "MS": (6, 5), "AL": (6, 6), "GA": (6, 7), "HI": (7, 0), "TX": (7, 3), "FL": (7, 8), "PR": (7, 10)}


def n_appr(st):
    return len(approvati(STATI_C.get(st, [])))


def mappa_stati():
    limiti = [1, 25, 100, 300, 1000]

    def classe(m):
        return sum(m >= x for x in limiti)
    celle = []
    for r in range(8):
        for col in range(11):
            st = next((s for s, p in TESSERE.items() if p == (r, col)), None)
            if not st:
                continue
            m = n_appr(st)
            if st in STATI_C:
                celle.append(f'<a class="m{max(1, classe(m)) if m else 0}" href="{{rel}}{url_stato(st)}" title="{h(nome_stato(st))}: {plur(m, "approved project")}" '
                             f'style="grid-row:{r + 1};grid-column:{col + 1}">{st}<small>{intero(m)}</small></a>')
            else:
                celle.append(f'<span class="m0" style="grid-row:{r + 1};grid-column:{col + 1}" title="{h(nome_stato(st))}: none listed">{st}</span>')
    leg = ('<li><i class="m0" style="background:var(--mute)"></i>0</li><li><i class="m1"></i>1–24</li><li><i class="m2"></i>25–99</li>'
           '<li><i class="m3"></i>100–299</li><li><i class="m4"></i>300–999</li><li><i class="m5"></i>1,000+</li>')
    return (f'<div class="card"><div class="mappa" role="list" aria-label="FHA-approved condo projects by state">{"".join(celle)}</div>'
            f'<ul class="legenda" aria-label="Legend">{leg}</ul><p class="small" style="margin:8px 0 0;text-align:center">Number of FHA-approved condo projects, HUD data as of {data_lunga(ASOF)}. '
            f'Each tile links to the state list.</p></div>')


def blocco_cerca():
    tot = len(CONDOMINI)
    esempi = ["Fairfax", "22003", "Denver", "Harbor"]
    bott = ", ".join(f'<button type="button" data-es="{h(e)}">{h(e)}</button>' for e in esempi)
    return f"""<section class="card cerca-card" id="search" data-cerca data-url="{{rel}}data/search.json" data-rel="{{rel}}">
<form role="search" action="{{rel}}" method="get"><label for="q">{ico("search")}Is the condo on HUD's FHA-approved list?</label>
<div class="cerca-box">{ico("building")}<input id="q" name="q" class="cerca" type="search" placeholder="Name, city, ZIP or HUD ID" autocomplete="off" enterkeyhint="search"></div></form>
<div class="risultati" aria-live="polite"></div>
<p class="esempi">Try: {bott}. The search runs in your browser on {intero(tot)} projects: all FHA-approved ones and those that expired or were withdrawn in the last {MESI_RECENTI} months.</p>
</section>"""


def home():
    A = [c for c in CONDOMINI if c["tipo"] == "A"]
    soon = sum(1 for c in A if c["soon"])
    R = len(CONDOMINI) - len(A)
    n_stati = sum(1 for s in STATI_C if n_appr(s))
    unita = sum(c["unita"] for c in A if c["unita"] is not None)
    top_st = sorted((s for s in STATI_C if n_appr(s)), key=lambda s: -n_appr(s))[:3]
    top_txt = ", ".join(f"{nome_stato(s)} ({intero(n_appr(s))})" for s in top_st)
    citta_top = sorted(URL_CITTA, key=lambda k: -len(approvati(CITTA_C[k])))[:12]
    contee_top = sorted(URL_CONTEA, key=lambda k: -len(approvati(CONTEE_C[k])))[:12]
    tre = sum(1 for c in A if c["data_stato"] and c["scadenza"] and piu_mesi(date.fromisoformat(c["data_stato"]), 36).isoformat() == c["scadenza"])
    testata = banda("HUD data · updated weekly", "Is the condo FHA approved?",
                    f"Search HUD's list of <strong>{intero(len(A))} FHA-approved condo projects</strong> by name, city or ZIP code, and browse every state, county and city. "
                    f"Each listing shows when the approval expires.",
                    f'<ul class="trust"><li>{ico("db")}Copied from HUD\'s official lookup</li><li>{ico("calendar")}HUD data as of {data_lunga(ASOF)}</li>'
                    f'<li>{ico("shield")}Free, no sign-up, no tracking</li></ul>')
    corpo = f"""<div class="pull">{blocco_cerca()}</div>
<section class="card stats" style="margin-top:22px" aria-label="Key figures, United States">
<div class="stat main"><b>{intero(len(A))}</b><span>FHA-approved condo projects in {n_stati} states and territories</span></div>
<div class="stat"><b>{intero(unita)}</b><span>units in projects where HUD states a unit count</span></div>
<div class="stat soon"><b>{intero(soon)}</b><span>approvals expire in the next {MESI_SCADENZA} months</span></div>
<div class="stat"><b>{intero(R)}</b><span>expired or withdrawn in the last {MESI_RECENTI} months</span></div>
<p class="asof"><span>{ico("calendar")} HUD data as of <b>{data_lunga(ASOF)}</b> · updated weekly</span><a href="{HUD_LOOKUP}" rel="noopener">Official HUD lookup {ico("ext")}</a></p>
</section>
{avviso()}
<h2>FHA-approved condos by state</h2>
<p class="lead">The most approved projects are in {top_txt}. Open a state for its counties, cities and the full list.</p>
{mappa_stati()}
<details class="tutti"><summary>All states and territories in a list</summary>{griglia([(url_stato(s), nome_stato(s), plur(n_appr(s), "approved project")) for s in sorted(STATI_C, key=nome_stato)])}</details>
{AD}
<h2>Counties with the most FHA-approved condos</h2>
{griglia([(URL_CONTEA[k], f"{nome_contea(k[1])}, {k[0]}", plur(len(approvati(CONTEE_C[k])), "approved project")) for k in contee_top])}
<h2>Cities with the most FHA-approved condos</h2>
{griglia([(URL_CITTA[k], f"{NOME_CITTA[k]}, {k[0]}", plur(len(approvati(CITTA_C[k])), "approved project")) for k in citta_top])}
<h2>Guides</h2>
<div class="cols3">
<a class="card guida" href="{{rel}}is-my-condo-fha-approved/"><b>Is my condo FHA approved? How to check</b><span>Find the project, read the expiration date, the phases covered and the FHA concentration.</span><em>Read the guide {ico("arrow")}</em></a>
<a class="card guida" href="{{rel}}condo-not-fha-approved/"><b>What if a condo is not FHA approved?</b><span>Single-unit approval, project approval, renewals, and other loan types.</span><em>See your options {ico("arrow")}</em></a>
<a class="card guida" href="{{rel}}fha-vs-va-vs-warrantable-condos/"><b>FHA vs VA vs warrantable condos</b><span>Who approves what, where to check, and the rules behind each.</span><em>Compare {ico("arrow")}</em></a>
</div>
<h2>How this list works</h2>
<div class="cols"><div class="card"><h3 style="margin-top:0">What it is</h3><p class="small">HUD keeps the official list of condominium projects approved for FHA-insured mortgages in its FHA Condominium Lookup, a search form that shows 25 results at a time. Every week we download the whole list for all {len(NOMI_STATI)} states and territories and publish it by place. {intero(tre)} of the {intero(len(A))} current approvals run exactly three years, the standard term set by HUD's rule.</p></div>
<div class="card"><h3 style="margin-top:0">What it is not</h3><p class="small">It is not HUD's site and not a loan approval. An approval can expire, be renewed or be withdrawn after our last download, and some approvals cover only part of a project. Always confirm with the <a href="{HUD_LOOKUP}" rel="noopener">HUD lookup</a> and your lender. <a href="{{rel}}methodology/">Read the methodology</a>.</p></div></div>
{fonte_box()}"""
    pagina("", f"FHA Approved Condos List: Search HUD's {intero(len(A))} Approved Projects",
           f"Is the condo FHA approved? Search HUD's list of {intero(len(A))} FHA-approved condo projects by name, city or ZIP code, "
           f"with approval expiration dates. Updated weekly.", corpo, testata=testata)


def pagina_stati():
    righe = []
    for s in sorted(NOMI_STATI, key=nome_stato):
        l = STATI_C.get(s, [])
        a, so, r = conta(l)
        nome = f'<a href="{{rel}}{url_stato(s)}">{h(nome_stato(s))}</a>' if s in STATI_C else h(nome_stato(s))
        righe.append((nome, a, so, r))
    tab = "".join(f'<tr><td>{n}</td><td class="n">{intero(a)}</td><td class="n hide-s">{intero(s) if s else "–"}</td>'
                  f'<td class="n hide-s">{intero(r) if r else "–"}</td></tr>' for n, a, s, r in righe)
    tot = sum(r[1] for r in righe)
    corpo = f"""<div class="pull">{mappa_stati()}</div>
{avviso()}
<h2>All states and territories</h2>
<div class="tab"><table class="pl"><thead><tr><th>State or territory</th><th class="n">Approved</th><th class="n hide-s">Expire within 6 months</th><th class="n hide-s">Expired or withdrawn (24 months)</th></tr></thead><tbody>{tab}</tbody>
<tfoot><tr><td><strong>Total</strong></td><td class="n"><strong>{intero(tot)}</strong></td><td class="hide-s"></td><td class="hide-s"></td></tr></tfoot></table></div>
<p class="small">States and territories without a link have no approved project and none that expired or was withdrawn in the last {MESI_RECENTI} months.</p>
{fonte_box()}"""
    testata = banda("FHA condo list · by state", "FHA-approved condos by state",
                    f"{intero(tot)} condo projects are on HUD's FHA-approved list as of {data_lunga(ASOF)}. Pick a state for its counties, cities and the full list.")
    pagina("states/", f"FHA Approved Condos by State: HUD List ({mese_anno(ASOF)})",
           f"How many condo projects are FHA approved in each state: {intero(tot)} in total on HUD's list, with approvals expiring soon and recent expirations.",
           corpo, briciole=[("States", "states/")], testata=testata)


# ---------------------------------------------------------------- guide
def stat_naz():
    A = [c for c in CONDOMINI if c["tipo"] == "A"]
    tre = sum(1 for c in A if c["data_stato"] and c["scadenza"] and piu_mesi(date.fromisoformat(c["data_stato"]), 36).isoformat() == c["scadenza"])
    soon = sum(1 for c in A if c["soon"])
    dl = sum(1 for c in A if c["metodo"].upper() == "DELRAP")
    hr = sum(1 for c in A if c["metodo"].upper() == "HRAP")
    E = sum(1 for c in CONDOMINI if c["tipo"] == "E")
    W = sum(1 for c in CONDOMINI if c["tipo"] == "W")
    return {"A": len(A), "tre": tre, "soon": soon, "dl": dl, "hr": hr, "E": E, "W": W}


def guida_controllo():
    S = stat_naz()
    corpo = f"""<div class="pull">{blocco_cerca()}</div>
<div class="testo">
<p class="lead" style="margin-top:24px"><strong>Short answer:</strong> for an FHA-insured mortgage, the condo unit generally has to be in a project approved by HUD or by a lender with HUD's DELRAP authority. The other routes are a single-unit approval or, for some detached or townhouse-style projects, the "site condominium" rules (<a href="{CFR_FHA}" rel="noopener">24 CFR 203.43b(c)</a>). Here is how to check a project in a few minutes.</p>
<ol class="passi">
<li><h3>Search the project on this site</h3><p>Type the condo name, the city or the ZIP code in the box above. HUD's lookup cuts project names at 30 characters and often abbreviates them (for example "CONDO" for "Condominium"), so one distinctive word or the ZIP code works best. Each result shows whether the approval is current and when it expires.</p></li>
<li><h3>Confirm it on HUD's official lookup</h3><p>Open the <a href="{HUD_LOOKUP}" rel="noopener">HUD FHA Condominium Lookup</a>. Choose the state, then enter the city, the ZIP code or the start of the name, and leave the other fields empty. With "Status" set to "All" (the default), expired and withdrawn projects are shown too. Our list is a weekly copy, so HUD's page is the one that counts.</p></li>
<li><h3>Read the status and the dates</h3><p>HUD's lookup shows a status for each project (Approved, Expired, Rejected or Withdrawn), a status date and an expiration date. Unless HUD specifies otherwise in writing, a project is approved for three years from the date it is placed on the list, and HUD can rescind an approval at any time if the project fails to comply with a requirement (<a href="{CFR_FHA}" rel="noopener">24 CFR 203.43b(h)(3)</a>). In HUD's data as of {data_lunga(ASOF)}, {intero(S["tre"])} of the {intero(S["A"])} current approvals run exactly three years.</p></li>
<li><h3>Check which phases or buildings are covered</h3><p>The "Composition of Project" column in HUD's lookup describes what is approved, for example "PHASES 1-8" or "BLDG C, D, E". If the unit you want is in a building or phase that is not listed, the project approval may not cover it. We do not copy that column, because it is free text; read it on HUD's page.</p></li>
<li><h3>Look at the FHA concentration</h3><p>HUD sets a maximum share of units in a project that can have FHA-insured mortgages; under the rule, the limit must be between 25% and 75%, and HUD fixes the exact figure by notice. HUD may stop issuing new FHA case numbers in a project that is over the limit (<a href="{CFR_FHA}" rel="noopener">24 CFR 203.43b(d)(6)(viii)</a>). The lookup shows an FHA concentration figure for each project; ask your lender how close the project is to the limit.</p></li>
<li><h3>Ask your lender before you make an offer</h3><p>Give the lender the HUD condo ID shown in the listing. The lender checks the project's status and the loan's other requirements. A project on the list does not mean your loan is approved.</p></li>
</ol>
<h2>What the statuses mean for a buyer</h2>
<div class="tab scorre" style="margin-top:6px"><table class="cmp"><thead><tr><th>Status</th><th>What it means</th></tr></thead><tbody>
<tr><td><span class="badge b-ok">Approved</span></td><td>The project is on HUD's list of approved condominium projects until the expiration date shown (<a href="{CFR_FHA}" rel="noopener">203.43b(h)(2)</a>).</td></tr>
<tr><td><span class="badge b-soon">Expiring soon</span></td><td>Our label for approvals that end within {MESI_SCADENZA} months ({intero(S["soon"])} nationwide). The project can request renewal from six months before to six months after expiration, using updated information (<a href="{CFR_FHA}" rel="noopener">203.43b(h)(4)</a>).</td></tr>
<tr><td><span class="badge b-bad">Expired</span></td><td>The approval period ended. If the renewal request comes more than six months after expiration, a complete new application is required (<a href="{CFR_FHA}" rel="noopener">203.43b(h)(4)</a>). {intero(S["E"])} approvals expired or reached their expiration date in the last {MESI_RECENTI} months.</td></tr>
<tr><td><span class="badge b-mute">Withdrawn</span></td><td>HUD lists the project as withdrawn, with the date of the change ({intero(S["W"])} in the last {MESI_RECENTI} months). An FHA loan then needs a new project approval or one of the other routes in <a href="{{rel}}condo-not-fha-approved/">this guide</a>.</td></tr>
</tbody></table></div>
<h2>Who approves a condo project</h2>
<p>A project can be approved by HUD itself or by a lender with Direct Endorsement Lender Review and Approval Process (DELRAP) authority; the application goes to one or the other, and an approved project is placed on HUD's list (<a href="{CFR_FHA}" rel="noopener">24 CFR 203.43b(h)(1)–(2)</a>). HUD's lookup shows which route was used in the "Approval Method" column: of the current approvals, {intero(S["hr"])} went through HUD's own review (HRAP) and {intero(S["dl"])} through a DELRAP lender.</p>
<h2>Why a condo might not be on the list</h2>
<ul><li>No one has applied: approval is not automatic. An application has to be submitted to HUD or to a DELRAP lender (<a href="{CFR_FHA}" rel="noopener">203.43b(h)(1)</a>).</li>
<li>The approval expired or was withdrawn: search with status "All" in HUD's lookup, or look at the "recently expired" section of the city or county page here.</li>
<li>The project is listed under a different or shortened name: try the ZIP code or one distinctive word.</li>
<li>It may not meet the requirements: for example, a project must be primarily residential, not intended for transient or hotel rentals, and complete (<a href="{CFR_FHA}" rel="noopener">203.43b(d)</a>).</li></ul>
<p>If the project is not approved, there may still be a way: see <a href="{{rel}}condo-not-fha-approved/">what to do if a condo is not FHA approved</a>.</p>
<p class="cite">Sources: 24 CFR 203.43b, as published in the Federal Register on August 15, 2019 (<a href="{FR_2019}" rel="noopener">84 FR 41846</a>) and current in the eCFR; HUD FHA Condominium Lookup. Read on {data_lunga(CONTROLLO_FONTI)}. Counts from HUD data as of {data_lunga(ASOF)}.</p>
</div>
{fonte_box()}"""
    testata = banda("Guide", "Is my condo FHA approved? How to check",
                    "Search the project, confirm it on HUD's lookup and read what the listing really says: expiration date, phases covered and FHA concentration.")
    descr = "How to check if a condo is FHA approved: search HUD's list by name or ZIP, confirm it on the official lookup, and read the expiration date and phases."
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": "Is my condo FHA approved? How to check", "description": descr,
          "dateModified": ASOF.isoformat(), "author": {"@type": "Organization", "name": NOME, "url": URL_SITO + "/"},
          "publisher": {"@type": "Organization", "name": NOME, "url": URL_SITO + "/"}, "mainEntityOfPage": URL_SITO + "/is-my-condo-fha-approved/"}
    pagina("is-my-condo-fha-approved/", "Is My Condo FHA Approved? How to Check HUD's List", descr, corpo,
           briciole=[("Is my condo FHA approved?", "is-my-condo-fha-approved/")], testata=testata, jsonld_extra=ld)


def guida_non_approvato():
    S = stat_naz()
    corpo = f"""<div class="testo pull card" style="padding:22px 24px">
<p class="lead" style="margin:0">If the condo you like is not on HUD's list, an FHA loan is not automatically ruled out. Depending on the project, there are four routes to discuss with your lender. The FHA rules below come from HUD's condominium regulation, <a href="{CFR_FHA}" rel="noopener">24 CFR 203.43b</a>.</p></div>
<div class="testo">
<h2>1. Single-unit approval</h2>
<p>One unit in a project that is not approved can still get a "single-unit approval" (<a href="{CFR_FHA}" rel="noopener">203.43b(a)(6)</a>). Under <a href="{CFR_FHA}" rel="noopener">203.43b(i)</a>, a unit may be eligible if:</p>
<ul><li>the project is not on the list of FHA-approved projects;</li>
<li>HUD has not identified the project as subject to an adverse determination for significant issues that affect its viability;</li>
<li>the project is complete;</li>
<li>the unit is not a manufactured home; and</li>
<li>the project has at least five dwelling units.</li></ul>
<p>The lender (the "mortgagee") must make sure the project meets HUD's standards, which for single-unit approvals can be a subset of the full project rules set by HUD notice. There is also a cap on FHA loans: in projects with 10 or more units, HUD sets a maximum share of FHA-insured units between 0% and 20%; in projects with fewer than 10 units, no more than two units can have FHA-insured mortgages (<a href="{CFR_FHA}" rel="noopener">203.43b(i)(2)</a>). Ask the lender early whether it can process one.</p>
<h2>2. The association applies for project approval</h2>
<p>An application for project approval can be submitted to HUD or to a lender with DELRAP authority; if all the criteria are met, the project is approved and placed on HUD's list (<a href="{CFR_FHA}" rel="noopener">203.43b(h)(1)–(2)</a>). Among other things, the project must be primarily residential and not intended for transient or hotel rentals, consist only of one-family units, be complete and ready for occupancy, and have its plat or development plan approved by the local jurisdiction (<a href="{CFR_FHA}" rel="noopener">203.43b(d)</a>). Further requirements on insurance, finances, owner occupancy, commercial space and reserves are set by HUD through notices, some of them within ranges written in the rule. Of the {intero(S["A"])} approvals on HUD's list as of {data_lunga(ASOF)}, {intero(S["dl"])} came through DELRAP lenders and {intero(S["hr"])} through HUD review.</p>
<h2>3. A recently expired approval can be renewed</h2>
<p>If the project's approval expired, an eligible party can request recertification up to six months after the expiration date by updating the information it already submitted; after six months a complete new application is needed (<a href="{CFR_FHA}" rel="noopener">203.43b(h)(4)</a>). {intero(S["E"])} approvals expired or reached their expiration date in the last {MESI_RECENTI} months: each state, county and city page here lists them, so you can see whether the project you like is one of them.</p>
<h2>4. Site condominiums</h2>
<p>A "site condominium" is a project made up entirely of detached homes without shared garages or other attached buildings, or a project of detached or townhouse-style homes where each unit is the home and its land, with no manufactured homes (<a href="{CFR_FHA}" rel="noopener">203.43b(a)(7)</a>). It does not need to be on the approved list, but it must meet the basic project requirements, and the insurance and maintenance costs of each unit must be the sole responsibility of its owner (<a href="{CFR_FHA}" rel="noopener">203.43b(c) and (j)</a>).</p>
<h2>Other loan types</h2>
<ul><li><strong>VA loans</strong> (for eligible veterans and service members) can be used to buy a condo only in a VA-approved project (<a href="{USC_VA}" rel="noopener">38 U.S.C. 3710(a)(6)</a>; <a href="{VA_PURCHASE}" rel="noopener">VA.gov</a>). VA approval is separate from FHA approval: check VA's own list.</li>
<li><strong>Conventional loans</strong> sold to Fannie Mae: before delivering the loan, the lender must determine that the project meets Fannie Mae's eligibility requirements (<a href="{FANNIE_PROJECT}" rel="noopener">Fannie Mae Selling Guide, B4-2.1-01</a>). This review is separate from HUD's list.</li></ul>
<p>See the <a href="{{rel}}fha-vs-va-vs-warrantable-condos/">comparison of FHA, VA and "warrantable" condos</a>.</p>
<p class="cite">Sources: 24 CFR 203.43b (<a href="{CFR_FHA}" rel="noopener">eCFR</a>; <a href="{FR_2019}" rel="noopener">84 FR 41846</a>, August 15, 2019); 38 U.S.C. 3710(a)(6); VA.gov, "VA-backed purchase loan"; Fannie Mae Selling Guide B4-2.1-01 (August 5, 2026). Read on {data_lunga(CONTROLLO_FONTI)}. This is general information, not legal or mortgage advice: your lender applies the current HUD notices and handbooks.</p>
</div>
{fonte_box()}"""
    testata = banda("Guide", "What if a condo is not FHA approved?",
                    "Single-unit approval, a project application, a renewal or another type of loan: what HUD's rules allow, in plain English.", corta=True)
    descr = ("Condo not FHA approved? What HUD's rules allow: single-unit approval and its limits, a project application, renewal of an expired "
             "approval, site condos.")
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": "What if a condo is not FHA approved?", "description": descr,
          "dateModified": ASOF.isoformat(), "author": {"@type": "Organization", "name": NOME, "url": URL_SITO + "/"},
          "publisher": {"@type": "Organization", "name": NOME, "url": URL_SITO + "/"}, "mainEntityOfPage": URL_SITO + "/condo-not-fha-approved/"}
    pagina("condo-not-fha-approved/", "Condo Not FHA Approved? Single-Unit Approval and Other Options", descr, corpo,
           briciole=[("If a condo is not FHA approved", "condo-not-fha-approved/")], testata=testata, jsonld_extra=ld)


def guida_confronto():
    corpo = f"""<div class="pull">
<div class="tab scorre"><table class="cmp"><thead><tr><th></th><th>FHA-approved</th><th>VA-approved</th><th>"Warrantable" (conventional)</th></tr></thead><tbody>
<tr><td>Loan</td><td>FHA-insured mortgage</td><td>VA-guaranteed loan for eligible veterans and service members</td><td>Conventional loan, for example one sold to Fannie Mae</td></tr>
<tr><td>Who approves the project</td><td>HUD, or a lender with DELRAP authority (<a href="{CFR_FHA}" rel="noopener">24 CFR 203.43b(c)</a>)</td><td>VA (<a href="{USC_VA}" rel="noopener">38 U.S.C. 3710(a)(6)</a>)</td><td>The lender reviews the project against the investor's standards (<a href="{FANNIE_PROJECT}" rel="noopener">Fannie Mae B4-2.1-01</a>)</td></tr>
<tr><td>Where to check</td><td><a href="{HUD_LOOKUP}" rel="noopener">HUD FHA Condominium Lookup</a> (copied weekly on this site)</td><td><a href="{VA_CONDO}" rel="noopener">VA condo report on the LGY Hub</a>, or ask your lender</td><td>Ask the lender</td></tr>
<tr><td>Approval term</td><td>3 years from listing, unless HUD specifies otherwise (<a href="{CFR_FHA}" rel="noopener">203.43b(h)(3)</a>)</td><td>Ask VA or your lender</td><td>Set by the investor's rules</td></tr>
<tr><td>One unit in an unapproved project</td><td>Possible with a single-unit approval, within limits (<a href="{CFR_FHA}" rel="noopener">203.43b(i)</a>)</td><td>Ask VA or your lender</td><td>Depends on the investor's rules</td></tr>
<tr><td>Rules</td><td><a href="{CFR_FHA}" rel="noopener">24 CFR 203.43b</a></td><td><a href="{USC_VA}" rel="noopener">38 U.S.C. 3710</a>; <a href="{CFR_VA}" rel="noopener">38 CFR 36.4360</a> and following</td><td><a href="{FANNIE_PROJECT}" rel="noopener">Fannie Mae Selling Guide, chapter B4-2</a></td></tr>
</tbody></table></div></div>
<div class="testo">
<h2>Three separate checks</h2>
<p>FHA, VA and conventional loans each have their own project rules, written in different places (see the table), and HUD's FHA list does not cover VA or conventional loans. A project can be on HUD's FHA list and not approved by VA, or the other way around. Check the list that matches the loan you plan to use.</p>
<h2>FHA approval</h2>
<p>For an FHA-insured mortgage, the unit must be in a project approved by HUD or by a DELRAP lender, or qualify as a site condominium or through a single-unit approval (<a href="{CFR_FHA}" rel="noopener">24 CFR 203.43b(c)</a>). Approved projects are placed on HUD's public list, which this site copies every week with the expiration date of each approval. See <a href="{{rel}}is-my-condo-fha-approved/">how to check a project</a>.</p>
<h2>VA approval</h2>
<p>The law allows a VA-guaranteed loan to buy a unit in a condominium project only if the project is approved by VA under criteria set in its regulations (<a href="{USC_VA}" rel="noopener">38 U.S.C. 3710(a)(6)</a>; VA's condominium rules start at <a href="{CFR_VA}" rel="noopener">38 CFR 36.4360</a>). VA.gov lists "buy a condo in a VA-approved project" among the uses of a VA-backed purchase loan (<a href="{VA_PURCHASE}" rel="noopener">VA.gov</a>). VA's condo report is on its <a href="{VA_CONDO}" rel="noopener">LGY Hub</a>; your lender can also check it.</p>
<h2>"Warrantable" condos</h2>
<p>"Warrantable" is not a term defined in HUD's condominium rule, in the VA law quoted above or in the Fannie Mae section cited here. Lenders use it informally for a project that meets the standards of the investor that will buy a conventional loan. For Fannie Mae, for example, the lender must determine that the project meets Fannie Mae's eligibility requirements before delivering the loan (<a href="{FANNIE_PROJECT}" rel="noopener">Selling Guide B4-2.1-01</a>). If a lender calls a condo "non-warrantable", ask which standard it does not meet and whether another loan type is possible.</p>
<p class="cite">Sources: 24 CFR 203.43b (<a href="{FR_2019}" rel="noopener">84 FR 41846</a>, August 15, 2019; current eCFR text); 38 U.S.C. 3710(a)(6); 38 CFR 36.4360; VA.gov; Fannie Mae Selling Guide B4-2.1-01 (August 5, 2026). Read on {data_lunga(CONTROLLO_FONTI)}.</p>
</div>
{fonte_box()}"""
    testata = banda("Guide", "FHA vs VA vs warrantable condos",
                    "Three loan types, three separate checks. Who approves a condo project, where to look it up, and the rules behind each.")
    descr = "FHA-approved, VA-approved and warrantable condos compared: who approves the project, where to check, approval terms and single-unit options, with official sources."
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": "FHA vs VA vs warrantable condos", "description": descr,
          "dateModified": ASOF.isoformat(), "author": {"@type": "Organization", "name": NOME, "url": URL_SITO + "/"},
          "publisher": {"@type": "Organization", "name": NOME, "url": URL_SITO + "/"}, "mainEntityOfPage": URL_SITO + "/fha-vs-va-vs-warrantable-condos/"}
    pagina("fha-vs-va-vs-warrantable-condos/", "FHA vs VA vs Warrantable Condos: What's the Difference?", descr, corpo,
           briciole=[("FHA vs VA vs warrantable condos", "fha-vs-va-vs-warrantable-condos/")], testata=testata, jsonld_extra=ld)


# ---------------------------------------------------------------- pagine fisse
def metodologia():
    S = stat_naz()
    cm = META["conteggi_modulo"]
    righe = "".join(f'<tr><td>{h(nome_stato(s))}</td><td class="n">{intero(cm["A"].get(s, 0))}</td><td class="n">{intero(cm["E"].get(s, 0))}</td>'
                    f'<td class="n">{intero(cm["W"].get(s, 0))}</td></tr>' for s in sorted(NOMI_STATI, key=nome_stato))
    n_unita = sum(1 for c in CONDOMINI if c["tipo"] == "A" and c["unita"] is not None)
    corpo = f"""<div class="testo">
<h2 style="margin-top:28px">Source</h2>
<p>Everything on this site comes from the U.S. Department of Housing and Urban Development's <a href="{HUD_LOOKUP}" rel="noopener">FHA Condominium Lookup</a>, the official search of condominium projects approved for FHA-insured mortgages. HUD's page states the date of its data ("as of"); the current edition is <strong>{data_lunga(ASOF)}</strong>.</p>
<h2>How we download it</h2>
<ul><li>Every week we run HUD's search for each of the {len(NOMI_STATI)} states and territories in its menu, with the search type "Project" (one row per condominium project; the separate rows for phases, which HUD calls submissions, are not repeated).</li>
<li>Three searches per state: status "Approved"; status "Expired" with an expiration date in the last {MESI_RECENTI} months; status "Withdrawn" with a status date in the last {MESI_RECENTI} months.</li>
<li>HUD shows 25 results per page. We read every page, one request at a time, a second or two apart, and check that the rows we read match the total HUD reports for each search. If they do not match, the update stops and the site is not changed.</li>
<li>Each week we also look up a random sample of 20 projects again, one by one, on HUD's lookup and compare every field we publish.</li></ul>
<h2>What we publish</h2>
<ul><li><strong>Project name, street, city, ZIP code and county</strong>, as HUD lists them (we convert HUD's capital letters to normal capitalization).</li>
<li><strong>HUD condo ID</strong>, to look the project up on HUD's site.</li>
<li><strong>Units</strong>: HUD has no separate field for the number of units, only a free-text description ("Composition of Project", for example "48 UNITS, 9 BUILDINGS"). We take the number only when the text gives one clear figure, a total ("168 total units") or a single number followed by "units"; numbers of buildings or phases and figures such as "12 units per building" are ignored. Today {intero(n_unita)} of {intero(S["A"])} approved projects have a unit count; the others show "–".</li>
<li><strong>FHA share</strong>: HUD's "FHA Concentration", the share of units with FHA-insured mortgages as listed by HUD.</li>
<li><strong>Approved until</strong>: HUD's expiration date. "Expiring soon" means within {MESI_SCADENZA} months of HUD's data date (by {data_lunga(LIMITE_SOON)}).</li>
<li><strong>Recently expired</strong>: projects with status "Expired" and an expiration date from {data_lunga(INIZIO_RECENTI)} to {data_lunga(ASOF)}; <strong>recently withdrawn</strong>: status "Withdrawn" with a status date in the same period. HUD's "Expired" search also returns a few projects whose approval ends on the data date itself and that still show "Approved" ({intero(sum(1 for c in CONDOMINI if c["tipo"] == "E" and c["stato"] == "Approved"))} today): we list them among the recent ones as "Approval ends".</li></ul>
<p>We do not publish HUD's free-text description or its comments: they sometimes contain internal notes, and we cannot check them one by one. They are on HUD's page for each project.</p>
<h2>Which places get a page</h2>
<ul><li><strong>States and territories</strong>: every one with at least one approved project, or one that expired or was withdrawn in the last {MESI_RECENTI} months. The state page lists all its approved projects; California, with more than {intero(LIMITE_LISTA_STATO)}, lists the ones that are not on a county or city page.</li>
<li><strong>Counties</strong>: at least {SOGLIA_CONTEA} approved projects. <strong>Cities</strong>: at least {SOGLIA_CITTA}. Smaller places are in the tables of the state or county page and in the search, so every project is listed somewhere. A county page is skipped when it would repeat the list of its state; when a city and its county have almost the same list (at least 90% of projects in common), there is a single page, the city's, which names the county.</li>
<li>Cities are grouped by name within a state ("ST PETERSBURG" and "SAINT PETERSBURG" are the same city). Counties are as written by HUD.</li></ul>
<h2>Counts reported by HUD for this edition</h2>
<p>Number of projects returned by HUD's search, by state; the rows we read are identical. Total: {intero(sum(cm["A"].values()))} approved, {intero(sum(cm["E"].values()))} expired and {intero(sum(cm["W"].values()))} withdrawn in the last {MESI_RECENTI} months{f" (we removed {META['doppi_tolti']} projects that appear both as approved and as expired or withdrawn, keeping the approved row)" if META.get("doppi_tolti") else ""}.</p>
<div class="tab scorre"><table class="pl"><thead><tr><th>State or territory</th><th class="n">Approved</th><th class="n">Expired (24 months)</th><th class="n">Withdrawn (24 months)</th></tr></thead><tbody>{righe}</tbody></table></div>
<h2>Limits</h2>
<ul><li>HUD updates its list every day; we update weekly. A project can be approved, renewed or withdrawn after our last download.</li>
<li>Some approvals cover only certain phases or buildings. The list shows the project, not each unit.</li>
<li>Names and addresses are HUD's, including its abbreviations and occasional typos.</li>
<li>This is not a loan approval. The lender checks the project and the loan.</li></ul>
<p>Spotted a mistake? <a href="{{rel}}contact/?ref=methodology">Tell us</a>.</p>
</div>
{fonte_box()}"""
    testata = banda("Methodology", "How we build the list", f"Where the data comes from, how we check it and what we leave out. HUD data as of {data_lunga(ASOF)}.", corta=True)
    pagina("methodology/", f"Methodology and Sources | {NOME}",
           "How we copy HUD's FHA Condominium Lookup every week, check it against HUD's totals, read unit counts and choose which places get a page.",
           corpo, briciole=[("Methodology", "methodology/")], testata=testata)


def about():
    corpo = f"""<div class="testo">
<p class="lead" style="margin-top:28px">{NOME} answers one question that decides many condo purchases: <em>can I buy this condo with an FHA loan?</em></p>
<p>HUD publishes the official answer in its FHA Condominium Lookup, a search form that shows 25 results at a time and only after you submit a search. We copy the whole list every week and publish it by state, county and city, with the expiration date of each approval, the approvals that expire soon and the ones that expired recently.</p>
<h2>Rules we follow</h2>
<ul><li>Every listing comes from HUD's data, with the HUD date on every page and a link to the official lookup.</li>
<li>We check our copy against HUD's totals every week and re-check a random sample of projects one by one.</li>
<li>We publish only information about condominium projects: names, addresses, counts and dates. No personal data.</li>
<li>No advice: this is information to check with HUD and your lender, not a loan approval.</li></ul>
<h2>Who we are</h2>
<p>{NOME} is an independent project run by Massimiliano Cori. It is not affiliated with HUD, FHA, VA, any lender or any real estate company. The site may show advertising and, in the future, clearly marked links to lenders; they never change the list.</p>
<h2>Corrections</h2>
<p>Found a mistake? <a href="{{rel}}contact/?ref=about">Write to us</a>; we check it against HUD's lookup and correct the page at the next update.</p></div>"""
    testata = banda("About", f"About {NOME}", "An independent site that makes HUD's list of FHA-approved condos easy to find and read.", corta=True)
    pagina("about/", f"About | {NOME}", f"About {NOME}: an independent site that publishes HUD's list of FHA-approved condo projects by state, county and city.",
           corpo, briciole=[("About", "about/")], testata=testata)


def contatti():
    corpo = f"""<section class="card pull"><form class="form ajax" name="contact" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="contact"><input type="hidden" name="source" value="">
<p class="hp"><label>Do not fill this in <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Your email<input type="email" name="email" required autocomplete="email"></label>
<label>Condo project or page (optional)<input type="text" name="place" maxlength="200"></label>
<label>Message<textarea name="message" rows="6" required maxlength="4000"></textarea></label>
<label class="check"><input type="checkbox" name="consent" value="yes" required><span>I have read the <a href="{{rel}}privacy.html">privacy notice</a>.</span></label>
<button class="btn" type="submit">Send</button><p class="errore" data-errore hidden>Sorry, it did not work. Please try again.</p></form>
<div class="ok" data-ok hidden><strong>Thank you.</strong> We will check and reply by email.</div></section>
<p class="small" style="margin-top:16px">We cannot tell you whether a specific loan will be approved, and we cannot change HUD's records: for the status of a project, use the <a href="{HUD_LOOKUP}" rel="noopener">HUD lookup</a> or ask your lender.</p>"""
    testata = banda("Contact", "Contact us", "Spotted a mistake or a project listed in the wrong place? Tell us and we will check it against HUD's data.")
    pagina("contact/", f"Contact | {NOME}", f"Contact {NOME}: report a mistake in a condo listing or a project shown in the wrong place, and we will check it against HUD's data.", corpo, briciole=[("Contact", "contact/")], testata=testata)


def privacy():
    # Cookie, link di affiliazione e pubblicità: con AdSense acceso (monetizzazione.json) o con link di affiliazione, il testo
    # comune di monetizzazione.py (GoatCounter senza cookie, pubblicità con il consenso di Google); altrimenti il testo di oggi.
    cookie = MON.privacy_cookie("en", SITO_ID, ci_sono_affiliati()) or """<h2>Cookies and visit counter</h2><p>This site sets no cookies. To count visits we use <a href="https://www.goatcounter.com/" rel="noopener">GoatCounter</a>, a privacy-friendly counter: it sets no cookies and stores nothing in your browser, builds no profiles and does not store your IP address, your full browser signature or any identifier. It keeps only aggregate numbers (page, hour or day, browser, country, screen width) on servers in the European Union and shares nothing with third parties; see <a href="https://www.goatcounter.com/help/privacy" rel="noopener">GoatCounter's privacy policy</a>. If we add advertising or affiliate links, we will update this notice and ask for your consent where required before any advertising cookies are used.</p>"""
    corpo = f"""<div class="testo"><p class="small" style="margin-top:28px">Last updated: {MESI[OGGI.month - 1]} {OGGI.year}</p>
<h2>Who is responsible</h2><p>The data controller is Massimiliano Cori (Italy), who runs {NOME} as an independent project. Contact: the <a href="{{rel}}contact/">contact form</a>.</p>
<h2>What we collect</h2><p>Only what you type in the contact form: your email, the project or page and your message, plus the page you came from. The search box and the table filters run in your browser: what you type is not sent to us. If you switch the light or dark theme, your choice is stored in your browser only.</p>
<h2>The data on this site</h2><p>The listings come from HUD's public FHA Condominium Lookup. We publish only information about condominium projects (name, address, county, unit count, FHA share and dates), not the names or contact details of people.</p>
<h2>Why</h2><p>To answer your messages and correct the site. The legal basis is your consent (Art. 6(1)(a) GDPR), which you can withdraw at any time.</p>
<h2>Who processes data for us</h2><p>The site and its form are hosted by Netlify, Inc., which stores form data on our behalf and may process it outside the EU with the safeguards required by the GDPR (standard contractual clauses). Netlify keeps technical server logs (such as IP addresses) for security. We do not sell or share your data.</p>
{cookie}
<h2>How long</h2><p>Messages are kept for up to 12 months after our last exchange.</p>
<h2>Your rights</h2><p>You can ask for access, correction, deletion, restriction, portability and objection (Articles 15–22 GDPR) and you can complain to the Italian data protection authority (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>) or the authority where you live. {MON.frase_california(SITO_ID) or 'California residents: we do not sell or share personal information.'}</p></div>"""
    # Sottotitolo e descrizione dicono "no cookies, no tracking": con AdSense acceso o con link di affiliazione si usa la frase
    # breve di monetizzazione.py, altrimenti resta il testo di oggi.
    breve = MON.privacy_breve("en", SITO_ID, ci_sono_affiliati())
    testata = banda("Privacy", "Privacy notice", breve or "What we collect (very little) and why. No cookies, no tracking.", corta=True)
    descr = (f"Privacy notice of {NOME}: {breve[0].lower()}{breve[1:]}" if breve else
             f"Privacy notice of {NOME}: no cookies and no tracking, a privacy-friendly visit counter; only what you send through the contact form.")
    pagina("privacy.html", f"Privacy | {NOME}", descr, corpo, testata=testata)


# ---------------------------------------------------------------- file accessori
def indice_ricerca():
    """data/search.json: p = pagine [url, etichetta, cercabile, approvati]; t = città [nome, Stato]; c = condomini
    [nome, città, ZIP, unità, pagina, data AAAAMMGG, stato 0/1/2, scade entro 6 mesi, ID]."""
    pagine, idx_p = [], {}

    def pid(u, etich, cercabile, n):
        if u not in idx_p:
            idx_p[u] = len(pagine)
            pagine.append([u, etich, 1 if cercabile else 0, n])
        return idx_p[u]
    for st in sorted(STATI_C, key=nome_stato):
        pid(url_stato(st), nome_stato(st), True, n_appr(st))
    for k, u in sorted(URL_CONTEA.items(), key=lambda kv: kv[1]):
        pid(u, f"{nome_contea(k[1])}, {k[0]}", True, len(approvati(CONTEE_C[k])))
    for k, u in sorted(URL_CITTA.items(), key=lambda kv: kv[1]):
        pid(u, f"{NOME_CITTA[k]}, {k[0]}", True, len(approvati(CITTA_C[k])))
    citta, idx_t = [], {}
    righe = []
    for c in sorted(CONDOMINI, key=lambda c: (c["tipo"] != "A", c["nome"].lower())):
        kt = (c["citta"], c["st"])
        if kt not in idx_t:
            idx_t[kt] = len(citta)
            citta.append([c["citta"] or "–", c["st"]])
        u = pagina_di(c)
        if c["tipo"] == "A":
            d, s = c["scadenza"], 0
        elif c["tipo"] == "E":
            d, s = c["scadenza"], (3 if c["stato"] == "Approved" else 1)
        else:
            d, s = c["data_stato"], 2
        righe.append([c["nome"], idx_t[kt], c["cap"], c["unita"], idx_p[u], int((d or "0").replace("-", "")), s,
                      1 if c["soon"] or c["passata"] else 0, c["id"]])
    (SITO / "data").mkdir(parents=True, exist_ok=True)
    (SITO / "data" / "search.json").write_text(json.dumps({"p": pagine, "t": citta, "c": righe}, separators=(",", ":"), ensure_ascii=False),
                                               encoding="utf-8")


def extra():
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n")
    (SITO / f"{CHIAVE_INDEXNOW}.txt").write_text(CHIAVE_INDEXNOW)  # file chiave IndexNow: non in sitemap, non linkato
    MON.scrivi_ads_txt(SITO_ID, SITO)  # sito/ads.txt solo con AdSense acceso (monetizzazione.json)
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{ASOF.isoformat()}</lastmod></url>" for u in URLS)
    (SITO / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n')
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Pubblica solo se è cambiato qualcosa in fhacondos/sito (ogni pubblicazione consuma crediti Netlify).
  # Impostazioni del sito su Netlify: Base directory = fhacondos/sito, Build command vuoto, Publish directory = "."
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."

[[headers]]
  for = "/*"
  [headers.values]
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    X-Frame-Options = "DENY"
    Permissions-Policy = "camera=(), microphone=(), geolocation=()"

[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=604800"

[[headers]]
  for = "/data/*"
  [headers.values]
    Cache-Control = "public, max-age=86400"
""")
    corpo = f"""<div class="pull">{blocco_cerca()}</div><p class="lead" style="margin-top:20px">Or go to the <a href="/">home page</a> or the <a href="/states/">list of states</a>.</p>"""
    pagina("404.html", f"Page not found | {NOME}", "Page not found.", corpo, indicizza=False, assoluto=True,
           testata=banda("Error 404", "Page not found", "The page may have moved after a data update: search for the condo, the city or the ZIP code."))


def copia_grafica():
    (SITO / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (RADICE / "grafica" / "fonts").iterdir():
        shutil.copy(f, SITO / "assets" / "fonts" / f.name)
    og = RADICE / "grafica" / "og.png"
    if og.exists():
        shutil.copy(og, SITO / "assets" / "og.png")


def controlli():
    err = []
    for c in CONDOMINI:
        if c["st"] not in NOMI_STATI:
            err.append(f"{c['id']}: Stato {c['st']} sconosciuto")
        if c["tipo"] == "A" and not c["scadenza"]:
            err.append(f"{c['id']}: approvato senza data di scadenza")
    tutti = list(URL_CONTEA.values()) + list(URL_CITTA.values()) + [url_stato(s) for s in STATI_C]
    doppi = [u for u, n in Counter(tutti).items() if n > 1]
    if doppi:
        err.append(f"URL duplicati: {doppi[:10]}")
    riservati = {"states/", "methodology/", "about/", "contact/", "data/", "assets/", "is-my-condo-fha-approved/", "condo-not-fha-approved/",
                 "fha-vs-va-vs-warrantable-condos/"}
    if riservati & set(url_stato(s) for s in STATI_C):
        err.append("uno Stato usa un indirizzo riservato")
    if err:
        raise SystemExit("ERRORI NEI DATI:\n" + "\n".join(err[:50]))


def main():
    controlli()
    conserva = {}
    if SITO.exists():
        conserva = {p.name: p.read_bytes() for p in SITO.glob("google*.html")}
        shutil.rmtree(SITO)
    SITO.mkdir()
    for nome, contenuto in conserva.items():
        (SITO / nome).write_bytes(contenuto)
    copia_grafica()
    scrivi_asset()
    home()
    pagina_stati()
    conti = {"stato": 0, "contea": 0, "citta": 0}
    for s in sorted(STATI_C):
        conti["stato"] += pagina_stato(s)
    for (st, k) in sorted(URL_CONTEA):
        conti["contea"] += pagina_luogo("contea", st, k)
    for (st, k) in sorted(URL_CITTA):
        conti["citta"] += pagina_luogo("citta", st, k)
    guida_controllo()
    guida_non_approvato()
    guida_confronto()
    metodologia()
    about()
    contatti()
    privacy()
    indice_ricerca()
    extra()
    n = Counter(c["tipo"] for c in CONDOMINI)
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili; Stati {conti['stato']}, contee {conti['contea']}, città {conti['citta']}. "
          f"Condomini: {n['A']} approvati, {n['E']} scaduti e {n['W']} ritirati negli ultimi {MESI_RECENTI} mesi. HUD as of {ASOF}.")


if __name__ == "__main__":
    main()
