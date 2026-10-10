# Ricerca C – Lead generation e crescita a pagamento con pubblico Tier 1 (USA/UK/CA/AU) legato all'Italia

Data: 10 ottobre 2026. Autore: Claude (analista) per Massimiliano Cori.
Regole applicate: `studio-business/REGOLE-FISSE.md` (spesa solo come test con tetto e soglia scritta prima; niente cold email; prove che la gente paga; confronto alternative; niente dati inventati) e `intelaiatura/8-leadgen-e-obblighi.md` (consenso separato per la cessione dei contatti, destinatari nominati).
Metodo: ricerca web (~40 query), lettura diretta via `curl` dal server delle pagine ufficiali dei programmi (SafetyWing, Airalo, Trainline, Heymondo, Booking, Smart Move Italy, My Italian Family, ICA, ItalianPod101, Travelpayouts), **Google Trends letto dal server** (API `trends.google.com`, USA, 5 anni, 10/10/2026) per 5 termini, **Google Autocomplete** (hl=en, gl=us e hl=it, gl=it) su ~30 query. Dove un dato non si trova, è scritto **"non trovato"**. Limiti: nessun Keyword Planner (i CPC sono benchmark di settore, non del termine esatto); le pagine ufficiali di italki, Preply, Babbel, DiscoverCars, World Nomads e Welcome Pickups non si aprono dal server (404/403): le loro cifre vengono da directory terze e sono segnate come "non verificate".

---

## 1. Tabella riassuntiva

| # | Candidata | Qualcuno paga? (prova) | Domanda Tier 1 (Trends USA, 5 anni) | Cosa costruiamo | Investimento | Ricavo prudente 12 mesi | Probabilità | Ore Massimiliano | Automatico? | Vincoli |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Cittadinanza per discendenza | Pratiche da 5-15k $ (My Italian Family 8-15k $, Domani 5-10k €). **Nessun programma di affiliazione/referral pubblico** trovato per ICA, Mazzeschi, Bersani, MIF, IDC. Unico: Smart Move Italy (commissione non pubblica). Gli avvocati **non possono** pagare provvigioni per clienti (art. 37 Codice deontologico forense) | In calo: media 2026 ≈ 20 su 100 contro picco maggio 2024 = 100 e 41 nel Q1 2025 (decreto); ultime 8 settimane 7-12 | Sito EN "chi è ancora idoneo dopo la legge 74/2025" + verifica idoneità + modulo con consenso separato verso un solo partner nominato | 0 € (test ads solo con partner firmato, tetto 100 €) | 0-1.500 € | **Bassa-media** (domanda -70 %, compratori in parte avvocati, SERP piena di agenzie con blog propri) | 3-5 h (contatto partner, firma) | Sì dopo l'accordo | Consenso separato; art. 37 CDF; attività commerciale → CCIAA al primo incasso |
| 2 | Trasferirsi in Italia (ERV, 7 % pensionati, casa) | Smart Move Italy: programma partner pubblico, "commissione per ogni iscrizione", accetta blogger/YouTuber; pacchetti ERV 4.000-8.000 €. Agenzie immobiliari: provvigione solo a mediatori abilitati (L. 39/1989) → no | **In crescita costante**: "move to italy" media 13,5 (2021) → 48,8 (2026); "retire to italy from usa/uk/canada/australia" in autocomplete | Sito EN satellite "Retire/Move to Italy: 7 % flat tax towns list, ERV income requirements" + modulo partner | 0 € | 0-2.000 € (1 cliente da 4-8k € a commissione sconosciuta; serve la cifra all'onboarding) | **Media** (domanda cresce, un compratore pubblico c'è, commissione ignota, concorrenza forte) | 3-4 h (candidatura partner, verifica termini) | Sì | Stessi di 1; nessun referral su immobili senza abilitazione |
| 3 | Scuole/corsi di italiano online (affiliazione) | ItalianPod101 **25 % per vendita, cookie senza scadenza** (FAQ ufficiale); italki ~10-15 $ per nuovo studente; Preply 15 £ (Awin UK); Babbel fino a ~80 €/vendita (terzi, non verificati) | "learn italian" in crescita: 27,6 (2021) → 48,9 (2026), picco marzo 2026; ma autocomplete = "free" | Pagina "imparare l'italiano prima del viaggio/trasferimento" sui siti EN; link affiliati | 0 € | 100-500 € | **Alta che renda qualcosa, bassa che renda molto** | 0,5 h (iscrizioni) | Sì | Dichiarare i link come pubblicità; fiscale come sopra |
| 4 | Affiliazione viaggi su Italy Strikes Today | Cifre pubbliche: Omio 6 % (eCPC 0,07 $), Welcome Pickups 8-9 % (eCPC 0,03 $), GetYourGuide 8 % (eCPC 0,02 $), SafetyWing ~10 % del premio (pagina ufficiale), Airalo 10 % (ufficiale), EKTA assicurazione 20 %, DiscoverCars 70 % del margine (terzi) | "italy strikes" USA: 3,2 (2023) → 9,0 (2025) → **21,6 (2026)**, picco marzo 2026; autocomplete "italy strikes october 2026", "italy strike website" | Box "Cosa fare se c'è sciopero" con link (treno alternativo Omio, transfer, auto, eSIM, assicurazione) su ogni pagina di sciopero | 0 € | 100-600 € (dipende dal traffico: oggi zero) + AdSense | **Alta** che renda poco; nessun traffico minimo su Travelpayouts/SafetyWing | 1 h (iscrizioni a nome suo) | Sì, al 100 % | Compatibile con AdSense (link non contestuali); disclosure; fiscale |
| 5 | Google Ads per i servizi fotografici di Massimiliano | È lui che incassa: matrimonio media **2.236 €** (sondaggio Fearless, 61 fotografi Italia 2025); headshot Italia "non trovato" (USA 150-350 $/persona) | Autocomplete IT: "fotografo matrimonio prezzi roma/milano/torino" forte; **"fotografo headshot" zero suggerimenti**; "fotografo linkedin milano" esiste | Landing page + campagna locale | 1.000-3.000 € (test a scaglioni da 300 €) | Matrimoni: 1-3 incarichi = 2-6k € lordi; headshot: 300-1.500 € | **Media** matrimoni, **bassa** headshot | **Alte**: ogni cliente è lavoro suo (servizio, telefonate, post-produzione) | **NO** | Nessuno nuovo (già P.IVA 74.20.19) |
| 6 | Amazon Ads sul catalogo KDP | Lo stato del catalogo **non è in questo repo** (nessuna cartella kdp; la skill rimanda a `claude/libro-kdp-stato.md`, assente) | — | Campagne auto per titolo secondo la skill (bid 0,60-0,80 $, stop a 20-25 clic senza vendita) | Test 100 € | Non stimabile senza dati di catalogo; benchmark: ACOS low-content 50-150 % (secondario) | **Bassa-media** | 1 h/settimana (letture report) | Semi | REGOLE-FISSE 9/10: KDP "senza Amazon Ads" salvo decisione nuova |
| 7 | Destination wedding Italia (Massimiliano fotografo per coppie estere) | **16.700 matrimoni di coppie straniere nel 2025 (+9,8 %), 1,1 mld €, 67.000 €/evento, 31,7 % richieste dagli USA** (Osservatorio Italy for Weddings/CST). Fotografo 2.000-5.000 €; i planner **chiedono** ~10 % di commissione al fotografo, non la pagano | "italy wedding photographer cost/price", "tuscany/rome/florence italy wedding photographer" in autocomplete; Trends USA per "italian wedding photographer" troppo basso (≈0-2) | Portfolio EN + schede su directory (Fearless, Wezoree, Zankyou) + Pinterest + Ads EN sulla sua regione | 0-1.000 € | 1-2 matrimoni = 3-8k € (solo se è in Toscana/laghi/costiera/Roma; altrimenti 0) | **Media** (sede dipende), con ~5.000 fotografi di matrimonio in Italia come concorrenza (poidata) | Molto alte | **NO** | Nessuno nuovo |

**Le due migliori per le regole di Massimiliano (automatico, 0 €, Tier 1):** n. 4 (affiliazione viaggi su Italy Strikes Today) e n. 2 (satellite EN "Move/Retire to Italy" con Smart Move Italy come partner). La n. 7 è l'unica ad alto ticket ma è lavoro di Massimiliano, non un business automatico: va trattata a parte (§3 bis).

---

## 2. Dettagli e prove

### 2.1 Cittadinanza italiana per discendenza (jure sanguinis)

**Domanda (Google Trends, USA, "italian citizenship by descent", 10/10/2021-10/10/2026, letto dal server il 10/10/2026, valori relativi 0-100):**

| Periodo | Media trimestrale | Nota |
|---|---|---|
| 2022 | 6-15 | base |
| 2023 | 11-14 | base |
| 2024 Q2 | 41,8 (picco **100** la settimana 19-25 maggio 2024) | notizie su restrizioni e "minor issue" |
| 2024 Q4 | 30,4 (max 82) | |
| 2025 Q1 | **41,4** (max 85) | decreto 28/3/2025 |
| 2025 Q2-Q3 | 31,8 → 23,8 | |
| 2025 Q4 | 17,5 | |
| 2026 Q1 | 28,6 (max 50) | udienza Consulta marzo 2026 |
| 2026 Q2 | 20,6 | sentenza 63/2026 |
| 2026 Q3 | 12,0 | |
| ultime 8 settimane | 7-12 | |

Lettura: la domanda USA **non è crollata a zero ma è circa un terzo del 2024-inizio 2025** e sta tornando ai livelli 2023. È ancora una domanda "di notizie" (autocomplete USA: "italian citizenship by descent changes 2026 / new law / news / minor issue / reddit") più che "di acquisto"; le query di acquisto esistono: "italian citizenship lawyer cost / toronto / canada / melbourne / uk / nyc", "italian citizenship assistance cost / reviews", "italian citizenship by descent lawyer cost".

**Legge e stato al 10/10/2026 (fonti):**
- DL 36/2025 (28/3/2025) convertito in L. 74/2025: cittadinanza automatica solo con genitore o nonno nato in Italia; circa 60.000 pratiche pendenti sotto le vecchie regole ([Feather](https://feather-insurance.com/en-it/blog/citizenship-by-descent); [NTL](https://ntlinternational.com/press/italy-citizenship-by-descent-changes-2026/); [Mazzeschi](https://www.mazzeschi.it/navigate-the-new-italian-citizenship-rules-what-changes-with-law-n-74/)).
- Corte costituzionale: sentenza **63/2026** (depositata 30/4/2026) respinge le questioni di Torino; il limite generazionale è nella discrezionalità del legislatore ([italylawfirms](https://italylawfirms.com/en/italian-citizenship-by-descent-after-the-march-2026-constitutional-court-hearing/); [Mondaq, udienza 9/6/2026 su altri rinvii](https://webiis10.mondaq.com/italy/investment-immigration/1783590/june-9-constitutional-court-hearing-on-italian-citizenship-what-foreign-applicants-need-to-know)). Rinvio alla Corte di giustizia UE pendente (ord. 147/2026, fonte studio legale).
- Cassazione: udienza 14/4/2026 su famiglie USA ([CNN/AP](https://abc17news.com/entertainment/cnn-style/2026/04/16/italy-ruling-that-stripped-millions-of-their-right-to-citizenship-is-scrutinized-by-its-supreme-court/)); sentenza **13818/2026** del 12/5/2026: lo ius sanguinis è "diritto soggettivo assoluto" ([AMDJus, Brasile](https://amdjus.com.br/cidadania-italiana-corte-confirma-direito-por-descendencia-sanguinea/)). Tribunali di merito divisi (Bologna, Napoli, Palermo, Venezia favorevoli in casi singoli; Brescia, Perugia contrari — fonti: blog di studi legali).
- Tassa consolare **600 € per adulto** dal 1/1/2025 (699,10 $ a Washington nel Q3 2026, [Ambasciata](https://ambwashingtondc.esteri.it/en/servizi-consolari-e-visti/servizi-per-il-cittadino-straniero/cittadinanza/consular-fee-for-applying-for-recognition-of-iure-sanguinis-citizenship/)); dal 1/7/2026 domande solo per posta (Chicago, [consolato](https://conschicago.esteri.it/en/servizi-consolari-e-visti/servizi-per-il-cittadino-straniero/cittadinanza/cittadinanza-jure-sanguinis-per-discendenza/)); contributo unificato per le cause "1948" 600 € per ricorrente.
- "Referendum/riforme 2026" citati nel mandato: **non trovato** nulla di specifico su un referendum sulla cittadinanza per discendenza nel 2026 (Domani, marzo 2025, cita un referendum sulla cittadinanza, diverso tema).

**Prezzo di una pratica (fonti):**
| Fonte | Cifra | Data |
|---|---|---|
| [My Italian Family, programma completo](https://www.myitalianfamily.com/italian-citizenship-assistance-programs) (letta 10/10/2026) | **8.000-15.000 $**; consulenze 250-1.000 $ | 2026 |
| [Domani / PresaDiretta](https://www.editorialedomani.it/fatti/il-grande-affare-dello-ius-sanguinis-basta-un-lontano-parente-e-10mila-euro-per-la-cittadinanza-italiana-d27yhnkb) | pacchetti "all inclusive" **5.000-10.000 €**; consolato di San Paolo: 45.000 nuove richieste nel 2024 | 8/3/2025 |
| [The Local, sondaggio lettori](https://www.thelocal.it/20231017/revealed-how-much-it-really-costs-to-get-italian-citizenship-via-ancestry) | documenti 1.500-3.000 $; con avvocato 3.700 € – 20.000-25.000 $ | 10/2023 |
| [TT&Partners](https://www.ttandpartners.com/post/cost-of-italian-citizenship-by-descent-the-2026-comprehensive-price-guide) (studio legale) | onorari 3.000-10.000 $ | 2026 |
| [ICA, servizi](https://italiancitizenshipassistance.com/jure-sanguinis-services/) | "contact us for pricing", tariffa forfettaria | 2026 |

**Chi paga per i contatti (prove cercate: Partnerstack, network di affiliazione, "refer a friend", "we pay referrals"):**
- ICA, Mazzeschi, Bersani, My Italian Family, Italian Dual Citizenship, ICAP, ITAMCAP: **nessun programma di affiliazione o referral pubblico trovato** (ricerche 10/10/2026). ITAMCAP ha solo uno sconto per soci NIAF.
- [Smart Move Italy – Partner](https://smartmoveitaly.com/partner) (letta 10/10/2026): "we reward those referrals with a commission… you earn a commission for every successful sign-up"; servizi coperti: visti, **cittadinanza**, immobili, tasse; partner ammessi: "bloggers, YouTubers, or Instagram creators" oltre ad agenzie; **cifra non pubblica** ("you'll receive your custom link, commission terms" dopo l'approvazione).
- Prezzo per lead nel settore: **non trovato** (nessun marketplace, nessun listino). Riferimento indiretto: CPC USA settore legale 8,58 $ (2025) – 9,87 $ (2026) (WordStream/LocaliQ via [Shopifreaks](https://www.shopifreaks.com/google-ads-cpcs-rose-to-5-42-in-2025-with-87-of-industries-seeing-increases-but-conversion-rates-climbed-to-8-18-as-automation-improves/) e [custom.legal](https://custom.legal/?p=22353)); CPC del termine "italian citizenship lawyer": **non trovato**.
- **Vincolo legale decisivo**: Codice deontologico forense, art. 37 c. 2: "L'avvocato non deve offrire o corrispondere a colleghi o a terzi provvigioni o altri compensi quale corrispettivo per la presentazione di un cliente" ([Simone](https://simoneconcorsi.it/accaparramento-della-clientela/); [Studio Cataldi](https://www.studiocataldi.it/articoli/37416-avvocati-accaparramento-di-clientela-offrire-prestazioni-non-richieste.asp)). Quindi gli studi legali italiani (Mazzeschi, Bersani, ICA nella parte legale) **non possono** comprare lead da noi; restano solo le agenzie non legali (My Italian Family, Smart Move Italy, agenzie brasiliane/argentine).

**Cosa costruiremmo**: sito EN "Am I still eligible after Law 74/2025?" con verifica in 5 domande (genitore/nonno nato in Italia, naturalizzazione, "minor issue", 1948), pagine per Paese (USA, Canada, Australia, UK) e modulo con due caselle (avvisi / "voglio essere contattato da [partner nominato]"). Il motore è quello di EsameB1.
**Ricavo prudente 12 mesi**: 0-1.500 € (ipotesi: 1 partner, 3-10 clienti riferiti in un anno, commissione 5-10 % su 4-8k €; traffico organico su SERP già dominata dai blog di ICA, MIF, Bersani). **Probabilità bassa-media**: domanda -70 %, SERP presidiata, un solo compratore pubblico.

### 2.2 Trasferirsi in Italia: visto residenza elettiva, 7 % pensionati, acquisto casa

**Domanda (Trends USA, 5 anni, medie annue):** "move to italy" 13,5 (2021) → 21,0 → 26,9 → 34,8 → 41,6 → **48,8 (2026)**, picco 3-9 novembre 2024. Autocomplete USA: "move to italy from usa", "move to italy as an american", "move to italy and get paid 2026", "retire to italy from usa / uk / canada / australia / ireland", "italy elective residence visa income requirements / 2026 / tax", "italy 7 flat tax regions map / pdf", "buying property in italy as an american / foreigner / dual citizen / us citizen / from uk / australian / canadian". Domanda alta, crescente e Tier 1.

**Chi paga:**
| Soggetto | Programma | Cifre | Fonte |
|---|---|---|---|
| **Smart Move Italy** | partner con link tracciato, commissione per iscrizione, graduata per servizio (visto/cittadinanza/immobili) | commissione **non pubblica**; pacchetti ERV **4.000 € single / 5.000 € coppia**, livello superiore 6.500/8.000 € | [partner page](https://smartmoveitaly.com/partner); [servizio ERV](https://smartmoveitaly.com/fullervservice) |
| Arletti & Partners, Why Wait Italy, Doing Italy/Expatsi, Professional Relo, Movingto (7 % flat tax) | nessun programma referral trovato | — | ricerche 10/10/2026 |
| Agenzie immobiliari / Gate-away / Idealista | nessun programma; Gate-away vende solo inserzioni | provvigione agenzia 3-8 % | [Gate-away](https://gate-away.com/advertise_with_us_en.php) |

**Vincolo immobiliare**: in Italia la provvigione di mediazione spetta solo agli iscritti al ruolo/abilitati (L. 39/1989, art. 6): un sito non abilitato non può incassare "finder's fee" su compravendite (da verificare con il professionista al primo incasso; il referral verso un consulente di relocation non è mediazione immobiliare).

**Cosa costruiremmo**: sito EN "Retire to Italy" con (a) elenco dei comuni ≤ 30.000 abitanti ammessi al 7 % (soglia alzata da 20.000 il 7/4/2026 secondo [Movingto](https://movingto.com/services/italy-7-percent-flat-tax); da verificare su Agenzia Entrate), (b) calcolatore "reddito minimo ERV", (c) checklist, (d) modulo con consenso separato verso Smart Move Italy (o altro partner con cifra scritta). Aggiornamento automatico degli elenchi comunali da ISTAT.
**Ricavo prudente 12 mesi**: 0-2.000 € (1-3 clienti riferiti × 4-8k € × commissione ipotetica 5-10 %). **Probabilità media**: la domanda cresce ogni anno e c'è un compratore pubblico, ma la commissione è ignota finché non si fa la candidatura (0 €, 48 ore di risposta dichiarate) e la SERP è piena (The Local, Italy Magazine, idealista, Wise, studi legali).

### 2.3 Scuole di italiano online (aggiornamento alla ricerca 8)

| Programma | Commissione | Cookie | Requisiti | Verifica |
|---|---|---|---|---|
| **ItalianPod101** | **25 % su ogni vendita, "for the lifetime of a customer"** (es.: abbonamento 180 $ → 45 $) | mai scade | blog/sito attivo su lingua o cultura italiana; PayPal | pagina ufficiale letta 10/10/2026: [FAQ](https://www.italianpod101.com/affiliate-program/affiliate-faq) |
| italki | ~10-15 $ per nuovo studente al primo acquisto | 30 gg | — | terzi ([copycatcafe](https://copycatcafe.com/blog/language-learning-affiliate-programs), [uppromote](https://uppromote.com/affiliate-programs/italki/)); pagina ufficiale 404 dal server → **non verificata** |
| Preply | 15 £ per nuovo cliente pagante (programma UK su Awin); altrove "fisso o % della prima lezione", non pubblicato | 30 gg | — | [Awin](https://ui.awin.com/merchant-profile/21098), [recensione 2026](https://copycatcafe.com/blog/preply-affiliate-program); **non verificata** |
| Babbel | fino a ~75-80 € per vendita (varia per piano) | 30-45 gg | — | terzi ([affninja](https://affninja.com/language-learning-affiliate-programs/)); **non verificata** |

Domanda: Trends USA "learn italian" 27,6 (2021) → **48,9 (2026)**, picco 22-28 marzo 2026; autocomplete "learn italian online free / free with certificate / free for beginners" (il pubblico cerca gratis). Resa attesa per 1.000 visite Tier 1 (ipotesi dichiarate: 1-2 % clic, 2-5 % conversione, 20-45 $ a vendita): **4-20 $**. Sui nostri siti attuali il pubblico EN (scioperi) non è "studente", quindi i volumi sono bassi: **100-500 €/anno**. Costo 0, lavoro 30 minuti, automatico. Nota: EsameB1 è in italiano per immigrati in Italia (B1 cittadinanza), pubblico diverso; qui vale la ricerca 8.

### 2.4 Affiliazione viaggi per Italy Strikes Today

**Domanda**: Trends USA "italy strikes" media 3,2 (2023) → 2,2 → 9,0 (2025) → **21,6 (2026)**, picco 1-7 marzo 2026 (letto dal server 10/10/2026). Autocomplete USA: "italy strikes september/october/july/august 2026", "italy train strike schedule 2026", "italy strike website". Il sito è online da ieri: traffico oggi zero; tutte le stime dipendono dal verdetto Search Console.

**Programmi (letti il 10/10/2026):**
| Programma | Commissione | Cookie | Dati utili | Accesso | Fonte |
|---|---|---|---|---|---|
| **Omio** (treni/bus alternativi) | 6 % del prezzo | 30 gg | **eCPC 0,07 $, carrello medio 81 $** | Travelpayouts, gratis, nessun traffico minimo | [Travelpayouts](https://www.travelpayouts.com/en/offers/omio-affiliate-program) |
| **Welcome Pickups** (transfer) | 8 % transfer, 9 % sightseeing (Travelpayouts); "fixed-rate" sul sito ufficiale; 5 € a transfer (Affilimate) | 45 gg | **eCPC 0,03 $, carrello 100 $** | Travelpayouts / Tapfiliate | [Travelpayouts](https://www.travelpayouts.com/en/offers/welcome-pickups-partner-program); [Affilimate](https://affilimate.io/programs/welcome-pickups-affiliate-program/) |
| GetYourGuide | 8 % | 31 gg | eCPC 0,02 $, carrello 140 $ | Travelpayouts | [Travelpayouts](https://www.travelpayouts.com/en/offers/getyourguide-affiliate-program) |
| **SafetyWing** (assicurazione) | "flat affiliate fee… approximately **10 % of total premium**" | 30 gg (handbook) vs 364 gg (directory): **contrasto** | — | iscrizione diretta | [pagina ufficiale Ambassador](https://safetywing.com/ambassador); [help](https://intercom.help/safetywing/en/articles/9796053-the-ambassador-program) |
| **Airalo** (eSIM) | **10 % standard** | 30 gg | — | Impact, con revisione | [FAQ ufficiale](https://www.airalo.com/blog/airalo-affiliate-program-faqs) |
| EKTA (assicurazione) | 20 % | — | prezzo medio 18 $ | Travelpayouts | [Travelpayouts](https://www.travelpayouts.com/en/offers/ekta-affiliate-program) |
| Heymondo | "attractive commissions", **cifra non pubblica** | 30 gg | — | diretta | [pagina ufficiale](https://heymondo.com/affiliate-program) |
| DiscoverCars (auto) | 70 % del margine DC + 30 % Full Coverage (non del prezzo) | 365 gg | minimo pagamento 100-200 $ | diretta; pagina ufficiale 404 dal server | [uppromote](https://uppromote.com/affiliate-directory/discover-cars/) – **non verificata** |
| Trainline | "based on Partnerize network rates" – **cifra non pubblica** (terzi: 3 %/1 % o "fino al 20 %", in contrasto) | 30 gg | — | Partnerize, revisione | [pagina ufficiale](https://www.thetrainline.com/about-us/partnerships/affiliates) |
| Booking.com | quota della commissione Booking (≈4 % del prenotato; fino a ~40 % della commissione a volumi alti) | sessione/30 gg (contrasto) | **giugno 2025: Booking ha chiuso gli affiliati sotto ~1.000 €/mese** | CJ/Awin | [pagina ufficiale](https://www.booking.com/affiliate-program/v2/index.html); [world-travellers](https://world-travellers.com/travel-news/booking-com-affiliate-stops-stay22-travelpayouts/) |
| World Nomads | pagina 404 dal server | — | — | — | **non verificato** |

**Guadagno atteso per 1.000 visite Tier 1** (calcolo dichiarato: 3-6 % dei visitatori clicca un link affiliato; eCPC pubblici 0,02-0,07 $): **1,5-5 $ da affiliazione** (Omio è il più adatto: chi trova lo sciopero cerca un treno/bus alternativo). AdSense travel con traffico USA: RPM 5-12 $ a 10-15k sessioni/mese (fonti blog, [lovable](https://lovable.dev/hi/guides/how-to-make-money-as-travel-blogger)). Totale **≈ 7-17 $ per 1.000 visite**. Con 5.000 visite/mese al mese 12 (ipotesi del rapporto 7): **35-85 $/mese → 100-600 €/anno** solo da affiliazione.
**Compatibilità con AdSense**: i link affiliati testuali sono ammessi sulla stessa pagina se non sono annunci contestuali e non imitano gli annunci Google (policy citata in [WebmasterWorld](https://www.webmasterworld.com/forum89/8493.htm); la [policy ufficiale](https://support.google.com/adsense/answer/48182?hl=en) non li vieta). Serve la dicitura "link di affiliazione/pubblicità" (Codice del consumo e linee guida AGCM sulla pubblicità occulta).
**Probabilità alta** che renda, **bassa** che superi i 1.000 €/anno nei primi 12 mesi. Lavoro di Massimiliano: iscrizioni a suo nome (Travelpayouts, SafetyWing, Airalo/Impact) ≈ 1 ora. Automatico al 100 %.

### 2.5 Google Ads per i servizi fotografici di Massimiliano (NON automatico)

- **CPC Italia per "fotografo headshot [città]"**: **non trovato**. Benchmark: Italia CPC medio 0,50-3,00 € ([Andava](https://www.andava.com/learn/italy-digital-marketing-statistics/), senza fonte); settore più caro in Italia 1,76 $ (Semrush/Statista, maggio 2023); fotografia (Paese non indicato) CPC 4-18 $, costo per richiesta 25-85 $, chiusura 15-35 % con matrimoni in basso ([Adwave](https://adwave.com/resources/photography-advertising)); Arts & Entertainment USA 2025: conversione 3,3-4,8 %, costo per lead 20-30 $ ([TheeDigital](https://www.theedigital.com/blog/2025-google-ads-benchmarks)). Caso autodichiarato: servizi fotografici per stranieri in Italia 15 $/lead, 50 % chiusura, 30 $/cliente ([Freelancehunt](https://freelancehunt.com/en/showcase/work/roas-1500-cpl-15/1836341.html)).
- **Domanda in italiano (autocomplete IT, 10/10/2026)**: "fotografo headshot" → **nessun suggerimento**; "fotografo ritratti professionali" → nessuno; "fotografo linkedin" → "milano", "per linkedin"; "fotografo ecommerce" → "milano", "roma"; "fotografo matrimonio" → "prezzi", "vicino a me", "roma", "torino", "milano", "palermo", "lecce", "catania", "economico". Il termine "headshot" non esiste nel pubblico italiano: si cerca "foto profilo linkedin", "foto curriculum".
- **Valore cliente**: matrimonio **2.236 € medi** (pacchetto 10 ore, 600-1.000 file; sondaggio di 61 fotografi italiani 2025, [Fearless](https://www.fearlessphotographers.com/blog/353/2025-italy-prices)), maggioranza 1.500-2.500 €; ritratto professionale in Italia: **non trovato** (USA 150-350 $/persona, [BetterPic](https://www.betterpic.io/blog/company-headshot-photographer-pricing-2026); Milano su Airbnb 59-155 $/persona); e-commerce: non trovato.
- **Scenario con 1.000-3.000 € (tutte ipotesi da sostituire con il Keyword Planner, gratuito, 15 minuti)**: CPC 1-2 € → 500-3.000 clic; conversione 3-5 % → 15-150 richieste; chiusura 20 % → 3-30 clienti. Ritratti a 100-150 € → 300-4.500 € lordi (in pareggio o in perdita); matrimoni: **basta 1 incarico ogni 1.000 € di annunci per andare in pari**, 2-3 per guadagnare; stagionalità (le coppie prenotano 6-12 mesi prima). E-commerce: clienti ricorrenti, ma domanda piccola fuori Milano/Roma.
- **Verdetto**: test da **300 €** solo su "fotografo matrimonio [città] prezzi" con pagina prezzi chiara, soglia: ≤ 40 € per richiesta e ≥ 1 incarico firmato entro 60 giorni; niente annunci su "headshot" (domanda zero). Probabilità media; **ore di Massimiliano alte** (è il suo lavoro: ogni cliente = un servizio). Vantaggio: è già coperto dalla P.IVA 74.20.19, nessun nodo fiscale.

### 2.6 Amazon Ads sul catalogo KDP

- **Stato del catalogo: non trovato in questo repo** (`find` su kdp/amazon: solo `schede-amazon/PIANO.md`, business scartato; la skill `kdp-book-pipeline` rimanda a `claude/libro-kdp-stato.md`, `ricerca-nicchie-ottobre.md`, `manuale-produzione.md`, non presenti qui). Senza numero di titoli, BSR, prezzi e royalty non si può stimare nulla di serio.
- Regole già scritte nella skill (sezione 6): break-even ACOS = royalty/prezzo; campagna automatica, bid 0,60-0,80 $, nessuna modifica per 2 settimane, **stop a 20-25 clic senza vendita**; "nicchia debole: abbassa il budget, non il bid".
- Benchmark esterni: break-even paperback 9,99 £ ≈ 26 %; ebook al 70 % ≈ 70 % ([Vappingo](https://www.vappingo.com/word-blog/acos-amazon-ads-books/)); low-content: ACOS 50-150 % (Written Word Media 2023 citato da [The Write Moves](https://the-write-moves.beehiiv.com/p/amazon-ads-for-low-content-worth-the-spend-or-a-money-pit), di seconda mano), CPC massimo in pareggio ≈ 0,21 £ contro bid suggeriti 0,35-0,60 £ ([Vappingo low content](https://www.vappingo.com/word-blog/?p=11830)); sondaggio WWM 2025: 44 % degli autori ≤ 100 $/mese ([Vappingo](https://www.vappingo.com/word-blog/how-much-do-kdp-authors-earn/)).
- REGOLE-FISSE (9/10): la strada KDP è "senza Amazon Ads". **Verdetto**: non è lead-gen e non è Tier-1 specifico; si riapre solo con i dati del catalogo e un test da 100 € su 1-2 titoli con BSR competitor < 20.000; probabilità bassa-media.

### 2.7 Destination wedding in Italia (Massimiliano come fotografo per coppie estere)

- **Mercato**: Osservatorio Destination Wedding in Italy (Italy for Weddings/Convention Bureau Italia + Centro Studi Turistici): **16.700 matrimoni di coppie straniere nel 2025 (+9,8 %), 1,1 mld € (+19,6 %), 67.000 € a evento, 3 mln pernottamenti; USA 31,7 % delle richieste, poi UK e Germania; regioni: Toscana, Lombardia, Campania, Piemonte, Sicilia** ([QuiFinanza](https://quifinanza.it/lifestyle/travel-economy/matrimoni-stranieri-italia-2025/959327/); [9colonne](https://www.9colonne.it/593950/more-and-more-foreign-couples-choose-to-marry-in-italy-16-700-last-year)).
- **Prezzi fotografo**: media 2.236 € (Fearless, 61 fotografi, 2025); guide di settore 1.500-10.000 €, Toscana full-service 5-15k € ([Emiliano Russo](https://www.emilianorusso.com/wedding-photographer-cost-in-italy/), fonte interessata); Venezia 2-7k, Como 3-8k.
- **Concorrenza**: ~5.002 attività di fotografia matrimoniale in Italia (luglio 2026, [poidata](https://poidata.io/report/wedding-photographer/italy), metodo non dichiarato); directory: Fearless (a quota), Wezoree, planning.wedding 19 $/mese; i planner si aspettano **~10 % di commissione dal fotografo** ([La Lista](https://www.lalista.com/articles/italian-wedding-commission)): il flusso di denaro va dal fotografo al planner, non il contrario → **nessuna prova che planner o fotografi paghino lead a terzi**.
- **Domanda**: autocomplete USA "italy wedding photographer cost / price / reddit", "tuscany / rome / florence italy wedding photographer", "destination wedding italy cost / packages / lake como / amalfi coast / tuscany". Trends USA "italian wedding photographer": troppo basso per essere misurato (0-2).
- **Canali**: Instagram/Pinterest (foto), directory, planner (commissione 10 %), Google Ads in inglese sulla sua regione (CPC non trovato). **Dipende dalla sua città**: fuori da Toscana, laghi, costiera, Roma, Puglia, Sicilia la domanda estera è minima.
- **Verdetto**: è l'unica idea ad alto ticket (2-5k € a incarico, in parte già fattibile con la P.IVA attuale) ma è lavoro di Massimiliano, non automatico; probabilità media se la sede è in una zona wedding; 1-2 incarichi/anno = 3-8k €. Da trattare come "lavoro da fotografo venduto all'estero", non come business automatico.

### 2.8 Vincoli comuni (privacy, fiscale)
- **Consenso**: modulo con due caselle separate, non pre-spuntate, destinatario nominato (Garante 2013 § 2.6.3, già in ricerca 8). Per gli affiliati non serve consenso (nessun dato passa), serve la dicitura "link di affiliazione".
- **Niente email a freddo** verso agenzie/studi: la candidatura ai programmi partner è un modulo loro (inbound), ammesso.
- **Avvocati**: art. 37 CDF vieta loro di pagare provvigioni: non proporre mai "lead a pagamento" a uno studio legale.
- **Immobili**: provvigione solo ad agenti abilitati (L. 39/1989).
- **Fiscale**: commissioni di affiliazione e cessione di lead sono attività commerciale (intermediazione/pubblicità, es. 73.11.02), diversa da 74.20.19: al primo incasso serve il codice ATECO aggiuntivo e probabilmente CCIAA + Gestione commercianti (stesso nodo delle ricerche precedenti; ammesso dalla regola 2 allentata il 9/10). I servizi fotografici (5 e 7) non hanno questo nodo.

---

## 3. Le due migliori: piano in 5 passi e soglie di stop

### A. Affiliazione viaggi su Italy Strikes Today (0 €, automatica)
1. **Massimiliano (1 h)**: iscrizione a Travelpayouts (Omio, Welcome Pickups, GetYourGuide, EKTA), SafetyWing Ambassador, Airalo via Impact; invia a Claude gli ID affiliato. Niente Booking (rischio chiusura sotto 1.000 €/mese) e niente DiscoverCars finché non c'è traffico (minimo di pagamento 100-200 $).
2. **Claude (1 giorno)**: box "Lo sciopero ti blocca? Alternative" su ogni pagina di sciopero: treno/bus alternativo (Omio), transfer aeroporto (Welcome Pickups), auto (dopo), eSIM (Airalo), assicurazione (SafetyWing/EKTA); dicitura "link di affiliazione"; nessun link in alto sopra i contenuti (AdSense).
3. **Claude**: tracciamento clic (Netlify/GA4 senza cookie) e report mensile con il resto della routine del lunedì.
4. **Mese 3 (dopo il verdetto Search Console)**: se le visite Tier 1 superano 2.000/mese, aggiungere pagine "come arrivare da X a Y durante lo sciopero" (Omio) e "aeroporto → centro" (Welcome Pickups).
5. **Mese 6**: revisione; al primo pagamento ricevuto si apre il nodo fiscale con il professionista.
**Soglie**: continua se al mese 6 ≥ 2 % dei visitatori clicca un link e ≥ 1 commissione maturata; **stop** (togli i box, resta AdSense) se a 6 mesi i clic sono < 1 % o le commissioni = 0 con ≥ 5.000 visite cumulate. Nessuna spesa prevista: non serve un sì su cifre.

### B. Satellite EN "Retire / Move to Italy" con partner di relocation (0 €, automatico dopo l'accordo)
1. **Massimiliano (30 min)**: compila il modulo partner di Smart Move Italy (risposta dichiarata in 48 h); chiede per iscritto: percentuale/importo per servizio, durata del tracciamento, quando si paga. **Se la commissione è < 150 € per cliente ERV o non è scritta → stop prima di costruire.**
2. **Claude (7-10 giorni, motore EsameB1)**: sito EN con elenco comuni ≤ 30.000 abitanti ammessi al 7 % (ISTAT, aggiornamento automatico), requisiti ERV per Paese (USA/UK/CA/AU), calcolatore reddito, pagine "retire to italy from [Paese]"; modulo "Avvisami" + casella separata "voglio essere contattato da Smart Move Italy" con link tracciato.
3. **Claude**: indicizzazione, Search Console, routine settimanale come gli altri siti.
4. **Mese 2-3**: se Search Console mostra impression Tier 1 > 5.000/mese, test annunci **tetto 100 €** (sì esplicito di Massimiliano) su "italy elective residence visa requirements", "italy 7% flat tax towns", solo verso la pagina con il modulo; soglia: costo per lead qualificato ≤ 1/5 della commissione scritta.
5. **Mese 6**: con ≥ 1 cliente pagato, secondo partner (cittadinanza: My Italian Family o altra agenzia non legale) con lo stesso modulo; altrimenti il sito resta informativo con AdSense + affiliati lingua (ItalianPod101 25 %).
**Soglie**: continua se al mese 6 ≥ 10 lead qualificati/mese e ≥ 1 commissione pagata; **stop** se a 6 mesi lead < 3/mese o nessun pagamento dal partner entro 90 giorni dal primo lead.

### 3 bis. Terza via, non automatica: Massimiliano fotografo per destination wedding
Solo se la sua città è in una zona wedding (Toscana, laghi, Roma, costiera, Puglia, Sicilia): pagina EN con portfolio e prezzi (2.000-3.500 €, in linea con la media 2.236 €), scheda su Wezoree/planning.wedding (19 $/mese), Pinterest con 50 pin (Claude li prepara), test Ads EN da 300 € su "[regione] wedding photographer"; soglia: ≥ 3 richieste qualificate e 1 contratto entro 90 giorni. Lavoro suo: servizi, trasferte, chiamate.

---

## 4. Cosa NON fare
- **Non proporre lead a pagamento a studi legali** (art. 37 CDF: non possono pagare provvigioni); non comprare né vendere liste di contatti; niente email a freddo ad agenzie o scuole.
- **Non spendere in annunci sulla cittadinanza per discendenza** prima di un accordo scritto con una cifra: domanda -70 % dal picco, SERP già occupata, compratori in gran parte avvocati.
- **Non fare di Booking.com il programma principale** (chiusura degli affiliati piccoli nel 2025) né iscriversi a DiscoverCars prima di avere traffico (minimo di pagamento 100-200 $).
- **Non pagare directory wedding o Ads su "fotografo headshot"** (domanda italiana zero) e non lanciare Amazon Ads senza i dati del catalogo (non presenti in questo repo) e senza il sì sul test da 100 €.
- **Non promettere "finder's fee" immobiliari** (riservate agli agenti abilitati) e non raccogliere telefoni nei moduli nella fase di test.
- **Non contare su cifre non verificate**: italki, Preply, Babbel, DiscoverCars, Trainline, Heymondo e Booking hanno commissioni non pubbliche o in contrasto tra le fonti; la cifra vera si legge solo nella dashboard dopo l'iscrizione.
