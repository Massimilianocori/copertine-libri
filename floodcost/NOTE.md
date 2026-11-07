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
| `verifica_browser.js` | Playwright a 375 (fino al 30/10/2026: 390) e 1280 px, tema chiaro e scuro: niente scorrimento orizzontale, niente errori JS o richieste fallite, ricerca e pulsante del tema funzionanti; screenshot in `cache/screenshot/` |
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

## Sezione "Disaster declarations and IRS tax relief by county" (30/10/2026)
Idea: `studio-business/intelaiatura/ricerca-2026-10-28.md` candidata 1 (voto 7,5) e rivalutazione in `ricerca-profonda-2026-10-28-mercato.md`
(candidata 2, pay-per-call non attivo: nessun link nuovo). Costruita per la regola del 30/10 (rete fitta di guadagno). Guadagno: AdSense già acceso.

**Pagine (487, tutte nella sitemap con `lastmod` = data di lettura dei dati):**
| Tipo | Quante | Regola |
|---|---|---|
| Indice `/disaster-relief/` | 1 | avvisi IRS aperti (scadenza ≥ data di lettura), 25 dichiarazioni FEMA più recenti, Stati, glossario, link ufficiali |
| Stato `/disaster-relief/<stato>/` | 48 | ogni Stato/territorio con una dichiarazione FEMA negli ultimi 24 mesi o un avviso IRS dell'anno in corso o precedente |
| Contea `/disaster-relief/<stato>/<contea>/` | 438 | dichiarazione negli ultimi 24 mesi (FEMA, o dello Stato citata dall'IRS) **e** domanda (sotto) |
Prima frase della pagina contea = risposta (dichiarazione sì/no, poi nella scheda: assistenza individuale sì/no con l'ultima data per fare
domanda `lastIAFilingDate`, scadenza IRS rinviata); fonte con data di lettura; frasi IRS tra virgolette con link; rimando alla pagina
FloodCost della stessa contea (premio NFIP) o dello Stato; disasterassistance.gov e irs.gov; avviso "check with the IRS or a tax professional".
Titoli ≤ 70 caratteri (con la scadenza IRS nel titolo quando c'è un avviso aperto). Menu e piè di pagina hanno "Disaster relief"; le pagine
NFIP di Stato e contea e la home rimandano alla sezione (`rimando_disastri`, `teaser_disastri`).

**Fonti e come si leggono** (`raccolta/disastri.py`):
- OpenFEMA `DisasterDeclarationsSummaries` v2, `$filter=declarationDate ge '<oggi - 24 mesi>'`, a pagine da 1.000, conteggio controllato
  (30/10/2026: 3.346 righe, 288 dichiarazioni, 1.652 contee, 66 aree tribali/speciali; riga più recente aggiornata 30/10/2026 19:06 UTC).
  Pubblico dominio. **Termini d'uso** (`fema.gov/about/openfema/terms-conditions`, aggiornati 22/1/2025; letti con Playwright il
  30/10/2026, curl dà 403): citare l'endpoint con la versione, la data e preferibilmente l'ora di lettura, dichiarare "This product uses
  the Federal Emergency Management Agency's OpenFEMA API, but is not endorsed by FEMA. The Federal Government or FEMA cannot vouch…"
  (testo esatto nel piè di pagina), niente logo/sigilli FEMA o DHS, non modificare i dati presentandoli come FEMA, niente
  reidentificazione, dati non usati per decidere diritti o benefici di una persona. Rispettati: fonte "Disaster Declarations Summaries
  (v2)" con link, "Read by our script on <data> at <ora> UTC" (`letto_alle_utc`), nessun logo FEMA, "not affiliated with FEMA".
- IRS: indice `irs.gov/newsroom/tax-relief-in-disaster-situations` (sezione "Tax relief by date", voci con codice tipo `FL-2026-07`),
  poi ogni comunicato degli Stati/territori dell'anno in corso e del precedente (57 il 30/10/2026; i codici `IR-` nazionali esclusi).
  Da ogni comunicato: data, "Updated on", frase "now have until …", frase "… qualify for tax relief", chi ha dichiarato (FEMA o lo Stato).
  **Contee collegate solo se il nome della frase è esattamente una contea del Census dello stesso Stato**; i nomi che non corrispondono
  restano nella frase citata e la scheda dice "The notice also names “Park”, which we could not match…" (`nomi_non_trovati`; revisione
  30/10/2026: prima un solo nome sbagliato scollegava tutto il comunicato, e IN-2026-01, aperto fino all'1/2/2027, mancava per 26 contee
  dell'Indiana). Nomi non trovati il 30/10: IN-2026-01 "Park" (Parke), TN-2026-01 "Summer" (Sumner), MS-2025-01 "Davis", WA-2025-03
  "Samish" (area tribale), VA-2025-03 "City of Bristol" e MO-2025-01 "City of St. Louis" (città indipendenti). Senza elenco leggibile:
  aree tribali, isole NMI, "designated area", e i comunicati per tutto lo Stato.
- Da sapere: dal 2026 diversi comunicati IRS seguono una **dichiarazione dello Stato** (TX-2026-05 62 contee, AL-2026-01 40, NE): molte
  contee IRS non hanno l'assistenza individuale FEMA (campo `contee_con_ih_fema`); le contee senza righe FEMA hanno la pagina con la sola parte IRS.

**Domanda (Google Autocomplete, `dati/disastri-domanda.json`, 1.070 query con data, riusate 28 giorni).** Query generali: "fema disaster
declaration " (by county, search, 2026, indiana, hawaii…), "fema disaster declaration by county" → "fema disaster declarations by county",
"federal disaster declarations by county"; "federal disaster area " → "tax relief", "lookup"; "disaster declaration county" → "counties texas",
"travis county", "texas harris county"; "irs disaster relief " → "2026", "extension", "2026 texas", "washington state", "hawaii"; "irs tax
extension disaster" → "disaster areas". Per Stato: "irs tax extension <stato> hurricane", "irs tax extension <stato> storm" (quasi sempre
vuote), "irs disaster relief <stato>" (piene per 21 Stati), "fema disaster declaration <stato>". Per evento: "<evento> irs"/"<evento> fema"
(hurricane isaias irs → extension, relief, deadline; tropical storm arthur irs extension; winter storm fern irs extension). Per contea:
"<contea> fema", "<contea> disaster" (solo contee con assistenza individuale o in un avviso IRS: 536+).
Regola della pagina contea: (contea) suggerimento con il nome e fema/irs/disaster declaration|relief|assistance… (non "flood map"; nomi
ripetuti in più Stati solo con lo Stato nel suggerimento) 52; (irs-evento) in un avviso IRS aperto per un evento con domanda 70;
(irs-stato) in un avviso IRS aperto e "irs disaster relief <stato>" con domanda 83; (fema-ia-stato) assistenza individuale FEMA e
"fema disaster declaration <stato>" con domanda 229.

**File:** `raccolta/disastri.py` → `dati/disastri.json` (con `letto_il` e `impronta` SHA-256 del contenuto) e `dati/disastri-domanda.json`;
pagine in `genera.py` (sezione "Disaster declarations…": `pagina_dis_indice/stato/contea`); controllo `controlla_disastri` in `verifica.py`.

**Aggiornamento consigliato: ogni lunedì con la routine** (gli avvisi IRS escono ogni settimana e cambiano: contee aggiunte, date di inizio):
`python3 floodcost/raccolta/disastri.py` (2-3 minuti; con la cache della domanda; `--senza-domanda` per non toccare l'autocomplete) →
`python3 floodcost/genera.py` → `python3 floodcost/verifica.py --browser` → commit di `floodcost/dati` e `floodcost/sito`. Una
pubblicazione Netlify a settimana (15 crediti). Leggere le righe "senza contee" stampate dallo script: un comunicato nuovo non collegato
va guardato a mano (resta comunque in pagina a livello di Stato).

**Controlli del 30/10/2026:** `verifica.py --browser` tutto superato (3.404 pagine HTML, 3.403 nella sitemap; 116 caricamenti Playwright,
29 pagine × 375/1280 px × chiaro/scuro, compresi indice, 3 Stati e 4 contee della sezione); `monetizzazione.py verifica floodcost` 0 errori.
`controlla_disastri`: impronta, pagine attese e solo quelle, sitemap, titoli ≤ 70, numeri/codici/scadenze delle pagine uguali ai dati,
prima frase che risponde, frasi obbligatorie, nessuna frase da consulenza, e 10 valori ricontrollati sull'API (senza dati locali):

| Dichiarazione · contea | Pubblicato (data, IA/PA/HM) | API OpenFEMA | Esito |
|---|---|---|---|
| EM-3656-AL · Baldwin AL | 9/10/2026, 0/1/0 | uguale | OK |
| DR-4951-HI · Honolulu HI | 7/10/2026, 0/1/0 | uguale | OK |
| EM-3633-KY · Daviess KY | 24/1/2026, 0/1/0 | uguale | OK |
| EM-3633-KY · Powell KY | 24/1/2026, 0/1/0 | uguale | OK |
| DR-4925-MI · Osceola MI | 30/6/2026, 1/1/0 | uguale | OK |
| DR-4899-MS · Montgomery MS | 6/2/2026, 1/1/0 | uguale | OK |
| DR-4872-MO · Oregon MO | 21/5/2025, 1/1/0 | uguale | OK |
| DR-4898-TN · Clay TN | 6/2/2026, 1/1/0 | uguale | OK |
| DR-4935-TX · Frio TX | 1/9/2026, 0/1/0 | uguale | OK |
| DR-4906-WA · King WA | 7/4/2026, 1/1/0 | uguale | OK |
Controllati a mano anche Kerr County TX (3 dichiarazioni; DR-4879-TX con IA, ultima data 28/9/2025; TX-2026-05 → 1/2/2027), Santa Rosa FL
(DR-4955-FL con IA fino al 28/12/2026; FL-2026-07 → 8/2/2027), Mobile AL (EM-3656-AL solo PA; AL-2026-01 → 4/2/2027).
Non letti dal server: disasterassistance.gov (403: solo link). Nessun commit, nessuna pubblicazione.
**Revisione indipendente 30/10/2026:** termini OpenFEMA letti (sopra); 19 contee in 18 Stati/territori confrontate con l'API e con i
comunicati IRS scaricati (tutte giuste; tutte le 1.719 aree e 288 dichiarazioni coincidono con l'API); corretti: collegamento parziale
dei comunicati IRS (+4 pagine Indiana), dichiarazione OpenFEMA col testo esatto, ora di lettura, prima frase degli Stati e dell'indice
con la fonte ("FEMA lists…"), "No FEMA declaration" nelle griglie, riquadro "No open IRS postponed deadline today" al posto di "None open".

## Sezione "California FAIR Plan policies and non-renewals by ZIP code" (7/11/2026, revisionata, correzioni applicate)
Idea n. 1 di `studio-business/intelaiatura/fronti-2026-11-07-settori-nuovi.md` (voto 7 come sezione; 300 / 2.750 / 11.000 €/anno).
**Riapre FloodCost dal congelamento del 6/11** (0 visite), come ApprovedCondos con il pannello solare: tema nuovo dentro un sito che ha già
le pagine ZIP della California. Indirizzo `/california-home-insurance/` (non `/california/`: è la pagina NFIP dello Stato). Voce "California" nel menu e nel piè di pagina.

**Pagine (3 nuove + blocco in 81 pagine esistenti):**
| Tipo | Quante | Regola |
|---|---|---|
| Indice `/california-home-insurance/` | 1 | prima frase con il dato e la data; ricerca nel browser su 2.179 ZIP (97635, Oregon, escluso) (`data/california-zip.json`: ZIP, luogo, contea, polizze FAIR Plan 2022 e 2026, premio medio, non rinnovi 2023 e tasso, link); tabella delle 58 contee; classifiche (più polizze, crescita dal 2022 con almeno 500 polizze, tasso di non rinnovo 2023 con almeno 1.000 polizze nuove + rinnovate); limiti; aiuto ufficiale; 7 FAQ; fonti con impronta |
| Città con domanda `/california-home-insurance/<città>/` | 2 | Los Angeles e San Diego: le sole aree con ≥ 1.000 polizze FAIR Plan **e** un suggerimento vero ("california fair plan los angeles", "california fair plan san diego"). Provate 44 contee e 175 città con ≥ 1.000 polizze con "california fair plan <luogo>", "fair plan <luogo>", "insurance non renewal <luogo>" (gl=us): nessuna contea, nessun'altra città. Tabella di tutti gli ZIP del luogo, anni 2022-2026 e 2020-2023, premio per gruppo di rischio, 3 FAQ |
| Blocco "Home insurance availability in ZIP …" | 81 | tutte le pagine ZIP della California che FloodCost aveva già (soglia NFIP 300 case), dopo la tabella delle zone: prima frase con dato e data, 4 cifre, tabelle anni, limiti, fonti, link all'indice |
| Rimandi | 1 + contee CA | pagina NFIP della California e pagine NFIP delle contee della California: una riga con le polizze FAIR Plan della contea e il link; home: riga "California" |
Nessuna pagina per i 2.000 ZIP senza pagina NFIP (sarebbero sottili): stanno nella ricerca e nelle tabelle.

**Fonti (lette dal server il 7/11/2026, `raccolta/california.py`; file in `cache/california/`, fuori da git; impronte in `dati/california.json`):**
| Fonte | File | SHA-256 (inizio) | Contenuto |
|---|---|---|---|
| FAIR Plan, Key Statistics & Data (`cfpnet.com/key-statistics-data/`) | `CFP-5-yr-PIF-Zip-FY26-DWE-261020.pdf` (36 pagine) | 6e551e84ece1 | polizze residenziali al 30/9 2022-2026, 1.687 righe ZIP (una è 97635, Oregon), totale 665.673 |
| idem | `CFP-5-yr-TIV-Zip-FY26-DWE-261020.pdf` | b5cd3574c9f8 | valore assicurato, stessi ZIP: $714.651.760.473 |
| idem | `Policies-by-category-DWE-as-of-260930-DL-261019v001.pdf` | dcab04e49c4f | polizze per ZIP × gruppo di rischio (Low/Medium/High) × tipo (Owner-occupied Single Family, Tenant-occupied, Renters, Condo, Other), 1.662 ZIP |
| idem | `Premium-by-category-DWE-as-of-260930-DL-261019v001.pdf` | 3ad971d04d29 | premio delle stesse celle, 1.664 ZIP |
| CDI, Data and Analysis on Wildfires and Insurance | `Residential-Insurance-Voluntary-Market-New-Renew-NonRenew-by-ZIP-2020-2023.xlsx` | 316d0ee62f11 | 8.032 righe: contea, ZIP, anno, nuove, rinnovate, non rinnovate (mercato volontario) |
| idem | fact sheet `…FAIR-Plan-v-011325-2.pdf` (13/1/2025) | 1808dbaa3ea6 | definizioni: non rinnovi totali, "75-80% … initiated by policyholders", rapporto non rinnovi/(nuove+rinnovate); appendice A = totali dello Stato |
| GeoNames postal codes `US.zip` (CC BY 4.0) | `US.zip` | cambia ogni giorno | nome del luogo e contea dello ZIP (attribuzione nelle fonti) |
Il nome del file FAIR Plan porta la data 20/10/2026 ("report dated October 20, 2026" nelle pagine); il server dà Last-Modified 27/10/2026.
Pagine citate tra virgolette (lette il 7/11/2026, `CA_CITAZIONI` in `genera.py`): FAIR Plan dwelling, DIC, how to apply; CDI consumer help
(1-800-927-4357), Home Insurance Finder (`homeinsurancefinder.insurance.ca.gov`, rinvia a interactive.web.insurance.ca.gov).

**Definizioni (uguali in `genera.py`, nella sezione "How to read these numbers" e in Methodology):**
- Polizze FAIR Plan = polizze residenziali in vigore al 30/9 (anno fiscale). Variazioni ricalcolate dai conteggi (le crescite stampate nel PDF coincidono entro 1 punto: 12.954 confronti, 0 differenze).
- **Premio medio** = premio delle polizze in vigore al 30/9/2026 ÷ numero di polizze, solo "Owner-occupied Single Family Residential" (somma dei 3 gruppi), pubblicato solo con ≥ 10 polizze. Stato: $1.562.500.858 / 520.412 = **$3.002** (Low $1.431, Medium $3.115, High $4.013). Non è un prezzo: lo dicono tutte le pagine.
- **Tasso di non rinnovo** = non rinnovate ÷ (nuove + rinnovate), il rapporto del fact sheet CDI; pubblicato solo con ≥ 100 polizze nuove + rinnovate. Stato 2023: 788.485 / 8.300.730 = **9,5 %**.
- Limiti scritti in ogni pagina: i non rinnovi finiscono nel **2023**; sono totali (75-80 % chiesti dagli assicurati secondo il CDI), solo mercato volontario, nessun nome di compagnia; la FAIR Plan dà solo copertura incendio di base (DIC a parte, non contato).
- Contea dello ZIP: quella del PDF FAIR Plan per categoria (gli ZIP a cavallo vanno alla contea più popolosa), poi CDI, poi GeoNames. Somme per contea e città = somme degli ZIP.
- **Difetto della fonte:** il PDF delle polizze per categoria finisce prima delle ultime 2 righe (95962 e 95972, Yuba, 305 polizze, presenti nel PDF dei premi): per quei 2 ZIP niente premio medio; la raccolta controlla che la differenza con la riga All sia esattamente quella.

**FAQ (solo da ricerche vere, `dati/california-domanda.json`):** indice: "how much is the california fair plan", "california fair plan cost by zip code",
"what does california fair plan cover", "what is a dic policy in california", "state farm non renewal zip codes california", "which insurance
companies are writing new policies in california", "what to do if homeowners insurance is not renewed". Città: costo e non rinnovi locali + copertura.
Risposte solo con numeri delle fonti o frasi ufficiali tra virgolette; nessun consiglio, nessun nome di compagnia. JSON-LD FAQPage = testo.

**Monetizzazione:** AdSense già acceso (annunci automatici). Nessun programma nuovo. Voce `casa_california` in `dati/affiliati.json`
(**spenta**, `url` vuoto; candidati Lemonade su Awin, Policygenius o simili, solo dopo l'iscrizione di Massimiliano): il riquadro
`box_casa_ca()` compare solo nelle pagine della sezione quando `url` è compilato; `box_quote()` (alluvione) la ignora.

**Controlli (`verifica.py`, `controlla_california`):** impronta dei dati e delle fonti (file in cache con la stessa SHA-256, riscaricati se mancano);
**ricalcolo di tutti i 2.180 ZIP dai file sorgente con motori diversi dalla raccolta** (raccolta: pdftotext per i PDF a 5 anni, pdfplumber per quelli
per categoria, openpyxl per l'XLSX; verifica: il contrario e l'XML grezzo dell'XLSX); somme = righe Total/All; totali CDI = appendice A del fact sheet
(2023: 724.037 / 7.576.693 / 788.485); pagine attese e sitemap con lastmod; titoli ≤ 70; prima frase con dato e data; scheda, ogni riga ZIP, ogni contea,
81 blocchi ZIP e la ricerca uguali al ricalcolo; limiti e avvisi; nessuna frase da consulenza; nessun link di affiliazione; FAQ da ricerche salvate = JSON-LD;
link indice ↔ città, blocchi → indice, Stato e contee NFIP → sezione; con la rete, 9 frasi ufficiali citate ancora presenti e avviso se la pagina FAIR Plan
collega file nuovi. `verifica_browser.js`: indice (con prova della ricerca "9524" e "paradise"), Los Angeles, San Diego, ZIP 90265.
Esito del 7/11/2026: tutti i controlli superati (3.408 pagine HTML, 3.407 nella sitemap).

**Aggiornamento:** la pagina FAIR Plan dice che i dati si aggiornano ogni trimestre (i file a 5 anni sono per anno fiscale, al 30/9); il CDI pubblica
il file per ZIP una volta l'anno (il 2024 non c'è ancora: quando esce, il nome cambia in `…-by-ZIP-2021-2024.xlsx` o simile e la raccolta lo prende da sola).
Comandi: `python3 floodcost/raccolta/california.py` (circa 20 secondi più l'autocomplete, cache 28 giorni; `--senza-domanda` per non toccarlo) →
`python3 floodcost/genera.py` → `python3 floodcost/verifica.py --browser` → commit di `floodcost/dati` (e di `floodcost/sito` solo nel push serale).
Se l'autocomplete fa nascere pagine nuove di città o contea, controllare che abbiano senso prima di pubblicare.

**Numeri principali (7/11/2026):** Stato 665.673 polizze FAIR Plan (265.909 nel 2022, ×2,5; +7,2 % in un anno), $714,7 miliardi; Los Angeles (69 ZIP)
41.982 polizze, premio medio $1.934, non rinnovi 2023 26.805 (9,6 %); San Diego (52 ZIP) 14.556 polizze, $2.170, 21.210 (8,6 %).
Tasso di non rinnovo 2023 più alto: 95954 Magalia 78,6 % (969 su 1.233), poi Shingletown, Paradise.

**Revisione indipendente del 7/11/2026 (pubblicabile con correzioni), applicate lo stesso giorno:**
1. Il conteggio CDI per ZIP è il "Non-Renewed/Canceled" del fact sheet (stessi totali): ovunque "not renewed or cancelled (the Department's
   'non-renewed/canceled' count, 75-80% initiated by policyholders, e.g. after a sale)" (costante `NR_DEF`); 788.485 non è mai presentato come
   "polizze non rinnovate" e basta; nei limiti la spiegazione completa e il rapporto (non-renewed + canceled) ÷ (new + renewed).
2. Limiti e Methodology: solo mercato volontario, compagnie con ≥ $5 milioni di premi (~98 % del mercato), esclusi HO-4 e HO-6.
3. "Fastest growth since 2022": solo ZIP con ≥ 100 polizze nel 2022 (`CA_MIN_BASE`), con la nota sulle percentuali gonfiate dalle basi piccole.
4. Los Angeles e San Diego: prima frase e scheda dicono che la pagina copre i 69 (52) ZIP con nome postale Los Angeles (San Diego) e danno
   il totale della contea (Los Angeles County 155.124, San Diego County 63.401 polizze FAIR Plan).
5. 97635 (Oregon, assegnato dal PDF a "Lake") escluso da contee e ricerca (`ca_in_california`, 90000-96199; ricerca su 2.179 ZIP); lastmod
   delle 81 pagine ZIP con il blocco = data dei dati California; teaser della home "residential policies"; H1 senza "crisis".
`verifica.py` controlla anche: frasi "not renewed or cancelled", "non-renewed/canceled", "$5 million", HO-4/HO-6 in ogni pagina e blocco;
base minima della classifica di crescita; H1 senza "crisis"; ricerca senza ZIP fuori dalla California; lastmod delle pagine ZIP con il blocco.
