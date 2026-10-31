# Fronte nuovo: esami obbligatori nel mondo (31/10/2026)

**Angolo assegnato.** Esami obbligatori nel mondo con date, sedi o risultati ufficiali (il modello EsameB1 replicato): test di lingua per cittadinanza e residenza, esami professionali, patenti per stranieri. Per ognuno la domanda chiave: le date e le sedi si leggono in automatico, città per città? (lezione del test tedesco fallito il 30/10: 31 sedi leggibili su 85).

**Letto prima:** skill `rete-siti` (metodo, voto severo, asticella: siti nuovi solo con voto ≥ 7 e ≥ 5.000 €/anno centrali; sezioni se costano zero e il guadagno atteso è positivo), `REGOLE-FISSE.md` (regole del 31/10: fronti nuovi, conta il fatturato, niente lavori a ore di Massimiliano) e `ESPLORATE.md`.

**Cosa era già chiuso e non ho rivalutato da capo:** Life in the UK, test australiano, Einbürgerungstest/DTZ (test fallito), examen civique e TCF (scesi a 4,5 oggi nel giro Francia-Belgio), CCSE/DELE A2 come riserva, inburgering olandese (scarto, studio 4), Danimarca (autocomplete vuota), Norvegia, Finlandia, Svezia (riserva con innesco), Austria ÖIF/ÖSD (riserva per licenza), Polonia, Portogallo, Cechia, KIIP, TOPIK, Goethe, SELT (costruito), N-400, NCLEX per scuola e per Paese, ABA 509 per facoltà, agenti immobiliari, notai, PLAB/AMC (oggi, fonti chiuse), patente in Giappone e negli Emirati, conversione della patente Paese × Paese, esami di guida per centro (UK, IE, AU, ES, BE, FR).

**Come ho cambiato angolo.** Visto che i test di cittadinanza sono quasi tutti chiusi, ho spostato la ricerca su tre famiglie nuove: (1) esami professionali USA e Regno Unito con domanda forte e pubblico ricco (bar exam, MPRE/UBE, CPA, Praxis, SQE); (2) esami di lingua "internazionali" con calendario unico mondiale (DELE/CCSE, HSK); (3) patenti per stranieri viste dal lato "posso fare l'esame in inglese?". In più ho ricontrollato due riserve con un fatto nuovo possibile (Svezia, Paesi Bassi) e un Paese mai guardato (Grecia, esame PEGP).

**Metodo e prove (tutte del 31/10/2026).** `curl` dal nostro server con agente da browser (stato HTTP, dimensione, formato, data di aggiornamento letta nella pagina, condizioni d'uso); PDF letti con `pdftotext`; suggerimenti di Google (`suggestqueries.google.com`, `client=firefox`) con lingua e Paese giusti (en/us, en/gb, sv/se, nl/nl, nl/be, da/dk, el/gr, en/gr, fr/lu, en/lu, en/in, en/ie): il numero dopo la ricerca è quante varianti propone Google (massimo 10); ricerche web per vedere chi c'è oggi in prima pagina. Dove una fonte risponde 403, 000 o con una pagina anti-robot l'ho scritto e mi sono fermato: nessun blocco aggirato. Nessun dato personale raccolto (gli elenchi dei promossi con i nomi, che alcuni Stati pubblicano, NON si usano).

**Ipotesi comuni per i calcoli** (le stesse dei giri precedenti, non ancora misurate): pagine viste per visita 1,3-1,5; pubblicità per pubblico USA/UK in inglese 6-15 € ogni 1.000 pagine viste (istruzione e diritto nella parte alta); pubblico europeo in inglese 6-10 €; pubblico greco, indiano, pakistano, nigeriano 1-3 €. italki paga 18 $ a nuovo studente (verificato su Awin il 28/10, scritto nel cruscotto). Le visite sono stime a 18 mesi, non dati.

---

## 1. Risultato in breve

**Nessuna idea passa l'asticella dei siti nuovi** (voto ≥ 7 e ≥ 5.000 €/anno centrali). La migliore arriva a 5. Una sola è una sezione a costo zero con guadagno atteso positivo (patente: posso fare l'esame in inglese?). Il fronte "esami obbligatori nel mondo" si può considerare **esaurito per il modello EsameB1**: dove la domanda è per città, l'ente ha il proprio motore o un blocco anti-robot; dove i dati sono aperti e leggibili (NCBE, Cervantes, Diavgeia), il dato è nazionale e la fonte ufficiale è già prima su Google.

| # | Idea | Forma | Voto | Stima €/anno a 18 mesi (prudente / centrale / ottimista) | Ore | Esito |
|---|---|---|---|---|---|---|
| 1 | Bar exam USA per Stato: date di uscita dei risultati, promossi, punteggio minimo, passaggio al NextGen, MPRE | sito nuovo (EN) | 5 | 100 / 500 / 3.000 | 25-35 | NO come sito: NCBE ha già la tabella ufficiale e ne vieta la copia; 5 siti già in campo |
| 2 | Patente all'estero: posso fare l'esame (teoria e pratica) in inglese? Paese per Paese | sezione di Before You Fly ("Before you drive") | 5 | 30 / 150 / 550 | 12-18 | **SEZIONE in coda bassa** (costo zero, guadagno positivo, domanda che gli assistenti AI ricevono) |
| 3 | Praxis: punteggio minimo per Stato e per test | sito nuovo o blocco dell'idea 1 | 4,5 | 60 / 350 / 1.500 | 20-30 | NO: 240tutoring, achievable, teachercertification.com già con la tabella |
| 4 | DELE e CCSE 2027: date, scadenze, centri | pagina | 4,5 | 20 / 120 / 500 | 6-10 | RISERVA con innesco: calendario 2027 leggibile, centri no (sito esami Cervantes in rifacimento) |
| 5 | CPA exam: date di uscita dei punteggi e promossi per sezione | blocco dell'idea 1 | 4 | 50 / 250 / 1.200 | 10-15 | NO: Becker, UWorld, Gleim, Surgent e altri già primi |
| 6 | HSK (cinese): date 2027 e centri per città | sito nuovo (EN) | 4 | 30 / 200 / 800 | 15-20 | NO: centri dietro JavaScript, pubblico a pubblicità bassa |
| 7 | Grecia: esame PEGP per la cittadinanza (date, 70 centri, risultati) | pagina o sito in greco | 4 | 20 / 100 / 400 | 12-18 | NO: fonte aperta (Diavgeia), ma domanda senza città e pubblicità greca bassa |
| 8 | Svezia: medborgarskapsprovet (riserva del 20/10, riletta) | – | 3,5 | 0 / 50 / 200 | – | NO confermato: fatto nuovo (primo esame il 15/8, 875 candidati), ma nessuna data né sede pubblicata |
| 9 | Regno Unito: SQE (esame per solicitor) date e promossi | – | 3 | – | – | NO dal server: `sqe.sra.org.uk` anti-robot Incapsula |
| 10 | Paesi Bassi: inburgeringsexamen e Staatsexamen NT2 (riletta) | – | 3 | – | – | NO confermato: prenotazione centrale DUO, nessuna città in autocomplete, `inburgeren.nl` 000 |

---

## 2. Le idee una per una

### Idea 1. Bar exam USA per Stato (voto 5, NO come sito nuovo)

**L'idea in una riga.** Un sito in inglese con una pagina per ognuna delle 56 giurisdizioni USA: quando escono i risultati del bar exam di febbraio e di luglio (con lo storico delle date), percentuale di promossi (totale, prima volta, ripetenti) negli ultimi anni, punteggio minimo, quando lo Stato passa al nuovo esame NextGen, punteggio minimo dell'MPRE e regole per trasferire il punteggio UBE.

**Fonte ufficiale (verificata con curl).**
- NCBE, "Bar Exam Pass Rates by Jurisdiction", `ncbex.org/statistics-research/bar-exam-results-jurisdiction` → **200**, HTML, 98.650 byte, tabella in chiaro: "July 2026 Bar Exam Table last updated October 30, 2026, 4:50 p.m. (CDT)". Campi per giurisdizione: promossi totali, prima volta, ripetenti, numero di candidati, punteggio minimo, tipo di esame, **data di uscita dei risultati**. Esempi letti: New York 67 % / 76 % / 25 %, 9.936 candidati, 266, uscita 23/10; Texas 70 % / 79 % / 23 %, 3.230, 270, uscita 6/10; Alabama 52 % / 77 % / 13 %, 548, 260, uscita 25/9. Con i link ai comunicati ufficiali degli Stati (PDF di Hawaii, Iowa, Mississippi, New York, Ohio, Rhode Island, Tennessee, Vermont, West Virginia, Maryland…).
- NCBE, "NextGen UBE Adoption by Jurisdiction" → **200**, aggiornata il 23/10/2026: primo esame NextGen per Stato (Connecticut e Idaho luglio 2026, Arizona luglio 2027, Delaware e DC febbraio 2028, California e Florida luglio 2028…), punteggi minimi (616-620 o "TBA").
- NCBE, "UBE Minimum Scores" → **200**: 260 (Alabama, Iowa dal luglio 2026, Minnesota, Missouri, New Mexico, North Dakota, Oklahoma, Utah), 264 Indiana, 266 (Connecticut, DC, Illinois, New York…), 268 Michigan, 270 (Texas, Arizona, Colorado, Pennsylvania…).
- Fonte primaria di uno Stato: comunicato di New York `nybarexam.org/Press/20261023 FinalPressRelease_ExamResults.pdf` → **200**, PDF 374.565 byte, testo leggibile ("grading has been completed for the July 2026… overall passing rate of 67 %"). Ohio `supremecourt.ohio.gov/.../20260728.pdf` → 200.
- **Licenza.** Condizioni d'uso NCBE (`ncbex.org/website-terms-use`, 200): "You may not sell or modify the Content or reproduce, display, distribute… or create derivative works from any Content on the Site". La tabella NCBE quindi **non si copia**: si potrebbero usare solo i comunicati dei singoli Stati (atti di tribunali, numeri di fatto), una cinquantina di fonti diverse, PDF in formati diversi. Attenzione: diversi Stati pubblicano l'elenco dei promossi con i nomi (Maine, New Hampshire, Tennessee): dati personali, da non usare.

**Domanda (en/us).** "bar exam results" **10** (by state, release dates, new york, texas, california, by jurisdiction); "bar exam results release date" **10** (2026, illinois, texas, massachusetts, indiana, ny, georgia); "july 2026 bar exam results" **10** (date, by state, texas, ny, massachusetts, indiana, nc, florida); "february 2027 bar exam" **10** (date, registration, deadline, california, texas, ny, florida); "bar exam pass rates" **10** (by state, 2026, july 2026, by school, california); "ube minimum score by state" **10**; "mpre passing score by state" **10**; "nextgen bar exam states" **9**; "mpre results release date" **10**. Domanda vera, a ondate (fine settembre-ottobre e aprile-maggio). Pubblico: circa 67.000 candidati l'anno (dato NCBE 2025 riportato nei risultati di ricerca: 67.442 candidati, 63 % promossi).

**Chi c'è oggi su Google.** NCBE stessa (tabella e mappa ufficiali, aggiornate in giornata), casefleet.com (mappa per Stato), casecub.com (guida per Stato, dati del 2024), getoncourse.ai (promossi e NextGen per giurisdizione), UWorld/Themis (pagina statistiche), ABA Journal e Daily Journal per le notizie, JD Advising, Reddit. **Battibile solo sulla coda lunga** (storico per Stato, "quando escono i risultati di febbraio 2027 in Texas"), non sulle ricerche principali, dove NCBE e le commissioni statali vincono.

**Chi paga e quanto.** AdSense USA (istruzione/diritto: 8-15 € ogni 1.000 pagine viste, ipotesi). Corsi di preparazione (Barbri, Themis/UWorld, Kaplan, Quimbee da circa 1.199 $, BarMax, AdaptiBar, JD Advising): **nessuna commissione letta**. Pagine provate: `quimbee.com/affiliates` 404, `barmax.com/affiliates` 404, `jdadvising.com/affiliate-program/` 404, `adaptibar.com/affiliates` 200 ma solo JavaScript, nessuna cifra.

**Stima a 18 mesi.**
- Prudente: 8.000 visite × 1,3 pagine × 10 € / 1.000 = **~100 €**.
- Centrale: 30.000 visite × 1,4 × 12 € / 1.000 = 504 € → **~500 €**.
- Ottimista: 90.000 visite × 1,5 × 15 € / 1.000 = 2.025 € + un'affiliazione di corsi trovata dopo (~1.000 €) → **~3.000 €**.
- Primi soldi: non prima dei risultati di febbraio 2027 (aprile-maggio 2027), più probabilmente con l'ondata di settembre-ottobre 2027.

**Ore.** 25-35 (56 giurisdizioni, ~50 fonti statali in PDF diversi, storico, pagine NextGen).

**Voto 5** = domanda forte e a ondate (+), pubblico USA (+), ma il dato è già pubblicato in tabella dalla fonte ufficiale che vieta la copia (−), 5 concorrenti in prima pagina (−), nessuna affiliazione letta (−), raccolta da ~50 fonti (−). Sotto l'asticella dei siti nuovi; nessun sito esistente della rete ha questo pubblico, quindi niente sezione.

### Idea 2. Patente all'estero: posso fare l'esame in inglese? (voto 5, SEZIONE in coda bassa)

**L'idea in una riga.** Nel blocco "Before you drive" di Before You Fly, una tabella e una pagina per Paese (25-30 Paesi europei, più Giappone, Corea, Emirati, USA per Stato in un secondo tempo): in quali lingue si può fare l'esame di teoria, se l'esame pratico si può fare in inglese o con un interprete, il costo dell'esame in lingua straniera, con il link alla norma o all'ente ufficiale. Completa la conversione della patente (riserva 6,5 del 30/10) dal lato di chi non può convertire e deve rifare l'esame.

**Fonte ufficiale (verificata con curl), Paese per Paese.**
- Germania: Fahrerlaubnis-Verordnung, allegato 7, `gesetze-im-internet.de/fev_2010/anlage_7.html` → **200**, HTML, testo di legge libero. Testo letto: la prova teorica "kann auch in folgenden Fremdsprachen abgelegt werden: a) Englisch, b) Französisch, c) Griechisch, d) Italienisch, e) Polnisch, f) Portugiesisch, g) Rumänisch, h) Russisch, i) Kroatisch, j) Spanisch, k) Türkisch, l) Hocharabisch, m) Kurmandschi oder n) Ukrainisch". **14 lingue.**
- Spagna: DGT, `sede.dgt.gob.es/.../permiso-conducir/` → 200 ma pagina corta (5.619 byte): la lista delle lingue va cercata nelle pagine d'esame.
- Paesi Bassi: `cbr.nl` → **000** (connessione chiusa): fonte non leggibile dal server.
- Norvegia: percorso provato su `vegvesen.no` → 404 (sito raggiungibile, pagina da trovare). Giappone (polizia di Tokyo): percorso provato 404.
- Regno Unito e Irlanda: lingue dell'esame note dalle pagine ufficiali (DVSA inglese e gallese; RSA con voce in 22 lingue, da `theorytest.ie`), da rileggere in costruzione.
- Ogni Paese ha la sua fonte, quasi sempre in prosa: aggiornamento manuale ogni 3-6 mesi (le regole cambiano di rado; la Germania ha aggiunto l'ucraino e il kurmandschi).

**Domanda.** en/us "can i take driving test in english in" **10** (Germany, Japan, Italy, Belgium, Spain, Switzerland, France…); "driving theory test in english" **10** (Belgium, Germany, Spain, Poland, Norway, Portugal, Denmark, Romania); "theory test languages" **10** (UK, Ireland, RTA Dubai, NZTA, DVSA); "driving test in english japan" **10**; "theory exam in english netherlands" **2**. È esattamente il tipo di domanda che la gente fa agli assistenti AI, con una risposta ufficiale precisa ("14 lingue, tra cui l'inglese").

**Chi c'è oggi su Google.** autoviatest.com (pagine "expat license" per Paese e perfino un file `llms-expat.txt` per gli assistenti AI; vende test di pratica; per la Germania scrive "13 lingue", la norma ne elenca 14), passmefast.co.uk (ricerca sui test europei), The Local (articoli per Paese), nutheorie.nl, practicatest.com, teoricentralen.se. Battibile con le fonti ufficiali citate e aggiornate, non con il volume.

**Chi paga e quanto.** Solo AdSense (pubblico di espatriati in Europa in inglese, 6-10 € ogni 1.000 pagine viste, ipotesi). DiscoverCars (~20 $ a prenotazione, cookie 365 giorni, letto oggi su `discovercars.com/affiliate`) è per chi noleggia, non per chi prende la patente: non conta. Nessun programma di scuole guida o app di quiz con commissione letta.

**Stima a 18 mesi (come sezione).**
- Prudente: 4.000 visite × 1,3 × 6 € / 1.000 = 31 € → **~30 €**.
- Centrale: 12.000 visite × 1,4 × 8 € / 1.000 = 134 € → **~150 €** (con qualche citazione dagli assistenti AI).
- Ottimista: 35.000 visite × 1,5 × 10 € / 1.000 = 525 € → **~550 €**.
- Primi soldi: dopo l'indicizzazione della sezione (2-3 mesi), pochi euro al mese.

**Ore.** 12-18 (25-30 Paesi, una fonte ufficiale per ognuno, pagine dal motore esistente di Before You Fly).

**Voto 5** come sezione = domanda vera in molti Paesi (+), risposta ufficiale precisa che gli assistenti AI citano (+), costo zero e motore già pronto (+), ma solo pubblicità, un concorrente specializzato già in campo (autoviatest) e fonti sparse in prosa (−). Passa la regola della "rete fitta" (costo zero, guadagno positivo): **coda bassa** di Before You Fly, insieme agli altri pezzi di "Before you drive", con una sola pubblicazione.

### Idea 3. Praxis: punteggio minimo per Stato e per test (voto 4,5, NO)

**Fonte.** ETS, `praxis.ets.org/state-requirements.html` → **200** (227 KB): elenco degli Stati; la pagina di ogni Stato (`/state-requirements/newjersey-tests.html` → 200) carica i dati da un servizio JSON `.../Search-GetRequiredTests?nationalCode=NJ` → **200**, 1.485 byte, con `qualifyingScore` per test (letto: Speech-Language Pathology 5331 → 162). Il parametro che restituisce tutti i test del Dipartimento dell'Istruzione non l'ho trovato in 4 prove (agencyId, agency, stateAgency…): da capire in costruzione, senza aggirare nulla.

**Domanda (en/us).** "praxis passing scores" **10** (nj, slp, pa, by state, virginia, louisiana, indiana, arkansas); "praxis passing scores by state" **10** (sc, 5165, 5081, 5581, 5038, 5412); "praxis 5165 passing score" **10** (by state, nj, virginia, maryland, indiana, colorado); "praxis core passing score" **10** (nj, sc, nc, ct, utah, mississippi). Coda lunga vera: ~100 test × ~45 Stati.

**Chi c'è.** ETS (strumento ufficiale per Stato, e vende la preparazione con il 25 % di sconto), 240tutoring.com (tabella per test con le eccezioni per Stato: "5165 | 159, Arkansas 143, Missouri 145, Wyoming 160, DE/KY/MS/UT 152"), achievable.me (3 pagine), teachercertification.com, open-exam-prep.com, documenti dei Dipartimenti statali (Virginia). Mercato già presidiato da chi vende la preparazione.

**Chi paga.** AdSense istruzione USA; affiliazioni non lette (`240tutoring.com/affiliate-program/` 404, `mometrix.com/affiliates/` 404, `study.com/pages/Affiliate_Program.html` 403).

**Stima.** Prudente 5.000 visite × 1,3 × 9 € = 59 → **~60 €**; centrale 25.000 × 1,4 × 10 € = 350 → **~350 €**; ottimista 90.000 × 1,5 × 11 € = 1.485 → **~1.500 €**. **Ore** 20-30. **Voto 4,5**: domanda in coda lunga ma tabella già fatta da 3-4 siti di preparazione, fonte da decifrare, nessuna affiliazione letta.

### Idea 4. DELE e CCSE 2027: date, scadenze e centri (voto 4,5, RISERVA con innesco)

**Fatto nuovo.** Il sito esami dell'Instituto Cervantes è in rifacimento: `examenes.cervantes.es/es/dele/fechas` (e `/donde`, `/centros`, `/en/dele/when`) → 200 ma tutti reindirizzati a `cervantes.org/es/examenes/dele` (177 KB), titolo "Información para las convocatorias DELE y CCSE 2027", testo: "Estamos preparando una nueva web de exámenes… aquí tienes la información esencial". La pagina contiene in HTML tutto il calendario 2027:
- DELE: iscrizioni dal **18/11/2026**; 8 sessioni (5/3, 2/4, 21-22/5, 9/7, 10/9, 15/10, 12-13/11/2027) con chiusura delle iscrizioni e livelli per sessione;
- CCSE (esame per la nazionalità spagnola): iscrizioni dal **23/11/2026**; 10 sessioni (28/1, 25/2, 18/3, 29/4, 27/5, 24/6, 29/7, 30/9, 28/10, 25/11/2027) con chiusura iscrizioni e finestre di appuntamento.
- **Centri: non leggibili.** La ricerca dei centri è sparita con il vecchio sito; il negozio `tienda.cervantes.org` (200, 77 KB) è un'applicazione Salesforce in JavaScript. Stessa trappola del test tedesco: senza i centri per città non c'è il modello EsameB1.

**Domanda.** en/us "dele exam dates 2027" **10** (india, uk, b2, c1, a2); "dele exam centers" **10** (usa, near me, mumbai, india, california, texas, locations canada, locations usa). Il CCSE si cerca in spagnolo (riserva del 14/10: lingua).

**Chi c'è.** Instituto Cervantes (prima), le sedi Cervantes nazionali (New York, Chicago, Albuquerque, Londra, Nuova Delhi), università e accademie.

**Chi paga.** italki 18 $ a nuovo studente (Awin, 28/10); AdSense.

**Stima (una pagina, in Visa Income Checker per chi chiede la nazionalità spagnola, in inglese).** Prudente 1.500 visite × 1,3 × 8 € = 16 € + 0 studenti → **~20 €**; centrale 5.000 × 1,4 × 8 € = 56 € + 3 studenti italki × 18 $ ≈ 50 € → **~120 €**; ottimista 15.000 × 1,5 × 10 € = 225 € + 15 studenti ≈ 250 € → **~500 €**. **Ore** 6-10.

**Voto 4,5.** Calendario unico e leggibile (+), ma senza centri è una pagina di date che la fonte ufficiale ha già in prima posizione. **Innesco per riaprire:** quando il nuovo sito esami del Cervantes pubblica l'elenco dei centri in una pagina o un file leggibile, si rifà il conto per città (USA e Regno Unito). Controllo consigliato a fine gennaio 2027.

### Idea 5. CPA exam: date di uscita dei punteggi e promossi per sezione (voto 4, NO)

**Fonte.** NASBA `nasba.org/exams/cpaexam/` → 200 (180 KB) e `/exams/cpaexam/scores/` → 200: spiega le "target score release dates" pubblicate dall'AICPA; la pagina AICPA sui promossi provata (`aicpa-cima.com/resources/article/learn-more-about-cpa-exam-pass-rates`) → 404.

**Domanda (en/us).** "cpa exam score release dates" **10** (2026, 2027, reddit, schedule); "cpa exam pass rates" **10** (2026, by section, q2 2026, by year, historical); "cpa exam pass rates by state" **2** (debole); "cpa score release" **10**.

**Chi c'è.** AICPA e NASBA, Becker, UWorld Roger CPA, Gleim, Surgent, Ultimate CPA, crushendo, Another71 e Reddit: il mercato più presidiato di tutto il giro.

**Chi paga.** Surgent ha un programma di affiliazione (`surgent.com/affiliate-program/` 200) ma senza cifra leggibile; AdSense finanza/istruzione.

**Stima (come blocco dell'idea 1).** 50 / 250 / 1.200 € (5.000 / 20.000 / 70.000 visite × 1,3-1,5 × 8-12 €). **Ore** 10-15. **Voto 4**: domanda forte ma pochi numeri (4 sezioni, un calendario) e concorrenti con budget grandi.

### Idea 6. HSK (cinese): date 2027 e centri per città (voto 4, NO)

**Fonte.** `chinesetest.cn` → **200** (625 KB, applicazione Nuxt): mostra "2027 Test Calendar", "169 countries, 1522 test centers, 30,000+ test venues, 800,000 test takers". La ricerca dei centri ("Find a Test Center") è in JavaScript; l'interfaccia dati non è nel codice della pagina. Centri per città **non leggibili** senza studiare il servizio interno.

**Domanda.** en/us "hsk test dates 2027" **10** (in india, in pakistan, hsk 3/4/5); "hsk test center" **10** (usa, pakistan, jakarta, india, bangkok, indonesia, philippines, nigeria); en/gb "hsk exam london" **10**; en/in "hsk exam centre in india" **2**. Domanda soprattutto da Paesi con pubblicità bassa.

**Chi paga.** italki 18 $ a studente; AdSense 1-3 € (Asia del Sud, Africa) e 6-10 € (USA/UK).

**Stima.** Prudente 5.000 visite × 1,3 × 3 € = 20 € + 1 studente → **~30 €**; centrale 20.000 × 1,4 × 4 € = 112 € + 5 studenti ≈ 85 € → **~200 €**; ottimista 60.000 × 1,5 × 5 € = 450 € + 20 studenti ≈ 330 € → **~800 €**. **Ore** 15-20. **Voto 4**: stesso destino del TOPIK (NO del 17/10): pubblico povero, centri non leggibili.

### Idea 7. Grecia: esame PEGP per la cittadinanza (voto 4, NO)

**Fonte (verificata).** Il Ministero dell'Interno (`ypes.gr`) → **403**; `pegp.gr` e `ithageneia.ypes.gr` → **000**. Ma le decisioni ufficiali stanno su **Diavgeia**, il portale della trasparenza con interfaccia aperta: `diavgeia.gov.gr/opendata/decisions/ΡΔΜ846ΜΤΛ6-9ΣΓ.json` → **200** (JSON), decisione sui centri d'esame della sessione del **26/4/2026**. La circolare del Ministero dell'Istruzione del 3/3/2026 (PDF 200, letta) conferma: **70 centri d'esame** e **9 centri speciali** (6 in Attica, 2 a Salonicco, 1 a Heraklion); esame di greco livello B1 più geografia, storia, cultura e istituzioni. Le sedi si leggerebbero in automatico da un documento unico per sessione (la lezione tedesca è rispettata).

**Domanda.** el/gr "πεγπ" **10** (εξετασεις 2026, τραπεζα θεματων, αιτηση, θεματα, ιθαγενεια); "εξετάσεις πολιτογράφησης" **4**; "πεγπ αποτελεσματα" **4**; **"πεγπ εξεταστικα κεντρα" 1** (nessuna città); en/gr "greek citizenship exam" **10** (2026 results, practice, pdf, questions). Si cercano domande e risultati, non le sedi.

**Chi paga.** AdSense greco 1-3 € (pubblico di immigrati in Grecia); in inglese poco.

**Stima.** Prudente 3.000 visite × 1,3 × 2 € = 8 → **~20 €** con l'inglese; centrale 12.000 × 1,4 × 2,5 € = 42 € + pagine in inglese ~50 € → **~100 €**; ottimista 40.000 × 1,5 × 3 € = 180 € + 200 € in inglese → **~400 €**. **Ore** 12-18. **Voto 4**: fonte aperta e documento unico (+), ma la domanda non è per città e il pubblico paga poco.

### Idea 8. Svezia: medborgarskapsprovet, riletta (voto 3,5, NO confermato)

**Fatto nuovo (UHR, notizia del 22/10/2026, pagina 200):** il primo esame di educazione civica si è tenuto il **15/8/2026** con **875 candidati**; circa l'**80 %** promossi; soglia **28 punti su 40**. La pagina `uhr.se/medborgarskapsprovet/` (200) dice: "Information om nästa provtillfälle i samhällskunskap kommer" e "Anmälan… är stängd". Nessuna data, nessuna sede, prova di svedese "vid senare tillfälle".

**Domanda.** sv/se "medborgarskapsprovet" **10** (frågor, test, resultat, exempelfrågor, uhr, svt, alla frågor); "medborgarskapsprov datum" **1**.

**Verdetto.** La regola di riapertura del 20/10 ("se UHR pubblica date e sedi per città") **non è scattata**. Pubblico piccolo (875 candidati alla prima sessione). Stima 0 / 50 / 200 €. Si ricontrolla quando UHR annuncia la seconda sessione.

### Idea 9. Regno Unito: SQE, esame per diventare solicitor (voto 3, NO dal server)

**Domanda (en/gb).** "sqe results" **10** (results day 2026, dates, july 2026, today); "sqe dates 2027" **10** (sqe 1, sqe 2, january, july); "sqe2 pass rate" **10** (2026, april 2026, bpp, ulaw); "sqe1 pass rate" **6**. Pubblico britannico con pubblicità alta.

**Fonte.** `sqe.sra.org.uk/about-sqe/sqe-pass-rates` e `/exam-arrangements/assessment-dates` → 200 ma pagina di 212 byte con lo script **Incapsula** (anti-robot): non si aggira. `sra.org.uk/become-solicitor/sqe/` → 200 senza date né statistiche. **NO** finché la fonte non è leggibile.

### Idea 10. Paesi Bassi: inburgeringsexamen e Staatsexamen NT2, riletta (voto 3, NO confermato)

**Domanda.** nl/nl "inburgeringsexamen" **10** (oefenen, b1, a2, buitenland, vragen, engels, duo, aanvragen); "staatsexamen nt2" **10** (aanmelden, programma ii, rooster, uitslag); en/nl "inburgering exam" **10** (practice, results, schedule). Nessuna città: si cercano esercizi e risultati.

**Fonte.** `inburgeren.nl/examen-doen/` → **000** oggi (era 200 il 9/10); `duo.nl/particulier/inburgeren/` → 200. Prenotazione centrale DUO in poche sedi: niente modello per città. Verdetto dello studio 4 confermato.

---

## 3. Lezioni del giro

1. **Il modello EsameB1 nel mondo è esaurito sui test di cittadinanza.** Dopo i giri del 17, 20, 24, 30 e 31/10 restano solo esami dove (a) l'ente assegna la data (USA, Canada, Australia, Austria, Svezia), (b) la prenotazione è centrale (Regno Unito, Paesi Bassi, Finlandia, Spagna CCSE), (c) le sedi sono dietro JavaScript o anti-robot (Germania, Francia, Cervantes oggi, HSK, SQE), oppure (d) le sedi sono leggibili ma nessuno le cerca per città (Grecia, Danimarca).
2. **Gli esami professionali USA hanno la domanda e il pubblico ricco, ma il dato è già pubblicato bene da chi lo produce** (NCBE con tabella aggiornata in giornata, ETS con lo strumento per Stato, AICPA/NASBA) e la prima pagina è occupata da chi vende la preparazione. Le loro affiliazioni non mostrano cifre leggibili.
3. **Dove la domanda è una risposta precisa che gli assistenti AI ricevono** ("posso fare l'esame di guida in inglese in Germania?") c'è ancora spazio per una sezione piccola con la fonte di legge citata: è l'unico pezzo del giro che si costruisce.
4. **Vincolo da allentare per arrivare a 7+ su questo fronte:** i permessi scritti degli enti con licenza chiusa (ÖIF/ÖSD in Austria, CCIP e FEI in Francia, già proposti nei giri precedenti) restano l'unica strada per un sito nuovo d'esame con sedi per città; un'email a un ente è un contatto diretto e va deciso da Massimiliano. Oggi non c'è un caso nuovo che lo giustifichi.
5. **Angolo per il prossimo giro (non verificato oggi, solo indicazione):** sugli esami i soldi non stanno nelle date ma nella preparazione. Il passo naturale è guardare i prodotti propri (libri KDP, come la collana B1 già in lista) per esami con banca ufficiale delle domande pubblica e licenza aperta, in lingue dove Amazon è poco presidiato. Va verificato con i numeri di Amazon e le licenze, esame per esame.

---

## 4. Righe proposte per `ESPLORATE.md` (da copiare a cura di chi aggiorna l'elenco; questo file non lo modifica)

| Nicchia | Esito | Studio |
|---|---|---|
| Bar exam USA per Stato: date di uscita dei risultati, promossi, punteggio minimo, NextGen, MPRE, UBE (NCBE 200, tabella aggiornata il 30/10/2026; "bar exam results" 10, "july 2026 bar exam results" 10, "ube minimum score by state" 10) | NO come sito (5; 100 / 500 / 3.000 €/anno; 25-35 ore): condizioni d'uso NCBE vietano la copia, ~50 fonti statali in PDF, NCBE, casefleet, casecub, getoncourse.ai, UWorld già primi; affiliazioni dei corsi senza cifra | wf-2026-10-31-esami-mondo |
| Patente all'estero: esame di teoria e pratica in inglese, Paese per Paese (FeV allegato 7: 14 lingue; "can i take driving test in english in" 10; "driving theory test in english" 10) | **SEZIONE in coda bassa** di Before You Fly, blocco "Before you drive" (5; 30 / 150 / 550 €/anno; 12-18 ore); autoviatest.com già in campo | wf-2026-10-31-esami-mondo |
| Praxis: punteggio minimo per Stato e per test (ETS JSON 200; "praxis passing scores by state" 10) | NO (4,5): 240tutoring, achievable, teachercertification.com con la tabella | wf-2026-10-31-esami-mondo |
| DELE e CCSE 2027: date e centri (calendario 2027 leggibile su cervantes.org; centri in Salesforce JS) | RISERVA con innesco (4,5): si riapre quando il nuovo sito esami del Cervantes pubblica i centri leggibili; controllo a fine gennaio 2027 | wf-2026-10-31-esami-mondo |
| CPA exam: date dei punteggi e promossi per sezione | NO (4): mercato più presidiato del giro | wf-2026-10-31-esami-mondo |
| HSK: date 2027 e centri per città (1.522 centri, ricerca in JS) | NO (4): centri non leggibili, pubblico a pubblicità bassa | wf-2026-10-31-esami-mondo |
| Grecia: esame PEGP per la cittadinanza (Diavgeia JSON 200, 70 centri; "πεγπ εξεταστικα κεντρα" 1) | NO (4): domanda senza città, pubblicità greca bassa | wf-2026-10-31-esami-mondo |
| Svezia: medborgarskapsprovet (riletta) | NO confermato (3,5): primo esame 15/8/2026, 875 candidati, 80 % promossi, soglia 28/40; nessuna data né sede per la sessione successiva | wf-2026-10-31-esami-mondo |
| Regno Unito: SQE date e promossi ("sqe results" 10) | NO dal server (3): `sqe.sra.org.uk` Incapsula | wf-2026-10-31-esami-mondo |
| Paesi Bassi: inburgeringsexamen e Staatsexamen NT2 (riletta) | NO confermato (3): prenotazione centrale DUO, nessuna città; `inburgeren.nl` 000 | wf-2026-10-31-esami-mondo |

---

## 5. Fonti controllate (31/10/2026)

| Fonte | Esito |
|---|---|
| `ncbex.org/statistics-research/bar-exam-results-jurisdiction` | 200, HTML 98.650 byte, "last updated October 30, 2026, 4:50 p.m. (CDT)", tabella per giurisdizione con data di uscita |
| `ncbex.org/exams/ube/score-portability/minimum-scores` | 200, minimi UBE per Stato (Iowa 260 dal luglio 2026) |
| `ncbex.org/exams/nextgen/.../nextgen-ube-adoption-jurisdiction` | 200, aggiornata il 23/10/2026 |
| `ncbex.org/website-terms-use` | 200: "You may not… reproduce, display, distribute… or create derivative works" |
| `ncbex.org/exams/mpre/score-services/mpre-minimum-scores`, `/news-resources/bar-exam-results-release-dates` | 404 |
| `nybarexam.org/Press/20261023 FinalPressRelease_ExamResults.pdf` | 200, PDF 374.565 byte, 67 % su 9.936 candidati |
| `supremecourt.ohio.gov/AttySvcs/admissions/Results/20260728.pdf` | 200, PDF 119.950 byte |
| `calbar.ca.gov/Admissions/Examinations/Statistics` | 404 (percorso) |
| `nasba.org/exams/cpaexam/`, `/scores/` | 200 |
| `aicpa-cima.com/resources/article/learn-more-about-cpa-exam-pass-rates` | 404 |
| `praxis.ets.org/state-requirements.html`, `/state-requirements/newjersey-tests.html` | 200 |
| `praxis.ets.org/.../Search-GetRequiredTests?nationalCode=NJ` | 200, JSON, `qualifyingScore` 162 per il test 5331 |
| `ncsbn.org/exams/exam-statistics-and-publications/nclex-pass-rates.page` | 200 (NCLEX non approfondito: già chiuso per scuola e per Paese) |
| `ncees.org/engineering/pass-rates/` | 503 |
| `sqe.sra.org.uk/about-sqe/sqe-pass-rates`, `/exam-arrangements/assessment-dates` | 200 ma Incapsula (anti-robot), 212 byte |
| `sra.org.uk/become-solicitor/sqe/` | 200, senza dati |
| `uhr.se/medborgarskapsprovet/` e notizia del 22/10/2026 | 200 |
| `inburgeren.nl/examen-doen/` | 000 |
| `duo.nl/particulier/inburgeren/` | 200 |
| `ypes.gr` | 403 |
| `pegp.gr`, `ithageneia.ypes.gr` | 000 |
| `diavgeia.gov.gr/opendata/decisions/ΡΔΜ846ΜΤΛ6-9ΣΓ.json` | 200, JSON (decisione sui centri d'esame del 26/4/2026) |
| `alfavita.gr/sites/default/files/2026-03/pegp.pdf` (circolare del Ministero dell'Istruzione del 3/3/2026) | 200, PDF 372.403 byte: 70 centri + 9 speciali |
| `greek-language.gr/certification/` | 200 |
| `examenes.cervantes.es/es/dele/fechas` (e altri percorsi) | 200, reindirizzati a `cervantes.org/es/examenes/dele` con il calendario DELE e CCSE 2027 |
| `tienda.cervantes.org` | 200, applicazione Salesforce in JavaScript |
| `chinesetest.cn` | 200, applicazione Nuxt, "2027 Test Calendar", 1.522 centri |
| `jlpt.jp/e/application/overseas_list.html` | 200 (JLPT già in lista, non rivalutato) |
| `gesetze-im-internet.de/fev_2010/anlage_7.html` | 200, 14 lingue straniere per la teoria |
| `sede.dgt.gob.es/.../permiso-conducir/` | 200, pagina corta |
| `cbr.nl` (due percorsi) | 000 |
| `vegvesen.no/en/driving-licence/...`, `keishicho.metro.tokyo.lg.jp/multilingual/...` | 404 (percorsi) |
| `quimbee.com/affiliates`, `barmax.com/affiliates`, `jdadvising.com/affiliate-program/`, `240tutoring.com/affiliate-program/`, `mometrix.com/affiliates/` | 404 |
| `adaptibar.com/affiliates` | 200, solo JavaScript, nessuna cifra |
| `study.com/pages/Affiliate_Program.html`, `preply.com/en/affiliate-program` | 403 |
| `surgent.com/affiliate-program/` | 200, nessuna cifra leggibile |
| `italki.com/en/affiliate-program` | 200 (cifra 18 $ a studente già verificata su Awin il 28/10) |
| `discovercars.com/affiliate` | 200, "~$20 per booking, Cookie Lifetime: 365 days" |

Concorrenti visti nelle ricerche web: casefleet.com, casecub.com, getoncourse.ai, legal.uworld.com (statistiche), abajournal.com, dailyjournal.com; 240tutoring.com, achievable.me, teachercertification.com, open-exam-prep.com; autoviatest.com (con `llms-expat.txt`), passmefast.co.uk, thelocal.com, nutheorie.nl, practicatest.com, teoricentralen.se, theorytest.ie.
