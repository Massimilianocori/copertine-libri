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
