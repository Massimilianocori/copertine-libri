"""Visto elettronico per l'India (sezione "india-e-visa-fee/", dal 31/10/2026): costo per nazionalità e tipo dalle due tabelle ufficiali in PDF,
visto all'arrivo (pagina "india-visa-on-arrival/") ed e-Arrival card (pagina "india-e-arrival-card/").

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/india_evisa.py             rilegge le fonti, estrae le tabelle dai PDF, controlla le frasi citate, scrive dati/india_evisa.json
    python3 -I beforeyoufly/raccolta/india_evisa.py --cache     come sopra ma senza rete, dalle copie in raccolta/.cache/india_evisa/
    python3 -I beforeyoufly/raccolta/india_evisa.py --domanda   rilegge anche l'autocompletamento di Google (dati/india_evisa_domanda.json)
    python3 -I beforeyoufly/raccolta/india_evisa.py --testo ID  stampa il testo normalizzato di una fonte (per scrivere le citazioni)
    python3 -I beforeyoufly/raccolta/india_evisa.py --tabella ID stampa le righe estratte da un PDF (fee_tv, fee_altri)

Regole (decise il 31/10/2026, idea n. 1 di studio-business/intelaiatura/wf-2026-10-31-india-nri.md):
  - Solo fonti ufficiali del governo indiano: il portale indianvisaonline.gov.in (e-Visa, visto all'arrivo, avvisi) e il sito del Bureau of
    Immigration (boi.gov.in, Ministry of Home Affairs). Niente rivenditori di visti, agenzie, blog, siti "di aiuto": il sito rimanda solo al
    portale ufficiale per pagare.
  - Costi: SOLO dalle due tabelle ufficiali in PDF ("Country/Territory Wise e-Tourist Visa Fee (in US $)" e "Country/Territory Wise e-Visa Fee
    (e-Business, e-Medical, e-Medical Attendant and e-Conference Visa)"), estratte in automatico con `pdftotext -layout`: numero d'ordine,
    nome del Paese come lo scrive la tabella, valori in dollari ("00" = 0 dollari come scritto; "-" = nessun valore). Controlli: numeri
    d'ordine 1..N senza buchi, N righe = ultimo numero, tutte le righe con lo stesso numero di valori, intestazioni delle colonne e nota sul
    3 % ancora presenti, data in fondo alla tabella, ogni Paese riconosciuto (dati/paesi_iso.json + NOMI_PDF), Paesi delle due tabelle uguali
    salvo le differenze note (DIFFERENZE_NOTE). verifica.py (punto 27) rilegge lo stesso PDF salvato con un secondo metodo (pdfplumber) e
    confronta numero di Paesi e valori.
  - Se il PDF cambia (impronta SHA-256 del file) i valori cambiati per Paese vanno in dati/india_evisa_cambi.json: rigenerare e pubblicare.
  - Le frasi mostrate tra virgolette sono citazioni parola per parola (dati/india_evisa_manuali.json), al massimo 40 parole ciascuna: il
    Bureau of Immigration scrive che ogni uso dei suoi testi oltre lo scaricamento richiede il suo permesso, quindi pubblichiamo i fatti
    (le cifre delle tabelle) con parole nostre e citazioni brevi con il link e la data.
  - La lettura vale solo con HTTP 200. NESSUN nuovo tentativo su HTTPError (403, 404, 5xx...) né su pagine anti-robot: non si aggirano i
    blocchi; si riprova solo per errori di rete o di tempo, al massimo 3 volte. Se una fonte non risponde 200, una citazione non c'è più o
    un controllo delle tabelle non torna, lo script NON sovrascrive dati/india_evisa.json ed esce con 1: si ricontrolla a mano.
  - Impronta (SHA-256, 16 caratteri) della "zona citata" delle pagine HTML (cambi in dati/india_evisa_cambi.json).
  - Pagine grezze e PDF in raccolta/.cache/india_evisa/ (escluse da git).
  - Ricontrollo: ogni settimana con la routine (le tabelle sono cambiate più volte nel 2025-26).
"""
import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
CACHE = Path(__file__).resolve().parent / ".cache" / "india_evisa"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
BOI = "Bureau of Immigration, Ministry of Home Affairs (Government of India)"
EVISA = "https://indianvisaonline.gov.in/evisa/"  # unico sito ufficiale per chiedere e pagare l'e-Visa (FAQ Q3 della pagina ufficiale)

# id -> url, ente, titolo, tipo (pdf = tabella dei costi, html = pagina)
FONTI = {
    "fee_tv": {"url": "https://indianvisaonline.gov.in/evisa/images/Etourist_fee_final.pdf", "tipo": "pdf", "ente": BOI,
               "titolo": "Country/Territory Wise e-Tourist Visa Fee (in US $)"},
    "fee_altri": {"url": "https://indianvisaonline.gov.in/evisa/images/eTV_revised_fee_final.pdf", "tipo": "pdf", "ente": BOI,
                  "titolo": "Country/Territory Wise e-Visa Fee (e-Business, e-Medical, e-Medical Attendant and e-Conference Visa)"},
    "evisa": {"url": "https://indianvisaonline.gov.in/evisa/tvoa.html", "tipo": "html", "ente": BOI, "titolo": "Indian Visa Online: e-Visa"},
    "ivo_home": {"url": "https://indianvisaonline.gov.in/", "tipo": "html", "ente": BOI, "titolo": "Indian Visa Online (home page)"},
    "voa": {"url": "https://indianvisaonline.gov.in/visa/visa-on-arrival.html", "tipo": "html", "ente": BOI, "titolo": "Indian Visa Online: Visa on Arrival"},
    "boi_voa": {"url": "https://boi.gov.in/boi/contents/travelling-to-india/foreigners/visa-free-regime-visa-on-arrival", "tipo": "html", "ente": BOI,
                "titolo": "Bureau of Immigration: Visa free Regime & Visa on Arrival"},
    "boi_gg": {"url": "https://boi.gov.in/boi/contents/travelling-to-india/general-guidelines", "tipo": "html", "ente": BOI,
               "titolo": "Bureau of Immigration: General Guidelines (travelling to India)"},
}
RX_ANTIROBOT = re.compile(r"Just a moment|_Incapsula_Resource|perfdrive\.com|Attention Required|cf-browser-verification|captcha|"
                          r"Access to this page has been denied", re.I)

# Tabelle: colonne (chiave, nome come lo scrive il PDF), frasi d'intestazione che devono esserci nel testo del PDF
TABELLE = {
    "fee_tv": {"colonne": [("tv30_apr_giu", "30 days e-TV (April to June)"), ("tv30_lug_mar", "30 days e-TV (July to March)"),
                           ("tv1", "01 year e-TV"), ("tv5", "05 years e-TV")],
               "intestazione": ["Country/Territory Wise e-Tourist Visa Fee", "(in US $)", "30 days e-", "TV(April to June)", "to March)",
                                "01 year e-TV", "05 years e-TV"]},
    "fee_altri": {"colonne": [("business", "e-Business Visa"), ("medico", "e-Medical Visa"), ("accompagnatore", "e-Medical Attendant Visa")],
                  "intestazione": ["Country/Territory Wise e-Visa Fee(e-", "Business, e-Medical, e-Medical Attendant and", "e-Conference Visa)",
                                   "e-Business Visa", "e-Medical Visa", "e-Medical Attendant Visa"]},
}
NOTA_3 = "Note: - Bank charge of 3% will be charged additional on applicable e-Visa fees."
# Paesi presenti in una sola delle due tabelle (letto il 31/10/2026): il Bangladesh è solo nella tabella degli altri e-Visa, con "-" per
# l'e-Business. Se cambia, lo script esce con 1 e si ricontrolla a mano.
DIFFERENZE_NOTE = {"solo_altri": ["Bangladesh"], "solo_tv": []}
# Nomi del PDF che dati/paesi_iso.json non riconosce da solo
NOMI_PDF = {"Cameroon Republic": "CM", "Cayman Island": "KY", "Cook Islands": "CK", "Niger Republic": "NE", "Niue Island": "NU",
            "Republic Of Korea": "KR", "Saint Christopher And Nevis": "KN", "Saint Vincent And The Grenadines": "VC", "Turks And Caicos": "TC",
            "United Kingdom (UK)": "GB", "United States Of America": "US", "Vatican City - Holy See": "VA", "Trinidad And Tobago": "TT",
            "Antigua & Barbuda": "AG", "Bosnia & Herzegovina": "BA", "Cote D'Ivoire": "CI", "Swaziland": "SZ", "Macedonia": "MK"}
MESI_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

# Ricerche dell'autocompletamento (client=firefox): (lingua, Paese di Google, ricerca). Inglese da USA, Regno Unito, Canada, Australia;
# tedesco da Germania, Austria e Svizzera; francese da Francia, Belgio e Svizzera. Per le ricerche "per nazionalità" anche le lettere a-z.
SEMI_EN = ["india e visa fee", "india e visa fee for", "india e visa fee for citizens", "india e visa cost", "india e visa cost for",
           "india visa cost", "india visa cost for", "india visa fee", "india visa fee for", "india tourist visa fee", "india tourist visa fee for",
           "india business visa fee", "india medical visa fee", "india 5 year visa cost", "indian visa cost", "indian visa fee",
           "indian e visa fee", "indian e visa cost", "india visa price", "how much is india e visa", "how much is an indian visa",
           "india visa on arrival", "visa on arrival india", "india visa on arrival for", "indian visa on arrival",
           "india e arrival card", "india arrival card", "indian e arrival card", "e arrival card india", "india e arrival card for"]
LETTERE_EN = ["india e visa fee for", "india visa cost for", "india visa fee for", "india e visa fee"]
SEMI_DE = ["indien visum kosten", "indien e visum kosten", "e visum indien kosten", "visum indien kosten", "indien visum preis",
           "indien visum gebühr", "indien e visum", "indien visum"]
SEMI_FR = ["visa inde prix", "e visa inde prix", "prix visa inde", "visa inde tarif", "visa inde cout", "visa inde coût", "e visa inde", "visa inde"]
PAESI_GOOGLE = {"en": ["us", "uk", "ca", "au"], "de": ["de", "at", "ch"], "fr": ["fr", "be", "ch"]}


def leggi(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-GB,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.status, r.geturl(), r.headers.get("Last-Modified"), r.read()


def testo_html(html_):
    """Testo visibile normalizzato (stesso metodo di raccolta/treni_bagagli.py)."""
    t = re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>|<!--.*?-->", " ", html_)
    t = re.sub(r"(?i)</?(?:strong|b|em|i|a|span|abbr|sup|u|font)\b[^>]*>", "", t)
    t = unescape(re.sub(r"<[^>]+>", " ", t))
    for x in ("​", "⁣", "﻿", "­"):
        t = t.replace(x, "")
    t = re.sub(r"\s+", " ", t.replace("\xa0", " "))
    return re.sub(r" ([,.;:!?])", r"\1", t).strip()


def testo_pdf_layout(f):
    """Testo del PDF con le colonne allineate (pdftotext -layout, poppler)."""
    return subprocess.run(["pdftotext", "-layout", str(f), "-"], capture_output=True, text=True, check=True).stdout


def testo_fonte(fid, f):
    if FONTI[fid]["tipo"] == "pdf":
        return re.sub(r"\s+", " ", testo_pdf_layout(f)).strip()
    return testo_html(f.read_bytes().decode("utf-8", "replace"))


def file_cache(fid):
    return CACHE / (f"{fid}.pdf" if FONTI[fid]["tipo"] == "pdf" else f"{fid}.html")


# ---------------------------------------------------------------- tabelle dei costi
RX_RIGA = re.compile(r"^\s*(\d{1,3})\s+([A-Za-z][A-Za-z .'&()\-]*?)\s+((?:\d+|-)(?:\s+(?:\d+|-))*)\s*$")
RX_SEGUITO = re.compile(r"^\s+([A-Za-z][A-Za-z .'&()\-]*?)\s*$")
RX_DATA = re.compile(r"^\s*(\d{2})-(" + "|".join(MESI_EN) + r")-(\d{4})\s*$")


def valore(s):
    return None if s == "-" else int(s)


def estrai_tabella(testo, fid):
    """Righe della tabella dal testo -layout: [(n, nome, [valori], [grezzi])], data in fondo (AAAA-MM-GG), problemi."""
    k = len(TABELLE[fid]["colonne"])
    righe, problemi, data_t = [], [], None
    ultima = None  # indice dell'ultima riga letta, per i nomi su due righe
    for linea in testo.splitlines():
        if not linea.strip():
            ultima = None
            continue
        m = RX_RIGA.match(linea)
        if m:
            grezzi = m.group(3).split()
            if len(grezzi) != k:
                problemi.append(f"{fid}: riga {m.group(1)} con {len(grezzi)} valori invece di {k}: {linea.strip()!r}")
                continue
            righe.append([int(m.group(1)), re.sub(r"\s+", " ", m.group(2)).strip(), [valore(x) for x in grezzi], grezzi])
            ultima = len(righe) - 1
            continue
        d = RX_DATA.match(linea)
        if d:
            data_t = f"{d.group(3)}-{MESI_EN.index(d.group(2)) + 1:02d}-{d.group(1)}"
            ultima = None
            continue
        s = RX_SEGUITO.match(linea)
        if s and ultima is not None and not s.group(1).startswith("Note"):
            righe[ultima][1] += " " + s.group(1).strip()  # seconda riga del nome ("United States Of" + "America")
            ultima = None
            continue
        ultima = None
    numeri = [r[0] for r in righe]
    if numeri != list(range(1, len(righe) + 1)):
        mancano = sorted(set(range(1, max(numeri or [0]) + 1)) - set(numeri))
        problemi.append(f"{fid}: numeri d'ordine non consecutivi (mancano {mancano[:10]}, righe lette {len(righe)})")
    if not data_t:
        problemi.append(f"{fid}: data in fondo alla tabella non trovata")
    return righe, data_t, problemi


def mappa_iso():
    P = json.loads((DATI / "paesi_iso.json").read_text(encoding="utf-8"))["paesi"]
    out = {}
    for p in P:
        for n in [p["nome"], *p.get("alias", [])]:
            out[n.lower().replace("&", "and")] = p
    return out, {p["iso2"]: p for p in P}


def iso_di(nome, M, PER):
    if nome in NOMI_PDF:
        return PER[NOMI_PDF[nome]]
    return M.get(nome.lower().replace("&", "and"))


def slug(s):
    s = s.lower().replace("&", "and")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


# ---------------------------------------------------------------- citazioni
def citazioni_tutte(M):
    return M["citazioni"]


def impronta_zona(testo, frasi):
    pos = [(testo.find(x), len(x)) for x in frasi]
    if not pos or any(i < 0 for i, _ in pos):
        return None
    a, b = min(i for i, _ in pos), max(i + n for i, n in pos)
    return hashlib.sha256(testo[a:b].encode("utf-8")).hexdigest()[:16]


TEMI = {"pagare", "ufficiale", "costo", "validita", "quando", "porti", "terra", "crociera", "voa_chi", "voa_dove", "voa_costo", "voa_durata",
        "voa_esclusi", "senza_visto", "arrivo_chi", "arrivo_dove", "arrivo_cosa", "arrivo_costo", "arrivo_altro", "rimborso", "tipi"}
MAX_PAROLE = 40


def frase_porti(P):
    """Frase della FAQ Q11 della pagina e-Visa ricomposta dagli elenchi di dati/india_evisa_manuali.json ("porti")."""
    a, s = P["aeroporti_faq"], P["porti_faq"]
    return (f"You may arrive at {len(a)} designated Airports i.e. {', '.join(a[:-1])} & {a[-1]}, and {len(s)} designated seaports "
            f"(i.e. {', '.join(s[:-1])} and {s[-1]}).")


def controlla_porti(M, testo_evisa):
    """Elenchi degli aeroporti e dei porti uguali alla pagina e-Visa: la frase della FAQ ricomposta c'è parola per parola; gli aeroporti in più
    del riquadro 'Authorized Immigration Checkposts' (37) sono in quel riquadro e non nella FAQ."""
    out, P = [], M["porti"]
    if frase_porti(P) not in testo_evisa:
        out.append("evisa: elenco degli aeroporti o dei porti della FAQ Q11 cambiato (rileggere e correggere 'porti')")
    i = testo_evisa.find("designated international airports (37) namely:")
    j = testo_evisa.find("Seaports", i)
    riquadro = testo_evisa[i:j] if i >= 0 and j > i else ""
    if not riquadro:
        out.append("evisa: riquadro 'Authorized Immigration Checkposts' con 37 aeroporti non trovato")
    for x in P["aeroporti_solo_lista"]:
        if f" {x} " not in riquadro + " " or x in P["aeroporti_faq"]:
            out.append(f"evisa: aeroporto {x} non nel riquadro dei 37 o già nella FAQ")
    return out


def controlla_struttura(M):
    out = []
    ids = [c["id"] for c in M["citazioni"]]
    doppi = sorted({i for i in ids if ids.count(i) > 1})
    if doppi:
        out.append(f"id di citazione doppi: {doppi}")
    for c in M["citazioni"]:
        if c["f"] not in FONTI:
            out.append(f"citazione {c['id']}: fonte sconosciuta {c['f']}")
        if c["tema"] not in TEMI:
            out.append(f"citazione {c['id']}: tema non previsto {c['tema']}")
        if len(c["x"].split()) > MAX_PAROLE:
            out.append(f"citazione {c['id']}: {len(c['x'].split())} parole, oltre {MAX_PAROLE}")
    for gruppo, ff in M.get("faq", {}).items():
        for q in ff:
            if any(i not in ids for i in q.get("cit", [])):
                out.append(f"FAQ {gruppo} «{q['q']}»: citazione sconosciuta")
    return out


# ---------------------------------------------------------------- domanda (autocompletamento)
def ricerche_domanda():
    out = []
    for lingua, semi in (("en", SEMI_EN), ("de", SEMI_DE), ("fr", SEMI_FR)):
        for q in semi:
            out.append((lingua, q))
    for q in LETTERE_EN:
        for ch in "abcdefghijklmnopqrstuvwxyz":
            out.append(("en", f"{q} {ch}"))
    return out


def tutte_ricerche(D):
    return {s for lingua in D["lingue"].values() for g in lingua.values() for ss in g.values() for s in ss}


def domanda():
    out = {}
    for lingua, q in ricerche_domanda():
        for gl in PAESI_GOOGLE[lingua]:
            u = "https://suggestqueries.google.com/complete/search?client=firefox&gl=%s&hl=%s&q=%s" % (gl, lingua, urllib.parse.quote(q))
            try:
                sugg = json.loads(leggi(u)[3].decode("utf-8", "replace"))[1]
            except Exception as e:  # una richiesta persa non ferma la raccolta (nessun nuovo tentativo)
                print(f"  autocompletamento {lingua}/{gl} {q!r}: {e}")
                continue
            out.setdefault(lingua, {}).setdefault(gl, {})[q] = sugg
            time.sleep(0.2)
    doc = {"_nota": "Ricerche vere (autocompletamento di Google, client=firefox) sul costo dell'e-Visa per l'India per nazionalità, sul visto "
                    "all'arrivo e sulla e-Arrival card: inglese (gl=us, uk, ca, au), tedesco (de, at, ch), francese (fr, be, ch). Le pagine "
                    "Paese e le pagine in tedesco e francese esistono solo se qui c'è una ricerca vera (vedi raccolta/india_evisa.py, "
                    "pagine_paese); ogni FAQ è legata a una di queste ricerche. Riscritto da raccolta/india_evisa.py --domanda.",
           "letto_il": date.today().isoformat(), "lingue": out}
    (DATI / "india_evisa_domanda.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("domanda:", len(tutte_ricerche(doc)), "suggerimenti diversi")


# ---------------------------------------------------------------- pagine per nazionalità (solo con ricerche vere)
# Parole con cui le persone scrivono la nazionalità nelle ricerche (curate a mano il 31/10/2026 dalle ricerche lette); "titolo" e "cittadini"
# sono i nomi usati nei titoli e nelle domande delle pagine. Una nazionalità ha una pagina solo se è in almeno una delle due tabelle e ha
# almeno MIN_RICERCHE ricerche vere sul costo del visto indiano (vedi ricerche_paese).
NAZIONALITA = {
    "GB": {"parole": ["uk", "british", "united kingdom", "britain"], "titolo": "UK", "cittadini": "UK citizens", "frase": "the UK"},
    "US": {"parole": ["us", "usa", "american", "americans", "united states"], "titolo": "US", "cittadini": "US citizens", "frase": "the US"},
    "CA": {"parole": ["canada", "canadian", "canadians"], "titolo": "Canadian", "cittadini": "Canadian citizens", "frase": "Canada"},
    "AU": {"parole": ["australia", "australian", "australians"], "titolo": "Australian", "cittadini": "Australian citizens", "frase": "Australia"},
    "NZ": {"parole": ["nz", "new zealand"], "titolo": "New Zealand", "cittadini": "New Zealand citizens", "frase": "New Zealand"},
    "IE": {"parole": ["irish", "ireland"], "titolo": "Irish", "cittadini": "Irish citizens", "frase": "Ireland"},
    "DE": {"parole": ["german", "germany"], "titolo": "German", "cittadini": "German citizens", "frase": "Germany"},
    "MY": {"parole": ["malaysian", "malaysia", "malaysians"], "titolo": "Malaysian", "cittadini": "Malaysian citizens", "frase": "Malaysia"},
    "SG": {"parole": ["singapore", "singaporean", "singaporeans"], "titolo": "Singapore", "cittadini": "Singapore citizens", "frase": "Singapore"},
    "ZA": {"parole": ["south africa", "south african", "south africans"], "titolo": "South African", "cittadini": "South African citizens",
           "frase": "South Africa"},
    "PH": {"parole": ["philippines", "filipino", "filipinos"], "titolo": "Filipino", "cittadini": "Filipino citizens", "frase": "the Philippines"},
    "LK": {"parole": ["sri lanka", "sri lankan", "sri lankans"], "titolo": "Sri Lankan", "cittadini": "Sri Lankan citizens", "frase": "Sri Lanka"},
    "BD": {"parole": ["bangladesh", "bangladeshi", "bangladeshis", "bd"], "titolo": "Bangladeshi", "cittadini": "Bangladeshi citizens",
           "frase": "Bangladesh"},
    "TH": {"parole": ["thai", "thailand"], "titolo": "Thai", "cittadini": "Thai citizens", "frase": "Thailand"},
    "RU": {"parole": ["russia", "russian", "russians"], "titolo": "Russian", "cittadini": "Russian citizens", "frase": "Russia"},
    "IT": {"parole": ["italian", "italy"], "titolo": "Italian", "cittadini": "Italian citizens", "frase": "Italy"},
    "NL": {"parole": ["netherlands", "dutch"], "titolo": "Dutch", "cittadini": "Dutch citizens", "frase": "the Netherlands"},
    "FR": {"parole": ["france", "french"], "titolo": "French", "cittadini": "French citizens", "frase": "France"},
    "JP": {"parole": ["japan", "japanese"], "titolo": "Japanese", "cittadini": "Japanese citizens", "frase": "Japan"},
    "ES": {"parole": ["spanish", "spain"], "titolo": "Spanish", "cittadini": "Spanish citizens", "frase": "Spain"},
    "GR": {"parole": ["greek", "greece"], "titolo": "Greek", "cittadini": "Greek citizens", "frase": "Greece"},
    "MM": {"parole": ["myanmar"], "titolo": "Myanmar", "cittadini": "Myanmar citizens", "frase": "Myanmar"},
    "GH": {"parole": ["ghana", "ghanaian", "ghanaians"], "titolo": "Ghanaian", "cittadini": "Ghanaian citizens", "frase": "Ghana"},
    "KE": {"parole": ["kenya", "kenyan", "kenyans"], "titolo": "Kenyan", "cittadini": "Kenyan citizens", "frase": "Kenya"},
    "UG": {"parole": ["uganda", "ugandan", "ugandans"], "titolo": "Ugandan", "cittadini": "Ugandan citizens", "frase": "Uganda"},
    "TZ": {"parole": ["tanzania", "tanzanian", "tanzanians"], "titolo": "Tanzanian", "cittadini": "Tanzanian citizens", "frase": "Tanzania"},
    "OM": {"parole": ["oman", "omani"], "titolo": "Omani", "cittadini": "Omani citizens", "frase": "Oman"},
    "AE": {"parole": ["uae", "emirati"], "titolo": "UAE", "cittadini": "UAE nationals", "frase": "the UAE"},
    "VN": {"parole": ["vietnam", "vietnamese"], "titolo": "Vietnamese", "cittadini": "Vietnamese citizens", "frase": "Vietnam"},
    "ID": {"parole": ["indonesia", "indonesian"], "titolo": "Indonesian", "cittadini": "Indonesian citizens", "frase": "Indonesia"},
    "KR": {"parole": ["south korea", "korean", "korea"], "titolo": "South Korean", "cittadini": "South Korean citizens", "frase": "South Korea"},
}
# Nazionalità cercate che NON sono in nessuna delle due tabelle (nessuna pagina: l'indice le elenca con la frase ufficiale sull'idoneità)
FUORI_TABELLA = {"China": ["china", "chinese"], "Pakistan": ["pakistan", "pakistani"], "Nigeria": ["nigeria", "nigerian", "nigerians"],
                 "Egypt": ["egypt", "egyptian"], "Turkey": ["turkey", "turkish"], "Afghanistan": ["afghanistan", "afghan"],
                 "Hong Kong": ["hong kong"]}
MIN_RICERCHE = 2
RX_COSTO = re.compile(r"\b(?:fee|fees|cost|costs|price|prices|how much|koto)\b")
# ricerche sul visto di un altro Paese per chi parte dall'India ("visa cost for japan from india", "japanese visa fee for indian")
RX_ALTRO_VERSO = re.compile(r"from india|india to |\bfor indians?\b|^(?:japanese|uk|hungary|student|tourist|work|visit) |visa cost for \w+ from|india visa fee koto")
# categorie delle domande (FAQ) nelle pagine per nazionalità: la prima che corrisponde
CATEGORIE = [("5anni", re.compile(r"\b5 years?\b|\bfive years?\b")), ("1anno", re.compile(r"\b1 year\b|\bone year\b")),
             ("30giorni", re.compile(r"\b30 days\b|\b1 month\b|\bone month\b")), ("business", re.compile(r"\bbusiness\b")),
             ("medico", re.compile(r"\bmedical\b")), ("generale", re.compile(r"."))]
RX_VOA = re.compile(r"visa on arrival")


def suggerimenti(D, lingua="en"):
    return sorted({s for g in D["lingue"].get(lingua, {}).values() for ss in g.values() for s in ss})


def parla_di(s, parole):
    return any(re.search(r"\b" + re.escape(w) + r"\b", s) for w in parole)


def ricerche_paese(D, parole):
    """Ricerche vere (inglese) sul costo del visto indiano che nominano la nazionalità: [(categoria, ricerca)]."""
    out = []
    for s in suggerimenti(D):
        if not re.search(r"\bindian?\b", s) or not RX_COSTO.search(s) or RX_ALTRO_VERSO.search(s) or not parla_di(s, parole):
            continue
        out.append((next(k for k, rx in CATEGORIE if rx.search(s)), s))
    return out


def ricerche_voa(D, parole):
    return [s for s in suggerimenti(D) if RX_VOA.search(s) and re.search(r"\bindian?\b", s) and parla_di(s, parole)
            and "indian passport" not in s and "indians" not in s]


def pagine_paese(D, iso_in_tabella):
    out = []
    for iso, N in NAZIONALITA.items():
        rr = ricerche_paese(D, N["parole"])
        if iso not in iso_in_tabella or len(rr) < MIN_RICERCHE:
            continue
        cat = {}
        for k, s in rr:
            cat.setdefault(k, s)
        out.append({"iso2": iso, "titolo": N["titolo"], "cittadini": N["cittadini"], "frase": N["frase"], "ricerche": [s for _, s in rr],
                    "faq": [{"categoria": k, "query": s} for k, s in sorted(cat.items(), key=lambda kv: [c for c, _ in CATEGORIE].index(kv[0]))],
                    "voa": (ricerche_voa(D, N["parole"]) or [None])[0]})
    return out


def fuori_tabella(D):
    out = []
    for nome, parole in FUORI_TABELLA.items():
        rr = ricerche_paese(D, parole)
        if rr:
            out.append({"nome": nome, "ricerche": [s for _, s in rr]})
    return out


# ---------------------------------------------------------------- lettura
def scarica(fid, da_cache, prima):
    """(raw, http, url finale, Last-Modified) dalla rete (una richiesta, nuovi tentativi solo per errori di rete) o dalla cache."""
    F, f_c = FONTI[fid], file_cache(fid)
    if da_cache:
        P0 = prima.get("fonti", {}).get(fid) or {}
        if not f_c.exists():
            return None, None, None, None, "nessuna copia in cache"
        return f_c.read_bytes(), P0.get("http", 200), P0.get("url_finale", F["url"]), P0.get("last_modified"), None
    errore = None
    for tentativo in range(3):
        try:
            stato, finale, lm, raw = leggi(F["url"])
            f_c.write_bytes(raw)
            return raw, stato, finale, lm, None
        except urllib.error.HTTPError as e:
            return None, e.code, F["url"], None, f"HTTP {e.code} (nessun nuovo tentativo)"
        except Exception as e:  # solo errori di rete/timeout: si riprova
            errore = e
            time.sleep(5 + 10 * tentativo)
    return None, None, None, None, f"lettura fallita ({errore})"


def data_http(lm):
    """'Fri, 30 Oct 2026 11:39:36 GMT' -> '2026-10-30' (data del file sul server)."""
    if not lm:
        return None
    m = re.match(r"\w{3}, (\d{2}) (\w{3}) (\d{4})", lm)
    mesi = [x[:3] for x in MESI_EN]
    return f"{m.group(3)}-{mesi.index(m.group(2)) + 1:02d}-{m.group(1)}" if m and m.group(2) in mesi else None


def main():
    oggi = date.today().isoformat()
    da_cache = "--cache" in sys.argv
    CACHE.mkdir(parents=True, exist_ok=True)
    M = json.loads((DATI / "india_evisa_manuali.json").read_text(encoding="utf-8"))
    D = json.loads((DATI / "india_evisa_domanda.json").read_text(encoding="utf-8"))
    f_dati = DATI / "india_evisa.json"
    prima = json.loads(f_dati.read_text(encoding="utf-8")) if f_dati.exists() else {"fonti": {}}
    problemi, letture, cambi, tabelle = controlla_struttura(M), {}, [], {}
    MI, PER = mappa_iso()
    for fid, F in FONTI.items():
        raw, stato, finale, lm, err = scarica(fid, da_cache, prima)
        if raw is None:
            problemi.append(f"{fid}: {err}")
            continue
        if stato != 200:
            problemi.append(f"{fid}: HTTP {stato}")
        f_c = file_cache(fid)
        P = prima.get("fonti", {}).get(fid) or {}
        letto = oggi if not da_cache else (P.get("letto_il") or oggi)
        voce = {"url": F["url"], "url_finale": finale, "http": stato, "byte": len(raw), "ente": F["ente"], "titolo": F["titolo"], "tipo": F["tipo"],
                "last_modified": lm, "file_del": data_http(lm), "letto_il": letto}
        if F["tipo"] == "pdf":
            if raw[:5] != b"%PDF-":
                problemi.append(f"{fid}: il file non è un PDF")
                continue
            sha = hashlib.sha256(raw).hexdigest()
            lay = testo_pdf_layout(f_c)
            piatto = re.sub(r"\s+", " ", lay)
            for h in TABELLE[fid]["intestazione"]:
                if h not in lay:
                    problemi.append(f"{fid}: intestazione cambiata, manca {h!r} (rileggere il PDF a mano)")
            if NOTA_3 not in piatto:
                problemi.append(f"{fid}: nota sul 3 % cambiata o sparita")
            righe, data_t, pp = estrai_tabella(lay, fid)
            problemi += pp
            out = []
            for n, nome, valori, grezzi in righe:
                p = iso_di(nome, MI, PER)
                if not p:
                    problemi.append(f"{fid}: Paese non riconosciuto {nome!r} (aggiungerlo a NOMI_PDF)")
                    continue
                out.append({"n": n, "nome_pdf": nome, "iso2": p["iso2"], "valori": dict(zip([k for k, _ in TABELLE[fid]["colonne"]], valori)),
                            "grezzi": grezzi})
            if len({r["iso2"] for r in out}) != len(out):
                problemi.append(f"{fid}: lo stesso Paese compare due volte")
            tabelle[fid] = {"titolo": F["titolo"], "colonne": TABELLE[fid]["colonne"], "data": data_t, "righe": out}
            imp = sha[:16]
            voce.update({"sha256": sha, "righe": len(out), "data_tabella": data_t, "impronta": imp})
            if P.get("sha256") and P["sha256"] != sha:
                vecchie = {r["iso2"]: r["valori"] for r in (prima.get("tabelle", {}).get(fid) or {}).get("righe", [])}
                diff = [{"iso2": r["iso2"], "prima": vecchie.get(r["iso2"]), "dopo": r["valori"]} for r in out if vecchie.get(r["iso2"]) != r["valori"]]
                diff += [{"iso2": k, "prima": v, "dopo": None} for k, v in vecchie.items() if k not in {r["iso2"] for r in out}]
                cambi.append({"data": oggi, "fonte": fid, "url": F["url"], "prima": P["sha256"][:16], "dopo": imp, "paesi": diff})
                print(f"  CAMBIATO il PDF {fid}: {len(diff)} Paesi con valori diversi (dati/india_evisa_cambi.json)")
            print(f"  {fid}: HTTP {stato}, {len(raw)} byte, Last-Modified {lm}, {len(out)} righe, tabella del {data_t}")
        else:
            t = testo_html(raw.decode("utf-8", "replace"))
            if RX_ANTIROBOT.search(t[:3000]):
                problemi.append(f"{fid}: pagina anti-robot (nessun nuovo tentativo)")
            imp = None
            print(f"  {fid}: HTTP {stato}, {len(raw)} byte, {len(t)} caratteri")
        # citazioni di questa fonte: parola per parola nel testo normalizzato
        t = testo_fonte(fid, f_c)
        if fid == "evisa":
            problemi += controlla_porti(M, t)
        frasi = [c["x"] for c in M["citazioni"] if c["f"] == fid]
        for x in frasi:
            if x not in t:
                problemi.append(f"{fid}: frase non trovata: {x[:90]!r}")
        if F["tipo"] == "html":
            imp = impronta_zona(t, frasi) if frasi else hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]
            voce["impronta"] = imp
            if P.get("impronta") and imp and P["impronta"] != imp:
                cambi.append({"data": oggi, "fonte": fid, "url": F["url"], "prima": P["impronta"], "dopo": imp})
                print(f"  CAMBIATA la zona citata di {fid}: rileggere la pagina")
        voce["cambiato_il"] = P.get("cambiato_il") if P.get("impronta") == voce.get("impronta") and P.get("cambiato_il") else letto
        voce["frasi"] = len(frasi)
        letture[fid] = voce
        if not da_cache:
            time.sleep(0.5)
    # le due tabelle: stessi Paesi salvo le differenze note
    if len(tabelle) == 2:
        a = {r["nome_pdf"] for r in tabelle["fee_tv"]["righe"]}
        b = {r["nome_pdf"] for r in tabelle["fee_altri"]["righe"]}
        if sorted(b - a) != sorted(DIFFERENZE_NOTE["solo_altri"]) or sorted(a - b) != sorted(DIFFERENZE_NOTE["solo_tv"]):
            problemi.append(f"Paesi diversi tra le due tabelle: solo e-Tourist {sorted(a - b)}, solo altri e-Visa {sorted(b - a)} (aggiornare DIFFERENZE_NOTE dopo il controllo a mano)")
    # FAQ delle pagine generali: ogni domanda legata a una ricerca vera (inglese, tedesco o francese)
    ricerche = tutte_ricerche(D)
    for gruppo, ff in M.get("faq", {}).items():
        for q in ff:
            if q["query"] not in ricerche:
                problemi.append(f"FAQ {gruppo} «{q['q']}» senza ricerca vera ({q['query']!r})")
    if problemi:
        print("NON SCRITTO dati/india_evisa.json. Da controllare a mano:\n  " + "\n  ".join(problemi))
        sys.exit(1)
    # Paesi: unione delle due tabelle, nell'ordine della tabella degli altri e-Visa (che li contiene tutti)
    tv = {r["iso2"]: r for r in tabelle["fee_tv"]["righe"]}
    paesi = []
    for r in tabelle["fee_altri"]["righe"]:
        p = PER[r["iso2"]]
        paesi.append({"iso2": r["iso2"], "nome": p["nome"], "nome_pdf": r["nome_pdf"], "slug": slug(p["nome"]), "alias": p.get("alias", []),
                      "tv": tv[r["iso2"]]["valori"] if r["iso2"] in tv else None, "altri": r["valori"]})
    pagine = pagine_paese(D, {p["iso2"] for p in paesi})
    doc = {"_nota": "e-Visa per l'India: tabelle ufficiali dei costi estratte dai PDF (pdftotext -layout) e fonti rilette da "
                    "raccolta/india_evisa.py (HTTP, Last-Modified, data di lettura, impronta); citazioni e FAQ da dati/india_evisa_manuali.json; "
                    "pagine per nazionalità solo con ricerche vere (dati/india_evisa_domanda.json). Non modificare a mano: rilanciare lo script.",
           "controllato_il": max(v["letto_il"] for v in letture.values()), "fonti": letture, "tabelle": tabelle, "paesi": paesi,
           "pagine": pagine, "fuori_tabella": fuori_tabella(D), "citazioni": M["citazioni"], "faq": M.get("faq", {}),
           "pagine_lingua": M.get("pagine_lingua", {}), "porti": M["porti"]}
    f_dati.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    if cambi:
        f_c = DATI / "india_evisa_cambi.json"
        storico = json.loads(f_c.read_text(encoding="utf-8")) if f_c.exists() else {"cambi": []}
        storico["cambi"] = cambi + storico["cambi"]
        f_c.write_text(json.dumps(storico, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Scritto {f_dati.relative_to(RADICE.parent)}: {len(paesi)} Paesi ({len(tv)} nella tabella e-Tourist, "
          f"{len(tabelle['fee_altri']['righe'])} nella tabella degli altri e-Visa), {len(pagine)} pagine per nazionalità, {len(letture)} fonti"
          + (f", {len(cambi)} cambi" if cambi else ""))


if __name__ == "__main__":
    if "--testo" in sys.argv:
        fid = sys.argv[sys.argv.index("--testo") + 1]
        f_c = file_cache(fid)
        if not f_c.exists():
            CACHE.mkdir(parents=True, exist_ok=True)
            f_c.write_bytes(leggi(FONTI[fid]["url"])[3])
        print(testo_fonte(fid, f_c))
        sys.exit(0)
    if "--tabella" in sys.argv:
        fid = sys.argv[sys.argv.index("--tabella") + 1]
        righe, data_t, pp = estrai_tabella(testo_pdf_layout(file_cache(fid)), fid)
        for r in righe:
            print(r[0], r[1], r[3])
        print("data:", data_t, "problemi:", pp)
        sys.exit(0)
    if "--domanda" in sys.argv:
        domanda()
        if "--solo-domanda" in sys.argv:
            sys.exit(0)
    main()
