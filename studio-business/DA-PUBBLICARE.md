# Da pubblicare nel push serale

Sezioni già revisionate, con i sorgenti salvati, che aspettano la pubblicazione serale unica (regola crediti Netlify del 31/10/2026: una pubblicazione per sito al giorno). Il punto 0 della routine serale le pubblica e poi cancella la riga.

| Sito (cartella) | Sezione | Revisione | Note |
|---|---|---|---|
| esameb1 | Decreto flussi 2027, date dei click day (`/decreto-flussi-click-day/`), 11 correzioni del revisore applicate (commit dcbe06f; anche il selettore di lingua corretto su tutte le pagine senza traduzione) | 4-5/11/2026, pubblicabile | EsameB1 non ancora pubblicato il 5/11: va nella pubblicazione serale del 5/11 |
| visaincome | Infermieri all'estero (`/nurses-abroad/`, 17 pagine) e visto UK Ancestry (`/uk-ancestry-visa/`), 14 correzioni del revisore applicate (commit 536c2c7); **liste università per visti da laureati** (`/top-university-visas/`, 82 pagine: 39 pagine università, le altre 161 solo in tabella per il contenuto sottile), correzioni del revisore applicate (commit e1eb9ed) | 5/11/2026, pubblicabile | Visa Income già pubblicato il 5/11 (alle 2:30): pubblicare il 6/11 |
| beforeyoufly | Blue Badge abroad (`/blue-badge-abroad/`, 25 pagine) e Amsterdam nei mezzi pubblici (commit dd0c8d1); **liquidi: 37 aeroporti nuovi** e riquadri DiscoverCars (52 pagine) e Stay22 (5), 8 correzioni del revisore applicate (commit 4f95272); dati dei passaporti australiani del 4/11 | 5/11/2026, tutto pubblicabile | Before You Fly non ancora pubblicato il 5/11: va nella pubblicazione serale del 5/11 |

Pubblicato il 31/10/2026 alle 14:20 circa (ora di Roma): Visa Income, Before You Fly, EsameB1 (tutte le sezioni revisionate del giorno). Esperimento citazioni: conteggio dal 1/11/2026.

Pubblicato il 5/11/2026 alle 2:30 circa: Visa Income (visti lunghi es/pt, 40 pagine) e Tourist Tax (Santiago de Compostela, Napoli).

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
| touristtax | Licenza per affitti turistici in Spagna per Comune (prima leggere la sentenza 620/2026 sul BOE) | 6 | dopo Santiago | idee-2026-11-04-europa.md |
| touristtax | Versioni es/pt (con la francese già in coda) | 6,5 | dopo | idee-2026-11-04-america-latina.md |
| visaincome | Pensione statale britannica congelata o no, Paese per Paese | 6,5 | con la sezione pensioni HMRC già in coda | idee-2026-11-04-africa-medio-oriente.md |
| visaincome | Israele nelle pagine moved-to (API data.gov.il) | 5,5 | coda bassa | idee-2026-11-04-africa-medio-oriente.md |
| beforeyoufly | **Riquadro eSIM acceso con Roamable** (Awin, approvato il 5/11; link https://www.awin1.com/cread.php?awinmid=118127&awinaffid=3145171 con `ued=` verso la pagina giusta, da verificare in un browser): il riquadro `esim` di affiliati.json è già pronto e spento; dominio awin1.com già in whitelist | 7 | dopo la pubblicazione serale del 5/11 (Before You Fly) | email Awin del 5/11 |
| beforeyoufly | Liquidi, pagine a 2 litri (Fiumicino, Vienna, Bologna, Bergamo, Knock e altre UE): la FAQ sul 2026 cita Your Europe (100 ml) sotto una risposta "2 litres"; aggiungere la frase ponte come nella FAQ sulla busta | piccola | prossimo giro di Before You Fly | revisione del 5/11 |
| beforeyoufly | **Available in: +8 servizi** con lista ufficiale dei Paesi (Google Wallet, PayPal, Revolut, Wise, Disney+, Netflix, Uber, Prime Video; solo quelli con lista ufficiale leggibile). Motivo: sezione passata da 0 a 49 visite in una settimana (Starlink in testa) | 7 | PRIMA in coda per Before You Fly, dopo Amsterdam/Blue Badge | GoatCounter 28/10-4/11 |
| beforeyoufly | Ryder Cup 2027: alloggi per distanza da Adare Manor (CSV Fáilte Ireland) | 6 | entro gennaio 2027 | fronti-2026-11-04-grandi-eventi.md |
| beforeyoufly | Cina senza visto nel 2027 | 5,5 | il giorno dell'annuncio ufficiale (cs.mfa.gov.cn) | idee-2026-11-04-asia-pacifico.md |
| beforeyoufly | Los Angeles 2028 sede per sede | 6 | febbraio-aprile 2027 | fronti-2026-11-04-grandi-eventi.md |
