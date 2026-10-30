# FloodCost (Flood Insurance Cost, USA) – note di lavoro

Approvato da Massimiliano il 15/10/2026 (idea n. 1 di `studio-business/intelaiatura/idee-mondo-2026-10-14.md`).
Costruito il 15/10/2026. Sito statico in inglese per il pubblico USA: "what does flood insurance really cost here?",
con i dati ufficiali FEMA del National Flood Insurance Program (NFIP). Generato da `genera.py` in `sito/`.
Indirizzo previsto: `https://flood-insurance-cost.netlify.app` (costante `URL_SITO` in `genera.py`, unico punto da cambiare).
Il sito Netlify NON è stato creato: lo crea Massimiliano (impostazioni più sotto).

## Pagine (edizione del 15/10/2026: polizze in vigore al 31/8/2026)

| Tipo | Quante | Regola |
|---|---|---|
| Home | 1 | panoramica nazionale, ricerca ZIP/contea/Stato (nel browser, `data/search.json`), mappa a tessere degli Stati, zone, contee più grandi, confronto con l'anno prima, risarcimenti dal 1978 |
| Stati e territori | 54 + elenco `states/` | tutti quelli con almeno 10 polizze "homes" (manca solo Northern Mariana Islands) |
| Contee | 1.230 | almeno **100** polizze "homes" in vigore (le altre 1.306 contee con almeno 10 polizze sono nella tabella della pagina dello Stato e nella ricerca, senza pagina) |
| ZIP | 1.622 | almeno **300** polizze "homes" in vigore (gli altri 11.644 ZIP con almeno 10 polizze sono nella ricerca, con mediana, e rimandano alla contea) |
| Zone | 7 + `flood-zones/` | VE, AE, A, AO, AH, A99/AR (`zone-a99/`, 32.340 case, quasi tutte A99), X (la D ha troppe poche polizze per una guida: compare nelle tabelle) |
| Fisse | 5 | methodology, about, contact (modulo Netlify), privacy, 404 |
| **Totale** | **2.920 indicizzabili** + 404 | tutte nella sitemap |

Perché 300 per gli ZIP e non 100: con 300-400 polizze uno ZIP ha in genere 2-3 zone sopra la soglia di 10 e pochi anni di
risarcimenti; sotto i 300 la pagina diventa una ripetizione della contea (contenuto sottile). Con 100 sarebbero 3.360 pagine ZIP,
con 200 2.115. Le soglie sono in `raccolta/aggrega.py` (`SOGLIA_CONTEA`, `SOGLIA_ZIP`) e in `dati/fonti.json`.

## Fonti (tutte OpenFEMA, lette dal server il 15/10/2026)

| Dataset | Versione | Endpoint | Aggiornato da FEMA | Righe |
|---|---|---|---|---|
| NFIP Redacted Policies | **v3** | `https://www.fema.gov/api/open/v3/NfipPolicies` | 9/9/2026 (asOfDate 8/9/2026) | 74.739.461 |
| NFIP Redacted Claims | **v3** | `https://www.fema.gov/api/open/v3/NfipClaims` | 9/9/2026 | 2.725.989 |
| NFIP Residential Penetration Rates | v1 | `https://www.fema.gov/api/open/v1/NfipResidentialPenetrationRates` | 4/8/2026 | 3.159 |
| Census Bureau, nomi delle contee | 2020 | `https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt` | – | 3.235 |

- Le versioni v2 (`FimaNfipPolicies`, `FimaNfipClaims`) si spengono il 15/10/2026: il sito usa solo le v3. `scarica.py` controlla le
  versioni all'inizio e si ferma se FEMA ne pubblica una nuova (`VERSIONI_ATTESE`).
- I file completi (CSV/parquet "bulk" su `fema.gov/about/reports-and-data/openfema/v3/...`) rispondono **403 (Akamai)** dal nostro
  server: si usa l'API, in CSV, solo i campi utili, con paginazione "a chiave" (`id gt ultimo`, ordinate per `id`, 10.000 righe a
  richiesta), un blocco per mese di decorrenza (polizze) o per anno della perdita (risarcimenti), 4 richieste in parallelo.
  Tempo: circa 21 minuti; spazio in `cache/`: 257 MB (fuori da git, `.gitignore`).
- Le pagine HTML di fema.gov rispondono 403 dal server: le definizioni vengono dal dizionario dati dell'API (`DataSetFields`) e da
  FloodSmart.gov (sito NFIP della FEMA, leggibile): `premiumcosts` (voci del costo, tetto agli aumenti 18-25%), `what-is-my-flood-zone`,
  `get-insured/eligibility` (obbligo per mutui garantiti dal governo nelle zone A e V). Map Service Center `msc.fema.gov` letto (200).
- Testo di citazione richiesto dai termini OpenFEMA ("This product uses the FEMA OpenFEMA API, but is not endorsed by FEMA...") nel piè
  di pagina di ogni pagina e nella metodologia.

## Definizioni (uguali in `aggrega.py`, nella pagina Methodology e in `controllo_api.py`)

- **In vigore alla data D** (oggi D = 31/8/2026; anno prima 31/8/2025): decorrenza nei 12 mesi fino a D, `policyTerminationDate` > D,
  nessuna `cancellationDateOfFloodPolicy` entro D, `policyCost` > 0. Risultato: 3.367.522 polizze (4.441.546 unità assicurate contando
  ogni unità delle polizze condominiali); anno prima 3.575.640.
- **Costo** = `policyCost` (premio + reserve fund assessment + federal policy fee + surcharge HFIAA): il totale annuo pagato.
- **Homes** (cifra principale) = `occupancyType` 11, 12, 14, 16 (più i vecchi 1 e 2): 3.004.117 polizze, mediana **$1.082**
  (metà tra $741 e $1.421, media $1.317); anno prima $961. Edifici interi 5+ unità/condomini (13, 15) e non residenziali (17, 18, 19)
  solo nella tabella "type of building".
- Mediana e percentili 25/75 con interpolazione lineare (pandas), arrotondati al dollaro.
- **Contea** = prime 5 cifre di `censusGeoid` (per i risarcimenti senza `censusGeoid`, `countyCode`); **ZIP** = prime 5 cifre di
  `reportedZipCode` (FEMA a volte scrive ZIP+4). **Zone** raggruppate: AE (AE, A1-A30), VE (VE, V, V1-V30), A, AO (+AOB), AH (+AHB),
  A99/AR, X (X, B, C), D. Attenzione: in `gruppo_zona` la A99 va controllata PRIMA della regola `A\d{1,2}` (fino al 15/10/2026 le
  32.338 case in A99 finivano per errore in AE: corretto nella revisione indipendente).
- **Polizze pluriennali**: la finestra di 12 mesi esclude circa 24.500 polizze condominiali (occupancyType 15) con durata di 2-3 anni
  iniziate prima; nessuna polizza "homes" è esclusa (controllato con l'API: 0 al 31/8/2026, 2 al 31/8/2025). Scritto nella metodologia.
- **Risarcimenti**: per anno della perdita dal 1978 (tutte le 2.725.989 righe hanno l'anno); "pagato" se edificio + contenuto + ICC > 0;
  importi nominali, non rivalutati.
- **Privacy**: nessuna cella con meno di **10** polizze o risarcimenti (né il numero né gli importi); niente minimi o massimi; la
  ricerca contiene solo ZIP e contee con almeno 10 polizze. Controllato da `verifica.py` sui dati e sull'indice di ricerca.
- **Risk Rating 2.0**: il 100% delle polizze in vigore in entrambe le date ha i codici di occupazione a 2 cifre (che il dizionario FEMA
  riserva alle polizze Risk Rating 2.0): il confronto anno su anno è fatto nello stesso sistema di prezzi.

## File

| File | A cosa serve |
|---|---|
| `raccolta/scarica.py` | scarica i dati grezzi in `cache/` (controlla versioni; riprende da dove era rimasto: i blocchi completi hanno un file `.ok`) |
| `raccolta/aggrega.py` | calcola gli aggregati compatti in `dati/` (pandas; circa 4 minuti) |
| `raccolta/controllo_api.py` | ricalcola 10 numeri pubblicati con richieste dirette all'API (senza cache) e stampa la tabella qui sotto |
| `genera.py` | genera `sito/` (circa 3 secondi), `sito/netlify.toml`, sitemap, robots, `data/search.json` |
| `verifica.py` | link, fonte e date su ogni pagina, celle piccole, sitemap, meta di verifica, parole vietate, ricalcolo indipendente della mediana nazionale dai dati grezzi; con `--browser` lancia `verifica_browser.js` |
| `verifica_browser.js` | Playwright a 390 e 1280 px, tema chiaro e scuro: niente scorrimento orizzontale, niente errori JS o richieste fallite, ricerca e pulsante del tema funzionanti; screenshot in `cache/screenshot/` |
| `dati/affiliati.json` | riquadro "get a quote": **nascosto** finché `quote.url` è vuoto. Mettere solo un URL di affiliazione vero (mai inventato) |
| `grafica/` | font (Figtree e Source Serif 4, licenza OFL inclusa), `og.html` + `og.js` → `og.png` (immagine di condivisione) |

Monetizzazione: spazio pubblicitario `<div class="ad-slot">` dopo la scheda principale (invisibile finché vuoto) e riquadro
"get a quote" da `dati/affiliati.json`. Nessun URL di affiliazione inserito.

## Aggiornamento mensile (dopo l'aggiornamento FEMA, di solito a inizio mese)

1. Controllare la data dei dati FEMA: `python3 floodcost/raccolta/scarica.py --solo-meta` (stampa versione, `lastDataSetRefresh`, righe).
2. In `raccolta/scarica.py` spostare `RIF_ATTUALE` all'ultimo giorno del mese completo prima dell'`asOfDate` di NfipPolicies
   (es. dati di inizio novembre → `2026-10-31`) e `RIF_PRECEDENTE` allo stesso giorno dell'anno prima.
3. Cancellare la cache vecchia e riscaricare: `rm -rf floodcost/cache/polizze floodcost/cache/sinistri && python3 floodcost/raccolta/scarica.py` (~20 min).
4. `python3 floodcost/raccolta/aggrega.py` → `python3 floodcost/genera.py` → `python3 floodcost/verifica.py --browser`.
5. `python3 floodcost/raccolta/controllo_api.py` e aggiornare la tabella dei controlli qui sotto.
6. Commit di `floodcost/dati` e `floodcost/sito` (una sola pubblicazione Netlify al mese: 15 crediti).
Se `scarica.py` si ferma per una versione nuova: leggere il dizionario dati della versione nuova, aggiornare campi ed endpoint
in `scarica.py` e `VERSIONI_ATTESE`, rifare tutto.

## Impostazioni Netlify (da fare da Massimiliano)

- Collegare il repository GitHub, ramo `ccr-b7fd6b9e-n096cr`.
- **Base directory: `floodcost/sito`** · **Build command: vuoto** · **Publish directory: `.`** (relativa alla base).
- `floodcost/sito/netlify.toml` (scritto da `genera.py`, come negli altri siti) ha già `publish = "."`, `command = ""`, la regola
  `ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."` (pubblica solo se cambia `floodcost/sito`) e le intestazioni di sicurezza.
- Nome del sito: `flood-insurance-cost` (se diverso, cambiare `URL_SITO` in `genera.py` e rigenerare).
- Search Console: la meta di verifica `btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI` è in ogni pagina; poi inviare `sitemap.xml`.
- Moduli: attivare le notifiche email del modulo "contact" (Netlify Forms).

## Controllo a campione: 10 numeri ricalcolati dall'API (15/10/2026, `raccolta/controllo_api.py`)

Ogni numero è stato ricalcolato da zero con una richiesta diretta all'API OpenFEMA (filtro sotto), senza la cache e senza pandas.

| # | Numero controllato | Pubblicato | Ricalcolato dall'API | Esito | Filtro API |
|---|---|---|---|---|---|
| 1 | ZIP 32836: polizze "homes" in vigore al 31/8/2026 | 419 | 419 | OK | `startswith(reportedZipCode,'32836')` + decorrenza nei 12 mesi |
| 2 | ZIP 32836: mediana annua, homes | $673 | $673 | OK | idem |
| 3 | ZIP 32836: mediana, homes in zona X | $683 | $683 | OK | idem + `ratedFloodZone` X/B/C |
| 4 | ZIP 32836: mediana un anno prima (31/8/2025) | $664 | $664 | OK | idem, anno prima |
| 5 | Vermont: mediana annua, homes | $1.364 | $1.364 | OK | `propertyState eq 'VT'` |
| 6 | Contea 01001 (Autauga County, AL): polizze homes | 184 | 184 | OK | `startswith(censusGeoid,'01001')` |
| 7 | ZIP 33904 (Cape Coral): risarcimenti dal 1978 | 2.773 | 2.773 | OK | `startswith(reportedZipCode,'33904') and yearOfLoss ge 1978` |
| 8 | USA: risarcimenti dal 1978 | 2.725.989 | 2.725.989 | OK | `yearOfLoss ge 1978` |
| 9 | ZIP 33904: totale pagato per le perdite del 2022 | $206.393.768 | $206.393.768 | OK | `startswith(reportedZipCode,'33904') and yearOfLoss eq 2022` |
| 10 | Lee County FL (12071): quota di case nelle zone ad alto rischio con polizza NFIP | 47,47% | 47,47% | OK | `NfipResidentialPenetrationRates`, `fipsCode eq '12071'` |

In più `verifica.py` ricalcola dai file grezzi, senza pandas, la mediana nazionale ($1.082), le case (3.004.117) e le polizze (3.367.522): coincidono.

## Controlli fatti il 15/10/2026

- `verifica.py --browser`: tutti superati (2.920 pagine HTML, 2.919 nella sitemap; 84 caricamenti Playwright: 21 pagine × 390/1280 px ×
  chiaro/scuro, nessuno scorrimento orizzontale, nessun errore JS, nessuna richiesta fallita).
- Design: identità propria (marchio casa sulle onde, blu acqua + sabbia, Source Serif 4 per titoli e cifre, Figtree per il testo),
  token di colore chiaro/scuro come nei siti ridisegnati più pulsante del tema; cifra principale in alto con forchetta 25°-75° e
  tendenza; mappa a tessere degli Stati (scala a una tinta, 5 gruppi); tabella delle zone con barre di forchetta che su telefono
  diventa a schede; grafico dei risarcimenti per anno (una serie, etichette solo sui 3 anni più alti, tooltip nativi, tabella completa).
- Peso: CSS, JS, favicon/marchio e icone sono file esterni con l'impronta nel nome (`assets/site.<hash>.css`, `app.<hash>.js`,
  `favicon.<hash>.svg`, `icons.<hash>.svg`, scritti da `genera.py`); in ogni pagina resta solo lo script minimo del tema.
  `sito/` è passato da 151 MB a 77 MB su disco (60 MB di contenuto; le pagine ZIP da circa 44 a 20 KB).

## Punti da tenere d'occhio

1. Le polizze di agosto 2026 potrebbero essere ancora incomplete (FEMA riceve le segnalazioni in ritardo): i conteggi del mese di
   riferimento possono crescere leggermente al prossimo aggiornamento. Le polizze "homes" sono calate del 5,6% in un anno
   (3.182.048 → 3.004.117), coerente con il calo delle polizze NFIP, ma una parte può essere ritardo di segnalazione.
2. Alcune righe hanno decorrenza futura (rinnovi registrati in anticipo, es. 2027): escluse perché fuori dalla finestra.
3. Contea: `censusGeoid` è un indirizzo geocodificato da FEMA; in pochi casi il codice manca o è sbagliato (contano solo per Stato e nazione).
4. Il Connecticut usa le contee storiche (codici 2020) nei dati FEMA: le pagine usano quei nomi.
5. I testi sull'obbligo assicurativo e sul tetto agli aumenti citano FloodSmart.gov (letto il 15/10/2026), non fema.gov (403 dal server).
6. `controllo_api.py` sceglie lo ZIP e la contea di prova tra quelli con 300-420 e 150-300 polizze: a ogni aggiornamento possono cambiare.

## Revisione indipendente del 15/10/2026 (fatti, peso, design)

- Oltre 100 valori pubblicati (19 aree) ricalcolati con richieste proprie all'API OpenFEMA v3 (`$filter`, `$count`, righe grezze per le aree piccole; per le aree
  grandi la mediana e i percentili sono controllati contando le polizze sotto e sopra il valore pubblicato): nazionale (case, polizze,
  mediana, 25°/75° percentile, anno prima), Delaware e Rhode Island (tutte le statistiche, zone, risarcimenti), contee Calaveras CA,
  Jackson FL (righe grezze), Fairfield CT (righe grezze), Harris TX e Lee FL (conteggi), ZIP 32824, 33713, 95608, 28539 (righe grezze,
  zone, anno prima, risarcimenti), zone VE e AO e AE corretta, risarcimenti nazionali (2.725.989; pagati 2.117.326; $89.864.867.337).
  Tutti coincidono; unico errore trovato: A99 dentro AE (corretto, AE nazionale ora 1.350.523 case, mediana $1.278, verificata).
- Citazioni FloodSmart rilette il 15/10/2026 (premiumcosts, what-is-my-flood-zone, eligibility): coincidono.
- Correzioni: nomi "X County (unincorporated areas)" → "unincorporated X County" (niente parentesi annidate nei titoli), "Of/And"
  minuscoli nei nomi delle comunità, anni a pari merito nei risarcimenti, finestra di decorrenza esatta in metodologia (dal 1° settembre),
  `<title>` più corti con la cifra in testa, tabelle su telefono (tipo di edificio a schede, prima colonna fissa e avviso di
  scorrimento nelle tabelle larghe, tabella "one year on" più compatta), tessere chiare della mappa più visibili nel tema scuro.
- Dopo le correzioni: `verifica.py --browser` tutto superato (2.921 pagine HTML, 2.920 nella sitemap, 84 caricamenti Playwright).

## IndexNow (26/10/2026)
- IndexNow: file chiave scritto dal generatore; invio con studio-business/strumenti/indexnow.py. Costante `CHIAVE_INDEXNOW` in `genera.py` accanto a `SCRIPT_CONTATORE` (chiave pubblica, uguale in tutti i siti della rete); `extra()` scrive `sito/<chiave>.txt` accanto a `robots.txt`, fuori dalla sitemap e non linkato. Nuovo controllo in `verifica.py` (`controlla_indexnow`): file presente, contenuto = chiave, non citato nella sitemap.

## Monetizzazione: come si attiva (30/10/2026)
- **Dove si scrive:** un solo file per tutta la rete, `studio-business/strumenti/monetizzazione.json` (`adsense_client`, `adsense_siti`, domini di affiliazione ammessi). In una riga: `python3 studio-business/strumenti/monetizzazione.py attiva ca-pub-XXXXXXXXXXXXXXXX floodcost`, poi `python3 floodcost/genera.py`. Il nome del sito nel file è `floodcost` (`SITO_ID` in `genera.py`).
- **Cosa cambia con AdSense acceso:** script ufficiale nel `<head>` di ogni pagina (annunci automatici, nessun blocco manuale), `sito/ads.txt` con `google.com, pub-…, DIRECT, f08c47fec0942fa0`, sezione «Advertising (Google AdSense)» in `privacy.html` e frase sulla California aggiornata; la frase sui cookie diventa «GoatCounter non usa cookie, la pubblicità sì». Prima di pubblicare: in AdSense accendere il messaggio di consenso certificato di Google (Privacy e messaggi, regolamenti europei: UE/SEE, Regno Unito, Svizzera), che la privacy descrive.
- **Link di affiliazione:** `dati/affiliati.json` (campo `url`) → riquadro «get a quote». Ammessi solo verso i domini di `domini_affiliazione`, con `rel="sponsored noopener"` e la riga di trasparenza (la aggiunge `riquadro_trasparenza()` se manca); con almeno un link la privacy aggiunge la sezione sui link di affiliazione.
- **Come si verifica:** `python3 floodcost/verifica.py`; controllo comune in `monetizzazione.py` (script e `ads.txt` solo con AdSense acceso, privacy coerente, nessun dominio fuori elenco o bloccato, Amazon.it solo con `tag=`).
- **Con il codice vuoto o il sito fuori elenco l'output non cambia:** il 30/10/2026 `sito/` è stato rigenerato identico byte per byte.

## AdSense acceso (30/10/2026)
- **AdSense acceso il 30/10/2026** (codice editore `ca-pub-3750093987658434`, già usato da EsameB1, Visa Income e Before You Fly): `python3 studio-business/strumenti/monetizzazione.py attiva ca-pub-3750093987658434 floodcost`, poi `python3 floodcost/genera.py`. Script ufficiale nel `<head>` di ogni pagina, `sito/ads.txt` (`google.com, pub-3750093987658434, DIRECT, f08c47fec0942fa0`), privacy `/privacy.html` con la sezione «Advertising (Google AdSense)» e la frase sulla California aggiornata.
- **Controlli del 30/10/2026:** `python3 floodcost/verifica.py --browser` → «Tutti i controlli superati»; `monetizzazione.py verifica floodcost` → AdSense acceso, 0 errori; Playwright a 375 px su home (script AdSense caricato davvero): nessun errore JS, nessuno scorrimento orizzontale. Da fare in AdSense: aggiungere il sito (Siti → Aggiungi) e controllare che il messaggio di consenso UE copra anche questo dominio. Nessun commit, nessuna pubblicazione.
- **`verifica_browser.js` e AdSense (30/10/2026):** con lo script AdSense nelle pagine Playwright segnalava come «richiesta fallita» i beacon di Google interrotti al cambio pagina (`pagead2.googlesyndication.com/pagead/ping`). Ora le richieste ai server degli annunci (costante `PUBBLICITA`: googlesyndication.com, doubleclick.net, googleadservices.com, adtrafficquality.google, fundingchoicesmessages.google.com) ricevono una risposta vuota e non contano come errori: la prova non dipende da annunci esterni. Lo script e il suo indirizzo li controlla `monetizzazione.py`.
