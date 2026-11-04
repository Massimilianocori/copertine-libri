# Da pubblicare nel push serale

Sezioni già revisionate, con i sorgenti salvati, che aspettano la pubblicazione serale unica (regola crediti Netlify del 31/10/2026: una pubblicazione per sito al giorno). Il punto 0 della routine serale le pubblica e poi cancella la riga.

| Sito (cartella) | Sezione | Revisione | Note |
|---|---|---|---|
| touristtax | Santiago de Compostela (`/santiago-de-compostela/`) e Napoli (`/naples/`), 9 correzioni del revisore applicate (commit 9ee192b) | 4/11/2026, pubblicabile | Tourist Tax già pubblicato il 4/11: pubblicare il 5/11 |
| visaincome | Visti lunghi es/pt per nazionalità (`/es/visados/`, `/pt/vistos/`, 40 pagine), 10 correzioni del revisore applicate (commit 3e8ae56; lo script richiede LibreOffice `soffice` per il .xls di Bogotá) | 4/11/2026, pubblicabile | Visa Income già pubblicato il 4/11: pubblicare il 5/11 |
| beforeyoufly (prossimo giro) | Amsterdam: la pagina GVB ora si apre (multa 70 € + tariffa), da aggiungere ai mezzi pubblici | da fare | segnalato dal revisore del 31/10 |

Pubblicato il 31/10/2026 alle 14:20 circa (ora di Roma): Visa Income, Before You Fly, EsameB1 (tutte le sezioni revisionate del giorno). Esperimento citazioni: conteggio dal 1/11/2026.

Pubblicato il 1/11/2026 alle 00:15 circa: Visa Income (cerimonie australiane, es/pt) e Before You Fly (animali, Croazia, India, biglietti Giappone/USA, scooter). Tourist Tax: Niseko 3% già online.

## Ricontrolli con data (dalla seconda revisione esterna del 31/10/2026)

| Quando | Cosa |
|---|---|
| dopo il 9/11/2026 | Visa Income, OPT: chiusi i commenti sulla proposta da $70.000; controllare Federal Register e la causa sulla regola dei 30 giorni |
| quando esce un atto nazionale sulla proroga al 4/3/2028 | EsameB1 /uk/ protezione temporanea: aggiungerlo a `esameb1/dati/lingue.json` e aggiornare la pagina |
| 15/12/2026 (45 giorni) | EsameB1 /en/, /uk/, /ro/: almeno 100 impressioni al mese per lingua in Search Console, altrimenti si congela |
| 30/11/2026 e 28/12/2026 | Visa Income, esperimento citazioni: `python3 visaincome/raccolta/esperimento_citazioni.py misura` (prima lettura e verdetto) |
| dopo il 30/11/2026 | Visa Income, Study in Italy: riscrivere le frasi sulla scadenza del visto del 30/11/2026 |

## Coda di costruzione (dalla ricerca del 4/11/2026)

| Sito | Sezione | Voto | Quando | Fonte (file di ricerca) |
|---|---|---|---|---|
| visaincome | Liste università per visti da laureati (HPI UK, TTPS Hong Kong, J-Find Giappone) | 6,5 | dopo i visti es/pt | idee-2026-11-04-asia-pacifico.md |
| touristtax | Licenza per affitti turistici in Spagna per Comune (prima leggere la sentenza 620/2026 sul BOE) | 6 | dopo Santiago | idee-2026-11-04-europa.md |
| touristtax | Versioni es/pt (con la francese già in coda) | 6,5 | dopo | idee-2026-11-04-america-latina.md |
| visaincome | Infermieri all'estero per Paese di formazione + pagina lista rossa OMS 2026 (prima dell'uscita della lista; costi NMC da ricontrollare) | 6,5-7 | dopo i visti es/pt | idee-2026-11-04-africa-medio-oriente.md |
| visaincome | UK Ancestry visa per nazionalità (dati già in casa) | 6 | piccola, 4-6 ore | idee-2026-11-04-africa-medio-oriente.md |
| visaincome | Pensione statale britannica congelata o no, Paese per Paese | 6,5 | con la sezione pensioni HMRC già in coda | idee-2026-11-04-africa-medio-oriente.md |
| visaincome | Israele nelle pagine moved-to (API data.gov.il) | 5,5 | coda bassa | idee-2026-11-04-africa-medio-oriente.md |
| beforeyoufly | **Available in: +8 servizi** con lista ufficiale dei Paesi (Google Wallet, PayPal, Revolut, Wise, Disney+, Netflix, Uber, Prime Video; solo quelli con lista ufficiale leggibile). Motivo: sezione passata da 0 a 49 visite in una settimana (Starlink in testa) | 7 | PRIMA in coda per Before You Fly, dopo Amsterdam/Blue Badge | GoatCounter 28/10-4/11 |
| beforeyoufly | Ryder Cup 2027: alloggi per distanza da Adare Manor (CSV Fáilte Ireland) | 6 | entro gennaio 2027 | fronti-2026-11-04-grandi-eventi.md |
| beforeyoufly | Blue Badge all'estero Paese per Paese | 5,5 | quando la cartella è libera | idee-2026-11-04-europa.md |
| beforeyoufly | Cina senza visto nel 2027 | 5,5 | il giorno dell'annuncio ufficiale (cs.mfa.gov.cn) | idee-2026-11-04-asia-pacifico.md |
| beforeyoufly | Los Angeles 2028 sede per sede | 6 | febbraio-aprile 2027 | fronti-2026-11-04-grandi-eventi.md |
