# Verifica indipendente: "Libri di testo: costo per scuola e classe con la lista nel carrello Amazon.it" (10/11/2026)

Idea verificata: riga della coda in `DA-PUBBLICARE.md` (voto del ricercatore 6,5; 700 / 3.800 / 16.000 €/anno), fonte `fronti-2026-11-07-sera-settori.md`.

Tutto letto con curl dal nostro server il 10/11/2026. Nessun blocco aggirato: dove una pagina risponde 403/503 o con una pagina anti-robot lo scrivo, e quel punto resta "non verificato".

## 0. Verdetto in breve

| | Ricercatore (7/11) | Verifica (10/11) |
|---|---|---|
| Voto | 6,5 | **5** |
| €/anno a 18 mesi (prudente / centrale / ottimista) | 700 / 3.800 / 16.000 | **300 / 1.900 / 18.000** |
| Dati ufficiali | "ci sono" | **confermati e buoni** (20 Regioni, 756 MB, IODL 2.0, unione con l'anagrafe 100 %), ma **escono da luglio**, non da maggio |
| Carrello Amazon con più libri e tag | "da verificare" | **NON confermato**: la pagina ufficiale del modulo "Add to Cart" non esiste più (API vecchia dismessa); Amazon blocca il nostro server (503); il **40 % delle classi** ha almeno un libro con ISBN 979, che non ha ISBN-10 e quindi non entra nel carrello senza l'API |
| Concorrenti | "nessuno dà il totale per classe" | **sbagliato**: Libraccio dà il totale per classe (nuovo + usato, "Tot. € 276,29 Risparmi € 68,26") e mette tutta la lista nel carrello in un clic; Libreria Scolastica ha una pagina statica per ogni classe con "Totale prodotti selezionati"; Amazon ha il suo "adozioni" |

**NO-GO come sito nuovo.** Le 4 prove:

| Prova | Esito | Perché |
|---|---|---|
| 1. Domanda reale | **SÌ** | autocomplete pieno, anche a novembre, con nomi di scuole e città (sez. 4) |
| 2. Dati leggibili | **SÌ, con un limite** | open data ottimo; ma il primo file dell'anno nuovo arriva a luglio, mentre le scuole e i librai (banca dati AIE) pubblicano le liste da fine maggio-giugno |
| 3. Pagatore attivo | **A METÀ** | Amazon.it Libri 5 % letto oggi e tag attivo; ma il conto è ancora nel periodo "3 vendite in 180 giorni", e il pulsante "tutta la lista nel carrello" non è né documentato né completo (ISBN 979). Restano i link normali libro per libro, che sono permessi |
| 4. Nessuno lo fa già meglio | **NO** | Libraccio, Libreria Scolastica, Amazon, Mondadori Store fanno già lista per classe + totale + carrello in un clic, con i dati AIE (prima dei nostri) e con l'usato, che noi non possiamo offrire |

Due prove su quattro non passano; il voto scende a 5 e il centrale a 1.900 €/anno (asticella dei siti nuovi: voto ≥ 7 e ≥ 5.000 €). La riga esce dal "secondo posto" della coda.

**Quel che resta di buono (riserva, non sito):** i numeri che nessun libraio mostra, cioè la spesa reale per classe confrontata con il tetto ministeriale e le mediane per anno e indirizzo. È materiale per una **sezione piccola (10-40 pagine) su un sito italiano esistente**, non per 17.000 pagine per scuola. Stima 150 / 600 / 2.500 €/anno, 10-14 ore di agenti (sez. 8).

## 1. DATI (prova 2: sì)

**Adozioni.** Catalogo: `https://dati.istruzione.it/opendata/opendata/catalogo/elements1/?area=Adozioni%20libri%20di%20testo` (200). Venti dataset, uno per Regione (`DS0701ALTABRUZZO` … `DS0720ALTVENETO`), ognuno in CSV, JSON, XML, RDF. File: `…/elements1/ALT<REGIONE>000020260909.csv`.

Scheda del dataset (pagina "leaf", 200): pubblicato da DGCASIS; "Data pubblicazione 09/09/2026, Dati al 09/09/2026"; **"Periodicità rilevazione: Settimanale nel periodo luglio/novembre"**; **Licenza IODL 2.0**; contenuto: "adozioni dei libri di testo per la scuola primaria e la secondaria di I e II grado".

Dimensioni lette con HEAD (CSV): Lombardia 114,6 MB, Campania 88,6, Lazio 71,6, Sicilia 68,6, Veneto 58,2, Puglia 53,8, Emilia-Romagna 52,4, Piemonte 50,4, Toscana 45,5, Calabria 28,6, Marche 21,2, Sardegna 20,7, Abruzzo 16,7, Liguria 16,3, Friuli-VG 15,2, Umbria 11,7, Trentino-AA 9,0, Basilicata 7,7, Molise 4,1, Valle d'Aosta 1,4. **Totale 756 MB**, tutte e 20 le Regioni rispondono 200.

Colonne (16): `CODICESCUOLA, ANNOCORSO, SEZIONEANNO, TIPOGRADOSCUOLA (EE/MM/NO/NT), COMBINAZIONE (indirizzo), DISCIPLINA, CODICEISBN, AUTORI, TITOLO, SOTTOTITOLO, VOLUME, EDITORE, PREZZO, NUOVAADOZ, DAACQUIST, CONSIGLIATO`.

**Qualità, due Regioni scaricate e contate:**

| | Valle d'Aosta | Umbria |
|---|---|---|
| Righe | 6.871 | 54.315 |
| Codici scuola | 120 (45 secondarie) | 501 (222 secondarie) |
| Classi | 817 | 5.224 |
| Prezzo mancante / zero | 0 / 15 | 34 / 394 |
| ISBN non di 13 cifre | 0 | 394 (codici "AIE…": materiali senza ISBN) |
| Righe doppie (stessa classe e ISBN) | 0 | 0 |
| "Da acquistare" Sì | 4.850 (71 %) | 32.415 (60 %) |
| Nuove adozioni | 1.005 (15 %) | 7.846 (14 %) |
| ISBN 979 tra i libri da comprare (secondarie) | 6,4 % | 9,0 % |

Mediana della spesa per classe (solo "da acquistare"), Umbria: prima media 315 € (12 libri), seconda 124 €, terza 138 €; prima superiore 330 € (12 libri), seconda 191 €, terza 308 €, quarta 224 €, quinta 235 €; primaria 25-57 € (pagata dal Comune). Valle d'Aosta: 284 / 175 / 144 e 371 / 169 / 280 / 222 / 242. I numeri del ricercatore sono confermati.

Statali e paritarie: ci sono entrambe (codici con "1M", "1A" = paritarie).

**Controllo incrociato con un libraio:** classe 1A della scuola PGMM834013 (Assisi): 13 libri nell'open data, 13 su 14 ISBN uguali alla pagina di Libraccio per la stessa classe. Il dato ministeriale e la banca dati AIE coincidono.

**Anagrafe scuole** (stesso portale, area "Scuole"): `SCUANAGRAFESTAT20262720260901.csv` (13,1 MB, 50.273 sedi statali) e `SCUANAGRAFEPAR20262720260901.csv` (11.331 paritarie). Campi: Regione, Provincia, codice e nome dell'istituto di riferimento, codice scuola, nome, indirizzo, CAP, Comune, tipo di scuola, sito web. **Unione con le adozioni: 501 codici umbri su 501 trovati.** Secondarie statali: 7.496 di primo grado + circa 7.300 di secondo grado; paritarie 611 + 1.527. In tutto circa **17.000 scuole secondarie** e 6.648 Comuni.

**Tetti di spesa 2026/27:** pagina `https://www.mim.gov.it/web/guest/libri-di-testo` (200): circolare n. 97152 del 31/3/2026, **D.M. 51/2026** (26/3/2026) con due allegati PDF, letti:
- Allegato 1, secondaria di I grado: **I anno 303 €, II anno 121 €, III anno 136 €**.
- Allegato 2, secondaria di II grado, per indirizzo e anno: classico 346 / 199 / 395 / 326 / 336; scientifico 331 / 230 / 331 / 297 / 321; scienze applicate e sportivo 314 / 215 / 331 / 297 / 321; linguistico 346 / 199 / 321 / 326 / 336; scienze umane (anche economico-sociale) 331 / 189 / 321 / 244 / 256; artistico 283 / 189 / 267 / 203 / 213; tecnico economico 329 / 215 / 297 / 267 / 233; tecnico tecnologico 346 / 230 / 321 / 285 / 244; professionali da 267-324 (I anno) a 128-149 (V anno), 11 indirizzi.
- Art. 1, c. 3: tetti ridotti del 10 % se i testi sono in versione mista, del 30 % se solo digitali.

Dato nuovo calcolato (Umbria, medie): la spesa "da acquistare" supera il tetto in 276 prime su 376, 232 seconde su 374, 217 terze su 378; oltre il tetto + 10 % in 21, 43 e 21 classi. È il confronto che i librai non mostrano (ma va scritto con cautela: il tetto riguarda l'intera dotazione e ha le riduzioni dell'art. 1).

**Il limite dei dati: il calendario.** I collegi docenti adottano entro maggio; scuole, AIE e librai pubblicano le liste da fine maggio-giugno; l'open data parte a **luglio**. A maggio e giugno il nostro sito mostrerebbe le liste dell'anno prima (uguali per circa l'85 %, ma con la data sbagliata), proprio mentre i concorrenti hanno già quelle nuove.

## 2. CARRELLO AMAZON (prova 3: a metà)

**Commissione:** `https://programma-affiliazione.amazon.it/help/node/topic/GRXPHT8U84RAYDXZ` (200), tabella "Commissioni Pubblicitarie Standard del Sito Amazon IT": **Libri 5,0 %** (insieme a Casa, Fai da Te, Auto e Moto, Libri Kindle). Confermata.

**Regole lette** (`…/help/operating/policies`, 200):
- sessione di **24 ore** dal clic; se in quelle 24 ore il cliente mette il prodotto nel carrello, la vendita conta se l'ordine è completato **entro 89 giorni**;
- prezzi: "il tuo Sito può mostrare prezzi e disponibilità solo se (a) forniamo un link in cui il prezzo e la disponibilità sono esposti, o (b) ottieni i dati tramite Creators API o PA API". Mostrare il **prezzo di copertina ministeriale** (non il prezzo Amazon) è difendibile, ma va etichettato chiaramente come "prezzo dichiarato dalla scuola al Ministero" e mai come prezzo Amazon;
- vietati i link che non fanno capire che si va su Amazon e i reindirizzamenti automatici; il pulsante deve dire "Amazon".

**Il modulo "Add to Cart" (carrello con più articoli):**
- la pagina ufficiale che lo descriveva, `https://webservices.amazon.com/paapi5/documentation/add-to-cart-form.html`, oggi rimanda all'avviso **"PA-API 5 Deprecation Notice"**: la Product Advertising API 5 è dismessa e sostituita dalla Creators API; la versione italiana (`webservices.amazon.it/…`) risponde 403;
- nella documentazione nuova (`affiliate-program.amazon.com/creatorsapi/docs/en-us/…`: introduzione, concetti, migrazione, FAQ, registrazione; tutte 200) **la parola "cart" non compare mai**: il modulo non è più documentato;
- la Creators API "is available only to associates who have referred qualified sales and have been accepted into the program": noi siamo ancora nel periodo di prova (3 vendite in 180 giorni dal 30/10/2026);
- prova tecnica dal server: `https://www.amazon.it/gp/aws/cart/add.html?ASIN.1=…&Quantity.1=1…` (senza il nostro tag, una sola richiesta) → **503 "Ci dispiace"**; `https://www.amazon.it/dp/<ISBN-10>` per 3 ISBN reali dell'open data → pagina anti-robot ("Fai clic sul pulsante qui sotto per continuare a fare acquisti"). Non aggirato, mi sono fermato a 4 richieste. **Quindi: non verificato che l'indirizzo funzioni ancora, né che /dp/ISBN-10 porti al libro giusto, né quanti libri scolastici Amazon venda.** Può verificarlo solo Massimiliano dal suo browser (2 minuti), ma non cambia il verdetto.

**Il problema che resta anche se l'indirizzo funziona: gli ISBN 979.** Il carrello vuole l'ASIN; per i libri l'ASIN è l'ISBN-10, che esiste solo per i 978. In Umbria il 9 % dei libri da comprare è 979 (quota in crescita: gli editori italiani usano ormai il prefisso 979-12), e **il 40,1 % delle classi secondarie (1.318 su 3.289) ha almeno un libro 979**: per 4 classi su 10 "tutta la lista in un clic" sarebbe una lista incompleta, a meno di cercare l'ASIN con l'API (che non abbiamo) o leggendo Amazon in automatico (vietato e bloccato).

**Che cosa è sicuramente permesso:** un link normale per libro (`https://www.amazon.it/dp/<ISBN-10>?tag=guideesami-21`) o un link di ricerca per ISBN-13. Basta un clic per aprire la sessione di 24 ore, quindi il guadagno non dipende dal carrello multiplo; ma sparisce il "pezzo nuovo" su cui l'idea si reggeva, e Amazon ha già il suo cerca-classe ("libri scolastici amazon adozioni", "per regione", "sconto 15" in autocomplete).

**Conto Amazon:** attivo dal 30/10/2026, esaminato dopo 3 vendite in 180 giorni (scadenza circa fine aprile 2027). Un sito che vende solo da luglio non aiuta a superare l'esame; se il conto non lo supera con gli altri siti, a luglio il tag non esiste.

## 3. CONCORRENZA (prova 4: no)

| Chi | Che cosa ha (letto oggi) | Totale per classe | Tutta la lista in un clic | Usato |
|---|---|---|---|---|
| **Libraccio** `libraccio.it/scolastici` (200) | "Trova i libri della tua classe anno scolastico 2026-2027", tutta Italia; percorso Regione → Provincia → Città → tipo → scuola (con codice ministeriale) → classe; ricerca per nome o codice; **una pagina indicizzabile per classe** con titolo "Libri per 1A Sec I Grado Assisi 2 di Assisi, nuovi e usati" e canonical; "La banca dati è utilizzata su licenza dell'Associazione Italiana Editori" | **Sì**: "Scelta conveniente: Usato (7) Nuovo (6) Tot. € 276,29 Risparmi € 68,26" e "Solo nuovo (13)" | **Sì** ("aggiungere con un solo click tutti i libri") | **Sì** |
| **Libreria Scolastica** `libreriascolastica.it` (200) | "Adozioni 2026/2027", "aggiornamento dati circa al 97 %"; **pagine statiche** Regione → Provincia → Comune → tipo → scuola (con codice nell'indirizzo) → classe, titolo "Libri 1A … Amelia 2026/2027: Offerte e Sconti Testi Scolastici Nuovi e Usati" | **Sì** ("Totale prodotti selezionati", "Risparmi") | Sì (selezione e carrello) | Sì |
| **Amazon.it** | cerca-classe per le adozioni e sconto 15 % (dall'autocomplete: "amazon adozioni libri di testo 2026 27", "libri scolastici amazon per regione", "sconto 15"); pagina 503 dal server, non letta | non letto | non letto | sì (venditori terzi) |
| **Mondadori Store** `mondadoristore.it/libri-scolastici` (200) | "Cerca la tua classe, seleziona i libri e ordina in pochi passaggi; tutte le adozioni ufficiali aggiornate" | non letto (ricerca in JavaScript) | sì | no |
| Coop, Conad, Esselunga | in autocomplete tra i primi ("libri di testo esselunga / coop / conad"): prenotazione con sconto in buoni spesa | — | — | — |
| Sito della scuola | pubblica il PDF ufficiale della lista (è il primo risultato atteso per "libri di testo ‹nome scuola›") | sì (il PDF AIE ha il totale) | no | no |
| IBS, Feltrinelli, Libreria Universitaria | percorsi provati 404; Unilibro 403 (Cloudflare); scuolabook e coopdiscuola non raggiungibili (502 del proxy) | — | — | — |

**Il "buco" indicato dal ricercatore ("nessuno dà il costo totale per classe") non c'è.** Lo danno Libraccio e Libreria Scolastica, con in più l'usato (cioè un totale più basso del nostro) e la lista che arriva prima della nostra. La composizione dei risultati Google non è leggibile (motori chiusi a curl), ma per le ricerche con il nome della scuola i concorrenti hanno già una pagina per classe ciascuno.

**Che cosa non fa nessuno di quelli letti:** il confronto con il tetto ministeriale (nessuna occorrenza di "tetto" nelle pagine di classe), la quota di nuove adozioni, le mediane per anno, indirizzo, Provincia. È un contenuto informativo, non un negozio: vale una sezione, non un sito.

## 4. DOMANDA (prova 1: sì)

Autocomplete Google `gl=it&hl=it`, 40 domande il 10/11/2026 (fuori stagione):

- **con il nome della scuola (coda lunga):** "libri di testo liceo" 10 (5 indirizzi + scuole per nome: "liceo nobel torre del greco", "liceo scientifico volta reggio calabria"…); "libri di testo scuola media" 10 ("dante alighieri", "pascoli", "verga vercelli", "garibaldi palermo", più "amazon", "esselunga", "sono detraibili"); "lista libri scuola media" 10 (8 scuole per nome e città); "lista libri liceo scientifico" 10 (7 scuole); "libri di testo itis" 10 (9 città); "libri di testo liceo galilei" 10; "libri di testo perugia" 10 (4 scuole + contributo, bonus, Comune);
- **con il venditore:** "libri di testo" 10 ("2026/27", "amazon", "esselunga", "coop", "conad", "usati"); "libri scolastici 2026/27" 10 (amazon, coop, conad, esselunga, usati, sconti, libraccio); "adozioni libri di testo" 10 (amazon, libraccio, argo, aie); "libri scolastici amazon" 10; "amazon adozioni" 8; "libraccio adozioni" 4; "libri scolastici usati" 10;
- **sul costo:** "costo libri scolastici" 10 (medie, superiori, elementari; ma anche "730", "detrazione", "rimborso"); "quanto si spende per i libri" 5; "libri prima media costo" 4 ("costo totale libri prima media"); "quanto costano i libri del liceo" 3; "quanto costano i libri della prima media" 2;
- **sul tetto:** "tetto di spesa libri" 10 e "tetti di spesa libri di testo" 10 ("2026/27", "tabella", "scuola secondaria secondo grado", "prima media"): pubblico misto, molti insegnanti e segreterie;
- **deboli:** "codice scuola libri di testo" 1, "codice meccanografico libri" 2, "lista libri prima superiore" 1, "caro libri 2026" 1.

Lettura: la domanda c'è ed è grande, ma chi cerca "libri di testo ‹scuola›" vuole la lista (la trova sul sito della scuola o dal libraio) e chi aggiunge "amazon / libraccio / coop" ha già scelto il negozio. La parte in cui avremmo qualcosa di nostro (costo, tetto) è la più piccola.

**Stima delle visite in stagione (luglio-settembre 2027, prima stagione; a maggio-giugno non abbiamo i dati nuovi).** Metodo: 17.000 scuole secondarie × pagine di scuola; un dominio nuovo con pagine in serie, contro due librai con una pagina per classe e i siti delle scuole. Ipotesi sulla quota di scuole per cui otteniamo visite e sulle visite per scuola:
- prudente: 4 % delle scuole (680) × 5 visite + 600 dalle pagine nazionali = **4.000**;
- centrale: 10 % (1.700) × 7 visite + 3.000 dalle pagine "costo" e "tetto" = **15.000**;
- ottimista: 35 % (6.000) × 13 visite + 12.000 = **90.000**.

## 5. SOLDI

**Per ordine:** lista di prima superiore 330 € × 0,85 (sconto scolastico 15 %) × 5 % = 14 €; lista mediana di tutti gli anni (circa 230 €) = 9,8 €; ma si compra spesso solo una parte (usato, libri dei fratelli, supermercato, buoni regionali): **6 € centrali** per ordine (5 prudente, 6,5 ottimista).

**Quota di visite che compra su Amazon entro 24 ore dal nostro clic:** 1,5 % / 2 % / 3 % (il ricercatore usava 2-3,5 %; tolgo qualcosa perché senza carrello multiplo servono più passaggi e perché Libraccio offre l'usato).

**Pubblicità:** RPM Italia ipotizzato 2 / 3 / 4 € per 1.000 pagine (nessuna cifra pubblica letta: è un'ipotesi), 1,6-2 pagine a visita.

| | Visite | Amazon | Pubblicità | **Totale €/anno** |
|---|---|---|---|---|
| Prudente | 4.000 | 4.000 × 1,5 % × 5 € = 300 | 4.000 × 1,6 × 2 / 1.000 = 13 | **≈ 300** |
| Centrale | 15.000 | 15.000 × 2 % × 6 € = 1.800 | 15.000 × 1,8 × 3 / 1.000 = 81 | **≈ 1.900** |
| Ottimista | 90.000 | 90.000 × 3 % × 6,5 € = 17.550 | 90.000 × 2 × 4 / 1.000 = 720 | **≈ 18.000** |

A 18 mesi (maggio 2028) è passata una sola stagione piena.

**Altri pagatori:** Libraccio ha un programma di affiliazione vero (`libraccio.it/pg/partnership`, 200: Awin, TradeDoubler ID 238295, TradeTracker; la pagina cita proprio "la banca dati delle adozioni"), ma **senza percentuale scritta**: non è un pagatore "con cifra letta". IBS ha la voce "Programma di affiliazione" nel piè di pagina (cifra non letta). Mondadori Store, scuolabook: nessuna cifra. Il correttivo del ricercatore ("Libraccio e IBS: pagina affiliati 404") era impreciso: il programma Libraccio esiste, ma mandargli traffico vuol dire fare da vetrina al concorrente che fa già tutto meglio.

## 6. RISCHI

1. **Concorrenza diretta e più forte** (prova 4): lista, totale, carrello e usato esistono già, con dati che arrivano 4-6 settimane prima dei nostri.
2. **Carrello multiplo**: non documentato, legato a un'API dismessa, incompleto per il 40 % delle classi (ISBN 979).
3. **Conto Amazon in prova** fino a circa fine aprile 2027; il sito non genera vendite prima di luglio.
4. **Pagine in serie su dominio nuovo**: 17.000 scuole × classi = oltre 100.000 pagine quasi uguali; rischio che Google ne indicizzi poche.
5. **Esattezza**: le adozioni cambiano tra luglio e novembre (file settimanale); servirebbero data, fonte e link alla scuola su ogni pagina, e un aggiornamento almeno mensile in stagione (756 MB a giro).
6. **Stagione di 10 settimane utili** (luglio-metà settembre), poi quasi zero per 9 mesi.
7. Legale: nessun dato personale (scuole, classi, libri: dati pubblici, IODL 2.0 con citazione della fonte). Nessun problema qui.

## 7. Voto corretto: 5 su 10

- Domanda: forte (+).
- Dati: ufficiali, gratuiti, puliti (+), ma tardivi rispetto ai concorrenti (−).
- Pagatore: 5 % reale ma su ordini parziali, conto in prova, pulsante chiave non garantito (−).
- Concorrenza: due librai nazionali più Amazon fanno già il prodotto, meglio (− −).
- Centrale 1.900 €/anno contro un'asticella di 5.000 €.

**NO-GO come sito nuovo.** Non serve il piano di costruzione completo. Nomi liberi controllati comunque (.com, RDAP Verisign 404 = libero): costolibriscuola, quantocostanoilibri, libriperclasse, tettolibri, costolibriditesto, spesalibri: tutti liberi; i .it non verificabili (RDAP del registro .it non raggiungibile dal server).

Che cosa farebbe cambiare il verdetto (tutte e tre insieme): (a) Amazon documenta di nuovo un carrello multiplo per gli Affiliati oppure abbiamo la Creators API per trovare gli ASIN dei 979; (b) il conto Amazon.it ha superato le 3 vendite; (c) il Ministero anticipa l'open data a giugno. Senza (a) e (c) restiamo una copia più lenta di Libraccio.

## 8. Riserva: sezione piccola "quanto costano davvero i libri" (non sito)

Regola del 5-7/11: le idee automatiche a costo zero si costruiscono come sezione anche se piccole. Questa lo è, ma **non è urgente** (stagione a luglio) e va decisa dal manager della rete insieme al sito italiano che la ospita.

- **Che cosa:** 10-40 pagine calcolate dai 20 file: spesa mediana reale per anno (prima media, prima superiore…) e per indirizzo (i 24 del D.M. 51/2026) confrontata con il tetto; quante classi lo superano, per Regione e Provincia; quota di nuove adozioni (dove l'usato non esiste); tabella dei tetti 2026/27; una pagina "come leggere la lista" (da acquistare, consigliato, nuova adozione).
- **Dati:** script che scarica i 20 CSV (756 MB, non nel repository: solo i risultati aggregati), unisce l'anagrafe, calcola le mediane; `verifica.py`: numero di Regioni = 20, righe per Regione entro ±15 % dell'anno prima, prezzi 0 esclusi, totali ricalcolati su 5 classi campione confrontati a mano, data e fonte presenti in ogni pagina, tetti uguali agli allegati del D.M.
- **Guadagno:** link normali Amazon al reparto libri scolastici con il tag (dichiarazione "In qualità di Affiliato Amazon…" in pagina), pubblicità. Nessun prezzo Amazon mostrato.
- **Stima:** 150 / 600 / 2.500 €/anno (2.000 / 6.000 / 20.000 visite × 1 % / 1,5 % / 2 % × 5-6 € + pubblicità). Ore: 10-14 di agenti, 0 di Massimiliano. Da pubblicare entro maggio 2027 con i dati 2026/27, aggiornare a fine luglio 2027.
- **Quando:** dopo i lavori già in coda; non prende il posto di nessuno.

## 9. Fonti lette (10/11/2026)

- Adozioni: `dati.istruzione.it/opendata/opendata/catalogo/elements1/?area=Adozioni libri di testo` e scheda `leaf?…datasetId=DS0719ALTVALLEDAOSTA`; file `ALTVALLEDAOSTA000020260909.csv`, `ALTUMBRIA000020260909.csv` (scaricati), gli altri 18 con HEAD.
- Anagrafe: `…/elements1/SCUANAGRAFESTAT20262720260901.csv`, `SCUANAGRAFEPAR20262720260901.csv`.
- Tetti: `mim.gov.it/web/guest/libri-di-testo`, D.M. 51/2026 e allegati 1 e 2 (PDF).
- Amazon: `programma-affiliazione.amazon.it/help/node/topic/GRXPHT8U84RAYDXZ`, `…/help/operating/policies`, `…/help/operating/agreement`; `webservices.amazon.com/paapi5/documentation/add-to-cart-form.html` (ora avviso di dismissione); `affiliate-program.amazon.com/creatorsapi/docs/en-us/` (introduction, concepts, migrating…, frequently-asked-questions, onboarding/register-for-creators-api); `amazon.it/dp/…` e `/gp/aws/cart/add.html` bloccati (anti-robot, 503).
- Concorrenti: `libraccio.it/scolastici` fino alla pagina della classe 1A di PGMM834013; `libraccio.it/pg/partnership`; `libreriascolastica.it` fino alla classe 1A di TRMM02200C; `mondadoristore.it/libri-scolastici`. Non letti: Amazon adozioni (503), Unilibro (403), orizzontescuola (403), scuolabook e coopdiscuola (502), IBS/Feltrinelli/Libreria Universitaria (404 ai percorsi provati), adozioniaie.it (solo pagina di accesso).
- Autocomplete: `suggestqueries.google.com/complete/search?client=firefox&gl=it&hl=it`, 40 domande.
