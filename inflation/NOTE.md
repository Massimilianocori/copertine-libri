# Inflation Calculator US·UK·DE – note di lavoro

Costruito il 13/11/2026 dal fronte B di `studio-business/intelaiatura/fronti-2026-11-13-nuovi-radar.md` (riga "inflation" di `DA-PUBBLICARE.md`).
Sito statico generato da `genera.py` in `sito/`: calcolatore dell'inflazione per USA (home, inglese), Regno Unito (`/uk/`, inglese) e
Germania (`/de/inflationsrechner/`, tedesco), con gli indici ufficiali dentro la pagina (il calcolo gira nel browser).
**Nome Netlify scelto: `inflation-calculator-us-uk-de`** (libero il 13/11: `curl -sI` → 404) → `URL_SITO = https://inflation-calculator-us-uk-de.netlify.app`
in `genera.py`. Il sito su Netlify NON è ancora creato.

## Pagine (143 indicizzabili + 404)

| Pagina | Contenuto |
|---|---|
| `/` | calcolatore USA (CPI-U, 1913 → ultimo mese), come calcola, ottobre 2025 mancante, dollaro per decennio, anni, 3 FAQ |
| `/us/inflation-rate-by-year/` | tasso per anno 1914-2025 (media annua e dicembre su dicembre), grafico a barre, mesi dell'anno in corso, medie per decennio |
| `/us/AAAA-dollars-today/` (113, 1913-2025) | valore di $1…$10.000 oggi, grafico, inflazione dell'anno e posizione in classifica, CPI dei 12 mesi; FAQ solo per 1950, 1960, 1970, 1980 |
| `/us/100-dollars-in-AAAA/`, `/us/1000-dollars-in-AAAA/` (20, decenni 1920-2010) | tabella anno per anno, grafico, il contrario, altri decenni |
| `/uk/`, `/uk/rpi-calculator/`, `/uk/inflation-rate-by-year/` | calcolatore CPI/RPI, calcolatore RPI, tassi CPI dal 1989 e RPI dal 1801 |
| `/de/inflationsrechner/`, `/de/inflationsrate-deutschland/` | Inflationsrechner (euro e D-Mark, dal 1962), Inflationsrate per anno dal 1992, mesi dal 2021, Germania Ovest 1963-1991 |
| `/about/`, `/how-we-check/`, `/privacy/`, `404.html` | in inglese (le pagine tedesche li collegano come "englisch") |

**Tetto delle pagine (perché non migliaia):** 30 ricerche di volume (`dati/domanda.json`, 13/11/2026). USA: il modello forte è "ANNO dollars
today" (1980: 720, 1960: 480, 1970: 480 + varianti; 1920: 210) → una pagina per anno. "100 dollars in 1970" ~300/mese con le varianti, "1000 dollars
in 1980" ~400, ma "100 dollars in 1985" solo ~100 → pagine importo solo per $100 e $1.000 ai decenni (gli altri importi stanno nella tabella della
pagina anno). Regno Unito ("value of £1 in 1950", "£100 in 1970", "1970 pounds today", "uk inflation rate 1980") e Germania ("dm kaufkraft
heute", "kaufkraft 1990", "inflationsrate 2023"): volume 0 → nessuna pagina per anno. Nessuna pagina noindex oltre alla 404.

## Fonti e licenze (lette il 13/11/2026, nessun blocco aggirato)

| Serie | Da dove | Licenza |
|---|---|---|
| USA CPI-U, CUUR0000SA0 (NSA, 1982-84=100), mesi da gen 1913 + medie annue | pagina dati BLS `data.bls.gov/timeseries/...annualAveragesRequested=true` (copia di controllo dall'API v2) | pubblico dominio (lavoro del governo federale) |
| Regno Unito CPI D7BT (2015=100, dal 1988), tasso D7G7; RPI lungo CDKO (gen 1974=100, anni dal 1800, mesi da giu 1947), RPI CHAW, tasso CZBH | CSV ONS (dataset MM23) | OGL v3.0, attribuzione "Source: Office for National Statistics licensed under the Open Government Licence v.3.0" in ogni pagina |
| Germania VPI (2020=100): mesi e anni attuali | tabella HTML Destatis "Verbraucherpreise-12Kategorien" (gen 2021 → ultimo mese) | © Destatis, riproduzione con fonte; GENESIS: dl-de/by-2-0 |
| Germania VPI dal 1991 e Germania Ovest "alle privaten Haushalte" (1995=100) 1962-1999 | xlsx "Verbraucherpreisindex – Lange Reihen ab 1948" (ultima edizione 10/7/2025) | come sopra |
| Cambio 1 € = 1,95583 DM | Regolamento (CE) 2866/98 (EUR-Lex PDF) e pagina BCE | – |

Non letti: file piatto `download.bls.gov` (403), pagina copyright BLS (403), API GENESIS (401, serve un account): scritti in `fonti.json`
(`_non_lette`) e nella pagina How we check. Calcolatore ufficiale BLS (`cpicalc.pl`) letto: 5 risultati in `dati/esempi_bls.json`.

**Germania prima del 1991**: unica serie calcolata da noi: indice Germania Ovest × (VPI 1991 / Ovest 1991) = × 0,69551, dichiarato nella pagina.
**USA ottobre 2025**: non raccolto dal BLS (blocco dei finanziamenti); il calcolatore non dà risultato per quel mese e le pagine lo dicono.

## File

`raccolta/scarica.py` (scarica tutto in `dati/grezzi/` + `dati/fonti.json` con URL, data, HTTP, SHA-256, licenza; ricontrolla le frasi di Fed, BCE, EUR-Lex),
`serie.py` (lettura uniforme + continuità), `motore.py` (calcolo di riferimento), `stile.py` (CSS, icone, JS del browser = copia del motore),
`genera.py`, `verifica.py`, `verifica_browser.js`, `grafica/og.html` → `og.png`, `dati/domanda.json` (volumi), `dati/faq_generate.json` (FAQ ↔ ricerca).

## Controlli (`python3 inflation/verifica.py --browser`, 13/11/2026: 0 errori)

Continuità di tutte le serie (unico buco ammesso: ottobre 2025 USA, con la nota BLS); BLS pagina dati = API su 1.365 mesi; medie annue rifatte dai
mesi (USA esatte dal 2007, entro l'arrotondamento prima); 11 valori noti; **5 risultati del calcolatore ufficiale BLS rifatti al centesimo**;
453 tassi CPI e 940 tassi RPI = ONS entro l'arrotondamento degli indici; CDKO = CHAW × 3,945; Destatis: due file uguali dove si sovrappongono e
141 tassi pubblicati rifatti entro 0,1 punti; JS pubblicato = Python su 6.005 casi; canonical = sitemap, link interni, titoli, descrizioni, h1,
JSON-LD FAQ = testo visibile, ogni FAQ da una ricerca con volume, pagine tedesche senza parole inglesi; monetizzazione
(`python3 studio-business/strumenti/monetizzazione.py verifica inflation`: 0 errori); Playwright 11 pagine × 375/1280 × chiaro/scuro (niente
scorrimento orizzontale, errori JS, testo < 11 px) e 9 casi dei calcolatori (anche il passaggio CPI→RPI e la D-Mark).

## Aggiornamento mensile (dopo le uscite: BLS e ONS a metà mese, Destatis a fine mese/metà mese)

1. `python3 -I inflation/raccolta/scarica.py` (con `--api` solo se serve rifare la copia di controllo BLS: 12 richieste, limite giornaliero condiviso).
2. `python3 inflation/genera.py && python3 inflation/verifica.py --browser` → 0 errori. `genera.py` si ferma se una serie ha un buco.
3. Un commit, una pubblicazione (crediti Netlify), poi IndexNow.
Attenzione: se Destatis pubblica una nuova base (2025=100) o un nuovo link dell'xlsx "Lange Reihen", aggiornare `URL_DE_XLSX` in `scarica.py`;
la tabella HTML attuale copre solo da gennaio 2021. Se la copia API BLS non è aggiornata, il controllo "pagina dati = API" fallisce: rifarla con `--api`.

## Monetizzazione

AdSense acceso (`inflation` in `SITI` di `monetizzazione.py` e in `adsense_siti`/`_siti_della_rete` di `monetizzazione.json`), `ads.txt`,
privacy con la sezione AdSense e la frase per la California. Nessuna affiliazione. Nessun consiglio finanziario (avviso in ogni pagina).
IndexNow: host in `SITI` di `indexnow.py` e in `NON_ONLINE` finché il sito non è su Netlify.

## Da fare per pubblicare (passi del titolare)

1. Netlify: nuovo sito dal repository, Base directory `inflation/sito`, Build command vuoto, Publish directory `.`, nome `inflation-calculator-us-uk-de`.
2. Search Console: proprietà `https://inflation-calculator-us-uk-de.netlify.app/` (meta di verifica già nelle pagine), inviare la sitemap.
3. Togliere l'host da `NON_ONLINE` in `indexnow.py` e lanciare l'invio.

## Limiti noti

- Pagine tedesche senza Impressum (nessun dato personale nel repository): da valutare se il sito incassa dal pubblico tedesco.
- Il controllo indipendente dei fatti (revisore) non è ancora stato fatto; i confronti automatici con le cifre ufficiali sono sopra.
