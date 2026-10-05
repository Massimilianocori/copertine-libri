# Higgsfield: catalogo dei workflow ufficiali per Scrollcraft (studio del 5/10/2026)

Studio a costo zero: nessuna generazione, nessun upload, nessuna spesa. Fonti: `get_workflow_instructions` (catalogo + SKILL.md di ogni workflow), `get_workflow_bundle_file` (riferimenti chiave), `models_explore` (sola lettura), documenti interni 18, 19, 30, 31, `ERRORI.md`, `PROCEDURE.md`.

Legenda: **[V]** = verificato nella fonte indicata; **[I]** = ipotesi o deduzione mia, da provare.

## 0. Elenco dei 12 workflow (catalogo ufficiale, [V])

| # | Workflow | Versione | Una riga | Trattato in |
|---|---|---|---|---|
| 1 | `ad-multiplier` | 1.4 | Da 1 video (4-30 s) a N versioni modificate (persone, prodotto, sfondo, testo) mantenendo moto, tagli, tempi, audio | sez. 1 |
| 2 | `ads-studio` | 1.2 | Annunci statici con copy + immagini (Meta/IG/FB) da brand o prodotto | sez. 2 |
| 3 | `brand-asset-creation` | 1.1 | Loghi, identità, mockup, packaging, brandbook, deck, grafiche social | sez. 3 |
| 4 | `character-sheet` | 1.0 | Prompt per tavola personaggio (vista intera + primo piano) | sez. 4 |
| 5 | `faceless-video` | 2.4 | Video di canale con voce narrante, senza volto (spiegazione, storia, bambini) | sez. 5 |
| 6 | `narration` | 1.1 | Voce narrante a finestre fisse, lettura continua, o "metti me nel video" | sez. 6 |
| 7 | `product-photoshoot` | 1.0 | Foto prodotto e still di marca (packshot, lifestyle, pack annunci, try-on) | sez. 7 |
| 8 | `thumbnail-generation` | 1.3 | Miniature YouTube/Instagram e copertine video | sez. 8 |
| 9 | `ugc-video` | n.d. | Video UGC (review, product, unboxing, try-on, tutorial, sito) | già in `31-ugc-regole-ufficiali-higgsfield.md`; solo riga qui (sez. 9) |
| 10 | `video-editing` | 1.0 | Montaggio nativo "Higgsedit": tagli, grafica animata, shader, titoli | sez. 10 |
| 11 | `video-montage` | n.d. | Unire clip finite, colonna sonora, sottotitoli bruciati | sez. 11 |
| 12 | `website-builder-flow` | 2026-07-25 | Siti, app, giochi su Higgsfield (3 tipi: game, website, app) | solo riga (sez. 12) |

Regola trasversale di tutti i workflow ([V], appendice `use_unlim`): `use_unlim` si passa solo se l'utente lo chiede; i modelli bloccati dal workflow non si sostituiscono; le chiamate non-generate (upscale, trascrizione, montaggio) si pagano comunque. Nota interna [V, doc 18 sez. 9]: i pass illimitati valgono solo dal sito higgsfield.ai, non dai tool MCP.

## Conflitti da ricordare con le regole di Scrollcraft ([V] confronto con CLAUDE.md/ERRORI.md)

| Cosa fanno i workflow | Regola Scrollcraft | Come si risolve |
|---|---|---|
| Modalità "full auto / go ahead / no questions" con default decisi dal workflow (varianti, stile, voce) | Niente iniziative, brief approvato prima; nessuna generazione senza "sì" | Non usare le modalità automatiche. Presentare il brief e il preventivo, aspettare il "sì" per ogni generazione |
| Modelli bloccati (es. `nano_banana_pro`, `minimax_h3`, `seedance_2_5`, `ad_multiplier`) | ERRORI n. 19: il modello lo decide Massimiliano dopo prova affiancata | Dire a Massimiliano quale modello il workflow blocca prima di partire; se non lo vuole, non usare il workflow ma la procedura manuale (PROCEDURE.md) |
| Voce predefinita (faceless: Cillian) o scelta in autonomia | Mai decidere un elemento di propria iniziativa | La voce va approvata nella scheda voce |
| Il workflow decide tagli, ritmo, "mostra solo il risultato finale" | Controllo fotogramma per fotogramma, confronto affiancato col casting | Aggiungere sempre i controlli di CLAUDE.md dopo ogni output |
| Il workflow sostituisce o rigenera da sé (retry automatici) | Ogni generazione = permesso + costo | I retry vanno comunicati e approvati; un retry costa crediti |

---

## 1. `ad-multiplier` (v1.4)

**A cosa serve [V].** Da UN video sorgente di 4-30 s produce una o molte versioni modificate in modo indipendente, conservando movimento, inquadrature, tagli, tempi, formato e audio originale. Operazioni: sostituire, aggiungere, togliere, modificare persone, animali, prodotti, oggetti, abiti, sfondi, attributi, testo esplicitamente indicato. Più modifiche simultanee per uscita. Se mancano immagini, può generare persone adulte sostitutive.

**Quando usarlo per Scrollcraft.** Varianti di un annuncio già approvato (stesso video, creator diversa, prodotto diverso, sfondo diverso): è il cuore del pacchetto "10 hook / varianti" e dell'offerta white-label alle agenzie. NON è per hook diversi con inquadrature diverse (quelli si girano a parte).

**Input richiesti [V].**
- Un solo video sorgente misurato 4,0-30,0 s (fuori intervallo: stop, nessun taglio automatico).
- Elenco ordinato delle uscite o N.
- Immagini di sostituzione: tutte, alcune o nessuna.
- Risoluzione finale: 720p (consigliata) o 1080p.

**Modelli bloccati [V].** `ad_multiplier` (descritto da `models_explore` come "powered by Seedance 2.5"), sempre `mode:"video_edit"`, `generate_audio:false`, `count:1`, una chiamata per posizione. Mai `seedance_2_5` diretto. Persone mancanti: `soul_2` (3:4, 2k, `count:1`). Il costo in `video_edit` è "billed by that video's duration" [V, schema].

**Passi principali [V].**
1. Intake unico (modifica, N, immagini, risoluzione).
2. Registrare il video, misurarlo con ffprobe nel sandbox, analizzarlo UNA volta con `video_analysis_create`.
3. Pianificare le uscite in ordine (mappatura bersaglio, tempi dal sottotitolo/scene analizzate).
4. Acquisire riferimenti: immagini dell'utente oppure persone Soul 2.0 da approvare.
5. Scrivere un prompt per uscita (max 3900 caratteri; formato COMPACT o DETAILED; per sostituzioni di persone solo DETAILED).
6. Generare una posizione alla volta (anteprima muta).
7. Finalizzare: audio originale ripristinato dal sorgente, controlli di durata/aspetto/risoluzione, upload e conferma.

**Regole e divieti [V].**
- Sostituire una persona = sostituzione completa in ogni apparizione; l'originale non deve sopravvivere (tagli, riflessi, ombre). Le persone non mappate restano.
- L'immagine mappata comanda l'intero aspetto (volto, capelli, corpo, abiti, scarpe, accessori), salvo capo separato o istruzione esplicita.
- Sempre il blocco fisso: "Preserve every caption, subtitle, and other untargeted on-screen text element from @Video1 exactly as it appears..."; mai aggiungere/togliere sottotitoli in automatico.
- Mai prodotto cartesiano di liste; mai ritaglio o loop del sorgente.
- Persona generata: solo adulti 20+; sotto i 20 serve riferimento utente o consenso a rifarla adulta. Contrasto obbligatorio su due assi (presentazione etnica apparente e acconciatura) rispetto alla persona sostituita; stile "strikingly beautiful/handsome" imposto dal workflow.
- Un retry per posizione fallita; mai ripetere un job in attesa; mai consegnare l'anteprima muta (si consegna il file finale con audio ripristinato).

**Errori comuni [V dal flusso / I per lo studio].**
- [V] Sorgente fuori 4-30 s; mappatura ambigua; prompt oltre 3900 caratteri o con tag immagine non dichiarati.
- [V] Ripetere un job in attesa; consegnare l'anteprima senza audio.
- [I] Per Scrollcraft: il workflow genera persone "attraenti" di sua scelta, in conflitto con "coerenza assoluta, casting approvato": per le varianti usare sempre immagini del casting approvato come riferimento e scartare ogni persona inventata dal modello.
- [I] Etichetta del prodotto che cambia tra le versioni: controllare in ogni fotogramma.

**Fattori di costo.** [V] durata del sorgente (fatturazione `video_edit` a durata), risoluzione (480p/720p/1080p), numero di uscite (N chiamate), persone generate con Soul 2.0 (immagini), retry (max 1 per posizione), sorgente di durata fino a 30 s. [I] tariffa al secondo uguale a Seedance (3 / 7 / 12 crediti a 480p / 720p / 1080p, doc 30): non verificata per `ad_multiplier`. Il workflow offre solo 720p o 1080p. Non verificato: costo reale (get_cost non consentito).

---

## 2. `ads-studio` (v1.2)

**A cosa serve [V].** Annunci STATICI con copy e immagini, tramite i tool `ads_studio_*`: da sito di brand (ricerca brand kit e prodotti), da brand o prodotto già esistenti, da link prodotto, da foto più descrizione, o da solo prompt. Genera titolo, testo principale, CTA, URL.

**Quando usarlo per Scrollcraft.** Solo per annunci statici Meta (feed, stories). Non per video, UGC o foto prodotto senza copy.

**Input richiesti [V].** Brand (sito) oppure prodotto (link, foto con descrizione o testo); numero totale di creatività; formato (`1:1`, `9:16`, `16:9`, `3:4`; **`4:5` non disponibile**); obiettivo solo se chiaro (sales, leads, traffic, awareness, engagement).

**Modelli bloccati [V].** Nessun modello scelto da noi: Ads Studio decide in proprio (non dichiarato). **[I]** perciò non rispetta "modello deciso da Massimiliano": da dire in anticipo.

**Passi principali [V].**
1. Partire da brand o da prodotto (mai inventare domini: con solo il nome si chiede conferma del sito).
2. Aspettare la lettura (brand circa 1,5 minuti; prodotto circa 1 minuto): niente quote né generazioni prima che prodotto sia `completed`, `texts_ready: true` e brand `done`.
3. Proporre prodotti e chiamare `ads_studio_quote` con gli stessi argomenti della generazione; comunicare i crediti.
4. Generare solo dopo il sì esplicito al prezzo, una sola chiamata, `idempotency_key` fissa.
5. Seguire la run solo su richiesta; i quadri sono pronti quando `still_rendering` è false (circa 3 minuti dopo la scrittura).

**Regole e divieti [V].** Mai polling in loop; mai usare `generate_image` per annunci da foto prodotto; mai generare prima del sì al prezzo; mai `4:5`; mai passare id di Ads Studio ai tool di job generici; non mescolare "brand kit" di Ads Studio con quello di Marketing Studio; modifiche e varianti non disponibili da questi tool (solo app web).

**Errori comuni [V].** Quotare con prodotto ancora in lettura (annunci generici); riusare l'`idempotency_key` per un altro lotto o crearne una nuova per un retry (si paga due volte); link prodotto trattato come brand.

**Fattori di costo.** [V] `ads_studio_quote` restituisce i crediti in anticipo (è un preventivo non una generazione: va comunque chiesto a Massimiliano se `quote` è ammesso, in analogia a get_cost rifiutato, PROCEDURE.md). Numero di creatività (`total`), numero di prodotti (ciascuno una run), ricerca brand. Importo reale non verificato.

---

## 3. `brand-asset-creation` (v1.1)

**A cosa serve [V].** Creare asset di marca: loghi, identità, palette, tipografia, mockup (packaging, merchandising, insegne), brandbook, deck, grafiche social, poster, banner. Conserva esattamente gli asset ufficiali forniti; ricolorazione e export SVG/PNG deterministici.

**Quando usarlo per Scrollcraft.** Grafica finale su nero dello spot, mockup del prodotto del cliente, pacchetto grafico quando il cliente non ha logo/palette. Per spot di marca solo se il cliente non fornisce materiali.

**Input richiesti [V].** Materiali ufficiali del cliente (logo, palette, font) da bloccare uno per uno; deliverable richiesti; formato mockup/rapporto prima di generare. Per un nuovo logo serve richiesta esplicita.

**Modelli bloccati [V].** Recraft V4.1 (`recraft_v4_1`, vettoriale) unico generatore di logo SVG; Seedream per mockup (id da risolvere dal riferimento `mockups.md`); GPT Image 2 solo come secondo stadio quando nel mockup c'è testo leggibile; GPT Image 2 per grafiche social.

**Passi principali [V].** Classificare (apply-existing, extend-partial, create-identity) → leggere stato approvazioni nel sandbox → intake con una sola domanda compatta → inventario e blocco asset → costruire solo gli slot mancanti (palette → logo → tipografia, ciascuno approvato dall'utente) → produrre gli output → QA e approvazione.

**Regole e divieti [V].**
- Mai ridisegnare un logo caricato se si può posizionare esattamente; mai usare il generatore di loghi quando esiste il logo ufficiale.
- Mai inventare missione, valori, claim, prezzi, statistiche, sapori.
- Ordine nuovo logo: opzioni palette → attesa scelta → solo allora tre loghi.
- Copiare esattamente hex e font in ogni prompt (Brand Lock). Testo utente non parafrasato.
- Mai file nativi Figma/Canva/PSD/AI/EPS promessi; i font personalizzati vanno installati dal destinatario.
- Niente narrazione del processo interno all'utente.

**Errori comuni [V].** Chiedere di nuovo cose già dette; fare Brandbook senza slot approvati; rigenerare un logo ufficiale; usare script ad hoc al posto di `brandkit.py` per ricolorare.

**Fattori di costo.** [V] tre candidati logo (batch distinti), opzioni palette, mockup (immagini Seedream/GPT Image 2), brandbook (script nel sandbox, senza generazione). [I] il costo è soprattutto in immagini; nessun tariffario verificato.

---

## 4. `character-sheet` (v1.0)

**A cosa serve [V].** Costruire un prompt (e, su richiesta, generare) per una tavola personaggio a più viste: split-screen (intera a sinistra, primo piano a destra), turnaround, espressioni, varianti di outfit, triplo pannello. Motore "anti-AI / non ritoccato".

**Quando usarlo per Scrollcraft.** Creazione di personaggi (come Sienna, doc 19) e casting da usare come riferimento volto in ogni generazione.

**Input richiesti [V].** Descrizione del personaggio (identità, volto, capelli, corpo, abiti dalla testa ai piedi), preset di stile, composizione, "genera sì/no".

**Modelli bloccati [V].** Nessuno bloccato: "account default image model" oppure `models_explore(recommend)`. Formato 16:9 (o 3:2) per split-screen. [I] La nostra guida interna (doc 18) indica GPT Image 2, 2K, 16:9, fondo bianco.

**Passi principali [V].** Leggere il brief → scegliere stile → scegliere composizione → riempire gli slot in ordine (composizione, identità, volto, occhi con clausola anti-riflesso, sopracciglia, capelli, modulo realismo, corpo, abbigliamento, luce, coda qualità, coda negativa) → emettere un prompt su una riga → generare solo se richiesto.

**Regole e divieti [V].**
- Realismo = anti-ritocco (pori, asimmetrie, trucco non perfetto, nessuno smoothing).
- Solo personaggi ORIGINALI: mai somiglianza a persone reali o IP; celebrità solo come vago spirito.
- Adulti con struttura facciale matura (niente "baby face").
- Coerenza che si porta avanti: ogni dettaglio già stabilito resta, si cambia solo ciò che è richiesto.
- Sinistra sempre in piedi e a figura intera; destra sempre primo piano; una sola persona, niente oggetti, niente specchi.
- Non generare senza richiesta esplicita (default = solo testo).

**Errori comuni [V].** Pannello sinistro seduto o tagliato; seconda persona o manichino nel campo; volto da "baby face"; pelle plastica; occhi con riflessi enormi.

**Fattori di costo.** [V] solo la generazione dell'immagine (una per tavola; correzioni mirate = immagini in più); modalità prompt = zero. [V, doc 30] immagine Nano Banana ≈ 2 crediti; per GPT Image 2 costo non verificato.

---

## 5. `faceless-video` (v2.4)

**A cosa serve [V].** Video finito di canale con voce narrante, senza presentatore in video. Cinque tipi: Explainer, History, Kids, Picture Story, Fairy Tale & Myth. Stile non fotorealistico bloccato, asset riutilizzabili, una voce, sottotitoli bruciati.

**Quando usarlo per Scrollcraft.** Poco: serve per video educativi o di canale, non per annunci di prodotto. **Non** per spot, UGC, demo di prodotto, video con volto o presentatore (esclusi dal workflow stesso). [I] Possibile solo per un cliente che vuole un canale narrato o un contenuto "spiegazione del problema" a bassa produzione.

**Input richiesti [V].** Intake in ordine fisso nella Phase 0 (tipo di canale, soggetto, durata a multipli di 10 s, formato, stile, voce, sottotitoli sì/no, miniatura sì/no, modalità movimento animata o scene fisse).

**Modelli bloccati [V, regola 1].** Immagini/asset `seedream_v5_pro` (1k); clip `minimax_h3` a 2K; narrazione `text2speech_v2` variante `elevenlabs` (`seed_audio` solo per canzone Kids e lettura continua di stills); musica `sonilo_music` (solo strumentale). Nessun altro modello.

**Passi principali [V].** Phase 0 intake → 1 ancora di stile → 2 asset (personaggi, luoghi, oggetti) → 3 copione e piano blocchi → 4 blocchi video (ciascuno 10 s con 5 tagli da circa 2 s) → 5 narrazione (carica `narration`) → 6 montaggio del master pulito → 7 sottotitoli (carica `video-montage`) → 8 nessun upscale automatico (8b miniatura) → 9 consegna di un unico file.

**Regole e divieti [V].** Un clip = un blocco da 10 s con 5 tagli duri; contare i tagli tornati (il modello ne consegna meno); mai una clip dal solo stile; `aspect_ratio` esplicito ogni volta; personaggi non parlano (eccezione solo Kids con personaggi parlanti); vietate le parole "child/kid/childlike" nei prompt e qualsiasi nome di marchio; durata fissa N×10 s, mai accorciare per audio breve; una voce bloccata (`voice.lock`) riletta a ogni chiamata; mai time-stretch; sottotitoli solo tramite `video-montage`; consegna di UN solo file; 12 richieste per chiamata batch.

**Errori comuni [V].** NSFW come falso positivo (~50%): ritentare con la scala di retry; blocchi con meno tagli del richiesto; sandbox che perde i file tra una chiamata e l'altra (ogni fase = una chiamata autosufficiente); `--data-binary` che carica file vuoti; link costruiti a mano.

**Fattori di costo.** [V] numero di blocchi (durata/10), un clip `minimax_h3` 2K per blocco, asset e chiave di stile (immagini 1k), una chiamata di voce per riga con ritentativi (max 3 per riga), musica, retry NSFW e di tagli (una rigenerazione per blocco), miniatura. [I] Costi non verificati (nessun `get_cost`); `minimax_h3` non misurato nello storico (doc 30).

---

## 6. `narration` (v1.1)

**A cosa serve [V].** Voce narrante in tre modi: (A1) riprese numerate adattate a finestre di tempo fisse (blocco da 10 s = 7,8-9,5 s di parlato), (A2) lettura continua di una storia lunga con voce bloccata, (B) "mettimi nel video": un video esistente più la foto di una persona consenziente diventa un presentatore a schermo nello stesso video.

**Quando usarlo per Scrollcraft.** Voiceover per video prodotto, spot narrati, doppiaggio su misura di un montaggio. Si attiva solo se richiesta esplicitamente (non per TTS generico, non per clonazione, non per voce come parte di un annuncio generato).

**Input richiesti [V].** Righe di testo numerate più coppia `voice_id` + `voice_type` (preset o element) scelta dal chiamante; per il modo B: video, UNA foto di persona consenziente non pubblica, voce bloccata, testo facoltativo.

**Modelli bloccati [V].** A1: `text2speech_v2` variante `elevenlabs`; A2: `seed_audio`; B: `gpt_image_2` (riferimento su verde, fallback `nano_banana_pro`), `gemini_omni` per i blocchi parlanti (9:16, 10 s, 720p), `voice_change` obbligatorio, mai lipsync aggiuntivo. Voce predefinita se manca la scelta: Cillian (`d8ba9f14-...`), da NON accettare senza approvazione di Massimiliano.

**Passi principali [V].** A1: scrivere voce in `voice.lock` → ogni riga nel formato `[ {DELIVERY}, starts speaking immediately] [00:00-00:09] testo` → convertire l'MP3 → misurare parlato, pause e ritmo con `speech_metrics.sh` → riscrivere il testo se fuori finestra (max 3 tentativi). B: video e foto → riferimento su verde → blocchi parlanti → `voice_change` → compositing con `presenter_composite.sh` → controllo del contact sheet.

**Regole e divieti [V].** Una sola voce per lavoro; mai time-stretch né `speech_rate` (la durata si regola riscrivendo il testo); mai rigenerare un take già passato; mai clonare una voce; nessun dato personale nel testo (va a un fornitore esterno); nel modo B solo persone consenzienti non pubbliche e l'audio originale viene perso se mono.

**Errori comuni [V].** Voci diverse per blocco (si rilegge sempre il lock); take fuori finestra o con pause interne; rigenerare tutto per un solo take; sandbox senza file scaricabile.

**Fattori di costo.** [V] una chiamata di voce per riga (retry fino a 3), blocchi parlanti `gemini_omni` 10 s ciascuno più `voice_change` nel modo B. [V, doc 30] TTS Seed Audio circa 1,1 crediti a battuta; voce clonata 40 crediti una tantum (non qui, è un altro flusso). Costi di `text2speech_v2` e `gemini_omni` non verificati.

---

## 7. `product-photoshoot` (v1.0)

**A cosa serve [V].** Foto prodotto e still di marca finiti. Dieci modalità: `product-shot` (packshot), `lifestyle-scene`, `closeup-product-with-person`, `pinterest-pin`, `hero-banner`, `social-carousel` (3-10 slide), `ad-creative-pack` (varianti per test), `virtual-model-tryout`, `conceptual-product`, `restyle`.

**Quando usarlo per Scrollcraft.** Foto prodotto del cliente, immagini di partenza per spot (ma con riserva: vedi sotto), pacchetti statici per annunci a pagamento (con `ad-creative-pack`), try-on con modella AI (solo indicativo).

**Input richiesti [V].** Immagine prodotto confermata (o descrizione dettagliata: categoria, forma, imballo, materiale, colore, etichetta); modalità; numero di varianti (default 3); direzione visiva; rapporto; testo esatto sull'immagine; palette. `restyle`, `virtual-model-tryout` e `closeup-product-with-person` richiedono SEMPRE un'immagine di origine.

**Modelli bloccati [V].** `nano_banana_pro` sempre, 2k, `count:1`, riferimenti con ruolo `image_references`; il prompt termina con la riga `resolution: 2k`. Per prodotto solo testo: la prima variante (indice 0) diventa il riferimento delle altre.

**Passi principali [V].** Intake (silent defaults se "full auto") → scegliere modalità → caricare i 6 riferimenti (modalità, tipografia, vocabolario fotografico, riferimenti fotografi, prompt negativi, rifinitura) → verificare `nano_banana_pro` con `models_explore` → batch indicizzato → eventuale rifinitura (max 2 per indice, un solo riferimento) → galleria finale unica.

**Regole e divieti [V].**
- Nomi di fotografi, testate, rivenditori e concorrenti sono ancore interne: mai nei prompt; solo descrittori concreti di luce, palette, composizione.
- Nessun claim, materiale, prezzo, colore di marca o etichetta inventati.
- Regola della tipografia a tre casi: testo concreto indicato → integrato; testo in post → zona calma "tonalmente uniforme" (mai "negative space" o "banda vuota", crea bande piatte); altrimenti non menzionare il testo.
- Non per Amazon (compliance), video, miniature, ritratti generici, UGC.
- Ogni variante materialmente diversa; mai `count:N` per prompt distinti.
- Controllo visivo opzionale: senza immagine vista, non dichiarare superati i controlli di qualità.
- Prodotto = eroe: nel try-on "il prodotto resta identico al riferimento".

**Errori comuni [V].** Bande di colore piatte per aver forzato "spazio vuoto"; etichette deformate (usare la sezione anti-text-warp); mani e dita nel try-on; nomi di fotografi nel prompt; stile "stock".

**Fattori di costo.** [V] numero di varianti × 2k per immagine con `nano_banana_pro`; rifiniture (max 2 per indice; il budget totale è 3 invii per indice); retry di errori tecnici (1 per indice). [V, doc 30] Nano Banana Pro ≈ 2 crediti per immagine (verificato dallo storico crediti). Pack annunci predefinito = 5 varianti ≈ 10 crediti [I, calcolo].

**Nota Scrollcraft [I].** Per le immagini di partenza degli spot (casting, coerenza volto), questo workflow non basta: non usa il casting approvato come riferimento volto e blocca il modello. Usarlo per foto prodotto e still statici, non per storyboard con la modella.

---

## 8. `thumbnail-generation` (v1.3)

**A cosa serve [V].** Miniature YouTube/Instagram e copertine video "cinematografiche e virali": concetto (16 schemi) → casting → scena → render 4K → ritocchi mirati → testo. Possiede la produzione di miniature: caricarlo PRIMA di chiamare `generate_image`.

**Quando usarlo per Scrollcraft.** Copertine per canali di clienti o per video campione. Non per annunci né per foto prodotto.

**Input richiesti [V].** Testo scena; 0-3 foto del volto o personaggio (il riferimento si blocca con Identity Lock); eventuale miniatura di riferimento (solo come esempio, mai inviata al modello); logo; titolo e se va "cotto" nell'immagine; rapporto (default 16:9); emozioni e numero di varianti (default shock per persone, max 16).

**Modelli bloccati [V].** Render `nano_banana_pro` a 4K sempre; logo 3D `gpt_image_2` (high, 4k, 1:1); ritocchi `seedream_v5_pro` 2k (fallback `seedream_v4_5` qualità high); 4:5 solo su Nano Banana.

**Passi principali [V].** Raccogliere input → cancello del personaggio (mai inventare una persona se ne è stata fornita una; se serve una persona e manca la foto, una domanda) → eventuale analisi della miniatura di riferimento con la propria visione → logo 3D se richiesto → un prompt per variante (11 blocchi in ordine) → controllo post-render → ritocchi Seedream → testo come overlay deterministico in PNG.

**Regole e divieti [V].**
- Default: render PULITO senza testo; il titolo si applica dopo con `bake_text_overlay.mjs` (nessun credito); testo dentro l'immagine solo su richiesta esplicita.
- Riferimento volto = Identity Lock per ogni persona; niente beautify.
- Il riferimento di stile non entra mai in `medias`.
- Una chiamata per variante (mai `count`).
- "Truthfulness law": l'immagine può esagerare ma deve rappresentare il video con onestà; nessun marchio o rete reali nei testi.
- Prova di leggibilità a circa 120 px di larghezza.

**Errori comuni [V].** Il volto deriva anche con Identity Lock (si rifà il render); testo "cotto" illeggibile; 4K con `use_unlim` rifiutato (`unlim_config_not_covered`); sostituire una persona fornita con un'altra.

**Fattori di costo.** [V] render in 4K (più caro del 2k), numero di varianti (emozioni × inquadrature, max 16), logo 3D, ritocchi Seedream, retry (max 2 per variante). Overlay testo = zero crediti. Importi non verificati.

---

## 9. `ugc-video` (solo riga)

[V, doc 31] Creator generata (identità bloccata), tavola 21:9 a 8 riquadri con GPT Image 2, pulizia obbligatoria con Seedream 5 Pro, clip Seedance 2.5 con 8 tagli e voce nativa, sei formati. Vincoli: niente testimonianze sintetiche, claim solo da lista del cliente, parole vietate. Dettaglio completo in `31-ugc-regole-ufficiali-higgsfield.md`; confronto strumenti e costi in `30-higgsfield-strumenti-confronto.md`.

---

## 10. `video-editing` (v1.0) — Higgsedit

**A cosa serve [V].** Montaggio nativo (Node, CLI `higgsedit` v0.14.0): importare immagini/video/audio, tagli e trim, mixaggio audio, layout, testo animato, forme, icone, maschere, fotogrammi chiave, transizioni, camera 2.5D, filtri, ombre, shader GLSL, titoli. Uscite: PNG, contact sheet, MP4/MOV/MKV (H.264, HEVC Main10, AV1), progetti modificabili.

**Quando usarlo per Scrollcraft.** Grafica finale su nero dello spot, titoli animati, card di chiusura, montaggio con curve e sovrapposizioni, non generativo. [I] Alternativa alle nostre ricette ffmpeg di PROCEDURE.md (punto 8) quando serve grafica animata; per un semplice montaggio o sottotitoli basta `video-montage`.

**Input richiesti [V].** Materiale fornito (clip, immagini, audio) o descrizione grafica; formato e dimensione; fps; durata.

**Modelli bloccati.** [V] Nessuno (nessuna generazione: strumenti di montaggio in sandbox). Esclusi: generazione di riprese, restyling generativo, trascrizione, traduzione sottotitoli, sottotitoli parlati normali.

**Passi principali [V].** Preparare il progetto (script JSX/TSX con `project()`, `p.add()`, `p.cut()`, `p.compose()`, `p.render()`) → `higgsedit build`, `frame`, `sheet` (controllo fotogrammi) → `render` → riservare lo slot con `media_upload`, eseguire render e PUT nella stessa `sandbox_exec`, `media_confirm` dopo HTTP 200.

**Regole e divieti [V].** Solo CLI v0.14.0 (se l'identità `f39e3bc5882b` differisce, segnalare, non installare); scene HTML, callback di animazione a runtime, LUT native e nodi di regolazione shader NON supportati; le build dell'intero script sostituiscono la timeline; nessuna pubblicazione di editor ospitato; non attivare per solo analisi o recensione di un video.

**Errori comuni [V].** Sandbox effimero (file persi fra due chiamate); anteprime shader del browser non equivalenti al render nativo; output a 10 bit con ripiego a 8 bit del compositore.

**Fattori di costo.** [V] nessun modello generativo; costi di crediti non dichiarati nel workflow. [I] probabilmente nessun credito di generazione (solo sandbox e upload), da confermare.

---

## 11. `video-montage`

**A cosa serve [V].** Unire clip esistenti in un video finito, aggiungere o cambiare colonna sonora, bruciare o ristilizzare sottotitoli parlati. Possiede tutta la produzione di sottotitoli (trascrizione, allineamento parole, posizionamento, controllo finale).

**Quando usarlo per Scrollcraft.** Montaggio finale di UGC e annunci, sottotitoli di stile TikTok, musica sotto il parlato. Per UGC c'è la variante "UGC-natural" (frasi corte, caso normale).

**Input richiesti [V].** Clip finite (o il video master), copione autorizzato e lingua per i sottotitoli (le parole mostrate vengono dal copione), look richiesto (`bold` TikTok, `paper`, `clean`) e font.

**Modelli bloccati.** [V] Nessun modello generativo: `faster-whisper` (o STT OpenAI solo se la chiave è già nell'ambiente) per l'orologio delle parole, ffmpeg per montaggio e burn.

**Passi principali [V].** Montaggio: probe di ogni sorgente → manifest di concat ordinato → tagli duri (nessuna transizione non richiesta) → verifica di durata, flussi, primo e ultimo fotogramma e di ogni giunzione. Sottotitoli: (1) trascrivere sull'audio più pulito → (2) verificare la trascrizione (similarità ≥ 0,90 col copione) → (3) bruciare un solo look → (4) verificare il burn (parole = parole, due fotogrammi a metà battuta).

**Regole e divieti [V].** Timing solo da Whisper, mai dal copione; mai consegnare una trascrizione non verificata; massimo 5 parole / 32 caratteri per sottotitolo, in basso, senza coprire il soggetto; mai ffmpeg scritto a mano per il burn; mai aggiungere musica non richiesta; il master pulito resta immutabile; nessun SRT ospitato (il backend non lo accetta); font Cyrillic: PatrickHand e PermanentMarker non coprono il cirillico.

**Errori comuni [V].** Sottotitoli che perdono parole o derivano (passo saltato); caption vuote per font senza glifi; consegnare un video non controllato.

**Fattori di costo.** [V] la nota dell'appendice: trascrizione e sottotitoli si pagano comunque e non rientrano nell'illimitato. Importo non dichiarato. [I] nessuna generazione di crediti, solo elaborazione nel sandbox.

**Nota Scrollcraft [V, PROCEDURE.md punto 8].** Per gli spot di marca il montaggio "senza scritte dentro lo spot" e la curva colori approvata restano la procedura interna: usare `video-montage` solo per sottotitoli di UGC e annunci, non per aggiungere testo agli spot.

---

## 12. `website-builder-flow` (solo riga)

[V] Obbligatorio prima di qualsiasi tool sito (`create_website`, `deploy_website`, `publish_website`, ecc.); tre tipi: `game`, `website` (indipendente, Tailwind/CSS, pipeline a fasi basata su immagini), `app` (integrata Higgsfield). Per il sito Scrollcraft valgono comunque ERRORI n. 12-14 e 17 (font reali, anteprima uguale all'online, un solo deploy al giorno). Non è un workflow di produzione di video o foto.

---

## 13. Tabella: lavoro del cliente → workflow da usare

Tutte le righe richiedono prima brief con ricerca approvato, preventivo scritto e "sì" per ogni generazione (CLAUDE.md). Colonna "Prove" = cosa è già verificato nei nostri documenti.

| Lavoro del cliente | Workflow principale | Workflow di supporto | Note / stato |
|---|---|---|---|
| UGC con creator che parla (singolo video) | `ugc-video` | `video-montage` (sottotitoli UGC), `narration` solo se si vuole controllare la voce parola per parola | [V] doc 31; in alternativa Marketing Studio per volume (doc 30) |
| Pacchetto 10 video + 10 hook (Holiday Ad Pack) | `ugc-video` per i master + `ad-multiplier` per le varianti dello stesso video | `video-montage` | [I] da provare su un master; l'hook con inquadrature diverse = nuovo video, non Ad Multiplier |
| Varianti di un annuncio già approvato (altra creator, altro prodotto, altro sfondo) | `ad-multiplier` | `video-montage` per sottotitoli nuovi | [V] regole workflow; costo da verificare |
| Cambio di testo/sottotitolo in un annuncio esistente | `ad-multiplier` (edit di testo esplicito) oppure `video-montage` per i sottotitoli parlati | | [V] testo mirato solo se indicato |
| Spot di marca (lusso, moda, gioielli) | Nessun workflow dedicato: procedura manuale di PROCEDURE.md (storyboard visivo, Cinema Studio o Seedance, blocchi, upscale) | `product-photoshoot` per foto prodotto, `video-montage` o `video-editing` per grafica finale su nero | [V] doc 30 e PROCEDURE.md; i workflow ufficiali non coprono lo spot con casting approvato |
| Foto prodotto / packshot / catalogo | `product-photoshoot` (`product-shot`) | | [V] `nano_banana_pro` 2k; prodotto con riferimento ufficiale del cliente |
| Foto lifestyle, prodotto in mano | `product-photoshoot` (`lifestyle-scene`, `closeup-product-with-person`) | | [V] etichetta da controllare; mani da controllare |
| Modella AI che indossa il prodotto (statico) | `product-photoshoot` (`virtual-model-tryout`) | `character-sheet` se serve un volto ricorrente | [V] il workflow non ricorda la modella tra generazioni; per coerenza volto serve riferimento da casting |
| Annunci statici Meta con copy | `ads-studio` | `product-photoshoot` (`ad-creative-pack`) se si vuole il controllo di stile | [V] `ads-studio` decide copy e modello; `ad-creative-pack` lascia a noi hook e prompt |
| Pacchetto annunci statici per test A/B | `product-photoshoot` (`ad-creative-pack`, 5 varianti predefinite) | `ads-studio` per il copy | [V] 12 hook disponibili (problema-soluzione, trasformazione, ecc.) |
| Pinterest, banner sito, carosello social | `product-photoshoot` (`pinterest-pin`, `hero-banner`, `social-carousel`) | `brand-asset-creation` se serve coerenza di marca | [V] |
| Logo, identità, mockup, packaging, brandbook, deck | `brand-asset-creation` | | [V] solo se richiesto esplicitamente; con asset ufficiali del cliente si usano così come sono |
| Personaggio ricorrente / casting / "influencer AI" | `character-sheet` (tavola) | tool `ai_influencer_*` e Soul ID (doc 18 sez. 7, doc 19) | [V] character sheet = riferimento immagine per tutti i modelli video |
| Voiceover per un video già montato | `narration` (A1 o A2) | `video-montage` per mix e sottotitoli | [V] voce approvata prima; mai la voce predefinita senza ok |
| "Metti il cliente come narratore nel suo video" | `narration` modo B | | [V] solo persona consenziente non pubblica |
| Montaggio di clip, musica, sottotitoli | `video-montage` | `video-editing` se serve grafica animata | [V] |
| Titoli animati, card finale, grafica animata | `video-editing` (Higgsedit) | | [V] solo CLI v0.14.0 |
| Miniature YouTube/Instagram | `thumbnail-generation` | | [V] volto del cliente con Identity Lock; render pulito + overlay del testo |
| Canale narrato senza volto (spiegazione, storia, bambini) | `faceless-video` | `narration`, `video-montage` | [V] non per annunci; modelli bloccati |
| Doppiaggio o cambio voce di una clip | Non è un workflow: tool `voice_change` / `dubbing` | | [V, PROCEDURE.md] |
| Sito o landing del cliente | `website-builder-flow` | | [V] vedi ERRORI n. 12-14 e 17 |

## 14. Non verificato / da provare

- Costo reale di ogni workflow (nessun `get_cost` o `ads_studio_quote` richiesto: non consentiti a costo zero).
- Se la tariffa di `ad_multiplier` coincide con quella di Seedance (3 / 7 / 12 crediti/s).
- Se `ad-multiplier` mantiene identità e etichetta prodotto con immagini del nostro casting (il workflow impone persone "attraenti" generate da Soul 2.0 quando mancano immagini).
- Qualità di `minimax_h3`, `gemini_omni`, `seedream_v5_pro` confrontata con Cinema Studio 4.0 e Seedance 2.5 (nessun confronto nello storico).
- Se `ads_studio_quote`, come `get_cost`, ricade nel rifiuto di Massimiliano (PROCEDURE.md punto 5): chiedere.
- Quali modelli Ads Studio usa sotto.
