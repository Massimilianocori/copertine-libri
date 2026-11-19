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
FAQ: 77, ognuna legata a una ricerca misurata. Frase fissa in ogni pagina: «Information, not financial advice».

## Fonti (7 file in `dati/grezzi/`, 61 frasi alla lettera, `dati/fonti.json`)

| Fonte | Che cosa dà | Impronta |
|---|---|---|
| Modulo FAFSA 2027-28, PDF di studentaid.gov (pagine 1-2) | apertura 1/10/2026, scadenza federale 30/6/2028, voce di ogni Stato | sha256 del file |
| Federal Register 2026-18493 (govinfo.gov, 10/9/2026) | tassi 6,52 / 8,07 / 9,07 %, asta 4,468 %, storia dal 2013, tabella 2006-2013 | sha256 del file |
| Federal Register 2026-08556 (govinfo.gov, 1/5/2026) | 34 CFR 685.203: 20.500/100.000, 50.000/200.000, genitori 20.000/65.000, 257.500 a vita | sha256 del file |
| Public Law 119-21 (govinfo.gov), sez. 81001 e 82001 | stessi tetti, piano standard a fasce, formula del RAP | sha256 del file |
| FSA Handbook 2025-26, vol. 8 cap. 4 (fsapartners.ed.gov) | tetti dei corsi di laurea (5.500-12.500; 31.000/57.500) | sha256_frasi |
| 34 CFR 685.200 e 685.202, edizione 1/7/2025 (PDF di govinfo.gov) | requisito di credito del PLUS dei genitori; commissione trattenuta da ogni erogazione (4 % nel regolamento) | sha256 del file |

- **studentaid.gov il 19/11 chiudeva la connessione al nostro server** (HTTP 0, anche la home; riprovato tre volte nella giornata, l'ultima dopo la revisione: sempre HTTP 0 da qui): il PDF del modulo è quello scaricato il 18/11 dalla ricerca (data di lettura 18/11, detta in pagina).
  `fonti.py` tiene il file registrato quando un sito non risponde e lo dice a fine giro. Le pagine web di studentaid.gov (vuote senza JavaScript) e ed.gov (403) non sono usate.
- Il volume 8 del manuale 2026-27 non è ancora pubblicato: la tabella dei corsi di laurea viene dal 2025-26 **più** la frase della regola finale «remain unchanged» (i due totali devono coincidere). Detto in `/how-we-check/`.
- I file di govinfo con un indirizzo email cambiano qualche byte a ogni scarico (protezione degli indirizzi): `fonti.py` scrive «file cambiato» anche se le cifre sono le stesse; l'impronta vale per il file conservato.
- Controlli in `fonti.py`: due letture del PDF (normale e `-raw`) uguali voce per voce; asta + maggiorazione = tasso; legge = regola per ogni tetto; scaglioni consecutivi.
- Non coperto perché senza fonte letta: la commissione esatta di ogni anno (il regolamento dice 4 % per il PLUS; la cifra applicata può essere diversa: in pagina si rimanda all'ufficio aiuti), definizione di prestito sussidiato, borsa Pell 2027-28, scadenze 2026-27, scadenze delle singole università, prezzi delle università
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

## Revisione indipendente del 19/11/2026 (voto 8,2): che cosa è cambiato

1. Tetti: «stesso programma» distinto per tipo di studente (cambio di indirizzo dentro lo stesso titolo solo per i corsi di laurea e il PLUS dei genitori; i laureati che cambiano programma e chiunque cambi università perdono l'eccezione; il cambio di concentrazione nello stesso codice CIP a 4 cifre la conserva). Quattro frasi della regola finale citate; avviso anche nelle FAQ e in `/parent-plus-loans/`.
2. Calcolatore della rata: pagamento minimo di 50 $ al mese (34 CFR 685.208, letto dalla regola finale in `aiuti.json`, `rimborso.standard.minimo_mese`): sotto i 50 $ si usa 50 e si ricalcolano rate e interessi; saldo sotto 50 $ = un pagamento del dovuto. Nota in pagina con le due frasi; `verifica.py` ha il minimo nel conto di riferimento e due conti a mano.
3. Tabella 2006-2013: etichette di chi prende il prestito copiate per intero (righe di continuazione).
4. RAP: anche chi ha solo prestiti precedenti al 1/7/2026 può sceglierlo (sez. 455(d)(1)(F)), punto e FAQ.
5. PLUS dei genitori: commissione trattenuta da ogni erogazione (34 CFR 685.202) e controllo del credito (685.200(c)), due fonti nuove.
6. PLUS dei genitori: un prestito nuovo dal 1/7/2026 porta nel piano standard anche i PLUS vecchi.
7. RAP: dichiarazione congiunta = reddito della coppia, con ripartizione sul debito (685.209(e) e (g)); la quota capitale richiede il pagamento puntuale e si perde nei mesi pagati in anticipo (685.209(o)).
8. **Non fatto**: rilettura del modulo FAFSA il 19/11. Da questo server studentaid.gov continua a chiudere la connessione; la data di lettura resta il 18/11. Basta rilanciare `fonti.py` da una macchina che lo raggiunge.
9. `/fafsa-deadlines/`: pulsante «Jump to your state» nella testata.

## Schede dei costi di 200 università (prova dell'idea A, riga 155 della classifica) – 19/11/2026

`/college-costs/` (indice con ricerca e filtro per tipo) + 200 pagine `/college-costs/<nome-ufficiale>/`. Sito: 221 pagine indicizzabili + 404. Voce «College costs» nel menu, nel piede, in home, in `/federal-student-loan-limits/` e `/parent-plus-loans/`. Riquadro dei partner sempre SPENTO (Ascent non è nemmeno in `affiliati.json`).

**Fonti (2 nuove, `dati/fonti_scorecard.json`, script `raccolta/scorecard.py`):**
- File College Scorecard «Most Recent Institution-Level Data», `ed-public-download.scorecard.network/downloads/Most-Recent-Cohorts-Institution_11022026.zip`: HTTP 200 il 19/11, 24.209.950 byte, sha256 `4c31be45…a7305d`, 6.272 istituti, 3.379 colonne, aggiornato il 2/11/2026. Lo zip sta in `cache/scorecard/` (non va nel repository). Nel repository c'è `dati/grezzi/scorecard_estratto.csv`: tutte le 6.272 righe con le 35 colonne usate, celle copiate carattere per carattere, con la sua impronta.
- Dizionario dei dati (`collegescorecard.ed.gov/files/CollegeScorecardDataDictionary.xlsx`, rilasciato il 15/10/2026, in `dati/grezzi/`): **nel CSV l'anno non c'è**; viene dal foglio «Most_Recent_Inst_Cohort_Map». Tasse 2025-26; costo totale e prezzo netto 2024-25; ammissione e iscritti autunno 2024; laurea: classe entrata nel 2019-20; debito mediano: anni fiscali 2024 e 2025; debito PLUS: 2023-24 e 2024-25. Ogni cifra in pagina ha il suo anno accanto.
- «NA» = «Not reported in the file», «PS» = «Suppressed in the file (privacy)»: detti in pagina, mai stimati. Università pubbliche: il prezzo netto del file vale solo per chi paga le tasse da residente (detto in pagina).

**Scelta delle 200 (`raccolta/domanda_universita.py`, `dati/domanda_universita.json`):** 745 candidate (PREDDEG 3, aperte, almeno 2.500 studenti, o 900 se ammettono meno del 30 %), 2.605 frasi «<nome> tuition» e «<nome> cost» misurate con seodata (USA). Nomi cercati: nome ufficiale, nome senza campus (solo se di una sola università o della sede con almeno il doppio degli studenti), nome senza «University» (solo se non ambiguo), alias e sigle della colonna ALIAS (sigle solo se sono le iniziali e uniche nel file). Una frase che può indicare due università non è di nessuna («usc», «asu», «msu» non sono attribuite). Domanda di un'università = volume della frase più cercata: **1.417.600 ricerche al mese sulle 200** (2.365.610 sommando «tuition» e «cost», ma per molte lo strumento dà lo stesso numero alle due frasi: è un tetto). Ultima scelta: 2.900; a pari volume decide la somma, poi gli studenti (UT Dallas e Florida Southern restano fuori a 2.900). Il titolo di ogni pagina comincia con la frase misurata. Il primo giro di curl a 6 in parallelo ha dato 706 «upstream_error»: rifatti a 2 in parallelo, zero errori.

**Il «buco»:** per ogni fascia di reddito, 4 anni al prezzo netto del file (tenuto fermo) meno i tetti già del sito (`buco()`: studente a carico 5.500/6.500/7.500/7.500 entro 31.000; genitori 20.000 l'anno entro 65.000). Dichiarato «our arithmetic», con l'avvertenza che non è un consiglio. In 4 anni i prestiti federali coprono al massimo 92.000 $.

**Controlli (`verifica.py`, 0 errori; `--browser` 0 errori):** ogni cella riletta dal file (dallo zip ufficiale se è in cache, e allora l'estratto deve essere identico cella per cella; altrimenti dall'estratto con la sua impronta), anni trascritti a mano e ritrovati nel dizionario, ogni importo e percentuale del testo, del titolo, della descrizione e delle FAQ dentro l'insieme delle cifre del file o del conto; buco rifatto con due conti (forma chiusa e anno per anno); scelta delle 200 ricontrollata sulle misure e sulle risposte conservate; link alla scadenza FAFSA dello Stato (pagina dello Stato se è uno dei 10, altrimenti l'indice, più la voce del modulo parola per parola), link ai prestiti. Browser: indice e 11 schede campione in 4 viste, tutte le 200 a 375 px, filtro e ricerca dell'indice.

**Non fatto / da sapere:** niente commit e niente IndexNow (da decidere dopo la revisione indipendente, non ancora fatta su queste pagine). L'indirizzo del calcolatore del prezzo netto di ogni università è quello scritto nel file (link esterno `nofollow`, non provato uno per uno). Stipendio a 10 anni e pagine per Stato dell'idea A non ci sono. Misura a 45 giorni: 3/1/2027.
Aggiornare: `python3 collegeaid/raccolta/scorecard.py` (cambiare `URL_ZIP` quando esce un file nuovo, e le trascrizioni `M_SC_*` in `verifica.py`), poi `genera.py` e `verifica.py --browser`.
