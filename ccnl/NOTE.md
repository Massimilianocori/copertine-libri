# Paga CCNL – note di lavoro (12/11/2026)

Sito statico in italiano: minimo mensile, paga oraria e giornaliera, part time e aumenti già firmati per contratto × livello.
Nato dalla verifica dati CCNL del 12/11/2026 (`studio-business/intelaiatura/fronti-2026-11-12-radar-settori-diversi.md`, ultima sezione).
Indirizzo previsto `https://paga-ccnl.netlify.app` (costante `URL_SITO` in `genera.py`, unico punto da cambiare).
**Il sito Netlify non esiste ancora**: i passi sono in fondo.

## Pagine (63 indicizzabili + 404)

| Pagina | Contenuto |
|---|---|
| `/` | ricerca nella tabella di tutti i 53 livelli (minimo, paga oraria, data), metodo, 4 FAQ |
| `/<contratto>/` (5) | cifre chiave, tabella dei livelli, calendario degli aumenti, regole usate (divisori, mensilità, orario con articolo), cifre escluse con motivo, FAQ, documenti ufficiali |
| `/<contratto>/<livello>/` (53) | minimo con le sue voci e il controllo fatto, paga oraria e giornaliera con formula e articolo, calcolo per ore settimanali (solo lordo), tabella 20/24/30/tempo pieno, minimo annuo con le mensilità, aumenti futuri, minimi precedenti, livelli vicini, declaratoria citata dal contratto (domestico, commercio, metalmeccanici), FAQ dove esiste una ricerca vera, fonti numerate, «Controllato il» |
| `/colf-badanti/` | guida per le famiglie: livello, convivente o a ore, tabella B, vitto e alloggio (tabella F con controllo della somma), notturno (D, E), sostituzioni (G), indennità (H, I, L), tredicesima, aumenti 2027-2028, calcolo a ore, 4 FAQ |
| `/come-lavoriamo/`, `/chi-siamo/`, `/privacy/`, `404.html` | metodo, elenco dei 19 documenti con impronta, cifre escluse, modulo «segnala un errore» (Netlify Forms, email facoltativa, consenso) |

Pagine livello per contratto: lavoro domestico 8 (A, AS, B, BS, C, CS, D, DS), commercio 8 (Quadro, 1°-7°), metalmeccanici 9 (D1-A1),
multiservizi 8 (1°-7°, Quadro), logistica 20 (non viaggiante Q, 1, 2, 3S, 3, 4, 4J, 5, 6; viaggiante C3, B3, A3, E2, D2; driver e rider H1, G1,
I primi 6 mesi, I, L 7-15 mesi, L).

## Fonti e regola di qualità

Una cifra si pubblica solo se (1) le voci stampate sommano al totale stampato e (2) una seconda fonte indipendente riporta lo stesso importo al
centesimo. `raccolta/estrai.py` scrive tutto in `dati/contratti.json` (anche le righe escluse, con il motivo); `verifica.py` rifà somma e confronto da zero.

| Contratto | Fonte A | Fonte B | Regole (frase controllata nel testo) |
|---|---|---|---|
| Lavoro domestico (H501) | tabella 2026 del Ministero (`min_domestico_2026`) | stessa tabella depositata al CNEL con il verbale 11/2/2026 (accordo 245798) | CCNL 28/10/2025 (245143): 1/26 giornaliero, 13 mensilità art. 39, 54/40 ore art. 14, aumenti art. 55 |
| Terziario Confcommercio (H011) | testo unico 3/2/2026 (246574), pagine 363-364 lette con OCR (cifre in caratteri codificati) | tabelle dei minimi di Filcams CGIL (pagina web) | art. 215 divisore 168 (182/195), art. 214 divisore 26, artt. 224-225, art. 133 (40 ore) |
| Metalmeccanici (C011) | tabelle impiegati/operai del decreto n. 94 del 26/10/2026 (annuo ÷ 12, divisione esatta) | ipotesi di accordo 22/11/2025, pag. 2 (Federmeccanica, scansione con OCR) | CCNL 5/2/2021 (157071): divisore 173 (Sez. IV Tit. IV artt. 3 e 5), tredicesima (art. 7), 40 ore |
| Multiservizi (K511) | tabelle del decreto n. 25 del 30/3/2026, pagine «NAZIONALE» (annuo ÷ 12), 8 date fino a marzo 2029 | accordo integrativo 6/8/2025 (234752, scansione con OCR + 32 correzioni in `dati/correzioni_ocr.json`) | CCNL 31/5/2011 (105782): art. 19 divisore 173 e 22/26, artt. 20-21, art. 30 (40 ore). Controllo in più: aumento stampato = differenza tra due date |
| Logistica (I100) | testo 25/9/2025 (223634), tabella minimi + EPA | decreto n. 135 del 19/12/2025 (annuo ÷ 12) | art. 61 c. 3 divisori 168 / 22 / 26, artt. 18-19, artt. 9 e 11 (39 ore) |

Tutte le fonti sono lette da `raccolta/fonti.py` (HTTP, byte, SHA-256, pagine, frasi) in `dati/fonti.json`; i file grezzi stanno in
`raccolta/_grezzi/` (fuori da git, ~35 MB, si riscaricano). OCR: tesseract 5, italiano, 300 dpi, `--psm 4`; testo in `_grezzi/ocr/`.
Confcommercio e FIM CISL rispondono 403 al robots: non usati. Federmeccanica: robots permesso, pausa di 3 secondi rispettata.

### Cifre escluse (e perché)
- Logistica F2 (viaggiante), tutte le date: minimo + EPA ≠ totale stampato (6 centesimi; il testo ufficiale è così).
- Logistica non viaggiante dal 1/1/2027 (9 livelli): i totali stampati usano già il minimo di giugno 2027; le voci coincidono col Ministero ma il totale no. La data compare con «—» e una nota; dal 1/6/2027 tutto torna.
- Logistica L primi 6 mesi (parametro 110) dal 2026: il Ministero stampa EPA 120,00 annui (10 al mese) invece di 16,67 al mese: nessuna pagina.
- Metalmeccanici giugno 2027 e 2028: solo nell'accordo (e possono salire con l'IPCA): testo senza cifre fino al decreto del Ministero.
- Multiservizi 2° livello parametro 115 e logistica 6° Junior (solo 2025): nessuna pagina (manca la seconda fonte / non più in tabella).
- Operatori di vendita del commercio: solo nella tabella della pagina contratto (somma e Filcams tornano), senza pagina propria.

## Controlli (`python3 ccnl/verifica.py --browser`, 12/11/2026: 0 errori, 0 avvisi)
1. Fonti: HTTP 200, impronta del file uguale a quella registrata, tutte le frasi trovate; `cnel_monitor.json` presente.
2. Regole: ogni divisore/mensilità/orario ha una frase che è tra quelle controllate e contiene il valore; le citazioni delle declaratorie sono nel testo (o nell'OCR).
3. Cifre: 211 righe livello × data ricalcolate da `estratti.json` (177 pubblicabili, 34 escluse) e confrontate con `contratti.json`; in ogni pagina livello si cercano minimo, paga oraria, giornaliera, annuo, part time 20/24/30/pieno e aumenti futuri; gli attributi del calcolo coincidono con i dati.
4. Pagine: titolo ≤ 65 e descrizione 70-160 caratteri, unici; un h1; canonical; sitemap = canonical; link interni e ancore; risorse; GoatCounter in ogni pagina (404 compresa); robots, chiave IndexNow, netlify.toml, og.png.
5. FAQ: 49 domande, ogni ricerca è tra i 931 suggerimenti salvati (`dati/domanda.json`, hl=it gl=it); JSON-LD = testo visibile; nessun segnaposto rimasto.
6. Testi: nessun nome di modello o servizio di IA, nessun dato personale, nessun netto.
7. Monetizzazione: `monetizzazione.controlla_sito` (AdSense acceso, ads.txt, privacy) — anche `python3 studio-business/strumenti/monetizzazione.py verifica ccnl`.
8. JS = Python: il calcolo del browser (interi in centesimi, mezzo verso l'alto) su 1.828 casi.
9. Browser (Playwright, ogni richiesta esterna bloccata con `page.route`): home, commercio 4° livello, domestico CS, contratto logistica a 375 e 1280 px, chiaro e scuro; niente scorrimento orizzontale, testi ≥ 11 px, sfondo coerente col tema, calcolo a 24 ore, pulsanti delle ore, ricerca della home, pulsante del tema, nessun errore JS. Screenshot in `cache/screenshot/` (fuori da git).

## Aggiornamento
**Ogni mese (1 ora):**
1. `python3 ccnl/raccolta/fonti.py --rete` — riscarica tutto; guardare in `dati/cnel_monitor.json` se per H501, H011, C011, K511, I100 c'è un accordo nuovo (campo `ultimi`, confrontare gli id con la tabella qui sopra) e se un'impronta è cambiata (`git diff ccnl/dati/fonti.json`).
2. Rileggere le pagine di settore del Ministero (metalmeccanico, pulizia e multiservizi, logistica; elenco decreti dell'anno) per decreti nuovi.
3. `python3 ccnl/raccolta/estrai.py && python3 ccnl/genera.py && python3 ccnl/verifica.py --browser`; aggiornare `controllato_il` in `dati/contratti_meta.json`.

**Scadenze note:**
- Gennaio 2027: nuova tabella del lavoro domestico (Ministero + deposito CNEL). Dal 1/1/2027 `genera.py` e `verifica.py` si fermano finché non c'è: aggiungere la fonte in `fonti.py` (anno nuovo) e la data in `estrai.py` (`righe_livello`, ramo domestico).
- 1/1/2027 logistica non viaggiante: la riga resta esclusa (totali sbagliati nel testo); `genera.py` si ferma con errore il 1/1/2027 se nel frattempo non c'è una fonte che la chiarisca. Opzione prevista: se il Ministero conferma le voci, pubblicare minimo + EPA come somma delle voci verificate (decisione da scrivere qui prima di farlo).
- 1/2/2027 commercio: ultima rata già caricata; il contratto scade il 31/3/2027 → controllare il rinnovo al CNEL.
- Giugno 2027 metalmeccanici: verbale IPCA e poi decreto del Ministero → nuova fonte A (tabelle del decreto) e controllo con l'accordo.
- Multiservizi: nessun lavoro fino al 2029 salvo conguagli (clausola consuntivo art. 73).

Ricerche (FAQ): `python3 ccnl/raccolta/domanda.py` ogni 3 mesi; `verifica.py` segnala le FAQ la cui ricerca non c'è più.

## Monetizzazione
AdSense acceso come gli altri siti: `ccnl` aggiunto a `SITI` in `studio-business/strumenti/monetizzazione.py` e ad `adsense_siti` e `_siti_della_rete`
in `monetizzazione.json`; `ads.txt` scritto da `genera.py`; script solo nelle pagine indicizzabili con almeno 400 parole di contenuto
(regola di EsameB1, per la lezione AdSense «scarso valore» dell'11-12/11): oggi tutte tranne la 404 e una pagina breve. Ogni pagina livello ha
cifre proprie (voci, divisore, part time, aumenti, storico, livelli vicini, declaratoria). Nessuna affiliazione.

## Da fare per pubblicare (passi di Massimiliano)
1. Netlify: «Add new site» → «Import an existing project» → GitHub, repository di questo progetto, **branch `ccr-b7fd6b9e-n096cr`**;
   Base directory `ccnl/sito`, Build command vuoto, Publish directory `.` (il file `ccnl/sito/netlify.toml` lo conferma);
   nome del sito `paga-ccnl` (se diverso, cambiare `URL_SITO` in `ccnl/genera.py` e rigenerare).
2. Netlify → Forms: lasciare acceso il rilevamento dei moduli (modulo `segnalazioni`) e impostare la notifica email.
3. Search Console: proprietà `https://paga-ccnl.netlify.app/` (meta di verifica già nelle pagine), inviare `sitemap.xml`.
4. Dopo la pubblicazione: aggiungere l'host a `SITI` in `studio-business/strumenti/indexnow.py` (cartella `ccnl`) e lanciare l'invio.

## Dubbi aperti per il revisore
- Multiservizi: divisori, mensilità e orario vengono dal testo del 2011 (i rinnovi 2021 e 2025 al CNEL sono scansioni; le pagine lette non toccano l'art. 19). Il Ministero usa anch'esso 173.
- Metalmeccanici: divisore e tredicesima dal testo 2021; il rinnovo 22/11/2025 non è nell'archivio corrente del CNEL.
- Lavoro domestico D/DS: la tabella stampa minimo e indennità di funzione separati senza totale; l'art. 34 dice che il minimo la comprende: le pagine mostrano le due voci e la loro somma (calcolo nostro, dichiarato).
- Logistica I/L: le etichette «primi 6 mesi», «7-15 mesi» vengono dalle tabelle del Ministero; il contratto stampa solo i parametri.
- Part time: proporzione lineare sull'orario normale del contratto (40 o 39 ore); per driver discontinui l'orario di riferimento è diverso (detto in pagina tramite le regole).
