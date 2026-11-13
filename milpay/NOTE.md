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
`/how-we-check/` (con modulo delle correzioni Netlify: pagina, messaggio, fonte; nessun campo per nome o email) · `/about/` · `/privacy/`. FAQ: 16, ognuna da una ricerca misurata (`dati/domanda.json`, 18 ricerche seodata).

## Fonti (nessun blocco aggirato: dfas.mil, militarypay.defense.gov, defense.gov, congress.gov, bls.gov rispondono 403)

- Tabelle: Schedule 8 dell'ordine esecutivo 14368 (18/12/2025, Federal Register 90 FR 60521, doc 2025-23844), **solo immagini**.
  `raccolta/tabelle.py` legge ogni cella tre volte: riconoscimento ottico cella per cella a due scale (616/616 uguali) + testo GPO del PDF
  (515 uguali, 0 diverse, 101 illeggibili). Controllo: 374 celle = gennaio 2025 × 1,038 ± 0,15 $ (escluse E-1…E-5 e celle al tetto).
- Tetto O-7…O-10: **18.999,90 $** (cifra della tabella). La nota * stampata dice 18.899,90 $, ma è un refuso dell'ordine: lo Schedule 5 dello stesso
  ordine fissa il livello II a 228.000 $ l'anno (228.000 / 360 al centesimo × 30 = 18.999,90; lo stesso calcolo ridà i tetti 2024 e 2025 e il livello V 2026),
  la tabella si ferma proprio lì e il Department of the Air Force pubblica 18.999,90. Il sito mostra la tabella e dichiara la differenza con la nota;
  non applica più 18.899,90 (lo faceva la prima versione: 32 celle O-8/O-9/O-10 uscivano 100 $ più basse).
- Aprile 2025 (`raccolta/aprile2025.py` → `dati/paga_2025_aprile.json`): tabella di legge in vigore dal 1/4/2025 (Public Law 118-159, sez. 601), testo e non immagini.
  Controllo: 502 celle del 2026 = aprile 2025 × 1,038 ± 0,15 $ su tutte le righe (E-1…E-5 comprese) e 38 celle esattamente al tetto. Spiega anche perché E-1…E-5
  superano il 3,8 % rispetto a gennaio 2025 (pagina storico).
- 2027: il 26/8/2026 il Presidente ha fissato con 37 U.S.C. 1009(e) l'aumento 7,0 / 6,0 / 5,0 % per le Forze armate (House Document 119-189 su govinfo), 3,6 % per gli altri
  servizi in uniforme. Al 13/11/2026 nessuna legge sulla difesa per il 2027 tra le leggi pubblicate (fino a P.L. 119-138): `fonti.py` rilegge l'elenco (API govinfo,
  chiave dimostrativa) e `genera.py` si ferma se ne compare una → riscrivere `/2027-pay-raise/` con la cifra di legge.
- Storico (`raccolta/storico.py`): ordini 2016-2026 (testo dei PDF o lettura ottica), mediana dei rapporti; formula ECI dall'API BLS
  (serie CIU2020000000000A). 2021: solo la cifra della formula (tabelle scansionate non confrontabili); 2017: manca il dato ECI 2015.
- `raccolta/fonti.py` rilegge 21 fonti e le frasi esatte → `dati/fonti.json` (37 U.S.C. 1009 su govinfo, bilancio FY2027 Appendix p. 241, ricerca nel Federal Register).
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
3. Togliere l'host da `NON_ONLINE` in `studio-business/strumenti/indexnow.py` e lanciare l'invio. Moduli Netlify: attivare il rilevamento dei moduli (Forms → Enable form detection) e la notifica email.

## Revisione indipendente del 13/11/2026

Tutte le 616 celle confrontate a occhio con le sei immagini dello Schedule 8 (riscaricate: stesse impronte): 0 differenze. `verifica.py` ora ha controlli che non
dipendono dai dati del costruttore: impronta delle tabelle viste (`TABELLE_VISTE`: se i dati cambiano vanno riguardati), 37 casi letti a mano provati sul JS e sulle
pagine di grado, tetto 18.999,90, modulo senza dati personali e privacy coerente, frasi obbligatorie e vietate nella pagina 2027, titoli e descrizioni unici.
Il modulo di Payroll Tax by State ha ancora il campo email facoltativo con consenso: se la regola è «nessun dato personale nei moduli» va tolto anche lì.
