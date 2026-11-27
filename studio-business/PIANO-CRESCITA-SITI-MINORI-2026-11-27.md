# Piano di crescita dei 5 siti minori — 27/11/2026

Solo analisi e piano. Nessun sito toccato. Nessun commit.
Siti: Tourist Tax, Cruise Health Scores, Aste in Chiaro, Payroll Tax by State, Italy Strikes.
Regola del titolare: «dobbiamo crescere sempre»; ogni decisione con una ricerca e con le conseguenze.

## 0. In breve

1. **Da fare per primo: Italy Strikes, pagine per azienda in italiano** (ATM, Trenord, GTT, ATAC, Trenitalia e altre 11). Domanda misurata: circa 270.000 ricerche al mese. Oggi il sito non ha nessuna pagina per azienda. 7 ore. Online entro il 2/12, prima dello sciopero del 4/12.
2. **Tourist Tax: pacchetto Canarie** (Tenerife, Gran Canaria, Fuerteventura, Lanzarote). 8.180 ricerche al mese nel Regno Unito, nessuna pagina nostra. 5 ore. Solo dopo aver letto una fonte ufficiale.
3. **Cruise: sezione epidemie per compagnia e per anno.** 9.000 ricerche al mese negli USA; i dati sono già nel sito (65 epidemie CDC). 6 ore. Online entro il 7/12: la stagione del norovirus e la «wave season» partono a gennaio.
4. **Aste: una sola costruzione piccola** (veicoli per tipo e provincia). Google non manda visite: prima serve la foto di Search Console.
5. **Payroll Tax: solo manutenzione fino al 10/12.** Il sito è australiano: il cambio fiscale USA del 1/1/2027 non lo riguarda.
6. **Soldi, detto chiaro:** su questi 5 siti il codice AdSense è acceso ma **nessuno è approvato**. Oggi incassano 0. Le costruzioni servono a portare i siti sopra 300 visite al mese: è la soglia nostra per chiedere dominio e AdSense.

## 1. Come ho misurato

- **Visite:** API pubblica GoatCounter `rete-siti`, dal 15/10 al 26/11/2026. `stats/hits` con paginazione `exclude_paths` (id separati da virgola): 1.429 pagine lette, 5.520 visite in tutta la rete. Provenienze pagina per pagina con `stats/hits/{id}`.
- I numeri qui sotto sono **visite** (un visitatore per pagina). I numeri di `DECISIONE-SITI-2026-11-27.md` sono pagine viste, con settimane diverse: per questo non coincidono al numero.
- **Domanda:** `api.seodata.dev /v1/keyword`, 27/11/2026, 290 ricerche misurate (Italia, USA, Regno Unito, Australia). Volume = ricerche al mese. La chiave non è scritta da nessuna parte.
- **Già esplorato:** `intelaiatura/ESPLORATE.md` (1.582 righe), `ricerca-2026-11-27-idee-nuove.md`, `piano-crescita-2026-11-26.md`. Dove un'idea era già stata bocciata lo scrivo.
- **Limite:** Search Console non si legge da qui. Impressioni e pagine indicizzate **mancano**.

### Quanto rende una pagina nuova (conto usato in tutto il file)

Ho confrontato le visite vere delle nostre pagine con il volume della loro ricerca.

| Pagina nostra | Visite al mese | Volume della ricerca | Resa |
|---|---|---|---|
| Tourist Tax `/istanbul/` | 14 | 560 (Regno Unito) | 2,5 % |
| Tourist Tax `/france/` | 9 | 480 | 1,9 % |
| Cruise, home | 14 | 1.200 («cdc cruise ship scores» e simili) | 1,2 % |
| Italy Strikes `/it/aeroporti/roma-fiumicino/` | 8 | 90 | 9 % |
| Aste `/roma/` da Google | 0 | 4.400 | 0 % |

- Regola: **prudente 1 %, centrale 3 %** del volume diventa visite al mese. Per le ricerche dove i giornali sono primi (scioperi delle grandi aziende): prudente 0,05 %, centrale 0,2 %.
- Sono **ipotesi** costruite su pochi numeri. Si ricontrollano 4 settimane dopo ogni pubblicazione.
- Valore: 1,6-3,0 € ogni 1.000 visite, **solo con AdSense approvato** (conto di `piano-crescita-2026-11-26.md`).

### Monetizzazione oggi (da `strumenti/monetizzazione.json`)

| Sito | Codice AdSense | Approvato | Affiliazioni attive | Affiliazioni pronte ma spente |
|---|---|---|---|---|
| Italy Strikes | acceso | no (netlify.app) | SafetyWing; Italo su Awin (2 pagine) | Stay22, DiscoverCars: dominio ammesso, nessun link |
| Tourist Tax | acceso | no (netlify.app) | nessuna | Stay22, DiscoverCars, Viator: dominio ammesso, nessun link |
| Cruise | acceso | no (netlify.app) | SafetyWing (258 pagine) | CruiseDirect su CJ e Viator: dominio ammesso, nessun link |
| Aste | acceso | no (netlify.app) | nessuna | riquadro mutuo vuoto |
| Payroll Tax | acceso | non chiesto (dominio proprio) | nessuna | Employment Hero, MYOB: riquadri pronti, regola «domanda a 1.000 visite al mese» |

Incassi da questi 5 siti finora: 0. Affiliazioni nuove: ferme per decisione del 19/11. Non propongo di cambiarla ora.

### Vincolo dei crediti Netlify

Circa 200 crediti fino al 15/12, 15 per pubblicazione. Il piano non chiede pubblicazioni in più: ogni costruzione esce con la pubblicazione già prevista (Italy Strikes 2/12; Aste e Cruise 7/12; Tourist Tax 8-10/12).

---

## 2. Italy Strikes — il sito con più spazio per crescere

### Cosa funziona

- Visite a settimana dal 29/10: 1 · 9 · 35 · 34. Totale 79. Google 45, ChatGPT 10, dirette 8.
- Il picco è stato il 19/11 (23 visite), **il giorno prima** dello sciopero generale del 20/11.
- Dal 23 al 26/11: 0 visite. Senza scioperi vicini il sito è vuoto. È un sito a picchi.
- Pagine migliori: guida voli e scioperi 6 (Google) · Fiumicino in italiano 6 (Google) · Firenze aeroporto 5 (tutte ChatGPT) · scioperi generali 5 · Bologna aeroporto in italiano 5 (Google).
- Lezione: **Google ci mostra sulle ricerche precise** (un aeroporto, una guida). Le pagine in italiano rendono più di quelle in inglese.

### Domanda misurata

| Ricerca (Italia) | Al mese | Pagina nostra |
|---|---|---|
| sciopero trenitalia | 110.000 | no |
| sciopero atm (Milano) | 49.500 | no |
| sciopero trenord | 33.100 | no |
| sciopero gtt (Torino) | 27.100 | no |
| sciopero atac (Roma) | 12.100 | no |
| sciopero actv (Venezia) | 6.600 | no |
| sciopero italo | 6.600 | no |
| sciopero tper (Bologna) | 5.400 | no |
| sciopero amt genova · cotral | 4.400 · 4.400 | no |
| sciopero anm · eav (Napoli) | 2.900 · 2.900 | no |
| sciopero ryanair · easyjet | 1.900 · 1.300 | no |
| autolinee toscane · amat palermo · amtab | 1.000 · 720 · 480 | no |
| sciopero venerdì · sciopero 15 dicembre · sciopero aerei 15 dicembre | 9.900 · 390 · 590 | no (solo pagine del mese) |
| sciopero mezzi roma · sciopero mezzi milano | 60.500 · 27.100 | sì (pagine città) |
| treni garantiti in caso di sciopero | 6.600 | sì (guida) |

In inglese: «italy train strike» 2.900 USA + 1.300 Regno Unito; «italy airport strike» 1.900 + 2.400. Le pagine `/trains/` e `/airports/` ci sono già.

### Costruzioni, in ordine di visite per ora

**1. Pagine per azienda in `/it/` (16 pagine). DA FARE PER PRIMO.**
- Cosa: una pagina per azienda («Sciopero ATM Milano: prossime date e fasce garantite»). In cima il prossimo sciopero o la frase «nessuno sciopero in programma». Sotto: fasce di garanzia, storico degli scioperi dell'azienda dal registro, link alla fonte.
- Perché si può fare in fretta: `dati/operatori.json` riconosce già 51 aziende. Lo storico dal 2014 è già nei dati.
- Ore: 7. Attese: **+20 prudente / +80 centrale** visite a settimana nelle settimane con scioperi. Circa 11 visite per ora (centrale).
- Rischio: i giornali sono primi su queste ricerche. Per questo uso la resa bassa (0,05-0,2 %). La pagina senza scioperi in programma deve dire comunque qualcosa di utile (storico, fasce), altrimenti è una pagina vuota.
- Rischio 2: nomi delle aziende scritti in modi diversi nel registro. Serve un controllo a mano su 16 aziende.

**2. Pagine per data dei grandi scioperi (automatiche).**
- Cosa: per ogni sciopero nazionale in programma, una pagina `/it/sciopero-15-dicembre-2026/` con chi sciopera, orari, treni e voli garantiti. Nasce e si archivia da sola.
- Domanda: «sciopero 15 dicembre» 390 + «sciopero aerei 15 dicembre» 590 + «sciopero venerdì» 9.900. Le ricerche con la data nascono pochi giorni prima: il volume storico le sottostima.
- Ore: 3. Attese: +5 / +20 a settimana. Circa 7 visite per ora.
- Rischio: pagine che scadono. Vanno tenute online dopo lo sciopero con la scritta «concluso».

**3. I 13 aeroporti mancanti (26 pagine, italiano e inglese).**
- Già nel piano del 26/11: Catania, Palermo, Bari, Torino, Verona, Cagliari, Ciampino, Treviso, Olbia, Lamezia, Brindisi, Genova, Trieste.
- Ore: 5. Attese: +6 / +17 a settimana. Circa 3 visite per ora.

### Tempi

- 4/12 sciopero generale; 14-17/12 altri scioperi (15/12 taxi nazionale). A gennaio: 15/1/2027 ENAV e Techno Sky.
- Le pagine azienda e data devono uscire con la pubblicazione forzata del **2/12**. Dopo il 17/12 la domanda cala fino a metà gennaio.

### Conseguenze

- **Se si fa:** con la stima centrale il sito passa da 34 a circa 115 visite a settimana nelle settimane di sciopero, cioè sopra 300 al mese. È la soglia per chiedere dominio e AdSense. Con AdSense: 10-18 € l'anno. Pochi soldi, ma è il primo sito italiano del gruppo che ci arriva.
- **Se non si fa:** il sito resta a 0-35 visite a settimana e a 90 giorni (8/1/2027) rischia la regola del calo. Il picco del 4/12 e del 14-17/12 passa senza di noi.

---

## 3. Tourist Tax — cresce con le pagine giuste per il Regno Unito

### Cosa funziona

- Visite a settimana dal 22/10: 5 · 24 · 17 · 37 · 27. Totale 111 su 45 pagine. Google 68, dirette 33, assistenti 0.
- Pagine migliori: Istanbul 16 (14 da Google) · Francia 10 · home 10 (dirette) · Sapporo 6 · Giappone 5 · Catalogna 5 · Minorca 4 · Tampa 4.
- La sezione USA (Florida, Texas) porta 15 visite su 69 pagine. Il Giappone 15.
- Lezione: una pagina per luogo con la cifra nel titolo arriva su Google anche senza dominio.

### Domanda misurata

| Ricerca | Paese | Al mese | Pagina nostra |
|---|---|---|---|
| tourist tax | Regno Unito | 9.900 | home |
| hawaii tourist tax | USA | 6.600 | **no** |
| greece tourist tax | Regno Unito | 4.400 | sì |
| fuerteventura tourist tax | Regno Unito | 3.600 | **no** |
| tourist tax tenerife | Regno Unito | 2.400 | **no** |
| tourist tax spain | Regno Unito | 2.400 | sì |
| edinburgh tourist tax | Regno Unito | 1.900 | sì |
| tourist tax mexico | Regno Unito | 1.900 | sì |
| manchester tourism tax | Regno Unito | 1.600 | **no** |
| wales tourism tax | Regno Unito | 1.300 | solo Cardiff |
| tourist tax gran canaria | Regno Unito | 1.000 | **no** |
| portugal tourist tax | Regno Unito | 1.000 | solo Porto |
| hotel tax calculator | USA | 880 (clic 17,85 $) | sezione USA |
| tourist tax morocco | Regno Unito | 720 | **no** |
| nyc hotel tax | USA | 720 | **no** |
| tourist tax uk | Regno Unito | 720 | pagina paese con titolo generico |
| lanzarote · canary islands | Regno Unito | 590 · 590 | **no** |
| las vegas resort fees | USA | 8.100 | no (non è una tassa; molti concorrenti) |
| tourist tax 2027 | USA e Regno Unito | 0 | sì |

Sorpresa: «tourist tax 2027» ha volume 0. La gente cerca il luogo, non l'anno.

### Costruzioni, in ordine di visite per ora

**1. Pacchetto Canarie (5 pagine: Tenerife, Gran Canaria, Fuerteventura, Lanzarote, pagina Canarie).**
- Domanda: 8.180 al mese nel Regno Unito. Oggi nessuna pagina.
- La risposta che la gente cerca è «si paga o no?». Va scritta **solo da una fonte ufficiale** (ordinanza del Comune di Mogán, Governo delle Canarie, Cabildo di Tenerife per il Teide). La nota del sito dice che il 10/10 non c'era una fonte con tariffa: è il primo passo, 1 ora. Se la fonte non si legge, non si costruisce.
- Ore: 5. Attese: **+20 / +60** a settimana. Circa 12 visite per ora.
- Rischio: pagina con risposta «no» = poco testo. Va riempita con fatti utili: cosa si paga davvero, cosa è stato proposto, confronto con le Baleari (già nel sito).
- Tempo: le prenotazioni invernali per le Canarie sono adesso; quelle estive partono a gennaio.

**2. Tariffe 2027 (lavoro dovuto, scadenza 1/1/2027).**
- Turchia 2 %, Milano, Amsterdam (16 % sulla stampa, non ancora nella gazzetta), Islanda, Napoli, Francia 2027, sovrimposte della Florida (4 contee scadono il 31/12). Poi 1/4/2027: Catalogna, Tokyo, Cardiff. 1/7/2027: Vienna.
- Ore: 4. Attese: 0 / +8. Non porta visite nuove: **evita cifre sbagliate dal 1° gennaio**.
- Si chiude entro il 28/12, come già scritto in `STRATEGIA-LAVORO-2026-11-27.md`.

**3. Hawaii, New York e città del Regno Unito (6-8 pagine).**
- Hawaii 6.600 + 320 + 260; New York 720 + 590; Manchester 1.600 + 590; Galles 1.300; «tourist tax uk» 720 (basta rifare titolo e prima frase della pagina paese).
- Ore: 7. Attese: +10 / +35. Circa 5 visite per ora.
- Rischio: per le Hawaii i giornali sono primi; Manchester e Liverpool non sono tasse comunali ma contributi dei consorzi alberghieri: la fonte va trovata.
- Già bocciate e non riproposte: Budapest (23 delibere), Lisbona e Algarve (fonti 403), Dubrovnik.

### Monetizzazione

- AdSense non approvato. «hotel tax calculator» ha il clic più caro del gruppo (17,85 $): la sezione USA è quella che renderà di più quando ci sarà la pubblicità.
- Stay22 (alloggi) ha il dominio ammesso ma nessun link: è l'affiliazione naturale. Resta ferma per la decisione del 19/11.

### Conseguenze

- **Se si fa (1 + 2 + 3):** da 27 a 55-120 visite a settimana entro fine gennaio. Sopra 300 al mese nel caso centrale.
- **Se non si fa la 2:** dal 1/1 il calcolatore dà cifre vecchie per Turchia, Milano, Francia. È un danno di fiducia, non solo di visite.
- **Se non si fanno 1 e 3:** il sito resta intorno a 26 a settimana. Non cala, ma non cresce.

---

## 4. Cruise Health Scores — una costruzione giusta prima di gennaio

### Cosa funziona

- Visite a settimana dal 15/10: 5 · 17 · 38 · 26 · 31 · 29. Totale 150 su 54 pagine. Google 55, dirette 42, ChatGPT 23.
- Pagine migliori: home 20 · Norwegian 12 · anno 2026 10 · Royal Caribbean 7 · Carnival 6 · confronto 2026-2025 6 · Holland America 5 (tutte da Google).
- Lezione: rendono le **pagine compagnia** (41 pagine, 40 visite). Le 217 pagine nave rendono poco (1-4 visite l'una). ChatGPT cita le classifiche.

### Domanda misurata (USA)

| Ricerca | Al mese | Pagina nostra |
|---|---|---|
| norovirus on cruise ships | 3.600 | una sola pagina `/outbreaks/` |
| cruise illness · cruise ships with sickness | 1.900 | idem |
| norovirus outbreaks on cruise ships | 1.300 | idem |
| dirtiest cruise ships | 1.300 | «lowest scores» (titolo diverso dalla ricerca) |
| royal caribbean cruise outbreak | 1.000 (clic 15,84 $) | **no** |
| safest cruise line | 880 | no (un voto sanitario non è sicurezza: non si fa) |
| cruise ship outbreak | 720 | `/outbreaks/` |
| cdc cleanest cruise ships | 720 | solo per compagnia, non per nave |
| cdc cruise ship scores | 480 | home |
| wave season cruise deals | 480 | no (è vendita, non dati) |
| royal caribbean · holland america · princess norovirus | 260 · 170 · 110 | **no** |
| «<compagnia> cdc score», «<nave> cdc score» | 0 | sì (rendono lo stesso: ricerche troppo piccole per il database) |
| cruise travel insurance | 22.200 (clic 14,33 $) | riquadro SafetyWing |

### Costruzioni, in ordine di visite per ora

**1. Sezione epidemie: per compagnia e per anno (circa 10 pagine).**
- Dati già nel sito: 65 epidemie CDC dal 2023 (2023: 14 · 2024: 18 · 2025: 23 · 2026: 10). Princess 12, Holland America 11, Royal Caribbean 9, Celebrity 6, Lindblad 5, Cunard 4.
- Pagine: 6 compagnie con almeno 4 epidemie («Royal Caribbean norovirus outbreaks: CDC list») + 4 anni + la pagina madre rifatta su «norovirus on cruise ships» con la tabella per mese.
- Ore: 6. Attese: **+10 / +30** a settimana. Circa 5 visite per ora.
- Rischio: i concorrenti sono il CDC e i giornali. Rischio di tono: mai scrivere che una compagnia è «pericolosa». Solo l'elenco CDC, con data e causa.

**2. Titoli sulle ricerche vere: «dirtiest» e «cleanest cruise ships».**
- `/rankings/lowest-scores-2026/` diventa «Dirtiest cruise ships 2026? The 25 lowest CDC scores», con l'avviso che è un voto sanitario e non un giudizio. Nuova classifica «cleanest cruise ships» per nave (media degli ultimi 12 mesi).
- Ore: 2. Attese: +3 / +10. Circa 5 visite per ora.
- Rischio: la parola «dirtiest» è forte. Va usata come domanda, con il metodo scritto sotto.

**3. Anno 2027 e dati ogni settimana da gennaio a marzo.**
- Le pagine dell'anno e le classifiche 2027 devono nascere con la prima ispezione del 2027. Dati CDC ogni lunedì invece di due volte al mese, solo nei mesi di punta.
- Ore: 1 più 20 minuti a settimana. Attese: tiene le visite che ci sono.

### Tempi

- Norovirus: stagione dicembre-marzo. «Wave season» (prenotazioni): gennaio-marzo. Le pagine devono essere online **entro il 7/12** per essere lette da Google prima di gennaio.

### Monetizzazione

- AdSense non approvato. SafetyWing: 0 incassi (il pubblico delle crociere è anziano, il prodotto è per nomadi: resa attesa bassa).
- CruiseDirect su CJ (3 % della tariffa, cookie 45 giorni): dominio già ammesso, **manca il link**. La «wave season» è l'unico momento dell'anno in cui avrebbe senso. Lo segnalo: la decisione del 19/11 ferma le affiliazioni nuove, e a 120 visite al mese l'incasso atteso è vicino a 0.

### Conseguenze

- **Se si fa:** da 29 a 40-70 visite a settimana a gennaio-febbraio. È il sito su netlify.app più vicino alla soglia di 300 al mese.
- **Se non si fa:** resta a 25-30 a settimana. Nessun danno, ma si perde l'unica stagione forte dell'anno. La prossima è dicembre 2027.

---

## 5. Aste in Chiaro — manutenzione, più una costruzione piccola

### Cosa funziona

- Visite a settimana dal 22/10: 7 · 33 · 20 · 29 · 17. Totale 110 su 53 pagine.
- **ChatGPT 78 visite su 110. Google 1.**
- Pagine migliori: auto all'asta 13 (11 da ChatGPT) · Roma 13 (12 da ChatGPT) · home 5 · Milano 4.

### Domanda misurata (Italia)

| Ricerca | Al mese |
|---|---|
| aste giudiziarie | 135.000 |
| aste immobiliari · case all'asta | 18.100 · 14.800 |
| auto all'asta · aste autovetture | 6.600 · 6.600 |
| aste giudiziarie auto · aste auto | 5.400 · 5.400 |
| aste auto sequestrate polizia | 4.400 |
| aste giudiziarie roma · brescia | 4.400 · 4.400 |
| aste giudiziarie catania · milano · torino · verona · bologna · palermo | 2.900 · 1.900 · 1.900 · 1.900 · 1.900 · 1.900 |
| barche · moto · camper · trattori · furgoni all'asta | 880 · 880 · 720 · 880 · 480 |
| dopo quante aste deserte il bene torna al proprietario | 590 |
| mutuo asta giudiziaria | 140 (clic 4,50 €) |

- La domanda è grande, ma **il clic vale 0,08-0,40 €** e Google ci manda 1 visita in 6 settimane.
- Con Roma a 4.400 ricerche e 0 visite da Google, il problema non è la mancanza di pagine. O Google non ha indicizzato il sito, o i portali grandi occupano tutta la prima pagina. Da qui non si vede.

### Cosa fare

**1. Foto di Search Console (30 minuti del titolare, 0 ore nostre). Prima di tutto.**
- Serve sapere: pagine indicizzate su 436, impressioni per «aste giudiziarie <città>». Senza questo dato ogni costruzione per Google è al buio.

**2. Veicoli per tipo e per provincia (circa 15 pagine).**
- È l'unica pagina che cresce, e ChatGPT la cita. I dati ci sono: 988 veicoli con tipo e provincia (410 auto, 319 commerciali, 82 moto).
- Pagine: moto, furgoni, camper e barche se i lotti bastano, più le province con almeno 15 veicoli.
- Ore: 6. Attese: **+3 / +10** a settimana. Circa 1,7 visite per ora: la resa più bassa del piano.
- Si fa solo se il 7/12 il sito è ancora sopra 15 visite a settimana (regola del 26/11). Esce con la pubblicazione del 7/12.

**3. Due ritocchi da 2,5 ore:** pagina anche per i capoluoghi con 3-7 aste (Verona, Bologna, Venezia oggi non hanno pagina e hanno 1.900 ricerche l'una); guida «aste deserte» (590 + 210). Attese +2 / +6.

### Giudizio onesto

- **Manutenzione.** Il sito vive di una sola fonte (ChatGPT) che non controlliamo. La routine serale dei dati costa già lavoro ogni giorno.
- Se la foto di Search Console mostra impressioni vere e posizione 8-20, allora le pagine città meritano lavoro: il giudizio cambia.
- **Se non si fa niente:** 17-30 visite a settimana, a rischio alla verifica dei 90 giorni (13/1/2027).

---

## 6. Payroll Tax by State — manutenzione fino al 10/12

### Un chiarimento

- Il sito tratta la payroll tax **australiana** (8 Stati, anno fiscale dal 1/7 al 30/6). Il cambio delle tasse USA del 1/1/2027 non lo riguarda: quello è lavoro del sito Paycheck.
- La data che conta qui è il **1/7/2027** (anno 2027-28), con i bilanci statali di maggio-giugno. A gennaio non cambia niente.

### Cosa funziona

- Online dal 13/11. Visite: 40 · 18. Totale 60. **44 dirette** (lancio e prove), Google 11, Bing 1.
- L'unica pagina che Google manda: `/due-dates/` 12 visite, 9 da Google.

### Domanda misurata (Australia)

| Ricerca | Al mese | Pagina nostra |
|---|---|---|
| payroll tax (tutte le forme per Stato) | circa 40.000 | sì |
| payday super | 1.900 (clic 17 $) | sì |
| payroll tax due dates | 480 | sì |
| payroll tax exemptions · contractors · grouping | 320 · 320 · 320 | no · no · sì |
| payroll tax calculator nsw · qld · wa · vic | 390 · 320 · 320 · 210 (clic 4-10 $) | sì |
| long service leave | 18.100 | no |
| long service leave nsw · vic · qld · wa · act · sa | 14.800 · 8.100 · 6.600 · 3.600 · 3.600 · 2.900 | no |
| long service leave calculator (+ per Stato) | 9.900 (+ 8.700) | no |
| portable long service leave | 5.400 | no |

### Cosa fare

- **Adesso: niente costruzioni.** Il sito ha 2 settimane e 11 visite da Google. Le pagine ci sono già per quasi tutta la domanda del tema.
- **10/12:** foto di Search Console (già in calendario).
- **Candidata per dopo, misurata oggi: «Long service leave Stato per Stato» con calcolatore.** Circa 75.000 ricerche al mese, clic 2,6-6,6 $, regole diverse in ogni Stato: è lo stesso schema del sito. 14 ore. Attese +10 / +40 a settimana. Circa 3 visite per ora.
  - Si apre **solo se** il 10/12 Search Console mostra che Google legge il sito (almeno 20 pagine indicizzate e impressioni in crescita).
  - Rischi: tema da consulenza (ogni regola solo dal testo di legge); gli Stati hanno calcolatori ufficiali; il nome del dominio parla di payroll tax.
- Piccole, in tema: pagine «exemptions» e «contractors» (640 ricerche in tutto, 4 ore, +2 / +6). Dopo il 10/12.

### Conseguenze

- **Se si aspetta fino al 10/12:** si perdono al massimo due settimane su un sito che oggi fa 6 visite da Google a settimana.
- **Se si costruisce subito:** 14 ore al buio su un dominio che Google potrebbe non avere ancora letto. Le stesse ore su Italy Strikes rendono 3-4 volte di più.

---

## 7. Classifica di tutte le costruzioni

Visite in più a settimana, prudente / centrale. Sono ipotesi (vedi sezione 1).

| # | Sito | Costruzione | Domanda al mese | Ore | Visite in più | Visite per ora (centrale) | Entro |
|---|---|---|---|---|---|---|---|
| 1 | Italy Strikes | 16 pagine per azienda in italiano | 270.000 | 7 | +20 / +80 | 11 | 2/12 |
| 2 | Tourist Tax | Canarie (5 pagine), se c'è la fonte | 8.180 | 5 | +20 / +60 | 12 | 10/12 |
| 3 | Italy Strikes | pagine per data degli scioperi nazionali | 10.900 | 3 | +5 / +20 | 7 | 2/12 |
| 4 | Cruise | epidemie per compagnia e per anno | 9.000 | 6 | +10 / +30 | 5 | 7/12 |
| 5 | Cruise | titoli «dirtiest / cleanest cruise ships» | 2.300 | 2 | +3 / +10 | 5 | 7/12 |
| 6 | Tourist Tax | Hawaii, New York, città del Regno Unito | 13.000 | 7 | +10 / +35 | 5 | gennaio |
| 7 | Italy Strikes | 13 aeroporti | 4.300 | 5 | +6 / +17 | 3 | 14/12 |
| 8 | Payroll Tax | long service leave per Stato (solo dopo il 10/12) | 75.000 | 14 | +10 / +40 | 3 | gennaio |
| 9 | Tourist Tax | tariffe 2027 (dovuto) | 0 | 4 | 0 / +8 | 2 | 28/12 |
| 10 | Aste | veicoli per tipo e provincia | 30.000 | 6 | +3 / +10 | 1,7 | 7/12 |

La Canarie ha la resa più alta ma dipende da una fonte ancora da leggere. Per questo il primo lavoro è Italy Strikes: i dati ci sono già e la scadenza è il 2/12.

Totale delle righe 1-5 e 9: 27 ore, da +58 a +208 visite a settimana. Oggi i 5 siti insieme fanno circa 125 visite a settimana.

## 8. Calendario

| Quando | Lavoro | Pubblicazione |
|---|---|---|
| 27-30/11 | Italy Strikes: pagine azienda e pagine data; revisione indipendente | – |
| 30/11 | Controllo: Italy Strikes è tornato sopra 0 visite al giorno? | – |
| 1/12 | Tourist Tax: lettura delle fonti per le Canarie (1 ora). Sì o no | – |
| 2/12 | Italy Strikes online (pubblicazione forzata già prevista) | 15 crediti |
| 3-6/12 | Cruise: epidemie e titoli. Aste: veicoli, solo se sopra 15 visite a settimana | – |
| 7/12 | Cruise e Aste online con i dati | 30 crediti |
| 8-10/12 | Tourist Tax: Canarie + prima parte delle tariffe 2027 | 15 crediti |
| 10/12 | Foto di Search Console: Payroll Tax e Aste. Decisione su long service leave | – |
| 14/12 | Italy Strikes: aeroporti, prima degli scioperi del 14-17/12 | 15 crediti |
| 21-28/12 | Tourist Tax: chiusura tariffe 2027 (Amsterdam, Milano, Islanda) | 15 crediti |
| 4/1/2027 | Misura a 4 settimane: visite vere contro le attese di questo file | – |

## 9. Cosa serve dal titolare

1. Foto di Search Console (Rendimento, 28 giorni, e pagine indicizzate) per Aste e Payroll Tax entro il 9/12. 30 minuti.
2. Nient'altro. Nessun acquisto, nessun dominio, nessuna affiliazione nuova.

## 10. Rischi del piano

- **Le stime sono costruite su poche decine di visite.** Possono sbagliare del doppio in su o in giù. Per questo c'è la misura del 4/1/2027.
- **Pagine a modello.** Le pagine azienda e le pagine Canarie devono avere testo proprio e dati veri. Pagine sottili su siti che un giorno chiederanno AdSense sono lo stesso errore dell'audit del 26/11.
- **Italy Strikes dipende da una fonte di riserva** (il registro del Ministero è muto dal 23/10). Se la riserva si ferma, le pagine nuove mostrano dati vecchi. La riga di freschezza del 25/11 lo dice già al lettore.
- **Crediti Netlify.** Il calendario usa 90 crediti su circa 200. Resta margine per uno sciopero improvviso.
- **Nessun incasso a breve.** Anche nel caso migliore questi 5 siti arrivano a 250-330 visite a settimana, cioè 20-50 € l'anno con AdSense approvato. Il valore vero è un altro: imparare quali schemi portano visite (pagine per azienda, pagine «si paga o no?», epidemie per compagnia) e riusarli sui siti grandi.
