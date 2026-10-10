# Visa Income Checker – note di lavoro

Costruito il 10/10/2026. Sito statico in inglese, generato da `genera.py` in `sito/` (37 pagine + 404).
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
| `dati/cambi.json` | cambi BCE (scritto da `raccolta/cambi.py`) |
| `dati/affiliati.json` | riquadro affiliati: compare solo quando un URL è compilato |
| `raccolta/cambi.py` | scarica `eurofxref-daily.xml` della BCE; se qualcosa non va non tocca il file |
| `verifica.py` | esempi a mano, confronto JS/Python, link, fonti sotto la cifra, parole vietate |

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

