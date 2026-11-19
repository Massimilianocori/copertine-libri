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

## Sezione prezzi del gasolio da riscaldamento e del propano per Stato (13/11/2026 sera, NON committata: revisione indipendente, pubblicazione 15/11)

Dall'idea 1 di `studio-business/intelaiatura/fronti-2026-11-13-sera-riscaldamento-additivi.md`. **43 pagine nuove** (190 indicizzabili + 404):
`/heating-oil-prices/` e `/propane-prices/` (indici: Stati Uniti, tutti gli Stati rilevati, regioni PADD, inverno in corso e scorso, storia dal 1990-91,
medie per inverno in dollari di oggi con il CPI-U, calcolatore del pieno, 4 FAQ ciascuno) + **13 pagine Stato per il gasolio** (CT, DE, ME, MD, MA, MI,
NH, NJ, NY, OH, PA, RI, VT) e **28 per il propano** (AR, CO, CT, FL, IL, IN, IA, KS, KY, ME, MD, MA, MI, MN, MO, NE, NH, NJ, NY, NC, OH, OK, PA, RI, TX,
VT, VA, WI). Codice in `riscaldamento.py` (chiamato da `genera.py`), JS del calcolatore in `stile.TANK_JS` (file `assets/tank.*.js`, solo in queste
pagine). Menu USA: «Heating oil», «Propane»; piè di pagina, card in home, sezione in How we check, riga in About; sitemap (lastmod = giorno della lettura EIA).
`SEZIONE_DE` resta `False`; gli indirizzi usano il nome intero dello Stato (`/heating-oil-prices/delaware/`), quindi niente «/de/» nel sito.

**Dati, solo EIA** (`raccolta/eia.py` → `dati/grezzi/eia/`, 7 file con URL, data, HTTP, SHA-256 e byte in `fonti.json`; dominio pubblico, pagina
«Copyrights and reuse» letta): i due XLS «Weekly Heating Oil and Propane Prices» (prezzo residenziale, **dollari per gallone, tasse escluse**, un prezzo
per lunedì da ottobre a marzo): gasolio 29 serie × 802 settimane (1/10/1990 → 9/11/2026), propano 46 serie × 805; Stati con prezzo corrente **21 per il
gasolio** (l'Illinois finisce nel 1991 e il Distretto di Columbia nel 2019: per questo 21 e non 22) e **38 per il propano**; le due tabelle HTML (ultime
6 settimane), la pagina «Heating Oil and Propane Update» (variazioni su settimana e anno), le definizioni, la pagina sul riuso. Lo script scrive
`dati/eia_prezzi.json` (quello che legge il generatore) **solo se** i controlli passano: foglio e unità attesi, date tutte di lunedì e crescenti, valori a
tre decimali tra 0,3 e 15 $, storia mai più corta, nessun valore vecchio cambiato tranne le ultime due settimane (l'EIA dichiara le revisioni della
settimana precedente), tabella HTML = XLS, frasi delle definizioni ancora presenti; altrimenti esce con errore e non tocca nessun file. Serve `xlrd`.
Fino all'inverno 1999-2000 la rilevazione era quasi sempre ogni due settimane (12 prezzi per inverno; settimanale dal 2000-01): le pagine lo dicono e mostrano il numero di settimane di ogni inverno.

**Regole dei conti** (in millesimi di dollaro interi, dichiarate nelle pagine): «un anno prima» = 52 settimane prima (364 giorni; se manca, 371 o 357):
è la stessa regola dell'EIA, controllata su 73 aree della pagina Update. Media di un inverno = media semplice dei prezzi settimanali pubblicati da
ottobre a marzo, **calcolo nostro** (scritto in ogni pagina: l'EIA non la pubblica). Inverno in corso contro lo scorso = media delle settimane che hanno
anche il prezzo di 52 settimane prima. Dollari di oggi = media dell'inverno × CPI-U dell'ultimo mese ÷ CPI-U di gennaio di quell'inverno, con la
spiegazione che il CPI-U misura tutti i prezzi al consumo e non il gasolio (non è un prezzo «reale» ufficiale); il link apre l'esempio nel calcolatore
dell'inflazione (`/?a=…&f=AAAA-1`). Costo del pieno = galloni × ultimo prezzo medio dello Stato, al centesimo (mezzo centesimo per eccesso), con lo
stesso pieno al prezzo di un anno prima; il testo dice di inserire i galloni del preventivo, non la capienza della cisterna (nessuna regola
sull'80 % o sulle cisterne da 275 galloni: non sono in una fonte scaricata).

**Domanda** (127 ricerche seodata country=us, gruppo `riscaldamento` in `dati/domanda.json`): heating oil prices 27.100, propane price per gallon 14.800,
propane prices 12.100, how much is propane per gallon 5.400, current propane prices 2.900, heating oil prices today 2.400; per Stato: gasolio CT 6.600,
MA 2.900, ME 2.400, RI 1.900, NY 1.600, NJ 1.300, NH e PA 1.000, DE e MD 390, VT 320, OH 170, MI 110; propano ME 1.900, CT 1.300, NH e MI 1.000, MA e WI
880, MN 720, OH 590, PA 480 … FL 110. **Regola delle pagine Stato** (`riscaldamento.domanda()`): la frase più cercata tra quelle misurate (con le
«simili») che nomina il combustibile, «price» o «cost» e un solo Stato (per nome, o per sigla postale a inizio o fine frase; le sigle che sono anche
parole, come «in» o «me», solo dopo «prices») deve avere ≥ 100 ricerche al mese. Sotto soglia, solo nella tabella dell'indice: gasolio VA 90, NC 50,
WI 50, IN/IA/KY/MN/NE 0; propano DE, GA, ND, UT 90, ID 70, SD, TN, MS, MT 50, AL 40. FAQ solo nei due indici, 8 in tutto, ognuna da una frase misurata.

**Controlli nuovi in `verifica.py`** (`riscaldamento()`, `tank_motore()`; lettura dell'XLS scritta a parte, non usa `raccolta/eia.py`): 7 file grezzi =
`fonti.json`; 50.319 valori di `eia_prezzi.json` = XLS; 438 valori delle tabelle HTML = XLS; ultimo prezzo e variazioni di 73 aree = pagina Update;
**ogni prezzo stampato ha un attributo `data-*` con serie, area e settimana** e viene rifatto dall'XLS: 5.670 prezzi settimanali, 417 differenze, 460
variazioni %, 1.654 medie, 74 importi CPI, 47 costi del pieno, più 4.206 date accanto ai prezzi; nessun importo in dollari fuori dalle celle etichettate;
titolo (≤ 65), descrizione (≤ 160) e apertura = ultima settimana; dati dei calcolatori = XLS; JS del pieno = Python su 4.110 casi; pagine Stato = Stati
con frase misurata ≥ 100; fonte, «excluding taxes», «not a price quote», «our own calculation», data dell'uscita EIA, niente frasi da consiglio
(«buy now», «lock in», «cheapest»…). Nel browser: 4 pagine nuove × 375/1280 × chiaro/scuro e 7 casi del pieno × 2 larghezze (pulsanti, altro Stato,
decimali, valori non validi). Se uno Stato non ha il prezzo dell'ultima settimana (l'EIA scrive NA) è un avviso, non un errore: la pagina mostra la
data del suo ultimo prezzo.

**Aggiornamento settimanale (da ottobre a marzo)**. L'EIA pubblica di norma il mercoledì (la data della prossima uscita è in `dati/eia_prezzi.json`,
campo `prossima_uscita`, e in ogni pagina; con le feste slitta di un giorno o due):
1. `python3 -I inflation/raccolta/eia.py` (se l'EIA non ha ancora pubblicato, l'ultima settimana resta la stessa e non cambia niente; se un controllo
   fallisce lo script non tocca i file: leggere l'errore, di solito una colonna nuova o una frase delle definizioni cambiata; se l'EIA ha rivisto
   settimane più vecchie delle ultime due, controllare le note della tabella EIA e rilanciare con `--accetta-revisioni`).
2. `python3 inflation/genera.py && python3 inflation/verifica.py --browser` → 0 errori; `python3 studio-business/strumenti/monetizzazione.py verifica inflation`.
3. Un commit, una pubblicazione, poi IndexNow per le 43 pagine (i titoli contengono prezzo e data: cambiano ogni settimana).
Da aprile a settembre l'EIA non pubblica prezzi settimanali: le pagine dicono da sole che l'ultima rilevazione è quella di fine marzo e che si
riparte a ottobre (`riscaldamento.IN_STAGIONE`); nessun lavoro fino alla prima uscita di ottobre. A ottobre l'inverno nuovo parte da solo.
Ogni tanto (a inizio stagione) rimisurare la domanda per gli Stati sotto soglia: aggiungere le frasi a `dati/domanda.json` (gruppo `riscaldamento`) e
le pagine nascono o spariscono da sole; `verifica.py` controlla che ogni pagina abbia la sua frase.

### Revisione indipendente della sezione gasolio/propano (14/11/2026, NON committata)

File EIA riscaricati a parte (stessi SHA-256 dei grezzi) e riletti con un lettore scritto da zero: **11.034 valori stampati nelle 43 pagine rifatti
dall'XLS, 0 diversi** (titolo, descrizione, apertura, variazioni su settimana e anno, medie d'inverno, tabelle storiche, tabelle per Stato e PADD, 72
importi CPI rifatti con `bls_cpiu.csv`, costo del pieno) e 219 valori contro la pagina «Heating Oil and Propane Update» dell'EIA, 0 diversi. 21 Stati
per il gasolio e 38 per il propano confermati; uscita 12/11 e prossima 18/11 confermate sulle tabelle EIA.

Corretto:
- **Fine stagione**: `IN_STAGIONE` dipendeva solo dalla data di lettura, che non avanza se nessuno rilancia `raccolta/eia.py`: da aprile a ottobre le
  pagine avrebbero continuato a dire «so far» e «the next release is scheduled for…». Ora l'inverno è in corso solo se anche il lunedì dopo l'ultimo
  prezzo cade tra ottobre e marzo (dopo l'ultimo lunedì di marzo le pagine passano da sole al testo di fuori stagione).
- **Prezzi mensili fuori stagione**: l'XLS contiene anche prezzi di aprile-settembre (secondo lunedì del mese, 2024 e 2025; frase EIA ora tra quelle
  controllate, `fuori_stagione`). Le pagine dicevano «only from October through March» e, con un prezzo mensile come ultimo dato, «weekly survey»: ora
  lo dicono (nota sui dati, apertura, FAQ) e precisano che quei prezzi non entrano nelle medie d'inverno.
- **Illinois e District of Columbia** (gasolio): l'indice ora nomina le due serie finite con la data dell'ultimo prezzo (18/3/1991 e 7/10/2019) e dice
  che non sono tra i 21 Stati; `verifica.py` rifà le date dall'XLS.
- **FAQ del propano** «cost to fill 500 gallon propane tank»: la risposta dava 300 e 400 galloni; ora dà 300 e 500 e dice che la capienza non è la
  quantità consegnata (nessuna regola dell'80 %: non è in una fonte scaricata).
- **Dati vecchi**: `verifica.py` dà errore se in stagione la «prossima uscita» stampata è passata da più di 7 giorni senza una nuova lettura.
- Tabella delle settimane: una riga dell'inverno scorso senza corrispondente non mostra più una data passata come se fosse futura.
- **Grafica a 375 px**: prima colonna fissa nelle tabelle larghe (`.tab.fissa`), tabella CPI in quattro colonne senza scorrimento (`table.stretta`),
  etichette dell'asse «2020» e «2026» non più sovrapposte nel grafico storico (`_etichette_x`, vale per tutti i grafici a linea).

Resta noto: il titolo porta prezzo e data, quindi non invecchia in silenzio, ma l'aggiornamento settimanale è manuale (passi qui sopra).

## Sezioni «cifre 2027»: UK da aprile 2027 e tetti agli aumenti dell'affitto (18/11/2026, NON committate: serve la revisione indipendente)

Dall'idea G di `studio-business/intelaiatura/fronti-2026-11-14-sera-regole-2027.md` e dall'idea A-piccola di `fronti-2026-11-18-affitti.md`.
**13 pagine nuove** (203 indicizzabili + 404), costruite sopra le sezioni limiti e gasolio/propano (non toccate, a parte menu, piè di pagina e CSS comune).

### A. `/uk/…-2027/` (5 pagine, codice in `uk2027.py`, dati in `dati/uk_2027.json`)

`/uk/rates-april-2027/` (indice), `/uk/minimum-wage-2027/` (4 fasce d'età, calcolatore della paga, paga a 16-40 ore, storia dal 2024),
`/uk/state-pension-2027/` (nuova e di base, Pension Credit, ×4 e ×52), `/uk/benefit-rates-2027/` (Universal Credit, PIP, Attendance Allowance, DLA,
Carer's, JSA, Bereavement Support), `/uk/statutory-sick-pay-2027/` (SSP, maternità, paternità, adozione, Maternity Allowance). Menu UK: «April 2027 rates».

**Cifre confermate sulla fonte** (50, in pence, ognuna con la riga di tabella citata): paga minima dal 1/4/2027 13,21 £ (21+), 11,27 (18-20), 8,31 (sotto i 18 e
apprendisti), da 12,71 / 10,85 / 8,00, +3,9 % (pagina GOV.UK dei tassi = tabella dell'annuncio Low Pay Commission del 28/10/2026; accommodation offset 11,53 £);
pensione nuova piena 241,30 → 250,70 £ a settimana, di base 184,90 → 192,10; SSP 123,25 → 127,55; SMP/SPP/SAP 194,32 → 201,11; Universal Credit single 25+
424,90 → 443,21 al mese (under 25 338,58 → 353,87); PIP 114,60 → 118,60 e 80,00 → 82,80; Attendance Allowance 76,70/114,60 → 79,40/118,60; Carer's 86,45 → 89,50.
Le cifre DWP vengono dal documento «Proposed benefit and pension rates 2027 to 2028» dell'11/11/2026: **le pagine dicono «proposed»** finché non esce l'ordine.
Le cifre in vigore scritte nelle guide GOV.UK (241,30; 338,58; 123,25) devono essere uguali alla colonna 2026-27 (controllo).
**Lasciato fuori**: Employment and Support Allowance (le tabelle del documento non distinguono bene contributiva e legata al reddito), Housing Benefit, Income
Support, deduzioni, benefit cap; Child Benefit e sussidi scozzesi (non sono nel documento DWP: la pagina indice lo scrive); il giorno d'inizio di ogni sussidio (il
documento dà solo l'anno «2027 to 2028»). Non letta: la dichiarazione ministeriale del 28/10 su questions-statements.parliament.uk (403, in `_non_lette`).
Ogni pagina ha il confronto con l'ultimo tasso CPI a 12 mesi dell'ONS (serie già caricata dal sito) e quindi l'attribuzione OGL dell'ONS oltre a quella di GOV.UK.

### B. `/rent-increase-cap/` (8 pagine, codice in `affitti.py`, dati in `dati/affitti.json`)

Indice con calcolatore «maximum new rent» + California, New York City, Washington, Oregon, Ontario, British Columbia, Saint Paul. Menu USA: «Rent caps».
Tetti in millesimi di punto, ognuno con il periodo e la frase ufficiale:

| Luogo | Cifre lette | Fonte |
|---|---|---|
| California (AB 1482), aumenti dal 1/8/2026 al 31/7/2027 | Los Angeles 8,7 % · Riverside 8,1 % · San Diego 8,2 % · San Francisco 8,8 % · altre contee 8,6 % (periodo prima: 8 / 7,5 / 8,8 / 6,3 / 7,7) | tabella dell'Attorney General, oag.ca.gov/rentcaps |
| Oregon | 2027: 10 % · 2026: 9,5 % | DAS, pagina + file Excel del 30/9/2026 |
| Washington (HB 1217) | 2027: **10 %** (7 % + 4,53 % = 11,53 % → tetto) · 2026: 9,683 % | Commerce, pagina inglese `hb1217-landlord-resource-center` |
| New York City, affitti stabilizzati | Ordine n. 58 (25/6/2026), contratti dal 1/10/2026 al 30/9/2027: **0 % e 0 %**; Ordine n. 57: 3 % e 4,5 % | Rent Guidelines Board |
| Ontario | 2027: 1,9 % · 2026: 2,1 % (+ storia 2018-2027) | ontario.ca |
| British Columbia | 2027: 2,2 % · 2026: 2,3 % | gov.bc.ca |
| Saint Paul | 3 % in 12 mesi (eccezioni 3-8 %, CPI + 8 %) | stpaul.gov |

**Punti aperti del file di ricerca, chiusi**: (1) le cifre californiane per zona sono ufficiali (Attorney General) e **rifatte da noi** dagli indici BLS delle
quattro aree (aprile; marzo per Riverside e San Diego) e dal CPI californiano del DIR: 10 tetti su 10 uguali (variazione arrotondata a un decimale + 5 punti);
regioni e ciclo del 1° agosto confermati sulla stessa pagina; (2) Washington 2027 = 10 %, letto (la copia della ricerca era la pagina spagnola, ferma al 2026);
(3) Ordine 58 letto dal testo. (4) **Los Angeles, San José, San Francisco**: le pagine dei Comuni non danno la cifra al nostro server (PDF non trovato, 403, 404:
in `_non_lette`); le cifre mostrate (3 %, 5 %, 1,6 %) sono quelle della tabella «Local Rent Increase Caps» dell'Attorney General (35 Comuni, copiati con
nome, massimo e periodo) e la pagina lo dice. Il testo di legge (leginfo, 403) non è letto: la regola è citata dall'Attorney General.
**Lasciato fuori**: case mobili di Washington al 5 % (la frase c'è solo nella pagina spagnola), Washington DC, Oakland come pagina, Montgomery County.
Calcolatore: affitto × tetto, **per difetto al centesimo** (la British Columbia scrive che non si arrotonda per eccesso), in centesimi interi.

### Domanda misurata (seodata, 18/11/2026, 209 ricerche in `dati/domanda.json`, gruppi `uk_2027` e `affitti`)

gb (104 frasi, 1.832.690 al mese senza «basic state pension», che lo strumento confonde con «state pension» 1.000.000): minimum wage 2025 301.000 · minimum wage uk
165.000 · state pension increase 2025 90.500 · statutory sick pay 90.500 · national minimum wage 2025 90.500 · pip rates 74.000 · how much is state pension 60.500 ·
statutory maternity pay 60.500 · minimum wage for 18 year olds 40.500 · for 16 year olds 33.100 · dla rates 27.100 · how much is ssp 27.100 · attendance allowance
rates 22.200 · how much is universal credit 18.100 · apprentice minimum wage 14.800. Le frasi con «2027» valgono ancora 0-70.
us (75 frasi, 59.040): rent control 6.600 · how much can a landlord raise rent in california 3.600 · ab 1482 3.600 · los angeles rent control 2.900 · rent guidelines
board 2.400 · how much can a landlord raise rent 1.900 · rent increase calculator 1.600 · nyc rent increase 1.300 · hb 1217 880 · washington state rent control 720 ·
st paul rent control 260 · oregon rent control 210. ca (30 frasi, 26.010): bc rent increase 2.900 · rent control ontario 2.900 · rent increase ontario 1.900.
**Regola delle pagine di luogo** (`affitti.DOMANDA_PAGINA`, soglia 100): ogni pagina ha la sua frase misurata; `verifica_2027.py` lo controlla.
20 FAQ nuove per il Regno Unito e 26 per gli affitti, ognuna da una frase misurata (86 FAQ in tutto nel sito).

### File e controlli

`raccolta/regole2027.py` (25 fonti: 9 GOV.UK, 11 sugli affitti, 5 serie BLS regionali; testo in `dati/grezzi/regole2027/`, originali tenuti per il documento DWP,
la pagina dell'Attorney General e l'Excel dell'Oregon; URL, data, HTTP, SHA-256 in `fonti.json`; se una fonte non risponde 200 o una frase citata non c'è più,
esce senza toccare niente). I due file di dati sono scritti a mano dopo la lettura (frasi comprese) e lo script non li cambia.
`stile.PAY_JS` / `stile.RENT_JS` (file `assets/pay.*.js`, `assets/rent.*.js`, solo nelle pagine che li usano).
`verifica_2027.py` (chiamato da `verifica.py`): 165 frasi ritrovate nei testi; tabelle DWP rilette dall'originale con un lettore a parte (50 cifre); paga minima
GOV.UK = annuncio LPC; 314 cifre e 92 citazioni delle pagine UK rifatte (ogni cella ha `data-uk`); 23 periodi d'affitto con la cifra dentro la frase; 10 tetti
californiani dagli indici; indici della pagina di Washington = BLS; Oregon dall'Excel; 35 tetti locali = originale; 92 cifre e 61 citazioni delle pagine affitti
(`data-rent`, `data-ca`, `data-wa`, `data-on`); dati dei calcolatori = file di dati; JS pubblicato = Python = conto con le frazioni (3.072 e 4.114 casi); solo siti
ufficiali; «proposed», «not legal advice», «not a government website»; niente frasi da consiglio; **errore se l'ultimo periodo di un tetto è scaduto** o se una
fonte è più vecchia di 120 giorni. Prova al contrario fatta (una cifra UK, due tetti e una cella cambiati → 20 errori).
18/11/2026: `python3 inflation/verifica.py --browser` → 0 errori, 0 avvisi (30 pagine × 375/1280 × chiaro/scuro, 6 casi della paga e 8 dell'affitto × 2 larghezze);
`python3 studio-business/strumenti/monetizzazione.py verifica inflation` → 0 errori. Nessuna affiliazione: i riquadri dei programmi per proprietari non sono costruiti.

### Quando aggiornare (le pagine non si aggiornano da sole)

- **Febbraio-marzo 2027**: ordine di rivalutazione DWP → se le cifre restano uguali, togliere «proposed» dai testi (`uk2027.stato_box`, titoli delle descrizioni);
  dal 1/4/2027 GOV.UK cambia la tabella «Current rates» e le guide (la riga citata e il controllo «cifre in vigore» vanno riscritti: è il segnale).
- **Metà maggio 2027**: esce l'indice di aprile → si può rifare il tetto californiano del 1/8/2027 (dichiarandolo calcolo nostro finché l'Attorney General non lo pubblica).
- **Fine giugno 2027** (voto di New York, Ordine 59), **luglio** (Washington 2028), **fine agosto** (British Columbia e Ontario 2028), **30 settembre** (Oregon 2028).
- Ogni volta: aggiornare URL o frasi in `raccolta/regole2027.py` e nei due JSON, `python3 -I inflation/raccolta/regole2027.py`, poi `genera.py` e `verifica.py --browser`.
- L'ONS ha pubblicato il CPI di ottobre il 18/11/2026: il confronto con l'inflazione nelle pagine UK usa ancora settembre finché non gira l'aggiornamento mensile.

### Revisione indipendente delle sezioni «cifre 2027» (19/11/2026)

Fonti riscaricate da zero (19 pagine ufficiali): 80 frasi UK e 76 frasi sugli affitti ritrovate nel testo nuovo (le 3 restanti differiscono solo per il trattino
«–» che `normalizza` scrive «-»); 46 cifre DWP, 4 fasce della paga minima, tutti i tetti (California 8,7/8,1/8,2/8,8/8,6; Oregon 10; Washington 10; Ordine 58
0 % e 0 % letto nel testo; Ontario 1,9; BC 2,2; Saint Paul 3) uguali alla fonte. Calcolatori: 6 casi paga e 9 casi affitto rifatti a mano, uguali.
Corretto: «proposed» ora anche nelle intestazioni delle tabelle DWP, nei riquadri in alto, nei sottotitoli, nelle descrizioni e in ogni risposta FAQ delle
pagine pensione/sussidi/malattia (`uk2027.PROP_TH`, `PROP_FAQ`); 5 descrizioni portate a ≤ 160 caratteri (verifica.py ne ammette 165); frase sul tetto del
90 % dei guadagni per maternità/paternità (letta su GOV.UK, senza citazione registrata); NYC «leases» al posto di «renewal leases»; riquadro BC «3 full months»;
intestazione «Period» per Saint Paul. Resta noto: in `dati/affitti.json` Larkspur ha la contea «Los Angeles County» (la tabella dell'Attorney General lascia la
cella vuota; Larkspur è nella contea di Marin): la contea non è stampata, non stamparla senza correggerla. Dopo le correzioni: `verifica.py --browser` 0 errori,
monetizzazione 0 errori.
