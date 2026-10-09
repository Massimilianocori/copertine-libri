## ONLINE dal 10/10/2026 su https://esamidistato.netlify.app
- Progetto Netlify **esamidistato**: site id `daea196d-6628-4035-8e5f-0e7e0980db78`, moduli attivi, form `avvisami` id `6ac969aacc2e230008015795` (prova d'invio riuscita e cancellata).
- Pubblicazione automatica da GitHub: branch `ccr-b7fd6b9e-n096cr`, base/publish `esamidistato/sito` (regola `ignore` nel netlify.toml).
- Da fare: notifica email del modulo (Massimiliano), Search Console (tag HTML → costante `GOOGLE_VERIFICA` in `genera.py`), routine settimanale.

# EsamiDiStato — note di costruzione

## Stato (9 ottobre 2026): Fase 1 costruita, NON ancora pubblicata
- Sito statico in `esamidistato/sito/` (46 pagine), generato da `python3 esamidistato/genera.py`.
- Zip per Netlify Drop: `esamidistato-sito.zip` (nello scratchpad della sessione; si rigenera zippando il contenuto di `esamidistato/sito/`).
- Momento giusto: la scadenza delle domande per la **seconda sessione 2026 è il 21 ottobre 2026** (12 giorni da oggi); avvocato fino all'11 novembre.

## Cosa c'è
- **19 professioni**: 9 dell'OM 694 (ingegnere, architetto, psicologo, biologo, geologo, chimico, agronomo e forestale, assistente sociale, attuario),
  5 dell'OM 693 (farmacista, odontoiatra, veterinario, fisico, tecnologo alimentare), commercialista ed esperto contabile (OM 692),
  geometra, perito agrario, agrotecnico (OM MIM 76-77-78) e avvocato (decreto Giustizia 3/9/2026).
- **12 sessioni** in `dati/sessioni.json` (7 future al 9/10/2026): prima sessione MUR (27 e 31 luglio, domande entro 24 giugno, già svolta),
  seconda sessione MUR (16 novembre sezione A / 20 novembre sezione B e iunior, domande entro 21 ottobre), MIM (scritti 18-19 novembre,
  domande chiuse il 15 giugno), avvocato (scritti 15-16 dicembre, domande online 1° ottobre – 11 novembre).
- **102 sedi** in `dati/sedi.json`: 75 sedi universitarie (67 università; la stessa università può avere sedi in più città, per es. Bologna a Cesena e Forlì)
  + 27 Corti di appello (26 + sezione di Bolzano). Conteggi per professione uguali alle tabelle: ingegnere 39, architetto 25, psicologo 22,
  commercialista 59, biologo 36, assistente sociale 35, farmacista 33, odontoiatra 31, chimico 27, geologo 23, agronomo 22, tecnologo alimentare 19,
  veterinario 13, fisico 9, attuario 3, avvocato 27. Provincia e regione da ISTAT. Sito ufficiale per tutte le università tranne due (vedi sotto) e pagina
  "esami di Stato" trovata in automatico per 33 nomi di ateneo (link verificati HTTP 200 il 9/10/2026).
- Pagine: home (calendario con filtro per professione, prossima scadenza in evidenza, griglie professioni e città, FAQ), 19 pagine professione
  (date, in breve: domanda, costo, sede in tedesco, note, atto ufficiale; sedi per regione), 24 pagine città (Milano, Roma, Torino, Napoli, Bologna,
  Firenze, Genova, Bari, Palermo, Catania, Verona, Padova, Brescia, Venezia, Bergamo, Modena, Parma, Pisa, Perugia, Cagliari, Trieste, Salerno,
  Messina, Pavia: tabella professione → sede, sedi, professioni mancanti con le sedi nella stessa regione, date), Come funziona, privacy, 404.
- Modulo Netlify `avvisami`: email, professione, città, consenso, honeypot, `source` (da `?ref=`), invio AJAX come EsameB1. JSON-LD `EducationEvent`.
- Verifiche fatte: generazione senza errori; 2.802 link interni senza rotture; Playwright (desktop e 375 px) su home, ingegnere, psicologo, avvocato,
  geometra, Milano, Napoli, Come funziona, privacy, 404: nessun errore in console, nessuno scroll orizzontale (controllate tutte le 46 pagine a 375 px),
  filtro ok, modulo bloccato se vuoto e inviato con risposta simulata.

## Fonti (scaricate e lette il 9/10/2026)
- MUR, pagina esami di Stato: https://www.mur.gov.it/it/aree-tematiche/universita/professioni/esami-di-stato (raggiungibile dallo script: nessun blocco).
- OM 694, 693, 692 del 27/5/2026 (PDF sul sito MUR, letti con pdfplumber; testi in `dati/fonti/om69x-2026.txt`).
- MIM OM 76/77/78 del 9/5/2026: **non presi dal sito MIM** ma dalla copia ufficiale dell'Ufficio scolastico regionale del Veneto
  (https://istruzioneveneto.gov.it/20260513_41372/), termine del 15/6/2026 dalla nota USR Veneto del 13/5/2026 (testi in `dati/fonti/`).
- Avvocato: decreto 3/9/2026 e scheda di sintesi su giustizia.it (testi in `dati/fonti/`). Fonte semplice (date nazionali, elenco delle Corti), quindi incluso.

## Cosa manca / da fare
- **Percentuali di abilitati per ateneo**: TODO della fase 2 (servono gli elenchi di ~60 atenei; contare, non copiare i nomi).
- **Date 2027**: non ancora pubblicate (controllato il 9/10/2026); di solito le ordinanze MUR escono tra aprile e giugno. `raccogli.py` segnala se la pagina MUR cambia.
- **Medico**: non compare nelle ordinanze MUR 2026 (detto in pagina). **Perito industriale**: ordinanza 2026 non trovata, escluso.
- Geometra, perito agrario, agrotecnico: nessun elenco di sedi (la Tabella A delle ordinanze MIM elenca gli istituti disponibili, le commissioni
  si decidono dopo); domande già chiuse. Da aggiungere il provvedimento con le sedi delle commissioni se lo troviamo.
- Pagina "esami di Stato" non trovata per 35 nomi di ateneo (link solo alla home); Politecnico di Bari e Parthenope senza sito (certificato non verificabile da qui).
- Bandi dei singoli atenei (scadenze interne, contributi, calendari delle prove scritte): non raccolti in questa fase.
- Aggiornamento: `python3 esamidistato/raccolta/raccogli.py` → se "PAGINE UFFICIALI CAMBIATE" aggiornare `dati/sessioni.json` a mano con fonte →
  `python3 esamidistato/genera.py` → commit e push (al massimo un push del sito a settimana, per i crediti Netlify).

## Test (45 giorni dalla pubblicazione) — soglie uguali a EsameB1
- **Continua** se: ≥20 pagine indicizzate, ≥300 clic da Google, ≥100 iscritti, almeno 5 pagine (professione o città) tra i primi 20 risultati.
- **Rivedi** (domanda c'è ma non converte) se l'indicizzazione è ok ma gli iscritti sono <40.
- **Stop** se <100 clic e <20 iscritti.
- Il conteggio parte dalla pubblicazione e dal collegamento a Search Console. Attenzione alla stagionalità: dopo il 21 ottobre la ricerca cala
  fino alle ordinanze 2027 (primavera); gli iscritti di adesso sono quelli da avvisare allora.

## Istruzioni per Massimiliano
1. **Pubblicare** (scegli una strada):
   - *Netlify Drop*: apri https://app.netlify.com/drop e trascina lo zip `esamidistato-sito.zip` (o la cartella `esamidistato/sito`).
     Poi in Site configuration → Change site name scegli `esamidistato` (se il nome è preso, dimmelo: cambio `URL_SITO` in `genera.py`).
   - *Collegamento GitHub* (aggiornamenti automatici): Add new site → Import from Git → repository `copertine-libri`, branch `ccr-b7fd6b9e-n096cr`,
     **Base directory `esamidistato/sito`, Publish directory `esamidistato/sito`**, build command vuoto. La regola `ignore` del `netlify.toml`
     pubblica solo quando cambia `esamidistato/sito`.
2. **Modulo**: Project configuration → Forms → abilita il rilevamento dei moduli; poi Forms → `avvisami` → Form notifications → Add notification → Email.
   Fai una prova di invio e cancellala.
3. **Search Console**: aggiungi la proprietà `https://esamidistato.netlify.app` con il metodo "tag HTML" e mandami il codice: lo metto in
   `GOOGLE_VERIFICA` in `genera.py` e ripubblico; poi invia `sitemap.xml`.
4. Nessuna spesa: niente dominio finché il test non dice "continua".
