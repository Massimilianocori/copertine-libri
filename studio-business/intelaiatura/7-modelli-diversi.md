# 7. Due modelli diversi: negozi per sviluppatori (A) e siti a pubblicità (B)

*10 ottobre 2026. Ricerca con fonti linkate e datate; status HTTP verificati con `curl` dal server (sez. 6). Dati primari: catalogo Apify Store scaricato dall'API pubblica (10.090 Actor "per rilevanza" + 7.852 "più recenti"), Google Trends (serie 12 mesi e 5 anni, interrogate dal server), Google Autocomplete, pagine ufficiali delle piattaforme.*

## 0. Esito in breve

| Modello | Regge? | Prova decisiva | Migliore progetto concreto | 12 mesi | 18 mesi (run-rate) |
|---|---|---|---|---|---|
| **A – Negozi per sviluppatori** | **Solo Apify, e solo come test passivo a costo zero.** RapidAPI, Chrome, WordPress, GitHub, Zapier/Make, Figma, Notion: NO (prove in sez. 2) | Apify: 1 solo Actor su 1.000 tra i più recenti ha ≥10 utenti negli ultimi 30 giorni; i 20 creatori più grandi hanno il 71% degli utenti paganti; gli Actor su dati pubblici italiani esistenti hanno 2–26 utenti totali (API Store, 10/10/2026) | Pacchetto di 3 Actor su dati pubblici italiani (scioperi MIT, bandi ANAC, carburanti MIMIT) | 100–600 $ | 300–1.500 $/anno |
| **B – Siti a pubblicità** | **Regge solo in inglese per pubblico di Paesi "Tier 1"; NON regge in italiano per l'antismog** | Antismog: "blocco traffico" vale il 4% di "sciopero treni" su Google Italia (Trends 12 mesi) ed è dominato dalle domeniche ecologiche di Roma; RPM Italia reale 3–6 €. Scioperi in inglese: "italy strike" vale il 46% di "sciopero treni" nel mondo, con "italy strike today" come prima query correlata; SERP = articoli di testate e The Local a pagamento | **Sito "Italy strikes today/tomorrow" in inglese** da RSS ufficiale del MIT (fonte unica, 200, aggiornata ogni giorno) | 400–900 € | 3.000–5.000 €/anno |

**Verdetto netto**: aprire prima la famiglia **B in inglese** (sito scioperi), perché costa zero, riusa `genera.py`, ha una fonte ufficiale unica e si misura in 45 giorni con Search Console; Apify si apre **in parallelo come test passivo** (pubblicare 2–3 Actor non costa nulla e i pagamenti scattano solo con il KYC, rinviabile 12 mesi). Nessuno dei due arriva a 10k €/anno con stime prudenti: restano siti/prodotti piccoli da sommare, come i precedenti.

---

## 1. Metodo e limiti

- **Apify Store**: API pubblica [`api.apify.com/v2/store`](https://api.apify.com/v2/store?limit=1) (200). Dichiara `total: 83.854` Actor, ma la paginazione si ferma a ~10.090 risultati per ordinamento; ho scaricato i 10.090 "per rilevanza" e i 7.852 "più recenti" (`sortBy=newest`). Campi usati: utenti totali, utenti negli ultimi 30 giorni, recensioni, modello di prezzo, categorie, creatore. Nessuna data di creazione nel feed: la "coorte dei nuovi" è l'ordinamento `newest`.
- **Google Trends**: interrogato dal server con cookie di sessione (prima chiamata 429, poi 200). Dà solo valori relativi 0–100; l'unico ancoraggio assoluto trovato è uno snippet Semrush (database Italia, agosto–novembre 2025) con "sciopero dei treni" ≈ 18.100 e "sciopero treni" ≈ 9.200 ricerche/mese, testo ambiguo ([it.semrush.com/website/missionline.it](https://it.semrush.com/website/missionline.it/overview)).
- **Ricerca web**: lo strumento restituisce SERP statunitensi; la composizione delle SERP italiane viene dallo studio 6 (10/10/2026).
- **Bloccati**: `WebFetch` (DNS) su tutti i domini → tutto letto con `curl` + estrazione testo. `help.raptive.com` (403), `cgsse.it` (000), `make.com` (403), `github.com/marketplace` (403), `pasqualepillitteri.it` (000). La pagina [apify.com/ideas](https://apify.com/ideas) è un'app React: l'elenco delle idee non è nel sorgente e non ho trovato un endpoint; ho usato le regole ufficiali della pagina e il catalogo come prova delle lacune.
- **Nessuna piattaforma pubblica i ricavi dei singoli**: le cifre di guadagno sono (a) marketing delle piattaforme, (b) post di singoli senza verifica, (c) annunci di vendita su Flippa. Lo dico caso per caso.

---

## 2. MODELLO A – Negozi dove lo sviluppatore vende e la piattaforma incassa

### 2.1 Tabella delle regole (verificate il 10/10/2026)

| Negozio | Chi vende all'acquirente | Commissione | Payout | Approvazione | Stato per un nuovo entrante |
|---|---|---|---|---|---|
| **Apify Store** | **Il creatore**: «Each Actor is made available directly to Users by you, and the contractual relationship … is established between you and the User, not between Apify and the User» ([Store Publishing Terms §4.1](https://docs.apify.com/legal/store-publishing-terms-and-conditions), agg. 26/2/2025) | **20%** sulle somme pagate dagli utenti, più i costi piattaforma dei run (§10.2.1); sconti promozionali a carico del creatore (§10.2.3) | Fattura auto-generata dalla piattaforma l'11 di ogni mese (self-billing), 3 giorni per contestarla; minimo **20 $ PayPal / 100 $ bonifico**; bonifico SWIFT dalla Rep. Ceca con spese 10–50 $ a carico del creatore; saldi sotto soglia o senza KYC per 12 mesi **decadono** (§10.1.6, §10.3.2; [payouts](https://docs.apify.com/platform/actors/publishing/monetize/monthly-payouts)) | Pubblicazione immediata; test automatico giornaliero (run ≤5 min con output non vuoto) ([docs](https://docs.apify.com/academy/scraping-with-ai/before-publishing-to-apify-store)); nessuna revisione manuale documentata | Modelli attivi: **pay-per-event** e pay-per-usage; il **rental** non è più nella pagina ufficiale ([monetize](https://docs.apify.com/platform/actors/publishing/monetize)); terze parti: stop nuovi rental 1/4/2026, ritiro 1/10/2026 ([use-apify](https://use-apify.com/docs/apify-for-developers/monetize-actors)) |
| **RapidAPI Hub** (Nokia dal 11/2024) | Rapid incassa, il provider riceve un payout | **25% dal 15/11/2025** (era 20%): «The marketplace fee on all payments made through the API Hub will be %25» ([docs](https://docs.rapidapi.com/docs/payouts-and-finance), agg. ~11 mesi fa) | **Solo PayPal**; pagato alla fine del mese successivo (es. abbonamenti di gennaio pagati la prima settimana di marzo); W9 su richiesta | n/d | Recensioni Trustpilot 2025–26 sull'aumento «senza preavviso» e payout in ritardo ([trustpilot](https://www.trustpilot.com/review/rapidapi.com?page=2)) |
| **WordPress.org** | Il plugin gratuito non si vende; la versione Pro va venduta altrove (Freemius ~7% + gateway, o Stripe proprio) | 0% (nessun pagamento gestito) | – | Coda revisione: picco ~1.050 plugin ad aprile 2026, azzerata a giugno 2026 ([make.wordpress.org, giugno 2026](https://make.wordpress.org/?p=154)); l'avviso standard dice «almeno 12 giorni» ([meta.trac](https://meta.trac.wordpress.org/ticket/7801)) | **70.934 plugin** nel repository ([API wp.org](https://api.wordpress.org/plugins/info/1.2/?action=query_plugins), 10/10/2026); conversione free→Pro 1–2% ([Freemius](https://freemius.com/blog/increase-freemium-upgrades-wordpress-plugin-theme/)) |
| **Chrome Web Store** | Lo sviluppatore, con un proprio sistema di pagamento | Google non gestisce pagamenti dal 1/2/2021 ([neowin](https://www.neowin.net/news/google-is-permanently-removing-paid-extensions-from-the-chrome-web-store/)) | – | Revisioni accelerate dall'agosto 2026 ([blog Chrome](https://developer.chrome.com/blog/cws-review-updates-2026)) | Su 112 estensioni con ricavi noti: **57% guadagna zero, 6,3% supera 1.000 $/mese** (fonte: venditore di SDK di pagamento, [konabayev 2026](https://konabayev.com/blog/extension-monetization-statistics-2026/)); mediana **18 utenti** per estensione (Exstats, citato da [fungies](https://fungies.io/monetize-chrome-extension-2026)) |
| **Figma Community** | Il creatore; Figma è "marketplace facilitator" per le imposte sulle vendite | 15% | Stripe; Italia supportata; W-8BEN obbligatorio | **CHIUSO**: «We are not approving new creators to sell paid files on Community at this time» ([help.figma.com](https://help.figma.com/hc/en-us/articles/12067637274519), letto 10/10/2026; conferma nel forum, agosto 2026) | Non accessibile |
| **Notion Marketplace** | Il creatore; Notion gestisce IVA/sales tax; «creators are responsible for … income taxes» | **8% + 0,40 $** per transazione, +1% cambio per non-USA | Stripe, ogni due settimane, minimo 20 $, fondi trattenuti 14 giorni; Italia nell'elenco dei Paesi ([notion.com/help](https://www.notion.com/help/selling-on-marketplace)) | Lista d'attesa: «it may take a few months to get reviewed» | Nessun dato di vendite di singoli oltre al marketing (Thomas Frank, cifre discordanti 1–2,5 M$ su [fungies](https://fungies.io/?p=37753)) |
| **GitHub Marketplace** | Lo sviluppatore | 5% (95% allo sviluppatore dal 2021, [github.blog](https://github.blog/news-insights/company-news/github-reduces-marketplace-transaction-fees-revamps-technology-partner-program/)) | – | «only apps owned by **organizations** can sell their app» + publisher verification + onboarding finanziario ([docs](https://docs.github.com/en/apps/github-marketplace/github-marketplace-overview/about-github-marketplace-for-apps)) | Non per un singolo; le Actions non si vendono |
| **Zapier / Make / n8n template** | – | – | – | – | **Nessun programma di template a pagamento**: la pagina [zapier.com/templates](https://zapier.com/templates) elenca solo template gratuiti; n8n offre un "Verified Creator Badge" e un'affiliazione 30% ([n8n.io/creators](https://n8n.io/creators/)); Make: gallery gratuita (403 dal server). Si vendono solo fuori (Gumroad, siti terzi) |

**Conclusione sulle regole**: di 8 negozi, **uno solo** (Apify) incassa, paga e porta traffico a prodotti di dati/automazione; Notion è accessibile ma vende design, non dati; RapidAPI è accessibile ma al 25% con solo PayPal e segnali di degrado; gli altri sono chiusi, senza pagamenti o riservati a organizzazioni.

### 2.2 Apify Store: prove di guadagno, come arriva il traffico, saturazione (dati primari)

**Cosa dichiara Apify (marketing, non verificabile):** «$1.6M paid out last month. Many developers earn over $3k» (menu del sito, 10/10/2026); «the most successful independent creators … make over $10,000 monthly recurring revenue. Many others make more than $1,000 every month» ([help, 22/10/2025](https://help.apify.com/en/articles/8684010-make-money-publishing-your-actors-on-apify-store)); «In September alone, Apify paid out $563k» e «more than $4 million … since launching» ([challenge, fine 2025](https://apify.com/challenge); [press release 11/2025](https://natlawreview.com/press-releases/apify-bets-1m-independent-developers-building-ais-missing-tools)). Terze parti: ~1,4 M$/mese su ~3.000 sviluppatori ≈ **470 $/mese di media**, «heavily skewed» ([reinventing.ai 2026](https://www.reinventing.ai/blog/apify-actor-passive-income)).

**Unico racconto di un singolo con numeri (senza ricavi):** «98 production Actors in 6 months»: 2.500 utenti totali, 855 attivi al mese, «I'm not going to post revenue here»; i mercati grandi (LinkedIn, Amazon, Instagram) hanno «5 to 15 competing Actors per major site, several … maintained by Apify itself»; i suoi successi sono siti di nicchia europei (Welcome to the Jungle 60 utenti, Skool 45) ([blog.apify.com, 2026](https://blog.apify.com/building-98-actors-on-apify-store/)). 98 Actor per 855 utenti attivi = **~9 utenti attivi per Actor**.

**Cosa dice il catalogo (API Store, 10/10/2026, `dati` in scratchpad):**

| Misura | Valore |
|---|---|
| Actor nei 10.090 "per rilevanza" | 9.763 a pagamento (97% pay-per-event), 327 gratuiti |
| Utenti negli ultimi 30 giorni, per Actor | **mediana 4**, 90° percentile 57, 99° 1.141; 615 Actor a zero |
| Actor a pagamento con ≥10 / ≥100 / ≥1.000 utenti in 30 gg | 3.173 / 662 / **104** |
| Concentrazione | 1.518 creatori con Actor a pagamento; **i primi 20 hanno il 71% degli utenti-30gg**; `apify` da solo il 31% (266.989 su 862.603) |
| Coorte "più recenti" (7.852 Actor) | utenti totali: **mediana 2**; utenti-30gg: mediana 1. **Nei 1.000 più recenti: 1 solo Actor con ≥10 utenti in 30 gg, 0 con ≥50, 5 con una recensione**. Tra il 1.001° e il 3.000°: 185 con ≥10 e 61 con ≥50 |
| Ritmo di uscita | i 1.000 Actor più recenti hanno tutti l'ultimo run in ottobre 2026 (996/1.000): il flusso di nuovi è di **centinaia a settimana** (il `total` dichiarato è 83.854 contro 26.929 ad aprile 2026 secondo [vantaige](https://vantaige.io/ai-tool/apify)) |
| Categorie più affollate | Automation 4.106, Lead generation 3.888, Developer tools 2.677, Social media 2.589, E-commerce 1.892, AI 1.139, Real estate 871, Jobs 856 |

**Come arriva il traffico**: ricerca interna per nome/descrizione, categorie, ordinamenti (popolarità = utenti), badge e recensioni, più la SEO delle pagine Actor su Google. La pagina [ideas](https://apify.com/ideas/how-it-works) regala al primo che realizza un'idea un **backlink** dalla pagina ("SEO juice"). Apify stessa chiede al creatore di promuovere su Reddit, Product Hunt, YouTube ([monetize](https://docs.apify.com/platform/actors/publishing/monetize)). Il dato della coorte dice che **senza promozione un Actor nuovo resta a 1–2 utenti**.

**Saturazione e lacune sui dati italiani** (ricerca nel catalogo, 10/10/2026; utenti totali / ultimi 30 gg):

| Fonte italiana | Actor esistenti | Il migliore | Lettura |
|---|---|---|---|
| idealista (ES/IT/PT) | 45 pertinenti | 2.458 / 366 | occupato (3 Actor >150 utenti/mese) |
| immobiliare.it | 46 | 698 / 69 e 471 / 111 | occupato |
| subito.it | 45 | 186 / 40 | occupato a livello basso |
| autoscout24 | 43 | 875 / 44; 330 / 100 | occupato |
| paginegialle | 15 | 169 / 11 | occupato, domanda piccola |
| registro imprese / bilanci | 7 | 91 / 11; 50 / 12 | occupato, domanda piccola |
| aste giudiziarie PVP | 7 | 26 / 3; 22 / 5 | esiste, quasi nessun utente |
| **ANAC / bandi / gare** | 4 + 8 | **18 / 3** | esiste, quasi nessun utente |
| trenitalia | 4 | 15 / 7 | quasi nessun utente |
| carburanti MIMIT | 2 | 2 / 1 | quasi nessun utente |
| **scioperi, ZTL, albo pretorio, catasto, Agenzia Entrate, INPS, farmacie** | **0** | – | vuoto, ma i vicini sopra dicono che la domanda su Apify per dati pubblici italiani è di **decine di utenti**, non di migliaia |

Esempio di prezzo reale: il TikTok Scraper (322.371 utenti) chiede 3,7 $ per 1.000 risultati sul piano Free e 0,5 $ sul piano Diamond (tariffe a scaglioni nel feed API). Un Actor di dati pubblici italiani con 20 utenti al mese che spendono 5 $ ciascuno = 100 $ lordi → **80 $ di payout** meno i costi di run.

**Lacune con richieste senza offerta**: non ho potuto leggere l'elenco delle idee (app JS). Le lacune verificabili sono quelle del catalogo qui sopra (scioperi MIT: 0 Actor; ZTL: 0; albo pretorio: 0) e, dal blog del creatore dei 98 Actor, i siti regionali europei senza scraper. Nessuna "richiesta con voti" verificabile → questa parte del punto (5) resta **non provata**.

### 2.3 Cosa può costruire Claude e manutenzione

- **Fattibile da solo**: Actor pay-per-event in Python/JS su fonti pubbliche già lette per gli studi precedenti: scioperi (RSS MIT, 200), bandi ANAC (JSON/CSV open data), prezzi carburanti MIMIT (CSV giornaliero), bollettini ARPA, Gazzetta Ufficiale concorsi, PVP aste. Costo di costruzione: 3–6 h per Actor; i costi di run sono a carico dell'utente o detratti dal payout.
- **Manutenzione**: test automatico giornaliero di Apify (se fallisce, l'Actor viene segnalato e perde il diritto al payout finché è "Faulty", §10.2.2); risposte ai problemi degli utenti (il profilo pubblica il tempo di risposta; «under 12 hours earns repeat buyers»). Per fonti ufficiali stabili (RSS, CSV) la manutenzione è di ~1 h/mese; per siti commerciali (immobiliare, subito) di ore a ogni cambio di layout.
- **Fiscale per un italiano**: il creatore è il venditore verso utenti di tutto il mondo (§4.1); la fattura è emessa dalla piattaforma per conto del creatore (self-billing, §10.3.1) e il pagamento parte da Apify Technologies s.r.o., Praga (VAT CZ04788290); il KYC può chiedere «tax documentation» (§10.1.2). È vendita continuativa di servizi a molti clienti → **stesso nodo della regola 2** (P.IVA/CCIAA): va nella stessa domanda a Fiscozen/Flextax. Punto a favore: si può pubblicare e misurare senza KYC; i saldi si accumulano e decadono solo dopo 12 mesi (§10.1.6).

### 2.4 Stima prudente, 2–3 prodotti concreti su Apify

Assunzioni dalla coorte: un Actor nuovo senza promozione fa 1–2 utenti/mese; con README curato e nicchia scoperta (i casi WTJ/Skool del blog) 10–60 utenti/mese dopo 3–4 mesi; spesa media per utente 2–5 $ (gli utenti di dati pubblici sono piccoli); 80% al creatore.

| Prodotto | Mese 6 (utenti/mese) | Mese 12 | Payout 12 mesi | Run-rate 18 mesi |
|---|---|---|---|---|
| Italy Strikes API (RSS MIT → JSON, oggi/domani/mese) | 3–8 | 5–15 | 30–150 $ | 100–400 $/anno |
| ANAC/bandi (gare per CPV/regione/importo) | 5–15 | 10–25 | 50–300 $ | 150–700 $/anno |
| Carburanti MIMIT (prezzi per comune, serie storica) | 2–6 | 4–10 | 20–150 $ | 50–400 $/anno |
| **Totale** | | | **100–600 $** | **300–1.500 $/anno** |

Il 90° percentile della coorte "nuovi" (8 utenti/mese tra il 1.001° e il 3.000°) conferma l'ordine di grandezza. Chi supera i 1.000 $/mese ha decine di Actor mantenuti e un canale promozionale.

### 2.5 Gli altri negozi, in una riga ciascuno (perché no)

- **RapidAPI**: 25% + PayPal + payout a 60 giorni; nessun guadagno di singolo verificabile; Trustpilot 2025–26 con payout mancanti ([pagina 2](https://www.trustpilot.com/review/rapidapi.com?page=2)). Un'API di dati pubblici italiani si vende meglio come Actor (stesso lavoro, 20% invece di 25%, pagamento bonifico).
- **WordPress.org**: 70.934 plugin; il repository non porta vendite ma installazioni; la Pro si vende da soli (fiscale pieno); conversione 1–2%. Serve il mercato WooCommerce italiano già studiato (H-software-marketplace.md: 200–1.000 €/mese dopo anni).
- **Chrome**: nessun pagamento in store, mediana 18 utenti, 57% a zero; serve Stripe proprio e assistenza.
- **Figma**: chiuso ai nuovi venditori. **Notion**: 8% + 0,40 $, lista d'attesa di mesi, prodotto di design; per Claude senza gusto umano verificato è un azzardo senza dati. **GitHub**: solo organizzazioni. **Zapier/Make**: non esiste la vendita.

---

## 3. MODELLO B – Siti ad alto traffico monetizzati con pubblicità

### 3.1 RPM, soglie, tempi, AI Overview (fonti 2025–2026)

**RPM per Paese (per 1.000 pagine viste).** Modello di [adstimate](https://adstimate.com/blog/country/italy-adsense-rpm.html) (agg. 29/7/2026, «calculated estimates from our own RPM model, not a survey»): **Italia 10,50 $** base, USA 20 $, UK 16 $, Germania 14 $, Spagna 10 $; Finanza ×3, Software ×2,4, Tech ×1,8; Q4 +35%, Q1 −18%. **Dati reali di singoli**: blog salute francese con AdSense **3,11 € di RPM** medio prima di passare a Journey (30.000 sessioni/mese, [kinedarbois, 8/8/2024](https://kinedarbois.fr/en/2024/08/08/blog-income-report-journey-by-mediavine/)); blog viaggi su Copenhagen con Journey: **7,50 $ il primo mese, 12,69 $ medio nei primi 90 giorni**, 717 $ in 90 giorni ([danny-cph, 2025](https://danny-cph.com/?p=6835)); benchmark viaggi Mediavine/Raptive/Ezoic 6–18 $ ([earnifyhub 2026](https://earnifyhub.com/blog/blogging/blog-display-ad-rpm-by-niche-2026), campione non dichiarato); stime generiche 5–10 $ per 1.000 visitatori ([ranktracker](https://www.ranktracker.com/it/blog/adsense-earnings-by-traffic-threshold-how-much-can-you-earn/)). **Regola prudente usata qui: Italia 3–6 € (notizie/auto), inglese Tier 1 con AdSense 8–12 $, con Journey/Raptive 12–18 $.**

**Soglie di ammissione (verificate):**

| Rete | Requisito | Fonte |
|---|---|---|
| **AdSense** | nessuna soglia di traffico; pagamento da 100 $ ([support.google.com](https://support.google.com/adsense/answer/9724), 200) | – |
| **Journey by Mediavine** | **≥1.000 sessioni in 30 giorni da Paesi Tier 1 (USA, Canada, UK, Australia)** | [mediavine.com/mediavine-requirements](https://www.mediavine.com/mediavine-requirements/) (200, letta 10/10/2026); terze parti: in vigore dal 15/1/2026, quota al publisher 70% (non confermata); quota standard Mediavine 75% ([revenue share](https://www.mediavine.com/?p=14516)) |
| **Mediavine** | ≥5.000 $/anno di ricavi pubblicitari | stessa pagina |
| **Raptive** | **≥25.000 pagine viste/mese** (da 100.000, annuncio 16/10/2025, [ppc.land](https://ppc.land/raptive-drops-pageview-requirement-to-25-000-monthly-visits/)); 50% del traffico da USA/UK/CA/NZ/AU sotto le 100k pagine (40% sopra); dominio ≥6 mesi; GA4 | [help.raptive.com](https://help.raptive.com/hc/en-us/articles/360032840891-How-do-I-apply-to-Raptive) (403 dal server, citata nei risultati di ricerca) |
| **Ezoic** | **≥250.000 utenti/mese** dal 19/2/2026 (prima ~10.000); Incubator: 20 siti al mese | [support.ezoic.com](https://support.ezoic.com/kb/article/getting-started-ezoics-requirements), [ezoic.com/incubator](https://www.ezoic.com/incubator) (200) |

Conseguenza: per un sito **italiano** nuovo l'unica rete è AdSense (Journey conta solo sessioni Tier 1, Ezoic è chiuso). Per un sito **in inglese** su pubblico USA/UK/CA/AU si entra in Journey a 1.000 sessioni e in Raptive a 25.000 pagine.

**Tempi per arrivare a 50k visite/mese con solo SEO.** Nessuno studio solido: il 96,55% delle pagine non riceve traffico da Google ([Ahrefs, 12/2023](https://ahrefs.com/blog/search-traffic-study/)); case study di programmatic SEO con «flat first half and compounding after roughly month 6» su 512 pagine ([thestacc, 5/2026](https://thestacc.com/blog/programmatic-seo-case-study/), fonte commerciale); stime da blog «1–3 anni per il primo mese da 10k». Google ha colpito i siti programmatici sottili a marzo 2026 (perdite 50–90% raccontate da autori, nessun dataset: [alexcloudstar](https://www.alexcloudstar.com/blog/programmatic-seo-2026-indie-hackers/)); la policy "scaled content abuse" riguarda l'intento, «a programmatically generated page with real data is fine». **Dato nostro in arrivo**: EsameB1 e EsamiDiStato danno il primo numero reale il 23–24/11/2026.

**AI Overview.** Esperimento randomizzato: **−39,8% di clic** in uscita quando compare un AIO ([SSRN, 4/2026, via ppc.land](https://ppc.land/researchers-find-google-ai-overviews-cut-publisher-clicks-39-8/)); Ahrefs: −58% di CTR per la prima posizione ([12/2025](https://ahrefs.com/blog/ai-overviews-reduce-clicks-update/)); Pew: clic 8% con AIO contro 15% senza; Chartbeat: referral Google −33% su 2.576 testate tra 11/2024 e 11/2025 ([DCN, 10/2026](https://digitalcontentnext.org/blog/2026/10/05/the-evidence-is-clear-ai-search-is-costing-publishers/)); Semrush: AIO nel 15,69% delle query (11/2025), Sistrix DE 20% ([keywordseverywhere tracker](https://keywordseverywhere.com/news/ai-overviews/)). Per tipo: domande 85,9% e confronti 95,4% con AIO ([Seer 2026](https://seerinteractive.com/insights/aio-impact-on-google-ctr-2026-update)); **nessuno studio separa strumenti/calcolatori o pagine "oggi/domani"**: la resistenza di queste pagine è un'ipotesi ragionevole (l'AIO non può calcolare né leggere il bollettino di stamattina), non un dato. Va misurata con Search Console.

**Prove di siti di singoli con numeri pubblici.** calculator.net/unitconverters.net (Maple Tech, un fondatore: «ad revenue was higher than his salary», nessuna cifra, [Google case study](https://www.google.com/ads/publisher/stories/maple_tech/)); The Calculator Site: 3,8 M utenti/mese dal 2004 ([argh](https://www.argh.com/?p=33)); Omni Calculator: 15–18 M visite/mese, azienda con redattori ([Semrush 8/2025](https://www.semrush.com/website/omnicalculator.com/overview/)); Convert Case: «well over 5 figures every month» (autodichiarato, 3/2024). Flippa (dichiarati dal venditore): sito di calcolatori del 2020 a **186 $/mese di profitto** (agosto 2026, [flippa](https://flippa.com/13553326)); convertitore con 91.214 pagine viste/mese ≈ 800 $/mese ([flippa](https://flippa.com/11593531)); sito da 400.522 pagine/mese = 858 $/mese (2,1 $ di RPM). **Lettura**: i grandi sono aziende nate 10–20 anni fa; i piccoli valgono 2–9 $ per 1.000 pagine.

**Fiscale AdSense per un italiano.** Google Ireland Ltd (VAT IE6388047V) è il cliente; fattura senza IVA in inversione contabile art. 7-ter, iscrizione VIES; sotto 4.800 €/anno c'è chi dichiara come redditi diversi (quadro RL) ma «non è del tutto corretto» perché l'attività è continuativa ([money.it, 5/6/2026](https://www.money.it/Guadagni-AdSense-come-fatturare-fisco)); codice ATECO 73.11.02 con coefficiente **78%** in forfettario; le guide per blogger indicano **iscrizione alla Camera di Commercio (~80 €/anno) e Gestione Commercianti INPS (contributi fissi ~4.800 €/anno)**, con la Gestione Separata solo se la pubblicità è accessoria ([quickfisco](https://quickfisco.it/blog/regime-forfettario/regime-forfettario-blogger/), [Il Commercialista Online](https://www.ilcommercialistaonline.it/?p=190)). Nessuna ritenuta: Google non trattiene nulla. **È lo stesso nodo della regola 2**: la domanda da fare a Fiscozen/Flextax va estesa ad AdSense. Fino al primo pagamento (100 $) non c'è nulla da aprire.

### 3.2 Candidata a) Antismog "posso circolare oggi a [città]" (italiano) — NON REGGE come sito a pubblicità

- **Domanda misurata** (Trends Italia, 12 mesi al 10/10/2026): "blocco traffico" media **1,0** contro "sciopero treni" **23,6** (stessa scala) → **~4%**; su 5 anni 1,3 contro 15,9 (~8%). "euro 5 diesel" media 3,1 con picco 33 nella settimana 6–12/9/2026 (rinvio nazionale); "semaforo antismog" **0**. Le query correlate di "blocco traffico" sono per l'82% **Roma** ("blocco traffico roma" 100, "roma oggi" 17, "domenica ecologica roma" 16; Milano 12, Torino 11, Padova 6): la domanda è fatta soprattutto dalle **domeniche ecologiche di Roma**, eventi annunciati con settimane di anticipo e coperti da Roma Mobilità e da tutte le testate. Stagionalità confermata (picchi dicembre–febbraio: 92 il 1–7/1/2023, 97 il 28/1–3/2/2024), ma l'inverno 2025–26 è stato più basso (57 e 51).
- **Stima pagine viste**: con l'ancoraggio Semrush ("sciopero treni" 9–18k/mese per le due varianti) la famiglia "blocco traffico" vale **1–3k ricerche/mese in media, 4–8k nei mesi di picco**, concentrate su Roma. Un sito nuovo in posizione 3–6 sotto testate e Roma Mobilità prende il 5–10%: **150–600 visite/mese in inverno, 3–6k pagine viste a stagione**. È coerente con le 35–45k visite/anno stimate nello studio 6 come tetto ottimistico.
- **Ricavi**: 5k pagine × 3–6 € = **15–30 €/stagione**; anche con 45k visite/anno = 100–300 €/anno. RPM auto/notizie in Italia, Q1 −18%.
- **Fonti dati**: 5 bollettini di cui 3 app JS (studio 6, sez. 2.2) → 25–35 h di costruzione per un sito da 100–300 €/anno. **Bocciata** come sito a pubblicità. Resta valida solo come **sezione** di un sito "oggi/domani" più ampio in italiano (scioperi + blocchi + domeniche ecologiche), dove le pagine Roma costano 2 h e non 30.

### 3.3 Candidata c) "Italy strikes today / tomorrow" in inglese — LA MIGLIORE

- **Domanda** (Trends, 12 mesi): nel mondo "italy strike" media **2,6** contro "sciopero treni" **5,6** e "sciopero" 28,5 → l'inglese vale il **46% del termine italiano "sciopero treni"**. USA: "italy strike" 39,5 e "italy strikes" 19,1 (stessa scala), "italy strike today" 3,3; Canada: "italy strike" 24,5; Australia 8,8 con picco 100 nella settimana 16–22/8/2026; UK: "italy strikes" 16,6 con 33 settimane su 53 sopra 10. **Prima query correlata nel mondo: "italy strike today" (100)**, poi "italy strikes" (26) e la data specifica "italy strike may 29"; negli USA le correlate sono "italy strikes june 2026" e "may 2026" (le persone cercano il mese del viaggio). Autocomplete USA/UK: "italy strike tomorrow", "italy train strike tomorrow", "italy airport strike tomorrow", "rome strike today", "milan strike tomorrow", **"italy strike website"** (cercano un sito dedicato), "italy transport strike dates".
- **Stima assoluta** (ancoraggio Semrush, prudente): famiglia inglese ("italy strike/strikes", "italy train/transport/airport strike", "rome/milan strike", mese+anno) ≈ **8–20k ricerche/mese**, da Paesi Tier 1, con picchi nei mesi di viaggio e nei giorni di sciopero generale.
- **SERP** (ricerca 10/10/2026 "italy strike today", "italy train strike tomorrow", "italy strikes october 2026"): articoli di testate per singolo sciopero (Wanted in Rome, Travel Gossip, Euronews, AA, ANSA English), **The Local Italia a pagamento** («Members only … Become a member or log in to continue reading», [calendario maggio 2026](https://www.thelocal.it/20260429/calendar-the-transport-strikes-to-expect-in-italy-in-may-2026), 200), blog di viaggio con calendari mensili (visitworld, pixidia, stampednomad) che si **contraddicono sulle date** (es. 16/10/2026: easyJet secondo il registro MIT per stampednomad; Pisa/Firenze per pixidia). **Nessuna pagina che legga il registro ufficiale e dica "oggi/domani/questa settimana, per settore e città" in inglese.**
- **Fonte dati**: una sola, ufficiale, pubblica: il prospetto del MIT [scioperi.mit.gov.it](https://scioperi.mit.gov.it/mit2/public/scioperi) (200, HTML 30 KB) con **RSS** ([rss](https://scioperi.mit.gov.it/mit2/public/scioperi/rss), 200) che per ogni sciopero dà inizio, fine, settore (aereo, ferroviario, TPL, marittimo, merci, taxi…), rilevanza (nazionale/regionale/locale), regione, provincia, sindacati, modalità (ore), data di proclamazione, revoche. Aggiornato ogni giorno ("aggiornato alla data: 10/10/2026"). Fasce di garanzia: pagine Trenitalia/Italo/ATM (link, non da ricopiare).
- **Cosa fa Claude**: lettura RSS ogni ora (GitHub Actions) → `genera.py` con pagine: oggi, domani, settimana, mese corrente e prossimo (le query "june 2026"), per settore (trains / flights / airports / local transport / ferries / taxi), per città (Rome, Milan, Florence, Venice, Naples, Bologna, Turin, Pisa…), per aeroporto, "general strike"; ogni pagina con fonte, data di proclamazione, link alle fasce di garanzia, avviso email gratuito "strikes on my travel dates". Nessun verdetto personale: si riporta il registro.
- **Ore**: **10–15 h** (lettore RSS 2 h, modello dati 2 h, adattamento `genera.py` 4–6 h, pagine statiche "how strikes work in Italy / guaranteed trains / refunds" 2–3 h, modulo avviso 1–2 h). Manutenzione: ~0; 1 h al cambio di formato del feed.
- **Concorrenza e rischi**: The Local e Wanted in Rome hanno autorità e un articolo per ogni sciopero; Google può mostrare "Top stories"; AIO possibile sulle domande generiche ("do strikes affect trains in Italy") ma non sul "today"; Trenitalia/Italo hanno pagine ufficiali in inglese; stagionalità (estate alta). Responsabilità: nulla (dati ufficiali riportati con fonte e ora).
- **Ricavi prudenti** (AdSense 8–12 $ fino a Journey; Journey/Raptive 12–18 $ dopo): mese 6 ≈ 3–6k pagine viste; mese 12 ≈ 8–15k (≈ 60–150 €/mese); **12 mesi ≈ 400–900 €**; 18 mesi a 20–30k pagine/mese con Journey/Raptive ≈ 250–450 €/mese → **3–5k €/anno**. Non contati: affiliazione biglietti/assicurazioni e la lista email (fase 2).

### 3.4 Candidata b) Strumenti in inglese con SERP debole — SOLO COME SATELLITI

Sondaggio Autocomplete + Trends (USA/UK, 10/10/2026):

| Strumento | Domanda | SERP | Giudizio |
|---|---|---|---|
| **Codice fiscale calculator (per stranieri)** | "codice fiscale" USA media 7,4 (contro "italy strike" 11,9), UK 35,7 (scala UK), Canada 5,9; correlate USA: "codice fiscale italy", "online", "calcolo", "in english", "generator", "inverso"; autocomplete: "codice fiscale calculator for foreigners / temporary / estero" | pagine spinte ("Calculator Codice Fiscale" clonate), codicefiscaleai.it, quifinanza, guide ESN; nessun calcolatore "per stranieri" con spiegazione in inglese e codici Belfiore dei Paesi esteri in primo piano | **SÌ come satellite**: algoritmo pubblico, 2–4 h, zero responsabilità (si dichiara che il codice ufficiale lo assegna l'Agenzia); 1–3k visite/mese possibili; 20–60 €/mese |
| Italy ZTL (zone, map, app, fine) | "italy ztl" USA media 6,0; "ztl fine" Trends 0 (troppo piccola), autocomplete ricco ("ztl fine florence", "how to pay ztl fine italy", "italian traffic fines debt collection") | forum Rick Steves, blog 2009–2022, Italy Handbook; nessun motore ufficiale | SÌ come pagine informative per città (orari dai siti comunali: lavoro manuale, no dataset) ma **"italy traffic fine" media 0,2**: niente traffico per uno strumento |
| Italy public holidays 2027 | USA media 7,1 | timeanddate, officeholidays (fortissimi) | NO |
| Schengen 90/180 calculator, ETIAS, UK ETA | ricche ma servite da siti ufficiali UE/UK e decine di calcolatori | NO |
| Notice period / UAE salary / Ireland pension calculator | servite (gov, banche, Zurich) | NO |
| Carburanti/"load shedding"/"fuel price today" Kenya-Nigeria-Pakistan | domanda enorme ma RPM Tier 3 (2–10 $ dichiarati per "tier 2/3", [arbhunter](https://arbhunter.dev/blog/best-countries-ad-arbitrage-2026)) e testate locali | NO |

**Lettura strutturale**: dove la SERP è debole il Paese ha RPM basso; dove l'RPM è alto (USA/UK) la SERP è presidiata. L'eccezione utile è **"l'Italia spiegata in inglese a chi viaggia o si trasferisce"**: pubblico Tier 1, SERP di forum e blog vecchi, fonti italiane ufficiali che Claude legge già. Scioperi (c) e codice fiscale (b) sono lo stesso sito.

### 3.5 Pagine "dati locali aggiornati" in italiano: "sciopero oggi [città]" — da tenere in riserva

Trends Italia 12 mesi: "sciopero treni" 23,6, "sciopero oggi" 10,3, "sciopero domani" 6,7, "sciopero mezzi" 5,5 (scala comune); correlate: "sciopero treni giugno/maggio/febbraio…" (mese) e date esatte in forte crescita ("sciopero treni marzo 2026" +347.550%). Domanda **4–8 volte** quella inglese, ma SERP italiana presidiata (insella, Telepass Moveo, Il Sussidiario, Today, Il Sole 24 Ore, Trenitalia) e RPM 3–6 €. Stesso motore del sito inglese: **versione italiana = +20% di lavoro**, da aprire solo se il sito inglese passa il test (misura reale di indicizzazione e RPM).

---

## 4. Classifica unica, verdetto, test

### 4.1 I migliori 5 progetti concreti

| # | Progetto | Modello | Ore | Spesa | 12 mesi | 18 mesi (run-rate) | Prova principale |
|---|---|---|---|---|---|---|---|
| **1** | **Italy strikes today/tomorrow (inglese)** da RSS MIT | B (c) | 10–15 | 0 € | 400–900 € | **3–5k €/anno** | Trends: 46% di "sciopero treni" nel mondo; "italy strike today" prima correlata; The Local a pagamento; fonte unica RSS 200 |
| 2 | Satelliti "Italy in English": codice fiscale calculator per stranieri, ZTL per città, "how to pay an Italian fine" (informativo) | B (b) | 6–10 | 0 € | 150–400 € | 0,5–1,5k €/anno | "codice fiscale" USA 7,4 / UK 35,7; SERP di pagine clonate e forum |
| 3 | Pacchetto Apify: Italy Strikes API + ANAC bandi + carburanti MIMIT (stessi lettori del #1) | A | 10–18 | 0 € | 100–600 $ | 300–1.500 $/anno | catalogo: 0 Actor scioperi/ZTL, ANAC 18 utenti; coorte nuovi 1/1.000 ≥10 utenti |
| 4 | Versione italiana del #1 ("sciopero oggi/domani città") + sezione blocchi antismog Roma/Milano/Torino | B | +8–12 | 0 € | 100–400 € | 1–2k €/anno | domanda 4–8× l'inglese ma RPM 3–6 € e SERP presidiata; antismog da sola 100–300 €/anno |
| 5 | Template Notion (dati pubblici italiani → database pronti) | A | 10+ | 0 € | 0–200 $ | n/d | 8% + 0,40 $, lista d'attesa di mesi, nessun dato di vendite di singoli: non misurabile prima di mesi |

### 4.2 Verdetto

**Aprire prima la famiglia B, in inglese, col progetto 1.** Motivi con prove: (i) è l'unica candidata con fonte ufficiale unica e aggiornata ogni giorno (RSS MIT, 200) e nessun motore "oggi/domani" in inglese nella SERP; (ii) pubblico Tier 1 (USA/Canada/UK/Australia) → RPM 8–18 $ invece di 3–6 € e accesso a Journey da 1.000 sessioni; (iii) 10–15 h con `genera.py`, zero spesa, zero responsabilità, zero assistenza; (iv) si misura in 45 giorni con Search Console come EsameB1. La famiglia A **non si scarta ma si retrocede a test passivo**: gli stessi lettori (RSS MIT, ANAC, MIMIT) diventano 3 Actor pubblicati su Apify in 10–18 h, senza KYC né pagamenti finché non ci sono utenti; i dati della coorte (1 su 1.000) dicono di non aspettarsi nulla senza promozione, ma il costo è nullo e il contatore utenti è pubblico.

**Modelli che non reggono, con le prove**: antismog a pubblicità (4% di "sciopero treni", Roma-centrico, 100–300 €/anno); RapidAPI (25%, PayPal, reclami); Chrome (57% a zero, nessun pagamento in store); Figma (chiuso); GitHub (solo organizzazioni); Zapier/Make (nessuna vendita); strumenti inglesi generici (SERP presidiate o RPM Tier 3).

### 4.3 Test a 30–45 giorni per il progetto 1 (soglie numeriche)

**Costruzione (giorni 1–5, solo Claude):** lettore RSS MIT + tabella storica (gli ultimi 90 giorni di scioperi, per avere pagine-mese già piene); `genera.py` → ~60 pagine (oggi, domani, settimana, 3 pagine-mese, 7 settori, 15 città, 8 aeroporti, 10 guide fisse); sitemap, dati strutturati `Event`, pagina "sources & how to read the register"; modulo avviso "strikes on my dates" (Netlify Forms); Massimiliano: pubblicazione Netlify + Search Console (come EsameB1). Richiesta AdSense al giorno 20 (il sito deve avere le pagine fisse e la privacy).

**Soglie al giorno 45 (Search Console, ultimi 14 giorni):**
1. Pagine indicizzate **≥40 su 60**;
2. Impression **≥1.500/settimana** e in crescita per 2 settimane consecutive;
3. Clic totali dal giorno 1 **≥150**, CTR ≥2%;
4. **≥40% dei clic da USA+Canada+UK+Australia** (requisito Raptive 50% e Journey Tier 1);
5. Almeno 5 query con "today" o "tomorrow" o un mese+anno tra le prime 20 per impression (prova che le pagine "oggi/domani" reggono);
6. AdSense approvato; se attivo ≥7 giorni: **RPM ≥6 $** (sotto, il modello pubblicità non copre e si passa a lista + affiliazione).

**Decisione**: passano 1, 2, 3, 4 → si continua e si aggiungono i satelliti (#2) e la versione italiana (#4) con lo stesso motore; richiesta Journey al raggiungimento di 1.000 sessioni Tier 1/30 gg. Fallisce 1 o 2 (Google non indicizza) → chiudere come per BandiPosteggi. Fallisce solo 4 (clic italiani) → tenere il sito ma aprire subito la versione italiana e rimisurare.

**Tetto di spesa**: **0 € obbligatori**. Opzione da autorizzare separatamente: **≤50 €** di Google Ads su "italy strike today/tomorrow" dopo l'approvazione AdSense, per comprare 300–500 visite Tier 1 e misurare l'RPM reale in 7 giorni invece di aspettare la stagione; soglia: RPM ≥6 $ e costo per visita ≤0,15 €; non è un budget "per farsi conoscere".

**Test parallelo del modello A (giorni 6–10, 0 €)**: pubblicare su Apify gli Actor "Italy Strikes API" e "ANAC public tenders" con README nel formato dei migliori (una frase d'uso, 3 punti, JSON d'esempio) e prezzo pay-per-event 1–2 $ per 1.000 risultati. Soglia al giorno 45: **≥10 utenti totali e ≥3 negli ultimi 30 giorni** su almeno un Actor (il 90° percentile della coorte "nuovi" è 8). Sotto: si lasciano online senza altro lavoro; sopra: KYC e domanda fiscale.

---

## 5. Cosa resta non provato

- Elenco "idee richieste" di Apify (app JS): nessun esempio verificabile con voti.
- Volumi assoluti: solo relativi (Trends) con un ancoraggio Semrush ambiguo; Keyword Planner richiede un account Google Ads (Massimiliano può aprirlo gratis e leggere "italy strike", "sciopero treni", "blocco traffico" in 10 minuti: sarebbe la prima cosa da fare).
- RPM reali in Italia per notizie/auto: nessun report pubblico 2025–26; usati 3–6 € da un caso francese e dalle stime generiche.
- Resistenza delle pagine "oggi/domani" agli AI Overview: nessuno studio per tipo di pagina; da misurare.
- Quota Journey (70%) e dettaglio Raptive (403): citati da terze parti e dai risultati di ricerca.

---

## 6. Riepilogo HTTP status delle fonti chiave (10/10/2026, `curl` dal server, UA browser)

| Fonte | Status | Nota |
|---|---|---|
| api.apify.com/v2/store | 200 | JSON; `total` 83.854; paginazione effettiva ~10.090 |
| docs.apify.com (monetize, payouts, store terms) | 200 | testo letto |
| help.apify.com/…/8684010 | 200 | 22/10/2025 |
| apify.com/ideas, /ideas/how-it-works | 200 | elenco idee in JS, non leggibile |
| blog.apify.com/building-98-actors-on-apify-store | 200 | |
| docs.rapidapi.com/docs/payouts-and-finance | 200 | 25% dal 15/11/2025 |
| help.figma.com/…/12067637274519 | 200 | «not approving new creators» |
| notion.com/help/selling-on-marketplace | 200 | 8% + 0,40 $; Italia elegibile |
| docs.github.com (marketplace) | 200 | solo organizzazioni per piani a pagamento |
| github.com/marketplace | 403 | |
| zapier.com/templates | 200 | solo gratuiti |
| make.com/en/templates | 403 | |
| n8n.io/creators | 200 | badge, nessun pagamento |
| api.wordpress.org plugins | 200 | 70.934 plugin |
| developer.chrome.com/webstore/cws-payments-deprecation | 404 (link vecchio) | deprecazione documentata dalle testate 2020–21 |
| mediavine.com/mediavine-requirements | 200 | Journey 1.000 sessioni Tier 1; Mediavine 5.000 $/anno |
| mediavine.com/journey, /requirements | 404 | URL cambiati |
| raptive.com | 200 | help center 403 |
| support.ezoic.com (requirements), ezoic.com/incubator | 200 | 250k utenti dal 19/2/2026 |
| support.google.com/adsense/answer/9724 | 200 | |
| adstimate.com (Italia, USA, UK, DE) | 200 | modello, non rilevazione |
| money.it/Guadagni-AdSense-come-fatturare-fisco | 200 | 5/6/2026 |
| pasqualepillitteri.it | 000 | |
| scioperi.mit.gov.it (prospetto) | 200 | HTML 30 KB, aggiornato 10/10/2026 |
| scioperi.mit.gov.it/…/rss | 200 | RSS con settore/rilevanza/regione/provincia/orari |
| cgsse.it/calendario-scioperi | 000 | |
| trenitalia.com, italotreno.com (pagine scioperi, URL ipotizzati) | 404 | da cercare gli URL giusti |
| thelocal.it (calendario scioperi maggio 2026) | 200 | «Members only» |
| wantedinrome.com/news/transport-strike.html | 200 | articolo datato |
| trends.google.com/trends/api/explore | 429 → 200 | con cookie di sessione |
| suggestqueries.google.com | 200 | autocomplete |

*Dati grezzi: `scratchpad/ricerca7/store/all.jsonl`, `store/newest.json`, output Trends nei log della sessione.*
