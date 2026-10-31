"""Legge le fonti ufficiali sulla residenza in Messico (costi dei permessi, UMA, Lineamientos e pagine dei consolati) e scrive
visaincome/dati/mexico.json (sezione "Mexico residency" del sito, dal 31/10/2026).

Uso (dalla radice del repository):
    python3 visaincome/raccolta/mexico.py              # rilegge le fonti e scrive il JSON (domanda: quella già salvata)
    python3 visaincome/raccolta/mexico.py --domanda    # rifà anche l'autocompletamento di Google (gl=us, circa 30 secondi)

Fonti (lette A MANO il 31/10/2026; ogni valore in LETTURE ha il FRAMMENTO del testo ufficiale da cui viene)
- Ley Federal de Derechos (LFD), testo vigente della Cámara de Diputados (PDF): art. 8 (documento migratorio: residente
  temporal 1-4 anni, residente permanente, reposición, riduzione del 50%), art. 9 (cambio di condizione), art. 22 (visto
  consolare). Il PDF dice che le cifre per il 2026 sono quelle aggiornate dalla Resolución Miscelánea Fiscal (DOF 28/12/2025).
- DOF 07/11/2025, decreto che riforma la LFD (importi dell'art. 8 per il 2026; entrata in vigore 1/1/2026).
- DOF 28/12/2025, Anexo 4 della Resolución Miscelánea Fiscal 2026: "Cantidades actualizadas establecidas en la LFD para 2026",
  cuota "sin ajuste" e "con ajuste" (arrotondata: è quella che si paga).
- INEGI, comunicato 1/26 dell'8/1/2026: UMA 2026 (117.31 pesos al giorno) in vigore dal 1/2/2026.
- DOF 25/07/2025, Lineamientos generales para la expedición de visas (SEGOB e SRE), Trámite 5 (residencia temporal) e
  Trámite 7 (residencia permanente): solvenza in "días en UMA" (680 / 11.460; 1.140 / 45.850; 220 per familiare).
- Consolati: pagine o PDF ufficiali (consulmex.sre.gob.mx) con la cifra in USD, CAD, GBP o MXN. Per ogni pagina si salvano
  data della pagina (data del PDF o "Última actualización"), impronta SHA-256 del testo e risposta HTTP.
  Un consolato entra solo se la sua pagina ufficiale scrive la cifra (nessuna cifra ricavata da noi) e la pagina è del 2026
  (o, se non ha data, usa le cifre dell'UMA 2026).

Regole
- Se un frammento non è più nel testo, la pagina è cambiata: il JSON NON viene aggiornato (esce con codice 1) finché qualcuno
  non rilegge la pagina e aggiorna LETTURE o CONSOLATI.
- Se una pagina di consolato non si può leggere (errore, 403, pagina di verifica anti-bot del sito SRE), lo script usa la copia
  già salvata in raccolta/_grezzi/mexico/ (scaricata in un lancio precedente) e lo scrive in "copia_salvata"; senza copia si ferma.
  Non si cerca di aggirare la verifica anti-bot: si riprova un altro giorno.
- Controlli incrociati: importi dell'Anexo 4 = importi della LFD e del decreto; UMA mensile = diaria × 30,4; la tabella del
  consolato di Londra (pesos) = giorni × UMA 2026.
Nessun testo copiato per intero: si pubblicano fatti brevi (importi, condizioni) con il link alla pagina ufficiale.
"""
import hashlib
import html as H
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
USCITA = RADICE / "dati" / "mexico.json"
GREZZI = RADICE / "raccolta" / "_grezzi" / "mexico"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"}

FONTI = {
    "lfd": {"url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LFD.pdf", "tipo": "pdf", "editore": "Cámara de Diputados",
            "titolo": "Ley Federal de Derechos (current text)"},
    "decreto": {"url": "https://dof.gob.mx/nota_detalle.php?codigo=5772360&fecha=07/11/2025", "tipo": "html", "editore": "Diario Oficial de la Federación",
                "titolo": "Decree amending the Ley Federal de Derechos (DOF, 7 November 2025)", "data": "2025-11-07"},
    "anexo4": {"url": "https://dof.gob.mx/nota_detalle.php?codigo=5777219&fecha=28/12/2025", "tipo": "html", "editore": "Diario Oficial de la Federación",
               "titolo": "Annex 4 of the 2026 Miscellaneous Tax Resolution: updated amounts of the Ley Federal de Derechos (DOF, 28 December 2025)",
               "data": "2025-12-28"},
    "uma": {"url": "https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2026/uma/uma2026.pdf", "tipo": "pdf", "editore": "INEGI",
            "titolo": "UMA 2026, press release 1/26 (8 January 2026)", "data": "2026-01-08"},
    "lineamientos": {"url": "https://dof.gob.mx/nota_detalle.php?codigo=5763837&fecha=25/07/2025", "tipo": "html", "editore": "Diario Oficial de la Federación",
                     "titolo": "Lineamientos generales para la expedición de visas (SEGOB and SRE, DOF, 25 July 2025)", "data": "2025-07-25"},
}
PAGINA_INEGI = "https://www.inegi.org.mx/temas/uma/"   # tabella UMA (pagina con JavaScript): solo come link

# valore + fonte + frammento (testo normalizzato: spazi compattati, puntini di riempimento tolti)
LETTURE = {
    "nota_2026": {"valore": "2025-12-28", "fonte": "lfd", "frammento": "Cantidades actualizadas por Resolución Miscelánea Fiscal DOF 28-12-2025"},
    "rt_1": {"valore": 11140.74, "fonte": "lfd", "frammento": "a). Hasta un año $11,140.74"},
    "rt_2": {"valore": 16693.36, "fonte": "lfd", "frammento": "b). Dos años $16,693.36"},
    "rt_3": {"valore": 21142.58, "fonte": "lfd", "frammento": "c). Tres años $21,142.58"},
    "rt_4": {"valore": 25057.82, "fonte": "lfd", "frammento": "d). Cuatro años $25,057.82"},
    "rp": {"valore": 13578.96, "fonte": "lfd", "frammento": "VII. Residente Permanente $13,578.96"},
    "reposicion": {"valore": 1779.93, "fonte": "lfd", "frammento": "Respecto a las fracciones II, V, VI y VII la cuota aplicable será de $1,779.93"},
    "renovacion": {"valore": True, "fonte": "lfd", "frammento": "Por la renovación de los documentos a que se refieren las fracciones II a VII de este artículo, se pagará la misma cuota del derecho según corresponda."},
    "cambio": {"valore": 1847.13, "fonte": "lfd", "frammento": "la autorización del cambio de condición de estancia se pagará el derecho conforme a la cuota de $1,847.13"},
    "mitad": {"valore": True, "fonte": "lfd",
              "frammento": "pagarán el 50% de las cuotas que les correspondan conforme a las citadas disposiciones, siempre que acrediten ante el Instituto Nacional de Migración "
                           "que su estancia en el país obedece a la preservación de la unidad familiar, oferta de empleo"},
    "visa": {"valore": 990.79, "fonte": "lfd", "frammento": "expedición de las visas ordinarias en pasaportes extranjeros $990.79"},
    "dec_rt_1": {"valore": 11140.74, "fonte": "decreto", "frammento": "a). Hasta un año $11,140.74"},
    "dec_rt_4": {"valore": 25057.82, "fonte": "decreto", "frammento": "d). Cuatro años $25,057.82"},
    "dec_rp": {"valore": 13578.96, "fonte": "decreto", "frammento": "VII. Residente Permanente $13,578.96"},
    "dec_vigore": {"valore": "2026-01-01", "fonte": "decreto", "frammento": "El presente Decreto entrará en vigor a partir del 1 de enero de 2026"},
    "a4_titolo": {"valore": True, "fonte": "anexo4", "frammento": "Cantidades actualizadas establecidas en la LFD para 2026"},
    "a4_rt": {"valore": {"1": [11140.74, 11141], "2": [16693.36, 16693], "3": [21142.58, 21143], "4": [25057.82, 25058]}, "fonte": "anexo4",
              "frammento": "VI a) $11,140.74 $11,141 VI b) $16,693.36 $16,693 VI c) $21,142.58 $21,143 VI d) $25,057.82 $25,058"},
    "a4_rp": {"valore": [13578.96, 13579], "fonte": "anexo4", "frammento": "VII $13,578.96 $13,579"},
    "a4_repos": {"valore": [1779.93, 1780], "fonte": "anexo4", "frammento": "Respecto a las fracciones II, V, VI y VII... $1,779.93 $1,780"},
    "a4_cambio": {"valore": [1847.13, 1847], "fonte": "anexo4", "frammento": "Artículo 9 $1,847.13 $1,847"},
    "a4_visa": {"valore": [990.79, 990], "fonte": "anexo4", "frammento": "III d) $990.79 $990"},
    "uma_diaria": {"valore": 117.31, "fonte": "uma", "frammento": "Diario 117.31 pesos mexicanos"},
    "uma_mensile": {"valore": 3566.22, "fonte": "uma", "frammento": "Mensual 3 566.22 pesos mexicanos"},
    "uma_annua": {"valore": 42794.64, "fonte": "uma", "frammento": "Anual 42 794.64 pesos mexicanos"},
    "uma_dal": {"valore": "2026-02-01", "fonte": "uma", "frammento": "Los valores de la UMA que entrarán en vigor a partir del 1 de febrero de 2026 son"},
    "rt_saldo_giorni": {"valore": 11460, "fonte": "lineamientos",
                        "frammento": "cuentas bancarias con saldo promedio mensual equivalente a once mil cuatrocientos sesenta días en UMA, durante los últimos doce meses; o 2. "
                                     "Original de los documentos que demuestren que cuenta con empleo o pensión con ingresos mensuales libres de gravámenes mayores al equivalente "
                                     "de seiscientos ochenta días en UMA durante los últimos seis meses."},
    "rt_reddito_giorni": {"valore": 680, "fonte": "lineamientos", "frammento": "mayores al equivalente de seiscientos ochenta días en UMA durante los últimos seis meses"},
    "rt_tramite": {"valore": True, "fonte": "lineamientos", "frammento": "Trámite 5 Visa de Residencia Temporal"},
    "rp_saldo_giorni": {"valore": 45850, "fonte": "lineamientos",
                        "frammento": "a. Jubilados o pensionados: 1. Original o documento electrónico con certificado digital de comprobante de inversiones o cuentas bancarias "
                                     "con saldo promedio mensual equivalente a cuarenta y cinco mil ochocientos cincuenta días en UMA, durante los últimos doce meses"},
    "rp_reddito_giorni": {"valore": 1140, "fonte": "lineamientos",
                          "frammento": "cuenta con pensión con ingresos mensuales libres de gravámenes mayores al equivalente de mil ciento cuarenta días en UMA, durante los últimos seis meses"},
    "rp_tramite": {"valore": True, "fonte": "lineamientos", "frammento": "Trámite 7 Visa de Residencia Permanente"},
    "familiare_giorni": {"valore": 220, "fonte": "lineamientos",
                         "frammento": "Acreditar solvencia económica para la manutención de cada uno de sus familiares durante su estancia en el país, con: – Original o documento "
                                      "electrónico con certificado digital de comprobante de inversiones o cuentas bancarias con saldo promedio mensual equivalente a doscientos "
                                      "veinte días en UMA"},
    "lin_vigore": {"valore": 15, "fonte": "lineamientos",
                   "frammento": "Los presentes Lineamientos entrarán en vigor a los quince días naturales siguientes al de su publicación en el Diario Oficial de la Federación."},
    "lin_abroga": {"valore": True, "fonte": "lineamientos", "frammento": "Se abrogan los Lineamientos Generales para la expedición de visas que emiten las secretarías de Gobernación y de Relaciones Exteriores , publicados en el Diario Oficial de la Federación el 10 de octubre de 2014"},
}

# Consolati letti il 31/10/2026. pagine: URL (indice "p" nei frammenti); "layout": PDF letto con pdftotext -layout (tabelle).
# tr / pr: residenza temporanea / permanente; reddito = reddito mensile netto (6 mesi), saldo = saldo medio mensile (12 mesi).
# approssimato: la pagina scrive "approx." (Portland). chiavi: parole dei suggerimenti di ricerca che nominano la sede.
CONSOLATI = [
    {"id": "new-york", "sede": "New York", "paese": "United States", "tipo": "Consulate-General", "valuta": "USD",
     "pagine": [{"url": "https://consulmex.sre.gob.mx/nuevayork/images/2026_4_VisaResidenteTemporal.pdf"},
                {"url": "https://consulmex.sre.gob.mx/nuevayork/images/2026_6_VisaResidentePermanente.pdf"}],
     "tr": {"reddito": {"importo": 4200, "frammento": "recibos de sueldo con un ingreso mínimo de $4,200.00 USD", "p": 0},
            "saldo": {"importo": 71500, "frammento": "cuentas bancarias personales con un balance mínimo de $71,500.00 dólares, durante los últimos 12 meses", "p": 0}},
     "pr": {"reddito": {"importo": 7100, "frammento": "Carta de pensión con ingresos mensuales equivalentes a $7,100.00 dólares, durante los últimos 6 meses", "p": 1},
            "saldo": {"importo": 286100, "frammento": "saldo promedio mensual equivalentes a $286,100.00 dólares, durante los últimos 12 meses", "p": 1}},
     "tassa": {"importo": 56, "valuta": "USD", "frammento": "Costo por aplicación $56.00 USD en efectivo", "p": 0},
     "chiavi": ["new york", "nyc"]},
    {"id": "new-brunswick", "sede": "New Brunswick, NJ", "paese": "United States", "tipo": "Consulate", "valuta": "USD",
     "pagine": [{"url": "https://consulmex.sre.gob.mx/new-brunswick/images/visas-es-2026/TEMPORARY_RESIDENT.pdf"},
                {"url": "https://consulmex.sre.gob.mx/new-brunswick/images/visas-es-2026/PERMANENT_RESIDENT_VISA.pdf"}],
     "tr": {"reddito": {"importo": 4500, "frammento": "a job or pension that yields a monthly income of $4,500.00 USD after taxes during the previous 6 months", "p": 0},
            "saldo": {"importo": 75500, "frammento": "with a monthly balance of at least $75,500.00 USD during the previous 12 months", "p": 0}},
     "pr": {"reddito": {"importo": 7500, "frammento": "a job or pension that yields a monthly income of $7,500.00 USD after taxes during the previous 6 months", "p": 1},
            "saldo": {"importo": 301500, "frammento": "with a monthly balance of at least $301,500.00 USD during the previous 12 months", "p": 1}},
     "tassa": {"importo": 56, "valuta": "USD", "frammento": "Application processing fee $56.00 USD", "p": 0},
     "chiavi": ["new jersey", "new brunswick"]},
    {"id": "washington-dc", "sede": "Washington, DC", "paese": "United States", "tipo": "Embassy (consular section)", "valuta": "MXN",
     "pagine": [{"url": "https://consulmex.sre.gob.mx/washington/images/2026/visas/eng/Temporary_resident.pdf"},
                {"url": "https://consulmex.sre.gob.mx/washington/images/2026/visas/eng/Permanent_resident_visa_retiree.pdf"}],
     "tr": {"reddito": {"importo": 83640, "frammento": "a job or pension that yields a monthly income of $83,640.00 MXN after taxes during the previous 6 months", "p": 0},
            "saldo": {"importo": 1394000, "frammento": "with a monthly balance of at least $1,394,000.00 MXN during the previous 12 months", "p": 0}},
     "pr": {"reddito": {"importo": 139400, "frammento": "a pension that yields a monthly income of $139,400.00 MXN after taxes during the previous 6 months", "p": 1},
            "saldo": {"importo": 5576000, "frammento": "balance of at least $5,576,000.00 MXN during the previous 12 months", "p": 1}},
     "tassa": {"importo": 56, "valuta": "USD", "frammento": "Application processing fee $56.00 dollars", "p": 0},
     "altre": [{"frammento": "All amounts are calculated in Mexican pesos. You can consult the official exchange rate on the day of your appointment", "p": 0}],
     "chiavi": ["washington", "dc"]},
    {"id": "indianapolis", "sede": "Indianapolis", "paese": "United States", "tipo": "Consulate", "valuta": "USD",
     "pagine": [{"url": "https://consulmex.sre.gob.mx/indianapolis/images/Visas/6_TEMPORARY_RESIDENT.pdf"},
                {"url": "https://consulmex.sre.gob.mx/indianapolis/images/Visas/2_PERMANENT_RESIDENT.pdf"}],
     "tr": {"reddito": {"importo": 4431, "frammento": "a job or pension that yields a monthly income of $4,431.00 US Dollars after taxes during the previous 6 months", "p": 0},
            "saldo": {"importo": 74687, "frammento": "with a balance of at least $74,687.00 US Dollars during the previous 12 months", "p": 0}},
     "pr": {"reddito": {"importo": 7429, "frammento": "a pension that yields a monthly income of $7,429.00 US Dollars, after taxes, during the last previous 6 months", "p": 1},
            "saldo": {"importo": 298814, "frammento": "with a balance of at least $298,814.00 US Dollars during the previous 12 months", "p": 1}},
     "tassa": {"importo": 56, "valuta": "USD", "frammento": "Application processing fee $56.00 Dollars", "p": 0},
     "chiavi": ["indianapolis", "indiana"]},
    {"id": "san-diego", "sede": "San Diego", "paese": "United States", "tipo": "Consulate-General", "valuta": "USD",
     "pagine": [{"url": "https://consulmex.sre.gob.mx/sandiego/images/visasingles2026/5a_Temporary_Resident_Visa_-_Economic_Solvency.pdf"},
                {"url": "https://consulmex.sre.gob.mx/sandiego/images/visasingles2026/7a_Permanent_Resident_Visa_Retirement"}],
     "tr": {"reddito": {"importo": 4510, "frammento": "prove an income of at least $4,510.00 USD per month through employment or pension for the previous six months", "p": 0},
            "saldo": {"importo": 75950, "frammento": "proving a minimum monthly balance of at least $75,950.00 USD for the previous twelve months", "p": 0}},
     "pr": {"reddito": {"importo": 7560, "frammento": "prove an income of at least $7,560.00 USD per month through a pension for the previous six months", "p": 1},
            "saldo": {"importo": 303880, "frammento": "proving a minimum monthly balance of at least $303,880.00 USD for the previous twelve months", "p": 1}},
     "tassa": {"importo": 56, "valuta": "USD", "frammento": "Non-refundable processing fee: $56.00 USD (cash only)", "p": 0},
     "chiavi": ["san diego"]},
    {"id": "las-vegas", "sede": "Las Vegas", "paese": "United States", "tipo": "Consulate", "valuta": "USD",
     "pagine": [{"url": "https://consulmex.sre.gob.mx/lasvegas/images/2026/VISAS2026/TemporaryResidenceVisa2026"}],
     "tr": {"reddito": {"importo": 4630, "frammento": "Bank statements for the last 6 months with a monthly income of at least $ 4,630 USD per person", "p": 0},
            "saldo": {"importo": 78025, "frammento": "bank statements for the last 12 months with a monthly minimum balance of at least $78,025 USD per person", "p": 0}},
     "tassa": {"importo": 56, "valuta": "USD", "frammento": "Visa fee: $56 USD", "p": 0},
     "altre": [{"frammento": "average monthly balance equivalent to $ 1,498 USD for the last twelve months", "p": 0, "nota": "per family member"}],
     "chiavi": ["las vegas", "vegas"]},
    {"id": "portland", "sede": "Portland", "paese": "United States", "tipo": "Consulate", "valuta": "USD", "approssimato": True,
     "pagine": [{"url": "https://consulmex.sre.gob.mx/portland/index.php/tramites/7-servicios/63-temporary-residents-without-authorization-for-lucrative-activities-visa"}],
     "tr": {"reddito": {"importo": 4500, "frammento": "a monthly income of at least 680 days in UMA* funds (approx. $4,500 USD) after taxes", "p": 0},
            "saldo": {"importo": 75000, "frammento": "monthly ending balance of at least 11,460 days in UMA* funds (approx. $75,000 USD)", "p": 0}},
     "tassa": {"importo": 56, "valuta": "USD", "frammento": "authorization and printing of visa - $56.00 USD", "p": 0},
     "altre": [{"frammento": "within the following 30 calendar days from their entry into the national territory, the residence card", "p": 0}],
     "chiavi": ["portland", "oregon"]},
    {"id": "london", "sede": "London", "paese": "United Kingdom", "tipo": "Embassy (consular section)", "valuta": "GBP",
     "pagine": [{"url": "https://consulmex.sre.gob.mx/reinounido/images/2022/Equivalencechart.pdf", "layout": True},
                {"url": "https://consulmex.sre.gob.mx/reinounido/index.php/es/contenido/96-rentista-visitor-carnet-visa"},
                {"url": "https://consulmex.sre.gob.mx/reinounido/index.php/es/contenido/265-Permanent-Residence-Visa-by-economic-solvency"}],
     "tr": {"reddito": {"importo": 3425.91, "frammento": "680 $79,770.80 £3,425.91", "p": 0},
            "saldo": {"importo": 57736.77, "frammento": "11460 $1,344,372.60 £57,736.77", "p": 0}},
     "pr": {"reddito": {"importo": 5743.44, "frammento": "1140 $133,733.40 £5,743.44", "p": 0},
            "saldo": {"importo": 230997.46, "frammento": "45850 $5,378,663.50 £230,997.46", "p": 0}},
     "altre": [{"frammento": "Exchange rate for Mexican peso to British pound sterling: .042947 Source: HSBC 30th January 2026", "p": 0},
               {"frammento": "from the 1st February 2026 the daily wage in UMA is $117.31", "p": 0},
               {"frammento": "monthly income free of taxes greater than the equivalent of 680 UMA days", "p": 1},
               {"frammento": "average monthly balance equivalent to 11460 UMA days", "p": 1},
               {"frammento": "monthly income free of taxes greater than the equivalent of 1140 UMA days", "p": 2},
               {"frammento": "average monthly balance equivalent to 45850 UMA days", "p": 2}],
     "chiavi": ["london", "uk", "united kingdom"]},
    {"id": "vancouver", "sede": "Vancouver", "paese": "Canada", "tipo": "Consulate-General", "valuta": "CAD",
     "pagine": [{"url": "https://consulmex.sre.gob.mx/vancouver/index.php/es/temporary-resident-visa"}],
     "tr": {"reddito": {"importo": 6461, "frammento": "a monthly tax-free income of over $6,461.00 Canadian dollars during the past six months", "p": 0},
            "saldo": {"importo": 108894, "frammento": "an average monthly balance of $108,894.00 Canadian dollars during the past twelve months", "p": 0}},
     "altre": [{"frammento": "average monthly balance of $2,090.00 Canadian dollars during the past twelve months", "p": 0, "nota": "per family member"}],
     "chiavi": ["vancouver", "canada", "canadian", "canadians"]},
    {"id": "montreal", "sede": "Montreal", "paese": "Canada", "tipo": "Consulate-General", "valuta": "CAD",
     "pagine": [{"url": "https://consulmex.sre.gob.mx/montreal/index.php/es/extranjeros/visas/345-visas-7"},
                {"url": "https://consulmex.sre.gob.mx/montreal/index.php/es/extranjeros/visas/346-visas-8"}],
     "tr": {"reddito": {"importo": 6460, "frammento": "ingresos mensuales libres de impuestos por un monto superior a 6460 $ CAD durante los últimos seis meses", "p": 0},
            "saldo": {"importo": 108856, "frammento": "saldo promedio mensual superior a 108 856 $ CAD durante los últimos doce meses", "p": 0}},
     "pr": {"reddito": {"importo": 10829, "frammento": "ingresos mensuales provenientes de pensiones por 10 829 $CAD durante los últimos seis meses", "p": 1},
            "saldo": {"importo": 435520, "frammento": "saldo promedio mensual equivalente a 435 520 $ CAD durante los últimos doce meses", "p": 1}},
     "altre": [{"frammento": "superior a $25 808 MXP o el equivalente a 2, 090 $ CAD", "p": 0, "nota": "25,808 pesos = 220 × UMA 2026 (117.31)"}],
     "chiavi": ["montreal", "quebec", "canada", "canadian", "canadians"]},
]

# Pagine lette ma non usate (31/10/2026): cifre di anni passati o pagina non leggibile. Si elencano nel sito senza cifre.
ESCLUSI = [
    {"sede": "Chicago", "url": "https://consulmex.sre.gob.mx/chicago/index.php/component/content/article?id=88",
     "motivo": "vecchia", "data": "2017-03-13", "nota": "page last updated on 13 March 2017"},
    {"sede": "Detroit", "url": "https://consulmex.sre.gob.mx/detroit/index.php/visas-and-other-information-for-foreigners/visas-en-espanol",
     "motivo": "vecchia", "data": "2025-01-13", "nota": "page last updated on 13 January 2025"},
    {"sede": "Orlando", "url": "https://consulmex.sre.gob.mx/orlando/images/pdfs/Temporary_Resident_Visa_Economic_Solvency24.pdf",
     "motivo": "vecchia", "data": "2024-01-21", "nota": "PDF dated 21 January 2024"},
    {"sede": "El Paso", "url": "https://consulmex.sre.gob.mx/elpaso/images/2025/Julio/visasingles/TEMPORARY_RESIDENT_MORE_THAN_180_DAYS.pdf",
     "motivo": "vecchia", "data": "2025-07-25", "nota": "PDF dated 25 July 2025"},
    {"sede": "Saint Paul", "url": "https://consulmex.sre.gob.mx/saintpaul/index.php/se/visesp/5-seccion/235-residente-temporal",
     "motivo": "bloccata", "nota": "the website's bot check did not let our reader through"},
    {"sede": "Madrid (embassy in Spain)", "url": "https://embamex.sre.gob.mx/espana/index.php/visas/5-secconsular/catavisos/540-residente-temporal-por-solvencia-economica",
     "motivo": "bloccata", "nota": "the website's bot check did not let our reader through"},
    {"sede": "Ottawa (embassy in Canada)", "url": "https://embamex.sre.gob.mx/canada/index.php/en/sconeng/11354-temporary-resident-visa",
     "motivo": "bloccata", "nota": "the website's bot check did not let our reader through"},
]

QUERY = ["mexico temporary residency income requirements 2026", "mexico temporary residency income requirements", "mexico residency fees",
         "mexico residency fees 2026", "mexico temporary residency", "mexico permanent residency", "mexico residency income requirements",
         "mexico temporary resident visa", "mexico residency requirements", "mexico residency consulate", "mexican consulate temporary residency",
         "mexico temporary residency fees", "mexico permanent residency income requirements", "mexico retirement visa income",
         "mexico temporary residency cost", "mexico temporary residency financial requirements", "mexico residency calculator", "mexico residency uma"]


def norm(t):
    t = H.unescape(t).replace(" ", " ").replace(" ", " ")
    t = re.sub(r"(?:\s*\.){4,}", " ", t)   # puntini di riempimento della LFD
    return re.sub(r"\s+", " ", t).strip()


def scarica(u):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90)
        return r.status, r.read()
    except Exception as e:  # noqa: BLE001
        return getattr(e, "code", 0) or 0, b""


def testo_di(b, layout=False):
    if b[:4] == b"%PDF":
        p = subprocess.run(["pdftotext"] + (["-layout"] if layout else []) + ["-", "-"], input=b, capture_output=True)
        info = subprocess.run(["pdfinfo", "-"], input=b, capture_output=True).stdout.decode("utf-8", "replace")
        m = re.search(r"ModDate:\s*(.+)", info) or re.search(r"CreationDate:\s*(.+)", info)
        data = ""
        if m:
            try:
                data = datetime.strptime(m.group(1).strip(), "%a %b %d %H:%M:%S %Y %Z").date().isoformat()
            except ValueError:
                data = ""
        return norm(p.stdout.decode("utf-8", "replace")), data, "pdf"
    s = b.decode("utf-8", "replace")
    s = re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", " ", s)
    t = norm(re.sub(r"<[^>]+>", " ", s))
    mesi = {"Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8, "Septiembre": 9,
            "Octubre": 10, "Noviembre": 11, "Diciembre": 12}
    m = re.search(r"Última actualización: (\d{1,2}) ([A-Z][a-z]+) (\d{4})", t)
    data = f"{m.group(3)}-{mesi[m.group(2)]:02d}-{int(m.group(1)):02d}" if m and m.group(2) in mesi else ""
    return t, data, "html"


def bloccata(t):
    return "Radware" in t[:400] or "your activity and behavior on this site made us think that you are a bot" in t


def leggi(u, layout=False, oggi=""):
    """Scarica u; se non si legge, usa la copia salvata in _grezzi (se c'è). -> (meta, testo) o (None, motivo)."""
    GREZZI.mkdir(parents=True, exist_ok=True)
    nome = hashlib.md5(u.encode()).hexdigest()[:12]
    st, b = scarica(u)
    copia = False
    if st == 200 and b:
        t, data, tipo = testo_di(b, layout)
        if bloccata(t):
            st, b = 0, b""
        else:
            (GREZZI / nome).write_bytes(b)
            (GREZZI / (nome + ".json")).write_text(json.dumps({"url": u, "scaricato_il": oggi}), encoding="utf-8")
    if not (st == 200 and b):
        if not (GREZZI / nome).exists():
            return None, f"non leggibile (HTTP {st}) e nessuna copia salvata: {u}"
        b = (GREZZI / nome).read_bytes()
        copia = json.loads((GREZZI / (nome + ".json")).read_text(encoding="utf-8"))["scaricato_il"]
        st = 200
    t, data, tipo = testo_di(b, layout)
    meta = {"url": u, "http": st, "formato": tipo, "data_pagina": data, "sha256": hashlib.sha256(t.encode("utf-8")).hexdigest()}
    if copia:
        meta["copia_salvata"] = copia
    return meta, t


def autocompleta(q, gl="us"):
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
    for q in QUERY:
        out[f"us|{q}"] = autocompleta(q)
        time.sleep(0.3)
    return {"data": date.today().isoformat(), "metodo": "https://suggestqueries.google.com/complete/search?client=firefox&gl=us&hl=en&q=…", "query": out}


def main():
    oggi = date.today().isoformat()
    errori, avvisi = [], []
    fonti, testi = {}, {}
    for k, f in FONTI.items():
        meta, t = leggi(f["url"], oggi=oggi)
        if meta is None:
            errori.append(f"fonte {k}: {t}")
            continue
        meta.update({kk: f[kk] for kk in ("editore", "titolo") if kk in f})
        meta["data"] = f.get("data", meta["data_pagina"])
        meta["letto_il"] = meta.get("copia_salvata") or oggi
        fonti[k], testi[k] = meta, t
    for k, v in LETTURE.items():
        if v["frammento"] not in testi.get(v["fonte"], ""):
            errori.append(f"{k}: frammento non trovato in {v['fonte']}: {v['frammento'][:120]!r}")
    L = {k: v["valore"] for k, v in LETTURE.items()}
    # controlli incrociati
    for n in "1234":
        if L["a4_rt"][n][0] != L[f"rt_{n}"]:
            errori.append(f"Anexo 4 e LFD diversi per la residenza temporanea di {n} anni")
        if round(L["a4_rt"][n][0]) != L["a4_rt"][n][1]:
            errori.append(f"Anexo 4: importo con ajuste non arrotondato dall'importo sin ajuste ({n} anni)")
    if (L["a4_rp"][0], L["a4_repos"][0], L["a4_cambio"][0], L["a4_visa"][0]) != (L["rp"], L["reposicion"], L["cambio"], L["visa"]):
        errori.append("Anexo 4 e LFD diversi (permanente, reposición, cambio o visto)")
    if (L["dec_rt_1"], L["dec_rt_4"], L["dec_rp"]) != (L["rt_1"], L["rt_4"], L["rp"]):
        errori.append("decreto del 7/11/2025 e LFD diversi")
    if round(L["uma_diaria"] * 30.4, 2) != L["uma_mensile"] or round(L["uma_mensile"] * 12, 2) != L["uma_annua"]:
        errori.append("UMA: mensile ≠ diaria × 30,4 o annua ≠ mensile × 12")
    consolati = []
    vecchio = json.loads(USCITA.read_text(encoding="utf-8")) if USCITA.exists() else {}
    for C in CONSOLATI:
        pag, tx = [], []
        for P in C["pagine"]:
            meta, t = leggi(P["url"], P.get("layout", False), oggi)
            if meta is None:
                errori.append(f"{C['id']}: {t}")
                meta, t = {"url": P["url"], "http": 0}, ""
            if meta.get("copia_salvata"):
                avvisi.append(f"{C['id']}: pagina non leggibile oggi, usata la copia del {meta['copia_salvata']}: {P['url']}")
            meta["letto_il"] = meta.get("copia_salvata") or oggi
            pag.append(meta)
            tx.append(t)
        voci = []
        for tipo in ("tr", "pr"):
            for cosa in ("reddito", "saldo"):
                if tipo in C and cosa in C[tipo]:
                    voci.append((f"{tipo}.{cosa}", C[tipo][cosa]))
        if "tassa" in C:
            voci.append(("tassa", C["tassa"]))
        voci += [(f"altre[{i}]", a) for i, a in enumerate(C.get("altre", []))]
        for nome, v in voci:
            if v["frammento"] not in tx[v["p"]]:
                errori.append(f"{C['id']} {nome}: frammento non trovato: {v['frammento'][:120]!r}")
        out = {k: C[k] for k in ("id", "sede", "paese", "tipo", "valuta", "tr", "pr", "tassa", "altre", "approssimato", "chiavi") if k in C}
        out["pagine"] = pag
        out["data_pagina"] = max((p.get("data_pagina") or "" for p in pag), default="")
        consolati.append(out)
    # Londra: la tabella del consolato (pesos) deve essere giorni × UMA 2026
    for C, out in zip(CONSOLATI, consolati):
        if C["id"] != "london":
            continue
        for gg, chiave in ((L["rt_reddito_giorni"], ("tr", "reddito")), (L["rt_saldo_giorni"], ("tr", "saldo")),
                           (L["rp_reddito_giorni"], ("pr", "reddito")), (L["rp_saldo_giorni"], ("pr", "saldo"))):
            pesos = f"${round(gg * L['uma_diaria'], 2):,.2f}"
            if f"{gg} {pesos} " not in C[chiave[0]][chiave[1]]["frammento"] + " ":
                errori.append(f"Londra: la riga {gg} giorni non è {pesos} (giorni × UMA)")
    # data della pagina: almeno del 2026, oppure (senza data) cifre in pesos dell'UMA 2026 nella pagina
    for out in consolati:
        if out["data_pagina"] and out["data_pagina"] < "2026-01-01":
            errori.append(f"{out['id']}: pagina del {out['data_pagina']}, prima del 2026: spostarla in ESCLUSI")
        if not out["data_pagina"] and not any("UMA 2026" in a.get("nota", "") for a in out.get("altre", [])):
            errori.append(f"{out['id']}: pagina senza data e senza un importo che leghi le cifre all'UMA 2026")
    dom = nuova_domanda() if "--domanda" in sys.argv else vecchio.get("domanda")
    if not dom:
        errori.append("domanda: nessun dato di autocompletamento (lanciare con --domanda)")
    for a in avvisi:
        print("AVVISO:", a)
    if errori:
        print("ERRORI: il file dei dati NON è stato aggiornato")
        for x in errori[:80]:
            print(" -", x)
        sys.exit(1)
    letture = {k: {"valore": v["valore"], "fonte": v["fonte"], "frammento": v["frammento"]} for k, v in LETTURE.items()}
    contenuto = {"letture": letture, "fonti": fonti, "consolati": consolati, "esclusi": ESCLUSI}
    uscita = {"_nota": "Generato da raccolta/mexico.py: non modificare a mano (i valori letti a mano stanno in LETTURE e CONSOLATI dentro lo script). "
                       "Fonti: DOF, Cámara de Diputados, INEGI, pagine ufficiali dei consolati del Messico (SRE), lette il giorno indicato.",
              "generato_il": oggi, "letto_il": oggi, "pagina_inegi": PAGINA_INEGI,
              "impronta": hashlib.sha256(json.dumps(contenuto, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20],
              "domanda": dom, **contenuto}
    USCITA.write_text(json.dumps(uscita, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"Scritto {USCITA}: {len(fonti)} fonti, {len(letture)} valori, {len(consolati)} consolati "
          f"(UMA {L['uma_diaria']}; residente temporale 1 anno {L['a4_rt']['1'][1]} pesos); impronta {uscita['impronta']}.")


if __name__ == "__main__":
    main()
