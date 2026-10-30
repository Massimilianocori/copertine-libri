# Visa Income Checker – note di lavoro

Costruito il 10/10/2026. Sito statico in inglese, generato da `genera.py` in `sito/` (37 pagine + 404; dal 15/10/2026 141 pagine con la sezione "Visa refusal rates"; dal 21/10/2026 186 con le 45 pagine "Easiest Schengen visa"; dal 28/10/2026 410 con la sezione "Who moved where" e la pagina dei visti UK di famiglia; dal 30/10/2026 411 con la pagina dei visti Schengen a ingressi multipli, poi 492 con la sezione "UK visa English tests": 81 pagine; poi 510 con la sezione "Thailand DTV visa" (17 pagine) e la pagina Irlanda dei britannici (le altre 10 pagine Irlanda c'erano già e ora usano i PPS)).
Indirizzo previsto: `https://visa-income-checker.netlify.app` (costante `URL_SITO` in `genera.py`, unico punto da cambiare).
Corretto il 10/10/2026 dopo la revisione indipendente (vedi "Correzioni dopo la revisione").

## Cosa fa

Per ogni visto mostra il reddito minimo ufficiale del richiedente e di ogni familiare, calcolato dalla base ufficiale
(salario minimo, IPREM, salario medio, soglie di legge), in euro (o nella valuta ufficiale) e convertito nella valuta
scelta con i cambi di riferimento BCE. Calcolatore: paese + visto + categoria + adulti/figli + valuta (+ reddito facoltativo
per il confronto "sopra/sotto la soglia").

## File

| File | A cosa serve |
|---|---|
| `genera.py` | genera tutte le pagine; contiene il motore di calcolo in Python e lo stesso in JS |
| `dati/programmi.json` | indici ufficiali e programmi, con regole, fonti (URL, data del controllo, risposta HTTP) |
| `dati/cambi.json` | cambi BCE di riserva, scritti nelle pagine alla generazione (`raccolta/cambi.py`) |
| `dati/affiliati.json` | riquadro affiliati: compare solo quando un URL è compilato |
| `raccolta/cambi.py` | scarica `eurofxref-daily.xml` della BCE; se qualcosa non va non tocca il file |
| `verifica.py` | esempi a mano, confronto JS/Python, link, fonti sotto la cifra, parole vietate, sezione visti rifiutati (controllo 7; `--offline` salta i link esterni), pagine "easiest" e visti UK studio/lavoro (controllo 8), Australia/Nuova Zelanda/Canada (controllo 11), visti Schengen a ingressi multipli (controllo 15) |
| `raccolta/rifiuti.py` | scarica e legge i file ufficiali sui visti rifiutati (Commissione Europea, Home Office) e scrive `dati/rifiuti.json`; i file grezzi vanno in `raccolta/_grezzi/` (esclusi da git) |
| `dati/rifiuti.json` | dati della sezione "Visa refusal rates" (generato, non modificare a mano); dal 30/10/2026 ogni riga Schengen ha un 8° elemento: visti a ingressi multipli (MEV) rilasciati |
| `raccolta/rifiuti_altri.py` | dal 26/10/2026: scarica e legge i file ufficiali di Australia (Home Affairs), Nuova Zelanda (INZ) e Canada (IRCC) e scrive `dati/rifiuti_altri.json` |
| `dati/rifiuti_altri.json` | dati delle sezioni Australia, Nuova Zelanda e Canada (generato, non modificare a mano) |
| `raccolta/trasferimenti.py` | dal 28/10/2026: scarica Eurostat `migr_resfirst`, IRCC (residenti permanenti per cittadinanza) e legge il file del Home Office già usato da `rifiuti.py`; scrive `dati/trasferimenti.json` |
| `dati/trasferimenti.json` | dati della sezione "Who moved where" (generato, non modificare a mano) |
| `raccolta/selt.py` | dal 30/10/2026: scarica la pagina SELT di GOV.UK e i 4 ODS (centri e test approvati nel Regno Unito e fuori), controlla le frasi delle guide GOV.UK sui livelli e di HC 1691 (B2 dal 26/3/2027); con `--domanda` rifà l'autocompletamento; scrive `dati/selt.json` |
| `dati/selt.json` | dati della sezione "UK visa English tests" con data, impronta (SHA-256 del contenuto) e SHA-256 di ogni file (generato, non modificare a mano) |
| `raccolta/dtv.py` | dal 30/10/2026: rilegge le pagine DTV delle sedi thailandesi, controlla che ogni valore letto a mano (in `LETTURE`) sia ancora scritto nella pagina ufficiale, scrive `dati/dtv.json`; con `--domanda` rifà l'autocompletamento |
| `dati/dtv.json` | sezione "Thailand DTV visa": elenco ufficiale delle 94 sedi, 37 pagine lette (SHA-256 del testo, data di modifica), regola generale, esenzione 30 giorni, domanda, impronta (generato) |
| `raccolta/ppsn.py` | dal 30/10/2026: scarica i due CSV dei PPS assegnati per nazionalità (gov.ie), controlla somme e licenza, scrive `dati/ppsn.json` |
| `dati/ppsn.json` | PPS assegnati alle 12 nazionalità di "Who moved where": per anno dal 2001 e per mese dal 2023, totali, fonti, domanda, impronta (generato) |
| `dati/lastmod.json` | registro scritto da `genera.py`: per ogni URL la data dell'ultima modifica del contenuto e la sua impronta (serve al `lastmod` della sitemap) |

## Cambi automatici

Le pagine leggono `https://raw.githubusercontent.com/Massimilianocori/copertine-libri/ccr-b7fd6b9e-n096cr/italystrikes/dati/cambi-bce.json`
(costante `URL_CAMBI_LIVE` in `genera.py`). Quel file è aggiornato due volte al giorno dal workflow già attivo di Italy Strikes
(`italystrikes/raccolta/raccogli.py` chiama `visaincome/raccolta/cambi.py` con la variabile `CAMBI_FILE`): non serve nessun workflow nuovo.
Se il file è più recente dei cambi scritti nella pagina, le tabelle e il calcolatore si aggiornano; altrimenti restano i cambi della generazione
(`visaincome/dati/cambi.json`, valore di riserva). Aggiornare i cambi non ripubblica il sito su Netlify (la regola `ignore` guarda solo `visaincome/sito`).

## Programmi pubblicati (17) e fonti

| Programma | Regola | Fonte ufficiale (tutte lette il 10/10/2026, HTTP 200) |
|---|---|---|
| Spagna nomadi digitali | 200% SMI = 2.442 € × 14 mensilità = 34.188 €/anno (2.849 € su 12); +75% primo familiare (915,75 × 14); +25% ciascun altro (305,25 × 14) | Consolato di Spagna a Buenos Aires (pagina DNV); Consolato di Spagna ad Hanoi (tabella SMI); UGE FAQ PDF; SMI: BOE RD 126/2026 + SEPE |
| Spagna non lucrativo | 400% IPREM; +100% IPREM per familiare | BOE RD 1155/2024 art. 62; IPREM: BOE Ley 31/2022 DA 90 + SEPE |
| Portogallo D8 | 4 × RMMG = 3.680 €; familiari: nessun importo (la pagina MNE non dice come si combinano con il D8) | vistos.mne.gov.pt (residency, sezione nomadi digitali; means of subsistence, RMMG 2026 = 920 €) |
| Portogallo D7 | 100% RMMG primo adulto, 50% altri adulti, 30% figli | vistos.mne.gov.pt (means of subsistence) |
| Croazia nomadi | 2,5 × salario netto medio anno precedente; +10% per familiare | mup.gov.hr (3.622,50 €); DZS comunicato RAD-2025-1-1/12 (media 2025: 1.449 €) |
| Ungheria White Card | 3.000 € netti/mese; familiari esclusi (eccezione: figlio nato in Ungheria durante il permesso) | oif.gov.hu |
| Italia nomadi | 3 × soglia esenzione ticket (16 milioni di lire) = 24.789,93 €/anno; conta solo il reddito da lavoro, non quello passivo | G.U. n. 79 del 4/4/2024 (PDF); L. 537/1993 art. 8 c. 16 (Normattiva); cambio lira BCE; Consolato d'Italia a Boston |
| Germania Blue Card | 50.700 €; ridotta 45.934,20 € (professioni carenti, laureati da meno di 3 anni, specialisti IT § 18g(2)) | Bundesanzeiger BAnz AT 18.12.2025 B3; service.berlin.de |
| Olanda kennismigrant | 30+: 5.942 €/mese; <30: 4.357; ridotta 3.122 | ind.nl |
| Olanda Blue Card | 5.942 €/mese; ridotta 4.754 | ind.nl |
| Austria Blue Card | 55.678 €/anno (2026) | migration.gv.at |
| Francia Blue Card | 59.373 €/anno | service-public.gouv.fr (verificata dal sito il 1/6/2026) |
| Svezia Blue Card | 53.625 SEK/mese (dal 15/7/2026) | migrationsverket.se |
| Danimarca Pay Limit | 552.000 DKK/anno (2026) | nyidanmark.dk |
| Irlanda Critical Skills | 40.904 €; 36.848 € (neolaureati); 68.911 € (altre professioni) | enterprise.gov.ie |
| UK Skilled Worker | 41.700 £ o going rate se più alto; casi ridotti: almeno 33.400 £ E 70-90% del going rate (100% per l'immigration salary list); dottorato non STEM 37.500 £ E 90%. Nessun verdetto sì/no nel calcolatore | gov.uk (your job; when you can be paid less) |
| UK coniuge/partner | reddito di coppia 29.000 £; proroga regole pre-11/4/2024: 18.600 £ + 3.800 £ primo figlio + 2.400 £ altri, tetto 29.000 £. Nessun verdetto sì/no | gov.uk |

## Scelte di interpretazione (da tenere d'occhio)

1. **Spagna nomadi**: i consolati scrivono l'importo come 200% dello SMI "mensili durante 14 pagas" (Buenos Aires: 2.442 € × 14; Hanoi: 200% = 2.442, 75% = 915,75, 25% = 305,25). Il sito mostra prima questa forma, poi l'equivalente su 12 mesi (2.849 €, stesso totale annuo di 34.188 €). Nel confronto con il reddito servono sia l'importo mensile sia il totale annuo; se ne rispetta uno solo il sito dice "chiedi al consolato".
2. **Portogallo D8, familiari**: nessun importo. La sezione D8 della pagina MNE fissa solo 4 × RMMG; la sezione separata sui familiari al seguito rimanda alla Portaria 1563/2007 senza dire come si somma al D8. La pagina lo spiega.
3. **Italia, familiari**: il decreto rimanda al ricongiungimento (art. 29 TU), che ha un suo test di reddito: non calcoliamo importi per i familiari.
4. **Importi annuali → mensili**: annuo / 12 (in Austria si pagano 14 mensilità: la pagina e il calcolatore lo dicono).
5. **Confronto con il reddito** (calcolatore): regole mensili (HR, HU, PT, NL, SE, ES non lucrativo) confrontate mese per mese; soglie annuali con il totale annuo (reddito mensile × 12, 13 o 14 mensilità, scelta dall'utente); Spagna nomadi: entrambi. Visti UK: nessun verdetto, solo le condizioni (going rate, regole sulle prove).

## Da ricontrollare ogni gennaio (e quando cambia la pagina ufficiale)

- **Spagna**: nuovo SMI (decreto di solito tra gennaio e febbraio, retroattivo al 1/1) → aggiornare `indici.es_smi` (valore = annuo/12) e le fonti. IPREM: cambia solo con una nuova legge di bilancio (oggi 600 € dalla Ley 31/2022 prorogata).
- **Portogallo**: nuovo RMMG dal 1/1 → `indici.pt_rmmg` (fonte: pagina MNE "means of subsistence").
- **Croazia**: il MUP aggiorna l'importo con il nuovo salario netto medio dell'anno precedente (DZS) → `indici.hr_neto` = nuovo importo / 2,5.
- **Germania**: Bekanntmachung BMI sul Bundesanzeiger (dicembre) per l'anno dopo.
- **Olanda**: importi IND dal 1/1.
- **Austria, Danimarca, Irlanda**: importi annuali dal 1/1 (Irlanda quando il Dipartimento li cambia).
- **Svezia**: nuova soglia ogni anno (quest'anno dal 15/7).
- **Francia**: soglia legata al salario medio di riferimento (decreto/arrêté annuale).
- **UK**: cambi di regole (Statement of Changes), di solito in primavera/estate.
- **Ungheria, Italia**: importi fissi; ricontrollare le pagine due volte l'anno.
- **Spagna nomadi**: con il nuovo SMI aggiornare anche le fonti dei consolati (Buenos Aires, Hanoi) se pubblicano il nuovo importo.
- Dopo ogni modifica: `python3 visaincome/genera.py && python3 visaincome/verifica.py` (aggiornare gli esempi e i controlli di contenuto di `verifica.py` e `TEST.md` se cambiano gli indici).

## Esclusi (da verificare) e perché

| Programma | Motivo |
|---|---|
| Grecia nomadi digitali e FIP (persone finanziariamente indipendenti) | migration.gov.gr risponde 404 alle pagine dei programmi; nessuna pagina ufficiale (mfa.gr, gov.gr, et.gr) leggibile con importi e maggiorazioni familiari. Le cifre circolanti (3.500 €, +20% coniuge, +15% figlio) vengono da siti terzi |
| Cipro nomadi | pagine moi.gov.cy 404, migration.gov.cy irraggiungibile |
| Malta Nomad Residence Permit | residencymalta.gov.mt risponde 403 |
| Estonia nomadi | politsei.ee e vm.ee 404; e-resident.gov.ee dice "4.500 € netti" mentre altre fonti dicono lordi: conflitto, non pubblicato |
| Cechia nomadi | pagine mpo.gov.cz / mvcr.cz non trovate; importo 2026 incerto |
| Romania, Lettonia | pagine ufficiali non trovate o 404 |
| Islanda (remote work) | island.is / work.iceland.is rispondono 404 al server |
| Costa Rica | sito Migración 403; testo della legge su SCIJ caricato via JavaScript |
| Brasile | Resolução CNIg 45/2021 non letta su fonte ufficiale (DOU/gov.br 404) |
| Panama, EAU, Thailandia (DTV), Georgia, Turchia | pagine ufficiali non leggibili (404 o solo JavaScript); la DTV thailandese chiede risparmi, non reddito |
| Colombia | regola leggibile (cancilleria.gov.co: 3 o 10 salari minimi), ma in pesos colombiani: la BCE non pubblica il cambio COP, quindi niente conversione ufficiale |
| Messico | ogni consolato applica cifre proprie: nessuna regola nazionale unica |
| Italia residenza elettiva | nessuna soglia ufficiale fissa |
| Norvegia, Finlandia | udi.no e migri.fi rispondono 403 |
| Lussemburgo, Polonia, Lituania | pagine non trovate o senza importi |
| Australia | pagina Home Affairs caricata via JavaScript |

Possibili aggiunte quando le fonti diventano leggibili: Grecia (molto cercata), Cipro, Malta, Estonia, Cechia.

## Per pubblicare (Massimiliano)

1. Netlify → "Add new site" → "Import an existing project" → GitHub → repository `copertine-libri`, branch `ccr-b7fd6b9e-n096cr`,
   **Base directory `visaincome/sito`**, build command vuoto, publish directory `.` (lo legge da `netlify.toml`). Nome del sito: `visa-income-checker`
   (se è preso, scegliere un altro nome e cambiare `URL_SITO` in `genera.py`, poi rigenerare).
2. Search Console: aggiungere la proprietà con l'URL del sito, verificare con il file HTML (metterlo in `visaincome/sito/`: il generatore conserva i file `google*.html`), inviare `sitemap.xml`.
3. Cambi: niente da fare (li aggiorna già il workflow di Italy Strikes, vedi "Cambi automatici").
4. Affiliati: quando arrivano gli URL (assicurazione sanitaria per il visto, Wise o simili, studio legale), inserirli in `dati/affiliati.json` e rigenerare.

## Correzioni dopo la revisione indipendente (10/10/2026)

Revisione in `scratchpad/visaincome/REVISIONE.md`: tutte le 17 cifre principali coincidevano con le fonti; corretti questi punti.
1. UK Skilled Worker: 33.400 £ è una soglia minima con anche il 70-90% del going rate (100% per l'immigration salary list); aggiunta la variante dottorato non STEM 37.500 £; niente verdetto "sopra la soglia" per i visti UK.
2. Spagna nomadi: forma ufficiale dei consolati 2.442 € × 14, con 2.849 € solo come equivalente su 12; SMI indicato come 1.221 € × 14; tolta l'attribuzione a Santiago del Cile e la frase "non 2.762 €".
3. Italia: conta solo il reddito da lavoro (Consolato di Boston).
4. Portogallo D8: tolte le righe familiari (erano una nostra lettura).
5. Calcolatore: scelta 12/13/14 mensilità e confronto sul totale annuo per le soglie annuali (Austria 3.977 × 14 = soglia: ora "sì").
6. UK coniuge: testo GOV.UK sui sussidi (nessuna cifra minima ma mantenimento adeguato senza fondi pubblici); etichetta "Couple (combined income)"; figli con pre-settled status.
7. Pagina 404 con link assoluti e senza canonical.
8. Tabella delle soglie di lavoro senza il visto coniuge; nota sulle cifre olandesi senza indennità di ferie.
9. Altro: "latest ECB rates"; i valori fuori scala nel calcolatore vengono corretti e segnalati; specialisti IT nella soglia ridotta tedesca; regola dell'azienda con almeno un anno (Spagna); eccezione del figlio nato in Ungheria; fonte DZS per la Croazia; conversioni di mese e anno coerenti (l'anno si ricava dal mese convertito, o viceversa).


## Pubblicazione (10/10/2026)
- Online su https://visa-income-checker.netlify.app (Netlify, base `visaincome/sito`). Meta tag Search Console `GOOGLE_VERIFICA` in `genera.py` (non rimuoverlo). Test: al 9/12/2026 servono ≥ 200 impression a settimana.


## Sezione "Visa refusal rates" (approvata da Massimiliano il 15/10/2026, costruita il 15/10/2026)

Pagine (104, tutte in sitemap): `/visa-refusal-rates/` (panoramica, metodo in inglese semplice, tabelle per Stato Schengen e per Paese di domanda, UK in breve),
`/visa-refusal-rates/<paese>/` (74 Paesi con almeno 10.000 domande Schengen nel 2025, esclusi gli Stati Schengen: tasso per ogni Stato Schengen, classifica
"lowest/highest" tra gli Stati con almeno 500 decisioni, tabella per consolato, sezione UK per nazionalità se ci sono almeno 500 decisioni sui visti turistici),
`/visa-refusal-rates/schengen/<stato>/` (28 Stati che trattano visti; il Liechtenstein è rappresentato dalla Svizzera), `/visa-refusal-rates/uk/` (tutte le nazionalità).
Tabelle ordinabili (clic sull'intestazione) e filtrabili; avviso "Statistics, not advice" su ogni pagina; regola ufficiale "si fa domanda al Paese della destinazione principale".
Collegamenti dal resto del sito: menu ("Refusal rates"), piè di pagina, home (sezione con 8 Paesi), pagine dei programmi e dei Paesi (riga in fondo), How it works (punto 7), About (fonti), Privacy (link di affiliazione).

Aggiornare i dati: `python3 visaincome/raccolta/rifiuti.py --nuovo && python3 visaincome/genera.py && python3 visaincome/verifica.py`
(lo script si ferma e non tocca `dati/rifiuti.json` se un controllo fallisce).

| Fonte | URL | Dati | Data |
|---|---|---|---|
| Commissione Europea, DG HOME – pagina con tutti gli anni | https://home-affairs.ec.europa.eu/policies/schengen/visa-policy/short-stay-visas-issued-schengen-countries_en | elenco dei file per anno | pagina aggiornata il 28/5/2026, letta il 15/10/2026 (200) |
| "Visa statistics for consulates 2025" (XLSX, `2025-consulates-schengen-visa-statistics.xlsx`, 512.813 byte) | https://home-affairs.ec.europa.eu/document/download/56816949-e59f-442b-9091-5d03360bf860_en | 1.874 righe Stato × Paese × consolato | scaricato il 15/10/2026 |
| "Visa statistics for consulates 2024" (XLSX, 558.784 byte) | https://home-affairs.ec.europa.eu/document/download/6552447c-1d75-4f7c-bed6-1bd17a5d59f8_en?filename=2024-schengen-visa-statistics-consulates_en.xlsx | 2.035 righe, per il confronto | scaricato il 15/10/2026 |
| Metadati della Commissione (PDF) | https://home-affairs.ec.europa.eu/document/download/b4626219-fa37-4650-8216-0c2bda466c74_en?filename=visa_statistics_-_quality_and_metadata_reporting.pdf | "not issued" = rifiutati + esami interrotti (art. 8(2) Codice dei visti); dati per Paese in cui si fa domanda, non per nazionalità | letto il 15/10/2026 |
| Home Office, "Entry clearance visa applications and outcomes detailed datasets, year ending June 2026" (XLSX, 33 MB) | https://assets.publishing.service.gov.uk/media/6a85c3741b45e4e555421eda/entry-clearance-visa-outcomes-datasets-jun-2026.xlsx | foglio Data_Vis_D02 (nazionalità × gruppo di visto × esito, trimestrale dal 2005): usati gli ultimi 8 trimestri (2024 Q3–2026 Q2) | pubblicato il 27/8/2026, scaricato il 15/10/2026; 2026 Q1-Q2 provvisori |
| Home Office, tabelle di sintesi (ODS), Vis_06 | https://assets.publishing.service.gov.uk/media/6a85c6003d82f78d5c514552/visas-summary-jun-2026-tables.ods | controllo incrociato: le 20 nazionalità di Vis_06 coincidono (concessi e rifiutati) | 15/10/2026 |
| Pagina GOV.UK dei dati (API dei contenuti) | https://www.gov.uk/government/statistical-data-sets/immigration-system-statistics-data-tables | lo script trova lì l'URL del file più recente | aggiornata il 27/8/2026 |
| Commissione, "Applying for a Schengen visa" | https://home-affairs.ec.europa.eu/policies/schengen/visa-policy/applying-schengen-visa_en | dove fare domanda (Paese della destinazione principale, consolato del luogo di residenza), assicurazione medica obbligatoria, motivazione e ricorso | letta il 15/10/2026 (200) |

Formule: Schengen = non rilasciati / (visti uniformi rilasciati compresi MEV + LTV + non rilasciati), la stessa del file (lo script ricalcola ogni riga e la confronta con la colonna ufficiale, poi confronta le somme con i fogli "Totals - Schengen State" e "Totals - third country").
UK = rifiutati / (concessi + rifiutati), come il "grant rate" del Home Office (ritirati e decaduti esclusi).
**USA esclusi**: travel.state.gov risponde 403 / non risolvibile dal nostro server il 15/10/2026; le pagine lo dicono. Da riprovare a ogni aggiornamento (PDF "Adjusted refusal rate – B visas", uno per anno fiscale).
**Importo minimo dell'assicurazione (30.000 €)**: non scritto perché il testo del Codice dei visti su EUR-Lex non è leggibile dal server (risposta 202 vuota); la pagina dice "controlla la copertura minima chiesta dal consolato".

Monetizzazione: riquadro SafetyWing ("Affiliate", `rel="sponsored"`, dicitura completa, nessuna promessa sull'accettazione della polizza) su panoramica, Paesi e Stati,
link in `dati/affiliati.json` alla voce `_safetywing_schengen` (stesso referenceID 26614957 del link già attivo, campagna `visa-refusal-rates` per contare i clic a parte).
EKTA/Travelpayouts resta spento (script con cookie): verifica.py controlla che non compaia.

Revisione indipendente del 15/10/2026: oltre 3.400 cifre ricontrollate con un parser proprio sui file ufficiali (EU 2025/2024, Home Office D02, Vis_06), 0 differenze.
Corretti: nomi dei consolati ("Washington, DC", "Port of Spain", "Rio de Janeiro" invece di "Washington, Dc"...: funzione `nome_consolato`),
"The United States ranks" a metà frase, barre verdi della lista "Lowest" invisibili (la classe `ok` prendeva lo stile del riquadro `.ok`; ora `basso`/`alto`,
con la stessa scala per le due liste), barrette delle tabelle allineate (numero in `.tv` a larghezza fissa).

## Aggiunte del 21/10/2026: "Easiest Schengen visa" e visti UK di studio e lavoro

Motivo: le 32 visite della settimana 14-21/10 erano tutte nella sezione dei rifiuti (Pakistan 6); la gente cerca "easiest schengen visa from pakistan / for indians",
"which schengen country has lowest rejection rate for <nazionalità>" (ricerca del 21/10) e la classifica c'era già dentro le pagine, ma titoli e H1 non lo dicevano.

1. **Pagine per Paese** (`/visa-refusal-rates/<paese>/`): titolo "Schengen visa rejection rate <Paese> 2025: by country, easiest and hardest, plus UK",
   H1 "... Schengen countries (2025), easiest and hardest, and the UK", primo paragrafo e riquadro di sintesi con il Paese Schengen con il tasso più basso e quello con il più alto
   (solo tra gli Stati con almeno 500 decisioni, `SOGLIA_CLASSIFICA`), meta description con "Easiest Schengen visa for <aggettivo> applicants: X (tasso); hardest: Y (tasso)",
   H2 `#easiest` "Easiest Schengen visa from <Paese>: lowest and highest refusal rates" con le due liste (5 più bassi, 3 più alti) e la frase "These rates describe past decisions, not your chances".
   Aggettivi di nazionalità nel dizionario `DEMONIMI` di `genera.py` (il generatore si ferma se manca un Paese con pagina).
2. **Pagine `/visa-refusal-rates/<paese>/easiest-schengen-visa/`** (45, tutte in sitemap, breadcrumb a tre livelli): solo per i Paesi in cui **almeno 8 Stati Schengen hanno deciso
   almeno 500 domande** nell'anno più recente (`SOGLIA_FACILE = 8`: così "5 più bassi" e "3 più alti" non si sovrappongono; 29 Paesi su 74 restano senza pagina separata,
   ad es. Suriname con 1 Stato, Togo con 2). Contenuto: H1 "Easiest Schengen visa from <Paese> (2025): countries with the lowest refusal rate", riquadro con Stato più basso,
   più alto, media del Paese, numero di Stati e consolati classificati; liste "Lowest/Highest"; tabella ordinabile di tutti gli Stati con 500+ decisioni dal tasso più basso
   (con 2024 e variazione in punti); tabella dei consolati con 500+ decisioni dal tasso più basso; 4 domande e risposte (anche in JSON-LD FAQPage); "What easiest means here";
   griglia delle altre 8 pagine "easiest" più vicine per numero di domande. Dati solo da `dati/rifiuti.json`. Collegamenti: dalla pagina madre (riquadro e sezione `#easiest`),
   dalla panoramica (griglia dei 12 Paesi con più domande) e tra le pagine "easiest". Perché pagine separate: la domanda "easiest schengen visa from X" è diversa da
   "rejection rate X" e Google tende a premiare una pagina per intento; il contenuto non è un doppione (classifica completa, consolati classificati, domande).
3. **Regno Unito, visti di studio e lavoro per nazionalità** (idea 4 del 20/10): il file Home Office già usato (`Data_Vis_D02`, gruppi Visitor/Study/Work/Family/Other) aveva
   già studio e lavoro in `dati/rifiuti.json` e nella tabella "Visa type" di ogni pagina; ora stanno anche nel riquadro di sintesi (KPI "study visas refused · N decisions",
   "work visas refused"), nel primo paragrafo UK, nella meta description ("visitor 43.2%, study 19.0%, work 23.4%"), in una tabella trimestrale "Study visas and work visas, quarter by quarter"
   e nella pagina `/uk/` (colonne "Study visas refused / Study decisions / Work visas refused / Work decisions", riquadro con i totali). La sezione UK compare ora quando **uno qualsiasi**
   tra turismo, studio e lavoro ha almeno 500 decisioni (`gruppi_uk_ok`): 8 Paesi in più (Cipro, Hong Kong, Giappone, Kuwait, Oman, Qatar, Arabia Saudita, Singapore), con la cifra
   principale sul gruppo più grande. Gruppi come nel file: "Study" = Sponsored study (Student, Child Student) + Other study (Short-term study); "Work" = Worker (Skilled Worker,
   Health and Care Worker, ...) + Temporary Worker + Investor/business/talent + Other work visas and exemptions. Raccolta: nessuna modifica (`raccolta/rifiuti.py --nuovo` rigenera tutto).
   File ufficiale controllato con curl dal server il 21/10/2026: HTTP 206 (richiesta parziale) per il XLSX, l'API dei contenuti GOV.UK e l'ODS di sintesi; ultimo aggiornamento della pagina 27/8/2026.
   Controllo indipendente sul file grezzo (Pakistan, India, Nigeria, USA: studio e lavoro, 4 trimestri): cifre uguali alle pagine.
4. `verifica.py` controllo 8: numero di pagine "easiest" (≥ 30), sitemap, titolo, frase di cautela, classifica/FAQ/avviso, link dalla pagina madre; per Pakistan, India e Nigeria
   ricalcolo dello Stato più basso e più alto e ordine della tabella; tassi UK di studio e lavoro ricalcolati per Pakistan, India, Nigeria e Giappone (riquadro, tabella, pagina `/uk/`).
   Sito: 186 pagine indicizzabili (141 + 45). Screenshot Playwright 375/1280 px (Pakistan, Pakistan easiest, /uk/, Giappone, panoramica): nessuno scorrimento orizzontale, 0 errori JS.
   Misura (dalla ricerca del 21/10): ≥ 200 impressioni al mese sulle pagine "easiest" a 30 giorni (Search Console, filtro `easiest-schengen-visa`).

Correzioni dopo la revisione indipendente del 21/10/2026 (numeri Schengen e UK ricalcolati da zero: tutti uguali alle pagine):
- `ESENTI_VISTO` in `genera.py`: per i 13 Paesi i cui cittadini non hanno bisogno del visto Schengen o sono cittadini UE (Australia, Canada, Cipro, Georgia, Hong Kong,
  Irlanda, Israele, Giappone, Serbia, Singapore, Emirati, Regno Unito, USA) `demonimo()` scrive "applicants from Ireland" invece di "Irish applicants":
  le domande lì vengono da residenti di altre nazionalità, e "Irish applicants" / "UK applicants" era sbagliato (meta, H2, domande e JSON-LD).
- Titolo e H1 delle pagine per Paese: "easiest first" → "easiest and hardest" (la tabella per Stato resta ordinata per domande, non per tasso: "easiest first" prometteva
  un ordine che non c'è); tolto " (official)" dal titolo per accorciarlo. Nel riquadro di sintesi "(full ranking)" dopo la parentesi del tasso → frase a sé "Full ranking by country and consulate".
- Pagina `/uk/`: con 10 colonne la tabella era larga 1.684 px in un contenitore di 1.026 px (a 1280 px le colonne lavoro e totale restavano fuori schermo senza alcun segnale):
  solo per `#t-uk` intestazioni a capo, celle più strette e barrette nascoste → 1.026 px, tutte le colonne visibili a 1280 px (a 375 px scorre nel contenitore come prima).

### Da ricontrollare (date)
- **26/11/2026** (prossima pubblicazione del Home Office, scritta nel file; la tabella dei contenuti indica anche il 27/10/2026 per i dataset: controllare entrambe le date): rilanciare lo script con `--nuovo` → UK fino a 2026 Q3.
- Poi ogni trimestre (fine febbraio, maggio, agosto, novembre).
- **1/6/2027**: file Schengen dell'anno 2026 (la Commissione pubblica di solito tra aprile e giugno; il 2025 c'era già il 28/5/2026). Lo script prende da solo gli ultimi due anni della pagina.
- A ogni aggiornamento: riprovare la fonte USA e il testo del Codice dei visti su EUR-Lex.

## 23/10/2026 — blocco «Other useful tools for your trip» (link ai siti fratelli)
- In fondo a ogni pagina, nel piè di pagina prima della riga finale, il blocco `.f-altri` (`ALTRI_SITI` e `blocco_altri()` in `genera.py`, stesso modello di EsameB1/EsamiDiStato): titolo piccolo e una riga per sito, 3 link normali (`rel="noopener"`, nessun nofollow) a Italy Strikes Today, Tourist Tax Calculator e Before You Fly (niente Cruise Health Scores: pubblico dei visti, non delle crociere). Scopo: Italy Strikes Today dopo 13 giorni aveva 0 pagine indicizzate e nessun sito nostro lo linkava. Nuovo controllo 9 in `verifica.py` (blocco in tutte le pagine indicizzabili, link uguali a `genera.py` e nell'ordine, mai a questo sito, tutti `noopener`): 186 pagine, 0 errori; `verifica.py` tutto OK. Rigenerate 186 pagine + 404: cambiano solo il blocco, il CSS e il `lastmod` della sitemap. Schermate 375/1280 px, chiaro e scuro, in `scratchpad/link-shot/` (fuori dal repository). Non ancora pubblicato (commit e push da fare).

## IndexNow (26/10/2026)
- IndexNow: file chiave scritto dal generatore; invio con studio-business/strumenti/indexnow.py. Costante `CHIAVE_INDEXNOW` in `genera.py` accanto a `SCRIPT_CONTATORE` (chiave pubblica, uguale in tutti i siti della rete); `extra()` scrive `sito/<chiave>.txt` accanto a `robots.txt`, fuori dalla sitemap e non linkato. Nuovo controllo in `verifica.py` (`controlla_indexnow`): file presente, contenuto = chiave, non citato nella sitemap.

## 26/10/2026 — Australia, Nuova Zelanda e Canada nella sezione dei visti rifiutati

Motivo: la sezione rifiuti ha avuto 62 visite nella settimana 19-26/10, in buona parte rimandate da un assistente conversazionale che cita le tabelle con fonte e data; pubblico Pakistan, Nigeria, India, Filippine, Iran, Tunisia. Fonti dal dossier `studio-business/intelaiatura/idee-2026-10-20.md` (idee 1-3), tutte riscaricate e ricontrollate il 26/10/2026.

**Raccolta**: modulo nuovo `raccolta/rifiuti_altri.py` → `dati/rifiuti_altri.json` (1,2 MB; `rifiuti.py` e `dati/rifiuti.json` non toccati). Uso: `python3 visaincome/raccolta/rifiuti_altri.py --nuovo && python3 visaincome/genera.py && python3 visaincome/verifica.py`. Se un controllo fallisce il JSON non viene toccato. File grezzi in `raccolta/_grezzi/` (au-*, nz-*, ca-*). Serve `pdftotext` (poppler) per i PDF. Riprova da solo se immigration.govt.nz chiude la connessione (succede).

| Fonte | URL | Stato 26/10 | Licenza (attribuzione) | Periodo |
|---|---|---|---|---|
| Home Affairs, BP0015 Student visa grant rates (pivot XLSX; URL dal catalogo `data.gov.au/data/api/3/action/package_show?id=student-visas`, risorsa "grant rates") | `…/bp0015l-student-visa-grant-rates-locked-at-2026-09-30-v100.xlsx` | 200, 21.179.753 byte, Last-Modified 20/10/2026 | CC BY 2.5 AU (catalogo); "cite the Department of Home Affairs as the source", il Dipartimento non risponde delle nostre analisi | 2005-06 → 30/9/2026, 2.085.133 righe, 235 nazionalità, mese, settore, in/fuori Australia, principale/familiare |
| Home Affairs, BR0112 Visitor visa program report 31/12/2025 (PDF, primo link della pagina `homeaffairs.gov.au/research-and-statistics/statistics/visa-statistics/visit`) | `…/research-and-stats/files/visitor-visa-december-2025.pdf` | 200, 1.217.445 byte | CC BY 3.0 AU (pagina "Copyright and disclaimer" del sito; attribuire a "Australian Government Department of Home Affairs") | tabelle 3.02 (Tourist Visitor 600/676) e 3.03 (Sponsored Tourist 600): grant rate per 15 nazionalità, 5 trimestri ott 2024 – dic 2025 |
| Home Affairs, BP0018 Visitor visas granted (pivot XLSX, data.gov.au `visitor-visas-granted-pivot-table`) | `…/bp0018l-visitor-visas-granted-quarterly-report-as-at-2026-09-30-v100.xlsx` | 200, 2.004.978 byte | CC BY 2.5 AU | solo per la soglia (concessioni del trimestre = limite inferiore delle decisioni) e controllo incrociato |
| Immigration New Zealand, "Visitor / Student / Work applications decided" (PDF mensili, pagina `immigration.govt.nz/about-us/research-and-statistics/immigration-statistics/statistics/`) | `…/assets/inz/documents/statistics/statistics-{visitor,student,work}-applications-decided.pdf` | 200 (1,25 / 0,87 / 1,46 MB), preparati l'8/10/2026 | CC BY 3.0 NZ (pagina Copyright; attribuire alla Corona e al sito del Ministero) | anni fiscali 2016/17 → 2025/26 + 2026/27 al 30/9/2026, per nazionalità (passaporto), domande |
| IRCC, Operational Processing – Monthly IRCC Updates (dataset `9b34e712-513f-44e9-babf-9df4f7256550`): TR Processed, TR Approved, SP Processed, TRV V-1 Approved | `ircc.canada.ca/opendata-donneesouvertes/data/Open Data - OPS … en.xlsx` | 200, 64-74 KB, Last-Modified 20/10/2026, "MBR as of September 1, 2026" | Open Government Licence – Canada ("Contains information licensed under the Open Government Licence – Canada") | gennaio 2023 → agosto 2026, per Paese ("source country") e mese, persone |

**Definizioni (scritte sotto ogni tabella)**
- Australia studenti: rifiutati ÷ (concessi + rifiutati), complemento del grant rate del Dipartimento. Cifra principale = **richiedenti principali che fanno domanda fuori dall'Australia**, ultimo anno fiscale completo (2025-26); accanto 2024-25, luglio-settembre 2026, tutti i richiedenti, per settore, mese per mese (12 mesi) e anno per anno (dal 2016-17). Controlli nello script: totale = concessi + rifiutati su ogni riga, righe = recordCount.
- Australia turisti: il PDF dà solo tassi, non decisioni. Si mostra "100% − grant rate" e una nazionalità solo se BP0018 conta ≥ 500 concessioni di quel visto nell'ultimo trimestre (quindi ≥ 500 decisioni): 3.02 tutte le 15; 3.03 solo India, Pakistan, Filippine, Sri Lanka, Cina (Bangladesh 470, Iran 460, Vietnam 437, Nepal 420 concessioni: esclusi e nominati in pagina). Controllo incrociato automatico: Sponsored Tourist luglio-dicembre 2025 nel PDF (tabella 2.04) 19.237 = BP0018 (600, Sponsored Family) 19.237. Il gruppo "Tourist Visitor" del PDF (780.883) ≈ BP0018 Tourist + ADS + Frequent Traveller (780.871): per la soglia si usa solo "Tourist" (limite inferiore sicuro).
- Nuova Zelanda: respinte ÷ (approvate + respinte), domande. Per INZ "declined" **comprende le domande ritirate**: scritto in ogni pagina, non confrontabile con UK/Australia. Controlli: approvate + respinte = totale per ogni anno, somma degli anni = totale generale, somma delle nazionalità = riga Total per ogni anno; nomi su 2 o 3 righe del PDF ricomposti.
- Canada: approvati ÷ esaminati (TR Approved / TR Processed, stesse persone, stesso ambito: visti turistici, visitor records, permessi di studio e lavoro, nuove domande e proroghe; "processed" = approvate, rifiutate e ritirate). Per gli **studenti** c'è solo "esaminate" e per i **turisti** solo "approvati": **nessun tasso** per loro, solo i conteggi, con la spiegazione in pagina. Totali annui = colonna "Total" del file (IRCC la arrotonda dai dati non arrotondati; la somma dei mesi arrotondati differisce di 0-15). "–" = Paese assente dal file V-1 (di solito esente da visto).
- **Soglia** `SOGLIA_ALTRI = 500` decisioni (Canada: domande esaminate) nell'ultimo anno completo; sotto 500 il tasso secondario ha l'asterisco, sotto 100 "–".

**Pagine** (189 indicizzabili, +3):
- `/visa-refusal-rates/australia-visas/` (43 nazionalità con ≥ 500 decisioni 2025-26, tabella ordinabile e filtrabile, settori, 12 mesi, turisti 3.02/3.03, fonti, JSON-LD Dataset CC BY 2.5 AU), `/new-zealand-visas/` (54 nazionalità con ≥ 500 decisioni in almeno un tipo, anni 2016/17-2026/27), `/canada-visas/` (151 Paesi con ≥ 500 esaminate nel 2025). **Non `/australia/` e `/canada/`**: quegli indirizzi sono già le pagine Schengen "domande fatte in Australia / in Canada" (online dal 15/10, in sitemap); ora hanno in testa un riquadro che rimanda alle pagine delle destinazioni, e non mostrano la sezione su sé stesse.
- Pagine per Paese (74): sezioni `#australia` (23 Paesi sopra soglia), `#new-zealand` (25), `#canada` (67), altrimenti una riga "fewer than 500" con il link; riquadro di sintesi con la riga "Australia, New Zealand and Canada · by citizenship" e fonte; titolo "Schengen visa rejection rate {Paese} 2025…, plus UK and Australia" ("and Australia" solo se c'è la sezione australiana; entro 75 caratteri: si tolgono prima "by country", poi "easiest and hardest", mai UK/Australia — revisione 26/10), H1 "…, the UK, Australia, New Zealand and Canada", meta con il tasso australiano.
- Panoramica: sezione `#destinations` con tre schede, metodo e fonti ufficiali aggiornati; pagina `/uk/`: "Other destinations". Bandiere SVG nuove (Australia, Nuova Zelanda, Canada) in `_B`.
- CSS: `.trim.m12` (12 barre, 6 per riga sotto 760 px), `table.larga` (intestazioni a capo, barrette solo nella prima colonna dei tassi: la tabella australiana a 1280 px non esce più dal contenitore).
- `verifica.py`: domini ufficiali nuovi in `URL_UFFICIALI`; controllo 11 (pagine in sitemap con licenza, fonte, avviso, JSON-LD Dataset e breadcrumb; righe della tabella australiana = nazionalità ≥ 500 ricalcolate; cifre AU/NZ/CA di India, Pakistan, Nigeria, Filippine ricalcolate da `rifiuti_altri.json`; rimandi dalle pagine Schengen di Australia e Canada).

**Correzione al dossier del 20/10**: i numeri neozelandesi dell'India erano spostati di un anno (70.197/33.714 è il 2023/24, non il 2024/25; 2025/26 = 66.794/13.876 = 17,2% respinte). Nel PDF non c'è nessuna dicitura di arrotondamento casuale a base 3 (il dossier la citava): non la scriviamo.

**Da ricontrollare**: BP0015 e BP0018 ogni mese (verso il 20); INZ ogni mese (verso l'8); IRCC ogni mese (verso il 20); BR0112 ogni sei mesi (il rapporto al 30/6/2026 non c'era ancora il 26/10: lo script prende il primo PDF della pagina). A luglio cambia l'anno fiscale completo (AU, NZ) e a gennaio l'anno canadese: le pagine si spostano da sole. Riprovare IRCC per un file "Study permits approved" o "TRV refused" per Paese: se esce, si può calcolare un vero tasso.

**Revisione indipendente 26/10/2026**: numeri ricalcolati con parser separati (regex in streaming sulla cache pivot di BP0015, pdftotext per INZ e BR0112, openpyxl per IRCC) su file riscaricati con SHA-256 uguale: India, Nigeria, Filippine, Pakistan, Iran uguali alle pagine e ai riepiloghi. Corretti: titoli oltre 75 caratteri (71 pagine Paese fino a 103, e le 3 pagine di riepilogo), anno spezzato a capo nell'intestazione del riquadro AU/NZ a 375 px, controllo dei link esterni in `verifica.py` che falliva per connessioni chiuse da ircc.canada.ca (ora riprova 4 volte). Titolo della pagina `/uk/` (82 caratteri, precedente) lasciato com'era.


## 28/10/2026 — Sezione "Who moved where" (quanti [nazionalità] si sono trasferiti in [Paese]) e visti UK di famiglia e del partner

Dal rapporto `studio-business/intelaiatura/ricerca-profonda-2026-10-28-assistenti.md` (candidate 1 e 2, sez. 7 sulla citabilità). Non ancora pubblicato: revisione indipendente prima.

### Raccolta
`python3 visaincome/raccolta/trasferimenti.py [--nuovo] && python3 visaincome/genera.py && python3 visaincome/verifica.py`
(se un controllo fallisce `dati/trasferimenti.json` non viene toccato). File grezzi in `raccolta/_grezzi/` (`eurostat-migr_resfirst.json`, `ca-pr-citizenship.csv`, il XLSX del Home Office di `rifiuti.py`).

| Fonte | URL | Stato 28/10/2026 | Licenza | Aggiornamento |
|---|---|---|---|---|
| Eurostat `migr_resfirst`, primi permessi di soggiorno per motivo, durata e cittadinanza (API JSON-stat; una sola richiesta: 12 cittadinanze × UE-27 + 27 Stati + 4 EFTA × 5 motivi × 4 durate × 2019-2025) | `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/migr_resfirst` (pagina: `…/databrowser/view/migr_resfirst/default/table`; definizioni: `…/cache/metadata/en/migr_resval_esms.htm`) | 200; dati aggiornati il 22/10/2026 (campo `updated`) | avviso di copyright Eurostat (`https://ec.europa.eu/eurostat/help/copyright-notice`, 200): riuso libero citando la fonte, CC BY 4.0. La vecchia pagina `about-us/policies/copyright` risponde 404 | **una volta l'anno** (l'anno N esce in autunno dell'anno N+1; metadati: "most of the statistics released by end September"), **più revisioni**: i Paesi correggono gli anni passati e Eurostat aggiorna senza preavviso. Rilanciare lo script con `--nuovo` ogni 2-3 mesi e a fine settembre/ottobre 2027 per l'anno 2026 |
| IRCC, "Canada – Permanent Residents by Country of Citizenship" (CSV a tabulazioni, mensile dal 2015) | `https://www.ircc.canada.ca/opendata-donneesouvertes/data/ODP-PR-Citz.csv` (catalogo `open.canada.ca/data/en/dataset/f7e5498e-0ad8-4417-85c9-9b8aff9b9eda`) | 200, 1.296.015 byte, Last-Modified 21/10/2026, dati fino ad agosto 2026 | Open Government Licence – Canada | mensile (verso il 20) |
| Home Office, entry clearance visa outcomes, foglio Data_Vis_D02 (stesso file di `rifiuti.py`, YE giugno 2026) | vedi sezione "Visa refusal rates" | l'API GOV.UK punta ancora al file del 27/8/2026 (controllato il 28/10) | OGL v3.0 | trimestrale (prossimo 26/11/2026) |

Cittadinanze (12): USA, Regno Unito, Canada, Australia, India, Pakistan, Nigeria, Filippine, Cina, Brasile, Sudafrica, Nuova Zelanda (comprendono le 8 del rapporto). Destinazioni: i 27 Stati UE + Islanda, Liechtenstein, Norvegia, Svizzera (Regno Unito fino al 2019 e Serbia esclusi), più Canada e Regno Unito con le loro misure. **Le tre misure non si sommano mai** e ogni pagina dice cosa conta.

Controlli dello script: per ogni cittadinanza, Paese e anno totale = somma dei 4 motivi; UE-27 = somma dei 27 Stati (82 casi su 82, tutti uguali); durate = totale (eccezione nei dati ufficiali: Liechtenstein 2019, 8 caselle in cui le durate non sommano al totale: lì le durate non si usano, elenco in `fonti.eurostat.durate_scartate`); IRCC: intestazione attesa, 12 mesi per ogni anno 2019-2025, USA 2025 = 7.510 (lettura del rapporto); Home Office: i visti concessi per trimestre e gruppo coincidono con `dati/rifiuti.json` (264 confronti) e il file deve essere lo stesso (SHA-256) usato da `rifiuti.py`. Segni Eurostat salvati e mostrati: `u` poco affidabile (Irlanda, tutti gli anni), `b` interruzione della serie (Portogallo 2025, Spagna 2023, Italia 2022, Grecia 2021...): con `b` sul 2025 la pagina dice che parte della variazione può venire da un cambio di conteggio (Brasiliani in Portogallo: 29.752 → 115.709, +288,9%).

Fonti aggiuntive **non** usate: rinunce alla cittadinanza USA (Federal Register): risponde a un'altra domanda e si conterebbero nomi di persone private; residenti per cittadinanza (`migr_pop1ctz`): ultimo anno vecchio per alcuni Paesi (Francia 2020), possibile aggiunta dopo la prova dei 30 giorni; IRCC permessi temporanei di studio e lavoro per cittadinanza: non richiesti, da valutare.

### Pagine (220, tutte in sitemap)
- `/moved-to/` indice: tabella delle 12 nazionalità (UE 2025, 2024, variazione, EFTA, Canada, UK), metodo, fonti.
- `/moved-to/<nazionalità>/` (12): "How many Americans moved to Europe in 2025?", prima frase con numero UE-27, anno, fonte e data di aggiornamento; variazione sul 2024; primi 3 Paesi; EFTA; Canada e UK a parte; tabella ordinabile dei 27 Stati (2025, 2024, variazione, 4 motivi) con totale; tabella EFTA; serie UE-27 2019-2025 per motivo; riquadro "What this number is, and what it is not"; FAQ (JSON-LD FAQPage) con le parole delle ricerche; JSON-LD Dataset.
- `/moved-to/<nazionalità>/<paese>/` (207): **soglia `SOGLIA_TR = 500`** nel 2025 (primi permessi, nuovi residenti permanenti o visti concessi): sotto 500 il numero resta nella tabella della nazionalità senza pagina propria (meno di 500 ha variazioni annue troppo grandi e una pagina sottile). Contenuto: H1 = domanda; prima frase con numero, anno, fonte e data; variazione; motivi; quota con permesso di 12 mesi o più; riquadro con 2024, variazione, 12+ mesi, posizione tra i Paesi UE; tabella per motivo; serie 2019-2025 in HTML semplice (didascalia nascosta `<caption>`); "what this number is"; FAQ; link alle pagine del sito sullo stesso Paese (soglie di reddito, tassi di rifiuto Schengen, pagine Canada/UK) e sulla nazionalità; altre destinazioni e altre nazionalità. Pagine Canada (IRCC: nuovi residenti permanenti, serie e gennaio-agosto 2026) e UK (Home Office: visti di lavoro, studio e famiglia concessi per anno della decisione, gennaio-giugno 2026 provvisorio).
- Britannici: la serie comincia nel 2021 (fino al 2020 erano cittadini UE); per l'Irlanda pochissimi permessi (Common Travel Area), scritto in pagina.
- Titoli ≤ 70 caratteri con l'anno (`titolo_tr`: "How many X moved to Y in 2025? Official figures", poi forme più corte).
- Collegamenti: home (sezione con 8 nazionalità), piè di pagina ("Who moved where"), le 13 pagine `/country/<paese>/` (blocco "Who moved to <Paese> in 2025"), le pagine dei visti rifiutati di India, Pakistan, Nigeria, Filippine, Cina e Sudafrica. Nessun link di affiliazione nella sezione (verificato da `verifica.py`).

### Visti UK di famiglia e del partner (candidata 2)
`rifiuti.py` leggeva già il gruppo "Family" (verificato: 57.590 concessi, 9.197 rifiutati negli ultimi 4 trimestri = 13,8%, come nel rapporto). Il file ha anche il tipo di visto **"Family: Partner"** (coniugi e partner; il gruppo Family comprende anche figli, altri familiari e ricongiungimento dei rifugiati): ora `rifiuti.py` lo salva come voce in più ("Family: Partner", controllo: mai sopra il gruppo Family) e `dati/rifiuti.json` è stato rigenerato dagli stessi file grezzi (gruppi e fonti identici a prima). Partner, tutte le nazionalità: **7,3%** rifiutati (3.081 su 41.983).
- Pagine per Paese: Family entra in `GRUPPI_UK_PAGINA` (riquadro, prima frase, meta description, tabella trimestrale "Study, work and family visas, quarter by quarter") con la stessa soglia di 500 decisioni; nella tabella "Visa type" riga "of which partner (spouse) visas" solo con almeno 100 decisioni (* sotto 500) e frase sul partner con link.
- Pagina `/uk/`: due riquadri (famiglia, partner), sezione `#family` con le 10 nazionalità con più decisioni; titolo ora "UK visa refusal rate by nationality 2026: visitor, study, work, family" (69 caratteri).
- Pagina nuova `/visa-refusal-rates/uk/family-visas/` ("UK spouse and family visa refusal rate by nationality 2026"): cifra principale sul partner, tabella ordinabile di tutte le nazionalità con almeno 100 decisioni di famiglia (famiglia, anno prima, partner), trimestri, FAQ, link alla soglia di reddito del visto coniuge.

### Sitemap: `lastmod` vero per tutto il sito
Prima ogni URL aveva la data della generazione. Ora `genera.py` calcola un'impronta del contenuto (titolo, descrizione, JSON-LD, `<main>`; non CSS, menu e piè di pagina) e tiene `dati/lastmod.json`: impronta uguale → la data resta; cambiata o pagina nuova → oggi. Alla prima generazione le date delle pagine non cambiate sono state ricavate da git (ultimo commit in cui il contenuto è cambiato): oggi 310 pagine al 28/10 (220 nuove + quelle toccate dalla famiglia UK, home, pagine Paese), le altre tra l'11 e il 26/10. Rigenerare senza cambiamenti non sposta le date. IndexNow: nessuna modifica (`studio-business/strumenti/indexnow.py` legge la sitemap, quindi invia anche le pagine nuove).

### Controlli (`verifica.py`)
- Controllo 8 esteso: tassi di famiglia e partner di Pakistan, India, Nigeria e Bangladesh ricalcolati (riquadro, righe, frase), totali partner/famiglia e riga Pakistan della pagina `family-visas`, sitemap, titolo, FAQ, rimando da `/uk/`.
- Controllo 12 (nuovo): pagine nazionalità × Paese attese ricalcolate da `dati/trasferimenti.json` con la soglia 500 (207, nessuna in più o in meno), tutte in sitemap, titoli ≤ 70 con l'anno, numero principale e data, confronto con il 2024, motivi e serie anno per anno uguali ai dati, righe delle tabelle delle 12 nazionalità e link coerenti con la soglia, fonte ufficiale con data sotto ogni tabella, JSON-LD (Dataset, FAQPage, BreadcrumbList), riquadro "what this number is", niente affiliazioni, nessun link interno rotto, link da home e pagine Paese. Prova al contrario: cambiando a mano 15.810 → 15.811 il controllo segnala l'errore.
- Controllo 13 (nuovo): ogni URL della sitemap ha un `lastmod` valido, non nel futuro, uguale al registro; nessun URL doppio.
- Esito 28/10/2026: TUTTO OK (410 pagine indicizzabili, 0 link interni rotti).

### Ricontrollo dei numeri contro l'API (28/10/2026)
10 valori a caso (seme 20261028) richiesti uno per uno all'API Eurostat e confrontati con `dati/trasferimenti.json`: **10 su 10 uguali** (BR→EL 2019 altro 5; CN→IT 2019 altro 1.057; ZA→ES 2022 totale 456; ZA→FI 2019 lavoro 17; CN→RO 2025 famiglia 234; US→PL 2020 altro 230; CN→PL 2021 studio 1.038; ZA→EE 2025 lavoro 6; AU→ES 2021 altro 68; US→HU 2023 totale 1.418). Altri 5 valori visibili nelle pagine (IN→DE 2025 49.023; PK→IT 25.257; UK→FR 8.235; PH→ES studio 678; US→IE 3.644) uguali tra API, JSON e pagina. Uguali anche ai numeri letti nel rapporto: USA nell'UE-27 80.424 (2024) e 91.615 (2025), Spagna 15.810, Irlanda 3.644, britannici 44.446, indiani 227.577, pakistani 98.329, filippini 71.280; Canada USA 10.640 / 9.325 / 7.510.

### Schermate
Playwright (375 e 1280 px, chiaro e scuro): indice, Americans, Americans → Spain, Indians → UK, British → Canada, `uk/family-visas/`, `/uk/`, Pakistan, `country/spain/`. Nessuno scorrimento orizzontale della pagina, nessuna tabella fuori dallo schermo (a 375 px le tabelle larghe scorrono dentro il loro riquadro, come nel resto del sito), nessun errore JS. Schermate in scratchpad (fuori dal repository).

### Da ricontrollare
- **26/11/2026** (Home Office): `rifiuti.py --nuovo`, poi `trasferimenti.py` (si ferma se il file UK non è lo stesso di `rifiuti.json`).
- Ogni mese verso il 20: `trasferimenti.py --nuovo` per IRCC (anno in corso).
- Ogni 2-3 mesi e **ottobre 2027** (anno 2026): Eurostat. Quando esce il 2026, `ANNI` nello script va portato a `range(2019, 2027)` (o spostato in avanti di un anno).
- Misura del rapporto: a 30 giorni dalla pubblicazione ≥ 150 visite a settimana sulla sezione (GoatCounter, filtro `moved-to`).

### Revisione indipendente del 28/10/2026 (sezione "Who moved where" e visti UK di famiglia)
Numeri ricontrollati con strumenti propri, non con `trasferimenti.py`: 20 celle Eurostat estratte a caso dalle pagine (seme 4242) e richieste una per una all'API, più 8 valori mirati (totali UE-27, segni `b` e `u`, caselle vuote): tutti uguali; IRCC: CSV riscaricato (SHA-256 uguale), somme dei mesi di 6 nazionalità × 8 anni uguali alle pagine; Home Office: XLSX riscaricato (SHA-256 uguale) e letto con un parser separato: visti concessi di 6 nazionalità, tassi famiglia/partner di 6 nazionalità, totali e trimestri tutti uguali. Codici: Regno Unito = `UK` (Eurostat), Cina = `CN` (unico codice del dataset, etichetta "China"; IRCC e Home Office tengono Hong Kong a parte).
Corretti nel generatore:
- Irlanda: "low reliability for 2019–2025" includeva il 2020, che non ha il segno `u` → intervalli veri (`anni_testo`: "2019 and 2021–2025").
- Variazioni minime: "+0.0%" (britannici 44.426 → 44.446) → due decimali sotto 0,05% ("+0.05%").
- "The most common reason was other" → "other reasons", con la spiegazione di Eurostat; "the closest official count of how many moved there" → "the main official indicator".
- IRCC: la nota del catalogo dice "values between 0 and 5 are shown as --" e "nearest multiple of 5" (non "1 to 4"); "IRCC's open data do not say why" → "This IRCC file does not say why"; risposta FAQ sul 2026 con il soggetto.
- Pagina `uk/family-visas/`: prima frase con il numero, il periodo, la fonte e la data; FAQ senza il nesso causale "so it is higher": ora dà il tasso del resto del gruppo famiglia (24,7%).
- Elenchi "Spain, France, Germany" → "Spain, France and Germany"; indice con la risposta numerica nella prima frase; "remunerated activities" nella definizione di "Work".
- 375 px: le tabelle "by reason" (UE) e "by type" (UK) ora stanno nello schermo (classe `.tab.motivi`): 207 pagine controllate, 0 tabelle fuori, 0 scorrimenti orizzontali.

## Monetizzazione: come si attiva (30/10/2026)
- **Dove si scrive:** un solo file per tutta la rete, `studio-business/strumenti/monetizzazione.json` (`adsense_client`, `adsense_siti`, domini di affiliazione ammessi). In una riga: `python3 studio-business/strumenti/monetizzazione.py attiva ca-pub-XXXXXXXXXXXXXXXX visaincome`, poi `python3 visaincome/genera.py`. Il nome del sito nel file è `visaincome` (`SITO_ID` in `genera.py`).
- **Cosa cambia con AdSense acceso:** script ufficiale nel `<head>` di ogni pagina (annunci automatici, nessun blocco manuale), `sito/ads.txt` con `google.com, pub-…, DIRECT, f08c47fec0942fa0`, sezione «Advertising (Google AdSense)» in `privacy.html`; la frase sui cookie diventa «GoatCounter non usa cookie, la pubblicità sì». Prima di pubblicare: in AdSense accendere il messaggio di consenso certificato di Google (Privacy e messaggi, regolamenti europei: UE/SEE, Regno Unito, Svizzera), che la privacy descrive.
- **Link di affiliazione:** `dati/affiliati.json` (campo `url`; SafetyWing delle pagine dei rifiuti: voce `_safetywing_schengen`, di nuovo attiva dal 30/10/2026). Ammessi solo verso i domini di `domini_affiliazione`, con `rel="sponsored noopener"` e la riga di trasparenza (la aggiunge `riquadro_trasparenza()` se manca); con almeno un link la privacy aggiunge la sezione sui link di affiliazione.
- **Come si verifica:** `python3 visaincome/verifica.py --offline` (punto 14; il punto 12 vieta ancora EKTA e Travelpayouts nelle pagine «Who moved where»); controllo comune in `monetizzazione.py` (script e `ads.txt` solo con AdSense acceso, privacy coerente, nessun dominio fuori elenco o bloccato, Amazon.it solo con `tag=`).
- **Con il codice vuoto o il sito fuori elenco l'output non cambia:** il 30/10/2026 `sito/` è stato rigenerato identico byte per byte.

## SafetyWing di nuovo attivo (30/10/2026)
- `dati/affiliati.json`, voce `_safetywing_schengen`: `url` di nuovo compilato (quello che era in `url_sospeso`, campagna `visa-refusal-rates`), `attivo_dal` 2026-10-30, `nota_riattivazione`; `url_sospeso` e `nota_sospensione` tolti. Il controllo in `genera.py` (link SafetyWing né attivo né sospeso) resta valido.
- Riquadro «Travel medical insurance for your application» (`box_assicurazione()`): etichetta «Affiliate», `rel="sponsored noopener"`, riga di trasparenza, e le frasi già presenti «Buying insurance does not change the decision on your visa, and we do not know whether a given consulate accepts a given policy: check before you pay.» (nessuna promessa sul visto). Ritocco: «SafetyWing sells travel medical insurance for travellers and nomads online.» **148 pagine** (sezione Visa refusal rates).
- Privacy `/privacy.html`: con il link attivo compare la sezione comune «Affiliate links» e una riga che nomina SafetyWing («Affiliate links to SafetyWing (travel medical insurance) appear in the box marked “Affiliate” on the visa refusal rate pages. Buying a policy does not change the decision on your visa.»). La frase su SafetyWing del testo senza pubblicità (usato solo con AdSense spento e nessun link) ora compare solo se il link è attivo (`FRASE_SW`), così non torna a essere falsa se il link si spegne.
- Controlli: `python3 visaincome/verifica.py --offline` → «TUTTO OK» (punto 14: AdSense acceso, 148 link di affiliazione in 148 pagine su 411, 0 errori); Playwright a 375 px sulla pagina dei rifiuti degli Emirati: riquadro visibile, nessun errore JS, nessuno scorrimento orizzontale. Nessun commit.

## 30/10/2026 — Visti Schengen a ingressi multipli (MEV) per Stato e per Paese di domanda

Dal rapporto `studio-business/intelaiatura/ricerca-2026-10-28.md` (candidata 3, voto 7) e dalla sez. 7 di `ricerca-profonda-2026-10-28-assistenti.md` (numero, periodo, fonte e data nella prima frase; tabelle in HTML semplice; FAQ con le parole cercate; JSON-LD Dataset). Non ancora pubblicato (nessun commit).

### Dati
- Stesso file della Commissione già usato per i rifiuti ("Visa statistics for consulates" 2025 e 2024, foglio "Data for consulates"), colonne 10 "Multiple entry uniform visas (MEVs) issued" e 11 "Share of MEVs on total number of uniform visas issued". `raccolta/rifiuti.py` ora salva i MEV come **8° elemento di ogni riga** di `dati/rifiuti.json` (gli altri 7 invariati: tutto il resto del JSON è identico a prima, controllato campo per campo; UK, fonti e righe uguali; cambiano solo `generato_il`, `_nota` e il nuovo campo `fonti.schengen_<anno>.mev_anomalie`). Rigenerato dagli stessi file grezzi (SHA-256 invariati; l'API GOV.UK punta ancora al file del 27/8/2026, controllato il 30/10).
- Controlli nuovi dello script: intestazioni delle colonne 10-11; quota MEV ricalcolata = colonna "Share of MEVs" su ogni riga; somme dei MEV per Stato = foglio "Totals - Schengen State" (colonna 3) e per Paese = "Totals - third country" (colonna 4). **Anomalia nel file ufficiale**: 2024, Czech Republic / UKRAINE / LVIV, 2 MEV con 0 visti uniformi rilasciati: si tiene il dato (le somme ufficiali lo comprendono) e si annota in `mev_anomalie`; lo script si ferma se le anomalie sono più di 5.
- **Formula**: quota MEV = MEV rilasciati ÷ visti uniformi rilasciati (MEV compresi), come la colonna del file. LTV esclusi. Il resto dei visti uniformi sono a ingresso singolo o doppio (metadati della Commissione: "single entry, double or multiple entries (MEV)").
- **Soglia `SOGLIA_MEV = 500`** visti uniformi rilasciati (Stato × Paese di domanda) per mostrare uno Stato nel confronto; sotto 500 lo Stato è nominato e basta; la cifra dell'anno prima sotto 500 ha l'asterisco e niente variazione.
- **La durata di validità (1, 3, 5 anni) non è nel file**: ogni pagina lo scrive. Le regole "cascade" restano fuori (fonti 403, vedi rapporto).
- Totali: 2025 **51,7%** (5.303.749 MEV su 10.265.942 visti uniformi, uguale al "Grand Total" del foglio ufficiale 0,5166), 2024 52,2%. Più alto Germania 89,1%, più basso Finlandia 20,6%. India 57,6% (556.870 su 966.529), Pakistan 40,8%, Nigeria 29,3%, Turchia 68,7%, Arabia Saudita 92,5% (uguali al rapporto).

### Pagine
- Nuova `/visa-refusal-rates/multiple-entry-schengen-visa/` (in sitemap): titolo "Multiple-entry Schengen visa: which countries give them most (2025)" (67 caratteri); prima frase con numero, file della Commissione (`2025-consulates-schengen-visa-statistics.xlsx`), data di scaricamento e Stati con la quota più alta e più bassa; riquadro di sintesi; avviso "Statistics, not advice" con le definizioni ufficiali (pagina "Applying for a Schengen visa" riletta il 30/10/2026, HTTP 200: "allowing several visits to the Schengen area for as long as the visa is valid"); tabella dei 28 Stati (quota 2025, 2024, variazione, visti, MEV); tabella dei 74 Paesi di domanda con filtro e Stato con la quota più alta; 9 domande (JSON-LD FAQPage); "What these figures do not say"; griglia dei 10 Paesi con più visti; riquadro assicurazione (già presente in tutta la sezione); fonti con il PDF dei metadati (riletto il 30/10, 200) e la licenza (avviso legale della Commissione, 200: riuso CC BY 4.0 citando la fonte); JSON-LD Dataset e BreadcrumbList.
- **74 pagine per Paese**: riquadro `#multiple-entry` dopo la classifica "easiest" (cifra, 2024, variazione, Stato con la quota più alta e più bassa tra quelli con 500+ visti, media mondiale, link alla pagina riassuntiva, fonte), tabella degli Stati con 500+ visti dalla quota più alta, avviso su cosa significa la quota (MEV ≠ visto lungo; durata non nel file; non una previsione); una riga nel riquadro di sintesi in alto ("Multiple-entry visas: X% … by country") e il link nella riga di fondo.
- Indice della sezione: paragrafo `#multiple-entry` con il totale e il link. Nessuna promessa ("you will get…") e nessun consiglio su dove fare domanda (la regola della destinazione principale è citata).

### Ricerche (autocomplete Google, 30/10/2026, `client=firefox&hl=en`, gl=us/in/pk/ng)
- "multiple entry schengen visa" → requirements, cost, reddit, **for indians**, south africa, **validity**, **meaning**, cost for indians, **germany** (us); in: rules, **switzerland**, **first time**, **vs single entry**; pk: **for pakistani**; ng: from dubai.
- "schengen multiple entry visa" → rules, for indians, cost, validity, requirements, meaning, **5 years**, fees, **from pakistan**.
- "which schengen country gives multiple entry visa" → "… tourist visa", "which schengen countries give multi year tourist visa", "can i get / how to get multiple entry schengen visa", "which schengen country gives tourist visa easily" (uguale nei 4 Paesi).
- "multiple entry schengen visa for" → indians, pakistani, filipino, indonesian, indian citizens, indian passport holders, 5 years, us citizens, tourists.
- "easiest schengen country for multiple entry visa" → nessun suggerimento.
- Le FAQ usano queste parole: which country gives most, meaning, vs single entry, validity / 5 years, first time, requirements (regola del passaporto della Commissione), for Indians, from Pakistan, Germany e Switzerland. Costo e tasse non trattati (nessuna fonte letta).

### Controlli
- `verifica.py` controllo 15 (nuovo, ricalcolo da `dati/rifiuti.json` senza le funzioni di `genera.py`): pagina in sitemap, titolo ≤ 70 con l'anno, prima frase con numero, fonte e data, totale dell'anno prima; tabella per Stato = 28 Stati con valori e ordine giusti; tabella per Paese = Paesi con 10.000+ domande, valori uguali; FAQPage, Dataset, frasi sulla durata e sul visto lungo, nessuna promessa; in ognuna delle 74 pagine per Paese riquadro, link, cifra e righe = Stati con 500+ visti, ordinati; indice con link e totale. Prova al contrario: India 556.870 → 556.871 a mano → il controllo segnala l'errore.
- Esito 30/10/2026: `python3 visaincome/verifica.py` (anche link esterni, 27 controllati) **TUTTO OK**; `python3 studio-business/strumenti/monetizzazione.py verifica visaincome` 0 errori (149 link di affiliazione in 149 pagine su 412).
- **Ricontrollo contro i file originali** (script separato in scratchpad, openpyxl sui XLSX in `raccolta/_grezzi/`, non su `rifiuti.json`; seme 20261030): **10 su 10 uguali** — 2025: Danimarca a Singapore 722/3.728 (19,4%), Spagna a Hong Kong 315/1.961 (16,1%), Polonia in Sudafrica 453/1.208 (37,5%), Austria in Kazakistan 3.172/5.011 (63,3%), Germania in Marocco 6.884/8.835 (77,9%), Austria in Azerbaigian 4.015/4.237 (94,8%), Belgio in Arabia Saudita 927/1.265 (73,3%); 2024 (pagina contro foglio "Schengen totals - visas issued" e colonna "Share of MEVs"): Paesi Bassi 381.805/602.158 (63,4%), Svizzera 408.514/560.493 (72,9%), Francia 917.660/2.549.735 (36,0%).
- Playwright 375 e 1280 px, chiaro e scuro (pagina riassuntiva, India, Pakistan, Suriname con un solo Stato sopra soglia, indice): nessuno scorrimento orizzontale della pagina, nessun errore JS; a 375 px le tabelle scorrono dentro il loro riquadro come nel resto del sito (colonna "Highest share" senza a capo). Schermate in scratchpad (fuori dal repository).

### Da ricontrollare
- **1/6/2027**: con il file 2026 della Commissione (`rifiuti.py --nuovo`) le pagine si aggiornano da sole; ricontrollare l'anomalia MEV > visti e i titoli con l'anno.
- Misura (rapporto): a 30 giorni dalla pubblicazione visite rimandate dagli assistenti conversazionali (GoatCounter, provenienze) e ricerche "multiple entry" in Search Console sulla pagina `multiple-entry-schengen-visa` e sulle ancore `#multiple-entry`.

## 30/10/2026 — Sezione "UK visa English tests (SELT): test centres by city and the 2027 B2 change"

Dal rapporto `studio-business/intelaiatura/ricerca-cloni-esameb1-2026-10-30.md`, sez. 3.2 (voto 7,5 come sezione). Non pubblicata (nessun commit).

### Fonti (tutte GOV.UK, Open Government Licence v3.0; lette il 30/10/2026, HTTP 200)
| Fonte | URL | Cosa |
|---|---|---|
| "Prove your English language abilities with a secure English language test (SELT)" (Home Office) | https://www.gov.uk/guidance/prove-your-english-language-abilities-with-a-secure-english-language-test-selt (API: `/api/content/guidance/...`) | aggiornata il 26/10/2026; fornitori nel Regno Unito (Trinity, IELTS SELT Consortium, LanguageCert, Pearson) e fuori (PSI, IELTS, LanguageCert, Pearson); nomi dei test; 28 giorni; validità 2 anni; tariffe degli intermediari |
| List of approved test centres in the UK (ODS, 7.855 byte) | https://assets.publishing.service.gov.uk/media/6adf1017b62d80a107bc5caf/List_of_approved_test_centres_in_the_UK_from_October_2026_23.10.2026.ods | **84 centri** in 28 città (elenco del 23/10/2026; colonne Provider, Name of TC, Country, Address, City, Availability; tutti "Available") |
| List of approved test centres outside the UK (ODS, 95.191 byte) | https://assets.publishing.service.gov.uk/media/6adf10212263175ac2aca3fd/List_of_approved_test_centres_outside_the_UK_from_October_2026_23.10.2026.ods | **1.312 centri** in 140 Paesi e territori (IELTS 567, PSI 327, LanguageCert 213, Pearson 205) |
| List of approved SELT taken in / outside the UK (ODS) | link sulla stessa pagina (`...Tests_taken_in_the_UK+_5_.ods`, `...outside_the_UK+_1_.ods`) | test per livello CEFR, tipo (2-facet = parlato e ascolto, 4-facet = quattro abilità), voto minimo |
| Guide dei visti, parte "Knowledge of English" | uk-family-visa, english-language, skilled-worker-visa, health-care-worker-visa, student-visa, high-potential-individual-visa, scale-up-worker-visa | A1 primo visto partner/genitore; A2 proroga dopo 2,5 anni; B1 cittadinanza e residenza; B2 Skilled Worker, Health and Care, HPI, Scale-up (B1 per chi aveva il visto prima dell'8/1/2026); Student B2 laurea, B1 sotto |
| **Statement of Changes HC 1691** (5/3/2026, su GOV.UK dal 6/3/2026): nota esplicativa par. 5.60-5.62 e testo delle regole (APP KOLL2-3, APP SF1-2) | https://www.gov.uk/government/publications/statement-of-changes-to-the-immigration-rules-hc-1619-5-march-2026 | **B2 in parlato e ascolto per la residenza (settlement) per le domande dal 26/3/2027** sulle 14 appendici elencate (KoLL, Skilled Worker, Settlement Family Life, Long Residence, Global Talent…); prima di quella data B1. "5.62 These changes will come into force on 26 March 2027." La cittadinanza non è nell'elenco. HC 259 (9/7/2026) e HC 584 (3/9/2026) riletti: nessun cambio a questa data |

Nota (fatto, non interpretazione): negli elenchi dei test approvati letti il 30/10/2026 **non c'è un test B2 di solo parlato e ascolto** (2-facet): tutti i B2 sono a quattro abilità. Le pagine lo dicono. Prezzi: nessuno (non sono negli elenchi ufficiali; GOV.UK dice solo che gli intermediari non devono costare più del sito del fornitore); skillsforenglish.com risponde 403 al server.

### Dati e script
- `python3 visaincome/raccolta/selt.py` → `dati/selt.json` (data, impronta, SHA-256 dei file). Si ferma senza toccare il JSON se: cambiano intestazioni o fornitori, i centri calano di oltre il 30%, PSI compare nel Regno Unito o Trinity all'estero, manca una delle frasi GOV.UK su cui si basano le pagine (livelli, 28 giorni, validità, tariffe) o una frase di HC 1691.
- Normalizzazioni (registrate nel JSON): Paesi "GHANA", "Sri lanka", "morocco" → forma normale; "Guayaquil" → Ecuador; "Cyprus" (un centro a Limassol) → "Cyprus (South)"; città "Newcastle" e "Newcastle Upon Tyne" → Newcastle upon Tyne. Refuso del file dei test "GESE Grace 3" mostrato come "Grade 3" (`nome_test()` in `genera.py`).
- **Aggiornamento: ogni lunedì con la routine**: `python3 visaincome/raccolta/selt.py && python3 visaincome/genera.py && python3 visaincome/verifica.py` (l'elenco dei centri cambia ogni 1-3 settimane; l'URL dell'ODS cambia e lo script lo ritrova dalla pagina). Una volta al mese, o quando compare l'avviso "luoghi nuovi senza dati di domanda": `selt.py --domanda` (circa 10 minuti).

### Domanda (autocompletamento Google, 30/10/2026, `client=firefox&hl=en`)
- Generali (salvate in `selt.json` → `domanda.generali`, gl=uk/in/pk/ng, risultati quasi uguali): "selt test centre" → birmingham, near me, in pakistan, london, manchester, in india, croydon, leeds; "ielts for ukvi" → general training, academic, means, life skills a1/b1, b2, skilled worker visa, cost; "a1 english test for uk spouse visa" → in pakistan, example, questions, in pakistan price, expiry date, validity period, in india, in islamabad (con "in": nigeria, ghana, iran); "b1 english test for citizenship" → online, near me, fee, book, birmingham, manchester, glasgow; "english test for ilr" → cost, b2, near me, validity, 2027, spouse visa; "b2 english test for ilr" → sample, uk, spouse visa, 2027; "selt b2" → test, sample pdf, booking, preparation.
- Per luogo (gl=uk): città con "selt test centre / ielts for ukvi / b1 english test / a1 english test / english test for citizenship <città>"; Paesi con "selt test centre in / a1 english test for uk spouse visa in / ielts life skills / ielts for ukvi <Paese>". Conta come domanda un suggerimento con il nome del luogo e un termine dei test (selt, ukvi, life skills, a1-b2, spouse, citizenship, ilr…), esclusi quelli sul test usato per un altro Paese ("ielts ukvi for canada", "accepted in"). Soglia 1. Risultato: **tutte le 28 città** (Cambridge 22, London 14, Birmingham e Manchester 10; Exeter, Maidstone, Uxbridge 1) e **52 Paesi** (Pakistan 11, Bangladesh e India 4, Albania, Ghana, Marocco, Nepal, Nigeria 2; gli altri 1, quasi sempre "ielts ukvi <Paese>"). 88 Paesi senza domanda: solo nella tabella dell'indice, senza pagina.

### Pagine (81, tutte in sitemap)
- `/uk-english-test/` (titolo "UK visa English test (SELT): levels, test centres and B2 from 2027", 66 caratteri; H1 con il nome della sezione): prima frase con 84 e 1.312 centri, date degli elenchi e B2 dal 26/3/2027; tabella "quale livello per quale visto" con la fonte GOV.UK per riga; sezione sul cambio 2027 con le citazioni di HC 1691; tabella dei test da prenotare per livello (Regno Unito / estero); tabelle delle 28 città e dei 140 Paesi (ordinabili, filtro); come prenotare; FAQ; JSON-LD FAQPage e Dataset.
- `/uk-english-test/<città>/` (28) e `/uk-english-test/<paese>/` (52; slug `cyprus-south`, `united-states`…): prima frase con numero, fornitori, data dell'elenco e fonte; tabella dei centri (fornitore, nome, indirizzo; all'estero anche la città, con filtro sopra 12 righe); Londra rimanda a Croydon, Stratford e Uxbridge e viceversa; riquadro B2 breve; FAQ (per i Paesi: i test A1 dei fornitori presenti).
- Avviso "Not immigration or legal advice" su ogni pagina; nessun prezzo; la lista ufficiale non dice quali test e date offre ogni centro (scritto nelle FAQ).
- Collegamenti: menu a piè di pagina ("UK visa English tests (SELT)"), home (sezione con 6 link), pagine dei visti UK (`link_selt`), How it works (punto 8), privacy (riga su italki).

### Monetizzazione
- AdSense già attivo (annunci automatici). **italki**: voce `_italki_selt` in `dati/affiliati.json` (stesso link di EsameB1 `https://www.italki.com/affshare?ref=af34201678`, dominio `italki.com` già ammesso in `monetizzazione.json`): riquadro «Prepare for the speaking test» (`box_italki()`), etichetta "Affiliate", dopo "How to book" (cioè dopo le informazioni ufficiali), `rel="sponsored noopener"`, riga di trasparenza, nessun prezzo, nessuna promessa sul risultato o sul visto. Con il trattino basso la voce non entra nel riquadro generico `box_affiliati()`. Per spegnerlo: `url` vuoto e rigenerare.

### Controlli
- `verifica.py` controllo 16 (nuovo, ricalcolo da `dati/selt.json`): impronta del JSON; pagine = indice + luoghi con domanda (tutte in sitemap, nessuna in più); titoli ≤ 70; prima frase con numero ricalcolato e data dell'elenco; righe della tabella = centri del luogo (nome e indirizzo); tabelle dell'indice (28 città, 140 Paesi, somme); la data "26 March 2027" solo se `selt.json` contiene la frase di HC 1691; nessun prezzo; avviso, OGL, FAQPage; link di affiliazione solo italki, solo se attivo, `sponsored noopener`, riga di trasparenza, dopo "How to book". Il controllo 6 ("Santiago") ora esclude le pagine SELT (Santiago è una città dell'elenco cileno). Provato con una pagina alterata a mano: gli errori escono.
- Esito 30/10/2026: `python3 visaincome/verifica.py` **TUTTO OK** (492 URL in sitemap, 0 link interni rotti); `python3 studio-business/strumenti/monetizzazione.py verifica visaincome` 0 errori (230 link di affiliazione in 230 pagine su 493).
- Controlli a campione contro gli ODS originali (letti con uno script separato, non con `selt.py`): Glasgow 4 e Leeds 4 centri con tutti i nomi; Nigeria 19 (Lagos 10, Abuja 6), Bangladesh 30 (Dhaka 15, Sylhet 10), India 145: uguali alle pagine.
- Playwright 375 e 1280 px, chiaro e scuro (indice, London, Pakistan, China con 185 righe, Glasgow, Stratford): nessuno scorrimento orizzontale, tabelle dentro lo schermo, nessun errore JS.
- Revisione indipendente 30/10/2026 (fonti riscaricate: 4 ODS, guida SELT, 7 guide dei visti, HC 1691 memorandum e testo delle regole, HC 259 e HC 584): 5 città e 5 Paesi a caso uguali agli ODS (centri, nomi, indirizzi, fornitori); livelli e cambio B2 uguali alle fonti. Corretti: tolto "differ by country / by test and country" dalle FAQ sui prezzi (non nelle fonti); FAQ dell'indice sul riuso del B1 per la residenza: ora dice che sulle rotte di HC 1691 il B1 vale solo per le domande prima del 26/3/2027 (regola KOLL 2.2).

### Da ricontrollare
- Ogni lunedì: `selt.py` (vedi sopra). Se GOV.UK aggiorna le guide (es. nuovo test B2 di parlato e ascolto, o una data diversa per il B2), lo script si ferma: rileggere e aggiornare frasi e testi.
- **26/3/2027**: dal giorno dopo le frasi "before 26 March 2027" diventano storia: rivedere prima frase e tabella dei livelli (B2 come livello attuale per la residenza).
- Misura (rapporto): a 30 giorni dalla pubblicazione ≥ 100 visite a settimana sulla sezione (GoatCounter, filtro `uk-english-test`); clic italki nel pannello italki.



## 30/10/2026 — Thailand DTV visa ambasciata per ambasciata (A) e arrivi in Irlanda per nazionalità con i PPS (B)

Dai rapporti `studio-business/intelaiatura/ricerca-zona-europa-asia-2026-10-30.md` (candidata 1, voto 7,5) e `ricerca-zona-uk-irlanda-2026-10-30.md` (candidata 2, voto 7). Non pubblicato (nessun commit).

### A. Thailand DTV visa (`/thailand-dtv-visa/`)

**Fonti (lette il 30/10/2026, tutte HTTP 200 salvo dove detto)**
- Elenco delle sedi: `https://www.thaiembassy.org/` (Ministero degli Esteri thailandese, dati `__NEXT_DATA__`): **94 sedi** (65 ambasciate, 29 consolati generali; esclusi missioni presso l'ONU/ASEAN e l'ufficio di Taipei). 89 home in HTTP 200; Vienna, Praga, Giacarta, Tokyo, Stoccolma su domini propri non raggiungibili dal server (DNS o certificato).
- Le sedi su `<città>.thaiembassy.org` mettono testo, data di inserimento e **data di modifica** (`date_edit`) nei dati della pagina: lo script li legge da lì. 20 sedi hanno la home solo in thailandese (`/en/index` 404).
- **37 sedi con una pagina DTV trovata** (menu e pagine dei visti, più indirizzi tipici): 20 con il costo scritto nel testo, 18 con una regola sulla residenza; 12 senza né l'uno né l'altra (DTV solo in immagini, in thailandese o testo breve: Phnom Penh, Dubai, Tel Aviv, Canberra, Pretoria, Dhaka, Brunei, Atene, Hanoi, Nanning, Chengdu, Nairobi): in tabella con "Not written on the page". 57 sedi senza pagina DTV trovata: elenco a parte con il link al sito.
- Regola dal **31/8/2026**: annuncio del Department of Consular Affairs del 28/8/2026 (`consular.mfa.go.th/th/content/28-8-69-00`, in thailandese, testo in immagine: si controllano titolo e data), riportato in testo da Mosca ("According to an announcement published by the Department of Consular Affairs … on 28 August 2026") e Osaka ("Proof of permanent residence in the country/territory where the visa application is submitted"; casellario giudiziale; domande prima del 31/8 con le regole vecchie). L'infografica ufficiale (Dubai, Wellington) dice lo stesso.
- Esenzione **30 giorni dal 15/9/2026**: ambasciata a Londra (`/en/page/exemp-visa`, britannici e irlandesi "as well as foreign travellers from many other countries"; due volte per anno solare; 20.000 THB a persona su richiesta; proroga fino a 30 giorni) e a Washington ("Nationals of the following 60 countries and territories…"; l'elenco è un'immagine, non trascritto). New Delhi: esenzione di 30 giorni per gli indiani dal 15/9/2026.
- Assicurazione: **nessuna** delle pagine DTV lette la chiede. Il riquadro SafetyWing lo scrive ("Insurance is not a DTV requirement on the pages we read").

**Costi letti (testo ufficiale, valuta locale)**: Londra £300; Washington, Los Angeles, New York, Chicago 400 USD (per i tre consolati la tabella non stampa la valuta: scritto in pagina); Vientiane 10.000 baht in contanti; Ho Chi Minh 340 USD; Kuala Lumpur RM 1.600 (tabella in MYR); Kota Bharu RM 1.600 (pagina 2024); Singapore 500 SGD; Yangon 400 USD (2024); Helsinki, Budapest, Bucarest, Madrid 350 €; Mosca 350 USD; Cairo 18.000 EGP (2025); Varsavia 1.575 PLN (2024); New Delhi 30.000 INR; Qingdao 2.300 RMB (2025, sito in thailandese). Senza costo nel testo: Roma, Oslo, Hong Kong, Savannakhet, Osaka e le 12 pagine senza dettagli.
**Residenza**: Londra (residenza permanente in UK, Irlanda o territori britannici), Washington e Los Angeles (residenza permanente: visto USA valido o green card; LA anche patente), Vientiane (cittadini laotiani o residenti permanenti), Savannakhet, Ho Chi Minh (**solo TRC o PRC** per gli stranieri: chi è in Vietnam da turista non può chiederlo lì), Singapore (solo cittadini e residenti permanenti), Helsinki (Finlandia/Estonia), Bucarest (Romania/Bulgaria), Roma (Italia, Cipro, Albania, Libia), Madrid (Spagna/Andorra, traduzione nostra dallo spagnolo), Oslo (Norvegia/Islanda), Mosca, Hong Kong (HK o Macao), Osaka (regola generale). **Pagine ferme a prima del 31/8/2026** con la regola vecchia: Budapest ("proof of current location"), Cairo (visto di residenza egiziano), Varsavia ("currently residing in Poland or Ukraine"): la pagina lo dice.

**Script e controlli**: `python3 visaincome/raccolta/dtv.py [--domanda] && python3 visaincome/genera.py && python3 visaincome/verifica.py`. In `LETTURE` ogni valore ha il frammento di testo ufficiale da cui viene; se una pagina cambia e il frammento sparisce, lo script si ferma e non tocca il JSON: rileggere la pagina e aggiornare `LETTURE`. Per ogni pagina si salvano SHA-256 del testo e data di modifica della sede.

**Domanda (autocompletamento, 30/10/2026, `client=firefox&hl=en`, gl=us per 86 ricerche, gl=uk/in/vn per 59; tutte salvate in `dati/dtv.json` → `domanda`)**: "dtv visa from" → vietnam, india, laos, thailand, dubai, bangladesh, malaysia, for indians, for muay thai, for medical treatment; "dtv visa embassy" → london embassy, thai embassy london/singapore/hanoi, uk embassy; per città: london, washington dc, vientiane, hanoi, ho chi minh, kuala lumpur, singapore, jakarta, tokyo, los angeles, berlin, manila, hong kong, taipei, yangon, mumbai (requirements), canberra, chicago, warsaw, ankara, frankfurt, münchen, moscow; per Paese (gl=uk/in/vn): vietnam, laos, malaysia, india, singapore, hong kong, usa, uk, cambodia, myanmar, russia, poland, spain, italy, romania, china, sri lanka. Vuote: phnom penh, new delhi, penang, sydney, new york, savannakhet, seoul, colombo, kathmandu, chennai, kolkata, wellington, ottawa, vancouver, paris, madrid, lisbon, rome, the hague, stockholm, oslo, copenhagen, helsinki, budapest, prague, vienna, athens, doha, abu dhabi, riyadh, cairo, nairobi, pretoria, osaka, egypt, finland, hungary, norway, nepal. Escluso "dtv nomad visa spain" (visto spagnolo).
**Regola delle pagine per sede**: almeno un suggerimento con "dtv" che nomina la città (o il Paese, per l'ambasciata; per il Vietnam va a Ho Chi Minh perché Hanoi pubblica solo immagini) **e** costo o regola sulla residenza letti. **16 pagine**: london, washington-dc, los-angeles, chicago, vientiane, ho-chi-minh-city, kuala-lumpur, singapore, yangon, bucharest, rome, madrid, moscow, warsaw, new-delhi, hong-kong. Con domanda ma senza dati leggibili (nessuna pagina): Hanoi, Dubai, Phnom Penh, Canberra, Dhaka, Giacarta, Tokyo, Berlino, Manila, Taipei.

**Pagine**: indice (titolo "Thailand DTV visa by embassy 2026: fees and residence rules", 59 caratteri): prima frase con 10.000 baht a Vientiane, £300 a Londra, US$400 a Washington, fonte e data; riquadro (37 di 94, 20 con costo, 18 con regola, intervallo in euro €266–€359 ai cambi BCE di riserva); avviso "Not legal or immigration advice" (nessuna promessa: "paying the fee does not mean the visa will be granted"); tabella ordinabile e filtrabile (sede, costo in valuta locale, ≈ euro, regola citata tra virgolette, link ufficiale, data di modifica della sede); cosa è cambiato il 31/8; esenzione 30 giorni; come fare domanda; riquadro SafetyWing; FAQ (JSON-LD FAQPage), Dataset; elenco delle 57 altre sedi. Pagine per sede: prima frase con costo, regola, data di modifica e data di lettura; tabella "What the official page says" con le citazioni e le pagine; regola generale breve; esenzione; altre sedi dello stesso Paese; SafetyWing; FAQ.
**Collegamenti**: pagina dei visti per nomadi (la Thailandia non è più tra i "non coperti": riga con il link), How it works (punto 9 e "Not covered yet"), home (sezione con 6 sedi), piè di pagina ("Thailand DTV visa by embassy").
**Monetizzazione**: AdSense già attivo; SafetyWing nuova voce `_safetywing_dtv` in `dati/affiliati.json` (stesso referenceID 26614957, campagna `thailand-dtv-visa`), riquadro dopo le informazioni ufficiali, `rel="sponsored noopener"`, etichetta "Affiliate", riga di trasparenza; privacy aggiornata ("…and on the Thailand DTV visa pages").
**Non fatto**: visti da pensionato e da nomade di Asia e Golfo (candidata 3 del rapporto): fonti non rilette in questa sessione, restano da fare. Parigi (thaiembassy.fr, altro sistema) ha una pagina DTV in francese senza costo nel testo: non inclusa.

### B. Irlanda: PPS assegnati per nazionalità (`/moved-to/<nazionalità>/ireland/`)

**Fonte**: Department of Social Protection, raccolta gov.ie "Annual Allocations: PPS Numbers" (pagina aggiornata il **21/10/2026**), CSV `20261019_PPSN_registrations_by_year_month_and_country.csv` (mensile, gen 2023 → **set 2026**, 152.210 byte, Last-Modified 21/10/2026) e `20261019_PPSN_registrations_by_year_and_country.csv` (annuale dal 2001, 97.476 byte); scheda data.gov.ie `personal-public-service-number-ppsn-allocations`, **CC BY 4.0**. Il rapporto citava il file del 15/9/2026 (dati ad agosto): è uscito quello di ottobre, usato quello. Definizione e prudenza dalla pagina gov.ie "Get a Personal Public Service (PPS) Number" (aggiornata il 30/1/2026): "helps you access social welfare benefits, public services and information in Ireland" e il servizio è aperto anche a chi risiede all'estero → **PPS assegnati ≠ persone arrivate**, scritto in ogni pagina.
**Script**: `python3 visaincome/raccolta/ppsn.py [--nuovo]` → `dati/ppsn.json`. Controlli: intestazioni, mesi consecutivi, mesi pubblicati per le 12 nazionalità, somma dei mesi = totale annuo (2023-2026), somma annua di tutte le nazionalità = riga "All" del mensile, licenza della scheda, frasi della pagina gov.ie. Nel file annuale il Regno Unito nel 2020 sta in due regioni ("European Union" 4.734 e "Europe excluding EU" 5.360): si sommano (10.094) e la pagina lo dice. Valori " " nel mensile = non pubblicati (piccoli; nessuno per le 12 nazionalità).
**Pagine**: soglia 500 PPS nell'ultimo anno intero (2025) **oppure** 500 primi permessi Eurostat: **11 pagine** (tutte tranne i neozelandesi, 411 PPS e 264 permessi). Le 10 pagine Irlanda Eurostat esistenti ora mettono i PPS al primo posto (titolo "How many Indians moved to Ireland in 2026? PPS numbers by month", prima frase con gennaio-settembre 2026, anno 2025, data del file e confronto con gli stessi mesi del 2025), poi le tabelle mese per mese (2023-2026) e anno per anno (2001-2026, quota sul totale), poi i primi permessi Eurostat come misura separata ("never add the two together"); nuova pagina `british/ireland/` (5 permessi Eurostat nel 2025: lì si spiega la Common Travel Area). Hub delle 12 nazionalità: riquadro "Ireland: PPS numbers by month" (con link se la pagina esiste) e domanda FAQ; indice `/moved-to/`: colonna "Ireland PPS 2025" e sezione `#ireland`; pagina Paese Irlanda: griglia ordinata per PPS.
Esempi: India 9.437 (gen-set 2026, −44,5% sugli stessi mesi del 2025) e 22.684 (2025); Brasile 11.287 e 13.188; Regno Unito 9.981 (+7,7%) e 12.634; USA 4.016 e 5.610.
**Domanda (autocompletamento gl=ie, uguale con gl=in, 30/10/2026; salvata in `raccolta/ppsn.py` e in `dati/ppsn.json`)**: "how many indians in ireland" → 2026, percentage, 2025, 2025 statistics, today, live in ireland 2025; "how many brazilians in ireland" → 2026, 2025; "how many pakistanis in ireland" → pakistani in ireland 2025/2026; "how many nigerians in ireland" → 2026, 2025; "how many filipinos in ireland" → 2026, 2025, 2024, working; "how many chinese in ireland" → 2025, students; "how many americans in ireland" → us citizens, live in ireland 2025, work; "how many british in ireland" → brits, live, citizens; "how many south africans in ireland" → live; "indians in ireland" → population, 2026, percentage, number.

### Controlli (`verifica.py`)
- Controllo 12 aggiornato: pagine Irlanda attese anche con i PPS; titolo con l'anno dei PPS; i numeri delle pagine Irlanda si controllano nel 17. Controllo 6: escluse anche le pagine DTV (nominano l'ambasciata di Santiago del Cile).
- **Controllo 17 (PPS)**: impronta, pagine attese, prima frase (anno in corso, anno intero, data gov.ie, confronto con gli stessi mesi), tabelle mese per mese e anno per anno, riquadro "what this number is" con le frasi gov.ie, cifra Eurostat, blocco dell'hub, colonna e sezione dell'indice; **10 valori a caso** (seme 20261030) riletti dai CSV ufficiali con un lettore proprio: 10/10 uguali (US 2019 4.030; PK 2023-01 225; UK 2008 19.054; PH 2025-03 296; BR 2024-05 1.131; US 2026-03 351; CN 2004 3.511; ZA 2013 339; NZ 2025-11 34; CA 2014 839).
- **Controllo 18 (DTV)**: impronta, pagine attese (indice + 16), sitemap, titoli ≤ 70, prima frase con data, righe della tabella = 37 sedi con costo, regola e link, frammenti citati, avviso, nessuna promessa sull'approvazione, SafetyWing solo dopo le informazioni ufficiali con `sponsored noopener`, trasparenza e frase "non richiesta", link dal resto del sito; online **10 frammenti a caso** riletti sulle pagine ufficiali: 10/10 presenti.
- Prova al contrario: £300 → £301 nella pagina di Londra e 2.379 → 2.380 nella pagina degli indiani: i controlli 17 e 18 segnalano gli errori.
- Esito 30/10/2026: `python3 visaincome/verifica.py` (online) **TUTTO OK** (510 URL in sitemap, 511 pagine, 0 link interni rotti); `python3 studio-business/strumenti/monetizzazione.py verifica visaincome` 0 errori (247 link di affiliazione in 247 pagine su 511).
- Controllo a campione con curl, fuori dagli script: Londra "Visa Fee: £300", Vientiane "10,000 Baht", Washington "400 USD", Ho Chi Minh "340 USD", Singapore "500 SGD" (tutte HTTP 200); India gen-set 2026 = 9.437 e Brasile 2025 = 13.188 dai CSV grezzi.
- Playwright 375 e 1280 px, chiaro e scuro (indice DTV, Londra, Ho Chi Minh, Madrid, Kuala Lumpur, indiani e britannici in Irlanda, hub indiani, indice moved-to, pagina dei nomadi): nessuno scorrimento orizzontale, nessun errore JS. Schermate in scratchpad.

### Da ricontrollare
- **DTV, ogni settimana**: `raccolta/dtv.py` (se una sede cambia pagina lo script si ferma: rileggere e aggiornare `LETTURE`). Una volta al mese `--domanda`. Riprovare Hanoi, Dubai, Phnom Penh, Canberra (domanda senza dati), i siti su altri domini (Tokyo, Giacarta, Berlino, Parigi) e la lista delle 60 nazionalità dell'esenzione (oggi solo in immagine).
- **PPS, ogni mese verso il 20**: `raccolta/ppsn.py --nuovo` (il nome del CSV cambia: lo script lo ritrova sulla pagina gov.ie). A gennaio 2027 il 2026 diventa l'anno intero e le pagine si spostano da sole.
- Misura (rapporti): DTV ≥ 150 visite a settimana e ≥ 2% di clic sul riquadro SafetyWing a 30 giorni (filtro `thailand-dtv-visa`, campagna `thailand-dtv-visa`); Irlanda: impressioni su "how many <nazionalità> in ireland" in Search Console.
- Il link nel piè di pagina cambia il file di tutte le pagine (496 file in `sito/`), ma non il `lastmod` delle pagine non toccate: l'impronta guarda solo titolo, descrizione, JSON-LD e `<main>`.

### Revisione indipendente (30/10/2026, sera)
- Riletti online (fonti scaricate a parte, testo da `__NEXT_DATA__`): 19 sedi DTV (le 16 con pagina + Budapest, Cairo, Qingdao): costo, valuta, regola e data di modifica uguali alla pagina ufficiale; nessuna delle 37 pagine DTV lette (44 URL) nomina un'assicurazione; annuncio MFA del 28/8/2026 solo titolo + immagine (pagine prudenti: "as reported by" Mosca e Osaka; infografica di Dubai coerente); esenzione 30 giorni: l'elenco dei 60 Paesi di Washington è un'immagine (USA, UK e Irlanda presenti); cambi BCE del 9/10/2026 verificati sul file storico BCE. PPS: 15 valori a caso + le prime frasi di tutte le 11 pagine ricalcolate dai CSV ufficiali (SHA-256 uguali): tutti giusti.
- Corretti in `genera.py`: prima frase delle sedi senza costo (Roma, Hong Kong: frase rotta); Yangon e Chicago dicono che la pagina è ferma a prima del 31/8/2026; data della pagina del costo quando è più vecchia (Vientiane 2024, Madrid 2024, Kuala Lumpur 7/2026); "the United States/Kingdom" nelle FAQ e in "Other Thai missions in"; FAQ di Varsavia e Madrid; FAQ sul saldo; indice: le pagine prima del 31/8 "may be out of date" solo se non citano la regola nuova; riquadro SafetyWing senza la frase non documentata sulle spese mediche; pagina Paese Irlanda: non più "How many people … moved" con i PPS e niente "plus" con Eurostat; britannici in Irlanda: Common Travel Area con fonte (Immigration Service Delivery, "Irish and British citizens can travel freely").
