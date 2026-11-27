# Piano visite: Visa Income e Paga CCNL — 27/11/2026

Solo analisi e piano. Nessuna pagina toccata, nessun commit.
Vale insieme a `STRATEGIA-RECUPERO.md` (fermo fino al 9/12) e a `REGOLE-FISSE.md` (i domini non si cambiano più).

Dove scrivo **ipotesi** non ho una prova diretta.

## In breve

1. **Nessun guasto tecnico.** Controllati oggi: 813 + 63 pagine in sitemap, 1.073 vecchi indirizzi, robots, canonical, noindex. Tutto a posto.
2. **Visa Income ha perso solo Google.** Google: 159 visite a settimana → 157 → **15**. ChatGPT è fermo a circa 110 a settimana. Il calo di Google è su tutte le sezioni insieme (197 pagine con visite da Google, ora 12).
3. **Paga CCNL ha perso solo Google.** 76 visite a settimana → 18. Caduta in un giorno, il 21/11, senza nostre modifiche.
4. **Stesso giorno per i due siti.** Visa tocca il fondo il 21/11, CCNL anche. È il segno di una decisione di Google sui domini nuovi (aggiornamento del 10–24/11 più fine della «prova» del sito nuovo). **Ipotesi**: serve un dato di Search Console per confermarla (sezione 5).
5. **Trovato un lavoro saltato:** il Home Office ha pubblicato il 26/11 i dati fino a settembre 2026. Le nostre 153 pagine dei rifiuti (quelle che ChatGPT cita) hanno ancora i dati di giugno. È una correzione di dati: si può fare oggi.
6. **Trovato un risultato forte:** l'esperimento sulle pagine dei rifiuti dice che le 36 pagine «facili da citare» prendono **138 visite da ChatGPT contro 54** delle 36 di controllo (1–26/11). È la leva più grande che abbiamo. Si allarga il 10/12.

---

## 1. Come ho misurato

- GoatCounter, API pubblica: `stats/hits` (pagine viste al giorno, dal 15/10 al 27/11) e `stats/hits/{id}` giorno per giorno per ogni pagina dei due siti (1.203 richieste), per sapere da dove arriva ogni visita.
- Vecchio e nuovo dominio sommati. Tolti gli eventi `/clic/`.
- Circa il 7 % delle pagine viste di Visa non ha una riga di provenienza: i totali per sorgente sono un po' più bassi dei totali del sito.
- Controlli online fatti con richieste dirette il 27/11 mattina.

## 2. Visa Income: che cosa è successo

### 2.1 Visite a settimana per sorgente

| Settimana | Google | ChatGPT | Dirette | Interne | Totale |
|---|---|---|---|---|---|
| 16–22/10 | 0 | 27 | 2 | 6 | 36 |
| 23–29/10 | 0 | 53 | 5 | 16 | 74 |
| 30/10–5/11 | 59 | 55 | 15 | 23 | 153 |
| 6–12/11 | 159 | 93 | 96 | 80 | 433 |
| 13–19/11 | 157 | 110 | 80 | 46 | 399 |
| 20–26/11 | **15** | 109 | 50 | 65 | 240 |

- **Google**: comincia solo il 2/11 (11 visite). Massimo il 10/11 (51 in un giorno). Poi 28–36 al giorno fino al 15/11; 19 il 16/11; 15 il 17 e il 18; 11 il 19; 5 il 20; **1–4 al giorno dal 21/11**.
- **ChatGPT**: stabile, 10–22 al giorno. Non ha risentito del cambio di dominio.
- **Dirette**: 48 e 35 visite alla home nelle due settimane dopo lo spostamento, 8 nell'ultima. Sono quasi tutte controlli nostri e robot dopo lo spostamento (**ipotesi**). Non è pubblico perso.
- **Interne**: il 23/11 un solo visitatore ha aperto 36 pagine di `moved-to`. Per questo `moved-to` sembra cresciuta: non è vero.

Il conto vero: **persi circa 140 visite a settimana da Google. Il resto tiene.**

### 2.2 Quali sezioni hanno perso Google

Visite da Google nelle settimane 6–12/11 → 13–19/11 → 20–26/11:

| Sezione | Google | ChatGPT nell'ultima settimana |
|---|---|---|
| Cerimonie australiane | 49 → 47 → **3** | 11 |
| Test di inglese UK | 35 → 28 → **0** | 7 |
| Who moved where | 15 → 19 → **1** | 6 |
| Pagine singole dei visti | 15 → 4 → **0** | 2 |
| Top university visas | 10 → 9 → **0** | 1 |
| Study in Italy | 8 → 12 → **2** | 0 |
| Pagine in spagnolo | 7 → 13 → **2** | 0 |
| Rifiuti dei visti | 8 → 19 → **6** | **79** |

- Non c'è una pagina che ha perso tanto da sola. Erano visite sparse: 197 pagine con almeno una visita da Google, nessuna sopra 5 a settimana. Nell'ultima settimana solo 12 pagine.
- Un calo così, uguale su tutte le sezioni negli stessi giorni, non viene da un difetto di una pagina. Viene da un giudizio sul sito intero (**ipotesi**, coerente con `STRATEGIA-RECUPERO.md`, I1 e I2).
- Le pagine messe in noindex il 13/11 avevano 17 visite da Google in tutto il periodo e 2 da ChatGPT. Non sono la causa.

### 2.3 ChatGPT: che cosa cita

- 79 visite su 109 vanno alle pagine dei rifiuti, quasi tutte alle pagine Paese (72 a settimana). Prime: Türkiye 15, India 7, Russia 6, Algeria 5.
- 152 pagine hanno ricevuto almeno una visita da ChatGPT; 61 nell'ultima settimana.
- **Esperimento «pagine facili da citare»** (`intelaiatura/esperimento-citazioni-2026-10-31.md`), visite da ChatGPT dall'1 al 26/11:

| | 36 trattate | 36 di controllo |
|---|---|---|
| Linea di base 17–31/10 | 37 | 27 |
| 1–26/11 | **138** | **54** |
| Senza la coppia Pakistan/Iraq | 127 | 51 |
| Coppie vinte | 18 | 8 |

Rapporto 2,6. Corretto per la partenza (÷ 1,36): 1,9. La soglia scritta nel piano dell'esperimento è 1,5. La prima lettura ufficiale è il 30/11.

### 2.4 Controlli tecnici (27/11)

| Controllo | Esito |
|---|---|
| Home `https://visaincomechecker.com/` | 200 |
| `http://` e `www.` | 301 verso il dominio giusto |
| `robots.txt` | `Allow: /`, una riga `Sitemap:` |
| `sitemap.xml` | indice di 17 file, **813 indirizzi**, uguali al repository |
| Le 813 pagine in sitemap | 813 rispondono 200; canonical = se stessa su 813; 0 noindex; 0 `X-Robots-Tag`; contatore presente su 813; annunci su 497 |
| 10 vecchi indirizzi (turkiye, pakistan, indice rifiuti, casey, uk-english-test/india, moved-to/nigerians, isee-parificato, j-find, es/…italia, work-visa-salary-thresholds) | 10 su 10: 301 verso la stessa pagina |
| Tutti i 1.073 indirizzi di `sitemap-vecchi-indirizzi.xml` | 1.073 su 1.073: 301 verso la stessa pagina, che risponde 200. **702** arrivano su una pagina in indice, **371** su una pagina in noindex (voluto dal 13/11) |
| Pagina che non esiste | 404 |
| Robot di Google, Bing e ChatGPT (stessa pagina con il loro nome) | 200, stessa pagina |
| Vecchio indirizzo con parametri (`?x=1`) | 301 che conserva i parametri |

Due cose piccole, da non toccare ora:
- Un vecchio indirizzo **senza** la barra finale fa due salti (netlify → nuovo dominio senza barra → con barra). Google conosce gli indirizzi con la barra. Nessun intervento.
- 1.574 link da pagine in indice verso pagine in noindex (870 in `moved-to`, 327 in `top-university-visas`, 147 in `country`, 104 in `h1b-wage-level`). Non è un errore, ma fa «scoprire» a Google 496 pagine che non vogliamo in indice. Vedi 2.5 e azione D3.

### 2.5 Come leggere i numeri di Search Console del 26/11

669 indicizzate + 351 «rilevate» + 35 noindex + 2 doppie = 1.057 indirizzi conosciuti. Il sito ha 813 pagine in indice e 496 in noindex.

- Google ha visto il noindex solo su 35 delle 496. Le altre 461 sono ancora o tra le «indicizzate» (entrate tra l'8 e il 13/11, prima del noindex) o tra le «rilevate». **Ipotesi**: buona parte delle 351 «rilevate» sono pagine in noindex, cioè pagine che non ci servono.
- Quindi «669 indicizzate» non vuol dire «669 delle nostre 813». Il numero giusto si legge filtrando per sitemap (sezione 5, controllo V2).

### 2.6 Cause, in ordine

1. **Google ha abbassato il sito intero tra il 16 e il 21/11** (ipotesi più probabile). Il sito aveva visite da Google solo dal 2/11; il dominio è nuovo dall'8/11; l'aggiornamento di Google è andato dal 10 al 24/11. Il massimo è il 10/11, la discesa è a gradini fino al 21/11. Le pagine sono in gran parte ancora in indice (669), quindi è un problema di posizione più che di indice.
2. **Nessuna causa tecnica nostra** trovata oggi.
3. **Noindex del 13/11 e titoli del 14/11**: non spiegano il calo (dati sopra e verifica del 25/11).
4. **Lavoro saltato da noi**: l'aggiornamento Home Office del 26/11 non è stato fatto. Non ha causato il calo, ma tocca le pagine che oggi portano più visite.

## 3. Paga CCNL: che cosa è successo

### 3.1 Visite per giorno e sorgente

| Giorno | 14 | 15 | 16 | 17 | 18 | 19 | 20 | **21** | 22 | 23 | 24 | 25 | 26 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Google | 5 | 3 | 16 | 25 | 16 | 11 | 11 | **2** | 0 | 1 | 1 | 1 | 2 |
| Totale | 13 | 9 | 26 | 32 | 20 | 17 | 15 | 3 | 0 | 1 | 1 | 6 | 6 |

- Settimana 13–19/11: Google 76, dirette 36, ChatGPT 4. Settimana 20–26/11: Google 18, dirette 2, ChatGPT 2.
- Le dirette erano quasi tutte sulla home nei primi giorni (controlli nostri, **ipotesi**).
- Google per contratto, 13–19/11 → 20–26/11: multiservizi 36 → 5; logistica 26 → 8; commercio 8 → 1; metalmeccanici 6 → 1. Pagine prime: indice multiservizi (15 → 2), logistica livello G1 (8 → 2), multiservizi 1° livello (6 → 1), 2° livello (5 → 0).
- 28 pagine con visite da Google nella settimana buona, 12 nell'ultima.

### 3.2 Controlli tecnici (27/11)

| Controllo | Esito |
|---|---|
| Home, `http://`, `www.` | 200; 301; 301 |
| `robots.txt` e `sitemap.xml` | a posto; 63 indirizzi |
| Le 63 pagine | 63 rispondono 200; canonical = se stessa; 0 noindex; contatore su 63 |
| Vecchio `paga-ccnl.netlify.app` (home, robots, sitemap) | 301 verso `pagaccnl.com` |
| Pagina che non esiste | 404 |
| Robot di Google, Bing e ChatGPT | 200 |

Un difetto vero, piccolo: **tutte le pagine hanno in sitemap la stessa data, 12/11** (`ccnl/genera.py`, riga della sitemap: usa `CONTROLLO` per tutte). I titoli e le 33 FAQ del 14/11 e la modifica del 25/11 non hanno mosso nessuna data. Google usa `lastmod` solo se è credibile.

### 3.3 Cause, in ordine

1. **Sito nato il 12/11 su un dominio nuovo.** Google lo ha mostrato per 7 giorni (14–20/11) e poi ha smesso il 21/11. Nessuna nostra pubblicazione tra il 14 e il 25/11. Stesso giorno del fondo di Visa. **Ipotesi**: fine della prova del sito nuovo più aggiornamento di Google.
2. Non è uno spostamento: il vecchio indirizzo è vissuto un giorno. Il Cambio di indirizzo non serve.
3. Nessuna causa tecnica.

---

## 4. Azioni che si possono pubblicare ADESSO

Regole del fermo: solo correzioni di dati, link interni, sitemap. Nessun indirizzo nuovo su Visa, nessun titolo cambiato, nessun noindex nuovo.

### Visa Income

**A1. Dati Home Office fino a settembre 2026 (la più importante).**
- Che cosa: il file «Entry clearance visa applications and outcomes detailed datasets, year ending September 2026» è online dal 26/11 alle 09:30 (controllato oggi: l'API di GOV.UK lo elenca, il file risponde 200, 33 MB). Le nostre pagine scrivono «July 2025 to June 2026 · published 27 August 2026». Era già previsto in `visaincome/NOTE.md` («26/11/2026: rilanciare lo script con `--nuovo`»).
- Passi, in quest'ordine:
  1. `python3 visaincome/raccolta/esperimento_citazioni.py misura --dal 2026-11-01 --al 2026-11-26` e salvare il risultato nel registro dell'esperimento (lettura prima del cambio).
  2. `python3 visaincome/raccolta/rifiuti.py --nuovo`
  3. `python3 visaincome/raccolta/trasferimenti.py`, `infermieri.py`, `ancestry.py` (usano lo stesso file).
  4. `python3 visaincome/raccolta/rifiuti_altri.py` (Australia, Nuova Zelanda, Canada: letti il 26/10; se c'è un mese nuovo entra).
  5. `python3 visaincome/genera.py && python3 visaincome/verifica.py`
  6. `python3 visaincome/raccolta/esperimento_citazioni.py impronte --motivo "Home Office, anno fino a settembre 2026, uguale nei due gruppi"` e una riga nel piano dell'esperimento.
  7. Revisione indipendente delle cifre UK su 10 Paesi, pubblicazione, `indexnow.py --solo visaincomechecker.com`.
- Pagine toccate: le 153 di `/visa-refusal-rates/` (blocco UK), le pagine UK di `moved-to`, `nurses-abroad`, `uk-ancestry-visa`. Cambia solo il dato.
- Effetto atteso: tenere e alzare le visite da ChatGPT sulle pagine dei rifiuti (oggi 79 a settimana) con un dato uscito ieri che pochi siti hanno già (**ipotesi**). `lastmod` vero su circa 200 pagine: invito a Google a rileggerle.
- Misura: visite da ChatGPT su `/visa-refusal-rates/` nella settimana 30/11–6/12 (base 79; bene se ≥ 90) e sul sito (base 109); numero di pagine citate (base 61). In Search Console: richieste di scansione al giorno dopo la pubblicazione.

**A2. Riga di link «per la stessa nazionalità» sulle pagine Paese dei rifiuti** (link interni, nella stessa pubblicazione di A1).
- Che cosa: le 74 pagine Paese sono la porta d'ingresso del sito (circa 100 arrivi a settimana), ma oggi linkano quasi solo dentro la loro sezione. Sulle 79 pagine di secondo livello della sezione: 2.418 link verso i rifiuti, 6 verso `moved-to`, 0 verso `uk-english-test`. Al contrario i link ci sono già (`moved-to/turkish/` → `visa-refusal-rates/turkiye/`).
- Dove: `visaincome/genera.py`, funzione `pagina_rif_paese` (riga 2656). Una riga sola, dopo il blocco UK, con al massimo 3 link: l'hub `moved-to/<nazionalità>/` (22 hub), la pagina `uk-english-test/<paese>/` (84 pagine Paese), e la pagina UK dei visti di famiglia. Solo verso pagine in indice. Uguale per trattate e controllo.
- Condizione: va dentro il passo 6 di A1 (impronte rinnovate, riga nel registro). Se il revisore dell'esperimento dice no, si rimanda al 10/12.
- Effetto atteso: piccolo. Oggi 16–21 clic interni a settimana dalla sezione; obiettivo +10. Porta lettori e link alle sezioni che hanno perso Google.
- Misura: visite con provenienza `visaincomechecker.com/visa-refusal-rates/…` su `moved-to` e `uk-english-test` (base: 0–2 a settimana).

**A3. Blocco «Most used pages» con i dati fino al 26/11** (link interni).
- Che cosa: `visaincome/dati/piu_usate.json` è fermo al 24/11 e si aggiorna a mano. Rifarlo con le visite 17/10–26/11 (stessa chiamata di `dati-recupero/visite-visaincome.json`). Entrano Türkiye, Russia, China, Jordan (SELT) più in alto.
- Dove: solo home e 6 indici di sezione (`blocco_piu`, riga 1302). Fuori dall'impronta del `lastmod`.
- Effetto atteso: piccolo. Misura: nessuna diretta; si controlla che le 24 pagine linkate siano le prime 24 per visite.

**A4. Niente da correggere nella sitemap di Visa.** Controllata: 813 indirizzi, date vere, nessun noindex. Resta da fare a mano (titolare): inviare `sitemap-vecchi-indirizzi.xml` in Search Console, se non è già fatto.

### Paga CCNL

**B1. `lastmod` vero per pagina** (correzione della sitemap).
- Dove: `ccnl/genera.py`, riga che scrive la sitemap (oggi `CONTROLLO.isoformat()` per tutte, circa riga 1429). Stesso metodo di Visa: impronta di titolo, descrizione, JSON-LD e `<main>`, registro `ccnl/dati/lastmod.json` (vedi `impronta_contenuto` in `visaincome/genera.py`, riga 1349). Primo avvio con le date vere da `git log` (12/11, 14/11, 25/11), non con la data di oggi.
- Attenzione: in `ccnl/` c'è lavoro di oggi non ancora pubblicato (strumento per l'annuncio, 4 pagine). La correzione va fatta nello stesso lotto, da chi sta lavorando lì, per non pestarsi i piedi.
- Effetto atteso: piccolo. Google rilegge prima le pagine cambiate davvero. Misura: in sitemap almeno 3 date diverse; in Search Console «Ultima lettura» della sitemap dopo la pubblicazione.

**B2. Pubblicare lo strumento per l'annuncio già costruito oggi** (decisione già presa dal titolare: scheda `2026-11-27-pagaccnl-annuncio.md`).
- Non è una mia proposta nuova: lo segno perché è l'unica cosa che dà a Paga CCNL una strada di visite che non dipende da Google (link da chi assume, ChatGPT). Dopo: revisione indipendente, IndexNow, sitemap a 67 pagine.
- Misura: quella della scheda (usi dello strumento, moduli).

**B3. Nessuna modifica alle 63 pagine esistenti.** Non c'è un difetto da correggere. Cambiare titoli o testi ora toglierebbe la possibilità di capire che cosa fa Google.

### Per tutti e due: controlli del titolare (20 minuti, decidono la diagnosi)

Sono nella sezione 5. Senza questi restiamo alle ipotesi.

---

## 5. Controlli in Search Console e Bing (titolare)

| # | Dove | Che cosa guardare | Che cosa decide |
|---|---|---|---|
| V1 | visaincomechecker.com → Rendimento → ultimi 28 giorni, con «Posizione media» accesa | clic, impressioni e posizione giorno per giorno dall'8 al 26/11 (una foto) | Impressioni crollate e pagine in indice stabili = Google ci ha abbassati (posizione). Impressioni che reggono = è solo un problema di clic |
| V2 | Indicizzazione → Pagine → in alto «Tutte le pagine inviate» | quante delle 813 inviate sono indicizzate | Il numero vero. Base per il 2/12 e il 9/12 |
| V3 | Indicizzazione → Pagine → «Rilevata, ma attualmente non indicizzata» → Esporta | l'elenco delle 351 | Lo confronto con l'elenco delle 496 noindex: se sono in gran parte quelle, il numero non preoccupa |
| V4 | Sitemap | `sitemap-vecchi-indirizzi.xml` inviata sì/no | — |
| C1 | pagaccnl.com → Indicizzazione → Pagine | quante delle 63 sono indicizzate; quante «rilevate» e «scansionate, non indicizzate» | Se sono in indice ma senza visite: posizione. Se non sono in indice: Google non si fida ancora del sito |
| C2 | pagaccnl.com → Rendimento, 28 giorni, con posizione | giorno per giorno dal 12 al 26/11 | La data esatta della caduta e se è posizione o indice |
| C3 | pagaccnl.com → Impostazioni → Cambio di indirizzo | deve essere **vuoto** | Conferma che il crollo non dipende da quello strumento |
| C4 | Controllo URL (senza richiesta) su: `/multiservizi-pulizie/`, `/logistica-trasporto-merci/livello-g1/`, `/multiservizi-pulizie/1-livello/`, `/multiservizi-pulizie/2-livello/`, `/logistica-trasporto-merci/5-livello/` | indicizzata sì/no, data dell'ultima scansione | Campione fisso di CCNL da rivedere ogni lunedì |
| B1 | Bing Webmaster Tools | aggiungere `visaincomechecker.com` e `pagaccnl.com` (si importano da Search Console), inviare `sitemap.xml` | ChatGPT cerca anche attraverso motori esterni e con il suo robot; da qui non riesco a vedere l'indice di Bing. Serve a proteggere il canale che tiene (**ipotesi** sull'effetto) |

---

## 6. Azioni per il 10/12 (dopo il fermo)

**D1. Allargare la forma «facile da citare» (la leva più grande).**
- Che cosa: data «Updated on», riquadro «Key figures» in frasi complete, `dateModified`, CSV e schema `Dataset`. Oggi solo su 36 pagine Paese.
- Regola: lettura del 30/11 e seconda lettura il 9/12. Se il rapporto corretto resta ≥ 1,5, il 10/12 si chiude l'esperimento prima del 28/12 e si mette la forma sulle 36 di controllo e sulle 2 pagine Paese fuori esperimento. Chiudere prima è una scelta: si perde il verdetto pieno, si guadagnano 18 giorni.
- Poi, una sezione alla volta: 10 council delle cerimonie con più visite, 10 pagine SELT, 22 hub di `moved-to` (già citate da ChatGPT: 6–11 visite a settimana).
- Dove: `visaincome/genera.py`, blocco «Esperimento» e `pagina_rif_paese`.
- Effetto atteso: le 36 di controllo fanno 54 visite da ChatGPT in 26 giorni; con il rapporto corretto 1,9 sarebbero circa 100. **Circa +50 visite al mese** su quelle pagine (stima prudente: +25).
- Misura: visite da ChatGPT sulle 36 ex controllo, 4 settimane prima e 4 dopo.

**D2. Sfoltimento (azione 7 di `STRATEGIA-RECUPERO.md`)**, deciso con V1–V3, non con le sole visite.

**D3. Link verso le pagine in noindex.** Per le quattro famiglie con più link (moved-to 870, top-university 327, country 147, h1b 104): togliere il link dove il dato è già nella tabella dell'hub, oppure unire le pagine nell'hub dal 23/12 (come scritto nella strategia). Effetto atteso: meno pagine «rilevate» inutili, scansione concentrata sulle 813 (**ipotesi**). Misura: «Rilevata, non indicizzata» in calo.

**D4. Paga CCNL: un contratto nuovo alla volta**, cominciando da cooperative sociali (6.600 ricerche al mese, due fonti esistono: `ccnl/NOTE.md`). Solo se C1 dice che le pagine attuali sono in indice. Effetto atteso: stima in `PIANO-FATTURATO.md`. Misura: visite da Google sulle pagine del contratto nuovo a 4 settimane.

**D5. Paga CCNL: forma «facile da citare» anche lì**, se D1 conferma: data visibile e frase completa con minimo e paga oraria in cima alle 53 pagine livello (la frase c'è già nelle FAQ). ChatGPT oggi porta 2–4 visite a settimana: base bassa, misura facile.

---

## 7. Come misuriamo, ogni lunedì

| Misura | Base (20–26/11) | Bene il 7/12 | Dove |
|---|---|---|---|
| Visa: visite da Google a settimana | 15 | ≥ 30 | GoatCounter, provenienza Google |
| Visa: visite da ChatGPT a settimana | 109 | ≥ 120 | GoatCounter, provenienza chatgpt.com |
| Visa: pagine citate da ChatGPT nella settimana | 61 | ≥ 70 | idem |
| Visa: pagine inviate e indicizzate | da V2 | in crescita | Search Console |
| CCNL: visite da Google a settimana | 18 (massimo 76) | ≥ 30 | GoatCounter |
| CCNL: pagine indicizzate su 63 | da C1 | in crescita | Search Console |
| CCNL: campione di 5 pagine indicizzate | da C4 | ≥ 4 su 5 | Controllo URL |

Le soglie «bene» sono **ipotesi** mie: Google non dà numeri. Se il 9/12 Google è ancora fermo su tutti e due i siti, vale quello che dice `STRATEGIA-RECUPERO.md`: tempi di mesi, si lavora sul canale che cresce (ChatGPT) e sulla qualità delle pagine migliori. Non si torna ai vecchi indirizzi.

## 8. Che cosa non fare adesso

- Non cambiare titoli, indirizzi o noindex su Visa prima del 9/12.
- Non toccare i 301 (nemmeno per il doppio salto senza barra).
- Non riscrivere le 63 pagine di Paga CCNL.
- Non contare le visite dirette alla home come pubblico: sono in gran parte controlli nostri.
- Non leggere «669 indicizzate» come «va bene»: prima V2.

## 9. Limiti di questa analisi

- Non vedo Search Console: la causa «Google ci ha abbassati» resta un'ipotesi finché non arrivano V1 e C2.
- Numeri piccoli: Paga CCNL ha 163 pagine viste in tutto. Un giorno fa già differenza.
- Non ho potuto controllare l'indice di Bing da qui.
- L'esperimento sulle citazioni ha numeri discreti (192 visite), ma Türkiye da sola ne porta 23: la lettura del 30/11 con la prova a permutazione dirà quanto fidarsi.
