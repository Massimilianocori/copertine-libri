# 6. Test di facilità: trovare i primi 3 utenti per un'app HubSpot (12 ottobre 2026)

Domanda: se costruiamo una piccola app per HubSpot (studio 5), è **facile** trovare le prime 3 installazioni attive senza andare a caccia di clienti? Massimiliano accetta solo di copiare e incollare risposte già pronte, circa 15 minuti al giorno, con una guida passo per passo.

Il test: contare le richieste **pubbliche, recenti (aprile 2025 - ottobre 2026) e con data** in cui qualcuno chiede una funzione che una sola piccola app potrebbe dare. Poi leggere le regole dei forum per capire se rispondere citando la propria app è permesso.

---

## 1. Verdetto

**DIFFICILE.** Nessun bisogno ha 30 o più richieste recenti, votate e ancora senza soluzione: il gruppo più grande (associazioni automatiche tra record) ha 69 richieste, ma con pochissimi voti (38 in tutto su 57 discussioni) e 33 già risolte nella discussione stessa.

Il canale "chiedo 3 installazioni" è intasato: nella Community HubSpot 39 sviluppatori l'hanno chiesto in 12 mesi e la risposta mediana è **1**; su Reddit funziona meglio, ma servono messaggi privati e conversazioni, cioè proprio la "caccia" che Massimiliano non vuole fare.

Se si va avanti comunque, il test indica come prima app un'**azione per i workflow che crea, toglie ed etichetta le associazioni con regole di abbinamento** (la domanda più ampia), non l'iscrizione alle sequenze (idea n. 1 dello studio 5), dove due concorrenti rispondono già in quasi tutte le discussioni.

---

## Come ho raccolto i dati (12/10/2026)

- **Community HubSpot** (community.hubspot.com). Dal 2025 il forum usa un nuovo software, che ha anche una versione dati delle pagine pubbliche. L'accesso diretto è bloccato dal proxy (pagina anti-robot, errore 403), quindi ho letto le stesse pagine pubbliche attraverso un servizio di lettura web.
  - circa 90 ricerche su 12 bisogni, filtrate dal 12/4/2025 in poi: **2.354 messaggi trovati**.
  - Per 119 discussioni candidate ho letto la scheda completa: voti, risposte, soluzione accettata, app concorrenti citate.
- **Reddit r/hubspot.** reddit.com è bloccato (errore 403). Ho usato l'archivio pubblico Arctic Shift: **3.936 post dal 12/4/2025 al 12/10/2026**, di cui 595 rimossi (15%). Punteggi e numero di commenti sono quelli salvati dall'archivio: possono essere più bassi di quelli attuali.
- **Stack Overflow** (API pubblica): solo **2 domande** con l'etichetta "hubspot" dal 12/4/2025. È una fonte morta.
- **Bloccati:** G2 (403), reddit.com (403, anche tramite il servizio di lettura), legal.hubspot.com e redditinc.com (non raggiungibili). Capterra non l'ho provato: le recensioni dei collegamenti ufficiali erano già nello studio 5.
- **Installazioni dei concorrenti:** dallo studio 5 (catalogo del 12/10/2026) oppure dalla scheda pubblica del marketplace letta il 12/10/2026, che mostra cifre arrotondate (es. "3K").
- **Limiti.**
  - La ricerca del forum restituisce al massimo 50 messaggi per pagina; ne ho letto fino a 3 pagine per ricerca. Per i gruppi grandi i conteggi sono quindi un **minimo**.
  - Per 3 gruppi ho controllato le discussioni una per una (associazioni, sequenze, Stripe). Per gli altri il conteggio viene dai titoli: è una stima.

---

## 2. Tabella dei bisogni

Periodo: dal 12/4/2025 al 12/10/2026. "C" = Community HubSpot, "R" = r/hubspot.

| Bisogno (cosa farebbe l'app) | Richieste trovate | Voti e risposte | Più recente | Concorrenti già presenti (installazioni) | Nostra probabilità |
|---|---|---|---|---|---|
| **Associazioni automatiche nei workflow**: crea o toglie un collegamento tra record e mette l'etichetta, abbinando per dominio, per un campo qualsiasi o tramite un terzo record | **57 C** (49 persone diverse, 23 nel forum Ideas) + **12 R** = **69**. Controllate una per una | 38 voti in tutto, solo 4 discussioni con 3 voti o più; 106 risposte; **33 su 57 hanno già una soluzione accettata** | C 31/8/2026, R 14/9/2026 | Associ8 di hapily, **circa 3.000** (scheda, 12/10/2026). Workflow Associations Manager di Integration Glue: una delle sue 4 app, che hanno 536-612 installazioni ciascuna (studio 5). Nuove app in prova nel 2025-2026 (R 22/6/2025, R 5/4/2026, C 3/4/2026). HubSpot ha in prova privata le associazioni "attraverso un record intermedio" (R 26/8/2026) | **Medio-bassa** |
| Calcoli su date (giorni tra due date, "giorni da", date che si aggiornano da sole) | circa 33 C (dai titoli, non verificate una per una) + circa 3 R | voti bassi | C 29/9/2026 | Workflow Date Calculator **1.159** (studio 5). Calcoli di Integration Glue, circa 550-610 (studio 5). Proprietà calcolate native nei piani Pro | Bassa |
| **Iscrizione alle sequenze da workflow senza Enterprise** (idea n. 1 dello studio 5) | circa **15 richieste esatte** e circa 15 simili in C + **2 R**. Controllate una per una | L'idea del 2017 ha **780 voti**, ma dal 4/2025 ha ricevuto 1 solo messaggio. Le richieste recenti hanno 0-18 voti | C 3/8/2026, R 23/2/2026 | Enrollem **1.823**, FlowNer **175** (studio 5). I loro venditori rispondono già in **10 delle 33 discussioni controllate** e su Reddit | **Bassa** |
| **Stripe → HubSpot** con abbonamenti e prodotti (idea n. 2 dello studio 5) | circa **16 C** + **11 R** (6 persone; una sola ne ha scritti 6) | Le richieste recenti hanno 0 voti; le vecchie idee del 2019 ne hanno 121 e 89 | R 7/10/2026 | Stripe Data Sync ufficiale **14.256**, voto 2,13; hapily 267, ClearSync 95, Finrite 56 (studio 5). **Due nuove app in prova dal 17/8/2026** (C: 0 risposte; R: 1 interessato) | Medio-bassa |
| Prodotti nei workflow (creare, copiare, aggiornare righe di prodotto, clonare offerte) | circa 18 C (dai titoli) + circa 5 R | voti bassi | C 12/10/2026 | Clonazione di Integration Glue (studio 5); in più HubSpot ha introdotto la funzione nativa "duplica record" (R 4/7/2025) | Bassa |
| Formattazione dei dati (maiuscole, unione di testi, formati) | circa 18 C (dai titoli), quasi 0 R | voti bassi | C 2/7/2026 | Data Format Actions di Integration Glue (studio 5); "Format data" nativo nei piani Data Hub | Bassa: domanda scarsa |
| Duplicati | molte | — | R 10/8/2026 | Koalify 4.927, Insycle 7.095, Dedupely 3.921 (studio 5). In più **4 nuove app in prova nel 2026** (R 7/8 e 10/8, C 17/8 e 9/10) | Molto bassa |
| Backup e ripristino | circa 7 C + circa 4 R | — | R 12/8/2026 | ProBackup 681 (studio 5). HubSpot ha aggiunto il ripristino delle associazioni (R 20/10/2025) e l'annullamento delle modifiche di un'integrazione (R 22/6/2026) | Bassa |

**Cosa dice la tabella.**
- Le richieste sono **sparse**: tanti bisogni simili, ognuno con poche richieste e pochissimi voti.
- Nei gruppi più chiari (sequenze, Stripe) i concorrenti sono già dentro le discussioni.
- Il gruppo più grande (associazioni) è anche quello dove HubSpot sta aggiungendo funzioni native.

---

## 3. Lista per il gruppo migliore: associazioni automatiche (40 discussioni)

Legenda: **Ris.** = la discussione ha già una soluzione accettata (sì/no). **Risp.** = numero di risposte. Ordine: prima le richieste ancora aperte, poi le altre, dalla più recente.

**Attenzione:** questa lista NON è da usare tutta per proporre l'app. Le regole (sezione 4) sconsigliano di incollare messaggi nelle discussioni vecchie o già risolte. Va usata per scrivere un testo di presentazione che risponda proprio a questi casi. Le discussioni aperte e recenti (le prime 20) sono le uniche in cui una risposta è naturale.

### Ancora aperte (nessuna soluzione accettata)

| # | Data | Dove, autore | Bisogno | Voti / Risp. |
|---|---|---|---|---|
| 1 | 14/9/2026 | [R, Nylacinad](https://www.reddit.com/r/hubspot/comments/1wgii50/) | Collegare in automatico il contatto dell'azienda a tutti i ticket dell'help desk | 3 punti / 9 comm. |
| 2 | 13/8/2026 | [C Ideas, ETu](https://community.hubspot.com/t/improve-automatic-company-association-by-supporting-website-domain-matching-when-email-domain-differ/156021) | Collegare contatto e azienda anche quando il dominio email è diverso dal sito | 3 / 2 |
| 3 | 10/8/2026 | [C Ideas, gtuerk_gpc](https://community.hubspot.com/t/create-association-labels-without-matching/155676) | Mettere un'etichetta di associazione usando un'altra associazione, senza codice | 2 / 2 |
| 4 | 29/7/2026 | [C Ideas, Arsath](https://community.hubspot.com/t/root-domain-based-company-association-to-prevent-duplicate-companies/154575) | Collegare per dominio principale (es. eu.acme.com → acme.com), senza creare aziende doppie | 0 / 2 |
| 5 | 28/7/2026 | [C Ideas, IreneAe](https://community.hubspot.com/t/allow-updating-and-removing-association-labels-using-matching-properties-in-workflows/154440) | Aggiornare o togliere etichette abbinando i record per campo | 0 / 0 |
| 6 | 20/7/2026 | [C Ideas, EBeatrix](https://community.hubspot.com/t/allow-bulk-association-of-records-using-lists-or-segments/153488) | Collegare in blocco i record di una lista o di un segmento | 0 / 0 |
| 7 | 28/5/2026 | [C Ideas, PJur](https://community.hubspot.com/t/native-record-lookup-and-record-by-id-actions-in-workflows/149808) | Nel workflow: cercare un record e agire su quello trovato, senza codice | 3 / 1 |
| 8 | 28/4/2026 | [C, CHerdeg](https://community.hubspot.com/t/creating-a-property-that-associates-through-matching-numbers-in-hubspot/148777) | Collegare righe di prodotto e ordini abbinando il numero d'ordine | 0 / 2 |
| 9 | 27/4/2026 | [C Ideas, AllisonL](https://community.hubspot.com/t/feature-request-auto-associate-company-level-meetings-to-open-tickets-in-a-specified-pipeline/148754) | Collegare le riunioni dell'azienda ai suoi ticket aperti | 0 / 0 |
| 10 | 23/4/2026 | [C Ideas, tz18392](https://community.hubspot.com/t/apply-engagement-auto-association-rules-to-third-party-created-activities/148642) | Applicare le regole di collegamento anche alle attività create da altre app | 0 / 0 |
| 11 | 8/4/2026 | [R, imurkween](https://www.reddit.com/r/hubspot/comments/1sfmobw/) | Nel workflow, trovare i contatti collegati a un altro contatto con una certa etichetta | 5 / 5 |
| 12 | 27/3/2026 | [C Ideas, AWeed](https://community.hubspot.com/t/enable-associate-all-associated-notes-when-a-lead-based-workflow-creates-a-deal/147771) | Quando un workflow crea un'opportunità da un lead, portarsi dietro le note | 1 / 1 |
| 13 | 21/3/2026 | [C Ideas, FMimo_1](https://community.hubspot.com/t/flexible-contact-to-company-association-rules-beyond-domain-matching-make-contact-to-company-associ/147532) | Regole flessibili contatto-azienda, oltre il dominio email | 2 / 0 |
| 14 | 13/3/2026 | [C Ideas, Sarah8Medilo](https://community.hubspot.com/t/automatically-associate-help-desk-email-replies-with-the-company-record/147237) | Collegare all'azienda le risposte email dei ticket | **20** / 1 |
| 15 | 7/3/2026 | [R, Open_Butterscotch_87](https://www.reddit.com/r/hubspot/comments/1rn2zev/) | Collegare in blocco abbonamenti e oggetti personalizzati | 3 / 5 |
| 16 | 5/3/2026 | [R, Qin_Kanki](https://www.reddit.com/r/hubspot/comments/1rlfmca/) | Aiuto per un workflow di associazioni | 1 / 1 |
| 17 | 23/1/2026 | [C Ideas, andyvb](https://community.hubspot.com/t/more-customizable-selection-for-association-labels-in-workflow/145329) | Aggiornare solo alcune etichette di associazione, non tutte | 0 / 0 |
| 18 | 31/12/2025 | [C Ideas, zqevgaz](https://community.hubspot.com/t/allow-true-multi-select-for-is-any-of-filters-in-apply-association-labels-workflow-actions/144476) | Filtro a scelta multipla nell'azione "applica etichette" | 0 / 0 |
| 19 | 12/12/2025 | [C Ideas, Burobert](https://community.hubspot.com/t/workflows-processor-to-create-associations-between-objects-which-are-not-enrolled/143982) | Collegare due record che non sono quello del workflow | 0 / 0 |
| 20 | 10/12/2025 | [R, No-External-7722](https://www.reddit.com/r/hubspot/comments/1pj8oy5/) | Collegare contatti e aziende | 1 / 9 |
| 21 | 23/10/2025 | [R, iced_milk](https://www.reddit.com/r/hubspot/comments/1oe8yg8/) | Togliere l'associazione "principale" con un workflow | 2 / 3 |
| 22 | 17/8/2025 | [R, Altruistic_Back_7356](https://www.reddit.com/r/hubspot/comments/1mt471b/) | Impostare l'azienda principale del contatto in base al dominio email | 3 / 6 |
| 23 | 25/7/2025 | [C Ideas, CHansenFrazil](https://community.hubspot.com/t/increase-limit-on-create-record-association-workflow-action/136918) | Superare il limite nascosto di 100 collegamenti per azione | 1 / 0 |
| 24 | 23/7/2025 | [C Ideas, Stevie-Kv](https://community.hubspot.com/t/workflow-action-create-associations-match-on-additional-emails-too/136717) | Abbinare anche sugli indirizzi email secondari | 3 / 0 |
| 25 | 22/7/2025 | [R, Altruistic_Back_7356](https://www.reddit.com/r/hubspot/comments/1m6h22u/) | Collegare in automatico un'opportunità a un record di oggetto personalizzato | 3 / 7 |
| 26 | 7/7/2025 | [C Ideas, ABeney](https://community.hubspot.com/t/have-option-in-workflow-to-choose-specific-objects-to-remove-or-change-association-labels/135761) | Scegliere su quali record togliere o cambiare l'etichetta | 0 / 0 |
| 27 | 23/5/2025 | [C Ideas, RRoseberg58](https://community.hubspot.com/t/automatically-add-association-label-to-first-associated-record-in-workflows/133299) | Etichettare il "primo" record collegato | 1 / 0 |
| 28 | 30/4/2025 | [C Ideas, pm_di](https://community.hubspot.com/t/allow-approximate-matching-for-create-association-or-edit-record-in-workflows/130884) | Abbinamento non esatto (nomi simili) per creare collegamenti | 0 / 0 |
| 29 | 29/4/2025 | [C Ideas, Jigar_Thakker](https://community.hubspot.com/t/enable-copying-of-associations-between-custom-objects-in-workflows/130753) | Copiare i collegamenti da un oggetto personalizzato a un altro | 2 / 0 |

### Con una soluzione accettata (spesso un rimedio parziale o codice)

| # | Data | Dove, autore | Bisogno | Risp. |
|---|---|---|---|---|
| 30 | 31/8/2026 | [C, cclark2](https://community.hubspot.com/t/what-is-the-best-way-to-auto-associate-companies/157597) | Collegare in automatico le aziende a opportunità create da un altro software | 2 |
| 31 | 20/8/2026 | [C, GCluster](https://community.hubspot.com/t/workflow-that-associates-companies-and-contacts-when-both-are-associated-to-the-same-custom-object/156676) | Collegare contatti e aziende legati allo stesso oggetto personalizzato | 1 |
| 32 | 20/8/2026 | [C, cclark2](https://community.hubspot.com/t/can-you-de-associate-objects-through-workflows/156666) | Togliere un collegamento con un workflow (nella risposta: Associ8) | 1 |
| 33 | 16/7/2026 | [C, CMRs](https://community.hubspot.com/t/automatically-associate-contacts-with-a-parent-company/153243) | Collegare i contatti all'azienda madre | 3 |
| 34 | 30/6/2026 | [C, PPob12](https://community.hubspot.com/t/workflow-to-auto-create-association-label-on-deal/151745) | Mettere un'etichetta alle opportunità di una pipeline | 3 |
| 35 | 26/6/2026 | [C, ycarvin_HH](https://community.hubspot.com/t/match-associated-records-based-on-equal-property-values/151500) | Abbinare i record collegati con lo stesso valore di un campo | 4 |
| 36 | 26/5/2026 | [C, BWarren](https://community.hubspot.com/t/remove-associations-between-tickets-and-companies-contacts/149714) | Togliere i collegamenti ticket-azienda creati in automatico | 4 |
| 37 | 20/5/2026 | [C, AAbu-Farha](https://community.hubspot.com/t/associate-contacts-that-are-associated-with-companies-with-deals/149514) | Collegare all'opportunità i contatti dell'azienda | 1 |
| 38 | 27/4/2026 | [C, candicesanjuan](https://community.hubspot.com/t/associate-contact-to-company-via-custom-object-assocation/148737) | Collegare contatto e azienda tramite un oggetto intermedio | 3 |
| 39 | 26/3/2026 | [C, BKnightSSE](https://community.hubspot.com/t/company-rebranded-and-has-two-email-domains-to-associate-with-contacts/147717) | Azienda con due domini email | 4 |
| 40 | 20/3/2026 | [C, CSchenk](https://community.hubspot.com/t/associate-all-contacts-associated-to-a-company-to-any-new-deal-via-workflow/147514) | Collegare tutti i contatti dell'azienda a ogni nuova opportunità | 2 |

Le altre 29 richieste del gruppo (25 nella Community e 4 su Reddit, quasi tutte già risolte) sono nei dati di lavoro e si possono rigenerare. Le discussioni 31, 37 e 38 sono proprio il caso che HubSpot sta rendendo nativo ("associazioni attraverso un record intermedio", in prova privata, [R 26/8/2026](https://www.reddit.com/r/hubspot/comments/1vyz47h/)).

### In più: richieste esatte per l'idea "sequenze senza Enterprise"

Sono 15 in 18 mesi: 13 nella Community e 2 su Reddit. In 4 di queste discussioni della Community e nel post Reddit di febbraio, FlowNer o Enrollem hanno già risposto con il link alla loro app; lo stesso è successo in almeno altre 6 discussioni più vecchie.
- 3/8/2026 [SPG_Chris](https://community.hubspot.com/t/filter-contacts-by-call-outcome-in-list-builder-is-this-possible-on-pro/155088)
- 30/4/2026 [MolAlyH](https://community.hubspot.com/t/enroll-deals-in-sequences/148902)
- 13/4/2026 [HRichthe2nd](https://community.hubspot.com/t/enrolling-contact-lists-in-sales-email-sequences-on-behalf-of-a-sales-rep/148278) (FlowNer ha risposto)
- 23/3/2026 [AEatmon](https://community.hubspot.com/t/enrolling-contacts-on-the-second-step-of-a-sequence-using-a-workflow/147584)
- 18/3/2026 [RLee23](https://community.hubspot.com/t/automatically-enroll-a-contact-in-a-sequence-from-a-deal/147428) (FlowNer)
- 23/2/2026 [R NorthShoreHard](https://www.reddit.com/r/hubspot/comments/1rc9dx4/): «non voglio pagare un altro prodotto» (Enrollem ha risposto il 18/3/2026)
- 18/12/2025 [JVermunt](https://community.hubspot.com/t/unenrolling-from-sequence-when-quote-is-signed/144219)
- 4/12/2025 [DMcLaren4](https://community.hubspot.com/t/workflow-sequencing/143691)
- 15/10/2025 [R bobdiamond](https://www.reddit.com/r/hubspot/comments/1o7jubp/)
- 18/9/2025 [HugoDosSantos](https://community.hubspot.com/t/enroll-a-contact-in-sequence-with-workflow-even-when-selecting-base-object-deals/139750) (0 risposte)
- 31/7/2025 [MCarlson99](https://community.hubspot.com/t/setting-up-sequences-on-behalf-of-other-users/137209) (18 voti; FlowNer)
- 1/7/2025 [JRank9](https://community.hubspot.com/t/automatically-enrol-in-sequence/135478)
- 18/6/2025 [HMay301](https://community.hubspot.com/t/automatically-set-follow-ups/134733) (FlowNer)
- 15/5/2025 [USotomayor](https://community.hubspot.com/t/no-show-workflow/132792)
- 15/4/2025 [TThomas0](https://community.hubspot.com/t/add-lists-and-event-based-automations-to-sequences/129966)

### In più: Stripe (le più chiare)
- [R Future-Network-634](https://www.reddit.com/r/hubspot/comments/1wzzp3w/), 7/10/2026: prodotti creati in un solo verso, prezzi mensili mancanti. La stessa persona ha scritto altri 5 post tra 9/2026 e 10/2026.
- [C TracyLew22](https://community.hubspot.com/t/hubspot-payments-commerce-subscription-management/155937), 12/8/2026.
- [R Lumpy-Tower5803](https://www.reddit.com/r/hubspot/comments/1tvu4ai/), 3/6/2026: «qualcuno fattura in Stripe con HubSpot CRM?».
- [C CarstenK](https://community.hubspot.com/t/pushing-stripe-payments-into-hubspot-for-reporting/141110), 15/10/2025.
- [C mwh](https://community.hubspot.com/t/can-stripe-sync-automatically-update-hubspot-contact-records/140338), 30/9/2025: ClearSync ha già risposto.
- [C RichMai](https://community.hubspot.com/t/how-can-i-edit-subscriptions-in-hubspot-1-or-3-months-after-the-subscription-stasrts/133945), 4/6/2025: hapily ha già risposto.

---

## 4. Regole: si può rispondere citando la propria app?

### Community HubSpot: sì, ma solo se risolve proprio quel problema

Fonte: pagina ufficiale «[Third-Party App Promotion: Community Content Best Practices](https://community.hubspot.com/t/third-party-app-promotion-community-content-best-practices/123187)», creata il 2/1/2025 e aggiornata il 9/9/2026. Dice (testo originale):
- «App partners can share their solutions when it directly addresses a user's specific question or pain point» (si può citare l'app quando risponde proprio al problema di chi chiede).
- «App partners should avoid unsolicited promotion and focus on relevance and providing value to the conversation».
- Se HubSpot ha già una soluzione nativa, bisogna dirlo e spiegare cosa aggiunge l'app; se non ce l'ha, bisogna spiegare quale lacuna copre l'app.
- Da non fare: «Copy paste the same message into older threads», cioè incollare lo stesso messaggio nelle discussioni vecchie senza spiegare come l'app risolve il problema di chi ha scritto. Conseguenza dichiarata: il messaggio rischia di sparire quando archiviano le discussioni vecchie.
- I post che presentano un'app vanno nella bacheca apposita, «Third-Party App Board» (oggi la sezione "Marketplace Apps").

Fonte: «[HubSpot Community Guidelines](https://community.hubspot.com/t/hubspot-community-guidelines/27610)», aggiornate il 25/8/2026:
- «Keep your comments constructive and relevant to the topic.» I moderatori possono togliere contenuti non pertinenti o sbagliati, «created either by humans or AI», e sospendere l'account.
- «**Please disclose that your content was assisted by AI** and check the accuracy of the information before posting.» **Importante per noi:** le risposte preparate dall'agente vanno dichiarate come scritte con l'aiuto dell'IA.
- Ogni account deve essere di una sola persona reale, niente account aziendali.

**Cosa succede davvero ai post "cerco tester".** Nella sezione Marketplace Apps ho contato **39 post di sviluppatori in 12 mesi** (12/10/2025 - 12/10/2026) che cercano tester o le 3 installazioni. Da luglio 2026 ne arrivano 4-8 al mese.
- **Risposte mediane: 1.** In 16 casi le risposte sono **zero**.
- Esempi: «Looking for beta testers — Stripe ↔ HubSpot sync» (17/8/2026), 0 risposte; «Looking for 3 beta testers for PropSweep — free Pro access for a year» (27/4/2026), 0 risposte.
- Spesso l'unica risposta arriva da un altro sviluppatore nella stessa situazione, che installa per aiutare (discussione di [greg.thingz, 19/7/2026](https://community.hubspot.com/t/need-help-meeting-the-3-active-installs-requirement-for-first-time-marketplace-submission/153422)).

### r/hubspot: citare la propria app solo se qualcuno lo chiede

Regola n. 3 del subreddit, «No Spam or Self-Promotion» (letta dall'archivio Arctic Shift; versione salvata il 26/1/2025, regola creata il 29/8/2024):
> «Posts or comments that promote specific software, services, or products **without being directly requested by another user** are considered self-promotion and will be removed. Instead, focus on contributing meaningful educational content directly within your post or comment.»

**Cosa succede davvero.**
- **43 post "cerco tester / mi servono 3 installazioni" in 12 mesi, 14 rimossi (33%).**
- Dei 26 rimasti visibili di cui ho letto i commenti, **14 hanno ricevuto 5 o più commenti** da altre persone. Il migliore: «Built a HubSpot app solo… now I need 3 real installs» ([TrueTax975, 17/7/2026](https://www.reddit.com/r/hubspot/comments/1uzbphh/)), con circa 6 persone che si sono offerte («happy to help», «DM me»).
- Funziona meglio della Community, ma tutto passa da **messaggi privati** e da conversazioni una per una.
- Anche il venditore di Enrollem risponde su Reddit con il link all'app, e la sua risposta non è stata rimossa ([18/3/2026](https://www.reddit.com/r/hubspot/comments/1rc9dx4/)).

### Cosa conta come "installazione attiva" (regola applicata dal 19/8/2026)

Fonte: [annuncio ufficiale nella Community, 18/8/2026](https://community.hubspot.com/t/changes-to-marketplace-submission-flow-how-active-installs-are-determined/156427).
- Serve un **account cliente vero** con attività riuscita dell'app negli **ultimi 30 giorni**.
- Non valgono gli account sviluppatore, di test, le sandbox e gli account nostri, anche se gratuiti.
- Quindi non basta che qualcuno installi l'app: deve **usarla davvero**. Per un'azione dei workflow significa creare e attivare un workflow che la usa.
- Prima della pubblicazione chi installa vede l'avviso di app non verificata ("I accept the risk"). Due sviluppatori dicono che è un ostacolo vero (Community, 19/7/2026 e 20/7/2026).

### Il modo giusto, non invadente
1. **Un solo post di presentazione** nella sezione Marketplace Apps della Community: cosa fa l'app, quale lacuna copre, offerta di 1 anno gratis ai primi 5 team in cambio di 2 giri di commenti, nota "testo scritto con l'aiuto dell'IA".
2. **Un solo post su r/hubspot**, con contenuto utile: come risolvere il problema delle associazioni con gli strumenti nativi, e alla fine "sto costruendo un'app per i casi che restano, cerco 3-5 tester". È il formato che ha funzionato meglio. Rischio di rimozione: circa 1 su 3.
3. **Risposte solo nelle discussioni nuove** (meno di 30 giorni) e ancora aperte. Prima la soluzione nativa, poi l'app come alternativa per il caso che resta scoperto. Niente testo identico ripetuto, niente risposte nelle discussioni vecchie o già risolte.

---

## 5. Come sarebbe la giornata di Massimiliano (realistico)

Quanto spesso arrivano richieste nuove nel gruppo migliore: **11 discussioni negli ultimi 3 mesi** (12/7/2026 - 12/10/2026) nella Community, cioè circa **una a settimana**. Su Reddit circa una al mese. Quindi **non c'è materiale per rispondere tutti i giorni**.

| Quando | Cosa fa | Tempo |
|---|---|---|
| Giorno 1 | Copia il post di presentazione nella Community (sezione Marketplace Apps) e quello per r/hubspot | 20-30 min |
| Ogni giorno, settimane 1-6 | Legge risposte e messaggi privati. Incolla le risposte preparate dall'agente. Manda il link di installazione a chi è interessato | 10-15 min, ma solo se qualcuno ha scritto |
| Una volta a settimana | Risponde a 1 discussione nuova del gruppo (la lista la prepara l'agente) | 10 min |
| Per ogni volontario | Lo aiuta a creare e attivare il workflow con la nostra azione, altrimenti l'installazione non conta come "attiva" | 20-40 min in tutto, con scambi di messaggi |

**Stima onesta (ipotesi, non dato):** da 2 a 6 settimane per arrivare a 3 installazioni attive, senza garanzia.
- Dal campione della Community: risposta mediana 1, molti zero.
- Su Reddit circa metà dei post riceve 5 o più commenti, ma un terzo viene rimosso.
- In tutto 2-4 ore, in gran parte **conversazioni private** con sconosciuti.

È proprio il lavoro "da venditore" che la decisione del 12/10/2026 (studio 5) esclude. Per questo il verdetto resta **DIFFICILE**.

**Unica scorciatoia vista nei dati:** lo scambio di installazioni tra sviluppatori che hanno lo stesso problema. Ci sono offerte pubbliche su Reddit (23/9/2026 e 25/9/2026) e nella Community (20/7/2026). Vale solo se il loro account HubSpot è un account aziendale vero e l'app viene usata davvero, come chiede la regola del 18/8/2026. Altrimenti è un rischio per la pubblicazione: non la consiglio come base.

---

## Fonti principali (consultate il 12/10/2026)
- Community HubSpot, regole: https://community.hubspot.com/t/third-party-app-promotion-community-content-best-practices/123187 · https://community.hubspot.com/t/hubspot-community-guidelines/27610
- Installazioni attive: https://community.hubspot.com/t/changes-to-marketplace-submission-flow-how-active-installs-are-determined/156427
- Community HubSpot, ricerche e discussioni: pagine pubbliche `community.hubspot.com/search.json` e `/t/<id>.json`, lette tramite un servizio di lettura web (accesso diretto bloccato)
- Reddit r/hubspot: archivio pubblico Arctic Shift (`arctic-shift.photon-reddit.com/api/posts/search`, `/api/comments/search`, `/api/subreddits/rules`)
- Stack Overflow: `api.stackexchange.com/2.3/questions?tagged=hubspot`
- Installazioni dei concorrenti: studio 5 (`studio-business/saas/5-app-alto-potenziale.md`) e schede del marketplace, es. https://ecosystem.hubspot.com/marketplace/listing/associations-app-272901
