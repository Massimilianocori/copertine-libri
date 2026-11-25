# Ricerca settore nuovo: casa e giardino negli Stati Uniti (giardinaggio, radon, isolamento) e altri 5 settori a confronto

Data: 25/11/2026. Solo ricerca. Nessun sito toccato, nessun commit.

## In breve

- **Nessun candidato arriva a voto 7 e a 5.000 €/anno centrali.** Il migliore è il giardinaggio USA: voto 5,5 e 827 €/anno centrali.
- Quindi, con la regola «NIENTE MASSA DI SITI INUTILI», **non propongo nessun sito nuovo**.
- Ho trovato due fatti nuovi che servono lo stesso:
  1. Nel file ufficiale di AdSense la categoria **Casa e giardino in America paga 13,37 $ ogni 1.000 pagine**. Tutte le altre categorie pagano fra 0,89 e 4,34 $. Nessun nostro documento lo aveva notato.
  2. Il file ufficiale delle zone climatiche per codice postale (PRISM) **oggi si scarica**. Il 13/11 non si scaricava, ed era il motivo della riserva sul giardinaggio.
- Il conto che decide tutto: per fare 5.000 €/anno servono da 6.000 a 10.000 visite a settimana su un solo sito. Il nostro sito migliore (EsameB1) ne fa 420.

## 1. Che cosa dicono i nostri dati veri

Fonte: GoatCounter. Oggi l'API mi ha bloccato a metà lettura («rate limited», 31 minuti). Uso quindi le letture già scritte in `AUDIT-25-11.md` e nel cruscotto, più una lettura mia di oggi sulle provenienze.

| Dato | Valore | Fonte |
|---|---|---|
| Visite 18–24/11, per sito | EsameB1 420 · Visa Income 292 · Before You Fly 218 · Paga CCNL 60 · Cruise 32 · Tourist Tax 31 · Aste 17 · Payroll Tax 13 · FloodCost 11 · Inflation 4 · FHA 2 · Quiz 2 · EsamiDiStato 1 · ATECO 1 · gli altri 0 | `AUDIT-25-11.md` |
| Provenienze 18–24/11, tutta la rete | ChatGPT 330 · Google 270 · diretto 138 · Yandex 8 · Bing 5 | API `stats/toprefs`, letta oggi |
| Siti con zero visite | circa 13 su 27 | `AUDIT-25-11.md` |

Che cosa ne ricavo:

- Solo 3 siti su 27 superano 200 visite a settimana.
- ChatGPT oggi porta più visite di Google. Premia le tabelle di dati ufficiali.
- Un sito nuovo, dopo sei settimane, sta fra 0 e 60 visite a settimana. Italy Strikes è a 31 da Google.
- 420 visite a settimana sono circa 22.000 visite l'anno. È il nostro massimo.

## 2. Quanto paga la pubblicità (fonti pubbliche)

**Fonte ufficiale.** File del calcolatore di AdSense: `https://adsense.google.com/start/calculator-data.json`. Letto oggi, risposta 200. Data del file: 9/12/2024. Il numero è il guadagno in dollari ogni 1.000 pagine viste.

| Categoria | Americhe | Europa | Asia-Pacifico |
|---|---|---|---|
| **Casa e giardino (Home & Garden)** | **13,37** | **5,16** | 4,11 |
| Computer ed elettronica | 4,34 | 2,60 | 4,04 |
| Salute | 3,41 | 3,25 | 3,23 |
| Imprese e industria | 3,39 | 2,32 | 3,28 |
| Finanza | 3,34 | 4,29 | 5,29 |
| Legge e governo | 3,05 | 2,59 | 4,39 |
| Viaggi | 2,95 | 3,25 | 2,08 |
| Auto | 2,66 | 2,28 | 2,18 |
| Cibo | 2,62 | 1,94 | 1,90 |

**Fonti di terzi (meno affidabili, solo come controllo).** Blog di editori letti oggi con una ricerca: Casa e giardino con AdSense fra 5 e 15 $; con le reti grandi (Mediavine) fra 22 e 35 $. Publift per i siti di «stile di vita»: 4–12 $.

**Che cosa uso nelle stime.** Per Casa e giardino USA: prudente 5 $, centrale 8 $, ottimista 13,37 $. Il 13,37 è un valore isolato e vecchio di due anni: non lo uso come centrale. Per le altre categorie: prudente il valore ufficiale, centrale e ottimista un po' sopra.

**Nota per i siti che abbiamo già.** In Europa Casa e giardino paga 5,16 $: il doppio delle altre. Heat Pump Grants UK e Solare da Balcone stanno in questa categoria. Oggi hanno 0 visite, ma se crescono valgono il doppio per visita.

## 3. Come ho stimato

- Formula (la stessa dei nostri studi): ricerche al mese × 12 × quota = visite l'anno. Visite × 1,3 = pagine viste. Pagine viste ÷ 1.000 × $ × 0,92 = €.
- Le stime sono a 36 mesi. A 12 mesi contare circa un terzo.
- **Domanda.** Lo strumento dei volumi non c'è. Per il giardinaggio uso i volumi veri misurati il 13/11 (`intelaiatura/fronti-2026-11-13-nuovi-radar.md`). Per gli altri sette la domanda è una **mia stima** da segnali pubblici. È il punto più debole di questo studio.
- Google Trends: non leggibile dal server (404). Non ho forzato.
- Wikipedia, pagine viste in 12 mesi (segnale debole, l'API mi ha limitato): «Canning» 90.929, «Probate» 88.407, «Energy Star» 59.099, «Building insulation» 24.173, «Radon mitigation» 20.694, «Home canning» 14.193.
- **Quota.** I nostri dati dicono che un sito nuovo prende poco. Uso quote basse: da 0,1 % a 3 % dove i concorrenti sono forti, fino a 6 % dove rispondono con PDF.
- **Concorrenti.** Ho aperto le pagine dei primi risultati per ogni candidato. Letti in fretta, una pagina ciascuno.

## 4. Gli 8 candidati

Tutti fuori dalle zone vietate (viaggi, visti, cittadinanza, esami di lingua, pratiche per stranieri, assicurazioni viaggio, eSIM, casa per stranieri).

### Tabella dei voti

Voti da 0 a 10. Concorrenza: 10 = campo libero, 0 = campo chiuso.

| # | Settore e idea | Domanda | Concorrenza | Pubblicità | Dati ufficiali | **Voto** | €/anno prudente / centrale / ottimista | Ore |
|---|---|---|---|---|---|---|---|---|
| 1 | **Giardinaggio USA**: zona climatica per codice postale, date delle gelate, quando seminare | 9 | 3 | 9 | 8 | **5,5** | 155 / **827** / 4.145 | 40 |
| 2 | **Sicurezza della casa USA**: radon per contea e per Stato | 5 | 5 | 7 | 8 | **5** | 15 / **194** / 2.303 | 35 |
| 3 | **Isolamento della casa USA**: valore R per zona e per Stato | 6 | 2 | 9 | 6 | **4** | 11 / **161** / 1.535 | 35 |
| 4 | **Agricoltura USA**: affitto e valore dei terreni per Stato e contea | 3 | 5 | 4 | 7 | **4** | 7 / **86** / 620 | 30 |
| 5 | **Tassi ufficiali per fiscalisti USA**: AFR del mese, tasso 7520, interessi IRS | 3 | 3 | 5 | 9 | **4** | 7 / **86** / 775 | 25 |
| 6 | **Conserve fatte in casa**: tempi USDA per alimento, vasetto e altitudine | 7 | 2 | 3 | 7 | **3,5** | 8 / **103** / 1.148 | 45 |
| 7 | **Auto USA**: vetri oscurati, limite di legge per Stato | 7 | 2 | 3 | 2 | **3** | 9 / **100** / 969 | 35 |
| 8 | **Elettrodomestici USA**: consumo e costo per Stato | 8 | 1 | 8 | 9 | **3** | 22 / **207** / 1.919 | 30 |

**Somma dei centrali: 1.764 €/anno per 275 ore.** Nessuno passa il 7. Nessuno passa i 5.000 €.

### I conti, uno per uno

**1. Giardinaggio USA.**
- Domanda: 720.000 ricerche al mese (325.000 misurate il 13/11: «usda zone map» 90.500, «planting zones» 49.500, «what planting zone am i in» 33.100, «tomatoes when to plant» 40.500). Spesa per il giardino nel 2025: 79 miliardi di dollari, record (National Gardening Survey 2026).
- Concorrenti: almanac.com (calendario per codice postale, molto forte), Urban Farmer (un calendario per zona), Gardening Know How, mappa ufficiale USDA.
- Dati: file PRISM delle zone per codice postale, **200 oggi** (1,2 MB, `prism.oregonstate.edu/phzm/data/2023/phzm_us_zipcode_2023.csv`). Medie NOAA 1991-2020 delle gelate: 200, 15.616 file di stazione. Dominio pubblico.
- Prudente: 8.640.000 × 0,3 % = 25.920 visite × 1,3 = 33.696 pagine × 5 $ = 168 $ = **155 €**.
- Centrale: 8.640.000 × 1 % = 86.400 visite × 1,3 = 112.320 pagine × 8 $ = 899 $ = **827 €**.
- Ottimista: 8.640.000 × 3 % = 259.200 visite × 1,3 = 336.960 pagine × 13,37 $ = 4.505 $ = **4.145 €**.
- Limite: tre quarti della domanda sta in quattro mesi (febbraio-maggio).

**2. Radon per contea e per Stato.**
- Domanda: stima 150.000 al mese (forbice 60.000–300.000). Segnali: 7 milioni di case sopra il limite (EPA, 1 su 15); 4,5 milioni di case vendute l'anno, molte con prova del radon. Gennaio è il mese nazionale del radon.
- Concorrenti: tabella EPA (ufficiale, con ricerca), city-data.com (dati vecchi), radonresources.com (elenco di installatori con «livello medio» preso da pochi invii di utenti: Franklin County 10,7 pCi/L senza fonte).
- Dati: file EPA delle zone, 200, 3.219 righe di contee. API CDC con le prove di laboratorio per contea (media, mediana, massimo in 10 anni), 200. Solo 21 Stati mandano dati al CDC.
- Già vista il 15/10 come «radon per CAP: NO, nessuna fonte unica». Per contea la fonte c'è: è il fatto nuovo.
- Prudente: 720.000 × 0,5 % = 3.600 × 1,3 = 4.680 × 3,41 $ = 16 $ = **15 €**.
- Centrale: 1.800.000 × 1,5 % = 27.000 × 1,3 = 35.100 × 6 $ = 211 $ = **194 €**.
- Ottimista: 3.600.000 × 4 % = 144.000 × 1,3 = 187.200 × 13,37 $ = 2.503 $ = **2.303 €**.

**3. Isolamento e zona climatica.**
- Domanda: stima 200.000 al mese (80.000–400.000).
- Concorrenti: ENERGY STAR (tabella ufficiale chiara), Home Depot, Angi, e **hvacbase.org**: tutte le 3.142 contee, aggiornato il 17/11/2026, con autore. Fa già ciò che faremmo noi.
- Dati: file PNNL delle zone per contea, 200. Tabella ENERGY STAR, 200. Stato dei codici per Stato (energycodes.gov): **403**.
- Prudente: 960.000 × 0,2 % = 1.920 × 1,3 = 2.496 × 5 $ = 12 $ = **11 €**.
- Centrale: 2.400.000 × 0,7 % = 16.800 × 1,3 = 21.840 × 8 $ = 175 $ = **161 €**.
- Ottimista: 4.800.000 × 2 % = 96.000 × 1,3 = 124.800 × 13,37 $ = 1.669 $ = **1.535 €**.

**4. Agricoltura USA: affitti dei terreni.**
- Domanda: stima 40.000 al mese (15.000–90.000). Segnali: 1,9 milioni di aziende agricole; affitto medio 2026 160 $ per acro; il dato esce una volta l'anno, ad agosto.
- Concorrenti: farmdoc (Università dell'Illinois), i servizi delle università di Iowa e Nebraska, Farm Bureau, AcreValue. Molti rispondono con PDF.
- Dati: pagina USDA NASS 200. I file per contea chiedono una chiave gratuita.
- Prudente: 180.000 × 1 % = 1.800 × 1,3 = 2.340 × 3,39 $ = 8 $ = **7 €**.
- Centrale: 480.000 × 3 % = 14.400 × 1,3 = 18.720 × 5 $ = 94 $ = **86 €**.
- Ottimista: 1.080.000 × 6 % = 64.800 × 1,3 = 84.240 × 8 $ = 674 $ = **620 €**.

**5. Tassi ufficiali per fiscalisti (AFR).**
- Domanda: stima 60.000 al mese (30.000–120.000). Pubblico di professionisti che torna ogni mese.
- Concorrenti: IRS (PDF), Thomson Reuters, Bloomberg Tax, Eide Bailly, Principal, Ascensus. Tutti pubblicano il tasso il giorno stesso. La ricerca di oggi mi ha dato il tasso di dicembre 2026 (4,60 %) senza aprire nessun sito: rischio «zero clic» alto.
- Dati: irs.gov 200, uscourts.gov 200.
- Prudente: 360.000 × 0,5 % = 1.800 × 1,3 = 2.340 × 3,34 $ = 8 $ = **7 €**.
- Centrale: 720.000 × 2 % = 14.400 × 1,3 = 18.720 × 5 $ = 94 $ = **86 €**.
- Ottimista: 1.440.000 × 5 % = 72.000 × 1,3 = 93.600 × 9 $ = 842 $ = **775 €**.
- Se si fa, va dentro Inflation (dove c'è già la riserva «tassi ufficiali USA»), non in un sito nuovo.

**6. Conserve fatte in casa.**
- Domanda: stima 300.000 al mese (100.000–500.000), forte da luglio a ottobre.
- Concorrenti: il centro ufficiale NCHFP (primo), decine di università, healthycanning.com, Ball.
- Dati: NCHFP 200, guida USDA di dominio pubblico (PDF). Tema di sicurezza alimentare (botulino): ogni cifra va copiata uguale.
- Prudente: 1.200.000 × 0,2 % = 2.400 × 1,3 = 3.120 × 2,62 $ = 8 $ = **8 €**.
- Centrale: 3.600.000 × 0,6 % = 21.600 × 1,3 = 28.080 × 4 $ = 112 $ = **103 €**.
- Ottimista: 6.000.000 × 2 % = 120.000 × 1,3 = 156.000 × 8 $ = 1.248 $ = **1.148 €**.

**7. Vetri oscurati per Stato.**
- Domanda: stima 250.000 al mese (120.000–450.000).
- Concorrenti: Rayno (aggiornato ad agosto 2026), recordinglaw.com (2026), Madico, FindLaw.
- Dati: **non esiste una tabella ufficiale**. Servono 51 leggi lette a mano. La tabella dell'associazione di settore (IWFA) oggi risponde 404.
- Prudente: 1.440.000 × 0,2 % = 2.880 × 1,3 = 3.744 × 2,66 $ = 10 $ = **9 €**.
- Centrale: 3.000.000 × 0,8 % = 24.000 × 1,3 = 31.200 × 3,5 $ = 109 $ = **100 €**.
- Ottimista: 5.400.000 × 2,5 % = 135.000 × 1,3 = 175.500 × 6 $ = 1.053 $ = **969 €**.

**8. Consumo degli elettrodomestici per Stato.**
- Domanda: stima 600.000 al mese (300.000–1.000.000).
- Concorrenti: campo pieno di siti automatici. In una sola ricerca: hvacbase.org, jouleio.com, voltflow.net, due copie su `.pages.dev`, Jackery, Perch Energy.
- Dati: API ENERGY STAR 200, senza chiave.
- Rischio: pagine modello tutte uguali. È il motivo del rifiuto «Low value content» che abbiamo già preso.
- Prudente: 3.600.000 × 0,1 % = 3.600 × 1,3 = 4.680 × 5 $ = 23 $ = **22 €**.
- Centrale: 7.200.000 × 0,3 % = 21.600 × 1,3 = 28.080 × 8 $ = 225 $ = **207 €**.
- Ottimista: 12.000.000 × 1 % = 120.000 × 1,3 = 156.000 × 13,37 $ = 2.086 $ = **1.919 €**.

## 5. Perché nessuno arriva a 5.000 €

Il conto al contrario:

- 5.000 € = 5.435 $.
- Con 8 $ ogni 1.000 pagine: servono 679.000 pagine viste l'anno. Sono 523.000 visite, cioè **10.000 a settimana**. È 24 volte EsameB1.
- Con 13,37 $ (il caso migliore): servono 406.000 pagine. Sono 313.000 visite, cioè **6.000 a settimana**. È 14 volte EsameB1.
- Con 3 $ (tutte le altre categorie): servono 1,8 milioni di pagine. Sono 27.000 visite a settimana.

Un sito con meno di 100 pagine, su un dominio nuovo, con sola pubblicità, non arriva lì in 36 mesi con i numeri che vediamo oggi. La soglia dei 5.000 € con la sola pubblicità chiede un sito grande dieci volte il nostro migliore.

Questo è un risultato, non un fallimento della ricerca. Vuol dire: **la regola del 19/11 sta funzionando**. Blocca siti che avrebbero reso 100–800 €.

## 6. Raccomandazione

1. **Nessun sito nuovo.** Né prima né dopo il 1/12. Nessun candidato ha i numeri.
2. **Tenere il giardinaggio come prima riserva.** È l'unico con domanda misurata, dati ufficiali tutti leggibili e la categoria che paga di più. Se un giorno Massimiliano vuole una sola prova fuori soglia, è questa. Va decisa entro il 20/12: la stagione parte a febbraio e Google ha bisogno di sei settimane.
3. **Usare il fatto nuovo sui siti che ci sono.** Casa e giardino paga il doppio in Europa (5,16 $). Heat Pump Grants UK e Solare da Balcone sono lì. Prima di aprire altro, conviene capire perché sono a 0 visite.
4. **Il lavoro che rende di più oggi resta quello sui tre siti con visite** e sul canale ChatGPT (330 visite a settimana, più di Google).

## 7. Piano di costruzione (solo se Massimiliano dice sì a una prova fuori soglia)

Scrivo il piano per i primi due, come chiesto. Nessuno dei due passa la regola: servirebbe un sì esplicito.

### A. Giardinaggio USA — «zona, gelate, quando seminare»

**Pagine: 85 in tutto.**

| Pagine | Numero | Che cosa risponde |
|---|---|---|
| Strumento per codice postale | 1 | Scrivi il codice: zona, ultima gelata, prima gelata, date di semina di 30 ortaggi |
| Una pagina per Stato | 51 | Tabella delle zone per città, date medie delle gelate per stazione NOAA |
| Una pagina per ortaggio | 30 | «Quando seminare i pomodori»: tabella per zona, calcolata dalle gelate |
| Metodo, fonti, chi siamo | 3 | Da dove viene ogni numero |

Niente pagine per codice postale (sarebbero 40.000 pagine modello). Il codice postale si risolve nello strumento.

**Fonti.**
- Zone: file PRISM / USDA 2023 (200 oggi).
- Gelate: medie NOAA 1991-2020 per stazione (200).
- Distanza dalla gelata per ortaggio: tabelle dei servizi agrari delle università. Da leggere a mano, una fonte per ortaggio, con il link accanto.

**Ore: 40.** Raccolta dati 10. Strumento 8. Pagine e testi 12. Revisione indipendente 6. Controlli 4.

**Guadagno: 155 / 827 / 4.145 €/anno a 36 mesi.** A 12 mesi circa 250 € centrali. Resa centrale: 21 €/ora.

**Che cosa può andare male.** almanac.com fa già lo stesso per codice postale. Un dominio nuovo dopo un aggiornamento di Google parte piano. La domanda dura quattro mesi.

**Prova per decidere dopo.** 100 visite a settimana da Google entro il 30/4/2027. Sotto, si ferma.

### B. Radon — «zona e livelli per contea e per Stato»

**Pagine: 75 in tutto.**

| Pagine | Numero | Che cosa risponde |
|---|---|---|
| Una pagina per Stato | 51 | Tabella di tutte le contee: zona EPA, media e mediana delle prove (dove il CDC ha il dato), numero di case provate |
| Ricerca per contea | 1 | Scrivi la contea: zona e numeri |
| Risposte precise | 20 | Livello sicuro (4 pCi/L), costo dell'impianto, obbligo di dichiararlo alla vendita per Stato |
| Metodo e fonti | 3 | |

**Fonti.** File EPA delle zone (200). API CDC «Radon Tests from Labs» (200; solo una parte degli Stati). Uffici del radon dei singoli Stati per gli obblighi di legge.

**Ore: 35.** Guadagno: 15 / 194 / 2.303 €/anno. Resa centrale: 6 €/ora.

**Che cosa può andare male.** La domanda è una mia stima, non misurata. È un tema di salute: ogni pagina deve dire «prova la tua casa, la zona non basta» (lo dice l'EPA). I dati delle zone sono del 1993.

**Giudizio.** Non conviene. La scrivo perché è la seconda in classifica, non perché la consiglio.

## 8. Limiti di questo studio

- La domanda di 7 candidati su 8 è stimata senza strumento. Può essere sbagliata anche del doppio. Non cambia il verdetto: anche raddoppiando la domanda, il migliore resta sotto 2.000 € centrali.
- Il 13,37 $ di Casa e giardino è un dato del 2024 e vale per le «Americhe», non solo per gli USA.
- GoatCounter mi ha bloccato: non ho riletto le quattro settimane pagina per pagina.
- Concorrenti letti in fretta. Per nessun candidato ho dimostrato un vuoto su 5 esempi: per la regola del 10/11 il voto massimo sarebbe comunque 5.
- Settori già chiusi nei nostri studi e quindi non rifatti: caccia e pesca USA (19/10), autotrasporto (14/11), Medicare e Social Security (14/11), piccole successioni e diritto per Stato (13/11), prezzi agricoli in Italia (12/11), animali (18/11).

## Fonti lette oggi

- AdSense, dati del calcolatore: https://adsense.google.com/start/calculator-data.json
- PRISM / USDA, zone per codice postale: https://prism.oregonstate.edu/phzm/
- NOAA, medie 1991-2020: https://www.ncei.noaa.gov/data/normals-annualseasonal/1991-2020/access/
- EPA, zone del radon: https://www.epa.gov/radon/epa-map-radon-zones
- CDC, prove del radon: https://www.cdc.gov/environmental-health-tracking/php/data-research/radon-testing.html
- ENERGY STAR, valori R: https://www.energystar.gov/saveathome/seal_insulate/identify-problems-you-want-fix/diy-checks-inspections/insulation-r-values
- PNNL, zone per contea: https://basc.pnnl.gov/guide-determining-climate-zone-county-data-files
- hvacbase.org (concorrente): https://www.hvacbase.org/climate-zone-map
- USDA NASS, affitti: https://www.nass.usda.gov/Surveys/Guide_to_NASS_Surveys/Cash_Rents_by_County/
- IRS, tassi AFR: https://www.irs.gov/applicable-federal-rates
- NCHFP, conserve: https://nchfp.uga.edu/how/can
- National Gardening Survey 2026: https://gardenresearch.com/view/national-gardening-survey-2026-edition/
- Rayno, vetri oscurati (concorrente): https://raynofilm.com/blog/window-tint-laws-by-state/
- radonresources.com (concorrente): https://radonresources.com/ohio
