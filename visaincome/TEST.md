# Visa Income Checker – controlli prima della pubblicazione

Data: 10 ottobre 2026. Comandi (dalla radice del repository):

```
python3 visaincome/raccolta/cambi.py   # cambi BCE in dati/cambi.json
python3 visaincome/genera.py           # sito in visaincome/sito/
python3 visaincome/verifica.py         # i controlli qui sotto (esce con 1 se qualcosa non va)
```

## Risultato

| Controllo | Esito |
|---|---|
| Generatore | 37 pagine indicizzabili + 404, 17 programmi in 13 paesi, cambi BCE del 09/10/2026 |
| 1. Esempi calcolati a mano (sotto) | 25 su 25 giusti |
| 2. Motore JS (lo stesso delle pagine) contro Python | 0 differenze su 3.000 casi casuali + i 25 esempi |
| 3. Link interni | 38 pagine, 0 link rotti |
| 4. Fonte ufficiale (URL) e data del controllo sotto la cifra principale | 17 programmi su 17 |
| 5. Nomi di modelli o servizi di IA nei file del sito | nessuno |
| Playwright, 375 px, tema chiaro e scuro | 5 pagine (home, Spagna nomadi, confronto nomadi, UK coniuge, soglie lavoro): nessuno scorrimento orizzontale, 0 errori in console |

Nel test Playwright l'indirizzo `raw.githubusercontent.com/.../visaincome/dati/cambi.json` è servito dal file locale (prima del push il file su GitHub non esiste ancora): la pagina lo legge, aggiorna la data dei cambi ("12 October 2026" nel test) e ricalcola. Senza il file la pagina resta sui cambi scritti al momento della generazione.

## Esempi calcolati a mano

Indici: SMI 2026 = 17.094 / 12 = 1.424,50 €; IPREM = 600 €; RMMG = 920 €; salario netto medio HR 2025 = 3.622,50 / 2,5 = 1.449 €; soglia esenzione ticket IT = 16.000.000 / 1.936,27 = 8.263,31 €/anno.
Cambi BCE del 9/10/2026 (1 € = …): USD 1,1206 · GBP 0,84763 · PHP 70,397 · INR 108,3965 · AUD 1,6052 · SEK 11,1675 · DKK 7,4751 · JPY 177,34.
Arrotondamento: al centesimo, mezzo in su (JPY all'unità).

| # | Caso | Calcolo a mano | Atteso |
|---|---|---|---|
| 1 | Spagna nomadi, 1 adulto, al mese | 2 × 1.424,50 | 2.849,00 € |
| 2 | Spagna nomadi, 1 adulto, all'anno | 2.849 × 12 | 34.188,00 € |
| 3 | Spagna nomadi, coppia | 2.849 + 75% × 1.424,50 (= 1.068,375 → 1.068,38) | 3.917,38 € |
| 4 | Spagna nomadi, coppia + 2 figli | 2.849 + 1.068,38 + 2 × 356,13 (25% × 1.424,50 = 356,125) | 4.629,64 € |
| 5 | Spagna non lucrativo, coppia + 2 figli | 400% × 600 + 3 × 100% × 600 | 4.200,00 € |
| 6 | Portogallo D8, 1 adulto | 4 × 920 | 3.680,00 € |
| 7 | Portogallo D8, coppia + 1 figlio | 3.680 + 50% × 920 + 30% × 920 | 4.416,00 € |
| 8 | Portogallo D7, coppia + 2 figli, all'anno | (920 + 460 + 2 × 276) × 12 | 23.184,00 € |
| 9 | Croazia nomadi, 2 adulti + 1 figlio | 2,5 × 1.449 + 2 × 10% × 1.449 | 3.912,30 € |
| 10 | Ungheria White Card, coppia | i familiari non contano (ricongiungimento escluso) | 3.000,00 € |
| 11 | Italia nomadi, al mese | 3 × 8.263,31 = 24.789,93 / 12 = 2.065,8275 | 2.065,83 € |
| 12 | Germania Blue Card ridotta, al mese | 45.934,20 / 12 | 3.827,85 € |
| 13 | Olanda kennismigrant 30+, all'anno | 5.942 × 12 | 71.304,00 € |
| 14 | UK coniuge, proroga regole pre-2024, 3 figli | 18.600 + 3.800 + 2 × 2.400 | 27.200,00 £ |
| 15 | UK coniuge, proroga, 4 figli | 18.600 + 3.800 + 3 × 2.400 = 29.600 → tetto | 29.000,00 £ |
| 16 | Spagna nomadi in dollari | 2.849 × 1,1206 = 3.192,5894 | 3.192,59 USD |
| 17 | Spagna nomadi in pesos filippini | 2.849 × 70,397 = 200.561,053 | 200.561,05 PHP |
| 18 | Spagna nomadi, famiglia di 4, in dollari | 4.629,64 × 1,1206 = 5.187,9746 | 5.187,97 USD |
| 19 | Portogallo D8 in rupie indiane | 3.680 × 108,3965 | 398.899,12 INR |
| 20 | Croazia nomadi in sterline | 3.622,50 × 0,84763 = 3.070,5397 | 3.070,54 GBP |
| 21 | UK Skilled Worker da sterline a rupie | 41.700 / 0,84763 = 49.195,99 € × 108,3965 | 5.332.673,51 INR |
| 22 | Svezia Blue Card da corone a dollari | 53.625 / 11,1675 = 4.801,88 € × 1,1206 | 5.380,99 USD |
| 23 | Danimarca pay limit da corone a dollari | 552.000 / 7,4751 = 73.845,17 € × 1,1206 | 82.750,89 USD |
| 24 | Germania Blue Card in yen (senza decimali) | 50.700 × 177,34 | 8.991.138 JPY |
| 25 | Spagna non lucrativo, famiglia di 4, in dollari australiani | 4.200 × 1,6052 | 6.741,84 AUD |

Controllo incrociato con i numeri ufficiali già pubblicati (3 su 3 al centesimo): Croazia 3.622,50 € (MUP), Portogallo D8 4 × 920 = 3.680 € (MNE), Germania 4.225,00 €/mese e 3.827,85 €/mese (Service Berlin).

## Controlli a vista (Playwright)

- Spagna nomadi, 2 adulti + 2 figli, valuta PHP, reddito 300.000 PHP: 4.629,64 €/mese, 55.555,68 €/anno, ≈ 325.912,77 PHP/mese; esito "below this minimum" (corretto: 300.000 < 325.912,77).
- Il calcolatore mostra sempre la regola, la fonte ufficiale con la data e la data dei cambi BCE.
