# Angolo C — Regole di viaggio e dati ufficiali di viaggio nel mondo

Data: **10 ottobre 2026** (controlli dal server della sessione, 18:00-21:00 UTC).
Cartella: `scratchpad/globale/C/` — `ac1..ac5.json/.txt` (autocomplete grezzo: 183 ricerche × 3 mercati = 549 chiamate), `dl/` (92 file + 226 pagine FCDO, 31 MB, letti solo con `python3 -I`), `script/` (scanner, sonde, analisi).
Nessun file del repository `copertine-libri` è stato toccato.

**Criterio (lo stesso dello studio 14, scritto prima):** passa se (1) domanda confermata nell'autocomplete in ≥ 2 mercati tra USA/UK/Australia; (2) fonte ufficiale gratuita leggibile da programma (HTTP 200 dal server, senza login) o al massimo 3 fonti per pagina; (3) nessun sito inglese già dominante che fa la stessa cosa; (4) ricavo prudente ≥ 1.500 €/anno a 18 mesi (da solo o come parte della rete). Dove manca un dato scrivo "non trovato".

---

## 0. Risposta in breve

- La **domanda c'è per tutto** (183 ricerche su 183 con suggerimenti in 3 mercati su 3). Come nello studio 14, la domanda non decide nulla: decidono la fonte e la concorrenza.
- Le grandi regole "nuove" (EES, ETIAS, UK ETA, ESTA, calcolatore Schengen) hanno domanda enorme ma sono **presidiate dagli enti stessi e da decine di siti grandi**; ETIAS non è nemmeno partito e non ha una data. Si possono usare solo come **pagine dentro la rete**, non come siti.
- Ho trovato **3 idee che passano** (piccole-medie, nessuna "grande"):
  1. **Liquidi in aeroporto, aeroporto per aeroporto (100 ml o 2 litri?)**, con la frase ufficiale citata e la data del controllo settimanale. Domanda 3/3 su **46 aeroporti** provati, confusione vera (anche le pagine ufficiali di Francoforte si contraddicono), concorrenti solo articoli scritti a mano.
  2. **Validità del passaporto per 225 Paesi (passaporto britannico)**, calcolatore + "regole cambiate questa settimana", da **una sola fonte** (GOV.UK Content API, 226/226 pagine scaricate senza errori, licenza OGL).
  3. **Global Entry: primo appuntamento libero per ogni centro USA**, dall'API pubblica del CBP (131/131 centri letti, 0 errori). Pubblico USA (pubblicità più ricca), nessuna pagina gratuita aggiornata trovata.
- Più due "pagine di rete" utili e una cosa da fare subito: pagina **EES/ETIAS stato ufficiale** (2-4 ore), **confronto avvisi di viaggio USA/UK/Canada** (fonti 3/3 aperte, concorrenza media), e il **riquadro rimborso voli (AirHelp/Compensair) nel sito scioperi** (mezz'ora, soldi piccoli ma sicuri nei giorni di sciopero).
- Onestà sulle dimensioni: ognuna vale **0,1-1 k€ a 12 mesi e 0,3-2 k€ a 18 mesi** con stime prudenti. Insieme, in una rete "prima di volare", possono arrivare a 1,5-4 k€/anno a 18 mesi. Non sono un nuovo "Italy Strikes".

---

## 1. Tabella di tutti i controlli

Legenda domanda: "3/3" = suggerimenti in USA, UK e Australia. Fonte: codice HTTP dal server con User-Agent da browser. Verdetto: **PASSA**, **PAGINA** (solo pagina dentro la rete), **NO**.

| # | Idea | Domanda (autocomplete, esempi) | Fonte ufficiale provata | Esito fonte | Concorrenza (chi si posiziona) | Soldi | Verdetto |
|---|---|---|---|---|---|---|---|
| 1 | **EES** (Entry/Exit System) regole e code | 3/3: "ees border queues", "ees dover delays", "ees eurostar delays", "cdg/fco ees wait times today", "ees exemptions" | travel-europe.europa.eu: **certificato incompleto + pagina "Error" (anti-robot)**; home-affairs.ec.europa.eu **200** | Regole sì (Commissione: "pienamente operativo il 10 aprile 2026", tranne Cipro e Irlanda; avviato il 12/10/2025). **Tempi di attesa: nessuna fonte ufficiale** | Commissione, gov.uk, giornali; **flightqueue.com** fa già "EES live" con stime e segnalazioni degli utenti | assicurazione, eSIM | **PAGINA** (regole); code live **NO** |
| 2 | **ETIAS** stato e data di avvio | 3/3: "etias start date 2027", "etias delayed to 2027", "etias delayed indefinitely", "etias fee increase 2026" | home-affairs.ec.europa.eu 200 | Commissione: "ETIAS is currently not in operation… the EU will inform about the specific date… several months prior to its launch". A luglio 2026 tolto l'obiettivo "ultimo trimestre 2026" (Navan) | etias.com-tipo, schengenvisainfo, giornali, siti a pagamento che imitano l'ufficiale | servizi visti (iVisa: commissioni 10-20 % secondo gli aggregatori, programma forse chiuso) | **PAGINA** ("stato ufficiale, controllato ogni giorno") |
| 3 | **UK ETA** | 3/3: "uk eta cost for us citizens", "uk eta transit heathrow", "uk eta official website" | GOV.UK Content API `/api/content/eta` **200** JSON | Dato chiaro: "An ETA costs £20… Other websites may charge more… Avoid websites that imitate government services" | gov.uk primo; rivenditori | solo rivenditori (= imitatori) | **NO** |
| 4 | **ESTA** USA | 3/3 ma "esta" inquinato ("estate sales"); "esta cost increase", "esta application official site" | esta.cbp.dhs.gov 200 (pagina JS 2 KB) | regole statiche | CBP + rivenditori | come sopra | **NO** |
| 5 | **Attese visto USA per consolato** | 3/3: "us visa wait times india/chennai/mumbai", "canada", "sydney" | travel.state.gov pagina e database **403** | non leggibile dal server | molti siti indiani | pubblico per lo più India (RPM basso) | **NO** |
| 6 | **Calcolatore Schengen 90/180** | 3/3: "schengen calculator official", "90/180 rule spain" | calcolatore ufficiale della Commissione (home-affairs 200) | esiste già | Commissione + AXA, HelloSafe (assicurazioni che lo usano per vendere), app | assicurazione | **NO** (nessuno spazio) |
| 7 | **Validità passaporto per Paese** | 3/3: "passport validity calculator/checker", "passport 6 months validity calculator", "passport validity requirements for spain/uk/dominican republic" | **GOV.UK Content API** per 226 Paesi **200** (226/226); travel.state.gov **403** | regola classificata in automatico in **208/226** pagine (vedi §2.2) | wecovr, europevisacheck, mybritishpassport (lanciato 9/2025), articoli booking/kiwi; gov.uk non ha calcolatore | assicurazione, eSIM | **PASSA** (solo passaporto UK) |
| 8 | **Avvisi di viaggio confrontati** (USA/UK/Canada/Australia) | 3/3: "travel advisory italy today", "is it safe to travel to paris right now", "fcdo travel advice dubai" | USA RSS **200** (223 Paesi, livelli 1-4); UK API **200** (226); Canada JSON **200** (230); Australia **errore HTTP/2 / timeout** | 3 fonti su 4 | TravelWarningCheck (aprile 2026), travel-advisory.info, Actor Apify; pagine-spam che copiano | assicurazione | **PAGINA/rete** (YMYL, concorrenza media) |
| 9 | **Eurocontrol / ritardi ATC Europa** | 3/3: "eurocontrol delays today", "flight delays europe today" | ansperformance.eu 200 ma dati **mensili** (fino ad agosto 2026); portale NOP = app JS da 1,4 KB | nessun dato "oggi" aperto | Eurocontrol, FlightAware, giornali | – | **NO** |
| 10 | **Scioperi ATC/compagnie in Europa** | 3/3: "french air traffic control strike dates 2026", "ryanair strikes 2026 timetable" | nessun registro fuori Italia (studi 10, 11, 14) | – | giornali | – | **NO** (l'Italia c'è già) |
| 11 | **Rimborso voli EU261/UK261** | 3/3: "eu261 compensation table", "uk261 claim", "airhelp legit" | regole: Your Europe 200, CAA 200 | statiche | AirHelp, Flightright, Compensair sono loro stessi i giganti SEO | **AirHelp 15 %** (media 70 €/pratica approvata, pagina AirHelp); Travelpayouts: 15-16,6 %, eCPC **0,01 $**, cookie 45 gg; **Compensair 5-12 €**, eCPC **0,04 $** | sito **NO**; **riquadro nel sito scioperi SÌ** |
| 12 | **Franchigie dogana (duty free)** | 3/3: "duty free allowance uk to spain/ireland/turkey", "cbp duty free limit" | GOV.UK API 200; Your Europe 200; cbp.gov **403** | regole statiche | aph.com, entrybrief.com (sito programmatico), gov | parcheggi (APH) | **NO** (statico, nessun vantaggio automatico) |
| 13 | **Limiti di contanti** | 3/3: "how much cash can i travel with internationally" | EU taxation-customs 404 all'URL provato; regola fissa 10.000 € (Reg. UE 2018/1672) | statica | gov, banche | – | **NO** |
| 14 | **Prese/voltaggio** | 3/3: "plug types by country", "travel adapter for italy" | iec.ch/world-plugs **202** (sfida anti-robot) | statica | worldstandards.eu, Amazon | Amazon (bassa) | **NO** |
| 15 | **Mance** | 3/3 | nessuna fonte ufficiale (escluso dal mandato) | – | – | – | **NO** |
| 16 | **Festivi nel mondo** | 3/3: "public holidays 2027", "bank holidays 2027 uk" | gov.uk/bank-holidays.json 200; Nager.Date 200 | ottime | timeanddate, officeholidays dominano (studio 14) | – | **NO** |
| 17 | **Ora legale** | 3/3: "when do clocks change 2026" | – | – | timeanddate domina | – | **NO** |
| 18 | **Liquidi ai controlli (100 ml / 2 litri)** | 3/3 su **46 aeroporti** + generiche ("100ml rule airports", "european airports with new scanners", "2 litre liquids gatwick", "liquid restrictions barcelona airport today") | pagina ufficiale di ogni aeroporto | **7 su 16** leggibili subito con la frase della regola (LHR, LGW, FRA, DUB, HEL, MAN, STN); 5 bloccate (AMS, CDG, BHX, ATH 403; FCO 202); 1 JS (LIS); 3 URL da correggere | tripprof (tabella manuale, ~17 aeroporti), heygyro, travelsort, Which?, giornali; **nessun sito per-aeroporto aggiornato in automatico** | pubblicità; Holiday Extras (parcheggi/lounge, 1,6-12 % secondo aggregatori), Kiwitaxi 9-11 %, EKTA 20 % | **PASSA** |
| 19 | **Vignette autostradali** (AT, CH, CZ, SI, HU) | 3/3: "austria vignette official website", "do i need a vignette for austria", "czech vignette check" | ASFINAG **403**; CH via.admin.ch 200; CZ edalnice 200; SI **reset**; HU 200 (1 KB) | prezzi annuali (Austria 10 giorni 2026: 12,80 €; dal 2027 solo digitale) | fuel-prices.eu, tollguru, guide; rivenditori con sovrapprezzo | solo rivenditori (Vintrica via Daisycon, % non pubblica) → contro "solo ufficiale" | **NO** (statico, affiliato ambiguo) |
| 20 | **Zone a basse emissioni** | 3/3: "crit air paris english", "low emission zone checker", "umweltplakette frankreich" | urbanaccessregulations.eu 200 (progetto finanziato UE); certificat-air.gouv.fr 200; UBA 404 | lista esiste già | urbanaccessregulations, Green-Zones (app), APH; rivenditori Crit'Air a ~30 € | – | **NO** (studio 6 già simile) |
| 21 | **Patente internazionale (IDP)** | 3/3: "do i need an international driving permit for italy", "idp aaa" | gov.uk API 200; travel.state.gov 403 | statica | AAA, Post Office, gov | – (siti IDP falsi) | **NO** |
| 22 | **Global Entry, appuntamenti per centro** (extra) | 3/3 su 12 città ("global entry appointment jfk/lax/dfw…", "global entry interview wait times", "global entry next available appointment") | CBP TTP `schedulerapi` **200** JSON, senza chiave | **131/131** centri USA letti, 0 errori | TPG (fotografie manuali), app/servizi a pagamento (Appointment Scanner 29 $), bot open source | pubblicità USA | **PASSA** (con rischio blocco) |
| 23 | **Attese ai controlli di sicurezza** (extra) | 3/3: "dublin airport security wait times live", "heathrow security wait times terminal 5", "how early to get to dublin airport" | Dublin `/upi/SecurityTimes/GetTimes` **200** (`{"T1":"= 3","T2":"= 3"}`); Heathrow `pihub/securitywaittime` **200** JSON; Schiphol 403 | dati in tempo reale, API interne del sito, nessuna licenza | gli aeroporti stessi (sito e app) | parcheggi, lounge | **solo test** (vedi §4) |

---

## 2. Le candidate che passano

Ipotesi comuni (come studio 14 e 12, da non vendere come promessa): RPM pubblicità Tier 1 **5-12 $** (benchmark viaggi 8-18 $, AdSense non-Journey 5-15 $); affiliazione viaggi **1,5-5 $ per 1.000 visite**; 1 $ ≈ 0,92 €. I volumi **non sono misurabili dal server** (Google Trends 429): le visite sono ordini di grandezza. Ore: riuso del motore `italystrikes/genera.py` (pagine, `vista.json`, workflow GitHub Actions).

### 2.1 "Airport Liquid Rules" — 100 ml o 2 litri? Aeroporto per aeroporto, controllato ogni settimana (PASSA; la migliore)

**Cosa è.** Una pagina per aeroporto (80-150 aeroporti in Europa, UK, Irlanda, poi Nord America/Asia/Oceania) che risponde in una riga: "**Heathrow: contenitori fino a 2 litri, liquidi nella borsa — secondo la pagina ufficiale, controllata il 13/10/2026**", con la frase ufficiale citata tra virgolette, il link, le eccezioni (terminal, varchi transfer, voli USA/Israele/Australia), e la regola dell'aeroporto del ritorno. Più una tabella generale "dove si può portare 2 litri oggi" e un archivio dei cambi ("Francoforte ha cambiato la pagina il …").

**Prove.**
- Domanda: 3/3 su **46 aeroporti** provati (Heathrow con i terminal 2/3/4/5, Gatwick North/South, Manchester T1/T2/T3, Dublin T1/T2, Stansted, Edinburgh, Birmingham, Bristol, Glasgow, Luton, Newcastle, Belfast, Cork, Amsterdam, Roma, Milano, Venezia, Napoli, Francoforte, Monaco, Madrid, Barcellona, Malaga, Palma, Parigi, Nizza, Lisbona, Faro, Atene, Helsinki, Copenaghen, Vienna, Zurigo, Praga, Budapest, Cracovia, Bruxelles, Istanbul, Dubai, Singapore, Toronto, Auckland, Melbourne, Sydney). Ci sono anche query "**today**" ("liquid restrictions barcelona airport today", "liquid restrictions newcastle airport today") e per anno ("frankfurt airport liquid rules 2026").
- Confusione reale, misurata oggi: GOV.UK scrive solo "The rules … depend on the airport. Before you travel, check the rules" (API `hand-luggage-restrictions` 200); Manchester: "under 100ml each… no longer need to be in a plastic bag"; Dublino: "The previous 100ml maximum limit … no longer applies, and items in containers up to 2 litres can be brought through security"; Francoforte: 2 litri "at most security checkpoints in Terminal 1 and at all checkpoints in Terminal 3" ma 100 ml ai varchi transfer e speciali — e un'altra pagina Fraport dice il contrario (trovato in ricerca). I siti di terzi si contraddicono tra loro (Southend 2 litri o 100 ml?).
- Fonte: **una per pagina** (la pagina dell'aeroporto). Test di oggi: 7/16 leggibili con la frase della regola; 5 bloccate dal server (Schiphol, Paris Aéroport, Birmingham, Atene 403; Fiumicino 202); 1 JavaScript (Lisbona); 3 URL da correggere (Edimburgo, Monaco, Madrid).
- Concorrenza: articoli scritti a mano e datati (tripprof: una tabella con "Confirmed Sep 2026" su ~17 aeroporti e "Reported, not independently confirmed" su altri; heygyro ~13 aeroporti; travelsort "Updated January 2025"; Which?; Express & Star; blog Holiday Extras). **Nessun sito con una pagina per aeroporto aggiornata in automatico.**

**Soldi.**
- Pubblicità: pubblico UK/Irlanda/USA/Australia, stagione lunga (vacanze estive + Natale).
- Affiliazioni pertinenti al momento (chi cerca le regole dei liquidi sta per partire): **parcheggi, lounge, hotel aeroporto** (Holiday Extras su Awin: 1,6 % secondo Revshare/FlexOffers, "1,6-12 %" secondo FlexOffers UK — la cifra vera si legge solo nel pannello Awin); **transfer** (Kiwitaxi su Travelpayouts: 9-11 %, prezzo medio 77 $, eCPC 0,05 $); **assicurazione** (EKTA 20 %, prezzo medio 18 $); eSIM (Yesim 18 %, cookie 90 giorni).
- Stima prudente (ipotesi: a 12 mesi 2.000-8.000 visite/mese in media, 1,2 pagine per visita, RPM 6-10 $, affiliazioni 1,5-5 $/1.000 visite): **12 mesi 150-900 €; 18 mesi 500-2.000 €**. Sopra i 1.500 € solo se entra nei primi 3 risultati per gli aeroporti grandi del Regno Unito.

**Ore:** 14-20 (elenco aeroporti con URL ufficiale; estrattore per frasi "100 ml / 2 litres / CT scanner / plastic bag"; impronta della pagina e confronto settimanale; pagine aeroporto + tabella + archivio cambi; workflow settimanale). Per le pagine bloccate: la routine del lunedì di Claude le legge con WebFetch e aggiorna a mano la data (10-15 minuti a settimana) oppure si esce solo con gli aeroporti leggibili.

**Rischi.** Pagine degli aeroporti che cambiano indirizzo (gestibile: allarme se 404); pagine ufficiali che si contraddicono (si mostrano entrambe con data, mai una scelta nostra); responsabilità bassa (il danno massimo è un flacone buttato) ma si scrive sempre "Fonte: pagina ufficiale dell'aeroporto, controllata il …; verifica prima di partire"; un sito grande (Which?, Holiday Extras) può fare una tabella migliore; Google può rispondere direttamente con la pagina dell'aeroporto.

**Test tecnico a costo zero (14 giorni):**
1. Elenco di **60 aeroporti** con la pagina ufficiale. Lettura giornaliera dal server e da un workflow GitHub Actions di prova (repository pubblico, 0 €).
2. Soglie: (a) **≥ 70 % (42/60)** delle pagine lette con HTTP 200 e una frase-regola estratta in ≥ 12 giorni su 14; (b) confronto a mano su 20 aeroporti: regola estratta corretta in **≥ 95 %**; (c) falsi "cambi" (pagina cambiata senza cambio di regola) **≤ 10 %** delle letture; (d) almeno 25 dei 42 leggibili devono essere aeroporti con domanda 3/3 dell'elenco sopra.
3. Se passa → costruzione. Se (a) < 50 % → NO (troppe pagine da fare a mano).

### 2.2 "Passport Validity Checker" — passaporto britannico, 225 destinazioni, fonte unica GOV.UK (PASSA, piccola)

**Cosa è.** Un calcolatore ("data di rilascio, data di scadenza, Paese, date del viaggio → la regola ufficiale dice OK / non OK") con la frase dell'FCDO citata, più una pagina per Paese ("Passport validity for Spain/Turkey/USA…") e una pagina "regole d'ingresso cambiate questa settimana".

**Prove.**
- Domanda: 3/3 per "passport validity calculator" (anche "uk", "eu", "usa"), "passport validity checker" ("uk", "turkey", "spain"), "passport 6 months validity calculator", "passport expiry rules uk/europe/spain/turkey", "passport validity requirements for …".
- Fonte: GOV.UK Content API (`/api/content/foreign-travel-advice/<paese>`), JSON, **226/226 pagine scaricate oggi, 0 errori**, licenza **Open Government Licence v3** (riuso commerciale consentito con attribuzione). Ogni pagina ha la sezione "Passport validity requirements". Classificazione automatica di oggi: **114 "6 mesi"**, **35 "per la durata del soggiorno"**, **33 "Schengen: rilascio < 10 anni + 3 mesi dopo l'uscita"**, **24 "3 mesi"**, 2 "1 mese", **17 casi particolari** (es. Israele 90 giorni dall'arrivo, Costa Rica 1 giorno dopo l'uscita, St Lucia "dopo il giorno di uscita") da tradurre in regole a mano, 1 senza sezione (Irlanda). Copertura automatica **92 %**.
- Aggiornamenti: **80 note di modifica in 30 giorni** su tutto l'FCDO; il campo `change_history` dà data e testo (es. Italia 11/8/2026 "Updated information on European Entry-Exit System"). Utile per la pagina "cosa è cambiato".
- Concorrenza: wecovr (assicurazioni), europevisacheck, mybritishpassport (calcolatore gratuito da settembre 2025), articoli di Booking e Kiwi sul "10-year rule". GOV.UK è la fonte e si posiziona bene ma **non ha un calcolatore**.
- Per i passaporti USA la fonte (travel.state.gov) dà **403** dal server: oggi non si può.

**Soldi.** Pubblicità UK; affiliazioni: assicurazione (EKTA 20 %), eSIM (Yesim 18 %); nessun affiliato per il rinnovo del passaporto (solo il governo: niente "agenzie fast track"). Stima prudente: **12 mesi 100-600 €; 18 mesi 300-1.400 €**.

**Ore:** 10-14 (lettore API, classificatore + 17 regole a mano, calcolatore in JavaScript nella pagina, pagine Paese, pagina cambi, workflow giornaliero).

**Rischi.** Responsabilità **media**: un passeggero respinto all'imbarco è un danno vero → mai "OK garantito", sempre "secondo la regola FCDO aggiornata il …, controlla con la compagnia aerea"; nessun dato personale salvato (il calcolo avviene nel browser). La parte Schengen è affollata (ci sono già 4-5 calcolatori): il valore sta nei 190 Paesi non Schengen.

**Test tecnico (14 giorni):** lettura giornaliera delle 226 pagine → soglie: **≥ 99 %** risposte 200; classificatore che resta stabile (nessun Paese cambia categoria senza una nota in `change_history`); controllo a mano di 30 Paesi a caso: regola corretta in **30/30**; almeno **5 cambi reali** di regole d'ingresso registrati nelle 2 settimane (se 0, la pagina "cambi" non regge e si fa solo il calcolatore).

### 2.3 "Global Entry Appointment Finder" — primo appuntamento libero per ogni centro (PASSA, con rischio)

**Cosa è.** Una pagina per centro d'iscrizione (JFK, LAX, O'Hare, Atlanta, DFW…): "primo appuntamento libero alle ore X di oggi: il 26 ottobre", numero di posti nei prossimi 30 giorni, grafico delle ultime settimane, link al sito ufficiale per prenotare, e la spiegazione ufficiale di "Enrollment on Arrival". Non è un servizio di allerta a pagamento.

**Prove.**
- Domanda: 3/3 per 12 città ("global entry appointment jfk terminal 4", "global entry interview dfw terminal d", "global entry interview atlanta walk in"…), "global entry interview wait times", "current global entry interview wait times", "global entry next available appointment", "global entry enrollment on arrival locations", "nexus appointment blaine".
- Fonte: CBP Trusted Traveler `schedulerapi` (`/locations` 200, 135 centri Global Entry, 131 negli USA; `/slots?orderBy=soonest&locationId=…` 200). Oggi **131/131 letture, 0 errori**. Dati del 10/10/2026: **mediana 3 giorni** al primo posto libero, massimo **152 giorni**, **24 centri senza posti**; esempi: JFK oggi, LAX oggi, DFW 26/10, Denver 28/10. Opere del governo USA = pubblico dominio; **nessuna condizione d'uso pubblicata per l'API** (è quella usata dal sito; la usano anche bot open source dal 2019).
- Concorrenza: The Points Guy (tabelle fatte a mano, una tantum), Chase (guide), FlyerTalk; servizi di allerta a pagamento (Appointment Scanner 29 $) e app. **Nessuna pagina gratuita per centro aggiornata ogni giorno trovata.**

**Soldi.** Solo pubblicità (pubblico USA, l'RPM più alto); le carte di credito che rimborsano Global Entry pagano molto ma i programmi non hanno commissioni pubbliche e richiedono approvazione → non contate. Stima prudente: **12 mesi 100-700 €; 18 mesi 300-1.300 €**. Picchi quando le attese si allungano (febbraio-marzo 2026: programma sospeso per lo shutdown del DHS, interviste ferme).

**Ore:** 8-12 (lettore 131 centri × 2 volte al giorno = 262 richieste/giorno, pagine centro, storico in `vista.json`, workflow).

**Rischi.** CBP può bloccare o cambiare l'API senza avviso (nessun contratto); oggi le attese sono brevi (mediana 3 giorni) → meno interesse; politica (sospensioni, cambi del programma: autocomplete "is global entry going away"); pubblico solo USA, fuori dal "pubblico unico" della strategia (ma soldi migliori).

**Test tecnico (21 giorni):** letture 2 volte al giorno da GitHub Actions → soglie: **≥ 97 %** risposte 200 su tutte le letture; nessun blocco (403/429) per 21 giorni; almeno **20 centri** con primo posto libero **≥ 14 giorni** in almeno una lettura (altrimenti non c'è "attesa" da raccontare e il valore cala); controllo a mano su 5 centri: data uguale a quella del sito ufficiale.

### 2.4 Pagine di rete (non siti)

- **"EES & ETIAS: official status today"** (2-4 ore). Fonte: home-affairs.ec.europa.eu (200 dal server; il sito travel-europe.europa.eu dà certificato incompleto e pagina di errore anti-robot). Il lettore controlla ogni giorno la frase "ETIAS is currently not in operation" e la data delle notizie ufficiali; la pagina dice "nessuna data ufficiale; ultimo controllo il …". Domanda enorme ("etias delayed to 2027", "etias start date for us citizens"), concorrenza enorme: utile come pagina d'ingresso alla rete, non come sito. Ricavo: 50-300 €/anno.
- **"Travel advisory: US vs UK vs Canada"** (12-16 ore). Fonti: USA RSS (223 Paesi, livelli 1-4; 4 cambi negli ultimi 30 giorni), UK API (226, con `alert_status` e cronologia), Canada JSON (230 Paesi, `advisory-state`). Australia non leggibile dal server. Concorrenti: TravelWarningCheck (aprile 2026), travel-advisory.info, un Actor Apify, e pagine-spam che copiano. Tema "sicurezza" = YMYL, Google premia gli enti. Ricavo 100-500 €/anno. Ha senso solo nello stesso sito del 2.2 (stessa fonte UK).
- **Riquadro "Flight cancelled by the strike? You may be owed €250-600"** nel sito Italy Strikes Today (mezz'ora). Con le regole EU261 citate dalla pagina Your Europe (200) e la frase "verifica con la compagnia/l'ente". Programmi: **Compensair** (Travelpayouts: 5-12 € a pratica, eCPC 0,04 $, cookie 30 giorni) e **AirHelp** (15 % sul compenso di AirHelp, media 70 € per pratica approvata dichiarata da AirHelp; Travelpayouts 15-16,6 %, eCPC 0,01 $, cookie 45 giorni). Nota: AirHelp vieta Google Ads (studio 12), ma il traffico organico va bene. Con eCPC 0,01-0,04 $ servono 1.000 clic per 10-40 $: soldi piccoli, ma zero lavoro e pubblico perfetto (voli cancellati per sciopero; attenzione: lo sciopero del personale della compagnia dà diritto, quello dei controllori di solito no → citare la regola, non decidere noi).

---

## 3. Scartate, con la prova

| Idea | Prova del no |
|---|---|
| Code EES in tempo reale | Nessun dato ufficiale delle code di frontiera; Commissione e giornali parlano di attese fino a 2-3 ore (ACI Europe/A4E) ma non pubblicano numeri aperti; flightqueue.com fa già "EES live" con stime e segnalazioni. |
| ETIAS come sito | Non è in funzione e non ha data ("currently not in operation"); i siti che lo spiegano sono centinaia, alcuni imitano l'ufficiale; l'unico affiliato (servizi visti, iVisa) ha stato incerto (affi.io: "Closed") e vende un modulo che costerà 20 € sul sito ufficiale. |
| UK ETA / ESTA | Il governo stesso avverte: "Other websites may charge more… Avoid websites that imitate government services" (GOV.UK, ETA £20). Guadagnare lì significa mandare gente ai rivenditori: no. |
| Attese visto USA | travel.state.gov 403 dal server; pubblico in gran parte indiano ("india", "chennai", "mumbai" nei suggerimenti) → RPM basso; molti siti già fatti. |
| Calcolatore Schengen | Esiste quello ufficiale della Commissione; AXA, HelloSafe e varie app lo offrono gratis per vendere assicurazioni. |
| Eurocontrol / ritardi ATC | Dati aperti solo mensili (da gennaio 2011 ad agosto 2026); il portale operativo NOP è un'app JavaScript; nessun dato "oggi". |
| Scioperi ATC e compagnie in Europa | Nessun registro pubblico fuori Italia (già provato per Francia, Spagna, Grecia, Portogallo, Germania e altri negli studi 10, 11, 14). |
| Calcolatore EU261 come sito | I giganti sono gli stessi che pagano l'affiliazione (AirHelp, Flightright, Compensair); eCPC 0,01-0,04 $. Solo riquadro nei siti esistenti. |
| Franchigie dogana, limiti di contanti, IDP | Regole statiche, già spiegate da GOV.UK/Your Europe e da siti come aph.com, entrybrief.com; cbp.gov 403. Nessun vantaggio dall'automazione. |
| Prese e voltaggio, ora legale, festivi | Domanda enorme ma dominata da worldstandards.eu e timeanddate (studio 14); iec.ch dà 202 (anti-robot). |
| Mance | Nessuna fonte ufficiale (escluse dal mandato). |
| Vignette | ASFINAG 403; prezzi fissi una volta l'anno (Austria 10 giorni 12,80 € nel 2026, dal 2027 solo digitale); fuel-prices.eu e tollguru già coprono; l'unico affiliato è un rivenditore (Vintrica) che aggiunge un costo → contro la regola "solo ufficiale". |
| Zone a basse emissioni | urbanaccessregulations.eu (progetto UE) e Green-Zones coprono già tutta Europa; i rivenditori Crit'Air chiedono ~30 € contro ~4 € ufficiali. |

---

## 4. Idea da tenere in tasca (non passa oggi)

**"How early to get to the airport": storico delle attese ai controlli** dai dati ufficiali in tempo reale di Heathrow (`api-dp-prod.dp.heathrow.com/pihub/securitywaittime`, 200, per terminal, "Less than 5 minutes") e Dublino (`/upi/SecurityTimes/GetTimes`, 200, `{"T1":"= 3","T2":"= 3"}`). Domanda 3/3 ("dublin airport security wait times live", "how early to get to dublin airport for us flight", "how early should i get to heathrow terminal 5"). Non passa oggi perché: (a) il dato "adesso" lo mostrano già gli aeroporti, e un sito aggiornato 2 volte al giorno non può essere "live"; (b) il valore sarebbe la **media per ora e giorno** (es. "lunedì alle 6 a Dublino T1: 12 minuti"), che richiede letture ogni 15-30 minuti per 2-3 mesi; (c) sono API interne dei siti, **senza licenza**: ripubblicare aggregati è probabilmente lecito, copiare il flusso no. Se un giorno si fa il sito 2.1, si può aggiungere come sezione delle pagine Heathrow e Dublino dopo 8 settimane di raccolta silenziosa.

---

## 5. Ordine consigliato e somma onesta

1. **Subito (0,5 ore):** riquadro Compensair/AirHelp nel sito scioperi (serve l'iscrizione a Travelpayouts di Massimiliano, 10 minuti, già nel suo elenco "da fare").
2. **Test 2.1 liquidi** (14 giorni, 0 €) → se passa, costruzione 14-20 ore. È la più ampia (mondo intero, 46 aeroporti con domanda già provata) e la più "nostra" (fonte ufficiale citata, aggiornamento automatico, nessuno lo fa per aeroporto).
3. **Test 2.2 passaporto** (14 giorni) → costruzione 10-14 ore, con la pagina EES/ETIAS (2.4) dentro lo stesso sito "Before You Fly".
4. **Test 2.3 Global Entry** (21 giorni) → solo se 2.1 e 2.2 sono partiti; pubblico diverso.

Somma prudente se tutte e tre passano e indicizzano: **12 mesi 0,4-2,2 k€; 18 mesi 1,1-4,7 k€** (lordi). Probabilità onesta: media che almeno una superi 1.000 €/anno, bassa che una da sola superi 3.000 €/anno. Come negli studi precedenti, nessuna è "grande": è la somma di pagine piccole con fonte ufficiale, che rafforza la rete e la lista email.

Massimiliano: per i test non serve nulla (0 €, 0 minuti). Per la costruzione: 10 minuti di Netlify/Search Console per sito, e le iscrizioni Awin (Holiday Extras) e Travelpayouts (Kiwitaxi, EKTA, Yesim, Compensair, AirHelp).

---

## Fonti principali (oltre ai file in `dl/`)
- Commissione UE, EES pienamente operativo 10/4/2026: home-affairs.ec.europa.eu/news/entryexit-system-will-become-fully-operational-10-april-2026-2026-03-30_en; pagina Smart Borders ("ETIAS is currently not in operation…").
- ETIAS senza data: navan.com/blog/when-does-etias-go-into-effect (obiettivo "ultimo trimestre 2026" tolto a luglio 2026).
- Code EES: euronews.com/2026/08/12/…ees-wait-times-double; flightqueue.com/ees-live.
- GOV.UK Content API (OGL v3): /api/content/eta ("An ETA costs £20"), /api/content/hand-luggage-restrictions, /api/content/foreign-travel-advice/<paese>, /api/search.json?filter_format=travel_advice.
- US State Dept RSS: travel.state.gov/_res/rss/TAsTWs.xml; Canada: data.international.gc.ca/travel-voyage/index-updated.json.
- CBP TTP: ttp.cbp.dhs.gov/schedulerapi/locations e /slots; packetlife.net (2019) su API senza autenticazione; johnnyjet.com (Appointment Scanner 29 $); Global Entry sospeso 22/2-11/3/2026 (airwaysmag, planetware).
- Affiliati: travelpayouts.com/en/offers/airhelp-affiliate-program (15-16,6 %, eCPC 0,01 $, 45 gg), …/compensair-affiliate-program (5-12 €, eCPC 0,04 $), …/kiwitaxi (9-11 %), …/ekta (20 %), …/yesim (18 %); airhelp.com/en-int/affiliate (15 %, media 70 €); Holiday Extras: revshare.so, flexoffers.com (1,6-12 %), ui.awin.com/merchant-profile/3496.
- Liquidi: pagine ufficiali LHR, LGW, FRA, DUB, HEL, MAN, STN (lette oggi); concorrenti tripprof.com, heygyro.com, travelsort.com, which.co.uk, expressandstar.com.
- Vignette: oesterreich.gv.at (prezzo 2026, solo digitale dal 2027); vintrica.com/en/affiliate.
