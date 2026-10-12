# 5. App ad alto potenziale nei marketplace: ricerca con dati (12 ottobre 2026)

Domanda di Massimiliano: quale app costruire dentro un marketplace che porta clienti da solo, con un obiettivo di almeno 5.000 €/mese ricorrenti entro 12-18 mesi e un tetto molto più alto? Niente email a freddo, niente social, niente pubblicità all'inizio. Tutto il software lo costruisce e lo mantiene l'agente di programmazione.

---

## In breve

- **Il marketplace migliore per noi è HubSpot**, non Shopify, Atlassian o WordPress. È l'unico in cui ho trovato **app nuove (2024-2026) di piccoli fornitori che crescono di 25-155 installazioni al mese** in categorie già affollate. I clienti sono aziende che pagano HubSpot in media **11.800 $ l'anno** ([HubSpot, 10-Q, 30/6/2026](https://www.sec.gov/Archives/edgar/data/0001404655/000119312526335232/hubs-20260630.htm)). HubSpot non trattiene commissioni.
- **Idea n. 1 (voto 7/10): una piccola serie di "app di servizio" per HubSpot.** Sono app che aggiungono azioni ai workflow o sbloccano funzioni che HubSpot riserva ai piani Enterprise. Si parte con una e se ne aggiunge una ogni 3 mesi. Ci sono esempi concreti: Koalify (4.927 installazioni in circa 31 mesi, prezzi da 50 a 1.000 $/mese) ed Enrollem (1.823 installazioni in circa 15 mesi, da 35 €/mese).
- **Idea n. 2 (voto 6/10): un collegamento Stripe → HubSpot fatto bene**, cioè abbonamenti e prodotti venduti dentro HubSpot. Quello ufficiale ha **14.256 installazioni e voto 2,13 su 5**, con lamentele del 2026. I concorrenti terzi sono pochi: uno costa da 417 $/mese, l'altro ha 95 installazioni.
- **Avvertenza onesta.** Con ipotesi prudenti il n. 1 arriva a **circa 2.300-4.100 $/mese al mese 18**. I 5.000 € si raggiungono solo se almeno un'app cresce come Enrollem o Koalify. Il potenziale c'è (Koalify vale probabilmente oltre 20.000 $/mese, stima mia), ma non è garantito.
- **Scartate con prove:** Shopify (sezione IA e llms.txt satura e coperta da Shopify stesso), WooCommerce "vendita dentro gli assistenti IA" (nessuna domanda: il plugin migliore ha 60 installazioni), sostituti delle app Atlassian Connect in dismissione (il 95% è già migrato e i sostituti ci sono già), WordPress "connettore per agenti IA" (domanda vera, ma presa da aziende grandi e dal plugin ufficiale di WordPress).

---

## Cosa era già stato studiato (non lo ripeto)
- `H-software-marketplace.md`: app fiscali italiane per Shopify, obblighi UE, WordPress italiano. Tetto basso.
- `saas/4-marketplace-candidati.md`: barra laterale Pipedrive per Gmail (la migliore, 450-2.500 $/mese al mese 12), notifiche Jira in Google Chat, Gmail → Notion. Scoperta chiave: su Atlassian **un'app nuova ha una mediana di 2 installazioni**.
- `saas/DECISIONE.md`, `CONFRONTO-FINALE.md`: time tracking (abbandonato) e inventario Shopify (scartato).
- `fattibilita-saas/VERDETTO.md`: SaaS bandi, scartato.

Qui uso gli stessi criteri. In più misuro, marketplace per marketplace, **quanto cresce davvero un'app nuova**: era il punto debole degli studi precedenti.

---

## Metodo (dati estratti il 12/10/2026)
- **HubSpot App Marketplace.**
  - Ho scaricato l'intero catalogo dalla ricerca pubblica della pagina: **2.590 app**, con installazioni, voto e numero di recensioni.
  - Per 847 app di terzi con almeno 100 installazioni ho letto tutte le recensioni, sempre dall'interfaccia pubblica della pagina. La data della **prima recensione** mi serve come indicatore dell'età dell'app.
  - Le schede si trovano su `https://ecosystem.hubspot.com/marketplace/listing/<nome-app>`.
- **WordPress.org.** API pubblica: le 5.996 estensioni più installate su 71.310, con data di pubblicazione e installazioni attive ([API](https://api.wordpress.org/plugins/info/1.2/?action=query_plugins&request[browse]=popular)).
- **Atlassian.** API pubblica: 6.578 app cloud per Jira e Confluence, indicando per ciascuna se è ancora su Connect ([API](https://marketplace.atlassian.com/rest/2/addons?hosting=cloud&application=jira)).
- **Shopify App Store.** Pagine delle schede e ricerche (ora raggiungibili, a differenza degli studi precedenti) e pagine delle recensioni.
- **Limiti.**
  - Nessun marketplace pubblica i ricavi delle singole app.
  - La data della prima recensione viene **dopo** il lancio, quindi le installazioni al mese che calcolo sono un po' **più alte** della realtà.
  - Il forum di HubSpot, G2, Indie Hackers e Reddit sono bloccati dal proxy: quei dati vengono dagli estratti dei motori di ricerca.

---

## Scoperta chiave: dove un'app nuova riceve davvero clienti

| Marketplace | Cosa succede a un'app nuova (dato) | Commissione |
|---|---|---|
| **HubSpot** | **2.590 app** in tutto, mediana di 58 installazioni, 256 app oltre le 1.000. Il 10% più recente delle app ha una mediana di 11 installazioni (il 90% ne ha 96 o meno): la maggior parte fallisce. Però **piccoli fornitori entrati tardi in categorie già piene crescono**: Koalify, Enrollem, FlowNer, Integration Glue (dettagli sotto). [catalogo, 12/10/2026] | Nessuna. Il fornitore incassa da sé ([guida 2026](https://appnigma.ai/blogs/hubspot-marketplace-complete-guide/)) |
| Atlassian | Mediana di **2 installazioni** dopo 3-6 mesi per le app uscite tra aprile e giugno 2026 (studio 4) | 0% fino a 1 M$ (Forge) |
| Shopify | 2.713 app nuove nel solo maggio 2026 (studio 4). Le ricerche sono piene di app a 5,0 stelle: "accessibility" dà 2.943 risultati, "llms.txt" 348, "order editing" 4.619 [ricerche, 12/10/2026] | 0% fino a 1 M$ |
| WordPress.org | La directory porta molte installazioni gratuite: WPVibe ha 70.000 installazioni in 6 mesi. Ma quasi tutti i successi recenti sono di aziende grandi (hosting, Elementor, Brainstorm Force, Awesome Motive). Passa a pagamento l'1-2% degli utenti ([Freemius](https://freemius.com/blog/increase-freemium-upgrades-wordpress-plugin-theme/)) | Nessuna, ma i pagamenti si gestiscono da sé |
| monday.com | Più di 850 app e 1,6 M di installazioni; il 49% degli account ha installato almeno un'app ([monday](https://monday.com/appsdeveloper)). **Non ci sono dati per singola app**: non misurabile | 0% fino a 200k$ |

**Perché HubSpot.** I clienti sono 306.446 aziende (+14% in un anno) e pagano in media 11.800 $ l'anno ([10-Q del 30/6/2026](https://www.sec.gov/Archives/edgar/data/0001404655/000119312526335232/hubs-20260630.htm)). La crescita arriva soprattutto dai piani più economici (Starter), che non hanno le funzioni dei piani Enterprise: è il terreno delle app che "sbloccano" quelle funzioni.

### App nuove di piccoli fornitori su HubSpot: quanto crescono

Le installazioni al mese sono calcolate dalla data della prima recensione fino al 12/10/2026.

| App (fornitore) | Prima recensione | Installazioni | Al mese | Prezzo | Scheda |
|---|---|---|---|---|---|
| Koalify, unione dei duplicati | 20/2/2024 | 4.927 | ~155 | 50-1.000 $/mese ([prezzi](https://koalify.io/pricing)) | [link](https://ecosystem.hubspot.com/marketplace/listing/koalify-io) |
| Enrollem (Ogham Works), iscrizione alle sequenze dai workflow senza Enterprise | 23/7/2025 | 1.823 | ~125 | gratis fino a 50 al mese, poi da 35 €/mese ([sito](https://www.oghamworks.com/enrollem)) | [link](https://ecosystem.hubspot.com/marketplace/listing/enrollem-by-oghamworks) |
| Koalify Email Validation | 29/6/2026 | 154 | ~45 | n/d | [link](https://ecosystem.hubspot.com/marketplace/listing/koalify-email-validation) |
| ProBackup, backup giornaliero del CRM | 11/3/2025 | 681 | ~36 | 25-86 $/mese ([prezzi](https://www.probackup.io/pricing)) | [link](https://ecosystem.hubspot.com/marketplace/listing/pro-backup-380854) |
| FlowNer (4CRMs), stessa funzione di Enrollem ma uscita dopo | 11/5/2026 | 175 | ~35 | 19 $/mese per 1.000 iscrizioni | [link](https://ecosystem.hubspot.com/marketplace/listing/automated-sequence-enrollment-by-flowner) |
| Integration Glue, 4 app di azioni per workflow (calcoli, formati, associazioni, clonazione) | 9/2024 - 5/2025 | 554 / 536 / 605 / 612 | ~25-33 ciascuna | 0 / 19 / 99 / 499 $/mese ([prezzi](https://www.integrationglue.com/pricing)) | [esempio](https://ecosystem.hubspot.com/marketplace/listing/workflow-calculation-actions) |
| Workflow Date Calculator (Exelab) | 30/8/2023 | 1.159 | ~31 | n/d | [link](https://ecosystem.hubspot.com/marketplace/listing/future-date-calculator-1828077) |
| Emergency Unmerge, per annullare un'unione sbagliata | 2/4/2026 | 97 | ~16 | n/d | [link](https://ecosystem.hubspot.com/marketplace/listing/emergency-unmerge) |

Le app di **collegamento** tra HubSpot e un altro software crescono più piano:

| App | Prima recensione | Installazioni | Al mese |
|---|---|---|---|
| Xero by Cloudify | 9/2024 | 657 | ~26 |
| Shopify Sync by Unific | 5/2020 | 972 | ~15 |
| Invoice Stack (Xero + QuickBooks) | 2/2021 | 638 | ~10 |
| ClearSync (Stripe) | 9/2025 | 95 | ~7 |
| ClickSync (ClickUp) | 4/2026 | 28 | ~5 |

**Regola che ne esce.** Su HubSpot conviene un'app di servizio, cioè un'azione per i workflow o una funzione bloccata dal piano. Conviene di meno un collegamento. Ed entrare tardi in una categoria già provata funziona: lo mostrano FlowNer dopo Enrollem e Koalify dopo Dedupely e Insycle.

---

## Classifica

Voto da 0 a 10: più alto = meglio. Le cifre di ricavo sono IPOTESI, calcolate più sotto.

| # | Idea | Marketplace | Prove di domanda | Lacuna | Settimane per l'MVP | Ricavo al mese 18 (prudente → ottimista) | Rischi principali | Voto |
|---|---|---|---|---|---|---|---|---|
| **1** | **Serie di app di servizio per HubSpot** (azioni nei workflow e funzioni Enterprise sbloccate). Una nuova ogni ~3 mesi | HubSpot | Koalify ~155 installazioni/mese, Enrollem ~125, 4 app di Integration Glue ~25-33 ciascuna, prezzi 19-1.000 $/mese | Funzioni riservate a Enterprise o assenti; l'idea "workflow → sequenza" è chiesta dal 2017 ([HubSpot Ideas](https://community.hubspot.com/t5/HubSpot-Ideas/Use-workflow-to-trigger-a-sequence/idc-p/554505/highlight/true)) | 2-4 per app | **~2.300 → ~7.000 $** | HubSpot rende la funzione nativa o la estende ai piani bassi; servono 3 installazioni prima di comparire nel marketplace | **7** |
| 2 | **Stripe → HubSpot** con abbonamenti, prodotti e ricavo ricorrente | HubSpot (+ Stripe App Marketplace) | Il collegamento ufficiale ha 14.256 installazioni | Voto 2,13 su 91 recensioni; nel 2026: «non per gli abbonamenti, che sono la cosa chiave» | 4-6 | ~1.000 → ~3.200 $ | Crescita lenta dei collegamenti (7-26 al mese); HubSpot può sistemare il suo | **6** |
| 3 | QuickBooks/Xero ↔ HubSpot per le fatture | HubSpot | Ufficiali: QuickBooks 14.893 installazioni (voto 2,08), Xero 6.481 (2,24). Invoice Stack da 49 $/mese | Recensioni 2026: errori di sincronizzazione, imposte non gestite fuori dagli USA | 6-8 | ~1.000 → ~3.000 $ | Assistenza pesante (imposte, contabilità); costi API Xero da 22 a 895 $/mese dal 2/3/2026 | 5 |
| 4 | HubSpot ↔ Shopify, pubblicata su **entrambi** i marketplace | HubSpot + Shopify | Ufficiale: 15.310 installazioni su HubSpot (voto 2,32); su Shopify voto **1,0** | Recensioni 2025-2026: «non si collega», «niente SKU», «troppo lento» | 6-8 | ~800 → ~2.500 $ | Su Shopify i negozi usano Klaviyo, non HubSpot (domanda lato Shopify quasi nulla); volumi di ordini da gestire | 4 |
| 5 | Barra Pipedrive in Gmail (studio 4) | Pipedrive + Google | App Outlook a pagamento (266 e 78 valutazioni) | Add-on ufficiale con voto 2,1 | 2-3 | 450 → 2.500 $ (al mese 12, studio 4) | Marketplace piccolo; tetto basso | 4 |
| 6 | Connettore WordPress per agenti IA, gratuito con versione a pagamento | WordPress.org | WPVibe 70.000 installazioni in 6 mesi | Nessuna: la domanda è già coperta | 3-4 | <500 $ | Plugin ufficiale di WordPress (40.000 installazioni in 10 giorni) e aziende grandi | 3 |
| 7 | Sostituti delle app Atlassian Connect in dismissione (es. OpenAPI/Swagger per Confluence) | Atlassian | Due app Connect ferme con 2.869 e 1.211 installazioni | Fine supporto il 31/1/2027 | 2-3 | <500 $ | Il 95% dei posti a pagamento è già migrato; sostituti Forge già usciti; mediana di 2 installazioni per le app nuove | 2 |
| 8 | App per farsi trovare dagli assistenti IA (llms.txt) | Shopify | 348 app, leader con 392-2.845 recensioni | Nessuna | 2 | ~0 | Shopify invia già da sé i cataloghi agli assistenti IA | 2 |
| 9 | Vendita dentro gli assistenti IA per WooCommerce | WordPress.org | Il plugin migliore ha **60** installazioni | Domanda non provata | 4 | ~0 | Serve l'approvazione della piattaforma IA | 1 |

---

## Schede

### 1. Serie di app di servizio per HubSpot (voto 7)

**Prove che si paga (12/10/2026)**
- Koalify: 4.927 installazioni e 131 recensioni con voto 4,95. Prezzo in base ai record: da 50 $/mese, con un tetto di 500 $/mese se pagato all'anno e 1.000 $/mese se pagato al mese ([prezzi](https://koalify.io/pricing)). È entrata **dopo** Dedupely (3.921 installazioni, ricavi 2025 stimati a 990k$ da [Latka](https://getlatka.com/companies/dedupe.ly)) e Insycle (7.095).
- Enrollem: 1.823 installazioni, gratis fino a 50 iscrizioni al mese, poi da 35 €/mese ([Ogham Works](https://www.oghamworks.com/enrollem)). Fa da sola una cosa che HubSpot riserva all'Enterprise: «questa funzione è limitata agli account con abbonamento Enterprise» ([HubSpot KB](https://knowledge.hubspot.com/sequences/enroll-and-unenroll-contacts-in-sequences-using-workflows)).
- Integration Glue: 4 app da 536-612 installazioni ciascuna, a 19 / 99 / 499 $/mese più crediti ([prezzi](https://www.integrationglue.com/pricing)). È esattamente il modello "serie di piccole app" che propongo.
- Media del marketplace (dato del 2024, metodo non verificato): circa 23k$ al mese per prodotto indipendente, escludendo i valori estremi ([Indie Hackers, 2024](https://www.indiehackers.com/post/indies-are-making-280k-arr-on-hubspot-in-2024-608dc3fab2)). Probabilmente sovrastimato.

**Lacune (dove cercare la prima app)**
- **Funzioni riservate a Enterprise o a Operations Hub.** Esempio: l'idea "usare un workflow per avviare una sequenza", chiesta dal 2017 e poi data solo all'Enterprise. Un utente: «è stato uno schiaffo» ([HubSpot Ideas](https://community.hubspot.com/t5/HubSpot-Ideas/Use-workflow-to-trigger-a-sequence/idc-p/554505/highlight/true)). Enrollem e FlowNer sono nate proprio qui.
- **I collegamenti "Data Sync" fatti da HubSpot sono scadenti in modo sistematico.** Sono 115 app con 245.006 installazioni in tutto, e il voto mediano (tra quelle con almeno 10 recensioni) è **2,48**. Esempi: Shopify 2,32, QuickBooks 2,08, Stripe 2,13, Xero 2,24, Square 2,5, Outreach 1,79, Freshdesk 1,56, Mixpanel 1,3 [catalogo, 12/10/2026].
- **Categorie con pochi concorrenti seri:**
  - backup e ripristino: ProBackup ha 681 installazioni; SysCloud ha voto 2,0;
  - controllo dello stato del portale e pulizia delle proprietà: le app hanno 13-305 installazioni;
  - riepiloghi tra oggetti collegati ("rollup"): un'app sola, con 13 installazioni.

**Prima app consigliata.** Va scelta con una regola semplice: una funzione chiesta in HubSpot Ideas, riservata all'Enterprise oppure assente, e con al massimo 2 concorrenti sopra le 500 installazioni. Candidati da controllare per primi:
- (a) backup e ripristino a prezzo basso, con "annulla l'unione sbagliata" incluso;
- (b) azioni di calcolo e riepilogo tra oggetti collegati;
- (c) una versione economica di una funzione Enterprise ancora senza concorrenti.

Non la scelgo ora perché il forum Ideas è bloccato dal proxy: è il primo controllo da fare, a mano o con una ricerca mirata.

**Fattibilità per l'agente di programmazione: alta**
- Cosa va costruito:
  - app pubblica con OAuth;
  - azioni personalizzate per i workflow ([documentazione](https://developers.hubspot.com/docs/apps/developer-platform/add-features/custom-workflow-actions.md));
  - un piccolo server (funzioni serverless) e i pagamenti.
- Tempi: 2-4 settimane per app.
- Niente consulenza legale, medica o finanziaria. Si trattano però dati personali del CRM, quindi servono privacy policy e DPA (GDPR).

**Assistenza**
- Media-bassa. Gli utenti sono responsabili del CRM (RevOps) e scrivono in inglese.
- Le risposte le prepara l'agente. Stima: 2-4 ore a settimana per Massimiliano con 100 clienti (ipotesi).

**Ostacoli all'ingresso (dati verificati)**
- Servono **almeno 3 installazioni attive di account non collegati a noi** prima di poter chiedere di comparire nel marketplace ([requisiti HubSpot](https://developers.hubspot.com/docs/apps/developer-platform/list-apps/listing-your-app/app-marketplace-listing-requirements)). Senza email a freddo, la strada è rispondere nelle discussioni di HubSpot Ideas e Community dove le persone chiedono proprio quella funzione: è un piccolo lavoro manuale di Massimiliano.
- Prima revisione entro 10 giorni lavorativi, tutto il processo entro 60 giorni (stessa fonte). Si può inviare una sola app alla volta.
- Dal 2/11/2026 le app costruite con il vecchio sistema ("legacy") non vengono più accettate come nuove schede ([community HubSpot](https://community.hubspot.com/t/changes-to-marketplace-submission-flow-how-active-installs-are-determined/156427)): si costruisce subito sulla piattaforma nuova.

**Rischi**
- HubSpot porta la funzione ai piani bassi o la fa fare al suo assistente IA.
- La maggior parte delle app nuove non cresce: le schede del 10% più recente hanno una mediana di 11 installazioni.
- Si dipende da una sola piattaforma.

### 2. Stripe → HubSpot con abbonamenti e prodotti (voto 6)
- **Domanda.** "Stripe" (data sync di HubSpot) ha 14.256 installazioni, voto 2,13 e 91 recensioni ([scheda](https://ecosystem.hubspot.com/marketplace/listing/stripe-data-sync)). Recensioni:
  - 29/4/2026: «funziona per le fatture ma non per gli abbonamenti, che sono la cosa chiave»;
  - 11/9/2026: «sarebbe molto meglio se registrasse gli articoli della transazione»;
  - 8/12/2025: «sincronizzazione a senso unico, costringe a gestire i dati due volte».
- **Concorrenti.**
  - hapily "saas", da **417 a 833 $/mese** ([prezzi](https://hapily.com/pricing)): 267 installazioni, ultima recensione del 3/5/2024.
  - ClearSync: 95 installazioni in 13 mesi.
  - Finrite: 56 installazioni.
- **Spazio.** Una via di mezzo a 29-99 $/mese.
- **Fattibilità.** Webhook di Stripe e API di HubSpot: 4-6 settimane. Le API di Stripe e di HubSpot sono gratuite. Si può pubblicare anche nello Stripe App Marketplace come secondo canale.
- **Ruolo nel piano.** Ottima come **seconda app della serie**, ma da sola non arriva ai 5.000 € (vedi i calcoli).

### 3. QuickBooks/Xero ↔ HubSpot (voto 5)
- **Domanda.** QuickBooks data sync: 14.893 installazioni, voto 2,08. Xero: 6.481 installazioni, voto 2,24.
- **Recensioni.**
  - QuickBooks: «solo errori di sincronizzazione mai risolti» (10/8/2026); «i workflow non funzionano con QuickBooks canadese» (10/4/2026); «le imposte non passano correttamente» (24/4/2026).
  - Xero: «impossibile sincronizzare le fatture storiche per le aliquote» (29/9/2026); «il collegamento cade spesso» (24/9/2026).
  - Fonte: interfaccia pubblica delle recensioni delle schede [quickbooks-data-sync](https://ecosystem.hubspot.com/marketplace/listing/quickbooks-data-sync) e [xero-data-sync](https://ecosystem.hubspot.com/marketplace/listing/xero-data-sync).
- **Concorrenti.** Invoice Stack da 49 $/mese (638 installazioni), Cloudify Xero (657), SyncQ (481).
- **Perché il voto è basso.**
  - Assistenza pesante: imposte di paesi diversi, rischio di errori contabili.
  - Da marzo 2026 Xero fa pagare l'accesso alle API, da 22 a 895 $/mese in base alle connessioni ([Apideck](https://apideck.com/blog/xero-api-pricing-and-the-app-partner-program)).
  - QuickBooks è gratis solo fino a 500.000 chiamate al mese ([Truto](https://truto.one/blog/how-much-does-the-quickbooks-api-cost-2026-pricing-rate-limits/)).

### 4. HubSpot ↔ Shopify su due marketplace (voto 4)
- **Lato HubSpot.** "Shopify" data sync: 15.310 installazioni, voto 2,32. Recensioni: «inutile senza componenti aggiuntivi costosi» (24/2/2026); «non fornisce né SKU né dati utilizzabili» (19/1/2026); «troppo lento» (16/12/2025).
- **Lato Shopify.** L'app ufficiale HubSpot ha voto **1,0** con 8 recensioni ed è uscita il 10/10/2023 ([scheda](https://apps.shopify.com/hubspot-2), [recensioni](https://apps.shopify.com/hubspot-2/reviews?sort_by=newest)). Il 2/6/2025 un utente scrive: «hanno chiuso la vecchia app a maggio 2025 e ci hanno costretti su questa versione rotta».
- **Ma la domanda lato Shopify è minima.** Cercando "salesforce" sul Shopify App Store escono 100 app, quasi tutte con 0-4 recensioni [ricerca, 12/10/2026]. L'unico terzo serio, Unific, cresce di circa 15 installazioni al mese.

### 5. Barra Pipedrive in Gmail
Vedi lo studio 4: resta valida, ma ha un tetto basso (450-2.500 $/mese al mese 12).

### 6. Connettore WordPress per agenti IA (voto 3)
- **Le installazioni arrivano** (dati dell'API WordPress del 12/10/2026):
  - WPVibe (SeedProd): 70.000 dal 20/4/2026;
  - Easy MCP AI (Themeisle): 10.000 dal 25/3/2026;
  - Royal MCP: 10.000 dal 14/1/2026.
- **Ma il plugin ufficiale di WordPress** "mcp-adapter", uscito il 2/10/2026, ha già 40.000 installazioni.
- La conversione a pagamento sui plugin WordPress è dell'1-2% ([Freemius](https://freemius.com/blog/increase-freemium-upgrades-wordpress-plugin-theme/)). Con prezzi da 49-99 $ l'anno servirebbero centinaia di migliaia di utenti per arrivare ai 5.000 €.

### 7. Sostituti delle app Atlassian Connect (voto 2)
- **Lo spazio c'è sulla carta.** Su 6.578 app cloud, 961 sono ancora su Connect. Tra quelle a pagamento e abbandonate:
  - "Open API (Swagger) Integration": 2.869 installazioni, ultima versione 19/9/2024;
  - "Visualize OpenAPI": 1.211, ultima versione 16/11/2024;
  - "Slack Connector for Jira": 1.153, ultima versione 20/11/2021.
- **Ma i sostituti esistono già.** Ad esempio "PlantUML, Swagger, drawio.xml, Mermaid" su Forge (3.163 installazioni) e "OpenAPI (Swagger) for Confluence" (397, gratuita, aggiornata il 10/10/2026).
- **Atlassian dice che il 95% dei posti a pagamento è già migrato** ([Atlassian](https://www.atlassian.com/blog/developer/getting-ready-for-connect-end-of-support); scadenza spostata al 31/1/2027, [community](https://community.developer.atlassian.com/t/connect-end-of-support-extended-to-january-31-2027/102002)).

### 8. Shopify, farsi trovare dagli assistenti IA (voto 2)
- Cercando "llms.txt" escono 348 app: StoreSEO ha 760 recensioni, SEOLab 2.845, Avada AEO 392 [ricerca, 12/10/2026].
- Shopify invia già da sé i cataloghi dei negozi agli assistenti IA con gli "agentic storefronts" ([guida](https://www.ringly.io/blog/agentic-storefront-shopify)).

### 9. Vendita dentro gli assistenti IA per WooCommerce (voto 1)
- Cercando "agentic commerce" tra i plugin WordPress escono 68 risultati. Il primo, "Agentic Commerce for WooCommerce", ha **60 installazioni** (12/10/2026).
- Il commerciante deve essere approvato dalla piattaforma IA ([scheda WPMR](https://wordpress.org/plugins/wpmr-agentic-checkout/)).
- La domanda non è provata.

---

## Calcoli per l'idea n. 1 (IPOTESI, in dollari)

**Ipotesi**
- **Calendario delle uscite:**
  - app 1 nel marketplace al mese 3 (2-4 settimane di sviluppo, le 3 installazioni, poi la revisione);
  - app 2 al mese 6;
  - app 3 al mese 9.
  - Al mese 18 fanno in tutto 36 "mesi-app" di vendita.
- **Installazioni al mese per app:**
  - prudente: 20, sotto i 25-36 dei piccoli fornitori della tabella;
  - centrale: 35;
  - ottimista: un'app a 100, come Enrollem e Koalify, e le altre a 35.
- **Altri parametri:**
  - restano attive il 60% delle installazioni (ipotesi);
  - paga il 12% delle installazioni attive (ipotesi). Le guide sulle app Shopify indicano dal 3 al 15% ([Taylor Sicard](https://taylorsicard.com/blog/shopify-app-listing-conversion)); qui i clienti sono aziende;
  - prezzo medio 45 $/mese, coerente con Enrollem (35 €), ProBackup (25-86 $), Integration Glue (19-99 $) e Koalify (50 $ e oltre).

**Risultato al mese 18**

| Scenario | Installazioni | Attive | Paganti | Ricavo mensile |
|---|---|---|---|---|
| Prudente | 720 | 432 | 52 | **~2.300 $/mese** |
| Centrale | 1.260 | 756 | 91 | **~4.100 $/mese**, circa 3.700 € (cambio da verificare) |
| Ottimista | ~2.235 | ~1.340 | ~160 | **~7.200 $/mese** |

**Tetto.** Un'app al livello di Koalify, con 4.927 installazioni, il 60% attive, il 12% paganti e 80 $ di prezzo medio, varrebbe **circa 28.000 $/mese** (stima mia, non dichiarata da Koalify).

**Costi**
- HubSpot: nessuna commissione.
- Pagamenti: Stripe circa 3%, oppure Paddle come venditore per conto nostro, che gestisce l'IVA estera, al 5% + 0,50 $ a transazione ([Paddle](https://www.paddle.com/pricing)).
- Server: pochi euro al mese.
- Posizione fiscale: circa 4.000 €/anno. Conviene aprirla solo all'arrivo dei primi pagamenti, come già deciso nelle regole fisse.

---

## Verdetto

**Una idea passa, con riserva: la n. 1, una serie di app di servizio per HubSpot. La n. 2 (Stripe → HubSpot) va fatta come seconda app della serie.**

Perché passa:
- È l'unico marketplace con prove misurate che un nuovo arrivato piccolo riceve 25-155 installazioni al mese anche in categorie già occupate (Koalify, Enrollem, FlowNer, Integration Glue).
- I clienti sono aziende che pagano molto e non c'è commissione.
- La costruzione è alla portata dell'agente di programmazione.

Riserve:
- Lo scenario centrale si ferma a circa 4.100 $/mese al mese 18. I 5.000 € richiedono che almeno un'app vada sopra la media dei piccoli fornitori.
- Serve un piccolo lavoro manuale per le prime 3 installazioni.

Le altre falliscono almeno un criterio: domanda non provata (9), lacuna già chiusa (6, 7, 8), tetto basso (5) o assistenza troppo pesante (3, 4).

### Piano a costo zero e regola di stop
1. **Settimana 1.** Scegliere la prima app con la regola della scheda 1: funzione chiesta in HubSpot Ideas, riservata all'Enterprise o assente, al massimo 2 concorrenti sopra le 500 installazioni. Aprire l'account sviluppatore HubSpot (gratuito).
2. **Settimane 2-4.** L'agente costruisce l'app sulla piattaforma nuova, con una versione gratuita a uso limitato e piani da 19 a 99 $/mese. Massimiliano trova 3 utenti veri rispondendo nelle discussioni dove la funzione viene chiesta.
3. **Mese 2-3.** Invio della scheda; revisione da 10 giorni a 2 mesi.
4. **Soglia, 60 giorni dopo la pubblicazione:** almeno **40 installazioni** (20 al mese, lo scenario prudente) e almeno **3 clienti paganti**. Se si raggiunge si fa l'app 2 (Stripe → HubSpot). Se non si raggiunge si cambia funzione una volta, poi stop.
5. **Posizione fiscale e pagamenti:** solo all'arrivo dei primi clienti paganti (regola fissa n. 1).

---

## Fonti principali (consultate il 12/10/2026)
- Catalogo HubSpot (ricerca pubblica del marketplace) e recensioni delle schede: `ecosystem.hubspot.com/marketplace/listing/<nome-app>`
- Requisiti delle schede HubSpot: https://developers.hubspot.com/docs/apps/developer-platform/list-apps/listing-your-app/app-marketplace-listing-requirements
- HubSpot 10-Q, 30/6/2026: https://www.sec.gov/Archives/edgar/data/0001404655/000119312526335232/hubs-20260630.htm
- API WordPress.org: https://api.wordpress.org/plugins/info/1.2/
- API Atlassian Marketplace: https://marketplace.atlassian.com/rest/2/addons
- Shopify App Store: https://apps.shopify.com/hubspot-2/reviews
- Prezzi: https://koalify.io/pricing · https://www.oghamworks.com/enrollem · https://www.integrationglue.com/pricing · https://www.probackup.io/pricing · https://hapily.com/pricing · https://www.paddle.com/pricing
- Studi precedenti: `studio-business/saas/4-marketplace-candidati.md`, `studio-business/H-software-marketplace.md`

## Decisione di Massimiliano (12/10/2026)

**Non si procede.** I primi clienti richiederebbero risposte pubblicate da lui sui forum (HubSpot, Reddit, LinkedIn) e un lavoro di vendita personale. Questo non rientra nel modello automatico che vuole. Si riapre solo se emerge un canale che porta i primi utenti senza il suo intervento.
