# Payroll Tax by State (Australia) – note di lavoro

Costruito l'11/11/2026 dal piano della sez. 8 di `studio-business/intelaiatura/verifica-2026-11-09-payroll-tax-australia.md`.
Sito statico in inglese (en-AU) generato da `genera.py` in `sito/`: payroll tax delle 8 giurisdizioni australiane per l'anno
fiscale **2026-27** (1/7/2026 – 30/6/2027) e un calcolatore multi-Stato che gira solo nel browser.
Indirizzo: `https://payrolltaxbystate.com` (dal 13/11; costante `URL_SITO` in `genera.py`, unico punto da cambiare).
**Il sito Netlify NON è stato creato e niente è stato pubblicato** (passi in fondo). Nessun commit fatto.

## Pagine (21 indicizzabili + 404)

| Pagina | Contenuto |
|---|---|
| `/` | calcolatore 8 Stati in alto (con un esempio NSW+VIC+QLD), tabella 2026-27 con fonte e data, grafici soglie/aliquote, novità, guide, 5 FAQ |
| `/calculator/` | calcolatore, metodo (formula di ogni Stato con la fonte), cosa non fa, 3 FAQ, JSON-LD WebApplication |
| `/nsw/ … /nt/` (8) | cifre chiave, come si calcola (testo + formula), **esempi ufficiali ricalcolati dal nostro motore** (ACT e NT: esempio nostro dichiarato come tale), calcolatore dello Stato (Stato + "altri Stati"), soglia mensile e registrazione, scadenze, novità 2026-27, storico dal 2021-22, grouping, strumenti ufficiali, 2-4 FAQ, fonti |
| `/interstate-wages/` | regola, 8 esempi ufficiali ricalcolati, un caso a 4 Stati, regole nexus |
| `/grouping/` | come si viene raggruppati, DGE, esclusione, link alle 6 pagine ufficiali + Acts ACT/NT; nessun calcolo |
| `/regional-rates/` | VIC 1,2125 % (regola 85 %), QLD −1 % fino al 30/6/2030, aree, amnistia QLD, esempi nostri |
| `/thresholds-history/` | tabella 2021-22 → 2026-27 per Stato (celle vuote dove la fonte ufficiale non è leggibile) |
| `/due-dates/` | scadenze mensili e annuali per Stato, calendario 2026-27 NSW/QLD (e SA) |
| `/what-changed-2026-27/` | ACT (soglia 1,75 mln e 5 aliquote), NT 6,5 %, altri invariati, tabella ACT 2025-26 vs 2026-27 (nostro calcolo) |
| `/payday-super/` | dal testo della legge (C2025A00057): 7 giorni lavorativi, 20 giorni, 12 %, maggiorazione 60 %, abrogazione "approved clearing house" |
| `/over-the-threshold/` | passi, soglie di registrazione per Stato, sanzioni (portale congiunto) |
| `/about/`, `/how-we-check/`, `/privacy/`, `404.html` | |

FAQ: 53 domande (48 dell'11/11 + 5 del 13/11), ognuna nata da un suggerimento vero dell'autocompletamento Google (`gl=au`, `dati/domanda.json`, 66 radici,
628 suggerimenti, 11/11/2026) o da una ricerca con volume misurato in Australia (`dati/volumi-2026-11-13.json`, vedi 13/11); JSON-LD FAQPage identico al testo visibile.

## Fonti (lette con il nostro server l'11/11/2026, nessun blocco aggirato)

`raccolta/fonti.py` legge **69 fonti** e controlla **181 frasi esatte** (cifre ed esempi); scrive `dati/fonti.json` (HTTP, SHA-256, data
"Last updated" della pagina, esito di ogni frase). 66 lette con HTTP 200; 3 **non lette** (403 Cloudflare, mai aggirate): ATO (Payday
Super), ACT Revenue Office, NT Treasury. Le cifre ACT e NT vengono dal portale congiunto `payrolltax.gov.au/resources` e dai testi di legge.

Principali: portale congiunto (Last updated 28/10/2026); Revenue NSW (rates, interstate, key dates, registration, grouping, calculator);
SRO Victoria (current rates + CSV, threshold and phase-out, regional, surcharges, historical rates, grouping, lodgement) e **Payroll Tax Act 2007 (Vic)**
versione autorizzata 041, sch 1 cl 1, 1A, 5, 7A; QRO (rates,
deductions + immagine dell'esempio, regional discount, mental health levy, calculators, due dates, register, grouping, amnistia, panoramica
dell'Home Ownership and Other Legislation Amendment Act 2026) e
**Payroll Tax Act 1971 (Qld)** s 10, 10A, 29; WA Payroll Tax Employer Guide (calculation, interstate, local, returns, registration,
grouping) e **Pay-roll Tax Assessment Act 2002 (WA)** ss 8, 10, 13, 14; RevenueSA (rates, how calculated, rate table PDF, returns, register,
grouping, nexus) e **Payroll Tax Act 2009 (SA)** sch 1; SRO Tasmania (rates, Annual Adjustment Return Guideline PDF con 5 esempi,
lodge, registration, grouping) e **Payroll Tax Act 2008 (Tas)** sch 1 (formule in immagine, lette); ACT: **Determination 2026
DI2026-151** + explanatory statement, Determinations 2025/2024/2016 (storico), **Payroll Tax Act 2011** sch 1, s 9; NT: **Payroll Tax Act
2009** "as in force at 1 July 2026" (s 7A, s 87, sch 1 – formula AD letta dall'immagine della pagina 67 del PDF); Payday Super:
**Treasury Laws Amendment (Payday Superannuation) Act 2025** (Federal Register of Legislation).

## Formule: confermate sui testi ufficiali (nessuna stimata)

Tutte le formule del calcolatore sono in `motore.py` (riferimento Python) e identiche in `stile.MOTORE_JS`.

| Stato | Formula (W = salari australiani, q = quota dello Stato, f = giorni/365) | Confermata su |
|---|---|---|
| NSW | soglia 1,2 mln × q × f; 5,45 % | pagina Revenue NSW con 5 esempi |
| VIC | Act 2007 sch 1 cl 5 (cl 7A gruppi): ND = minore tra (b) D1 = 1 mln × q × f e (a) D1 − (w − 3 mln × q × f) × 50 %, (a) negativo = 0; **nessun limite su W** (con anno parziale la riduzione parte da 3 mln × f e la soglia è nulla da 5 mln × f); 4,85 % / 1,2125 %; **sovrattasse calcolate** 1 % sopra STA1 = 10 mln × f e +1 % sopra 100 mln × f (× q) | Act (versione autorizzata 041) + pagina SRO (2 esempi 2024-25 con 900k/45 %) + pagina surcharges; 2 casi calcolati dalla legge: 2,9 mln in 183 giorni → soglia 0, imposta 140.650,00; in 329 giorni → soglia 803.424,66, imposta 101.683,90 |
| QLD | AD = q × (K f − (W − K f)/7), K = 1,3 mln (Act s 29: **prima si riduce la soglia per i giorni, poi il taglio 1/7**, non "× f alla fine" come nel piano); 4,75 % / 4,95 % sopra 6,5 mln; −1 % regionale (non sopra 350 mln); **levy calcolata** 0,25 % sopra 10 mln e 0,5 % sopra 100 mln (soglie × q × f) | Act + esempio QRO 932.460 + 3 esempi levy (315.000, 3.750, 48.750) |
| WA | AAT = 1 mln × f, AUT = 7,5 mln × f; D = (AAT − (W − AAT) × 2/13) × q (Act ss 10, 13: anche qui **soglie ridotte per i giorni prima del taglio**) | Act + 3 esempi (969.231; 134.616/47.596,12; 6.600) |
| SA | nulla se W ≤ 1,5 mln × f; R = (W/f − 1,5 mln)/200.000 × 4,95 % fino a 1,7 mln annualizzati, poi 4,95 %; deduzione 600.000 × q × f | **Act sch 1 (formula esatta)**; la tabella RevenueSA è "indicativa": le 200 righe stanno entro 0,01 punti dalla formula |
| TAS | **marginale**: 4 % sulla fascia tra le due soglie ripartite, 6,1 % sopra la seconda | Act sch 1 (immagini delle formule) + 7 esempi della Guideline (54.400, 77.589, 72.800, 112.523, 44.741, 76.466, 116.153) |
| ACT | **non marginale**: un'unica aliquota R scelta dallo scaglione di W, applicata a tutti i salari ACT sopra la soglia ripartita | Act sch 1 + DI2026-151 (+ schedule 2A 2025-26 che faceva lo stesso) |
| NT | AD = ETA − (W − ETA)/2 ≥ 0, ETA = 2,5 mln × f; imposta (w − q AD) × R; 6,5 % se W ≥ 100 mln | Act s 7A e sch 1 |

**Rimandato all'ufficio (non calcolato):** un solo caso. ACT con anno parziale e salari totali ≤ 1,75 mln ma sopra la soglia
ridotta: si è tenuti a pagare, ma la tabella della determinazione parte "more than $1.75 million" e non dà un'aliquota per quel
livello. Il calcolatore scrive "not calculated" e rimanda all'ACT Revenue Office.

Differenze rispetto al piano (sez. 8.4), tutte per seguire il testo ufficiale: sovrattasse VIC e levy QLD sono **calcolate** (le pagine
ufficiali danno formula ed esempi) invece che solo segnalate; QLD e WA applicano i giorni alla soglia prima del taglio (Acts).
Non modellati (detto nelle pagine): esenzioni, contractor, apprendisti, indennità, ripartizione dell'imposta tra i membri del gruppo
(il risultato è il totale del gruppo), dichiarazioni mensili (la cifra mensile è annuale/12).

## File

| File | A cosa serve |
|---|---|
| `genera.py` | genera tutte le pagine (testi per Stato in `STATI`, FAQ da `dati/faq.json`) |
| `motore.py` | motore di calcolo di riferimento in Python |
| `stile.py` | CSS, icone, marchio, `MOTORE_JS` (copia del motore) e interfaccia del calcolatore |
| `verifica.py` | controlli (sotto); `--rete` rilegge le fonti, `--browser` lancia `verifica_browser.js` |
| `verifica_browser.js` | Playwright: 22 pagine × 375/1280 px × chiaro/scuro, niente scorrimento orizzontale, errori JS, testo < 11 px; 7 casi del calcolatore (anche ACT "not calculated" e link condiviso); pulsante del tema. Screenshot in `cache/screenshot/` (fuori da git) |
| `raccolta/fonti.py` | rilegge le 67 fonti e le frasi -> `dati/fonti.json` |
| `raccolta/domanda.py` | autocompletamento Google gl=au -> `dati/domanda.json` |
| `dati/giurisdizioni.json` | parametri 2026-27 (`parametri`) e fatti per Stato con gli id delle fonti |
| `dati/storico.json` | soglie e aliquote 2021-22 → 2026-27 (null = nessuna fonte ufficiale leggibile: NSW 2021-22, NT fino al 2024-25) |
| `dati/payday_super.json` | contenuto della pagina /payday-super/ (sezioni con fonti, esempio di un giorno di paga di luglio 2026 costruito solo con le regole della legge) |
| `dati/esempi_ufficiali.json` | 28 esempi numerici ufficiali + 2 casi calcolati dalla legge VIC (`legge: true`, non mostrati come ufficiali) + tabella SA (200 righe) + scaglioni ACT + regole NT + soglie mensili NSW + soglie sovrattasse VIC |
| `dati/faq.json` | 48 FAQ con la ricerca d'origine e le fonti |
| `dati/affiliati.json` | Employment Hero e MYOB: **preparati, spenti** |
| `grafica/` | font OFL (Public Sans, Source Serif 4), `og.html` + `og.js` -> `og.png` |

## Controlli (`python3 paytax/verifica.py --browser`, risultato dell'11/11/2026 dopo la revisione: 0 errori, 0 avvisi)

1. Fonti: 66 con HTTP 200, impronta, 181 frasi trovate; 3 non lette con motivo. Con `--rete` rilettura oggi; se la data "Last updated" di una pagina cambia o supera il nostro controllo: avviso.
2. Parametri: ogni soglia, aliquota, rapporto del JSON è scritto in una frase trovata nella sua fonte; aliquote 0-10 %; anno fiscale non scaduto (errore dopo il 30/6/2027).
3. Esempi: 28 ufficiali + 2 dalla legge VIC (35 cifre) entro tolleranza (1-3 $ dove l'ufficio arrotonda i passi), anche col JS; tabella SA; limiti ACT; regole NT; soglie mensili NSW; soglie sovrattasse VIC.
4. JS pubblicato = Python su 5.038 casi (5.000 casuali + 38 limite), nessuna imposta negativa, soglia ripartita ≤ piena, aliquote 0-10 %.
5. Numeri stampati (home) = motore; parametri nei calcolatori = JSON; nessun segnaposto.
6. FAQ da ricerche vere (autocompletamento o volume misurato > 0); JSON-LD = testo.
6b. (13/11) Ricerche misurate `RICERCHE_PAGINA` di `genera.py`: volume > 0 in `dati/volumi-2026-11-13.json`, la prima tutta nel titolo, le altre in titolo + h1 + descrizione + FAQ; titoli e descrizioni unici, descrizioni ≤ 160; nessuna chiave nel file misurato.
7. Canonical, titoli ≤ 65, descrizioni 70-165, un h1, link e ancore, sitemap = canonical, le 21 pagine del piano, robots, netlify.toml, chiave IndexNow, og.png, GoatCounter in ogni pagina (404 compresa), fonti con data e avviso "not tax advice" in ogni pagina di contenuto; modulo `corrections` (honeypot, consenso, email facoltativa) e privacy che lo spiega; spazio pubblicitario sempre dopo il calcolatore; parole del **contenuto proprio** (solo `<main>`, senza calcolatore, fonti, griglie delle guide, avviso): almeno 500 per ogni pagina di contenuto (oggi il minimo è /over-the-threshold/ con 515) e almeno 900 per /payday-super/, /regional-rates/, /what-changed-2026-27/, /how-we-check/.
8. Monetizzazione: `monetizzazione.controlla_sito` + nessun link affiliato a programmi spenti + prova di resa del riquadro acceso (rel="sponsored noopener", riga di trasparenza).
9. Nessun dato personale, nessun nome di modello AI (sito, codice, dati, questa nota).

Anche: `python3 studio-business/strumenti/monetizzazione.py verifica paytax` (0 errori).

## Aggiornamento ogni 1° luglio (e dopo i bilanci statali di maggio-giugno)

1. `python3 paytax/raccolta/fonti.py` – le frasi che spariscono indicano le cifre cambiate. Rileggere a mano le pagine segnalate, ACT
   (nuova determinazione "Taxation Administration (Amounts and Rates—Payroll Tax) Determination AAAA" sul registro ACT) e NT (Act aggiornato).
2. Aggiornare `dati/giurisdizioni.json`: `anno_fiscale`, `inizio`, `fine`, `giorni_anno` (**2027-28 ha 366 giorni**, 29/2/2028),
   `controllato_il`, `parametri`, testi per Stato; aggiornare le frasi `cerca` in `raccolta/fonti.py` con le cifre nuove.
3. Aggiungere la colonna del nuovo anno in `dati/storico.json`; aggiornare i testi "what changed" (pagina `what-changed-2026-27/`:
   crearne una per il nuovo anno e tenere la vecchia), le date delle scadenze (`scadenze()` e `STATI[...]["scadenze"]`) e le FAQ con anni.
4. `python3 paytax/raccolta/domanda.py` (nuove ricerche) e controllare che ogni FAQ abbia ancora la sua ricerca.
5. `python3 paytax/genera.py && python3 paytax/verifica.py --rete --browser` → 0 errori. Poi IndexNow.
Ogni mese basta `python3 paytax/verifica.py --rete` (pagine ufficiali cambiate = avviso/errore).

## Monetizzazione

- **AdSense acceso** come gli altri siti: `paytax` aggiunto a `SITI` in `studio-business/strumenti/monetizzazione.py` e a
  `adsense_siti` e `_siti_della_rete` in `monetizzazione.json`; `ads.txt` scritto da `genera.py`; privacy con la sezione AdSense.
  Gli annunci sono automatici: è Google a decidere dove compaiono, quindi non si promette che non finiscano sopra il calcolatore;
  lo spazio `ad-slot` riservato da noi è sempre dopo il calcolatore (controllato da `verifica.py`).
- **Affiliazioni preparate ma spente** (regola: domande ai programmi solo a 1.000 visite al mese). Per accenderle: in
  `dati/affiliati.json` mettere `attivo: true` e l'`url` del link tracciato; aggiungere il dominio del link (es. quello di PartnerStack
  per Employment Hero) a `domini_affiliazione` in `monetizzazione.json`; rigenerare e verificare. I riquadri compaiono: sotto il risultato
  del calcolatore quando l'imposta è > 0, in `/payday-super/`, `/over-the-threshold/`, nelle 8 pagine Stato (Employment Hero e MYOB),
  in `/due-dates/` e `/thresholds-history/` (MYOB). Nessun premio o incentivo per prenotare una demo (termini Employment Hero).
- IndexNow: aggiunto in `studio-business/strumenti/indexnow.py` (`SITI`) e in `NON_ONLINE` finché il sito non è su Netlify.

## Da fare per pubblicare (passi del titolare)

1. Netlify: nuovo sito dal repository, Base directory `paytax/sito`, Build command vuoto, Publish directory `.`; nome
   `payroll-tax-by-state` (se diverso, cambiare `URL_SITO` e rigenerare).
2. Search Console: proprietà `https://payrolltaxbystate.com/` (meta di verifica già nelle pagine), inviare la sitemap.
3. Togliere l'host da `NON_ONLINE` in `indexnow.py` e lanciare l'invio.

## Limiti noti

- Storico: NSW 2021-22 e NT fino al 2024-25 non sono in fonti ufficiali leggibili dal server (celle "not on a source we can read").
- Payday Super: la pagina ATO risponde 403; scriviamo solo ciò che è nella legge e rimandiamo all'ATO per la clearing house.
- Correzioni: modulo Netlify `corrections` in /how-we-check/#corrections (pagina, messaggio, fonte facoltativa, email facoltativa,
  consenso obbligatorio, honeypot). Si attiva da solo quando il sito è su Netlify (Forms: controllare che il rilevamento dei moduli
  sia acceso e impostare la notifica email nel pannello Netlify). La privacy spiega cosa si riceve e perché.
- Media mensile: con l'anno intero è l'imposta annua ÷ 12; con un anno parziale è divisa per i mesi di impiego (giorni ÷ 365 × 12).
- ACT non calcolato: il totale dice "total excludes ACT (not calculated)" e rimanda all'ACT Revenue Office.
- QLD tetto dei 350 mln per lo sconto regionale: QRO parla di salari australiani, l'Act s 10A(4) dei salari imponibili del datore nel periodo;
  il calcolatore applica il tetto ai salari australiani e lo dice (nessuna differenza sotto i 350 mln).

## Domanda misurata e titoli dalle ricerche (13/11/2026, NON pubblicato: revisione indipendente, poi pubblicazione)

**Attenzione al mandato.** La richiesta parlava di domanda **USA** (SUTA, FUTA, withholding per Stato). Il sito è sulla payroll tax
**australiana** (en-AU, 8 giurisdizioni): titoli e FAQ si sono rifatti sulle ricerche **australiane** (`country=au`); quelle USA sono
misurate e scritte sotto solo come informazione (nessuna pagina USA costruita).

**Misura.** `api.seodata.dev /v1/keyword` il 13/11/2026: 305 richieste andate a buon fine (193 Australia, 110 USA, 2 di prova; un primo
giro da Python senza curl è stato respinto con 403 prima di arrivare ai dati ed è stato rifatto con curl). File `dati/volumi-2026-11-13.json`
(volume, cpc, frasi simili; `errore: 404` = frase non nel database). Chiave mai scritta: il grep del prefisso della chiave su `paytax/` è vuoto, e
`verifica.py` (6b) lo ricontrolla.

**Ricerche australiane più cercate (al mese).** payroll tax 8.100 · payroll tax nsw 6.600 (cpc 11 $) · payroll tax queensland 4.400 ·
payroll tax qld 3.600 · payroll tax victoria 2.900 · payroll tax wa = western australia 2.400 · payday super 1.900 (cpc 17 $) = payday
superannuation 1.900 · payroll tax calculator 1.600 (cpc 15,6 $) · payroll tax thresholds 1.600 (cpc 23 $) · nsw payroll tax threshold 1.600 ·
payroll tax vic 1.600 · current super rate australia 1.600 · payroll tax sa = south australia 1.300 · payroll tax act 1.300 · what is payroll
tax 1.300 · nsw / qld payroll tax rate 1.000 · qld payroll tax threshold 880 · payroll tax rates 880 · vic payroll tax threshold 720 ·
payroll tax tasmania 590 (cpc 29,7 $) · superannuation rate 2026 590 · victoria payroll tax rate 480 · payroll tax due dates 480 ·
how is payroll tax calculated 390 · payroll tax nt = northern territory 320 · payroll tax registration / register for payroll tax 320 ·
payroll tax grouping 320 · payroll tax exemptions 320 · payroll tax contractors 320. Nel database ma senza volume o assenti:
"payroll tax new south wales", "payroll tax interstate wages", "regional payroll tax", "payroll tax changes 2026", "payday super 2026".

**Cosa è cambiato (tutto da `genera.py`; `NOMI_RICERCA` sceglie il nome più cercato per ogni Stato, `RICERCHE_PAGINA` lega pagina e ricerche):**

| Pagina | Titolo prima | Titolo dopo | h1 dopo | Ricerca guida (vol.) |
|---|---|---|---|---|
| `/` | Payroll Tax by State 2026-27: Rates, Thresholds, Calculator | Payroll Tax Australia 2026-27: Rates and Thresholds by State | Payroll tax in Australia by state: 2026-27 rates, thresholds and calculator | payroll tax 8.100, payroll tax australia 480, payroll tax rates 880, payroll tax thresholds 1.600 |
| `/calculator/` | Payroll Tax Calculator 2026-27: All Australian States | Payroll Tax Calculator Australia 2026-27: All 8 States | Payroll tax calculator 2026-27: all Australian states in one | payroll tax calculator 1.600, … australia 320 |
| `/vic/` | VIC Payroll Tax 2026-27: … | Victoria Payroll Tax 2026-27: Threshold, Rate, Calculator | invariato + ": threshold, rate and calculator" | payroll tax victoria 2.900 > vic 1.600 |
| `/qld/` | QLD Payroll Tax 2026-27: … | Queensland Payroll Tax 2026-27: Threshold, Rate, Calculator | idem | payroll tax queensland 4.400 > qld 3.600 |
| `/tas/` | TAS Payroll Tax 2026-27: … | Tasmania Payroll Tax 2026-27: Threshold, Rate, Calculator | idem | payroll tax tasmania 590 > tas 170 |
| `/nsw/`, `/act/` | titolo invariato | invariato | **NSW** / **ACT** payroll tax 2026-27: threshold, rate and calculator (prima il nome intero, che nessuno cerca) | payroll tax nsw 6.600, payroll tax act 1.300 |
| `/wa/`, `/sa/`, `/nt/` | invariato (sigla) | invariato | nome intero + ": threshold, rate and calculator" (le due forme pareggiano: sigla nel titolo, nome nell'h1) | 2.400 / 1.300 / 320 per forma |
| 8 Stati, descrizioni | "{nome} payroll tax 2026-27: …" | "{sigla o nome} payroll tax ({l'altra forma}) 2026-27: …" | | |
| `/over-the-threshold/` | Over the Payroll Tax Threshold? Registering, State by State | Payroll Tax Registration: When to Register in Each State | Payroll tax registration: when you must register, state by state (briciole, piede e guide: "Registration") | payroll tax registration 320, register for payroll tax 320 |
| `/thresholds-history/` | Payroll Tax Thresholds History by State, 2021-2027 | Payroll Tax Thresholds by State and Year, 2021-22 to 2026-27 | invariato | payroll tax thresholds 1.600, payroll tax threshold vic 2025 140 |
| `/payday-super/` | invariato | invariato; descrizione con "12% superannuation guarantee" | invariato | payday super 1.900, superannuation rate 2026 590 |
| `/interstate-wages/` | | invariato; descrizione 161 → 156 caratteri | | |

URL invariati (nessun rinvio). Negli h1 gli anni "2026-27" non vanno più a capo sul trattino (`<span class="nw">`, `.nw{white-space:nowrap}` in `stile.py`).

**FAQ nuove (5, ognuna da una ricerca misurata, risposte solo con cifre già nei dati e fonti già controllate; JSON-LD = testo):**
home "What is payroll tax?" (what is payroll tax 1.300; fonte nuova `portal_about` = home di payrolltax.gov.au, 3 frasi, HTTP 200) ·
NSW "What is the NSW payroll tax rate?" (nsw payroll tax rate 1.000) · VIC "What is the payroll tax rate in Victoria?" (victoria payroll tax
rate 480) · storico "What were the payroll tax thresholds in 2025-26?" (payroll tax threshold vic 2025 140; dai dati di `storico.json`) ·
Payday Super "What is the super guarantee rate in 2026-27?" (superannuation rate 2026 590; "charge percentage means 12" del Payday Super Act).
Fonti: 70 (67 lette con 200, 3 non lette), 184 frasi.

**Domanda non coperta (nessuna pagina nuova costruita oggi):**

| Tema | Volume AU | Fonte ufficiale leggibile (curl, nessun blocco aggirato) | Giudizio |
|---|---|---|---|
| Esenzioni (payroll tax exemptions, nsw … exemptions) | 320 + 140 | Revenue NSW exemptions 200; QRO exemptions 200; SRO Vic: indirizzo da trovare (404 su due tentativi) | candidata n. 1: pagina "Payroll tax exemptions by state" solo con l'elenco ufficiale di ogni Stato; serve revisore (molte eccezioni) |
| Contractor (payroll tax contractors, contractors payroll tax) | 320 + 70 NSW + 50 QLD | Revenue NSW contractors 200; SRO Vic contractors 200; QRO contractor 200; RevenueSA contractors 200; WA: indirizzo da trovare | candidata n. 2, ma tema da consulenza (relevant contracts, medici): solo testo ufficiale citato, niente casi nostri |
| Aliquota del super (current super rate australia, super rate 2026) | 1.600 + 590 + 590 | ATO 403 (non letta); il 12 % è nel Payday Super Act (letto) | coperta in parte con la FAQ nuova di /payday-super/ |
| PAYGW / "is payroll tax deductible" | 9.900 / 140 + 70 | ATO 403 | non coperte: fonte non leggibile |
| GP / medical centres (gp payroll tax victoria 170, patient tax qld 90) | piccole | QRO amnistia già letta (qld_amnesty) | da rivalutare con le esenzioni |

**USA (solo misura, il sito non tratta gli USA):** payroll taxes 18.100 (cpc 32 $) · payroll tax calculator 18.100 · suta 5.400 ·
employer payroll taxes 4.400 (cpc 33 $) · futa tax rate 3.600 · california payroll tax 2.400 · california withholding 2.400 · state withholding
tax 1.900 · texas payroll tax 1.300 · florida / new jersey payroll tax 1.000 · payroll tax by state 590 (in Australia 140) · "<state> unemployment
tax rate" 30-390 · "<state> suta rate 2026" e "<state> new employer rate": non nel database · social security wage base 2026 50.
Fonti: IRS Pub 15 e Topic 759 200; California EDD 200; SSA 403; Texas TWC 202 vuota (pagina in JS). Un sito o una sezione USA sarebbe un
progetto a parte (su un dominio diverso: payrolltaxbystate.com è già il dominio di questo sito australiano; pubblico, valuta e fonti diversi): da proporre alla sessione principale, non fatto qui.

**Controlli del 13/11:** `python3 paytax/genera.py` → `python3 paytax/verifica.py` 0 errori, 0 avvisi (nuova sezione 6b: 49 ricerche su 15
pagine); `python3 studio-business/strumenti/monetizzazione.py verifica paytax` 0 errori; Playwright 375/1280 su `/`, `/qld/`,
`/over-the-threshold/` con tutte le richieste esterne bloccate: niente scorrimento orizzontale, nessun errore JS, titoli e h1 nuovi.

**Revisione indipendente del 13/11 (prima della pubblicazione).** Rilette oggi con curl (UA normale, nessun blocco aggirato) 14 fonti:
portale congiunto (home e resources, "Last updated on: 28/10/2026"), Revenue NSW, SRO Victoria (current rates, regional, surcharges), QRO,
WA Employer Guide, RevenueSA, SRO Tasmania, determinazioni ACT DI2025-161 e DI2026-151, Payroll Tax Act 2009 (NT) in vigore all'1/7/2026,
Payday Super Act C2025A00057; ACT Revenue Office e NT Treasury rispondono 403 (non aggirato). Soglie e aliquote 2026-27 e 2025-26 degli
8 Stati, storico NSW dal 2022-23, sovrattasse e tasso regionale VIC, 12 % ("charge percentage means 12"): tutte uguali alle fonti.
Correzioni: la FAQ "What is payroll tax?" era una parafrasi delle frasi del portale → ora cita parola per parola le 3 frasi
di `portal_about`, e `verifica.py` (6) controlla che ogni citazione “…” di una FAQ sia dentro una frase controllata e trovata delle sue
fonti; descrizione di /payday-super/ senza la frase spezzata finale; indirizzo del sito in questa nota allineato a `URL_SITO`.
