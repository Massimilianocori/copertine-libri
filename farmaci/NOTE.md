# Farmaco Equivalente – note di lavoro (12/11/2026)

Sito statico in italiano: per ogni principio attivo della lista di trasparenza AIFA, i gruppi di equivalenza con prezzo al
pubblico, prezzo di riferimento, differenza a carico e stato di carenza di ogni confezione; elenco dei farmaci carenti
filtrabile; guida «farmaco che non si trova» con le indicazioni AIFA.
Nato dall'approfondimento 1 del radar del 12/11/2026 (`studio-business/intelaiatura/fronti-2026-11-12-radar-settori-diversi.md`)
dopo il via libera di Massimiliano sul tema farmaci (paragrafo in testa a `studio-business/REGOLE-FISSE.md`).
Indirizzo di lavoro `https://farmaci-equivalenti.netlify.app` (costante `URL_SITO` in `genera.py` e in `verifica.py`, da cambiare
insieme). **Il sito Netlify non esiste ancora**: i passi sono in fondo.

Nome: «Farmaco Equivalente» è un termine descrittivo (la confezione degli equivalenti porta la scritta «Medicinale Equivalente»):
ricerca del 12/11/2026 senza marchi registrati con questo nome; esiste però equivalente.it, campagna informativa di un'azienda
di farmaci equivalenti. Il sito dice in ogni pagina «Sito indipendente, non affiliato ad AIFA». Se si cambia nome: `NOME`,
il logo in `pagina()` e `grafica/og.html` (poi `python3 farmaci/grafica/og.py`).

## Regole del sito (vincoli del 12/11/2026)
- Solo dati ufficiali AIFA, con la data della lista accanto a ogni cifra e il rimando numerato alla fonte.
- Nessun consiglio medico né diagnosi. Frase fissa in ogni pagina: «chiedi al medico o al farmacista» (controllata).
- Nessuna pubblicità di farmaci con ricetta: niente link di affiliazione (controllato: 0), nessun testo promozionale.
  AdSense solo nelle pagine indicizzate con almeno 400 parole; Google può limitare gli annunci nel tema salute: va bene.
- «Prezzi al pubblico da lista AIFA del <data>; in farmacia possono variare per i farmaci di fascia C» in ogni pagina con prezzi.

## Fonti (licenza CC BY 4.0, dichiarata nella pagina «Open Data» di AIFA)
| File | Pubblicato da AIFA | Righe | Uso |
|---|---|---|---|
| Lista di trasparenza, CSV (`/documents/20142/825643/Lista_farmaci_equivalenti.csv`) | 15/10/2026 | 8.576 confezioni, 1.018 gruppi, 377 principi attivi (373 pagine: 4 scritti con maiuscole diverse) | prezzi, riferimento, differenza, gruppi |
| Elenco completo dei farmaci carenti, CSV (`/documents/20142/847339/elenco_medicinali_carenti.csv`) | 10/11/2026 (anche nel file: «aggiornato al 10/11/2026») | 2.552 righe, 2.549 AIC | stato di carenza, date, motivo, indicazioni |
| Carenti con equivalenti, ODS | 10/11/2026 | 1.532 | elenco in cui compare la confezione |
| Carenti con trattamento alternativo, ODS | 10/11/2026 | 283 | idem |
| Fascia A per principio attivo, CSV | 30/06/2026 | 10.766 | solo controllo incrociato (8.419 confezioni della lista ci sono, 8.353 con lo stesso prezzo) |

Pagine lette (frasi controllate a ogni aggiornamento, `dati/fonti.json`): Open Data (licenza), Liste di trasparenza (art. 7,
data del CSV), Farmaci carenti (definizione, date dei file), Classi A e H (data), Farmaci equivalenti (definizione, sostituibilità
nel gruppo), Cosa fare quando un farmaco è mancante (carenza/indisponibilità, tre grossisti, 48 ore, importazione), e il testo
vigente dell'art. 7 del DL 347/2001 (conv. L. 405/2001) su Normattiva, citato alla lettera in home (commi 1 e 4).
robots.txt di aifa.gov.it permette i percorsi usati. Nota: il radar contava 2.585 righe carenti e 1.019 gruppi; i file del
10/11 e del 15/10 riletti oggi ne hanno 2.552 e 1.018. L'incrocio torna: 1.190 confezioni carenti sono nella lista, 1.170 con
almeno un equivalente non carente nello stesso gruppo.

## Pagine (380 file HTML)
| Pagina | Contenuto |
|---|---|
| `/` | ricerca nel browser (indice JSON di principi attivi, 3.695 nomi commerciali, farmaci carenti fuori lista), come funzionano equivalenti e prezzo di riferimento con l'art. 7 citato, carenti con equivalente non carente, 10 differenze più alte, indice A-Z, 6 FAQ |
| `/carenze/` | elenco AIFA completo (2.552 righe) con filtro, «solo con equivalente», ordinamento per colonna (desktop), link al gruppo, legenda, 3 FAQ |
| `/farmaco-mancante/` | guida: carenza o indisponibilità, cosa prevede AIFA nei due casi, conteggi per indicazione, principi attivi con più carenti, 3 FAQ |
| `/<principio-attivo>/` (373) | un blocco per gruppo di equivalenza: riferimento, tabella delle confezioni (prezzo, differenza, carenza), nota con gli equivalenti non carenti, dettaglio AIFA di ogni carenza, altre confezioni carenti con lo stesso ATC, FAQ dalle ricerche vere |
| `/come-lavoriamo/`, `/chi-siamo/`, `/privacy/`, `404.html` | metodo, impronte dei file, licenza, cosa non facciamo, modulo «segnala un errore» (Netlify Forms) |

**Indicizzazione.** Una pagina principio attivo è indicizzata solo se in `dati/domanda.json` c'è almeno un suggerimento vero con il
nome (principio attivo o prima parola di un nome commerciale «di fantasia») e una parola d'interesse (generico, equivalente,
prezzo, costo, carenza, non si trova, mutuabile…). Le altre sono `noindex`, fuori dalla sitemap e senza pubblicità.
Il 12/11/2026 (1.837 richieste, 1.795 nomi letti): **340 pagine indicizzate** (334 principi attivi + home, carenze, guida,
come lavoriamo, chi siamo, privacy) e **39 principi attivi noindex**. Delle 334: 81 con ricerche su equivalente/generico,
9 su carenza/non si trova, 244 solo su prezzo/costo/mutuabile. Interruttore `INDICIZZA_CON_SOLO_PREZZO` in `genera.py`:
con `False` restano indicizzate solo le 90 pagine «equivalente/carenza». 22 dei 39 principi attivi noindex hanno confezioni
carenti: restano raggiungibili dalla ricerca e dall'elenco dei carenti. FAQ: 870 in tutto (858 nelle pagine dei principi attivi). Una pagina per principio attivo (non per gruppo)
per non creare centinaia di pagine quasi uguali: il gruppo è un'ancora (`#g-<codice>`), ogni confezione ha `#aic-<codice>`.
Quota di testo in comune con la pagina più simile (gruppi di 5 parole, 40 pagine a caso): mediana 54%, da 26% a 78%.

## Controlli (`python3 farmaci/verifica.py --browser`, 12/11/2026)
1. Fonti: impronta SHA-256 di ogni file = `fonti.json`; HTTP 200; data di pubblicazione presente; 22 frasi ritrovate nelle pagine AIFA e Normattiva salvate.
2. Dati ricalcolati dai CSV grezzi con un lettore proprio (non usa `estrai.py`): su tutte le 8.576 righe differenza = prezzo − riferimento,
   un solo riferimento per gruppo, data del file carenti = data della pagina; i JSON del sito coincidono.
3. Pagine: ogni confezione compare una volta sola; attributi e testo visibile (prezzo, differenza o «nessuna», nome) uguali al CSV;
   stato di carenza = presenza dell'AIC nell'elenco, con «Carente dal gg/mm/aaaa» o «Carenza prevista dal…»; riferimento di ogni gruppo,
   conteggio «senza differenza» e numero di equivalenti non carenti; 2.552 righe dell'elenco carenti con date ed «equivalente»; numeri della home.
4. SEO: titoli ≤ 65, descrizioni 70-160 uniche, un h1, canonical, sitemap = canonical, noindex senza canonical e senza AdSense, link interni e ancore,
   link esterni solo verso domini previsti, nessun `rel="sponsored"`, GoatCounter in ogni pagina, robots, IndexNow, netlify.toml con `ignore`, og.png.
5. FAQ: ogni domanda viene da una ricerca salvata (`dati/faq.json` per le pagine generali, `dati/faq_pagine.json` scritto da `genera.py` per le altre); JSON-LD = testo visibile.
6. Testi: frase fissa e «non affiliato ad AIFA» e licenza in ogni pagina; nessun nome di modello di IA; nessun dato personale (titolare solo in privacy);
   nessuna frase che sembri un consiglio medico.
7. Monetizzazione: `python3 studio-business/strumenti/monetizzazione.py verifica farmaci` (AdSense acceso, ads.txt, privacy, 0 link di affiliazione).
8. Browser (Playwright, ogni richiesta esterna bloccata con `page.route`): home, carenze, amoxicillina + acido clavulanico, guida, a 375 e 1280 px
   chiaro e scuro: niente scorrimento orizzontale, testi ≥ 11 px, sfondo coerente col tema, ricerca «augmentin» → pagina giusta, filtro «quetiapina»,
   «solo con equivalente» = numero di righe con «Sì», ordinamento per inizio, pulsante del tema, nessun errore JS. Screenshot in `cache/screenshot/` (fuori da git).

## Aggiornamento (script + controlli)
AIFA pubblica la lista di trasparenza **ogni mese** e aggiorna l'elenco dei carenti **almeno due volte alla settimana**.
**Ogni settimana (carenti) e dopo il 15 di ogni mese (trasparenza), 10 minuti:**
```
python3 -I farmaci/raccolta/fonti.py --rete      # riscarica tutto; le date vengono dalle pagine AIFA
python3 -I farmaci/raccolta/estrai.py            # si ferma se un'intestazione di colonna cambia
python3 farmaci/genera.py
python3 farmaci/verifica.py --browser
python3 studio-business/strumenti/monetizzazione.py verifica farmaci
```
`git diff --stat farmaci/dati/fonti.json` mostra quali file sono cambiati. Se il nome del CSV della lista di trasparenza cambia
(oggi l'indirizzo è fisso), aggiornarlo in `raccolta/fonti.py`. Il file della fascia A ha la data nel nome: quando AIFA pubblica
quello nuovo, aggiornare l'indirizzo (serve solo al controllo incrociato). `verifica.py` avvisa se l'elenco carenti ha più di 10 giorni
o la lista più di 40. Si pubblica solo se i dati sono cambiati (regola `ignore` di Netlify: un push senza cambi in `farmaci/sito` non consuma crediti).
**Ogni 3 mesi:** `python3 -I farmaci/raccolta/domanda.py --tutto` (≈ 1.800 richieste, 0,5 s di pausa; si ferma alla prima risposta
diversa da 200 e riprende da dove era rimasto), poi genera e verifica: le pagine indicizzate e le FAQ seguono le ricerche nuove.

## Monetizzazione
`farmaci` aggiunto a `SITI` in `studio-business/strumenti/monetizzazione.py` e ad `adsense_siti` e `_siti_della_rete` in
`monetizzazione.json`; `ads.txt` scritto da `genera.py`. Nessuna affiliazione: le farmacie online vendono solo farmaci senza ricetta,
che non sono nella lista di trasparenza.

## Da fare per pubblicare (passi di Massimiliano)
1. Netlify: «Add new site» → «Import an existing project» → GitHub, repository di questo progetto, **branch `ccr-b7fd6b9e-n096cr`**;
   Base directory `farmaci/sito`, Build command vuoto, Publish directory `.` (il file `farmaci/sito/netlify.toml` lo conferma);
   nome del sito `farmaci-equivalenti` (se diverso, cambiare `URL_SITO` in `farmaci/genera.py` e `farmaci/verifica.py` e rigenerare).
2. Netlify → Forms: lasciare acceso il rilevamento dei moduli (modulo `segnalazioni`) e impostare la notifica email.
3. Search Console: proprietà `https://farmaci-equivalenti.netlify.app/` (meta di verifica già nelle pagine), inviare `sitemap.xml`.
4. Dopo la pubblicazione: aggiungere l'host a `SITI` in `studio-business/strumenti/indexnow.py` (cartella `farmaci`) e lanciare l'invio.

## Dubbi per il revisore indipendente
1. Indicizzazione larga: 244 delle 334 pagine indicizzate lo sono solo per ricerche «<nome> prezzo/costo». È domanda vera e la
   pagina risponde con il prezzo ufficiale, ma va pesato contro la lezione AdSense (pagine simili): con l'interruttore
   `INDICIZZA_CON_SOLO_PREZZO = False` si scende a 90 pagine principio attivo indicizzate.
2. «Nome di fantasia» = la prima parola del nome commerciale non è il principio attivo (`nomi.py`): regola sul nome, usata solo per le ricerche,
   i titoli e le FAQ, mai per dire chi è l'originatore.
3. «Altre confezioni carenti con lo stesso codice ATC»: l'abbinamento è per codice ATC, non per nome.
4. Differenza a carico: è quella stampata da AIFA; le Regioni applicano la lista con direttive proprie (art. 7, c. 1) e il ticket non è calcolato.
5. Nella pagina privacy il titolare è nominato come negli altri siti della rete (convenzione già revisionata).
