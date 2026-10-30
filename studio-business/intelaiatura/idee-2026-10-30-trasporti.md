# Caccia serale del 30/10/2026: treni, trasporti pubblici e viaggi

Settore assegnato: treni, trasporti pubblici e spostamenti per turisti e stranieri, in Europa e nel mondo. Multe e convalida per città, city card, bagagli e animali sui treni, sconti per età, apertura delle prenotazioni, scioperi fuori dall'Italia, trasferimenti ufficiali aeroporto-città, traghetti.

**Letti prima di cominciare:** `.claude/skills/rete-siti/SKILL.md`, `REGOLE-FISSE.md` (le due regole del 30/10), `ESPLORATE.md` per intero, `CRUSCOTTO-RETE.md` (sez. 7 affiliazioni, note del 28-30/10), `affiliazioni-2026-10-17.md`, `strumenti/monetizzazione.json`, gli studi 10, 11 e 14 sugli scioperi.

**Già chiuse, che NON rivaluto:** pedaggi con l'auto a noleggio, gomme invernali, patenti all'estero (fatti oggi); zone a basse emissioni, prezzi dei carburanti, calcolatori Swiss Travel Pass e JR Pass, taxi degli aeroporti; scioperi in Francia, Spagna, Germania, Grecia, Portogallo, Regno Unito (studi 10, 11, 14); biglietti e abbonamenti per città (23/10: NO); Shinkansen e traghetti greci (14).

**Metodo.** Autocomplete Google `client=firefox`, `hl=en`, con `gl=us` e `gl=uk` (circa 80 interrogazioni; i risultati delle due zone sono quasi identici). Prova delle fonti con curl e un browser finto (codice HTTP, formato, se il dato è nella pagina). Ricerca web per la prima pagina di Google (risultati come da un computer negli USA). Niente Keyword Planner: i volumi sono "varianti in autocomplete", non ricerche al mese.

**Chi paga, in questo settore (verificato stasera).**
- **Trainline**: pagina affiliati 200, "Fee-free, commission paid based on Partnerize network rates": cifra non pubblica (le schede esterne dicono da 0,45 % a 20 %, contraddittorie). Non iscritti.
- **Omio**: diretto 403; su Travelpayouts 6 % (bloccato da noi per lo script); schede esterne 2-8 % secondo il Paese.
- **Rail Europe**: 403; schede esterne 1,3 % sui biglietti, 1,8 % sui pass.
- **Eurail/Interrail**: pagina affiliati 200, nessuna cifra nella pagina.
- **Ferryhopper**: la pagina affiliati rimanda alla home; Direct Ferries 403.
- **Radical Storage** (deposito bagagli): programma aperto, "commission on every booking", cifra non scritta.
- **Wise**: 10 £ a conversione (Partnerize, già nei domini ammessi della rete): adatto a chi paga con la carta contactless all'estero.
- **DiscoverCars** (attivo), **Viator** (account in analisi), **Stay22** (da chiedere): servono poco ai treni, tranne gli aeroporti (noleggio) e le città (escursioni).
- Lezione: **i treni pagano poco** (commissioni da 1 a 6 %, spesso non pubbliche). In questo settore il guadagno vero è AdSense, più Wise dove si parla di pagare con la carta.

---

## Tabella delle candidate

| # | Idea | Voto | Stima a 18 mesi (€/anno: prudente / centrale / ottimista) | Ore | Dove |
|---|---|---|---|---|---|
| 1 | Regole del trasporto pubblico per città: convalida, contactless, multa ufficiale | **6,5** | 150 / 700 / 2.500 | 18-26 | Before You Fly, blocco nuovo "Before you ride" |
| 2 | Scioperi di oggi e domani in Portogallo (e Spagna) con i servizi minimi ufficiali | **6** | 100 / 450 / 2.000 | 12-18 | Italy Strikes, pagina "Spain & Portugal" |
| 3 | Bagagli sui treni per compagnia (SNCF, Ouigo, Iryo, Renfe, Avlo, Eurostar, Italo, Trenitalia, DB, Nightjet) | **6** | 100 / 500 / 1.800 | 10-14 | Before You Fly, accanto al bagaglio a mano |
| 4 | Treni aeroporto-città: prezzi ufficiali di treni e bus per aeroporto | **5,5** | 150 / 600 / 2.500 | 12-18 | Before You Fly, nelle pagine degli aeroporti |
| 5 | Quando escono i biglietti dei treni: Regno Unito compagnia per compagnia (National Rail) + orizzonti europei | **5,5** | 100 / 400 / 1.500 | 8-12 | Before You Fly o Italy Strikes |
| 6 | Sconti ufficiali per età sui treni, Paese per Paese (senior e giovani; railcard per turisti) | **5** | 50 / 250 / 900 | 6-10 | Visa Income (pensionati) o Before You Fly |
| 7 | Orari di check-in Eurostar per stazione con l'EES | **5** | 30 / 120 / 400 | 2-3 | Before You Fly, pagina EES |
| 8 | Animali e bici sui treni per compagnia | 4,5 | – | – | no |
| 9 | City card: prezzi ufficiali e "conviene?" | 4 | – | – | no |
| 10 | Prenotazioni obbligatorie Interrail/Eurail; treni notte | 4 | – | – | no |
| 11 | Deposito bagagli nelle stazioni | 3,5 | – | – | no |
| 12 | Deutschlandticket per i turisti e prezzo 2027 | 3,5 | – | – | no |
| 13 | Traghetti: orari e prezzi ufficiali | 3 | – | – | no |
| 14 | Scioperi in Belgio e Paesi Bassi (riprova) | 3 | – | – | no |

**Nessuna idea passa l'asticella dei siti nuovi** (voto ≥ 7 e ≥ 5.000 €/anno). Niente righe nel cruscotto come sito nuovo e niente messaggio a Massimiliano. Le idee da 1 a 7 hanno guadagno atteso positivo e costo zero. Per la regola della rete fitta vanno nella coda delle sezioni, in quest'ordine: 1, 3, 2, 4, 5, 7, 6.

---

## 1. Regole del trasporto pubblico per città: convalida, contactless, multa (voto 6,5)

**L'idea.** Una pagina per ognuna delle 40 città più visitate (Europa per prima, poi New York, Tokyo, Sydney, Toronto, Dublino). Ogni pagina dice:
- come si paga (carta contactless sì/no, da quando e su quali linee);
- se bisogna convalidare;
- quanto costa la multa ufficiale, pagata subito o dopo;
- cosa fare se si viene multati.

**Domanda (autocomplete us e uk uguali).**
- "fine for not validating ticket": 10 varianti, cioè budapest, italy, berlin, prague, trenitalia, milan, paris.
- "fine for no ticket on": 10 varianti, cioè luas, go train, tram, dart, france.
- "paris metro fine": 10 varianti, con refund e appeal.
- "contactless payment metro": 10 varianti, cioè paris, london, madrid, porto, barcelona, lisbon, milan.
- "can i use contactless on": 10 varianti, cioè paris metro, stansted express, heathrow express, gatwick express.
- "can i use apple pay on paris metro": 10 varianti.
- "prague tram fine": 6 varianti. "budapest public transport fine": 7.

**Prima pagina.**
- Multe: soprattutto forum (Rick Steves, Fodor's, Reddit) e articoli di cronaca (Daily News Hungary, Curly Tales, The Local).
- **Nessuna tabella che metta insieme le città.** La ricerca web non trova un confronto aggiornato. Le cifre circolano con anni diversi: Budapest 6.000, 8.000 o 12.000 Ft.
- Contactless: c'è un concorrente, publictransportguide.com, con guide 2026 per Lisbona e Barcellona. Ci sono anche Littlepay, NFCW e i giornali.

**Fatti datati (sono il motivo per tornare sulla pagina).**
- De Lijn porta la multa a 127 € nel 2026.
- MÁV mette 25.000 Ft senza biglietto dal 16/10/2025.
- Atene ha multe nuove.
- Praga discute il raddoppio a 3.000 CZK.
- Contactless a Parigi annunciato per luglio 2026 (fonti in contrasto).
- Porto completa il contactless a fine 2026.
- Budapest: contactless in tutte le stazioni della metro dal 30/4/2026.
- Lisbona: metro con carta bancaria (pagina ufficiale `metrolisboa.pt/en/metro-bank-card/` 200).

**Fonti.**
- Domini degli operatori raggiungibili dal server: BVG, DPP, BKK, ATM, ATAC, Roma Mobilità, GVB, Wiener Linien, TMB, Metro Lisboa, MVG, MVV, HVV, SL, Transport for Ireland, Metro Madrid, OASA (tutti 200).
- Chiusi: RATP 403; luas.ie non risponde (000).
- Le pagine esatte delle multe vanno trovate a mano: gli indirizzi indovinati rispondono 404.
- Formato HTML. Una cifra per città, che cambia di rado.
- Nessuna licenza da chiedere per una cifra di legge citata con la fonte.
- **Non è un dato che si legge da solo ogni giorno.** È un elenco tenuto a mano (40 righe), con un controllo automatico mensile: il programma confronta la pagina ufficiale e avvisa quando cambia. Stessa forma della sezione bagaglio a mano (fonte frammentata, voto 7 il 18/10).

**Chi paga.**
- AdSense: pubblico USA e UK in viaggio.
- Wise, 10 £ a conversione, in un riquadro "paga con una carta senza commissioni sul cambio" accanto al contactless.
- Viator nelle pagine città, se l'account viene approvato.
- Nessuna commissione sui biglietti dei mezzi pubblici.

**Stima a 18 mesi.**
- Prudente 150 €: 40 città, 1.500 visite al mese, AdSense 6 € ogni 1.000 visite, nessun Wise.
- Centrale 700 €: 6.000 visite al mese, più 10-15 aperture di conto Wise all'anno.
- Ottimista 2.500 €: le pagine contactless e multe vanno nei primi 3 risultati per 10-15 città.

**Ore:** 18-26 (riuso il motore di Before You Fly: modello di pagina per aeroporto, file dati JSON, controllo dei cambi).

**Voto 6,5**, perché:
- la domanda è grande e i concorrenti sono deboli sulle multe;
- però la fonte è frammentata, il lavoro è in parte a mano e gli affiliati sono deboli;
- arriva a 7 se Wise è attivo e la pagina sulla multa di Budapest o Praga prende 300 impressioni in 30 giorni.

---

## 2. Scioperi di oggi e domani in Portogallo (e Spagna), con i servizi minimi ufficiali (voto 6)

**Fatto nuovo, rispetto allo studio 14.** Lo studio 14 aveva chiuso il Portogallo con "nessun elenco dei preavvisi" (DGERT: solo statistiche mensili in PDF). Stasera ho trovato il **Conselho Económico e Social (CES)**.
- Pubblica ogni decisione del tribunale arbitrale sui servizi minimi degli scioperi nelle aziende pubbliche.
- Lo fa con un'**API JSON aperta**: `https://ces.pt/wp-json/wp/v2/posts?search=greve` → 200, `application/json`.
- Ogni post ha data, azienda, giorni e ore dello sciopero, percentuale dei servizi minimi e PDF allegati.

**Esempi letti stasera:**
- 26/10: Metropolitano de Lisboa, scioperi del 28 e 30/10. Servizio minimo del 25 % tra le 7 e le 10, cioè 4 treni per linea su ognuna delle 4 linee.
- 28/10: CP – Comboios de Portugal, sciopero di 24 ore del **30/10/2026** (oggi). Il PDF allegato è `Greve_SFRCI_30Out26_25SM_ANEXO-AO-ACORDAO.pdf`: probabilmente l'elenco dei treni garantiti, come i "treni garantiti" italiani. Da aprire nel test.
- In archivio, da maggio 2025: Carris, Transtejo Soflusa, STCP (Porto), IP Infraestruturas, TAP, handling SPdH/Menzies e Portugália.

**Limiti.**
- L'anticipo è di **2-3 giorni**: decisione del 25/10 per il 28/10, del 27/10 per il 30/10.
- È lo stesso difetto che ha chiuso la Spagna nello studio 11 (mediana 2-3 giorni; solo il 12 % con 5 giorni o più).
- Il CES copre solo gli scioperi delle aziende pubbliche che vanno in arbitrato. Mancano gli accordi diretti e le aziende private (Fertagus, Metro Transportes do Sul).
- Volume: circa 12 scioperi dei trasporti in 10 mesi del 2026.
- Licenza: le decisioni dei tribunali arbitrali sono atti ufficiali. Il diritto d'autore portoghese (art. 7 del Código do Direito de Autor) esclude i testi delle decisioni delle autorità, da confermare. Sul sito non ho trovato una nota di copyright.

**Domanda (autocomplete us e uk).**
- "lisbon metro strike": 10 varianti, cioè update today, tomorrow, update today live, dates.
- "portugal train strike": 10 varianti, cioè update today live map, tomorrow, 2026.
- "belgium train strike" e "netherlands train strike": 10 varianti ciascuna, ma lì non c'è nessuna fonte (vedi n. 14).

**Prima pagina:** The Portugal News, Portugal Resident, forum del Cammino di Santiago, Reddit. Nessuno mostra i servizi minimi con i numeri dei treni.

**Chi paga:**
- AdSense;
- Omio è bloccato (Travelpayouts);
- SafetyWing è già acceso su Italy Strikes;
- un riquadro DiscoverCars ("noleggia un'auto se il treno non parte") è possibile, ma la conversione è incerta.

**Stima:** 100 / 450 / 2.000 €/anno. Pochi scioperi; picchi di traffico solo nei giorni di sciopero.

**Ore:** 12-18. Si riusa la raccolta di Italy Strikes, che legge già la riserva CGSSE. Per la Spagna c'è già il lettore delle 2 pagine del ministero scritto nello studio 11.

**Dove:** Italy Strikes, pagina "Spain & Portugal strikes today", che riunisce le due fonti ufficiali (circa 90 decisioni all'anno in tutto).

**Prima condizione:** Italy Strikes indicizzato (al 21/10 aveva 0 pagine indicizzate). Altrimenti le pagine nuove nascono su un sito che Google non legge.

**Voto 6:**
- fonte ufficiale nuova e leggibile;
- però anticipo corto e copertura parziale;
- non è un sito nuovo.

---

## 3. Bagagli sui treni per compagnia (voto 6)

**L'idea.** È la stessa forma della sezione bagaglio a mano (PASSA, voto 7, il 18/10), ma per i treni. Una pagina per compagnia con:
- numero di bagagli;
- misure;
- peso;
- multa o supplemento;
- data dell'ultima modifica.

Più un confronto "la mia valigia va bene su Ouigo, Iryo, Avlo?".

**Domanda (autocomplete us e uk, 10 varianti ciascuna).**
- "sncf luggage" (rules, allowance, restrictions, size, label);
- "ouigo luggage", "iryo luggage", "renfe luggage", "eurostar luggage", "italo luggage", "trenitalia luggage", "frecciarossa luggage", "nightjet luggage" (allowance, size, rules);
- "luggage allowance on trains in": europe, japan, italy, spain.

**Prima pagina:**
- baggagepolicies.com (pagine per compagnia 2026, anche Eurail);
- blog di Stasher in 8 lingue;
- FAQ di Trainline;
- everyrail.com;
- le compagnie stesse.

Le fonti si contraddicono (Italo 75×53×30 oppure 75×30×30; il peso di Renfe). Le multe SNCF sono date "fino a 150 €" senza fonte.

**Fonti.**
- Raggiungibili (200): Ouigo (FR e ES), Renfe, Eurostar, Italo, Trenitalia, DB, ÖBB, SBB, CP, Irish Rail, NS, SJ, Vy, ČD, MÁV.
- Chiuse: SNCF Voyageurs e SNCF Connect 403, Iryo 403, SNCB 403.
- HTML; regola in prosa.
- Elenco a mano di circa 15 compagnie, con controllo mensile dei cambi.

**Chi paga:**
- AdSense;
- Radical Storage, deposito bagagli: programma aperto, cifra non pubblicata;
- Amazon UK per le valigie (bassa resa, vedi 26/10).

**Stima:** 100 / 500 / 1.800 €/anno.

**Ore:** 10-14, con il motore della sezione bagaglio a mano.

**Voto 6:** concorrente automatico già presente (baggagepolicies), e 3 fonti importanti su 4 della Francia e della Spagna sono chiuse dal server.

---

## 4. Treni e bus aeroporto-città: prezzi ufficiali (voto 5,5)

**Domanda enorme**, 10 varianti ciascuna: "leonardo express price", "cdg to paris train price", "heathrow express price" (vs elizabeth line, contactless, railcard), "how to get from fiumicino to rome", "schiphol to amsterdam train", "lisbon airport to city metro", "athens airport metro price", "airport train ticket price" (sydney, munich, vienna, oslo, brussels, barcelona, berlin), "orly to paris".

**Fonti, prova di stasera.**
- Prezzo nella pagina: Trenitalia Leonardo Express 200 (prezzi in HTML); Heathrow Express 200 ("from £10"); Gatwick Express 200; City Airport Train di Vienna 200 ("from €7").
- Pagina raggiungibile, prezzi caricati in JavaScript: Arlanda Express, Flytoget, Vienna Airport, BER.
- Chiusi: Schiphol, STASY e Brussels Airport 403; Athens Airport e Luas senza risposta (000); Stansted Express 403.
- `aerobusbcn.com` risponde 200 **con pubblicità di casinò dentro la pagina**: dominio compromesso o venduto. Da non linkare.

**Prima pagina:** siti degli aeroporti, Rome2rio, Klook e GetYourGuide (vendono Leonardo Express e Heathrow Express), blog. Il dato "taxi" è già chiuso (ricerca dei numeri ufficiali).

**Chi paga:**
- DiscoverCars, attivo (riquadro noleggio all'aeroporto);
- Stay22 (hotel vicino all'aeroporto);
- Trainline vende Heathrow Express, Stansted Express e Trenitalia, con cifra non pubblica.
- Welcome Pickups è bloccato.

**Stima:** 150 / 600 / 2.500 €/anno. **Ore:** 12-18.

**Dove:** riquadro "Airport to city" dentro le pagine aeroporto di Before You Fly, che esistono già.

**Voto 5,5:** concorrenza forte (aeroporti e Rome2rio). Ma è un'aggiunta naturale alle pagine che hanno già traffico (liquidi per aeroporto).

---

## 5. Quando escono i biglietti dei treni (voto 5,5)

**Fonte ufficiale leggibile.** `https://www.nationalrail.co.uk/travel-information/advance-booking-dates/` risponde 200, HTML di 270 KB.
- Elenca **23 compagnie britanniche** con la data fino a cui i biglietti sono in vendita, separata per sabato, domenica e feriali (es. LNER fino al 16-22 gennaio, CrossCountry fino al 23 aprile), più le chiusure di linea.
- Si aggiorna ogni settimana: si può leggere da solo.
- Licenza: condizioni d'uso di National Rail da leggere prima di costruire.

**Domanda.**
- "when are train tickets released": 10 varianti per mese (december, july, august…) e "uk".
- "when do lner tickets": 10 varianti (christmas, weekend).
- "when do avanti tickets": 10; "when do gwr tickets": 8.
- "advance tickets released": 10 (scotrail, gwr, lner).
- "when do eurostar tickets go on sale": 10 (december 2026, august 2026, christmas, ski train, snap).
- "sncf ouverture des ventes": 10 (noël 2026, été 2026, hiver 2027), ma in francese.
- "how far in advance can you book trains in": 10 (italy, japan, france, spain, europe).

**Prima pagina.**
- Le compagnie rispondono da sole: LNER scrive "tickets on sale up to Friday 15 January 2027" e ha gli avvisi per email.
- Ci sono anche Trainline Ticket Alert, TrainSplit, i blog di Railforums, MoneySavingExpert e la stessa National Rail.
- In Francia: voyagerentrain.fr, hourrail.voyage (con la pagina "ouverture des ventes en Europe 2026"), ulysse.com.
- Le vendite SNCF di Natale 2026 sono già aperte (30/9/2026).

**Chi paga:** AdSense UK; Trainline (Partnerize, cifra non pubblica); Omio è bloccato.

**Stima:** 100 / 400 / 1.500 €/anno. **Ore:** 8-12.

**Voto 5,5:** fonte perfetta, ma l'ente e le compagnie rispondono già con gli avvisi. È lo stesso verdetto dei parchi NPS e di recreation.gov.

---

## 6. Sconti ufficiali per età sui treni (voto 5)

**Domanda.**
- "senior discount trains": 10 varianti (uk, portugal, italy, france, spain).
- "railcard for tourists": 10 (senior, two together, price).
- "carte avantage senior": 10.
- "trenitalia senior discount": 9.
- "bahncard for tourists": 7.
- "can tourists buy a deutschland ticket" compare in "can tourists buy a".

**Fonti:** Renfe, Trenitalia, CP, DB, ÖBB 200; SNCF 403. Le tariffe cambiano una volta l'anno.

**Prima pagina:** seat61 (copertura completa per Paese), Trainline, blog dei pensionati.

**Chi paga:** AdSense; Trainline vende le railcard (cifra non pubblica).

**Stima:** 50 / 250 / 900 €/anno. **Ore:** 6-10.

**Voto 5:** seat61 è difficile da battere. Ha senso solo come pagina dentro Visa Income per i pensionati che si trasferiscono, con il link alle loro pagine Paese.

---

## 7. Check-in Eurostar per stazione con l'EES (voto 5)

**Domanda:** "eurostar ees" 10 varianti (st pancras, delays today, queues, pre registration, kiosks); "eurostar check in time" 10 (st pancras, gare du nord, brussels, rotterdam, lille).

**Fonte:** eurostar.com 200. Code dal vivo: nessuna fonte ufficiale.

**Stima:** 30 / 120 / 400 €/anno. **Ore:** 2-3, una pagina dentro la pagina EES di Before You Fly.

**Voto 5**, positivo ma piccolo.

---

## Le chiuse (NO)

**8. Animali e bici sui treni (4,5).**
- La domanda c'è, ma più debole delle altre: "can i take my dog on the train in" (melbourne, ireland, france, uk), "bike on train in" (japan, italy, france, belgium, germany), "eurostar pet" 10.
- Le regole sugli animali sono già RISERVA nello studio 1 e NO per le compagnie aeree (19/10).
- Chi paga: nessun programma adatto. Al massimo una riga nelle pagine della n. 3.
- Stessa sera, il ricercatore degli animali ha messo "cani sui treni europei per compagnia" a RISERVA (5) in `idee-2026-10-30-animali.md`: i due verdetti sono coerenti.

**9. City card, prezzi ufficiali e "conviene?" (4).**
- Domanda alta: "city card worth it" 10 (vienna, amsterdam, copenhagen, reykjavik, madrid, budapest, prague); "vienna city card" 10.
- Ma thebettervacation.com ha le pagine "worth it" per città in 6 lingue, all-museums.pages.dev è un sito automatico, e c'è travelarbitrage su vercel.
- Prezzi ufficiali nella pagina solo per Vienna e Praga: Berlino, Budapest, Copenaghen e Roma Pass caricano i prezzi in JavaScript; Stockholm Pass 403; Oslo Pass senza risposta.
- Chi paga: Go City 403, GetYourGuide e Tiqets non iscritti.
- È la stessa conclusione dei calcolatori Swiss Pass e JR Pass del 28/10.

**10. Prenotazioni obbligatorie Interrail/Eurail e treni notte (4).**
- "eurail reservation fees" 9 varianti, "interrail seat reservation" 10, "nightjet booking" 10.
- Seat61 ed Eurail stessa (con il suo portale prenotazioni) rispondono; le tariffe sono di ogni compagnia.
- Eurail affiliati: pagina 200, nessuna cifra.

**11. Deposito bagagli nelle stazioni (3,5).**
- "luggage storage termini" 10 varianti.
- Ma Radical Storage, Bounce e Stasher hanno già pagine automatiche per ogni stazione, e sono loro i programmi che pagherebbero.

**12. Deutschlandticket per i turisti e prezzo 2027 (3,5).**
- "deutschlandticket price 2027" 6 varianti, "deutschlandticket for tourists" 5.
- Una cifra all'anno, le testate tedesche e la DB rispondono. Al massimo una riga nella n. 6.

**13. Traghetti: orari e prezzi ufficiali (3).**
- Domanda per rotta ("ferry from italy to greece" 10, "ferry to sardinia" 10).
- Ma nessuna fonte ufficiale unica: prezzi dinamici delle compagnie, Ferryhopper e Direct Ferries in testa. Lo studio 14 aveva già chiuso i traghetti greci.
- Ferryhopper non mostra le condizioni di affiliazione; Direct Ferries 403.

**14. Scioperi in Belgio e Paesi Bassi, riprova (3).**
- Domanda forte: "belgium train strike" 10 (dates, 2026, eurostar, november), "brussels airport strike" 10, "netherlands train strike" 10.
- Ma nessun registro pubblico: belgiantrain.be 403; NS 200 ma senza elenco; gli scioperi si leggono solo sui giornali (Brussels Times).
- Resta il verdetto degli studi 10 e 14.

---

## Sezioni piccole da costruire (regola della rete fitta)

| Ordine | Sezione | Sito | Ore | € a 18 mesi (prudente / centrale) | Condizione |
|---|---|---|---|---|---|
| 1 | Regole del trasporto pubblico in 40 città (convalida, contactless, multa, con data del cambio) | Before You Fly | 18-26 | 150 / 700 | Wise già nei domini ammessi: verificare che il link sia attivo |
| 2 | Bagagli sui treni per 15 compagnie | Before You Fly | 10-14 | 100 / 500 | Nessuna |
| 3 | Scioperi in Spagna e Portogallo con i servizi minimi (CES JSON + ministero spagnolo) | Italy Strikes | 12-18 | 100 / 450 | Dopo le prime pagine indicizzate di Italy Strikes |
| 4 | Riquadro "Airport to city" (treno e bus ufficiali) nelle pagine aeroporto | Before You Fly | 12-18 | 150 / 600 | Nessuna; non linkare aerobusbcn.com |
| 5 | Biglietti in vendita fino a…: 23 compagnie britanniche, ogni settimana | Before You Fly | 8-12 | 100 / 400 | Leggere le condizioni d'uso di National Rail |
| 6 | Check-in Eurostar con l'EES | Before You Fly | 2-3 | 30 / 120 | Nessuna |
| 7 | Sconti per età sui treni, Paese per Paese | Visa Income | 6-10 | 50 / 250 | Coda bassa |

Totale: 68-101 ore. Somma prudente circa 680 €/anno, centrale circa 3.000 €/anno, a 18 mesi.

---

## Prove (indirizzi provati stasera)

- **200:**
  - `nationalrail.co.uk/travel-information/advance-booking-dates/`
  - `ces.pt/wp-json/wp/v2/posts?search=greve` (JSON), `ces.pt/arbitragem/`
  - `metrolisboa.pt/en/metro-bank-card/`
  - `trenitalia.com/en/services/leonardo-express.html`, `heathrowexpress.com`, `gatwickexpress.com`, `cityairporttrain.com/en`, `arlandaexpress.com`, `flytoget.no/en/`
  - `viennaairport.com`, `berlin-airport.de`
  - `thetrainline.com/about-us/affiliates`, `eurail.com/en/affiliate-program`, `ferryhopper.com/en/affiliates`, `radicalstorage.com/affiliate`, `discovercars.com/affiliate`
  - `viennacitycard.at`, `praguevisitorpass.eu`
  - `ouigo.com`, `renfe.com`, `eurostar.com`, `italotreno.com`, `bahn.com`, `oebb.at`, `sbb.ch`, `cp.pt`, `irishrail.ie`, `ns.nl`, `sj.se`, `vy.no`, `cd.cz`, `mavcsoport.hu`
  - `bvg.de`, `dpp.cz`, `bkk.hu`, `atm.it`, `atac.roma.it`, `romamobilita.it`, `gvb.nl`, `wienerlinien.at`, `tmb.cat`, `metrolisboa.pt`, `mvg.de`, `sl.se`, `hvv.de`, `transportforireland.ie`, `metromadrid.es`, `oasa.gr`, `dgert.gov.pt`
- **403:**
  - `ratp.fr`, `sncf-voyageurs.com`, `sncf-connect.com`, `groupe-sncf.com`, `ter.sncf.com`, `iryo.eu`, `belgiantrain.be`
  - `schiphol.nl`, `stasy.gr`, `brusselsairport.be`, `stanstedexpress.com`
  - `omio.com/partners`, `raileurope.com`, `gocity.com`, `12go.asia`, `welcomepickups.com`, `directferries.co.uk`, `viator.com/partner`, `stockholmpass.com`
- **000 (nessuna risposta):** `luas.ie`, `athensairport.gr`, `oslopass.no`, `presse.sncf.com`, `pkpintercity.pl`.
- **404 (indirizzi indovinati, non per forza chiusi):** pagine interne di BVG, DPP, ATM, TMB, MVV, Aena, Dublin Airport, Zurich Airport, Munich Airport, `dgert.gov.pt/avisos-previos-de-greve`, Eurostar booking horizon.
- **Notato:** `aerobusbcn.com` 200 con contenuti di casinò.
- **Ricerca web** (risultati come da un computer USA): booking horizon UK e SNCF Noël 2026; affiliazioni Trainline, Omio e Rail Europe; multe a Budapest e tabella europea delle multe; scioperi in Belgio e in Portogallo; bagagli sui treni; city card; contactless a Lisbona e in Europa; LNER advance tickets.
