# Fronte nuovo, settore officina e riparazioni: codici di guasto delle auto con i dati ufficiali NHTSA (13/11/2026)

Solo ricerca: nessun sito modificato. Settore lontano dalle zone già battute (non viaggi, visti, esami, assicurazioni, eSIM). In `ESPLORATE.md` c'erano righe vicine ma diverse: richiami auto (NO del 14/10), numero di telaio (RISERVA del 13/11), consumi per modello (seme scartato). Codici di guasto, bollettini tecnici dei costruttori, codici d'errore degli elettrodomestici, tabelle per frigoristi e filettature: mai toccati (0 righe).

## In breve

- **Lo strumento dei volumi si è fermato alla quarta chiamata (errore 429, "rate limit exceeded").** Ho smesso come da regola: **3 frasi misurate su 40 previste**. Tutto il resto è contato con i suggerimenti di Google (quante varianti esistono, non quante ricerche) ed è scritto come "non misurato".
- **La domanda c'è ed è grande, ma vale poco a clic.** "p0420 code" 60.500 ricerche al mese negli USA a 0,35 $; "p0420" 49.500 a 0,60 $; "p0171" 40.500 (più "code p0171" 27.100 a 1,11 $). Due codici soli fanno circa 200.000 ricerche al mese; i codici esistenti sono oltre 12.000.
- **Il dato ufficiale si legge tutto, ed è la novità.** Oggi i file NHTSA rispondono 200 (il 14-18/10 rispondevano 403): 2.266.299 reclami dei proprietari, di cui 27.519 citano un codice di guasto (3.431 codici diversi, 1.573 terne codice × marca × modello con almeno 5 reclami); bollettini tecnici dei costruttori 2015-2025, nel solo 2025 14.836 righe con un codice (3.265 terne con almeno 5 righe).
- **Il vuoto è dimostrato:** nessuno dei concorrenti letti dice "su questo modello il costruttore ha pubblicato un bollettino per questo codice" né "quanti proprietari l'hanno segnalato all'autorità". Ma i primi posti sono di marchi forti e il pagatore è debole.
- **Esito: nessun COSTRUIRE. Due riserve, una riserva da misurare, due no.** Il migliore (codici di guasto) vale al centro circa 1.300 €/anno a 36 mesi per 50 ore: 26 €/ora, sotto i fronti già in coda (militari USA 115 €/ora, inflazione 90).

## 1. Come ho stimato

- Formula della casa: ricerche al mese × 12 × quota × 1,3 pagine a visita × incasso per 1.000 pagine × 0,92.
- Incasso per 1.000 pagine: 8 / 12 / 18 $, **sotto** la forbice di taratura (13-31 $) perché il costo per clic letto è 0,35-1,5 $ (un solo valore alto, 6,66 $ su "p0171", non confermato dalle frasi vicine).
- Quota: 0,1 / 0,4 / 1,2 %, molto meno del 3-15 % della regola, perché in prima pagina ci sono AutoZone, Kelley Blue Book, RepairPal, FIXD, YouTube e la risposta diretta di Google.
- "Usate" 1.500.000 ricerche al mese = primi 50 codici × 20.000 + coda dei codici per marca e modello 500.000. **È un'estensione da due soli codici misurati: è il numero più incerto del file.**

## 2. Le cinque idee

| # | Idea | Ricerche al mese | Costo per clic | 12 mesi | 36 mesi prudente / centrale / ottimista | Ore | €/ora (centrale 36 mesi) | Voto | Esito |
|---|---|---|---|---|---|---|---|---|---|
| A | Codici di guasto (OBD-II) per marca e modello, con bollettini e reclami NHTSA | 200.000 misurate (2 codici) → 1.500.000 usate | 0,35-1,5 $ | 400 | 170 / 1.300 / 5.500 | 50 | 26 | 4,5 | **RISERVA** |
| B | "Problemi" e "anni da evitare" per modello e anno, dagli stessi reclami | non misurate (ipotesi 1.000.000) | non letto | 200 | 100 / 600 / 3.000 | +20 | 30 | 4 | RISERVA (stesso motore di A) |
| C | Tabelle pressione-temperatura dei gas refrigeranti (R-454B, R-32, R-410A) per frigoristi | non misurate | non letto | — | non stimabile senza volumi | 20 | — | 4 | RISERVA DA MISURARE |
| D | Codici d'errore di lavatrici, asciugatrici, lavastoviglie, caldaie per marca | non misurate | non letto | — | — | 60 | — | 3 | **NO** |
| E | Filettature: punta per maschiare e coppia di serraggio per misura | non misurate | non letto | — | — | 25 | — | 3 | **NO** |

Cifre in €/anno. Le righe B e C non hanno una stima vera: senza volumi misurati la cifra di B è un'ipotesi dichiarata, quella di C non la scrivo.

### A. Codici di guasto per marca e modello — RISERVA

| Voce | Che cosa ho letto |
|---|---|
| Domanda misurata | "p0420 code" 60.500 (0,35 $), "p0420" 49.500 (0,60 $), "catalyst system efficiency below threshold" 8.100; "p0171" 40.500 (6,66 $), "code p0171" 27.100 (1,11 $), "p0171 code" 22.200 (1,54 $), "p0171 ford" 5.400 (1,89 $); "obd2 codes" 2.400 (3,59 $) |
| Forma della domanda | Codice × marca × modello: 10 suggerimenti su 10 per 12 codici provati ("p0420 honda accord", "p0300 chevy silverado", "p1450 ford escape", "c1201 toyota camry"); anche "p0420 cost to fix" con 10 varianti per marca |
| Dato ufficiale | Reclami NHTSA: file completo 376 MB (200) e API per veicolo (200). Bollettini tecnici: file 2015-2019, 2020-2024 e 2025 (200). Opere del governo federale USA; la pagina delle condizioni di nhtsa.gov risponde 403, quindi la licenza **non è riletta oggi** |
| Elenco dei codici | Archivio aperto con licenza MIT letta: 12.128 codici, 18.805 definizioni, 33 marche. **Rischio:** le definizioni generiche vengono dalla norma SAE J2012, che è protetta; i fatti brevi sono ripubblicati da tutti, ma è un elenco di terzi, non una fonte ufficiale |
| Concorrenti letti | RepairPal (2.482 parole, nessun bollettino, nessun reclamo), YourMechanic (1.151 parole, generica), FIXD (4.392 parole, costi e marche, cita i bollettini 3 volte senza elencarli), samarins.com (sito di una persona, con pubblicità), 700r4transmissionhq.com (pagina "Honda Accord P0420", 1.468 parole, nessun dato ufficiale, rete pubblicitaria di fascia alta). Non leggibili (403): obd-codes.com, kbb.com, autozone.com, engine-codes.com, autocodes.com |
| Che cosa manca a loro | Su 5 pagine lette, 0 riportano quanti proprietari hanno segnalato quel codice su quel modello e 0 elencano i bollettini del costruttore con numero e data |
| Pagatore | Pubblicità. Amazon: **4,50 % sulla categoria auto** (tabella letta oggi), per lettori di codici da 30-80 $ e ricambi. Programmi di FIXD, BlueDriver, Advance Auto Parts, CarParts: pagine 404 o 410; JustAnswer, AutoZone, PartsGeek: 403. **Nessun pagatore con cifra alta trovato** |
| Rischio | Google risponde da solo al significato del codice; i due siti piccoli che ci vivono hanno anni di anzianità; cifre di costo della riparazione non le abbiamo |

Perché non COSTRUIRE: il vuoto c'è, ma con quota 0,4 % e clic da mezzo dollaro il centrale resta a 1.300 €/anno. Sale a COSTRUIRE solo se una misura completa (i primi 30 codici e 20 terne codice × modello) mostra più di 4 milioni di ricerche al mese oppure se si trova un programma che paga a contatto (officine, garanzie estese).

### B. Problemi e anni da evitare per modello — RISERVA

- Stesso file dei reclami: conteggio per modello, anno e componente, con i bollettini accanto.
- Domanda: "years to avoid" 10 suggerimenti con 8 modelli diversi; "2014 honda accord problems" 10. Volumi non misurati.
- Concorrente: carcomplaints.com fa già questo con gli stessi dati NHTSA (pagina letta: 44 volte "complaint", 18 volte "NHTSA"). Nessun vuoto: solo quota.
- Vale come seconda sezione se A si costruisce; da sola no.

### C. Tabelle dei gas refrigeranti — RISERVA DA MISURARE

- Spinta nuova: dal 2025 i condizionatori nuovi negli USA usano R-454B e R-32 al posto dell'R-410A. Suggerimenti: "r454b pt chart" 10, "r32 pt chart" 10, "superheat chart" 10 (con 8 gas diversi).
- Dato: libreria aperta CoolProp 8.0.0, licenza MIT letta; l'R-454B è una miscela e **non ho verificato che la libreria la calcoli** (file non trovato al primo indirizzo provato).
- Pagatore: pubblicità per artigiani del clima; Amazon 3 % sugli attrezzi. Concorrenti non letti (i produttori pubblicano PDF, esistono app gratuite).
- Costa poco (20 ore, circa 40 gas × 2 unità di misura), ma senza volumi non la stimo. Prima cosa da misurare quando lo strumento riparte: "410a pt chart", "r454b pt chart", "r32 pt chart", "superheat calculator".

### D. Codici d'errore degli elettrodomestici — NO

- Domanda larga nei suggerimenti (Whirlpool, Samsung, LG, climatizzatori, caldaie Carrier: 10 su 10), non misurata.
- Nessun dato ufficiale aperto: i codici stanno nei manuali dei produttori, uno per modello. Si torna alla scrittura a mano, 60 ore e rischio di errori.
- Pagatore che conta (ricambi): RepairClinic 403, AppliancePartsPros 404. Nessuna cifra letta.

### E. Filettature e coppie di serraggio — NO

- Suggerimenti pieni ("tap drill size for" 10 misure, "1/4-20 torque spec" 10 varianti), volumi non misurati.
- Le tabelle si calcolano dalle formule, ma esistono già ovunque (littlemachineshop.com letta, 200) e chi cerca vuole un numero che Google mostra da solo. Pagatore: solo Amazon 3 % su utensili da pochi dollari.

## 3. Che cosa resta utile anche senza costruire

- **I file NHTSA ora si leggono dal server.** Questo riapre due righe vecchie di `ESPLORATE.md` ferme per il 403: "prodotti ritirati / seggiolini" (riga 230) e "modelli assemblati negli USA" (riga 213, da riprovare sul suo indirizzo specifico, non provato oggi).
- Il sito del numero di telaio (RISERVA del 13/11) guadagnerebbe una pagina per modello con reclami e bollettini: è lo stesso file.

## 4. Limiti di questa ricerca

- Volumi: 3 chiamate riuscite, poi 429. Nessun nuovo tentativo.
- Concorrenti: 5 letti, 5 bloccati (403); i due più forti (AutoZone, Kelley Blue Book) non letti.
- I conteggi dei codici nei file NHTSA vengono da una ricerca per forma (lettera + 4 caratteri): includono falsi positivi evidenti, per esempio "C1500" e "C2500" sono nomi di furgoni Chevrolet. Il numero vero è più basso di qualche punto percentuale.
- Licenza NHTSA e programmi di affiliazione dell'auto non riletti oggi.
