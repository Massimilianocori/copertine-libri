# Tourist Tax Calculator – note di lavoro

Stato al **10 ottobre 2026**: sito costruito, **non pubblicato**. Nome: Tourist Tax Calculator. Indirizzo previsto:
`https://tourist-tax-calculator.netlify.app` (costante `URL_SITO` in `genera.py`, unico punto da cambiare).
Origine: studio `studio-business/intelaiatura/18-mondo-paesi-lingua-locale.md` sez. 2.1 e studio 16 sez. 2.1.
Risultati del test a costo zero e dei controlli: `TEST.md` (29 destinazioni con dati ufficiali completi, soglia 25).

## Struttura

| File | Cosa fa |
|---|---|
| `genera.py` | un comando costruisce tutto `sito/` (pagine, sitemap, robots, 404, `netlify.toml`, `data/fr.json`) |
| `verifica.py` | esempi a mano, confronto motore JS/Python, link interni, fonte + data su ogni pagina |
| `raccolta/francia.py` | scarica il dataset DGFiP DELTA (solo righe 2026) e la capacità turistica INSEE 2026, scrive `dati/francia.json` e `dati/francia_top.json` |
| `dati/destinazioni.json` | una voce per destinazione: paese, nome, slug, valuta, tipo di regola, tariffe (con date e mesi), età esenti, notti massime, riduzioni, fonti (URL, HTTP, formato, data del controllo), note |
| `dati/affiliati.json` | riquadro affiliati: **vuoto** (URL vuoti → non compare nulla). Da riempire con Stay22 / Booking / assicurazione dopo l'iscrizione |
| `sito/` | il sito statico da pubblicare (base directory su Netlify: `touristtax/sito`) |

Comandi (dalla radice del repository):

```
python3 -I touristtax/raccolta/francia.py --cache /tmp/touristtax-fr   # solo quando si aggiorna la Francia
python3 touristtax/genera.py
python3 touristtax/verifica.py
```

Tipi di regola nel calcolatore: `per_person` (importo fisso a persona per notte), `per_room` (a camera/unità per notte:
Grecia, Islanda), `percent` (percentuale del prezzo: Amsterdam, Berlino, Vienna, Edimburgo, Turchia, Kutchan),
`bands` (fasce di prezzo a persona: Kyoto, Tokyo, Sapporo, Hakuba), `per_trip` (una volta per viaggio: Bali), `france`
(tariffa comunale + tasse aggiuntive; non classificati = % del costo a persona con tetto). Le tariffe hanno date
(`dal`/`al`) e mesi: il calcolatore guarda la data di ogni notte, quindi gestisce i cambi a metà soggiorno
(Vienna 1/7, Turchia 1/5/2026, Milano 1/4/2026, Catalogna 1/4/2027) e le stagioni (Baleari, Grecia).
La formula usata è stampata sotto il calcolatore in ogni pagina.

## Fonti (tutte controllate il 10/10/2026; elenco completo con URL in `dati/destinazioni.json` e nella pagina /about/)

- Francia: DGFiP "Tarifs taxe de séjour – DELTA" (Licence Ouverte 2.0, aggiornato 29/06/2026), regole: service-public F31635 e guida DGCL (fiche 4 e 6, giugno 2026). Pagine comunali: 150 comuni con più posti turistici INSEE 2026.
- Spagna: ATC Catalogna (Barcellona e resto), BOE testo consolidato legge 2/2016 Baleari.
- Grecia: ΦΕΚ Α' 198/2024 (legge 5162/2024 art. 24). AADE dà 403.
- Turchia: Resmî Gazete 1/5/2026 (Decisione 11263, 1% fino al 31/12/2026) + guida GİB.
- Amsterdam: CVDR703815 (ordinanza 2024 ancora in vigore). amsterdam.nl dà 403.
- Berlino, Vienna, Praga, Edimburgo, Roma, Firenze, Milano, Kyoto, Tokyo, Sapporo, Kutchan, Hakuba, Bali, Islanda: pagine o atti ufficiali (vedi JSON).

## Date in cui rigenerare il sito (obbligatorio)

Titoli, cifre in evidenza ed esempi delle pagine sono calcolati alla data di generazione (le cifre cambiano a quella data,
ad esempio "Turkey: 1% until 31 December 2026, then 2%"). `genera.py` stampa a ogni esecuzione l'elenco delle prossime date.
Al 10/10/2026 sono: **1/1/2027** (Turchia 2%, fine tariffe Milano 2026, Francia anno 2027), **1/4/2027** (Catalogna e
supplementi comunali, fine tabella Barcellona, Tokyo), **1/7/2027** (Vienna 8%), **1/6/2029** (Hakuba/Nagano).
In ognuna di queste date: `python3 touristtax/genera.py && python3 touristtax/verifica.py`, controllo delle fonti della
destinazione interessata, commit (Netlify pubblica da solo).

## Revisione indipendente del 10/10/2026: cosa è stato corretto

- Praga: il limite è di 60 giorni di calendario consecutivi (il giorno di arrivo conta), quindi 60 notti = 61 giorni = fuori dalla tassa.
- Milano: esenzione dal 15° giorno solo per residence turistico-alberghieri, case per ferie gestite da enti non profit e case e appartamenti per vacanze (avviso ufficiale del Comune, edizione 2025); locazioni brevi e altre case per ferie pagano ogni notte.
- Vienna: aggiunta l'esenzione per gli studenti delle scuole superiori e universitarie di Vienna e la regola "più di 3 mesi senza interruzione = esente" (data di uscita oltre la stessa data 3 mesi dopo l'arrivo).
- Baleari: confermate il 10/10/2026 sulla pagina dell'Agència Tributària (ATIB, sede.atib.es, "Informació i normativa"). **Il certificato TLS del server ATIB era scaduto**: la pagina (un'applicazione JavaScript) è stata letta con un browser automatico che ignora il certificato, solo per leggere questa pagina ufficiale. Il testo consolidato della legge sul sito ATIB è aggiornato al 17/05/2025; nel BOIB non è stata trovata nessuna modifica successiva dell'art. 13. Avviso visibile sulle pagine delle Baleari. **Da ricontrollare** a ogni trimestre e prima dell'estate 2027 (in stampa si è parlato di un supplemento estivo, mai trovato in atti ufficiali).
- Catalogna: supplementi dei 7 comuni (dal 1/10/2026 e dal 1/4/2027) nel calcolatore (scelta del comune) e in tabella.
- Edimburgo, Sapporo, Hakuba: le notti prima dell'inizio della tassa risultano "no tax yet", non "senza tariffa". Per chi arriva prima del 24/7/2026 a Edimburgo non è chiaro da dove si contano le 5 notti: avviso nel risultato.
- Tolte le frasi non sostenute da fonti ufficiali (Bali "on arrival", Baleari "at check-out"); Baleari: l'esercizio deve addebitare la tassa prima della fine del soggiorno (ATIB).
- Berlino: fonti sostituite con le pagine ufficiali della Senatsverwaltung für Finanzen (FAQ) e del Service-Portal; il testo pubblicato della legge (gesetze.berlin.de) non era raggiungibile dal server.
- Grecia: il link è il PDF ufficiale della Gazzetta servito dall'archivio di search.et.gr (Tipografia nazionale); la scheda del record su search.et.gr non è stata trovata (la ricerca restituisce errore). Aggiunta l'esenzione per i soggiorni gratuiti.
- Roma: aggiunti rifugi montani, rifugi escursionistici, case del camminatore (€3,50) e l'esenzione per persone con disabilità grave e caregiver (art. 5 del regolamento).
- Testi: criterio INSEE per le 150 comuni ("most tourist accommodation", non "most visited"); "33 destination pages" basate su 20 regole ufficiali (21 con la Francia); frase introduttiva diversa per tipo di regola; tabella Tokyo "Current rates (until 31 March 2027)"; definizione della base di calcolo a Kutchan, Sapporo e Hakuba ("宿泊料金"; chiedere alla struttura se include i pasti); Nozawa Onsen con fonte MIC (3,5% per 3 anni, poi 5%).
- `sito/netlify.toml` resta nella cartella pubblicata perché Netlify lo legge dalla base directory; commento in inglese, contenuto innocuo.

## Cosa controllare ogni trimestre (routine del lunedì, una settimana su tredici) e prima del 1° gennaio e del 1° aprile

1. Rilanciare `verifica.py` e aprire tutte le fonti di `dati/destinazioni.json` (le 200 si leggono anche in automatico; AADE, amsterdam.nl danno 403: controllo a mano).
2. Date di cambio già note:
   - **31/12/2026** Turchia: scade la Decisione 11263 (1%); dal 1/1/2027 torna il 2% di legge salvo nuova decisione nella Gazzetta.
   - **31/12/2026** Milano: le tariffe 2026 finiscono; cercare le tariffe 2027 su comune.milano.it.
   - **gennaio 2027** Oita (Giappone) e **1/2/2027** Okinawa, Ishigaki, Miyakojima, Nago, Motobu, Onna, Chatan: nuove tasse (elenco MIC) → nuove pagine.
   - **1/3/2027** Wakkanai, Shirahama; **1/4/2027** Tomakomai, Yamagata, Fujiyoshida, Fujikawaguchiko, Unzen, Kagoshima, Ibusuki (elenco MIC).
   - **31/3/2027** Barcellona: la tabella ATC non ha ancora la tariffa generale da aprile 2027 (il calcolatore si ferma); il supplemento sale a €6. Catalogna: tariffe dal 1/4/2027 già inserite.
   - **1/4/2027** Tokyo: passaggio previsto al 3% con soglia ¥13.000, inclusi minpaku e simple lodging (pagina del Bureau of Taxation: "予定") → aggiornare quando confermato.
   - **1/7/2027** Vienna: 8% (già inserito).
   - **1/6/2029** Hakuba e Nagano: fine delle tariffe ridotte dei primi 3 anni (già inserito).
   - **giugno-luglio** di ogni anno: nuovo aggiornamento DELTA (le delibere per l'anno dopo vanno prese prima del 1° luglio) → rilanciare `raccolta/francia.py` con `ANNO` = anno successivo quando compaiono le righe con data d'effetto 2027 e pubblicare le pagine "2027" a novembre-dicembre.
3. Nuove destinazioni: controllare l'elenco MIC (`soumu.go.jp`, "法定外税の状況") e il feed `soumu.go.jp/news.rdf`.

## Destinazioni escluse (da verificare)

| Destinazione | Motivo | Cosa serve per aggiungerla |
|---|---|---|
| Venezia (imposta + contributo d'accesso) | comune.venezia.it e cda.ve.it danno 403 | lettura a mano della delibera tariffe e del calendario dei giorni di accesso, o una fonte ufficiale alternativa leggibile |
| Lisbona | lisboa.pt 403 | regolamento pubblicato nel Diário da República |
| ~~Porto~~ | aggiunta il 26/10/2026 (volantino ufficiale CMP + regolamento) | – |
| Algarve | nessun regolamento comunale letto | regolamenti di Albufeira, Faro, Lagos, Portimão, Loulé |
| Budapest | tassa decisa dai distretti | delibere dei distretti centrali (V, VI, VII, VIII) |
| Dubrovnik, Spalato | decisioni delle contee 2026 non trovate | Gazzetta ufficiale delle contee |
| Osaka | pref.osaka.lg.jp risponde 408 al server | lettura a mano o consenso MIC sul cambio 2025 |
| Glasgow | glasgow.gov.uk 403 | pagina del Council o schema ufficiale |
| ~~Quintana Roo (Visitax)~~ | aggiunto il 30/10/2026 (sezione Messico, importo = 2,50 × UMA INEGI) | – |
| Okinawa | in vigore solo dal 1/2/2027 (già nella pagina dei cambi 2027) | pagina calcolatore da aggiungere a gennaio 2027 |
| Egitto, Marocco, Canarie | nessuna fonte ufficiale con tariffa | – |
| Francia: comuni senza righe 2026 nel file DGFiP (es. Nizza, Marsiglia, Tolosa) | le tariffe nel file sono di anni precedenti | non si mostrano: la ricerca dice di chiedere al comune |

## Note e limiti noti

- Bali: sul portale ufficiale c'è l'importo (IDR 150.000) ma il PDF del regolamento dà 403; non scriviamo "per visita" né l'elenco delle esenzioni.
- Kutchan: il 3% è il totale (Hokkaido + comune) secondo il poster ufficiale dell'Hokkaido; Niseko Town, Rusutsu, Akaigawa hanno regole proprie, non coperte.
- Hakuba: si sommano tassa del villaggio e tassa di Nagano (metà della tariffa prefettizia, come da consenso MIC).
- Francia: due comuni hanno righe in conflitto nel file (Le Barcarès, Saméon): nessuna tariffa mostrata.
- Nessuno script esterno, nessun cookie. Spazio pubblicità: `<div class="ad-slot">` (vuoto, nascosto finché vuoto).
- Link "Spotted a change? Tell us" in ogni pagina → modulo contatti Netlify Forms con honeypot.

## Pubblicazione (da fare da Massimiliano)

1. Netlify → Add new site → Import from Git → repository `copertine-libri`, branch `ccr-b7fd6b9e-n096cr`,
   **base directory `touristtax/sito`**, build command vuoto, publish directory `.` (lo dice anche `sito/netlify.toml`).
   Nome del sito: `tourist-tax-calculator` (se è preso, cambiare `URL_SITO` in `genera.py` e rigenerare).
   Il file `netlify.toml` pubblica solo quando cambia qualcosa in `touristtax/sito` (crediti Netlify condivisi).
2. Netlify → Forms: attivare il rilevamento dei moduli (modulo "contact") e le notifiche email.
3. Google Search Console: aggiungere la proprietà `https://tourist-tax-calculator.netlify.app/`, verificare con il file
   HTML (va in `touristtax/sito/`, `genera.py` lo conserva) e inviare `sitemap.xml`.

## Pubblicazione (10/10/2026)
- Online su https://tourist-tax-calculator.netlify.app (Netlify, base `touristtax/sito`, pubblica solo se cambia `touristtax/sito`). Search Console verificata con il meta tag `GOOGLE_VERIFICA` in `genera.py` (non rimuoverlo) e sitemap inviata il 10/10/2026.
- Test: al giorno 60 (9/12/2026) servono ≥ 200 impression a settimana in Search Console, altrimenti si rivede o si chiude.

## 23/10/2026 — blocco «Other useful tools for your trip» (link ai siti fratelli)
- In fondo a ogni pagina, nel piè di pagina prima della riga finale, il blocco `.f-altri` (`ALTRI_SITI` e `blocco_altri()` in `genera.py`, stesso modello di EsameB1/EsamiDiStato): titolo piccolo e una riga per sito, 4 link normali (`rel="noopener"`, nessun nofollow) a Italy Strikes Today, Before You Fly, Visa Income Checker e Cruise Health Scores. Scopo: Italy Strikes Today dopo 13 giorni aveva 0 pagine indicizzate e nessun sito nostro lo linkava. Nuovo controllo 5 in `verifica.py` (blocco in tutte le pagine indicizzabili, link uguali a `genera.py` e nell'ordine, mai a questo sito, tutti `noopener`): 202 pagine, 0 errori; `verifica.py` tutto a posto. Rigenerate 202 pagine + 404: oltre al blocco e al CSS cambia, come a ogni rigenerazione, la data dell'esempio «3 nights from …» (oggi) in 183 pagine e il `lastmod` della sitemap. Schermate 375/1280 px, chiaro e scuro, in `scratchpad/link-shot/` (fuori dal repository). Non ancora pubblicato (commit e push da fare).

## IndexNow (26/10/2026)
- IndexNow: file chiave scritto dal generatore; invio con studio-business/strumenti/indexnow.py. Costante `CHIAVE_INDEXNOW` in `genera.py` accanto a `SCRIPT_CONTATORE` (chiave pubblica, uguale in tutti i siti della rete); `extra()` scrive `sito/<chiave>.txt` accanto a `robots.txt`, fuori dalla sitemap e non linkato. Nuovo controllo in `verifica.py` (`controlla_indexnow`): file presente, contenuto = chiave, non citato nella sitemap.

## 26/10/2026 — titoli con la risposta, pagina dei cambi 2027, 4 destinazioni nuove
Spunto: idea 1 di `studio-business/intelaiatura/idee-2026-10-25.md` e Search Console del 23/10 (345 impressioni in 28 giorni, 0 clic, posizione 32,5; query Majorca, Spagna, Grecia, Turchia, Menorca).

**1. Titoli, descrizioni, H1 e risposta diretta** (tutte le 37 pagine di destinazione + paese Spagna, Grecia, Turchia). Funzioni nuove in `genera.py` (`titolo_seo`, `h1_seo`, `risposta`, `descrizione_seo`, `paese_seo`): le cifre vengono solo dalle tariffe dei dati alla data di generazione; `NOMI_SEO` ha solo i nomi cercati (Majorca) e il suffisso col nome locale già in `official_name` (ecotasa). "2026 and 2027" compare solo se i dati hanno una tariffa o un cambio ufficiale che parte nel 2027 (Catalogna, Barcellona, Turchia ×4, Vienna, Tokyo); Cardiff dice "2027". Baleari e Grecia restano "2026" (tariffe di legge senza scadenza, nessun cambio datato). Campi dati nuovi, facoltativi: `cambi_annunciati` (Barcellona: supplemento 6 € dal 1/4/2027, 7 € dal 1/4/2028, tabella ATC), `breve_seo` e `risposta` (Cardiff, Tunisia: frasi scritte dalle note ufficiali). Prima i titoli erano tutti "X tourist tax 2026: how much per night (calculator)"; ora per esempio "Majorca tourist tax 2026 calculator: €1–€4 per person per night (ecotasa)". Le date di rigenerazione restano obbligatorie: titoli "now … from …" cambiano il 1/1, 1/4 e 1/7/2027.

**2. Pagina `tourist-tax-changes-2027/`** da `dati/cambi_2027.json` (7 voci: Turchia 1/1, Okinawa 1/2, Cardiff 1/4, Catalogna 1/4, Barcellona 1/4, Tokyo 1/4, Vienna 1/7; "dopo": Barcellona 1/4/2028, Hakuba 1/6/2029; "non elencati": Venezia, Milano 2027, tariffa catalana di Barcellona da aprile 2027). Ogni voce ha fonte (URL, HTTP, data del controllo) e `verifica` = [slug, data] controllata contro i dati. Tabella in cima, schede per data, 4 domande visibili + JSON-LD FAQPage. Linkata da home (riquadro), piè di pagina di tutte le pagine, tabella Europa, pagine paese interessate e riquadro "What changes in 2027" sulle pagine dei luoghi. In sitemap. Okinawa non ha pagina calcolatore (la base è il prezzo per persona arrotondato ai 1.000 ¥ con tetto, non modellato): aggiungerla a gennaio 2027.

**Fonti ricontrollate oggi con curl (200)**: BOE legge 2/2016 Baleari (testo consolidato ancora del 17/05/2025), ATC Catalogna (tabelle 2026-27, dal 1/4/2027 e supplementi Barcellona 2027-2029), wien.gv.at (8 % dal 1/7/2027), CVDR Amsterdam, Resmî Gazete 11263, Gazzetta greca, Tokyo FAQ e pagina 宿泊税の見直し (ordinanza approvata il 27/3/2026, consenso MIC 30/6/2026, cambio dal 1/4/2027: 3 % da 13.000 ¥ a persona, anche minpaku), Okinawa (施行期日 1/2/2027, 2 % con tetto 2.000 ¥), gov.wales (OGL v3.0, attribuzione nella pagina /about/). ATIB (Baleari) non ricontrollata (certificato): resta 10/10.

**Motore**: due campi nuovi, uguali in Python e JS (`verifica.py` confronta 2.047 casi): `esente_da_notti` (Cardiff: una prenotazione di 32 notti o più non paga) e `bande_pct` sulle fasce (Tokyo dal 1/4/2027: la fascia è una percentuale del prezzo a persona). Valuta nuova TND.

**3. Destinazioni nuove** (37 in tutto; 210 pagine indicizzabili):
- **Cardiff** (Galles): £1,30 a persona a notte (tutte le età), 75 p per adulto in ostelli/dormitori/tende, dal 1/4/2027, prenotazioni fatte dal 28/9/2026, esenti le prenotazioni da 32 notti. Fonti gov.wales / Welsh Revenue Authority (4 pagine, 200, OGL).
- **Malta**: eco-contribution 1,50 € a notte dai 18 anni, massimo 22,50 € a visita (15 notti), per soggiorni dal 1/7/2026. Fonti MTA (pagina, linee guida 2026, avviso agli ospiti; 200). tourism.gov.mt dà 403 (Cloudflare).
- **Porto**: 3 € a notte dai 13 anni, massimo 7 notti. Fonte: volantino ufficiale della Câmara Municipal (novembre 2024) + regolamento (DR 23/11/2022) per età ed esenzioni; la copia del regolamento sul portale ha ancora 2 € all'art. 2: avviso visibile in pagina. Da ricontrollare (la stampa parla di una revisione nel 2026, nessun importo deciso).
- **Tunisia**: legge di finanze 2024 (legge 2023-13) art. 46, JORT n. 144 del 12/12/2023, PDF del Ministero delle Finanze (200, letto anche come immagine per la tabella): stranieri 12/8/4 TND (4-5 stelle / 3 stelle / 2 stelle e altro), tunisini e maghrebini 3/2/1, massimo 10 notti di fila. L'articolo non parla di bambini: in pagina "chiedere all'hotel".

**Escluse (motivo)**: Lisbona (lisboa.pt e informacoeseservicos.lisboa.pt 403); Cipro (nessuna pagina ufficiale né sulla tassa né sulla sua assenza; la stampa parla di un prelievo proposto); Croazia (21 decisioni di contea per comune e stagione, ragazzi 12-18 al 50 % non modellato; nessuna decisione 2026 di Dubrovnik/Spalato letta); Venezia (comune.venezia.it 403, cda.ve.it pagina vuota); Napoli (pagina comunale 404, importi 2026 solo in stampa e discordanti); Bologna (tariffe 2026 lette su Bologna Welcome, ma il regolamento leggibile è del 2015 con massimo 5 notti e 5 fasce: regola attuale non confermata; prenotazioni via portale a percentuale con tetto); Verona e Torino (connessione chiusa dal server); Glasgow (403); Algarve, Budapest come prima.

**Da fare a gennaio 2027**: rigenerare il 1/1 (Turchia 2 %, titoli), aggiungere Okinawa (1/2/2027) e le tariffe 2027 di Milano; ricontrollare Porto (eventuale nuovo importo) e Malta.

`verifica.py`: nuovi esempi a mano (Tokyo 2027, Cardiff, Malta, Porto, Tunisia: 47 in tutto) e controlli 6 (pagina 2027), 7 (destinazioni nuove), 8 (titoli/descrizioni/risposte): tutto a posto. Schermate 375/1280 px, chiaro e scuro, di Mallorca, Cardiff e della pagina 2027 in `scratchpad/touristtax-2027/` (fuori dal repository). Non pubblicato: commit e push da fare.

**Revisione indipendente (26/10/2026)**: fonti rilette con curl (tutte 200): Resmî Gazete 11263 (1% fino al 31/12/2026, letto dall'immagine), Okinawa, gov.wales (4 pagine), ATC (tabelle 2026-27 e dal 1/4/2027), Tokyo 宿泊税の見直し (可決 27/3/2026, 総務大臣同意 30/6/2026, 3% da 13.000 ¥), wien.gv.at, MTA (pagina + 2 PDF), Porto (volantini PT ed EN: 3 €; regolamento sul portale = testo 2022 con 2 €), JORT/LF 2024 art. 46 (tabella confermata anche dal livello di testo del PDF). Correzioni: Sant Just Desvern non cambia il 1/4/2027 (tolta dalla voce Catalogna); Okinawa: comuni con tassa comunale "previste", arrotondamento "to the nearest ¥1,000"; avviso Porto più chiaro + fonte volantino EN; Tunisia: nota sui bambini (la legge 2018 tassa chi ha più di 12 anni, verbale ARP del novembre 2023, nuova fonte); meta description delle pagine paese tagliate a metà frase (Turchia, Grecia) corrette; titolo Malta accorciato (€1.50 per adult per night). Da decidere: titolo Catalogna lungo (86 caratteri).

## Monetizzazione: come si attiva (30/10/2026)
- **Dove si scrive:** un solo file per tutta la rete, `studio-business/strumenti/monetizzazione.json` (`adsense_client`, `adsense_siti`, domini di affiliazione ammessi). In una riga: `python3 studio-business/strumenti/monetizzazione.py attiva ca-pub-XXXXXXXXXXXXXXXX touristtax`, poi `python3 touristtax/genera.py`. Il nome del sito nel file è `touristtax` (`SITO_ID` in `genera.py`).
- **Cosa cambia con AdSense acceso:** script ufficiale nel `<head>` di ogni pagina (annunci automatici, nessun blocco manuale), `sito/ads.txt` con `google.com, pub-…, DIRECT, f08c47fec0942fa0`, sezione «Advertising (Google AdSense)» in `privacy.html`; la frase sui cookie diventa «GoatCounter non usa cookie, la pubblicità sì». Prima di pubblicare: in AdSense accendere il messaggio di consenso certificato di Google (Privacy e messaggi, regolamenti europei: UE/SEE, Regno Unito, Svizzera), che la privacy descrive.
- **Link di affiliazione:** `dati/affiliati.json` (campo `url`, es. Stay22) → riquadro affiliati. Ammessi solo verso i domini di `domini_affiliazione`, con `rel="sponsored noopener"` e la riga di trasparenza (la aggiunge `riquadro_trasparenza()` se manca); con almeno un link la privacy aggiunge la sezione sui link di affiliazione.
- **Come si verifica:** `python3 touristtax/verifica.py`; controllo comune in `monetizzazione.py` (script e `ads.txt` solo con AdSense acceso, privacy coerente, nessun dominio fuori elenco o bloccato, Amazon.it solo con `tag=`).
- **Con il codice vuoto o il sito fuori elenco l'output non cambia:** il 30/10/2026 `sito/` è stato rigenerato identico byte per byte.

## AdSense acceso (30/10/2026)
- **AdSense acceso il 30/10/2026** (codice editore `ca-pub-3750093987658434`, già usato da EsameB1, Visa Income e Before You Fly): `python3 studio-business/strumenti/monetizzazione.py attiva ca-pub-3750093987658434 touristtax`, poi `python3 touristtax/genera.py`. Script ufficiale nel `<head>` di ogni pagina, `sito/ads.txt` (`google.com, pub-3750093987658434, DIRECT, f08c47fec0942fa0`), privacy `/privacy.html` con la sezione «Advertising (Google AdSense)».
- **Controlli del 30/10/2026:** `python3 touristtax/verifica.py` → «Tutto a posto»; `monetizzazione.py verifica touristtax` → AdSense acceso, 0 errori; Playwright a 375 px su home (script AdSense caricato davvero): nessun errore JS, nessuno scorrimento orizzontale. Da fare in AdSense: aggiungere il sito (Siti → Aggiungi) e controllare che il messaggio di consenso UE copra anche questo dominio. Nessun commit, nessuna pubblicazione.

## 30/10/2026 — sezione Messico (Visitax del Quintana Roo, DNR, crociere)
Spunto: `studio-business/intelaiatura/ricerca-zona-latam-africa-2026-10-30.md`, candidata 1 (voto 7,5). Non pubblicato: nessun commit, nessun push.

**Pagine nuove (5, in sitemap):** `/mexico/` (tabella di tutte le tasse, calcolatore Visitax, importi per anno, luoghi, DNR, crociere, imposta sull'alloggio, FAQ) e `/cancun/`, `/tulum/`, `/playa-del-carmen/`, `/cozumel/` (calcolatore, formula, importi per anno, note, esenzioni, altre tasse, FAQ). Isla Mujeres, Holbox, Bacalar, Mahahual, Puerto Morelos, Chetumal: citati in `/mexico/` (domanda debole, pagina propria sarebbe un doppione). Titoli ≤ 70 caratteri con anno e importo (es. «Cancun tourist tax 2026: Visitax MXN 293.28 per person (calculator)»); prima frase con importo, legge, INEGI e data del controllo; FAQPage JSON-LD uguale al testo visibile. Il Messico ha la sua pagina `mexico/` (non `country/mexico/`: `link_paese()` in `genera.py`).

**Importi e fonti (tutte lette con curl il 30/10/2026, HTTP 200):**
- Visitax = **2,50 UMA** (Ley de Derechos del Estado de Quintana Roo, art. 51-Octies, testo con ultima riforma POE 18/12/2025, `documentos.congresoqroo.gob.mx/leyes/L195-XVIII-20251218-…pdf`; l'elenco `congresoqroo.gob.mx/leyes/195/` non ha versioni più nuove). UMA INEGI: 113,14 dal 1/2/2025 (comunicato 1/25), **117,31 dal 1/2/2026** (comunicato 1/26 dell'8/1/2026) → **MXN 282,85** fino al 31/1/2026, **MXN 293,28** dal 1/2/2026 (293,275 arrotondato al centesimo). Esenti: chi entra dalla frontiera sud e i crocieristi che hanno pagato il diritto statale per crociere. Portale ufficiale `https://visitax.gob.mx/sitio/` (FAQ: obbligatorio per tutti i turisti stranieri, nessuna tariffa adulti/bambini, vale per Cozumel; si paga sul portale o tramite società autorizzate dal SATQ). Il portale non scrive l'importo: per questo lo calcoliamo dalla formula.
- Crocieristi, Quintana Roo: **US$5** a passeggero, con il biglietto, solo al primo porto, sostituisce il Visitax (art. 51-Nonies).
- DNR federale: **MXN 983,00 nel 2026** (Ley Federal de Derechos art. 8 fr. I; testo della Camera, ultima riforma DOF 7/11/2025, importi aggiornati dalla RMF DOF 28/12/2025). La legge dice che per chi arriva in aereo lo riscuote la compagnia aerea; via terra esente fino a 7 giorni (art. 11). Diritto migratorio in aeroporto all'uscita: **MXN 231,55** (art. 12), riscosso dalla compagnia aerea.
- Crocieristi, federale: decreto di stimolo fiscale del 30/6/2025 (SIDOF `sidof.segob.gob.mx/notas/docFuente/5761557`): DNR ridotto all'equivalente in pesos di **US$5** (1/7/2025-31/7/2026), **US$10** (1/8/2026-30/6/2027), **US$15** (1/7/2027-31/7/2028), **US$21** (1/8/2028-30/9/2030); reingressi con la stessa crociera gratis. Nel testo della LFD non c'è: è nel decreto.
- Imposta sull'alloggio (ISH) del Quintana Roo: **5 %** (6 % per case, appartamenti e ville), solo l'alloggio senza pasti (Ley del Impuesto al Hospedaje, artt. 4 e 8, ultima riforma 16/12/2025). **Non pubblicate** le ISH di Baja California Sur (cbcs.gob.mx e congresobcs.gob.mx: 000), Jalisco (congresoweb.congresojal.gob.mx: 403) e Città del Messico (data.consejeria.cdmx.gob.mx: certificato TLS non verificabile dal server): scritto in pagina «Not covered».

**Motore e dati:** `dati/uma.json` (valori INEGI con fonte; "prossima" = 2027), `dati/messico.json` (fonti e importi federali e statali, testi e FAQ delle pagine, query di domanda), 4 voci in `dati/destinazioni.json` con `uma_moltiplicatore: 2.5` e `tariffe` vuote: `genera.py` (`tariffe_uma`) scrive una tariffa per anno (1/2 → 31/1). Valuta MXN; tipo `per_trip` con campi nuovi `chiedi_data` / `etichetta_data` (il calcolatore chiede la data d'arrivo) e `nota_senza_importo` (dopo il 31/1/2027, finché manca la UMA 2027, il calcolatore dice che l'importo non è ancora ufficiale).

**Aggiornamento automatico della UMA 2027:** `python3 -I touristtax/raccolta/uma.py` (accetta solo il PDF INEGI con «1 de febrero de 2027» e la riga diario/mensual/anual coerente; il 30/10 il percorso 2027 risponde 200 con una pagina HTML «Página no encontrada» e lo script non scrive nulla). Avvisa anche se esce una versione nuova della legge del Quintana Roo o una riforma della LFD. Poi `genera.py`: titoli, risposte, tabella per anno, calcolatore e la voce del 1/2/2027 di `cambi_2027.json` (campo `uma`: importo e «prima» calcolati) si aggiornano da soli. Provato in una copia con una UMA 2027 finta: titoli «… 2027: Visitax MXN … from 1 Feb 2027», `verifica.py` tutto a posto. `genera.py` stampa il promemoria finché la UMA 2027 manca. **Da fare: dall'8 gennaio 2027** lanciare `uma.py` + `genera.py`; **il 1/1/2027** ricontrollare DNR e art. 12 (la RMF di fine dicembre aggiorna gli importi della LFD).

**Pagina 2027:** voci nuove «Quintana Roo (Mexico)» 1/2/2027 (2,50 × UMA 2027) e «Mexico (cruise passengers)» 1/7/2027 (US$15); in «dopo» 1/8/2028 (US$21). Risposta in cima, descrizione e riquadro della home aggiornati.

**Domanda (autocomplete 30/10/2026, gl=us/uk/ca, risposte uguali; elenco completo in `dati/messico.json`, "domanda"):** visitax 10 (official website, cancun airport, cancun 2026, cost, departure date, tui), cancun tourist tax 10 (official website, 2026, reddit, when to pay, cost, departure date, airport, tui), quintana roo tourist tax 10, mexico cruise tax 10 (increases, passenger tax), mexico non resident fee 10 (dnr, flight, volaris), tulum tourist tax 8, visitax scam 7 (cancun airport, online, app, travelkore), cozumel tourist tax 7, playa del carmen tourist tax 6, mexico tourist tax 2026 5, isla mujeres tourist tax 4, holbox tourist tax 4, visitax children 3.

**Avviso sui siti non ufficiali:** riquadro in ogni pagina con un solo link, al portale ufficiale, e la frase neutra «The official fee is MXN 293.28 per person; third-party sites may charge a service fee.» FAQ «Is Visitax a scam?» con la stessa frase.

**Monetizzazione:** AdSense già acceso. DiscoverCars (dominio in whitelist; link `https://www.discovercars.com/?a_aid=Massimilianocori` provato con curl: 200, a_aid nella pagina) nel riquadro «Hire a car in Cancún and the Riviera Maya» solo nelle 5 pagine Messico, dopo FAQ e fonti ufficiali, `rel="sponsored noopener"`, riga di trasparenza; voce `_discovercars_messico` in `dati/affiliati.json` (per spegnerlo: url vuoto e rigenerare). `ci_sono_affiliati()` ora conta anche le voci «_»: la privacy ha la sezione sui link di affiliazione.

**Controlli:** `verifica.py` punto 9 (pagine in sitemap; Visitax ricalcolato da `uma.json` indipendentemente da `genera.py`; titoli ≤ 70 con anno e importo; prima frase con importo, art. 51-Octies, INEGI e data; formula mostrata; avviso e link solo a visitax.gob.mx; FAQPage visibile; importo DNR; affiliazione solo DiscoverCars con il nostro a_aid, dopo le informazioni ufficiali, mai fuori dalla sezione; voce 2027) + 3 esempi a mano (Cancún 3 × 293,28 = 879,84; Tulum 31/1/2026 2 × 282,85 = 565,70; Cozumel 4 × 293,28 = 1.173,12). Esito: «Tutto a posto» (50 esempi, 2.050 casi JS/Python, 7.039 link, 215 pagine); `monetizzazione.py verifica touristtax`: 0 errori (5 link di affiliazione in 5 pagine). Playwright 375/1280 px, chiaro e scuro, home, `/mexico/`, Cancún, Cozumel, Playa del Carmen: nessun errore JS, nessuno scorrimento orizzontale; calcolatore: 3 viaggiatori dal 20/12/2026 = MXN 879,84, arrivo 1/3/2027 = avviso «No official amount yet…». Schermate in scratchpad (fuori dal repository).


**Revisione indipendente (30/10/2026), fonti riscaricate con curl (tutte 200):** legge del Quintana Roo (PDF POE 18/12/2025, art. 51-Octies e 51-Nonies parola per parola), INEGI 1/25 e 1/26, LFD della Camera (art. 8 fr. I $983.00, art. 11 fr. II a, art. 12 $231.55; in testa: «Cantidades actualizadas por RMF DOF 28-12-2025», Anexo 4 RMF 2026), decreto SIDOF 5761557 (fattori 5/10/15/21 e date confermati), portale visitax.gob.mx (FAQ: tutti i turisti stranieri, bambini e neonati compresi), Ley del Impuesto al Hospedaje (art. 4, 6, 8: 5 %, 6 % per fr. V). Tutto confermato tranne l'importo:
- **Correzione: il Visitax si paga arrotondato al peso.** La pagina di pagamento del portale (`registro.php`) ha `PRECIOUNITARIO = 293` e mostra il totale come «n × 293.00 MXN»; il Código Fiscal del Estado de Quintana Roo, art. 18 (ultima riforma POE 16/12/2025) arrotonda per il pagamento: 1-50 centavos giù, 51-99 su. Quindi **MXN 293,00** dal 1/2/2026 (non 293,28) e **MXN 283,00** dal 1/2/2025 al 31/1/2026 (282,85, regola applicata da noi: il portale di allora non è leggibile). `genera.py`: `al_peso()`, `tariffe_uma()` ha `valore` (arrotondato) ed `esatto`; formula «2.50 × MXN 117.31 = MXN 293.275, rounded to MXN 293.00» con la frase sull'art. 18 e sul prezzo del portale (`messico.json` → `visitax.portale.prezzo_unitario`, mostrata solo se uguale all'importo dell'anno). Nuova fonte `quintana_roo.codice_fiscale`. `verifica.py`: ricalcolo al peso, esempi 879,00 / 566,00 / 1.172,00, controllo che il prezzo del portale coincida con la formula.
- Calcolatore: per arrivi dopo il 31/1/2027 il totale dice «Not yet official» invece di «MXN 0.00».
- Testo: frase doppia su Isla Mujeres/Holbox tolta; tabella «At a glance» con l'importo in seconda colonna (a 375 px restava fuori); tabella per anno compatta (`tab sintesi`, date brevi).
- **Da fare a febbraio 2027:** con la UMA 2027 ricontrollare sul portale (`registro.php`, campo `PRECIOUNITARIO`) che l'importo arrotondato coincida e aggiornare `prezzo_unitario`.
