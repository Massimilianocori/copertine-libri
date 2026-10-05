# Higgsfield: catalogo modelli, costi, preset e app (studio del 5/10/2026, costo zero)

Nessuna generazione, nessun `get_cost`, nessuna spesa. Strumenti usati, tutti di sola lettura: `models_explore` (video, immagini, audio, 3D, tutte le pagine), `transactions` (tutte le 6 pagine fino a `next_cursor` nullo, dal 15/9 al 5/10), `get_presets`, `apps_search`, `apps_describe`, `balance`, `show_plans_and_credits`, più `CLAUDE.md`, `ERRORI.md`, `PROCEDURE.md`, `18`, `19`, `30`, `31`.

Legenda: **V** = verificato (fonte indicata); **I** = ipotesi (non verificata, da provare o chiedere).
Regola di `CLAUDE.md`: il modello lo decide Massimiliano. Le tabelle "cosa scegliere" sono una proposta di partenza, non una scelta.

## 0. Limite importante dello storico crediti

`transactions` riporta solo: nome del modello, crediti, data, tipo (spesa, rimborso, accredito). **Non riporta risoluzione, durata, modalità né parametri.** Quindi:
- L'importo speso è **osservato (V)**.
- L'abbinamento a risoluzione e durata è **ricavato** dalle tariffe già verificate in `19` e `30` (3, 7, 12 crediti/s per Seedance 2.5 e Cinema Studio 4.0) e dalle durate note dei lavori: lo marco "ricavato (I)" quando non c'è una nota scritta nel repo.

## 1. Saldo e prezzo dei crediti (V, `balance` e `show_plans_and_credits`, 5/10)

| Voce | Valore |
|---|---|
| Saldo | 529,88 crediti (piano ULTRA, 3.000 crediti/mese) |
| Ricariche una tantum | 500 = 26 €; 1.000 = 49 €; 2.000 = 95 €; 4.000 = 190 € (scadenza 90 giorni) |
| Costo per credito | circa 0,048-0,052 € (coerente con "1.000 = 50 €" di `30`) |
| Accrediti storici | 270 (sub, 15/9), 3.000 (sub, 17/9, con azzeramento di 28,09), 2.000 (pacchetto, 24/9), 200 (3/10), 1.000 e 500 (5/10): pacchetti acquistati in totale 3.700 |
| Unlimited | `unlim.available = false` oggi sull'account; le offerte "7-Day / 365 Unlimited" sono acquistabili fino al 6/10 e valide sul sito web (Nano Banana Pro e Nano Banana 2, Kling 3.0 720p/5s per 7 giorni; Seedream 5.0 Lite, Seedream 4.5, FLUX.2 Pro 1K, Nano Banana, Kling O1 Image, GPT Image per 365 giorni; Soul V2 e Cinema con generazioni gratuite) |

## 2. Catalogo video (V, `models_explore`)

Colonne: ruoli media = ingressi accettati. "Audio" = audio nativo. Tutti i modelli sono testo e/o immagine verso video salvo dove indicato.

### 2a. Modelli principali (già usati da noi in alcuni casi)

| Modello (id) | Durata | Risoluzioni | Aspect ratio | Ruoli media | Parametri chiave | Punti di forza dichiarati | Limiti (dallo schema) | Provato da noi |
|---|---|---|---|---|---|---|---|---|
| Seedance 2.5 (`seedance_2_5`) | 4-30 s | 480p, 720p, 1080p | auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | start_image, end_image, image_references, video_references, audio_references | `mode` t2v / omni_reference / video_edit / video_extension; `draft` (480p, finalizzabile entro 7 giorni); `draft_job_id`; `generate_audio`; `bitrate_mode`; `extension_mode` | riferimenti multimodali, identità, audio di riferimento, modifica ed estensione video | niente genere/camera dichiarati; 4:5 non disponibile | Sì (molti) |
| Cinema Studio 4.0 (`cinematic_studio_video_4_0`) | 4-30 s | 480p, 720p, 1080p | auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | start_image, end_image, image_references, video_references, audio_references | stesse modalità di Seedance + `era_id`, `camera_model_id`, `camera_lens_id`, `camera_aperture_id`, `pacing_id`, `genre_id`, `light`/`light_id`/`light_custom`, `color_palette` | regia automatica del prompt: camera, luce, ritmo, genere, epoca, colore | i tag dichiarano solo 480p/720p ma lo schema accetta 1080p (e noi abbiamo pagato 1080p); niente `draft` | Sì (molti) |
| Kling v3.0 (`kling3_0`) | 3-15 s | `mode`: std, pro, 4k | 16:9, 9:16, 1:1 | start_image, end_image | `sound` on/off (off = meno crediti), `mode` | multi-shot, audio sincronizzato, motion transfer; ha unlimited | solo immagine iniziale e finale (niente riferimenti), niente 3:4 né 4:5 | Sì |
| Marketing Studio (`marketing_studio_video`, v1) | 12-15 s dichiarati | 480p, 720p, 1080p | auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | avatars, medias | `mode` (slug del formato: UGC, Tutorial, Unboxing, Product Review, UGC Virtual Try On), `avatar_ids` (max 1), `product_ids`, `hook_id`, `setting_id`, `ad_reference_id`, `generate_audio` | annunci prodotto e UGC in una chiamata | hook e setting solo per i 5 formati; `ad_reference_id` esclude hook e setting; 1 solo avatar. Nota: lo schema dice 12-15 s ma noi abbiamo un video da 30 s (208,2 crediti, `30`) | Sì |
| Topaz Video (`topaz_video`) | durata del sorgente | 1080p, 2160p | auto | video_references | `enhancement`, `frame_interpolation` | upscale | tariffa non dichiarata | Sì (3, 5, 3 crediti, 5/10) |
| Genjutsu motion transfer (`hf_mult_motion_control`) | n.d. | 480p, 720p, 1080p | n.d. | image_references, video_references | `resolution` | trasferisce il movimento di un video a soggetti in immagini | non dichiara durata | Sì, una volta (0 crediti, 26/9) |
| Voice Change, Dubbing, Sync Lipsync 3 | n.d. | n.d. | n.d. | input_video (+ input_audio per sync) | voci preset o elemento; lingue dubbing: eng, cmn, fra, hin, ita, jpn, kor, por, rus, tur, spa, deu, ara, pol, ind, fil, swe, fin; `sync_mode` bounce/loop/cut_off/silence/remap | doppiaggio in italiano disponibile (`ita`) | n.d. | Voice Change sì (2 e 4 crediti); Dubbing e Sync no |

### 2b. Altri modelli video (tutti non ancora provati da noi, V = non compaiono in `transactions`)

| Modello (id) | Durata | Risoluzioni | Aspect ratio | Ruoli media | Note dallo schema |
|---|---|---|---|---|---|
| Cinema Studio Video 3.5 (`cinematic_studio_video_3_5`) **nuovo** | min 4 s, default 15 | 480p, 720p, 1080p | auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | start/end image, image/video/audio references | `multi_shots` fino a 6 con `multi_prompt`; `camera_style` (9 stili), `light_scheme` (6), `color_grading` (8), `style_prompt`, `enhance_prompt`; **`prompt_language` di default `zh`**: impostare `en` |
| Cinema Studio Video 3.0 (`cinematic_studio_3_0`) | 4-15 s | 480p, 720p, 1080p, 4k | auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | image, start_image, end_image | genere (6), `generate_audio` default false; tag "sota, best-quality" |
| Cinema Studio Video v2 (`cinematic_studio_video_v2`) | 3-12 s | n.d. | 1:1, 4:3, 3:4, 16:9, 9:16 | image, start_image, end_image | `mode` pro/std, genere, `speedramp`, `multi_shots`, `cfg_scale`, `sound` |
| Cinema Studio Video (v1) (`cinematic_studio_video`) | 5 o 10 s | n.d. | 1:1, 4:3, 3:4, 16:9, 9:16 | image, start_image, end_image | `slow_motion`, `sound`; legacy |
| Seedance 2.0 (`seedance_2_0`) | 4-15 s | 480p, 720p, 1080p, 4k | auto, 16:9, 9:16, 4:3, 3:4, 1:1, 21:9 | start/end image, image/video/audio references | `mode` std/fast (fast solo 480p/720p), genere, bitrate; ha unlimited; incluso nel piano ("full access") |
| Seedance 2.0 Mini (`seedance_2_0_mini`) | 4-15 s | 480p, 720p | come 2.0 | come 2.0 | variante economica; ha unlimited |
| Seedance 1.5 Pro (`seedance1_5`) | 4, 8, 12 s | 480p, 720p, 1080p | auto, 16:9, 9:16, 4:3, 3:4, 1:1, 21:9 | start_image, end_image | audio opzionale |
| Ad Multiplier (`ad_multiplier`) | 4-30 s | 480p, 720p, 1080p | come Seedance 2.5 | come Seedance 2.5 | descritto come "powered by Seedance 2.5"; stesse modalità (t2v, omni_reference, video_edit, video_extension) |
| Kling 3.0 Turbo (`kling3_0_turbo`) | 3-15 s | 720p, 1080p | 16:9, 9:16, 1:1 | start_image | veloce, economico (tag "budget") |
| Kling 3.0 Omni Edit (`kling_video_edit`) | n.d. | std, pro, 4k | n.d. | video_references, image_references | modifica un video con testo e immagini |
| Kling 3.0 Motion Control (`kling3_0_motion_control`) | n.d. | std, pro | n.d. | image_references, video_references | `background_source` immagine o video; ha unlimited |
| Kling 2.6 (`kling2_6`) | 5 o 10 s | n.d. | 16:9, 9:16, 1:1 | start_image | audio nativo |
| MiniMax H3 (`minimax_h3`) | 4-15 s | 2K | auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | start/end image, image/video/audio references | `batch_size` 1-4 |
| MiniMax H3 Max (`minimax_h3_max`) | 5-15 s | 480p, 768p | come H3 | come H3 | veloce; `batch_size` 1-4 |
| Minimax Hailuo (`minimax_hailuo`) | 6 o 10 s | 512, 768, 1080 | n.d. | start_image, end_image | varianti minimax / fast / 2.3 / 2.3-fast; "fisica naturale, emozione del volto" |
| Google Veo 3.1 (`veo3_1`) | 4, 6, 8 s | qualità basic / high / ultra | 16:9, 9:16 | solo start_image | "ultra-realistico"; varianti preview / fast |
| Google Veo 3.1 Lite (`veo3_1_lite`) | 4, 6, 8 s | n.d. | 16:9, 9:16, auto | start_image, end_image | economico; audio opzionale (default no) |
| Google Veo 3 (`veo3`) | n.d. | n.d. | 16:9, 9:16 | start_image | varianti preview / fast |
| Gemini Omni Flash 1.1 (`gemini_omni_flash_1_1`) **nuovo** | 3-10 s | 360p, 720p, 1080p, 4k | 16:9, 9:16 | start/end image, image/video references | modalità: text-to-video, image-to-video, reference-to-video, edit (fino a 30 s); audio nativo |
| Gemini Omni Flash (`gemini_omni`) | 4-10 s | 720p | 16:9, 9:16 | image/video references | ha unlimited |
| Wan 3.0 / Wan 3.0 Prime (`wan3_0`, `wan3_0_prime`) **nuovi** | 2-30 s (o -1 = scelta del modello, fatturato come 10 s) | 480p, 720p, 1080p | auto, 16:9, 9:16, 1:1, 4:3, 3:4 | start/end image, image/video/audio references | audio nativo; `enable_thinking` (più lento, più aderente) |
| Wan 2.7 (`wan2_7`) | 2-15 s | 720p, 1080p | 16:9, 9:16, 1:1, 4:3, 3:4 | start/end image, audio_references | audio sincronizzato, personaggio coerente; ha unlimited |
| Wan 2.6 (`wan2_6`) | 5, 10, 15 s | 720p, 1080p | 16:9, 9:16, 1:1 | image/video/audio references | "stilizzato, sperimentale" |
| FLUX 3 Video (`flux_3_video`) **nuovo** | 5-20 s | 720p, 1080p | auto, 21:9, 2:1, 16:9, 4:3, 1:1, 3:4, 9:16 | start/end image, image_references, video_references | continuazione video, storyboard multi-frame, audio sincronizzato |
| FLUX 3 Video Edit (`flux_3_video_edit`) **nuovo** | max 15 s | n.d. | n.d. | video_references | **1 credito al secondo** del clip elaborato (dichiarato nello schema) |
| Grok Video 1.5 (`grok_video_v15`) | 2-15 s | 480p, 720p, 1080p | non dichiarati | start_image, image_references, audio_references | tag "preview", fisica e movimenti di camera |
| Grok Imagine Video 1.5 Lite (`grok_video_v15_lite`) | 1-15 s | 480p, 720p, 1080p (upscalato da 720p) | auto, 16:9, 9:16, 4:3, 3:4, 1:1, 3:2, 2:3 | start_image | veloce |
| Grok Video (`grok_video`) | 1-15 s | n.d. | 16:9, 9:16, 1:1 | start_image | versione precedente |
| Happy Horse Video (`happy_horse_video`) | 3-15 s | 720p, 1080p | 16:9, 9:16, 1:1, 4:3, 3:4 | start_image | testo e un fotogramma iniziale |
| Marketing Studio Video v2 (`marketing_studio_v2_video`) **nuovo** | motion 5-15 s, altri 4-30 s | `ugc_v2`: 480p, 720p | auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | input_images, product_photo, character_photo, location_photo, avatars | `type`: 2d_motion, hypermotion, mixed_media, saas_motion, ugc, ugc_v2; stile o preset da catalogo; `batch_size` 1-4 |
| Marketing Studio Reference Video (`marketing_studio_v2_reference2video`) **nuovo** | n.d. | n.d. | n.d. | input_video, character_image, product_image | rifà un video di riferimento con il nostro personaggio e prodotto |
| Draw To Video, Reframe | n.d. | 480p-1080p | vari | video, riferimenti | strumenti accessori |
| Strumenti di post | n.d. | n.d. | n.d. | video_references | Bytedance Video Upscale (1080p, 2k, 4k; preset common / aigc / short_series / ugc / old_film; `pro`), Topaz Hyperion 2.5 (SDR verso HDR), Video Deflicker, FPS Boost (ByteDance o Topaz, 16-120 fps), Video Background Remover, Depth Anything, Clipify (un video YouTube in clip con sottotitoli) |

Osservazioni dagli schemi (V):
- **Nessun modello video ha 4:5**: per Instagram feed servirebbe 3:4 o ritaglio. 9:16 è disponibile quasi ovunque (Veo, Gemini, Kling, Wan 2.6 e Grok 1.5 base sì; Grok Video 1.5 non dichiara gli aspect ratio).
- Solo Seedance 2.5, Cinema 4.0, Wan 3.0, Gemini Omni 1.1 e FLUX 3 Video superano i 15 s in una sola chiamata (30 s i primi tre, 20 s FLUX, 10 s Gemini 1.1 ma modifica fino a 30 s).
- Il `draft` è solo di Seedance 2.5 (480p finalizzabile entro 7 giorni).

## 3. Catalogo immagini (V)

| Modello (id) | Risoluzioni | Aspect ratio principali | Ruoli e parametri | Punti di forza dichiarati | Provato da noi |
|---|---|---|---|---|---|
| Nano Banana Pro (`nano_banana_pro`) | 1k, 2k (default), 4k | 1:1, 3:2, 2:3, 4:3, 3:4, 4:5, 5:4, 9:16, 16:9, 21:9 | image_references | qualità massima, testo e diagrammi, fotorealismo; unlimited | Sì (modello principale, 2 crediti) |
| Nano Banana 2 (`nano_banana_2`) | 1k (default), 2k, 4k | come sopra + auto | image_references, mask (inpaint) | veloce, alta qualità; unlimited | Sì |
| Nano Banana 2 Lite (`nano_banana_2_lite`) | 1k | come sopra | `thinking` MINIMAL/HIGH, mask | economico | No |
| Nano Banana (`nano_banana`) | n.d. | come sopra | image_references | economico; unlimited | No |
| GPT Image 2.5 (`gpt_image_2_5`) | 1k, 2k, 4k | auto, 1:1, 3:2, 2:3, 4:3, 3:4, 16:9, 9:16, 21:9, 27:16, 16:27, 9:8, 8:9, 4:5, 5:4 | varianti `flare` / `sunburst`; qualità low, medium, high, xhigh, max; `background` transparent | generazione e modifica, testo | Sì (variante Flare) |
| GPT Image 2 (`gpt_image_2`) | 1k, 2k, 4k | 1:1, 4:3, 3:4, 16:9, 21:9, 9:16, 3:2, 2:3 | qualità low/medium/high | testo, tipografia, fotorealismo; unlimited | Sì |
| OpenAI Hazel (`openai_hazel`) | n.d. | 1:1, 3:2, 2:3, auto | qualità low/medium/high | miglior testo, loghi, infografiche | No |
| Seedream 5.0 Pro (`seedream_v5_pro`) | 1k, 1.5k, 2k | 1:1, 4:3, 3:4, 16:9, 9:16, 3:2, 2:3, 21:9 | `remove_bg`, `is_inpaint` | ragionamento visivo, modifica a istruzioni; unlimited | Sì (passaggio anti-"effetto AI") |
| Seedream 5.0 Lite / Flash (`seedream_v5_lite`, `seedream_5_0_flash`) | fino a 2k | simili | qualità basic/high | modifica a istruzioni; Lite ha unlimited | No |
| Seedream 4.5 (`seedream_v4_5`) | fino a 4k (high ~6k) | 1:1, 4:3, 16:9, 3:2, 21:9, 3:4, 9:16, 2:3 | image_references | 4K, trasformazioni; unlimited | No |
| FLUX 3 Image (`flux_3_image`) **nuovo** | 768sq, 1k, 1.5k, 2k, 4k | molti, incluso 4:5, 5:7, 7:5, 1:2 | fino a 10 riferimenti, `batch_size` 1-4 | generazione e modifica multi-riferimento | No |
| FLUX.2 (`flux_2`) | 1k, 2k | 1:1, 4:3, 3:4, 16:9, 9:16 | varianti pro / flex / max | aderenza al prompt; unlimited | No |
| Flux Kontext (`flux_kontext`) | n.d. | 1:1, 4:3, 3:4, 16:9, 9:16 | image_references | modifica contestuale, trasferimento di stile | No |
| Kling O1 Image (`kling_omni_image`) | 1k, 2k | 1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3, 21:9 | image_references | fotorealismo; unlimited | No |
| Grok Image / Grok Image 2.0 | 1k, 2k | 1:1, 1:2, 2:1, 3:2, 2:3, 4:3, 3:4, 16:9, 9:16 | `mode` std/quality, qualità low/medium | espressivo, alto contrasto | No |
| Ideogram 4.5 (`ideogram_4_5`) **nuovo** | 1k, 2k | 24 formati, incluso 4:5 | fino a 5 immagini sorgente, mask, `seed` | tipografia | No |
| Recraft V4.1 (`recraft_v4_1`) **nuovo** | 1k, 2k | 1:1, 3:4, 4:3, 4:5, 5:4, 3:2, 2:3, 16:9, 9:16 | `model_type`: standard, vector, utility (foto prodotto e mockup puliti), utility_vector; palette fino a 10 colori; `background_color` | loghi, icone, packshot prevedibili | No |
| Soul 2.0 / Soul V2 (`soul_2`, `soul_v2`) | 1.5k, 2k | 1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3 | `soul_id`, 1 immagine di riferimento | UGC realistico, moda, personaggi; unlimited | Sì (0,12 crediti, o 0 con unlimited) |
| Soul Cinema / Soul Cinema Studio | 1.5k, 2k | fino a 21:9 | `soul_id`, `style_id`, `custom_reference_id`, `enhance_prompt` | still cinematografici | No |
| Cinema Studio Image 2.5 (`cinematic_studio_2_5`) | 1k, 2k, 4k | fino a 21:9, incluso 4:5 | image | still cinematografici fino a 4K | No |
| Cinematic Studio Image (`cinematic_studio_image`) | 1k, 2k, 4k | fino a 21:9 | richiede ID camera, ottica, focale (apertura opzionale) | controllo fotocamera virtuale | No |
| Marketing Studio Image (`marketing_studio_image`) | 1k, 2k, 4k | inclusi 4:5, 5:4 | image | annunci prodotto in un clic | Sì (2 e 1,5 crediti) |
| Marketing Studio Product Shot (`marketing_studio_2_image`) **nuovo** | n.d. | 1:1, 3:2, 2:3, 4:3, 3:4, 9:16, 16:9 | `type`: product_shots, product_shots_people, poster, ads, marketplace; stile o preset; `want_person` | foto prodotto, poster, annunci, marketplace | No |
| DTC Ads (`ms_image`) | 1k, 2k, 4k | molti | `style_id` obbligatorio (da scegliere dall'elenco stili), `brand_kit_id`, `product_ids` fino a 4, `batch_size` 1-20 | annunci DTC con brand kit | No |
| Soul Cast, Soul Location, Cinematic Studio Soul Cast / Location | n.d. | 16:9 o vari | `budget` 10-500 per Soul Cast | personaggio e ambienti coerenti | No |
| Strumenti: Outpaint, FLUX.2 Pro Outpaint, Topaz Image (e generativo), Bytedance Image Upscale (2k, 4k), Image Background Remover, Image Decompose (livelli), 3D Jutsu Angles (Seedream 5 Pro), AutoSprite, Z Image, Image Auto | vari | vari | vari | utilità | Solo Outpaint (2 crediti, 3/10) |

## 4. Audio (V)

| Modello (id) | Cosa fa | Parametri | Provato |
|---|---|---|---|
| Seed Audio 1.0 (`seed_audio`) | voce da testo, con riferimento voce/audio o immagine; ha unlimited | formato, frequenza, velocità (-50..100), volume, tono (-12..12), voce preset o elemento | Sì (1,1 e 0,7 crediti) |
| Eleven v4 (`elevenlabs_v4`) | dialoghi fino a 10 voci, 10.000 caratteri | stabilità, somiglianza, `batch_size` 1-4 | No |
| Eleven v4 Turbo | una voce sola | come sopra | No |
| Qwen Audio 3.0 TTS Flash (`qwen_audio_tts`) | voce da testo con istruzione di emozione/stile; lingue incluso **it** | velocità 0,5-2, tono, volume, seed, `batch_size` | No |
| Text to Speech V2 (`text2speech_v2`) | motore a scelta: elevenlabs, minimax, seed_speech, vibe_voice, cozy_voice; ha unlimited | voce preset o elemento | Probabile ("Voiceover" 0,3 crediti: non dichiara il motore) |
| Inworld TTS, Sonilo Music, Mirelo Text to Audio | voce, musica, effetti sonori | durata | No; marcati "solo pipeline giochi" |
| Voice Element (clonazione voce) | crea una voce clonata | n.d. | Sì (40 crediti, una tantum) |

## 5. 3D (V, nessuno provato, probabilmente fuori dai nostri servizi)

SAM 3 3D Objects (immagine verso mesh), SAM 3 3D Body, Meshy (image-to-3D, multi-image, Meshy 6 testo, Meshy 7 immagine, rigging, remesh, retexture), Tripo (testo, immagine, multivista), Hunyuan3D (v3 immagine, v3.1 testo). Output GLB, PBR, rigging e animazioni opzionali. **I (non verificato)**: utile solo per mockup 3D di packaging o oggetti; non serve ai servizi UGC/spot/ads attuali.

## 6. Costi VERIFICATI dallo storico crediti

Fonte: `transactions` (tutte le pagine). "Osservato" = importo in `transactions`. "Abbinamento" = a quale risoluzione/durata corrisponde (ricavato, vedi sezione 0).

### 6a. Video

| Modello | Importo osservato (crediti) | Quante volte | Abbinamento a risoluzione e durata | Grado di certezza |
|---|---|---|---|---|
| Seedance 2.5 | 12 | 1 (24/9) | 4 s a 480p (3/s) | ricavato (I) |
| Seedance 2.5 | 28 | 4 (24/9) | 4 s a 720p (7/s) | ricavato (I) |
| Seedance 2.5 | 30 | 1 (5/10) | 10 s a 480p | V (`30`) |
| Seedance 2.5 | 35 | 4 (24/9) | 5 s a 720p | ricavato (I) |
| Seedance 2.5 | 42 | 6 (24/9 e 1/10) | 14 s a 480p (bozza) | V (`30`); 6 s a 720p darebbe lo stesso importo |
| Seedance 2.5 | 56 | molte (24/9, 2/10; conteggi di questa tabella indicativi) | 8 s a 720p | V (`30`) |
| Seedance 2.5 | 70 | 5 (23/9) | 10 s a 720p | V (`19`) |
| Seedance 2.5 | 98 | 1 (23/9) | 14 s a 720p | ricavato (I) |
| Seedance 2.5 | 112 | 1 (29/9) | 16 s a 720p | V (`30`) |
| Seedance 2.5 | 168 | 1 (1/10) | 14 s a 1080p, finalizzazione di una bozza da 42 | V (`30`) |
| Seedance 2.5 | 180 | 2 (21/9, 22/9) | 15 s a 1080p (12/s) | V: `00-STATO` riporta 191,6 totali con circa 12 di immagini |
| Seedance 2.5 | rimborsi di 56 | 2 (2/10) | job falliti | V (rimborso automatico) |
| Cinema Studio 4.0 | 12 | 1 (5/10) | 4 s a 480p | ricavato (I); conteggi indicativi |
| Cinema Studio 4.0 | 36 | 1 (5/10) | 12 s a 480p | V (`30`) |
| Cinema Studio 4.0 | 45 | 1 (5/10) | 15 s a 480p | ricavato (I) |
| Cinema Studio 4.0 | 48 | 8 (18/9, 5/10) | 4 s a 1080p oppure 16 s a 480p | ambiguo (I) |
| Cinema Studio 4.0 | 60 | 10 (18/9, 5/10) | 5 s a 1080p | V (`30`) |
| Cinema Studio 4.0 | 72 | 4 (17-18/9) | 6 s a 1080p | ricavato (I) |
| Cinema Studio 4.0 | 96 | 1 (18/9) | 8 s a 1080p | ricavato (I) |
| Cinema Studio 4.0 | 108 | 3 (18-19/9) | 9 s a 1080p | ricavato (I) |
| Cinema Studio 4.0 | 135 | 1 (17/9) | non spiegato da 3/7/12 al secondo con durate intere | non decifrato (I): potrebbe essere un'altra modalità (estensione o modifica) o un moltiplicatore diverso |
| Kling v3.0 | 7,5 | 5 (22/9) | tentativi std da 5 s, ma non si sa se con audio | non decifrato (I) |
| Kling v3.0 | 8,75 | 2 (5/10) | std, 5 s | V (`30`) |
| Kling v3.0 | 10 | 1 (22/9) | n.d. | non decifrato (I) |
| Kling v3.0 | 20 | 1 (22/9) | std, 10 s | V (`19`) |
| Kling v3.0 | 30 | 3 (23/9) | std 15 s oppure altra modalità | non decifrato (I) |
| Marketing Studio Video | 30,65 / 36,59 / 42,53 / 66,29 / 72,23 / 90,05 | 1 / 2 / 1 / 2 / 1 / 2 (15-17/9) | non registrato; i passi tra 30,65, 36,59, 42,53 e tra 66,29 e 72,23 sono di 5,94 | non decifrato (I) |
| Marketing Studio Video | 105,15 | 4 (17/9) | 15 s a 720p (Meridian) | V (`30`) |
| Marketing Studio Video | 139,5 | 1 (17/9) | n.d. | non decifrato (I) |
| Marketing Studio Video | 208,2 | 1 (28/9) | 30 s a 720p (Sienna Niacinamide) | V (`30`) |
| Topaz Video | 3 / 5 / 3 | 5/10 | upscale a 1080p di clip brevi (4 s e 15 s) | V (`30`: 3 per 4 s, 5 per 15 s); tariffa a clip, non lineare |
| Voice Change | 2 e 4 | 29/9 e 28/9 | n.d. | osservato, mapping n.d. |
| Genjutsu Motion Transfer | 0 | 26/9 | n.d. | osservato (probabile promozione o unlimited, I) |

Tariffe al secondo per Seedance 2.5 e Cinema Studio 4.0 (V, `19`, `30` e dati sopra): **480p = 3, 720p = 7, 1080p = 12 crediti/s**. Cinema Studio 4.0 a 720p non risulta mai nello storico: la riga "720p 28 per 4 s" di `30` per Cinema Studio non trova riscontro (28 compare solo come Seedance 2.5, 24/9): da correggere o verificare. Nessun costo osservato per 4k, `bitrate_mode: high`, estensioni, modifiche video o `video_extension`.

### 6b. Immagini e altro

| Modello | Importo osservato (crediti) | Note |
|---|---|---|
| Nano Banana Pro | 2 (centinaia di volte); 4 una volta (27/9); 0 in alcune generazioni (17/9, 22/9: unlimited dal sito) | impostazione di default 2k (schema); il 4 è probabilmente 4k o due immagini (I) |
| Nano Banana 2 | 1,5 (24/9, default 1k); 2 (1/10) | il 2 è probabilmente 2k (I) |
| GPT Image 2.0 | 6,5 (molte); 0,5 (24/9, 25/9); 0 (24/9 "GPT Image") | 6,5 = qualità alta (I); 0 = unlimited |
| GPT Image 2.5 Flare | 0,25 / 1 / 2,75 / 3 / 4,25 | qualità e risoluzione non registrate; probabile scala low / medium / high a 1k-2k (I); 2,75 è il prezzo dominante (storyboard, 1-5/10); 4,25 per lotti da 24 (1/10) |
| Seedream 5.0 Pro | 2,5 (23/9, 4 volte); 3 (21-22/9, 3 volte) | pulizia anti-"effetto AI" |
| Higgsfield Soul V2 | 0,12 (comune), 0,14 (2 volte), 0 (molte, free gens) | |
| Marketing Studio Image | 2 (21/9, 1/10), 1,5 (16/9) | |
| Outpaint | 2 (3/10) | |
| Soul ID (addestramento) | 25 (26/9, 1/10, 2/10) | 3 addestramenti |
| Voice Element (clonazione) | 40 (28/9) | una tantum |
| Seed Audio 1.0 | 1,1 (1/10), 0,7 (16/9) | per battuta o richiesta (I) |
| Voiceover | 0,3 (16/9, 29/9 x2) | |
| Rimborsi | automatici sui job falliti (Nano Banana Pro/2, GPT Image 2.5, Seedance 2.5, Soul V2) | V |

Costi mai osservati (non stimabili da qui): tutti gli altri modelli dell'elenco 2b e 3, e `get_cost` non è usabile. FLUX 3 Video Edit dichiara 1 credito/s (V, schema). Wan 3.0 "durata -1" è fatturato come 10 s (V, schema).

## 7. Preset e app (sola lettura)

### 7a. Preset Viral (`get_presets source: viral`, categoria unica `effects`, 87 in totale; letti 48)

Sono effetti virali "da chain" (immagine verso video). Il parametro `category` per Viral accetta solo `effects` (V, messaggio di errore dello strumento: product-shot e motion valgono solo per Marketing Studio).

| Preset | Descrizione dichiarata | Utilità per noi |
|---|---|---|
| Floating fall | caduta all'indietro mentre gli oggetti fluttuano, camera su dettagli di prodotto | ads prodotto giocosi (I) |
| Smash and grab | prodotto inquadrato dal finestrino, soggetto rompe il vetro e lo afferra | ads d'azione (I) |
| Lacewalker | miniatura che cammina tra borse giganti | moda e borse (I) |
| Scrapbook collage, Studio slide | layout multipannello e copie in 3D | lookbook e moda (I) |
| Wild ride | orbita di camera ad alta velocità | auto, musica (I) |
| Bullet time | tempo congelato con giro a 360 gradi | hook d'impatto (I) |
| Earth zoom, High flip, Eyes in, Cutout | transizioni di scena | transizioni (I) |
| Vanish, Clones, Infinite clones, Selfception, Melting, Act natural, Frozen in motion, Stop world | effetti surreali | hook comici; poco adatti a lusso (I) |
| Fallen angel, Cyclope, Pearl earring, Argus (split screen su quadri famosi) | formato "ricostruzione di un'opera" | contenuti social, non servizi (I) |
| Comic, Canvas, Palette, Particles, Cold vision, Windows, Tracking, LSD, Ink Riot | stili mixed-media | stile grafico (I) |
| Monster dab, Street colossus, World morphing, Architecture wave, Burning man, Pigeons, Superstar, Moonwalk, Knight's diary, Fairytale castle, Mighty fighter, Blue depth, Agamemnon, boarding pass, Lidar transition, Incline | fantasia, giganti, viaggi | non rilevanti per prodotto (I) |

Costo dei preset: **non verificato** (`execute_preset` vietato; non compaiono "Preset" nello storico).

### 7b. Preset Marketing Studio (`source: marketing_studio`, 649 totali = 418 product-shot + 231 motion; letti i primi 12 di ogni categoria)

| Tipo (campo `type`) | Cosa è | Esempi letti | Utilità per noi |
|---|---|---|---|
| `product_shots` | foto prodotto in stile | Ice Cube Hover, Linen Lid Lift, Off Kilter, Pistachio Void, Buried in Ice, Slanted Shelf Duo | foto e carousel e-commerce (I) |
| `product_shots_people` | prodotto con persona | Chilled Can, Brushed Tin, Golden Dew, Emerald Pajamas, Sky High Chili, Blue Sky Cap | ads con persona; attenzione alla coerenza del volto (I) |
| `hypermotion` | video motion di prodotto | Monospace Callouts, Wheatpaste Wall, Green Tea Macro | video prodotto senza persona (I) |
| `mixed_media` | collage in movimento | Pixel Block Yard, 90s Bedroom CRT, Halftone Street Collage | contenuti social di tendenza (I) |
| `2d_motion` | motion grafico 2D | Pastel Shape Choreography, Retro Starburst Orbit, Storybook Page Turns | spiegazioni e brand (I) |
| `saas_motion` | motion da URL di prodotto SaaS | Echo Wave, Ink & Ribbon, Vibrant Carousel | clienti software, non e-commerce (I) |
| formati immagine aggiuntivi dello schema | `poster`, `ads`, `marketplace` | non elencati nei preset letti | locandine, annunci, schede marketplace (I) |

### 7c. App (`apps_search`, `apps_describe`)

Una sola app nel marketplace: ricerche con "product ad ugc video", "product", "ad", "image", "edit", "photo" vuote; con "video" e con query vuota: 1 risultato (V).

**Match Cut + Tracelab** (`3a69aa1d-8456-4705-92b5-b0616b03e642`, manifest v3): tutte le azioni sono render video asincroni in mp4. Utili per i servizi: `create_productcut` (ritaglia un prodotto e lo anima tra scene di sfondo), `create_logocut` (logo su sfondi di brand), `create_commentcut` (parole e reazioni come commenti social), `create_typewriter`, `create_notebook`, `create_notereel`, `create_wordstack`, `create_scrapboard`, `create_stickercut`, `create_spherecut`, `create_lenscut`, `create_searchcut`, `create_facecut` (match cut di volti), `create_tracelab` (tracciamento oggetti). Effetti filtro su immagine: CRT, glitch, VHS, thermal (4 palette), night vision, Nokia. Costo e qualità **non verificati**. Rischio per i nostri standard: sono grafiche di tendenza, non adatte a spot di lusso né a "UGC credibile" (I).

## 8. Cosa scegliere per cosa (PROPOSTA, I salvo dove indicato V; la decide Massimiliano)

| Esigenza | Candidati | Fondamento | Stato |
|---|---|---|---|
| Spot di marca / lusso, 21:9 o 16:9, camera controllata | Cinema Studio 4.0; alternativa Seedance 2.5 | stessa tariffa (V); Cinema 4.0 ha controlli camera, ottica, apertura, luce, palette, epoca, ritmo; Cinema 3.5 offre `camera_style` / `light_scheme` / `color_grading` | I per la qualità relativa: serve prova affiancata (già prevista da `PROCEDURE.md`). 3.5 mai provato |
| Spot lunghi con stessa persona | Cinema 4.0 `video_extension` (V in `PROCEDURE.md`); Seedance 2.5 `video_extension` | modalità nello schema | I per Seedance |
| UGC con creator che parla (nucleo del business) | Marketing Studio Video; workflow `ugc-video` con Seedance 2.5 (`31`) | V in `30` e `31` | Marketing Studio v2 `ugc_v2` e `reference2video` non provati |
| Clip economiche di test (parlato, un piano) | Kling v3.0 (V: 8,75 per 5 s std) ; Kling 3.0 Turbo, Seedance 2.0 Mini, Grok 1.5 Lite, Veo 3.1 Lite, MiniMax H3 Max | prezzo basso dichiarato ("budget", "fast") | Solo Kling provato; gli altri I |
| Qualità facciale e fisica del volto | Veo 3.1 (ultra), Minimax Hailuo ("emozione del volto"), Gemini Omni Flash 1.1 | solo descrizioni dei modelli | I: da provare, mai testati |
| Video con clip fino a 30 s in una chiamata | Seedance 2.5, Cinema 4.0, Wan 3.0 | durata massima (V) | Wan 3.0 non provato |
| Cambiare solo un elemento di un video esistente | Seedance 2.5 `video_edit`, Kling Omni Edit, FLUX 3 Video Edit (1 credito/s), Gemini Omni 1.1 `edit`, Genjutsu (sostituzione oggetto) | schemi | I qualità; FLUX Edit economico (V) |
| Ricreare un annuncio esistente con il nostro personaggio | Marketing Studio Reference Video; `ad_reference_id` del Marketing Studio v1 | schemi | Non provato; attenzione ai diritti sul video originale |
| Bozza economica e poi alta qualità | Seedance 2.5 `draft` 480p poi 1080p nativo (finalizzazione 168 per 14 s, V); Cinema 4.0 480p poi Topaz (V in `PROCEDURE.md`) | V | Confronto qualità Topaz contro nativo: I |
| Lipsync / voce | voce nativa Seedance (`31`); Sync Lipsync 3; Voice Change; Dubbing `ita` | schemi | Sync e Dubbing non provati |
| Immagine personaggio e ritratti realistici | Soul V2 (0,12 crediti, V); Nano Banana Pro con riferimenti (2 crediti, V) | storico | già in uso |
| Storyboard in tavola (GPT Image) | GPT Image 2.5 Flare (2,75 per immagine, V) | storico e `31` | già in uso |
| Pulizia anti-"effetto AI" | Seedream 5.0 Pro (2,5-3 crediti, V) | storico e `31` | già in uso |
| Testi leggibili su grafiche, etichette, packshot | OpenAI Hazel, Ideogram 4.5, Recraft V4.1 utility, GPT Image 2.5 | descrizioni dei modelli ("miglior testo", "tipografia") | I: nessuno provato; `19` segnala il limite di Nano Banana Pro sul testo piccolo |
| Foto prodotto per e-commerce | Marketing Studio Product Shot (`product_shots`, `marketplace`), preset product-shot, Recraft utility | schemi | I: non provati; prodotto reale = solo foto ufficiali (`ERRORI.md` n. 5) |
| Carousel formato 4:5 | Nano Banana Pro, GPT Image 2.5, FLUX 3 Image, Cinema Image 2.5, Ideogram 4.5 | solo questi supportano 4:5 (V) | I qualità |
| Upscale foto | Topaz Image, Bytedance Image Upscale (2k, 4k) | schemi | Non provati; costo n.d. |
| Grafiche di tendenza (parole, glitch, CRT) | app Match Cut + Tracelab | elenco azioni | I: non per lusso |

## 9. Novità o modelli non ancora provati da noi (segnalazione)

Provati (V, nello storico): Seedance 2.5, Cinema Studio 4.0, Kling v3.0, Marketing Studio Video (v1), Marketing Studio Image, Nano Banana Pro e 2, GPT Image 2.0 e 2.5 Flare, Seedream 5.0 Pro, Soul V2, Soul ID, Outpaint, Topaz Video, Seed Audio, Voiceover, Voice Change, Voice Element, Genjutsu motion transfer.

**Più interessanti da provare, in ordine di rilevanza per i nostri servizi (I):**
1. **Cinema Studio Video 3.5** (nuovo): multi-shot fino a 6 inquadrature, controlli camera/luce/colore. Attenzione: `prompt_language` di default cinese.
2. **Marketing Studio v2** (`ugc_v2`, `reference2video`, `product_shots`, `marketplace`): evoluzione del formato UGC, direttamente sul nostro nucleo di servizio.
3. **Wan 3.0 / Prime** (fino a 30 s, 1080p, audio nativo, riferimenti), **FLUX 3 Video** (20 s, continuazione) e **Gemini Omni Flash 1.1** (fino a 4k): concorrenti di Seedance 2.5 sulla stessa categoria "riferimenti più audio".
4. **Veo 3.1** (qualità ultra, ma solo immagine iniziale e 8 s al massimo) e **Minimax Hailuo** (volti).
5. **Kling 3.0 Turbo**, **Seedance 2.0 Mini**, **Grok 1.5 Lite**: opzioni a basso costo per hook di test.
6. **Recraft V4.1 (utility)**, **Ideogram 4.5**, **OpenAI Hazel**: testo ed etichette.
7. **Seedance 2.5 `video_edit`** e **FLUX 3 Video Edit** (1 credito/s): correggere un clip senza rigenerarlo (rilevante per `ERRORI.md`: difetti puntuali).

**Non provati e senza interesse immediato:** modelli 3D, Clipify, Depth Anything, AutoSprite, Soul Cast, modelli legacy (Cinema Studio v1/v2, Kling 2.6, Veo 3, Grok Video, Wan 2.6, Seedance 1.5).

## 10. Anomalie e cose da verificare

- `30` riporta "Cinema Studio 4.0, 720p: 28 per 4 s": nello storico quel 28 è Seedance 2.5. Da correggere o confermare con un nuovo dato.
- Kling v3.0: stesso tipo di tentativo (std, 5 s) a 7,5 il 22/9 e a 8,75 il 5/10: possibile variazione di listino (I) o differenza di audio acceso.
- Cinema Studio 4.0 a 135 crediti (17/9): non coerente con 3/7/12 al secondo con durate intere.
- Il Marketing Studio v1 dichiara 12-15 s, ma c'è stato un video da 30 s (208,2): la durata dello schema potrebbe non essere vincolante, o il video è stato prodotto con la v2.
- Il preset Viral non ha categorie `product-shot` e `motion`: solo `effects`.
- Offerte unlimited in scadenza il 6/10 (V): Nano Banana Pro e Nano Banana 2 (7 giorni) e Kling 3.0 720p/5s (7 giorni); Seedream 5.0 Lite, Seedream 4.5, FLUX.2 Pro 1K, Nano Banana, Kling O1 Image e GPT Image (365 giorni): valutare se servono prima di acquistare. Valide solo sul sito, non da strumento (`19`).
- Dati mancanti che richiederebbero un test o un consenso: costi di tutti i modelli non provati; risoluzione e durata esatta delle righe "ambiguo" della sezione 6.
