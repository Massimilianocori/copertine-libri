# Higgsfield Marketing Studio, Ads Studio, Shorts Studio: guida operativa Scrollcraft (studio del 5/10/2026)

Studio a costo zero: nessuna generazione, nessun `get_cost`. Fonti: schemi dei modelli (`models_explore`), catalogo preset (`get_presets`, `show_marketing_studio_v2`), workflow ufficiale `ads-studio`, storico completo di `show_marketing_studio_generations` (13 voci, 1 sola pagina, `next_cursor` nullo), storico crediti (`transactions`, tutte le pagine dal 15/9), 14 video scaricati e controllati con ffmpeg. Letti prima: CLAUDE.md, ERRORI.md, PROCEDURE.md, docs 18, 19, 30, 31.

Legenda: **V** = verificato (fonte indicata), **I** = ipotesi.

## 1. Cosa esiste (V: `models_explore`, `show_marketing_studio_v2`)

| Modello (id) | A cosa serve | Parametri chiave |
|---|---|---|
| `marketing_studio_video` (v1) | annunci prodotto/UGC "one-click" | risoluzione 480/720/1080p, durata 12-15 s, audio on/off, `mode` (formato), `avatar_ids` (max 1), `product_ids`, `hook_id` (il "cosa", es. oggetto che entra in scena), `setting_id` (il "dove"), `ad_reference_id` (ricrea lo scenario di un video analizzato). Hook e setting solo per: UGC, Tutorial, Unboxing, Product Review, Virtual Try On. `ad_reference_id` è incompatibile con hook/setting. Avatar e prodotto collegati a un ad reference NON vengono applicati da soli: vanno passati a mano |
| `marketing_studio_v2_video` | v2: motion e UGC | `type`: `ugc`, `ugc_v2`, `hypermotion`, `2d_motion`, `mixed_media`, `saas_motion`. Durata motion 5-15 s; `ugc` parlato fino a 30 s (visto nello storico). `ugc_v2`: 480p o 720p, `generate_audio`, `mode_id`, 1 prodotto, fino a 6 immagini. `saas_motion`: parte da un URL pubblico (`brand_url`). `batch_size` 1-4. Formati 9:16, 3:4, 1:1, 4:3, 16:9, 21:9, auto. Slot media: `product_photo`, `character_photo`, `location_photo`, `avatars` |
| `marketing_studio_v2_reference2video` | ricrea un video di riferimento con il nostro personaggio e prodotto | ingressi: video, immagine personaggio, immagine prodotto. Nessun altro parametro |
| `marketing_studio_image`, `marketing_studio_2_image`, `ms_image` (DTC Ads) | immagini: product shot (con modella / da solo), poster, ads, marketplace | `marketing_studio_image`: 1k/2k/4k. `ms_image`: richiede `style_id`, kit brand, qualità low/medium/high, batch fino a 20, fino a 4 prodotti |

Nessuna generazione gratuita ("unlim") disponibile ora (`unlim.available: false`).

**Catalogo preset (V, `get_presets` / widget v2):**
- Feed Marketing Studio: 649 preset (categorie Motion, Product shot, Effects). Il widget UGC ne conta 986 (numero non spiegato, I: include varianti).
- Formato UGC nel widget v2: solo "talking head". Preset visti (12 su 986): Classic Unboxing, UGC Addiction, Mystery Box, Before and After, How-To, UGC Virtual Try On, Secret Hack Reveal, Direct-to-Camera, Product Hit, Selfie Testimonial, Spicy, Couple Sharing At Home.
- Motion, esempi per tipo: hypermotion (Monospace Callouts, Wheatpaste Wall, Green Tea Macro, Claymation Storm, Slow ambient), 2d_motion (Pastel Shape Choreography, Retro Starburst Orbit, Storybook Page Turns), mixed_media (Pixel Block Yard, 90s Bedroom CRT, Halftone Street Collage), saas_motion (Echo Wave, Ink & Ribbon, Nova).
- Product shot: standalone (Ice Cube Hover, Linen Lid Lift, Buried in Ice...) e con modella (Chilled Can, Golden Dew, Pink Eyeshadow...).
- **Non verificato:** l'elenco completo di hook, setting e avatar (lo strumento `show_marketing_studio` v1 non è disponibile in questa sessione). I tre `preset_id` usati nei nostri video (`da3c5285...`, `b58f8f83...`, `0d4bb966...`) risultano "non nel catalogo pubblicato": non sappiamo come si chiamano. Per rifare un video uguale si riusa l'ID.

## 2. Ads Studio e Shorts Studio (sola lettura)

| | Stato nostro account | Cosa fa (V) | Da verificare |
|---|---|---|---|
| **Ads Studio** | 0 brand, 0 prodotti, 0 run (V: list_brands, list_products, list_runs) | Solo **annunci statici** (non video) per Meta/Instagram: scrive il testo (headline, primary text, CTA) e rende le immagini. Parte da un brand (ricerca dal sito, circa 90 s), da un prodotto (link, foto con descrizione) o da un prompt. Prima si crea il prodotto, si aspetta `completed`, poi `ads_studio_quote` dà il prezzo in crediti, poi `generate` solo dopo il sì. Formati 1:1, 9:16, 16:9, 3:4 (**4:5 non esiste**, usare 3:4). Obiettivi: sales, leads, traffic, awareness, engagement. Rendering circa 3 minuti. Modifiche e varianti non sono disponibili via strumenti (solo web app) | Prezzo per creatività (richiede un prodotto per `quote`, non fatto); qualità testi e immagini; resa delle etichette |
| **Shorts Studio** | 0 sessioni (V) | Applica uno **stile visivo** a un corto (restyle). Preset CMS visti (16, ce ne sono altri): Bold Urban, Green Contrast, Urban Serenity, Warm Glow, Yellow Frame, Monochrome Vibes, Claymation, Marker Scribble, Sticker Type, Blue Comic, Red Graffiti, Watercolor, Pencil Sketch, Desktop, Acid Green, Balloon Type. Si possono creare preset propri | Ingressi richiesti, durata, costo, qualità: niente di documentato, nessuna sessione passata. Non usare per clienti finché non c'è una prova autorizzata |

## 3. Cosa abbiamo fatto davvero (V: storico + crediti + video)

14 video Marketing Studio (15-28/9) più 4 immagini. I video di Marketing Studio **escono con traccia audio** (V: tutti i 14). Il contenuto audio non l'ho ascoltato (nessuno strumento): voce e musica sono da verificare a orecchio.

| Video (id corto) | Tipo e preset | Prompt/brief | Durata richiesta → reale | Uscita | Crediti | Cr/s |
|---|---|---|---|---|---|---|
| Sienna Niacinamide `bdd7fb46` (28/9) | talking (preset `da3c5285`) | copione 30 s, foto prodotto, personaggio, location | 30 → 30,0 s | 720x1280 | 208,2 | 6,9 |
| Meridian parlato `a6602ac4` e `32ddb591` (17/9) | talking (`da3c5285`) | cammina, siede, applica crema, "un'unica ripresa" | 15 → 15,0 s | 720x1280 | 105,15 x2 | 7,0 |
| Noir parlato `7c58a884` | talking (`b58f8f83`) | uomo su divano, bottiglia ferma sul tavolino | 20 → 20,0 s | 720x1280 | 139,5 | 7,0 |
| Fort deodorante `f2111aa2` | talking (`b58f8f83`) | uomo con stick in mano, non lo apre | 15 → 15,0 s | 720x1280 | 105,15 | 7,0 |
| Wagwell parlato `bb97d37a` | talking (`b58f8f83`) | donna in cucina, zoom lento, rumore cane fuori campo | 15 → 15,0 s | 720x1280 | 105,15 | 7,0 |
| Unboxing Meridian `7ddff8e8` | prodotto (`0d4bb966`) | 3 scene con stacchi, mani solo polso | 15 → 15,1 s | 1440x2560 | 90,05 | 6,0 |
| Wagwell 4 inquadrature `104b4236` | prodotto (`0d4bb966`) | 4 setup con stacchi netti | 15 → 15,1 s | 1440x2560 | 90,05 | 6,0 |
| Noir film `cf1d233b` | prodotto (`0d4bb966`), immagine di partenza | prompt automatico "tenebroso" | 12 → 12,3 s | 1440x2560 | 72,23 | 6,0 |
| VOLT `671e243b` | prodotto (`0d4bb966`) | CGI energetico con grafica | 7 → 7,3 s | 1440x2560 | 42,53 | 6,1 |
| Barattolo bianco `c28537d3`, `2d549bae` | prodotto (`0d4bb966`) | prompt corto, zoom out, nessuno stacco | 6 → 6,6 s | 1440x2560 | 36,59 x2 | 6,1 |
| Baxter tubo `1a54e8c4`, `6d1a79d2` | prodotto (`0d4bb966`) | 3 sfondi (uno) / bagno vissuto (altro) | 11 → 11,5 s | 1440x2560 | 66,29 x2 | 6,0 |

Il tipo (`hypermotion`, `mixed_media` ecc.) non è registrato nello storico dei video di prodotto: non so quale dei quattro motion sia stato usato (I: preset `0d4bb966` è un formato "prodotto cinematografico"). Un addebito da 30,65 crediti (16/9, 22:04) non corrisponde a nessun video dell'elenco (I: video non completato o non mostrato).
Immagini: `marketing_studio_image` 2k = 2 crediti; `marketing_studio_2_image` = 1,5 crediti (16/9).
Totale Marketing Studio video: circa 1.300 crediti (circa 65 euro a 50 euro per 1.000 crediti, dato di Massimiliano) per 15 addebiti, media circa 87 a video. Saldo oggi: 529,88 crediti, piano Ultra.

**Costo osservato (V):** parlato 720p circa 7 crediti/s (15 s = 105, 20 s = 140, 30 s = 208); prodotto/motion in 2K circa 6 crediti/s (6 s = 37, 12 s = 72, 15 s = 90). Lineare. 15 s parlato circa 5,3 euro, 15 s prodotto circa 4,5 euro. Stessa tariffa di Seedance a 720p (doc 30); il 2K a 6 crediti/s è più economico del 720p.

## 4. Cosa ho trovato guardando i video (V: ffmpeg, 8 fotogrammi per video, rilevamento tagli, ingrandimenti)

Limite: non è un controllo fotogramma per fotogramma completo; sono 8 fotogrammi per video più 5 ingrandimenti a piena risoluzione e il rilevamento dei tagli (soglia 0,35).

| Problema | Dove (V) | Nota |
|---|---|---|
| **Etichetta specchiata o capovolta** | Meridian parlato: entrambi i video, "MERIDIAN" specchiato quando il vasetto viene girato. Baxter: entrambi i video, testo del tubo ruotato di 180 gradi ("Baxter", "OIL FREE MOISTURIZER" capovolti), nonostante il prompt dicesse "mai capovolto, leggibile". 4 video su 14 | Il prompt automatico scrive già "etichetta mai deformata", ma non basta. Istruzione esplicita nel secondo Meridian ("mai specchiata") non ha cambiato il risultato (V: confronto dei due) |
| **Stacchi non richiesti** | Meridian parlato: 3 stacchi (4,8 s, 8,6 s, 11,5 s) nel primo video e 2 (4,8 s, 11,0 s) nell'altro, pur con "un'unica ripresa continua, non un taglio". Wagwell parlato: 3 stacchi con "zoom lento continuo". Sienna 30 s: 1 stacco a 24,1 s (cambio inquadratura tra tavolo e primo piano) | Il modello monta da solo. Se serve una ripresa unica, non è garantita |
| **Stacchi richiesti rispettati** | Wagwell 4 inquadrature (stacchi a 3,9 s, 8,0 s, 12,4 s), unboxing (5,0 s, 10,4 s), Baxter 3 sfondi | I formati con scene elencate funzionano |
| **Oggetto "fermo" che si muove** | Wagwell parlato: la bottiglia doveva uscire dall'inquadratura senza toccarla; nel fotogramma finale è in primo piano accanto al viso. Aspetto dell'etichetta diverso dal film prodotto (tan e grassetto contro crema e serif), ma i due video usano foto prodotto diverse (da verificare se è lo stesso prodotto) | Comportamento "mai toccare" rispettato in Noir e Fort (V) |
| **Sorrisi non richiesti, mani** | Fort: un sorriso a metà video. Mani: nessuna anomalia vista nei fotogrammi campionati, ma 8 fotogrammi non bastano per i diti | Controllare tutte le mani frame per frame |
| **Testo in sovrimpressione** | VOLT: scritta "ELECTROLYTE HYDRATION" e logo, resi bene ma generati dal modello. Noir: "NOIR" nitido e stabile | I testi corti in stampatello reggono; prodotti con molte righe piccole (Baxter) no |
| **Prodotto reale di terzi** | Sienna 30 s mostra una bottiglia con etichetta "The Ordinary" leggibile | Marchio reale: va bene per i nostri test, non per un cliente senza permesso |
| **Voce in prima persona inventata** | Meridian ("tre settimane fa"), Wagwell, Noir, Fort | Contro le regole ufficiali (doc 31): dimostratrice, non cliente |

Punti riusciti (V): pelle realistica con texture, mano e camera "da telefono", etichette corte (NOIR, VOLT, WAGWELL, FORT) leggibili, motion di prodotto in 2K molto puliti (Noir film, VOLT, Wagwell 4 inquadrature, unboxing).

## 5. Guida per i nostri servizi

| Servizio | Strumento consigliato | Come | Cosa controllare |
|---|---|---|---|
| **UGC a volume (parlato)** | v2 `ugc` o `ugc_v2` con `batch_size` 2-4 | Un personaggio approvato (`character_photo`), foto prodotto ufficiale, copione da dimostratrice con claim approvati (doc 31). 720p, 15 s | Volto = casting, etichetta (orientamento), mani, bocca/labiale, sorrisi, stacchi, persone extra |
| **Varianti hook** | v1 `hook_id` (+ `setting_id`) o 4 copioni diversi con stesso personaggio | Cambiare solo il primo secondo e la prima frase; stessi prodotto e personaggio. Mai combinare con `ad_reference_id` | Prima frase non banale (doc 31), coerenza del personaggio tra varianti |
| **Annuncio prodotto, senza persona** | v2 hypermotion/mixed_media o preset prodotto, 2K, 6-15 s | Foto prodotto pulita e frontale, prompt corto, scene elencate con stacchi. Preferire etichette corte | Etichetta leggibile in ogni scena, forma, colori, nessun elemento inventato (ERRORI 4, 5, 8) |
| **Unboxing / tutorial / try-on** | v1 con preset dedicato | Preset "Classic Unboxing", "How-To", "UGC Virtual Try On" | Mani (max 2), un'azione per scena |
| **Motion grafico** | 2d_motion, saas_motion (da URL) | Per loghi, UI, annunci "design". Grafica di terze parti: assicurarsi che il testo sia quello del cliente | Ortografia di ogni parola, font |
| **Annunci statici (Meta)** | Ads Studio | Aggiungere il prodotto, aspettare la lettura, quotare, generare dopo il "sì" | Testi e claim (solo quelli approvati), 3:4 invece di 4:5 |
| **Copia di un video esistente** | reference2video / `ad_reference_id` | Solo con video di cui abbiamo i diritti | Che non imiti persone o marchi altrui |

**Regole pratiche dai test (V salvo indicato):**
1. Etichetta: il prompt "mai specchiata" non basta. Se l'etichetta ha testo piccolo o il vasetto si gira, rifare: (I) foto prodotto con etichetta frontale chiara e azione senza rotazione del prodotto (come regola doc 31: la camera si muove, il prodotto no).
2. Se serve una ripresa unica, non fidarsi: contare gli stacchi con ffmpeg (`select='gt(scene,0.35)'`).
3. Il parlato costa il 17% in più al secondo ma ha 720p; il prodotto è in 2K.
4. Un rifacimento costa 37-208 crediti: l'unica difesa è il brief e la foto prodotto giusti prima (stesse regole di CLAUDE.md: proporre, ricevere il "sì", poi generare).
5. Un brief per Massimiliano deve includere: preset/ID, durata, risoluzione, numero di varianti, costo atteso (6-7 crediti/s), claim approvati.

## 6. Limiti e cose ancora da verificare

| Da verificare | Perché | Come (con "sì" di Massimiliano) |
|---|---|---|
| Quale motore usa Marketing Studio | Il costo coincide con Seedance, ma non è dichiarato | Non importa per il costo; per la qualità serve una prova |
| Nomi dei tre preset usati e dei tipi (hypermotion ecc.) | Non nel catalogo pubblico | Aprire i preset nel widget |
| Elenco completo hook, setting, avatar | `show_marketing_studio` v1 non disponibile qui | Aprire il widget Marketing Studio |
| Prezzo `ugc_v2` 480p e `batch_size` | Mai usato | `get_cost` rifiutato da Massimiliano: chiedere prima |
| Prezzo e qualità di Ads Studio e Shorts Studio | Nessun brand, nessuna sessione | `ads_studio_quote` con un prodotto: serve il "sì" |
| Qualità audio, voce e labiale | Non ascoltabile qui | Ascolto da parte di Massimiliano o prova con trascrizione |
| Se uno stesso brief dà sempre stacchi non voluti | Solo 3 casi | Prova su 2 varianti, contando gli stacchi |
| Rispetto di "etichetta frontale e non ruota" nelle regole doc 31 | Non provato in Marketing Studio | Una prova (i test attuali hanno ruotato il prodotto) |
