# Raddoppiare su quello che funziona (31/10/2026)

Angolo: non si cerca un tema nuovo. Si parte dai numeri veri della rete (GoatCounter), si guardano le 2-3 sezioni che portano visite (EsameB1 e la sezione rifiuti dei visti di Visa Income Checker) e si cerca **il passo successivo del lettore**: cosa deve fare subito dopo, con quale fonte ufficiale per città o Paese, e chi paga.

Letti prima: skill `rete-siti`, `CRUSCOTTO-RETE.md`, `REGOLE-FISSE.md`, `ESPLORATE.md` (per intero le sezioni su cittadinanza, rifiuti dei visti, KDP), `idee-vincenti-2026-10-18.md`. Nessuna nicchia chiusa è rivalutata da capo: dove tocco un tema già visto scrivo il fatto nuovo.

**Prove usate (tutte del 31/10/2026):** API GoatCounter (`stats/hits` con limit=100 e paging con `exclude_paths`, `stats/hits/{id}` per la provenienza di ogni pagina, `stats/toprefs`, `stats/locations`); suggerimenti di Google (`suggestqueries.google.com`, `client=firefox`, lingua e Paese giusti: it/it, en/pk, en/in, en/gb, en/ae, en/us, pt/br); `curl` sulle fonti; ricerca web per la composizione dei risultati (i risultati sono come da un computer negli USA: in Italia possono essere un po' diversi); pagine di Amazon.it lette con `curl` (classifica di vendita del giorno). Le stime sono stime, non dati: ogni stima ha il calcolo.

Voti con la griglia delle ricerche precedenti: domanda 0-3 · buco nei risultati 0-2 · fonte ufficiale leggibile 0-2 · valore del pubblico e chi paga 0-2 · rischi e ore 0-1.

---

## 0. Risposta in breve

**I numeri (GoatCounter, 17-31/10, il contatore è attivo dal 17/10):** 676 visite su tutta la rete; **EsameB1 427 (63 %)**, **Visa Income 130**, Before You Fly 71, Cruise 25, Aste 16, Tourist Tax 7, gli altri 4 siti 0. Ultimi 7 giorni (24-30/10) **495 visite contro 171** dei 7 giorni prima (×2,9): EsameB1 329, Visa Income 86, Before You Fly 48. Provenienza: **Google 274, ChatGPT 158**, diretto 90, Bing 3, Gemini 1. EsameB1 vive di Google (208) e di passaggi interni (112); Visa Income quasi solo di ChatGPT (94 su 130, Google 1).

**Le idee (12 valutate):**

| # | Idea | Dove | Voto | Prudente / centrale / ottimista €/anno a 18 mesi | Ore | Chi paga |
|---|---|---|---|---|---|---|
| 1 | **Dopo il B1: la domanda di cittadinanza prefettura per prefettura** (106 prefetture) | sezione EsameB1 | **7** | 290 / 770 / 2.400 | 25-35 | AdSense, italki/Amazon, libro (n. 3) |
| 2 | Stato della pratica e fasi della cittadinanza (attesa di 24-36 mesi) | sezione EsameB1 | 6 | 100 / 380 / 1.400 | 8-12 | AdSense |
| 3 | **Collana KDP "Esame B1 cittadinanza" (3 titoli) promossa da EsameB1** | prodotto proprio | **7** (7,5 con BookBeam) | 2.100 / 5.000 / **15.100** | 150-220 | Amazon (diritti d'autore) |
| 4 | Simulatore B1 gratuito online | sezione EsameB1 | 6 | 380 / 1.150 / 3.800 | 30-45 | AdSense, libro |
| 5 | **Redditi minimi per stranieri 2026 con calcolatore** (cittadinanza, carta di soggiorno, ricongiungimento) | sezione EsameB1 | **7** | 140 / 380 / 1.200 | 6-10 | AdSense |
| 6 | Pagine coppia "[Stato] visa rejection rate for [Paese]" (232 coppie) | sezione Visa Income | 6,5 | 120 / 360 / 1.440 | 10-16 | AdSense, AXA Schengen, Stay22 |
| 7 | **Visto Schengen per chi vive nel Regno Unito e negli Emirati** (residenti, non cittadini) | sezione Visa Income | **7** | 410 / 1.100 / 4.200 | 12-18 | AdSense UK, assicurazioni UK su Awin |
| 8 | Permesso di soggiorno questura per questura | – | 4,5 NO | – | – | – |
| 9 | Documenti dal Paese d'origine (certificato penale, atto di nascita) per Paese | – | 3,5 NO | – | – | – |
| 10 | Contatti a pagamento per avvocati della cittadinanza | – | 2 NO | – | – | – |
| 11 | B1 e cittadinanza per matrimonio in inglese (coniugi all'estero) | – | 6 RISERVA | – | – | – |
| 12 | Assicurazione per il visto Schengen come pagina a sé | – | RISERVA confermata | – | – | – |

**Le due con potenziale ≥ 10.000 €/anno, detto onestamente:**
- **n. 3, collana KDP**: 15.100 € nel caso ottimista, **5.000 € nel centrale**. È l'unica idea dove il nostro traffico vero diventa una vendita con un margine pieno (5,6 € a copia) e senza cancello fiscale (diritti d'autore).
- **Il pacchetto "Dal B1 al passaporto"** (n. 1 + 2 + 3 + 5 costruiti insieme, sez. 4): **~21.600 € ottimista, ~6.700 € centrale, ~2.600 € prudente**.

**Nessuna idea arriva a 10.000 €/anno nel caso centrale.** Il motivo è uno solo: il pubblico che oggi ci premia (stranieri in Italia, richiedenti visto da Pakistan, Iraq, Bangladesh) vale poco in pubblicità, e l'unico pagatore ricco del percorso, l'avvocato, **non può pagare i contatti** (art. 37 del Codice deontologico forense: vietato acquisire clienti tramite agenzie o procacciatori). Il vincolo da allentare, se Massimiliano vuole i 10.000 € nel centrale: **un test di Amazon Ads con tetto (es. 100 €) sulla collana B1**, dopo che il primo titolo ha almeno 10 recensioni. È una spesa: si fa solo col suo sì.

---

## 1. I numeri veri della rete (GoatCounter, letti il 31/10/2026)

Chiamate: `stats/hits?start=2026-10-01T00:00:00Z&end=2026-10-31T23:00:00Z&limit=100` con paging `exclude_paths` (173 percorsi, 676 visite; il contatore registra dal 17/10); stesse chiamate per 17-23/10 e 24-30/10; `stats/hits/{path_id}` per la provenienza di ognuno dei 173 percorsi; `stats/toprefs`; `stats/locations`.

**Per sito (17-31/10):** EsameB1 427 · Visa Income 130 · Before You Fly 71 · Cruise Health Scores 25 · Aste in Chiaro 16 · Tourist Tax 7 · Italy Strikes, EsamiDiStato, FloodCost, ApprovedCondos 0.

**Settimana contro settimana:** 17-23/10 = 171 (EsameB1 96, Visa 44, BYF 17, Cruise 13); 24-30/10 = **495** (EsameB1 **329**, Visa **86**, BYF 48, Aste 15, Cruise 10, Tourist Tax 7). EsameB1 a questo ritmo fa ~1.400 visite al mese.

**Provenienza per sito (17-31/10):**

| Sito | Google | ChatGPT | Interno (da un'altra pagina del sito) | Diretto | Altro |
|---|---|---|---|---|---|
| EsameB1 | 208 | 39 | 112 | 65 | Bing 1, Yandex 1, WeChat 1 |
| Visa Income | 1 | **94** | 26 | 8 | Bing 1 |
| Before You Fly | 55 | 5 | – | 10 | Gemini 1 |
| Aste in Chiaro | – | **13** | 2 | – | – |
| Cruise | 5 | 7 | 6 | 6 | Bing 1 |

**Pagine più viste:** EsameB1 home 71, **Milano 58**, come funziona 24, costo 22, Verona 20, **esempi d'esame 17 (11 da ChatGPT)**, risultati 16, Modena/CELI/Torino/Roma 12; Visa Income **Pakistan 18 (16 da ChatGPT)**, Iraq 6, Bangladesh/UK/Tunisia/Pakistan "easiest" 5; Before You Fly liquidi TSA USA 11, Barcellona 8; Aste Roma 8 (7 da ChatGPT).

**Percorso del lettore dentro EsameB1 (passaggi interni, 17-31/10):** città → costo (Milano 6, Verona 2, Bari 2, Genova 1, Modena 1); città → come funziona (Milano 4, Verona 2 e 15 altre città 1 ciascuna); come funziona → home 9; come funziona → pagine ente (CELI 3, CILS 2, CERT.IT 2). **Chi arriva su una città cerca subito "quanto costa" e "come funziona": il lettore vuole il passo successivo.** Il passo successivo dopo l'esame (la domanda di cittadinanza) oggi non c'è nel sito, a parte la pagina del reddito per il ricongiungimento.

**Dentro Visa Income:** Pakistan → "easiest Schengen visa from Pakistan" 2; il resto arriva da ChatGPT direttamente sulla pagina della nazionalità.

**Paesi dei visitatori:** Italia 393, USA 62, Pakistan 29, Regno Unito 23, Germania 19, Tunisia 8, Turchia 8, Canada 7, Giappone 7.

**Search Console (dal cruscotto, foto del 30/10):** EsameB1 3.570 impressioni e 163 clic dall'apertura, CTR 4,6 %, posizione media 7,3, ~400 impressioni e 20-25 clic al giorno il 26-28/10.

---

## 2. Il percorso del lettore e cosa ha dati ufficiali

**Chi fa il B1** (Istat, `esploradati.istat.it` SDMX, flusso `29_849_DF_DCIS_ACQCITIZ_3`, letto il 31/10, HTTP 200): acquisizioni di cittadinanza in Italia **2025: 196.955** (2024: 217.448), di cui **per residenza 88.533**, **per matrimonio 22.845** (+8,2 %), per trasmissione 85.577. Chi ottiene la cittadinanza per residenza o matrimonio ha fatto il B1 (o è esentato): sono ~111.000 persone all'anno, più chi aspetta (24-36 mesi).

| Passo dopo il B1 | Domanda (suggerimenti it/it) | Fonte ufficiale per città/Paese | Chi paga |
|---|---|---|---|
| Domanda online (portale ALI, SPID) | "domanda cittadinanza italiana" 10 (online, per matrimonio, per residenza, documenti, requisiti, portale ali) | DLCI (Ministero dell'Interno), pagine art. 9 e art. 5: **200** | AdSense |
| Requisito di reddito | "reddito cittadinanza italiana" 10 (2026, requisiti, **lordo o netto**); "reddito minimo per cittadinanza italiana" 6 | PDF della Prefettura `redditoimponibile.pdf`: **200** (8.263,31 €; 11.362,05 € col coniuge; +516 € per figlio; tabella per 1-4 figli; quale rigo del 730) | AdSense |
| Contributo 250 € | "contributo cittadinanza" 10 (250 euro, 2026, pagopa, pagamento online) | Prefetture di Milano e Torino: 250 € dal 5/10/2018, validità un anno, rimborso con raccomandata (**200**) | AdSense |
| Prefettura competente | "cittadinanza italiana prefettura" 10 (Milano, Firenze, Torino, Trieste, Parma, Roma, Bergamo, Verona, Udine); "cittadinanza prefettura [città]" con suggerimenti in **18 città su 18** provate (Milano 6, Roma 6, Brescia 6, Bologna 5, Bergamo 5…) | **106 prefetture** con pagina `prefettura.interno.gov.it/it/prefetture/<città>/cittadinanza`: **23 su 23** provate rispondono 200 (Milano 113 kB, Verona 134 kB: documenti, discordanze nei nomi, indirizzo dell'ufficio, rimborso) | AdSense |
| Tempi | "tempi cittadinanza italiana" 10 (per matrimonio, per residenza, attesa 2026, forum) | DLCI: 24 mesi prorogabili a 36 per le domande dal 20/12/2020, 48 mesi prima (**200**); nessun tempo per prefettura (già NO il 18/10) | AdSense |
| Stato della pratica | "stato pratica cittadinanza" 10 ("sono in corso verifiche istruttorie", fasi, lettera f, lettera d); "cittadinanza fase" 10 (fase 3, 4, 5, 6, 7, "quanto dura") | Vademecum DLCI del 23/4/2025 (PDF **200**: fase preliminare, istruttoria, decreto, notifica). I numeri di fase del portale **non** sono pubblicati | AdSense |
| Giuramento | "giuramento cittadinanza" 10; "giuramento cittadinanza [città]" in **15 città su 18** (Roma 10, Bologna 5, Torino 4, Verona 4, Genova 4, Perugia 4) | pagine dei Comuni, sparse (`comune.torino.it` 000 dal server) | AdSense |
| Documenti dal Paese d'origine | "certificato penale [Paese]" 0-2 per Paese; "atto di nascita marocco" 5 | consolati, sparsi | nessuno (NO del 26/10 confermato) |
| Avvocato se la pratica si ferma | "avvocato cittadinanza" 10 (costo, Milano, Verona, Roma, Bologna); "ricorso tar cittadinanza costi" | – | **nessuno**: art. 37 del Codice deontologico forense |
| Permesso di soggiorno (prima della cittadinanza) | "permesso di soggiorno questura milano/verona" 10 ciascuna (ritiro, appuntamento, pronto, orari) | `questure.poliziadistato.it/it/Milano` 200 ma solo notizie; stato del permesso solo col numero di pratica; `portaleimmigrazione.it` 0 byte (JavaScript) | nessuno |
| Prepararsi all'esame | "test b1 cittadinanza online" 7 (gratis, pdf); "simulazione esame b1 cittadinanza" 4; "cils b1 cittadinanza libro" 3 | prove ufficiali CILS/CELI/PLIDA (già linkate in `/esempi-esame-b1/`) | italki (approvato), Amazon.it (attivo), **libro proprio** |

**Chi chiede un visto Schengen** (sezione rifiuti di Visa Income): il passo dopo "quanto rifiutano" è "dove conviene chiedere" ("easiest schengen visa for pakistani / filipino / indians / moroccans / nigerians / uae residents…" 10), poi soldi da mostrare ("schengen visa bank statement requirement pakistan" 10; già PASSA il 27/10), assicurazione ("schengen visa insurance pakistan / uae / from uk / axa" 10), appuntamento ("schengen visa appointment pakistan / karachi / islamabad / london / dubai" 10: nessuna fonte ufficiale, NO del 21/10). La domanda per **coppia Stato × Paese** c'è: "italy visa rejection rate for pakistan / for indians / for bangladeshi", "france visa success rate for indian / from nepal / from pakistan", "germany visa rejection rate for pakistan" (en/pk, en/in). E c'è una domanda grande dei **residenti** nel Regno Unito e negli Emirati che chiedono il visto da lì (sez. 3, idea 7).

---

## 3. Le idee una per una

### Idea 1. Dopo il B1: la domanda di cittadinanza, prefettura per prefettura (sezione `/cittadinanza/` di EsameB1)

**Cosa:** 106 pagine prefettura ("Cittadinanza italiana a Verona: prefettura, documenti, contributo, giuramento") + 8-10 pagine guida (per residenza, per matrimonio, documenti, contributo 250 € e come pagarlo, portale ALI, tempi, notifica e giuramento, trascrizione dell'atto di nascita) con link da ogni pagina città dell'esame ("Dopo l'esame: la domanda alla Prefettura di …"). Ogni pagina prefettura ha i suoi dati: indirizzo e contatti dell'ufficio cittadinanza, regole locali scritte dalla prefettura (es. Verona: discordanze dei nomi, circolare 462/2019; Torino: dichiarazione consolare; Milano: rimborso del contributo), cittadinanze concesse nella regione (Istat), Comune capoluogo per il giuramento e la trascrizione, sedi d'esame B1 vicine (già in `sedi.json`).

**Traffico che la giustifica:** EsameB1 427 visite in 14 giorni, 329 nell'ultima settimana; i lettori passano da città a costo e come funziona (sez. 1): seguono il percorso. Il modello "una pagina per città con dati ufficiali" è quello che porta Milano a 58 visite e 94 città in Google in posizione 7,3.

**Domanda:** 18 città su 18 con suggerimenti "cittadinanza prefettura [città]"; "domanda cittadinanza italiana" 10, "cittadinanza italiana per matrimonio" 10, "tempi cittadinanza italiana" 10, "documenti per cittadinanza italiana" 10.

**Google (ricerca "cittadinanza italiana prefettura verona documenti tempi", 31/10):** PDF della Prefettura, studi legali generalisti (leggioggi, studiocataldi, infoimmigrazione, waitaly), moduli di Comuni piccoli, un PDF dell'UNHCR. **Nessuna pagina ordinata per prefettura** con documenti, contatti e contributo insieme.

**Fonte (curl 31/10):** `prefettura.interno.gov.it/it/prefetture` → 106 prefetture; pagina `/cittadinanza` 200 per 23 su 23 provate (Milano, Firenze, Torino, Verona, Roma, Napoli, Lodi, Bologna + 15 a caso); DLCI art. 9 e art. 5 200; vademecum 23/4/2025 200 (259 kB); Istat SDMX 200. Testi pubblici del Ministero: si riportano i fatti con fonte e link, senza copiare le pagine.

**Chi paga:** AdSense (EsameB1 in revisione); italki e Amazon.it per chi arriva prima dell'esame; il libro della n. 3. Nessun contatto venduto (sez. 3, n. 10).

**Stima a 18 mesi.** Visite al mese: prudente 3.000, centrale 8.000, ottimista 20.000 (base: EsameB1 oggi ~1.400 al mese con la sola parte esame; ~111.000 cittadinanze all'anno per residenza e matrimonio, più chi aspetta). Guadagno ogni 1.000 visite: AdSense italiano ~4 € ogni 1.000 pagine × 1,5 pagine = 6 €, più 2 € di affiliazioni = 8 € (10 € nell'ottimista).
- Prudente: 3.000 × 12 × 8 / 1.000 = **290 €/anno**
- Centrale: 8.000 × 12 × 8 / 1.000 = **770 €/anno**
- Ottimista: 20.000 × 12 × 10 / 1.000 = **2.400 €/anno**
Primi soldi: con AdSense approvato, 1-2 mesi dalla pubblicazione.

**Ore:** 25-35 (raccolta delle 106 pagine con lo stesso schema, controllo a mano di 10 prefetture, pagine guida, collegamenti, revisione indipendente). Esce con la pubblicazione del lunedì di EsameB1, nessun deploy in più.

**Voto 7** (domanda 3 · buco 1,5 · fonte 2 · valore 0,5 · rischi e ore 0). Regge come sezione (rete fitta), non come sito: sotto i 5.000 €. Il valore vero è far crescere EsameB1 e portare lettori al libro.

### Idea 2. Stato della pratica e fasi della cittadinanza (pagine dentro la sezione 1)

**Cosa:** 10-15 pagine: "Sono in corso verifiche istruttorie: cosa vuol dire", "Lettera f nella pratica: è l'articolo 9 comma 1 lettera f (10 anni di residenza), non una fase", notifica del decreto, preavviso di rigetto, cosa dice la legge dopo 24-36 mesi (diffida, ricorso: solo i passi, senza consigli legali).

**Domanda:** "cittadinanza fase" 10 (fase 3, 4, 5, 6, 7 e "quanto dura" per 4, 5, 6, 7); "stato pratica cittadinanza" 10; "sono in corso verifiche istruttorie" 6; "notifica decreto cittadinanza" 6; "diffida cittadinanza" 4. Chi aspetta 2-3 anni torna a cercare: visite ripetute.

**Google ("stato pratica cittadinanza fase 5 quanto dura"):** siti di domande e risposte senza fonte (areasosta, qualcherisposta, tattoomuse, in3giorni) con durate che si contraddicono ("circa 3 mesi", "2-3 mesi"), un avvocato (boccadutri, "le 7 fasi"). Buco vero.

**Fonte:** vademecum DLCI 23/4/2025 (200) per le fasi del procedimento; DLCI per i termini. **Limite:** i numeri di fase mostrati dal portale non sono pubblicati in una pagina pubblica; le pagine diranno solo ciò che il Ministero scrive e "il Ministero non pubblica la durata delle singole fasi". Rischio di dire meno dei siti che inventano.

**Chi paga:** AdSense.

**Stima:** visite al mese 1.000 / 4.000 / 12.000 × 8-10 € ogni 1.000 → **100 / 380 / 1.400 €/anno**. **Ore** 8-12. **Voto 6** (domanda 2,5 · buco 1,5 · fonte 1 · valore 0,5 · rischi 0,5).

### Idea 3. Collana KDP "Esame B1 cittadinanza" promossa da EsameB1 (prodotto proprio)

**Cosa:** 3 titoli in italiano semplice: (a) CILS B1 Cittadinanza, 10 simulazioni originali con soluzioni; (b) CELI 2 Cittadinanza, simulazioni; (c) prova orale e scritta (tracce, modelli, frasi utili). Gli **audio** stanno su EsameB1 (QR nel libro → pagina del sito): ogni lettore del libro torna sul sito. Dal sito: riquadro "Il libro di EsameB1" su esempi, ente, costo e città.

**Traffico che la giustifica:** `/esempi-esame-b1/` 17 visite in 14 giorni, **11 da ChatGPT** (la gente chiede all'assistente "dove trovo prove del B1"); EsameB1 329 visite nell'ultima settimana; 11 iscritti veri al 28/10.

**Domanda (it/it):** "test b1 cittadinanza online" 7 (gratis, pdf), "simulazione esame b1 cittadinanza" 4, "cils b1 cittadinanza libro" 3, "esercizi b1 cittadinanza" 3; (en/us) "cils b1 cittadinanza book", "past papers", "sample test".

**Composizione di Amazon.it** (ricerca "cils b1 cittadinanza" nei libri, 31/10): 20 risultati, **5 sponsorizzati**, almeno 15 titoli autopubblicati (ASIN B0…), molti del 2026. Classifiche lette dalle schede: Ornimi "Percorso CILS Cittadinanza" **n. 856 in Libri** (522 voti, 2021); Loescher "Pronti per il test B1" n. 3.496 (295 voti); autopubblicato "Cils Facile B1-B2" n. 14.264 (45 voti, marzo 2026); "Workbook CILS B1 Cittadinanza" n. 31.833 (75 voti, 2024); "Esame B1 Cittadinanza CILS – Prova scritta" n. 278.831 (agosto 2026). **Il mercato c'è** (il primo vende circa 15-20 copie al giorno: stima da classifica, non dato) **ma è affollato**: un libro nuovo senza il sito resterebbe tra n. 15.000 e n. 30.000 (circa 0,5-1 copia al giorno).

**Fonte ufficiale:** formati e sillabi ufficiali (CILS, CELI, PLIDA, CERT.IT già verificati il 26-30/10 nelle pagine esempi e risultati; `cils.unistrasi.it` e `cvcl.it` 200 il 31/10). Le prove ufficiali non si copiano: le simulazioni sono originali. Royalty KDP (pagina d'aiuto KDP 200): 60 % del prezzo senza IVA meno la stampa.

**Margine per copia:** brossura 14,99 € → 14,41 € senza IVA al 4 % × 60 % = 8,65 € − stampa (0,85 € + 0,012 € × 180 pagine = 3,01 €) = **5,64 €**; ebook 7,99 € → ~4,6 €. Media usata: 5,6 €.

**Stima a 18 mesi (3 titoli).** Visite EsameB1 al mese: 3.000 / 6.000 / 12.000 (oggi ~1.400). Clic sul riquadro del libro 3 % / 4 % / 5 %, acquisto su Amazon 10 % / 12 % / 15 %. Vendite da Amazon senza pubblicità: 0,25 / 0,5 / 1,5 copie al giorno per titolo.
- Prudente: 3.000 × 3 % × 10 % = 9 dal sito + 3 × 7,5 = 22,5 da Amazon = 31,5 copie al mese × 5,6 € × 12 = **2.100 €/anno**
- Centrale: 6.000 × 4 % × 12 % = 29 + 3 × 15 = 45 → 74 copie × 5,6 × 12 = **5.000 €/anno**
- Ottimista: 12.000 × 5 % × 15 % = 90 + 3 × 45 = 135 → 225 copie × 5,6 × 12 = **15.100 €/anno**
Primi soldi: Amazon paga circa 60 giorni dopo la fine del mese di vendita; primo titolo vendibile 4-6 settimane dopo l'inizio del lavoro.

**Ore:** 60-90 per titolo (simulazioni originali, soluzioni, audio registrati con sintesi vocale e ospitati sul sito, copertina con codice, controllo indipendente della lingua). 150-220 per la collana.

**Vincoli:** Massimiliano (30/10): i libri con voto 9 hanno la precedenza; la collana resta in coda dopo di loro (cruscotto sez. 7b). Prima di scrivere: verifica secondo la skill KDP (foto BookBeam di 2-3 ricerche). Nessuna spesa: Amazon Ads solo con un test a tetto e il sì di Massimiliano.

**Voto 7** (domanda 2 · buco 0,5 · vantaggio proprio del sito 2 · valore 2 · rischi e ore 0,5); **7,5** se BookBeam conferma vendite costanti dei titoli autopubblicati. Unica idea della giornata con ottimista oltre 10.000 €.

### Idea 4. Simulatore B1 gratuito online (sezione `/prova/` di EsameB1)

**Cosa:** quiz interattivo con domande originali di ascolto, lettura e lessico per CILS e CELI, correzione immediata, punteggio con le soglie ufficiali; alla fine il riquadro del libro e italki.

**Domanda:** "test b1 cittadinanza online" 7 (con "gratis"); en/us "italian b1 test online free", "italian b1 test example pdf with answers" (10 varianti su "italian b1 test").

**Google:** prove ufficiali gratuite degli enti, siti di corsi (lingookies, open-exam-prep, europassitalian), video. Gli enti hanno già le prove migliori: il nostro buco è solo il formato interattivo.

**Chi paga:** AdSense (molte pagine viste per visita), libro, italki.

**Stima:** utenti al mese 1.000 / 2.000 / 6.000 × 8 / 10 / 12 pagine × 4-4,5 € ogni 1.000 pagine, più qualche libro → **380 / 1.150 / 3.800 €/anno**. **Ore** 30-45 (200-400 domande originali, audio, revisione). **Voto 6**: meglio come parte della collana (le stesse domande servono al libro) che da sola.

### Idea 5. Redditi minimi per stranieri 2026, con calcolatore (pagine dentro EsameB1, accanto al ricongiungimento)

**Cosa:** (a) "Reddito per la cittadinanza italiana 2026": 8.263,31 € da solo, 11.362,05 € col coniuge, +516 € per figlio, tabella per 1-4 figli, **imponibile IRPEF (quale rigo del 730, del Modello Redditi, della CU)**, ultimi 3 anni, redditi esteri esclusi, chi della famiglia conta; calcolatore. (b) "Reddito per la carta di soggiorno (permesso UE di lungo periodo) 2026": importo dell'assegno sociale (546,24 € × 13 = 7.101,12 €, già verificato sul PDF INPS per la pagina del ricongiungimento). (c) collegamento con la pagina del ricongiungimento già online.

**Domanda:** "reddito cittadinanza italiana" 10 (2026, requisiti, **lordo o netto**); "reddito minimo per cittadinanza italiana" 6; "permesso di soggiorno lungo periodo reddito" 10 (2026, 10 anni); "carta di soggiorno requisiti" 10 (reddito, cud).

**Google:** la ricerca dagli USA confonde con il "reddito di cittadinanza" (sussidio abolito) e mostra assegno unico e ADI: segnale che non c'è una pagina chiara; in Italia compaiono PDF delle prefetture e blog legali.

**Fonte (curl 31/10):** `prefettura.interno.gov.it/sites/default/files/16/2024-05/redditoimponibile.pdf` 200 (tabella completa e righi dei modelli); pagine prefettura di Lodi e L'Aquila (redditi esclusi); INPS per l'assegno sociale (già in `dati/ricongiungimento.json`).

**Chi paga:** AdSense.

**Stima:** visite al mese 1.500 / 4.000 / 10.000 × 8 / 8 / 10 € → **140 / 380 / 1.200 €/anno**. Picco a gennaio (nuovo assegno sociale). **Ore** 6-10. **Voto 7** (domanda 2,5 · buco 1,5 · fonte 2 · valore 0,5 · rischi 0,5). Da fare per prima: poche ore, dati già in casa a metà.

### Idea 6. Pagine coppia "[Stato] visa rejection rate for [Paese]" (sezione rifiuti di Visa Income)

**Cosa:** una pagina per ogni coppia con almeno 10.000 domande nel 2025 (**232 coppie**; 467 con almeno 3.000): "Italy visa rejection rate for Pakistan 2025: 39,2 %". Contenuto proprio di ogni coppia (altrimenti non si fa): tasso 2025 e 2024, ogni consolato (es. Islamabad e Karachi), quota di visti a ingressi multipli, posizione tra gli Stati Schengen per quel Paese, soldi da mostrare per quello Stato in valuta locale (idea del 27/10), link all'ambasciata.

**Traffico che la giustifica:** ChatGPT porta 94 visite su 130 a Visa Income, quasi tutte sulle pagine di nazionalità (Pakistan 16 da ChatGPT); la pagina "easiest" del Pakistan riceve passaggi interni. La pagina Pakistan contiene già la tabella per Stato (Italia 39,2 % nel 2025, 31,7 % nel 2024; Germania 24,2 %; Danimarca 78,7 %): la coppia dà un indirizzo proprio alla domanda precisa.

**Domanda:** en/pk "italy visa rejection rate" 10 (for pakistan, for indians, for bangladeshi, 2026), "france visa success rate" 10 (for indian, from nepal, from pakistan, 2026), "germany visa rejection rate for pakistan" 6; en/in "schengen visa rejection rate" 10.

**Google ("italy visa rejection rate for pakistan 2025"):** giornali e blog pakistani (propakistani, arynews, pakobserver, bolnews, urdupoint) con cifre sbagliate o vecchie (ProPakistani scrive "Italia 12 %"; il dato ufficiale per le domande fatte in Pakistan è 39,2 %). Buco vero, e una cifra ufficiale che contraddice i giornali è quella che gli assistenti citano.

**Fonte:** file della Commissione "Visa statistics for consulates 2025" già in `visaincome/dati/rifiuti.json` (generato il 30/10); pagina della Commissione 200 il 31/10.

**Chi paga:** AdSense (pubblico di Pakistan, India, Bangladesh, Nord Africa: vale poco), AXA Schengen (da 4,90 €, 10 % su Tradedoubler, da iscrivere: meno di 1 € a polizza nella maggior parte dei casi), Stay22 per l'albergo dell'itinerario.

**Stima:** visite al mese 1.000 / 3.000 / 8.000; ogni 1.000 visite AdSense 2 € + AXA 1 % di clic × 20 % × 3 € = 6 € + albergo 2 € = 10 € (15 € nell'ottimista) → **120 / 360 / 1.440 €/anno**. **Ore** 10-16. **Voto 6,5** (domanda 2,5 · buco 1,5 · fonte 2 · valore 0,5 · rischi 0: pagine simili tra loro, si fanno solo con i dati propri della coppia).

### Idea 7. Visto Schengen per chi vive nel Regno Unito e negli Emirati (sezione rifiuti di Visa Income)

**Cosa:** chi vive a Londra o a Dubai con un passaporto indiano, pakistano, nigeriano o filippino chiede il visto Schengen dal consolato nel Paese dove vive. Pagine: "Schengen visa from the UK: which country refuses least" (hub), "France / Spain / Italy / Germany… visa from the UK" (circa 27 Stati con consolato nel Regno Unito), lo stesso per gli Emirati (circa 30), poi Arabia Saudita e Qatar. Dati per pagina: domande e tasso di rifiuto nei consolati di quello Stato nel Paese di residenza (Londra, Edimburgo, Manchester; Dubai, Abu Dhabi), visti a ingressi multipli, soldi da mostrare convertiti in sterline o dirham (cambio BCE per GBP; ancoraggio ufficiale al dollaro per AED), tassa del visto (90 €, pagina UE 200), assicurazione obbligatoria (30.000 €).

**Traffico che la giustifica:** visitatori dal Regno Unito 23 e dagli Emirati 3 nel periodo; la pagina `/visa-refusal-rates/united-kingdom/` esiste ma ha **0 visite**: il titolo dice "Schengen visa rejection rate United Kingdom", la gente scrive "schengen visa **from** uk". Primo passo a costo quasi zero: titolo e risposta in alto.

**Domanda:** en/gb "schengen visa from uk" 10 (for indian passport, price, to france, to spain, to italy, to germany, for pakistani passport, as an international student); "easiest schengen visa from uk" 10; "france visa from uk" 10 (for indian/pakistani passport, tls, fees, processing time); "schengen visa uk residents" 10; en/ae "schengen visa from dubai" 10 (cost, to france, switzerland, italy, greece, netherlands, germany, for indian/pakistani passport); "easiest schengen visa from dubai" 10.

**Google ("easiest schengen visa from uk for indian passport holders rejection rate"):** giornali indiani con i tassi per nazionalità (non per Paese di residenza), blog di agenzie (atlys, visa2fly). **Nessuno ha i tassi dei consolati nel Regno Unito o negli Emirati**, che il file della Commissione contiene.

**Fonte:** stesso file della Commissione (in casa): Regno Unito **512.426 domande, 10,4 % non rilasciati, 34 consolati**; Emirati **298.064, 23,9 %, 30 consolati**; Arabia Saudita 553.967, 5,1 %; Qatar 102.930, 14,9 %.

**Chi paga:** AdSense con pubblico britannico ed emiratino (vale di più); assicurazioni di viaggio britanniche su Awin: Debenhams Travel Insurance **3,50 £ (premi fino a 30 £), 10 £ (oltre 30 £), 21 £ (annuale)** per polizza (pagina di lancio del programma su Awin), Globelink 10-20 % del premio (pagina del programma); AXA Schengen; Stay22 e DiscoverCars (già approvato). Da fare da Massimiliano: iscrizione ad Awin e a un programma assicurativo britannico.

**Stima:** visite al mese 1.500 / 4.000 / 10.000; ogni 1.000 visite AdSense 10 € + assicurazione (metà dei visitatori nel Regno Unito: 1,5 % di clic × 15 % × 9 € medi × 0,5 = 10 €) + albergo e auto 3 € = 23 € (35 € nell'ottimista) → **410 / 1.100 / 4.200 €/anno**. Primi soldi: AdSense subito dopo l'approvazione; assicurazioni dopo l'iscrizione. **Ore** 12-18.

**Voto 7** (domanda 2,5 · buco 1,5 · fonte 2 · valore 1 · rischi 0: la nostra pagina con gli stessi dati oggi non è trovata, quindi la domanda per noi va provata a 30 giorni). Fra le idee visti è quella col pubblico migliore.

### Idea 8. Permesso di soggiorno, questura per questura — NO (4,5)

Domanda fortissima ("permesso di soggiorno questura milano" 10: ritiro, appuntamento, pronto, orari; uguale per Verona; "permesso di soggiorno pronto per il ritiro [città]" 10; "kit permesso di soggiorno" 10). Ma le pagine `questure.poliziadistato.it/it/<città>` (200) contengono solo notizie; lo stato del permesso si vede solo col numero di pratica; `portaleimmigrazione.it` risponde con una pagina vuota (JavaScript); appuntamenti dietro accesso. Stesso verdetto di CIE e passaporto (18/10). Si riapre se le questure pubblicano orari e tempi di ritiro in una pagina leggibile. Al massimo: costo del permesso e della carta di soggiorno ("carta di soggiorno costo" 10) come riga nella pagina dei redditi (n. 5), solo con una fonte ufficiale leggibile.

### Idea 9. Documenti dal Paese d'origine per Paese — NO confermato (3,5)

Suggerimenti 31/10: "certificato penale" + Marocco, Pakistan, Bangladesh, Brasile, Tunisia, Senegal, Nigeria 1 ciascuno; Egitto, Cina, Moldavia, India 0; Albania 2; "atto di nascita marocco" 5. Conferma il NO del 26/10: la gente cerca la regola generale ("certificato penale cittadinanza" 10: scadenza, 14 anni, online, quando non serve, autocertificazione), non il Paese. La regola generale va in una pagina guida della n. 1.

### Idea 10. Contatti a pagamento per avvocati della cittadinanza — NO (2)

Domanda vera ("avvocato cittadinanza" 10 con costo e città; "ricorso tar cittadinanza costi"), ma l'art. 37 del Codice deontologico forense vieta all'avvocato di acquisire clienti tramite agenzie o procacciatori: un sito che vende contatti agli avvocati li espone a sanzione. Si chiude. Toglie anche l'ipotesi "contatti" dagli ottimisti delle idee 1 e 2.

### Idea 11. B1 e cittadinanza per matrimonio in inglese — RISERVA (6), invariata

"italian citizenship by marriage" 10 (requirements, language requirements, processing time, new law, documents, australia, canada), "italian citizenship b1 test" e "italian b1 citizenship practice test" (en/us), ma per le sedi all'estero: "cils exam london" 5, "cils exam centers usa" 3, "celi exam centers usa" 1. Regola di riapertura del 21/10 invariata (pagina inglese degli esempi con ≥ 100 impressioni al mese dall'estero). Da sapere: un'edizione inglese della collana (n. 3) su Amazon.com è il modo più economico per provarla (Amazon.com dal server: 503, non verificato).

### Idea 12. Assicurazione per il visto Schengen come pagina a sé — RISERVA confermata

AXA Schengen (200 il 31/10): "da 4,90 €", "full refund in case of visa rejection". Con il 10 % la commissione è di pochi centesimi o pochi euro: vale come riquadro dentro le idee 6 e 7, non come sezione.

---

## 4. Il pacchetto "Dal B1 al passaporto" (idee 1 + 2 + 3 + 5 insieme)

| Parte | Prudente | Centrale | Ottimista |
|---|---|---|---|
| 1. Cittadinanza per prefettura | 290 | 770 | 2.400 |
| 2. Stato della pratica | 100 | 380 | 1.400 |
| 3. Collana KDP | 2.100 | 5.000 | 15.100 |
| 5. Redditi minimi | 140 | 380 | 1.200 |
| Più visite su EsameB1 → più italki e Amazon (stima: +15 % sulle affiliazioni del sito) | – | ~200 | ~1.500 |
| **Totale €/anno a 18 mesi** | **~2.600** | **~6.700** | **~21.600** |

Ore: ~190-280 (di cui 150-220 per i libri). Il pacchetto rende soprattutto attraverso il libro: le sezioni portano le persone, il libro guadagna. Ordine consigliato: n. 5 (6-10 ore, subito) → n. 1 (25-35 ore, pubblicazioni del lunedì) → n. 2 → collana KDP quando la coda dei libri da 9 si libera. Per Visa Income: titolo e risposta in alto della pagina Regno Unito (1 ora) → n. 7 → n. 6.

**Soglie di controllo (a 30 giorni dalla pubblicazione, GoatCounter):** n. 5 ≥ 100 visite; n. 1 ≥ 300 visite sulle pagine prefettura; n. 7 ≥ 150 visite sulle pagine "from UK/Dubai"; n. 6 ≥ 200 visite sulle coppie. Sotto soglia: niente lavoro in più, la sezione resta online.

## 5. Cosa ha insegnato questo giro

1. **Il percorso del lettore si vede nei numeri**: dentro EsameB1 il 26 % delle visite arriva da un'altra pagina del sito, e va verso "costo" e "come funziona". Il passo dopo l'esame (la domanda in Prefettura) ha la stessa forma del modello vincente: obbligatorio, una pagina ufficiale per ognuna delle 106 prefetture, domanda in tutte le città provate.
2. **Il pagatore del pubblico immigrati in Italia è debole**: niente avvocati (deontologia), niente traduttori e patronati (nessun programma), rimesse senza domanda in italiano ("mandare soldi in pakistan" 1, "inviare soldi in bangladesh" 1). Il guadagno vero è un prodotto nostro (libro) che il traffico vende.
3. **Visa Income vive di ChatGPT su pagine con numeri ufficiali per Paese**: conviene dare a ogni domanda precisa (Stato × Paese, residenti nel Regno Unito e negli Emirati) il suo indirizzo, con la cifra ufficiale in alto. Il pubblico dei residenti nel Regno Unito e negli Emirati vale di più di quello dei Paesi di partenza.
4. Per arrivare a 10.000 €/anno nel caso centrale manca un pagatore: il vincolo da discutere con Massimiliano è un test di Amazon Ads con tetto sulla collana B1 (spesa, solo col suo sì).
