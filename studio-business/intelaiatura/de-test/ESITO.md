# Test Germania: date delle Prüfstellen leggibili da programma (30/10/2026)

Test della ricerca `ricerca-cloni-esameb1-2026-10-30.md`, sezione 3.1. Serviva a decidere se il clone tedesco di EsameB1 sale da 7,5 a 8.

## Verdetto: NON PASSA

| Condizione per l'8 | Soglia | Risultato | Esito |
|---|---|---|---|
| Prüfstellen con date future leggibili da programma nelle 20 città più cercate | almeno 60 | **31** su 85 (30 siti diversi). Con il solo DTZ si arriva a 32 | **NO** |
| Licenza del portale servizi di Berlino | compatibile | Si possono usare solo fatti e link, con un programma che si presenta col suo nome. Il problema è un altro: **le pagine del portale non hanno date** | in parte |
| Data giusta nei controlli a mano | almeno 90 % su 30 | **27 su 30 (90 %)**, proprio sulla soglia | sì, al limite |

La soglia non si raggiunge neanche con strumenti migliori. Nelle 20 città le Prüfstellen sono solo 85, quindi ne servirebbero 71 su 100. Anche aggiungendo:
- un browser vero per i 5 siti che caricano i dati con JavaScript,
- il permesso dei 3 siti che bloccano i programmi nel robots.txt,
- qualche pagina in più trovata a mano,

si arriva al massimo a circa **45**. Mi sono fermato a circa 2,5 ore di lavoro.

**Proposta:** il voto non sale a 8. Lo abbasserei a **7**. Le date si leggono per poco più di un terzo delle sedi, e a Berlino (seconda città per domanda) solo per 2 sedi su 12.

---

## 1. Elenco delle sedi (BAMF)

- **Fonte:** 16 pagine `bamf.de/SharedDocs/Anlagen/DE/Integration/Einbuergerung/Pruefstellen-<LAND>.html`, tutte HTTP 200. Ogni pagina linka un file XLSX, anche questo HTTP 200 (29-92 KB). Le versioni cambiano da Land a Land (da `v=6` a `v=77`): i file vengono aggiornati uno per uno.
- **Formato:** un foglio per file. L'intestazione è alla riga 9-10 e il nome della colonna cambia: "Name der Prüfstelle" oppure "Namen der Prüfstelle". Colonne: Kreis, PLZ, Ort, nome, via, telefono, email. **Nessuna data.**
- **Totale: 663 Prüfstellen** in Germania. Le più numerose: NRW 176, Baviera 116, Bassa Sassonia 71, Baden-Württemberg 66, Assia 60, Renania-Palatinato 53. Turingia, Schleswig-Holstein e Brema hanno 1-4 righe ciascuno (spesso l'associazione regionale delle VHS per tutto il Land).
- **Note legali:** nell'Impressum del BAMF i diritti riservati riguardano **solo le immagini**. Non c'è una licenza aperta esplicita (né CC né DL-DE), ma non c'è nemmeno un divieto sui testi o sugli elenchi. Rischio basso, con la fonte citata.
- **Attenzione:** molte email sono personali (nome.cognome@...). Nel file dati tengo solo il dominio dell'email, che serve a trovare il sito della sede. Gli XLSX non sono salvati nel repository.

## 2. Le 20 città più cercate

Ho interrogato l'autocomplete tedesco (gl=de, hl=de) su 55 città, con "einbürgerungstest termine <città>" e "dtz prüfung termine <città>". Ho aggiunto l'espansione lettera per lettera (a-z) delle due frasi. Il punteggio somma i suggerimenti ricevuti e la presenza tra i primi 10.

**Classifica:** Hamburg, Berlin, Frankfurt, München, Köln, Stuttgart, Essen, Leipzig, Ulm, Düsseldorf, Hannover, Nürnberg, Mannheim, Karlsruhe, Wiesbaden, Erfurt, Regensburg, Dortmund, Augsburg, Chemnitz.

Subito dopo vengono Freiburg, Potsdam, Saarbrücken, Bonn e Bremen. Ulm entra perché per la "u" ci sono poche città in concorrenza: l'espansione per lettera la favorisce un po'.

In queste 20 città ci sono **85 Prüfstellen**. Molte città ne hanno 1 o 2: Stuttgart, Ulm, Karlsruhe, Regensburg e Augsburg una sola; Essen, Nürnberg, Mannheim, Erfurt e Dortmund due.

## 3. Quante sedi pubblicano le date in HTML

**Metodo:**
- user-agent di un browser normale; per berlin.de, un user-agent che dichiara il programma, come chiedono le condizioni del portale;
- robots.txt rispettato e pausa tra una richiesta e l'altra;
- nessun aggiramento dei blocchi (429, 403, anti-robot);
- solo HTML, niente PDF;
- conta una sede se sulla sua pagina c'è almeno una data **futura** (31/10/2026-31/12/2027) di un Einbürgerungstest, di un test "Leben in Deutschland" o di un DTZ.

| Città | Prüfstellen | con date EBT/LiD | con date EBT o DTZ |
|---|---|---|---|
| Hamburg | 9 | 3 | 4 |
| Berlin | 12 | 2 | 2 |
| Frankfurt | 6 | 1 | 1 |
| München | 7 | 2 | 2 |
| Köln | 4 | 3 | 3 |
| Stuttgart | 1 | 1 | 1 |
| Essen | 2 | 1 | 1 |
| Leipzig | 6 | 3 | 3 |
| Ulm | 1 | 1 | 1 |
| Düsseldorf | 8 | 4 | 4 |
| Hannover | 7 | 4 | 4 |
| Nürnberg | 2 | 0 | 0 |
| Mannheim | 2 | 1 | 1 |
| Karlsruhe | 1 | 0 | 0 |
| Wiesbaden | 5 | 2 | 2 |
| Erfurt | 2 | 0 | 0 |
| Regensburg | 1 | 0 | 0 |
| Dortmund | 2 | 1 | 1 |
| Augsburg | 1 | 0 | 0 |
| Chemnitz | 6 | 2 | 2 |
| **Totale** | **85** | **31** | **32** |

Le 31 comprendono due righe BAMF della stessa scuola di Düsseldorf, quindi i siti diversi sono 30.

**Perché le altre 53 non hanno date leggibili:**
- **26: la data non è pubblicata, oppure la pagina del test non c'è.** Alcuni esempi:
  - Karlsruhe dà la data solo allo sportello, al momento dell'iscrizione;
  - Essen smette di fare il test da febbraio 2027;
  - Dortmund pubblica solo le finestre di prenotazione del mese, non i giorni del test;
  - Berlitz Hannover non compare sulla pagina nazionale di Berlitz;
  - poi diverse scuole private senza calendario online.
- **10 a Berlino:** il portale centrale delle VHS dice che ci si iscrive solo prendendo un appuntamento su service.berlin.de. Il sistema di prenotazione è vietato ai programmi dal robots.txt ed escluso per usi commerciali. Le 13 pagine per sede del portale servizi (tutte HTTP 200) **non contengono nessuna data**. Solo Pankow e Treptow-Köpenick scrivono la prossima data sulla loro pagina.
- **9 senza sito o non raggiungibili:** 3 non hanno un sito (email generica o nessuna email); 6 rispondono con un errore o con un rinvio ad altro.
- **5 caricano i dati con JavaScript** (l'HTML è vuoto): VHS Frankfurt, VHS Augsburg, VHS Regensburg e due scuole private.
- **3 vietano i programmi nel robots.txt** (`Disallow: /` per tutti): la VHS Düsseldorf (sito del Comune) e le due sedi dello stesso istituto a Erfurt e Chemnitz. Le date ci sono, ma non le ho lette.

## 3b. L'estrattore e i formati coperti

`estrai_date.py` legge la pagina di ogni sede e prende le date che appartengono a una "voce" sul test:
- il titolo prima della data ("Einbürgerungstest … Do. 26.11.2026") oppure dopo ("14.01.2027: Einbürgerungstest");
- le date in fila ereditano l'intestazione dell'elenco ("Unsere nächsten Termine: …");
- le date precedute da "Anmeldeschluss", "Anmeldung bis" o "Meldefrist" sono marcate come scadenze, non come esami;
- le date di corsi e di altri esami (Integrationskurs, telc B2, Goethe, TestAS) vengono scartate.

| Formato | Sedi con date |
|---|---|
| Pagina del sito (WordPress, TYPO3…) con testo libero | 16 |
| KuferWeb (catalogo corsi delle VHS: indirizzi `/kategorie/…`, `/kurs/<titolo>/<n>`) | 9 |
| Kursportal VHS (itemKG / Kufer SQL: indirizzi `…-CAT-KAT…`, `…-C-…`) | 2 |
| Portale berlin.de (testo libero) | 2 |
| Elenco per città di una catena (Berlitz) | 2 |
| Altro catalogo corsi VHS (Hamburg) | 1 |

Il formato più comune è il **testo libero**, diverso da sito a sito, non un sistema di prenotazione unico. KuferWeb e Kursportal insieme coprono 11 sedi. Un lettore "per formato" porta poco: quasi metà delle sedi con date ha una pagina fatta a mano. Per 10 sedi ho dovuto indicare a mano l'indirizzo della pagina giusta, perché i link dalla home non portavano lì.

**30 controlli a mano** (`grezzi/controlli_30.json`, almeno una data per sede): 27 giuste. I 3 errori:
- la data di apertura delle iscrizioni presa per data del test;
- un esame telc B2 preso per Einbürgerungstest, perché l'estrattore ha letto il titolo della voce successiva;
- la fine di una finestra di prenotazione presa per data d'esame (Dortmund, tolta dal conteggio).

Sono errori correggibili, ma dicono che ogni sito chiede regole sue.

## 4. Licenze e condizioni d'uso

Valutazione di buon senso, non un parere legale. In Germania una data presa da sola non è protetta dal diritto d'autore. Lo sono i testi, le foto e l'impaginazione. Le banche dati sono protette solo se se ne copia una parte sostanziale.

| Fonte | Cosa dice | Uso commerciale di date con link |
|---|---|---|
| BAMF (elenco sedi) | Diritti riservati solo sulle immagini | **Sì**, con la fonte |
| berlin.de e service.berlin.de (robots.txt con condizioni) | I programmi devono dichiararsi nello user-agent e rispettare il robots.txt; possono essere bloccati in qualsiasi momento. Prenotazioni vietate ai programmi e "nicht zu kommerziellen Zwecken" | **Sì per i fatti con link**, con un programma che si dichiara. Ma non ci sono date da prendere |
| VHS Berlin (Impressum) | Testi, foto e "Sammlung der Beiträge" protetti; uso "solo nei limiti di legge". Nessuna licenza | Solo fatti e link, niente testi copiati |
| telc | "Downloads und Kopien … nur für den privaten, nicht kommerziellen Gebrauch" | **No** per copiare contenuti; telc non pubblica comunque date per sede |
| Münchner VHS | Copia o uso di "Teilen davon" in altre pubblicazioni solo con il loro consenso | Solo la data e il link; meglio chiedere il permesso |
| VHS Stuttgart | Le informazioni "dürfen gespeichert, weitergegeben und vervielfältigt werden", senza modifiche e con la fonte | **Sì** |

In sintesi: date e link sono possibili quasi ovunque. La licenza però non è il problema principale. Il problema è che **le date non ci sono**, oppure non si leggono senza browser o senza permesso, per due sedi su tre.

## 5. Cosa resta da fare (proposta)

1. Aggiornare la ricerca e il registro ESPLORATE. Proposta di riga: "Einbürgerungstest + B1 per città (DE): test date NON PASSATO (31 Prüfstellen su 85 con date leggibili, soglia 60) → voto 7".
2. Non costruire il sito tedesco come clone pieno. Se un giorno si libera un posto, la versione possibile è più povera:
   - pagine città con le sedi del BAMF;
   - la data dove la sede la pubblica (circa 1 su 3);
   - "come iscriversi" per ogni sede;
   - "avvisami".
   Ma è proprio la "risposta a metà" che la ricerca considerava non sufficiente.
3. Non serve creare un dominio .netlify.app nuovo: il test non è passato.

## File

| File | Contenuto |
|---|---|
| `leggi_bamf.py` | Legge i 16 XLSX del BAMF e scrive `grezzi/sedi_bamf.json` (663 sedi; dell'email solo il dominio) |
| `citta_autocomplete.py` | Classifica delle città dall'autocomplete; risultati in `grezzi/autocomplete/` |
| `sedi_top20.py` | Le 85 sedi delle 20 città, con l'indirizzo di partenza → `grezzi/sedi_top20.json` |
| `cerca_date.py` | Cerca la pagina del test su ogni sito (due passate: `grezzi/date_passata1/`, `grezzi/date/`) |
| `estrai_date.py` | Estrattore finale → `grezzi/estratte.json` (date per sede, formato, pagina fonte) |
| `grezzi/controlli_30.json` | I 30 controlli a mano |
| `grezzi/pagine_scaricate.json` | Elenco delle pagine BAMF e Berlino lette. L'HTML è stato cancellato perché conteneva i contatti del personale |

Nessun file contiene il testo intorno alle date: può contenere nomi di docenti o di impiegati.
