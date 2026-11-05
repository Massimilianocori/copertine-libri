# Fronte affitti: inquilini e proprietari di casa (5/11/2026)

Angolo: dati ufficiali per città o ente locale che proprietari e inquilini cercano e che cambiano con regole nuove (licenze, tetti agli affitti, cauzioni, certificati, calendari di legge). Paesi: Regno Unito, Irlanda, USA, Canada, Australia, Germania, Paesi Bassi, Spagna, Italia. Esclusi gli affitti turistici brevi (Tourist Tax) e le nicchie già in `ESPLORATE.md`.

## In breve

- **Nessuna idea nuova arriva a 7.** Il fronte non è vergine: 7 nicchie del settore erano già valutate (registro dei padroni di casa inglesi, licenze selettive, tetti agli affitti USA/Canada, Mietpreisbremse, Irlanda, Spagna, classi energetiche).
- **L'unico veicolo che regge è il sito già proposto il 31/10**: "registro dei padroni di casa in Inghilterra" (voto 7, in attesa del sì di Massimiliano, da mettere online entro il 10/12/2026). Questa ricerca gli aggiunge due blocchi con fonti verificate: le **maggiorazioni della council tax su seconde case e case vuote per consiglio** (un solo file ufficiale, 296 consigli) e il **calendario delle regole nuove** (Renters' Rights Act, Scozia, Galles, EPC C 2030).
- **Pagatori letti con la cifra (USA):** TurboTenant **40 $ per cliente + 5 $ per contatto**; RentRedi **fino al 20 % del primo acquisto**, cookie 30 giorni. Rafforzano la riserva "aumento massimo dell'affitto" come sezione di FloodCost.
- **Fatti nuovi su riserve vecchie:** la Mietpreisbremse del Baden-Württemberg scade il **31/12/2026** (Sassonia 30/6/2027, Turingia 31/12/2027), ma il Mieterbund pubblica già la lista completa dei Comuni; in Irlanda le regole nuove sono in vigore dal **1/3/2026**; Oregon 2027 = **10 %** (2026: 9,5 %).

## Metodo e limiti

- Autocomplete Google per Paese (`gl`/`hl` giusti), circa 60 richieste, risultati salvati nelle note sotto.
- Fonti verificate con curl (status HTTP, formato). Le pagine dei risultati di Google, Bing e DuckDuckGo non sono leggibili da qui (Bing restituisce risultati casuali, DuckDuckGo vuoto): i concorrenti sono stati letti direttamente sui loro siti.
- CPC di AdSense: **stima**, non letta (nessun accesso a Keyword Planner). Le stime di ricavo sono prudente / centrale / ottimista per anno, con le ipotesi scritte.

## Idee valutate

### 1. Maggiorazione della council tax su seconde case e case vuote, consiglio per consiglio (Inghilterra)

- **Regola nuova:** dal 1/4/2025 i consigli inglesi possono raddoppiare la council tax sulle seconde case (premium fino al 100 %); la maggiorazione sulle case vuote parte da 1 anno (prima 2). In Galles fino al 300 %.
- **Fonte:** MHCLG, "Council Taxbase 2025 in England" (pubblicata 21/1/2026, rivista), file `2025_Local_Authority_Drop_Down.xlsx` **200**, 1,8 MB, licenza OGL. Fogli "Second Homes Data" ed "Empty Properties Data" con 296 consigli e i livelli di sconto e maggiorazione (0, 50, 100 %, variabile) per fascia A-H. Tabella 6.06 "Has the authority applied the Second Homes Premium in 2025-26?": **211 sì, 85 no**. **170.299 seconde case** pagano la maggiorazione (Cornovaglia 11.109, Westminster 10.587, North Yorkshire 6.581, Dorset 4.843, Westmorland and Furness 4.830, North Norfolk 4.421). Case vuote con maggiorazione: 152.928.
- **Galles:** `gov.wales` **403** da qui. Il dato gallese va preso a mano o lasciato fuori.
- **Domanda (gl=gb):** "second home council tax" → scotland, wales, edinburgh, rules, england, premium, **cornwall**, highland; "does cornwall council charge" → "does cornwall charge double council tax on second homes"; "empty homes premium" → exemptions, council tax, legislation, charge; "council tax premium" → exceptions, **pembrokeshire**, wales.
- **Concorrenti:** le pagine dei singoli consigli (ognuno la sua), giornali locali, Which?. Nessuna tabella unica "chi la applica e quanto" trovata tra i siti letti.
- **Chi paga:** AdSense Regno Unito sul tema tasse della casa (CPC stimato 0,3-1 £, basso). Assicurazione per proprietari: AXA Landlord su Awin ancora senza risposta (cruscotto 4/11); Simply Business ha una pagina "Partners & affiliates", cifra non letta.
- **Stima:** 60 / 400 / 1.500 €/anno (ipotesi: 296 pagine, 2-15 visite al mese ciascuna dopo 6-9 mesi, RPM 3-8 €).
- **Ore:** 8-12 (il file è unico e pulito).
- **Rischi:** dato fermo a ottobre 2025; il file 2026 esce verso gennaio 2027 (stesso calendario del 2025). Scozia e Galles a parte.
- **Voto 5,5. Dove:** blocco del sito nuovo "registro dei padroni di casa", non da solo.

### 2. Calendario delle regole nuove per proprietari e inquilini (Inghilterra, Scozia, Galles, Irlanda)

- **Fonti lette:**
  - GOV.UK, "Renters' Rights Act 2025: Implementation roadmap" (API 200): nuovo regime delle locazioni dal **1/5/2026**; **Database dei proprietari "da fine 2026"**; regole estese alle case popolari nel 2027; **iscrizione obbligatoria all'Ombudsman dei proprietari nel 2028**; Decent Homes Standard proposto per il **2035 o il 2037**; **EPC C entro il 2030** per tutte le case in affitto in Inghilterra e Galles, salvo esenzioni.
  - GOV.UK, consultazione "Extending Awaab's Law to private rented tenancies" del 9/10/2026.
  - gov.scot "Private renting" (200), "Key dates for changes": dal 1/4/2026 i consigli devono valutare gli affitti, con il **primo rapporto di ogni consiglio entro il 31/5/2027**; 1/5/2026 reato di discriminare inquilini con figli o con sussidi; 6/10/2026 successione ridotta da 12 a 6 mesi, risarcimenti più alti e obblighi su muffa e umidità.
  - RTB Irlanda (rtb.ie): "Rental law changes from 1 March 2026" e "Tenant's right to stay from 1 March 2026" nel menù.
- **Domanda (gl=gb):** "renters rights act" → 2026, information sheet 2026, notice period, pets, rent increases; "epc c by 2030" → legislation, private rentals, landlord targets; "scotland rent control" → areas, zones, **market assessments**; "landlord licence" → check, public register, croydon, birmingham, liverpool, wales, scotland.
- **Concorrenti:** NRLA, Propertymark, Shelter, Landlord Today, GOV.UK stesso. Molto forti sulle notizie; nessuno incrocia le date con il singolo consiglio.
- **Chi paga:** come sopra (assicurazione per proprietari, cifra non letta); certificati EPC/gas: nessun programma con cifra trovato.
- **Stima:** 100 / 700 / 3.000 €/anno (solo come pagine che portano traffico alle pagine per consiglio).
- **Ore:** 6-10.
- **Voto 6. Dove:** blocco "cosa cambia e quando" dello stesso sito nuovo.

### 3. Zone di controllo degli affitti in Scozia per consiglio

- **Fonte:** gov.scot (sopra). Oggi non c'è nessuna zona: i consigli fanno le valutazioni e i rapporti arrivano entro il 31/5/2027; solo dopo i ministri possono designare zone.
- **Domanda:** "scotland rent control areas / zones / market assessments", "scottish rent control exemptions".
- **Voto 5 oggi.** RISERVA con innesco: si riapre quando escono i primi rapporti dei consigli (entro il 31/5/2027) o la prima designazione. Pubblico piccolo (Scozia).

### 4. Germania: regole d'affitto Comune per Comune (Mietpreisbremse + Kappungsgrenze + Mietspiegel)

- **Riserva già esistente** (voto 7 in `ricerca-zona-europa-asia-2026-10-30`). Fatti nuovi del 5/11:
  - **Positivo:** dalla lista del Mieterbund (mieterbund.de 200, "Stand 12/2025") le scadenze dei regolamenti per Land: **Baden-Württemberg 31/12/2026**, Hessen 25/11/2025, **Sachsen 30/6/2027**, **Thüringen 31/12/2027**, Mecklenburg-Vorpommern 30/9/2029, tutti gli altri 31/12/2029. A fine anno il Baden-Württemberg deve rifare la lista dei Comuni.
  - **Negativo:** il Mieterbund pubblica già la lista completa dei Comuni con la Mietpreisbremse. Il buco resta solo nell'incrocio per Comune (Kappungsgrenze 15/20 %, Mietspiegel, divieto di disdetta dopo la vendita) e nel calcolatore.
- **Domanda (gl=de):** "mietpreisbremse baden-württemberg" → 2026, **liste**, welche städte; "kappungsgrenze" → berlin, nrw, hamburg, frankfurt, münchen, düsseldorf; "mietspiegel 2026" → berlin, frankfurt, münchen, nürnberg, essen, bielefeld; "co2 kostenaufteilung" → berechnen, vermieter.
- **Mietspiegel per città da solo: NO (3,5).** mietspiegeltabelle.de (200) ha già pagine per Land, distretto e città; wohnungsboerse (401 da qui) e i portali immobiliari; i Mietspiegel ufficiali sono PDF diversi città per città.
- **Chi paga:** kautionsfrei.de ha un programma partner (pagina 200, "attraktive Provisionen", cifra non scritta). Deutsche Kautionskasse: pagina partner vuota. conny.de: pagina partner 404.
- **Voto 6,5** (da 7): RISERVA, si riapre a gennaio 2027 con il nuovo regolamento del Baden-Württemberg come innesco e una cifra di commissione letta.

### 5. Italia: canone concordato per Comune e Comuni ad alta tensione abitativa

- **Domanda (gl=it) forte:** "canone concordato" → milano, 2027, roma, bologna, milano calcolo, torino; "accordo territoriale canone concordato" → roma, torino, firenze, milano, bologna, palermo; "comuni ad alta tensione abitativa" → individuati dal cipe 2026, emilia romagna; "cedolare secca 10" → elenco comuni; "attestazione canone concordato" → online, costo, milano, roma, catania.
- **Fonti:** nessun archivio unico. mit.gov.it **000** (non raggiungibile); comune.milano.it **403**; comune.torino.it **000**; comune.bologna.it 200; comune.roma.it 200. Ogni accordo è un PDF diverso (zone, subfasce, elementi). Elenco CIPE 87/2003 in Gazzetta Ufficiale (200).
- **Concorrenti:** Confedilizia (confedilizia.it 200) ha già l'archivio degli accordi territoriali e l'elenco dei Comuni ad alta tensione abitativa; SUNIA, UPPI, APE con i calcolatori delle sedi locali; i Comuni.
- **Chi paga:** nessun affiliato. L'attestazione la vendono le associazioni (non affiliabili). AdSense Italia sul tema affitti (CPC stimato 0,2-0,5 €).
- **Stima:** 30 / 200 / 700 €/anno (10 città capoluogo, calcolatore per città). **Ore:** 15-25 (lettura manuale dei PDF).
- **Voto 5. Dove:** RISERVA, eventualmente pagine in Aste in Chiaro (pubblico italiano della casa) solo se Aste cresce.

### 6. USA: aumento massimo dell'affitto per giurisdizione (aggiornamento della riserva del 31/10)

- **Fatti nuovi:** Oregon 2027 = **10 %** (2026: 9,5 %), pagina OEA 200 con Excel; NYC Rent Guidelines Board con l'Order #58 2026-27 in prima pagina (rentguidelinesboard.cityofnewyork.us 200). Washington: pagina Commerce sulla stabilizzazione degli affitti **404** all'indirizzo provato.
- **Pagatori letti:** TurboTenant (turbotenant.com/affiliates 200): "Earn **$40** commission for every TurboTenant customer you refer and **$5** for leads". RentRedi (rentredi.com/affiliate-program 200): "**up to 20%** commission of a first-time purchase", cookie 30 giorni. Steadily (assicurazione per proprietari) ha un widget per partner, cifra non scritta. Avail: "Earn $50" solo come invito tra utenti.
- **Domanda (gl=us):** "rent increase limit" → california, washington state, los angeles, nyc, san francisco, 2026; "rent stabilized increase 2026" → nyc, dhcr, san francisco.
- **Voto 6 (invariato):** i pagatori ora hanno la cifra scritta, ma la California resta senza tabella ufficiale per contea. **Dove:** sezione di FloodCost (proprietari USA), dopo i dati veri di FloodCost.

### 7. Altre nicchie scartate

| Nicchia | Voto | Motivo |
|---|---|---|
| Registrazione e licenza degli affitti per città USA (Baltimore, Cleveland, Detroit, Philadelphia, Denver, Maricopa) | 4 | autocomplete "rental registration [città]" vivo, ma nessun file unico: ogni città la sua pagina, che è prima su Google. Stesso limite degli affitti brevi USA (NO del 31/10) |
| Aumento NYC del Rent Guidelines Board | 3 | un numero solo, il sito ufficiale è primo |
| Tempi d'attesa dei tribunali degli affitti in Canada (LTB Ontario, RTB BC, TAL Québec) | 4,5, riserva | "ltb wait times 2026", "bc rtb wait times" ma nessuna fonte trovata (pagina BC 404, TAL 404), risultati Reddit; solo 3 enti |
| Aumento massimo dell'affitto nei Paesi Bassi 2026 | 3 | tetto nazionale unico, Rijksoverheid e Huurcommissie (huurprijscheck) ufficiali; nessun dato per Comune |
| Regole di aumento e cauzioni per Stato in Australia | 3,5 | 8 enti statali e agenzie immobiliari; "landlord insurance terri scheer / budget direct" senza cifra letta; affitti per sobborgo già NO |
| Classe EPC minima C entro il 2030 per area | 3 | già NO il 19/10 (domanda per la singola casa); resta solo come pagina del calendario (idea 2) |

## Conclusione

- **Migliore idea:** nessuna nuova a sé. La mossa giusta resta il sito "registro dei padroni di casa in Inghilterra" già proposto (voto 7, 450 / 3.000 / 14.400 €/anno); con i due blocchi di questo studio la stima centrale sale di circa 1.000 €/anno (blocco 1: +400, blocco 2: +700, in parte sovrapposti).
- **Voto ≥ 8:** nessuno.
- **Costruibile subito a costo zero:** nessuna sezione nei siti esistenti; i blocchi 1 e 2 si costruiscono solo dentro il sito nuovo, dopo il sì di Massimiliano. Il blocco 1 usa un solo file (MHCLG Council Taxbase 2025, xlsx, OGL).
- **Inneschi da segnare:** gennaio 2027 (nuova lista Mietpreisbremse del Baden-Württemberg; Council Taxbase 2026); 31/5/2027 (rapporti dei consigli scozzesi sugli affitti).
