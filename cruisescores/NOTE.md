# Cruise Health Scores (USA) – note di lavoro

Approvato da Massimiliano il 17/10/2026 (idea n. 1 di `studio-business/intelaiatura/idee-2026-10-15.md`).
Costruito il 17/10/2026. Sito statico in inglese americano per chi ha prenotato una crociera o sta scegliendo la nave:
"che voto ha preso la mia nave all'ispezione sanitaria del CDC?". Generato da `genera.py` in `sito/`.
Indirizzo previsto: `https://cruise-health-scores.netlify.app` (costante `URL_SITO` in `genera.py`, unico punto da cambiare).
Il sito Netlify NON è stato creato e nulla è stato pubblicato: lo crea Massimiliano (impostazioni più sotto).

## Cosa contiene (edizione del 17/10/2026)

| Tipo | Quante | Indirizzo | Regola |
|---|---|---|---|
| Home | 1 | `/` | ricerca della nave nel browser (`data/ships.json`), numeri chiave, scala dei voti, ultime 10 ispezioni, bocciate dell'anno, compagnie, domande |
| Navi | 217 | `/ships/<nome>/` | 206 attive (tutte quelle del Green Sheet) + 11 archiviate. Ultimo voto (anello), storia completa con grafico accessibile e tabella, infrazioni per esteso delle ultime 3 ispezioni raggruppate per area, punti tolti per voce, epidemie CDC, altre navi della compagnia |
| Elenco navi | 1 | `/ships/` | A-Z con ultimo voto; archiviate in fondo |
| Compagnie | 41 | `/cruise-lines/<nome>/` | media degli ultimi voti, migliore e peggiore, tabella delle navi, tutte le bocciature della compagnia, epidemie |
| Elenco compagnie | 1 | `/cruise-lines/` | classifica delle compagnie con almeno 5 navi + tabella di tutte |
| Classifiche | 6 | `/rankings/…` | indice; 100 nel 2026 e nel 2025; voti più bassi 2026 e 2025 (le 25 più basse + pari merito); tutte le 75 bocciature dal 1991 |
| Anni | 16 + indice | `/years/<anno>/` | dal 2010 al 2026 (manca il 2021: nessuna ispezione, crociere ferme per il COVID) |
| Epidemie | 1 | `/outbreaks/` | 64 epidemie gastrointestinali pubblicate dal CDC 2023-2026 |
| Guida | 1 | `/how-cdc-cruise-ship-inspections-work/` | chi ispeziona, quanto spesso, otto aree, come funziona il voto, cosa succede dopo, cosa il voto non dice (tutto citato dal CDC) |
| Fisse | 4 + 404 | methodology, about, contact (Netlify Forms con campo esca), privacy (niente strumenti di analisi né cookie) | |
| **Totale** | **290 indicizzabili** + 404 | tutte nella sitemap | peso del sito 15,3 MB (304 file; HTML 14,9 MB; pagina più pesante 112 KB) |

Titoli scritti per le ricerche viste nell'autocomplete: "<Nave> CDC Inspection Score: 95/100 (Jun 2026)", "<Compagnia> CDC Inspection Scores (2026): All N Ships",
"Cruise Ship Sanitation Scores 2026: All 197 CDC Inspections", "Cruise Ships With a Perfect 100 CDC Score in 2026", "Cruise Ship Norovirus Outbreaks 2026…".
JSON-LD: WebSite e Dataset (home), BreadcrumbList (tutte), Article (guida). Open Graph con `assets/og.png`.
Design: identità propria (marchio "anello del voto con spunta", blu notte + verde acqua, ottone per i dettagli; Newsreader per titoli e cifre,
Public Sans per il testo), tema chiaro/scuro con pulsante, colori dei voti con contrasto AA (testo bianco almeno 4,7:1 in tutti e due i temi), tabelle che su telefono diventano schede,
grafico in due proporzioni (computer/telefono). CSS e JS in file esterni con impronta nel nome (`assets/site.<hash>.css`, `app.<hash>.js`).
Pubblicità: `<div class="ad-slot">` vuoto e nascosto. Affiliati: solo SafetyWing ("Travel medical insurance", dicitura "Affiliate", `rel="sponsored nofollow noopener"`), su home, navi e compagnie.
In fondo a ogni pagina "Other useful tools": Before You Fly, Visa Income Checker, Flood Insurance Cost (URL presi dai rispettivi `genera.py`).

## Fonte (CDC Vessel Sanitation Program, letta dal server il 17/10/2026)

| Pagina | Indirizzo | Cosa ne prendiamo |
|---|---|---|
| Green Sheet | `https://wwwn.cdc.gov/InspectionQueryTool/InspectionGreenSheetRpt.aspx` | ultimo voto di ogni nave "attiva" (206 navi) e la frase "Inspections scores of 85 or lower are NOT satisfactory" |
| Ricerca | `https://wwwn.cdc.gov/InspectionQueryTool/InspectionSearch.aspx` | elenco di 325 navi e 71 compagnie; per ogni nave la ricerca "All Dates" (POST ASP.NET con `__VIEWSTATE`) dà tutte le ispezioni con compagnia, data e voto |
| Rapporto | `InspectionDetailReport.aspx?ColI=…` (serve la sessione) | infrazioni: numero della voce, luogo a bordo, testo per esteso |
| Riepilogo | `InspectionSummaryReport.aspx` (stessa sessione, subito dopo il rapporto) | punti tolti per voce: 100 − punti = voto, controllato su ogni rapporto |
| Pagine informative | `www.cdc.gov/vessel-sanitation/faq/`, `…/php/our-role/public-health-inspections.html`, `…/communication-resources/operational-inspections.html` | soglia (85 o meno = bocciata), due ispezioni l'anno senza preavviso, 6-8 ore, 1-5 ispettori, otto aree, tariffe |
| Epidemie | `www.cdc.gov/vessel-sanitation/cruise-ship-outbreaks/` (+ pagine 2025-2024 e 2023) | epidemie gastrointestinali pubblicate dal CDC dal 2023 |

- Soglia verificata sulla fonte: Green Sheet "85 or lower are NOT satisfactory"; FAQ "Cruise ships fail inspections when they score 85 or below". Sul sito: 86 o più = Passed.
- Dati del governo USA, pubblico dominio. Ogni pagina cita il CDC con link, la data dell'ispezione (pagine delle navi), "Data checked on" e dice che il sito non è del CDC e che un voto non è un giudizio di sicurezza.
- Il CDC non permette link diretti a un singolo rapporto (senza sessione rimanda al modulo): le pagine spiegano come ritrovarlo (scegli la nave, "All Dates", "Report").
- **Codifica**: lo strumento del CDC dichiara iso-8859-1 ma i dati sono in codifica Windows (°, ’): `scarica.py` legge in cp1252. Nel database del CDC molti apostrofi, virgolette, trattini e gradi sono diventati "?": `estrai.py` li ripristina solo nei casi evidenti (restano una decina di "?" ambigui su ~8.000 infrazioni).
- **www.cdc.gov** risponde 403 (Akamai) alle richieste Python ma non a `curl`: le pagine informative si scaricano con `curl`. Se non arrivano resta la copia in cache e lo scarico dei voti continua.
- **Nomi di persone**: `estrai.py` toglie titolo + nome proprio (Mr./Mrs./Ms./Dr./Captain + Nome) e `verifica.py` ricontrolla il testo pubblicato. Nei 614 rapporti scaricati c'erano solo 2 nomi di passeggeri tra virgolette (tolti, vedi i controlli); per il resto solo ruoli ("the chief officer", "Officer Mess" = mensa ufficiali). Non pubblichiamo le "Corrective Action Statement" (contengono firme del personale) né le raccomandazioni (testo standard ripetuto).

## Navi con pagina e navi escluse

- **Attive (206)**: tutte le navi del Green Sheet del 17/10/2026. L'ultima ispezione pubblicata dal CDC è del 29/8/2026 (nessuna ispezione nuova sul sito del CDC da 7 settimane: da tenere d'occhio).
- **Archiviate con pagina (11)**: nel modulo ma non nel Green Sheet, ultima ispezione dal 1/1/2023 e almeno 3 ispezioni: Artania, Balmoral, Celebrity Millennium,
  Costa Deliziosa, Le Boreal, Mein Schiff 6, MSC Magnifica, Norwegian Spirit, Seven Seas Navigator, Silver Muse, Viking Star. Hanno un avviso "No longer in the CDC's current list".
- **Escluse (108)**, elenco completo con il motivo in `dati/escluse.json`:
  - 66 navi sono nell'elenco del modulo ma la ricerca "All Dates" non restituisce nessuna ispezione (il CDC le ha "archiviate": es. AIDAprima, Costa Diadema,
    MSC Seaview, Spectrum of the Seas, Viking Jupiter, Le Commandant Charcot, Disney Adventure, Explora III). Senza nemmeno un voto la pagina sarebbe vuota.
  - 39 navi hanno l'ultima ispezione prima del 2023 (dal 1990 al 2020): dati vecchi di anni, pagina poco utile e probabilmente navi rinominate o demolite.
  - 3 navi con ispezioni dal 2023 ma meno di 3 in tutto (Amera 2, Star Breeze 1, Viking Saturn 1): troppo poco per una pagina.
  - Le ispezioni di tutte queste navi restano nei totali degli anni e nella lista delle bocciature (senza link).
- Nomi delle compagnie: 71 nel modulo; 41 hanno almeno una nave con pagina (dopo aver unito Viking ×3, CMI ×2, V.Ships ×2).

## File

| File | A cosa serve |
|---|---|
| `raccolta/scarica.py` | scarica nel `cache/` (fuori da git, `.gitignore`): Green Sheet, modulo, storia di ogni nave, rapporti + riepiloghi delle ultime 3 ispezioni di ogni nave con pagina, pagine informative ed epidemie. Una richiesta ogni 1-2 secondi, un collegamento alla volta, ripresa automatica (i file già scaricati non si riscaricano; scrittura atomica). Si ferma se il CDC cambia il modulo o il Green Sheet |
| `raccolta/comune.py` | lettura delle pagine CDC e regola delle navi pubblicate (`N_RAPPORTI = 3`, `ARCHIVIATE_DAL = "2023-01-01"`, `ARCHIVIATE_MIN_ISPEZIONI = 3`) |
| `raccolta/estrai.py` | dalla cache scrive `dati/`: `navi.json`, `rapporti.json`, `ispezioni.json` (tutte le ispezioni di tutte le 325 navi), `epidemie.json`, `escluse.json`, `fonti.json`. Si ferma se 100 − punti ≠ voto, se il Green Sheet non coincide con la storia, se la FAQ del CDC cambia soglia |
| `dati/compagnie.json` | nome mostrato di ogni compagnia (scritto a mano; es. "Carnival Cruise Lines, Inc." → "Carnival Cruise Line"; le tre società Viking e le due CMI/V.Ships diventano una pagina). Se il CDC aggiunge una compagnia, `estrai.py` lo segnala |
| `dati/affiliati.json` | riquadri di affiliazione: attivo solo SafetyWing (campagna `cruise-health-scores`); "crociere" ha l'URL vuoto e resta nascosto finché non c'è un'affiliazione vera |
| `genera.py` | genera `sito/` (pochi secondi), `sito/netlify.toml`, sitemap, robots, `data/ships.json` (ricerca nel browser) |
| `verifica.py` | controlli (vedi sotto); `--browser` lancia `verifica_browser.js`; `--senza-rete` salta il confronto con il CDC |
| `verifica_browser.js` | Playwright a 375 e 1280 px, tema chiaro e scuro: niente scorrimento orizzontale né elementi fuori schermo, niente errori JS o richieste fallite, ricerca e pulsante del tema funzionanti; screenshot (cartella in `CHS_SCREENSHOT`, altrimenti `cache/screenshot/`) |
| `grafica/` | font Newsreader (titoli) e Public Sans (testo), licenza OFL inclusa; `og.html` + `og.js` → `og.png` (immagine di condivisione) |

Pubblicità: spazio `<div class="ad-slot">` vuoto (nascosto dal CSS finché vuoto) dopo la scheda principale di ogni pagina.

## Aggiornamento settimanale (comandi esatti, dalla radice del repository)

```
python3 cruisescores/raccolta/scarica.py        # 5-10 minuti: Green Sheet, storie delle navi con ispezioni nuove, rapporti nuovi
python3 cruisescores/raccolta/estrai.py
python3 cruisescores/genera.py
python3 cruisescores/verifica.py --browser      # confronto con il CDC su 15 navi a caso + controlli + Playwright
```
Poi commit di `cruisescores/dati` e `cruisescores/sito` (una pubblicazione Netlify a settimana al massimo: 15 crediti).
- Se `scarica.py` esce con codice 2 qualche rapporto non è arrivato: rilanciarlo (riprende da dove era).
- Se si ferma con "Il modulo del CDC è cambiato" o "Il Green Sheet è cambiato": il CDC ha modificato lo strumento; controllare a mano prima di pubblicare (rischio n. 1 dello studio).
- Controllo veloce senza scaricare le storie: `python3 cruisescores/raccolta/scarica.py --controllo`.
- Per riscaricare tutte le storie (es. una volta al mese): `python3 cruisescores/raccolta/scarica.py --tutto`.
- Al cambio d'anno le classifiche dell'anno nuovo (`rankings/perfect-scores-2027/`, `lowest-scores-2027/`) nascono da sole; quelle dell'anno prima restano (si tengono l'anno in corso e il precedente).

## Impostazioni Netlify (da fare da Massimiliano)

- Collegare il repository GitHub, ramo `ccr-b7fd6b9e-n096cr`.
- **Base directory: `cruisescores/sito`** · **Build command: vuoto** · **Publish directory: `.`** (relativa alla base).
- `cruisescores/sito/netlify.toml` (scritto da `genera.py`) ha già `publish = "."`, `command = ""`, la regola
  `ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."` (pubblica solo se cambia `cruisescores/sito`) e le intestazioni di sicurezza.
- Nome del sito: `cruise-health-scores` (se diverso, cambiare `URL_SITO` in `genera.py` e rigenerare).
- Search Console: la meta di verifica `btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI` è in ogni pagina; poi inviare `sitemap.xml`.
- Moduli: attivare le notifiche email del modulo "contact" (Netlify Forms, con campo esca anti-spam).

## Controlli fatti il 17/10/2026 (`python3 cruisescores/verifica.py --browser`: tutti superati)

- 291 pagine HTML (290 nella sitemap + 404), tutte con risposta 200 da un server locale; indirizzo inesistente → 404.
- Link interni e ancore tutti validi; un solo h1, title e description per pagina; canonical = sitemap; meta di Search Console in ogni pagina; JSON-LD valido.
- Nessuna pagina senza voto (navi: l'anello mostra l'ultimo voto dei dati; la tabella della storia ha tutte le ispezioni).
- Fonte CDC con link + "Data checked on October 17, 2026" + avviso "not affiliated… not a safety rating" in ogni pagina con dati; data dell'ispezione su ogni nave.
- 614 rapporti: in tutti 100 − punti tolti = voto; data e voto coincidono con la storia; Green Sheet = ultima ispezione di ogni nave attiva.
- Nomi di persone: trovati e tolti 2 nomi di passeggeri tra virgolette ('John S.', 'Jack', Celebrity Summit 10/3/2025). "Dr. Inks, PH.d." è un bar (Carnival Jubilee) e resta.
- Parole vietate: nessuna. Unica eccezione documentata: un ristorante degli yacht Ritz-Carlton (Ilma, Evrima) ha lo stesso nome di un modello di
  intelligenza artificiale e compare nei rapporti del CDC come "Deck 11 - <nome>"; è un dato ufficiale e resta. `verifica.py` lo esclude solo in quella forma.
- Confronto con la fonte (riscaricata dal CDC durante la verifica) su 15 navi a caso: storia completa, ultimo voto, punti e numero di infrazioni del rapporto più
  recente. Tutte OK: Norwegian Getaway, Oasis of the Seas, Celebrity Constellation, Norwegian Encore, Oceania Regatta, Explora I, Carnival Pride, MSC Seascape,
  MSC World America, Oceania Nautica, Artania, MSC Grandiosa, Seabourn Encore, Pearl Mist, Europa 2.
- Playwright: 108 caricamenti (27 pagine × 375/1280 px × chiaro/scuro): niente scorrimento orizzontale, niente elementi fuori schermo, niente errori JS o
  richieste fallite; ricerca ("wonder", "carnival", nessun risultato) e pulsante del tema funzionanti.
- Scarico iniziale: 1.507 + 62 richieste al CDC, 0 errori, circa 45 minuti (una richiesta ogni 1-2 secondi). L'aggiornamento di prova (seconda esecuzione) è durato 1 minuto e mezzo.

## Punti da tenere d'occhio

1. Il CDC può cambiare o spegnere lo strumento (tagli del 2025): `scarica.py` si ferma se cambia; `--controllo` lo dice in pochi secondi.
2. Gli anni prima del 2023 sono incompleti: il CDC tiene nella ricerca solo le navi ancora nel suo elenco (scritto sulle pagine degli anni e nella metodologia).
3. Nel 2021 non c'è nessuna ispezione e nel 2020 e 2022 poche (crociere ferme per il COVID): niente pagina per il 2021.
4. Alcune compagnie del CDC sono società di gestione, non marchi: "Carnival UK" (navi Cunard e P&O nei nomi), "MSC Cruise Management" (anche Explora I), "Bernhard Schulte Cruise Services". Si mostra il nome del CDC accorciato, senza attribuire marchi non scritti dalla fonte.
5. Le epidemie sono collegate alla nave quando il nome coincide (o finisce con il nome scritto dal CDC, es. "Insignia" → "Oceania Insignia"); quelle senza pagina compaiono senza link.
6. Fase 2 possibile (studio): una pagina per ogni rapporto d'ispezione; oggi i rapporti completi sono solo gli ultimi 3 per nave (per non appesantire lo scarico: ~2 richieste per rapporto).

## Revisione indipendente del 17/10/2026

- Fatti ricontrollati dal CDC con script propri (fuori da `raccolta/`): Green Sheet (206/206 navi uguali), storia completa di tutte le 325 navi del modulo
  (4.097 ispezioni, 75 bocciature dal 1991, totali per anno, 49 voti da 100 nel 2026: tutto uguale), 22 navi a caso con un'infrazione del rapporto più recente,
  64 epidemie (nave, date, causa, compagnia) contro le tre tabelle CDC, medie e classifica delle compagnie ricalcolate.
- Corretti: medie delle compagnie con un decimale (Disney mostrava "100" con media 99,57), titoli e testi delle compagnie con una sola nave ("All 1 Ships"),
  plurali (grafico, riquadri, descrizioni), guida e FAQ riscritte solo con frasi delle pagine CDC citate (tolti "13 or more passengers", esempi inventati,
  "in one day"; aggiunto che il CDC "may also post other outbreaks of public health significance": Allure of the Seas 2024 era sotto il 3%),
  frase sui ritardi in metodologia (non verificabile) sostituita da una nota onesta in ogni riquadro fonti ("most recent inspection the CDC has published is from…"),
  avviso sulle navi del Green Sheet senza ispezioni da più di un anno, "Independent site, not the CDC" nella testata, `rel="sponsored nofollow"`,
  "Wonder Of The Seas" → "Wonder of the Seas", apostrofi "O?Sheehan’s" e "April?3 May" (`estrai.py`), descrizioni ≤ 160 caratteri, tabelle su telefono più compatte.

## IndexNow (26/10/2026)
- IndexNow: file chiave scritto dal generatore; invio con studio-business/strumenti/indexnow.py. Costante `CHIAVE_INDEXNOW` in `genera.py` accanto a `SCRIPT_CONTATORE` (chiave pubblica, uguale in tutti i siti della rete); `extra()` scrive `sito/<chiave>.txt` accanto a `robots.txt`, fuori dalla sitemap e non linkato. Nuovo controllo in `verifica.py` (`controlla_indexnow`): file presente, contenuto = chiave, non citato nella sitemap.

## Monetizzazione: come si attiva (30/10/2026)
- **Dove si scrive:** un solo file per tutta la rete, `studio-business/strumenti/monetizzazione.json` (`adsense_client`, `adsense_siti`, domini di affiliazione ammessi). In una riga: `python3 studio-business/strumenti/monetizzazione.py attiva ca-pub-XXXXXXXXXXXXXXXX cruisescores`, poi `python3 cruisescores/genera.py`. Il nome del sito nel file è `cruisescores` (`SITO_ID` in `genera.py`).
- **Cosa cambia con AdSense acceso:** script ufficiale nel `<head>` di ogni pagina (annunci automatici, nessun blocco manuale), `sito/ads.txt` con `google.com, pub-…, DIRECT, f08c47fec0942fa0`, sezione «Advertising (Google AdSense)» in `privacy.html`, descrizione senza più «no cookies and no tracking», frase sulla California aggiornata; la frase sui cookie diventa «GoatCounter non usa cookie, la pubblicità sì». Prima di pubblicare: in AdSense accendere il messaggio di consenso certificato di Google (Privacy e messaggi, regolamenti europei: UE/SEE, Regno Unito, Svizzera), che la privacy descrive.
- **Link di affiliazione:** `dati/affiliati.json` (campo `url`; SafetyWing di nuovo attivo dal 30/10/2026 nella voce `assicurazione`; le altre voci solo verso domini ammessi). Ammessi solo verso i domini di `domini_affiliazione`, con `rel="sponsored noopener"` e la riga di trasparenza (la aggiunge `riquadro_trasparenza()` se manca); con almeno un link la privacy aggiunge la sezione sui link di affiliazione.
- **Come si verifica:** `python3 cruisescores/verifica.py --senza-rete`; controllo comune in `monetizzazione.py` (script e `ads.txt` solo con AdSense acceso, privacy coerente, nessun dominio fuori elenco o bloccato, Amazon.it solo con `tag=`).
- **Con il codice vuoto o il sito fuori elenco l'output non cambia:** il 30/10/2026 `sito/` è stato rigenerato identico byte per byte.

## AdSense acceso e SafetyWing di nuovo attivo (30/10/2026)
- **AdSense:** `python3 studio-business/strumenti/monetizzazione.py attiva ca-pub-3750093987658434 cruisescores`, poi `python3 cruisescores/genera.py`. Script nel `<head>`, `sito/ads.txt`, privacy `/privacy.html` con «Advertising (Google AdSense)», descrizione senza «no cookies and no tracking», frase sulla California aggiornata. Da fare in AdSense: aggiungere il sito.
- **SafetyWing:** `dati/affiliati.json`, voce `assicurazione`: `url` di nuovo compilato (campagna `cruise-health-scores`), `attivo_dal` 2026-10-30, `nota_riattivazione`; `url_sospeso` e `nota_sospensione` tolti. Riquadro con «Affiliate» e riga di trasparenza su home, navi e compagnie: **258 pagine**. Il pulsante ora ha `rel="sponsored noopener"` come il resto della rete (prima `sponsored nofollow noopener`). Testi: «SafetyWing sells travel medical insurance for travellers and nomads online.» e avvertenza «check that the policy covers cruise travel, your age, every country on your itinerary and your dates» (aggiunta l'età: il pubblico delle crociere è spesso anziano e i piani hanno limiti di età).
- **Frasi corrette:** About, «Who we are»: la frase fissa «The site may show advertising and contains clearly marked affiliate links» ora viene da `frase_monetizzazione()` ed è vera in ogni combinazione (oggi: «The site shows advertising (Google AdSense) and contains clearly marked affiliate links (travel medical insurance); neither ever changes the data.»). Piè di pagina: «Some links are affiliate links and are marked as such» solo se c'è almeno un link (`ci_sono_affiliati()`). Privacy: riga che nomina SafetyWing quando il link è attivo; la frase su SafetyWing del testo senza pubblicità compare solo con il link attivo (`FRASE_SW`).
- **`verifica_browser.js`:** con AdSense Playwright segnalava «richiesta fallita: https://pagead2.googlesyndication.com/pagead/ping?e=1» (beacon di Google interrotto al cambio pagina). Ora le richieste ai server degli annunci (costante `PUBBLICITA`) ricevono una risposta vuota e non contano come errori; lo script e il suo indirizzo li controlla `monetizzazione.py`.
- **Controlli:** `python3 cruisescores/verifica.py --senza-rete --browser` → «Tutti i controlli superati» (108 caricamenti, 375 e 1280 px, chiaro e scuro); `monetizzazione.py verifica cruisescores` → AdSense acceso, 258 link di affiliazione in 258 pagine su 290, 0 errori; Playwright a 375 px su una pagina compagnia e su About con lo script AdSense caricato davvero: nessun errore JS, nessuno scorrimento orizzontale. Nessun commit.

## Rinforzo SEO per le ricerche USA e aggiornamento dati (31/10/2026)
Search Console (28 giorni al 29/10/2026): 287 impressioni, 4 clic, posizione media 19,8, in crescita; ricerche "cdc cruise ship inspections", "cruise score",
"cdc cruise ship inspections list", "cruise ship inspections". Autocomplete gl=us: "cdc cruise ship inspection scores", "cruise ship health inspection <compagnia>",
"<nave> cdc score", "cruise ship norovirus outbreaks 2026", "cleanest cruise lines", "failed cdc inspection cruise ship".
- **Dati aggiornati** (`scarica.py` + `estrai.py`, 44 richieste, 0 errori): il CDC ha pubblicato ispezioni fino al **17/10/2026** (prima 29/8). 3.706 ispezioni, 615 rapporti,
  205 navi attive + 12 archiviate (217 pagine nave). Due bocciature nuove: **Le Lyrial 83 (17/10/2026)** ed **Emerald Princess 78 (16/10/2026)**.
- **Pagine nuove (2)**, nella sitemap e linkate da home, classifiche, elenco compagnie e pagine compagnia:
  - `/rankings/cleanest-cruise-lines/` «Cleanest Cruise Lines 2026: Ranked by CDC Inspection Scores»: media di tutte le ispezioni CDC degli ultimi 12 mesi
    (dal giorno dopo lo stesso giorno di un anno prima fino all'ultima ispezione pubblicata: oggi 18/10/2025-17/10/2026, 274 ispezioni), solo compagnie con almeno
    5 ispezioni (`MIN_ISP_CLASSIFICA`; oggi 14), pari merito con la stessa media a un decimale; compagnie piccole a parte senza posto; navi con 100 a ogni ispezione (almeno 2).
    Avviso: il CDC non fa classifiche, «cleanest» = media dei voti sanitari, non giudizio di sicurezza. Oggi: Disney 99,0 (11 ispezioni), Oceania 98,8, Regent 98,6 … Princess 95,0.
  - `/rankings/year-over-year/` «Cruise Ship CDC Scores 2026 vs 2025»: anni dal 2023 (dati CDC completi) con ispezioni, navi, 100 (%), bocciate, epidemie e media;
    compagnie con almeno 3 ispezioni in tutti e due gli anni (`MIN_ISP_CONFRONTO`); navi che migliorano/peggiorano di più (10 + pari merito). 2026: 96,8 contro 96,0.
- **Pagine compagnia (41)**: titolo «<Compagnia> CDC Health Inspection Scores 2026: All N Ships» (accorciato sopra 66 caratteri), tabella **anno per anno dal 2010**
  (ispezioni, 100, voto più basso, bocciate, media; avviso sugli anni prima del 2023) e posto nella classifica degli ultimi 12 mesi nella prima risposta.
- **Prime risposte e titoli** delle pagine con impressioni: home «CDC Cruise Ship Inspections 2026: Scores of All 205 Ships» con h1 «CDC cruise ship inspection scores»
  e risposta in alto (ispezioni 2026, data e nave dell'ultima, media, bocciate, 100); `/years/2026/` «CDC Cruise Ship Inspections List 2026: All 209 Scores»
  (gli anni passati restano «Cruise Ship Sanitation Scores <anno>»); `/rankings/failed-inspections/` «Cruise Ships That Failed a CDC Inspection: All 77 Since 1991»
  con quante nell'anno e nell'anno prima e la tabella per compagnia; `/outbreaks/` «Cruise Ship Norovirus & GI Outbreaks 2026: CDC List (9 So Far)» con risposta
  sull'anno, tabella per anno e causa e tabella per compagnia (nome della tabella CDC: «Cunard Line» resta Cunard, non «Carnival UK»). Nessuna promessa nei titoli.
- Metodologia: nuova sezione «Rankings and comparisons» (finestra, minimi, pari merito, compagnia = quella scritta dal CDC al momento dell'ispezione).
- `verifica.py`: controlli **11-17** (cifre ricalcolate da `dati/*.json` senza le funzioni di `genera.py`): classifica 12 mesi, anno su anno, tabelle anno per anno delle
  41 compagnie e loro posto, epidemie per anno/norovirus/compagnia e titolo, bocciature (titolo, anno, somma per compagnia), prima risposta della home e titolo dell'anno,
  sitemap (lastmod = `scaricato_il` di `fonti.json`, mai nel futuro, pagine nuove presenti), title ≤ 70 e description ≤ 160 caratteri. Provati con errori finti: li trovano.
  `verifica_browser.js`: le due pagine nuove e Princess nel campione e negli screenshot.

### Revisione indipendente del 31/10/2026
- Riscaricati dal CDC con script propri: Green Sheet (205/205 navi, ultimo voto e data uguali), storia completa di 17 navi (207 ispezioni, tra cui Le Lyrial 83 del 17/10/2026
  ed Emerald Princess 78 del 16/10/2026: tutto uguale), tabella delle epidemie 2026 (9, nave, date e causa uguali). Ricalcolati: finestra 18/10/2025-17/10/2026
  (274 ispezioni), 14 compagnie con almeno 5 ispezioni (Disney 99,0 … Princess 94,96 → 95,0), 77 bocciature dal 1991 (la prima il 4/12/1991), medie 2026 96,82 e 2025 96,01.
- Corretti: titolo delle epidemie «Cruise Ship Norovirus Outbreaks 2026 … (9 So Far)» → «Norovirus & GI Outbreaks» (delle 9 del 2026 solo 5 sono norovirus,
  2 E. coli, 2 causa sconosciuta); `/rankings/year-over-year/` dice ora in un riquadro che medie e variazioni sono nostri calcoli dai voti CDC e non un giudizio di sicurezza;
  tooltip delle medie («Average of the latest scores» anche dove era la media delle ispezioni dell'anno o dei 12 mesi: `chip_media(m, titolo)`); titolo della nave
  Margaritaville at Sea Paradise di 71 caratteri (sopra 70 il titolo perde il mese); `verifica.py` controlla ora title ≤ 70.

### Monetizzazione: affiliazioni crociere (31/10/2026)
- Nessun link nuovo: in `monetizzazione.json` ci sono i domini di CruiseDirect/CJ e di Viator, ma **nessun URL di affiliazione ricevuto**; SafetyWing resta l'unico attivo.
  La voce `crociere` di `dati/affiliati.json` resta vuota (riquadro nascosto).
- Programmi da proporre a Massimiliano (pagine ufficiali lette il 31/10/2026 con curl):
  1. **CruiseDirect** (rete CJ), prenotazione crociere: «3% of the commissionable cruise fare», «45-day cookie» (https://www.cruisedirect.com/affiliates).
     Iscrizione: https://signup.cj.com/member/signup/publisher/?cid=965192#/branded . CJ approva marchio per marchio: con le impressioni in crescita si può chiedere ora,
     descrivendo il sito (217 navi, 41 compagnie, dati CDC settimanali). Posto naturale: pagine nave e compagnia («Compare prices for this cruise»).
  2. **Travel Guard** (AIG, rete CJ), assicurazione viaggio USA: paga «for every quote received» (importo non pubblicato; volantino del programma del 2019),
     iscrizione https://signup.cj.com/member/signup/publisher/?cid=1544502 (pagina https://www.travelguard.com/affiliate-program). **Attenzione:** i termini vietano di
     «discuss travel insurance coverage or the features of Travel Guard plans» e di raccomandare l'acquisto: andrebbe solo un banner neutro. Da valutare solo dopo CruiseDirect.
  3. **Viator** (escursioni nei porti, 8%, cookie 30 giorni): account già creato, in analisi (vedi `studio-business/affiliazioni-2026-10-17.md`). Quando arriva il link,
     va in `dati/affiliati.json` come nuova voce (dominio `viator.com` già ammesso).
