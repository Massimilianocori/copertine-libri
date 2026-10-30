"""Scarica e legge l'elenco ufficiale dei test di inglese per i visti UK (SELT) e scrive visaincome/dati/selt.json.

Uso (dalla radice del repository):
    python3 visaincome/raccolta/selt.py              # pagina GOV.UK + 4 file ODS + pagine dei livelli; tiene la domanda già salvata
    python3 visaincome/raccolta/selt.py --domanda    # in più rifà le ricerche di autocompletamento (città e Paesi con domanda)

Fonti (vedi NOTE.md, sezione "UK visa English tests"), tutte su GOV.UK (Open Government Licence v3.0):
1. "Prove your English language abilities with a secure English language test (SELT)" (Home Office), letta dall'API dei
   contenuti di GOV.UK: data di aggiornamento, fornitori ammessi nel Regno Unito e fuori, nomi dei test da prenotare, link
   ai siti dei fornitori e i 4 allegati ODS:
   - List of approved test centres in the UK / outside the UK (colonne Provider, Name of TC, Country, Address, City, Availability);
   - List of approved secure English language tests taken in the UK / outside the UK (CEFR Level, Type, test, provider, voto, dal).
2. Livelli richiesti per tipo di visto: le guide GOV.UK dei visti (family, Skilled Worker, Health and Care Worker, Student,
   High Potential Individual, Scale-up) e "Prove your knowledge of English for citizenship and settling". Lo script controlla che
   le frasi su cui si basano le pagine ci siano ancora: se una manca, si ferma (la regola può essere cambiata: rileggere a mano).
3. Il cambio da B1 a B2 per la residenza (settlement) dal 26 marzo 2027: Statement of Changes HC 1691 (5 marzo 2026), nota
   esplicativa par. 5.60-5.62, e il testo delle regole (Appendix KOLL e Settlement Family Life). Stesso controllo delle frasi.

Domanda (--domanda): autocompletamento di Google (client=firefox, hl=en, gl=uk) per ogni città britannica con almeno un centro
e per ogni Paese dell'elenco estero, più le ricerche generali con gl=uk, in, pk, ng (salvate per le note). Un luogo "ha domanda"
(e quindi una pagina) se almeno SOGLIA_DOMANDA suggerimenti contengono il suo nome e un termine dei test (TERMINI_TEST), esclusi
quelli che parlano di usare il test per un altro Paese ("ielts ukvi for canada", "accepted in", "valid for").

Se un controllo fallisce, il JSON esistente NON viene toccato (esce con codice 1).
I file grezzi stanno in raccolta/_grezzi/selt/ (esclusi da git, si riscaricano a ogni esecuzione: sono piccoli).
"""
import hashlib
import html
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
GREZZI = Path(__file__).resolve().parent / "_grezzi" / "selt"
USCITA = RADICE / "dati" / "selt.json"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"}

PAGINA = "https://www.gov.uk/guidance/prove-your-english-language-abilities-with-a-secure-english-language-test-selt"
API = "https://www.gov.uk/api/content/guidance/prove-your-english-language-abilities-with-a-secure-english-language-test-selt"
ALLEGATI = {  # chiave -> parola che deve stare nel nome del file ODS linkato dalla pagina
    "centri_uk": "test_centres_in_the_UK",
    "centri_estero": "test_centres_outside_the_UK",
    "test_uk": "Tests_taken_in_the_UK",
    "test_estero": "Tests_taken_outside_the_UK",
}
INTESTAZIONE_CENTRI = ["Provider", "Name of TC", "Country", "Address", "City", "Availability"]
INTESTAZIONE_TEST = ["CEFR Level", "Type", "Approved English language test", "SELT provider", "Minimum grade required", "Effective from"]
# Nome del fornitore nei file dei centri -> nome ufficiale nella pagina GOV.UK
FORNITORI = {
    "IELTS SELT Consortium": "IELTS SELT Consortium",
    "LanguageCert": "LANGUAGECERT",
    "Pearson": "Pearson",
    "Trinity College London": "Trinity College London",
    "PSI": "PSI Services (UK) Ltd",
}
# Nomi dei test da prenotare (frasi della pagina GOV.UK, controllate a ogni esecuzione)
TEST_FORNITORE = {
    "IELTS SELT Consortium": "IELTS SELT Consortium: ‘ IELTS for UKVI ’ or ‘ IELTS Life Skills’",
    "LanguageCert": "LANGUAGECERT: ‘LANGUAGECERT International ESOL SELT ’ or ‘LANGUAGECERT Academic SELT ’ or ‘LANGUAGECERT General SELT ’",
    "Pearson": "Pearson: ‘ PTE Academic UKVI ’ or ‘ PTE Home’",
    "PSI": "PSI Services: ‘Skills for English UKVI ’",
    "Trinity College London": "Trinity College London: ‘Secure English Language Tests for UKVI ’ – Integrated Skills in English ( ISE ) or Graded Examinations in Spoken English ( GESE )",
}
# Frasi della pagina SELT usate nelle pagine del sito
FRASI_SELT = [
    "you will need to take a test that assesses your speaking and listening abilities: citizenship International Sportsperson parent partner Representative of an Overseas Business settlement (also known as indefinite leave to remain)",
    "you will need to take a test that assesses your reading, writing, speaking and listening abilities",
    "If you are in the UK You can only take a SELT with one of the following providers: Trinity College London IELTS SELT Consortium LANGUAGECERT Pearson",
    "If you are outside of the UK You can only take a SELT with one of the following providers: PSI Services (UK) Ltd IELTS SELT Consortium LANGUAGECERT Pearson",
    "You should be able to take a test within 28 days of booking, but it may not always be at the location nearest to you.",
    "Check the SELT provider’s website to find out when tests are available and to make sure the test centre is open.",
    "Do not contact the test centre directly.",
    "Test results are valid for 2 years from the date the test is awarded.",
    "their fees are the same as, or lower than, the price on the test provider’s website",
    "If there is not an approved test location in your country, you will have to travel to another country to take the test.",
]
# Livelli per tipo di visto: (chiave, URL dell'API, parte della guida, frase che deve esserci)
LIVELLI = [
    ("partner_primo", "https://www.gov.uk/api/content/uk-family-visa", "knowledge-of-english",
     "You must pass at least level A1 on the Common European Framework of Reference for Languages ( CEFR ) scale for your first visa application."),
    ("partner_proroga", "https://www.gov.uk/api/content/uk-family-visa", "knowledge-of-english",
     "level A1, you’ll need to pass at least level A2 in speaking and listening"),
    ("partner_b1_riuso", "https://www.gov.uk/api/content/uk-family-visa", "knowledge-of-english",
     "If you pass level B1 or higher, you can use your test result again when you apply for settlement after 5 years."),
    ("cittadinanza_residenza", "https://www.gov.uk/api/content/english-language", "overview",
     "You can prove it by having either: an English qualification at B1, B2, C1 or C2 level"),
    ("skilled_worker", "https://www.gov.uk/api/content/skilled-worker-visa", "knowledge-of-english",
     "You must prove you can read, write, speak and understand English to at least level B2 on the Common European Framework of Reference for Languages ( CEFR ) scale ."),
    ("skilled_worker_prima", "https://www.gov.uk/api/content/skilled-worker-visa", "knowledge-of-english",
     "If you had this visa before 8 January 2026 and you’re applying to extend or update it, you need level B1 English."),
    ("health_care", "https://www.gov.uk/api/content/health-care-worker-visa", "knowledge-of-english",
     "You must prove you can read, write, speak and understand English to at least level B2 on the Common European Framework of Reference for Languages ( CEFR ) scale ."),
    ("studente", "https://www.gov.uk/api/content/student-visa", "knowledge-of-english",
     "Degree level or above Equivalent to CEFR level B2 Below degree level CEFR level B1"),
    ("hpi", "https://www.gov.uk/api/content/high-potential-individual-visa", "knowledge-of-english",
     "You must prove you can read, write, speak and understand English to at least level B2 on the Common European Framework of Reference for Languages (CEFR) scale ."),
    ("scale_up", "https://www.gov.uk/api/content/scale-up-worker-visa", "knowledge-of-english",
     "You must prove you can read, write, speak and understand English to at least level B2 on the Common European Framework of Reference for Languages ( CEFR ) scale ."),
]
PAGINE_LIVELLI = {
    "https://www.gov.uk/api/content/uk-family-visa": "https://www.gov.uk/uk-family-visa/knowledge-of-english",
    "https://www.gov.uk/api/content/english-language": "https://www.gov.uk/english-language",
    "https://www.gov.uk/api/content/skilled-worker-visa": "https://www.gov.uk/skilled-worker-visa/knowledge-of-english",
    "https://www.gov.uk/api/content/health-care-worker-visa": "https://www.gov.uk/health-care-worker-visa/knowledge-of-english",
    "https://www.gov.uk/api/content/student-visa": "https://www.gov.uk/student-visa/knowledge-of-english",
    "https://www.gov.uk/api/content/high-potential-individual-visa": "https://www.gov.uk/high-potential-individual-visa/knowledge-of-english",
    "https://www.gov.uk/api/content/scale-up-worker-visa": "https://www.gov.uk/scale-up-worker-visa/knowledge-of-english",
}
# HC 1691: cambio B1 -> B2 per la residenza
HC = "https://www.gov.uk/government/publications/statement-of-changes-to-the-immigration-rules-hc-1619-5-march-2026"
HC_API = "https://www.gov.uk/api/content/government/publications/statement-of-changes-to-the-immigration-rules-hc-1619-5-march-2026"
HC_MEMO = HC + "/explanatory-memorandum-to-the-statement-of-changes-in-the-immigration-rules-hc-1691-5-march-2026-accessible"
HC_TESTO = HC + "/statement-of-changes-to-the-immigration-rules-hc-1691-5-march-2026-accessible-version"
FRASI_HC_MEMO = [
    "5.60 This change increases the English language requirement for settlement to B2 level under the Common European Framework of Reference for Languages (CEFR) for a number of immigration routes where the existing requirement is at B1 level.",
    "The changes apply to those routes covered by Appendix KoLL; Appendix Skilled Worker; Appendix Tier 2 Minister of Religion; Appendix Representative of an Overseas Business; Appendix UK Ancestry; Appendix Global Talent; Appendix Scale Up; Appendix Innovator Founder; Appendix International Sportsperson; Appendix Child Relative (Sponsors with Protection); Appendix Long Residence; Appendix Bereaved Partner; Appendix Private Life; and Appendix Settlement Family Life",
    "5.62 These changes will come into force on 26 March 2027.",
    "The changes will therefore apply to those already on a pathway to settlement in the UK",
]
FRASI_HC_TESTO = [
    "where the date of application is on or after 26 March 2027, that the applicant has passed an English language test in speaking and listening, at a minimum level B2",
    "Where the date of application is on or after 26 March 2027, the applicant must, unless an exemption applies, show English language ability on the Common European Framework of Reference for Languages in speaking and listening to at least level B2.",
]
# Nomi scritti in modi diversi nel file dei centri esteri -> nome unico (si registrano nel JSON)
PAESI_NORMALI = {"GHANA": "Ghana", "Sri lanka": "Sri Lanka", "morocco": "Morocco", "Guayaquil": "Ecuador",
                 "Cyprus": "Cyprus (South)"}  # "Cyprus": un solo centro, a Limassol (nel sud, come le altre righe di Limassol)
CITTA_NORMALI_UK = {"Newcastle": "Newcastle upon Tyne", "Newcastle Upon Tyne": "Newcastle upon Tyne"}
# Domanda (autocompletamento)
SOGLIA_DOMANDA = 1  # suggerimenti diversi, con un termine dei test (TERMINI_TEST) e il nome del luogo, non del tipo "ielts ukvi for canada"
TERMINI_TEST = ("selt", "ukvi", "life skills", "a1", "a2", "b1", "b2", "spouse", "citizenship", "ilr", "pte home", "languagecert",
                "skills for english", "trinity", "uk visa")
QUERY_GENERALI = ["selt test centre ", "ielts for ukvi ", "a1 english test for uk spouse visa ", "b1 english test for citizenship ",
                  "english test for ilr ", "b2 english test for ilr ", "selt b2 "]
GL_GENERALI = ["uk", "in", "pk", "ng"]
QUERY_CITTA = ["selt test centre {}", "ielts for ukvi {}", "b1 english test {}", "a1 english test {}", "english test for citizenship {}"]
QUERY_PAESI = ["selt test centre in {}", "a1 english test for uk spouse visa in {}", "ielts life skills {}", "ielts for ukvi {}"]
NOMI_RICERCA = {  # Paese dell'elenco -> nomi usati nelle ricerche (il primo nelle query)
    "USA": ["usa", "america", "united states"], "United Arab Emirates": ["uae", "dubai", "abu dhabi", "united arab emirates"],
    "South Korea": ["korea", "south korea"], "Bosnia & Herzegovina": ["bosnia"], "Democratic Republic of Congo": ["congo", "drc"],
    "Occupied Palestinian Territories": ["palestine", "gaza", "west bank"], "Trinidad and Tobago": ["trinidad"],
    "Cyprus (North)": ["north cyprus", "northern cyprus"], "Cyprus (South)": ["cyprus"], "Virgin Islands (US)": ["us virgin islands"],
    "Ivory Coast": ["ivory coast", "cote d'ivoire"], "Hong Kong": ["hong kong"],
}


def scarica(url, nome=None):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r:
        dati = r.read()
        meta = {"http": r.status, "last_modified": r.headers.get("Last-Modified", "")}
    if nome:
        GREZZI.mkdir(parents=True, exist_ok=True)
        (GREZZI / nome).write_bytes(dati)
    return dati, meta


def testo(html_body):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html_body))).strip()


def impronta(b):
    return hashlib.sha256(b).hexdigest()


def leggi_ods(dati):
    """Primo foglio di un ODS (solo libreria standard): righe di testo, senza celle vuote finali e senza righe vuote."""
    ns = {"table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0", "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0"}
    t = lambda k: "{%s}%s" % (ns[k.split(":")[0]], k.split(":")[1])  # noqa: E731
    radice = ET.fromstring(zipfile.ZipFile(io.BytesIO(dati)).read("content.xml"))
    tab = next(radice.iter(t("table:table")))
    righe = []
    for r in tab.iter(t("table:table-row")):
        riga = []
        for c in r:
            if c.tag not in (t("table:table-cell"), t("table:covered-table-cell")):
                continue
            rip = min(int(c.get(t("table:number-columns-repeated"), "1")), 30)
            riga += [re.sub(r"\s+", " ", " ".join("".join(p.itertext()) for p in c.iter(t("text:p")))).strip()] * rip
        while riga and not riga[-1]:
            riga.pop()
        if riga:
            righe.append(riga)
    return righe


def suggerimenti(q, gl="uk"):
    u = (f"https://suggestqueries.google.com/complete/search?client=firefox&gl={gl}&hl=en&q=" + urllib.parse.quote(q))
    try:
        d = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=20).read()
        return json.loads(d.decode("utf-8", "replace"))[1]
    except Exception:  # noqa: BLE001
        return None


def valido(sugg, nomi):
    """Suggerimento che conta come domanda per il luogo: contiene il nome e un termine dei test, e non chiede di usare il test altrove."""
    if not any(t in sugg for t in TERMINI_TEST):
        return False
    for k in nomi:
        k = re.escape(k)
        if re.search(r"\b" + k + r"\b", sugg) and not re.search(r"\b(for|accepted in|valid for|valid in)( \w+)? " + k + r"\b", sugg):
            return True
    return False


def domanda(luoghi, query, nomi):
    """{luogo: [suggerimenti diversi che contengono il nome]} per ogni luogo; None nella lista se una ricerca è fallita."""
    out, falliti = {}, 0
    for l in luoghi:
        trovati = []
        tutti = nomi.get(l, [l.lower()])
        for n in tutti[:2]:
            for q in query:
                s = suggerimenti(q.format(n))
                time.sleep(0.35)
                if s is None:
                    falliti += 1
                    continue
                trovati += [x for x in s if valido(x, tutti)]
        out[l] = sorted(set(trovati))
    return out, falliti


def main():
    errori = []
    oggi = date.today().isoformat()
    vecchio = json.loads(USCITA.read_text(encoding="utf-8")) if USCITA.exists() else {}
    # 1. pagina SELT
    b, meta = scarica(API)
    pag = json.loads(b)
    corpo = pag["details"]["body"]
    t = testo(corpo)
    for f in FRASI_SELT:
        if f not in t:
            errori.append(f"pagina SELT: frase non trovata (rileggere la pagina): {f[:90]}…")
    test_fornitore = {}
    for k, f in TEST_FORNITORE.items():
        if f not in t:
            errori.append(f"pagina SELT: nomi dei test di {k} cambiati: {f[:80]}…")
        test_fornitore[k] = [x.strip() for x in re.findall(r"‘([^’]+)’", f)]
    link_fornitori = {}
    for href, a in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', corpo, re.S):
        nome = testo(a)
        for k, v in FORNITORI.items():
            if nome == v and href.startswith("https://"):
                link_fornitori[k] = href.replace("LANGUAGECERT.org", "languagecert.org")
    if set(link_fornitori) != set(FORNITORI):
        errori.append(f"pagina SELT: link dei fornitori trovati solo per {sorted(link_fornitori)}")
    allegati = {}
    for href in sorted(set(re.findall(r'href="(https://assets\.publishing\.service\.gov\.uk/[^"]+\.ods)"', corpo))):
        for k, parola in ALLEGATI.items():
            if parola in href:
                allegati[k] = href
    if set(allegati) != set(ALLEGATI):
        errori.append(f"pagina SELT: allegati ODS trovati solo per {sorted(allegati)}")
        print("\n".join(errori))
        sys.exit(1)
    fonti = {"pagina": {"titolo": pag["title"], "editore": "Home Office (GOV.UK)", "url": PAGINA, "aggiornata": pag["public_updated_at"][:10],
                        "letta_il": oggi, "http": meta["http"], "licenza": "Open Government Licence v3.0",
                        "licenza_url": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"}}
    righe = {}
    for k, url in allegati.items():
        nome = urllib.parse.unquote(url.rsplit("/", 1)[1])
        dati, m = scarica(url, nome)
        r = leggi_ods(dati)
        righe[k] = r
        data_lista = re.search(r"(\d{2})\.(\d{2})\.(\d{4})\.ods$", nome)
        fonti[k] = {"url": url, "file": nome, "byte": len(dati), "sha256": impronta(dati), "scaricato_il": oggi, "http": m["http"],
                    "data_elenco": f"{data_lista.group(3)}-{data_lista.group(2)}-{data_lista.group(1)}" if data_lista else "",
                    "righe": len(r) - 1}
    # 2. centri
    norm = {"paesi": {}, "citta_uk": {}}
    centri = {"uk": [], "estero": []}
    for k, dove in (("centri_uk", "uk"), ("centri_estero", "estero")):
        r = righe[k]
        if r[0] != INTESTAZIONE_CENTRI:
            errori.append(f"{k}: intestazione cambiata: {r[0]}")
            continue
        for x in r[1:]:
            x = (x + [""] * 6)[:6]
            prov, nome, paese, ind, citta, disp = x
            if prov not in FORNITORI:
                errori.append(f"{k}: fornitore sconosciuto {prov!r}")
            if not (nome and paese and citta):
                errori.append(f"{k}: riga incompleta {x}")
            if dove == "uk":
                if paese != "United Kingdom":
                    errori.append(f"{k}: Paese {paese!r} nell'elenco del Regno Unito")
                if citta in CITTA_NORMALI_UK:
                    norm["citta_uk"][citta] = CITTA_NORMALI_UK[citta]
                    citta = CITTA_NORMALI_UK[citta]
                centri["uk"].append([prov, nome, citta, ind, disp])
            else:
                if paese in PAESI_NORMALI:
                    norm["paesi"][paese] = PAESI_NORMALI[paese]
                    paese = PAESI_NORMALI[paese]
                if citta.isupper() or citta.islower():
                    citta = citta.title()
                centri["estero"].append([prov, nome, paese, citta, ind, disp])
    if len(centri["uk"]) < 40 or len(centri["estero"]) < 600:
        errori.append(f"centri: troppo pochi ({len(centri['uk'])} nel Regno Unito, {len(centri['estero'])} all'estero)")
    for dove in ("uk", "estero"):
        prima = len(vecchio.get("centri", {}).get(dove, []))
        if prima and len(centri[dove]) < prima * 0.7:
            errori.append(f"centri {dove}: da {prima} a {len(centri[dove])} (calo oltre il 30%: controllare il file)")
    if any(x[0] == "PSI" for x in centri["uk"]) or any(x[0] == "Trinity College London" for x in centri["estero"]):
        errori.append("centri: PSI nel Regno Unito o Trinity all'estero (la pagina GOV.UK dice il contrario): rileggere")
    # 3. test approvati
    test = {}
    for k, dove in (("test_uk", "uk"), ("test_estero", "estero")):
        r = righe[k]
        if r[0] != INTESTAZIONE_TEST:
            errori.append(f"{k}: intestazione cambiata: {r[0]}")
            continue
        test[dove] = [(x + [""] * 6)[:6] for x in r[1:]]
        livelli = {x[0] for x in test[dove]}
        if not {"A1", "A2", "B1", "B2"} <= livelli:
            errori.append(f"{k}: mancano livelli ({sorted(livelli)})")
    # 4. livelli per visto
    livelli = {}
    cache = {}
    for chiave, api, parte, frase in LIVELLI:
        if api not in cache:
            bb, mm = scarica(api)
            cache[api] = (json.loads(bb), mm["http"])
        d, http = cache[api]
        corpo_p = next((p["body"] for p in d["details"].get("parts", []) if p["slug"] == parte), "")
        if frase not in testo(corpo_p):
            errori.append(f"livelli {chiave}: frase non trovata in {api} ({parte}): la regola può essere cambiata, rileggere")
        url_pag = PAGINE_LIVELLI[api] if parte != "overview" else PAGINE_LIVELLI[api]
        livelli[chiave] = {"url": url_pag, "titolo": d["title"].strip(), "frase": frase, "letta_il": oggi, "http": http,
                           "aggiornata": d.get("public_updated_at", "")[:10]}
    # 5. HC 1691
    bb, mm = scarica(HC_API)
    hc = json.loads(bb)
    memo = testo(json.loads(scarica(HC_MEMO.replace("https://www.gov.uk/", "https://www.gov.uk/api/content/"))[0])["details"]["body"])
    regole = testo(json.loads(scarica(HC_TESTO.replace("https://www.gov.uk/", "https://www.gov.uk/api/content/"))[0])["details"]["body"])
    for f in FRASI_HC_MEMO:
        if f not in memo:
            errori.append(f"HC 1691, nota esplicativa: frase non trovata: {f[:80]}…")
    for f in FRASI_HC_TESTO:
        if f not in regole:
            errori.append(f"HC 1691, testo: frase non trovata: {f[:80]}…")
    fonti["hc1691"] = {"titolo": hc["title"], "url": HC, "memorandum": HC_MEMO, "testo": HC_TESTO, "pubblicato": hc["first_published_at"][:10],
                       "letto_il": oggi, "http": mm["http"], "in_vigore": "2027-03-26", "frasi_memorandum": FRASI_HC_MEMO, "frasi_testo": FRASI_HC_TESTO}
    # 6. domanda
    citta_uk = sorted({x[2] for x in centri["uk"]})
    paesi = sorted({x[2] for x in centri["estero"]})
    dom = vecchio.get("domanda", {})
    if "--domanda" in sys.argv:
        nomi_c = {c: [c.lower()] + (["newcastle"] if c == "Newcastle upon Tyne" else []) for c in citta_uk}
        nomi_c["Newcastle upon Tyne"] = ["newcastle", "newcastle upon tyne"]
        sc, fc = domanda(citta_uk, QUERY_CITTA, nomi_c)
        sp, fp = domanda(paesi, QUERY_PAESI, NOMI_RICERCA)
        generali = {}
        for gl in GL_GENERALI:
            for q in QUERY_GENERALI:
                generali[f"{gl}|{q.strip()}"] = suggerimenti(q, gl) or []
                time.sleep(0.35)
        if fc + fp > 20:
            errori.append(f"domanda: {fc + fp} ricerche di autocompletamento fallite")
        dom = {"data": oggi, "metodo": "https://suggestqueries.google.com/complete/search?client=firefox&gl=uk&hl=en&q=…",
               "soglia": SOGLIA_DOMANDA, "query_citta": QUERY_CITTA, "query_paesi": QUERY_PAESI, "nomi_ricerca": NOMI_RICERCA,
               "citta": sc, "paesi": sp, "generali": generali}
    if not dom:
        errori.append("domanda: nessun dato di autocompletamento (lanciare con --domanda)")
    else:
        nuove = [c for c in citta_uk if c not in dom["citta"]] + [p for p in paesi if p not in dom["paesi"]]
        if nuove:
            print(f"Attenzione: luoghi nuovi senza dati di domanda (nessuna pagina finché non si lancia --domanda): {nuove}")
    if errori:
        print("ERRORI: il file dei dati NON è stato aggiornato")
        for x in errori[:60]:
            print(" -", x)
        sys.exit(1)
    contenuto = {"centri": centri, "test": test}
    uscita = {"_nota": "Generato da raccolta/selt.py: non modificare a mano. centri.uk: [fornitore, nome del centro, città, indirizzo, disponibilità]; "
                       "centri.estero: [fornitore, nome del centro, Paese, città, indirizzo, disponibilità]; test: [livello CEFR, tipo, test, fornitore, "
                       "voto minimo, in vigore dal]. Fonte: Home Office, GOV.UK (Open Government Licence v3.0).",
              "generato_il": oggi, "impronta": hashlib.sha256(json.dumps(contenuto, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20],
              "fonti": fonti, "fornitori": {k: {"nome_ufficiale": FORNITORI[k], "test": test_fornitore[k], "url": link_fornitori.get(k, "")} for k in FORNITORI},
              "livelli": livelli, "normalizzazioni": norm, "domanda": dom, **contenuto}
    USCITA.write_text(json.dumps(uscita, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    con = [c for c in citta_uk if len(dom.get("citta", {}).get(c, [])) >= SOGLIA_DOMANDA]
    conp = [p for p in paesi if len(dom.get("paesi", {}).get(p, [])) >= SOGLIA_DOMANDA]
    print(f"Scritto {USCITA}: {len(centri['uk'])} centri nel Regno Unito ({len(citta_uk)} città), {len(centri['estero'])} all'estero "
          f"({len(paesi)} Paesi); elenco del {fonti['centri_uk']['data_elenco']}, pagina aggiornata il {fonti['pagina']['aggiornata']}; "
          f"domanda del {dom.get('data')}: {len(con)} città e {len(conp)} Paesi; impronta {uscita['impronta']}.")


if __name__ == "__main__":
    main()
