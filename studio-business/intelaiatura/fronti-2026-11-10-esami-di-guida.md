# Fronte: il modello EsameB1 sugli esami di guida (mercati inglesi + Francia), 10/11/2026

**Domanda del giro.** EsameB1 cresce (48 → 428 visite a settimana in 4 settimane, 350 clic da Google in 28 giorni) perché trasforma i dati ufficiali per sede d'esame in pagine per città. Si può fare lo stesso con l'esame di guida (percentuale di promossi, attese, sedi, costi) nei Paesi di lingua inglese, dove chi paga (assicurazioni per neopatentati, corsi, app per la teoria) vale di più?

**Risposta breve: no, non con i numeri di oggi.** Nessuna idea arriva a 8, nessuna passa l'asticella del sito nuovo (voto ≥ 7 e ≥ 5.000 €/anno centrali), nessuna ha un ottimista ≥ 10.000 €. Il quadro, mercato per mercato:
- **I dati ci sono, ma un sito automatico è già primo:** Regno Unito, Irlanda, Francia.
- **I dati per sede non sono pubblici:** California e Stati USA, Ontario, Victoria, British Columbia.
- **I dati ci sono, ma non per sede o sono vecchi:** New South Wales (per Comune di residenza), Queensland (fermo a gennaio 2024), South Australia (solo totale statale).
- **La fonte risponde 403 o con una verifica anti-robot, che non si aggira:** Irlanda (RSA), Nuova Zelanda (NZTA), Ontario (DriveTest).

Da dove nasce l'idea (fonti esterne): i cataloghi open data ufficiali (data.nsw/Transport for NSW, data.qld, data.sa, BC Data Catalogue, data.ca.gov, data.ny.gov e catalogo Socrata USA, data.ontario, data.govt.nz, data.vic, data.wa, data.gouv.fr) e l'autocomplete Google in AU, NZ, CA, US, IE e FR. Le ripetizioni di ESPLORATE sono state evitate: le righe sui promossi nel Regno Unito (14/10, 21/10), in Irlanda e Victoria (16/10), nei Paesi Bassi (16/10) e in Spagna (17/10) si richiamano qui solo come conferma.

## Classifica

| # | Idea | Dove andrebbe | Voto | Prudente / centrale / ottimista €/anno a 18 mesi | Ore (agenti + Massimiliano) | Esito |
|---|---|---|---|---|---|---|
| 1 | **Promossi all'esame di guida per ufficio DMV in California**, con dati ottenuti da una richiesta di accesso agli atti (CPRA) | sito nuovo in inglese | **5** | 100 / 1.200 / 5.000 | 25-35 + 20 min (invio della richiesta) | RISERVA: la domanda per ufficio c'è, ma il dato non è pubblico. Si riapre solo se la DMV consegna la tabella per ufficio |
| 2 | **Promossi per Comune (LGA) nel New South Wales**, più l'esame di teoria (DKT) per lingua, l'esame di percezione del pericolo (HPT) e i tentativi | sito nuovo in inglese (nessun sito nostro adatto) | **4,5** | 50 / 300 / 1.500 | 15-20 + 0 | NO come sito: dato per Comune di residenza e non per sede, domanda piccola, nessun pagatore australiano con una cifra |
| 3 | **Taux de réussite par auto-école e par ville (Francia)**, file ufficiale di 11.371 autoscuole | sito nuovo in francese | **4** | 100 / 600 / 2.500 | 20-30 + 0 | NO: la mappa ufficiale e vroomvroom.fr mostrano già il tasso per autoscuola e per città; i pagatori fanno solo parrainage |
| 4 | Attese e promossi per sede: Regno Unito, Irlanda, Nuova Zelanda, BC, Ontario, Queensland, South Australia, New York | – | 2-5,5 | – | – | NO: già presidiati, fonte bloccata o dato inesistente (sez. 4) |

---

## 1. Promossi per ufficio DMV in California (voto 5, RISERVA)

**In una riga.** Una pagina per ognuno dei circa 175 uffici DMV californiani che fanno l'esame pratico, con la percentuale di promossi, il numero di esami e il confronto con la contea. Ci sarebbero anche le classifiche cercate ("easiest DMV to pass driving test in Los Angeles / Bay Area / San Diego / Orange County").

**Domanda (autocomplete en/us, 10/11/2026).**
- "dmv driving test pass rate": 10 suggerimenti, 9 con il nome dell'ufficio (pomona, norco, pasadena, montebello, bellflower, westminster, el monte, west covina, van nuys).
- "san jose dmv driving test pass rate": 4.
- "easiest dmv to pass driving test": 10 (los angeles, bay area, california, san diego, southern california, orange county, ct).
- Altri Stati, ma solo a livello di Stato: "texas driving test pass rate" 7, "ny road test pass rate" 5, "nj road test pass rate" 5.
- Varianti generiche: "dmv pass rates by location" 0, "california dmv pass rates by office" 0.

È la domanda per sede più forte trovata nel giro, molto simile a EsameB1, ma concentrata sulla zona di Los Angeles.

**Dati.** Il dato non è pubblico.
- data.ca.gov: per "drive test" non c'è nessun dataset della DMV. Per "dmv field office" c'è solo "Department of Motor Vehicles Office Locations" (aggiornato il 29/10/2026), cioè gli indirizzi.
- La pagina dell'ufficio (es. `dmv.ca.gov/portal/field-office/pomona/`, 200, 129 KB) non riporta né promossi né attese.
- Catalogo Socrata USA: per "road test pass", "road test results" e "driver license exam" non c'è nessun dataset con i promossi per sede. New York pubblica solo l'elenco dei siti d'esame (`n6g4-x6f5`, 4/6/2026).

L'unica strada è una richiesta CPRA, che chiunque può fare senza costi. Le domande per ufficio in autocomplete fanno pensare che qualcuno abbia già ottenuto e pubblicato una tabella del genere (non verificato: i risultati di Google, DuckDuckGo e Bing non si leggono dal server).

**Concorrenza.** Non letta, perché i motori di ricerca sono chiusi a curl. È probabile che esistano articoli o liste fatte con dati ottenuti da richieste del passato. Il rischio di trovare un concorrente già primo è alto (lezione del 21/10 sul DVSA).

**Chi paga (cifre lette).**
- Aceable (corsi di guida online per neopatentati) ha un programma di affiliazione su `partnerships.aceable.com` ("Affiliate Program: earn commission on referrals"), senza cifra pubblica.
- I Drive Safely ha un programma su `idrivesafely.com/partnerships/` ("competitive commission rates"), anche qui senza cifra.
- Amazon US: Automotive 4,5 % (tabella letta il 6/11, già nel repository).
- AdSense: pubblico USA con temi auto e assicurazione.

**Stima a 18 mesi (formula: visite al giorno × 365 × 1,5 pagine × RPM 10 € ogni 1.000 pagine + vendite affiliate × 6 €).**
- Prudente **100 €**: la DMV rifiuta o tarda oltre 6 mesi, restano poche pagine generiche.
- Centrale **≈ 1.200 €**: 120 visite/giorno → 657 € di pubblicità + 8 corsi al mese × 6 € × 12 = 576 €.
- Ottimista **≈ 5.000 €**: 500 visite/giorno → 2.740 € + 30 corsi al mese × 6 € × 12 = 2.160 €.

**Ore.**
- Agenti: 25-35.
- Massimiliano: 20 minuti, per l'invio della richiesta al portale atti della DMV (è un contatto con un ente pubblico, va proposto a lui).
- Poi una richiesta all'anno per aggiornare i dati.

**Rischi.**
- Il dato è una fotografia, non un flusso mensile come quello di EsameB1.
- Concorrenza non verificata.
- I pagatori non dichiarano una cifra.
- Un solo Stato. Gli altri Stati hanno domanda solo a livello di Stato.

**Si riapre** se la DMV consegna i numeri per ufficio e un programma (Aceable o I Drive Safely) mostra una cifra ≥ 10 $ a iscrizione. Con questi due fatti il voto salirebbe a 6,5, ancora sotto l'asticella.

## 2. Promossi per Comune nel New South Wales (voto 4,5, NO come sito)

**Dati (i migliori del giro).**
- Fonte: Transport for NSW, "Driver Licence Test Statistics". Licenza CC BY, file mensili zip, 10 file del 2026, da gennaio a ottobre. Il file di ottobre è stato pubblicato l'1/11/2026.
- Ogni riga riporta: tipo di esame, sesso, età, esito, tentativo, lingua dell'esame, interprete, Comune di residenza (130 LGA) e conteggio (le celle "<=5" sono mascherate).
- Volumi da gennaio a ottobre 2026: 370.258 esami pratici per auto (34-41 mila al mese), 159.969 esami di percezione del pericolo, 126.597 esami di teoria, 74.593 esami di teoria per moto.
- Promossi al pratico: 53,5 % al 1° tentativo, 49,5 % al 4°. Per Comune vanno da Cumberland 42,7 % a Liverpool 49,7 %.
- Promossi alla teoria per lingua: inglese 59,6 %, cinese 73,8 %, arabo 49,7 %, vietnamita 66,0 %.
- **Il limite: il dato è per Comune di residenza del candidato, non per sede d'esame.** Il catalogo non ha altri dataset "per centro".

**Domanda (en/au).**
- "driving test pass rate nsw": 5 suggerimenti ("richmond nsw", "highest pass rate driving test centre nsw").
- Per sede: "silverwater driving test pass rate" 2, "blacktown driving test" 10 (soprattutto i percorsi: route, map, pdf, reddit).
- "best place to do driving test sydney": 6.
- "dkt pass rate": 3.
- "hazard perception test pass rate": 10, ma quasi tutte sul punteggio minimo.

La gente cerca la sede, noi avremmo il Comune: la pagina non risponde esattamente alla domanda.

**Concorrenza.** I risultati non sono leggibili. Sui percorsi d'esame ci sono app dedicate ("driving test routes app", in autocomplete).

**Chi paga (cifre lette).**
- Amazon.com.au Associates: Books 8 %, elettronica e Camera & Photo 5 %, Automotive 2 % (tabella ufficiale letta oggi).
- EzLicence (prenotazione delle lezioni): nessuna pagina affiliati (`/affiliates` e `/refer-a-friend` danno 404).
- Assicurazione per P-plater: "car insurance for p platers" ha 10 varianti per Stato, ma nessun programma con cifra è stato trovato.

**Stima a 18 mesi (formula: visite/giorno × 365 × 1,5 pagine × RPM 6 € + Amazon).**
- Prudente **50 €**.
- Centrale **≈ 300 €**: 60 visite/giorno → 197 € + 5 libri o dash cam al mese × 1,5 € × 12 ≈ 90 €.
- Ottimista **≈ 1.500 €**: 250 visite/giorno → 820 € + affiliazione assicurativa ipotetica.

**Ore.** 15-20 di agenti: il generatore di EsameB1 si adatta e i file sono puliti.

**Rischi.** Pagina "per area" invece che "per sede", e mercato piccolo (circa 200 mila candidati all'anno).

**Esito.** Non si costruisce. Non c'è un sito nostro dove metterla come sezione (EsameB1 è italiano, Before You Fly parla di viaggi): resterebbe un sito nuovo da 300 €.

## 3. Taux de réussite per autoscuola e per città, Francia (voto 4, NO)

**Dati (perfetti).**
- File ufficiale `autoecoles.securite-routiere.gouv.fr/.../auto-ecoles.csv`: 200, 5,3 MB, 11.371 autoscuole, tutte con il tasso di promossi B al 1° tentativo e complessivo. Ci sono anche moto e mezzi pesanti, le etichette e l'accessibilità.
- Ultima modifica del file: 19/2/2026. Licenza Ouverte 2.0. Su data.gouv.fr risulta "mensile".

**Domanda (fr/fr, forte).**
- "taux de réussite permis": 10, con "par auto-école" e "par ville".
- "taux de réussite auto école": 10 (lyon, paris, marseille, montpellier, yvelines, 2025).
- "centre d'examen permis": 10 (montpellier, reims, strasbourg, nimes, angers, saint priest, "le plus facile").
- "examen code de la route la poste": 10.
- "taux de réussite code de la route": 10 (con Ornikar e La Poste).

**Concorrenza.**
- Il Ministero ha già la mappa ufficiale delle autoscuole con i tassi: l'ente ha il motore.
- vroomvroom.fr ha pagine per città con i tassi per autoscuola e i prezzi delle lezioni (a Parigi: "taux de réussite moyen 52 %", lezione 63 €, letti).
- centrestagepermis.fr ha pubblicato ieri (9/11/2026) su data.gouv.fr un dataset "taux de réussite au permis B par département 2025".

È lo schema già visto nei Paesi Bassi il 16/10: ente con il motore più aggregatore.

**Chi paga.** Solo il parrainage da cliente a cliente: lePERMISLIBRE dà 50 € al cliente e all'amico, Ornikar fa promozioni, e le pagine affiliazione o parrainage di Ornikar e Stych danno 404. Nessun programma per editori con una cifra.

**Stima.** 100 / 600 / 2.500 €/anno (pubblicità francese con RPM 4 €).

**Esito.** Non si costruisce.

## 4. Scartate con prova

| Mercato | Perché no (10/11/2026) |
|---|---|
| **Regno Unito** (promossi, attese, teoria, moto, mezzi pesanti) | passrates.uk ha la home "321 car centres ranked", la mappa, le classifiche, le città, le attese ("booking-wait-times"), la teoria, la moto e i mezzi pesanti, tutto dal DVSA. Pagatori letti oggi: Driving Test Success paga **1,00 £ per vendita dell'app** (programma ADI Hubb); Veygo ha solo "give £10, get £10" tra clienti; Marmalade solo cashback Quidco; PassMeFast risponde 403. Conferma il NO del 21/10 (5,5) |
| **Irlanda** | Pagina delle attese RSA: **403** dal server; odo.ie riprende già i promossi per sede (NO del 16/10). Domanda forte ("driving test pass rate finglas/waterford/tralee/dundalk/longford", "driving test wait times dublin/cork") ma fonte chiusa |
| **Nuova Zelanda** | `nzta.govt.nz/resources/driver-licence-statistics/` risponde con la pagina di verifica anti-robot "Just a moment..." (non aggirata); data.govt.nz non ha dataset. Domanda piccola ("restricted driving test pass rate nz" 4) |
| **British Columbia** | Domanda forte ("icbc road test wait times" 10), ma le pagine ICBC sulle attese danno 404. Il dataset "ICBC - Driver Licensing" (9/12/2025) contiene solo i metadati: i dati sono ad accesso per ricerca, per Comune di residenza, fino al 2024 |
| **Ontario** | Domanda per sede ("oakville g2 test pass rate" 4; peterborough, orangeville, newmarket, etobicoke; "drivetest wait times" 10), ma drivetest.ca risponde **403** e data.ontario.ca non ha niente ("drivetest" 0). Servirebbe una richiesta FIPPA, che costa 5 $: è una spesa |
| **Queensland** | data.qld ha i promossi per LGA e i tempi d'attesa (giorni lavorativi) per 73 sedi: buona granularità, ma **ultimo dato gennaio 2024** (promossi dicembre 2023). Domanda: "brisbane / ipswich qld driving test pass rate". Si riapre se il TMR riprende a pubblicare |
| **South Australia** | Il dataset "Practical Driving Tests" (25/7/2025) riporta solo il totale statale per classe e per anno, non le sedi |
| **Victoria, Western Australia** | data.vic: "driving test" 0 dataset (VicRoads non pubblica, come il 16/10); WA: nessun dataset, pagine del Ministero 404. Domanda WA ("west perth driving test pass rate", "highest pass rate driving test centre perth") senza fonte |
| **New York, altri Stati USA** | New York: solo l'elenco dei siti d'esame; le attese mensili trovate sono del New Brunswick (`gnb.socrata.com`) e solo a livello di provincia. Le attese live agli uffici (NC, Colorado, San Diego in autocomplete) cambiano ogni minuto: non sono adatte a un sito statico |

## 5. Cosa insegna

1. **EsameB1 funziona perché unisce due cose:** un dato ufficiale per sede che si aggiorna e nessun aggregatore. Negli esami di guida le due cose non stanno mai insieme. Dove il dato è pubblico per sede (UK, IE, FR, NL, ES) un sito automatico o l'ente l'hanno già trasformato in pagine. Dove manca un concorrente (California, Ontario, Victoria) il dato non è pubblico.
2. **Il dato "per area di residenza" (NSW, BC, QLD) non risponde alla domanda "per sede"** e vale poco.
3. **Chi paga per i neopatentati non paga gli editori.** UK: 1 £ per app, sconti tra amici, cashback. Francia: parrainage. AU: nessun programma. USA: programmi esistenti ma senza cifra. È la differenza decisiva rispetto alle categorie con pagamento per contatto.
4. **L'unico buco vero è la California.** Serve la richiesta di accesso agli atti: un'azione di Massimiliano verso un ente, gratuita, da proporre solo se un pagatore USA mostra una cifra.

## 6. Fonti controllate (10/11/2026, curl dal server)

| Fonte | Stato | Nota |
|---|---|---|
| data.nsw.gov.au / opendata.transport.nsw.gov.au "Driver Licence Test Statistics" | 200, zip 1,17 MB | 10 CSV mensili 2026, 20-22 mila righe ciascuno, CC BY, per LGA |
| data.qld.gov.au "Practical driving tests" (API datastore) | 200 (download diretto 202 vuoto) | 435.979 righe promossi fino al 12/2023; 427.342 righe attese, 73 sedi, fino al 1/2024 |
| data.sa.gov.au "Driver Licensing - Practical Driving Tests" | 200 | CSV annuali 2018-2024, solo totale statale |
| catalogue.data.gov.bc.ca "ICBC - Driver Licensing" | 200 | solo metadati; icbc.com, pagine delle attese: 404 |
| data.ca.gov; dmv.ca.gov/portal/field-office/pomona/ | 200 | nessun dato di promossi o attese per ufficio |
| api.us.socrata.com (road test, driver license exam) | 200 | New York: solo i siti; New Brunswick: attese provinciali |
| data.ontario.ca; drivetest.ca | 200 (0 risultati); **403** | – |
| nzta.govt.nz; catalogue.data.govt.nz | pagina "Just a moment..." (non aggirata); 0 | – |
| rsa.ie (waiting times) | **403** | – |
| passrates.uk | 200, 410 KB | 321 centri, teoria, moto, mezzi pesanti, attese |
| autoecoles.securite-routiere.gouv.fr auto-ecoles.csv; data.gouv.fr | 200, 5,3 MB; 200 | 11.371 autoscuole, modificato il 19/2/2026 |
| vroomvroom.fr/auto-ecoles/paris/; centrestagepermis.fr | 200 | concorrenti francesi |
| Pagatori: drivingtestsuccess.com/app-referral-program (1,00 £), veygo.com/refer (10 £ tra amici), wearemarmalade.co.uk/affiliates (Quidco), partnerships.aceable.com (senza cifra), idrivesafely.com/partnerships (senza cifra), lepermislibre.fr/parrainage (50 € tra clienti), affiliate-program.amazon.com.au (Books 8 %, Electronics 5 %, Automotive 2 %) | 200 | passmefast.co.uk 403; veygo, collingwood, ezlicence, ornikar, stych pagine affiliati 404 |
| suggestqueries.google.com (au, nz, ca, us, ie, fr) | 200 | circa 75 interrogazioni, riportate sopra |
| DuckDuckGo, Bing, Brave | 202 / non usati / 429 | composizione dei risultati non letta |
