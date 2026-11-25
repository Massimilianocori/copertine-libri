# Piano di crescita della rete — 26/11/2026

Solo ricerca. Nessun sito toccato. Nessun commit.
Regola usata: ogni decisione ha un numero e una fonte. Dove il dato manca c'è scritto **manca** o **ipotesi**.

Fuori da questo piano: EsameB1, Visa Income, Before You Fly (seguiti a parte; Visa e BYF fermi fino al 9/12).

## In breve

- I 20 siti di questo piano fanno **186 visite a settimana** in tutto (19-25/11). È il 17 % della rete (1.093).
- **Nessuno incassa.** AdSense non è approvato su nessun sito. Incassi veri del mese: 0 (registro del cruscotto, 25/11).
- Anche con AdSense approvato ovunque, 186 visite a settimana valgono **15-29 € l'anno** (conto sotto). Quindi nessuna azione qui rende più di 1 € per ora di lavoro in pubblicità.
- 13 siti su 20 hanno **da 0 a 5 visite a settimana**. Sono online da 12-18 giorni. Lì non c'è nessun dato che giustifichi ore di costruzione. Serve prima la foto di Search Console.
- Il rischio vero è un altro: **le routine di aggiornamento possono chiedere fino a 26 pubblicazioni prima del 15/12 (390 crediti). Ne restano 370**, e servono anche a EsameB1, che è l'unico sito con un prodotto che vende.
- Il solo sito con una crescita misurata e un dominio suo è **Paga CCNL**. Ma è crollato il 21/11 (da 15-32 visite al giorno a 0-6). Prima di costruire si controlla l'indicizzazione.
- La regola «togliere» chiede 90 giorni online. Il 1/12 **nessun sito ha 90 giorni** (i più vecchi ne hanno 52). Il 1/12 si chiude solo EsamiDiStato, per la regola dei dati non aggiornabili.

## Come ho misurato

- Fonte: API GoatCounter `rete-siti`, lette il 25/11/2026 tra le 23:10 e le 23:30 UTC.
- `stats/hits` con paginazione `exclude_paths` (id separati da virgola). `stats/toprefs?include_paths=` per le provenienze di ogni sito. `stats/total?include_paths=` per le visite al giorno.
- Circa 110 chiamate in tutto, una ogni 0,6 secondi.
- Settimane di 7 giorni pieni, a ritroso da oggi: **S1** 29/10-4/11 · **S2** 5-11/11 · **S3** 12-18/11 · **S4** 19-25/11.
- Totali della rete: 806 · 1.389 · 1.566 · 1.093. Gli eventi (clic sul libro, prove) sono esclusi.
- Host vecchi e nuovi sommati (es. `paga-ccnl.netlify.app` + `pagaccnl.com`).
- «Altro» = visite dirette più passaggi interni da una pagina all'altra.
- Limite: Search Console non è leggibile da qui. Impressioni e pagine indicizzate dei siti piccoli: **mancano** (ultime foto 31/10 per Cruise, FHA, FloodCost).

### Quanto vale una visita (conto usato in tutto il file)

- AdSense: 1,7-3,3 $ ogni 1.000 pagine (calcolatore pubblico di Google, già citato in `DA-PUBBLICARE.md`). In euro: **1,6 € prudente, 3,0 € centrale** ogni 1.000 visite.
- Formula: visite in più a settimana × 52 ÷ 1.000 × 1,6 (o 3,0). Cioè **0,08 € l'anno prudente e 0,16 € centrale per ogni visita a settimana in più**.
- Vale **solo se AdSense approva il sito**. Regola di `ORGANIZZAZIONE.md` sez. 4: dominio proprio, 21 giorni online, 30 pagine indicizzate, 300 visite al mese. Oggi nessun sito di questo piano la rispetta.
- Affiliazioni nuove: spente (decisione del 19/11). I riquadri vecchi (SafetyWing su Cruise e Italy Strikes, Amazon su FHA ed EsamiDiStato) sono accesi: incassi 0.
- Prodotti nostri: nessuno su questi siti. Il libro B1 è solo su EsameB1.
- Un dominio costa circa 10 € l'anno. Nessun sito su netlify.app arriva a 10 € l'anno di pubblicità (il migliore, Cruise: 124 visite al mese → 1.600 l'anno → 2,6-4,8 €). **Nessun dominio da comprare.**

## Tabella di tutti i siti

Visite = S1 · S2 · S3 · S4. Fonti = settimana S4. Attese = visite in più a settimana, prudente / centrale. € = l'anno, prudente / centrale, **se** AdSense fosse approvato.

| Sito (online dal) | Visite S1·S2·S3·S4 | 28 gg | Fonti S4 (Google / AI / altro) | Pagine che contano | Guadagno oggi | Azione migliore | Attese/sett. | €/anno | Ore | Verdetto |
|---|---|---|---|---|---|---|---|---|---|---|
| **Paga CCNL** pagaccnl.com (12/11) | 0·0·113·44 | 157 | 28 / 4 / 12 | multiservizi-pulizie 34→19, logistica 34→15, home 33→4; commercio 7→2, metalmeccanici 5→3 | 0. AdSense non chiesto (previsto 3/12) | 1) Controllo URL di 10 pagine in Search Console. 2) Poi 2 contratti nuovi (cooperative sociali, vigilanza) | 1) 0 / +50 · 2) +6 / +34 | 1) 0 / 7,8 · 2) 0,5 / 5,3 | 1) 0,5 + 15 min di Massimiliano · 2) 10 | **SPINGERE** (dopo il controllo) |
| **Italy Strikes** netlify.app (10/10) | 1·9·35·34 | 79 | 17 / 3 / 14 | aeroporti IT 11→3, aeroporti EN 4→6, guide 7→4, sciopero generale 1→4 | 0. AdSense non approvato. SafetyWing: 0 | 13 aeroporti mancanti (IT + EN, 26 pagine) | +6 / +17 | 0,5 / 2,7 | 5 | **SPINGERE** poco. Unione con BYF: **non ora** |
| **Tourist Tax** netlify.app (10/10) | 24·17·38·26 | 105 | 16 / 0 / 10 | USA 0→0→5→11 (Tampa 4, Key West 2), Giappone 0→0→4→7, Francia 7→11→8→1, Istanbul 7→1→6→0 | 0. AdSense non approvato. Nessun riquadro | Tariffe 2027 e sovrimposte Florida 2027 (lavoro dovuto entro l'1/1) | 0 / +8 | 0 / 1,2 | 4 | **MANTENERE** |
| **Cruise Health Scores** netlify.app (17/10) | 38·27·30·29 | 124 | 16 / 1 / 12 | navi 16→15→13→8, compagnie 10→8→7→10, home 2→2→7→4 | 0. AdSense non approvato. SafetyWing: 0 | Solo i dati CDC (2 volte al mese) | 0 | 0 | 0,5 al mese | **MANTENERE** |
| **Aste in Chiaro** netlify.app (15/10) | 34·20·28·17 | 99 | 1 / 12 / 4 | auto-all-asta 1→3→2→5, Roma 9→3→3→2 | 0. AdSense non approvato | Pagine «auto all'asta» per provincia | +3 / +6 | 0,2 / 0,9 | 6 | **MANTENERE**. Costruire solo se il 7/12 è ancora sopra 15/sett. |
| **Payroll Tax** payrolltaxbystate.com (12/11) | 0·0·44·14 | 58 | 6 / 0 / 8 | home 29→7, due-dates 3→7 | 0. AdSense non chiesto | Nessuna costruzione. Foto di Search Console | 0 | 0 | 0,3 | **MANTENERE** |
| **FloodCost** netlify.app (15/10) | 0·1·1·11 | 13 | 10 / 0 / 1 | 11 pagine diverse (CAP, contee Florida e Georgia), 1 visita ciascuna, tutte il 23-24/11 | 0 | Foto di Search Console al controllo dei 45 giorni (29/11) | 0 | 0 | 0,3 | **MANTENERE** |
| **ApprovedCondos** netlify.app (17/10) | 0·2·12·2 | 16 | 1 / 0 / 1 | solo la home (11 in S3, dirette) | 0 | Niente. Dati una volta al mese | 0 | 0 | 0,3 al mese | **MANTENERE**. Candidato a chiudere a 90 giorni (15/1) |
| **EsamiDiStato** netlify.app (10/10) | 0·4·1·3 | 8 | 1 / 0 / 2 | home, geometra 2 | 0 | **Chiudere il 1/12** | 0 | 0 | 0,5 | **CHIUDERE** |
| **Inflation** netlify.app (13/11) | 0·0·0·5 | 5 | 3 / 0 / 2 | 5 pagine, 1 visita ciascuna | 0 | Togliere la data dai titoli dei prezzi (così non scadono ogni settimana) | 0 | 0 | 0,5 | **MANTENERE** (prova fino al 10/12) |
| **Quiz Ufficiali** netlify.app (13/11) | 0·0·2·0 | 2 | – | patentino fitosanitario 2 | 0 | Niente | 0 | 0 | 0 | **MANTENERE** (prova) |
| **Codici ATECO** netlify.app (13/11) | 0·0·0·1 | 1 | – | home 1 | 0 | Niente | 0 | 0 | 0 | **MANTENERE** (prova) |
| **Farmaco Equivalente** netlify.app (13/11) | 0·0·0·0 | 0 | – | – | 0 | Passare da 2 pubblicazioni a settimana a 1 al mese | 0 | 0 | 0,3 | **MANTENERE** (prova) |
| **Heat Pump Grants UK** netlify.app (13/11) | 0·0·0·0 | 0 | – | – | 0 (riquadro spento) | Niente. Riscrivere ECO4 a fine dicembre (già previsto) | 0 | 0 | 0 | **MANTENERE** (prova) |
| **Statute Limits** netlify.app (13/11) | 0·0·0·0 | 0 | – | – | 0 (riquadro spento) | Niente | 0 | 0 | 0 | **MANTENERE** (prova) |
| **Military Pay** netlify.app (13/11) | 0·0·0·0 | 0 | – | – | 0 | Niente prima delle tabelle 2027 (22/12) | 0 | 0 | 0 | **MANTENERE** (prova) |
| **NAICS** netlify.app (13/11) | 0·0·0·0 | 0 | – | – | 0 (riquadro spento) | Niente | 0 | 0 | 0 | **MANTENERE** (prova) |
| **US Paycheck** netlify.app (14/11) | 0·0·0·0 | 0 | – | – | 0 (riquadro spento) | Niente | 0 | 0 | 0 | **MANTENERE** (prova) |
| **Real Estate Exam** netlify.app (14/11) | 0·0·0·0 | 0 | – | – | 0 | Niente | 0 | 0 | 0 | **MANTENERE** (prova) |
| **US College Aid** netlify.app (19/11) | –·–·–·0 | 0 | – | – | 0 | Niente. È la «prova delle 200 università» | 0 | 0 | 0 | **MANTENERE** (prova) |
| **Balcony Solar Europe** netlify.app (8/11) | 0·0·0·0 | 0 | – | – | 0. Revisione AdSense chiesta l'8/11: esito **manca** | Niente | 0 | 0 | 0 | **MANTENERE** (prova) |
| BandiChiari, orelab (cartelle con `sito/`) | – | – | – | – | – | Non sono online (non stanno in `salute.py` né in `indexnow.py`). Archiviati | – | – | – | Fuori dalla rete |

Somma dei 20 siti online: 97 · 80 · 304 · 186.
Valore massimo in pubblicità di tutto il gruppo oggi: 186 × 52 = 9.672 visite l'anno → **15 € prudente, 29 € centrale**. Con AdSense non approvato: 0.

## Sito per sito: i dati e i conti

### Paga CCNL — l'unico da spingere, ma prima un controllo

- Visite al giorno dal 12/11: 5, 6, 13, 9, 26, 32, 20, 18, 15, 5, 0, 1, 1, 6.
- Google: 66 in S3, 28 in S4. Negli ultimi 5 giorni il sito fa 13 visite in tutto.
- È un calo oltre il 30 %. La regola del 24/11 dice: si verifica lo stesso giorno con il Controllo URL.
- `STRATEGIA-RECUPERO.md` (azione 9) lo ha già notato: il sito è crollato senza nostre modifiche, come i tre domini nuovi 7-10 giorni dopo l'arrivo sul dominio. Lì è scritto «solo controlli» finché BYF e Visa non danno un risultato leggibile.
- **Azione 1 (0 crediti).** Massimiliano apre Search Console di pagaccnl.com. Controllo URL di queste 10 pagine: `/`, `/multiservizi-pulizie/`, `/logistica-trasporto-merci/livello-g1/`, `/multiservizi-pulizie/2-livello/`, `/logistica-trasporto-merci/5-livello/`, `/multiservizi-pulizie/1-livello/`, `/logistica-trasporto-merci/livello-i/`, `/logistica-trasporto-merci/livello-a3/`, `/multiservizi-pulizie/4-livello/`, `/logistica-trasporto-merci/6-livello/`. Poi la foto di Rendimento (28 giorni). Se meno di 8 su 10 sono indicizzate: richiesta di indicizzazione.
  - Conto: Google prima del crollo 66 a settimana. Oggi circa 14 (2 al giorno). Recupero centrale +50. Prudente 0 (non dipende da noi).
  - € l'anno: 50 × 0,16 = 7,8 centrale. 0 prudente.
- **Azione 2 (dopo il controllo, esce con la pubblicazione del 10/12).** Due contratti nuovi: cooperative sociali e vigilanza privata.
  - Dato: i contratti «di nicchia» portano le visite. Multiservizi 34 e 19, logistica 34 e 15. I due contratti grandi no: commercio 7 e 2, metalmeccanici 5 e 3, anche se hanno 22.200 e 33.100 ricerche al mese.
  - Le fonti ci sono già in `ccnl/NOTE.md`: cooperative sociali 6.600 ricerche al mese (decreto del Ministero n. 30/2024 + CNEL), vigilanza 1.000 (guardia giurata 2.900; decreto n. 50/2024).
  - Conto centrale: 2 contratti × 17 (media di 19 e 15, settimana S4) = +34. Prudente: 2 × 3 = +6 (se Google non torna).
  - € l'anno: 6 × 0,08 = 0,5 · 34 × 0,16 = 5,3. Ore: 10 (lettura ottica, doppia fonte, revisione).
- **AdSense: non chiederlo il 3/12.** Il promemoria dice «~480 visite al mese». Il dato vero è 157 in 14 giorni e 44 nell'ultima settimana (circa 190 al mese). La soglia è 300. Chiederlo ora, con Google che ha tolto le pagine, rischia un rifiuto «low value content» come per BYF. Si chiede quando il sito fa almeno 70 visite a settimana per due settimane.
- Perché conta: è il solo sito del gruppo con un dominio suo e una storia sopra la soglia AdSense (113 in una settimana). 113 + 34 = circa 150 a settimana: 7.800 visite l'anno, 12-23 € l'anno. È poco. Ma è il passo che sblocca il primo incasso di un sito italiano.

### Italy Strikes — cresce, non spostarlo adesso

- 1 → 9 → 35 → 34. Google 0 → 5 → 23 → 17. Il 23/10 aveva 0 pagine indicizzate: ora Google lo mostra.
- Le pagine per aeroporto portano 15 visite su 35 (S3) e 9 su 34 (S4). Sono 18 pagine (9 in italiano, 9 in inglese). Media: 12 visite ÷ 18 pagine = 0,67 a pagina a settimana.
- Mancano 13 aeroporti con voli di linea (Catania, Palermo, Bari, Torino, Verona, Cagliari, Ciampino, Treviso, Olbia, Lamezia, Brindisi, Genova, Trieste). È lo schema «una pagina per ogni voce di un elenco lungo».
- Conto centrale: 26 pagine × 0,67 = +17. Prudente: metà delle pagine a metà resa = +6. Ore: 5 (il generatore c'è già).
- € l'anno: 0,5 / 2,7 **solo con AdSense**. Oggi 0: il sito è su netlify.app.
- **Attenzione:** 0 visite il 23, 24 e 25/11. Da rivedere lunedì 30/11 con le visite al giorno. Se resta a 0, si applica la regola del calo.
- **Unione dentro Before You Fly: non proporla il 1/12.** Tre dati: (1) la regola chiede 90 giorni e nessuna crescita; il sito ha 52 giorni e cresce; (2) BYF è fermo fino al 9/12; (3) i cambi di indirizzo hanno appena tolto il 70 % delle visite da Google a tre siti. Si rivede a 90 giorni (8/1/2027), prima del picco di marzo.
- **Crediti:** il robot può pubblicare fino a 12 volte al mese (`decidi_deploy.py`, commit del 25/11). Sono 180 crediti al mese per 34 visite a settimana. Fino al 15/12: 1 pubblicazione programmata, più 1 solo per uno sciopero nazionale (taxi 15/12).

### Tourist Tax — fermo intorno a 26 a settimana

- 24 · 17 · 38 · 26. Google 14 · 4 · 30 · 16. Nessuna visita dagli assistenti.
- Cresce la sezione USA (Florida e Texas, 69 pagine): 0 → 0 → 5 → 11. Cresce il Giappone (49 luoghi, già tutti con pagina): 0 → 0 → 4 → 7. Cala la Francia: 7 → 11 → 8 → 1.
- Non manca niente accanto alle pagine che crescono: le pagine ci sono già. Manca solo l'aggiornamento.
- Azione: tariffe 2027 e sovrimposte Florida 2027 (il file DR-15DSS 2027 esce a fine novembre; 4 contee scadono il 31/12). È un lavoro dovuto: senza, dal 1° gennaio i dati sono sbagliati. In più le 11 fonti da leggere a mano (audit n. 12).
- Conto: nessun dato dell'anno scorso sulla domanda di gennaio. **Ipotesi**: +30 % sulle 26 visite = +8 centrale. Prudente 0.
- € l'anno: 0 / 1,2. Oggi 0.

### Cruise Health Scores — stabile, solo dati

- 38 · 27 · 30 · 29. Google 15 · 11 · 9 · 16. ChatGPT 8 · 5 · 3 · 1 (in calo).
- 50 pagine diverse viste in 4 settimane, quasi tutte 1-2 visite. Nessuna pagina cresce.
- Nessuna azione di costruzione ha un dato a favore. Si tiene la promessa dei dati (1° e 3° lunedì).
- È il sito più visto fra quelli su netlify.app: 124 al mese. Soglia per il dominio: 300.

### Aste in Chiaro — vive di ChatGPT, e cala

- 34 · 20 · 28 · 17. ChatGPT 20 · 17 · 19 · 12. Google: 1 visita in 4 settimane.
- L'unica pagina che cresce è `/auto-all-asta/`: 1 → 3 → 2 → 5.
- Azione possibile (da `ricerca-2026-11-25-asset.md`, n. 15): pagine «auto all'asta» per provincia. +3 / +6 visite a settimana. 6 ore. 0,2 / 0,9 € l'anno.
- Costa 6 ore per meno di 1 € l'anno. Si fa solo se il 7/12 il sito è ancora sopra 15 visite a settimana. Altrimenti resta fermo.
- A 90 giorni (13/1/2027) rischia la regola: 99 visite in 28 giorni, in calo.

### Payroll Tax (Australia)

- 44 · 14. In S3 36 visite erano dirette (lancio e prove): non sono domanda. Google: 4 e 6.
- `/due-dates/` sale da 3 a 7. Sono numeri troppo piccoli per costruire.
- Azione: foto di Search Console (Rendimento 28 giorni). Decisione il 10/12.

### FloodCost

- Primo segnale: 10 visite da Google il 23-24/11, su 11 pagine diverse (4 CAP, 5 contee, 2 aiuti per disastri). Prima: 2 visite in 3 settimane.
- 3.400 pagine online. Dati riscaricati il 25/11.
- Azione: foto di Search Console al controllo dei 45 giorni (29/11). Soglie già scritte: 300 impressioni al mese e 500 pagine indicizzate.

### ApprovedCondos

- 16 visite in 28 giorni, 11 delle quali sulla home in un solo periodo e dirette. Google: 3 in 4 settimane.
- Search Console al 31/10: 89 impressioni, posizione 77,8, in calo.
- Niente da costruire. Dati una volta al mese. Primo candidato a chiudere quando compie 90 giorni (15/1/2027).

### EsamiDiStato — chiudere il 1/12

- 8 visite in 28 giorni. 1 sola da Google.
- I dati sono del 9/10 e non si aggiornano (avviso di `salute.py` del 24/11). Dopo il 15/12 non resta nessuna data d'esame.
- Regola usata: «dati che non riusciamo a tenere aggiornati → si toglie subito, a qualsiasi età».
- Niente da spostare: nessuna pagina ha più di 2 visite in 4 settimane.
- Passi: sì di Massimiliano → lui cancella il progetto su Netlify → si toglie da `indexnow.py`, `salute.py` e dal cruscotto. Nessuna pubblicazione.

### I 12 siti con 0-5 visite a settimana

Inflation, Quiz, ATECO, Farmaci, Heat Pumps, Statute Limits, Military Pay, NAICS, Paycheck, Real Estate, College Aid, Balcony Solar.

- Online da 12 a 18 giorni. In tutto: 8 visite in 28 giorni.
- Nessun dato dice quali pagine crescono. Costruire adesso sarebbe a intuito.
- L'unico dato utile si prende senza crediti: **foto di Search Console** (Rendimento 28 giorni + Pagine) per ognuno. 30 minuti di Massimiliano, una volta sola, entro il 9/12. Serve per il verdetto del 10/12.
- Tre siti consumano crediti senza visite: Farmaci (2 letture a settimana), Inflation (prezzi ogni giovedì, con la data nel titolo), Heat Pumps (uscita DESNZ del 26/11). Vedi il piano dei crediti.

## La regola «togliere» applicata al 1/12

Regola (`ORGANIZZAZIONE.md` sez. 4): sito online da almeno 90 giorni, meno di 100 visite al mese e nessuna crescita negli ultimi 2 mesi. Oppure dati non aggiornabili: subito.

| Sito | Giorni online al 1/12 | Visite in 28 gg | Crescita | Esito il 1/12 | Prossima data |
|---|---|---|---|---|---|
| EsamiDiStato | 52 | 8 | no | **Chiudere** (dati non aggiornabili) | 1/12 |
| Italy Strikes | 52 | 79 | sì (1 → 34) | Resta. Niente unione ora | 8/1/2027 |
| Tourist Tax | 52 | 105 | ferma | Resta | 8/1/2027 |
| Aste in Chiaro | 47 | 99 | in calo | Resta | 13/1/2027 |
| FloodCost | 47 | 13 | primo segnale | Resta | 13/1/2027 |
| Cruise | 45 | 124 | ferma | Resta | 15/1/2027 |
| ApprovedCondos | 45 | 16 | no | Resta. Primo candidato | 15/1/2027 |
| Siti del 12-19/11 | 12-20 | 0-157 | – | Troppo presto | 10-17/2/2027 |

Candidati a unire dentro un sito forte, da decidere a gennaio con i dati di Search Console: Real Estate (13 pagine), Quiz (18), Balcony Solar (30). Oggi hanno 0 visite: non c'è niente da spostare.

## Piano dei crediti fino al 15/12

Restano circa 370 crediti. Una pubblicazione costa 15. Quindi circa 24 pubblicazioni.

**Il problema.** Le routine scritte in `ORGANIZZAZIONE.md` sez. 2.1 possono chiedere, dal 26/11 al 14/12:

| Routine | Pubblicazioni possibili | Visite a settimana del sito |
|---|---|---|
| Italy Strikes (una ogni 3 giorni) | 6 | 34 |
| Farmaci (lunedì e giovedì) | 6 | 0 |
| Inflation (ogni giovedì) | 3 | 5 |
| Giovedì 10/12: CCNL, ATECO, NAICS, Quiz, Payroll Tax | 5 | 44, 1, 0, 0, 14 |
| Lunedì 7/12: Aste, Cruise, FHA, FloodCost | 4 | 17, 29, 2, 11 |
| Heat Pumps (26/11) | 1 | 0 |
| Tourist Tax (fonti a mano prima del 10/12) | 1 | 26 |
| **Totale** | **26 = 390 crediti** | |

390 è più di 370. E mancano ancora EsameB1, Visa e BYF.

**Il piano: 9 pubblicazioni per questi siti (135 crediti).**

| Quando | Sito | Cosa esce insieme | Crediti |
|---|---|---|---|
| 26/11 | Heat Pumps | dati DESNZ. Solo se sono cambiati | 15 |
| entro il 4/12 | Italy Strikes | scioperi aggiornati + 13 aeroporti | 15 |
| 7/12 | Aste | pagine rigenerate (+ auto per provincia se costruite) | 15 |
| 7/12 | Cruise | dati CDC | 15 |
| 8-10/12 | Tourist Tax | Florida 2027, fonti a mano, cambi 2027 | 15 |
| 10/12 | Paga CCNL | dati del mese + 2 contratti nuovi (se il controllo dà il via) | 15 |
| 10/12 | Inflation | indici di novembre + titoli senza data | 15 |
| 10/12 | Farmaci | carenti e lista di trasparenza | 15 |
| 10/12 | Payroll Tax | solo se i dati sono cambiati | 15 |

- 0 pubblicazioni: ATECO, NAICS, Quiz, Statute Limits, Military Pay, Paycheck, Real Estate, College Aid, Balcony Solar, FHA, FloodCost (FHA e FloodCost sono usciti il 25/11 e promettono dati mensili), EsamiDiStato.
- Riserva per i tre siti esclusi: 8 pubblicazioni = 120 crediti (**ipotesi mia**: EsameB1 4, Visa 2, BYF 2).
- Totale 255. Margine 115 crediti (7 pubblicazioni) per errori e scioperi nazionali.
- Da cambiare perché il piano regga (non l'ho fatto: è solo ricerca): tetto di Italy Strikes in `decidi_deploy.py` da 12 a 2 fino al 15/12; Farmaci una lettura al mese finché ha 0 visite; Inflation una pubblicazione al mese con i titoli senza data.

## Lista delle azioni, in ordine di € per ora

Prima i passi che sbloccano un incasso o lo proteggono. Poi le costruzioni. € = l'anno, prudente / centrale.

| # | Azione | Dato | Visite/sett. in più | €/anno | Ore | €/ora (centr.) | Crediti | Quando |
|---|---|---|---|---|---|---|---|---|
| 1 | **Piano dei crediti**: da 26 a 9 pubblicazioni di routine | 390 crediti possibili contro 370; 13 di quelle pubblicazioni sono su siti con 0-5 visite a settimana | 0 | 4,6 subito (una ricarica da 5 $ evitata). Protegge EsameB1: riquadro del libro 60 / 215 (`ricerca-2026-11-25-asset.md`) | 1 | 4,6 (più la protezione) | −255 risparmiati | subito |
| 2 | **Paga CCNL: Controllo URL di 10 pagine** e foto del Rendimento | Google 66 → 28; visite al giorno 26, 32, 20 → 0, 1, 1 | 0 / +50 | 0 / 7,8 con AdSense. Oggi 0. **È il passo che sblocca AdSense** (soglia 70 a settimana) | 0,5 + 15 min di Massimiliano | 15 | 0 | subito |
| 3 | **Chiudere EsamiDiStato** | 8 visite in 28 giorni; dati del 9/10 | 0 | 0. Toglie un dato vecchio e circa 1 ora al mese | 0,5 | – | 0 | 1/12 |
| 4 | **Foto di Search Console dei 14 siti piccoli** (i 12 a 0-5 visite, Payroll Tax, FloodCost) | 14 siti con 0-14 visite a settimana: senza impressioni non si può decidere | 0 | 0. Serve ai verdetti del 10/12 | 1 + 30 min di Massimiliano | – | 0 | entro il 9/12 |
| 5 | **Italy Strikes: 13 aeroporti** (26 pagine) | aeroporti = 0,67 visite a pagina a settimana; sito 1 → 34 | +6 / +17 | 0,5 / 2,7 con AdSense. Oggi 0 | 5 | 0,5 | 15 | entro il 4/12 |
| 6 | **Paga CCNL: cooperative sociali e vigilanza** | multiservizi 19-34 e logistica 15-34 a settimana; commercio 2-7 | +6 / +34 | 0,5 / 5,3 con AdSense. Oggi 0. Porta il sito sopra la soglia AdSense se Google torna | 10 | 0,5 | 15 (con i dati del 10/12) | 10/12, solo dopo l'azione 2 |
| 7 | **Tourist Tax: tariffe e Florida 2027** | USA 0 → 11, Giappone 0 → 7; lavoro dovuto entro l'1/1 | 0 / +8 (**ipotesi**) | 0 / 1,2 con AdSense. Oggi 0 | 4 | 0,3 | 15 | 8-10/12 |
| 8 | **Aste: auto all'asta per provincia** | `/auto-all-asta/` 1 → 5; sito al 70 % da ChatGPT, in calo 20 → 12 | +3 / +6 | 0,2 / 0,9 con AdSense. Oggi 0 | 6 | 0,15 | 0 in più (esce il 7/12) | solo se il 7/12 il sito è sopra 15/sett. |
| – | Inflation: titoli senza data | il titolo scade ogni giovedì; 5 visite a settimana | 0 | 0. Risparmia 2 pubblicazioni al mese | 0,5 | – | −30 al mese | 10/12 |
| – | Costruire sui 12 siti a 0-5 visite | nessun dato | – | – | – | – | – | **no**, fino alle foto |
| – | Comprare domini | nessun sito su netlify.app supera 124 visite al mese (soglia 300) | – | – | – | – | – | **no** |
| – | Chiedere AdSense per pagaccnl.com il 3/12 | 190 visite al mese contro 300 | – | – | – | – | – | **rimandare** |

Somma delle costruzioni (5-8): **+15 prudente, +65 centrale** visite a settimana, 25 ore, 45 crediti.
In € l'anno: 1,2 prudente, 10 centrale, e solo dopo un'approvazione AdSense. **Oggi 0.**

## Detto chiaro

- Su questi 20 siti non esiste oggi un'azione che renda soldi. Le azioni 1-4 costano 3 ore e proteggono l'unico incasso possibile (il libro su EsameB1) e l'unico sito che può arrivare ad AdSense (Paga CCNL).
- Le azioni 5-8 portano visite, non soldi: meno di 1 € per ora. Hanno senso solo come passi verso le soglie (AdSense a 300 visite al mese, verdetti a 90 giorni).
- Le ore di costruzione rendono di più sui tre siti esclusi da questo piano: lì ci sono circa 907 visite a settimana su 1.093 e l'unico prodotto.

## Cosa resta incerto

1. Perché Paga CCNL è crollato il 21/11: lo dice solo il Controllo URL.
2. Italy Strikes a 0 visite dal 23 al 25/11: tre giorni sono pochi. Da rivedere il 30/11.
3. Impressioni e pagine indicizzate di 14 siti: mancano.
4. Lo stato in AdSense dei siti su netlify.app (Balcony Solar, revisione chiesta l'8/11): manca.
5. La domanda di gennaio per Tourist Tax: nessun dato dell'anno scorso.
6. Le provenienze di Italy Strikes: `toprefs` elenca 23 visite su 34 in S4. Le altre 11 sono contate come «altro».
7. Quanti crediti servono davvero a EsameB1, Visa e BYF: la riserva di 120 è una mia ipotesi.
