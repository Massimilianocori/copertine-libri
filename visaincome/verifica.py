"""Controlli prima di pubblicare Visa Income Checker.

Uso (dalla radice del repository, dopo python3 visaincome/genera.py):
    python3 visaincome/verifica.py

1. Esempi calcolati a mano (TEST.md): il motore Python deve dare esattamente il risultato atteso
   (cambi fissi BCE del 9 ottobre 2026, così il test non cambia ogni giorno).
2. Il motore JS (lo stesso testo che va nelle pagine) deve dare gli stessi importi, conversioni ed esiti del Python,
   sugli esempi e su 3.000 casi casuali, anche con valori fuori scala (serve node).
3. Nessun link interno rotto in sito/.
4. Ogni pagina di programma mostra la fonte ufficiale (URL) e la data del controllo sotto la cifra.
5. Nessun nome di modelli o servizi di intelligenza artificiale nei file del sito.
6. Le correzioni della revisione indipendente del 10/10/2026 sono presenti nelle pagine.
7. Sezione "Visa refusal rates": ogni tabella e ogni cifra principale hanno sotto la fonte ufficiale (URL) e la data;
   le percentuali principali ricalcolate qui da dati/rifiuti.json coincidono con le pagine; avviso, dicitura di affiliazione,
   niente EKTA/Travelpayouts; i link esterni della sezione rispondono (HTTP 200 o 206; si salta con --offline).
8. Sezione "Easiest Schengen visa" e visti UK di studio e lavoro.
9. Blocco "Other useful tools for your trip" in ogni pagina indicizzabile: gli stessi link di genera.ALTRI_SITI, nell'ordine,
   mai a questo sito, tutti rel="noopener" e senza nofollow o sponsored.
10. File chiave IndexNow.
11. Australia, Nuova Zelanda e Canada (26/10/2026): pagine di riepilogo in sitemap con licenza, fonte, avviso e JSON-LD Dataset;
    righe della tabella australiana = nazionalità con almeno 500 decisioni; cifre di India, Pakistan, Nigeria e Filippine ricalcolate
    da dati/rifiuti_altri.json; le pagine Schengen di Australia e Canada rimandano alle pagine delle destinazioni.
12. "Who moved where" (28/10/2026): pagine nazionalità × Paese = quelle con almeno 500 nel 2025 ricalcolate qui da dati/trasferimenti.json,
    tutte in sitemap e nessuna in più; titoli entro 70 caratteri con l'anno; numero principale, serie per anno e tabella per Paese
    uguali ai dati; fonte con data sotto ogni tabella; riquadro "what this number is"; JSON-LD; nessun link interno rotto nella sezione.
13. Sitemap: ogni URL ha un lastmod vero (data valida, non nel futuro, uguale al registro dati/lastmod.json), nessun URL doppio.
15. Visti Schengen a ingressi multipli (30/10/2026): pagina /visa-refusal-rates/multiple-entry-schengen-visa/ in sitemap, titolo entro 70
    caratteri con l'anno, prima frase con numero, fonte e data; tabelle per Stato e per Paese e riquadro di ogni pagina per Paese
    ricalcolati da dati/rifiuti.json (visti uniformi rilasciati e MEV), soglia 500 visti; link dall'indice e dalle pagine per Paese.
16. Test di inglese per i visti UK (SELT, 30/10/2026): ricalcolo da dati/selt.json (impronta, centri per città e per Paese, totali), pagine attese
    = indice + luoghi con domanda (tutte in sitemap, nessuna in più), titoli entro 70 caratteri, prima frase con numero, fonte e data,
    data del B2 solo con la fonte HC 1691 letta, nessun prezzo, link di affiliazione solo italki (ammesso, sponsored noopener, trasparenza).
17. Irlanda, PPS assegnati per nazionalità (30/10/2026): ricalcolo da dati/ppsn.json (impronta, pagine attese, numeri del primo paragrafo,
    tabelle mese per mese e anno per anno, confronto con gli stessi mesi, riquadro "what this number is", link dall'hub e colonna dell'indice);
    10 valori a caso ricontrollati sui CSV ufficiali con un lettore proprio.
18. Thailand DTV visa (30/10/2026): ricalcolo da dati/dtv.json (impronta, pagine attese = indice + sedi con domanda e dati, titoli ≤ 70,
    prima frase con data, righe della tabella = sedi lette con costo, regola e link ufficiale, frammenti citati, avviso, nessuna promessa,
    SafetyWing solo dopo le informazioni ufficiali e con la frase che l'assicurazione non è richiesta, link dal resto del sito);
    online, 10 frammenti a caso ricontrollati sulle pagine ufficiali riscaricate.
19. US OPT e STEM OPT (30/10/2026): ricalcolo da dati/opt.json (impronta), pagine attese (indice + 5) tutte in sitemap e nessuna in più,
    titoli ≤ 70, prima frase con fonte e data di lettura, cifre ufficiali presenti (tariffe I-765, premium processing, 90/60/30 giorni,
    90/150 giorni di disoccupazione), la proposta da 70.000 $ sempre come proposta, la regola dei 30 giorni come rinviata, link alle fonti,
    calcolatori presenti con le costanti dei dati, motore JS dei calcolatori uguale a un calcolo Python indipendente (casi fissi + 400 a caso),
    nessun link sponsorizzato; online: documenti del Federal Register e pagina I-765 di USCIS riletti (tipo, date, frammenti).
20. UK Graduate visa (30/10/2026): ricalcolo da dati/graduate.json (impronta), pagine attese (indice + 3), titoli ≤ 70, prima frase con fonte
    e data, durate (2 anni fino al 31/12/2026, 18 mesi dal 1/1/2027, 3 anni PhD), tariffa e IHS, tabelle dei costi ricalcolate, calcolatore,
    stesso confronto JS/Python, OGL; online: guida GOV.UK e Appendix Graduate rilette e frammenti ricontrollati.
21. Mexico residency (31/10/2026): ricalcolo da dati/mexico.json (impronta), pagine attese (indice + reddito + costi + una per consolato) tutte in
    sitemap e nessuna in più, titoli ≤ 70, prima frase con fonte e data di lettura, costi 2026 (Anexo 4 = LFD), calcolo UMA (giorni × UMA),
    tabella dei consolati e pagine per consolato con le cifre e i frammenti ufficiali, data della pagina del consolato, consolati esclusi,
    SafetyWing solo dopo le informazioni ufficiali e con la frase che non è un requisito, nessuna promessa, link dal resto del sito,
    costanti del calcolatore = dati e motore JS = calcolo Python indipendente (casi fissi + 400 a caso); online: 10 frammenti a caso
    riletti su LFD, Anexo 4, INEGI e Lineamientos (le pagine dei consolati non si rileggono qui: il sito SRE ha una verifica anti-bot).
22. Study in Italy (31/10/2026): ricalcolo da dati/studio_italia.json (impronta), pagine attese (indice + 5 pagine tematiche + una per ente DSU)
    tutte in sitemap e nessuna in più, titoli ≤ 70, prima frase con fonte e data di lettura, cifre nazionali (mezzi per il visto, borse minime,
    limiti ISEE/ISPE, costi del permesso ricalcolati, SSN), tabella degli enti e pagine per ente con limiti, importi, scadenze e frammenti dei
    bandi, elenco dei Paesi particolarmente poveri completo, tabella delle valute ricalcolata, esempio ISEE ricalcolato, enti non letti elencati,
    tutte le fonti citate, SafetyWing solo nella pagina dell'assicurazione e dopo le informazioni ufficiali, link dal resto del sito, costanti
    del calcolatore = dati e motore JS = calcolo Python indipendente (casi fissi + 400 a caso); online: 12 frammenti a caso riletti sulle fonti.
23. Italy 7% flat tax for foreign pensioners (31/10/2026): ricalcolo da dati/flat7.json (impronta), pagine attese (indice + regions) in sitemap
    e nessuna in più, titoli ≤ 70, prima frase con la fonte (Normattiva) prima della data di lettura, avviso fiscale e frase "decide l'Agenzia",
    nessuna promessa né elenco di Comuni consigliati, nessun link sponsorizzato, regole (30.000, 20.000 fino al 6/4/2026, 7%, 5 e 10 anni,
    1° gennaio dell'anno prima, art. 247 dal 1/1/2027), tabella delle regioni e Comuni vicini alla soglia ricalcolati da un calcolo indipendente,
    elenchi del sisma (Lazio, Marche, Umbria) con le cifre ISTAT, towns.json dello strumento = dati, motore JS dello strumento (preso dalla pagina)
    = Python su tutti i Comuni per i due anni e ricerca per nome esatto di ogni Comune, tutte le fonti citate, link dal resto del sito;
    online: 8 frammenti a caso riletti su Normattiva e Agenzia delle Entrate.
24. Schengen visa from the UK / from Dubai (31/10/2026): ricalcolo indipendente da dati/rifiuti.json (file della Commissione), dati/cambi.json
    e dati/schengen_residenti.json (impronta): pagine attese (2 hub + Stati con almeno 1.000 domande nel Paese) in sitemap e nessuna in più,
    titoli ≤ 70, prima frase con cifra ricalcolata, fonte (Commissione) e data; tabella dell'hub = tutti gli Stati del file nel Paese
    (tasso, anno prima, domande, non rilasciati, quota MEV) nell'ordine giusto; in ogni pagina di Stato cifre della prima frase, riquadro e righe
    dei consolati = ricalcolo; tassa e copertura in sterline (BCE) e dirham (BCE EUR/USD × 3,6725) ricalcolate; importi di riferimento dello
    Stato convertiti; fornitori dei servizi visti solo dove letti; riquadro AXA spento (e acceso con un URL di prova: rel sponsored e dicitura);
    link da home, piè di pagina, pagine dei rifiuti (Regno Unito, Emirati, easiest, Stati Schengen) e panoramica; titoli delle pagine dei rifiuti
    di Regno Unito ed Emirati con "Schengen visa from".
25. Esperimento "pagine più facili da citare" (31/10/2026, dati/esperimento_citazioni.json): coppie e gruppi ricalcolati dal seme e dalla
    linea di base salvata (stesso risultato), coppie = pagine Paese meno le escluse, una trattata per coppia; ogni pagina trattata ha la data
    "Updated on" sotto il titolo uguale al lastmod del registro, dateModified uguale nel JSON-LD (WebPage e Dataset), niente datePublished
    (non c'era), riquadro "Key figures" prima del riepilogo con numeri = ricalcolo indipendente da dati/rifiuti.json, fonte con link e data,
    licenza e link al CSV; data.csv valido (intestazione, campi, numeri interi, tassi) e uguale al ricalcolo, riga del totale = riquadro;
    pagine di controllo senza nessun elemento del trattamento, senza data.csv e con l'impronta del contenuto uguale a quella salvata prima.
26. Australian citizenship ceremony wait times (31/10/2026, dati/cerimonie.json): righe del JSON = risposta grezza di Home Affairs (lista
    citizenshipCeremony); pagine attese (indice, council con 3+ suggerimenti, tempi) in sitemap con titoli ≤ 70; prima frase con cifra, fonte e
    data; tabelle e quote ponderate ricalcolate; storico, percentili, avviso, licenza CC BY 3.0 AU, link.
27. Sezioni in spagnolo (/es/) e portoghese (/pt/) "¿Cuánto dinero necesito para entrar a Europa?" (31/10/2026, dati/entrar_europa.json e
    dati/schengen_residenti.json): 11 + 11 pagine attese in sitemap, lang, canonical, titoli ≤ 70, FAQPage, "la policía de fronteras decide",
    prima frase con fonte e data; hreflang es/pt reciproci e selettore di lingua; importi = JSON (formattazione indipendente), esempi = calcolo
    indipendente, dati del calcolatore = JSON, motore JS = Python; citazioni = frammenti ufficiali; visti = allegati del Reg. 2018/1806; ETIAS
    senza date inventate; SafetyWing solo sull'assicurazione e onesto; link da home e How it works; piè di pagina comune invariato.
    Il controllo 9 accetta dal 31/10/2026 il titolo tradotto del blocco "Other useful tools" nelle pagine es/pt (stessi link).
28. Visti di lunga durata per nazionalità in spagnolo (/es/visados/) e portoghese (/pt/vistos/) (4/11/2026, dati/visados.json): impronta del JSON,
    fonti lette (HTTP 200) e PDF-immagine di San Paolo con lo SHA-256 atteso; pagine attese (2 indici + visto × nazionalità) in sitemap e nessuna in
    più, lang, canonical, titoli ≤ 70, FAQPage, BreadcrumbList, "el consulado decide"/"o consulado decide"; hreflang: indici es/pt reciproci,
    pagine di dettaglio autoreferenziali, ogni alternato esiste e rimanda indietro; ogni importo della prima frase e delle tabelle = ricalcolo
    indipendente (IPREM, SMI, RMMG di programmi.json, percentuali e tasse dei frammenti, cambi EUR/USD BCE × valuta/USD della fonte del Paese);
    ogni tassa = numero scritto nel frammento ufficiale; data del listino in pagina; ogni <q> = frammento ufficiale; link esterni solo verso
    le fonti del JSON; nessun link sponsorizzato; FAQ da ricerche vere dell'autocompletamento; link da home, How it works, menu es/pt;
    piè di pagina comune invariato. Online: 8 frammenti a caso riletti sulle fonti.
29. Infermieri formati all'estero (/nurses-abroad/) e UK Ancestry visa (/uk-ancestry-visa/) (5/11/2026, dati/infermieri.json e dati/ancestry.json):
    impronte dei JSON, fonti lette (HTTP 200), file del Home Office = quello di dati/rifiuti.json; valori del JSON = file grezzi NMC e JQ06 riletti
    con un lettore proprio; pagine attese (indice, 12 Paesi ricalcolati con la soglia di 1.000 sul registro, UK, Irlanda, lista rossa, costi, Ancestry)
    in sitemap e nessuna in più, titoli ≤ 70, canonical, FAQPage, BreadcrumbList, avviso, nessun riquadro di affiliazione; prima frase con numero,
    fonte e data; tabelle (registro, nuovi iscritti, Irlanda, Health and Care Worker, 20 Paesi UK, Paesi irlandesi, rossi e ambra, costi NMC,
    conversioni BCE, Ancestry per nazionalità e per anno) = ricalcolo indipendente; grado del codice e lista OMS 2023 (55 Paesi, Kenya assente);
    lista OMS 2026 dichiarata non pubblicata e nessuna cifra della lista provvisoria; nessun "£1,170"; ogni citazione = frammento ufficiale; ogni
    domanda della FAQ legata a un suggerimento salvato dell'autocompletamento; link da home, How it works e /visa-refusal-rates/uk/; piè di pagina invariato.
30. Liste delle università per i visti dei laureati (/top-university-visas/, 5/11/2026, dati/top_university.json): impronta del JSON, fonti lette
    (HTTP 200, SHA-256, data); righe delle liste HPI 2021-2026 = tabelle GOV.UK rilette con un lettore proprio, righe TTPS = PDF riletto con
    pdftotext -raw (stesso numero, stesso ordine, asterischi delle nuove), nomi giapponesi J-Find presenti nel PDF; frammenti trovati nei file grezzi;
    valori numerici scritti nei frammenti; università = righe delle liste; pagine attese (indice, 6 HPI, TTPS, J-Find, 39 università: anni HPI misti e britanniche, una
    per Paese + India e Nigeria) in sitemap e nessuna in più, titoli ≤ 70 con l'anno, canonical, FAQPage, BreadcrumbList, avviso, nessuna
    promessa né affiliazione; prima frase con risposta, fonte e data; tabelle ricalcolate (liste per università, righe delle liste, entrate e uscite
    HPI, conteggi per Paese, confronto dei visti); citazioni = frammenti; FAQ da ricerche salvate; link da home e How it works; piè di pagina e
    pagine di controllo dell'esperimento senza la sezione.
Il controllo 8 comprende dal 28/10/2026 anche i visti UK di famiglia e del partner (coniuge).
Monetizzazione (30/10/2026, controllo comune di studio-business/strumenti/monetizzazione.py): i link di affiliazione sono
ammessi solo verso i domini di monetizzazione.json, con rel="sponsored noopener" e la riga di trasparenza nella pagina;
domini bloccati e link sponsorizzati verso altri domini sono errori; script AdSense, ads.txt e sezione privacy ci sono
solo se AdSense è acceso per questo sito in monetizzazione.json.
Esce con codice 1 se qualcosa non va.
"""
import html
import json
import math
import random
import re
import subprocess
import sys
import time
import tempfile
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import genera as G  # noqa: E402

SITO = G.SITO
P = {p["slug"]: p for p in G.PROG}
# Cambi BCE del 9 ottobre 2026 (1 EUR = ...), quelli usati negli esempi di TEST.md
T = {"USD": 1.1206, "GBP": 0.84763, "CAD": 1.5942, "AUD": 1.6052, "PHP": 70.397, "INR": 108.3965, "SEK": 11.1675,
     "DKK": 7.4751, "JPY": 177.34}

# (descrizione, programma, variante, adulti, figli, campo, valuta di arrivo o None, atteso calcolato a mano)
# campo: "mensile" (importo mensile della regola, per mensilità), "annuale", "mensile12" (annuale / 12).
# Con una valuta di arrivo si usa converti_importi: si converte l'importo del periodo della regola e si ricava l'altro.
ESEMPI = [
    ("ES nomadi, 1 adulto: 200% × 1.221 = 2.442 al mese (× 14)", "spain-digital-nomad-visa", "std", 1, 0, "mensile", None, 2442.00),
    ("ES nomadi, 1 adulto, annuo: 2.442 × 14", "spain-digital-nomad-visa", "std", 1, 0, "annuale", None, 34188.00),
    ("ES nomadi, 1 adulto, su 12 mesi: 34.188 / 12", "spain-digital-nomad-visa", "std", 1, 0, "mensile12", None, 2849.00),
    ("ES nomadi, coppia: (2.442 + 75% × 1.221 = 915,75) × 14 = 47.008,50 / 12 = 3.917,375", "spain-digital-nomad-visa", "std", 2, 0, "mensile12", None, 3917.38),
    ("ES nomadi, coppia + 2 figli: 2.442 + 915,75 + 2 × 305,25", "spain-digital-nomad-visa", "std", 2, 2, "mensile", None, 3968.25),
    ("ES nomadi, coppia + 2 figli, annuo: 3.968,25 × 14", "spain-digital-nomad-visa", "std", 2, 2, "annuale", None, 55555.50),
    ("ES non lucrativo, coppia + 2 figli: 4 × 600 + 3 × 600", "spain-non-lucrative-visa", "std", 2, 2, "mensile", None, 4200.00),
    ("PT D8, 1 adulto: 4 × 920", "portugal-d8-digital-nomad-visa", "std", 1, 0, "mensile", None, 3680.00),
    ("PT D8, coppia + 1 figlio: nessun importo familiare ufficiale, resta 3.680", "portugal-d8-digital-nomad-visa", "std", 2, 1, "mensile", None, 3680.00),
    ("PT D7, coppia + 2 figli, annuo: (920 + 460 + 2 × 276) × 12", "portugal-d7-visa", "std", 2, 2, "annuale", None, 23184.00),
    ("HR nomadi, 2 adulti + 1 figlio: 2,5 × 1.449 + 2 × 10% × 1.449", "croatia-digital-nomad-visa", "std", 2, 1, "mensile", None, 3912.30),
    ("HU White Card, coppia: i familiari non contano, 3.000", "hungary-white-card", "std", 2, 0, "mensile", None, 3000.00),
    ("IT nomadi, mensile: 3 × 8.263,31 = 24.789,93 / 12 = 2.065,8275", "italy-digital-nomad-visa", "std", 1, 0, "mensile", None, 2065.83),
    ("DE Blue Card ridotta, mensile: 45.934,20 / 12", "germany-eu-blue-card", "red", 1, 0, "mensile", None, 3827.85),
    ("NL kennismigrant 30+, annuo: 5.942 × 12", "netherlands-highly-skilled-migrant", "30plus", 1, 0, "annuale", None, 71304.00),
    ("UK Skilled Worker, dottorato non STEM: soglia minima 37.500", "uk-skilled-worker-visa", "phd", 1, 0, "annuale", None, 37500.00),
    ("UK coniuge (proroga regole pre-2024), 3 figli: 18.600 + 3.800 + 2 × 2.400", "uk-spouse-visa", "legacy", 2, 3, "annuale", None, 27200.00),
    ("UK coniuge (proroga), 4 figli: 18.600 + 3.800 + 3 × 2.400 = 29.600 → tetto 29.000", "uk-spouse-visa", "legacy", 2, 4, "annuale", None, 29000.00),
    ("Valori fuori scala: 0 adulti e -3 figli diventano 1 e 0 (ES nomadi = 2.442)", "spain-digital-nomad-visa", "std", 0, -3, "mensile", None, 2442.00),
    ("Valori fuori scala: 50 adulti diventano 20 (HR: 3.622,50 + 19 × 144,90)", "croatia-digital-nomad-visa", "std", 50, 0, "mensile", None, 6375.60),
    ("ES nomadi in USD per mensilità: 2.442 × 1,1206 = 2.736,5052", "spain-digital-nomad-visa", "std", 1, 0, "mensile", "USD", 2736.51),
    ("ES nomadi in USD all'anno: 2.736,51 × 14 (coerente col mese)", "spain-digital-nomad-visa", "std", 1, 0, "annuale", "USD", 38311.14),
    ("ES nomadi in PHP su 12 mesi: 2.442 × 70,397 = 171.909,47 × 14 = 2.406.732,58 / 12", "spain-digital-nomad-visa", "std", 1, 0, "mensile12", "PHP", 200561.05),
    ("ES nomadi famiglia di 4 in USD per mensilità: 3.968,25 × 1,1206 = 4.446,82", "spain-digital-nomad-visa", "std", 2, 2, "mensile", "USD", 4446.82),
    ("PT D8 in INR: 3.680 × 108,3965", "portugal-d8-digital-nomad-visa", "std", 1, 0, "mensile", "INR", 398899.12),
    ("HR nomadi in GBP: 3.622,50 × 0,84763 = 3.070,5397", "croatia-digital-nomad-visa", "std", 1, 0, "mensile", "GBP", 3070.54),
    ("HR nomadi in GBP all'anno: 3.070,54 × 12 (non 3.622,50 × 12 convertito a parte)", "croatia-digital-nomad-visa", "std", 1, 0, "annuale", "GBP", 36846.48),
    ("UK Skilled Worker da GBP a INR: 41.700 / 0,84763 × 108,3965", "uk-skilled-worker-visa", "std", 1, 0, "annuale", "INR", 5332673.51),
    ("SE Blue Card da SEK a USD: 53.625 / 11,1675 × 1,1206", "sweden-eu-blue-card", "std", 1, 0, "mensile", "USD", 5380.99),
    ("DK pay limit da DKK a USD: 552.000 / 7,4751 × 1,1206", "denmark-pay-limit-scheme", "std", 1, 0, "annuale", "USD", 82750.89),
    ("DE Blue Card in JPY (0 decimali): 50.700 × 177,34", "germany-eu-blue-card", "std", 1, 0, "annuale", "JPY", 8991138),
    ("ES non lucrativo famiglia di 4 in AUD: 4.200 × 1,6052", "spain-non-lucrative-visa", "std", 2, 2, "mensile", "AUD", 6741.84),
]

# Confronto con il reddito: (descrizione, programma, variante, reddito al mese, mensilità, valuta, esito atteso)
ESITI = [
    ("AT Blue Card: 3.977 × 14 = 55.678 = soglia → sì", "austria-eu-blue-card", "std", 3977, 14, "EUR", "si"),
    ("AT Blue Card: 3.977 × 12 = 47.724 → no", "austria-eu-blue-card", "std", 3977, 12, "EUR", "no"),
    ("ES nomadi: 2.442 × 14 = 34.188 → sì", "spain-digital-nomad-visa", "std", 2442, 14, "EUR", "si"),
    ("ES nomadi: 2.849 × 12 = 34.188 → sì", "spain-digital-nomad-visa", "std", 2849, 12, "EUR", "si"),
    ("ES nomadi: 2.500 × 12 = 30.000 (mese sì, anno no) → parziale", "spain-digital-nomad-visa", "std", 2500, 12, "EUR", "parziale"),
    ("ES nomadi: 2.400 × 14 → no", "spain-digital-nomad-visa", "std", 2400, 14, "EUR", "no"),
    ("ES nomadi in USD: 2.736,51 USD × 14 → 2.442,00 € × 14 → sì", "spain-digital-nomad-visa", "std", 2736.51, 14, "USD", "si"),
    ("HU White Card, regola mensile: 2.600 × 14 = 36.400 > 36.000 ma 2.600 < 3.000 → no", "hungary-white-card", "std", 2600, 14, "EUR", "no"),
    ("HU White Card: 3.000 × 12 → sì", "hungary-white-card", "std", 3000, 12, "EUR", "si"),
    ("DE Blue Card: 4.225 × 12 = 50.700 → sì", "germany-eu-blue-card", "std", 4225, 12, "EUR", "si"),
    ("DE Blue Card: 4.224 × 12 → no", "germany-eu-blue-card", "std", 4224, 12, "EUR", "no"),
    ("IT nomadi: 2.100 × 12 = 25.200 ≥ 24.789,93 → sì", "italy-digital-nomad-visa", "std", 2100, 12, "EUR", "si"),
    ("UK Skilled Worker standard: nessun verdetto (conta anche il going rate)", "uk-skilled-worker-visa", "std", 5000, 12, "GBP", "nd"),
    ("UK Skilled Worker ridotto: nessun verdetto", "uk-skilled-worker-visa", "lower", 2800, 12, "GBP", "nd"),
    ("UK coniuge: nessun verdetto", "uk-spouse-visa", "std", 3000, 12, "GBP", "nd"),
]


def valore(o, campo, a):
    return o[campo] if a is None else G.converti_importi(o, a, T)[campo]


def controlla_esempi():
    errori = []
    for descr, slug, vid, ad, fi, campo, a, atteso in ESEMPI:
        v = valore(G.calcola(P[slug], vid, ad, fi), campo, a)
        if abs(v - atteso) > 0.001:
            errori.append(f"ESEMPIO SBAGLIATO: {descr}: atteso {atteso}, calcolato {v}")
    for descr, slug, vid, x, k, cur, atteso in ESITI:
        e = G.esito(P[slug], G.calcola(P[slug], vid, 1, 0), x, k, cur, T)
        if e != atteso:
            errori.append(f"ESITO SBAGLIATO: {descr}: atteso {atteso}, calcolato {e}")
    return errori


def casi_casuali(n=3000, seme=11):
    rnd = random.Random(seme)
    valute = ["EUR"] + sorted(G.CAMBI["tassi"])
    casi = []
    for _ in range(n):
        p = rnd.choice(G.PROG)
        casi.append([p["slug"], rnd.choice(p["varianti"])["id"], rnd.randint(-2, 25), rnd.randint(-3, 25), rnd.choice(valute),
                     round(rnd.uniform(0, 3000000), 2), rnd.choice([12, 13, 14, 11, 15]), rnd.choice(valute)])
    return casi


def controlla_js(casi):
    """Esegue il motore JS con node sugli stessi casi e confronta i risultati con il Python."""
    dati = {"programmi": G.PROG, "indici": G.INDICI}
    script = ("var D=" + json.dumps(dati) + ";var T=" + json.dumps(G.CAMBI["tassi"]) + ";var TT=" + json.dumps(T) + ";\n" + G.MOTORE_JS +
              "\nvar casi=" + json.dumps(casi) + ";var es=" + json.dumps([[e[1], e[2], e[3], e[4], e[5], e[6]] for e in ESEMPI]) +
              ";var esiti=" + json.dumps([[e[1], e[2], e[3], e[4], e[5]] for e in ESITI]) + ";\n"
              "function trova(s){for(var i=0;i<D.programmi.length;i++)if(D.programmi[i].slug===s)return D.programmi[i];}\n"
              "var out={casi:casi.map(function(c){var P=trova(c[0]);var o=calcola(D,P,c[1],c[2],c[3]);var cv=convertiImporti(o,c[4],T);"
              "return [o.mensile,o.annuale,o.mensile12,cv.mensile,cv.annuale,cv.mensile12,esito(P,o,c[5],c[6],c[7],T)];}),"
              "es:es.map(function(e){var o=calcola(D,trova(e[0]),e[1],e[2],e[3]);return e[5]?convertiImporti(o,e[5],TT)[e[4]]:o[e[4]];}),"
              "esiti:esiti.map(function(e){var P=trova(e[0]);return esito(P,calcola(D,P,e[1],1,0),e[2],e[3],e[4],TT);})};"
              "console.log(JSON.stringify(out));")
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(script)
        nome = fh.name
    try:
        r = subprocess.run(["node", nome], capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        return ["node non trovato: confronto JS saltato"]
    if r.returncode != 0:
        return ["Errore JS: " + r.stderr[:500]]
    js = json.loads(r.stdout)
    errori = []
    for c, j in zip(casi, js["casi"]):
        o = G.calcola(P[c[0]], c[1], c[2], c[3])
        cv = G.converti_importi(o, c[4], G.CAMBI["tassi"])
        py = [o["mensile"], o["annuale"], o["mensile12"], cv["mensile"], cv["annuale"], cv["mensile12"]]
        if any(abs(a - b) > 0.001 for a, b in zip(py, j[:6])) or G.esito(P[c[0]], o, c[5], c[6], c[7], G.CAMBI["tassi"]) != j[6]:
            errori.append(f"JS diverso dal Python per {c}: py {py} js {j}")
    for e, j in zip(ESEMPI, js["es"]):
        if abs(j - e[7]) > 0.001:
            errori.append(f"JS sbaglia l'esempio {e[0]}: {j}")
    for e, j in zip(ESITI, js["esiti"]):
        if j != e[6]:
            errori.append(f"JS sbaglia l'esito {e[0]}: {j}")
    return errori[:20]


def leggi(rel):
    return (SITO / rel).read_text(encoding="utf-8")


def controlla_contenuti():
    """Correzioni della revisione indipendente del 10/10/2026: devono restare."""
    errori = []
    tutto = "\n".join(f.read_text(encoding="utf-8") for f in SITO.rglob("*.html"))
    def deve(cond, msg):
        if not cond:
            errori.append(msg)
    es = leggi("spain-digital-nomad-visa/index.html")
    deve("€2,442</strong> a month × 14 payments" in es and "€2,849 a month if spread over 12 payments" in es, "ES: manca la forma ufficiale 2.442 × 14 con l'equivalente su 12")
    deve("consulados/buenosaires" in es.lower() and "HANOI" in es, "ES: mancano le fonti dei consolati (Buenos Aires, Hanoi)")
    deve("€1,221 a month × 14 payments" in es, "ES: SMI non indicato come 1.221 × 14")
    # dal 30/10/2026 le pagine dei centri SELT (uk-english-test/chile/) nominano Santiago come città dell'elenco ufficiale: esclusa
    # dal 30/10/2026 anche l'elenco delle sedi thailandesi (thailand-dtv-visa/) nomina l'ambasciata a Santiago del Cile: esclusa
    # dal 4/11/2026 anche i visti di lunga durata per nazionalità (es/visados/, pt/vistos/) citano il listino del Consolato di Spagna a Santiago del Cile: esclusi
    senza_selt = "\n".join(f.read_text(encoding="utf-8") for f in SITO.rglob("*.html")
                            if "uk-english-test" not in f.parts and "thailand-dtv-visa" not in f.parts and "visados" not in f.parts and "vistos" not in f.parts)
    deve("Santiago" not in senza_selt, "Attribuzione a Santiago del Cile ancora presente")
    deve("not €2,762" not in tutto and "not €3,295" not in tutto, "Frase 'not €…' ancora in home")
    it = leggi("italy-digital-nomad-visa/index.html")
    deve("passive income such as social security, rents or stocks is not considered" in it and "consboston.esteri.it" in it, "IT: manca la regola sul reddito passivo (consolato di Boston)")
    pt = leggi("portugal-d8-digital-nomad-visa/index.html")
    deve("How much for a family" not in pt and "does not say how this combines" in pt, "PT D8: righe familiari ancora presenti o nota mancante")
    uk = leggi("uk-skilled-worker-visa/index.html")
    deve("£37,500" in uk and "70% to 90% of the going rate" in uk and "100% of the going rate" in uk and "We do not give a yes/no" in uk, "UK SW: condizioni del going rate mancanti")
    sp = leggi("uk-spouse-visa/index.html")
    deve("There is no income requirement" not in sp and "without relying on additional public funds" in sp, "UK coniuge: frase sui sussidi non corretta")
    deve("Couple (combined income)" in sp and "pre-settled status" in sp, "UK coniuge: etichetta di coppia o pre-settled mancanti")
    nf = leggi("404.html")
    hrefs = re.findall(r'href="([^"]+)"', nf)
    rel_rotti = [h for h in hrefs if not h.startswith(("/", "http", "data:", "#", "mailto:"))]
    deve(not rel_rotti, f"404: link relativi {rel_rotti[:3]}")
    deve('rel="canonical"' not in nf, "404: canonical da togliere (pagina noindex)")
    wk = leggi("work-visa-salary-thresholds/index.html")
    tb = re.search(r"<tbody>.*?</tbody>", wk, re.S).group(0)
    deve("spouse" not in tb.lower(), "Lavoro: righe del visto coniuge ancora nella tabella")
    deve("8% holiday allowance" in wk, "Lavoro: nota olandese mancante")
    deve("latest European Central Bank reference rates" in leggi("index.html") and "today's European Central Bank" not in tutto, "Home: 'today's ECB rates' da correggere")
    deve("IT specialists" in leggi("germany-eu-blue-card/index.html"), "DE: specialisti IT mancanti nella soglia ridotta")
    deve("at least one year earlier" in es, "ES: regola dell'azienda con almeno un anno mancante")
    deve("child born in Hungary" in leggi("hungary-white-card/index.html"), "HU: eccezione del figlio nato in Ungheria mancante")
    deve("podaci.dzs.hr" in leggi("croatia-digital-nomad-visa/index.html"), "HR: fonte DZS mancante")
    for s in ("netherlands-highly-skilled-migrant", "netherlands-eu-blue-card"):
        deve("8% holiday allowance" in leggi(f"{s}/index.html"), f"{s}: nota sull'indennità di ferie mancante")
    zeri = re.findall(r"(?:[€£]|\b[A-Z]{3} )\d[\d,]*\.00\b", tutto)
    deve(not zeri, f"Importi interi ancora con '.00': {sorted(set(zeri))[:5]}")
    deve('function soldi(v,c){var t=grp(v,DEC[c]===0?0:2);if(t.slice(-3)===\'.00\')t=t.slice(0,-3);' in es, "JS: soldi() non toglie '.00' dagli importi interi")
    deve('name="pagamenti"' in es, "Calcolatore: scelta 12/13/14 mensilità mancante")
    deve("italystrikes/dati/cambi-bce.json" in es, "URL dei cambi dal vivo non aggiornato")
    return errori


class Link(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href = []

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k in ("href", "src") and v:
                self.href.append(v)


def controlla_link():
    errori = []
    pagine = list(SITO.rglob("*.html"))
    for f in pagine:
        p = Link()
        p.feed(f.read_text(encoding="utf-8"))
        for h in p.href:
            if h.startswith(("http://", "https://", "mailto:", "data:", "#", "javascript:")):
                continue
            h = h.split("#")[0].split("?")[0]
            if not h:
                continue
            dest = (SITO / h.lstrip("/")) if h.startswith("/") else (f.parent / h)
            dest = dest.resolve()
            if dest.is_dir():
                dest = dest / "index.html"
            if not dest.exists():
                errori.append(f"LINK ROTTO in {f.relative_to(SITO)}: {h}")
    return errori, len(pagine)


def controlla_fonti():
    errori = []
    for p in G.PROG:
        t = (SITO / p["slug"] / "index.html").read_text(encoding="utf-8")
        f = p["fonti"][0]
        blocco = re.search(r'<p class="cifra">.*?</section>', t, re.S)
        if not blocco or f["url"].replace("&", "&amp;") not in blocco.group(0) or "checked on " + G.data_lunga(f["controllato_il"]) not in blocco.group(0):
            errori.append(f"{p['slug']}: fonte o data mancanti sotto la cifra principale")
        if t.count("checked on") < 2:
            errori.append(f"{p['slug']}: date dei controlli mancanti")
    return errori


# Parole vietate scritte al contrario, così questo file non le contiene in chiaro.
_AL_CONTRARIO = ["edualc", "ciporhtna", "ianepo", "tpgtahc", "inimeg", "tolipoc", "amall", "lartsim", "supo", "tennos", "ukiah"]
VIETATE = re.compile(r"\b(" + "|".join(w[::-1] for w in _AL_CONTRARIO) + r"|gpt-\d)\b", re.I)
# Nomi di Comuni italiani veri (elenco ISTAT, dati della flat tax del 7% dal 31/10/2026) che contengono una parola della lista:
# si tolgono prima del controllo, solo come stringa JSON intera tra virgolette ("San ..."), case-sensitive: nel testo delle pagine restano vietati.
TOPONIMI_AMMESSI = re.compile(r'"San (?:Giovanni )?' + _AL_CONTRARIO[4][::-1].capitalize() + r'"')


def controlla_parole():
    errori = []
    for f in list(SITO.rglob("*")) + list((SITO.parent / "dati").glob("*.json")):
        if f.is_file() and f.suffix in (".html", ".xml", ".txt", ".toml", ".json"):
            m = VIETATE.search(TOPONIMI_AMMESSI.sub(" ", f.read_text(encoding="utf-8")))
            if m:
                errori.append(f"Parola vietata '{m.group(0)}' in {f}")
    return errori


# ---------------------------------------------------------------- 7. Visa refusal rates
RE_DATA = re.compile(r"\b\d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December) 20\d\d\b")
URL_UFFICIALI = ("https://home-affairs.ec.europa.eu/", "https://assets.publishing.service.gov.uk/", "https://www.gov.uk/",
                 # Australia, Nuova Zelanda, Canada (26/10/2026)
                 "https://data.gov.au/", "https://www.homeaffairs.gov.au/", "https://www.immigration.govt.nz/", "https://www.ircc.canada.ca/",
                 "https://open.canada.ca/")


def pagine_rifiuti():
    return sorted((SITO / "visa-refusal-rates").rglob("index.html"))


def controlla_rifiuti(online=True):
    errori = []
    R = json.loads((SITO.parent / "dati" / "rifiuti.json").read_text(encoding="utf-8"))
    anni = sorted(R["schengen"], key=int)
    a1 = anni[-1]
    pagine = pagine_rifiuti()
    if len(pagine) < 60:
        errori.append(f"Rifiuti: solo {len(pagine)} pagine")
    esterni = set()
    for f in pagine:
        t = f.read_text(encoding="utf-8")
        nome = str(f.relative_to(SITO))
        corpo = t.split('<main id="main">', 1)[1].split("</main>", 1)[0]
        # ogni tabella deve avere sotto (prima della tabella dopo) una riga di fonte con URL ufficiale e data
        pezzi = corpo.split("<table")
        for i, dopo in enumerate(pezzi[1:], 1):
            m = re.match(r'.*?</table></div>\s*<p class="fonte">(.*?)</p>', dopo, re.S)  # subito sotto la tabella
            if not m or not any(u in m.group(1) for u in URL_UFFICIALI) or not RE_DATA.search(m.group(1)):
                errori.append(f"Rifiuti: tabella {i} di {nome} senza fonte ufficiale e data sotto")
        # la cifra principale (riquadro di sintesi) ha la fonte con data
        for m in re.finditer(r'<p class="cifra[^"]*">.*?</p>\s*(?:<div class="kpi">.*?</div></div>\s*)?(?:<p class="lead"[^>]*>.*?</p>\s*)?(<p class="fonte">.*?</p>|<p class="cifra)', corpo, re.S):
            blocco = m.group(1)
            if blocco.startswith('<p class="cifra'):
                continue
            if not any(u in blocco for u in URL_UFFICIALI) or not RE_DATA.search(blocco):
                errori.append(f"Rifiuti: cifra principale di {nome} senza fonte e data")
        if "Statistics, not advice." not in corpo:
            errori.append(f"Rifiuti: avviso mancante in {nome}")
        if "safetywing.com" in corpo:
            if 'rel="sponsored noopener"' not in corpo or "Affiliate" not in corpo or "affiliate link" not in corpo:
                errori.append(f"Rifiuti: link SafetyWing senza rel sponsored o dicitura in {nome}")
        if re.search(r"ekta|travelpayouts|tp\.media", t, re.I):
            errori.append(f"Rifiuti: EKTA/Travelpayouts presente in {nome}")
        esterni.update(h for h in re.findall(r'href="(https://[^"]+)"', corpo))
    # ricalcolo indipendente delle percentuali principali
    def tot(filtro):
        v = [0, 0, 0, 0]
        for r in R["schengen"][a1]:
            if filtro(r):
                for i in range(4):
                    v[i] += r[3 + i]
        d = v[1] + v[2] + v[3]
        return v, (v[3] / d if d else None)
    v, tx = tot(lambda r: True)
    p = (SITO / "visa-refusal-rates" / "index.html").read_text(encoding="utf-8")
    if f"<strong>{tx * 100:.1f}%</strong> of decisions were visas not issued" not in p or f"{v[0]:,}" not in p:
        errori.append("Rifiuti: totale Schengen della panoramica diverso dal ricalcolo")
    for paese, slug in (("INDIA", "india"), ("NIGERIA", "nigeria"), ("PAKISTAN", "pakistan"), ("TÜRKIYE", "turkiye"), ("MOROCCO", "morocco")):
        v, tx = tot(lambda r: r[1] == paese)
        p = (SITO / "visa-refusal-rates" / slug / "index.html").read_text(encoding="utf-8")
        if f"<strong>{tx * 100:.1f}%</strong> not issued ({v[3]:,} of {v[1] + v[2] + v[3]:,} decisions)" not in p:
            errori.append(f"Rifiuti: cifra principale di {slug} diversa dal ricalcolo")
    for stato in ("France", "Germany", "Spain", "Italy", "Netherlands"):
        v, tx = tot(lambda r: r[0] == stato)
        p = (SITO / "visa-refusal-rates" / "schengen" / stato.lower() / "index.html").read_text(encoding="utf-8")
        if f"<strong>{tx * 100:.1f}%</strong> of decisions were visas not issued" not in p:
            errori.append(f"Rifiuti: cifra principale di {stato} diversa dal ricalcolo")
    q4 = R["uk"]["trimestri"][-4:]
    for naz, slug in (("India", "india"), ("Nigeria", "nigeria"), ("Pakistan", "pakistan"), ("Ghana", "ghana")):
        c = sum(R["uk"]["naz"][naz]["Visitor"].get(q, [0, 0])[0] for q in q4)
        r = sum(R["uk"]["naz"][naz]["Visitor"].get(q, [0, 0])[1] for q in q4)
        p = (SITO / "visa-refusal-rates" / slug / "index.html").read_text(encoding="utf-8")
        if f"<strong>{r / (c + r) * 100:.1f}%</strong> of visitor visa decisions" not in p or f"({r:,} refused out of {c + r:,})" not in p:
            errori.append(f"Rifiuti: cifra UK di {slug} diversa dal ricalcolo")
    # link esterni della sezione
    controllati = 0
    if online:
        import urllib.request
        for u in sorted(esterni):
            u2 = u.replace("&amp;", "&")
            for _tentativo in range(4):  # ircc.canada.ca e immigration.govt.nz a volte chiudono la connessione: si riprova
                try:
                    req = urllib.request.Request(u2, headers={"User-Agent": "Mozilla/5.0", "Range": "bytes=0-2047"})
                    with urllib.request.urlopen(req, timeout=60) as r:
                        st = r.status
                except Exception as e:  # noqa: BLE001
                    st = getattr(e, "code", str(e))
                if isinstance(st, int):
                    break
                time.sleep(3)
            controllati += 1
            if st not in (200, 206):
                errori.append(f"Rifiuti: link esterno {u2} risponde {st}")
    return errori, len(pagine), controllati


# ---------------------------------------------------------------- 8. "Easiest Schengen visa" e visti UK di studio e lavoro (21/10/2026)
def controlla_facile():
    errori = []
    R = json.loads((SITO.parent / "dati" / "rifiuti.json").read_text(encoding="utf-8"))
    anni = sorted(R["schengen"], key=int)
    a1 = anni[-1]
    pagine = sorted((SITO / "visa-refusal-rates").glob("*/easiest-schengen-visa/index.html"))
    if len(pagine) < 30:
        errori.append(f"Facile: solo {len(pagine)} pagine 'easiest-schengen-visa'")
    sitemap = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    for f in pagine:
        t = f.read_text(encoding="utf-8")
        slug = f.parent.parent.name
        if f"/visa-refusal-rates/{slug}/easiest-schengen-visa/</loc>" not in sitemap:
            errori.append(f"Facile: {slug} non in sitemap")
        titolo = re.search(r"<title>(.*?)</title>", t).group(1)
        if not titolo.startswith("Easiest Schengen visa from "):
            errori.append(f"Facile: titolo di {slug}: {titolo}")
        if "Rates describe past decisions, not your chances." not in t:
            errori.append(f"Facile: frase di cautela mancante in {slug}")
        if 'class="classifica"' not in t or "FAQPage" not in t or "Statistics, not advice." not in t:
            errori.append(f"Facile: classifica, FAQ o avviso mancanti in {slug}")
        madre = (SITO / "visa-refusal-rates" / slug / "index.html").read_text(encoding="utf-8")
        if 'href="easiest-schengen-visa/"' not in madre:
            errori.append(f"Facile: la pagina {slug} non rimanda alla classifica")
    # ricalcolo per Pakistan, India e Nigeria: Stato con il tasso più basso e più alto tra quelli con almeno 500 decisioni
    for paese, slug in (("PAKISTAN", "pakistan"), ("INDIA", "india"), ("NIGERIA", "nigeria")):
        per_stato = {}
        for r in R["schengen"][a1]:
            if r[1] == paese:
                v = per_stato.setdefault(r[0], [0, 0, 0, 0])
                for i in range(4):
                    v[i] += r[3 + i]
        ok = sorted(((v[3] / (v[1] + v[2] + v[3]), s, v) for s, v in per_stato.items() if v[1] + v[2] + v[3] >= 500))
        if len(ok) < 8:
            errori.append(f"Facile: {slug} ha solo {len(ok)} Stati con 500+ decisioni ma ha la pagina")
            continue
        t = (SITO / "visa-refusal-rates" / slug / "easiest-schengen-visa" / "index.html").read_text(encoding="utf-8")
        tb, sb = ok[0][0], ok[0][1]
        ta, sa = ok[-1][0], ok[-1][1]
        if f"<strong>{sb}: {tb * 100:.1f}%</strong> not issued" not in t:
            errori.append(f"Facile: Stato più basso di {slug} diverso dal ricalcolo ({sb} {tb * 100:.1f}%)")
        if f"<b>{sa}</b><span>highest rate: {ta * 100:.1f}%</span>" not in t:
            errori.append(f"Facile: Stato più alto di {slug} diverso dal ricalcolo ({sa} {ta * 100:.1f}%)")
        prime = re.search(r'<ol class="classifica">(.*?)</ol>', t, re.S).group(1)
        if f">{sb}</a>" not in prime.split("</li>")[0]:
            errori.append(f"Facile: primo della lista 'Lowest' di {slug} non è {sb}")
        # tabella: tutte le righe in ordine crescente di tasso
        tassi = [float(x) for x in re.findall(r'<td class="n" data-v="(\d\.\d+)"><span class="tb"', t.split("All Schengen countries ranked", 1)[1].split("</table>", 1)[0])]
        tassi_a1 = tassi[0::2]  # colonne alternate: anno più recente, anno prima
        if tassi_a1 != sorted(tassi_a1) or len(tassi_a1) != len(ok):
            errori.append(f"Facile: tabella di {slug} non ordinata o incompleta ({len(tassi_a1)} righe su {len(ok)})")
    # UK: tassi di studio e lavoro nel riquadro delle pagine per nazionalità e nella pagina /uk/
    q4 = R["uk"]["trimestri"][-4:]
    uk_pag = (SITO / "visa-refusal-rates" / "uk" / "index.html").read_text(encoding="utf-8")
    for naz, slug in (("Pakistan", "pakistan"), ("India", "india"), ("Nigeria", "nigeria"), ("Japan", "japan")):
        p = (SITO / "visa-refusal-rates" / slug / "index.html").read_text(encoding="utf-8")
        for g, nome in (("Study", "study"), ("Work", "work")):
            c = sum(R["uk"]["naz"][naz][g].get(q, [0, 0])[0] for q in q4)
            r = sum(R["uk"]["naz"][naz][g].get(q, [0, 0])[1] for q in q4)
            tx = f"{r / (c + r) * 100:.1f}%"
            if f"<b>{tx}</b><span>{nome} visas refused · {c + r:,} decisions</span>" not in p and f"<strong>{tx}</strong> of {nome} visa decisions" not in p:
                errori.append(f"Rifiuti UK: tasso {nome} di {slug} ({tx}) non trovato nel riquadro")
            if f"<td>{nome.capitalize()} visas</td>" not in p or f'<td class="n">{c + r:,}</td><td class="n">{c:,}</td><td class="n">{r:,}</td>' not in p:
                errori.append(f"Rifiuti UK: riga {nome} di {slug} diversa dal ricalcolo")
            riga = re.search(rf'<tr><td>(?:<a [^>]+>)?{naz}(?:</a>)?</td>.*?</tr>', uk_pag, re.S)
            if not riga or f'<td class="n" data-v="{c + r}">{c + r:,}</td>' not in riga.group(0) or f'data-v="{r / (c + r):.6f}"' not in riga.group(0):
                errori.append(f"Rifiuti UK: pagina /uk/, riga {naz}: {nome} {tx} o {c + r} decisioni non trovati")
    if "Study visas refused" not in uk_pag or "Work visas refused" not in uk_pag:
        errori.append("Rifiuti UK: colonne studio/lavoro mancanti nella pagina /uk/")
    # famiglia e partner (28/10/2026): riquadro, riga della tabella "Visa type" e riga del partner nelle pagine per nazionalità
    def somma_uk(naz, g, qq):
        c = sum(R["uk"]["naz"].get(naz, {}).get(g, {}).get(q, [0, 0])[0] for q in qq)
        r = sum(R["uk"]["naz"].get(naz, {}).get(g, {}).get(q, [0, 0])[1] for q in qq)
        return c, r
    for naz, slug in (("Pakistan", "pakistan"), ("India", "india"), ("Nigeria", "nigeria"), ("Bangladesh", "bangladesh")):
        p = (SITO / "visa-refusal-rates" / slug / "index.html").read_text(encoding="utf-8")
        c, r = somma_uk(naz, "Family", q4)
        if c + r >= 500 and f"<b>{r / (c + r) * 100:.1f}%</b><span>family visas refused · {c + r:,} decisions</span>" not in p:
            errori.append(f"Rifiuti UK: tasso famiglia di {slug} non trovato nel riquadro")
        if f'<td>Family visas</td>' not in p or f'<td class="n">{c + r:,}</td><td class="n">{c:,}</td><td class="n">{r:,}</td>' not in p:
            errori.append(f"Rifiuti UK: riga famiglia di {slug} diversa dal ricalcolo")
        pc, pr = somma_uk(naz, "Family: Partner", q4)
        if pc + pr >= 100 and (f'<td>of which partner (spouse) visas</td>' not in p or f'<td class="n">{pc + pr:,}</td><td class="n">{pc:,}</td><td class="n">{pr:,}</td>' not in p
                               or f"the rate was {pr / (pc + pr) * 100:.1f}% ({pr:,} refused out of {pc + pr:,} decisions" not in p):
            errori.append(f"Rifiuti UK: riga o frase del partner di {slug} diversa dal ricalcolo")
        if pc > c or pr > r:
            errori.append(f"Rifiuti UK: partner oltre la famiglia per {naz}")
    fam = (SITO / "visa-refusal-rates" / "uk" / "family-visas" / "index.html")
    if not fam.exists():
        errori.append("Rifiuti UK: manca la pagina uk/family-visas/")
    else:
        ft = fam.read_text(encoding="utf-8")
        tot_p = [0, 0]
        tot_f = [0, 0]
        for naz in R["uk"]["naz"]:
            a, b = somma_uk(naz, "Family: Partner", q4)
            tot_p[0] += a; tot_p[1] += b
            a, b = somma_uk(naz, "Family", q4)
            tot_f[0] += a; tot_f[1] += b
        if f"<strong>{tot_p[1] / sum(tot_p) * 100:.1f}%</strong> refused ({tot_p[1]:,} of {sum(tot_p):,} decisions)" not in ft:
            errori.append("Rifiuti UK: tasso del partner (tutte le nazionalità) diverso dal ricalcolo")
        if f"<b>{tot_f[1] / sum(tot_f) * 100:.1f}%</b><span>all family visas refused · {sum(tot_f):,} decisions</span>" not in ft:
            errori.append("Rifiuti UK: tasso della famiglia (tutte le nazionalità) diverso dal ricalcolo")
        riga = re.search(r'<tr><td>(?:<a [^>]+>)?Pakistan(?:</a>)?</td>.*?</tr>', ft, re.S)
        c, r = somma_uk("Pakistan", "Family", q4)
        if not riga or f'data-v="{r / (c + r):.6f}"' not in riga.group(0) or f'data-v="{c + r}">{c + r:,}<' not in riga.group(0):
            errori.append("Rifiuti UK: riga Pakistan della pagina family-visas diversa dal ricalcolo")
        if "/visa-refusal-rates/uk/family-visas/</loc>" not in (SITO / "sitemap.xml").read_text(encoding="utf-8"):
            errori.append("Rifiuti UK: family-visas non in sitemap")
        if len(re.search(r"<title>(.*?)</title>", ft).group(1)) > 70 or "FAQPage" not in ft:
            errori.append("Rifiuti UK: titolo oltre 70 caratteri o FAQ mancante in family-visas")
    if 'href="family-visas/"' not in uk_pag or "partner (spouse) visas refused" not in uk_pag:
        errori.append("Rifiuti UK: la pagina /uk/ non mostra famiglia e partner o non rimanda a family-visas")
    return errori, len(pagine)


def controlla_altri_siti():
    """9. Blocco "Other useful tools for your trip" in ogni pagina indicizzabile: gli stessi link di genera.ALTRI_SITI,
    nell'ordine, da 3 a 4, mai a questo sito, tutti con rel="noopener" e senza nofollow o sponsored."""
    errori = []
    n = 0
    for f in sorted(SITO.rglob("*.html")):
        rel = f.relative_to(SITO).as_posix()
        if f.name == "404.html" or f.name.startswith("google"):
            continue
        n += 1
        t = f.read_text(encoding="utf-8")
        blocchi = re.findall(r'<div class="f-altri"><h2>(.*?)</h2><ul>(.*?)</ul></div>', t, re.S)
        if len(blocchi) != 1:
            errori.append(f"blocco altri siti mancante o doppio in {rel}")
            continue
        titolo, voci = blocchi[0]
        attesi, titolo_atteso = G.ALTRI_SITI, "Other useful tools for your trip"
        lingua = re.search(r'<html lang="([a-z]+)"', t).group(1)
        if lingua in G.TITOLO_ALTRI_EE:  # sezioni in spagnolo e portoghese (31/10/2026): stesso blocco, titolo e descrizioni tradotti
            titolo_atteso = G.TITOLO_ALTRI_EE[lingua]
        if titolo != titolo_atteso:
            errori.append(f"titolo del blocco altri siti sbagliato in {rel}: {titolo}")
        link = re.findall(r"<a ([^>]*)>", voci)
        url = [re.search(r'href="([^"]+)"', a).group(1) for a in link]
        if url != [u for u, _, _ in attesi] or not 3 <= len(url) <= 4:
            errori.append(f"link del blocco altri siti diversi da genera.py in {rel}: {url}")
        for a, u in zip(link, url):
            if u.startswith(G.URL_SITO) or 'rel="noopener"' not in a or "nofollow" in a or "sponsored" in a:
                errori.append(f"link sbagliato nel blocco altri siti in {rel}: {a}")
    return errori, n


def controlla_indexnow():
    """File chiave IndexNow in sito/: presente, con dentro solo la chiave, fuori dalla sitemap (scritto da genera.py accanto a robots.txt)."""
    errori = []
    f = SITO / f"{G.CHIAVE_INDEXNOW}.txt"
    if not f.exists():
        errori.append(f"file chiave IndexNow mancante: {f.name}")
    elif f.read_text(encoding="utf-8").strip() != G.CHIAVE_INDEXNOW:
        errori.append(f"file chiave IndexNow con contenuto sbagliato: {f.name}")
    if f.name in (SITO / "sitemap.xml").read_text(encoding="utf-8"):
        errori.append("file chiave IndexNow citato nella sitemap")
    return errori



# ---------------------------------------------------------------- 11. Australia, Nuova Zelanda, Canada (26/10/2026)
PAGINE_ALTRI = {"australia-visas": ("CC BY 2.5 AU", "data.gov.au"), "new-zealand-visas": ("CC BY 3.0 NZ", "immigration.govt.nz"),
                "canada-visas": ("Open Government Licence – Canada", "ircc.canada.ca")}


def controlla_altri():
    """Pagine di riepilogo e sezioni nelle pagine per Paese: fonte, licenza, soglia e cifre ricalcolate qui da dati/rifiuti_altri.json
    (con un codice separato da genera.py)."""
    errori = []
    R = json.loads((SITO.parent / "dati" / "rifiuti_altri.json").read_text(encoding="utf-8"))
    mappa = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    soglia = 500
    for slug, (lic, dominio) in PAGINE_ALTRI.items():
        f = SITO / "visa-refusal-rates" / slug / "index.html"
        if not f.exists():
            errori.append(f"Altri: manca la pagina {slug}")
            continue
        t = f.read_text(encoding="utf-8")
        if f"/visa-refusal-rates/{slug}/</loc>" not in mappa:
            errori.append(f"Altri: {slug} non in sitemap")
        if lic not in t or dominio not in t or "Statistics, not advice." not in t:
            errori.append(f"Altri: {slug} senza licenza, fonte o avviso")
        ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)]
        if not any(x.get("@type") == "Dataset" and x.get("license", "").startswith("https://") for x in ld) or not any(x.get("@type") == "BreadcrumbList" for x in ld):
            errori.append(f"Altri: {slug} senza JSON-LD Dataset con licenza o breadcrumb")
    # Australia: tasso dei richiedenti principali fuori dall'Australia, ultimo anno fiscale completo
    au = R["au"]
    pieni = [a for a in au["anni"] if re.fullmatch(r"\d{4}-\d{2}", a)]
    a1 = pieni[-1]
    def au_po(n, a):
        c = au["naz"].get(n, {}).get("y", {}).get(a)
        return c[0] if c else [0, 0]
    escl = {"Not Specified", "Stateless Person", "UN Convention Refugee", "Refugee", "UNMIK Travel Document", "United Nations Organisation",
            "Yugoslavia, Fed Republic of", "Serbia and Montenegro"}
    attese = {n for n in au["naz"] if n not in escl and sum(au_po(n, a1)) >= soglia}
    t = (SITO / "visa-refusal-rates" / "australia-visas" / "index.html").read_text(encoding="utf-8")
    tab = re.search(r'<table class="ord[^"]*" id="t-au">.*?<tbody>(.*?)</tbody>', t, re.S)
    righe = re.findall(r"<tr>(.*?)</tr>", tab.group(1), re.S) if tab else []
    if len(righe) != len(attese):
        errori.append(f"Altri: tabella australiana con {len(righe)} righe, attese {len(attese)} (soglia {soglia})")
    for r in righe:
        dec = re.findall(r'<td class="n" data-v="(\d+)">', r)
        if dec and int(dec[0]) < soglia:
            errori.append(f"Altri: riga australiana sotto la soglia: {re.sub('<[^>]+>', '', r)[:60]}")
    tot = [sum(au_po(n, a1)[0] for n in au["naz"]), sum(au_po(n, a1)[1] for n in au["naz"])]
    if f"<strong>{tot[1] / sum(tot) * 100:.1f}%</strong> refused ({tot[1]:,} of {sum(tot):,} decisions)" not in t:
        errori.append("Altri: cifra principale australiana diversa dal ricalcolo")
    # Nuova Zelanda: ultimo anno completo = penultimo se l'ultimo è in corso
    nz = R["nz"]
    anni_nz = nz["info"]["visitor"]["anni"]
    nz1 = anni_nz[-2] if not nz["info"]["visitor"]["periodo"][1].startswith("30 June") else anni_nz[-1]
    # Canada: ultimo anno con 12 mesi
    ca = R["ca"]
    mesi = ca["tr_processed"]["mesi"]
    ca1 = max(a for a in {m[:4] for m in mesi} if sum(1 for m in mesi if m.startswith(a)) == 12)
    def ca_sum(k, n):
        t = ca[k].get("totali", {}).get(n, {}).get(ca1)
        return t if t is not None else sum(x for m, x in ca[k]["paesi"].get(n, {}).items() if m.startswith(ca1) and x is not None)
    for slug, n_au, n_nz, n_ca in (("india", "India", "India", "India"), ("pakistan", "Pakistan", "Pakistan", "Pakistan"),
                                   ("nigeria", "Nigeria", "Nigeria", "Nigeria"), ("philippines", "Philippines", "Philippines", "Philippines")):
        t = (SITO / "visa-refusal-rates" / slug / "index.html").read_text(encoding="utf-8")
        v = au_po(n_au, a1)
        if sum(v) >= soglia:
            if (f"refused <strong>{v[1] / sum(v) * 100:.1f}%</strong> of student visa decisions for primary applicants" not in t
                    or f"({v[1]:,} refused out of {sum(v):,})" not in t or 'id="australia"' not in t):
                errori.append(f"Altri: cifra australiana di {slug} diversa dal ricalcolo")
            if "and Australia</title>" not in t:
                errori.append(f"Altri: titolo di {slug} senza Australia")
        elif "of student visa decisions for primary applicants" in t:
            errori.append(f"Altri: {slug} mostra un tasso australiano sotto la soglia")
        vz = nz["tipi"]["visitor"].get(n_nz, {}).get(nz1, [0, 0])
        if sum(vz) >= soglia and (f"declined <strong>{vz[1] / sum(vz) * 100:.1f}%</strong> of visitor visa applications" not in t or 'id="new-zealand"' not in t):
            errori.append(f"Altri: cifra neozelandese di {slug} diversa dal ricalcolo")
        ap, es = ca_sum("tr_approved", n_ca), ca_sum("tr_processed", n_ca)
        if es >= soglia and (f"approved <strong>{ap / es * 100:.1f}%</strong> of the temporary resident applications" not in t
                             or f"({ap:,} approved out of {es:,} people)" not in t or "cannot be calculated" not in t):
            errori.append(f"Altri: cifra canadese di {slug} diversa dal ricalcolo")
        for lic in ("CC BY 2.5 AU", "CC BY 3.0 NZ", "Open Government Licence – Canada"):
            if lic not in t:
                errori.append(f"Altri: {slug} senza la licenza {lic}")
    # le pagine Schengen "domande fatte in Australia / in Canada" rimandano alle pagine delle destinazioni, e non hanno la sezione su sé stesse
    for slug, dest, ancora in (("australia", "australia-visas", 'id="australia"'), ("canada", "canada-visas", 'id="canada"')):
        t = (SITO / "visa-refusal-rates" / slug / "index.html").read_text(encoding="utf-8")
        if f'href="../{dest}/"' not in t or ancora in t:
            errori.append(f"Altri: pagina {slug}: manca il rimando a {dest} o c'è la sezione su sé stessa")
    return errori

# ---------------------------------------------------------------- 12. "Who moved where" (28/10/2026)
URL_UFFICIALI_TR = ("https://ec.europa.eu/eurostat/", "https://www.ircc.canada.ca/", "https://open.canada.ca/", "https://assets.publishing.service.gov.uk/",
                    "https://www.gov.ie/", "https://assets.gov.ie/")  # gov.ie: PPS (Irlanda), dal 30/10/2026


def controlla_trasferimenti():
    """Ricalcolo indipendente da dati/trasferimenti.json (senza le funzioni di genera.py): pagine attese, numeri, titoli, fonti, link."""
    errori = []
    D = json.loads((SITO.parent / "dati" / "trasferimenti.json").read_text(encoding="utf-8"))
    y1, y0 = D["anni"][-1], D["anni"][-2]
    eu = D["eurostat"]["dati"]
    nomi = D["eurostat"]["nomi_destinazioni"]
    slug_naz = {c: v[0] for c, v in G.NAZ_TR.items()}  # solo gli slug (configurazione), i numeri si ricalcolano qui
    def slug(n):
        import unicodedata
        n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode().lower()
        return re.sub(r"[^a-z0-9]+", "-", n).strip("-")
    attese = {}
    for c, s in slug_naz.items():
        for g, nome in nomi.items():
            if g == "EU27_2020":
                continue
            v = eu.get(c, {}).get(g, {}).get(y1)
            if v and v[0] is not None and v[0] >= 500:
                attese[f"{s}/{slug(nome)}"] = ("eu", c, g, v)
        ca = D["canada"]["cittadinanze"].get(c)
        if ca and ca["anni"][y1] >= 500:
            attese[f"{s}/canada"] = ("ca", c, None, ca)
        uk = D["uk"]["cittadinanze"].get(c)
        if uk and sum(uk["anni"][y1]) >= 500:
            attese[f"{s}/uk"] = ("uk", c, None, uk)
    # Irlanda (30/10/2026): pagina anche con almeno 500 PPS nell'ultimo anno intero; queste pagine si controllano nel punto 17
    PP = json.loads((SITO.parent / "dati" / "ppsn.json").read_text(encoding="utf-8"))
    ult = PP["mesi"][-1]
    pieno = ult[:4] if ult.endswith("-12") else str(int(ult[:4]) - 1)
    for c, s in slug_naz.items():
        x = PP["nazionalita"].get(c)
        if (x and (x["anni"].get(pieno) or 0) >= 500) or f"{s}/ireland" in attese:
            attese[f"{s}/ireland"] = ("ie", c, "IE", None)
    base = SITO / "moved-to"
    trovate = {f.parent.relative_to(base).as_posix() for f in base.glob("*/*/index.html")}
    if trovate != set(attese):
        errori.append(f"Trasferimenti: pagine in più {sorted(trovate - set(attese))[:5]}, mancanti {sorted(set(attese) - trovate)[:5]}")
    mappa = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    pagine = sorted(base.rglob("index.html"))
    for f in pagine:
        rel = f.parent.relative_to(SITO).as_posix() + "/"
        t = f.read_text(encoding="utf-8")
        if f"<loc>{G.URL_SITO}/{rel}</loc>" not in mappa:
            errori.append(f"Trasferimenti: {rel} non in sitemap")
        titolo = re.search(r"<title>(.*?)</title>", t).group(1)
        anno_t = ult[:4] if rel.endswith("/ireland/") else y1   # pagine Irlanda: anno dei PPS
        if len(titolo.replace("&amp;", "&")) > 70 or anno_t not in titolo:
            errori.append(f"Trasferimenti: titolo di {rel} oltre 70 caratteri o senza {anno_t}: {titolo}")
        corpo = t.split('<main id="main">', 1)[1].split("</main>", 1)[0]
        for i, dopo in enumerate(corpo.split("<table")[1:], 1):
            m = re.match(r'.*?</table></div>\s*<p class="fonte">(.*?)</p>', dopo, re.S)
            if not m or not any(u in m.group(1) for u in URL_UFFICIALI_TR) or not RE_DATA.search(m.group(1)):
                errori.append(f"Trasferimenti: tabella {i} di {rel} senza fonte ufficiale e data sotto")
        ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)]
        tipi = {x.get("@type") for x in ld}
        if "Dataset" not in tipi or "BreadcrumbList" not in tipi or (rel != "moved-to/" and "FAQPage" not in tipi):
            errori.append(f"Trasferimenti: JSON-LD mancante in {rel}: {tipi}")
        if rel != "moved-to/" and "What this number is, and what it is not" not in corpo:
            errori.append(f"Trasferimenti: riquadro 'what this number is' mancante in {rel}")
        # link di affiliazione (dal 30/10/2026): ammessi solo come nel controllo comune 14 (domini di monetizzazione.json,
        # rel="sponsored noopener", riga di trasparenza); qui restano vietati EKTA e Travelpayouts, che non sono in elenco
        if re.search(r'ekta|travelpayouts|tp\.media', corpo, re.I):
            errori.append(f"Trasferimenti: link a una rete di affiliazione non ammessa in {rel}")
    def num(n):
        return f"{n:,}"
    # pagine nazionalità × Paese: numero principale, anno prima e serie per anno
    for k, (tipo, c, g, v) in sorted(attese.items()):
        f = base / k / "index.html"
        if not f.exists() or tipo == "ie":
            continue
        t = f.read_text(encoding="utf-8")
        lead = re.search(r'<p class="lead">(.*?)</p>', t, re.S).group(1)
        if tipo == "eu":
            serie = eu[c][g]
            tot = serie[y1][0]
            if f"<strong>{num(tot)}</strong> first residence permits to" not in lead or "data updated on " + G.data_lunga(D["fonti"]["eurostat"]["aggiornato_il"]) not in lead:
                errori.append(f"Trasferimenti: numero principale o data di {k} diversi dai dati")
            for a, r in serie.items():
                if c == "UK" and a < "2021":
                    continue
                m = re.search(rf'<tr><td>{a}</td><td class="n" data-v="(\d+)">', t)
                if r[0] is not None and (not m or int(m.group(1)) != r[0]):
                    errori.append(f"Trasferimenti: serie {k} {a} diversa dai dati ({r[0]})")
            p0 = serie.get(y0)
            if p0 and p0[0] is not None and f"than in {y0} ({num(p0[0])})" not in lead:
                errori.append(f"Trasferimenti: confronto con {y0} di {k} diverso dai dati")
            mot = re.findall(r'<tr><td>(Family|Education|Work|Other)</td><td class="n" data-v="(\d*)">', t)
            if [int(x) if x else None for _, x in mot] != serie[y1][1:5]:
                errori.append(f"Trasferimenti: motivi {y1} di {k} diversi dai dati")
        elif tipo == "ca":
            if f"<strong>{num(v['anni'][y1])}</strong> " not in lead or f"({num(v['anni'][y0])})" not in lead:
                errori.append(f"Trasferimenti: numero canadese di {k} diverso dai dati")
            for a in D["anni"]:
                if not re.search(rf'<tr><td>{a}</td><td class="n" data-v="{v["anni"][a]}">', t):
                    errori.append(f"Trasferimenti: serie canadese {k} {a} diversa dai dati")
        else:
            tot1, tot0 = sum(v["anni"][y1]), sum(v["anni"][y0])
            if f"<strong>{num(tot1)}</strong> work, study and family visas" not in lead or f"({num(tot0)})" not in lead:
                errori.append(f"Trasferimenti: numero britannico di {k} diverso dai dati")
            for a in D["anni"]:
                x = v["anni"][a]
                if not re.search(rf'<tr><td>{a}</td><td class="n" data-v="{sum(x)}">[^<]*</td><td class="n" data-v="{x[0]}">[^<]*</td><td class="n" data-v="{x[1]}">[^<]*</td><td class="n" data-v="{x[2]}">', t):
                    errori.append(f"Trasferimenti: serie britannica {k} {a} diversa dai dati")
    # pagine della nazionalità: totale UE, righe dei Paesi
    for c, s in slug_naz.items():
        f = base / s / "index.html"
        if not f.exists():
            errori.append(f"Trasferimenti: manca la pagina {s}")
            continue
        t = f.read_text(encoding="utf-8")
        ue = eu[c]["EU27_2020"]
        if f"<strong>{num(ue[y1][0])}</strong> " not in re.search(r'<p class="lead">(.*?)</p>', t, re.S).group(1) or f"({num(ue[y0][0])})" not in t:
            errori.append(f"Trasferimenti: totale UE di {s} diverso dai dati")
        tab = re.search(r'id="t-tr">.*?<tbody>(.*?)</tbody>', t, re.S).group(1)
        righe = re.findall(r'<tr><td>(?:<a href="([^"]+)">)?([^<]+)(?:</a>)?</td><td class="n" data-v="(\d+)">', tab)
        for href, nome, x in righe:
            g = next((k for k, n in nomi.items() if n == nome), None)
            if g is None or eu[c][g][y1][0] != int(x):
                errori.append(f"Trasferimenti: riga {nome} di {s} diversa dai dati")
            if (href != "") != (f"{s}/{slug(nome)}" in attese):
                errori.append(f"Trasferimenti: link della riga {nome} di {s} non coerente con la soglia")
        attesi_ue = sum(1 for g in nomi if g != "EU27_2020" and g not in ("IS", "LI", "NO", "CH") and eu[c].get(g, {}).get(y1) and eu[c][g][y1][0] is not None)
        if len(righe) != attesi_ue:
            errori.append(f"Trasferimenti: {s} ha {len(righe)} righe UE, attese {attesi_ue}")
    # link interni della sezione (oltre al controllo 3, che copre tutto il sito)
    rotti = 0
    for f in pagine:
        pz = Link()
        pz.feed(f.read_text(encoding="utf-8"))
        for h in pz.href:
            if h.startswith(("http", "mailto:", "data:", "#", "javascript:")):
                continue
            h = h.split("#")[0].split("?")[0]
            dest = ((SITO / h.lstrip("/")) if h.startswith("/") else (f.parent / h)).resolve()
            if dest.is_dir():
                dest = dest / "index.html"
            if h and not dest.exists():
                rotti += 1
                errori.append(f"Trasferimenti: link rotto in {f.relative_to(SITO)}: {h}")
    # collegamenti dalla home e dalle pagine Paese
    if 'href="moved-to/"' not in leggi("index.html") or 'href="moved-to/americans/"' not in leggi("index.html"):
        errori.append("Trasferimenti: la home non rimanda alla sezione")
    for paese, d in (("spain", "spain"), ("germany", "germany"), ("united-kingdom", "uk")):
        if f'moved-to/americans/{d}/"' not in leggi(f"country/{paese}/index.html"):
            errori.append(f"Trasferimenti: la pagina Paese {paese} non rimanda a moved-to/americans/{d}/")
    return errori, len(pagine), len(attese)


def controlla_lastmod():
    """13. Ogni URL della sitemap ha un lastmod vero: data valida, non nel futuro, uguale al registro di genera.py; nessun doppione."""
    from datetime import date
    errori = []
    mappa = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    voci = re.findall(r"<url><loc>([^<]+)</loc>(?:<lastmod>([^<]*)</lastmod>)?</url>", mappa)
    reg = json.loads((SITO.parent / "dati" / "lastmod.json").read_text(encoding="utf-8"))["pagine"]
    if len(voci) != len({u for u, _ in voci}):
        errori.append("Sitemap: URL doppi")
    if len(voci) != len(re.findall(r"<url>", mappa)):
        errori.append("Sitemap: voci non lette")
    for u, d in voci:
        try:
            ok = date.fromisoformat(d) <= date.today()
        except ValueError:
            ok = False
        p = u[len(G.URL_SITO) + 1:]
        if not ok or reg.get(p, [None])[0] != d:
            errori.append(f"Sitemap: lastmod {d!r} non valido o diverso dal registro per {u}")
    return errori, len(voci), len({d for _, d in voci})


# ---------------------------------------------------------------- 15. Visti Schengen a ingressi multipli (30/10/2026)
def controlla_mev():
    """15. Ricalcolo indipendente da dati/rifiuti.json (colonne 4 = visti uniformi rilasciati, 7 = di cui MEV): pagina riassuntiva
    in sitemap con titolo ≤ 70 e anno, prima frase con numero, fonte e data, tabelle per Stato e per Paese uguali ai dati,
    riquadro in ogni pagina per Paese (cifra e righe degli Stati con almeno 500 visti), link dall'indice e dalle pagine per Paese."""
    errori = []
    R = json.loads((SITO.parent / "dati" / "rifiuti.json").read_text(encoding="utf-8"))
    anni = sorted(R["schengen"], key=int)
    a1, a0 = anni[-1], anni[-2]
    soglia = 500
    righe = {a: R["schengen"][a] for a in (a1, a0)}
    if any(len(r) != 8 for a in righe for r in righe[a]):
        return ["MEV: righe di dati/rifiuti.json senza la colonna dei visti a ingressi multipli"], 0

    def somma(a, filtro):
        v = [0, 0]
        for r in righe[a]:
            if filtro(r):
                v[0] += r[4]
                v[1] += r[7]
        return v

    def pc(v):
        return f"{v[1] / v[0] * 100:.1f}%" if v[0] else "–"

    def leggi_righe(tabella):
        """[(nome, quota data-v, visti rilasciati, MEV)] dalle righe di una tabella MEV."""
        out = []
        for tr in re.findall(r"<tr><td>(.*?)</tr>", tabella, re.S):
            nome = re.sub(r"<[^>]+>", "", tr.split("</td>", 1)[0])
            dv = re.findall(r'data-v="([^"]*)"', tr)
            out.append((html.unescape(nome), dv[0], int(dv[3]), int(dv[4])))
        return out

    percorso = "visa-refusal-rates/multiple-entry-schengen-visa/"
    f = SITO / percorso / "index.html"
    if not f.exists():
        return [f"MEV: manca {percorso}"], 0
    t = f.read_text(encoding="utf-8")
    sitemap = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    if f"{G.URL_SITO}/{percorso}</loc>" not in sitemap:
        errori.append("MEV: pagina riassuntiva non in sitemap")
    titolo = html.unescape(re.search(r"<title>(.*?)</title>", t).group(1))
    if len(titolo) > 70 or a1 not in titolo:
        errori.append(f"MEV: titolo oltre 70 caratteri o senza l'anno: {titolo!r} ({len(titolo)})")
    tot1, tot0 = somma(a1, lambda r: True), somma(a0, lambda r: True)
    corpo = t.split('<main id="main">', 1)[1].split("</main>", 1)[0]
    prima = re.search(r'<p class="lead">(.*?)</p>', corpo, re.S).group(1)
    if (f"<strong>{pc(tot1)}</strong> of the {tot1[0]:,} uniform Schengen visas issued were multiple-entry visas ({tot1[1]:,})" not in prima
            or "European Commission" not in prima or "home-affairs.ec.europa.eu" not in prima or not RE_DATA.search(prima)):
        errori.append("MEV: prima frase senza numero ricalcolato, fonte (Commissione) o data")
    if f"<b>{pc(tot0)}</b><span>in {a0} ({tot0[1]:,} of {tot0[0]:,})</span>" not in corpo:
        errori.append(f"MEV: totale {a0} diverso dal ricalcolo")
    tabelle = re.findall(r"<table.*?</table>", corpo, re.S)
    if len(tabelle) != 2:
        errori.append(f"MEV: {len(tabelle)} tabelle nella pagina riassuntiva (attese 2)")
        return errori, 1
    # per Stato Schengen: tutti, valori uguali, ordine dalla quota più alta
    stati = sorted({r[0] for r in righe[a1]})
    lette = leggi_righe(tabelle[0])
    if sorted(x[0] for x in lette) != stati:
        errori.append(f"MEV: righe della tabella per Stato ({len(lette)}) diverse dai {len(stati)} Stati dei dati")
    for nome, dv, ril, mev in lette:
        v = somma(a1, lambda r, s=nome: r[0] == s)
        if [ril, mev] != v or abs(float(dv) - v[1] / v[0]) > 1e-6:
            errori.append(f"MEV: riga {nome} della tabella per Stato diversa dal ricalcolo ({v})")
    if [float(x[1]) for x in lette] != sorted((float(x[1]) for x in lette), reverse=True):
        errori.append("MEV: tabella per Stato non ordinata dalla quota più alta")
    # per Paese di domanda: i Paesi con almeno 10.000 domande (esclusi gli Stati Schengen), valori uguali
    dom = {}
    for r in righe[a1]:
        dom[r[1]] = dom.get(r[1], 0) + r[3]
    maiusc = {s.upper() for s in stati}
    paesi = {p for p, n in dom.items() if n >= G.SOGLIA_PAGINA and p not in maiusc}
    lette_p = leggi_righe(tabelle[1])
    if len(lette_p) != len(paesi):
        errori.append(f"MEV: {len(lette_p)} righe nella tabella per Paese, attese {len(paesi)}")
    per_nome = {html.unescape(G.nome_paese(p)): p for p in paesi}  # solo i nomi visibili (configurazione), i numeri si ricalcolano qui
    for nome, dv, ril, mev in lette_p:
        p = per_nome.get(nome)
        if not p:
            errori.append(f"MEV: Paese {nome} nella tabella ma non tra quelli con {G.SOGLIA_PAGINA:,}+ domande")
            continue
        v = somma(a1, lambda r, p=p: r[1] == p)
        if [ril, mev] != v or abs(float(dv) - v[1] / v[0]) > 1e-6:
            errori.append(f"MEV: riga {nome} della tabella per Paese diversa dal ricalcolo ({v})")
    for frase in ("FAQPage", '"@type": "Dataset"', "does not say how long", "not a long-stay visa", "Statistics, not advice."):
        if frase not in t:
            errori.append(f"MEV: manca {frase!r} nella pagina riassuntiva")
    if re.search(r"you will (get|receive|be given) a multiple|guarantee[ds]? a multiple", t, re.I):
        errori.append("MEV: promessa sul visto nella pagina riassuntiva")
    # riquadro nelle pagine per Paese
    n = 1
    for p in sorted(paesi):
        slug = G.SLUG_RIF[p]
        fp = SITO / "visa-refusal-rates" / slug / "index.html"
        tp = fp.read_text(encoding="utf-8")
        n += 1
        if 'id="multiple-entry"' not in tp or 'href="../multiple-entry-schengen-visa/"' not in tp:
            errori.append(f"MEV: riquadro o link alla pagina riassuntiva mancanti in {slug}")
            continue
        sez = tp.split('id="multiple-entry"', 1)[1].split("<h2>By consulate</h2>", 1)[0]
        v = somma(a1, lambda r, p=p: r[1] == p)
        if f"<strong>{pc(v)}</strong> were multiple-entry visas ({v[1]:,} of {v[0]:,} uniform visas issued)" not in sez:
            errori.append(f"MEV: cifra del riquadro di {slug} diversa dal ricalcolo ({pc(v)}, {v})")
        if "does not say how long" not in sez:
            errori.append(f"MEV: frase sulla durata mancante in {slug}")
        attesi = {}
        for r in righe[a1]:
            if r[1] == p:
                x = attesi.setdefault(r[0], [0, 0])
                x[0] += r[4]
                x[1] += r[7]
        attesi = {s: x for s, x in attesi.items() if x[0] >= soglia}
        tab = re.search(r"<table.*?</table>", sez, re.S)
        lette_s = leggi_righe(tab.group(0)) if tab else []
        if {x[0] for x in lette_s} != set(attesi):
            errori.append(f"MEV: Stati nella tabella di {slug} diversi da quelli con {soglia}+ visti rilasciati")
        for nome, dv, ril, mev in lette_s:
            if attesi.get(nome) != [ril, mev]:
                errori.append(f"MEV: riga {nome} di {slug} diversa dal ricalcolo ({attesi.get(nome)})")
        if [float(x[1]) for x in lette_s] != sorted((float(x[1]) for x in lette_s), reverse=True):
            errori.append(f"MEV: tabella di {slug} non ordinata dalla quota più alta")
    indice = (SITO / "visa-refusal-rates" / "index.html").read_text(encoding="utf-8")
    if 'href="multiple-entry-schengen-visa/"' not in indice or f"In {a1}, {pc(tot1)} of the {tot1[0]:,} uniform visas issued were multiple-entry visas" not in indice:
        errori.append("MEV: l'indice della sezione non rimanda alla pagina riassuntiva o ha un totale diverso")
    return errori, n


# ---------------------------------------------------------------- 16. Test di inglese per i visti UK (SELT), 30/10/2026
def controlla_selt():
    """16. Ricalcolo indipendente da dati/selt.json: impronta dei dati; pagine attese (indice + città e Paesi con domanda) tutte in
    sitemap e nessuna in più; titoli ≤ 70; prima frase con numero, fonte e data; righe delle tabelle = centri dell'elenco (nome e
    indirizzo); data del B2 solo se letta nella fonte ufficiale (HC 1691); nessun prezzo; avviso; JSON-LD; link di affiliazione
    solo italki (dominio ammesso, rel="sponsored noopener", riga di trasparenza) e solo se attivo in dati/affiliati.json."""
    import hashlib
    errori = []
    D = json.loads((SITO.parent / "dati" / "selt.json").read_text(encoding="utf-8"))
    aff = json.loads((SITO.parent / "dati" / "affiliati.json").read_text(encoding="utf-8")).get("_italki_selt", {})
    contenuto = {"centri": D["centri"], "test": D["test"]}
    if hashlib.sha256(json.dumps(contenuto, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != D["impronta"]:
        errori.append("SELT: impronta di dati/selt.json diversa dal contenuto (file modificato a mano?)")
    uk, est = D["centri"]["uk"], D["centri"]["estero"]
    if len(uk) != D["fonti"]["centri_uk"]["righe"] or len(est) != D["fonti"]["centri_estero"]["righe"]:
        errori.append("SELT: numero di centri diverso dalle righe del file ufficiale")
    soglia = D["domanda"]["soglia"]
    citta = sorted({r[2] for r in uk})
    paesi = sorted({r[2] for r in est})
    citta_pag = [c for c in citta if len(D["domanda"]["citta"].get(c, [])) >= soglia]
    paesi_pag = [p for p in paesi if len(D["domanda"]["paesi"].get(p, [])) >= soglia]
    sitemap = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    sez = SITO / "uk-english-test"
    attese = {"": None}
    attese.update({G.SLUG_SELT[c]: ("uk", c) for c in citta_pag})
    attese.update({G.SLUG_SELT[p]: ("estero", p) for p in paesi_pag})  # slug: configurazione del generatore; i numeri si ricalcolano qui
    trovate = {f.parent.relative_to(sez).as_posix().replace(".", "") for f in sez.rglob("index.html")}
    if trovate != set(attese):
        errori.append(f"SELT: pagine diverse da quelle attese (in più: {sorted(trovate - set(attese))[:5]}, mancanti: {sorted(set(attese) - trovate)[:5]})")
    hc = D["fonti"]["hc1691"]
    b2_ok = hc.get("in_vigore") == "2027-03-26" and any("come into force on 26 March 2027" in f for f in hc.get("frasi_memorandum", []))
    data_el = G.data_lunga(D["fonti"]["centri_uk"]["data_elenco"])
    url_it = aff.get("url", "")
    n = 0
    for slug, chi in attese.items():
        f = sez / slug / "index.html" if slug else sez / "index.html"
        if not f.exists():
            continue
        n += 1
        percorso = f"uk-english-test/{slug + '/' if slug else ''}"
        t = f.read_text(encoding="utf-8")
        main = t.split('<main id="main">', 1)[1].split("</main>", 1)[0]
        if f"{G.URL_SITO}/{percorso}</loc>" not in sitemap:
            errori.append(f"SELT: {percorso} non in sitemap")
        titolo = html.unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(titolo) > 70:
            errori.append(f"SELT: titolo oltre 70 caratteri in {percorso}: {titolo!r} ({len(titolo)})")
        prima = re.search(r'<p class="lead">(.*?)</p>', main, re.S).group(1)
        if data_el not in prima or not RE_DATA.search(prima):
            errori.append(f"SELT: prima frase senza la data dell'elenco in {percorso}")
        for frase in ("Not immigration or legal advice.", "FAQPage", "Open Government Licence v3.0", "list dated"):
            if frase not in t:
                errori.append(f"SELT: manca {frase!r} in {percorso}")
        if re.search(r"[£$€₹]\s?\d|\bRs\.?\s?\d|\bPKR\s?\d|\bINR\s?\d|\bGBP\s?\d", re.sub(r"<[^>]+>", " ", main)):
            errori.append(f"SELT: prezzo nella pagina {percorso} (nessuna fonte ufficiale del fornitore letta)")
        if "26 March 2027" in t and not b2_ok:
            errori.append(f"SELT: data del B2 in {percorso} senza la fonte ufficiale in dati/selt.json")
        # link di affiliazione
        sponsor = re.findall(r'<a [^>]*rel="([^"]*sponsored[^"]*)"[^>]*>', main) + re.findall(r'<a [^>]*href="([^"]*italki[^"]*)"', main)
        link_it = re.findall(r'<a [^>]*href="(https?://[^"]*italki\.com[^"]*)"[^>]*rel="([^"]*)"', main)
        if url_it:
            if len(link_it) != 1 or link_it[0][0] != html.escape(url_it) and link_it[0][0] != url_it or link_it[0][1] != "sponsored noopener":
                errori.append(f"SELT: riquadro italki assente, doppio o con rel sbagliato in {percorso}")
            if G.MON.RIGA_EN not in main:
                errori.append(f"SELT: riga di trasparenza mancante in {percorso}")
            if not G.MON.dominio_ammesso(url_it):
                errori.append("SELT: dominio del link italki non tra quelli ammessi in monetizzazione.json")
            if main.find("aff-i-h") < main.find("How to book</h2>") or main.find("How to book</h2>") < 0:
                errori.append(f"SELT: riquadro italki prima delle informazioni ufficiali in {percorso}")
        elif link_it or sponsor:
            errori.append(f"SELT: link di affiliazione in {percorso} ma _italki_selt non è attivo")
        for h, r in re.findall(r'<a [^>]*href="(https?://[^"]+)"[^>]*rel="([^"]*sponsored[^"]*)"', main):
            if "italki.com" not in h:
                errori.append(f"SELT: link sponsorizzato non ammesso in {percorso}: {h}")
        if chi is None:
            tot = f"<strong>{len(uk):,} approved centres in the UK</strong> or <strong>{len(est):,} outside the UK</strong>"
            if tot not in prima:
                errori.append("SELT: totali della prima frase dell'indice diversi dal ricalcolo")
            for tid, attesi in (("t-uk-c", {c: sum(1 for r in uk if r[2] == c) for c in citta}), ("t-est", {p: sum(1 for r in est if r[2] == p) for p in paesi})):
                tab = re.search(r'<table[^>]*id="%s".*?</table>' % tid, main, re.S)
                righe = re.findall(r'<tr><td>(.*?)</td><td class="n" data-v="(\d+)"', tab.group(0)) if tab else []
                if len(righe) != len(attesi) or sorted(int(x[1]) for x in righe) != sorted(attesi.values()) or sum(int(x[1]) for x in righe) != sum(attesi.values()):
                    errori.append(f"SELT: tabella {tid} dell'indice diversa dal ricalcolo ({len(righe)} righe, attese {len(attesi)})")
            if b2_ok and "B2 for settlement applications made on or after 26 March 2027" not in prima:
                errori.append("SELT: prima frase dell'indice senza il cambio B2 del 26 March 2027")
            continue
        dove, luogo = chi
        qui = [r for r in uk if r[2] == luogo] if dove == "uk" else [r for r in est if r[2] == luogo]
        m = len(qui)
        if f"<strong>{m:,} approved centre{'s' if m != 1 else ''}</strong>" not in prima:
            errori.append(f"SELT: numero di centri nella prima frase di {percorso} diverso da {m}")
        tab = re.search(r'<table[^>]*id="t-centri".*?</table>', main, re.S)
        righe = re.findall(r"<tr><td>", tab.group(0)) if tab else []
        if len(righe) != m:
            errori.append(f"SELT: {len(righe)} righe nella tabella di {percorso}, attesi {m} centri")
        corpo_tab = html.unescape(tab.group(0)) if tab else ""
        for r in qui:
            nome, ind = (r[1], r[3]) if dove == "uk" else (r[1], r[4])
            if nome not in corpo_tab or ind not in corpo_tab:
                errori.append(f"SELT: centro {nome!r} o indirizzo mancante in {percorso}")
                break
        if dove == "estero":
            for c in {r[3] for r in qui}:
                if f"<td>{html.escape(c)}</td>" not in tab.group(0):
                    errori.append(f"SELT: città {c} mancante in {percorso}")
    # collegamenti dal resto del sito
    for f, link in (("index.html", 'href="uk-english-test/"'), ("uk-spouse-visa/index.html", 'href="../uk-english-test/"')):
        if link not in (SITO / f).read_text(encoding="utf-8"):
            errori.append(f"SELT: {f} non rimanda alla sezione")
    return errori, n



# ---------------------------------------------------------------- 17. Irlanda: PPS assegnati per nazionalità (30/10/2026)
def _sorgente(url, nome_locale):
    """File ufficiale grezzo: da raccolta/_grezzi/ se c'è, altrimenti scaricato (None se offline o non raggiungibile)."""
    import urllib.request
    f = SITO.parent / "raccolta" / "_grezzi" / nome_locale
    if f.exists():
        return f.read_bytes()
    if "--offline" in sys.argv:
        return None
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
    except Exception:  # noqa: BLE001
        return None


def controlla_ppsn():
    """17. Ricalcolo indipendente da dati/ppsn.json: impronta; pagine 'nazionalità × Irlanda' attese (PPS ≥ 500 nell'ultimo anno intero
    o primi permessi Eurostat ≥ 500) tutte in sitemap; titoli ≤ 70 con l'anno; prima frase con il numero dell'anno in corso, quello
    dell'anno intero e la data della pagina gov.ie; tabella mese per mese e tabella anno per anno uguali ai dati; confronto con gli
    stessi mesi dell'anno prima; riquadro "what this number is" con le frasi di gov.ie; cifra Eurostat uguale a trasferimenti.json;
    blocco e link dalla pagina della nazionalità; colonna dell'indice. Più 10 valori a caso ricontrollati sui CSV ufficiali (letti qui
    con un lettore proprio, non con raccolta/ppsn.py)."""
    import csv
    import hashlib
    import io
    errori = []
    D = json.loads((SITO.parent / "dati" / "ppsn.json").read_text(encoding="utf-8"))
    TR = json.loads((SITO.parent / "dati" / "trasferimenti.json").read_text(encoding="utf-8"))
    cont = {"anni": D["anni"], "mesi": D["mesi"], "nazionalita": D["nazionalita"], "tutte": D["tutte"], "righe_sommate": D["righe_sommate"]}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != D["impronta"]:
        errori.append("PPS: impronta di dati/ppsn.json diversa dal contenuto (file modificato a mano?)")
    mesi = D["mesi"]
    ult = mesi[-1]
    ytd = ult[:4] if not ult.endswith("-12") else None
    pieno = str(int(ult[:4]) - 1) if ytd else ult[:4]
    mm = int(ult[5:])
    nomi_mesi = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    def num(n):
        return f"{n:,}"
    def var(a, b):
        x = (a - b) / b * 100
        return f"{'+' if x > 0 else '−'}{abs(x):.{2 if abs(x) < 0.05 else 1}f}%"
    sitemap = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    agg = G.data_lunga(D["fonti"]["pagina"]["aggiornata"])
    eu = TR["eurostat"]["dati"]
    y1 = TR["anni"][-1]
    n = 0
    for c, x in D["nazionalita"].items():
        s = G.NAZ_TR[c][0]
        atteso = (x["anni"].get(pieno) or 0) >= 500 or ((eu.get(c, {}).get("IE", {}).get(y1) or [0])[0] or 0) >= 500
        f = SITO / "moved-to" / s / "ireland" / "index.html"
        if f.exists() != atteso:
            errori.append(f"PPS: pagina {s}/ireland {'mancante' if atteso else 'in più'}")
        hub = (SITO / "moved-to" / s / "index.html").read_text(encoding="utf-8")
        if 'id="ireland-pps"' not in hub or (atteso and 'href="ireland/"' not in hub):
            errori.append(f"PPS: blocco o link all'Irlanda mancante nella pagina della nazionalità {s}")
        if not f.exists():
            continue
        n += 1
        percorso = f"moved-to/{s}/ireland/"
        t = f.read_text(encoding="utf-8")
        main = t.split('<main id="main">', 1)[1].split("</main>", 1)[0]
        if f"<loc>{G.URL_SITO}/{percorso}</loc>" not in sitemap:
            errori.append(f"PPS: {percorso} non in sitemap")
        titolo = html.unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(titolo) > 70 or (ytd or pieno) not in titolo:
            errori.append(f"PPS: titolo di {percorso} oltre 70 caratteri o senza l'anno: {titolo!r}")
        lead = re.search(r'<p class="lead">(.*?)</p>', main, re.S).group(1)
        n_ytd = sum(x["mesi"][f"{ytd}-{m:02d}"] for m in range(1, mm + 1)) if ytd else None
        n_ytd0 = sum(x["mesi"][f"{pieno}-{m:02d}"] for m in range(1, mm + 1)) if ytd else None
        if ytd and (f"<strong>{num(n_ytd)}</strong> PPS numbers to" not in lead or f"to {nomi_mesi[mm - 1]} {ytd}" not in lead):
            errori.append(f"PPS: numero dell'anno in corso di {percorso} diverso dai dati ({n_ytd})")
        if f"<strong>{num(x['anni'][pieno])}</strong> in {pieno}" not in lead or f"file updated on {agg}" not in lead:
            errori.append(f"PPS: numero {pieno} o data della fonte di {percorso} diversi dai dati")
        if ytd and (f"was {num(n_ytd0)}" not in lead or var(n_ytd, n_ytd0) not in lead):
            errori.append(f"PPS: confronto con gli stessi mesi del {pieno} di {percorso} diverso dai dati")
        piano = html.unescape(re.sub(r"<[^>]+>", "", main))
        if "It is not a count of people who arrived" not in piano or D["fonti"]["servizio"]["frasi"][1] not in piano:
            errori.append(f"PPS: riquadro 'what this number is' incompleto in {percorso}")
        # tabella mese per mese
        tab = re.search(r'id="t-pps-mesi">.*?<tbody>(.*?)</tbody>', main, re.S).group(1)
        anni_m = sorted({m[:4] for m in mesi})
        for i, riga in enumerate(re.findall(r'<tr><th scope="row">(\w+)</th>(.*?)</tr>', tab)):
            if riga[0] not in nomi_mesi:
                continue
            celle = re.findall(r'data-v="(\d*)"', riga[1])
            for a, v in zip(anni_m, celle):
                atteso_v = x["mesi"].get(f"{a}-{nomi_mesi.index(riga[0]) + 1:02d}")
                if (int(v) if v else None) != atteso_v:
                    errori.append(f"PPS: {percorso} {riga[0]} {a} = {v}, atteso {atteso_v}")
        # tabella anno per anno
        tab = re.search(r'id="t-pps-anni">.*?<tbody>(.*?)</tbody>', main, re.S).group(1)
        righe = re.findall(r'<tr><td>(\d{4})[^<]*</td><td class="n" data-v="(\d*)">', tab)
        if len(righe) != len(D["anni"]) or any(int(v) != x["anni"][a] for a, v in righe):
            errori.append(f"PPS: tabella anno per anno di {percorso} diversa dai dati")
        r1 = eu.get(c, {}).get("IE", {}).get(y1)
        if r1 and r1[0] and r1[0] >= 100 and f"<strong>{num(r1[0])}</strong> first residence permits" not in main:
            errori.append(f"PPS: cifra Eurostat {y1} di {percorso} diversa da trasferimenti.json")
        for frase in ("FAQPage", "Dataset", "BreadcrumbList", "CC BY 4.0", "What this number is, and what it is not"):
            if frase not in t:
                errori.append(f"PPS: manca {frase!r} in {percorso}")
    idx = (SITO / "moved-to" / "index.html").read_text(encoding="utf-8")
    if f"Ireland PPS {pieno}" not in idx or 'id="ireland"' not in idx:
        errori.append("PPS: colonna o sezione Irlanda mancanti nell'indice moved-to")
    # 10 valori a caso ricontrollati sui CSV ufficiali (lettore indipendente)
    rng = random.Random(20261030)
    grezzi = {}
    for k in ("mensile", "annuale"):
        b = _sorgente(D["fonti"][k]["url"], f"ppsn-{k}.csv")
        if b is not None and hashlib.sha256(b).hexdigest() != D["fonti"][k]["sha256"]:
            errori.append(f"PPS: il file {k} in raccolta/_grezzi/ non è quello usato per i dati (SHA-256 diverso)")
        grezzi[k] = list(csv.reader(io.StringIO(b.decode("utf-8-sig")))) if b else None
    ricontrollati = []
    if grezzi["mensile"] and grezzi["annuale"]:
        campioni = [("m", c, m) for c in D["nazionalita"] for m in mesi] + [("a", c, a) for c in D["nazionalita"] for a in D["anni"]]
        for tipo, c, k in rng.sample(campioni, 10):
            nome = D["nazionalita"][c]["nome"]
            if tipo == "m":
                etich = f"{k[:4]} {nomi_mesi[int(k[5:]) - 1]}"
                v = sum(int(r[4]) for r in grezzi["mensile"][1:] if r[2] == nome and r[1] == etich and r[4].strip().isdigit())
                dj = D["nazionalita"][c]["mesi"][k]
                pag = SITO / "moved-to" / G.NAZ_TR[c][0] / "ireland" / "index.html"
                ok_pag = True
                if pag.exists():
                    tab = re.search(r'id="t-pps-mesi">.*?<tbody>(.*?)</tbody>', pag.read_text(encoding="utf-8"), re.S).group(1)
                    riga = re.search(rf'<th scope="row">{nomi_mesi[int(k[5:]) - 1]}</th>(.*?)</tr>', tab).group(1)
                    ok_pag = re.findall(r'data-v="(\d*)"', riga)[sorted({m[:4] for m in mesi}).index(k[:4])] == str(v)
            else:
                v = sum(int(r[4]) for r in grezzi["annuale"][1:] if r[2] == nome and r[0] == k)
                dj = D["nazionalita"][c]["anni"][k]
                pag = SITO / "moved-to" / G.NAZ_TR[c][0] / "ireland" / "index.html"
                ok_pag = (not pag.exists()) or bool(re.search(rf'<tr><td>{k}[^<]*</td><td class="n" data-v="{v}">', pag.read_text(encoding="utf-8")))
            ricontrollati.append(f"{c} {k}: file {v}, dati {dj}, pagina {'ok' if ok_pag else 'DIVERSA'}")
            if v != dj or not ok_pag:
                errori.append(f"PPS: valore ricontrollato diverso dal file ufficiale: {c} {k} (file {v}, dati {dj})")
    return errori, n, ricontrollati


# ---------------------------------------------------------------- 18. Thailand DTV visa, ambasciata per ambasciata (30/10/2026)
def controlla_dtv(online=True):
    """18. Ricalcolo indipendente da dati/dtv.json: impronta; pagine attese (indice + sedi con domanda e con costo o regola sulla
    residenza) tutte in sitemap e nessuna in più; titoli ≤ 70; prima frase con risposta, fonte e data; righe della tabella = sedi lette,
    con costo e regola uguali ai dati; frammenti citati presenti; avviso "Not legal or immigration advice"; nessuna promessa
    sull'approvazione; link di affiliazione solo SafetyWing (sponsored noopener, riga di trasparenza, dopo le informazioni ufficiali,
    con la frase che l'assicurazione non è richiesta); collegamenti dal resto del sito. Online: 10 frammenti a caso ricontrollati
    sulle pagine ufficiali riscaricate (con --offline si salta)."""
    import hashlib
    errori = []
    D = json.loads((SITO.parent / "dati" / "dtv.json").read_text(encoding="utf-8"))
    aff = json.loads((SITO.parent / "dati" / "affiliati.json").read_text(encoding="utf-8")).get("_safetywing_dtv", {})
    cont = {"sedi": D["sedi"], "letture": D["letture"], "generale": D["generale"]}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != D["impronta"]:
        errori.append("DTV: impronta di dati/dtv.json diversa dal contenuto (file modificato a mano?)")
    L = D["letture"]
    con_pag = [x["id"] for x in L if x["domanda"] and ("costo" in x or "residenza" in x)]
    sez = SITO / "thailand-dtv-visa"
    trovate = {f.parent.relative_to(sez).as_posix().replace(".", "") for f in sez.rglob("index.html")}
    if trovate != set([""] + con_pag):
        errori.append(f"DTV: pagine diverse da quelle attese (in più {sorted(trovate - set([''] + con_pag))}, mancanti {sorted(set([''] + con_pag) - trovate)})")
    sitemap = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    letto = G.data_lunga(D["letto_il"])
    def costo(c):
        pre, post = {"GBP": ("£", ""), "USD": ("US$", ""), "EUR": ("€", ""), "THB": ("", " baht (THB)"), "MYR": ("RM", ""), "SGD": ("S$", ""),
                     "EGP": ("", " Egyptian pounds (EGP)"), "PLN": ("", " złoty (PLN)"), "INR": ("₹", ""), "CNY": ("", " yuan (CNY)")}[c["valuta"]]
        return f"{pre}{c['importo']:,}{post}"
    n = 0
    for slug in [""] + con_pag:
        f = sez / slug / "index.html" if slug else sez / "index.html"
        if not f.exists():
            continue
        n += 1
        percorso = f"thailand-dtv-visa/{slug + '/' if slug else ''}"
        t = f.read_text(encoding="utf-8")
        main = t.split('<main id="main">', 1)[1].split("</main>", 1)[0]
        testo_main = html.unescape(re.sub(r"<[^>]+>", " ", main))
        if f"<loc>{G.URL_SITO}/{percorso}</loc>" not in sitemap:
            errori.append(f"DTV: {percorso} non in sitemap")
        titolo = html.unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(titolo) > 70:
            errori.append(f"DTV: titolo oltre 70 caratteri in {percorso}: {titolo!r} ({len(titolo)})")
        lead = html.unescape(re.sub(r"<[^>]+>", "", re.search(r'<p class="lead">(.*?)</p>', main, re.S).group(1)))
        if letto not in lead:
            errori.append(f"DTV: prima frase senza la data di lettura in {percorso}")
        for frase in ("Not legal or immigration advice.", "FAQPage", "BreadcrumbList", "31 August 2026"):
            if frase not in t:
                errori.append(f"DTV: manca {frase!r} in {percorso}")
        if re.search(r"\b(guarantee[sd]?|will be approved|will get (?:a|the|your) visa|100% approval|easy approval)\b", testo_main, re.I):
            errori.append(f"DTV: promessa sull'approvazione in {percorso}")
        # affiliazione
        sw = re.findall(r'<a [^>]*href="([^"]*safetywing[^"]*)"[^>]*rel="([^"]*)"', main)
        altri_sp = [h for h in re.findall(r'<a [^>]*href="([^"]+)"[^>]*rel="[^"]*sponsored', main) if "safetywing.com" not in h]
        if altri_sp:
            errori.append(f"DTV: link sponsorizzati non ammessi in {percorso}: {altri_sp[:2]}")
        if aff.get("url"):
            if len(sw) != 1 or html.unescape(sw[0][0]) != aff["url"] or sw[0][1] != "sponsored noopener":
                errori.append(f"DTV: riquadro SafetyWing assente, doppio o con rel sbagliato in {percorso}")
            if G.MON.RIGA_EN not in main or "Insurance is not a DTV requirement" not in main or "does not change the decision on your visa" not in main:
                errori.append(f"DTV: riga di trasparenza o frase 'assicurazione non richiesta' mancanti in {percorso}")
            if main.find("safetywing") < main.find("What the official page says" if slug else 'id="table"'):
                errori.append(f"DTV: SafetyWing prima delle informazioni ufficiali in {percorso}")
        elif sw:
            errori.append(f"DTV: link SafetyWing in {percorso} ma voce spenta in dati/affiliati.json")
        if slug:
            x = next(y for y in L if y["id"] == slug)
            if "costo" in x and costo(x["costo"]) not in lead:
                errori.append(f"DTV: costo di {slug} nella prima frase diverso dai dati ({costo(x['costo'])})")
            for campo in ("costo", "residenza", "saldo"):
                if campo in x and html.escape(x[campo]["frammento"].rstrip("."), quote=False) not in main:
                    errori.append(f"DTV: frammento {campo} di {slug} non citato nella pagina")
            agg = G.data_lunga(max(p["modificata"] for p in x["pagine"]))
            if agg not in lead:
                errori.append(f"DTV: data di modifica della pagina ufficiale mancante nella prima frase di {slug}")
        else:
            tab = re.search(r'id="t-dtv">.*?<tbody>(.*?)</tbody>', main, re.S).group(1)
            righe = re.findall(r"<tr>(.*?)</tr>", tab, re.S)
            if len(righe) != len(L):
                errori.append(f"DTV: la tabella dell'indice ha {len(righe)} righe, attese {len(L)}")
            for x in L:
                riga = next((r for r in righe if re.search(rf'>{re.escape(html.escape(x["sede"], quote=False))}<', r)), None)
                if not riga:
                    errori.append(f"DTV: riga di {x['sede']} mancante nell'indice")
                    continue
                if ("costo" in x and costo(x["costo"]) not in html.unescape(riga)) or ("costo" not in x and "Not written on the page" not in riga):
                    errori.append(f"DTV: costo di {x['sede']} nell'indice diverso dai dati")
                if "residenza" in x and html.escape(x["residenza"]["frammento"].rstrip("."), quote=False) not in riga:
                    errori.append(f"DTV: regola sulla residenza di {x['sede']} nell'indice diversa dai dati")
                if html.escape(x["pagine"][0]["url"]) not in riga and x["pagine"][0]["url"] not in riga:
                    errori.append(f"DTV: link ufficiale di {x['sede']} mancante nell'indice")
            altre = re.search(r'id="t-altre">.*?<tbody>(.*?)</tbody>', main, re.S).group(1)
            if len(re.findall(r"<tr>", altre)) + len(L) != len(D["sedi"]):
                errori.append("DTV: sedi lette + altre sedi diverso dall'elenco ufficiale")
            for v in ("vientiane", "london", "washington-dc"):
                x = next(y for y in L if y["id"] == v)
                if costo(x["costo"]) not in lead:
                    errori.append(f"DTV: costo di {v} mancante nella prima frase dell'indice")
            if "60 countries and territories" not in main or "15 September 2026" not in main:
                errori.append("DTV: sezione sull'esenzione di 30 giorni mancante o incompleta")
    for f, link in (("index.html", 'href="thailand-dtv-visa/"'), ("digital-nomad-visa-income-requirements/index.html", 'href="../thailand-dtv-visa/"'),
                    ("how-it-works/index.html", 'href="../thailand-dtv-visa/"')):
        if link not in (SITO / f).read_text(encoding="utf-8"):
            errori.append(f"DTV: {f} non rimanda alla sezione")
    if "Thailand (DTV)," in (SITO / "digital-nomad-visa-income-requirements" / "index.html").read_text(encoding="utf-8"):
        errori.append("DTV: la pagina dei nomadi elenca ancora la Thailandia tra i visti non coperti")
    # 10 frammenti a caso ricontrollati sulle pagine ufficiali riscaricate
    ricontrollati = []
    if online:
        sys.path.insert(0, str(SITO.parent / "raccolta"))
        import dtv as R  # solo per scaricare e normalizzare il testo nello stesso modo
        rng = random.Random(20261030)
        campioni = [(x["id"], campo, v) for x in L for campo in ("costo", "residenza", "saldo") if campo in x for v in [x[campo]]]
        campioni += [(x["id"], "altre", a) for x in L for a in x.get("altre", [])]
        for sid, campo, v in rng.sample(campioni, 10):
            x = next(y for y in L if y["id"] == sid)
            u = x["pagine"][v["p"]]["url"]
            letta = R.leggi(u)
            ok = letta["ok"] and v["frammento"] in letta["_testo"]
            ricontrollati.append(f"{sid} {campo}: {'presente' if ok else 'ASSENTE'} ({v['frammento'][:50]}…)")
            if not ok:
                errori.append(f"DTV: frammento non più nella pagina ufficiale: {sid} {campo} ({u})")
    return errori, n, ricontrollati

# ---------------------------------------------------------------- 19-20. Sezioni per studenti: US OPT e UK Graduate visa (30/10/2026)
from datetime import date as _date, timedelta as _td
import calendar as _cal


def _d(s):
    try:
        return _date.fromisoformat(s) if s else None
    except ValueError:
        return None


def _am(d, n):
    """Aggiunge n mesi; se il giorno non esiste nel mese di arrivo, ultimo giorno del mese."""
    y, m = divmod(d.month - 1 + n, 12)
    y += d.year
    return _date(y, m + 1, min(d.day, _cal.monthrange(y, m + 1)[1]))


def py_finestra(fine, dso, k):
    e = _d(fine)
    if not e:
        return None
    r = {"apre": (e - _td(k["prima"])).isoformat(), "chiude": (e + _td(k["dopo"])).isoformat(), "limite": "fine",
         "inizio_max": (e + _td(k["inizio"])).isoformat(), "chiude_30": (e + _td(k["nuova"])).isoformat()}
    d = _d(dso)
    if d:
        l = (d + _td(k["dso"])).isoformat()
        r["dso_entro"] = l
        if l < r["chiude"]:
            r["chiude"], r["limite"] = l, "dso"
        r["chiude_30"] = min(r["chiude_30"], l)
        if d.isoformat() > r["apre"]:
            r["apre"], r["apre_dso"] = d.isoformat(), True
    r["impossibile"] = r["apre"] > r["chiude"]
    return r


def py_disoccupazione(inizio, limite, usati, oggi):
    s = _d(inizio)
    if not s:
        return None
    r = {"limite": limite, "ultimo": (s + _td(limite - 1)).isoformat(), "oltre": (s + _td(limite)).isoformat()}
    if usati is not None:
        u = max(0, int(usati))
        r["usati"], r["rimasti"] = u, max(0, limite - u)
        if r["rimasti"] > 0:
            r["ultimo_da_oggi"] = (_d(oggi) + _td(r["rimasti"] - 1)).isoformat()
    return r


def py_stem(scad, dso, k):
    e = _d(scad)
    if not e:
        return None
    r = {"apre": (e - _td(k["prima"])).isoformat(), "scade": e.isoformat(), "proroga_fino": (e + _td(k["proroga"])).isoformat()}
    d = _d(dso)
    if d:
        r["dso_entro"] = (d + _td(k["dso"])).isoformat()
        if d.isoformat() > r["apre"]:
            r["apre"], r["apre_dso"] = d.isoformat(), True
    r["impossibile"] = r["apre"] >= r["scade"] or bool(r.get("dso_entro") and r["dso_entro"] < r["apre"])
    return r


def py_graduate(dom, tipo, dec, scad, k):
    a = _d(dom)
    if not a:
        return None
    m = k["m_phd"] if tipo == "phd" else (k["m_prima"] if dom < k["cambio"] else k["m_dopo"])
    d8 = a + _td(k["sett"] * 7)
    r = {"mesi": m, "prima_del_cambio": dom < k["cambio"], "giorni_al_cambio": (_d(k["cambio"]) - a).days, "fine_subito": _am(a, m).isoformat(),
         "decisione_8": d8.isoformat(), "fine_8": _am(d8, m).isoformat()}
    d = _d(dec)
    if d:
        if d.isoformat() < dom:
            r["dec_errore"] = True
        else:
            r["decisione"], r["fine"] = d.isoformat(), _am(d, m).isoformat()
    s = _d(scad)
    if s:
        r["scad"], r["tardi"] = s.isoformat(), dom >= s.isoformat()
    return r


def py_costo(mesi, adulti, figli, k):
    ia, im = k["ihs_a"] * mesi / 12, k["ihs_m"] * mesi / 12
    t, i = (adulti + figli) * k["tassa"], adulti * ia + figli * im
    return {"tasse": t, "ihs": i, "totale": t + i, "ihs_adulto": ia, "ihs_figlio": im, "persone": adulti + figli}


def casi_studio(seme=30, n=400):
    rng = random.Random(seme)
    def gd(a="2026-01-01", b="2028-12-31"):
        x, y = _date.fromisoformat(a), _date.fromisoformat(b)
        return (x + _td(rng.randint(0, (y - x).days))).isoformat()
    fissi = [("finestra", ["2026-12-18", "", None]), ("finestra", ["2027-05-15", "2027-06-01", None]), ("finestra", ["2027-08-31", "2027-05-20", None]),
             ("disoccupazione", ["2026-06-01", 90, 20, "2026-10-30"]), ("disoccupazione", ["2027-01-10", 150, None, "2026-10-30"]),
             ("stem", ["2027-03-31", "", None]), ("stem", ["2026-11-15", "2026-11-20", None]),
             ("graduate", ["2026-12-31", "altro", "", "", None]), ("graduate", ["2027-01-01", "altro", "2027-02-20", "", None]),
             ("graduate", ["2028-08-31", "altro", "", "", None]), ("graduate", ["2027-03-10", "phd", "", "2027-02-01", None]),
             ("costo", [18, 2, 1, None]), ("costo", [24, 1, 0, None]), ("costo", [36, 3, 2, None])]
    casuali = []
    for _ in range(n):
        tipo = rng.choice(["finestra", "disoccupazione", "stem", "graduate", "costo"])
        if tipo == "finestra":
            f = gd()
            casuali.append((tipo, [f, rng.choice(["", (_d(f) + _td(rng.randint(-120, 90))).isoformat()]), None]))
        elif tipo == "disoccupazione":
            casuali.append((tipo, [gd(), rng.choice([90, 150]), rng.choice([None, rng.randint(0, 160)]), gd("2026-10-01", "2027-12-31")]))
        elif tipo == "stem":
            f = gd()
            casuali.append((tipo, [f, rng.choice(["", (_d(f) + _td(rng.randint(-150, 30))).isoformat()]), None]))
        elif tipo == "graduate":
            a = gd("2026-06-01", "2028-06-30")
            casuali.append((tipo, [a, rng.choice(["altro", "phd"]), rng.choice(["", (_d(a) + _td(rng.randint(-10, 200))).isoformat()]),
                                   rng.choice(["", gd("2026-06-01", "2028-06-30")]), None]))
        else:
            casuali.append((tipo, [rng.choice([18, 24, 36]), rng.randint(1, 4), rng.randint(0, 4), None]))
    return fissi + casuali


def confronta_js_studio(file_pagina, k_tutti):
    """Esegue con node il JS dei calcolatori preso dalla pagina pubblicata e lo confronta con le funzioni Python qui sopra."""
    t = (SITO / file_pagina).read_text(encoding="utf-8")
    js = next(s for s in re.findall(r"<script>(.*?)</script>", t, re.S) if "window.CALC_STUDIO=C" in s)
    casi = casi_studio()
    prog = ("var window={};var document={querySelectorAll:function(){return [];}};\n" + js +
            "\nvar K=" + json.dumps(k_tutti) + ";var CASI=" + json.dumps(casi) + ";var C=window.CALC_STUDIO;var out=CASI.map(function(c){var a=c[1];"
            "if(c[0]==='finestra')return C.finestra(a[0],a[1],K.finestra);if(c[0]==='disoccupazione')return C.disoccupazione(a[0],a[1],a[2]===null?'':a[2],a[3]);"
            "if(c[0]==='stem')return C.stem(a[0],a[1],K.stem);if(c[0]==='graduate')return C.graduate(a[0],a[1],a[2],a[3],K.graduate);"
            "return C.costo(a[0],a[1],a[2],K.graduate);});console.log(JSON.stringify(out));")
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(prog)
    r = subprocess.run(["node", f.name], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        return [f"JS dei calcolatori non eseguibile: {r.stderr[-300:]}"], 0
    ris = json.loads(r.stdout)
    errori = []
    for (tipo, a), j in zip(casi, ris):
        if tipo == "finestra":
            p = py_finestra(a[0], a[1], k_tutti["finestra"])
        elif tipo == "disoccupazione":
            p = py_disoccupazione(a[0], a[1], a[2], a[3])
        elif tipo == "stem":
            p = py_stem(a[0], a[1], k_tutti["stem"])
        elif tipo == "graduate":
            p = py_graduate(a[0], a[1], a[2], a[3], k_tutti["graduate"])
        else:
            p = py_costo(a[0], a[1], a[2], k_tutti["graduate"])
        if p != j:
            errori.append(f"calcolatore {tipo} {a}: JS {j} ≠ Python {p}")
    return errori[:10], len(casi)


def _pagine_sezione(sez, attese, errori, nome, affiliati=False):
    cart = SITO / sez.rstrip("/")
    trovate = {f.parent.relative_to(cart).as_posix().replace(".", "") for f in cart.rglob("index.html")}
    if trovate != set(attese):
        errori.append(f"{nome}: pagine diverse da quelle attese (in più {sorted(trovate - set(attese))}, mancanti {sorted(set(attese) - trovate)})")
    sitemap = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    out = {}
    for s in attese:
        f = cart / s / "index.html" if s else cart / "index.html"
        if not f.exists():
            continue
        percorso = f"{sez}{s + '/' if s else ''}"
        t = f.read_text(encoding="utf-8")
        main = t.split('<main id="main">', 1)[1].split("</main>", 1)[0]
        if f"<loc>{G.URL_SITO}/{percorso}</loc>" not in sitemap:
            errori.append(f"{nome}: {percorso} non in sitemap")
        titolo = html.unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(titolo) > 70:
            errori.append(f"{nome}: titolo oltre 70 caratteri in {percorso} ({len(titolo)})")
        for x in ("FAQPage", "BreadcrumbList", "Not legal or immigration advice.", 'rel="canonical"'):
            if x not in t:
                errori.append(f"{nome}: manca {x!r} in {percorso}")
        if not affiliati and re.search(r'rel="[^"]*sponsored', main):
            errori.append(f"{nome}: link sponsorizzato in {percorso} (nessuna affiliazione prevista in questa sezione)")
        lead = html.unescape(re.sub(r"<[^>]+>", "", re.search(r'<p class="lead">(.*?)</p>', main, re.S).group(1)))
        out[s] = (t, main, html.unescape(re.sub(r"<[^>]+>", " ", main)), lead, percorso)
    return out


def controlla_opt(online=True):
    import hashlib
    errori = []
    D = json.loads((SITO.parent / "dati" / "opt.json").read_text(encoding="utf-8"))
    cont = {k: D[k] for k in ("letture", "fonti", "federal_register", "ecfr")}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != D["impronta"]:
        errori.append("OPT: impronta di dati/opt.json diversa dal contenuto")
    L = {k: v["valore"] for k, v in D["letture"].items()}
    fr = D["federal_register"]
    letto = G.data_lunga(D["letto_il"])
    attese = ["", "opt-application-deadline-calculator", "opt-unemployment-days", "stem-opt-extension-fee", "opt-fee-proposal", "opt-grace-period"]
    P = _pagine_sezione("us-opt/", attese, errori, "OPT")
    usd = lambda n: f"${n:,}"  # noqa: E731
    k_fin = {"prima": L["finestra"]["prima"], "dopo": L["finestra"]["dopo"], "dso": L["finestra"]["dso"], "inizio": L["inizio_max"], "nuova": L["regola_30"]}
    k_stem = {"prima": L["finestra_stem"]["prima"], "dso": L["finestra_stem"]["dso"], "proroga": L["proroga_stem"]}
    k_dis = {"opt": L["disoccupazione"], "stem": L["disoccupazione_stem"]}
    if L["finestra"] != L["finestra_opt"] or L["disoccupazione_uscis"] != k_dis or L["mesi_opt"] != L["mesi_opt_uscis"] or L["finestra_stem_i765"] != L["finestra_stem"]["prima"]:
        errori.append("OPT: due fonti ufficiali danno valori diversi per la stessa regola (letture)")
    calcolatori = {"": ("finestra", "disoccupazione"), "opt-application-deadline-calculator": ("finestra",), "opt-unemployment-days": ("disoccupazione",),
                   "stem-opt-extension-fee": ("stem",), "opt-grace-period": ("finestra",), "opt-fee-proposal": ()}
    costanti = {"finestra": k_fin, "disoccupazione": k_dis, "stem": k_stem}
    for s, (t, main, testo, lead, percorso) in P.items():
        if letto not in lead or re.search(r"\. [A-Z]", lead.split(letto)[0]):
            errori.append(f"OPT: data di lettura non nella prima frase in {percorso}")
        primo = lead.split(f"{letto}")[0]
        if not re.search(r"USCIS|SEVP|Federal Register", primo):
            errori.append(f"OPT: prima frase senza la fonte prima della data in {percorso}")
        for tipo in calcolatori[s]:
            m = re.search(rf'data-studio="{tipo}" data-k=\'(.*?)\'', main)
            if not m or json.loads(m.group(1)) != costanti[tipo]:
                errori.append(f"OPT: calcolatore {tipo} assente o con costanti diverse dai dati in {percorso}")
        if calcolatori[s] and "window.CALC_STUDIO=C" not in t:
            errori.append(f"OPT: script dei calcolatori mancante in {percorso}")
        if usd(L["proposta_importi"]["iniziale"]) in testo:
            pezzi = re.split(r"[.:|]\s", html.unescape(re.sub(r"<[^>]+>", " | ", main)))
            for frase in [x for x in pezzi if "$70,000" in x]:
                if re.search(r"\b(is|are) (now )?in force|takes effect on|must pay \$70", frase) and "not in force" not in frase and "Is the" not in frase:
                    errori.append(f"OPT: frase che presenta la proposta come regola in {percorso}: {frase.strip()[:120]}")
    if "" in P:
        t, main, testo, lead, _ = P[""]
        for x in (usd(L["tassa_online"]), usd(L["tassa_carta"]), usd(L["premium"]), f'{L["finestra"]["prima"]} days', f'{L["finestra"]["dopo"]} days',
                  f'{k_dis["opt"]} days', f'{k_dis["stem"]} days', f'{L["mesi_stem"]} months', "Proposal", "Final rule on hold", "In force"):
            if x not in testo:
                errori.append(f"OPT: indice senza {x!r}")
        for u in [v["url"] for v in D["fonti"].values()] + [v["html_url"] for v in fr.values()]:
            if html.escape(u) not in main and u not in main:
                errori.append(f"OPT: fonte non citata nell'indice: {u}")
    if "stem-opt-extension-fee" in P:
        testo = P["stem-opt-extension-fee"][2]
        for x in (usd(L["tassa_online"]), usd(L["tassa_carta"]), usd(L["premium"]), f'{L["proroga_stem"]} days', usd(L["proposta_importi"]["successiva"])):
            if x not in testo:
                errori.append(f"OPT: pagina STEM senza {x!r}")
    if "opt-fee-proposal" in P:
        testo = P["opt-fee-proposal"][2]
        for x in ("$70,000", "$30,000", "not in force", G.data_lunga(fr["tasse_opt"]["comments_close_on"]), fr["tasse_opt"]["citation"], "ICEB-2026-0100", "school"):
            if x not in testo:
                errori.append(f"OPT: pagina della proposta senza {x!r}")
        if fr["tasse_opt"]["type"] != "Proposed Rule" or L["proposta_importi"] != {"iniziale": 70000, "successiva": 30000}:
            errori.append("OPT: la proposta non è più una proposta da 70.000/30.000 $: rivedere i testi (anche le domande scritte a mano)")
    if "opt-grace-period" in P:
        testo = P["opt-grace-period"][2]
        for x in ("postponed", "60 days", f'{L["regola_30"]} days', G.data_lunga(L["rinvio_regola"]), "previous regulatory provisions", D["ecfr"]["precedente"]["url"]):
            if x not in testo and html.escape(x) not in P["opt-grace-period"][1]:
                errori.append(f"OPT: pagina del periodo di grazia senza {x!r}")
    if "opt-unemployment-days" in P:
        if "Count each day without employer information" not in D["letture"]["conteggio_giorni"]["frammento"] or "each day without employer information" not in P["opt-unemployment-days"][2]:
            errori.append("OPT: regola di conteggio dei giorni di disoccupazione mancante")
    for f, link in (("index.html", 'href="us-opt/"'), ("how-it-works/index.html", 'href="../us-opt/"'), ("about/index.html", 'href="../us-opt/"')):
        if link not in (SITO / f).read_text(encoding="utf-8"):
            errori.append(f"OPT: {f} non rimanda alla sezione")
    e_js, n_js = confronta_js_studio("us-opt/index.html", {"finestra": k_fin, "stem": k_stem, "graduate": json.loads(re.search(
        r'data-studio="graduate" data-k=\'(.*?)\'', (SITO / "uk-graduate-visa/index.html").read_text(encoding="utf-8")).group(1))})
    errori += e_js
    riletti = []
    if online:
        for k, d in fr.items():
            try:
                x = json.loads(urllib.request.urlopen(f"https://www.federalregister.gov/api/v1/documents/{d['document_number']}.json", timeout=60).read())
                ok = all(x.get(c) == d.get(c) for c in ("type", "publication_date", "effective_on", "comments_close_on", "citation"))
            except Exception as e:  # noqa: BLE001
                ok, x = False, {"errore": str(e)[:80]}
            riletti.append(f"Federal Register {d['citation']}: {'uguale' if ok else 'CAMBIATO'}")
            if not ok:
                errori.append(f"OPT: documento del Federal Register cambiato o non leggibile: {d['citation']}")
        r = subprocess.run(["node", str(SITO.parent / "raccolta" / "browser.js"), D["fonti"]["i765"]["url"]], capture_output=True, text=True, timeout=300)
        try:
            tx = json.loads(r.stdout)[D["fonti"]["i765"]["url"]]["testo"]
        except (ValueError, KeyError):
            tx = ""
        for k in ("finestra", "finestra_stem_i765", "rinvio_regola", "regole_precedenti"):
            ok = D["letture"][k]["frammento"] in tx
            riletti.append(f"USCIS I-765 {k}: {'presente' if ok else 'ASSENTE'}")
            if not ok:
                errori.append(f"OPT: frammento {k} non più nella pagina I-765 di USCIS")
    return errori, len(P), n_js, riletti


def controlla_graduate(online=True):
    import hashlib
    errori = []
    D = json.loads((SITO.parent / "dati" / "graduate.json").read_text(encoding="utf-8"))
    cont = {k: D[k] for k in ("letture", "fonti", "tariffa_ods")}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != D["impronta"]:
        errori.append("Graduate: impronta di dati/graduate.json diversa dal contenuto")
    L = {k: v["valore"] for k, v in D["letture"].items()}
    letto = G.data_lunga(D["letto_il"])
    k = {"cambio": L["durata_18_mesi"]["dal"], "m_prima": L["durata_2_anni"]["mesi"], "m_dopo": L["durata_18_mesi"]["mesi"], "m_phd": L["durata_phd"]["mesi"],
         "sett": L["decisione_settimane"], "tassa": L["tassa"], "ihs_a": L["ihs_adulti"], "ihs_m": L["ihs_minori"]}
    if (k["cambio"], k["m_prima"], k["m_dopo"], k["m_phd"], L["durata_2_anni"]["fino_al"]) != ("2027-01-01", 24, 18, 36, "2026-12-31"):
        errori.append("Graduate: durate o date diverse da quelle scritte nei testi delle pagine: rivedere i testi")
    if L["ihs_anno"] != L["ihs_adulti"] or abs(L["ihs_18"] - 1.5 * L["ihs_adulti"]) > 0.001 or L["ihs_24"] != 2 * L["ihs_adulti"] or L["ihs_36"] != 3 * L["ihs_adulti"]:
        errori.append("Graduate: importi della guida e della pagina IHS non coerenti")
    if D["tariffa_ods"]["riga"][2] != f"£{L['tassa']:,}":
        errori.append("Graduate: tariffa della tabella ODS diversa dalla guida")
    P = _pagine_sezione("uk-graduate-visa/", ["", "18-months", "cost", "phd"], errori, "Graduate")
    gbp = lambda x: "£" + (f"{x:,.2f}"[:-3] if f"{x:,.2f}".endswith(".00") else f"{x:,.2f}")  # noqa: E731
    for s, (t, main, testo, lead, percorso) in P.items():
        if letto not in lead or re.search(r"\. [A-Z]", lead.split(letto)[0]):
            errori.append(f"Graduate: data di lettura non nella prima frase in {percorso}")
        if not re.search(r"GOV\.UK|Immigration Rules", lead.split(letto)[0]):
            errori.append(f"Graduate: prima frase senza fonte in {percorso}")
        m = re.search(r'data-studio="graduate" data-k=\'(.*?)\'', main)
        if not m or json.loads(m.group(1)) != k:
            errori.append(f"Graduate: calcolatore assente o con costanti diverse dai dati in {percorso}")
        if "Open Government Licence v3.0" not in testo:
            errori.append(f"Graduate: manca l'attribuzione OGL in {percorso}")
        for x in ("1 January 2027", "18 months", "3 years", gbp(L["tassa"])):
            if x not in testo:
                errori.append(f"Graduate: manca {x!r} in {percorso}")
    if "" in P:
        testo, main = P[""][2], P[""][1]
        for x in ("31 December 2026", gbp(L["ihs_adulti"]), gbp(L["ihs_minori"]), gbp(L["ihs_18"]), gbp(L["ihs_24"]), gbp(L["ihs_36"]), "8 weeks", "before your Student visa expires"):
            if x not in testo:
                errori.append(f"Graduate: indice senza {x!r}")
        for u in [v["url"] for v in D["fonti"].values()]:
            if html.escape(u) not in main and u not in main:
                errori.append(f"Graduate: fonte non citata nell'indice: {u}")
        if html.escape(D["letture"]["regola_18"]["frammento"], quote=False) not in main:
            errori.append("Graduate: citazione di GR 8.1 mancante")
    if "cost" in P:
        tab = re.search(r'id="t-famiglie-grad".*?<tbody>(.*?)</tbody>', P["cost"][1], re.S).group(1)
        for (a, f), riga in zip(((1, 0), (2, 0), (2, 1), (2, 2)), re.findall(r"<tr>(.*?)</tr>", tab, re.S)):
            for mesi in (24, 18, 36):
                v = gbp(py_costo(mesi, a, f, k)["totale"])
                if v not in riga:
                    errori.append(f"Graduate: tabella famiglie, {a} adulti {f} figli {mesi} mesi: atteso {v}")
    for f, link in (("index.html", 'href="uk-graduate-visa/"'), ("how-it-works/index.html", 'href="../uk-graduate-visa/"'),
                    ("uk-skilled-worker-visa/index.html", 'href="../uk-graduate-visa/"')):
        if link not in (SITO / f).read_text(encoding="utf-8"):
            errori.append(f"Graduate: {f} non rimanda alla sezione")
    e_js, n_js = confronta_js_studio("uk-graduate-visa/index.html", {"finestra": {"prima": 90, "dopo": 60, "dso": 30, "inizio": 60, "nuova": 30},
                                                                     "stem": {"prima": 90, "dso": 60, "proroga": 180}, "graduate": k})
    errori += e_js
    riletti = []
    if online:
        sys.path.insert(0, str(SITO.parent / "raccolta"))
        import graduate as RG
        for fonte in ("guida", "appendice", "ihs"):
            r = RG.leggi_pagina(RG.PAGINE[fonte][0])
            tx = r[1] if len(r) == 3 else ""
            for key, v in D["letture"].items():
                if v["fonte"] == fonte:
                    ok = v["frammento"] in tx
                    riletti.append(f"GOV.UK {fonte} {key}: {'presente' if ok else 'ASSENTE'}")
                    if not ok:
                        errori.append(f"Graduate: frammento {key} non più nella pagina GOV.UK ({fonte})")
    return errori, len(P), n_js, riletti


# ---------------------------------------------------------------- 21. Mexico residency (31/10/2026)
import math as _math


def _r2(x):
    return _math.floor(x * 100 + 0.5) / 100


def py_mx(importo, val, cosa, tipo, k):
    """Stesso risultato di CALC_MX.mx (MX_JS), scritto qui senza le funzioni di genera.py."""
    if importo in ("", None):
        return None
    x = float(importo)
    if not x >= 0:
        return None
    i = 1 if cosa == "saldo" else 0
    t = k["tassi"]
    righe, nok, n = [], 0, 0
    for c in k["cons"]:
        s = c[tipo]
        if not s:
            righe.append({"id": c["id"], "assente": True})
            continue
        soglia = s[i]
        tuo = x if c["val"] == val else _r2(x / t[val] * t[c["val"]])
        ok = tuo >= soglia
        n += 1
        nok += ok
        righe.append({"id": c["id"], "soglia": soglia, "val": c["val"], "tuo": tuo, "stessa": c["val"] == val, "ok": ok, "appr": c["appr"]})
    su = k["uma"][tipo][i]
    tu = x if val == "MXN" else _r2(x / t[val] * t["MXN"])
    return {"righe": righe, "uma": {"soglia": su, "tuo": tu, "ok": (tu >= su) if i == 1 else (tu > su)}, "nok": nok, "n": n}   # saldo "equivalente a", reddito "mayores al"


def casi_mx(k, seme=31, n=400):
    rng = random.Random(seme)
    casi = [[None, "USD", "reddito", "tr"], ["", "USD", "saldo", "pr"], [0, "MXN", "reddito", "tr"]]
    for c in k["cons"]:   # esattamente sulla soglia, un centesimo sotto, nella valuta del consolato
        casi += [[c["tr"][0], c["val"], "reddito", "tr"], [round(c["tr"][0] - 0.01, 2), c["val"], "reddito", "tr"], [c["tr"][1], c["val"], "saldo", "tr"]]
        if c["pr"]:
            casi += [[c["pr"][0], c["val"], "reddito", "pr"], [c["pr"][1], c["val"], "saldo", "pr"]]
    casi += [[k["uma"]["tr"][0], "MXN", "reddito", "tr"], [k["uma"]["pr"][1], "MXN", "saldo", "pr"], [k["uma"]["tr"][1], "MXN", "saldo", "tr"]]
    for _ in range(n):
        val = rng.choice(["USD", "CAD", "GBP", "EUR", "MXN"])
        cosa, tipo = rng.choice(["reddito", "saldo"]), rng.choice(["tr", "pr"])
        base = {"USD": 1, "CAD": 1.4, "GBP": 0.75, "EUR": 0.86, "MXN": 18}[val] * (4500 if cosa == "reddito" else 75000) * (1.7 if tipo == "pr" else 1) * (4 if cosa == "saldo" and tipo == "pr" else 1)
        casi.append([round(rng.uniform(0.5, 1.5) * base, rng.choice([0, 2])), val, cosa, tipo])
    return casi


def controlla_mx(online=True):
    import hashlib
    errori = []
    D = json.loads((SITO.parent / "dati" / "mexico.json").read_text(encoding="utf-8"))
    cont = {k: D[k] for k in ("letture", "fonti", "consolati", "esclusi")}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != D["impronta"]:
        errori.append("Messico: impronta di dati/mexico.json diversa dal contenuto")
    L = {k: v["valore"] for k, v in D["letture"].items()}
    letto = G.data_lunga(D["letto_il"])
    cons = D["consolati"]
    uma = L["uma_diaria"]

    def mx(x):
        return "MXN " + (f"{x:,.0f}" if float(x).is_integer() else f"{x:,.2f}")

    def imp(x, v):
        return {"USD": "US$", "CAD": "C$", "GBP": "£", "EUR": "€", "MXN": "MXN "}[v] + (f"{x:,.0f}" if float(x).is_integer() else f"{x:,.2f}")
    # costi: Anexo 4 = LFD, importo da pagare = arrotondamento
    for n_ in "1234":
        if L["a4_rt"][n_][0] != L[f"rt_{n_}"] or L["a4_rt"][n_][1] != round(L[f"rt_{n_}"]):
            errori.append(f"Messico: costo della residenza temporanea di {n_} anni diverso tra Anexo 4 e LFD")
    if L["a4_rp"] != [L["rp"], round(L["rp"])] or L["a4_visa"][0] != L["visa"] or L["a4_cambio"][0] != L["cambio"]:
        errori.append("Messico: costi della residenza permanente, del cambio o del visto diversi tra Anexo 4 e LFD")
    giorni = {"tr": (L["rt_reddito_giorni"], L["rt_saldo_giorni"]), "pr": (L["rp_reddito_giorni"], L["rp_saldo_giorni"])}
    if giorni != {"tr": (680, 11460), "pr": (1140, 45850)} or L["familiare_giorni"] != 220:
        errori.append("Messico: giorni di UMA diversi da quelli scritti nei testi (680/11.460, 1.140/45.850, 220): rivedere i testi")
    pesos = {t: [round(g * uma, 2) for g in giorni[t]] for t in giorni}
    attese = ["", "income-requirements", "fees"] + [c["id"] for c in cons]
    P = _pagine_sezione("mexico-residency/", attese, errori, "Messico", affiliati=True)
    for s, (t, main, testo, lead, percorso) in P.items():
        prima = re.split(r"(?<=[a-z0-9)])\.\s+(?=[A-Z])", lead)[0]
        if letto not in prima:
            errori.append(f"Messico: data di lettura non nella prima frase in {percorso}")
        elif not re.search(r"Annex 4|guidelines|Diario Oficial|official", prima.split(letto)[0]):
            errori.append(f"Messico: prima frase senza la fonte prima della data in {percorso}")
        if re.search(r"(?i)you will get (the|a|your) visa|guarantee[sd]? (the|a|your) visa|will be approved", testo):
            errori.append(f"Messico: promessa sul visto in {percorso}")
        m = main.find('class="card aff-r"')
        if m >= 0:
            pezzo = main[m:main.find("</section>", m)]
            if 'rel="sponsored noopener"' not in pezzo or "safetywing.com" not in pezzo or "Insurance is not a requirement" not in html.unescape(pezzo):
                errori.append(f"Messico: riquadro SafetyWing senza sponsored noopener o senza la frase sul requisito in {percorso}")
            if m < main.find("Not legal or immigration advice."):
                errori.append(f"Messico: riquadro SafetyWing prima delle informazioni ufficiali in {percorso}")
        for a in re.findall(r'<a [^>]*rel="[^"]*sponsored[^"]*"[^>]*>', main):
            if "safetywing.com" not in a:
                errori.append(f"Messico: link sponsorizzato non previsto in {percorso}")
        # calcolatore: costanti = dati
        km = re.search(r"data-mx data-rel=\"[^\"]*\" data-k='(.*?)'", main)
        if s in ("", "income-requirements") or s in [c["id"] for c in cons]:
            if not km:
                errori.append(f"Messico: calcolatore assente in {percorso}")
            else:
                k = json.loads(km.group(1))
                attesi = {"cons": [{"id": c["id"], "sede": c["sede"], "val": c["valuta"], "tr": [c["tr"]["reddito"]["importo"], c["tr"]["saldo"]["importo"]],
                                    "pr": ([c["pr"]["reddito"]["importo"], c["pr"]["saldo"]["importo"]] if "pr" in c else None), "appr": bool(c.get("approssimato"))}
                                   for c in sorted(cons, key=lambda c: c["sede"])],
                          "uma": pesos, "tassi": {v: (1 if v == "EUR" else G.CAMBI["tassi"][v]) for v in ("EUR", "USD", "GBP", "CAD", "MXN")}, "data_cambi": G.data_lunga(G.CAMBI["data"])}
                if k != attesi:
                    errori.append(f"Messico: costanti del calcolatore diverse dai dati in {percorso}")
            if "window.CALC_MX=C" not in t:
                errori.append(f"Messico: script del calcolatore mancante in {percorso}")
    if "" in P:
        t, main, testo, lead, _ = P[""]
        for x in (mx(L["a4_rt"]["1"][1]), mx(L["a4_rp"][1]), mx(pesos["tr"][0]), mx(pesos["tr"][1]), mx(pesos["pr"][0]), mx(pesos["pr"][1]), f"MXN {uma}"):
            if x not in testo:
                errori.append(f"Messico: indice senza {x!r}")
        tab = re.search(r'id="t-cons-mx".*?<tbody>(.*?)</tbody>', main, re.S)
        righe = re.findall(r"<tr>(.*?)</tr>", tab.group(1), re.S) if tab else []
        if len(righe) != len(cons):
            errori.append(f"Messico: righe della tabella dei consolati {len(righe)} invece di {len(cons)}")
        for c in cons:
            riga = next((r for r in righe if f'href="{c["id"]}/"' in r), "")
            for tipo in ("tr", "pr"):
                for cosa in ("reddito", "saldo"):
                    if tipo in c and imp(c[tipo][cosa]["importo"], c["valuta"]) not in riga:
                        errori.append(f"Messico: tabella, {c['id']} {tipo} {cosa}: manca {imp(c[tipo][cosa]['importo'], c['valuta'])}")
            if html.escape(c["pagine"][0]["url"]) not in riga:
                errori.append(f"Messico: tabella senza il link ufficiale di {c['id']}")
        for e in D["esclusi"]:
            if html.escape(e["url"]) not in main:
                errori.append(f"Messico: consolato escluso non elencato: {e['sede']}")
        for u in [f["url"] for f in D["fonti"].values()]:
            if html.escape(u) not in main:
                errori.append(f"Messico: fonte non citata nell'indice: {u}")
    if "fees" in P:
        testo = P["fees"][2]
        for x in [mx(L["a4_rt"][n_][1]) for n_ in "1234"] + [mx(L["a4_rp"][1]), mx(L["a4_cambio"][1]), mx(L["a4_repos"][1]), mx(L["a4_visa"][1]), "50%"]:
            if x not in testo:
                errori.append(f"Messico: pagina dei costi senza {x!r}")
        tab = re.search(r'id="t-esempi-mx".*?<tbody>(.*?)</tbody>', P["fees"][1], re.S).group(1)
        for (n_, c), riga in zip(((1, L["a4_rt"]["1"][1]), (2, L["a4_rt"]["1"][1]), (1, L["a4_rp"][1]), (2, L["a4_rp"][1])), re.findall(r"<tr>(.*?)</tr>", tab, re.S)):
            if mx(n_ * c) not in riga or imp(n_ * 56, "USD") not in riga:
                errori.append(f"Messico: esempio dei costi sbagliato: {n_} × {c}")
    if "income-requirements" in P:
        testo = P["income-requirements"][2]
        for x in (mx(pesos["tr"][0]), mx(pesos["tr"][1]), mx(pesos["pr"][0]), mx(pesos["pr"][1]), mx(round(220 * uma, 2))):
            if x not in testo:
                errori.append(f"Messico: pagina del reddito senza {x!r}")
    for c in cons:
        if c["id"] not in P:
            continue
        t, main, testo, lead, percorso = P[c["id"]]
        for x in (imp(c["tr"]["reddito"]["importo"], c["valuta"]), imp(c["tr"]["saldo"]["importo"], c["valuta"])):
            if x not in lead:
                errori.append(f"Messico: prima frase di {c['id']} senza {x}")
        d = c["data_pagina"]
        if d and G.data_lunga(d) not in lead:
            errori.append(f"Messico: data della pagina del consolato non nella prima frase di {c['id']}")
        if d and d < "2026-01-01":
            errori.append(f"Messico: pagina di {c['id']} prima del 2026")
        voci = [c[tp][cs] for tp in ("tr", "pr") if tp in c for cs in ("reddito", "saldo")] + ([c["tassa"]] if "tassa" in c else []) + c.get("altre", [])
        for v in voci:
            if html.escape(v["frammento"], quote=False) not in main and html.escape(v["frammento"]) not in main:
                errori.append(f"Messico: frammento ufficiale non citato nella pagina di {c['id']}: {v['frammento'][:60]}")
        for p in c["pagine"]:
            if html.escape(p["url"]) not in main:
                errori.append(f"Messico: link ufficiale mancante nella pagina di {c['id']}")
    for f, link in (("index.html", 'href="mexico-residency/"'), ("how-it-works/index.html", 'href="../mexico-residency/"'),
                    ("digital-nomad-visa-income-requirements/index.html", 'href="../mexico-residency/"'), ("about/index.html", 'href="../mexico-residency/"')):
        if link not in (SITO / f).read_text(encoding="utf-8"):
            errori.append(f"Messico: {f} non rimanda alla sezione")
    # motore JS del calcolatore (preso dalla pagina pubblicata) = calcolo Python
    n_js = 0
    if "" in P:
        t = P[""][0]
        js = next(x for x in re.findall(r"<script>(.*?)</script>", t, re.S) if "window.CALC_MX=C" in x)
        k = json.loads(re.search(r"data-mx data-rel=\"[^\"]*\" data-k='(.*?)'", P[""][1]).group(1))
        casi = casi_mx(k)
        prog = ("var window={};var document={querySelectorAll:function(){return [];}};\n" + js + "\nvar K=" + json.dumps(k) + ";var CASI=" + json.dumps(casi)
                + ";console.log(JSON.stringify(CASI.map(function(c){return window.CALC_MX.mx(c[0],c[1],c[2],c[3],K);})));")
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
            fh.write(prog)
        r = subprocess.run(["node", fh.name], capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            errori.append(f"Messico: JS del calcolatore non eseguibile: {r.stderr[-300:]}")
        else:
            diff = [(c_, j) for c_, j in zip(casi, json.loads(r.stdout)) if py_mx(*c_, k) != j]
            n_js = len(casi)
            errori += [f"Messico: calcolatore {c_}: JS {str(j)[:120]} ≠ Python {str(py_mx(*c_, k))[:120]}" for c_, j in diff[:5]]
    riletti = []
    if online:
        sys.path.insert(0, str(SITO.parent / "raccolta"))
        import mexico as RM
        testi = {}
        for k_, f in RM.FONTI.items():
            meta, tx = RM.leggi(f["url"], oggi=_date.today().isoformat())
            testi[k_] = tx if meta else ""
        rng = random.Random(20261031)
        for key in rng.sample(sorted(D["letture"]), 10):
            v = D["letture"][key]
            ok = v["frammento"] in testi.get(v["fonte"], "")
            riletti.append(f"{v['fonte']} {key}: {'presente' if ok else 'ASSENTE'}")
            if not ok:
                errori.append(f"Messico: frammento {key} non più in {v['fonte']}")
    return errori, len(P), n_js, riletti


# ---------------------------------------------------------------- 22. Study in Italy (31/10/2026)
def py_it(i, k):
    """Stesso risultato di CALC_IT.isee (ISEE_JS), scritto qui senza le funzioni di genera.py."""
    try:
        n = int(float(i["n"])) if i["n"] not in ("", None) else 0
    except ValueError:
        return None
    if not (1 <= n <= 20) or i["reddito"] in ("", None):
        return None

    def num(v):
        if v in ("", None):
            return 0.0
        x = float(v)
        return x if x >= 0 else None
    red, ris, mq, mut = num(i["reddito"]), num(i["risparmi"]), num(i["mq"]), num(i["mutuo"])
    if None in (red, ris, mq, mut):
        return None
    t = 1 if i["val"] == "EUR" else k["cambi"].get(i["anno"], {}).get(i["val"])
    if not t:
        return None
    isr, mob = _r2(red / t), _r2(ris / t)
    imm = _r2(max(0, mq * k["mq"] - _r2(mut / t)))
    isp = _r2(mob + imm)
    ise = _r2(isr + k["quota"] * isp)
    s = k["scala"]
    sc = s[str(n)] if n <= 5 else _r2(s["5"] + (n - 5) * s["oltre"])
    isee, ispe = _r2(ise / sc), _r2(isp / sc)
    righe = [{"id": e["id"], "ok_isee": isee <= e["isee"], "ok_ispe": ispe <= e["ispe"], "ok": isee <= e["isee"] and ispe <= e["ispe"],
              "top": isee <= e["isee"] and ispe <= e["ispe"] and isee <= e["fs_isee"]} for e in k["enti"]]
    return {"t": t, "isr": isr, "mob": mob, "imm": imm, "isp": isp, "ise": ise, "scala": sc, "isee": isee, "ispe": ispe, "righe": righe,
            "povero": i["paese"] in k["poveri"], "unimi_auto": i["paese"] not in ("", "other") and i["paese"] not in k["unimi"]}


def casi_it(k, seme=22, n=400):
    rng = random.Random(seme)
    base = {"n": 4, "val": "EUR", "anno": "2025", "reddito": 10000, "risparmi": 0, "mq": 0, "mutuo": 0, "paese": ""}
    casi = [dict(base, reddito=""), dict(base, n=0), dict(base, n=21), dict(base, reddito=-5), dict(base, val="XXX"), dict(base, n="2.7"),
            dict(base, paese="Bangladesh"), dict(base, paese="Pakistan"), dict(base, paese="United States"), dict(base, paese="other")]
    for e in k["enti"]:   # esattamente sul limite e un centesimo sopra (ISEE e ISPE), in euro, una persona
        casi += [dict(base, n=1, reddito=e["isee"]), dict(base, n=1, reddito=round(e["isee"] + 0.01, 2)),
                 dict(base, n=1, reddito=0, risparmi=e["ispe"]), dict(base, n=1, reddito=0, risparmi=round(e["ispe"] + 0.01, 2)),
                 dict(base, n=1, reddito=e["fs_isee"]), dict(base, n=1, reddito=round(e["fs_isee"] + 0.01, 2))]
    valute = ["EUR"] + list(k["cambi"]["2025"])
    paesi = ["", "other", "India", "Pakistan", "Nigeria", "Bangladesh", "Nepal", "Iran", "United States", "Japan", "Egypt"]
    for _ in range(n):
        v = rng.choice(valute)
        anno = rng.choice(["2024", "2025"])
        t = 1 if v == "EUR" else k["cambi"][anno][v]
        casi.append({"n": rng.randint(1, 9), "val": v, "anno": anno, "reddito": round(rng.uniform(0, 45000) * t, rng.choice([0, 2])),
                     "risparmi": round(rng.choice([0, rng.uniform(0, 90000)]) * t, 0), "mq": rng.choice([0, 0, 60, 95.5, 120, 240, 400]),
                     "mutuo": round(rng.choice([0, 0, rng.uniform(0, 80000)]) * t, 0), "paese": rng.choice(paesi)})
    return casi


def controlla_it(online=True):
    import hashlib
    errori = []
    D = json.loads((SITO.parent / "dati" / "studio_italia.json").read_text(encoding="utf-8"))
    cont = {k: D[k] for k in ("letture", "fonti", "enti", "non_letti", "poveri", "unimi_allegato1", "cambi_bdi")}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != D["impronta"]:
        errori.append("Italia: impronta di dati/studio_italia.json diversa dal contenuto")
    L = {k: v["valore"] for k, v in D["letture"].items()}
    letto = G.data_lunga(D["letto_il"])
    enti = D["enti"]

    def e_(x):
        x = float(x)
        return "€" + (f"{x:,.0f}" if x.is_integer() else f"{x:,.2f}")
    if (L["mezzi"], L["dsu_fs"], L["isee_max"], L["ispe_max"], L["ssn_minimo"]) != (10179.85, 7171.11, 28339.88, 61608.48, 700):
        errori.append("Italia: cifre nazionali diverse da quelle scritte nelle FAQ (10.179,85 / 7.171,11 / 28.339,88 / 61.608,48 / 700): rivedere i testi")
    for E in enti:
        if E["isee"]["valore"] > L["isee_max"] or E["ispe"]["valore"] > L["ispe_max"]:
            errori.append(f"Italia: {E['id']} con limiti sopra il massimo nazionale")
    tema = ["student-visa-funds", "isee-parificato", "dsu-scholarship-deadlines", "particularly-poor-countries", "health-insurance"]
    attese = [""] + tema + [E["id"] for E in enti]
    P = _pagine_sezione("study-in-italy/", attese, errori, "Italia", affiliati=True)
    tutto = ""
    for s_, (t, main, testo, lead, percorso) in P.items():
        tutto += main
        prima = re.split(r"(?<=[a-z0-9)%])\.\s+(?=[A-Z])", lead)[0]
        if letto not in prima:
            errori.append(f"Italia: data di lettura non nella prima frase in {percorso}")
        elif not re.search(r"procedures|call|decree|Normattiva|Ministry", prima.split(letto)[0]):
            errori.append(f"Italia: prima frase senza la fonte prima della data in {percorso}")
        if re.search(r"(?i)you will get (the|a|your) (visa|scholarship)|guarantee[sd]? (the|a|your) (visa|scholarship)|will be approved", testo):
            errori.append(f"Italia: promessa in {percorso}")
        m = main.find('class="card aff-r"')
        if m >= 0:
            pezzo = html.unescape(main[m:main.find("</section>", m)])
            if s_ != "health-insurance":
                errori.append(f"Italia: riquadro affiliato fuori dalla pagina dell'assicurazione ({percorso})")
            if 'rel="sponsored noopener"' not in pezzo or "safetywing.com" not in pezzo or "SSN registration is the official route" not in pezzo:
                errori.append(f"Italia: riquadro SafetyWing senza sponsored noopener o senza la frase sul SSN in {percorso}")
            if m < main.find("Not legal or immigration advice.") or m < main.find("The three options in the procedures"):
                errori.append(f"Italia: riquadro SafetyWing prima delle informazioni ufficiali in {percorso}")
        for a in re.findall(r'<a [^>]*rel="[^"]*sponsored[^"]*"[^>]*>', main):
            if "safetywing.com" not in a or s_ != "health-insurance":
                errori.append(f"Italia: link sponsorizzato non previsto in {percorso}")
        km = re.search(r"data-isee data-rel=\"[^\"]*\" data-primo=\"[^\"]*\" data-v='[^']*' data-k='(.*?)'", main)
        if s_ in ("", "isee-parificato") or s_ in [E["id"] for E in enti]:
            if not km:
                errori.append(f"Italia: calcolatore assente in {percorso}")
            else:
                k = json.loads(html.unescape(km.group(1)))
                attesi = {"enti": [{"id": E["id"], "nome": E["nome"], "isee": E["isee"]["valore"], "ispe": E["ispe"]["valore"], "fs": E["fs"]["valore"],
                                    "fs_isee": E["fs"]["fino_isee"]} for E in enti],
                          "scala": L["scala"], "mq": 500, "quota": 0.2, "cambi": D["cambi_bdi"]["anni"]}
                if {x: k[x] for x in attesi} != attesi:
                    errori.append(f"Italia: costanti del calcolatore diverse dai dati in {percorso}")
                if sorted(k["poveri"]) != sorted(G.NOMI_POVERI_IT.get(p, p) for p in D["poveri"]):
                    errori.append(f"Italia: elenco dei Paesi poveri del calcolatore diverso dal decreto in {percorso}")
                if any(G.PAESI_ALL1_IT[p] not in D["unimi_allegato1"] for p in k["unimi"]):
                    errori.append(f"Italia: Paese del calcolatore non nell'allegato 1 UNIMI in {percorso}")
            if "window.CALC_IT=C" not in t:
                errori.append(f"Italia: script del calcolatore mancante in {percorso}")
    base_ps = L["ps_marca"] + L["ps_poste"] + L["ps_documento"]
    if "" in P:
        t, main, testo, lead, _ = P[""]
        for x in (e_(L["mezzi"]), e_(L["dsu_fs"]), e_(L["isee_max"]), e_(L["ispe_max"]), G.data_lunga(L["visto_scadenza"]), e_(round(base_ps + L["ps_contributo_1"], 2))):
            if x not in testo:
                errori.append(f"Italia: indice senza {x!r}")
        tab = re.search(r'id="t-enti-it".*?<tbody>(.*?)</tbody>', main, re.S)
        righe = re.findall(r"<tr>(.*?)</tr>", tab.group(1), re.S) if tab else []
        if len(righe) != len(enti):
            errori.append(f"Italia: righe della tabella degli enti {len(righe)} invece di {len(enti)}")
        for E in enti:
            riga = html.unescape(next((r for r in righe if f'href="{E["id"]}/"' in r), ""))
            for x in (e_(E["isee"]["valore"]), e_(E["ispe"]["valore"]), e_(E["fs"]["valore"]), G.data_lunga(E["scadenza"]["valore"])):
                if x not in riga:
                    errori.append(f"Italia: tabella, {E['id']} senza {x}")
            if E["fonti"][0] and D["fonti"][E["fonti"][0]]["url"] not in riga:
                errori.append(f"Italia: tabella senza il bando di {E['id']}")
        for x in D["non_letti"]:
            if html.escape(x["url"]) not in main:
                errori.append(f"Italia: ente non letto non elencato: {x['nome']}")
    if "student-visa-funds" in P:
        t, main, testo, lead, _ = P["student-visa-funds"]
        for x in (e_(round(base_ps + L["ps_contributo_1"], 2)), e_(round(base_ps + L["ps_contributo_2"], 2)), e_(L["ps_documento"]), e_(L["ps_contributo_2"])):
            if x not in testo:
                errori.append(f"Italia: pagina dei mezzi senza {x!r}")
        tab = re.search(r'id="t-mezzi-it".*?<tbody>(.*?)</tbody>', main, re.S)
        for r in re.findall(r"<tr>(.*?)</tr>", tab.group(1) if tab else "", re.S):
            v = re.search(r'<th[^>]*>([A-Z]{3}) ', r).group(1)
            tasso = G.CAMBI["tassi"][v] if v in G.CAMBI["tassi"] else D["cambi_bdi"]["anni"]["2025"][v]
            if f"{L['mezzi'] * tasso:,.0f}" not in r:
                errori.append(f"Italia: conversione dei mezzi in {v} sbagliata")
    if "isee-parificato" in P:
        testo = P["isee-parificato"][2]
        t_ = D["cambi_bdi"]["anni"]["2025"]["PKR"]
        isr, mob = _r2(1500000 / t_), _r2(600000 / t_)
        isp = _r2(mob + 120 * 500)
        isee = _r2(_r2(isr + 0.2 * isp) / L["scala"]["4"])
        for x in (e_(isee), e_(_r2(isp / L["scala"]["4"])), "1.57", "2.46", "0.35"):
            if x not in testo:
                errori.append(f"Italia: pagina ISEE senza {x!r} (esempio o scala)")
    if "particularly-poor-countries" in P:
        testo = P["particularly-poor-countries"][2]
        if len(D["poveri"]) != 46:
            errori.append(f"Italia: {len(D['poveri'])} Paesi poveri (il decreto ne elenca 46): rivedere i testi")
        for p in D["poveri"]:
            if html.unescape(G.NOMI_POVERI_IT.get(p, p)) not in testo:
                errori.append(f"Italia: Paese povero non elencato: {p}")
        for p in ("India", "Pakistan", "Nigeria"):
            if p in D["poveri"]:
                errori.append(f"Italia: {p} è ora tra i Paesi poveri: rivedere le FAQ")
    if "health-insurance" in P and e_(L["ssn_minimo"]) not in P["health-insurance"][2]:
        errori.append("Italia: pagina dell'assicurazione senza il minimo SSN")
    if "dsu-scholarship-deadlines" in P:
        testo = P["dsu-scholarship-deadlines"][2]
        for E in enti:
            if G.data_lunga(E["scadenza"]["valore"]) not in testo:
                errori.append(f"Italia: pagina delle scadenze senza la scadenza di {E['id']}")
    for E in enti:
        if E["id"] not in P:
            continue
        t, main, testo, lead, percorso = P[E["id"]]
        for x in (e_(E["isee"]["valore"]), e_(E["ispe"]["valore"]), e_(E["fs"]["valore"]), G.data_lunga(E["scadenza"]["valore"])):
            if x not in lead:
                errori.append(f"Italia: prima frase di {E['id']} senza {x}")
        d_ = D["fonti"][E["fonti"][0]].get("data")
        if d_ and G.data_lunga(d_) not in lead:
            errori.append(f"Italia: data del bando non nella prima frase di {E['id']}")
        for c in ("isee", "ispe", "fs", "fs_cifra", "fs_fascia", "fs_base", "servizi", "scadenza", "estero", "estero_cambio", "estero_regola", "estero_scad_fr", "isee_conferma", "poveri"):
            v = E.get(c)
            if v and html.escape(v["frammento"], quote=False) not in main and html.escape(v["frammento"]) not in main:
                errori.append(f"Italia: frammento del bando non citato nella pagina di {E['id']} ({c})")
        for k_ in E["fonti"]:
            if html.escape(D["fonti"][k_]["url"]) not in main:
                errori.append(f"Italia: link al bando mancante nella pagina di {E['id']}")
    for k_, f in D["fonti"].items():
        if html.escape(f["url"]) not in tutto:
            errori.append(f"Italia: fonte non citata in nessuna pagina della sezione: {k_}")
    for f, link in (("index.html", 'href="study-in-italy/"'), ("how-it-works/index.html", 'href="../study-in-italy/"'),
                    ("italy-digital-nomad-visa/index.html", 'href="../study-in-italy/"'), ("country/italy/index.html", 'href="../../study-in-italy/"'),
                    ("about/index.html", 'href="../study-in-italy/"')):
        if link not in (SITO / f).read_text(encoding="utf-8"):
            errori.append(f"Italia: {f} non rimanda alla sezione")
    # motore JS del calcolatore (preso dalla pagina pubblicata) = calcolo Python
    n_js = 0
    if "" in P:
        t, main = P[""][0], P[""][1]
        js = next(x for x in re.findall(r"<script>(.*?)</script>", t, re.S) if "window.CALC_IT=C" in x)
        k = json.loads(html.unescape(re.search(r"data-isee data-rel=\"[^\"]*\" data-primo=\"[^\"]*\" data-v='[^']*' data-k='(.*?)'", main).group(1)))
        casi = casi_it(k)
        casi_js = [{a: ("" if b is None else (str(b) if a in ("n", "reddito", "risparmi", "mq", "mutuo") else b)) for a, b in c.items()} for c in casi]
        prog = ("var window={};var document={querySelectorAll:function(){return [];}};\n" + js + "\nvar K=" + json.dumps(k) + ";var CASI=" + json.dumps(casi_js)
                + ";console.log(JSON.stringify(CASI.map(function(c){return window.CALC_IT.isee(c,K);})));")
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
            fh.write(prog)
        r = subprocess.run(["node", fh.name], capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            errori.append(f"Italia: JS del calcolatore non eseguibile: {r.stderr[-300:]}")
        else:
            diff = [(c_, j) for c_, j in zip(casi_js, json.loads(r.stdout)) if py_it(c_, k) != j]
            n_js = len(casi)
            errori += [f"Italia: calcolatore {c_}: JS {str(j)[:160]} ≠ Python {str(py_it(c_, k))[:160]}" for c_, j in diff[:5]]
    riletti = []
    if online:
        sys.path.insert(0, str(SITO.parent / "raccolta"))
        import studio_italia as RI
        voci = [(k_, v["fonte"], v["frammento"]) for k_, v in D["letture"].items()]
        voci += [(f"{E['id']}.{c}", E[c]["fonte"], E[c]["frammento"]) for E in enti for c in ("isee", "fs", "scadenza", "estero") if E.get(c)]
        rng = random.Random(20261031)
        scelte = rng.sample(voci, 12)
        testi = {}
        for nome, fonte, fr in scelte:
            if fonte not in testi:
                _m, testi[fonte] = RI.leggi(RI.FONTI[fonte])
            ok = fr in testi[fonte]
            riletti.append(f"{fonte} {nome}: {'presente' if ok else 'ASSENTE'}")
            if not ok:
                errori.append(f"Italia: frammento {nome} non più in {fonte}")
    return errori, len(P), n_js, riletti


def controlla_f7(online=True):
    import hashlib
    errori = []
    D = json.loads((SITO.parent / "dati" / "flat7.json").read_text(encoding="utf-8"))
    cont = {k: D[k] for k in ("letture", "fonti", "sisma2016", "sisma2009", "comuni", "anni_popolazione", "pagina_istat")}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != D["impronta"]:
        errori.append("7%: impronta di dati/flat7.json diversa dal contenuto")
    L = {k: v["valore"] for k, v in D["letture"].items()}
    soglia, regioni = L["soglia"], L["regioni"]
    if (soglia, L["art247"], L["nove_anni"], L["cinque_anni"], L["circ_dieci"]) != (30000, 30000, 9, 5, 10):
        errori.append("7%: regole diverse da quelle scritte nei testi (30.000, 9 + 1 anni, 5 anni): rivedere le pagine")
    letto = G.data_lunga(D["letto_il"])
    # calcolo indipendente delle aree: 8 regioni, allegati 2016-2017 (fuori dalle 8 regioni), Valfornace a parte
    sis = {}
    for x in D["sisma2016"]:
        sis.setdefault(x["codice"], []).append(x)
    def area(c):
        if c[4] in regioni:
            return 1
        if c[0] in sis:
            return 3 if all(x["nota"] for x in sis[c[0]]) and c[1] == "Valfornace" else 2
        return 0
    comuni = D["comuni"]
    # pagine
    sez = "italy-7-percent-flat-tax/"
    cart = SITO / sez.rstrip("/")
    trovate = {f.parent.relative_to(cart).as_posix().replace(".", "") for f in cart.rglob("index.html")}
    if trovate != {"", "regions"}:
        errori.append(f"7%: pagine diverse da quelle attese: {sorted(trovate)}")
    sitemap = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    P = {}
    for s_ in ("", "regions"):
        f = cart / s_ / "index.html" if s_ else cart / "index.html"
        if not f.exists():
            continue
        percorso = sez + (s_ + "/" if s_ else "")
        t = f.read_text(encoding="utf-8")
        main = t.split('<main id="main">', 1)[1].split("</main>", 1)[0]
        testo = html.unescape(re.sub(r"<[^>]+>", " ", main))
        testo = re.sub(r"\s+", " ", testo)
        P[s_] = (t, main, testo)
        if f"<loc>{G.URL_SITO}/{percorso}</loc>" not in sitemap:
            errori.append(f"7%: {percorso} non in sitemap")
        titolo = html.unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(titolo) > 70:
            errori.append(f"7%: titolo oltre 70 caratteri in {percorso} ({len(titolo)})")
        for x in ("FAQPage", "BreadcrumbList", 'rel="canonical"', "Not tax or legal advice.", "Check with an Italian tax adviser (commercialista) or the Agenzia delle Entrate",
                  "the Agenzia delle Entrate decides", "window.F7=C"):
            if x not in t:
                errori.append(f"7%: manca {x!r} in {percorso}")
        lead = html.unescape(re.sub(r"<[^>]+>", "", re.search(r'<p class="lead">(.*?)</p>', main, re.S).group(1)))
        prima = re.split(r"(?<=[a-z0-9)%])\.\s+(?=[A-Z])", lead)[0]
        if letto not in prima or "Normattiva" not in prima.split(letto)[0]:
            errori.append(f"7%: prima frase senza fonte e data di lettura in {percorso}")
        if re.search(r'rel="[^"]*sponsored', main):
            errori.append(f"7%: link sponsorizzato in {percorso}")
        if re.search(r"(?i)\b(you will qualify|guarantee[sd]?|qualifying towns?|recommended towns?|best towns?|towns? we recommend|eligible towns? list)\b", testo):
            errori.append(f"7%: promessa o elenco di Comuni consigliati in {percorso}")
        if re.search(r"(?i)\b\w+ (qualifies|is eligible) for the 7", testo):
            errori.append(f"7%: un Comune presentato come ammesso in {percorso}")
        for x in ("30,000", "7%", "1 January 2025", "1 January 2026"):
            if x not in testo:
                errori.append(f"7%: manca {x!r} in {percorso}")
        for k_ in ("art24ter", "istat2025", "istat2026"):
            if html.escape(D["fonti"][k_]["url"]) not in main:
                errori.append(f"7%: fonte {k_} non citata in {percorso}")
    if "" in P:
        t, main, testo = P[""]
        for x in ("20,000", "7 April 2026", "five tax years", "Ten tax years in all", "article 247", "1 January 2027", "Legislative Decree 117",
                  "Law 34 of 11 March 2026", "1 January of the year before", "Circular 21/E", "summary page talks of \"nine tax periods\"",
                  "between 1 January and 6 April 2026"):
            if x not in testo:
                errori.append(f"7%: indice senza {x!r}")
        tutto = main + P.get("regions", ("", "", ""))[1]
        for k_, f in D["fonti"].items():
            if html.escape(f["url"]) not in tutto:
                errori.append(f"7%: fonte non citata nella sezione: {k_}")
        # tabella delle regioni
        tab = re.search(r'id="t-regioni-f7".*?<tbody>(.*?)</tbody>', main, re.S)
        righe = re.findall(r"<tr>(.*?)</tr>", tab.group(1), re.S) if tab else []
        attese = {}
        for c in comuni:
            a = area(c)
            if a:
                k = c[4]
                v = attese.setdefault(k, [0, 0, 0])
                v[0] += 1
                v[1] += c[5] <= soglia
                v[2] += c[6] <= soglia
        if len(righe) != len(attese) + 1:
            errori.append(f"7%: righe della tabella delle regioni {len(righe)} invece di {len(attese) + 1}")
        nomi = {"Sicilia": "Sicily", "Sardegna": "Sardinia", "Puglia": "Puglia (Apulia)"}
        for r, v in attese.items():
            riga = next((x for x in righe if f">{nomi.get(r, r)}<" in x), "")
            celle = [int(n.replace(",", "")) for n in re.findall(r'<td[^>]*class="n"[^>]*>(?:<b>)?([\d,]+)', riga)]
            if celle != [v[0], v[1], v[2], v[0] - v[1]]:
                errori.append(f"7%: riga {r} della tabella {celle} invece di {[v[0], v[1], v[2], v[0] - v[1]]}")
        tot = [sum(v[i] for v in attese.values()) for i in range(3)]
        if f"{tot[1]:,}" not in testo or tot[1] != 2535:
            errori.append(f"7%: totale entro la soglia {tot[1]} (1/1/2025) non nella pagina o diverso da 2.535 (verifica del 30/10/2026)")
        # Comuni vicini alla soglia
        tab = re.search(r'id="t-vicini-f7".*?<tbody>(.*?)</tbody>', main, re.S)
        righe = re.findall(r"<tr>(.*?)</tr>", tab.group(1), re.S) if tab else []
        vicini = [c for c in comuni if area(c) and (abs(c[5] - soglia) <= 1000 or abs(c[6] - soglia) <= 1000)]
        if len(righe) != len(vicini):
            errori.append(f"7%: Comuni vicini alla soglia {len(righe)} invece di {len(vicini)}")
        for c in vicini:
            riga = next((x for x in righe if f">{html.escape(c[1])}" in x and f"({c[3]})" in x), "")
            s1 = "Under" if c[5] <= soglia else "Over"
            s2 = "Under" if c[6] <= soglia else "Over"
            if not re.search(rf"{c[5]:,} <span[^>]*>{s1}</span>.*{c[6]:,} <span[^>]*>{s2}</span>", riga):
                errori.append(f"7%: riga dei Comuni vicini sbagliata per {c[1]}")
        for nome, a25, ok26 in (("Grottaglie", "Over", "Under"), ("Oristano", "Over", "Under"), ("Ostuni", "Under", "Under")):
            riga = next((x for x in righe if f">{nome} (" in x), "")
            if re.findall(r">(Under|Over)<", riga) != [a25, ok26]:
                errori.append(f"7%: {nome} non come nella verifica del 30/10/2026 ({a25} per il 2026, {ok26} per il 2027)")
    if "regions" in P:
        t, main, testo = P["regions"]
        for r in ("Lazio", "Marche", "Umbria"):
            cc = [c for c in comuni if c[4] == r and area(c) in (2, 3)]
            tab = re.search(rf'id="t-sisma-{r.lower()}".*?<tbody>(.*?)</tbody>', main, re.S)
            righe = re.findall(r"<tr>(.*?)</tr>", tab.group(1), re.S) if tab else []
            if len(righe) != len(cc):
                errori.append(f"7%: {r}, {len(righe)} Comuni del sisma invece di {len(cc)}")
            for c in cc:
                riga = next((x for x in righe if f">{html.escape(c[1])} ({c[3]})" in x), "")
                if f"{c[5]:,}" not in riga or f"{c[6]:,}" not in riga:
                    errori.append(f"7%: {r}, cifre ISTAT mancanti per {c[1]}")
        for r in regioni:
            n = sum(1 for c in comuni if c[4] == r and c[5] > soglia)
            if not re.search(rf"{re.escape({'Sicilia': 'Sicily', 'Sardegna': 'Sardinia', 'Puglia': 'Puglia (Apulia)'}.get(r, r))}: {n} towns? over 30,000", testo):
                errori.append(f"7%: {r}, numero di Comuni sopra la soglia diverso da {n}")
        for x in ("Valfornace", "Fabriano", "L'Aquila", "Teramo"):
            if x not in testo:
                errori.append(f"7%: pagina delle regioni senza {x}")
    # towns.json = dati
    tj = cart / "towns.json"
    if not tj.exists():
        errori.append("7%: towns.json mancante")
        return errori, len(P), 0, []
    T = json.loads(tj.read_text(encoding="utf-8"))
    if T["soglia"] != soglia or [a[1] for a in T["anni"]] != ["2025", "2026"] or len(T["c"]) != len(comuni):
        errori.append("7%: towns.json non coerente con i dati (soglia, anni o numero di Comuni)")
    else:
        for r, c in zip(T["c"], comuni):
            if r[:3] != [c[1], c[2], c[3]] or r[4] != area(c) or r[5:] != c[5:7] or T["reg"][r[3]] != {"Sicilia": "Sicily", "Sardegna": "Sardinia", "Puglia": "Puglia (Apulia)", "Toscana": "Tuscany", "Lombardia": "Lombardy", "Piemonte": "Piedmont", "Valle d'Aosta/Vallée d'Aoste": "Aosta Valley", "Trentino-Alto Adige/Südtirol": "Trentino-South Tyrol"}.get(c[4], c[4]):
                errori.append(f"7%: towns.json diverso dai dati per {c[1]}")
                break
    # motore JS dello strumento = Python, su tutti i Comuni e i due anni; ricerca per nome esatto
    n_js = 0
    if "" in P:
        js = next(x for x in re.findall(r"<script>(.*?)</script>", P[""][0], re.S) if "window.F7=C" in x)
        prog = ("var window={};var document={querySelectorAll:function(){return [];}};\n" + js + "\nvar D=" + json.dumps(T, ensure_ascii=False) +
                ";var st=[];D.c.forEach(function(r){st.push([window.F7.stato(r,0,D),window.F7.stato(r,1,D)]);});"
                "var ce=D.c.map(function(r,i){var x=window.F7.cerca(r[0],D,50);return x.indexOf(i)>=0&&x.length&&(D._k[x[0]][0]===D._k[i][0]||D._k[x[0]][1]===D._k[i][0]);});"
                "var pr=['ostuni','GROTTAGLIE','cefalu','lec','sant','xx'].map(function(q){return window.F7.cerca(q,D,8).map(function(j){return D.c[j][0];});});"
                "var bo=[window.F7.stato(['x','','XX',0,1,D.soglia,D.soglia+1],0,D),window.F7.stato(['x','','XX',0,1,D.soglia,D.soglia+1],1,D),window.F7.stato(['x','','XX',0,0,1,1],0,D)];"
                "console.log(JSON.stringify({st:st,ce:ce,pr:pr,bo:bo}));")
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
            fh.write(prog)
        r = subprocess.run(["node", fh.name], capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            errori.append(f"7%: JS dello strumento non eseguibile: {r.stderr[-300:]}")
        else:
            o = json.loads(r.stdout)
            for c, s in zip(comuni, o["st"]):
                attesi = ["area" if not area(c) else ("ok" if c[5 + i] <= soglia else "over") for i in (0, 1)]
                n_js += 2
                if s != attesi:
                    errori.append(f"7%: strumento, {c[1]}: JS {s} ≠ Python {attesi}")
                    break
            sbagliati = [c[1] for c, x in zip(comuni, o["ce"]) if not x]
            if sbagliati:
                errori.append(f"7%: la ricerca per nome esatto non trova per primi {len(sbagliati)} Comuni (es. {sbagliati[:3]})")
            if o["bo"] != ["ok", "over", "area"]:
                errori.append(f"7%: strumento sbagliato sulla soglia esatta (30.000 = sotto, 30.001 = sopra): {o['bo']}")
            if o["pr"][0][:1] != ["Ostuni"] or o["pr"][1][:1] != ["Grottaglie"] or o["pr"][2][:1] != ["Cefalù"] or o["pr"][5]:
                errori.append(f"7%: ricerca di prova inattesa: {o['pr']}")
    for f, link in (("index.html", 'href="italy-7-percent-flat-tax/"'), ("how-it-works/index.html", 'href="../italy-7-percent-flat-tax/"'),
                    ("italy-digital-nomad-visa/index.html", 'href="../italy-7-percent-flat-tax/"'), ("country/italy/index.html", 'href="../../italy-7-percent-flat-tax/"'),
                    ("about/index.html", 'href="../italy-7-percent-flat-tax/"')):
        if link not in (SITO / f).read_text(encoding="utf-8"):
            errori.append(f"7%: {f} non rimanda alla sezione")
    riletti = []
    if online:
        sys.path.insert(0, str(SITO.parent / "raccolta"))
        import flat7 as R7
        voci = [(k, v["fonte"], v["frammento"]) for k, v in D["letture"].items() if v["fonte"] in ("art24ter", "l34", "ade", "art247", "circ21e")]
        rng = random.Random(20261031)
        testi = {}
        for nome, fonte, fr in rng.sample(voci, 8):
            if fonte not in testi:
                _m, testi[fonte], _b = R7.leggi(R7.FONTI[fonte])
            ok = fr in testi[fonte]
            riletti.append(f"{fonte} {nome}: {'presente' if ok else 'ASSENTE'}")
            if not ok:
                errori.append(f"7%: frammento {nome} non più in {fonte}")
    return errori, len(P), n_js, riletti


# ---------------------------------------------------------------- 24. Schengen visa from the UK / from Dubai (31/10/2026)
def controlla_sr():
    """24. Ricalcolo indipendente (vedi in cima al file). Restituisce (errori, pagine controllate)."""
    import hashlib
    from decimal import Decimal, ROUND_HALF_UP
    errori = []
    R = json.loads((SITO.parent / "dati" / "rifiuti.json").read_text(encoding="utf-8"))
    C = json.loads((SITO.parent / "dati" / "cambi.json").read_text(encoding="utf-8"))
    S = json.loads((SITO.parent / "dati" / "schengen_residenti.json").read_text(encoding="utf-8"))
    cont = {k: S[k] for k in ("fonti", "letture", "riferimento", "fornitori", "ancoraggio_righe")}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != S["impronta"]:
        errori.append("SR: impronta di dati/schengen_residenti.json diversa dal contenuto")
    anni = sorted(R["schengen"], key=int)
    a1, a0 = anni[-1], anni[-2]
    peg = S["letture"]["ancoraggio"]["valore"]
    tassa, bimbi, cop = (S["letture"][k]["valore"] for k in ("tassa_adulti", "tassa_bambini", "copertura"))
    if (tassa, bimbi, cop, peg) != (90, 45, 30000, 3.6725):
        errori.append(f"SR: valori ufficiali cambiati ({tassa}, {bimbi}, {cop}, {peg}): ricontrollare i testi delle pagine")

    def r2(x):
        return Decimal(repr(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def fmt(x, val):
        d = r2(x)
        t = f"{d:,.2f}"
        t = t[:-3] if t.endswith(".00") else t
        return {"GBP": "£", "EUR": "€"}.get(val, f"{val} ") + t

    def locale(eur, val):
        return eur * C["tassi"]["GBP"] if val == "GBP" else eur * C["tassi"]["USD"] * peg

    def somma(righe):
        v = [0, 0, 0, 0, 0]
        for r in righe:
            for i in range(5):
                v[i] += r[3 + i]
        return v

    def pc(v):
        d = v[1] + v[2] + v[3]
        return v[3] / d if d else None

    def slug(s):
        return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

    def art(s):
        return ("the " + s) if s in ("Netherlands", "Czech Republic") else s

    sitemap = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    n = 0
    paesi = {"UNITED KINGDOM": ("schengen-visa-from-uk/", "GBP", "gb", "from the UK"), "UNITED ARAB EMIRATES": ("schengen-visa-from-dubai/", "AED", "ae", "from Dubai")}
    forn = {(F["paese"], F["stato"]) for F in S["fornitori"]}
    for P, (sez, val, gl, da) in paesi.items():
        righe1 = [r for r in R["schengen"][a1] if r[1] == P]
        righe0 = [r for r in R["schengen"][a0] if r[1] == P]
        stati = {}
        for r in righe1:
            stati.setdefault(r[0], []).append(r)
        st1 = {s: somma(rr) for s, rr in stati.items()}
        st0 = {}
        for r in righe0:
            st0.setdefault(r[0], []).append(r)
        st0 = {s: somma(rr) for s, rr in st0.items()}
        ok = sorted([s for s, v in st1.items() if v[0] >= 1000], key=lambda s: (pc(st1[s]), s))
        sotto = sorted([s for s, v in st1.items() if v[0] < 1000 and (v[0] or v[1] + v[2] + v[3])], key=lambda s: -st1[s][0])
        attese = [""] + [slug(s) for s in ok]
        pag = _pagine_sezione(sez, attese, errori, f"SR {gl}", affiliati=True)
        n += len(pag)
        if "" not in pag:
            continue
        t, main, testo, lead, _ = pag[""]
        tot = somma(righe1)
        if (f"did not issue <strong>{pc(tot) * 100:.1f}%</strong> of the {tot[1] + tot[2] + tot[3]:,} visa applications they decided" not in main
                or "European Commission" not in lead or not RE_DATA.search(lead) or "home-affairs.ec.europa.eu" not in main.split("</p>", 1)[0]):
            errori.append(f"SR {gl}: prima frase dell'hub senza cifra ricalcolata, fonte o data")
        if f"<strong>{html.escape(art(ok[0]))}</strong> had the lowest rate ({pc(st1[ok[0]]) * 100:.1f}%)" not in main or f"<strong>{art(ok[-1])}</strong> the highest" not in main:
            errori.append(f"SR {gl}: Stato più basso o più alto dell'hub diverso dal ricalcolo ({ok[0]}, {ok[-1]})")
        tab = re.search(rf'<table class="ord" id="t-sr-{gl}">.*?</table>', main, re.S)
        lette = []
        for tr in re.findall(r"<tr[^>]*><td>(.*?)</tr>", tab.group(0) if tab else "", re.S):
            nome = html.unescape(re.sub(r"<[^>]+>", "", tr.split("</td>", 1)[0]))
            lette.append((nome, re.findall(r'data-v="([^"]*)"', tr)))
        if [x[0] for x in lette] != ok + sotto:
            errori.append(f"SR {gl}: Stati o ordine della tabella dell'hub diversi dal ricalcolo")
        for nome, dv in lette:
            v, v0 = st1.get(nome), st0.get(nome)
            mev = sum(r[7] for r in stati.get(nome, [])), v[1] if v else 0
            atteso = [f"{pc(v):.6f}", (f"{pc(v0):.6f}" if v0 and v0[1] + v0[2] + v0[3] else ""), str(v[0]), str(v[3]),
                      (f"{mev[0] / mev[1]:.6f}" if mev[1] else "")]
            if dv != atteso:
                errori.append(f"SR {gl}: riga {nome} della tabella dell'hub {dv} diversa dal ricalcolo {atteso}")
        def righe_costi(main):
            return [f'<td class="n">€{a:,}</td><td class="n">{fmt(locale(a, val), val)}</td>' for a in (tassa, bimbi, cop)]
        for x in righe_costi(main):
            if x not in main:
                errori.append(f"SR {gl}: riga dei costi {x} assente o diversa dal ricalcolo nell'hub")
        if 'rel="sponsored noopener"' in main and "safetywing.com" not in main and "tradedoubler.com" not in main and "axa-schengen.com" not in main:
            errori.append(f"SR {gl}: link sponsorizzato non previsto nell'hub")

        def riquadro_sw(main, dove):
            # revisione 31/10/2026: SafetyWing non garantisce l'accettazione per il visto Schengen; il riquadro deve dirlo con le sue parole
            # e non presentare la polizza come adatta alla domanda ("for your application")
            if "safetywing.com" in main:
                box = re.search(r'<section class="card aff-r"[^>]*>.*?</section>', main, re.S)
                b = box.group(0) if box else ""
                if "cannot guarantee" not in b or "safetywing.com/nomad-insurance/faq" not in b or not RE_DATA.search(html.unescape(re.sub(r"<[^>]+>", "", b))):
                    errori.append(f"SR {gl}: riquadro SafetyWing senza la frase 'cannot guarantee', la FAQ o la data in {dove}")
                if re.search(r"for your application|meets? the (visa )?requirements?|accepted by (the )?consulates|valid for (a|the|your) (Schengen )?visa", b, re.I):
                    errori.append(f"SR {gl}: riquadro SafetyWing presenta la polizza come adatta al visto in {dove}")
        riquadro_sw(main, "hub")
        # pagine degli Stati
        for s in ok:
            k = slug(s)
            if k not in pag:
                continue
            t, main, testo, lead, perc = pag[k]
            v = st1[s]
            dec = v[1] + v[2] + v[3]
            if (f"received {v[0]:,} Schengen visa applications made" not in lead or f"did not issue {pc(v) * 100:.1f}% of the {dec:,}" not in lead
                    or "European Commission" not in lead or not RE_DATA.search(lead)):
                errori.append(f"SR {gl}: prima frase di {k} diversa dal ricalcolo o senza fonte e data")
            if f"<strong>{pc(v) * 100:.1f}%</strong> not issued ({v[3]:,} of {dec:,} decisions)" not in main:
                errori.append(f"SR {gl}: riquadro di {k} diverso dal ricalcolo")
            if f"<b>{ok.index(s) + 1} of {len(ok)}</b>" not in main:
                errori.append(f"SR {gl}: posizione di {k} diversa dal ricalcolo")
            tc = re.search(r'<table class="ord" id="t-cons-sr">.*?</table>', main, re.S)
            righe_c = re.findall(r"<tr><td>(.*?)</td>(.*?)</tr>", tc.group(0) if tc else "", re.S)
            attese_c = sorted((r for r in stati[s] if r[3] > 0), key=lambda r: -r[3])
            if len(righe_c) != len(attese_c):
                errori.append(f"SR {gl}: righe dei consolati di {k} ({len(righe_c)}) diverse dal file ({len(attese_c)})")
            for (citta, celle), r in zip(righe_c, attese_c):
                dv = re.findall(r'data-v="([^"]*)"', celle)
                if citta.upper() != r[2] or dv[:4] != [f"{pc(r[3:7]):.6f}", str(r[3]), str(r[4]), str(r[6])]:
                    errori.append(f"SR {gl}: consolato {citta} di {k} diverso dal file")
            for x in righe_costi(main):
                if x not in main:
                    errori.append(f"SR {gl}: riga dei costi {x} assente o diversa dal ricalcolo in {k}")
            for imp, v_, _ in S["riferimento"][s]["importi"]:
                eur = imp if v_ == "EUR" else imp / C["tassi"][v_]
                if f"≈ <strong>{fmt(locale(eur, val), val)}</strong>" not in main:
                    errori.append(f"SR {gl}: importo di riferimento {v_} {imp} di {k} non convertito come atteso ({fmt(locale(eur, val), val)})")
            if html.escape(S["riferimento"][s]["frammento"][len(s):].lstrip("* "), quote=True) not in main:
                errori.append(f"SR {gl}: parole della tabella degli importi di riferimento mancanti in {k}")
            nomi_forn = re.search(r"VFS|TLScontact|BLS International", testo)
            if (P, s) in forn and not nomi_forn:
                errori.append(f"SR {gl}: fornitore letto ma non scritto in {k}")
            if (P, s) not in forn and nomi_forn:
                errori.append(f"SR {gl}: fornitore nominato senza lettura della pagina ufficiale in {k}")
            if re.search(r"you will (get|be granted)|guarantee[ds]? (a|your) visa|easy to get", testo, re.I):
                errori.append(f"SR {gl}: promessa sul visto in {k}")
            if "the consulate decides" not in testo.lower():
                errori.append(f"SR {gl}: manca 'the consulate decides' in {k}")
            riquadro_sw(main, k)
        # link dalle pagine dei rifiuti
        slug_p = "united-kingdom" if P == "UNITED KINGDOM" else "united-arab-emirates"
        rp = (SITO / "visa-refusal-rates" / slug_p / "index.html").read_text(encoding="utf-8")
        titolo = html.unescape(re.search(r"<title>(.*?)</title>", rp).group(1))
        if not titolo.startswith(f"Schengen visa {da}") or len(titolo) > 70:
            errori.append(f"SR {gl}: titolo della pagina dei rifiuti {slug_p}: {titolo!r}")
        primo = re.search(r'<p class="lead">(.*?)</p>', rp.split('<main id="main">', 1)[1], re.S).group(1)
        if f'href="../../{sez}"' not in primo or f"{pc(tot) * 100:.1f}%" not in primo:
            errori.append(f"SR {gl}: la prima risposta della pagina dei rifiuti {slug_p} non porta all'hub o ha un'altra cifra")
        fp = (SITO / "visa-refusal-rates" / slug_p / "easiest-schengen-visa" / "index.html").read_text(encoding="utf-8")
        if f'href="../../../{sez}"' not in fp:
            errori.append(f"SR {gl}: la pagina easiest di {slug_p} non porta all'hub")
        for s in ok:
            ps = (SITO / "visa-refusal-rates" / "schengen" / slug(s) / "index.html").read_text(encoding="utf-8")
            if f'href="../../../{sez}{slug(s)}/"' not in ps:
                errori.append(f"SR {gl}: la pagina Schengen di {s} non porta a {sez}{slug(s)}/")
    home = (SITO / "index.html").read_text(encoding="utf-8")
    pano = (SITO / "visa-refusal-rates" / "index.html").read_text(encoding="utf-8")
    pie = (SITO / "about" / "index.html").read_text(encoding="utf-8").split("<footer>", 1)[1]
    for sez in ("schengen-visa-from-uk/", "schengen-visa-from-dubai/"):
        if f'href="{sez}"' not in home or f'href="../{sez}"' not in pano or f'href="../{sez}"' not in pie:
            errori.append(f"SR: link a {sez} mancante dalla home, dalla panoramica dei rifiuti o dal piè di pagina")
    # riquadro AXA: spento finché l'URL è vuoto; acceso con un URL di prova ha rel sponsored, etichetta e dicitura
    aff = json.loads((SITO.parent / "dati" / "affiliati.json").read_text(encoding="utf-8"))
    if "_axa_schengen" not in aff:
        errori.append("SR: voce _axa_schengen mancante in dati/affiliati.json")
    elif not aff["_axa_schengen"]["url"]:
        if G.box_axa("../") != "" or any("axa-schengen" in f.read_text(encoding="utf-8").split('<main id="main">', 1)[1].lower()
                                          for f in (SITO / "schengen-visa-from-uk").rglob("index.html")):
            errori.append("SR: riquadro AXA visibile con l'URL vuoto")
        vecchio = G.URL_AXA
        G.URL_AXA = "https://clk.tradedoubler.com/click?p=0&a=0&url=https%3A%2F%2Fwww.axa-schengen.com%2F"
        prova = G.box_axa("../")
        G.URL_AXA = vecchio
        if 'rel="sponsored noopener"' not in prova or "Affiliate" not in prova or G.MON.RIGA_EN not in prova or "does not change the decision" not in prova:
            errori.append("SR: riquadro AXA (prova con URL) senza rel sponsored, etichetta o dicitura")
    return errori, n

# ---------------------------------------------------------------- 25. Esperimento "pagine più facili da citare" (31/10/2026)
def controlla_esperimento():
    import csv
    import hashlib
    import importlib.util
    errori = []
    fj = SITO.parent / "dati" / "esperimento_citazioni.json"
    if not fj.exists():
        return ["Esperimento: dati/esperimento_citazioni.json mancante"], 0, 0, 0
    E = json.loads(fj.read_text(encoding="utf-8"))
    spec = importlib.util.spec_from_file_location("esp_cit", SITO.parent / "raccolta" / "esperimento_citazioni.py")
    X = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(X)
    # 1. gruppi: stesso risultato dal seme e dalla linea di base salvata; coppie = pagine Paese meno le escluse
    pag = [(s, v["nome"], v["domande"]) for s, v in E["pagine"].items()]
    lb = {s: [v["visite"], v["visite_assistente"]] for s, v in E["pagine"].items()}
    if X.coppie_e_gruppi(pag, lb, E["seme"]) != E["coppie"]:
        errori.append("Esperimento: coppie o pagine trattate diverse da quelle ricalcolate con il seme")
    slug_p = {G.SLUG_RIF[p]: p for p in G.PAESI_RIF}
    in_coppia = [s for c in E["coppie"] for s in c["pagine"]]
    if sorted(in_coppia + list(E["escluse"])) != sorted(slug_p) or len(set(in_coppia)) != len(in_coppia):
        errori.append("Esperimento: le coppie non coprono esattamente le pagine Paese meno le escluse")
    tratt = [c["trattata"] for c in E["coppie"]]
    contr = [s for c in E["coppie"] for s in c["pagine"] if s != c["trattata"]]
    if sorted(tratt) != E["trattate"] or sorted(contr) != E["controllo"] or set(tratt) != G.TRATTATE:
        errori.append("Esperimento: elenchi trattate/controllo incoerenti con le coppie o con genera.TRATTATE")
    R = json.loads((SITO.parent / "dati" / "rifiuti.json").read_text(encoding="utf-8"))
    anni = sorted(R["schengen"], key=int)
    a1, a0 = anni[-1], anni[-2]
    reg = json.loads((SITO.parent / "dati" / "lastmod.json").read_text(encoding="utf-8"))["pagine"]

    def somme(anno, paese):   # ricalcolo indipendente: Stato -> [domande, uniformi, LTV, non rilasciati, MEV]
        out = {}
        for r in R["schengen"][anno]:
            if r[1] == paese:
                v = out.setdefault(r[0], [0, 0, 0, 0, 0])
                for i in range(5):
                    v[i] += r[3 + i]
        return out

    def pc(n, d):
        return f"{n / d * 100:.1f}" if d else ""

    n_csv = 0
    for s in tratt:
        p = slug_p[s]
        t = leggi(f"visa-refusal-rates/{s}/index.html")
        perc = f"visa-refusal-rates/{s}/"
        d = reg.get(perc, [None])[0]
        hero = re.search(r'<section class="hero">.*?</section>', t, re.S).group(0)
        if f'<p class="agg">Updated on <time class="agg-t" datetime="{d}">{G.data_lunga(d)}</time>' not in hero:
            errori.append(f"Esperimento {s}: data 'Updated on' assente dal titolo o diversa dal lastmod {d}")
        lds = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)]
        tipi = {x["@type"]: x for x in lds}
        wp, ds = tipi.get("WebPage", {}), tipi.get("Dataset", {})
        if wp.get("dateModified") != d or ds.get("dateModified") != d:
            errori.append(f"Esperimento {s}: dateModified del JSON-LD diverso dal lastmod {d}")
        if any("datePublished" in x for x in lds):
            errori.append(f"Esperimento {s}: datePublished aggiunto (non c'era prima)")
        dist = ds.get("distribution") or [{}]
        if (ds.get("license") != "https://creativecommons.org/licenses/by/4.0/" or dist[0].get("contentUrl") != f"{G.URL_SITO}/{perc}data.csv"
                or dist[0].get("encodingFormat") != "text/csv" or len(ds.get("description", "")) < 50):
            errori.append(f"Esperimento {s}: schema Dataset senza licenza, descrizione o link al CSV")
        kf = re.search(r'<section class="card kf" id="key-figures".*?</section>', t, re.S)
        if not kf or t.index('id="key-figures"') > t.index('class="card summary"'):
            errori.append(f"Esperimento {s}: riquadro Key figures mancante o non in cima")
            continue
        kf = kf.group(0)
        st1, st0 = somme(a1, p), somme(a0, p)
        T1 = [sum(v[i] for v in st1.values()) for i in range(5)]
        T0 = [sum(v[i] for v in st0.values()) for i in range(5)]
        dec1, dec0 = T1[1] + T1[2] + T1[3], T0[1] + T0[2] + T0[3]
        attesi = [f"{T1[0]:,}", pc(T1[3], dec1) + "%", f"{T1[3]:,}", f"{dec1:,}", f"{T1[1]:,}"] + ([pc(T0[3], dec0) + "%"] if dec0 else [])
        visti = re.findall(r"<b>([^<]+)</b>", kf)
        if visti != attesi:
            errori.append(f"Esperimento {s}: numeri del riquadro {visti} diversi dal ricalcolo {attesi}")
        if len(re.findall(r"<li>", kf)) not in (3, 4, 5) or kf.count(f"In {a1},") < 2:
            errori.append(f"Esperimento {s}: riquadro senza 3-5 frasi complete con l'anno")
        f1 = R["fonti"][f"schengen_{a1}"]
        if (html.escape(f1["url"]) not in kf or "downloaded on " + G.data_lunga(f1["scaricato_il"]) not in kf
                or "https://commission.europa.eu/legal-notice_en" not in kf or "2011/833/EU" not in kf or 'href="data.csv"' not in kf):
            errori.append(f"Esperimento {s}: fonte con link e data, licenza o link al CSV mancanti nel riquadro")
        # data.csv
        fc = SITO / perc / "data.csv"
        if not fc.exists():
            errori.append(f"Esperimento {s}: data.csv mancante")
            continue
        righe = list(csv.reader(fc.read_text(encoding="utf-8").splitlines()))
        n_csv += 1
        if righe[0] != G.COLONNE_CSV or any(len(r) != len(G.COLONNE_CSV) for r in righe):
            errori.append(f"Esperimento {s}: data.csv con intestazione o numero di campi sbagliati")
            continue
        atteso = []
        for anno, st in ((a1, st1), (a0, st0)):
            if not st:
                continue
            tot = [sum(v[i] for v in st.values()) for i in range(5)]
            for nome_s, v in [("All Schengen countries", tot)] + sorted(st.items(), key=lambda x: (-x[1][0], x[0])):
                dd = v[1] + v[2] + v[3]
                if v[0] == 0 and dd == 0:
                    continue
                atteso.append([anno, G.nome_paese(p), nome_s, str(v[0]), str(v[1]), str(v[4]), str(v[2]), str(v[3]), str(dd), pc(v[3], dd)])
        if righe[1:] != atteso:
            errori.append(f"Esperimento {s}: data.csv diverso dal ricalcolo da dati/rifiuti.json")
        for r in righe[1:]:
            if not all(x.isdigit() for x in r[3:9]) or (r[9] and not re.fullmatch(r"\d{1,3}\.\d", r[9])):
                errori.append(f"Esperimento {s}: data.csv con valori non numerici")
                break
    # 3. controllo: identico a prima
    uguali_byte = 0
    for s in contr:
        t = leggi(f"visa-refusal-rates/{s}/index.html")
        segni = [m for m in G.SEGNI_ESPERIMENTO if m in t] + (["Updated on"] if "Updated on" in t else []) + (["Key figures"] if "Key figures" in t else [])
        if segni:
            errori.append(f"Esperimento {s} (controllo): elementi del trattamento {segni}")
        if (SITO / "visa-refusal-rates" / s / "data.csv").exists():
            errori.append(f"Esperimento {s} (controllo): data.csv presente")
        imp = E["impronte_controllo"].get(s, {})
        if G.impronta_contenuto(t) != imp.get("contenuto"):
            errori.append(f"Esperimento {s} (controllo): contenuto cambiato rispetto all'impronta salvata il {E['creato_il']}")
        uguali_byte += hashlib.sha256(t.encode("utf-8")).hexdigest() == imp.get("file_sha256")
    # nessun segno del trattamento fuori dalle pagine trattate, nessun segnaposto rimasto
    for f in SITO.rglob("index.html"):
        r = f.relative_to(SITO).as_posix()
        tt = f.read_text(encoding="utf-8")
        if G.AGG_ISO in tt or G.AGG_TESTO in tt:
            errori.append(f"Esperimento: segnaposto della data rimasto in {r}")
        if ('id="key-figures"' in tt or 'class="agg-t"' in tt) and r not in {f"visa-refusal-rates/{s}/index.html" for s in tratt}:
            errori.append(f"Esperimento: elementi del trattamento fuori dal gruppo trattato in {r}")
    return errori, len(tratt), n_csv, uguali_byte


# ---------------------------------------------------------------- 26. Australian citizenship ceremony wait times (31/10/2026)
_PCT = re.compile(r"^\d{1,3}%$")


def _celle(tr):
    return [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]


def _media(righe):
    tot = sum(r[2] or 0 for r in righe)
    return tot, [sum((r[2] or 0) * r[3 + i] for r in righe) / tot for i in range(3)] if tot else [0, 0, 0]


def controlla_cer():
    """26. Ricalcolo indipendente da dati/cerimonie.json e dalla risposta grezza di Home Affairs (raccolta/_grezzi/cerimonie/, o riscaricata
    con lo stesso POST se online): righe del JSON = risposta ufficiale; pagine attese = indice + council con 3+ suggerimenti e persone in attesa
    + pagina dei tempi, in sitemap, titoli ≤ 70; prima frase con cifra, fonte e data; tabella dell'indice = 539 righe del JSON (nome, Stato,
    numero, 3 quote, data); tabella degli Stati = ricalcolo ponderato; pagine dei council: cifre, posizione nello Stato, confronto, storico,
    council vicini; pagina dei tempi: percentili, domande in lavorazione e ricevute; avviso "Home Affairs and your council decide", licenza
    CC BY 3.0 AU, nessuna data di cerimonia inventata, nessun link sponsorizzato; link da home, pagina Australia, How it works."""
    import hashlib
    errori = []
    D = json.loads((SITO.parent / "dati" / "cerimonie.json").read_text(encoding="utf-8"))
    cont = {k: D[k] for k in ("fonti", "lista", "tempi", "storico", "storico_tempi")}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != D["impronta"]:
        errori.append("Cerimonie: impronta di dati/cerimonie.json diversa dal contenuto")
    L, T = D["lista"], D["tempi"]
    righe, al, pub = L["righe"], L["al"], L["modificata"]
    per_nome = {r[0]: r for r in righe}
    # 1. risposta ufficiale grezza
    raw = None
    f = SITO.parent / "raccolta" / "_grezzi" / "cerimonie" / f"lista-{al}.json"
    if f.exists():
        raw = f.read_bytes()
    elif "--offline" not in sys.argv:
        try:
            req = urllib.request.Request(D["fonti"]["lista"]["url"], data=json.dumps({"webUrl": "/", "listName": "citizenshipCeremony"}).encode(),
                                         headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": "Mozilla/5.0"})
            raw = urllib.request.urlopen(req, timeout=90).read()
        except Exception:  # noqa: BLE001
            raw = None
    n_raw = 0
    if raw is not None:
        uff = json.loads(raw.decode("utf-8"))["d"]["data"]
        if hashlib.sha256(raw).hexdigest() != D["fonti"]["lista"]["sha256"] and {x["Modified"] for x in uff} == {"/".join(reversed(pub.split("-")))}:
            errori.append("Cerimonie: risposta ufficiale con la stessa data ma contenuto diverso da quello salvato")
        if {x["Modified"] for x in uff} == {"/".join(reversed(pub.split("-")))}:
            if len(uff) != len(righe):
                errori.append(f"Cerimonie: {len(uff)} righe ufficiali, {len(righe)} nel JSON")
            for x in uff:
                nome = html.unescape(x["Title"]).replace("​", "").strip()
                r = per_nome.get(nome)
                tot = html.unescape(x["TotalApprovedApplicants"]).strip()
                atteso = [nome, x["State"].strip(), None if tot == "<5" else int(tot.replace(",", "")),
                          int(x["LessThanThreeMonths"].strip("% ")), int(x["WaitTime3To6Months"].strip("% ")), int(x["Wait_x0020_time_x0020_more_x0020"].strip("% "))]
                if r != atteso:
                    errori.append(f"Cerimonie: riga di {nome} diversa dalla risposta ufficiale ({r} invece di {atteso})")
                n_raw += 1
    # 2. pagine attese
    soglia = 3
    if G.SOGLIA_DOMANDA_CER != soglia:
        errori.append("Cerimonie: soglia della domanda cambiata in genera.py senza aggiornare il controllo 26")
    con_pagina = [r for r in righe if len(D["domanda"]["council"].get(r[0], [])) >= soglia and r[2]]
    slug = G.SLUG_CER
    if len(set(slug.values())) != len(slug):
        errori.append("Cerimonie: slug ripetuti")
    pag = _pagine_sezione(G.SEZ_CER, [""] + [slug[r[0]] for r in con_pagina], errori, "Cerimonie")
    pag.update({"tempi": x for x in _pagine_sezione(G.SEZ_TEMPI_CER, [""], errori, "Cerimonie tempi").values()})
    tot, med = _media(righe)
    dl = G.data_lunga
    for k, (t, main, testo, lead, perc) in pag.items():
        if "Home Affairs and your council decide" not in main:
            errori.append(f"Cerimonie: avviso 'Home Affairs and your council decide' mancante in {perc}")
        if "https://creativecommons.org/licenses/by/3.0/au/" not in main or "Australian Government Department of Home Affairs" not in main:
            errori.append(f"Cerimonie: licenza CC BY 3.0 AU o attribuzione mancante in {perc}")
        if "Department of Home Affairs" not in lead:
            errori.append(f"Cerimonie: la prima frase di {perc} non nomina la fonte")
        if re.search(r"ceremon[a-z]* (on|is on|will be on) \d{1,2} (" + "|".join(G.MESI) + ")", testo, re.I):
            errori.append(f"Cerimonie: data di cerimonia scritta in {perc} (Home Affairs non le pubblica)")
    # indice
    if "" in pag:
        t, main, testo, lead, perc = pag[""]
        if f"On {dl(al)}, {tot:,} people approved for Australian citizenship were waiting for a ceremony in {len(righe)} council areas" not in lead or dl(pub) not in lead:
            errori.append("Cerimonie: prima frase dell'indice senza cifra, numero di council o date ricalcolati")
        tb = re.search(r'<table class="ord" id="t-cer">.*?<tbody>(.*?)</tbody>', main, re.S)
        trs = re.findall(r'<tr data-stato="(\w+)">(.*?)</tr>', tb.group(1), re.S) if tb else []
        if len(trs) != len(righe):
            errori.append(f"Cerimonie: tabella dell'indice con {len(trs)} righe invece di {len(righe)}")
        corto = f"{int(al[8:])} {G.MESI[int(al[5:7]) - 1][:3]} {al[:4]}"
        for st, tr in trs:
            c = _celle("<tr>" + tr + "</tr>")
            r = per_nome.get(c[0])
            if not r:
                errori.append(f"Cerimonie: council {c[0]!r} nella tabella ma non nel JSON")
                continue
            q = ["–"] * 3 if r[2] == 0 else [f"{x}%" for x in r[3:]]
            if c != [r[0], r[1], "<5" if r[2] is None else f"{r[2]:,}", *q, corto] or st != r[1]:
                errori.append(f"Cerimonie: riga di {r[0]} nell'indice diversa dal JSON ({c})")
            if ('href="' in tr) != (r in con_pagina):
                errori.append(f"Cerimonie: link della riga di {r[0]} incoerente con la pagina")
        for s in G.STATI_CER:
            rr = [r for r in righe if r[1] == s]
            n_s, m_s = _media(rr)
            riga = f"<tr><td>{G.STATI_CER[s]}</td>"
            i = main.find(riga)
            c = _celle(main[i:main.find("</tr>", i) + 5]) if i >= 0 else []
            if c != [G.STATI_CER[s], str(len(rr)), f"{n_s:,}"] + [f"{x:.0f}%" for x in m_s]:
                errori.append(f"Cerimonie: riga dello Stato {s} diversa dal ricalcolo ({c})")
        kpi = re.findall(r"<b>([^<]+)</b>", main.split('class="kpi"', 1)[1].split("</div></div>", 1)[0]) if 'class="kpi"' in main else []
        if kpi[:3] != [f"{x:.0f}%" for x in med] or kpi[3] != f"{T['novanta']['cerimonia_mesi']} months":
            errori.append(f"Cerimonie: riquadro dell'indice {kpi} diverso dal ricalcolo")
    # council
    for r in con_pagina:
        s = slug[r[0]]
        if s not in pag:
            continue
        t, main, testo, lead, perc = pag[s]
        nome = "the ACT Government (Canberra)" if r[1] == "ACT" else r[0]
        frase = (f"On {dl(al)}, {r[2]:,} people approved for Australian citizenship were waiting for a ceremony with {nome} ({r[1]}): {r[3]}% had been waiting "
                 f"less than 3 months since approval, {r[4]}% between 3 and 6 months and {r[5]}% more than 6 months (Department of Home Affairs, "
                 f"ceremony wait times published on {dl(pub)}).")
        if lead.strip() != frase:
            errori.append(f"Cerimonie {s}: prima frase diversa dal ricalcolo")
        st = sorted([x for x in righe if x[1] == r[1] and x[2]], key=lambda x: (-x[2], x[0]))
        posto = [x[0] for x in st].index(r[0]) + 1
        n_st = sum(1 for x in righe if x[1] == r[1])
        if not re.search(rf"<strong>{r[2]:,}</strong> \({posto}(st|nd|rd|th) of {n_st} councils in {G.STATI_CER[r[1]]}\)", main):
            errori.append(f"Cerimonie {s}: numero o posizione nello Stato ({posto} di {n_st}) diversi")
        cmp_ = re.search(r"<h2>Compared with .*?<tbody>(.*?)</tbody>", main, re.S)
        rr = [_celle(x) for x in re.findall(r"<tr>.*?</tr>", cmp_.group(1), re.S)] if cmp_ else []
        m_s = _media([x for x in righe if x[1] == r[1]])[1]
        attese = [[f"{x}%" for x in r[3:]], [f"{x:.0f}%" for x in m_s], [f"{x:.0f}%" for x in med]]
        if [x[1:] for x in rr] != attese:
            errori.append(f"Cerimonie {s}: confronto con Stato e Australia diverso dal ricalcolo ({rr})")
        sto = re.search(r"<h2>History</h2>.*?<tbody>(.*?)</tbody>", main, re.S)
        rs = [_celle(x) for x in re.findall(r"<tr>.*?</tr>", sto.group(1), re.S)] if sto else []
        att = [[dl(d), "<5" if S["righe"][r[0]][0] is None else f"{S['righe'][r[0]][0]:,}"] + [f"{x}%" for x in S["righe"][r[0]][1:]]
               for d, S in sorted(D["storico"].items(), reverse=True) if r[0] in S["righe"]]
        if rs != att:
            errori.append(f"Cerimonie {s}: storico diverso dal JSON")
        vic = re.search(r"<h2>Other councils in .*?<tbody>(.*?)</tbody>", main, re.S)
        nv = [_celle(x)[0] for x in re.findall(r"<tr[^>]*>.*?</tr>", vic.group(1), re.S)] if vic else []
        if nv != [x[0] for x in sorted([x for x in righe if x[1] == r[1] and x[0] != r[0]], key=lambda x: (-(x[2] if x[2] is not None else 1), x[0]))][:12]:
            errori.append(f"Cerimonie {s}: council vicini diversi dal ricalcolo")
    # tempi
    if "tempi" in pag:
        t, main, testo, lead, perc = pag["tempi"]
        nov, P = T["novanta"], T["percentili"]
        if (f"90% of applications for Australian citizenship by conferral are processed within {nov['conferimento_mesi']} months" not in lead
                or f"within {nov['cerimonia_mesi']} months of approval" not in lead or dl(T["aggiornata"]) not in lead):
            errori.append("Cerimonie tempi: prima frase diversa dalle frasi ufficiali o senza data")
        for fr in ("conferimento", "cerimonia"):
            if T["frasi"][fr].replace(" ", " ") not in json.dumps(T["frasi"]):
                errori.append("Cerimonie tempi: frase ufficiale mancante nel JSON")
        tb = re.search(r"<h2>Processing times by percentile</h2>.*?<tbody>(.*?)</tbody>", main, re.S)
        rr = [_celle(x)[2:] for x in re.findall(r"<tr>.*?</tr>", tb.group(1), re.S)] if tb else []
        if rr != [P["conferimento"]["decisione"], P["conferimento"]["approvazione_cerimonia"], P["conferimento"]["domanda_cerimonia"],
                  P["discendenza"]["decisione"], P["prova"]["decisione"]]:
            errori.append(f"Cerimonie tempi: tabella dei percentili diversa dal JSON ({rr})")
        tb = re.search(r"<h2>Applications on hand and received</h2>.*?<tbody>(.*?)</tbody>", main, re.S)
        rr = [_celle(x)[1:] for x in re.findall(r"<tr>.*?</tr>", tb.group(1), re.S)] if tb else []
        if rr != [[f"{T['in_lavorazione'][k]:,}", f"{T['ricevute'][k]:,}"] for k in ("conferimento", "discendenza", "prova")]:
            errori.append("Cerimonie tempi: domande in lavorazione o ricevute diverse dal JSON")
    # collegamenti
    for f_, cosa in (("index.html", G.SEZ_CER), ("visa-refusal-rates/australia-visas/index.html", G.SEZ_CER), ("how-it-works/index.html", G.SEZ_CER),
                     ("index.html", G.SEZ_TEMPI_CER)):
        if f'href="{"" if f_ == "index.html" else "../../" if f_.count("/") == 2 else "../"}{cosa}"' not in leggi(f_):
            errori.append(f"Cerimonie: manca il link a {cosa} in {f_}")
    return errori, len(pag), n_raw


# ---------------------------------------------------------------- 27. Sezioni in spagnolo e portoghese: denaro per entrare in Europa (31/10/2026)
PAGINE_EE = {
    "es": ["", "requisitos-para-entrar-a-europa", "carta-de-invitacion-espana", "seguro-de-viaje-obligatorio-europa", "etias",
           "cuanto-dinero-para-entrar-a-espana", "cuanto-dinero-para-entrar-a-italia", "cuanto-dinero-para-entrar-a-francia",
           "cuanto-dinero-para-entrar-a-alemania", "cuanto-dinero-para-entrar-a-suiza", "cuanto-dinero-para-entrar-a-portugal"],
    "pt": ["", "requisitos-para-entrar-na-europa", "carta-convite-espanha", "seguro-viagem-obrigatorio-europa", "etias",
           "quanto-dinheiro-para-entrar-na-espanha", "quanto-dinheiro-para-entrar-na-italia", "quanto-dinheiro-para-entrar-na-franca",
           "quanto-dinheiro-para-entrar-na-alemanha", "quanto-dinheiro-para-entrar-na-suica", "quanto-dinheiro-para-entrar-em-portugal"],
}
STATI_PAG_EE = {"Spain": 5, "Italy": 6, "France": 7, "Germany": 8, "Switzerland": 9, "Portugal": 10}   # indice nella lista sopra
MESI_V = {"es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
          "pt": ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]}


def _soldi_v(x, val, l):
    """Formattazione indipendente da genera.py: separatore delle migliaia '.', decimali ',', interi senza ',00'."""
    from decimal import Decimal, ROUND_HALF_UP
    d = Decimal(repr(x)).quantize(Decimal("1") if val == "ISK" else Decimal("0.01"), rounding=ROUND_HALF_UP)
    intero, _, dec = f"{d:f}".partition(".")
    gruppi = []
    while len(intero) > 3:
        gruppi.insert(0, intero[-3:])
        intero = intero[:-3]
    t = ".".join([intero] + gruppi) + ("," + dec if dec and dec != "00" else "")
    if val == "EUR":
        return f"{t} €" if l == "es" else f"€ {t}"
    pre = {"USD": "US$ ", "MXN": "MX$ ", "BRL": "R$ "}.get(val)
    return pre + t if pre else f"{t} {val}"


def py_ee(v, dias, personas):
    """Calcolo indipendente dell'importo minimo (stesse regole lette nella tabella, scritte di nuovo qui)."""
    def r2(x):
        return math.floor(x * 100 + 0.5 + 1e-9) / 100
    def intero_js(x, predefinito):  # parseInt del browser: cifre iniziali, altrimenti il valore predefinito
        if isinstance(x, (int, float)):
            return int(x)
        m = re.match(r"\s*([-+]?\d+)", str(x))
        return int(m.group(1)) if m else predefinito
    d = min(90, max(1, intero_js(dias, 15)))
    p = min(10, max(1, intero_js(personas, 1)))
    t = v["t"]
    if t in ("dia", "dia_hasta"):
        x = v["a"] * d if (t == "dia" or d <= v["n"]) else None
    elif t == "dia_min":
        x = max(v["a"] * d, v["m"])
    elif t == "dia_min_desde":
        x = max(v["a"] * d, v["m"]) if d > v["n"] else v["a"] * d
    elif t == "entrada_dia":
        x = v["e"] + v["a"] * d
    elif t == "fijo_hasta":
        x = v["f"] if d <= v["n"] else v["a"] * d
    elif t == "fijo_hasta_solo":
        x = v["f"] if d <= v["n"] else None
    else:
        x = None
    if x is None or (v.get("solo1") and p > 1):
        return None
    return r2(x * p)


def controlla_ee(online=True):
    """27. Pagine /es/ e /pt/: impronta di dati/entrar_europa.json; pagine attese (11 + 11) in sitemap, lang, canonical, titoli ≤ 70, FAQPage,
    "la policía de fronteras decide" / "a polícia de fronteiras decide", prima frase con fonte e data; hreflang es/pt reciproci (e autoreferenziali) e
    selettore di lingua con gli stessi indirizzi; importi della tabella dell'hub = dati/schengen_residenti.json (formattazione indipendente) ed esempi a
    7/15/30 giorni = calcolo indipendente; dati del calcolatore (data-k) = importi del JSON; motore JS (preso dalla pagina) = calcolo Python su casi
    fissi e casuali; ogni citazione <q> = frammento ufficiale del JSON; tabella dei visti = allegati del Reg. 2018/1806; ETIAS senza date inventate;
    SafetyWing solo nelle due pagine sull'assicurazione, con "no puede garantizar"/"não pode garantir", FAQ, riga di trasparenza; link da home e How it works.
    Online: 10 frammenti a caso riletti sulle fonti (non le pagine ETIAS, lette con il browser)."""
    import hashlib
    errori = []
    E = json.loads((SITO.parent / "dati" / "entrar_europa.json").read_text(encoding="utf-8"))
    S = json.loads((SITO.parent / "dati" / "schengen_residenti.json").read_text(encoding="utf-8"))
    C = json.loads((SITO.parent / "dati" / "cambi.json").read_text(encoding="utf-8"))
    cont = {k: E[k] for k in ("fonti", "letture", "assenti", "paesi")}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != E["impronta"]:
        errori.append("ES/PT: impronta di dati/entrar_europa.json diversa dal contenuto")
    RIF = S["riferimento"]
    frammenti = {html.escape(L["frammento"], quote=False) for L in E["letture"].values()}
    sitemap = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    pagine = {}
    for l, slugs in PAGINE_EE.items():
        cart = SITO / l
        # dal 4/11/2026 le cartelle es/visados/ e pt/vistos/ (visti di lunga durata per nazionalità) hanno il loro controllo (28)
        trovate = {f.parent.relative_to(cart).as_posix().replace(".", "") for f in cart.rglob("index.html")
                   if f.relative_to(cart).parts[0] not in ("visados", "vistos")}
        if trovate != set(slugs):
            errori.append(f"ES/PT {l}: pagine diverse da quelle attese (in più {sorted(trovate - set(slugs))}, mancanti {sorted(set(slugs) - trovate)})")
        for i, sl in enumerate(slugs):
            perc = f"{l}/{sl + '/' if sl else ''}"
            f = SITO / perc / "index.html"
            if not f.exists():
                continue
            t = f.read_text(encoding="utf-8")
            pagine[(l, i)] = (perc, t)
            main = t.split('<main id="main">', 1)[1].split("</main>", 1)[0]
            testo = html.unescape(re.sub(r"<[^>]+>", " ", main))
            if f"<loc>{G.URL_SITO}/{perc}</loc>" not in sitemap:
                errori.append(f"ES/PT: {perc} non in sitemap")
            if f'<html lang="{l}">' not in t:
                errori.append(f"ES/PT: {perc} senza lang=\"{l}\"")
            if f'<link rel="canonical" href="{G.URL_SITO}/{perc}">' not in t:
                errori.append(f"ES/PT: canonical sbagliato in {perc}")
            tit = html.unescape(re.search(r"<title>(.*?)</title>", t).group(1))
            if len(tit) > 70:
                errori.append(f"ES/PT: titolo oltre 70 caratteri in {perc} ({len(tit)})")
            if "FAQPage" not in t or (sl and "BreadcrumbList" not in t):
                errori.append(f"ES/PT: FAQPage o BreadcrumbList mancanti in {perc}")
            decide = "la policía de fronteras decide" if l == "es" else "a polícia de fronteiras decide"
            if decide not in testo:
                errori.append(f"ES/PT: manca «{decide}» in {perc}")
            lead = re.search(r'<p class="lead">(.*?)</p>', main, re.S).group(1)
            lead_t = html.unescape(re.sub(r"<[^>]+>", "", lead))
            if (not re.search(r"\b\d{1,2} de (" + "|".join(MESI_V[l]) + r") de 20\d\d\b", lead_t) or 'href="http' not in lead
                    or not re.search(r"Comisión Europea|Comissão Europeia|Código|Orden PRE|ETIAS", lead_t)):
                errori.append(f"ES/PT: prima frase di {perc} senza fonte, link o data")
            ammessi = {_soldi_v(x, val, l) for St in RIF.values() for x, val, _ in St["importi"]}
            for St in RIF.values():
                for x, val, _ in St["importi"]:
                    ammessi |= {_soldi_v(round(x * d_, 2), val, l) for d_ in range(1, 91)} | {_soldi_v(round(x * d_ / C["tassi"][val], 2), "EUR", l) for d_ in range(1, 91) if val != "EUR"}
            ammessi |= {_soldi_v(round(RIF["Portugal"]["importi"][0][0] + RIF["Portugal"]["importi"][1][0] * d_, 2), "EUR", l) for d_ in range(1, 91)}
            ammessi |= {_soldi_v(E["letture"]["es_seguro_30000"]["valore"], "EUR", l)}
            for cifra in re.findall(r"(?:€\u00a0[\d.,]*\d|[\d.,]*\d\u00a0(?:€|CHF|CZK|DKK|NOK|PLN|SEK|ISK))", lead_t):
                if cifra not in ammessi:
                    errori.append(f"ES/PT: cifra della prima frase di {perc} non nei dati né ricalcolabile: {cifra}")
            for q in re.findall(r"<q>(.*?)</q>", main, re.S):
                if q not in frammenti:
                    errori.append(f"ES/PT: citazione non uguale al frammento ufficiale in {perc}: {q[:70]}")
            if re.search(r'rel="[^"]*sponsored', main) and "seguro" not in sl:
                errori.append(f"ES/PT: link sponsorizzato fuori dalle pagine sull'assicurazione ({perc})")
            for x in ("Some links are affiliate links", "Algunos enlaces" if l == "es" else "Alguns links"):
                if re.search(r'rel="[^"]*sponsored', main) and x not in testo:
                    errori.append(f"ES/PT: riga di trasparenza «{x}» mancante in {perc}")
            # parole vietate in spagnolo (controllo 5): "llama" è anche una parola spagnola; nessuna nelle pagine
    # hreflang reciproci e selettore di lingua
    for (l, i), (perc, t) in pagine.items():
        alt = dict(re.findall(r'<link rel="alternate" hreflang="(es|pt)" href="([^"]+)">', t))
        altro = "pt" if l == "es" else "es"
        if alt.get(l) != f"{G.URL_SITO}/{perc}":
            errori.append(f"ES/PT: hreflang {l} non autoreferenziale in {perc}")
        cop = pagine.get((altro, i))
        if not cop or alt.get(altro) != f"{G.URL_SITO}/{cop[0]}":
            errori.append(f"ES/PT: hreflang {altro} sbagliato in {perc}")
        elif dict(re.findall(r'<link rel="alternate" hreflang="(es|pt)" href="([^"]+)">', cop[1])).get(l) != f"{G.URL_SITO}/{perc}":
            errori.append(f"ES/PT: hreflang non reciproco tra {perc} e {cop[0]}")
        sel = re.search(r'<nav class="lingue".*?</nav>', t, re.S)
        rel = "../" * perc.count("/")
        if not sel or (cop and f'href="{rel}{cop[0]}" lang="{altro}"' not in sel.group(0)) or f'href="{rel}" lang="en"' not in sel.group(0):
            errori.append(f"ES/PT: selettore di lingua mancante o diverso dagli hreflang in {perc}")
    # tabella dell'hub e dati del calcolatore
    n_js = 0
    for l in ("es", "pt"):
        if (l, 0) not in pagine:
            continue
        t = pagine[(l, 0)][1]
        tab = re.search(r'<table class="pila" id="t-ee">.*?</table>', t, re.S)
        corpo_t = re.search(r"<tbody>(.*?)</tbody>", tab.group(0), re.S).group(1) if tab else ""
        righe = re.findall(r"<tr><th[^>]*>(.*?)</th><td[^>]*>(.*?)</td>(.*?)</tr>", corpo_t, re.S)
        if len(righe) != len(RIF):
            errori.append(f"ES/PT {l}: {len(righe)} righe nella tabella dell'hub, {len(RIF)} Stati nel JSON")
        kraw = re.search(r"data-ee data-k='(.*?)'", t)
        K = json.loads(html.unescape(kraw.group(1))) if kraw else {"stati": {}}
        if set(K["stati"]) != set(RIF):
            errori.append(f"ES/PT {l}: Stati del calcolatore diversi dalla tabella della Commissione")
        nomi = {s: K["stati"][s]["nome"] for s in K["stati"]}
        per_nome = {v: s for s, v in nomi.items()}
        for th, td, resto in righe:
            nome = html.unescape(re.sub(r"<[^>]+>", "", th)).strip()
            s = per_nome.get(nome)
            if not s:
                errori.append(f"ES/PT {l}: Stato sconosciuto nella tabella: {nome}")
                continue
            celle = html.unescape(td)
            for x, val, _ in RIF[s]["importi"]:
                if _soldi_v(x, val, l) not in celle:
                    errori.append(f"ES/PT {l}: importo {x} {val} di {s} mancante nella tabella dell'hub")
            if html.escape(G.rif_testo_sr(s)) not in td:
                errori.append(f"ES/PT {l}: testo originale della tabella mancante per {s}")
            celle_g = re.findall(r'<td[^>]*\bdata-g="(\d+)"[^>]*>(.*?)</td>', resto)
            if len(celle_g) != 3:
                errori.append(f"ES/PT {l}: esempi a 7/15/30 giorni mancanti per {s}")
            for g, cel in celle_g:
                v = K["stati"][s]["var"][0] if K["stati"][s]["var"] else None
                x = py_ee(v, int(g), 1) if v else None
                atteso = "—" if x is None else _soldi_v(x, v["val"], l)
                if atteso not in html.unescape(cel):
                    errori.append(f"ES/PT {l}: esempio {g} giorni di {s} diverso dal calcolo ({html.unescape(cel)} invece di {atteso})")
        # numeri del calcolatore = importi del JSON (stessa valuta)
        for s, St in K["stati"].items():
            imp = {(x, v) for x, v, _ in RIF[s]["importi"]}
            for v in St["var"]:
                for c in ("a", "m", "e", "f"):
                    if c in v and (v[c], v["val"]) not in imp:
                        errori.append(f"ES/PT {l}: valore {c}={v[c]} {v['val']} del calcolatore non negli importi di {s}")
            if not St["var"] and RIF[s]["importi"]:
                errori.append(f"ES/PT {l}: {s} senza cifra nel calcolatore ma con importi nella tabella")
        if any(abs(K["tassi"][v] - C["tassi"][v]) > 1e-12 for v in K["tassi"]):
            errori.append(f"ES/PT {l}: cambi del calcolatore diversi da dati/cambi.json")
        # motore JS = Python
        js = next((x for x in re.findall(r"<script>(.*?)</script>", t, re.S) if "window.CALC_EE=C" in x), None)
        if not js:
            errori.append(f"ES/PT {l}: motore JS del calcolatore mancante")
            continue
        rng = random.Random(27 + (l == "pt"))
        casi = []
        for s in sorted(K["stati"]):
            for i, v in enumerate(K["stati"][s]["var"]):
                for d in (1, 4, 5, 6, 9, 10, 29, 30, 31, 90, 0, -3, 200, "", "x", "7.9"):
                    casi.append([s, i, d, rng.choice([1, 2, 3, 0, 11])])
        stati_v = [(s, i) for s in sorted(K["stati"]) for i in range(len(K["stati"][s]["var"]))]
        for _ in range(600):
            s, i = rng.choice(stati_v)
            casi.append([s, i, rng.randint(-5, 120), rng.randint(-2, 14)])
        prog = ("var window={};var document={querySelectorAll:function(){return [];}};\n" + js + "\nvar K=" + json.dumps(K) + ";var CASI=" + json.dumps(casi) +
                ";console.log(JSON.stringify(CASI.map(function(c){var v=K.stati[c[0]].var[c[1]];var x=window.CALC_EE.calc(v,c[2],c[3]);"
                "if(x===null)return null;var e=window.CALC_EE.eur(x,v.val,K);return [x,e,K.valute.map(function(a){return window.CALC_EE.conv(e,a,K);})];})));")
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
            fh.write(prog)
        r = subprocess.run(["node", fh.name], capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            errori.append(f"ES/PT {l}: JS del calcolatore non eseguibile: {r.stderr[-300:]}")
            continue

        def r2(x):
            return math.floor(x * 100 + 0.5 + 1e-9) / 100
        diff = []
        for c, j in zip(casi, json.loads(r.stdout)):
            v = K["stati"][c[0]]["var"][c[1]]
            x = py_ee(v, c[2], c[3])
            if x is None:
                py = None
            else:
                e = x if v["val"] == "EUR" else r2(x / C["tassi"][v["val"]])
                py = [x, e, [e if a == "EUR" else r2(e * C["tassi"][a]) for a in K["valute"]]]
            if py != j:
                diff.append((c, j, py))
        n_js += len(casi)
        errori += [f"ES/PT {l}: calcolatore {c}: JS {j} ≠ Python {py}" for c, j, py in diff[:5]]
    # Spagna: 10% e 90% dello SMI 2026 = cifre della tabella
    smi = G.INDICI["es_smi"]["valore"]
    sp = RIF["Spain"]["importi"]
    if round(smi * 0.10, 2) != sp[0][0] or round(smi * 0.90, 2) != sp[1][0]:
        errori.append("ES/PT: Spagna, 10%/90% dello SMI diversi dalla tabella della Commissione")
    # tabella dei visti = allegati
    for l, i in (("es", 1), ("pt", 1)):
        if (l, i) not in pagine:
            continue
        t = pagine[(l, i)][1]
        for P in E["paesi"]:
            m = re.search(rf'<th[^>]*\bid="{P["id"]}"[^>]*>([^<]*)</th><td[^>]*\bclass="(si-v|no-v)"[^>]*>\s*(Sí|No|Sim|Não)\b', t)
            atteso = ("Sí" if l == "es" else "Sim") if P["allegato"] == 1 else ("No" if l == "es" else "Não")
            if not m or html.unescape(m.group(1)) != G.nome_paese_ee(P, l) or m.group(3) != atteso:
                errori.append(f"ES/PT {l}: riga del visto di {P[l]} diversa dall'allegato {P['allegato']}")
    # ETIAS: frase ufficiale e nessuna data di avvio
    for l, i, k in (("es", 4, "etias_es_estado"), ("pt", 4, "etias_pt_estado")):
        if (l, i) not in pagine:
            continue
        t = pagine[(l, i)][1]
        main = t.split('<main id="main">', 1)[1].split("</main>", 1)[0]
        testo = html.unescape(re.sub(r"<[^>]+>", " ", main))
        if html.escape(E["letture"][k]["frammento"], quote=False) not in main:
            errori.append(f"ES/PT {l}: frase ufficiale sullo stato dell'ETIAS mancante")
        ammessi = [G.data_ee(E["fonti"][f"etias_{l}"]["letto_il"], l), G.data_ee(E["fonti"][f"vis_{l}"]["letto_il"], l), "2018/1806", "30/12/2025",
                   f"{MESI_V[l][int(E['fonti'][f'etias_{l}']['letto_il'][5:7]) - 1]} de {E['fonti'][f'etias_{l}']['letto_il'][:4]}"]
        resto = testo
        for a in ammessi:
            resto = resto.replace(a, " ")
        if re.search(r"\b20[2-3]\d\b", resto):
            errori.append(f"ES/PT {l}: anno nella pagina ETIAS fuori dalle date di lettura (data di avvio inventata?): {re.findall(r'.{30}20[2-3]\d.{10}', resto)[:2]}")
    # SafetyWing solo nelle pagine sull'assicurazione
    for l, i in (("es", 3), ("pt", 3)):
        if (l, i) not in pagine or not G.URL_SW_EE:
            continue
        t = pagine[(l, i)][1]
        box = re.search(r'<section class="card aff-r".*?</section>', t, re.S)
        b = box.group(0) if box else ""
        for x in ("no puede garantizar" if l == "es" else "não pode garantir", G.URL_SW_FAQ, G.MON.RIGA_EN, 'rel="sponsored noopener"',
                  G.data_ee(G.DATA_SW_FAQ, l)):
            if x not in b:
                errori.append(f"ES/PT {l}: riquadro SafetyWing senza «{x}»")
        if b and t.index(b) < t.index("Código de"):
            errori.append(f"ES/PT {l}: riquadro SafetyWing prima delle regole ufficiali")
    # collegamenti dal resto del sito (home e How it works; il piè di pagina comune NON cambia)
    for f_, pre in (("index.html", ""), ("how-it-works/index.html", "../")):
        for l in ("es", "pt"):
            if f'href="{pre}{l}/"' not in leggi(f_):
                errori.append(f"ES/PT: manca il link a /{l}/ in {f_}")
    if 'href="../es/"' in G.piede_en("../") or "/es/" in G.piede_en(""):
        errori.append("ES/PT: il piè di pagina comune non deve cambiare (esperimento A/B)")
    riletti = []
    if online:
        sys.path.insert(0, str(SITO.parent / "raccolta"))
        import entrar_europa as RE_
        rng = random.Random(20261031)
        chiavi = rng.sample(sorted(k for k, L in E["letture"].items() if E["fonti"][L["fonte"]]["formato"] != "browser"), 10)
        testi = {}
        for k in chiavi:
            fo = E["letture"][k]["fonte"]
            if fo not in testi:
                F = E["fonti"][fo]
                st, b, _ = RE_.scarica(F["url"], "application/xhtml+xml" if "celex" in F else None, RE_.LINGUE_UE[F["lingua"]][0] if "celex" in F else None)
                testi[fo] = RE_.testo_di(b, F["formato"]) if st == 200 else ""
            ok = RE_.norm(E["letture"][k]["frammento"]) in testi[fo]
            riletti.append(f"{fo} {k}: {'presente' if ok else 'ASSENTE'}")
            if not ok:
                errori.append(f"ES/PT: frammento {k} non più in {fo}")
    return errori, len(pagine), n_js, riletti


# ---------------------------------------------------------------- 28. Visti di lunga durata per nazionalità, es/pt (4/11/2026)
def _fmt_vl(x, val, l, dec):
    """Formattazione indipendente: migliaia '.', decimali ',', interi senza ',00'; EUR '2.400 €' (es) / '€ 2.400' (pt), BRL 'R$ x', altre 'x COD'."""
    from decimal import Decimal, ROUND_HALF_UP
    d = Decimal(repr(float(x))).quantize(Decimal("1") if dec == 0 else Decimal("0.01"), rounding=ROUND_HALF_UP)
    intero, _, dc = f"{d:f}".partition(".")
    gruppi = []
    while len(intero) > 3:
        gruppi.insert(0, intero[-3:])
        intero = intero[:-3]
    t = ".".join([intero] + gruppi) + ("," + dc if dc and dc != "00" else "")
    if val == "EUR":
        return f"{t} €" if l == "es" else f"€ {t}"
    if val == "BRL":
        return f"R$ {t}"
    return f"{t} {val}"


def _numeri_fr(fr):
    """Numeri scritti in un frammento ufficiale, letti in tutti i formati usati dalle fonti (152.000 / 352,10 / 1,902 / $47,400 / 1.902,00)."""
    out = set()
    for t in re.findall(r"\d[\d.,]*\d|\d", fr):
        cand = {t.replace(".", "").replace(",", "."), t.replace(",", ""), t.replace(".", "").replace(",", "")} | set(t.split(","))   # celle CSV (Bogotá)
        for c in cand:
            try:
                out.add(round(float(c), 4))
            except ValueError:
                pass
    return out


def controlla_vl(online=True):
    errori = []
    import hashlib
    V = json.loads((SITO.parent / "dati" / "visados.json").read_text(encoding="utf-8"))
    F, L, C = V["fonti"], V["letture"], V["cambi"]
    cont = {k: V[k] for k in ("fonti", "letture", "valute", "cambi")}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != V["impronta"]:
        errori.append("VL: impronta di dati/visados.json diversa dal contenuto")
    for k, f in F.items():
        if f.get("http") != 200:
            errori.append(f"VL: fonte {k} non letta")
        if f["formato"] == "immagine" and f["sha256"] != f.get("sha256_atteso"):
            errori.append(f"VL: il PDF-immagine {k} è cambiato rispetto alla lettura a vista")
    # ogni tassa o valore numerico delle letture è scritto nel frammento ufficiale
    for k, x in L.items():
        vals = x.get("valore")
        if isinstance(vals, bool) or vals is None:
            continue
        vals = vals if isinstance(vals, list) else [vals]
        nums = _numeri_fr(x["frammento"])
        for v in vals:
            if v == 0 and "Gratuit" in x["frammento"]:
                continue
            ok = round(float(v), 4) in nums or (v <= 10 and round(v * 100, 4) in nums)   # percentuali (4.0 = 400 %, 0.75 = 75 %)
            if not ok and k == "pt_d8_4" and "quatro" in x["frammento"]:
                ok = v == 4
            if not ok and k in ("nl_un_ano",) and "un año" in x["frammento"]:
                ok = v == 1
            if not ok and k == "pt_escala":
                ok = round(v * 100, 4) in nums
            if not ok:
                errori.append(f"VL: valore {v} di {k} non scritto nel frammento ufficiale")
    # indici
    iprem, smi, rmmg = G.INDICI["es_iprem"]["valore"], G.INDICI["es_smi"]["valore"], G.INDICI["pt_rmmg"]["valore"]
    if L["nl_ba_2400"]["valore"] != [4 * iprem, 48 * iprem, iprem] or L["pt_rmmg"]["valore"] != rmmg:
        errori.append("VL: IPREM o RMMG di programmi.json diversi dalle fonti della sezione")
    # cambi ricalcolati
    tassi = {"MXN": C["bce"]["MXN"], "BRL": C["bce"]["BRL"]}
    for v, x in C["per_usd"].items():
        tassi[v] = round(C["bce"]["USD"] * x, 4)
    for v, x in tassi.items():
        if abs(C["tassi"][v] - x) > 1e-9:
            errori.append(f"VL: cambio {v} diverso dal ricalcolo")
    domanda = {s_ for v in V["domanda"]["query"].values() for s_ in (v or [])}
    sitemap = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    attese = {"es/visados/": "es", "pt/vistos/": "pt"}
    for v, n, l, p in G.pagine_vl():
        attese[p] = l
    for l, cart in (("es", "visados"), ("pt", "vistos")):
        trovate = {f"{l}/{f.parent.relative_to(SITO / l).as_posix()}/" for f in (SITO / l / cart).rglob("index.html")}
        previste = {p for p, ll in attese.items() if ll == l}
        if trovate != previste:
            errori.append(f"VL {l}: pagine diverse da quelle attese (in più {sorted(trovate - previste)}, mancanti {sorted(previste - trovate)})")
    if len(attese) < 40:
        errori.append(f"VL: solo {len(attese)} pagine")
    url_ok = {f["url"] for f in F.values()} | {x["url"] for x in C["fonti"].values()} | {G.F_CIRC_VL["url"]}
    frammenti = {html.escape(x["frammento"], quote=q) for x in L.values() for q in (False, True)} | {
        html.escape(G.SI["letture"]["mezzi"]["frammento"], quote=q) for q in (False, True)}
    # le FAQ registrate da genera.py: si rigenerano in memoria senza scrivere file (pagina() sostituita per un momento)
    orig = G.pagina
    G.pagina = lambda *a, **k: None
    try:
        G.genera_vl()
    finally:
        G.pagina = orig
    alt_di = {}
    pagine = {}
    for p, l in attese.items():
        f = SITO / p / "index.html"
        if not f.exists():
            continue
        t = f.read_text(encoding="utf-8")
        pagine[p] = t
        if f"<loc>{G.URL_SITO}/{p}</loc>" not in sitemap:
            errori.append(f"VL: {p} non in sitemap")
        if f'<html lang="{l}">' not in t:
            errori.append(f"VL: {p} senza lang={l}")
        if f'<link rel="canonical" href="{G.URL_SITO}/{p}">' not in t:
            errori.append(f"VL: {p} canonical errato")
        tit = html.unescape(re.search(r"<title>(.*?)</title>", t, re.S).group(1))
        if len(tit) > 70:
            errori.append(f"VL: titolo oltre 70 caratteri ({len(tit)}) in {p}")
        for x in ('"@type": "FAQPage"', '"@type": "BreadcrumbList"', "el consulado decide" if l == "es" else "o consulado decide"):
            if x not in t:
                errori.append(f"VL: {p} senza {x}")
        if re.search(r'rel="[^"]*sponsored', t.split('<main id="main">')[1].split("</main>")[0]):
            errori.append(f"VL: link sponsorizzato in {p} (nessun affiliato in questa sezione)")
        alt_di[p] = dict(re.findall(r'<link rel="alternate" hreflang="(\w+)" href="' + re.escape(G.URL_SITO) + r'/([^"]*)">', t))
        main = t.split('<main id="main">')[1].split("</main>")[0]
        for q in re.findall(r"<q(?: [^>]*)?>(.*?)</q>", main, re.S):
            if q not in frammenti:
                errori.append(f"VL: citazione non uguale al frammento ufficiale in {p}: {q[:60]!r}")
        for u in re.findall(r'href="(https?://[^"]+)"', main):
            if html.unescape(u) not in url_ok and not u.startswith(G.URL_SITO):
                errori.append(f"VL: link esterno non tra le fonti in {p}: {u[:80]}")
        # FAQ da ricerche vere
        for r_, q_, _a in G.FAQ_VL.get(p, []):
            if r_ not in domanda:
                errori.append(f"VL: FAQ senza ricerca vera in {p}: {r_!r}")
            if f"<h3>{html.escape(q_)}</h3>" not in main:
                errori.append(f"VL: FAQ non in pagina {p}: {q_!r}")
        if not G.FAQ_VL.get(p):
            errori.append(f"VL: {p} senza FAQ registrate")
    # hreflang: indici reciproci, dettaglio autoreferenziale, ogni alternato rimanda indietro
    for p, alts in alt_di.items():
        if p in ("es/visados/", "pt/vistos/"):
            if alts != {"es": "es/visados/", "pt": "pt/vistos/"}:
                errori.append(f"VL: hreflang dell'indice {p} non reciproci: {alts}")
        elif alts != {attese[p]: p}:
            errori.append(f"VL: hreflang di {p} non autoreferenziale: {alts}")
        for h, q in alts.items():
            if q not in alt_di or alt_di[q].get(attese[p]) != p:
                errori.append(f"VL: hreflang {p} -> {q} senza ritorno")
    # importi ricalcolati: ogni importo della prima frase deve essere tra quelli attesi per la pagina
    rx = re.compile(r"(?:€ |R\$ )\d{1,3}(?:\.\d{3})*(?:,\d+)?|\d{1,3}(?:\.\d{3})*(?:,\d+)? (?:€|COP|MXN|ARS|CLP|PEN)")
    def conv(x, val):
        return x * tassi[val]
    for v, n, l, p in G.pagine_vl():
        t = pagine.get(p)
        if not t:
            continue
        val = G.NAZ_VL[n]["val"] if n else None
        lead = re.search(r'<p class="lead">(.*?)</p>', t, re.S).group(1)
        att = set()
        def add(x, dec_eur=2):
            att.add(_fmt_vl(x, "EUR", l, dec_eur))
            if val:
                att.add(_fmt_vl(conv(x, val), val, l, 0))
        if v == "es_nl":
            m = L["nl_400"]["valore"] * iprem
            add(m); add(12 * m)
        elif v == "es_nd":
            add(L["nd_200"]["valore"] * smi)
        elif v == "es_est":
            add(L["est_100"]["valore"] * iprem)
        elif v == "pt_d7":
            add(rmmg)
        elif v == "pt_d8":
            add(L["pt_d8_4"]["valore"] * rmmg); att.add(_fmt_vl(rmmg, "EUR", l, 2))
        elif v == "pt_est":
            add(12 * rmmg)
        elif v == "pt_cplp":
            pass
        elif v == "it_est":
            add(G.SI["letture"]["mezzi"]["valore"])
        if v.startswith("pt_"):
            att.add(_fmt_vl(L["pt_110"]["valore"], "EUR", l, 2))
            att.add(_fmt_vl(rmmg, "EUR", l, 2))
        if v.startswith("es_"):
            T = G.TASAS_ES_VL[n]
            x = L[T["v"]]
            if x["valore"]:
                att.add(_fmt_vl(x["valore"], x["valuta"], l, 0 if x["valuta"] in ("ARS", "CLP", "COP") else 2))
            if F[T["f"]]["data_listino"] and G.data_ee(F[T["f"]]["data_listino"], l) not in t:
                errori.append(f"VL: data del listino mancante in {p}")
            if not x["valore"] and "gratuit" not in lead:
                errori.append(f"VL: {p}: visto gratuito non detto nella prima frase")
        if v == "it_est":
            if n in G.TASAS_IT_VL:
                x = L[G.TASAS_IT_VL[n][0]]
                att.add(_fmt_vl(x["valore"], x["valuta"], l, 0 if x["valuta"] in ("ARS", "CLP", "COP") else 2))
            else:
                att.add(_fmt_vl(50, "EUR", l, 2))
        trovati = set(rx.findall(html.unescape(re.sub(r"<[^>]+>", "", lead))))
        if not trovati and v != "pt_proc":
            errori.append(f"VL: nessun importo nella prima frase di {p}")
        for x in trovati - att:
            errori.append(f"VL: importo non ricalcolabile nella prima frase di {p}: {x!r}")
        if v != "pt_proc" and not re.search(r"(leíd[oa] el|lid[oa] em|listado del|tabela de) \d", html.unescape(lead)):
            errori.append(f"VL: prima frase senza data di lettura o del listino in {p}")
        if v != "pt_proc" and "href=" not in lead and v not in ("es_nl", "es_nd", "es_est", "pt_d7", "pt_d8", "pt_est", "pt_cplp"):
            errori.append(f"VL: prima frase senza link alla fonte in {p}")
        # tabella della famiglia ricalcolata
        tab = re.search(r'<table[^>]*\bid="t-vl-fam"[^>]*>(.*?)</table>', t, re.S)
        if v in ("es_nl", "es_nd", "es_est") and tab:
            p1, a1 = (L["nd_familia"]["valore"] if v == "es_nd" else L["est_familia"]["valore"] if v == "es_est" else (L["nl_100"]["valore"],) * 2)
            base = (L["nd_200"]["valore"] * smi if v == "es_nd" else L["est_100"]["valore"] * iprem if v == "es_est" else L["nl_400"]["valore"] * iprem)
            ind = smi if v == "es_nd" else iprem
            righe = re.findall(r'<tr><th[^>]*scope="row"[^>]*>.*?</tr>', tab.group(1), re.S)
            for i, r_ in enumerate(righe, start=1):
                m = base + (p1 * ind if i >= 2 else 0) + max(0, i - 2) * a1 * ind
                celle = [html.unescape(c) for c in re.findall(r'<td[^>]*class="n"[^>]*>(.*?)</td>', r_)]
                exp = [_fmt_vl(m, "EUR", l, 2), "≈ " + _fmt_vl(conv(m, val), val, l, 0)]
                if v != "es_nd":
                    exp += [_fmt_vl(12 * m, "EUR", l, 2), "≈ " + _fmt_vl(conv(12 * m, val), val, l, 0)]
                if celle != exp:
                    errori.append(f"VL: tabella della famiglia di {p}, riga {i}: {celle} ≠ {exp}")
        if v in ("es_nl", "es_nd", "es_est", "pt_d7") and not tab:
            errori.append(f"VL: tabella della famiglia mancante in {p}")
        if val and v != "pt_proc" and G.data_ee(C["data"], l) not in t:
            errori.append(f"VL: data del cambio mancante in {p}")
    # collegamenti dal resto del sito; il piè di pagina comune (inglese) non cambia
    for f_, pre in (("index.html", ""), ("how-it-works/index.html", "../")):
        for x in ("es/visados/", "pt/vistos/"):
            if f'href="{pre}{x}"' not in leggi(f_):
                errori.append(f"VL: manca il link a /{x} in {f_}")
    for x in ("es/index.html", "pt/index.html"):
        if "visados/" not in leggi(x) and "vistos/" not in leggi(x):
            errori.append(f"VL: manca il link alla sezione nel menu o nel piè di pagina di {x}")
    if "visados" in G.piede_en("") or "vistos" in G.piede_en(""):
        errori.append("VL: il piè di pagina comune non deve cambiare (esperimento A/B)")
    riletti = []
    if online:
        sys.path.insert(0, str(SITO.parent / "raccolta"))
        import visados as RV
        rng = random.Random(20261104)
        chiavi = rng.sample(sorted(k for k, x in L.items() if not x.get("visiva")), 8)
        testi = {}
        for k in chiavi:
            fo = L[k]["fonte"]
            if fo not in testi:
                st, b = RV.scarica(F[fo]["url"])
                testi[fo] = RV.testo_di(b, F[fo]["formato"]) if st == 200 else ""
            ok = RV.norm(L[k]["frammento"]) in testi[fo]
            riletti.append(f"{fo} {k}: {'presente' if ok else 'ASSENTE'}")
            if not ok:
                errori.append(f"VL: frammento {k} non più in {fo}")
    return errori, len(pagine), riletti


# ---------------------------------------------------------------- 29. Infermieri formati all'estero e UK Ancestry visa (5/11/2026)
def _n29(x):
    return f"{x:,}"


def _testo29(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def _righe29(main, id_tab):
    m = re.search(r'<table[^>]*id="' + id_tab + r'".*?<tbody>(.*?)</tbody>', main, re.S)
    if not m:
        return None
    return [[_testo29(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)] for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", m.group(1), re.S)]


def _hcw29(I, naz, anno):
    x = I["hcw"]["naz"].get(naz, {}).get(anno)
    if not x:
        return None
    m, d = x["M"], x["D"]
    return m[0], d[0], m[0] + d[0], m[1] + d[1]


def _pc29(r, i):
    return "–" if i + r == 0 else f"{r / (i + r) * 100:.1f}%"


def controlla_infermieri():
    import hashlib
    errori = []
    note = []
    I = json.loads((SITO.parent / "dati" / "infermieri.json").read_text(encoding="utf-8"))
    A = json.loads((SITO.parent / "dati" / "ancestry.json").read_text(encoding="utf-8"))
    R = json.loads((SITO.parent / "dati" / "rifiuti.json").read_text(encoding="utf-8"))
    for nome, D, chiavi in (("infermieri", I, ("letture", "fonti", "nmc", "irlanda", "codice", "oms", "hcw", "scartati")),
                            ("ancestry", A, ("letture", "fonti", "trimestri", "primo_trimestre_familiari", "controlli_work", "naz"))):
        cont = {k: D[k] for k in chiavi}
        if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != D["impronta"]:
            errori.append(f"29 {nome}: impronta del JSON diversa dal contenuto")
        if any(f.get("http") not in (200, None) for f in D["fonti"].values() if isinstance(f, dict)):
            errori.append(f"29 {nome}: fonte non letta (HTTP diverso da 200)")
    if I["hcw"]["fonte"]["sha256"] != R["fonti"]["uk"]["sha256"] or A["fonti"]["ho"]["sha256"] != R["fonti"]["uk"]["sha256"]:
        errori.append("29: file del Home Office diverso da quello di dati/rifiuti.json")
    L = {k: v["valore"] for k, v in I["letture"].items()}
    LA = {k: v["valore"] for k, v in A["letture"].items()}
    nmc, ie, cod = I["nmc"], I["irlanda"], I["codice"]
    date_ = nmc["date"]
    # 1. ricalcolo indipendente dai file grezzi (NMC e JQ06), se ci sono
    gr = SITO.parent / "raccolta" / "_grezzi" / "infermieri"
    f_nmc = gr / I["fonti"]["nmc_xlsx"]["file"]
    if f_nmc.exists() and hashlib.sha256(f_nmc.read_bytes()).hexdigest() == I["fonti"]["nmc_xlsx"]["sha256"]:
        import openpyxl
        wb = openpyxl.load_workbook(f_nmc, read_only=True, data_only=True)
        for foglio, campo in (("Training Country ALL", "registro"), ("Training Country Joiners", "nuovi")):
            righe = {}
            for r in wb[foglio].iter_rows(values_only=True):   # la prima occorrenza: sotto ci sono le stesse righe in percentuale
                if r[2] and r[2] != "Country of Training" and str(r[2]).strip() not in righe:
                    righe[str(r[2]).strip()] = [int(x or 0) for x in r[3:15]]
            for p in list(G.PAESI_INF) + ["Total"]:
                atteso = righe.get(p)
                v = (nmc["totale"] if campo == "registro" else nmc["totale_nuovi"]) if p == "Total" else nmc["paesi"][p][campo]
                if atteso != v:
                    errori.append(f"29 NMC: {foglio} {p} nel JSON {v} diverso dal file {atteso}")
    else:
        note.append("file NMC grezzo assente: ricalcolo dal file saltato")
    f_ie = gr / "jq06.csv"
    if f_ie.exists() and hashlib.sha256(f_ie.read_bytes()).hexdigest() == I["fonti"]["jq06_csv"]["sha256"]:
        import csv
        import io
        for r in csv.DictReader(io.StringIO(f_ie.read_bytes().decode("cp1252"))):
            c = r["QUALCOU"].strip()
            if r["TRNGTYPE"] == "FOREIGN" and c in ie["paesi"]:
                v = int(r["VALUE"]) if r["VALUE"].strip().isdigit() else None
                if ie["paesi"][c]["v"].get(r["YEAR"]) != v:
                    errori.append(f"29 JQ06: {c} {r['YEAR']} nel JSON {ie['paesi'][c]['v'].get(r['YEAR'])} diverso dal CSV {v}")
            elif r["TRNGTYPE"] == "TOTAL" and int(r["VALUE"]) != ie["totale"][r["YEAR"]]:
                errori.append(f"29 JQ06: totale {r['YEAR']} diverso dal CSV")
    else:
        note.append("CSV JQ06 grezzo assente: ricalcolo dal file saltato")
    # 2. pagine attese, sitemap, titoli, JSON-LD, avvisi, niente affiliazioni
    sez = G.SEZ_INF
    attese = [""] + [G.PAESI_INF[p][0] for p in G.PAG_INF] + ["uk", "ireland", "red-list", "nmc-registration-cost"]
    cart = SITO / sez.rstrip("/")
    trovate = {f.parent.relative_to(cart).as_posix().replace(".", "") for f in cart.rglob("index.html")}
    if trovate != set(attese):
        errori.append(f"29: pagine diverse da quelle attese (in più {sorted(trovate - set(attese))}, mancanti {sorted(set(attese) - trovate)})")
    sel = sorted([(v["registro"][-1], k) for k, v in nmc["paesi"].items() if v["area"] == "Rest of the World" and v["registro"][-1] >= 1000 and k not in ("Unknown", "Australia")], reverse=True)
    if [k for _, k in sel] != G.PAG_INF or len(G.PAG_INF) != 12:
        errori.append(f"29: Paesi con pagina {G.PAG_INF} diversi dal ricalcolo (soglia 1.000, fuori da UK e UE/SEE) {[k for _, k in sel]}")
    sitemap = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    pagine = {}
    for s in attese + ["@anc"]:
        percorso = G.PERC_ANC if s == "@anc" else f"{sez}{s + '/' if s else ''}"
        f = SITO / percorso / "index.html"
        if not f.exists():
            errori.append(f"29: manca {percorso}")
            continue
        t = f.read_text(encoding="utf-8")
        main = t.split('<main id="main">', 1)[1].split("</main>", 1)[0]
        if f"<loc>{G.URL_SITO}/{percorso}</loc>" not in sitemap:
            errori.append(f"29: {percorso} non in sitemap")
        titolo = html.unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(titolo) > 70:
            errori.append(f"29: titolo oltre 70 caratteri in {percorso} ({len(titolo)})")
        for x in ("FAQPage", "BreadcrumbList", f'<link rel="canonical" href="{G.URL_SITO}/{percorso}">'):
            if x not in t:
                errori.append(f"29: manca {x!r} in {percorso}")
        if "not advice.</strong>" not in main and "Not immigration or legal advice.</strong>" not in main:
            errori.append(f"29: avviso mancante in {percorso}")
        if re.search(r'rel="[^"]*sponsored', main) or "Affiliate" in main:
            errori.append(f"29: link di affiliazione in {percorso} (nessun riquadro previsto)")
        for x in ("C.L.25.2026", "36 countries", "£1,170"):
            if x in main:
                errori.append(f"29: {x!r} in {percorso} (lista provvisoria o totale NMC che non torna)")
        lead = _testo29(re.search(r'<p class="lead">(.*?)</p>', main, re.S).group(1))
        pagine[s] = (t, main, lead, percorso)
    d1 = G.data_lunga(date_[-1])
    agg_ie = G.data_lunga(I["fonti"]["jq06_scheda"]["aggiornata"])
    # 3. pagine Paese: prima frase, tabelle e FAQ ricalcolate
    for p in G.PAG_INF:
        slug, X, agg, iso, naz = G.PAESI_INF[p]
        if slug not in pagine:
            continue
        t, main, lead, perc = pagine[slug]
        v = nmc["paesi"][p]
        ie1 = ie["paesi"][iso]["v"].get(ie["anni"][-1])
        attesi_lead = [f"{_n29(v['registro'][-1])} people on the UK's nursing and midwifery register trained in {X} on {d1}", "NMC register data", f"JQ06, updated {agg_ie}",
                       f"{_n29(v['nuovi'][-1])} nurses, midwives or nursing associates trained in {X} joined"]
        attesi_lead.append(f"{_n29(ie1)} nurses and midwives practising in Ireland at the end of {ie['anni'][-1]}" if ie1 is not None else "under 25")
        for x in attesi_lead:
            if x not in lead:
                errori.append(f"29 {slug}: prima frase senza {x!r}")
        if lead.index("NMC") > 400:
            errori.append(f"29 {slug}: fonte troppo lontana dall'inizio della prima frase")
        reg = _righe29(main, "t-reg-inf")
        att = [[G.data_lunga(date_[i]), _n29(v["registro"][i])] for i in sorted(set([i for i, d in enumerate(date_) if d.endswith("03-31")][-4:] + [len(date_) - 2]))]
        if reg != att:
            errori.append(f"29 {slug}: tabella del registro {reg} diversa dal ricalcolo {att}")
        nu = _righe29(main, "t-nuovi-inf")
        if nu != [[f"6 months to {G.data_lunga(date_[i])}", _n29(v["nuovi"][i])] for i in range(len(date_) - 4, len(date_))]:
            errori.append(f"29 {slug}: tabella dei nuovi iscritti diversa dal ricalcolo")
        ir = _righe29(main, "t-ie-inf")
        if ir != [[f"End of {a}", _n29(ie["paesi"][iso]["v"][a]) if ie["paesi"][iso]["v"].get(a) is not None else "under 25",
                   _n29(ie["totale"][a] - ie["irlanda"][a] - ie["sconosciuto"][a])] for a in ie["anni"]]:
            errori.append(f"29 {slug}: tabella dell'Irlanda diversa dal ricalcolo")
        hr = _righe29(main, "t-hcw-inf")
        att_h = []
        for a in sorted({a for x in I["hcw"]["naz"].values() for a in x}):
            h = _hcw29(I, naz, a)
            att_h.append(None if not h else [_n29(h[0]), _n29(h[1]), _n29(h[2]), _n29(h[3]), _pc29(h[3], h[2])])
        if hr is None or [r[1:] if len(r) == 6 else None for r in hr] != att_h:
            errori.append(f"29 {slug}: tabella dei visti Health and Care Worker diversa dal ricalcolo")
        grado = "red" if p in cod["rosso"] else "amber" if p in cod["ambra"] else "green"
        frase = {"red": "is on the red list", "amber": "is on the amber list", "green": "not on the red"}[grado]
        if frase not in _testo29(main):
            errori.append(f"29 {slug}: grado del codice ({grado}) non scritto")
        oms = (cod["nomi_oms"].get(p, p) in I["oms"]["lista_2023"])
        if (f"{X} is on the WHO health workforce support and safeguards list 2023".lower() in _testo29(main).lower()) != oms:
            errori.append(f"29 {slug}: appartenenza alla lista OMS 2023 sbagliata")
        if not re.search(r"<title>Nurses trained in ", t):
            errori.append(f"29 {slug}: il titolo non dice 'Nurses trained in' (i dati sono per Paese di formazione)")
        if I["letture"]["codice_residenza"]["frammento"] not in html.unescape(main):
            errori.append(f"29 {slug}: manca la frase del codice sul Paese di residenza")
        if "Kenya" == p and oms:
            errori.append("29: il Kenya risulta nella lista OMS 2023")
    # 4. indice, Regno Unito, Irlanda
    if "" in pagine:
        _, main, lead, _ = pagine[""]
        intl, tot = nmc["subtotali"]["International sub-total"][-1], nmc["totale"][-1]
        for x in (f"{_n29(intl)} of the {_n29(tot)} people on the UK's NMC register ({intl / tot * 100:.1f}%) trained outside the UK", "NMC register data", "JQ06",
                  f"{_n29(ie['totale'][ie['anni'][-1]] - ie['irlanda'][ie['anni'][-1]] - ie['sconosciuto'][ie['anni'][-1]])} of {_n29(ie['totale'][ie['anni'][-1]])} practising nurses"):
            if x not in lead:
                errori.append(f"29 indice: prima frase senza {x!r}")
        righe = _righe29(main, "t-inf")
        if not righe or [r[0] for r in righe] != G.PAG_INF:
            errori.append("29 indice: righe della tabella diverse dai Paesi con pagina")
        else:
            for r in righe:
                p = r[0]
                v = nmc["paesi"][p]
                h = _hcw29(I, G.PAESI_INF[p][4], G.HCW_A1)
                ie1 = ie["paesi"][G.PAESI_INF[p][3]]["v"].get(ie["anni"][-1])
                att = [_n29(v["registro"][-1]), _n29(v["registro"][-3]), _n29(v["nuovi"][-1]), _n29(v["nuovi"][-3]), _n29(ie1) if ie1 is not None else "under 25", _n29(h[2])]
                if r[1:7] != att:
                    errori.append(f"29 indice: riga {p} {r[1:7]} diversa dal ricalcolo {att}")
    if "uk" in pagine:
        _, main, lead, _ = pagine["uk"]
        top = sorted(((v["registro"][-1], k) for k, v in nmc["paesi"].items() if v["area"] != "UK" and k != "Unknown"), reverse=True)[:10]
        righe = _righe29(main, "t-top-inf")
        if not righe or [[r[0], r[2], r[3], r[4]] for r in righe] != [[k, _n29(x), _n29(nmc["paesi"][k]["registro"][-3]), _n29(nmc["paesi"][k]["nuovi"][-1])] for x, k in top]:
            errori.append("29 uk: tabella dei 10 Paesi diversa dal ricalcolo")
        serie = _righe29(main, "t-serie-inf")
        if serie != [[f"6 months to {G.data_lunga(date_[i])}", _n29(nmc["subtotali_nuovi"]["International sub-total"][i]), _n29(nmc["totale_nuovi"][i])] for i in range(len(date_) - 4, len(date_))]:
            errori.append("29 uk: serie dei nuovi iscritti (ultimi 4 semestri) diversa dal ricalcolo")
        si = nmc["subtotali_nuovi"]["International sub-total"]
        if f"The highest figure in the NMC series was {_n29(max(si))}" not in _testo29(main) or f"including {_n29(nmc['paesi']['Unknown']['registro'][-1])} with unknown training country" not in lead:
            errori.append("29 uk: picco della serie o nota sugli 'Unknown' mancanti")
    if "ireland" in pagine:
        _, main, lead, _ = pagine["ireland"]
        a1, a0 = ie["anni"][-1], ie["anni"][-2]
        pubb = [c for _, c in sorted(((v["v"][a1], c) for c, v in ie["paesi"].items() if v["v"].get(a1)), reverse=True)]
        sopp = sorted((c for c, v in ie["paesi"].items() if v["v"].get(a1) is None), key=lambda c: ie["paesi"][c]["nome"])
        righe = _righe29(main, "t-ie-paesi")
        cel = lambda x: _n29(x) if x is not None else "under 25"  # noqa: E731
        if not righe or [r[:3] for r in righe] != [[ie["paesi"][c]["nome"], cel(ie["paesi"][c]["v"].get(a1)), cel(ie["paesi"][c]["v"].get(a0))] for c in pubb + sopp]:
            errori.append("29 ireland: tabella dei Paesi diversa dal ricalcolo (valori > 0, poi 'under 25', nessuno zero)")
        if any(r[1] == "0" for r in righe or []):
            errori.append("29 ireland: Paesi con 0 in tabella")
        if "CC BY 4.0" not in main or "creativecommons.org/licenses/by/4.0" not in main:
            errori.append("29 ireland: licenza CC BY 4.0 non citata")
    # 5. lista rossa
    if "red-list" in pagine:
        _, main, lead, _ = pagine["red-list"]
        righe = _righe29(main, "t-rossa")
        att = []
        for p in cod["rosso"] + cod["ambra"]:
            h = _hcw29(I, cod["nomi_ho"].get(p, p), G.HCW_A1)
            att.append([p, "red" if p in cod["rosso"] else "amber", "yes" if cod["nomi_oms"].get(p, p) in I["oms"]["lista_2023"] else "no"] + ([_n29(h[2]), _n29(h[3])] if h else ["–", "–"]))
        if righe != att:
            errori.append("29 red-list: tabella dei Paesi rossi e ambra diversa dal ricalcolo")
        if I["letture"]["codice_residenza"]["frammento"] not in html.unescape(main) or "employers in England" not in lead:
            errori.append("29 red-list: frase sul Paese di residenza o 'employers in England' mancanti")
        if len(cod["rosso"]) != 54 or cod["ambra"] != ["Kenya", "Nepal"] or len(I["oms"]["lista_2023"]) != 55 or "Nepal" not in I["oms"]["lista_2023"]:
            errori.append("29 red-list: liste del codice o dell'OMS cambiate")
        for x in ("not published the final 2026 list", "WHO health workforce support and safeguards list 2023", f"{L['oms_2023_55']} countries",
                  G.data_lunga(I["fonti"]["codice"]["aggiornata"])):
            if x not in lead:
                errori.append(f"29 red-list: prima frase senza {x!r}")
        if I["oms"]["lista_2026"] != "non pubblicata":
            errori.append("29 red-list: la lista OMS 2026 risulta pubblicata: riscrivere la pagina")
    # 6. costi NMC
    if "nmc-registration-cost" in pagine:
        _, main, lead, _ = pagine["nmc-registration-cost"]
        voci = [L["costo_valutazione"], L["costo_cbt"], L["costo_osce"], L["costo_iscrizione"]]
        if sum(voci) != L["costo_totale"]:
            errori.append("29 costi: le voci non sommano al totale")
        righe = _righe29(main, "t-costi-inf")
        if not righe or [r[1] for r in righe] != [f"£{x:,}" for x in voci + [sum(voci)]]:
            errori.append("29 costi: tabella dei costi diversa dalle letture")
        if f"£{L['costo_totale']:,} in fees and tests" not in lead or "NMC" not in lead or "1 October 2026" not in lead:
            errori.append("29 costi: prima frase senza totale, fonte o data")
        C = G.CAMBI["tassi"]
        val = _righe29(main, "t-valute-inf")
        att = []
        for v in ("INR", "PHP", "ZAR", "USD", "EUR"):
            k = (1 if v == "EUR" else C[v]) / C["GBP"]
            att.append([f"≈ {round(x * k):,}" for x in (L["costo_totale"], L["costo_cbt"], L["costo_osce"])])
        if not val or [r[1:] for r in val] != att:
            errori.append("29 costi: conversioni diverse dal ricalcolo con i cambi BCE")
    # 7. UK Ancestry
    if "@anc" in pagine:
        _, main, lead, _ = pagine["@anc"]
        trim = A["trimestri"]
        a1 = str(int(trim[-1][:4]) - 1) if not trim[-1].endswith("Q4") else trim[-1][:4]

        def tot(n, a):
            x = A["naz"].get(n, {}).get(a)
            return [0] * 4 if not x else [x["M"][i] + x["D"][i] for i in range(4)]
        T = [sum(tot(n, a1)[i] for n in A["naz"]) for i in range(4)]
        for x in (f"In {a1} the Home Office issued {_n29(T[0])} UK Ancestry visas and refused {_n29(T[1])} ({_pc29(T[1], T[0])} of decisions)",
                  f"South Africa ({_n29(tot('South Africa', a1)[0])} issued, {_n29(tot('South Africa', a1)[1])} refused)", "published " + A["fonti"]["ho"]["pubblicato"]):
            if x not in lead:
                errori.append(f"29 ancestry: prima frase senza {x!r}")
        righe = _righe29(main, "t-anc")
        naz = sorted([n for n in A["naz"] if sum(tot(n, a1)) > 0], key=lambda n: (-tot(n, a1)[0], n))
        att = [[n, _n29(tot(n, a1)[0]), _n29(tot(n, a1)[1]), _pc29(tot(n, a1)[1], tot(n, a1)[0])] for n in naz]
        if not righe or [[r[0], r[3], r[4], r[6]] for r in righe[:-1]] != att:
            errori.append("29 ancestry: tabella per nazionalità diversa dal ricalcolo")
        anni = _righe29(main, "t-anc-anni")
        anni_att = sorted({a for v in A["naz"].values() for a in v})
        mp = lambda n, a: A["naz"].get(n, {}).get(a, {"M": [0] * 4})["M"]  # noqa: E731
        att_a = [[_n29(sum(mp(n, a)[0] for n in A["naz"])), _n29(sum(mp(n, a)[1] for n in A["naz"])),
                  _n29(sum(A["naz"][n][a]["D"][0] for n in A["naz"] if a in A["naz"][n])) if a >= "2020" else "–"] for a in anni_att]
        if not anni or [[r[1], r[2], r[6]] for r in anni] != att_a:
            errori.append("29 ancestry: tabella anno per anno (principali, familiari dal 2020) diversa dal ricalcolo")
        if A["primo_trimestre_familiari"] != "2020 Q3" or any(sum(x["D"]) for v in A["naz"].values() for a, x in v.items() if a < "2020"):
            errori.append("29 ancestry: familiari prima del 2020 Q3 (le serie lunghe devono usare i soli principali)")
        if "The counts include family members" in lead or "family members, whom the file counts only from 2020 Q3" not in lead:
            errori.append("29 ancestry: prima frase senza la nota sui familiari dal 2020 Q3")
        if main.count("appear in the Home Office file only from 2020 Q3") < 3:
            errori.append("29 ancestry: nota sui familiari mancante sotto le tre tabelle")
        if anni_att[0] != "2005" or len(anni_att) < 20:
            errori.append("29 ancestry: anni disponibili inattesi")
        if f"£{LA['tassa']}" not in main or "grandparents" not in main:
            errori.append("29 ancestry: tassa o regola del nonno mancanti")
    # 8. citazioni = frammenti ufficiali; FAQ da ricerche vere (le FAQ si registrano rigenerando le pagine senza scriverle)
    orig = G.pagina
    G.pagina = lambda *a, **k: None
    try:
        G.genera_inf()
        G.pagina_anc()
    finally:
        G.pagina = orig
    frammenti = [v["frammento"] for v in I["letture"].values()] + [v["frammento"] for v in A["letture"].values()]
    for s, (t, main, lead, perc) in pagine.items():
        for q in re.findall(r"“([^”]+)”", html.unescape(main)):
            q = q.rstrip(".").strip()
            if not any(q in f for f in frammenti):
                errori.append(f"29 {perc}: citazione non presente nei frammenti ufficiali: {q[:80]!r}")
        faq = G.FAQ_ANC if s == "@anc" else G.FAQ_INF.get(perc, [])
        h3 = re.findall(r"<h3>(.*?)</h3>", main.split("Questions people ask", 1)[-1])
        if not faq or [html.unescape(x) for x in h3] != [d for _, _, d in faq]:
            errori.append(f"29 {perc}: domande della FAQ diverse da quelle legate a ricerche dell'autocompletamento")
        dom = (A if s == "@anc" else I)["domanda"]["query"]
        for k, sug, d in faq:
            if sug not in (dom.get(k) or []):
                errori.append(f"29 {perc}: la domanda {d!r} non viene da una ricerca salvata ({k} -> {sug!r})")
    # 9. collegamenti dal resto del sito; piè di pagina comune invariato
    for f, x in (("index.html", f'href="{sez}"'), ("index.html", f'href="{G.PERC_ANC}"'), ("how-it-works/index.html", f'href="../{sez}"'),
                 ("visa-refusal-rates/uk/index.html", f'href="../../{G.PERC_ANC}"'), ("visa-refusal-rates/uk/index.html", f'href="../../{sez}"')):
        if x not in leggi(f):
            errori.append(f"29: manca il link {x} in {f}")
    if "nurses-abroad" in G.piede_en("") or "ancestry" in G.piede_en(""):
        errori.append("29: il piè di pagina comune è cambiato (vincolo dell'esperimento A/B)")
    return errori, len(pagine), note


def _norm30(t):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)).replace("\xa0", " ")).strip()


def _testo_html30(b):
    t = b.decode("utf-8", "replace") if isinstance(b, bytes) else b
    return _norm30(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)))


def _hpi30(body):
    """Lettore proprio delle tabelle GOV.UK: righe (università, Paese) con HTMLParser."""
    class P(HTMLParser):
        def __init__(self):
            super().__init__()
            self.righe, self.cella, self.riga, self.in_td, self.in_body = [], [], None, False, False

        def handle_starttag(self, tag, a):
            if tag == "tbody":
                self.in_body = True
            elif tag == "tr" and self.in_body:
                self.riga = []
            elif tag == "td" and self.riga is not None:
                self.in_td, self.cella = True, []

        def handle_endtag(self, tag):
            if tag == "td" and self.in_td:
                self.riga.append(re.sub(r"\s+", " ", "".join(self.cella)).strip())
                self.in_td = False
            elif tag == "tr" and self.riga is not None:
                self.righe.append(tuple(self.riga))
                self.riga = None

        def handle_data(self, d):
            if self.in_td:
                self.cella.append(d)
    p = P()
    p.feed(body)
    return p.righe


def controlla_tu():
    import hashlib
    errori = []
    note = []
    T = json.loads((SITO.parent / "dati" / "top_university.json").read_text(encoding="utf-8"))
    cont = {k: T[k] for k in ("letture", "fonti", "liste", "universita")}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != T["impronta"]:
        errori.append("30: impronta del JSON diversa dal contenuto")
    for k, f in T["fonti"].items():
        if f.get("http") != 200 or not re.fullmatch(r"[0-9a-f]{64}", f.get("sha256_file", "")) or f.get("letto_il") != T["letto_il"]:
            errori.append(f"30: fonte {k} senza HTTP 200, impronta o data di lettura")
    L, U = T["liste"], T["universita"]
    LT = {k: v["valore"] for k, v in T["letture"].items()}
    anni = sorted(int(k[4:]) for k in L if k.startswith("hpi-"))
    if anni != list(range(2021, 2027)) or set(L) != {f"hpi-{a}" for a in anni} | {"ttps", "j-find"}:
        errori.append(f"30: liste inattese {sorted(L)}")
    # 1. ricalcolo indipendente dai file grezzi, se ci sono (stessa impronta)
    gr = SITO.parent / "raccolta" / "_grezzi" / "top_university"
    grezzi_ok = 0
    for a in anni:
        f = gr / f"hpi-{a}.json"
        if f.exists() and hashlib.sha256(f.read_bytes()).hexdigest() == T["fonti"][f"hpi-{a}"]["sha256_file"]:
            grezzi_ok += 1
            body = json.loads(f.read_bytes())["details"]["body"]
            righe = [(html.unescape(x), html.unescape(c)) for x, c in _hpi30(body)]
            if righe != [(x["nome"], x["paese_lista"]) for x in L[f"hpi-{a}"]["voci"]]:
                errori.append(f"30 HPI {a}: righe del JSON diverse dalla tabella GOV.UK")
            if f"between 1 November {a} " not in _testo_html30(body) or f"31 October {a + 1}" not in _testo_html30(body):
                errori.append(f"30 HPI {a}: periodo dei titoli non trovato nella pagina")
    f = gr / "aggregate_list.pdf"
    if f.exists() and hashlib.sha256(f.read_bytes()).hexdigest() == T["fonti"]["ttps_pdf"]["sha256_file"]:
        grezzi_ok += 1
        t = subprocess.run(["pdftotext", "-raw", str(f), "-"], capture_output=True, text=True).stdout
        paesi_cn = ("阿根廷|澳洲|奧地利|比利時|巴西|加拿大|智利|中國內地|丹麥|芬蘭|法國|德國|香港|愛爾蘭|以色列|意大利|日本|馬來西亞|墨西哥|荷蘭|紐西蘭|挪威|俄羅斯|沙特阿拉伯|"
                    "新加坡|韓國|西班牙|瑞典|瑞士|台灣|英國|美國")
        righe = [r for r in t.split("\n") if re.search(r"(?:" + paesi_cn + r")\s*$", r) and not re.search(r"國家|Country", r)]
        if len(righe) != len(L["ttps"]["voci"]):
            errori.append(f"30 TTPS: {len(righe)} righe con il Paese nel PDF (lettura -raw), {len(L['ttps']['voci'])} nel JSON")
        for x, r in zip(L["ttps"]["voci"], righe):
            if not r.startswith(x["nome_lista"].split(" / ")[0]):
                errori.append(f"30 TTPS: riga {r[:60]!r} diversa da {x['nome_lista'][:60]!r}")
                break
        if sum(1 for x in L["ttps"]["voci"] if x["nuova"]) != t.count("*") - 2:   # due asterischi nella nota in cinese e in inglese
            errori.append("30 TTPS: numero di università nuove (*) diverso dal PDF")
    f = gr / "jfind.pdf"
    if f.exists() and hashlib.sha256(f.read_bytes()).hexdigest() == T["fonti"]["jf_pdf"]["sha256_file"]:
        grezzi_ok += 1
        t = re.sub(r"\s+", "", subprocess.run(["pdftotext", "-raw", str(f), "-"], capture_output=True, text=True).stdout)
        for x in L["j-find"]["voci"]:
            if re.sub(r"\s+", "", x["nome_ja"]) not in t:
                errori.append(f"30 J-Find: nome giapponese {x['nome_ja']!r} non trovato nel PDF")
        if len({x["nome_ja"] for x in L["j-find"]["voci"]}) != len(L["j-find"]["voci"]):
            errori.append("30 J-Find: nomi giapponesi doppi")
    for k, f_ in (("hpi_guida", "hpi-guida.json"), ("ttps_pagina", "ttps_pagina.html"), ("ttps_tariffe", "ttps_tariffe.html"), ("jf_pagina", "jfind.html")):
        f = gr / f_
        if f.exists() and hashlib.sha256(f.read_bytes()).hexdigest() == T["fonti"][k]["sha256_file"]:
            grezzi_ok += 1
            b = f.read_bytes()
            testo = (" ".join(f'{x["title"]}. {_testo_html30(x["body"])}' for x in json.loads(b)["details"]["parts"]) if f_.endswith(".json") else _testo_html30(b))
            for c, v in T["letture"].items():
                if v["fonte"] == k and v["frammento"] not in testo:
                    errori.append(f"30: frammento {c} non trovato nel file grezzo {f_}")
    if grezzi_ok < 12:
        note.append(f"file grezzi presenti e uguali all'impronta: {grezzi_ok} su 12 (ricalcolo parziale)")
    # ogni valore numerico delle letture è scritto nel frammento
    for c, v in T["letture"].items():
        x = v["valore"]
        if isinstance(x, int) and not isinstance(x, bool) and x > 9:
            forme = {str(x), f"{x:,}", f"{x / 1e6:g} million", f"{x:,}".replace(",", "")}
            if c.startswith("jf_") and x == 200000:
                forme |= {"２０万円", "200,000 yen"}
            if not any(fm in v["frammento"] for fm in forme):
                errori.append(f"30: valore {x} di {c} non scritto nel frammento")
    # 2. università: ogni riga ha la sua università e viceversa; Paesi; India e Nigeria assenti
    ids = {x["id"] for l in L.values() for x in l["voci"]}
    if ids != set(U):
        errori.append(f"30: università del JSON diverse dalle righe delle liste ({len(ids)} contro {len(U)})")
    for i, u in U.items():
        attese = {k: x["nome"] for k, l in L.items() for x in l["voci"] if x["id"] == i}
        if u["liste"] != attese:
            errori.append(f"30: {i}: liste {sorted(u['liste'])} diverse da {sorted(attese)}")
    if any(u["paese"] in ("India", "Nigeria") for u in U.values()):
        errori.append("30: università in India o Nigeria: le pagine dei Paesi senza università non valgono più")
    if L["hpi-2026"]["dal"] != "2026-11-01" or L["hpi-2026"]["al"] != "2027-10-31":
        errori.append("30: la lista HPI 2026 non è per i titoli dal 1/11/2026 al 31/10/2027")
    # 3. pagine attese, sitemap, titoli, JSON-LD, avviso, niente affiliazioni
    sez = G.SEZ_TU
    paesi = sorted({u["paese"] for u in U.values()}) + ["India", "Nigeria"]
    # pagine università solo per gli anni HPI misti e le britanniche presenti a Hong Kong e in Giappone (decisione sul contenuto sottile, 5/11/2026)
    con_pag = {i for i, u in U.items() if 0 < sum(f"hpi-{a}" in u["liste"] for a in anni) < len(anni)
               or (u["paese"] == "United Kingdom" and "ttps" in u["liste"] and "j-find" in u["liste"])}
    if con_pag != set(G.PAG_UNI_TU) or len(con_pag) != 39:
        errori.append(f"30: università con pagina {len(G.PAG_UNI_TU)} diverse dal ricalcolo ({len(con_pag)}, attese 28 + 11)")
    attese = {""} | {f"hpi-{a}" for a in anni} | {"ttps", "j-find"} | {f"universities/{i}" for i in con_pag} | {f"countries/{G.slug_testo(p)}" for p in paesi}
    cart = SITO / sez.rstrip("/")
    trovate = {f.parent.relative_to(cart).as_posix().replace(".", "") for f in cart.rglob("index.html")}
    if trovate != attese:
        errori.append(f"30: pagine diverse da quelle attese (in più {sorted(trovate - attese)[:5]}, mancanti {sorted(attese - trovate)[:5]})")
    sitemap = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    letto = G.data_lunga(T["letto_il"])
    pagine = {}
    for s in sorted(attese & trovate):
        percorso = f"{sez}{s + '/' if s else ''}"
        t = (SITO / percorso / "index.html").read_text(encoding="utf-8")
        main = t.split('<main id="main">', 1)[1].split("</main>", 1)[0]
        if f"<loc>{G.URL_SITO}/{percorso}</loc>" not in sitemap:
            errori.append(f"30: {percorso} non in sitemap")
        titolo = html.unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(titolo) > 70 or not re.search(r"\b20\d\d\b", titolo):
            errori.append(f"30: titolo oltre 70 caratteri o senza anno in {percorso} ({titolo!r})")
        for x in ("FAQPage", "BreadcrumbList", f'<link rel="canonical" href="{G.URL_SITO}/{percorso}">', "Not immigration or legal advice.</strong>"):
            if x not in t:
                errori.append(f"30: manca {x!r} in {percorso}")
        if re.search(r'rel="[^"]*sponsored', main) or "Affiliate" in main or "wise.com" in main:
            errori.append(f"30: link di affiliazione in {percorso} (nessun riquadro previsto: Wise non ha un link attivo)")
        for x in ("in force from 1 january 2026", "updated 21 october 2024", "graduated from a university ranked in the”", "possession of 200,000 yen for living”"):
            if x in html.unescape(main).lower():
                errori.append(f"30: frase corretta dalla revisione ancora presente ({x!r}) in {percorso}")
        for x in ("guarantee", "you will get", "you qualify", "you are eligible"):
            if x in main.lower():
                errori.append(f"30: promessa ({x!r}) in {percorso}")
        lead = _testo29(re.search(r'<p class="lead">(.*?)</p>', main, re.S).group(1))
        if f"read on {letto}" not in lead or not any(x in lead for x in ("GOV.UK", "Immigration")):
            errori.append(f"30: prima frase senza fonte o data di lettura in {percorso}")
        pagine[s] = (t, main, lead, percorso, titolo)
    # 4. pagine delle università: risposta nella prima frase e tabella ricalcolate
    ordine = [f"hpi-{a}" for a in reversed(anni)] + ["ttps", "j-find"]
    for i, u in U.items():
        s = f"universities/{i}"
        if s not in pagine:
            continue
        t, main, lead, perc, titolo = pagine[s]
        correnti = [k for k in ("hpi-2026", "ttps", "j-find") if k in u["liste"]]
        brevi = {"hpi-2026": "the UK's HPI list 2026", "ttps": "Hong Kong's TTPS list", "j-find": "Japan's J-Find list"}
        testa = {3: "On all three lists:", 2: "On two of the three lists:", 1: f"Only on {brevi[correnti[0]] if correnti else ''}:", 0: "On none of the current lists:"}[len(correnti)]
        na = ("the " + u["nome"]) if u["nome"].startswith("University of ") else u["nome"]
        if not lead.startswith(f"{testa} {na} ({u['paese']}) is ") or lead.startswith("Yes"):
            errori.append(f"30 {i}: la prima frase non comincia con la risposta attesa ({testa!r})")
        if lead.count("but not") > 0:
            errori.append(f"30 {i}: 'but not' nella prima frase")
        su = {"hpi-2026": "High Potential Individual (HPI) list 2026", "ttps": "Top Talent Pass Scheme (TTPS) list of December 2025", "j-find": "J-Find list of October 2026"}
        for k, frase in su.items():
            if (k in u["liste"]) != (frase in lead):
                errori.append(f"30 {i}: prima frase sbagliata per {k}")
        vecchi = [a for a in anni if f"hpi-{a}" in u["liste"] and a != 2026]
        if vecchi and len(vecchi) + ("hpi-2026" in u["liste"]) < len(anni) and f"It was on the HPI list" not in lead:
            errori.append(f"30 {i}: manca la frase sulla storia HPI")
        righe = _righe29(main, "t-uni-tu")
        att = []
        for k in ordine:
            if k.startswith("hpi-"):
                va = f"qualifications awarded from {G.data_lunga(L[k]['dal'])} to {G.data_lunga(L[k]['al'])}"
                nl = f"HPI list {k[4:]}"
            else:
                va = "list of December 2025" if k == "ttps" else "as of October 2026"
                nl = "TTPS list" if k == "ttps" else "J-Find list"
            att.append([nl, va, "Yes" if k in u["liste"] else "No", u["liste"].get(k, "–")])
        if righe != att:
            errori.append(f"30 {i}: tabella delle liste diversa dal ricalcolo")
        if u["paese"] == "United Kingdom" and "UK universities are not eligible." not in main:
            errori.append(f"30 {i}: manca la regola delle università britanniche")
    # 5. pagine delle liste: righe = liste ufficiali, nell'ordine
    for k, id_tab in [(f"hpi-{a}", "t-hpi") for a in anni] + [("ttps", "t-ttps"), ("j-find", "t-jf")]:
        if k not in pagine:
            continue
        t, main, lead, perc, titolo = pagine[k]
        righe = _righe29(main, id_tab)
        voci = L[k]["voci"]
        if righe is None or len(righe) != len(voci):
            errori.append(f"30 {k}: {len(righe or [])} righe in tabella, {len(voci)} nella lista")
            continue
        for r, x in zip(righe, voci):
            nome = x["nome"] + (" *" if x.get("nuova") else "")
            att_r = [nome, x["nome_ja"], x["paese"]] if k == "j-find" else [nome, x["paese_lista"]]
            if r[:len(att_r)] != att_r:
                errori.append(f"30 {k}: riga {r[:3]} diversa dalla lista {att_r}")
                break
        if f"<strong>{len(voci)}</strong>" not in main or str(len(voci)) not in titolo:
            errori.append(f"30 {k}: numero di università assente dalla prima frase o dal titolo")
        if k.startswith("hpi-"):
            a = int(k[4:])
            if f"{G.data_lunga(L[k]['dal'])} to {G.data_lunga(L[k]['al'])}" not in lead:
                errori.append(f"30 {k}: periodo dei titoli assente dalla prima frase")
            if f"hpi-{a - 1}" in L:
                prima = {x["id"] for x in L[f"hpi-{a - 1}"]["voci"]}
                ora = {x["id"] for x in voci}
                if f"{len(ora - prima)} added:" not in _testo29(main) or f"{len(prima - ora)} not on the {a} list:" not in _testo29(main):
                    errori.append(f"30 {k}: università entrate e uscite diverse dal ricalcolo")
    # 6. indice e Paesi: conteggi e confronto dei visti
    if "" in pagine:
        t, main, lead, perc, titolo = pagine[""]
        tre = sum(1 for u in U.values() if all(k in u["liste"] for k in ("hpi-2026", "ttps", "j-find")))
        for x in (f"{len(U)} universities", f"{len(L['hpi-2026']['voci'])} on the UK's", f"{len(L['ttps']['voci'])} on Hong Kong's", f"{len(L['j-find']['voci'])} on Japan's", f"{tre} are on all three"):
            if x not in lead:
                errori.append(f"30 indice: prima frase senza {x!r}")
        if len(_righe29(main, "t-tu") or []) != len(U):
            errori.append("30 indice: la tabella delle università non ha tutte le università")
        linkate = set(re.findall(r'href="universities/([^/"]+)/"', re.search(r'<table class="ord" id="t-tu".*?</table>', main, re.S).group(0)))
        if linkate != con_pag:
            errori.append(f"30 indice: link alle pagine università diversi dalle pagine generate ({len(linkate)} contro {len(con_pag)})")
        h26 = {x["id"] for x in L["hpi-2026"]["voci"]}
        jf = {x["id"] for x in L["j-find"]["voci"]}
        if h26 <= jf and {U[i]["paese"] for i in jf - h26} == {"United Kingdom"}:
            if f"Every university on the HPI list 2026 ({len(h26)}) is also on the J-Find list; the other {len(jf - h26)} J-Find universities are all in the United Kingdom" not in _testo29(main):
                errori.append("30 indice: frase sul confronto HPI 2026 / J-Find assente o con numeri diversi")
        elif "is also on the J-Find list; the other" in main:
            errori.append("30 indice: frase sul confronto HPI 2026 / J-Find non più vera")
        conf = _testo29(re.search(r'<table id="t-confronto".*?</table>', main, re.S).group(0))
        for x in (f"£{LT['hpi_tassa']}", f"£{LT['hpi_ihs']:,}", f"£{LT['hpi_ecctis']}", f"£{LT['hpi_fondi']:,}", f"HK${LT['ttps_tassa_domanda']}", f"HK${LT['ttps_tassa_visto']:,}",
                  f"¥{LT['jf_fondi']:,}", "36 months", "24 months", f"May be granted a stay of up to {LT['jf_durata']} years", "does not list a fee",
                  "Category B: no limit on the year of the degree, but at least three years of work experience in the past five"):
            if x not in conf:
                errori.append(f"30 indice: confronto senza {x!r}")
    for p in paesi:
        s = f"countries/{G.slug_testo(p)}"
        if s not in pagine:
            continue
        t, main, lead, perc, titolo = pagine[s]
        ids_p = [i for i, u in U.items() if u["paese"] == p]
        if ids_p:
            h = sum(1 for i in ids_p if "hpi-2026" in U[i]["liste"])
            tt = sum(1 for i in ids_p if "ttps" in U[i]["liste"])
            j = sum(1 for i in ids_p if "j-find" in U[i]["liste"])
            if not re.search(rf"^{len(ids_p)} universit(y|ies) in ", lead) or f"{h} on the UK's HPI list" not in lead or f"{tt} on Hong Kong's" not in lead or f"{j} on Japan's" not in lead:
                errori.append(f"30 {s}: conteggi della prima frase diversi dal ricalcolo")
            if len(_righe29(main, "t-tu") or []) != len(ids_p):
                errori.append(f"30 {s}: righe della tabella diverse dalle università del Paese")
        elif not lead.startswith(f"No university in {p} is on any of the three official lists"):
            errori.append(f"30 {s}: la prima frase non dice che non ci sono università")
    # 7. citazioni = frammenti ufficiali (o frase della lista HPI); FAQ da ricerche vere
    orig = G.pagina
    G.pagina = lambda *a, **k: None
    try:
        G.FAQ_TU.clear()
        G.genera_tu()
    finally:
        G.pagina = orig
    frammenti = [v["frammento"] for v in T["letture"].values()] + [l["frase"] for l in L.values() if "frase" in l]
    dom = T["domanda"]["query"]
    for s, (t, main, lead, perc, titolo) in pagine.items():
        for q in re.findall(r"“([^”]+)”", html.unescape(main)):
            q = q.rstrip(".").strip()
            if not any(q in f for f in frammenti):
                errori.append(f"30 {perc}: citazione non presente nei frammenti ufficiali: {q[:80]!r}")
        faq = G.FAQ_TU.get(perc, [])
        h3 = re.findall(r"<h3>(.*?)</h3>", main.split("Questions people ask", 1)[-1])
        if not faq or [html.unescape(x) for x in h3] != [d for _, _, d in faq]:
            errori.append(f"30 {perc}: domande della FAQ diverse da quelle legate a ricerche dell'autocompletamento")
        for k, sug, d in faq:
            if sug not in (dom.get(k) or []):
                errori.append(f"30 {perc}: la domanda {d!r} non viene da una ricerca salvata ({k} -> {sug!r})")
    # 8. collegamenti dal resto del sito; piè di pagina comune invariato (vincolo dell'esperimento A/B)
    for f, x in (("index.html", f'href="{sez}"'), ("how-it-works/index.html", f'href="../{sez}"')):
        if x not in leggi(f):
            errori.append(f"30: manca il link {x} in {f}")
    if "top-university" in G.piede_en("") or any("top-university" in leggi(f"visa-refusal-rates/{c}/index.html") for c in G.ESP.get("controllo", [])):
        errori.append("30: il piè di pagina comune o una pagina di controllo dell'esperimento è cambiata")
    return errori, len(pagine), note


def main():
    errori = controlla_esempi()
    print(f"1. Esempi a mano: {len(ESEMPI)} importi e {len(ESITI)} confronti con il reddito, {len(errori)} errori")
    e2 = controlla_js(casi_casuali())
    print(f"2. Motore JS contro Python: {len(e2)} differenze")
    e3, n = controlla_link()
    print(f"3. Link interni: {n} pagine, {len(e3)} link rotti")
    e4 = controlla_fonti()
    print(f"4. Fonte e data sotto la cifra: {len(G.PROG)} programmi, {len(e4)} errori")
    e5 = controlla_parole()
    print(f"5. Parole vietate: {len(e5)}")
    e6 = controlla_contenuti()
    print(f"6. Correzioni della revisione presenti nelle pagine: {len(e6)} errori")
    e7, n7, x7 = controlla_rifiuti(online="--offline" not in sys.argv)
    print(f"7. Visa refusal rates: {n7} pagine, {x7} link esterni controllati, {len(e7)} errori")
    e8, n8 = controlla_facile()
    print(f"8. Easiest Schengen visa ({n8} pagine) e visti UK di studio, lavoro, famiglia e partner: {len(e8)} errori")
    e9, n9 = controlla_altri_siti()
    print(f"9. Blocco \"Other useful tools for your trip\" ({len(G.ALTRI_SITI)} link) in {n9} pagine indicizzabili: {len(e9)} errori")
    e10 = controlla_indexnow()
    print(f"10. File chiave IndexNow {G.CHIAVE_INDEXNOW}.txt in sito/ (contenuto giusto, fuori dalla sitemap): {len(e10)} errori")
    e11 = controlla_altri()
    print(f"11. Australia, Nuova Zelanda, Canada (3 pagine di riepilogo, sezioni per Paese, soglia e cifre ricalcolate): {len(e11)} errori")
    e12, n12, c12 = controlla_trasferimenti()
    print(f"12. Who moved where: {n12} pagine ({c12} nazionalità × Paese attese con 500+), numeri, titoli, fonti, JSON-LD e link: {len(e12)} errori")
    e13, n13, d13 = controlla_lastmod()
    print(f"13. Sitemap: {n13} URL con lastmod ({d13} date diverse, uguali al registro dati/lastmod.json): {len(e13)} errori")
    e14, i14 = G.MON.controlla_sito(G.SITO_ID, SITO)  # controllo comune di monetizzazione (monetizzazione.py)
    print("14. " + G.MON.riepilogo(G.SITO_ID, i14, e14))
    e15, n15 = controlla_mev()
    print(f"15. Visti Schengen a ingressi multipli: {n15} pagine (riassuntiva + riquadri per Paese), numeri ricalcolati, sitemap, titolo, link: {len(e15)} errori")
    e16, n16 = controlla_selt()
    print(f"16. Test di inglese UK (SELT): {n16} pagine (indice + città e Paesi con domanda), centri ricalcolati, sitemap, titoli, fonte, B2, affiliati: {len(e16)} errori")
    e17, n17, r17 = controlla_ppsn()
    print(f"17. Irlanda, PPS per nazionalità: {n17} pagine, numeri, tabelle, fonte, link dall'hub; 10 valori ricontrollati sui CSV ufficiali: {len(r17)}: {len(e17)} errori")
    for x in r17:
        print("    ·", x)
    e18, n18, r18 = controlla_dtv(online="--offline" not in sys.argv)
    print(f"18. Thailand DTV visa: {n18} pagine (indice + sedi), costi, regole, frammenti, affiliati, link; frammenti ricontrollati online: {len(r18)}: {len(e18)} errori")
    for x in r18:
        print("    ·", x)
    e19, n19, j19, r19 = controlla_opt(online="--offline" not in sys.argv)
    print(f"19. US OPT e STEM OPT: {n19} pagine, cifre, fonti, proposta e regola rinviata, calcolatori (JS = Python su {j19} casi); riletti online: {len(r19)}: {len(e19)} errori")
    for x in r19:
        print("    ·", x)
    e20, n20, j20, r20 = controlla_graduate(online="--offline" not in sys.argv)
    print(f"20. UK Graduate visa: {n20} pagine, durate, tariffa e IHS, tabelle ricalcolate, calcolatore (JS = Python su {j20} casi); frammenti riletti online: {len(r20)}: {len(e20)} errori")
    e21, n21, j21, r21 = controlla_mx(online="--offline" not in sys.argv)
    print(f"21. Mexico residency: {n21} pagine, costi 2026, calcolo UMA, consolati e frammenti, affiliati, link, calcolatore (JS = Python su {j21} casi); riletti online: {len(r21)}: {len(e21)} errori")
    for x in r21:
        print("    ·", x)
    e22, n22, j22, r22 = controlla_it(online="--offline" not in sys.argv)
    print(f"22. Study in Italy: {n22} pagine, cifre nazionali, enti DSU e frammenti dei bandi, Paesi poveri, cambi, esempio ISEE, affiliati, link, calcolatore (JS = Python su {j22} casi); riletti online: {len(r22)}: {len(e22)} errori")
    for x in r22:
        print("    ·", x)
    e23, n23, j23, r23 = controlla_f7(online="--offline" not in sys.argv)
    print(f"23. Italy 7% flat tax: {n23} pagine, regole, tabella delle regioni, Comuni vicini alla soglia, elenchi del sisma, towns.json, strumento (JS = Python su {j23} casi, ricerca di ogni Comune); riletti online: {len(r23)}: {len(e23)} errori")
    for x in r23:
        print("    ·", x)
    e24, n24 = controlla_sr()
    print(f"24. Schengen visa from the UK / from Dubai: {n24} pagine, cifre ricalcolate dal file della Commissione, tabelle, consolati, conversioni GBP/AED, importi di riferimento, fornitori, AXA spento, link: {len(e24)} errori")
    e25, n25, c25, b25 = controlla_esperimento()
    print(f"25. Esperimento pagine citabili: {n25} trattate (data, dateModified, Key figures = dati, Dataset, {c25} CSV validi), "
          f"{len(G.ESP.get('controllo', []))} di controllo invariate ({b25} identiche byte per byte all'impronta salvata): {len(e25)} errori")
    e26, n26, r26 = controlla_cer()
    print(f"26. Australian citizenship ceremony wait times: {n26} pagine (indice, council con domanda, tempi), {r26} righe ricontrollate sulla risposta ufficiale di Home Affairs, "
          f"tabelle, quote ponderate, storico, percentili, avviso, licenza, link: {len(e26)} errori")
    e27, n27, j27, r27 = controlla_ee(online="--offline" not in sys.argv)
    print(f"27. Sezioni in spagnolo e portoghese (denaro per entrare in Europa): {n27} pagine, importi = tabella della Commissione, esempi ricalcolati, "
          f"hreflang reciproci e selettore di lingua, citazioni = frammenti ufficiali, visti = Reg. 2018/1806, ETIAS senza date, SafetyWing, link, "
          f"calcolatore (JS = Python su {j27} casi); riletti online: {len(r27)}: {len(e27)} errori")
    for x in r27:
        print("    ·", x)
    e28, n28, r28 = controlla_vl(online="--offline" not in sys.argv)
    print(f"28. Visti di lunga durata per nazionalità (es/pt): {n28} pagine, fonti e impronte, importi e tabelle ricalcolati, tasse = frammenti, date dei listini, "
          f"hreflang, citazioni, link alle fonti, FAQ da ricerche vere, nessun affiliato, link; riletti online: {len(r28)}: {len(e28)} errori")
    for x in r28:
        print("    ·", x)
    e29, n29, r29 = controlla_infermieri()
    print(f"29. Infermieri formati all'estero e UK Ancestry visa: {n29} pagine, ricalcolo dai file NMC e JQ06, prima frase, tabelle (registro, nuovi iscritti, Irlanda, "
          f"Health and Care Worker, lista rossa, costi NMC e cambi, Ancestry per nazionalità e per anno), citazioni = frammenti, FAQ da ricerche vere, link, piè di pagina: {len(e29)} errori")
    for x in r29:
        print("    ·", x)
    e30, n30, r30 = controlla_tu()
    print(f"30. Liste delle università per i visti dei laureati (HPI, TTPS, J-Find): {n30} pagine, impronte e fonti, righe = liste ufficiali (lettore proprio sui file grezzi), "
          f"frammenti, università e Paesi, prima frase con risposta, fonte e data, tabelle ricalcolate, confronto dei visti, citazioni, FAQ da ricerche vere, nessun affiliato, link, piè di pagina: {len(e30)} errori")
    for x in r30:
        print("    ·", x)
    tutti = errori + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9 + e10 + e11 + e12 + e13 + e14 + e15 + e16 + e17 + e18 + e19 + e20 + e21 + e22 + e23 + e24 + e25 + e26 + e27 + e28 + e29 + e30
    for e in tutti:
        print(" -", e)
    if tutti:
        sys.exit(1)
    print("TUTTO OK")


if __name__ == "__main__":
    main()
