# US Paycheck Calculator (paycheck) – note di lavoro

Costruito il 14/11/2026 come **prova su 5 Stati** dell'idea 76 di `studio-business/intelaiatura/fronti-2026-11-14-notte-grandi.md` (riga «nuovo (USA)» di
`studio-business/DA-PUBBLICARE.md`). Sito statico in inglese (USA) generato da `genera.py` in `sito/`: busta paga netta e imposte del datore di lavoro, anno 2026.
Indirizzo previsto: **`https://us-paycheck-calculator.netlify.app`** (nome libero il 14/11: risposta 404; costante `URL_SITO` in `genera.py` e in `verifica.py`).
**Il sito Netlify non esiste ancora. NON è stato fatto alcun commit: prima la revisione indipendente.** Pubblicità: AdSense acceso (`monetizzazione.json`), contatore GoatCounter.

## Stati scelti e perché (domanda misurata, `dati/domanda.json`, 97 ricerche seodata del 14/11)

| Stato | «<Stato> paycheck calculator» al mese | Perché |
|---|---|---|
| Texas | 60.500 | nessuna imposta statale sul salario; fonte TWC leggibile |
| California | 60.500 | EDD leggibile: Method B (PDF), SDI, UI, ETT; in più la riduzione del credito FUTA 2026 |
| Florida | 27.100 | nessuna imposta statale; Florida Department of Revenue leggibile |
| Illinois | 27.100 | aliquota unica 4,95 %, formula «automated payroll method» nel libretto IL-700-T; IDES (EA-50) leggibile; nessuna tassa locale |
| North Carolina | 27.100 | formula «percentage method» nel modulo NC-30; DES leggibile; nessuna tassa locale |

Scartati per questa prova: **Ohio** (22.200; le pagine di tax.ohio.gov e jfs.ohio.gov provate rispondono 404 e quasi tutti i lavoratori pagano tasse comunali e
scolastiche: fuori portata), **Pennsylvania** (18.100; pa.gov è una pagina JavaScript e l'imposta locale EIT vale quasi ovunque), **New York** (40.500; New York City e Yonkers).

## Pagine (11 indicizzabili + 404)

`/` calcolatore (Stato, frequenza, lordo per periodo / stipendio annuo / paga oraria × ore, W-4: stato civile, casella Step 2, Step 3, 4(a), 4(b), 4(c), lordo già
ricevuto nell'anno; moduli statali DE 4, IL-W-4, NC-4) · `/texas/` `/florida/` `/california/` `/illinois/` `/north-carolina/` (calcolatore con lo Stato scelto, tabella di
5 stipendi, formula statale con le frasi ufficiali, **esempio ufficiale ricalcolato**, imposte del datore con calcolatore) · `/employer-payroll-taxes/` (FICA, FUTA,
riduzione del credito, tabella dei 5 Stati, calcolatore del costo) · `/federal-withholding/` (Worksheet 1A, le 6 tabelle annuali, esempio svolto, bozza 2027) ·
`/how-we-check/` (con modulo delle correzioni senza dati personali) · `/about/` · `/privacy/`. FAQ: 34, ognuna da una ricerca misurata.

## Fonti (16 file in `dati/grezzi/`, URL, data e SHA-256 in `dati/fonti.json`; 60 frasi citate alla lettera)

- **Federale**: IRS Pub. 15-T 2026 (Worksheet 1A e tabelle della sezione 1), Pub. 15 2026 (Social Security 6,2 % fino a 184.500 $, Medicare 1,45 %, 0,9 % oltre
  200.000 $, FUTA 6,0 % sui primi 7.000 $, credito 5,4 %), modulo W-4 2026, bozza della Pub. 15-T 2027 (solo per dire che è una bozza: **non usata**).
- **FUTA, riduzione del credito 2026**: foglio finale del Department of Labor (aggiornato il 10/11/2026): California 1,5 % → FUTA 2,1 % (147 $ invece di 42 $).
- **Texas** TWC: base 9.000 $, aliquota d'ingresso 2,70 %, minimo 0,32 % e massimo 6,32 %. **Florida** DOR: 2,7 % sui primi 7.000 $.
- **California** EDD: Method B 2026 (tabelle 1-4 e 17-28: settimanale, bisettimanale, due volte al mese, mensile), SDI 1,3 % su tutto il salario (1,4 % nel 2027, già
  pubblicato), UI 3,4 % ai nuovi su 7.000 $, ETT 0,1 %.
- **Illinois**: IL-700-T (4,95 %, 2.925 $ e 1.000 $ per esenzione), IDES EA-50 (3,350 % d'ingresso, compreso lo 0,550 % «Fund Building», su 14.250 $).
- **North Carolina**: NC-30 (ritenuta 4,09 % = 3,99 % + 0,1 %, arrotondata al dollaro), DES (1 % ai nuovi su 34.200 $).
- **Patriot Software**: pagina del programma affiliati («You receive $150 per new customer», iscrizione con Impact).
- Blocchi non aggirati: **ssa.gov risponde 403** (il tetto contributivo viene dalla Pub. 15; il tetto 2027 non è mostrato). Le pagine HTML di Florida, North Carolina DES
  e Patriot cambiano byte a ogni scarico (parti dinamiche): per tutte le pagine HTML fa fede l'impronta delle frasi citate (`sha256_frasi`).

## Revisione indipendente del 14/11/2026 (che cosa è cambiato)

- **Impronte**: i PDF e il foglio DOL restano legati allo SHA-256 del file; per le 7 pagine HTML (`"impronta": "frasi"` in `fonti.json`) fa fede `sha256_frasi`,
  l'impronta delle frasi citate ritrovate nel file: `genera.py` e `verifica.py` non si fermano più se i byte della pagina cambiano e le frasi ci sono ancora.
  `fonti.py` ora è «tutto o niente»: scarica in file `.tmp` e sostituisce `dati/grezzi` solo se tutte le fonti rispondono, tutte le frasi ci sono e le regole si
  leggono (altrimenti i file nuovi finiscono in `cache/fonti_non_lette/` e `dati/grezzi` resta uguale a `fonti.json`). A fine giro dice quali file sono cambiati.
- **Federale**: le righe 2h e 3b del Worksheet 1A sono arrotondate al centesimo una per una, come nel foglio (prima si arrotondava solo alla fine): l'esempio
  svolto ora torna anche a mano (178,33 − 166,67 = 11,66). Differenza massima rispetto a prima: 1 centesimo, solo con lo Step 3 compilato.
- **Texas**: aggiunte due frasi TWC («a flat tax paid by all employers», RTR 0,21 %) e un paragrafo che mostra le due letture (2,70 % oppure 3,02 % = 243 $ o
  271,80 $ per dipendente). Il calcolatore parte da 2,70 %, l'unica aliquota per i nuovi che TWC scrive; nota anche nella tabella dei 5 Stati. La legge
  (statutes.capitol.texas.gov) è una pagina JavaScript non leggibile: questione **non risolta**, detta in pagina.
- **California, colonna «Married 0-1 / 2+»**: lettura confermata come ragionevole (il documento dice che l'imposta si calcola «based on the total number of regular
  withholding allowances claimed on line 1 of DE 4», e l'esempio B usa la colonna 2+ con 2 regolari + 1 stimata), ma resta un'interpretazione ed è detta in pagina.
- Aspetto: didascalie delle tabelle che su telefono uscivano dallo schermo, etichette più corte nel menu della frequenza; voce «extra state withholding» tra le cose non coperte.
- Controllo del revisore: 652 celle e aliquote rilette da scarichi propri (0 differenze), 60 frasi su 60, 40 buste paga e 10 casi del datore rifatti con un
  calcolo scritto da zero contro il JS pubblicato (0 differenze).

## Come sono fatti i conti

`app.js` (nel browser) e `motore.py` (testi delle pagine) lavorano in **centesimi interi**; aliquote in millesimi di punto. Federale: Worksheet 1A (lordo × periodi,
+ 4(a) − 4(b) − 8.600/12.900 $ oppure 0 con la casella Step 2, tabella annuale, ÷ periodi (riga 2h, al centesimo), − Step 3 ÷ periodi (riga 3b, al centesimo), + 4(c)); l'IRS permette
anche il dollaro intero: detto in pagina. California: Method B con le tabelle del periodo. Illinois: esenzioni ÷ periodi arrotondate al centesimo, poi 4,95 %.
North Carolina: 4,09 % arrotondato al dollaro. `dati/regole.json` è scritto da `raccolta/fonti.py` leggendo i file grezzi (mai a mano).

## Controlli (`verifica.py`, 0 errori il 14/11)

Indipendenti dai dati del costruttore: tabelle federali, aliquote, soglie e tabelle 1-4 della California **trascritte a mano** in `verifica.py`; le 12 tabelle di
scaglioni della California rilette con un'altra estrazione (`pdftotext -raw`); busta paga di riferimento con frazioni esatte. JS pubblicato = riferimento su
**3.041 buste paga** (600 casuali per Stato con casi al limite del tetto Social Security e dei 200.000 $, 10 casi a mano con i conti scritti nel file, 6 esempi
stampati dalle agenzie: California A-D, Illinois, North Carolina, 25 righe delle tabelle) e 1.505 casi del datore. Poi: impronte e 60 frasi alla lettera, ogni citazione in
pagina = frase della fonte, tabelle federali e dei datori cella per cella, titoli ≤ 65 e descrizioni ≤ 160 unici, FAQ visibili = JSON-LD e solo da ricerche misurate,
link interni ed esterni, modulo senza dati personali, riquadro Patriot assente con l'interruttore spento, nessuna chiave. `--browser`: Playwright, 12 pagine a 375 e
1280 px (3 anche in scuro), richieste esterne bloccate, i 10 casi a mano digitati nel calcolatore, stipendio annuo, paga oraria, messaggi d'errore, calcolatore del datore.

## Non coperto o non verificato (detto anche in pagina)

- Deduzioni prima delle imposte (401(k), assicurazione sanitaria), tasse locali, W-4 fino al 2019, bonus, stranieri non residenti, esenti, deduzioni su mance e straordinari.
- California: per la colonna «Married 0-1 / 2+ allowances» contiamo le esenzioni regolari (riga 1 del DE 4): il documento non dice quale riga intende. Tabelle annuali e
  giornaliere non usate (gli esempi E e F dell'EDD non sono riprodotti).
- Texas: le pagine lette non dicono se le componenti fisse (0,32 % in tutto) si sommano all'aliquota d'ingresso del 2,70 % per un datore nuovo (in pagina: le due cifre, 2,70 % e 3,02 %).
- Florida: l'intervallo delle aliquote dopo il periodo iniziale non è nella pagina letta. Illinois: aliquote d'ingresso più alte per alcuni settori (citato solo il settore 56).
- Scadenze e versamenti (moduli 941/940, calendari statali): fuori dalla prova.
- Le ricerche con l'anno («… 2026») risultano a 0 nello strumento: i titoli usano l'anno comunque, come i concorrenti.

## Riquadro Patriot Software (SPENTO)

`dati/affiliati.json`: `"attivo": false`, link segnaposto. Il riquadro (`riquadro_patriot()` in `genera.py`) è previsto sotto il calcolatore del datore nelle 5 pagine
di Stato e in `/employer-payroll-taxes/`; testo e riga di trasparenza sono già scritti e ripetono solo la descrizione che Patriot dà di sé. Per accenderlo:
1. Massimiliano si iscrive al programma Patriot su Impact (pulsante «Apply Now With Impact» in https://www.patriotsoftware.com/affiliates/; proposto dopo le prime 300 visite al mese).
2. Mettere il link tracciato in `"link"` (i domini Impact `sjv.io`, `pxf.io`, `evyy.net` sono già ammessi in `monetizzazione.json`; se il dominio è un altro va aggiunto lì) e `"attivo": true`.
3. `python3 paycheck/genera.py && python3 paycheck/verifica.py --browser`. La privacy e la pagina About prendono da sole il paragrafo sui link di affiliazione.

## Aggiornare alle tabelle 2027 (fine dicembre 2026 – gennaio 2027)

1. Controllare che siano **definitive** (non bozze): IRS Pub. 15-T e Pub. 15 del 2027 agli stessi indirizzi (`irs-pdf/p15t.pdf`, `p15.pdf`; di solito a metà-fine dicembre);
   California `27methb.pdf` (cambiare l'URL in `FONTI`) e la pagina delle aliquote EDD; Illinois IL-700-T (stesso indirizzo «currentyear») e `EA-50_2027.pdf`;
   North Carolina NC-30 2027 (stesso indirizzo) e la pagina DES; Texas (le due pagine TWC passano al 2027 a dicembre); Florida.
   Il foglio FUTA del Department of Labor esce verso il 10 novembre di ogni anno (`final_credit_states_2027.xlsx`).
2. In `raccolta/fonti.py`: `ANNO = 2027`, gli URL con l'anno, le frasi citate che contengono l'anno o una cifra (lo script dice quali non trova più), le espressioni
   regolari in `regole()` con «2026», gli importi della riga 1g se cambiano, il controllo sulla riduzione del credito FUTA. Togliere la fonte `irs_p15t_2027` (bozza).
3. `python3 paycheck/raccolta/fonti.py` → deve finire senza errori. In `verifica.py` **ritrascrivere a mano** dalle fonti nuove: `ATTESO_FED`, `ATTESO_1G`, FICA, FUTA,
   `SUTA`, tabelle NC e California 1-4, e rifare i 10 casi a mano e gli esempi ufficiali (cambiano con le tabelle). In `genera.py` rileggere i testi con cifre scritte
   (descrizioni delle pagine di Stato, esempio B della California, esempi di Illinois e North Carolina: `genera.py` si ferma se un esempio ufficiale non torna).
4. `python3 paycheck/genera.py && python3 paycheck/verifica.py --browser` → 0 errori, poi revisione indipendente e pubblicazione.
5. Volumi nuovi: curl verso seodata (mai la chiave in un file), risposte in una cartella, poi `python3 paycheck/raccolta/domanda.py <cartella>`.

## Pubblicare (passi del titolare, dopo la revisione)

1. Netlify: nuovo sito dal repository, Base directory `paycheck/sito`, Build command vuoto, Publish directory `.`, nome `us-paycheck-calculator`.
2. Search Console: proprietà `https://us-paycheck-calculator.netlify.app/` (meta di verifica già nelle pagine), inviare la sitemap.
3. Togliere l'host da `NON_ONLINE` in `studio-business/strumenti/indexnow.py` e lanciare l'invio. Moduli Netlify: attivare il rilevamento dei moduli e la notifica email.
4. Se in 60 giorni le pagine del datore prendono impressioni: allargare agli altri Stati (uno per fonte leggibile) e proporre l'iscrizione a Impact.
