# Regno Unito, amministrazione quotidiana per council (31/10/2026)

Angolo assegnato: Regno Unito, pratiche di tutti i giorni con dati ufficiali per council o per area: council tax, DVLA, tempi d'attesa (passaporti, NHS), benefit e soglie, parcheggi e multe, scuole.

Prima di partire ho letto: metodo e asticella (`.claude/skills/rete-siti/SKILL.md`), regole del 30-31/10 (`REGOLE-FISSE.md`: fronti nuovi, conta il fatturato, niente lavori a ore) e `ESPLORATE.md`. Molti temi dell'angolo erano già chiusi e **non li ho ripetuti**: council tax per fascia e per council (NO 14/10 e 30/10, salarytax.uk), maggiorazione seconde case (riserva debole 28/10), liste d'attesa NHS (NO, treatcompare), tempi dei passaporti (NO 23/10), attese esame di guida (NO 21/10), date dell'11+ e scuole più richieste (NO), MOT (NO), dentisti e medici NHS (NO), registro dei padroni di casa e licenze HMO (31/10), multe dei parcheggi privati (NO 30/10). Ho cercato i temi rimasti scoperti dentro lo stesso angolo.

Prove raccolte il 31/10/2026: `curl` dal nostro server (stato HTTP, formato, data), API di ricerca e di contenuto di gov.uk, Google Autocomplete con Paese e lingua giusti (`gl=gb`, `hl=en`, client firefox: il numero dopo la query è quante varianti propone, massimo 10), ricerche web per vedere chi c'è oggi in prima pagina.

## In breve

- **Nessuna idea passa l'asticella dei siti nuovi** (voto ≥ 7 e ≥ 5.000 €/anno centrali). La migliore stima centrale, mettendo insieme le idee 1 e 2 in un solo sito, è circa 2.300 €/anno.
- **Il fatto nuovo del giro** è nel Bilancio del 28/10/2026 (gov.uk, letto): il **"Household Energy Payment"**, 100 £ a ogni casa in fascia A-D in Inghilterra, pagati **dai council da gennaio 2027** attraverso la council tax, più 100 milioni £ ai council per aiuti mirati. È la copia del "£150 council tax rebate" del 2022, che fece cercare "quando paga il mio council" per mesi. Oggi l'autocompletamento non lo propone ancora (annuncio di 3 giorni fa); ancora oggi si cerca "150 council tax rebate 2026", quattro anni dopo. Il file ufficiale VOA con il numero di case per fascia e per council (8/9/2026, OGL) permette di scrivere per ogni council "quante case ricevono i 100 £ e quanti soldi arrivano": un numero preciso, del tipo che gli assistenti AI citano. Leeds: 339.450 case in fascia A-D, cioè circa 33,9 milioni £.
- **Il buco vero dell'angolo** sono le **tariffe dei servizi del council**: rifiuti del giardino, ritiro degli ingombranti, disinfestazione, permessi di sosta per residenti e visitatori, passo carrabile (dropped kerb). La domanda è fortissima e fatta **per council** ("garden waste cost wiltshire", "islington council pest control cost", "dropped kerb cost liverpool", "wandsworth visitor parking permit cost": tutte 10 varianti con nomi di council), e **nessun sito mette insieme le tariffe di tutti i council**: ci sono solo le pagine dei singoli council e qualche classifica di giornale una volta l'anno. Però la paga è solo la pubblicità (nessun programma di affiliazione con cifra scritta trovato), e il council stesso è primo per il proprio nome.
- **Il resto dell'angolo è chiuso**: pianificazione per council (planwatch.co.uk ha già una pagina per ogni council con i dati 2026), tariffe urbanistiche dall'8/12/2026 (planninggeek), business rates (licenza ristretta della VOA), targhe personalizzate DVLA (403), Blue Badge (nessun tempo d'attesa ufficiale per council), tempi DVLA (nessun dato ufficiale), ospedali (ERIC 403), case popolari (dato ufficiale che non risponde alla domanda vera).
- **Lezione del giro:** nell'amministrazione britannica per council la domanda c'è sempre, ma chi cerca vuole quasi sempre la pagina del proprio council (ricerca "di navigazione"), e nessuno paga una commissione. Il Regno Unito rende quando c'è un acquisto dietro (assicurazioni, viaggi, case, internet); le pratiche del council da sole valgono solo pubblicità.
- **Prossimo angolo consigliato:** bollette e servizi di casa per codice postale nel Regno Unito con un pagatore vero (copertura e velocità della banda larga per codice postale dai dati aperti Ofcom, cambio di fornitore con commissione scritta), oppure "trasferirsi in un council" con un pagatore per traslochi e notai (Sirelo paga il 50 % del valore di ogni contatto accettato, ma senza una cifra scritta: da approfondire).

## Tabella delle idee

| # | Idea | Dove | Voto | €/anno a 18 mesi (prud. / centr. / ott.) | Ore | Esito |
|---|---|---|---|---|---|---|
| 1 | £100 Household Energy Payment council per council (da gennaio 2027): chi lo riceve, quante case per council, come e quando paga ogni council | sito nuovo (nessun sito della rete adatto) o insieme all'idea 2 | 6,5 | 100 / 500 / 2.000 (quasi tutto una tantum, gennaio-marzo 2027) | 10-15 | RISERVA con data: vale solo se il sito dell'idea 2 si fa entro inizio dicembre |
| 2 | Tariffe dei servizi del council, council per council: rifiuti del giardino, ingombranti, disinfestazione, permessi di sosta, dropped kerb, cassonetti + Band D 2026/27 | sito nuovo "UK council costs" | 6 | 200 / 900 / 3.500 (con l'idea 1: 300 / 1.400 / 5.500) | 40-60 | NO come sito nuovo oggi (sotto l'asticella); riserva se Massimiliano vuole un sito britannico generalista |
| 3 | PIP: percentuale di domande accolte per malattia, riesame, tribunale, tempi d'attesa | sito nuovo | 5 | 150 / 600 / 2.000 | 25-35 | NO (benefitsandwork forte, pubblico fragile, Stat-Xplore con chiave) |
| 4 | Tetti dell'affitto pagato dallo Stato (LHA) per area, 2026/27 e aprile 2027 | sito nuovo | 4 | 50 / 250 / 900 | 8-12 | NO (tariffe ferme dal 2024, pocketwise e i council già in campo) |
| 5 | Ospedali: tariffe del parcheggio per ospedale (NHS ERIC) | sito nuovo | 4 | – | – | RISERVA solo se ERIC diventa leggibile (oggi 403) |
| 6 | Pianificazione per council: percentuale di domande approvate, tempi, tariffe dall'8/12/2026 | – | 3,5 | – | – | NO: planwatch.co.uk e planninggeek coprono già tutto |
| 7 | Blue Badge: tempi d'attesa per council | – | 3 | – | – | NO: domanda forte ma nessun dato ufficiale sui tempi |
| 8 | Case popolari: persone in lista d'attesa per council (LAHS) | – | 3,5 | – | – | NO: il dato ufficiale non risponde a "quanto si aspetta" |
| 9 | DVLA: tempi di lavorazione (patenti, libretto, visite mediche) | – | 3 | – | – | NO: domanda forte, nessun dato ufficiale pubblicato |
| 10 | Business rates dopo la rivalutazione 2026, per immobile e per council | – | 2,5 | – | – | NO: le liste VOA sono sotto "restricted licence" |
| 11 | Targhe personalizzate DVLA: prezzi d'asta | – | 2,5 | – | – | NO: `dvlaauction.co.uk` 403, sito DVLA 000; dominano i commercianti |
| 12 | Multe del council (PCN): percentuale di ricorsi accolti per council | – | 3 | – | – | NO: domanda debole ("pcn appeal success rate" 3 varianti) |

Ipotesi comuni per i calcoli (le stesse dei giri precedenti): pagine viste per visita 1,3-1,5; RPM della pubblicità per pubblico britannico in inglese **8-12 €** ogni 1.000 pagine viste (ipotesi della rete, non ancora misurata: AdSense non è aperto finché il cancello fiscale è chiuso). Le visite sono stime a 18 mesi, non dati. Per confronto, i numeri veri della rete: EsameB1 114 visite a settimana, Visa Income 62 (settimana 19-26/10).

---

## 1. £100 Household Energy Payment council per council (voto 6,5, RISERVA con data)

**Cosa.** Una pagina per council inglese (296 billing authority) con: chi ha diritto (fascia A-D), quante case in fascia A-D ci sono in quel council e quanti soldi arrivano (case × 100 £), come paga quel council (chi paga la council tax con addebito diretto riceve in automatico? gli altri devono fare domanda?), da quando, fino a quando si può chiedere, e il fondo per gli aiuti mirati a chi è in fascia E-H. Più una pagina "Scotland, Wales, Northern Ireland": il Bilancio dice che i governi locali ricevono la loro parte "per fornire un aiuto simile", ancora da decidere.

**Fonte ufficiale (curl).**
- Bilancio 2026, versione HTML: `gov.uk/api/content/government/publications/budget-2026-document/budget-2026-html` **200**. Testo letto: "Household Energy Payment: £100 council tax rebate for bands A-D from January 2027 – Spend -2,625m" (tabella 6.1); "a £100 Household Energy Payment for households in bands A to D in England, alongside £100 million of further funding for local authorities to provide targeted support… This will be delivered by local authorities from January 2027"; "up to 20 million households". Licenza OGL.
- Case per fascia e per council: VOA, "Council Tax: stock of properties, 2026", tabella supplementare `assets.publishing.service.gov.uk/media/6aa92763f1f8d2a39605f7f7/2026_CT_SoP_Supplementary_Table.ods` **200**, ODS, `last-modified` 15/9/2026, dati all'8/9/2026, OGL. Letto: Inghilterra A 6.128.830, B 5.068.220, C 5.730.140, D 4.092.200 (totale A-D **21.019.390**, il governo dice "fino a 20 milioni" perché toglie case vuote ed esenti); Leeds A-D **339.450**.
- Mancano ancora le regole operative (in 2022 uscirono "billing authority guidance" e le assegnazioni per council). Da controllare ogni settimana su gov.uk; ogni council pubblicherà la sua pagina (le pagine dei council si leggono quasi tutte: 9 su 11 provate rispondono 200).

**Domanda.** Oggi zero: "household energy payment" propone solo frasi generiche, "£100 council tax rebate", "council tax rebate 2027", "energy payment january 2027" 0-2 varianti. È normale, l'annuncio è del 28/10. Il precedente è forte: "£150 council tax rebate" ha ancora 7 varianti, compresa "150 council tax rebate 2026", quattro anni dopo; nel 2022 i giornali locali scrivevano un articolo per ogni gruppo di council ("seven councils paying the 150 tax rebate from this week", "the ten Greater Manchester borough councils have shared when…").

**Chi c'è su Google.** Nel 2022: i council, MoneySavingExpert (articoli su addebito diretto e scadenze), i giornali del gruppo Reach con liste di council. Nessuno con una pagina per council e numeri ufficiali per council. Battibile solo sugli assistenti AI e sulle ricerche lunghe ("how many households in leeds get the £100"); sulle ricerche brevi vincono il council e i giornali.

**Chi paga.** Solo pubblicità (AdSense, quando aperto). Nessun affiliato adatto.

**Stima.** È un'ondata una tantum, gennaio-marzo 2027, con una coda fino alla scadenza delle domande. Visite nella stagione: prudente 8.000, centrale 40.000, ottimista 150.000. Pubblicità: 8.000 × 1,3 × 8 / 1.000 = 83 €; 40.000 × 1,3 × 10 / 1.000 = 520 €; 150.000 × 1,4 × 10 / 1.000 = 2.100 €. Totale arrotondato **100 / 500 / 2.000 €**, quasi tutto tra gennaio e marzo 2027. Primi soldi: gennaio 2027, **solo se AdSense è attivo**; senza AdSense l'ondata passa e non lascia niente.

**Ore.** 10-15 (296 pagine da un file ODS, una tabella "come paga il mio council" aggiornata dagli agenti ogni settimana da dicembre a marzo).

**Voto 6,5.** Fonte perfetta, data certa, numero per council che nessuno ha. Ma è un'ondata sola, i giornali sono forti, e nessun sito della rete parla di case britanniche. Ha senso solo come lancio del sito dell'idea 2 (porta citazioni e link nel momento giusto). Da solo non giustifica un sito.

---

## 2. Tariffe dei servizi del council, council per council (voto 6, NO come sito nuovo oggi)

**Cosa.** Un sito "UK council costs" con una pagina per council (circa 360: Inghilterra, Scozia, Galles, Irlanda del Nord) e una per servizio con la classifica di tutti i council: abbonamento ai rifiuti del giardino (2026/27), ritiro degli ingombranti, disinfestazione (topi, vespe, cimici; con lo sconto per chi riceve benefit), permesso di sosta per residenti (primo e secondo veicolo, diesel) e visitatori, passo carrabile (domanda, ispezione, costruzione), cassonetto nuovo, più la council tax Band D 2026/27 e l'aumento sull'anno prima. Aggiornamento annuale a febbraio-aprile, quando i council approvano le tariffe.

**Fonte ufficiale (curl).**
- Pagine tariffe dei council: 9 su 11 provate leggibili (Welwyn Hatfield permessi 200, Epping Forest giardino 200, Amber Valley 200, Midlothian 200, Colchester 200, Birmingham permessi 200, opencouncil.network con le delibere 200); Wandsworth 403, Manchester 403, Glasgow 403: quei council restano fuori o si leggono dai PDF "fees and charges". Esempi letti da pagine ufficiali o delibere 2026/27: giardino Epping Forest 60 £, North Hertfordshire 57 £, North Yorkshire 52 £, Dorset 74 £; dropped kerb Waltham Forest 475 £, Newham 250 £, Sutton 175,10 £, Oldham 58,70 £, Solihull 210 £ dal 1/4/2026; disinfestazione topi St Helens 57,20 £, Colchester 115 £.
- Band D per council: MHCLG "Council Tax levels set by local authorities in England 2026 to 2027", Table 10 (`assets.publishing.service.gov.uk/media/6a02eeeccd2e0e8b5b20b449/Table_10_2026-27.ods`), pubblicata il 25/3/2026, OGL.
- Licenza: le tariffe sono fatti pubblici, ripresi con fonte e data; i testi dei council non si copiano.

**Domanda (autocomplete gb/en).** "garden waste cost" 10 (northampton, wiltshire, edinburgh, north yorkshire), "brown bin cost" 10 (norfolk, 2026, edinburgh, rotherham, kirklees), "green bin cost" 10 (bristol, wiltshire, south glos, liverpool, sheffield), "how much is garden waste collection" 10 (dorset, birmingham, edinburgh, stoke, shropshire), "council pest control cost" 10 (islington, wolverhampton, wakefield, cardiff, barnet…), "bulky waste collection cost" 10 (newham, havant, lambeth), "resident parking permit cost" 10 (edinburgh, wandsworth, ealing, brighton), "visitor parking permit cost" 10 (wandsworth, lambeth, brent, islington…), "dropped kerb cost council" 10 (tameside, dudley, thurrock, luton, birmingham…), "council tax band d" 10 (manchester, glasgow, edinburgh, birmingham, "per month").

**Chi c'è su Google.** Per "[council] + servizio" è primo il council stesso: noi saremmo secondi o terzi nel caso migliore. Per i confronti ("most expensive parking permits", "garden waste charges uk") ci sono solo articoli di giornale e indagini annuali delle assicurazioni (Churchill/Direct Line, dati di aprile 2025), LetsRecycle per i rifiuti, un sito automatico su pages.dev per la disinfestazione a Londra. **Nessuna tabella completa per council**: questo è il buco. La Band D per council è già coperta (salarytax.uk, NO del 14/10): qui sarebbe solo una riga di contorno.

**Chi paga.** Pubblicità. Affiliazioni cercate e non trovate con cifra scritta: Clearabee (ritiro rifiuti) nessun programma trovato; Sirelo (traslochi) paga il 50 % del valore dei contatti accettati, senza cifra; per disinfestazione e passi carrabili nessun programma per editori trovato.

**Stima a 18 mesi.** Visite al mese: prudente 1.500, centrale 5.000, ottimista 15.000 (circa 2.000 pagine, secondi dopo il council). Pubblicità: 1.500 × 1,4 × 12 × 8 / 1.000 = 202 €; 5.000 × 1,4 × 12 × 10 / 1.000 = 840 €; 15.000 × 1,5 × 12 × 12 / 1.000 = 3.240 €. Totale **200 / 900 / 3.500 €/anno**. Con l'ondata dell'idea 1 nello stesso sito: **300 / 1.400 / 5.500 €**. Primi soldi: gennaio 2027 con l'idea 1 (se AdSense è attivo), poi aprile 2027 con le tariffe nuove.

**Ore.** 40-60 per la prima raccolta (360 council × 6 servizi, molte pagine PDF), poi 10-15 ore l'anno di agenti a febbraio-aprile. È tutto lavoro di agenti, niente ore di Massimiliano tranne la creazione del sito su Netlify.

**Voto 6.** Buco vero e domanda vera, ma solo pubblicità e sempre dietro il council. Sotto l'asticella anche nel caso centrale combinato (1.400 €). Non si costruisce come sito nuovo; si riapre se un programma di affiliazione per servizi di casa (disinfestazione, rifiuti, passi carrabili) mostra una cifra scritta, oppure se Massimiliano vuole un sito britannico "generalista" a cui attaccare altre sezioni.

---

## 3. PIP: domande accolte per malattia, riesame, tribunale e tempi (voto 5, NO)

**Fonte (curl).** DWP "Personal Independence Payment statistics to July 2026" (gov.uk 200, pubblicata il 15/9/2026, ODS e XLSX con tempi di lavorazione e percorso del richiedente, OGL). Il dato per malattia è solo in Stat-Xplore: sito 200, **API 401 senza chiave** (serve un account gratuito, cioè un passaggio di Massimiliano). Il Bilancio 2026 cita la revisione Timms ("PIP no longer fit for purpose"): arriverà una riforma, quindi altre ricerche.

**Domanda.** Fortissima: "pip success rate" 10 ("by condition", "mental health", "autism", "fibromyalgia", "depression", "ptsd"…), "pip tribunal success rate" 10 ("2026", "appeal success rate 2026"), "pip waiting times" 10 ("2026", "after assessment 2026").

**Chi c'è.** Benefits and Work (tabella per malattia con i dati di ottobre 2024, articoli a ogni uscita), Citizens Advice, la DWP stessa. Una tabella aggiornata a luglio 2026 batterebbe la loro (ferma a ottobre 2024) sugli assistenti AI.

**Chi paga.** Solo pubblicità; pubblico di persone disabili e con pochi soldi, pubblicità che rende poco; nessun affiliato onesto possibile. La rete ha già scartato temi simili per delicatezza (date dei pagamenti, 14/10).

**Stima.** Visite al mese 1.000 / 4.000 / 12.000; RPM 6 / 8 / 10 € → 1.000 × 1,3 × 12 × 6 / 1.000 = 94 €; 4.000 × 1,3 × 12 × 8 / 1.000 = 500 €; 12.000 × 1,4 × 12 × 10 / 1.000 = 2.016 €. **150 / 600 / 2.000 €/anno** (arrotondato). Ore 25-35.

**Voto 5.** Domanda grande e un buco di aggiornamento, ma concorrente specializzato forte, pubblico fragile, guadagno basso e un account in più da aprire. NO.

---

## 4. Tetti dell'affitto pagato dallo Stato (LHA) per area (voto 4, NO)

**Fonte (curl).** VOA "Local Housing Allowance (LHA) rates applicable from April 2026 to March 2027" (gov.uk 200, 30/1/2026, XLSX 44 KB, OGL). Testo letto: le tariffe dal 1/4/2026 "are the same rates that came into force on 1st April 2024". Il Bilancio 2026 non cita mai "Local Housing Allowance" (0 occorrenze nel testo HTML): con buona probabilità resteranno ferme anche nel 2027/28.

**Domanda.** "lha rates" 10 (birmingham, london, manchester, glasgow, liverpool), "lha rates 2026" 10, "lha rates 2027" 8 ("will lha rates increase 2027").

**Chi c'è.** Strumento ufficiale LHA-Direct, pagine dei council (Hull, Chorley, Swindon, Braintree), gov.scot, e **pocketwise** (sito automatico su pages.dev e .co.uk con le pagine 2026/27).

**Stima.** 50 / 250 / 900 €/anno (pubblicità su pubblico a basso reddito; numeri fermi da 3 anni, nessuna novità da raccontare). Ore 8-12. **Voto 4. NO.**

---

## 5. Parcheggio degli ospedali per ospedale (voto 4, RISERVA tecnica)

**Domanda.** Forte per singolo ospedale: "addenbrookes parking charges" 10 ("for patients", "blue badge", "for a&e"), "royal london hospital parking" 10 ("charges", "free parking"), "hospital parking charges" 10.

**Fonte.** La raccolta ufficiale dei dati sugli edifici NHS (ERIC) è su `digital.nhs.uk`: **403** dal server (come il 30/10); non aggirato. Non ho potuto verificare se contiene le tariffe orarie per paziente. Senza ERIC servirebbero le pagine di circa 200 trust, una per una. Tema sanitario (serve il sì di Massimiliano). Concorrenti: le pagine degli ospedali, JustPark, Parkopedia.

**Voto 4.** Si riapre solo se ERIC diventa leggibile e contiene la tariffa per ospedale.

---

## 6. Pianificazione per council: approvazioni, tempi e tariffe dall'8/12/2026 (voto 3,5, NO)

**Fatti.** Le tariffe nazionali delle domande urbanistiche cambiano l'**8/12/2026** (risposta del governo del 16/7/2026; "planning fees increase december 2026" e "planning fees 2026" 10 varianti). Ma **planninggeek.co.uk** ha già la pagina "Planning fees are changing on 8th December 2026" con tutte le voci, e **planwatch.co.uk** ha già una pagina per ogni council con la percentuale di approvazione "(2026)" dai dati ufficiali PS2 (Lewisham 84,6 %, Barking and Dagenham 66,2 %…). Fatto nuovo trovato sulla strada: il 30/10/2026 il governo ha annunciato "Faster planning decisions as new rules and AI tackle delays" (gov.uk). **NO**: il buco è chiuso da siti automatici.

## 7. Blue Badge: tempi d'attesa per council (voto 3, NO)

**Domanda** forte e per council ("blue badge waiting time" 10: bcp, liverpool, tower hamlets, south glos). **Fonte:** DfT "Blue Badge scheme statistics data tables (DIS)" (gov.uk 200, 19/3/2026, OGL): solo contrassegni validi e rilasciati per council (DIS0105, DIS0108); **nessun tempo di lavorazione**. Senza un dato ufficiale sui tempi la pagina non risponde alla domanda. NO.

## 8. Case popolari: liste d'attesa per council (voto 3,5, NO)

**Domanda** "council house waiting list" 10 (birmingham, london, sheffield, nottingham, "time"). **Fonte:** MHCLG "Local Authority Housing Statistics data returns for 2024 to 2025" (gov.uk, 25/6/2026, OGL): famiglie in lista per council. Ma la gente vuole sapere **quanto si aspetta**, dato che non è ufficiale (lo stimano Shelter e i council con criteri diversi). Pubblico che vale poco in pubblicità. NO.

## 9. DVLA: tempi di lavorazione (voto 3, NO)

**Domanda** forte: "dvla processing times" 10 ("medical 2026", "medical 2026 gov uk"), "dvla medical waiting times" 10, "dvla waiting times" 10 (rinnovo, libretto V5C, foglio rosa). **Fonte:** nessuna serie ufficiale trovata su gov.uk (ricerche API su "DVLA processing times", "DVLA medical statistics": solo pagine di servizio; 4 percorsi provati 404). Senza un numero ufficiale aggiornato si scrivono solo stime prese dai forum. NO.

## 10. Business rates dopo la rivalutazione 2026 (voto 2,5, NO)

**Domanda** "business rates 2026" 10 ("multipliers", "calculator", "transitional relief"); il Bilancio 2026 alza la soglia del Small Business Rate Relief e congela i rates di negozi, pub e ristoranti per due anni da aprile 2027 (79 citazioni nel testo). **Fonte:** le liste della VOA si scaricano (`voaratinglists.blob.core.windows.net/html/rlidata.htm` 200) ma "are only available under our **restricted licence** terms and conditions": non si possono ripubblicare liberamente. Strumento ufficiale per immobile (`tax.service.gov.uk/business-rates-find` 200) e consulenti in prima pagina. NO.

## 11. Targhe personalizzate DVLA (voto 2,5, NO)

**Domanda** molto forte ("dvla auction results" 10, "private number plate value" 10), ma `dvlaauction.co.uk` risponde **403** e il sito DVLA delle targhe **000**: non aggirato. Prima pagina dei commercianti di targhe. NO.

## 12. Multe del council: ricorsi accolti per council (voto 3, NO)

"pcn appeal success rate" 3 varianti, "parking fine appeal success rate" 4: domanda debole. La risposta che la gente vuole ("conviene fare ricorso?") è un consiglio legale caso per caso; MoneySavingExpert e i forum sono primi. NO.

---

## Cosa farei

1. **Niente sito nuovo da questo angolo.** Nessuna idea arriva a 5.000 €/anno centrali, neanche mettendo insieme le idee 1 e 2.
2. **Unica decisione con una data:** se Massimiliano vuole comunque un sito britannico "generalista" (idee 1 + 2, 50-75 ore di agenti, zero euro, un passaggio su Netlify), va deciso **entro metà novembre**, per essere online prima che i council comunichino come pagano i 100 £ (da gennaio 2027). Senza AdSense attivo l'ondata di gennaio non frutta nulla: in quel caso non conviene.
3. **Da segnare in ESPLORATE** (lo fa chi aggiorna il file): il Household Energy Payment (fatto nuovo del 28/10/2026), il buco delle tariffe dei servizi per council, e i NO di questo giro (PIP, LHA, pianificazione, Blue Badge, case popolari, DVLA, business rates, targhe, PCN; ospedali in riserva tecnica).
4. **Prossimo angolo:** servizi di casa per codice postale nel Regno Unito con un pagatore a cifra scritta (banda larga dai dati aperti Ofcom, cambio di fornitore), oppure "trasferirsi in un council" con un pagatore per traslochi e notai.

## Limiti

- Non vedo i volumi di ricerca, solo il numero di varianti dell'autocompletamento.
- Il RPM britannico è un'ipotesi della rete, non un dato misurato.
- Le regole operative del Household Energy Payment non sono ancora uscite: le date e i modi di pagamento per council sono da verificare quando la guida del governo sarà pubblicata.
- `digital.nhs.uk`, `dvlaauction.co.uk`, Stat-Xplore (API) e alcune pagine dei council (Wandsworth, Manchester, Glasgow) non sono leggibili dal server; non ho cercato di aggirare i blocchi.

## Fonti principali

- Bilancio 2026, testo HTML: https://www.gov.uk/government/publications/budget-2026-document/budget-2026-html
- VOA, Council Tax stock of properties 2026: https://www.gov.uk/government/statistics/council-tax-stock-of-properties-2026
- MHCLG, Council Tax levels 2026 to 2027: https://www.gov.uk/government/statistics/council-tax-levels-set-by-local-authorities-in-england-2026-to-2027
- DWP, PIP statistics to July 2026: https://www.gov.uk/government/statistics/personal-independence-payment-statistics-to-july-2026
- VOA, LHA rates 2026-2027: https://www.gov.uk/government/publications/local-housing-allowance-lha-rates-applicable-from-april-2026-to-march-2027
- DfT, Blue Badge data tables (DIS): https://www.gov.uk/government/statistical-data-sets/blue-badge-scheme-statistics-data-tables-dis
- MHCLG, Local Authority Housing Statistics 2024 to 2025: https://www.gov.uk/government/statistical-data-sets/local-authority-housing-statistics-data-returns-for-2024-to-2025
- VOA, condizioni delle liste dei business rates: https://voaratinglists.blob.core.windows.net/html/rlidata.htm
- Concorrenti: https://planwatch.co.uk/planning-approval-rates/lewisham , https://www.planninggeek.co.uk/applications/fees/ , https://www.benefitsandwork.co.uk/personal-independence-payment-pip/success-rates , https://pocketwise.co.uk/benefits/housing/lha-rates-2026-27/
- Programma Sirelo per affiliati: https://sirelo.co.uk/for-affiliates/
- Precedente 2022: https://www.moneysavingexpert.com/news/2022/05/150-council-tax-rebate-direct-debit-may/
