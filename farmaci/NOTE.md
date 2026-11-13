# Farmaco Equivalente – note di lavoro (12-13/11/2026)

Sito statico in italiano: per ogni principio attivo della lista di trasparenza AIFA, i gruppi di equivalenza con prezzo al
pubblico, prezzo di riferimento, differenza a carico e stato di carenza di ogni confezione; elenco dei farmaci carenti
filtrabile; guida «farmaco che non si trova» con le indicazioni AIFA.
Nato dall'approfondimento 1 del radar del 12/11/2026 (`studio-business/intelaiatura/fronti-2026-11-12-radar-settori-diversi.md`)
dopo il via libera di Massimiliano sul tema farmaci (paragrafo in testa a `studio-business/REGOLE-FISSE.md`).
**Online dal 13/11/2026 su `https://farmaco-equivalente.netlify.app`** (sito Netlify creato il 13/11; costante `URL_SITO` in `genera.py`
e in `verifica.py`, da cambiare insieme se cambia l'indirizzo). Pubblicazione: ogni push di `farmaci/sito` sul branch collegato; host già in
`studio-business/strumenti/indexnow.py`. Restano da controllare Search Console (sitemap) e la notifica email dei moduli (passi in fondo).

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
**Ogni 3 mesi:** volumi con `python3 -I farmaci/raccolta/volumi.py <elenco.txt> --max N` (una frase per riga, budget a parte; scrive
`dati/volumi-<data>.json`, `genera.py` usa il più recente) e `python3 -I farmaci/raccolta/domanda.py --tutto` (≈ 1.800 richieste, 0,5 s di pausa; si ferma alla prima risposta
diversa da 200 e riprende da dove era rimasto), poi genera e verifica: le pagine indicizzate e le FAQ seguono le ricerche nuove.

## Monetizzazione
`farmaci` aggiunto a `SITI` in `studio-business/strumenti/monetizzazione.py` e ad `adsense_siti` e `_siti_della_rete` in
`monetizzazione.json`; `ads.txt` scritto da `genera.py`. Nessuna affiliazione: le farmacie online vendono solo farmaci senza ricetta,
che non sono nella lista di trasparenza.

## Pubblicazione (fatta il 13/11/2026; restano i punti 2-3)
1. ~~Netlify~~ fatto: sito `farmaco-equivalente` (Base directory `farmaci/sito`, Build command vuoto, Publish directory `.`, `farmaci/sito/netlify.toml`).
   Se cambia l'indirizzo: `URL_SITO` in `farmaci/genera.py` e `farmaci/verifica.py`, poi rigenerare.
2. Netlify → Forms: lasciare acceso il rilevamento dei moduli (modulo `segnalazioni`) e impostare la notifica email.
3. Search Console: proprietà `https://farmaco-equivalente.netlify.app/` (meta di verifica già nelle pagine), inviare `sitemap.xml`.
4. ~~IndexNow~~ fatto: host in `SITI` di `studio-business/strumenti/indexnow.py`; lanciare l'invio dopo ogni pubblicazione con pagine nuove.

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

## Domanda misurata, titoli e FAQ (13/11/2026)
**Misura.** 391 richieste a `api.seodata.dev` (country=it; conteggio prudente: 363 frasi salvate + 5 prove a mano + fino a 25 risposte perse
in un'interruzione di rete, poi lo script salva dopo ogni risposta) con `raccolta/volumi.py` (la chiave si legge dal file locale e non va mai
scritta). Risultati in `dati/volumi-2026-11-13.json`: 116 frasi con volume, 246 non nel database dello strumento (404: quasi tutte le forme
«<marchio> generico» dei marchi poco noti), 1.168 frasi con volume contando le «simili» restituite dallo strumento. Volume di una pagina = la frase
più cercata attribuita a lei (mai la somma), contando solo nomi commerciali che nella lista hanno quel solo principio attivo («triatec» vale per
ramipril e ramipril + idroclorotiazide: non decide nulla). Le frasi su usi, effetti, dosi, «senza ricetta», «originale», «migliore» non contano.

**Cosa cercano le persone (volumi mensili).** Le forme più cercate non sono «<marca> generico» ma **«<principio attivo> nome commerciale»**
e **«<marca> principio attivo»**: zoloft principio attivo 4.400, keppra 4.400, xarelto 3.600, lyrica 3.600, tegretol/monuril/lasix/lopresor/tripliam/
pradaxa 2.900; olanzapina, fluoxetina, amlodipina, duloxetina, rivaroxaban nome commerciale 2.900; sertralina, carbamazepina, citalopram,
levofloxacina, gabapentin 2.400. «Generico»: generico cialis 6.600, cialis generico 5.400, augmentin generico 1.600, monuril generico 880,
tadalafil 5mg generico 720, amoxicillina generico 720. Teste: lista di trasparenza aifa 1.300 (e varianti), farmaci carenti aifa 1.000,
aifa farmaci carenti 880, farmaci equivalenti 590, carenti aifa 590, carenze aifa 590, farmaci mancanti / farmaci mancanti nelle farmacie /
carenza farmaci / farmaci generici / cerca farmaco equivalente 480. «<principio> carenza» quasi sempre 0 o 404 (quetiapina carenza 0); fanno
eccezione «auradol non si trova» 390 e «vasexten 10 mg non si trova» 320. «Differenza <marca> e generico», «lista farmaci equivalenti»,
«lista farmaci generici», «farmaci equivalenti aifa»: 404. Non usate perché fuori dai dati AIFA: sertralina 40.500, quetiapina 40.500,
gabapentin 33.100, «monuril a cosa serve» 12.100 (domande mediche); **aifa farmaci mutuabili 2.400** (è l'elenco di fascia A, che abbiamo
solo per il controllo incrociato: idea per una pagina futura, da far vedere al revisore).

**Cosa fa `genera.py` con i volumi** (`MISURE`, `VOLUME_PA`, `MIN_VOLUME = 100`):
- titolo, h1 e descrizione delle pagine principio attivo dalla frase più cercata (tipi: nome commerciale, principio attivo, generico, prezzo,
  carenza), con le cifre della pagina; titolo ≤ 65 e descrizione 70-160 uniche, altrimenti restano quelle di prima. «X: principio attivo Y»
  solo se il nome commerciale X nella lista compare con il solo principio attivo Y. L'h1 usa la seconda idea più cercata.
- indicizzazione: la prova di domanda è l'autocompletamento **oppure** almeno 100 ricerche al mese misurate; minimo 8 confezioni e testo in comune
  sotto il 60% restano uguali.
- FAQ nuove solo da frasi misurate: «Quali sono i nomi commerciali di X?» (elenco dei nomi della lista AIFA) e «Qual è il principio attivo di Y?»
  (principio attivo, ATC, confezioni e gruppi dalla lista); le FAQ «equivalente/generico», «quanto costa», «carenza» usano la frase misurata
  quando c'è. Massimo 7 FAQ per pagina. Nessuna risposta su usi, effetti o dosi.
- carenze: titolo e h1 «Farmaci carenti AIFA: elenco aggiornato al …», riquadro «Il tuo farmaco è nell'elenco?» con «chiedi al medico o al
  farmacista», tabella «Stato per principio attivo» (20 principi attivi con più righe: righe, carenze previste, «con equivalente» secondo AIFA),
  2 FAQ nuove (farmaci carenti aifa 1.000, elenco farmaci carenti aifa 260). Home e guida: titoli dalle frasi misurate, 1 FAQ nuova ciascuna
  (cerca farmaco equivalente 480, farmaci mancanti nelle farmacie 480).

| | Prima (12/11) | Dopo (13/11) |
|---|---|---|
| Pagine indicizzabili (sitemap) | 228 | **250** |
| Principi attivi indicizzati / noindex | 222 / 151 | **244 / 129** |
| Pagine con titolo, h1 e descrizione dalla frase misurata | 0 | 111 principi attivi + home, carenze, guida (110 dopo la revisione: tadalafil ha il titolo neutro) |
| FAQ nelle pagine (di cui da frasi misurate) | 870 (0) | 1.137 (277) |
| Testo in comune massimo tra pagine indicizzate | 59% | 59% |
| Home | Farmaco equivalente: prezzi, differenza e carenze AIFA | Farmaci equivalenti: lista di trasparenza AIFA e carenze |
| Carenze | Farmaci carenti: elenco AIFA del 10/11/2026 | Farmaci carenti AIFA: elenco aggiornato al 10/11/2026 |
| Guida | Farmaco che non si trova in farmacia: cosa dice AIFA | Farmaci mancanti in farmacia: cosa dice AIFA |
| tadalafil (generico cialis 6.600) | Cialis ed equivalenti: prezzi, differenza e carenze | ~~Cialis generico (tadalafil)…~~ → **Tadalafil: equivalenti di Cialis nella lista AIFA** (revisore, sotto) |
| sertralina (zoloft principio attivo 4.400) | Zoloft ed equivalenti: prezzi, differenza e carenze | Zoloft: principio attivo sertralina, generici e prezzi AIFA |
| levetiracetam (keppra principio attivo 4.400) | Epitiram ed equivalenti: prezzi, differenza e carenze | Keppra: principio attivo levetiracetam, generici e prezzi AIFA |
| pregabalin (lyrica principio attivo 3.600) | Ecubalin ed equivalenti: prezzi, differenza e carenze | Lyrica: principio attivo pregabalin, generici e prezzi AIFA |
| olanzapina (nome commerciale 2.900) | Zyprexa ed equivalenti: prezzi, differenza e carenze | Olanzapina: nomi commerciali, generici e prezzi AIFA |
| fluoxetina (nome commerciale 2.900) | Fluoxetina: equivalenti, prezzi e carenze (noindex) | Fluoxetina: nomi commerciali, generici e prezzi AIFA (indicizzata) |
| fosfomicina (monuril principio attivo 2.900) | Monuril ed equivalenti: prezzi, differenza e carenze | Monuril: principio attivo fosfomicina, generici e prezzi AIFA |
| amoxicillina + ac. clavulanico (augmentin generico 1.600) | Augmentin ed equivalenti: prezzi, differenza e carenze | Augmentin generico: equivalenti, prezzi e carenze |

**Passate a indicizzate (22, nessuna tolta):** amlodipina-valsartan, atenololo-clortalidone, carbamazepina, cefpodoxima, fluoxetina, levocetirizina,
lurasidone, nifedipina, paliperidone, perampanel, repaglinide, risperidone, ropinirolo, telmisartan, terbinafina, ticlopidina, torasemide, valaciclovir,
valsartan, venlafaxina, verapamil, zolmitriptan. 15 avevano solo la domanda misurata (≥ 100); 7 (levocetirizina, lurasidone, terbinafina, ticlopidina,
torasemide, valaciclovir, zolmitriptan) avevano già l'autocompletamento ed erano sopra il 60% di testo in comune: con l'elenco dei nomi commerciali
(dato AIFA proprio della pagina) sono scese sotto. **Con domanda ≥ 100 ma ancora noindex** (regole del revisore rispettate): amiodarone (1.300; 65%
in comune), naprossene (1.900; 63%), barnidipina (1.300; 6 confezioni), clopidogrel + acido acetilsalicilico (1.000; 62%), ebastina (390; 62%),
manidipina (480; 60,0%), vildagliptin (320; 66%), acido acetilsalicilico (170; 61%), vareniclina (170; 7 confezioni), dorzolamide (110; 7 confezioni).

**Indicizzate senza domanda misurata (144, da guardare in Search Console, NON tolte):** una sola richiesta per pagina, quasi sempre «<marca> generico»
finita in 404, quindi «nessun dato» più che «zero ricerche». L'elenco è in `dati/indicizzazione.json` (`indicizzata` vero e `volume_misurato` 0):
acarbosio, aceclofenac, acido-alendronico, acido-alendronico-colecalciferolo, acido-folico, acido-micofenolico, acido-ursodesossicolico, alfuzosina,
almotriptan, ambrisentan, amisulpride, anastrozolo, apremilast, azitromicina, beclometasone, beclometasone-formoterolo, betametasone, bicalutamide,
bimatoprost-timololo, bosentan, brimonidina, budesonide-formoterolo, buprenorfina, bupropione, calcio-carbonato-colecalciferolo,
calcipotriolo-betametasone, calcitriolo, candesartan-cilexetil-idroclorotiazide, capecitabina, carvedilolo, cefaclor, cefixima, ceftazidima,
ceftriaxone, cefuroxima, celecoxib, cinacalcet, claritromicina, deferasirox, desmopressina, dienogest, diltiazem, dimetilfumarato, donepezil, doxazosin,
dutasteride, eletriptan, enalapril-idroclorotiazide, enalapril-lercanidipina, entecavir, eplerenone, exemestane, ezetimibe, ezetimibe-simvastatina,
famciclovir, felodipina, fentanil, fexofenadina, fingolimod, flecainide, flunisolide, fluticasone, formoterolo, gliclazide, glimepiride, granisetrone,
imatinib, indapamide, irbesartan, irbesartan-idroclorotiazide, isosorbide-mononitrato, isotretinoina, itraconazolo, ivabradina, ketorolac, lacidipina,
lamotrigina, latanoprost, latanoprost-timololo, lercanidipina, letrozolo, levodopa-carbidopa-entacapone, levotiroxina, lisinopril,
lisinopril-idroclorotiazide, losartan, losartan-idroclorotiazide, lovastatina, magaldrato, memantina, metilprednisolone, micofenolato-mofetile,
midazolam, nebivololo-idroclorotiazide, nimesulide, nitroglicerina, octreotide, olmesartan-medoximil-amlodipina-idroclorotiazide,
omega-polienoici-esteri-etilici-di-acidi-grassi-polinsaturi, ondansetrone, ossicodone-oxicodone-cloridrato-naloxone-cloridrato-diidrato,
paracetamolo-codeina-fosfato, paroxetina, perindopril, perindopril-indapamide, pioglitazone, piperacillina-tazobactam, piroxicam, posaconazolo,
pravastatina, propafenone, rabeprazolo, ramipril-amlodipina, ramipril-amlodipina-idroclorotiazide, ramipril-bisoprololo, ramipril-idroclorotiazide,
rasagilina, rivastigmina, rosuvastatina-acido-acetilsalicilico, rotigotina, sevelamer, sildenafil, sitagliptin-metformina, sodio-ibandronato,
sodio-risedronato, solifenacina, sumatriptan, tacrolimus, tamoxifene, tapentadolo, teicoplanina, telmisartan-idroclorotiazide, temozolomide, terazosina,
teriflunomide, ticagrelor, timololo, topiramato, tramadolo-cloridrato, travoprost, valsartan-idroclorotiazide, vinorelbina, voriconazolo, zonisamide.
Prossima misura (con un nuovo budget): «<principio attivo> nome commerciale» per queste 144, che è la forma che rende di più.

**Controlli nuovi in `verifica.py`:** ogni FAQ nasce da un suggerimento salvato **o** da una frase misurata con volume (e il volume dichiarato è
quello del file); le FAQ su nomi commerciali e principio attivo devono avere una frase misurata; risposte «nomi commerciali» (confezioni, numero e
nomi) e «X ha come principio attivo Y» (vale per tutte le confezioni X della lista, ATC, confezioni, gruppi) ricalcolate dal CSV grezzo; nei titoli
e nelle descrizioni delle pagine principio attivo «N confezioni», «N carenti», «N nomi», «da … a …» € e «X ha come principio attivo Y» ricalcolati
dal CSV; il titolo nato da una frase misurata contiene la parola e il nome di quella frase e la frase è nel file con quel volume; tabella «Stato per
principio attivo» e cifre delle FAQ nuove di carenze e guida ricalcolate dal CSV dei carenti; parole da consiglio in più («dovresti»,
«sostituiscilo», «scegli il generico», «puoi sostituire»…). Browser: aggiunta `/sertralina/`. Prova a mano: cifre alterate in copie di 3 pagine →
5 errori trovati su 5.

**Dubbi per il revisore.** (a) «Cialis generico (tadalafil)» nel titolo: è la frase più cercata (6.600) e la pagina ha solo dati AIFA, ma è il
marchio con più rischio di sembrare promozione: se non va, una riga in `candidati_titolo` (o togliere tadalafil dalle frasi) e torna «Cialis ed
equivalenti…». (b) «generico/generici» nei titoli e nelle domande: è la parola delle ricerche; AIFA usa «equivalente» (il titolo «Farmaci generici»
compare nella sua pagina sui farmaci equivalenti); le risposte restano sui gruppi di equivalenza. (c) Le frasi «simili» dello strumento sono trattate
come misurate (come per ATECO). (d) Le 22 pagine nuove indicizzate hanno pubblicità solo se superano le 400 parole (regola invariata).

## Revisione indipendente (13/11/2026, sera)
**Cifre.** Lista di trasparenza riscaricata da AIFA (identica byte per byte a `raccolta/_grezzi/trasparenza.csv`, 15/10/2026). L'elenco dei carenti
riscaricato oggi è già **aggiornato al 13/11/2026** (2.524 righe; ~45 righe diverse da quello del 10/11: tolte, aggiunte o con fine presunta nuova):
le cifre del sito sono state ricontrollate sul file del 10/11 in `_grezzi` (uguale al nuovo in tutte le righe non cambiate, intestazione «aggiornato al
10/11/2026»). Con un lettore scritto a parte, sulle 111 pagine ritolate e le 22 nuove indicizzate: 1.000 cifre controllate in titoli, h1, descrizioni e FAQ
(confezioni, carenti, nomi, intervalli di prezzo, «X ha come principio attivo Y» su tutta la lista, ATC, gruppi, prezzi per gruppo dei nomi commerciali,
«altri N nomi» e prezzo di riferimento per gruppo, righe nell'elenco carenti) + tabella «Stato per principio attivo» (20 righe × 3 numeri) + FAQ di
carenze: **0 differenze** (le «56 righe di quetiapina» contano le tre grafie AIFA: quetiapina 30, quetiapina fumarato 25, quetiapine 1). Tutti i 34
titoli «X: principio attivo Y» (e «Brufen generico (ibuprofene)», «Auradol (frovatriptan)») valgono: il nome commerciale X nella lista ha solo quel principio attivo.
**Decisioni sui farmaci con ricetta «di stile di vita»** (`TEMI_SENSIBILI` in `genera.py`: tadalafil, sildenafil, vardenafil, finasteride).
Nella lista AIFA tadalafil, sildenafil e vardenafil sono solo confezioni da 20/25 mg con la nota «In distribuzione diretta da parte delle Regioni»:
chi cerca «generico cialis» (6.600) cerca altro, e un titolo costruito su quella frase sembra un richiamo commerciale a un farmaco con ricetta.
Quindi: titolo con il principio attivo in testa («Tadalafil: equivalenti di Cialis nella lista AIFA», «Sildenafil: equivalenti, prezzi e carenze nella
lista AIFA», «Finasteride: nomi commerciali ed equivalenti nella lista AIFA»), h1 e descrizione senza «generico», la domanda «Qual è il generico di
Cialis?» diventa «Qual è l'equivalente di Cialis?», **nessuna pubblicità** su queste quattro pagine (rischio norme AdSense su salute sessuale e farmaci
con ricetta; il segno «adsense: no» è lo stesso delle pagine noindex). Restano indicizzate (tranne vardenafil, già noindex): sono solo dati AIFA, senza
inviti all'acquisto; nel sito non ci sono «compra/acquista/online/senza ricetta» (controllato). Se Search Console o AdSense segnalano qualcosa: noindex
con `INDICIZZA[pa] = False` per gli slug di `TEMI_SENSIBILI`. Oppioidi, isotretinoina, contraccettivi: titoli già neutri «<marca> ed equivalenti…».
**«Generico» nei titoli.** Ammesso come parola delle ricerche perché ora ogni pagina che lo usa (titolo, h1, descrizione o domande: 109 pagine) dice nel
primo paragrafo «"Generico" è la parola delle ricerche: il termine di AIFA è "equivalente"» (`TERMINE_GENERICO`, solo dove serve, per non alzare il
testo in comune delle altre). Indicizzazione invariata (250 / 244); testo in comune massimo 59,8% (terbinafina; verapamil 59,7%, ticlopidina 59,3%):
sono pagine al limite, da guardare per prime in Search Console.
**Correzioni minori.** Descrizione «ZARELIS ha come principio attivo venlafaxina: 75 confezioni…» (sembravano 75 confezioni Zarelis) → «75 confezioni
di venlafaxina»; «altri 1 nome commerciale» → «un altro nome commerciale», «altri 0 nomi» → «solo confezioni con lo stesso nome»; «costano da 46,08 € a
46,08 €» → «costano tutte 46,08 €»; «1 carenti» nell'indice dei gruppi; l'elenco nel testo «Nomi commerciali nella lista (2)» contraddiceva la FAQ «18 nomi
commerciali» (contava solo i nomi di fantasia) → «Nomi di fantasia nella lista (2)»; apertura di queste note (il sito è online dal 13/11).
**Risposte ai dubbi.** (a) Cialis: vedi sopra. (b) «Generico»: vedi sopra. (c) Frasi «simili» trattate come misurate: accettabile, il volume è quello
dello strumento. (d) Pubblicità sopra le 400 parole: invariato, tranne le quattro pagine sensibili. **Da fare alla pubblicazione:** aggiornare i carenti al
13/11 (`fonti.py --rete`, `estrai.py`, genera, verifica) prima del prossimo push (`verifica.py` avvisa dal 20/11); titolo noindex «Amlodipina+ Valsartan…» con lo spazio
come scritto da AIFA (pagina noindex, lasciato).

