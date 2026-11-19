"""Scarica i file ufficiali e rilegge le pagine delle regole per Heat Pump Grants UK.

Uso (dalla radice del repository):
    python3 heatpumps/raccolta/fonti.py     # file grezzi in heatpumps/raccolta/_grezzi/ (fuori da git) + heatpumps/dati/fonti.json

Cosa fa:
1. Cerca con l'API dei contenuti di GOV.UK (www.gov.uk/api/content/...) l'ultima versione di ogni file statistico:
   Boiler Upgrade Scheme statistics (mensile), Renewable electricity by local authority (annuale), Solar PV cost data TIC
   (annuale), Solar photovoltaics deployment ET 6.3 (mensile). I nomi dei file cambiano a ogni uscita: l'indirizzo si legge
   sempre dall'API, mai a mano.
2. Scarica i quattro xlsx in raccolta/_grezzi/ con un nome fisso e ne calcola l'impronta SHA-256.
3. Rilegge le pagine delle regole (GOV.UK "Apply for the Boiler Upgrade Scheme" via API, due pagine Ofgem) e controlla che le
   frasi esatte usate nel sito ci siano ancora (campo "cerca" di DEFINIZIONI).
Scrive dati/fonti.json: definizioni + esito di ogni lettura (HTTP, data, impronta, frasi trovate). Nessun dato personale:
le richieste non portano nulla di nostro. Nessun blocco anti-robot viene aggirato.
"""
import hashlib
import html
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
GREZZI = Path(__file__).resolve().parent / "_grezzi"
FILE = RADICE / "dati" / "fonti.json"
UA = {"User-Agent": "Mozilla/5.0 (compatible; heatpumps-check/1.0)"}
API = "https://www.gov.uk/api/content/"

# File statistici: pagina GOV.UK da cui si legge l'indirizzo e regola per scegliere l'allegato
FILE_STAT = {
    "bus_xlsx": {"pagina": "government/collections/boiler-upgrade-scheme-statistics", "collezione": True,
                 "allegato": r"^Boiler Upgrade Scheme Statistics: .* \(Excel\)$", "nome": "bus.xlsx",
                 "titolo": "Boiler Upgrade Scheme statistics (Excel workbook)", "chi": "Department for Energy Security and Net Zero (DESNZ), data from Ofgem"},
    "solare_la_xlsx": {"pagina": "government/statistics/regional-renewable-statistics", "allegato": r"^Renewable electricity by local authority",
                       "nome": "solare_la.xlsx", "titolo": "Renewable electricity by local authority (Excel workbook)", "chi": "DESNZ, Energy Trends"},
    "solare_costi_xlsx": {"pagina": "government/statistics/solar-pv-cost-data", "allegato": r"TIC basis \(Excel\)$", "nome": "solare_costi_tic.xlsx",
                          "titolo": "Solar PV cost data, Total Installed Capacity basis (Excel workbook)", "chi": "DESNZ, data from the Microgeneration Certification Scheme (MCS)"},
    "solare_et63_xlsx": {"pagina": "government/statistics/energy-trends-section-6-renewables", "allegato": r"^Solar photovoltaics deployment \(Excel\)",
                         "nome": "solare_et63.xlsx", "titolo": "Solar photovoltaics deployment, Energy Trends table 6.3 (Excel workbook)", "chi": "DESNZ, Energy Trends"},
    # 13/11/2026: schemi per le pagine ECO4, Great British Insulation Scheme e Warm Homes: Local Grant
    "gbis_xlsx": {"pagina": "government/collections/great-british-insulation-scheme", "collezione": True, "filtro": "great-british-insulation-scheme-release-",
                  "allegato": r"^Great British Insulation Scheme statistics: .* \(Excel\)$", "nome": "gbis.xlsx",
                  "titolo": "Great British Insulation Scheme statistics (Excel workbook)", "chi": "DESNZ, data from Ofgem"},
    "whlg_xlsx": {"pagina": "government/collections/warm-homes-local-grant-statistics", "collezione": True, "filtro": "warm-homes-local-grant-statistics-",
                  "allegato": r"^Warm Homes: Local Grant statistics data tables - [A-Za-z]+ \d{4}$", "nome": "whlg.xlsx",
                  "titolo": "Warm Homes: Local Grant statistics (Excel workbook)", "chi": "DESNZ, data reported by the councils that run the grant"},
    "hee_xlsx": {"pagina": "government/collections/household-energy-efficiency-national-statistics", "collezione": True,
                 "filtro": "household-energy-efficiency-statistics-headline-release-", "allegato": r"^Headline HEE release tables, .* \(Excel\)$",
                 "nome": "hee.xlsx", "titolo": "Household Energy Efficiency statistics, headline tables (Excel workbook)", "chi": "DESNZ, data from Ofgem"},
}

# Pagine delle regole: frasi esatte (dopo aver tolto i tag e normalizzato spazi e apostrofi)
PAGINE = {
    "gov_apply": {"url": "https://www.gov.uk/apply-boiler-upgrade-scheme", "api": "apply-boiler-upgrade-scheme",
                  "titolo": "Apply for the Boiler Upgrade Scheme", "chi": "GOV.UK",
                  "cerca": ["This scheme is open to people in England and Wales.",
                            "The Boiler Replacement Scheme in Northern Ireland is now closed.",
                            "If you live in Scotland",
                            "New build properties which the developer is still building are not eligible.",
                            "you or the original owner built it yourself or you paid a builder to build it",
                            "If you move into a finished new build with a fossil fuel boiler, you may be able to get a grant for a heat pump under the scheme.",
                            "your property is off the gas grid",
                            "your property is in a rural location",
                            "You can get one grant per property.",
                            "£7,500 towards an air source heat pump (sometimes called an air-to-water heat pump)",
                            "£7,500 towards a ground source heat pump (including water source heat pumps and those on shared ground loops)",
                            "£5,000 towards a biomass boiler",
                            "£2,500 towards an air-to-air heat pump",
                            "Until March 2027, you can get an additional £1,500 towards an air source heat pump or ground source heat pump if both:",
                            "your property is heated by oil or LPG",
                            "you do not have a mains gas connection at the property",
                            "You cannot get a grant for a hybrid heat pump system",
                            "45kWth for individual systems",
                            "You cannot get a grant to replace a low carbon heating system.",
                            "own the property you're applying for (including if it's a business, a second home, or a property you rent out to tenants)",
                            "be replacing fossil fuel heating systems - such as oil, gas, electric or LPG (liquefied petroleum gas)",
                            "You're still eligible if you've already had funding to make your property more energy efficient, for example by insulating it.",
                            "Your installer must commission and install the heat pump within 120 days of applying for the grant",
                            "most new build properties",
                            "social housing",
                            "a property that's already been given government funding or support for a heat pump or biomass boiler",
                            "it's never been owned by a business or organisation",
                            "Contact suitable MCS certified installers to get quotes for the work.",
                            "The installer will apply on your behalf on the Ofgem website.",
                            "The value of the grant will be taken off the amount you pay for installation."]},
    "ofgem_bus": {"url": "https://www.ofgem.gov.uk/environmental-and-social-schemes/boiler-upgrade-scheme-bus",
                  "titolo": "Boiler Upgrade Scheme (BUS): about the scheme", "chi": "Ofgem",
                  "cerca": ["This scheme is open in England and Wales.",
                            "£9,000 off the cost and installation of air-to-water or ground source heat pumps in eligible off-gas grid properties. This is available until 31 March 2027.",
                            "£7,500 off the cost and installation of air-to-water heat pumps, ground source heat pumps and water source heat pumps",
                            "£5,000 off the cost and installation of biomass boilers",
                            "£2,500 off the cost and installation of air-to-air heat pumps for residential properties only",
                            "The scheme is installer-led."]},
    "ofgem_owners": {"url": "https://www.ofgem.gov.uk/environmental-and-social-schemes/boiler-upgrade-scheme-bus/property-owners",
                     "titolo": "Boiler Upgrade Scheme: property owners", "chi": "Ofgem",
                     "cerca": ["(available from 21 July 2026 until 31 March 2027)",
                               "From 1 April 2022 to 31 March 2027, there is 0% VAT on the installation of energy-saving materials including heat pumps and biomass boilers.",
                               "The value of the grant for your chosen technology should be provided to you as an upfront discount on the quote provided to you by your installer.",
                               "As with all home improvements we recommend that you obtain quotes from multiple installers.",
                               "If we do not receive your confirmations of the above within 14 calendar days, we may reject the application.",
                               "your installer has three months from the moment the application is approved to complete the installation",
                               "(six months for ground source heat pumps)",
                               "The scheme is open to residential and non-residential properties in England and Wales.",
                               "non-residential buildings (where installing an air-to-air heat pump)",
                               "Hybrid heat pump systems, for example a combination of a fossil fuel boiler and an air source heat pump, are not eligible.",
                               "replace an existing fossil fuel or electric heating system",
                               "not replace an existing low-carbon heating system",
                               "can only be installed in rural properties",
                               "provided at lower than market value to people that could not have afforded it otherwise (including arrangements like shared ownership)",
                               "If your property has an Energy Performance Certificate (EPC), this will include a 'changes you could make' section",
                               "can only be installed in properties with no connection to the gas grid"]},
    # 13/11/2026: pagine nuove (ECO4, Great British Insulation Scheme, Warm Homes: Local Grant, contributi per il solare, Scozia, Galles, Irlanda del Nord)
    "gov_eco": {"url": "https://www.gov.uk/energy-company-obligation", "api": "energy-company-obligation", "titolo": 'Help from your energy supplier: the Energy Company Obligation', "chi": 'GOV.UK',
        "cerca": ['You might be able to get help for energy-saving improvements to your home if you either:',
                  'claim certain benefits and live in private housing (for example you own your home or rent from a private landlord)',
                  'insulation work, for example to your loft or cavity walls',
                  'replacing or repairing your boiler - or other upgrades to your heating',
                  'Universal Credit',
                  'Pension Guarantee Credit',
                  'Pension Savings Credit',
                  'Income Support',
                  "income-based Jobseeker's Allowance",
                  'income-related Employment and Support Allowance',
                  'Child Benefit',
                  'Housing Benefit',
                  'If you own your house, it must have an energy efficiency rating of D, E, F or G to be eligible.',
                  'If you rent from a private landlord, the house must have an energy efficiency rating of E, F or G to be eligible.',
                  "You must have the owner's permission to do the work.",
                  'If you live in social housing that has an energy efficiency rating of E, F or G you might be eligible for help with insulation or installing a heating system for the first time.',
                  'The Energy Company Obligation scheme is closing on 31 December 2026.',
                  "Contact your local council to find out if they're taking part in the Energy Company Obligation scheme, or contact an energy supplier directly.",
                  'Installers or agents might contact you directly.',
                  "If you're not sure if an offer is genuine, contact your local council or the energy supplier they represent to check.",
                  'There are quality issues with some solid wall insulation fitted through the Energy Company Obligation scheme.']},
    "ofgem_eco": {"url": "https://www.ofgem.gov.uk/environmental-and-social-schemes/energy-company-obligation-eco", "titolo": 'Energy Company Obligation (ECO)', "chi": 'Ofgem',
        "cerca": ['The Energy Company Obligation (ECO) is a government energy efficiency scheme in Great Britain designed to tackle fuel poverty and help reduce carbon emissions.',
                  'ECO4 applies to measures installed from 1 April 2022 and will run until 31 December 2026, following a nine-month extension.',
                  'The ECO scheme works by placing a Home Heating Cost Reduction Obligation (HHCRO) on medium and large energy suppliers.',
                  'Under HHCRO, obligated suppliers must promote measures that improve the ability of low-income, fuel-poor and vulnerable households to heat their homes.',
                  'We administer ECO4 on behalf of DESNZ.']},
    "gov_gbis": {"url": "https://www.gov.uk/apply-great-british-insulation-scheme", "api": "apply-great-british-insulation-scheme", "titolo": 'The Great British Insulation Scheme', "chi": 'GOV.UK',
        "cerca": ["The Great British Insulation Scheme helps people get free or cheaper insulation to reduce their home's energy bills.",
                  'Installations must be complete by 31 March 2026, when the scheme ends.',
                  'There are quality issues with some solid wall insulation fitted through the Great British Insulation Scheme.']},
    "ofgem_gbis": {"url": "https://www.ofgem.gov.uk/environmental-and-social-schemes/great-british-insulation-scheme", "titolo": 'Great British Insulation Scheme', "chi": 'Ofgem',
        "cerca": ['This scheme is now closed to new installations.',
                  'The Great British Insulation Scheme delivered improvements to the least energy-efficient homes in Great Britain to tackle fuel poverty and help reduce energy bills.',
                  "The scheme complements the Energy Company Obligation (ECO4) scheme, yet unlike ECO4's 'whole house' approach, this scheme will mostly deliver single insulation measures.",
                  'As well as supporting low-income and vulnerable households, it was also available to those living in homes with an Energy Performance Certificate rating of D-G, and within Council Tax bands A-D in England and A-E in Scotland and Wales.',
                  'The scheme began in April 2023 and ended on 31 March 2026.']},
    "gov_whlg": {"url": "https://www.gov.uk/apply-warm-homes-local-grant", "api": "apply-warm-homes-local-grant", "titolo": 'Apply for the Warm Homes: Local Grant to improve a home', "chi": 'GOV.UK',
        "cerca": ["You could get free energy saving improvements made to your home if you're on a low income, getting certain benefits or living in a certain postcode area.",
                  'The Warm Homes: Local Grant is only available in England.',
                  'wall, loft and underfloor insulation',
                  'air source heat pumps',
                  'smart controls',
                  'solar panels',
                  "Your local council will then organise and pay for any improvement work they've agreed with you.",
                  'You will not need to pay for it.',
                  'If you have a landlord, they may need to pay for some of the improvements.',
                  'be privately owned (either by you or your landlord)',
                  'have an Energy Performance Certificate (EPC) of D, E, F or G',
                  'Your household income must usually be £36,000 a year or less.',
                  'you live in a certain postcode area',
                  'someone in your household is getting certain benefits',
                  'Your local council will usually contact you within 10 working days to get more information and arrange a home survey.']},
    "hmrc_vat": {"url": "https://www.gov.uk/guidance/vat-on-energy-saving-materials-and-heating-equipment-notice-7086", "api": "guidance/vat-on-energy-saving-materials-and-heating-equipment-notice-7086", "titolo": 'Energy-saving materials and heating equipment (VAT Notice 708/6)', "chi": 'HM Revenue & Customs, GOV.UK',
        "cerca": ['A zero rate applies to the installation of certain specified energy-saving materials from 1 May 2023 to 31 March 2027.',
                  'solar panels (read section 2.11)',
                  'batteries for storing energy converted from electricity',
                  'From 1 April 2027 onwards, supplies of installations of energy-saving materials will revert to the reduced rate of VAT of 5%.',
                  'Energy-saving materials, when installed in residential accommodation']},
    "ofgem_seg": {"url": "https://www.ofgem.gov.uk/environmental-and-social-schemes/smart-export-guarantee-seg", "titolo": 'Smart Export Guarantee (SEG)', "chi": 'Ofgem',
        "cerca": ['The SEG launched on 1 January 2020 and is a government-backed initiative.',
                  'The SEG requires some electricity suppliers, known as SEG Licensees, to pay small-scale generators, known as SEG Generators, for low-carbon electricity which they export back to the National Grid, providing certain criteria are met.',
                  'SEG Licensees determine the rate, contract length and other terms which SEG Generators will receive.',
                  'SEG tariff rates must always be above zero.',
                  'SEG payments are calculated by using export meter readings.',
                  'Installations must be located in Great Britain and meet the applicable eligibility criteria.',
                  'Generators thinking of applying for a SEG tariff should shop around to see which tariff is best for their individual circumstances.']},
    "hes_grant": {"url": "https://www.homeenergyscotland.org/home-energy-scotland-grant-loan", "titolo": 'Home Energy Scotland: funding for homeowners', "chi": 'Home Energy Scotland, funded by the Scottish Government',
        "cerca": ['For heating systems such as heat pumps and heat network connections, grant funding of up to £7,500 is available',
                  'For energy efficiency measures such as insulation, grant funding is available up to 75% of the combined cost of measures up to a maximum grant amount of £7,500.',
                  'An uplift of £1,500 is available for rural and island homes to both the heating and energy efficiency grants, meaning rural households can claim up to £18,000 in grant funding.',
                  'the property is an existing property located in Scotland and you are the homeowner – you own the home you live in and it is your only or primary private residence.',
                  'You do not need to be in receipt of benefits to qualify',
                  'Only heat pumps that provide 100% of heating and hot water requirements are eligible for funding.',
                  'Hybrid heat pumps, air-to-air heat pumps and exhaust air heat pumps are not eligible for funding.',
                  'Solid wall insulation (external and internal) £2,500 £7,500',
                  'Flat roof or room-in-roof insulation £1,000 £3,000',
                  'Loft, cavity and underfloor insulation £500 £1,500',
                  'Heating controls £150 £450',
                  'Solar thermal £5,000 Not available',
                  'Hybrid solar PV / water heating¹ £5,000 Not available',
                  'Funding is allocated on a first-come, first-served basis and is subject to availability.',
                  'Funding agreements are valid for nine months.',
                  'you must use both a Microgeneration Certification Scheme (MCS) installer',
                  'a free advice service funded by the Scottish Government',
                  '0808 808 2282',
                  "You'll need a valid Energy Performance Certificate (EPC) if you want to apply for funding for energy efficiency improvements."]},
    "hes_whs": {"url": "https://www.homeenergyscotland.org/warmer-homes-scotland", "titolo": 'Warmer Homes Scotland', "chi": 'Home Energy Scotland, for the Scottish Government',
        "cerca": ["The Scottish Government's Warmer Homes Scotland programme offers support worth £10,000 or more for eligible households for energy-saving home improvements like heating and insulation to help make your home warmer and cheaper to heat.",
                  'Be a homeowner or the tenant of a private-sector landlord.',
                  'Live in the home as your main residence.',
                  'Have lived there for at least six months',
                  'Live in a home with a poor energy rating.',
                  'Live in a home with a floor area of 230m2 or less (typically up to five bedrooms).',
                  'Live in a home where the council tax band is A - G.',
                  'Eligible households must include either a person who is aged 75 and over with no working heating, a person who has a DS1500 or BASRiS certificate completed by a medical professional, or a person who receives at least one of the passport benefits',
                  "The work is done by Warmworks' installers and in most cases, the Scottish Government will meet all the costs.",
                  'central heating (including electric storage heater, new gas boiler or air source heat pump)',
                  'installing a home renewables system',
                  "You cannot get funding for work that's already completed.",
                  "Warmworks will need your landlord's permission before any energy-saving home improvements can be installed."]},
    "wales_nest": {"url": "https://www.gov.wales/get-help-energy-efficiency-your-home-nest", "titolo": 'Get help with energy efficiency in your home from Nest', "chi": 'Welsh Government (GOV.WALES)',
        "cerca": ['Nest is a Welsh Government scheme which provides free advice and home improvements to help you save energy and money.',
                  'Nest free on 0808 808 2244',
                  'Calls and emails are welcomed in Welsh.',
                  'If your property is without heating or hot water, you may be eligible for a repair or replacement to boilers or electric storage heaters.']},
    "wales_nest_free": {"url": "https://www.gov.wales/get-free-home-energy-efficiency-improvements-nest", "titolo": 'Get free home energy efficiency improvements: Nest', "chi": 'Welsh Government (GOV.WALES)',
        "cerca": ['Nest can confirm if you are eligible for a package of free home energy efficiency improvements such as: heat pump insulation solar panels']},
    "nid_grants": {"url": "https://www.nidirect.gov.uk/articles/energy-saving-grants-your-area", "titolo": 'Energy saving grants in your area', "chi": 'nidirect, Northern Ireland Government',
        "cerca": ['The Affordable Warmth Scheme aims to help with the effects of fuel poverty and energy inefficiency.',
                  'It is run by the Northern Ireland Housing Executive (NIHE).',
                  'NI Energy Advice offers independent and impartial energy advice to domestic householders in Northern Ireland - plus referrals to energy grants and other sources of help.',
                  'The Northern Ireland Sustainable Energy Programme fund is collected from all Northern Ireland electricity customers through a public service obligation.']},
    "mcs_find": {"url": "https://mcscertified.com/find-an-installer/", "titolo": "Find an MCS certified installer", "chi": "Microgeneration Certification Scheme (MCS)",
                 "cerca": []},
}


def scarica(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.status, r.read()


def norm(t):
    t = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S | re.I)))
    t = t.replace("’", "'").replace("‘", "'").replace("\xa0", " ")
    return re.sub(r"\s+", " ", t)


def api(percorso):
    st, b = scarica(API + percorso)
    return json.loads(b.decode("utf-8"))


def trova_allegato(d):
    """Indirizzo, titolo e data di pubblicazione dell'allegato voluto; per le collezioni prima l'ultima uscita."""
    pag = api(d["pagina"])
    if d.get("collezione"):
        uscite = sorted(pag["links"]["documents"], key=lambda x: x.get("public_updated_at", ""), reverse=True)
        uscite = [u for u in uscite if d.get("filtro", "statistics-") in u["base_path"]]
        pag = api(uscite[0]["base_path"].lstrip("/"))
    for a in pag["details"].get("attachments", []):
        if re.search(d["allegato"], a.get("title", "")):
            data = pag.get("first_published_at") if d.get("collezione") else pag.get("public_updated_at")
            return a["url"], a["title"], data, "https://www.gov.uk" + pag["base_path"], pag.get("title")
    raise SystemExit(f"allegato {d['allegato']} non trovato in {d['pagina']}")


def main():
    GREZZI.mkdir(exist_ok=True)
    oggi = date.today().isoformat()
    definizioni, esiti = {}, {}
    for fid, d in FILE_STAT.items():
        url, titolo_all, pubblicato, pagina, titolo_pag = trova_allegato(d)
        st, b = scarica(url)
        (GREZZI / d["nome"]).write_bytes(b)
        definizioni[fid] = {"url": url, "pagina": pagina, "titolo": d["titolo"], "chi": d["chi"], "file": d["nome"], "titolo_allegato": titolo_all,
                            "uscita": titolo_pag, "tipo": "xlsx", "licenza": "Open Government Licence v3.0"}
        esiti[fid] = {"http": st, "letto_il": oggi, "sha256": hashlib.sha256(b).hexdigest(), "byte": len(b), "pubblicato": pubblicato}
        print(f"{fid}: {titolo_pag} -> {d['nome']} ({len(b):,} byte)")
    for pid, p in PAGINE.items():
        definizioni[pid] = {"url": p["url"], "titolo": p["titolo"], "chi": p["chi"], "tipo": "pagina", "cerca": p["cerca"]}
        try:
            if p.get("api"):
                dj = api(p["api"])
                corpo = " ".join(x.get("body", "") for x in dj["details"].get("parts", [])) or dj["details"].get("body", "")
                testo, st, agg = norm(corpo), 200, dj.get("public_updated_at")
            else:
                st, b = scarica(p["url"])
                testo, agg = norm(b.decode("utf-8", errors="replace")), None
            trovate = {c: (norm(c) in testo) for c in p["cerca"]}
            esiti[pid] = {"http": st, "letto_il": oggi, "aggiornata": agg, "sha256": hashlib.sha256(testo.encode("utf-8")).hexdigest(),
                          "trovate": trovate}
            manca = [c for c, ok in trovate.items() if not ok]
            print(f"{pid}: HTTP {st}, {len(trovate) - len(manca)}/{len(trovate)} frasi" + (f" MANCANO: {manca}" if manca else ""))
        except Exception as e:  # noqa: BLE001
            esiti[pid] = {"http": getattr(e, "code", str(e)[:80]), "letto_il": oggi, "trovate": {c: False for c in p["cerca"]}}
            print(f"{pid}: errore {e}", file=sys.stderr)
    FILE.write_text(json.dumps({"definizioni": definizioni, "fonti": esiti}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"-> {FILE}")


if __name__ == "__main__":
    main()
