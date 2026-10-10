# Ricerca A — Comprare attività online già redditizie (invece di crearle da zero)

Data della ricerca: 10 ottobre 2026. Tutte le pagine citate sono state lette quel giorno, salvo dove indicato.
Budget considerato: fascia A 0-3.000 €, fascia B 3.000-10.000 €. Cambio usato nei calcoli: 1 $ ≈ 0,92 € (approssimazione mia).

Regole rispettate (REGOLE-FISSE.md): ogni candidata ha prove di prezzi reali, un confronto con l'alternativa "costruire da zero" (che è ciò che stai già facendo a 0 €), niente email a freddo, niente dati inventati. Dove un numero non esiste o non è verificabile c'è scritto **non trovato** o **stima mia**.

---

## 0. La risposta in breve

**Comprare un sito piccolo (2.000-10.000 €) NON è, oggi, un affare chiaramente migliore di costruirne uno a 0 €.** Tre motivi, tutti con numeri sotto:

1. **I prezzi sono "27 mesi di profitto"** (mediana reale su Motion Invest, 92 inserzioni attive lette il 10/10/2026). Cioè, se tutto resta uguale, recuperi i soldi in 2 anni e 3 mesi. Ma "tutto resta uguale" non è lo scenario prudente: le vendite di siti di contenuto sono crollate (-39 % in un semestre su Flippa, da 70 a ~30 all'anno su Empire Flippers) proprio perché Google e le risposte AI tolgono visite.
2. **Il nodo fiscale mangia il guadagno.** I ricavi da pubblicità/affiliazione per un italiano sono considerati attività commerciale: Camera di Commercio + INPS commercianti, circa **3.000 €/anno fissi** anche con lo sconto forfettario del 35 %. Un sito da 5.000 € rende 2.000-2.600 €/anno: non copre nemmeno l'INPS. (Fonti italiane in sez. 7.) Stesso nodo che hai già per EsameB1 e gli altri: si apre al primo incasso, ma qui l'incasso è più piccolo del costo fisso.
3. **Nel forfettario il prezzo di acquisto non si scarica** (i costi non sono deducibili) e, se il venditore è un'impresa estera, l'IVA al 22 % va versata e non è recuperabile. Un sito da 5.000 $ può costare, in pratica, fino a 6.100 $.

**Cosa ha senso:** al massimo **UN acquisto-test da 2.000-3.000 € da Motion Invest o Investors Club** (dati Google Analytics/Search Console verificati), con traffico NON solo da Google (Pinterest, Bing, strumenti online), e **solo dopo** aver chiuso il nodo fiscale con un professionista (la domanda è già scritta in REGOLE-FISSE). Vedi il piano in sez. 9.

---

## 1. Tabella riassuntiva delle 6 candidate

| Candidata | Investimento tipico | Rendimento prudente a 12 mesi | Probabilità di successo | Lavoro mensile (dopo l'acquisto) | Vincolo fiscale |
|---|---|---|---|---|---|
| 1. Sito di contenuto (AdSense/affiliazione) | 2.000-10.000 $ per 70-350 $/mese di profitto (27x) | **30-45 % del prezzo** (es. 5.000 $ → 1.500-2.200 $ netti). Payback 2,5-3,5 anni se il traffico tiene | **Media-bassa**: prezzi ragionevoli, ma il traffico Google cala e nessun marketplace garantisce il dopo | 3-10 h; Claude può fare 80-90 % (articoli, aggiornamenti, pin) | CCIAA + INPS commercianti (~3.000 €/anno) |
| 2. Negozi Etsy/Shopify/POD | 2.000-9.000 $ | **non calcolabile**: Etsy vieta il passaggio di account; su Flippa i negozi sotto 10 k$ sono venduti a 0,2-1,4 anni di profitto (segnale di allarme) | **Bassa** | 5-20 h (ordini, clienti) | Commercio al dettaglio → CCIAA + INPS commercianti |
| 3. Micro-SaaS / estensioni | 1.500-5.500 $ per 1.000-2.300 $/ANNO di ricavo (2-3x ricavo annuo) | **20-30 %** (churn 25 % + costi server) | **Bassa-media**: vendita di software in abbonamento = attività commerciale (stesso blocco dell'app Pipedrive) | 2-8 h; Claude può fare quasi tutto il tecnico | Commerciale; Stripe/Paddle intestati a te |
| 4. Newsletter con sponsor | 3.600-30.000 $ (prezzi Duuce/LetterTrader) | **non trovato** (ricavi non pubblici); gli sponsor vanno cercati: contatti a freddo = vietati dalla tua regola 3 | **Bassa** | 4-12 h (scrivere + vendere sponsor) | Commerciale (pubblicità) |
| 5. Canali YouTube/TikTok | 2.000-12.000 $ per 100-700 $/mese (9-40x) | **35-45 %** se la rimonetizzazione va bene; **0 %** se il canale viene demonetizzato | **Bassa-media**: AdSense non trasferibile, 8-12 h/settimana dichiarate dai venditori, policy sui contenuti "senza volto" | 30-50 h (video); Claude non può caricare né produrre video senza crediti (regola 1) | Commerciale |
| 6. Domini | 10-15 $/anno per dominio + acquisto | **negativo o zero**: si vende il 2-3 % del portafoglio all'anno, prezzo medio 1.281 $ ma mediana **non trovata** (NameBio bloccato) | **Bassa** | 1-2 h | Commerciale se abituale |

---

## 2. Prezzi reali: quanto costano davvero (prove)

### 2.1 Multipli di mercato (quante mensilità di profitto si pagano)

| Fonte | Dato | URL (letto il 10/10/2026) |
|---|---|---|
| **Motion Invest – dati del marketplace** (ho letto il database pubblico che alimenta il loro sito: 719 inserzioni totali, 92 attive, 174 vendute, 453 bozze) | Fascia 2.000-12.000 $: **31 inserzioni attive, multiplo mediano 27,1x il profitto mensile** (25 % sotto 22,7x, 25 % sopra 35,6x). **69 vendute** nella stessa fascia: mediana **28,7x**. Monetizzazione più comune: Google AdSense (11), Amazon Associates (5), Mediavine Journey (3), YouTube (4). | https://www.motioninvest.com/websites-for-sale/ (la pagina è un'app JavaScript: curl riceve solo 2,8 KB; i dati li ho presi dall'API pubblica che la pagina stessa interroga) |
| Empire Flippers, video del 25/5/2025 (agg. 11/7/2025), 145 vendite analizzate | Multiplo medio siti di contenuto: **30x (2023) → 27x (2024) → 24x (2025)**. Siti venduti: **70 (2023) → 50 (2024) → ~30 (metà 2025)**. Prezzo medio 325.000 $ (fuori dalla tua fascia). | https://empireflippers.com/you-can-sell-your-business-for-life-changing-money-in-2025-heres-the-secret/ |
| Flippa, "Digital M&A Insights H1 2026" | Multiplo medio siti di contenuto **2,32x il profitto ANNUO** (= ~28 mesi); i migliori 4,68x. **Vendite di siti di contenuto -39 % nel semestre**, il calo peggiore di tutte le categorie; **YouTube +23 %**, ha superato i siti di contenuto per numero di vendite. Fascia 10-100 k$: media 2,24x annuo. | https://flippa.com/blog/digital-ma-insights-h1-2026/ |
| Niche Pursuits (Spencer Haws, fondatore Motion Invest), statistiche storiche | 308 inserzioni, 96,4 % vendute, 11,1 giorni per vendere, multiplo medio 35,5x (min 17x, max 90x per un sito da 20 $/mese) | https://www.nichepursuits.com/?p=24833 (post non datato, dati di ~2021) |
| Jean Galea, guida 2026 | "I multipli sono passati da 35-40x (2021) a ~24x (2025); i siti si vendono all'82 % del prezzo chiesto, contro il 90 % del 2023" | https://jeangalea.com/guide-buying-websites/ |

**Traduzione pratica:** oggi un sito che fa 200 $/mese costa 4.800-5.600 $. Per recuperare il prezzo servono 24-28 mesi *se il profitto non cala*.

### 2.2 Inserzioni reali ATTUALI nella fascia 2.000-12.000 $ (siti di contenuto)

Da Motion Invest, stato "attivo" il 10/10/2026 (pubblicate tra febbraio e ottobre 2026). Profitto = media mensile dichiarata dal venditore; "visite" = pagine viste/mese da Google Analytics collegato; "DR" = autorità dei link (Ahrefs, 0-100); "AI" = punteggio Originality.ai se presente (100 = tutto scritto da AI).

| Sito | Prezzo | Profitto/mese | Multiplo | Età / anno | Monetizzazione | Visite/mese | Articoli | DR | AI |
|---|---|---|---|---|---|---|---|---|---|
| londonfromscratch.co.uk | 2.100 $ | 72 $ | 29x | 2 anni / 2024 | AdSense | 15.943 | 359 | 7 | — |
| vivyro.com | 2.500 $ | 78 $ | 32x | 2 anni / 2025 | Mediavine Journey | 14.550 | 360 | 1,5 | — |
| wedwithme.com | 2.650 $ | 104 $ | 25x | 1 anno / 2025 | Mediavine Journey | 17.014 | 220 | 0 | — |
| vocabish.com | 3.000 $ | 137 $ | 22x | 3 anni / 2024 | AdSense | 35.403 | 700 | 32 | — |
| lifeverse.pro | 3.000 $ | 116 $ | 26x | 2 anni / 2025 | Mediavine Journey + Monumetric | 25.109 | 800 | 0,3 | 1 |
| deliasmithrecipes.uk | 4.550 $ | 224 $ | 20x | 1 anno / 2025 | AdSense | 43.292 | 294 | 6 | 34 |
| medsdog.com | 5.100 $ | 228 $ | 22x | 1 anno / 2025 | AdSense + Amazon | 16.963 | 253 | 1,4 | — |
| gardeninglatest.com | 8.200 $ | 307 $ | 27x | 6 anni / 2021 | Ezoic | 28.182 | 529 | 13 | — |
| coveradvice.com | 9.000 $ | 321 $ | 28x | 4 anni / 2022 | Amazon Associates | 4.370 | 2.233 | 2,9 | — |
| philhealthportal.com | 10.000 $ | 341 $ | 29x | 1 anno / 2025 | AdSense | 112.432 | 16 | 32 | — |

Cose che saltano all'occhio (osservazioni mie sui dati): quasi tutti hanno **1-2 anni di vita** (creati nel 2024-2025, dopo gli update Google); molti vivono di **Pinterest** e non di Google; diversi sono siti "menu di catene di ristoranti" (thesheetzmenu.com 5.000 $, 7brewcoffemenu.com 3.000 $, daveshotchickenmenu.us) o "ricette di un cuoco famoso" (deliasmithrecipes.uk, gordonramsayrecipes.uk venduto a 5.000 $): usano **marchi altrui** nel dominio, rischio legale. Dove c'è il punteggio AI, spesso è alto (smartlanguagelearner.com 94, ereads.com 100).

**Venduti di recente su Motion Invest** (stessa fascia, per capire a che prezzo si chiude davvero): chefol.com 2.100 $ per 69 $/mese (30x, Mediavine Journey, 1.800 articoli); resizeclub.com 2.350 $ per 100 $/mese (23x, strumento online, AdSense); rbtpracticeexam.io 4.850 $ per 328 $/mese (15x, quiz + abbonamenti); gordonramsayrecipes.uk 5.000 $ per 233 $/mese (21x); cosyblisshomes.com 7.000 $ per 325 $/mese (21x, Ezoic); chicnstylish.com 11.500 $ per 782 $/mese (15x, Mediavine Journey, 82.885 visite/mese).

**Investors Club** (newsletter con le nuove inserzioni, ~dicembre 2025-gennaio 2026; marketplace a 404 senza login): sito di cucina su WordPress + Mediavine Journey, traffico da Pinterest e Bing, profitto annuo 715 $, prezzo **2.000 $**; blog di cucina con Ezoic, 300 articoli, Pinterest, 2-4 h/settimana, profitto annuo 792 $, prezzo **2.299 $**; strumento online per ridimensionare immagini (pubblicità), profitto annuo 1.104 $, prezzo **4.000 $**; SaaS di generazione immagini AI, profitto annuo 3.450 $, prezzo **9.500 $**. Fonte: https://emails.investors.club/posts/6-new-listings-650-12k-1 e https://emails.investors.club/posts/11-new-listings-1-2k-5m . Investors Club dichiara di accettare solo siti con Google Analytics e Search Console collegati ("non ammettiamo siti con dati di traffico non verificati"), commissione 5-7 % al venditore (https://investors.club/how-to-list-your-website/).

**Flippa** (ricerca "siti, 2.000-10.000 $", letta con curl il 10/10/2026; la pagina mostra 305 inserzioni "Content" in tutto il sito): "Copywriters Now Blog", Nigeria, 8 anni, profitto 306 $/mese, prezzo **8.799 $** (2,4x annuo = 29 mesi). Le altre inserzioni sotto i 10 k$ sono negozi: AnyCases.shop (UK) 6.590 $ con profitto dichiarato 882 $/mese ma **"negozio in pausa da giugno 2026"** (multiplo 0,6x annuo); Prankpakket.nl 8.566 $ per 508 $/mese (1,4x annuo); FashionMotive.com ribassato del 54 % a 21.740 $ (0,2x annuo). Multipli così bassi (meno di un anno e mezzo di profitto) sono il classico segnale di numeri non reali o non ripetibili. Esempi di inserzioni singole: sito CPA "sondaggi pagati", 2 anni, profitto verificato 540 $/mese, prezzo 19.000 $ (https://flippa.com/12767786-...); sito tech di 12 anni, AdSense verificato, profitto 464 $/mese, multiplo 3,1x annuo (https://flippa.com/9857005-...).

### 2.3 Negozi Etsy / Shopify / print-on-demand

- **Etsy vieta il passaggio di account**: "per motivi di sicurezza e requisiti legali, i trasferimenti di account non sono permessi su Etsy, come indicato nei Termini d'uso; se Etsy ritiene che sia avvenuto un trasferimento, l'account può essere sospeso senza preavviso". https://help.etsy.com/hc/articles/360040985353 . Quindi "comprare un negozio Etsy" significa comprare i file e il nome e **ricominciare da zero con un negozio nuovo** (recensioni e posizionamento non si trasferiscono). Tu hai già PressedHeart: comprare file di altri non aggiunge nulla che Claude non possa produrre.
- **Shopify/POD su Flippa**: le inserzioni sotto 10 k$ viste sopra sono a 0,2-1,4 anni di profitto, con negozi "in pausa" o dropshipping. Una guida 2025 all'acquisto di negozi Shopify avverte che "molti venditori gonfiano i numeri con vendite finte, traffico bot o campagne pubblicitarie non sostenibili" e che "molte inserzioni hanno screenshot di vendite falsi" (https://ecomm.design/how-to-buy-a-shopify-store/).
- Verdetto: **no**.

### 2.4 Micro-SaaS / estensioni / app

- **Microns.io** (home letta il 10/10/2026, listing completi solo con abbonamento Premium 49 $/mese): estensione Chrome "Reddit bookmark manager" ricavo annuo 1.467 $, prezzo **3.500 $**; "AI writing assistant" ricavo annuo 2.250 $, prezzo **5.500 $**; "AI book summaries" ricavo annuo 1.114 $, prezzo **3.600 $**; app iOS "AI calorie counter" ricavo annuo 156 $, prezzo 2.000 $. **Venduti**: app iOS restauro foto, ricavo annuo 1.900 $, venduta a **2.000 $**; piattaforma "YouTube growth" ricavo annuo 11.300 $, venduta a **3.000 $** (sotto il ricavo: segno di churn o costi alti); newsletter Substack 2.800 iscritti, ricavo annuo 235 $, venduta a 4.000 $. https://www.microns.io/
- **Acquire.com**: la home si legge, ma il marketplace risponde 404 senza login (https://acquire.com/marketplace/). Dati di terzi: prezzo mediano richiesto 195.800 $, ~2x ricavo annuo (https://bigideasdb.com/state-of-saas-valuations-2026, pagina che però mi ha risposto 429 "troppe richieste" al secondo accesso). Fuori dalla tua fascia.
- **Tiny Acquisitions**: il dominio non risolve dal server (errore DNS, due tentativi). **Non verificato.**
- **Regola pratica**: le micro-app si pagano **2-3 volte il ricavo ANNUO**, cioè il doppio di un sito di contenuto a parità di soldi incassati. E il ricavo di un'app in abbonamento cala da solo se non la fai crescere (churn): un broker racconta prodotti passati "da 20-30 k$/mese a zero quasi da un giorno all'altro perché la piattaforma ha cambiato le regole" (https://podcast.ausha.co/indie-board-session/from-30k-mrr-to-zero-and-why-platform-risk-scares-buyers).
- **Blocco fiscale già noto**: vendere software in abbonamento è ciò che REGOLE-FISSE segna come "probabile attività commerciale → CCIAA". Vale uguale per un'app comprata.

### 2.5 Newsletter

- **Duuce** (ora "LetterTrader", home letta il 10/10/2026): in vendita newsletter AI 19 k iscritti a **16.000 $**, AI 58 k a 25.000 $, business 36 k a 20.000 $, finanza 116 k a 20.000 $ ("prezzo ridotto"), crypto 173 k a 30.000 $. **Vendute**: business 24 k iscritti a **8.000 $**, locale 36 k a 13.000 $, locale (eventi a Columbus) **2.400 iscritti a 3.600 $**. I ricavi **non sono mostrati** pubblicamente. https://duuce.com/
- Fonti di seconda mano (2022-2023): esempio 4.103 iscritti con 440 $/mese chiesti 7.500 $ (17x); Duuce prendeva il 10 % a vendita (https://inboxreads.co/blog/buying-selling-newsletters).
- Problema strutturale: il ricavo viene dagli **sponsor**, che vanno cercati e convinti uno a uno. È un lavoro di vendita, non automatico, e il canale tipico (email a freddo alle aziende) è vietato dalla tua regola 3. Verdetto: **no**.

### 2.6 Canali YouTube / TikTok

- **Motion Invest** (10 canali attivi, 27 venduti): @LivingDecisionsUSA 6.000 $ per 321 $/mese (19x, 2.470 iscritti); @SmartConsumerGuides 3.999 $ per 178 $/mese (22x); @msparkquiz 10.000 $ per 520 $/mese (19x). **Venduti**: @QuantumWhisper 2.099 $ per 224 $/mese (**9x**, 1.870 video), @Nerdsplaining 7.100 $ per 299 $/mese (24x), @Quizplacess 7.200 $ per 250 $/mese (29x).
- **Investors Club**: canale scacchi "senza volto", AdSense, profitto annuo 8.020 $, prezzo 12.000 $ (18x) — ma "**richiede 8-12 ore a settimana** per essere mantenuto".
- **Fameswap** (primo tentativo: errore 502; secondo: ok): 25.938 inserzioni, quasi tutte pagine TikTok/Instagram da 100-5.000 $ senza ricavi dichiarati; canale YouTube "UFO" monetizzato 16 k iscritti **19.500 $**; canale Shorts 3,1 M iscritti 39.999 $. Commissione 10 %. https://fameswap.com/
- **Flippa H1 2026**: multiplo medio canali YouTube 1,57x annuo (≈19 mesi), i migliori 2,65x.
- **Rischi specifici**: (a) **l'account AdSense non si trasferisce** (Google lo vieta): il compratore deve avere il proprio AdSense approvato e il canale va ri-collegato, con un periodo senza incassi; (b) i canali si cedono spostando un "Brand Account", ma la vendita in sé non è prevista dai Termini e YouTube può intervenire se nota anomalie (fonti: https://investors.club/buying-monetized-youtube-channels/ , https://outlierkit.com/resources/is-it-legal-to-sell-youtube-channel/ — entrambi venditori/broker, non Google; il testo dei Termini YouTube non l'ho verificato); (c) i canali "senza volto" con contenuti ripetitivi sono il tipo più esposto alle regole di monetizzazione (**non verificato in questa ricerca**: da leggere le norme YPP aggiornate prima di comprare). (d) Per continuare servono video nuovi: Claude non può caricarli né produrli senza crediti (regola 1). Verdetto: **no, salvo che tu voglia fare video tu stesso**.

### 2.7 Domini

- Sell-through (quota di domini venduti in un anno): "**2-3 % è tipico**" (DomainSherpa, https://www.domainsherpa.com/?p=11452); stima 2019 da NameBio: 0,48 % riportato, forse 3 % reale per i .com (https://www.namecheap.com/blog/domain-name-sell-through-rate/).
- Prezzo medio 2024: **1.281 $** su 144.700 vendite (185 M$) — media, non mediana; la mediana è molto più bassa (https://domaindetails.com/kb/domain-investing/comparable-domain-sales). NameBio.com risponde **403** dal server: **dati 2025-2026 non trovati**.
- Su Flippa ci sono **15.501 domini** in vendita contro 305 siti di contenuto (filtri della ricerca Flippa del 10/10/2026): offerta enorme, domanda scarsa.
- **Calcolo (stima mia)**: 100 domini × 12 $/anno di rinnovo = 1.200 $/anno; al 2-3 % vendi 2-3 domini; se il prezzo mediano reale è 300-1.000 $ incassi 600-3.000 $. Risultato tra perdita e pareggio, prima dei costi di acquisto. Rendimento **non dimostrato**. Verdetto: **no**.

---

## 3. Truffe e rischi noti (con numeri dove esistono)

| Rischio | Cosa dicono le fonti | URL |
|---|---|---|
| Inserzioni non verificate | "Flippa verifica le inserzioni sopra i 50.000 $, non quelle sotto (e la grande maggioranza è sotto)". Flippa stessa scrive su ogni pagina: "i dati finanziari sono inseriti dal venditore". | https://investors.club/?p=5001 ; pagine Flippa citate sopra |
| Compratori che non controllano | Sondaggio Flippa (2011, vecchio ma unico trovato): "il 50 % dei compratori passa meno di 1 ora a verificare traffico e ricavi; meno del 5 % entra nei sistemi di analytics/ricavi del venditore". | https://www.businesswire.com/news/home/20110623005626/en/ |
| Traffico finto | Si compra traffico a basso costo che fa bello Google Analytics; il venditore smette di pagarlo dopo la vendita. Segnali: picchi improvvisi, molto traffico "diretto"/social, meno di 10 secondi per pagina. | https://investors.club/?p=5001 |
| Ricavi finti | Screenshot modificati con l'HTML del browser; Flippa non controlla gli screenshot. Il trucco classico: "il sito fa 600 $/mese" ma sono i ricavi sommati di più siti. | https://investors.club/?p=5001 ; https://jeangalea.com/guide-buying-websites/ |
| Multiplo troppo basso | "I siti si vendono a 20-40 volte il profitto mensile; un'inserzione a 6-12x (o meno) è quasi sempre un problema nascosto". | https://investors.club/?p=5001 |
| Dipendenza da Google | 671 siti di viaggi analizzati: **il 32 % ha perso più del 90 % del traffico** dopo gli update 2023-2025; chi "si è ripreso" ha recuperato circa un terzo. Casi singoli: HouseFresh -95 %, un sito moto -65 %. Studio Zyppy su 50 siti: variazioni da **-67 % a +5.595 %** in 4 mesi (ago-dic 2023); i siti con annunci fissi in fondo pagina + video che segue + nessuna esperienza personale avevano l'83 % di probabilità di essere tra i perdenti. | https://jeangalea.com/guide-buying-websites/ ; https://zyppy.com/seo/google-update-case-study/ ; https://hooshmand.net/google-helpful-content-niche-bloggers-forums/ |
| Risposte AI di Google | Click dal primo risultato **-34,5 %** sulle ricerche informative con AI Overview (Ahrefs); ricerche "senza click" dal 56 % al 69 % (Similarweb, mag 2024→mag 2025); referral a siti di viaggio -20 %, news -17 %. | https://blog.on-page.ai/the-zero-click-apocalypse-how-ai-search-is-killing-publisher-traffic/ (riassunto di seconda mano di dati Similarweb/Ahrefs) |
| Il mercato lo sa | Vendite di siti di contenuto: Empire Flippers 70 → 50 → ~30/anno; Flippa **-39 %** in H1 2026; i siti che si vendono sono "i sopravvissuti": età media salita del 29 %, oltre 10 anni. | fonti sez. 2.1 |
| Quanti compratori ci perdono | **Non trovato**: nessun marketplace pubblica i risultati dei siti DOPO la vendita. Motion Invest pubblica solo il tasso di vendita (96 %), che riguarda il venditore. Un commento sul blog di Motion Invest chiedeva "perché non mostrate i dati dei siti venduti?" senza risposta. | https://www.nichepursuits.com/?p=15915 |
| Marchi altrui | Molti siti in vendita sotto 5 k$ usano marchi registrati nel dominio (menu di catene, ricette di cuochi famosi): rischio di reclamo e chiusura. | osservazione mia sui dati Motion Invest, sez. 2.2 |

---

## 4. Quanto lavoro serve dopo l'acquisto e cosa può fare Claude

| Tipo | Ore/mese dichiarate dai venditori | Cosa fa Claude | Cosa resta a te |
|---|---|---|---|
| Sito di contenuto (WordPress) | 8-20 h (Investors Club: "2-4 h/settimana"; Flippa: "3-5 h/settimana") | Articoli nuovi e aggiornamenti, pin Pinterest (testo+immagine con codice, senza crediti), controllo Search Console, backup, aggiornamenti plugin, migrazione hosting. **80-90 %** | Pagare hosting/dominio (unica spesa fissa: 60-150 €/anno), ricevere i pagamenti AdSense/Amazon, approvare i contenuti |
| Strumento online (calcolatori, resize immagini) | 1-4 h | Tutto il tecnico; può anche riscriverlo su Netlify a 0 € | Nulla di rilevante |
| Micro-SaaS | 5-20 h (supporto clienti, bug, server) | Codice, bug, email di supporto scritte (le invii tu) | Stripe/Paddle intestati a te, costi server/API |
| YouTube | 30-50 h (8-12 h/settimana per il canale scacchi) | Copioni, titoli, descrizioni | Produrre e caricare i video |
| Newsletter | 15-40 h (scrivere + trovare sponsor) | Testi | Vendere gli sponsor (telefono, non email) |
| Domini | 1-2 h | Monitoraggio scadenze | Rinnovi |

Conclusione: **solo siti di contenuto e strumenti online sono davvero "automatici" con Claude**. Gli altri richiedono te.

---

## 5. Rendimento atteso a 12 mesi, prudente (con il calcolo)

Ipotesi comuni: escrow 2,4-2,6 % + 25 $ di bonifico internazionale; hosting 100 €/anno; nessuna crescita; **calo del traffico del 30 % nell'anno** (prudente: è meno del -34,5 % dei click misurato da Ahrefs e molto meno del -90 % subito da un terzo dei siti di viaggio).

**Sito di contenuto da 5.000 $ che rende 200 $/mese (25x)**
- Costo totale: 5.000 + 145 (escrow) + 25 = 5.170 $ (+ 1.100 $ di IVA se il venditore è un'impresa estera soggetta a IVA, vedi sez. 7).
- Incasso 12 mesi: 200 $/mese che scende linearmente a 140 $ → media 170 $ × 12 = 2.040 $; meno hosting 110 $ = **1.930 $ (37 % del prezzo)**.
- Se il traffico tiene: 2.290 $ (44 %). Se il sito prende un update brutto (-70 %): ~1.000 $ (19 %).
- **Payback: 2,5-3,5 anni** senza costi fiscali; **mai** se sopra ci metti 3.000 €/anno di INPS commercianti (sez. 7). Per coprire l'INPS servono almeno 300 $/mese di profitto *netto di calo*, cioè un acquisto da 9.000-12.000 $ che non è più un "test".
- Valore di rivendita a 12 mesi (stima mia): 24x su 140 $ = 3.400 $. Totale a 12 mesi 1.930 + 3.400 = 5.330 $ contro 5.170 $ spesi: **pareggio**, non guadagno.

**Sito-test da 2.500 $ che rende 100 $/mese (25x)**
- Incasso prudente 12 mesi: 85 $ × 12 - 110 = **910 $ (36 %)**. Payback ~3 anni. Serve a imparare, non a guadagnare.

**Micro-SaaS da 4.000 $ con 1.500 $/anno di ricavo (2,7x ricavo, come Microns)**
- Churn 25 %, costi server/API 200 $: 1.500 × 0,8 media - 200 = **1.000 $ (25 %)**. Payback 4 anni. Con il rischio "piattaforma cambia le regole".

**Canale YouTube da 6.000 $ con 321 $/mese (19x)**
- 2 mesi senza incassi per ri-collegare AdSense, poi -30 %: 321 × 0,85 × 10 = **2.700 $ (45 %)** — ma con 8-12 h/settimana di lavoro tuo e rischio di demonetizzazione (= 0 $).

**Newsletter, domini, Etsy**: non calcolabile con dati verificabili (vedi sopra).

---

## 6. Pagamenti, contratti, trasferimento, rischio di perdere l'asset

- **Escrow.com** (tariffe lette il 10/10/2026): **2,6 % fino a 5.000 $ (minimo 50 $)**, **2,4 % da 5.000 a 50.000 $ (minimo 130 $)**; +25 $ se il compratore è fuori USA e paga con bonifico; +3,05 % se paghi con carta/PayPal (solo sotto 5.000 $). Il venditore riceve i soldi solo quando confermi di aver ricevuto dominio e sito. https://www.escrow.com/fee-calculator . Motion Invest, Flippa (con "FlippaPay"), Investors Club, Microns, Fameswap e LetterTrader dichiarano tutti di usare un escrow proprio o Escrow.com. **Regola di Flippa che vale ovunque: "mai completare un acquisto senza escrow; un venditore che rifiuta l'escrow è un segnale d'allarme"** (https://flippa.com/blog/buy-youtube-channel/).
- **Cosa si trasferisce** in un sito di contenuto: (1) il **dominio** (spostato al tuo registrar: è l'unica cosa che conta davvero, chi ha il dominio ha il sito); (2) i file WordPress + database (Claude li migra su un hosting tuo o, se il sito è statico, su Netlify a 0 €); (3) gli account pubblicitari **NON si trasferiscono**: AdSense, Mediavine, Ezoic, Amazon Associates vanno riaperti a tuo nome e ri-approvati (Mediavine Journey richiede da gennaio 2026 solo 1.000 sessioni/mese; Raptive 25.000 pagine viste; Ezoic 250.000 utenti — https://ppc.land/is-your-site-finally-ready-the-new-math-behind-premium-ad-network-approvals/). Nel passaggio ci sono 2-6 settimane senza incassi (stima mia).
- **Contratto**: i marketplace forniscono un contratto standard (Acquire: LOI/APA generati sulla piattaforma; Flippa: partner legali). Per importi sotto 10 k$ nessuno fa due diligence al posto tuo: Claude può controllare Analytics/Search Console in sola lettura PRIMA di pagare (è la verifica che il 95 % dei compratori non fa).
- **Rischi di perdere l'asset**: dominio con marchio altrui (reclamo UDRP → perdi il dominio); contenuti copiati (DMCA); account pubblicitario rifiutato (sito con contenuti AI di bassa qualità → AdSense dice no); venditore che tiene accessi (cambiare tutte le password e le email di recupero subito). Per YouTube/Etsy il rischio è la **sospensione dell'account** stesso (sez. 2.3, 2.6).

---

## 7. Vincoli legali e fiscali per te (forfettario, ATECO 74.20.19, senza Camera di Commercio)

Cosa dicono le fonti italiane trovate (tutte lette il 10/10/2026):

| Fonte | Cosa dice (frasi chiave) | URL |
|---|---|---|
| **Il Commercialista Online** – "Google AdSense: aprire partita IVA sì o no?" (agg. 09/07/2025) | "Se sei un creator, blogger o marketer, apri Partita IVA come **ditta individuale** e ti iscrivi al **Registro Imprese**". Adempimenti: "apertura P.IVA, iscrizione Registro Imprese (Camera di Commercio), **Iscrizione INPS Gestione Commercianti**". ATECO consigliato **73.11.02** o 73.12.00. Costi: "ComUnica circa 35 € tra diritti e bolli; **diritto camerale annuale 57 €**"; "Gestione Commercianti: contributi annuali sul **minimale pari a circa 4.000 €**; per i forfettari **riduzione del 35 %**". **Eccezione**: "se l'attività pubblicitaria AdSense è **accessoria ad altra attività tipicamente professionale**, potrebbe non essere necessaria l'iscrizione in Camera di Commercio" e "è prevista l'iscrizione alla **Gestione Separata**, con contributi sul reddito percepito". Fattura a Google Ireland senza IVA (art. 7-ter, reverse charge), serve iscrizione VIES. | https://www.ilcommercialistaonline.it/?p=190 |
| **Il Commercialista Online** – "Codici ATECO per le professioni online" (agg. 20/10/2025) | "Se intendi lavorare con affiliazioni online, pubblicità, eCommerce, la partita IVA è necessaria fin dall'inizio". **Affiliate marketing: 73.11.02**. "Le attività commerciali devono iscriversi al Registro delle Imprese... diritti annuali e iscrizione alla Gestione commercianti dell'INPS. I professionisti devono iscriversi alla Gestione separata". | https://www.ilcommercialistaonline.it/?p=53682 |
| **Flextax** – "Obbligo CCIAA per attività di segnalatore?" (risposta ufficiale del loro team) | Procacciatore/segnalatore: ATECO 46.19.02, coefficiente 62 %, "iscrizione in Camera di Commercio, diritto camerale annuale di circa 50 €", "**Gestione Commercianti INPS: contributi fissi pari a 4.611,64 € fino a un reddito di 18.808 €**, oltre 24,48 %"; con il forfettario "**riduzione del 35 %** sui contributi, sia fissi che in percentuale" → **≈ 3.000 €/anno fissi**. | https://flextax.it/ho-lobbligo-di-iscrizione-in-camera-di-commercio-per-lattivita-di-segnalatore/ |
| **Money.it** – "Come si fattura Google AdSense" (21/06/2022) | "Serve la partita IVA? **Sì. Si tratta di un'attività di tipo commerciale** e come tale deve essere trattata. Non si può usare la prestazione occasionale". | https://www.money.it/come-si-fattura-google-adsense-nel-2022 |
| **Il Commercialista Online** – "Vendere su Etsy" (agg. 23/09/2024) | Artisti: ATECO 90.03.09, **Gestione Separata, niente Registro Imprese né SCIA**. Commercianti: 47.91.10, Registro Imprese + Gestione Commercianti + SCIA al SUAP. (Rilevante per te: i tuoi prodotti PressedHeart sono creazioni tue; un sito comprato con pubblicità no.) | https://www.ilcommercialistaonline.it/vendere-su-etsy-cosa-devi-sapere/ |
| **Fiscozen** – "Acquisti internazionali in regime forfettario" (agg. agosto 2026) | "In forfettario paghi sempre l'IVA sugli acquisti esteri: **servizi esteri sempre reverse charge**"; "**In forfettario l'IVA versata non è detraibile. Diventa un costo secco per te**"; e-fattura TD17, versamento con F24 entro il 16 del mese dopo. | https://www.fiscozen.it/guide/acquisti-internazionali-in-regime-forfettario-come-funzionano/ |
| **PartitaIVA.it** – spese deducibili nel forfettario | "Nel forfettario i **costi non si deducono**... l'unica vera eccezione: i contributi previdenziali"; "l'IVA pagata sugli acquisti non è detraibile". | https://www.partitaiva.it/spese-deducibili-regime-forfettario/ |
| Gestione Separata 2026 | Aliquota **26,07 %** sul reddito, **nessun minimo fisso**; lo sconto del 35 % "riguarda esclusivamente artigiani e commercianti". | https://quickfisco.it/blog/regime-forfettario/calcolo-gestione-separata-inps-esempi-regime-forfettario/ |

**Cosa significa per te, in pratica (lettura mia delle fonti, da confermare con il professionista):**
1. I ricavi da AdSense/affiliazione sono **commerciali** per tutti i commercialisti trovati → Camera di Commercio (~90 € il primo anno, 57 €/anno dopo) + **INPS commercianti ≈ 3.000 €/anno fissi** con lo sconto forfettario, anche se incassi 1.000 €. Nessuna fonte dice che bastano la Gestione Separata e il tuo codice da fotografo.
2. **Unica porta aperta**: la frase "se accessoria ad attività professionale → Gestione Separata" (Il Commercialista Online). Un sito di contenuto fotografico/visivo collegato alla tua attività di fotografo potrebbe rientrarci; un sito di ricette comprato in Texas, no. È esattamente la domanda da fare a Fiscozen/Flextax (consulenza gratuita), aggiungendo: *"Se compro un sito con pubblicità AdSense da 3.000 €, posso dichiararne i ricavi come accessori all'attività di fotografo in Gestione Separata?"*
3. **Il prezzo del sito non si scarica** (forfettario = niente costi deducibili). Paghi le tasse sul ricavo lordo × coefficiente, anche nell'anno in cui hai speso 5.000 € per comprarlo.
4. **IVA 22 % in più** se il venditore è un'impresa estera e la cessione è una prestazione di servizi B2B: va versata con F24 e non la recuperi. Se il venditore è un privato (non soggetto IVA) non si applica. Quale dei due casi vale per la cessione di un sito **non l'ho trovato scritto da nessuna fonte**: da chiedere nella stessa consulenza. Prudenza: metti in conto +22 % finché non hai la risposta.
5. La regola 2 di REGOLE-FISSE (costi fissi solo dopo gli incassi) qui si scontra con i numeri: l'incasso arriva (è il motivo per cui si compra) ma è più piccolo del costo fisso. Aprire la Camera di Commercio per 1.500-2.500 € di pubblicità all'anno è una perdita secca.

---

## 8. Confronto con l'alternativa: costruire da zero (quello che stai già facendo)

| | Comprare un sito da 5.000 $ | Costruire (EsameB1, EsamiDiStato, Italy Strikes) |
|---|---|---|
| Spesa iniziale | 5.000-6.100 $ + escrow | 0 € (Netlify + AdSense su .netlify.app) |
| Incasso primo anno (prudente) | 1.900-2.300 $ | 0-500 € (verdetti a novembre 2026; Italy Strikes 3-5 k€/anno a 18 mesi) |
| Rischio di perdere il capitale | Alto (truffa, update Google, marchio altrui, AdSense rifiutato) | Zero capitale a rischio: si perde solo tempo di Claude |
| Nodo fiscale | Identico (CCIAA + commercianti) ma con incasso più piccolo del costo fisso | Identico, ma si apre solo quando i ricavi superano il costo fisso |
| Tempo per sapere se funziona | 1-3 mesi (hai già i dati storici) | 6-9 mesi (Google deve indicizzare) |

L'unico vantaggio vero dell'acquisto è il **tempo**: compri dati storici e traffico esistente invece di aspettare Google 6 mesi. Vale qualcosa solo se il prezzo è basso (≤ 2.500 $) e il traffico non dipende da Google.

---

## 9. Le 2 candidate migliori e il piano in 5 passi

Le candidate 2, 4, 5, 6 sono scartate con i dati sopra. Restano la 1 (sito di contenuto/strumento) e, a distanza, la 3 (micro-strumento) — ma la 3 ha il blocco fiscale del software in abbonamento già scritto in REGOLE-FISSE, quindi la ritengo "da riaprire solo dopo il SÌ del professionista". Qui sotto il piano per la 1, nella versione più prudente possibile.

### Candidata 1 — Sito-test da 2.000-3.000 $ su Motion Invest o Investors Club

**Perché questi due**: entrambi mostrano Google Analytics collegato (Motion Invest: visite, DR, punteggio AI, prove di reddito caricate; Investors Club: non accetta siti senza GA + Search Console). Flippa sotto i 50 k$ non verifica nulla.

**Profilo del sito da cercare** (dedotto dai dati di sez. 2.2 e 3):
- prezzo 2.000-3.000 $, profitto 80-130 $/mese, multiplo ≤ 28x;
- **traffico non solo da Google**: Pinterest + Bing + diretto almeno 40 % (molti siti di cucina/casa in vendita sono così), oppure uno **strumento online** (calcolatore, resize immagini) che la gente cerca per usarlo, non per leggere;
- dominio **senza marchi altrui**, età ≥ 2 anni, punteggio AI basso o assente ma con contenuti leggibili (Claude li controlla);
- monetizzazione AdSense o Mediavine Journey (soglia 1.000 sessioni/mese: facile da ri-ottenere), non Ezoic (soglia 250.000 utenti: non la rifai);
- venditore che dà accesso in sola lettura a GA4 e Search Console PRIMA dell'offerta.

**Piano in 5 passi**
1. **Chiudere il nodo fiscale (0 €, 1 settimana)**: consulenza gratuita Fiscozen/Flextax con la domanda di REGOLE-FISSE più le due aggiunte di sez. 7 (accessorietà in Gestione Separata; IVA sull'acquisto da venditore estero). **Se la risposta è "Camera di Commercio + commercianti obbligatori", il piano si ferma qui**: con 3.000 €/anno di costi fissi un sito da 3.000 $ non ha senso, e il capitale va tenuto per scalare ciò che già passa i test (regola 4 del mandato).
2. **Lista corta (0 €, 2 settimane)**: Claude tiene d'occhio le nuove inserzioni (Motion Invest pubblica 5-15 siti al mese; newsletter Investors Club) e scarta tutto ciò che non rispetta il profilo. Target: 3 siti candidati.
3. **Verifica prima di pagare (0 €, 1 settimana per sito)**: accesso GA4 + Search Console in lettura; 24 mesi di traffico (non 3); confronto click Search Console vs sessioni GA (se GA è molto più alto di GSC, c'è traffico comprato); Copyscape su 10 pagine; Ahrefs gratuito sui link; verifica marchio nel dominio; screenshot AdSense confrontati con le date di GA. Claude lo fa in un giorno; il venditore che rifiuta → scartato.
4. **Offerta e pagamento (≤ 3.000 $ + escrow)**: offerta all'82 % del prezzo (è la media di mercato 2025); solo via escrow del marketplace o Escrow.com; trasferimento dominio al tuo registrar PRIMA del rilascio dei fondi; cambio di tutte le password; AdSense/Mediavine Journey ri-richiesti a tuo nome; sito migrato su hosting tuo (Claude).
5. **Gestione e verdetto (12 mesi)**: Claude pubblica 4-8 contenuti/mese + pin, aggiorna i vecchi, controlla Search Console ogni lunedì come per gli altri siti. Verdetto a 6 mesi (sotto).

**Soglie di stop (scritte prima, come chiede la regola di spesa del 10/10)**
- Prima dell'acquisto: nessun accesso in lettura a GA/GSC → stop. Traffico Google > 60 % → stop. Marchio altrui nel dominio → stop. Prezzo > 28x → stop.
- A 3 mesi: profitto medio < 60 % di quello dichiarato → si rimette in vendita (Motion Invest ricompra o rivende in ~11 giorni; perdita attesa 30-50 %).
- A 6 mesi: profitto < 70 % del dichiarato o traffico in calo per 3 mesi di fila → si rivende.
- A 12 mesi: se incasso + valore di rivendita (24x il profitto attuale) < prezzo pagato → nessun secondo acquisto, mai.
- Tetto di spesa complessivo: **un solo acquisto, massimo 3.000 $**, finché il primo non ha superato i 12 mesi in positivo.

### Candidata 3 (riserva) — micro-strumento online con pubblicità, non in abbonamento

Variante che evita il blocco "software in abbonamento": strumenti web gratuiti pagati dalla pubblicità (es. "image resizing tool" a 4.000 $ con 1.104 $/anno su Investors Club; resizeclub.com venduto a 2.350 $ per 100 $/mese su Motion Invest; calcolatori). Fiscalmente è pubblicità come la candidata 1, quindi stesso nodo; tecnicamente Claude può riscriverlo su Netlify a 0 € e non dipende da articoli. Stesso piano e stesse soglie della candidata 1. Da preferire alla 1 se si trova a ≤ 25x con traffico da Bing/diretto.

---

## 10. Cosa NON fare

1. **Non comprare su Flippa sotto i 50.000 $** senza accesso diretto ad Analytics/Search Console: nulla è verificato, e i multipli a 0,2-1,4 anni di profitto dei negozi visti sopra sono il segnale tipico dei numeri falsi.
2. **Non comprare negozi Etsy**: l'account non si trasferisce e il negozio nuovo riparte da zero (e tu ne hai già uno).
3. **Non comprare canali YouTube/TikTok**: AdSense non trasferibile, lavoro di 8-12 h/settimana tuo, rischio di demonetizzazione totale, nessun modo per Claude di produrre video a 0 €.
4. **Non comprare newsletter**: il ricavo dipende dal vendere sponsor con contatti a freddo (regola 3).
5. **Non investire in domini**: 2-3 % venduti l'anno, 15.501 domini in vendita contro 305 siti su Flippa, rendimento mai dimostrato con dati pubblici.
6. **Non comprare siti con marchi altrui nel dominio** (menu di catene, ricette di cuochi famosi): sono una buona parte dell'offerta sotto 5 k$ e si possono perdere con un reclamo.
7. **Non comprare siti nati nel 2025 con punteggio AI alto** solo perché costano poco: sono quelli che Google e gli ad network rifiutano per primi.
8. **Non pagare fuori escrow, mai**, nemmeno "per risparmiare la commissione".
9. **Non comprare prima della risposta fiscale**: con CCIAA + INPS commercianti obbligatori, qualunque acquisto sotto i 10.000 € è in perdita per costruzione.
10. **Non fare un secondo acquisto** finché il primo non ha chiuso 12 mesi in attivo (incasso + valore di rivendita > prezzo).

---

## Appendice — cosa non sono riuscito a leggere (per onestà)

- motioninvest.com: le pagine HTML sono vuote per curl (app JavaScript); i dati vengono dall'API pubblica che la pagina usa (719 record, campi: prezzo, profitto, visite GA, DR, punteggio AI, data di pubblicazione). Letti il 10/10/2026.
- acquire.com/marketplace: 404 senza login. tinyacquisitions.com: errore DNS. namebio.com: 403. fameswap.com: 502 al primo tentativo, ok al secondo. partitaiva.it/?p=109206: 403. bigideasdb.com: 429.
- WebFetch (lo strumento di lettura) ha dato "ENOTFOUND" su molti domini; tutte le pagine citate sono state scaricate con curl e user-agent da browser.
- Nessun marketplace pubblica cosa succede ai siti DOPO la vendita: il "tasso di compratori che ci perdono" resta **non trovato**.
- Testo ufficiale dei Termini YouTube sul trasferimento dei canali e norme YPP 2025 sui contenuti "inautentici": **non verificati in questa ricerca** (fonti solo di broker).
- Trattamento IVA della cessione di un sito da venditore estero privato vs impresa: **non trovato** in fonti italiane; da chiedere al professionista.
