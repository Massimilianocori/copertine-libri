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

## Sezione per diem e rimborso chilometrico (13/11/2026, NON ancora pubblicata: revisione indipendente e commit il 14/11)

Coda: riga milpay di `studio-business/DA-PUBBLICARE.md` (famiglia 2 di `fronti-2026-11-13-scoperta-volumi.md`). 76 pagine nuove (109 indicizzabili in tutto):
`/per-diem/` (ricerca per città/contea/Stato, tariffa standard, come funziona con frasi GSA citate, tabella M&IE, nota su OCONUS/JTR), 49 pagine Stato
`/per-diem/<stato>/` (48 Stati contigui + DC; FY2027 e FY2026 mese per mese, calcolatore con le località dello Stato), 24 pagine di località solo dove la domanda
misurata è ≥ 300 ricerche al mese (`LOC_PAGINE` in `sezione_perdiem.py`; Washington DC 4.400, San Diego 1.900 … Houston 320; Norfolk 390 escluso: non è un'area GSA),
`/per-diem/calculator/` (località + date → alloggio massimo per notte del mese + M&IE con 75 % il primo e l'ultimo giorno; formula scritta sotto), `/irs-mileage-rate/`
(IRS 2026 in due periodi: 72,5 ¢ fino al 30/6, 76 ¢ dal 1/7 per Announcement 2026-11; medico/trasloco 20,5 → 23,5; beneficenza 14; storico 2023-2025; tariffe GSA per i
viaggi federali; calcolatore delle miglia in interi). Menu (Per diem, Mileage rate), piè di pagina e un paragrafo in home. Codice: `sezione_perdiem.py` (chiamato da `genera.py`),
JS in `stile.APP_JS` (`viaggio`, `miglia`), raccolta in `raccolta/perdiem.py`.

- **Dati** (`raccolta/perdiem.py` → `dati/perdiem.json`; file grezzi in `dati/grezzi/`, URL, data e SHA-256 in `dati/fonti.json` chiave `grezzi`): GSA xlsx FY2026
  (649 righe, 296 aree, standard 110 $ + 68 $) e FY2027 (641 righe, 295 aree, standard 113 $ + 68 $); API GSA (DEMO_KEY) alloggio mese per mese e tabella M&IE:
  **tutte le aree uguali mese per mese all'xlsx** (l'API ripete Washington DC sotto MD e VA, stessi valori); IRS Notice 2026-10 (PDF), IRB 2026-29 (Announcement 2026-11),
  pagina IRS dello storico, pagina GSA delle miglia. Tra FY2026 e FY2027: Oak Brook Terrace → Oakbrook Terrace (stesse contee, unite), Allentown/Easton/Bethlehem tolta.
- **Fonti con frasi** (`raccolta/fonti.py`, nuova opzione `--solo=id1,id2` che rilegge solo quelle fonti e conserva le altre e il registro `grezzi`): gsa_pd, gsa_faq, gsa_mie
  (anche le 5 righe della tabella M&IE), gsa_api, gsa_mileage, irs_n2026_10, irs_a2026_11, irs_smr, irs_ir2025_128, gsa_xlsx2026/2027 (impronta = file grezzo).
- **Controlli**: `genera.py` si ferma se un file grezzo cambia impronta, se cambiano i conteggi, se xlsx riletto ≠ perdiem.json, xlsx ≠ API, M&IE fuori dai 5 livelli,
  alloggio sotto lo standard, frase GSA/IRS mancante, pagina di località sotto 300 ricerche. `verifica.py` (lettura indipendente dell'xlsx): 8.259 celle pubblicate = file
  grezzi; dati dei calcolatori in 74 pagine = grezzo; JS = Python su 547 viaggi (passaggio del 1/10/2026, giorno singolo, errori, rinomina) e 305 casi di miglia; casi a mano
  (standard, attraversamento FY, New York 30/12/2026–2/1/2027); 130 citazioni tra virgolette ritrovate alla lettera nelle frasi delle fonti; avviso di non affiliazione GSA/IRS/DoD.
  Playwright (script in scratchpad, non nel repository): indice, calcolatore, San Diego, miglia, Texas a 375 e 1280 px, chiaro e scuro, nessuno scorrimento orizzontale,
  calcolatore e ricerca provati, richieste esterne bloccate.
- **Non coperto e detto in pagina**: Alaska, Hawaii, territori (DoD) ed estero (State) per frase GSA; travel.dod.mil risponde 403 → JTR e OCONUS militari non verificati.
  Niente tassazione delle diarie (nessuna fonte ufficiale letta). Tariffe IRS 2027 non ancora uscite al 13/11 (di solito a fine dicembre: aggiornare `/irs-mileage-rate/`).
- **Domanda**: `dati/domanda_perdiem.json`, 127 ricerche seodata del 13/11 (volumi medi recenti: le frasi con "2026/2027" risultano ancora a 0). FAQ solo da queste.
- **Aggiornare**: a metà agosto 2027 esce FY2028 → aggiungere il file in `raccolta/perdiem.py` (FILE, ATTESI), `FYS` e i testi in `sezione_perdiem.py`; a fine dicembre 2026
  le miglia IRS 2027. Poi `python3 milpay/raccolta/perdiem.py && python3 milpay/raccolta/fonti.py --solo=... && python3 milpay/genera.py && python3 milpay/verifica.py --browser`.

### Revisione indipendente della sezione per diem (13/11/2026, prima della pubblicazione)

File GSA e IRS riscaricati (stesse impronte SHA-256 dei file in `dati/grezzi/`), xlsx riletto dall'XML senza la libreria del costruttore: 9.533 celle pubblicate
(Stati e 24 località) = file grezzi, 0 differenze; xlsx = API GSA per tutte le 296 e 295 aree; 26 viaggi calcolati a parte (passaggio 30/9–1/10, cambio di mese e di anno,
giorno singolo, 75 %) = JS del sito; 25 citazioni distinte ritrovate alla lettera nelle pagine ufficiali riscaricate; Notice 2026-10 e Announcement 2026-11 letti parola per parola
(72,5 → 76 ¢ e 20,5 → 23,5 ¢ dal 1/7/2026, beneficenza 14 ¢); pagina IRS senza tariffe 2027 al 13/11. Correzioni:
- **Area di Washington DC in Maryland e Virginia** (errore vero): GSA mette nell'area "District of Columbia" Montgomery e Prince George's (MD) e Alexandria, Falls Church, Fairfax,
  Arlington (VA), ma le due pagine di Stato dicevano «i luoghi non elencati hanno la tariffa standard» (113 $ invece di 192–295 $). Ora riga «Washington, DC area» nelle due tabelle,
  paragrafo, cifre chiave, FAQ, descrizione e voce nel calcolatore (anche in quello generale, sotto Maryland e Virginia). Costanti `DC_*` in `sezione_perdiem.py`; `controlla()` si ferma
  se GSA cambia la definizione o se un'altra area nomina un altro Stato; `verifica.py` (`DC_FUORI`) controlla riga, valori e testo nelle due pagine.
- Tolta la frase «Military members and DoD civilians travel under the Joint Travel Regulations» (nessuna fonte letta: travel.dod.mil dà 403); ora la nota dice solo che non abbiamo
  potuto leggere il JTR e che il sito non spiega la diaria dei militari. `verifica.py` vieta la frase vecchia.
- Descrizione di `/per-diem/` portata sotto i 160 caratteri.

## Sezione VA disability (15/11/2026, NON ancora pubblicata: serve la revisione indipendente, poi il commit)

Idea B di `studio-business/intelaiatura/fronti-2026-11-14-sera-regole-2027.md` (online entro il 28/11/2026). 13 pagine nuove (122 indicizzabili in tutto):
`/va-disability-rates/` (tabelle ufficiali in vigore dal 1/12/2025, che il VA chiama «2026»: 10 gradi, 12 situazioni familiari × 8 gradi, 3 importi aggiunti; confronto con il 2025;
come si leggono con le frasi del VA; calcolatore), 10 pagine di grado `/va-disability-rates/<n>-percent/` (tutte con ricerca misurata ≥ 300 al mese, `GRADO_RICERCA`),
`/va-disability-calculator/` (grado combinato, oppure più gradi combinati con la Table I del 38 CFR 4.25, + coniuge, Aid and Attendance del coniuge, genitori, figli → mese e anno),
`/va-disability-rates/2027/` (stato dell'aumento). Menu («VA disability»), piè di pagina, paragrafo in home e in `/how-we-check/#va-checks`.
Codice: `sezione_va.py` (chiamato da `genera.py`), JS in `stile.APP_JS` (`vaCombina`, `vaPaga`), raccolta in `raccolta/va.py`, avviso proprio (`DISCLAIMER_VA`: informazione, non consulenza sui benefici).

- **2027: tabelle NON calcolate, solo la percentuale ufficiale.** Al 15/11/2026: SSA +3,6 % da dicembre 2026 (Federal Register 91 FR 67380, doc 2026-21796); la legge dell'anno (H.R. 8552,
  Veterans' Compensation COLA Act of 2026) è su govinfo come «enrolled bill» dal 13/11 ma non è ancora tra le leggi pubblicate (ultima: P.L. 119-138); va.gov (pagina aggiornata il 2/11)
  mostra ancora le tabelle dal 1/12/2025; l'ultimo avviso del VA con gli importi è il 2026-02997 del 17/2/2026. **Perché non si calcola:** la legge dà la percentuale e una sola regola di
  arrotondamento (38 U.S.C. 1115(2): quote dei familiari sotto il 100 % arrotondate per difetto al dollaro); nessuna fonte ufficiale letta dice come si arrotonda al centesimo ogni importo aumentato.
  Prova fatta sugli avvisi 2024→2025 (2,5 %) e 2025→2026 (2,8 %): «importo × percentuale, metà in su» ridà 27 importi su 28 ogni anno (tutti i 10 importi base e i 7 dei familiari; sbaglia di
  1 centesimo solo il primo importo del 1114(r)); il troncamento ne ridà 11-12. Quindi il metodo è molto probabile ma non scritto: se il coordinatore decide di pubblicare una tabella
  «calcolata dal 3,6 % ufficiale, tabella VA non ancora pubblicata» il calcolo è: 10 importi base e importi del 1115(1) × 1,036 al centesimo (metà in su), poi `quota()` di `raccolta/va.py`.
  `verifica.py` oggi vieta qualsiasi importo base × 1,036 nelle pagine.
- **Quando esce la tabella 2027** la generazione si ferma da sola (`stato_2027()` in `sezione_va.py`): le frasi di `va_rates` («Effective December 1, 2025», «Review 2026 Veterans…») non si
  trovano più, oppure la legge compare in `plaw119` (`va_cola_2026`), oppure l'API del Federal Register dà un avviso più nuovo del 2026-02997. Allora: in `raccolta/va.py` aggiungere il 2027 in
  `ANNI` e `FILE` (pagina corrente = 2027, `past-rates-2026/` = 2026; l'avviso nel Federal Register può arrivare mesi dopo: finché manca, il confronto si fa con importi × percentuale e va detto),
  aggiornare le frasi in `raccolta/fonti.py`, `ANNO`/`PRIMA` e i testi «2026» in `sezione_va.py`, riscrivere `/va-disability-rates/2027/`, i casi a mano in `verifica.py` (`CASI_VA_MANO`).
  Poi `python3 milpay/raccolta/va.py && python3 milpay/raccolta/fonti.py --solo=va_rates,va_rates_2025,plaw119,fr_va_search,... && python3 milpay/genera.py && python3 milpay/verifica.py --browser`.
  Ricontrollare va.gov ogni 2-3 giorni fino al 1/12 (basta `fonti.py --solo=va_rates,plaw119,fr_va_search` + `genera.py`).
- **Dati** (`raccolta/va.py` → `dati/va.json`, importi in centesimi interi; file grezzi in `dati/grezzi/` con URL, data e SHA-256 nel registro `grezzi` di `dati/fonti.json`): due pagine va.gov
  (122 importi l'una), due avvisi del VA nel Federal Register letti su govinfo (importi di legge 38 U.S.C. 1114 e 1115(1)), XML dell'eCFR del 38 CFR 4.25, pagina va.gov «About disability ratings»,
  API del Federal Register. **Tutte le 244 celle di va.gov = importo di legge + quota 1115(2)**; Table I (76 righe × 9) = formula del testo del 4.25. La copia della Table I su va.gov ha un refuso
  (riga 86, colonna 80: 91 invece di 97): vale il regolamento, la differenza è dichiarata in `/how-we-check/` e `REFUSI_VA` ferma la raccolta se cambia.
- **Fonti con frasi** (`raccolta/fonti.py`, 12 nuove): va_rates, va_rates_2025, va_fr_2026, va_fr_2025, ssa_cola_2027, hr8552, plaw119_42, usc1115, cfr4_25, cfr4_26 (eCFR: serve la compressione,
  opzione `gzip`), va_about, fr_va_search. federalregister.gov (pagine HTML) chiede un CAPTCHA ai programmi: non aggirato, si usano la sua API e govinfo.
- **Controlli di `verifica.py`** (`controlla_va`, lettura dei file grezzi rifatta a parte): 1.368 celle pubblicate = file grezzi; dati dei calcolatori in 12 pagine = grezzo; JS = calcolo rifatto
  dagli importi di legge dell'avviso = copia Python su 2.888 combinazioni; gradi combinati JS = formula su 3.100 liste; 11 casi letti a mano (esempi di va.gov) e 8 esempi del regolamento;
  citazioni tra virgolette ritrovate nelle fonti; nessun importo × 1,036 in pagina; parole di previsione o consiglio vietate; avviso proprio della sezione.
  Playwright (script in scratchpad, non nel repository): 6 pagine nuove + home e how-we-check a 375 e 1280 px, chiaro e scuro, nessuno scorrimento orizzontale, menu su una riga, 11 casi del calcolatore per vista.
- **Non coperto e detto in pagina**: special monthly compensation, special benefit allowances, birth defect, superstiti (DIC); fattore bilaterale (38 CFR 4.26) non applicato dal calcolatore;
  famiglia con soli figli maggiorenni a scuola (la tabella del VA dà quell'importo solo come aggiunta: il calcolatore lo dice e non calcola). Niente date di pagamento («va disability pay dates 2025»
  18.100 ricerche, 3,57 $: nessuna fonte letta, possibile aggiunta) e niente tassazione.
- **Domanda**: `dati/domanda_va.json`, 77 ricerche seodata del 15/11 (us): «va disability calculator» 135.000 (1,69 $), «va disability rates 2025» 90.500, «va disability rates» 74.000,
  «va disability pay chart 2025» 49.500, «va rating calculator» 27.100, «va disability rating calculator» 22.200, «va disability pay chart» 22.200, «va combined rating calculator» 12.100,
  «100 va disability pay» 12.100, «2026 va disability rates» 3.600; tutte le frasi con 2027 ancora a 0. `genera.volume()` ora guarda prima la frase esatta, poi le simili.
