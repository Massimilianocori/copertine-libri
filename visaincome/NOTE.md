# Visa Income Checker – note di lavoro

Costruito il 10/10/2026. Sito statico in inglese, generato da `genera.py` in `sito/` (37 pagine + 404; dal 15/10/2026 141 pagine con la sezione "Visa refusal rates"; dal 21/10/2026 186 con le 45 pagine "Easiest Schengen visa").
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
| `verifica.py` | esempi a mano, confronto JS/Python, link, fonti sotto la cifra, parole vietate, sezione visti rifiutati (controllo 7; `--offline` salta i link esterni), pagine "easiest" e visti UK studio/lavoro (controllo 8) |
| `raccolta/rifiuti.py` | scarica e legge i file ufficiali sui visti rifiutati (Commissione Europea, Home Office) e scrive `dati/rifiuti.json`; i file grezzi vanno in `raccolta/_grezzi/` (esclusi da git) |
| `dati/rifiuti.json` | dati della sezione "Visa refusal rates" (generato, non modificare a mano) |

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
