# Da pubblicare nel push serale

Sezioni già revisionate, con i sorgenti salvati, che aspettano la pubblicazione serale unica (regola crediti Netlify del 31/10/2026: una pubblicazione per sito al giorno). Il punto 0 della routine serale le pubblica e poi cancella la riga.

| Sito (cartella) | Sezione | Revisione | Note |
|---|---|---|---|
| beforeyoufly | Amazon acceso nel bagaglio a mano (ricerche per misura: 27 pagine amazon.co.uk, 8 amazon.com, 5 entrambi; tag UK beforeyoufly-21, US beforeyoufl08-20) ed eSIM Roamable (Awin) nel riquadro «Before you go», ora solo nelle 631 pagine passaporti ed EES/ETIAS (tolto da home e liquidi); vedi `beforeyoufly/NOTE.md`, sezione 6/11/2026 | 6/11/2026: revisore indipendente PUBBLICABILE (70 link controllati, Awin verificato, nessuna regressione); ritocco del testo dello strumento applicato | pubblicare il 6/11 sera |
| touristtax | Licenze per affitti turistici in Spagna (`/spain-holiday-let-licence/`, 27 pagine), 10 correzioni del revisore applicate (commit 9dc3a88) | 5/11/2026, pubblicabile | Tourist Tax già pubblicato il 5/11 (alle 2:30): pubblicare il 6/11 |
| visaincome | Infermieri all'estero (`/nurses-abroad/`, 17 pagine) e visto UK Ancestry (`/uk-ancestry-visa/`), 14 correzioni del revisore applicate (commit 536c2c7); **liste università per visti da laureati** (`/top-university-visas/`, 82 pagine: 39 pagine università, le altre 161 solo in tabella per il contenuto sottile), correzioni del revisore applicate (commit e1eb9ed) | 5/11/2026, pubblicabile | Visa Income già pubblicato il 5/11 (alle 2:30): pubblicare il 6/11 |

Pubblicato il 31/10/2026 alle 14:20 circa (ora di Roma): Visa Income, Before You Fly, EsameB1 (tutte le sezioni revisionate del giorno). Esperimento citazioni: conteggio dal 1/11/2026.

Pubblicato il 5/11/2026 alle 23:30 circa: EsameB1 (click day del decreto flussi) e Before You Fly (Blue Badge, Amsterdam, 37 aeroporti dei liquidi, riquadri DiscoverCars e Stay22); IndexNow fatto.

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
| touristtax | Versioni es/pt (con la francese già in coda) | 6,5 | dopo | idee-2026-11-04-america-latina.md |
| visaincome | Pensione statale britannica congelata o no, Paese per Paese | 6,5 | con la sezione pensioni HMRC già in coda | idee-2026-11-04-africa-medio-oriente.md |
| visaincome | Israele nelle pagine moved-to (API data.gov.il) | 5,5 | coda bassa | idee-2026-11-04-africa-medio-oriente.md |
| beforeyoufly | Liquidi, pagine a 2 litri (Fiumicino, Vienna, Bologna, Bergamo, Knock e altre UE): la FAQ sul 2026 cita Your Europe (100 ml) sotto una risposta "2 litres"; aggiungere la frase ponte come nella FAQ sulla busta | piccola | prossimo giro di Before You Fly | revisione del 5/11 |
| beforeyoufly | **Available in: +8 servizi** con lista ufficiale dei Paesi (Google Wallet, PayPal, Revolut, Wise, Disney+, Netflix, Uber, Prime Video; solo quelli con lista ufficiale leggibile). Motivo: sezione passata da 0 a 49 visite in una settimana (Starlink in testa) | 7 | PRIMA in coda per Before You Fly, dopo Amsterdam/Blue Badge | GoatCounter 28/10-4/11 |
| visaincome | **Livello salariale H-1B per occupazione e area con le probabilità della lotteria pesata** (`/h1b-wage-level/`, ~40 occupazioni × 60 aree + calcolatore; file ufficiale OFLC_Wages_2026-27.zip e Federal Register) | 7 | entro metà gennaio 2027 (registrazione di marzo) | idee-2026-11-05-usa-canada.md |
| touristtax | Tassa sugli alberghi USA/Canada: prima Florida (67 contee, dr15tdt.pdf) e Texas (data.texas.gov er34-v24h), poi ~15 città a mano | 6,5 | dopo le versioni es/pt/fr | idee-2026-11-05-usa-canada.md |
| beforeyoufly | Ryder Cup 2027: alloggi per distanza da Adare Manor (CSV Fáilte Ireland) | 6 | entro gennaio 2027 | fronti-2026-11-04-grandi-eventi.md |
| beforeyoufly | Cina senza visto nel 2027 | 5,5 | il giorno dell'annuncio ufficiale (cs.mfa.gov.cn) | idee-2026-11-04-asia-pacifico.md |
| beforeyoufly | Los Angeles 2028 sede per sede | 6 | febbraio-aprile 2027 | fronti-2026-11-04-grandi-eventi.md |
