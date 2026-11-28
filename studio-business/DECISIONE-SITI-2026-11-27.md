# Decisione: siti da chiudere e siti da far funzionare — 27/11/2026

Massimiliano, 27/11: «abbiamo aperto molti siti e li devi controllare a uno a uno e li devi far funzionare tutti. quelli che non hanno mai funzionato si chiudono»; «dobbiamo crescere sempre»; «come funzionavano all'inizio possono ancora funzionare»; «ogni volta che prendi una decisione deve essere supportata da una ricerca e dalle conseguenze che porta».

## Dati (GoatCounter, pagine viste a settimana, vecchio e nuovo dominio sommati, settimane dal 12/10 al 22/11; data di nascita = primo commit del sito)

| Sito | Nato | Pagine | Settimane (dal 12/10) | Massimo | Gruppo |
|---|---|---|---|---|---|
| EsameB1 | ottobre | 226 | 10 114 342 475 635 397 | 635 | funziona, in calo: recupero |
| Visa Income | ottobre | 813 | 3 57 91 220 572 273 | 572 | funziona, in calo: recupero |
| Before You Fly | ottobre | 1.552 | 1 22 77 212 414 236 | 414 | funziona, in calo: recupero |
| Paga CCNL | 11/11 circa | 63 | 0 0 0 0 33 116 | 116 | funzionava, crollato dal 21/11: recupero |
| Tourist Tax | 10/10 | 381 | 0 10 29 27 41 | 41 | piccolo, in crescita: tenere e far crescere |
| Italy Strikes | 10/10 | 119 | 0 0 1 24 54 | 54 | a picchi (scioperi 4/12 e 14-17/12) |
| Cruise Scores | 17/10 | 289 | 19 17 45 19 40 | 45 | piccolo, stabile |
| Aste | 15/10 | 452 | 3 21 22 23 33 | 33 | piccolo, in crescita |
| Payroll Tax | 11/11 | 21 | 0 29 21 | 29 | piccolo |
| **EsamiDiStato** | 9/10 | 45 | 0 0 4 1 1 | 4 | **mai funzionato, 7 settimane** |
| **Flood Cost** | 15/10 | 3.398 | 0 0 0 2 0 | 2 | **mai funzionato, 6 settimane** |
| **FHA Condos** | 17/10 | 354 | 0 0 1 13 2 | 13 | **mai funzionato, 6 settimane** |
| Balcony Solar | 8/11 | 29 | 0 0 0 | 0 | zero, 3 settimane |
| Farmaci, Quiz, Heat Pump, ATECO | 12/11 | 17-812 | 0-2 | ≤ 2 | zero, 2 settimane |
| Statute Limits, Inflation, Military Pay, NAICS | 13/11 | 88-1.499 | 0 | 0 | zero, 2 settimane |
| US Paycheck, Real Estate | 14/11 | 12-34 | 0 | 0 | zero, 2 settimane |
| US College Aid | 19/11 | 221 | 0 | 0 | zero, 1 settimana |

## Ricerca e conseguenze

- Un sito nuovo su un sottodominio netlify.app senza link esterni di solito non riceve visite da Google per settimane: il primo segnale vero arriva dopo 4-8 settimane (esperienza della nostra rete: EsameB1, Visa, Before You Fly hanno avuto le prime visite tra la 2ª e la 4ª settimana, poi sono cresciuti). Per questo: chi ha superato 6 settimane con quasi zero non ha funzionato; chi ha 1-3 settimane non si può ancora giudicare.
- **Conseguenze di chiudere** i 3 siti oltre 6 settimane: nessuna perdita di visite (2-16 in tutto); si tolgono le loro routine dai controlli (meno lavoro e meno crediti); nessun effetto sui domini principali (sono indirizzi separati). Si perde il lavoro fatto: i dati restano nel repository e si possono riusare. La cancellazione del progetto su Netlify la fa Massimiliano; non si può annullare.
- **Conseguenze di chiudere ora** i 12 siti di 1-3 settimane: si perderebbe la possibilità di sapere se funzionano proprio quando il primo segnale può arrivare. Conseguenza di aspettare: nessun costo di soldi (sono su netlify.app, non pubblichiamo se non cambiano i dati).

## Decisione

1. **Chiudere subito**: EsamiDiStato (già deciso il 1/12), Flood Cost, FHA Condos. Da parte nostra: fuori da indexnow, salute e routine. Da parte di Massimiliano: cancellare i 3 progetti su Netlify.
2. **Verdetto il 10/12** (4 settimane) per i 12 siti nati dal 8/11 in poi, con la stessa regola: meno di 10 pagine viste nella settimana 3-9/12 → si chiudono. Promemoria già attivo il 10/12, esteso a tutti i 12.
3. **Far funzionare e crescere** i 9 siti con visite: recupero di EsameB1, Visa, Before You Fly e Paga CCNL (piani in BYF-PIANO-RILANCIO-2026-11-27.md e PIANO-VISITE-VISA-CCNL-2026-11-27.md), allarme visite giornaliero su tutti, crescita di Tourist Tax, Aste, Cruise, Italy Strikes (picchi di dicembre).


## Aggiornamento 28/11/2026 (dati GoatCounter)
FHA Condos 16 pagine viste negli ultimi 7 giorni (7 giorni prima: 2) e Flood Cost 12 (1): non sono più «mai funzionato». La chiusura di questi due è sospesa; si decide il 10/12 con la regola dei siti giovani (meno di 10 pagine viste nella settimana 3-9/12 → chiusura). Resta proposta la chiusura di EsamiDiStato (3 pagine viste in 7 giorni).

## Chiusura EsamiDiStato — 28/11/2026
Massimiliano, 28/11: «chiudi esamidistato». Tolto dai controlli di salute.py e da IndexNow (NON_ONLINE in strumenti/indexnow.py). Il progetto Netlify «esamidistato» lo cancella Massimiliano (passi dati in chat il 28/11). La cartella esamidistato/ resta nel repository come archivio.
Netlify: progetto cancellato da Massimiliano il 28/11/2026; esamidistato.netlify.app risponde 404 (controllato).
