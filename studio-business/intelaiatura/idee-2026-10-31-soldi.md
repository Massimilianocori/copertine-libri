# Ricerca del 31/10/2026: "segui i soldi" (seconda parte)

**Angolo.** Si parte da chi paga molto per un cliente, poi si cerca la nicchia di dati ufficiali dove una pagina automatica porta proprio quel cliente. La prima ricerca con questo metodo (`ricerca-profonda-2026-10-28-commissioni.md`) ha già controllato 34 programmi: noleggio auto, trasferimenti di denaro, assicurazioni di viaggio, VPN, eSIM, lingue, prestiti agli studenti. **Qui non li rifaccio**: cerco solo programmi e pubblici nuovi (camper e campeggi negli USA, società americane per non residenti, assicurazioni per chi viaggia dal Regno Unito, corsi per insegnare inglese all'estero, nautica, assicurazioni per i genitori in visita, cambi di valuta per chi compra casa all'estero, pompe di calore, porti delle crociere).

**Letti prima:** skill `rete-siti`, `REGOLE-FISSE.md`, `ESPLORATE.md` (per parole chiave su tutte le famiglie toccate), `ricerca-profonda-2026-10-28-commissioni.md`, `strumenti/monetizzazione.json`. Già chiusi e non rifatti: alloggi per studenti (30/10), traduzioni giurate (26/10), assicurazione sanitaria per i visti (26/10 e 30/10), assicurazioni per animali (30/10), traslochi e mutui per stranieri (28/10), rimborsi alla partenza (28/10), rimesse e VPN (28/10), prenotazioni dei campeggi nei parchi (29/10).

**Prove, tutte del 31/10/2026:** `curl` dal nostro server (codice HTTP e testo letto), Google Autocomplete (`suggestqueries.google.com/complete/search?client=firefox`, Paese `gl` scritto ogni volta, lingua `hl=en`), ricerca web per la composizione dei risultati di Google (fatta dagli USA: per le ricerche britanniche è un'approssimazione) e per le condizioni che il server non legge. Le cifre lette solo su elenchi di terzi sono segnate **"non letto sulla pagina ufficiale"**.

**Griglia del voto** (come le ricerche precedenti): domanda 0-3, Google debole 0-2, fonte e licenza 0-2, soldi per visitatore 0-2, rischi e ore 0-1. Le stime sono a 18 mesi, in euro lordi all'anno, con il conto scritto. Sono stime, non dati.

---

## 0. Risposta in breve

**Nessuna idea arriva a 10.000 €/anno nella stima centrale.** Due idee ci arrivano solo nell'ipotesi ottimista, e sono le due con il tetto più alto trovate finora con questo angolo:

| # | Idea | Dove | Chi paga | Voto | 18 mesi €/anno (prudente / centrale / ottimista) | Ore | Esito |
|---|---|---|---|---|---|---|---|
| 1 | **"Will my RV fit?": lunghezza massima del camper per ogni campeggio federale USA** (Recreation.gov, 81.948 piazzole con la misura in 2.341 campeggi, file aggiornato ogni giorno) | **sito nuovo** | RVshare 4 % (prenotazione media 900 $), Outdoorsy 60-80 $ a prenotazione (non letto), AdSense USA | **7** | 480 / 2.600 / 10.800 | 28-40 | RISERVA alta: candidato a prendere il posto di un sito congelato a fine novembre |
| 2 | **Società americana (LLC) per non residenti, Paese per Paese** (trattato fiscale IRS, sanzioni OFAC, obbligo BOI per le società estere, costi per Stato) | sezione di Visa Income Checker | doola 15 % (100-300 $ a cliente, non letto), ZenBusiness su Awin (cifra non pubblica) | **6** | 470 / 2.000 / 9.500-11.700 | 14-20 | RISERVA: si costruisce solo se una delle due commissioni si legge sulla pagina del programma |
| 3 | GHIC Paese per Paese per chi parte dal Regno Unito + assicurazione di viaggio | sezione di Before You Fly | Staysure 5 %+ (letto), InsureandGo 12 %, Holiday Extras 15 % | 6,5 | 190 / 720 / 2.400 | 6-10 | **SEZIONE in coda** (rete fitta: costo zero, guadagno positivo) |
| 4 | Insegnare inglese all'estero: programmi ufficiali (JET, TAPIF, EPIK, Auxiliares…) e requisiti del visto + corsi TEFL | sezione di Visa Income Checker | Bridge 15 % (letto, cookie 90 giorni), OISE/Teach Away 15-18 % (letto), The TEFL Academy 10 % = 20-60 $ (letto) | 6 | 270 / 1.150 / 3.650 | 14-20 | SEZIONE in coda bassa |
| 5 | Freedom camping in Nuova Zelanda per Comune + noleggio camper | – | Motorhome Republic fino all'8 % (letto, prenotazione media 800 NZD) | 5 | – | – | RISERVA debole |
| 6 | Patente nautica per Stato USA e PCOC canadese | – | BOATsmart fino al 30 % (non letto) | 5 | – | – | NO |
| 7 | Assicurazione per i genitori in visita negli USA e Super Visa canadese | – | VisitorsCoverage 1-100 $ a scaglioni, Insubuy fino a 150 $ (non letti; Insubuy solo via Travelpayouts, bloccato) | 4,5 | – | – | NO |
| 8 | Cambio di valuta per chi compra casa all'estero + imposte di acquisto per regione | – | Smart Currency, Moneycorp, Currencies Direct, TorFX: nessuna cifra pubblica | 4 | – | – | NO |
| 9 | Orari delle navi da crociera per porto | – | CruiseDirect 3 % (già nostro partner) | 4 | – | – | NO |
| 10 | Pompe di calore e Boiler Upgrade Scheme per Comune (Regno Unito) | – | nessun programma per editori con cifra pubblica | 3,5 | – | – | NO |
| 11 | Punteggi minimi Praxis per Stato + preparazione | – | nessun programma di affiliazione trovato (240 Tutoring solo accordi con università) | 3 | – | – | NO |

**La lezione di oggi.** Le commissioni più alte trovate (doola 100-300 $, Outdoorsy 60-80 $, VisitorsCoverage fino a 100 $, cambi di valuta per le case) hanno quasi sempre una di queste tre debolezze: (1) la cifra non è sulla pagina ufficiale del programma; (2) i risultati di Google sono occupati dalle aziende che pagano o da siti automatici con una pagina per ogni combinazione; (3) la fonte ufficiale è chiusa dal nostro server (travel.state.gov 403, canada.ca 000, data.govt.nz con controllo anti-robot). **L'unico posto dove i tre pezzi si incastrano bene è il camper negli USA (idea 1)**: dato ufficiale ricco e fresco, nessuno lo usa per intero, chi paga è pubblico (RVshare 4 % letto). Ma è un sito nuovo, e la stima centrale (2.600 €) sta sotto l'asticella dei 5.000 €: per questo è "riserva alta" e non "costruire subito".

**Cosa vincolo allentare per arrivare a 10.000 € realistici** (regola del 17/10: dirlo). Con questi vincoli le idee da 10.000 € centrali non esistono nelle famiglie viste fino a oggi. Le strade che cambierebbero il conto sono già note: la spesa di prova per leggere travel.state.gov (candidata 9 del 28/10, passaporto americano), oppure i contatti (lead) venduti alle aziende dopo la consulenza fiscale (studio del 17/10). Questa ricerca non ne aggiunge di nuove.

---

## 1. Idea 1 — "Will my RV fit?": lunghezza massima del camper per campeggio, parco e foresta (USA) — voto 7, sito nuovo

**Chi paga e quanto.**
- **RVshare** (pagina ufficiale `rvshare.com/affiliates`, 200, testo letto): "Earn 4% commission of the total booking value for every RV rental & earn $7 commission for every new RV listing"; "$900 average booking value"; "30 day cookie duration"; "Websites, bloggers, content providers and networks can monetize their traffic with our affiliate program for free". Quindi circa **36 $ a prenotazione**.
- **Outdoorsy**: pagina affiliati 403 dal server. Elenchi di terzi (non letto sulla pagina ufficiale): 60-80 $ a prenotazione, cookie 30 giorni, rete AvantLink o FlexOffers.
- **Motorhome Republic** (noleggi camper in tutto il mondo, compresi USA; pagina 200, letto): "Earn up to 8% revenue from motorhome rental and insurance. Average booking value in 2022 was over NZD $800".
- AdSense su pubblico USA che viaggia (assunzione delle ricerche precedenti: 4-10 € ogni 1.000 pagine viste; il camper è un pubblico che spende).

**Domanda (autocomplete us/en, 31/10).**
- "rv length limit" → for national parks, for state parks, by state, in campgrounds, **yellowstone**, california, size limit for national parks, camper length limit for national parks (10).
- "national park campgrounds" → near me, map, in florida, michigan, north carolina, washington state, georgia, arizona, nh (10).
- "rv camping" → near me, colorado, oregon coast, san diego, **yosemite**, sites near me (10).
- "can you sleep at rest stops in" → ohio, florida, california, north carolina, washington, texas, georgia, tennessee, iowa, virginia (10): seconda famiglia, per Stato.
- "rv rental" → near me, las vegas, san diego, houston, cost, los angeles, chicago, denver (10); "rv rental cost" → per week, per day, per month, for 2 weeks (10).

**Google oggi.**
- "rv length limit for national parks list": blog di RVshare (un riassunto per Stato: "Alaska 40 ft, Florida 45 ft, Utah 19-50 ft"), Cruise America, Airstream, JD Power, rvtravel, camperreport, forum (irv2, airforums). **Nessuno dà il dato campeggio per campeggio per tutti i parchi.**
- "rv length limit yellowstone": forum (forestriverforums, Good Sam), blog di Outdoorsy, csginger, un sito automatico su `pages.dev` (`yellowstone-national-park-com.pages.dev`), yellowstonervpark. Le risposte si contraddicono (il limite comprende l'auto trainata o no?).
- "can you sleep at rest stops in ohio": Yahoo/USA Today, campendium, boondockersbible, interstaterestareas, blog e siti di bassa qualità; le fonti si contraddicono (3 ore o notte intera).
- Concorrenti da tenere d'occhio: campsitephotos.com (manuale, piazzola per piazzola, forte sui nomi dei campeggi), campendium e The Dyrt (recensioni degli utenti), recreation.gov stessa (prima per il nome del campeggio).

**Fonte ufficiale (curl del 31/10).**
- `https://ridb.recreation.gov/downloads/RIDBFullExport_V1_CSV.zip` → **200**, 248 MB, `last-modified: Fri, 30 Oct 2026 18:46:41 GMT` (si aggiorna ogni giorno). Dentro: `PermittedEquipment_API_v1.csv` (CampsiteID, MaxLength, EquipmentName: RV, Trailer, Fifth wheel, Caravan/camper van…), `CampsiteAttributes_API_v1.csv` (Max Vehicle Length 103.378 righe, Driveway Length 55.731, Electricity Hookup 43.689 con 30/50 ampere, Water Hookup 46.242, Pets Allowed 112.867), `Campsites`, `Facilities`, `RecAreas`.
- Conto fatto sul file: **81.948 piazzole con una lunghezza massima > 0, in 2.341 campeggi, in 375 aree** (parchi nazionali, foreste nazionali, laghi del Genio militare). Esempi letti: Yosemite Upper Pines 236 piazzole, massimo 35 ft; Grand Canyon Mather 156 piazzole, 30 ft; Acadia Blackwoods 35 ft; Arches Devils Garden 40 ft; Grand Teton Colter Bay 262 piazzole, 50 ft.
- **Difetti del dato** (da gestire nel codice): valori sbagliati (Smokemont 227 ft, Dorst Creek 121 ft) → si mostra la distribuzione delle piazzole e si scartano i valori oltre 65 ft; Yellowstone ha solo 5 campeggi su 12 (quelli gestiti da Xanterra mancano) → riga chiara "non su Recreation.gov".
- `https://developer.nps.gov/api/v1/parks?api_key=DEMO_KEY` → 200 (nomi e coordinate dei parchi; chiave gratuita).
- **Licenza: da leggere prima di costruire** (regola del 23/10). È un dato federale USA nato come dato aperto ("free and open data exchange using REST API standards" sulla pagina `ridb.recreation.gov/docs`, 200), ma la pagina delle condizioni non si legge dal server (`www.recreation.gov` non raggiungibile da questa sessione). Per questo fonte e licenza = 1,5 e non 2.
- Soste nei "rest areas" per Stato: 50 pagine dei DOT statali, regole quasi ferme; si compilano a mano una volta (6-8 ore), con la data di controllo.

**Le pagine.** Una pagina per campeggio (2.341 con la misura; le altre con "misura non pubblicata"), una per parco o foresta (375: "il camper da 35 ft entra in 9 campeggi su 13"), una per Stato, il calcolatore "quanto è lungo il mio camper con l'auto dietro", 50 pagine "dormire nelle aree di sosta in [Stato]". Riquadro noleggio (RVshare, Outdoorsy) e AdSense.

**Voto.** Domanda **2,5** (famiglie per parco e per Stato con 10 varianti, coda lunga dei nomi dei campeggi) + Google debole **1,5** (blog e forum, nessuno con il dato completo; campsitephotos è forte solo sui nomi dei campeggi) + fonte **1,5** (ottima e fresca, licenza da leggere) + soldi **1** (pubblico USA che spende; ma molti lettori hanno già il camper e non noleggiano) + rischi e ore **0,5** (sito nuovo, 28-40 ore, dato con errori da ripulire) = **7**.

**Stima (assunzioni scritte).**
- Per 1.000 visite: AdSense 1.600 pagine viste × 6-10 € = 10-16 €; noleggio: 20 % dei lettori pensa di noleggiare × 5 % clicca × 3 % prenota × ~45 € (media tra 36 $ RVshare e 60-80 $ Outdoorsy) = 13,5 €. Totale **20-30 € ogni 1.000 visite**.
- Visite al mese a 18 mesi (sito nuovo su `.netlify.app`, nessuna autorità; il paragone è EsameB1, ~810 visite al mese dopo 3 settimane, ma con una domanda molto più piccola): prudente 2.000, centrale 8.000, ottimista 30.000.
- **Prudente** 2.000 × 12 × 20 € / 1.000 = **480 €**. **Centrale** 8.000 × 12 × 27 € / 1.000 = **2.600 €**. **Ottimista** 30.000 × 12 × 30 € / 1.000 = **10.800 €**.
- **Primi soldi:** le prenotazioni dei camper per l'estate si fanno da febbraio a maggio. Se il sito esce a dicembre 2026, prime entrate marzo-maggio 2027; il grosso a 12-18 mesi.

**Ore.** 28-40: lettura del file e pulizia (8-10), pagine e calcolatore (10-14), soste per Stato a mano (6-8), revisione indipendente di 40 campeggi contro recreation.gov (4-6), design (sito nuovo, regola "falli subito bene").

**Esito.** **RISERVA alta**: voto 7 ma stima centrale sotto i 5.000 € dei siti nuovi. Candidato a prendere il posto del primo sito congelato al verdetto di fine novembre (stesso posto nella rete, stessi crediti). Si sblocca prima se: la licenza RIDB è letta e chiara **e** Outdoorsy conferma 60-80 $ sulla sua pagina (allora i soldi per visitatore salgono a 2 e il voto a 7,5-8).

---

## 2. Idea 2 — Società americana (LLC) per non residenti, Paese per Paese — voto 6, sezione di Visa Income Checker

**Chi paga e quanto.**
- **doola** (società per non residenti): pagine `doola.com/affiliates` e `/partners` **403** dal server. Elenchi di terzi (non letto sulla pagina ufficiale): 15 % su ogni piano, "almeno 100 $" e "fino a 300 $" a cliente, cookie 90 giorni, rete PartnerStack.
- **ZenBusiness** (pagina ufficiale `zenbusiness.com/affiliate-program/`, 200, letto): "Join our program in Awin to earn commissions on new business formations"; "access to increased payout tiers". **Cifra non pubblica.** Elenchi di terzi: 60-175 $ a società.
- Bizee compare nell'autocomplete ("bizee llc for non residents"): programma non controllato.

**Domanda (autocomplete, 31/10).**
- pk/en "us llc from pakistan" → registration from pakistan, price, open, formation, how to open, register (9).
- in/en "llc in usa for" → non resident, foreigners, registration for non residents, from pakistan, online (10).
- ng/en "how to open llc in usa from" → pakistan, india, bangladesh, canada, saudi arabia, uk, uae (10).
- us/en "llc for non residents" → us, wyoming, uk, formation, taxes, cheapest, reddit (10); "llc annual fee by state" (10).
- È lo stesso pubblico che arriva già a Visa Income Checker da ChatGPT (Pakistan, Turchia, Nigeria: cruscotto del 28/10).

**Google oggi** ("how to open llc in usa from pakistan"): businessanywhere.io (**una pagina per Paese**, già automatica), zenind, scounts.pk (5 pagine sul tema), globalsolo, acciyo, nsave, fiverr (venditori di servizi). Pieno di chi vende.

**Fonti ufficiali (curl del 31/10, tutte 200):** `irs.gov/businesses/international-businesses/united-states-income-tax-treaties-a-to-z` (Paesi con trattato), `irs.gov/forms-pubs/about-form-5472` (modulo obbligatorio per le LLC con un proprietario straniero), `fincen.gov/boi` (dal 2025 l'obbligo BOI resta solo per le società estere registrate negli USA), `ofac.treasury.gov/sanctions-programs-and-country-information` (Paesi sotto sanzioni), `sos.wyo.gov/Business/Docs/BusinessFees.pdf` (costi del Wyoming). I costi degli altri 49 Stati sono su 49 siti diversi e cambiano poco: filtro duro a metà.

**Voto.** Domanda **3** + Google debole **0,5** (businessanywhere ha già le pagine per Paese) + fonte **1** (fonti federali 200 ma quasi ferme; Stati sparsi) + soldi **1,5** (commissioni alte ma nessuna letta sulla pagina ufficiale) + rischi e ore **0** (vicino alla consulenza fiscale e legale: solo fatti ufficiali, mai "conviene"; il tema attira truffe) = **6**.

**Stima.** Per 1.000 visite: 40 clic sul riquadro × 1,5 % × ~110 € = 66 € + AdSense pubblico pk/in/ng 1-2 € = **~65 € ogni 1.000 visite** (prudente 40 €). Visite al mese a 18 mesi: 600 / 2.500 / 12.000-15.000. **Prudente** 600 × 12 × 0,065 = **470 €**; **centrale** 2.500 × 12 × 0,065 = **2.000 €**; **ottimista** 12.000-15.000 × 12 × 0,065 = **9.500-11.700 €**. Primi soldi: 2°-4° mese dopo la pubblicazione, se le iscrizioni sono approvate.

**Ore.** 14-20 (190 pagine Paese dai dati già in Visa Income + tabella trattati + 50 Stati a mano + revisione).

**Esito.** RISERVA. Si costruisce solo quando una delle due commissioni (doola o ZenBusiness) si legge sulla pagina del programma e il revisore conferma che il testo resta "fatti ufficiali, nessun consiglio".

---

## 3. Idea 3 — GHIC Paese per Paese per chi viaggia dal Regno Unito + assicurazione — voto 6,5, sezione di Before You Fly

**Chi paga e quanto.** **Staysure** (pagina ufficiale `staysure.co.uk/affiliates/`, 200, letto): "5%+ commission of the price of each travel insurance policy sold not including medical screening costs or add-ons", rete Tradedoubler; specialisti di chi ha malattie preesistenti. **InsureandGo** 12 % e **Holiday Extras** fino al 15 % (già nel piano del 28/10, stessa rete Tradedoubler/Awin). Premio medio di un viaggio singolo 25-70 £: **3-8 £ a polizza**.

**Domanda (autocomplete gb/en).** "is ghic valid in" → turkey, usa, canada, norway, switzerland, egypt, spain, thailand, croatia, malta (10); "ghic valid" → validity, turkey, validity period, valid countries, usa, norway, canada, cyprus (10); "ghic" → card, application, renewal, apply online (10); "travel insurance pre existing medical conditions" → list, over 70s, comparison sites, uk (10).

**Google oggi** ("is ghic valid in turkey"): Acibadem (ospedale turco), Avanti e Staysure (assicuratori: pagina "Which countries don't accept GHIC?"), Admiral, TUI, ABI, Global Citizen Solutions, gobackpacking, **due siti automatici su `pages.dev`** (`estate-7l0.pages.dev`, `fastplay-travel.pages.dev/insurance/turkey/`). Chi paga è già in pagina.

**Fonte ufficiale (curl).** API GOV.UK dei consigli di viaggio (OGL): 226 Paesi, tutti 200. Conto fatto oggi: **61 pagine "health" su 226 citano la GHIC/EHIC o un accordo sanitario reciproco** (es. Spagna e Svizzera "you need a GHIC or EHIC"; Serbia e Macedonia del Nord "reciprocal healthcare agreement"; Bosnia "do not cover"); 165 non la citano. Pagina NHS della GHIC: `nhs.uk/using-the-nhs/healthcare-abroad/apply-for-a-free-uk-global-health-insurance-card-ghic/` 200. Attenzione: "non citata" non vuol dire "non valida": la pagina dirà "non coperta secondo la lista NHS" solo per i Paesi fuori dalla lista ufficiale.

**Voto.** Domanda 3 + Google 0,5 + fonte 1,5 + soldi 1 + rischi e ore 0,5 (6-10 ore, regola sanitaria semplice) = **6,5**.

**Stima.** Per 1.000 visite: 60 clic × 4 % × ~6 € = 14 € + AdSense Regno Unito 1.300 pagine viste × 5 € = 6,5 € → **~20 €**. Visite al mese a 18 mesi: 800 / 3.000 / 10.000 (picco d'estate). **190 / 720 / 2.400 €/anno.** Primi soldi: aprile-giugno 2027 (prenotazioni estive).

**Esito.** **SEZIONE in coda** (regola della rete fitta: costo zero, guadagno positivo), nelle 225 pagine passaporto britannico già online, nella pubblicazione già prevista di Before You Fly.

---

## 4. Idea 4 — Insegnare inglese all'estero: programmi ufficiali, paga e requisiti del visto + corsi TEFL — voto 6, sezione di Visa Income Checker

**Chi paga e quanto (pagine ufficiali lette, 200).**
- **Bridge** (`bridge.edu/tefl/affiliates`): "Bridge Affiliates earn 15% of revenue for each new customer"; "90-Day Cookie Tracking"; "Anyone can join"; PayPal mensile.
- **OISE / Teach Away** (`teachaway.com/partnerships/affiliates`): "Up to 10 courses sold, you will earn a 15% commission for each course sold. For 11+ courses, you will earn an 18% commission".
- **The TEFL Academy** (`theteflacademy.com/affiliate-programme/`): "10% of the sale value which usually equates to $20-$60 per purchase", pagamento tramite ShareASale.
- Le pagine affiliati di i-to-i, Premier TEFL, TEFL Org e ITA rispondono 404 dal server.

**Domanda (autocomplete us/en).** "jet program salary" (10, con 2026, per month, after tax, philippines); "epik salary" (10, con levels, scale 2026); "tapif salary" (7, con 2026); "teach english in spain" (10, con government program, nalcap, 2027); "teach english in japan requirements" (10); "teach english in taiwan requirements" (10); "teach english in vietnam requirements" (10); "teaching english in china salary" (10); "do you need a tefl to teach in" → china, thailand, japan, spain, korea (10).

**Google oggi** ("teach english in vietnam requirements"): goabroad, International TEFL Academy, The TEFL Academy (4 pagine), tefl.org, teachinghouse, teflonline, tefl-certificate, wise, Vietnam Law Magazine. **I risultati sono delle scuole TEFL che pagano**: chi vende il corso scrive anche la guida.

**Fonti ufficiali (curl).** `jetprogramme.org/en/salary/` 200 e `/en/eligibility/` 200; `france-education-international.fr/en/teaching-assistant-in-france` 200 (TAPIF); `epik.go.kr` **000**; `talk.go.kr` **000**; `tfetp.org` (Taiwan) **000**; pagina spagnola degli Auxiliares 404 all'indirizzo provato; `edb.gov.hk` (NET Hong Kong) 404 all'indirizzo provato. Le cifre cambiano una volta l'anno: poco "automatico".

**Voto.** Domanda 3 + Google 0,5 + fonte 0,5 (metà delle fonti chiuse, dati annuali) + soldi 1,5 + rischi e ore 0,5 = **6**.

**Stima.** Per 1.000 visite: 50 clic × 1,5 % × ~40 € = 30 € + AdSense 8 € → **~38 €**. Visite al mese a 18 mesi: 600 / 2.500 / 8.000 → **270 / 1.150 / 3.650 €/anno**. Primi soldi: gennaio-marzo (domande per JET, EPIK, Auxiliares e TAPIF si aprono in autunno-inverno).

**Esito.** SEZIONE in coda bassa (dopo le sezioni da 7 già in coda), solo con le fonti che rispondono 200 (JET, TAPIF) più le pagine dei visti già in Visa Income.

---

## 5. Le idee chiuse (prove in breve)

**5.1 Freedom camping in Nuova Zelanda per Comune + noleggio camper — 5, RISERVA debole.** Domanda vera: us/en "freedom camping rules" → nz, christchurch, auckland, wellington, queenstown, coromandel (10); "campervan hire nz" (10); "self contained vehicle nz" (10). Chi paga: Motorhome Republic fino all'8 % su prenotazioni medie di 800 NZD (letto). Fonte: regolamenti di circa 60 Comuni in PDF (filtro duro), `catalogue.data.govt.nz` risponde con una pagina anti-robot ("Pardon Our Interruption"), `api.doc.govt.nz/v2/campsites` **403**. Google: Comune di Christchurch, Motorhome Republic stessa, Rankers, giornali.

**5.2 Patente nautica per Stato USA e PCOC canadese — 5, NO.** Domanda: us/en "do i need a boating license in" → mn, florida, texas, pa, wisconsin, ohio, nc, tennessee, missouri, michigan (10); ca/en "pleasure craft operator card" (10). Chi paga: BOATsmart "up to 30%" tramite Campfire Collective (non letto sulla pagina ufficiale; corso da ~50 $ → 10-15 $). Google: i fornitori ufficiali dei corsi (Boat-Ed, BoaterExam) e le agenzie statali. Fonte: 50 agenzie diverse, NASBLA in redirect; Transport Canada 200. Chi vende il corso è già il primo risultato.

**5.3 Assicurazione per i genitori in visita negli USA e Super Visa — 4,5, NO.** Domanda fortissima: us/en "visitor insurance for parents" → in usa, from india to usa, visiting canada, over 70, in australia (10). Chi paga: VisitorsCoverage da 1 a 100 $ a scaglioni (non letto: la pagina `visitorscoverage.com/affiliate-partnership/` è in JavaScript); Insubuy fino a 150 $ ma solo tramite Travelpayouts (bloccato dal 17/10). Fonte ufficiale per una pagina automatica: nessuna leggibile (`travel.state.gov` **403**, `canada.ca` **000** per la Super Visa). Google: Insubuy e VisitorsCoverage stessi.

**5.4 Cambio di valuta per chi compra casa all'estero — 4, NO.** Domanda: gb/en "buying property in spain" → from uk, as an american, from ireland, as a canadian, to get residency (10). Chi paga: Smart Currency Exchange (pagina 200): "Commercial partnership agreements vary… Enquire with our team" (nessuna cifra); Moneycorp (200, nessuna cifra nel testo); Currencies Direct e TorFX **403**. Le commissioni del settore sono probabilmente alte (una quota di ogni trasferimento), ma nessuna è pubblica: stesso verdetto delle assicurazioni sanitarie per i visti (26/10 e 30/10). Si riapre solo con una cifra scritta.

**5.5 Orari delle navi da crociera per porto — 4, NO.** Domanda enorme: us/en "cruise ship schedule" → 2026, key west, st thomas, port canaveral, ketchikan 2026, juneau, seattle, bar harbor (10); "juneau cruise ship schedule" con 2027 e pdf (10); gb/en "southampton cruise schedule" con 2027 e 2028 (10). Ma Google è di cruisetimetables.com, che ha **una pagina per porto e per giorno** già per il 2027, più cruisemapper e crew-center. Fonti dei porti: Port Canaveral 404, PortMiami 404, Port Everglades 403, Seattle 403, Cruise Line Agencies of Alaska 200. Chi paga (CruiseDirect 3 %) è già nel piano di Cruise Health Scores. Parcheggi dei porti ("port canaveral parking", 10): risponde il porto stesso.

**5.6 Pompe di calore e Boiler Upgrade Scheme per Comune (Regno Unito) — 3,5, NO.** Domanda: gb/en "boiler upgrade scheme" (10), "heat pump grant" (10), "free boiler scheme" (10). Fonte: statistiche mensili GOV.UK del BUS (200). Chi paga: nessun programma per editori con una cifra; Octopus paga 100 £ solo ai propri clienti che presentano un amico; Heatable solo "refer a friend"; BOXT senza pagina affiliati leggibile.

**5.7 Punteggi minimi Praxis per Stato — 3, NO.** Nessun programma di affiliazione trovato: 240 Tutoring lavora con università e associazioni (sconti), non con editori.

---

## 6. Cosa fare adesso

1. **GHIC (idea 3)**: in coda come sezione di Before You Fly, nella prossima pubblicazione già prevista (una sola, di sera, regola dei crediti del 31/10). Iscrizione Tradedoubler già prevista (InsureandGo, AXA): Staysure si aggiunge allo stesso account.
2. **Camper USA (idea 1)**: due controlli a costo zero prima di proporlo: (a) leggere la licenza RIDB da un browser normale (Massimiliano o una sessione con `www.recreation.gov` raggiungibile); (b) leggere la commissione di Outdoorsy sulla sua pagina. Poi, al verdetto di fine novembre, se un sito viene congelato, è il primo candidato per il suo posto.
3. **LLC per non residenti (idea 2)** e **TEFL (idea 4)**: aspettano. La 2 riparte solo con una commissione letta; la 4 dopo le sezioni da 7 già in coda.
4. Nessun messaggio a Massimiliano per queste idee: nessuna passa voto ≥ 7 **e** 5.000 € realistici (regola del 17/10). Si scrive in ESPLORATE.

---

## 7. Fonti lette il 31/10/2026

**Programmi (curl, testo letto):** rvshare.com/affiliates (200: 4 %, 900 $, 30 giorni); motorhomerepublic.com/affiliates (200: fino all'8 %, 800 NZD); staysure.co.uk/affiliates (200: 5 %+, Tradedoubler); bridge.edu/tefl/affiliates (200: 15 %, 90 giorni); teachaway.com/partnerships/affiliates (200: 15-18 %); theteflacademy.com/affiliate-programme (200: 10 %, 20-60 $); zenbusiness.com/affiliate-program (200: Awin, cifra non pubblica); smartcurrencyexchange.com/partners (200: nessuna cifra); moneycorp.com/en-gb/affiliates (200: nessuna cifra); prioritypass.com/en/affiliates (200: nessuna cifra).
**Non leggibili:** currenciesdirect.com e torfx.com (403), insubuy.com/affiliates (403), outdoorsy.com/affiliates (403), doola.com/affiliates e /partners (403), 1stformations.co.uk/affiliates (403), allclear.co.uk (000); 404: visitorscoverage.com/affiliates, i-to-i.com, premiertefl.com, teflcourse.net, sevenseasworldwide.com, worldtrips.com.
**Cifre solo da ricerca web (non lette sulla pagina ufficiale):** Outdoorsy 60-80 $, doola 15 % / 100-300 $, ZenBusiness 60-175 $, VisitorsCoverage 1-100 $, Insubuy fino a 150 $, BOATsmart fino al 30 %.
**Fonti ufficiali:** ridb.recreation.gov/downloads/RIDBFullExport_V1_CSV.zip (200, 248 MB, 30/10/2026; scaricato e contato nel blocco appunti della sessione, non nel repository); developer.nps.gov (200); gov.uk/api/content/foreign-travel-advice (226 Paesi, 200, OGL); nhs.uk pagina GHIC (200); jetprogramme.org (200); france-education-international.fr (200); irs.gov trattati e modulo 5472 (200); fincen.gov/boi (200); ofac.treasury.gov (200); sos.wyo.gov tariffe (200); gov.uk statistiche BUS (200); doc.govt.nz (200), api.doc.govt.nz (403), catalogue.data.govt.nz (pagina anti-robot); epik.go.kr, talk.go.kr, tfetp.org, canada.ca (000); travel.state.gov, porteverglades.net, portseattle.org (403).
**Autocomplete:** circa 50 interrogazioni (us, gb, ca, nz, au, in, pk, ng).
**Ricerca web (risultati di Google, dagli USA):** "can you sleep at rest stops in ohio", "is ghic valid in turkey", "teach english in vietnam requirements", "freedom camping rules christchurch", "rv length limit yellowstone", "rv length limit for national parks list", "how to open llc in usa from pakistan", "juneau cruise ship schedule 2027", più 9 ricerche sulle condizioni dei programmi.
