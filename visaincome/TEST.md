# Visa Income Checker – controlli prima della pubblicazione

Data: 10 ottobre 2026. I controlli sono stati rifatti dopo le correzioni della revisione indipendente. Comandi (dalla radice del repository):

```
python3 visaincome/raccolta/cambi.py   # cambi BCE di riserva in dati/cambi.json
python3 visaincome/genera.py           # sito in visaincome/sito/
python3 visaincome/verifica.py         # i controlli qui sotto (esce con 1 se qualcosa non va)
```

## Risultato

| Controllo | Esito |
|---|---|
| Generatore | 37 pagine indicizzabili + 404, 17 programmi in 13 paesi, cambi BCE del 09/10/2026 |
| 1. Esempi calcolati a mano (sotto) | 32 importi su 32 e 15 confronti con il reddito su 15 giusti |
| 2. Motore JS (lo stesso delle pagine) contro Python | 0 differenze su 3.000 casi casuali (importi, conversioni, esiti, anche con valori fuori scala) + tutti gli esempi |
| 3. Link interni | 38 pagine, 0 link rotti (la 404 usa link assoluti) |
| 4. Fonte ufficiale (URL) e data del controllo sotto la cifra principale | 17 programmi su 17 |
| 5. Nomi di modelli o servizi di IA nei file del sito | nessuno |
| 6. Correzioni della revisione presenti nelle pagine | 23 controlli, 0 errori |
| Playwright, 375 px, tema chiaro e scuro | 6 pagine (home, Spagna nomadi, UK Skilled Worker, Austria Blue Card, soglie lavoro, Portogallo D8): nessuno scorrimento orizzontale, 0 errori in console; 9 prove del calcolatore riuscite |

Cambi dal vivo: le pagine chiedono `raw.githubusercontent.com/.../italystrikes/dati/cambi-bce.json` (verificato in Playwright). Nel test la risposta è servita dal file locale con una data successiva ("12 October 2026"): la pagina aggiorna la data e ricalcola. Senza risposta restano i cambi scritti alla generazione.

## Esempi calcolati a mano

Indici: SMI 2026 = 1.221 € × 14 mensilità = 17.094 €/anno; IPREM = 600 €; RMMG = 920 €; salario netto medio HR 2025 = 1.449 € (DZS); soglia esenzione ticket IT = 16.000.000 / 1.936,27 = 8.263,31 €/anno.
Cambi BCE del 9/10/2026 (1 € = …): USD 1,1206 · GBP 0,84763 · PHP 70,397 · INR 108,3965 · AUD 1,6052 · SEK 11,1675 · DKK 7,4751 · JPY 177,34.
Arrotondamento: al centesimo, mezzo in su (JPY all'unità). Conversioni: si converte l'importo del periodo della regola (mese o anno) e si ricava l'altro dal valore convertito, così mese e anno restano coerenti.

| # | Caso | Calcolo a mano | Atteso |
|---|---|---|---|
| 1 | Spagna nomadi, 1 adulto, per mensilità | 200% × 1.221 | 2.442,00 € (× 14) |
| 2 | Spagna nomadi, 1 adulto, all'anno | 2.442 × 14 | 34.188,00 € |
| 3 | Spagna nomadi, 1 adulto, su 12 mesi | 34.188 / 12 | 2.849,00 € |
| 4 | Spagna nomadi, coppia, su 12 mesi | (2.442 + 75% × 1.221 = 915,75) × 14 = 47.008,50 / 12 = 3.917,375 | 3.917,38 € |
| 5 | Spagna nomadi, coppia + 2 figli, per mensilità | 2.442 + 915,75 + 2 × 305,25 | 3.968,25 € |
| 6 | Spagna nomadi, coppia + 2 figli, all'anno | 3.968,25 × 14 | 55.555,50 € |
| 7 | Spagna non lucrativo, coppia + 2 figli | 400% × 600 + 3 × 100% × 600 | 4.200,00 € |
| 8 | Portogallo D8, 1 adulto | 4 × 920 | 3.680,00 € |
| 9 | Portogallo D8, coppia + 1 figlio | nessun importo ufficiale per i familiari | 3.680,00 € |
| 10 | Portogallo D7, coppia + 2 figli, all'anno | (920 + 460 + 2 × 276) × 12 | 23.184,00 € |
| 11 | Croazia nomadi, 2 adulti + 1 figlio | 2,5 × 1.449 + 2 × 10% × 1.449 | 3.912,30 € |
| 12 | Ungheria White Card, coppia | i familiari non contano | 3.000,00 € |
| 13 | Italia nomadi, al mese | 3 × 8.263,31 = 24.789,93 / 12 = 2.065,8275 | 2.065,83 € |
| 14 | Germania Blue Card ridotta, al mese | 45.934,20 / 12 | 3.827,85 € |
| 15 | Olanda kennismigrant 30+, all'anno | 5.942 × 12 | 71.304,00 € |
| 16 | UK Skilled Worker, dottorato non STEM | soglia minima | 37.500,00 £ |
| 17 | UK coniuge, proroga regole pre-2024, 3 figli | 18.600 + 3.800 + 2 × 2.400 | 27.200,00 £ |
| 18 | UK coniuge, proroga, 4 figli | 18.600 + 3.800 + 3 × 2.400 = 29.600 → tetto | 29.000,00 £ |
| 19 | Valori fuori scala: 0 adulti e −3 figli | diventano 1 e 0 | 2.442,00 € |
| 20 | Valori fuori scala: 50 adulti (Croazia) | diventano 20: 3.622,50 + 19 × 144,90 | 6.375,60 € |
| 21 | Spagna nomadi in dollari, per mensilità | 2.442 × 1,1206 = 2.736,5052 | 2.736,51 USD |
| 22 | Spagna nomadi in dollari, all'anno | 2.736,51 × 14 | 38.311,14 USD |
| 23 | Spagna nomadi in pesos filippini, su 12 mesi | 2.442 × 70,397 = 171.909,47; × 14 = 2.406.732,58; / 12 | 200.561,05 PHP |
| 24 | Spagna nomadi, famiglia di 4, in dollari, per mensilità | 3.968,25 × 1,1206 = 4.446,8209 | 4.446,82 USD |
| 25 | Portogallo D8 in rupie indiane | 3.680 × 108,3965 | 398.899,12 INR |
| 26 | Croazia nomadi in sterline, al mese | 3.622,50 × 0,84763 = 3.070,5397 | 3.070,54 GBP |
| 27 | Croazia nomadi in sterline, all'anno | 3.070,54 × 12 | 36.846,48 GBP |
| 28 | UK Skilled Worker da sterline a rupie | 41.700 / 0,84763 = 49.195,99 € × 108,3965 | 5.332.673,51 INR |
| 29 | Svezia Blue Card da corone a dollari | 53.625 / 11,1675 = 4.801,88 € × 1,1206 | 5.380,99 USD |
| 30 | Danimarca pay limit da corone a dollari | 552.000 / 7,4751 = 73.845,17 € × 1,1206 | 82.750,89 USD |
| 31 | Germania Blue Card in yen (senza decimali) | 50.700 × 177,34 | 8.991.138 JPY |
| 32 | Spagna non lucrativo, famiglia di 4, in dollari australiani | 4.200 × 1,6052 | 6.741,84 AUD |

### Confronti con il reddito (campo facoltativo del calcolatore)

Regole mensili confrontate mese per mese; soglie annuali confrontate con il totale annuo (reddito mensile × mensilità scelte: 12, 13 o 14); Spagna nomadi: servono sia l'importo mensile (2.442 €) sia il totale annuo (34.188 €); visti UK: nessun verdetto, solo le condizioni.

| # | Caso | Esito atteso |
|---|---|---|
| 1 | Austria Blue Card, 3.977 € × 14 = 55.678 € (= soglia) | sì |
| 2 | Austria Blue Card, 3.977 € × 12 = 47.724 € | no |
| 3 | Spagna nomadi, 2.442 € × 14 = 34.188 € | sì |
| 4 | Spagna nomadi, 2.849 € × 12 = 34.188 € | sì |
| 5 | Spagna nomadi, 2.500 € × 12 = 30.000 € (mese sì, anno no) | parziale ("chiedi al consolato") |
| 6 | Spagna nomadi, 2.400 € × 14 | no |
| 7 | Spagna nomadi, 2.736,51 USD × 14 (= 2.442,00 €) | sì |
| 8 | Ungheria, 2.600 € × 14 = 36.400 € (regola mensile: 2.600 < 3.000) | no |
| 9 | Ungheria, 3.000 € × 12 | sì |
| 10 | Germania Blue Card, 4.225 € × 12 = 50.700 € | sì |
| 11 | Germania Blue Card, 4.224 € × 12 | no |
| 12 | Italia nomadi, 2.100 € × 12 = 25.200 € ≥ 24.789,93 € | sì |
| 13 | UK Skilled Worker standard, 5.000 £ al mese | nessun verdetto (condizioni del going rate) |
| 14 | UK Skilled Worker ridotto, 2.800 £ al mese | nessun verdetto |
| 15 | UK coniuge, 3.000 £ al mese | nessun verdetto |

Controllo incrociato con i numeri ufficiali già pubblicati (al centesimo): Spagna 2.442 € / 915,75 € / 305,25 € (consolato di Hanoi) e 2.442 € × 14 (Buenos Aires); Croazia 3.622,50 € (MUP); Portogallo D8 4 × 920 = 3.680 € (MNE); Germania 4.225,00 € e 3.827,85 € al mese (Service Berlin); Italia "non meno di 24.789 €" (consolato di Boston).

## Prove del calcolatore in Playwright

- Spagna nomadi: 2.442 € × 14 → "at or above"; 2.500 € × 12 → "meets one form of the amount but not the other"; la cifra mostrata è "€2,442.00 a month × 14 = €34,188.00 a year (€2,849.00 a month over 12 payments)".
- Adulti = 0: nota "Adults set to 1" e il campo torna a 1.
- UK Skilled Worker (standard e ridotto) con 5.000 £: nessun "at or above", al suo posto le condizioni sul going rate.
- Austria: 3.977 € × 14 → "at or above"; compare la nota sulle 14 mensilità.
- Portogallo D8 con 2 adulti + 1 figlio: resta 3.680 € con "family members not counted" e la spiegazione.


## Sezione "Visa refusal rates" (15/10/2026)

| Controllo | Esito |
|---|---|
| `raccolta/rifiuti.py` | tassi ricalcolati = colonna ufficiale su tutte le righe 2024 e 2025; somme = fogli dei totali; UK = Vis_06 su 20 nazionalità |
| `verifica.py` punto 7 | 104 pagine: ogni tabella e ogni cifra principale con fonte ufficiale e data; cifre di panoramica, 5 Paesi, 5 Stati e 4 nazionalità UK ricalcolate da `dati/rifiuti.json`; link esterni della sezione 200/206 |
| Playwright 390 e 1280 px, chiaro e scuro | 104 pagine nuove + home, Spagna nomadi, Germania, How it works, About, Privacy: nessuno scorrimento orizzontale, 0 errori JS, ordinamento delle tabelle corretto |
| Controllo a campione sui file grezzi | 14 cifre su 14 uguali (vedi rapporto della sessione) |
