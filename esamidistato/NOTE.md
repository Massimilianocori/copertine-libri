## ONLINE dal 10/10/2026 su https://esamidistato.netlify.app
- Progetto Netlify **esamidistato**: site id `daea196d-6628-4035-8e5f-0e7e0980db78`, moduli attivi, form `avvisami` id `6ac969aacc2e230008015795` (prova d'invio riuscita e cancellata).
- Pubblicazione automatica da GitHub: branch `ccr-b7fd6b9e-n096cr`, base/publish `esamidistato/sito` (regola `ignore` nel netlify.toml).
- **Search Console verificata e sitemap inviata il 10/10/2026** (costante `GOOGLE_VERIFICA` in `genera.py`, non rimuoverla).
- **Routine settimanale** condivisa con EsameB1: `trig_017HFNXZX5fKYcerETVg5zq4` (lunedì 7:59 ora italiana).
- **Test a 45 giorni: verdetto il 24/11/2026.**

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

## Grafica (11/10/2026)
- EsamiDiStato: blu notte istituzionale, bordeaux per le scadenze, filo d'oro; marchio a frontone classico; titoli in Source Serif 4.
- Identità propria del sito, tutta in `genera.py` (CSS con token su `:root`, chiaro/scuro automatico, icone SVG in linea con uno sprite per pagina, marchio SVG nel logo e nel favicon).
- In cima a home, pagine città/professione: scheda "risposta" con prossimo esame e prossima scadenza ancora aperta; il JS nasconde le voci scadute, quindi resta giusta anche tra un aggiornamento e l'altro.
- Font servito dal sito (`assets/fonts/`, licenza SIL OFL in `OFL.txt`, copiato in `sito/fonts/`): nessuna risorsa esterna.
- Immagine Open Graph 1200x630: `assets/og.png`, generata con Playwright da `assets/og-template.html` (istruzioni nel file).
- Moduli `avvisami`, titoli, description, canonical, h1, JSON-LD e URL invariati.

## Revisione design (11/10/2026)
- Scuro: bottoni e date in oro (`--brand:#E9C977`), il periwinkle resta solo per i link; campanella del modulo oro su blu notte in entrambi i temi.
- Schede sessione: al massimo 2 professioni + "+N professioni" (si espande), la sessione è testo nella riga della data; col filtro si vede solo la professione scelta, evidenziata. Nota della scadenza comune detta una volta in testa all'elenco.
- Filtro professione: menu a tendina "Professione" con conteggio dei risultati (aria-live).
- Pagine professione: sedi a tutta larghezza in due colonne, raggruppate per regione e già aperte. Colonna laterale "sticky" con il solo modulo.

## Collegamenti tra siti (19/10/2026)
- In fondo a ogni pagina, blocco "Altri strumenti utili" con il link alla home di EsameB1 e una riga di descrizione (costante `ALTRI_SITI` in `genera.py`). Deciso nel cruscotto (sez. 6, riga 19/10), uscito con la pubblicazione settimanale.

## IndexNow (26/10/2026)
- IndexNow: file chiave scritto dal generatore; invio con studio-business/strumenti/indexnow.py. Costante `CHIAVE_INDEXNOW` in `genera.py` accanto a `SCRIPT_CONTATORE` (chiave pubblica, uguale in tutti i siti della rete); `extra()` scrive `sito/<chiave>.txt` accanto a `robots.txt`, fuori dalla sitemap e non linkato.
- Blocco «Altri strumenti utili»: aggiunta come seconda voce (`ALTRI_SITI` in `genera.py`) il link a Italy Strikes Today in italiano, `https://italy-strikes-today.netlify.app/it/`, testo «Scioperi dei trasporti in Italia oggi e domani» e descrizione «treni, aerei e mezzi pubblici, dal registro ufficiale del Ministero»; link normale `rel="noopener"`, stesso stile della voce esistente.

## Monetizzazione: come si attiva (30/10/2026)
- **Dove si scrive:** un solo file per tutta la rete, `studio-business/strumenti/monetizzazione.json` (`adsense_client`, `adsense_siti`, domini di affiliazione ammessi). In una riga: `python3 studio-business/strumenti/monetizzazione.py attiva ca-pub-XXXXXXXXXXXXXXXX esamidistato`, poi `python3 esamidistato/genera.py`. Il nome del sito nel file è `esamidistato` (`SITO_ID` in `genera.py`).
- **Cosa cambia con AdSense acceso:** script ufficiale nel `<head>` di ogni pagina (annunci automatici, nessun blocco manuale), `sito/ads.txt` con `google.com, pub-…, DIRECT, f08c47fec0942fa0`, sezione «Pubblicità (Google AdSense)» in `privacy.html`; la frase sui cookie diventa «GoatCounter non usa cookie, la pubblicità sì». Prima di pubblicare: in AdSense accendere il messaggio di consenso certificato di Google (Privacy e messaggi, regolamenti europei: UE/SEE, Regno Unito, Svizzera), che la privacy descrive.
- **Link di affiliazione:** `dati/affiliati.json` (dal 30/10/2026: libri Amazon.it, vedi sotto). Ammessi solo verso i domini di `domini_affiliazione`, con `rel="sponsored noopener"` e la riga di trasparenza (la aggiunge `riquadro_trasparenza()` se manca); con almeno un link la privacy aggiunge la sezione sui link di affiliazione.
- **Come si verifica:** nessun `verifica.py`: `python3 studio-business/strumenti/monetizzazione.py verifica esamidistato`; controllo comune in `monetizzazione.py` (script e `ads.txt` solo con AdSense acceso, privacy coerente, nessun dominio fuori elenco o bloccato, Amazon.it solo con `tag=`).
- **Con il codice vuoto o il sito fuori elenco l'output non cambia:** il 30/10/2026 `sito/` è stato rigenerato identico byte per byte.

## Manuali su Amazon.it (30/10/2026)
- Programma di Affiliazione Amazon EU, ID negozio **`guideesami-21`** (5 % sui libri; Amazon esamina l'account dopo 3 vendite in 180 giorni). Nuovo file `dati/affiliati.json`, voce `amazon`: `url` (ricerca generale della home), `tag`, `ricerche` (parole chiave per ogni slug di `professioni.json`; se ne manca una la generazione si ferma).
- Riquadro sobrio **«Manuali per prepararsi»** (`riquadro_manuali()` in `genera.py`, classe `.manuali`, bordo sinistro oro): 19 pagine professione (colonna sinistra, subito dopo «In breve») e home (in fondo alla sezione Professioni). Due frasi semplici (manuale aggiornato e tracce degli anni passati; controllare edizione e professione), un link a una ricerca nel reparto Libri di amazon.it, `rel="sponsored noopener"`, `target="_blank"`, la frase «In qualità di Affiliato Amazon, ricevo un guadagno dagli acquisti idonei.» e la riga di trasparenza della rete. Mai in città, Come funziona, privacy, 404.
- URL: `https://www.amazon.it/s?k=<parole>&i=stripbooks&tag=guideesami-21`. Home: `esame di stato abilitazione manuale`. Professioni: `esame di stato <professione> manuale` per ingegnere, architetto, psicologo, biologo, assistente sociale, commercialista, farmacista, geometra; senza «manuale» (pochi titoli) per geologo, chimico, agronomo, attuario, veterinario, fisico, tecnologo alimentare, perito agrario, agrotecnico; `esame di stato odontoiatria`; `esame avvocato manuale`.
- Parole chiave scelte a mano: il 30/10/2026 amazon.it risponde 503 alla ricerca e con la pagina anti-robot alle schede `/dp/`, quindi nessun risultato controllato e nessun libro singolo linkato. Da rivedere a mano dal browser (se una ricerca dà libri non pertinenti, cambiare `ricerche.<slug>` e rigenerare).
- Regole Amazon: niente prezzi, niente recensioni o stelle, link non nascosti, mai link Amazon in email o PDF.
- Privacy: con la voce `amazon` attiva compaiono la sezione comune «Link di affiliazione» (da `monetizzazione.py`) e la sezione «Programma di Affiliazione Amazon» («Partecipiamo al Programma di Affiliazione Amazon EU…», costante `PRIVACY_AMAZON`). Per spegnere tutto: `url` vuoto e rigenerare.
- Verifica: `monetizzazione.py verifica esamidistato` → 20 link di affiliazione in 20 pagine su 47, 0 errori; Playwright su home e ingegnere a 375 e 1280 px, chiaro e scuro: nessun errore JS, nessuno scorrimento orizzontale. Nessun commit.
