"""Scarica e legge i file ufficiali della sezione "H-1B wage level and weighted lottery odds" (dal 7/11/2026) e scrive
visaincome/dati/h1b.json (fonti, frasi ufficiali, aree, occupazioni, impieghi) e visaincome/dati/h1b_salari.json (estratto
dei quattro livelli salariali OFLC per area e occupazione, per le pagine e il calcolatore).

Uso (dalla radice del repository):
    python3 visaincome/raccolta/h1b.py              # riscarica i file e scrive i due JSON (domanda: quella già salvata)
    python3 visaincome/raccolta/h1b.py --domanda    # rifà anche l'autocompletamento di Google (circa 1 minuto)

Fonti
- DOL, Office of Foreign Labor Certification (OFLC): OFLC_Wages_2026-27.zip (flag.dol.gov, salari OEWS di luglio 2026-giugno 2027,
  pubblico dominio). Dentro: ALC_Export.csv (Area, SocCode, GeoLvl, Level1-4, Average, Label; salari orari, o annuali con
  Label "Annual Wage"), Geography.csv (aree e contee), oes_soc_occs.csv (nomi), Appendix A (istruzione), note tecniche (PDF).
  Il CSV è di 29 MB: nel repository va solo l'estratto delle colonne usate (h1b_salari.json); lo zip resta in raccolta/_grezzi/h1b/.
- OFLC Wage Search (flag.dol.gov/wage-data/wage-search): le note della pagina stanno nel suo main.js (2080 ore, Geo Level 1-4).
- BLS, OEWS maggio 2025 (oesm25ma.zip per le aree, oesm25nat.zip nazionale): impieghi per area (per scegliere le aree delle
  pagine) e media e mediana nazionali. bls.gov risponde 403 a un User-Agent generico; con un User-Agent che dice chi scarica
  (nome del sito e pagina dei contatti) risponde 200.
- Federal Register (API JSON + PDF ufficiale su govinfo, pdftotext): regola finale DHS del 29/12/2025 sulla selezione pesata
  (90 FR 60864), proclamazione 11069 del 18/9/2026 (91 FR 60497), proposta DHS "Fee for Certain H-1B Petitions" (91 FR 54817),
  proposta DOL sui livelli salariali (91 FR 15454).
- LETTURE: ogni valore letto A MANO il 7/11/2026 con il FRAMMENTO del testo ufficiale. A ogni lancio si controlla che il frammento
  ci sia ancora: se manca, il JSON NON si aggiorna (codice 1) finché qualcuno non rilegge la fonte.
"""
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
USCITA = RADICE / "dati" / "h1b.json"
USCITA_SAL = RADICE / "dati" / "h1b_salari.json"
GREZZI = Path(__file__).resolve().parent / "_grezzi" / "h1b"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"}
UA_BLS = {"User-Agent": "VisaIncomeChecker data collection (+https://visa-income-checker.netlify.app/contact/)"}

URL_ZIP = "https://flag.dol.gov/sites/default/files/wages/OFLC_Wages_2026-27.zip"
URL_DOWNLOADS = "https://flag.dol.gov/wage-data/wage-data-downloads"
URL_RICERCA = "https://flag.dol.gov/wage-data/wage-search"
URL_BLS = {"bls_aree": "https://www.bls.gov/oes/special-requests/oesm25ma.zip", "bls_nazionale": "https://www.bls.gov/oes/special-requests/oesm25nat.zip"}
PAGINA_BLS = "https://www.bls.gov/oes/tables.htm"
FILE_ZIP = ("ALC_Export.csv", "Geography.csv", "oes_soc_occs.csv", "Wage Year 2026-27 Appendix A, Job Zone, and Education.xlsx",
            "FINAL-OEWS-Technical-Release-Notes-for-July-2026-Wage-Year.pdf")

DOCUMENTI_FR = {
    "regola": "2025-23853",        # DHS, regola finale "Weighted Selection Process..." (29/12/2025, in vigore dal 27/2/2026)
    "proclamazione": "2026-19554",  # proclamazione 11069 del 18/9/2026: proroga del pagamento di 100.000 $ fino al 21/9/2027
    "tassa": "2026-17324",         # DHS, proposta "Fee for Certain H-1B Petitions" (25/8/2026)
    "salari_dol": "2026-06017",    # DOL, proposta "Improving Wage Protections..." (27/3/2026): livelli più alti
}
ATTESI_FR = {
    "regola": {"type": "Rule", "citation": "90 FR 60864", "publication_date": "2025-12-29", "effective_on": "2026-02-27"},
    "proclamazione": {"type": "Presidential Document", "citation": "91 FR 60497", "publication_date": "2026-09-23"},
    "tassa": {"type": "Proposed Rule", "citation": "91 FR 54817", "publication_date": "2026-08-25", "comments_close_on": "2026-09-24"},
    "salari_dol": {"type": "Proposed Rule", "citation": "91 FR 15454", "publication_date": "2026-03-27", "comments_close_on": "2026-05-26"},
}
# Se compare una regola finale con uno di questi titoli, lo script si ferma: le pagine dicono "proposta".
TITOLI_DA_SEGUIRE = ("Fee for Certain H-1B Petitions", "Improving Wage Protections for the Temporary and Permanent Employment",
                     "Weighted Selection Process for Registrants")

# ---------------------------------------------------------------- letture a mano (7/11/2026)
# fonte: "pdf:<chiave FR>" (testo del PDF), "fr:<chiave FR>" (sommario dell'API), "note" (note tecniche OFLC nello zip),
#        "ricerca" (main.js della pagina OFLC Wage Search), "downloads" (pagina OFLC Wage Data Downloads).
LETTURE = {
    "pesi": {"valore": {"I": 1, "II": 2, "III": 3, "IV": 4}, "fonte": "pdf:regola",
             "frammento": "a beneficiary assigned wage level IV will be entered into the selection pool four times, a beneficiary assigned wage level III will be "
                          "entered into the selection pool three times, a beneficiary assigned wage level II will be entered into the selection pool two times, "
                          "and a beneficiary assigned wage level I will be entered into the selection pool one time"},
    "livello_scelto": {"valore": True, "fonte": "pdf:regola",
                       "frammento": "the highest Occupational Employment and Wage Statistics (OEWS) wage level that the beneficiary’s proffered wage equals or exceeds "
                                    "for the relevant Standard Occupational Classification (SOC) code in the area(s) of intended employment"},
    "sotto_livello_1": {"valore": "I", "fonte": "pdf:regola",
                        "frammento": "If the beneficiary’s proffered wage is lower than OEWS wage level I, because it is based on a prevailing wage from another legitimate "
                                     "source (other than OEWS) or an independent authoritative source, the registrant must select ‘‘wage level I.’’"},
    "piu_sedi": {"valore": "lowest", "fonte": "pdf:regola",
                 "frammento": "If the beneficiary will work in multiple locations, or in multiple positions if the registrant is an agent, the registrant must select "
                              "the lowest corresponding OEWS wage level that the beneficiary’s proffered wage will equal or exceed."},
    "intervallo": {"valore": "lowest", "fonte": "pdf:regola",
                   "frammento": "If the beneficiary’s proffered wage is expressed as a range, the registrant must select the OEWS wage level that the lowest wage "
                                "in the range will equal or exceed."},
    "senza_oews": {"valore": True, "fonte": "pdf:regola",
                   "frammento": "Where there is no current OEWS prevailing wage information for the beneficiary’s proffered position, the registrant must select "
                                "the OEWS wage level that corresponds to the requirements of the beneficiary’s proffered position using the Department of Labor’s "
                                "prevailing wage guidance."},
    "piu_registrazioni": {"valore": "lowest", "fonte": "pdf:regola",
                          "frammento": "USCIS will assign each unique beneficiary to the lowest OEWS wage level among all registrations submitted on the beneficiary’s behalf"},
    "una_volta": {"valore": True, "fonte": "pdf:regola",
                  "frammento": "Each unique beneficiary will only be counted once toward the numerical allocation projections, regardless of how many registrations "
                               "were submitted for that beneficiary or how many times the beneficiary is entered in the selection pool"},
    "periodo_14": {"valore": 14, "fonte": "pdf:regola", "frammento": "The annual initial registration period will last a minimum of 14 calendar days"},
    "annuncio_30": {"valore": 30, "fonte": "pdf:regola",
                    "frammento": "USCIS will announce the start of the initial registration period at least 30 calendar days in advance of such date."},
    "stima_dhs": {"valore": {"I": 15.29, "II": 30.58, "III": 45.87, "IV": 61.16}, "fonte": "pdf:regola",
                  "frammento": "estimates that the probability of being selected to file a H–1B cap-subject petition for a unique beneficiary will be 15.29 percent "
                               "for level I, 30.58 percent for level II, 45.87 percent for level III, and 61.16 percent for level IV"},
    "stima_casuale": {"valore": 29.59, "fonte": "pdf:regola",
                      "frammento": "the probability of being selected to file an H–1B cap-subject petition for a unique beneficiary is 29.59 percent across all the wage levels"},
    "ipotesi_dhs": {"valore": {"quote": {"I": 28, "II": 55, "III": 12, "IV": 5}, "beneficiari": 320711, "selezioni": 94900}, "fonte": "pdf:regola",
                    "frammento": "(level I, 28%; level II, 55%; level III, 12%; and level IV, 5%) of the 5-year average of the number of beneficiaries with eligible registrations, 320,711"},
    "formula_dhs": {"valore": True, "fonte": "pdf:regola",
                    "frammento": "Level II, 30.58% = (probability of being selected for level I, 15.29%) x 2. Level III, 45.87% = 15.29% x 3. Level IV, 61.16% = 15.29% x 4."},
    "selezioni_dhs": {"valore": 94900, "fonte": "pdf:regola", "frammento": "The probability of being selected under random selection is 29.59% = (94,900 + 320,711) x 100%"},
    "conteggi_dhs": {"valore": {"I": 89911, "II": 177216, "III": 37928, "IV": 15657}, "fonte": "pdf:regola",
                     "frammento": "(89,911 x 1 + 177,216 x 2 + 37,928 x 3 + 15,657 x 4)"},
    "obbligo_salario": {"valore": True, "fonte": "pdf:regola",
                        "frammento": "employers remain legally obligated to pay H–1B workers at least the prevailing wage or the actual wage, whichever is higher."},
    "senza_reimmissione": {"valore": True, "fonte": "pdf:regola",
                           "frammento": "Since unique beneficiaries can be selected only once, the selection process is conducted without replacement."},
    "due_fasi": {"valore": True, "fonte": "pdf:regola",
                 "frammento": "The final rule will maintain this two-stage selection process to keep a higher chance of beneficiaries with a qualifying U.S. master’s degree or higher of being selected."},
    "fasi": {"valore": True, "fonte": "pdf:regola",
             "frammento": "USCIS first selects from a pool of all unique beneficiaries, including those eligible for the advanced degree exemption. USCIS then selects "
                          "from the remaining unique beneficiaries a sufficient number projected as needed to reach the advanced degree exemption."},
    "peso_master": {"valore": True, "fonte": "pdf:regola",
                    "frammento": "USCIS will weight each unique beneficiary as described in paragraph (h)(8)(iii)(A)(4)(ii) of this section and randomly select the number of "
                                 "unique beneficiaries deemed necessary to meet the H–1B advanced degree exemption numerical limitation"},
    "esenti": {"valore": True, "fonte": "pdf:regola",
               "frammento": "H–1B petitions for aliens who are employed by, or have received offers of employment at, U.S. institutions of higher education, nonprofit "
                            "entities related to or affiliated with U.S. institutions of higher education, or nonprofit research organizations or governmental research "
                            "organizations are exempt from the H–1B cap."},
    "bonus": {"valore": True, "fonte": "pdf:regola",
              "frammento": "While cash bonuses may, in limited circumstances, be counted towards the annual salary"},
    "salari_invariati": {"valore": True, "fonte": "pdf:regola", "frammento": "This rule does not change how wages are defined or measured."},
    "gruppo_15": {"valore": {"petizioni": 470023, "gruppo_15": 326000, "quota": 69}, "fonte": "pdf:regola",
                  "frammento": "Of the 470,023 H–1B cap-subject petitions received in FY 2020–FY 2024, 69 percent (326,000) were associated with SOC major group 15 "
                               "(Computer and Mathematical Occupations)."},
    "gruppo_17": {"valore": 52402, "fonte": "pdf:regola",
                  "frammento": "After SOC major group code 15, the major group with the next greatest number of petitioners is SOC major group code 17 "
                               "(Architecture and Engineering Occupations). This major group had 52,402 petitions filed in FY 2020 through FY 2024."},
    "in_tempo_2027": {"valore": True, "fonte": "fr:regola", "frammento": "This rule will be effective in time for the FY 2027 registration season."},
    # proclamazione 11069 (18/9/2026)
    "selezioni_2027": {"valore": {"alti": 46.3, "basso": 17.8}, "fonte": "pdf:proclamazione",
                       "frammento": "Job offers with wages corresponding to the two highest wage levels accounted for approximately 46.3 percent of H–1B registration "
                                    "selections while those corresponding with the lowest wage level accounted for only 17.8 percent."},
    "master_2027": {"valore": {"2026": 45.1, "2027": 66.1}, "fonte": "pdf:proclamazione",
                    "frammento": "registrations for beneficiaries with at least a U.S. Master’s degree rising from 45.1 percent of total registrants for FY 2026 to 66.1 percent for FY 2027"},
    "pagamento": {"valore": 100000, "fonte": "pdf:proclamazione",
                  "frammento": "is restricted, except for those aliens whose petitions are accompanied or supplemented by a payment of $100,000"},
    "pagamento_fino": {"valore": "2027-09-21", "fonte": "pdf:proclamazione",
                       "frammento": "to extend the 2025 Proclamation for an additional 12 months, until 12:00 a.m. eastern daylight time on September 21, 2027."},
    "proclamazione_2025": {"valore": "2025-09-19", "fonte": "pdf:proclamazione",
                           "frammento": "On September 19, 2025, Proclamation 10973 (Restriction on Entry of Certain Nonimmigrant Workers) (2025 Proclamation), was issued"},
    "eccezioni": {"valore": True, "fonte": "pdf:proclamazione",
                  "frammento": "shall not apply to any individual alien, all aliens working for a company, or all aliens working in an industry, if the Secretary of Homeland "
                               "Security determines, in the Secretary’s discretion, that the hiring of such aliens to be employed as H–1B specialty occupation workers is in the national interest"},
    "pagamento_fuori": {"valore": True, "fonte": "pdf:proclamazione",
                        "frammento": "The Secretary of Homeland Security shall restrict decisions on petitions not accompanied by a $100,000 payment for H–1B specialty "
                                     "occupation workers under section 101(a)(15)(H)(i)(b) of the INA, who are currently outside the United States"},
    # proposte
    "tassa_proposta": {"valore": 103265, "fonte": "fr:tassa",
                       "frammento": "proposes to establish a $103,265 fee, payable at the time of filing, for all H-1B cap-subject petitions, including those eligible "
                                    "for the advanced degree exemption"},
    "livelli_proposti": {"valore": {"I": [17, 34], "II": [34, 52], "III": [50, 70], "IV": [67, 88]}, "fonte": "pdf:salari_dol",
                         "frammento": "The Department proposes to increase the prevailing wage floors for Wage Level I from the 17th percentile to the 34th percentile, "
                                      "for Wage Level II from the 34th to the 52nd, for Wage Level III from the 50th to the 70th, and for Wage Level IV from the 67th to the 88th"},
    # OFLC
    "ore_anno": {"valore": 2080, "fonte": "ricerca",
                 "frammento": "Yearly wages are calculated based on 2080.0 work hours per year and rounded to the nearest dollar."},
    "geo_1": {"valore": 1, "fonte": "ricerca",
              "frammento": "If the data used to calculate the wage estimate came from the actual MSA or BOS area the Geo Level code will equal \"1\"."},
    "geo_2": {"valore": 2, "fonte": "ricerca",
              "frammento": "If there were no releasable estimates for the desired area then the wages area for the area indicated plus its contiguous areas. "
                           "This is signified by a Geo Level \"2\"."},
    "geo_3": {"valore": 3, "fonte": "ricerca",
              "frammento": "If there was no releasable estimates for the area, or for the area plus contiguous areas the wage is calculated from statewide data, "
                           "indicated by a Geo Level equaling \"3\"."},
    "geo_4": {"valore": 4, "fonte": "ricerca",
              "frammento": "Finally, if there is no releasable estimate for the state, the national average is used. This is indicated by Geo Level \"4\"."},
    "anno_salari": {"valore": {"dal": "2026-07-01", "al": "2027-06-30"}, "fonte": "note",
                    "frammento": "(OEWS) wages for July 1, 2026 through June 30, 2027 (Wage Year 2026-27)"},
    "base_maggio_2025": {"valore": "May 2025", "fonte": "note", "frammento": "This data is based on BLS’s May 2025 wage estimates."},
    "alto": {"valore": {"ora": 115, "anno": 239200}, "fonte": "note",
             "frammento": "Therefore, OFLC will issue the prevailing wage as $115.00 per hour or $239,200.00 per year as indicated in the OEWS data."},
    "aggiornato": {"valore": "2026-07-01", "fonte": "downloads", "frammento": "7/2026 - 6/2027 July 1, 2026"},
}

QUERY = {"us": ["h1b wage level", "h1b wage level calculator", "h1b lottery odds", "h1b lottery chances", "h1b weighted lottery", "h1b lottery 2027",
                "h1b level 1 salary", "h1b level 2 salary", "h1b level 3 salary", "h1b level 4 salary", "h1b level 2 salary new york",
                "h1b level 2 salary seattle", "h1b level 2 salary california", "h1b wage level software engineer", "h1b wage level software developer",
                "h1b wage level data scientist", "h1b lottery odds by wage level", "h1b wage levels by state"],
         "in": ["h1b wage level", "h1b lottery odds", "h1b lottery chances"]}


def get(u, intestazioni=UA, tentativi=3):
    for i in range(tentativi):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=intestazioni), timeout=180)
            return r.status, r.read(), dict(r.headers)
        except Exception as e:  # noqa: BLE001
            c = getattr(e, "code", 0)
            if c in (403, 404, 410):
                return c, b"", {}
            time.sleep(2 + 2 * i)
    return 0, b"", {}


def norm(t):
    return re.sub(r"\s+", " ", t or "").strip()


def sha(b):
    return hashlib.sha256(b).hexdigest()


# pdftotext perde il trattino di alcune parole spezzate a fine riga: si rimettono quelle citate in pagina
TRATTINI = {"twostage": "two-stage"}


def pdf_testo(b):
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "doc.pdf"
        f.write_bytes(b)
        t = norm(subprocess.run(["pdftotext", str(f), "-"], capture_output=True, text=True, timeout=180).stdout)
    for x, y in TRATTINI.items():
        t = t.replace(x, y)
    return t


def testo_html(b):
    t = b.decode("utf-8", "replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)
    return norm(re.sub(r"<[^>]+>", " ", t))


def leggi_fr(num):
    st, b, _ = get(f"https://www.federalregister.gov/api/v1/documents/{num}.json")
    if st != 200:
        return None, ""
    d = json.loads(b)
    st2, pdf, _ = get(d["pdf_url"])
    testo = pdf_testo(pdf) if st2 == 200 and pdf[:4] == b"%PDF" else ""
    meta = {k: d.get(k) for k in ("title", "type", "citation", "publication_date", "effective_on", "comments_close_on", "html_url", "pdf_url", "abstract", "document_number")}
    meta["sha256_pdf"] = sha(pdf) if testo else None
    return meta, testo


def regole_finali_nuove():
    """Documenti di tipo Rule pubblicati dopo la regola sulla selezione pesata con uno dei titoli da seguire."""
    q = urllib.parse.urlencode({"conditions[term]": "H-1B", "conditions[type][]": "RULE", "conditions[publication_date][gte]": "2026-01-01",
                                "order": "newest", "per_page": 50, "fields[]": ["title", "publication_date", "document_number"]}, doseq=True)
    st, b, _ = get("https://www.federalregister.gov/api/v1/documents.json?" + q)
    if st != 200:
        return None
    return [r for r in json.loads(b).get("results", []) if any(t.lower() in r["title"].lower() for t in TITOLI_DA_SEGUIRE)]


def xlsx_righe(b, foglio=0):
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(b), read_only=True)
    it = wb.worksheets[foglio].iter_rows(values_only=True)
    h = next(it)
    return h, it


def autocompleta(q, gl):
    u = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode({"client": "firefox", "gl": gl, "hl": "en", "q": q})
    for _ in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20)
            return json.loads(r.read().decode("utf-8", "replace"))[1]
        except Exception:  # noqa: BLE001
            time.sleep(2)
    return None


def nuova_domanda():
    out = {}
    for gl, qs in QUERY.items():
        for q in qs:
            out[f"{gl}|{q}"] = autocompleta(q, gl)
            time.sleep(0.3)
    return {"data": date.today().isoformat(), "metodo": "https://suggestqueries.google.com/complete/search?client=firefox&gl=<us|in>&hl=en&q=…", "query": out}


def cent(x):
    """'73.46' -> 7346; '' -> None (i valori del CSV hanno al massimo due decimali)."""
    x = (x or "").strip()
    if not x:
        return None
    return int(round(float(x) * 100))


def main():
    oggi = date.today().isoformat()
    errori = []
    GREZZI.mkdir(parents=True, exist_ok=True)
    fonti, testi = {}, {}
    # 1. zip OFLC
    st, zb, h = get(URL_ZIP)
    if st != 200 or zb[:2] != b"PK":
        sys.exit(f"ERRORE: zip OFLC non scaricato (HTTP {st})")
    (GREZZI / "OFLC_Wages_2026-27.zip").write_bytes(zb)
    z = zipfile.ZipFile(io.BytesIO(zb))
    nomi = set(z.namelist())
    for f in FILE_ZIP:
        if f not in nomi:
            errori.append(f"zip OFLC: manca {f}")
    if errori:
        sys.exit("ERRORE: " + "; ".join(errori))
    contenuto = {f: z.read(f) for f in FILE_ZIP}
    fonti["oflc_zip"] = {"url": URL_ZIP, "editore": "U.S. Department of Labor, Office of Foreign Labor Certification (OFLC)",
                         "titolo": "OFLC wage data files, wage year 2026-2027 (OFLC_Wages_2026-27.zip)", "http": st, "byte": len(zb), "sha256": sha(zb),
                         "last_modified": h.get("Last-Modified", ""), "letto_il": oggi,
                         "file": {f: {"sha256": sha(b), "byte": len(b)} for f, b in contenuto.items()}}
    testi["note"] = pdf_testo(contenuto[FILE_ZIP[4]])
    st, b, _ = get(URL_DOWNLOADS)
    testi["downloads"] = testo_html(b) if st == 200 else ""
    fonti["oflc_downloads"] = {"url": URL_DOWNLOADS, "editore": "OFLC", "titolo": "OFLC Wage Data Downloads", "http": st, "sha256": sha(testi["downloads"].encode()), "letto_il": oggi}
    if URL_ZIP not in b.decode("utf-8", "replace"):
        errori.append("la pagina OFLC Wage Data Downloads non collega più OFLC_Wages_2026-27.zip (nuovo anno? aggiornare URL_ZIP)")
    st, b, _ = get(URL_RICERCA)
    m = re.search(r'src="(/wage-search/static/js/main\.js[^"]*)"', b.decode("utf-8", "replace"))
    js = b""
    if st == 200 and m:
        st_js, js, _ = get("https://flag.dol.gov" + m.group(1))
    testi["ricerca"] = norm(js.decode("utf-8", "replace").replace("\\n", " "))
    fonti["oflc_ricerca"] = {"url": URL_RICERCA, "editore": "OFLC", "titolo": "OFLC Wage Search", "http": st,
                             "script": ("https://flag.dol.gov" + m.group(1).split("?")[0]) if m else "", "sha256": sha(js), "letto_il": oggi}
    # 2. BLS OEWS maggio 2025
    bls = {}
    for k, u in URL_BLS.items():
        st, b, h = get(u, UA_BLS)
        if st != 200 or b[:2] != b"PK":
            sys.exit(f"ERRORE: BLS {u} non scaricato (HTTP {st})")
        (GREZZI / Path(u).name).write_bytes(b)
        bls[k] = zipfile.ZipFile(io.BytesIO(b))
        fonti[k] = {"url": u, "editore": "U.S. Bureau of Labor Statistics (BLS)", "titolo": f"Occupational Employment and Wage Statistics, May 2025 ({Path(u).name})",
                    "pagina": PAGINA_BLS, "http": st, "byte": len(b), "sha256": sha(b), "last_modified": h.get("Last-Modified", ""), "letto_il": oggi}
    # 3. Federal Register
    fr = {}
    for k, num in DOCUMENTI_FR.items():
        meta, testo = leggi_fr(num)
        if not meta or not testo:
            errori.append(f"Federal Register: documento {num} non leggibile")
            continue
        for campo, atteso in ATTESI_FR[k].items():
            if meta.get(campo) != atteso:
                errori.append(f"Federal Register {num}: {campo} = {meta.get(campo)!r}, atteso {atteso!r}")
        meta["letto_il"] = oggi
        fr[k] = meta
        testi[f"fr:{k}"] = norm(meta.get("abstract") or "")
        testi[f"pdf:{k}"] = testo
    nuove = regole_finali_nuove()
    if nuove is None:
        errori.append("Federal Register: ricerca delle regole finali non riuscita")
    else:
        for r in nuove:
            if r["document_number"] != DOCUMENTI_FR["regola"]:
                errori.append(f"Federal Register: nuova regola finale da leggere: {r['publication_date']} {r['document_number']} {r['title'][:90]}")
    for k, v in LETTURE.items():
        if v["frammento"] not in testi.get(v["fonte"], ""):
            errori.append(f"{k}: frammento non trovato in {v['fonte']}: {v['frammento'][:110]!r}")
    # 4. file OFLC: aree, contee, occupazioni, istruzione, salari
    def leggi_csv(nome):
        return list(csv.DictReader(io.StringIO(contenuto[nome].decode("utf-8-sig"))))
    geo = leggi_csv("Geography.csv")
    aree, contee = {}, {}
    for r in geo:
        a = aree.setdefault(r["Area"], {"nome": r["AreaName"], "stati": []})
        if r["StateAb"] not in a["stati"]:
            a["stati"].append(r["StateAb"])
        contee.setdefault(r["StateAb"], {"nome": r["State"], "voci": []})["voci"].append([r["CountyTownName"], r["Area"]])
    occ = {r["soccode"]: r["Title"] for r in leggi_csv("oes_soc_occs.csv")}
    h_, it = xlsx_righe(contenuto[FILE_ZIP[3]], 0)
    app_a = {}
    for r in it:
        if r and r[0]:
            app_a.setdefault(str(r[0])[:7], r[2])
    alc = leggi_csv("ALC_Export.csv")
    if len(alc) < 400000 or set(alc[0]) != {"Area", "SocCode", "GeoLvl", "Level1", "Level2", "Level3", "Level4", "Average", "Label"}:
        errori.append(f"ALC_Export.csv inatteso ({len(alc)} righe, colonne {sorted(alc[0])})")
    calc = sorted(s for s in occ if s in app_a or s.startswith("15-") or s == "17-1011" or s.startswith("17-2"))
    ordine = sorted(aree, key=lambda a: (aree[a]["nome"], a))
    pos = {a: i for i, a in enumerate(ordine)}
    sal = {s: [None] * len(ordine) for s in calc}
    etichette = {}
    sigla = {"Annual Wage": "a", "High Wage": "h", "No Leveled Wage": "n"}
    for r in alc:
        s = r["SocCode"]
        if s not in sal:
            continue
        if r["Area"] not in pos:
            errori.append(f"area {r['Area']} di ALC_Export.csv non in Geography.csv")
            continue
        sal[s][pos[r["Area"]]] = [cent(r["Level1"]), cent(r["Level2"]), cent(r["Level3"]), cent(r["Level4"]), cent(r["Average"]), int(r["GeoLvl"])]
        if r["Label"]:
            if r["Label"] not in sigla:
                errori.append(f"etichetta sconosciuta {r['Label']!r} ({s}, {r['Area']})")
            etichette.setdefault(s, {})[r["Area"]] = sigla.get(r["Label"], "?")
    vuote = [s for s in calc if not any(sal[s])]
    if vuote:
        errori.append(f"occupazioni senza righe in ALC_Export.csv: {vuote[:5]}")
    # 5. BLS: nazionale e impieghi per area (gruppi 15 e 17: candidate alle pagine), controllo media OFLC = media BLS
    h_, it = xlsx_righe(bls["bls_nazionale"].read("oesm25nat/national_M2025_dl.xlsx"))
    i_ = {c: h_.index(c) for c in ("OCC_CODE", "O_GROUP", "TOT_EMP", "A_MEAN", "A_MEDIAN", "H_MEAN")}
    nazionale = {}
    for r in it:
        if r[i_["OCC_CODE"]] in occ and r[i_["O_GROUP"]] in ("detailed", "broad"):
            nazionale[r[i_["OCC_CODE"]]] = {k.lower(): (r[i_[k]] if isinstance(r[i_[k]], (int, float)) else None) for k in ("TOT_EMP", "A_MEAN", "A_MEDIAN", "H_MEAN")}
    candidate = [s for s in calc if s.startswith("15-") or s == "17-1011" or s.startswith("17-2")]
    impieghi = {s: {} for s in candidate}
    medie_bls = {}
    for nome in ("oesm25ma/MSA_M2025_dl.xlsx", "oesm25ma/BOS_M2025_dl.xlsx"):
        h_, it = xlsx_righe(bls["bls_aree"].read(nome))
        i_ = {c: h_.index(c) for c in ("AREA", "OCC_CODE", "TOT_EMP", "H_MEAN")}
        for r in it:
            s = r[i_["OCC_CODE"]]
            a = str(int(r[i_["AREA"]]))
            if s in impieghi and isinstance(r[i_["TOT_EMP"]], (int, float)):
                impieghi[s][a] = int(r[i_["TOT_EMP"]])
            if s in candidate and isinstance(r[i_["H_MEAN"]], (int, float)):
                medie_bls[(a, s)] = r[i_["H_MEAN"]]
    pari = tot = 0
    for s in candidate:
        for a, v in zip(ordine, sal[s]):
            if v and v[5] == 1 and (a, s) in medie_bls and v[4] is not None and s not in etichette.get(s, {}):
                tot += 1
                pari += v[4] == int(round(medie_bls[(a, s)] * 100))
    if tot < 1000 or pari / tot < 0.95:
        errori.append(f"media OFLC (Geo Level 1) uguale alla media oraria BLS dell'area solo in {pari} casi su {tot}")
    nonmsa = [a for s in impieghi for a in impieghi[s] if a not in aree]
    if nonmsa:
        errori.append(f"aree BLS senza corrispondenza in Geography.csv: {sorted(set(nonmsa))[:5]}")
    vecchio = json.loads(USCITA.read_text(encoding="utf-8")) if USCITA.exists() else {}
    dom = nuova_domanda() if "--domanda" in sys.argv else vecchio.get("domanda")
    if not dom:
        errori.append("domanda: nessun dato di autocompletamento (lanciare con --domanda)")
    if errori:
        print("ERRORI: i file dei dati NON sono stati aggiornati")
        for x in errori[:80]:
            print(" -", x)
        sys.exit(1)
    salari = {"_nota": "Generato da raccolta/h1b.py: estratto di ALC_Export.csv (OFLC_Wages_2026-27.zip). Per ogni occupazione una riga per area "
                       "nell'ordine di 'aree': [Level1, Level2, Level3, Level4, Average, GeoLvl] in centesimi (salari orari, o annuali se l'etichetta è 'a'); "
                       "null = nessuna riga. Etichette: a = Annual Wage, h = High Wage, n = No Leveled Wage.",
              "aree": ordine, "soc": sal, "etichette": etichette}
    testo_sal = json.dumps(salari, ensure_ascii=False, separators=(",", ":"))
    letture = {k: {"valore": v["valore"], "fonte": v["fonte"], "frammento": v["frammento"]} for k, v in LETTURE.items()}
    contenuto_j = {"letture": letture, "fonti": fonti, "federal_register": fr, "aree": aree, "contee": contee,
                   "occupazioni": {s: {"titolo": occ[s], "istruzione": app_a.get(s)} for s in calc},
                   "nazionale": {s: nazionale.get(s) for s in calc}, "impieghi": impieghi,
                   "salari": {"file": "dati/h1b_salari.json", "sha256": sha(testo_sal.encode()), "occupazioni": len(calc), "aree": len(ordine)},
                   "controllo_medie": {"uguali": pari, "su": tot}}
    uscita = {"_nota": "Generato da raccolta/h1b.py: non modificare a mano (i valori letti a mano stanno in LETTURE dentro lo script). "
                       "Fonti: OFLC (DOL), BLS OEWS maggio 2025, Federal Register, lette il giorno indicato.",
              "generato_il": oggi, "letto_il": oggi,
              "impronta": hashlib.sha256(json.dumps(contenuto_j, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20],
              "domanda": dom, **contenuto_j}
    USCITA_SAL.write_text(testo_sal + "\n", encoding="utf-8")
    USCITA.write_text(json.dumps(uscita, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"Scritti {USCITA} e {USCITA_SAL}: {len(calc)} occupazioni × {len(ordine)} aree, {len(fr)} documenti del Federal Register, "
          f"{len(letture)} frasi controllate; media OFLC = media BLS in {pari}/{tot} casi; zip {fonti['oflc_zip']['sha256'][:12]}; impronta {uscita['impronta']}.")


if __name__ == "__main__":
    main()
