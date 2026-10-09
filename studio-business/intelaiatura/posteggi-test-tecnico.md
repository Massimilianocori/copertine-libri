# BandiPosteggi – Test tecnico delle fonti (condizione 2)

Data del test: 9 ottobre 2026 (tutti gli HTTP status e i conteggi sono di questa data). Riferimento: `3-opportunita-diverse.md`, candidata A, condizione 2 e sezione 6 "Test a costo zero".
Dati e script: `bandiposteggi/` (elenco dei file in fondo). Spesa: zero.

## 0. Esito in breve

| Criterio della soglia | Richiesto | Misurato | Esito |
|---|---|---|---|
| Avvisi 2026 raccolti | ≥ 60 | **84** (60 Comuni diversi) | raggiunto, ma solo grazie alla ricerca web manuale |
| Regioni | ≥ 8 | **15** | raggiunto, come sopra |
| … di cui da fonti lette in automatico (BUR) | – | **32 avvisi da 6 regioni** | sotto soglia |
| Scadenza corretta (campione di 20 riletti) | ≥ 80% | **13/20 = 65%** | **non raggiunto** |
| Numero posteggi corretto (stesso campione) | ≥ 80% | **11/20 = 55%** | **non raggiunto** |
| Entrambi corretti | – | 8/20 = 40% | – |

**VERDETTO: NON COSTRUIRE** (nella forma del piano: aggregatore nazionale alimentato in automatico dai 20 BUR). Motivi in sez. 7. È un NO con due condizioni precise per riaprire il caso (sez. 7.3).

## 1. Metodo

- Si è ripartiti dal lavoro parziale del commit cc2480d (script per Piemonte, Lazio, Puglia, Toscana, calendari, siti comunali e 70 URL comunali trovati con ricerca web). Gli script sono stati completati, corretti dove perdevano avvisi, e se ne sono aggiunti tre (`bur_altri.py`, `municipium.py`, `consolida.py`).
- Richieste educate: User-Agent `BandiPosteggi-test/0.1 (...)`, una richiesta ogni 1,5 s, download in una cartella fuori dal repository.
- Estrazione di tipo, numero posteggi e scadenza con regole (espressioni regolari) in `comune.py`, **senza correzioni a mano**: i campi `posteggi_auto` e `scadenza_auto` di `avvisi-test.json` sono quelli dell'automatismo.
- Revisione manuale dichiarata in `bandiposteggi/dati/revisione-manuale.json`: 22 candidati scartati (con motivo), correzioni solo di comune/provincia/tipo, e i 20 controlli a campione.
- Regola "avviso del 2026": pubblicato nel 2026, oppure data di pubblicazione ignota e scadenza nel 2026. Avvisi pubblicati nel 2025 per fiere o mercati del 2026 sono stati scartati (8 casi).
- Dati personali: le graduatorie con nomi sono solo linkate; i nomi nelle intestazioni sono omessi; tolti telefoni ed email degli organizzatori dai calendari.

## 2. Tabella delle fonti

| Fonte | URL di partenza | HTTP | Formato | Avvisi 2026 trovati | Difficoltà |
|---|---|---|---|---|---|
| BUR Piemonte, numeri 1–40 | [indice n. 40](https://www.regione.piemonte.it/governo/bollettino/abbonati/2026/40/annunci/index.htm) | 200 (appalti: 404 in 19 numeri = sezione assente) | indice HTML + PDF per annuncio | **3** su 2.895 annunci letti (Cossato, Rivoli, Pinerolo) | facile da leggere; quasi nessun Comune ci pubblica i bandi posteggi (Torino 19 posteggi isolati di ottobre 2026 non c'è) |
| BUR Lazio (sintesi URP), 76 numeri | [sintesi BUR](https://www.regione.lazio.it/urp/sintesi-concorsi-bur?pagina=1) | 200 (76/76) | HTML | **7** (5 Roma Capitale, Castelforte, Sabaudia) | il testo completo è in archivi .rar; termini spesso relativi ("entro 30 giorni dalla pubblicazione") |
| BURP Puglia, 116 numeri | [elenco 2026](https://burp.regione.puglia.it/bollettini) | 200 (116/116) | HTML Liferay + PDF | **4** (Bisceglie, Taranto 128 posteggi, Vieste, Massafra) | la Regione pubblica i bandi comunali in un'unica raccolta semestrale (L.R. 24/2015 art. 30: [BURP n. 41 del 25/5/2026, PDF 23 MB](https://burp.regione.puglia.it/documents/20135/2792459/ATTI_REGIONE.pdf/e3b0959d-2689-44de-6f90-e68b4a77b402?version=1.0&t=1779709206975), "n. 3 bandi"); scadenze relative; "Fiera del Levante" produce falsi positivi |
| BURT Toscana, Parte III, 44 PDF | [consultazione](https://www.regione.toscana.it/burt/consultazione) | 200 (44/44) | PDF del numero intero (73–424 pagine) | **16** | la prima versione (divisione per intestazioni) ne trovava 13 in 1.552 s; la seconda legge il **sommario** e ne trova 16 in 42 s |
| BURERT Emilia-Romagna | [ricerca](https://bur.regione.emilia-romagna.it/ricerca) (POST `/risultati`) | 200 | HTML | **0** | la determinazione annuale dei posteggi liberi non esce dal 2024: ultima è la ricognizione del [BUR n. 299 del 27/9/2024](https://bur.regione.emilia-romagna.it/area-bollettini/n-299-del-27-09-2024-parte-seconda/bollettino_view/++widget++form.widgets.pdf_firmato/@@download), preceduta da due proroghe (BUR 109 e 191 del 2024); nel 2025–2026 nessun titolo o testo con "posteggi" |
| BURL Lombardia | API `PUT /ConsultazioneBurl/api/ricercaAvanzata` su [consultazioniburl.servizirl.it](https://www.consultazioniburl.servizirl.it/ConsultazioneBurl/) | 200 | JSON; il documento è l'intero numero (387 pagine) in base64 | **1** (Borgosatollo, 2 posteggi) | i Comuni lombardi pubblicano quasi solo all'albo |
| BURVET Veneto | [ricerca](https://bur.regione.veneto.it/BurvServices/pubblica/ricerca.aspx) | 200 | ASP.NET (VIEWSTATE) | **1** (Nervesa della Battaglia) | è solo un preavviso: [il bando è all'albo comunale](https://bur.regione.veneto.it/BurvServices/pubblica/DettaglioAvviso.aspx?id=580357), senza numero né scadenza |
| BURAS Sardegna | API Directus `/api/items/inserzione` su [buras.regione.sardegna.it](https://buras.regione.sardegna.it/) | 200 | JSON | **0** | API comoda, ma nessun avviso comunale sui posteggi |
| BURAT Abruzzo | [ricerca "posteggi"](https://bura.regione.abruzzo.it/search/node?keys=posteggi) | 200 | HTML Drupal | **0** nel 2026 (5 tra 2023 e 2025) | i Comuni pubblicano in "Speciali" occasionali |
| BUR Marche | [elenco numeri](https://www.regione.marche.it/Entra-in-Regione/BUR/Ricerca-BUR) | 200 | solo PDF del numero intero, nessuna ricerca | **0** nei 10 numeri campione (N83–N92) | va letto tutto il testo di ogni numero |
| BURC Calabria | burc.regione.calabria.it | https: nessuna risposta; http: 403 | – | non misurabile | non raggiungibile da questo ambiente |
| BUR FVG | bur.regione.fvg.it | 200 "Sito non definito"; vecchio URL 404 | – | non misurato | URL attuale da individuare |
| BURC Campania / GURS Sicilia | burc.regione.campania.it / gurs.regione.sicilia.it | 200 home / 403 | – | non misurati | Napoli dichiara di pubblicare i bandi Califano sul BURC (sotto) |
| Siti comunali (URL da ricerca web) | `bandiposteggi/dati/semi-comuni.tsv` (71 URL) | 65×200 (34 PDF, 31 HTML), 3×403, 1×404, 1×410, 1 file vuoto | PDF/HTML | **52** da 15 regioni | trovati a mano; 8 erano del 2025; 7 non più disponibili o bloccati |
| Municipium: PDF su `<comune>-api.municipiumapp.it` | idem | **24/25 PDF serviti allo script (200)**; 1 file rimosso (307 → `/resize`, 0 byte) | PDF | (compresi sopra) | il test chiesto dal piano è superato: i sottodomini servono i PDF |
| Municipium: elenco "Avvisi" `/it/news?type=3` | 12 Comuni, `bandiposteggi/dati/municipium-test.json` | 12/12 = 200; l'API risponde 401 | HTML a schede | **25 titoli pertinenti** nel 2026 (circa 15 avvisi veri, molti non trovati dalla ricerca web: es. Ragusa chiosco Piazza Matteotti, Trani posteggi fuori mercato 2026, Acquapendente Fiera dei Campanelli) | funziona in 73 s per 12 Comuni; manca l'elenco dei Comuni che usano Municipium |
| Ricerca web per regione (WebSearch) | 9 ricerche il 9/10/2026 (FVG, Umbria, Basilicata/Molise, Campania, Trentino-AA, Veneto, BUR Veneto/Sardegna/Marche) | – | – | **1 URL nuovo** (Montichiari, poi scartato perché del 2025) | i risultati si ripetono: la ricerca restituisce sempre gli stessi ~30 PDF |

## 3. Conteggi finali (`bandiposteggi/dati/avvisi-test.json`)

- Candidati automatici 106 → scartati 22 → **84 avvisi 2026**, **15 regioni**, 60 Comuni diversi (Genova pesa 10 avvisi di spunta per fiere).
- Per regione: Toscana 22, Lombardia 10, Liguria 10, Lazio 9, Puglia 8, Sicilia 5, Piemonte 4, Calabria 4, Veneto 3, Sardegna 3, Emilia-Romagna 2, Campania 1, Marche 1, Abruzzo 1, Valle d'Aosta 1.
- Per fonte: **BUR 32** (Toscana 16, Lazio 7, Puglia 4, Piemonte 3, Lombardia 1, Veneto 1) e **siti comunali 52**.
- Per tipo: fiera 25, mercato 22, spunta/graduatorie 19, posteggi isolati 12, chioschi 5, edicole 1.
- Completezza automatica: numero posteggi presente in 52/84, scadenza presente in 48/84; data di pubblicazione presente per tutti gli avvisi da BUR, per 29/52 di quelli comunali.
- Avvisi ancora aperti al 9/10/2026: 4 (Siena 29/10, Torino 26/10, Aosta 9/12, Modena 18/12).
- Motivi di scarto: 8 pubblicati nel 2025, 6 pagine con HTTP 403/404/410/503 o rimandate alla home, 3 doppioni (stesso avviso su BUR e sito comunale, o due copie dello stesso PDF), 2 falsi positivi del filtro (acqua pubblica, alienazione di un terreno), 2 selezioni di un organizzatore di mercatini, 1 file Municipium rimosso (dettaglio in `revisione-manuale.json`).

## 4. Controllo a campione (20 avvisi riletti sul documento)

Estrazione casuale con seme fisso (`random.seed(20261009)`) tra gli 85 avvisi della bozza; Pontida, risultato pubblicato il 24/11/2025, è stato scartato e sostituito con un'estrazione supplementare (seme 20261010). "Corretto" per gli avvisi di spunta senza domande = l'automatismo non ha inventato nulla.

| # | Avviso | Posteggi (auto) | Posteggi (letti) | OK | Scadenza (auto) | Scadenza (letta) | OK |
|---|---|---|---|---|---|---|---|
| 1 | [Roma](https://www.regione.lazio.it/urp/sintesi-concorsi-bur/sintesi-del-bollettino-ufficiale-n-12-del-10022026) (Lazio, BUR) | – | 16 aree per chioschi ("n. 16 Aree") | **no** | – | non nella sintesi: bando solo nel .rar allegato | **no** |
| 2 | [Bisceglie](https://burp.regione.puglia.it/documents/20135/2792459/ATTI_REGIONE.pdf/e3b0959d-2689-44de-6f90-e68b4a77b402?version=1.0&t=1779709206975) (Puglia, BUR) | 2 | 2 chioschi | sì | 24/07/2026 | 24/07/2026 (60 gg dal BURP del 25/05) | sì |
| 3 | [Vieste](https://burp.regione.puglia.it/documents/20135/2792459/ATTI_REGIONE.pdf/e3b0959d-2689-44de-6f90-e68b4a77b402?version=1.0&t=1779709206975) (Puglia, BUR) | – | 2 box | **no** | – | 24/07/2026 (60 gg) | **no** |
| 4 | [Seravezza, Ripa](https://www.regione.toscana.it/documents/d/guest/parte-iii-n-15-del-15-04-2026) (Toscana, BUR) | 1 | 1 | sì | – | 15/05/2026 (30 gg dal BURT) | **no** |
| 5 | [Siena](https://www.regione.toscana.it/documents/d/guest/parte-iii-n-33-del-19-08-2026) (Toscana, BUR) | 2 | 2 | sì | 21/09/2026 | 21/09/2026 | sì |
| 6 | [Carmignano](https://www.regione.toscana.it/documents/d/guest/parte-iii-n-37-del-16-09-2026) (Toscana, BUR) | 22 | 13 (22 nel regolamento) | **no** | – | 31/10/2026 (45° giorno dal BURT) | **no** |
| 7 | [Lamporecchio](https://www.regione.toscana.it/documents/d/guest/parte-iii-n-8-del-25-02-2026) (Toscana, BUR) | 1 | 1 | sì | – | 06/04/2026 (40° giorno dal BURT) | **no** |
| 8 | [Ossona](https://ossona-api.municipiumapp.it/s3/4850/allegati/avvisoall1.pdf) (Lombardia, Comune) | 2 | non indicato (planimetria) | **no** | 10/07/2026 | 10/07/2026 | sì |
| 9 | [Firenzuola, S. Bartolomeo](https://firenzuola-api.municipiumapp.it/s3/2797/allegati/1-bando-avviso-fiera-di-san-bartolomeo.pdf) (Toscana, Comune) | 39 | 16 liberi (39 in tutto) | **no** | 08/08/2026 | 08/08/2026 | sì |
| 10 | [Firenzuola, Pasquetta](https://firenzuola-api.municipiumapp.it/s3/2797/allegati/1-bando-avviso-fiera-di-pasquetta_signed.pdf) (Toscana, Comune) | 39 | 14 liberi (39 in tutto) | **no** | 12/03/2026 | 12/03/2026 | sì |
| 11 | [Orgiano](https://orgiano-api.municipiumapp.it/s3/4779/allegati/bando-di-gara-26_signed.pdf) (Veneto, Comune) | – | 1 chiosco | **no** | 09/03/2026 | 09/03/2026 | sì |
| 12 | [Genova, Fiera del Mare](https://www.comune.genova.it/novita/avvisi/fiera-del-mare-2026-avviso-agli-operatori-commerciali-e-graduatoria-spuntisti) (Liguria, Comune) | – | non applicabile (spunta) | sì | – | non applicabile (spunta 23/07) | sì |
| 13 | [Genova, S. Salvatore](https://www.comune.genova.it/novita/avvisi/fiera-di-s-salvatore-2026-avviso-agli-operatori-commerciali-e-graduatoria-spuntisti) (Liguria, Comune) | – | non applicabile (spunta) | sì | – | non applicabile (spunta 30/04) | sì |
| 14 | [Acquapendente](https://acquapendente-api.municipiumapp.it/s3/31/allegati/bando-assegnazioni-posteggi-mercato-aprile2026.pdf) (Lazio, Comune) | 9 | 9 | sì | – | 21/05/2026 (data spezzata da un'intestazione di pagina) | **no** |
| 15 | [Catanzaro, Porto Salvo](https://www.comune.catanzaro.it/files/Bandi/Avvisi%20vari/2026/Fiera%20Madonna%20di%20Porto%20Salvo/AVVISO%20PUBBLICO%20FIERA%20MADONNA%20DI%20PORTO%20SALVO.pdf) (Calabria, Comune) | 70 | 70 | sì | 12/07/2026 | 12/07/2026 | sì |
| 16 | [Paola](https://paola-api.municipiumapp.it/s3/4969/allegati/avviso-fiera-maggio_2026_signed.pdf) (Calabria, Comune) | 1 | non indicato (planimetrie) | **no** | 16/03/2026 | 16/03/2026 | sì |
| 17 | [Ragusa](https://www.comune.ragusa.it/en/news/132542/bando-posteggi-piazza-cappuccini) (Sicilia, Comune) | 5 | 5 (dal PDF allegato) | sì | 12/05/2026 | 12/05/2026 | sì |
| 18 | [Sestu, San Gemiliano](https://comune.sestu.ca.it/wp-content/uploads/2026/08/Bando-pubblico-posteggi-San-Gemiliano.pdf) (Sardegna, Comune) | – | non indicato (planimetria) | sì | 24/08/2026 | 24/08/2026 | sì |
| 19 | [Sestu, graduatoria spuntisti](https://comune.sestu.ca.it/wp-content/uploads/2026/02/Det.162_16.02.2026_graduatoria-spuntisti.pdf) (Sardegna, Comune) | 17 | non applicabile (determina di graduatoria) | **no** | 11/02/2026 | non applicabile (domande 21/01–05/02) | **no** |
| 20 | [Modena, fiere 2027](https://www.comune.modena.it/servizi/imprese-e-commercio/commercio-su-area-pubblica-fiera-di-santantonio-e-san-geminiano/allegati/su_det_dete_1811_2026-graduatoria.pdf/@@download/file) (Emilia-Romagna, Comune) | – | non applicabile (spunta) | sì | 18/12/2026 | 18/12/2026 | sì |

**Esito: scadenza 13/20 (65%), numero posteggi 11/20 (55%), entrambi 8/20 (40%).** Contando solo i casi in cui il documento contiene davvero il dato: scadenza 11/16 (69%), posteggi 7/13 (54%).

Tipi di errore, in ordine di frequenza:
1. **Scadenze relative** ("entro 30 giorni / dal 20° al 45° giorno dalla pubblicazione sul BURT/BURP"): 4 casi. La regola per i termini relativi esiste (`comune.scadenza_da_relativa`) ed è usata per la Puglia, ma non nello script del BURT; agganciarla recupererebbe 1–2 casi (stima, non misurata dopo il campione per non adattare le regole al campione): si arriverebbe al 70–75%, sempre sotto l'80%.
2. **Totale invece dei posteggi messi a bando** (39 della fiera invece dei 14–16 liberi; 22 del regolamento invece dei 13 assegnabili): 3 casi.
3. **Numero letto da un'altra frase** ("più di 2 concessioni", ecc.) o **numero scritto in lettere / come "aree", "box", "un chiosco"**: 5 casi.
4. **Atti che non sono bandi** (determina di graduatoria) letti come bandi: 1 caso.
5. **Testo non accessibile** (bando dentro un .rar; divisione sbagliata della raccolta pugliese): 2 casi.

Rileggendo gli stessi 20 documenti, il dato giusto era ricavabile in 19 casi su 20 (manca solo il .rar di Roma). Quindi l'informazione c'è: è l'estrazione automatica a regole che non regge. Un'estrazione fatta da un modello linguistico non è stata misurata in questo test.

## 5. Calendari fieristici (`bandiposteggi/dati/fiere-test.json`, conteggio a parte)

| Regione | Fonte | HTTP | Eventi 2026 | Pertinenza per ambulanti |
|---|---|---|---|---|
| Piemonte | [Calendario regionale 2026, PDF](https://www.regione.piemonte.it/web/media/55082/download) | 200 | 720 (424 sagre e fiere mercato + 296 manifestazioni fieristiche) | alta per le sagre/fiere mercato |
| Emilia-Romagna | [banca dati fiere su aree pubbliche](https://wwwservizi.regione.emilia-romagna.it/sagre/ris_ricerca_sagre.asp?dt_datada=01/01/2026&dt_dataa=31/12/2026) | 200 | 116 | alta |
| Lombardia | allegati A/B/C del decreto 11496 del 4/9/2026 (3° aggiornamento) | 200 | 188 righe | bassa (fiere di settore nei quartieri fieristici); righe non ancora divise in campi |
| Abruzzo | [Allegato A, calendario 2026](https://bura.regione.abruzzo.it/sites/bura.regione.abruzzo.it/files/bollettini/2025-12-05/calendario-regionale-fiere-2026.pdf) | 200 | 9 | bassa |
| Lombardia 2027 | PDF del Dec. 9712 del 17/7/2026 citato nello studio | **404** | – | – |

Totale **1.033 eventi 2026** da 4 regioni (836 pertinenti). Sono date di fiere, non avvisi con scadenze: utili per una pagina "calendario", non sostituiscono i bandi.

## 6. Copertura nazionale raggiungibile in automatico

**Dai BUR**: 32 avvisi in 9 mesi e 1 settimana da 6 regioni, cioè circa **1 avviso a settimana per tutta Italia**. Il motivo è normativo e si vede nei dati:
- I BUR raccolgono soprattutto le **concessioni decennali** dove la legge regionale impone la pubblicazione (Toscana, Puglia, Lazio, in parte Piemonte). Le **fiere temporanee, sagre, spunta, food truck e mercatini**, che sono la maggioranza degli avvisi trovati sui siti comunali (fiera + spunta = 44 su 84), non passano dal BUR nemmeno in Toscana: dei 22 avvisi toscani, i 6 comunali (Firenze, Prato, Carrara, Firenzuola ×2, Sansepolcro) non compaiono nel BURT.
- Nelle altre regioni il BUR è vuoto o quasi: Emilia-Romagna 0 (determinazione annuale sospesa dal 2024), Lombardia 1, Veneto 1 preavviso senza dati, Sardegna 0, Abruzzo 0, Marche 0 sul campione; Liguria, Sicilia, Calabria, Campania, Umbria non sono stati misurati o non sono raggiungibili. Liguria (10 avvisi di Genova), Sicilia (5), Calabria (4) e Lombardia (9) arrivano solo dai siti comunali.
- Ordine di grandezza del flusso reale: se anche solo un Comune su due (≈ 3.950 su ≈ 7.900) pubblicasse un avviso all'anno tra fiera, sagra, spunta o posteggio libero, il flusso sarebbe ≈ 4.000 avvisi/anno contro ≈ 45/anno dai BUR: **copertura automatica dai soli BUR ≈ 1% (al massimo qualche punto percentuale anche con ipotesi molto prudenti)**. Questa è una stima con l'assunzione dichiarata, non un dato.

**Dai siti comunali**:
- La ricerca web non è una fonte automatizzabile: 9 ricerche mirate per regione hanno restituito sempre gli stessi ~30 documenti (1 URL nuovo, del 2025). Inoltre 15 dei 71 URL erano del 2025 o non più raggiungibili.
- L'elenco "Avvisi" dei siti **Municipium** invece si legge bene: su 12 Comuni, 25 titoli pertinenti nel 2026 (≈ 15 avvisi veri) in 73 secondi, molti assenti dalla ricerca web. Estrapolazione prudente (i 12 Comuni sono stati scelti perché avevano già un avviso, quindi sovrastimano): **0,5–1 avviso vero per Comune Municipium ogni 9 mesi**. Con ~1.000 Comuni Municipium (dato dello studio) sarebbero ≈ 10–25 avvisi/settimana, da 1.000 richieste a settimana (≈ 25 minuti). **Manca però l'elenco dei Comuni che usano Municipium**: andrebbe costruito sondando i ≈ 7.900 siti comunali (una volta, ≈ 3,5 ore di richieste), cosa non fatta in questo test. Con lo stesso metodo andrebbe provato il modello AGID "design comuni" (`/novita/avvisi`, usato da Genova, Pontida, Modugno, Castelfranco Veneto…), non misurato.
- Stima complessiva, se i due crawler di CMS funzionassero sull'elenco completo: **20–35% del flusso nazionale**, concentrato al Nord e nei Comuni medio-grandi; resterebbero fuori i Comuni con siti fatti a mano o albo pretorio in PDF (es. Catanzaro, Palermo, Sestu, Castrovillari tra quelli trovati).

## 7. Verdetto contro la soglia

### 7.1 VERDETTO: NON COSTRUIRE

1. **L'accuratezza è sotto soglia**: 65% sulle scadenze e 55% sui posteggi contro l'80% richiesto. Il piano prevedeva di fermarsi sotto il 50%: siamo tra 50% e 80%, ma una pagina con 4 avvisi su 10 sbagliati su scadenza o numero non è pubblicabile, perché la scadenza è il dato per cui l'ambulante pagherebbe.
2. **Il volume oltre la soglia viene dal lavoro manuale**: 52 degli 84 avvisi sono stati trovati con ricerche web fatte a mano, che non si ripetono ogni settimana in automatico. Le fonti automatiche (BUR) danno 32 avvisi da 6 regioni in 9 mesi: sotto i 60 da 8 regioni.
3. **L'ipotesi centrale dello studio è smentita**: "in Piemonte ogni bando comunale è pubblicato per estratto sul BUR" e "in Emilia-Romagna la Regione pubblica ogni settembre una determinazione unica" non valgono nel 2026 (3 avvisi in 40 numeri piemontesi; nessuna determinazione ER nel 2025–2026).

"COSTRUIRE SOLO PER LE REGIONI X" è stato valutato e scartato: la sola regione dove l'automatismo funziona bene è la **Toscana** (BURT letto dal sommario, 16 avvisi, 42 secondi), ma 16 avvisi in 9 mesi (≈ 2 al mese) sono troppo pochi per un sito e per un abbonamento; Lazio (7) e Puglia (4 in una raccolta semestrale) aggiungono poco.

### 7.2 Cosa resta utile
- Il calendario fiere e sagre di Piemonte ed Emilia-Romagna (836 eventi pertinenti, fonti ufficiali stabili) corrisponde all'ipotesi **PIVOT** della sezione 6 dello studio (solo fiere/sagre/eventi). Non è stato testato se porta traffico.
- Gli script restano pronti: BURT dal sommario, raccolta pugliese, API BURL e BURAS, crawler Municipium.

### 7.3 Condizioni per riaprire il caso (test da fare, entrambi a costo zero)
1. **Estrazione con modello linguistico** sugli stessi 20 documenti più 20 nuovi: si riapre se scadenza e posteggi sono corretti in ≥ 80% (sui 20 riletti qui il dato era ricavabile in 19 casi).
2. **Elenco dei Comuni Municipium e AGID** (sondaggio una tantum dei siti comunali) e crawler settimanale: si riapre se dà ≥ 25 avvisi veri a settimana da ≥ 10 regioni per 4 settimane di fila.

## 8. Ore di manutenzione settimanale (stima)

| Scenario | Lavoro settimanale | Ore/settimana |
|---|---|---|
| Solo BUR (come testato) | esecuzione automatica (≈ 15 min di macchina), rilettura di ≈ 1–2 avvisi, correzione degli script quando un BUR cambia formato (già visto: Toscana con PDF "compressed", Lombardia SPA con API, Veneto ASP.NET; stimo 1–2 rotture al mese su 6–8 fonti, 1–2 h l'una) | **0,5–1 h**, ma con ≈ 1 avviso/settimana: inutile |
| BUR + crawler Municipium/AGID su ≈ 1.000–2.000 Comuni | ≈ 50–110 titoli/settimana da filtrare (la metà circa falsi positivi, dal test Municipium), ≈ 25–55 avvisi da verificare: con estrazione a regole servono 2–3 minuti di rilettura ciascuno perché il 35–45% è sbagliato; più manutenzione dei crawler | **3–5 h** |
| Come sopra con estrazione da modello linguistico ≥ 80% (non misurata) | controllo a campione e casi dubbi | **1,5–2,5 h** |

Il vincolo "lavoro umano quasi zero" (condizione 5 dello studio) sarebbe rispettato solo nel terzo scenario, che oggi non è dimostrato.

## 9. File consegnati e come rieseguire

- `bandiposteggi/dati/avvisi-test.json`: 84 avvisi con comune, provincia, regione, tipo, posteggi_auto, data_pubblicazione, scadenza_auto, URL ufficiale, fonte (BUR/Comune), come è stato trovato, data di verifica; 20 con `verifica_a_campione`; 22 scartati con motivo.
- `bandiposteggi/dati/fiere-test.json`: 1.033 eventi dai calendari regionali, con fonti e note.
- `bandiposteggi/dati/revisione-manuale.json`: esclusioni, correzioni anagrafiche e controlli a campione.
- `bandiposteggi/dati/bur-ricerche-test.json`, `municipium-test.json`, `municipium-domini.txt`, `semi-comuni.tsv`: evidenze delle ricerche.
- `bandiposteggi/raccolta/`: `comune.py` (download educato, testo PDF, regole di estrazione, termini relativi), `bur_piemonte.py`, `bur_lazio.py`, `bur_puglia.py` (con divisione della raccolta regionale), `bur_toscana.py` (dal sommario), `bur_altri.py` (Emilia-Romagna, Lombardia, Veneto, Sardegna, Abruzzo, Marche), `comuni_web.py`, `municipium.py`, `calendari.py`, `consolida.py`. Ogni script ha l'uso nella docstring; tutti vanno eseguiti con `python3 -I` e una cartella di download fuori dal repository. Tempo totale di un giro completo con i PDF già in cache: ≈ 30 minuti (Piemonte ≈ 10, BUR con ricerca ≈ 6, comuni ≈ 6, Puglia ≈ 3, Lazio ≈ 2, il resto ≈ 1 ciascuno).
