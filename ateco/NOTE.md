# Codici ATECO 2025 – note di lavoro (12/11/2026)

Sito statico in italiano: una pagina per ogni sezione, divisione e classe della classificazione ATECO 2025 dell'Istat, con titolo ufficiale
(italiano, più inglese e tedesco), note esplicative («Comprende», «Comprende anche», «Non comprende», note operative), sottocategorie a
sei cifre come schede con ancora, vecchi codici ATECO 2022 dalla tavola di raccordo, coefficiente del regime forfetario dalla legge.
Più: ricerca nel browser (codici 2025, vecchi codici 2022, parole delle note), tabella «da ATECO 2022 a ATECO 2025», guida «cosa cambia»,
pagina dei coefficienti, tre pagine «codice ATECO per mestiere».
Nato dalla famiglia 1 di `studio-business/intelaiatura/fronti-2026-11-12-volumi-prima.md` (passo 1 dell'ordine di costruzione).
Indirizzo previsto `https://codici-ateco.netlify.app` (libero il 12/11/2026: risposta 404). Costante `URL_SITO` in `genera.py` e in
`verifica.py` (cambiarle insieme). **Il sito Netlify non esiste ancora**: i passi sono in fondo.

Nome: «Codici ATECO 2025» è descrittivo (è il nome della classificazione); nessun marchio trovato con questo nome il 12/11/2026. Ogni pagina
dice «Sito indipendente, non affiliato a Istat, all'Agenzia delle entrate o alle Camere di commercio». Concorrente con nome simile:
codiceateco.it (al singolare).

## Fonti (lette il 12/11/2026, impronte in `dati/fonti.json`)
| Fonte | Cosa | Uso |
|---|---|---|
| Istat, `StrutturaATECO-2025-IT-EN-DE.xlsx` | 3.257 codici: 22 sezioni, 87 divisioni, 287 gruppi, 651 classi, 920 categorie, 1.290 sottocategorie | albero, titoli IT/EN/DE |
| Istat, `Note-esplicative-ATECO-2025-italiano-inglese.xlsx` | 9.512 note in italiano | note di ogni codice (testo invariato) |
| Istat, tavola di raccordo bidirezionale ATECO 2025 – ATECO 2022, **aggiornamento 2026** (luglio 2026), italiano | 6.745 righe, 2.748 al sesto livello | vecchi codici e «contenuto in comune» |
| Istat, tabella operativa di riclassificazione ATECO 2022 → 2025, aggiornamento 2026 | 3.157 codici 2022 (1.241 a sei cifre) | codice rappresentativo Istat e Camere di commercio |
| Nota informativa congiunta Istat – sistema camerale – Agenzia delle entrate, 11/12/2024 (PDF) | date, riclassificazione d'ufficio, ComUnica, modelli AA9/12, AA7/10, AA5/6, ANR/3, visura transitoria | pagina «cosa cambia», FAQ |
| Agenzia delle entrate, risoluzione n. 24/E dell'8/4/2025 (PDF) | in vigore 1/1/2025, attiva dal 1/4/2025, nessun obbligo di variazione, Cassetto fiscale | idem |
| Normattiva: L. 190/2014 allegato 4 (testo vigente); D.Lgs. 81/2025 art. 1 (vigente al 1/1/2026); D.Lgs. 117/2026 (testo unico imposte sui redditi) art. 235, allegato D, art. 377 | 9 gruppi e coefficienti; regola «coefficiente secondo ATECO 2007 fino ai nuovi coefficienti»; TU in vigore dal 1/1/2027 con la stessa tabella | coefficienti |
| Agenzia delle entrate, istruzioni al modello Redditi Persone fisiche 2026, fascicolo 3, quadro LM (PDF, aggiornamento 13/5/2026) | rigo LM21 con il codice ATECO 2025; coefficiente «individuato sulla base del codice … secondo la classificazione ATECO 2007» | conferma dell'Agenzia della regola del forfettario (pagina coefficienti). **L'indirizzo cambia ogni anno**: se `fonti.py --rete` dà 404, cercare il fascicolo 3 dell'anno |
| Pagine Istat: «ATECO 2025 e aggiornamenti» (aggiornata il 15/7/2026), comunicato stampa, «Note legali» (licenza) | frasi controllate | date, licenza |

Date chiave verificate: ATECO 2025 in vigore dal **1° gennaio 2025**, adottata operativamente dal **1° aprile 2025** (pagina Istat, nota
congiunta, risoluzione 24/E). L'aggiornamento 2026 cambia solo le corrispondenze, non struttura e titoli (pagina Istat).
Il D.Lgs. 81/2025 art. 1 su Normattiva risulta abrogato dal D.Lgs. 117/2026, che però si applica dal 1/1/2027 (art. 377) e riprende la regola
all'art. 235 comma 6: il sito cita tutte e due le norme con le date.

**Licenza e attribuzione (CC BY 4.0, note legali Istat):** testo usato nel piè di pagina e in «Come lavoriamo»:
«Fonte dei codici, dei titoli e delle note: Istat, classificazione ATECO 2025 (struttura, note esplicative, tavola di raccordo e tabella
operativa, aggiornamento 2026), licenza CC BY 4.0. I testi Istat sono riportati senza modifiche; impaginazione, collegamenti, conteggi e
abbinamento ai coefficienti del forfettario sono nostri.» Unica modifica tecnica ai testi: «_x000D_» (a capo di Excel scritto come testo) → a capo.

## Pagine (771 file HTML: 447 indicizzabili, 324 noindex compresa la 404)
| Pagina | Contenuto |
|---|---|
| `/` | ricerca (indice JSON di 3.257 codici 2025, codici 2022 dalla classe in giù, guide), numeri, guide, 22 sezioni, come si legge un codice, 4 FAQ |
| `/sezione-a/` … (22) | note della sezione, divisioni |
| `/56/` … (87) | note della divisione, un capitolo per gruppo (`#g-56.1`) con note e classi, coefficienti presenti nella divisione |
| `/56-11/` … (651) | classe: note; per ogni categoria/sottocategoria una scheda `#c-56.11.11` con titolo IT/EN/DE, note, vecchi codici 2022 (tabella o «stesso contenuto»), riga del forfettario; vecchi codici riclassificati qui (tabella operativa); «attività che Istat rimanda a questa classe» (note di esclusione di altri codici); posizione nell'albero |
| `/da-ateco-2022-a-2025/` | 1.241 vecchi codici a sei cifre → codice rappresentativo (Istat e Camere) e tutte le corrispondenze; filtro, 100 righe alla volta, ancore `#v-96.02.01` |
| `/cosa-cambia-ateco-2025/` | date, cosa fare, forfettario, vecchi codici che si dividono di più, codici nuovi senza corrispondente (46.89.00), 4 FAQ |
| `/coefficienti-redditivita-forfettario/` | tabella di legge, regola ATECO 2007, coefficienti per divisione 2025, 3 FAQ |
| `/codice-ateco-parrucchiere/`, `/codice-ateco-ristorante/`, `/codice-ateco-e-commerce/` | codici, note Istat citate, vecchio codice, codici vicini, FAQ |
| `/come-lavoriamo/`, `/chi-siamo/`, `/privacy/`, `404.html` | metodo, impronte, licenza, modulo «segnala un errore» (Netlify Forms) |

**Perché le sottocategorie non hanno una pagina ciascuna (regola AdSense «scarso valore»):** 725 delle 1.290 sottocategorie hanno lo stesso
titolo della classe o categoria sopra; quasi tutte hanno 1-3 note. Una pagina per classe tiene insieme le sottocategorie (con ancora propria,
raggiungibile dalla ricerca e dalla tabella 2022). Quando la classe ha una sola sottocategoria, il titolo della pagina usa il codice a sei cifre
(«Codice ATECO 96.21.00: …»).
**Indicizzazione delle pagine di codice:** indicizzata solo con almeno 150 gruppi di 5 parole propri (che non compaiono in nessun'altra pagina di
codice) e meno del 55% del testo in comune con la pagina più simile (`MIN_PAROLE_PROPRIE`, `MAX_SOVRAPPOSIZIONE` in `genera.py`; misure per pagina in
`dati/indicizzazione.json`; `verifica.py` le ricalcola sulle pagine scritte con confronto completo). Oggi: classi 362 sì / 289 no, divisioni 64 / 23,
sezioni 11 / 11 (prima della revisione, con 120 e 60%: 430, 69, 15). Le noindex restano nel sito, fuori dalla sitemap e senza pubblicità. Esempio: la classe 96.21 (parrucchieri) è noindex (84 gruppi
propri), ma la pagina mestiere del parrucchiere è indicizzata.
**Forfettario:** per ogni sottocategoria 2025 si prendono i codici ATECO 2022 collegati al sesto livello e si guarda in quale dei 9 gruppi
dell'allegato 4 cadono (i codici della legge sono ATECO 2007; l'aggiornamento 2022 non cambia divisioni, gruppi e classi). Se cadono in gruppi
diversi la scheda mostra i coefficienti possibili con i vecchi codici. È un abbinamento nostro, dichiarato in pagina: la legge chiede il codice
ATECO 2007 della singola attività. 46.89.00 non ha corrispondenti: nessun coefficiente.

**Mestieri:** pagina solo se una frase ha un volume misurato (`dati/volumi.json`, misure del 12/11/2026 dal file dei fronti): parrucchiere 1.300,
ristorante 720 (+ ristorazione 590, «56.10.11» 590, pizzeria 390), e-commerce 480 (+ vendita online 390). **Il 12/11/2026 sera lo strumento dei
volumi rispondeva 429 (quota esaurita, con e senza chiave)**: gli altri mestieri (estetista, idraulico, elettricista, fotografo, b&b,
affittacamere, affitti brevi, consulente, bar, muratore, giardiniere, ncc, influencer, personal trainer, psicologo, agente di commercio,
avvocato, architetto, geometra, fisioterapista) hanno suggerimenti veri in `dati/domanda.json` ma nessun volume: elenco in `volumi.json`
(«da_misurare»). Per pubblicarne uno: misurare, scrivere il volume in `volumi.json`, aggiungere la voce in `dati/mestieri.json` (codici, vecchi,
vicini, intro) e le FAQ in `dati/faq.json`, poi genera e verifica.

## Controlli (`python3 ateco/verifica.py --browser`, 12/11/2026: 0 errori, 0 avvisi)
1. Fonti: impronte dei 7 file e 8 pagine = `fonti.json`, HTTP 200, 47 frasi ritrovate nei testi salvati (PDF con pdftotext).
2. Dati riletti dagli xlsx con un lettore proprio: 3.257 codici, titoli IT/EN/DE, padri e livelli, forma dei codici, nessun ramo senza
   sottocategorie; 9.512 note, 6.745 righe di raccordo, 3.157 righe della tabella operativa uguali a `ateco.json`; tabella dei coefficienti riletta
   dal testo di legge salvato e 2.776 codici 2022 riassegnati ai gruppi (0 differenze).
3. Contenuti: ogni codice nella pagina/ancora giusta con il titolo ufficiale; tutte le 9.512 note presenti nella pagina del loro codice;
   2.748 vecchi codici e 1.290 coefficienti delle schede uguali al ricalcolo; tabella 2022 → 2025 con le 1.241 righe e tutte le corrispondenze.
4. Pagine: titoli ≤ 65 e descrizioni ≤ 160 (70-160 per le indicizzate) unici, un h1, canonical = sitemap, noindex senza canonical e senza
   pubblicità, id unici, link interni e ancore, link esterni solo verso domini previsti, GoatCounter, robots, IndexNow, netlify.toml con `ignore`, og.png.
5. FAQ: 26 domande, ognuna da una ricerca salvata (1.211 suggerimenti, hl=it gl=it); JSON-LD = testo visibile; ogni «codice «titolo»» citato
   ha il titolo ufficiale (controllato anche da `genera.py`).
6. Indicizzazione: ricalcolata (massimo 55% in comune, almeno 154 gruppi propri tra le indicizzate).
7. Testi: nessun nome di modelli di IA, nessun dato personale (titolare solo in privacy), nessuna frase di consiglio; frase fissa «verifica con il
   commercialista o la Camera di commercio» e attribuzione CC BY in ogni pagina.
8. Monetizzazione: `python3 studio-business/strumenti/monetizzazione.py verifica ateco`.
9. Browser (Playwright, ogni richiesta esterna bloccata con `page.route`): home, classe 56.11, parrucchiere, tabella 2022 → 2025 a 375 e 1280 px,
   chiaro e scuro: niente scorrimento orizzontale, testi ≥ 11 px, sfondo coerente, ricerca («pizzeria», «96.21», «96.02.01», «programmazione
   informatica», nessun risultato), filtro della tabella (100 righe, «47.91.10» = 1 riga, «Mostra tutti»), tema, nessun errore JS.
   Screenshot in `cache/screenshot/` (fuori da git).

## Aggiornamento
**Ogni mese (15 minuti):**
```
python3 -I ateco/raccolta/fonti.py --rete     # riscarica file Istat, PDF e pagine di legge
git diff --stat ateco/dati/fonti.json         # impronta cambiata = file nuovo
python3 -I ateco/raccolta/estrai.py           # si ferma se cambiano le intestazioni o l'albero non torna
python3 ateco/genera.py
python3 ateco/verifica.py --browser
python3 studio-business/strumenti/monetizzazione.py verifica ateco
```
Istat ha annunciato aggiornamenti più frequenti dal 2026: rileggere la pagina `istat.it/classificazione/ateco-2025/` (data di aggiornamento nella
home del sito). Se Istat pubblica un file con un nome nuovo (es. «Aggiornamento-2027-…»), cambiare l'indirizzo in `raccolta/fonti.py`.
**Forfettario:** quando saranno approvati i nuovi coefficienti basati su ATECO 2025 (art. 235 c. 6 TU), la regola cambia: aggiungere la fonte in
`fonti.py`, sostituire l'abbinamento via raccordo in `estrai.py`/`genera.py` e i testi della pagina coefficienti e delle FAQ.
**Dal 1/1/2027** il testo unico (D.Lgs. 117/2026) si applica: le pagine lo dicono già; aggiornare la frase «dal 1° gennaio 2027» in un testo al presente.
**Ogni 3 mesi:** `python3 -I ateco/raccolta/domanda.py --tutto` (165 richieste, 0,5 s di pausa), poi genera e verifica (le FAQ la cui ricerca
sparisce fermano `genera.py`: riscriverle in `dati/faq.json`).

## Monetizzazione
AdSense acceso come gli altri siti: `ateco` in `SITI` di `studio-business/strumenti/monetizzazione.py` e in `adsense_siti` e `_siti_della_rete`
di `monetizzazione.json`; `ads.txt` scritto da `genera.py`; script solo nelle pagine indicizzate con almeno 400 parole (oggi 439 delle 447
indicizzabili, il resto ha il segno «niente pubblicità»). Riquadro affiliati per la partita IVA (Fiscozen, Qonto) **spento**: `dati/affiliati.json`
ha gli URL vuoti; compare su «cosa cambia», coefficienti e mestieri quando ci sono URL tracciati veri (aggiungere anche il dominio in
`monetizzazione.json`). Nessuna commissione letta.

## Da fare per pubblicare (passi di Massimiliano)
1. Netlify: «Add new site» → «Import an existing project» → GitHub, repository di questo progetto, **branch `ccr-b7fd6b9e-n096cr`**;
   Base directory `ateco/sito`, Build command vuoto, Publish directory `.` (il file `ateco/sito/netlify.toml` lo conferma);
   nome del sito `codici-ateco` (se diverso, cambiare `URL_SITO` in `ateco/genera.py` e `ateco/verifica.py` e rigenerare).
2. Netlify → Forms: lasciare acceso il rilevamento dei moduli (modulo `segnalazioni`) e impostare la notifica email.
3. Search Console: proprietà `https://codici-ateco.netlify.app/` (meta di verifica già nelle pagine), inviare `sitemap.xml`.
4. Dopo la pubblicazione: aggiungere l'host a `SITI` in `studio-business/strumenti/indexnow.py` (cartella `ateco`) e lanciare l'invio.

**Regola di arresto (file dei fronti):** se a 60 giorni dalla pubblicazione le pagine ATECO hanno meno di 3.000 impressioni al mese in Search
Console, non si costruiscono NAICS/SIC nello stesso motore.

## Dubbi per il revisore indipendente
- Abbinamento sottocategoria 2025 → coefficiente tramite i codici 2022 del raccordo: è un passaggio nostro (dichiarato). Va bene mostrare un solo
  coefficiente quando tutti i vecchi codici cadono nello stesso gruppo?
- La «nota operativa» e le note di provenienza italiana/europea sono mostrate senza distinzione di provenienza.
- Pagine di classe noindex (221) anche per codici cercati (es. 96.21): soglia 120 scelta per prudenza AdSense; da rivedere dopo l'approvazione.
- Titoli di sezione mostrati con l'iniziale maiuscola (Istat li scrive in maiuscolo).
- Tre sole pagine mestiere per mancanza di volumi misurati (quota dello strumento esaurita il 12/11/2026).
- La tabella operativa porta il vecchio 47.91.10 al codice di gruppo 47.1: la pagina e-commerce lo spiega come codice per riclassificazioni massive.

## Revisione indipendente (12/11/2026)
Rifatti da zero, con file riscaricati e un lettore diverso (openpyxl): tutte le 651 pagine di classe (2.861 titoli IT/EN/DE, 8.657 note parola per
parola, 1.953 antenati, 2.748 vecchi codici con il «contenuto in comune», 1.290 coefficienti ricalcolati dalla tabella di legge): 0 differenze nei
dati. Date 1/1/2025 e 1/4/2025 rilette in nota congiunta, risoluzione 24/E e pagina Istat. Cambiato:
- **Riga del forfettario** di ogni sottocategoria: ora dice sempre che è una derivazione nostra, da quali vecchi codici (tutti elencati, senza «e altri»)
  e «per la legge conta il codice ATECO 2007 della tua attività, verifica con il commercialista». Nel riquadro in alto «forfettario, dai vecchi codici».
- **Fonte dell'Agenzia delle entrate** per la regola ATECO 2007 (istruzioni Redditi PF 2026, quadro LM) aggiunta a `fonti.py` e alla pagina coefficienti.
- **FAQ** del coefficiente di parrucchiere ed e-commerce: «se il codice ATECO 2007 dell'attività è …» e «per il tuo caso verifica con il commercialista».
- **Soglia di indicizzazione** da 120/60% a 150/55% (lente AdSense «scarso valore»: le 90 pagine tra 120 e 160 gruppi propri avevano 380 parole di
  mediana). Da rivedere dopo l'approvazione AdSense: riportare a 120/60% rende indicizzabili circa 80 pagine in più.
- Titoli inglese e tedesco anche per le categorie a 5 cifre; «1 codice ATECO 2022 collegato» al singolare; classi con due gruppi di legge alla stessa
  percentuale mostrano la percentuale e non «dipende»; rimandi alle fonti ad almeno 11 px.
**Risposte ai dubbi:** un solo coefficiente quando tutti i vecchi codici sono nello stesso gruppo va bene, se la riga dice da dove viene (ora lo dice).
Classi molto cercate ma noindex perché le note Istat sono corte (96.21 parrucchieri, 86.21 medici, 86.23 dentisti, 86.93 psicologi, 86.95
fisioterapisti, 74.30 traduttori): non gonfiarle; la strada è la pagina mestiere (come per il parrucchiere), appena ci sono i volumi misurati.
Note senza distinzione di provenienza, sezioni con l'iniziale maiuscola e spiegazione del 47.91.10 → 47.1: vanno bene così.
