# Nel mondo: altre pagine "oggi / domani / stato" costruibili con il motore di Italy Strikes Today

Data: **10 ottobre 2026** (scansioni e download dal server della sessione tra le 16:00 e le 19:30 UTC).
Cartella: `scratchpad/mondo/` — `scan1.json` e `scan2.json` (autocomplete grezzo, 891 chiamate), `analisi1.txt` e `analisi2.txt` (tabelle), `dl/` (379 file scaricati, 32 MB, letti solo con `python3 -I`), `script/` (scanner e analisi).
Nessun file del repository è stato toccato.

**Criterio scritto prima del lavoro.** Una candidata PASSA se: (1) domanda "today/tomorrow/status" confermata nell'autocomplete Google in **almeno 2 mercati** tra USA, UK, Australia; (2) **una** fonte ufficiale gratuita leggibile in automatico (HTTP 200 dal server, senza login) con dati strutturati o HTML stabile; (3) nessun sito dedicato in inglese già dominante (ammessi app ufficiali e giornali); (4) ricavo prudente **≥ 1.500 €/anno a 18 mesi**. Niente dati inventati: dove manca, scrivo "non trovato".

---

## 0. Risposta in breve

- Ho scansionato **297 combinazioni Paese/città × bisogno** in 3 mercati. La domanda "today/tomorrow" c'è quasi ovunque (**254 combinazioni su 297 hanno suggerimenti in tutti e 3 i mercati**). **La domanda non è il collo di bottiglia: lo è la fonte.**
- Ho provato **~250 URL ufficiali**. Fonti ufficiali gratuite, senza token, con dati strutturati e 200 dal server: **18**. Di queste, quelle che rispondono a una domanda turistica anglofona non già coperta da un sito dedicato in inglese: **4**.
- **Candidate che passano (4):** Venezia acqua alta (satellite Italia), Islanda strade/F-roads/eruzione, Londra chiusure della Tube nel weekend, e — con riserva, perché serve un token gratuito ancora da provare — Giappone treni/Shinkansen + tifoni.
- **Nessuna è "grande" come gli scioperi italiani.** Lo sciopero italiano è un caso unico per tre motivi insieme: registro pubblico con 10 giorni di anticipo, fonte in italiano con pessima usabilità, nessun sito inglese. Nel mondo ho trovato pezzi di questo schema, mai tutti e tre insieme con volumi alti.
- Gli **scioperi fuori Italia** (Grecia, Portogallo, Germania, Belgio, Olanda, Irlanda, Norvegia, Austria, Spagna, Francia) hanno domanda forte in tutti e 3 i mercati, ma in **nessun Paese** esiste un registro pubblico leggibile: confermato anche oggi per Grecia (hcg.gr e gov.gr bloccano il server; i sindacati non sono fonte ufficiale) e Portogallo (la DGERT pubblica solo statistiche mensili in PDF, non l'elenco dei preavvisi).

---

## 1. Tabella della scansione (autocomplete Google, `client=firefox`, `hl=en`, `gl=us|gb|au`)

Lettura: "3/3" = suggerimenti con today/tomorrow/live/status/now/this weekend in tutti e tre i mercati. Riga per riga nei file `analisi1.txt` (128 seed) e `analisi2.txt` (169 seed). Qui le combinazioni più rilevanti, raggruppate.

| Gruppo | Combinazione (seed) | Suggerimenti trovati (esempi) | Mercati |
|---|---|---|---|
| **Italia (altre pagine)** | venice acqua alta / venice high tide / venice flooding / venice tide forecast | "venice acqua alta today", "venice high tide today", "venice flooding today live", "venice tide chart today" | 3/3 |
| | etna eruption / etna today / etna erupting now / stromboli / vesuvius / catania airport closed today | "etna eruption today live", "etna erupting now", "catania airport closed today", "stromboli eruption today" | 3/3 |
| | amalfi coast road closed / cinque terre trail closed / pompeii / vatican museums / colosseum | "amalfi coast road closure today", "cinque terre blue trail closed today", "is pompeii closed today", "is the vatican museum open today" | 3/3 |
| | italy strike today / tomorrow / rome strike tomorrow | "italy strike today", "italy strike tomorrow", "rome strike tomorrow" | 3/3 |
| **Giappone** | shinkansen status / shinkansen running today / shinkansen cancelled today | "shinkansen status today", "shinkansen status tomorrow", "is tokaido shinkansen running today", "shinkansen delays today" | 3/3 |
| | jr east status / jr west status / tokyo train delays / japan train delays | "jr east status live", "jr west status today", "tokyo train delays today live", "japan train delays today" | 3/3 |
| | japan typhoon today / typhoon japan flights / narita flights cancelled today / japan earthquake today | "japan typhoon today map", "typhoon japan flights cancelled today", "japan earthquake today tsunami warning" | 3/3 |
| | mount fuji closed / open today; is tomorrow a holiday in japan | "mount fuji current status", "mount fuji open today", "is tomorrow a holiday in japan" | 3/3 |
| **UK / Londra** | tube closures / tube closures this weekend / tube strike / london tube strike today / is there a tube strike today | "tube closures this weekend map", "tube closures tomorrow", "tube strikes this week", "tube strike tomorrow" | 3/3 |
| | train strikes uk / rail strike / heathrow strike / uk airport strike / heathrow-gatwick delays today | "train strikes uk today", "heathrow strike update today live", "flight delays today heathrow terminal 5" | 3/3 (rail strike: 1/3) |
| **Islanda** | iceland road conditions / road closures / iceland roads / f roads / golden circle open today | "iceland road conditions today", "iceland road closures today map", "iceland f roads status", "is golden circle open today" | 3/3 |
| | iceland eruption / iceland volcano / iceland weather warning | "iceland eruption today", "iceland volcano eruption today", "iceland weather warning today map", "iceland weather warning tomorrow" | 3/3 (reykjanes eruption: 0/3) |
| **Grecia** | greece strike / athens strike / athens metro strike / greek strike tomorrow | "greece strike tomorrow", "athens strike tomorrow time", "athens metro strike today" | 3/3 |
| | greece ferries cancelled / greek ferries today / ferry cancelled today | "greece ferries cancelled today", "greek ferry cancellations today santorini", "ferry cancellations today greece" | 3/3 (santorini ferry: 0/3) |
| | greece sailing ban / greece wildfire / acropolis closed-open today | "sailing in greece today", "greece wildfires today", "acropolis closed due to heat today", "is acropolis open today athens" | 3/3 |
| **Francia** | paris strike / paris metro strike / france train strike / france ATC strike / france-paris strike tomorrow | "paris strikes today", "paris metro strike tomorrow", "france air traffic control strike update today" | 3/3 (france strike: 0/3) |
| | louvre closed today / louvre strike / eiffel tower closed today / cdg delays today | "louvre closed today", "louvre strike today", "eiffel tower closed today" | 3/3 |
| **Spagna** | spain airport strike / barcelona-madrid airport strike today / sagrada familia / alhambra closed today | "spain airport strikes today", "barcelona airport strike today", "sagrada familia closed today" | 3/3 (spain strike, barcelona strike: 2/3 ma suggerimenti di calcio "striker") |
| **Portogallo** | lisbon strike / lisbon metro strike / portugal train strike / lisbon airport strike today / power outage portugal today | "lisbon strike tomorrow", "lisbon metro strike update today live", "portugal train strike update today" | 3/3 |
| **Germania / Austria / Svizzera** | germany train strike / deutsche bahn strike / berlin strike / db strike tomorrow / sbb disruptions today | "germany train strike today", "deutsche bahn strike tomorrow", "berlin strikes this week", "sbb disruptions today" | 3/3 (austria strike, switzerland strike: 0/3; vienna strike 3/3 su scan1) |
| **Benelux / Irlanda / Norvegia** | brussels strike / brussels airport strike / amsterdam strike / dublin strike / oslo strike / ns disruptions today | "brussels strike tomorrow", "amsterdam strike today", "dublin strike update today", "oslo airport strike update today" | 3/3 (belgium strike, netherlands strike, ns strike: 0/3) |
| **Croazia / Turchia** | croatia ferry / jadrolinija / split ferry / istanbul strike / turkey earthquake today | solo "istanbul strike today", "turkey earthquake today" | croazia 0/3; turchia 3/3 |
| **Asia** | hong kong typhoon signal / typhoon 8 today / taiwan typhoon / typhoon day off tomorrow | "hong kong typhoon signal right now", "typhoon signal 8 today", "taiwan typhoon work cancellations today", "taiwan typhoon day off tomorrow" | 3/3 |
| | bali ash cloud / bali volcano / bali flights cancelled today / bali airport closed today | "bali ash cloud today live", "bali volcano eruption today", "bali flights cancelled today international" | 3/3 (bali flights: 0/3) |
| | thailand flood / bangkok-phuket-chiang mai flooding today / vietnam-philippines typhoon today | "thailand flooding today live", "bangkok flood now", "vietnam typhoon warning today live", "manila flights cancelled today" | 3/3 |
| | korea strike / seoul subway strike / korea train strike | "korea strike today" | 3/3 / 0/3 / 0/3 |
| **Americhe** | cancun sargassum / tulum / playa del carmen sargassum today / cancun hurricane today | "cancun sargassum today map", "cancun sargassum live cam", "tulum sargassum today" | 3/3 (sargassum forecast: 0/3) |
| | kilauea eruption / is kilauea erupting / hawaii volcano | "kilauea eruption today", "is kilauea erupting now", "hawaii volcano live cam" | 3/3 (hawaii flights: 0/3) |
| | yosemite closed / is yosemite open today / tioga pass open / chains required today / california wildfire road closures | "yosemite closed today", "yosemite road closures today", "is chains required on i 80 today" | 3/3 (yosemite road: 0/3) |
| | via rail strike / canada rail strike / amtrak delays today | "via rail strike update today", "amtrak delays today" | 3/3 |
| **Oceania** | total fire ban / nsw total fire ban / nsw fire danger / victoria fire danger | "total fire ban today", "nsw total fire ban today", "victoria fire danger rating today" | 3/3 |
| | sydney train strike / sydney trains delays today / melbourne trains today / nz road closures / auckland trains today | "sydney train strike update today", "nz state highway closures today" | 3/3 (new zealand strike: 0/3) |
| **Generici** | strikes today / strike tomorrow / train strike today / airport strike today / flights-ferry-metro-road today | "train strike today italy", "train strike today uk", "lisbon airport strike today", "ferry cancellations today greece", "europe strikes today" | 3/3 |
| **Musei / luoghi / festivi** | louvre, acropolis, colosseum, pompeii, vatican, sagrada familia, alhambra "closed/open today"; public holiday tomorrow italy/spain/france/japan; shops closed tomorrow | tutti con "closed today" / "open today" / "tomorrow" | 3/3 |
| **Neve / spiagge** | ski lifts open today (zermatt, chamonix, whistler, niseko, val thorens); beach flag / red flag / purple flag / jellyfish today | "chamonix lifts open today", "red flag beach today", "jellyfish today ocean city md" (USA domestico) | 3/3 (jellyfish barcelona: 0/3) |

Avvertenze sull'autocomplete: (a) è un segnale di **presenza** della domanda, non di volume; (b) per i Paesi anglofoni (UK, Australia, USA, Canada) il suggerimento viene soprattutto dai residenti, non dai turisti; (c) "spain/germany/netherlands strike" porta suggerimenti di calcio ("striker"); (d) in `gl=us|gb|au` i suggerimenti sono quasi identici: Google li globalizza per l'inglese, quindi il requisito "≥ 2 mercati" è quasi sempre soddisfatto e discrimina poco.

---

## 2. Tabella delle fonti verificate (dal server, User-Agent browser, 10/10/2026)

"Auto": **sì** = leggibile in automatico oggi; **parziale** = leggibile con limiti seri; **no**.

| # | Paese / bisogno | Fonte (ente) | URL provato | HTTP | Formato | Token | Licenza | Tempo reale / anticipo | Auto |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **IT Venezia acqua alta** | ICPSM – Centro Previsioni e Segnalazioni Maree, su dati.venezia.it | `https://dati.venezia.it/sites/default/files/dataset/opendata/previsione.json` | **200** (3 KB) | JSON: 13 estremali (min/max, cm a Punta Salute, data/ora), previsione del 10/10 13:30 fino al 13/10 | nessuno | **CC-BY** (scheda dataset `?q=content/cpsm-dati-meteomarini-laguna-e-litorale-veneziano`, "Licenza: CC-BY") | aggiornata "in genere tre volte al giorno", **3-4 giorni di previsione** | **sì** |
| 2 | IT Venezia livello in tempo reale | ICPSM | `.../opendata/livello.json` (+ vento, pressione, onde) | **200** | JSON: 16 stazioni, valore in m, ogni 15 min | nessuno | CC-BY | tempo reale | sì |
| 3 | IT Venezia pagina ufficiale del Comune | Comune di Venezia | `https://www.comune.venezia.it/it/content/centro-previsioni-e-segnalazioni-maree` | **403** (blocco anti-robot) | HTML | – | – | – | no (non serve: c'è la #1) |
| 4 | IT Etna | INGV Osservatorio Etneo, comunicati e VONA | `https://www.ct.ingv.it/index.php/.../comunicati-attivita-vulcanica` e `/vona` | 200 (105 KB) | HTML Joomla "wrapper": **l'elenco dei comunicati non è nel HTML** (caricato da un'altra applicazione); feed RSS → 404 | – | – | – | **no** (da riprovare cercando l'applicazione interna) |
| 5 | IT Cinque Terre sentieri | Parco Nazionale | `parconazionale5terre.it/sentieri-stato.php`, `/Esentieri.php` | 404 / 404 (home 200) | – | – | – | – | non trovato |
| 6 | **JP Shinkansen Tokaido** | JR Central | `https://traininfo.jr-central.co.jp/shinkansen/pc/en/index.html` | 200 (9 KB) | HTML con **script che reindirizza ogni lingua (en, fr, de, ko, zh) alla versione giapponese** `/pc/ja/`; pagina interamente JavaScript; i JSON dei dati (`var/train_info/service_status.json` ecc., nomi letti in `main.js`) restituiscono la **home del sito** (soft 404) anche con Referer | – | © JR Central | tempo reale | **no** (serve browser headless; e la pagina inglese oggi non esiste più) |
| 7 | JP Shinkansen Tohoku/Hokuriku, treni Tokyo | JR East | `https://traininfo.jreast.co.jp/train_info/e/service.aspx` e `.../data/jsonlist/shinkansen.json` | **403** "Access Denied" (Akamai) su tutte le pagine, anche la home | – | – | – | – | **no** |
| 8 | JP JR West | JR West "train-guide" | `https://www.train-guide.westjr.co.jp/api/v3/area_kinki_trafficinfo.json` (anche hokuriku, okayama, hiroshima, sanin) | **200** | JSON `{"lines":{},"express":{}}` (vuoto = nessuna perturbazione oggi; struttura nota dalla libreria WestJR su PyPI) | nessuno | non indicata | tempo reale | parziale (solo linee ordinarie dell'ovest; **Sanyo Shinkansen non trovato**) |
| 9 | JP tutti gli operatori (JR East, Tokyo Metro, Toei…) | ODPT – Public Transportation Open Data Center | `https://api.odpt.org/api/v4/odpt:TrainInformation` | **403** "Require acl:consumerKey" | JSON | **token gratuito** con registrazione sviluppatore (sito `developer.odpt.org` è un'app JS, non letta dal server) | CC-BY per molti dataset (da verificare per JR East) | tempo reale | parziale (non provato: serve l'account di Massimiliano, come PRIM) |
| 10 | **JP tifoni** | JMA (気象庁) | `https://www.jma.go.jp/bosai/typhoon/data/targetTc.json` → `TC2634/specifications.json`, `forecast.json` | **200** | JSON con nome in inglese ("Koguma"), categoria, venti, traccia, previsione | nessuno | **Public Data License v1.0** (citare la fonte; dichiarare le modifiche) | tempo reale (emissione ogni 3-6 h) | **sì** |
| 11 | JP avvisi meteo per prefettura | JMA | `.../bosai/warning/data/warning/130000.json` | 200 | JSON (codici, giapponese) | nessuno | PDL v1.0 | tempo reale | sì |
| 12 | **UK Londra Tube** | TfL Unified API | `https://api.tfl.gov.uk/Line/Mode/tube,dlr,overground,elizabeth-line/Status` e `.../Line/Mode/tube/Status?startDate=2026-10-17&endDate=2026-10-18` | **200** / **200** (anche con date future fino a 4 settimane) | JSON: per linea stato, "reason" in inglese, periodi di validità. Esempio reale per il weekend 17-18/10: District "no service between Turnham Green and Ealing Broadway", Piccadilly "no service between Hammersmith and Heathrow" | **nessuno** fino a 50 richieste/minuto; chiave gratuita per 500/min | OGL v2 con modifiche TfL: uso commerciale ok, credito "Powered by TfL Open Data" | tempo reale + **chiusure programmate settimane prima** | **sì** |
| 13 | UK scioperi ferroviari nazionali | National Rail | `nationalrail.co.uk/travel-information/industrial-action/` | 200 | HTML "archivio": "No further nationwide industrial action has been announced" | – | – | – | no (nessun registro) |
| 14 | **IS strade** | Vegagerðin (IRCA) | `https://gagnaveita.vegagerdin.is/api/faerd2014_1` | **200** (394 KB) | JSON: **974 tratti**, stato in islandese con codice (`IdAstand` 14 "Greiðfært" percorribile, 16 "Fært fjallabílum 4x4", 56 "Ófært" impraticabile, 149 "Vegur ekki í þjónustu" non in servizio…), flag `ErHalendi` (altopiano/F-roads, 111 tratti), colore, data | nessuno | **CC BY 4.0** (pagina "Terms of Use for Data Services", letta oggi: citare IRCA, dataset, data di scarico) | tempo reale (`DagsKeyrtUt` 16:21 di oggi) | **sì** |
| 15 | IS meteo ufficiale (stazioni stradali) | Vegagerðin | `.../api/vedur2014_1` | 200 (105 KB) | JSON | nessuno | CC BY 4.0 | tempo reale | sì |
| 16 | **IS allerte meteo** | Icelandic Met Office (vedur.is) | `https://api.vedur.is/cap/capbroker/active/detailed/all` | **200** | JSON CAP con `headline_en`, `description_en`, regione, colore, onset/expires (oggi: "Southeast severe gale", South Iceland, giallo, dal 11/10 22:00) | nessuno (Swagger pubblico su api.vedur.is) | non indicata (da chiedere) | tempo reale, allerte fino a 2-3 giorni prima | sì |
| 17 | **IS vulcani** | Icelandic Met Office | `https://api.vedur.is/volcanoes/vals` (livelli di allerta), `/vona`, `/volcanoes` | **200** | JSON: codice vulcano, colore in inglese, descrizione in inglese, data (es. REY Reykjanes arancione 15/10/2025) | nessuno | non indicata | tempo reale | sì |
| 18 | GR scioperi / divieti di navigazione | Hellenic Coast Guard, YNANP, gov.gr, Protezione civile, Ministero cultura | `hcg.gr/el/anakoinoseis`, `hcg.gr/en`, `ynanp.gr`, `gov.gr`, `civilprotection.gov.gr`, `culture.gov.gr` | **403** tutte (anche WebFetch: dominio non risolto) | – | – | – | – | **no** |
| 19 | GR scioperi (sindacati) | GSEE, ADEDY | `gsee.gr`, `adedy.gr` | 200 | HTML greco | – | – | annunci sindacali | no (non ufficiali, testo libero) |
| 20 | GR traghetti | porto del Pireo (OLP), ferries.gr, greekferries.gr, Ferryhopper | `olp.gr/en` 200, `/en/news` 404; siti privati 200 | 200 | HTML | – | – | – | no (nessuna fonte ufficiale strutturata) |
| 21 | PT scioperi | DGERT (Direção-Geral do Emprego e das Relações de Trabalho) | `dgert.gov.pt/avisos-previos-de-greve` 404; ricerca web: solo "Relatório Avisos Prévios de Greve" mensili in PDF (statistiche aggregate) | 404 / PDF | PDF statistici | – | – | – | **no** (nessun elenco dei preavvisi) |
| 22 | PT treni / metro | CP, Metro Lisboa | `cp.pt/passageiros/en/` 200 ma 3 KB (app JS); `api.metrolisboa.pt:8243/...` connessione fallita | – | – | API Metro Lisboa richiede chiave | – | – | no |
| 23 | DE scioperi | Deutsche Bahn | `bahn.de/info/streik` 404, `bahn.de/web/api/.../verbindungsstoerungen` 403 | 404/403 | – | – | – | – | no |
| 24 | BE treni | iRail (riusa SNCB) | `https://api.irail.be/disturbances/?format=json&lang=en` | 200 (67 avvisi, inglese) | JSON | nessuno | – | tempo reale | parziale (**non ufficiale**; SNCB stessa dà 403) |
| 25 | NO trasporti | Entur (nazionale) | `https://api.entur.io/realtime/v1/rest/sx` | 200 (728 KB) | XML SIRI SX | nessuno | NLOD | tempo reale | sì (ma nessuna domanda specifica trovata: "norway strike" 1/3) |
| 26 | CH treni | SBB open data | `https://data.sbb.ch/api/explore/v2.1/catalog/datasets/rail-traffic-information/records?...` | **200** | JSON, testo in inglese, 7.169 record storici, campo `cause` | nessuno | Open data SBB | tempo reale | sì (ma SBB inglese già perfetto) |
| 27 | NL treni | NS API | `gateway.apiportal.ns.nl/disruptions/v3` | **401** | JSON | chiave gratuita | – | tempo reale | parziale (non provato) |
| 28 | IE / AU / NZ / CA treni | Irish Rail XML 200; Transport NSW `api.transport.nsw.gov.au/v1/gtfs/alerts/sydneytrains` **401** (chiave gratuita); VIA Rail `tsimobile.viarail.ca/data/allData.json` **200** (JSON EN/FR, 58 treni, alert) | 200/401/200 | XML/JSON | varia | – | tempo reale | parziale (pubblico domestico) |
| 29 | **AU NSW fire ban** | NSW RFS | `https://www.rfs.nsw.gov.au/feeds/fdrToban.xml` | **200** | XML: 21 distretti, `DangerLevelToday/Tomorrow`, `FireBanToday/Tomorrow` | nessuno | pagina feeds → 403 dal server; su data.nsw.gov.au il feed incendi è CC-BY, **per fdrToban non trovata** | oggi + **domani** | sì |
| 30 | AU VIC emergenze | Emergency Management Victoria | `https://emergency.vic.gov.au/public/osom-geojson.json` | 200 | GeoJSON CAP | nessuno | – | tempo reale | sì |
| 31 | US NPS parchi (Yosemite, Hawai'i Volcanoes) | National Park Service API | `https://developer.nps.gov/api/v1/alerts?parkCode=yose` → 403 senza chiave; con `api_key=DEMO_KEY` → **200** | 200 | JSON | chiave gratuita (DEMO_KEY: 30/ora, 50/giorno, basta per 2 letture/giorno) | pubblico dominio USA | tempo reale | sì |
| 32 | **US vulcani (Kilauea)** | USGS HANS | `https://volcanoes.usgs.gov/hans-public/api/volcano/getElevatedVolcanoes`, `.../notice/getRecentNotices/hvo` | **200** | JSON: colore, livello, "Daily Update" Kilauea ogni giorno (ultimo 9/10) | nessuno | pubblico dominio USA | tempo reale | sì |
| 33 | US Caltrans strade (Yosemite, catene I-80) | Caltrans | `https://roads.dot.ca.gov/roadscell.php?roadnumber=120` | 200 | HTML semplice e stabile ("No traffic restrictions are reported") | nessuno | – | tempo reale | sì |
| 34 | US uragani | NHC | `https://www.nhc.noaa.gov/CurrentStorms.json` | 200 | JSON | nessuno | pubblico dominio | tempo reale | sì |
| 35 | **HK tifoni** | Hong Kong Observatory | `https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warnsum&lang=en` | **200** (oggi `{}` = nessun avviso) | JSON in inglese | nessuno | Open data HKO (pagina letta) | tempo reale | sì |
| 36 | **TW "typhoon day off"** | DGPA (Executive Yuan) | `https://www.dgpa.gov.tw/typh/daily/ndse.html` | **200** | HTML stabile in inglese: "Update Time 2026/10/11 01:05 … Work and Classes as Usual" | nessuno | – | sera prima | sì |
| 37 | TW tifoni | CWA open data | `opendata.cwa.gov.tw/api/.../W-C0034-005` | 401 | JSON | chiave gratuita | – | – | parziale |
| 38 | ID Bali vulcani | MAGMA Indonesia (PVMBG) | `magma.esdm.go.id/v1/gunung-api/tingkat-aktivitas` 200 (HTML indonesiano); `/v1/vona/list` **403** | 200/403 | HTML | – | – | – | parziale |
| 39 | ID terremoti | BMKG | `data.bmkg.go.id/DataMKG/TEWS/autogempa.json` | 200 | JSON | nessuno | – | tempo reale | sì (non richiesto) |
| 40 | TH / VN / PH | TMD API 200 (stazioni vuote), NCHMF 200 HTML, PAGASA 200 HTML (1,7 MB) | 200 | HTML/JSON | – | – | – | parziale / no |
| 41 | MX sargasso | Red de Monitoreo del Sargazo (sargazo.red, redsargazo.org), SEMAR, Quintana Roo | 000 / 000 / 200 (pagina generica) / 200 (generica) | – | – | – | – | **non trovato** (il sito dedicato esistente, sargassummonitoring.com, è privato e basato su Facebook) |
| 42 | MX uragani / Popocatépetl | CONAGUA 500; CENAPRED 000; gob.mx "Challenge Validation" | 500/000 | – | – | – | – | no |
| 43 | HR traghetti / strade | Jadrolinija (`/en/news` 200, pagine cambi orario 404), HAK 200 HTML croato | 200 | HTML | – | – | – | parziale (e domanda 0/3) |
| 44 | Google Trends (per i volumi) | – | `trends.google.com/trends/api/explore` | **429** | – | – | – | – | no (volumi non misurabili da server) |

Non trovate oggi (nessuna fonte ufficiale strutturata): Acropoli/Louvre/Colosseo/Pompei/Vaticano "closed today"; Amalfi/Cinque Terre chiusure; scioperi in GR, PT, DE, BE, NL, IE, AT, NO (nessun registro, come FR/ES); sargasso Messico; Bali VONA (403).

---

## 3. Classifica delle candidate che PASSANO

Ipotesi comuni per i ricavi (da non vendere come promessa): RPM Tier 1 **5-12 $**; affiliazioni viaggio **1,5-5 $ per 1.000 visite**; cambio 1 $ ≈ 0,92 €. I **volumi non sono misurabili** dal server (Trends 429): le visite sotto sono **stime di ordine di grandezza** basate sul tipo di domanda e sulla stagionalità, con l'ipotesi che la pagina arrivi nei primi 3 risultati su una parte delle query. Ore: riuso di `italystrikes/genera.py` (1.427 righe: layout, oggi/domani nel browser, `vista.json`, workflow GitHub Actions).

### 3.1 **Venezia acqua alta oggi / domani** — satellite di Italy Strikes Today (passa; primo da fare)
- **Domanda**: 3/3 su 7 seed ("venice acqua alta today", "venice high tide today", "venice flooding today live", "venice tide chart today"). Stesso pubblico del sito scioperi.
- **Fonte**: #1 `previsione.json` (CC-BY, 3 aggiornamenti/giorno, 3-4 giorni di previsione, min/max in cm) + #2 `livello.json` (tempo reale). Testo da tradurre: solo "min/max", data e cm; soglie ufficiali del Centro Maree (80 cm, 100 cm, 110 cm, 140 cm) da riportare come definizioni dell'ente, non come consigli nostri.
- **Concorrenza**: nessun sito inglese dedicato "today" (ricerche `venice acqua alta today`, `acqua alta forecast today`: solo giornali 2019-2023, blog, pagina del Comune in italiano bloccata ai robot). App ufficiale "Hi!Tide" in italiano/inglese.
- **Ricavo prudente** (stima): 20-60k visite/anno molto stagionali (ottobre-gennaio, picchi enormi nei giorni di marea ≥ 110 cm, quando i giornali del mondo ne parlano) → pubblicità 100-650 € + affiliazioni (stivali/assicurazione/hotel/transfer) 30-300 € = **0,2-1,0k €/anno da solo**; passa la soglia di 1.500 € solo come parte della rete Italia (link interni, stessa lista email). Lo scrivo chiaramente: **da solo non passa il criterio del ricavo**, ma costa poco e rafforza il sito madre.
- **Ore**: 6-10 (lettore JSON, pagine today/tomorrow/this-week, tabella livelli, grafico semplice, workflow 2-3 volte al giorno).
- **Rischi**: il file può cambiare nome o struttura senza avviso (nessuna versione); responsabilità: riportare solo i numeri dell'ICPSM con ora di emissione, mai "potete andare a San Marco"; MOSE: non prevedere noi se si alza (lo dice solo il Comune/Consorzio); stagionalità estrema.
- **Test tecnico (soglie)**: 14 giorni di letture silenziose 3 volte/giorno → **≥ 95 % risposte 200**, `DATA_PREVISIONE` nuova **≥ 2 volte/giorno** in ≥ 12 giorni su 14, orizzonte ≥ 3 giorni in ogni lettura. Se passa, si costruisce.

### 3.2 **Islanda: strade / F-roads / allerte / eruzione oggi** (passa)
- **Domanda**: 3/3 su 10 seed ("iceland road conditions today", "iceland road closures today map", "iceland f roads status/open", "is golden circle open today", "iceland eruption today", "iceland weather warning today/tomorrow"). Pubblico USA/UK quasi puro (2,2 milioni di turisti/anno, quasi tutti anglofoni, quasi tutti in auto).
- **Fonti**: #14 strade (CC BY 4.0, 974 tratti, codici di stato), #16 allerte meteo in inglese, #17 vulcani con colore e testo in inglese. Tre fonti, tutte senza token, tutte JSON: rispetta la regola "≤ 3 fonti".
- **Concorrenza**: le fonti ufficiali hanno già l'inglese (umferdin.is/road.is, safetravel.is, vedur.is) e sono forti nei risultati; giornali (Iceland Monitor, Grapevine). Nessun sito privato dedicato "today". Il nostro vantaggio sarebbe la **risposta in una frase** ("Ring Road open; 7 tratti chiusi; F-roads: 100 non in servizio; allerta vento gialla Sud da domani 22:00") e le pagine per itinerario (Golden Circle, Ring Road, South Coast, Westfjords, Highlands).
- **Ricavo prudente** (stima): 40-120k visite/anno (picco giugno-settembre per F-roads, ottobre-aprile per neve/tempeste, picchi enormi a ogni eruzione) → pubblicità 200-1.300 € + affiliazioni **noleggio auto** (le più ricche del settore in Islanda) 150-600 € = **0,4-1,9k €/anno a 18 mesi**; con un'eruzione nell'anno, più. Passa la soglia solo nello scenario medio-alto: lo dico.
- **Ore**: 14-20 (mappa codici islandese → inglese, raggruppamento per itinerario, allerte CAP, vulcani, workflow ogni 3-6 ore; nessuna mappa grafica).
- **Rischi**: API "2014_1" senza documentazione pubblica trovata (Swagger non raggiunto), può cambiare; licenza CC BY 4.0 con attribuzione precisa (nome IRCA, dataset, data di scarico); **responsabilità alta** (guida in Islanda): solo "lo dice la Vegagerðin alle ore X", link e 1777; le pagine ufficiali inglesi possono tenere il primo posto per sempre.
- **Test tecnico (soglie)**: 14 giorni, letture ogni 3 ore → ≥ 95 % 200; `DagsKeyrtUt` più recente di 2 ore in ≥ 90 % delle letture; CAP: almeno 1 allerta vista con `onset` futuro (anticipo misurato); in parallelo controllare in Search Console se "iceland road conditions today" è dominata al 100 % da umferdin.is (se sì, ridurre la stima).

### 3.3 **Londra: chiusure della Tube questo weekend / sciopero domani** (passa, con concorrenza forte)
- **Domanda**: 3/3 su 8 seed ("tube closures this weekend (map)", "tube closures tomorrow/today/this week", "is there a tube strike today", "tube strike tomorrow", "london underground strikes this week"). È il bisogno con più volume tra quelli trovati (Londra 20 milioni di visitatori stranieri + residenti).
- **Fonte**: #12 TfL Unified API: senza chiave 50 richieste/minuto (bastano 2-4 al giorno); con **date future** restituisce le chiusure programmate (esempio reale scaricato: weekend 17-18 ottobre, District e Piccadilly). Licenza chiara, uso commerciale consentito con credito.
- **Concorrenza**: TfL stessa (status in inglese), **Time Out** (articolo settimanale "full list of tube closures this weekend", scritto a mano), Citymapper, Londonist. Nessun sito automatico dedicato. Rischio concreto di non superare TfL/Time Out su Google.
- **Ricavo prudente** (stima): 30-100k visite/anno se si entra nei primi 5 risultati (UK RPM alto, pubblico misto residenti/turisti) → pubblicità 150-1.100 € + affiliazioni (Oyster/transfer/hotel, deboli per residenti) 50-250 € = **0,2-1,35k €/anno a 18 mesi**. Sotto la soglia nello scenario basso; sopra solo se batte Time Out su "this weekend".
- **Ore**: 10-16 (lettore Status con date, pagine "this weekend / next weekend / today / tomorrow / per linea", archivio settimanale che Time Out non ha, workflow ogni 6 ore).
- **Rischi**: TfL cambia l'API con preavviso sul forum (gestibile); gli **scioperi** nella Tube compaiono nello stato TfL solo pochi giorni prima (come in Francia): la pagina "strike" sarebbe spesso vuota; stagionalità bassa.
- **Test tecnico (soglie)**: 4 settimane: entro il **martedì** la query con le date del weekend seguente deve contenere ≥ 1 chiusura programmata in ≥ 3 settimane su 4 (misura dell'anticipo); ≥ 98 % 200; confronto a campione con la lista Time Out del venerdì (≥ 90 % di coincidenza).

### 3.4 **Giappone: Shinkansen / treni Tokyo / tifoni oggi** (passa SOLO con un token gratuito ancora da provare; oggi non costruibile)
- **Domanda**: la più forte e la più "turistica" di tutto lo studio: 3/3 su 12 seed ("shinkansen status today/tomorrow", "is the shinkansen running today", "tokyo train delays today live", "jr east status live", "japan typhoon today", "typhoon japan flights cancelled today", "narita flights cancelled today"). Il Giappone è la meta extraeuropea più cercata da USA/AU.
- **Vuoto reale**: la pagina inglese di JR Central **oggi reindirizza al giapponese** (script nel HTML scaricato); JR East blocca i server; l'unico sito inglese che prova a rispondere (japantrain.net, "Shinkansen status today") è un'agenzia biglietti con un articolo fermo al 2 maggio 2026. Nessun sito automatico in inglese.
- **Fonti**: tifoni **sì** (#10 JMA, JSON, licenza aperta). Treni: **oggi no** (#6, #7); JR West parziale (#8); **ODPT (#9) richiede un token gratuito** da sviluppatore (come PRIM in Francia): serve l'account di Massimiliano (10 minuti) e poi un test di 2-4 settimane per vedere se copre JR East Shinkansen e Tokyo Metro con testi utilizzabili.
- **Ricavo prudente** (stima, se la fonte treni c'è): 60-200k visite/anno (stagione tifoni agosto-ottobre, neve gennaio-febbraio, terremoti) → pubblicità 300-2.200 € + affiliazioni (JR Pass/biglietti Shinkansen, eSIM, assicurazione: tra le più ricche) 200-1.000 € = **0,5-3,2k €/anno**; l'unica candidata con potenziale "medio-grande".
- **Ore**: 20-30 (ODPT + JMA + JR West; traduzione delle frasi d'esercizio giapponesi a regole fisse, come per l'italiano).
- **Rischi**: senza ODPT non c'è nulla; condizioni d'uso ODPT per uso commerciale da leggere; frasi giapponesi non standard; responsabilità bassa (si riporta lo stato dell'operatore).
- **Test tecnico (soglie)**: Massimiliano crea l'account ODPT → 21 giorni di letture ogni ora di `odpt:TrainInformation` → deve includere `odpt.Operator:JR-East` con Shinkansen e `TokyoMetro`, ≥ 95 % 200, ≥ 1 evento reale (ritardo/sospensione) letto con testo in giapponese traducibile a regole. Se JR East manca da ODPT → **NON PASSA** e si chiude.

Ordine consigliato: **3.1 Venezia subito** (costa poco, stesso pubblico), poi **3.4 Giappone test token** (10 min di Massimiliano, alto potenziale), poi 3.2 Islanda, infine 3.3 Londra. Mai due costruzioni insieme (regola della catena).

---

## 4. Scartate e perché

| Candidata | Domanda | Fonte | Perché scartata |
|---|---|---|---|
| Scioperi Grecia (Atene metro/generale, traghetti) | 3/3, fortissima | hcg.gr, ynanp.gr, gov.gr, culture.gov.gr **403**; sindacati non ufficiali | nessun registro pubblico; stesso schema di FR/ES |
| Traghetti Grecia cancellati / sailing ban | 3/3 | nessuna fonte ufficiale leggibile (Guardia costiera 403, porti senza elenco) | fonte assente; i siti privati (Ferryhopper) non sono ufficiali |
| Scioperi Portogallo (Lisbona metro, treni, aeroporto) | 3/3 | DGERT: solo statistiche mensili PDF; CP/Metro: app JS / API con chiave | nessun elenco dei preavvisi |
| Scioperi Germania / Belgio / Olanda / Irlanda / Norvegia / Austria / Svizzera | 3/3 (tranne AT/CH 0/3) | DB 404/403; SNCB 403 (iRail non ufficiale); NS 401; nessun registro | come FR/ES: anticipo 1-3 giorni solo nei flussi operatori |
| Spagna / Francia | 3/3 | già testate il 10/10 (studi 10 e 11) | NON PASSANO (anticipo 2-3 giorni) |
| Etna / Stromboli / Catania aeroporto oggi | 3/3 | INGV: elenco comunicati non nel HTML (wrapper), RSS 404; VONA idem | fonte non leggibile oggi; **da riprovare** cercando l'applicazione interna INGV (sarebbe un buon satellite Italia) |
| Amalfi, Cinque Terre, Pompei, Colosseo, Vaticano, Louvre, Acropoli, Sagrada Família, Alhambra "closed today" | 3/3 | nessuna fonte strutturata (404/403/HTML libero) | non trovato |
| Hong Kong segnale tifone oggi | 3/3 | HKO JSON in inglese, aperta (ottima) | l'Osservatorio è già perfetto in inglese e domina; pubblico Tier 1 piccolo; stagionale → ricavo stimato < 1.000 €/anno |
| Kilauea / Hawaii vulcano oggi | 3/3 | USGS HANS JSON, pubblico dominio (ottima) | USGS e NPS rispondono già in inglese ogni giorno; solo USA; stima < 1.500 € |
| Yosemite aperto oggi / Tioga Pass / catene I-80 | 3/3 | NPS API (DEMO_KEY ok), Caltrans HTML | NPS in inglese domina; solo USA domestico |
| NSW/Victoria total fire ban today | 3/3 (ma utenti australiani) | RFS XML oggi+domani (ottima); licenza del feed non trovata | non è un bisogno di viaggio: pubblico residente di un solo mercato; RFS domina |
| Taiwan "typhoon day off tomorrow" | 3/3 | DGPA HTML inglese stabile (ottima) | pubblico residenti/espatriati, pochi turisti Tier 1; eventi 3-6 l'anno |
| Bali cenere / aeroporto chiuso | 3/3 | MAGMA HTML indonesiano; VONA 403; VAAC Darwin 000 | fonte instabile; eventi rari; giornali australiani già coprono |
| Cancún / Tulum sargasso oggi | 3/3 (USA fortissimo) | nessuna fonte ufficiale trovata (rete di monitoraggio irraggiungibile, pagine governative generiche) | fonte assente; esiste già un sito privato dedicato (non ufficiale) |
| Thailandia / Vietnam / Filippine tifoni e alluvioni | 3/3 | HTML pesanti, nessun JSON utile trovato | fonte e responsabilità |
| Svizzera SBB / Olanda NS / VIA Rail / Amtrak / Sydney Trains / NZ strade | 3/3 | SBB e VIA aperte; NS e TfNSW con chiave | operatori già perfetti in inglese; pubblico domestico |
| Festivi domani (Giappone, Italia, Spagna, Francia), negozi aperti domenica | 3/3 | calendari ufficiali statici | timeanddate.com domina; non è un dato "oggi" |
| Impianti sci aperti oggi (Zermatt, Chamonix, Whistler, Niseko) | 3/3 | nessuna fonte ufficiale unica (ogni comprensorio ha il suo sito) | > 3 fonti per pagina |
| Bandiere spiaggia / meduse | 3/3 ma USA domestico | nessuna fonte unica | fuori pubblico |
| Croazia traghetti / strade | **0/3** | Jadrolinija 404 sulle pagine utili | nessuna domanda |

---

## 5. Risposta onesta alla domanda di Massimiliano ("possibile che in tutto il mondo abbiamo trovato solo questo?")

Sì, è possibile, e oggi ho le prove del perché. Il modello funziona quando si incastrano **quattro cose insieme**: (1) una domanda quotidiana in inglese, (2) una fonte ufficiale unica, gratuita e leggibile da un programma, (3) quella fonte scritta nella lingua locale o con pessima usabilità, così che nessuno l'abbia già tradotta in una pagina "today", (4) un **anticipo** che permette pagine "domani / questa settimana / mese" (è quello che fa indicizzare e tornare la gente).

- La **domanda (1) c'è dappertutto**: 254 combinazioni su 297 con "today/tomorrow" in tutti e tre i mercati. Google suggerisce "oggi" per qualunque cosa.
- La **fonte (2) è rara**: su ~250 URL ufficiali, 18 sono aperte e strutturate. Molti enti bloccano i server (JR East, Guardia costiera greca, gov.gr, Comune di Venezia, Metro Madrid, RATP, ADP, Schiphol) o pubblicano solo pagine JavaScript (JR Central, ODPT, CP).
- Dove la fonte è aperta, quasi sempre **(3) è già in inglese e ottima** (TfL, road.is, HKO, USGS, NPS, SBB, VIA, RFS): il bisogno lo copre l'ente stesso, e Google lo premia. Il nostro spazio è una fetta.
- **(4) l'anticipo esiste solo in Italia.** Scioperi in FR, ES, GR, PT, DE, BE, NL, IE, NO, AT: nessun registro. Chiusure Tube: 2-4 settimane (buono). Maree Venezia: 3-4 giorni. Strade Islanda, tifoni, vulcani: tempo reale, zero anticipo.

Quante opportunità "grandi" esistono con questo modello nel mondo? Con le prove di oggi: **zero grandi come Italy Strikes** (nessun'altra combina registro + anticipo + lingua locale + volume), **una potenzialmente medio-grande** (Giappone treni + tifoni, bloccata da un token da provare e dai blocchi di JR), **tre piccole-medie** (Venezia come satellite, Islanda, Londra), ognuna da 0,2 a 2k €/anno stimati, non 5-10k. La strategia scritta il 10/10 ("stesso Paese, più bisogni, più lingue") resta la più sensata: in Italia abbiamo la fonte unica e l'anticipo; all'estero troviamo solo fonti in tempo reale che l'ente già spiega in inglese.

Cosa farei: (a) Venezia subito come satellite (6-10 ore, stesso pubblico); (b) Massimiliano apre l'account ODPT (10 minuti) e un lettore silenzioso misura per 3 settimane se il Giappone è fattibile; (c) Islanda e Londra solo dopo i verdetti del 23-24/11, una alla volta, con i test a soglia scritti sopra; (d) riprovare l'Etna cercando la vera sorgente dei comunicati INGV (sarebbe il secondo satellite Italia).

---

## Fonti usate oltre ai download
- Licenza TfL: `tfl.gov.uk/corporate/terms-and-conditions/transport-data-service` (OGL v2 modificata, credito "Powered by TfL Open Data"); limiti: forum TfL (50/min anonimi, 500/min con chiave).
- Licenza Vegagerðin: `vegagerdin.is/vegagerdin/gagnasafn/vefthjonustur/terms-and-conditions` (CC BY 4.0, letta dal server).
- Licenza JMA: `jma.go.jp/jma/en/copyright.html` (Public Data License v1.0).
- Licenza dati Venezia: scheda dataset su dati.venezia.it ("Licenza: CC-BY", aggiornamento "in genere tre volte al giorno").
- NSW RFS: data.nsw.gov.au (feed incendi CC-BY; feed fire-ban senza licenza indicata).
- DGERT Portogallo: relazioni mensili "Relatório Avisos Prévios de Greve 2026.05-08" (PDF statistici).
- Concorrenza: ricerche web del 10/10 su "venice acqua alta today", "shinkansen status today" (japantrain.net, articolo del 2/5/2026), "tube closures this weekend" (Time Out, Citymapper, Londonist), "iceland road conditions today" (Iceland Monitor, Grapevine, umferdin.is), "is kilauea erupting", "hong kong typhoon signal", "total fire ban today", "athens strike tomorrow" (apergia.gr citato da OSAC: sito privato greco), "bali ash cloud".
