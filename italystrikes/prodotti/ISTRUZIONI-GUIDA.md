# Guida in PDF "Italy by Train: the strike-proof guide" — istruzioni di costruzione

Decisione del 10/10/2026 (Massimiliano: "per le guide sei tu il cervello, se pensi sia una buona idea falla"; Claude: sì, come test a costo zero). Chi costruisce legge prima `studio-business/STRATEGIA.md`, `studio-business/REGOLE-FISSE.md`, `italystrikes/NOTE.md`.

## Cosa
Un PDF in inglese, 50-60 pagine formato 6×9 pollici, testo grande (≥11,5 pt), impaginato bene (stile del sito: rosso #B3261E, grigi, font Inter per i titoli e DejaVu Serif/Charter per il testo: sono i font installati, vedi `fc-list`), da vendere a 9-12 $ con **Payhip** (account gratuito a nome di Massimiliano: incassa, consegna il file e gestisce l'IVA UE; commissione 5 %). Pagina di vendita dentro il sito scioperi (`/guide/italy-by-train/`), collegata dal menu e dal riquadro "Stuck by a strike?". **Nessun pagamento gestito da noi.**
Canale secondario, dopo: versione KDP (Morgan Reade, guide "Explained") SOLO se il punteggio BookBeam ≥ 9 (skill kdp-book-pipeline).

## Soglia del test (scritta prima)
45 giorni dal primo traffico misurabile (≥ 1.000 visite/mese al sito): **≥ 10 vendite → si continua** (altre guide: Rome by train, Driving in Italy, Moving to Italy); sotto → stop, la pagina resta.

## Regole non negoziabili
1. **Solo fatti verificati** su fonti ufficiali, con la fonte e la data in appendice; tutto il resto "check with your operator". Niente consulenza legale: sui diritti si riporta la norma e si rimanda. Nessun dato inventato, nessun orario "tipico" non documentato.
2. Nessun identificatore di modello AI nel PDF, nei metadati, nei file.
3. Dichiarare in apertura che è una guida indipendente, non affiliata a MIT, Trenitalia, Italo ecc.
4. Niente promesse di bonus esterni; i link al sito sono ammessi (è nostro).
5. Il PDF va in `italystrikes/prodotti/italy-by-train/` (sorgente HTML + `build.py` che stampa il PDF con Playwright/Chromium: `/opt/node-tools/node_modules/playwright`, `executablePath: '/opt/pw-browsers/chromium'`, `page.pdf({width:'6in',height:'9in'})`). Il PDF finito NON va in `sito/` (lo ospita Payhip).

## Fatti verificati disponibili (fonti lette il 10/10/2026)
- **Legge 146/1990**: scioperi nei servizi pubblici essenziali con preavviso minimo 10 giorni; Commissione di garanzia. Fonte Normattiva: https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1990-06-12;146
- **Registro MIT** https://scioperi.mit.gov.it/mit2/public/scioperi (RSS /rss): per ogni sciopero data inizio/fine, settore, rilevanza, regione, provincia, sindacati, categoria, modalità (orari), data di proclamazione, note. Il prospetto principale mostra gli scioperi futuri; c'è anche una ricerca storica dal 2014 (Effettuato/Revocato). Dati con licenza CC BY 4.0 (citazione obbligatoria). Statistiche del registro al 10/10/2026 (32 scioperi): 13 trasporto locale, 8 aereo, 3 merci, 3 generali, 2 plurisettoriali, 1 ferroviario, 1 marittimo, 1 autostrade; 10 nazionali; **15 su 32 di venerdì**; 12 "24 ore", 11 "4 ore"; anticipo proclamazione→sciopero da 10 a 119 giorni (mediana ~24). Usare come "snapshot", non come regola eterna.
- **Trenitalia** (https://www.trenitalia.com/it/informazioni/treni-garantiti-incasodisciopero.html e pagina EN "In case of strike" https://www.trenitalia.com/en/information/in-case-of-strike.html): regionali garantiti feriali 06:00-09:00 e 18:00-21:00; festivi 07:00-10:00 e 18:00-21:00; alcuni treni a lunga percorrenza garantiti tutti i giorni (tabella sul sito IT); treni in viaggio all'inizio dello sciopero arrivano a destinazione se raggiungibile entro un'ora, poi possono fermarsi prima. Pagina EN: "See Italian version for details on guaranteed trains".
- **Trenord** (https://www.trenord.it/en/assistance/useful-information/in-case-of-strike-action/): stesse fasce (feriali e sabato 6-9/18-21; festivi 7-10/18-21); EC82/EC83 Brennero-Bologna sempre garantiti; **rimborso del biglietto entro 30 giorni dallo sciopero** se non si è potuto viaggiare.
- **Italo**: nessuna pagina fissa; avvisi e lista treni garantiti in home https://www.italotreno.com/en prima di ogni sciopero (PDF per sciopero).
- **ENAC voli garantiti** https://www.enac.gov.it/trasporto-aereo/diritto-alla-mobilita/scioperi-nel-trasporto-aereo/voli-garantiti/ : "fasce orarie di tutela dalle ore 7 alle 10 e dalle ore 18 alle 21, nelle quali i voli devono essere comunque effettuati"; elenco voli garantiti per ogni sciopero (PDF).
- **ZTL** (Codice della Strada su Normattiva, estratti in `italystrikes/satelliti/fonti/`): art. 7 c. 14 sanzione 83-332 €; art. 202 pagamento del minimo entro 60 giorni, -30 % entro 5 giorni; art. 201 notifica entro 360 giorni per i residenti all'estero (dal momento in cui l'amministrazione può identificare il trasgressore).
- **Codice fiscale** (Agenzia delle Entrate EN https://www.agenziaentrate.gov.it/portale/web/english/nse/individuals/tax-identification-number-for-foreign-citizens): 16 caratteri; all'estero via consolato; in Italia Sportello Unico Immigrazione/Questura per chi ha permesso di soggiorno, altrimenti uffici AdE con appuntamento di persona; UE con documento d'identità. Algoritmo in `italystrikes/genera.py` (CF_JS) e dati in `satelliti/`.
- **Diritti UE**: ferrovia Reg. (UE) 2021/782 (pagina Your Europe https://europa.eu/youreurope/citizens/travel/passenger-rights/rail/index_en.htm); aereo Reg. 261/2004 (https://europa.eu/youreurope/citizens/travel/passenger-rights/air/index_en.htm). Sullo sciopero: dire solo che i diritti dipendono da chi sciopera (personale della compagnia vs controllo aereo) e rimandare alle pagine UE e alla compagnia; niente cifre di compensazione se non lette sulla pagina UE.
- Link operatori locali verificati in `italystrikes/dati/link.json` (ATM, GTT, ACTV, TPER, Autolinee Toscane/GEST, AMT, AMAT, AMTAB, AMTS, Busitalia Veneto, Trieste Trasporti, ATV; ATAC e aeroporti FCO/BGY/VCE/NAP/PSA "browser").
- Affiliati: SafetyWing (link in `dati/affiliati.json`), Airalo (in attesa), Omio/Welcome Pickups (Travelpayouts in pausa). Nella guida i link affiliati vanno dichiarati ("affiliate link").

## Struttura proposta (adattare)
1. Copertina; frontespizio; avvertenza (indipendente; verifica sempre; non consulenza legale); come usare la guida (+ link al sito per gli scioperi di oggi).
2. How strikes work in Italy (legge, registro, chi sciopera, come leggere un avviso, lo snapshot statistico, revoche).
3. Trains: guaranteed services (Trenitalia/Trenord/Italo), the one-hour rule, how to read the guaranteed list, what to do when your train is cancelled (rimborso/riprotezione secondo Reg. 2021/782 e operatore; Trenord 30 giorni), alternatives (bus FlixBus/Itabus, Omio, car).
4. Flights and airports: protected bands 7-10/18-21, ENAC list, airline vs ATC strikes, rights (rimando UE), airport transfers when trains stop.
5. Buses, metro, trams: 4h vs 24h, guaranteed bands set by each operator (link per città), taxis.
6. Driving: ZTL (regole verificate), rental cars and fines, autostrade strikes (solo rimando al registro).
7. Practical Italy: codice fiscale (quando serve davvero e come si ottiene), eSIM/connettività, assicurazione, validazione biglietti regionali, classi e tariffe (solo fatti generali), bagagli.
8. The strike-proof planning method: timeline (check register 10-14 days before each leg; book changeable fares; buffer days; never put airport transfer on a strike day; where to position yourself: cities with alternatives), checklist.
9. Itineraries by train with "strike buffers": 7 giorni (Rome–Florence–Venice), 10 giorni (+Milan/Lakes o Naples/Amalfi), 14 giorni (grand tour); tempi di viaggio approssimati ("about 1h30"), senza orari precisi.
10. Appendix: official sources with URLs and dates; glossary IT→EN (sciopero, fasce di garanzia, treni garantiti, revoca, proclamazione, varco attivo, biglietto, convalida…); emergency numbers (112); quick card da stampare.

## Pagina di vendita nel sito
`genera.py`: nuova pagina `guide/italy-by-train/` (titolo "Italy by Train 2026: the strike-proof guide (PDF)"), con indice, 3-4 pagine di esempio come immagini (PNG dal PDF), prezzo, pulsante "Buy on Payhip" = link `https://payhip.com/b/XXXX` preso da `dati/prodotti.json` (se vuoto, la pagina non viene generata). Link dal menu ("Guide PDF") e dal riquadro "Stuck by a strike?". Niente script esterni.

## Cosa deve fare Massimiliano
1. Account Payhip (gratis): https://payhip.com → Sign up; prodotto digitale, caricare il PDF consegnato da Claude, prezzo 9,99 $ (o 11,99), abilitare la raccolta IVA UE (Payhip lo fa come venditore); copiare il link del prodotto e mandarlo a Claude.
2. Facoltativo dopo: screenshot BookBeam per la versione KDP.
