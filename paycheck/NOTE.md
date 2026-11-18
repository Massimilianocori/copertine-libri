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

## Pagine (17 indicizzabili + 404; le 11 della mattina del 14/11 più le 6 per i datori, vedi sotto)

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
link interni ed esterni, modulo senza dati personali, riquadro dei partner assente se tutti spenti (e, se acceso, solo nelle pagine dei datori, sotto il calcolatore, con rel sponsored nofollow noopener), cifre delle 6 pagine dei datori contro le trascrizioni a mano, nessuna chiave. `--browser`: Playwright, 18 pagine a 375 e
1280 px (6 anche in scuro), richieste esterne bloccate, i 10 casi a mano digitati nel calcolatore, stipendio annuo, paga oraria, messaggi d'errore, calcolatore del datore.

## Non coperto o non verificato (detto anche in pagina)

- Deduzioni prima delle imposte (401(k), assicurazione sanitaria), tasse locali, W-4 fino al 2019, bonus, stranieri non residenti, esenti, deduzioni su mance e straordinari.
- California: per la colonna «Married 0-1 / 2+ allowances» contiamo le esenzioni regolari (riga 1 del DE 4): il documento non dice quale riga intende. Tabelle annuali e
  giornaliere non usate (gli esempi E e F dell'EDD non sono riprodotti).
- Texas: le pagine lette non dicono se le componenti fisse (0,32 % in tutto) si sommano all'aliquota d'ingresso del 2,70 % per un datore nuovo (in pagina: le due cifre, 2,70 % e 3,02 %).
- Florida: l'intervallo delle aliquote dopo il periodo iniziale non è nella pagina letta. Illinois: aliquote d'ingresso più alte per alcuni settori (citato solo il settore 56).
- Scadenze e versamenti: dal 14/11 sera i moduli 941/940 e i rapporti trimestrali statali sono in `/how-to-do-payroll/` e nelle pagine `/<stato>-payroll-taxes/`; restano fuori i calendari della ritenuta statale.
- Le ricerche con l'anno («… 2026») risultano a 0 nello strumento: i titoli usano l'anno comunque, come i concorrenti.

## Riquadro dei partner paghe: Gusto, ADP, Patriot (tutti SPENTI, 14/11/2026 sera)

`dati/affiliati.json` ora ha un elenco `partner` (Gusto, RUN Powered by ADP, Patriot), ognuno con `"attivo": false` e `"link": ""`. **Nessun link di affiliazione esiste
ancora e nessuno è stato inventato**: `verifica.py` dà errore se un partner spento ha un link, o se uno acceso non ha un link https su un dominio ammesso.
Il riquadro (`riquadro_partner()` in `genera.py`) esce solo se almeno un partner è acceso e mostra solo quelli accesi, nell'ordine dell'elenco. Titolo «Running payroll
for employees?», testo neutro («Payroll software works out these taxes on every payday, and full-service plans also make the deposits and file the returns for you…
We have not tested their software… Check what each plan includes»), per ogni partner una riga che ripete solo ciò che scrive di sé nella pagina registrata in
`fonti.json` (nessun prezzo, nessun giudizio: `verifica.py` lo controlla), pulsante con `rel="sponsored nofollow noopener"`, etichetta «Advertisement · affiliate
links» e riga di trasparenza. Posizione: **sempre sotto il calcolatore del datore, mai sopra la risposta**: 5 pagine di Stato (sotto il calcolatore del datore),
`/employer-payroll-taxes/`, le 5 pagine `/<stato>-payroll-taxes/` (dopo tabella, costo e iscrizione) e `/how-to-do-payroll/` (sotto il calcolatore in fondo). Mai in
home, federale, about, privacy. Provato acceso il 14/11 con tre link di prova (poi tolti): 0 errori, 36 link in 12 pagine, schermate 375/1280 chiaro e scuro buone.

### Programmi letti il 14/11/2026 (file in `dati/grezzi/`, frasi in `fonti.json`)

| Partner | Rete | Compenso scritto | Condizioni lette | Editore fuori dagli USA |
|---|---|---|---|---|
| Gusto | PartnerStack (`market.partnerstack.com/page/gusto`, 200) | «Earn $300 for every new customer (who runs payroll) you refer to Gusto.» | Termini `gusto.com/legal/terms/partnerstack-terms`: **non letta (403)**; anche `gusto.com/partners/affiliates`: non letta (403) | **non scritto** nella pagina letta; termini non letti |
| RUN Powered by ADP | PartnerStack (`/page/adp`, 200) + accordo PDF (`contracts.adp.com`, 200, «Last updated: June 9, 2026») | «Earn up to $1,000+ for every new U.S. based RUN Powered by ADP® customer who actively runs payroll!». Accordo: 500 $ (1–4 clienti convertiti), 750 $ (5–9), 1.000 $ (10 o più) | Cliente «convertito» = almeno 3 paghe nei 45 giorni dall'inizio e fattura pagata; pagamento entro 45 giorni dalla fine del mese; consenso scritto di ADP per usare i marchi ADP in pubblicità; il programma lavora con una pagina di segnalazione co-marcata e moduli (lead) | **non scritto**: l'accordo non nomina Paesi; chiede che il partner sia «duly organized, validly existing and in good standing under the laws of its jurisdiction of organization» (formula da società: per una persona fisica va chiesto) |
| Patriot Software | Impact (`patriotsoftware.com/affiliates/`, 200) | «You receive $150 per new customer.» | «Apply Now With Impact»; chiede il pubblico: «Do you have an audience of USA–based business owners?» | **non scritto**: la pagina parla del pubblico (USA), non del Paese dell'editore |

Quindi per un editore italiano persona fisica: **nessuno dei tre lo esclude per iscritto e nessuno lo ammette per iscritto**; si saprà alla domanda. Con 1–4 clienti
ADP paga 500 $, non 1.000 $. `adp.com/affiliates` e `adp.com/partners/affiliate-program` rispondono 404.

### Per accendere un partner

1. Massimiliano crea il conto editore su PartnerStack (Gusto, ADP) e su Impact (Patriot) e chiede i programmi. Per ADP leggere prima nel pannello le regole sull'uso del marchio.
2. In `dati/affiliati.json`: mettere il link tracciato vero in `"link"` e `"attivo": true` solo per quel partner. Se il dominio del link non è in
   `studio-business/strumenti/monetizzazione.json` (`domini_affiliazione`: per Impact `sjv.io`, `pxf.io`, `evyy.net` ci sono già; i link PartnerStack usano un dominio del
   programma, da leggere nel pannello) va aggiunto lì, altrimenti `genera.py` si ferma.
3. `python3 paycheck/genera.py && python3 paycheck/verifica.py --browser && python3 studio-business/strumenti/monetizzazione.py verifica paycheck`. Privacy e About prendono da sole il paragrafo sui link di affiliazione.

## Contenuti per i datori di lavoro aggiunti il 14/11/2026 (sera): 6 pagine, NON ancora pubblicate

- **`/texas-payroll-taxes/`, `/florida-payroll-taxes/`, `/california-payroll-taxes/`, `/illinois-payroll-taxes/`, `/north-carolina-payroll-taxes/`**: calcolatore del datore
  con lo Stato scelto in alto, tabella «chi paga che cosa» (aliquota, chi, su che cosa), costo di un dipendente da 50.000 $ riga per riga, «How to do payroll in <State>:
  register, report, pay» con le frasi delle agenzie alla lettera (TWC: iscrizione entro dieci giorni, rapporto e tassa entro l'ultimo giorno del mese dopo il trimestre,
  tutto in via elettronica; Florida DOR: iscrizione, soglie 1.500 $ / 20 settimane, RT-6; EDD: 15 giorni, 100 $ nel trimestre, nuovi assunti entro 20 giorni, DE 9 e DE 9C;
  IDOR e IDES: MyTax Illinois, soglie; NCDOR NC-BR e frequenza, DES: soglie, numero, rapporto trimestrale), che cosa si trattiene al dipendente (esempio 2.000 $), 4–6 FAQ.
- **`/how-to-do-payroll/`**: 8 passi con le frasi della Pub. 15 (EIN, registro dei nuovi assunti, EFT, lookback 50.000 $, primo anno mensile, 15 del mese dopo,
  semisettimanale, Form 941, FUTA e Form 940), una busta paga svolta (Texas, 2.000 $: da versare all'IRS 462,15 $), tabella delle scadenze, tabella dei 5 Stati, calcolatore del datore.
- Collegamenti: da ogni pagina di Stato, da `/employer-payroll-taxes/` (griglia «Payroll taxes by state»), dalla home («For employers») e dal piè di pagina (colonna «Employers»).
- Fonti nuove (11 pagine ufficiali + 8 frasi in più della Pub. 15, 2 dell'NC-30, 3 di Florida DOR): `tx_ut`, `tx_filing`, `fl_return`, `ca_step1/4/5/6`, `il_ides_tax`,
  `il_idor_reg`, `nc_required`, `nc_quarterly`. Scaricate con curl il 14/11 e registrate con `raccolta/fonti.py --locale` (le altre fonti non sono state riscaricate).
- **Domanda misurata** (seodata, 52 frasi nuove il 14/11, aggiunte a `dati/domanda.json` con `raccolta/domanda.py <cartella> --aggiungi`; 149 in tutto):
  «<stato> payroll tax»: California 2.400 (15,1 $), Texas 1.300 (17,0 $), Florida 1.000 (21,0 $), Illinois 390 (18,5 $), North Carolina 320 (38,8 $) = **5.410 al mese**;
  «<stato> payroll tax rate»: 320 / 110 / 50 / 90 / 90; «employer payroll taxes <stato>»: California 260, Texas 90, Florida 70, Illinois 50, North Carolina senza dato;
  «how to do payroll in <stato>»: California 40 (106 $), Texas 30 (66 $), Florida 20 (55 $), Illinois e North Carolina senza dato: **piccole**, usate solo come FAQ;
  «florida employer taxes» 1.000 (19 $), «edd payroll taxes» 590 (25 $), «california de 9» 210, «florida unemployment tax» 480;
  generiche: «how to calculate payroll taxes» 2.900 (18,8 $), «how to do payroll» 1.300, «how to pay payroll taxes» 1.000 (54,7 $), «how to do payroll yourself» 590 (63,7 $),
  «how to do payroll for small business» 480 (131 $), «when are payroll taxes due» 480, «payroll tax deposit schedule» 320, «how to run payroll» 210 (63,8 $),
  «employee cost calculator» 1.300 (20,4 $), «form 941» 40.500, «form 940» 14.800. Già misurate la mattina: «<stato> payroll tax calculator» Texas 2.900, California 1.600,
  North Carolina 1.600, Illinois 1.000, Florida 590.
- Non coperto (detto in pagina): Form I-9, W-2 e W-3, regola dei 100.000 $, Form 944, calendario dei versamenti della ritenuta statale (Illinois, California, North Carolina
  nel dettaglio), giorno esatto in cui un DE 9 è in ritardo (la pagina EDD «Required Filings and Due Dates» non è tra le fonti).
- **Seconda revisione indipendente (14/11 sera)**: 30 fonti riscaricate, 106 frasi su 106 ritrovate alla lettera; tutte le cifre, scadenze e soglie delle 6 pagine rilette sulle fonti (0 differenze); riquadro provato acceso con link di prova e rispento. Corretti: «a Illinois paycheck» → «an Illinois», e nella FAQ californiana sull'aliquota ora è nominato lo 0,1 % di ETT compreso nel totale.
- **Da fare per pubblicare** (insieme agli altri siti): commit di `paycheck/`, poi IndexNow per i 6 indirizzi nuovi.

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
