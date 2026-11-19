# Statute of Limitations by State – note di lavoro (13/11/2026)

Sito statico in inglese (en-US) generato da `genera.py` in `sito/`: termini di prescrizione civile ("statute of limitations") per
11 Stati × 6 cause (10 il 13/11 mattina; Pennsylvania aggiunta il 13/11 sera, vedi la sezione in fondo), con il testo di legge citato parola per parola, link al sito ufficiale del parlamento, data di lettura, regole di
decorrenza e di sospensione, preavvisi per le cause contro enti pubblici, modifiche recenti e un calcolatore della scadenza generale.
Nato da `studio-business/intelaiatura/fronti-2026-11-13-prescrizione-usa.md` (prova di 60 pagine, voto 5, COSTRUIRE in coda).
Indirizzo: `https://statute-limits-by-state.netlify.app`, **online dal 13/11/2026** (costante `URL_SITO` in `genera.py` e `verifica.py`).
Nome: descrittivo e generico (nessun marchio). Le modifiche del 13/11 sera (sezione in fondo) NON sono pubblicate né committate.

## Pagine (88 indicizzabili + 404 dal 13/11 sera; prima 79)

| Pagina | Contenuto |
|---|---|
| `/` | calcolatore (Stato + causa + data → data generale per ogni variante, limite massimo, elenco delle eccezioni con articolo), tabella 10 × 6, come si legge un termine, cambi recenti (Florida 2023, Ohio 2021), 5 FAQ |
| `/<stato>/` (10) | tabella delle 6 cause, calcolatore con lo Stato scelto, regole di sospensione dello Stato (citate), cause contro enti pubblici, cambi recenti |
| `/<stato>/<causa>/` (59) | termine/i con citazione, decorrenza, limite massimo (repose) se c'è, esempio calcolato, calcolatore della cella, eccezioni della causa, regole dello Stato, enti pubblici, cambi recenti se toccano la cella, confronto con gli altri 9 Stati, FAQ se c'è |
| `/<causa>/` (6) | tabella di confronto fra 10 Stati con articolo e limite massimo, calcolatore, citazione per ogni Stato; su `/debt/` la regola federale |
| `/car-accident/`, `/credit-card-debt/` (dal 13/11 sera) | viste sulle cause esistenti (lesioni + danni + morte; debiti), nessuna cella nuova |
| `/about/`, `/how-we-check/`, `/privacy/`, `404.html` | senza pubblicità |

Stati: TX, FL, OH, WA, VA, NC, MI, AZ, MA, MN (gli stessi letti dal ricercatore). Cause scelte con la domanda misurata (sotto):
personal injury, medical malpractice, wrongful death, debt collection, breach of contract (scritto e verbale nella stessa pagina),
property damage. **Manca Washington × wrongful death** (59 celle, non 60): il capitolo 4.20 RCW non scrive un termine suo e la regola
è "nessuna cella senza un articolo letto che dica il termine". California e New York esclusi: leginfo.legislature.ca.gov e
nysenate.gov rispondono 403 ai programmi (non aggirato); l'archivio ufficiale della California e l'API del Senato di New York (chiave
gratuita da chiedere) restano per l'estensione. Louisiana non inclusa (nessuna pagina, nessuna menzione).

## Fonti (81 file, letti il 13/11/2026, nessun blocco aggirato)

`raccolta/fonti.py` scarica ogni pagina ufficiale in `raccolta/_grezzi/` (fuori da git) e scrive in `dati/fonti.json` indirizzo,
data, HTTP, byte e SHA-256. Siti: tcss.legis.texas.gov (CPRC capp. 16, 74, 101; Finance Code 392; Government Code 81),
leg.state.fl.us (§§ 95.11, 95.051, 95.04, 768.28, 766.106) + laws.flrules.org (Laws of Florida 2023-15, PDF), codes.ohio.gov (11
sezioni, più le versioni 2012 di 2305.06 e 1993 di 2305.07), app.leg.wa.gov (cap. 4.16 RCW intero, 4.96.020), law.lis.virginia.gov
(8 sezioni), search-prod.lis.state.oh.us (Senate Bill 13 approvato, PDF: regola transitoria), courts.wa.gov (sentenza Bennett v. United States, PDF), ncleg.gov (7), legislature.mi.gov (10), azleg.gov (11), malegislature.gov (9), revisor.mn.gov (8), eCFR (12 CFR
1006.26, Regulation F). Il testo delle leggi statali non ha diritto d'autore (Georgia v. Public.Resource.Org, 2020).

I termini, le citazioni e le spiegazioni stanno in `norme.py` (curati a mano): ogni citazione è un elenco di frammenti copiati dal
testo ufficiale; `genera.py` si ferma se un frammento non c'è più nel file salvato.

**Cose trovate leggendo le leggi** (dette nelle pagine):
- Florida HB 837: ch. 2023-15 sposta "an action founded on negligence" da 4 a 2 anni; approvata e in vigore il 24/3/2023; s. 28: vale
  per le cause "accruing after the effective date". Il calcolatore usa 4 anni fino al 24/3/2023 compreso, 2 dopo. Oggi è § 95.11(5)(a)
  (numerazione cambiata da leggi 2024-2025). § 95.11(4): debiti ospedalieri 3 anni dall'invio al recupero crediti.
- Ohio SB 13 (16/6/2021): scritti 8 → 6 anni, verbali 6 → 4, debiti di consumo 6 anni con decorrenza 30 giorni dopo l'ultimo
  addebito o pagamento (§ 2305.07(C)). Regola transitoria (sezioni 4 e 5 della legge, non nel codice): letta dal revisore nel PDF
  ufficiale del parlamento (API LIS; legislature.ohio.gov dà errore di certificato, non aggirato) e citata nelle pagine: vale il
  termine nuovo contato dal 16/6/2021 oppure la fine del termine precedente, quello che viene prima. Il calcolatore **non dà una
  data** per i contratti Ohio sorti prima del 16/6/2021 (per i debiti di consumo conta il giorno in cui il diritto sorge, cioè 30
  giorni dopo la data inserita) e mostra la regola. § 2305.06
  di nuovo modificato dal SB 219 con effetto 23/9/2026 (resta 6 anni).
- Minnesota lesioni: § 541.05 subd. 1(5) 6 anni e § 541.07(1) 2 anni ("other tort resulting in personal injury"): mostrate tutte e
  due, con la frase che la colpa (negligence) è "generally treated" sotto i 6 anni e l'invito a chiedere a un avvocato.
- Texas debiti: Finance Code § 392.307 (chi compra debiti non può fare causa dopo i 4 anni; un pagamento non li riapre).
- Arizona § 12-548(B): per debiti scritti e carte di credito vale il termine dell'Arizona se un altro Stato è in conflitto.

## Domanda

- `raccolta/volumi.py`: 15 richieste senza chiave a api.seodata.dev (la chiave del conto non è stata usata né letta), in
  `dati/volumi.json`. Esempi (USA, al mese): medical malpractice statute of limitations 4.400 (10 $); statute of limitations on debt
  in texas / in florida 2.400 ciascuna; statute of limitations florida personal injury 1.600 (38 $); ... personal injury texas 880
  (61 $); ... breach of contract texas 720; property damage 480; wrongful death texas 210 (32 $); calculator 210; Ohio 2.400,
  Michigan, Virginia, North Carolina, Arizona 1.600 ciascuno; Minnesota 140.
- `raccolta/domanda.py`: autocompletamento Google gl=us, 38 radici, 347 suggerimenti in `dati/domanda.json`. Le 24 FAQ
  (`dati/faq.json`) nascono ognuna da un suggerimento vero; i termini nelle risposte sono segnaposto riempiti da `norme.py`.

## Regole legali

- Informazione, non consulenza: su ogni pagina la frase fissa "General information, not legal advice, and not a substitute for the
  advice of an attorney ... Talk to a licensed attorney in your state" (Texas Government Code § 81.101(c): la pubblicazione su un
  sito non è "practice of law" se dichiara in modo chiaro e visibile di non sostituire il parere di un avvocato) e il riquadro rosso
  "Estimate, not legal advice" sotto le cifre. Nessuna risposta su casi singoli, nessun "puoi ancora fare causa"; se la data
  generale è passata il calcolatore dice solo che le eccezioni possono cambiarla e di parlare con un avvocato.
- Nessun modulo (nemmeno correzioni: chi scrive racconterebbe il suo caso), nessuna raccolta di contatti, nessun rimando a studi legali.
- Nessuna intermediazione di debiti: `verifica.py` rifiuta debt relief, debt settlement, consolidat…, loan(s), guarantee…, free
  consultation, lawyer/attorney near me, you should sue, you can still sue; e i temi sexual abuse / sexual assault / child sex (nessuna
  pagina e nessuna citazione su abusi).

## Monetizzazione

- AdSense: `limits` aggiunto a `SITI` in `studio-business/strumenti/monetizzazione.py` e ad `adsense_siti` e `_siti_della_rete` in
  `monetizzazione.json`; script solo sulle 76 pagine di contenuto (home, Stati, celle, cause); about, how-we-check, privacy e 404
  segnate senza pubblicità. `ads.txt` scritto da `genera.py`; privacy con la sezione AdSense e la frase per la California.
- **Riquadro "Legal documents online" preparato e SPENTO** (`dati/affiliati.json`): Rocket Lawyer e LegalZoom via FlexOffers, non
  ancora iscritti. Per accenderlo: iscrizione FlexOffers, link tracciati, dominio dei link in `domini_affiliazione`, `attivo: true`,
  rigenerare e verificare.

## Controlli (`python3 limits/verifica.py --browser`, 13/11/2026: 0 errori, 0 avvisi)

1. SHA-256 di ogni file grezzo = `dati/fonti.json`; `.gitignore` esclude `raccolta/_grezzi/`.
2. Estrattore **scritto a parte** (html.parser e `pdftotext -layout`; non usa `testo.py` né `genera.py`): 101 periodi (varianti,
   periodi precedenti e limiti massimi) riletti dalla frase della legge ("within two years", "WITHIN FOUR YEARS", "is 3 years") e
   confrontati con `norme.py`, con 1.160 cifre nelle pagine (attributi `data-v`) e con i dati del calcolatore.
3. 522 citazioni nelle pagine presenti parola per parola nel testo ufficiale.
4. Calcolatore: JS del sito eseguito con node = calcolo Python scritto in `verifica.py` su 744 casi (59 celle × 12 date + 36 calcolati a mano, fra cui
   29/2, 23-24-25/3/2023, 15-16/6/2021) + 6 casi noti scritti a mano.
5. Titoli ≤ 65 e descrizioni 70-160 uniche, un h1, canonical = sitemap, link interni e ancore, robots, `netlify.toml` con `ignore`,
   chiave IndexNow, GoatCounter ovunque, frase fissa ovunque, nessun modulo, parole e temi vietati, nessun nome di modello AI (sito,
   codice, dati, questa nota), nessun dato personale.
6. FAQ: ricerca presente in `dati/domanda.json`; JSON-LD = testo visibile. 7. `MON.controlla_sito` + nessun link affiliato.
8. `--browser`: Playwright 375 e 1280 px, chiaro e scuro, su `/`, `/florida/personal-injury/`, `/ohio/debt/`, `/debt/`; tutte le
   richieste non locali bloccate con `page.route`; calcolatore compilato e cliccato, niente scorrimento orizzontale, testi ≥ 11 px,
   tema, nessun errore JS. Screenshot in `cache/screenshot/` (fuori da git).

Anche: `python3 studio-business/strumenti/monetizzazione.py verifica limits` → 0 errori.

## Aggiornamento (almeno una volta l'anno e dopo ogni sessione legislativa; `genera.py` si ferma dopo 400 giorni dalla lettura)

1. `python3 limits/raccolta/fonti.py` (riscarica tutto; se una pagina non risponde 200 resta la copia vecchia e lo script lo dice).
2. `python3 limits/genera.py`: se una citazione non c'è più, leggere la sezione sul sito ufficiale, correggere `norme.py` (testo,
   anni, spiegazione, eventuale voce in `cambi`) e aggiornare `VERIFICATO_IL`.
3. `python3 limits/verifica.py --browser` → 0 errori.
4. Ogni tanto `python3 limits/raccolta/domanda.py` e controllare che ogni FAQ abbia ancora la sua ricerca.
5. Pubblicare solo se `sito/` è cambiato (crediti Netlify); poi IndexNow.

## Da fare per pubblicare (passi del titolare)

1. Netlify: nuovo sito dal repository, branch `ccr-b7fd6b9e-n096cr`, Base directory `limits/sito`, Build command vuoto, Publish
   directory `.`; nome `statute-limits-by-state` (se diverso, cambiare `URL_SITO` in `genera.py` e `verifica.py`, rigenerare).
2. Search Console: proprietà `https://statute-limits-by-state.netlify.app/` (meta di verifica della rete già nelle pagine), sitemap.
3. Aggiungere `("statute-limits-by-state.netlify.app", "limits")` a `SITI` in `studio-business/strumenti/indexnow.py` e lanciare
   l'invio (non fatto qui: il commit è limitato a `limits/` e alla registrazione in monetizzazione).
4. Più avanti: FlexOffers (Rocket Lawyer, LegalZoom); chiave gratuita dell'API del Senato di New York per l'estensione.

## Dubbi per il revisore indipendente

- Ogni periodo è letto dal testo della legge, ma alcune scelte di classificazione sono interpretazioni dichiarate come tali:
  Minnesota lesioni (6 contro 2 anni), Arizona contratti (le sezioni parlano di "debt"), Florida danni alle cose (colpa 2 anni contro
  4 anni per "injuring personal property" e "trespass on real property"), Texas contratti (residuale 4 anni § 16.051, debito § 16.004),
  Michigan wrongful death ("3 years after the time of the death or injury": il calcolatore conta dalla data della morte e lo dice),
  North Carolina colpa medica (3 anni dalla clausola "below three years" di § 1-15(c)).
- Nessuna giurisprudenza riassunta; la nota su Washington medical malpractice cita solo la nota del legislatore su DeYoung.
- Washington RCW 4.16.350: il testo della pagina ufficiale è stato tagliato nel mio controllo a vista dopo "until the date the patient
  or the patient's"; le citazioni usate sono parti precedenti, presenti nel file.
- Massachusetts debiti: ho letto solo il capitolo 260; eventuali regole sui debiti di consumo in altri capitoli o regolamenti (940 CMR)
  non lette, e la pagina lo dice.
- Calcolatore: 29/2 → 28/2 (la data più vicina e prudente); nessuno spostamento per weekend e festivi; non applica sospensioni.

## Revisione indipendente (13/11/2026)

Rilette dal sito ufficiale tutte le 81 fonti con un programma scritto a parte: 265 frammenti citati su 265 presenti parola per parola
(59 celle su 59, nessun termine sbagliato). Corretto o aggiunto:
- Washington colpa medica: il limite di otto anni è stato dichiarato incostituzionale dalla Corte Suprema dello Stato il 7/12/2023
  (Bennett v. United States); la pagina e il calcolatore lo mostrano ancora com'è scritto nella legge, ma con la frase della sentenza
  citata dal sito dei tribunali. È l'unica sentenza citata.
- Ohio: regola transitoria letta e citata (sopra); la prova "prima del 16/6/2021" guarda il giorno in cui il diritto sorge.
- Debiti: l'etichetta della data non dice più "o ultimo pagamento" (resta solo in Ohio, dove lo dice la legge); su ogni pagina debiti
  la nota "scaduto il termine per fare causa non vuol dire debito cancellato" e l'ambito della regola federale (12 CFR 1006.2(i)).
  Massachusetts: resta 6 anni (c. 260 § 2); le proposte di legge per 5 anni sui debiti di consumo non risultano approvate.
- Calcolatore: accanto al risultato la frase "nessuna sospensione, nessuna regola di scoperta, nessun preavviso, nessuno spostamento
  per weekend e festivi", l'elenco dei preavvisi agli enti pubblici dello Stato per le cause per danni, la nota sul 29 febbraio.
- Michigan wrongful death (data: morte o lesione, la prima è la più prudente; rimando alla colpa medica), North Carolina colpa medica
  (i tre anni vengono da § 1-52, citato), Arizona contratti (strumento scritto firmato fuori dallo Stato 4 anni; vendita di beni),
  Florida (termine di 4 anni per le cause contro lo Stato § 768.28(14); frode fino a 7 anni; morte da cure mediche), Minnesota
  (responsabilità oggettiva da prodotto 4 anni).
- Pubblicità: lo spazio non è più subito sotto il risultato del calcolatore. Peso: le pagine cella portano solo la loro cella (circa
  25-32 KB invece di 55); home, Stati e cause leggono i dati da un solo file in cache `assets/calc.<impronta>.js` (35 KB).
- `verifica.py`: 36 casi calcolati a mano, controlli su avvertenze, debiti, enti pubblici, posizione della pubblicità, sentenza e regola
  transitoria; nel browser anche Ohio prima del 2021 e Washington.

## Domanda misurata, titoli, FAQ, Pennsylvania e due viste (13/11/2026 sera; NON pubblicato, NON committato: revisione indipendente, poi pubblicazione)

**Misura.** `api.seodata.dev /v1/keyword` (USA, volume medio mensile Google Ads) il 13/11/2026: 317 richieste con curl, 181 con volume,
136 `errore: 404` (frase non nel database). File `dati/volumi-2026-11-13.json` (volume, cpc, competition e dieci frasi simili per frase);
script `raccolta/volumi_misura.py` (la chiave è letta solo dentro la shell di curl: mai stampata né scritta; il grep del prefisso della chiave su `limits/` è vuoto,
e `verifica.py` lo ricontrolla sul file misurato e su tutti i .py/.json). Frasi misurate: "statute of limitations <causa> <stato>", "<stato>
statute of limitations <causa>", "how long do you have to sue for <causa> in <stato>" (tutte 404), "<stato> debt statute of limitations",
"<stato> statute of limitations", le generiche, CA/NY/GA/PA/IL/NJ, credit card debt, car accident, fraud, defamation, wrongful termination,
"lemon law <stato>".

**Ricerche più cercate (al mese, USA).** lemon law texas 12.100 · lemon law florida 9.900 · california statute of limitations 8.100 ·
texas statute of limitations 6.600 · florida statute of limitations 5.400 · statute of limitations on debt 4.400 · medical malpractice statute of
limitations 4.400 · statute of limitations auto accident 4.400 (simile) · lemon law ohio / michigan 4.400 · statute of limitations for car accident
3.600 (simile) · lemon law WA/VA/NC/AZ/MA 3.600 · statute of limitations by state 2.900 · new york statute of limitations 2.900 · how long is the
statute of limitations 2.900 (simile) · pennsylvania statute of limitations 2.400-2.900 · statute of limitations debt texas / florida 2.400 ·
car accident statute of limitations 2.400 · ohio / georgia / pennsylvania / illinois statute of limitations 2.400 · statute of limitations debt
california 2.400 · fraud statute of limitations 1.900 · statute of limitations on credit card debt 1.600 · statute of limitations personal injury
florida 1.600 · personal injury statute of limitations 1.300 · wrongful death statute of limitations 1.000 · ... debt ohio 880 · ... personal
injury texas 880 · breach of contract statute of limitations 880 · pennsylvania debt 720 · statute of limitations medical malpractice texas 590 ·
property damage statute of limitations 480 · statute of limitations on debt by state 390 · pennsylvania medical malpractice 390 · pennsylvania
personal injury 320. Celle piccole: "<stato> statute of limitations property damage" 30-320, "... breach of contract" 30-720 (TX/FL 720).
Tutte le "how long do you have to sue for ..." e "medical malpractice arizona/new york/new jersey": non nel database.

**Fuori tema ma enorme: "lemon law <stato>"** 1.600-12.100 al mese in tutti e 10 gli Stati coperti (cpc 6-24 $; TX 12.100, FL 9.900, OH/MI/NC
4.400). Non è prescrizione e non è stato costruito qui: è il candidato più forte per un sito o una sezione nuova (idea di riserva di
`fronti-2026-11-13-stati-usa-alto-valore.md`), da proporre alla sessione principale con le stesse regole (legge citata, nessun consiglio).

**Titoli, h1 e descrizioni (tutto da `genera.py`; URL invariati, nessun rinvio):**

| Pagina | Titolo prima | Titolo dopo | h1 dopo | Ricerca guida (vol.) |
|---|---|---|---|---|
| 59 celle (non debiti), es. `/texas/personal-injury/` | Texas Personal Injury Statute of Limitations (2 Years) | Texas Statute of Limitations for Personal Injury (2 Years) | invariato ("Texas statute of limitations for personal injury") | texas statute of limitations 6.600 + "... personal injury texas" 880 (le tre forme hanno lo stesso volume: il titolo ora comincia con la frase dello Stato) |
| 11 celle debiti, es. `/texas/debt/` | Texas Debt Collection Statute of Limitations (4 Years) | Texas Statute of Limitations on Debt (4 Years) | Texas statute of limitations on debt (prima "for debt collection") | statute of limitations debt texas 2.400, statute of limitations on debt 4.400 |
| `/debt/` | Debt Collection Statute of Limitations by State (10 States) | Statute of Limitations on Debt by State (11 States) | Statute of limitations on debt by state | statute of limitations on debt 4.400, ... by state 390 |
| altre 5 pagine causa | "... by State (10 States)" | "... by State (11 States)" | invariato | medical malpractice ... 4.400, personal injury ... 1.300, ecc. |
| 11 pagine Stato | invariato ("Texas Statute of Limitations: Civil Deadlines by Claim") | invariato | "Texas statute of limitations for civil claims" (prima "statutes", plurale) | texas statute of limitations 6.600 |
| descrizioni delle celle | "Texas personal injury statute of limitations: 2 years under …" | "Texas statute of limitations for personal injury: 2 years under …" | | |
| home, about, piede, 404, how-we-check | "ten states" scritto a mano | numero di Stati calcolato (`N_ST_P` = "eleven"), elenco degli Stati da `ORDINE_STATI` | | |

Nuove pagine: `/pennsylvania/` + 6 celle; `/car-accident/` "Car Accident Statute of Limitations by State (11 States)" (statute of limitations
auto accident 4.400, ... for car accident 3.600, car accident statute of limitations 2.400); `/credit-card-debt/` "Statute of Limitations on
Credit Card Debt by State" (statute of limitations on credit card debt 1.600; florida 590, california 390, texas 260). Pagine: 79 → 88.

**Pennsylvania (6 celle nuove, unico Stato scoperto con fonte leggibile).** Fonti lette il 13/11 con curl, HTTP 200, nessun blocco: Title 42 Pa.C.S.
su `legis.state.pa.us/WU01/LI/LI/CT/HTM/42/00.055.0xx.000..HTM` (Pennsylvania General Assembly) e MCARE Act (Act 13 of 2002) dal testo che
la pagina ufficiale `palegis.us` carica nel suo iframe (stesso indirizzo con `iFrame=true`; il link per i lettori è la pagina normale). 10 fonti
nuove (91 in tutto): `pa_5524`, `pa_5525`, `pa_5529`, `pa_5502`, `pa_5522`, `pa_5532`, `pa_5533`, `pa_5535`, `pa_8301`, `pa_mcare`.

| Cella | Periodo/i | Citazione (frase riletta da `verifica.py`) | Decorrenza | Eccezioni citate |
|---|---|---|---|---|
| PA/personal-injury | 2 anni | § 5524(2) "must be commenced within two years" | § 5502(a) "from the time the cause of action accrued" | § 5524(1) assault/battery (stessi 2 anni), § 5524(8) amianto, § 5535(a)(2)(i) niente anno extra |
| PA/medical-malpractice | 2 anni + limite massimo 7 | § 5524(2); MCARE § 513(a) "after seven years from the date of the alleged tort" | § 5502(a) | § 513(b) corpo estraneo, § 513(c) minori (7 anni o 20 anni d'età), § 513(d) morte: 2 anni dalla morte |
| PA/wrongful-death | 2 anni | § 5524(2) ("or for the death of an individual") | § 5502(a); il calcolatore conta dalla data inserita (morte) e lo dice | § 8301(a)-(b) chi beneficia, MCARE § 513(d) |
| PA/debt | 4 / 4 / 4 anni | § 5525(a)(8) scritti, (a)(3) orali, (a)(7) titoli | § 5502(a) | (a)(7) a vista: dalla richiesta o dall'ultimo pagamento; § 5529(b)(1) sotto sigillo 20 anni; Regulation F |
| PA/breach-of-contract | 4 / 4 anni | § 5525(a)(8), (a)(3) | § 5502(a) | § 5525(a)(1)-(2) beni e UCC, (a)(4) contratti impliciti, § 5529(b)(1) |
| PA/property-damage | 2 / 2 / 2 anni | § 5524(3) cose mobili, (4) immobili, (7) altri danni (anche "deceit or fraud") | § 5502(a) | – |

Regole dello Stato: minori § 5533(b)(1) (citato senza la parte (2) sugli abusi, tema escluso), insanity/imprisonment § 5533(a), assenza o nome
falso § 5532, sospensione § 5535(b). Enti pubblici: § 5522(a) dichiarazione scritta entro sei mesi (con la scusa ragionevole), § 5522(b)(1)
azioni contro funzionari sei mesi. Calcolatore: dati generati da `norme.py` come per le altre celle; 7 casi PA calcolati a mano in `verifica.py`
(29/2, MCARE 2020-02-29 → 2027-02-28). **Interpretazione dichiarata in pagina:** la colpa medica usa la sezione generale § 5524(2) ("that is our
reading of the statute, not a quoted rule"); il limite di 7 anni è citato dal MCARE. Il codice dello Stato è scritto "Pa.C.S. Title 42": la
forma "Pennsylvania Consolidated Statutes" fa scattare la parola vietata "consolidat" (pensata per i debiti) di `verifica.py`.

**Stati e cause non aggiunti (domanda ≥ 300 ma fonte non leggibile, nessun blocco aggirato):** California (leginfo.legislature.ca.gov) e New York
(nysenate.gov) rispondono 403 con la pagina di controllo anti-robot "Just a moment..." (riprovato il 13/11); l'API del Senato di New York
risponde 401 senza chiave. Illinois (ilga.gov): errore di certificato TLS ("unable to get local issuer certificate"), non aggirato. Georgia
(legis.ga.gov): pagina JavaScript di 1,5 KB, nessun testo di legge con curl. New Jersey: solo "new jersey statute of limitations" 1.600, le celle
non sono nel database; non provato oltre. Cause nuove: "fraud statute of limitations" 1.900 (TX 320, FL 320, CA 720) è la prossima candidata
(in Pennsylvania § 5524(7) nomina "deceit or fraud": letto; gli altri Stati non letti); defamation 720, wrongful termination 1.000: non costruite
(una colonna nuova vuol dire 11 celle, oltre il tetto di ~12 celle già usato in parte per la Pennsylvania).

**Viste (nessuna cella nuova, solo termini già letti):** `/car-accident/` mette affiancati lesioni, danni al veicolo (escluse le varianti per
terreni ed edifici: etichette con "real property/real estate") e morte, con la frase "Matching a crash to these periods is our reading of the
statutes, not a quoted rule", la citazione del termine per lesioni di ogni Stato, il rimando ai preavvisi agli enti pubblici e la modifica della
Florida del 2023. `/credit-card-debt/` mostra tutte le varianti dei debiti; "names credit cards" è calcolato dalle citazioni (solo l'Arizona,
§ 12-548(A)(2); controllato anche sui file grezzi: "credit card" compare solo in az_12_548 e in tx_fin392, che non è una norma sulla
prescrizione); nota "termine scaduto non vuol dire debito cancellato" e Regulation F come le pagine debiti. Collegamenti dalle pagine causa, dalle
celle lesioni/danni/morte/debiti e dalla griglia della home.

**FAQ: 24 → 35** (11 nuove, ognuna da una frase misurata con il suo volume nel campo `volume`; risposte solo con segnaposto di `norme.py`, nuovo
segnaposto `{R:STATO/causa}` per il limite massimo e `{NST}` per il numero di Stati): home "How long is the statute of limitations?" (2.900) ·
Texas "What is the statute of limitations in Texas?" (880) · Florida "What are the statutes of limitations in Florida?" (390) · Ohio (260) ·
Michigan (210) · Pennsylvania "... in Pennsylvania (PA)?" (210) · PA/debt (720) · PA/medical-malpractice (390) · PA/personal-injury (320) ·
car-accident "What is the statute of limitations for a car accident?" (2.400) · credit-card-debt "What is the statute of limitations for credit
card debt?" (1.600). Le 3 FAQ con l'elenco degli Stati (debt, personal injury, medical malpractice) ora includono la Pennsylvania e "{NST}".

**`verifica.py` (nuovo):** FAQ con `volume` = volume nel file misurato (frase o simile); 6b: ogni frase misurata ≥ 100 al mese che riguarda una
pagina (Stato, causa, Stato × causa, vista, home "by state"/"calculator"; escluse lemon law, Stati e cause non coperti) ha tutte le sue parole nel
titolo della pagina (100 frasi); la frase "only Arizona names credit cards" ricalcolata dalle citazioni; pagina carte di credito nei controlli
debiti; 7 casi PA a mano; browser anche su `/pennsylvania/medical-malpractice/` e `/car-accident/`. `genera.py`: il numero di celle atteso è
calcolato (Stati × cause − assenti) invece di 59 fisso.

**Controlli del 13/11 sera:** `python3 limits/genera.py` → 88 pagine + 404, 65 celle; `python3 limits/verifica.py --browser` → 0 errori, 0 avvisi
(91 fonti, 113 periodi riletti, 1.467 cifre nelle pagine, 617 citazioni parola per parola, 823 casi del calcolatore JS = Python, 43 a mano,
35 FAQ, 100 frasi misurate nei titoli, 7 pagine × 375/1280 × chiaro/scuro); `python3 studio-business/strumenti/monetizzazione.py verifica limits`
→ 0 errori; il grep del prefisso della chiave su `limits/` è vuoto.

**Dubbi per il revisore indipendente:** (1) Pennsylvania colpa medica: § 5524(2) come termine generale è una lettura nostra (dichiarata); (2) PA
wrongful death: § 5524 non dice quando decorre, il calcolatore conta dalla data della morte inserita (detto in pagina); (3) PA debiti: il
link "official text" porta a `legis.state.pa.us` (pagina HTML del General Assembly), il MCARE a `palegis.us`; (4) vista car accident: la scelta di
togliere le varianti per immobili dalla colonna del veicolo è meccanica (etichetta); (5) titoli delle celle: le tre forme della ricerca hanno lo
stesso volume, la scelta "<Stato> Statute of Limitations for <causa>" segue la frase dello Stato (6.600 per il Texas); (6) pubblicare solo dopo
la revisione (crediti Netlify) e poi IndexNow per le 9 pagine nuove.

## Revisione indipendente della crescita del 13/11 sera (fatta la notte del 13/11/2026; NON committato)

Fonti rilette dal revisore: le 10 pagine della Pennsylvania riscaricate (byte per byte uguali ai file salvati). Nota: `legis.state.pa.us` e
`palegis.us` rispondono 403 al nome predefinito di curl e 200 a un nome che si dichiara programma (come quello di `raccolta/fonti.py`):
nessuna pagina di controllo anti-robot aggirata. Tutte le citazioni della Pennsylvania coincidono parola per parola.

**Errori trovati e corretti (tutti in `norme.py`, `dati/faq.json`, `genera.py`, `stile.py`, `verifica.py`, `raccolta/fonti.py`):**
1. **MCARE § 513(a), limite di sette anni: dichiarato incostituzionale** dalla Corte Suprema della Pennsylvania (Yanakos v. UPMC, 218 A.3d
   1214, 2019). Il testo ufficiale dell'Act non porta nessuna nota, quindi la pagina lo dava come limite in vigore. Ora: stesso schema di
   Washington (limite mostrato "as printed" con avviso nel riquadro in alto, sotto la citazione, nell'esempio, nel risultato del calcolatore,
   nella tabella di confronto con asterisco, nelle FAQ PA e PA/medical-malpractice) e citazione testuale della Corte da fonte ufficiale
   nuova `pa_reibenstein` (Reibenstein v. Barax, 12/12/2022, nota 58, pacourts.us). Le eccezioni § 513(b)-(c) sono dette "as printed".
   Lo stesso avviso ora compare anche per Washington nei punti dove prima mancava (riquadro, sotto la citazione, tabella, esempio).
2. **Titoli negoziabili: sei anni nel Commercial Code** (13 Pa.C.S. § 3118(a)-(b), fonte nuova `pa_13_3118`, letta su palegis.us). La
   variante "Note or similar written instrument: 4 years" (§ 5525(a)(7)) ora porta la nota e un'eccezione citata; FAQ PA/debt aggiornata.
3. § 5522(a): aggiunte le regole (a)(3)(ii)-(iii) per gli enti diversi dal Commonwealth (notizia effettiva, morte). § 5532: citata anche la
   prima frase. § 5529(b)(1): detto che § 5525(a)(8) elenca anche gli scritti "under seal or otherwise" a quattro anni. § 5524(8): riportata
   la nota ufficiale sull'Act 152 del 2004 (Commonwealth v. Neiman).
4. `/car-accident/`: tolta la frase "No statute in these eleven states has a section for car accidents" (falsa: Mass. c. 260 § 4 e Va.
   § 8.01-243(E) nominano i veicoli); ora "The limitations statutes quoted on this site do not set one deadline…", FAQ con "our reading".
5. `/credit-card-debt/`: "only Arizona" ora limitato a "the limitations sections quoted on this site" (controllato: "credit card" compare
   solo in az_12_548 e tx_fin392); note delle varianti sotto la tabella.
6. FAQ Florida: "Section 95.051 lists the only reasons" corretto con il testo di § 95.051(2) (anche § 95.091, Probate Code, Guardianship Law).
7. Risultato del calcolatore: la frase "Many exceptions do not extend past this date" non compare più quando il limite è dichiarato
   incostituzionale. Etichetta "march" minuscola nella vista car accident corretta.

Letture del costruttore giudicate corrette e lasciate come interpretazione dichiarata: § 5524(2) per la colpa medica; morte contata dalla
data inserita; § 5525(a)(8) scritti e (a)(3) orali; titoli a vista (a)(7). Controlli: 93 fonti, 0 errori, 0 avvisi; 15 casi PA a mano in
node: 15 giusti; 89 titoli e descrizioni unici, ≤ 65 / ≤ 160; 79 URL vecchi tutti presenti; 35 FAQ JSON-LD = testo visibile.
Da sapere: 18 celle hanno il titolo senza "(N Years)" perché supererebbe i 65 caratteri.
