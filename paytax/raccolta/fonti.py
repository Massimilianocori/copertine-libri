"""Rilegge le fonti ufficiali del sito Payroll Tax by State e scrive paytax/dati/fonti.json.

Uso (dalla radice del repository):
    python3 paytax/raccolta/fonti.py            # rilegge tutte le fonti
    python3 paytax/raccolta/fonti.py nsw_rates  # solo alcune (per id)

Per ogni fonte: codice HTTP, data della lettura, impronta SHA-256 del testo (o dei byte per immagini e PDF), data
"Last updated" se la pagina la scrive, e l'esito di ogni frase cercata ("cerca"). Le frasi sono le cifre e le regole
che il sito pubblica: se una frase sparisce dalla pagina ufficiale, verifica.py dà errore e la cifra va ricontrollata.

Regola: nessun blocco aggirato. Le pagine che rispondono 403 (ATO, ACT Revenue Office, NT Treasury: Cloudflare) sono
segnate "non_letta" con il motivo e i loro dati vengono dal portale congiunto payrolltax.gov.au o dal testo di legge.
"""
import hashlib
import html
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
FILE = RADICE / "dati" / "fonti.json"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

# tipo: html (testo della pagina), pdf (pdftotext), csv/testo (testo grezzo), img (solo impronta dei byte)
# chi: chi pubblica la fonte (si mostra nell'elenco delle fonti)
FONTI = {
    # ---------------------------------------------------------------- portale congiunto degli uffici delle entrate
    "portal_rates": {
        "url": "https://www.payrolltax.gov.au/resources",
        "titolo": "Payroll tax rates and thresholds (all states and territories)", "chi": "Australian Revenue Offices (payrolltax.gov.au)",
        "cerca": ["Last updated on: 28/10/2026", "6.75% more than $1.75 million but not more than $20 million",
                  "8.75% more than $150 million", "Annual $1 750 000", "Monthly $145 833.33", "New South Wales 5.45% Annual $1 200 000",
                  "higher payroll tax rate of 6.5% for employers", "Annual $2 500 000 Monthly $208 333",
                  "4.75% $6 500 000 or less 4.95% more than $6 500 000", "1% discount on the rate until 30 June 2030",
                  "Annual $1 300 000 Monthly $108 333", "0% to 4.95% Exceeds $1 500 000 but not $1 700 000", "$600 000",
                  "4% $1 250 001 - $2 000 000 6.1% $2 000 001 or more", "4.85% 1.2125% for regional employers",
                  "Annual $1 000 000 Monthly $83 333", "Additional 0.25% (primary rate) more than $10 million (primary threshold)",
                  "+ 0.5% (additional rate) more than $100 million", "must be lodged by the 21st July each year, except in the ACT, New South Wales and South Australia, where it must be lodged by 28th July"]},
    "portal_lodging": {
        "url": "https://www.payrolltax.gov.au/lodging", "titolo": "Lodging payroll tax returns", "chi": "Australian Revenue Offices (payrolltax.gov.au)",
        "cerca": ["Monthly returns are due on the 7th of the following month", "only the DGE is entitled to the threshold/deduction"]},
    "portal_registration": {
        "url": "https://www.payrolltax.gov.au/registration", "titolo": "Registration", "chi": "Australian Revenue Offices (payrolltax.gov.au)",
        "cerca": ["you must register with each state and territory where you pay taxable wages",
                  "Employers who voluntarily declare their liabilities may receive significantly lower penalties than those who do not"]},
    # ---------------------------------------------------------------- New South Wales
    "nsw_rates": {
        "url": "https://www.revenue.nsw.gov.au/taxes-duties-levies-royalties/payroll-tax/lodge-and-pay-returns/thresholds-and-rates",
        "titolo": "Payroll tax thresholds and rates", "chi": "Revenue NSW",
        "cerca": ["Last updated: 01 July 2026", "1 July 2026 – 30 June 2027 $1,200,000 5.45%", "28 $92,055 30 $98,630 31 $101,918",
                  "$1,200,000 x (184 ÷ 365) = $604,931.51", "2025-26 threshold $360,000", "$400,000 x (184 ÷ 365) = $201,643.84",
                  "1 July 2022 – 30 June 2023 $1,200,000 5.45%"]},
    "nsw_interstate": {
        "url": "https://www.revenue.nsw.gov.au/taxes-duties-levies-royalties/payroll-tax/taxable-wages/interstate-wages",
        "titolo": "Payroll tax and interstate wages", "chi": "Revenue NSW",
        "cerca": ["$400,000 = ($1,000,000 ÷ $3,000,000) x $1,200,000", "Your annual tax-free threshold would currently be $960,000"]},
    "nsw_keydates": {
        "url": "https://www.revenue.nsw.gov.au/taxes-duties-levies-royalties/payroll-tax/lodge-and-pay-returns/key-dates",
        "titolo": "Key dates for payroll tax", "chi": "Revenue NSW",
        "cerca": ["July monthly return 7 August 2026", "December monthly return 14 January 2027", "2027 Annual return 28 July 2027"]},
    "nsw_register": {
        "url": "https://www.revenue.nsw.gov.au/taxes-duties-levies-royalties/payroll-tax/registration/register-for-payroll-tax",
        "titolo": "Register for payroll tax", "chi": "Revenue NSW",
        "cerca": ["register for payroll tax within 7 days after the month when your total Australian wages go above the monthly threshold"]},
    "nsw_grouping": {
        "url": "https://www.revenue.nsw.gov.au/taxes-duties-levies-royalties/payroll-tax/grouping",
        "titolo": "Payroll tax grouping", "chi": "Revenue NSW", "cerca": ["group"]},
    "nsw_calc": {
        "url": "https://apps09.revenue.nsw.gov.au/erevenue/calculators/payrolltax.php",
        "titolo": "Payroll tax calculator", "chi": "Revenue NSW", "cerca": []},
    # ---------------------------------------------------------------- Victoria
    "vic_rates": {
        "url": "https://www.sro.vic.gov.au/payroll-tax-current-rates", "titolo": "Payroll tax (current rates)", "chi": "State Revenue Office Victoria",
        "cerca": ["From 1 July 2025 onward $1,000,000 $83,333 4.85% 1.2125% for regional Victorian employers",
                  "From 1 July 2025 and each subsequent financial year it is 50%", "Businesses with a national payroll above $10 million will pay a combined 1%",
                  "Businesses with a national payroll above $100 million will pay a combined 2%", "Updated: 29 September 2026",
                  "between $3,000,000 and $5,000,000 are eligible for a reduced deduction"]},
    "vic_csv": {
        "url": "https://www.sro.vic.gov.au/sites/default/files/2026-07/ptx-rates-from-1-July-2025.csv", "tipo": "csv",
        "titolo": "Payroll tax rates from 1 July 2025 (CSV)", "chi": "State Revenue Office Victoria",
        "cerca": ['"$1,000,000","$83,333",4.85% and 1.2125% for regional Victorian employers']},
    "vic_phase": {
        "url": "https://www.sro.vic.gov.au/businesses-and-organisations/payroll-tax/thresholds-and-grouping/threshold-and-phase-out-rate",
        "titolo": "Threshold and phase-out rate", "chi": "State Revenue Office Victoria",
        "cerca": ["50% from the 2025-26 financial year onwards", "The employer is entitled to a payroll tax-free threshold of $360,000",
                  "The employer is entitled to a payroll tax-free threshold of $210,030", "Step 2: Multiply $3 million by the percentage of Victorian wages"]},
    "vic_regional": {
        "url": "https://www.sro.vic.gov.au/businesses-and-organisations/payroll-tax/industries-and-locations/regional-employers",
        "titolo": "Regional employers", "chi": "State Revenue Office Victoria",
        "cerca": ["the regional employer rate of payroll tax is 1.2125%", "you must pay at least 85% of your Victorian taxable wages to regional employees"]},
    "vic_surcharges": {
        "url": "https://www.sro.vic.gov.au/businesses-and-organisations/payroll-tax/thresholds-and-grouping/payroll-tax-surcharges",
        "titolo": "Payroll tax surcharges", "chi": "State Revenue Office Victoria",
        "cerca": ["Over $10 million 0.5% 0.5% 1%", "Over $100 million Additional 0.5% Additional 0.5% 2%", "$10,000,000 × 230 ÷ 365 = $6,301,370",
                  "= $5,333,333.33", "The surcharges only apply to Victorian taxable wages above the relevant thresholds"]},
    "vic_hist": {
        "url": "https://www.sro.vic.gov.au/about-us/rates-and-statistics/historical-rates/payroll-tax-historical-rates",
        "titolo": "Payroll tax (historical rates)", "chi": "State Revenue Office Victoria",
        "cerca": ["1 July 2024 to 30 June 2025 900,000 75,000 4.85 1.2125 (regional)", "1 July 2021 to 30 June 2024 700,000 58,333 4.85 1.2125 (regional)"]},
    "vic_act": {
        "url": "https://content.legislation.vic.gov.au/sites/default/files/2026-05/07-26aa041-authorised.pdf", "tipo": "pdf",
        "titolo": "Payroll Tax Act 2007 (Vic), authorised version 041, Schedule 1 cl 1, 1A, 5 and 7A", "chi": "Victorian Legislation",
        "cerca": ["APT or annual phase out threshold means, for the financial year commencing on 1 July 2024 and each subsequent financial year—$3 000 000",
                  "for the financial year commencing on 1 July 2025 and each subsequent financial year—50%", "where ND is the lesser of the following amounts",
                  "if the amount calculated in accordance with the formula in paragraph (a) of the definition of the variable ND is an amount that is less than zero, the amount is taken to be zero",
                  "the first surcharge threshold amount or STA1 for an employer or a group of employers is the amount calculated in accordance with the following formula— $10 million"]},
    "vic_grouping": {
        "url": "https://www.sro.vic.gov.au/businesses-and-organisations/payroll-tax/thresholds-and-grouping/grouping",
        "titolo": "Grouping", "chi": "State Revenue Office Victoria", "cerca": ["Businesses may be grouped for payroll tax if they share ownership, control or employees"]},
    "vic_monthly": {
        "url": "https://www.sro.vic.gov.au/businesses-and-organisations/payroll-tax/managing-your-payroll-tax/lodge-your-monthly-return",
        "titolo": "Lodge your monthly return", "chi": "State Revenue Office Victoria", "cerca": ["you must pay by the 7th of the next month"]},
    "vic_annual": {
        "url": "https://www.sro.vic.gov.au/businesses-and-organisations/payroll-tax/managing-your-payroll-tax/lodge-your-annual-reconciliation",
        "titolo": "Lodge your annual reconciliation", "chi": "State Revenue Office Victoria", "cerca": ["You must lodge and pay your annual return by 21 July"]},
    "vic_register": {
        "url": "https://www.sro.vic.gov.au/businesses-and-organisations/payroll-tax/managing-your-payroll-tax/register-payroll-tax",
        "titolo": "Register for payroll tax", "chi": "State Revenue Office Victoria", "cerca": ["You must register for payroll tax if you pay wages in Victoria"]},
    # ---------------------------------------------------------------- Queensland
    "qld_rates": {
        "url": "https://qro.qld.gov.au/payroll-tax/calculate/rates-thresholds/", "titolo": "Payroll tax rates and thresholds", "chi": "Queensland Revenue Office",
        "cerca": ["4.75% for employers or groups of employers who pay $6.5 million or less in Australian taxable wages",
                  "4.95% for employers or groups of employers who pay more than $6.5 million", "The current threshold is $1.3 million",
                  "the $1.3 million threshold is calculated proportionately on the number of days"]},
    "qld_deductions": {
        "url": "https://qro.qld.gov.au/payroll-tax/calculate/deductions/", "titolo": "Payroll tax deductions", "chi": "Queensland Revenue Office",
        "cerca": ["the deduction reduces by $1 for every $7 of taxable wages over this amount", "The deduction reduces to zero when your Australian taxable wages reach $10.4 million",
                  "yearly taxable wages from $1,300,000 to $10,400,000", "Queensland taxable wages $1,356,789 Australian taxable wages $1,789,776"]},
    "qld_deduction_example": {
        "url": "https://qro.qld.gov.au/files/AD-July-2023.png", "tipo": "img",
        "titolo": "Worked example image: annual deduction (Q $1,356,789 of A $1,789,776 → $932,460)", "chi": "Queensland Revenue Office", "cerca": []},
    "qld_regional": {
        "url": "https://qro.qld.gov.au/payroll-tax/calculate/regional-discount/", "titolo": "Payroll tax discount for regional businesses", "chi": "Queensland Revenue Office",
        "cerca": ["3.75% for employers or groups of employers who pay $6.5 million or less", "The discount does not apply for employers who pay more than $350 million",
                  "These rates apply from 1 July 2019 to 30 June 2030", "pay at least 85% of your Queensland taxable wages to regional employees"]},
    "qld_mhl": {
        "url": "https://qro.qld.gov.au/payroll-tax/mental-health-levy/calculating/", "titolo": "Calculating the mental health levy", "chi": "Queensland Revenue Office",
        "cerca": ["$255,000 + $60,000 = $315,000", "= $3,750 (annual mental health levy liability)", "= $48,750 (annual mental health levy liability)",
                  "The levy is then applied proportionately to Queensland taxable wages that exceed the thresholds"]},
    "qld_calcs": {
        "url": "https://qro.qld.gov.au/payroll-tax/calculate/calculators/", "titolo": "Payroll tax calculators", "chi": "Queensland Revenue Office",
        "cerca": ["(Total Queensland taxable wages – Deduction) × Payroll tax rate = Payroll tax liability"]},
    "qld_due": {
        "url": "https://qro.qld.gov.au/payroll-tax/returns/due-dates/", "titolo": "Payroll tax due dates", "chi": "Queensland Revenue Office",
        "cerca": ["7 August 2026 July 2026 monthly periodic", "14 January 2027 December 2026", "21 July 2027 2026–27 annual return"]},
    "qld_register": {
        "url": "https://qro.qld.gov.au/payroll-tax/register/", "titolo": "Register for payroll tax", "chi": "Queensland Revenue Office",
        "cerca": ["You must register within 7 days of the first month that your Australian wages (or your group’s Australian wages) exceed $25,000 a week"]},
    "qld_grouping": {
        "url": "https://qro.qld.gov.au/payroll-tax/liability/grouping/", "titolo": "Grouping", "chi": "Queensland Revenue Office", "cerca": ["group"]},
    "qld_amnesty": {
        "url": "https://qro.qld.gov.au/2026/11/payroll-tax-regional-discount-amnesty/", "titolo": "Payroll tax amnesty for regional employers", "chi": "Queensland Revenue Office",
        "cerca": ["The amnesty period will last up until 31 December 2026"]},
    "qld_hoola": {
        "url": "https://qro.qld.gov.au/2026/11/home-ownership-other-legislation-overview/", "titolo": "Home Ownership and Other Legislation Amendment Act 2026: overview", "chi": "Queensland Revenue Office",
        "cerca": ["The Home Ownership and Other Legislation Amendment Act 2026 received Royal Assent on 22 October 2026",
                  "Payroll Tax Act 1971 Confirms that the Commissioner of State Revenue may exclude a set of persons from a group"]},
    "qld_act": {
        "url": "https://www.legislation.qld.gov.au/view/whole/html/inforce/current/act-1971-037", "titolo": "Payroll Tax Act 1971 (Qld)", "chi": "Queensland Legislation",
        "cerca": ["K means 1,300,000", "(a) for an annual return period—$6,500,000", "(a) for an annual return period—$350,000,000"]},
    "qld_act_formula": {
        "url": "https://www.legislation.qld.gov.au/image/_1b934ee2-07b2-4998-ac61-dbd46abb5ebe.gif", "tipo": "img",
        "titolo": "Payroll Tax Act 1971 (Qld), s 29: annual deduction formula (image)", "chi": "Queensland Legislation", "cerca": []},
    # ---------------------------------------------------------------- Western Australia
    "wa_calc": {
        "url": "https://www.wa.gov.au/government/multi-step-guides/payroll-tax-employer-guide/calculation-payroll-tax-employer-guide",
        "titolo": "Calculation: Payroll Tax Employer Guide", "chi": "Department of Treasury and Finance (WA)",
        "cerca": ["The payroll tax rate is 5.5% on the taxable wages paid by employers or groups of employers", "This can be simplified to 2/13",
                  "$1,000,000 - [($1,200,000 - $1,000,000) X (2/13)] = $969,231", "Payroll tax of $6,600 will apply during this period", "Last updated: 2 June 2026",
                  "upper threshold of $7,500,000"]},
    "wa_interstate": {
        "url": "https://www.wa.gov.au/government/multi-step-guides/payroll-tax-employer-guide/calculation-payroll-tax-employer-guide/interstate-non-group-employer-payroll-tax",
        "titolo": "Interstate non-group employer: Payroll tax", "chi": "Department of Treasury and Finance (WA)",
        "cerca": ["$538,462 x 0.25 = $134,616", "$865,384 x 5.5% = $47,596.12"]},
    "wa_local": {
        "url": "https://www.wa.gov.au/government/multi-step-guides/payroll-tax-employer-guide/calculation-payroll-tax-employer-guide/local-non-group-employer-payroll-tax",
        "titolo": "Local non-group employer: Payroll tax", "chi": "Department of Treasury and Finance (WA)", "cerca": ["$230,769 x 5.5% = $12,692.30"]},
    "wa_returns": {
        "url": "https://www.wa.gov.au/government/multi-step-guides/payroll-tax-employer-guide/returns-payroll-tax-employer-guide",
        "titolo": "Returns: Payroll Tax Employer Guide", "chi": "Department of Treasury and Finance (WA)",
        "cerca": ["the monthly return for April must be lodged by 7 May", "Annual reconciliation returns, together with the June return, are due on or before 21 July"]},
    "wa_register": {
        "url": "https://www.wa.gov.au/government/multi-step-guides/payroll-tax-employer-guide/registration-payroll-tax-employer-guide",
        "titolo": "Registration: Payroll Tax Employer Guide", "chi": "Department of Treasury and Finance (WA)",
        "cerca": ["Register within seven days after the end of the month in which"]},
    "wa_grouping": {
        "url": "https://www.wa.gov.au/government/multi-step-guides/payroll-tax-employer-guide/grouping-payroll-tax-employer-guide",
        "titolo": "Grouping: Payroll Tax Employer Guide", "chi": "Department of Treasury and Finance (WA)", "cerca": ["group"]},
    "wa_act": {
        "url": "https://www.legislation.wa.gov.au/legislation/statutes.nsf/RedirectURL?OpenAgent&query=mrdoc_42096.pdf", "tipo": "pdf",
        "titolo": "Pay-roll Tax Assessment Act 2002 (WA), ss 8, 10, 13", "chi": "WA Legislation",
        "cerca": ["The annual threshold amount for a financial year beginning on or after 1 July 2020 is $1 000 000",
                  "The upper threshold amount for a financial year beginning on or after 1 July 2020 is $7 500 000",
                  "AAT is the apportioned annual threshold amount for the part-year"]},
    "wa_calculator": {
        "url": "https://apps.osr.wa.gov.au/portal/0/calculators/payrolltax", "titolo": "Payroll tax calculator", "chi": "RevenueWA", "cerca": []},
    # ---------------------------------------------------------------- South Australia
    "sa_rates": {
        "url": "https://www.revenuesa.sa.gov.au/payrolltax/rates-and-thresholds", "titolo": "Rates and thresholds", "chi": "RevenueSA",
        "cerca": ["from 1 January 2019 nil variable from 0% to 4.95% 4.95%", "from 1 January 2019 $1,500,000 per annum (equivalent to $28,846 per week or $125,000 per month)",
                  "from 1 July 2009 $600,000 $50,000"]},
    "sa_how": {
        "url": "https://www.revenuesa.sa.gov.au/payrolltax/how-is-payroll-tax-calculated", "titolo": "How is payroll tax calculated?", "chi": "RevenueSA",
        "cerca": ["X 365 = Annualised wages of $1,729,857", "the employer would be eligible to claim an annual deduction entitlement of $200,000 in South Australia"]},
    "sa_table": {
        "url": "https://www.revenuesa.sa.gov.au/__data/assets/pdf_file/0007/205459/PRT-Rate-Table.pdf", "tipo": "pdf",
        "titolo": "Payroll Tax Rate Table from 1 January 2019 (indicative)", "chi": "RevenueSA",
        "cerca": ["Payroll Tax Rate Table - from 1 January 2019", "Rates provided in this table are an indication only"]},
    "sa_act": {
        "url": "https://www.legislation.sa.gov.au/_legislation-documents/lz/c/a/payroll-tax-act-2009/current/2009.22.auth.pdf", "tipo": "pdf",
        "titolo": "Payroll Tax Act 2009 (SA), Schedule 1", "chi": "South Australian Legislation",
        "cerca": ["EA is $600 000", "TA or threshold amount is $1 500 000", "R is 4.95%", "more than $1 700 000, R is 4.95%"]},
    "sa_returns": {
        "url": "https://www.revenuesa.sa.gov.au/payrolltax/returns-and-annual-reconciliation", "titolo": "Returns and annual reconciliation", "chi": "RevenueSA",
        "cerca": ["The due date for completion and lodgement of the annual reconciliation return is 28 July", "Annual Reconciliation 2026-27 Wednesday 28 July 2027"]},
    "sa_register": {
        "url": "https://www.revenuesa.sa.gov.au/payrolltax/register-for-payroll-tax", "titolo": "Register for payroll tax", "chi": "RevenueSA",
        "cerca": ["the weekly payroll tax threshold is $28,846"]},
    "sa_grouping": {
        "url": "https://www.revenuesa.sa.gov.au/payrolltax/grouping-of-employers", "titolo": "Grouping of employers", "chi": "RevenueSA", "cerca": ["group"]},
    "sa_nexus": {
        "url": "https://www.revenuesa.sa.gov.au/payrolltax/nexus-provisions", "titolo": "Nexus provisions", "chi": "RevenueSA", "cerca": ["nexus"]},
    "sa_calculator": {
        "url": "https://www.revenuesaonline.sa.gov.au/external/prt/calculator.xhtml", "titolo": "Payroll tax calculator", "chi": "RevenueSA Online", "cerca": []},
    # ---------------------------------------------------------------- Tasmania
    "tas_rates": {
        "url": "https://www.sro.tas.gov.au/payroll-tax/rates-thresholds", "titolo": "Rates and thresholds", "chi": "State Revenue Office of Tasmania",
        "cerca": ["0 to 1 250 000 0 1 250 001 to 2 000 000 4 2 000 001 and above 6.1", "2026-27 financial year"]},
    "tas_guide": {
        "url": "https://www.sro.tas.gov.au/Documents/Annual-Adjustment-Return-Guideline.pdf", "tipo": "pdf",
        "titolo": "Annual Adjustment Return Guideline (worked examples)", "chi": "State Revenue Office of Tasmania",
        "cerca": ["$54 400", "$77 589", "$72 800", "$112 523", "$44 741", "$76 466", "$116 153"]},
    "tas_act": {
        "url": "https://www.legislation.tas.gov.au/view/whole/html/inforce/current/act-2008-016", "titolo": "Payroll Tax Act 2008 (Tas), Schedule 1", "chi": "Tasmanian Legislation",
        "cerca": ["R 1 is 4%", "R 2 is 6.1%", "TA or threshold amount is $1 250 000", "TTB or top tax bracket threshold is $2 000 000"]},
    "tas_act_formula": {
        "url": "https://www.legislation.tas.gov.au/image/taxma184s5.gif", "tipo": "img",
        "titolo": "Payroll Tax Act 2008 (Tas), sch 1 cl 4(5): formula above the subsequent threshold (image)", "chi": "Tasmanian Legislation", "cerca": []},
    "tas_lodge": {
        "url": "https://www.sro.tas.gov.au/payroll-tax/lodge-your-return", "titolo": "Lodge your return", "chi": "State Revenue Office of Tasmania",
        "cerca": ["Returns must be lodged by the 7th of the month following", "The AAR must be lodged by 21 July each year"]},
    "tas_register": {
        "url": "https://www.sro.tas.gov.au/payroll-tax/Registration", "titolo": "Registration", "chi": "State Revenue Office of Tasmania",
        "cerca": ["$24 038.00 per week during a month"]},
    "tas_grouping": {
        "url": "https://www.sro.tas.gov.au/payroll-tax/grouping-de-grouping", "titolo": "Grouping and de-grouping", "chi": "State Revenue Office of Tasmania", "cerca": ["group"]},
    "tas_calculator": {
        "url": "https://www.tro.tas.gov.au/Home/CalculatorPayrollTax", "titolo": "Payroll tax thresholds calculator", "chi": "Tasmanian Revenue Online", "cerca": []},
    # ---------------------------------------------------------------- Australian Capital Territory
    "act_det2026": {
        "url": "https://www.legislation.act.gov.au/DownloadFile/di/2026-151/current/PDF/2026-151.PDF", "tipo": "pdf",
        "titolo": "Taxation Administration (Amounts and Rates—Payroll Tax) Determination 2026 (DI2026-151)", "chi": "ACT Legislation Register",
        "cerca": ["The annual threshold amount for the purposes of schedule 1 of the Act is $1 750 000", "The monthly threshold amount for the purposes of section 86 of the Act is $145 833.33",
                  "more than $1.75 million but not more than $20 million 6.75 per cent", "more than $20 million but not more than $50 million 6.85 per cent",
                  "more than $50 million but not more than $100 million 7.35 per cent", "more than $100 million but not more than $150 million 7.85 per cent",
                  "more than $150 million 8.75 per cent", "capped at 6.85 per cent"]},
    "act_es2026": {
        "url": "https://www.legislation.act.gov.au/DownloadFile/es/db_74770/current/PDF/db_74770.PDF", "tipo": "pdf",
        "titolo": "Explanatory statement to the Payroll Tax Determination 2026", "chi": "ACT Legislation Register",
        "cerca": ["Payroll tax is collected monthly, but it is an annual tax based on Australia-wide wages",
                  "From 1 July 2026 the payroll tax surcharge, that applied for larger employers, has been incorporated into the general rate"]},
    "act_act": {
        "url": "https://www.legislation.act.gov.au/DownloadFile/a/2011-18/current/PDF/2011-18.PDF", "tipo": "pdf",
        "titolo": "Payroll Tax Act 2011 (ACT), Schedule 1 and s 9", "chi": "ACT Legislation Register",
        "cerca": ["TA (or threshold amount) means the amount determined under the Taxation Administration Act 1999, section 139 for this schedule",
                  "within 28 days after the end of June"]},
    "act_det2025": {
        "url": "https://www.legislation.act.gov.au/DownloadFile/di/2025-161/20250701-87703/PDF/2025-161.PDF", "tipo": "pdf",
        "titolo": "Payroll Tax Determination 2025 (DI2025-161), now revoked", "chi": "ACT Legislation Register",
        "cerca": ["The annual threshold amount for the purposes of schedule 1 of the Act is $2 000 000", "more than $100 million 6.85 per cent 1.00 per cent"]},
    "act_det2024": {
        "url": "https://www.legislation.act.gov.au/DownloadFile/di/2024-173/20240701-84146/PDF/2024-173.PDF", "tipo": "pdf",
        "titolo": "Payroll Tax Determination 2024 (DI2024-173), now revoked", "chi": "ACT Legislation Register",
        "cerca": ["more than $100 million 6.85 per cent 0.50 per cent"]},
    "act_det2016": {
        "url": "https://www.legislation.act.gov.au/DownloadFile/di/2016-145/20160701-63940/PDF/2016-145.PDF", "tipo": "pdf",
        "titolo": "Payroll Tax Determination 2016 (No 1) (DI2016-145), now revoked", "chi": "ACT Legislation Register",
        "cerca": ["is $2 000 000", "6.85%"]},
    "act_revenue": {
        "url": "https://www.revenue.act.gov.au/payroll-tax", "titolo": "Payroll tax", "chi": "ACT Revenue Office", "cerca": [],
        "non_letta": True, "motivo": "answers 403 (Cloudflare check) to our server; figures taken from the joint portal and the ACT legislation register"},
    # ---------------------------------------------------------------- Northern Territory
    "nt_act": {
        "url": "https://legislation.nt.gov.au/api/sitecore/Act/PDF?id=12078", "tipo": "pdf",
        "titolo": "Payroll Tax Act 2009 (NT), as in force at 1 July 2026", "chi": "Northern Territory Legislation",
        "cerca": ["As in force at 1 July 2026", "the rate of payroll tax is 5.5%", "is 6.5% if either", "the threshold amount is $100 000 000",
                  "TA or threshold amount means $2 500 000", "AD or annual deduction means", "within 21 days after the end of the month",
                  "within 21 days after the end of each month (except June)"]},
    "nt_treasury": {
        "url": "https://treasury.nt.gov.au/dtf/territory-revenue-office/payroll-tax", "titolo": "Payroll tax", "chi": "Territory Revenue Office (NT)", "cerca": [],
        "non_letta": True, "motivo": "answers 403 (Cloudflare check) to our server; figures taken from the joint portal and the Payroll Tax Act 2009"},
    # ---------------------------------------------------------------- Payday Super (Commonwealth)
    "payday_act": {
        "url": "https://www.legislation.gov.au/C2025A00057/asmade/2025-11-06/text/1/epub/OEBPS/document_1/document_1.html",
        "titolo": "Treasury Laws Amendment (Payday Superannuation) Act 2025 (No. 57, 2025)", "chi": "Federal Register of Legislation",
        "cerca": ["[ Assented to 6 November 2025 ]", "1 July 2026", "ending on the seventh business day after the QE day",
                  "ending on the 20th business day after the QE day", "charge percentage means 12", "definition of quarterly salary or wages base", "Omit “a quarter that ended”, substitute “a QE day”",
                  "The employer’s administrative uplift amount for the QE day is equal to 60%", "definition of approved clearing house",
                  "period ending on the day before the current QE day", "general interest charge rate has the same meaning as in section 8AAD of the Taxation Administration Act 1953",
                  "Lodging a statement in the approved form can reduce the employer’s administrative uplift amount",
                  "a day which is a public holiday for the whole of: (i) any State; or (ii) the Australian Capital Territory; or (iii) the Northern Territory"]},
    "ato_payday": {
        "url": "https://www.ato.gov.au/businesses-and-organisations/super-for-employers/payday-super", "titolo": "Payday Super", "chi": "Australian Taxation Office", "cerca": [],
        "non_letta": True, "motivo": "answers 403 to our server; what we write comes from the Act itself"},
}

RE_AGG = re.compile(r"(Last updated(?: on)?:?\s*[0-9]{1,2}[ /][A-Za-z0-9]+[ /][0-9]{4}|Updated:\s*[0-9]{1,2} [A-Za-z]+ [0-9]{4}|Last published on:\s*[0-9/]+)")


def normalizza(t):
    t = html.unescape(t).replace(" ", " ").replace("​", "").replace("‑", "-")
    return re.sub(r"\s+", " ", t).strip()


def testo_html(b):
    t = b.decode("utf-8", errors="replace")
    t = re.sub(r"<(script|style|noscript)\b.*?</\1>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return normalizza(t)


def testo_pdf(b):
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(b)
        f.flush()
        r = subprocess.run(["pdftotext", "-raw", f.name, "-"], capture_output=True, text=True)
    return normalizza(r.stdout)


def leggi(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-AU,en;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read() if hasattr(e, "read") else b""
    except Exception as e:  # noqa: BLE001
        return 0, str(e).encode()


def testo_di(f, corpo):
    tipo = f.get("tipo", "html")
    if tipo == "pdf" or corpo[:5] == b"%PDF-":
        return testo_pdf(corpo)
    if tipo in ("csv", "testo"):
        return normalizza(corpo.decode("utf-8", errors="replace"))
    if tipo == "img":
        return ""
    return testo_html(corpo)


def controlla(fid, f):
    codice, corpo = leggi(f["url"])
    es = {"http": codice, "letto_il": date.today().isoformat()}
    if f.get("non_letta"):
        es["motivo"] = f["motivo"]
        return es
    if codice != 200:
        es["motivo"] = f"HTTP {codice}"
        return es
    t = testo_di(f, corpo)
    es["sha256"] = hashlib.sha256(t.encode("utf-8") if t else corpo).hexdigest()
    es["byte"] = len(corpo)
    m = RE_AGG.search(t) if t else None
    if m:
        es["aggiornata"] = m.group(1)
    es["trovate"] = {c: normalizza(c) in t for c in f.get("cerca", [])}
    return es


def main(ids):
    vecchio = json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else {"fonti": {}}
    esiti = vecchio.get("fonti", {})
    for fid, f in FONTI.items():
        if ids and fid not in ids:
            continue
        es = controlla(fid, f)
        esiti[fid] = es
        mancano = [c for c, ok in es.get("trovate", {}).items() if not ok]
        print(f"{fid:24} {es['http']} {es.get('aggiornata', '')} {'MANCANO: ' + str(mancano) if mancano else ''}")
        time.sleep(0.4)
    esiti = {k: v for k, v in esiti.items() if k in FONTI}
    out = {"_nota": "scritto da raccolta/fonti.py: non modificare a mano", "definizioni": FONTI, "fonti": esiti}
    FILE.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
