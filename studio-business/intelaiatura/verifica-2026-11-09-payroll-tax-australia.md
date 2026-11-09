# Verifica indipendente: payroll tax per Stato australiano + calcolatore multi-Stato + Payday Super (9/11/2026, sera)

Idea verificata: n. 1 di `fronti-2026-11-09-pomeriggio-software-piccole-imprese.md` (voto del ricercatore 6; 250 / 2.700 / 20.000 €/anno; pagatore Employment Hero AUD 200 a demo su PartnerStack). Mandato di Massimiliano: "studia se vale la pena e, quando trovi qualcosa, vai fino in fondo".

Tutto letto con curl dal nostro server il 9/11/2026. Nessun blocco aggirato. Dove una pagina risponde 403 o con risultati finti lo scrivo.

## 0. Verdetto in breve

| | Ricercatore | Verifica |
|---|---|---|
| Voto | 6 | **6,5** |
| €/anno a 18 mesi (prudente / centrale / ottimista) | 250 / 2.700 / 20.000 | **350 / 3.100 / 23.000** |
| Dati ufficiali leggibili | 6 Stati su 8 | **8 su 8** (portale ufficiale congiunto payrolltax.gov.au + 6 siti statali; ACT e NT solo dal portale) |
| Concorrente con calcolatore multi-Stato | "atteso, non letto" | **uno solo, fermo al 2025-26, senza ripartizione interstatale** (payrolltaxcalculator.com.au); i fornitori di paghe hanno tabelle vecchie di 2-4 anni |
| Pagatori con cifra letta | Employment Hero AUD 200 a demo | Employment Hero AUD 200 a demo + **MYOB AUD 80 a iscrizione** (+ Airwallex 200 $, Rippling 600 $ a demo da verificare per l'Australia) |

**NO-GO come sito nuovo adesso**: non passa l'asticella (voto ≥ 7 e ≥ 5.000 €/anno centrali). L'idea è più solida di quanto scritto dal ricercatore sui dati e sulla concorrenza, ma i soldi restano sotto: mercato piccolo (solo Australia), guadagno legato a una demo prenotata da un sito informativo, accettazione "a sola discrezione" di Employment Hero non verificata.

**GO condizionato (RISERVA alta → PASSA) se scatta UNA condizione**: Employment Hero accetta la domanda di Massimiliano su PartnerStack (gratis, 10 minuti). Con il pagatore confermato il voto sale a 7 e il sito si costruisce con il piano della sez. 8 (25-35 ore di agenti, 0 €), da pubblicare entro maggio 2027 per essere indicizzato alla stagione di luglio (riconciliazioni annuali e nuove aliquote del 1/7/2027). Senza quel sì, resta in riserva: nessuna riga in DA-PUBBLICARE.

## 1. DATI: le 8 giurisdizioni, 2026-27 (letti il 9/11/2026)

**Fonte unica per tutte e 8: payrolltax.gov.au** (portale ufficiale congiunto degli uffici delle entrate statali, "Last updated 28/10/2026", pagina 200): `https://www.payrolltax.gov.au/harmonisation/payroll-tax-rates-and-thresholds`. Contiene soglia annua/mensile, aliquote e deduzione massima di ogni giurisdizione, compresi ACT e NT, più le date delle dichiarazioni annuali (21 luglio; 28 luglio in ACT, NSW e SA).

| Giurisdizione | Soglia annua | Aliquota | Deduzione / riduzione | Pagina ufficiale (stato) |
|---|---|---|---|---|
| **NSW** | 1.200.000 $ (mensile 92.055 / 98.630 / 101.918 $ per 28/30/31 giorni) | 5,45 % | soglia piena; ripartita per quota di salari NSW sul totale australiano e per giorni/365; tabella storica dal 2022-23; "Last updated 01 July 2026" | `revenue.nsw.gov.au/taxes-duties-levies-royalties/payroll-tax/rates-and-thresholds` 200; grouping `/payroll-tax/grouping` 200; calcolatore `apps09.revenue.nsw.gov.au/erevenue/calculators/payrolltax.php` 200 (JavaScript) |
| **VIC** | 1.000.000 $ (mensile 83.333 $) | 4,85 %; **1,2125 % regionali** (≥ 85 % dei salari vittoriani a dipendenti regionali) | deduzione ridotta ("phase-out") tra 3 e 5 milioni $ di salari australiani al **50 % dal 1/7/2025**, zero sopra 5 milioni; sovrattasse 1 % sopra 10 milioni e 2 % sopra 100 milioni (quota vittoriana); "Updated 29 September 2026"; **file CSV ufficiale** `sro.vic.gov.au/sites/default/files/2026-07/ptx-rates-from-1-July-2025.csv` (183 byte, 200) | `sro.vic.gov.au/payroll-tax-current-rates` 200; `/businesses-and-organisations/payroll-tax/thresholds-and-grouping/threshold-and-phase-out-rate` 200 (formula con esempi); `/industries-and-locations/regional-employers` 200; grouping `/thresholds-and-grouping/grouping` 200; calcolatore della soglia = file Excel scaricabile |
| **QLD** | 1.300.000 $ (mensile 108.333 $) | 4,75 % fino a 6,5 milioni $; 4,95 % oltre; **−1 % regionali fino al 30/6/2030**; mental health levy +0,25 % sopra 10 milioni, +0,5 % in più sopra 100 milioni | deduzione ridotta di **1 $ ogni 7 $** sopra 1,3 milioni, zero a 10,4 milioni | `qro.qld.gov.au/payroll-tax/calculate/rates-thresholds/` 200; `/calculate/deductions/` 200; `/calculate/regional-discount/` 200; `/mental-health-levy/` 200; `/liability/grouping/` 200; **3 calcolatori online** `/calculate/calculators/` 200 |
| **WA** | 1.000.000 $ (mensile 83.333 $) | 5,5 % | soglia decrescente tra 1 e 7,5 milioni $: deducibile = 1.000.000 − (salari − 1.000.000) × **2/13**; esempio ufficiale 1,2 milioni → 969.231 $; "Last updated 2 June 2026" | `wa.gov.au/government/multi-step-guides/payroll-tax-employer-guide/calculation-payroll-tax-employer-guide` 200; grouping `.../grouping-payroll-tax-employer-guide` 200; calcolatore `apps.osr.wa.gov.au/portal/0/calculators/payrolltax` **500** alla lettura |
| **SA** | 1.500.000 $ massima (mensile 125.000 $) | 0 → 4,95 % variabile tra 1,5 e 1,7 milioni $; 4,95 % oltre 1,7 milioni | deduzione massima **600.000 $**, ripartita per quota SA sul totale australiano (esempio ufficiale 700.000 / 2.100.000 → 200.000 $) e per giorni; la tabella PDF dell'aliquota variabile non trovata al percorso provato (404) | `revenuesa.sa.gov.au/payrolltax/rates-and-thresholds` 200; `/payrolltax/how-is-payroll-tax-calculated` 200; grouping `/payrolltax/grouping-of-employers` 200; nexus `/payrolltax/nexus-provisions` 200; calcolatore `revenuesaonline.sa.gov.au/external/prt/calculator.xhtml` |
| **TAS** | 1.250.000 $ (mensile = giorni/365 × 1,25 milioni) | 0 fino a 1,25 milioni; **4 %** da 1.250.001 a 2.000.000; **6,1 %** da 2.000.001 (tabella 2026-27 esplicita) | soglie ripartite per gruppo e giorni; storico dal 2021 | `sro.tas.gov.au/payroll-tax/rates-thresholds` 200; grouping `/payroll-tax/grouping-de-grouping` 200; **calcolatore online** `tro.tas.gov.au/Home/CalculatorPayrollTax` 200 |
| **ACT** | **1.750.000 $** (mensile 145.833,33 $) | **6,75 %** da 1,75 a 20 milioni; 6,85 % a 50; 7,35 % a 100; 7,85 % a 150; 8,75 % oltre 150 milioni ("rates applying on or after 1 July 2026") | nessuna riduzione progressiva | `revenue.act.gov.au/...` **403** (Cloudflare "Just a moment", non aggirato); dati dal portale congiunto; Payroll Tax Act 2011 su `legislation.act.gov.au/a/2011-18/` 200 |
| **NT** | 2.500.000 $ (mensile 208.333 $) | 5,5 %; **6,5 % dal 1/7/2026 per salari ≥ 100 milioni $** | deduzione decrescente secondo il Payroll Tax Act 2009 (da confermare sul testo di legge: il portale non la riporta) | `treasury.nt.gov.au/...` e `nt.gov.au/...` **403** (Cloudflare); dati dal portale congiunto; Act su `legislation.nt.gov.au/en/Legislation/PAYROLL-TAX-ACT-2009` 200 (solo PDF, link non estratto) |

**Novità 2026-27 che creano domanda nuova:** l'ACT passa da aliquota unica e soglia 2 milioni a soglia **1,75 milioni $ con 5 scaglioni** (autocomplete "payroll tax threshold act 2026" 10 suggerimenti); il NT aggiunge il 6,5 % sopra 100 milioni; il QLD proroga lo sconto regionale al 2030. NSW, VIC, WA, SA, TAS invariati. Il portale congiunto segna ogni cambiamento con la data.

**Si può costruire un calcolatore multi-Stato corretto solo dai testi ufficiali?** Sì, per 6 giurisdizioni su 8 le formule sono scritte con esempi numerici (NSW: soglia × salari NSW/totale × giorni/365; VIC: phase-out con 2 esempi; QLD: 1 $ ogni 7 $; WA: 2/13; SA: 600.000 × quota; TAS: giorni/365). Restano tre punti da chiudere prima della pubblicazione, tutti verificabili con i calcolatori ufficiali online (QLD, TAS, SA) o con il testo di legge: (1) formula esatta dell'aliquota variabile SA tra 1,5 e 1,7 milioni; (2) se gli scaglioni TAS e ACT sono marginali o sull'intero imponibile (prova con 2 casi sul calcolatore TRO Tasmania); (3) la riduzione della deduzione NT dal PDF dell'Act. Le regole di grouping (quando due società contano come una) sono lunghe e cambiano per Stato: nel sito si spiegano in breve e si rimanda alle 6 pagine ufficiali lette, senza automatizzarle.

## 2. CONCORRENZA

**Calcolatori degli uffici statali (ognuno solo per il suo Stato):** QLD 3 calcolatori online (periodico, deduzione fissa per chi ha salari interstatali, annuale); TAS calcolatore online; SA calcolatore su RevenueSA Online; NSW pagina calcolatore (JavaScript); WA calcolatore (500 alla lettura); VIC solo un file Excel per la soglia; ACT e NT non leggibili. **Nessuno confronta gli Stati né ripartisce la soglia tra più Stati nello stesso strumento.**

**Calcolatori gratuiti multi-Stato trovati:**
- `payrolltaxcalculator.com.au` (200): "Australian State Payroll Tax Calculator 2025-26, all states & territories". Si sceglie **uno** Stato alla volta e si inseriscono i salari australiani totali; la pagina dice da sé "does not account for grouping, contractor rules, exemptions, or surcharges" e "thresholds may be pro-rated for ... interstate wage apportionment" (cioè non lo fa). Al 9/11/2026 è ancora al **2025-26** (quindi senza i nuovi scaglioni ACT). Ha AdSense (`ca-pub-…` nel sorgente): conferma che il pubblico vale pubblicità. È il concorrente diretto: battibile con il 2026-27, la ripartizione multi-Stato e le formule mostrate.
- `payrolltax.com.au` (200): solo un elenco di link a leggi e uffici. Nessun calcolo.
- `atotaxrates.info/businesses/payroll-tax/` (200): spiegazione lunga con link agli uffici, sito con pubblicità; nessun calcolatore.
- `payrolltaxcalculator.au`: pagina vuota (114 byte).

**Fornitori di paghe e contabili (i pagatori stessi):**
- Employment Hero, `employmenthero.com/blog/payroll-tax/` (200): tabella **vecchia** (ACT "2,5 milioni", NT "1,5 milioni", aliquota NT "2021-22"): oggi sbagliata.
- MYOB, `myob.com/au/resources/guides/payroll/payroll-tax` (200): "as at July 2022", VIC 700.000 $: vecchia.
- Xero, `xero.com/au/guides/payroll-tax/` (200, 9 luglio 2026): aggiornata ma con un solo esempio NSW, senza calcolatore e senza tabella completa.
- paycat.com.au (200): "2024/25". Deputy blog e William Buck: pagine senza contenuto utile. ADP Australia **403**. QuickBooks Australia: connessione chiusa (000). BDO, Pitcher, RSM, Canstar, H&R Block: 404 ai percorsi provati.
- business.gov.au (200): spiegazione 2025-26 con i link agli uffici. ATO **403**.

**Composizione dei risultati Google: non letta.** Bing risponde 200 ma restituisce risultati non pertinenti alle nostre richieste (artrite, Toyota, conversioni cm-piedi): degradazione anti-bot, non usabile e non aggirata. DuckDuckGo chiede un captcha, Brave 429, Mojeek 403, Startpage blocco JavaScript, Yahoo 500. Quindi il "buco" è provato sui siti letti direttamente, non sulla pagina dei risultati.

## 3. DOMANDA (autocomplete Google, gl=au, 70 domande il 9/11/2026)

Dieci suggerimenti su dieci per: "payroll tax calculator" (con wa, nsw, qld, vic, sa, australia, 2026, tasmania), "payroll tax threshold" (+ ogni Stato, 2026, 2027), "payroll tax threshold nsw/vic/qld/wa/sa/tas/act/nt" (con anni dal 2021 al 2027, "monthly", "historical", "regional"), "payroll tax rate nsw/vic/qld/wa", "payroll tax rates australia" ("by state", "2026"), "payroll tax grouping" e "grouping rules" (per Stato), "payroll tax multiple states" ("claiming payroll tax threshold in multiple states"), "payroll tax contractors", "payroll tax gp", "payroll tax exemption", "payroll tax due dates" ("2026", "2027", per Stato), "payroll tax annual reconciliation" ("due date 2026" per Stato), "payroll tax registration", "payroll tax regional", "how is payroll tax calculated" (per Stato), "mental health levy qld", "payday super" ("rules", "ato", "for contractors", "late payment", "due date", "penalties"), "payday super xero/myob" (10), "super guarantee 2026" (10).

Più deboli: "payroll tax calculator multi state" **2**, "payroll tax interstate wages" 6, "payroll tax apportion" 3, "payroll tax calculator tas/act/nt" 3-4, "payday super calculator" 4, "payday super software" 4, "payday super employment hero" 4, "payroll tax by state australia" 6, "which state has the lowest payroll tax" 10 ma quasi tutto imposta sul reddito USA.

**Stima delle ricerche mensili (metodo dichiarato, non un dato):** nessuno strumento di volumi è leggibile dal server. Uso la regola empirica già usata negli studi precedenti: una domanda con 10 suggerimenti e varianti per anno (2024, 2025, 2026, 2027) e per periodo ("monthly") vale di norma almeno 1.000 ricerche al mese nel Paese; le code per Stato minore (tas, act, nt) 100-300. Somma dell'insieme "payroll tax" australiano (soglie, aliquote, calcolatore, grouping, scadenze, registrazione per 8 Stati): **20.000-40.000 ricerche al mese**, di cui la metà va per forza agli uffici statali (ricerche "login", "contact", "registration"). "Payday super": 3.000-8.000 al mese nel 2026, in calo dopo il primo anno di applicazione.

**Stagionalità:** sì, ciclo dell'anno fiscale australiano (1 luglio - 30 giugno): nuove aliquote il 1° luglio, riconciliazione annuale il 21 luglio (28 luglio in ACT, NSW, SA), bilanci statali a maggio-giugno con gli annunci. L'autocomplete lo conferma ("payroll tax annual reconciliation due date 2026" 10 con varianti per Stato; "payroll tax threshold 2027" già 10 a novembre 2026). Google Trends risponde 429: non letto. Picco atteso giugno-agosto, con un secondo picco a gennaio-febbraio (nuove assunzioni, superamento della soglia mensile).

## 4. SOLDI

**Employment Hero su PartnerStack** (`market.partnerstack.com/page/employmenthero`, 200): "Earn **AUD$200 / £100 GBP** for every qualified lead who books a demo"; il programma accetta "Link based attribution" e "Lead forms". Termini ufficiali (`employmenthero.com/legals/affiliate-partner-terms-conditions/`, 200): commissione solo sul **primo** contatto (non su acquisti, rinnovi, upgrade); il contatto deve avere dati completi, "genuine interest", nessun metodo fraudolento, automatico o **incentivato**; "the Company shall make the final determination as to lead acceptability in its sole discretion"; pagamento entro 45 giorni dalla fine del mese; audit e recupero di commissioni su contatti non idonei; l'affiliato deve dichiarare il rapporto di affiliazione e elencare i propri domini. **Nessun requisito scritto di dimensione dell'azienda né di Paese dell'editore.** Prezzi Employment Hero (`/pricing/`, 200): da 11 $ a dipendente al mese con **minimo 25 $/mese**: vende anche a imprese con 3-5 dipendenti, quindi chi supera la soglia della payroll tax (circa 10-15 dipendenti a 1 milione $ di salari) è in pieno nel suo mercato.

**Altri pagatori australiani con cifra letta:**
- **MYOB Affiliate Program** (`myob.com/au/affiliates`, 200): "**$30 for Payroll Only and MYOB Solo. $80 for all other eligible products.** Commission amounts are in AUD and exclude GST"; cliente nuovo o senza abbonamento da 30 giorni; domanda soggetta ad approvazione. Pagamento a iscrizione, non a demo: utile come seconda offerta.
- **Airwallex** (PartnerStack, 200): "Earn $200 referral commissions for new Airwallex customer, conditions apply" (conti aziendali multivaluta: pubblico vicino ma non centrato).
- **Rippling** (PartnerStack, 200): 600 $ a demo qualificata (SQO) + 1.000 $ alla firma; sito `rippling.com/en-AU` 200 (vende in Australia); i termini del programma sono una pagina JavaScript non leggibile: idoneità del traffico australiano **da verificare**.
- **Deel** (PartnerStack, letta dal ricercatore: 1.500 $ a cliente pagante; `deel.com/en-au` 200): paga tardi (cliente pagante) e vende a chi assume all'estero: marginale.
- **Deputy** (PartnerStack, 200): 15-25 % del fatturato, programma per consulenti ("Deal registration"): non adatto a un sito.
- **Reckon** (`reckon.com/au/partners/`, 200): 20 % ricorrente solo dopo 5 clienti, programma per studi contabili.
- **Senza cifra o non leggibili:** Xero (404 sulle pagine affiliati, fallback su PartnerStack), QuickBooks Australia (000), KeyPay/Employment Hero Payroll e Tanda (fallback PartnerStack), BizCover assicurazioni (404 e fallback), Square Payroll 429.

**AdSense:** l'Australia è un mercato pubblicitario di prima fascia e il tema è finanza d'impresa; il concorrente diretto monetizza con AdSense. Stima **8-15 € ogni 1.000 visite** (stima, nessun numero letto; uso 10 €).

**Chi converte davvero.** La payroll tax la paga chi supera circa 1-1,75 milioni $ di salari (10-25 dipendenti e oltre). Chi arriva al nostro calcolatore è il titolare, il contabile interno o lo studio che lo segue, nel momento in cui scopre di dover registrarsi, ripartire la soglia tra Stati o cambiare strumento. È il cliente tipico di Employment Hero/MYOB; in più, dal 1/7/2026 il Payday Super chiude la Small Business Superannuation Clearing House dell'ATO (fonte: pagina Payday Super di Employment Hero, 200; l'ATO è 403) e obbliga chi la usava a passare a un software: la spinta all'acquisto c'è. Ma la demo si prenota sul sito del fornitore dopo il clic: da un sito informativo mi aspetto **0,03-0,2 % delle visite**, e Employment Hero decide a sua discrezione quali contatti pagare.

## 5. RISCHI

- **Tema fiscale (YMYL):** un numero sbagliato costa soldi veri a chi legge. Mitigazione: ogni cifra con link alla pagina ufficiale e data di controllo; formule mostrate con l'esempio ufficiale accanto; "stima, non è una consulenza"; rimando ai calcolatori degli uffici per il dato da dichiarare; nessuna automazione delle regole di grouping e dei contractor (si spiega e si rimanda).
- **Aggiornamenti:** 8 giurisdizioni, cambiamenti ogni 1° luglio e con i bilanci (maggio-giugno); nel 2026-27 sono cambiati ACT e NT. Mitigazione: `verifica.py` legge ogni mese il portale congiunto e le 6 pagine statali e confronta le cifre del JSON con il testo (sez. 8.5); ACT e NT si controllano sul portale congiunto (data "Last updated") perché i loro siti rispondono 403.
- **Calcolatore fuorviante:** i casi con gruppo di società, part-year, regionali e sovrattasse sono i più complessi. Mitigazione: il calcolatore chiede i dati del gruppo come un solo datore, mostra la soglia ripartita Stato per Stato e segnala con un avviso i casi che non calcola (sovrattasse VIC e levy QLD sopra 10 milioni: si mostrano come nota, non come cifra).
- **Pagatore unico forte:** Employment Hero può rifiutare la domanda, respingere i contatti o cambiare la cifra ("We reserve the right to alter or change the Commission amount"). Mitigazione: MYOB come seconda offerta; AdSense come base.
- **Mercato piccolo e stagionale:** l'Australia ha circa 2,6 milioni di imprese ma la payroll tax riguarda una minoranza; le ricerche si concentrano a luglio.
- **Pagine dei risultati non lette:** se Google mostra già i calcolatori statali e Xero in cima, il nostro spazio è la coda lunga ("threshold act 2026", "interstate wages", "multiple states").

## 6. Stima €/anno a 18 mesi (maggio 2028) con la formula

Formula: ricavo annuo = visite/anno × (RPM AdSense / 1.000) + visite/anno × tasso demo × tasso accettazione × 114 € (AUD 200) + visite/anno × tasso iscrizione MYOB × 45 € (AUD 80).

| | Prudente | Centrale | Ottimista |
|---|---|---|---|
| Visite al mese a 18 mesi | 800 | 3.000 | 9.000 |
| AdSense (10 € / 1.000) | 96 € | 360 € | 1.080 € |
| Demo Employment Hero (0,03 / 0,08 / 0,2 % delle visite; accettate 50 / 60 / 70 %) | 1,4 demo → 160 € | 17 demo → 1.970 € | 151 demo → 17.200 € |
| Iscrizioni MYOB (0,02 / 0,05 / 0,1 %) | 2 → 90 € | 18 → 810 € | 108 → 4.860 € |
| **Totale** | **≈ 350 €** | **≈ 3.100 €** | **≈ 23.000 €** |

Primi soldi: AdSense da 4-6 mesi dopo la pubblicazione (se approvato), prime demo nella stagione di luglio 2027. Ore: 25-35 di agenti; Massimiliano 30-40 minuti (domanda a Employment Hero e a MYOB, sito Netlify, Search Console).

## 7. Gemello Regno Unito (controllo rapido)

Dati leggibili dall'API GOV.UK (`/api/content/guidance/rates-and-thresholds-for-employers-2026-to-2027`, aggiornata 1/9/2026): soglia secondaria datore **5.000 £/anno** (96 £/settimana), aliquota datore **15 %**, Employment Allowance **10.500 £**. Autocomplete GB: "employer national insurance calculator 2026/27" 10, "employment allowance 2026/27" 10, "employer nic rates 2026/27" 10, "secondary threshold 2026/27" 9, "auto enrolment thresholds 2026/27" 2. Pagatore: Employment Hero £100 a demo (stesso programma). Ma è una regola nazionale unica, GOV.UK ha le tabelle e i propri strumenti, e i calcolatori dei datori sono il prodotto base di ogni software per paghe britannico: nessun buco paragonabile a quello degli 8 Stati australiani. **Non si lega al sito adesso**; al massimo una sezione `/uk/` di 3 pagine se il sito australiano prende traffico (stesso pagatore).

## 8. Piano di costruzione (si usa SOLO se Employment Hero accetta la domanda su PartnerStack)

### 8.1 Nome e indirizzo
Nome di lavoro: **Payroll Tax by State** (Australia). Indirizzo Netlify gratuito `payroll-tax-by-state.netlify.app` (il dominio non serve per AdSense). Domini .com **liberi** al 9/11/2026 (RDAP Verisign 404): `payrolltaxbystate.com`, `payrolltaxaustralia.com`, `aupayrolltax.com`, `payrolltaxthreshold.com`, `statepayrolltax.com`, `payrolltaxcompare.com`, `multistatepayrolltax.com`, `paydaysupercalculator.com`, `employerthresholds.com`, `payrolltaxchecker.com`, `ozpayrolltax.com`. **Occupati:** payrolltaxcalculator.com, payrolltaxrates.com, payrolltaxtables.com, payrolltaxhub.com, payrolltaxguide.com, payrolltaxmap.com, paydaysuper.com, payrolltaxau.com. Scelta consigliata se si compra (solo con il sì di Massimiliano): `payrolltaxbystate.com`.

### 8.2 Pagine (22)
1. Home: tabella 2026-27 delle 8 giurisdizioni (soglia annua e mensile, aliquote, deduzione, sconto regionale, scadenze) con data di controllo e link ufficiale per riga; il calcolatore multi-Stato in alto.
2. `/calculator/`: calcolatore multi-Stato (sez. 8.4).
3-10. `/nsw/`, `/vic/`, `/qld/`, `/wa/`, `/sa/`, `/tas/`, `/act/`, `/nt/`: soglia, aliquote, come si riduce la deduzione (formula + esempio ufficiale), soglia mensile, scadenze, storico dal 2021 (NSW, VIC, WA, TAS, SA letti), "cosa è cambiato nel 2026-27", link al calcolatore ufficiale e alla pagina grouping dello Stato.
11. `/interstate-wages/`: come si ripartisce la soglia tra Stati, con i 4 esempi ufficiali (NSW, VIC, SA, QLD).
12. `/grouping/`: in breve, Stato per Stato, con i 6 link ufficiali; nessun calcolo.
13. `/regional-rates/`: VIC 1,2125 % (regola dell'85 %), QLD −1 % fino al 30/6/2030.
14. `/thresholds-history/`: tabella per anno e Stato (2021-22 → 2026-27).
15. `/due-dates/`: dichiarazioni mensili e annuali (21/28 luglio) per Stato, dal portale congiunto e dalle pagine statali.
16. `/what-changed-2026-27/`: ACT (5 scaglioni, soglia 1,75 milioni), NT (6,5 % sopra 100 milioni), QLD (sconto regionale al 2030), VIC (phase-out al 50 %).
17. `/payday-super/`: dal 1/7/2026 contributi pensionistici entro 7 giorni lavorativi dalla paga, chiusura della clearing house ATO, sanzioni; breve, con link ad ATO e legislazione (dal nostro server l'ATO è 403: si scrive dalla legge e dai comunicati e si rilegge a mano).
18. `/over-the-threshold/`: "ho superato la soglia: registrazione entro 7 giorni, cosa succede ai mesi precedenti" (testi letti su Xero e sulle pagine statali, con link ufficiali).
19-22. `/about/`, `/how-we-check/` (metodo e date), `/privacy/`, 404.

### 8.3 File dati
- `dati/giurisdizioni.json`: per ogni giurisdizione: `soglia_annua`, `soglia_mensile`, `aliquote` (lista di scaglioni con limite e aliquota), `deduzione` (`tipo`: `piena` | `decrescente_lineare` con `rapporto` (QLD 1/7, WA 2/13) e `zero_a` | `phase_out` (VIC: da 3 a 5 milioni, 50 %) | `variabile` (SA)), `regionale` (aliquota o sconto e regola), `sovrattasse` (VIC, QLD: solo nota), `scadenze` (mensile, annuale), `fonte_url`, `fonte_data_aggiornamento`, `controllato_il`, `anno_fiscale`.
- `dati/storico.json`: soglie e aliquote per anno dal 2021-22.
- `dati/payday_super.json`: date, regole, fonti.
- `dati/affiliati.json`: `employment_hero` (link PartnerStack o modulo), `myob` (link affiliato), spenti finché Massimiliano non è accettato.
- `dati/esempi_ufficiali.json`: i casi numerici presi dalle pagine ufficiali, usati come prova del calcolatore.

### 8.4 Calcolatore multi-Stato (specifica)
Ingressi: anno fiscale (2026-27); per ogni giurisdizione i salari imponibili pagati (0 se nessuno); giorni di impiego nell'anno (default 365); "fate parte di un gruppo?" (se sì, si inseriscono i totali del gruppo e si avvisa che paga la soglia solo il datore designato); regionale VIC/QLD sì/no. Calcolo: W = totale salari australiani; per ogni Stato S con salari w: quota q = w / W, frazione dell'anno f = giorni / 365.
- NSW: soglia = 1.200.000 × q × f; imposta = max(0, w − soglia) × 5,45 %.
- VIC: deduzione D = 1.000.000 × q × f; se 3 ≤ W ≤ 5 milioni: D = max(0, D − (w − 3.000.000 × q × f) × 50 %); se W > 5 milioni: D = 0; imposta = max(0, w − D) × 4,85 % (1,2125 % se regionale); se W > 10 milioni: nota sulle sovrattasse.
- QLD: D = max(0, 1.300.000 − (W − 1.300.000) / 7) × q × f; aliquota 4,75 % se W ≤ 6,5 milioni, altrimenti 4,95 %; −1 % se regionale; se W > 10 milioni: nota sulla levy.
- WA: D = 1.000.000 − (W − 1.000.000) × 2/13 se 1 < W < 7,5 milioni (0 se W ≥ 7,5 milioni), poi × q × f; imposta = max(0, w − D) × 5,5 %.
- SA: 0 se W ≤ 1,5 milioni; D = 600.000 × q × f; aliquota 4,95 % se W > 1,7 milioni, altrimenti variabile tra 1,5 e 1,7 milioni **con la formula da leggere sulla tabella RevenueSA prima della pubblicazione** (prova sul calcolatore ufficiale).
- TAS: soglie 1,25 e 2 milioni × q × f; 4 % e 6,1 % **marginali o sull'intero: da provare con due casi sul calcolatore TRO** prima di pubblicare.
- ACT: soglia 1.750.000 × q × f; aliquota per W (6,75 % fino a 20 milioni, poi 6,85 / 7,35 / 7,85 / 8,75 %), **da confermare sull'Act 2011 se per scaglioni o sull'intero**.
- NT: soglia 2.500.000 × q × f con riduzione **da leggere sul Payroll Tax Act 2009**; 5,5 % (6,5 % se W ≥ 100 milioni).
Uscita: per Stato soglia spettante, imponibile, aliquota, imposta annua e stima mensile; totale; formula scritta sotto ogni riga con il link all'esempio ufficiale; avvisi (gruppo, part-year, sovrattasse); pulsante "copia come testo"; riga "stima: il dato da dichiarare lo calcola l'ufficio del tuo Stato" con il link al suo calcolatore. Tutto in JavaScript senza server; nessun dato inviato.

### 8.5 Controlli di `verifica.py`
1. Le 7 fonti leggibili rispondono 200 (portale congiunto, NSW, VIC rates + CSV, QLD rates + deductions, WA calculation, SA rates + how-calculated, TAS rates); ACT e NT: si controlla che la riga del portale congiunto contenga ancora "1 750 000", "6.75%", "2 500 000", "5.5%" e che "Last updated on" non sia cambiato senza un nostro aggiornamento.
2. Ogni cifra del JSON è presente nel testo della sua pagina: NSW "$1,200,000" e "5.45%"; VIC CSV "$1,000,000", "4.85%", "1.2125%"; QLD "$1.3 million", "4.75%", "4.95%", "$1 for every $7"; WA "$7,500,000", "2/13", "$969,231"; SA "$1,500,000", "$600,000", "4.95%", "$1.7 million"; TAS "1 250 000", "2 000 000", "6.1".
3. Casi di prova dagli esempi ufficiali: NSW 900.000 su 3.000.000 → soglia 360.000 $; NSW 184 giorni → 604.931,51 $; VIC esempio con interstatali (1,5 milioni su 3,5, 335 giorni) ricalcolato con 1.000.000 e 50 %; WA 1.200.000 → 969.231 $; SA 700.000 su 2.100.000 → 200.000 $; TAS e QLD confrontati con i calcolatori online (valori salvati in `esempi_ufficiali.json`).
4. Coerenza: nessuna imposta negativa; somma delle soglie ripartite ≤ soglia piena di ogni Stato; aliquote tra 0 e 10 %.
5. Date: se oggi è dopo il 1° luglio e `anno_fiscale` è ancora quello vecchio, errore; se "Last updated" di una pagina ufficiale è più recente di `controllato_il`, avviso.
6. Link affiliati 200 e verso gli host giusti; pagine con "Last checked" e link alla fonte; sitemap e canonical; nessun nome di modello AI nei file; nessun dato personale.

### 8.6 Dove vanno i link dei pagatori
- **Employment Hero (AUD 200 a demo):** sotto il risultato del calcolatore quando l'imposta è > 0 ("Over the threshold? Payroll software that files STP and pays super each payday", con la dichiarazione di affiliazione, nessun premio o incentivo); in `/payday-super/` (chiusura della clearing house → serve un software o una clearing house commerciale); in `/over-the-threshold/`; riquadro laterale nelle 8 pagine statali. Il modulo contatti di PartnerStack solo se Employment Hero lo attiva: altrimenti link.
- **MYOB (AUD 80 a iscrizione):** seconda opzione negli stessi riquadri ("or an accounting + payroll package"), e nelle pagine `/due-dates/` e `/thresholds-history/` (pubblico contabile).
- **Rippling (600 $ a demo) e Deel:** solo dopo la verifica dell'idoneità australiana; se sì, nelle pagine `/grouping/` e sui casi sopra 10 milioni (imprese grandi).
- AdSense su tutte le pagine con testo sufficiente, mai sopra il calcolatore.

### 8.7 Passaggi di Massimiliano (solo se si costruisce)
1. Domanda a Employment Hero su PartnerStack (`market.partnerstack.com/page/employmenthero`, "Apply to program"): 10 minuti, gratis; indicare il dominio del sito.
2. Domanda al MYOB Affiliate Program (`myob.com/au/affiliates`, "Join now"): 10 minuti, gratis.
3. Sito su Netlify collegato al repository e Search Console: 15 minuti.

## 9. Cosa cambia nei file
- `ESPLORATE.md`: riga con il verdetto (NO-GO come sito nuovo; GO condizionato al sì di Employment Hero; voto 6,5; 350 / 3.100 / 23.000 €).
- `DA-PUBBLICARE.md`: **nessuna riga** (non passa l'asticella). Si aggiunge in cima alla coda il giorno in cui arriva l'accettazione di Employment Hero.
