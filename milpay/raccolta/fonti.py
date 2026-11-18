"""Rilegge le fonti ufficiali del sito e controlla le frasi esatte da cui vengono le cifre; scrive dati/fonti.json.

Uso (dalla radice del repository): python3 milpay/raccolta/fonti.py [--solo=id1,id2]
Per ogni fonte: HTTP, SHA-256 del file, data di lettura, esito di ogni frase cercata (spazi normalizzati).
Nessun blocco aggirato: dfas.mil, militarypay.defense.gov, defense.gov, congress.gov e bls.gov (sito) rispondono 403 al
nostro server e non sono usati; il BLS si legge dalla sua API pubblica.
"""
import gzip
import hashlib
import html
import json
import re
import subprocess
import tempfile
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
DATI = RADICE / "dati"
UA = {"User-Agent": "rete-siti-dati/1.0 (controllo delle fonti ufficiali)"}

P26 = json.loads((DATI / "paga_2026.json").read_text())["fonte"]
P25 = json.loads((DATI / "paga_2025.json").read_text())["fonte"]
ST = json.loads((DATI / "storico.json").read_text())

FONTI = {
    "eo2026": {"titolo": f"Executive Order {P26['ordine_esecutivo']}, Adjustments of Certain Rates of Pay, Schedule 8 (Pay of the Uniformed Services)",
               "chi": f"Federal Register, {P26['citazione']}, published {P26['pubblicato_il']}", "url": P26["url"], "leggi": P26["pdf"], "pdf": True,
               "cerca": ["Schedule 8 is effective January 1, 2026", "rates of monthly basic pay (37 U.S.C. 203(a)) for members of the uniformed services",
                         "level II of the Executive Schedule in effect during calendar year 2026, which is $18,899.90", "level V of the Executive Schedule in effect during calendar year 2026, which is $15,408.30",
                         "basic pay for this grade is $11,166.90 per month", "cadet or midshipman pay authorized by 37 U.S.C. 203(c) is $1,452.90",
                         "credited with over 4 years of active duty service as an enlisted member or warrant officer", "at least 1,460 points",
                         "served 4 months or more on active duty", "served less than 4 months on active duty", "Computed Under 37 U.S.C. 205"]},
    "eo2025": {"titolo": f"Executive Order {P25['ordine_esecutivo']}, Adjustments of Certain Rates of Pay, Schedule 8",
               "chi": f"Federal Register, {P25['citazione']}, published {P25['pubblicato_il']}", "url": P25["url"], "leggi": P25["pdf"], "pdf": True,
               "cerca": ["Schedule 8 is effective January 1, 2025", "2,108.10", "which is $18,808.20"]},
    "usc1009": {"titolo": "37 U.S.C. 1009, Adjustments of monthly basic pay", "chi": "United States Code, 2024 edition (govinfo.gov, U.S. Government Publishing Office)",
                "url": "https://www.govinfo.gov/content/pkg/USCODE-2024-title37/html/USCODE-2024-title37-chap19-sec1009.htm",
                "cerca": ["Effective on January 1 of each year, the rates of basic pay for members of the uniformed services",
                          "rounded to the nearest one-tenth of one percent", "the ECI for the base quarter of the year before the preceding year",
                          "Employment Cost Index (wages and salaries, private industry workers) published quarterly by the Bureau of Labor Statistics",
                          "the three-month period ending on September 30 of such year", "before September 1 of the preceding year a plan for such alternative pay adjustments",
                          "the basic allowance for subsistence", "the basic allowance for housing"]},
    "bls_eci": {"titolo": "Employment Cost Index: wages and salaries, private industry workers, 12-month percent change (series CIU2020000000000A)",
                "chi": "U.S. Bureau of Labor Statistics, public data API", "url": "https://api.bls.gov/publicAPI/v2/timeseries/data/CIU2020000000000A", "api_bls": True,
                "cerca": []},
    "budget2027": {"titolo": "Budget of the U.S. Government, Fiscal Year 2027, Appendix (Department of Defense, Military Personnel), PDF page 241",
                   "chi": "Office of Management and Budget, published on govinfo.gov", "url": "https://www.govinfo.gov/app/details/BUDGET-2027-APP",
                   "leggi": "https://www.govinfo.gov/content/pkg/BUDGET-2027-APP/pdf/BUDGET-2027-APP.pdf", "pdf": True,
                   "cerca": ["the Budget funds a military pay raise of 7 percent for all military personnel ranked E-5 and below, 6 percent for E-6 to O-3, and 5 percent for O-4 and above"]},
    "fr_search": {"titolo": "Federal Register search: presidential documents titled “Adjustments of Certain Rates of Pay”",
                  "chi": "Federal Register (National Archives), public API", "url": "https://www.federalregister.gov/documents/search?conditions%5Bterm%5D=%22Adjustments+of+Certain+Rates+of+Pay%22&conditions%5Btype%5D%5B%5D=PRESDOCU",
                  "leggi": "https://www.federalregister.gov/api/v1/documents.json?conditions%5Bterm%5D=%22Adjustments%20of%20Certain%20Rates%20of%20Pay%22&conditions%5Btype%5D%5B%5D=PRESDOCU&per_page=5&order=newest",
                  "cerca": ["2025-23844"]},
    # --- aggiunte della revisione indipendente del 13/11/2026
    "eo2026_s5": {"titolo": f"Executive Order {P26['ordine_esecutivo']}, Schedule 5 (Executive Schedule: level II $228,000, level V $184,900 a year)",
                  "chi": f"Federal Register, {P26['citazione']}, published {P26['pubblicato_il']}", "url": P26["url"], "leggi": P26["pdf"], "pdf": True, "layout": True,
                  "cerca": ["Schedule 5-Executive Schedule", "Level II 228,000", "Level V 184,900"]},
    "af_basicpay": {"titolo": "Basic Pay (2026 notes: limits for O-7 to O-10 and for O-6 and below)",
                    "chi": "Department of the Air Force, myairforcebenefits.us.af.mil",
                    "url": "https://myairforcebenefits.us.af.mil/Benefit-Library/Federal-Benefits/Basic-Pay?serv=23",
                    "cerca": ["Basic pay for an O-7 to O-10 is limited by Level II of the Executive Schedule during calendar year 2026 ($18,999.90)",
                              "Basic pay for O-6 and below is limited by Level V of the Executive Schedule in effect during calendar year 2026 ($15,408.30)"]},
    "usc203": {"titolo": "37 U.S.C. 203, Rates (limits on basic pay)", "chi": "United States Code, 2023 edition (govinfo.gov, U.S. Government Publishing Office)",
               "url": "https://www.govinfo.gov/content/pkg/USCODE-2023-title37/html/USCODE-2023-title37-chap3-sec203.htm",
               "cerca": ["may not exceed the monthly equivalent of the rate of pay for level II of the Executive Schedule",
                         "may not exceed the monthly equivalent of the rate of pay for level V of the Executive Schedule"]},
    "ndaa2025": {"titolo": "Public Law 118-159, section 601, Reform of basic pay rates (table effective April 1, 2025)",
                 "chi": "138 Stat. 1924, approved December 23, 2024 (govinfo.gov, U.S. Government Publishing Office)",
                 "url": "https://www.govinfo.gov/content/pkg/PLAW-118publ159/html/PLAW-118publ159.htm",
                 "cerca": ["Effective April 1, 2025, the rates of monthly basic pay for members of the uniformed services within each pay grade",
                           "Approved December 23, 2024"]},
    "hdoc189": {"titolo": "House Document 119-189, Alternative Plan for Pay Adjustments (letter of the President, August 26, 2026)",
                "chi": "119th Congress, 2d Session; referred August 27, 2026 (govinfo.gov, U.S. Government Publishing Office)",
                "url": "https://www.govinfo.gov/content/pkg/CDOC-119hdoc189/html/CDOC-119hdoc189.htm",
                "cerca": ["Washington, August 26, 2026",
                          "exercise my authority under section 1009(e) of title 37, United States Code, to set the 2027 monthly basic pay increase for members of the Armed Forces at 7.0 percent for grades E1 to E5, 6.0 percent for grades E6 to O3, and 5.0 percent for grades O4 and above, subject to the caps established by 37 U.S.C. 203",
                          "The adjustments described shall take effect on January 1, 2027",
                          "Uniformed service members who do not serve in the Armed Forces",
                          "monthly basic pay for these service members shall be increased by 3.6 percent, as determined pursuant to 37 U.S.C. 1009(c)"]},
    # elenco delle leggi pubblicate dal GPO (API govinfo, chiave dimostrativa pubblica): serve a dire, con una data, che NON c'è ancora
    # una legge di autorizzazione della difesa per l'anno fiscale 2027. Se compare, genera.py si ferma: la pagina 2027 va riscritta.
    "plaw119": {"titolo": "Public laws of the 119th Congress (list of published laws)", "chi": "govinfo.gov, U.S. Government Publishing Office",
                "url": "https://www.govinfo.gov/app/collection/plaw/119/public",
                "leggi": "https://api.govinfo.gov/collections/PLAW/2026-07-01T00:00:00Z?offsetMark=*&pageSize=1000&congress=119&api_key=DEMO_KEY",
                "api_plaw": True, "cerca": []},
}
# --- sezione per diem e chilometri (13/11/2026): file grezzi in dati/grezzi/ (raccolta/perdiem.py) e frasi esatte delle pagine GSA e IRS
_PD = json.loads((DATI / "perdiem.json").read_text()) if (DATI / "perdiem.json").exists() else None
FONTI.update({
    "gsa_xlsx2026": {"titolo": "FY 2026 per diem rates master file (Excel), effective October 1, 2025", "chi": "U.S. General Services Administration, Per diem files",
                     "url": "https://www.gsa.gov/travel/per-diem-rates/per-diem-files", "leggi": "https://www.gsa.gov/system/files/FY2026_PerDiemMasterRatesFile.xlsx", "binario": True, "cerca": []},
    "gsa_xlsx2027": {"titolo": "FY 2027 per diem rates file (Excel, FY2027_PerDiemRates_Validated090126.xlsx), effective October 1, 2026", "chi": "U.S. General Services Administration, Per diem files",
                     "url": "https://www.gsa.gov/travel/per-diem-rates/per-diem-files", "leggi": "https://www.gsa.gov/system/files/FY2027_PerDiemRates_Validated090126.xlsx", "binario": True, "cerca": []},
    "gsa_api": {"titolo": "Per diem API (lodging by month and M&IE breakdown, FY 2026 and FY 2027)", "chi": "U.S. General Services Administration, open.gsa.gov",
                "url": "https://open.gsa.gov/api/perdiem/",
                "cerca": ["The per diem reimbursement rates consist of a maximum lodging allowance component and a meals and incidental expenses (M&IE) component",
                          "Rates for the coming federal government fiscal year (October 1st to September 30th) are typically announced in mid-August"]},
    "gsa_pd": {"titolo": "Per diem rates", "chi": "U.S. General Services Administration, gsa.gov", "url": "https://www.gsa.gov/travel/per-diem-rates",
               "cerca": ["We establish the per diem rates that federal agencies use to reimburse their employees for lodging and meals and incidental expenses incurred while on official travel within the continental United States.",
                         "A standard rate applies to most of CONUS.", "Individual rates apply to about 300 non-standard areas.",
                         "Most NSAs are a key city/primary destination and the surrounding county."]},
    "gsa_faq": {"titolo": "Frequently asked questions, per diem", "chi": "U.S. General Services Administration, gsa.gov", "url": "https://www.gsa.gov/travel/per-diem-rates/faqs",
                "cerca": ["Per diem is an allowance for lodging, meals, and incidental expenses.",
                          "The U.S. General Services Administration (GSA) establishes the per diem reimbursement rates that federal agencies use to reimburse their employees for subsistence expenses incurred while on official travel within the continental U.S. (CONUS), which includes the 48 contiguous states and the District of Columbia.",
                          "The U.S. Department of Defense (DOD) establishes rates for travel in non-foreign areas outside of CONUS, which includes Alaska, Hawaii, and U.S. territories and possessions.",
                          "The U.S. Department of State establishes rates for travel in foreign areas.",
                          "If neither the city nor county you are looking for is listed on the GSA per diem rate page, then the standard CONUS rate applies.",
                          "If the city is not listed, but the county is, then the per diem rate is the rate for that entire county.",
                          "On the first and last travel day, Federal employees are only eligible for 75 percent of the total M&IE rate for their temporary duty travel location (not the official duty station location).",
                          "The lodging per diem rates are a maximum amount; the traveler only receives actual lodging costs up to that maximum rate.",
                          "Lodging taxes are not included in the CONUS per diem rate.",
                          "the meals and incidental expense (M&IE) rate does include taxes and tips in the rate",
                          "Hotels are not required to honor the federal per diem rates.",
                          "travelers are entitled to 75% of the prescribed meals and incidental expenses for one day travel away from your official station if it is longer than 12 hours",
                          "GSA establishes per diem rates and related policies for federal travelers on official travel only"]},
    "gsa_mie": {"titolo": "M&IE breakdowns", "chi": "U.S. General Services Administration, gsa.gov", "url": "https://www.gsa.gov/travel/per-diem-rates/mie-breakdowns",
                "cerca": ["Use the tables below to determine how much to deduct from your meals and incidental expenses allowance, or M&IE, when a meal is provided by the government or included in a registration fee.",
                          "Meals provided by a common carrier or complimentary meals provided by a hotel or motel do not affect your per diem allowance."]
                + ([f"${m['totale']} ${m['colazione']} ${m['pranzo']} ${m['cena']} ${m['extra']} ${m['primo_ultimo']:.2f}" for m in _PD["mie_tabella"]["2027"]] if _PD else [])},
    "gsa_mileage": {"titolo": "Mileage reimbursements (privately owned vehicle rates for official travel)", "chi": "U.S. General Services Administration, gsa.gov",
                    "url": "https://www.gsa.gov/travel/mileage-reimbursements",
                    "cerca": ["Current mileage rates for official travel on or after July 1, 2026", "For example, 100 miles in your own automobile at $0.76 per mile = $76.00.",
                              "Check with your agency's travel office before using a privately owned vehicle for official travel.",
                              "Jan. 1, 2026 $0.725 $0.205 $0.705 $1.78"]},
    "irs_n2026_10": {"titolo": "Notice 2026-10, 2026 Standard Mileage Rates", "chi": "Internal Revenue Service, irs.gov (PDF)", "url": "https://www.irs.gov/pub/irs-drop/n-26-10.pdf", "pdf": True,
                     "cerca": ["The standard mileage rate for transportation or travel expenses for 2026 is 72.5 cents per mile for all miles of business use",
                               "The standard mileage rate is 14 cents per mile for use of an automobile in rendering gratuitous services to a charitable organization",
                               "The standard mileage rate for 2026 is 20.5 cents per mile for use of an automobile: (1) for medical care"]},
    "irs_a2026_11": {"titolo": "Announcement 2026-11, Optional Standard Mileage Rates (Internal Revenue Bulletin 2026-29, July 13, 2026)", "chi": "Internal Revenue Service, irs.gov",
                     "url": "https://www.irs.gov/irb/2026-29_irb",
                     "cerca": ["This modification results from recent increases in the price of fuel.", "(1) Business 76 cents per mile", "(2) Medical and moving 23.5 cents per mile",
                               "The mileage rate that applies to the deduction for charitable contributions is fixed under § 170(i) of the Internal Revenue Code at 14 cents per mile.",
                               "on or after July 1, 2026"]},
    "irs_smr": {"titolo": "Standard mileage rates (all years)", "chi": "Internal Revenue Service, irs.gov", "url": "https://www.irs.gov/tax-professionals/standard-mileage-rates",
                "cerca": ["Self-employed and business: 76 cents/mile", "Charities: 14 cents/mile", "Medical: 23.5 cents/mile", "2026 (Jan. 1 - June 30) 72.5 14 20.5",
                         "2025 70 14 21 IR-2024-312", "2024 67 14 21 IR-2023-239", "2023 65.5 14 22 IR-2022-234"]},
    "irs_ir2025_128": {"titolo": "IR-2025-128, IRS sets 2026 business standard mileage rate at 72.5 cents per mile", "chi": "Internal Revenue Service newsroom, December 29, 2025",
                       "url": "https://www.irs.gov/newsroom/irs-sets-2026-business-standard-mileage-rate-at-725-cents-per-mile-up-25-cents",
                       "cerca": ["72.5 cents per mile driven for business use", "Use of the standard mileage rates is optional.",
                                 "Optional standard mileage rates are used to calculate the deductible costs of operating vehicles for business, charitable, and medical purposes.",
                                 "certain members of the intelligence community",
                                 "The rates apply to fully-electric and hybrid automobiles, as well as gasoline and diesel-powered vehicles."]},
})
# --- sezione "VA disability" (15/11/2026): tabelle di va.gov, avvisi del VA e della SSA nel Federal Register (testo GPO su govinfo), legge, regolamento.
# Le frasi di va_rates dicono anche QUALI tabelle sono in linea: quando va.gov passa alle tabelle dal 1/12/2026 le frasi non si trovano più e genera.py si ferma.
FONTI.update({
    "va_rates": {"titolo": "Current Veterans disability compensation rates (effective December 1, 2025)", "chi": "U.S. Department of Veterans Affairs, va.gov",
                 "url": "https://www.va.gov/disability/compensation-rates/veteran-rates/",
                 "cerca": ["Review 2026 Veterans disability compensation rates.", "Effective December 1, 2025",
                           "We base your monthly payment amount on your disability rating and details about your dependent family members.",
                           "If you have a 10% to 20% disability rating, you won't receive a higher rate even if you have a dependent spouse, child, or parent.",
                           "We're required by law to match the percentage of cost-of-living adjustments made to Social Security benefits.",
                           "These adjustments help to make sure that the purchasing power of your benefits keeps up with inflation.",
                           "If your spouse receives Aid and Attendance benefits or you have more than 1 child, you may qualify for additional monthly payment amounts as listed in the Added amounts table.",
                           "Since your basic rate already provides payment for 1 child, you would add the rate of $76.00 for each additional child",
                           "Find the dependent status in the left column that best describes you. Then look for your disability rating in the top row. Your basic monthly rate is where your dependent status and disability rating meet."]},
    "va_rates_2025": {"titolo": "Past rates: 2025 Veterans disability compensation rates (effective December 1, 2024)", "chi": "U.S. Department of Veterans Affairs, va.gov",
                      "url": "https://www.va.gov/disability/compensation-rates/veteran-rates/past-rates-2025/", "cerca": ["Effective December 1, 2024"]},
    "va_fr_2026": {"titolo": "Cost of Living Adjustments for Service-Connected Benefits (notice of the rates effective December 1, 2025)",
                   "chi": "Department of Veterans Affairs, Federal Register, 91 FR 7386, February 17, 2026 (document 2026-02997, text from govinfo.gov)",
                   "url": "https://www.govinfo.gov/content/pkg/FR-2026-02-17/html/2026-02997.htm",
                   "cerca": ["As required by the Veterans' Compensation Cost-of-Living Adjustment Act of 2025, Public Law 119-42, the VA is hereby giving notice of adjustments in certain benefit rates.",
                             "VA is required to increase these benefit rates by the same percentage as increases in the benefit amounts payable under title II of the Social Security Act.",
                             "The increased rates are required to be published in the Federal Register.",
                             "The Social Security Administration has announced that there will be a 2.8% cost-of-living increase in Social Security benefits for 2026.",
                             "the following rates for VA's compensation program became effective on December 1, 2025"]},
    "va_fr_2025": {"titolo": "Cost of Living Adjustments for Service-Connected Benefits (notice of the rates effective December 1, 2024)",
                   "chi": "Department of Veterans Affairs, Federal Register, July 18, 2025 (document 2025-13484, text from govinfo.gov)",
                   "url": "https://www.govinfo.gov/content/pkg/FR-2025-07-18/html/2025-13484.htm",
                   "cerca": ["2.5% cost-of-living increase in Social Security benefits for 2025"]},
    "ssa_cola_2027": {"titolo": "Cost-of-Living Increase and Other Determinations for 2027",
                      "chi": "Social Security Administration, Federal Register, 91 FR 67380, October 26, 2026 (document 2026-21796, text from govinfo.gov)",
                      "url": "https://www.govinfo.gov/content/pkg/FR-2026-10-26/html/2026-21796.htm",
                      "cerca": ["there will be a 3.6 percent cost-of-living increase in Social Security benefits effective December 2026"]},
    "hr8552": {"titolo": "H.R. 8552, Veterans' Compensation Cost-of-Living Adjustment Act of 2026, enrolled bill",
               "chi": "119th Congress, 2d Session (govinfo.gov, U.S. Government Publishing Office, issued November 13, 2026)",
               "url": "https://www.govinfo.gov/content/pkg/BILLS-119hr8552enr/html/BILLS-119hr8552enr.htm",
               "cerca": ["H.R. 8552 Enrolled Bill (ENR)", "Veterans' Compensation Cost-of-Living Adjustment Act of 2026",
                         "Effective on December 1, 2026, the Secretary of Veterans Affairs shall increase, in accordance with subsection (c), the dollar amounts in effect on November 30, 2026, for the payment of disability compensation and dependency and indemnity compensation",
                         "Each dollar amount described in subsection (b) shall be increased by the same percentage as the percentage by which benefit amounts payable under title II of the Social Security Act (42 U.S.C. 401 et seq.) are increased effective December 1, 2026",
                         "The Secretary of Veterans Affairs shall publish in the Federal Register the amounts specified in section 2(b), as increased under that section"]},
    "plaw119_42": {"titolo": "Public Law 119-42, Veterans' Compensation Cost-of-Living Adjustment Act of 2025", "chi": "139 Stat. 665, approved November 25, 2025 (govinfo.gov, U.S. Government Publishing Office)",
                   "url": "https://www.govinfo.gov/content/pkg/PLAW-119publ42/html/PLAW-119publ42.htm",
                   "cerca": ["Approved November 25, 2025", "Effective on December 1, 2025, the Secretary of Veterans Affairs shall increase"]},
    "usc1115": {"titolo": "38 U.S.C. 1115, Additional compensation for dependents", "chi": "United States Code, 2024 edition (govinfo.gov, U.S. Government Publishing Office)",
                "url": "https://www.govinfo.gov/content/pkg/USCODE-2024-title38/html/USCODE-2024-title38-partII-chap11-subchapII-sec1115.htm",
                "cerca": ["whose disability is rated not less than 30 percent, shall be entitled to additional compensation for dependents",
                          "in an amount having the same ratio to the amount specified in paragraph (1) of this section as the degree of disability bears to total disability",
                          "The amounts payable under this paragraph, if not a multiple of $1, shall be rounded down to the nearest dollar."]},
    "cfr4_25": {"titolo": "38 CFR 4.25, Combined ratings table (Table I)", "chi": "Code of Federal Regulations, eCFR in effect on October 1, 2026 (ecfr.gov, National Archives and GPO)",
                "url": "https://www.ecfr.gov/current/title-38/section-4.25", "leggi": "https://www.ecfr.gov/api/versioner/v1/full/2026-10-01/title-38.xml?part=4&section=4.25", "gzip": True,
                "cerca": ["the disabilities will first be arranged in the exact order of their severity, beginning with the greatest disability and then combined with use of table I",
                          "This combined value will then be converted to the nearest number divisible by 10, and combined values ending in 5 will be adjusted upward.",
                          "Thus, a person having a 60 percent disability is considered 40 percent efficient.",
                          "with a 50 percent disability and a 30 percent disability, the combined value will be found to be 65 percent, but the 65 percent must be converted to 70 percent to represent the final degree of disability",
                          "if there are three disabilities ratable at 60 percent, 40 percent, and 20 percent, respectively, the combined value for the first two will be found opposite 60 and under 40 and is 76 percent",
                          "The conversion to the nearest degree divisible by 10 will be done only once per rating decision",
                          "10 combined with 10 is 19"]},
    "cfr4_26": {"titolo": "38 CFR 4.26, Bilateral factor", "chi": "Code of Federal Regulations, eCFR in effect on October 1, 2026 (ecfr.gov, National Archives and GPO)",
                "url": "https://www.ecfr.gov/current/title-38/section-4.26", "leggi": "https://www.ecfr.gov/api/versioner/v1/full/2026-10-01/title-38.xml?part=4&section=4.26", "gzip": True,
                "cerca": ["the ratings for the disabilities of the right and left sides will be combined as usual, and 10 percent of this value will be added"]},
    "va_about": {"titolo": "About disability ratings (combined ratings table)", "chi": "U.S. Department of Veterans Affairs, va.gov", "url": "https://www.va.gov/disability/about-disability-ratings/",
                 "cerca": ["Calculating your combined disability rating involves more than adding up your individual ratings.",
                           "That's why your combined rating may be different from the sum of your individual ratings.",
                           "If you have 2 disabilities, each rated at 10% disabling, your combined disability rating is 19%."]},
    "fr_va_search": {"titolo": "Federal Register search: VA notices of cost-of-living adjustments for service-connected benefits", "chi": "Federal Register (National Archives), public API",
                     "url": "https://www.federalregister.gov/documents/search?conditions%5Bagencies%5D%5B%5D=veterans-affairs-department&conditions%5Bterm%5D=%22Cost+of+Living+Adjustments+for+Service-Connected+Benefits%22",
                     "leggi": ("https://www.federalregister.gov/api/v1/documents.json?conditions%5Bagencies%5D%5B%5D=veterans-affairs-department"
                               "&conditions%5Bterm%5D=%22Cost+of+Living+Adjustments+for+Service-Connected+Benefits%22&conditions%5Btype%5D%5B%5D=NOTICE&order=newest&per_page=5"),
                     "api_fr_va": True, "cerca": ["2026-02997"]},
})
for anno, f in ST["fonti_tabelle"].items():
    FONTI[f"eo{anno}"] = FONTI.get(f"eo{anno}") or {
        "titolo": f"Executive Order {f['ordine_esecutivo']}, Adjustments of Certain Rates of Pay, Schedule 8 (effective January 1, {anno})",
        "chi": f"Federal Register, {f['citazione']}", "url": f["url"], "leggi": f["pdf"], "pdf": True, "cerca": []}


def norm(t):
    t = t.replace("—", "-").replace("–", "-").replace("’", "'").replace("ﬁ", "fi").replace("ﬂ", "fl")
    t = re.sub(r"-\s*\n\s*", "-", t)
    return re.sub(r"\s+", " ", t)


def leggi(fid, f):
    url = f.get("leggi", f["url"])
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=dict(UA, **({"Accept-Encoding": "gzip"} if f.get("gzip") else {}))), timeout=180) as r:
            b, http = r.read(), r.status
            if r.headers.get("Content-Encoding") == "gzip":
                b = gzip.decompress(b)
    except urllib.error.HTTPError as e:
        return {"http": e.code, "letto_il": date.today().isoformat()}
    if f.get("binario"):
        testo = ""
    elif f.get("pdf"):
        with tempfile.NamedTemporaryFile(suffix=".pdf") as t:
            t.write(b)
            t.flush()
            testo = subprocess.run(["pdftotext"] + (["-layout"] if f.get("layout") else []) + [t.name, "-"], capture_output=True, text=True).stdout
    else:
        testo = b.decode("utf-8", "replace")
        testo = re.sub(r"<(script|style)\b.*?</\1>", " ", testo, flags=re.S | re.I)
        testo = html.unescape(re.sub(r"<[^>]+>", " ", testo)).replace("``", '"').replace("''", '"')
    es = {"http": http, "letto_il": date.today().isoformat(), "sha256": hashlib.sha256(b).hexdigest(), "byte": len(b)}
    if f.get("api_bls"):
        try:
            d = json.loads(b)
            es["api"] = d.get("status")
        except ValueError:
            es["api"] = "risposta non JSON"
    if f.get("api_plaw"):
        # leggi pubblicate dal 1° luglio 2026: numero più alto, data, ed eventuale legge di autorizzazione della difesa per il 2027
        try:
            pk = [p for p in json.loads(b).get("packages", []) if re.match(r"PLAW-119publ\d+$", p.get("packageId", ""))]
        except ValueError:
            pk = []
        if pk:
            ult = max(pk, key=lambda p: int(p["packageId"].split("publ")[1]))
            es["ultima_legge"] = {"numero": "119-" + ult["packageId"].split("publ")[1], "data": ult.get("dateIssued"), "titolo": ult.get("title")}
            es["leggi_lette"] = len(pk)
            es["ndaa_2027"] = [p["packageId"] for p in pk if re.search(r"National Defense Authorization Act for Fiscal Year 2027|Department of (Defense|War) Appropriations Act, 2027", p.get("title", ""))]
            # sezione VA: la legge che fa scattare l'aumento dal 1/12/2026 (finché non è tra le leggi pubblicate il sito lo dice)
            es["va_cola_2026"] = [p["packageId"] for p in pk if re.search(r"Veterans.{0,3} Compensation Cost-of-Living Adjustment Act of 2026", p.get("title", ""))]
        else:
            es["api"] = "elenco non letto"
    if f.get("api_fr_va"):
        # ultimo avviso del VA con gli importi di legge: se ne esce uno nuovo (quello delle tabelle dal 1/12/2026) genera.py si ferma
        try:
            es["avvisi"] = [{"numero": r_["document_number"], "data": r_["publication_date"]} for r_ in json.loads(b).get("results", [])]
        except ValueError:
            es["avvisi"] = []
    t = norm(testo)
    es["trovate"] = {c: norm(c) in t for c in f["cerca"]}
    return es


def main():
    import sys
    vecchio = json.loads((DATI / "fonti.json").read_text(encoding="utf-8")) if (DATI / "fonti.json").exists() else {}
    solo = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--solo=")), None)  # rilegge solo queste fonti, le altre restano
    esiti = dict(vecchio.get("fonti", {})) if solo else {}
    for fid, f in FONTI.items():
        if solo and fid not in solo:
            continue
        esiti[fid] = leggi(fid, f)
        e = esiti[fid]
        mancano = [c for c, ok in e.get("trovate", {}).items() if not ok]
        print(f"{fid}: HTTP {e['http']}" + (f" API {e['api']}" if "api" in e else "") + (f" MANCANO {mancano}" if mancano else ""))
    uscita = {"definizioni": FONTI, "fonti": esiti}
    if "grezzi" in vecchio:  # registro dei file grezzi scritto da raccolta/perdiem.py: si conserva
        uscita["grezzi"] = vecchio["grezzi"]
    (DATI / "fonti.json").write_text(json.dumps(uscita, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
