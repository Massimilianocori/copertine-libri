# Caccia serale del 30/10/2026: animali domestici (viaggiare con cane e gatto, razze, tasse, licenze)

Settore nuovo per la rotazione delle cacce serali: **animali domestici nel mondo**. Stesso modello di sempre: pagine gratuite costruite e aggiornate in automatico da fonti ufficiali, costo zero, niente vendita diretta, niente email a freddo, niente social. Asticella: per un **sito nuovo** voto ≥ 7 e ≥ 5.000 €/anno a 18 mesi; per una **sezione** di un sito esistente basta che sia automatica, a costo zero e con guadagno atteso positivo (regola "rete fitta" del 30/10).

**Già valutato e NON rifatto** (da `ESPLORATE.md`): "Pet travel rules" dello studio 1 (RISERVA, 5/5 con riserve); animali in cabina per compagnia aerea (NO, 19/10); tassa sul cane in Germania e Paesi Bassi (NO, 16/10); animali esotici Stato per Stato USA (NO, 30/10 zona USA); costo per portare il cane in Australia/NZ/USA (NO 4, 30/10 numeri ufficiali: fonti 000/403); prezzi dei veterinari UK per catena e città (6,5 → 8 condizionato, 30/10 zona UK: controllo a gennaio 2027). Dove una prova di stasera tocca queste idee lo scrivo.

**Fatti nuovi che giustificano la riapertura parziale dello studio 1** (regola di ESPLORATE: si riapre solo se cambia un fatto):
1. **Regole UE nuove e leggibili dal server**: dal 22/4/2026 vale il Regolamento delegato (UE) **2026/131**; le liste dei Paesi esenti dal test degli anticorpi della rabbia sono negli allegati I e II del Regolamento di esecuzione (UE) **2026/636**; il modello di certificato è nel Reg. (UE) **2026/705**. La pagina della Commissione con la lista è in HTML (200), modificata il 7/7/2026; la pagina "Bringing a pet into the EU from a non-EU country" è stata modificata **oggi, 30/10/2026**.
2. **Tabella ufficiale britannica delle compagnie aeree e dei porti** autorizzati a far entrare cani e gatti in Gran Bretagna: HTML, **630 righe** (compagnia → aeroporto e centro di accoglienza animali), più 35 righe di rotte via mare e treno; aggiornata il **23/10/2026**; licenza OGL.
3. **Data in arrivo**: il governo britannico scrive che l'accordo veterinario con l'UE (SPS) "will take effect in **mid-2027**" e che allora i proprietari potranno avere di nuovo un **passaporto per animali valido più volte** per l'UE, invece di un certificato sanitario (AHC) per ogni viaggio. Dal 22/4/2026 i britannici non possono più usare il passaporto UE del loro animale per entrare nell'UE.

**Prove:** tutte del 30/10/2026, sera. `curl` dal server (stato HTTP e dimensione), API dei contenuti di GOV.UK, Google Autocomplete (`suggestqueries.google.com`, `client=firefox`, con `gl`/`hl` scritti accanto: gb/en, us/en, au/en, nz/en, ca/en, ae/en, in/en, ph/en, de/de; circa 90 interrogazioni), ricerca web per la prima pagina di Google (mostrata come da un computer negli USA), mappe dei siti dei concorrenti.
**Limiti:** niente Keyword Planner (l'autocomplete dice quali varianti esistono, non quante ricerche); le commissioni delle assicurazioni per animali vengono da elenchi di terzi, non dalle pagine ufficiali, salvo dove scritto; l'accettazione di un affiliato italiano non si può verificare senza un account (si vede solo alla domanda d'iscrizione).
**Chiusi o muti dal server stasera:** `cdc.gov/importation/dogs` 403 (regole cani USA 2024), `aphis.usda.gov/pet-travel` 403, `agriculture.gov.au` 000 (Australia), `mpi.govt.nz` 212-849 byte in JavaScript (Nuova Zelanda), `moccae.gov.ae` 245 byte (Emirati), `nparks.gov.sg` 404 sul percorso provato (Singapore), `gov.ie` 403 (Irlanda), `eur-lex.europa.eu` 202 vuoto (controllo anti-robot), `poferries.com` 403, `sbb.ch` 403; percorsi indovinati 404 per SNCF Connect, Deutsche Bahn, Renfe, NS, Eurostar, DFDS. Dei 34 siti nazionali elencati dalla Commissione per le regole dei singoli Paesi UE, **17 rispondono 200**, 15 danno 000, 2 danno 403 (Irlanda, Lituania).

---

## 0. Risposta in breve

Ho guardato **15 spunti** (8 analizzati, 7 chiusi in fretta). **Nessuno passa l'asticella di un sito nuovo** (il migliore arriva a 7, ma senza un pagatore con cifra alta). **Tre diventano sezioni da costruire** dentro Before You Fly, che ha già le pagine per Paese, i passaporti e il blocco "Before you drive":

| # | Idea | Dove vivrebbe | Esito | Voto | Primi soldi | 18 mesi (lordo, all'anno) | Ore |
|---|---|---|---|---|---|---|---|
| 1 | **Dal Regno Unito all'UE con cane o gatto**: certificato AHC oggi, **passaporto britannico dal 2027** (pagina che segue la data), regole in più per Paese (verme solitario per Irlanda, Finlandia, Malta, Norvegia), **traghetti ed Eurotunnel con l'animale** (rotte ufficiali GOV.UK), ritorno in Gran Bretagna | Sezione "Pets" di Before You Fly | **SEZIONE da costruire** | **7** (7,5 con Direct Ferries iscritto) | 2°-3° mese (AdSense); traghetti dopo l'iscrizione | **400-1.000 €** prudente, ~1.500 centrale, **5.000 ottimista** (ondata del passaporto 2027) | 16-24 |
| 2 | **Portare il cane in Gran Bretagna in aereo: quali compagnie e quali aeroporti** (tabella ufficiale di 630 righe), da quali Paesi serve l'esame del sangue, quali documenti; una pagina per compagnia ("Can I fly my dog to the UK with Emirates?") e per Paese di partenza | Sezione "Pets" di Before You Fly | **SEZIONE da costruire** | **7** | 3°-4° mese (AdSense) | **300-700 €** prudente, ~1.000 centrale, 3.000 ottimista | 12-18 |
| 3 | **Entrare nell'UE con il cane da ogni Paese del mondo: serve il test della rabbia e l'attesa di 3 mesi?** (liste ufficiali 2026/636: 9 Paesi all. I + 51 all. II esenti; tutti gli altri no), con il **calcolatore delle date** (vaccino → prelievo → primo giorno utile) | Sezione "Pets" di Before You Fly (dopo la 1 e la 2) | **SEZIONE, in coda** | **6** | 3°-6° mese | **200-600 €** prudente, ~900 centrale, 3.000 ottimista | 20-30 (+6-8 il calcolatore) |

Le altre cinque analizzate restano in riserva o chiuse: destinazioni con quarantena (Giappone, Hawaii, Australia, NZ, Singapore, Emirati) 5; razze vietate per Paese 5; cani sui treni europei 5; regole CDC per i cani negli USA 4,5 (fonte chiusa); assicurazioni per animali come pagatore (non è un'idea, è il modo di guadagnare: cifre non verificate). Chiusi in fretta: tassa sul cane (non riaperta), licenze per cani per contea USA, spiagge per cani UK, parchi nazionali USA con il cane, regole delle auto a noleggio per gli animali, legge sul microchip dei gatti, hotel per cani.

**Perché nessuna supera i 5.000 €.** La domanda c'è ed è ampia (decine di rotte "bringing dog to X from Y" con 10 varianti), ma: (a) **chi paga è debole**: le aziende di trasporto animali (PetRelocation, Starwood, Pet Air UK) non hanno programmi di affiliazione aperti; le assicurazioni per animali pagano bene sulla carta (20-40 £ a polizza secondo elenchi di terzi) ma solo per il pubblico britannico o americano e con cifre non lette sulle pagine ufficiali; Amazon paga circa il 3 % sugli articoli per animali (USA); l'unico pagatore con regola letta su pagina ufficiale è **Direct Ferries** ("50% of the commission we receive from the ferry operators"); (b) la prima pagina è già occupata da **PetRelocation** (pagina per ogni Paese), da siti automatici (**entrybrief.com** 200 pagine Paese, **zoovettravel.com** 156 pagine "atlas", **tailharbor.eu** rotte Paese → Paese, **petholidayclub.com** 499 pagine con abbonamento a 24 $/mese) e dai giornali per espatriati (Connexion, idealista, The Local); (c) un errore costa caro (animale respinto o in quarantena), quindi ogni pagina deve avere fonte, data di controllo e avviso.

**Cosa farei:** una sezione **"Pets" in Before You Fly**, in quest'ordine: n. 1 (pronta **prima della primavera 2027**, quando i britannici prenotano le vacanze estive, e aggiornata quando GOV.UK pubblica la data del passaporto), poi n. 2 (fonte che cambia ogni poche settimane: vantaggio dell'aggiornamento automatico), poi n. 3 col calcolatore. Insieme: **900-2.300 € prudenti**, ~3.400 centrali, ~11.000 ottimisti, 55-80 ore. A Massimiliano non si scrive (nessun sito nuovo); entra nella coda di costruzione. Da chiedergli solo l'iscrizione a **Direct Ferries** (gratuita) quando la n. 1 è online.

---

## 1. I 15 spunti e l'esito

Voto da 0 a 10: domanda (0-3), risultati di Google deboli (0-2), fonte ufficiale leggibile e stabile (0-2), valore del pubblico e guadagni (0-2), rischi e lavoro (0-1).

| # | Spunto | Esito | Motivo in una riga (prove del 30/10/2026, sera) |
|---|---|---|---|
| 1 | Dal Regno Unito all'UE con l'animale: AHC, passaporto 2027, traghetti ed Eurotunnel | **SEZIONE (7)** | Vedi sez. 2 |
| 2 | In Gran Bretagna in aereo con il cane: compagnie e aeroporti autorizzati | **SEZIONE (7)** | Vedi sez. 3 |
| 3 | Entrare nell'UE da ogni Paese: test della rabbia sì o no, calcolatore delle date | **SEZIONE in coda (6)** | Vedi sez. 4 |
| 4 | Destinazioni con quarantena o attesa lunga (Giappone 180 giorni, Hawaii, Australia, NZ, Singapore, Emirati) | **RISERVA (5)** | Domanda forte (us/en "bringing dog to japan" 10, "bringing dog to hawaii" 10 con quarantine e checklist; au/en "bringing dog to australia from" 10 con philippines, uk, usa, india; nz/en 10; "dog quarantine cost" 10 con australia, nz, singapore). Fonti: Giappone MAFF **200** (regioni designate: Islanda, Australia, NZ, Figi, Hawaii, Guam; altrimenti due vaccini, esame del sangue e **180 giorni** di attesa), Hawaii **200**, Canada CFIA **200**; ma Australia **000**, NZ in JavaScript, Singapore 404, Emirati 245 byte, USA 403: metà delle destinazioni chiuse (filtro duro). Il costo australiano era già NO il 30/10. Al massimo pagine Giappone e Hawaii dentro la sez. 4 |
| 5 | Razze di cani vietate o limitate, Paese per Paese, per chi viaggia o si trasferisce | **RISERVA (5)** | Domanda vera (us/en "banned dog breeds in" → uk, germany, us, california, texas, japan, france, norway, south korea; gb/en → india, malaysia, australia, singapore, ontario; "xl bully ban uk" 10). Fonti: GOV.UK "banned dogs" 200 (API JSON), dogana tedesca (`zoll.de`, pagina per Land, in prima pagina), ma 16 Länder con liste proprie, Francia 000, Danimarca e Norvegia 000/404; dei 34 siti nazionali indicati dalla Commissione solo 17 rispondono. Prima pagina: PetRelocation, zoovettravel, recordinglaw (16 liste dei Länder), Wikipedia, t-online. Pubblico che vale (chi ha un pitbull o un bull terrier e si trasferisce), ma nessun pagatore: al massimo un riquadro "razze" nelle pagine Paese della sez. 4 |
| 6 | Portare il cane negli USA: regole CDC dal 1/8/2024, Paesi ad alto rischio rabbia, modulo CDC | **NO dal server (4,5)** | Domanda forte (us/en "cdc dog import" 10 con form, receipt, canada; "bringing dog to us from" 10 con canada, mexico, japan, uk, europe, korea, philippines; ph/en "bringing dog to usa from philippines"). Ma `cdc.gov/importation/dogs` **403** e `aphis.usda.gov` **403**; il Federal Register (200) ha il testo della regola ma non la lista aggiornata dei Paesi. Si riapre solo se cdc.gov si legge dal browser di Massimiliano (come per travel.state.gov) |
| 7 | Cani sui treni in Europa, compagnia per compagnia (biglietto, museruola, orari) | **RISERVA (5)** | Domanda per Paese (gb/en "dogs on trains in" → europe, spain, france, italy, uk, germany, switzerland, portugal, ireland; "eurostar dog" 10: Eurostar non accetta animali salvo cani guida). Ma sono **condizioni commerciali** delle compagnie, come gli animali in cabina (NO il 19/10): Trenitalia 200 ma i prezzi non sono nel testo statico, SBB 403, SNCF/DB/Renfe/NS/Eurostar 404 sui percorsi provati. Prima pagina: italiarail, showmethejourney, Euronews, siti di guide. Al massimo 6-8 pagine dentro la sez. 2 come "dopo il traghetto" |
| 8 | Assicurazione per animali come pagatore (ManyPets, Petplan, PDSA, Everypaw, Lemonade, Embrace, Trupanion) | **Non è un'idea: è il modo di guadagnare delle sez. 2-4** | Cifre **non verificate** sulle pagine ufficiali: ManyPets 20-40 £ a polizza (LinkClicky; rete contesa tra Impact e Partnerize), PDSA 25 £ al lancio su Awin (rapporto zona UK del 30/10), Embrace 36 $ a contatto ma altri elenchi dicono 1,60-5 $, Trupanion 25 $, Lemonade solo su Impact (già annotato il 17/10: Awin chiuso). Accettazione di un affiliato italiano: Awin accetta editori italiani (account già previsto per Holiday Extras), ma ogni assicuratore decide alla domanda. Domanda gb/en "pet travel insurance" 10 (uk, single trip, europe), us/en "pet insurance for travel" 10 |
| 9 | Tassa sul cane per Comune in Germania (Hundesteuer) | **Non riaperta** | Già NO il 16/10 (circa 10.700 regolamenti, nessuna fonte unica). Stasera de/de "hundesteuer" ha sempre le grandi città (berlin, münchen, hamburg, köln, leipzig, dortmund, paderborn), ma nessun fatto nuovo sulla fonte |
| 10 | Licenza del cane per contea o città negli USA (costo) | **NO (3)** | Domanda sparsa (us/en "dog license fee" → california, pennsylvania 2026, ohio; "dog license cost" → los angeles, costa mesa, calgary, ireland, singapore), ma migliaia di contee e città, ognuna risponde da sé; vale poco (10-30 $); filtro duro |
| 11 | Spiagge con divieto per i cani in estate, per Comune (UK) | **NO (3,5)** | gb/en "dogs on beaches" 10 (cornwall, jersey, wales, swansea, st ives), ma decine di consigli comunali con ordinanze diverse; siti turistici e dei consigli già primi |
| 12 | Parchi nazionali USA dove il cane è ammesso | **NO (3)** | us/en "dog friendly national parks" 10 (california, utah, colorado, texas, map), ma risponde l'ente (nps.gov, pagina pets per parco) e BringFido; stesso verdetto dei parchi NPS del 14/10 |
| 13 | Regole e costi degli animali nelle auto a noleggio, compagnia per compagnia | **NO (4)** | us/en "rental car with dog" 10, ma "pet fee rental car" solo 4 varianti; condizioni commerciali; DiscoverCars poco pertinente (chi viaggia con il cane di solito usa la sua auto) |
| 14 | Legge sul microchip dei gatti (UK, dal 10/6/2024) e costo della registrazione | **NO (2,5)** | gb/en "cat microchip law" 10 (england, wales, scotland, 2024), ma una regola sola che GOV.UK spiega già; i costi sono prezzi dei veterinari e delle banche dati private (rientrano nell'idea veterinari UK di gennaio 2027) |
| 15 | Hotel e alloggi che accettano cani, per città | **NO (3)** | Domanda enorme ma nessun dato ufficiale; BringFido, Booking con il filtro, Airbnb |

---

## 2. N. 1 — Dal Regno Unito all'UE con cane o gatto: AHC oggi, passaporto nel 2027, traghetti ed Eurotunnel (SEZIONE, voto 7)

**L'idea in una riga.** Dentro Before You Fly, una pagina che segue la data ("UK pet passport 2027: when it starts and what to do until then") e 25-30 pagine "Taking your dog from the UK to [Paese UE]" con: documento richiesto oggi (AHC: "valid for travel any time within 10 days after it's issued", fino a 5 animali per certificato, GOV.UK), vaccino e 21 giorni, trattamento contro il verme solitario dove serve (Irlanda, Finlandia, Malta, Norvegia, Irlanda del Nord) e per il ritorno, punti di ingresso ufficiali del Paese, razze limitate se la fonte nazionale risponde, e le **rotte via mare e treno autorizzate** (tabella GOV.UK) con il riquadro traghetti.

**Domanda (gb/en).** "taking dog to france" 10 (from uk, rules, on holiday, eurotunnel, requirements, france and spain); "animal health certificate" 10 (cost, near me, online, folkestone); "ahc cost" 10 (vets for pets, pets at home, london); "pet passport uk" 10 (price, to france, to ireland, to eu, coming back, update, **2027**); "uk pet passport 2027" 5 (cost, requirements, new pet passport rules uk); "dog to ireland from" 10; "eurotunnel dog" 10 (rules, cost, check in); "ferry with dog to" 10 (spain, france, ireland, santander); "dog friendly ferry" 10 (to france, to ireland, uk to spain, to amsterdam); "tapeworm treatment for dogs travelling" 9 (to uk, to ireland, to france, cost).

**Fonte.**
| Fonte | Stato dal server | Licenza | Cosa dà |
|---|---|---|---|
| GOV.UK "Taking your pet dog, cat or ferret abroad" (`/api/content/taking-your-pet-abroad`) | 200, JSON 41 KB | OGL | AHC, microchip, vaccino, verme solitario, Irlanda del Nord |
| GOV.UK "Bringing your pet to Great Britain" (`/api/content/bring-pet-to-great-britain`) | 200, JSON 79 KB | OGL | Ritorno: documenti, Paesi esenti dal verme solitario |
| GOV.UK "SPS agreement: veterinary sector" | 200 | OGL | "mid-2027", "multiuse pet passport valid for EU travel" |
| GOV.UK rotte via mare e treno autorizzate | 200, 35 righe (es. "Calais to Dover: DFDS Seaways, Irish Ferries, P&O Ferries"; "Caen to Portsmouth: Brittany Ferries") | OGL | Quale compagnia accetta animali su quale rotta |
| Commissione UE, punti di ingresso e pagine nazionali | 200; 17 siti nazionali su 34 rispondono | Riutilizzo con citazione (decisione 2011/833/UE) | Regole in più per Paese |
| Eurotunnel (pagina animali), Brittany Ferries (pagina animali) | 200 / 200 (prezzi non letti nel testo statico) | Condizioni commerciali | Prezzo dell'animale a bordo (da leggere con il browser) |

**Prima pagina di Google ("uk pet passport 2027 …").** Connexion France (tre articoli), wamiz, Pet Holiday Club (articolo sul ritorno del passaporto), STV, IBTimes, Euro Weekly News, petizione su change.org, GOV.UK. Tutti articoli con una data; **nessuna pagina che segue la data e si aggiorna da sola**, nessuna pagina "UK → [Paese]" che metta insieme AHC, verme solitario, razze e traghetti. Per "taking dog to france from uk": GOV.UK, Eurotunnel/LeShuttle, Brittany Ferries, blog.

**Chi paga.**
- **Direct Ferries**: pagina ufficiale `directferries.com/affiliate.htm` (200): "For every confirmed ferry booking (for a ferry that sailed) you can earn 50% of the commission we receive from the ferry operators". La percentuale di Direct Ferries non è pubblica; gli elenchi di terzi dicono 2-4 % sul prezzo (CJ, Tradedoubler, FlexOffers). Un traghetto con auto Dover-Calais o Portsmouth-Caen costa 100-600 £: **2-15 £ a prenotazione**, stima.
- Assicurazione per animali (sez. 1, n. 8): cifre non verificate.
- AdSense britannico (viaggi, animali).
- Collegamento con l'idea dei **prezzi dei veterinari UK** (gennaio 2027): se le liste CMA comprendono l'AHC, la pagina "AHC cost" diventa la tabella per catena.

**Stima a 18 mesi.** Prudente 400-1.000 €/anno (2.000-4.000 visite al mese in estate, metà in inverno; AdSense 8-12 € ogni 1.000 pagine; 10-30 prenotazioni di traghetto l'anno). Centrale ~1.500. Ottimista **5.000** se la pagina del passaporto 2027 si posiziona nell'ondata di ricerche quando il governo annuncia la data.
**Ore.** 16-24, riusando le pagine Paese di Before You Fly, il motore dei consigli di viaggio GOV.UK e il blocco "Before you drive".
**Rischi.** La data del 2027 non è confermata ("It is our intention"): la pagina deve dirlo e mostrare la frase ufficiale con la data di controllo. Errori costosi: avviso e link alla fonte in ogni pagina.
**Voto 7** (domanda 2,5; Google 1; fonte 1,5; guadagni 1,5; rischi 0,5). 7,5 con Direct Ferries iscritto.

---

## 3. N. 2 — In Gran Bretagna in aereo con il cane: quali compagnie e quali aeroporti (SEZIONE, voto 7)

**L'idea in una riga.** La tabella ufficiale GOV.UK "Pet travel: airlines and airports you can use" (630 righe: compagnie commerciali e charter, ciascuna con gli aeroporti britannici e il centro di accoglienza animali, per esempio "Air Canada → Edinburgh, London Heathrow (HARC), Manchester (Pets on Jets)") trasformata in: una pagina per compagnia ("Can I fly my dog to the UK with Air Canada?": sì, in stiva, verso questi aeroporti), una per aeroporto britannico, una per i principali Paesi di partenza (USA, Canada, Australia, India, Filippine, Thailandia, Polonia, UE) con documenti, esame del sangue sì o no, e la regola chiave: **in cabina si entra in Gran Bretagna solo con i cani d'assistenza** (tabella a parte, sempre GOV.UK). Si aggiorna da sola: la pagina è cambiata il 23/10/2026.

**Domanda.** us/en "flying dog to uk" 10 (from usa, from australia, from canada); gb/en "pet friendly airlines to uk" 10 (uk to usa, uk to australia, dog friendly flights to uk); "bringing dog to uk from" 10 (usa, eu, poland, ireland, canada, france, philippines, europe, india, thailand), uguale da gb e us; "pet passport usa to uk" e "pet passport usa to uk requirements".

**Prima pagina di Google ("which airlines fly dogs into UK …").** GOV.UK stessa, Pet Air UK (venditore), airport.online, Heathrow FAQ, PPRuNe (forum), copie delle versioni vecchie di GOV.UK su siti che registrano le modifiche. **Nessuna pagina per compagnia** che dica "sì, verso questi aeroporti".

**Chi paga.** Solo AdSense (pubblico USA/UK/AU che vale) e, nelle pagine Paese, l'assicurazione per animali. I trasportatori di animali (Pet Air UK, PetRelocation) non hanno programmi aperti. Debole: per questo 7 e non di più.
**Stima a 18 mesi.** Prudente 300-700 €/anno; centrale ~1.000; ottimista 3.000.
**Ore.** 12-18 (una tabella HTML, una pagina per riga raggruppata; controllo settimanale delle modifiche).
**Voto 7** (domanda 2; Google 1,5; fonte 2; guadagni 1; rischi 0,5).

---

## 4. N. 3 — Entrare nell'UE con il cane da ogni Paese: test della rabbia e attesa, con il calcolatore delle date (SEZIONE in coda, voto 6)

**L'idea in una riga.** Per ogni Paese di partenza (circa 190) una pagina "Bringing a dog to the EU from [Paese]": se il Paese è negli allegati I o II del Reg. (UE) 2026/636 (oggi 9 + 51, tra cui USA, Canada, Regno Unito, Australia, Giappone, Messico, Emirati, Malesia, Singapore, Taiwan, Serbia) **niente esame del sangue**; altrimenti (India, Filippine, Thailandia, Brasile, Turchia, Sudafrica, Corea del Sud, Cina, Egitto, Marocco, Ucraina, Russia…) **esame del sangue almeno 30 giorni dopo il vaccino e certificato non prima di 90 giorni dal prelievo**, in un laboratorio della lista UE. Più le pagine per le prime destinazioni (Germania, Spagna, Portogallo, Francia, Italia, Paesi Bassi, Irlanda) con le regole nazionali dove la fonte risponde, e il **calcolatore** "il mio cane quando può entrare?" (data del vaccino → primo prelievo utile → primo giorno di ingresso), con le stesse regole per Gran Bretagna, Giappone (180 giorni) e Hawaii.

**Domanda.** us/en "bringing dog to germany from" 10 (us, canada, philippines), "bringing dog to spain from" 10, "to portugal from" 7, "to france from" 10, "to italy from us" 9, "taking dog to europe from us" 7, "moving to europe with a dog" 10; in/en "can i take my dog to europe from india"; "rabies titer test for" 10 (international travel, hawaii, cost), "rabies titer test eu" 6 (how long, valid); "eu pet health certificate" 10 (pdf, form, cost); "rabies free countries list" 6 (eu list, cdc list, woah list).

**Prima pagina di Google.** Per "bringing dog to spain from usa": PetRelocation (6 risultati), movingtospain, myspainvisa, idealista (2026), worldcarepet, tailharbor (PDF per rotta), spainguru, **entrybrief.com/pets/spain**, The Local. Per "rabies titer test required countries EU": Starwood, Commissione UE, Baviera, petraveller, pettravel.com, travelnuity, BMEL, dogana francese, **zoovettravel.com** (atlas 2026). **Concorrenti automatici presenti**: entrybrief (200 pagine Paese di arrivo), zoovettravel (156 pagine), tailharbor (rotte Paese → Paese), Pet Holiday Club (499 pagine e abbonamento). Il buco è più stretto di quanto credeva lo studio 1.

**Fonte.** Commissione UE: lista dei Paesi esenti (200, HTML, all. I e II del Reg. 2026/636), condizioni (200, modificata il 30/10/2026), punti di ingresso (200), laboratori (200). EUR-Lex 202 vuoto dal server (si usa la pagina della Commissione). Riutilizzo con citazione della fonte.
**Chi paga.** AdSense USA/UK; assicurazione per animali solo per i pubblici britannico e americano; Amazon (trasportini omologati, circa 3 % negli USA). Debole.
**Stima a 18 mesi.** Prudente 200-600 €/anno; centrale ~900; ottimista 3.000.
**Ore.** 20-30, più 6-8 per il calcolatore.
**Voto 6** (domanda 2; Google 0,5; fonte 2; guadagni 1; rischi 0,5).

---

## 5. Sezioni da costruire (rete fitta: automatiche, costo zero, guadagno positivo)

Tutte dentro **Before You Fly**, nuova sezione `pets/`, con AdSense e il link adatto. Ordine per guadagno atteso per ora:

| Ordine | Sezione | Pagine | Stima prudente / centrale / ottimista (€/anno a 18 mesi) | Ore | Quando | Serve da Massimiliano |
|---|---|---|---|---|---|---|
| 1 | UK → UE con l'animale + "UK pet passport 2027" + traghetti ed Eurotunnel | ~30 | 400-1.000 / 1.500 / 5.000 | 16-24 | Online entro febbraio 2027 (prenotazioni estive) | Iscrizione gratuita a Direct Ferries quando è online |
| 2 | In Gran Bretagna in aereo: compagnie e aeroporti autorizzati (+ cani d'assistenza) | ~120 | 300-700 / 1.000 / 3.000 | 12-18 | Dopo la 1 | Niente |
| 3 | Entrare nell'UE da ogni Paese + calcolatore delle date | ~200 | 200-600 / 900 / 3.000 | 26-38 | Dopo la 2 | Niente |
| 4 (piccola) | Riquadro "razze limitate" nelle pagine Paese, solo dove la fonte nazionale risponde (GOV.UK, dogana tedesca, Paesi Bassi, Austria, Svezia, Svizzera…) | dentro la 1 e la 3 | +50-150 | 4-6 | Con la 3 | Niente |
| 5 (piccola) | Giappone e Hawaii come pagine dentro la 3 (MAFF e HDOA 200) | 2-10 | +50-200 | 3-5 | Con la 3 | Niente |

**Totale:** 1.000-2.650 € prudenti, ~3.700 centrali, ~11.000 ottimisti; 61-91 ore. Ogni pagina: frase ufficiale citata, link alla fonte, data di controllo, avviso "verifica sempre con il tuo veterinario e la fonte ufficiale".
**Misura a 30 giorni dalla pubblicazione:** ≥ 500 impressioni al mese sulla sezione e posizione media < 30 su "uk pet passport 2027" e "taking dog to france from uk"; altrimenti la 3 non si costruisce.

---

## 6. Collegamenti con idee già in lista
- **Prezzi dei veterinari UK (gennaio 2027)**: "ahc cost" (vets for pets, pets at home, london) è una delle ricerche più forti di stasera; se le liste CMA comprendono l'AHC, la pagina di costo va in quella sezione e si collega alla n. 1.
- **Before you drive** (patente, pedaggi, gomme invernali): chi va in Francia o Spagna in auto con il cane passa dalle stesse pagine; collegamento reciproco.
- **Studio 1 "Pet travel rules"**: resta RISERVA come sito a sé (concorrenti automatici in campo); passa come **sezione** grazie ai tre fatti nuovi in testa a questo file.

## 7. Fonti lette stasera (30/10/2026)
- 200 `https://www.gov.uk/api/content/taking-your-pet-abroad`; 200 `https://www.gov.uk/api/content/bring-pet-to-great-britain`
- 200 `https://www.gov.uk/government/publications/pet-travel-approved-air-sea-and-rail-carriers-and-routes` (aggiornata 23/10/2026) e le due tabelle `.../approved-air-routes-for-pet-travel` (630 righe), `.../pet-travel-sea-routes-and-companies-you-can-use` (35 righe)
- 200 `https://www.gov.uk/government/publications/sps-agreement-preparing-your-business/veterinary-sector-preparing-your-business` ("mid-2027", "multiuse pet passport")
- 200 `https://www.gov.uk/api/content/control-dog-public/banned-dogs`
- 200 `https://food.ec.europa.eu/animals/live-animal-movements/dogs-cats-and-ferrets/listing-territories-and-non-eu-countries_en`, `.../bringing-pet-eu-non-eu-country_en` (modificata 30/10/2026), `.../travellers-points-entry_en`, `.../eu-countries-specific-information_en`, `.../designated-laboratories-performing-rabies-antibody-titration-tests/non-eu-countries_en`
- 200 `https://www.maff.go.jp/aqs/english/animal/dog/import-free.html` e `import-other.html`; 200 `https://hdoa.hawaii.gov/ai/aqs/animal-quarantine-information-page/`; 200 `https://inspection.canada.ca/en/importing-food-plants-animals/pets/dogs`
- 200 `https://www.directferries.com/affiliate.htm` ("50% of the commission we receive from the ferry operators")
- 200 `https://www.eurotunnel.com/uk/travelling-with-us/pets/`; 200 `https://www.brittany-ferries.co.uk/travel-information/pet-travel`; 200 `https://www.trenitalia.com/it/html/trenitalia/viaggia-con-il-tuo-cane.html`
- 403 `https://www.cdc.gov/importation/dogs/`; 403 `https://www.aphis.usda.gov/pet-travel`; 000 `https://www.agriculture.gov.au/biosecurity-trade/cats-dogs`; 200 (849 byte, JavaScript) `https://www.mpi.govt.nz/bring-send-to-nz/pets-travelling-to-nz/bringing-cats-and-dogs-to-nz/`; 200 (245 byte) `https://www.moccae.gov.ae/en/services/import-of-pet-animals.aspx`; 403 `https://www.gov.ie/...bringing-your-pet-into-ireland/`; 202 vuoto `https://eur-lex.europa.eu/...CELEX:32013R0577`
- Concorrenti: `entrybrief.com/sitemap/pets.xml` 200 indirizzi; `zoovettravel.com/sitemap.xml` 822 indirizzi (156 "atlas"); `petholidayclub.com/sitemap.xml` 499; `tailharbor.eu` rotte Paese → Paese (blog e PDF).
