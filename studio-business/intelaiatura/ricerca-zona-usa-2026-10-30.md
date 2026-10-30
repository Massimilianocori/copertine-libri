# Ricerca di zona: STATI UNITI (30/10/2026)

Richiesta di Massimiliano: "il mondo è molto più grande, ci sono più opportunità e tu non le stai trovando". Obiettivo: idee da voto 8-9 per siti o sezioni automatici (script Python + dati ufficiali + Netlify), pagati da AdSense e da affiliazioni con nome. Restano le regole: niente spese senza il suo sì, niente email a freddo, niente social, niente vendita diretta, niente consulenza personalizzata (legale, medica, finanziaria).

**Zona di questa ricerca:** gli Stati Uniti, cioè il pubblico che vale di più in pubblicità. Settori provati apposta lontano dai due ricercatori in parallelo ("cloni di EsameB1" e "numeri ufficiali che spostano soldi"): viaggi interni e parchi, banche, assicurazioni sanitarie, assicurazioni auto e casa, energia, istruzione universitaria, licenze professionali, veicoli, casa, animali, pesca.

**Letti prima:** `ESPLORATE.md` per intero (492 righe) e i tre rapporti `ricerca-profonda-2026-10-28-*.md` (mercato, commissioni, assistenti). Molte famiglie americane sono già chiuse (prezzi degli ospedali, Care Compare, limiti dei mutui, affitti HUD, tasse sulla casa per contea, richiami, incentivi auto elettriche, premi ACA, NCLEX, caccia e pesca, parchi statali, prenotazioni NPS, reclami CFPB, assicurazione casa in Florida, alluvioni, condomini FHA, disastri). Non le ho rifatte. Dove una prova nuova tocca una vecchia idea lo scrivo (sez. 3).

**Prove:** tutte del 30/10/2026.
- `curl` dal nostro server: stato HTTP e contenuto letto davvero.
- Autocomplete di Google (`suggestqueries.google.com`, `client=firefox`, `gl=us`, `hl=en`). Il 28/10 un'altra ricerca ha visto che `gl` non cambia i suggerimenti: valgono per l'inglese in generale.
- Ricerca web per vedere chi c'è in prima pagina.

Limiti onesti: niente volumi di ricerca veri, quindi le stime in euro sono stime con le assunzioni scritte accanto.

---

## 0. Risposta in breve

**Una candidata arriva a 8: "quanto è affollato il parco [X] a [mese]", per i parchi nazionali americani.** È un sito nuovo con i dati mensili ufficiali delle visite (National Park Service, pubblico dominio, dal 1979).

- **Domanda provata:** la ricerca ha la forma "parco × mese", la stessa forma "per città" che fa funzionare EsameB1. Esempi dall'autocomplete: "is yellowstone crowded in september/october/august/july/june/may" (10 varianti), "is rocky mountain national park crowded in september/june/august/october/july" (10), "is arches national park crowded in october/september/march/april", "is glacier national park crowded in july/august/september/june" (10). Esiste anche "[parco] crowd calendar" per 10 parchi diversi.
- **Google è debole:** in prima pagina ci sono forum (Fodor's, Good Sam, Reddit), blog con cifre inventate o vecchie, notizie del 2015-2023 e pagine spazzatura su `pages.dev`. Nessuna pagina mette i numeri ufficiali mese per mese.
- **Chi paga ha un nome:** DiscoverCars (circa 20 $ a noleggio, cookie 365 giorni), RVshare (4 % della prenotazione, media dichiarata 900 $ cioè circa 36 $), Viator (8 %), Stay22 per gli alberghi vicino al parco. Si aggiunge AdSense su un pubblico americano di viaggio.

Le altre candidate restano tra 6 e 6,5, per tre motivi diversi:
- la licenza non permette l'uso commerciale (WUE, sconti universitari);
- un sito automatico c'è già (chiusure di filiali bancarie, branchspot.com);
- il tema è sanitario e la finestra dura solo 7 settimane all'anno (piani Medicare Advantage che chiudono).

| # | Candidata | Dove | Voto | 18 mesi €/anno (prudente / centrale / ottimista) | Prima entrata | Ore |
|---|---|---|---|---|---|---|
| 1 | **Affollamento dei parchi nazionali mese per mese** ("is [park] crowded in [month]", "crowd calendar"), dati NPS IRMA + clima NOAA | sito nuovo (da dicembre, oltre il tetto di novembre) | **8** | 800 / 4.800 / 25.000 | AdSense dal 1°-2° mese; prime commissioni marzo-maggio 2027 (stagione in cui si prepara l'estate) | 20-30 |
| 2 | Piani Medicare Advantage che chiudono nel 2027, per assicuratore, Stato e contea (file CMS "crosswalk" 1/10/2026) | sito o sezione nuova | 6,5 | 300 / 1.200 / 4.000 | solo nella finestra 15/10-7/12 | 12-18 |
| 3 | Sconti WUE sulle tasse universitarie: 169 università × 13.694 corsi, per Stato e corso | sezione o sito nuovo | 6 (7 con il permesso scritto di WICHE) | 200 / 900 / 3.000 | 3°-6° mese | 10-15 |
| 4 | Filiali bancarie chiuse per banca, Stato e città (FDIC, 1.247 chiusure in 13 mesi) | sito nuovo | 6 | 200 / 800 / 2.500 | 2°-4° mese | 12-18 |
| 5 | Costo e regole del GED Stato per Stato | da passare al ricercatore "cloni di EsameB1" | 6 | – | – | – |

**Migliori a 7-7,5:** nessuna in questa zona. Le due più vicine sono:
- **WUE: 7 se WICHE dà il permesso scritto.** I dati sono perfetti (un JSON dentro la pagina), ma la licenza è CC BY-NC-SA, cioè non commerciale.
- **Piani Medicare Advantage che chiudono: 6,5.** Domanda e fonte sono ottime, ma il tema è sanitario e c'è già concorrenza (MoneyGeek, Becker's, careroute.ai).

**Lezione della zona USA.** Quasi ogni tema "di soldi" americano (assicurazioni, mutui, sanità, licenze) ha già in prima pagina un comparatore che vive di affiliazioni. Il buco si trova nei temi di **pianificazione**, dove chi cerca sta per spendere ma la domanda è "quando" e non "quanto costa". Sono i viaggi interni, i parchi, le stagioni. Lì in prima pagina ci sono forum e blog senza dati, mentre la fonte ufficiale ha decenni di serie mensili che nessuno mette in pagina.

---

## 1. Candidata 1: affollamento dei parchi nazionali mese per mese (voto 8)

### In una riga
Un sito nuovo (nome di lavoro "Park Crowds") con queste pagine:
- una pagina per ogni parco nazionale (63) con il "calendario dell'affollamento": visite di ogni mese della media 2021-2025, posizione del mese (1° = più pieno), confronto con il mese di punta, andamento dal 2019;
- **una pagina per ogni coppia parco × mese** ("Is Yellowstone crowded in September? 839,579 visits in Sept 2025, 86% of July"), con temperature medie NOAA e i fatti datati che contano (prenotazione a orario, strade chiuse) quando l'ente li scrive;
- una pagina per ognuna delle altre unità NPS che pubblicano le visite (monumenti, coste, parkway);
- 12 classifiche "busiest / least crowded national parks in [month]";
- 50 pagine Stato.

### Perché non è un'idea già chiusa
In `ESPLORATE` ci sono tre righe sui parchi, tutte diverse da questa:
- "parchi NPS/Yosemite, l'ente risponde già" (14/10): erano le **condizioni di oggi**, strade e chiusure, a cui risponde nps.gov;
- "apertura delle prenotazioni" (29/10): risponde recreation.gov;
- "sovrapprezzo 100 $" (18/10): è una regola sola.

L'affollamento per mese è un'altra domanda. L'ente ha il dato ma **non lo mostra a chi pianifica**: sta nel portale statistico IRMA, fatto per i ricercatori. Fa eccezione Yosemite, che ha una pagina sua delle visite.

### Fonte (letta il 30/10/2026)
- **NPS IRMA, servizio REST**: `irmaservices.nps.gov/v3/rest/stats/visitation?unitCodes=…&startMonth=…&startYear=…` → **200**, XML con visite ricreative e non ricreative per unità e mese. Ci sono dati dal 1979 (provato) al dicembre 2025. Il 2026 non è ancora nel servizio; secondo la pagina "statistics FAQ" del NPS il portale web pubblica i dati provvisori del mese entro il 15 del mese dopo. Il totale per mese della rete risponde 200 (`/stats/total/2025`): 323.014.305 visite ricreative nel 2025. Licenza: dato federale, **pubblico dominio**.
- **NOAA NCEI, normali climatiche mensili 1991-2020**: `ncei.noaa.gov/access/services/data/v1?dataset=normals-monthly-1991-2020…` → **200**, JSON. Pubblico dominio.
- **Pagine dei parchi** (fatti datati da scrivere a mano una volta l'anno, per circa 10 parchi con prenotazione a orario): `nps.gov/romo/planyourvisit/timed-entry-permit-system.htm` → 200; `nps.gov/yose/planyourvisit/visitation.htm` → 200; Arches con il percorso provato → 404 (da cercare).
- **API NPS** (`developer.nps.gov`) → 403 senza chiave. La chiave è gratuita e serve solo un'iscrizione: non è una spesa. Darebbe tariffe, avvisi ed eventi per parco. Non è necessaria per la prima versione.
- `recreation.gov` (RIDB) → 401 senza chiave; disponibilità dei permessi → 404. Non serve.

**Esempio di cosa dice il dato (2025, visite ricreative):**

| Parco | Mese più pieno | Settembre in % del mese più pieno | Sorpresa che corregge i blog |
|---|---|---|---|
| Yellowstone | luglio 975.109 | **86 %** (839.579) | "September is quiet" non è vero: è quasi come agosto |
| Rocky Mountain | luglio 763.213 | 76 % (578.186) | ottobre (382.163) è più pieno di maggio (319.336): l'autunno non è "vuoto" |
| Glacier | luglio 765.061 | 72 % (552.479) | ottobre crolla a 127.537: il vero "mese vuoto" è ottobre, non settembre |
| Arches | **maggio** 193.448 | 74 % (142.337) | il picco è in primavera, non in estate; marzo (152.554) è più pieno di settembre |

È la forma che gli assistenti di intelligenza artificiale citano già nella sezione dei rifiuti dei visti: numero ufficiale in alto, fonte e data, una pagina per ogni domanda.

### Domanda (autocomplete, 30/10/2026)
- "is yellowstone crowded in" → 10: *september, october, august, july, june, late september, mid september, late august, mid august, may*.
- "rocky mountain national park crowds" → 10: *crowd calendar, is … crowded in september/june/august/october/july, best time … to avoid crowds, how many visitors…*.
- "glacier national park crowds" → 10: *by month, 2026, crowd calendar, is … crowded in july/august/september/june, least crowded*.
- "arches national park crowds" → 8: *by month, crowd calendar, is … crowded in october/september/march/april, peak season*.
- "zion crowds" → 10: *by month, today, reddit, october, in march, narrows, spring break*.
- "national park crowd calendar" → 10, con 9 parchi diversi (Zion, Yosemite, Yellowstone, Acadia, Sequoia, Glacier, Arches, Smoky Mountains, Rocky Mountain).
- "yellowstone visitation by month" → 8; "least crowded time to visit" → 10 (Yellowstone e Yosemite tra Disney, Giappone, Roma); "busiest national parks" → 10 (*in july, ranked, most visited*).
- Più deboli: "acadia crowds" 5, "great smoky mountains crowds" 5, "yosemite crowds by month" 4.

Lettura: la matrice parco × mese esiste davvero almeno per 6-8 parchi grandi. Per gli altri c'è "crowd calendar" o "by month". Le varianti "today" e "right now" non le copriamo: sono il dato "di oggi" che non abbiamo.

### Prima pagina di Google (ricerca web, 30/10/2026)
- "is rocky mountain national park crowded in september": blog (morethanjustparks, wereintherockies, jameskaiser), turismo locale (estes-park.com, visitestespark), notizie del 2019, un forum Fodor's e **`nestward.netlify.app`**. Quest'ultimo è il sito di un'app di viaggi con 253 guide scritte a mano senza numeri mensili: non è un motore di dati.
- "is yellowstone crowded in september": blog (outdoor-society, sightdoing, a-z-animals), forum (Fodor's, Good Sam, early-retirement), notizie 2015-2023.
- "zion national park crowd calendar": **nessun calendario**. Ci sono solo notizie sui fine settimana di festa (Fox Weather, KSL) e pagine spazzatura (`csr.hdsupply.com`) con cifre sbagliate (3,5 milioni di visite invece di circa 5).
- "glacier national park crowds by month": solo articoli del Flathead Beacon anno per anno. Nessuna tabella completa.
- Concorrente da rispettare: **Earthtrekkers**, un blog forte che ha tabelle "best time to visit" costruite sulle statistiche NPS degli ultimi quattro anni. Risponde a "best time", non a "is X crowded in [month]", e non ha una pagina per ogni mese. C'è anche `parks-decoded.pages.dev`, un sito generato in automatico, con poche pagine.

**Buco: reale ma non vuoto.** La domanda "best time to visit [parco]" è piena di blog autorevoli e non la consideriamo nostra. Le domande "crowded in [mese]" e "crowd calendar" sì.

### Chi paga (pagine lette il 30/10/2026)
| Programma | Condizioni lette | Stato | Momento giusto? |
|---|---|---|---|
| **DiscoverCars** | "$20 Average commission from booking", "3 - 5.5% Average Conversion Rate", cookie 365 giorni | 200 | sì: per quasi tutti i parchi dell'Ovest si vola e si noleggia |
| **RVshare** | "4% commission of the total booking value for every RV rental", "$900 average booking value", cookie 30 giorni | 200 | sì: viaggio tipico tra i parchi |
| **Viator** | "8% commission on any experience booked within 30 days", minimo 50 $ per bonifico | 200 | sì: escursioni guidate nei parchi |
| Stay22 (alberghi vicino al parco; già visto il 17/10) | quota delle commissioni delle agenzie | 200 | sì |
| Outdoorsy | pagina affiliati 403 dal server | 403 | da verificare |
| GetYourGuide | 403 | 403 | da verificare |
| AdSense | pubblico americano di viaggio; assunzione 6-12 € ogni 1.000 pagine viste con AdSense (le cifre di Empire Flippers, 55 $ per i viaggi con reti premium, divise per 2-3 e con le affiliazioni tolte) | – | sempre |

### Stima (assunzioni scritte)
- **Pagine:** 63 parchi × (1 + 12 mesi) = 819, più le altre unità NPS, 12 classifiche mensili e 50 Stati: circa 1.100-1.300 pagine.
- **Pagine viste al mese a 18 mesi** (media dell'anno; d'estate il doppio, d'inverno la metà): prudente 6.000, centrale 20.000, ottimista 60.000. Termine di paragone: EsameB1 con 77 pagine città ha circa 400 impressioni al giorno dopo 3 settimane e circa 810 visite al mese. Qui le pagine sono 15 volte di più e il pubblico è quello dei parchi più visitati del mondo (323 milioni di visite nel 2025).
- **Euro ogni 1.000 pagine viste:**

  | Ipotesi | AdSense | Affiliazioni (noleggio, camper, escursioni, alberghi) | Totale |
  |---|---|---|---|
  | prudente | 6 € | 5 € | 11 € |
  | centrale | 8 € | 12 € | 20 € |
  | ottimista | 10 € | 25 € | 35 € |

  Conto delle affiliazioni nell'ipotesi centrale: 1,5 % di clic sul noleggio × 3 % di conversione × 18 € = 0,8 € ogni 1.000; RVshare e Viator altrettanto; alberghi 8-10 €.
- **18 mesi, €/anno:** prudente 6.000 × 12 × 11/1.000 ≈ **800 €**; centrale 20.000 × 12 × 20/1.000 ≈ **4.800 €**; ottimista 60.000 × 12 × 35/1.000 ≈ **25.000 €**.
- **12 mesi:** 300 / 1.800 / 7.000 €.
- **Prima entrata:** AdSense già dal 1°-2° mese dopo l'indicizzazione. Le prime commissioni arrivano tra marzo e maggio 2027, quando si prenota l'estate. Il pagamento vero arriva 1-2 mesi dopo (Viator ogni settimana con PayPal; DiscoverCars ogni mese).
- **Stagione:** conviene pubblicare entro dicembre 2026, così a gennaio Google ha già visto le pagine.

### Ore (riusando i motori esistenti)
20-30 ore in tutto:
- **Raccolta (6-8 ore):** raccolta e generatore copiati dalla struttura di `cruisescores/`, cioè una pagina per entità con tabelle, voti e date (`raccolta/`, `genera.py`, `verifica.py`, `verifica_browser.js`). IRMA in 1 chiamata per parco e per anno; NOAA con la stazione più vicina a ogni parco, da scegliere una volta.
- **Pagine e testi a modello (8-12 ore):** parco, mese, classifiche, Stati.
- **Fatti datati a mano per 10 parchi (3-4 ore l'anno):** prenotazione a orario, strade.
- **Verifica, revisione indipendente, pubblicazione (4-6 ore).**

### Rischi
- Google mostra già le "ore di punta" dei luoghi in Maps, ma per ora e per giorno e non per mese: non è la stessa risposta.
- 819 pagine mese con poco testo possono sembrare sottili. Rimedio: ogni pagina mese ha almeno 4 numeri propri (visite, posizione, % del picco, temperature) e una frase che confronta con il mese prima e quello dopo.
- I dati 2026 entrano nel servizio solo a inizio 2027. Le pagine dicono "media 2021-2025, ultimo anno 2025" con la data.
- Il tetto dei siti nuovi fino a fine novembre: si parte a dicembre.

### Voto: 8
Griglia delle cacce precedenti:

| Voce | Punti |
|---|---|
| Domanda | 3/3 (matrice parco × mese in autocomplete, 10 varianti per i parchi grandi) |
| Buco | 1,5/2 (forum, notizie, spazzatura; Earthtrekkers forte solo su "best time") |
| Fonte | 2/2 (API pubblica, pubblico dominio, 46 anni di serie) |
| Soldi | 1,5/2 (quattro programmi con nome al momento della prenotazione; pubblico USA) |
| Rischi e ore | 0,5/1 (sito nuovo, stagionale) |

Non è 9 perché la stima prudente resta sotto i 1.000 € e il traffico non è provato.

**Soglie per confermare (proposta).** A 45 giorni dalla pubblicazione: almeno 300 impressioni al giorno e almeno 20 parchi con impressioni. A 120 giorni, cioè in piena stagione di prenotazione: almeno 5.000 visite al mese e almeno 10 clic su DiscoverCars o RVshare. Sotto le soglie si congela. Sopra, diventa 8,5 e si aggiungono i parchi canadesi (Parks Canada pubblica solo i totali annuali: da verificare) e le lotterie dei permessi (sez. 2.5).

---

## 2. Le altre candidate (sotto 8)

### 2.1 Piani Medicare Advantage che chiudono nel 2027, per assicuratore, Stato e contea (voto 6,5)
- **Fonte:** file "Plan Crosswalk 2027" della CMS (`cms.gov/files/zip/plan-crosswalk-2027.zip` → **200**, 676 KB, file del 1/10/2026, TXT e XLSX). Contiene 9.144 righe:

  | Stato del piano | Righe |
  |---|---|
  | Terminated/Non-renewed Contract | **1.006** |
  | New Plan | 928 |
  | Consolidated Renewal Plan | 808 |
  | Renewal Plan with SAR | 789 |
  | Renewal Plan with SAE | 546 |

  La contea si aggiunge con i file mensili di iscrizione per contratto, piano e contea (non scaricati oggi). Pubblico dominio.
- **Domanda:** "medicare advantage plans leaving" → 10 (*in 2026, in 2027, nh, vermont, florida, aetna…*); "aetna medicare advantage leaving" → 10 (*florida, illinois, georgia, what states…*). È la matrice assicuratore × Stato.
- **Google:** MoneyGeek ha già l'analisi per il 2027 ("67 counties will lose all general-enrollment plans"). Ci sono anche Becker's (elenchi degli assicuratori), `careroute.ai` (pagina "plans ending 2027"), Insurify e i giornali locali.
- **Soldi:** la pubblicità su Medicare paga molto negli USA, ma i contatti per Medicare sono regolati (regole CMS per chi fa marketing) e non ho trovato un programma con nome aperto a noi. Il tema è sanitario: la regola "medicina esclusa" del 9/10 è ancora da sciogliere.
- **Voto 6,5**, con una finestra di 7 settimane all'anno (15/10-7/12). Si può riprendere a settembre 2027 se Massimiliano scioglie il tema sanitario.

### 2.2 Sconti WUE sulle tasse universitarie per Stato e corso (voto 6; 7 con permesso)
- **Fonte:** la pagina `wiche.edu/tuition-savings/wue/wue-savings-finder/` → **200**, 2,7 MB. Ha dentro un JSON con 169 università, 13.694 corsi, retta WUE, scadenza della domanda (per esempio Boise State 9.527 $, scadenza 12/15/26). Simili: SREB Academic Common Market → 200, NEBHE Tuition Break → 200.
- **Licenza:** "personal, educational, and non-commercial purposes… strictly prohibited without prior written consent"; materiali con CC BY-NC-SA. **Blocca** (lezione del 23/10: la licenza si legge prima del voto).
- **Domanda:** "wue schools" → 10 (*list, tuition list, in california, for california residents, colorado, oregon, washington, with nursing programs, list 2026*); "academic common market" → 10 (*states, georgia, maryland, virginia, schools, tennessee*); "nebhe tuition break" → 3; MSEP → 3.
- **Soldi:** famiglie americane che scelgono l'università. AdSense istruzione nella media; prestiti agli studenti non verificati (il 28/10 le pagine affiliati di Credible e SoFi rispondevano 404).
- **Voto 6.** Sale a **7** con il permesso scritto di WICHE: una richiesta di licenza di 15 minuti, come quelle per OONI e ÖIF.

### 2.3 Filiali bancarie chiuse per banca, Stato e città (voto 6)
- **Fonte:** API FDIC `api.fdic.gov/banks/history?filters=CHANGECODE:721…` → **200**, pubblico dominio. 1.247 chiusure tra 1/10/2025 e 22/10/2026, con indirizzo e data, aggiornate ogni giorno (ultima elaborazione 28/10/2026). Banche con più chiusure:

  | Banca | Chiusure |
  |---|---|
  | JPMorgan Chase | 90 |
  | Wells Fargo | 80 |
  | Fifth Third | 67 |
  | Bank of America | 60 |
  | PNC | 53 |
  | TD | 53 |
  | Huntington | 46 |

- I preavvisi di 90 giorni stanno nel bollettino settimanale dell'OCC. Dal server le pagine indice e i PDF del 2026 rispondono **302 verso la home**; un PDF del 2025 ha risposto 200 una volta e vuoto la seconda. Quindi abbiamo solo le chiusure già avvenute, cioè la risposta a "è chiusa?" e non a "chiuderà?".
- **Domanda:** "chase branch closures" → 10; "td bank closing branches" → 10 (*in nj, in pa, list, 2026, massachusetts*); "bank of america closing branches" → 10 (*2026, massachusetts, florida, california*); "wells fargo branch closures" → 10. Metà riguarda però gli orari ("closing time", "closed today").
- **Google:** pagine spazzatura su sottodomini e notizie senza fonte. Ma **branchspot.com** fa già un "U.S. bank branch closure tracker" automatico dai dati FDIC (944 chiusure, pagine per Stato, riquadro "switch bank") ed è primo nella ricerca web.
- **Soldi:** i conti correnti pagano 50-300 $ a conto aperto secondo i blog del settore, ma **nessun programma con nome è stato letto** sulla pagina ufficiale. Resta AdSense finanza.
- **Voto 6.**

### 2.4 GED: costo e regole Stato per Stato (voto 6, da passare)
- **Domanda:** fortissima. "ged cost in" → 10 Stati; "how much does the ged cost in" → 10 Stati.
- **Google:** pieno di pagine spazzatura con cifre che si contraddicono. Per la Florida: 128 $ contro 152 $.
- **Fonte:** è un ente privato (GED Testing Service) più 50 dipartimenti statali; `ged.com` dal server dà 404 e 000.
- È un "esame obbligatorio per Stato": appartiene al ricercatore dei cloni di EsameB1. **Glielo segnalo invece di valutarlo.**

### 2.5 Lotterie dei permessi (Half Dome, The Wave, Enchantments, Mount Whitney, Angels Landing) (voto 5,5 da sola)
- **Domanda:** "half dome permit odds" → 9; "the wave lottery odds" → 7; "mt whitney lottery" → 10 (*2027, odds, dates, results*); "enchantments lottery odds" → 5; "angels landing permit odds" → 7.
- **Fonte:** frammentata, una pagina per ente. La pagina statistiche di Half Dome sul NPS arriva al 2023; blog e pagine spazzatura riportano percentuali diverse.
- **Solo come modulo della candidata 1**, dopo la soglia dei 120 giorni.

---

## 3. Scartate, con la prova (30/10/2026)

| Nicchia | Prova | Voto |
|---|---|---|
| Case di proprietà pubblica in vendita per Stato (HUD Home Store, HomePath, HomeSteps, USDA, VA) | Domanda forte ("hud homes for sale in" con 10 Stati, "government owned homes for sale"). Ma gli annunci di `hudhomestore.gov` si caricano da script (pagina 200 senza annunci nell'HTML) e in prima pagina ci sono hudhomestore, Zillow, Realtor e hudhomesusa.org (aggregatore a pagamento). Sono annunci che cambiano ogni giorno, non dati | 5 |
| Premi auto e casa per compagnia e città dalle indagini statali (California CDI, Texas HelpInsure) | Fonti 200 (`helpinsure.com`, CDI APEX). Ma "cheapest car insurance in fresno" e simili sono di Insurify, ValuePenguin, MoneyGeek con pagine per città; "california premium survey" ha autocomplete vuota. Conferma la famiglia "Florida per contea" (NO del 29/10) | 5 |
| Reclami per assicurazione in Texas (data.texas.gov) | API Socrata 200, ma la domanda per compagnia e Stato è piccola e l'indice NAIC sta già in ogni recensione (NO del 23/10) | 4,5 |
| Patti interstatali delle licenze (infermieri, counseling, assistenti sociali, PSYPACT, odontoiatri) | Domanda vera ("counseling compact states" 10, "social work compact states" 10, "psypact states" 10), ma ogni patto ha la sua mappa ufficiale che risponde prima; affiliazioni deboli (corsi di aggiornamento) | 5,5 |
| Reciprocità delle licenze per Stato (insegnanti, estetiste, agenti immobiliari, infermieri per endorsement) | Domanda enorme (10 varianti ciascuna), ma 50 enti × N professioni senza file unico (filtro duro), più i venditori di corsi (The CE Shop, Aceable, teach.org) in prima pagina | 4,5 |
| Animali esotici permessi Stato per Stato ("is it legal to own a raccoon/capybara/fox/otter…") | Domanda enorme, ma nessuna fonte ufficiale unica: 50 regolamenti in prosa (filtro duro) | 4,5 |
| Aumenti delle bollette per azienda elettrica ("duke energy rate increase 2026/2027" 10 varianti) | La risposta sta nelle decisioni delle 50 commissioni statali (nessun file unico); l'EIA dà solo la media annuale passata (findenergy.com già per azienda e città); "electricity rates by utility" 5 varianti | 5 |
| Tasse e oneri sul noleggio auto per Stato e aeroporto | "rental car taxes and fees by state (calculator)" esiste, ma nessuna fonte ufficiale unica (Stati + ~100 aeroporti) | 5 |
| Collaudo delle emissioni per Stato e contea | Domanda media ("emissions testing required in" 10 Stati), ma 30 programmi statali e dmv.org in prima pagina | 4,5 |
| Calendari delle immissioni di trote per Stato | "trout stocking schedule" 10 Stati, ma 50 agenzie ciascuna con la sua pagina, che è la risposta (stesso verdetto di pesca e caccia, 19/10) | 4,5 |
| Prezzi di propano e gasolio da riscaldamento per Stato (EIA) | Domanda per Stato (Maine, CT, NH) ma "near me/today": la gente vuole il prezzo del fornitore locale (aggregatori di rivenditori già primi); `api.eia.gov` 403 | 3,5 |
| Detrazione degli interessi sul prestito auto, modelli assemblati negli USA (riserva del 18/10) | **Riprova:** `nhtsa.gov` (Part 583) ancora **403**; l'API vPIC risponde 200, ma la fabbrica si legge solo per singolo numero di telaio, non per modello. La riserva resta com'è | 6 (invariato) |
| Fonti federali provate per altre idee | `bls.gov` 403, `travel.state.gov` 403 (vincolo noto), `huduser.gov` 202 vuoto, `api.eia.gov` 403; aperte invece `data.cms.gov`, `collegescorecard.ed.gov`, `fhfa.gov`, `eia.gov` (pagine), `api.nhtsa.gov`, `fueleconomy.gov` | – |

---

## 4. Righe proposte per ESPLORATE (questo rapporto non modifica quel file)

| Nicchia | Esito | Studio |
|---|---|---|
| **Affollamento dei parchi nazionali USA mese per mese** (NPS IRMA 200 dal 1979, NOAA normali 200; "is [park] crowded in [month]" e "crowd calendar") | **PASSA** (voto 8; 800 / 4.800 / 25.000 €/anno a 18 mesi; 20-30 ore; sito nuovo da dicembre) | ricerca-zona-usa-2026-10-30 |
| Piani Medicare Advantage che chiudono nel 2027 (CMS crosswalk 1/10/2026, 1.006 piani) | RISERVA (6,5): tema sanitario, MoneyGeek e Becker's, finestra 15/10-7/12 | ricerca-zona-usa-2026-10-30 |
| Sconti WUE / Academic Common Market / Tuition Break | RISERVA (6; 7 con il permesso scritto di WICHE: licenza non commerciale) | ricerca-zona-usa-2026-10-30 |
| Filiali bancarie chiuse per banca e Stato (FDIC) | RISERVA (6): branchspot.com già automatico, OCC chiuso al server, nessun programma bancario letto | ricerca-zona-usa-2026-10-30 |
| GED costo per Stato | passata al ricercatore dei cloni di EsameB1 (6) | ricerca-zona-usa-2026-10-30 |
| Lotterie dei permessi dei parchi | solo modulo dei parchi (5,5) | ricerca-zona-usa-2026-10-30 |
| Case pubbliche in vendita, premi assicurativi statali, reclami Texas, patti delle licenze, reciprocità, animali esotici, aumenti delle bollette, tasse del noleggio, emissioni, trote, propano | NO (sez. 3) | ricerca-zona-usa-2026-10-30 |

---

## 5. Prossimi passi proposti (zero spese)

1. **Decisione di Massimiliano:** sì o no al sito dei parchi come primo sito nuovo di dicembre.
2. **Iscrizioni** (10-20 minuti ciascuna, nessun traffico minimo scritto): RVshare e Viator. DiscoverCars e Stay22 sono già nel piano del 28/10. La chiave gratuita dell'API NPS è facoltativa.
3. **Costruzione:** 20-30 ore, motore di `cruisescores/`. Prima pubblicazione con i 63 parchi e i 12 mesi; le altre unità NPS e gli Stati nella seconda.
4. **Richiesta di licenza a WICHE** (facoltativa, 15 minuti): uso commerciale con attribuzione dei dati WUE.

---

## 6. Fonti lette il 30/10/2026 (stato HTTP dal nostro server)

| Fonte | Stato |
|---|---|
| `irmaservices.nps.gov/v3/rest/stats/visitation?unitCodes=YELL,ZION,ROMO,GLAC,ARCH…` (1979, 2024-2025; 2026 vuoto) | 200 |
| `irmaservices.nps.gov/v3/rest/stats/total/2025` | 200 |
| `irmaservices.nps.gov/v3/rest/stats/traffic…` | 404 |
| `irma.nps.gov/Stats/` | 200 (pagina in JavaScript) |
| `developer.nps.gov/api/v1/parks` | 403 (chiave gratuita mancante) |
| `ridb.recreation.gov/api/v1/facilities` | 401 |
| `recreation.gov/api/permits/…/availability` | 404 |
| `ncei.noaa.gov/access/services/data/v1?dataset=normals-monthly-1991-2020` | 200 |
| `nps.gov/yose/planyourvisit/visitation.htm` | 200 |
| `nps.gov/romo/planyourvisit/timed-entry-permit-system.htm` | 200 |
| `nps.gov/arch/planyourvisit/timed-entry-reservations.htm` | 404 |
| `discovercars.com/affiliate` | 200 |
| `rvshare.com/affiliates` | 200 |
| `partnerresources.viator.com` | 200 |
| `stay22.com` | 200 |
| `outdoorsy.com/affiliate(s)` | 403 |
| `getyourguide.com/c/partner/` | 403 |
| `hipcamp.com/en-US/affiliates` | 404 |
| `nestward.netlify.app` (concorrente; sitemap 253 guide) | 200 |
| `cms.gov/…/plan-crosswalks/2027-part-cd-plan-crosswalk` e `cms.gov/files/zip/plan-crosswalk-2027.zip` | 200 |
| `wiche.edu/tuition-savings/wue/wue-savings-finder/` | 200 |
| `wiche.edu/copyright-and-use/` | 200 |
| `sreb.org/academic-common-market` | 200 |
| `nebhe.org/tuitionbreak/` | 200 |
| `api.fdic.gov/banks/history` | 200 |
| `api.fdic.gov/banks/locations` | 200 |
| `branchspot.com/bank-branches-closed/` | 200 |
| `occ.gov` / `occ.treas.gov` bollettino settimanale 2026 | 302 verso la home |
| PDF OCC del 2025 | 200 la prima volta, vuoto la seconda |
| `hudhomestore.gov` (ricerca GA) | 200, annunci da script |
| `homepath.fanniemae.com`, `homesteps.com`, `properties.sc.egov.usda.gov`, `vrmproperties.com` | 200 |
| `ged.com/about_test/test_cost/` | 404 |
| `ged.com/en/curriculum/state-requirements/` | 000 |
| `helpinsure.com` | 200 |
| `interactive.web.insurance.ca.gov` | 200 |
| `insurance.ca.gov` (guide auto) | 200 |
| `data.texas.gov` (reclami assicurativi) | 200 |
| `nhtsa.gov` (Part 583) | 403 |
| `vpic.nhtsa.dot.gov` | 200 |
| `api.nhtsa.gov` | 200 |
| `fueleconomy.gov` | 200 |
| `travel.state.gov` | 403 |
| `bls.gov` | 403 |
| `data.cms.gov` | 200 |
| `collegescorecard.ed.gov` | 200 |
| `eia.gov/electricity/data/eia861m/` | 200 |
| `api.eia.gov` | 403 |
| `fhfa.gov` | 200 |
| `huduser.gov` (FMR) | 202 vuoto |

Ricerche web (risultati come da un computer negli USA): "Chase branch closures 2026 list by state", "zion national park crowd calendar", "glacier national park crowds by month visitation statistics", "crowd calendar national parks monthly visitation every park", "is rocky mountain national park crowded in september", "is yellowstone crowded in september", "half dome lottery odds 2026", "how much does the ged cost in florida 2026", "medicare advantage plans terminated 2027 list by state county", "OCC weekly bulletin branch closings October 2026", programmi affiliati per i conti correnti (solo blog, nessuna pagina ufficiale).
