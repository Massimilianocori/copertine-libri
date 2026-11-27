# Before You Fly — piano di rilancio

Scritto il 27/11/2026. Solo analisi: nessuna pagina del sito toccata, nessun commit.

Si legge insieme a `STRATEGIA-RECUPERO.md` (fermo fino al 9/12, decisione sullo sfoltimento il 2/12) e a `ADSENSE-AUDIT-2026-11-26.md`. Questo documento è il piano dei rischi scritto prima, come chiede `REGOLE-FISSE.md` per ogni sfoltimento.

## 0. In breve

1. **Il sito oggi vive di ChatGPT, non di Google.** Dal 17/11: ChatGPT 16 visite al giorno (53 %), Google 7 (23 %). Prima del crollo Google ne dava 27 al giorno.
2. **Le visite stanno su poche pagine.** 344 pagine su 1.554 hanno avuto almeno una visita in 41 giorni. 1.210 pagine (78 %) non ne hanno mai avuta una.
3. **Sì, per come è fatto oggi BYF è un sito «a modello in scala».** 885 pagine in indice su 1.554 (57 %) hanno meno di 100 parole proprie. Google rifiuta di scansionarne metà (791 «Rilevata, non indicizzata»). AdSense lo ha scritto: «low value content».
4. **Piano del 2/12:** togliere dall'indice e dalla sitemap 671 pagine sottili e senza visite. Poi, con la lista di Search Console in mano, altre 339 pagine dei passaporti. Il sito scende da 1.554 a 883 e poi a 544 pagine. Si perde zero visite misurate.
5. **Si tengono e si curano 4 sezioni:** bagaglio a mano, date dei biglietti, liquidi, «Available in» (solo indici dei servizi e Paesi con visite).
6. **Soldi, detto chiaro:** con le visite di oggi BYF vale circa 40 € l'anno (prudente) e circa 180 € l'anno (centrale). Gli 800 € l'anno scritti nel cruscotto chiedono da 4 a 12 volte le visite di oggi. BYF va tenuto a bassa manutenzione. Il dominio non si tocca.
7. **AdSense:** il 16/12 quasi di sicuro è presto. Data realistica: metà gennaio.

## 1. Chi visita che cosa

### 1.1 Da dove vengono i numeri

- GoatCounter, API pubblica, letta il 27/11. Visite pagina per pagina, giorno per giorno.
- Il contatore parte il 17/10. Per l'1–16/10 non esistono dati.
- Vecchio indirizzo (netlify.app) e dominio nuovo sono sommati.
- Provenienza: 496 richieste, una per pagina e per periodo. La somma torna con il totale delle visite (scarto 0).
- Tre periodi:
  - **A** = 17/10–8/11, 23 giorni, vecchio indirizzo.
  - **B** = 9–16/11, 8 giorni, dominio nuovo, settimana migliore.
  - **C** = 17–26/11, 10 giorni, dopo il crollo.

### 1.2 Totale del sito

| Periodo | Visite | Al giorno | Google | ChatGPT | Diretto | Interno e altro |
|---|---|---|---|---|---|---|
| A (23 gg) | 312 | 14 | 200 (8,7/g) | 39 (1,7/g) | 52 | 21 |
| B (8 gg) | 467 | 58 | 216 (27/g) | 115 (14/g) | 112 | 24 |
| C (10 gg) | 307 | 31 | 71 (7,1/g) | 162 (16/g) | 52 | 22 |

Cosa dice la tabella:

- Google è sceso del 74 % (da 27 a 7 al giorno). Non è a zero.
- ChatGPT non è sceso. È salito da 14 a 16 al giorno. Oggi è la prima sorgente.
- Altri motori e altri assistenti: 5 visite in tutto il periodo. Non contano.
- Il «diretto» del periodo B è gonfio: 45 visite sulla home in 8 giorni. Sono probabilmente controlli nostri e robot. Non è pubblico vero.

Visite per settimana (lunedì–domenica): 22 · 77 · 212 · 414 · 236 · 124 (ultima: solo 4 giorni, cioè 31 al giorno).

### 1.3 Per sezione

Colonne: pagine in indice; pagine con almeno una visita; visite totali; poi Google / ChatGPT nei tre periodi.

| Sezione | Pagine | Con visite | Visite | A: G / C | B: G / C | C: G / C |
|---|---|---|---|---|---|---|
| available-in | 449 | 104 (23 %) | 359 | 41 / 20 | 34 / 56 | 39 / 72 |
| liquids | 102 | 42 (41 %) | 165 | 75 / 2 | 42 / 12 | 4 / 12 |
| pagine principali (home e indici) | 27 | 17 | 148 | 7 / 3 | 15 / 4 | 5 / 9 |
| ticket-release-dates | 33 | 13 (39 %) | 83 | 10 / 7 | 14 / 15 | 4 / 27 |
| cabin-bags | 53 | 14 (26 %) | 54 | **0** / 4 | **0** / 11 | **0** / 32 |
| india-e-visa-fee | 25 | 15 (60 %) | 45 | 7 / 1 | 15 / 10 | 0 / 3 |
| canadian-passport | 229 | 35 (15 %) | 40 | 5 / 1 | 24 / 0 | 2 / 0 |
| australian-passport | 173 | 22 (13 %) | 38 | 5 / 0 | 21 / 0 | 8 / 1 |
| driving-abroad | 116 | 23 (20 %) | 31 | 13 / 0 | 6 / 4 | 2 / 3 |
| passport-validity | 225 | 19 (8 %) | 28 | 4 / 0 | 11 / 1 | 3 / 1 |
| public-transport-rules | 20 | 13 | 24 | 8 / 0 | 11 / 0 | 0 / 0 |
| pets | 17 | 5 | 18 | 15 / 0 | 2 / 0 | 0 / 0 |
| train-luggage-rules | 14 | 7 | 12 | 3 / 0 | 7 / 0 | 0 / 0 |
| winter-tyres-rental-car | 14 | 5 | 8 | 2 / 0 | 2 / 0 | 2 / 1 |
| blue-badge-abroad | 24 | 3 | 5 | 0 / 0 | 4 / 0 | 0 / 0 |
| foreign-licence (CA, AU, NZ) | 14 | 3 | 5 | 2 / 0 | 2 / 0 | 1 / 0 |
| tolls-rental-car | 13 | 3 | 4 | 1 / 0 | 2 / 0 | 0 / 0 |
| dog-airlines | 2 | 1 | 1 | 0 / 0 | 0 / 0 | 0 / 1 |
| scooter-rental-licence | 4 | **0** | **0** | — | — | — |
| **Totale in indice** | **1.554** | **344 (22 %)** | **1.068** | | | |

Le pagine italiane (`/it/`, 219, già fuori indice) hanno avuto 9 visite. Le altre 90 pagine fuori indice: 6.

Nella tabella l'indice di ogni sezione è contato in «pagine principali». Nelle righe qui sotto i numeri di una sezione comprendono anche il suo indice.

Cosa dice la tabella:

- **Liquidi era il motore su Google.** 79 visite da Google nel periodo A, 46 nel B, 6 nel C. È la sezione che ha perso di più.
- **Bagaglio a mano non ha mai avuto una visita da Google.** Zero in 41 giorni. Tutte le sue visite vengono da ChatGPT: 55, di cui 40 negli ultimi 10 giorni. `cabin-bags/united/` da sola: 25 visite da ChatGPT dopo il 17/11. È la pagina più vista del sito oggi.
- **Date dei biglietti cresce con ChatGPT** (8 → 15 → 27). `vatican-museums` è la seconda pagina del sito.
- **Available in tiene da sola dopo il crollo.** Google 40, ChatGPT 72 nel periodo C. Starlink fa quasi tutto: 240 visite su 359. Le 61 pagine Starlink per Paese con visite: 100 da ChatGPT, 45 da Google.
- **Le tre famiglie dei passaporti e la patente all'estero** sono 743 pagine (48 % del sito). Hanno portato 137 visite (13 %). Hanno avuto un momento buono su Google solo negli 8 giorni del periodo B.

### 1.4 Sezioni e gruppi con zero visite, mai

- `scooter-rental-licence`: 4 pagine, 0 visite. (L'indice ha avuto 2 visite da Google.)
- Dentro «Available in», quasi a zero: Uber 37 pagine, 2 visite. Bolt 26 pagine, 3 visite. Google Wallet 33 pagine, 8 visite. Wise 34 pagine, 13 visite (12 sull'indice).
- Quasi a zero come sezione: tolls (4 visite), blue-badge (5), foreign-licence (5), dog-airlines (1).
- Pagine singole senza nessuna visita: **1.210 su 1.554**. Di queste, 702 sono anche sottili (meno di 100 parole proprie) e 508 no.

### 1.5 Le pagine sottili portano visite

Attenzione a questo dato. Le 885 pagine sottili non sono tutte morte.

- 183 pagine sottili hanno visite: 447 visite, cioè il 42 % di tutte le visite del sito.
- 48 ne hanno 3 o più.
- Nel periodo C le pagine sottili hanno avuto 75 visite da ChatGPT e 35 da Google. Le pagine non sottili: 87 e 35.

Quindi: «sottile» non vuol dire «inutile». Una pagina che risponde sì o no a «Starlink c'è in Messico?» è corta ma serve. Il problema non è la singola pagina. È averne 885, quasi uguali, di cui 702 che nessuno ha mai aperto.

## 2. Diagnosi onesta

### 2.1 La misura

Ho rimisurato tutte le 1.863 pagine di `beforeyoufly/sito/` oggi. Metodo uguale all'audit: tolgo testata, menu, piè di pagina, script e riquadri di affiliazione. Divido il testo in gruppi di 5 parole. Una parola è «propria» se non sta in nessun gruppo che compare in 3 o più pagine. «Somiglianza» = quota di gruppi in comune con la pagina più simile della stessa sezione.

| Sezione | In indice | Parole totali (mediana) | Parole proprie (mediana) | Sotto 100 proprie | Somiglianza ≥ 0,6 |
|---|---|---|---|---|---|
| available-in | 449 | 424 | **16** | 442 (98 %) | 415 (92 %) |
| canadian-passport | 229 | 630 | 79 | 133 (58 %) | 84 (37 %) |
| passport-validity | 225 | 729 | 121 | 85 (38 %) | 38 (17 %) |
| australian-passport | 173 | 1.037 | 184 | 33 (19 %) | 40 (23 %) |
| driving-abroad | 116 | 600 | 57 | 90 (78 %) | 10 (9 %) |
| liquids | 102 | 1.088 | 121 | 45 (44 %) | 54 (53 %) |
| cabin-bags | 53 | 1.521 | 466 | 10 (19 %) | 10 (19 %) |
| ticket-release-dates | 33 | 1.374 | 753 | 0 | 0 |
| india-e-visa-fee | 25 | 1.187 | **29** | 21 (84 %) | 23 (92 %) |
| blue-badge-abroad | 24 | 1.255 | 104 | 12 (50 %) | 19 (79 %) |
| pets | 17 | 1.532 | **17** | 13 (76 %) | 14 (82 %) |
| pagine principali | 27 | 1.827 | 849 | 1 | 0 |
| 7 sezioni piccole scritte a mano (81 pagine) | 81 | 743–1.904 | 391–1.441 | 0 | 0 |
| **Totale** | **1.554** | | | **885 (57 %)** | **697 (45 %)** |

I numeri coincidono con l'audit del 26/11 (891) e con il cancello della pubblicità (891). La differenza di 6 pagine viene dalla soglia: 47 pagine stanno tra 100 e 115 parole proprie.

### 2.2 I fatti che dicono «sito a modello»

1. **57 % delle pagine in indice ha meno di 100 parole proprie.** In «Available in» la mediana è 16 parole proprie su 424. Cambia il nome del Paese e un «Yes».
2. **45 % ha una pagina sorella uguale per oltre il 60 %.**
3. **78 % delle pagine non ha mai avuto una visita.**
4. **Il sito è passato da 1.141 a 1.858 pagine in due settimane**, su una ventina di argomenti. 215 pagine Starlink sono uscite il 13/11. Il crollo è del 16–17/11.
5. **Google non scansiona metà del sito.** Search Console, proprietà nuova, rapporto Pagine, aggiornato al 23/11: 787 indicizzate, 797 non indicizzate. Di queste 791 sono «Rilevata, ma attualmente non indicizzata»: Google le conosce e non è mai andato a leggerle. Solo 6 sono «Scansionata, non indicizzata». Le indicizzate sono ferme a 800–900 dal 10/11 circa.
6. **AdSense ha rifiutato il sito il 24/11** per «low value content».

### 2.3 Come cambia la diagnosi con il dato di Search Console

- L'indicizzazione è a metà (787 pagine). Non è a zero.
- Ma le impressioni sono a zero dal 17/11 **con 787 pagine in indice**. Quindi il crollo non è «pagine fuori indice». È posizione e fiducia: Google ha le pagine e non le mostra.
- Insieme, Google rifiuta di leggere l'altra metà. Mueller (10/11/2026) dice che questo stato «di solito» vuol dire che i sistemi di qualità non sono convinti del sito.
- Questo conferma l'ipotesi I1 della strategia («Google non è convinto della qualità del sito») e la rende più precisa: **il giudizio è sul sito intero, non sulle singole pagine**. Anche le pagine buone e indicizzate hanno perso le posizioni. Liquidi: da 46 a 6 visite da Google.

Resta un'ipotesi, non una prova. Tre cose sono successe insieme (cambio di dominio, aggiornamento di Google del 10–24/11, centinaia di pagine nuove). Non si possono separare con i dati di oggi.

### 2.4 Quante delle 797 «non indicizzate» sono le 885 pagine sottili

Non lo posso sapere dal repository. Lo sa solo Search Console. Posso dare i limiti e una stima.

- Limite matematico: tra 122 e 791. (Le pagine in indice sono 1.554. Le sottili 885. Le non scansionate 791.)
- Se Google scegliesse a caso: 450 (57 %).
- Indizio vero: le pagine che hanno avuto una visita da Google dal 9/11 sono di sicuro indicizzate. Sono 150. Di queste, 62 sono sottili (41 %). Nel sito le sottili sono il 57 %. Quindi le sottili sono indicizzate un po' meno delle altre, ma Google ne ha indicizzate molte.
- **Stima: da 435 a 565 delle 797 sono pagine sottili. Diciamo circa 500 (60 %).** Le altre 300 circa sono pagine non sottili ma mai aperte: soprattutto passaporti (328 pagine non sottili a zero visite nelle tre famiglie).

Pagine con una visita da Google dal 9/11 (indicizzate di sicuro), per sezione:

| Sezione | In sitemap | Indicizzate di sicuro | Di cui sottili |
|---|---|---|---|
| available-in | 449 | 21 | 20 |
| canadian-passport | 229 | 23 | 11 |
| passport-validity | 225 | 11 | 5 |
| australian-passport | 173 | 15 | 0 |
| driving-abroad | 116 | 8 | 5 |
| liquids | 102 | 20 | 8 |
| cabin-bags | 53 | 0 | 0 |
| ticket-release-dates | 33 | 10 | 0 |
| india-e-visa-fee | 25 | 10 | 9 |
| altre | 149 | 32 | 4 |
| **Totale** | **1.554** | **150** | **62** |

È un minimo, non il numero vero (le indicizzate sono 787). Serve a una cosa sola: mostrare che Google ha indicizzato anche pagine sottili, e che le pagine di bagaglio a mano non danno nessun segno di vita su Google.

**La risposta esatta costa 5 minuti al titolare.** Search Console → Pagine → «Rilevata, ma attualmente non indicizzata» → Esporta. L'esportazione dà fino a 1.000 righe: le 791 ci stanno tutte. Con quella lista il conto per sezione è esatto. È la prima cosa da fare (sezione 3.2).

### 2.5 Risposta alla domanda

**Sì.** BYF oggi ha il profilo di un sito a modello in scala, e Google lo tratta così: non legge metà delle pagine e non mostra l'altra metà.

**Ma dentro c'è un sito vero, piccolo.** Circa 150–200 pagine scritte da fonti lette una per una: date dei biglietti (753 parole proprie di mediana), bagaglio a mano (466), le sezioni piccole (391–1.441), più gli indici. Sono le pagine che ChatGPT cita. Il lavoro è far vedere a Google quel sito, e togliere il resto dalla sua vista.

## 3. Piano

### 3.1 Principi

1. **Il dominio non si tocca.** Nessun ritorno a netlify.app. Nessun cambio di URL delle pagine che restano.
2. **Un solo intervento di sfoltimento, il 2/12.** Per regola, non per elenco a mano. Reversibile.
3. **Non si perde nessuna visita misurata.** Ogni pagina con almeno una visita resta.
4. **Non si chiude la porta a ChatGPT.** È il 53 % delle visite.
5. **Niente sezioni nuove.** Fino a quando Google non torna a mostrare il sito.

### 3.2 Prima del 2/12 (il fermo lo permette)

| # | Cosa | Chi | Tempo |
|---|---|---|---|
| P1 | Esportare da Search Console la lista delle 791 «Rilevata, non indicizzata» e delle 787 indicizzate (proprietà nuova) | titolare | 5 min |
| P2 | Esportare dalla proprietà **vecchia** la scheda Pagine, ultimi 3 mesi (impressioni per URL). È già richiesta dall'azione 1 della strategia | titolare | 5 min |
| P3 | Rendimento, proprietà nuova, ultimi 7 giorni: impressioni e clic al giorno. È la misura del 28/11 e del 2/12 | titolare | 2 min |
| P4 | Link interni dalle pagine che ChatGPT porta: da `cabin-bags/united/`, `cabin-bags/`, `ticket-release-dates/vatican-museums/`, `colosseum`, `available-in/starlink/` verso 3–5 pagine vicine che restano. Oggi chi arriva guarda una pagina e va via | noi | 1 ora |
| P5 | Dati: rileggere i 10 aeroporti con la data vecchia (LGW, EDI, NCL, LCY, AMS, BRU, FCO, DOH, ATH, CWL) | noi | routine |
| P6 | Preparare la regola della sezione 3.3 nel generatore, spenta. Provarla in locale. Non pubblicare | noi | 2 ore |
| P7 | Arricchire a mano, una per una, solo pagine con visite e con una fonte ufficiale vera. Nessun testo senza fonte | noi | a piccoli gruppi |

P4 e P7 toccano poche pagine. Non sono una pubblicazione di massa.

### 3.3 Il 2/12 — primo gruppo: 671 pagine fuori dalla vista di Google

**Regola.** Una pagina esce se sono vere tutte e quattro:

1. ha meno di 100 parole proprie (stessa misura del cancello della pubblicità, già nel generatore);
2. ha zero visite da qualunque sorgente dal 17/10 (da ricalcolare il giorno prima con i dati fino all'1/12);
3. non è la home, un indice di sezione, l'indice di un servizio o una pagina di servizio;
4. non è della sezione liquidi (vedi 3.5).

In più, dopo P2: una pagina con 10 o più impressioni nella proprietà vecchia resta (regola 2 dell'azione 7).

**Conteggio di oggi, con i dati al 26/11:**

| Sezione | Escono | Restano in indice | Nota |
|---|---|---|---|
| available-in | 340 | 109 | Starlink 155, Uber 35, Wise 32, Google Wallet 30, Apple Pay 26, Stripe 22, YouTube Premium 20, Bolt 20 |
| canadian-passport | 114 | 115 | |
| passport-validity | 77 | 148 | |
| driving-abroad | 75 | 41 | |
| australian-passport | 32 | 141 | |
| blue-badge-abroad | 10 | 14 | |
| pets | 9 | 8 | pagine per tratta |
| india-e-visa-fee | 8 | 17 | pagine per nazionalità; la tariffa resta nella tabella dell'indice |
| cabin-bags | 6 | 47 | solo pagine per misura (40x30x20…) |
| **Totale** | **671** | **883** | |

Il numero cambierà di poco il 2/12: ogni pagina che prende una visita in questi giorni resta.

**Che cosa si fa a queste pagine. È qui che smettiamo di chiedere a Google di leggerle.**

1. **Fuori dalla sitemap.** La sitemap passa da 1.554 a 883 URL. È il messaggio principale: «queste sono le pagine che contano».
2. **Fuori dai link.** Negli indici la riga del Paese resta, con il dato (sì/no, tariffa, regola). Ma senza link alla pagina. I blocchi «Most used» e «Related» puntano solo a pagine che restano. Oggi ogni indice chiede a Google di seguire centinaia di link verso pagine quasi uguali.
3. **Fuori dall'indice di Google.**
   - Sezioni senza visite da ChatGPT (passaporti, patente, blue badge, pets, India, misure): `noindex` normale, come le 309 pagine già fuori.
   - «Available in» (340 pagine): `noindex` **solo per Google** (`<meta name="googlebot" content="noindex">`). Così Bing e ChatGPT continuano a vederle. Motivo: questa sezione ha avuto 149 visite da ChatGPT, e 63 delle 66 pagine citate da ChatGPT sono sottili. Chiudere tutto vorrebbe dire rinunciare alla sorgente che cresce.
4. **Fuori dalla sitemap dei vecchi indirizzi.** Si tolgono i vecchi URL che portano a queste 671 pagine. Il 301 resta attivo.
5. **Nessuna pubblicità e nessun link di affiliazione.** È già così per il cancello.
6. **Nessun 301 adesso.** Sarebbe un secondo cambio di URL nel mezzo dello spostamento. L'unione vera (301 verso la riga dell'indice) si fa dal 23/12, come dice la strategia.

Non si usa robots.txt per bloccarle. Google non vedrebbe più il `noindex`.

**Eccezione alla regola dei 28 giorni.** L'azione 7 dice che una pagina pubblicata da meno di 28 giorni resta. Le 215 pagine Starlink sono del 13/11: il 2/12 hanno 19 giorni. Propongo di non applicare l'eccezione alle 155 Starlink senza visite. Motivo: sono la pubblicazione più vicina al crollo e la più «a modello» del sito (16 parole proprie). Le 61 con visite restano tutte.

### 3.4 Il 2/12 — secondo gruppo: 339 pagine dei passaporti, solo con la lista di Search Console

Sono pagine **non** sottili ma mai aperte, nelle famiglie morte per la regola dell'azione 7 (meno del 15 % di pagine vive, meno di 0,3 visite per pagina):

| Famiglia | Pagine vive | Visite per pagina | Escono (zero visite, non sottili) |
|---|---|---|---|
| passport-validity | 8 % | 0,12 | 129 |
| australian-passport | 13 % | 0,22 | 119 |
| canadian-passport | 15 % | 0,17 | 80 |
| blue-badge-abroad | 12 % | 0,21 | 11 |
| **Totale** | | | **339** |

Queste pagine hanno parole proprie, ma sono in gran parte frasi copiate dalle pagine dei governi (audit: australian 50 % di citazioni, canadian 35 %). Per un revisore è «contenuto di altri senza valore aggiunto».

**Condizione.** Una pagina di questo gruppo esce il 2/12 solo se, nelle esportazioni P1 e P2:

- è nella lista «Rilevata, non indicizzata» (Google non l'ha mai letta: non c'è niente da perdere), **e**
- ha meno di 10 impressioni nella proprietà vecchia.

Se P1 e P2 non arrivano, questo gruppo aspetta il 23/12. Stesso trattamento del primo gruppo (`noindex` normale, fuori da sitemap e link).

Con i due gruppi: **1.010 pagine fuori, 544 in indice.** Le 1.010 coprono, per stima, quasi tutte le 797 che Google non vuole leggere.

Le sezioni tra il 15 % e il 40 % di pagine vive (driving-abroad, tolls, foreign-licence, scooter) non entrano nel secondo gruppo. Si rivalutano il 23/12.

### 3.5 Che cosa si tiene e con quale valore vero

| Sezione | Pagine che restano | Perché | Cosa si aggiunge (da gennaio, una sezione alla volta) |
|---|---|---|---|
| **cabin-bags** | 47 | La più citata da ChatGPT. Zero da Google: tutto da guadagnare. 466 parole proprie | Una pagina di confronto unica tra le 40 compagnie (misure, peso, prezzo). Su ogni compagnia «che cosa è cambiato e quando», con data e fonte. Le 10 pagine per misura unite in una sola dal 23/12 |
| **ticket-release-dates** | 33 | 753 parole proprie, nessuna pagina debole. ChatGPT in crescita (27 in 10 giorni), Google presente | È il modello per tutto il sito. Solo manutenzione delle date. Nuove attrazioni: non più di 3–5 al mese, solo con domanda misurata, e non prima che Google riparta |
| **liquids** | 102 | Unica sezione con domanda Google provata (131 visite). Ha perso le posizioni, non la domanda | Le 30 pagine sottili senza visite (isole greche, piccoli aeroporti spagnoli: stessa regola nazionale) si uniscono dal 23/12 in pagine per Paese («Liquidi negli aeroporti greci»). Sulle 15 sottili con visite: stato dello scanner, limite vero (100 ml o 2 litri), data, frase della fonte |
| **available-in** | 109 | Tiene dopo il crollo. Starlink è la pagina più vista dopo la home | Gli 11 indici dei servizi diventano le pagine forti: tabella completa di tutti i Paesi, filtro, data dell'ultimo cambio, elenco «che cosa è cambiato». Le pagine Paese restano solo dove c'è una visita |
| **india-e-visa-fee** | 17 | 60 % di pagine vive | Niente. Solo dati |
| 7 sezioni piccole | 81 | Scritte a mano, nessuna debole. Costano poco | Niente. Rilettura dei dati al ritmo più lento possibile |
| passaporti, patente, blue badge | 150–490 | Solo le pagine con visite (e, senza il secondo gruppo, le non sottili) | Niente. Nessun lavoro nuovo. Si rivalutano il 23/12 |

Regola per ogni aggiunta: solo da fonte ufficiale letta, con revisore, una sezione alla volta, mai più di 20–30 pagine toccate in una pubblicazione.

### 3.6 Effetto atteso

- **Sulle visite, subito: zero.** Le pagine che escono hanno zero visite per definizione.
- **Su ChatGPT: zero o quasi.** Le pagine «Available in» restano visibili a Bing. Rischio residuo: senza link dagli indici, col tempo vengono rilette meno.
- **Su Google: incerto, e lento.** Google lo dice: rimpicciolire il sito da solo non alza la qualità (Mueller, 10/11/2026). E dice anche che togliere il contenuto poco utile «può aiutare il contenuto buono». Tempi ufficiali: «diversi mesi». Mia ipotesi: primo segno a 3–6 settimane (più scansioni al giorno, «Rilevata» in calo), impressioni di nuovo sopra 500 al giorno non prima di febbraio.
- **Su AdSense: è la condizione per riprovare.** Senza lo sfoltimento il punto 15 dell'audit (pagine deboli in indice) resta al 57 %.

### 3.7 Rischi

| Rischio | Quanto pesa | Cosa facciamo |
|---|---|---|
| Altro cambio grosso durante lo spostamento | Medio. È il motivo per cui è uno solo | Nessun URL cambia. Tutto si annulla rigenerando il sito con la regola spenta |
| Togliamo pagine che Google avrebbe premiato più avanti | Basso. Zero visite in 41 giorni e sotto 100 parole proprie | Le pagine restano online. Se una prende visite, rientra da sola alla generazione dopo |
| Zero visite misura il danno, non la domanda (pagine mai indicizzate) | Vero per il secondo gruppo | Per questo il secondo gruppo parte solo con la lista di Search Console |
| Google non reagisce | Probabile nei primi due mesi | Non si aggiunge un secondo sfoltimento. Si passa a bassa manutenzione (sezione 4) |
| Arriva l'aggiornamento di dicembre nel mezzo | Probabile | Si annota inizio e fine. Non si attribuisce a caldo nessun cambio |
| Il `noindex` solo per Google è meno comune | Basso. È una direttiva ufficiale | Controllo a campione con Controllo URL dopo 7 giorni |
| Il rapporto pagine deboli / pagine in indice peggiora con il secondo gruppo (213 su 544 = 39 %) | Vero | Vedi 3.9, punto 15: si misura sulle pagine con pubblicità, e si arricchiscono le 48 sottili con 3 o più visite |

### 3.8 Misura, ogni lunedì

Base = lunedì 30/11. Stesse misure, stessa ora.

| # | Misura | Dove | Base (26/11) | Buon segno |
|---|---|---|---|---|
| 1 | Visite da Google al giorno | GoatCounter | 7,1 | ≥ 14 entro il 4/1; ≥ 27 entro l'1/3 |
| 2 | Visite da ChatGPT al giorno | GoatCounter | 16 | non scende sotto 12 |
| 3 | Visite totali al giorno | GoatCounter | 31 | ≥ 45 entro l'1/2 |
| 4 | Impressioni al giorno, proprietà nuova | Search Console | ~0 | > 0 ogni giorno; ≥ 500 entro febbraio |
| 5 | Pagine indicizzate / «Rilevata, non indicizzata» | Search Console, Pagine | 787 / 791 | «Rilevata» sotto 150 entro il 4/1 |
| 6 | Richieste di scansione al giorno | Statistiche di scansione | da leggere | in crescita dopo il 2/12 |
| 7 | Campione fisso di 20 URL: quante indicizzate | Controllo URL | 2 su 10 il 24/11 | ≥ 14 su 20 |
| 8 | Visite sulle pagine tolte | GoatCounter | 0 | resta sotto 10 a settimana. Se una pagina ne prende 2, rientra |
| 9 | Visite da Google su `cabin-bags/` | GoatCounter | 0 | la prima visita da Google |

**Regole di decisione.**

- **9/12:** fine del fermo. Se la misura 6 non sale, niente altro sfoltimento: si aspetta.
- **23/12:** unione con 301 delle pagine tolte verso la riga dell'indice. Rivalutazione di driving-abroad, tolls, foreign-licence, scooter.
- **15/1/2027:** bilancio. Se Google è sotto 10 visite al giorno **e** le impressioni sono ancora ~0: BYF passa a «solo manutenzione» (sezione 4.3).
- **1/3/2027:** se Google è tornato a 27 al giorno o più: si riapre la crescita, una sezione alla volta, sul modello di date dei biglietti.

### 3.9 AdSense: lista per la nuova richiesta

La lista è quella dell'audit (17 punti). Stato di oggi e stato atteso dopo il 2/12.

| N. | Criterio | 26/11 | Oggi (misurato) | Dopo il 2/12 |
|---|---|---|---|---|
| 1 | Nessun codice sotto 100 parole proprie | NO (891) | **SÌ** (661 pagine con codice; controllato online: `starlink/turkey` senza, `cabin-bags/united` con) | SÌ |
| 2 | Nessun codice su pagine uguali per ≥ 80 % | NO | da rimisurare sulle 661 | da rimisurare |
| 3 | Meno del 5 % delle pagine con codice simili per ≥ 60 % | NO | da rimisurare | da rimisurare |
| 4 | Mediana delle parole proprie sulle pagine con codice ≥ 200 | NO (71) | da rimisurare | atteso SÌ |
| 5 | Al massimo 1 riquadro di affiliazione; nessuno sotto soglia | NO | **SÌ** (fatto il 26/11) | SÌ |
| 6 | Nessuna famiglia con codice e citazioni oltre il 30 % senza commento nostro | NO | NO (australian, canadian) | SÌ solo se il secondo gruppo parte, o se si toglie il codice dalle due famiglie |
| 7 | Le 20 pagine più viste hanno ≥ 100 parole proprie | NO (6) | NO | NO finché non si arricchiscono. Senza fonte ufficiale non si scrive: restano senza pubblicità |
| 8–13 | Codice in home, pagine di servizio, navigazione, privacy, chi siamo, ads.txt | SÌ | SÌ | SÌ |
| 14 | Messaggio di consenso visibile dall'Italia | da verificare | **da verificare (titolare, 2 minuti, finestra anonima)** | — |
| 15 | Pagine deboli in indice sotto il 20 % | NO (57 %) | NO (57 %) | 24 % con il primo gruppo (213 su 883). Per scendere sotto il 20 %: arricchire o unire circa 40 pagine (le 30 dei liquidi unite per Paese bastano quasi) |
| 16 | Correzioni online da 14 giorni, nessuna pubblicazione di massa | NO | NO | SÌ dal **16/12** (14 giorni dopo il 2/12) |
| 17 | Almeno 20 delle 30 pagine di punta indicizzate, impressioni ogni giorno da 7 giorni | da verificare | NO (impressioni ~0) | dipende da Google |

**Giudizio onesto sul 16/12.** I punti 16 e 17 non saranno veri insieme il 16/12, salvo sorprese. Il punto 15 chiede l'unione dei liquidi, che parte il 23/12. Una seconda bocciatura a distanza di tre settimane non insegna niente. **Data realistica: lunedì 11/1/2027**, con tutti i punti a SÌ. Il costo dell'attesa è piccolo: con 31 visite al giorno la pubblicità renderebbe pochi euro al mese.

Il 16/12 si fa comunque il controllo della lista. Se per caso è tutta SÌ, si chiede.

## 4. Quanto può rendere, in euro

### 4.1 I numeri di partenza

- Visite oggi: 31 al giorno = circa 11.300 l'anno.
- Settimana migliore di sempre (9–15/11): 414 visite = 59 al giorno = 21.600 l'anno.
- Incassi fino a oggi: nei documenti che ho letto non c'è nessuna vendita di affiliazione registrata per BYF. AdSense non è approvato.
- Resa stimata nel cruscotto (30/10): AdSense in inglese 6–10 € ogni 1.000 visite, se approvato. Modello misto della rete: 18 € ogni 1.000 visite, mai verificato con incassi veri.
- Costo: dominio circa 11 € l'anno. Più il lavoro: letture periodiche dei dati di 19 sezioni.

### 4.2 Stima per il 2027, con il piano

| | Prudente | Centrale |
|---|---|---|
| Google | resta a 7 al giorno | torna a 27 al giorno da marzo |
| ChatGPT | 18 al giorno | 25 al giorno |
| Altro | 6 al giorno | 8 al giorno |
| Visite nell'anno | circa 11.500 | circa 18.000 |
| AdSense | approvato da luglio: 5.700 visite × 6 € / 1.000 = **34 €** | approvato da febbraio: 15.500 visite × 8 € / 1.000 = **124 €** |
| Affiliazioni | 0–10 € (nessuna vendita finora) | circa 60 € (qualche prenotazione di auto, eSIM, biglietti) |
| **Totale lordo** | **circa 40 € l'anno** | **circa 180 € l'anno** |

Ipotesi dichiarate: resa AdSense presa dal cruscotto, lato basso; nessuna crescita «a raddoppio» come a inizio novembre; nessuna sezione nuova; le visite da ChatGPT rendono come le altre (non verificato).

Senza il piano, la stima prudente è la stessa (40 €) e la centrale non esiste: senza sfoltimento AdSense non passa.

### 4.3 La risposta onesta

- **Il cruscotto scrive 800 € l'anno (prudente) per BYF.** Per arrivarci servono da 45.000 visite l'anno (a 18 € ogni 1.000) a 130.000 (a 6 €). Cioè da 4 a 12 volte le visite di oggi. Niente nei dati di oggi lo sostiene. Propongo di correggere il cruscotto: **40 / 180 € l'anno**, con tetto a circa 600 € se Google torna e la crescita di inizio novembre riparte.
- **BYF da solo non guadagna in modo che conti.** Nemmeno nello scenario centrale ripaga il lavoro di manutenzione di 19 sezioni.
- **Ma non va chiuso, e non va spostato.**
  - Costa 11 € l'anno.
  - Ha una cosa che gli altri siti non hanno: ChatGPT lo cita 16 volte al giorno e cresce.
  - Unire le sezioni buone a un altro sito sarebbe un altro spostamento. La regola dice: nessun cambio di dominio finché non c'è un recupero misurato. E su un sito sano porterebbe il rischio, non il valore.

**Proposta: BYF a bassa manutenzione.**

1. Si fa il piano del 2/12 (una volta) e l'unione del 23/12 (una volta).
2. Poi il lavoro su BYF ha un tetto: **1–2 ore a settimana**. Solo dati delle 4 sezioni vive e misura del lunedì.
3. Letture periodiche: cabin-bags, ticket-release-dates, liquids, available-in al ritmo di oggi. Tutte le altre sezioni: una volta al mese, non di più. Le pagine fuori indice non si rileggono.
4. Nessuna sezione nuova e nessuna pagina nuova in blocco fino all'1/3/2027.
5. Le ore liberate vanno al sito che rende di più per ora di lavoro (oggi EsameB1).
6. Il 15/1 e l'1/3 si decide con i numeri della sezione 3.8. Se Google torna, BYF riparte dal modello che funziona: poche pagine, scritte da fonti lette, come date dei biglietti e bagaglio a mano.

## 5. Cosa non so

- Quali pagine sono indicizzate e quali no. Lo dice solo l'esportazione P1.
- Se le impressioni di Search Console sono davvero ancora a zero oggi. GoatCounter vede 7 visite al giorno da Google: qualcosa viene mostrato.
- Quale delle tre cause pesa di più (dominio, aggiornamento di Google, pagine in scala).
- Come ChatGPT sceglie le pagine. Ipotesi: passa da Bing. Per questo il `noindex` solo per Google su «Available in».
- Se le visite da ChatGPT rendono con la pubblicità quanto quelle da Google.
- Le soglie (100 parole proprie, 15 %, 0,3 visite per pagina, 20 %) sono nostre. Google non dà numeri.
- I dati partono dal 17/10. 41 giorni sono pochi per pagine a coda lunga come i passaporti: per questo il secondo gruppo ha una condizione in più.

## 6. Dove stanno i calcoli

Calcoli fatti il 27/11 con script temporanei, non salvati nel repository. Si rifanno con:

- visite: API GoatCounter `stats/hits`, un giorno alla volta, finestre più corte quando le pagine superano 100;
- provenienza: `stats/toprefs` con `include_paths` di una sola pagina per richiesta (con più pagine insieme la risposta è incompleta);
- parole proprie e somiglianza: metodo della sezione 2.1 su `beforeyoufly/sito/`; il generatore ha già la stessa misura (`parole_proprie()`), elenco in `beforeyoufly/dati/cancello_pubblicita.json`.
