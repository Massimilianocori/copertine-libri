# Fronte del 14/11/2026 sera: «prima chi paga» dal mercato PartnerStack, in settori mai toccati

Settori di partenza (lontani dai nostri): officine auto, artigiani di casa, studi di terapia e fisioterapia, associazioni non profit, investitori immobiliari, numeri verdi per aziende, contabili, ristoranti, saloni.

Approccio del giro: **n. 7 «Prima chi paga»** (lista di BRIEF-RICERCA). Si parte dai programmi con compenso scritto di almeno 50 $ ad azione, si guarda che cliente servono, e solo dopo si cerca dove quel cliente fa una ricerca misurabile di un dato ufficiale o di uno strumento gratuito. Chi arriva sulla pagina deve essere già il compratore.

**Esito in una riga.** Nessuna idea arriva a 5.000 €/anno centrali. La migliore è **«preventivo e fattura dell'officina conformi alla legge dello Stato» con Shopmonkey (300 $ a dimostrazione fatta): voto 5,5, ~1.000 €/anno centrali, 30 ore, 33 €/ora**, come sezione del sito NAICS, con una prova di 10 ore su 4 Stati. Tre idee cadono per una regola scritta nei termini: Zeffy e Tradify non ammettono editori italiani, BetterLife chiede il modulo fiscale W-9 (solo soggetti USA).

## 1. Metodo

- **Pagatori.** Pagina pubblica `market.partnerstack.com` (200, 11 MB): dentro ci sono i dati di **424 programmi** (offerta, scaglioni, iscrizioni per ogni 100 clic, numero di partner, indirizzo dei termini). Per i finalisti ho letto anche la pagina del programma `market.partnerstack.com/page/<nome>` (200) e i termini ufficiali dove si aprono. «Letto» = risposta 200 con la cifra dentro, oggi 14/11/2026.
- **Domanda.** `api.seodata.dev /v1/keyword`: **258 ricerche di volume** (250 USA, 8 Canada). Le frasi con lo stesso numero nello stesso gruppo sono contate una volta.
- **Dati ufficiali.** Letti con curl dal contenitore. I 403 sono scritti e non aggirati; dove c'è una via diversa è indicata, altrimenti «DA RIPROVARE».
- **Concorrenti.** Per i finalisti ho letto le pagine dei primi risultati raggiungibili (parole, anno, cosa manca) prima del voto.
- **Conti.** Pubblicità: visite × 1,3 pagine × 3,3 $ ogni 1.000 (6 $ dove il costo per clic è ≥ 10 $) × 0,92. Cambio 1 $ = 0,92 €. €/ora = €/anno centrali a 36 mesi ÷ ore.
- **Attenzione sul dato «iscrizioni per clic».** È il numero pubblico della rete (quanti clic diventano una iscrizione o un contatto). Non dice quanti poi pagano: quella quota è una mia ipotesi, scritta ogni volta.

## 2. I programmi con compenso scritto ≥ 50 $, per tipo di cliente

Su 424 programmi, circa 220 hanno una cifra ≥ 50 $ nel testo dell'offerta. La maggior parte è software generico per aziende (marketing, vendite, sicurezza): niente cliente riconoscibile, niente ricerca di dati ufficiali. Qui sotto quelli che servono un mestiere preciso.

| Cliente servito | Programmi (compenso letto) | Iscrizioni ogni 100 clic | Editore italiano |
|---|---|---|---|
| **Officine auto** | Shopmonkey: 300 $ a dimostrazione fatta (scaglioni fino a 500 $) | 3,5 | non scritto |
| **Artigiani di casa** (idraulici, elettricisti, tuttofare, edili) | Housecall Pro: 10 $ a contatto, 180 $ a cliente, «fino a 320 $» a contatto qualificato · Tradify 200 $ · Contractor Foreman 150 $ a dimostrazione · Houzz Pro 100-400 $ · Thryv 250 $ | 0,8 · 0,4 · 0,05 · 0,1 · 1,4 | Housecall: non scritto (i contatti devono essere di USA o Canada) · **Tradify: solo partner di AU, NZ, UK, USA, Canada, Irlanda** |
| **Terapeuti, fisioterapisti, studi sanitari** | SimplePractice 100 $ a cliente pagante (scaglioni fino a 300 $) · Jane 120 $ a clinica (150-200 $ dopo) · Healthie 150 $ · Heard 100 $ (contabilità per terapeuti) · Weave 250 $ a dimostrazione + 500-750 $ a contratto (dentisti) | 1,2 · 2,2 · 0,7 · 1,0 · 0,2 | non scritto (Heard: cliente negli USA) · termini SimplePractice non letti (pagina in JavaScript) |
| **Associazioni non profit** | Zeffy: 30 % delle mance per 12 mesi («in media 500 $») · Aplos: 250 $ a cliente (nei dati pubblici anche «25 $ a contatto») | 3,8 · 0,5 | **Zeffy: solo partner di USA, Canada, UK** · Aplos: non scritto |
| **Investitori immobiliari** | BetterLife: 700 $ a prestito erogato | 3,5 | **serve il modulo W-9 e un conto ACH: di fatto solo USA** |
| **Aziende che vogliono un numero** | 800.com 125 $ · Nextiva 100-350 $ a linea · AT&T 400 $ a linea · Aircall 75 $ a contatto | 1,5 · 1,5 | non scritto |
| **Chi assume o affitta** (controlli sui precedenti) | Checkr: 150 $ ad azienda pagante, 25 $ a privato pagante | 11,8 | nessuna esclusione (i termini parlano di chi opera fuori dagli USA) |
| **Piccoli datori con turni** | Connecteam: 25 % del primo anno (negli scaglioni 200-300 $ a cliente, 100-200 $ a contatto) · Gusto 300 $ (già in classifica) | 0,7 | Connecteam: esclusi solo i Paesi sotto sanzioni |
| **Contabili e chi paga fornitori** | Forwardly 100 $, «fino a 1.000 $» · Melio 150-400 $ al primo pagamento · BILL 250 $ · Nickel 250 $ ad azienda e 750 $ a studio, ma solo dopo 10 pagamenti da 250 $ · TaxCycle 250 $ (solo Canada) · Xero 200 $ | 1,0 (Melio) · 5,1 (TaxCycle) | non scritto |
| **Ristoranti** | Owner: 50 $ a contatto + 500 $ a ristorante attivo | 0,2 | non scritto |
| **Saloni, centri estetici, palestre** | Boulevard 750 + 750 $ · Momence 500 $ | 0,02 · 0,2 | non scritto |
| **Affitti brevi** | Guesty 100 $ al primo annuncio (il cliente deve gestire 5 o più case) | 2,1 | non scritto |
| **Studi legali** | 8am (MyCase): 10 % del contratto annuo | 1,2 | non scritto |
| **Autotrasporto** (già visto stamattina) | Coast 300 $, Motive 150 $, Samsara 150 $, Alvys 250 + 300 $ | – | – |

## 3. Tabella delle idee

| # | Idea | Pagatore (letto) | Ricerche/mese misurate | 36 mesi p/c/o €/anno | Ore | €/ora | Voto | Esito |
|---|---|---|---|---|---|---|---|---|
| A | Officine: preventivo e fattura conformi alla legge dello Stato, più tariffa oraria (sezione di NAICS) | Shopmonkey 300 $ a dimostrazione | ~25.000 | 150 / 1.000 / 5.000 | 30 | 33 | **5,5** | **PROVA 10 ore** su 4 Stati |
| B | Numeri verdi: i 7 prefissi + «come averne uno» (aggiunta alla riga 9, prefissi USA) | 800.com 125 $, Nextiva 100-350 $ | 519.300 (prefissi) + ~41.000 (acquisto) | 100 / 420 / 1.300 | 12 | 35 | 4,5 | RISERVA: dà un pagatore alla riga 9 |
| C | «Quanto indietro va il controllo dei precedenti», Stato per Stato (sezione di Statute Limits) | Checkr 25 $ a privato, 150 $ ad azienda | ~55.000 | 45 / 300 / 2.500 | 16 | 19 | 4,5 | RISERVA con prova di 6 ore |
| D | Tariffe Medicare 2027 per codice di terapia e per località (sito nuovo) | SimplePractice 100 $, Jane 120 $, Healthie 150 $ | ~120.000 | 45 / 290 / 3.200 | 30 | 10 | 4,5 | RISERVA (rischio diritti AMA; sotto 40 €/ora) |
| E | Calcolatore del cartellino e degli straordinari per Stato (sezione di Paycheck) | Connecteam 25 % primo anno, Gusto 300 $ | ~350.000 | 30 / 155 / 1.500 | 14 | 11 | 4 | RISERVA bassa (strumenti completi già primi) |
| F | Non profit: come aprire per Stato, modulo 990-N, regole delle lotterie | Aplos 250 $ (Zeffy non ammette l'Italia) | ~62.000 | 20 / 115 / 900 | 40 | 3 | 3,5 | NO |
| G | Licenza degli artigiani per Stato, con la soglia in dollari del tuttofare | Housecall Pro 10-320 $ | ~90.000 su 17 frasi | 30 / 200 / 1.500 | 60 | 3 | 3,5 | NO (il pagatore stesso ha già le pagine) |
| H | Calcolatori per investitori immobiliari (DSCR, prestiti a breve) + affitti HUD | BetterLife 700 $ (chiede W-9) | ~110.000 | 10 / 30 / 250 | 20 | 1,5 | 3 | NO (pagatore non accessibile) |
| I | Pagamenti ai fornitori, ACH e bonifici (Melio, Forwardly, Nickel, BILL) | 150-1.000 $ | 5.400-74.000 per seme | non stimato (≤ 150) | – | – | 3 | NO (ricerche commerciali, nessun dato ufficiale) |
| L | Ristoranti e furgoni del cibo: licenze e costo della licenza alcolici | Owner 50 + 500 $ | ~25.000 | non stimato (≤ 100) | – | – | 3 | NO (0,2 iscrizioni ogni 100 clic) |
| M | Canada: scadenze fiscali per chi prepara dichiarazioni | TaxCycle 250 $ | ~5.000 | non stimato (≤ 80) | – | – | 2,5 | NO (domanda piccola) |

## 4. Le idee una per una

### A. Officine auto: preventivo e fattura conformi alla legge dello Stato — voto 5,5, PROVA

- **Chi paga.** Shopmonkey (gestionale per officine). Pagina pubblica e dati PartnerStack: «Earn $300 for every Demo Held Lead»; negli scaglioni anche 500 $ a dimostrazione e 500 $ a cliente chiuso. 227 partner, risposta alla domanda in 5 giorni, **3,5 iscrizioni ogni 100 clic** (la più alta tra i programmi di mestiere). I termini indicati sono quelli generali del sito: sull'editore italiano niente di scritto.
- **Chi cerca.** Il titolare di una piccola officina che fa ancora preventivi e fatture a mano. È esattamente il cliente di Shopmonkey.
- **Domanda misurata (USA).** Modelli di fattura: «auto repair shop invoices» 1.600 a 10,5 $, «auto repair invoices» 1.300 a 15,6 $, «auto repair invoice template» 1.000 a 12 $, «mechanic invoice» 480 a 19 $, «mechanic receipt template» 390. Preventivi: «auto repair estimate template» 880 a 12,8 $, «template for auto repair estimate» 590, «body shop estimate template» 210 a 22 $. Ordini di lavoro: «repair order template» 480, «auto repair work order template» 210. Tariffa oraria: «mechanic labor rate» 1.300, «auto repair labor rate» 590, «average mechanic labor rate» 480. Tempari: «automotive labor guides» 1.600 a 9,6 $, «automotive labor guide» 1.000. Avvio: «auto repair shop business plan» 880, «how to start a mechanic shop» 390, «mechanics lien on car» 1.000. Software: «car repair shop software» 5.400 a 33 $, «auto repair software» 4.400 a 35 $, «free auto repair software» 590. **Totale ~25.000 al mese**, con costi per clic da 10 a 47 $ (chi vende software alle officine paga molto).
- **Dato ufficiale letto.**
  - Florida: lista ufficiale del Dipartimento dell'Agricoltura «Estimate and Invoice Requirements» (PDF, 200): elenca voce per voce cosa deve stare nel preventivo e nella fattura (legge 559.905).
  - Washington: RCW 46.71.025 (200): preventivo scritto obbligatorio e la frase esatta da stampare.
  - Minnesota: statuto 325F.60 (200): la fattura deve dire se i ricambi sono originali, i chilometri all'arrivo, i sintomi descritti dal cliente.
  - California: la pagina «Write It Right» dell'ufficio statale dà 404 all'indirizzo provato: **DA RIPROVARE** (la guida esiste, va trovato l'indirizzo giusto).
- **Concorrenti letti.** Invoice Fly (2.248 parole, modelli in 5 formati), Vertex42 (479 parole, modello Excel): **nessuno dei due nomina le voci obbligatorie per legge** (zero volte «state law», «odometer», «required by»). Invoicequick 403. Gli altri primi posti sono Xero, QuickBooks, Wave, Tofu: modelli generici. La pagina modelli di Shopmonkey dà 404.
  - **Cosa manca a tutti:** un modello di preventivo e di fattura già con le voci e le frasi che la legge di quello Stato chiede, con l'articolo accanto. È un vuoto vero, ma la domanda è piccola.
- **Conto centrale a 36 mesi.** Modelli, tariffe e avvio: 12.500 ricerche × 2 % = 250 visite al mese. Software: 10.700 × 0,3 % = 30. Totale 280 visite. Il 6 % clicca il riquadro «fai preventivi e fatture dal telefono» = 17 clic × 3,5 % = 0,58 richieste di dimostrazione al mese × 50 % fatte davvero (mia ipotesi) = 0,29 × 300 $ × 0,92 × 12 = ~970 €. Pubblicità ~25 €. **Totale ~1.000 €.** Prudente 150 (100 visite, 4 %, 30 %). Ottimista 5.000 (900 visite, 8 %, 60 %).
- **Ore.** 30 per 10 Stati con legge sulle officine (modello stampabile + pagina delle regole + tariffa oraria dai salari ufficiali BLS). **Prova 10 ore**: Florida, Washington, Minnesota, California.
- **Dove va.** Sezione del sito NAICS (pagina dell'attività 811111, riparazione auto): nessun sito nuovo.
- **Rischi.** La dimostrazione deve essere «fatta» e l'officina vera: chi scarica un modello gratis può essere troppo piccolo. Ammissione dell'editore italiano non scritta. La quota del 2 % regge solo se i modelli sono davvero migliori di quelli generici.
- **Azione di Massimiliano.** Domanda a Shopmonkey su PartnerStack (10 minuti), solo dopo le prime 100 visite al mese sulla sezione.

### B. Numeri verdi: i 7 prefissi e «come averne uno» — voto 4,5, RISERVA (pagatore per la riga 9)

- **Chi paga.** 800.com: «Earn $125 for every successful referral» (pagina e termini letti: il compenso scatta quando l'azienda apre il conto e paga; 1,5 iscrizioni ogni 100 clic; nessuna esclusione di Paese scritta). Nextiva: 100-350 $ a linea venduta. AT&T Business: 400 $ a linea.
- **Domanda misurata.** Prefissi: «833 area code» 135.000, «855» 90.500, «844» 90.500, «877» 74.000, «866» 74.000, «888» 40.500, «800» 14.800: **519.300 al mese**, quasi tutte di chi vuole sapere chi ha chiamato. Acquisto: «business phone number» 14.800 a 66 $, «toll free number» 9.900 a 22,6 $, «800 numbers» 6.600 a 34 $, «buy a phone number» 5.400 a 13 $, «vanity phone numbers» 2.900 a 16 $, «get a toll free number» 1.300 a 33 $: **~41.000**.
- **Dato ufficiale.** FCC 403, Somos 404 all'indirizzo provato, NANPA errore di rete: **DA RIPROVARE**. Il dato in sé è minimo (7 prefissi con la data di apertura).
- **Concorrenti.** Non letti uno per uno: i primi posti delle frasi d'acquisto sono i venditori stessi (nessun vuoto, quota 0,2 %); per i prefissi vale la verifica del 13/11 sulla riga 9 (rischio alto di risposta diretta di Google).
- **Conto centrale.** Prefissi: 519.300 × 0,3 % = 1.560 visite, lo 0,5 % clicca = 8 clic. Acquisto: 41.000 × 0,2 % = 82 visite, il 10 % clicca = 8 clic. 16 clic × 1,5 % × 125 $ × 0,92 × 12 = ~340 €. Pubblicità ~80 €. **Totale ~420 €.** Prudente 100, ottimista 1.300.
- **Esito.** Non è un'idea a sé: è il pagatore che mancava alla riga 9 (prefissi USA, oggi solo pubblicità). Se la riga 9 si costruisce, queste 7 pagine si fanno per prime (12 ore).

### C. «Quanto indietro va il controllo dei precedenti», Stato per Stato — voto 4,5, RISERVA con prova

- **Chi paga.** Checkr: pagina pubblica «Earn $150 for every paid signup for businesses · $25 for every paid signup for individuals». **11,8 iscrizioni ogni 100 clic.** Termini letti: vietato comprare pubblicità sul marchio; chi opera fuori dagli USA deve rispettare le leggi del suo Paese (quindi non è escluso).
- **Chi cerca.** Chi sta per essere assunto e ha un precedente: vuole sapere cosa vedrà il datore di lavoro. Il passo naturale è farsi il controllo da solo (25 $ a noi). In piccola parte datori di lavoro (150 $).
- **Domanda misurata.** «how long does a background check take» 27.100 a 8-10 $, «what does a background check show» 8.100, «how far back do background checks go» 3.600 + 1.900, «level 2 background check» 4.400 (legge della Florida), «how to do a background check on yourself» 2.900, «background check on myself» 1.900, «do misdemeanors show up» 1.300, «10-year background check states» 1.300, «does a dui show up» 880. Le frasi per singolo Stato sono piccole (Texas 170, California 140, Florida 140). **Totale ~55.000.**
- **Dato ufficiale letto.** Legge federale 15 U.S.C. 1681c su govinfo.gov (200): 7 anni per arresti, cause e debiti; le condanne non hanno limite federale. Texas: pagina degli statuti 200 ma il testo si carica con JavaScript. California e New York: 403. Le leggi statali vanno prese dai siti dei parlamenti che rispondono, una per una: **in parte DA RIPROVARE**.
- **Concorrenti letti (5).** iprospectcheck (3.846 parole): elenca gli Stati con l'articolo di legge accanto (California, Hawaii, Maryland, Massachusetts…): **completo**. GoodHire (2.724 parole), ScoutLogic (2.809), Cisive (1.991), backgroundchecks.com (1.762): guide generali di chi vende i controlli. Help For Felons (2.300 parole): pagina per Stato. Le liste degli Stati non coincidono tra un sito e l'altro. **Nessun vuoto: è quota (0,5 %).**
- **Conto centrale.** 55.000 × 0,5 % = 275 visite × 8 % = 22 clic × 11,8 % = 2,6 iscrizioni × 40 % paganti (mia ipotesi) × 25 $ × 0,92 × 12 = ~290 €. Pubblicità ~13 €. **Totale ~300 €.** Prudente 45, ottimista 2.500.
- **Ore.** 16 (tabella dei 50 Stati con l'articolo + 12 pagine per gli Stati con un limite). Prova: 6 ore con la pagina generale e 5 Stati dentro Statute Limits (è un «limite di tempo per Stato», lo stesso schema).
- **Esito.** RISERVA: si prova solo se Statute Limits prende impressioni.

### D. Tariffe Medicare 2027 per codice di terapia e per località — voto 4,5, RISERVA

- **Chi paga.** SimplePractice 100 $ a cliente pagante (+100 $ se resta 6 mesi), Jane 120 $ a clinica, Healthie 150 $, Heard 100 $. Termini letti: Jane, Healthie, Heard senza esclusioni di Paese; SimplePractice non letto (pagina in JavaScript).
- **Chi cerca.** Terapeuti, fisioterapisti, logopedisti e chi fa le loro fatture: sono i compratori di questi gestionali.
- **Domanda misurata.** Codici di psicoterapia: 90837 6.600 a **34 $**, 90791 5.400, 90834 4.400, 90847 2.400 a **94 $**, 90832 2.400, 90792 1.900, 90846 1.300. Fisioterapia: 97110 6.600, 97530 5.400, 97140 4.400, 97112 3.600, 97161 1.900, «physical therapy cpt codes» 6.600. Altri: logopedia 1.900 + 1.300, chiropratica 1.900 + 1.000, massaggio 1.300, agopuntura 1.300. Regole: «8 minute rule» 14.800, «modifier 95» 3.600, «place of service 10» 2.400. Patti tra Stati per esercitare a distanza: «psypact» 6.600 + 4.400, «counseling compact» 5.400, «pt compact» 1.900. **Totale ~120.000.**
- **Dato ufficiale letto.** File ufficiale CMS delle tariffe 2027 (`rvu27a`, uscito il **10/11/2026**, 3,9 MB, 200): per ogni codice i valori relativi, il fattore di conversione 2027 (**32,6286 $**) e i correttivi di 109 località. Esempio letto: 90837 ha valore totale 5,62 → circa 183 $ a livello nazionale, da correggere per località. Patti: sito del counseling compact 200, PT compact 200, PSYPACT 403 (DA RIPROVARE).
- **Rischio legale.** Il file dice: «CPT codes and descriptions only are copyright American Medical Association». Le cifre sono pubbliche, i codici e le descrizioni no. Si potrebbe limitare a ~40 codici con descrizioni scritte da noi, ma l'AMA difende i suoi diritti: **da decidere prima di costruire**.
- **Concorrenti letti (6).** PayerPrice (1.060 parole): tariffa nazionale 2026 per codice, 11.200 codici. FastRVU (753 parole): valori 2026, scrive «GPCI adjustments not applied». TheraThink (1.881 parole): tariffe 2026 e pagine per Stato. CarePaths: pagine codice × Stato quasi vuote (71 parole). Sessions Health (1.410 parole) e AAPC (842): spiegazione del codice. **Nessuno ha ancora il 2027**, e la tariffa per località è coperta poco. Ma sono siti automatici già forti: il vantaggio dura poche settimane.
- **Conto centrale.** 120.000 × 0,6 % = 720 visite × 4 % = 29 clic × 1,5 % = 0,43 prove × 40 % paganti (mia ipotesi) × 120 $ × 0,92 × 12 = ~230 €. Pubblicità ~60 €. **Totale ~290 €.** Prudente 45, ottimista 3.200.
- **Esito.** RISERVA: 10 €/ora, serve un sito nuovo (soglia 40 €/ora) e c'è il nodo AMA.

### E. Calcolatore del cartellino e degli straordinari per Stato — voto 4, RISERVA bassa

- **Chi paga.** Connecteam: la pagina pubblica oggi dice 25 % del primo anno; negli scaglioni dei dati pubblici 200 $ (piano mensile), 300 $ (annuale), 100-200 $ a contatto. Termini letti: esclusi solo i Paesi sotto sanzioni. Gusto 300 $ è già nel piano del sito Paycheck.
- **Domanda misurata.** «time card calculator» **201.000** a 4,8 $, «timesheet calculator» 49.500, «overtime calculator» 27.100 a 8,8 $, «payroll hours calculator» 22.200, «time and a half calculator» 14.800, «time card calculator with lunch» 6.600 a 9,4 $, «california overtime calculator» 2.400 a 21 $, modelli di turni 9.900 a 10 $ e di fogli ore 14.800. **Totale ~350.000** (esclusa «hours calculator» 368.000, troppo generica).
- **Dato ufficiale.** California (dir.ca.gov, 200): straordinario oltre 8 ore al giorno e doppia paga. Regola federale dell'arrotondamento (29 CFR 785.48): eCFR risponde 406 alla richiesta fatta, dol.gov 403: DA RIPROVARE.
- **Concorrenti letti (5).** calculator.net (1.503 parole): straordinari al giorno e alla settimana, arrotondamenti, stampa: **completo**. timecardcalculator.net: ha già la scelta «California». Clockify (4.930 parole) spiega anche la regola dei 7 minuti. Redcort: senza straordinari. calculatehours.com 403. **Nessun vuoto: quota 0,15 %.**
- **Conto centrale.** 325.000 × 0,15 % + 25.000 × 0,3 % = 565 visite. Pubblicità ~27 €. Il 3 % clicca = 17 clic × 0,7 % × 50 % × 200 $ × 0,92 × 12 = ~127 €. **Totale ~155 €.** Prudente 30, ottimista 1.500.
- **Esito.** RISERVA bassa: 14 ore, 11 €/ora. Ha senso solo se Paycheck prende visite: allora è una pagina in più a costo basso.

### F. Non profit — voto 3,5, NO

- **Pagatori.** Zeffy (in media 500 $ a iscrizione, 3,8 iscrizioni ogni 100 clic) sarebbe stato il migliore, ma i termini letti dicono: «open to individuals, agencies, and consultants located in the United States, Canada, and the UK». **Italia fuori.** Aplos: 250 $ a cliente, 0,5 iscrizioni ogni 100 clic.
- **Domanda.** «how to start a nonprofit» 14.800 a 9 $; per Stato: Texas 1.300, California 1.000, Florida 880, Ohio 480, Georgia 260; «990-n» 8.100; «501c3 application» 6.600 a 12 $; «form 1023-ez» 4.400; «nonprofit bylaws template» 4.400; «when are 990s due» 2.400; lotterie di beneficenza ~4.000 in tutto. ~62.000 con la stima degli altri Stati.
- **Dato ufficiale.** IRS (scadenze del modello 990): 200.
- **Conto.** 250 visite × 3 % × 0,5 % × 250 $: ~115 €/anno, 40 ore. Concorrenti non letti (non è finalista).

### G. Licenze degli artigiani per Stato — voto 3,5, NO

- Riga del 31/10 («licenza da impresa edile per Stato», voto 5, pagatore non letto) riaperta con il pagatore scritto: Housecall Pro.
- **Domanda.** California 40.500 (in gran parte ricerca del registro), Florida 8.100, North Carolina 6.600, Texas 4.400, Georgia 2.900; elettricista Texas 1.900, idraulico Texas 1.900, climatizzazione Texas 1.600; «handyman license» 2.400, California 880, Florida 590.
- **Perché NO.** Housecall Pro ha già una pagina per Stato e per mestiere (California tuttofare: **7.105 parole**, aggiornata al 2026, con la nuova soglia di 1.000 $): il pagatore è anche il primo concorrente. Tradify non ammette editori italiani. Contractor Foreman: 0,05 iscrizioni ogni 100 clic.

### H. Calcolatori per investitori immobiliari — voto 3, NO

- **Domanda forte:** «dscr loan» 60.500 a 9,6-14 $, «cap rate calculator» 14.800, «rental property calculator» 9.900, «fix and flip loans» 6.600 a 27 $, «dscr loan calculator» 4.400, «hard money calculator» 3.600, «fair market rent hud» 5.400. File HUD degli affitti 2027: 200.
- **Perché NO.** BetterLife (700 $ a prestito, 3,5 iscrizioni ogni 100 clic) paga solo a chi ha compilato il modulo W-9 e ha un conto ACH: i termini letti lo scrivono. Senza pagatore restano ~30 €/anno di pubblicità. Si riapre con un altro prestatore che accetta editori europei.

### I, L, M. Fornitori, ristoranti, Canada — NO

- **Pagamenti ai fornitori.** «accounts payable software» ha un costo per clic di 118-230 $, «pay vendors» 5.400 a 27-43 $, «ach payment» 74.000: sono ricerche commerciali o generiche, senza un dato ufficiale da offrire. Nickel paga solo dopo 10 pagamenti del cliente. Forwardly: «fino a 1.000 $» ma la base letta è 100 $.
- **Ristoranti.** «food truck license» 9.900, «liquor license texas» 2.400, «how much is a liquor license» 2.400. Owner serve ristoranti già aperti con ordini in linea e ha 0,2 iscrizioni ogni 100 clic.
- **Canada.** «taxcycle» 1.900 (ricerca del marchio), «t4 deadline» 1.300, «efile cra» 1.000: troppo poco per TaxCycle (250 $).

## 5. Cosa ho imparato per i prossimi giri

1. **Il dato «iscrizioni per clic» della rete ordina i pagatori meglio della cifra scritta.** Boulevard scrive 1.500 $ ma converte 0,02 clic su 100; Checkr scrive 25 $ ma converte 11,8. Valore di un clic, a occhio: Shopmonkey ~5 $, 800.com ~1,9 $, Checkr ~1,2 $, terapeuti ~0,7 $, Housecall ~0,5 $.
2. **Leggere sempre i termini prima del conto.** Tre pagatori su dodici escludono un editore italiano per iscritto (Zeffy, Tradify) o di fatto (BetterLife, W-9).
3. **Con questi compensi il limite è il traffico, non il pagatore.** Per fare 5.000 €/anno con Shopmonkey servono ~70 clic al mese, cioè ~1.200 titolari di officina al mese: la domanda intera del settore è 25.000. Il metodo dà idee da 300-1.000 €, buone come sezioni, non siti.
4. **Il file CMS delle tariffe 2027 si scarica senza blocchi** (uscito il 10/11): utile se si decide il nodo AMA.

## 6. Cosa NON ho potuto leggere

- Termini di affiliazione di SimplePractice (pagina in JavaScript) e di Shopmonkey (rimanda ai termini generali).
- California «Write It Right» (404 all'indirizzo provato), leggi di California e New York sui controlli (403), FCC e Somos sui numeri verdi (403, 404), eCFR e dol.gov sugli straordinari (406, 403), PSYPACT (403).
- Quanti contatti diventano clienti paganti per ogni programma: le quote usate (30-60 %) sono ipotesi mie.
- Concorrenti delle idee F, I, L, M (non finaliste).

## 7. Iscrizioni che servirebbero a Massimiliano (solo se la prova parte)

- **Shopmonkey** su PartnerStack (idea A): 10 minuti, dopo le prime 100 visite al mese.
- **800.com** su PartnerStack (idea B): solo se si costruisce la riga 9.
- **Checkr** su PartnerStack (idea C): solo se Statute Limits prende impressioni.
- Nessuna spesa. Il conto PartnerStack è lo stesso già previsto per Gusto.
