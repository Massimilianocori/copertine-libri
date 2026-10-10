# Chi pagherebbe per i dati e gli avvisi sugli scioperi dei trasporti italiani (oltre alla pubblicità)?

Studio del 10 ottobre 2026. Tutte le pagine citate sono state lette il 10/10/2026 (con curl dal server o con la ricerca web). Dove un numero viene da una fonte secondaria lo dico. Nessun numero è inventato: le stime sono calcoli dichiarati a partire dalle prove.

## 0. Risposta in breve

**Nessuna delle sei vie cambia l'ordine di grandezza dei 4-8k €/anno.** Sommate con prudenza aggiungono **400-2.000 €/anno a 18 mesi**, e solo se il sito passa il test di novembre e cresce. Il motivo principale, scoperto in questo studio: **i dati non sono scarsi**.

1. Il registro MIT ha un **archivio storico pubblico dal 1° gennaio 2014** (pagina "Ricerca": «L'archivio on line degli scioperi parte dal 1 gennaio 2014»; verificato con tre interrogazioni: marzo 2015 → 66 scioperi, anno 2025 → 584, marzo 2026 → 46, con stato "Effettuato/Revocato"). La nostra nota interna ("il registro mostra solo gli scioperi futuri") vale per la pagina principale e per l'RSS, **non per la ricerca**. Il nostro archivio storico non è un bene unico.
2. Il MIT pubblica lo stesso dataset su dati.gov.it con **licenza CC-BY 4.0** (riuso commerciale permesso citando la fonte); il CSV è fermo al 2020 (4.695 righe, 2014-2020), ma la licenza è il punto.
3. L'associazione onData (campagna DatiBeneComune, con ActionAid e Transparency International) **estrae ogni giorno** i dati MIT e CGSSE dal 1/1/2025 e li pubblica gratis in CSV/JSONL su GitHub; Sky TG24 ci ha costruito sopra "Lo scioperometro". Un giornale che vuole i dati li prende da lì, gratis.
4. Chi vende "strike alerts" a chi viaggia per lavoro (Riskline, International SOS, Crisis24, Hozint) copre già l'Italia e vende a 10-50k $/anno con contratto annuale; TripIt Pro (48,99 $/anno) e TravelPerk ricevono gli avvisi di sciopero da Riskline. Le app di viaggio (Omio, Trainline, TravelPerk, Navan) non hanno un buco da riempire.
5. Le app consumer sugli scioperi italiani esistono già e sono piccole: la più scaricata ("C'è Sciopero", giugno 2025) ha **1.000+ download su Google Play e 24 valutazioni su App Store Italia dopo 16 mesi**, gratis senza acquisti in-app. Quella a pagamento ("Strike Tracker", 4,99 €/mese o 19,99 €/anno) ha 500+ download e zero valutazioni in Italia.

Quello che resta vendibile è piccolo e va fatto **solo in modo passivo**: un feed "Pro" (iCal/JSON/email per città e settore) venduto da una pagina "For businesses" e da un Actor Apify, e, molto più avanti, avvisi personalizzati a pagamento quando la lista supera i 5.000 iscritti.

## 1. Tabella riassuntiva

| Via | Chi pagherebbe | Prezzo realistico | Clienti a 12 / 18 mesi (prudente) | Ricavo lordo/anno a 18 mesi | Ore di Massimiliano | Automatico? | Vincolo fiscale/legale | Test a costo zero e soglia |
|---|---|---|---|---|---|---|---|---|
| **1. Feed B2B** (iCal/JSON/email/Slack per città-settore) | Piccole agenzie incoming/DMC (290 "ricettivisti" in Italia), NCC, hotel; non le piattaforme grandi (hanno Riskline) | 15-29 €/mese o 99-199 €/anno (riferimenti: Calendarific 12 $/mese-100 $/anno; aviationstack 49,99 $/mese) | 0-2 / 2-6 | **300-1.500 €** | 0,5 h (sì/no sul prezzo) + 1 h se serve un contratto | Sì (il JSON esiste già; pagamenti tramite Apify o Lemon Squeezy/Paddle) | Ricavo d'impresa → cancello fiscale (CCIAA + INPS commercianti) quando si incassa; obbligo di citare la fonte (CC-BY) | Pagina "For businesses" con modulo "chiedi il feed" (senza prezzo). Soglia: **≥ 3 richieste vere in 90 giorni** → si costruisce; altrimenti resta solo l'Actor Apify |
| **2. Licenza dei dati / archivio storico** | Nessuno trovato: MIT (2014→), dati.gov.it (CC-BY 4.0), onData (2025→, quotidiano) danno tutto gratis; Sky TG24 usa onData | 0 € | 0 / 0 | **0 €** | 0 | — | CC-BY 4.0: riuso commerciale permesso citando "Ministero delle Infrastrutture e dei Trasporti" | Nessun test: non costruire. Mettere la citazione CC-BY sul sito (1 riga) |
| **3. App mobile a pagamento** (push 1-3 €/mese o 5-10 €/anno) | Pendolari e turisti; mercato dimostrato piccolo (app leader: 1.000+ download/16 mesi, gratis) | 4,99 €/anno (Strike Tracker chiede 19,99 €/anno: nessuna valutazione) | 0 / 20-60 paganti | **100-300 €** (meno 99 $/anno Apple, 25 $ una tantum Google) | 3-4 h (account Apple/Google a suo nome, identità, fiscale) | Costruzione sì (PWA o Capacitor), pubblicazione e rinnovi no | Vendita abituale via store = P.IVA con codice 62.01 e, secondo i commercialisti online, **INPS commercianti** → stesso cancello fiscale; Apple e Google incassano l'IVA UE al posto nostro | **PWA gratuita con push web** (0 €, nessuno store): soglia **≥ 300 installazioni + ≥ 100 iscritti push in 60 giorni** prima di parlare di app a pagamento |
| **4. Avvisi email a pagamento** per viaggiatori (fase 2) | Lettori della lista gratuita | 10-20 €/anno (mediana newsletter a pagamento 100 $/anno; TripIt Pro 48,99 $/anno; ExpertFlyer da 131,88 $/anno) | con 500 iscritti: 3-10 paganti; con 5.000: 30-100 | **500 iscritti: 50-200 €; 5.000 iscritti: 500-2.000 €** | 0 (il modulo esiste; Claude invia) | Sì | Idem cancello fiscale; consenso GDPR già nel modulo | Contare gli iscritti del modulo `alerts`; soglia **≥ 500 iscritti** per fare un sondaggio (senza prezzo), **≥ 5.000** per vendere |
| **5. Media e syndication** | Nessuno paga: The Local, Wanted in Rome, Italy Magazine scrivono gli articoli da soli dal registro; Sky usa onData gratis | 0 € in denaro; valore = backlink | 0 / 0 | **0 €** (indiretto: SEO) | 0 | Sì | Licenza del widget: CC-BY a cascata, obbligo del link alla fonte | Widget gratuito "strikes this week" con link al sito: soglia **≥ 5 siti che lo incorporano in 6 mesi** = canale utile |
| **6. Canale di vendita senza email a freddo** | — | — | — | — | 0-1 h | Sì | Niente email a freddo (art. 130 Codice privacy); Google Ads B2B inutile: le query B2B ("strike alerts for tour operators", "sciopero alert") **non esistono** nel completamento automatico | Pagina "For businesses" + Actor Apify + directory gratuite; soglia: 3 richieste/90 giorni |

**Somma prudente a 18 mesi: 400-2.000 €/anno lordi**, concentrata nelle vie 1 e 4. Al netto non cambia il giudizio sul cancello fiscale: si apre solo se pubblicità + affiliazioni + queste vie superano insieme i 3.000 €/anno.

## 2. Le prove, via per via

### 2.1 B2B: abbonamento o API

**Esiste già un prodotto "strike alerts" a pagamento?** Sì, ma solo per grandi aziende e dentro piattaforme più grandi:

| Prodotto | Cosa copre | Prezzo | Fonte |
|---|---|---|---|
| Riskline (Danimarca) | avvisi 24/7 mondiali, scioperi inclusi; API e widget | «Annual contract $10,000+/yr» (pagina di un concorrente); Vendr: +250/anno per utente aggiuntivo | traveladvisory.io/platform/pricing; vendr.com/marketplace/riskline |
| International SOS / Crisis24 | assistenza + avvisi | «Annual contract, enterprise only $10,000-50,000/yr» (stesso concorrente); «$8 to $45 per active traveler monthly» (guida Travel Code 2026, da risposte RFP 2024 GSA Schedule 541) | traveladvisory.io; travel-code.com/news/travel-risk-management-software-features-vendors-buyer-guide-2026 |
| Hozint | intelligence per posto | «EUR 499-799/mo per user» (stesso concorrente) | traveladvisory.io |
| TravelRisk Pro | dati Paese, API | 199 / 499 / 999 $/mese | traveladvisory.io/platform/pricing |
| TripIt Pro | «Risk Alerts» incl. «labor action such as strikes», dati da Riskline | 48,99 $/anno (App Store/Google Play) | help.tripit.com/en/support/solutions/articles/103000280834 |
| TravelPerk | avvisi Riskline + TravelCare (strikes, closures, protests) inclusi nel servizio | incluso nel contratto | perk.com/partnership/riskline; press release Albatross |
| Perk "Travel Disruption Advisories" | pagina gratuita per travel manager (airline strikes…) | gratis | support.perk.com |

Quindi Omio, Trainline, Rome2rio, Moovit, TravelPerk, Navan, compagnie aeree e handling **non sono clienti**: o hanno Riskline, o leggono il registro MIT/ENAC (ENAC pubblica l'elenco dei voli garantiti per ogni sciopero: enac.gov.it, es. sciopero del 20/6/2025, aggiornato il 13/6/2025). Nessuna ricerca ha trovato un'API o un servizio italiano "alert scioperi per aziende/HR/mobility manager".

**Quanti sono i possibili piccoli clienti?** Agenzie di viaggio attive in Italia: «circa 7.100 agenzie, di cui 6.810 dettaglianti puri e **290 ricettivisti**» (ricerca per Fiavet Confcommercio, qualitytravel.it); «circa 7.000 agenzie con oltre 88.000 addetti» (Provincia di Trento, 25/5/2025). FTO Confcommercio: «oltre 1.900 aziende aderenti» (tour operator, agenzie e società di servizi). I 290 ricettivisti (incoming/DMC) sono il bersaglio vero: pochi e già abituati a leggere il registro. Assoviaggi/ADMEI: nessun numero pubblico trovato.

**Domanda misurata:** completamento automatico Google (10/10/2026, server USA/IT): «strike alerts api» → nessun suggerimento; «strike alerts for tour operators» → nessuno; «sciopero alert» → nessuno; «italy strike alerts email» → nessuno. La domanda B2B non si vede in Google.

**Prezzi di micro-SaaS su dati pubblici (prezzi pubblici):** Calendarific (festività): gratis 500 chiamate/mese con attribuzione; Starter **12 $/mese o 100 $/anno**; Business 500 $/anno (calendarific.com/pricing). aviationstack (voli): gratis 100 richieste; Basic **49,99 $/mese** (aviationstack.com/pricing). È la fascia giusta per noi: 10-30 €/mese.

**Stima prudente:** un feed per città/settore (iCal + JSON + email) costruito sul `vista.json` già esistente. Con una pagina "For businesses" e zero vendita attiva, lo studio 7 (sez. 2.4) stimava per un Actor Apify "Italy Strikes" 3-8 utenti e **100-400 $/anno**; aggiungendo 2-6 clienti diretti a 15-29 €/mese si arriva a **300-1.500 €/anno**. Il lavoro di Claude: 4-6 ore (endpoint iCal, pagina, Actor). Massimiliano: dire sì al prezzo.

**RapidAPI (studio 7):** scartato perché **25 % di commissione dal 15/11/2025, pagamento solo PayPal alla fine del mese successivo, recensioni Trustpilot 2025-26 su aumenti senza preavviso e pagamenti in ritardo** (docs.rapidapi.com/docs/payouts-and-finance). **Il motivo vale anche per un feed B2B**, anzi di più: un'agenzia che paga un abbonamento vuole fattura e un interlocutore, non un marketplace per sviluppatori; e Apify (20 %, bonifico) resta il canale passivo migliore per la stessa cosa.

### 2.2 Licenza dei dati e valore dell'archivio storico

- **Licenza:** dati.gov.it, dataset «scioperi-dei-trasporti», organizzazione «Ministero Infrastrutture e Trasporti», autore «Osservatorio sui conflitti sindacali del MIT», **`license_id: CC-BY-4.0`** (API: dati.gov.it/opendata/api/3/action/package_show?id=scioperi-dei-trasporti). Risorsa CSV su dati.mit.gov.it: **4.695 righe dal 4/1/2014 al 6/9/2020**, ultima modifica 4/3/2022, campi: dataInizio, dataFine, sindacato, settore, categoria, modalità, rilevanza, dataProclamazione, dataRicezione, regione, provincia, note. Le "Note legali" di mit.gov.it (non raggiungibili dal server per un blocco TLS; dalla ricerca) indicano CC BY 3.0 IT salvo diversa indicazione. **Conclusione: riuso commerciale permesso, con citazione della fonte.** Il sito deve citare «Fonte: Ministero delle Infrastrutture e dei Trasporti, scioperi.mit.gov.it, CC BY» (una riga da aggiungere).
- **Il MIT conserva lo storico:** pagina scioperi.mit.gov.it/mit2/public/scioperi/ricerca: «La ricerca verrà effettuata sull'archivio storico degli scioperi includendo, se richiesti, quelli effettuati o revocati. **L'archivio on line degli scioperi parte dal 1 gennaio 2014.**» Verifica con POST (stessi parametri dello script onData): 1-31/3/2015 → 66 righe; 1/1-31/12/2025 → 584 righe; 1-31/3/2026 → 46 righe, con stato «Effettuato» o «Revocato (include le azioni di revoca, sospensione e differimento)». Quindi lo storico lo ha il MIT, con lo stato finale. Il nostro `scioperi.json` aggiunge solo: la traduzione inglese, la mappa città/aeroporti, lo stato "rimosso dal registro" e la cronologia delle modifiche. Utile per il sito, non vendibile.
- **Già liberato gratis da altri:** github.com/ondata/liberiamoli-tutti/tree/main/scioperi (README letto il 10/10/2026): due script, `mit.sh` (ricerca MIT per l'anno corrente, tabella → JSONL/CSV con 15 campi incluse `data_proclamazione` e `data_ricezione`) e `cgsse.sh` (calendario CGSSE, via Tor da GitHub Actions); file `data/mit/mit_data.csv` e `data/cgsse/cgsse_data.csv`, dal 1/1/2025, aggiornati ogni giorno. Sky TG24 «Lo scioperometro» (tg24.sky.it/stories/cronaca/scioperometro): «I dati utilizzati in questo progetto sono estratti quotidianamente dal sito della Commissione di garanzia scioperi e messi a disposizione in formato aperto dall'associazione onData per la campagna DatiBeneComune». Un grande gruppo editoriale ha scelto i dati gratuiti: nessuno pagherà i nostri.
- **Statistiche ufficiali già pubbliche:** relazione annuale CGSSE 2025 (presentata alla Camera il 23/6/2026, dai giornali): 1.020 scioperi effettuati (-5,5 %), **626 proclamati nei trasporti** (settore più colpito), TPL da 62 a 101 giornate, scioperi generali da 17 a 33. I ricercatori hanno le relazioni e onData; le assicurazioni, per la regola dello "sciopero già annunciato", si basano sulla data di proclamazione del sindacato/vettore (worldnomads.com, squaremouth.com, rateschaser.com sul 29/5/2026), cioè su documenti ufficiali, non su banche dati private. **Nessun compratore di storici trovato.**

### 2.3 App mobile con avvisi push a pagamento

**App esistenti (dati letti il 10/10/2026):**

| App | Sviluppatore | Prezzo | Numeri | Da quando |
|---|---|---|---|---|
| C'è Sciopero: Scioperi treni / Italian Strikes | Volodymyr Kubiv (singolo) | gratis, **nessun acquisto in-app** | App Store IT: 4,7 su **24 valutazioni**; App Store US: 5 su 6; Google Play: **1.000+ download, 83 recensioni, 4,3** | 2/6/2025 |
| Strike Tracker: Work & Travel | Muhammed Tanriverdi / S3soft (Mechelen, Belgio); Europa, tutti i mezzi | gratis + Pro **4,99 €/mese o 19,99 €/anno** | App Store IT: **nessuna valutazione**; Google Play: **500+ download** | ~9/2025 |
| Scioperi Italia | APORT solutions ltd | gratis | **0 valutazioni** | 17/8/2026 |
| Alert Scioperi Trasporto (storica) | — | 0,79 € | recensione iPhoneItalia, anni fa | — |
| Moovit, Trenord, Trenitalia, Italo | operatori | gratis | avvisi sciopero inclusi | — |

L'app più riuscita, in 16 mesi, ha ~1.000 download Android e 24 valutazioni iOS in Italia: è la misura del mercato "app dedicata". Completamento automatico: «app sciopero» → «app sciopero treni», «app trenitalia sciopero», «c'è sciopero app» (quindi la gente cerca per nome l'app esistente, poca domanda nuova); «italy strike app» → solo «apple italy strike»; «sciopero notifiche push», «sciopero oggi app» → vuoti.

**Costi e regole degli store:**
- Apple Developer Program: «$99 annual membership» (developer.apple.com/programs). Small Business Program: «reduced commission rate of 15% … developers new to the App Store can qualify» (developer.apple.com/app-store/small-business-program).
- Google Play: tassa di registrazione 25 $ una tantum (fonti terze concordi, es. splitmetrics.com 8/2025); nuove commissioni SEE dal 30/6/2026: abbonamenti rinnovabili **10 % + 5 % di commissione di fatturazione** sul primo milione (support.google.com/googleplay/android-developer/answer/112622, letto il 10/10/2026).
- IVA: per l'Italia Apple Distribution International Ltd è «Your commissionaire» (Exhibits to Schedule 2 and 3, 21/8/2025, developer.apple.com) e l'IVA stimata viene tolta prima della commissione; Google «is responsible for charging, collecting, and remitting the VAT» per gli acquirenti UE (support.google.com/googleplay/answer/2850368). Lo sviluppatore fattura ad Apple/Google in reverse charge (art. 7-ter DPR 633/72, ilcommercialistaonline.it, fiscomania.com).
- **Fiscale:** «Occorre aprire partita IVA quando si esercita un'attività abituale e continuativa di vendita» anche con un solo account venditore, codice ATECO 62.01.00, e nel forfettario «riduzione del 35% dei contributi dovuti alla **Gestione Commercianti INPS**» (ilcommercialistaonline.it/vendita-app-ecco-come-mettersi-in-regola). Cioè: lo store non evita il cancello fiscale; lo apre.
- **Automatizzabile?** Claude costruisce una PWA (push web su iOS dalla 16.4, solo se installata nella schermata Home; un fornitore segnala limiti nei PWA UE dopo il DMA: da verificare) o un'app Capacitor. Account Apple e Google, verifica dell'identità, rinnovi, risposte alle recensioni: **solo Massimiliano** (3-4 ore la prima volta, 1 ora/anno).

**Ricavo prudente:** con 1.000-2.000 download/anno (il massimo osservato) e 2-3 % di paganti a 4,99 €/anno: **100-300 €/anno lordi**, meno 99 $/anno di Apple e il 15 %. **Non ora.** La PWA gratuita con push invece costa 0 €, non richiede store e misura la domanda: se in 60 giorni ≥ 300 installazioni e ≥ 100 iscritti push, si riparla di versione a pagamento.

### 2.4 Avvisi email a pagamento per viaggiatori (fase 2)

- **Conversione gratis → pagante:** mediana su beehiiv **0,62 %** («about six of every 1,000 subscribers pay», Press Gazette su analisi beehiiv 2026; top 10 % finanza 20 %); stime Substack per liste da 100 a qualche migliaio: 1-3 % (post di un autore, aneddotico); 5-10 % è il "benchmark" ottimistico suggerito da Substack. Prezzo mediano delle newsletter a pagamento: **10 $/mese o 100 $/anno** (beehiiv, via voxbooster/pressgazette).
- **Avvisi di viaggio a pagamento esistenti:** TripIt Pro 48,99 $/anno (risk alerts incl. scioperi); ExpertFlyer "Disruption Alerts" nel piano da 131,88 $/anno (upgradedpoints.com); e-Travel Alerts 2 $/destinazione/mese (phocuswire, vecchio); Going/Scott's Cheap Flights 49 $/anno (offerte voli, non scioperi). Nessuna newsletter a pagamento solo sugli scioperi trovata.
- **Calcolo:** 500 iscritti × 1-2 % × 10-20 €/anno = **50-200 €/anno**; 5.000 iscritti × 1-2 % × 10-20 € = **500-2.000 €/anno**. Confronto con "tutto gratis + pubblicità": 5.000 iscritti attivi valgono, come traffico di ritorno, 20-50k pagine viste/anno ≈ 200-700 € di pubblicità e di affiliazioni, senza cancello fiscale e senza assistenza clienti. Fino a 5.000 iscritti la lista rende di più gratis.
- **Vincolo pratico:** le iscrizioni passano da Netlify Forms, che nel piano gratuito consuma crediti condivisi («Includes usage credits for production deploys, compute, form submissions…», netlify.com/pricing); fonti terze parlano di 100 invii/mese. Se la lista cresce, va spostata su un servizio gratuito (Brevo: 300 email/giorno gratis; Buttondown: gratis fino a 100 iscritti) prima di qualunque idea a pagamento.

### 2.5 Media e syndication

- The Local Italy (articolo 22/7/2019) rimanda «al sito del Ministero dei Trasporti (solo in italiano)»; Wanted in Rome scrive i propri pezzi mensili ("Italy strikes… October 2025"); Sky TG24 ha costruito lo scioperometro con i dati gratuiti di onData. **Nessun esempio di media che paga un feed o un widget sugli scioperi.** The Local vende abbonamenti ai lettori (2,49 €/mese o 24,99 €/anno al lancio del 2018), non compra dati.
- Cosa ha valore: un **widget gratuito** "strikes this week in Italy" incorporabile con link alla fonte e a noi (CC-BY impone la citazione del MIT; noi chiediamo il link). Valore = backlink e segnalazioni, non denaro. Costruzione: 1-2 ore di Claude.
- RapidAPI: vedi 2.1, resta no. Apify Actor: sì, passivo (già deciso nello studio 7).

### 2.6 Canale di vendita senza email a freddo

- Google Ads B2B: le query B2B non esistono (completamento automatico vuoto), quindi non c'è un annuncio da comprare; i CPC del turismo vanno da 0,23 $ (mediana 2025, twominutereports) a 1,60-2,75 $ (focus-digital), ma su parole senza ricerche non servono.
- LinkedIn organico: richiede post regolari e risposte ai commenti → lavoro continuativo, escluso.
- Resta: pagina "For businesses" sul sito (Google la trova con "italy strike calendar for tour operators" se qualcuno la cerca), Actor Apify (traffico dello store), widget gratuito, directory gratuite di API (publicapis, free-for-dev: inserimento una tantum di Claude). Lavoro di Massimiliano: **0-1 ora** (sì/no su prezzo e sul contratto standard). Realistico per un solista che non vende: sì, ma i numeri sono quelli della tabella (0-6 clienti).

## 3. Le due vie migliori, con piano in 5 passi e soglie

### Via A — "Pro feed" passivo (iCal/JSON/email) + Actor Apify

1. **Ora (Claude, 1 ora):** aggiungere al sito la citazione CC-BY del MIT e una pagina `/for-businesses/` con: cosa c'è (JSON già pubblico, aggiornato due volte al giorno), esempio di iCal per città, modulo «Request the feed» (senza prezzo). Contatore delle richieste nella routine del lunedì.
2. **Entro il 24/11 (Claude, 2 ore):** Actor Apify "Italy transport strikes (MIT register) → JSON/iCal" a pagamento per evento (prezzo 1-3 $/1.000 righe, come gli Actor simili), con link al sito. È il solo posto dove si incassa senza aprire pagamenti propri (Apify paga a bonifico, 20 %).
3. **Soglia 1 (90 giorni dalla pagina):** ≥ 3 richieste vere dal modulo o ≥ 5 utenti paganti dell'Actor → si costruisce il feed per città/settore (iCal + webhook + email settimanale), 4 ore di Claude. Sotto soglia: resta solo l'Actor.
4. **Prezzo (sì di Massimiliano):** 19 €/mese o 149 €/anno per feed, pagamento con un "merchant of record" (Lemon Squeezy/Paddle gestiscono l'IVA) **solo dopo l'apertura del cancello fiscale**; prima, i clienti usano l'Actor Apify.
5. **Verdetto a 12 mesi:** < 300 €/anno → si chiude la pagina e resta l'Actor; ≥ 1.000 €/anno → si aggiunge il feed per aeroporti e il contratto standard in inglese.

### Via B — Lista gratuita → PWA con push gratuita → avvisi a pagamento solo a 5.000 iscritti

1. **Ora (Claude, 2 ore):** costruire l'invio degli avvisi gratuiti agli iscritti del modulo `alerts` (confronto date/luoghi con `vista.json`, invio con Brevo gratis o Gmail con il sì di Massimiliano); spostare le iscrizioni da Netlify Forms a Brevo quando superano 50/mese.
2. **Entro febbraio 2027 (Claude, 3-4 ore):** PWA installabile con push web (città e date scelte dall'utente), gratuita, senza store, con le stesse pagine del sito. Misura: installazioni e iscritti push.
3. **Soglia 1 (60 giorni dalla PWA):** ≥ 300 installazioni e ≥ 100 iscritti push → la PWA resta e si promuove nel sito; sotto, resta solo l'email.
4. **Soglia 2 (≥ 500 iscritti email):** sondaggio nella mail di benvenuto, senza prezzo («vorresti avvisi personalizzati per il tuo viaggio?»); si annota la percentuale di sì.
5. **Soglia 3 (≥ 5.000 iscritti e cancello fiscale aperto):** piano "Trip alerts" a 9,99 €/anno (sotto il prezzo di TripIt Pro, che offre molto di più) con pagamento tramite merchant of record; previsione 1-2 % di paganti = 500-1.000 €/anno. Se i paganti dopo 6 mesi sono < 30, si torna a tutto gratis.

## 4. Cosa NON fare (con il motivo)

- **Non vendere i dati o lo storico**: sono CC-BY e già gratis dal MIT (2014→) e da onData (2025→, ogni giorno). Nessun compratore trovato.
- **Non pubblicare un'app a pagamento adesso**: 99 $/anno, 3-4 ore di Massimiliano, cancello fiscale aperto per 100-300 €/anno; l'app leader gratuita ha 1.000 download in 16 mesi.
- **Non andare su RapidAPI**: 25 %, solo PayPal, pagamenti a 60 giorni, reclami; per un feed B2B serve fattura e interlocutore, non un marketplace.
- **Non proporre il feed a Omio, Trainline, TravelPerk, Navan, compagnie aeree**: hanno Riskline o leggono MIT/ENAC; e sarebbe vendita attiva (email a freddo vietata).
- **Niente Google Ads B2B e niente LinkedIn**: le query non esistono; LinkedIn è lavoro continuativo.
- **Non promettere SLA, tempi di risposta o "dati verificati"**: siamo un lettore del registro (ogni 12 ore, 6 pubblicazioni/mese su Netlify); le revoche possono arrivare in ritardo. Il contratto standard deve dirlo.
- **Non fissare prezzi per gli avvisi email prima dei 500 iscritti** (regola già scritta in STRATEGIA.md) e non venderli prima dei 5.000: sotto, la lista rende di più gratis.
- **Non dimenticare la citazione CC-BY** del MIT sul sito: è l'unica condizione della licenza.

## 5. Nota per i file del progetto (da correggere, non fatto qui)

`italystrikes/NOTE.md` dice che il registro «mostra solo gli scioperi futuri»: vale per la pagina principale e l'RSS (~30 voci), ma la pagina "Ricerca" ha l'archivio dal 1/1/2014 con stato Effettuato/Revocato (POST con `dataInizio`, `dataFine`, `settore=0`, `rilevanza=0`, `stato=`). Serve a: riempire le pagine-mese passate con lo stato finale, e verificare le nostre voci "rimosso dal registro" (se nel MIT risultano "Revocato" possiamo scriverlo con certezza). Zero crediti in più: una lettura al mese nella routine.

## 6. Fonti principali (lette il 10/10/2026)

- scioperi.mit.gov.it/mit2/public/scioperi/ricerca (archivio dal 1/1/2014; tre interrogazioni POST eseguite)
- dati.gov.it/opendata/api/3/action/package_show?id=scioperi-dei-trasporti (CC-BY-4.0; CSV 4.695 righe 2014-2020 su dati.mit.gov.it)
- github.com/ondata/liberiamoli-tutti/tree/main/scioperi (README, scripts/mit.sh); tg24.sky.it/stories/cronaca/scioperometro
- Relazione CGSSE 2025 via lanotiziagiornale.it, italiaoggi.it, avvenire.it (23/6/2026)
- traveladvisory.io/platform/pricing; vendr.com/marketplace/riskline; travel-code.com (guida TRM 5/10/2026); help.tripit.com (Risk Alerts); perk.com/partnership/riskline; enac.gov.it/passeggeri/sciopero
- calendarific.com/pricing; aviationstack.com/pricing
- apps.apple.com/it/app/id6742243477 (C'è Sciopero), id6751948513 (Strike Tracker), lookup id6796648627 (Scioperi Italia); play.google.com (com.kissel.kubiv.strikeNotifier.strike_notifier; com.striketracker); iphoneitalia.com (Alert Scioperi Trasporto)
- suggestqueries.google.com (completamento automatico, hl=en/gl=us e hl=it/gl=it)
- developer.apple.com/programs ($99), developer.apple.com/app-store/small-business-program (15 %), Exhibits to Schedule 2 and 3 (21/8/2025); support.google.com/googleplay/android-developer/answer/112622 (commissioni SEE dal 30/6/2026); support.google.com/googleplay/answer/2850368 (IVA UE)
- ilcommercialistaonline.it/vendita-app-ecco-come-mettersi-in-regola; fiscomania.com/vendita-applicazioni-sul-web-guida-fiscale; flextax.it (reverse charge forfettari)
- pressgazette.co.uk/newsletters/newsletters-2026-prices-retention-churn (beehiiv 0,62 %); stevenscesaon.substack.com (1-3 %); upgradedpoints.com (ExpertFlyer); phocuswire.com (e-Travel Alerts)
- qualitytravel.it (7.100 agenzie, 290 ricettivisti; FTO 1.900 aderenti); ufficiostampa.provincia.tn.it (25/5/2025)
- thelocal.it/20190722; wantedinrome.com (strikes October 2025); thelocal.it/20180918 (membership)
- studio-business/intelaiatura/7-modelli-diversi.md (RapidAPI 25 %, Apify 100-400 $/anno)
- netlify.com/pricing; goodbarber.com e magicbell.com (push web iOS 16.4)
