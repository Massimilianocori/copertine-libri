# Ricerca del 30/10/2026: calendari e date ufficiali ad alta domanda ricorrente

Settore assegnato: calendari e date ufficiali che la gente cerca ogni anno o ogni mese, in tutto il mondo e in più lingue. Vacanze scolastiche, festività e ponti, scadenze fiscali, date d'esame, saldi, caccia e pesca, rifiuti, pagamenti di pensioni e sussidi, giorni gratis e chiusure dei musei.

**Prove da cui parto.**
- EsameB1 vince con le date ufficiali per città e i titoli con "prossima data": 3.570 impressioni e 163 clic dall'apertura, posizione media 7,3 (Search Console, 30/10).
- Italy Strikes ha il motore dei calendari con file iCal (`italystrikes/genera.py`, righe 582-640: un `.ics` per settore e per città).
- Monetizzazione già attiva (`studio-business/strumenti/monetizzazione.json`): AdSense su 10 siti, DiscoverCars, Amazon.it, SafetyWing, italki. Viator: account creato, in analisi. Stay22: da chiedere.

**Letti prima di cominciare:**
- `ESPLORATE.md` per intero, fino alle ricerche del 30/10;
- `REGOLE-FISSE.md`, le due regole del 30/10;
- `CRUSCOTTO-RETE.md`, sez. 1, 2 e 2b;
- i rapporti del 30/10 (cloni EsameB1, numeri ufficiali, zone USA, UK-Irlanda, Canada-Australia);
- `italystrikes/NOTE.md`, per i blocchi delle fonti italiane.

**Già chiuse, che NON rivaluto da capo:**
- calendari scolastici per espatriati in inglese (studi 16 e 18);
- festivi e ora legale (studi 14, 17, 18 e caccia del 25/10);
- date dei pagamenti pubblici in inglese, cioè Social Security, Universal Credit, CCB e Centrelink (14/10);
- calendario laboral spagnolo (17/10);
- scadenze fiscali per espatriati (25/10);
- mercatini di Natale (studio 3);
- regole dei rifiuti (studio 18);
- caccia e pesca negli USA (19/10);
- test di medicina e concorso docenti (24/10);
- IMU (studio 5).

Dove la lingua o il pubblico sono nuovi (italiano, tedesco, francese, spagnolo; pensioni INPS; SNAP americano), li ho provati da capo e lo scrivo.

**Metodo.**
- Domanda: autocomplete di Google nel Paese e nella lingua giusti, circa 120 ricerche.
- Concorrenza: prima pagina dei risultati, con lo strumento di ricerca web (risultati americani: per le ricerche italiane è un'approssimazione).
- Fonti: curl dal server con codice HTTP, dimensione e contenuto letto.
- Soldi: stima con le assunzioni scritte.

---

## 0. Risposta in breve

**Nessuna candidata arriva a 8.** La migliore arriva a 7,5 ed è una sezione, non un sito.

**La lezione del settore.** I calendari "puri" sono già pieni in ogni lingua. Parlo di festività, ponti, vacanze scolastiche, pagamenti di pensioni e sussidi, scadenze fiscali e saldi:
- ogni mese ci scrivono i giornali (quifinanza, investireoggi, orizzontescuola, studenti.it, web.de, Merian, ADAC…);
- ci sono i grandi siti di calendari (schulferien.org, ferienwiki, schulferienplaner, timeanddate);
- a volte ha già il calendario l'ente stesso (INPS, Agenzia Entrate, education.gouv.fr).

Il buco c'è dove la data è legata **a un acquisto o a un posto da prenotare**, le fonti ufficiali sono sparse e i blog hanno date vecchie o in contrasto tra loro:
1. quando escono i biglietti delle grandi attrazioni, quando chiudono e quando sono gratis;
2. date e posti liberi dei test TOLC sede per sede: è la forma esatta di EsameB1.

| # | Candidata | Dove | Voto | € a 18 mesi (prudente / centrale / ottimista) | Ore |
|---|---|---|---|---|---|
| 1 | **Quando escono i biglietti, quando si chiude, quando è gratis: calendario ufficiale delle grandi attrazioni, con promemoria iCal** (Cenacolo, Vaticano, Colosseo, Pompei, Uffizi, Casa di Anna Frank, Alhambra, Sagrada Família, Acropoli…) | sezione nuova di **Before You Fly** (`/tickets/`), con link dalle pagine città di Italy Strikes | **7,5** | 300 / 1.100 / 4.000 | 16-24 |
| 2 | **TOLC sede per sede: prossime date, scadenza d'iscrizione, posti liberi o esauriti** (tabella CISIA letta ogni giorno) | sezione di **EsamiDiStato** | **6,5** | 50 / 150 / 400 | 8-12 |
| 3 | **Gomme invernali e catene, Paese per Paese e strada per strada, con le date, per chi noleggia l'auto** | aggiunta al blocco "Driving abroad" di Before You Fly (DiscoverCars già attivo) | **6** | 120 / 400 / 1.200 | 6-10 |
| 4 | Giorni gratis dei musei per città in Europa (Domenica al museo, Museumssonntag, Parigi, Atene) | solo dentro la n. 1 | 6,5 dentro la n. 1, 5 da sola | – | +4-6 |

**Da costruire come sezioni**, secondo la regola "rete fitta": costo zero e guadagno atteso positivo.
- **La n. 1, subito.** È l'unica sopra i 1.000 € nel caso centrale.
- **La n. 3, entro metà novembre**, se si fa. La stagione delle gomme invernali parte il 15/11 in Italia e l'1/11 in Austria; dopo, aspetterebbe un anno.
- **La n. 2, come sezione piccola.** Guadagno positivo ma sotto i 300 €/anno: si fa solo perché costa 8-12 ore e ripete la forma di EsameB1. Prima va letta la licenza di CISIA.

---

## 1. Candidata n. 1: biglietti, chiusure e giorni gratis delle grandi attrazioni (voto 7,5)

### Che cosa è
Una pagina per attrazione, più una pagina-calendario e un file iCal per attrazione. In alto c'è la risposta con la data, come in EsameB1.

Esempi di titoli in alto:
- "Last Supper: next ticket release …";
- "Anne Frank House: next release Tuesday 3 November 2026, 10:00 CET, for visits 14-20 December";
- "Colosseum: tickets for 1 December go on sale 1 November".

Poi tre cose:
- le chiusure dell'anno, cioè festività e giorni particolari ("Is the Vatican open on 8 December?");
- i giorni gratis (prima domenica del mese in Italia, ultima domenica ai Musei Vaticani, giorni gratis in Grecia);
- il riquadro "Sold out?", con visite guidate che includono il biglietto (Viator) e la riga di trasparenza.

Il calcolo della "prossima uscita" lo fa uno script ogni giorno, partendo dalla regola ufficiale di ogni attrazione. Un controllo settimanale confronta l'impronta delle pagine ufficiali e segnala quando una regola cambia.

### Domanda (autocomplete USA e Regno Unito, inglese, 30/10)
- **Uscita dei biglietti.**
  - "when do last supper tickets go on sale": 10 varianti, quasi tutte con il mese e l'anno ("for may 2026", "for september 2026", "for june 2026", "for october 2026", "for november").
  - "when do colosseum tickets go on sale / get released / become available": 10.
  - "when do vatican tickets go on sale / release": 10.
  - "when do alhambra tickets go on sale / when are alhambra tickets released": 7.
  - "anne frank house tickets release time / **ticket release date calculator** / does anne frank house release more tickets": 10.
- **Esauriti.** "colosseum tickets sold out (what to do / reddit / immediately)", "vatican tickets sold out what to do", "last supper tickets sold out", "sagrada familia tickets sold out", "neuschwanstein tickets sold out", "borghese gallery tickets how far in advance": tutte con 10 varianti.
- **Aperto o chiuso in un giorno preciso.**
  - "is the colosseum open on" con all saints day, christmas day, easter sunday, new year's day, good friday;
  - "is the vatican museum open on" con christmas eve, easter monday, new year's day;
  - "is the vatican open on" con august 15, january 1st;
  - "is pompeii open on" con ferragosto, may 1, christmas day;
  - "is the uffizi open on" con easter monday, "may 1 2026";
  - "colosseum closed dates 2026", "pompeii closed on tuesdays / in november": tutte con 10 varianti.
- **Gratis.**
  - "colosseum free sunday (tickets, hours, queue, tips)": 10;
  - "vatican museums free sunday": 10;
  - "pompeii free sunday": 9;
  - "acropolis free days (2026)": 10;
  - "first sunday of the month free museums" con barcelona, milan, rome, florence, paris, brussels, vienna, venice, italy: 10;
  - "prado free hours": 10;
  - "louvre free first friday": 9.
- **Lo stesso in italiano e in tedesco.** "domenica al museo" con 1 novembre, firenze, torino, reggia di caserta; "musei gratis domenica" con roma, napoli, milano, torino; "museumssonntag" con berlin, münchen, dresden, frankfurt, wien.

È la forma di EsameB1: una data ufficiale ripetuta, cercata con il mese e il luogo.

### Fonti (curl dal server, 30/10)

| Attrazione | Fonte | Esito | Cosa dice |
|---|---|---|---|
| Cenacolo (Milano) | `cenacolovinciano.org/en/` e `/en/info/` | **200** (120 e 140 kB) | Regola trimestrale scritta: settembre → nov-dic-gen, dicembre → feb-mar-apr, marzo → mag-giu-lug, giugno → ago-set-ott; "Additional tickets will go on sale every Wednesday at 12 noon". **Ma** la notizia dice "September–December 2026 go on sale Tuesday, June 23", che non torna con la regola: è proprio la pagina che corregge |
| Musei Vaticani | `museivaticani.va/.../museivaticani-mobile/en/info/tutti-gli-orari.html` | **200** | Orari, "every last Sunday of the month… free entry", pagina "Openings/Closures 2026–2027". PDF `calendario_musei.pdf` e `tickets.museivaticani.va`: 000 |
| Casa di Anna Frank | `annefrank.org/en/museum/tickets/` | **200** | "Every Tuesday at 10am CET all tickets become available for a visit six weeks later" |
| Pompei | `pompeiisites.org` (WordPress, API `wp-json` 200 JSON) | **200** | Comunicati e chiusure leggibili da API |
| Uffizi | `uffizi.it/en` | **200** (pagine interne da trovare: 2 percorsi 404) | – |
| Alhambra | `alhambra-patronato.es/en` | **200** | – |
| Sagrada Família | `sagradafamilia.org/en/` | **200** | – |
| Pantheon | `pantheonroma.com` | **200** | – |
| Palazzo Ducale (Venezia) | `palazzoducale.visitmuve.it` | **200** | – |
| Berlino, Museumssonntag | `museumssonntag.berlin/en` | **200** | Elenco mensile dei musei |
| Parigi, musei della città; Louvre | `parismusees.paris.fr`, `louvre.fr` | **200** | – |
| **Colosseo** | `colosseo.it`, `ticketing.colosseo.it` | **000** (connection reset) | Chiuso al server, come tutta la rete del Ministero della Cultura (`cultura.gov.it`, `beniculturali.it` 000). Stesso tipo di blocco del registro scioperi (vedi `italystrikes/NOTE.md`) |
| Galleria Borghese, Accademia di Firenze | siti ufficiali | **000** | – |
| Acropoli e giorni gratis in Grecia | `odysseus.culture.gr` 000, `culture.gov.gr` 403, `hhticket.gr` 403 | chiuse | – |
| Prado, Torre Eiffel | – | **403** | – |

**Licenza.** Si riprendono solo fatti (date, orari, regole), con il link alla pagina ufficiale. Non si copiano testi né immagini.

**Il punto debole.** Per Colosseo, Borghese, Accademia e Grecia la regola non si legge dal server. Va scritta a mano una volta, con la fonte, e ricontrollata da un browser in Italia (quello di Massimiliano) quando cambia, cioè poche volte l'anno. Per queste attrazioni il controllo automatico dei cambi non c'è: lo scrivo nelle pagine ("last checked …").

### Prima pagina di Google (30/10)
- **"when do last supper tickets go on sale for january 2027".** Ci sono european-traveler, alongdustyroads, artvisitguide.com e la sua copia `artvisitguide.pages.dev`, la pagina ufficiale e `lastsupperticket.com` (rivenditore). Le date si contraddicono: una guida dice "terzo mercoledì del secondo mese prima", un'altra "fine settembre"; la regola ufficiale stessa non torna con la notizia del 23/6.
- **"anne frank house ticket release date calculator".** Il calcolatore esiste già: `amsterdamexperiences.nl` (venditore di visite; è lo stesso che tiene il livello del Reno "oggi", vedi 29/10), più holland-explorer e amsterdam-explorer. Alcune pagine mostrano date di uscita già passate.
- **"colosseum closed dates 2026".** Domina il sito ufficiale (chiuso al nostro server), poi deeparrival, mamalovesrome e `artvisitguide.pages.dev`.
- **"is the vatican museum open on christmas eve".** Pagina ufficiale, poi blog e rivenditori: visitingthevatican, citywonders, thevaticantickets, vaticanmuseum.co, mamalovesrome, `vaticanbulletin.pages.dev`. Le chiusure si contraddicono (8, 25, 26 dicembre e 1° gennaio contro "chiuso la domenica").
- **"acropolis free days 2026".** realgreekexperiences, blogspot, `angelsathens-gr.pages.dev`, civitatis, grandpl. Si contraddicono ("prima e terza domenica" contro "prima domenica"; date di febbraio che non tornano).
- **"when do colosseum tickets go on sale".** Forum di Rick Steves, thebettervacation, goaskalocal, `departly.pages.dev`, archaeology-travel. Danno 30 giorni, 60 giorni, 7 giorni.

**Lettura.** Il buco c'è:
- nessuno tiene, per più attrazioni insieme, la **prossima** data di uscita calcolata dalla regola ufficiale, con il promemoria iCal;
- le pagine invecchiano e si contraddicono, che è la forma che gli assistenti premiano (lezione del 27/10).

Ma la famiglia non è vuota:
- per ogni attrazione c'è il blog del venditore di visite;
- su Anna Frank c'è già un calcolatore;
- compaiono siti automatici su `pages.dev`, che fanno pagine "opening hours 2026" e "tickets sold out".

Per questo il voto è 7,5 e non 8.

### Chi paga
- **Viator**: 8 %, cookie 30 giorni; account creato, in analisi. La visita guidata con il biglietto incluso è la risposta naturale a "sold out, what to do". Prezzo medio di una visita al Vaticano o al Colosseo: 60-90 €, quindi 5-7 € a prenotazione.
- **AdSense** su un pubblico americano e britannico che sta per spendere: già acceso su Before You Fly.
- **Dopo, se si iscrive:** GetYourGuide e Tiqets, che vendono anche i biglietti d'ingresso. Non sono iscritti né in elenco: li nomino, ma non li conto.

### Stima (assunzioni scritte)
- **Pagine.** 20 attrazioni × 3 (uscita biglietti, chiusure, giorni gratis), più la pagina-calendario e le pagine di 6 città: circa 70 pagine e 20 file iCal.
- **Visite a 18 mesi.** Prudente 600 al mese, centrale 2.000, ottimista 6.000, con picchi da marzo a settembre.
- **Resa per visita.**
  - AdSense: 0,015-0,02 € a visita (circa 10-14 € per 1.000 pagine viste, pubblico USA e Regno Unito, 1,4 pagine a visita).
  - Viator: clic sul riquadro "Sold out?" 8-10 %, conversione 4-5 %, 5-6 € a prenotazione, cioè circa 0,02-0,03 € a visita.
  - Totale: circa 0,04-0,05 € a visita.
- **A 18 mesi:** prudente **300**, centrale **1.100**, ottimista **4.000 €/anno**. L'ottimista è con GetYourGuide o Tiqets iscritti e più attrazioni.
- **A 12 mesi:** 100 / 500 / 2.000 €.
- **Prima entrata:** il mese dopo l'approvazione di Viator. AdSense subito.

### Ore e motori riusati: 16-24
- **iCal**: si copia il blocco di `italystrikes/genera.py`.
- **"Prossima data" in alto**: modello delle pagine città di EsameB1.
- **Lavoro nuovo:**
  - regole in un file JSON per attrazione: tipo di regola (giorni prima, giorno della settimana con ora, trimestrale), fuso orario, fonte, data dell'ultimo controllo;
  - calcolo giornaliero;
  - controllo settimanale dell'impronta delle pagine ufficiali leggibili.

### Dove si mette
**Before You Fly**, sezione `/tickets/`. Ha 206 pagine indicizzate e 2.610 impressioni in 28 giorni (al 21/10), e un pubblico "chi vola in Europa".

Non Italy Strikes, anche se il motore è suo: al 23/10 aveva **0 pagine indicizzate** e il verdetto è il 24/11. Dalle 44 pagine città di Italy Strikes basta un link "Museum closures and ticket dates in Rome" per collegare scioperi e chiusure. Le chiusure dei musei per assemblee sindacali sono un altro motivo di ricerca dei turisti.

### Voto: 7,5
Domanda forte, ripetuta e datata; buco nella "prossima data" calcolata e corretta; chi paga ha un nome. Toglie mezzo punto ciascuno:
- metà delle fonti più cercate è chiusa al server (Colosseo, Grecia, Borghese);
- per ogni attrazione c'è già qualcuno (venditori, calcolatore di Anna Frank, siti `pages.dev`);
- i soldi sono piccoli finché Viator non è approvato.

**Sale a 8** se a 30 giorni le prime 10 pagine pilota (Cenacolo, Anna Frank, Vaticano, Colosseo, Pompei) fanno almeno 1.500 impressioni, e se Viator è approvato.

### Prova a 30 giorni
Pubblicare prima 10 pagine: Cenacolo, Anna Frank, Vaticano chiusure, Vaticano gratis, Colosseo uscita biglietti, Colosseo gratis, Pompei chiusure, Uffizi, Alhambra, Sagrada Família. Si guardano impressioni, posizione e visite da chatgpt.com.

---

## 2. Candidata n. 2: TOLC sede per sede, con i posti liberi (voto 6,5)

### Che cosa è
Una pagina per tipo di TOLC × città o università. In alto:
- "Prossima data a Bologna: 10/11/2026, iscrizioni fino al 04/11, 71 posti liberi";
- l'elenco delle prossime date;
- lo stato "posti esauriti / disponibili", aggiornato ogni giorno;
- un iCal con le scadenze d'iscrizione.

È la forma di EsameB1, applicata ai test d'ingresso all'università.

### Fonte
`testcisia.it/calendario.php?tolc=ingegneria` (e `=economia`, `psicologia`, `scienze`, `farmacia`, `biologia`, `agraria`, `umanistica`, `lauree_professionalizzanti`): **200**, tabella HTML pulita.

Colonne: modalità (TOLC@UNI / TOLC@CASA), università, regione, città, fine iscrizioni, posti, stato, data del test. Solo per ingegneria, 51 righe di date nelle prossime settimane.

Esempio letto: "TOLC@UNI | Università degli studi del Molise | MOLISE | CAMPOBASSO | 04/11/2026 | 71 | POSTI DISPONIBILI | 10/11/2026"; Sapienza, Messina, Bergamo e Firenze "POSTI ESAURITI".

Licenza: **non letta**. Le condizioni di CISIA vanno lette prima di costruire (lezione del 23/10: lo stato 200 non basta). Sono comunque fatti (date e posti), con il link alla prenotazione ufficiale.

### Domanda (autocomplete Italia, italiano)
- "tolc i date": 10 (2026, 2027, disponibili, aperte, bologna, padova, polimi).
- "tolc psi date": 10 (padova, sapienza, torino, agosto).
- "tolc su date": 10 (bologna, padova, torino).
- "tolc b date": 10 (unisa, verona, torino, sapienza).
- "tolc e date": 10 (bologna, disponibili, 2027).
- "tolc i posti disponibili": 6, anche "posti disponibili tolc i politecnico di bari".
- "tolc e bologna": 10.

### Prima pagina
Per "tolc psi date disponibili padova 2026":
- testbuddy.it, sito che sembra automatico, con pagine `.md` per gli assistenti;
- studenti.it;
- PDF dei bandi delle università;
- il regolamento CISIA.

Nessuna pagina "TOLC a Padova: prossime date e posti". Però l'ente ha il motore: CISIA filtra già per TOLC, ed è lo stesso verdetto che ha bocciato gli esami nordici il 20/10.

### Chi paga
- AdSense su un pubblico italiano di 18-19 anni: resa bassa.
- Amazon.it (tag attivo) sui manuali di preparazione.
- Corsi di preparazione: nessun programma verificato.

### Stima
Visite a 18 mesi: 500 / 1.500 / 4.000 al mese, con picchi da febbraio a settembre. Resa circa 0,008 € a visita. Totale **50 / 150 / 400 €/anno**.

### Ore e dove si mette
- 8-12 ore: lettore della tabella, pagine per città, iCal (motore Italy Strikes), lettura giornaliera.
- Dove: sezione di **EsamiDiStato** (pubblico italiano degli esami). Porta anche pagine nuove e scansioni a un sito oggi poco indicizzato (7 pagine al 16/10).

### Voto: 6,5
Forma vincente e fonte perfetta, ma l'ente risponde già e il pubblico vale poco.

Si costruisce come sezione piccola solo per la regola "rete fitta": guadagno positivo, costo 8-12 ore. Sale a 7 se la licenza CISIA è chiara e se, a 30 giorni, le pagine città superano 300 impressioni.

---

## 3. Candidata n. 3: gomme invernali e catene con le date, per chi noleggia (voto 6)

### Domanda
- Inglese (Regno Unito e USA):
  - "winter tyres italy" con law, map, **car rental**, dates, e "sixt / europcar / hertz / avis winter tyres italy": 10;
  - "winter tyres france map 2025 / dates / law": 10;
  - "winter tyres austria dates": 7;
  - "snow chains italy car rental / mandatory", "snow chains france map": 10.
- Francese: "pneus hiver obligatoires quels départements", con italie, allemagne, suisse: 10.
- Italiano: "obbligo gomme invernali" con lombardia, piemonte, autostrada, tolleranza, svizzera, austria: 10.

### Fonti
- Italia: `mit.gov.it` 000, `stradeanas.it` 000, `autostrade.it` 200.
- Francia: `securite-routiere.gouv.fr` 200, `bison-fute.gouv.fr` 200, `data.gouv.fr` instabile (200 alla prima chiamata, tunnel chiuso alla seconda).
- Le regole per strada in Italia sono ordinanze di ANAS, delle Province e delle società autostradali: fonte frammentata.

### Prima pagina
- tyremap.com, con pagine automatiche "tyre-laws/<Paese>";
- Auto Europe, Green Motion, Zest e altri noleggiatori;
- comparis;
- forum.

Le date si contraddicono: 15/11-15/4, oppure 15/10-15/4 in Valle d'Aosta.

### Chi paga, stima e ore
- DiscoverCars (circa 20 $ a noleggio, cookie 365 giorni) è già online su 118 pagine di "Driving abroad".
- Stima a 18 mesi: **120 / 400 / 1.200 €/anno**, stagionale (novembre-aprile).
- 6-10 ore come aggiunta: una pagina per Paese (IT, FR, AT, DE, CH, SI) con le date, la regola per il noleggio e le righe per le strade principali.

### Voto: 6
Si fa solo **entro il 10-15/11**, oppure si rinvia all'autunno 2027.

---

## 4. Candidata n. 4: giorni gratis dei musei per città (solo dentro la n. 1)

- Domanda europea chiara: "first sunday of the month free museums" con 9 città; "museumssonntag" con 6 città tedesche e Vienna; "domenica al museo" e "musei gratis domenica" con 5 città italiane.
- Fonti:
  - Italia: la regola nazionale della prima domenica del mese e dei giorni 25/4, 2/6 e 4/11 sta sulla rete del Ministero della Cultura, **chiusa al server** (000). Si scrive a mano dalla norma, con il link.
  - Berlino e Parigi: 200.
  - Grecia: 403/000.
  - Prado: 403.
- Concorrenza:
  - italiano: initaly.it, in-lombardia, giornali;
  - inglese: thebettervacation, expatslivinginrome, thewomtravel, il portale del Comune di Milano.
- Da sola vale 5. Come terza colonna della n. 1 vale 6,5: stesse pagine, stesso pubblico.

---

## 5. Famiglie provate e chiuse (con le prove)

| Famiglia | Domanda (autocomplete) | Fonte | Prima pagina | Voto | Esito |
|---|---|---|---|---|---|
| Calendario scolastico per regione e ponti 2027 (IT). **Fatto nuovo**: San Francesco, 4 ottobre, di nuovo festa nazionale dal 2026 (L. 151/2025) | Fortissima: "calendario scolastico 2027" 10 (veneto, piemonte, lombardia, campania, emilia romagna); "ponti 2027" 10 ("scuola lombardia", "san francesco", "4 ottobre"); "festività 2027" 10 | MIM 200, regioni 200 | orizzontescuola (confronto regione per regione), studenti.it, greenme, scuolainforma, newsistruzione, quotidiano.net, panorama, virgilio | 3,5 | NO: ogni regione e ogni giornale rifà la tabella in giornata; il 4/10/2027 cade di lunedì (nessun ponte nuovo); pubblicità italiana bassa; nessun sito nostro per famiglie italiane |
| Brückentage e Schulferien per Land (DE) | "brückentage 2027" 10 Länder; "schulferien 2027" 10 | schulferien.org 200, KMK 404 sul percorso | schulferienplaner, ferienwiki, schulferien.eu, ADAC, urlaubsguru, Merian, web.de, karrierebibel, rechner-hub, alloq.digital (strumento) | 2,5 | NO: pieno di siti di calendari e giornali |
| Vacances scolaires e ponts 2027 (FR) | "vacances scolaires 2027" 10 (zone, città); "ponts 2027" 10 | `data.education.gouv.fr` 200 (studio 16) | education.gouv.fr e siti di calendari (studio 16) | 2,5 | NO (conferma, ora in francese) |
| Calendario escolar 2026-27, puentes 2027 (ES) | 10 e 10 per comunità | – | stesso muro del calendario laboral (17/10) | 2,5 | NO |
| School term dates per council (UK) | "school term dates 2027" 10 (anche AU e NZ) | centinaia di council | council e siti scolastici | 2 | NO (filtro duro: ~150 fonti) |
| Pagamenti INPS: pensioni, tredicesima, assegno unico, NASpI, assegno di inclusione | Fortissima e mensile: "pagamento pensioni" 10 (novembre 2026, poste); "assegno unico novembre 2026 data / quando pagano" 10; "naspi pagamento" 10; "cedolino pensione" 10 | `inps.it` 200 | quifinanza, investireoggi, informazionefiscale, businessonline, trend-online, diritto.it, centrofiscale: ognuno con "calendario pensioni 2026" e un articolo al mese | 3 | NO: i giornali rispondono in giornata e la data è una sola (primo giorno bancabile); tema di soldi per persone fragili (verdetto del 14/10); nessun sito nostro adatto |
| Rente-Auszahlungstermine (DE), date CAF e retraite (FR) | "rente auszahlung" 10; "date versement retraite" 10 (CARSAT, Agirc-Arrco); "date paiement caf" 10 | – | giornali | 3 | NO, stesso verdetto dell'INPS |
| SNAP, date di accredito per Stato (USA) | "snap payment schedule" 10 (pa, nyc, states); "snap deposit dates" 10 (texas, indiana) | 50 agenzie statali | **muro di siti automatici e fatti con l'IA**: feedam.org, benefitsusa.org, govtschemes.org, snapeligibilitycalculator, un sito `vercel.app`; testate ispaniche (futbolete, okdiario, cronista) con tabelle sbagliate (giorni della settimana del 2025 usati per il 2026) | 4 | NO: date che si contraddicono (il buco c'è), ma il pubblico vale poco, è un tema delicato e il campo è affollato |
| Scadenze fiscali IT (F24, 730, IMU, acconto IRPEF) | "scadenze fiscali" 10 (per mese); "scadenza f24" 10; "scadenza imu" 10; "acconto irpef" 10 | `agenziaentrate.gov.it` 200 (scadenzario ufficiale) | ente, studi, giornali fiscali | 3 | NO: l'ente risponde, c'è responsabilità fiscale |
| Saldi invernali 2027 per regione (IT) e "sales in Italy" (EN) | IT forte: "saldi invernali 2027" 10 regioni. EN debole: "italy sales dates" 1, "when are the sales in italy" 4 | Conferenza delle Regioni (`regioni.it` 200); calendario 2027 non ancora uscito (di solito a dicembre) | quifinanza, investireoggi, studenti.it, greenme, quotidiano.net, ilsussidiario: tutti "regione per regione" | 4 | NO in italiano. In inglese al massimo una pagina in Italy Strikes (1-2 ore, guadagno quasi nullo): non la propongo |
| Calendario venatorio per regione (IT) | Forte: "calendario venatorio 2026 2027" 10 regioni; "apertura caccia 2026" 10 regioni | delibere regionali in PDF (Calabria, Basilicata, Veneto, Piemonte, Abruzzo; Toscana pagina 200), tante sospensioni dei TAR | in prima pagina soprattutto i PDF ufficiali e la stampa locale | 5 | RISERVA debole: buco vero (solo PDF), ma 20 fonti PDF da rileggere a mano ogni anno, specie per specie; pubblicità limitata sul tema armi; nessun sito nostro adatto; sito nuovo sotto l'asticella |
| Maturità 2027, test di ammissione | "maturità 2027 date" 10 | MIM 200 | una data nazionale, giornali scolastici | 3 | NO |
| Fechas PAU 2027 per comunità (ES) | 10 comunità | università e comunità | università, El País, portali di studenti (non approfondito) | 4,5 | NO: pubblicità spagnola bassa, nessun sito nostro in spagnolo |
| Cambio dell'ora 2026-2027 (IT) | 10 | – | timeanddate, giornali | 2 | NO (conferma) |
| Raccolta differenziata per Comune (IT) | 10 (bergamo, aprilia, roma, alia) | migliaia di gestori e app | gestori e Comuni | 2 | NO (filtro duro) |
| Festa patronale e santo patrono per Comune (IT) | 10 (comuni pugliesi; "santo patrono milano") | nessuna fonte ufficiale unica | Wikipedia, Comuni, stampa locale | 2,5 | NO |

---

## 6. Righe proposte per `ESPLORATE.md` (non le ho scritte io: le aggiunge chi aggiorna l'elenco)

```
## Ricerca settore calendari e date ufficiali (30/10/2026)
| Nicchia | Esito | Studio |
|---|---|---|
| **Uscita dei biglietti, chiusure e giorni gratis delle grandi attrazioni, con iCal** (Cenacolo, Vaticano, Anna Frank, Pompei, Alhambra, Sagrada 200; Colosseo, MiC, Borghese, Grecia chiusi al server) | **PASSA** (voto 7,5; 300 / 1.100 / 4.000 €/anno; 16-24 ore) come sezione `/tickets/` di Before You Fly; 8 con 1.500 impressioni sulle 10 pagine pilota a 30 gg e Viator approvato | ricerca-settore-calendari-2026-10-30 |
| TOLC sede per sede con posti liberi (testcisia.it, tabella 200) | sezione piccola di EsamiDiStato (voto 6,5; 50-400 €/anno; 8-12 ore), dopo aver letto la licenza CISIA | ricerca-settore-calendari-2026-10-30 |
| Gomme invernali e catene per Paese con le date, per il noleggio | aggiunta a "Driving abroad" (voto 6; 120-1.200 €/anno; entro il 15/11 o nel 2027) | ricerca-settore-calendari-2026-10-30 |
| Giorni gratis dei musei per città | solo dentro la sezione biglietti (5 da sola) | ricerca-settore-calendari-2026-10-30 |
| Calendario scolastico e ponti (IT, DE, FR, ES, UK), pagamenti INPS, Rente, CAF, SNAP, scadenze fiscali IT, saldi, maturità, PAU, cambio dell'ora, rifiuti, patroni | NO (2-4,5) | ricerca-settore-calendari-2026-10-30 |
| Calendario venatorio per regione (IT) | RISERVA debole (5) | ricerca-settore-calendari-2026-10-30 |
```

## 7. Note per chi costruisce

- **Fonti italiane chiuse al server e a GitHub Actions.** La rete del Ministero della Cultura (`cultura.gov.it`, `beniculturali.it`, `colosseo.it`, Borghese, Accademia), `mit.gov.it` e `stradeanas.it` danno 000 (connection reset), come il registro scioperi dal 23/10. Per queste attrazioni la regola si scrive a mano con la fonte e la data del controllo; il ricontrollo si fa da un browser in Italia.
- **Fonti italiane aperte.** INPS, MIM, Agenzia Entrate, regioni, Gazzetta, Normattiva, CISIA, Poste e `regioni.it` rispondono 200.
- **Regola delle date.** Mai una data scritta a mano dentro le pagine: solo regole (giorni prima, giorno della settimana con ora e fuso, trimestre) più le eccezioni datate. Il calcolo lo fa lo script ogni giorno, così le pagine non invecchiano come quelle dei concorrenti.
- **Riquadro "Sold out?".** Solo visite con il biglietto incluso, da venditori in elenco (Viator), con `rel="sponsored noopener"` e la riga di trasparenza. Mai rivenditori di biglietti a prezzo maggiorato (vedi Which?, "£130 for a £19 ticket"): stessa logica della regola del 10/10 sui servizi visto.
