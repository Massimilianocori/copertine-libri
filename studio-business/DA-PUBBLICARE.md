# Da pubblicare nel push serale

Sezioni già revisionate, con i sorgenti salvati, che aspettano la pubblicazione serale unica (regola crediti Netlify del 31/10/2026: una pubblicazione per sito al giorno). Il punto 0 della routine serale le pubblica e poi cancella la riga.

**Nota per la routine serale del 6/11/2026:** i 2 ricercatori di stasera (Spagna CCSE/DELE e fronte mai toccato) sono già partiti alle 18; **stasera nessun ricercatore in più**: fai solo la PARTE A e, quando i due finiscono, i verificatori per le idee che passano l'asticella.

**6/11/2026 sera:** Massimiliano ha aggiunto ApprovedCondos su Awin (spazio promozionale) e su Amazon US, e ha chiesto l'iscrizione a **EcoFlow USA** su Awin. Quando arriva l'email di approvazione EcoFlow: accendere il riquadro `kit_solari` di `fhacondos/dati/affiliati.json` con il link awin1 (awinmid dalla pagina del programma, awinaffid 3145171).

| Sito (cartella) | Sezione | Revisione | Note |
|---|---|---|---|
| touristtax | Tassa sugli alberghi USA, prima parte: Florida (67 contee, DR-15TDT e DR-15DSS 2026) e Texas (6 % + er34-v24h), 69 pagine `usa/` | da revisionare | sorgenti nel commit del 7/11; NOTE.md 7/11; seconda parte (~15 città a mano, Canada) ancora da fare: idee-2026-11-05-usa-canada.md |

Pubblicato il 31/10/2026 alle 14:20 circa (ora di Roma): Visa Income, Before You Fly, EsameB1 (tutte le sezioni revisionate del giorno). Esperimento citazioni: conteggio dal 1/11/2026.

Pubblicato il 7/11/2026 alle 18:00 circa: Before You Fly (Available in: Google Wallet, Wise, Uber, Stripe, 131 pagine); IndexNow fatto.

Pubblicato il 7/11/2026 alle 16:00 circa: Visa Income (H-1B, 160 pagine) e ApprovedCondos (link Amazon US nella sezione solare); IndexNow fatto.

Pubblicato il 6/11/2026 alle 21:00 circa: ApprovedCondos (pannello solare da balcone, 17 pagine; riaperto dal congelamento per questa sezione); IndexNow fatto. Connecticut: fonte cga.ct.gov da rileggere (errore di certificato).

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
| beforeyoufly | **Scioperi in Italia come sezione di Before You Fly** (`/italy-strikes/`): spostare Italy Strikes (0 pagine indicizzate su 119 dopo 4 settimane, 1 visita al mese) dentro BYF, con 301 dal vecchio sito; il robot degli scioperi resta uguale ma pubblica BYF. Domanda: "italy strike today", "italy strikes november 2026", "train strike italy today" (autocomplete gb/us 6/11). Stima 40 / 180 / 900 €/anno | 6 | dopo H-1B e Available in, prima di febbraio 2027 (picco di marzo) | decisione del 6/11, CRUSCOTTO |
| beforeyoufly | Auto a noleggio oltre confine e sul traghetto, coppia per coppia (DiscoverCars): prima verificare che le offerte mostrino le condizioni per l'estero, poi 3 pagine di prova (Croazia→Bosnia, Germania→Polonia, Sicilia in traghetto) | 6,5 (250 €/anno centrali) | coda bassa, dopo gli scioperi | fronti-2026-11-06-dal-pagatore.md |
| visaincome | **Assicurazione sanitaria richiesta da ogni visto** (sezione) + **assicurazione Schengen HelloSafe Atlas sulle pagine rifiuti** (fino al 50 % del premio, cookie 90 giorni): costruire appena Massimiliano è iscritto ad Atlas e il pannello dice per quali Paesi di residenza vende; il riquadro Schengen sulle pagine dell'esperimento citazioni solo dopo il verdetto del 28/12 | 6-7 (1.500 + 600 €/anno centrali; ottimista 15.000 + 10.800) | dopo l'iscrizione ad Atlas | fronti-2026-11-07-alto-compenso.md |
| floodcost | **California: FAIR Plan e polizze casa non rinnovate, CAP per CAP** (PDF FAIR Plan del 20/10/2026: 1.686 CAP, polizze 2022-30/9/2026 e valore assicurato; Excel del Department of Insurance sui non rinnovi 2020-2023) nelle pagine CAP della California che FloodCost ha già; riapre FloodCost dal congelamento come ApprovedCondos con il solare | 7 (300 / 2.750 / 11.000 €/anno; 14-18 ore) | prossimo turno libero | fronti-2026-11-07-settori-nuovi.md |
| beforeyoufly | Ryder Cup 2027: alloggi per distanza da Adare Manor (CSV Fáilte Ireland) | 6 | entro gennaio 2027 | fronti-2026-11-04-grandi-eventi.md |
| beforeyoufly | Cina senza visto nel 2027 | 5,5 | il giorno dell'annuncio ufficiale (cs.mfa.gov.cn) | idee-2026-11-04-asia-pacifico.md |
| beforeyoufly | Los Angeles 2028 sede per sede | 6 | febbraio-aprile 2027 | fronti-2026-11-04-grandi-eventi.md |
