# Africa e Medio Oriente: salute, lavoro e visti in uscita, studio, soldi (4/11/2026)

Zona: Nigeria, Kenya, Sudafrica, Egitto, Marocco, Ghana, Golfo, Turchia, Israele. Settori di questo giro: salute, lavoro e visti in uscita verso Europa, Regno Unito, Canada e Golfo, studio all'estero, rimesse e soldi. Modello cercato: numeri ufficiali per nazionalità (come Visa Income) o passaggi obbligatori per città (come EsameB1), in inglese o francese.

**Letti prima:** skill `rete-siti`, `REGOLE-FISSE.md` (regole del 30 e 31/10), `STRATEGIA.md`, `ESPLORATE.md`, i rapporti `wf-2026-10-31-africa-diaspora.md`, `wf-2026-10-31-golfo-asia.md`, `ricerca-zona-latam-africa-2026-10-30.md`, `idee-2026-10-30-studio.md`, `wf-2026-10-31-lavoro-salari.md`, `wf-2026-10-31-salute-amministrativa.md`, `fronti-2026-10-31-lingue-immigrati.md`. **Non rifatti** (già chiusi, nessun fatto nuovo): rifiuti dei visti per nazionalità (FATTO), test TB britannico (riserva), PLAB (riserva), divieto d'ingresso USA (riquadro in coda), diaspora per città (sezione in coda), GAMCA/Wafid, stipendio per il visto di famiglia nel Golfo, Skill Verification saudita, Hajj, rimesse per corridoio, costi dei visti di studio, studenti per università HESA (403), LMIA, costo del trasferimento in Canada.

**Metodo (tutte le prove del 4/11/2026):** `curl` dal nostro server (stato HTTP, dimensione, `Last-Modified`), file aperti e contati; autocomplete Google (`client=firefox`) con Paese e lingua giusti (en/ng, en/gh, en/ke, en/za, en/eg, en/in, en/ph, en/gb, en/au, en/us, fr/ma, fr/dz, fr/tn, fr/cm, tr/tr, iw/il); ricerca web (dagli USA) per vedere chi c'è nei risultati. **Nessun blocco aggirato:** dove la risposta è 403, 000 o reCAPTCHA mi sono fermato e l'ho scritto.

**Numeri veri della rete (GoatCounter 5/10-4/11/2026):** Visa Income 130 visite, quasi tutte sulla sezione rifiuti: `pakistan` 20, `nigeria` 9, `iraq` 8, `turkiye` 6, `iran` 6, `tunisia` 5, `algeria` 4, `morocco` 3. EsameB1 592. I pubblici di questa zona arrivano, ma valgono poco a visita: le stime sotto usano 1-3 € ogni 1.000 visite per lettori in Africa e Asia del Sud e 6-10 € per lettori in Regno Unito, Irlanda, Australia e Canada (ipotesi del cruscotto del 30/10, AdSense non ha ancora incassi: **sono stime, non dati**).

Voto con la griglia solita: domanda 0-3 · buco nei risultati 0-2 · fonte ufficiale leggibile e riusabile 0-2 · valore del pubblico e chi paga 0-2 · rischi e ore 0-1.

---

## 0. Risposta in breve

**Nessuna idea arriva a 8; nessuna passa l'asticella dei siti nuovi** (voto ≥ 7 e ≥ 5.000 €/anno). Quattro idee sono sezioni o pagine a costo zero con guadagno positivo (regola della rete fitta del 30/10), tutte in Visa Income Checker; tre di queste si costruiscono con dati già scaricati o leggibili oggi.

| # | Idea | Dove | Voto | €/anno a 18 mesi (prudente / centrale / ottimista) | Ore | Chi paga |
|---|---|---|---|---|---|---|
| 1 | **Infermieri all'estero per Paese di formazione: quanti nel Regno Unito e in Irlanda, quanti visti Health and Care, lista rossa OMS 2026, costi NMC** | sezione di Visa Income | **6,5** (7 la pagina "lista rossa 2026" nella finestra della nuova lista) | 50 / 350 / 1.800 | 14-20 | AdSense (annunci di reclutamento nel Regno Unito), Wise quando attivo |
| 2 | **Pensione statale britannica all'estero: congelata o no, Paese per Paese, con calcolatore "quanto perdo" + contributi volontari dal 6/4/2026** (Sudafrica, Kenya, Nigeria, Ghana congelate; Israele e Turchia rivalutate per accordo) | aggiunta alla sezione "UK pension tax" già in coda in Visa Income | **6,5** | 80 / 400 / 1.800 | 10-14 con la sezione HMRC, 16-20 da sola | AdSense pensionati UK (6-10 €), Wise |
| 3 | **UK Ancestry visa per nazionalità** (Sudafrica 645 rilasciati nel 2025 e 7 rifiutati; India 40 e 22 rifiutati; costi in ZAR/AUD) | una pagina in Visa Income | **6** | 30 / 200 / 700 | 4-6 (dati già in casa) | AdSense Sudafrica/Australia/Canada/NZ |
| 4 | **Israele come destinazione in "moved-to"**: nuovi immigrati 2025 per Paese d'origine e città (22.423 in tutto; USA 3.733, Francia 3.353, Regno Unito 892, Canada 452, Sudafrica 256) | pagine `moved-to/<nazionalità>/israel` | **5,5** | 20 / 120 / 600 | 5-8 | AdSense USA/Francia/UK, Wise |
| 5 | Strutture sanitarie autorizzate al turismo sanitario in Turchia per città (lista del Ministero, PDF del 27/10/2026) | – | 5 RISERVA | 20 / 150 / 900 | 12-16 | AdSense UK (tema sanitario) |
| 6 | TCF Canada / TCF Québec in Marocco e Tunisia per città (prezzi; date non leggibili) | – | 5 RISERVA | 10 / 80 / 400 | 10-14 | AdSense Maghreb (1-2 €) |
| 7 | Infermieri formati all'estero in Germania per Paese (Destatis 21231) | aggiunta alla n. 1 | RISERVA (serve un account gratuito Destatis) | – | – | – |
| 8 | Tasse del permesso di soggiorno turco per nazionalità | – | 4 NO | – | – | – |
| 9 | Sponsor britannici con licenza revocata | – | 4 NO | – | – | – |
| 10 | Banche non accettate per il visto studenti britannico | – | 3 NO | – | – | – |
| 11 | "Evidence level" australiano per Paese (visto studenti) | – | 4 NO | – | – | – |
| 12 | Goethe A1 per il ricongiungimento in Germania (Turchia, Egitto, Marocco) | – | 3,5 NO | – | – | – |
| 13 | Soldi da mostrare per l'Express Entry canadese in naira/cedi/scellini | – | 4 NO | – | – | – |
| 14 | Emigrazione fiscale sudafricana e ritiro della retirement annuity | – | 4 NO | – | – | – |

**Totale delle quattro sezioni utili (1-4):** 180 / 1.070 / 4.900 €/anno, 33-48 ore. Primi soldi: 2°-3° mese dopo la pubblicazione (AdSense). La n. 1 e la n. 2 hanno una data che porta ricerche: la nuova lista OMS (pubblicazione annunciata "later in 2026") e i contributi volontari cambiati dal 6/4/2026.

**La migliore:** la n. 1 (infermieri), perché è il modello che porta già visite (numeri ufficiali per nazionalità citati dagli assistenti AI: "how many indian nurses in ireland", "how many nigerian nurses in uk") con due fonti nuove mai usate nella rete e un evento datato (lista rossa 2026). La n. 2 vale di più a visita, ma è per metà fuori zona (Australia e Canada sono i Paesi più cercati).

**Lezioni del giro.**
1. **Confermato per la terza volta (30/10, 31/10, 4/11): il pubblico che vive in Africa e nel Golfo paga poco.** Le idee che reggono sono quelle in cui il lettore vive in Regno Unito, Irlanda, USA, Australia (infermieri già partiti, pensionati, discendenti con l'Ancestry visa, chi fa l'aliyah dagli USA e dalla Francia).
2. **I dati britannici già in casa valgono più di quanto usiamo.** Il file Home Office delle decisioni sui visti (`uk-entry-clearance-outcomes.xlsx`, giugno 2026, scaricato il 4/11) ha il dettaglio per sottotipo di visto: Health and Care Worker, UK Ancestry, Skilled Worker, Graduate. Oggi la sezione rifiuti usa solo i gruppi. Le idee 1 e 3 nascono da lì e costano poche ore.
3. **Turchia ed Egitto chiudono le tabelle per nazionalità** (tasse del permesso turco calcolate solo dentro e-ikamet; Goethe 403): niente cloni di Visa Income da quella parte.

---

## 1. Infermieri all'estero per Paese di formazione — voto 6,5, SEZIONE di Visa Income

**L'idea in una riga.** Una pagina per Paese di formazione (India, Filippine, Nigeria, Ghana, Kenya, Zimbabwe, Nepal, Pakistan, Sri Lanka, Sudafrica, Egitto, Camerun: le 12 con numeri sufficienti) con: quanti infermieri formati lì sono iscritti all'albo nel Regno Unito (NMC, marzo 2026) e in Irlanda (2025), quanti si sono iscritti negli ultimi 6 mesi e il calo dal 2023, quanti visti Health and Care il Regno Unito ha rilasciato a quella nazionalità, se il Paese è nella **lista rossa** (reclutamento attivo vietato, candidatura diretta permessa), e i costi ufficiali NMC. Più una pagina centrale "Red list countries 2026" che segue l'aggiornamento della lista OMS.

**Fonti ufficiali (verificate con curl il 4/11/2026).**
- **NMC, Registration data reports**: `nmc.org.uk/about-us/reports-and-accounts/registration-statistics/` **200**; file `.../data-reports/2026/nmc-register-march-2026-uk-data-tables.xlsx` **200**, 863.884 byte, `Last-Modified: 28 Jul 2026`; fogli "Training Country ALL", "Training Country Joiners", "Training Country Leavers", ogni 6 mesi dal 2020. Prove: iscritti formati in **Nigeria 17.092** (marzo 2026; erano 14.815 un anno e mezzo prima), **India 73.026**, Filippine 50.527, Ghana 8.531, Zimbabwe 4.798, Nepal 3.087, Sudafrica 2.836, Kenya 2.585, Pakistan 1.838, Camerun 239, Turchia 128, Egitto 106; totale albo 867.935. Nuovi iscritti nei 6 mesi a marzo 2026: India 1.748 (erano 3.399 un anno prima), Nigeria 683 (1.074), Ghana 612 (927), Filippine 337 (758): **il calo è la notizia** e nessuno nei risultati la dà per Paese. **Licenza:** le condizioni NMC (sez. 6) tengono il diritto d'autore e permettono la riproduzione libera solo di "rules, standards and guidance"; i numeri si citano come fatti, pochi per pagina, con link al file e "Source: NMC" (rischio basso ma da far vedere al revisore).
- **Irlanda, Department of Health, JQ06 "Stock of nurses by country of first qualification"**: `data.gov.ie/api/3/action/package_show?id=jq06-...` **200**, licenza **CC BY 4.0**, aggiornato il 3/9/2026; CSV `assets.gov.ie/.../JQ06_-_Stock_of_Nurses_by_country_of_training.csv` **200**, 125.136 byte (codifica cp1252), anni 2021-2025. Prove 2025: **41.951 formati all'estero su 77.090** (54 %); **India 20.568**, Regno Unito 9.486, Filippine 6.946, Zimbabwe 718, **Nigeria 676**, Ghana 305, Kenya 60.
- **Home Office, visti Health and Care Worker per nazionalità**: già in casa (`visaincome/raccolta/_grezzi/uk-entry-clearance-outcomes.xlsx`, foglio Data_Vis_D02, sottotipo "Health and Care Worker", dati fino al 2° trimestre 2026; OGL v3). Prove 2025, visti rilasciati: India 14.589, **Nigeria 7.712**, **Zimbabwe 4.153**, **Ghana 2.678**, **Egitto 1.636**, Kenya 868, Sudafrica 394.
- **Lista rossa**: GOV.UK Content API, "Code of practice for the international recruitment of health and social care personnel in England" **200** (JSON, OGL, aggiornato il 27/3/2025): "The red list is drawn from the WHO Health Workforce Support and Safeguards List 2023"; regola della candidatura diretta; "updated by WHO every 3 years". **Fatto nuovo:** pagina OMS `who.int/news-room/questions-and-answers/item/who-health-workforce-support-and-safeguards-list` **200**, datata **5/8/2026**, descrive la **SSL 2026** con la novità dell'"opzione di flessibilità" (i Paesi possono chiedere di uscire dalle raccomandazioni); la lettera circolare C.L.25.2026 dell'8/6/2026 (trovata solo su un sito specchio, non letta come fonte) parla di una lista provvisoria di **36 Paesi contro i 55 del 2023**, con risposte dei governi entro il 31/8/2026. Quando l'OMS pubblica la lista e il Regno Unito aggiorna l'allegato A, cambia la risposta a "is Nigeria still on the red list".
- **Costi NMC**: `nmc.org.uk/registration/information-for-internationally-trained-applicants/` **200**: valutazione £167, CBT £83, OSCE £794, iscrizione £182; la stessa pagina dice "total cost £1,170", ma la somma fa £1.226: **da far controllare al revisore** (probabile importo vecchio).

**Domanda (autocomplete).**
- en/in "how many indian nurses in" **10**: germany, uk, ireland, usa, australia, canada, saudi arabia, new zealand, kuwait, uae. en/ph "how many filipino nurses in" **10** (us, saudi arabia, uk, germany, canada, australia…).
- en/ng "how many nigerian nurses" **9** ("in uk" primo); en/gb "nigerian nurses in uk" **10** ("how many nigerian nurses in uk", "can nigerian nurses work in uk").
- en/gh "nmc registration fee" **10** ("2026", "for overseas nurses", "increase"); en/ng "nmc application fee" **10**; en/ng "nmc osce fee" **6** ("pass rates", "resit fee"); en/ng "nmc cbt centre in" **10** (Nigeria, Ibadan, Lagos, Kerala, Arabia Saudita).
- Lista rossa: en/ng "is nigeria on the red list" **6** ("still on uk red list", "for sponsorship visa", "nhs red list"); en/gh "is ghana on the red list" **4** ("off the red list", "still on the who red list"); en/ng "red list countries for nurses" **4** ("who red list countries 2026 for nurses"); en/gb "nhs red list countries" **5**.

**Chi c'è oggi su Google** ("how many indian nurses in uk NMC register 2026"): ThePrint e Udayavani con il dato **2021-22 (37.815)**, blog di agenzie (Y-Axis, Leap Scholar, acadfly), pagine automatiche `wheretoemigrate.io`/`.pages.dev` e `immigrationstartguide.com`, RCNi con il totale. Per la Germania ("how many filipino nurses in germany") solo stime di stampa ("circa 6.000", DW 2024). **Nessuno usa i file NMC di marzo 2026 né il JQ06 irlandese per Paese.** Battibile sui numeri; non sulle domande "come diventare infermiere in UK" (agenzie e NHS).

**Chi paga e quanto.** AdSense: lettori in India, Filippine, Nigeria, Ghana (1-3 €), più una parte che vive già in Regno Unito o Irlanda (6-10 €, annunci di agenzie di reclutamento sanitario): media stimata 2-4 €. Wise (CPA da 10 £, iscrizione di Massimiliano non ancora fatta) per chi manda soldi a casa. Corsi OET/IELTS per infermieri: nessun programma letto oggi, non conto nulla.

**Stima a 18 mesi (formula: visite al mese × 12 × € ogni 1.000).**
- Prudente: 1.500 × 12 × 2 € = 36 € + 15 € di picco lista rossa → **50 €**.
- Centrale: 5.000 × 12 × 3,5 € = 210 € + 100 € nei mesi della lista 2026 + Wise ~40 € → **350 €**.
- Ottimista: 15.000 × 12 × 6 € = 1.080 € + citazioni degli assistenti e lettori UK/IE + affiliazione corsi → **1.800 €**.
- Primi soldi: 2°-3° mese; picco quando esce la lista OMS 2026 (annunciata per il 2026) e quando il Regno Unito aggiorna l'allegato A.

**Ore:** 14-20 (lettura di due xlsx/CSV, filtro del sottotipo nel file Home Office già in casa, 12 pagine Paese + 2 pagine Paese di arrivo + pagina lista rossa + pagina costi; controllo settimanale automatico della pagina OMS e della pagina GOV.UK, pubblicazione solo se cambiano).

**Voto 6,5** = domanda 2,5 + buco 1,5 + fonte 1,5 (JQ06 CC BY e Home Office OGL; NMC solo citazione) + valore 0,5 + rischi/ore 0,5. **7 per la sola pagina "Red list countries 2026"** nella finestra della nuova lista.

**Rischi:** "formati in" non è "nazionalità" (un infermiere indiano formato nel Regno Unito conta come UK): va detto in alto, come in `moved-to`; frasi sulla lista rossa da scrivere con cura (vietato il reclutamento attivo, non la candidatura); tema "lavoro sanitario", non medico: non tocca la regola "medicina esclusa".

**Allargamenti (fatti a parte, non nel conto):** Germania (Destatis 21231, riconoscimenti per Paese di formazione; l'API ospite risponde **401** "not allowed": serve un account gratuito Destatis a nome di Massimiliano, 5 minuti) e Australia (AHPRA, non provata oggi): sono le domande con "germany" e "australia" in testa all'autocomplete indiano e filippino.

---

## 2. Pensione statale britannica all'estero: congelata o no, con calcolatore — voto 6,5, AGGIUNTA alla sezione HMRC in coda

**L'idea in una riga.** Accanto alla sezione già in coda "Dove si paga la tassa sulla pensione britannica" (voto 7,5 del 30/10, `ricerca-numeri-ufficiali-2026-10-30.md`), per ogni Paese: la State Pension **sale ogni anno o resta congelata?** (Sudafrica, Kenya, Nigeria, Ghana, Egitto, Marocco, Emirati: congelata; Israele e Turchia: rivalutata per accordo di sicurezza sociale; UE: rivalutata), con un **calcolatore "quanto perdo"** (anno in cui si è lasciato il Regno Unito → importo congelato contro importo di oggi) e le **nuove regole dei contributi volontari per i periodi all'estero dal 6/4/2026**.

**Fonti (verificate).**
- GOV.UK Content API `state-pension-if-you-retire-abroad` **200** (OGL): "Your State Pension will only increase each year if you live in: the EEA, Gibraltar, Switzerland, countries that have a social security agreement with the UK (but you cannot get increases in Canada or New Zealand)".
- Storico degli importi: "Abstract of DWP benefit rate statistics 2025" (GOV.UK, pubblicato il 28/1/2026, OGL; trovato con l'API di ricerca GOV.UK **200**; tabelle da leggere in costruzione).
- Contributi volontari: pagina GOV.UK "Voluntary National Insurance contributions for periods abroad from 6 April 2026" (pubblicata il 16/3/2026, API di ricerca **200**).

**Domanda.** en/gb "is uk pension frozen in" **10** (australia, thailand, philippines, spain, canada, "countries where uk state pension is not frozen"); en/gb "uk pension frozen" **10** ("latest news", "for expats"); en/za "uk pension in south africa" **10** ("tax on uk pension in south africa", "can i get my uk pension in south africa"); en/gb "voluntary national insurance contributions abroad" **10** (con "changes" e "for periods abroad from april 2026"); en/au "uk voluntary contributions" **10** ("class 2", "deadline", "abroad"). Kenya e Ghana: 0 (domanda solo dal Sudafrica nella zona).

**Chi c'è su Google:** Wikipedia "Frozen state pension", campagna frozenbritishpensions.org, articoli (GB News, Interactive Investor "£37.477 in 15 anni", MoneyWeek, Saga, fxcompared). **Nessun calcolatore per anno di partenza** trovato: è il buco.

**Chi paga:** AdSense con pensionati britannici all'estero (6-10 €), Wise (CPA 10 £, da attivare). **Stima:** prudente 1.000 × 12 × 6 € = 72 → **80 €**; centrale 4.000 × 12 × 8 € = 384 → **400 €**; ottimista 12.000 × 12 × 10 € = 1.440 € + Wise → **1.800 €**. Primi soldi: 2° mese.

**Ore:** 10-14 se costruita insieme alla sezione HMRC (stesse pagine Paese), 16-20 da sola. **Voto 6,5** = domanda 3 + buco 1 + fonte 2 + valore 1,5 + rischi/ore −1 (tema soldi con errori costosi, calcolatore da tenere aggiornato ogni aprile; più della metà della domanda è fuori zona). **Rischio:** il calcolo vale per la vecchia "basic State Pension" e per la nuova in modo diverso: due rami nel calcolatore e frase "check your forecast on GOV.UK".

---

## 3. UK Ancestry visa per nazionalità — voto 6, PAGINA di Visa Income

**L'idea.** Una pagina "UK Ancestry visa: who gets it and how many are refused, by nationality" con i numeri del file Home Office già in casa (sottotipo "UK Ancestry"), i costi ufficiali in sterline e nella valuta del lettore (ZAR, AUD, CAD, NZD con i cambi che Visa Income già aggiorna) e la regola del nonno (non il bisnonno).

**Fonte.** `uk-entry-clearance-outcomes.xlsx` (Home Office, giugno 2026, OGL; in casa). Prove 2025: **Sudafrica 645 rilasciati, 7 rifiutati, 4 ritirati**; Australia 433 / 7 / 6; Canada 282 / 3; Nuova Zelanda 280; **Zimbabwe 91 / 11 rifiutati**; India 40 rilasciati e **22 rifiutati**, 19 ritirati; USA 22 / 5 / 10; Pakistan 21 / 3 / 9. Il confronto per nazionalità non c'è da nessuna parte.

**Domanda.** en/za "uk ancestry visa" **10** ("south africa", "cost south africa", "great grandparent", "processing time", "changes"); en/au **10** ("for australian citizens", "age limit", "grandparent"). "ancestry visa uk success rate" 0: la domanda è sui requisiti e sul costo, il numero dei rifiuti è il valore aggiunto, non la domanda principale.

**Google:** GOV.UK primo; studi legali e consulenti sudafricani e australiani. **Chi paga:** AdSense Australia/Canada/NZ (8-10 €), Sudafrica (2-3 €). **Stima:** 30 / 200 / 700 €/anno. **Ore:** 4-6. **Voto 6** = domanda 2 + buco 1 + fonte 2 + valore 1 + rischi/ore 0 (una sola pagina, poca coda lunga).

---

## 4. Israele come destinazione in "moved-to" — voto 5,5, PAGINE in coda

**L'idea.** La sezione `moved-to` (Eurostat, IRCC, Home Office) non ha Israele. Il governo israeliano pubblica ogni anno i nuovi immigrati per Paese d'origine e città di arrivo: si aggiungono le pagine `moved-to/americans/israel`, `/british/israel`, `/canadians/israel`, `/south-africans/israel` (e Francia nella versione francese, quando esiste) con il totale 2025 e le prime città.

**Fonte (verificata).** `data.gov.il` (CKAN) **200**, dataset "עולים חדשים לפי שנים" (aggiornato il 23/2/2026, licenza aperta del governo israeliano); il file CSV diretto risponde **403** (CloudFront), ma l'API ufficiale `datastore_search` risponde **200** con i record anonimi (anno, mese, età, sesso, Paese d'origine, città, professione: nessun nome). Conteggio 2025 fatto dal server: **22.423** nuovi immigrati; Russia 8.548, **USA 3.733** (Gerusalemme 959, Beit Shemesh 496, Tel Aviv 424, Ra'anana 243), **Francia 3.353** (Netanya 805, Gerusalemme 565, Tel Aviv 440), Ucraina 928, **Regno Unito 892**, Bielorussia 470, Canada 452, Georgia 284, Argentina 280, **Sudafrica 256**. Solo numeri aggregati nelle pagine.

**Domanda.** en/us "aliyah statistics" **8** ("2025", "2026", "by country", "by year"); fr/fr "alyah france" **7** ("chiffres", "2025", "nombre alyah france"); en/gb "aliyah from uk" **6**. Più forte la domanda sui soldi ("sal klita" **10** in USA, Israele e Francia, con "2026" e "amount"), ma la pagina ufficiale `gov.il` risponde **403** e Nefesh B'Nefesh ha già la tabella: non si fa.

**Chi paga:** AdSense USA/Francia/UK (tema immigrazione, 6-8 €), Wise (trasferimenti verso Israele). **Stima:** 20 / 120 / 600 €/anno. **Ore:** 5-8 (stesso generatore di `moved-to`). **Voto 5,5** = domanda 1,5 + buco 1 + fonte 1,5 + valore 1 + rischi/ore 0,5 (tema politicamente sensibile: solo numeri e fonte, nessun commento).

---

## 5. Turismo sanitario in Turchia: strutture autorizzate per città — voto 5, RISERVA

**Fonte (verificata):** Ministero della Salute turco, `shgmturizmdb.saglik.gov.tr` **200**, pagina "Yetkili Sağlık Tesisleri" aggiornata il **5/10/2026** con 4 PDF (ospedali, centri medici, ambulatori, altre strutture) e l'elenco delle agenzie autorizzate; il PDF degli ospedali (`dosyamerkez.saglik.gov.tr/Eklenti/56715/...`) **200**, `Last-Modified: 27 Oct 2026`, leggibile con `pdftotext` (1.849 righe, provincia, nome, tipo, indirizzo, telefono; Istanbul 271 righe). `saglikturizmi.gov.tr` 000.

**Domanda:** en/gb "turkey teeth" **10** (cost, implants, packages, "gone wrong"), ma la domanda di verifica è debole: "health tourism authorization certificate turkey" **5**, "licensed clinics in turkey" **0**, "is my clinic in turkey" **0**.

**Perché riserva:** tema sanitario (regola "medicina esclusa" del 9/10: serve il sì di Massimiliano); gli ambulatori ("muayenehane") portano il nome del medico, cioè dati personali: si userebbero solo ospedali e centri medici; le cliniche di trapianto capelli spesso lavorano sotto altre strutture e la lista non risponde a "questa clinica è sicura?". **Stima** 20 / 150 / 900 €/anno, 12-16 ore. Si riapre con il sì sul tema sanitario.

---

## 6. TCF Canada e TCF Québec in Marocco e Tunisia per città — voto 5, RISERVA

**Domanda forte (modello EsameB1):** fr/ma "tcf canada maroc" **10** (prix, rabat, fes, rendez vous, dates, calendrier, agadir); fr/ma "tcf casablanca" **10**; fr/ma "date tcf" **10** (maroc 2026, casablanca, tunisie, cameroun, sousse, alger); fr/tn "tcf canada tunis" **10**; fr/dz "tcf canada alger" **7**; fr/cm "tcf canada" **10** (cameroun, douala).

**Fonti:** Institut français du Maroc `if-maroc.org` **200**, 12 sedi (Agadir, Casablanca, El Jadida, Essaouira, Fès, Kénitra, Marrakech, Meknès, Oujda, Rabat, Tanger, Tétouan); **prezzi leggibili** nella pagina certificazioni di Casablanca (TCF Canada **2.900 Dhs**, TCF Québec **2.900 Dhs**, TCF IRN 1.900 Dhs), ma **le date no**: la pagina TCF Canada non le ha in HTML e il calendario 2026 è un PDF fatto di immagini (`calendrier-PDF-2026-1.pdf`, testo vuoto); le iscrizioni passano da un portale. Tunisia `institutfrancais-tunisie.com` 200 (non letto a fondo); Algeria `if-algerie.com` pagina JavaScript da 1,4 kB; Camerun 000; France Éducation International 2 kB (anti-robot già visto il 30/10).

**Perché riserva:** senza le date resta una tabella di prezzi; pubblico Maghreb a 1-2 € ogni 1.000 visite; gli Institut sono primi su Google per le loro città. **Stima** 10 / 80 / 400 €/anno, 10-14 ore. Si riapre se un Institut pubblica le sessioni in HTML o in un file di testo.

---

## 7. NO (con le prove)

- **Tasse del permesso di soggiorno turco per nazionalità (4).** Domanda vera (en/tr "turkey residence permit fee" **10**, con "for pakistani", "price increase 2026"), ma nessuna tabella ufficiale per Paese leggibile: `goc.gov.tr/ikamet-izni-harclari` e `en.goc.gov.tr/residence-permit-fees` → 302 verso la pagina 404; il calcolo è dentro `e-ikamet.goc.gov.tr`; i siti di avvocati si contraddicono (964 TL di tessera, "57.899 → 4.799 TL" ad aprile 2026 non verificabile); concorrenti già automatici (ikamet.com, pagine `.pages.dev` e `vercel.app`).
- **Sponsor britannici con licenza revocata (4).** Domanda c'è (en/ng "sponsor licence revoked list" **10**, "revoked care sponsor licence list", "2026"), fonte ufficiale sì (registro giornaliero Home Office), ma la revoca non si distingue dalla rinuncia e Tarve (rapporti mensili: maggio 2026 508 tolti, giugno 639), Morgan Smith e huntukvisasponsors fanno già il confronto giornaliero. Stesso NO del 14/10 sugli sponsor.
- **Banche non accettate per il visto studenti britannico (3).** La domanda c'è (en/gh "banks accepted for uk visa" **7**, "approved bank list for uk visa in bangladesh/india"), ma la lista non esiste più: l'Appendix P è stata tolta (pagina GOV.UK del 2020 vuota, 780 byte) e l'Appendix Finance dice solo "unable to make satisfactory verification checks".
- **"Evidence level" australiano per Paese (4).** Domanda (en/np "australia evidence level" **10**, en/pk **8**), ma l'elenco non è pubblicato: lo strumento ufficiale `immi.homeaffairs.gov.au/visas/web-evidentiary-tool` interroga un'API con reCAPTCHA (non forzata); la pagina "evidence-level" 404.
- **Goethe A1 per il ricongiungimento (3,5).** tr/tr "goethe a1 sınav" **10** (tarihleri izmir/ankara, ücreti 2026), en/eg "goethe exam" **10** ("price egypt"); ma `goethe.de` **403** su tutte le pagine d'esame provate.
- **Soldi da mostrare per l'Express Entry nelle valute africane (4).** en/ng "proof of funds canada" **10**, ma `canada.ca` **000** (come il 30/10); confermato il NO "costo del trasferimento".
- **Emigrazione fiscale sudafricana e retirement annuity (4).** en/za "tax emigration" **10**, en/gb "south african expat tax" **9**; ma sono regole, non numeri per Paese o città, e FinGlobal (che vende il servizio) occupa quasi tutta la prima pagina; SARS senza guida 2026.
- **Studenti africani all'estero per nazionalità:** già coperto da `moved-to` (Eurostat motivo "education" + visti britannici); in più la domanda è soprattutto "scholarships for…" (en/eg "egyptian students in" **10**, quasi tutto borse di studio): nessuna pagina nuova.

---

## 8. Cosa farei (in ordine di guadagno atteso per ora)

1. **Idea 3 (4-6 ore, dati in casa):** pagina UK Ancestry. Si fa nella stessa pubblicazione serale di Visa Income con altre sezioni pronte (una pubblicazione al giorno al massimo).
2. **Idea 1 (14-20 ore):** sezione infermieri, partendo dalle 6 nazionalità che già portano visite o hanno numeri grandi (India, Filippine, Nigeria, Ghana, Zimbabwe, Kenya) e dalla pagina "Red list countries 2026", da pronta prima che l'OMS pubblichi la lista. Revisione dei fatti obbligatoria (somma dei costi NMC, frasi sulla lista rossa).
3. **Idea 2:** dentro la sezione pensioni HMRC già in coda, non da sola.
4. **Idea 4 (5-8 ore):** quando si aggiorna `moved-to`.
5. **Da chiedere a Massimiliano (nessuna spesa):** un account gratuito Destatis (GENESIS) per allargare la n. 1 alla Germania, che è la prima destinazione cercata dagli infermieri indiani ("how many indian nurses in germany").

Nessun messaggio a Massimiliano per idee nuove: nessuna arriva a 7 con 5.000 €/anno.
