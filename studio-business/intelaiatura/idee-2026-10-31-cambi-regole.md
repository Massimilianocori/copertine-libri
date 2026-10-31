# Ricerca del 31/10/2026: le regole che cambiano creano domanda improvvisa

Angolo assegnato: cambi di regole ufficiali **già pubblicati**, con data tra novembre 2026 e dicembre 2027, in tutto il mondo, che toccano milioni di persone e fanno nascere ricerche del tipo "how much / do I need / from when / am I affected". Per ogni cambio: fonte ufficiale provata con curl, quante persone tocca, domanda (autocomplete reale), chi c'è oggi su Google, se una pagina automatica precisa arriva prima dei giornali e resta utile dopo, chi paga, dove si mette.

**Letti prima:** skill `rete-siti`, `REGOLE-FISSE.md`, `ESPLORATE.md` per intero (fino alla caccia "treni" del 30/10), `ricerca-settore-calendari-2026-10-30.md`, `CRUSCOTTO-RETE.md` sez. 1-3, `touristtax/NOTE.md` (pagina dei cambi 2027 già online), dati di Before You Fly (`pedaggi.json`, `ees_etias.json`, `passaporti_*.json`).

**Già chiusi e non rifatti da capo:** tasse di soggiorno 2027 (pagina `tourist-tax-changes-2027/` già costruita il 26/10, Messico il 30/10), ETA UK ed ESTA (17/10), EES (fatto), power bank (17/10), bagaglio a mano UE 2027 (18/10), animali UK/UE 2027 (30/10), SELT B2 26/3/2027 (30/10), visto Graduate 1/1/2027 (30/10), tassa OPT (30/10), Medicaid 1/1/2027, rimesse USA, parchi USA (18/10), loi Le Meur (18/10). Dove riprendo una riserva vecchia (K-ETA, ETIAS) scrivo il fatto nuovo.

**Metodo.** Autocomplete di Google (`suggestqueries`, Paese e lingua giusti, ~50 ricerche); prima pagina con lo strumento di ricerca web (risultati USA: per le ricerche britanniche è un'approssimazione); fonti con curl dal server (codice HTTP, dimensione, frase letta); soldi con le assunzioni scritte. Nessun dato di volume di ricerca: dove serve un numero di persone uso quello della fonte ufficiale.

---

## 0. Risposta in breve

**Il fatto più grosso della sera è britannico e ha 3 giorni.** Il Budget del 28/10/2026 (documento ufficiale OOTLAR su GOV.UK, letto) ha cambiato di nuovo le regole di aprile 2027, e tre date si sommano sullo stesso pubblico, i proprietari che affittano casa in Inghilterra:
1. **registro obbligatorio dei padroni di casa** ("Register your rental property"), regione per regione dal **15/12/2026** al 15/8/2027, scadenze dal 14/3 al 14/11/2027, **£65 all'anno per casa**;
2. **tasse sugli affitti al 24 / 44 / 49 %** dal **6/4/2027** (il Budget 2025 diceva 22/42/47: metà delle pagine in rete oggi è sbagliata);
3. **Making Tax Digital** dal 6/4/2027 per chi incassa più di £30.000 (**1.077.000 persone**, stima HMRC).

È la forma di EsameB1 (una data ufficiale diversa per luogo, decine di regioni e ~300 consigli comunali elencati nel regolamento) su un pubblico che vale molto di più (proprietari britannici, assicurazione casa e mutui). **Nessuno dei nostri 10 siti è adatto**: serve un sito nuovo, quindi il sì di Massimiliano.

| # | Cambio (data) | Chi tocca | Dove | Voto | € a 18 mesi (prudente / centrale / ottimista) | Ore |
|---|---|---|---|---|---|---|
| 1 | **Registro padroni di casa per regione (15/12/2026 → 14/11/2027) + tasse sugli affitti 24/44/49 % (6/4/2027) + MTD £30.000 (6/4/2027)** | ~11 milioni di inquilini, milioni di proprietari in Inghilterra; 1.077.000 nuovi in MTD | **sito nuovo** "England landlord dates 2027" | **7** | 450 / 3.000 / **14.400** | 30-40 |
| 2 | Soglia "side income" da £1.000 a £3.000 + MTD £30.000 (6/4/2027) | chi vende online o ha piccoli lavori extra nel Regno Unito | seconda sezione dello stesso sito nuovo | 6,5 | 150 / 1.200 / 9.000 | 12-18 |
| 3 | **ETIAS** (data non ancora fissata; obiettivo "fine 2026" tolto dal portale UE) | tutti i visitatori senza visto dell'area Schengen | pagina già esistente di Before You Fly | 5 oggi | 120 / 1.800 / **14.400** il giorno in cui esce la data | 4-6 al momento |
| 4 | **Fine dell'esenzione K-ETA il 31/12/2026** (nessuna proroga pubblicata) | 22 Paesi, tra cui USA, Regno Unito, Canada, Australia, Germania, Francia, Italia, Giappone | pagina di Before You Fly | 5,5 | 25 / 150 / 550 | 2-3 |
| 5 | **Pedaggi senza caselli in Croazia (Crolibertas), dal 1/3/2027 per legge** | milioni di turisti in auto (Germania, Austria, Slovenia, Italia, Polonia) | aggiornamento della pagina Croazia in "pedaggi" di Before You Fly | 6 | 30 / 150 / 800 | 3-5 |
| 6 | Click day del decreto flussi 2027 (12/1, 9/2, 16/2, 18/2/2027; 165.850 quote) | datori di lavoro in Italia e lavoratori stranieri | pagina in EsameB1 (IT) + una in Visa Income (EN) | 5 | 60 / 300 / 1.000 | 5-8 |
| 7 | Tasse del permesso di soggiorno in Giappone (dal 1/10/2026; permanente da ¥10.000 a ¥200.000) | ~3,9 milioni di stranieri residenti | pagina in Visa Income | 5,5 | 50 / 250 / 900 | 4-6 |

**Obiettivo dei 10 cambi: raggiunto** (17 valutati: 7 sopra, 10 chiusi nella sez. 8).
**Obiettivo dei 2 con potenziale ≥ 10.000 €/anno: raggiunto solo nel caso ottimista**, e lo dico chiaro: il n. 1 arriva a 14.400 € ottimista ma 3.000 € nel centrale; ETIAS arriva a 14.400 € ottimista solo dal giorno in cui l'UE fissa la data, che oggi non c'è. **Nel caso centrale nessun cambio supera i 10.000 €**: la somma 1 + 2 (stesso sito) fa ~4.200 € centrale.

**Urgenti (da costruire entro dicembre):**
- **n. 1, entro il 10/12/2026**: il 15/12 apre la prima regione (West Midlands, Birmingham, Coventry) e la finestra delle tasse 2027 è aperta adesso, finché le pagine dei concorrenti riportano ancora il 22/42/47. Serve il sì di Massimiliano a un sito nuovo (1 passaggio su Netlify, crediti).
- **n. 4, entro il 15/12/2026**: una pagina "K-ETA from 1 January 2027" con la regola "se il 31/12 non esce la proroga, dal 1/1 serve"; da riscrivere il giorno della decisione coreana.
- **n. 6, entro il 20/12/2026**: precompilazione fino al 7/12/2026, primo click day il 12/1/2027.
- **n. 5, entro fine gennaio 2027** (non dicembre), prima delle ricerche di primavera.

---

## 1. Registro dei padroni di casa + tasse sugli affitti 2027 + MTD (Inghilterra) — voto 7

### Cosa cambia (fonti lette con curl il 31/10/2026)
- **Registro "Register your rental property" (Private Rented Sector Database).**
  - `legislation.gov.uk/ukdsi/2026/9780348286861/contents` **200** (36 kB) e `/data.xml` **200** (117 kB): *The Private Rented Sector Database Regulations 2026*, bozza depositata in Parlamento (sez. 140(5) del Renters' Rights Act 2025). Reg. 1(3): entrata in vigore per regione: West Midlands **15/12/2026**, East of England 15/1/2027, East Midlands 15/2, South East 15/3, Yorkshire and Humber 15/4, North West 15/5, North East 15/6, London 15/7, South West **15/8/2027**; per il resto 15/9/2027. **Schedule 1 elenca, per ogni regione, tutti i consigli comunali** ("Birmingham City Council, Coventry City Council, Dudley…"; Londra: City of London e i 32 borough). Reg. 14: tassa fissata dal gestore del registro.
  - `housinghub.campaign.gov.uk/renting-is-changing/get-ready-to-register/` **200** (pagina governativa): "an annual **£65** registration fee per property", "rolling out… from 15 December 2026, beginning in the West Midlands", scadenze per regione (Londra 14/10/2027, South West **14/11/2027**), "if you live in London but your rental property is in Birmingham, then you'll need to meet the deadline… in the West Midlands", tassa ridotta in proporzione durante il rollout, multa per chi non si registra.
  - Stato: le date sono scritte sia nella bozza sia nella pagina governativa; il voto finale delle Camere va ricontrollato su legislation.gov.uk (cambia l'indirizzo da `ukdsi` a `uksi`).
- **Tasse sugli affitti dal 6/4/2027.** `gov.uk/government/publications/budget-2026-overview-of-tax-legislation-and-rates-ootlar/...` **200** (360 kB), misura 1.2: "From 2027 to 2028, the property basic rate will be **24%**, the property higher rate will be **44%**, and the property additional rate will be **49%**… England, Wales and Northern Ireland… from 6 April 2027", nel Finance Bill 2026-27. La nota tecnica del Budget 2025 (`gov.uk/.../change-to-tax-rates-for-property-savings-and-dividend-income-technical-note` **200**) diceva 22/42/47: **le pagine scritte tra novembre 2025 e ottobre 2026 sono superate** (Price Bailey, Lanop, UK Property Accountants nei risultati di oggi).
- **Making Tax Digital £30.000.** Comunicato HMRC del 5/10/2026 (`gov.uk/government/news/sole-traders-and-landlords-earning-more-than-30000-urged-to-act-now` **200**): "From 6 April 2027, around **1,077,000** more sole traders and landlords will need to… send HMRC quarterly updates". OOTLAR 2.36: niente punti di penalità per i ritardi trimestrali nel 2027-28 per chi entra ad aprile 2027 (fatto nuovo del 28/10).

### Chi tocca
- Inquilini interessati dalla riforma: "11 million renters" (comunicato GOV.UK del 2024 sul Renters' Rights Bill, titolo letto dall'API di ricerca GOV.UK). Il numero dei proprietari non l'ho letto da una fonte ufficiale stasera: **manca** (ordine dei milioni; da leggere nell'English Private Landlord Survey prima di costruire).
- MTD: 1.077.000 in più dal 6/4/2027 (HMRC).

### Domanda (autocomplete Regno Unito, 31/10)
- "landlord database" **10** (registration, rollout to start in december, 2026, uk cost, cost, gov uk); "register your rental property" **10** (service england, gov uk online, database); "prs database" **10** (registration, rollout, landlord fees, enforcement, regulations); "landlord database fee" 8; "landlord registration england" **10** (2026, fee, check, number).
- Per città: "landlord database london" 3; "landlord registration birmingham" 6 ma con risultati generici: **le ricerche per luogo non sono ancora nate** (la Scozia, con il registro dal 2006, ha "landlord register edinburgh"): arriveranno con le date regionali, come per EsameB1.
- Tasse: "property income tax 2027" **10** (rates 2027-28, april 2027, changes 2027, rental income tax increase 2027); "landlord tax 2027" **10**; "rental income tax calculator" **10** (uk, 2026-27); "landlord tax calculator" **10** (uk, gov uk, hmrc, 2026).
- MTD: "making tax digital 2027" 9 (threshold, april 2027, for landlords 2027); "mtd for landlords" **10** (threshold, start date, free software).

### Chi c'è oggi su Google
- **Registro**: NRLA (strumento delle date), Landlord Studio ("PRS Database Registration Deadline Checker", `landlordstudio.com` **200**), The Independent Landlord (codice postale → regione), Lendlord (strumento lanciato il 13/10), la pagina governativa stessa con la tabella delle regioni, studi legali (Mishcon, HCR, Gowling, Macfarlanes), agenzie (Winkworth, Your Move, Reeds Rains), Property118, Propertymark.
- **Tasse 2027**: Propertymark e Property118 già con 24/44/49; Simply Business, accountants; molte pagine ancora a 22/42/47.
- **Lettura onesta**: lo strumento "in che regione sono e quando scade" **esiste già** in 3-4 versioni. Il buco è più stretto di quanto sembri: (a) le pagine **per consiglio comunale** (~300, dall'elenco ufficiale dello Schedule 1) con data, scadenza, tassa proporzionale del mese e link al servizio; (b) il **calcolatore 2027-28 corretto** (24/44/49, credito sugli interessi del mutuo al tasso base, confronto con il 2026-27), che oggi le pagine sbagliano; (c) la pagina unica "tutte le date del padrone di casa 2026-2027" con promemoria iCal (motore di Italy Strikes).

### Una pagina automatica arriva prima e resta utile?
- **Prima dei giornali**: sì per le pagine per consiglio (i giornali scrivono per regione il giorno dell'apertura, non per consiglio) e per il calcolatore corretto (oggi).
- **Dopo**: sì. La tassa è **annuale** (rinnovo ogni anno), il registro resta, le aliquote cambiano a ogni Budget (il calcolatore si aggiorna da OOTLAR ogni novembre), MTD scende a £20.000 nell'aprile 2028 (`gov.uk` policy paper, letto nei risultati). È un sito che vive di "date del padrone di casa" ogni anno.

### Chi paga
- **AXA Landlord Insurance su Awin** (`ui.awin.com/merchant-profile/12425` **200**: programma attivo, cookie 30 giorni). Commissioni non visibili senza accesso: un elenco di terzi riporta da £30 (polizze £130-249) a £170 (oltre £750); una versione più vecchia £35-100. **Da verificare con l'iscrizione** (spetta a Massimiliano). Nessuna commissione sui rinnovi.
- **AdSense** su pubblico britannico che parla di case, tasse e assicurazioni (resa alta per visita).
- Dopo, da verificare: software MTD per proprietari, mutui buy-to-let (lead solo dopo la consulenza fiscale, STRATEGIA sez. 10). Non li conto.

### Stima (assunzioni scritte)
- **Visite al mese a 18 mesi** (registro + calcolatore + MTD): prudente 1.200, centrale 5.000, ottimista 15.000. Picchi a ogni apertura regionale (dic 2026 → ago 2027), a marzo-aprile (aliquote nuove) e a novembre (Budget).
- **Resa per visita**: AdSense 0,02-0,03 € (pubblico UK su casa e tasse, 1,5 pagine a visita); AXA: clic 1,5-3 % sulle pagine del registro, conversione 2 %, ~£40-60 a polizza → 0,01-0,05 € a visita. Totale **0,03 / 0,05 / 0,08 €**.
- **Calcolo**: 1.200 × 12 × 0,03 = **430 ≈ 450 €**; 5.000 × 12 × 0,05 = **3.000 €**; 15.000 × 12 × 0,08 = **14.400 €/anno**.
- **A 12 mesi**: 150 / 1.200 / 6.000 €.
- **Primi soldi**: AdSense dal primo mese con visite (dicembre-gennaio se online entro il 10/12); AXA dal mese dopo l'iscrizione.

### Ore: 30-40
- Lettore dello Schedule 1 (consigli per regione) dal file XML ufficiale: 3-4 ore.
- Pagine regione (9) e consiglio (~300) con data, scadenza, tassa del mese, iCal: 10-14 ore (motore delle pagine città di EsameB1 e iCal di Italy Strikes).
- Calcolatore 2026-27 / 2027-28 (Python e JS uguali, con prove a mano come `touristtax/verifica.py`): 8-10 ore.
- Pagina MTD £30.000 con "sono dentro?" e date trimestrali: 4-6 ore.
- Design, revisore dei fatti, revisore di design: 6-8 ore.

### Dove
**Sito nuovo** (inglese, solo Inghilterra per il registro; Inghilterra, Galles e Irlanda del Nord per le aliquote). Nessuno dei 10 siti ha questo pubblico (Visa Income è per chi si trasferisce, FloodCost è americano). Serve: sì di Massimiliano, un sito su Netlify, Search Console, iscrizione AXA su Awin.

### Voto: 7 (non 8)
Più: fonte ufficiale perfetta e aperta (OGL, XML), date per luogo come EsameB1, pubblico che vale, chi paga con un nome, cambio di 3 giorni fa che rende sbagliate le pagine dei concorrenti, uso che si ripete ogni anno.
Meno (mezzo punto ciascuno): 3-4 strumenti "quando devo registrarmi" già online e la pagina governativa stessa ha la tabella; tema fiscale (prudenza di Google, nessuna consulenza: solo calcolo con fonte); sito nuovo su indirizzo `.netlify.app` senza link contro studi e associazioni; commissione AXA non verificata.
**Sale a 8** se, a 30 giorni dall'apertura, le pagine dei consigli delle West Midlands fanno ≥ 1.000 impressioni e AXA è approvato. Essendo un 7 su sito nuovo, va **prima al verificatore indipendente** e poi al sì di Massimiliano.

### Prova a 30 giorni
Online entro il 10/12 con: 9 pagine regione, i ~30 consigli delle West Midlands, il calcolatore 2027-28, la pagina MTD. Si guardano impressioni per "landlord database/registration + consiglio" e "property income tax 2027 calculator", e le visite da chatgpt.com.

---

## 2. Soglia del reddito extra da £1.000 a £3.000 + MTD (Regno Unito, 6/4/2027) — voto 6,5

- **Fonte**: `gov.uk/government/publications/income-tax-increasing-the-trading-allowance/increasing-the-trading-allowance` **200**; OOTLAR 1.5: "increase the Trading Allowance from £1,000 to £3,000… The trading income reporting threshold for Self Assessment will also be increased to £3,000… from 6 April 2027".
- **Chi tocca**: chi vende online, affitta l'attrezzatura, fa piccoli lavori; nessun numero ufficiale letto stasera (**manca**; da cercare nella nota d'impatto della misura).
- **Domanda (UK)**: "trading allowance" 10 (increase, self employed, hmrc); "trading allowance 3000" 7 ("increase to 3000", "tax free trading allowance 3000"); "side hustle tax" 10 (calculator uk, allowance uk, rules uk).
- **Google**: FreeAgent, Enterprise Nation, Pie, ANNA, Bytestart, yourmoney, un sito automatico `accountancy-ally.pages.dev`; **si contraddicono** ("tassa zero fino a £3.000" contro "solo soglia di dichiarazione, l'allowance resta £1.000"). La fonte ufficiale dice entrambe le cose: aumento dell'allowance **e** della soglia di dichiarazione. Correzione con fonte = forma che gli assistenti premiano (lezione del 27/10).
- **Chi paga**: AdSense; programmi dei software contabili (FreeAgent, QuickBooks, Coconut) **non verificati**: solo nell'ottimista.
- **Stima**: visite 800 / 4.000 / 15.000 al mese; resa 0,015 / 0,025 / 0,05 € → 800 × 12 × 0,015 = **144 ≈ 150 €**; 4.000 × 12 × 0,025 = **1.200 €**; 15.000 × 12 × 0,05 = **9.000 €**.
- **Ore**: 12-18 (calcolatore "devo dichiarare? quanto pago?" 2026-27 contro 2027-28 + pagina MTD in comune con il n. 1).
- **Dove**: seconda sezione del sito del n. 1 (stesso Paese, stesse fonti HMRC, stesso calcolatore). Da sola non vale un sito.
- **Voto 6,5**: pubblico grande e cambio fresco, ma concorrenza fitta di software contabili con blog forti, resa per visita più bassa dei proprietari.

---

## 3. ETIAS — voto 5 oggi (riserva con innesco)

- **Fatto nuovo rispetto al 17/10 e 25/10**: nei risultati di oggi l'obiettivo "ultimo trimestre 2026" risulta **tolto dal portale UE a luglio 2026**; riportata da terzi (Financial Times) la frase di eu-LISA "2026 no longer feasible". Il portale ufficiale `travel-europe.europa.eu/etias_en` risponde **200 ma 1.543 byte** (applicazione JavaScript: non si legge dal server). Before You Fly ha già la frase ufficiale "The European Union will inform about the specific date… several months prior to its launch" (`beforeyoufly/dati/ees_etias.json`).
- **Domanda**: "etias" 10 (application, start date, 2026, launch date, uk, official website).
- **Google**: portale UE, gov.uk, giornali, e il muro di siti non ufficiali che vendono la domanda.
- **Perché lo tengo**: il giorno in cui la Commissione pubblica la data (atto nella Gazzetta UE, leggibile dalla banca dati SPARQL trovata il 27/10), la domanda esplode per mesi in USA, Regno Unito, Canada, Australia; la pagina c'è già.
- **Stima solo da quel giorno**: visite medie 500 / 5.000 / 30.000 al mese per 12 mesi; resa 0,02 / 0,03 / 0,04 € → **120 / 1.800 / 14.400 €**. Oggi: 0.
- **Azione (2 ore, automatica)**: un controllo settimanale (GitHub Actions già in uso) che cerca nella banca dati SPARQL dell'Ufficio pubblicazioni un atto con "ETIAS" e "start of operations"; quando compare, avvisa e si rigenera la pagina con la data in alto. Voto 5 finché non c'è la data; 7 il giorno dopo.

---

## 4. Fine dell'esenzione K-ETA (Corea del Sud, 31/12/2026) — voto 5,5

- **Fonte**: avviso del Ministero della Giustizia coreano del 29/12/2025 (esenzione 1/1-31/12/2026 per 22 Paesi), riportato da più fonti; `k-eta.go.kr/portal/apply/index.do` **200** (286 kB, testo in JavaScript, non letto); pagina del consolato `mofa.go.kr` **000**. Nessuna proroga pubblicata al 17/10 (fonte di terzi).
- **Domanda**: "k-eta 2027" **10** (exemption 2027, us citizen 2027, in giapponese, cinese, coreano, spagnolo); "k-eta exemption" 10 (countries 2026, uk, australia).
- **Google**: `tripprof.com` (**200**) ha già la pagina "What Changes January 1, 2027" in 10 lingue, `korea-visa-hub.pages.dev`, studi legali (EIG, Envoy). Il buco è piccolo.
- **Fatto rispetto al 25/10**: la data è a 2 mesi; il giorno della decisione (proroga o no) arriva l'ondata di ricerche.
- **Stima**: visite medie 100 / 500 / 1.500 al mese (picco dicembre-febbraio), resa 0,02-0,03 € → **25 / 150 / 550 €**. **Ore 2-3**: una pagina in Before You Fly (sezione `ees-etias/` o passaporti) con "if no extension is published by 31 December, from 1 January 2027 you need K-ETA (₩10,000, valid 3 years)", da rigenerare il giorno della decisione. Fare entro il 15/12.

---

## 5. Pedaggi senza caselli in Croazia (Crolibertas, 1/3/2027) — voto 6 come aggiornamento

- **Fonte**: `crolibertas.hr/en/` **200** (88 kB, sito ufficiale HAC): sistema unico su tutte le autostrade (HAC, Bina Istra, Autocesta Zagreb–Macelj), "ENC… mandatory for heavy vehicles, while users of light vehicles will have the option to choose: ENC or license plate recognition"; avviso di prova del 5/10/2026, 111 portali al 16/9/2026. La **data del 1/3/2027 è scritta nella legge sui pedaggi** (approvata a dicembre, secondo HAC citato da dnevnik.hr, informator.hr, croatiaweek); il sito ufficiale non la ripete; index.hr e Novi list dubitano dei tempi (gara del portale web annullata). `hac.hr` **200** senza la data in home.
- **Il nostro buco**: la pagina "Tolls in Croatia with a rental car (2026)" di Before You Fly (`beforeyoufly/dati/pedaggi.json`) dice ancora "Toll plazas: ticket at the entry, pay at the exit". Dal 1/3/2027 diventa sbagliata, e la domanda "con l'auto a noleggio devo registrare la targa?" non ha risposta ufficiale (né HAC né i noleggiatori ne parlano).
- **Domanda**: "croatia toll" 10 (system, how to pay, calculator); "maut kroatien 2027" 3 (kosten, registrieren) in tedesco; "croatia tolls 2027" vuota in inglese (arriverà).
- **Stima**: visite medie 100 / 400 / 1.500 al mese, resa 0,025-0,05 € (AdSense + DiscoverCars) → **30 / 150 / 800 €**. **Ore 3-5**: riquadro "From 1 March 2027 (by law)" con fonte, regola per targa ed ENC, "ask your rental company", data dell'ultimo controllo; controllo mensile di `crolibertas.hr` per le notizie. Fare entro fine gennaio.

---

## 6. Click day del decreto flussi 2027 (Italia) — voto 5

- **Fonte**: `lavoro.gov.it/node/43439` **200** (93 kB): "il **12 gennaio 2027** per lavoro subordinato stagionale nel settore agricolo; il **9 febbraio 2027**… turistico; il **16 febbraio 2027**… non stagionale…; il **18 febbraio 2027**… assistenza familiare. Tutte le domande potranno essere presentate fino al 31 d[icembre 2027]". Quote 2027: 165.850 (DPCM 2/10/2025, riportato da finanza.com e quifinanza; non letto nella Gazzetta stasera). Precompilazione 23/10-7/12/2026.
- **Google**: informazionefiscale, quifinanza, fiscal-focus, edotto, studi (Arletti Partners), Envoy; in inglese businesstoday.in per il pubblico indiano.
- **Chi paga**: AdSense (italiano e pubblico indiano/bengalese: resa bassa). Nessuna affiliazione.
- **Stima**: visite medie 400 / 1.500 / 4.000 al mese con picco gennaio-febbraio, resa 0,01-0,02 € → **60 / 300 / 1.000 €**. **Ore 5-8**: pagina IT in EsameB1 (stesso pubblico di stranieri in Italia, il sito che va) + pagina EN in Visa Income ("Italy work permit click day 2027") con iCal. Entro il 20/12. È "rete fitta": guadagno positivo, costo basso.

---

## 7. Tasse del permesso di soggiorno in Giappone (dal 1/10/2026) — voto 5,5 (riserva per la fonte)

- **Fonte**: pagina ufficiale dell'Ufficio immigrazione `moj.go.jp/isa/11_00107.html` **403** dal server (anche `index.html` e il PDF delle tariffe). Dai risultati: in vigore dal **1/10/2026** (fa fede la data di presentazione della domanda), permanente da ¥10.000 a **¥200.000** (ordinanza del 25/8/2026, Japan Times), rinnovi a fasce al posto dei ¥6.000 fissi.
- **Fuori dalla finestra di poco** (ottobre 2026), ma la domanda dura: ogni straniero lo incontra al rinnovo. "japan visa renewal fee" **10** (increase, 2026, **2027**, 3 years, reddit); "japan permanent residency fee" **10**.
- **Google**: Japan Times, Euronews, Coto Academy, YOLO Japan, studi; cifre che si contraddicono (1.150 % contro 1.900 %).
- **Stima**: **50 / 250 / 900 €** (pagina in Visa Income, 4-6 ore). **Solo se** la tabella ufficiale si legge: da provare con e-Gov (`elaws.e-gov.go.jp` **200**: testo dell'ordinanza sulle tariffe) o dal browser di Massimiliano.

---

## 8. Cambi provati e chiusi (con le prove)

| Cambio (data) | Fonte (curl) | Domanda / Google | Voto | Esito |
|---|---|---|---|---|
| Limite del cash ISA a £12.000 dal 4/2027 | GOV.UK `reduction-in-the-cash-individual-savings-account-isa-limit` 200 (17/9/2026); **OOTLAR 2.5 del 28/10: ritirato, resta £20.000** | "cash isa 2027" 10 | 3 | NO: il cambio non c'è più; MoneySavingExpert, banche e giornali rispondono in giornata |
| Inheritance tax sulle pensioni non usate (6/4/2027) | GOV.UK policy paper 26/11/2025 (API di ricerca), OOTLAR 1.27 | "pension inheritance tax 2027" 10 | 4,5 | NO: tema da consulenza, consulenti, MSE, Which?, giornali finanziari; nessuna data per luogo |
| Aliquote risparmi 22/42/47 % (6/4/2027) | OOTLAR 1.1 | dentro "property income tax 2027" | – | riga nel calcolatore del n. 1, non idea a sé |
| Payroll obbligatorio dei benefit (6/4/2027) | OOTLAR 1.24 | – | 3 | NO: pubblico di imprese e paghe, software paghe primi |
| eVED 3 p/miglio, APD 2028-29, tassa sugli studenti stranieri (1/8/2028), surcharge council tax £2m (4/2028) | OOTLAR 1.76, 1.71, 1.65, 1.22 | – | – | fuori finestra (2028): da rivedere a novembre 2027 |
| Divieto agli stranieri di comprare case usate in Australia (doveva finire il 31/3/2027) | pagina ATO (risultati, aggiornata 13/5/2026): **prorogato al 30/6/2029** | "australia foreign buyer ban" 5 | 3 | NO: nessun cambio nella finestra |
| Divieto agli stranieri in Canada (fino al 1/1/2027?) | regolamento SOR/2022-250 200, nessuna data di fine trovata; legge P-26.8 404 sul percorso | "canada foreign buyer ban 2027 / expiry / extension" 10 | 4,5 | RISERVA: domanda vera, ma stato al 2027 non verificato; si riapre se Finance Canada pubblica la decisione |
| VeriFactu in Spagna (1/1/2027 società, 1/7/2027 autonomi) | RDL 15/2025 nel BOE (risultati); il Ministero ha annunciato il rinvio a ottobre 2028 (5/10/2026) senza atto pubblicato | spagnolo, B2B | 3,5 | NO: data instabile, software di fatturazione primi, pubblicità spagnola bassa |
| Tassa "visa integrity" da 250 $ (USA) | Federal Register API 200: solo 2 documenti, nessuno sull'avvio; travel.state.gov 403 (17/10) | studi legali, giornali indiani | 4 | NO: nessuna data ufficiale |
| Tariffe per stranieri in 4 siti DOC (Nuova Zelanda, "2027") | `doc.govt.nz` 200 (pagina notizie in JavaScript, 447 caratteri); importi 20-40 NZ$ solo annunciati nel 2025 | "milford sound fee" 5 (parcheggio) | 5 | RISERVA per Tourist Tax: entra nella pagina dei cambi 2027 quando DOC pubblica data e importi |
| Visto esente 30 giorni in Thailandia (15/9/2026) | Gazzetta reale `ratchakitcha.soc.go.th` 403 | – | – | già passato; le pagine passaporto di Before You Fly si aggiornano dalle fonti canadesi e australiane (scheda Thailandia CA aggiornata 13/10) |
| Legge sulla cittadinanza portoghese, 10 anni (19/5/2026) | `diariodarepublica.pt` 000 | studi (Global Citizen Solutions, Movingto) | 3,5 | NO: fuori finestra, fonte chiusa, studi legali forti |

---

## 9. Righe aggiunte a `ESPLORATE.md`

Sezione "Ricerca cambi di regole con data (31/10/2026)".

## 10. Note per chi costruisce

- **Fonte del registro**: leggere lo Schedule 1 da `legislation.gov.uk/ukdsi/2026/9780348286861/data.xml` (XML ufficiale, OGL); quando il regolamento viene approvato l'indirizzo passa a `uksi`: uno script settimanale controlla e avvisa. Le date nelle pagine vengono solo dal file, mai scritte a mano.
- **Calcolatore delle tasse**: aliquote da OOTLAR (misure 1.2 e 1.1) con data e link; finanziamento del mutuo con credito al tasso base della tabella del Budget; frase "this is an estimate, not tax advice"; prove a mano come in `touristtax/verifica.py`. Scozia esclusa (aliquote proprie).
- **Nessun dato personale, nessun nome di proprietario**: solo regole, date e luoghi.
- **Affiliazioni**: AXA Landlord Insurance su Awin (cookie 30 giorni) da proporre a Massimiliano con l'iscrizione; `rel="sponsored noopener"` e riga di trasparenza.
- **Crediti Netlify**: un sito nuovo costa un deploy alla nascita e poi uno al giorno al massimo; le pagine regionali si rigenerano solo il giorno di ogni apertura (15 del mese).
