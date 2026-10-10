# Comprare traffico per i tre siti: si può? A che prezzo? (studio del 10/10/2026)

Scritto da Claude su richiesta di Massimiliano. Domanda: *l'unico modo per far crescere un sito informativo senza aspettare Google è comprare visite a meno di quanto rendono. È possibile oggi per Italy Strikes Today, EsameB1 ed EsamiDiStato?*

**Risposta breve: no, non con la pubblicità e l'affiliazione che abbiamo. Una visita comprata su un pubblico USA/UK costa 0,10–2 $; la stessa visita rende 0,01–0,025 $. Il rapporto ricavo/costo è 0,01–0,2, non 1,3. L'unica eccezione documentata (un blogger, 127 $ → 593 $, aprile 2024) richiede RPM ≥ 30 $ e contenuti "virali" con CTR ≥ 5 %: non è il nostro caso. In Italia regge solo la lead-gen per scuole, già studiata (studio 8), e anche lì con margine stretto.**

Metodo: fonti ufficiali lette con `curl` (WebFetch bloccato sui domini Google/Mediavine), ricerca web (~45 query), file scaricati in `scratchpad/ads/raw/`. Nessun accesso a Google Keyword Planner, Semrush o Ahrefs: dove manca un numero lo dico ("non trovato"). Tutte le cifre sono in dollari salvo dove scritto in euro.

---

## 1. Le regole: chi permette il traffico comprato e chi no

| Chi | Cosa dice (testuale) | Fonte, data | Per noi |
|---|---|---|---|
| **Google AdSense** | "You're welcome to promote your site in any manner that complies with our program policies. However, AdSense publishers are ultimately responsible for the traffic to their ads." Consiglia un canale AdSense dedicato ("Google Ads") per misurare il traffico comprato. Vietati: paid-to-click, autosurf, scambi di clic, email non richieste, pop-up, software. Il sito che riceve traffico da annunci deve rispettare "the spirit of Google's Landing Page Quality Guidelines". | [AdSense, "If you want to purchase traffic to your site"](https://support.google.com/adsense/answer/1348722) e [Program policies, "Traffic sources"](https://support.google.com/adsense/answer/48182), lette il 10/10/2026 | **Permesso** comprare visite da Google Ads, Meta, Pinterest, Reddit, Microsoft. Vietato comprare clic o traffico "a pacchetti". |
| **Google Ads (lato inserzionista)** | Disapprovazione per "Insufficient original content": "Destination content that is designed for the primary purpose of showing ads. Examples: Driving traffic through 'arbitrage' or other methods to destinations with more ads than original content, little or no original content, or excessive advertising." Avviso 7 giorni prima di una sospensione. | [Google Ads policy, "Insufficient original content"](https://support.google.com/adspolicy/answer/16427718), 10/10/2026 | Le nostre pagine hanno dati reali (registro MIT) e pochi spazi pubblicitari: non sono "arbitrage destinations". Ma mai mandare annunci a pagine con più pubblicità che testo. |
| **Mediavine Journey** | Requisiti: "minimum of 1,000 sessions from Tier 1 countries (U.S., Canada, U.K., Australia) within a 30-day period"; "clean, human, brand-safe traffic — real visitors, not bots, incentivized clicks, or traffic from sources that put advertisers at risk". Valuta anche "Traffic sources" e "Traffic countries of origin" (GA4). Nessuna frase esplicita sul traffico a pagamento. | [mediavine.com/mediavine-requirements](https://www.mediavine.com/mediavine-requirements/) e [help: What does it take to get approved](https://help.mediavine.com/what-does-it-take-to-get-approved-by-mediavine), 10/10/2026 | Non vietato, ma le fonti di traffico vengono guardate: un sito con metà visite da annunci rischia il rifiuto. Journey paga il 70 % (fonte terza, [productiveblogging](https://www.productiveblogging.com/?p=15446)). |
| **Raptive** | "Examples of traffic that would violate our policies include: Fraudulent traffic; Suspicious traffic sources; Non-human traffic; **Traffic purchased with the intent of making more money from advertising**." Soglia 25.000 pagine/mese (dal 16/10/2025) con ≥ 50 % da US/UK/CA/AU/NZ. | [Raptive Content and Traffic Policies](https://help.raptive.com/hc/en-us/articles/29872333292443-Raptive-Content-and-Traffic-Policies) (letta via API Zendesk il 10/10/2026); [ppc.land 19/10/2025](https://ppc.land/raptive-drops-pageview-requirement-to-25-000-monthly-visits/) | **Vietato per iscritto** proprio l'arbitraggio. Chi compra traffico per guadagnare con gli annunci non entra in Raptive. |
| **Ezoic** | Nessuna policy pubblica trovata. Nel forum ufficiale lo staff dice: per le promozioni a pagamento "reach out to us before experimenting with paid traffic"; chiedono accesso in sola lettura a GA e al conto AdSense. | [community.ezoic.com/d/8156](https://community.ezoic.com/d/8156/2) (riassunto da ricerca; la pagina risponde 404 al nostro server) | Avvisare prima. |
| **SafetyWing (Ambassador)** | "We don't allow paid advertising of our products and ask that you only use the promotional materials we provide for you." | [SafetyWing help, "The Ambassador Program"](https://intercom.help/safetywing/en/articles/9796053-the-ambassador-program), aggiornata 5/3/2026 | **Vietato** fare annunci per l'assicurazione. Annunci per il nostro sito che contiene il link: zona grigia → chiedere per iscritto prima del test, oppure togliere il riquadro SafetyWing dalla pagina usata per il test. |
| **Airalo (via Impact)** | "Use any type of bidding on Airalo trademark terms through keyword bidding and other paid search on Google, Bing, Yahoo, MSN… includes 'Airalo' and/or any misspellings… separately or together with other keywords" (3.2.8); vietati i marchi nei testi degli annunci (3.2.9); violazione = rimozione e storno delle commissioni (3.2.16). Commissione standard 10 %, "rates may vary depending on promotional method". | Termini riprodotti su [MCANISM](https://campaigns.mcanism.com/airalo-the-worlds-first-esim-store); [Airalo affiliate FAQ](https://www.airalo.com/blog/airalo-affiliate-program-faqs), 10/10/2026 | Niente parola "Airalo" (né "eSIM Airalo") nelle parole chiave o negli annunci. Annunci per il nostro sito: permessi. |
| **Travelpayouts / Omio** | "It is forbidden to direct ads to the Omio website, but you can advertise your website with Omio widgets instead." "Most companies forbid brand contextual advertising." Viator e AirHelp vietano del tutto Google Ads. Il "brand bidding" è tra le prime cause di blocco dei pagamenti. | [Travelpayouts, "Promote an affiliate offer with Google Ads"](https://www.travelpayouts.com/blog/promote-offer-with-google-ads/) (3/1/2022); [Travelpayouts rules](https://www.travelpayouts.com/blog/travelpayouts-rules/) | Annunci solo verso le nostre pagine; mai "Omio", "Italo", "Trenitalia" come parole chiave di marca. |

**Conclusione sulle regole**: comprare visite per il nostro sito è lecito con AdSense, Journey (con cautela), Omio e Airalo (senza marchi); è **vietato** con Raptive (l'obiettivo "più soldi dagli annunci" è proprio quello scritto nella policy) e per i prodotti SafetyWing. Nessuna "quota minima di traffico organico" scritta da nessuno: Mediavine e Raptive guardano le fonti in GA4 e decidono caso per caso.

## 2. Quanto costa una visita dai Paesi ricchi (USA/UK/CA/AU)

Nessuna stima pubblica per le nostre parole esatte ("italy strike today", "italy train strike", "italy strikes november 2026", "italy travel insurance", "codice fiscale calculator", "ztl fine italy"): **non trovate** (Semrush/Ahrefs non espongono pagine per queste query; Keyword Planner richiede l'account Google Ads). Uso i benchmark di settore.

| Canale | CPC (costo per clic) | Fonte, periodo | Costo per 1.000 visite |
|---|---|---|---|
| **Google Search** (USA) | Viaggi **2,14 $**; Finanza e assicurazioni 3,39 $; Istruzione 4,81 $; media tutti i settori 5,42 $ | [LocaliQ/WordStream, Search Advertising Benchmarks](https://localiq.com/blog/search-advertising-benchmarks/), aggiornato 1/6/2026 | **2.100–3.400 $** |
| **Microsoft Ads (Bing)** | ~30–40 % meno di Google: media 1,54 $ (tutti i settori, 2025); 1,20–1,35 € (2026); viaggi "tra i più economici" ma senza cifra | [shno.co](https://www.shno.co/marketing-statistics/bing-ads-statistics); [trackbee 21/9/2026](https://www.trackbee.io/blog/microsoft-ads-cost) | **1.300–1.500 $** |
| **Google Demand Gen** (ex Discovery) | 2,00–2,75 $ al primo lancio; 0,40–1,20 $ ottimizzato; 2,41 $ mediana B2B | [Affect Group](https://affectgroup.com/blog/demand-gen-benchmarks-ctr-and-cpc-planning-ranges/); [Starr Conspiracy, ago 2025](https://www.thestarrconspiracy.com/insights/benchmarks/google-demand-gen-vs-performance-max-benchmarks-2025) | **400–2.750 $** |
| **Facebook/Instagram** | Ricreazione e viaggi: mediana **0,55 $** mondo (lug 2025–lug 2026), **0,69 $ USA** (dic 2024–dic 2025), su 3 Mld $ di spesa analizzata; viaggi campagne traffico 0,51 $ (WordStream 2025) | [Superads, Recreation & Travel](https://www.superads.ai/facebook-ads-costs/cpc-cost-per-click/recreation-and-travel) e [USA](https://www.superads.ai/facebook-ads-costs/cpc-cost-per-click/recreation-and-travel/united-states) | **500–700 $** (viaggi USA); 50–150 $ solo con post "virali" (CTR ≥ 5 %) |
| **Pinterest** | 0,05–0,10 $ dichiarato dal venditore Tailwind; 0,10–1,50 $ campagne traffico; 0,21–2,00 $ (WebFX) | [Tailwind, 10/6/2025](https://www.tailwindapp.com/blog/how-much-does-pinterest-advertising-cost); [cropink/WebFX](https://cropink.com/pinterest-ads-cost) | **100–1.500 $**, realistico 200–500 $ |
| **Reddit** | Consumer/viaggi **0,10–0,50 $**; CPM 1–4 $; minimo 5 $/giorno | [Dataslayer, 12/12/2025](https://www.dataslayer.ai/blog/reddit-ads-in-2025-complete-guide-for-marketers); Affect Group dice invece 2–4 $ (clienti propri) | **100–500 $** |
| Arbitraggio "classico" (dati di chi lo fa) | Traffico Facebook USA 0,50–0,80 $/clic; UK 0,35–0,60; Canada 0,35–0,55; Australia 0,40–0,70 | [arbhunter, 27/1/2026](https://arbhunter.dev/blog/best-countries-ad-arbitrage-2026) (sito di settore, fonti citate: Vaizle, WordStream, Lebesgue) | 350–800 $ |

**Costo realistico per visita Tier 1: 0,10–0,50 $ sui social, 1,3–3,4 $ sulla ricerca.** Sotto 0,05 $ si va solo con contenuti che la gente condivide da sola (CTR altissimo) o con Paesi Tier 3 (India 0,10–0,20 $, Filippine 0,15–0,25 $), che però pagano RPM 1–6 $ (arbhunter).

## 3. Quanto rende una visita sulle nostre pagine

### 3.1 Pubblicità (RPM = ricavo per 1.000 pagine viste)

| Caso | RPM | Fonte |
|---|---|---|
| Blog viaggi su Copenhagen, Journey, **primo mese** (7/1–7/2/2025): 13.866 sessioni, 104 $ | **7,50 $**; 1,61 $ il primo giorno, 11,57 $ a fine mese; **12,69 $ medio sui primi 90 giorni** (717 $) | [danny-cph.com](https://danny-cph.com/?p=6835), agg. 5/1/2026 |
| Blog viaggi, Journey, primo mese con 45k sessioni (20 % USA) | 430 $ → ~9,5 $; poi Mediavine pieno **18 $** a gennaio con 25 % USA | [Sunshine Seeker](https://www.sunshineseeker.com/blogging/travel-blog-mediavine/), agg. 4/12/2025 |
| Benchmark 2026 "Lifestyle, Food, Travel" con traffico USA | Page RPM **8–18 $** (Q4 ed estate sopra la media) | [weforads](https://weforads.com/blog/ad-revenue-benchmarks-2026/) (venditore di servizi) |
| AdSense (non Journey) viaggi | 5–15 $ (stime di venditori, nessun dato primario) | [stay22 community](https://community.stay22.com/best-advertising-solutions-for-travel-sites); [aditude](https://www.aditude.com/blog/rpm-for-publishers) 2–8 $ |
| Italia (traffico italiano) | Mediavine **5,77 $** (un solo sito viaggi/outdoor, set 2023–feb 2024, r/juststart); stima interna 3–6 € (studio 7) | [r/juststart "RPM/CPM by country"](https://www.reddit.com/r/juststart/comments/1b0kkow/rpm_cpm_by_country) (riassunto da ricerca; Reddit blocca il nostro server) |

**Regola prudente**: scioperi in inglese con AdSense **6–10 $**, con Journey **8–15 $** (Q1 più basso, Q4 più alto). Siti italiani **3–6 €**.

### 3.2 Affiliazione (per 1.000 visite su una pagina con il riquadro "Stuck by a strike?")

| Partner | Dati certi | Ipotesi (nostre, da misurare) | Ricavo per 1.000 visite |
|---|---|---|---|
| **Omio** (Travelpayouts) | **eCPC 0,07 $**, commissione 6 %, prezzo medio **81 $** (→ 4,9 $ a prenotazione), cookie 30 giorni | 30–50 clic ogni 1.000 visite (riquadro in evidenza su pagine "oggi/domani") | **2–3,5 $** |
| **SafetyWing** | Essential **62,72 $ / 4 settimane** (18–39 anni, [prezzi ufficiali](https://safetywing.com/nomad-insurance/pricing), 10/10/2026); commissione 10 % → **6,27 $ a vendita**, ricorrente ai rinnovi; EPC pubblico: **non trovato** | 20–40 clic, conversione 1–2 % → 0,2–0,8 vendite | **1,3–5 $** (ma niente annunci a pagamento: vedi §1) |
| **Airalo** (Impact) | 10 % standard; valore medio ordine ed EPC: **non trovati** (FlexOffers riporta 8 % e cifre illeggibili) | ordine 10–30 $ → 1–3 $ a vendita; 30 clic, conversione 2–3 % | **1–3 $** |
| Welcome Pickups, EKTA | nessun dato pubblico | — | 0–2 $ |
| **Totale affiliazione** | | | **4–12 $**, prudente **5 $** |

### 3.3 Ricavo totale per 1.000 visite e confronto con il costo

| Pagina | Pubblicità | Affiliazione | **Ricavo / 1.000 visite** | Costo / 1.000 visite (canale più economico realistico) | **Rapporto ricavo/costo** (serve ≥ 1,3) |
|---|---|---|---|---|---|
| Scioperi EN, pagine "today/tomorrow", AdSense | 6–10 $ | 5 $ | **11–15 $** | Reddit/Pinterest 100–500 $; Facebook 500–700 $; Google 2.100 $ | **0,02–0,15** |
| Scioperi EN, stessa pagina con Journey | 8–15 $ | 5 $ | **13–20 $** | idem | **0,03–0,2** |
| Pagina "money" nuova (rimborsi + assicurazione + eSIM), Journey | 8–15 $ | 8–12 $ | **16–27 $** | idem | **0,03–0,27** |
| Scioperi IT (sezione `/it/`), AdSense | 3–6 € | 0 | **3–6 €** | Facebook Italia 200–400 €; Google IT 500–1.500 € | **0,005–0,03** |
| EsameB1 / EsamiDiStato, AdSense | 3–6 € | corsi 0–3 € | **3–9 €** | Google IT ("codice fiscale" 0,57 $, Semrush; istruzione USA 4,81 $) 500–1.500 € | **0,002–0,02** |
| EsameB1 con **lead-gen** (studio 8) | — | 10–20 €/lead | vedi §5 | Google IT 0,5–1,5 €/clic | **0,5–2** (solo con accordi firmati e CPC ≤ 0,5 €) |

**Per avere rapporto 1,3 con 15–20 $ di ricavo ogni 1.000 visite, la visita deve costare ≤ 0,012–0,015 $.** Nessun canale pubblico a pubblico USA/UK arriva lì. Il buco non è del 30 %: è di **10–50 volte**.

### 3.4 I casi documentati

- **Caso positivo (unico trovato)**: Hasib Alic, aprile 2024: 127 $ di annunci Facebook per spingere un articolo → 593 $ su Mediavine in 7 giorni (ROI dichiarato 360 %; sito e articolo non rivelati; cifra lorda, da un tweet). Le sue condizioni: **RPM ≥ 30 $** sull'articolo, **CTR ≥ 5 %** sul post, budget 10 $/giorno, aumento max 50 %/giorno. Ricostruzione: 593 $ / 30 $ RPM ≈ 20.000 sessioni per 127 $ = **0,006 $ a visita**, possibile solo con contenuti che la gente clicca e condivide da sola. [partnerkin, 25/9/2024](https://partnerkin.com/en/blog/case_study/%24466-in-7-days-facebook); [ebizfacts](https://ebizfacts.beehiiv.com/p/ebiz-insider-newsletter-369).
- **Chi lo fa di mestiere** (BlackHatWorld, set 2025): "ancora possibile ma più difficile: CPM più alti, policy più strette, margini sottili"; un utente: "CPC per i Paesi Tier 1 troppo alto per andare in pari con AdSense" ([thread](https://www.blackhatworld.com/seo/is-google-adsense-arbitrage-still-working.1751283/), riassunto da ricerca; il forum blocca il nostro server). Margini attesi nel "search arbitrage" professionale: 10–25 % ([creatify](https://creatify.ai/es/blog/search-arbitrage-a-strategic-gamble-for-passive-income)), con team e decine di migliaia di dollari al mese.
- **Chi vende strumenti** (MonetizeMore, 1/5/2025; Publift, 8/10/2026): "legale e permesso da Google", ma il loro esempio è "AdSense paga 0,50 $ a clic, basta pagare meno il traffico": confondono clic sugli annunci con visite (su 1.000 visite i clic sugli annunci sono 5–20). Nessun numero reale.
- **Ezoic (blog ufficiale, 2018)**: "What if I spend $100 on ads for that content, but the visits only generate $45? I would have lost $55"; ha senso solo se i visitatori tornano (newsletter). [ezoic.com/blog/buying-website-traffic](https://www.ezoic.com/blog/buying-website-traffic).
- **Reddit r/juststart, r/PPC, Niche Pursuits, Authority Hacker**: nessun caso con numeri reali "CPC pagato vs RPM ottenuto" in nicchia viaggi trovato (Reddit non è raggiungibile dal nostro server; le ricerche su Niche Pursuits/Authority Hacker non danno pagine sul tema). Un'agenzia riporta per un'assicurazione viaggi canadese CPC medio **4,48 $** e ROAS 4,7 (ago–set 2023, vende la polizza, non è affiliazione) ([freelancehunt](https://freelancehunt.com/en/showcase/work/lead-generation-for-insurance-service-using/1939839.html)).

## 4. Pagine "money": servono? Quali?

Sì, ma per il traffico **gratuito** (Google, link interni, email), non per quello comprato. Oggi il sito ha 7 guide (`refunds-and-your-rights`, `guaranteed-trains`, `flights-during-strikes`, `how-strikes-work-in-italy`, …) e il riquadro affiliati su home, oggi/domani, mesi, settori, città, aeroporti. Le pagine con intento d'acquisto da aggiungere (2–3 ore l'una, stesso motore):

1. **"My train in Italy is cancelled by a strike: what to do now"** (passo-passo: treni garantiti → rimborso Trenitalia/Italo → alternativa Omio/FlixBus → transfer). Intento alto, affiliazione Omio e Welcome Pickups.
2. **"Does travel insurance cover strikes in Italy?"** (cosa coprono davvero: SafetyWing paga 60 $ per ritardi 3–8 ore e 150 $ oltre 8 ore, dai termini ufficiali del 10/10/2026; EKTA; quando NON copre). Affiliazione assicurazioni, solo da traffico organico (SafetyWing vieta gli annunci).
3. **"Italy strike calendar for your trip dates"** (già coperto dalle pagine-mese: è la query USA "italy strikes june 2026").
4. **"Airport strike in Italy: your EU261 rights"** (rimborso 250–600 €; AirHelp vieta Google Ads ma non il traffico organico).

Esempi di siti che fanno "traffico comprato → affiliazione assicurazione/eSIM" con numeri: **non trovati**. I siti di recensioni SafetyWing trovati (backpackingislife, freakingnomads, earthsims, portail-asie) vivono di Google, non di annunci; nessuno pubblica CPC pagato vs EPC.

## 5. Siti italiani: EsameB1 ed EsamiDiStato

- **CPC Italia**: "codice fiscale" **0,57 $**, "calcolo codice fiscale" **0,01 $** (snapshot Semrush database Italia, [ja.semrush.com/website/codicefiscaleonline.com](https://ja.semrush.com/website/codicefiscaleonline.com/overview), riassunto da ricerca). "esame b1 cittadinanza", "esame di stato ingegnere 2026": **non trovati**. Benchmark: CPC Italia "0,50–3 € nella maggior parte dei settori" ([adwservice](https://adwservice.com.ua/en/google-contextual-advertising-in-italy)); istruzione USA 4,81 $ (LocaliQ 2026). Lo studio 8 prevede già: *se il Keyword Planner dà CPC medio > 1,50 € ci si ferma*.
- **Costo per lead Facebook, istruzione, Italia**: mediana **21,31 $** (ott 2025–set 2026, da 14,72 a 29,61 $), circa la metà della media mondiale 44,10 $ ([Superads](https://www.superads.ai/facebook-ads-costs/cost-per-lead/education/italy)).
- **Ricavo per visita**: pubblicità **3–6 €** per 1.000 pagine (studio 7; Mediavine Italia 5,77 $ su un sito). Con 300–1.500 € per 1.000 visite comprate, il rapporto è **0,002–0,02**: la pubblicità in Italia non ripaga mai una visita comprata.
- **Lead-gen** (studio 8, `intelaiatura/8-leadgen-e-obblighi.md`): lead venduto 10–20 € (prezzo di riferimento 15 €), conversione clic → "Avvisami" 15–25 %, costo per iscritto previsto 2,5–4 €, soglia di continuazione ≤ 3 €; dei contatti solo una parte diventa lead qualificato (ipotesi 20–30 %) → **costo per lead 8–20 €** contro 15 € di vendita. Regge **solo** se: CPC ≤ 0,50 €, conversione ≥ 20 %, 3 scuole con accordo scritto, costo per lead pagato ≤ 1/3 del prezzo. È un margine stretto, non una macchina da scalare: con 100 € si comprano 70–200 clic → 10–50 iscritti → 3–15 lead → 45–225 € lordi. Tetto realistico della lead-gen a 18 mesi: 4–9k €/anno (studio 8), con o senza annunci.
- **EsamiDiStato**: nessun partner che compra lead identificato; solo pubblicità → nessun arbitraggio possibile.

## 6. Rischi e come limitarli

| Rischio | Prova | Limite |
|---|---|---|
| Perdere il capitale di test | Rapporto atteso 0,02–0,2: in media si perdono 80–98 € su 100 | Tetto 50–100 € una volta sola; stop automatico a metà budget se il rapporto è < 0,1 |
| Rifiuto o ban AdSense | AdSense responsabilizza l'editore per ogni fonte; vietati clic comprati e pagine "landing" scadenti | Mai comprare "visite" da rivenditori, PTC, push, pop; solo piattaforme con auto-servizio (Meta, Reddit, Pinterest, Microsoft, Google); canale AdSense dedicato per il traffico comprato; aspettare l'approvazione AdSense e 30 giorni di dati organici prima del test |
| Rifiuto Journey/Raptive | Raptive vieta "traffic purchased with the intent of making more money from advertising"; Mediavine guarda "traffic sources" in GA4 | Il traffico comprato non deve superare il 10–15 % delle sessioni del mese; test finito prima della domanda a Journey, o almeno 30 giorni dopo; niente test se si punta a Raptive |
| Storno commissioni affiliati | Airalo 3.2.16: rimozione e storno; Travelpayouts blocca i pagamenti per brand bidding; SafetyWing vieta gli annunci sui suoi prodotti | Parole chiave senza marchi; chiedere a SafetyWing per iscritto se gli annunci al nostro sito sono ammessi, altrimenti pagina di test senza SafetyWing |
| Click fraud / traffico finto | AdSense: "some of these services actually send artificial traffic… click bots… incentives" | Solo piattaforme grandi; guardare in GA4 durata sessione e pagine/sessione del segmento UTM; se durata < 10 s o rimbalzo > 90 % → stop |
| Stagionalità | Trends (studio 7): marzo è il picco storico degli scioperi; estate blackout scioperi fine luglio–inizio settembre; RPM Q1 −18 %, Q4 +35 % (modello adstimate) | Fare il test quando ci sono scioperi in calendario (marzo–giugno 2027), non a gennaio |
| Pagina sbagliata | Google Ads disapprova destinazioni "with more ads than original content" | Pagina di test = guida con testo lungo e 1–2 spazi pubblicitari |
| Dati che non si misurano | Senza UTM e canale AdSense non si distingue il traffico comprato da quello organico | UTM `utm_source=reddit&utm_medium=cpc&utm_campaign=test1`, canale AdSense "test-annunci", link affiliati con sub-ID della campagna |

## 7. Conclusione

### (a) L'arbitraggio può portare il totale oltre 10k €/anno? **No.**

Con i numeri pubblici del 2025–2026 una visita USA/UK costa 0,10–0,70 $ sui social e 1,3–3,4 $ sulla ricerca; le nostre pagine rendono 0,011–0,027 $ a visita (pubblicità + affiliazione). Rapporto 0,02–0,27 contro l'1,3 richiesto. Per arrivare a 10k €/anno con questo rapporto bisognerebbe spendere 40–500k € e perderli quasi tutti. L'unico caso con ROI positivo documentato (127 → 593 $) richiede RPM ≥ 30 $ e contenuti virali con CTR ≥ 5 %: il sito scioperi ha RPM 6–15 $ e contenuti di servizio. Raptive, la rete che pagherebbe di più, vieta per iscritto proprio questa pratica. **Capitale e rischio**: qualunque cifra oltre il test da 50–100 € è denaro perso con probabilità > 90 %. La crescita del sito scioperi resta quella già scritta in `STRATEGIA.md`: Google, pagine in più per lo stesso pubblico, lista email, Journey a 1.000 sessioni Tier 1.

### (b) Il test da ≤ 100 €, da proporre a Massimiliano SOLO dopo l'approvazione AdSense e con il suo sì sulla cifra

Scopo onesto del test: **non guadagnare**, ma misurare tre numeri reali che oggi non abbiamo (costo per visita, RPM reale, EPC degli affiliati) e chiudere la domanda per sempre. Disegno:

- **Quando**: dopo (1) approvazione AdSense, (2) riquadro affiliati online con almeno Omio e Airalo, (3) 30 giorni di dati organici in Search Console/GA4, (4) uno sciopero nazionale treni o aerei in calendario nei 10 giorni del test (marzo–giugno 2027 è la finestra migliore).
- **Canale**: **Reddit Ads** (CPC viaggi 0,10–0,50 $, minimo 5 $/giorno, targeting per community: r/ItalyTravel, r/travel, r/solotravel, Paesi US/UK/CA/AU). Alternativa se Reddit rifiuta l'account: Facebook/Instagram, pubblico "interessi: viaggi in Italia", stessi Paesi, obiettivo "traffico". **Non** Google Search (2 $ a clic: 100 € = 50 visite, non misurano nulla).
- **Parole/annuncio**: "Italy train strike on [data]: which trains run, refunds, alternatives" → nessun marchio (no Trenitalia/Italo/Omio/Airalo/SafetyWing nel testo).
- **Pagina**: la guida nuova "My train in Italy is cancelled by a strike: what to do now" (§4.1) con riquadro Omio + Airalo + Welcome Pickups, **senza SafetyWing** (salvo via libera scritto). Testo lungo, 2 spazi pubblicitari. UTM e canale AdSense dedicati.
- **Budget e durata**: **5 $/giorno × 10 giorni = 50 $ (~46 €)**; tetto assoluto 100 € solo se dopo 5 giorni le soglie sotto sono tutte verdi.
- **Soglie scritte prima** (misurate sul segmento UTM):
  - costo per visita **≤ 0,15 $** (altrimenti stop al giorno 5);
  - durata media sessione ≥ 40 s e pagine/sessione ≥ 1,3 (traffico vero);
  - RPM reale del canale AdSense **≥ 6 $** (soglia già in `STRATEGIA.md` §7);
  - clic sugli affiliati ≥ 3 % delle visite; EPC Omio ≥ 0,05 $;
  - **continuazione** solo se (RPM + ricavo affiliati) per 1.000 visite ≥ **1,3 ×** costo per 1.000 visite. Con costo 150 $/1.000 servono ≥ 195 $/1.000 di ricavo: con i dati pubblici è quasi impossibile, e va scritto così a Massimiliano prima di spendere.
  - **stop definitivo** se dopo 50 $ il rapporto è < 0,3: la domanda "comprare traffico" si chiude e non si riapre senza un cambiamento misurato (RPM reale ≥ 30 $ o un partner che paga ≥ 10 € a lead sul pubblico inglese).
- Esito atteso: rapporto 0,05–0,3. Valore del test: sapere quanto vale davvero una visita del sito (serve per decidere quante pagine costruire) e avere l'RPM reale per la domanda a Journey.

Test alternativo con più probabilità di stare in piedi: la **lead-gen EsameB1** (studio 8), 100 € su Google Search Italia, solo con 3 accordi scritti con scuole e CPC ≤ 1,50 € nel Keyword Planner. È l'unico "traffico comprato" con un prezzo di vendita (15 €/lead) sopra il costo di acquisto.

### (c) Cosa NON fare

1. Non comprare traffico per i siti italiani con la sola pubblicità (3–6 € per 1.000 visite contro 300–1.500 € di costo).
2. Non usare Google Search per l'arbitraggio su pubblicità (2–5 $ a clic).
3. Non fare "brand bidding": niente Airalo, Omio, Italo, Trenitalia, SafetyWing, EKTA come parole chiave o nei testi (storno commissioni, blocco pagamenti).
4. Non fare annunci per i prodotti SafetyWing (vietato dai termini, 5/3/2026).
5. Non comprare "visite" da rivenditori, push, pop-under, PTC, traffico Tier 3 "economico": è quello che AdSense chiama traffico artificiale e porta al ban.
6. Non comprare traffico se si punta a Raptive (policy esplicita) e non superare il 10–15 % delle sessioni con traffico comprato prima della domanda a Journey.
7. Non scalare: nessun budget "per farsi conoscere", nessun secondo test senza che il primo abbia superato le soglie scritte (regola di spesa del 10/10/2026).
8. Non confondere "clic sull'annuncio pagato 0,50 $" con "0,50 $ di AdSense": AdSense paga per 1.000 pagine viste 6–15 $, cioè 0,006–0,015 $ a visita.

### Cosa manca (non trovato)

CPC esatti per le nostre parole (serve il Keyword Planner dall'account Google Ads di Massimiliano: 15 minuti, 0 €, già previsto nello studio 8 come "giorno 0"); EPC pubblico di SafetyWing e Airalo; policy scritta di Ezoic; casi con numeri reali di arbitraggio in nicchia viaggi su Reddit/Niche Pursuits/Authority Hacker; RPM AdSense Italia 2025 con dati primari; CPC Microsoft Ads per il settore viaggi.

File scaricati: `scratchpad/ads/raw/` (policy AdSense, Google Ads, Mediavine, Raptive via API, SafetyWing help, Airalo/MCANISM, Travelpayouts/Omio, LocaliQ, Superads, Tailwind, Dataslayer, arbhunter, danny-cph, Sunshine Seeker, partnerkin, weforads, trackbee).
