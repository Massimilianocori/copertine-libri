# Ricerca del 31/10/2026: calendari ufficiali da mettere in agenda (fronte nuovo)

Angolo assegnato: date ufficiali che la gente vuole nel calendario del telefono (file `.ics`), sul modello di Italy Strikes e della sezione "Ticket release dates" di Before You Fly. Cioè: quando escono i biglietti di eventi e treni, sorteggi (ballot), festività e ponti, scioperi in altri Paesi, cambi dell'ora, scadenze di iscrizione (scuole, università, concorsi).

**Letti prima di cominciare:** `.claude/skills/rete-siti/SKILL.md`, `REGOLE-FISSE.md` (con le regole del 31/10: fronti nuovi, conta il fatturato, niente ore di Massimiliano), `ESPLORATE.md` per intero e il rapporto `ricerca-settore-calendari-2026-10-30.md`.

**Già chiuse, che NON ho rifatto** (nessun fatto nuovo trovato):
- festività, ponti, ora legale, calendari scolastici (NO negli studi 14, 17, 18, nella caccia del 25/10 e nella ricerca calendari del 30/10);
- scioperi in Francia, Spagna, Belgio, Paesi Bassi, Germania, Grecia (NO negli studi 10, 11, 14 e il 30/10); scioperi in Portogallo e Spagna con i servizi minimi: già in coda come sezione;
- quando escono i biglietti dei treni britannici (sezione in coda bassa, 30/10); grandi attrazioni europee (sezione già costruita in Before You Fly: Cenacolo, Vaticano, Anna Frank, Pompei, Alhambra, Sagrada Família);
- prenotazioni nei parchi nazionali USA (NO il 29/10), JLPT (in lista), eclissi 2027-2028 (NO il 17/10), lotteria DV (riserva debole), quote del Working Holiday australiano (31/10).

**Metodo.** Domanda: autocomplete di Google nel Paese e nella lingua giusti (`client=firefox`, circa 90 interrogazioni). Concorrenza: prima pagina della ricerca web (risultati americani). Fonti: curl dal nostro server con il codice HTTP e la dimensione, senza cambiare l'identità del programma (nessun aggiramento dei blocchi: dove la fonte risponde 403 lo scrivo e basta). Soldi: pagina del programma o, se manca, le cifre trovate con la fonte, e il calcolo scritto.

---

## 0. Risposta in breve

**Nessuna idea passa l'asticella dei siti nuovi** (voto ≥ 7 e ≥ 5.000 €/anno nel caso centrale). La migliore è una **sezione a costo zero**: l'allargamento della sezione "Ticket release dates" di Before You Fly al Giappone e agli Stati Uniti (voto 6,5).

**La lezione dell'angolo.** La domanda è enorme e precisa ("wimbledon ballot 2027 dates", "when does easyjet release flights for july 2027", "rba meeting dates 2027", "when do ghibli museum tickets go on sale"): è proprio la forma di EsameB1, una data ufficiale cercata con il mese e il luogo. Ma ogni volta c'è già qualcuno con lo stesso modello:
- un **sito dedicato e automatico** (marathonballot.com per i sorteggi delle maratone, rbaratewatch.com per le riunioni della banca centrale australiana, tubenotifications.co.uk per gli scioperi della metro di Londra);
- oppure **i giornali**, che per gli eventi grandi (Wimbledon, Glastonbury, Euro 2028) scrivono un articolo il giorno stesso dell'annuncio;
- oppure **l'ente stesso** ha la pagina con la data e un'iscrizione per gli avvisi (easyJet, Wimbledon, Fed).

In più, **chi paga paga poco**: i biglietti di eventi rendono tra l'1 % (Ticketmaster UK, cookie di 1 giorno) e il 4 % (StubHub su Partnerize). Un file `.ics` porta una persona a tornare, ma il calendario del telefono non mostra pubblicità: il guadagno arriva solo quando l'evento nel calendario riporta la persona sulla pagina (link nella descrizione dell'evento).

Dove il nostro modello vince ancora è lo stesso buco trovato il 30/10: **date legate a un posto da prenotare, con fonti sparse e blog con date vecchie o in contrasto tra loro**. Per questo la n. 1 qui sotto è un allargamento di una sezione che c'è già.

| # | Idea | Dove | Voto | € a 18 mesi (prudente / centrale / ottimista) | Ore |
|---|---|---|---|---|---|
| 1 | **Biglietti che escono a data fissa in Giappone e negli USA** (Museo Ghibli il 10 del mese alle 10 JST, Ghibli Park, Nintendo Museum, sumo per torneo, Shibuya Sky, teamLab, Palazzo Imperiale, sentieri del Fuji; Washington Monument, corona della Statua della Libertà, Alcatraz) con file `.ics` mensili | allargamento della sezione **Ticket release dates di Before You Fly** | **6,5** | 150 / 600 / 2.000 | 12-18 |
| 2 | Calendario delle decisioni sui tassi di ~40 banche centrali, con `.ics` e ultimo tasso (dati BIS) | sito nuovo | 5,5 | 300 / 1.800 / 7.000 | 25-35 |
| 3 | Sorteggi e aperture delle vendite dei grandi eventi (Wimbledon, The Open, Euro 2028, Ryder Cup 2027, Rugby World Cup 2027, Glastonbury, Gran Premi F1, Eurovision 2027) | sito nuovo | 5 | 200 / 1.200 / 5.000 | 40-60 |
| 4 | Quando le compagnie aeree aprono le vendite (easyJet, Ryanair, Jet2, TUI, BA, Eurostar, crociere) | sezione di Before You Fly | 5 | 100 / 500 / 1.500 | 8-12 |
| 5 | Finestre di ammissione delle università italiane per studenti stranieri, ateneo per ateneo, con `.ics` | sezione "Study in Italy" di Visa Income Checker | 5 | 100 / 400 / 1.200 | 14-20 |
| 6 | Lotterie delle case a prezzo calmierato di New York (Housing Connect) con le scadenze | sito nuovo | 4,5 | NO | – |
| 7 | Scioperi della metropolitana e dei treni a Londra e nel Regno Unito | sezione o sito | 4 | NO | – |
| 8 | Date di uscita dei risultati degli esami professionali (bar exam per Stato, CPA, CFA, ACCA) | sito nuovo | 4 | NO | – |
| 9 | Sorteggi delle maratone (Londra, Berlino, New York, Chicago, Tokyo, Sydney) | sito o sezione | 3,5 | NO | – |
| 10 | Ultime date di spedizione per Natale, Paese per Paese (Royal Mail, USPS, Canada Post, Australia Post, An Post) | pagina stagionale | 3,5 | NO | – |
| 11 | Concorsi pubblici in scadenza (Italia, InPA) | sito nuovo | 3 | NO | – |

**Da fare (regola "rete fitta": costo zero e guadagno atteso positivo):**
- **La n. 1, presto.** Il prossimo torneo di sumo (gennaio 2027) apre le vendite il 5/12/2026 secondo le guide (data da confermare sul sito ufficiale), e il Museo Ghibli apre dicembre il 10/11 e gennaio il 10/12: un `.ics` ricorrente "il 10 di ogni mese alle 10:00 JST" è il caso perfetto.
- **La n. 4 e la n. 5 in coda bassa**, solo con le fonti che si leggono (vedi sotto).
- **La n. 2 e la n. 3 non si costruiscono come siti**: sono sotto l'asticella. Vanno in ESPLORATE con le prove.

---

## 1. Biglietti che escono a data fissa in Giappone e negli USA (voto 6,5, sezione)

### Che cosa è
Una pagina per attrazione dentro la sezione `beforeyoufly/sito/ticket-release-dates/` che c'è già (oggi 6 attrazioni europee, generate da `beforeyoufly/raccolta/biglietti.py` e `dati/biglietti.json`). In alto la risposta con la prossima data, calcolata ogni giorno dalla regola ufficiale; sotto il fuso orario convertito (New York, Londra, Sydney), il file `.ics`, cosa fare se è esaurito (visite con il biglietto incluso).

Esempi di risposta in alto:
- "Ghibli Museum: tickets for December go on sale Tuesday 10 November 2026, 10:00 JST (8:00 pm Monday in New York)";
- "Grand Sumo, January 2027 (Tokyo): advance sale from 5 December 2026" (dopo la conferma sulla fonte ufficiale);
- "Washington Monument: tickets are released 30 days ahead at 10:00 ET, plus a second batch the day before".

### Domanda (autocomplete USA, inglese, 31/10)
- "when do ghibli museum tickets": **10** varianti ("go on sale", "release", "what time do ghibli museum tickets go on sale", "do ghibli museum tickets sell out fast");
- "ghibli museum tickets": 10 ("when to buy", "for foreigners", "lawson", "klook");
- "ghibli park tickets": 10 ("for foreigners", "when to buy");
- "nintendo museum tickets": 10 ("lottery", "resale", "last minute");
- "sumo tickets": 10, **con il mese e l'anno** ("sumo tickets november 2026", "sumo tickets fukuoka 2026", "sumo tickets tokyo september 2026");
- "pokemon cafe reservation": 10 ("time", "tips", "bot");
- "teamlab planets tickets" e "shibuya sky tickets": 10 ciascuna ("how far in advance", "when to buy");
- "imperial palace tour": 10 ("reservation", "schedule", "booking");
- "mt fuji climbing reservation": 6;
- USA: "washington monument tickets": 10 (**"not released"**, "day of", "recreation.gov"); "statue of liberty crown tickets": 10 ("sold out", "official site"); "when do alcatraz tickets": 6 ("go on sale", "are released"); "louvre tickets release": 9 ("when does louvre release tickets").

### Fonti (curl dal server, 31/10)

| Attrazione | Indirizzo | Esito | Cosa dice |
|---|---|---|---|
| Museo Ghibli | `ghibli-museum.jp/en/tickets/` | **200**, 44 kB | "Tickets become available for purchase 10 a.m. (JST) on the 10th of each month for the subsequent month" (letto) |
| Ghibli Park | `ghibli-park.jp/en/ticket/` | **200**, 37 kB | pagina biglietti in HTML |
| Nintendo Museum | `museum.nintendo.com/en/` | **200**, 48 kB | lotteria e vendite |
| Sumo (Nihon Sumo Kyokai) | `sumo.or.jp/En/` | **200**, 105 kB | "November Grand Tournament: Tickets are sold out all dates" (letto); `sumo.or.jp/EnTicket/` rimanda a una pagina vuota (111 byte): la data di vendita va presa dalla pagina "How to Buy" o dal venditore ufficiale |
| teamLab Planets | `teamlab.art/e/planets/` | **200**, 665 kB | |
| Shibuya Sky | `shibuya-scramble-square.com/sky/ticket/` | **200**, 671 kB | |
| Fuji (prenotazione sentiero Yoshida) | `fujisan-climb.jp/en/` | **200**, 56 kB | |
| Palazzo Imperiale (Agenzia della Casa Imperiale) | `sankan.kunaicho.go.jp/english/guide/koukyo.html` | **200**, 60 kB | |
| Pokémon Café | `pokemoncenter-online.com/cafe/` | 404 | indirizzo da trovare; altrimenti esclusa |
| Tokyo Disney | `tokyodisneyresort.jp/en/tdr/ticket/` | 000 | esclusa |
| Washington Monument | `nps.gov/wamo/planyourvisit/hours.htm` 200; `recreation.gov/ticket/facility/234635` **200** | | NPS: pubblico dominio |
| Alcatraz | `nps.gov/alca/planyourvisit/index.htm` **200**; venditore `cityexperiences.com` 502 | | |
| Statua della Libertà | `nps.gov/stli/planyourvisit/feesandreservations.htm` 404 | | indirizzo da trovare |
| Louvre | `louvre.fr/en/visit/hours-admission` **200**, 223 kB | | |
| Neuschwanstein | `neuschwanstein.de/englisch/tourist/tickets.htm` 404 | | indirizzo da trovare |

Aggiornamento: le regole cambiano poche volte all'anno; il controllo settimanale dell'impronta delle pagine (già nel metodo della sezione) basta. Licenza: si riportano date e regole (fatti), con il link alla fonte, come per le 6 attrazioni già online.

### Chi c'è su Google
"when do ghibli museum tickets go on sale": in testa il **sito ufficiale**, poi fun-japan.jp, afternoonteareads, jw-webmagazine, japantravel.com, real-japan-guide, jasumo: guide di blog, una per attrazione, scritte a mano. Per il sumo di gennaio le guide **non sono d'accordo** (torneo dal 9 o dal 10/1/2027; prezzi "non confermati"). È lo stesso quadro che ha fatto scegliere la sezione europea il 30/10: battibile sulla data esatta e aggiornata, non sul racconto.

### Chi paga
- AdSense su pubblico USA di viaggio (già attivo su Before You Fly).
- Viator (account creato, in analisi: vedi `monetizzazione.json` e la ricerca del 30/10) per le visite guidate con il biglietto incluso, utile quando è esaurito.
- **Klook**, il più forte per il Giappone: commissione dichiarata da terzi tra 2-5 % e 5 % sulle attrazioni (Involve Asia), cookie di 30 giorni; **non c'è una pagina ufficiale con la cifra**: da verificare all'iscrizione, che spetta a Massimiliano.

### Stima a 18 mesi (€/anno)
- **Centrale 600 €**: 3.000 visite/mese a 18 mesi (36.000 l'anno) × 1,3 pagine × 10 € ogni 1.000 pagine (pubblico USA di viaggio) = 470 €; più 1,5 % di clic sugli affiliati (540) × 8 % di acquisti (43) × 80 € di biglietto × 5 % ≈ 170 € → circa 600 €.
- **Prudente 150 €**: 1.000 visite/mese, solo AdSense.
- **Ottimista 2.000 €**: 9.000 visite/mese (il sumo e il Ghibli hanno picchi mensili) e Klook attivo.
- **Primi soldi**: dal primo mese di indicizzazione (la sezione madre è già indicizzata).

### Ore: 12-18
Regole nel file dei dati e calcolo della prossima data (4-6), pagine e `.ics` con il motore che c'è (4-6), controllo delle fonti e testi (2-3), revisione indipendente (2-3).

### Voto: 6,5
Domanda vera e mensile, fonti ufficiali che si leggono, motore già pronto, concorrenti a mano con date in contrasto. Non va più in alto perché il guadagno dipende da AdSense e da un affiliato (Klook) non ancora iscritto, e perché il sito ufficiale è primo per la domanda principale.

---

## 2. Calendario delle decisioni sui tassi delle banche centrali (voto 5,5, sito nuovo: NO)

### Che cosa è
Per circa 40 banche centrali: prossima decisione, ora locale e ora di Londra/New York, ultimo tasso, file `.ics` per banca e uno per tutte. È un fronte nuovo (finanza personale e mutui), con una pubblicità che paga più del turismo.

### Domanda (autocomplete, 31/10)
- USA: "next fed meeting" **10** ("date", "on interest rates", "prediction"); "fomc meeting dates 2027" 6.
- Regno Unito: "bank of england interest rate decision dates" 10 (con 2026 e **2027**); "next bank of england" 10.
- Australia: "rba meeting dates" 10 (con **2027 e 2028**); "next rba" 10.
- Canada: "bank of canada rate announcement dates" 10 (con 2027). Nuova Zelanda: "ocr announcement dates" 10 (con 2027).
- India: "rbi mpc meeting dates" 10 (con 2026-27 e 2027). Mondo: "central bank meeting calendar" 10 ("global", "brazil", "egypt", "canada").

### Fonti (curl, 31/10)

| Banca | Indirizzo | Esito |
|---|---|---|
| Federal Reserve | `federalreserve.gov/monetarypolicy/fomccalendars.htm` | **200**, 166 kB. Letto: "2027 FOMC Meetings: January 26-27, March 16-17, April 27-28, June 8-9, July 27-28, September 14-15, October 26-27, December 7-8" |
| Reserve Bank of Australia | `rba.gov.au/schedules-events/board-meeting-schedules.html` | **200**, 24 kB. Letto il calendario 2027 (8-9 febbraio, 22-23 marzo, 3-4 maggio, 21-22 giugno, 9-10 agosto, 27-28 settembre…) |
| Bank of England | `bankofengland.co.uk/monetary-policy/upcoming-mpc-dates` | **200**, 79 kB |
| Bank of Canada | `bankofcanada.ca/press/upcoming-events/` | **200**, 148 kB |
| BCE | `ecb.europa.eu/press/calendars/mgcgc/html/index.en.html` | **200**, 106 kB |
| Bank of Japan | `boj.or.jp/en/mopo/mpmsche_minu/index.htm` | **200**, 42 kB |
| Reserve Bank of New Zealand | `rbnz.govt.nz/news-and-events/events` | **403** |
| Tassi ufficiali (BIS, tutte le banche) | `stats.bis.org/api/v1/data/WS_CBPOL/M.US/all?lastNObservations=1` | **200** (API aperta) |

Le date escono una volta l'anno: l'aggiornamento è facile.

### Chi c'è su Google
"rba meeting dates 2027": **rbaratewatch.com** ha già una pagina per ogni riunione del 2027 (febbraio, marzo, maggio, giugno, agosto, settembre, novembre, dicembre) con conto alla rovescia e quote di mercato. Poi mnimarkets, financecalendar.com (una pagina per decisione), days.to. Per il mondo: **centralbank.watch** con lo strumento "calendar", investing.com e forexfactory con i calendari economici, i PDF delle banche d'affari (BMO). In più le banche stesse sono prime per le loro date. Battibile solo sulle banche piccole, dove però la pubblicità vale poco (Egitto, Brasile, Nigeria).

### Chi paga
AdSense finanza (in USA, Regno Unito e Australia vale molto più del turismo). Affiliati: i broker di trading pagano bene ma sono prodotti a rischio (CFD) e li escludo; mutui e conti di risparmio (comparatori australiani e britannici) da cercare: nessun programma letto. Wise per il cambio.

### Stima a 18 mesi (€/anno)
- **Centrale 1.800 €**: 8.000 visite/mese × 12 × 1,3 pagine × 15 € ogni 1.000 pagine ≈ 1.870 €.
- **Prudente 300 €**: 2.000 visite/mese a 10 €. **Ottimista 7.000 €**: 30.000 visite/mese (picchi nei giorni delle decisioni).
- Ore 25-35. **Voto 5,5**: domanda ricca e fonti perfette, ma il modello esatto esiste già (rbaratewatch, centralbank.watch, financecalendar) e il centrale resta sotto i 5.000 €. **NO come sito nuovo.**

---

## 3. Sorteggi e aperture delle vendite dei grandi eventi (voto 5, sito nuovo: NO)

### Domanda (autocomplete Regno Unito, inglese, 31/10)
Fortissima e con l'anno:
- "wimbledon ballot": 10 ("2027 dates", "2027 tickets release date", "2027 when does it open");
- "glastonbury 2027 tickets": 10 ("release date", "register", "sale date");
- "euro 2028 tickets": 10 ("ballot", "ballot timetable", "ballot date", "sign up");
- "ryder cup 2027 tickets": 10 ("ballot", "release date", "ireland");
- "rugby world cup 2027 tickets": 10 ("release date", "perth"); "six nations 2027 tickets": 10 ("release date ireland timetable", "wales", "scotland");
- "the open 2027 tickets": 10 ("ballot", "lottery", "st andrews"); "f1 tickets 2027": 10 (silverstone, monza, melbourne, montreal); "silverstone 2027 tickets": 10 ("release date"); in italiano "monza 2027 biglietti": 10 ("uscita biglietti", "quando escono");
- "eurovision 2027 tickets": 10 ("release date", "when will eurovision 2027 tickets go on sale");
- "tickets release date 2027": 10 (glastonbury, oasis, silverstone, ashes, wimbledon, tomorrowland, afcon);
- "ballot dates 2027": 10 (wimbledon, marathon, berlin).

### Fonti (curl, 31/10)
Pagine ufficiali leggibili: `wimbledon.com/en_GB/tickets` **200** (269 kB); LTA "Wimbledon ticket ballots" **200** (172 kB); `theopen.com/tickets-and-hospitality` **200**; `silverstone.co.uk/events/formula-1-british-grand-prix` **200**; `glastonburyfestivals.co.uk` **200** (la pagina biglietti rimanda alla home); `uefa.com/euro2028/` **000**. Ogni evento ha la sua pagina e il suo formato: si aggiorna solo con un agente che legge le pagine ogni settimana. Sono fonti "ufficiali" dell'organizzatore, non dati pubblici aperti.

### Chi c'è su Google
Per ogni evento: i **giornali** il giorno dell'annuncio (LBC, Time Out, Shortlist, ianVisits, Secret London, ITV, Official Charts, Radio X), siti a mano (britbrief.co.uk), rivenditori (goaltickets.com). Una pagina unica "tutte le aperture delle vendite" non esiste (la ricerca non l'ha trovata: solo koobit e frontstagefestivals con "date TBD"), ma la ricerca è per evento, non per calendario: la pagina unica non intercetta "wimbledon ballot 2027 dates".

### Chi paga
- **StubHub**: 4 % su quasi tutti gli eventi (0,8 % sul baseball), cookie 30 giorni, rete Partnerize (pagina della rete, senza data); altre directory dicono 3,2-9 %: cifra da verificare.
- **Ticketmaster UK**: circa 1 % con cookie di **1 giorno** (FlexOffers, affi.io; nessuna pagina ufficiale), rete Impact.
- Hotel vicino agli eventi (Stay22, già nel dominio degli affiliati di Before You Fly): quota non pubblicata.
- AdSense intrattenimento UK.

### Stima a 18 mesi (€/anno)
- **Centrale 1.200 €**: 6.000 visite/mese (72.000 l'anno) × 1,4 pagine × 7 € = 700 €; StubHub: 1 % di clic (720) × 3 % di acquisti (22) × 180 € × 4 % ≈ 160 €; hotel ≈ 300 €.
- **Prudente 200 €** (i giornali prendono tutto). **Ottimista 5.000 €** (25.000 visite/mese con 60-80 eventi e le citazioni degli assistenti IA).
- Ore 40-60 (60 eventi, pagine e `.ics`, agente settimanale). **Voto 5**: domanda enorme ma di cronaca, giornali sempre primi, commissioni basse. **NO come sito nuovo.**

---

## 4. Quando le compagnie aeree aprono le vendite (voto 5, sezione in coda bassa)

### Domanda (autocomplete Regno Unito, 31/10)
- "when does easyjet release flights": **10**, con il mese ("for july 2027", "for summer 2027", "for may 2027", "for feb 2027");
- "when does ryanair release": 10 ("summer 2027 flights", "april 2027", "winter 2026");
- "when do tui release": 10 ("2028 holidays", "summer 2027 holidays", "free child places");
- "easyjet release dates 2027": 9; "jet2 release dates": 3;
- "when do airlines release flights": 10 ("for august 2027", "how far in advance");
- "when do eurostar tickets go on sale": 10 ("for december 2026", "snap", "ski train");
- "when do cruise lines release": 10 ("2028 dates", "royal caribbean 2028").

### Fonti (curl, 31/10)
- easyJet `easyjet.com/en/flights-release` e `/schedule-release`: **403** (Akamai). Non si aggira: si leggono solo i comunicati.
- TUI `tui.co.uk/destinations/info/holiday-release-dates`: **403**. Jet2 `jet2.com/news`: **000**.
- Ryanair `corporate.ryanair.com/news/`: **200** (235 kB). British Airways media centre: **200**. Eurostar "booking horizon": **200** (3 kB).

### Chi c'è su Google
La pagina **ufficiale di easyJet** con l'iscrizione agli avvisi, MoneySavingExpert (Martin Lewis annuncia le date), i forum MSE, i giornali (GB News, Connexion, Travel Weekly, TravelMole). La notizia dell'estate 2027 di easyJet era del 28/7/2026: chi cerca a novembre trova già la risposta ufficiale.

### Chi paga
AdSense viaggi UK; vacanze a pacchetto (Jet2holidays, TUI, easyJet holidays) via Awin: **commissioni non lette**, da verificare.

### Stima e voto
100 / 500 / 1.500 €/anno (2.500 visite/mese nel centrale × 1,3 × 10 € ≈ 390 € più qualche pacchetto). Ore 8-12. **Voto 5**: domanda vera, ma le due fonti più cercate (easyJet e TUI) non si leggono dal server e l'ente risponde da sé. Sezione di Before You Fly in coda bassa, solo con le compagnie leggibili (Ryanair, BA, Eurostar, crociere).

---

## 5. Finestre di ammissione delle università italiane per studenti stranieri (voto 5, sezione in coda bassa)

### Domanda (autocomplete Pakistan e India, inglese, 31/10)
- "italian universities open for admission": 9 ("2026", "now", "**2027**");
- "polimi application deadline": 10 ("2027", "masters", "bachelor", "for international students", "2026 27");
- "sapienza application deadline": 10; "unibo application deadline": 10 (con altre università); "unipd application deadline": 3;
- "italy university application deadline 2027": 2; "universitaly pre enrollment 2027": poche varianti utili.

### Fonti (curl, 31/10)
`universitaly.it` **200** (143 kB); `unipd.it/en/how-apply` **200** (1,5 MB). Quattro indirizzi su sei provati per gli atenei (Polimi, Unibo, Sapienza, Statale di Milano) danno **404**: le pagine cambiano indirizzo ogni anno e i bandi sono in PDF. Circa 60 atenei con più turni ("rounds") ciascuno: fonte sparsa (vicina al filtro duro).

### Chi c'è su Google
Tabelle con le scadenze di hussainsilat.com, scholarsavenue.com (tabella 2027/28), waitaly.net, agenzie (Credila, Qogent, overseaspacific), post di LinkedIn. Le date sono in contrasto (30 aprile, fine maggio, inizio giugno per la preiscrizione).

### Chi paga
AdSense con pubblico di Pakistan, Bangladesh, Nigeria (vale poco); Wise per pagare le tasse; Uniplaces da verificare (ricerca del 30/10).

### Stima e voto
100 / 400 / 1.200 €/anno; ore 14-20. **Voto 5**: si appoggia alla sezione "Study in Italy" già costruita in Visa Income Checker e aggiunge un `.ics` per ateneo, ma la raccolta è manuale ogni anno e il pubblico paga poco. In coda bassa, solo per i 15 atenei più cercati.

---

## 6. Idee scartate, con le prove

### 6.1 Lotterie delle case a prezzo calmierato di New York (voto 4,5, NO)
- Fonte: NYC Open Data `vy5i-a666` "Advertised Lotteries on Housing Connect by Lottery", **200** in JSON: 1.754 lotterie dal 2020, circa 300 l'anno (2024: 325; 2025: 306; 2026: 196 fino a ottobre), con data di apertura e chiusura, alloggi, fasce di reddito, quartiere. Uso libero.
- Domanda: "housing connect lottery" 10, "nyc housing lottery" 10, "affordable housing lottery" 10 (anche Los Angeles, New Jersey, Long Island), "dahlia housing lottery" 10 (San Francisco).
- Perché NO: il file è aggiornato circa una volta al mese (ultimo aggiornamento 5/10/2026, letto il 31/10), mentre una lotteria resta aperta 3-4 settimane: molte si chiuderebbero prima di arrivare sul sito. Il portale Housing Connect è un'applicazione JavaScript; NY YIMBY scrive un articolo per ogni lotteria. Pubblico a basso reddito, pochi affiliati adatti.

### 6.2 Scioperi della metropolitana e dei treni nel Regno Unito (voto 4, NO)
- Domanda: "tube strike dates" 10, con i mesi del 2026 (maggio, giugno, agosto, settembre, ottobre); "tube strikes this week", "tomorrow", "today".
- Fonti: API di TfL `api.tfl.gov.uk/Line/Mode/tube/Status` **200** (JSON, stato delle linee); `tfl.gov.uk/campaign/strikes` **403**; National Rail "industrial action" **200** (239 kB).
- Perché NO: secondo Time Out e i tracker l'ultima serie di scioperi della metro è finita il 5/6/2026 e non ci sono nuove date annunciate; c'è già **tubenotifications.co.uk** dedicato, più BBC, Evening Standard, LBC, Time Out in giornata. Conferma la riserva del 17/10.

### 6.3 Date dei risultati degli esami professionali (voto 4, NO)
- Domanda forte: "bar exam results release date" 10 (Illinois, Texas, Massachusetts, New York, Georgia), "cpa score release dates" 10 (con 2027), "cfa results release date" 10, "acca results date" 10.
- Perché NO: le aziende di preparazione ne fanno il loro contenuto (JD Advising con la tabella Stato per Stato, UWorld, practicetestgeeks); NCBE e i singoli ordini pubblicano. Nessun buco.

### 6.4 Sorteggi delle maratone (voto 3,5, NO)
- Domanda: "london marathon ballot" 10, "berlin/nyc/chicago/tokyo marathon lottery" 10 ciascuna, "major marathon ballot dates 2027".
- Fonti ufficiali leggibili (Berlino, Chicago, Tokyo **200**; Londra **200** dopo il rinvio).
- Perché NO: **marathonballot.com** è già il sito automatico di questo modello: nella sitemap 261 pagine gara, 124 notizie, 39 strumenti tra cui "ballot calendar countdown". Più therunningchannel e marathonhandbook.

### 6.5 Ultime date di spedizione per Natale, Paese per Paese (voto 3,5, NO)
- Domanda: "last posting dates" 10, "last posting dates international" 10, "last day to ship" 10 (USPS, UPS, FedEx), "canada post holiday deadlines" 10, "an post christmas posting dates" 8, "australia post christmas cut off dates" 7.
- Perché NO: una data all'anno per servizio, pubblicata dalle poste stesse, che Google mostra nel riquadro; giornali e MoneySavingExpert ogni novembre. Tema stagionale di poche settimane.

### 6.6 Concorsi pubblici in scadenza in Italia (voto 3, NO)
- Domanda enorme ("concorsi in scadenza" 10, "bandi in scadenza oggi", "concorsi comune di milano/roma/napoli").
- Fonti: `inpa.gov.it` 200, ma il portale `portale.inpa.gov.it` è un'applicazione JavaScript (2,5 kB di HTML); Gazzetta Ufficiale, 4ª serie speciale, **200**.
- Perché NO: concorsando.it, ticonsiglio, concorsipubblici.com, InPA e i Comuni stessi; pubblicità italiana bassa. Stesso verdetto del concorso docenti (24/10).

---

## 7. Cosa resta come lezione per i prossimi giri

1. **Il file `.ics` non è un modello di guadagno da solo.** Tiene vicine le persone, ma la pubblicità si vede solo sulla pagina. Ogni evento nel calendario deve avere il link alla pagina con l'aggiornamento ("controlla qui se la data è cambiata"): è già così in Italy Strikes e va tenuto in ogni sezione nuova.
2. **Le date "di cronaca" (eventi, sorteggi, scioperi) vanno ai giornali; le date "di regola" (il 10 del mese, 30 giorni prima, ogni martedì) restano a noi.** La regola si calcola da sola, si mette in un `.ics` ricorrente e i blog la sbagliano. È il criterio per scegliere le prossime attrazioni e prenotazioni.
3. **Dove c'è un sito dedicato e automatico con lo stesso modello** (marathonballot, rbaratewatch, tubenotifications, parksdecoded il 30/10) non si entra: vincerebbe solo chi c'era prima.
4. Se si vuole un fronte nuovo più ricco in quest'angolo, il vincolo da allentare non è tecnico ma di canale: gli **avvisi a pagamento** ("ti scrivo quando escono i biglietti del sumo / della Ryder Cup") sono il prodotto naturale di questi calendari, ma sono vendita diretta e aspettano il cancello fiscale.

---

## 8. Righe proposte per ESPLORATE.md (da copiare a cura di chi tiene il file)

| Nicchia | Esito | Studio |
|---|---|---|
| **Biglietti a data fissa in Giappone e USA (Museo Ghibli il 10 del mese, Ghibli Park, Nintendo Museum, sumo per torneo, Shibuya Sky, teamLab, Palazzo Imperiale, Fuji; Washington Monument, Statua della Libertà, Alcatraz) con `.ics` mensili** | **SEZIONE da costruire** (voto 6,5; 150 / 600 / 2.000 €/anno; 12-18 ore) come allargamento di Ticket release dates di Before You Fly; sumo di gennaio in vendita dal 5/12 (da confermare) | wf-2026-10-31-eventi-calendari |
| Calendario delle decisioni di ~40 banche centrali con `.ics` e tassi BIS | NO come sito (5,5; 1.800 € centrali): rbaratewatch, centralbank.watch, financecalendar | wf-2026-10-31-eventi-calendari |
| Sorteggi e aperture delle vendite dei grandi eventi (Wimbledon, Euro 2028, Ryder Cup, Glastonbury, F1, Eurovision) | NO come sito (5; 1.200 € centrali): giornali in giornata, StubHub 4 %, Ticketmaster UK ~1 % con cookie di 1 giorno | wf-2026-10-31-eventi-calendari |
| Quando le compagnie aeree aprono le vendite (easyJet, Ryanair, Jet2, TUI, BA, Eurostar) | sezione in coda bassa (5; 100 / 500 / 1.500 €): easyJet e TUI 403, Jet2 000 | wf-2026-10-31-eventi-calendari |
| Finestre di ammissione delle università italiane per stranieri, con `.ics` | sezione in coda bassa (5; 100 / 400 / 1.200 €) in Study in Italy | wf-2026-10-31-eventi-calendari |
| Lotterie delle case di New York (Housing Connect); scioperi metro/treni UK; risultati esami professionali; sorteggi maratone; date di spedizione per Natale; concorsi pubblici italiani | NO (3-4,5), prove nel rapporto | wf-2026-10-31-eventi-calendari |
