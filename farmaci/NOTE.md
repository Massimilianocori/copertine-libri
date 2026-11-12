# Farmaco Equivalente – note di lavoro (12/11/2026)

Sito statico in italiano: per ogni principio attivo della lista di trasparenza AIFA, i gruppi di equivalenza con prezzo al
pubblico, prezzo di riferimento, differenza a carico e stato di carenza di ogni confezione; elenco dei farmaci carenti
filtrabile; guida «farmaco che non si trova» con le indicazioni AIFA.
Nato dall'approfondimento 1 del radar del 12/11/2026 (`studio-business/intelaiatura/fronti-2026-11-12-radar-settori-diversi.md`)
dopo il via libera di Massimiliano sul tema farmaci (paragrafo in testa a `studio-business/REGOLE-FISSE.md`).
Indirizzo di lavoro `https://farmaco-equivalente.netlify.app` (costante `URL_SITO` in `genera.py` e in `verifica.py`, da cambiare
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
| `/carenze/` | elenco AIFA completo (2.552 righe) con filtro, «solo con equivalente», ordinamento per colonna (desktop), 100 righe alla volta, link al gruppo, legenda, 3 FAQ |
| `/farmaco-mancante/` | guida: carenza o indisponibilità, cosa prevede AIFA nei due casi, conteggi per indicazione, principi attivi con più carenti, 3 FAQ |
| `/<principio-attivo>/` (373) | un blocco per gruppo di equivalenza: riferimento, tabella delle confezioni (prezzo, differenza, carenza), nota con gli equivalenti non carenti, dettaglio AIFA di ogni carenza, altre confezioni carenti con lo stesso ATC, FAQ dalle ricerche vere |
| `/come-lavoriamo/`, `/chi-siamo/`, `/privacy/`, `404.html` | metodo, impronte dei file, licenza, cosa non facciamo, modulo «segnala un errore» (Netlify Forms) |

**Indicizzazione (regola del revisore, 12/11/2026).** Una pagina principio attivo è indicizzata solo se: (1) in `dati/domanda.json` c'è almeno
un suggerimento vero con il nome (principio attivo o prima parola di un nome commerciale «di fantasia») e una parola d'interesse (generico,
equivalente, prezzo, costo, carenza, non si trova, mutuabile…); (2) ha almeno 8 confezioni nella lista (`MIN_CONFEZIONI`); (3) meno del 60% del
suo testo (gruppi di 5 parole) è in comune con la pagina principio attivo più simile (`MAX_SOVRAPPOSIZIONE`, misurata da `genera.py` sulle pagine
vere e ricalcolata da `verifica.py`). Le altre sono `noindex`, fuori dalla sitemap e senza pubblicità; il perché di ogni pagina è in
`dati/indicizzazione.json`.
Numeri del 12/11/2026: **228 pagine indicizzate** (222 principi attivi + home, carenze, guida, come lavoriamo, chi siamo, privacy) e
**151 principi attivi noindex** (39 senza ricerche, 95 con meno di 8 confezioni, 17 con 60% o più di testo in comune).
Perché non 334 e non 90: con 334 (ogni pagina con una ricerca) 97 pagine avevano il 60% o più del testo uguale a un'altra pagina e 34 il 70% o più
(fino all'81%: sono le pagine con 2-5 confezioni, quasi solo testo fisso). Con l'interruttore `INDICIZZA_CON_SOLO_PREZZO = False` (90 pagine) il
problema restava: 22 sopra il 60% e 5 sopra il 70%, perché il tipo di ricerca non dice quanti dati propri ha la pagina. Con la regola nuova:
0 pagine sopra il 60% (massimo 59%, mediana 46%), minimo 8 confezioni (mediana 24), almeno 230 gruppi di 5 parole che non compaiono in nessun'altra pagina.
Dopo l'approvazione AdSense la soglia si può allargare (per esempio a 6 confezioni) guardando Search Console.
FAQ: 870 in tutto (858 nelle pagine dei principi attivi). Una pagina per principio attivo (non per gruppo)
per non creare centinaia di pagine quasi uguali: il gruppo è un'ancora (`#g-<codice>`), ogni confezione ha `#aic-<codice>`.

**Note AIFA nei gruppi (revisore, 12/11/2026).** 1.150 confezioni (190 gruppi interi) hanno la nota «In distribuzione diretta da parte delle Regioni»:
il gruppo lo dice in un riquadro e la tabella della home «differenze più alte» le esclude (prima erano tutte e dieci farmaci in distribuzione diretta,
con differenze fino a 4.356,75 € che il paziente non paga al banco). 32 gruppi hanno altre note AIFA (antiepilettici, levotiroxina, ciclosporina,
nifedipina «non sostituibile con…», metotrexato): riquadro «Nota AIFA su questo gruppo» e, se c'è una carenza, nessun invito alla sostituzione.
**Elenco dei carenti.** La pagina pesa 1,6 MB (148 KB compressa) e resta una sola, perché filtro e ordinamento lavorano su tutto l'elenco; il browser
mostra 100 righe alla volta («Mostra altre 100», «Mostra tutte»): al telefono la pagina è alta 37.000 px invece di circa 900.000. Senza JavaScript si vedono tutte.

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
3. Search Console: proprietà `https://farmaco-equivalente.netlify.app/` (meta di verifica già nelle pagine), inviare `sitemap.xml`.
4. Dopo la pubblicazione: aggiungere l'host a `SITI` in `studio-business/strumenti/indexnow.py` (cartella `farmaci`) e lanciare l'invio.

## Revisione indipendente (12/11/2026)
Cifre ricalcolate dai CSV riscaricati da AIFA (stesse impronte di `fonti.json`) con un lettore scritto a parte: tutte le 8.576 righe di confezione
delle 373 pagine (prezzo, riferimento, differenza, gruppo, stato e date di carenza, motivo, fine presunta, indicazione AIFA), i conteggi di ogni gruppo
e di ogni pagina, le 2.552 righe dell'elenco carenti, i numeri e le due tabelle della home, i conteggi della guida, le 281 righe «stesso ATC»:
circa 61.500 controlli, 0 differenze. Art. 7 riletto su Normattiva (commi 1-4 uguali alle citazioni).
Correzioni: regola di indicizzazione (sopra); note AIFA e distribuzione diretta nei gruppi; tabella «differenze più alte» senza distribuzione diretta;
frase sulla sostituzione riscritta secondo l'art. 7, commi 2 e 3 (il farmacista propone dopo aver informato, il medico può scrivere «non sostituibile»);
tolto «quanto paghi in più con la marca»; «salvo diversa decisione di AIFA» nelle FAQ; «1 carente»/«1 gruppo» nelle descrizioni; elenco carenti a blocchi di 100.
Privacy: uguale alla convenzione della rete (stessa frase di EsameB1 e Paga CCNL), nessuna modifica.
Dubbi che restano: (a) il nome commerciale nel titolo (es. «Glucobay ed equivalenti…») è informazione con dati ufficiali, non pubblicità, ma se AdSense
o un titolare AIC protestano si toglie dal titolo con una riga in `titolo_pa`; (b) la differenza è quella nazionale stampata da AIFA: ticket e regole
regionali non sono calcolati (scritto in home e in «come lavoriamo»); (c) l'elenco dei carenti cambia due volte alla settimana: senza l'aggiornamento
settimanale le pagine invecchiano in fretta (`verifica.py` avvisa dopo 10 giorni).

## Dubbi del costruttore (risolti dal revisore, vedi sopra)
1. Indicizzazione larga: 244 delle 334 pagine indicizzate lo sono solo per ricerche «<nome> prezzo/costo». È domanda vera e la
   pagina risponde con il prezzo ufficiale, ma va pesato contro la lezione AdSense (pagine simili): con l'interruttore
   `INDICIZZA_CON_SOLO_PREZZO = False` si scende a 90 pagine principio attivo indicizzate.
2. «Nome di fantasia» = la prima parola del nome commerciale non è il principio attivo (`nomi.py`): regola sul nome, usata solo per le ricerche,
   i titoli e le FAQ, mai per dire chi è l'originatore.
3. «Altre confezioni carenti con lo stesso codice ATC»: l'abbinamento è per codice ATC, non per nome.
4. Differenza a carico: è quella stampata da AIFA; le Regioni applicano la lista con direttive proprie (art. 7, c. 1) e il ticket non è calcolato.
5. Nella pagina privacy il titolare è nominato come negli altri siti della rete (convenzione già revisionata).
