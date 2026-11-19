# US College Aid (collegeaid) – note di lavoro

Costruito il 19/11/2026 come **prova** dell'idea B di `studio-business/intelaiatura/fronti-2026-11-18-college.md` («aiuti e prestiti 2027-28»).
Sito statico in inglese (USA) generato da `genera.py` in `sito/`. Indirizzo previsto: **`https://us-college-aid.netlify.app`** (nome libero il 19/11: risposta 404;
costante `URL_SITO` in `genera.py` e in `verifica.py`). **Il sito Netlify non esiste ancora** (host in `NON_ONLINE` di `strumenti/indexnow.py`).
Pubblicità: AdSense acceso in `monetizzazione.json`, contatore GoatCounter. Manca la revisione indipendente (sez. 3.6 di ORGANIZZAZIONE.md) prima della pubblicazione.

## Pagine (20 indicizzabili + 404)

`/` · `/fafsa-deadlines/` (59 voci: 50 Stati, DC, 8 territori; testo del modulo parola per parola, date estratte, filtro) · 10 pagine `/fafsa-deadlines/<stato>/`
(California, Texas, Florida, Michigan, Ohio, New Jersey, Illinois, Massachusetts, Indiana, Pennsylvania) · `/student-loan-interest-rates/` (2026-27, storia 2013-2027, 2006-2013) ·
`/federal-student-loan-limits/` (tetti dal 1/7/2026, corsi di laurea invariati, prima/dopo, eccezione per chi era già iscritto) · `/student-loan-payment-calculator/`
(piano standard: 10 anni per i prestiti vecchi, 10-25 anni per fascia di capitale dal 1/7/2026) · `/repayment-assistance-plan/` (formula della legge, calcolatore, un mese sul saldo) ·
`/parent-plus-loans/` (9,07 %, 20.000/65.000 $, calcolatore di quanto resta scoperto con il costo scritto dall'utente) · `/how-we-check/` (modulo delle correzioni con campo-trappola) · `/about/` · `/privacy/`.
FAQ: 76, ognuna legata a una ricerca misurata. Frase fissa in ogni pagina: «Information, not financial advice».

## Fonti (5 file in `dati/grezzi/`, 47 frasi alla lettera, `dati/fonti.json`)

| Fonte | Che cosa dà | Impronta |
|---|---|---|
| Modulo FAFSA 2027-28, PDF di studentaid.gov (pagine 1-2) | apertura 1/10/2026, scadenza federale 30/6/2028, voce di ogni Stato | sha256 del file |
| Federal Register 2026-18493 (govinfo.gov, 10/9/2026) | tassi 6,52 / 8,07 / 9,07 %, asta 4,468 %, storia dal 2013, tabella 2006-2013 | sha256 del file |
| Federal Register 2026-08556 (govinfo.gov, 1/5/2026) | 34 CFR 685.203: 20.500/100.000, 50.000/200.000, genitori 20.000/65.000, 257.500 a vita | sha256 del file |
| Public Law 119-21 (govinfo.gov), sez. 81001 e 82001 | stessi tetti, piano standard a fasce, formula del RAP | sha256 del file |
| FSA Handbook 2025-26, vol. 8 cap. 4 (fsapartners.ed.gov) | tetti dei corsi di laurea (5.500-12.500; 31.000/57.500) | sha256_frasi |

- **studentaid.gov il 19/11 chiudeva la connessione** (HTTP 0, anche la home): il PDF del modulo è quello scaricato il 18/11 dalla ricerca (data di lettura 18/11, detta in pagina).
  `fonti.py` tiene il file registrato quando un sito non risponde e lo dice a fine giro. Le pagine web di studentaid.gov (vuote senza JavaScript) e ed.gov (403) non sono usate.
- Il volume 8 del manuale 2026-27 non è ancora pubblicato: la tabella dei corsi di laurea viene dal 2025-26 **più** la frase della regola finale «remain unchanged» (i due totali devono coincidere). Detto in `/how-we-check/`.
- I file di govinfo con un indirizzo email cambiano qualche byte a ogni scarico (protezione degli indirizzi): `fonti.py` scrive «file cambiato» anche se le cifre sono le stesse; l'impronta vale per il file conservato.
- Controlli in `fonti.py`: due letture del PDF (normale e `-raw`) uguali voce per voce; asta + maggiorazione = tasso; legge = regola per ogni tetto; scaglioni consecutivi.
- Non coperto perché senza fonte letta: commissioni d'apertura dei prestiti, definizione di prestito sussidiato, borsa Pell 2027-28, scadenze 2026-27, scadenze delle singole università, prezzi delle università
  (il «buco» per università dell'idea A resta fuori: qui c'è solo il calcolatore con il costo dell'utente).

## Domanda misurata (`dati/domanda.json`, 114 frasi seodata, USA)

«fafsa deadline» 60.500 · «repayment assistance plan» 60.500 · «student loan calculator» 60.500 · «parent plus loan» 60.500 · «student loan interest rates» 40.500 ·
«student loan payment calculator» 27.100 · «when is fafsa due» 27.100 · «grad plus loan» 22.200 · «big beautiful bill student loans» 14.800 · «federal student loan limits» 1.600.
Per Stato: California 1.600, Texas 720, Florida 480, Michigan 390, Ohio / New Jersey / Illinois 260, Massachusetts / Indiana 210, poi quattro a 170 (Pennsylvania, Oregon, Maryland, Georgia: scelta la Pennsylvania).
Le frasi con l'anno («fafsa deadline 2027-28», «student loan limits 2026») risultano a 0 nello strumento: i titoli usano l'anno comunque.

## Conti

`app.js`: centesimi interi, tassi in millesimi di punto. Rata = P·r/(1−(1+r)^−n), interesse mensile arrotondato al centesimo (i gestori contano per giorno: detto in pagina).
RAP: percentuale dello scaglione sull'intero reddito ÷ 12 − 50 $ per persona a carico, minimo 10 $; la legge non dice come arrotondare: al centesimo.
Tetti, scaglioni e fasce arrivano ai calcolatori dall'attributo `data-regole` (da `aiuti.json`), mai scritti nel JS.

## Controlli (`verifica.py`, 0 errori il 19/11)

Trascrizioni a mano di tassi, storia, tetti, scaglioni, fasce e date dei 10 Stati; voci FAFSA rilette dal PDF (la pagina 2 deve essere coperta per intero); ogni importo e ogni percentuale delle pagine
dentro l'insieme delle cifre trascritte; 4.446 casi dei calcolatori (JS pubblicato = conto di riferimento in Decimal); citazioni, FAQ = JSON-LD, link, modulo, partner spenti, chiavi.
`--browser`: 84 viste (21 pagine a 375/1280, chiaro e scuro), contrasto, 46 prove sui calcolatori, filtro, conto dei giorni con orologio fermo, senza JavaScript.

## Riquadro dei partner (SPENTO)

`dati/affiliati.json`: Splash Financial (240 $ letti su FlexOffers) e SoFi (120 $), `"attivo": false`, `"link": ""`. `verifica.py` dà errore se uno ha un link o è acceso: si cambia solo dopo la decisione di Massimiliano
(e allora va tolto quel controllo). Il riquadro uscirebbe solo in `/student-loan-payment-calculator/`, sotto calcolatore ed esempi, con l'avviso che rifinanziare fa perdere i piani federali.

## Quando aggiornare

Modulo FAFSA: a ogni ristampa (uno Stato che cambia data) e ogni ottobre per l'anno nuovo. Tassi: avviso dopo l'asta di maggio (di solito in estate). Manuale 2026-27 vol. 8: quando esce, cambiare l'indirizzo in `fonti.py`.
`python3 collegeaid/raccolta/fonti.py && python3 collegeaid/genera.py && python3 collegeaid/verifica.py --browser && python3 studio-business/strumenti/monetizzazione.py verifica collegeaid`
