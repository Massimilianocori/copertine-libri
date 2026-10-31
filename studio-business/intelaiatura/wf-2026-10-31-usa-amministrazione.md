# USA, amministrazione di tutti i giorni (non immobiliare) — ricerca del 31/10/2026

**Angolo:** le pratiche che un americano fa con lo Stato nella vita normale: patente e DMV (costi, tempi, esami), passaporti, USCIS, sussidi (disoccupazione, SNAP, Medicare), licenze professionali, esami (SAT/ACT/GED). Case e imprese le copre un altro ricercatore.

**Prove, tutte del 31/10/2026:** `curl` dal nostro server (codice HTTP e dimensione), Google Autocomplete (`suggestqueries.google.com`, `client=firefox`, `hl=en`, `gl=us`; il numero dopo la domanda è quante varianti propone, massimo 10), ricerca web fatta dagli USA per vedere chi c'è in prima pagina. Nessun blocco anti-robot aggirato: quando un sito risponde 403 lo scrivo e mi fermo.

**Metro dei soldi (dal cruscotto, 30/10):** AdSense in inglese 6-10 € ogni 1.000 visite; per i pubblici dei sussidi (persone con reddito basso) uso 4-8 €; per i temi Medicare, dove compaiono annunci di assicurazioni, 10-25 €. La rete oggi fa circa 1.300 visite al mese in tutto: le stime a 18 mesi sotto sono prudenti di proposito.

---

## 1. Verdetto in breve

**Nessuna idea passa l'asticella dei siti nuovi** (voto ≥ 7 e ≥ 5.000 €/anno nel caso centrale). Il miglior voto è **5,5**. Nessuna proposta a Massimiliano.

Perché l'angolo è povero, con le prove:
1. **I siti federali più utili ci chiudono la porta.** Dal nostro server rispondono 403 (Akamai "Access Denied"): `ssa.gov` (tutte le pagine provate, anche i dati aperti), `travel.state.gov`, `uscis.gov` ed `egov.uscis.gov`, `dol.gov`, `bls.gov`, `tsa.gov`, `cdc.gov/nchs/w2w`. `data.ssa.gov` non risponde (000).
2. **Dove la fonte è aperta, c'è già chi fa pagine automatiche con gli stessi dati:** sussidi di disoccupazione (indeedflex, fedratecalc, pagine `pages.dev`, perfino un pacchetto Apify sui dati DOL), scuole CDL (otrucking.com con una pagina per scuola), invalidità (mybenefitsdata.org, benefitsusa.org, aboutssdi.com), licenze professionali (getlicensemap.com con professione × Stato di partenza × Stato di arrivo).
3. **I pubblici dei sussidi valgono poco in pubblicità**, e per Medicare le regole CMS sul marketing impediscono le affiliazioni senza licenza da agente.
4. **Patente e DMV:** 50 enti diversi; su 14 pagine "nuovi residenti" provate, Massachusetts, Arizona, Colorado (403) e Illinois (000) sono chiusi; molti indirizzi cambiano (404).

**Cosa vale la pena tenere:** due fonti aperte, di pubblico dominio e aggiornate ogni mese, buone per il canale ChatGPT (numeri ufficiali precisi per Stato):
- **DOL ETA 9050** (`oui.doleta.gov/unemploy/csv/ar9050.csv`, 200, 5 MB, dati fino a settembre 2026): quanti primi pagamenti dei sussidi di disoccupazione arrivano entro 7, 14, 21… giorni, Stato per Stato, mese per mese.
- **USDA FNA** (ex FNS; `fns.usda.gov` ora rimanda a `fna.usda.gov`, 200): limiti di reddito SNAP dall'1/10/2026 al 30/9/2027, elenco ufficiale degli Stati che vietano bibite e dolci con lo SNAP, tassi di errore per Stato (aggiornati il 24/6/2026).

---

## 2. Tabella delle idee valutate

| # | Idea | Fonte (curl 31/10) | Domanda (autocomplete USA) | Chi c'è oggi | Chi paga | €/anno a 18 mesi (prudente / centrale / ottimista) | Ore | Voto |
|---|---|---|---|---|---|---|---|---|
| 1 | Disoccupazione per Stato: quanto si prende e **quanto in fretta paga ogni Stato** | DOL ETA 9050 CSV 200 (mensile, fino al 30/9/2026); "Significant Provisions" luglio 2026 PDF 200; pubblico dominio | "max unemployment benefits in" 10, "how much is unemployment in" 10, "how long does unemployment take to" 10 (ny, ct, washington state, massachusetts), "unemployment calculator" 10 | Calcolatori automatici in massa (indeedflex, fedratecalc, recordinglaw, pagine `pages.dev`), Apify; per la velocità solo giornali vecchi e siti spazzatura | AdSense | 120 / 670 / 3.240 | 25-35 | **5,5** |
| 2 | SNAP per Stato 2026-27: limiti di reddito, divieti di bibite e dolci, obblighi di lavoro, tassi di errore | FNA 200 (tabella 1/10/2026, mappa dei divieti con date, errori FY2025) | "snap income limits" 10, "snap soda ban" 10, "can you buy energy drinks with snap in" 10 Stati, "snap error rate by state" 10, "snap work requirements" 10 | Propel (app con il suo tracker), siti degli Stati, giornali, snapscreener | AdSense (pubblico che vale poco) | 70 / 480 / 2.400 | 20-30 | **4,5** |
| 3 | Medicare Savings Programs: limiti di reddito Stato per Stato | medicare.gov 200 (solo i valori nazionali); i limiti più alti vanno letti su 51 siti Medicaid | "medicare savings program income limits 2026" 10 Stati, "qmb income limits" 10 | medicare.gov, NCOA (PDF Stato per Stato), KFF (tabelle in parte vecchie), brevy.com automatico | AdSense con annunci assicurativi; affiliazioni Medicare vietate senza licenza da agente | 120 / 720 / 4.500 | 25-35 | **5** |
| 4 | Scuole per la patente da camion (CDL) per città: registrate o tolte dal registro FMCSA | `tpr.fmcsa.dot.gov` 200; interfaccia della pagina: 9.985 sedi tolte e 394 in revisione (contiene email e nomi di persone: si userebbero solo nome della scuola, città, stato) | "cdl schools in" 10, "cdl school cost in" 10 Stati, "free cdl training" 10, "non domiciled cdl" 10; "fmcsa removed cdl schools" 0, "cdl school removed" 4 | otrucking.com (una pagina per scuola), resumegeni, scuole stesse | Nessun programma per editori con cifra pubblica (solo un modulo di una scuola: 100 $ per studente) | 50 / 430 / 1.920 | 25-35 | **4** |
| 5 | Patente: "nuovo residente", scadenze e tasse una tantum per Stato | Campione di 14 pagine DMV: TX, PA, NV 200; MA, AZ, CO 403; IL 000; il resto indirizzi cambiati (404) | "transfer out of state license to" 10 Stati, "new resident dmv" 10 | Pagina ufficiale prima (es. NJ MVC), dmv.org, siti di traslochi | AdSense (annunci assicurazione auto); nessuna affiliazione assicurativa già nostra | 150 / 860 / 3.960 | 40-60 | **5** |
| 6 | Attese al DMV ufficio per ufficio e "ora migliore per andare" | Solo alcuni Stati pubblicano l'attesa in diretta: CT, OR, SC, GA 200; AZ, CO 403; pagina NC 404; CA senza dati nella pagina | "dmv wait times" 10 (nc, colorado springs, mn, sc, delaware, oregon, san diego) | Le pagine ufficiali (attesa in diretta), Google Maps ("orari di punta") | AdSense | 50 / 290 / 1.440 | 30-40 + robot ogni ora | **4** |
| 7 | Percentuale di promossi all'esame di guida per ufficio DMV | Nessun file pubblico: il DMV della California non pubblica il dato per ufficio; serve una richiesta di accesso agli atti (cioè contattare l'ente: escluso) | "easiest dmv to pass driving test in" 10 (los angeles, bay area, san diego, orange county, ct) | Zutobi ha già i dati FO21 della California (10 milioni di esami 2016-2025) | — | — | — | **3,5** |
| 8 | Invalidità (SSDI): approvazioni per Stato e per ufficio delle udienze | `ssa.gov` 403 su tutte le pagine, `data.ssa.gov` 000 | "ssdi approval rate by" 10, "ssdi approval rate by state" 7 | mybenefitsdata.org, benefitsusa.org, aboutssdi.com, studi legali con lo strumento per giudice | Contatti per avvocati (molto alti), ma fonte chiusa | — | — | **4** |
| 9 | Cambio del cognome dopo il matrimonio, Stato per Stato | SSA 403; 50 DMV; affiliazione HitchSwitch su Awin 200: "10%-15% commission" | "how to change last name after marriage in" 10 Stati | HitchSwitch e MissNowMrs stessi, The Knot, guide statali | HitchSwitch 10-15 % su pacchetti da circa 40-150 $ | 100 / 780 / 4.100 | 30-40 | **4,5** |

Conferme rapide di famiglie già chiuse (nessun fatto nuovo che le riapra):

| Famiglia | Prova del 31/10 | Esito |
|---|---|---|
| Tempi e centri dei passaporti USA | `travel.state.gov` 403 | NO confermato (idee-2026-10-23) |
| Tempi USCIS per ufficio | `egov.uscis.gov` e `uscis.gov` 403 | NO confermato (idee-2026-10-20, 30/10) |
| GED per Stato | home `ged.com` ora 200, ma le pagine di prezzo e regole per Stato 404 (pagine generate da JavaScript); "how much does the ged cost in" 10 | resta 6 come da ricerca-zona-usa-2026-10-30, nessun fatto nuovo |
| Date e centri SAT/ACT | `satsuite.collegeboard.org` e `act.org` 200, ma le date sono una tabella nazionale unica già prima su Google; i centri stanno dietro la ricerca di College Board e MyACT | NO (3) |
| Premio Medicare parte B e IRMAA 2027 | "medicare part b premium 2027" 10, "irmaa 2027" 10; un solo numero nazionale che CMS annuncia a novembre: rispondono subito medicare.gov e i grandi giornali | NO (3) |
| Reciprocità delle licenze professionali | "cosmetology license reciprocity" 10, "teaching license reciprocity" 10; in più oggi getlicensemap.com ha pagine automatiche professione × Stato × Stato | NO confermato (ricerca-zona-usa-2026-10-30, voto 4,5) |

---

## 3. Le idee una per una

### 3.1 Disoccupazione per Stato: importo e velocità di pagamento (voto 5,5)

**Cosa.** Una pagina per Stato (53 con DC, Porto Rico e Isole Vergini): sussidio minimo e massimo a settimana, settimane pagabili, settimana di attesa, regola del calcolo (dalla tabella DOL di luglio 2026) e soprattutto **la percentuale di primi pagamenti arrivati entro 7, 14 e 21 giorni**, mese per mese, con la classifica degli Stati. Aggiornamento automatico mensile dal CSV.

**Fonte.**
- `https://oui.doleta.gov/unemploy/csv/ar9050.csv`: 200, 5.047.873 byte, ultima riga "WY 2026-09-30". Colonne spiegate nel manuale `oui.doleta.gov/dmstree/handbooks/402/402_4/4024c6/4024c6.pdf` (200): c1 = primi pagamenti dentro lo Stato, c9 = entro 7 giorni, c17 = 8-14 giorni, c25 = 15-21 giorni, c5/c13/c21/c29 le stesse cose per le domande da un altro Stato.
- `https://oui.doleta.gov/unemploy/content/sigpros/2020-2029/July2026.pdf`: 200, 270 KB. Esempi letti: California massimo 450 $ a settimana, Florida 275 $, Mississippi 235 $, New Jersey 905 $, Texas 605 $, Washington 1.208 $.
- Licenza: opera del governo federale USA, pubblico dominio.
- Il mio conto su settembre 2026 (pagamenti entro 21 giorni sul totale, dentro e fuori Stato): **mediana degli Stati 87,2 %**; i più lenti Delaware 37,7 %, Michigan 50,1 %, Vermont 51,0 %, Washington 59,2 %; i più veloci North Dakota 98,0 %, Idaho 96,4 %, Tennessee 96,1 %; Florida 78,6 %, New York 83,2 %, Texas 84,6 %, California 90,5 %, Illinois 91,3 %. È un mio calcolo dal file ufficiale: prima di pubblicare va fatto controllare da un revisore indipendente sul metodo del DOL (che misura la tempestività con regole sue, 14 o 21 giorni a seconda della settimana di attesa).

**Domanda.** "max unemployment benefits in" 10 Stati (texas, california, florida, pa, nc, wisconsin, nj, ga, washington state); "how much is unemployment in" 10 Stati; "how long does unemployment take to" 10 (get approved in ny, process in ct, get approved in washington state e massachusetts); "unemployment calculator" 10 Stati; "unemployment benefits by state" 10 (2026, comparison, highest, lowest). "fastest unemployment payment by state" 0: la classifica in sé non è cercata, lo è il "quanto ci mette nel mio Stato".

**Chi c'è.** Per l'importo: un muro di calcolatori automatici (indeedflex.com per Stato, fedratecalc, recordinglaw, ustax.tools, tryascend, paychecktaxcalculator, `unemployment-calculator.pages.dev`, `layoffcalc.pages.dev`, perfino un pacchetto Apify "state-ui-provisions"). Molti hanno numeri vecchi o in contrasto (Washington 999 $ o 1.019 $ contro 1.208 $ della tabella di luglio): si batte sulla precisione, non sulla novità. Per la velocità: nessuno ha il dato Stato per Stato aggiornato; in prima pagina articoli del 2020-2023 e siti spazzatura. È il pezzo che un assistente AI citerebbe ("In Michigan solo il 50 % dei primi pagamenti di settembre 2026 è arrivato entro 21 giorni").

**Chi paga.** Solo AdSense. Pubblico di disoccupati: non metto prestiti né "soldi veloci" (sarebbe scorretto). Offerte di lavoro (ZipRecruiter, Indeed) non hanno un programma per editori con cifra letta oggi: non le conto.

**Stima a 18 mesi.** Visite al mese: 2.000 / 8.000 / 30.000; € per 1.000 visite: 5 / 7 / 9.
- Prudente 2.000 × 12 × 5 / 1.000 = **120 €**
- Centrale 8.000 × 12 × 7 / 1.000 = **672 € ≈ 670 €**
- Ottimista 30.000 × 12 × 9 / 1.000 = **3.240 €**
Primi soldi: non prima di 4-6 mesi dalla pubblicazione (serve un sito nuovo e l'approvazione AdSense).

**Ore.** 25-35 (lettore del CSV, tabella DOL da PDF, 53 pagine + classifica + aggiornamento mensile).

**Voto 5,5.** Fonte ottima e dato unico, ma non esiste un sito della rete adatto e come sito nuovo resta molto sotto l'asticella. **Unico uso sensato:** se Massimiliano approva il sito "US Small Business by State" (fronti-2026-10-31-nicchie-ricche, stessa tabella DOL), le pagine "quanto e quanto in fretta paga la disoccupazione" possono diventarne una sezione a costo quasi zero (stesso lettore della tabella), anche se il pubblico è diverso (lavoratori invece di datori).

### 3.2 SNAP per Stato 2026-27 (voto 4,5)

**Fonte.** `https://www.fns.usda.gov/snap/recipient/eligibility` → `fna.usda.gov` 200: tabella "Oct. 1, 2026, through Sept. 30, 2027", 1 persona 1.729 $ lordi e 1.330 $ netti al mese, 4 persone 3.575 $ e 2.750 $. `.../snap/waivers/foodrestriction` 200 (214 KB): elenco degli Stati con il divieto approvato, data d'inizio e cosa vieta (es. Arkansas 1/7/2026 bibite, bevande energetiche e dolci; Florida 20/4/2026; Idaho 15/2/2026; Hawaii 1/4/2027; Colorado annullato dal tribunale federale di Washington il 22/6/2026). `.../snap/qc/per` 200: tassi di errore per anno fino al 2025, pagina aggiornata il 24/6/2026. Pubblico dominio.

**Domanda.** Forte: "snap income limits" 10 (pa, texas, ny 2026, indiana, ohio, va 2026), "snap income limits 2027" 8, "snap soda ban" 10 (states, ohio, virginia, colorado, judge ruling, texas, alabama), "can you buy energy drinks with snap in" 10 Stati, "snap error rate by state" 10, "snap work requirements" 10.

**Chi c'è.** Propel (app per chi usa lo SNAP) ha già il suo elenco Stato per Stato dei divieti; giornali e TV locali per ogni Stato; snapscreener e i siti degli Stati per i limiti di reddito.

**Chi paga.** Solo AdSense, pubblico che vale poco (4-5 € ogni 1.000 visite al massimo). Nessuna affiliazione adatta e corretta.

**Stima.** Visite 2.000 / 10.000 / 40.000 al mese; € per 1.000: 3 / 4 / 5 → **70 / 480 / 2.400 €/anno** (2.000 × 12 × 3 = 72; 10.000 × 12 × 4 = 480; 40.000 × 12 × 5 = 2.400). Ore 20-30.

**Voto 4,5.** Domanda vera e fonte perfetta, ma soldi troppo pochi e un concorrente (Propel) che parla direttamente con lo stesso pubblico.

### 3.3 Medicare Savings Programs per Stato (voto 5)

**Fonte.** `medicare.gov/basics/costs/help/medicare-savings-programs` 200: solo i limiti nazionali 2026 (QMB 1.350 $, SLMB 1.616 $, QI 1.816 $ al mese per una persona; risorse 9.950 $). Gli Stati che danno di più (Alaska, Hawaii, Massachusetts senza limite di risparmi dal 2024, New Jersey, Connecticut, New York) vanno letti uno per uno sui 51 siti Medicaid: è il "filtro duro" della rete (nessun file unico).

**Domanda.** Forte e per Stato: "medicare savings program income limits 2026" 10 (california, ny, texas, massachusetts, indiana, florida, calculator), "qmb income limits" 10 (ct, washington state, texas, ny, tennessee).

**Chi c'è.** medicare.gov, NCOA (PDF Stato per Stato 2026), KFF (tabelle per Stato, in parte con valori vecchi), brevy.com con pagine automatiche per Stato, siti degli Stati.

**Chi paga.** AdSense con annunci assicurativi (10-25 € ogni 1.000 visite). Le affiliazioni Medicare (piani Advantage e integrativi) passano da agenti con licenza e regole CMS sul marketing: non sono per noi.

**Stima.** Visite 1.000 / 4.000 / 15.000 al mese; € per 1.000: 10 / 15 / 25 → 1.000 × 12 × 10 / 1.000 = 120; 4.000 × 12 × 15 / 1.000 = 720; 15.000 × 12 × 25 / 1.000 = 4.500 → **120 / 720 / 4.500 €/anno**. Ore 25-35 più un controllo all'anno su 51 siti (gennaio-aprile). Tema sanitario ed economico (YMYL): Google premia i siti con autorità.

**Voto 5.**

### 3.4 Scuole CDL registrate o tolte dal registro, per città (voto 4)

**Fonte.** `tpr.fmcsa.dot.gov` 200. La pagina "Location/Removed" chiede i dati a `/api/Location/RemovedOnly` (POST, la stessa chiamata del browser): **9.985 sedi tolte**; "InReviewOnly": **394 in revisione**. Le righe contengono anche email e nomi di persone: si potrebbero usare solo nome della scuola, città e stato, mai i contatti.

**Domanda.** "cdl schools in" 10 (houston, georgia, texas, florida, oklahoma, dallas), "cdl school cost in" 10 Stati, "free cdl training" 10, "non domiciled cdl" 10 (news, california, new rules, requirements). La notizia delle scuole tolte ha poche ricerche: "cdl school removed" 4 (con "3000 cdl schools removed"), "fmcsa removed cdl schools" 0.

**Chi c'è.** otrucking.com ha già una pagina per ogni scuola registrata (Houston: Papi Trucking School, AAA CDL School, Greenlight…), resumegeni.com ha l'elenco per Stato "FMCSA TPR-registered", più le scuole stesse e le aziende di trasporto.

**Chi paga.** Nessun programma per editori con cifra pubblica trovato; solo un modulo di una scuola che offre 100 $ per studente segnalato (non verificabile, e servirebbe un accordo diretto: escluso).

**Stima.** Visite 1.000 / 6.000 / 20.000; € per 1.000: 4 / 6 / 8 → 1.000 × 12 × 4 / 1.000 = 48; 6.000 × 12 × 6 / 1.000 = 432; 20.000 × 12 × 8 / 1.000 = 1.920 → **50 / 430 / 1.920 €/anno**. Ore 25-35.

**Voto 4.**

### 3.5 Patente per i nuovi residenti, Stato per Stato (voto 5)

**Cosa.** Entro quanti giorni cambiare patente e targa dopo il trasloco, cosa si porta, quanto costa, tasse una tantum dei nuovi residenti.

**Fonte.** Campione di 14 pagine "new residents": Texas DMV, Pennsylvania, Nevada 200; Massachusetts, Arizona 403; Illinois 000; Colorado (home) 403; le altre 404 per indirizzi cambiati. Con un quarto degli enti chiusi la soglia della rete (≥ 45 Stati su 51 leggibili) quasi certamente non si raggiunge.

**Domanda.** "transfer out of state license to" 10 (ma, nj, pa, georgia, california, ct, ny, texas, nc, florida), "new resident dmv" 10.

**Chi c'è.** La pagina ufficiale dello Stato è prima (es. NJ MVC "Moving to New Jersey"); poi dmv.org, helloskip, siti di traslochi. Battibile solo in parte.

**Chi paga.** AdSense (le pagine sulla patente attirano annunci di assicurazione auto). Nessun programma di assicurazione auto già aperto dalla rete; non lo conto.

**Stima.** Visite 1.500 / 9.000 / 30.000; € per 1.000: 8 / 8 / 11 → 1.500 × 12 × 8 / 1.000 = 144; 9.000 × 12 × 8 / 1.000 = 864; 30.000 × 12 × 11 / 1.000 = 3.960 → **150 / 860 / 3.960 €/anno**. Ore 40-60 (50 fonti a mano, 25 % chiuse).

**Voto 5.**

### 3.6 Attese al DMV e ora migliore per andare (voto 4)

**Fonte.** Solo alcuni Stati pubblicano l'attesa in diretta: `dmvselfservice.ct.gov/NemoService.aspx` 200, `oregon.gov/odot/dmv` 200, `scdmvonline.com/Locations` 200, `dds.georgia.gov/locations` 200; Arizona 403, Colorado 403, la pagina uffici della North Carolina 404, le pagine degli uffici della California senza dato di attesa. Servirebbe un robot che legge le attese ogni ora per mesi per costruire lo storico.

**Domanda.** "dmv wait times" 10 (near me, nc, colorado springs, mn, sc, delaware, oregon, san diego, right now).

**Chi c'è.** La risposta "adesso" la dà la pagina ufficiale; la risposta "a che ora c'è meno gente" la dà già Google Maps per ogni ufficio.

**Stima.** Visite 700 / 4.000 / 20.000 al mese a 6 € ogni 1.000 → 700 × 12 × 6 / 1.000 = 50; 4.000 × 12 × 6 / 1.000 = 288; 20.000 × 12 × 6 / 1.000 = 1.440 → **50 / 290 / 1.440 €/anno**. **Voto 4.**

### 3.7 Promossi all'esame di guida per ufficio (voto 3,5)

Domanda forte soprattutto in California: "easiest dmv to pass driving test in" 10 (los angeles, bay area, san diego, southern california, orange county, ct), "best dmv to take road test" 10. Ma il dato per ufficio non è pubblico: si ottiene solo con una richiesta di accesso agli atti (contattare l'ente, escluso), e Zutobi ha già pubblicato i dati FO21 della California (10.164.062 esami 2016-2025, 67,7 % di promossi). **NO.**

### 3.8 Invalidità SSDI per Stato e ufficio delle udienze (voto 4)

Domanda vera ("ssdi approval rate by" 10, "ssdi approval rate by state" 7) e il pubblico che paga di più dell'angolo (gli avvocati pagano molto per un contatto). Ma `ssa.gov` risponde 403 su ogni pagina provata (dati aperti, udienze, carichi di lavoro degli uffici statali) e `data.ssa.gov` 000; in prima pagina ci sono già siti costruiti apposta sugli stessi dati (mybenefitsdata.org con approvazioni per Stato e per fase, benefitsusa.org con le udienze 2026, aboutssdi.com) e strumenti per giudice degli studi legali. **NO.**

### 3.9 Cambio del cognome dopo il matrimonio (voto 4,5)

Domanda forte ("how to change last name after marriage in" 10 Stati). Affiliazione vera: HitchSwitch su Awin, "10%-15% commission on average" (`hitchswitch.com/affiliates` 200). Ma i primi su Google sono proprio HitchSwitch e MissNowMrs, che vendono il servizio, più The Knot e le guide statali; la parte federale (SSA) è 403; la parte statale sono 50 DMV.

**Stima.** Visite al mese 1.000 / 5.000 / 15.000. Vendite attribuite sul totale delle visite 0,05 % / 0,1 % / 0,2 %; pacchetto medio circa 90 $ × 12 % ≈ 10 € a vendita. AdSense a metà valore (3 € ogni 1.000 visite) perché le pagine portano il link.
- Prudente: 12.000 visite × 0,05 % = 6 vendite × 10 € = 60 €; AdSense 12.000 × 3 / 1.000 = 36 € → **circa 100 €**
- Centrale: 60.000 × 0,1 % = 60 vendite × 10 € = 600 €; AdSense 60.000 × 3 / 1.000 = 180 € → **circa 780 €**
- Ottimista: 180.000 × 0,2 % = 360 vendite × 10 € = 3.600 €; AdSense 180.000 × 3 / 1.000 = 540 € → **circa 4.100 €**
Ore 30-40. **Voto 4,5.**

---

## 4. Cosa resta da fare (per chi coordina)

1. **Nessuna riga nuova in "Idee in cantiere"**: nessuna idea supera 5,5.
2. **Da ricordare:** il file DOL ETA 9050 (`oui.doleta.gov/unemploy/csv/ar9050.csv`, pubblico dominio, mensile) è un dato unico Stato per Stato; se nasce il sito "US Small Business by State", le pagine disoccupazione (§ 3.1) diventano una sua sezione a costo quasi zero.
3. **Fonte da ricordare:** `fns.usda.gov` ora si chiama `fna.usda.gov` (rimando 301): chi la usa nei robot deve seguire il rimando.
4. **Lezione per i prossimi giri:** l'amministrazione federale USA è chiusa dal nostro server (SSA, Dipartimento di Stato, USCIS, DOL principale, BLS, TSA, CDC) e quella statale è divisa in 50 enti con un quarto chiusi. Il prossimo ricercatore cambi angolo invece di insistere qui. L'unica leva che riaprirebbe la famiglia è leggere i siti federali dai server di GitHub (prova già proposta il 17/10 per il passaporto americano): non è aggirare un blocco, ma va deciso da chi coordina, e anche con le fonti aperte i concorrenti automatici restano.

---

## 5. Fonti e prove (31/10/2026)

**Raggiungibili (200):**
- https://oui.doleta.gov/unemploy/csv/ar9050.csv (5.047.873 byte, fino al 30/9/2026)
- https://oui.doleta.gov/unemploy/content/sigpros/2020-2029/July2026.pdf
- https://oui.doleta.gov/dmstree/handbooks/402/402_4/4024c6/4024c6.pdf (mappa delle colonne ETA 9050, pag. 74)
- https://oui.doleta.gov/unemploy/DataDownloads.asp, https://oui.doleta.gov/unemploy/statelaws.asp, https://oui.doleta.gov/unemploy/data_summary/DataSum.asp
- https://www.fna.usda.gov/snap/recipient/eligibility (da fns.usda.gov), https://www.fna.usda.gov/snap/waivers/foodrestriction, https://www.fna.usda.gov/snap/qc/per
- https://www.medicare.gov/basics/costs/help/medicare-savings-programs, https://www.cms.gov/, https://data.cms.gov/
- https://tpr.fmcsa.dot.gov/ e le chiamate `/api/Location/RemovedOnly` (9.985) e `/api/Location/InReviewOnly` (394)
- https://www.dmvselfservice.ct.gov/NemoService.aspx, https://www.oregon.gov/odot/dmv/pages/offices/index.aspx, https://www.scdmvonline.com/Locations, https://dds.georgia.gov/locations
- https://www.txdmv.gov/motorists/new-to-texas, https://www.dmv.pa.gov/Driver-Services/Driver-Licensing/Pages/New-Residents.aspx, https://dmv.nv.gov/newresident.htm
- https://www.hitchswitch.com/affiliates (Awin, 10-15 %)
- https://satsuite.collegeboard.org/sat/dates-deadlines, https://www.act.org/, https://www.ged.com/ (home; pagine per Stato 404), https://hiset.org/

**Chiuse dal nostro server:**
- 403: https://www.ssa.gov/ (open/data, appeals, disability data, locator, ssa-performance), https://travel.state.gov/…/processing-times.html, https://egov.uscis.gov/processing-times/, https://www.uscis.gov/, https://www.dol.gov/, https://www.bls.gov/, https://www.tsa.gov/, https://www.cdc.gov/nchs/w2w/index.htm, https://azdot.gov/mvd/…, https://dmv.colorado.gov/, https://www.mass.gov/…rmv…
- 000: https://data.ssa.gov/, https://www.ilsos.gov/…

**Concorrenti visti in prima pagina (ricerca web dagli USA):** indeedflex.com, fedratecalc.com, recordinglaw.com, ustax.tools, tryascend.com, unemployment-calculator.pages.dev, layoffcalc.pages.dev, apify.com/retrainmap/state-ui-provisions (disoccupazione); propel.app (SNAP); ncoa.org, kff.org, brevy.com (Medicare Savings Programs); otrucking.com, resumegeni.com (CDL); zutobi.com (esame di guida California); mybenefitsdata.org, benefitsusa.org, aboutssdi.com (SSDI); helloskip.com, getlicensemap.com (patente e licenze).
