# Da pubblicare nel push serale

Sezioni già revisionate, con i sorgenti salvati, che aspettano la pubblicazione serale unica (regola crediti Netlify del 31/10/2026: una pubblicazione per sito al giorno). Il punto 0 della routine serale le pubblica e poi cancella la riga.

| Sito (cartella) | Sezione | Revisione | Note |
|---|---|---|---|
| visaincome | Esperimento citazioni (36 pagine rifiuti trattate + 36 CSV; annotare la data di pubblicazione nel registro di `intelaiatura/esperimento-citazioni-2026-10-31.md`); Schengen dal Regno Unito e da Dubai (`/schengen-visa-from-uk/` + 25, `/schengen-visa-from-dubai/` + 24), revisione 31/10 pubblicabile; Tassa 7% (`/italy-7-percent-flat-tax/` + 1), revisione 31/10 pubblicabile; Study in Italy (`/study-in-italy/` + 14), revisione 31/10 pubblicabile; Residenza Messico (`/mexico-residency/` + 12), revisione 31/10/2026 pubblicabile; OPT USA (`/us-opt/` + 5) e UK Graduate visa (`/uk-graduate-visa/` + 3) | 31/10/2026, pubblicabile | Visa Income già pubblicato il 31/10 alle 00:30 circa (ora di Roma): pubblicare la sera del 31/10 |
| beforeyoufly | Riquadri Stay22 sulle 6 pagine `/ticket-release-dates/` (link di Massimiliano), controllati 31/10; Bagagli sui treni (`/train-luggage-rules/` + 14) e `/eurostar-check-in-times/`, revisione 31/10 pubblicabile; mezzi pubblici (`/public-transport-rules/` + 19), revisione 31/10 pubblicabile; patente straniera Canada/Australia/NZ (`/foreign-licence-canada-australia-nz/` + 14), revisione 31/10/2026 pubblicabile | Before You Fly pubblicato il 31/10 alle 00:30 circa con i biglietti: pubblicare la sera del 31/10 (NZ cambia dal 1/11) |
| esameb1 | Sezione inglese `/en/` (16 pagine), revisione 31/10 pubblicabile; Cittadinanza per prefettura (`/cittadinanza/` + 30) e `/reddito-minimo-cittadinanza/`, revisione 31/10 pubblicabile; Esempi (`/esempi/` + 5), `/esonero-test-italiano/`, redirect da `/esempi-esame-b1/` | 31/10/2026, pubblicabile | Dopo la pubblicazione IndexNow; lunedì rilanciare `python3 esameb1/raccolta/esempi.py` (78/79 per un errore di rete sulla pagina della Corte costituzionale) |
| beforeyoufly (prossimo giro) | Amsterdam: la pagina GVB ora si apre (multa 70 € + tariffa), da aggiungere ai mezzi pubblici | da fare | segnalato dal revisore del 31/10 |

## Ricontrolli con data (dalla seconda revisione esterna del 31/10/2026)

| Quando | Cosa |
|---|---|
| dopo il 2/11/2026 | Before You Fly, Budapest: le multe BKK nuove (30.000/15.000 HUF) sono in vigore? togliere "from 2 November" |
| dopo il 9/11/2026 | Visa Income, OPT: chiusi i commenti sulla proposta da $70.000; controllare Federal Register e la causa sulla regola dei 30 giorni |
| 30/11/2026 e 28/12/2026 | Visa Income, esperimento citazioni: `python3 visaincome/raccolta/esperimento_citazioni.py misura` (prima lettura e verdetto) |
| dopo il 30/11/2026 | Visa Income, Study in Italy: riscrivere le frasi sulla scadenza del visto del 30/11/2026 |
