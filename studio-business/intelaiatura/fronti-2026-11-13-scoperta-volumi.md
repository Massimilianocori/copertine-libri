# Scoperta a volumi: tabelle, codici ed elenchi ufficiali aperti in 10 Paesi (13/11/2026)

Solo ricerca: nessun sito modificato. Settori di partenza lontani dalle zone battute: **telefonia, rimborsi di viaggio dei dipendenti, risparmio e pensione, studio, fisco delle vendite, cibo, codici fiscali esteri**. Metodo: prima il volume vero, poi il dato ufficiale, poi i concorrenti.

## In breve

- **677 ricerche di volume** (us 354, gb 69, it 52, de 44, ca 32, in 28, fr 24, br 24, au 24, es 23, pl 2, pt 1). Nessun errore dello strumento. Circa 300 per la scoperta, 240 per approfondire le code, 140 per rimisurare la riserva.
- **Una famiglia è di un altro ordine di grandezza: i prefissi telefonici USA.** 36 prefissi misurati, media 100.000 ricerche al mese l'uno, mediana 74.000 ("347 area code" 246.000, "404 area code" 165.000, "906 area code" 22.200). I prefissi geografici USA in servizio sono 378 (file ufficiale di oggi): **circa 20 milioni di ricerche al mese**, costo per clic mediano 1,8 $. Mai toccata in `ESPLORATE.md`.
- Centrale a 36 mesi **6.300 €/anno per 45 ore (140 €/ora)**: è la prima idea della coda per euro all'ora, sopra i militari USA (115). Ma la quota usata (0,2 %) è un'ipotesi: Google mostra la località nel riquadro e il primo concorrente non si è lasciato leggere (403).
- **Due sezioni economiche da aggiungere a siti che esistono o sono in coda**: diarie e rimborso chilometrico federali (un solo file ufficiale, 18 ore, 74 €/ora) e limiti 401(k)/IRA/Roth/HSA con calcolatore (20 ore, 68 €/ora).
- Le altre sette sono riserve: volume grande ma resa bassa (cibo, Brasile, CAP), dato sparso (imposta sulle vendite, salario minimo) o fonte che non si legge dal server (aiuti allo studio, Canada).
- **Riserva rimisurata: 59 righe.** Quasi tutte scendono: le teste misurate sono sotto 10.000 ricerche al mese o hanno clic da pochi centesimi. Sale solo il Balkonkraftwerk tedesco (368.000 al mese a 3,63 €).

Limiti, detti prima dei numeri:
- I volumi sono medie mensili Google Ads; frasi vicine con lo stesso numero sono lo stesso gruppo e sono contate una volta.
- Le code sono **estese da campioni** (scritto ogni volta quanti). È la parte più debole.
- La pagina dei risultati di Google non è stata letta (i motori bloccano il server). Non so quante ricerche finiscono senza clic: per questo le quote sono sotto lo 0,5-3 % della taratura dove Google risponde da solo.
- "product recall" dà 301.000 negli USA e 246.000 identici in Regno Unito e Canada: numero sospetto, non usato.
- Formula della casa: ricerche al mese × 12 × quota × 1,3 pagine a visita × incasso per 1.000 pagine × 0,92. A 12 mesi: un terzo della quota centrale.

## 1. Le dieci famiglie, in ordine di €/ora

Cifre in €/anno. "Usate" = misurate + coda estesa.

| # | Famiglia | Paese | Ricerche al mese (misurate → usate) | Costo per clic | Dato e licenza | 12 mesi | 36 mesi prudente / centrale / ottimista | Ore | €/ora | Esito |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Prefissi telefonici (area codes), una pagina per prefisso, Stato e città | US (+CA) | 3.600.000 su 36 prefissi → 20.000.000 | 0-10 $, mediana 1,8 | NANPA, CSV pubblico di oggi (200); reclami sulle chiamate indesiderate FTC (API 200, dominio pubblico) | 2.100 | 1.150 / 6.300 / 24.100 | 45 | 140 | **COSTRUIRE** (sito nuovo, dopo verifica indipendente) |
| 2 | Diarie federali per località (per diem) + rimborso chilometrico | US | 240.000 → 330.000 | 0-15 $ | GSA, file xlsx 2026 e 2027 (200), dominio pubblico; IRS (200) | 440 | 240 / 1.330 / 4.260 | 18 | 74 | **COSTRUIRE** come sezione del sito paghe militari |
| 3 | Limiti 401(k), IRA, Roth, HSA per anno + calcolatore del limite Roth per reddito | US | 850.000 | 2-4 $ | IRS, comunicato annuale (200), dominio pubblico | 460 | 245 / 1.370 / 5.120 | 20 | 68 | **COSTRUIRE** come sezione del sito dell'inflazione |
| 4 | Aiuti allo studio: scadenze FAFSA, tassi dei prestiti federali per anno, Pell, Grad PLUS | US | 400.000 | 10-47 $ | Tassi: Federal Register (API 200, avvisi del 10/9/2026), dominio pubblico. Scadenze per Stato: studentaid.gov è una pagina vuota senza JavaScript | 460 | 230 / 1.380 / 5.170 | 30 | 46 | RISERVA alta |
| 5 | Salario minimo per Stato, città, provincia e Paese con gli aumenti già decisi | US, GB, CA, AU | 1.500.000 su 8 Stati e 4 Paesi → 2.900.000 | 2,5-10 $ | gov.uk 200 (OGL); dol.gov 403: 50 fonti statali a mano | 670 | 500 / 2.000 / 9.160 | 40 | 50 | RISERVA (riapre i NO del 22/10 e 12/11: fatto nuovo, i volumi) |
| 6 | Codici fiscali brasiliani (CNAE, CBO, NCM, CFOP, CID-10) sul motore dei codici | BR | 680.000 → 1.400.000 | 0,2-0,6 $ | NCM: JSON ufficiale 200 (3,1 MB); CNAE: API IBGE non raggiunta | 300 | 200 / 900 / 4.020 | 25 | 36 | RISERVA, terzo blocco del motore |
| 7 | Valori nutrizionali per alimento (calorie, proteine, carboidrati) | US (+GB) | 1.150.000 su 16 alimenti → 8.000.000 | 0,1-1,3 $ | USDA FoodData Central, zip del 29/10/2026 (200), CC0 | 340 | 210 / 1.030 / 5.510 | 40 | 26 | RISERVA |
| 8 | Imposta sulle vendite (sales tax) per Stato e città + calcolatore | US | 400.000 → 1.500.000 | 3-15 $ | Nessun file unico: Texas tabella 200 (4.898 righe), California 200, 24 Stati con file comuni (pagina indice 200, pagina dei file per Stato 404) | 720 | 390 / 2.150 / 8.270 | 90 | 24 | RISERVA |
| 9 | CAP per città (zip codes), secondo blocco del sito dei prefissi | US | 300.000 su 6 città → 5.000.000 | 0-3 $ | Census, elenco ZCTA (zip 200), dominio pubblico; l'elenco USPS non è aperto | 240 | 115 / 720 / 3.440 | 30 | 24 | RISERVA |
| 10 | Date dei pagamenti pubblici canadesi (CPP, OAS, GST, ODSP, AISH) | CA | 290.000 | 0-5 $ | canada.ca non risponde al server (000) | 290 | 210 / 870 / 3.000 | 12 | 73 | RISERVA bloccata dal dato |

Quote e incasso per 1.000 pagine usati (prudente / centrale / ottimista): 1) 0,05 / 0,2 / 0,6 % e 8 / 11 / 14 $; 2) 0,5 / 2 / 5 % e 10 / 14 / 18 $; 3) 0,1 / 0,4 / 1,2 % e 20 / 28 / 35 $; 4) 0,2 / 0,8 / 2 % e 20 / 30 / 45 $; 5) 0,1 / 0,3 / 1 % e 12 / 16 / 22 $; 6) 0,5 / 1,5 / 4 % e 2 / 3 / 5 $; 7) 0,03 / 0,1 / 0,4 % e 6 / 9 / 12 $; 8) 0,1 / 0,4 / 1,2 % e 18 / 25 / 32 $; 9) 0,02 / 0,1 / 0,4 % e 8 / 10 / 12 $; 10) 0,5 / 1,5 / 4 % e 10 / 14 / 18 $.

## 2. Le prime cinque: volumi, dato, concorrenti

### 1. Prefissi telefonici USA — COSTRUIRE

| Voce | Che cosa ho letto |
|---|---|
| Volumi (us) | 347: 246.000 (2,10 $); 929: 246.000 (1,19 $); 213: 450.000 (3,33 $); 202, 404, 469, 206: 165.000; 305, 833: 135.000; 657, 239: 110.000; 212, 505, 540, 631, 737, 913, 855: 90.500; 252, 318, 864: 74.000; 307, 409, 605, 775, 814: 60.500; 435, 586, 701, 989, 260: 49.500; 888: 40.500; 445: 33.100; 906, 947: 22.200; 800: 14.800 |
| Come arrivo a 20 milioni | 378 prefissi geografici × 53.000, cioè sotto la mediana misurata (74.000) perché il campione può pendere verso i prefissi delle grandi città. Con la media misurata sarebbero 38 milioni |
| Teste | "area codes" 110.000 (0,79 $), "area code lookup" 33.100 (1,29 $), "california area codes" 33.100, "new york area codes" 49.500, "area code map" 18.100 |
| Canada | "437 area code" 74.000, "416 area code" 27.100, costo per clic 0 |
| Regno Unito | "0161 area code" 27.100, "0203" 12.100, "020" 9.900, costo per clic 0: non conviene |
| Dato | `reports.nanpa.com/public/npa_report.csv`: 200, 117 KB, data del file 13/11/2026, 800 codici; per ognuno Stato, data di entrata in servizio, sovrapposizioni, fuso, regole di composizione. In servizio: 398 USA (378 geografici), 58 Canada. Anche le previsioni di esaurimento (xlsx 200) |
| Licenza | Nessuna licenza scritta trovata (pagina dei termini 404). Sono dati di fatto pubblicati dall'amministratore del piano per conto della FCC: si usano citando la fonte, senza copiare testi |
| Dato in più | FTC, reclami "Do Not Call": API 200 con chiave dimostrativa, righe fino al 10/11/2026 con prefisso del chiamante e "chiamata registrata sì/no". Dominio pubblico. Si pubblicano **solo i conteggi per prefisso**, mai i numeri interi (possono essere di persone) |
| Concorrenti letti | area-codes.com/929: 1.172 parole, pubblicità (AdPushup), nessuna data, fuso o sovrapposizione. zip-codes.com: 2.959 parole, fuso, sovrapposizione, CAP. areacodes.com: 614 parole, tre righe generiche sulle truffe. Wikipedia: storia completa. allareacodes.com e callersmart: 403, non letti |
| Che cosa manca a loro | Nessuno dei tre letti dà: data ufficiale di servizio, prossima sovrapposizione prevista, **quanti reclami per chiamate indesiderate arrivano da quel prefisso questo mese**. È la domanda vera di chi cerca "929 area code" dopo una chiamata sconosciuta |
| Pagatore | Solo pubblicità. Le affiliazioni di "ricerca inversa del numero" vendono schede di persone: escluse |
| Rischi | Riquadro di Google con la località (quota incerta); 0,2 % sono 40.000 visite al mese, più di tutta la rete di oggi; serve un dominio; la chiave FTC gratuita la deve chiedere Massimiliano (2 minuti) |

Prova proposta prima del sito intero: 60 pagine (i 50 prefissi più cercati + 10 Stati), 15 ore, 60 giorni. Si va avanti se arrivano almeno 3.000 impressioni al mese.

### 2. Diarie federali e rimborso chilometrico — COSTRUIRE come sezione

| Voce | Che cosa ho letto |
|---|---|
| Volumi (us) | "gsa per diem" 74.000 (15 $ su una variante, 0 sull'altra), "per diem rates" 27.100 (10,7 $), "gsa rates" 12.100, "foreign per diem rates" 4.400, "per diem rates washington dc" 4.400, "dod per diem rates" 2.900, "per diem calculator" 5.400 (6,85 $). Rimborso chilometrico: "irs mileage rate 2025" 60.500 (2 $), "mileage reimbursement irs" 12.100, "irs mileage rate" 9.900, "mileage reimbursement rate" 5.400 (6,2 $), "mileage reimbursement calculator" 5.400 (5 $) |
| Coda | Per città: San Diego 1.900, New York 1.600, Las Vegas 1.300, Chicago 1.000, Denver, Orlando, Atlanta 880, Boston 720; tutte a 0 $. Estesa a 300 aree × 300 = 90.000. Non usata la testa generica "per diem" (135.000, è la definizione) |
| Dato | `FY2026_PerDiemMasterRatesFile.xlsx` 200 (652 righe) e file 2027 già pubblicato; API GSA 200 con tariffe mese per mese. Dominio pubblico |
| Concorrenti | gsa.gov: strumento ufficiale, letto (2026 e 2027 presenti). federalpay.org e perdiem101.com: 403, non letti. Il vuoto non è dimostrato |
| Dove va | Stesso pubblico del sito paghe militari già in coda (dipendenti federali e militari in missione): seconda sezione, stesso dominio |
| Rischio | Chi cerca "gsa per diem" vuole il sito GSA; i clic a 0 $ sulla coda |

### 3. Limiti dei conti pensione e sanitari — COSTRUIRE come sezione

| Voce | Che cosa ho letto |
|---|---|
| Volumi (us) | 401(k): "401k contribution limits 2025" 135.000 (3,87 $), "401k 2025 contribution limit irs" 60.500, "401k max contribution 2025" 49.500, "401k limit 2025" 33.100. Roth: "roth ira income limits" 90.500 (2,12 $), "roth ira contribution limits 2025" 90.500, "roth ira contribution limits" 33.100. IRA: 40.500 + 27.100 + 18.100. HSA: 49.500 (3,88 $) + 33.100 + 27.100 + 14.800. SEP 12.100, SIMPLE 12.100, 529 12.100, "backdoor roth" 27.100 |
| Dato | Comunicato IRS con i limiti 2026 (200; 401(k) 24.500 $, IRA 7.500 $). Dominio pubblico. Circa 40 pagine: conto × anno × età |
| Concorrenti letti | Fidelity (3.880 parole), NerdWallet (4.028), Schwab (2.381): tutti con 2026 e 2027. Nessun vuoto: è solo quota |
| Che cosa manca a loro | Poco: una tabella unica di tutti i conti per anno dal 2015 e il calcolo del limite Roth ridotto per reddito in una riga |
| Dove va | Sezione del calcolatore dell'inflazione (online, finanza personale USA) |
| Rischio | Google mostra la cifra; i primi sono banche e marchi fortissimi |

### 4. Aiuti allo studio USA — RISERVA alta

| Voce | Che cosa ho letto |
|---|---|
| Volumi (us) | "fafsa deadline 2025" 90.500 (11,3 $), "fafsa deadline" 60.500 (10 $), "when is fafsa due" 27.100; "student loan interest rates" 40.500 (43 $), "student loan interest rate" 33.100 (22 $); "grad plus loan" 22.200 (31 $); "student aid index" 18.100; "parent plus loan interest rate" 9.900 (47,5 $); "pell grant amount" 5.400 (23 $). Per Stato quasi nulla (California 1.600, Texas 720). "fafsa school code": nessun dato |
| Dato | Tassi: avvisi annuali sul Federal Register letti dall'API. Scadenze per Stato: la pagina ufficiale non si legge dal server |
| Concorrenti letti | NerdWallet (13.718 parole, tassi 2026-27, 36 rimandi al rifinanziamento), Bankrate, Saving for College (tabella delle scadenze per Stato), finaid.org (storico dei tassi) |
| Perché riserva | I clic più cari del file, ma nessuna cifra scritta di un programma letta e la tabella per Stato non viene da una fonte ufficiale leggibile. Assorbe la riga del 9/11 sui tetti dei prestiti |

### 5. Salario minimo — RISERVA

| Voce | Che cosa ho letto |
|---|---|
| Volumi | us "minimum wage" 110.000 (10,4 $), California 135.000 (2,8 $), Florida 110.000, Texas e New York 90.500, Washington e Ohio 49.500, Seattle 18.100, Wyoming 4.400. gb 550.000 (5,2 £). ca Ontario 165.000 (7,1 $), BC 40.500. au 60.500 (4,2 $). de 165.000 a 0,38 €, fr "smic" 201.000 a 0 €, es 40.500 a 0,2 €, br 450.000 a 0,09: fuori |
| Dato | gov.uk 200. dol.gov 403 come il 22/10: negli USA 50 pagine statali da leggere a mano |
| Concorrenti | Paycor letto (4.885 parole; "2026" 39 volte, "2027" una sola). minimum-wage.org, EPI, NCSL, ADP: 403 |
| Che cosa manca | Gli aumenti del 1/1/2027 già decisi, Stato per Stato e città per città, con la data |
| Perché riserva | Una cifra per pagina, che Google mostra da solo; dato statale sparso |

## 3. Semi misurati e scartati

| Seme | Paese | Volume al mese | Costo per clic | Perché no |
|---|---|---|---|---|
| federal poverty level | US | 450.000 (+ "2025" 27.100) | 0,08-0,3 (coda 3,4 $) | testa senza valore, coda piccola |
| social security payment schedule, ssi payment schedule, irs refund schedule | US | 110.000 + 90.500 + 60.500 + 40.500 + 74.000 | 1,5-5,3 $ | già NO il 14/10 e il 30/10. Con la regola della quota varrebbe circa 1.000 €/anno per 12 ore: da ridiscutere, non contata qui |
| federal holidays 2025 | US | 201.000 | 8,1 $ (0 sul 2026) | calendari già NO |
| pill identifier; "l484 pill" | US | 1.220.000; 74.000 | 1,5-3 $ | rischio sanitario (riconoscere una pillola), drugs.com |
| n number lookup, faa registry | US | 27.100 + 18.100 | 4,3 $ | il registro contiene nomi di proprietari |
| rmd calculator, rmd table | US | 90.500 + 22.200 | 0,5-0,8 $ | clic basso |
| fha / conforming loan limits | US | 9.900 + 6.600 | 4,6-9,6 $ | piccola; per contea 70-1.000 |
| cage code, duns, uei lookup | US | 12.100 / 18.100 / 8.100 | 5,7-13 $ | navigazione verso SAM e D&B |
| hcpcs codes, drg, ndc lookup, taxonomy code | US | 12.100 / 27.100 / 14.800 / 4.400 | 2-10 $ | piccole: al più pagine del blocco ICD |
| workers comp class codes | US | 5.400 | 10-13 $ | elenco NCCI protetto |
| how much is a stamp, postage rates | US | 60.500 + 9.900 | 1,5-5,3 $ | una cifra |
| prevailing wage, davis bacon | US | 22.200 + 4.400 | 5-7 $ | piccola, tabelle per contea su SAM |
| postcode finder, state pension, epc register, ulez check, sort code checker | GB | 1.000.000 / 1.000.000 / 246.000 / 201.000 / 60.500 | 0,6-3 £ | navigazione verso il servizio ufficiale o dato a licenza |
| tax code, tax code 1257l, personal allowance | GB | 74.000 / 22.200 / 165.000 | 2-5,6 £ | poche pagine, gov.uk primo; possibile pagina singola |
| statutory sick pay, redundancy pay, pip rates | GB | 90.500 / 22.200 / 74.000 | 2,7-3,9 £ | calcolatori gov.uk; famiglia sussidi già NO |
| stat holidays ontario, tfsa contribution limit, rrsp | CA | 49.500 / 49.500 / 22.200 | 1,5-3,4 $ | canada.ca non leggibile; festivi già NO |
| euribor hoy; iban calcular | ES | 823.000; 40.500 | 0,55; 1,56 € | Euribor con licenza dell'ente; resa bassa |
| kindergeld auszahlung, kfz kennzeichen, steuerklassen, kfz steuer rechner | DE | 165.000 / 135.000 / 110.000 / 135.000 | 0,8-1,7 € | una pagina sola o calcolatori già presenti |
| rappel conso, rappel produit | FR | 90.500 / 49.500 | 0,9-2,4 € | API non leggibile (riga del 12/11) |
| ifsc code, pin code, income tax slab, bank holidays, gold rate today | IN | 368.000 / 246.000 / 165.000 / 301.000 / 9.140.000 | 0-0,4 $ | clic da centesimi |
| tabela fipe, cep, calendário bolsa família, salário mínimo | BR | 2.240.000 / 823.000 / 1.500.000 / 450.000 | 0,03-0,7 | clic da centesimi, strumenti ufficiali |
| codice tributo, cap, scaglioni irpef, tabelle aci | IT | 18.100 / 49.500 / 27.100 / 4.400 | 0-0,6 € (ACI 3,9) | clic nullo |
| hsn code | IN | 90.500 | 0,86 $ | resa indiana |

## 4. Riserva rimisurata

Righe RISERVA / COSTRUIRE / IN CODA di `ESPLORATE.md` dal 1/11/2026 con volume non misurato. Una riga ciascuna; "centrale" = €/anno a 36 mesi con la formula della casa. Non rimisurate: libri, prodotti e lavori interni (non sono ricerche su Google) e le righe già misurate il 12-13/11.

| Riga (data) | Teste misurate oggi | Effetto |
|---|---|---|
| Prodotti ritirati per marca e tipo (19/10) | us "food recalls" 110.000 a 3,37 $, "fda recalls" 49.500, "costco recall" 90.500, "egg recall" 90.500, "ground beef recall" 60.500, "dog food recall" 60.500, "walmart recall" 40.500; de "lebensmittelwarnung" 27.100; ca "food recall" 18.100. API CPSC e openFDA 200, FSIS 403 | resta RISERVA: circa 600.000 usate, 90 / 600 / 2.300, 35 ore, 17 €/ora (domanda di cronaca) |
| Balkonkraftwerk città per città, DE (7/11) | "balkonkraftwerk" 368.000 a 3,63 €, "mit speicher" 110.000 a 3,11 €, "förderung" 1.900 | **sale**: 190 / 1.100 / 4.400, 40 ore, 28 €/ora; la testa è d'acquisto, la coda per città è piccola |
| Contratti di lavoro per livello, IT (12/11) | "ccnl metalmeccanici" 33.100 a 0,23 €, "ccnl commercio" 22.200 a 0,39, "tabelle retributive ccnl commercio" 8.100 a 0,13, "paga oraria" 260 | scende: centrale circa 450 (era 2.000 a 18 mesi), clic da 0,1-0,4 € |
| Motore "quiz ufficiali" e i suoi blocchi (12/11) | "quiz patente nautica" 1.900-2.400 a 0,4-0,7 €, "patentino fitosanitario" 1.300, "quiz licenza di caccia" 260, "quiz ncc" 90, taxi, tartufi, gestore trasporti: 0 | scende: teste sotto 6.000 in tutto, pubblicità ≤ 300; regge solo se reggono i libri |
| Bollo auto per kW × Regione (12/11) | "bollo auto" 135.000 a 0,62 €, "calcolo bollo auto" 74.000 a 0,18; "bollo auto 2027" 0 | volume grande, clic da centesimi: centrale circa 200 |
| "Anni da evitare" per modello (13/11) | "toyota rav4 years to avoid" 3.600, "honda crv" 2.900, "ford f150" 1.600; clic 0,3-1 $ | confermata: circa 450.000 usate, centrale 650 |
| Tabelle pressione-temperatura dei refrigeranti (13/11) | "r410a pt chart" 5.400 a 0,01 $, "pt chart" 5.400, "410a pressure chart" 4.400, "r454b pt chart" 1.900, "superheat chart" 1.600 | **NO**: teste circa 20.000, clic zero |
| Multa per eccesso di velocità per tribunale, US (12/11) | "how much is a speeding ticket" 6.600 a 0,8 $, "in california" 5.400-6.600 | scende: centrale circa 300 |
| Costo del divorzio per contea, US (12/11) | "how much does a divorce cost" 9.900 a 3,42 $, "divorce cost" 3.600, "to file" 1.600 | piccola: centrale circa 400, tutta sull'affiliazione |
| Sconti sulla tassa sulla casa per anziani, US (12/11) | "senior property tax exemption" 1.600-3.600 a 3,2-4,2 $; "at what age…" 140 | scende: testa circa 7.000, coda per contea non misurabile |
| Interessi sulle sentenze, US (13/11) | "judgment interest calculator" 880-1.300, "post judgment interest" 480 | minima: solo una pagina del sito prescrizione (≤ 100) |
| Codice LEI (12/11) | it "codice lei" 8.100 a 8,30 €; us "lei lookup" 2.900 a 6,8 $; gb 1.300 a 8 £; de 1.900 a 6 € | piccola ma ricca: centrale circa 450 più commissioni non lette; l'Italia è la più forte |
| Tasse dei marchi per Paese (12/11) | us "trademark registration cost" 4.400 a 16,7 $, "trademark cost" 3.600 a 10 $; gb 260-390 | piccola ma ricca: centrale circa 300 |
| Payroll tax australiana (9/11) | "payroll tax" 8.100 a 5,9 $, "payroll tax nsw" 6.600 a 11 $, "calculator" 1.600 a 15,6 $ | confermata: teste circa 20.000, centrale circa 500 |
| Price to Compare, luce USA (9/11) | "ppl price to compare" 1.000 a 7 $, "peco" 480, "price to compare" 260; "compare electric rates" 8.100 a 14 $ | scende: RISERVA debole |
| Gradazione delle carte (9/11) | "psa grading" 110.000 a 0,16 $, "psa card grading" 33.100, "psa grading cost" 22.200 a 0,06 | volume alto, clic nullo: centrale circa 150 |
| Promossi per ufficio DMV (10/11) | 40-210 | **NO**: domanda quasi nulla |
| Lettere di violazione dei dati (10/11) | "data breach letter" 140; "data breach settlement" 3.600 | la pagina "lettera" non ha domanda: **NO** |
| Tetti dei prestiti federali (9/11) | "grad plus loan" 22.200 a 31 $; "grad plus loan limits" 260-320 | confluisce nella famiglia 4 di oggi |
| Filtro dal numero di modello (8/11) | "furnace filter size" 2.900 a 1,56 $; per modello 0 | conferma il ridimensionamento (≤ 400) |
| Libri di testo per scuola (8/11) | "libri di testo" 6.600 a 0,83 €, "adozioni libri scolastici" 2.900 | piccola e stagionale: non sopra 1.900 |
| Seggiolini: scadenza per marca (6/11) | "how long are car seats good for" 14.800, "car seat expiration" 6.600, Graco 4.400-5.400; clic 0,1 $ | scende: centrale circa 150 |
| Pannello da balcone USA e UK (6/11) | us 1.000-1.600 a 1,5-3 $; gb 590 | scende: famiglia sotto 5.000 |
| Altersvorsorgedepot, Frühstart-Rente (6/11) | 5.400 a 3,01 €; 3.600 a 2,67 € | resta con innesco: piccola, in crescita |
| Brasile, consumo dei condizionatori (7/11) | 2.400 + 1.900 a 0,2-0,5 | **NO**: piccola |
| CCSE + DELE A2 (6/11) | es "ccse" 9.900 a 0,86 €, "examen ccse" 2.400, "dele a2" 2.900 | teste circa 17.000: centrale circa 200 di pubblicità; resta RISERVA |
| Hotel prima della crociera (6/11) | "hotels near port canaveral" 40.500-49.500 a 2,8-3,3 $ | domanda vera per porto: resta il riquadro Stay22 |
| Patente straniera negli Stati USA (6/11) | 320-590 a 3,35 $ ("international driving permit" 110.000 è la ricerca del documento) | piccola |
| Trasparenza salariale UE (4/11) | gb "eu pay transparency directive" 880 a 18,6 £; de "entgelttransparenzgesetz" 5.400 a 1,34 € | piccola |
| Affitti in Spagna, zone tensionate (4/11) | "zonas tensionadas" 0; "indice precios alquiler" 2.900 a 0 | **NO**: clic zero |
| IFICI Portogallo (4/11); Euro 2028 (4/11) | 720 a 6,6 €; "euro 2028 tickets" 590 | minime; Euro 2028 resta con innesco |
| Tetto workers' comp (5/11) | "workers comp settlement chart" 1.300-4.400 a 7-12 $ | debole confermata |
| Karta pobytu per ufficio, PL (11/11) | "karta pobytu" 9.900 a 1,13, "stan sprawy" 18.100 a 0 | resa polacca bassa: centrale circa 150 |
| Küstenpatent; barca senza patente; patente B 4.250 kg (11/11) | 260-720; de 880, it 720-1.600; 170-880 ("wohnmobil führerschein" 5.400 a 0,23) | minime |
| Sposarsi in Italia; nulla osta (11/11) | us 390, gb 720; it 1.600-1.900 | minime: sotto 100 l'una |
| Warm Homes; tariffe dei council; pompe di calore UK (11/11) | 1.900 a 6 £ (prestiti 0); "garden waste collection" 14.800 a 2,5 £, "dropped kerb cost" 2.400; "heat pump cost" 8.100 a 7,3 £, "heat pump grant" 5.400 a 11,4, "boiler upgrade scheme" 4.400 | impianti UK confermato (teste ricche); tariffe dei council circa 250 |
| IMU dall'estero in tedesco (11/11) | "imu italien" 140, "grundsteuer italien" 170 | **NO** in tedesco |
| Sorteggi delle maratone in altre lingue (12/11) | de 110; fr "marathon paris 2026" 8.100 a 11 €, "inscription" 1.000 a 18 € | solo il francese ha domanda |
| PMA per Regione; Conto Termico; autovelox (12/11) | "pma" 14.800 (generica); "conto termico 3.0" 18.100 a 0,78 €; "autovelox" 74.000 a 1,78 €, "censimento autovelox" 0 | deboli: Conto Termico circa 150; autovelox testa generica |
| Uscita dei biglietti, +20 attrazioni (12/11) | "eiffel tower tickets" 110.000 a 5,7 $, "colosseum tickets" 74.000 | confermata IN CODA prima: teste grandi e d'acquisto |
| Power bank; e-gates; visto di transito; rimborso IVA (12/11) | us 2.900, gb 1.900-2.900 a 0,5; gb 1.300 a 4,3 £; us 1.600 a 3,3 $; gb 1.000-2.400 a 2,7-3 £ | piccole: restano sezioni da poche ore |
| Numerus fixus; rifiuti dei permessi nordici; PTE Australia; cerimonie di cittadinanza; medici designati (12/11) | 0; 0; 260-880; 1.900 a 0; 210 | minime |
| Farmaci in Italia, equivalenti e carenze (12/11) | "aifa farmaci mutuabili" 2.400, "lista di trasparenza aifa" 1.300, "farmaci carenti" 210-1.000, "farmaco equivalente" 480; tutte a 0 € | scende: teste minime, clic zero; la domanda per nome del farmaco non è misurata |
| Parcoursup per formazione; disciplinari DOC (12/11) | "parcoursup" 2.240.000 (navigazione), "rang dernier admis" 140; 0 | **NO** tutti e due |
| Tongue drum; ricette Fujifilm (7/11) | 390-720; 0 | domanda minima su Google (sono prodotti: conta il marketplace) |

## 5. Che cosa farei

1. **Prefissi telefonici USA: prova da 60 pagine (15 ore), poi il sito intero.** Prima la verifica indipendente prevista dalle regole. A Massimiliano servono un dominio e la chiave gratuita FTC.
2. **Diarie federali + rimborso chilometrico** (18 ore) quando parte il sito paghe militari.
3. **Limiti 401(k)/IRA/Roth/HSA** (20 ore) dentro il calcolatore dell'inflazione.
4. Le altre restano in riserva. Da decidere a parte se riaprire le date dei pagamenti USA (già NO due volte, 450.000 ricerche al mese).
