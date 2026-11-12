# Heat Pump Grants UK – note di lavoro (12/11/2026)

Sito statico in inglese (en-GB) generato da `genera.py` in `sito/`: Boiler Upgrade Scheme (contributi pagati per regione, contea e
council di Inghilterra e Galles, regole ufficiali, costo mediano nazionale e quartili, costo dopo il contributo) e solare (impianti e
potenza per regione e per council del Regno Unito, costo per kW per regione).
Nato da `studio-business/intelaiatura/fronti-2026-11-11-impianti-uk.md` (idea 1) e dal riesame `riesame-2026-11-12-concorrenza.md`
(idea 1 COSTRUIRE); domanda misurata in `volumi-2026-11-12.md` sez. 3.5 (circa 85.000 ricerche al mese, CPC 7-23 £).
Indirizzo previsto: `https://heat-pump-grants-uk.netlify.app` (nome libero il 12/11/2026: curl → 404; costante `URL_SITO` in
`genera.py` e in `verifica.py`). **Il sito Netlify non esiste ancora** (passi in fondo).

## Pagine (313 indicizzabili + 56 noindex + 404)

| Pagina | Contenuto |
|---|---|
| `/` | cosa paga lo schema (5 importi con date), costo mediano luglio-settembre 2026 e quartili prima/dopo 7.500 e 9.000 £, domande per mese (record di settembre 2026), regole in breve, 10 regioni, 12 council con più contributi, solare, 6 FAQ |
| `/eligibility/` | regole con le parole di GOV.UK e Ofgem (chi, quali immobili esclusi, che impianto, come si fa domanda, IVA, cronologia delle modifiche 2023-2026), 8 FAQ |
| `/heat-pump-cost/` | mediana e quartili per trimestre dal 2022, mediana corretta per l'inflazione, costo per fascia di potenza 2025/26 (aria-acqua e geotermica), 3 FAQ |
| `/heat-pump-grants/` | tabella filtrabile dei 318 council, 10 regioni, 21 contee |
| `/heat-pump-grants/<regione>/` (10) | contributi pagati, per 10.000 famiglie (DESNZ), per anno finanziario, domande per mese (12 mesi), impianto sostituito nel 2025/26, tabella dei council, solare della regione |
| `/heat-pump-grants/<contea>/` (21) | come i council, con la tabella dei distretti |
| `/heat-pump-grants/<council>/` (318: 262 indicizzate, 56 noindex) | contributi pagati maggio 2022 - settembre 2026, per anno 2022/23-2025/26, 2026/27 finora (nostro calcolo), per 1.000 famiglie, posizione nella regione, confronto con regione e Inghilterra+Galles, council vicini, costo NAZIONALE dopo il contributo (riquadro "these costs are national, not local"), regole, solare del council (impianti e MW a fine 2025, 2020, per 1.000 famiglie, costo per kW della regione) |
| `/solar-panels/` e `/solar-panels/<regione>/` (12, Scozia e Irlanda del Nord comprese) | impianti e MW a settembre 2026, aggiunti in 12 mesi, costo medio per kW 2025/26 per fascia, impianti nuovi per mese, tabella dei council (fine 2025); 2 FAQ nell'hub |
| `/about/`, `/how-we-check/` (con modulo `corrections`), `/privacy/`, `404.html` | |

**Regola anti-pagine sottili (lezione AdSense):** una pagina council è indicizzata (canonical + sitemap + AdSense) solo con almeno
100 contributi pagati **e** tutti e quattro gli anni pubblicati da DESNZ (non oscurati). Le altre 56 hanno `noindex`, nessuna
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

## Aggiornamento (ogni mese, dopo l'uscita DESNZ del giovedì: prossima 26/11/2026)

1. `python3 heatpumps/raccolta/fonti.py` (scarica le ultime uscite via API GOV.UK, rilegge le frasi delle regole; se una frase manca,
   rileggere la pagina a mano e correggere testi e `cerca`).
2. `python3 heatpumps/raccolta/estrai.py && python3 heatpumps/genera.py && python3 heatpumps/verifica.py --browser` → 0 errori.
3. Le tabelle per council e i costi cambiano solo a gennaio, aprile, luglio e ottobre; domande e totali ogni mese. Il solare per
   council esce a settembre, i costi del solare a maggio.
4. **Entro il 31/3/2027** rileggere le regole: il contributo da 9.000 £ e l'IVA a zero scadono quel giorno (`genera.py` si ferma
   con un errore dopo il 31/3/2027). Se cambia l'anno finanziario (A1.7 con 2026/27), le pagine prendono da sole il nuovo anno.
5. FAQ: ogni tanto `python3 heatpumps/raccolta/domanda.py` e controllare che ogni FAQ abbia ancora la sua ricerca.
6. Pubblicare solo se `sito/` è cambiato (crediti Netlify); poi IndexNow.

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
- Le pagine council hanno testo a modello con numeri propri: soglia di indicizzazione 100 scelta da noi (262 su 318).
- Volumi: l'API dei volumi ha risposto 429 (limite del conto) alle 2 richieste di oggi; usati i volumi misurati il 12/11 nel file citato.
- Il costo del solare usa la base TIC ("official statistics in development"); la base DNC dà cifre per kW più alte.
- Dati solari per council 2025 sottostimati (nota 12 DESNZ); capacità per council comprende i parchi solari.
