"""Scarica le fonti ufficiali, ne registra URL, data e impronta SHA-256, controlla le frasi citate alla lettera e
ricava le regole di calcolo (dati/regole.json).

Uso (dalla radice del repository):
    python3 paycheck/raccolta/fonti.py            # riscarica tutto (curl, nessun blocco aggirato)
    python3 paycheck/raccolta/fonti.py --locale   # non scarica: rilegge i file già in dati/grezzi/

Uscite: dati/fonti.json (una voce per fonte: url, file, sha256, letto_il, http, frasi trovate) e dati/regole.json
(tabelle e aliquote lette dai file grezzi, ognuna con l'id della fonte). Ogni cifra di regole.json viene da
un'espressione regolare o da una tabella letta dal file grezzo: se una fonte cambia testo lo script si ferma.
"""
import hashlib
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import testo as T  # noqa: E402

DATI = QUI.parent / "dati"
GREZZI = DATI / "grezzi"
UA = "Mozilla/5.0 (X11; Linux x86_64) research-bot"
ANNO = 2026

# id, file, url, titolo (inglese, va in pagina), chi pubblica, frasi da ritrovare alla lettera
FONTI = [
    ("irs_p15t", "irs_p15t.pdf", "https://www.irs.gov/pub/irs-pdf/p15t.pdf",
     "Publication 15-T (2026), Federal Income Tax Withholding Methods", "Internal Revenue Service", {
         "uso": "If you’re an employer with an automated payroll system, use Worksheet 1A and the Percentage Method tables in this section to figure federal income tax withholding.",
         "1g": "If the box in Step 2 of Form W-4 is checked, enter -0-. If the box is not checked, enter $12,900 if the taxpayer is married filing jointly or $8,600 otherwise",
         "1i": "Subtract line 1h from line 1e. If zero or less, enter -0-. This is the Adjusted Annual Wage Amount",
         "2h": "Divide the amount on line 2g by the number of pay periods on line 1b. This is the Tentative Withholding Amount",
         "3c": "Subtract line 3b from line 2h. If zero or less, enter -0-",
         "4b": "Add lines 3c and 4a. This is the amount to withhold from the employee’s wages this pay period",
         "arrotonda": "You may also round the tax for the pay period to the nearest dollar. If rounding is used, it must be used consistently.",
     }),
    ("irs_p15", "irs_p15.pdf", "https://www.irs.gov/pub/irs-pdf/p15.pdf",
     "Publication 15 (2026), (Circular E), Employer’s Tax Guide", "Internal Revenue Service", {
         "ss": "For 2026, the social security tax rate is 6.2% (amount withheld) each for the employer and employee (12.4% total). The social security wage base limit is $184,500.",
         "medicare": "The tax rate for Medicare is 1.45% (amount withheld) each for the employee and employer (2.9% total). There is no wage base limit for Medicare tax; all covered wages are subject to Medicare tax.",
         "addl": "0.9% Additional Medicare Tax from wages you pay to an employee in excess of $200,000 in a calendar year.",
         "addl_solo": "Additional Medicare Tax is only imposed on the employee. There is no employer share of Additional Medicare Tax.",
         "futa": "For 2026, the FUTA tax rate is 6.0%. The tax applies to the first $7,000 you pay to each employee as wages during the year.",
         "futa_credito": "The credit may be as much as 5.4% of FUTA taxable wages. If you’re entitled to the maximum 5.4% credit, the FUTA tax rate after credit is 0.6%.",
         "futa_condizione": "You’re entitled to the maximum credit if you paid your state unemployment taxes in full, on time, and on all the same wages as are subject to FUTA tax, and as long as the state isn’t determined to be a credit reduction state.",
     }),
    ("irs_fw4", "irs_fw4.pdf", "https://www.irs.gov/pub/irs-pdf/fw4.pdf",
     "Form W-4 (2026), Employee’s Withholding Certificate", "Internal Revenue Service", {
         "step2": "Multiple Jobs or Spouse Works",
         "step3": "Claim Dependent and Other Credits",
         "step4": "Other Adjustments",
     }),
    ("irs_p15t_2027", "irs_p15t_2027_draft.pdf", "https://www.irs.gov/pub/irs-dft/p15t--dft.pdf",
     "Publication 15-T for 2027, early release draft", "Internal Revenue Service", {
         "bozza": "This is an early release draft of an IRS tax form, instructions, or publication, which the IRS is providing for your information.",
         "tabelle": "The 2027 federal income tax withholding tables are provided as an Excel attachment to this PDF rather than incorporated into this early release draft of Publication 15-T.",
     }),
    ("dol_futa", "dol_futa_credit.html", "https://oui.doleta.gov/unemploy/futa_credit.asp",
     "FUTA Credit Reductions", "U.S. Department of Labor, Employment and Training Administration", {
         "regola": "employers in states with a further credit reduction due to an outstanding balance of advances will incur a FUTA tax rate of .6% + FUTA credit reduction",
     }),
    ("dol_futa_2026", "dol_final_credit_states_2026.xlsx", "https://oui.doleta.gov/unemploy/docs/final_credit_states_2026.xlsx",
     "Final 2026 Federal Unemployment Tax Act (FUTA) Credit Reductions", "U.S. Department of Labor, Employment and Training Administration", {
         "titolo": "Final 2026 Federal Unemployment Tax Act (FUTA) Credit Reductions",
         "ca": "therefore employers in California are subject to a 1.5% credit reduction",
     }),
    ("tx_rates", "tx_tax_rates.html", "https://www.twc.texas.gov/programs/unemployment-tax/tax-rates",
     "Unemployment Insurance Tax Rates", "Texas Workforce Commission", {
         "base": "The maximum amount of taxable wages per employee per calendar year is set by statute and is currently $9,000.",
         "nuovo": "For 2026, the entry-level rate is 2.70% for all groups with no exceptions.",
         "formula": "The effective tax rate for experience-rated employers is the sum of five components.",
     }),
    ("tx_your", "tx_twc.html", "https://www.twc.texas.gov/programs/unemployment-tax/your-tax-rates",
     "Your 2026 Tax Rates", "Texas Workforce Commission", {
         "minmax": "The minimum tax rate for 2026 is 0.32 percent. The maximum tax rate for 2026 is 6.32 percent.",
         "rtr": "The second component of your UI tax rate is the Replenishment Tax Rate (RTR), a flat tax paid by all employers.",
         "rtr_2026": "The RTR for 2026 is 0.21 percent.",
         "base": "You pay unemployment tax on the first $9,000 that each employee earns during the calendar year.",
     }),
    ("fl_rt", "fl_rt.html", "https://floridarevenue.com/taxes/taxesfees/Pages/reemployment.aspx",
     "Florida Reemployment Tax", "Florida Department of Revenue", {
         "nuovo": "The initial tax rate for new employers is .0270 (2.7%), which is applied to the first $7,000 in wages paid to each employee during a calendar year.",
         "base": "Only the first $7,000 of wages paid to each employee by their employer in a calendar year is taxable.",
         "chi": "Reemployment tax is paid by employers",
     }),
    ("ca_rates", "ca_rates.html", "https://edd.ca.gov/en/payroll_taxes/rates_and_withholding/",
     "Contribution Rates, Withholding Schedules, and Meals and Lodging Values", "California Employment Development Department (EDD)", {
         "ui_nuovo": "New employers are assigned a 3.4 percent UI rate for two to three years.",
         "ui_2026": "The UI rate schedule for 2026 is Schedule F+.",
         "ui_base": "The taxable wage limit is $7,000 per employee, per calendar year.",
         "ett_2026": "The ETT rate for 2026 is 0.1 percent. The ETT taxable wage limit is $7,000 per employee, per calendar year.",
         "sdi_2026": "The SDI withholding rate for 2026 is 1.3 percent.",
         "sdi_tutto": "Senate Bill 951 removes the taxable wage limit and maximum withholdings for each employee subject to SDI contributions.",
         "sdi_2027": "The SDI withholding rate for 2027 is 1.4 percent.",
     }),
    ("ca_methb", "ca_26methb.pdf", "https://edd.ca.gov/siteassets/files/pdf_pub_ctr/26methb.pdf",
     "California Withholding Schedules for 2026, Method B – Exact Calculation Method", "California Employment Development Department (EDD)", {
         "metodo": "Method B may be used to calculate withholding amounts either manually or by computer. This method will give an exact amount of tax to withhold.",
         "step1": "Determine if the employee’s gross wages are less than, or equal to, the amount shown in Table 1",
         "step1b": "If so, no income tax is required to be withheld.",
         "step3": "Subtract the standard deduction amount shown in Table 3 - Standard Deduction Table to arrive at the employee’s taxable income.",
         "step5": "Subtract the tax credit shown in Table 4 - Exemption Allowance Table",
         "sposati": "we recommend that you use one of the following options: Single filing status to compute withholding amounts for the employee and spouse; or withhold an additional flat amount of tax.",
     }),
    ("il_700t", "il_700t.pdf", "https://tax.illinois.gov/content/dam/soi/en/web/tax/forms/withholding/documents/currentyear/il-700-t.pdf",
     "2026 Booklet IL-700-T, Illinois Withholding Tax Tables", "Illinois Department of Revenue", {
         "aliquota": "The income tax rate is 4.95 percent and the exemption allowance is $2,925.",
         "riga1": "Multiply the number of allowances your employee claimed on Form IL-W-4, Line 1, by $2,925.",
         "riga2": "Multiply the number of allowances your employee claimed on Form IL-W-4, Line 2, by $1,000.",
         "step4": "Multiply the taxable amount by 4.95 percent (.0495). You must withhold this amount.",
     }),
    ("il_ea50", "il_ea50_2026.pdf", "https://ides.illinois.gov/content/dam/soi/en/web/ides/ides_forms_and_publications/EA-50_2026.pdf",
     "EA-50 Report 2026: State Experience Factor and Employers’ UI Contribution Rates", "Illinois Department of Employment Security (IDES)", {
         "nuovo": "Most employers who became liable for the payment of contributions on or after January 1, 2024 will pay at the entry rate of 3.350%.",
         "fondo": "The above entry rate includes the 0.550% Fund Building Rate in effect for 2026.",
         "base": "Only the first $14,250 of wages paid to a worker in the calendar year 2026 are subject to the payment of contributions.",
     }),
    ("nc_30", "nc_30.pdf", "https://www.ncdor.gov/income-tax-withholding-tables-and-instructions-employers/open",
     "NC-30, 2026 Income Tax Withholding Tables and Instructions for Employers", "North Carolina Department of Revenue", {
         "aliquota": "tax year 2026 will be 3.99%. This change is reflected in the tables and computations included in this publication",
         "ritenuta": "The withholding calculations are based on the individual income tax rate of 3.99% plus 0.1%. This results in a withholding tax rate of 4.09%. Round off the final amount to the nearest whole dollar.",
     }),
    ("nc_des", "nc_des.html", "https://www.des.nc.gov/employers/tax-rate-information",
     "Tax Rate Information", "North Carolina Division of Employment Security", {
         "base": "Taxable Wage Base for 2026 $34,200",
         "nuovo": "UI Tax Rate for Beginning Employers 1%",
         "minmax": "your rate could be as low as 0.060% or as high as 5.760%",
     }),
    ("patriot", "patriot_aff.html", "https://www.patriotsoftware.com/affiliates/",
     "Patriot Software affiliate program", "Patriot Software", {
         "compenso": "You receive $150 per new customer.",
         "impact": "Apply Now With Impact",
         "prodotti": "Patriot offers two payroll software products— Basic Payroll and Full Service Payroll . Run unlimited payrolls and pay employees with ease.",
     }),
]


def scarica(url, dest):
    r = subprocess.run(["curl", "-sL", "-m", "120", "-A", UA, "-o", str(dest), "-w", "%{http_code}", url], capture_output=True, text=True)
    return int(r.stdout.strip() or 0)


def _testo_tmp(tmp, dest):
    """Testo di un file appena scaricato (nome.ext.tmp): T.testo sceglie il lettore dall'estensione vera."""
    copia = tmp.with_name("_lettura_" + dest.name)
    copia.write_bytes(tmp.read_bytes())
    try:
        return T.testo(copia)
    finally:
        copia.unlink(missing_ok=True)


def soldi(s):
    return float(s.replace("$", "").replace(",", ""))


def cerca(pattern, t, fid):
    m = re.search(pattern, t)
    if not m:
        raise SystemExit(f"{fid}: non trovo {pattern!r} nel testo della fonte")
    return m


# ---------------------------------------------------------------- tabelle federali (Pub. 15-T, sezione 1)
def tabelle_federali():
    righe = T.pdf(GREZZI / "irs_p15t.pdf", layout=True).split("\n")
    inizi = [i for i, r in enumerate(righe) if "Percentage Method Tables for Automated Payroll Systems and Withholding on Periodic" in r and str(ANNO) in r]
    if len(inizi) != 1:
        raise SystemExit(f"irs_p15t: intestazione della tabella trovata {len(inizi)} volte")
    stati = {"Married Filing Jointly": "mfj", "Single or Married Filing Separately": "single", "Head of Household": "hoh"}
    tab = {"std": {}, "step2": {}}
    corrente = None
    for r in righe[inizi[0]:inizi[0] + 60]:
        pulita = re.sub(r"\s+", " ", r).strip()
        for nome, k in stati.items():
            if pulita == f"{nome} {nome}":
                corrente = k
                tab["std"][k], tab["step2"][k] = [], []
        tok = re.findall(r"\$[\d,]+(?:\.\d\d)?|\d+%", r)
        if corrente and len(tok) in (10, 8):
            n = len(tok) // 2
            for lato, meta in (("std", tok[:n]), ("step2", tok[n:])):
                a = soldi(meta[0])
                c, d, e = soldi(meta[-3]), int(meta[-2].rstrip("%")), soldi(meta[-1])
                b = soldi(meta[1]) if n == 5 else None
                if a != e:
                    raise SystemExit(f"irs_p15t: colonna A diversa da E nella riga {pulita}")
                tab[lato][corrente].append({"da": int(a), "fino": int(b) if b is not None else None, "base": c, "pct": d})
        if pulita.startswith("Publication 15-T") and corrente == "hoh" and len(tab["std"]["hoh"]) == 8:
            break
    for lato in tab:
        for k, v in tab[lato].items():
            if len(v) != 8 or [x["pct"] for x in v] != [0, 10, 12, 22, 24, 32, 35, 37]:
                raise SystemExit(f"irs_p15t: tabella {lato}/{k} letta male: {v}")
            for i in range(7):
                if v[i]["fino"] != v[i + 1]["da"]:
                    raise SystemExit(f"irs_p15t: scaglioni non contigui in {lato}/{k}")
                atteso = v[i]["base"] + (v[i]["fino"] - v[i]["da"]) * v[i]["pct"] / 100
                if abs(atteso - v[i + 1]["base"]) > 0.51:  # gli scaglioni del riquadro Step 2 sono arrotondati al dollaro
                    raise SystemExit(f"irs_p15t: importo di base incoerente in {lato}/{k} riga {i + 2}: {atteso} contro {v[i + 1]['base']}")
    return tab


# ---------------------------------------------------------------- California, Method B
CA_PERIODI = {"weekly": "Weekly", "biweekly": "Biweekly", "semimonthly": "Semi-monthly", "monthly": "Monthly"}
CA_COL = {"weekly": 0, "biweekly": 1, "semimonthly": 2, "monthly": 3}   # colonne delle tabelle 2 e 4
CA_TAB = {"semimonthly": (17, 18, 19), "monthly": (20, 21, 22), "weekly": (23, 24, 25), "biweekly": (26, 27, 28)}  # single, married, hoh
CA_INTEST = {17: "Semi-monthly Payroll Period", 20: "Monthly Payroll Period", 23: "Weekly Payroll Period", 26: "Bi-weekly Payroll Period"}


def california():
    righe = T.pdf(GREZZI / "ca_26methb.pdf", layout=True).split("\n")

    def blocco(titolo):
        i = next(n for n, r in enumerate(righe) if r.strip().startswith(titolo))
        return righe[i:i + 40]

    def tabella_periodi(titolo):
        out = {}
        for r in blocco(titolo):
            for k, nome in CA_PERIODI.items():
                if r.strip().startswith(nome + " "):
                    v = [int(soldi(x)) for x in re.findall(r"\$[\d,]+", r)]
                    if len(v) != 4:
                        raise SystemExit(f"ca_methb: riga {nome} di {titolo} letta male")
                    out[k] = {"single": v[0], "married01": v[1], "married2": v[2], "hoh": v[3]}
        if set(out) != set(CA_PERIODI):
            raise SystemExit(f"ca_methb: {titolo} incompleta")
        return out

    def tabella_numero(titolo, primo, decimali):
        out = {k: [] for k in CA_COL}
        atteso = primo
        for r in blocco(titolo):
            m = re.match(r"\s*(\d+)\s+\$", r)
            if not m:
                # la riga "10" ha il numero della nota attaccato (102) oppure su una riga a parte
                m2 = re.match(r"\s+\$[\d,.]+\s+\$", r)
                if not (atteso == 10 and (m2 or re.match(r"\s*102\s+\$", r))):
                    continue
            elif int(m.group(1)) != atteso and not (atteso == 10 and m.group(1) == "102"):
                continue
            v = re.findall(r"\$([\d,]+\.\d\d)" if decimali else r"\$([\d,]+)(?!\.)", r)
            if len(v) != 8:
                raise SystemExit(f"ca_methb: riga {atteso} di {titolo} letta male: {r}")
            for k, c in CA_COL.items():
                out[k].append(soldi(v[c]))
            atteso += 1
            if atteso > 10:
                break
        if atteso != 11:
            raise SystemExit(f"ca_methb: {titolo} si ferma alla riga {atteso - 1}")
        return out

    esenzione = tabella_periodi("Method B - Table 1: Low Income Exemption Table")
    deduzione = tabella_periodi("Method B - Table 3: Standard Deduction Table")
    stimate = tabella_numero("Method B - Table 2: Estimated Deduction Table", 1, False)      # 1..10
    credito = tabella_numero("Method B - Table 4: Exemption Allowance Table", 0, True)       # 0..10

    # tabelle 17-28: due tabelle affiancate per riga
    scaglioni = {}
    sinistra = destra = None
    for r in righe:
        m = re.findall(r"Method B - Table (\d+):", r)
        if len(m) == 2:
            sinistra, destra = int(m[0]), int(m[1])
            scaglioni[sinistra], scaglioni[destra] = [], []
            continue
        if sinistra is None:
            continue
        meta = re.findall(r"(\d+\.\d{3})%\s+\$([\d,]+)\s+\$([\d,]+\.\d\d)", r)
        if len(meta) == 2:
            for n, (pct, oltre, piu) in zip((sinistra, destra), meta):
                scaglioni[n].append({"da": int(soldi(oltre)), "pct": float(pct), "base": soldi(piu)})
    intest = "\n".join(righe)
    for n, t in CA_INTEST.items():
        if not re.search(re.escape(t) + r"[^\n]*\n(?:[^\n]*\n){0,3}[^\n]*Method B - Table " + str(n) + ":", intest) and \
           not re.search(r"Method B - Table \d+:[^\n]*Method B - Table " + str(n) + ":", intest) and \
           not re.search(r"Method B - Table " + str(n) + ":", intest):
            raise SystemExit(f"ca_methb: tabella {n} non trovata")
    # l'ordine dei periodi si controlla sulle righe d'intestazione
    for riga_int, (a, b) in (("Semi-monthly Payroll Period", (17, 20)), ("Weekly Payroll Period", (23, 26))):
        i = next(n for n, r in enumerate(righe) if r.strip().startswith(riga_int))
        j = next(n for n in range(i, i + 6) if "Method B - Table" in righe[n])
        if [int(x) for x in re.findall(r"Table (\d+):", righe[j])] != [a, b]:
            raise SystemExit(f"ca_methb: dopo «{riga_int}» mi aspettavo le tabelle {a} e {b}")
    aliquote = [1.1, 2.2, 4.4, 6.6, 8.8, 10.23, 11.33, 12.43, 13.53, 14.63]
    tab = {}
    for per, nums in CA_TAB.items():
        tab[per] = {}
        for stato, n in zip(("single", "married", "hoh"), nums):
            v = scaglioni.get(n, [])
            if [x["pct"] for x in v] != aliquote or v[0]["da"] != 0 or v[0]["base"] != 0:
                raise SystemExit(f"ca_methb: tabella {n} letta male: {v}")
            for i in range(9):
                atteso = v[i]["base"] + (v[i + 1]["da"] - v[i]["da"]) * v[i]["pct"] / 100
                if abs(atteso - v[i + 1]["base"]) > 0.03:
                    raise SystemExit(f"ca_methb: tabella {n}, riga {i + 2}: importo «plus» {v[i + 1]['base']} contro {atteso:.2f}")
            tab[per][stato] = v
    return {"esenzione_basso_reddito": esenzione, "deduzione_standard": deduzione, "deduzioni_stimate": stimate, "credito_esenzioni": credito, "scaglioni": tab}


# ---------------------------------------------------------------- North Carolina, NC-30
def north_carolina():
    t = T.pdf(GREZZI / "nc_30.pdf", layout=True)
    i = t.index("Percentage Method - Formula Tables for Percentage Method Withholding Computations")
    j = t.index("Example:", i)
    pezzo = t[i:j]
    out = {}
    nomi = {"Weekly": "weekly", "Biweekly": "biweekly", "Semimonthly": "semimonthly", "Monthly": "monthly"}
    for m in re.finditer(r"(Weekly|Biweekly|Semimonthly|Monthly) Payroll Period\s+(Single Person, Married Person, or Surviving Spouse|Head of Household)\s+"
                         r"1\.\s+Enter \w+ wages.*?2\.\s+\w+ portion of N\.C\. standard deduction\s+\$([\d,]+\.\d\d).*?"
                         r"3\.\s+Multiply the number of allowances by \$([\d,]+\.\d\d).*?Multiply Line 5 by (\.\d+)", pezzo, flags=re.S):
        per = nomi[m.group(1)]
        st = "single" if m.group(2).startswith("Single") else "hoh"
        out.setdefault(per, {})[st] = {"deduzione": soldi(m.group(3)), "esenzione": soldi(m.group(4))}
        if m.group(5) != ".0409":
            raise SystemExit("nc_30: aliquota di ritenuta diversa da .0409")
    if sorted(out) != sorted(nomi.values()) or any(sorted(v) != ["hoh", "single"] for v in out.values()):
        raise SystemExit(f"nc_30: tabelle delle formule lette male: {out}")
    return {"aliquota_ritenuta": 0.0409, "aliquota_imposta": 0.0399, "periodi": out}


# ---------------------------------------------------------------- regole
def regole(testi):
    def n(fid, pattern, tipo=float):
        return tipo(soldi(cerca(pattern, testi[fid], fid).group(1)))

    fed = tabelle_federali()
    m = cerca(r"enter \$([\d,]+) if the taxpayer is married filing jointly or \$([\d,]+) otherwise", testi["irs_p15t"], "irs_p15t")
    r = {
        "anno": ANNO,
        "periodi": {"weekly": 52, "biweekly": 26, "semimonthly": 24, "monthly": 12},
        "federale": {"fonte": "irs_p15t", "riga_1g": {"mfj": int(soldi(m.group(1))), "altro": int(soldi(m.group(2)))}, "tabelle": fed},
        "fica": {
            "fonte": "irs_p15",
            "ss": n("irs_p15", r"For 2026, the social security tax rate is ([\d.]+)%") / 100,
            "ss_base": n("irs_p15", r"The social security wage base limit is \$([\d,]+)\.", int),
            "medicare": n("irs_p15", r"The tax rate for Medicare is ([\d.]+)%") / 100,
            "addl": n("irs_p15", r"([\d.]+)% Additional Medicare Tax from wages you pay to an employee in excess of") / 100,
            "addl_soglia": n("irs_p15", r"Additional Medicare Tax from wages you pay to an employee in excess of \$([\d,]+) in a calendar year", int),
        },
        "futa": {
            "fonte": "irs_p15",
            "aliquota": n("irs_p15", r"For 2026, the FUTA tax rate is ([\d.]+)%") / 100,
            "base": n("irs_p15", r"The tax applies to the first \$([\d,]+) you pay to each employee as wages during the year", int),
            "credito_max": n("irs_p15", r"entitled to the maximum ([\d.]+)% credit") / 100,
            "netta": n("irs_p15", r"the FUTA tax rate after credit is ([\d.]+)%") / 100,
            "riduzione_credito": {},
        },
    }
    # riduzioni del credito FUTA 2026: foglio del Department of Labor (solo gli Stati con riduzione finale > 0)
    righe = T.xlsx_righe(GREZZI / "dol_final_credit_states_2026.xlsx")
    if righe[0][0] != "Final 2026 Federal Unemployment Tax Act (FUTA) Credit Reductions":
        raise SystemExit("dol_futa_2026: titolo del foglio cambiato")
    sigle = {"California": "CA", "Texas": "TX", "Florida": "FL", "Illinois": "IL", "North Carolina": "NC"}
    stati_foglio = []
    for riga in righe:
        if len(riga) == 7 and re.fullmatch(r"[\d.E-]+", riga[-1]):
            stati_foglio.append(riga[0])
            if float(riga[-1]) > 0 and riga[0] in sigle:
                r["futa"]["riduzione_credito"][sigle[riga[0]]] = round(float(riga[-1]), 4)
    r["futa"]["stati_nel_foglio"] = stati_foglio
    if r["futa"]["riduzione_credito"] != {"CA": 0.015}:
        raise SystemExit(f"dol_futa_2026: riduzioni lette {r['futa']['riduzione_credito']}, atteso solo CA 1.5% (rileggere il foglio e la frase citata)")

    ca = california()
    nc = north_carolina()
    r["stati"] = {
        "TX": {"nome": "Texas", "slug": "texas", "imposta_reddito": None,
               "suta": {"fonte": "tx_rates", "nome": "Unemployment Insurance (UI) tax", "nuovo": n("tx_rates", r"For 2026, the entry-level rate is ([\d.]+)%") / 100,
                        "base": n("tx_rates", r"is currently \$([\d,]+)\.", int),
                        "min": n("tx_your", r"The minimum tax rate for 2026 is ([\d.]+) percent") / 100, "max": n("tx_your", r"The maximum tax rate for 2026 is ([\d.]+) percent") / 100}},
        "FL": {"nome": "Florida", "slug": "florida", "imposta_reddito": None,
               "suta": {"fonte": "fl_rt", "nome": "Reemployment tax", "nuovo": n("fl_rt", r"The initial tax rate for new employers is \.0270 \(([\d.]+)%\)") / 100,
                        "base": n("fl_rt", r"Only the first \$([\d,]+) of wages paid to each employee", int)}},
        "CA": {"nome": "California", "slug": "california",
               "imposta_reddito": {"fonte": "ca_methb", "metodo": "ca_b", **ca},
               "sdi": {"fonte": "ca_rates", "aliquota": n("ca_rates", r"The SDI withholding rate for 2026 is ([\d.]+) percent") / 100,
                       "aliquota_2027": n("ca_rates", r"The SDI withholding rate for 2027 is ([\d.]+) percent") / 100},
               "suta": {"fonte": "ca_rates", "nome": "Unemployment Insurance (UI)", "nuovo": n("ca_rates", r"New employers are assigned a ([\d.]+) percent UI rate") / 100,
                        "base": n("ca_rates", r"The UI rate schedule for 2026 is Schedule F\+\..*?The taxable wage limit is \$([\d,]+) per employee, per calendar year", int),
                        "min": n("ca_rates", r"The UI rate schedule for 2026 is Schedule F\+\..*?UI contribution rates from ([\d.]+) percent to") / 100,
                        "max": n("ca_rates", r"The UI rate schedule for 2026 is Schedule F\+\..*?UI contribution rates from [\d.]+ percent to ([\d.]+) percent") / 100,
                        "ett": n("ca_rates", r"The ETT rate for 2026 is ([\d.]+) percent") / 100,
                        "ett_base": n("ca_rates", r"The ETT rate for 2026 is [\d.]+ percent\. The ETT taxable wage limit is \$([\d,]+)", int)}},
        "IL": {"nome": "Illinois", "slug": "illinois",
               "imposta_reddito": {"fonte": "il_700t", "metodo": "il", "aliquota": n("il_700t", r"Multiply the taxable amount by [\d.]+ percent \((\.\d+)\)"),
                                   "riga1": n("il_700t", r"Form IL-W-4, Line 1, by \$([\d,]+)\.", int), "riga2": n("il_700t", r"Form IL-W-4, Line 2, by \$([\d,]+)\.", int)},
               "suta": {"fonte": "il_ea50", "nome": "Unemployment Insurance contributions", "nuovo": n("il_ea50", r"will pay at the entry rate of ([\d.]+)%") / 100,
                        "base": n("il_ea50", r"Only the first \$([\d,]+) of wages paid to a worker in the calendar year 2026", int),
                        "fondo": n("il_ea50", r"includes the ([\d.]+)% Fund Building Rate in effect for 2026") / 100}},
        "NC": {"nome": "North Carolina", "slug": "north-carolina",
               "imposta_reddito": {"fonte": "nc_30", "metodo": "nc", **nc},
               "suta": {"fonte": "nc_des", "nome": "Unemployment Insurance tax", "nuovo": n("nc_des", r"UI Tax Rate for Beginning Employers ([\d.]+)%") / 100,
                        "base": n("nc_des", r"Taxable Wage Base for 2026 \$([\d,]+)", int),
                        "min": n("nc_des", r"could be as low as ([\d.]+)%") / 100, "max": n("nc_des", r"or as high as ([\d.]+)%") / 100}},
    }
    # l'aliquota NC scritta nel riquadro «New for 2026» deve essere quella delle formule
    if abs(n("nc_30", r"tax year 2026 will be ([\d.]+)%") / 100 - nc["aliquota_imposta"]) > 1e-9:
        raise SystemExit("nc_30: aliquota 2026 diversa da 3,99 %")
    for st in r["stati"].values():
        for k, v in st["suta"].items():
            if isinstance(v, float):
                st["suta"][k] = round(v, 6)
    for k in ("ss", "medicare", "addl"):
        r["fica"][k] = round(r["fica"][k], 6)
    for k in ("aliquota", "credito_max", "netta"):
        r["futa"][k] = round(r["futa"][k], 6)
    r["stati"]["CA"]["sdi"] = {k: (round(v, 6) if isinstance(v, float) else v) for k, v in r["stati"]["CA"]["sdi"].items()}
    return r


def main():
    locale = "--locale" in sys.argv
    GREZZI.mkdir(parents=True, exist_ok=True)
    vecchie = {}
    if (DATI / "fonti.json").exists():
        vecchie = json.loads((DATI / "fonti.json").read_text(encoding="utf-8"))["fonti"]
    oggi = date.today().isoformat()
    fonti, testi, errori, nuovi = {}, {}, [], []
    for fid, nome, url, titolo, chi, frasi in FONTI:
        dest = GREZZI / nome
        leggi = dest          # file da cui leggere: quello nuovo (.tmp) finché non si sa che tutto il giro è buono
        if locale:
            http, letto = vecchie.get(fid, {}).get("http", 200), vecchie.get(fid, {}).get("letto_il", oggi)
            if not dest.exists():
                raise SystemExit(f"{fid}: manca {dest}")
        else:
            tmp = dest.with_name(dest.name + ".tmp")
            http, letto = scarica(url, tmp), oggi
            if http != 200 or not tmp.exists() or tmp.stat().st_size < 1000:
                tmp.unlink(missing_ok=True)
                errori.append(f"{fid}: HTTP {http} da {url} (file precedente conservato)")
                continue
            leggi = tmp
            nuovi.append((tmp, dest))
        grezzo = leggi.read_bytes()
        testi[fid] = T.norm(T.testo(leggi) if leggi == dest else _testo_tmp(leggi, dest))
        trovate = {k: (T.norm(f) in testi[fid]) for k, f in frasi.items()}
        for k, ok in trovate.items():
            if not ok:
                errori.append(f"{fid}: frase «{k}» non trovata alla lettera")
        # Le pagine HTML cambiano byte a ogni scarico (parti dinamiche): per loro fa fede l'impronta delle frasi citate.
        fonti[fid] = {"url": url, "file": f"dati/grezzi/{nome}", "titolo": titolo, "chi": chi, "sha256": hashlib.sha256(grezzo).hexdigest(), "byte": len(grezzo),
                      "impronta": "frasi" if nome.endswith(".html") else "file", "sha256_frasi": T.impronta_frasi(testi[fid], frasi),
                      "http": http, "letto_il": letto, "frasi": frasi, "trovate": trovate}
    if errori:
        # Giro non buono: i file scaricati si buttano, così dati/grezzi resta uguale a ciò che fonti.json descrive.
        for tmp, _ in nuovi:
            tmp.unlink(missing_ok=True)
        print("\n".join(errori))
        raise SystemExit(f"{len(errori)} errori: fonti.json, regole.json e dati/grezzi NON aggiornati")
    precedenti = []
    for tmp, dest in nuovi:
        if dest.exists():
            prec = dest.with_name(dest.name + ".prec")
            dest.replace(prec)
            precedenti.append((prec, dest))
        tmp.replace(dest)
    try:
        reg = regole(testi)
    except SystemExit:
        # Una tabella o una cifra non si legge più: si torna ai file di prima (dati/grezzi = fonti.json) e i nuovi vanno in cache/ per guardarli.
        scarto = DATI.parent / "cache" / "fonti_non_lette"
        scarto.mkdir(parents=True, exist_ok=True)
        for _, dest in nuovi:
            dest.replace(scarto / dest.name)
        for prec, dest in precedenti:
            prec.replace(dest)
        print(f"Una regola non si legge più nei file nuovi: dati/grezzi è rimasto com'era, i file nuovi sono in {scarto}.")
        raise
    for prec, _ in precedenti:
        prec.unlink()
    for fid, f in fonti.items():
        v = vecchie.get(fid)
        if v and v.get("sha256") != f["sha256"]:
            stesso = f["impronta"] == "frasi" and v.get("sha256_frasi") == f["sha256_frasi"]
            print(f"{fid}: file cambiato dall'ultima lettura" + (" (solo parti dinamiche della pagina: le frasi citate sono le stesse)" if stesso else " (rileggere le cifre)"))
    reg["letto_il"] = max(f["letto_il"] for f in fonti.values())
    (DATI / "fonti.json").write_text(json.dumps({"_nota": "Generato da raccolta/fonti.py. File grezzi in dati/grezzi/. PDF e fogli di calcolo: fa fede sha256 (file intero). Pagine HTML (impronta = frasi): i byte cambiano a ogni scarico, fa fede sha256_frasi (le frasi citate alla lettera, ritrovate nel file).",
                                                 "fonti": fonti}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (DATI / "regole.json").write_text(json.dumps(reg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(fonti)} fonti, {sum(len(f['frasi']) for f in fonti.values())} frasi trovate alla lettera; regole.json scritto ({ANNO}).")


if __name__ == "__main__":
    main()
