# Scheda: formato «citabile» sulle pagine di EsameB1 che ChatGPT cita già — 27/11/2026

Origine: esperimento di Visa Income (`intelaiatura/esperimento-citazioni-2026-10-31.md`): le 36 pagine con data visibile, `dateModified` e riquadro di cifre ufficiali con fonte hanno avuto 121 visite da ChatGPT contro 46 delle 36 di controllo (1–26/11; rapporto 2,63, corretto per la partenza 1,94; 138 contro 54 contando anche il vecchio indirizzo). Non è ancora il verdetto (28/12).

1. **Obiettivo.** Più visite da ChatGPT sulle pagine di EsameB1 dove una visita vale di più (libro e Pass), e una prova pulita che il formato funziona anche qui. Attese sulle 4 pagine trattate con visite: da +18 a +66 visite a settimana (punto 2); se la prova passa e il formato va anche sulle 3 pagine tenute fuori: da +24 a +91. Nel conto di `PIANO-FATTURATO.md` (sez. 7, punto 5) 100 visite a settimana in più su EsameB1 valgono 132 € l'anno: da 32 a 120 € l'anno a formato esteso. Tappa 2 (AdSense su esameb1.eu) e canale n. 1 (libro).

2. **Dati (GoatCounter, API di sola lettura, letti il 27/11/2026; somma dei due host `esameb1.eu` ed `esameb1.netlify.app`, dove non è scritto altro).**
   - Solo `esameb1.eu`, 20/10–26/11: 1.363 visite a pagine; da ChatGPT 319; da Google 428. Vecchio indirizzo nello stesso periodo: 883 visite, almeno 69 da ChatGPT (prime 45 pagine).
   - Ultimi 14 giorni (13–26/11), due host: 879 visite (440 a settimana), 250 da ChatGPT (125 a settimana, il 28%), 237 da Google.
   - **ChatGPT va quasi solo nella sezione `/esempi/`; Google va sulle pagine città, sulla home e su `/ente/cils/`.** Nelle pagine `/esempi/` scelte Google porta 0 visite: cambiare queste pagine non tocca il recupero di Google.
   - Settimane, visite da ChatGPT (trattate nel verdetto / controllo / resto del sito): 6–12/11 38 / 11 / 33 · 13–19/11 57 / 25 / 31 · 20–26/11 83 / 28 / 25. **Le pagine degli esempi crescevano già da sole; il resto è fermo.** Per questo serve un gruppo di controllo.
   - Clic sul libro dalle pagine `/esempi/` nei 14 giorni di base: 1 (`clic/libro-esempi`); sul Pass 0. Troppo pochi per farne una soglia: si leggono ogni lunedì, senza regola.

   **Tre gruppi** (`esameb1/dati/citabile.json`). Guadagno atteso a settimana in tre ipotesi: prudente +25% (qui le pagine hanno già fonte e data nel primo paragrafo), soglia di Visa +50%, effetto di Visa corretto +94%.

   | Gruppo | Pagina | Visite 20/10–26/11 su esameb1.eu (ChatGPT / Google) | Base 13–26/11: visite / ChatGPT | ChatGPT a settimana | +25% | +50% | +94% |
   |---|---|---|---|---|---|---|---|
   | Trattata, nel verdetto | `/esempi/cils/` | 162 (93 / 0) | 135 / 79 | 39,5 | +9,9 | +19,8 | +37,1 |
   | Trattata, nel verdetto | `/esempi/` | 92 (56 / 0) | 76 / 49 | 24,5 | +6,1 | +12,3 | +23,0 |
   | Trattata, nel verdetto | `/esempi/celi/` | 32 (19 / 0) | 20 / 10 | 5,0 | +1,3 | +2,5 | +4,7 |
   | Trattata, nel verdetto | `/esempi/certit/` | 10 (3 / 0) | 9 / 2 | 1,0 | +0,3 | +0,5 | +0,9 |
   | | **Totale trattate nel verdetto** | | **240 / 140** | **70,0** | **+18** | **+35** | **+66** |
   | Trattata, fuori dal verdetto | `/esempi/a1/`, `/esempi/c1/`, `/esempi/c2/`, `/esempi/cils-b1-standard/` (nate il 25/11) | 0–1 (1 in tutto / 0) | 2 / 1 | 0,5 | — | — | — |
   | Controllo (senza formato) | `/esempi/plida/` | 48 (33 / 0) | 35 / 24 | 12,0 | (+3,0) | (+6,0) | (+11,3) |
   | Controllo (senza formato) | `/esempi/b2/` | 20 (19 / 0) | 20 / 19 | 9,5 | (+2,4) | (+4,8) | (+8,9) |
   | Controllo (senza formato) | `/esempi/a2/` | 12 (10 / 0) | 12 / 10 | 5,0 | (+1,3) | (+2,5) | (+4,7) |
   | | **Totale controllo** | | **67 / 53** | **26,5** | (+7) | (+13) | (+25) |

   Tra parentesi: guadagno che arriva solo dopo il 28/12, se la prova passa. Trattate nel verdetto più controllo fanno il 77% delle visite da ChatGPT del sito (193 su 250).
   **Perché queste tre di controllo:** una per tipo di pagina (un ente B1: PLIDA; due livelli: A2 e B2), abbastanza visite per leggere una differenza (53 in 14 giorni), e le due pagine più forti (CILS e indice) restano trattate.
   **Scartate, con il motivo:** `/citta/milano/` (17 da ChatGPT ma 100 da Google nei due indirizzi: pagina di Google in recupero, non si tocca), `/ente/cils/` (5 da ChatGPT, 52 da Google: idem), home (5), `/esempi/confronto/` (0 da ChatGPT, è già una tabella), `/esempi/celi-2/`, `/esempi/ascolto/`, `/esempi/prova-orale/` (0 visite, pagine del 26/11 con dati «non aperti»: la regola non darebbe frasi sicure), pagine in inglese (4).

3. **Regole fisse toccate.** Decisioni con i dati (numeri sopra); niente riscrittura di massa dei titoli (titolo, H1, description e indirizzo uguali, controllati da `verifica.py`); niente noindex; forma editoriale e cancello AdSense invariati; riquadri del libro e del Pass al loro posto; `lastmod` solo per cambi veri; solo dati già nel sito con fonte ufficiale e data; italiano semplice; nessun nome di modello; nessun dato personale; un solo agente; nessuna spesa; una pubblicazione Netlify.

4. **Errori già fatti da non ripetere** (`REGISTRO-RISCHI-ERRORI.md`): `lastmod` mosso da una data di controllo (25/11) → la data «Pagina aggiornata il» e `dateModified` sono fuori dall'impronta, e sono la data del registro; riquadri che spostano la data di molte pagine → cambiano solo le 8 pagine trattate (prova: `git status`, 8 file più `sitemap-esempi.xml`; le 3 di controllo uguali a prima byte per byte, con la loro data di prima); testo più largo delle fonti → nessuna frase scritta a mano per pagina, tre regole che copiano i dati; decisioni senza misura → linea di base e gruppo di controllo scritti in `dati/citabile.json` prima di pubblicare.

5. **Variabili esterne.** ChatGPT può cambiare da solo quali pagine cita (le pagine degli esempi crescevano già); la stagione d'esame (gennaio-febbraio) alza tutte le visite: tutte e due le cose toccano trattate e controllo allo stesso modo, per questo il verdetto è un rapporto tra i due. Google in recupero (non toccato: 0 visite da Google su queste pagine). Se un ente cambia un dato, il riquadro cambia da solo alla prossima raccolta e la data si muove (cambio vero). **Fino al 28/12 non si cambiano le 3 pagine di controllo né le 4 trattate del verdetto**, salvo aggiornamenti dei dati uguali per tutte.

6. **Cosa non tocco.** Titoli, H1, description, indirizzi, robots, sitemap (solo le date delle 8 pagine), le 3 pagine di controllo, pagine città, pagine ente, home, sezioni in inglese, ucraino e rumeno, altri siti, `genera_dopo.py`, `genera_livelli.py`, riquadri del libro e del Pass, cancello AdSense.

7. **Misura.**
   - Costruzione: `cd esameb1 && python3 genera.py && python3 verifica.py` → 0 errori, riga «formato citabile: 8 pagine…»; `python3 studio-business/strumenti/monetizzazione.py verifica esameb1` → 0 errori; seconda generazione identica byte per byte; Playwright 390 e 1280 su `/esempi/cils/`, `/esempi/` e `/esempi/cils-b1-standard/`: nessuno scorrimento orizzontale (anche con la tabella aperta), nessun errore JS.
   - Risultato: **ogni lunedì** `python3 esameb1/raccolta/citabile.py --dal <lunedì> --al <domenica>`. Conta, sui due host, le visite da `chatgpt.com` di: trattate nel verdetto, controllo, trattate nate il 25/11 (a parte), resto del sito; poi pagina per pagina con le visite da Google, e i clic sul libro e sul Pass (`clic/libro-esempi`, `clic/libro-livelli`, `clic/pass-prezzo` e gli altri).
   - **Numero del verdetto = crescita delle trattate ÷ crescita del controllo**, tutte e due rispetto alla stessa base 13–26/11 (70,0 e 26,5 a settimana). Esempio: trattate 105 a settimana (× 1,5) e controllo 26,5 (× 1,0) → 1,5.
   - **Attenzione nel leggere il sì:** già prima del cambio le trattate salivano più in fretta del controllo (nell'ultima settimana × 1,19 contro × 1,06 sulla base: rapporto circa 1,1 senza nessun effetto). Un risultato appena sopra 1,5 va letto con prudenza: può essere in parte questa tendenza.
   - **Quanto si muove da solo, prima del formato:** lo stesso numero nelle tre settimane prima è stato 1,31 · 0,86 · 1,12. Una settimana sola non dice niente: si guarda la media di 4 settimane.
   - **Limite onesto:** il controllo sono 3 pagine con 26,5 visite a settimana, non assegnate a caso; la prova vede solo effetti grandi. La prova di causa più forte resta l'esperimento di Visa (verdetto 28/12).

8. **Fatto e stop.**
   - Fatto: 8 pagine online con riquadro, data e `dateModified`; 3 pagine di controllo uguali a prima; controlli a 0; `pubblicato_il` scritto in `dati/citabile.json`.
   - Prima lettura lunedì 7/12 (settimana 30/11–6/12). Verdetto **lunedì 28/12** sulle 4 settimane 30/11–27/12 insieme (se si pubblica dopo il 29/11: 4 settimane piene dal lunedì dopo).
   - **Sì:** crescita trattate ÷ crescita controllo ≥ 1,5 sulle 4 settimane **e** almeno +20 visite a settimana attribuibili al formato (trattate − 70 × crescita del controllo; lo stampa lo script). Allora il formato va sulle 3 pagine di controllo (basta spostare le loro voci da «controllo» a «pagine» in `dati/citabile.json`) e, se anche Visa dice sì, su `/ente/`, `/risultati/`, `/costo/`.
   - **In mezzo (tra 0,7 e 1,5):** il formato resta dove è (serve ai lettori), non si estende; le 3 di controllo restano come sono.
   - **Stop:** rapporto sotto 0,7 per 2 settimane di fila con il controllo ad almeno 15 visite a settimana → `"attivo": false` in `dati/citabile.json` e si rigenera.
   - Le 4 pagine nate il 25/11 non entrano in nessuna soglia: si riportano a parte.

9. **Costo.** Un agente, circa 4 ore; 1 pubblicazione Netlify (8 pagine più una sitemap); nessuna spesa.

10. **Dopo la pubblicazione.** Controllo online di 2 pagine trattate e 1 di controllo (riquadro, data, JSON-LD; controllo senza riquadro), IndexNow per le 8 pagine, `salute.py`, riga in `DA-PUBBLICARE.md`, `pubblicato_il` in `dati/citabile.json`, lettura ogni lunedì insieme al Pass.

Chiusura: (da spuntare dopo la pubblicazione)

## Cosa è il formato, qui

Uguale in tutte le 8 pagine, scritto da tre regole in `esameb1/genera.py` (blocco «formato citabile»), elenco delle pagine in `esameb1/dati/citabile.json`:

1. Riquadro «… i dati ufficiali in breve» subito sotto il titolo (nelle pagine degli enti prende il posto delle tre schede «Quanto dura / Per superare / Se non superi una parte», che dicevano le stesse cose senza fonte).
2. Riga «Pagina aggiornata il <data> · Dati: <ente (sigla)> · fonti ufficiali e date dei controlli nella tabella». La data è quella del registro `dati/lastmod.json`, la stessa della sitemap: si muove solo se il contenuto cambia.
3. Una frase di risposta. Pagine degli enti: «In breve: il CILS B1 Cittadinanza dura… Per superare serve… Se non superi una parte, … Costa…». Indice: i 4 esami con i loro file. Pagine dei livelli: quanti file con link diretto e per quali esami il link porta alla pagina dell'ente (non ripete il primo paragrafo); con un esame solo non c'è frase.
4. Tabella: un dato per riga, con i link alle fonti ufficiali (senza doppi) e «controllato il <data>» in ogni riga. Regola `ente_b1`: esempio, durata, punteggio, recupero, costo, risultati (`dati/enti.json`, `dati/risultati.json`, `dati/esempi.json`). Regola `indice_b1`: una riga per ente, con le fonti di esempio, durata, costo e risultati. Regola `file`: una riga per gruppo di file ufficiali (`dati/esempi_livelli.json`, `dati/dopo_esame.json`). Su telefono la tabella è chiusa e si apre con un tocco; su schermo largo è aperta. Con una riga sola è sempre aperta, senza comando.
5. `dateModified` in un nodo `WebPage` del JSON-LD (dopo il `FAQPage`, che resta il primo), con `isBasedOn` = le fonti del riquadro.

## Deviazioni

1. **8 pagine trattate, non 10-20.** Solo 7 pagine hanno visite da ChatGPT misurabili; 3 di queste sono tenute fuori come controllo (revisione del 27/11), 4 sono dello stesso tipo e nuove. Le pagine con visite da Google sono state lasciate fuori apposta.
2. **Niente CSV e niente schema `Dataset`** (c'erano nel formato di Visa): qui i dati sono testi e link a file degli enti, non una serie di numeri. L'esperimento di Visa non dice quale pezzo del formato ha fatto l'effetto: se era il CSV, qui l'effetto sarà più piccolo.
3. **Gruppo di controllo scelto, non tirato a sorte:** `/esempi/plida/`, `/esempi/b2/`, `/esempi/a2/`. Restano come nell'ultimo commit, byte per byte; il loro `lastmod` è tornato alla data di prima (19/11, 26/11, 26/11) rimettendo nel registro la voce dell'ultimo commit. Costo della prova: fino a +7/+25 visite a settimana rimandate di un mese.
4. **Le tre schede «in breve» delle pagine degli enti trattate sono state sostituite dal riquadro**, non lasciate accanto: stessi tre dati, ora con fonte e data, più costo e risultati. Il riquadro del Pass resta subito dopo, come prima. Nella pagina PLIDA (controllo) le schede restano.
5. **Tabella chiusa su telefono.** Aperta era alta circa 1.400 px e spingeva in basso i file, il libro e il Pass; chiusa il riquadro è alto circa 420 px. Il testo è comunque tutto nell'HTML.
6. **Titolo, H1 e description di oggi sono copiati in `dati/citabile.json`** e `verifica.py` segnala se cambiano. Per un cambio voluto di titolo su una di queste pagine va aggiornata lì la voce.
7. **Nelle voci A2 e B2 (oggi controllo) il nome dell'esame e l'ente dei gruppi di file sono scritti in `dati/citabile.json`** (in `dati/dopo_esame.json` non ci sono): sono le stesse etichette dei titoli delle schede della pagina.
8. **Date di controllo vecchie restano vecchie.** Punteggio e recupero portano «controllato il 30 ottobre 2026» (data di `dati/risultati.json`); nell'indice ogni riga porta la più vecchia tra le date delle sue fonti. Nessuna data è stata rinfrescata senza rileggere la fonte.
9. **Frase delle pagine degli enti, piccole regole di lingua:** si toglie il nome dell'esame ripetuto («CELI 2 i: scritto…» → «scritto…»); «il» davanti a una percentuale; il costo viene prima del recupero e, se il prezzo vale per una versione dell'esame, la frase lo dice («Il B1 Cittadinanza costa 100 €.»), altrimenti «Costa <cifra>» o «Il prezzo lo decide il centro»; se l'ente non scrive la regola del recupero: «Il sito non dice cosa succede se non superi una parte: chiedi alla sede.». Nell'indice la riga porta, per il costo, solo la fonte del prezzo scritto nella riga.
10. **Nessuna soglia sui clic del libro e del Pass:** nei 14 giorni di base sono 1 e 0. Lo script li stampa; l'evento `pass-prezzo` non dice la pagina e comprende la prova gratis.
11. **Il `lastmod` delle 8 pagine è passato al 27/11/2026**: cambio vero di contenuto. Nessun'altra pagina si è mossa.
12. **Script nuovo** `esameb1/raccolta/citabile.py` (solo lettura, nessuna chiave nel codice); con `--base` stampa i numeri della linea di base.
13. **Dopo la revisione indipendente (7,5):** applicati i 10 punti (controllo, due host, pagine nuove fuori dal verdetto, clic, fonti complete e senza doppi nell'indice, regola del recupero nella frase, niente due punti in fila, ente dei dati con la sigla, tabella a una riga aperta, «date dei controlli nella tabella»).
14. Non fatto, perché viene dopo: pubblicazione, controllo online, IndexNow, `salute.py`, riga in `DA-PUBBLICARE.md`. Nessun commit e nessun push.
