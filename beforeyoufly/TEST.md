# Before You Fly – controlli prima della pubblicazione

Data: 10 ottobre 2026 (rifatti dopo le correzioni della revisione indipendente). Comandi (dalla radice del repository):

```
python3 -I beforeyoufly/raccolta/passaporti.py     # 226 pagine FCDO -> dati/passaporti.json
python3 -I beforeyoufly/raccolta/eesetias.py       # frasi ufficiali EES/ETIAS -> dati/ees_etias.json
BYF_BROWSER=1 python3 -I beforeyoufly/raccolta/liquidi.py   # ricontrollo delle frasi citate per i liquidi
python3 beforeyoufly/genera.py                     # sito in beforeyoufly/sito/
python3 beforeyoufly/verifica.py                   # i controlli qui sotto (esce con 1 se qualcosa non va)
```

## Risultato

| Controllo | Esito |
|---|---|
| Raccolta passaporti | 226 pagine su 226 lette dalla GOV.UK Content API, 0 errori; 213 regole automatiche, 13 da leggere sulla frase ufficiale |
| Raccolta EES/ETIAS | 8/8 frasi della Commissione e 8/8 frasi GOV.UK trovate parola per parola |
| Ricontrollo liquidi (con browser) | 41 pagine (38 aeroporti, 2 nazionali, FAQ Finavia): tutte le frasi citate presenti. Porto è tornata vuota una volta (pagina JavaScript) ed è stata riletta: frasi presenti. Ora lo script riprova da solo |
| Correzioni della revisione indipendente | tutte (vedi NOTE.md, ultima sezione) |
| Generatore | 272 pagine indicizzabili + 404: 225 paesi, 38 aeroporti, 2 regole nazionali, EES/ETIAS, indici e pagine di servizio |
| 1. Casi del passaporto calcolati a mano (sotto) | 33 su 33 (esito e data minima); nessun esito verde con passaporto che scade prima della partenza |
| 2. Motore JS (lo stesso delle pagine) contro Python | 0 differenze su 3.000 casi casuali (date anche impossibili come partenza prima dell'arrivo) + i 33 casi |
| 3. Link interni | 273 pagine, 0 link rotti (la 404 usa link assoluti) |
| 4. Fonti, date e citazioni | 225 pagine paese: link GOV.UK, data di aggiornamento della pagina FCDO, data del controllo, testo ufficiale completo, attribuzione OGL. 40 pagine liquidi: URL ufficiale, data del controllo, tutte le frasi citate (e la seconda fonte per FRA/MUC). EES/ETIAS: frasi, URL e date |
| 5. Struttura e contenuti | nessuna promessa di ricontrollo periodico nelle pagine; le 12 pagine senza controllo non lo promettono; Irlanda con la spiegazione FCDO; Gibilterra fuori dal gruppo Schengen;  meta Google in tutte le pagine, canonical in tutte tranne la 404 (noindex, link assoluti), sitemap = pagine indicizzabili, robots con sitemap, netlify.toml con `ignore`, nessuno script esterno |
| 6. Nomi di modelli o servizi di IA | nessuno (sito, dati, raccolta, note) |
| 7. Playwright, 375 px, tema chiaro e scuro | home, `passport-validity/spain/`, `liquids/`: nessuno scorrimento orizzontale, 0 errori in console; 7 prove riuscite: Spagna "no" con 1 giorno in meno e "sì" con 0 giorni di margine, etichette e nota Schengen, Colombia "no automatic check", Irlanda con il testo ufficiale intero (nessun taglio), Thailandia con passaporto che scade prima della partenza (riquadro rosso, nessun verde), Belize con l'avviso delle compagnie aeree nel risultato |

Le frasi dei liquidi sono state confrontate anche con le copie scaricate delle pagine (script di lavoro): 0 frasi mancanti.

## Casi del passaporto calcolati a mano

Regola applicata alla lettera. Mesi: stesso giorno N mesi dopo, ridotto all'ultimo giorno del mese se non esiste. "More than" = almeno un giorno dopo. "Duration of stay" = scadenza il giorno della partenza o dopo. "Less than 10 years before the date you arrive" = emissione dal giorno dopo la stessa data di 10 anni prima.

| # | Destinazione (regola FCDO) | Date (emissione / scadenza / arrivo / partenza) | Calcolo a mano | Atteso |
|---|---|---|---|---|
| 1 | Spagna (Schengen: emesso < 10 anni prima dell'arrivo; scadenza ≥ 3 mesi dopo l'uscita) | 1/3/2017 · 1/6/2027 · 1/11/2026 · 10/11/2026 | scadenza minima 10/2/2027; emissione minima 2/11/2016 | sì |
| 2 | Spagna | 1/11/2016 · 1/6/2027 · 1/11/2026 · 10/11/2026 | emesso esattamente 10 anni prima: non "less than" | **no** |
| 3 | Spagna | 2/11/2016 · … | emissione = minima | sì |
| 4 | Spagna | 1/1/2020 · 10/2/2027 · 1/11/2026 · 10/11/2026 | scadenza = minima (0 giorni di margine, avviso "Only just") | sì |
| 5 | Spagna | 1/1/2020 · 9/2/2027 · … | un giorno prima della minima | **no** |
| 6 | Thailandia (≥ 6 mesi dall'arrivo) | – · 28/2/2027 · 31/8/2026 · 14/9/2026 | 31/8 + 6 mesi = 28/2/2027 (fine mese) | sì |
| 7 | Thailandia | – · 28/2/2028 · 31/8/2027 · 14/9/2027 | 31/8/2027 + 6 mesi = 29/2/2028 (bisestile) | **no** |
| 8 | Belize (più di 3 mesi dall'arrivo) | – · 1/3/2027 · 1/12/2026 · 10/12/2026 | 1/12 + 3 mesi = 1/3; "more than" → minima 2/3/2027 | **no** |
| 9 | Belize | – · 2/3/2027 · … | = minima | sì |
| 10 | USA (durata del soggiorno) | – · 20/12/2026 · 1/12/2026 · 20/12/2026 | scade il giorno della partenza | sì |
| 11 | USA | – · 19/12/2026 · 1/12/2026 · 20/12/2026 | scade il giorno prima (anche avviso "scade prima della partenza") | **no** |
| 12 | Cile (scadenza dopo il giorno di uscita) | – · 20/12/2026 · 1/12/2026 · 20/12/2026 | minima 21/12/2026 | **no** |
| 13 | Costa Rica (≥ 1 giorno dopo l'uscita) | – · 21/12/2026 · 1/12/2026 · 20/12/2026 | minima 21/12/2026 | sì |
| 14 | Turchia (≥ 150 giorni dall'arrivo) | – · 9/3/2027 · 10/10/2026 · 20/10/2026 | 21 (ott) + 30 + 31 + 31 + 28 + 9 = 150 → 9/3/2027 | sì |
| 15 | Turchia | – · 8/3/2027 · … | un giorno prima | **no** |
| 16 | Cuba (≥ 6 mesi dall'arrivo e 3 mesi dopo la partenza) | – · 1/6/2027 · 1/11/2026 · 15/3/2027 | minime 1/5/2027 e 15/6/2027: la seconda non è rispettata | **no** |
| 17 | Cuba | – · 15/6/2027 · … | entrambe rispettate | sì |
| 18 | Hong Kong (≥ 1 mese dopo l'uscita) | – · 28/2/2027 · 20/1/2027 · 31/1/2027 | 31/1 + 1 mese = 28/2/2027 | sì |
| 19 | Israele (≥ 90 giorni dall'arrivo) | – · 1/3/2027 · 1/12/2026 · 8/12/2026 | 30 + 31 + 28 + 1 = 90 → 1/3/2027 | sì |
| 20 | Bosnia (emesso < 10 anni; ≥ 90 giorni dopo l'uscita) | 5/5/2019 · 18/1/2027 · 13/10/2026 · 20/10/2026 | 11 + 30 + 31 + 18 = 90 → 18/1/2027; emissione minima 14/10/2016 | sì |
| 21 | Gibilterra (emesso negli ultimi 10 anni; ≥ 3 mesi dopo l'uscita) | 28/2/2018 · 1/1/2029 · 29/2/2028 · 5/3/2028 | 29/2/2028 − 10 anni = 28/2/2018 (non esiste il 29) → minima 1/3/2018 | **no** |
| 22 | Gibilterra | 1/3/2018 · … | = minima; scadenza minima 5/6/2028 | sì |
| 23 | Maldive (≥ 1 mese dall'arrivo) | – · 5/12/2026 · 1/11/2026 · 15/12/2026 | minima 1/12/2026 rispettata, ma il passaporto scade prima della partenza: riquadro rosso | **no** |
| 24 | Colombia (frase con "However … recommend") | qualsiasi | nessun calcolo, si mostra la frase | da leggere |
| 25 | Spagna senza data di emissione | – · 1/1/2030 · 1/11/2026 · 10/11/2026 | serve la data di emissione | errore "issue" |
| 26 | Thailandia, partenza prima dell'arrivo | – · 1/1/2030 · 10/11/2026 · 1/11/2026 | date impossibili | errore "order" |
| 27 | Singapore (6 mesi dall'arrivo) | – · 30/9/2026 · 31/3/2026 · 5/4/2026 | 31/3 + 6 mesi = 30/9/2026 | sì |
| 28 | Thailandia (6 mesi dall'arrivo), soggiorno lungo | – · 10/4/2027 · 10/10/2026 · 1/5/2027 | minima 10/4/2027 rispettata, ma scade prima della partenza | **no** (rosso) |
| 29 | Thailandia | – · 1/5/2027 · 10/10/2026 · 1/5/2027 | scade il giorno della partenza: non prima | sì |
| 30 | Turchia (150 giorni dall'arrivo) | – · 20/3/2027 · 10/10/2026 · 1/4/2027 | minima 9/3/2027 rispettata, scade prima della partenza | **no** (rosso) |
| 31 | Israele (90 giorni dall'arrivo) | – · 5/3/2027 · 1/12/2026 · 10/3/2027 | minima 1/3/2027 rispettata, scade prima della partenza | **no** (rosso) |
| 32 | Kazakistan (30 giorni dall'arrivo) | – · 10/12/2026 · 1/11/2026 · 20/12/2026 | minima 1/12/2026 rispettata, scade prima della partenza | **no** (rosso) |
| 33 | Kazakistan | – · 21/12/2026 · 1/11/2026 · 20/12/2026 | scade dopo la partenza | sì |

## Da verificare a mano (Massimiliano o routine)

- Aprire 5 pagine paese a caso e confrontare il testo con la pagina GOV.UK "Entry requirements".
- Aprire le pagine di Francoforte e Monaco: le due frasi in contrasto sono ancora entrambe sul sito ufficiale?
- Aena (Spagna): se un aeroporto spagnolo pubblica una sua pagina con 2 litri, passa da "100 ml" a quella pagina.
- Dopo la pubblicazione: la 404 di Netlify, il modulo contatti (una prova) e Search Console.
