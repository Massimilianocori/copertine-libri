# Italy Strikes Today — istruzioni di costruzione (Fase 1: test a costo zero)

Decisione del 10/10/2026: Massimiliano ha detto "sì" (studio: `studio-business/intelaiatura/7-modelli-diversi.md`, sez. 3.3 e 4.3).
Chi costruisce legge PRIMA: questo file, `studio-business/REGOLE-FISSE.md`, lo studio citato, poi `esameb1/genera.py` e `esamidistato/genera.py` (motore da riusare: stesso stile, stesso modulo Netlify, stesse regole di `netlify.toml`).

## Cosa costruiamo
Un sito **in inglese**, gratuito, che legge ogni giorno il **registro ufficiale degli scioperi del Ministero delle Infrastrutture e dei Trasporti** e risponde alle domande che i viaggiatori stranieri fanno a Google: *"Italy strike today / tomorrow"*, *"Italy train strike tomorrow"*, *"Rome transport strike"*, *"Italy strikes November 2026"*, *"Milan airport strike"*.
Modello di ricavo: **pubblicità** (AdSense, poi Journey/Mediavine se il traffico Tier 1 cresce). Nessuna vendita, nessun abbonamento in Fase 1.
Nome provvisorio: **Italy Strikes Today**; cartella `italystrikes/`; sito Netlify `italystrikes.netlify.app` (o simile, se occupato: `italy-strikes.netlify.app`). Dominio proprio solo dopo (vedi "AdSense").

## Fonte dati (unica, ufficiale, verificata il 10/10/2026)
- Prospetto: `https://scioperi.mit.gov.it/mit2/public/scioperi` (HTTP 200, HTML ~316 KB). Tabella `#scioperiLarge` con colonne: Inizio, Fine, Sindacati, Settore, Categoria, Modalità, Rilevanza, **Note**, Data proclamazione, Regione, Provincia, Data ricezione. Contiene anche una **legenda dei settori** (tabella con definizione e delibera della Commissione di garanzia per ogni settore: Aereo, Ferroviario, Trasporto pubblico locale, Marittimo, Trasporto merci, Taxi, Ncc, Circolazione e sicurezza stradale, Generale, Plurisettoriale…): usarla, con fonte, per la guida "how to read the register".
- RSS: `https://scioperi.mit.gov.it/mit2/public/scioperi/rss` (200, 32 voci il 10/10/2026). Ogni `<item>` ha titolo "Data inizio: … - Settore: … - Rilevanza: … - Regione: … - Provincia: …", descrizione con modalità, data fine, sindacati, categoria, data proclamazione/ricezione, e `<guid>http://scioperi.mit.gov.it/NNNN</guid>` (**id stabile dello sciopero**, es. 8565). L'RSS **non ha la colonna Note**: leggere anche l'HTML.
- **Il registro mostra solo gli scioperi futuri** (il 10/10/2026: 23 a ottobre, 6 a novembre, 3 a dicembre; nessuno passato, nessuna revoca visibile). Quindi **lo storico lo costruiamo noi**: ogni giorno si salva tutto in `dati/scioperi.json` per guid con `visto_prima`, `visto_ultimo`, `stato` (`in programma`, `concluso`, `rimosso dal registro`). Se un guid sparisce prima della data di inizio → `rimosso dal registro` (probabile revoca): in pagina si scrive "no longer listed in the official register as of DD Mon YYYY (likely called off): check with the operator", mai "cancelled" come fatto certo. Se la colonna Note contiene "revoc…" → `stato: revocato` con la nota originale.
- Primo seme dello storico: `dati/fonti/rss-2026-10-10.xml` (salvato il 10/10/2026). Conservare in `dati/fonti/` una copia giornaliera dell'RSS (piccola, 25 KB) solo per gli ultimi 30 giorni.
- Fasce di garanzia e servizi minimi: **non ricopiare**, linkare le pagine ufficiali (Trenitalia e Italo "sciopero/servizi garantiti", ENAC "voli garantiti", ATM/ATAC/GTT ecc.). Gli URL vanno trovati e verificati con HTTP 200 (quelli ipotizzati nello studio davano 404).
- Sito indipendente: in ogni pagina "Independent site. Data from the official register of the Italian Ministry of Infrastructure and Transport (MIT); we are not affiliated with MIT, unions or transport operators."

## Lettura e traduzione dei dati (`italystrikes/raccolta/raccogli.py`)
- Scarica RSS + HTML, unisce per guid, aggiorna `dati/scioperi.json`, salva `dati/impronta.json` (data "aggiornato alla data" del registro) e stampa un riepilogo (nuovi, rimossi, modificati).
- Mappa settori → inglese e slug: Aereo → *Air transport (flights and airports)* `/flights/`; Ferroviario → *Trains* `/trains/`; Trasporto pubblico locale → *Local public transport (buses, metro, trams)* `/local-transport/`; Marittimo → *Ferries and ports* `/ferries/`; Trasporto merci → *Freight* `/freight/`; Taxi → `/taxis/`; Ncc → *Private hire (NCC)*; Circolazione e sicurezza stradale → *Motorways and roadside assistance* `/motorways/`; Generale → *General strike* `/general-strikes/`; Plurisettoriale → *Multi-sector*. Settori nuovi non in mappa: tenere il nome italiano e segnalarlo nel riepilogo.
- Rilevanza → *National / Interregional / Regional / Provincial / Local / Territorial*. Regione e provincia → nomi inglesi dove esistono (Roma→Rome, Milano→Milan, Firenze→Florence, Venezia→Venice, Napoli→Naples, Torino→Turin, Genova→Genoa, Padova→Padua, Siracusa→Syracuse; Toscana→Tuscany, Lombardia→Lombardy, Piemonte→Piedmont, Sicilia→Sicily, Sardegna→Sardinia, Puglia→Apulia (mostrare anche "Puglia"), Lazio, Veneto…).
- Modalità: mostrare **sempre il testo originale** ("24 ORE: DALLE 06.00 DEL 13/10 ALLE 05.59 DEL 14/10") e, quando il parser riesce, una resa in inglese ("24 hours, from 06:00 on 13 Oct to 05:59 on 14 Oct"); se non riesce, solo l'originale. Mai inventare orari.
- Categoria (es. "PERSONALE SOC AMTAB DI BARI"): mostrare l'originale e, se si riconosce l'operatore (AMTAB, ATM, ATAC, GTT, Trenitalia, Italo, Trenord, ITA Airways, easyJet, Ryanair, ENAV, handling…), aggiungere l'etichetta in inglese ("Bari city buses, AMTAB"). Tabella `dati/operatori.json` curata a mano, con la città.
- Ogni sciopero in pagina: data/e, settore, dove (regione/provincia/città), chi (operatore + sindacati), orari (modalità), rilevanza, **data di proclamazione**, link "Official register entry (MIT id NNNN)", `stato`.

## Sito (`italystrikes/sito/`, statico, generato da `italystrikes/genera.py`)
Circa 60 pagine. Titoli e meta-description con le parole cercate (vedi studio 3.3). Inglese semplice, frasi corte.
- `/` — "Italy strikes today and tomorrow — official register, updated daily": riquadri Today / Tomorrow / This week (conteggio per settore + lista), poi "Next 30 days" per data, filtro JS per settore/città, modulo avviso, link alle guide.
- `/today/`, `/tomorrow/`, `/this-week/`, `/next-week/` (le pagine "oggi/domani" sono la ragione del sito).
- Pagine mese: `/2026/october/`, `/2026/november/`, `/2026/december/` e ogni mese che ha almeno uno sciopero nel registro, più i 2 mesi futuri anche se vuoti ("No strikes listed yet for March 2027: strikes must be announced at least 10 days in advance, check back"). Le pagine dei mesi passati restano (storico) con "What happened".
- Settori (7): `/trains/`, `/flights/`, `/local-transport/`, `/ferries/`, `/taxis/`, `/general-strikes/`, `/motorways/` (+ `/freight/` corto).
- Città (15): Rome, Milan, Florence, Venice, Naples, Bologna, Turin, Pisa, Genoa, Verona, Palermo, Bari, Catania, Padua, Trieste → `/rome/` ecc.: mostra scioperi **nazionali + della regione + della provincia** della città, divisi in "affects the whole country", "affects this region", "local"; operatori locali linkati; "no local strikes listed" quando non c'è nulla.
- Aeroporti (8): Rome Fiumicino (FCO), Milan Malpensa (MXP), Milan Linate (LIN), Bergamo Orio al Serio (BGY), Venice (VCE), Naples (NAP), Bologna (BLQ), Pisa (PSA) → `/airports/rome-fiumicino/` ecc.: scioperi Aereo nazionali + regionali/provinciali della provincia dell'aeroporto; spiegazione delle fasce 7-10 e 18-21 e dei voli garantiti **con link ENAC**; niente elenchi di voli copiati.
- Guide fisse (10, testi in inglese, con fonti linkate, niente consulenza legale): How strikes work in Italy (law 146/1990, 10 days' notice, Commissione di garanzia); Guaranteed trains during strikes (link Trenitalia/Italo/Trenord); Flights during strikes (fasce, voli garantiti ENAC; su rimborsi e EU261 scrivere solo "check the airline and the EU rules", link); Local transport strike hours (fasce di garanzia tipiche, variano per città: linkare ATM, ATAC, GTT, ANM); What a general strike means; Why strikes are often on Fridays (solo se c'è una fonte); How to read the official register (legenda settori con fonte); Refunds and your rights (link, nessuna promessa); About and sources; Privacy.
- Freschezza: ogni pagina mostra "Official register last updated: DD Mon YYYY · page generated DD Mon YYYY HH:MM CET". I dati sono incorporati in ogni pagina come JSON e il **JS ricalcola oggi/domani/settimana nel browser** (fuso Europe/Rome), così le pagine restano giuste tra una generazione e l'altra. In più il JS prova a scaricare `https://raw.githubusercontent.com/Massimilianocori/copertine-libri/ccr-b7fd6b9e-n096cr/italystrikes/dati/scioperi.json` (repo pubblico, CORS aperto) e, se più recente, aggiorna la lista e scrive "updated just now from the register"; se fallisce, resta la versione incorporata. Controllare che `netlify.toml` (CSP) permetta la connessione a raw.githubusercontent.com.
- Modulo Netlify `alerts`: email, travel dates from/to, città o aeroporto (select), consenso obbligatorio, honeypot, campo nascosto `source` (da `?ref=`), invio AJAX come EsameB1. Testo: "Get an email if a strike is listed for your travel dates. Free, no spam."
- `privacy.html` (titolare Massimiliano Cori, Netlify responsabile, niente cookie finché non c'è AdSense; quando ci sarà: sezione pubblicità + consenso CMP di Google), `404.html`, `sitemap.xml`, `robots.txt`, `netlify.toml` (copiare da EsameB1: header di sicurezza + `ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."`).
- Dati strutturati JSON-LD `Event` per ogni sciopero in programma (name, startDate/endDate con fuso, location, organizer = sindacati, eventStatus: EventScheduled / EventCancelled solo se `revocato`), `WebSite` + `BreadcrumbList`. Immagine OG `assets/og.png` come gli altri siti.
- Stile: come EsameB1 (token su :root, chiaro/scuro, mobile 375 px senza scroll orizzontale, nessuna libreria esterna). Lasciare **spazi vuoti predisposti** per gli annunci (un blocco sotto il primo riquadro e uno a fine pagina) senza codice AdSense.
- Costante `GOOGLE_VERIFICA` in `genera.py` (Massimiliano darà il tag HTML di Search Console: inserirlo quando lo manda, non inventarlo).

## Aggiornamento automatico (ogni giorno, senza Claude e senza Massimiliano)
- Workflow GitHub Actions `.github/workflows/italystrikes.yml`: cron ogni giorno alle 04:30 UTC (06:30 Roma) + `workflow_dispatch`; checkout del branch `ccr-b7fd6b9e-n096cr`; `python3 italystrikes/raccolta/raccogli.py`; se `dati/` è cambiato: `python3 italystrikes/genera.py`, commit "Italy strikes: registro del DD/MM/YYYY" e push sullo stesso branch (permissions `contents: write`). Il push fa partire il deploy Netlify.
- **Crediti Netlify (da verificare nei documenti ufficiali prima di scegliere)**: il piano gratuito ha un tetto mensile di crediti condiviso dai 3 siti (EsameB1 e EsamiDiStato pubblicano al massimo una volta a settimana). Verificare su docs.netlify.com quanto costa un deploy da GitHub e se un deploy "manuale" via CLI/API (file già pronti, senza build) costa meno. Scegliere: (a) deploy giornaliero se rientra nel gratuito con margine; (b) altrimenti: Actions aggiorna e committa solo `dati/` ogni giorno (le pagine si aggiornano nel browser dal JSON su raw.githubusercontent.com), e rigenera `sito/` solo il lunedì o quando entra nel registro uno sciopero **nazionale** entro 10 giorni (max 8 deploy al mese per questo sito). Scrivere la scelta e i numeri in `NOTE.md`.
- Aggiungere il sito alla routine settimanale `trig_017HFNXZX5fKYcerETVg5zq4` (prompt: controllo che il workflow abbia girato, che il formato del registro non sia cambiato, lettura iscritti e Search Console).

## Vincoli (non negoziabili)
1. **Zero spese** in Fase 1. Dominio e tutto il resto solo con il sì scritto di Massimiliano sull'importo.
2. **Ogni sciopero porta l'id MIT, la data di proclamazione e il link al registro.** Niente date, orari o revoche inventati o "probabili"; in dubbio si scrive "check with the operator" e si linka l'operatore.
3. In ogni pagina: "Strikes can be called off or changed at short notice. Always check with your train operator, airline or local transport company before travelling." Nessuna consulenza legale (rimborsi: solo link).
4. **Nessun identificatore di modello AI** nel codice, nelle pagine, nei commit, nel workflow.
5. Privacy GDPR: titolare Massimiliano Cori; modulo con consenso esplicito; niente cookie né analytics finché non c'è AdSense (si usa Search Console).
6. Niente email a freddo. Distribuzione: solo Google (sitemap + Search Console). Facoltativo e solo con il sì di Massimiliano: una risposta onesta su Reddit (r/ItalyTravel) o TripAdvisor quando qualcuno chiede "is there a strike tomorrow", dichiarando chi siamo.
7. Marchi: MIT, Trenitalia, Italo, ITA Airways ecc. sono citati solo come riferimento; nota "independent, not affiliated".
8. Nessun dato personale nel repo o nei report.

## AdSense (giorno ~20, non ora)
- AdSense accetta solo siti su **dominio proprio** (non sottodomini come `*.netlify.app`): verificare nelle regole AdSense e, se confermato, al giorno 20 proporre a Massimiliano l'acquisto di un dominio (`italystrikes.com` o simile, ~10-15 €/anno) **solo se** Search Console mostra ≥20 pagine indicizzate e impression in crescita. Senza il suo sì sull'importo non si compra nulla.
- Pagine richieste da AdSense già pronte dal giorno 1: About, Contact (modulo o email dedicata, non la personale), Privacy con sezione pubblicità, contenuti originali (le guide).
- Consenso pubblicità per i visitatori UE: CMP gratuita di Google (Privacy & messaging) quando si attiva AdSense.
- Fisco: i ricavi AdSense sono di natura commerciale (vedi REGOLE-FISSE): nulla da aprire finché non arriva il primo pagamento (soglia AdSense 70 €). Decisione con un professionista al primo incasso.

## Test (45 giorni dalla pubblicazione; dati Search Console, ultimi 14 giorni)
1. Pagine indicizzate ≥40 su ~60.
2. Impression ≥1.500/settimana e in crescita per 2 settimane di fila.
3. Clic totali dal giorno 1 ≥150, CTR ≥2%.
4. ≥40% dei clic da USA + Canada + UK + Australia.
5. Almeno 5 query con "today", "tomorrow" o mese+anno tra le prime 20 per impression.
6. AdSense approvato; se attivo ≥7 giorni: RPM ≥6 $.
Passano 1-4 → si continua: satelliti (codice fiscale calculator, ZTL per città), versione italiana con lo stesso motore, richiesta Journey a 1.000 sessioni Tier 1/30 giorni. Fallisce 1 o 2 → stop (come BandiPosteggi). Fallisce solo 4 → tenere il sito e aprire la versione italiana.
Opzione da autorizzare a parte, dopo l'approvazione AdSense: ≤50 € di Google Ads su "italy strike today/tomorrow" per misurare l'RPM reale in 7 giorni (soglia: RPM ≥6 $, costo per visita ≤0,15 €).

## Verifica prima di consegnare
- `python3 italystrikes/raccolta/raccogli.py` e `python3 italystrikes/genera.py` senza errori; nessun link interno rotto; Playwright (`/opt/node-tools/node_modules/playwright`, `executablePath: '/opt/pw-browsers/chromium'`, `waitUntil: 'domcontentloaded'`): home, today, una città, un aeroporto, un mese, modulo (invio simulato ok/errore), mobile 375 px, nessun errore in console, nessuno scroll orizzontale.
- Controllo dati: ogni sciopero ha guid, proclamazione e fonte; nessuno sciopero passato mostrato come futuro; il JS "oggi/domani" provato con una data finta.
- Workflow Actions provato con `workflow_dispatch` (o almeno con `act`/esecuzione locale degli stessi comandi) e commit di prova.
- `italystrikes/NOTE.md`: stato, scelte, cosa manca, data inizio test, soglie, cosa deve fare Massimiliano.

## Ruoli
- Claude: tutto il lavoro sopra; lettura settimanale dei numeri; proposta dominio/AdSense al giorno 20 con i dati.
- Massimiliano (10 minuti, come per gli altri due siti): nuovo progetto Netlify da GitHub (branch `ccr-b7fd6b9e-n096cr`, base e publish `italystrikes/sito`), attivare i moduli + notifica email, Search Console (tag HTML → mandarlo a Claude) + sitemap; abilitare GitHub Actions sul repo se chiesto. Nessuna spesa.
