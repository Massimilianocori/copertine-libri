# Foto da catalogo di abbigliamento con l'AI: si può, e con quale metodo (studio del 7/10/2026)

Domanda: possiamo fare foto da catalogo di un capo reale con fedeltà assoluta (colore, tessuto, cuciture, bottoni, colletto, vestibilità)? Caso: Collars & Co., Dress Collar Polo. Call con Justin Baer l'8/10 alle 19:30.

Studio a costo zero. Nessuna generazione, nessun upload, nessun preset eseguito. Letti prima: `CLAUDE.md`, `ERRORI.md`, `PROCEDURE.md`, docs 30, 32, 33, 34, 42, 54.

Legenda: **[V]** = fonte ufficiale, legge o dato nostro verificato · **[V debole]** = blog di venditore o solo riassunto di WebSearch (pagina non aperta) · **[I]** = ipotesi nostra.

> **Da sapere prima.** Il 5/10 Massimiliano ha deciso: "catalogo no, solo campagna" (PROCEDURE, doc 42). Questo studio non cambia quella decisione da solo. Dice cosa è possibile e a quali condizioni. Decide lui se proporlo.

---

## 1. Risposta breve

- **Sì, ma solo se il capo non viene generato.** Nessun modello di oggi, da una foto flat-lay, garantisce colletto, bottoni e colore identici. Le fonti lo dicono in modo concorde (§3).
- **Il metodo giusto: "capo bloccato".** Si parte da una foto vera del capo indossato. I pixel del capo restano quelli della foto. L'AI genera solo modello (viso, braccia, mani, pantaloni) e location intorno. Alla fine si rimettono sopra i pixel originali del capo.
- Per Collars & Co. "catalogo" vuol dire **foto indossate lifestyle** (modello uomo 40-50 anni, resort, palme, campo da croquet/golf, luce calda), 3-4 foto per variante, molte varianti colore. [V, screenshot di Massimiliano della pagina Luxury Pima Cotton Blend Polo, Navy, $96]. Il metodo serve proprio a questo: stesso modello e stessa location per tutte le varianti colore, con il capo vero.
- **Limite:** ogni variante colore (bianco, navy, nero, righe) richiede una sua foto vera. Ricolorare un capo con l'AI non è "fedeltà assoluta".

## 2. Cosa esiste sul mercato (2026)

| Strumento | Cosa fa | Prezzo | Fonte |
|---|---|---|---|
| FASHN (v1.6) | try-on da foto indossata o flat-lay, "model swap" che tiene il capo, 864x1296 | API ~$0,075/immagine | [V debole] https://help.fashn.ai/plans-and-pricing/api-pricing · https://fal.ai/learn/tools/best-virtual-try-on-apis-2026 · https://docs.fashn.ai/api-reference/model-swap |
| Google Virtual Try-On (Vertex AI) | persona + capo → persona che lo indossa, con pieghe e caduta | ~$0,06/immagine | [V debole] https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/imagen/virtual-try-on-001 · https://cloudprice.net/models/google-virtual-try-on-1 |
| Botika | da foto su manichino/persona a modella AI | ~$0,73-1,16/immagine | [V debole] https://www.photta.app/pricing-and-reviews/botika |
| Photoroom | Virtual Model, Ghost Mannequin, Flat Lay, fino a 4 capi | da $12,99/mese | [V debole] https://www.wearview.co/blog/photoroom-pricing |
| Model swap / mannequin-to-model (FASHN, Segmind, HuHu, WearView, autoRetouch) | cambia la persona e tiene capo, posa e luce | n.d. | [V debole] https://fashn.ai/model-swap · https://huhu.ai/mannequin-to-model/ · https://docs.autoretouch.com/specifications/model-swap-input-requirements |
| Nano Banana Pro come try-on | instabile: a volte non applica il capo o lo applica a metà; maniche sbagliate | ~2 crediti su Higgsfield | [V debole] https://discuss.google.dev/t/issues-with-virtual-try-on-stability-face-distortion-and-incorrect-sleeve-rendering-prompt-for-try-on-in-nano-banana/324604 |

**Brand che lo usano davvero:**
- Zalando: circa il 70% delle immagini editoriali di campagna nel Q4 fatte con AI; tempi da 6-8 settimane a 3-4 giorni, costi -90%. Nota: **campagna**, non schede prodotto. [V debole] https://kalkine.com.au/news/stocks/zalando-uses-ai-to-speed-up-marketing-caigns-cut-costs
- H&M: 30 "gemelli digitali" di modelli veri, con il loro consenso, per social e marketing (luglio 2025). [V debole] https://fashionunited.com/news/fashion/h-m-turns-to-ai-digital-twins-in-new-campaign-as-fashion-grapples-with-blurred-realities/2025070466982
- Levi's + Lalaland (2023): forte reazione negativa; Levi's ha confermato che continua con modelli veri. [V debole] https://www.nbcnews.com/business/business-news/ai-models-levis-controversy-backlash-rcna77280
- Casi Botika (JUAN & ME "+128% conversioni"): numeri del venditore, senza metodo. [V debole] https://botika.com/resources/case-studies

Lettura [I]: i grandi usano l'AI soprattutto per campagna ed editoriali. Sulle schede prodotto la usano con modelli veri digitalizzati e capo reale. Questo conferma l'intuizione di Massimiliano: il catalogo "generato da zero" non è ancora affidabile.

## 3. Limiti noti (perché il capo non va generato)

- Loghi, cerniere, bottoni e minuteria spesso non sopravvivono alla generazione. Colletti "sciolti", bottoni ridisegnati, scollo che si sposta, quadri deformati. In un test l'AI ha cucito un taschino sul retro di una camicia. [V debole] https://www.rewarx.com/blogs/why-ai-image-tools-struggle-apparel-categories · https://www.rewarx.com/blogs/why-ai-model-photography-doesnt-match-product
- Colore: "dusty rose" esce rosa acceso o malva. Il controllo serio si fa contro hex e Pantone forniti dal brand. [V debole] https://www.graswald.ai/blog/how-ai-on-model-imagery-meets-enterprise-brand-quality-standards
- Senza un'immagine del capo come ancora, il capo cambia da un'immagine all'altra ("il colletto migra"). [V debole] https://kive.ai/learn/virtual-try-on-vs-ai-product-photography
- Stampe distorte con Nano Banana Pro: casualità della generazione + prompt troppo insistenti. [V debole] https://docs.apiyi.com/en/faq/nano-banana-pro-print-distortion.md
- Coincide con i nostri errori: scritte storpiate (MERIDOAN), etichette specchiate, dettagli inventati (ERRORI 4, 8, 22; PROCEDURE studio 7/10).
- **Resi:** abbigliamento online USA ~20,8-24,4% di resi; "non corrisponde alla foto/descrizione" pesa per il 22-31% dei resi. Una foto infedele crea resi. [V debole] https://www.rewarx.com/blogs/why-ai-model-photography-doesnt-match-product · https://www.airframe.ai/product/botika-com/analysis

Per la Dress Collar Polo il punto debole è proprio il prodotto: **colletto rigido con stecche, punte "English spread", 3 bottoni chiari**. È il dettaglio che il cliente compra. Non si può lasciare al modello. [I, da doc 54 e screenshot]

## 4. Regole dei marketplace e obblighi di dichiarazione

- **Amazon, immagine principale abbigliamento uomo:** su modello umano, fondo bianco puro (255,255,255), capo intero, niente testo, modello non seduto. Deve essere una **fotografia professionale del prodotto vero**: niente mockup né illustrazioni. [V debole] https://www.junglescout.com/resources/articles/amazon-image-requirements/ · https://www.astria.ai/articles/amazon-product-images-apparel/
- **Amazon, da luglio 2026:** le immagini e i video con una **persona fotorealistica interamente generata dall'AI** vanno marcate nei metadati prima del caricamento; altrimenti l'immagine può essere segnalata e l'inserzione nascosta. [V debole] https://www.eweek.com/de/news/amazon-ai-generated-product-images-labels-new-york-law/ · https://novadata.io/resources/news/amazon-sellers-label-ai-generated-people-ny-law-july-23-2026
- **Legge di New York (Gen. Bus. Law § 396-b), in vigore dal 9/6/2026:** nelle pubblicità con "synthetic performer" va dichiarato in modo evidente. Multa $1.000, poi $5.000. [V, studi legali] https://www.hunton.com/privacy-and-cybersecurity-law-blog/new-york-enacts-law-regulating-the-use-of-ai-generated-synthetic-performers-in-advertising · https://mcdermottlaw.com/insights/new-yorks-synthetic-performer-disclosure-law-what-advertisers-need-to-know. [I] Se una foto della scheda prodotto conti come "pubblicità" non è chiaro: da far vedere a un avvocato.
- **FTC / Shopify:** Shopify non obbliga all'etichetta AI. La regola vera è un'altra: la foto non deve ingannare su colore, taglia, tessuto e vestibilità, AI o non AI. [V debole] https://craftshift.com/disclose-ai-generated-product-images-shopify-2026/ · https://nightjar.so/blog/ai-product-photography-legal-guide
- **UE, AI Act art. 50, dal 2/8/2026:** se vende in UE, le immagini con persone che possono sembrare foto vere richiedono un'etichetta visibile sull'immagine e un marchio leggibile dalla macchina. [V debole] https://www.claimlane.com/resources/blog/eu-ai-act-article-50-what-changes-on-2-august-2026-for-fashion-brands · https://craftshift.com/eu-ai-act-article-50-shopify-ai-product-photos-2026/
- Conseguenza per noi [I]: ogni immagine consegnata ha la nota "modello generato con AI" e il cliente la dichiara dove serve. Coerente con doc 37.

## 5. Cosa offre Higgsfield (verificato con strumenti di sola lettura, 7/10)

| Verifica | Risultato [V] |
|---|---|
| `models_explore` ricerca "try-on" | **nessun modello dedicato al try-on** |
| `models_explore` ricerca "fashion" | solo Soul 2.0 (`soul_2`, `soul_v2`): ritratti, UGC, editoriale; 1 immagine di riferimento; niente maschera |
| `models_explore` recommend (capo reale su modello) | Marketing Studio Image, Kling O1 Image, GPT Image 2, FLUX.2 Pro Outpaint, **Nano Banana 2.1** (nuovo), Nano Banana Pro, Nano Banana 2, Nano Banana 2 Lite, DTC Ads (`ms_image`), Soul 2.0 |
| Modelli con **maschera** (`mask` + `is_inpaint`: modifica solo la zona indicata) | **Nano Banana 2, Nano Banana 2.1, Nano Banana 2 Lite** (e Seedream 5.0 Pro con `is_inpaint`, doc 33). Nano Banana Pro **non** ha la maschera |
| Nano Banana 2.1 | 1k/2k/4k, riferimenti immagine e video, maschera, `thinking_level`, `seed` fisso, 4:5 e 3:4 disponibili. Mai usato da noi |
| Marketing Studio Product Shot (`marketing_studio_2_image`) | tipo `product_shots_people`, ruoli immagine `product_image`, `character_photo`, `model_image`. Mai usato; costo non osservato |
| Workflow `product-photoshoot`, modalità `virtual-model-tryout` (doc 32) | usa sempre Nano Banana Pro, senza maschera: **rigenera il capo**. "Non per Amazon" nel workflow stesso |
| Marketing Studio Video "UGC Virtual Try On" | è un video, non una foto da catalogo |
| `apps_search` (tutto, "try", "fashion") | 1 sola app nel marketplace (Match Cut + Tracelab): niente try-on |
| `get_presets` "try on" / "fashion" / "outfit" / "apparel"; product-shot "model" | nessun preset try-on o catalogo; solo effetti video "fashion edit" e 1 motion "Fashion Editorial Reveal" |
| Unlimited | non disponibile (`unlim.available: false`) |

**Costi:** gli strumenti di sola lettura **non riportano i crediti**. Gli unici costi sono quelli già spesi (`transactions`, doc 33): Nano Banana 2 = 1,5 (1k) e 2 crediti (probabilmente 2k [I]); Nano Banana Pro = 2 (2k); Soul 2.0 = 0,12; Seedream 5.0 Pro = 2,5. **Il costo di Nano Banana 2 in modalità maschera non è mai stato osservato.** Nano Banana 2.1 e Marketing Studio Product Shot: mai usati, costo sconosciuto. 1.000 crediti = 50 € (dato di Massimiliano).

## 6. Il metodo raccomandato (uno solo): "capo bloccato"

**Perché questo.** È l'unico che garantisce la fedeltà: il capo nella foto finale è fatto dei pixel della foto vera, non disegnato dal modello. È lo stesso principio del "model swap" che i fornitori del settore usano per le schede prodotto (§2). Su Higgsfield si fa con **Nano Banana 2 con maschera** (il modello con maschera già provato da noi, 1,5-2 crediti a immagine) e con il casting approvato come riferimento volto. Poi si rimettono sopra i pixel originali del capo in locale, a costo zero.
Qualità attesa [I]: capo identico al 100% (per costruzione); il rischio si sposta su bordi, luce e contatto collo-colletto, che si controllano a vista.

### Input dal cliente (per ogni variante colore)
1. **Foto vera del capo indossato** (fit model, anche un dipendente; il viso può restare fuori campo): fronte, 3/4, retro, se serve una posa seduta/camminata. Luce diurna morbida all'ombra, simile alla luce finale (calda, laterale). File ad alta risoluzione (RAW o JPG pieno), almeno 3000 px sul lato lungo.
2. **Macro** del colletto (punte, altezza del collo), dell'abbottonatura (3 bottoni) e del tessuto.
3. **Colore:** codice hex/Pantone dalla scheda tecnica, oppure un campione fisico misurato. Serve per il controllo, non per generare.
4. **Misure e vestibilità:** tabella taglie e taglia indossata dal fit model (per non "stringere" o allungare il capo).
5. **Riferimento di stile:** 3-4 foto lifestyle attuali del sito (location, luce, età e tipo del modello), per la coerenza del catalogo.
6. **Consenso scritto** della persona fotografata (il suo corpo resta nell'immagine) e conferma che il cliente possiede i diritti delle foto.

### Passaggi
1. Brief di una pagina, approvato dal cliente e da Massimiliano: casting (uomo 40-50 anni come il sito), location, luce, pose, numero di immagini per variante (CLAUDE.md: tutto da ricerca, niente iniziative).
2. **Casting:** 2-4 ritratti Soul 2.0 (0,12 crediti l'uno), Massimiliano approva. È il riferimento volto in ogni immagine (ERRORI 1, 16).
3. **Maschera del capo** in locale (scontorno del polo dalla foto vera; rifinita a mano sul colletto e sui bottoni). Costo zero.
4. **Generazione** con Nano Banana 2 (o 2.1 se una prova la dà migliore), `is_inpaint: true`, maschera = tutto tranne il capo, riferimenti = foto vera + casting + 1 foto di stile. Prompt: solo persona, location e luce; il capo non si descrive (PROCEDURE studio 7/10, punto 3). Formato 4:5 o 3:4 come il sito.
5. **Ricomposizione:** si incollano sopra i pixel originali del capo con la maschera, bordo sfumato di pochi pixel. Costo zero.
6. **Controllo qualità** (§7). Scartata = rifatta dal passo 4, mai da un'immagine già spostata.
7. Consegna con nota "AI-generated model" e file con metadati AI (Amazon, NY, UE).

### Costo per immagine
- Generazione: **1,5-2 crediti** a tentativo (Nano Banana 2, V dallo storico; in maschera non verificato).
- Con 2-3 tentativi per immagine buona [I]: **circa 4-6 crediti, 0,20-0,30 €**. Il costo vero è il tempo di maschera e controllo (circa 15-25 minuti a immagine [I]).

## 7. Controllo qualità per un capo (ogni immagine, a piena risoluzione, affiancata alla foto vera)

1. **Colletto:** forma delle punte, apertura, altezza del collo, simmetria, rigidità (non deve "sciogliersi" né appiattirsi). Contatto naturale tra collo generato e colletto vero, nessuna ombra mancante.
2. **Abbottonatura:** 3 bottoni, colore chiaro, distanza, asole, abbottonati o no come nella foto vera.
3. **Colore:** confronto col codice hex/Pantone su una zona in luce neutra; nessuna dominante calda della location trasferita sul capo (o, se c'è, coerente con la luce e approvata).
4. **Tessuto:** grana e lucentezza del pima, nessuna zona liscia o "plastica".
5. **Cuciture e orli:** spalle, maniche corte (lunghezza), orlo e spacchetti laterali, etichette o loghi se visibili.
6. **Vestibilità:** il capo non è più stretto, più lungo o più corto della foto vera; proporzioni del corpo credibili per la taglia.
7. **Bordi della ricomposizione:** nessun alone, nessun pixel di sfondo vecchio, nessuno stacco tra braccia generate e maniche vere.
8. **Luce:** direzione e temperatura della luce sul viso e sulla location uguali a quelle sul capo.
9. **Persona:** volto identico al casting, mani e anatomia, nessun sorriso non voluto (ERRORI 3, 7).
10. **Scena:** nessun oggetto non previsto, nessuna scritta finta, nessuna barra (ERRORI 4, 8).
11. **Serie:** stesso modello, stessa luce, stessa location in tutte le varianti colore (CLAUDE.md, coerenza assoluta).
12. **Dichiarazione:** nota AI presente e metadati scritti.

## 8. Cosa NON è verificato

- Costo di Nano Banana 2 / 2.1 in modalità maschera (mai osservato; gli strumenti non danno il prezzo).
- Che Nano Banana 2 lasci davvero intatta la zona fuori maschera (per questo c'è la ricomposizione al passo 5).
- Quanto bene il modello "attacca" collo, braccia e mani a un capo fermo (rischio principale del metodo).
- Resa di Nano Banana 2.1 rispetto a Nano Banana 2.
- Se Collars & Co. vende su Amazon o in UE (canali noti: sito, TikTok, Faire, negozi; doc 54).
- Se una foto della scheda prodotto rientra nella legge di New York sulle pubblicità: domanda per un avvocato.
- I prezzi di mercato (§10) sono tutti da blog di venditori.

## 9. La prova più economica (solo dopo il "sì" di Massimiliano)

- **Capo:** una polo o camicia di Massimiliano con colletto rigido, non un capo di Collars & Co. (le loro foto e il corpo del loro modello non sono nostri).
- **Input:** 1 foto indossata (fronte, viso fuori campo, luce diurna all'ombra) + 1 macro del colletto, scattate col telefono.
- **Generazioni:** 2 ritratti di casting Soul 2.0 (0,24 crediti) + 3 immagini finali (stesso modello, 2 location diverse + 1 posa 3/4), con al massimo 1 rifacimento ciascuna: 6 tentativi × 2 crediti = 12.
- **Totale massimo: circa 12,5 crediti (circa 0,60 €).** Il costo esatto della maschera si legge dallo storico dopo il primo tentativo; se supera i 4 crediti ci si ferma e si chiede.
- **Esito misurato:** i 12 controlli del §7 su ogni immagine, affiancati alla foto vera. Se 2 immagini su 3 passano, il metodo è pronto per un test pagato con un cliente.
- Tempo: circa 1 ora. Non serve prima della call: la call si fa anche senza.

## 10. Come proporlo a Justin e a che prezzo

**Quando:** solo se Justin parla di foto, varianti colore, nuove location o costi degli shooting. Il prodotto principale della call resta il pilota video (doc 54). Prima della call Massimiliano decide se togliere il "catalogo no" del 5/10.

**Frase (inglese):**
> "We can also do on-model lifestyle images for your colourways, but only from a real photo of each colour. We never let the AI redraw the shirt: your actual garment, collar, buttons and fabric, stays pixel for pixel from your photo, and we generate only the model and the location around it. Same model, same light across every colour. If that's useful, the first step is a small paid test on one colourway."

Se chiede "can you do it from a flat-lay?": "We can, but then the AI redraws the collar, and on your product the collar is the whole point. We won't put that on a product page."

**Prezzi di mercato** [V debole]:
- strumenti AI fai-da-te: $0,10-3 a immagine (FASHN $0,075, Google $0,06, Botika $0,73-1,16); https://vantaige.io/blog/ai-clothing-photoshoot-cost-2026 · https://www.blendnow.com/blog/best-ai-fashion-model-tools-for-clothing-brands
- foto on-model tradizionale: $200-500 a immagine tutto compreso; un preventivo da $40 a immagine finisce spesso a ~$84; shooting di una giornata $2.500-8.000 per 40-80 immagini. https://huhu.ai/blog/ai-product-photography-replacing-traditional-photoshoots-2026 · https://www.wearview.co/blog/real-cost-fashion-photoshoots

**Prezzo indicativo Scrollcraft [I]:** **$45 a immagine**, minimo 10 immagini ($450, come il pilota video), con brief, casting, controllo dei 12 punti e 1 giro di revisione. Sta sotto lo shooting (~$84-500) e sopra gli strumenti fai-da-te, perché si vende la direzione e la garanzia sul capo, non il software. Prova pagata d'ingresso: 1 variante colore, 4 immagini, $180. Prezzo da far approvare a Massimiliano.

## Fonti principali

- https://fal.ai/learn/tools/best-virtual-try-on-apis-2026
- https://help.fashn.ai/plans-and-pricing/api-pricing
- https://docs.fashn.ai/api-reference/model-swap
- https://fashn.ai/model-swap
- https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/imagen/virtual-try-on-001
- https://cloudprice.net/models/google-virtual-try-on-1
- https://botika.com/resources/case-studies
- https://www.photta.app/pricing-and-reviews/botika
- https://www.wearview.co/blog/photoroom-pricing
- https://kive.ai/learn/virtual-try-on-vs-ai-product-photography
- https://discuss.google.dev/t/issues-with-virtual-try-on-stability-face-distortion-and-incorrect-sleeve-rendering-prompt-for-try-on-in-nano-banana/324604
- https://docs.apiyi.com/en/faq/nano-banana-pro-print-distortion.md
- https://www.rewarx.com/blogs/why-ai-image-tools-struggle-apparel-categories
- https://www.rewarx.com/blogs/why-ai-model-photography-doesnt-match-product
- https://www.graswald.ai/blog/how-ai-on-model-imagery-meets-enterprise-brand-quality-standards
- https://www.airframe.ai/product/botika-com/analysis
- https://kalkine.com.au/news/stocks/zalando-uses-ai-to-speed-up-marketing-caigns-cut-costs
- https://fashionunited.com/news/fashion/h-m-turns-to-ai-digital-twins-in-new-campaign-as-fashion-grapples-with-blurred-realities/2025070466982
- https://www.nbcnews.com/business/business-news/ai-models-levis-controversy-backlash-rcna77280
- https://www.junglescout.com/resources/articles/amazon-image-requirements/
- https://www.astria.ai/articles/amazon-product-images-apparel/
- https://www.eweek.com/de/news/amazon-ai-generated-product-images-labels-new-york-law/
- https://novadata.io/resources/news/amazon-sellers-label-ai-generated-people-ny-law-july-23-2026
- https://www.hunton.com/privacy-and-cybersecurity-law-blog/new-york-enacts-law-regulating-the-use-of-ai-generated-synthetic-performers-in-advertising
- https://mcdermottlaw.com/insights/new-yorks-synthetic-performer-disclosure-law-what-advertisers-need-to-know
- https://craftshift.com/disclose-ai-generated-product-images-shopify-2026/
- https://nightjar.so/blog/ai-product-photography-legal-guide
- https://www.claimlane.com/resources/blog/eu-ai-act-article-50-what-changes-on-2-august-2026-for-fashion-brands
- https://vantaige.io/blog/ai-clothing-photoshoot-cost-2026
- https://huhu.ai/blog/ai-product-photography-replacing-traditional-photoshoots-2026
- https://www.wearview.co/blog/real-cost-fashion-photoshoots
- https://solefeed.com/shop/collars-co/semi-spread-collar-polo-navy-u3p9w1 (colori e prezzo $88)
- Higgsfield, sola lettura (7/10): `models_explore` (recommend, search "try-on" e "fashion", get `nano_banana_2_1` e `marketing_studio_2_image`), `apps_search`, `get_presets`.
- File interni: docs 30, 32, 33, 34, 42, 54; `PROCEDURE.md`; `ERRORI.md`; screenshot della pagina prodotto Collars & Co. (Massimiliano, 7/10).
