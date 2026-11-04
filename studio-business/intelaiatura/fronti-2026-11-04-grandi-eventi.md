# Fronte nuovo del 4/11/2026: grandi eventi e scadenze 2027-2028 che creano picchi di ricerca

Angolo assegnato: i grandi eventi del 2027-2028 nel mondo che portano ricerche prevedibili e pagabili con alloggi, biglietti, assicurazioni e trasporti, usando le affiliazioni che abbiamo già: Stay22 (Booking e altre agenzie, attivo dal 31/10), Viator (account creato, in analisi), DiscoverCars (attivo), SafetyWing (attivo). Per ogni evento: dati ufficiali stabili, domanda misurata, concorrenza, finestra, sito che lo ospiterebbe, numeri, voto severo.

**Letti prima:** skill `rete-siti`, `REGOLE-FISSE.md` (regole del 30/10 e del 31/10), `STRATEGIA.md`, `ESPLORATE.md` (righe su eclissi 2027, Hajj, ETIAS, K-ETA, ETA UK, tassa alberghiera USA), `wf-2026-10-31-eventi-calendari.md` (sorteggi di Ryder Cup, Rugby World Cup ed Euro 2028 già valutati come calendario di vendita dei biglietti: voto 5), `idee-2026-10-31-cambi-regole.md`.

**Già chiuse, che NON ho rifatto:** sorteggi e date di vendita dei biglietti dei grandi eventi come sito (voto 5, 31/10); eclissi 2027-2028 per Paese (NO, 17/10); Hajj (NO, 31/10); ETIAS, K-ETA, ETA UK, ESTA, "regole di viaggio 2027" (riserve e NO del 17/10, 25/10 e 31/10); tassa alberghiera USA per città (NO, 25/10). Qui l'angolo è diverso: **dove dorme, come arriva e cosa paga chi va all'evento**.

**Metodo.** Domanda: autocomplete di Google (`client=firefox`) nel Paese e nella lingua giusti, circa 110 interrogazioni; visite mensili alle voci di Wikipedia come misura di interesse (API Wikimedia: solo 5 voci lette, poi il server ha risposto 429 a ogni richiesta e non ho insistito). Concorrenza: prima pagina della ricerca web (risultati americani). Fonti: curl dal nostro server con codice HTTP e dimensione, senza cambiare l'identità del programma; dove la fonte risponde 403 o 000 lo scrivo e basta.

---

## 0. Risposta in breve

**Nessun evento passa l'asticella dei siti nuovi** (voto ≥ 7 e ≥ 5.000 €/anno nel caso centrale). Nessuna idea da 8. La migliore per potenziale è la **guida sede per sede delle Olimpiadi di Los Angeles 2028** (voto 6), ma rende tra metà 2027 e agosto 2028 e poi si spegne. Le più rapide sono due **pagine a costo zero di Tourist Tax** (Napoli con l'America's Cup di luglio 2027; Santiago de Compostela con l'Anno Santo 2027) e una **sezione "Ryder Cup 2027: dove dormire" in Before You Fly** costruita sul registro ufficiale irlandese degli alloggi (voto 6).

**La lezione dell'angolo.** La domanda c'è ed è datata: "la28 ticket drop 2", "ryder cup 2027 accommodation kerry", "ryder cup 2027 hotel shortage", "eclipse 2027 tours egypt", "america's cup napoli 2027 biglietti". Ma:
- **chi vende l'evento si tiene i soldi.** Biglietti e pacchetti passano da canali ufficiali (LA28 con Ticketmaster e On Location, Ryder Cup Travel Services, Rugby World Cup Experiences). Noi possiamo guadagnare solo su ciò che sta intorno: albergo, auto, escursioni, assicurazione;
- **la prima pagina si riempie in pochi giorni** con il sito ufficiale, i giornali e, novità vista oggi, **siti automatici fatti con l'intelligenza artificiale** (`olympics2028.vercel.app`, `olympichub.vercel.app`, `la2028metro.pages.dev` in prima pagina per "where to stay LA 2028 Olympics");
- **la pagina muore con l'evento.** Il lavoro rende una volta sola, mentre una pagina di EsameB1 o di Tourist Tax rende ogni anno.

Dove il nostro modello vince ancora è lo stesso buco di sempre: **un dato ufficiale sparso o contraddetto dai blog**, legato a un posto. Per questo le proposte migliori qui sotto sono pagine che restano utili anche dopo l'evento (la tassa di soggiorno di Napoli e di Santiago) o che usano un registro ufficiale che nessuno ha messo in tabella (gli alloggi registrati entro 30 km da Adare Manor).

| # | Evento e idea | Dove | Voto | € (prudente / centrale / ottimista) | Ore | Primi soldi |
|---|---|---|---|---|---|---|
| 1 | **Los Angeles 2028: guida sede per sede** (cosa si gioca in ogni sede e in quale giorno dal calendario ufficiale per sessione, come arrivarci con la metro, dove dormire con Stay22, regole d'ingresso per chi viene dall'estero, SafetyWing) | sezione nuova di **Before You Fly** | **6** | 300 / 2.500 / 8.000 **in tutto**, da metà 2027 ad agosto 2028 | 20-28 | 2° semestre 2027 |
| 2 | **Ryder Cup 2027 (Adare Manor, 13-19/9/2027): dove dormire per distanza** (alloggi registrati da Fáilte Ireland entro 15/30/50/80 km, paesi, aeroporto di Shannon, auto a noleggio) | sezione nuova di **Before You Fly** | **6** | 100 / 700 / 2.500 in tutto, da subito a settembre 2027 | 10-14 | dicembre 2026 - gennaio 2027 |
| 3 | **Napoli: tassa di soggiorno** (pagina che manca in Tourist Tax), con l'America's Cup del 10-18/7/2027 in evidenza | pagina di **Tourist Tax** | **6** | 100 / 450 / 1.200 **all'anno** (resta dopo l'evento) | 4-6 | primavera 2027 |
| 4 | **Santiago de Compostela: tassa turistica** (1-2,5 € a notte, esenti i pellegrini negli albergues pubblici), con l'Anno Santo 2027 in evidenza | pagina di **Tourist Tax** | **5,5** | 60 / 300 / 900 all'anno | 3-5 | gennaio-marzo 2027 |
| 5 | Euro 2028 (Regno Unito e Irlanda, giugno-luglio 2028): città, alloggi, ETA britannica per i tifosi europei | Before You Fly, ma non prima di metà 2027 | 5 (riserva) | 100 / 800 / 3.000 in tutto | 15-20 | 2028 |
| 6 | Rugby World Cup 2027 (Australia, 1/10-13/11/2027): visto per i tifosi delle 24 squadre, città sede | Before You Fly | 4,5 | 50 / 300 / 1.000 | 10-14 | estate 2027 |
| 7 | Tour de France 2027, partenza da Edimburgo il 2/7/2027 | riga nella pagina **Edinburgh** di Tourist Tax (c'è già) | 4,5 | 20 / 80 / 200 | 1 | estate 2027 |
| 8 | Eclissi totale del 2/8/2027 (Spagna, Gibilterra, Marocco, Tunisia, Egitto, Arabia Saudita): viaggi e tour | nessuno (NO del 17/10 confermato) | 4 | – | – | – |
| 9 | Coppa del Mondo femminile 2027 (Brasile): visto elettronico per USA, Canada, Australia | dentro la riserva "cambi di regole 2027" | 4,5 | – | – | – |
| 10 | Coppa d'Africa 2027 (Kenya, Uganda, Tanzania, 19/6-17/7/2027) | nessuno | 4 | – | – | – |
| 11 | Mondiali di cricket 2027 (Sudafrica, Zimbabwe, Namibia) | nessuno | 4 | – | – | – |
| 12 | Expo 2027 Belgrado (15/5-15/8/2027) e GREEN×EXPO 2027 Yokohama (19/3-26/9/2027) | nessuno | 4 / 3,5 | – | – | – |
| 13 | Giornata Mondiale della Gioventù, Seul 2027 | una riga nella pagina K-ETA già in coda | 3,5 | – | – | – |
| 14 | Kumbh Mela di Nashik 2027; Giochi Panamericani di Lima 2027 | nessuno | 3 | – | – | – |
| 15 | Capitali europee della cultura 2027 (Évora, Liepāja) e 2028 (Bourges, České Budějovice, Skopje) | nessuno | 2,5 | – | – | – |
| 16 | Giochi del Mediterraneo | fuori finestra: Taranto si è chiusa il 3/9/2026, la prossima edizione è nel 2030 | – | – | – | – |
| 17 | Regole di viaggio che cambiano nel 2027 | già studiate (31/10): nessun fatto nuovo, solo un limite in più per la n. 1 (fonti USA chiuse al server) | – | – | – | – |

**Da fare (regola "rete fitta": costo zero e guadagno atteso positivo), in ordine di guadagno per ora:**
1. **N. 3 e n. 4 (Tourist Tax, 7-11 ore in tutto)**: le due pagine restano utili ogni anno. Santiago va online **prima del 31/12/2026**, quando si apre la Porta Santa. Per Napoli prima va trovata la delibera ufficiale delle tariffe 2026 (vedi sez. 3).
2. **N. 2 (Before You Fly, 10-14 ore)**: entro gennaio 2027, perché i biglietti del sorteggio sono già assegnati e chi li ha vinti cerca casa adesso.
3. **N. 1 (Before You Fly, 20-28 ore)**: costruirla tra febbraio e aprile 2027, prima della vendita "first-come, first-served" del 2027 e della stagione delle prenotazioni alberghiere (luglio 2028 meno 12 mesi).
4. **N. 5 in riserva**: si riapre quando la UEFA pubblica le date del sorteggio dei biglietti di Euro 2028.

---

## 1. Los Angeles 2028: guida sede per sede (voto 6, sezione di Before You Fly)

### Che cosa è
Una pagina per ogni sede (circa 45) e per ogni zona (18 a Los Angeles, più le sedi fuori: Oklahoma City per softball e canoa slalom; New York, Columbus, Nashville, St. Louis, San José e San Diego per il calcio). In alto la risposta: "Rose Bowl Aquatics Center: swimming finals 15-23 July 2028, sessions at 09:30 and 18:00 PT" (esempio di forma, da riempire con i dati del PDF). Sotto: come si arriva (linea della metro, perché i Giochi sono pensati senza auto), mappa degli alloggi Stay22 con le date della sede già inserite, regole d'ingresso per chi arriva da fuori (ESTA o visto), assicurazione sanitaria (SafetyWing: per gli Stati Uniti conta davvero), escursioni Viator nei giorni liberi. Più una pagina per giorno ("what's on at LA28 on 21 July") e il file `.ics` per sede.

### Dati ufficiali (curl, 4/11)
| Fonte | Indirizzo | Esito | Cosa dice |
|---|---|---|---|
| LA28, home | `la28.org/en.html` | **200**, 168 kB | "Olympic Games Dates: July 14–30, 2028. Paralympic Games Dates: August 15–27, 2028"; "Drop 2 was the last general public ticket drop of 2026… The next opportunity… will be in 2027" (letto) |
| LA28, comunicato del 21/8/2026 | `la28.org/en/newsroom/record-demand-sets-the-stage-for-first-come-first-served-la28-olympic-ticket-sales-to-open-in-2027.html` | **200**, 80 kB | "total Olympic ticket sales have surpassed 6 million"; vendita 2027 "on a first-come, first-served basis" (letto). La data del 2027 non è ancora scritta |
| Calendario per sessione, versione 4.1 | `la28.org/content/dam/latwentyeight/competition-schedule-imagery/uploaded-oct-25-oly-4-1/LA28OlympicGamesCompetitionScheduleBySessionV4.1.pdf` | **200**, 217 kB, PDF | "As of October 26, 2026": sede × sport × giorno × orario di ogni sessione (ora del Pacifico); `pdftotext -layout` lo legge (433 righe); orari del calcio "announced at a later date". Esistono anche le versioni per giorno e per gara |
| Sedi e zone | `la28.org/en/games-plan/venues.html` | **200**, 153 kB | 18 zone a Los Angeles più OKC, New York, Columbus, Nashville, St. Louis, San José, San Diego (letto) |
| Viaggio | `la28.org/en/ticketing/traveling-to-la28.html` | **200**, 88 kB | consigli generali per chi viaggia |
| Biglietteria | `tickets.la28.org` | 000 | non serve: si linka la pagina ufficiale |
| Regole d'ingresso USA | `travel.state.gov` (tempi di attesa dei visti) | **403** | chiuso al server: non si aggira. Per le regole si usano le schede FCDO (`gov.uk/api/content/foreign-travel-advice/usa`, il formato JSON risponde 200 per gli altri Paesi) e travel.gc.ca |

Aggiornamento: il calendario cambia poche volte (versione 4.1 del 26/10/2026): controllo settimanale dell'impronta del PDF, come per i biglietti di Before You Fly.

### Domanda (autocomplete, 4/11)
- USA: "la 2028 olympics" **10** (tickets, dates, schedule, venues, schedule of events); "la28 tickets" 10 ("drop 2", "draw", "time slot", "resale"); "la28 ticket drop" 10 ("drop 3", "schedule", "dates"); "la28 venues" **10** ("map", "by sport", "list", "outside of la", "and events"); "la 2028 olympics schedule" 10 (swimming, cricket, soccer); "la olympics hotels" **10** ("reddit", "packages", "prices", "accommodation"); "2028 olympics soccer venues" 10; "oklahoma city olympics 2028" 10 (tickets, events, schedule); "la olympics visa" 10 (ma è la prevendita per chi ha la carta Visa, non il visto).
- Regno Unito: "la 2028 olympics" 10. Messico: "juegos olimpicos 2028" 10 (boletos, fechas). Brasile: "olimpiadas 2028" 10 (ingressos).
- Vuote: "la 2028 olympics events by venue", "visa olimpiadas los angeles", "visto americano olimpiadas": chi viene dall'estero non cerca il visto legato all'evento.

### Chi c'è su Google
"where to stay LA 2028 Olympics hotels near venues": `losangeles.com` (guide di quartieri, alberghi e sedi), agenzie (roadtrips.com, tours4fun, ocean-florida), alberghi singoli e **tre siti automatici nuovi** su `vercel.app` e `pages.dev`, uno con la scritta "Data from LA28 Games Plan and official schedule as of April 21, 2026" (cioè fermo alla versione vecchia). Per "Long Beach venues schedule hotels" ci sono solo le notizie NBC e CBS del 2025, senza date per sede e senza alberghi: il buco c'è, ma è sottile e altri lo stanno già riempiendo con lo stesso metodo.

### Chi paga
- **Stay22** (attivo): 30 % della commissione dell'agenzia (scheda del 17/10). Un soggiorno di 4-5 notti a Los Angeles durante i Giochi vale 1.500-2.500 $; con una commissione d'agenzia del 4-6 % ne restano a noi circa 20-40 $ a prenotazione (stima, da verificare con le prime prenotazioni vere).
- AdSense su pubblico USA.
- SafetyWing (attivo) per chi arriva da fuori; Viator per le escursioni; DiscoverCars solo per OKC e le sedi del calcio.

### Stima (in tutto, da metà 2027 ad agosto 2028)
- **Centrale 2.500 €**: 45.000 visite in tutto (da 1.000 al mese a metà 2027 a 8.000 al mese a maggio-luglio 2028); 4 % di clic su Stay22 (1.800) × 4 % di prenotazioni = 72 × 25 € = 1.800 €; AdSense 45.000 × 1,3 pagine × 10 € ogni 1.000 = 585 €; SafetyWing e Viator 100-150 €.
- **Prudente 300 €**: 8.000 visite in tutto (Before You Fly oggi ha posizione media 42: è il rischio vero), quasi solo AdSense.
- **Ottimista 8.000 €**: 120.000 visite, se le pagine per sede vanno in prima pagina per "[sede] olympics 2028".
- Dopo agosto 2028: zero. In media sui 14 mesi utili il caso centrale vale circa 2.100 €/anno: sotto l'asticella dei siti nuovi.

### Ore: 20-28
Lettura del PDF e tabella sede × giorno × sessione (6-8), coordinate e linee della metro (3-4), pagine e `.ics` con il motore di Before You Fly (6-8), regole d'ingresso dalle schede FCDO e canadesi (2-3), revisione indipendente (3-4).

### Rischi
Siti automatici concorrenti già online; posizione bassa di Before You Fly; tabelle del PDF da rileggere a ogni versione; nessuna fonte USA leggibile per i visti; marchi LA28 e cinque cerchi da non usare (solo testo descrittivo).

### Voto: 6
Domanda grande e misurata, dato ufficiale leggibile, prenotazioni care. Non sale perché la pagina vive 14 mesi, la prima pagina è già contesa e il guadagno dipende da prenotazioni di albergo di cui non abbiamo ancora nessun numero vero.

---

## 2. Ryder Cup 2027: dove dormire per distanza da Adare Manor (voto 6, sezione di Before You Fly)

### Che cosa è
Una pagina principale e 12-15 pagine di paese (Limerick, Castletroy, Shannon, Ennis, Adare, Bunratty, Newmarket-on-Fergus, Killaloe, Charleville, Mallow, Listowel, Tralee, Killarney, Nenagh, Tipperary). Per ognuno: distanza da Adare Manor, quante strutture e quante camere registrate, come si arriva (strada, treno per Limerick), mappa Stay22 con le date 13-19/9/2027 già inserite. Più: aeroporto di Shannon (con il controllo di frontiera americano già fatto in partenza per il ritorno negli USA), auto a noleggio (DiscoverCars: in Irlanda l'auto serve), escursioni Viator nei giorni liberi (Cliffs of Moher, Ring of Kerry).

### Dati ufficiali (curl, 4/11)
| Fonte | Indirizzo | Esito | Cosa dice |
|---|---|---|---|
| Ryder Cup, sito ufficiale | `rydercup.com/` | **200**, 258 kB | "September 13-19, 2027, Adare Manor, Limerick, Ireland" (letto) |
| Ryder Cup, biglietti | `rydercup.com/attend/ticket-information` | **200**, 143 kB | "The 2027 Ryder Cup Ballot has now closed… Tickets are still available through Ryder Cup Travel Services Ticket Inclusive Hotel Packages" (letto) |
| Ryder Cup, alloggi | `rydercup.com/attend/accommodation` | **200**, 154 kB | "Official Ryder Cup Campsite" e pacchetti autorizzati (letto) |
| **Registro Fáilte Ireland degli alloggi** (data.gov.ie, licenza CC BY 4.0) | `failteireland.azure-api.net/opendata-api/v2/accommodation/csv` | **200**, 416 kB, CSV | **2.305 strutture**, con settore, paese, contea, codice postale, numero di unità, coordinate per 1.749. Contati oggi: **entro 15 km da Adare Manor 15 strutture e 823 unità; entro 30 km 51 e 2.341; entro 50 km 108 e 3.231; entro 80 km 397 e 12.374**. Paesi entro 50 km con più unità: Limerick 768, Castletroy 443, Shannon 301, Ennis 227, Adare 221, Bunratty 206. Contea di Limerick: 28 alberghi, 2.339 camere |

Il registro non comprende gli affitti brevi non registrati e gli alloggi senza coordinate (17 a Limerick, 37 in Clare, 45 in Kerry): lo si scrive nella pagina.

### Domanda (autocomplete, 4/11)
- Irlanda: "ryder cup 2027" 10 ("accommodation", "accommodation prices", "tickets price"); "ryder cup 2027 accommodation" **10** ("prices", "tipperary", "kerry", "galway", "omagh", "to rent", "official", "adare manor"); "adare manor ryder cup" 10 ("house rental", "accommodation").
- USA: "ryder cup 2027" 10 ("packages", "packages for sale"); "ryder cup 2027 hotels" **10** ("**hotel shortage**", "hotel packages", "accommodation prices").
- Wikipedia "2027 Ryder Cup": 70.932 visite in 12 mesi, 7.112 al mese negli ultimi 3 (picco 14.812).

### Chi c'è su Google
Notizie (golf.com sulla "strange solution to hotel shortage", Irish Examiner "one in 10 hotel rooms in Ireland already booked", Limerick Leader, NBC Sports, BroBible sulle navi da crociera a Foynes), tripprof.com con una guida di viaggio, pacchetti ufficiali. **Nessuno dà il numero di camere registrate per distanza**: è il dato che risponde a "dove trovo ancora posto".

### Chi paga
Stay22 (soggiorni di 3-5 notti a prezzi da evento: 1.000-2.000 € → 12-25 € a prenotazione, stima); DiscoverCars (circa 20 $ a noleggio, attivo); Viator (8 %); AdSense su pubblico USA e irlandese.

### Stima (in tutto, fino a settembre 2027)
- **Centrale 700 €**: 8.000 visite; Stay22 4 % × 5 % = 16 prenotazioni × 18 € = 290 €; DiscoverCars 1,5 % × 6 % = 7 × 18 € = 130 €; AdSense 8.000 × 1,3 × 9 € ogni 1.000 = 95 €; Viator e SafetyWing 50-150 €; il resto dalle pagine che restano utili per il golf in Irlanda dopo l'evento (poco).
- **Prudente 100 €**: 1.500 visite. **Ottimista 2.500 €**: 25.000 visite se la pagina "Ryder Cup 2027 accommodation" entra tra i primi 5 risultati in Irlanda e negli USA.

### Ore: 10-14
Calcolo delle distanze dal CSV (2), pagine con il motore di Before You Fly (5-7), treno e aeroporto (1-2), revisione (2-3).

### Voto: 6
Dato ufficiale, aperto e mai messo in tabella; domanda precisa con le contee; pubblico americano che spende. Non sale perché la finestra è di 10 mesi e il traffico di Before You Fly oggi è basso.

---

## 3. Napoli: tassa di soggiorno, con l'America's Cup 2027 in evidenza (voto 6, pagina di Tourist Tax)

### Che cosa è
La pagina Napoli che manca in Tourist Tax (oggi ci sono Roma, Firenze, Milano), con il calcolatore: categoria della struttura, notti (massimo 14 consecutive secondo il regolamento citato dalla stampa), esenzioni. In evidenza: "38th America's Cup: Naples, 10-18 July 2027 (preliminary regattas before)" con la mappa Stay22 sulle date. Utile anche dopo l'evento: Napoli è una delle città italiane più visitate. Più, se le fonti si leggono, Ischia, Sorrento e la Costiera.

### Fonti
- **Comune di Napoli**: `comune.napoli.it` risponde 200, ma le pagine sull'imposta che ho provato rispondono 404 e la pagina "tributi" non ha link all'imposta. **La delibera di Giunta con le tariffe 2026 va trovata prima di costruire.** Senza la fonte ufficiale la pagina non si fa.
- I siti di terzi **non sono d'accordo**: Holidu (febbraio 2026) scrive 6 € per i 5 stelle, 5,50 € per i 4 stelle, 4,50 € per i 3 stelle; Chekin scrive 5 € per i 5 stelle con un tetto di 5 €; Fanpage scrive di un aumento di 1 € a notte nel 2026 senza la tabella. È esattamente il caso in cui una pagina con la fonte ufficiale vince.
- Ischia: tabella 2026 in PDF su `static.paytourist.com` (indicata dalla ricerca, da verificare con curl prima della costruzione).
- America's Cup: le date del Match (10-18/7/2027) vengono dalla stampa di settore (Sailing Scuttlebutt, Sail-World, The Star): **da confermare sul sito ufficiale** (`americascup.com` risponde 200 ma con 16 kB senza testo leggibile).

### Domanda (autocomplete, 4/11)
- USA: "naples tourist tax" **10** ("2026", "airbnb", "per night", "children", "calculator", "naples city tax 2026", "naples hotel tax"); "naples italy tourist tax" 7.
- Italia: "tassa di soggiorno napoli" 10 (2026, b&b, affitti brevi, bambini); "america's cup napoli 2027" **10** ("biglietti", "date", "programma", "calendario", "quanto dura").
- USA, Nuova Zelanda, Regno Unito: "america's cup naples" 10 ("2027 dates", "tickets", "schedule").

### Chi paga
Stay22 (alberghi a Napoli e in Costiera), Viator (barche per vedere le regate, Pompei, Capri), AdSense. Italy Strikes ha già le pagine di Napoli per gli scioperi dei trasporti: link interni nei due sensi.

### Stima (all'anno, a regime)
- **Centrale 450 €**: 2.500 visite al mese nella stagione (aprile-ottobre) e 800 negli altri mesi ≈ 21.000 l'anno; AdSense 21.000 × 1,3 × 8 € ogni 1.000 = 220 €; Stay22 1,5 % di clic × 5 % = 16 prenotazioni × 12 € = 190 €; Viator 40 €.
- **Prudente 100 €**: come le altre città di Tourist Tax oggi (posizione media 32). **Ottimista 1.200 €**: con Ischia e la Costiera e un luglio 2027 forte.

### Ore: 4-6 (Napoli), più 2-3 per ogni Comune vicino con fonte leggibile.

### Voto: 6
Domanda americana forte, fonti di terzi in contrasto, pagina che vale ogni anno; l'evento è solo una spinta in più. Non sale perché la fonte ufficiale non è ancora stata trovata.

---

## 4. Santiago de Compostela: tassa turistica, con l'Anno Santo 2027 (voto 5,5, pagina di Tourist Tax)

### Che cosa è
Pagina con calcolatore per Santiago de Compostela (tassa in vigore dal 1/10/2025 secondo la stampa): importo per categoria, massimo di notti, **esenzione per i pellegrini negli albergues pubblici della Xunta**, più l'Anno Santo (dal 31/12/2026, apertura della Porta Santa, a tutto il 2027). Se le fonti si leggono, anche A Coruña.

### Fonti (curl, 4/11)
- **Domande e risposte ufficiali** del Turismo di Santiago: `santiagoturismo.com/files/2025/09/20250915114905_Preguntaserespostas.pdf` **200**, 522 kB, PDF, letto: alberghi 5 stelle e 4 stelle superiore **2,5 €**, 4 e 3 stelle **2 €**, 2 stelle superiore 2 €, 2 e 1 stella **1,5 €**, pensioni 1,5 €, **albergues 1 €**, campeggi, turismo rurale e appartamenti turistici 1 €.
- Concello (`santiagodecompostela.gal`): 000 dal server. Xunta (`abertos.xunta.gal`, `xacobeo.gal`): 000.
- Statistiche dei pellegrini (Oficina del Peregrino): `oficinadelperegrino.com/estadisticas-nueva/` 200, ma i numeri sono in un riquadro Power BI incorporato: non si leggono in modo semplice e non lo forzo.

### Domanda (autocomplete, 4/11)
- USA: "santiago de compostela tourist tax" 8 ("city tax"); "camino de santiago 2027" **10** ("holy year", "dates", "tours 2027", "may 2027"); "camino de santiago accommodation" 10; "camino statistics" 10 ("2026", "2025", "2024").
- Spagna: "camino de santiago 2027" 10; "año santo 2027" 7. Germania: "jakobsweg 2027" 4. Italia: "cammino di santiago 2027" 3.

### Chi c'è su Google
Per la tassa: Chekin, guide di agenzie del Cammino (viajecaminodesantiago.com), forum di gronze.com. Per il Cammino in generale: un muro (gronze, Wise Pilgrim, Follow the Camino, CaminoWays, il forum caminodesantiago.me): **un sito sul Cammino è NO (voto 4)**.

### Chi paga
Stay22 (alberghi a Santiago alla fine del Cammino), SafetyWing (chi cammina 30 giorni), Viator (Finisterre), AdSense.

### Stima (all'anno): prudente 60 €, centrale 300 € (10.000 visite l'anno nel 2027 con l'Anno Santo, metà dopo), ottimista 900 €. Ore 3-5. Voto 5,5: fonte ufficiale leggibile e domanda vera ma piccola; si costruisce per la regola della rete fitta.

---

## 5. Gli altri eventi, in breve

**Euro 2028 (Regno Unito e Irlanda, giugno-luglio 2028) — voto 5, RISERVA.** Domanda forte e in più lingue: "euro 2028 tickets" 10 (gb: "ballot", "ballot timetable", "release date"); "em 2028 tickets" 10 (de: "ab wann", "preise"); "eta england" 10 (de, "kosten", "offizielle seite"), "eta royaume uni" 10, "eta regno unito" 10, "eta engeland" 10: i tifosi europei avranno bisogno dell'ETA britannica. Ma ETA UK è un muro (NO del 17/10) e le date del sorteggio dei biglietti non sono ancora uscite. Si riapre quando la UEFA le pubblica, con pagine per città sede e mappa Stay22. 100 / 800 / 3.000 € in tutto.

**Rugby World Cup 2027 (Australia, 1/10-13/11/2027, 52 partite, 8 stadi in 7 città) — voto 4,5.** Fonti: `rugbyworldcup.com/2027` 200, `world.rugby` (comunicato del calendario) 200, `immi.homeaffairs.gov.au` (visa finder) 200, schede FCDO 200. Domanda: "rugby world cup 2027" 10 in gb, za, nz, ie, fr (fixtures, tickets, draw); "rugby world cup 2027 accommodation" solo 5 (gb); "australia eta for uk" 10 (molti britannici credono di dover fare l'ETA, ma per loro c'è l'eVisitor). "australia visa for rugby world cup" 0: il visto si cerca per nazionalità, non per evento, e lì domina il governo australiano con VisaHQ e simili. Wikipedia "2027 Rugby World Cup": 89.588 visite in 12 mesi, 27.701 al mese negli ultimi 3. Pagine possibili: "Rugby World Cup 2027: which visa for fans of each team" (24 nazionalità: eVisitor per l'Europa, ETA per USA, Canada, Giappone, Hong Kong, visto 600 per Fiji, Samoa, Tonga, Sudafrica, Zimbabwe, Sud America da verificare). 50 / 300 / 1.000 €.

**Tour de France 2027 (partenza da Edimburgo il 2/7/2027, tappa Edimburgo-Carlisle; la Femmes parte da Leeds il 30/7) — voto 4,5.** "tour de france 2027" 10 (gb: "route map", "uk route", "grand départ"); "tour de france edinburgh" 10. Tourist Tax ha già la pagina di Edimburgo con il Visitor Levy (`edinburgh.gov.uk/visitorlevy` 200): basta un riquadro con la data e la mappa Stay22 (1 ora). Sito per tappe: NO, cyclingstage.com e letour.fr.

**Eclissi totale del 2/8/2027 — voto 4, il NO del 17/10 resta.** Fatti nuovi: Wikipedia "Solar eclipse of August 2, 2027" **657.360 visite in 12 mesi** (picco 378.040 in un mese, quasi certamente quello dell'eclissi del 12/8/2026); domanda di viaggio vera ("eclipse 2027 tours" 10: Morocco, Egypt, Spain, Tunisia; "eclipse 2027 holidays" 10 in gb: Egypt, Gibraltar, Luxor; "sonnenfinsternis 2027 reise" 8, anche con AIDA); in Spagna si cerca la mappa e l'ora, non l'albergo ("eclipse 2027 hoteles" 1). Chi vende sono gli operatori specializzati e le crociere: per Viator e Stay22 resta poco, e i concorrenti del 17/10 coprono la parte "dove e quando". Fonte NASA `eclipse.gsfc.nasa.gov/SEgoogle/SEgoogle2001/SE2027Aug02Tgoogle.html` 200 (pubblico dominio), se un giorno servisse.

**Coppa del Mondo femminile 2027 (Brasile, 24/6-25/7/2027) — voto 4,5.** "women's world cup 2027" 10 (us); "brazil visa for us citizens" 10 ("official site", "cost", "processing time"); "copa do mundo feminina 2027 ingressos" 10 (br). Wikipedia: 1.337.701 visite in 12 mesi (numero alto, da ricontrollare). Il visto elettronico brasiliano per USA, Canada e Australia è già nella riserva "cambi di regole" del 25/10 e del 31/10: si aggiunge lì una riga con le città sede, niente di più.

**Coppa d'Africa 2027 (Kenya, Uganda, Tanzania, 19/6-17/7/2027 secondo la CAF) — voto 4.** `cafonline.com` 200; `etakenya.go.ke` 200; stadi non ancora tutti confermati e voci di rinvio smentite dal presidente della CAF. Pubblico africano: pubblicità che vale poco, prenotazioni economiche. NO.

**Mondiali di cricket 2027 (Sudafrica, Zimbabwe, Namibia, ottobre-novembre 2027) — voto 4.** Domanda indiana forte ("cricket world cup 2027 tickets" 10 in, "south africa visa for indians" 10) ma pubblicità indiana bassa e `dha.gov.za` risponde 000. NO.

**Expo 2027 Belgrado (15/5-15/8/2027) — voto 4.** "expo 2027 belgrade" 10 (us: tickets, dates, location map); Wikipedia "Expo 2027" 100.171 visite in 12 mesi ma solo 6.297 al mese negli ultimi 3. Pubblico soprattutto regionale. **GREEN×EXPO 2027 Yokohama (19/3-26/9/2027) — voto 3,5**: domanda quasi solo giapponese ("横浜 花博 チケット" 10). NO.

**Giornata Mondiale della Gioventù, Seul 2027 — voto 3,5.** "world youth day 2027" 10 (us), "gmg 2027 seoul" 10 (it, con le diocesi di Milano, Padova, Verona): viaggi di gruppo organizzati dalle diocesi, nessuna prenotazione da intercettare. Una riga nella pagina K-ETA di Before You Fly già in coda (fine dell'esenzione il 31/12/2026).

**Kumbh Mela di Nashik 2027 — voto 3** (domanda indiana interna, "nashik kumbh 2027 hotel" 0). **Giochi Panamericani di Lima 2027 — voto 3** (domanda peruviana: volontariato, biglietti).

**Capitali europee della cultura — voto 2,5.** 2027: Évora e Liepāja; 2028: Bourges, České Budějovice e Skopje (Budva era solo finalista). "european capital of culture 2027" 5 (gb), "budějovice 2028" 2 (cz), "bourges 2028" 10 ma per programma, lavoro e bandi. NO.

**Giochi del Mediterraneo — fuori finestra.** Taranto 2026 si è svolta dal 21/8 al 3/9/2026; la prossima edizione è nel 2030.

**Regole di viaggio 2027 — nessun fatto nuovo** rispetto a `idee-2026-10-31-cambi-regole.md` (ETIAS in riserva con innesco, pagina K-ETA in coda). Unico fatto utile qui: per Los Angeles 2028 le fonti USA (travel.state.gov, cbp.gov) rispondono 403 al server, quindi la parte "ingresso negli USA" della n. 1 si scrive dalle schede FCDO e canadesi.

---

## 6. Cosa cambierebbe i voti
- **Le prime prenotazioni vere su Stay22** (attivo dal 31/10 su 6 pagine dei biglietti): se un soggiorno rende più di 30 € a noi, le n. 1 e 2 salgono di mezzo punto.
- **Before You Fly sopra la posizione media 20**: tutte le stime "centrali" di Before You Fly raddoppiano.
- **Un modo di riusare le pagine dopo l'evento**: le pagine di sede di Los Angeles possono restare come "LA stadium guides" (SoFi, Rose Bowl, Crypto.com Arena, Dodger Stadium ospitano concerti e partite tutto l'anno). Se reggono, la n. 1 smette di morire ad agosto 2028.
- Idea di fondo utile per la rete, a costo quasi zero: **un riquadro "grandi eventi in arrivo" nelle pagine città di Tourist Tax** (Napoli, Edimburgo, Santiago, Barcellona…), con il link Stay22 già impostato sulle date dell'evento. Rende poco finché Tourist Tax ha poche visite, ma si fa in 2-3 ore con i dati delle schede qui sopra.

## 7. Fonti consultate (oltre ai curl elencati)
Ricerca web del 4/11: losangeles.com/olympics-2028; olympics2028.vercel.app; world.rugby (calendario RWC 2027); citizen.digital e supersport.com (date della Coppa d'Africa 2027); golf.com, irishexaminer.com, limerickleader.ie (alloggi per la Ryder Cup); sailingscuttlebutt.com e sail-world.com (date dell'America's Cup); edinburgh.gov.uk/tourdefrance e cyclingnews.com (Tour de France 2027); sportface.it (Taranto 2026); culture.gouv.fr ed euronews.com (capitali della cultura 2028); fanpage.it, holidu.it, chekin.com (tassa di Napoli); publico.es, santiagoturismo.com (tassa di Santiago).
