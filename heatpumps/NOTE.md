# Heat Pump Grants UK – note di lavoro (12/11/2026)

Sito statico in inglese (en-GB) generato da `genera.py` in `sito/`: Boiler Upgrade Scheme (contributi pagati per regione, contea e
council di Inghilterra e Galles, regole ufficiali, costo mediano nazionale e quartili, costo dopo il contributo) e solare (impianti e
potenza per regione e per council del Regno Unito, costo per kW per regione).
Nato da `studio-business/intelaiatura/fronti-2026-11-11-impianti-uk.md` (idea 1) e dal riesame `riesame-2026-11-12-concorrenza.md`
(idea 1 COSTRUIRE); domanda misurata in `volumi-2026-11-12.md` sez. 3.5 (circa 85.000 ricerche al mese, CPC 7-23 £).
Indirizzo: `https://heat-pump-grants-uk.netlify.app` (costante `URL_SITO` in `genera.py` e in `verifica.py`). **Online dal 13/11/2026.**
Il lavoro del 13/11 (ricerche misurate, titoli, 5 pagine nuove) è descritto nella sezione datata in fondo: **non ancora pubblicato** (revisione
indipendente, poi pubblicazione dalla sessione principale).

## Pagine (230 indicizzabili dal 13/11, prima 225, + 144 noindex + 404)

| Pagina | Contenuto |
|---|---|
| `/` | cosa paga lo schema (5 importi con date), costo mediano luglio-settembre 2026 e quartili prima/dopo 7.500 e 9.000 £, domande per mese (record di settembre 2026), regole in breve, 10 regioni, 12 council con più contributi, solare, 6 FAQ |
| `/eligibility/` | regole con le parole di GOV.UK e Ofgem (chi, quali immobili esclusi, che impianto, come si fa domanda, IVA, cronologia delle modifiche 2023-2026), 8 FAQ |
| `/heat-pump-cost/` | mediana e quartili per trimestre dal 2022, mediana corretta per l'inflazione, costo per fascia di potenza 2025/26 (aria-acqua e geotermica), 3 FAQ |
| `/heat-pump-grants/` | tabella filtrabile dei 318 council, 10 regioni, 21 contee |
| `/heat-pump-grants/<regione>/` (10) | contributi pagati, per 10.000 famiglie (DESNZ), per anno finanziario, domande per mese (12 mesi), impianto sostituito nel 2025/26, tabella dei council, solare della regione |
| `/heat-pump-grants/<contea>/` (21) | come i council, con la tabella dei distretti |
| `/heat-pump-grants/<council>/` (318: 174 indicizzate, 144 noindex) | contributi pagati maggio 2022 - settembre 2026, per anno 2022/23-2025/26, 2026/27 finora (nostro calcolo), per 1.000 famiglie, posizione nella regione, confronto con regione e Inghilterra+Galles, council vicini, costo NAZIONALE dopo il contributo (riquadro "these costs are national, not local"), regole, solare del council (impianti e MW a fine 2025, 2020, per 1.000 famiglie, costo per kW della regione) |
| `/solar-panels/` e `/solar-panels/<regione>/` (12, Scozia e Irlanda del Nord comprese) | impianti e MW a settembre 2026, aggiunti in 12 mesi, costo medio per kW 2025/26 per fascia, impianti nuovi per mese, tabella dei council (fine 2025); 2 FAQ nell'hub |
| `/eco4/`, `/great-british-insulation-scheme/`, `/warm-homes-local-grant/`, `/solar-panel-grants/`, `/heat-pump-grants/scotland/` (13/11) | altri schemi: testo ufficiale citato + cifre DESNZ (vedi sezione del 13/11) |
| `/about/`, `/how-we-check/` (con modulo `corrections`), `/privacy/`, `404.html` | |

**Regola anti-pagine sottili (lezione AdSense):** una pagina council è indicizzata (canonical + sitemap + AdSense) solo con almeno
200 contributi pagati **e** tutti e quattro gli anni pubblicati da DESNZ (non oscurati): 174 council, l'82% dei contributi pagati
(soglia alzata da 100 a 200 nella revisione del 12/11, vedi in fondo). Le altre 144 hanno `noindex`, nessuna
pubblicità (`MON.SEGNO_SENZA_ADSENSE`), restano raggiungibili dalle tabelle. Contee, regioni e pagine solari regionali sono sempre
indicizzate (dati veri per luogo). Nessuna pagina per collegio elettorale (575 possibili con Q1.3 e ET 6.3 tabella 3: espansione futura).

## Fonti (OGL v3.0) – lette il 12/11/2026, nessun blocco aggirato

| id | File | Uscita | Cosa usiamo |
|---|---|---|---|
| `bus_xlsx` | DESNZ, Boiler Upgrade Scheme statistics September 2026 (xlsx, 30 fogli) | pubblicato 29/10/2026, prossimo 26/11/2026 | 1.1, 1.2A, 1.2B, M1.1, M1.2, Q1.1A/B, A1.3A, Q1.2, A1.7, A1.9, 1.3, 1.6, "Scheme background", "Commentary" |
| `solare_la_xlsx` | DESNZ, Renewable electricity by local authority 2014-2025 | 29/9/2026, prossimo 30/9/2027 | impianti e MW solari per council (2020, 2025), famiglie |
| `solare_et63_xlsx` | DESNZ, Energy Trends 6.3 Solar PV deployment (dati a settembre 2026) | 29/10/2026, prossimo 26/11/2026 | tabella 4 per regione (numero e MW, mensile) |
| `solare_costi_xlsx` | DESNZ, Solar PV cost data 2025/26, base TIC ("official statistics in development") | 28/5/2026, prossimo 27/5/2027 | mediana per kW (sommario), media per kW per regione e fascia, domestici |
| `gov_apply` | GOV.UK "Apply for the Boiler Upgrade Scheme" (API dei contenuti) | – | 30 frasi esatte controllate |
| `ofgem_bus`, `ofgem_owners` | Ofgem, pagine BUS e "property owners" | – | 6 + 16 frasi esatte |
| `mcs_find` | MCS, find an installer | – | solo link |

Gli xlsx stanno in `raccolta/_grezzi/` (fuori da git, `.gitignore`); impronta SHA-256, data e indirizzo in `dati/fonti.json`. Gli
indirizzi dei file si leggono sempre dall'API di GOV.UK (cambiano a ogni uscita).

**Attribuzione OGL (stampata nel piè di pagina e in /how-we-check/):** "Contains public sector information licensed under the Open
Government Licence v3.0." Più, per le tabelle per council e regione del BUS: "Contains OS data © Crown copyright and database right
2026", "Contains Royal Mail data © Royal Mail copyright and database right 2026", NSPL (ONS, OGL v3.0).

Regole 2026 rilette su testo ufficiale: £7,500 aria-acqua e geotermica; **£9,000** per case fuori rete scaldate a gasolio o GPL
"available from 21 July 2026 until 31 March 2027" (Ofgem; GOV.UK lo scrive come "additional £1,500 until March 2027"); **£2,500**
aria-aria dal 28/4/2026 "for residential properties only"; £5,000 biomassa; IVA a zero fino al 31/3/2027 (Ofgem scrive "0% VAT": sul
sito scriviamo "zero rate" per la regola sotto). Cambi del 28/4/2026 citati con le parole di DESNZ ("relaxing the requirement for a valid EPC" ecc.).

## Nostri calcoli (dichiarati nelle pagine)

- Costo dopo il contributo = costo ufficiale (che include il contributo) − 7.500 o 9.000 £. **Costo solo nazionale** (DESNZ non lo dà per regione o council): ogni pagina di luogo lo dice.
- Per 1.000 famiglie = contributi pagati (Q1.2) ÷ famiglie del file DESNZ sui council (stesso file del solare). Le regioni mostrano anche il dato ufficiale per 10.000 famiglie (1.2B, solo case).
- 2026/27 finora = cumulato (Q1.2) − somma dei 4 anni (A1.7), solo se nessun anno è oscurato.
- Esempi del solare: kW × costo per kW ufficiale. Barre "impianti nuovi per mese" = differenza dei cumulati mensili ET 6.3 (provvisori).
- Barnsley e Sheffield hanno codici diversi nei due file: abbinati per nome. Il file solare 2025 ha 31.900 impianti non assegnati a un council (nota 12 DESNZ): detto nelle pagine.

## Regola legale: niente prestiti

Nessuna parola su prestiti o pagamenti a rate (`verifica-2026-11-11-warm-homes-uk.md`). `verifica.py` rifiuta nel testo visibile e
negli attributi: loan(s), finance/financed/financing, APR (maiuscolo), credit…, "0%" isolato, interest-free, monthly payment(s), pay
monthly, borrow…, lend/lender/lending; e controlla lo stesso sul riquadro preventivi acceso di prova e sui testi di `affiliati.json`.
Le variazioni percentuali che arrotondano a zero si scrivono "no change"/"under 1%". GOV.UK cita per la Scozia un aiuto che non
nominiamo: scriviamo solo "Scottish Government's own home energy schemes".

## Monetizzazione

- AdSense acceso come gli altri siti: `heatpumps` aggiunto a `SITI` in `studio-business/strumenti/monetizzazione.py` e ad
  `adsense_siti` e `_siti_della_rete` in `monetizzazione.json`; `ads.txt` scritto da `genera.py`; privacy con la sezione AdSense.
  Pagine noindex senza pubblicità.
- **Riquadro "Get a quote" preparato e SPENTO** (`dati/affiliati.json`, `attivo: false`): Glow Green (Awin 73922: 250 £ pompa di
  calore, 300 £ solare) e BOXT (Awin 13574: 35 £). Il valore del sito dipende per tre quarti da Glow Green (stima del riesame).
  Per accenderlo: Massimiliano fa domanda dentro Awin; accettati, `attivo: true` e `url` del link tracciato `awin1.com` (dominio già
  ammesso), rigenerare e `verifica.py`. Il riquadro compare su home, costo, regole, regioni, contee, council e solare; testo solo
  "get a quote" (Ofgem consiglia più preventivi).

## Controlli (`python3 heatpumps/verifica.py --browser`, 12/11/2026: 0 errori, 0 avvisi)

1. Impronta SHA-256 di ogni xlsx = `dati/fonti.json`; pagine delle regole HTTP 200 con tutte le 52 frasi esatte.
2. **Ricalcolo indipendente**: `verifica.py` rilegge gli xlsx con codice suo (non `estrai.py`, non `dati/*.json`) e cerca nelle
   pagine 4.132 valori: per ogni council e contea cumulato, 4 anni (o "not published"), 2026/27 finora, per 1.000 famiglie, impianti
   solari e MW; per le regioni cumulato, per 10.000 famiglie, totale con biomassa, domande dell'ultimo mese, anni; per il solare
   numero, aggiunti in 12 mesi, costo per kW; home e costo: mediana, quartili, netti, geotermica, fasce. Regola di indicizzazione
   ricontrollata pagina per pagina.
3. Titoli ≤ 65 e descrizioni 70-160 unici, un h1, canonical = URL solo sulle indicizzate, noindex senza canonical e fuori sitemap,
   sitemap = canonical, link interni e ancore, robots, `netlify.toml` con `ignore`, chiave IndexNow, og.png, GoatCounter ovunque.
4. Parole vietate (sopra), nessun nome di modello AI (sito, codice, dati, questa nota), nessun dato personale né email nel testo.
5. FAQ: 19, ognuna da un suggerimento vero dell'autocompletamento gl=gb (`dati/domanda.json`, 51 radici, 423 suggerimenti); JSON-LD = testo.
6. `monetizzazione.controlla_sito` + nessun link affiliato con programmi spenti + riquadro di prova acceso corretto.
7. `--browser`: Playwright 375 e 1280 px, chiaro e scuro, su `/`, `/heat-pump-grants/cornwall/`, `/heat-pump-grants/south-west/`,
   `/solar-panels/`; tutte le richieste non locali bloccate con `page.route`; niente scorrimento orizzontale, testi ≥ 11 px, tema,
   filtro delle tabelle, nessun errore JS. Screenshot in `cache/screenshot/` (fuori da git).

Anche: `python3 studio-business/strumenti/monetizzazione.py verifica heatpumps` → 0 errori.

## Aggiornamento (ogni mese, dopo l'uscita DESNZ: prossima BUS 22/12/2026, ET 6.3 17/12/2026, WH:LG 25/2/2027)

1. `python3 heatpumps/raccolta/fonti.py` (scarica le ultime uscite via API GOV.UK, rilegge le frasi delle regole; se una frase manca,
   rileggere la pagina a mano e correggere testi e `cerca`).
2. `python3 heatpumps/raccolta/estrai.py && python3 heatpumps/genera.py && python3 heatpumps/verifica.py --browser` → 0 errori.
3. Le tabelle per council e i costi cambiano solo a gennaio, aprile, luglio e ottobre; domande e totali ogni mese. Il solare per
   council esce a settembre, i costi del solare a maggio. **Due periodi distinti dal 26/11/2026:** `PERIODO` (copertina, tabelle mensili
   1.1, 1.2A, M1.1, M1.2) e `PERIODO_LA` (titolo del foglio Q1.2, `periodo_la` in `bus.json`). Home, hub e regioni usano il dato
   mensile (pompe pagate = 1.2A meno biomassa); council e contee restano a `PERIODO_LA` e lo scrivono. Nelle uscite trimestrali i due
   coincidono e `genera.py` e `verifica.py` controllano che 1.2A meno biomassa = Q1.2.
4. **Se `estrai.py` si ferma** («foglio … non trovato», «colonna … non trovata», «frasi citate non trovate», «la somma … non dà il
   totale»): il formato è cambiato. Aprire l'xlsx, leggere il foglio a mano, correggere `estrai.py` **e** `verifica.py` (codice
   separato apposta); mai togliere il controllo. Vedi la sezione del 26/11/2026 in fondo.
5. **Entro il 31/3/2027** rileggere le regole: il contributo da 9.000 £ e l'IVA a zero scadono quel giorno (`genera.py` si ferma
   con un errore dopo il 31/3/2027). Se cambia l'anno finanziario (A1.7 con 2026/27), le pagine prendono da sole il nuovo anno.
6. FAQ: ogni tanto `python3 heatpumps/raccolta/domanda.py` e controllare che ogni FAQ abbia ancora la sua ricerca.
7. Pubblicare solo se `sito/` è cambiato (crediti Netlify); poi IndexNow.

## Da fare per pubblicare (passi del titolare)

1. Netlify: nuovo sito dal repository, branch `ccr-b7fd6b9e-n096cr`, Base directory `heatpumps/sito`, Build command vuoto, Publish
   directory `.`; nome `heat-pump-grants-uk` (se diverso, cambiare `URL_SITO` in `genera.py` e `verifica.py`, rigenerare).
   Forms: attivare il rilevamento dei moduli e la notifica email per `corrections`.
2. Search Console: proprietà `https://heat-pump-grants-uk.netlify.app/` (meta di verifica della rete già nelle pagine), inviare la sitemap.
3. Aggiungere `("heat-pump-grants-uk.netlify.app", "heatpumps")` a `SITI` in `studio-business/strumenti/indexnow.py` e lanciare l'invio
   (non fatto qui: il commit di questo lavoro è limitato a `heatpumps/` e alla registrazione in monetizzazione).
4. Awin: domanda a Glow Green (73922) e BOXT (13574) con questo sito.

## Limiti e dubbi per il revisore

- Costo solo nazionale: la domanda più cercata ("heat pump cost <regione>") non ha una risposta ufficiale aperta; lo diciamo.
- Le pagine council hanno testo a modello con numeri propri: soglia di indicizzazione 200 (174 su 318), vedi revisione.
- Volumi: l'API dei volumi ha risposto 429 (limite del conto) alle 2 richieste di oggi; usati i volumi misurati il 12/11 nel file citato.
- Il costo del solare usa la base TIC ("official statistics in development"); la base DNC dà cifre per kW più alte.
- Dati solari per council 2025 sottostimati (nota 12 DESNZ); capacità per council comprende i parchi solari.

## Revisione indipendente del 12/11/2026 (prima della pubblicazione)

- **Cifre:** i 4 xlsx riscaricati da GOV.UK (stesse impronte SHA-256) e riletti con un programma scritto da zero: 757 cifre
  confrontate su home, costo, 5 regioni, 5 contee, 19 council (4 noindex), hub solare e 4 regioni solari. Nessuna cifra sbagliata;
  4 valori con la seconda cifra decimale a 5 (per esempio 148,95 MW) uscivano arrotondati in giù (148.9): ora `n()` e `gbp()`
  arrotondano a metà verso l'alto (149.0), e così `verifica.py`.
- **Soglia di indicizzazione 200** (era 100): con 262 pagine council su 313 il sito era per l'84% un solo modello. Misura sulle
  pagine area indicizzate, prima: 1.056 parole nel corpo, 54% identiche su tutte, 32% in righe proprie, 54 numeri propri. Dopo:
  991 parole, 38% identiche, 47% in righe proprie, 77 numeri propri. Fatto così: tabella dei costi nazionali sostituita da un
  solo paragrafo (resta sulle pagine regione, costo e home), regole in un paragrafo con rimando, e un paragrafo nuovo con dati
  solo di quell'area (posizione per numero e per famiglia in regione e su 318, quota di famiglie contro quota di contributi, anno
  più alto, caldaie a biomassa). Pari merito scritti "joint". **Quando abbassarla:** dopo l'approvazione AdSense e quando Search
  Console mostra indicizzate almeno 150 delle 174, riportare `SOGLIA_INDICE` a 100 in `genera.py` e in `verifica.py` (+88 pagine).
- **Base dei prezzi corretti per l'inflazione:** il titolo del foglio Q1.1B dice ancora "2026 Q2 prices", ma la nota 28 dice
  "prices as at the latest quarter" e nei dati il valore reale dell'ultimo trimestre è uguale al nominale (12.826): la base è
  luglio-settembre 2026. La pagina lo scrive così e `genera.py` lo ricava dai dati (se un giorno non coincidono scrive
  "latest-quarter prices"). `costi_reali_base` in `bus.json` (dal titolo) non è usato.
- **Barnsley e Sheffield:** il file BUS usa i codici nuovi (E08000038, E08000039), il file solare quelli vecchi (E08000016,
  E08000019); abbinamento per nome ricontrollato, cifre giuste.
- **Solare per council:** l'avviso sui 31.900 impianti 2025 non assegnati c'è sulle pagine council e sotto le tabelle regionali.
- **Regole:** rilette oggi su GOV.UK (API dei contenuti) e Ofgem: importi, date (28/4/2026, 21/7/2026-31/3/2027), esclusioni e IVA
  coincidono. Due risposte ammorbidite: "Can I get a grant" ora parte da "GOV.UK says you are eligible if" e chiude con il controllo
  di installatore e Ofgem; la risposta sull'IVA non dice più "Not until" (l'aliquota zero non vale per tutti gli edifici).
- **Legale:** nessuna parola su prestiti o rate in pagine, FAQ, JSON-LD, attributi, `affiliati.json`. Quando si accende il riquadro,
  il link tracciato deve portare alla pagina dei preventivi del partner, non a una pagina sui pagamenti.
- **Attribuzione:** OS e Royal Mail ora anche nel piè di ogni pagina (prima solo in /how-we-check/). Data di uscita di ET 6.3 nelle
  fonti presa dalla copertina del file (29/10/2026), non dalla pagina che lo raccoglie (12/11/2026).
- Rimandi alle fonti [1] portati a 11 px minimi su telefono.


## Domanda misurata, titoli, FAQ e pagine nuove (13/11/2026, NON pubblicato: revisione indipendente, poi pubblicazione)

Metodo del 13/11 (come farmaci/, ccnl/, paytax/): misurare la domanda, poi titoli e FAQ sulle frasi misurate, pagine nuove solo dove ci sono
domanda (≥ 100 al mese) e fonte ufficiale leggibile.

**Misura.** `api.seodata.dev /v1/keyword`, `country=gb`, 13/11/2026: **337 richieste** (174 frasi con volume, 163 non nel database = 404).
Script nuovo `raccolta/volumi.py`: chiama **curl** (da Python con urllib lo strumento risponde 403) e passa la chiave solo dallo standard input
(`curl -K -`), quindi mai negli argomenti, nei file o nei messaggi. File `dati/volumi-2026-11-13.json` (volume, cpc £, data del dato, frasi simili).
`verifica.py` controlla che in `heatpumps/` non ci sia il prefisso della chiave; `grep -r` dello stesso prefisso: vuoto.

**Ricerche più cercate (UK, al mese).** Fuori tema ma enormi: energy performance certificate 110.000, epc check 74.000, warm home discount 33.100
(sconto in bolletta), ofgem 33.100. Pompe di calore: air source heat pump 33.100 · heat pump cost 8.100 · ground source heat pump 8.100 ·
heat pump grant(s) 5.400 (cpc 11 £) · air source heat pump cost 5.400 · boiler upgrade scheme 4.400 (cpc 9,7 £) · how much is a heat pump 4.400 ·
air source heat pump grant(s) 2.900 · how much does a heat pump cost 2.900 · heat pump installation cost 2.400 · government boiler scheme 1.900 ·
heat pump cost uk 1.900 · government grants for heat pumps 1.600 · ground source heat pump cost 1.600 · boiler upgrade grant 1.300 ·
heat pump grant uk 880 · government heat pump grant 880 · heat pump grant scotland 590 · heat pump installers 590 · boiler upgrade scheme
eligibility 480 · ground source heat pump grant 480 · bus grant 480 · heat pump grant eligibility 390 · heat pump grant wales 210 · heat pump grant
northern ireland 210 · air to air heat pump grant 140. Altri schemi: eco4 scheme 9.900 · eco4 / eco 4 grant / great british insulation scheme /
loft insulation grant / free boiler scheme / home energy scotland 4.400 · eco4 grant(s) 3.600 · new boiler grant 3.600 · external wall insulation
grant 2.900 · cavity wall insulation grant 2.400 · warm homes plan 1.900 · gbis scheme 1.900 · warm homes local grant 1.600 · home upgrade grant
1.600 · eco4 eligibility 1.300 · warmer homes scotland 1.300 · home energy scotland grant 1.000 · nest wales 880 · affordable warmth scheme ni 590.
Solare: solar panels 60.500 · solar panels cost / uk 9.900 · solar panel grants 8.100 · solar panel grants uk / solar panel grant 6.600 ·
government grants for solar panels 3.600 · free solar panels 2.400 · smart export guarantee 1.600 · solar panels scotland / northern ireland 1.600 ·
solar panels grant scotland 1.300 · solar panels grant wales 1.000 · vat on solar panels 390.
**Non nel database (404):** tutte le 43 frasi "heat pump grant <council/città/contea>" (anche "air source heat pump grant <contea>") (London, Cornwall, Devon, Kent, Leeds, Glasgow…), "£7500 heat pump
grant" e varianti, "boiler upgrade scheme 2026/9000/air to air/landlords/new build", "heat pump installers near me", "warm homes plan eligibility",
"eco4 2026", "nest grant". Le pagine council restano per i dati, non per la ricerca: **nessun cambio ai 318 council**.

**Titoli, h1, descrizioni (tutto da `genera.py`; `RICERCHE_PAGINA` lega pagina e ricerche; URL invariati):**

| Pagina | Titolo prima | Titolo dopo | h1 dopo | Ricerca guida (vol.) |
|---|---|---|---|---|
| `/` | Heat Pump Grant UK 2026: £7,500 Boiler Upgrade Scheme Figures | invariato | invariato | heat pump grant 5.400, boiler upgrade scheme 4.400; descrizione con "government heat pump grant" 880 |
| `/eligibility/` | Boiler Upgrade Scheme Eligibility 2026: Who Can Get the Grant | Air Source Heat Pump Grant: Boiler Upgrade Scheme Eligibility | Boiler Upgrade Scheme eligibility: who can get the heat pump grant (era "Who can get the heat pump grant") | air source heat pump grant 2.900, boiler upgrade scheme eligibility 480, heat pump grant eligibility 390 (descrizione) |
| `/heat-pump-cost/` | Heat Pump Cost UK 2026: Official Median After the Grant | Air Source Heat Pump Cost UK 2026: Official Median After Grant | How much does a heat pump cost? The official median, before and after the grant (era "How much a heat pump costs after the grant") | air source heat pump cost 5.400 (contiene heat pump cost 8.100 e heat pump cost uk 1.900), how much does a heat pump cost 2.900 |
| `/solar-panels/` | Solar Panel Cost UK 2026 by Region: Official £ per kW | Solar Panels Cost UK 2026: Official £ per kW by Region | invariato | solar panels cost 9.900 |
| `/heat-pump-grants/wales/` | Heat Pump Grants in Wales: 4,980 Paid, by Council | Heat Pump Grant Wales: 4,980 Paid and the Nest Scheme | Heat pump grants in Wales: Boiler Upgrade Scheme and Nest | heat pump grant wales 210, nest wales 880 |
| `/eco4/` (nuova) | – | ECO4 Scheme 2026: Eligibility, End Date and What It Covers | ECO4 grant scheme: who is eligible and when it ends | eco4 scheme 9.900, eco4 4.400, eco4 grant 3.600, eco4 eligibility 1.300 |
| `/great-british-insulation-scheme/` (nuova) | – | Great British Insulation Scheme (GBIS): Ended 31 March 2026 | Great British Insulation Scheme: closed, and what it installed | great british insulation scheme 4.400, gbis 1.600, loft insulation grant 4.400 (FAQ) |
| `/warm-homes-local-grant/` (nuova) | – | Warm Homes Local Grant 2026: Eligibility and What It Pays For | Warm Homes: Local Grant: who can get it and what it pays for | warm homes local grant 1.600, warm homes plan 1.900 (FAQ), warm homes grant 1.300 (FAQ) |
| `/solar-panel-grants/` (nuova) | – | Solar Panel Grants UK 2026: Which Official Schemes Cover Them | Solar panel grants in the UK: which official schemes pay for panels | solar panel grants uk 6.600 (contiene solar panel grants 8.100), government grants for solar panels 3.600, free solar panels 2.400 |
| `/heat-pump-grants/scotland/` (nuova) | – | Heat Pump Grant Scotland: Home Energy Scotland and Warmer Homes | Heat pump grants in Scotland: Home Energy Scotland grant and Warmer Homes Scotland | heat pump grant scotland 590, home energy scotland 4.400, warmer homes scotland 1.300 |

Prima del 13/11 le descrizioni di home ed eligibility non contenevano "government heat pump grant" né "heat pump grant eligibility"; ora sì
(147 e 148 caratteri). Le altre 9 regioni hanno titolo invariato ("heat pump grant <regione>" non è nel database).

**Pagine nuove (5; erano candidate anche Warm Homes Plan, Irlanda del Nord, Galles: vedi "non fatte").** Ognuna: testo ufficiale citato con il
rimando, cifre ufficiali DESNZ ricalcolate da `verifica.py`, FAQ, "Other grants and schemes", fonti; contenuto proprio 700+ parole (controllato).
- `/eco4/`: GOV.UK "Help from your energy supplier" (chiude il **31/12/2026**, benefici, EPC D-G proprietari, E-G affitto privato, social housing
  E-G) + Ofgem ECO ("will run until 31 December 2026, following a nine-month extension") + DESNZ Household Energy Efficiency tabella 1.6:
  **1.043.846 misure in 306.624 case** ad aprile 2026 (colonna "Surplus Actions, ECO3 Interim and ECO4"), 45.870 pompe aria-acqua, 65.484 FV,
  103.339 caldaie, 143.305 sottotetti.
- `/great-british-insulation-scheme/`: Ofgem (chiuso, aprile 2023 - 31/3/2026, criteri D-G e fasce council tax) + GOV.UK + DESNZ GBIS giugno 2026:
  **100.940 case, 139.136 misure**, per tipo e per regione/nazione con il tasso DESNZ per 100.000 famiglie (Nord Est 919, Londra 174, GB 355).
- `/warm-homes-local-grant/`: GOV.UK (solo Inghilterra, reddito di norma ≤ 36.000 £, EPC D-G, "You will not need to pay for it") + DESNZ WH:LG
  agosto 2026 (dati a luglio): **5.469 case, 11.247 misure**, FV 4.297 (costo medio 7.200 £), pompe aria-acqua 894 (14.800 £), per mese e per
  regione; citazione DESNZ "The Warm Homes: Local Grant (WH:LG) is part of this plan" (Warm Homes Plan).
- `/solar-panel-grants/`: nessun contributo nazionale; WH:LG (Inghilterra), Nest (Galles), ECO4; Scozia: la tabella di Home Energy Scotland segna
  "Not available" come contributo per solare termico e PV-T; IVA a aliquota zero fino al 31/3/2027 (HMRC VAT Notice 708/6, batterie dal 1/2/2024);
  Smart Export Guarantee (Ofgem); costo per kW dai dati già nel sito. Il Boiler Upgrade Scheme non copre il solare.
- `/heat-pump-grants/scotland/`: BUS non in Scozia (GOV.UK); Home Energy Scotland: contributo fino a 7.500 £ per la pompa di calore, +1.500 £
  rurale/isole, fino a 75 % (max 7.500 £) per l'isolamento, fino a 18.000 £ in totale, solo pompe che coprono tutto il riscaldamento (no ibride,
  aria-aria, aria esausta), tabella dei contributi; Warmer Homes Scotland (≥ 10.000 £, condizioni); ECO4 vale anche in Scozia; GBIS Scozia
  6.044 case; solare Scozia.
**Pagine cambiate oltre ai titoli:** Galles (sezione Nest con le parole di GOV.WALES, 2 FAQ); tutte le 10 regioni E+G (paragrafo "Other schemes
in …" con GBIS della regione e, in Inghilterra, WH:LG: dati propri di ogni regione); home (blocco "Other grants…", FAQ Irlanda del Nord);
eligibility (blocco altri schemi, FAQ ground source); hub aree (rimando Scozia); hub solare (rimando ai contributi); piè di pagina (5 guide nuove,
su tutte le 375 pagine); how-we-check e about (fonti nuove, licenze GOV.WALES/nidirect, citazioni Ofgem e Home Energy Scotland attribuite);
avviso in fondo alle pagine reso generico (prima diceva che l'idoneità la controlla Ofgem: vero solo per il BUS).

**FAQ: 46 (erano 19), +27** da ricerche misurate (campi `misurata`, `volume_gb` in `dati/faq.json`): home (Irlanda del Nord: BUS solo E+G, Boiler
Replacement Scheme NI chiuso, Affordable Warmth Scheme da nidirect), eligibility (ground source 480), costo ("how much is a heat pump" 4.400:
mediana per fascia di potenza 2025/26), Galles 2, Scozia 3, ECO4 5 (anche "new boiler grant" 3.600, "eco4 solar panels" 260), GBIS 4 (anche
"loft insulation grant" 4.400), WH:LG 4 ("warm homes plan" 1.900 risposto con la frase DESNZ), solare 6. Ogni citazione tra “…” è controllata
dentro una frase verificata della sua fonte (o nel testo dell'xlsx).

**Fonti nuove (lette il 13/11/2026 con lo stesso programma `raccolta/fonti.py`, nessun blocco aggirato):** 3 xlsx DESNZ (OGL) presi dall'API di
GOV.UK come gli altri: `gbis_xlsx` (GBIS statistics June 2026, ultima uscita mensile; ancora una prevista il 21/1/2027), `whlg_xlsx` (WH:LG
August 2026, ora trimestrale, prossima 26/11/2026), `hee_xlsx` (Household Energy Efficiency headline June 2026; DESNZ propone ancora un'uscita a
fine 2026 e una finale). 12 pagine con **102 frasi esatte** in più (tutte trovate; in totale 154): GOV.UK `gov_eco`, `gov_gbis`, `gov_whlg`,
`hmrc_vat`; Ofgem `ofgem_eco`, `ofgem_gbis`, `ofgem_seg`; Home Energy Scotland `hes_grant`, `hes_whs` (servizio del Scottish Government; testo
non OGL: solo citazioni brevi attribuite); GOV.WALES `wales_nest`, `wales_nest_free`; nidirect `nid_grants`. **Non lette (403, non aggirate):**
NIHE Affordable Warmth, Energy Saving Trust (NISEP, Cloudflare). Le 4 xlsx già usate sono identiche (stesse impronte).

**Regola "niente prestiti" e nomi dei sussidi.** ECO4 si spiega solo con l'elenco dei benefici di GOV.UK, che contiene "Universal Credit",
"Pension Guarantee Credit", "Pension Savings Credit". `verifica.py` toglie **solo questi tre nomi esatti** prima di cercare "credit" (variabile
`SUSSIDI`); ogni altro "credit" resta vietato. La Scozia: il programma di Home Energy Scotland si chiama "Grant and Loan" e Warmer Homes Scotland
cita un prestito; il sito nomina solo "Home Energy Scotland grant" e cita solo le frasi sui contributi (titolo della fonte: "Home Energy Scotland:
funding for homeowners"). **Warm Homes Plan:** nessuna pagina propria perché la sua parte principale per i proprietari è il Warm Homes Loan
Scheme (GOV.UK 28/10/2026, finanziatori nominati): la ricerca "warm homes plan" (1.900) ha solo la FAQ con la frase DESNZ sul WH:LG.

**Domanda non coperta (nessuna pagina):**

| Tema | Volume UK | Perché no |
|---|---|---|
| EPC (energy performance certificate, epc check, epc rating) | 110.000 / 74.000 / 40.500 | servizio GOV.UK di ricerca, non un dato che possiamo dare; solo link al registro nelle pagine ECO4 |
| Warm home discount | 33.100 | sconto in bolletta, non un contributo per impianti; fuori tema (possibile pagina futura con fonte GOV.UK) |
| Warm Homes Plan | 1.900 | parte principale = prestiti (regola legale) |
| Irlanda del Nord (affordable warmth 590+480, boiler replacement NI 390+390, warm homes NI 390, nisep 170) | ~2.400 | NIHE ed EST 403; nidirect ha 2 frasi: solo FAQ in home |
| Home upgrade grant | 1.600 | nessuna frase ufficiale letta che leghi HUG e WH:LG |
| Heat pump installers (590; "near me" non nel database) | 590 | nessun dato ufficiale per luogo; il riquadro preventivi resta spento |
| Boiler grants (free boiler scheme 4.400, new boiler grant 3.600, boiler replacement grant 1.600) | ~11.000 | coperti solo dalla FAQ ECO4 "new boiler grant"; una pagina sarebbe un doppione di /eco4/ |
| Insulation grants (external wall 2.900, cavity 2.400, free loft 1.900) | ~9.000 | FAQ "loft insulation grant" su GBIS; una pagina "insulation grants" con ECO4+WH:LG+HES è la candidata n. 1 per il prossimo giro |

**Controlli del 13/11 (`verifica.py`, sezioni nuove):** 2b ricalcolo indipendente da `gbis.xlsx`, `whlg.xlsx`, `hee.xlsx` (134 valori su pagine
nuove, Scozia, Galles, Nord Est, Londra); 4 FAQ: ricerca in `domanda.json` **oppure** volume misurato > 0 uguale a `volume_gb`, citazioni “…”
dentro le frasi controllate; 4b ricerche per pagina (43 su 10 pagine: volume > 0, la prima tutta nel titolo, le altre in titolo, h1, descrizione
o FAQ), 5 pagine nuove ≥ 700 parole di contenuto proprio, nessuna chiave dello strumento; nomi dei sussidi (sopra); `--browser` ora su 7 pagine
(+ /eco4/, /heat-pump-grants/scotland/, /warm-homes-local-grant/). `genera.py` si ferma dopo il **31/12/2026** finché la pagina ECO4 non viene
riscritta (fine dello schema).
Risultati: `python3 heatpumps/genera.py` → 230 indicizzabili + 144 noindex + 404; `python3 heatpumps/verifica.py --browser` → **0 errori, 0 avvisi**
(4.132 cifre BUS/solare + 134 schemi; 46 FAQ; 7 pagine × 375/1280 × chiaro/scuro, richieste esterne bloccate); `python3
studio-business/strumenti/monetizzazione.py verifica heatpumps` → 0 errori; Playwright a parte su /solar-panel-grants/ e
/great-british-insulation-scheme/ a 375 e 1280 px (solo file locali serviti, tutto il resto bloccato): niente scorrimento orizzontale, nessun
errore JS, nessun testo < 11 px. Riquadro preventivi: spento come prima.

**Aggiornamento (in più rispetto alla procedura sopra):** WH:LG trimestrale (prossima 26/11/2026, stesso giorno del BUS): `raccolta/fonti.py`
la prende da sola. GBIS: un'ultima uscita il 21/1/2027. ECO4: dopo il 31/12/2026 riscrivere `/eco4/`, le FAQ ECO4 e i rimandi "until 31 December
2026" (anche in `altri_schemi`, Scozia, solare, regioni). IVA a zero e 9.000 £: 31/3/2027 (controllo già presente). Ricerche: rimisurare ogni
qualche mese con `python3 -I heatpumps/raccolta/volumi.py elenco.txt` (scrive un file nuovo con la data; aggiornare `FILE_VOLUMI` in `verifica.py`).

**Dubbi per il revisore:** (a) eccezione "Universal Credit"/"Pension … Credit" alla parola vietata "credit"; (b) citazioni da Home Energy Scotland
(non OGL) e omissione della parte prestiti di quello schema; (c) ECO4: la colonna DESNZ comprende ECO3 "interim" e "surplus actions" (detto
nella didascalia); (d) titolo eligibility "Air Source Heat Pump Grant: …" sulla pagina di tutte le tecnologie (la pagina copre anche
ground source, aria-aria e biomassa); (e) titolo costo "… Cost UK" con dati solo Inghilterra e Galles (come prima; la pagina lo dice).

**Revisione indipendente (14/11/2026).** Fonti rilette da zero con un programma diverso (curl + estrazione propria): le 3 xlsx DESNZ sono le ultime
uscite e hanno le stesse impronte dei file in `_grezzi`; 132 frasi esatte su 132 presenti nelle pagine ufficiali; circa 190 cifre delle 5 pagine
nuove, dei paragrafi delle 10 regioni e delle FAQ confrontate a mano con le tabelle (GBIS T2-T4, WH:LG T1-T3, HEE 1.6): 0 differenze.
Correzioni fatte in `genera.py` e `dati/faq.json`: (1) ECO4: la nota sotto le cifre e la FAQ "What is the ECO4 scheme?" ora dicono che il conteggio
DESNZ comprende ECO3 interim e surplus actions (solo ECO4: 952.923 misure, 238.044 case; prima lo diceva solo la didascalia della tabella);
(2) descrizioni di home, eligibility e costo con "in England and Wales" (i titoli dicono "UK" o non dicono l'ambito); (3) Scozia: la frase copiata
parola per parola da Home Energy Scotland ora è attribuita e riformulata, la cifra in alto dice "maximum", la didascalia dice "Selected rows".
Risposte ai dubbi: (a) eccezione per i tre nomi esatti dei sussidi: va bene; (b) Home Energy Scotland: citazioni brevi e attribuite, la parte
non a fondo perduto resta fuori, va bene (l'unica traccia è l'indirizzo della fonte); (c) risolto con la correzione 1; (d) titolo eligibility:
tenuto (la pagina risponde alla ricerca e la descrizione nomina ground source, £9,000 e £2,500); (e) titolo costo "UK": tenuto, ambito ora nella
descrizione. Blocco del generatore dopo il 31/12/2026: sensato, ma ferma anche l'aggiornamento mensile del BUS finché `/eco4/` non è riscritta:
metterlo in agenda per la settimana del 28/12.


## Aggiornamento del 26/11/2026: formato degli xlsx cambiato (NON pubblicato, nessun commit: da rivedere)

Uscite DESNZ del 26/11/2026, ore 9:30: BUS «October 2026», ET 6.3 (dati a ottobre), Warm Homes: Local Grant «November 2026» (dati a
ottobre), HEE «November 2026» (ECO4 a settembre). `fonti.py` le aveva scaricate; `estrai.py` cadeva e `genera.py` aveva rigenerato il
sito con `bus.json` nuovo e `schemi.json` vecchio.

**Che cosa è cambiato nei file**

| File | Cambio | Effetto sul vecchio codice |
|---|---|---|
| `whlg.xlsx` | foglio «About this release» rinominato «About this Release» (stesso contenuto: piano, «Data Completeness») | `KeyError` in `estrai.py` |
| `whlg.xlsx` «About this Release» | frase sui progetti: da «based on data submitted by 67 of these projects» a «includes valid delivery data reported by 69 of these projects and linked to TrustMark lodgements» | regex senza risultato |
| `whlg.xlsx` T2 | colonne riordinate: misure (3ª), % misure, **costo medio (5ª, era 7ª)**, **case (6ª, era 5ª)**, % case; righe di subtotale per gruppo; celle vuote come stringa `""`; costi oscurati `N/A` (nota 4) | `estrai.py` avrebbe scritto il costo come «case» e una percentuale come costo; `verifica.py` cadeva con `decimal.InvalidOperation` sulla cella `""` in fondo alla riga Total |
| `whlg.xlsx` | intestazioni «Grant Recipient-reported …»; tabelle nuove T4 (collegi), T5 (enti locali), T6 (combined authorities) con `#` e `^` per i valori oscurati; date in Title invariate (periodo, «updated on», prossima 25/2/2027) | T4-T6 non usate (espansione possibile) |
| `bus.xlsx` | 32 fogli (nuovo «1.3B», domande per combustibile sostituito); nel foglio «Scheme background» la frase «The Government confirmed funding … up to 2029/30 …» è sostituita da «The Government will maintain the current funding levels at £400m in 2027/28, rising broadly in line with inflation thereafter.» | `/eligibility/` avrebbe stampato «None» dentro la citazione |
| `bus.xlsx` Commentary | il periodo delle domande da £9,000 è «July to October 2026» | la home aveva «From July to September 2026» scritto fisso con i numeri nuovi |
| `bus.xlsx` Q1.2, A1.7 | invariati (trimestrali, a settembre 2026): è la prima uscita non trimestrale da quando esiste il sito | le pagine scrivevano «May 2022 to October 2026» accanto a cifre di settembre (council, contee, regioni, home, hub) |
| `hee.xlsx` | stessa struttura; prossima uscita «Summer 2027»; misure ECO4 riviste al ribasso da Ofgem (1.043.846 → 1.043.418, case 306.624 → 304.814: nota in «Further Info») | nessuno |
| `solare_et63.xlsx` | stessa struttura, una colonna in più (Oct 2026) | nessuno |

**Correzioni**

- `estrai.py`: `foglio()` cerca il foglio per nome senza badare a maiuscole e spazi e, se non c'è, per contenuto; `colonna()` trova
  le colonne dall'intestazione (una sola corrispondenza, altrimenti si ferma); `numero()`/`intero()` accettano numeri, lasciano come
  testo le celle oscurate (`N/A`, `#`, `^`, `[c1]`, `[x]`) e si fermano su celle vuote o altro testo. Controlli di coerenza WH:LG:
  somma dei mesi = totale, totali T1 = T2 = somma delle 9 regioni di T3, ultimo mese = periodo della copertina. Ogni frase citata
  del BUS deve esserci, altrimenti l'estrazione si ferma (prima finiva `None` nella pagina). Nuovo campo `periodo_la`.
- `verifica.py` (codice suo): colonne WH:LG dalle intestazioni; `_cifra()` distingue cella oscurata (avviso, nessuna cifra da
  cercare) da cella vuota o testo (errore); `_arr()` rifiuta i non numeri con un messaggio chiaro. Nuovi controlli: periodo della
  copertina = ultima colonna di M1.1; home con le pompe pagate di 1.1 meno biomassa e la frase sulle £9,000 con periodo e numeri del
  commento di questa uscita; regioni con 1.2A meno biomassa e «2026/27 so far»; ogni pagina council/contea deve dire «May 2022 to
  <periodo di Q1.2>» e non può attribuire quelle cifre al mese della copertina. Valori controllati: 6.178 (erano 4.132).
- `genera.py`: `PERIODO_LA`, `POMPE` (mensile per regione), `TASSO_REG_M`/`TASSO_EW_M`; periodo delle £9,000 letto dal commento;
  `dati/faq.json` usa `{fine9000}` al posto di «September 2026».

**Prima → dopo (Inghilterra e Galles, tabella 1.1 e M1.1)**: domande ricevute 160.874 → 175.160; buoni emessi 131.619 → 139.840;
contributi pagati 96.611 → 101.742; pompe di calore pagate 96.185 → 101.313; domande del mese 9.738 (settembre) → 14.286 (ottobre,
record); pagati nel mese 3.332 → 5.138 (settembre rivisto a 3.329). WH:LG: 5.469 case e 11.247 misure (luglio) → 6.803 e 13.972
(ottobre). Solare UK: 2.189.367 impianti, 23.588 MW a ottobre.

**Controllo a mano del 26/11** (xlsx aperto con codice a parte, poi `bus.json`, poi pagina): le 4 righe di 1.1; i 54 mesi di M1.1
per i 4 stati; South West e Wales (1.2A, 1.2B, M1.2 settembre e ottobre); Cornwall e Leeds (Q1.2 e 4 anni di A1.7): tutto uguale.
`verifica.py --browser` 0 errori 0 avvisi; `monetizzazione.py verifica heatpumps` 0 errori.

**Lastmod per pagina (dopo la revisione del 26/11, voto 8,5).** Prima ogni pagina della sitemap prendeva la data di controllo
delle fonti. Ora `dati/lastmod.json` tiene per ogni pagina indicizzabile [data, impronta]: l'impronta è il testo visibile di `<main>`
senza `<p class="asof">` (date di uscita e controllo), senza `<p class="disclaimer">`, senza l'elenco delle fonti
(`<section class="fonti-box">`) e con le date complete sostituite da un segno; menu, piè di pagina e `<head>` non contano. La data si
sposta a oggi solo se l'impronta cambia. Seme da git con `raccolta/lastmod_seme.py` (4 commit di `sito/`; il commit del 25/11 ha
cambiato una sola pagina, quello del 19/11 ne ha cambiate 22). Distribuzione oggi: 12/11 × 196 (195 council e contee con cifre
invariate, privacy), 19/11 × 3 (about, GBIS, costo), 25/11 × 1 (how-we-check), 26/11 × 30 (home, hub, regole, 10 regioni, Scozia,
13 pagine solari, ECO4, WH:LG, contributi solari). `verifica.py` ricalcola l'impronta con codice suo e la confronta con registro e
sitemap. Il seme si lancia una volta sola: non rilanciarlo dopo una generazione con dati nuovi (riporterebbe le impronte a HEAD).
Anche le colonne di 1.2A, 1.2B, Q1.2 e A1.7 ora si cercano dall'intestazione (`colonna()`), con il controllo «pagati totale = somma
delle tecnologie»; `bus.json` è rimasto identico byte per byte.

**Da sapere:** council e contee non cambiano fino all'uscita di gennaio 2027 (dati a dicembre); in `sito/` cambiano comunque quasi
tutte le pagine per date, piè di pagina e riquadri delle regioni. La tabella «Pagine» in cima descrive ancora l'uscita di settembre.
