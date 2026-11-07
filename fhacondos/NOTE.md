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
| `dati/affiliati.json` | riquadro "Compare lenders": **nascosto** finché `mutuo.url` è vuoto. Mettere solo un URL di affiliazione vero. Riquadro `kit_solari` (Amazon US, solo ricerche): **acceso dal 7/11/2026**, solo nelle 17 pagine `/balcony-solar/` |
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
- **Link di affiliazione:** `dati/affiliati.json` (voce `mutuo`, campo `url`; voce `kit_solari` per la sezione /balcony-solar/, vedi sotto). Ammessi solo verso i domini di `domini_affiliazione`, con `rel="sponsored noopener"` e la riga di trasparenza (la aggiunge `riquadro_trasparenza()` se manca); con almeno un link la privacy aggiunge la sezione sui link di affiliazione.
- **Come si verifica:** `python3 fhacondos/verifica.py --senza-fonte`; controllo comune in `monetizzazione.py` (script e `ads.txt` solo con AdSense acceso, privacy coerente, nessun dominio fuori elenco o bloccato, Amazon.it solo con `tag=`).
- **Con il codice vuoto o il sito fuori elenco l'output non cambia:** il 30/10/2026 `sito/` è stato rigenerato identico byte per byte.

## AdSense acceso (30/10/2026)
- **AdSense acceso il 30/10/2026** (codice editore `ca-pub-3750093987658434`, già usato da EsameB1, Visa Income e Before You Fly): `python3 studio-business/strumenti/monetizzazione.py attiva ca-pub-3750093987658434 fhacondos`, poi `python3 fhacondos/genera.py`. Script ufficiale nel `<head>` di ogni pagina, `sito/ads.txt` (`google.com, pub-3750093987658434, DIRECT, f08c47fec0942fa0`), privacy `/privacy.html` con la sezione «Advertising (Google AdSense)», sottotitolo e descrizione senza «No cookies, no tracking», frase sulla California aggiornata.
- **Controlli del 30/10/2026:** `python3 fhacondos/verifica.py --senza-fonte --browser` → «Tutti i controlli superati»; `monetizzazione.py verifica fhacondos` → AdSense acceso, 0 errori; Playwright a 375 px su home (script AdSense caricato davvero): nessun errore JS, nessuno scorrimento orizzontale. Da fare in AdSense: aggiungere il sito (Siti → Aggiungi) e controllare che il messaggio di consenso UE copra anche questo dominio. Nessun commit, nessuna pubblicazione.
- **`verifica_browser.js` e AdSense (30/10/2026):** con lo script AdSense nelle pagine Playwright segnalava come «richiesta fallita» i beacon di Google interrotti al cambio pagina (`pagead2.googlesyndication.com/pagead/ping`). Ora le richieste ai server degli annunci (costante `PUBBLICITA`: googlesyndication.com, doubleclick.net, googleadservices.com, adtrafficquality.google, fundingchoicesmessages.google.com) ricevono una risposta vuota e non contano come errori: la prova non dipende da annunci esterni. Lo script e il suo indirizzo li controlla `monetizzazione.py`.
- Home: la riga «Free, no sign-up, no tracking» della testata diventa «Free, no sign-up» con AdSense acceso (gli annunci di Google usano cookie e identificatori, con il consenso): `genera.py`, funzione della home, condizione `MON.adsense_attivo(SITO_ID)`.

## Sezione "Balcony solar in condos" (`/balcony-solar/`, 6/11/2026, da revisionare)

Dallo studio `studio-business/intelaiatura/fronti-2026-11-06-nascenti.md` (pannello solare da balcone, voto 6): stesso pubblico di chi
compra o vive in un condominio, domanda vera ("is balcony solar legal in" 10 suggerimenti negli USA, con california, texas, pennsylvania,
ny, massachusetts, nj, washington state, nc, florida, illinois). **17 pagine**: indice + 16 Stati. **Regno Unito escluso**: il sito parla
a chi compra un condominio negli USA (HUD/FHA), una pagina britannica non c'entra con questo pubblico.

| Stato | Legge | Stato della legge (verificato il 6/11/2026) | Fonte ufficiale |
|---|---|---|---|
| Utah | H.B. 340 | in vigore dal 7/5/2025 (firmata 25/3/2025), 1.200 W | le.utah.gov (testo, dati di stato, Utah Code) |
| Colorado | HB26-1007 | in vigore dal 12/8/2026 (firmata 7/5/2026), 1.920 W; HOA: divieti irragionevoli nulli dal 1/1/2027 | leg.colorado.gov |
| Maine | LD 1730 | Public Law 644, firmata 6/4/2026, in vigore 29/7/2026 (data generale; il tracker di terzi dice 15/7: sbagliato) | legislature.maine.gov |
| Maryland | HB 1532 | Chapter 353, firmata 12/5/2026, in vigore 1/7/2026, PU § 7-321 | mgaleg.maryland.gov |
| Vermont | S.202 | Act 149, firmata 16/6/2026, in vigore 1/7/2026; covenant non possono vietarli | legislature.vermont.gov |
| Virginia | HB 395 (+ SB 250) | Code § 56-596.8, in vigore dal 1/1/2027 | law.lis.virginia.gov (la pagina del disegno di legge su lis.virginia.gov richiede JavaScript) |
| California | SB 868 | firmata il 30/9/2026 (comunicato del governatore) | **testo non letto**: leginfo 403 |
| New Jersey | S2368 | testo del 28/6/2026 letto; firma (1/9/2026) solo dal tracker di terzi | pub.njleg.gov; la pagina di stato richiede JavaScript |
| Connecticut | HB 5340 (PA 26-127) | solo tracker di terzi | **non letto**: cga.ct.gov, errore di certificato |
| New Hampshire | SB 540 | solo tracker di terzi | **non letto**: gc.nh.gov chiude la connessione |
| New York | A9111C / S8512C | approvata dalle due Camere il 28/5/2026, nessuna azione del governatore | nyassembly.gov (nysenate.gov 403) |
| Massachusetts | H.5175 | in commissione di conciliazione dal 16/7/2026 | malegislature.gov |
| Pennsylvania | HB 1971 | in commissione Energia dal 28/10/2025 | palegis.us |
| Michigan | HB 5764 | in commissione Energia dal 19/3/2026 | legislature.mi.gov |
| North Carolina | HB 1129 | in commissione Rules dal 30/4/2026 | ncleg.gov |
| Washington | SB 6050 | ferma nel 2026 (Rules "X" file il 26/2/2026) | app.leg.wa.gov |

Altri Stati (Illinois, Ohio, DC e altri 16 con proposte; 16 senza proposte, tra cui Texas e Florida) solo nell'indice, con lo stato del
tracker di terzi dichiarato come tale. Ohio e Illinois: siti ufficiali con errore di certificato, non letti.

- **Dati:** `dati/balcony_solar.json` (fonti con codice HTTP o motivo, affermazioni con fonti, FAQ con la ricerca da cui vengono,
  autocompletamento salvato, sintesi per la tabella). Il generatore (`genera.py`, blocco "pannello solare da balcone") non inventa testo:
  numera le fonti [n] per pagina, mette "Not read" e "Third party" dove serve, JSON-LD Article + FAQPage con lo stesso testo.
- **Pagine:** risposta nella prima frase con la data della verifica; riquadro sintesi; legge; limiti; condomini/HOA; riquadro fisso
  "Before you buy" (rimandi a legge, compagnia elettrica e regolamento del condominio, nessun consiglio legale o elettrico); FAQ; link alla
  pagina FHA dello Stato; altri Stati; fonti. Titoli ≤ 70 caratteri con l'anno ("Is Balcony Solar Legal in X? 2026 Plug-In Solar Law").
- **Collegamenti:** indice ↔ pagine Stato; pagina Stato ↔ pagina FHA dello stesso Stato (paragrafo dopo le guide); piè di pagina
  "Balcony solar laws by state" in tutte le pagine; sitemap automatica.
- **Monetizzazione: Amazon US acceso il 7/11/2026** (riquadro `kit_solari` di `dati/affiliati.json`). Il 6/11/2026 Massimiliano ha
  aggiunto `https://fha-approved-condos-list.netlify.app` ai siti del suo account Amazon Associates US (tag `beforeyoufl08-20`, lo
  stesso di Before You Fly; schema ripreso da `beforeyoufly/genera.py`: `amazon_link`, `AMAZON_FRASE`, `box_bagagli`).
  - **Solo link di RICERCA** `https://www.amazon.com/s?k=<ricerca>&tag=beforeyoufl08-20`, mai ASIN né pagine prodotto (`amazon_link`,
    `ricerche_kit`, `blocco_kit` in `genera.py`). 2 ricerche per pagina: `plug in balcony solar kit` e `portable power station`. Il
    limite di watt entra nella prima ricerca solo dove una legge che abbiamo letto lo fissa (stato `in_vigore` o `firmata`:
    `watt_legge`): Utah, Maryland, Maine, Vermont, Virginia `1200W`, Colorado `1920W`. Nessun watt per New Jersey (firma non
    confermata), California (testo non letto) e Stati con un disegno di legge.
  - **Dove:** indice `/balcony-solar/` (dopo "How we check") e 16 pagine Stato (dopo il riquadro "Before you buy", prima delle FAQ). Mai
    nelle pagine dei condomini FHA (Stati, contee, città, guide).
  - **Testo:** nessuna promessa di legalità o conformità del prodotto ("a kit being on sale does not mean you may use it at home"):
    prima di comprare, legge dello Stato (fonti della pagina), compagnia elettrica (avviso o modulo) e regolamento del condominio/HOA.
    Revisione del 7/11: negli Stati senza legge in vigore o firmata (o non letta) il riquadro dice che la legge non c'è ancora o non
    l'abbiamo letta e rimanda allo stato del disegno di legge; nelle pagine Stato rimanda ai Limits per l'elettricista abilitato sotto
    soglie più basse (Maine: oltre 420 W).
    Etichetta "Affiliate", `rel="sponsored noopener"`, riga di trasparenza e frase di Amazon «As an Amazon Associate we earn from
    qualifying purchases.» nel riquadro; sezione «Amazon Associates» con la stessa frase in `privacy.html`.
  - **Interruttore:** `kit_solari.url` (= ricerca generica). Vuoto = riquadro spento ovunque e privacy senza la sezione Amazon.
  - **Scadenza Amazon:** l'account US è condiviso con Before You Fly: le 3 vendite entro 180 giorni contano per l'account intero.
  - **EcoFlow (Awin):** iscrizione chiesta il 6/11; se approvata, decidere se affiancarlo ad Amazon e adattare `controlla_amazon`.
- **Controlli (`verifica.py`, `controlla_balcony_solar`):** ogni affermazione con fonte esistente; fonti con HTTP 200 o motivo scritto
  (**43 fonti: 37 lette, 6 con motivo scritto**), e con la rete le fonti registrate con HTTP 200 rispondono ancora 200 (39 su 39 il 6/11); terzi marcati; FAQ dalle ricerche salvate; JSON-LD = testo;
  titoli; prima frase con la data; rimandi verso fonti elencate; sitemap; link interni nei due sensi; nessun link di affiliazione
  salvo il riquadro Amazon. **`controlla_amazon` (punto 11, 7/11/2026):** in tutto il sito ogni link Amazon è `https://www.amazon.com/s`
  con solo `k` e `tag=beforeyoufl08-20` (scritto in `verifica.py`), nessun ASIN, `rel="sponsored noopener"`, frase di Amazon nella
  pagina e nella privacy; un riquadro per pagina e solo nelle 17 pagine /balcony-solar/; ricerche esattamente quelle attese (watt di
  legge scritti a mano in `WATT_LEGGE_ATTESI`); testo con compagnia elettrica e condominio, senza "legal", "compliant", "approved";
  `url` = ricerca generica. Controllo comune `monetizzazione.py verifica fhacondos`: 34 link in 17 pagine, 0 errori (7/11/2026).
  `verifica_browser.js` prova anche indice, Colorado, New Jersey e Connecticut a 375 e 1280 px.
- **Da ricontrollare:** ogni mese da gennaio a giugno 2027 (sessioni legislative) e subito: firma del governatore di New York,
  conciliazione del Massachusetts, testo di SB 868 (California) quando leginfo risponde, siti di Connecticut, New Hampshire, Ohio,
  Illinois. Cambiare `verificato_il` solo dopo aver riletto le fonti.
- **Revisione indipendente del 6/11/2026: pubblicabile con correzioni, applicate** (Virginia senza abbinamento capitolo/disegno di legge,
  titoli "Plug-In Solar Bill" per gli Stati senza legge: NY, MA, PA, MI, NC, WA; New Jersey "would allow" nella FAQ e nel JSON-LD).
  - **Connecticut:** il revisore legge la pagina di stato di HB 5340 su cga.ct.gov con 200 ("Public Act No. 26-127", "An Act Concerning
    Renewable Power Generation"). Da questo ambiente la stessa pagina dà ancora errore di certificato (curl e Python, 6/11 sera): non
    l'abbiamo letta, quindi la fonte `ct-cga` resta "Not read" e la pagina CT non cita numero e titolo del PA come letti. Al prossimo
    giro rileggerla e, se si apre, segnarla letta (http 200, senza motivo) con numero e titolo; limiti e data 1/10/2026 restano "dal
    tracker" finché non si apre il PDF dell'atto.
  - **Colorado:** "in force since August 12, 2026" viene dalla pagina del bill e dalla legge di sessione lette il 6/11 (200); il revisore
    riceve 406 da leg.colorado.gov con curl. Riconfermare la data sulla pagina del bill al prossimo controllo.
