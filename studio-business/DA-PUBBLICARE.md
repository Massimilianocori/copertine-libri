# Da pubblicare nel push serale

Sezioni già revisionate, con i sorgenti salvati, che aspettano la pubblicazione serale unica (regola crediti Netlify del 31/10/2026: una pubblicazione per sito al giorno). Il punto 0 della routine serale le pubblica e poi cancella la riga.

**Nota per la routine serale del 6/11/2026:** un ricercatore è già partito alle 15; stasera **1 solo ricercatore**, con questo compito (decisione del 6/11, Massimiliano: "fare altro, non solo guardare quello che abbiamo fatto"): **sito NUOVO clone di EsameB1 per la Spagna: esame CCSE + DELE A2 per la nacionalidad española** (calendari e sedi dell'Instituto Cervantes per città, costi, esenzioni per Paese ibero-americano, tempi). EsameB1 è il sito che cresce di più (226 → 362 visite a settimana): stesso modello, mercato più grande. In ESPLORATE era RISERVA solo per la lingua spagnola: rivalutare con i numeri di oggi (autocomplete es/mx/co/ve/ar, fonti cervantes.es con curl, pagatori in spagnolo con cifra: italki, Amazon.es libri CCSE/DELE, AdSense ES, accademie), stima prudente/centrale/ottimista, voto. Se voto ≥ 7 e ≥ 5.000 €/anno centrali: verificatore indipendente subito e, se conferma, riga in cima alla coda di costruzione come SITO NUOVO (lo costruisce il turno delle 11:43 senza aspettare sì: regola del 6/11). File `idee-2026-11-06-spagna-ccse.md`. Le idee grandi (vendere i nostri dati, app per assistenti, siti da comprare, programmi da 50-150 € a cliente, mercati nuovi) vanno ai 3 ricercatori del mercoledì 11/11.

| Sito (cartella) | Sezione | Revisione | Note |
|---|---|---|---|

Pubblicato il 31/10/2026 alle 14:20 circa (ora di Roma): Visa Income, Before You Fly, EsameB1 (tutte le sezioni revisionate del giorno). Esperimento citazioni: conteggio dal 1/11/2026.

Pubblicato il 6/11/2026 alle 13:00 circa: Visa Income (infermieri, UK Ancestry, università, correzione creator), Tourist Tax (licenze Spagna), Before You Fly (Amazon UK/US nel bagaglio a mano, eSIM Roamable); IndexNow fatto. Nessun'altra pubblicazione di questi tre siti il 6/11.

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
| beforeyoufly | **Scioperi in Italia come sezione di Before You Fly** (`/italy-strikes/`): spostare Italy Strikes (0 pagine indicizzate su 119 dopo 4 settimane, 1 visita al mese) dentro BYF, con 301 dal vecchio sito; il robot degli scioperi resta uguale ma pubblica BYF. Domanda: "italy strike today", "italy strikes november 2026", "train strike italy today" (autocomplete gb/us 6/11). Stima 40 / 180 / 900 €/anno | 6 | dopo H-1B e Available in, prima di febbraio 2027 (picco di marzo) | decisione del 6/11, CRUSCOTTO |
| beforeyoufly | Auto a noleggio oltre confine e sul traghetto, coppia per coppia (DiscoverCars): prima verificare che le offerte mostrino le condizioni per l'estero, poi 3 pagine di prova (Croazia→Bosnia, Germania→Polonia, Sicilia in traghetto) | 6,5 (250 €/anno centrali) | coda bassa, dopo gli scioperi | fronti-2026-11-06-dal-pagatore.md |
| beforeyoufly | Ryder Cup 2027: alloggi per distanza da Adare Manor (CSV Fáilte Ireland) | 6 | entro gennaio 2027 | fronti-2026-11-04-grandi-eventi.md |
| beforeyoufly | Cina senza visto nel 2027 | 5,5 | il giorno dell'annuncio ufficiale (cs.mfa.gov.cn) | idee-2026-11-04-asia-pacifico.md |
| beforeyoufly | Los Angeles 2028 sede per sede | 6 | febbraio-aprile 2027 | fronti-2026-11-04-grandi-eventi.md |
