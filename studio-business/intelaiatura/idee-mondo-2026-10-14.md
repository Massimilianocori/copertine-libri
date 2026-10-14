# Ricerca idee nel mondo (14/10/2026, notte): niente Italia, solo pubblici che valgono

Richiesta di Massimiliano: "tutto quello che trovate è italiano". Questa ricerca guarda **solo fuori dall'Italia**, in ordine di valore della pubblicità: USA, Regno Unito, Canada, Australia, Germania, Francia, Spagna, Paesi Bassi, Nordici, Giappone, Corea, Brasile, Messico, India.
Modello: sito o strumento gratuito, costruito e aggiornato in automatico, costo zero, niente email a freddo, niente social, niente vendita diretta. Soldi da pubblicità e affiliazioni.
Schema cercato: **una domanda che la gente fa su Google ogni giorno, a cui risponde un dato ufficiale (o poche fonti stabili), oggi presentato male**.

Tutte le prove sono del 14/10/2026: `curl` dal server (stato HTTP, formato, dimensione, data dell'ultima modifica), Google Autocomplete (`suggestqueries.google.com`, `client=firefox`, con il Paese giusto: en/us, en/gb, en/ca, en/au, en/in, en/ng, de/de, fr/fr, es/es, nl/nl) e ricerca web per vedere chi compare nei risultati.
Prima di cominciare ho riletto `ESPLORATE.md` e gli studi 1-19: nessuna idea qui sotto ripete una nicchia già chiusa (scioperi, tassa di soggiorno, redditi per i visti, passaporti, liquidi, zone a basse emissioni, richiami auto, incentivi auto, carburanti, passi alpini, Global Entry, patenti, aste).

**Limiti dichiarati**: niente Keyword Planner né Semrush. I volumi sono stime prudenti dall'autocomplete (Google propone solo ricerche fatte davvero) e dal numero di persone che hanno quel bisogno. Dal nostro proxy `travel.state.gov` risponde 403. La ricerca web usata per i risultati di Google è una ricerca USA: i risultati in India e Nigeria possono essere un po' diversi.

---

## 0. Risposta in breve

Ho messo in lista **31 idee**, ne ho scartate 23 subito o dopo un controllo, e ne ho verificate **8 fino in fondo** (domanda, risultati di Google, fonte scaricata, concorrenti, guadagni).

Il fatto più importante, che vale anche per le ricerche future: **nel 2026 i dati ufficiali americani "facili" sono già stati trasformati in siti automatici da altri.** Prestiti SBA per marchio di franchising (peersense.com, 5.186 marchi), limiti dei mutui per contea (homebuyer.com), diarie federali (federalpay.org), indennità militari (vetcalc.org), affitti HUD per CAP (bnbcalc.com), tasse comunali inglesi (salarytax.uk), percentuali di promossi all'esame di guida per centro (veygo.com). Restano libere le nicchie dove il dato è **grande, sporco o in più file**, e dove oggi Google mostra **notizie, PDF o pagine spam**.

Le tre che passano:

| # | Idea | Paese / lingua | Voto | 18 mesi (lordo, all'anno) | Ore |
|---|---|---|---|---|---|
| 1 | **Flood Insurance Cost**: quanto costa davvero l'assicurazione contro le alluvioni nel tuo CAP, contea e zona di rischio (dati di 3,7 milioni di polizze federali) | USA, inglese | **7,5** | 2.500-9.000 € | 30-40 |
| 2 | **Visa Refusal Rates**: quante domande di visto vengono respinte per nazionalità e Paese di destinazione (Schengen per consolato, Regno Unito, USA, Canada) | mondo, inglese (India, Nigeria, Pakistan, Filippine) | **7** | 1.500-5.000 € | 25-35 |
| 3 | **FAFSA School Codes**: il codice federale di ogni università americana più costi e debiti medi | USA, inglese | **6** | 1.000-4.000 € | 15-25 |

Nessuna supera da sola i 10.000 €/anno con stime prudenti. La n. 1 è la prima idea dal 9/10 con un pubblico **assicurativo americano**: è la nicchia dove la pubblicità vale di più, e dove un dato ufficiale enorme è ancora mostrato male.

---

## 1. Le 31 idee e il primo filtro

Voto da 0 a 10: domanda (0-3), risultati di Google deboli (0-2), fonte ufficiale leggibile e stabile (0-2), valore del pubblico e guadagni (0-2), rischi e lavoro (0-1).
"Verificata" vuol dire: autocomplete, risultati di Google, fonte scaricata e concorrenti guardati oggi.

| # | Idea | Paese | Verificata | Voto | Esito | Motivo in una riga (prova del 14/10/2026) |
|---|---|---|---|---|---|---|
| 1 | Costo dell'assicurazione alluvioni per CAP, contea e zona (FEMA NFIP) | USA | sì | **7,5** | **PASSA** | Vedi sez. 2 |
| 2 | Percentuali di visti respinti per nazionalità e destinazione | mondo | sì | **7** | **PASSA** | Vedi sez. 3 |
| 3 | Codici FAFSA delle università + costi | USA | sì | **6** | **PASSA con riserva** | Vedi sez. 4 |
| 4 | Attese al confine USA-Canada-Messico e alla dogana degli aeroporti, con l'ora migliore per passare | USA, CA, MX | sì | 5 | RISERVA | Domanda forte ("peace arch border wait times", "san ysidro wait time", "customs wait times jfk"); fonti ufficiali aperte (CBP `bwt.cbp.gov/api/bwtnew` 200 JSON, 85 valichi; CBSA `bwt-eng.csv` 200). Ma **bordify.com** fa già pagine con lo schema dei 90 giorni per Tijuana e Windsor, e il pubblico (pendolari) vale poco |
| 5 | Aliquota della Grundsteuer per Comune dopo la riforma 2025 | Germania | sì | 4 | RISERVA | Domanda forte ("grundsteuer hebesatz 2026 köln / bochum / essen / dortmund"); Google mostra PDF comunali e un calcolatore automatico (finanz-rechner-hub.de). Ma i dati 2026 di tutti i Comuni non hanno una fonte unica aggiornata: Destatis pubblica con un anno di ritardo, il Bund der Steuerzahler copre solo la Renania (PDF) |
| 6 | Tasso di insolvenza dei prestiti SBA per marchio di franchising e per banca | USA | sì | 3 | **NO** | Dato ottimo (file FOIA SBA 200, 436 MB, 934.089 prestiti, 4.443 marchi; aggiornato il 21/7/2026), domanda vera ("matco / f45 / meineke franchise failure rate", "sba lenders in georgia"). Ma è **già tutto fatto**: peersense.com (5.186 marchi, pagine di confronto), franchiseinvestordata.com, gosbaloans.com (classifiche per città), ctacquisitions.com (per settore) |
| 7 | Limiti dei mutui FHA, conformi, VA e USDA per contea | USA | sì | 3,5 | NO | Domanda enorme ("fha loan limits riverside county 2026", "conforming loan limits 2026 maricopa county"), ma primi homebuyer.com (pagina per contea), jvmlending.com, bankrate.com |
| 8 | Affitti HUD (Fair Market Rent) e Section 8 per CAP | USA | sì | 3 | NO | "hud fair market rent by zip code florida": bnbcalc.com (in 6 lingue), fairmarketrentmap.com, rentdata.org |
| 9 | Diarie federali GSA per città | USA | sì | 2,5 | NO | federalpay.org, fedpayscale.org, itilite.com già con le tariffe 2027 |
| 10 | Indennità casa dei militari (BAH) per base e grado | USA | sì | 2,5 | NO | vetcalc.org e milpaytools.com con pagine per base e grado |
| 11 | Salari minimi negli appalti pubblici (Davis-Bacon) per contea | USA | sì | 2,5 | NO | bidpulsar.com copia già SAM.gov; pubblico solo aziende |
| 12 | Attese ai controlli TSA per aeroporto | USA | sì | 2 | NO | Nessuna fonte ufficiale con lo storico; risultati di notizie, flightqueue.com, qsensor.co |
| 13 | Tassa comunale inglese 2026/27 per comune e fascia | UK | sì | 2,5 | NO | salarytax.uk, paychecktaxcalculator.net, uktaxdrag.co.uk con pagine per comune e fascia |
| 14 | Percentuale di promossi all'esame di guida per centro | UK | sì | 2,5 | NO | veygo.com (assicuratore) ha una pagina per ogni centro con i dati 2025/26 |
| 15 | Aliquota della taxe foncière per Comune | Francia | sì | 3 | NO | Strumento ufficiale su data.economie.gouv.fr e motore di ricerca di moneyvox.fr |
| 16 | Ritardi per numero di volo (BTS) | USA | sì | 2,5 | NO | Google Voli mostra già "spesso in ritardo"; FlightAware |
| 17 | Percentuali NCLEX (infermieri) per scuola | USA | in parte | 3 | NO | Domanda per Stato ("texas / florida nursing school nclex pass rates"), ma ~50 consigli statali (fallisce il filtro delle ≤ 20 fonti) e registerednursing.org già primo |
| 18 | Costo dell'asilo nido per contea (banca dati DOL) | USA | in parte | 3,5 | RISERVA debole | Domanda ("daycare cost in michigan / houston / nyc"), ma l'ultimo anno dei dati ufficiali è vecchio (2022) e care.com è forte |
| 19 | Software per Making Tax Digital (lista ufficiale HMRC) | UK | in parte | 3,5 | RISERVA | Domanda ("mtd software for landlords / free / sole traders"), affiliazioni contabili alte, ma è un confronto di prodotti: lo fanno già commercialisti e produttori di software. Da verificare se serve |
| 20 | Premi delle polizze sanitarie ACA 2027 per contea | USA | in parte | 3,5 | NO | Domanda ("aca premiums 2027", "obamacare 2027 changes"), ma healthcare.gov, il calcolatore KFF e healthinsurance.org sono fortissimi; tema vicino alla sanità |
| 21 | Bodenrichtwert (valore dei terreni) per Comune | Germania | solo domanda | 2,5 | NO | 16 portali regionali, quello bavarese è a pagamento: copertura sotto il 90 % |
| 22 | Date dei pagamenti pubblici (Social Security, CCB, Universal Credit, Centrelink) | USA, CA, UK, AU | solo domanda | 2,5 | NO | Domanda enorme, ma pagine ufficiali chiare e decine di siti di notizie; tema delicato (soldi di persone fragili) |
| 23 | Rendimenti dei titoli di Stato e aste del Tesoro | USA | solo domanda | 3 | NO | Un numero solo per giorno: risponde treasurydirect.gov e ogni portale finanziario |
| 24 | Salari H-1B e livelli di salario prevalente | USA | solo domanda | 2,5 | NO | h1bdata.info, myvisajobs.com già primi da anni |
| 25 | Dazi e codici doganali (HTS) | USA | solo domanda | 2 | NO | Flexport, Zonos e altri strumenti finanziati; classificare una merce è una responsabilità |
| 26 | Aziende che sponsorizzano visti di lavoro (UK, Canada LMIA, Paesi Bassi) | UK, CA, NL | solo domanda | 3 | NO | Domanda forte ("lmia approved jobs in canada", "uk sponsor licence list"), ma decine di siti "sponsor finder" e pubblico che vale poco in pubblicità |
| 27 | Tempi di lavorazione IRCC ed estrazioni Express Entry | Canada | solo domanda | 2,5 | NO | Strumento ufficiale e CIC News primi |
| 28 | Prezzo al metro quadro (Francia), valore WOZ (Olanda), valore catastale (Spagna) | FR, NL, ES | solo domanda | 2 | NO | Strumenti ufficiali (DVF, WOZ-waardeloket, Catastro) e portali immobiliari |
| 29 | Banche più o meno sicure (bilanci FDIC) | USA | no | 2,5 | NO | depositaccounts.com e Bauer hanno già un voto per ogni banca |
| 30 | Prestiti per banca e percentuale di mutui rifiutati (HMDA) | USA | solo domanda | 2,5 | NO | Domanda debole e generica ("mortgage denial rates by race") |
| 31 | Elettricità per CAP, internet per CAP | USA | no | 2 | NO | energysage, chooseenergy, broadbandnow, highspeedinternet: grandi siti già primi |

---

## 2. N. 1 — Flood Insurance Cost (USA): quanto costa l'assicurazione alluvioni nel tuo CAP, contea e zona

**L'idea in una riga.** Una pagina per ogni Stato, contea e CAP americano con il premio **mediano** che pagano davvero le case assicurate con il programma federale NFIP nell'ultimo anno, diviso per zona di rischio (X, AE, A, VE), più quante richieste di risarcimento ci sono state e quanto è stato pagato. Il dato è ufficiale, pubblico e aggiornato ogni giorno, ma oggi FEMA lo pubblica solo come banca dati grezza da 74 milioni di righe.

### Domanda (autocomplete en/us, 14/10/2026)
- "average flood insurance cost in" → florida, texas, pa, louisiana, houston, nc, indiana, nj, new orleans, **cape coral fl**.
- "flood insurance rates by zip code" → fema, texas, florida, california; "florida flood insurance cost by zip code".
- "cost of flood insurance in" → **zone ae**, **zone x**, nc, texas, california, **florida zone ae**, zone a, indiana, pa.
- "flood insurance cost" → florida, estimator, ae zone, by address, per month, texas, indiana, california, nj.
- "flood claims by" → address, fema flood claims by address, flood claim history by address.

Chi cerca: chi compra casa (la banca obbliga a prendere la polizza nelle zone A e V), chi ha appena ricevuto il rinnovo, chi valuta un trasloco in Florida, Texas, Louisiana, Carolina. È lo stesso pubblico di mutui e assicurazioni casa: quello che paga di più in pubblicità.
Stima prudente: centinaia di migliaia di ricerche al mese sommando Stati, città, CAP e zone, con picchi dopo ogni uragano e a ogni rinnovo.

### Risultati di Google oggi
- "average flood insurance cost in cape coral fl": NerdWallet (media di città, senza data), notizie, agenzie locali.
- "average flood insurance cost in houston texas": ValuePenguin (821 $/anno per città), Hippo, **pagine spam su domini rubati** (new.fadisma.com.br, phpmyadmin.muycomputerpro.com).
- "cost of flood insurance in zone ae florida": **solo pagine spam** che ripetono "757 $ l'anno" senza fonte (live.museum.manchester.ac.uk, revivalportal.goodwood.com, marketplace.ultimatemotorcycling.com). È il segnale più chiaro: Google non ha niente di buono da mostrare.
- "average flood insurance cost by zip code": Policygenius (medie per circa 14.000 CAP, metodo non verificabile), Bankrate (media nazionale 926 $), Gerald (stime senza metodo).

**Concorrenti e cosa manca a loro**: Policygenius ha i CAP ma senza zona di rischio e senza risarcimenti; ValuePenguin e NerdWallet hanno solo città e Stati; nessuno incrocia **zona × luogo × anno** con polizze recenti (le tariffe sono cambiate con il "Risk Rating 2.0"), e nessuno mostra i risarcimenti del CAP accanto al premio.

### La fonte (verificata dal server)
- **OpenFEMA `NfipPolicies` v3**: `https://www.fema.gov/api/open/v3/NfipPolicies` → **200 JSON**, **74.739.461 righe**, ultimo aggiornamento **14/10/2026**. Polizze con decorrenza dal 1/9/2025: **3.709.895**. Campi utili: `reportedZipCode`, `ratedFloodZone`, `policyCost`, `totalBuildingInsuranceCoverage`, `occupancyType`, `primaryResidenceIndicator`, `crsClassCode`, `policyEffectiveDate`. Una richiesta da 10.000 righe risponde in circa 2 secondi: l'anno intero si scarica in circa 370 richieste.
- **OpenFEMA `NfipClaims` v3** → **200 JSON**, **2.725.989 risarcimenti** (es. CAP 33904 di Cape Coral: 2.773 risarcimenti).
- **`NfipResidentialPenetrationRates`** (quota di case assicurate per contea, 3.159 righe) e **`NfipCommunityStatusBook`** (sconti CRS per Comune): stessa API.
- Licenza: dati pubblici del governo USA. FEMA chiede di dire che non sono un rapporto ufficiale.
- Attenzione: le versioni v2 si spengono il **15/10/2026** (domani). La v3 è quella giusta, e lo spegnimento dimostra che FEMA cambia le versioni: serve un controllo automatico che avvisa se l'API cambia.

Prova sul campione (CAP 77002, Houston, polizze dal 1/9/2025, case unifamiliari): 149 polizze, mediana zona X 1.154,5 $ (4 polizze). Per i CAP piccoli serve una soglia minima: pagina solo se ci sono almeno 10 polizze residenziali, altrimenti si mostra la contea.

### Come si guadagna
- **Pubblicità**: assicurazioni è la nicchia più cara. Le stime pubblicate per il 2026 vanno da 12-40 $ (calcolatore AdSense, ecomcalctools.com) a 40-80 $ ogni 1.000 pagine viste (biztoolkit.co). Per pagine informative uso una stima prudente di **8-15 $**.
- **Affiliazioni (preventivi casa, cifre pubbliche nelle directory, da confermare all'iscrizione)**: Lemonade 15 $ per preventivo casa negli USA (Awin, cookie 30 giorni, secondo Affilimate), Allstate fino a 28 $ per preventivo (FlexOffers, cookie 5 giorni), USAA 36 $ per preventivo idoneo (CJ). Neptune Flood (il maggiore assicuratore privato) vende solo tramite agenzie: niente programma pubblico.
- Nessun contatto da vendere, niente vendita diretta.

### Stima prudente a 18 mesi (lordo)
Ipotesi: 50 pagine di Stato con le zone, circa 3.100 pagine di contea, 8.000-14.000 pagine di CAP (solo quelli con almeno 10 polizze), 4 guide per zona. Indicizzazione lenta per i primi 4 mesi (sito nuovo, tema "soldi"). Al mese 18: **15.000-40.000 visite al mese**, quasi tutte dalle ricerche lunghe (zona × Stato, contea, CAP), mentre le ricerche principali restano a Policygenius e NerdWallet.
- Pubblicità: 15.000-40.000 × 8-15 $ / 1.000 = 120-600 $ al mese.
- Preventivi: 0,1-0,2 % delle visite = 15-80 preventivi al mese × 15 $ = 225-1.200 $ al mese.
- **Primo anno: 300-2.000 €. Al mese 18: 2.500-9.000 €/anno.** Sotto i 15.000 visite al mese la cifra scende verso il basso della forchetta.

### Ore di costruzione (riuso di `italystrikes/genera.py`): 30-40
- Scarico mensile con GitHub Actions (circa 370 richieste, solo i campi utili) e calcolo delle mediane per Stato, contea, CAP e zona: 12-15 ore.
- Pagine e sitemap con i modelli di `genera.py` (schema "luogo → tabella → spiegazione → fonte"): 10-12 ore.
- Grafici statici, guide per zona, controllo dei fatti e del design: 8-13 ore.
- Un deploy al mese (dati FEMA mensili): rientra nel limite dei crediti Netlify.

### Rischi
1. **Tema "soldi"**: Google chiede più fiducia. Ogni pagina dice "è la mediana di quanto pagano i vicini, non un preventivo" e linka FEMA.
2. La mediana di un CAP non è il prezzo di una casa: dipende dall'altezza della casa e dalla copertura. Si mostrano sempre il numero di polizze e la forchetta (25°-75° percentile).
3. Policygenius o NerdWallet possono aggiungere le zone in poco tempo.
4. FEMA cambia le versioni dell'API (v2 spenta il 15/10/2026).
5. Rinnovi del programma NFIP a ogni scadenza del Congresso: notizie da seguire, non un rischio per i dati.

---

## 3. N. 2 — Visa Refusal Rates (mondo): quante domande di visto vengono respinte, per nazionalità e destinazione

**L'idea in una riga.** Una pagina per ogni coppia "nazionalità → destinazione" (per esempio "Germany visa rejection rate for Nigerians", "France visa approval rate for Indians") e per ogni consolato Schengen ("French consulate Mumbai"), con le domande, i visti rilasciati, i rifiuti e l'andamento negli anni, presi dai file ufficiali di Commissione Europea, Home Office britannico, Dipartimento di Stato USA e Canada. Il dato esiste, ma oggi lo raccontano solo le notizie una volta l'anno.

### Domanda (autocomplete, 14/10/2026)
- en/in: "schengen visa rejection rate" → for indians, india, **by country**, pakistan, philippines, **country wise**; "schengen visa approval rate" → for indians, by country 2026, for nigerians, for pakistan.
- en/in: "**easiest schengen visa**" → from india, for indians, to get from india, country, for indian passport holders.
- en/in: "france visa rejection rate" → for indians, for indian students, pakistan, in nigeria; "germany visa approval rate" → for indians, for nigerians, for sri lanka, philippines, from nepal; "switzerland visa rejection rate" → for indians, pakistan, tourist, student, business.
- en/in e en/ng: "uk visa rejection/refusal rate" → for indians, by country, for indian students, pakistan, bangladesh, nigeria; "us visa rejection rate" → india 2026, b1/b2, in hyderabad, in delhi, pakistan; "canada visitor visa approval rate" → from india, 2026, by country, today, from pakistan.

Volume: solo dall'India 1,15 milioni di domande Schengen nel 2025; Cina 1,81 milioni, Turchia 1,27 milioni; 11,93 milioni in tutto (dati della Commissione riportati da traveltradejournal.com e freepressjournal.in). Ognuna di queste persone si chiede "dove ho più probabilità". La matrice è grande: circa 100 nazionalità × 29 Paesi Schengen + Regno Unito + USA + Canada.

### Risultati di Google oggi
- "schengen visa rejection rate by country for indians": notizie (Outlook Traveller, Free Press Journal, ETV Bharat), un blog di agenzia (abroadgateway.com).
- "germany visa approval rate for nigerians": notizie (Nairametrics, The African Courier), agenzie di visti con numeri senza fonte (visafeecalculator.com, visabeat.com).
- "uk visa refusal rate by country visitor visa 2026": notizie nigeriane, blog di studi legali (connaughtlaw.com), agenzie (visa2fly.com). Nessuna tabella per Paese.
- "France consulate Mumbai rejection rate": un blog (arbeitnow.com) con una tabella senza anno.

**Nessun sito ha una pagina per ogni coppia con i numeri ufficiali e l'andamento.** Le notizie escono una volta l'anno e poi invecchiano.

### Le fonti (verificate dal server)
- **Schengen, Commissione Europea**: file "Visa statistics for consulates" per anno (2010-2024) sulla pagina `home-affairs.ec.europa.eu/policies/schengen/visa-policy/short-stay-visas-issued-schengen-countries_en` (200). File 2024 scaricato: **200, XLSX, 558.784 byte**, **2.042 righe** (Stato Schengen × Paese × consolato) con domande, visti rilasciati, visti a ingressi multipli, rifiuti e percentuale di rifiuto. Il file 2025 non è ancora sulla pagina (le notizie di maggio-giugno 2026 citano già i numeri 2025): da ricontrollare. Riutilizzo libero con citazione (regole della Commissione).
- **Regno Unito, Home Office**: `entry-clearance-visa-outcomes-datasets-jun-2026.xlsx` → **200, 33 MB, aggiornato il 19/8/2026**, dal 2005 al secondo trimestre 2026, **407.288 righe** (nazionalità × tipo di visto × esito). Licenza OGL. Trimestrale.
- **USA, Dipartimento di Stato**: percentuale di rifiuto dei visti B per nazionalità, un PDF all'anno. `travel.state.gov` risponde **403** dal nostro proxy: da scaricare dal computer di Massimiliano o via ricerca. Una sola tabella l'anno.
- **Canada, IRCC**: dati aperti sui visti temporanei (portale open.canada.ca); il motore di ricerca del portale non ha risposto dal proxy oggi. Da provare nel test.

### Come si guadagna
- **Pubblicità**: pubblico per lo più indiano, nigeriano, pakistano, filippino. Pubblicità che vale poco: stima prudente **1,5-3 $** ogni 1.000 pagine viste (mista, perché una parte delle ricerche arriva da chi vive nel Regno Unito, negli USA o nel Golfo).
- **Affiliazioni che c'entrano davvero**: l'assicurazione di viaggio è **obbligatoria** per il visto Schengen. EKTA paga il **20 %** della polizza tramite Travelpayouts (pagina dell'offerta Travelpayouts); SafetyWing è già attivo sui nostri siti; iVisa paga il 10 % secondo i suoi termini (programma su Awin, da verificare se è aperto).
- Nota pratica: l'account Travelpayouts è approvato ma in pausa per lo script con i cookie (cruscotto, sez. 7). Senza EKTA resta SafetyWing.

### Stima prudente a 18 mesi (lordo)
Ipotesi: circa 2.000 pagine coppia Schengen (solo coppie con almeno 100 domande l'anno), circa 2.000 pagine consolato, 200 nazionalità × 3 (UK, USA, Canada). Al mese 18: **20.000-60.000 visite al mese**.
- Pubblicità: 20.000-60.000 × 1,5-3 $ / 1.000 = 30-180 $ al mese.
- Assicurazioni: 0,05-0,15 % delle visite = 10-90 polizze al mese × 4-8 € = 40-700 € al mese.
- **Primo anno: 200-1.200 €. Al mese 18: 1.500-5.000 €/anno.**

### Ore (riuso del motore): 25-35
Tre lettori di file (XLSX Commissione, XLSX Home Office, PDF USA) 10-14 ore; pagine coppia, consolato e Paese con `genera.py` 10-14 ore; controlli 5-7 ore.
**Proposta pratica**: costruirla come **sezione del sito Visa Income Checker** (stesso tema "visti", già online): niente sito nuovo, niente crediti Netlify in più, e le pagine si rafforzano a vicenda.

### Rischi
1. Le percentuali non predicono il singolo caso: ogni pagina lo dice chiaramente, niente consigli su come "ottenere" il visto.
2. Dati Schengen una volta l'anno: le pagine invecchiano nei mesi prima del file nuovo. Il Regno Unito è trimestrale e tiene il sito vivo.
3. Pubblico che vale poco in pubblicità: il guadagno dipende dalle assicurazioni.
4. Concorrenti con redazione (schengenvisainfo.com, Atlys) possono copiare la matrice.
5. Fonte USA bloccata dal proxy (403): si parte con Schengen e Regno Unito.

---

## 4. N. 3 — FAFSA School Codes (USA): il codice di ogni università, con costi e debiti

**L'idea in una riga.** Una pagina per ognuna delle 6.547 scuole con il codice federale da mettere nella domanda di aiuto allo studio (FAFSA), l'indirizzo, e accanto costo netto, debito medio e guadagni dopo la laurea (College Scorecard). È una domanda che ogni anno fanno milioni di famiglie, da ottobre a giugno.

### Domanda (autocomplete en/us)
- "fafsa school code" → search, list, **for capella university, penn state, wgu, chamberlain university, snhu, liberty university**.
- "fafsa code for" → chamberlain, penn state, columbia, wgu, boston university, boston college, northeastern, george washington, nyu.
- "federal school code" → lookup, list, search tool, list for 529 plans, list international.
- Simili: "css profile code for cornell / nyu / columbia / michigan / duke / stanford", "sat code for ohio state / usf / purdue / ut austin / virginia tech".

### Risultati di Google oggi
- "fafsa school code for wgu": **solo pagine spam su domini rubati** (alumni.caelum.com.br, tool.rubadub.co.uk, vacavilletrauma.kaiserpermanente.org…), una con un codice sbagliato (015690 invece di 033394).
- "fafsa code for boston university": le pagine dell'università stessa e una pagina spam con un codice sbagliato (E00473).

### La fonte (verificata dal server)
- **Federal School Code List 2026-27** (quarta edizione trimestrale, agosto 2026): `fsapartners.ed.gov/sites/default/files/2026-07/2627FederalSchoolCodeList4thQuarter.xlsx` → **200, XLSX, aggiornato il 29/7/2026**, **6.547 scuole** (codice, nome, indirizzo, città, Stato, CAP, Paese), comprese le università estere.
- **College Scorecard** (Dipartimento dell'Istruzione): API gratuita con chiave api.data.gov (2 minuti, da creare da Massimiliano), per costi, debiti e guadagni.

### Come si guadagna
- Pubblicità istruzione USA: stima prudente **6-12 $** ogni 1.000 pagine viste.
- Affiliazioni prestiti agli studenti (cifre delle directory, da confermare): Ascent fino a 125 $ per prestito approvato (cookie 90 giorni), Splash Financial 240 $ per prestito chiuso, ELFI fino a 400 $ per rifinanziamento. Per chi compila la FAFSA conta soprattutto Ascent (prestito privato).

### Stima prudente a 18 mesi (lordo)
Ipotesi: 6.547 pagine scuola + 50 pagine Stato; 10.000-40.000 visite al mese nella stagione (ottobre-marzo), la metà fuori stagione.
- **Primo anno: 150-1.000 €. Al mese 18: 1.000-4.000 €/anno.**

### Ore: 15-25 (la fonte è un solo file; la parte College Scorecard è facoltativa)

### Rischi (per questo il voto è 6)
1. **Risposta direttamente su Google**: per una domanda da un numero Google può mostrare il codice nella pagina dei risultati, e nessuno clicca.
2. Il modulo FAFSA ha già una ricerca delle scuole dentro: chi è già nel modulo non cerca su Google.
3. Stagionale (ottobre-giugno).
4. Lo spam di oggi può essere ripulito da Google o sostituito da un concorrente serio.

---

## 5. Le altre verificate, in breve

- **Attese al confine e alla dogana (voto 5, RISERVA)**. Fonti ufficiali aperte e in tempo reale: CBP `bwt.cbp.gov/api/bwtnew` (200, JSON, 134 KB, 85 valichi, aggiornato ogni pochi minuti), `bwt.cbp.gov/xml/bwt.xml` (200), CBSA `cbsa-asfc.gc.ca/bwt-taf/bwt-eng.csv` (200, verso il Canada); per gli aeroporti il sito ufficiale `awt.cbp.gov` ha un'esportazione CSV per aeroporto e ora (da provare). Domanda forte ("peace arch border wait times northbound/southbound", "ambassador bridge wait times", "san ysidro wait time pedestrian/ready lane", "best time to cross border on saturday", "customs wait times jfk/lax/ewr/iad/ord"). Il nostro vantaggio sarebbe lo storico ("l'ora migliore per passare il sabato"), che costruiremmo archiviando i dati ogni 15 minuti con il motore di Italy Strikes. Ma **bordify.com fa già esattamente questo** per Tijuana e Windsor, e il pubblico (pendolari, acquisti oltre confine) vale poco. Si tiene come riserva per la parte "dogana negli aeroporti", dove Google mostra solo notizie del 2013 e spam.
- **Grundsteuer per Comune (voto 4, RISERVA)**: vedi tabella, riga 5. Si riapre se Destatis o i 16 uffici statistici pubblicano le aliquote 2026 di tutti i Comuni in un unico file.
- **Prestiti SBA per franchising (voto 3, NO)**: ho scaricato i due file FOIA (255 MB e 181 MB, aggiornati il 21/7/2026) e calcolato i tassi di insolvenza: funziona (per esempio 47.446 prestiti a marchi di franchising tra il 2010 e il 2019, 7,7 % finiti in perdita). Ma peersense.com ha già 5.186 marchi con pagine di confronto, franchiseinvestordata.com ha pagine per marchio, gosbaloans.com le classifiche delle banche per città. Arriviamo tardi.
- **Limiti dei mutui per contea (voto 3,5, NO)**: il tempismo sarebbe perfetto (i limiti 2027 escono a fine novembre), ma homebuyer.com ha già una pagina per contea con 2025 e 2026, insieme a bankrate e jvmlending.

---

## 6. Verdetto

1. **Flood Insurance Cost (USA)** è la migliore idea trovata finora fuori dall'Italia: domanda grande e ripetuta, il pubblico che vale di più in pubblicità, una fonte federale enorme e aggiornata ogni giorno, e Google che per "zona AE in Florida" mostra solo spam. È un **sito nuovo** in inglese, stesso motore. **Proposta: costruirla.** Serve solo il sì di Massimiliano: niente chiavi, niente account nuovi, costo zero.
2. **Visa Refusal Rates** è la più grande per numero di persone, ma vale poco per visita. **Proposta: costruirla come sezione di Visa Income Checker**, partendo da Schengen e Regno Unito (fonti scaricate oggi).
3. **FAFSA School Codes** è facile e veloce, ma rischia che Google dia la risposta da solo. **Si costruisce solo se una delle prime due supera la soglia dei 45 giorni.**

Somma onesta: le tre insieme valgono **5.000-18.000 €/anno lordi a 18 mesi** se Google le indicizza tutte, **2.500-8.000 €** se ne passa una sola (di solito non passano tutte). Non sono un colpo solo: aggiungono alla rete pubblici nuovi e più ricchi (assicurazioni americane, studenti americani, viaggiatori di India e Africa), senza dipendere dall'Italia.

## 7. Soglie scritte prima (da riportare nel cruscotto)

| Idea | Quando | Soglia | Se non passa |
|---|---|---|---|
| Flood Insurance Cost | 45 giorni dalla pubblicazione | ≥ 300 impressioni al mese (regola della rete) e ≥ 500 pagine indicizzate | Si tengono solo le pagine di Stato e contea, si fermano i CAP |
| Flood Insurance Cost | 120 giorni | ≥ 1.000 clic al mese oppure ≥ 10.000 impressioni al mese | Chiusura con motivazione scritta |
| Visa Refusal Rates (sezione) | 45 giorni | ≥ 300 impressioni al mese sulla sezione | Si ferma l'aggiunta di pagine |
| Visa Refusal Rates (sezione) | 120 giorni | ≥ 1.000 clic al mese e ≥ 5 polizze vendute tramite i link | Si tiene solo la pubblicità, senza nuove pagine |
| FAFSA School Codes | si parte solo se una delle due sopra passa i 45 giorni; poi 45 giorni nella stagione FAFSA | ≥ 300 impressioni al mese | Chiusura |

## 8. Fonti principali (lette il 14/10/2026)
- OpenFEMA, elenco dei dataset NFIP e API v3: https://www.fema.gov/api/open/v1/OpenFemaDataSets ; https://www.fema.gov/api/open/v3/NfipPolicies ; https://www.fema.gov/api/open/v3/NfipClaims
- Commissione Europea, statistiche dei visti Schengen per consolato: https://home-affairs.ec.europa.eu/policies/schengen/visa-policy/short-stay-visas-issued-schengen-countries_en
- Home Office, esiti dei visti: https://www.gov.uk/government/statistical-data-sets/immigration-system-statistics-data-tables
- FSA, Federal School Code List: https://fsapartners.ed.gov/knowledge-center/library/federal-school-code-lists/2026-07-29/2026-27-federal-school-code-list-participating-schools-august-2026
- SBA, dati FOIA 7(a) e 504: https://data.sba.gov/dataset/7a-504-foia
- CBP, attese ai confini: https://bwt.cbp.gov/api/bwtnew ; CBSA: https://www.cbsa-asfc.gc.ca/bwt-taf/bwt-eng.csv
- Concorrenti citati: policygenius.com, valuepenguin.com, nerdwallet.com, peersense.com, franchiseinvestordata.com, gosbaloans.com, homebuyer.com, bnbcalc.com, federalpay.org, vetcalc.org, bidpulsar.com, salarytax.uk, veygo.com, bordify.com, finanz-rechner-hub.de
- Affiliazioni: Travelpayouts, offerta EKTA (20 %); Affilimate, programmi assicurativi (Lemonade, Allstate, USAA); directory FlexOffers e referly per i prestiti agli studenti; affi.io per iVisa
- Pubblicità per nicchia (stime di settore): ecomcalctools.com, biztoolkit.co, monetizemore.com
