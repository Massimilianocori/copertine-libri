"""Legge le pagine ufficiali del Destination Thailand Visa (DTV) delle ambasciate e dei consolati thailandesi e scrive
visaincome/dati/dtv.json (sezione "Thailand DTV visa" del sito, dal 30/10/2026).

Uso (dalla radice del repository):
    python3 visaincome/raccolta/dtv.py              # rilegge tutte le pagine e scrive il JSON (domanda: quella già salvata)
    python3 visaincome/raccolta/dtv.py --domanda    # rifà anche l'autocompletamento di Google (circa 5 minuti)

Come funziona
- Elenco delle sedi: pagina www.thaiembassy.org (Ministero degli Esteri thailandese), dati della pagina (__NEXT_DATA__):
  ambasciate ("Royal Thai Embassy") e consolati generali ("Royal Thai Consulate-General"). Missioni presso organizzazioni
  internazionali e l'ufficio di Taipei esclusi (non rilasciano visti come le altre o non hanno un sito sullo stesso sistema).
- Le sedi sullo stesso sistema di pagine (<città>.thaiembassy.org) mettono il testo della pagina nei dati __NEXT_DATA__
  (campo html o description) con la data di inserimento (date) e di modifica (date_edit). Lo script legge quel testo.
- LETTURE (sotto) contiene, per ogni sede di cui abbiamo trovato la pagina del DTV, i valori letti A MANO il 30/10/2026
  (costo, valuta, regola sulla residenza, saldo bancario) e, per ognuno, il FRAMMENTO DI TESTO della pagina ufficiale da cui viene.
  A ogni lancio lo script riscarica le pagine e controlla che ogni frammento sia ancora nel testo (spazi normalizzati):
  se un frammento manca, la pagina è cambiata e il JSON NON viene aggiornato (esce con codice 1) finché qualcuno non rilegge la pagina
  e aggiorna LETTURE. Per ogni pagina si salvano anche l'impronta SHA-256 del testo e la data di modifica scritta dalla sede.
- Le sedi in cui non abbiamo trovato una pagina DTV leggibile (sito in thailandese, testo solo in immagini, sito su un altro sistema)
  restano nell'elenco con lo stato della home (HTTP) e il link: le pagine del sito dicono di controllare la sede.
- Domanda: autocompletamento di Google (client=firefox, hl=en, gl=us/uk/in/vn), salvata in "domanda"; una sede ha una pagina
  propria solo se almeno un suggerimento con "dtv" nomina la sua città (o il suo Paese, per l'ambasciata) e se abbiamo letto
  almeno il costo o la regola sulla residenza.
Nessun testo copiato per intero: si pubblicano fatti brevi (importi, condizioni) con il link alla pagina ufficiale.
"""
import hashlib
import html as H
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import concurrent.futures as cf
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
USCITA = RADICE / "dati" / "dtv.json"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"}
ELENCO = "https://www.thaiembassy.org/"
ANNUNCIO_MFA = "https://consular.mfa.go.th/th/content/28-8-69-00?cate=5ddbe42115e39c4768007e1d"   # Department of Consular Affairs, 28/8/2026
EVISA = "https://www.thaievisa.go.th/"

# ---------------------------------------------------------------- letture a mano (30/10/2026)
# pagine: URL letti (indice 0, 1...). costo/residenza/saldo/altre: "frammento" = testo che deve stare nella pagina (indice "p").
# residenza.tipo: "paese" = cittadini o residenti permanenti del Paese (o dei Paesi) della sede; "carta" = solo carta di residenza;
# "vecchia" = pagina modificata prima del 31/8/2026 con una regola diversa; "generale" = la sede ripete la regola generale.
# chiavi: parole che, insieme a "dtv", in un suggerimento di ricerca contano come domanda per questa sede.
LETTURE = [
    {"id": "london", "sede": "London", "paese": "United Kingdom", "tipo": "Embassy",
     "pagine": ["https://london.thaiembassy.org/en/page/destination-thailand-visa", "https://london.thaiembassy.org/en/page/visa-general-information"],
     "costo": {"importo": 300, "valuta": "GBP", "frammento": "Visa Fee: £300", "p": 0},
     "residenza": {"tipo": "paese", "frammento": "Proof of permanent residence in the UK, Ireland, or the British Overseas Territories", "p": 0},
     "saldo": {"frammento": "amount of no less than £12,000 (500,000 THB)", "p": 0},
     "altre": [{"frammento": "the Embassy is unable to issue visas for foreign nationals who are outside the United Kingdom (UK), Ireland, or UK Territories", "p": 1},
               {"frammento": "The police clearance certificate must be issued within 6 months from the date of submission", "p": 1}],
     "chiavi": ["london", "uk", "united kingdom"]},
    {"id": "washington-dc", "sede": "Washington, DC", "paese": "United States", "tipo": "Embassy",
     "pagine": ["https://washingtondc.thaiembassy.org/en/page/dtv-visa"],
     "costo": {"importo": 400, "valuta": "USD", "frammento": "Fee: 400 USD", "p": 0},
     "residenza": {"tipo": "paese", "frammento": "Proof of permanent residence (i.e. valid U.S. Visa, Permanent resident Card)", "p": 0},
     "saldo": {"frammento": "ending balance of no less than 500,000 THB or ($16,000 USD)", "p": 0},
     "altre": [{"frammento": "A copy of the permanent resident alien card or a copy of a valid US visa (at least 6 months validity)", "p": 0}],
     "chiavi": ["washington", "usa", "us", "united states"]},
    {"id": "los-angeles", "sede": "Los Angeles", "paese": "United States", "tipo": "Consulate-General",
     "pagine": ["https://thaiconsulatela.thaiembassy.org/en/publicservice/dtv-visa", "https://thaiconsulatela.thaiembassy.org/en/page/visa-types-requirments",
                "https://thaiconsulatela.thaiembassy.org/en/page/visa-information"],
     "costo": {"importo": 400, "valuta": "USD", "frammento": "DTV | Workcation (Digital Nomad/remote worker/foreign talent/freelancer | N/A | 400 |", "p": 1,
               "nota": "fee table of the consulate, price for multiple entries; the table does not print the currency"},
     "residenza": {"tipo": "paese", "frammento": "Proof of permanent residence (i.e. valid driving license, valid U.S. Visa, Permanent resident Card)", "p": 0},
     "saldo": {"frammento": "ending balance of no less than 500,000 THB", "p": 0},
     "altre": [{"frammento": "please apply through the Royal Thai Embassy or Royal Thai Consulate-General responsible for your state of residence", "p": 2}],
     "chiavi": ["los angeles"]},
    {"id": "new-york", "sede": "New York", "paese": "United States", "tipo": "Consulate-General",
     "pagine": ["https://newyork.thaiembassy.org/en/page/visa-types-and-requirements"],
     "costo": {"importo": 400, "valuta": "USD", "frammento": "DTV | Workcation (Digital Nomad/remote worker/foreign talent/freelancer | N/A | 400 |", "p": 0,
               "nota": "fee table of the consulate, price for multiple entries; the table does not print the currency"},
     "chiavi": ["new york"]},
    {"id": "chicago", "sede": "Chicago", "paese": "United States", "tipo": "Consulate-General",
     "pagine": ["https://cgchicago.thaiembassy.org/en/page/visa-types-and-fees-v-2"],
     "costo": {"importo": 400, "valuta": "USD", "frammento": "DTV | Workcation (Digital Nomad/remote worker/foreign talent/freelancer) | N/A | 400 |", "p": 0,
               "nota": "fee table of the consulate, price for multiple entries; the table does not print the currency"},
     "chiavi": ["chicago"]},
    {"id": "vientiane", "sede": "Vientiane", "paese": "Laos", "tipo": "Embassy",
     "pagine": ["https://vientiane.thaiembassy.org/en/publicservice/destination-thailand-visa-dtv", "https://vientiane.thaiembassy.org/en/page/applying-for-a-visa"],
     "costo": {"importo": 10000, "valuta": "THB", "frammento": "VISA FEE (Cash only in Thai Baht and non-refundable ) 10,000 Baht", "p": 0,
               "nota": "cash only, in Thai baht"},
     "residenza": {"tipo": "paese", "frammento": "Be Lao nationals or permanent residents of the Lao PDR", "p": 1},
     "altre": [{"frammento": "new additional requirements for Destination Thailand Visa (DTV) applications will take effect worldwide from 31 August 2026", "p": 1},
               {"frammento": "Walk-ins will not be accepted", "p": 0}],
     "chiavi": ["vientiane", "laos"]},
    {"id": "savannakhet", "sede": "Savannakhet", "paese": "Laos", "tipo": "Consulate-General",
     "pagine": ["https://savannakhet.thaiembassy.org/th/publicservice/destination-thailand-visa"],
     "residenza": {"tipo": "paese", "frammento": "Proof of permanent residence in Lao PDR.", "p": 0},
     "saldo": {"frammento": "amount of not less than THB 500,000", "p": 0},
     "chiavi": ["savannakhet"]},
    {"id": "ho-chi-minh-city", "sede": "Ho Chi Minh City", "paese": "Vietnam", "tipo": "Consulate-General",
     "pagine": ["https://hochiminh.thaiembassy.org/en/page/destination-thailand-visa-dtv-thị-thực-điểm-đến-th"],
     "costo": {"importo": 340, "valuta": "USD", "frammento": "Visa processing fee: 340 USD", "p": 0, "nota": "debit or credit card only"},
     "residenza": {"tipo": "carta", "frammento": "For foreigners: Only a Temporary Residence Card (TRC) or Permanent Residence Card (PRC) is accepted.", "p": 0},
     "saldo": {"frammento": "amount of no less than 500,000 THB", "p": 0},
     "altre": [{"frammento": "For Vietnamese citizens: A valid Vietnamese ID card", "p": 0},
               {"frammento": "Expedited visa application is NOT available", "p": 0}],
     "chiavi": ["ho chi minh", "hcmc", "saigon", "vietnam"]},  # Hanoi (ambasciata) ha il DTV solo in immagini: il Paese va a Ho Chi Minh
    {"id": "kuala-lumpur", "sede": "Kuala Lumpur", "paese": "Malaysia", "tipo": "Embassy",
     "pagine": ["https://kualalumpur.thaiembassy.org/en/publicservice/destination-thailand-visa-dtv",
                "https://kualalumpur.thaiembassy.org/en/publicservice/visa-types-fees-requirements"],
     "costo": {"importo": 1600, "valuta": "MYR", "frammento": "DTV | Workcation (digital nomad/remote worker/ foreign talent/freelancer) | N/A | 1,600 |", "p": 1,
               "frammento2": "Price for Multiple (MYR)", "nota": "fee table of the embassy, price for multiple entries, in ringgit"},
     "altre": [{"frammento": "The processing time for DTV may take approximately 1 month or more", "p": 0}],
     "chiavi": ["kuala lumpur", "malaysia"]},
    {"id": "kota-bharu", "sede": "Kota Bharu", "paese": "Malaysia", "tipo": "Consulate-General",
     "pagine": ["https://kotabharu.thaiembassy.org/th/page/destination-thailand-visa-dtv"],
     "costo": {"importo": 1600, "valuta": "MYR", "frammento": "Visa Fee : 1,600 Ringgit", "p": 0},
     "saldo": {"frammento": "with a minimum of 500,000 baht", "p": 0},
     "chiavi": ["kota bharu"]},
    {"id": "singapore", "sede": "Singapore", "paese": "Singapore", "tipo": "Embassy",
     "pagine": ["https://singapore.thaiembassy.org/en/page/dtv-visa-workcation"],
     "costo": {"importo": 500, "valuta": "SGD", "frammento": "Multiple Entry : 500 SGD", "p": 0},
     "residenza": {"tipo": "paese", "frammento": "DTV Visa will only be granted by the Royal Thai Embassy Singapore to Singapore Citizens and Singapore Permanent Residents", "p": 0},
     "saldo": {"frammento": "balance at least 500,000 THB (Approximtely 20,000 SGD) for the past 3 months", "p": 0},
     "altre": [{"frammento": "Accept only Singapore and Thailand bank saving account", "p": 0}],
     "chiavi": ["singapore"]},
    {"id": "yangon", "sede": "Yangon", "paese": "Myanmar", "tipo": "Embassy",
     "pagine": ["https://yangon.thaiembassy.org/en/publicservice/destination-thailand-visa-dtv"],
     "costo": {"importo": 400, "valuta": "USD", "frammento": "Visa Fee 400 USD", "p": 0},
     "saldo": {"frammento": "no less than 500,000 THB or equivalent amount", "p": 0},
     "chiavi": ["yangon", "myanmar"]},
    {"id": "helsinki", "sede": "Helsinki", "paese": "Finland", "tipo": "Embassy",
     "pagine": ["https://helsinki.thaiembassy.org/en/publicservice/destination-thailand-visa-dtv"],
     "costo": {"importo": 350, "valuta": "EUR", "frammento": "VISA Fee : 350 Euro", "p": 0},
     "residenza": {"tipo": "paese", "frammento": "a valid permanent residence permit card in Finland/Estonia", "p": 0},
     "saldo": {"frammento": "no less than 500,000 THB or (15,000 Euro)", "p": 0},
     "chiavi": ["helsinki", "finland"]},
    {"id": "budapest", "sede": "Budapest", "paese": "Hungary", "tipo": "Embassy",
     "pagine": ["https://budapest.thaiembassy.org/en/publicservice/destination-thailand-visa-dtv"],
     "costo": {"importo": 350, "valuta": "EUR", "frammento": "Application fee : 350 euro for multiple entry", "p": 0},
     "residenza": {"tipo": "vecchia", "frammento": "Proof of current location such as a passport stamp or residence permit.", "p": 0},
     "chiavi": ["budapest", "hungary"]},
    {"id": "bucharest", "sede": "Bucharest", "paese": "Romania", "tipo": "Embassy",
     "pagine": ["https://bucharest.thaiembassy.org/en/page/destination-thailand-visa-dtv"],
     "costo": {"importo": 350, "valuta": "EUR", "frammento": "Visa fee : 350 EUR multiple entries", "p": 0},
     "residenza": {"tipo": "paese", "frammento": "Applicants who are Romanian or Bulgarian citizens, or who hold a valid long-term or permanent residence permit in Romania or Bulgaria, may apply for a DTV through the Royal Thai Embassy in Bucharest", "p": 0},
     "saldo": {"frammento": "demonstrating funds of at least THB 500,000", "p": 0},
     "chiavi": ["bucharest", "romania"]},
    {"id": "rome", "sede": "Rome", "paese": "Italy", "tipo": "Embassy",
     "pagine": ["https://rome.thaiembassy.org/en/publicservice/dtv", "https://rome.thaiembassy.org/en/content/adjustment-of-supporting-documents-for-dtv-applica"],
     "residenza": {"tipo": "paese", "frammento": "A document proving residency status in Italy, Cyprus, Albania, or Libya.", "p": 1},
     "saldo": {"frammento": "minimum balance of 500,000 THB or equivalent", "p": 0},
     "altre": [{"frammento": "Proof of permanent residence in the country where the application is submitted", "p": 0}],
     "chiavi": ["rome", "italy"]},
    {"id": "madrid", "sede": "Madrid", "paese": "Spain", "tipo": "Embassy",
     "pagine": ["https://madrid.thaiembassy.org/en/publicservice/dtv", "https://madrid.thaiembassy.org/en/publicservice/annoucement-consular-service-fees-15-july-2024"],
     "costo": {"importo": 350, "valuta": "EUR", "frammento": "Destination Thailand Visa (DTV) | 350", "p": 1, "frammento2": "Tasa (euros)",
               "nota": "fee table of the embassy, in Spanish, fees in euros"},
     "residenza": {"tipo": "paese", "frammento": "deberán ser nacionales españoles o andorranos, o residentes permanentes del Reino de España o del Principado de Andorra", "p": 0,
                   "traduzione": "must be Spanish or Andorran nationals, or permanent residents of Spain or Andorra (our translation from Spanish)"},
     "saldo": {"frammento": "un depósito igual o superior a 500.000 bahts", "p": 0, "traduzione": "a deposit of 500,000 baht or more (our translation from Spanish)"},
     "chiavi": ["madrid", "spain"]},
    {"id": "oslo", "sede": "Oslo", "paese": "Norway", "tipo": "Embassy",
     "pagine": ["https://oslo.thaiembassy.org/en/page/dtv"],
     "residenza": {"tipo": "paese", "frammento": "Proof of permanent residence in Norway/Iceland.", "p": 0},
     "saldo": {"frammento": "an amount of no less than 500,000 THB", "p": 0},
     "chiavi": ["oslo", "norway"]},
    {"id": "moscow", "sede": "Moscow", "paese": "Russia", "tipo": "Embassy",
     "pagine": ["https://moscow.thaiembassy.org/en/publicservice/dtv"],
     "costo": {"importo": 350, "valuta": "USD", "frammento": "Visa processing Fee: 350 USD", "p": 0},
     "residenza": {"tipo": "paese", "frammento": "Proof of permanent residence in the country where the application is submitted.", "p": 0},
     "saldo": {"frammento": "minimum balance of 500,000 THB or equivalent", "p": 0},
     "altre": [{"frammento": "FOR NON-RUSSIAN CITIZENS , a copy of permanent residence permit or a copy of valid Russian visa and registration paper", "p": 0}],
     "chiavi": ["moscow", "russia"]},
    {"id": "cairo", "sede": "Cairo", "paese": "Egypt", "tipo": "Embassy",
     "pagine": ["https://cairo.thaiembassy.org/en/publicservice/destination-thailand-visa-dtv"],
     "costo": {"importo": 18000, "valuta": "EGP", "frammento": "18,000 EGP", "p": 0},
     "residenza": {"tipo": "vecchia", "frammento": "Every Non-Egyptian applicant must have an EGYPTIAN Residence visa", "p": 0},
     "saldo": {"frammento": "account balance of not less than 850,000 EGP for previous consecutive 3 months", "p": 0},
     "chiavi": ["cairo", "egypt"]},
    {"id": "warsaw", "sede": "Warsaw", "paese": "Poland", "tipo": "Embassy",
     "pagine": ["https://warsaw.thaiembassy.org/en/page/visa-information"],
     "costo": {"importo": 1575, "valuta": "PLN", "frammento": "Pay application fee online: 1,575 PLN (multiple entries)", "p": 0},
     "residenza": {"tipo": "vecchia", "frammento": "applicants who are currently residing in Poland or Ukraine", "p": 0},
     "chiavi": ["warsaw", "poland"]},
    {"id": "new-delhi", "sede": "New Delhi", "paese": "India", "tipo": "Embassy",
     "pagine": ["https://newdelhi.thaiembassy.org/en/page/visa"],
     "costo": {"importo": 30000, "valuta": "INR", "frammento": "DTV | Multiple | 5 years | 180 days | 30,000 INR |", "p": 0,
               "nota": "fee table of the embassy"},
     "altre": [{"frammento": "The 30-day visa exemption for Indian ordinary passport holders for tourism and short-term business engagements purposes remains effective from 15 September 2026 until further announcement.", "p": 0}],
     "chiavi": ["new delhi", "delhi", "india", "indians", "indian"]},
    {"id": "hong-kong", "sede": "Hong Kong", "paese": "China", "tipo": "Consulate-General",
     "pagine": ["https://hongkong.thaiembassy.org/en/page/visa-info"],
     "residenza": {"tipo": "paese", "frammento": "Applicants need to show proof of their permanent residence in Hong Kong SAR or Macau SAR", "p": 0},
     "saldo": {"frammento": "account balance / income of at least 150,000 HKD", "p": 0},
     "chiavi": ["hong kong"]},
    {"id": "qingdao", "sede": "Qingdao", "paese": "China", "tipo": "Consulate-General",
     "pagine": ["https://qingdao.thaiembassy.org/th/page/86106-ข้อมูลวีซ่าประเภทต่าง-ๆ"],
     "costo": {"importo": 2300, "valuta": "CNY", "frammento": "Spouse and dependent children of DTV holders | 2,300 RMB", "p": 0, "nota": "fee table of the consulate"},
     "chiavi": ["qingdao"]},
    {"id": "osaka", "sede": "Osaka", "paese": "Japan", "tipo": "Consulate-General",
     "pagine": ["https://osaka.thaiembassy.org/en/content/announcement-updated-requirements-dtv"],
     "residenza": {"tipo": "generale", "frammento": "Proof of permanent residence in the country/territory where the visa application is submitted", "p": 0},
     "chiavi": ["osaka"]},
    # pagine DTV trovate, ma senza costo né regola sulla residenza nel testo (immagini, avviso generale o pagina breve)
    {"id": "phnom-penh", "sede": "Phnom Penh", "paese": "Cambodia", "tipo": "Embassy",
     "pagine": ["https://phnompenh.thaiembassy.org/en/publicservice/destination-thailand-visa-dtv"],
     "saldo": {"frammento": "amount of no less than 500,000 THB", "p": 0}, "chiavi": ["phnom penh", "cambodia"]},
    {"id": "dubai", "sede": "Dubai", "paese": "United Arab Emirates", "tipo": "Consulate-General",
     "pagine": ["https://dubai.thaiembassy.org/en/content/destination-thailand-visa-dtv"], "chiavi": ["dubai"]},
    {"id": "tel-aviv", "sede": "Tel Aviv", "paese": "Israel", "tipo": "Embassy",
     "pagine": ["https://telaviv.thaiembassy.org/en/content/destination-thailand-visa-dtv"], "chiavi": ["tel aviv", "israel"]},
    {"id": "canberra", "sede": "Canberra", "paese": "Australia", "tipo": "Embassy",
     "pagine": ["https://canberra.thaiembassy.org/en/content/destination-thailand-visa-dtv"], "chiavi": ["canberra", "australia"]},
    {"id": "pretoria", "sede": "Pretoria", "paese": "South Africa", "tipo": "Embassy",
     "pagine": ["https://pretoria.thaiembassy.org/en/page/destination-thailand-visa-dtv"], "chiavi": ["pretoria", "south africa"]},
    {"id": "dhaka", "sede": "Dhaka", "paese": "Bangladesh", "tipo": "Embassy",
     "pagine": ["https://dhaka.thaiembassy.org/en/publicservice/destination-thailand-visa-dtv"], "chiavi": ["dhaka", "bangladesh"]},
    {"id": "bandar-seri-begawan", "sede": "Bandar Seri Begawan", "paese": "Brunei", "tipo": "Embassy",
     "pagine": ["https://bsb.thaiembassy.org/en/publicservice/destination-thailand-visa-dtv"], "chiavi": ["brunei"]},
    {"id": "athens", "sede": "Athens", "paese": "Greece", "tipo": "Embassy",
     "pagine": ["https://athens.thaiembassy.org/en/content/announcement-no-2-2567-destination-thailand-visa"], "chiavi": ["athens", "greece"]},
    {"id": "hanoi", "sede": "Hanoi", "paese": "Vietnam", "tipo": "Embassy",
     "pagine": ["https://rtehanoi.thaiembassy.org/th/publicservice/destination-thailand-visa"], "chiavi": ["hanoi"]},
    {"id": "nanning", "sede": "Nanning", "paese": "China", "tipo": "Consulate-General",
     "pagine": ["https://nanning.thaiembassy.org/th/publicservice/destination-thailand-visa-dtv"], "chiavi": ["nanning"]},
    {"id": "chengdu", "sede": "Chengdu", "paese": "China", "tipo": "Consulate-General",
     "pagine": ["https://chengdu.thaiembassy.org/th/content/destination-thailand-visa-dtv"], "chiavi": ["chengdu"]},
    {"id": "nairobi", "sede": "Nairobi", "paese": "Kenya", "tipo": "Embassy",
     "pagine": ["https://nairobi.thaiembassy.org/th/publicservice/dtv"], "chiavi": ["nairobi", "kenya"]},
]

# Regola generale dal 31/8/2026 ed esenzione dal visto di 30 giorni dal 15/9/2026: pagine ufficiali e frammenti controllati
GENERALE = {
    "regola_osaka": {"url": "https://osaka.thaiembassy.org/en/content/announcement-updated-requirements-dtv",
                     "frammenti": ["Effective from 31 August 2026", "Proof of permanent residence in the country/territory where the visa application is submitted",
                                   "Certificate of criminal record clearance issued by the country/territory of the applicant’s nationality or permanent residence",
                                   "Applications submitted before 31 August 2026 will be considered in accordance with the supporting document requirements applicable prior to the effective date"]},
    "regola_mosca": {"url": "https://moscow.thaiembassy.org/en/publicservice/adjustment-to-supporting-documents-for-destination-thailand-visa-dtv-a",
                     "frammenti": ["According to an announcement published by the Department of Consular Affairs, Ministry of Foreign Affairs of Thailand, on 28 August 2026",
                                   "The revised requirements have been in effect since 00.00 hrs. on 31 August 2026 (Thailand local time)"]},
    "esenzione_londra": {"url": "https://london.thaiembassy.org/en/page/exemp-visa",
                         "frammenti": ["Effective from 15 September 2026", "British and Irish passport holders, as well as foreign travellers from many other countries",
                                       "can enter Thailand without a visa for up to 30 days under the Visa Exemption Scheme for tourism purposes only",
                                       "only twice within a calendar year", "proof of sufficient funds of 20,000 THB per person",
                                       "they may request an extension of stay for up to 30 days"]},
    "esenzione_washington": {"url": "https://washingtondc.thaiembassy.org/en/page/visaexempt-voajul2024",
                             "frammenti": ["New Tourist Visa Exemption Scheme (30 Days) Effective Date 15 September 2026",
                                           "Nationals of the following 60 countries and territories are entitled to visa exemption for the purpose of tourism for up to 30 days period of stay"]},
}

# Ricerche per l'autocompletamento (con --domanda): gl=us su QUERY_US, gl=uk/in/vn su QUERY_ALTRE
CITTA_US = ("london|washington|vientiane|hanoi|ho chi minh|kuala lumpur|singapore|phnom penh|new delhi|dubai|penang|jakarta|tokyo|sydney|"
            "los angeles|new york|berlin|savannakhet|manila|seoul|hong kong|taipei|colombo|kathmandu|yangon|mumbai|chennai|kolkata|canberra|"
            "wellington|ottawa|vancouver|chicago|paris|madrid|lisbon|rome|the hague|stockholm|oslo|copenhagen|helsinki|budapest|prague|vienna|"
            "warsaw|athens|ankara|doha|abu dhabi|riyadh|cairo|nairobi|pretoria|mexico|buenos aires|lima|santiago|bern|frankfurt|munich|osaka|"
            "shanghai|guangzhou|beijing|dhaka|islamabad|karachi|siem reap|kota bharu|brunei|dili|moscow|tel aviv|astana|bucharest|qingdao")
QUERY_US = ["dtv visa ", "dtv visa from", "dtv visa embassy", "dtv visa thai embassy", "dtv visa fee", "dtv visa price", "dtv visa cost",
            "dtv visa requirements", "dtv visa insurance"] + [f"dtv visa {x}" for x in CITTA_US.split("|")]
QUERY_ALTRE = (["dtv visa ", "dtv visa from", "dtv visa embassy", "dtv visa fee"] +
               [f"dtv visa {x}" for x in ("vietnam", "laos", "malaysia", "india", "singapore", "hong kong", "usa", "uk", "cambodia", "myanmar", "russia",
                                          "egypt", "poland", "spain", "italy", "finland", "romania", "hungary", "norway", "china", "nepal", "sri lanka")] +
               [f"dtv visa from {x}" for x in ("vietnam", "laos", "india", "malaysia", "uk", "usa", "cambodia", "hong kong", "singapore", "russia")] +
               [f"dtv visa {x}" for x in ("london", "ho chi minh", "vientiane", "kuala lumpur", "washington", "los angeles", "new york", "chicago", "yangon",
                                          "moscow", "warsaw", "madrid", "rome", "helsinki", "bucharest", "budapest", "oslo", "cairo", "kota bharu",
                                          "savannakhet", "osaka", "qingdao", "new delhi")])


def get(u, tentativi=3):
    for i in range(tentativi):
        try:
            r = urllib.request.urlopen(urllib.request.Request(urllib.parse.quote(u, safe=":/?&=%#"), headers=UA), timeout=45)
            return r.status, r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            c = getattr(e, "code", 0)
            if c in (403, 404, 410):
                return c, ""
            time.sleep(2 + 2 * i)
    return 0, ""


def dati_pagina(t):
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', t, re.S)
    if not m:
        return None
    pg = json.loads(m.group(1))["props"]["pageProps"]["components_meta"].get("page")
    return pg.get("data") if isinstance(pg, dict) and pg.get("data") else None


def testo(h):
    h = re.sub(r"<br\s*/?>|</p>|</li>|</tr>|</h\d>|</div>", "\n", h or "")
    h = re.sub(r"</td>", " | ", h)
    t = H.unescape(re.sub(r"<[^>]+>", " ", h))
    return re.sub(r"\s+", " ", t).strip()


def leggi(u):
    st, t = get(u)
    d = dati_pagina(t) if st == 200 else None
    if not d:
        return {"url": u, "http": st, "ok": False}
    tx = testo(d.get("html") or d.get("description"))
    return {"url": u, "http": st, "ok": True, "titolo": (d.get("name") or d.get("title") or "").strip(), "inserita": (d.get("date") or "")[:10],
            "modificata": (d.get("date_edit") or "")[:10], "caratteri": len(tx), "sha256": hashlib.sha256(tx.encode("utf-8")).hexdigest(), "_testo": tx}


def elenco_sedi():
    st, t = get(ELENCO)
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', t, re.S)
    if st != 200 or not m:
        sys.exit(f"ERRORE: elenco delle sedi non leggibile ({ELENCO}, HTTP {st})")
    cats = json.loads(m.group(1))["props"]["pageProps"]["components_meta"]["page"][0]["data"]["item"]["embassy_category"]
    out = []
    for c in cats:
        tipo = {"Royal Thai Embassy": "Embassy", "Royal Thai Consulate-General": "Consulate-General"}.get(c["name"])
        if not tipo:
            continue
        for it in c["items"]:
            u = it["url"].split(",")[0].strip()
            u = u if u.startswith("http") else "https://" + u
            citta = it["capital"].split("/")[0].strip()
            out.append({"sede": citta.title() if citta.isupper() else citta, "paese": it["country"].strip(), "tipo": tipo, "sito": u.rstrip("/")})
    return out


def stato_sito(s):
    base = re.match(r"https?://[^/]+", s["sito"]).group(0)
    if "thaiembassy.org" not in base:
        st, _ = get(s["sito"], tentativi=2)
        return {**s, "sistema": "other", "http": st}
    st, _ = get(base.replace("http://", "https://") + "/en/index", tentativi=2)
    lingua = "en"
    if st != 200:
        st, _ = get(base.replace("http://", "https://") + "/th/index", tentativi=2)
        lingua = "th"
    return {**s, "sistema": "thaiembassy.org", "http": st, "lingua_home": lingua}


def autocompleta(q, gl):
    u = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode({"client": "firefox", "gl": gl, "hl": "en", "q": q})
    for i in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20)
            return json.loads(r.read().decode("utf-8", "replace"))[1]
        except Exception:  # noqa: BLE001
            time.sleep(2)
    return None


def nuova_domanda():
    out = {}
    for gl, qs in (("us", QUERY_US), ("uk", QUERY_ALTRE), ("in", QUERY_ALTRE), ("vn", QUERY_ALTRE)):
        for q in qs:
            out[f"{gl}|{q}"] = autocompleta(q, gl)
            time.sleep(0.3)
    return {"data": date.today().isoformat(), "metodo": "https://suggestqueries.google.com/complete/search?client=firefox&gl=<us|uk|in|vn>&hl=en&q=…",
            "query": out}


def domanda_sede(L, dom):
    sugg = sorted({s for v in dom["query"].values() for s in (v or []) if "dtv" in s.lower()})
    pat = re.compile(r"\b(" + "|".join(re.escape(k) for k in L["chiavi"]) + r")\b", re.I)
    # esclusi i suggerimenti su altri visti chiamati "DTV" o "digital nomad" (es. "dtv nomad visa spain": il visto per nomadi spagnolo)
    return [s for s in sugg if pat.search(s) and not re.search(r"nomad visa|dtv nomad", s, re.I)]


def main():
    oggi = date.today().isoformat()
    errori = []
    sedi = elenco_sedi()
    if len(sedi) < 80:
        errori.append(f"elenco delle sedi troppo corto: {len(sedi)}")
    with cf.ThreadPoolExecutor(8) as ex:
        sedi = list(ex.map(stato_sito, sedi))
    # pagine DTV
    tutte = sorted({u for L in LETTURE for u in L["pagine"]} | {g["url"] for g in GENERALE.values()})
    with cf.ThreadPoolExecutor(8) as ex:
        lette = {r["url"]: r for r in ex.map(leggi, tutte)}
    for u, r in lette.items():
        if not r["ok"]:
            errori.append(f"pagina non leggibile (HTTP {r['http']}): {u}")
    def controlla(L, campo, voce, chiave="frammento"):
        pag = lette.get(L["pagine"][voce.get("p", 0)], {})
        if voce[chiave] not in pag.get("_testo", ""):
            errori.append(f"{L['id']}: {campo} — frammento non trovato in {pag.get('url')}: {voce[chiave]!r}")
    for L in LETTURE:
        for campo in ("costo", "residenza", "saldo"):
            if campo in L:
                controlla(L, campo, L[campo])
                if "frammento2" in L[campo]:
                    controlla(L, campo, L[campo], "frammento2")
        for a in L.get("altre", []):
            controlla(L, "altre", a)
        if not any(re.search(r"\bDTV\b|Destination Thailand", (lette.get(u, {}).get("titolo", "") + " " + lette.get(u, {}).get("_testo", "")[:20000]), re.I)
                   for u in L["pagine"]):
            errori.append(f"{L['id']}: nessuna pagina parla più del DTV")
    for k, g in GENERALE.items():
        for f in g["frammenti"]:
            if f not in lette.get(g["url"], {}).get("_testo", ""):
                errori.append(f"{k}: frammento non trovato in {g['url']}: {f!r}")
    # annuncio del Dipartimento degli affari consolari (pagina in thailandese: si controlla solo il titolo e la data)
    a_st, a_t = get(ANNUNCIO_MFA)
    a_d = dati_pagina(a_t) if a_st == 200 else None
    if not a_d or "Destination Thailand Visa (DTV)" not in (a_d.get("name") or a_d.get("title") or "") or not (a_d.get("date") or "").startswith("2026-08-28"):
        errori.append("annuncio del Dipartimento degli affari consolari (28/8/2026) non trovato o cambiato")
    # domanda
    vecchio = json.loads(USCITA.read_text(encoding="utf-8")) if USCITA.exists() else {}
    dom = nuova_domanda() if "--domanda" in sys.argv else vecchio.get("domanda")
    if not dom:
        errori.append("domanda: nessun dato di autocompletamento (lanciare con --domanda)")
    # coerenza delle sedi lette con l'elenco ufficiale
    host = {re.match(r"https?://([^/]+)", s["sito"]).group(1).replace("www.", "") for s in sedi}
    for L in LETTURE:
        h = re.match(r"https?://([^/]+)", L["pagine"][0]).group(1)
        if h not in host:
            errori.append(f"{L['id']}: sito {h} non più nell'elenco ufficiale delle sedi")
    if len({L["id"] for L in LETTURE}) != len(LETTURE):
        errori.append("id delle sedi doppi")
    if errori:
        print("ERRORI: il file dei dati NON è stato aggiornato")
        for x in errori[:80]:
            print(" -", x)
        sys.exit(1)
    letture = []
    for L in LETTURE:
        voce = {k: v for k, v in L.items() if k != "chiavi"}
        voce["pagine"] = [{k: v for k, v in lette[u].items() if not k.startswith("_")} for u in L["pagine"]]
        voce["domanda"] = domanda_sede(L, dom) if dom else []
        voce["sito"] = re.match(r"https?://[^/]+", L["pagine"][0]).group(0)
        letture.append(voce)
    lette_h = {re.match(r"https?://([^/]+)", L["pagine"][0]).group(1) for L in LETTURE}
    for s in sedi:
        s["dtv"] = re.match(r"https?://([^/]+)", s["sito"]).group(1).replace("www.", "") in lette_h
    contenuto = {"sedi": sedi, "letture": letture,
                 "generale": {k: {"url": g["url"], "frammenti": g["frammenti"], "modificata": lette[g["url"]]["modificata"], "sha256": lette[g["url"]]["sha256"]}
                              for k, g in GENERALE.items()}}
    uscita = {"_nota": "Generato da raccolta/dtv.py: non modificare a mano (i valori letti a mano stanno in LETTURE dentro lo script). "
                       "Fonte: siti delle ambasciate e dei consolati generali thailandesi (Ministero degli Esteri thailandese), letti il giorno indicato.",
              "generato_il": oggi, "letto_il": oggi,
              "impronta": hashlib.sha256(json.dumps(contenuto, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20],
              "fonti": {"elenco": {"url": ELENCO, "titolo": "Thai Embassy and Consulates (Ministry of Foreign Affairs of Thailand)", "letto_il": oggi},
                        "annuncio_mfa": {"url": ANNUNCIO_MFA, "titolo": (a_d.get("name") or a_d.get("title") or "").strip(), "data": (a_d.get("date") or "")[:10],
                                         "editore": "Department of Consular Affairs, Ministry of Foreign Affairs of Thailand", "letto_il": oggi},
                        "evisa": {"url": EVISA, "titolo": "Thai e-Visa (official website)"}},
              "domanda": dom, **contenuto}
    USCITA.write_text(json.dumps(uscita, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    con_pag = [L["id"] for L in letture if L["domanda"] and ("costo" in L or "residenza" in L)]
    print(f"Scritto {USCITA}: {len(sedi)} sedi nell'elenco ufficiale ({sum(1 for s in sedi if s['http'] == 200)} con la home in HTTP 200), "
          f"{len(letture)} con la pagina DTV letta ({sum(1 for L in letture if 'costo' in L)} con il costo, "
          f"{sum(1 for L in letture if 'residenza' in L)} con la regola sulla residenza); sedi con domanda e dati: {len(con_pag)} {con_pag}; impronta {uscita['impronta']}.")


if __name__ == "__main__":
    main()
