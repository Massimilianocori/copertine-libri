# Real Estate Exam Pass Rates (realestate) – note di lavoro

Costruito il 14/11/2026 come **prova su 4 Stati** dell'idea «abilitazioni immobiliari con il tasso ufficiale per scuola»
(`studio-business/intelaiatura/fronti-2026-11-14-riaperte.md`, sezione A; `fronti-2026-11-14-notte-grandi.md`, idea B). Sito statico in inglese (USA)
generato da `genera.py` in `sito/`. Indirizzo proposto: **`https://real-estate-exam-pass-rates.netlify.app`** (nome libero il 14/11: risposta 404;
costante `URL_SITO` in `genera.py` e in `verifica.py`). **Il sito Netlify non esiste ancora** (in `indexnow.py` l'host è in `NON_ONLINE`).
Pubblicità: AdSense acceso (`monetizzazione.json`), contatore GoatCounter, meta di verifica Google della rete. Revisione indipendente fatta il 14/11/2026 (vedi in fondo).

## Pagine (12 indicizzabili + 404)

`/` (scegli lo Stato: 4 schede con il tasso dello Stato, esami, periodo; tabella di confronto di ciò che ogni commissione pubblica) ·
`/texas/` `/alabama/` `/nebraska/` `/hawaii/` (tabella ufficiale per scuola: percentuale come la stampa la commissione, promossi ed esami accanto,
ricerca, ordinamento, filtro «almeno 30 esami», filtro classroom/online per Alabama e Hawaii; come leggere le cifre con le frasi ufficiali) ·
`/texas-real-estate-license/` e le altre tre (passi, ore, scadenze, tariffe solo dalle pagine della commissione, con le frasi alla lettera) ·
`/how-we-check/` (metodo, le 4 fonti, modulo delle correzioni senza dati personali e con trappola per i robot) · `/about/` · `/privacy/`.
FAQ: 36, ognuna da una ricerca misurata (`dati/domanda.json`).

## Stati e fonti (20 file in `dati/grezzi/`, URL, data e SHA-256 in `dati/fonti.json`; 63 frasi alla lettera)

| Stato | Fonte dei tassi | Che cosa conta | Periodo | Scuole |
|---|---|---|---|---|
| Texas | `trec.texas.gov/sites/default/files/json/PassRatesRei.json`, il file che la pagina ufficiale carica | esame da sales agent, **solo primo tentativo** | 1/12/2023 – 30/11/2025 | 30 (totale ufficiale 29.980 esami, 56,12 %; le 30 scuole sommano esattamente al totale) |
| Alabama | `arec.alabama.gov/apps/SchoolStatsWF/` (una scheda HTML per scuola) | salesperson: **primo tentativo e tutti i tentativi** | «previous 12 months», aggiornato il 10 del mese (date non stampate) | 107 (40 senza esami nel periodo); nessun totale ufficiale: riga «our sum» |
| Nebraska | PDF del 1° trimestre 2026 (`School Pass Report firstquarter2026.pdf`), **l'ultimo collegato dall'indice ufficiale** | parte nazionale e parte statale: **first-time takers e totale** | 1/1 – 31/3/2026 | 12 (due con ≥ 30 esami) |
| Hawaii | bollettino «School Files» di ottobre 2026 (`sf2610.pdf`, PDF con testo) | parte nazionale e statale, **tutti gli esami** (primo tentativo non separato) | 1/10/2025 – 30/9/2026 | 24 codici di scuola (+ 5 categorie senza scuola, non in tabella) |

**Stati non costruiti e perché** (non riprovati oggi; esito della ricerca del 14/11): North Carolina, Colorado, Kansas (i siti delle commissioni rispondono 403 al
server: blocco non aggirato); Washington e Arizona (i PDF trovati danno 404). Restano «da riprovare» da un altro posto, non bocciati.

Cose da sapere sulle fonti:
- **Nebraska: solo rapporti collegati dall'indice ufficiale** (decisione applicata nella revisione del 14/11/2026). L'indice è `examperformancebyschool.pdf`
  («Updated July 2026»), collegato dalla pagina della Commissione `nrec.nebraska.gov/licensing-forms/educationinfo`. Per il 2026 collega solo il 1° trimestre
  (2°, 3° e 4° sono nominati ma senza collegamento): si usa quello. Il PDF del 3° trimestre, raggiunto indovinando l'indirizzo, è stato **tolto** (file, trascrizione e cifre).
  `fonti.py` e `verifica.py` leggono i collegamenti dell'indice e si fermano se l'indirizzo di `ne_tassi` non è tra quelli; `verifica.py` avvisa quando l'indice collega un trimestre più recente.
- **Nebraska è una scansione senza strato di testo**: le cifre sono trascritte a mano in `dati/manuali/ne_q1_2026.json` (lette dalle immagini delle 7 pagine), legate
  allo SHA-256 del PDF. Ogni riga deve tornare in tre modi (`fonti.py`, `verifica.py`); la seconda lettura è automatica (`raccolta/testo.py`, `pdf_ocr`: pdftoppm a 400 dpi + tesseract,
  risultato in `cache/`): 25 delle 45 righe coincidono cifra per cifra, le altre la macchina le legge male (un 1 preso per 4: righe che non tornano con la loro stessa aritmetica, contate come rumore).
  Servono `pdftoppm` e `tesseract` sul computer che lancia i controlli. Trimestre nuovo = nuova trascrizione, solo quando l'indice lo collega.
  Il rapporto è una stampa di Pearson con la scritta «PEARSON CONFIDENTIAL», ma è pubblicato dalla Commissione sul proprio sito e collegato dal suo indice pubblico: in pagina è citato così
  («report posted by the commission», «printout prepared by the exam company, Pearson, which the commission posts on its own website»), con soli conteggi per scuola.
  La stampa porta anche il nome di chi l'ha stampata: non è in nessun file nostro né in pagina.
- **Texas**: alcune scuole si registrano con punti esclamativi attorno al nome («! ! ! AYPORealEstate.com ! ! !»): in pagina il nome è senza, il nome ufficiale resta in `tassi.json`.
- **Alabama**: il sito chiede che il client accetti i cookie (altrimenti reindirizza all'infinito): `fonti.py` usa un barattolo dei cookie di curl. Non è un blocco aggirato.
  Le pagine lette **non stampano le tariffe** («Refer to the license application…»): la pagina della licenza lo dice e non dà cifre. Il «Blueprint» (PDF di 11 MB) non è stato messo tra le fonti.
- **Hawaii**: le percentuali del bollettino sono troncate a un decimale (4/6 = 66,6 %): mostrate come stampate. La tassa d'esame non è nelle pagine della commissione (è nel bollettino di PSI, non usato).
- Robot dichiarato (`research-bot`) per tutti gli scarichi; nessun dato su persone (solo scuole e conteggi).

## Regola dei campioni piccoli

Accanto a ogni percentuale ci sono promossi ed esami. Sotto 30 esami (soglia nostra, `SOGLIA_CAMPIONE` in `fonti.py`) la cella ha l'etichetta «small sample».
La tabella nasce ordinata per numero di esami; ordinando per percentuale le scuole sotto soglia vanno **dopo** le altre, con una riga di stacco, e quelle senza esami in fondo.
Nessuna classifica, nessun giudizio (`verifica.py` cerca «best», «worst», «top-rated»…).

## Domanda misurata (seodata, 14/11/2026, 106 ricerche in `dati/domanda.json`)

«texas real estate license» 18.100 (CPC 7,9 $) · «real estate license texas» 18.100 · «texas real estate commission» 14.800 · «alabama real estate license» 3.600 ·
«how to become a real estate agent in texas» 3.600 · «texas real estate license online» 3.600 (15,3 $) · «online real estate school texas» 1.900 (12,8 $) ·
«hawaii real estate license» 1.600 (12,3 $) · «texas real estate license requirements» 1.300 · «nebraska real estate license» 880 · «nebraska real estate exam» 880 ·
«texas real estate exam» 720. Sul tasso in sé poco: «real estate exam pass rate» 390, «texas real estate exam pass rate» 50, «trec pass rates» 30.
Somma delle frasi dei 4 Stati misurate: ~103.000 al mese (con doppioni dello stesso gruppo e le ricerche di navigazione verso le commissioni).
Generali: «real estate license» 60.500, «how to become a real estate agent» 33.100. Molte frasi lunghe risultano a 0 nello strumento.

## Guadagno

- AdSense come nel resto della rete (decisione sugli annunci secondo `ORGANIZZAZIONE.md`, sez. 4).
- **Riquadro del partner AceableAgent: SPENTO** (`dati/affiliati.json`: `"attivo": false`, `"link": ""`). Nessun link di affiliazione esiste e nessuno è stato inventato.
  Programma letto il 14/11 su `partnerships.aceable.com/affiliate`: «15–25% commission per sale, tiered by volume. 30-day attribution.» (scaglione di partenza 15 %).
  Per accenderlo (dopo l'iscrizione di Massimiliano, solo dopo le prime 300 visite al mese): link tracciato vero in `"link"`, dominio in
  `monetizzazione.json` (`domini_affiliazione`), `"attivo": true`, poi `genera.py`, `verifica.py --browser`, `monetizzazione.py verifica realestate`.
  Il riquadro esce solo in `/texas/`, sotto la tabella ufficiale, e solo se la scuola è in quella tabella. Provato acceso con un link di prova (poi tolto): 0 errori.

## Controlli (14/11/2026, dopo la revisione)

`python3 realestate/verifica.py --browser`: 0 errori, 0 avvisi. 20 fonti e 63 frasi alla lettera; **340 celle** delle quattro tabelle uguali a una seconda lettura dei
file grezzi scritta in un altro modo (Texas: JSON con percentuale ricalcolata; Alabama: cella per cella; Hawaii: pypdf invece di pdftotext; Nebraska: aritmetica e lettura automatica della scansione);
righe e totali chiave e tutte le cifre della licenza trascritti a mano in `verifica.py`; FAQ = JSON-LD e solo da ricerche misurate; link, titoli ≤ 65, descrizioni ≤ 160.
Browser: 13 pagine a 375 e 1280 px, chiaro e scuro (52 viste), contrasto ≥ 4,5, 29 prove sulle tabelle (ordini, filtri, ricerca, senza JavaScript).
`python3 studio-business/strumenti/monetizzazione.py verifica realestate`: 0 errori.

## Revisione indipendente (14/11/2026)

Il revisore ha riscaricato le 20 fonti (13 identiche byte per byte, 7 pagine HTML diverse solo nelle parti dinamiche), ritrovato le 63 frasi con un suo programma, e riletto
**tutte** le celle di Texas (30 righe + totale), Alabama (214 celle + somme) e Hawaii (48 celle + totali) contro i file riscaricati: nessuna differenza. Nebraska ritrascritto da capo sul 1° trimestre 2026.
Corretto: Nebraska (sopra); «a Alabama» nei titoli; «between … to …»; cifre degli esami accanto a ogni percentuale anche nelle FAQ; risposta «license online» del Texas
(diceva una cosa che la pagina citata non dice); frase causale sulle percentuali delle Hawaii; aggiunti la condizione dei sei mesi dell'Alabama, il corso dopo la licenza del Nebraska,
il nome uguale dei codici 1185 e 1188 delle Hawaii; riga «scorri la tabella» sul telefono; `verifica.py` confrontava il link del partner senza togliere `&amp;` (un link vero con `&` avrebbe dato errore).
Riquadro del partner: spento non scrive niente; provato acceso con un link di prova (0 errori) e rimesso spento, sito identico byte per byte.

## Aggiornamenti

`python3 realestate/raccolta/fonti.py && python3 realestate/genera.py && python3 realestate/verifica.py --browser`. Alabama cambia il 10 di ogni mese (le cifre a mano
in `verifica.py`, `ATTESO_RIGHE["AL"]`, vanno rilette); Hawaii ogni trimestre (nuovo `sfAAMM.pdf`: cambiare l'URL in `fonti.py`, i totali e i periodi a mano in `verifica.py`);
Nebraska quando l'indice ufficiale collega un trimestre nuovo (nuova trascrizione; `verifica.py` avvisa); Texas quando cambia il periodo nel file (finestra di due anni). `genera.py` avvisa se le fonti hanno più di 45 giorni.

## Non coperto (detto anche in pagina)

Esami da broker (sono nelle fonti); licenze per chi è già abilitato in un altro Stato; numero di domande e punteggio dell'esame dove non sono nelle pagine della commissione;
prezzi dei corsi; rinnovi. Lo stato delle scuole del Texas rispetto al «Minimum Pass Rate» (colonna +/- MPR della pagina ufficiale) è spiegato ma non mostrato scuola per scuola.
