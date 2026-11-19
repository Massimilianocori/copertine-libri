"""Salario minimo 2026-2027: fonti ufficiali e lettura delle cifre (sezione /minimum-wage/ del sito).

Importato da raccolta/fonti.py: FONTI_MINIMO si aggiunge all'elenco delle fonti (stesso formato) e regole_minimo(testi)
scrive la parte «minimo» di dati/regole.json. Ogni cifra è letta con un'espressione regolare dal testo della fonte: se una
pagina cambia testo lo script si ferma. Nessuna cifra è calcolata o stimata: se una fonte non dà la tariffa 2027, lo Stato
resta senza tariffa 2027.

Fonti: per le tariffe in vigore nel 2026 di tutti gli Stati la tabella «State Minimum Wage Laws» del Department of Labor;
per il 2027 la pagina o l'avviso dell'ufficio del lavoro dello Stato (per Michigan e Rhode Island la legge dello Stato,
perché i siti degli uffici del lavoro rispondono 403).
Non letti il 18/11/2026 (403, nessun blocco aggirato): Arizona (azica.gov), Colorado (cdle.colorado.gov), Maine (maine.gov),
Michigan (michigan.gov), Rhode Island (dlt.ri.gov), Massachusetts (mass.gov), Florida (floridajobs.org), District of Columbia (does.dc.gov).
"""
import re

DOL = "U.S. Department of Labor, Wage and Hour Division"

# id, file, url, titolo, chi pubblica, frasi da ritrovare alla lettera
FONTI_MINIMO = [
    ("mw_dol_stati", "mw_dol_stati.html", "https://www.dol.gov/agencies/whd/minimum-wage/state",
     "State Minimum Wage Laws", DOL, {
         "aggiornata": "Updated November 5, 2026",
         "senza_legge": "No state minimum wage law. Employers subject to the Fair Labor Standards Act must pay the current Federal minimum wage of $7.25 per hour.",
         "locali": "Some local governments set minimum wage rates higher than their respective state minimum wage.",
         "avvertenza": "The Wage and Hour Division tries to ensure that the information on this page is accurate, but individuals should consult the relevant state labor office for official information.",
         "michigan": "The Michigan minimum wage is scheduled to increase on January 1, 2027 to $15.00 per hour and then will be adjusted annually based on a set formula.",
         "florida": "The Florida minimum wage is scheduled to be updated annually based on a set formula beginning January 1, 2028.",
         "dc": "The minimum wage is adjusted annually on July 1 based on a set formula.",
     }),
    ("mw_dol_fed", "mw_dol_fed.html", "https://www.dol.gov/agencies/whd/minimum-wage",
     "Minimum Wage", DOL, {
         "federale": "The federal minimum wage is $7.25 per hour effective July 24, 2009.",
         "entrambe": "Many states also have minimum wage laws. Some state laws provide greater employee protections; employers must comply with both.",
     }),
    ("mw_ca", "mw_ca.html", "https://www.dir.ca.gov/dlse/minimum_wage.htm",
     "Minimum Wage", "California Department of Industrial Relations, Labor Commissioner's Office", {
         "a2026": "The minimum wage in California, effective January 1, 2026, is $16.90/hour for all employers.",
         "locali": "Some cities and counties have higher minimum wages than the state’s rate.",
         "fast_food": "Starting April 1, 2024, all “fast food restaurant employees” who are covered by the new law must be paid at least $20.00 per hour.",
     }),
    ("mw_ca_2027", "mw_ca_2027.html", "https://www.dir.ca.gov/DIRNews/2026/2026-66.html",
     "News Release 2026-66: California’s minimum wage set to increase to $17.40 per hour on January 1, 2027", "California Department of Industrial Relations", {
         "data": "Date: August 13, 2026",
         "a2027": "Beginning January 1, 2027, California’s statewide minimum wage will increase to $17.40 per hour",
         "certificato": "On July 31, 2026, the Department of Finance certified the minimum wage increase for 2027",
         "esenti": "Beginning January 1, 2027, an employee must earn an annual salary of at least $72,384 to meet the salary threshold for exemption.",
     }),
    ("mw_ca_faq", "mw_ca_faq.html", "https://www.dir.ca.gov/dlse/faq_minimumwage.htm",
     "Minimum Wage Frequently Asked Questions", "California Department of Industrial Relations, Labor Commissioner's Office", {
         "mance": "An employer may not use an employee's tips as a credit toward its obligation to pay the minimum wage per hour.",
     }),
    ("mw_wa", "mw_wa.html", "https://www.lni.wa.gov/workers-rights/wages/minimum-wage/",
     "Minimum Wage", "Washington State Department of Labor & Industries", {
         "a2027": "The new minimum wage for 2027 will be $17.73 an hour for most workers. The minimum wage for 14-and 15-year-old workers will be $15.07 an hour. These changes take effect Jan. 1, 2027.",
         "a2026": "minimum wage in the state of Washington is $17.13 per hour.",
         "mance": "Businesses may not use tips and service charges paid to an employee as part of an employee’s hourly minimum wage.",
         "locali": "Some local jurisdictions have higher minimum wage rates and different labor rules than Washington State.",
     }),
    ("mw_wa_avviso", "mw_wa_avviso.pdf", "https://www.lni.wa.gov/workers-rights/_docs/2027-minimum-wage-announcement-Accessible.pdf",
     "Announcement: 2027 minimum wage", "Washington State Department of Labor & Industries", {
         "a2027": "Washington’s minimum wage will be $17.73 per hour beginning Jan. 1, 2027.",
         "minori": "Workers who are 14 or 15 years old may be paid 85% of the adult minimum wage, or $15.07 per hour.",
     }),
    ("mw_ny", "mw_ny.html", "https://dol.ny.gov/minimum-wage-0",
     "New York State’s Minimum Wage", "New York State Department of Labor", {
         "uguale": "On January 1, 2027, New York’s minimum wage will stay the same.",
         "nyc": "$17.00 per hour in New York City, Long Island, and Westchester County",
         "resto": "$16.00 per hour in the rest of New York State",
         "motivo": "For 2027, the conditions for one of the off-ramps has been met.",
         "riga_nyc": "New York City $17.00 $14.15 Cash Wage $2.85 Tip Credit $11.35 Cash Wage $5.65 Tip Credit",
         "riga_li": "Long Island & Westchester $17.00 $14.15 Cash Wage $2.85 Tip Credit $11.35 Cash Wage $5.65 Tip Credit",
         "riga_resto": "Remainder of New York State $16.00 $13.30 Cash Wage $2.70 Tip Credit $10.70 Cash Wage $5.30 Tip Credit",
         "ospitalita": "Only hospitality employers are allowed to take credit from minimum wage.",
     }),
    ("mw_ct", "mw_ct.html", "https://portal.ct.gov/governor/news/press-releases/2026/08-2026/governor-lamont-announces-minimum-wage-will-increase",
     "Governor Lamont Announces Connecticut’s Minimum Wage Will Increase to $17.48 on January 1, 2027", "State of Connecticut, Office of the Governor", {
         "data": "8/05/2026 (HARTFORD, CT)",
         "a2027": "Connecticut’s minimum wage will adjust to $17.48 per hour beginning January 1, 2027—an increase from the 2026 rate of $16.94 per hour.",
         "indice": "the employment cost index increased by 3.2% over the twelve-month period ending on June 30, 2026, accounting for a $0.54 increase to the state’s minimum wage that will become effective on January 1, 2027.",
     }),
    ("mw_ct_dol", "mw_ct_dol.html", "https://portal.ct.gov/dol/divisions/wage-and-workplace-standards",
     "Wage and Workplace Standards", "Connecticut Department of Labor", {
         "elenco": "$17.48 effective on January 1, 2027 $16.94 effective on January 1, 2026",
     }),
    ("mw_mi", "mw_mi.html", "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-408-934",
     "Improved Workforce Opportunity Wage Act, section 408.934: Minimum hourly wage rate", "Michigan Legislature", {
         "tariffe": "(b) Beginning January 1, 2026, $13.73. (c) Beginning January 1, 2027, $15.00.",
         "indice": "Every October beginning in October, 2027, the state treasurer shall calculate an adjusted minimum wage rate.",
     }),
    ("mw_mn", "mw_mn.html", "https://www.dli.mn.gov/minwage",
     "Minimum wage in Minnesota", "Minnesota Department of Labor and Industry", {
         "tabella": "State minimum wage $11.41 an hour $11.87 an hour 90-day training wage (under 20 years of age) $9.31 an hour $9.68 an hour",
         "formazione": "The 90-day training wage for workers under age 20 will increase to $9.68.",
         "mance": "No employer may take a tip credit against minimum wages in Minnesota.",
     }),
    ("mw_mn_avviso", "mw_mn_avviso.html", "https://dli.mn.gov/news/minimum-wage-rate-adjusted-inflation-jan-1-2027",
     "Minimum-wage rate adjusted for inflation as of Jan. 1, 2027", "Minnesota Department of Labor and Industry", {
         "a2027": "Minnesota’s minimum-wage rate will be adjusted for inflation on Jan. 1, 2027, to $11.87 an hour for all employers in the state.",
         "data": "August 19, 2026",
     }),
    ("mw_mo", "mw_mo.html", "https://labor.mo.gov/dls/minimum-wage",
     "Minimum Wage", "Missouri Department of Labor and Industrial Relations", {
         "storia": "2025 $13.75 2026 $15.00 2027 $15.00",
         "mance": "Employers are required to pay tipped employees at least 50 percent of the minimum wage, $7.50 per hour, plus any amount necessary to bring the employee’s total compensation to a minimum of $15.00 per hour.",
         "piccoli": "Employers engaged in retail or service businesses whose annual gross income is less than $500,000 are not required to pay the state minimum wage rate.",
     }),
    ("mw_mt", "mw_mt.html", "https://erd.dli.mt.gov/labor-standards/wage-and-hour-payment-act/state-minimum-wage",
     "Montana's Minimum Wage", "Montana Department of Labor & Industry", {
         "tariffe": "Current Minimum Wage: $10.85 (Effective 1/1/2027: $11.20)",
         "mance": "No tip credit, meal credit, or training wage is allowed under Montana's Wage & Hour Laws.",
         "eccezione": "A business not covered by the Fair Labor Standards Act whose gross annual sales are $110,000 or less may pay $4.00 per hour.",
     }),
    ("mw_mt_lettera", "mw_mt_lettera.pdf", "https://erd.dli.mt.gov/labor-standards/wage-and-hour-payment-act/MW-Determination-Letter1.pdf",
     "2027 Montana Minimum Wage Determination Letter", "Montana Department of Labor & Industry", {
         "data": "October 7, 2026",
         "a2027": "Montana’s Minimum Wage will increase to $11.20 per hour effective January 1, 2027.",
     }),
    ("mw_ne", "mw_ne.html", "https://dol.nebraska.gov/LaborStandards",
     "Labor Standards Home", "Nebraska Department of Labor", {
         "a2027": "Labor Standards Home - $15.26 Minimum Wage Effective January 1, 2027",
     }),
    ("mw_nj", "mw_nj.html", "https://www.nj.gov/labor/lwdhome/press/2026/20260929_min_wage.shtml",
     "New Jersey’s Minimum Wage to Increase to $16.48/Hour for Most Employees on Jan. 1", "New Jersey Department of Labor and Workforce Development", {
         "data": "September 29, 2026",
         "a2027": "New Jersey’s statewide minimum wage will increase by $0.56 to $16.48 per hour for most employees, effective January 1, 2027.",
         "piccoli": "The rate for employees of seasonal and small employers (less than six employees) will increase to $16.25 on Jan. 1, up from $15.23.",
         "agricoli": "Agricultural workers will reach a significant milestone on Jan. 1 when their rate increases to $15 per hour, up from $14.20.",
         "mance": "The minimum cash wage rate for tipped workers will rise to $6.61 an hour from $6.05, with the maximum tip credit employers are able to claim remaining at $9.87.",
     }),
    ("mw_oh", "mw_oh.pdf", "https://dam.assets.ohio.gov/image/upload/com.ohio.gov/DICO/WageAndHour/2027_Minumum_Wage_Poster.pdf",
     "State of Ohio 2027 Minimum Wage (poster)", "Ohio Department of Commerce", {
         "titolo": "2027 MINIMUM WAGE",
         "a2027": "NON-TIPPED EMPLOYEES A Minimum Wage of $11.40 per hour",
         "mance": "TIPPED EMPLOYEES A Minimum Wage of $5.70 per hour PLUS TIPS",
         "piccoli": "“Employers” who gross less than $419,000 shall pay their employees no less than the current federal minimum wage rate.",
         "minori": "“Employees” under the age of 16 shall be paid no less than the current federal minimum wage rate.",
     }),
    ("mw_ri", "mw_ri.html", "https://webserver.rilegislature.gov/Statutes/TITLE28/28-12/28-12-3.htm",
     "Rhode Island General Laws § 28-12-3: Minimum wages", "State of Rhode Island General Assembly", {
         "a2026": "Commencing January 1, 2026, the minimum wage is sixteen dollars ($16.00) per hour.",
         "a2027": "Commencing January 1, 2027, the minimum wage is seventeen dollars ($17.00) per hour.",
     }),
    ("mw_sd", "mw_sd.html", "https://dlr.sd.gov/employment_laws/minimum_wage.aspx",
     "South Dakota Minimum Wage", "South Dakota Department of Labor and Regulation", {
         "a2026": "The minimum wage for non-tipped employees in South Dakota is $11.85/hour",
         "a2027": "the minimum wage for non-tipped employees in South Dakota will be $12.30/hour",
         "mance_2027": "Effective Jan. 1, 2027, the minimum wage for tipped employees in South Dakota will be $6.15",
     }),
    ("mw_sd_avviso", "mw_sd_avviso.pdf", "https://dlr.sd.gov/employment_laws/publications/min-wage-poster-2027-english.pdf",
     "2027 South Dakota Minimum Wage Requirement (posting)", "South Dakota Department of Labor and Regulation", {
         "titolo": "2027 South Dakota Minimum Wage Requirement $12.30/Hour",
         "mance": "Employers with tipped employees must pay a cash wage of no less than $6.15 per hour, which is no less than 50% of the state minimum wage.",
     }),
    ("mw_vt", "mw_vt.html", "https://labor.vermont.gov/rights-and-wages",
     "Worker Rights & Protections", "Vermont Department of Labor", {
         "a2027": "Effective 01/01/2027: $14.91 per hour worked/ $7.46 for tipped employees",
         "a2026": "Effective 01/01/2026: $14.42 per hour worked/ $7.21 for tipped employees",
     }),
    ("mw_va", "mw_va.html", "https://doli.virginia.gov/programs/labor-law/payment-of-wage/",
     "Payment of Wage", "Virginia Department of Labor and Industry", {
         "a2026": "For the period of January 1, 2026, until January 1, 2027, the established adjusted state hourly minimum wage is $12.77 per hour.",
         "a2027": "Beginning January 1, 2027, the Virginia minimum wage rate shall increase to $13.75 per hour.",
         "a2028": "Beginning January 1, 2028, the Virginia minimum wage rate shall increase to $15.00 per hour.",
         "agricoli": "Beginning January 1, 2027, farm laborers must be paid at a rate not less than the Virginia minimum wage.",
     }),
    ("mw_or", "mw_or.html", "https://www.oregon.gov/boli/workers/pages/minimum-wage.aspx",
     "Oregon Minimum Wage", "Oregon Bureau of Labor and Industries (BOLI)", {
         "periodo": "Oregon's minimum wage depends on work location. For July 1, 2026, through June 30, 2027, those rates are:",
         "portland": "$16.80 per hour - Portland metro",
         "standard": "$15.55 per hour - Standard",
         "rurale": "$14.55 per hour - Non-urban",
         "luglio": "Increases to the minimum wage are based on inflation (if applicable) and take effect on July 1st of each year",
     }),
    ("mw_ak", "mw_ak.html", "https://labor.alaska.gov/news/2025/news25-11.htm",
     "Press release No. 25-11: Alaska Minimum Wage will increase July 1, 2025", "Alaska Department of Labor and Workforce Development", {
         "data": "June 11, 2025 No. 25-11",
         "passi": "It will subsequently increase to $14.00 on July 1, 2026, and to $15.00 on July 1, 2027.",
         "indice": "Thereafter, the minimum wage will be adjusted annually for inflation starting January 1, 2028.",
     }),
    ("mw_hi", "mw_hi.html", "https://labor.hawaii.gov/wsd/minimum-wage/",
     "Minimum Wage and Overtime", "Hawaii Department of Labor and Industrial Relations, Wage Standards Division", {
         "tariffe": "$16.00 per hour beginning January 1, 2026; and $18.00 per hour beginning January 1, 2028.",
     }),
]

# sigla: (nome come nella tabella del Department of Labor, indirizzo della pagina)
STATI = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming",
}
# voci della tabella che non sono Stati (servono solo a tagliare il testo nel punto giusto)
TERRITORI = ["American Samoa", "Guam", "Northern Mariana Islands", "Puerto Rico", "Virgin Islands"]
# Stati il cui ufficio del lavoro ha rifiutato la richiesta (403) e per i quali nessun'altra fonte ufficiale letta dà la tariffa 2027
NON_LETTI = {"AZ": "azica.gov", "CO": "cdle.colorado.gov", "ME": "maine.gov"}
IMPORTO = r"\$(\d+\.\d\d)"


def _cerca(pattern, t, fid):
    m = re.search(pattern, t)
    if not m:
        raise SystemExit(f"{fid}: non trovo {pattern!r} nel testo della fonte")
    return m


def tabella_dol(t):
    """Tabella del Department of Labor: per ogni Stato tutte le tariffe scritte dopo «Basic Minimum Rate (per hour):»."""
    inizio = _cerca(r"Table of minimum wage by state Historical Table ", t, "mw_dol_stati").end()
    fine = _cerca(r"Some states set subminimum rates", t, "mw_dol_stati").start()
    corpo = t[inizio:fine]
    nomi = sorted(list(STATI.values()) + TERRITORI)
    # ogni voce comincia con il nome seguito da una di queste formule; così «New York City» o «Montana's» nel testo non tagliano
    testa = r"(?:No state minimum wage law|Basic Minimum Rate|Applicable to|Businesses with|Employers with|American Samoa has)"
    pos = []
    for n in nomi:
        m = re.search(rf"(?:^| ){re.escape(n)} (?={testa})", corpo)
        if not m:
            raise SystemExit(f"mw_dol_stati: non trovo la voce «{n}» nella tabella")
        pos.append((m.start(), m.end(), n))
    pos.sort()
    if [n for _, _, n in pos] != nomi:
        raise SystemExit("mw_dol_stati: le voci della tabella non sono in ordine alfabetico come attese")
    voci = {}
    for i, (_, b, n) in enumerate(pos):
        voci[n] = corpo[b:pos[i + 1][0] if i + 1 < len(pos) else len(corpo)].strip()
    out = {}
    for sigla, n in STATI.items():
        v = voci[n]
        tariffe = re.findall(r"Basic Minimum Rate \(per hour\): ((?:\$\d+\.\d\d(?: \([^)]*\))?(?:; )?)+)", v)
        if not tariffe and not v.startswith("No state minimum wage law"):
            raise SystemExit(f"mw_dol_stati: {n} senza tariffa e senza «No state minimum wage law»")
        out[sigla] = {"nome": n, "slug": n.lower().replace(" ", "-"),
                      "tariffe": [re.findall(IMPORTO, x) for x in tariffe],        # una lista per ogni riga «Basic Minimum Rate»
                      "testo_tariffe": [x.strip() for x in tariffe],
                      "federale_citato": "$7.25" in v, "formula_annuale": bool(re.search(r"adjusted annually|updated annually", v))}
    return out


def regole_minimo(testi):
    def uno(fid, pattern, gruppi=1):
        m = _cerca(pattern, testi[fid], fid)
        return m.group(1) if gruppi == 1 else m.groups()

    stati = tabella_dol(testi["mw_dol_stati"])
    fed = uno("mw_dol_fed", rf"The federal minimum wage is {IMPORTO} per hour effective July 24, 2009")
    agg = uno("mw_dol_stati", r"Updated (\w+ \d{1,2}, \d{4}) Table of minimum wage by state")
    d = {}   # Stati con una pagina propria: tariffe lette dalla fonte dello Stato

    d["CA"] = {"a2026": uno("mw_ca", rf"The minimum wage in California, effective January 1, 2026, is {IMPORTO}/hour"),
               "a2027": uno("mw_ca_2027", rf"Beginning January 1, 2027, California’s statewide minimum wage will increase to {IMPORTO} per hour"),
               "dal": "2027-01-01", "fonti_2026": ["mw_ca"], "fonti_2027": ["mw_ca_2027"], "annuncio": "2026-08-13", "mance": "nessun credito",
               "esenti_annuo": uno("mw_ca_2027", r"an annual salary of at least \$([\d,]+) to meet the salary threshold").replace(",", ""),
               "fast_food": uno("mw_ca", rf"must be paid at least {IMPORTO} per hour")}
    d["WA"] = {"a2026": uno("mw_wa", rf"2026 minimum wage in the state of Washington is {IMPORTO} per hour"),
               "a2027": uno("mw_wa", rf"The new minimum wage for 2027 will be {IMPORTO} an hour for most workers"),
               "dal": "2027-01-01", "fonti_2026": ["mw_wa"], "fonti_2027": ["mw_wa", "mw_wa_avviso"], "mance": "nessun credito",
               "minori_2027": uno("mw_wa", rf"14-and 15-year-old workers will be {IMPORTO} an hour")}
    if uno("mw_wa_avviso", rf"Washington’s minimum wage will be {IMPORTO} per hour beginning Jan\. 1, 2027") != d["WA"]["a2027"]:
        raise SystemExit("Washington: la pagina e l'avviso PDF danno tariffe 2027 diverse")
    ny = {}
    for chiave, nome in (("nyc", "New York City"), ("li", "Long Island & Westchester"), ("resto", "Remainder of New York State")):
        g = uno("mw_ny", rf"{nome} {IMPORTO} {IMPORTO} Cash Wage {IMPORTO} Tip Credit {IMPORTO} Cash Wage {IMPORTO} Tip Credit", 5)
        ny[chiave] = {"minimo": g[0], "servizio_contanti": g[1], "servizio_credito": g[2], "ristorazione_contanti": g[3], "ristorazione_credito": g[4]}
    _cerca(r"Minimum Wage as of 01/01/2027", testi["mw_ny"], "mw_ny")
    _cerca(r"On January 1, 2027, New York’s minimum wage will stay the same", testi["mw_ny"], "mw_ny")
    d["NY"] = {"a2026": ny["nyc"]["minimo"], "a2027": ny["nyc"]["minimo"], "dal": "2027-01-01", "invariato": True, "fonti_2026": ["mw_dol_stati"], "fonti_2027": ["mw_ny"],
               "zone": ny, "mance": "tabella"}
    g = uno("mw_ct", rf"will adjust to {IMPORTO} per hour beginning January 1, 2027—an increase from the 2026 rate of {IMPORTO} per hour", 2)
    d["CT"] = {"a2026": g[1], "a2027": g[0], "dal": "2027-01-01", "fonti_2026": ["mw_ct"], "fonti_2027": ["mw_ct", "mw_ct_dol"], "annuncio": "2026-08-05"}
    if uno("mw_ct_dol", rf"{IMPORTO} effective on January 1, 2027") != g[0]:
        raise SystemExit("Connecticut: il comunicato e la pagina del Department of Labor danno tariffe 2027 diverse")
    g = uno("mw_mi", rf"Beginning January 1, 2026, {IMPORTO}\. \(c\) Beginning January 1, 2027, {IMPORTO}\.", 2)
    d["MI"] = {"a2026": g[0], "a2027": g[1], "dal": "2027-01-01", "fonti_2026": ["mw_mi"], "fonti_2027": ["mw_mi", "mw_dol_stati"]}
    if uno("mw_dol_stati", rf"The Michigan minimum wage is scheduled to increase on January 1, 2027 to {IMPORTO} per hour") != g[1]:
        raise SystemExit("Michigan: la legge e la tabella del Department of Labor danno tariffe 2027 diverse")
    g = uno("mw_mn", rf"State minimum wage {IMPORTO} an hour {IMPORTO} an hour 90-day training wage \(under 20 years of age\) {IMPORTO} an hour {IMPORTO} an hour", 4)
    _cerca(r"Amount as of Jan\. 1, 2026 Amount as of Jan\. 1, 2027", testi["mw_mn"], "mw_mn")
    d["MN"] = {"a2026": g[0], "a2027": g[1], "dal": "2027-01-01", "fonti_2026": ["mw_mn"], "fonti_2027": ["mw_mn", "mw_mn_avviso"], "annuncio": "2026-08-19", "mance": "nessun credito",
               "formazione_2026": g[2], "formazione_2027": g[3]}
    if uno("mw_mn_avviso", rf"on Jan\. 1, 2027, to {IMPORTO} an hour for all employers") != g[1]:
        raise SystemExit("Minnesota: la pagina e il comunicato danno tariffe 2027 diverse")
    g = uno("mw_mo", rf"2026 {IMPORTO} 2027 {IMPORTO} Missouri Minimum Wage Summary", 2)
    d["MO"] = {"a2026": g[0], "a2027": g[1], "dal": "2027-01-01", "invariato": g[0] == g[1], "fonti_2026": ["mw_mo"], "fonti_2027": ["mw_mo"],
               "mance_2026": uno("mw_mo", rf"at least 50 percent of the minimum wage, {IMPORTO} per hour")}
    g = uno("mw_mt", rf"Current Minimum Wage: {IMPORTO} \(Effective 1/1/2027: {IMPORTO}\)", 2)
    d["MT"] = {"a2026": g[0], "a2027": g[1], "dal": "2027-01-01", "fonti_2026": ["mw_mt"], "fonti_2027": ["mw_mt", "mw_mt_lettera"], "annuncio": "2026-10-07", "mance": "nessun credito"}
    if uno("mw_mt_lettera", rf"will increase to {IMPORTO} per hour effective January 1, 2027") != g[1]:
        raise SystemExit("Montana: la pagina e la lettera danno tariffe 2027 diverse")
    d["NE"] = {"a2026": stati["NE"]["tariffe"][0][0], "a2027": uno("mw_ne", rf"{IMPORTO} Minimum Wage Effective January 1, 2027"), "dal": "2027-01-01",
               "fonti_2026": ["mw_dol_stati"], "fonti_2027": ["mw_ne"]}
    g = uno("mw_nj", rf"will rise to {IMPORTO} an hour from {IMPORTO}, with the maximum tip credit employers are able to claim remaining at {IMPORTO}", 3)
    p = uno("mw_nj", rf"\(less than six employees\) will increase to {IMPORTO} on Jan\. 1, up from {IMPORTO}", 2)
    d["NJ"] = {"a2026": stati["NJ"]["tariffe"][0][0], "a2027": uno("mw_nj", rf"will increase by \$0\.56 to {IMPORTO} per hour for most employees, effective January 1, 2027"),
               "dal": "2027-01-01", "fonti_2026": ["mw_dol_stati"], "fonti_2027": ["mw_nj"], "annuncio": "2026-09-29",
               "mance_2026": g[1], "mance_2027": g[0], "credito_mance": g[2], "piccoli_2026": p[1], "piccoli_2027": p[0]}
    d["OH"] = {"a2026": stati["OH"]["tariffe"][0][0], "a2027": uno("mw_oh", rf"NON-TIPPED EMPLOYEES A Minimum Wage of {IMPORTO} per hour"), "dal": "2027-01-01",
               "fonti_2026": ["mw_dol_stati"], "fonti_2027": ["mw_oh"], "mance_2027": uno("mw_oh", rf"TIPPED EMPLOYEES A Minimum Wage of {IMPORTO} per hour PLUS TIPS"),
               "soglia_2027": uno("mw_oh", r"who gross less than \$([\d,]+) shall pay").replace(",", ""),
               "soglia_2026": uno("mw_dol_stati", r"Ohio Employers with annual gross receipts of \$([\d,]+) or more").replace(",", "")}
    d["RI"] = {"a2026": uno("mw_ri", rf"Commencing January 1, 2026, the minimum wage is sixteen dollars \({IMPORTO}\) per hour"),
               "a2027": uno("mw_ri", rf"Commencing January 1, 2027, the minimum wage is seventeen dollars \({IMPORTO}\) per hour"), "dal": "2027-01-01",
               "fonti_2026": ["mw_ri"], "fonti_2027": ["mw_ri"]}
    d["SD"] = {"a2026": uno("mw_sd", rf"The minimum wage for non-tipped employees in South Dakota is {IMPORTO}/hour"),
               "a2027": uno("mw_sd", rf"the minimum wage for non-tipped employees in South Dakota will be {IMPORTO}/hour"), "dal": "2027-01-01",
               "fonti_2026": ["mw_sd"], "fonti_2027": ["mw_sd", "mw_sd_avviso"],
               "mance_2026": uno("mw_sd", r"The minimum wage for tipped employees in South Dakota is \$(\d+\.\d{2,3}) ?/hour"),
               "mance_2027": uno("mw_sd", rf"the minimum wage for tipped employees in South Dakota will be {IMPORTO}")}
    if uno("mw_sd_avviso", rf"2027 South Dakota Minimum Wage Requirement {IMPORTO}/Hour") != d["SD"]["a2027"] or \
            uno("mw_sd_avviso", rf"a cash wage of no less than {IMPORTO} per hour") != d["SD"]["mance_2027"]:
        raise SystemExit("South Dakota: la pagina e l'avviso PDF danno cifre 2027 diverse")
    g7 = uno("mw_vt", rf"Effective 01/01/2027: {IMPORTO} per hour worked/ {IMPORTO} for tipped employees", 2)
    g6 = uno("mw_vt", rf"Effective 01/01/2026: {IMPORTO} per hour worked/ {IMPORTO} for tipped employees", 2)
    d["VT"] = {"a2026": g6[0], "a2027": g7[0], "dal": "2027-01-01", "fonti_2026": ["mw_vt"], "fonti_2027": ["mw_vt"], "mance_2026": g6[1], "mance_2027": g7[1]}
    d["VA"] = {"a2026": uno("mw_va", rf"For the period of January 1, 2026, until January 1, 2027, the established adjusted state hourly minimum wage is {IMPORTO} per hour"),
               "a2027": uno("mw_va", rf"Beginning January 1, 2027, the Virginia minimum wage rate shall increase to {IMPORTO} per hour"), "dal": "2027-01-01",
               "fonti_2026": ["mw_va"], "fonti_2027": ["mw_va"], "a2028": uno("mw_va", rf"Beginning January 1, 2028, the Virginia minimum wage rate shall increase to {IMPORTO} per hour")}
    _cerca(r"For July 1, 2026, through June 30, 2027, those rates are:", testi["mw_or"], "mw_or")
    d["OR"] = {"a2026": uno("mw_or", rf"{IMPORTO} per hour - Standard"), "a2027": None, "dal": None, "prossimo": "2027-07-01", "fonti_2026": ["mw_or"], "fonti_2027": ["mw_or"],
               "zone": {"portland": uno("mw_or", rf"{IMPORTO} per hour - Portland metro"), "standard": uno("mw_or", rf"{IMPORTO} per hour - Standard"),
                        "rurale": uno("mw_or", rf"{IMPORTO} per hour - Non-urban")}}

    # ---- le date degli annunci scritte sopra devono essere nelle fonti
    for s_, fid, scritta in (("CA", "mw_ca_2027", "Date: August 13, 2026"), ("CT", "mw_ct", "8/05/2026 (HARTFORD, CT)"), ("MN", "mw_mn_avviso", "August 19, 2026"),
                             ("MT", "mw_mt_lettera", "October 7, 2026"), ("NJ", "mw_nj", "FOR IMMEDIATE RELEASE September 29, 2026")):
        if scritta not in testi[fid]:
            raise SystemExit(f"{s_}: la data dell'annuncio «{scritta}» non è nella fonte {fid}")
    # ---- la tariffa 2026 della fonte dello Stato deve essere quella della tabella del Department of Labor
    for s, v in d.items():
        if v["a2026"] != stati[s]["tariffe"][0][0]:
            raise SystemExit(f"{s}: tariffa 2026 dello Stato ({v['a2026']}) diversa dalla tabella del Department of Labor ({stati[s]['tariffe'][0][0]})")
        if v["a2027"] is not None and float(v["a2027"]) < float(v["a2026"]):
            raise SystemExit(f"{s}: tariffa 2027 più bassa del 2026: rileggere la fonte")
    if stati["NY"]["tariffe"][0] != [ny["nyc"]["minimo"], ny["resto"]["minimo"]] or ny["li"] != ny["nyc"]:
        raise SystemExit("New York: zone diverse dalla tabella del Department of Labor")
    if stati["OR"]["tariffe"][0] != [d["OR"]["zone"]["standard"], d["OR"]["zone"]["portland"], d["OR"]["zone"]["rurale"]]:
        raise SystemExit("Oregon: zone diverse dalla tabella del Department of Labor")
    hi = uno("mw_hi", rf"{IMPORTO} per hour beginning January 1, 2026; and {IMPORTO} per hour beginning January 1, 2028", 2)
    if hi[0] != stati["HI"]["tariffe"][0][0]:
        raise SystemExit("Hawaii: tariffa 2026 diversa dalla tabella del Department of Labor")
    _cerca(r"Florida Basic Minimum Rate \(per hour\): \$\d+\.\d\d The Florida minimum wage is scheduled to be updated annually based on a set formula beginning January 1, 2028\.", testi["mw_dol_stati"], "mw_dol_stati")
    # Alaska (revisione del 18/11/2026): la tabella federale non lo dice, ma il comunicato dello Stato dà il passo del 1° luglio 2027
    ak = uno("mw_ak", rf"It will subsequently increase to {IMPORTO} on July 1, 2026, and to {IMPORTO} on July 1, 2027\.", 2)
    if ak[0] != stati["AK"]["tariffe"][0][0] or float(ak[1]) <= float(ak[0]):
        raise SystemExit("Alaska: tariffa dal 1° luglio 2026 diversa dalla tabella del Department of Labor")
    # Stati senza pagina propria per i quali una fonte ufficiale dice quando arriva il prossimo cambio (nessuna tariffa nuova il 1/1/2027)
    prossimo = {"AK": {"dal": "2027-07-01", "tariffa": ak[1], "fonte": "mw_ak"},
                "HI": {"dal": "2028-01-01", "tariffa": hi[1], "fonte": "mw_hi"},
                "FL": {"dal": "2028-01-01", "tariffa": None, "fonte": "mw_dol_stati"},
                "DC": {"dal": "2027-07-01", "tariffa": None, "fonte": "mw_dol_stati"}}
    if not re.search(r"District of Columbia Basic Minimum Rate \(per hour\): \$\d+\.\d\d Premium Pay After Designated Hours 1 : Weekly - 40 The minimum wage is adjusted annually on July 1 based on a set formula\.", testi["mw_dol_stati"]):
        raise SystemExit("mw_dol_stati: District of Columbia, frase sul 1° luglio non trovata")
    return {"fonte_tabella": "mw_dol_stati", "tabella_aggiornata": agg, "federale": {"fonte": "mw_dol_fed", "tariffa": fed, "dal": "2009-07-24"},
            "stati": stati, "dettaglio": d, "prossimo": prossimo, "non_letti": NON_LETTI}
