# Conformità e diritti per i contenuti AI: checklist, clausole, rischi (Scrollcraft)

Ricerca del 5/10/2026, a costo zero (nessuna generazione, nessun invio, nessun credito). **NON è consulenza legale**: i punti marcati **[AVVOCATO]** vanno fatti verificare da un legale (Italia/UE e USA) prima di basarci contratti o campagne.

## 0. Metodo e limiti (leggere)

- Le pagine ufficiali (ftc.gov, ecfr.gov, support.google.com, meta.com, ads.tiktok.com, higgsfield.ai) **non erano apribili** da questo ambiente (proxy: egress bloccato). Ho letto solo i risultati di ricerca che riportano titolo, URL e riassunto di quelle pagine, più articoli di studi legali.
- Etichette usate: **[VERIFICATO]** = confermato da più risultati, con pagina ufficiale indicata (URL); **[SECONDARIA]** = riportato solo da blog o studi legali, da controllare sulla pagina ufficiale; **[IPOTESI]** = mia deduzione o conoscenza generale non verificata in sessione.
- Le policy delle piattaforme cambiano spesso: ricontrollare le pagine ufficiali prima di ogni campagna dei clienti.

## 1. FTC: recensioni, testimonianze, endorsement (USA)

**Consumer Review Rule, 16 CFR Part 465 [VERIFICATO]**
- Pubblicata 14/8/2024 (Federal Register 22/8/2024), in vigore dal 21/10/2024. Comunicato FTC: https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials · Testo: https://www.federalregister.gov/documents/2024/08/22/2024-18519/trade-regulation-rule-on-the-use-of-consumer-reviews-and-testimonials
- Vietato creare, vendere o diffondere recensioni o testimonianze false: **di persone che non esistono (esempio citato dall'FTC: recensioni false generate con AI)**, di chi non ha avuto esperienza reale col prodotto, o che travisano l'esperienza di chi le dà. Vietati anche recensioni incentivate condizionate a un giudizio positivo, recensioni "insider" senza dichiarazione, soppressione di recensioni negative, acquisto o vendita di follower/visualizzazioni falsi.
- Sanzione civile fino a circa **$53.088 per violazione** (importo adeguato all'inflazione, [SECONDARIA]; l'importo 2026 va ricontrollato).
- Applicazione: 22/12/2025 l'FTC ha inviato 10 lettere di avvertimento (https://www.ftc.gov/news-events/news/press-releases/2025/12/ftc-warns-10-companies-about-possible-violations-agencys-new-consumer-review-rule). Sono passati dall'educazione ai controlli: [SECONDARIA] studi legali nel 2026 parlano di "enforcement" crescente (es. DLA Piper, luglio 2026, non apribile).

**Endorsement Guides, 16 CFR Part 255 (revisione luglio 2023) [VERIFICATO nei punti sotto, via riassunti]**
- Pagina FTC: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking · testo: https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255
- La definizione di "endorser" include anche **soggetti fittizi, tra cui influencer virtuali/avatar AI** [SECONDARIA: BakerHostetler, Proskauer]. Un avatar non può fare affermazioni "umane" (gusto, uso personale, risultati) che non ha vissuto.
- Ogni **connessione materiale** (pagamento, prodotto gratis, sconto, affiliazione) va dichiarata in modo "clear and conspicuous" (difficile da non vedere, facile da capire).
- **L'inserzionista risponde** di ciò che dice l'endorser e della mancata dichiarazione; di fatto rischia anche chi produce il contenuto [IPOTESI sul grado di responsabilità dell'agenzia: AVVOCATO].
- Claim di prodotto (salute, risultati, "clinicamente provato"): servono prove prima di dirli. Non ricercato in dettaglio in questa sessione [IPOTESI]; per integratori e cosmetici chiedere sempre al cliente la lista claim approvata (già regola in `31-ugc-regole-ufficiali-higgsfield.md` §6).

**Legge NY sui "performer sintetici" nelle pubblicità [SECONDARIA, importante]**
- S.8420-A / A.8887-B, firmata 11/12/2025, **in vigore dal 9/6/2026**: ogni pubblicità che mostra un "synthetic performer" (persona che sembra reale ma è generata digitalmente) deve riportare una dichiarazione chiara e visibile. Sanzione $1.000 la prima volta, $5.000 le successive. Vale per pubblicità destinate al pubblico di New York anche se l'inserzionista è fuori stato; riguarda chi "produce o crea" la pubblicità (quindi anche noi). Esenti opere espressive e pubblicità solo audio. Fonti: https://www.reedsmith.com/our-insights/blogs/viewpoints/102n129/fake-performer-real-penalty-what-advertisers-need-to-know-before-june-9/ · https://www.crowell.com/en/insights/client-alerts/synthetic-performers-real-consequences-implications-of-trailblazing-new-york-ai-ad-law · testo da verificare nel Senato NY. **[AVVOCATO USA]**: altri stati hanno leggi simili o in arrivo, non verificato.
- Conseguenza pratica: **ogni nostro video con creator sintetica (Sienna e simili) per clienti USA porta una scritta "AI-generated/synthetic" visibile nel video.**

## 2. Piattaforme pubblicitarie: contenuti AI

| Piattaforma | Cosa dice | Stato |
|---|---|---|
| **Meta** | Auto-etichetta "AI info" (in "About this ad") quando rileva contenuti creati/modificati con AI di terzi, tramite metadati C2PA/segnali di settore, **dal 1/6/2026**. Dichiarazione obbligatoria manuale ufficialmente solo per annunci su temi sociali, elezioni, politica (foto/video/audio realistici con persone inesistenti o eventi non veri). Fonti: https://transparency.meta.com/policies/ad-standards/SIEP-advertising/SIEP/ · https://www.meta.com/help/artificial-intelligence/355108217670024/ · https://about.fb.com/news/2024/04/metas-approach-to-labeling-ai-generated-content-and-manipulated-media/ | Verificato (via riassunti) |
| Meta, discrepanza | Vari blog sostengono che da marzo 2026 la dichiarazione sia obbligatoria anche per gli annunci commerciali e che "Undisclosed AI content" sia fra le prime cause di rifiuto. Non confermato dalle pagine ufficiali che ho visto. | **Non verificato**: trattare come obbligatoria (scelta prudente) |
| **TikTok** | Contenuti AI o molto modificati realistici richiedono etichetta AIGC o avviso chiaro; per gli annunci c'è l'interruttore di auto-dichiarazione in Ads Manager; contenuto AI non dichiarato = annuncio rifiutato o limitato. Fonti: https://ads.tiktok.com/help/article/tiktok-ads-policy-misleading-and-false-content · https://ads.tiktok.com/help/article/about-ad-disclaimers-in-tiktok-ads-manager · https://www.tiktok.com/creator-academy/en/article/ai-generated-content-label | Verificato (via riassunti) |
| TikTok, data | Blog riportano un aggiornamento del 21/7/2026 con etichetta visibile obbligatoria su tutti gli annunci con AI realistica, rilevazione C2PA e sanzioni fino al ban. | Secondaria |
| **Google Ads** | Pagina "Updates to AI labeling requirements (July 2026)": nuovo controllo per etichettare asset creati o modificati con AI di terzi, in arrivo gradualmente a luglio su Google Ads, DV360, CM360, Merchant Center, Ads Editor; le etichette nel creativo non violano la regola sui testi sovrapposti. L'inserzionista resta responsabile della conformità. Annunci elettorali: dichiarazione "Altered or synthetic content" obbligatoria. Fonti: https://support.google.com/adspolicy/answer/17257106 · https://support.google.com/adspolicy/answer/6014595 | Verificato (via riassunti); obbligo generale: secondaria (ppc.land) |
| **YouTube** | Il creator deve dichiarare contenuti realistici alterati o sintetici (persona reale che dice/fa ciò che non ha fatto, eventi reali alterati, scene realistiche mai avvenute); etichetta più evidente su salute, notizie, elezioni, finanza. Fonte: https://support.google.com/youtube/answer/14328491 · https://blog.youtube/news-and-events/disclosing-ai-generated-content/ | Verificato (via riassunti) |

**Regola Scrollcraft (scelta prudente):** dichiarare sempre l'uso di AI nell'impostazione della campagna (interruttore TikTok, campo Meta/Google se presente), e **non rimuovere mai i metadati C2PA/provenance** dai file per evitare le etichette [IPOTESI: rischio rifiuto/sospensione account del cliente]. Spiegarlo al cliente per iscritto.

**Prodotti e settori limitati o vietati (esempi verificati via riassunti)**
- Meta, salute e benessere: annunci per prodotti dietetici/dimagranti solo a maggiori di 18 anni; vietato indurre autopercezione negativa, frasi di inferiorità sull'aspetto, pizzicare il grasso, clickbait con risultati promessi in tempi precisi senza qualificazioni. https://transparency.meta.com/policies/ad-standards/restricted-goods-services/health-wellness/
- TikTok: vietati dimagranti (integratori brucia-grassi, tè detox), CBD, servizi/medicinali/telemedicina; alcol vietato in USA e Canada; integratori vitaminici solo 18+; gioco d'azzardo con limitazioni. Pagine: https://ads.tiktok.com/help/article/tiktok-ads-policy-weight-management · https://ads.tiktok.com/help/article/tiktok-ads-policy-healthcare-pharmaceuticals (parte dell'elenco viene da pagine TikTok Shop, non Ads: ricontrollare).
- Per le nostre nicchie (integratori animali, skincare bambini/eczema, haircare e caduta capelli, grooming): **niente claim medici, niente prima/dopo, niente "cura/guarisce"**; attenzione a eczema e caduta capelli (confine con il farmaco) [IPOTESI: AVVOCATO/regolatorio per i claim].
- Adulti, azzardo, tabacco, armi, finanza ad alto rischio: già esclusi (`31-...` §6).

## 3. Diritti d'uso dei contenuti

**Higgsfield, Terms of Use [VERIFICATO via riassunti; pagina non apribile]** https://higgsfield.ai/terms-of-use-agreement · https://higgsfield.ai/creator-hub/help-center/account/who-owns-my-generations-and-can-i-use-them-commercially · https://higgsfield.ai/blog/terms-of-use-privacy-policy-update
- Non rivendica la proprietà di input e output; **non limita l'uso commerciale** degli output, non legato al piano; i diritti sugli output esportati sopravvivono alla chiusura dell'account; puoi trasferirli o sublicenziarli ai clienti.
- Può inserire marcature/metadati di provenienza negli output, senza garantire che persistano.
- **Addestramento:** i contenuti e gli output possono essere usati da Higgsfield per migliorare i modelli (opt-in predefinito rimasto dopo la revisione). Storia: aggiornamento del 23/7/2026 con licenza perpetua e irrevocabile sugli output → proteste → riscrittura del 26/7 che elimina la licenza perpetua e lega l'uso promozionale a contenuti pubblici o consenso [SECONDARIA: mindstudio.ai, startupfortune.com; dichiarazione Higgsfield su X]. **Rileggere i termini correnti prima di ogni progetto**; il testo può cambiare ancora.
- **Volti e voci:** chi carica contenuti dichiara di avere diritti e consensi su nome, volto, voce di chiunque vi compaia; vietato caricare immagini di altre persone senza permesso, biometria, contenuti espliciti. Responsabilità dell'utente per copyright, marchi, diritto d'immagine.
- Non ho trovato (né verificato) una garanzia che gli output non violino diritti di terzi, né l'indennizzo. [IPOTESI: i servizi AI di norma non li danno → il rischio resta nostro; AVVOCATO].
- **Copyright dell'output [IPOTESI, non ricercato]:** negli USA i contenuti puramente generati da AI in genere non sono tutelabili dal diritto d'autore (posizione dello US Copyright Office); in UE conta l'apporto creativo umano. Quindi "full usage rights" va inteso come **licenza d'uso, non come garanzia di esclusiva o di copyright** → vedi clausole. **[AVVOCATO]**

**Pixabay (musica)** https://pixabay.com/service/license-summary/ · https://pixabay.com/blog/posts/how-to-clear-a-youtube-content-id-claim-with-a-pix-190/ · https://pixabay.com/service/terms/
- Uso commerciale gratuito, senza attribuzione. Non consentito: rivendere/distribuire il brano da solo, usarlo come marchio, usi ingannevoli o illegali, marchi/persone riconoscibili in uso commerciale su prodotti.
- **Rischio Content ID:** alcuni autori o distributori registrano i brani in Content ID, quindi anche l'uso lecito può generare reclami automatici (YouTube e simili). Pixabay descrive la procedura con il "License Certificate" per contestare. Pixabay accetta caricamenti aperti: il rischio sta a noi/cliente. [SECONDARIA per l'analisi del rischio: hellothematic.com, foximusic.com]
- Regola: per ogni brano usato, **scaricare e archiviare certificato di licenza + link + data + screenshot**; consegnare al cliente; avvisare che un reclamo è possibile e contestabile. Per clienti con canale YouTube/Meta di alto valore, proporre musica da libreria a pagamento con licenza scritta o composta su commissione [IPOTESI].

## 4. Marchi di terzi nel portfolio (Tom Ford, Prada, Cartier, Missoni, Bottega Veneta)

- Principio **[SECONDARIA, giurisprudenza USA; IPOTESI sull'applicazione a noi]**: la nominative fair use permette di nominare un marchio altrui se serve a identificare il prodotto, si usa solo quanto necessario e non si suggerisce sponsorizzazione o affiliazione. Il disclaimer "not affiliated" **aiuta ma non cura**: conta la presentazione complessiva (un tribunale ha dato torto a un'attività che usava il nome di un marchio di lusso con un'impaginazione che suggeriva sponsorizzazione). Fonti: https://www.michaelbest.com/insights/nominative-fair-use-the-dos-and-donts-for-using-someone-elses-trademark-102mpkz/ · https://www.arnoldporter.com/~/media/files/perspectives/publications/2012/12/nominative-fair-use-legitimate-advertising-or-tr__/files/publication/fileattachment/nominative-fair-use.pdf
- Il nostro caso è più rischioso del semplice nome: **ricreiamo prodotto, estetica e atmosfera di una campagna** (flacone, etichetta, stile), in un video in homepage e come biglietto da visita. Rischi: marchio (confusione, diluizione dei marchi celebri), diritto d'autore e design se partiamo da foto o grafica ufficiali, uso del nome per attirare clienti. In UE/Italia il quadro è diverso da quello USA (nessuna "nominative fair use" identica): **[AVVOCATO UE/IT + USA]**.
- Foto ufficiali del prodotto: sono protette da copyright anche se scaricate dal sito del marchio; i press kit sono di norma pensati per uso editoriale [IPOTESI]. Usarle come riferimento per generare lo spot (ERRORI #5) crea un'opera derivata. Per lavori per clienti: **solo foto fornite dal cliente titolare**.

**Formula per le didascalie dei concept (da usare uguale ovunque):**
> "Unofficial AI concept by Scrollcraft. Not commissioned by, affiliated with, or endorsed by [Brand]. [Brand] and its product names are trademarks of their respective owners."

Regole: mai il logo del marchio nelle miniature social/OG image/annunci; mai usare questi concept come inserzione a pagamento o in email di vendita al posto di lavori reali; chiarire sempre che sono esercizi creativi; se il marchio scrive, **rimozione immediata** (la pagina deve poter togliere un video in giornata). Meglio: a regime sostituire i concept di marchi reali con marchi fittizi nostri.

## 5. Italia / UE / USA: AI Act, GDPR, ePrivacy, CAN-SPAM

**AI Act (Reg. UE 2024/1689), art. 50 [VERIFICATO via riassunti]** https://artificialintelligenceact.eu/transparency-rules-article-50/ · https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act · https://digital-strategy.ec.europa.eu/en/policies/guidelines-ai-transparency-obligations · https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content
- Dal **2/8/2026** si applicano gli obblighi di trasparenza.
- Art. 50(2) (fornitori di sistemi generativi, es. Higgsfield): marcatura leggibile da macchina degli output. Accordo politico "Digital Omnibus" del 7/5/2026: per i sistemi già sul mercato il termine per questa marcatura slitta al **2/12/2026** [SECONDARIA: usercentrics, aiactblog.nl; verificare l'adozione formale]. L'omnibus ha rinviato solo gli obblighi sui sistemi ad alto rischio (2/12/2027 e 2/8/2028), non l'art. 50.
- Art. 50(4) (**chi usa il sistema, il "deployer": noi e i clienti**): chi genera o manipola immagini/audio/video che assomigliano a persone, oggetti, luoghi, eventi esistenti e potrebbero sembrare autentici (deep fake) deve dichiararlo, al più tardi alla prima esposizione, in modo chiaro. Per opere evidentemente creative/artistiche l'obbligo si riduce a una dichiarazione che non rovini la fruizione.
- Applicazione a noi **[IPOTESI + AVVOCATO]**: una creator interamente inventata probabilmente non "assomiglia a una persona esistente", ma **un flacone Tom Ford ricreato = oggetto/marchio esistente**; e uno spot per cliente UE va comunque dichiarato per prudenza. Sanzioni AI Act per art. 50 fino a 15 milioni € o 3% del fatturato (cifre da riverificare, non ricercate).
- Italia: Legge 132/2025 (in vigore 10/10/2025) introduce l'art. 612-quater c.p. (diffusione illecita di contenuti falsificati con AI di una persona reale, senza consenso, con danno ingiusto; reclusione 1-5 anni) [SECONDARIA: studiocataldi.it, agendadigitale.eu]. Per noi: **mai somiglianze con persone reali, mai voci clonate di persone reali senza consenso scritto.**

**GDPR e ePrivacy per i contatti B2B (Apollo, cold email)**
- GDPR art. 14 [VERIFICATO]: per dati non raccolti dall'interessato (Apollo, siti, LinkedIn) bisogna informare chi sei, perché, base giuridica, diritti, **entro un mese e al più tardi alla prima comunicazione**. https://gdpr-text.com/read/article-14/
- Apollo [VERIFICATO via riassunti]: tratta i dati B2B per "interesse legittimo", notifica le persone UE/UK/CH e offre opt-out; ha un'impostazione **GDPR che esclude automaticamente gli individui in UE** da ricerca ed email. https://knowledge.apollo.io/hc/en-us/articles/4409141087757-General-Data-Protection-Regulation-GDPR-Overview
- ePrivacy (dir. 2002/58/CE art. 13): consenso preventivo per email promozionali a persone fisiche; per le persone giuridiche decidono gli Stati. **Italia: tradizionalmente severa, art. 130 Codice Privacy (D.Lgs. 196/2003) richiede il consenso preventivo per email promozionali; il Garante ha detto che i dati presi da elenchi o siti pubblici non bastano** (https://www.garanteprivacy.it/home/docweb/-/docweb-display/docweb/2542348 linee guida spam; https://www.garanteprivacy.it/web/guest/home/docweb/-/docweb-display/docweb/1597151). Eccezione "soft spam" (art. 130 c.4) solo per servizi simili a quelli già acquistati. Altri blog dicono che Italia e Germania richiedono il consenso anche B2B [SECONDARIA]. Se questo si applichi a una cold email di un mittente italiano verso aziende USA, e quanto conti l'email nominale di un dipendente: **[AVVOCATO]**. Ipotesi prudente: **i destinatari in UE non si contattano a freddo** (attivare "GDPR settings" su Apollo); per i destinatari USA applicare CAN-SPAM e inserire comunque l'informativa art. 14 breve.
- **CAN-SPAM (USA) [VERIFICATO via riassunti]** guida FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business · vale anche per le email B2B. Requisiti: intestazioni e mittente veritieri, oggetto non ingannevole, **identificare il messaggio come pubblicità**, **indirizzo postale fisico valido** (anche casella postale), **meccanismo di disiscrizione chiaro**, onorarlo **entro 10 giorni lavorativi**, senza costi, funzionante per almeno 30 giorni dopo l'invio. Sanzione fino a circa **$53.088 per email**.

## 6. Checklist operativa per ogni progetto

**A. Prima di accettare (intake)**
1. Il cliente è titolare del prodotto e dei marchi? Ha fornito foto/asset ufficiali e conferma di avere i diritti? (scritto)
2. Lista **claim approvati** dal cliente, parola per parola. Prodotto in settore vietato/limitato per le piattaforme di destinazione? (§2)
3. Formato: **dimostratrice/creator AI dichiarata, mai "cliente" che racconta un uso**. Prima persona solo con copione e conferma di un utente reale. Niente recensioni, valutazioni, prima/dopo inventati.
4. Mercati di destinazione (USA, NY, UE/Italia): decide le diciture (§1, §5).
5. Voci: sintetiche non assimilabili a persone reali; nessuna clonazione senza consenso scritto. Volti: nessuna somiglianza con persone reali, nessuna celebrità.
6. Musica: brano scelto con licenza archiviata (§3).
7. Cartella di progetto: preventivo firmato, asset ricevuti con origine, brief approvato.

**B. Produzione**
8. Rileggere i termini correnti di Higgsfield (training, volti/voci) e non caricare materiale riservato/non lanciato del cliente senza il suo ok informato.
9. Archiviare per ogni file: modello usato, data, prompt, riferimenti usati (registro provenienza).
10. Controllo fotogramma per fotogramma (già in CLAUDE.md) + controllo "testi/loghi di terzi", persone riconoscibili, marchi non previsti, scritte finte, claim non approvati.

**C. Consegna**
11. Etichetta AI: scritta visibile nel video (es. "AI-generated" in basso, leggibile, per l'intera durata o all'inizio) + istruzioni per interruttore/campo AI nelle piattaforme + **metadati lasciati intatti**.
12. Nota di consegna: claim usati (solo approvati), musica con licenza e certificato, limiti d'uso (§7), avviso sulla responsabilità del cliente per la pubblicazione.
13. Per annunci con testimonial/creator: dichiarazione commerciale/#ad dove serve (Endorsement Guides).

**D. Portfolio/marketing nostro**
14. Nessun lavoro di cliente online senza permesso scritto; concept di marchi terzi solo con la formula del §4; **mai mostrare come "recensione" un video con esperienza inventata**.
15. Ogni campione: etichetta "AI-generated" e, se serve, "demonstration".

## 7. Clausole da inserire nei preventivi (bozza inglese, per clienti USA; **[AVVOCATO]** prima dell'uso)

1. **AI disclosure.** "Deliverables are created with generative AI tools. Where required by law or platform policy (including New York General Business Law §396-b, EU AI Act Art. 50, and the AI-content rules of Meta, TikTok, Google/YouTube), Client agrees to keep the AI disclosure we embed or recommend, to enable the platforms' AI-content labels, and not to strip provenance metadata (e.g., C2PA)."
2. **Claims and testimonials.** "Scrollcraft will use only product claims approved in writing by Client. Creators in deliverables are synthetic presenters, not customers. We will not create fabricated customer reviews, ratings, results, or before/after content. Client will not present deliverables as real customer testimonials."
3. **Client materials and warranties.** "Client warrants it owns or is licensed to use all products, trademarks, images, and other materials it supplies, and has the right to have them processed by third-party AI tools. Client acknowledges that those tools' terms may allow the provider to use inputs and outputs to improve its models; Client may request that confidential or unreleased materials not be uploaded."
4. **Licence, not ownership guarantee.** "Upon full payment, Scrollcraft grants Client a perpetual, worldwide, non-exclusive licence to use, edit and publish the Deliverables for advertising and marketing of Client's products. Scrollcraft does not warrant that AI-generated elements are eligible for copyright protection or exclusive to Client, or that they do not resemble existing works." (Ricontrollare "full usage rights" in sito e privacy.)
5. **Third-party elements and music.** "Music is licensed under the provider's licence (certificate supplied). Automated claims (e.g., Content ID) can occur; Scrollcraft will provide licence proof for disputes; Client is responsible for platform disputes and for any music Client supplies."
6. **Platform approval.** "Platform approval of ads is not guaranteed; Scrollcraft is not liable for rejections, restrictions or account actions. Client is responsible for targeting, landing page and substantiation of claims."
7. **No endorsement of third-party marks.** "Deliverables will not include third-party trademarks other than Client's."
8. **Liability and indemnity.** Limitazione della responsabilità al corrispettivo; manleva reciproca per materiali forniti dal cliente / per violazioni nostre. Forma e limiti: **[AVVOCATO]**.
9. **Portfolio permission.** "Scrollcraft may show Deliverables in its portfolio unless Client opts out in writing" (o solo dopo consenso scritto, più prudente).
10. **Law and venue.** Da decidere con l'avvocato (Italia vs. stato USA).

## 8. Cosa dire ai clienti (testo breve, pronto)

> "Our creators are AI-generated presenters, so we script demonstrations from your approved claims — never invented customer stories. The ad will carry an 'AI-generated' label, which Meta, TikTok and YouTube increasingly require anyway; and in some places (e.g. New York for synthetic performers) the law does. Keep the metadata intact and tick the platform's AI-content setting when you launch. The music comes with a licence certificate and we keep proof on file. We only use product images you have the rights to. This is how we protect your ad account and avoid the FTC's fake-review rules. If you'd like legal sign-off for your category, we recommend your counsel review the final cut."

In italiano per Massimiliano: i clienti non devono sentire "è rischioso", ma "il nostro processo è fatto per proteggere il tuo account pubblicitario".

## 9. Dove il nostro lavoro attuale è a rischio (ordine di priorità)

1. **ALTO: campioni con testimonianza in prima persona** (es. Meridian "ho cambiato tre settimane fa", `08-...` Campione 3 "Testimonial style", hook "Okay I need to talk about this", reel "Social proof: product B-roll with review overlay", i reel "UGC talking" per grooming/pet/skincare nel portfolio). Esperienza e recensioni inventate = zona di rischio della Consumer Review Rule e delle Endorsement Guides. Il portfolio li mostra pubblicamente e li vendiamo. Azione: verificare il testo parlato e le scritte dei reel; sostituire con formato dimostratrice + etichetta AI; togliere ogni overlay di recensione/valutazione inventata. **[AVVOCATO]**
2. **ALTO: concept su marchi reali in homepage** (Tom Ford Lost Cherry in hero, 5 "idee" Missoni/Cartier/Bottega Veneta/Prada/Tom Ford, og-image/miniature `spot-lostcherry.jpg`). Disclaimer presente ma non basta da solo (§4). Azione: formula completa del §4, nessun logo nelle anteprime social, piano di rimozione rapida, valutare marchi fittizi; verificare di non aver usato foto ufficiali come riferimento senza licenza.
3. **ALTO: email di outreach senza elementi CAN-SPAM**: i modelli (`22-outreach-v2.md`, `05-A1-outreach-offer-EN.md`) hanno firma ed email ma **nessun indirizzo postale e nessuna riga di disiscrizione**; non dichiarano la fonte dei dati (art. 14 GDPR). Azione: aggiungere (a) indirizzo postale o casella, (b) "If you'd rather not hear from me, reply 'no' and I won't write again", (c) una riga sulla fonte dei dati, (d) lista di esclusione rispettata entro 10 giorni lavorativi (meglio subito); escludere i contatti UE (impostazione GDPR di Apollo). Italia/Art. 130 **[AVVOCATO]**.
4. **MEDIO-ALTO: sito e informativa privacy** (`portfolio/privacy.html`). Dice che lo strumento visitatori di Apollo "non vi identifica personalmente": affermazione da verificare (identifica l'azienda dall'IP; per visitatori UE può servire il consenso cookie/tracciamento: [IPOTESI], linee guida cookie del Garante, non ricercate). Mancano: titolare con dati completi (P.IVA/indirizzo, obblighi del commercio elettronico italiano: [IPOTESI]), basi giuridiche, tempi di conservazione, diritti dell'interessato e reclamo al Garante, trasferimenti extra-UE (Formspree, Stripe, Apollo, Netlify). Azione: riscrivere con un legale o un generatore affidabile; banner/consenso per i visitatori UE se si mantiene lo strumento Apollo.
5. **MEDIO: "full usage rights" / "no extra licensing or whitelisting fees"** (sito e privacy) e "clean files with full usage rights": promessa più ampia di quanto possiamo garantire (copyright dell'AI, termini Higgsfield, musica, marchi). Azione: riformulare come licenza (clausola 4).
6. **MEDIO: "A real supplement brand" nello spot in evidenza.** Se non è un cliente che ha autorizzato la pubblicazione, o se i claim non sono approvati, è un rischio di rappresentazione ingannevole e di violazione del contratto. Azione: confermare l'autorizzazione scritta o riformulare ("concept").
7. **MEDIO: musica Pixabay** negli spot (hero e portfolio): conservare il certificato di licenza; possibile reclamo Content ID su YouTube/Meta; verificare di non aver usato brani senza certificato.
8. **MEDIO: etichette AI nei video** dei campioni e consegne: la pagina dice "made with AI" (bene), ma i singoli video non hanno la scritta; per i clienti NY serve nel video.
9. **MEDIO: materiali dei prospect caricati su Higgsfield per i campioni gratuiti** (foto prodotto del prospect, marchio). Rischio basso se il campione va solo al prospect e non è pubblicato, ma i termini consentono addestramento. Azione: dirlo nell'email del campione e non pubblicare mai campioni non acquistati.
10. **BASSO-MEDIO: Sienna e voci sintetiche**: dichiarare "AI creator"; nessuna somiglianza con persone reali; niente voce clonata senza consenso (artt. 612-quater c.p., diritto d'immagine). Verificare la provenienza della voce in uso.
11. **BASSO: claim di prestazione** ("24-55 ad variants/month", "built for any placement", "A/B-ready"): sono capacità di produzione, non risultati; mantenere la regola "no guaranteed ROAS" già presente in `05-...`.

## 10. Da far verificare a un avvocato (elenco)

1. Responsabilità di Scrollcraft come produttore di testimonial sintetici: FTC 16 CFR 465 e Endorsement Guides, anche per i campioni.
2. Concept con marchi di lusso: rischio marchio/copyright/diritto d'immagine in Italia, UE e USA; testo del disclaimer.
3. Cold email da mittente italiano: art. 130 Codice Privacy, GDPR (base giuridica, art. 14), CAN-SPAM; uso di Apollo/Vibe Prospecting.
4. Informativa privacy, cookie/tracking (strumento Apollo), obblighi di identificazione del prestatore in Italia (P.IVA, ecc.).
5. Art. 50 AI Act: ruolo di "deployer" per noi e per i clienti; se creator inventata e prodotti reali rientrano nel deep fake; formula dell'avviso.
6. Legge NY (§396-b) e altre leggi statali USA su performer sintetici; diritto d'immagine/voce.
7. Contratto: licenza vs "full usage rights", manleva, limitazione di responsabilità, foro e legge applicabile, trattamento dati dei clienti verso Higgsfield.
8. Claim per integratori/cosmetici/haircare per le nicchie target (FTC, FDA, piattaforme).

## 11. Prossimi passi proposti (nessuno eseguito)

Nessuna modifica a sito o email è stata fatta; ogni azione richiede il via di Massimiliano (regola: 1 push al giorno, nessun invio senza il suo ok). Proposta: (1) correggere template email (indirizzo postale + disiscrizione + fonte dati) prima del prossimo invio; (2) rivedere testi dei reel "social proof" e "UGC talking"; (3) etichettare i concept con la formula del §4; (4) fissare un'ora di consulenza con un avvocato su un elenco di 8 punti sopra; (5) aggiornare `PROCEDURE.md` con le checklist A-D dopo l'approvazione.

## Fonti principali (consultate tramite ricerca il 5/10/2026)

FTC press release 14/8/2024 e Federal Register 22/8/2024 (Rule 465); FTC press release 22/12/2025 (lettere); FTC Endorsement Guides FAQ e 16 CFR 255; FTC CAN-SPAM guide; Meta Transparency Center (SIEP, Health & Wellness) e about.fb.com 2024; TikTok Ads help (Misleading and false content, ad disclaimers, weight management, healthcare); Google Ads policy 17257106 e 6014595; YouTube Help 14328491; Higgsfield Terms of Use e Help Center; Pixabay license summary/Terms/blog Content ID; artificialintelligenceact.eu e digital-strategy.ec.europa.eu (art. 50, linee guida, codice di pratica); Garante Privacy (linee guida spam 2542348, doc 1597151); Apollo knowledge base GDPR; GDPR art. 14; studi legali su NY S.8420-A (Reed Smith, Crowell); Legge 132/2025 (studiocataldi.it, agendadigitale.eu).
