# Inflation Calculator US·UK·DE – note di lavoro

Costruito il 13/11/2026 dal fronte B di `studio-business/intelaiatura/fronti-2026-11-13-nuovi-radar.md` (riga "inflation" di `DA-PUBBLICARE.md`).
Sito statico generato da `genera.py` in `sito/`: calcolatore dell'inflazione per USA (home, inglese), Regno Unito (`/uk/`, inglese) e
Germania (`/de/inflationsrechner/`, tedesco), con gli indici ufficiali dentro la pagina (il calcolo gira nel browser).
**Nome Netlify scelto: `inflation-calculator-us-uk-de`** (libero il 13/11: `curl -sI` → 404) → `URL_SITO = https://inflation-calculator-us-uk-de.netlify.app`
in `genera.py`. Il sito su Netlify NON è ancora creato.

## Sezione tedesca SPENTA (13/11/2026)

Il titolare ha deciso di non pubblicare per ora le pagine tedesche: senza Impressum (§ 5 DDG) un sito con pubblicità rivolto al pubblico
tedesco rischia diffide a pagamento. Interruttore `SEZIONE_DE = False` in cima a `genera.py`: niente `/de/` (la cartella `sito/` viene
rifatta da zero, quindi nessun avanzo), niente link, redirect, Destatis, «Germany» o lang="de" nelle pagine; titoli e home dicono «US & UK»
(141 pagine indicizzabili + 404), immagine social `grafica/og_us_uk.png` (da `og_us_uk.html`, senza la pillola DE). Codice, dati Destatis e
controlli tedeschi restano: `verifica.py` li fa girare solo da accesa e da spenta controlla che nessun file di `sito/` contenga «/de/»,
«Inflationsrechner», «Destatis», «Germany» o lang="de". **Per riaccendere** (solo dopo «ok Impressum» di Massimiliano): aggiungere l'Impressum,
mettere `SEZIONE_DE = True`, `python3 inflation/genera.py && python3 inflation/verifica.py --browser` (0 errori, 143 pagine). Il resto di
queste note descrive anche la sezione tedesca, valido quando è accesa.

## Pagine (143 indicizzabili + 404 con la sezione tedesca; 141 + 404 da spenta)

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
(`_non_lette`) e nella pagina How we check. Calcolatore ufficiale BLS (`cpicalc.pl`) letto: 10 risultati in `dati/esempi_bls.json`.

**Germania prima del 1991**: unica serie calcolata da noi: indice Germania Ovest × (VPI 1991 / Ovest 1991) = × 0,69551, dichiarato nella pagina.
**USA ottobre 2025**: non raccolto dal BLS (blocco dei finanziamenti); il calcolatore non dà risultato per quel mese e le pagine lo dicono.

## File

`raccolta/scarica.py` (scarica tutto in `dati/grezzi/` + `dati/fonti.json` con URL, data, HTTP, SHA-256, licenza; ricontrolla le frasi di Fed, BCE, EUR-Lex),
`serie.py` (lettura uniforme + continuità), `motore.py` (calcolo di riferimento), `stile.py` (CSS, icone, JS del browser = copia del motore),
`genera.py`, `verifica.py`, `verifica_browser.js`, `grafica/og.html` → `og.png`, `dati/domanda.json` (volumi), `dati/faq_generate.json` (FAQ ↔ ricerca).

## Controlli (`python3 inflation/verifica.py --browser`, 13/11/2026: 0 errori)

Continuità di tutte le serie (unico buco ammesso: ottobre 2025 USA, con la nota BLS); BLS pagina dati = API su 1.365 mesi; medie annue rifatte dai
mesi (USA esatte dal 2007, entro l'arrotondamento prima); 11 valori noti; **10 risultati del calcolatore ufficiale BLS rifatti al centesimo**;
453 tassi CPI e 940 tassi RPI a 12 mesi = ONS entro l'arrotondamento degli indici; CDKO = CHAW × 3,945; Destatis: due file uguali dove si sovrappongono e
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
- Le pagine anno 1923, 1924, 1928 e 1929 (media annua 17,1), 1936/1939, 1932/1935, 1948/1950 hanno per forza le stesse cifre annuali: lo dichiarano,
  si collegano tra loro e si distinguono per i mesi e per il tasso dell'anno. Da guardare in Search Console se Google le tratta come doppioni.
- Annunci: solo annunci automatici di AdSense (lo script in testa); i riquadri `.ad-slot` sono nascosti, quindi la posizione la sceglie Google.

## Revisione indipendente (13/11/2026)

Fonti riscaricate e rilette con un lettore scritto a parte (pagina dati BLS, API BLS 2017-2026, 5 CSV ONS, xlsx Destatis letto dalle tabelle
impaginate e non dai fogli csv, tabella HTML Destatis): **4.118 indici pubblicati nel sito confrontati, 0 diversi**; 548 tassi annui, 0 diversi
dagli indici, ma 14 tassi RPI su 77 e 4 tassi CPI nella pagina RPI erano ricalcolati e differivano di 0,1-0,2 punti dal tasso pubblicato dall'ONS.
Calcolatore: 28 casi fatti a mano nel JS pubblicato (10 con il risultato del calcolatore BLS), 0 diversi.

Corretto:
- Regno Unito: i tassi annui RPI (dal 1949, serie CZBH) e CPI (D7G7) sono ora quelli pubblicati dall'ONS in tutte le pagine; prima del 1949 calcolati e segnati con *.
- Regno Unito: spiegato che prima del 1988 si usa il RPI per tutte e due le date (niente concatenazione) e che il risultato è più alto di quello
  della Banca d'Inghilterra (che usa stime CPI modellate): esempio della sua pagina, 23 £ 1975 → 1985 = 57,68 £ contro 63,68 £ qui. Fonte `boe_calc`
  in `fonti.json` con le frasi ricontrollate a ogni scarico. La nota sul RPI resta visibile e il calcolatore torna al CPI quando le date tornano dal 1988.
- Germania: fattore 0,69551 rifatto (61,9 ÷ 89,0, medie annue 1991): corretto e standard, ma è un calcolo nostro; ora è scritto («eigene Berechnung»,
  «kein amtlicher Index», precisione di una cifra decimale, salto di circa 0,4 % tra dicembre 1990 e gennaio 1991) anche accanto al risultato.
  Tedesco sistemato («in Preisen von …», «Abgerufen am», «Zieljahr», domanda della FAQ), citazione Destatis con il testo dell'Impressum.
- USA: «December 2025 to December 2025» → 2024-2025; «+0.0%» → «0.0%»; pagine anno con la precisione dell'indice a una cifra (±0,5 % nel 1913),
  gli anni con la stessa media annua, valore di 100 $ per ogni mese, mese più basso e più alto.
- `verifica.py`: fattore tedesco rifatto e applicato a ogni valore, 10 casi BLS, tassi stampati = tassi pubblicati, attribuzioni OGL/Destatis/BLS e
  avviso in ogni pagina, titoli ≤ 65, titoli e descrizioni unici, 113 pagine anno con valore e 12 mesi = BLS e mai gli stessi numeri, nota BoE;
  nel browser: passaggio CPI→RPI e ritorno, ottobre 2025 non selezionabile.

Resta al titolare: Impressum per le pagine tedesche (§ 5 DDG: un sito con pubblicità rivolto al pubblico tedesco è «geschäftsmäßig»; senza
Impressum il rischio concreto è una diffida a pagamento da concorrenti o associazioni). Alternativa senza Impressum: non pubblicare `/de/`.

## Sezione limiti 401(k)/IRA/Roth/SIMPLE/HSA (13/11/2026, NON ancora committata: revisione indipendente prima del commit del 14/11)

Dalla riga "inflation" di `DA-PUBBLICARE.md` (famiglia #3 di `fronti-2026-11-13-scoperta-volumi.md`). **6 pagine nuove** (147 indicizzabili + 404):
`/retirement-limits/` (2026 e 2027 a colpo d'occhio, storia 2015-2027, limiti 2015 in dollari 2025 con il CPI-U e link al calcolatore),
`/401k-limit/` (401(k)/403(b)/457(b)/TSP, catch-up 50+ e 60-63, 415(c)), `/ira-limit/` (limite IRA e fasce di deducibilità),
`/roth-ira-income-limit/` (fasce Roth + **calcolatore**), `/hsa-limit/` (HSA e HDHP), `/simple-ira-limit/`. Codice in `pensione.py` (chiamato da
`genera.py`), JS del calcolatore in `stile.ROTH_JS` (file `assets/roth.*.js`, solo in quella pagina). Menu USA: "401(k) & IRA limits"; card in home.

**Domanda** (138 ricerche seodata in `dati/domanda.json`, gruppo `limiti_pensione`): i volumi sono ancora sulle frasi "2025" (401k contribution
limits 2025 135.000, roth ira income limits 90.500, hsa contribution limits 2025 60.500, ira contribution limit 2025 40.500, simple ira 2025 12.100,
max ira contribution 18.100, 403b 5.400, 401k catch up 4.400, super catch up 1.300, roth ira contribution calculator 1.300); le frasi "2026/2027" hanno
ancora volumi bassi o 0. Niente pagine per SEP (3.600) e 529; 403(b), 457(b) e TSP stanno nella pagina 401(k) (stesso limite). 15 FAQ nuove, tutte da frasi misurate.

**Dati, solo IRS** (`raccolta/irs.py` → `dati/grezzi/irs/<id>.txt` + PDF piccoli, `fonti.json` con URL, data, HTTP, SHA-256): 13 comunicati (IR-2014-99 …
IR-2026-136 del 12/11/2026, il 2027 c'è), 13 Notice (2015 dall'IRB 2014-48: `n-14-70.pdf` dà 404), 14 Rev. Proc. HSA (2020 dall'IRB 2019-22:
`rp-19-25.pdf` 404; 2018 famiglia da Rev. Proc. 2018-27, 6.900 $), Publication 969 2015-2025, Publication 590-A (2025), tabelle COLA dell'IRS.
`dati/limiti.json`: 244 voci / 361 cifre, ognuna con fonte e **frase IRS citata** (scelte con un estrattore e riviste a mano; per il 2015 frasi del
comunicato perché l'IRB ha le intestazioni di pagina dentro le frasi). Contributo HSA 55+ per 2026 e 2027: dalla legge (vedi "Revisione indipendente
della sezione limiti" qui sotto), non più celle vuote. Limiti SIMPLE "alti" (SECURE 2.0) solo dal 2025, come nei Notice.

**Calcolatore Roth**: Publication 590-A, Worksheet 2-2, in centesimi interi; rapporto esatto (il foglio dice "rounded to at least three places":
cambia al massimo 10 $ ai bordi), per eccesso ai 10 $, minimo 200 $ se sopra zero, poi il minore tra riga 8 e riga 10 (compenso e versamenti ad
altri IRA facoltativi). 4 stati (MFS che ha vissuto separato = fascia single, come dice la Pub 590-A). Esempio del foglio IRS: 2025, single, MAGI
151.000 → 6.540 $ (attenzione: il testo dell'esempio IRS dice MAGI 150.000 e 6.530 $, ma le righe del foglio danno 151.000 e 6.540; usiamo le righe).

**Controlli nuovi in `verifica.py`** (`pensione()`, `roth_motore()`): ogni frase ritrovata nel testo della fonte, ogni cifra dentro la sua frase, fonte
dell'anno giusto (52 documenti con il loro numero/anno), 198 cifre ritrovate anche nel comunicato dell'anno, 15 serie uguali alle tabelle COLA dell'IRS,
ampiezze delle fasce e crescita; 440 celle delle pagine = `limiti.json`; citazioni nelle pagine = frasi registrate; limiti 2015 in dollari 2025 = CPI-U;
JS Roth = Python su 5.096 casi (bordi al centesimo, minimo 200 $, compenso basso); 7 casi Roth nel browser × 2 larghezze; 4 pagine nuove in Playwright.
Prova al contrario fatta: una cifra cambiata in `limiti.json`, una fonte di un altro anno e una cella cambiata nella pagina danno 8 errori.
`SEGNO_CHIAVE` ora è `"_".join(...)`: la vecchia somma di stringhe finiva intera nel `.pyc` e faceva scattare il controllo `grep` sul prefisso della chiave.

**Aggiornamento annuale**: a novembre (comunicato + Notice dell'anno dopo) e a maggio-giugno (Rev. Proc. HSA): aggiungere i nuovi URL in
`raccolta/irs.py`, `python3 -I inflation/raccolta/irs.py`, aggiungere l'anno in `dati/limiti.json` con le frasi (le pagine si rifanno da sole),
poi `genera.py` e `verifica.py --browser`. Quando esce la Publication 969 (2026) si può passare `hsa_catchup` 2026 dalla legge alla pubblicazione
(non è obbligatorio: la cifra è fissata dalla legge). Ogni novembre aggiungere anche `roth_catchup_soglia` del nuovo anno (è nel Notice).

### Revisione indipendente della sezione limiti (13/11/2026, prima del commit)

Fonti IRS riscaricate da zero in una cartella a parte (13 Notice, 14 Rev. Proc., comunicati 2026 e 2027, Publication 590-A e 969) e cifre estratte con
un programma scritto per la revisione: **224 cifre confrontate, 0 diverse** (204 lette in automatico, 20 a mano dove il PDF spezza la frase).
IR-2026-136 del 12/11/2026 esiste e dà le cifre 2027 pubblicate (25.500, 8.500, 11.750, IRA 7.500/1.100, Roth 158-173 e 250-260 mila, SIMPLE 17.500/19.100,
415(c) 75.000; HSA 2027 4.500/9.000 dalla Rev. Proc. 2026-24). Calcolatore Roth: 38 casi fatti a mano dal Worksheet 2-2 contro il JS pubblicato, 0 diversi.

Corretto:
- **HSA 55+ 2026 e 2027 = 1.000 $**, fonte la legge: 26 U.S.C. § 223(b)(3)(B) («2009 and thereafter $1,000»), non indicizzato perché § 223(g) indicizza
  solo (b)(2) e (c)(2)(A). Testo letto su govinfo.gov (U.S. Code ed. 2024, fonte `usc_223`, unica non irs.gov: `verifica.LEGGE_USA` la ammette solo per
  `hsa_catchup`). La pagina diceva già "From age 55 the limit is $1,000 higher" con le celle vuote: ora cella, testo e FAQ dicono la stessa cosa con la fonte.
- **Pagina 401(k)**: le tre spiegazioni non citate ora sono frasi IRS (`testi.k401_*`, fonti `irs_401k_limiti`, `irs_piu_piani`, `irs_catchup`):
  somma dei differimenti tra piani e 457(b) a parte, catch-up «If permitted by the 401(k) plan», 415(c) «elective deferrals (but not catch-up
  contributions)». Tolto "to one person's account" / "all contributions to one account": l'IRS dice «all of your accounts in plans maintained by one employer».
- **Soglia salariale del catch-up Roth** (150.000 $ per il 2026, 155.000 $ per il 2027): era scritta a mano nel codice; ora è una voce d'anno
  (`roth_catchup_soglia`) con la frase del Notice, e il testo dice che il salario è quello dell'anno prima presso il datore che ha il piano (frase IRS).
- **HDHP dal 2026**: la pagina diceva che serve un piano con quelle franchigie; dal 2026 i piani bronze e catastrophic dell'Exchange valgono come HDHP
  anche senza (Notice 2026-5, citato).
- **Citazioni con il numero di pagina del PDF dentro** («a high -2deductible health plan», «other 3 amounts»: 6 frasi delle Rev. Proc.): `frase` resta
  quella del testo estratto, `mostra` è quella stampata, e `verifica.py` controlla che differiscano solo per quel numero.
- Calcolatore Roth: con versamenti ad altri IRA il titolo diceva "you can contribute the full amount" e la riga sotto "before contributions you already
  made to other IRAs" anche quando la cifra era già al netto; ora due testi distinti (`full_meno`, `sotto_altre`). Il motore non è cambiato.
- Testi: SIMPLE 401(k) ("same amounts" valeva solo per limite generale e catch-up), "in fixed steps (for example $500)" tolto, "by $10 near the edges"
  corretto, fascia 0-10.000 $ dei coniugi separati citata, etichetta "Figures quoted from IRS documents", nome della pagina IRS nelle citazioni.
- `raccolta/irs.py`: 5 fonti nuove; le voci di elenco delle pagine HTML diventano «• » come nei PDF.

Controlli aggiunti in `verifica.py`: fonte di legge solo per le voci ammesse, HSA 55+ = 1.000 $ in ogni anno e § 223(g) senza (b)(3), soglia Roth
coerente tra un anno e l'altro e con la pagina IRS, frasi `mostra`, le 6 frasi IRS della pagina 401(k) presenti e le vecchie formule assenti, nessuna
cella vuota nella pagina HSA. Prova al contrario: 3 dati alterati → 6 errori.
