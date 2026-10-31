# Fronte nuovo: tempi d'attesa ufficiali nel mondo (31/10/2026)

Angolo assegnato: tempi d'attesa pubblicati dalle amministrazioni (passaporti, visti, appuntamenti, uffici pubblici), leggibili e aggiornabili in automatico.

**Prove, tutte del 31/10/2026:** `curl` dal nostro server (codice HTTP, dimensione, formato), Google Autocomplete (`suggestqueries.google.com`, `client=firefox`, Paese e lingua giusti; il numero dopo la domanda è quante varianti propone, massimo 10), ricerca web dagli USA per vedere chi c'è in prima pagina. Nessun blocco anti-robot aggirato: quando un sito risponde 403, 000 o con una pagina di verifica, lo scrivo e mi fermo.

**Cosa NON ho rifatto** (già chiuso in ESPLORATE, nessun fatto nuovo): tempi dei passaporti per Paese (23/10), appuntamenti per il visto Schengen e USA per città (21/10, 31/10 India e America Latina), USCIS e N-400, IRCC e INZ (siti chiusi), DMV ufficio per ufficio (USA 31/10), DVLA e Blue Badge (Regno Unito 31/10), cittadinanza e cerimonie (Australia, Germania, Francia), questure e CIE.

## In breve

- **Nessuna idea passa l'asticella dei siti nuovi** (voto ≥ 7 e ≥ 5.000 €/anno nel caso centrale).
- **La migliore è arrivata cambiando angolo**: dai tempi di passaporti e visti (dove l'ente risponde da solo o ci chiude la porta) ai **tempi dei sussidi pubblici negli USA, Stato per Stato**. Il governo federale pubblica ogni mese, per ogni Stato, quante domande di Medicaid vengono decise entro 24 ore, 7, 30, 45 giorni e oltre (dati dal 2018, pubblico dominio, aggiornati il 30/10/2026). La gente lo chiede ("how long does medicaid take to get approved in texas", 10 varianti con gli Stati) e in prima pagina oggi ci sono solo notizie, senza una tabella aggiornata. Voto 6: sotto l'asticella perché nessun sito della rete è adatto e la stima centrale è circa 1.900 €/anno. **RISERVA alta**, da unire alla "disoccupazione per Stato" del rapporto USA di oggi.
- **Una sezione da costruire a costo zero**: tempi ai controlli di frontiera all'arrivo negli USA, aeroporto per aeroporto e ora per ora, dai dati ufficiali della dogana americana (CBP). Il server risponde 200 e i dati arrivano fino al 29/10/2026. Va in Before You Fly. Voto 5,5, circa 750 €/anno nel caso centrale, 12-18 ore di lavoro. Ci sono già concorrenti che usano gli stessi dati.
- Le altre 10 idee sono NO o RISERVA bassa. Le code ai confini europei col nuovo sistema EES hanno molta domanda ("ees queues at malaga airport", "ees queue tracker"), ma **non esiste un dato ufficiale**: chi lo mostra lo stima da sé.

## Tabella delle idee

| # | Idea | Dove | Voto | €/anno a 18 mesi (prud. / centr. / ott.) | Ore | Esito |
|---|---|---|---|---|---|---|
| 1 | Tempi di Medicaid, SNAP e disoccupazione Stato per Stato ("quanto ci vuole per l'approvazione in Texas") | sito nuovo USA "tempi dei sussidi" (nessun sito della rete adatto) | 6 | 370 / 1.870 / 7.060 | 30-45 | **RISERVA alta**: da unire all'idea 1 di `wf-2026-10-31-usa-amministrazione.md` |
| 2 | Tempi ai controlli di frontiera all'arrivo negli USA, per aeroporto, terminal e ora (cittadini USA e stranieri a parte) | sezione di Before You Fly | 5,5 | 160 / 750 / 3.530 | 12-18 | **SEZIONE in coda** (costo zero, guadagno positivo) |
| 3 | Tempi della successione (probate): Dublino, Inghilterra e Galles, con lo storico | pagina singola; nessun sito adatto | 5 | 100 / 400 / 1.500 | 8-12 | RISERVA bassa |
| 4 | Tempo di registrazione di un marchio per Paese (USA, Regno Unito, UE, Canada, Australia, India) | sito nuovo | 4,5 | 150 / 600 / 2.500 | 20-30 | NO: fonti a metà chiuse, studi legali in prima pagina |
| 5 | Code al confine USA-Canada e USA-Messico ("best time to cross") | sezione di Before You Fly | 4 | – | – | NO: la CBP ha già lo storico e un assistente AI sul suo sito; la gente cerca il dato in diretta |
| 6 | Code al controllo passaporti in Europa col sistema EES | Before You Fly | 4 | – | – | NO: nessun dato ufficiale; flightqueue.com stima 125 aeroporti |
| 7 | Attesa per l'esame di guida per centro (Regno Unito, Irlanda) | sito nuovo | 4 | – | – | NO: nessun file ufficiale regolare nel Regno Unito, `rsa.ie` 403, passrates.uk già presente |
| 8 | Tempi dei permessi di soggiorno in Norvegia, Svezia, Finlandia, Paesi Bassi | riga in Visa Income | 4 | 30 / 120 / 400 | 4-6 | NO come sezione: ogni ente risponde già categoria per categoria |
| 9 | Tempi del Certificate of Eligibility in Giappone per tipo di visto | Visa Income | 4 | – | – | NO: japan-visa.com pubblica già la serie mensile dai dati ufficiali |
| 10 | Certificati di nascita e morte: tempi dell'ufficio di ogni Stato USA | sito nuovo | 4 | – | – | NO: 50 fonti, metà chiuse (CA 000, FL 403), VitalChek e intermediari |
| 11 | Tempi del Dipartimento del Lavoro per PERM e salari (H-1B, green card) | Visa Income | 3,5 | – | – | NO: una pagina nazionale, molti tracker ("perm processing time tracker") |
| 12 | Code ai controlli di sicurezza degli aeroporti europei (Dublino, Manchester, Heathrow, Schiphol) | Before You Fly | 3,5 | – | – | NO: dato in diretta del gestore, che risponde da solo; Schiphol, Copenaghen, Bruxelles 403 |

Ipotesi comuni per i calcoli (le stesse dei giri precedenti, **non ancora misurate**: AdSense non è attivo): pagine viste per visita 1,3-1,4; pubblicità per pubblico USA/UK in inglese 8-14 € ogni 1.000 pagine viste. Formula: visite al mese × pagine per visita × 12 × RPM / 1.000.

---

## 1. Tempi di Medicaid, SNAP e disoccupazione Stato per Stato (voto 6, RISERVA alta)

**Cosa sarebbe.** Una pagina per Stato (51) che risponde a "quanto ci vuole per avere Medicaid / i buoni pasto SNAP / il primo assegno di disoccupazione in [Stato]", con i numeri ufficiali più recenti, il confronto con gli altri Stati e l'andamento mese per mese. Più una classifica nazionale. Sono numeri che un assistente AI citerebbe volentieri: "A luglio 2026 il Texas ha deciso entro 24 ore il 12 % delle domande di Medicaid; il 31 % ha aspettato più di 45 giorni, che è il limite federale".

**Fonti verificate (31/10/2026).**

| Fonte | HTTP | Formato e aggiornamento | Licenza |
|---|---|---|---|
| CMS, "State Medicaid and CHIP Applications, Eligibility Determinations, and Enrollment Data" (`data.medicaid.gov`, id `6165f45b-…`) | 200 (API e CSV da 4,5 MB, `download.medicaid.gov/data/pi-dataset-october-2026-release.csv`) | mensile; aggiornato il 30/10/2026; dati da febbraio 2018 a luglio 2026 (67 mesi con il dato dei tempi); colonne "Processed in Less than 24 Hours", "24 Hours and 7 Days", "8 Days and 30 Days", "31 days and 45 days", "More than 45 Days" per ogni Stato | `usa.gov/government-works` (pubblico dominio) |
| USDA, "FY 2025 SNAP Application Processing Timeliness" (`fns.usda.gov/snap/qc/timeliness/apt-fy25`) | 200 | annuale, aggiornato il 28/8/2026; percentuale di domande decise in tempo per Stato (Wisconsin 97,22 %, Texas 80,42 %, Georgia 61,24 %, Alaska 64,26 %) | opera federale, pubblico dominio |
| Dipartimento del Lavoro, ETA 9050 (`oui.doleta.gov/unemploy/csv/ar9050.csv`) | 200 (5 MB) | mensile; già descritto nel rapporto USA di oggi (fino al 30/9/2026) | pubblico dominio |

Calcolo fatto oggi sul file di Medicaid (luglio 2026, dato preliminare; percentuale sul totale delle decisioni divise per tempo): Texas 12 % entro 24 ore, 31 % oltre 45 giorni; Georgia 28 % oltre 45; Illinois 25 %; Louisiana 25 %; Vermont 31 %; Montana 29 %; New York e Oklahoma 100 % entro 24 ore; Massachusetts 95 %; Connecticut 99 %. **Attenzione per chi costruisce:** per alcuni Stati il totale delle decisioni non coincide con la somma delle 5 fasce (Texas: 51.637 contro 27.532 + …): bisogna usare sempre la somma delle fasce e dirlo nella nota del metodo.

**Domanda (Google USA).** "how long does medicaid take to get approved in" 10 (Texas, Florida, Georgia, Illinois, Louisiana, Ohio, gravidanza); "medicaid processing time" 10; "how long does snap take to get approved in" 10 (Texas, Pennsylvania, Florida, New York, Tennessee, Virginia, Illinois, New Jersey); "how long does unemployment take to" 10 (New York, Connecticut, Washington). "medicaid approval time by state" 0: la gente chiede per il proprio Stato, non la classifica.

**Chi c'è oggi.** Per "how long does medicaid take to get approved in texas": notizie (click2houston 10/9/2026 "more than 200,000 Texans waiting", KERA e Texas Public Radio 12-13/5/2026 sulle donne incinte, ProPublica), un sito di assicurazioni (insuredandmore.com) e pagine spazzatura. Per i dati per Stato: solo articoli vecchi (Becker's "16 states with excessive processing times", Missouri Independent 2022-2024, Georgetown CCF 2018-2023). **Nessuno ha la tabella aggiornata mese per mese.** È battibile sulla precisione e sulla freschezza.

**Chi paga e quanto.** Solo pubblicità (pubblico USA). Non ho trovato un programma di affiliazione adatto e serio per chi aspetta Medicaid o SNAP. È un pubblico con poco reddito: la pubblicità sanitaria rende, ma meno di quanto farebbe pensare il tema. Ipotesi RPM 8-12 €.

**Stima a 18 mesi.** Visite al mese 3.000 / 12.000 / 35.000.
- Prudente: 3.000 × 1,3 × 12 × 8 / 1.000 = **374 €**
- Centrale: 12.000 × 1,3 × 12 × 10 / 1.000 = **1.872 €**
- Ottimista: 35.000 × 1,4 × 12 × 12 / 1.000 = **7.056 €**
Primi soldi: 4-6 mesi dopo la pubblicazione (serve AdSense attivo sul sito nuovo).

**Ore.** 30-45: tre lettori di dati (CSV Medicaid, pagina SNAP, CSV disoccupazione), 51 pagine Stato, classifiche, grafico mensile, aggiornamento automatico mensile (pubblica solo se il file CMS cambia: circa una volta al mese, 15 crediti).

**Voto 6.** Più 1 per la fonte (perfetta: mensile, per Stato, pubblico dominio, storico lungo), più 1 per la prima pagina senza tabella. Meno per il pubblico che vale poco, per l'assenza di affiliazioni e perché serve un sito nuovo (nessuno dei 10 è adatto: FloodCost e FHA condos sono casa e mutui). **RISERVA alta.** Proposta per il mercoledì: valutarla insieme all'idea 1 del rapporto USA di oggi (disoccupazione, voto 5,5) come un unico sito "tempi dei sussidi per Stato". Anche unite, la stima centrale resta sotto i 5.000 €/anno.

---

## 2. Tempi ai controlli di frontiera all'arrivo negli USA, per aeroporto e ora (voto 5,5, SEZIONE in coda)

**Cosa sarebbe.** Pagine per i 46 aeroporti americani con i controlli di frontiera, e per ogni terminal: quanto si aspetta in media al controllo passaporti, separando cittadini americani e stranieri (chi entra con ESTA o con il visto); l'ora peggiore e l'ora migliore; il massimo del mese; l'andamento mese per mese. Più un consiglio pratico: "quanto tempo serve per una coincidenza a JFK dopo un volo internazionale". È il pubblico di Before You Fly: chi vola verso gli USA dal Regno Unito e dall'Europa.

**Fonte verificata.** CBP Airport Wait Times (`awt.cbp.gov`): la pagina è un'applicazione JavaScript, ma i dati arrivano da due indirizzi pubblici del sito stesso.
- `GET awt.cbp.gov/api/waitTime` → 200 JSON: 66 terminal in 46 aeroporti (ATL, BOS, DFW, EWR, IAD, IAH, JFK, LAX, MIA, ORD, SEA, SFO…), date disponibili dal 3/5/2023 al **29/10/2026**.
- `POST awt.cbp.gov/api/waitTime` con `{"Id":"A171","FromDate":"2026-10-01","ToDate":"2026-10-07"}` → 200 JSON: una riga per terminal, giorno e ora, con attesa media e massima per cittadini USA e per stranieri, passeggeri, voli, posti di controllo aperti, passeggeri Global Entry.
- Licenza: opera del governo federale (CBP), pubblico dominio. Ritardo dei dati: circa 2-10 giorni.
- Nessun blocco: le stesse chiamate le fa il browser di chiunque apra il sito. Bastano circa 70 chiamate al mese (una per terminal).

Esempio calcolato oggi, **JFK, settembre 2026** (media pesata sui passeggeri):

| Terminal | Stranieri, attesa media | Cittadini USA | Massimo del mese | Ora peggiore per gli stranieri | Passeggeri |
|---|---|---|---|---|---|
| Terminal 1 | 47,3 min | 16,3 min | 222 min | 11-12 (61 min) | 304.036 |
| Terminal 4 | 32,8 min | 11,8 min | 203 min | 11-12 (51 min) | 590.135 |
| Terminal 8 | 35,1 min | 11,3 min | 180 min | 6-7 (51 min) | 267.240 |
| Terminal 7 | 26,9 min | 17,4 min | 140 min | 15-16 (33 min) | 59.909 |
| Terminal 5 | 20,1 min | 11,7 min | 165 min | 19-20 (25 min) | 154.821 |

**Domanda (Google USA e Regno Unito).** "jfk customs wait time" 10 (terminal 1, 4, 5, 7, 8, "today", "reddit"); "customs wait time" 10 (ATL, LAX, IAD, SFO, IAH, DFW, SeaTac, EWR); "how long does customs take at" 10 (JFK, LAX, DFW, Dulles, SeaTac, SFO, ORD, Logan); "immigration wait time at" 10; "newark customs wait" 10 (terminal B e C); "miami airport customs wait" 10. Dal Regno Unito: "customs wait time" 10 (JFK, Toronto, Montréal, Atlanta, LAX). Molte varianti chiedono il dato "today/live": quello non possiamo darlo (pagine statiche, crediti Netlify). Rispondiamo a "how long does it take" e "best time".

**Chi c'è oggi.** In prima pagina ci sono già siti che usano gli stessi dati CBP: flightqueue.com (pagine per aeroporto e per controllo passaporti), qsensor.co (pagine per terminal e articoli mensili, per esempio "JFK Customs: July 2026"), takeofftimer.com (pagine per codice aeroporto, media degli ultimi 90 giorni), upgradedpoints.com, un'app iOS "US Airports Wait Times". Poi comunicati di senatori e articoli vecchi (2013-2016). **Battibile solo in parte**: possiamo offrire la divisione cittadini/stranieri per terminal, lo storico mese per mese dal 2023 e il consiglio sulle coincidenze, ma il terreno è occupato.

**Chi paga.** Pubblicità di viaggio USA/UK (RPM 10-14 €, ipotesi) e i link affiliati che Before You Fly già usa (eSIM, trasferimenti dall'aeroporto, assicurazione viaggio). Nessuna spesa.

**Stima a 18 mesi.** Visite al mese 1.000 / 4.000 / 15.000.
- Prudente: 1.000 × 1,3 × 12 × 10 / 1.000 = **156 €**
- Centrale: 4.000 × 1,3 × 12 × 12 / 1.000 = **749 €**
- Ottimista: 15.000 × 1,4 × 12 × 14 / 1.000 = **3.528 €**
Primi soldi: appena Before You Fly ha AdSense attivo.

**Ore.** 12-18 (lettore dati, 46 pagine aeroporto, tabelle per terminal, aggiornamento mensile insieme alla pubblicazione già prevista del sito).

**Rischio.** L'indirizzo `/api/waitTime` non è un'API documentata: se la CBP cambia il sito, il lettore si rompe. Il controllo mensile deve fermare la pubblicazione se i dati non arrivano.

**Voto 5,5.** Fonte ottima e domanda forte, ma tre concorrenti con gli stessi dati e un pezzo grande della domanda chiede il dato in diretta. **SEZIONE in coda** secondo la regola della rete fitta (costo zero, guadagno positivo), dopo le sezioni di Before You Fly già in lista.

---

## 3. Tempi della successione (probate): Dublino, Inghilterra e Galles (voto 5, RISERVA bassa)

**Fonti.** Courts Service irlandese, "Probate processing times" (`courts.ie/guides/probate-processing-times`) → 200: aggiornata il 26/10/2026, mostra la data delle domande in lavorazione (domande tramite avvocato: 21/7/2026; domande personali: 3/9/2026; portale online: "3 to 4 weeks"). Vale solo per l'ufficio di Dublino; gli uffici di provincia non pubblicano. Inghilterra e Galles: solo il dato nazionale trimestrale del Ministero della Giustizia; il file mensile HMCTS "modernised services" (gov.uk, Excel, 8/10/2026) parla di uso dei servizi digitali, non di tempi.
**Domanda.** "probate waiting times" 10 nel Regno Unito e 10 in Irlanda ("dublin", "2026 gov uk", "nsw", "ireland").
**Chi c'è.** courts.ie stesso, globallawexperts.com, studi legali, notizie (Business Post "up to 24 weeks", Law Society Gazette 28/9/2026).
**Il nostro valore.** Solo lo storico: la pagina ufficiale mostra la data di oggi e cancella quella di ieri. Possiamo dire "in 6 mesi Dublino è passata da X a Y settimane".
**Chi paga.** Pubblicità UK/IE nel settore legale (ipotesi 10-12 €). Nessun sito della rete è adatto.
**Stima.** 600 / 2.500 / 8.000 visite al mese → 600 × 1,3 × 12 × 10 / 1.000 = 94 €; 2.500 × 1,3 × 12 × 11 / 1.000 = 429 €; 8.000 × 1,4 × 12 × 12 / 1.000 = 1.613 €. Circa **100 / 400 / 1.500 €**. Ore 8-12. **RISERVA bassa**: si riapre solo se nasce un sito per chi si occupa di un'eredità.

## 4. Tempo di registrazione di un marchio per Paese (voto 4,5, NO)

USPTO "Trademark processing wait times" 200: aggiornato al 1/10/2026, primo esame 4,3 mesi, registrazione 10,4 mesi. IP Australia 200. EUIPO 403. Le pagine dei tempi di CIPO (Canada) e UKIPO che ho provato rispondono 404. Domanda forte e pubblico che vale (piccole imprese): "how long does it take to register a trademark in" 10 (USA, India, Sudafrica, Regno Unito, Canada, Nigeria, Australia, Kenya). Ma ogni ufficio pubblica un solo numero nazionale e risponde da sé, e la prima pagina è degli studi legali e dei servizi di deposito. Fonti chiuse per metà. **NO.**

## 5. Code al confine USA-Canada e USA-Messico (voto 4, NO)

`bwt.cbp.gov/api/bwtnew` 200 (JSON in diretta, 85 valichi, aggiornato ogni ora) e il CSV canadese CBSA 200. Domanda enorme: "border wait times" 10, "san ysidro border wait time" 10, "peace arch border wait" 10. Però quasi tutte le ricerche chiedono "today/live/right now". Il JSON non permette la lettura da un'altra pagina web (nessuna intestazione CORS), quindi non possiamo mostrarlo in diretta senza ripubblicare il sito di continuo (impossibile con i crediti). E la CBP ha già sul suo sito lo storico per valico, mese e giorno (`/api/historicalwaittimes`, pagina "Historical Wait Times") e un assistente AI integrato. **NO.**

## 6. Code al controllo passaporti in Europa col sistema EES (voto 4, NO)

La domanda è nuova e forte dal Regno Unito: "ees queues" 10 (Malaga, Faro, Lisbona, Barcellona, Schiphol, "ees queue tracker"); "passport control wait time" 10 (Copenaghen, CDG, Lisbona, Francoforte, Amsterdam, Monaco); "dover queues" 10 e "eurostar queues" 10 (con "ees"). Ma **non esiste un dato ufficiale**: la Commissione non pubblica tempi; la polizia portoghese (PSP) dà i massimi solo nei comunicati stampa e solo per Lisbona, Porto e Faro. flightqueue.com stima 125 aeroporti con dati propri e segnalazioni dei viaggiatori, qsensor e Holiday Extras scrivono guide. Senza una fonte ufficiale il nostro metodo non regge. **NO.** Il tema EES resta utile come testo nelle pagine di Before You Fly che già ne parlano.

## 7. Attesa per l'esame di guida per centro (Regno Unito, Irlanda) (voto 4, NO)

Regno Unito: la DVSA pubblica solo il calendario delle uscite settimanali (gov.uk, aggiornato il 26/10/2026: si prenota fino all'11/4/2027) e il dato nazionale. I tempi per centro escono solo come allegati alle risposte in Parlamento, non come file regolare. passrates.uk fa già pagine per centro. Irlanda: la RSA pubblica la tabella per centro, ma `rsa.ie` risponde 403. **NO** (conferma il NO del 14/10 sui promossi per centro).

## 8. Tempi dei permessi di soggiorno nei Paesi nordici e nei Paesi Bassi (voto 4, NO come sezione)

UDI (Norvegia) 200, una pagina per categoria ("Waiting time": famiglia, lavoro, visti, cittadinanza); Migrationsverket (Svezia) 200 in home, ma la pagina dei tempi che ho provato è 404; Migri (Finlandia) 403; IND (Paesi Bassi) 404 all'indirizzo provato. Domanda c'è ("udi waiting time" 10, "migrationsverket waiting time" 9), ma ogni ente risponde da sé. Al massimo una riga di confronto in Visa Income (30 / 120 / 400 €/anno, 4-6 ore). **NO come sezione.**

## 9. Certificate of Eligibility in Giappone (voto 4, NO)

"coe processing time japan" 10 (2025, 2026, reddit). La pagina dei tempi sul sito dell'immigrazione giapponese non l'ho trovata dal server; japan-visa.com pubblica già la serie mensile per tipo di visto dai dati ufficiali (gennaio 2024 - marzo 2026). **NO.**

## 10. Certificati di nascita e morte, Stato per Stato (USA) (voto 4, NO)

"how long does it take to get a death certificate in" 10 Stati; "birth certificate processing time" 10. Texas DSHS 200 (ha una pagina "Processing Times"), California 000, Florida 403. 50 fonti diverse, metà chiuse, e la prima pagina è di VitalChek e di intermediari a pagamento. Stesso schema del DMV (NO il 31/10). **NO.**

## 11. PERM e salari per i visti di lavoro USA (voto 3,5, NO)

`flag.dol.gov/processingtimes` 200: date in lavorazione al 30/9/2026 (PERM: giugno 2026). Una sola pagina nazionale e un mercato di tracker già pieno ("perm processing time tracker", "calculator", "reddit" nell'autocomplete). **NO.**

## 12. Code ai controlli di sicurezza negli aeroporti europei (voto 3,5, NO)

"dublin airport security times" 10, "manchester airport security wait" 10, "heathrow security wait time" 10, "schiphol security wait" 10. È un dato in diretta del gestore, che lo mostra sul proprio sito. Schiphol, Copenaghen e Bruxelles rispondono 403. Non è un dato dell'amministrazione e non si può tenere in diretta su un sito statico. **NO.**

---

## Cosa cambia per la rete

1. **Lezione sull'angolo.** Sui tempi di passaporti, visti e permessi o l'ente risponde già da solo (una pagina per categoria), o ci chiude la porta (`travel.state.gov`, `canada.ca`, `rsa.ie`, `irishimmigration.ie` 403/000). Funzionano meglio i **tempi misurati e pubblicati come dati aperti, Stato per Stato o ufficio per ufficio, che nessuno ha ancora trasformato in pagine**. Oggi il caso è Medicaid: file mensile federale, 51 Stati, prima pagina fatta solo di notizie.
2. **Proposta per la coda di costruzione:** idea 2 (frontiera all'arrivo negli USA) come sezione di Before You Fly, dopo le sezioni già in lista. Nessuna spesa e nessun passaggio di Massimiliano.
3. **Proposta per il mercoledì:** decidere se unire Medicaid, SNAP e disoccupazione in un solo sito "tempi dei sussidi per Stato". Oggi la stima centrale è sotto l'asticella: va tenuto in "Idee in cantiere" come riserva, senza messaggio a Massimiliano.
4. Da aggiungere a ESPLORATE (non l'ho modificato, come richiesto): le righe delle idee 1-12 qui sopra.

## Fonti lette il 31/10/2026

| Fonte | HTTP |
|---|---|
| `awt.cbp.gov/api/waitTime` (GET e POST) | 200 JSON |
| `bwt.cbp.gov/api/bwtnew`, `bwt.cbp.gov/xml/bwt.xml` | 200 |
| `cbsa-asfc.gc.ca/bwt-taf/bwt-eng.csv` | 200 |
| `data.medicaid.gov` API e `download.medicaid.gov/data/pi-dataset-october-2026-release.csv` | 200 |
| `fns.usda.gov/snap/qc/timeliness/apt-fy25` | 200 |
| `oui.doleta.gov/unemploy/csv/ar9050.csv` | 200 |
| `courts.ie/guides/probate-processing-times` | 200 |
| `gov.uk` API: "Driving test appointments: release dates…", HMCTS management information August 2026 | 200 |
| `uspto.gov/trademarks/application-timeline` | 200 |
| `flag.dol.gov/processingtimes` | 200 |
| `udi.no/en/waiting-time/` | 200 |
| `dshs.texas.gov/vital-statistics` | 200 |
| `travel.state.gov` (tempi dei visti) | 403 |
| `rsa.ie`, `irishimmigration.ie`, `migri.fi`, `schiphol.nl`, `cph.dk`, `brusselsairport.be`, `euipo.europa.eu`, `floridahealth.gov`, `atf.gov`, `cbp.gov` | 403 |
| `cdph.ca.gov`, `data.gouv.fr` | 000 |
| `benefits.va.gov/reports/mmwr_va.asp` (rapporto settimanale VA) | 200 ma pagina "404 - Page Not Found" |
| `ind.nl`, pagina tempi di `migrationsverket.se`, `wipo.int` (tempi Madrid), CIPO, UKIPO (indirizzi provati) | 404 |
| Ricerca su DuckDuckGo | 202 (verifica anti-robot: mi sono fermato) |
