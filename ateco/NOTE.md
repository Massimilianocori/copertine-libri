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

## Pagine «Codice ATECO per …» (13/11/2026 sera, NON pubblicato: revisione indipendente, poi pubblicazione)
Modello: le pagine «NAICS code for …» di `naics/` (stesse regole: righe ufficiali citate parola per parola, FAQ solo da ricerche misurate, misura del
testo proprio). **Misura.** 244 ricerche `api.seodata.dev` (country=it) il 13/11: 144 attività × «codice ateco X», 80 forme «X codice ateco» (quasi
tutte 404: lo strumento le conta con la forma principale) e 20 frasi alternative (autotrasportatore, locazione turistica, sartoria…), in
`dati/volumi-attivita-2026-11-13.json` (volume, cpc, data del dato, frasi simili con volume; null = 404). 685 frasi con volume tra cercate e simili.
Volume di una pagina = la frase più cercata tra le sue (comprese le frasi «simili» e i vecchi codici a cui la pagina risponde, es. «codice ateco 70.22 09»
1.000 nella pagina del consulente), mai la somma. Soglia `MIN_VOLUME_ATTIVITA = 100`; tetto ~40 → attività vicine riunite.
**Pagine (41 + indice `/codice-ateco-per/`; le 3 pagine mestiere del 12/11 restano agli stessi indirizzi e sono nell'indice):** bar 1.900, avvocato
1.300, amministratore di condominio e condominio 1.300 («codice ateco condominio»; la frase dell'amministratore è 320), affittacamere e B&B 1.000,
architetto 1.000, consulente 1.000, commercialista e consulente del lavoro 880, estetista 720, geometra 720, fisioterapista e osteopata 720, edilizia e
muratore 720, agente di commercio e procacciatore 720, psicologo 720, personal trainer e palestra 590, ingegnere 590, medico 590, farmacia 590, elettricista
590, social media manager 480, infermiere 480, tabaccheria 480 (**noindex**: 42% in comune con la classe 47.26), hotel 480, affitti brevi e casa vacanze 390,
influencer e content creator 390, agriturismo 390, fotografo e videomaker 390, agente immobiliare 390, organizzazione eventi e wedding planner 390, dentista
320, tatuatore 320, giardiniere 320, meccanico/carrozziere/gommista 320, idraulico 260, imbianchino 260, holding 260, falegname 260, panificio/pasticceria/
gelateria 260, massaggiatore e operatore olistico 260, impresa di pulizie 210, NCC e taxi 210, autotrasporto 170. Misurate ≥ 100 ma senza pagina (tetto):
macelleria, lavanderia, autolavaggio (FAQ nel meccanico), veterinario, logopedista, giornalista, artista, musicista, agenzia viaggi, guida turistica, grafico,
copywriter, insegnante/formatore, asilo nido, ottico, toelettatura, consulente finanziario, consulente informatico/sviluppatore, noleggio auto (FAQ in NCC),
alimentari, negozio di abbigliamento, sartoria, edicola, ferramenta, artigiano (nessun codice: è una qualifica), azienda agricola 480 (sezione A troppo
ampia per una tabella di scelte). 404 (non nel database): food truck, ambulante, programmatore, dj, babysitter. Dropshipping 140: nessuna pagina propria, la pagina e-commerce del 12/11 non è stata toccata (possibile FAQ).
**Contenuto (`dati/attivita.json`, `pagina_attivita` in genera.py).** Introduzione nostra con i titoli e i numeri solo da segnaposto (`{ct:56.30.01}`,
`{t22:56.30.00}`, `{d22:…}` destinazioni del raccordo, `{v:…}` vecchi codici, `{perc:…}` coefficienti), tabella «Quale codice» (righe delle note Istat o
titolo ufficiale citati in `<q class="ni" data-c>`, scelte con l'inizio della nota o le note di inclusione del codice), «La regola di Istat» (note centrali
o operative, es. la regola della durata della divisione 55 e la nota sulla cucina della classe 56.30), «Cosa Istat mette in un altro codice» (note «Non
comprende» dei codici e, per i due principali, della loro classe e categoria; massimo 10), coefficiente del forfettario per ogni sottocategoria (stessa riga
delle pagine di codice: «Derivazione nostra…», con le fonti), «Dai vecchi codici ATECO 2022 ai codici 2025» (solo le righe verso i codici della guida, le
altre come «altri N codici» con link alla tabella 2022 → 2025), FAQ, guide vicine, fonti. Dove le note non usano la parola cercata la pagina lo dice
(agriturismo, onicotecnica, parafarmacia, youtuber, olistico, locazione turistica, multiservizi, personal trainer invece è citato).
**FAQ:** 82 nuove in `faq.json` con `"misura": "volumi-attivita-2026-11-13.json"`: la `ricerca` deve avere un volume misurato (genera si ferma). Molte
rispondono alle ricerche dei vecchi codici (70.22.09, 74.90.99, 73.11.02, 55.20.51, 43.21.01, 46.19.02, 45.20.10…) con la tavola di raccordo.
**Link:** menu «Per attività», piè di pagina, home (8 guide più cercate), ricerca (voci «Guida»), breadcrumb, e nelle pagine di classe un blocco
`<section data-ripreso>` «Guide per attività che indicano questo codice» (massimo 3 link; escluso dalla misura del testo e dal conteggio delle parole per la
pubblicità: le pagine di codice restano 437 indicizzate su 760, invariate).
**Indicizzazione:** pagina attività indicizzata con ≥ 150 gruppi di 5 parole propri (le righe Istat citate spezzano il testo, le frasi presenti in ≥ 25%
delle pagine attività non contano) e < 40% in comune con la pagina più simile, di codice o di attività (`MAX_SOVRAPPOSIZIONE_ATTIVITA`). Oggi 40 su 41
(minimo 156 gruppi propri, massimo 39% in comune); tabaccheria noindex, fuori sitemap, senza pubblicità. Per ridurre le somiglianze: massaggiatore e
fisioterapista non condividono più i codici in evidenza; esclusioni di classe solo per i due codici principali.
**Controlli** (`verifica.py --browser`, 13/11 sera: 0 errori, 0 avvisi; `monetizzazione.py verifica ateco`: 0 errori): nuova sezione 6b — pubblicazione
solo con volume ≥ 100 dal file con data; 599 righe citate ritrovate parola per parola nelle note o nei titoli del file Istat riletto con openpyxl; ogni
codice esiste; 128 coefficienti ricalcolati dalla legge; ogni riga del raccordo esiste e il conteggio «altri N codici» torna; indice completo; testo proprio
ricalcolato. FAQ attività solo da ricerche misurate; nessun file contiene una chiave dello strumento dei volumi. Prova di manomissione fatta (riga
citata cambiata, coefficiente cambiato: due errori trovati). Playwright anche su `/codice-ateco-per/` e `/codice-ateco-bar/` (375/1280, chiaro/scuro).
**Dubbi per il revisore:** pagina «amministratore di condominio e condominio» (il volume 1.300 è di «codice ateco condominio», risposta con 97.00.10);
tabelle «Quale codice» con righe brevi (es. «bar», «caffetterie») che sono voci S di una nota «attività di:»; intro di agente di commercio e tabaccheria
con frasi di sintesi nostre da rileggere contro le note; la soglia del 40% lascia noindex la tabaccheria (480 ricerche).

## Revisione indipendente delle pagine «Codice ATECO per …» (13/11/2026, notte; NON pubblicato, non committato)
Rifatto da zero con file riscaricati da istat.it (struttura, note, raccordo e tabella operativa: impronte uguali a `fonti.json`), letti con un
programma proprio (openpyxl), e con l'allegato 4 della L. 190/2014 riletto su Normattiva (versione vigente) e il D.Lgs. 81/2025 art. 1 (testo
originale; abrogato dal D.Lgs. 117/2026 art. 376 solo «dalla data di cui all'articolo 377», cioè dal 1/1/2027: la citazione va bene).
- **Righe citate:** 596 su 596 ritrovate parola per parola come nota intera o riga di nota del codice indicato in `data-c`; nella tabella «Quale
  codice» solo note centrali, di inclusione o titoli; in «Cosa Istat mette in un altro codice» solo note di esclusione. 0 differenze.
- **Coefficienti:** 129 su 129 ricalcolati dalla tabella di legge (gruppo per divisione/gruppo/classe ATECO 2007) sui vecchi codici del raccordo,
  con l'elenco dei vecchi codici mostrati: 0 differenze. Etichetta «Derivazione nostra … verifica con il commercialista» presente ovunque.
- **Intro e FAQ lette contro le note (16 pagine: bar, avvocato, condominio, affittacamere/B&B, affitti brevi, consulente, commercialista, psicologo,
  medico, social media manager, influencer, fotografo, agente di commercio, tabaccheria, holding, NCC/taxi; più imbianchino, giardiniere,
  elettricista, panificio, autotrasporto, eventi, hotel).** Corretti:
  - social media manager: la nota di 73.11.01 cita la «pianificazione di campagne di social media marketing» (e l'esclusione di 73.11.03 la rimanda lì)
    e 73.11.02 cita la «consulenza di marketing»; la pagina metteva 73.11.02 per primo e la FAQ mandava la consulenza di marketing a 70.20.09.
    Ora 73.11.01 e 73.11.02 con le righe giuste, FAQ corretta, titolo e descrizione nuovi;
  - influencer: 73.11.03 non era «la pubblicità basata sulla propria influenza»: le note citano agenzie e influencer marketer che conducono
    campagne, e rimandano la pubblicazione di contenuti di influencer a 59.11.00 (video) e 58.19.00 (non video). Intro, FAQ youtuber e titolo corretti;
  - medico: gli ambulatori specialistici sono in 86.22.03, non in 86.22.02 (intro e FAQ);
  - psicologo: 86.90.30 non era tra le «attività paramediche» (86.90.2) ma in 86.90.3;
  - agente di commercio: la frase «la nota del gruppo 46.1 lo dice in modo esplicito» legava la nota alla fusione di 46.19.01/02; ora la pagina dice
    che le parole «agente di commercio» e «procacciatore» non sono nelle note 2025, cita la nota del gruppo e l'esclusione degli agenti che
    assumono la proprietà dei beni; FAQ del forfettario con il gruppo di legge 46.1 (62%);
  - tabaccheria: l'intro rimandava a «note di esclusione più sotto» che la pagina non ha (47.26 non ne ha); ora cita la nota operativa di 47.26.0 e
    dice che «tabaccheria» è solo nel titolo del vecchio 47.26.00; descrizione senza «Tabaccherie: 47.26.01». Resta noindex (40,2% in comune con 47.26);
  - holding: aggiunto che la tabella operativa dà al vecchio 70.10.00 (holding operative) il codice rappresentativo 82.10.00 (la FAQ risponde alla
    ricerca «codice ateco 701000»); fonte «tabella operativa» nell'intro (`fonti_intro` in `attivita.json`);
  - parola cercata assente dalle note, ora detto: avvocato (solo «ordini degli avvocati»), imbianchino, elettricista, videomaker, agente di commercio,
    tabaccheria; NCC: «classe 49.32», non «gruppo»; imbianchino: aggiunto 43.34.02 che la descrizione prometteva, frase sgrammaticata corretta;
    giardiniere: la tabella mostrava come «attività» righe di elenco come «abitazioni private e pubbliche», ora righe di attività; panificio: «serve i clienti».
- **genera.py:** riga del forfettario con una voce per percentuale (prima «40% … ; 40% …» quando due gruppi di legge hanno la stessa percentuale).
- **Misure:** 41 pagine, 40 indicizzate (tabaccheria no), testo in comune massimo 39,1%, gruppi propri minimo 156; FAQ 82, tutte da ricerche con
  volume nel file del 13/11, JSON-LD = testo visibile; titoli ≤ 65 e unici, descrizioni ≤ 160 e uniche, canonical = sitemap. Doppioni: affitti brevi /
  affittacamere 30% in comune ma intenti diversi (regola dell'anno e property management contro B&B/affittacamere): restano separate.
- **Controlli:** `genera.py`, `verifica.py --browser` 0 errori 0 avvisi, `monetizzazione.py verifica ateco` 0 errori, Playwright proprio su 4 pagine a
  375/1280 chiaro/scuro con richieste non-file bloccate (nessuno scorrimento orizzontale, nessun errore JS), nessuna chiave dello strumento nei file.
