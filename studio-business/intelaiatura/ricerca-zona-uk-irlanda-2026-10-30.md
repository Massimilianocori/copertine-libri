# Ricerca di zona: Regno Unito e Irlanda (30/10/2026)

Richiesta di Massimiliano: "il mondo è molto più grande, ci sono più opportunità e tu non le stai trovando". Obiettivo: idee da voto 8-9 per siti o sezioni **automatici** (script Python su dati ufficiali, pubblicati su Netlify), pagati da AdSense e da affiliazioni con nome. Zona assegnata: **Regno Unito e Irlanda**. Altri ricercatori lavorano su cloni di EsameB1 (esami e pratiche per stranieri), su "numeri ufficiali che spostano soldi" e sugli USA: qui non li tocco.

Letti prima: `ESPLORATE.md` per intero (493 righe) e i tre rapporti `ricerca-profonda-2026-10-28-*.md`. Non ho rivalutato da capo nicchie già chiuse: dove un fatto nuovo cambia un voto lo scrivo (sez. 4).

---

## 0. Risposta in breve

**Nessuna idea arriva a 8 con un voto severo.** La lezione della giornata è netta: **il Regno Unito è il mercato più "coltivato" visto finora**. Per quasi ogni dato aperto britannico (dentisti NHS, medici di base, scuole, case di riposo, aree protette, sussidi per l'affitto) c'è già almeno un sito automatico che fa una pagina per città o per scuola, spesso nato nel 2025-2026 (`dentalchoices.org`, `alldentists.co.uk`, `allhealthandcare.co.uk`, `findmyschool.uk`, `schoolsinfo.uk`, `catchment.school`, `treatcompare.com`, `heritagecheck.co.uk`, `comparevetpricing.co.uk`). Il buco vero, con fonte aperta e domanda provata, sta **in Irlanda**, dove nei risultati ci sono solo notizie, PDF e due marchi immobiliari.

| # | Candidata | Dove | Voto | 18 mesi €/anno (prudente – ottimista) | Prima entrata | Ore |
|---|---|---|---|---|---|---|
| 1 | **Irlanda città per città: affitti ufficiali (RTB, 446 località), prezzi di vendita (registro PPR, 814.414 vendite), mediana per zona Eircode (CSO), classifiche "cheapest/best places to live in Ireland"** | sito nuovo (oltre il tetto) | **7** | 800-1.800 – 5.000/6.000 | AdSense 2°-3° mese; Wise e AA Ireland dopo l'iscrizione | 22-32 |
| 2 | **Aggiunta a Visa Income: persone arrivate in Irlanda per nazionalità, mese per mese (PPSN, CC BY 4.0)** | sezione "quanti si trasferiscono" già proposta il 28/10 | **7** (come aggiunta) | 100-400 – 1.000 | 1° mese dopo la pubblicazione (traffico da assistenti) | 3-5 |
| 3 | **Prezzi dei veterinari per catena e per città (ordine CMA del 22/9/2026)** | sito nuovo | **6,5 oggi; 8 condizionato** (vedi 2.3) | 1.000-2.500 – 8.000/10.000 | non prima di gennaio 2027 | 30-45 |
| 4 | Permessi di lavoro irlandesi rilasciati e rifiutati per nazionalità (DETE) | aggiunta a Visa Income | 6 (licenza "personal use") | 100-300 | – | 2-4 |
| 5 | Promossi alla revisione NCT per centro e per modello (Irlanda) | sito nuovo | 6 (fonte 403) | 500-1.500 | – | 15-20 |
| 6 | Classifiche delle scuole scozzesi per council (dati ACEL) | sito nuovo | 6 (file per scuola non trovato) | 500-2.000 | – | 15-25 |

**Cosa farei.** (a) La n. 2 subito, alla prossima pubblicazione di Visa Income: 3-5 ore, fonte aperta, domanda già in autocompletamento ("how many indians in ireland 2026"). (b) La n. 1 solo con il sì di Massimiliano (sito nuovo oltre il tetto), meglio a gennaio-febbraio 2027, quando escono i dati RTB del 2026 e ripartono le ricerche "rent/house prices 2027". (c) La n. 3 resta in riserva con due date in calendario: 23/12/2026 (prime liste prezzi delle grandi catene) e settembre 2027 (dati RCVS ai siti di confronto approvati).

---

## 1. Metodo e limiti

- **Domanda**: autocompletamento di Google (`suggestqueries`, `gl=uk` o `gl=ie`, `hl=en`), varianti per città, contea, catena. Numero di varianti tra parentesi (massimo 10).
- **Fonte**: `curl` dal server il 30/10/2026: stato HTTP, formato, file scaricato e aperto, licenza letta prima del voto (regola del 23/10).
- **Concorrenza**: ricerca web (motore con risultati USA, quindi i risultati britannici e irlandesi sono indicativi) e apertura dei siti concorrenti con `curl`.
- **Voto** (stessa griglia delle ricerche precedenti): domanda 0-3 · buco nei risultati 0-2 · fonte leggibile e riusabile 0-2 · valore del pubblico e chi paga 0-2 · rischi e ore 0-1.
- **Limiti**: non vedo i volumi di ricerca, solo le varianti; le commissioni di AA Ireland e di Petplan non sono lette sulla scheda della rete (servono le iscrizioni di Massimiliano). `rsa.ie`, `ncts.ie`, `digital.nhs.uk` rispondono 403 dal server; non ho cercato di aggirare i blocchi.

---

## 2. Le candidate

### 2.1 Irlanda città per città: affitti, prezzi venduti, posti più economici — voto 7

**Domanda (gl=ie).** "average rent in" → dublin, galway, cork, limerick, waterford, kilkenny, killarney, mayo, "dublin for a room" (10); "average rent in limerick" (10: city, per month, student, room); "how much to rent a house in limerick"; "house prices in" → ireland, dublin, galway, cork, wicklow, waterford, west cork (10); "house prices in mullingar" con "average house price in mullingar"; "house prices greystones" con "sold prices greystones"; "property price register" → dublin, cork, galway, limerick, waterford, sligo, kilkenny (10); "average house price in meath" con navan e donegal; "house value by eircode" e "cso house prices by eircode" (6). Domanda sulle classifiche: "cheapest places to live in ireland" (10, con 2026, "near dublin", "cheapest city"), "best places to live in ireland" (10, con **"as an american"**, "for expats", "for retirees", "for families", "near dublin"), "safest places to live in ireland" (10), "commuter towns dublin" (6). A livello di piccolo paese la domanda è sottile ("average rent in naas" 3, "average rent in drogheda" 2).

**Fonti (tutte 200 dal server, licenze aperte).**
- **Affitti RTB** tramite la banca dati CSO (API PxStat, tabella `RIQ02`, JSON-stat 7,7 MB, aggiornata il 14/5/2026, copyright RTB, dati CSO in CC BY 4.0): 446 località (contee, città, paesi, quartieri di Dublino) × 7 tagli di camere × 6 tipi di casa × trimestre dal 2007Q4 al 2025Q4. 306 località hanno il valore del 2025Q4. Esempi letti: Greystones 2.354 € al mese (2.273 un anno prima), Naas 1.922 (1.785), Galway City 1.885 (1.737), Drogheda (parte Meath) 1.831, Navan 1.422, Mullingar 1.243, contea di Kilkenny 1.216.
- **Registro dei prezzi PPR** (`propertypriceregister.ie`, file unico `PPR-ALL.zip` 19 MB, CSV di 111 MB): 814.414 vendite dal 2010 al **23/10/2026**, con indirizzo, contea, Eircode (35.176 vendite del 2026 su 46.020 hanno l'Eircode), prezzo, nuova o usata. Licenza CC BY 4.0 (scheda su data.gov.ie). Mediane 2026 calcolate dal file: Greystones 605.000 € (140 vendite), Naas 470.000 (377), Navan 382.630 (364), Mullingar 340.000 (347).
- **Mediana ufficiale per zona Eircode** (CSO `HPM04`, 16 MB, aggiornata il 13/10/2026): 140 zone di instradamento Eircode × mese fino ad agosto 2026 × nuove/usate × tipo di compratore (**prima casa**, ex proprietario, investitore). CSO `HPM05`: lo stesso per contea e città.

**Concorrenza.** Su "average rent kilkenny" e "average rent in galway 2026" solo PDF dell'RTB e dell'ESRI, radio e giornali locali (Kilkenny People, KCLR, Limerick Leader), il rapporto trimestrale di daft.ie in PDF. Su "median house price wicklow 2026" solo radio locali (East Coast FM), pagine singole di myhome.ie per ogni vendita, il comunicato CSO, `rightplace.ie` (piccolo, mescola contee). Su "cheapest places to live in ireland 2026": guide commerciali (youroverseashome, uhomes, amberstudent, escapefromusa) e due siti automatici fatti con Numbeo (`relocate-ireland.pages.dev`, `wheretoemigrate.pages.dev`), **nessuno con i dati ufficiali per paese**. Il buco c'è: nessuna pagina "affitto ufficiale e prezzo venduto a [paese]" con fonte e data.

**Chi paga.** AdSense (pubblico irlandese e, nelle pagine "living in Ireland", americano e britannico). **AA Ireland** ha il programma di affiliazione per assicurazione auto e casa su **Tradedoubler** (commissione non letta: serve l'iscrizione). **Wise** (già nelle liste del 17/10: circa 10 £ per nuovo cliente) per chi si trasferisce dagli USA o dal Regno Unito. Nessun programma irlandese di mutui con commissione pubblica trovato: è il limite del voto.

**Pagine.** Una per località (≈ 300 con dati): affitto ufficiale per camere e tipo, andamento dal 2008, prezzo mediano venduto nell'ultimo anno, ultime vendite del registro, zona Eircode e mediana per la prima casa. Pagine-classifica rigenerate ogni trimestre: "cheapest places to rent in Ireland (official RTB data, Q4 2025)", "cheapest commuter towns for Dublin", "where first-time buyers pay least". Prima riga di ogni pagina con numero, periodo, fonte e data, tabelle in HTML semplice (regola della sez. 7 del rapporto "assistenti").

**Stima.** Mercato piccolo (5,4 milioni di abitanti), ma domanda costante e senza stagione. 12 mesi: 200-1.500 €. 18 mesi: prudente 800-1.800 €/anno, ottimista 5.000-6.000 (con le pagine "as an american" e Wise attivo). Prima entrata: AdSense al 2°-3° mese. **Ore 22-32** (lettore JSON-stat e CSV nuovi; generatore di pagine riusato).

**Voto 7**: domanda 2 (forte per contee e città, sottile per i paesi) · buco 1,5 · fonte 2 · valore 1 (AdSense irlandese, AA Ireland e Wise senza cifra letta) · rischi e ore 0,5 (sito nuovo oltre il tetto). Non arriva a 8 perché manca un pagatore con cifra provata e perché il mercato è piccolo.

### 2.2 Aggiunta a Visa Income: arrivi in Irlanda per nazionalità (PPSN) — voto 7 come aggiunta

**Fatto nuovo.** Il Dipartimento della Protezione Sociale pubblica ogni mese i **numeri PPSN assegnati per Paese** (file `20260915_PPSN_registrations_by_year_month_and_country.xlsx`, 200, 107 KB, 3.822 righe: Paese × mese da gennaio 2023 ad **agosto 2026**; scheda data.gov.ie aggiornata il 28/9/2026, **CC BY 4.0**). Il PPSN serve a chiunque arrivi per lavorare o studiare: è il miglior indicatore mensile di "quanti [nazionalità] arrivano in Irlanda".

**Domanda (gl=ie).** "how many indians in ireland" (10: 2026, 2025, percentage, today, "statistics"), "how many brazilians in ireland" (6, con 2026).

**Dove va.** Nella sezione "Quanti [nazionalità] si trasferiscono in [Paese]" già proposta (voto 7,5) nella ricerca degli assistenti del 28/10: aggiunge l'Irlanda con un dato mensile che nessun concorrente mette in tabella per nazionalità. **Stima** 100-400 €/anno (1.000 ottimista); vale soprattutto per la citabilità. **Ore 3-5.**

### 2.3 Prezzi dei veterinari per catena e per città (Regno Unito) — 6,5 oggi, 8 condizionato

**Fatto nuovo (il più grande della giornata).** L'autorità della concorrenza (CMA) ha chiuso l'indagine sui veterinari: decisione finale 24/3/2026, **ordine firmato il 22/9/2026** e in vigore dal 23/9/2026. Gli studi devono pubblicare una **lista prezzi standard** (visite, vaccini, sterilizzazioni, esami, prescrizioni, cremazione); limite alla tassa sulla prescrizione (circa 21 £). Date riportate da più guide (da verificare sul testo dell'ordine): **grandi gruppi entro il 22/12/2026**, piccoli entro il 22/3/2027; il registro RCVS "Find a Vet" deve essere pronto a ricevere i prezzi entro **giugno 2027**, gli studi li mandano entro **settembre 2027**, e l'RCVS li **condivide con i siti di confronto approvati** (con aggiornamenti regolari e diritto di ricorso per chi viene rifiutato).

**Domanda (gl=uk), fortissima e per città e per catena.** "cheapest vets in" → swindon, hull, sheffield, wakefield, worcester, darlington, wigan, nottingham, stafford, cheltenham (10); "vet price comparison" (9: site, uk, near me); "cat neutering cost" (pets at home, pdsa, uk); "dog spay cost" (vets4pets); "animal health certificate cost" (vets4pets, medivet, pets at home, london, manchester); "pet cremation cost" (pdsa, vets4pets, medivet); "cma vets" (10: order, final report).

**Concorrenza.** `comparevetpricing.co.uk` è già online con pagine per città, procedure e gruppi (200, 131 KB) prima ancora che i dati esistano; `vetpricecomparison.co.uk` ha già chiuso ("This site is no longer operating"). La corsa è cominciata e dal 2027 risponderà anche il registro ufficiale.

**Chi paga.** Assicurazioni per animali: PDSA su Awin 25 £ a polizza (al lancio), Everypaw circa 20 £ (Awin), Petplan circa 10 £ (dato di un elenco, non verificato), Frank 8-10 %. Più AdSense britannico. È il pubblico giusto al momento giusto (chi confronta il prezzo della sterilizzazione sta prendendo un animale).

**Perché 6,5 oggi.** Fino a settembre 2027 la fonte non è un file ufficiale unico: sono le pagine prezzi di migliaia di studi (sei grandi gruppi coprono circa la metà), da leggere sito per sito, con formati da verificare. **Diventa 8** se (1) a gennaio 2027 le liste dei sei gruppi si leggono da script in formato stabile, e (2) nel 2027 Massimiliano chiede all'RCVS lo stato di "approved third party" (una richiesta di licenza, non un'email commerciale). Voto oggi: domanda 3 · buco 1 · fonte 0,5 · valore 1,5 · rischi 0,5.

### 2.4 Riserve minori

- **Permessi di lavoro irlandesi rilasciati e rifiutati per nazionalità** (DETE, `employment-permits-by-nationality-2026.xlsx`, 200): nel 2026 29.989 rilasciati e 3.348 rifiutati; India 9.120/769 (7,8 % rifiutati), Filippine 9,6 %, Brasile 14,3 %, Cina 12,1 %, Pakistan 9,7 %, Sudafrica 12,3 %, USA 3,9 %. È il dato che il 20/10 mancava ("Rifiuti dei visti per nazionalità in Irlanda: NO, il Dipartimento non pubblica"): **fatto nuovo per i permessi di lavoro**, non per i visti. Ma la pagina copyright del Dipartimento dice "personal use only" (con fonte se si diffonde): licenza da chiarire. Domanda debole ("work permit refusal ireland" 1 variante). **6**, aggiunta di 2-4 ore solo se la licenza si chiarisce. L'elenco per azienda (7.743 datori di lavoro) è già ripubblicato ogni mese da `irishtalents.com`: NO.
- **Promossi alla revisione NCT per centro e per modello** (Irlanda): domanda vera ("nct pass rates by centre", "nct pass rate by car", "galway/dublin/sligo nct centre failure rates", "kells/fonthill nct pass rate"), nei risultati solo giornali e radio locali; ma `rsa.ie` e `ncts.ie` 403 dal server e su data.gov.ie i file aperti (CC BY 4.0) si fermano al 2016. **6**; si riapre se `rsa.ie` si legge da GitHub Actions. Paga AA Ireland (auto).
- **Classifiche delle scuole scozzesi per council**: "primary school league tables scotland full list 2026" (con pdf), "secondary school league tables scotland 2026"; nei risultati solo The Scotsman (un articolo per council) e il Sunday Times a pagamento, che usano la banca dati ufficiale ACEL. Il file per scuola non l'ho trovato: le tabelle pubblicate (`ACEL 2425 supplementary tables`, 200) arrivano al council × fascia di deprivazione; il file "School level summary statistics 2025" (200, 2.447 scuole) ha alunni e insegnanti, non i risultati. **6**; si riapre se il file per scuola esiste.

---

## 3. Scartate, con la prova (30/10/2026)

| Famiglia | Prova | Voto |
|---|---|---|
| Dentisti NHS che accettano pazienti, per città | Domanda enorme (10 città: london, manchester, leeds, bristol, sheffield, swindon, derby…); dati NHS in OGL anche per uso commerciale (aggiornare entro 7 giorni), pagine risultati 200. Ma `dentalchoices.org` controlla il sito NHS ogni giorno e ha pagine per paese ("2174 dentisti su 10.981"), `alldentists.co.uk` ha il cruscotto per città | 4,5 NO |
| "Best GP surgery in [città]" (sondaggio GPPS) | 10 città in autocompletamento, ma `allhealthandcare.co.uk` ha già "Best GP practices in Eastbourne by Patient Experience (GPPS)" per distretto e contea, più `caredb.co.uk` e i giornali locali | 4 NO |
| Scuole inglesi più richieste (domande e offerte per scuola, DfE) | Fonte perfetta: CSV per scuola di 248.108 righe (prime scelte, posti, offerte, anni dal 2014, pubblicato 18/6/2026, OGL); domanda per council ("most oversubscribed schools in kent/liverpool/london", "oversubscribed schools sheffield/derbyshire/dudley"). Ma `findmyschool.uk` (scheda "demand"), `schoolsinfo.uk`, `catchment.school`, `propertistics.co.uk`, `crystalroof.co.uk` usano già questi numeri per ogni scuola | 5 NO |
| Tariffe delle case di riposo per council | "lancashire/suffolk/essex county council care home rates 2026" in autocompletamento; `treatcompare.com` ha già "Residential care home in Lancashire: cost per week" per contea | 4 NO |
| Local Housing Allowance per città | "lha rates birmingham/bristol/bolton/leeds/luton…" (20 varianti), ma councils e gov.uk rispondono con la tabella; tariffe congelate dal 2024; pubblico a bassa pubblicità | 3,5 NO |
| Aree protette, alberi protetti, Article 4 per codice postale | Domanda forte ("conservation area checker by postcode" 10); dati `planning.data.gov.uk` OGL ma incompleti; `heritagecheck.co.uk` e `housecheckup.co.uk` già primi con API e pagine per area | 3,5 NO |
| Rischio alluvione per codice postale (UK) | Risposta per indirizzo, servizio ufficiale gov.uk primo; stesso verdetto delle domande "per indirizzo" | 3 NO |
| Multe dei parcheggi privati per operatore (ParkingEye, Euro Car Parks, UKPC) | Domanda enorme ("should i pay", "appeal"), ma la risposta è consulenza legale; MoneySavingExpert e forum primi; nessun pagatore | 4 NO |
| Tassa comunale 2027 per council | Domanda forte ("wandsworth/edinburgh/bromley/merton/croydon council tax 2027"): **conferma il NO del 14/10** (salarytax.uk e simili per council e fascia) | NO confermato |
| Durezza dell'acqua in Irlanda | Domanda ("water hardness by postcode ireland", "map ireland"), ma nessun dato ufficiale per zona nella Repubblica (solo una mappa geologica del 2015); l'Irlanda del Nord sì, ma è piccola | 3 NO |
| Aziende irlandesi che sponsorizzano permessi | Domanda ("companies in ireland that sponsor visas", "ireland work permit company list"), ma `irishtalents.com` pubblica già i dati DETE ogni mese | 4 NO |
| Rette degli asili per contea (Irlanda) | "creche fees by county" 0 varianti; solo "dublin" e "ireland" | 3 NO |
| Vincoli di zonizzazione, tasse sulla casa, bollette dell'acqua UK, energia | Un numero o una tabella sola dall'ente (Local Property Tax, aumenti Ofwat per compagnia, tetto Ofgem), MoneySavingExpert primo | 2,5-3 NO |

---

## 4. Idee già valutate: cosa cambia con i fatti di oggi

| Idea (studio) | Prima | Fatto nuovo | Ora |
|---|---|---|---|
| Rifiuti dei visti per nazionalità in Irlanda (20/10) | NO 4,5 | Il DETE pubblica **permessi di lavoro** rilasciati e rifiutati per nazionalità (2026) | resta NO per i visti; permessi di lavoro **6** con licenza da chiarire (2.4) |
| Promossi all'esame di guida per centro, Irlanda (16/10) | NO | Non cambia; la revisione NCT è un'altra famiglia | NCT **6** in riserva (2.4) |
| Classifiche delle scuole per città, Regno Unito (18/10, "non approfondita") | – | Inghilterra già coperta da 5 siti automatici; la Scozia ha solo giornali | Inghilterra NO; Scozia **6** in riserva |
| Pet travel rules (studio 1) | RISERVA | Autocompletamento "pet passport uk 2027/update" e "animal health certificate cost vets4pets/medivet": il costo del certificato entrerà nelle liste prezzi CMA solo se rientra nei servizi standard | resta RISERVA; al massimo pagine dentro la n. 3 |
| Liste d'attesa NHS (19/10), classi energetiche (19/10), going rate (27/10), seconde case (28/10) | NO / riserva debole | Nessun fatto nuovo | invariate |

---

## 5. Perché nella zona non c'è un 8 (e cosa lo darebbe)

1. **Regno Unito: il buco si chiude in mesi, non in anni.** Ogni nuovo obbligo di pubblicazione (veterinari, dentisti, sondaggi NHS) produce un sito automatico prima ancora che i dati siano completi (`comparevetpricing.co.uk` esiste da prima del 22/12/2026). Per entrare servono o una fonte che altri non hanno (lo stato di "approved third party" RCVS) o un momento preciso.
2. **Irlanda: il buco c'è, i pagatori sono pochi.** Fonti aperte ottime (CSO, PPR, PPSN, tutte CC BY 4.0) e risultati fatti di PDF e radio locali; ma i programmi di affiliazione irlandesi con cifra pubblica sono rari (trovato solo AA Ireland su Tradedoubler, commissione da leggere).
3. **Cosa porterebbe a 8**: (a) per la n. 1, una commissione letta di AA Ireland o di un mediatore di mutui irlandese, più ≥ 300 impressioni al mese a 60 giorni; (b) per la n. 3, le liste prezzi dei sei grandi gruppi leggibili da script a gennaio 2027 e la richiesta RCVS nel 2027.

---

## 6. Righe da aggiungere a ESPLORATE (non le ho scritte io: questo rapporto tocca solo questo file)

| Nicchia | Esito | Studio |
|---|---|---|
| **Irlanda città per città: affitti RTB (446 località, CSO RIQ02), vendite PPR (814.414, fino al 23/10/2026), mediana per zona Eircode e prima casa (CSO HPM04), classifiche "cheapest/best places to live in Ireland"** | **PASSA sotto l'asticella** (voto 7; 800-1.800 €/anno prudente, 5-6k ottimista; 22-32 ore; sito nuovo oltre il tetto, AA Ireland su Tradedoubler e Wise da iscrivere) | ricerca-zona-uk-irlanda-2026-10-30 |
| **PPSN assegnati per nazionalità e mese (Irlanda, CC BY 4.0, fino ad agosto 2026)** | **PASSA** come aggiunta (voto 7; 3-5 ore) alla sezione "quanti si trasferiscono" di Visa Income | ricerca-zona-uk-irlanda-2026-10-30 |
| **Prezzi dei veterinari per catena e città (ordine CMA 22/9/2026; liste dei grandi gruppi dal 22/12/2026, dati RCVS ai siti approvati da settembre 2027)** | **RISERVA alta** (6,5; 8 condizionato a liste leggibili e approvazione RCVS); `comparevetpricing.co.uk` già in campo | ricerca-zona-uk-irlanda-2026-10-30 |
| Permessi di lavoro irlandesi rilasciati/rifiutati per nazionalità (DETE) | RISERVA (6): licenza "personal use only" da chiarire | ricerca-zona-uk-irlanda-2026-10-30 |
| Promossi NCT per centro e modello (Irlanda) | RISERVA (6): `rsa.ie` 403, dati aperti fermi al 2016 | ricerca-zona-uk-irlanda-2026-10-30 |
| Classifiche delle scuole scozzesi per council (ACEL) | RISERVA (6): file per scuola non trovato | ricerca-zona-uk-irlanda-2026-10-30 |
| Dentisti NHS che accettano pazienti; migliori medici di base per città; scuole inglesi più richieste; tariffe delle case di riposo per council; LHA per città; aree protette per codice postale; rischio alluvione UK; multe dei parcheggi privati; durezza dell'acqua in Irlanda; aziende irlandesi che sponsorizzano permessi; rette degli asili per contea | NO (prove in sez. 3) | ricerca-zona-uk-irlanda-2026-10-30 |

---

## 7. Fonti lette il 30/10/2026 (stato HTTP dal nostro server)

- Affitti RTB: `ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/RIQ02/JSON-stat/2.0/en` (200, 7,7 MB) e `RIA02` (200).
- Prezzi CSO: `.../HPM04/...` (200, 16 MB), `.../HPM05/...` (200), `.../HPM09/...` (200).
- Registro PPR: `propertypriceregister.ie/website/npsra/ppr/npsra-ppr.nsf/Downloads/PPR-ALL.zip/$FILE/PPR-ALL.zip` (200, 19 MB); licenza su `data.gov.ie` (CC BY 4.0).
- PPSN: `assets.gov.ie/static/documents/61551b04/20260915_PPSN_registrations_by_year_month_and_country.xlsx` (200).
- DETE: `enterprise.gov.ie/en/publications/employment-permit-statistics-2026.html` (200) e i file `employment-permits-by-nationality-2026.xlsx`, `employment-permits-issued-to-companies-2026.xlsx` (200); pagina `enterprise.gov.ie/en/copyright/` (200).
- NCT: `rsa.ie` 403, `ncts.ie` 403; `data.gov.ie` 4 schede NCT (2015-2016, CC BY 4.0).
- DfE domande e offerte: `explore-education-statistics.service.gov.uk/find-statistics/primary-and-secondary-school-applications-and-offers/2026-27` (200), zip dei file (200, 10,7 MB).
- Scozia: `gov.scot` tabelle ACEL 2024-25 (200, 3,2 MB) e "School level summary statistics 2025" (200).
- NHS: `nhs.uk/service-search/find-a-dentist/results?location=...` (200), termini `nhs.uk/our-policies/terms-and-conditions/` (200, OGL anche commerciale), `api.nhs.uk` 401, `digital.nhs.uk` 403.
- Dati di pianificazione: `planning.data.gov.uk/dataset.json` (200, OGL).
- Concorrenti aperti: `dentalchoices.org` (200), `alldentists.co.uk` (200), `comparevetpricing.co.uk` (200), `vetpricecomparison.co.uk` (200, "no longer operating").
- Veterinari: decisione CMA 24/3/2026 e ordine 22/9/2026 da pagine gov.uk e guide di settore (date da confermare sul testo dell'ordine); commissioni assicurazioni animali da Awin (PDSA 25 £ al lancio) e da elenchi di terzi (non verificate).
