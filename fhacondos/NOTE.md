# FHA Approved Condos (USA) – note di lavoro

Approvato da Massimiliano il 17/10/2026 (idea n. 2 di `studio-business/intelaiatura/idee-2026-10-15.md`).
Test della fonte superato il 17/10/2026 (`TEST.md`: 100 % dei condomini, 0 errori su 20). Costruito il 17/10/2026.
Sito statico in inglese per il pubblico USA: "questo condominio è approvato per i mutui FHA?", con l'elenco ufficiale HUD.
Nome del sito: **ApprovedCondos**. Indirizzo previsto: `https://fha-approved-condos-list.netlify.app` (costante `URL_SITO` in
`genera.py`, unico punto da cambiare). Il sito Netlify NON è stato creato e niente è stato pubblicato: lo fa Massimiliano.

## Cosa c'è (edizione del 17/10/2026, dati HUD "as of 10/17/2026")

- **6.539 condomini approvati** in 48 Stati e territori (i "progetti" HUD: un condominio = una riga; le fasi non si contano due volte),
  **1.882 scaduti** e **133 ritirati** negli ultimi 24 mesi. 1.328 approvazioni scadono entro 6 mesi.
- Attenzione: i numeri dello studio del 15/10 (13.812, Virginia 2.510) erano righe "Both" del modulo, cioè progetti + fasi.

| Tipo di pagina | Quante | Regola |
|---|---|---|
| Home | 1 | ricerca nel browser per nome, città, CAP o ID HUD (`data/search.json`, 8.554 condomini), mappa a tessere degli Stati, contee e città principali, guide |
| Elenco degli Stati | 1 | `states/`: tutti i 54 Stati e territori del modulo con i conteggi |
| Stati e territori | 48 | almeno 1 condominio approvato o scaduto/ritirato di recente. Senza pagina (zero in tutto): Guam, Louisiana, Mississippi, Nebraska, Isole Vergini, West Virginia (controllato a mano: in Louisiana HUD ha 267 righe, tutte scadute da anni o respinte) |
| Contee | 109 | almeno **10** condomini approvati |
| Città | 179 | almeno **8** condomini approvati |
| Guide | 3 | `is-my-condo-fha-approved/`, `condo-not-fha-approved/`, `fha-vs-va-vs-warrantable-condos/` |
| Fisse | 4 + 404 | methodology, about, contact (Netlify Forms con honeypot), privacy; 404 non indicizzata |
| **Totale** | **345 indicizzabili** + 404 | tutte nella sitemap |

Perché queste soglie: con 10 condomini una pagina di contea ha una tabella vera (nome, via, CAP, unità, scadenza) e di solito qualche
scadenza nei 6 mesi e qualche scaduto recente; sotto i 10 la pagina sarebbe quasi solo testo fisso (contenuto "sottile"). Per le città
bastano 8 perché la ricerca per città ("fha approved condos denver") è la più frequente. Con soglia 5 sarebbero 181 contee e 288 città,
con 15 solo 89 e 85. Contare anche gli scaduti recenti non aggiunge pagine (sono pochi per luogo). I luoghi sotto soglia restano nella
tabella della pagina superiore e nella ricerca: **ogni condominio compare in almeno una tabella** (controllato da `verifica.py`).

Altre regole (in `genera.py`, funzione `scelte_pagine`):
- contea con lo stesso elenco dello Stato (District of Columbia): nessuna pagina di contea; città uguale allo Stato: nessuna pagina di città;
- città e contea quasi uguali (almeno il 90 % dei condomini in comune, es. Colorado Springs / El Paso County, Norfolk / Norfolk city):
  una sola pagina, quella della città, con il nome della contea nel titolo;
- la pagina dello Stato elenca tutti i condomini approvati, tranne la California (1.660, oltre `LIMITE_LISTA_STATO` = 700): lì elenca
  solo i 50 che non sono in una pagina di contea o città (la pagina sarebbe stata di 800 KB).

Ogni pagina di luogo ha: cifre principali (approvati, unità, scadenze entro 6 mesi, scaduti/ritirati 24 mesi), data "HUD data as of",
link al lookup ufficiale, **avviso** ("l'approvazione può cambiare, alcune approvazioni coprono solo certe fasi o edifici, confermare con
HUD e con la banca"), elenco delle scadenze dei prossimi 6 mesi, tabella completa con filtro, tabella dei recenti, link alle guide,
link a FloodCost della stessa contea o Stato se la pagina esiste in `floodcost/sito/`, fonte, blocco "Other useful tools" (FloodCost).
Before You Fly non è linkato: parla di voli, non c'entra con chi compra casa.

## Fonte

HUD FHA Condominium Lookup, `https://entp.hud.gov/idapp/html/condlook.cfm` (modulo ColdFusion, dati aggiornati ogni giorno, pubblico
dominio). Funzionamento in `TEST.md`. Per ogni Stato 3 ricerche, tipo "Project": approvati; scaduti con scadenza negli ultimi 24 mesi;
ritirati con data dello stato negli ultimi 24 mesi. 25 righe per pagina, una richiesta ogni 1,2-2 secondi: **317 richieste, circa 9 minuti**.
Curiosità vista il 17/10: la ricerca "Expired" restituisce anche 11 condomini con scadenza uguale alla data HUD e stato ancora "Approved"
(la ricerca "Approved" non li dà): il sito li mostra tra i recenti come "Approval ends".

Cosa si pubblica: nome del complesso, via, città, CAP, contea, ID HUD, unità, quota FHA, date. **Non si pubblicano** il testo libero
"Composition of Project" né i commenti HUD (a volte contengono sigle di funzionari o note interne): il testo libero non è salvato
nemmeno in `dati/` (resta solo nella cache, fuori da git). `verifica.py` controlla che nel sito non ci siano email, telefoni o quel testo.
Unità: ricavate dal testo libero con regole prudenti (`numero_unita` in `raccolta/estrai.py`): note per 5.531 su 6.539, le altre "–".

Fonti delle guide (lette il 17/10/2026, solo fatti scritti lì):
- 24 CFR 203.43b (regola FHA sui condomini): testo in Federal Register 84 FR 41846 del 15/8/2019 (govinfo.gov) e testo attuale
  dall'API eCFR (ultima modifica sostanziale 15/10/2019). Approvazione per 3 anni, rinnovo da 6 mesi prima a 6 mesi dopo, single-unit
  approval (condizioni e limiti 0-20 % / massimo 2 unità sotto i 10), concentrazione FHA 25-75 % fissata da HUD, site condominium, DELRAP.
- 38 U.S.C. 3710(a)(6) (govinfo.gov) e VA.gov "VA-backed purchase loan" ("Buy a condo in a VA-approved project"); 38 CFR 36.4360.
- Fannie Mae Selling Guide B4-2.1-01 (5/8/2026): il prestatore deve verificare che il progetto rispetti i requisiti di Fannie Mae.
- Non scritto perché non verificato: le percentuali esatte in vigore (es. 50 %, 10 %), che stanno nell'Handbook HUD 4000.1 (pagina non
  raggiungibile dal server); regole VA su durata e singola unità; regole Freddie Mac.

## File

| File | A cosa serve |
|---|---|
| `raccolta/scarica.py` | scarica le pagine del modulo HUD in `cache/<data>/` (ripresa automatica: le pagine già salvate non si riscaricano; `completo.json` alla fine) |
| `raccolta/estrai.py` | legge le pagine e scrive `dati/condomini.json` e `dati/conteggi.json`; **si ferma** se le righe lette non sono uguali al totale dichiarato da HUD |
| `raccolta/ricontrolla.py` | ricontrolla N condomini a caso sul modulo HUD, uno per uno (nome, ID, indirizzo, città, contea, CAP, unità, stato, date) |
| `genera.py` | genera `sito/` (circa 1 secondo), sitemap, robots, `netlify.toml`, `data/search.json` |
| `verifica.py` | tutti i controlli prima di pubblicare (vedi sotto); `--browser` lancia `verifica_browser.js` |
| `verifica_browser.js` | Playwright a 375 e 1280 px, chiaro e scuro: niente scorrimento orizzontale, niente errori, ricerca, filtro, tema; screenshot in `cache/screenshot/` (o nella cartella `SHOT_DIR`) |
| `dati/affiliati.json` | riquadro "Compare lenders": **nascosto** finché `mutuo.url` è vuoto. Mettere solo un URL di affiliazione vero |
| `grafica/` | font Lora e Libre Franklin (licenza OFL inclusa), `og.html` + `og.js` → `og.png` |
| `TEST.md` | esito del test della fonte |

Pubblicità: `<div class="ad-slot">` vuoto (invisibile) dopo la tabella principale di ogni pagina di luogo e in home.

## Aggiornamento settimanale (comandi esatti, dalla radice del repository)

```
python3 fhacondos/raccolta/scarica.py          # circa 9 minuti; cartella nuova cache/<data di oggi>/
python3 fhacondos/raccolta/estrai.py           # usa l'ultima edizione completa
python3 fhacondos/genera.py
python3 fhacondos/verifica.py --browser        # deve finire con "Tutti i controlli superati." (ricontrolla anche 20 condomini su HUD)
rm -rf fhacondos/cache/<data vecchia>          # facoltativo: le edizioni vecchie non servono più (circa 30 MB l'una)
```
Poi commit di `fhacondos/dati` e `fhacondos/sito`. Se `scarica.py` si interrompe (rete o HUD lento), basta rilanciarlo: riprende.
Se `estrai.py` si ferma per un conteggio diverso, HUD ha cambiato la pagina: non pubblicare, controllare `raccolta/estrai.py`.
Crediti Netlify: ogni pubblicazione costa 15 crediti sui 300 al mese condivisi da tutti i siti; una a settimana = 60 al mese.
Se i crediti stringono, pubblicare ogni due settimane (le date "as of" restano giuste, sono quelle dello scarico).

## Impostazioni Netlify (da fare da Massimiliano)

- Collegare il repository GitHub, ramo `ccr-b7fd6b9e-n096cr`.
- **Base directory: `fhacondos/sito`** · **Build command: vuoto** · **Publish directory: `.`**
- `fhacondos/sito/netlify.toml` (scritto da `genera.py`) ha già `publish = "."`, `command = ""`, la regola
  `ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."` (pubblica solo se cambia `fhacondos/sito`) e le intestazioni di sicurezza.
- Nome del sito: `fha-approved-condos-list` (se diverso, cambiare `URL_SITO` in `genera.py` e rigenerare).
- Search Console: la meta di verifica `btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI` è in ogni pagina; poi inviare `sitemap.xml`.
- Moduli: attivare le notifiche email del modulo "contact" (Netlify Forms).

## Controlli fatti il 17/10/2026 (`python3 fhacondos/verifica.py --browser`)

- 346 pagine HTML, tutte 200 dal server locale; link e ancore interni validi; sitemap = pagine con canonical; meta di verifica ovunque.
- Conteggi: 6.539 approvati nei dati = 6.539 dichiarati da HUD (e così per ogni Stato e tipo); in ogni pagina il numero del titolo =
  righe della tabella = conteggio dai dati; tutti gli 8.554 condomini sono in una tabella e nella ricerca, che porta alla riga giusta.
- 20 condomini a caso ricontrollati sul modulo HUD e confrontati con la riga pubblicata: 0 errori.
- Dati personali: nessuna email o telefono nel sito; il testo libero HUD non compare.
- Parole vietate: nessuna. Unica eccezione ammessa: una via vera di Anchorage, "6909 Gemini Dr" (indirizzo di un condominio HUD).
- Browser: 28 pagine × 375/1280 px × chiaro/scuro, nessuno scorrimento orizzontale, nessun errore; ricerca (CAP, città, nome), filtro e tema funzionano.
- Peso: **11,2 MB** su disco (359 file); pagina più pesante `virginia/` 261 KB (617 righe); `data/search.json` 644 KB, caricato solo
  quando si usa la ricerca. CSS, JS, icone e favicon sono file esterni con l'impronta nel nome.

## Punti da tenere d'occhio

1. Il modulo HUD è vecchio: se cambia nomi dei campi o tabella, `scarica.py` o `estrai.py` si fermano (nessun dato sbagliato pubblicato).
2. La scheda di dettaglio HUD (`f17condo-maint.cfm`) funziona solo dalle 8 alle 22 ora della costa est, nei giorni feriali: non la usiamo.
3. Il campo contea di HUD è lungo al massimo 24 caratteri ("MATANUSKA-SUSITNA BOROUG", corretto in BOROUGH); le contee del Connecticut
   sono senza "COUNTY" (aggiunto); i nomi dei condomini sono troncati a 30 caratteri da HUD ("...Homeowners Associat").
4. Elenco VA (`lgy.va.gov/lgyhub/condo-report`): è un'app JavaScript, non incluso. Possibile aggiunta futura.
5. Pagine per singolo condominio: non fatte (fase successiva, solo se le pagine di città vengono indicizzate).

## Revisione indipendente del 17/10/2026

- Fonte ricontrollata a parte (curl, sessione e Referer): 25 condomini in 25 Stati diversi, 0 differenze (nome, città, contea, CAP,
  Stato, stato, date); conteggi uguali a HUD per Colorado 367, Texas 64, Washington 431, Fairfax County VA 118, San Diego County CA 403,
  Cook County IL 160. Testo di 24 CFR 203.43b riletto dall'API eCFR; 38 U.S.C. 3710(a)(6), VA.gov e Fannie Mae B4-2.1-01 riletti.
- Nomi: numeri romani riconosciuti con una regola (XXI, IIB), sigle senza vocali in maiuscolo (NW, DC, TH, SM), "13A", "St. Mary's",
  "@" spaziato, "#11", ultima parola maiuscola ("Villages #7, The"); città: "McLean", "St. Louis" (stile AP; la ricerca accetta "saint").
- Città indipendenti: "City of Alexandria" (prima "Alexandria (city)"). Badge senza giorni contati (le pagine restano online una settimana).
- Guide: tolte le affermazioni non verificabili (motivo dei ritiri, Freddie Mac, definizione di "warrantable", 38 CFR 36.4360–36.4367),
  precisata la revoca (h)(3); link FR su govinfo.gov e 38 CFR 36.4360 con l'indirizzo eCFR corto.
- SEO: description ≤ 165 caratteri, titoli ≤ 67, conteggio nel titolo di contee e città. Design: m4 della mappa più scuro (contrasto AA),
  griglie a 2 colonne e passi più larghi sul telefono, segnaposto della ricerca più corto.

## IndexNow (26/10/2026)
- IndexNow: file chiave scritto dal generatore; invio con studio-business/strumenti/indexnow.py. Costante `CHIAVE_INDEXNOW` in `genera.py` accanto a `SCRIPT_CONTATORE` (chiave pubblica, uguale in tutti i siti della rete); `extra()` scrive `sito/<chiave>.txt` accanto a `robots.txt`, fuori dalla sitemap e non linkato. Nuovo controllo in `verifica.py` (`controlla_indexnow`): file presente, contenuto = chiave, non citato nella sitemap.

## Monetizzazione: come si attiva (30/10/2026)
- **Dove si scrive:** un solo file per tutta la rete, `studio-business/strumenti/monetizzazione.json` (`adsense_client`, `adsense_siti`, domini di affiliazione ammessi). In una riga: `python3 studio-business/strumenti/monetizzazione.py attiva ca-pub-XXXXXXXXXXXXXXXX fhacondos`, poi `python3 fhacondos/genera.py`. Il nome del sito nel file è `fhacondos` (`SITO_ID` in `genera.py`).
- **Cosa cambia con AdSense acceso:** script ufficiale nel `<head>` di ogni pagina (annunci automatici, nessun blocco manuale), `sito/ads.txt` con `google.com, pub-…, DIRECT, f08c47fec0942fa0`, sezione «Advertising (Google AdSense)» in `privacy.html`, sottotitolo e descrizione senza più «No cookies, no tracking», frase sulla California aggiornata; la frase sui cookie diventa «GoatCounter non usa cookie, la pubblicità sì». Prima di pubblicare: in AdSense accendere il messaggio di consenso certificato di Google (Privacy e messaggi, regolamenti europei: UE/SEE, Regno Unito, Svizzera), che la privacy descrive.
- **Link di affiliazione:** `dati/affiliati.json` (voce `mutuo`, campo `url`). Ammessi solo verso i domini di `domini_affiliazione`, con `rel="sponsored noopener"` e la riga di trasparenza (la aggiunge `riquadro_trasparenza()` se manca); con almeno un link la privacy aggiunge la sezione sui link di affiliazione.
- **Come si verifica:** `python3 fhacondos/verifica.py --senza-fonte`; controllo comune in `monetizzazione.py` (script e `ads.txt` solo con AdSense acceso, privacy coerente, nessun dominio fuori elenco o bloccato, Amazon.it solo con `tag=`).
- **Con il codice vuoto o il sito fuori elenco l'output non cambia:** il 30/10/2026 `sito/` è stato rigenerato identico byte per byte.
