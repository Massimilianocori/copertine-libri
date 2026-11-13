# Statute of Limitations by State – note di lavoro (13/11/2026)

Sito statico in inglese (en-US) generato da `genera.py` in `sito/`: termini di prescrizione civile ("statute of limitations") per
10 Stati × 6 cause, con il testo di legge citato parola per parola, link al sito ufficiale del parlamento, data di lettura, regole di
decorrenza e di sospensione, preavvisi per le cause contro enti pubblici, modifiche recenti e un calcolatore della scadenza generale.
Nato da `studio-business/intelaiatura/fronti-2026-11-13-prescrizione-usa.md` (prova di 60 pagine, voto 5, COSTRUIRE in coda).
Indirizzo previsto: `https://statute-limits-by-state.netlify.app` (nome libero il 13/11/2026: curl → 404; costante `URL_SITO` in
`genera.py` e `verifica.py`). **Il sito Netlify non esiste ancora** (passi in fondo). Nome: descrittivo e generico (nessun marchio).

## Pagine (79 indicizzabili + 404)

| Pagina | Contenuto |
|---|---|
| `/` | calcolatore (Stato + causa + data → data generale per ogni variante, limite massimo, elenco delle eccezioni con articolo), tabella 10 × 6, come si legge un termine, cambi recenti (Florida 2023, Ohio 2021), 5 FAQ |
| `/<stato>/` (10) | tabella delle 6 cause, calcolatore con lo Stato scelto, regole di sospensione dello Stato (citate), cause contro enti pubblici, cambi recenti |
| `/<stato>/<causa>/` (59) | termine/i con citazione, decorrenza, limite massimo (repose) se c'è, esempio calcolato, calcolatore della cella, eccezioni della causa, regole dello Stato, enti pubblici, cambi recenti se toccano la cella, confronto con gli altri 9 Stati, FAQ se c'è |
| `/<causa>/` (6) | tabella di confronto fra 10 Stati con articolo e limite massimo, calcolatore, citazione per ogni Stato; su `/debt/` la regola federale |
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
