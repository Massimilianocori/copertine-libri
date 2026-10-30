# Verifica indipendente: affollamento dei parchi nazionali USA mese per mese (30/10/2026)

Idea da verificare: sito nuovo "Park Crowds" (63 parchi × 12 mesi, 12 classifiche mensili, 50 pagine Stato), dati NPS IRMA + normali NOAA, pagato da AdSense, DiscoverCars, RVshare, Viator, Stay22. Voto del ricercatore: **8**, stima 800 / 4.800 / 25.000 €/anno a 18 mesi (`ricerca-zona-usa-2026-10-30.md`, sez. 1).

Compito: provare a smontarla. Tutte le prove sono del 30/10/2026 (curl dal nostro server alle 21:01 UTC, autocomplete di Google `client=firefox&gl=us&hl=en`, ricerca web dagli USA). Letti per intero il rapporto e le righe di `ESPLORATE.md` sui parchi.

---

## 0. Verdetto

**DA ABBASSARE a 7, e sotto l'asticella dei soldi** (stima centrale circa 1.700 €/anno contro i 5.000 richiesti).

La fonte è perfetta e la domanda "is [parco] crowded in [mese]" è vera. Ma tre prove tolgono un punto:

1. **Esiste già un sito automatico con gli stessi dati.** `parksdecoded.com` (anche `parks-decoded.pages.dev`) usa IRMA 2020-2024 e le normali NOAA, come scrive nella pagina "Our Data". Nella sitemap ha **3.264 indirizzi**: 62 parchi, ciascuno con il "monthly crowd levels" (barra dei 12 mesi), più 12 pagine "national parks in [month]", 5 pagine "least crowded" e 639 confronti. Copre già le pagine parco e le classifiche mensili del piano. Gli manca solo la pagina "parco × mese". Il rapporto lo aveva liquidato come "poche pagine".
2. **La matrice parco × mese esiste solo per circa 17 parchi su 63.** Per i 13 parchi grandi l'autocomplete dà 10 varianti per mese su 12. Ma su 28 parchi medi e piccoli, **18 danno 0 suggerimenti** a "is [park] crowded in". Delle 756 pagine parco × mese, circa 150-200 hanno una domanda. Le altre sono pagine sottili prodotte in serie, cioè il rischio "scaled content" di Google.
3. **I soldi arrivano tardi e in parte si perdono.** "Is X crowded in September" si cerca mesi prima del viaggio, mentre RVshare e Viator hanno un cookie di **30 giorni**. Stay22 non pubblica la sua quota. L'NPS mette già la tabella mese per mese di **Zion e Yosemite**, due dei 5 parchi più cercati. Inoltre la domanda è un sì/no, la forma a cui Google risponde da solo nel riquadro dell'intelligenza artificiale.

Cosa regge: la fonte (2/2) e la forma della domanda per i parchi grandi. Nella prima pagina di Google, per le ricerche "crowded in [mese]", ci sono ancora notizie del 2015-2021, forum e blog. `parksdecoded` non è uscito in nessuna delle 6 ricerche fatte.

---

## 1. Fonte: PASSA (2/2)

| Prova | Esito |
|---|---|
| `irmaservices.nps.gov/v3/rest/stats/visitation?unitCodes=<63 codici>&startMonth=1&startYear=2019&endMonth=12&endYear=2026` | **200**, 671 KB in 0,7 secondi, una sola chiamata |
| Formato | XML di serie. JSON con l'intestazione `Accept: application/json` (provato) |
| Copertura | **63 parchi su 63**, 84 mesi ciascuno (gen 2019-dic 2025), 5.292 righe |
| 1979 | presente (provato YELL e INDU, gennaio 1979) |
| Ultimo mese nel servizio | **dicembre 2025**. Il 2026 è **vuoto** (risposta vuota anche per YELL 2026) |
| Dati 2026 provvisori | solo nei rapporti SSRS del portale ("Monthly Public Use", "Park YTD"), che si caricano da script (200, 625 byte senza dati). Non si scaricano in automatico |
| Pagina di aiuto del servizio | `irmaservices.nps.gov/v3/rest/stats/help` → 200, due operazioni (`visitation`, `total/{year}`). È un servizio documentato, quindi l'indirizzo è ragionevolmente stabile (versione `v3` nel percorso) |
| Licenza | `nps.gov/aboutus/disclaimer.htm`: "material created by the National Park Service … is generally considered in the public domain" |
| NOAA normali mensili 1991-2020 | `ncei.noaa.gov/access/services/data/v1?dataset=normals-monthly-1991-2020&stations=USC00489905…&format=json` → **200**, JSON (stazione di Yellowstone) |
| Cifre del rapporto | ricontrollate: Yellowstone luglio 975.109 / settembre 839.579 (86 %); Rocky Mountain 763.213 / 578.186; Glacier ottobre 127.537; Arches maggio 193.448. **Tutte esatte** |

Si può automatizzare? Sì, con un aggiornamento all'anno (a febbraio-marzo, quando il servizio chiude l'anno prima). La pagina deve dire "dati fino a dicembre 2025". Ogni ottobre il dato più recente ha già 22 mesi, ma per una stagionalità va bene.

Limiti del dato (sez. 5): sono ingressi stimati con contatori e moltiplicatori, non persone sui sentieri.

---

## 2. Domanda: vera per i parchi grandi, assente per i due terzi dei parchi

Prove salvate in `scratchpad/ac1.txt` e `ac2.txt` (52 + 28 interrogazioni).

**"is [park] crowded in"** (varianti di mese o stagione vere):

| Parco | Varianti | Parco | Varianti |
|---|---|---|---|
| Yellowstone | 10 | Acadia | 10 |
| Zion | 10 | Grand Teton | 10 (6 di mese) |
| Yosemite | 10 | Olympic | 10 (8 di mese) |
| Grand Canyon | 10 | Bryce Canyon | 10 (8 di mese) |
| Glacier | 10 | Joshua Tree | 10 (6 di mese) |
| Rocky Mountain | 10 (8 di mese) | Mount Rainier | 10 |
| Arches | 10 | Sequoia | 9 |
| Death Valley | 9 | Big Bend | 7 (tutte "busy in") |
| Crater Lake | 6 (2 di mese) | Great Smoky Mountains | 3 ("are the smoky mountains…") |
| North Cascades | 1 di mese | Shenandoah | 1 di mese |

**Zero suggerimenti:** Badlands, Great Sand Dunes, Capitol Reef, Congaree, Canyonlands, Denali, Redwood, Everglades, Hot Springs, Mesa Verde, Indiana Dunes, Cuyahoga Valley, White Sands, Kenai Fjords, Lassen, Pinnacles, Saguaro, Mammoth Cave, Great Basin, Isle Royale (Voyageurs dà solo Yellowstone e Yosemite).

**Altre forme:**
- "best time to visit [park] to avoid crowds": 0-6 varianti, quasi tutte riformulazioni. È il campo di Earthtrekkers e dei blog.
- "[park] crowd calendar": Yosemite 6, Rocky Mountain 5, Glacier 4, Bryce 4, Great Smoky 4, gli altri 0-3 (spesso con "right now"). Grand Teton, Olympic e Joshua Tree 0.
- "[park] busiest months": 4-10, ma per metà sono "best months / best time".
- Classifiche: "least crowded national parks in" → 10 (july, august, june, september, october, may…). "national parks to visit in" → 10 mesi. **Queste reggono**, ma `parksdecoded` le ha già tutte e 12.
- Pagine Stato: "national parks in utah crowd" → 0. Nessuna prova di domanda.

**Lettura.** Circa 17 parchi × 8-10 mesi ≈ **150-170 pagine parco × mese con domanda**, non 756. Il "3/3" del rapporto vale per i parchi grandi. Su tutta la griglia vale 2,5.

---

## 3. Concorrenza: il buco è più stretto di come è descritto

| Chi | Cosa fa | Peso |
|---|---|---|
| **parksdecoded.com** (`parks-decoded.pages.dev`, 200) | Sito automatico, dati IRMA 2020-2024 + NOAA + API NPS. 3.264 indirizzi: 2.115 sotto `/parks/` (pagina parco, sentieri, campeggi), barra "monthly crowd levels — click a month for details", "Busier than 21% of national parks", 12 "national parks in [month]", "least crowded in fall/spring/summer/winter", 639 confronti, 157 "near [città]" | **Alto**: copre già pagine parco e classifiche. Per ora non esce nelle ricerche provate |
| **nps.gov, pagine ufficiali** | `zion/planyourvisit/visitation.htm` → 200, tabella dei 12 mesi (media 2019-2023). `yose/planyourvisit/visitation.htm` → 200, tabella dei 12 mesi (media 2010-2024, aggiornata 19/11/2025). `zion/planyourvisit/crowds.htm` e `glac/planyourvisit/crowds.htm` → 200, "where and when to expect crowds". Per gli altri 16 parchi provati gli stessi percorsi danno 404 | **Medio**: per Zion e Yosemite l'ente risponde già con i numeri mensili |
| **Cruscotto NPS** (`nps.gov/subjects/socialscience/visitor-use-statistics-dashboard.htm`) | Power BI con grafici mensili per parco | Basso per Google (incorporato, nessuna pagina per parco) |
| **Outwander + Stacker** | "National park overcrowding index" (17/2/2026), dati IRMA REST di tutti i 63 parchi, "Month-by-Month Cheat Sheet" per i 15 più densi, ripreso da decine di siti di notizie | Medio: **Outwander è una piattaforma di noleggio camper**. Chi paga le commissioni fa già contenuti con questi dati |
| **Earthtrekkers** (`/us-national-parks-by-season/`) | Tabelle dei 63 parchi con i mesi di punta "based on National Park Service data from the last four years" | Medio su "best time" |
| **morethanjustparks.com** | "best time to visit [park]", "Last verified June 2026", esce per Yellowstone e Glacier | Medio |
| Prima pagina per "is yellowstone crowded in september" e "is glacier national park crowded in september" | notizie 2015-2024 (Flathead Beacon, Hungry Horse, ABC, Cowboy State Daily), Fodor's, blog | **Buco reale** per la forma sì/no con il mese |
| Prima pagina per "is zion crowded in october" | blog, notizie del 2015, `csr.hdsupply.com` (spazzatura). La tabella NPS dei mesi di Zion non esce | buco reale |

**Lettura.** Il voto "Buco 1,5/2" del rapporto si basava su "nessuno mette i numeri mese per mese" e su `parks-decoded.pages.dev` "con poche pagine". Tutte e due le cose sono sbagliate: l'NPS li mette per due parchi e un sito automatico ha 3.264 pagine con gli stessi dati. Resta libera solo la pagina parco × mese. **Buco 1/2.**

---

## 4. Soldi: i programmi ci sono, ma il momento è sbagliato per due su quattro

| Programma | Pagina ufficiale (30/10/2026) | Italiano persona fisica? | Problema |
|---|---|---|---|
| DiscoverCars | `discovercars.com/affiliate` 200: "~$20 per booking", "Cookie Lifetime: 365 days" | sì, **già attivo** (cruscotto 30/10, PayPal) | nessuno: il cookie di un anno copre la pianificazione lunga |
| RVshare | `rvshare.com/affiliates` 200: "4% commission … for each completed stay (after check-in)", "$900 average booking value", "30 day cookie duration". Iscrizione via **CJ** (`signup.cj.com/…cid=5126501`) | sì tramite CJ, con il W-8BEN (già fatto per AdSense, ma CJ ne vuole uno suo); serve l'approvazione dell'inserzionista | cookie di 30 giorni contro un viaggio pianificato 3-9 mesi prima; commissione solo dopo il check-in (estate = pagamento a fine stagione) |
| Viator | `partnerresources.viator.com` 200: "8% commission on any experience booked within 30 days", "no traffic or follower minimums", PayPal settimanale | sì (già nel piano del 17/10, scheda 6; W-8BEN) | cookie 30 giorni; commissione "once the experience has been completed" |
| Stay22 | `stay22.com/faq` 200: nessuna percentuale pubblicata ("variables that affect each partner's commission bracket (such as traffic…)"). Il cruscotto riporta 30 % della commissione delle agenzie, minimo 100 $ | sì (iscrizione `hub.stay22.com/signup`, 200) | quota non verificabile sulla pagina; soglia 100 $ |
| AdSense | già attivo su 10 siti | sì | assunzione 6-10 € ogni 1.000 pagine, da confermare |

**Il traffico "quando andare" converte?** Poco e tardi. Chi chiede "is Glacier crowded in September" sta scegliendo il mese, non ha ancora prenotato. Lo conferma il fatto che l'autocomplete aggiunge "right now / today" e "reddit", non "tours" o "rental". DiscoverCars (365 giorni) e gli alberghi (Stay22) sono i più adatti. RVshare e Viator perdono buona parte del merito per il cookie di 30 giorni.

**Stima rifatta (18 mesi, €/anno)**

Assunzioni: circa 200 pagine con domanda, più 63 pagine parco e 12 classifiche in cui `parksdecoded` è già davanti. Riferimento della rete: Cruise Health Scores (USA, 290 pagine, dal 17/10) ha fatto 20 visite nella settimana 19-26/10. EsameB1 è il motore della rete e fa circa 800 visite al mese. Le 20.000 pagine viste al mese del rapporto (venticinque volte EsameB1) sono un'ipotesi alta.

| Ipotesi | Pagine viste al mese (media dell'anno) | € ogni 1.000 (AdSense + affiliazioni) | €/anno |
|---|---|---|---|
| prudente | 4.000 | 9 (6 + 3) | **≈ 430** |
| centrale | 10.000 | 14 (8 + 6) | **≈ 1.700** |
| ottimista | 30.000 | 25 (10 + 15) | **≈ 9.000** |

Tutte le stime restano sotto i 5.000 €/anno dell'asticella, tranne l'ottimista.

---

## 5. Rischi

1. **Ingressi registrati ≠ affollamento.** "Recreation visits" sono entrate stimate con contatori di traffico e moltiplicatori per parco ("Count Procedures" che cambiano: pagina NPS "visitor-use-statistics"). Un mese con 800.000 ingressi può essere tranquillo nei giorni feriali e pieno nei fine settimana o nelle feste (Labor Day, che l'autocomplete chiede a parte). Nei parchi con **ingresso a orario** (Arches, Rocky Mountain, Glacier, Yosemite) il numero mensile è tenuto basso dalla prenotazione: il dato "sembra" meno pieno proprio quando il problema è trovare il biglietto. Le pagine devono dirlo, altrimenti la risposta "settembre è all'86 % di luglio" può portare a scelte sbagliate.
2. **Il riquadro di Google risponde da solo.** "Is X crowded in [month]" è una domanda sì/no. Le risposte sintetiche ottenute con le ricerche di oggi (Zion ottobre, Yellowstone settembre, Glacier settembre) davano già un sì/no ragionato, citando blog e notizie. Il clic resta solo a chi vuole il numero.
3. **Dato vecchio.** Il servizio REST arriva a dicembre 2025. I dati provvisori del 2026 stanno solo nei rapporti a script. Chi cerca "yellowstone in september 2026" (autocomplete vero) troverà un numero del 2025.
4. **Stagionalità forte.** Domanda e commissioni tra febbraio e agosto. In autunno e inverno poco, tranne i parchi del deserto.
5. **Pagine sottili in serie.** 756 pagine mese con 4 numeri ciascuna, di cui circa 600 senza domanda, sono esattamente ciò che Google declassa. Il rimedio è non farle.
6. **Concorrente con lo stesso motore** (`parksdecoded`), che può aggiungere le pagine parco × mese in un giorno.
7. **Idee vicine già chiuse** in `ESPLORATE`: "parchi NPS/Yosemite, l'ente risponde" (14/10), "prenotazioni NPS" (29/10), "sovrapprezzo 100 $" (18/10), "parchi statali" (29/10). Questa è davvero un'altra domanda (non duplicato), ma per Zion e Yosemite vale lo stesso verdetto "l'ente risponde".

---

## 6. Griglia rifatta

| Voce | Ricercatore | Verifica | Perché |
|---|---|---|---|
| Domanda | 3/3 | **2,5/3** | vera per circa 17 parchi su 63; Stati senza domanda |
| Buco | 1,5/2 | **1/2** | parksdecoded automatico con gli stessi dati; NPS con le tabelle di Zion e Yosemite |
| Fonte | 2/2 | **2/2** | confermata in tutto |
| Soldi | 1,5/2 | **1/2** | cookie di 30 giorni per RVshare e Viator su una ricerca di pianificazione lunga; Stay22 senza quota pubblicata |
| Rischi e ore | 0,5/1 | **0,5/1** | sito nuovo, stagionale, riquadro di Google |
| **Totale** | **8** | **7** | sotto l'asticella dei soldi (centrale ≈ 1.700 €/anno) |

Riga proposta per `ESPLORATE` (da sostituire alla riga "in verifica"):

| Affollamento dei parchi nazionali USA mese per mese | **RISERVA (7)**: fonte perfetta (IRMA REST 63/63 parchi, JSON, pubblico dominio) e "is [park] crowded in [month]" vera per circa 17 parchi; ma parksdecoded.com automatico con gli stessi dati (3.264 pagine, classifiche mensili), NPS con tabelle mensili per Zion e Yosemite, cookie di 30 giorni per RVshare e Viator; 430 / 1.700 / 9.000 €/anno | verifica-parchi-usa-2026-10-30 |

---

## 7. Se Massimiliano vuole comunque un sito di viaggio USA: la versione ridotta (12-16 ore)

Non è confermata a 8, quindi non è un piano di costruzione. È la forma più piccola che ha senso, se lui sceglie di provarla a dicembre:

1. **Riuso di `cruisescores/`.** Copiare `raccolta/`, `genera.py`, `verifica.py`, `verifica_browser.js`. Una sola chiamata IRMA in JSON per i 63 parchi, NOAA con una stazione scelta a mano per parco, cache in `dati/`. Aggiornamento una volta l'anno (marzo).
2. **Pagine (circa 250, non 1.300):** 63 pagine parco con il calendario dei 12 mesi. **Pagine parco × mese solo per i 17 parchi con domanda** (circa 170): titolo "Is Yellowstone Crowded in September? 839,579 visits (86% of July, 2025)". 12 classifiche "least crowded national parks in [month]". Niente 50 pagine Stato, niente altre unità NPS. Ogni pagina dice cosa il numero non misura (fine settimana, feste, ingresso a orario) e rimanda alla pagina NPS dell'ingresso a orario dove c'è.
3. **Monetizzazione.** AdSense e DiscoverCars (già attivi) in ogni pagina. Stay22 con i soli link "Allez" agli alberghi vicino al parco. Viator con le escursioni del parco. RVshare solo dopo l'approvazione su CJ, e solo nei parchi dell'Ovest.
4. **Controllo qualità.** Il `verifica.py` ricontrolla ogni cifra stampata contro il JSON IRMA. Ogni pagina mese deve avere 4 numeri propri e una frase diversa dalle altre (confronto con il mese prima e quello dopo). Revisione indipendente prima della pubblicazione. Soglie per decidere dopo l'uscita: a 45 giorni almeno 150 impressioni al giorno e almeno 10 parchi con impressioni; a 120 giorni (marzo-aprile 2027) almeno 3.000 visite al mese, altrimenti si congela.
5. **Cosa serve da Massimiliano:** il sì al sito nuovo (oltre il tetto di novembre, quindi da dicembre); creare il sito su Netlify con il nome scelto; aggiungerlo in AdSense; iscriversi a CJ (per RVshare), Viator e Stay22 (10-20 minuti ciascuno, W-8BEN come persona fisica residente in Italia). Facoltativa la chiave gratuita dell'API NPS.

---

## 8. Fonti lette il 30/10/2026

| Fonte | Stato |
|---|---|
| `irmaservices.nps.gov/v3/rest/stats/visitation` (63 parchi, 2019-2026; YELL 2025-2026; YELL/INDU 1979; ZION JSON) | 200 (2026 vuoto) |
| `irmaservices.nps.gov/v3/rest/stats/total/2025` (JSON) | 200 |
| `irmaservices.nps.gov/v3/rest/stats/help` | 200 |
| `irma.nps.gov/Stats/`, `/Stats/Reports/National`, `/STATS/Reports/Park/YELL` | 200 |
| Rapporti SSRS "Park YTD Version 1" e "Recreation Visitors By Month" per YELL | 200, 625-663 byte, senza dati (script) |
| `nps.gov/subjects/socialscience/visitor-use-statistics-dashboard.htm` (Power BI incorporato) | 200 |
| `nps.gov/subjects/socialscience/visitor-use-statistics.htm` | 200 |
| `nps.gov/aboutus/disclaimer.htm` (pubblico dominio) | 200 |
| `nps.gov/zion/planyourvisit/visitation.htm`, `nps.gov/yose/planyourvisit/visitation.htm` | 200 (tabelle mensili) |
| `nps.gov/zion/planyourvisit/crowds.htm`, `nps.gov/glac/planyourvisit/crowds.htm` | 200 |
| Stessi percorsi per yell, grca, romo, arch, acad, grsm, grte, olym, brca, jotr, mora, seki, deva, bibe, crla, shen | 404 |
| `ncei.noaa.gov/access/services/data/v1?dataset=normals-monthly-1991-2020` | 200 JSON |
| `parks-decoded.pages.dev/`, `/parks/yellowstone/`, `/about/our-data/`, `/sitemap-0.xml` (3.264 indirizzi) | 200 |
| `parksdecoded.com` | 200 |
| `stacker.com/stories/travel/national-park-overcrowding-index` (per outwander.com, 17/2/2026) | 200 |
| `outwander.com` (noleggio camper) | 200 |
| `earthtrekkers.com/us-national-parks-by-season/` | 200 |
| `rvshare.com/affiliates` (iscrizione su CJ) | 200 |
| `partnerresources.viator.com` | 200 |
| `viator.com/affiliates` | 403 |
| `stay22.com`, `/faq`, `/terms`, `/creators`; `hub.stay22.com/signup` | 200 |
| `discovercars.com/affiliate` | 200 |
| Autocomplete Google: 13 parchi × 4 forme + 28 parchi medi e piccoli + 7 forme di classifica | 87 interrogazioni |
| Ricerche web: "national park crowd calendar monthly visitation every park", "is zion crowded in october", "national park visitation by month chart all parks NPS data", "outwander national park overcrowding index…", "crowd calendar national parks…", "is yellowstone crowded in september", "yellowstone crowds by month", "parksdecoded national parks crowds", "is glacier national park crowded in september" | – |
