# 4. Micro-SaaS dentro un marketplace: candidati confrontati con dati (9 ottobre 2026)

Domanda: quale app costruire dentro un marketplace con ricerca interna, così che i clienti arrivino senza pubblicità, senza pubblico e senza rete?

## Metodo e limiti
- **Atlassian Marketplace.** Il 9/10/2026 ho scaricato tutto il catalogo dall'API pubblica ([`marketplace.atlassian.com/rest/2/addons`](https://marketplace.atlassian.com/rest/2/addons?hosting=cloud&application=jira)): 4.708 app cloud per Jira e 1.826 per Confluence. Per ogni app ho preso installazioni, recensioni, data della prima versione, framework (Connect o Forge) e prezzi. Ho poi letto le recensioni con data di 671 app.
- **Google Workspace Marketplace.** Ho letto le pagine di ricerca e le schede delle app: utenti, voto, recensioni con data, prezzo.
- **Pipedrive Marketplace.** Ho interrogato l'indice di ricerca pubblico della pagina (Algolia, chiave di sola lettura presente nel codice della pagina): 509 app.
- **Limiti.**
  - Il campo "utenti" di Google è gonfiato: conta le installazioni di dominio.
  - Le installazioni Atlassian comprendono anche i siti gratuiti fino a 10 utenti.
  - Nessun marketplace pubblica i ricavi delle singole app.
  - Indie Hackers, appmarketplace.com e il forum di monday sono bloccati dal proxy: quei dati vengono dagli estratti dei motori di ricerca.

---

## 0. La scoperta più importante: il marketplace NON porta traffico da solo a un'app nuova

Prima di confrontare i candidati bisogna correggere la premessa, perché i dati la smentiscono in parte.

| Marketplace | Prova (data) | Cosa significa |
|---|---|---|
| Atlassian (Jira cloud) | 617 app nuove dal 1/7 al 3/10/2026, circa 200 al mese. Le 348 app uscite tra aprile e giugno 2026 hanno, dopo 3-6 mesi, una **mediana di 2 installazioni** (il 90% ne ha 17 o meno). Su un campione di 700 app, le app a pagamento uscite nel 2024 hanno una **mediana di 16 installazioni** dopo circa 2 anni (il 90% ne ha 123 o meno). Su tutto il catalogo la mediana è 7 e 1.002 app su 4.708 hanno 0 installazioni. [API, estrazione del 9/10/2026] | Il marketplace è invaso da app fatte in serie (es. un fornitore con 3 app, un altro con 4, tutte uscite nel 2026 e ferme a 0-2 installazioni). |
| Shopify | 21.509 app; **2.713 nuove nel solo maggio 2026**; il 23,8% cita l'AI ([IH, giu 2026](https://www.indiehackers.com/post/i-analyzed-21-509-shopify-apps-to-see-if-the-market-is-saturated-5428b05aa9)). Il 55,3% delle app non ha recensioni ([profitable.app, 8/6/2026](https://profitable.app/shopify-apps/stats)). Revisione delle app in 4-6 settimane ([forum sviluppatori Shopify, gen-feb 2026](https://community.shopify.dev/t/warning-shopify-app-store-review-process/32259)). | È il marketplace più affollato. |
| Google Workspace | Mailtuck (aggiornata il 2/9/2026) non compare nei primi risultati per la sua parola chiave esatta, "save email to notion". MatterMail (luglio 2026) non si trova cercando nemmeno il suo nome. | La ricerca premia chi ha già molti utenti. |
| Pipedrive | 509 app in tutto; mediana di 2 valutazioni; 182 app (36%) con 0 valutazioni; 68 con almeno 50 ([indice pubblico, 9/10/2026](https://www.pipedrive.com/en/marketplace)). | Marketplace piccolo e poco affollato. |

Le eccezioni trovate su Atlassian nel 2026 sono quasi tutte di fornitori che hanno già clienti. Esempio: SprintRetro Pro di Agile Pulse ha fatto 593 installazioni in 5 mesi, ma lo stesso fornitore ha già Planning Poker con 3.299 installazioni.

**Regola di selezione che ne deriva.** Il marketplace porta clienti a un'app nuova solo se valgono tre condizioni insieme:
- (a) qualcuno cerca già quella funzione e i risultati pertinenti sono pochi;
- (b) l'app più usata è scadente o abbandonata;
- (c) non esiste un'alternativa gratuita buona.

Ho applicato questa regola a tutti i candidati.

---

## Regole e costi dei marketplace considerati

| | Atlassian | Google Workspace | Pipedrive | Shopify | monday.com |
|---|---|---|---|---|---|
| Commissione | **0% fino a 1 M$ di ricavi Forge cumulativi**, dall'1/1/2026; oltre, 17% dall'1/10/2026. App Connect: 25% ([annuncio](https://community.developer.atlassian.com/t/marketplace-revenue-share-updates-2026/91727), [nuove date](https://community.developer.atlassian.com/t/extended-timelines-for-marketplace-revenue-share-changes/96668)) | Nessuna, ma il marketplace non gestisce i pagamenti: serve Stripe | Nessuna commissione documentata per le app pubbliche; si fattura in proprio ([documentazione](https://pipedrive.readme.io/docs/about-the-marketplace)) | 0% fino a 1 M$ cumulativo, 19 $ una tantum ([shopify.dev](https://shopify.dev/docs/apps/launch/distribution/revenue-share)) | 0% fino a 200k$ cumulativi, poi 15%. Fatturazione di monday obbligatoria ([monday dev](https://developer.monday.com/apps/changelog/announcing-the-revshare-program)) |
| Costi di ingresso | Account sviluppatore gratuito. Uso dell'infrastruttura Forge a consumo, con una quota gratuita mensile ([Forge pricing, 1/2026](https://www.atlassian.com/blog/developer/updates-to-forge-pricing-effective-january-2026)). Il bug bounty è obbligatorio solo per i livelli Silver e superiori, che partono da 150k$ di vendite ([partner program](https://developer.atlassian.com/platform/marketplace/marketplace-partner-program/)) | Gratis. Gli scope "sensibili" richiedono la verifica OAuth (gratuita). Gli scope Gmail per add-on (`gmail.addons.current.*`) sono sensibili e non "ristretti", quindi non serve l'audit di sicurezza CASA, che è a pagamento ([Google scopes](https://developers.google.com/workspace/gmail/api/auth/scopes)) | Gratis (account sandbox) | 19 $ | Gratis |
| Tempi di approvazione | Non pubblicati (non verificato) | Verifica OAuth: giorni o settimane | **Fino a 21 giorni lavorativi** ([processo](https://pipedrive.readme.io/docs/marketplace-app-approval-process)) | 4-6+ settimane (testimonianze del 2026) | n/d |
| Concorrenza | ~6.500 app cloud, ~200 nuove al mese su Jira | Enorme | **509 app** | 21.509 app | **869 app** a fine 2025 ([SEC 20-F](https://www.sec.gov/Archives/edgar/data/1845338/000117891326000870/zk2634436.htm)) |

---

## Candidato 1: barra laterale Pipedrive dentro Gmail
*Dove si vende: Google Workspace Marketplace + Pipedrive Marketplace*

**Problema.** Chi usa il CRM Pipedrive e lavora in Gmail ha solo l'add-on ufficiale, che è lento e povero di funzioni. Per Outlook invece esistono app di terzi a pagamento che vanno bene.

**1. Prove che la gente paga**
- Nel Pipedrive Marketplace, per Outlook esistono già app di terzi a pagamento con trazione:
  - "Pipedrive for Outlook" di Baymats AB: a pagamento, voto 4,0 con **266 valutazioni** e 47 recensioni ([scheda](https://www.pipedrive.com/en/marketplace/app/pipedrive-for-outlook/594c78d1bdbacfbc)).
  - "Pipelook": voto 3,5 con **78 valutazioni**. Costa **5 $/mese** per un utente singolo, oppure **150 $/anno** per un team ([scheda](https://www.pipedrive.com/en/marketplace/app/outlook-connector-pipelook/3d08e105af238287), [AppSource](https://appsource.microsoft.com/en-us/product/web-apps/WA200006774)).
- I clienti pagano già Pipedrive 14-79 $ per utente al mese ([tech.co](https://tech.co/crm-software/pipedrive-pricing)): sono aziende abituate a pagare software.

**2. Lacuna (con date)**
- L'add-on ufficiale "Pipedrive CRM" su Google Workspace ha **83K+ utenti, voto 2,1, 108 recensioni**; la scheda è stata aggiornata il 14/5/2026 ([scheda](https://workspace.google.com/marketplace/app/pipedrive_crm/181457847709)). Recensioni recenti:
  - 11/3/2026: «non fate nulla per migliorare questa applicazione»;
  - 3/3/2026: «così lento da essere inutile… le app di terzi (es. Superhuman) integrano Pipedrive in modo impeccabile»;
  - 15/4/2026: «questa estensione è una barzelletta»;
  - 14/3/2026: «inutile»;
  - 8/1/2026: «non funziona»;
  - 17/12/2024: «sistematelo o toglietelo dallo store».
- Nel forum ufficiale di Pipedrive gli utenti elencano cosa manca ([thread "Gmail addon"](https://community.pipedrive.com/discussion/comment/37692)): campi personalizzati, lead, progetti, deduzione dell'azienda dall'email. Lamentano anche la lentezza nel passare da una mail all'altra.

**3. Concorrenza**
- **Pipedrive Marketplace:** cercando "gmail" escono 12 risultati e l'**unica barra laterale Gmail è quella ufficiale** (voto 3,5, 55 valutazioni). Gli altri risultati sono strumenti di automazione come Zapier e IFTTT.
- **Google Workspace:** cercando "pipedrive" escono l'add-on ufficiale e "Pipedrive for Google Chat" (6K+ utenti, un altro prodotto). C'è anche MatterMail, uscita a luglio 2026: non ha recensioni, non è sul Pipedrive Marketplace e la ricerca non la trova nemmeno per nome.
- **Fuori dai marketplace:** estensioni Chrome di terzi (es. Saysync, Add To Crm) e CRM nati per Gmail (Streak, NetHunt, folk).
- **Alternativa gratuita forte:** no. Quella gratuita è l'add-on ufficiale da 2,1.

**4. Distribuzione**
- **Pipedrive:**
  - nel 2023 oltre 134.000 utenti hanno installato almeno un'app ([Businesswire, 5/12/2023](https://www.businesswire.com/news/home/20231205485571/en));
  - la posizione nelle categorie dipende da voto e numero di installazioni ([documentazione](https://pipedrive.readme.io/docs/about-the-marketplace));
  - con 509 app, chi cerca "gmail" vedrebbe la nuova app al 1°-2° posto (stima, non misurata).
- **Google:** la ricerca favorisce le app con molti utenti (vedi MatterMail), quindi conterebbe come canale secondario.
- **Nessun numero pubblico** sulle installazioni organiche delle app Pipedrive: è l'incognita principale.

**5. Fattibilità per Claude da solo: alta**
- **Cosa va costruito:**
  - un add-on Gmail (Apps Script o runtime HTTP con interfaccia a "card");
  - una app OAuth pubblica nel Pipedrive Marketplace, con l'API REST di Pipedrive;
  - pagamenti con Stripe.
- **Tempi:**
  - MVP in 2-3 settimane: scheda del contatto e delle trattative del mittente, salvataggio della mail come nota, creazione di trattative e attività, campi personalizzati;
  - più fino a 21 giorni lavorativi di revisione Pipedrive e la verifica OAuth di Google.
- **Rischi:**
  - (a) Pipedrive migliora il suo add-on, trascurato da anni ma aggiornato a maggio 2026;
  - (b) l'interfaccia a card di Gmail è poco flessibile;
  - (c) ci sono due piattaforme da cui dipendere, ma nessuna delle due trattiene commissioni.

**6. Ricavi stimati a 12 mesi (prudente)**
- **Ipotesi:**
  - app pubblicata su entrambi i marketplace dal mese 3;
  - 12 installazioni al mese nei mesi 3-12 (10 da Pipedrive, 2 da Google), quindi circa 120;
  - prova gratuita di 14 giorni senza piano gratuito, con il 20% che passa a pagamento: circa 24 clienti;
  - 20 $/mese medi per account (12 $ un utente, 29 $ un team);
  - abbandono del 3% al mese.
- **Risultato:**
  - **circa 430-480 $ di ricavo mensile ricorrente al mese 12, circa 2.000 $ incassati nel primo anno**;
  - scenario ottimista (40 installazioni al mese, 25%, 25 $): circa 2.500 $ al mese;
  - scenario pessimista (meno di 5 installazioni al mese): meno di 150 $ al mese, quindi stop.

---

## Candidato 2: notifiche Jira in Google Chat
*Dove si vende: Atlassian Marketplace + Google Workspace Marketplace*

**Problema.** L'integrazione ufficiale fatta da Google è abbandonata. Gli utenti chiedono di filtrare le notifiche (per JQL o per passaggio di stato), di escludere le proprie azioni, di ricevere messaggi personali e di avere un thread per ogni ticket.

**1. Prove che la gente paga**
- Nell'equivalente per Microsoft Teams ci sono 4 app a pagamento con circa 9.300 installazioni:
  - yasoon "Microsoft 365 for Jira": 6.707 installazioni, **3,80 $/utente/mese** sopra i 10 utenti;
  - Move Work Forward Teams: 1.194 installazioni, 0,99 $/utente;
  - yasoon Teams: 840 installazioni, 2,10 $/utente;
  - Appfire: 594 installazioni, 1,52 $/utente.

  Fonte: API dei prezzi Atlassian, es. [yasoon](https://marketplace.atlassian.com/rest/2/addons/com.yasoon.jira.cloud/pricing/cloud/live).
- Su Atlassian si paga per tutti gli utenti del sito Jira: un sito da 50 utenti a 0,80 $ vale circa 40 $/mese.

**2. Lacuna**
- **Su Atlassian:** "Google Chat for Jira Cloud" (Google LLC) ha **10.998 installazioni, voto 2,3, 109 recensioni**. È gratuita, fatta su **Connect, con l'ultima versione dell'11/11/2021** ([scheda](https://marketplace.atlassian.com/apps/1218638/google-chat-for-jira-cloud)). Recensioni recenti:
  - 14/8/2026: «impossibile da configurare»;
  - 25/2/2026: «l'app è molto vecchia, la ricerca progetti e le notifiche non funzionano»;
  - 18/8/2025, 17/6/2025, 13/6/2025, 15/4/2025: errori di configurazione o notifiche non filtrabili.
- **Su Google:** "Jira for Google Chat" (Google) ha 1M+ utenti, voto 3,8; la scheda è ferma al 16/2/2024 ([scheda](https://workspace.google.com/marketplace/app/jira_for_google_chat/1063804824442)). Recensioni:
  - 16/3/2026 e 25/6/2026: nessun modo di escludere le proprie azioni, che Slack invece ha;
  - 28/2/2026: chiede la sincronizzazione ticket-thread;
  - 23/12/2025: «errori costanti e filtri solo per progetto intero».
- **Evento con data:**
  - le app Connect non possono più ricevere aggiornamenti da marzo 2026;
  - il supporto a Connect finisce il **31/1/2027**, dopo di che «le rotture aumenteranno»;
  - gli amministratori vedono già un avviso di fine supporto sulle app Connect ([Atlassian, 3/8/2026](https://www.atlassian.com/blog/developer/getting-ready-for-connect-end-of-support)).
- Google ha già marcato come "[Legacy]" la sua app gemella "Asana for Google Chat" (950K+ utenti).

**3. Concorrenza: c'è un motivo di scarto**
- **Move Work Forward, "Advanced Google Chat for Jira":** **gratuita**, Cloud Fortified, con filtri e messaggi personali ([guida del fornitore](https://www.moveworkforward.com/compare/google-chat-jira-integration-guide)). Ha 405 installazioni dal 14/3/2024.
- **Canary Apps:** 5 $ per 10 utenti, poi 1,20 $/utente; **123 installazioni in 32 mesi**.
- **Jigo (Seibert):** 137 installazioni, 2 $/utente.
- **Quota del leader:** circa il 94% delle installazioni della nicchia è sull'app abbandonata di Google.

**4. Distribuzione**
- Cercando "google chat" nella nicchia ci sono solo 6 app pertinenti: un'app nuova finirebbe in prima pagina.
- Ma la velocità storica è bassa: circa 4 installazioni al mese per Canary e circa 13 per MWF.
- Chi usa Google Chat cerca anche dal lato Google: "Jira Watcher" di Canary ha 26K+ utenti lì contro 123 installazioni su Atlassian.
- **Costo nascosto:** per pubblicare una vera app Chat serve un account Google Workspace a pagamento, circa 7 €/mese (requisito non verificato). Si può iniziare senza, con i webhook dei canali Chat, ma senza messaggi personali.

**5. Fattibilità: alta**
- App Forge con trigger sugli eventi Jira, filtri JQL e uscita verso l'API di Google Chat: 2-3 settimane.
- **Rischi:**
  - Google porta la sua app su Forge;
  - Atlassian crea un'integrazione ufficiale, come ha fatto per Slack e Teams;
  - la concorrenza gratuita di MWF.

**6. Ricavi stimati a 12 mesi (prudente)**
- **Ipotesi:**
  - 8 installazioni al mese dal mese 2, circa la metà del flusso storico di MWF più Canary, quindi circa 88;
  - il 15% paga, perché esiste MWF gratuita;
  - 32 $/mese medi.
- **Risultato:**
  - **circa 420 $ al mese al mese 12**;
  - se l'app di Google si rompe dopo il 31/1/2027 e il 3% delle sue 11k installazioni arriva da noi: circa 2.500 $ al mese.
- Commissione Atlassian 0%; pagamenti gestiti da Atlassian.

---

## Candidato 3: salvare le email di Gmail in Notion
*Dove si vende: Google Workspace Marketplace*

**Problema.** Salvare le email, allegati compresi, in un database Notion, a un prezzo onesto.

**1. Prove che la gente paga**
- Il leader "Gmail to Notion" ha **2M+ utenti** e fa pagare **16 $/mese** dopo 1 sola cattura gratuita ([scheda](https://workspace.google.com/marketplace/app/gmail_to_notion_save_emails_to_notion_da/798174831908)).
- Casi simili su Workspace: Notion2Sheets ha 66k installazioni e circa 5k $ al mese ([founderclub](https://www.founderclub.com/notion2sheets/)). Sync2Sheets è a 9k $ al mese ([Starter Story](https://www.starterstory.com/stories/sync2sheets-give-notion-the-superpowers-of-google-sheets)).

**2. Lacuna**
- Il leader ha voto **2,9** (76 recensioni) e la scheda è ferma al 13/2/2025. Le recensioni lamentano:
  - "non è gratis": 4/10/2026, 11/3/2026, 2/11/2025;
  - "salva solo il testo, niente immagini né file": 9/12/2025, 8/1/2026.
- "Save to Notion" (Digital Inspiration) ha 72K+ utenti, voto 2,2 e salva solo testo.

**3. Concorrenza in arrivo**
- **Quicktion:** 10K+ utenti, 25 recensioni, scheda aggiornata il 25/9/2026; allegati inclusi e 25 email/mese gratis ([scheda](https://workspace.google.com/marketplace/app/quicktion_save_emails_to_notion_google_s/898671993104)).
- **Mailtuck:** scheda del 2/9/2026, nata proprio sulla lacuna degli allegati ([scheda](https://workspace.google.com/marketplace/app/mailtuck/544587903941)), ma non compare nei risultati di ricerca.
- **Recensioni sospette:** gli stessi nomi ("Molly", "Wilson") recensiscono sia "Gmail to Notion" sia un'altra app Notion. Probabile manipolazione delle recensioni.

**4. Distribuzione.** È la più debole: le schede nuove restano sepolte sotto chi ha già milioni di utenti.

**5. Fattibilità**
- Alta: add-on Gmail con scope sensibile più API di Notion, che ora permette di caricare file.
- Rischi:
  - Notion (Notion Mail) o Gemini;
  - casi recenti di Google che rende nativa la funzione di un add-on: dal febbraio 2026 Google Forms limita da solo le risposte, e gli add-on "form limiter" da milioni di utenti perdono il motivo d'esistere ([TMU, 10/2/2026](https://www.torontomu.ca/google/news/2026/02/google-forms-introduces-native-response-limits)).

**6. Ricavi stimati (prudente)**
- **Ipotesi:** 300 installazioni in 10 mesi, il 3% passa a pagamento, 6 $/mese.
- **Risultato:**
  - **circa 50-100 $ al mese**;
  - scenario ottimista, sul modello di Quicktion (10K utenti, 2%, 8 $): circa 1.600 $ al mese.

---

## Scartato dopo verifica: domande e risposte in Confluence
*Alternativa a "Questions for Confluence" di Atlassian*

**A favore**
- L'app di Atlassian ha 3.513 installazioni e voto 3,0.
- Costa **2,50 $/utente/mese**.
- Lamentele recenti:
  - 18/3/2026: «le domande non si vedono da nessuna parte»;
  - 25/2/2026: «non funziona affatto»;
  - 4/12/2025: «non si può limitare chi risponde, la ricerca cerca solo nei titoli»;
  - 24/1/2025: «nessun import o export, nessuna API REST su Cloud».
- La n. 2, EliteSoft (641 installazioni), è su Connect e abbandonata (ultima versione 10/12/2024).

**Motivo dello scarto:** i tre nuovi arrivati del 2026 sono a quota **0, 0 e 3 installazioni**:
- ZanMind, dal 9/1/2026;
- NGPILOT "Modern Questions", dal 2/4/2026;
- Prometheus "Answers", dal 16/7/2026.

Esiste anche un'alternativa economica già affermata: Purde, a 0,44 $/utente, voto 4,4. Il marketplace non porta clienti nuovi in questa nicchia. C'è in più il rischio Rovo (l'AI di Atlassian risponde da sola alle domande).

## Altri esclusi o osservati, in breve
- **Shopify:** troppo affollato (2.713 app nuove al mese). L'evento utile sarebbe lo stop dei ScriptTag sulle vetrine dall'**1/3/2027** ([shopify.dev](https://shopify.dev/changelog/online-store-script-tags-deprecation)), ma non ho trovato un modo di individuare le app abbandonate che ne dipendono.
- **monday.com:**
  - il rapporto tra app e clienti è il migliore: 869 app per circa 245k clienti;
  - è a 0% di commissione fino a 200k$;
  - c'è un caso documentato: Pioneera, **30k $ al mese in "pochi mesi"** ([blog monday, 18/2/2025](https://monday.com/appdeveloper/blog/build-30k-saas-monday-marketplace/)).
  - Non ho però trovato una lacuna specifica con prove: il marketplace non espone dati per singola app e il forum è bloccato dal proxy. **Merita uno studio dedicato.**
- **Gmail che smette di scaricare la posta POP e chiude Gmailify (2026):** la domanda è enorme ([AlternativeTo, 10/2025](https://alternativeto.net/news/2025/10/google-is-ending-support-for-gmailify-and-pop-in-gmail-starting-january-2026)), ma gli utenti cercano su Google e non nel marketplace. In più lo scope necessario (`gmail.insert`) è ristretto, quindi serve l'audit CASA a pagamento.
- **Colori degli stati in Jira:** le app esistenti hanno voto 2,2-2,3 perché la piattaforma non lo consente (serve un'estensione Chrome). Infattibile.

---

## Classifica

| # | Candidato | Prove di pagamento | Lacuna datata | Alternativa gratuita forte | Traffico dimostrato per un nuovo arrivato | Rischio piattaforma | Ricavo mensile al mese 12 (prudente → ottimista) |
|---|---|---|---|---|---|---|---|
| **1** | **Barra Pipedrive in Gmail** (Workspace + Pipedrive) | Sì (app Outlook a pagamento: 266 e 78 valutazioni) | Sì (gen-apr 2026) | **No** | Parziale: marketplace piccolo, nessun concorrente terzo; volumi non pubblici | Medio | ~450 $ → 2.500 $ |
| 2 | Notifiche Jira in Google Chat (Atlassian + Workspace) | Sì (Teams: ~9.300 installazioni a pagamento) | Sì (2025-2026) + scadenza Connect 31/1/2027 | **Sì (MWF gratuita)** | Basso: 4-13 installazioni al mese per i concorrenti | Medio | ~420 $ → 2.500 $ (solo se l'app di Google si rompe) |
| 3 | Gmail → Notion (Workspace) | Sì (leader a 16 $/mese, 2M+ utenti) | Sì (2025-2026) | Parziale (Quicktion: 25 email/mese gratis) | No: le schede nuove restano sepolte | Alto | ~75 $ → 1.600 $ |
| – | Domande e risposte in Confluence | Sì (2,50 $/utente) | Sì | Economica (0,44 $) | **No: 0/0/3 installazioni per i nuovi** | Alto (Rovo) | scartato |

## Verdetto
**Il migliore è il candidato 1: la barra laterale Pipedrive per Gmail, pubblicata sia nel Pipedrive Marketplace sia in quello di Google Workspace.**

È l'unico che rispetta tutte e tre le condizioni della regola:
- c'è domanda di chi già paga, dimostrata dall'equivalente per Outlook;
- l'app più usata è scadente (2,1 su 83K+ utenti, con recensioni del 2026);
- non c'è un'alternativa gratuita forte, e nel Pipedrive Marketplace nessun terzo copre Gmail;
- il marketplace è piccolo (509 app), quindi un nuovo arrivato si vede.

Il candidato 2 ha l'evento più forte (scadenza Connect), ma ha un concorrente gratuito ben fatto. Va tenuto come seconda scelta: tornerà interessante se l'app di Google smette di funzionare dopo il 31/1/2027.

**Avvertenza onesta.** Nessun candidato ha prove di poter superare 2.500 $ al mese in 12 mesi con il solo traffico del marketplace. La base storica è coerente: la mediana di un'app Shopify era 725 $ al mese ([analisi 2021](https://spur-i-t.com/blog/shopify-app-store-analysis-2021/)), e Agile Docs su Atlassian è arrivata a 4.149 $ al mese dopo 18 mesi ([IH, 2020](https://www.indiehackers.com/post/reaching-4149-mrr-in-the-atlassian-marketplace-a3cc93a067)). Le app di marketplace sono un modo per ottenere i **primi clienti** senza pubblico, non un modo rapido per arrivare a 5.000 € al mese.

## Test di validazione a costo zero (il più rapido)
Il dubbio che conta è se il Pipedrive Marketplace porta installazioni da solo. L'unico modo di saperlo è essere pubblicati: una landing page non lo misura. Pubblicare è gratis.

1. **Giorni 1-10.** Claude costruisce un MVP minimo:
   - barra laterale con contatto, trattative e campi personalizzati del mittente;
   - "salva la mail come nota";
   - "crea trattativa o attività".

   Poi lo invia alla revisione del Pipedrive Marketplace e alla verifica OAuth di Google. Costo: 0 €. Si usa solo lo scope `gmail.addons.current.message.readonly`, quindi niente audit CASA.
2. **In parallelo (giorni 1-14).** Massimiliano risponde nel [thread ufficiale "Gmail addon"](https://community.pipedrive.com/discussion/comment/37692) e nella sezione idee del forum Pipedrive, con un link a una pagina che raccoglie iscrizioni in lista d'attesa. È un segnale secondario.
3. **Soglia di decisione, entro 30 giorni dalla pubblicazione:**
   - **almeno 15 installazioni** arrivate dalla ricerca del marketplace;
   - **almeno 3 prove gratuite** convertite in pagamento entro 45 giorni.

   Se non si raggiungono, stop. A quel punto si passa al candidato 2 con lo stesso schema (MVP Forge gratuito, soglia di installazioni a 30 giorni), da far coincidere con la scadenza Connect del 31/1/2027.

**Da chiarire prima di incassare:** come gestire in regime forfettario gli incassi Stripe in USD da clienti esteri, come già segnalato nello studio H.

## Verifica aggiuntiva (9/10/2026): costi di approvazione Google per il candidato 1
- Lo scope `gmail.addons.current.message.readonly` (leggere l'email aperta mentre l'add-on è attivo) è classificato **Sensitive**, non Restricted: https://developers.google.com/workspace/gmail/api/auth/scopes
- Gli scope Sensitive richiedono la verifica OAuth di Google (gratuita); la valutazione di sicurezza CASA (a pagamento) riguarda gli scope Restricted (`gmail.readonly`, `gmail.modify`, `mail.google.com`) — fonte non ufficiale: https://www.unipile.com/gmail-api-scopes-guide/
- **Vincolo di progetto:** usare solo scope add-on (current message), mai scope Restricted, per restare a costo zero. Da riconfermare nella console Google prima della pubblicazione.

## BLOCCO FISCALE (9/10/2026) — vale per qualsiasi SaaS
Regola di Massimiliano: si procede solo se basta aggiungere un codice ATECO alla P.IVA da fotografo (74.20.19, Gestione Separata); **no** se servono Camera di Commercio e contributi fissi (~3.000 €/anno).
- Vendere abbonamenti a un software proprio a molti clienti = probabilmente "edizione di software" (ATECO 58.29.00), attività commerciale → iscrizione CCIAA + INPS Gestione Commercianti con minimale fisso. Fonti: https://fidocommercialista.it/edizione-di-software , https://www.studiomicera.it/vendere-saas-partita-iva-developer-2026/
- 62.10.00 (programmazione, ex 62.01) resta in Gestione Separata ma copre lo sviluppo su commessa, non la vendita di un prodotto a catalogo: https://www.fiscozen.it/guide/codice-ateco-programmatore-informatico/
- Le fonti non sono concordi; serve parere di un professionista prima di costruire.
- Strada da far verificare: vendita tramite "merchant of record" (Paddle / Lemon Squeezy) con compensi come licenza/diritti d'autore sul software. NON verificata.
**Stato: costruzione sospesa finché un professionista non conferma la strada senza CCIAA.**
