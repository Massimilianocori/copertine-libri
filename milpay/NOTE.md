# Military Pay Chart (milpay) – note di lavoro

Costruito il 13/11/2026 (fronte A, passo 1, di `studio-business/intelaiatura/fronti-2026-11-13-nuovi-radar.md`). Sito statico in
inglese (USA) generato da `genera.py` in `sito/`: tabelle ufficiali 2026 della paga base mensile dei militari USA.
Indirizzo previsto: **`https://military-pay-chart.netlify.app`** (nome libero il 13/11: curl → 404; costante `URL_SITO` in `genera.py`).
**Il sito Netlify non esiste ancora.** Pubblicità: AdSense acceso (`monetizzazione.json`), contatore GoatCounter. Indennità di alloggio
(BAH, passo 2): NON c'è e il sito non la nomina né la promette.

## Pagine (33 indicizzabili + /o-9/ noindex + 404)

`/` tabella completa (4 tabelle, 616 celle) · `/calculator/` (grado + anzianità → mese, anno ×12, tetto, prossimo scatto; niente pensione:
nessuna formula ufficiale leggibile) · 27 pagine di grado `/e-1/` … `/o-10/`, `/o-1e/` … `/o-3e/` (O-9 noindex: riga identica a O-10) ·
`/pay-raise-history/` · `/2027-pay-raise/` (formula 3,6 %, proposta 7/6/5 % del bilancio FY2027, tabella 2027 non ancora pubblicata, con data) ·
`/how-we-check/` (con modulo contatti/correzioni Netlify) · `/about/` · `/privacy/`. FAQ: 16, ognuna da una ricerca misurata (`dati/domanda.json`, 18 ricerche seodata).

## Fonti (nessun blocco aggirato: dfas.mil, militarypay.defense.gov, defense.gov, congress.gov, bls.gov rispondono 403)

- Tabelle: Schedule 8 dell'ordine esecutivo 14368 (18/12/2025, Federal Register 90 FR 60521, doc 2025-23844), **solo immagini**.
  `raccolta/tabelle.py` legge ogni cella tre volte: riconoscimento ottico cella per cella a due scale (616/616 uguali) + testo GPO del PDF
  (515 uguali, 0 diverse, 101 illeggibili). Controllo: 374 celle = gennaio 2025 × 1,038 ± 0,15 $ (escluse E-1…E-5 e celle al tetto).
- Nota: la tabella stampa 18.999,90 $ per O-9/O-10 (e O-8 da 22 anni) ma il tetto in nota è 18.899,90 $: il sito mostra la tabella e applica il tetto.
- Storico (`raccolta/storico.py`): ordini 2016-2026 (testo dei PDF o lettura ottica), mediana dei rapporti; formula ECI dall'API BLS
  (serie CIU2020000000000A). 2021: solo la cifra della formula (tabelle scansionate non confrontabili); 2017: manca il dato ECI 2015.
- `raccolta/fonti.py` rilegge 15 fonti e le frasi esatte → `dati/fonti.json` (37 U.S.C. 1009 su govinfo, bilancio FY2027 Appendix p. 241, ricerca nel Federal Register).
  L'API BLS ha un limite giornaliero senza chiave: se risponde "REQUEST_NOT_PROCESSED" si riprova il giorno dopo (i valori restano in `storico.json`).

## Aggiornare quando escono le tabelle 2027 (fine dicembre 2026)

1. Trovare il nuovo ordine: `curl "https://www.federalregister.gov/api/v1/documents.json?conditions[term]=%22Adjustments%20of%20Certain%20Rates%20of%20Pay%22&conditions[type][]=PRESDOCU&order=newest&per_page=1"`.
2. In `raccolta/tabelle.py` aggiungere `2027` in `ANNI` (numero del documento e id delle 6 immagini dello Schedule 8: guardarle, la disposizione può cambiare);
   in `raccolta/storico.py` aggiungere `2027: "<documento>"` a `ORDINI`.
3. `python3 milpay/raccolta/tabelle.py 2027 2026` → deve finire senza disaccordi. In `genera.py`: `P = paga_2027.json`, `P25 = paga_2026.json`,
   il fattore del controllo (1,038 → aumento 2027) e le righe escluse; le posizioni in `controlla_faq_grado`; la pagina `/2027-pay-raise/` va
   riscritta (diventa storia) e ne serve una per il 2028. `genera.py` si ferma da solo se trova un ordine nuovo nel Federal Register.
4. `python3 milpay/raccolta/storico.py && python3 milpay/raccolta/fonti.py && python3 milpay/genera.py && python3 milpay/verifica.py --browser` → 0 errori.

## Pubblicare (passi del titolare)

1. Netlify: nuovo sito dal repository, Base directory `milpay/sito`, Build command vuoto, Publish directory `.`, nome `military-pay-chart`.
2. Search Console: proprietà `https://military-pay-chart.netlify.app/` (meta di verifica già nelle pagine), inviare la sitemap.
3. Togliere l'host da `NON_ONLINE` in `studio-business/strumenti/indexnow.py` e lanciare l'invio. Moduli Netlify: attivare la notifica email.
