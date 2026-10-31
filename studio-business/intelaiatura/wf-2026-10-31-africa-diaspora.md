# Africa e diaspora africana: visti, passaporti, esami, rimesse (31/10/2026)

Angolo assegnato: Nigeria, Ghana, Kenya, Sudafrica, Marocco, Egitto e le loro diaspore. Visti e rifiuti per nazionalità verso Regno Unito, USA, Schengen e Canada; passaporti e tempi; esami (WAEC/JAMB); rimesse.

Letti prima: skill `rete-siti`, `REGOLE-FISSE.md` (regole del 31/10: fronti nuovi, conta il fatturato, niente lavori a ore di Massimiliano), `ESPLORATE.md` sui temi vicini, il rapporto `ricerca-zona-latam-africa-2026-10-30.md` e i numeri di GoatCounter di ottobre.

**Già chiusi e NON rifatti da capo** (si citano solo se c'è un fatto nuovo): rifiuti dei visti Schengen/UK/Canada/Australia per nazionalità (FATTO: le pagine `visa-refusal-rates/nigeria`, `/ghana`, `/kenya`, `/south-africa`, `/morocco`, `/egypt` esistono già), sezione in francese e arabo per Marocco e Algeria (passa, in coda), pagine per singolo consolato (NO 21/10), rifiuti dei visti USA (NO 28/10, `travel.state.gov` 403), visto bond USA (NO 28/10), lotteria DV (NO 20/10), rimesse per corridoio e tassa dell'1 % (NO 18/10 e 28/10), tempi dei passaporti (NO 23/10), rinnovo del passaporto nigeriano/ghanese/sudafricano dall'estero (riserva 5,5, 30/10), WAEC/JAMB/SASSA/passaporti in patria (NO 30/10), ETA del Kenya e del Sudafrica, visto all'arrivo in Egitto (NO), prezzi dei monumenti in Egitto (NO 29/10), traghetti (NO 30/10), IMEI (riserva 21/10), "quanti [nazionalità] si trasferiscono" (PASSA 28/10, già costruita: `moved-to/nigerians`, `moved-to/south-africans`).

**Metodo e prove (tutte del 31/10/2026):** `curl` sulle fonti (stato HTTP, dimensione, `Last-Modified`), PDF letti con `pdftotext`; suggerimenti di Google (`suggestqueries.google.com`, `client=firefox`) con lingua e Paese giusti (en/us, en/gb, en/ng, en/gh, en/ke, en/ca, en/au, en/eg, fr/fr, fr/be, nl/nl); ricerca web per vedere chi c'è nei risultati (risultati da un computer negli USA). **Nessun blocco aggirato**: `gmc-uk.org`, `mcc.ca`, `ecfmg.org` (Cloudflare), `travel.state.gov`, `state.gov`, `dhs.gov` (403), il testo integrale su `federalregister.gov` (pagina "Request Access") non sono stati forzati né letti con altri strumenti; per il proclama si è usato il PDF ufficiale della tipografia federale (`govinfo.gov`, 200). Le stime sono stime, non dati: ognuna ha il calcolo.

Voto con la griglia delle ricerche precedenti: domanda 0-3 · buco nei risultati 0-2 · fonte ufficiale leggibile e riusabile 0-2 · valore del pubblico e chi paga 0-2 · rischi e ore 0-1.

Formula delle stime: visite al mese a 18 mesi × 12 × € ogni 1.000 visite ÷ 1.000. Riferimento del cruscotto (30/10): 6-10 € ogni 1.000 visite in inglese da USA e Regno Unito; per lettori in Nigeria, Kenya, Ghana, India 1-3 €. AdSense non ha ancora incassi: sono stime.

**Numeri veri da cui parto (GoatCounter, 1-31/10/2026, sito Visa Income Checker):** `visa-refusal-rates/pakistan` 18 visite, `/iraq` 7, `/nigeria` 5, `/tunisia` 5, `/bangladesh` 5, `/morocco` 3, `/south-africa/easiest-schengen-visa` 2, `/algeria` 2. Le pagine africane portano visite, ma poche: il pubblico africano c'è, il problema è quanto vale.

---

## 0. Risposta in breve

**Nessuna idea passa l'asticella dei siti nuovi** (voto ≥ 7 e ≥ 5.000 €/anno nel caso centrale). Tre idee sono **sezioni a costo zero con guadagno positivo** da mettere in coda in Visa Income Checker (regola del 30/10, "rete fitta"); le altre sono riserve o NO.

| # | Idea | Dove | Voto | Prudente / centrale / ottimista €/anno a 18 mesi | Ore | Chi paga |
|---|---|---|---|---|---|---|
| 1 | **Dove vive la diaspora: nati in [Paese] per città e contea nel Regno Unito, negli USA, in Canada e in Australia** (censimento britannico 2021, ACS 2025 uscita il 29/10/2026, censimenti CA/AU) | sezione Visa Income, accanto a "moved-to" | **6,5** | 80 / 500 / 2.000 | 18-26 | AdSense USA/UK/CA/AU, Wise (CPA da 10 £) |
| 2 | **Divieto d'ingresso negli USA per nazionalità** (Proclama 10998: 19 Paesi totali + 20 parziali, 18 africani; categorie sospese, eccezioni, tassi di overstay ufficiali per Paese) | riquadro nelle pagine nazionalità di Visa Income + pagina centrale | **6** | 40 / 250 / 1.200 | 6-10 | AdSense USA (immigrazione) |
| 3 | Test della tubercolosi per il visto britannico: cliniche approvate e **prezzo** per Paese (gov.uk, 73 pagine Paese, Nigeria 94 $/49 $) | riquadro nelle pagine nazionalità + una pagina | 5,5 | 10 / 60 / 290 | 5-8 | AdSense (pubblico India/Pakistan/Nigeria/Ghana) |
| 4 | Esami per medici stranieri: PLAB 1 (date e sedi estere: Lagos, Abuja, Cairo; chiusura di Accra e Alessandria nel 2027), AMC, USMLE, MCCQE | – | 4,5 RISERVA | 0 / 150 / 600 | – | corsi di preparazione (nessun programma letto) |
| 5 | Cittadinanza per afrodiscendenti: Benin (piattaforma ufficiale), Ghana, Sierra Leone | pagina in Visa Income | 5 | 30 / 150 / 600 | 6-10 | AdSense USA; test del DNA (commissione non letta) |
| 6 | Rimesse per Paese di provenienza (Kenya: file mensile della banca centrale, settembre 2026) | – | 4 NO | 10 / 40 / 150 | – | – |
| 7 | Marocchini d'Europa in estate: Opération Marhaba, dogana per auto e pensionati (MRE) | – | 4 NO | – | – | – |
| 8 | Visto per la Nigeria per nazionalità (anche figli della diaspora con passaporto USA/UK) | – | 4 NO | – | – | – |
| 9 | Dazio sulle auto importate in Kenya (lista CRSP del KRA) | – | 4 NO | – | – | – |
| – | WAEC/JAMB, passaporti in patria, rifiuti dei visti USA, costo delle rimesse | – | NO confermati (nessun fatto nuovo) | – | – | – |

**Totale delle tre sezioni utili (1+2+3):** 130 / 810 / 3.490 €/anno, 29-44 ore. Primi soldi: 2°-3° mese dopo la pubblicazione (AdSense); l'idea 2 può portare visite subito, perché il tema è in cronaca (il proclama prevede revisioni ogni 180 giorni).

**Lezione del giro.**
1. **Il pubblico africano in Africa non paga la rete** (confermato, lo diceva già il 30/10): WAEC, JAMB, passaporti, dazi sulle auto, visti per la Nigeria hanno un portale ufficiale che risponde o una tabella che non esiste, e lettori che valgono 1-3 € ogni 1.000 visite.
2. **La diaspora vale quando vive in USA, Regno Unito, Canada, Australia.** Le domande che fa ("nigerian population in houston", "is nigeria on the travel ban list 2026", "south african population in australia") sono in inglese, da Paesi ricchi, con numeri ufficiali precisi che oggi nei risultati sono sbagliati o discordanti: è la forma che gli assistenti AI citano. Ma sono domande "da curiosità" o da notizia, con poco da vendere: per questo restano sotto i 5.000 €.
3. **Le domande americane più ricche stanno tutte su `state.gov` (403):** rifiuti dei visti USA per nazionalità, elenco dei Paesi con il visto bond, pausa dei visti di immigrazione per 75 Paesi ("immigrant visa pause 75 countries" 10 suggerimenti, con "list", "update", "lawsuit"), riduzione della validità dei visti per reciprocità. **Vincolo da allentare** (già indicato il 17 e il 18/10, qui con una prova in più): una prova di lettura di `travel.state.gov` da GitHub Actions o da un indirizzo di rete fisso fuori dal nostro server (spesa piccola, decide Massimiliano). Con quella fonte l'idea 2 diventerebbe "Restrizioni USA per nazionalità" completa (divieto + bond + pausa + reciprocità + rifiuti) e salirebbe a 7.

**Fatto nuovo utile subito:** il Census Bureau ha pubblicato i dati ACS 2025 a 1 anno il **29/10/2026** (file `acsdt1y2025-b05006.dat`, `Last-Modified: Thu, 29 Oct 2026 11:45:47 GMT`): nati in Nigeria negli USA **479.759**, in Texas **118.381**, nell'area di Houston **51.617**; nati in Ghana **262.340**, in Egitto **207.248**, in Kenya **188.712**, in Sudafrica **150.108**, in Marocco **98.678**. Nei risultati di Google per "nigerian population in houston" oggi girano 22.304, 34.937, "50.000-85.000", "60.000" e "150.000": nessuno ha il numero 2025.

---

## 1. Dove vive la diaspora: nati in [Paese] per città e contea — voto 6,5, SEZIONE di Visa Income Checker

**L'idea in una riga.** Accanto a "Quanti nigeriani si sono trasferiti in Europa" (`moved-to/nigerians`, che oggi dice "non è il numero di nigeriani che vivono in un Paese UE, che è molto più grande") si aggiunge la risposta che manca: **quanti nati in [Paese] vivono nel Regno Unito, negli USA, in Canada e in Australia, e in quali città e contee**, con l'anno, il margine d'errore (ACS) e la fonte. Una pagina per nazionalità × Paese di arrivo (circa 40 nazionalità con numeri sufficienti × 4 = ~160 pagine), con la tabella delle 20 città/contee principali; nessuna pagina per singola città all'inizio (niente pagine sottili).

**Fonti ufficiali (verificate con curl).**
- **USA, ACS tabella B05006 "Place of birth for the foreign-born population"**: file in blocco senza chiave `www2.census.gov/programs-surveys/acs/summary_file/2025/table-based-SF/data/1YRData/acsdt1y2025-b05006.dat` **200**, 649.400 byte, `Last-Modified: 29 Oct 2026`, 378 righe (Stati USA, aree metropolitane, contee grandi); a 5 anni `.../2024/.../5YRData/acsdt5y2024-b05006.dat` **200**, 279.881.591 byte, `Last-Modified: 29 Jan 2026` (tutte le contee e le città). Etichette delle colonne da `api.census.gov/data/2025/acs/acs1/variables.json` **200** (senza chiave). L'API con i dati vuole una chiave gratuita (302 verso `missing_key.html`): non serve, bastano i file in blocco. **Pubblico dominio** (opera del governo federale). Aggiornamento: ogni settembre/ottobre (1 anno) e ogni dicembre/gennaio (5 anni).
- **Inghilterra e Galles, censimento 2021, TS012 "Country of birth (detailed)"**: API Nomis `nomisweb.co.uk/api/v01/dataset/NM_2032_1` **200** (a volte la connessione cade: serve ritentare), 84 voci tra cui Ghana, Nigeria, Kenya, Somalia, Sudafrica, Zimbabwe, Nord Africa, India, Pakistan, Bangladesh, Filippine, Polonia, Romania; per ogni autorità locale. Prova: nati in Nigeria, primi 5 comuni: **Greenwich 14.357**, Southwark 11.173, Manchester 10.329, Barking and Dagenham 9.434, Lewisham 9.278 (somma dei 331 comuni 267.509; il totale ONS di Inghilterra e Galles è 270.768: la differenza va spiegata nella pagina o si usa il livello nazionale). Licenza **OGL v3**. Dato fermo al 2021 (prossimo censimento 2031): va detto chiaramente.
- **Canada**: Statistics Canada, servizio dati `www150.statcan.gc.ca/t1/wds/rest` **200** (censimento 2021, luogo di nascita per area metropolitana; licenza aperta di StatCan). **Australia**: ABS Data API `data.api.abs.gov.au` **200** (censimento 2021, Paese di nascita per area; CC BY 4.0). Da leggere tabella per tabella in costruzione.

**Domanda (autocomplete).**
- en/us "nigerian population in" **10**: "us", "houston", "uk", "texas", "houston texas", "new york", "atlanta", "canada", "maryland", "nyc".
- en/us "where do most nigerians live in" **10**: "the us", "italy", "the uk", "canada", "london", "south africa", "houston", "germany", "spain", "nyc".
- en/gb "nigerian population in uk" **10** (2026, 2025, 2024, "biggest nigerian population in uk", "nigerian population in england"); en/gb "ghanaian population in uk" **7**; en/gb "pakistani population in uk by" **6** ("by city", "which city in uk has highest pakistani population").
- en/ca "nigerian population in canada" **8**; en/au "south african population in australia" **10** ("perth", "western australia", "largest"); en/gb "south african population in uk" **9**; en/us "somali population in" **10** (Maine, St Cloud MN, Columbus Ohio, Seattle, Michigan); en/us "kenyan population in" **10**; en/us "ghanaian population in" **10** (anche "worcester ma", "toronto").
- La stessa forma vale per ogni nazionalità: la sezione non è solo africana.

**Chi c'è oggi su Google** ("nigerian population in houston"): Guardian Nigeria (articoli "What City in Texas Has the Most Nigerians?" con stime della comunità), click2houston e fox26houston (notizie), **neilsberg.com** (pagine automatiche sull'ACS per città, ma con "ancestry" e non luogo di nascita, dati 2023-2024), mirror di Wikipedia con "150.000". Per il Regno Unito: Wikipedia "British Nigerians" (tabella copiata dal censimento) e **pagine FOI dell'ONS** (persone che chiedono per iscritto "population of Nigerians living in UK by cities": la domanda esiste, la risposta è sparsa). **Battibile** sulle città britanniche e canadesi e sul dato USA 2025 appena uscito; **non** sulle teste ("nigerian population in uk": Wikipedia prima).

**Chi paga e quanto.**
- AdSense: lettori in USA, Regno Unito, Canada, Australia, ma su temi demografici la pubblicità vale meno che su visti e soldi: stimo **4-8 €** ogni 1.000 visite (cruscotto 6-10 € in inglese, abbassato perché il tema non ha annunci ricchi).
- Wise: "CPA rates start at £10" (pagina ufficiale `wise.com/gb/affiliate-program`, letta il 17/10, iscrizione da Massimiliano su Partnerize): lettori della diaspora che mandano soldi a casa. Conversione stimata 1 ogni 5.000-10.000 visite (stima, nessun dato nostro).

**Stima a 18 mesi.**
- Prudente: 1.500 visite/mese × 12 × 4 € = **72 €** + Wise ~10 € → **80 €**.
- Centrale: 5.000 visite/mese × 12 × 6 € = **360 €** + Wise 12 iscrizioni × 11,5 € ≈ 140 € → **500 €**.
- Ottimista: 15.000 visite/mese × 12 × 8 € = **1.440 €** + Wise ~550 € → **2.000 €**.
- Primi soldi: 2°-3° mese (AdSense). Le citazioni degli assistenti AI (che mandano un terzo delle visite) sono il motivo per crederci: numeri ufficiali precisi con anno, contro stime discordanti.

**Ore:** 18-26 (lettura del file ACS 5 anni da 280 MB una volta l'anno, API Nomis, StatCan, ABS; generatore con lo stesso stile di `moved-to`; testo "cosa misura e cosa no": nati all'estero ≠ nazionalità ≠ origine).

**Voto 6,5** = domanda 2,5 (forte e ripetuta su decine di nazionalità, ma informativa) + buco 1,5 (città UK/CA e ACS 2025 scoperti; teste occupate da Wikipedia, USA da neilsberg) + fonte 2 (pubblico dominio, OGL, CC BY; file in blocco senza chiave) + valore 0,5 (pubblicità media, poco da vendere) + rischi/ore 0 (Nomis instabile, 4 fonti diverse da tenere).

**Rischio:** confondere "nati in", "cittadini di" e "origine etnica": la pagina deve dirlo in alto, come fa già `moved-to`.

---

## 2. Divieto d'ingresso negli USA per nazionalità — voto 6, RIQUADRO nelle pagine nazionalità di Visa Income

**L'idea in una riga.** Nelle pagine nazionalità che già esistono (`visa-refusal-rates/nigeria` e le altre ~70) si aggiunge un riquadro "USA": il Paese è nel divieto d'ingresso? Totale o parziale? Quali visti sono sospesi (per la Nigeria: immigrazione e B-1, B-2, B-1/B-2, F, M, J), da quando, eccezioni, e il **tasso di overstay ufficiale** che il proclama cita per quel Paese. Più una pagina centrale "US travel ban 2026: the 39 countries and exactly which visas" con la tabella.

**Fonte ufficiale (verificata).**
- API del Federal Register `federalregister.gov/api/v1/documents.json` **200** (JSON): ultimo proclama sugli ingressi = **Proclamation 10998** del 16/12/2025 (pubblicato il 19/12/2025, 90 FR 59717), in vigore dall'1/1/2026; prima la 10949 del 10/6/2025. Unico proclama 2026 sugli ingressi trovato: "Restriction on Entry of Certain Nonimmigrant Workers" (23/9/2026), da controllare in costruzione. La pagina del testo integrale su `federalregister.gov` risponde "Request Access" (non forzata).
- Testo letto dal **PDF ufficiale** `govinfo.gov/content/pkg/FR-2025-12-19/pdf/2025-23570.pdf` **200**, 217 KB: divieto **totale** per 12 Paesi confermati (Afghanistan, Birmania, Ciad, Rep. del Congo, Guinea Equatoriale, Eritrea, Haiti, Iran, Libia, Somalia, Sudan, Yemen) + **7 nuovi** (Burkina Faso, Laos, Mali, Niger, Sierra Leone, Sud Sudan, Siria) + documenti dell'Autorità Palestinese; **parziale** per 4 confermati (Burundi, Cuba, Togo, Venezuela) + Turkmenistan modificato + **15 nuovi** (Angola, Antigua e Barbuda, Benin, Costa d'Avorio, Dominica, Gabon, Gambia, Malawi, Mauritania, **Nigeria**, Senegal, Tanzania, Tonga, Zambia, Zimbabwe). Per la Nigeria: "B-1/B-2 visa overstay rate of 5.56 percent and an F, M, and J visa overstay rate of 11.90 percent"; Senegal 4,30 % e 13,07 %. **Pubblico dominio.**
- Non leggibili (403): `travel.state.gov` (visti bond, pausa dei visti di immigrazione per 75 Paesi, reciprocità), `state.gov` e le ambasciate `*.usembassy.gov`, `dhs.gov` (rapporto overstay completo). Nel riquadro si mette solo ciò che dice il proclama, con link al resto.
- Aggiornamento: controllo settimanale dell'API (nuovi proclami del tipo PRESDOCU); il proclama prevede revisioni ogni 180 giorni. Pubblicazione solo se cambia.

**Domanda (autocomplete).**
- en/us "travel ban countries" **10**: "2026", "2026 list", "75", "2026 uscis", "2026 usa", "uscis", "39", "nafsa".
- en/us "us travel ban list" **10** ("of countries 2026", "75 countries", "caribbean", "update", "expanded", "39 countries").
- en/us "is nigeria on the travel ban" **10** ("list 2026", "still on", "included"); en/ng "us visa ban nigeria" **10** ("2026", "update", "has us visa ban on nigeria been lifted", "us lifts visa ban on nigerian doctors"); en/gh "us visa ban ghana" **8**.
- en/us "travel ban f1 visa" **7**; "travel ban green card" **10**; en/us "visa overstay rate by country" **7**; en/us "visa bond countries" **10**; en/us "immigrant visa pause 75 countries" **10**.

**Chi c'è oggi su Google** (ricerca "US travel ban countries list 2026 update Nigeria proclamation"): giornali nigeriani (Nairametrics, ThisDay, Leadership, Gazette), AllAfrica, studi legali (Pryor Cashman, Jackson & Hertogs, visalawyerblog), uffici universitari (Columbia ISSO), wheretoemigrate.io. I conteggi si contraddicono (36, 39, "75"): è il buco che gli assistenti premiano. **Non battibile** su "travel ban countries 2026" (notizie, NAFSA, Wikipedia); **battibile** sulle code "is [Paese] on the travel ban list", "[Paese] overstay rate", e nelle risposte degli assistenti.

**Chi paga.** AdSense con lettori USA su temi d'immigrazione (annunci di avvocati, valore alto): 6-10 €; il pubblico nigeriano/ghanese in patria vale 1-3 €. Media stimata 6-8 €.

**Stima a 18 mesi.** Prudente 600 visite/mese × 12 × 6 € = **43 €** (→ 40); centrale 2.500 × 12 × 8 € = **240 €** (→ 250); ottimista 10.000 × 12 × 10 € = **1.200 €** (con un nuovo proclama in cronaca). Primi soldi: subito dopo la pubblicazione se il tema torna in cronaca.

**Ore:** 6-10 (lettura del PDF con `pdftotext`, tabella Paese → categoria → visti → overstay, controllo settimanale dell'API, riquadro nelle pagine esistenti; revisione dei fatti obbligatoria: tema legale).

**Voto 6** = domanda 3 + buco 1 + fonte 1,5 (proclama leggibile e pubblico dominio, ma le altre restrizioni sono su `state.gov` 403) + valore 1 + rischi/ore 0,5 (bassi: poche ore, ma tema che cambia per decreto e frasi da scrivere con cura). **Sale a 7** con la lettura di `travel.state.gov` (vedi sez. 0, lezione 3).

---

## 3. Test della tubercolosi per il visto britannico: cliniche e prezzo per Paese — voto 5,5, RIQUADRO

**L'idea in una riga.** Nelle pagine nazionalità (sezione Regno Unito) e in una pagina "TB test for UK visa: cost and clinics by country": serve il test? (soggiorni di 6 mesi o più per chi ha vissuto in uno dei Paesi elencati), quali cliniche approvate, in che città, **quanto costa** (adulti, bambini sotto 11 anni, ristampa del certificato), Paesi senza clinica (Benin, Burkina Faso: test in un altro Paese).

**Fonte ufficiale (verificata).** GOV.UK Content API `gov.uk/api/content/tb-test-visa` **200** (JSON, OGL), con 73 collegamenti alle pagine Paese; esempio `.../tuberculosis-test-for-a-uk-visa-clinics-in-nigeria/tuberculosis-testing-in-nigeria` **200**, aggiornata il **13/5/2026**: cliniche OIM di Abuja, Benin City e Lagos, "Test fees: 11 years and above **94 USD**, below 11 years **49 USD**, reprint of certificate 16 USD", pagamento in naira al cambio ONU. Le pagine contengono anche telefoni ed email delle cliniche (dati di uffici, non di persone): nella nostra pagina si mettono solo città, nome della clinica, prezzo e link a gov.uk.

**Domanda.** en/ng "tb test for uk visa" **10** ("in nigeria", "price", "in lagos nigeria", "in abuja", "in benin city nigeria", "in ghana", "in pakistan"); en/gh **10** ("location in accra", "kumasi", "price"); en/ke "tb test uk visa" **10** ("price", "zimbabwe", "malaysia", "sri lanka").

**Google.** gov.uk risponde già Paese per Paese (prima posizione probabile), poi IOM e blog locali. Il nostro valore è solo il confronto tra Paesi e il prezzo in valuta locale: piccolo.

**Chi paga.** AdSense con lettori in India, Pakistan, Nigeria, Ghana, Kenya: 1-3 €. Nessuna affiliazione adatta.

**Stima.** Prudente 800 × 12 × 1 € = **10 €**; centrale 2.500 × 12 × 2 € = **60 €**; ottimista 8.000 × 12 × 3 € = **290 €**. **Ore:** 5-8 (stesso motore GOV.UK delle sezioni passaporto di Before You Fly).

**Voto 5,5** = domanda 2,5 + buco 0,5 + fonte 2 + valore 0 + rischi/ore 0,5. Guadagno positivo e piccolo: in coda bassa, solo come riquadro dentro le pagine esistenti.

---

## 4. Esami per medici stranieri (PLAB 1, AMC, USMLE, MCCQE): date, sedi estere, promossi — voto 4,5, RISERVA

**Domanda forte e del Paese giusto:** en/us "plab exam dates" **10** ("2026", "2027", "in nigeria", "in sri lanka", "india"); en/ng "plab 1 dates" **10** ("2027", "in egypt"); en/gb "plab 1 pass rate" **10**; en/eg "plab" **10**; en/ng "amc exam" **10** ("centers in africa", "centers in nigeria", "dates 2027"). Il pubblico (medici) vale più della media.

**Fonti chiuse:** `gmc-uk.org` **403** su tutte le pagine (Cloudflare "Attention Required"), `mcc.ca` 403, `ecfmg.org` 403. `amc.org.au` **200**, ma le date dell'esame MCQ sono "eventi" prenotati su Pearson VUE con autorizzazione di 12 mesi: nessuna tabella per città. Dalla ricerca web: il GMC chiuderà le sedi PLAB 1 di **Dhaka, Alessandria, Accra e Chennai** nel 2027 ("down 40% from 2023 to 2025"): domanda in calo. I blog (medibuddy, academically, canadaqbank, iatrox) danno date 2026 diverse tra loro.

**Chi paga:** corsi di preparazione (Plabable, PassMedicine): nessun programma letto. **Si riapre** solo se `gmc-uk.org` si legge da GitHub Actions senza aggirare niente; stima in quel caso 0 / 150 / 600 €.

---

## 5. Cittadinanza per afrodiscendenti (Benin, Ghana, Sierra Leone) — voto 5

**Fonte:** `myafroorigins.bj` **200** (portale ufficiale del Governo del Benin, in inglese, spagnolo, francese e portoghese): riconoscimento della nazionalità beninese per chi ha un antenato deportato con la tratta, "3 months from date of notification of receipt of your complete file", cerimonie di consegna dei certificati. Ghana e Sierra Leone: pagine ufficiali non provate oggi.

**Domanda (pubblico USA, valore alto):** en/us "benin citizenship" **10** ("for african americans", "by dna", "requirements", "dna test", "application"); en/us "ghana citizenship for" **10** ("african american application year of return", "for jamaicans", "for diaspora"); en/us "african citizenship for african americans" **9**.

**Perché solo 5:** è una regola che cambia di rado, con 3-5 pagine possibili e nessun numero aggiornato (il portale non pubblica quante domande sono state accolte); nei risultati ci sono già giornali e forum. Test del DNA come affiliazione: commissione non letta. **Stima:** 30 / 150 / 600 €; 6-10 ore. Pagina singola in Visa Income solo se avanza tempo nella coda.

---

## 6. Rimesse per Paese di provenienza — voto 4, NO

`centralbank.go.ke/diaspora-remittances/` **200** con file mensile `wp-content/uploads/2026/10/September2026.xlsx` (rimesse per Paese di provenienza: USA, Regno Unito, Germania, resto del mondo) e indagine 2025 sulle famiglie. Domanda en/ke "diaspora remittances" **9** ("to kenya 2025", "by country", "to nigeria in 2025"); "how much do nigerians in diaspora send" **0**. Pubblico keniano e giornalisti, nessun pagatore (chi legge statistiche non sta mandando soldi). Confermato il NO del 18 e del 28/10 sulle rimesse; al massimo una riga nella pagina `moved-to` della Kenya, se un giorno esiste. Stima 10 / 40 / 150 €.

---

## 7. Marocchini d'Europa in estate: Opération Marhaba, dogana per auto e pensionati (MRE) — voto 4, NO

Domanda vera in francese e olandese: fr/fr "operation marhaba" **10** ("2026 date", "algeciras", "tanger med", "2025 chiffres"); fr/fr "admission temporaire voiture maroc" **10** ("2026", "1 an", "en ligne", "prolongation"); fr/fr "douane maroc mre" **7** ("60 ans", "voiture", "calcul", "retraité"); fr/be "bateau maroc" **10**; nl/nl "boot marokko" **10**. Ma **tutte le fonti ufficiali sono chiuse dal server:** dogana marocchina `douane.gov.ma` **000** (anche in http), `marhaba.ma` **000**, Fondazione Mohammed V `fm5.ma` **503**, Operación Paso del Estrecho su `interior.gob.es` **403**, pagina OPE di Protezione Civile 404. I traghetti sono già NO (30/10: nessuna fonte ufficiale, Ferryhopper e Direct Ferries); Yabiladi e Le360 coprono le notizie. Si riapre solo se la dogana marocchina diventa leggibile (tabella delle franchigie MRE e del calcolo per i pensionati).

---

## 8. Visto per la Nigeria per nazionalità (anche figli della diaspora) — voto 4, NO

Domanda: en/us "nigeria visa for" **10** ("us citizens", "us citizens cost", "indians"); en/gb "nigeria visa for british" **10** ("british passport holders", "uk citizens cost", "uk residents"); en/us "nigerian visa fee" **10** ("usa", "uk", "from canada"). Fonte: `immigration.gov.ng/nigerian-visa/` **200** descrive le classi di visto (Short Visit e-Visa, embassy, "Visiting Visa – Multiple Entry … based on reciprocity … up to five years") ma **nessuna tabella di prezzi per nazionalità**: il prezzo si vede solo dentro l'applicazione `evisa.immigration.gov.ng` (pagina JavaScript da 1,5 KB) e varia per reciprocità e ambasciata. A differenza dell'India (tabella ufficiale di 172 righe, voto 7 il 31/10) qui la tabella non esiste. Stesso NO del 30/10 sui moduli d'ingresso.

---

## 9. Dazio sulle auto importate in Kenya (lista CRSP del KRA) — voto 4, NO

Domanda locale fortissima: en/ke "kra duty calculator" **10** ("2026", "for motor vehicle", "excel"); en/ke "crsp" **10** ("kra 2026", "calculator kenya"); dal Regno Unito debole (en/gb "import car to kenya from uk" 3). `kra.go.ke` home **200**, ma la lista non è collegata dalla home (un indirizzo provato 404); dalla ricerca web l'ultima lista è quella in vigore dall'**1/7/2025**, con un sito di calcolatori che dice di non riuscire a leggere le pagine del KRA. Calcolatori automatici già presenti, venditori di auto giapponesi con il proprio calcolatore, pubblico keniano a 1-2 €. NO.

---

## 10. NO confermati senza fatti nuovi

- **WAEC/JAMB** (date, risultati, punteggi minimi): chi cerca vuole il portale ufficiale; pubblico che vale pochissimo (30/10).
- **Passaporti** nigeriani, ghanesi, keniani, sudafricani (in patria e dall'estero): riserva 5,5 del 30/10 invariata; `immigration.gov.ng/passports/` **200** ha solo requisiti, nessuna tabella dei tempi.
- **Rifiuti dei visti USA per nazionalità**: `travel.state.gov` ancora **403** oggi (anche la pagina dei visti bond).
- **Costo delle rimesse per corridoio** (UK → Nigeria, USA → Ghana): comparatori pieni; Banca Mondiale 403 (28/10).

---

## 11. Cosa farei (in ordine di guadagno atteso per ora)

1. **Idea 2 (6-10 ore)**: riquadro "USA" nelle pagine nazionalità + pagina centrale, prima del prossimo aggiornamento del proclama. Revisione dei fatti obbligatoria.
2. **Idea 1 (18-26 ore)**: "Where [nationals] live" accanto a `moved-to`, partendo da Nigeria, Ghana, Kenya, Sudafrica, Somalia, Zimbabwe, India, Pakistan, Filippine (le nazionalità che già portano visite), USA (ACS 2025) e Regno Unito (censimento 2021) prima; Canada e Australia dopo.
3. **Idea 3 (5-8 ore)**: solo come riquadro, in coda bassa.
4. **Proposta a Massimiliano** (sì/no, nessuna spesa adesso): provare la lettura di `travel.state.gov` da GitHub Actions; se fallisce, valutare un piccolo server con indirizzo fisso (pochi euro al mese). È il vincolo che blocca le domande americane più grandi di questo angolo (rifiuti per nazionalità, visti bond, pausa per 75 Paesi).

## 12. Righe proposte per ESPLORATE (da copiare dal coordinatore; questo file non modifica ESPLORATE)

| Nicchia | Verdetto | Rapporto |
|---|---|---|
| **Dove vive la diaspora: nati in [Paese] per città/contea in UK (censimento 2021, Nomis NM_2032_1, OGL), USA (ACS B05006 2025 a 1 anno uscita il 29/10/2026, file in blocco senza chiave), Canada, Australia** (Nigeria in USA 479.759, Houston 51.617; Greenwich 14.357) | **SEZIONE** (voto 6,5; 80 / 500 / 2.000 €/anno; 18-26 ore) in Visa Income accanto a `moved-to` | wf-2026-10-31-africa-diaspora |
| **Divieto d'ingresso USA per nazionalità** (Proclamation 10998, PDF govinfo 200, 19 totali + 20 parziali, overstay per Paese; state.gov 403 per bond, pausa 75 Paesi, reciprocità) | **RIQUADRO** (voto 6, 7 con state.gov; 40 / 250 / 1.200 €/anno; 6-10 ore) nelle pagine nazionalità di Visa Income | wf-2026-10-31-africa-diaspora |
| Test TB per il visto britannico: cliniche e prezzo per Paese (gov.uk API, Nigeria 94/49 $) | riquadro in coda bassa (5,5; 10 / 60 / 290 €) | wf-2026-10-31-africa-diaspora |
| PLAB 1 / AMC / USMLE / MCCQE per medici africani | RISERVA (4,5): gmc-uk.org, mcc.ca, ecfmg.org 403 (Cloudflare); AMC su Pearson VUE; sedi di Accra e Alessandria chiuse dal 2027 | wf-2026-10-31-africa-diaspora |
| Cittadinanza per afrodiscendenti (Benin, Ghana, Sierra Leone) | 5: una pagina se avanza tempo (myafroorigins.bj 200, nessun numero) | wf-2026-10-31-africa-diaspora |
| Rimesse per Paese di provenienza (CBK mensile); Opération Marhaba e dogana MRE (douane.gov.ma 000, fm5.ma 503, interior.gob.es 403); visto nigeriano per nazionalità (nessuna tabella); dazio auto Kenya (CRSP) | NO (4) | wf-2026-10-31-africa-diaspora |
