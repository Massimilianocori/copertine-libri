# NAICS Code Lookup – note di lavoro (13/11/2026)

Sito statico in inglese (pubblico USA): classificazione NAICS 2022 del Census Bureau con codici 2017 e raccordo SIC 1987. Famiglia 1 di
`studio-business/intelaiatura/fronti-2026-11-12-volumi-prima.md` («naics code» 90.500/mese a 6 $, «naics code lookup» 49.500 a 8 $).
Stesso motore di `ateco/` (genera, verifica, stile, misura dell'indicizzazione). Indirizzo previsto `https://naics-code-lookup.netlify.app`
(libero il 13/11/2026: 404). `URL_SITO` in `genera.py` e `verifica.py` (cambiarle insieme). **Il sito Netlify non esiste ancora.**

## Fonti (dati/fonti.json: URL, data, SHA-256; file grezzi in raccolta/_grezzi, fuori da git)
Census Bureau: codici 2-6 cifre, struttura (indicatori di cambio), descrizioni, indice (20.373 voci), rimandi, tabella dei conteggi;
concordanze 2022↔2017, 2017←2012←2007←2002←1997; **concordanza ufficiale SIC 1987 ↔ NAICS 1997** (in tutte e due le direzioni);
manuale NAICS 2022 (PDF, 25 frasi controllate); IRS, istruzioni Schedule C 2025 (3 frasi). Tutto dominio pubblico.
Le pagine HTML di census.gov rispondono 403 (Cloudflare): non aggirate, si leggono solo i file (200).
Refuso ufficiale gestito: 323120 «Support Activites for Printing» nella concordanza 2022→2017 (si usa il titolo della struttura).

## Controlli su albero e conteggi (`raccolta/estrai.py` si ferma se non tornano)
2.125 codici: 20 settori, 96 sottosettori, 308 gruppi, 689 industrie a 5 cifre, 1.012 a 6 cifre = tabella ufficiale per ogni settore
(anche le 522 «same as 5-digit»). Padri 2→3→4→5→6 (31-33, 44-45, 48-49), stessi codici e titoli in codici/struttura/descrizioni,
indice e concordanze solo verso codici esistenti.

## Pagine (1.446 HTML: 991 indicizzabili, 455 noindex compresa la 404)
`/` ricerca (due JSON: codici+titoli 209 KB, 46 KB compressi, al primo clic; voci dell'indice 913 KB, 188 KB compressi, scaricate solo quando si scrive una parola, mai per un numero; cerca codici 2022, 2017 e SIC; se nessun codice ha tutte le parole mostra quelli che ne hanno di più), 20 settori, come si legge un
codice, 9 FAQ · `/54/` settori · `/541/` sottosettori · `/5415/` gruppi (con i capitoli `#n-54151` delle industrie a 5 cifre con più figli) ·
`/541511/` industrie a 6 cifre (descrizione, esempi, tutte le voci dell'indice, rimandi linkati, codici 2017, SIC, albero, vicini) ·
`/naics-2017-to-2022/` (1.057 codici 2017, ancore `#v-454110`) · `/sic-to-naics/` (1.005 SIC, ancore `#sic-7371`) ·
`/naics-code-for-consulting|construction|cleaning-services/` · `/how-we-check/` (modulo correzioni Netlify Forms: solo pagina, messaggio e fonte, nessuna email né casella, come milpay), `/about/`, `/privacy/`.

**5 cifre:** nessuna pagina propria. 522 hanno un solo figlio (stesso titolo, «See industry description for …»): l'indirizzo è la pagina a
6 cifre. 167 con più figli: capitolo nella pagina del gruppo. **Indicizzazione:** pagina di codice indicizzata con ≥ 120 gruppi di 5 parole
propri e < 55% in comune con la più simile, escludendo le frasi di modello (presenti in ≥ 5% delle pagine). Oggi: 6 cifre 835 sì / 177 no,
4 cifre 74/234 (quasi tutti senza descrizione ufficiale), 3 cifre 55/41, settori 18/2.
**Codici cercati (revisione del 13/11):** una pagina a 6 cifre corta ma con domanda dimostrata resta indicizzata con soglie più basse (≥ 60 gruppi propri, < 65% in comune). «Domanda dimostrata» = il codice è scritto per numero in un suggerimento salvato (`domanda.json`) oppure è in `dati/richieste.json` con il suggerimento che lo giustifica (genera e verifica controllano che il suggerimento esista e che le sue parole siano nei testi ufficiali del codice). Oggi 25 pagine: 812113 nail salon, 811192 car wash, 524210 insurance agency, 484110 trucking, 541213 tax preparation, 541519, 541618, 531311/531312 property management, 541120 notary… Per aggiungerne una: riga in `richieste.json`.
**Rimandi in arrivo:** ogni pagina a 6 cifre mostra anche i rimandi ufficiali di altri codici che la citano («What other industries send to …»); il blocco è marcato `data-ripreso` e non conta come testo proprio nella misura. Le indicizzate tra 120 e 150 hanno mediana 540 parole.

**SIC:** l'unica concordanza ufficiale è SIC 1987 ↔ NAICS 1997. Per il 2022 si seguono le concordanze ufficiali passo per passo. «Diretto»
(702 industrie con SIC: stesso codice e contenuto dal 1997) = riga ufficiale tale e quale; 306 «via catena» = derivazione nostra, detta in pagina («There is no official SIC line for …»). Nelle pagine via catena i SIC sono divisi in due: **principali** (il codice del 1997 è finito tutto in questo codice 2022, oppure aveva lo stesso titolo: 200 pagine) e **parziali**, chiusi in un riquadro con la spiegazione; 106 pagine hanno solo parziali e lo dicono nel titolo («partial match» o «no single equivalent», es. 425120 con 71 righe). La scheda in alto e la tabella SIC → NAICS seguono la stessa regola (prima il codice 2022 con lo stesso titolo del 1997). 4 industrie senza SIC (112130, 481219, 541120, 551114). `naics.json` ha anche `titoli_1997`.

**FAQ:** 20 (aggiunta ecommerce / 454110 nella pagina 2017 → 2022, solo dalla concordanza e dall'indice), ognuna da un suggerimento vero (`dati/domanda.json`, 151 radici gl=us, 13/11/2026), risposte solo da manuale, IRS o dati.
SBA: solo la frase del manuale («NAICS categories do not distinguish between small and large business… SBA develops size standards»),
nessuna soglia. Nessuna conseguenza fiscale: solo dove va il codice nello Schedule C (riga B).

**Volumi:** `api.seodata.dev` il 13/11/2026 rispondeva 429 (quota esaurita, con e senza chiave): 0 ricerche usate. Volumi in `dati/volumi.json`
dal file dei fronti (12/11). Pagine attività solo con volume misurato: consulting 3.600, construction 3.600 + general contractor 1.900, cleaning
services 1.300. Da misurare (autocompletamento le mostra): real estate, restaurant, rental property, holding company, trucking, ecommerce…
Per aggiungerne una: volume in `volumi.json`, voce in `dati/attivita.json`, FAQ in `dati/faq.json`, genera e verifica.

## Controlli (`python3 naics/verifica.py --browser`, 13/11/2026: 0 errori)
Aggiunti dalla revisione indipendente: catena SIC rifatta dai file grezzi per tutti i 1.012 codici (serve `xlrd`) e presentazione principali/parziali; modulo senza dati personali e testo della privacy coerente; codici con domanda dimostrata e soglie basse; peso compresso dei due JSON; le voci dell'indice non si scaricano per una ricerca numerica; tabelle non più larghe dello schermo a 375 px; invio del modulo.
Fonti e frasi; dati riletti con un lettore xlsx proprio (codici, titoli, albero, conteggi, 50 codici a caso contro descrizioni, esempi,
indice, 2017, SIC e pagina); 2.125 codici nella loro pagina/ancora; 20.373 voci dell'indice nelle pagine; tabelle complete; titoli ≤ 65 unici,
descrizioni ≤ 160; canonical = sitemap; noindex senza pubblicità; link e ancore; FAQ JSON-LD = testo visibile; indicizzazione ricalcolata;
testi (niente IA, dati personali, chiavi, consigli, SBA/fisco); monetizzazione; Playwright 375/1280 chiaro/scuro su home, 541511, 5415,
SIC e 2017 (richieste esterne bloccate, 8 ricerche, filtri, tema, niente scorrimento orizzontale né errori JS).

## Aggiornamento (ogni mese)
```
pip install xlrd   # se manca (concordanze .xls)
python3 -I naics/raccolta/fonti.py --rete && python3 -I naics/raccolta/estrai.py
python3 naics/genera.py && python3 naics/verifica.py --browser
```
NAICS 2027: quando il Census pubblica i file, nuovi URL in `fonti.py`, concordanza 2027↔2022 nella catena.

## Monetizzazione
AdSense come gli altri: `naics` in `SITI` di monetizzazione.py e in `adsense_siti`/`_siti_della_rete`; ads.txt; script solo nelle pagine
indicizzate con ≥ 400 parole. **Nessun affiliato.** Possibili: formazione LLC / registered agent (CPC «llc cost» 13 $ dal file dei fronti);
nessuna commissione letta oggi.

## Da fare per pubblicare (Massimiliano)
1. Netlify: Import da GitHub, branch `ccr-b7fd6b9e-n096cr`, Base directory `naics/sito`, Build command vuoto, Publish `.`; nome `naics-code-lookup`.
2. Netlify → Forms: rilevamento acceso (modulo `corrections`), notifica email.
3. Search Console: proprietà `https://naics-code-lookup.netlify.app/`, inviare `sitemap.xml`.
4. Poi togliere l'host da `NON_ONLINE` in `studio-business/strumenti/indexnow.py` e lanciare l'invio.
