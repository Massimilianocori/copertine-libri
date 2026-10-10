# Italy Strikes Today — note di costruzione

## Stato (10 ottobre 2026): ONLINE su https://italy-strikes-today.netlify.app
- Sito statico in `italystrikes/sito/` (53 pagine + 404), generato da `python3 italystrikes/genera.py`. Indirizzo previsto: **https://italy-strikes-today.netlify.app** (libero il 10/10/2026). Se Netlify dà un altro nome, cambiare `URL_SITO` in `genera.py` e rigenerare.
- `italystrikes.netlify.app` è **già occupato** da un concorrente ("Italy Transport Strikes"): una pagina sola che carica i dati dal registro solo premendo un pulsante, senza sitemap né pagine per città/data. Google vede poco o nulla del suo contenuto.
- Da fare con Massimiliano: progetto Netlify, moduli, Search Console (vedi "Cosa deve fare Massimiliano"); permesso per il file di aggiornamento automatico su `main` (vedi sotto).

## Cosa c'è
- `raccolta/raccogli.py`: legge RSS e prospetto HTML del registro MIT, unisce per id MIT (guid RSS; la colonna Note c'è solo nell'HTML e si abbina per contenuto), aggiorna `dati/scioperi.json` (storico nostro con la cronologia di ogni sciopero; correzione del 10/10/2026: il prospetto principale del registro mostra solo gli scioperi futuri, ma il MIT ha anche una ricerca storica dal 2014 con stato Effettuato/Revocato; i dati sono con licenza CC BY 4.0 e la citazione è nel piè di pagina EN/IT e nella pagina About) e `dati/registro.json`. Stati: in programma / concluso / rimosso dal registro (mai presentato come revoca certa) / revocato (solo se la nota lo dice). Copia dell'RSS in `dati/fonti/` solo quando cambia, 30 giorni. Se il registro non risponde o cambia formato esce con errore senza toccare i dati. Provato: due esecuzioni di fila senza cambiamenti; simulazione di uno sciopero sparito → "rimosso dal registro".
- `genera.py`: traduce ogni sciopero in inglese con regole fisse (settore, ambito, dove, operatore da `dati/operatori.json`, orari: se la traduzione lascia parole italiane si mostra solo l'originale), decide città/aeroporti/settori coinvolti, scrive `dati/vista.json` e il sito. Scioperi generali: tutti i trasporti passeggeri salvo esclusioni nella nota; plurisettoriali: solo i settori nominati; cargo aereo spostato tra le merci; aeroporto specifico se la categoria lo nomina.
- Pagine: home (oggi/domani/settimana, prossimi 30 giorni con filtro), today, tomorrow, this-week, next-week, 5 mesi (ottobre 2026 – febbraio 2027, crescono da soli), 8 settori, 15 città, indice aeroporti + 9 aeroporti (aggiunto Firenze), 7 guide + indice, about, contact (modulo `contact`), privacy, 404, sitemap, robots, netlify.toml. Spazi vuoti per la pubblicità (`.ad-slot`, invisibili finché vuoti).
- Il JS ricalcola oggi/domani/settimana nel browser con l'ora di Roma e scarica `dati/vista.json` da raw.githubusercontent.com (CORS aperto, cache 5 minuti): le pagine restano giuste anche tra una pubblicazione e l'altra.
- `dati/link.json`: link ufficiali verificati il 10/10/2026 (status "200" dal server; "browser" = dominio ufficiale trovato con la ricerca ma che blocca le richieste automatiche: ATAC, aeroporti di Roma, Bergamo, Venezia, Napoli, Pisa). cgsse.it irraggiungibile dal server: non linkato. Firenze aeroporto: nessun link verificato.
- Fasce orarie nelle guide verificate sulle pagine ufficiali il 10/10/2026: Trenitalia regionali 6-9 e 18-21 feriali, 7-10 e 18-21 festivi, regola dell'ora per i treni in viaggio; voli 7-10 e 18-21 (ENAC).
- Verifiche fatte: Playwright desktop e 375 px su 21 pagine (nessun errore JS, nessuno scroll orizzontale), filtri, modulo (vuoto bloccato, date invertite bloccate, errore mostrato, invio riuscito con risposta simulata), data finta 16/10/2026 (oggi = 5 scioperi giusti), 1.479 link interni senza rotture.

## Scelte fatte (diverse dalle istruzioni)
- **Niente dati strutturati `Event`** per gli scioperi: le linee guida di Google li riservano a eventi a cui si partecipa; uno sciopero marcato come evento rischia un'azione manuale. Restano `WebSite` e `BreadcrumbList`.
- **Nessuna pagina per singolo sciopero** in Fase 1 (sarebbero pagine sottili); ogni sciopero ha un'ancora `#sNNNN` nelle liste.
- **AdSense non richiede un dominio**: netlify.app è nella Public Suffix List, e AdSense accetta come sito un sottodominio di una piattaforma in quella lista (support.google.com/adsense/answer/12170421, letto il 10/10/2026). Il dominio da 10-15 € non serve per la pubblicità.

## Crediti Netlify (vincolo importante)
- Piano gratuito a crediti: **300 crediti al mese, limite rigido**; ogni pubblicazione in produzione **15 crediti** (da Git, API o CLI è uguale); banda 20 crediti/GB; richieste 2 crediti/10.000; moduli gratis. **Se i crediti finiscono, tutti i progetti dell'account vanno offline fino al mese dopo** (docs.netlify.com, billing for credit-based plans, letto il 10/10/2026). L'account ha 6 progetti (team creato il 9/7/2026).
- Bilancio: EsameB1 + EsamiDiStato ~1 pubblicazione a settimana ciascuno ≈ 9 al mese ≈ 135 crediti; Italy Strikes **al massimo 6 al mese** ≈ 90 crediti; restano ~75 crediti per banda e imprevisti.
- Regola applicata da `raccolta/decidi_deploy.py` (stato in `dati/deploy.json`): una pubblicazione a settimana; una in più (dopo almeno 2 giorni) se cambia uno sciopero passeggeri nazionale o di una città/aeroporto del sito nei prossimi 21 giorni; mai più di 6 nel mese solare. Tra una pubblicazione e l'altra i dati arrivano dal JSON su GitHub.
- Se il sito cresce (banda > ~2 GB al mese) i crediti non bastano: a quel punto si valuta il piano Personal (9 $/mese, 1.000 crediti) con il sì di Massimiliano, pagato dai ricavi.

## Aggiornamento automatico
- `italystrikes/workflow/italystrikes.yml` è il file GitHub Actions pronto: due volte al giorno (07:17 e 17:17 ora italiana) legge il registro, aggiorna `dati/`, decide se ripubblicare e fa commit e push sul branch `ccr-b7fd6b9e-n096cr`.
- **ATTIVO dal 10/10/2026**: Massimiliano ha aggiunto lui stesso `.github/workflows/italystrikes.yml` su `main` (i workflow programmati partono solo da lì; il filtro di sicurezza della sessione impedisce a Claude di farlo). Prima esecuzione manuale riuscita il 10/10/2026 alle 16:35: commit del bot "Italy strikes: registro del 10/10/2026 (pubblicazione: no)". Se si modifica il workflow, aggiornare sia la copia in `italystrikes/workflow/` sia quella su `main` (quest'ultima a mano da GitHub).
- Se il workflow si ferma: la routine settimanale `trig_017HFNXZX5fKYcerETVg5zq4` (lunedì) aggiorna i dati e controlla il workflow. Con un solo aggiornamento a settimana gli scioperi nuovi compaiono comunque prima della data (preavviso minimo 10 giorni), ma le revoche possono arrivare in ritardo.

## Mancano / da fare
- **Versione italiana ACCESA (sì di Massimiliano il 10/10/2026)**: `genera_it.py`, interruttore `VERSIONE_IT_ATTIVA = True` in `genera.py`; esce con la pubblicazione settimanale decisa da `decidi_deploy.py` (17/10). Sezione `/it/` dello stesso sito (stesse pubblicazioni, nessun credito Netlify in più): home, oggi, domani, questa/prossima settimana, mesi (`/it/2026/novembre/`), 8 settori, **24 città** (le 15 inglesi + Bergamo, Brescia, Cagliari, Messina, Salerno, Modena, Parma, Perugia, Ancona), indice + 9 aeroporti, 2 guide (fasce di garanzia; come funzionano gli scioperi), contatti, privacy. 56 pagine; con l'inglese 111. `hreflang` it/en tra le pagine equivalenti e link "Italiano"/"English" nel menu. Il JS è quello inglese con testi e campi italiani (controllo automatico: se il JS inglese cambia, `genera_it.py` si ferma con errore invece di produrre pagine sbagliate). Nuovi campi in `vista.json`: `titolo_it`, `dove_it`, `chi_it`, `nota_it`, `ore_it`, `citta_it`; etichette italiane in `dati/operatori.json` (`it`), città e aeroporti italiani in `dati/luoghi.json`. Moduli: stessi nomi (`alerts`, `contact`). Niente riquadro affiliati sulle pagine italiane (pubblico italiano: solo pubblicità). Provato: 3.558 link senza rotture, Playwright desktop e 375 px su 11 pagine, data finta 16/10, filtri.
  - Anteprima: `ITALYSTRIKES_IT=1 python3 italystrikes/genera.py` in una copia della cartella.
- **Satelliti ACCESI (sì di Massimiliano il 10/10/2026)**: `SATELLITI_ATTIVI = True` in `genera.py`; escono alla prima pubblicazione decisa da `decidi_deploy.py` (al più tardi il 17/10, settimanale). Collegati da home, guide e sitemap (55 pagine).
  - `/codice-fiscale-calculator/`: calcolo nel browser (nessun dato inviato), paesi esteri dalla tabella 2 ANPR (Ministero dell'Interno, colonna CODAT, copia in `satelliti/fonti/`), comuni ISTAT (file `comuni.json` caricato solo se si sceglie "nato in Italia"); istruzioni ufficiali dalla pagina inglese dell'Agenzia delle Entrate; link al servizio di verifica. Dati rigenerabili con `python3 italystrikes/satelliti/prepara_cf.py`. Provato: RSSMRA80A01H501U (caso di riferimento), accenti/apostrofi, suggerimenti comuni, 375 px.
  - `/ztl-fines/`: solo regole nazionali verificate sul testo del Codice della Strada (Normattiva, estratti in `satelliti/fonti/cds-art*.txt`): 83-332 € (art. 7 c. 14), minimo entro 60 giorni e -30 % entro 5 (art. 202), notifica entro 360 giorni per i residenti all'estero (art. 201). Orari delle singole città NON copiati (fonti ufficiali non leggibili dal server, fonti secondarie in contraddizione): link ufficiali solo per Roma, Milano, Bologna.
  - Anteprima: `ITALYSTRIKES_SATELLITI=1 python3 italystrikes/genera.py` in una copia della cartella (non nella cartella vera: cambierebbe `sito/`).
- **Affiliazione (decisa il 10/10)**: riquadro "Stuck by a strike? Alternatives" in `genera.py` (`box_affiliati`), su home, oggi/domani/settimane, mesi, settori, città, aeroporti; compare solo per le voci di `dati/affiliati.json` con URL. Massimiliano si iscrive (Travelpayouts: Omio, Welcome Pickups, EKTA; SafetyWing; Airalo/Impact) e manda i link; link con `rel="sponsored"` e dicitura di affiliazione. Verrà pubblicato alla prima pubblicazione utile (non sprecare un deploy solo per questo).
- **Invio degli avvisi email** agli iscritti del modulo `alerts`: da costruire quando arrivano i primi iscritti (confronto giornaliero date/luogo con `vista.json`; serve un servizio di invio gratuito o la casella Gmail di Massimiliano con il suo sì). Fino ad allora la promessa in pagina va mantenuta a mano dalla routine settimanale.
- `GOOGLE_VERIFICA` inserito il 10/10/2026 (stesso codice degli altri due siti: è legato all'account Google). Non rimuoverlo.
- AdSense: richiesta al giorno ~20 se Search Console mostra pagine indicizzate e impression in crescita. Prima: privacy con sezione pubblicità e CMP di Google per il consenso UE.
- Satelliti dopo il test: codice fiscale calculator, ZTL per città, versione italiana con lo stesso motore.

## Test (45 giorni dalla pubblicazione; Search Console, ultimi 14 giorni)
1. Pagine indicizzate ≥40 su ~53.
2. Impression ≥1.500/settimana e in crescita per 2 settimane di fila.
3. Clic totali dal giorno 1 ≥150, CTR ≥2%.
4. ≥40% dei clic da USA + Canada + UK + Australia.
5. Almeno 5 query con "today", "tomorrow" o mese+anno tra le prime 20 per impression.
6. AdSense approvato; se attivo ≥7 giorni: RPM ≥6 $.
Passano 1-4 → si continua (satelliti, versione italiana, Journey a 1.000 sessioni Tier 1/30 giorni). Fallisce 1 o 2 → stop. Fallisce solo 4 → tenere il sito e aprire la versione italiana.
Data di inizio: **10/10/2026** (pubblicato da GitHub, progetto Netlify `italy-strikes-today`, site id `c6aea0b3-93d2-4570-9351-c7120a20968e`, moduli attivati: `alerts` id `6aca421bcfef520007089e7d`, `contact` id `6aca421ccfef520007089e98`; notifica email su tutti i moduli). Verdetto a 45 giorni: **24/11/2026**.

## Cosa deve fare Massimiliano (una volta)
1. Netlify → Add new project → Import an existing project → GitHub → `copertine-libri` → branch `ccr-b7fd6b9e-n096cr`, Base directory `italystrikes/sito`, Publish directory `italystrikes/sito`, build command vuoto → Deploy. Poi Project configuration → Change project name → `italy-strikes-today`.
2. Forms → Enable form detection; poi Forms → Form notifications → email per il modulo `alerts` (e `contact`).
3. Search Console → Aggiungi proprietà "Prefisso URL" `https://italy-strikes-today.netlify.app/` → metodo **Tag HTML** → mandare il tag a Claude → dopo la pubblicazione premere Verifica → Sitemap: `sitemap.xml`.

## Guida PDF "Italy by Train: the strike-proof guide" (10/10/2026) — IN PAUSA
- **Decisione di Massimiliano del 10/10/2026: non si vende per ora** (nessuna partita IVA dedicata alla vendita di prodotti: rischio fiscale/INPS). Riaprire solo con risposta fiscale scritta favorevole e nuovo sì.
- Sorgenti in `prodotti/italy-by-train/` (`contenuto.html`, `copertina.html`, `extra.json`, `build.py`, `font/`, `fonti/`); il PDF esce in `out/` (escluso da git: il repository è pubblico, il PDF non va pubblicato qui né in `sito/`). Ricostruire: `python3 italystrikes/prodotti/italy-by-train/build.py`.
- Edizione 1, 68 pagine 6×9. Revisione indipendente dei fatti fatta il 10/10/2026, tutte le correzioni applicate (treni garantiti: Tabella A 146, Tabella B 62, letti con `fonti/leggi_tabelle.py`).
- La Tabella A Trenitalia vale fino al 12/12/2026: a dicembre scaricare le nuove tabelle, rilanciare `leggi_tabelle.py` e `build.py`, aggiornare l'edizione e mandarla agli acquirenti.
- Vendita: Payhip (account di Massimiliano). Pagina `guide/italy-by-train/` e link nel menu/riquadro compaiono solo se `dati/prodotti.json` ha l'URL Payhip. Accendere solo con il sì di Massimiliano. Soglia del test in `prodotti/ISTRUZIONI-GUIDA.md`.

## Guide gratuite nuove (10/10/2026, sì di Massimiliano: "ok")
- EN `guides/strike-free-periods/` e `guides/strike-rules-notice-duration/`; IT `it/guida/periodi-di-franchigia/` e `it/guida/regole-degli-scioperi/` (hreflang collegati con `GUIDE_EN_IT` in `genera_it.py`). Dati in `FRANCHIGIE`, `TABELLA_A` in `genera.py`; fonti in `prodotti/italy-by-train/fonti/`.
- Guide esistenti corrette con i fatti della revisione: treni garantiti (come leggere la Tabella A: il numero di treni compare solo fino al 12/12/2026; clausola Italo "non garantito"; scadenze di rimborso Trenitalia prima dello sciopero), rimborsi (regole UE e indennizzi Trenitalia/Italo), registro (ricerca storica dal 2014, campi corretti), bus e metro (due fasce, 6 ore in tutto, 20 giorni tra scioperi).
- A dicembre 2026: aggiornare `TABELLA_A` con la nuova tabella Trenitalia.
- Escono con la pubblicazione settimanale (17/10), senza crediti in più.

## Acqua alta Venezia (10/10/2026, regola di Massimiliano: "qualsiasi cosa si possa aggiungere lo si faccia se porta maggiore guadagno")
- Pagine `venice-acqua-alta/` (EN) e `it/acqua-alta-venezia/` (IT), hreflang collegati; link da home (strumenti) e pagina Venezia.
- Dati: `raccolta/maree.py` scarica la previsione ICPSM (dati.venezia.it, CC BY) in `dati/maree.json`; lo chiama `raccogli.py` alla fine (se fallisce non ferma gli scioperi), quindi si aggiorna due volte al giorno con il workflow. ATTENZIONE: senza `?t=` la fonte restituisce una copia vecchia (21/09). La pagina rilegge `maree.json` da GitHub nel browser.
- Soglie (80/110/140 cm) dalla pagina del Centro Maree del Comune, letta tramite motore di ricerca: il sito del Comune blocca i robot (403 Incapsula). Da ricontrollare se si riesce ad aprirla.
