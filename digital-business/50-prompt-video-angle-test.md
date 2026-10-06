# 50 — Prompt video "Angle Test" MERIDIAN (Seedance 2.5) — SCRITTI, NON GENERATI (6/10/2026)

Nessun video generato. I prompt sotto sono pronti da usare solo dopo il "sì" di Massimiliano.
Fonti delle regole: workflow Higgsfield `ugc-video`, formato `review` (presentatrice/demo; non `tutorial`, che richiede le scritte "Step N" sul video), `references/ugc-board.md`, `references/boards.md`, `references/ugc-clip.md`; brief `48` (§7 copioni, §8 scheda voce aggiornata, §14 risoluzione 720p).

## 1. Tavole pulite (riferimento per i video)

| Clip | Tavola grezza (GPT Image 2) | Tavola pulita (Seedream 5 Pro) da usare | File locale |
|---|---|---|---|
| A dimostrazione | job `29649141-7381-4009-9ad7-9c56a1efd58f` | **job `543341f7-6da4-4245-8787-efcdd56f50f5`** | `scratchpad/angle/boardA.png`, `boardA_clean.png` |
| B texture | job `e483ff80-81aa-4f57-9564-b4184543f63f` | **media `ddab0f5c-adb0-4b64-b8a8-68841ce66683`** (= pulizia job `0e26c7d3-351b-4be8-bca8-57716d011603` con le didascalie finte "Step N." coperte di bianco; nessuna generazione) | `boardB.png`, `boardB_clean.png` (senza scritte), `boardB_clean_con_scritte.png` |
| C routine | job `3dc13dd2-5098-4313-98b6-52d4d19e62dc` | **job `cf8aa65b-d28f-4559-9530-94d8c35b969b`** | `boardC.png`, `boardC_clean.png` |

Scartati: job `5b9b2a4a-…` (tavola A bloccata dal filtro, falso positivo, rimborsata); job `e06a72fc-…` (seconda pulizia A: scritta ancora storpiata + didascalie finte "Step 1–6").

Riferimenti fissi in ogni video: casting `7cf0287b-13a7-4025-9723-78e8a845b3d3`, prodotto `d899ee6e-fb91-4d33-afad-48ff95efd116`.

## 2. Controllo pannello per pannello (fatto da Claude sulle immagini scaricate)

Regole verificate: volto = casting, maglia avena a collo alto, molletta tartarugata, nessun gioiello, nessun sorriso, max 2 mani e anatomia, un solo stick, scritta MERIDIAN, niente specchi/persone/telefoni/testi finti/barre nere, 8 pannelli in una riga.

**Note generali (tutte e 3 le tavole):** 8 pannelli in una riga, sì. I pannelli sono più stretti di 9:16 (circa 1:2,5) con margini bianchi sopra e sotto: è un limite geometrico (8 pannelli 9:16 non entrano in un foglio 21:9), non sono barre nere. Volto coerente con il casting in tutti i pannelli con viso; espressione neutra ovunque, nessun sorriso; nessuno specchio, nessuna altra persona, nessun telefono visibile. **La pulizia Seedream peggiora la scritta piccola** (lettere confuse): nei prompt video la scritta è sempre legata all'immagine prodotto.

**Tavola A (pulita `543341f7`)**
1. Statica, mezzo primo piano, ruota la base con due mani: OK. Scritta storpiata dalla pulizia ("MERIDOAN").
2. Selfie, primo piano stretto, stick sullo zigomo: OK; scritta ruotata di 90° (stick tenuto di lato, coerente col gesto) e poco leggibile.
3. Statica, a figura intera fino alla vita, accanto alla finestra: OK. Sullo scaffale c'è una pila di asciugamani invece di uno solo (difetto minore).
4. Macro: **difetto** — lo stick è sulla punta del naso, vicino alle labbra, e sembra un burrocacao. Nel prompt video il gesto è corretto in "down the bridge of the nose, then along the chin, away from the lips".
5. Selfie, stick sul mento: OK; scritta storpiata dalla pulizia.
6. Statica, tre quarti, picchietta lo zigomo, stick nell'altra mano: OK; scritta piccola storpiata.
7. Macro, polpastrelli sullo zigomo, niente prodotto: OK.
8. Selfie, stick accanto alla guancia, bocca chiusa: OK; scritta storpiata dalla pulizia.

**Tavola B (pulita, media `ddab0f5c`)**
1. Macro, stick sul dorso della mano: OK, scritta fuori campo.
2. Selfie, stick accanto al viso: OK, MERIDIAN leggibile (prima lettera un po' sbiadita).
3. Statica, fino alla vita, mano verso la finestra: **piccolo orecchino a bottone visibile** (gioiello non previsto): nel prompt video "no earrings, plain earlobes".
4. Macro, dito che stende lo swatch: OK.
5. Selfie, stick sullo zigomo: OK.
6. Statica, di profilo verso la finestra: OK; scritta minuscola storpiata.
7. Primo piano del prodotto: OK, MERIDIAN nitida e corretta.
8. Selfie, polpastrelli sullo zigomo, bocca chiusa: OK.
La pulizia aveva aggiunto le didascalie "Step 1.–Step 6." sopra i pannelli: coperte di bianco in locale (stesso sfondo), contenuto dei pannelli intatto.

**Tavola C (pulita `cf8aa65b`)**
1. Statica, tampona il viso con un solo asciugamano, due mani: OK.
2. Statica, posa l'asciugamano sul davanzale: OK.
3. Macro, toglie il tappo (tappo in una mano, stick nell'altra): OK, MERIDIAN corretta.
4. Statica, ruota la base: OK; scritta leggermente storpiata dalla pulizia.
5. Selfie, stick sullo zigomo: OK.
6. Statica, stick sulla fronte: OK; sullo scaffale in basso di nuovo due asciugamani piegati (minore).
7. Macro, stick sulla mandibola sotto l'orecchio, lontano dalle labbra: OK, nessun orecchino.
8. Selfie, stick accanto al viso, bocca chiusa: OK, MERIDIAN corretta.

## 3. Crediti spesi (da `transactions`)

Saldo prima 332,91 → dopo **303,41** = **29,5 crediti**.
- GPT Image 2 (2k, high): 6,5 a tavola × 3 = 19,5 (la tavola bloccata è stata rimborsata: 0).
- Seedream 5 Pro pulizia: 2,5 a passaggio × 4 = 10 (una pulizia A rifatta perché la prima aveva rovinato la scritta; la seconda è risultata peggiore ed è scartata).
- Generazioni di immagini usate: 8 su 10 (compresa quella bloccata).

## 4. Impostazioni comuni dei 3 video (da NON lanciare senza il sì)

```
model: seedance_2_5 · mode: omni_reference · generate_audio: true
aspect_ratio: 9:16 · resolution: 720p (nativo, brief §14) · duration: 12 · count: 1
medias (in quest'ordine): [tavola pulita della clip, role image] + [casting 7cf0287b-13a7-4025-9723-78e8a845b3d3, role image] + [prodotto d899ee6e-fb91-4d33-afad-48ff95efd116, role image]
audio di riferimento: clip A = nessuno (voce nativa dalla scheda); clip B e C = 5-10 s della voce della clip A approvata, segnaposto: <AUDIO_DA_CLIP_A_media_id> (role secondo lo schema di seedance_2_5, da verificare con models_explore prima)
```

Registro: calmo, misurato (brief: espressione neutra, nessun sorriso). Per le regole di `ugc-clip.md` questo significa: niente frase di "energia" nel Narrative Summary, niente suoni tra parentesi all'inizio, niente momento buffo; resta un solo piccolo momento spontaneo per clip e un momento a bocca chiusa. Tagli netti ovunque (il Pick-Up finale non è applicabile: l'ultimo taglio dura 1,5 s, meno dei 3 s richiesti).

Persona e "Come parla" (brief §8) sono inseriti integralmente in ogni prompt. Emozione per battuta: indicata dentro ogni taglio e riassunta qui.

| Clip | Battuta | Emozione |
|---|---|---|
| A | "Twist it up." | pratica, gentile, mentre lo fa |
| A | "Swipe once across the cheekbone." | concentrata, più lenta |
| A | "Down the nose, over the chin." | leggera, scorrevole |
| A | "Then pat it in." | più morbida, chiude; poi bocca chiusa |
| B | "Look at the texture." | sommessa, invita a guardare da vicino |
| B | "It glides, no tugging." | osservazione calma, piccola pausa dopo "glides" |
| B | "Clear on the skin, a soft sheen." | apprezzamento misurato |
| B | "Meridian, the balm stick." | semplice, come dire il nome a un'amica, nessun tono da annunciatore |
| C | "Morning, before makeup." | rilassata, un po' assonnata |
| C | "Pat dry, uncap, twist up." | ritmica, un verbo per battito |
| C | "Cheekbones first, then everywhere that feels dry." | pratica, tranquilla |
| C | "Done." | breve, morbida, in discesa |

## 5. Prompt clip A — dimostrazione

medias: `543341f7-6da4-4245-8787-efcdd56f50f5` (tavola A pulita), `7cf0287b-13a7-4025-9723-78e8a845b3d3`, `d899ee6e-fb91-4d33-afad-48ff95efd116`. Nessun audio di riferimento.

```
Style & Mood: UGC iPhone aesthetic, soft neutral morning daylight from a window on the left in a bright white-tiled washroom, MIXED: starts with a locked-off static camera, then hard-cuts between front-facing selfie handheld beats and locked-off static beats — POV alternates per cut across the eight beats, social media vertical format, native 720p.

Narrative Summary: A warm, easy-going presenter with a relaxed, slightly low voice, speaking at a calm conversational pace with a gentle melody, genuine and never salesy — she speaks and moves exactly like that. In one calm 12-second product demonstration she twists the MERIDIAN balm stick up, swipes it once across the cheekbone, down the bridge of the nose and along the chin, then pats it in and ends with a closed-mouth look into the lens; her expression stays neutral, relaxed and focused throughout, never smiling.

Dynamic Description:
Cut 1 (0-1.5s) — MEDIUM CLOSE-UP, static camera: the twist is already happening in frame one — her left hand holds the cream tube upright at chest height with the MERIDIAN wordmark facing the lens, her right fingertips turn the base and the translucent dome visibly climbs out of the tube; her eyes stay down on the stick, a slow breath out through the nose, shoulders soft; lips move on the first words at once, practical and gentle. Hard cut to.
Cut 2 (1.5-3s) — TIGHT CLOSE-UP, selfie: her left arm extends toward the lens off-frame, her right hand brings the dome to her right cheekbone and draws one slow, even stroke outward toward the temple; her gaze follows the stroke with half-lowered lids, her brow relaxes, a curl at the temple stirs as her head tilts a few degrees; her voice slows, concentrated. Hard cut to.
Cut 3 (3-4.5s) — WAIST-UP WIDE, static camera: she stands beside the window, right hand lowering the stick to her waist with the wordmark toward the lens, left arm resting at her side; she turns her head toward the daylight and the fresh sheen on her cheekbone catches the light; weight settles onto one hip; a brief recovered eye-flick back toward the lens as she finds the next words. Hard cut to.
Cut 4 (4.5-6s) — MACRO, static camera: the dome glides in one continuous stroke down the bridge of the nose from between the brows toward the tip, held by her right fingers, well above and away from the lips; a thin clear sheen follows the stroke, pores and fine texture sharp; her left hand stays out of frame; light, flowing delivery. Hard cut to.
Cut 5 (6-7.5s) — MEDIUM CLOSE-UP, selfie: her left arm extends toward the lens off-frame, her right hand sweeps the stick once along the chin line from one side to the other, chin lifting slightly into the stroke, never touching the lips; her eyes come up to the lens mid-stroke, calm and direct; the high neck of the oat sweater shifts with the movement. Hard cut to.
Cut 6 (7.5-9s) — THREE-QUARTER WIDE, static camera: standing at the tiled wall near the window, her right fingertips press-and-lift lightly on the cheekbone, her left hand holds the stick lowered at her waist with the wordmark facing the lens; her head tilts a little, eyes soft and downcast; her voice turns softer, closing the steps. Hard cut to.
Cut 7 (9-10.5s) — MACRO, static camera: close on her right fingertips pressing the balm into the cheekbone, short natural nails, the sheen sinking in; no product in frame, left hand out of frame; lips together, no voice — the quiet beat, only room tone and the faint touch of fingertips. Hard cut to.
Cut 8 (10.5-12s) — MEDIUM CLOSE-UP, selfie: her left arm extends toward the lens off-frame, her right hand raises the stick upright beside her cheek, wordmark facing the lens; lips stay closed, a slow blink, then a calm neutral gaze straight into the lens; the clip ends mid-motion as the stick settles beside her face.

Static Description: A bright washroom of matte white square tiles, one window on the left giving soft neutral daylight, one folded plain white towel on a white shelf and nothing else; no mirror, no reflective surface, no other products. She wears a fully covered, high-neck oat ribbed knit sweater with long sleeves, dark natural curls gathered up with a tortoiseshell claw clip on top of the head, no jewelry and plain earlobes, no makeup, short natural nails — identical to the character reference in every cut. The product is exactly one cream MERIDIAN balm stick, about 9 cm tall and 3 cm wide, palm-sized, uncapped for the whole clip, no cap anywhere; its wordmark is identical to the product reference image — MERIDIAN in thin serif capitals, horizontal, upright, reading left to right, never mirrored, never rotated to face away, never re-lettered.

Audio: She speaks to camera with a natural neutral American accent — a warm, relaxed, slightly low adult woman's voice — iPhone microphone audio with natural quiet room tone, close phone-mic sound, no music. How she talks: Talks to one friend standing next to her, not to an audience or a camera crew. Adult woman's voice, mid-low register, soft but clear; natural American English, neutral accent; uses contractions. Calm pace, about two and a half words per second; tiny natural pauses between steps; a soft breath before the first line. Sentences end with a gentle falling intonation: no upspeak, no announcer lift, no TV-ad energy. Steady volume, close phone-mic sound, quiet bathroom room tone; no music. Speaks only the script words: no added fillers, no laughter, no giggle, no "mm-hmm". Avoid: excitement, hype, whispering ASMR, exaggerated vocal fry, robotic flatness, rushing. Lines, in order, with emotion: Cut 1 (practical, gentle, while doing it): "Twist it up." Cuts 2-3 (focused, slower): "Swipe once across the cheekbone." Cuts 4-5 (light, flowing): "Down the nose, over the chin." Cut 6 (softer, closing): "Then pat it in." Cuts 7-8: silence, lips closed.

Facial features clear and undistorted, consistent clothing throughout, neutral relaxed expression in every cut, no smile, no grin, no laugh. Shot on iPhone, natural lighting, social media aesthetic, handheld micro-shake during selfie cuts, locked-off frozen frame during static-camera cuts. No on-screen text, no subtitles, no captions, no watermarks, no legible text on any object except the product's own MERIDIAN wordmark exactly as in the product reference image, no real brand logos anywhere, no cinematic grade, no film grain, no bokeh, no lens flare, no fisheye lens, no ultra-wide distortion, no slow motion, no beauty filter, no mirror, no reflection, no phone visible, no other people, no jewelry, no earrings, exactly one stick, no cap, no third arm, no extra hands, no duplicated limbs, no deformed hands.
```

## 6. Prompt clip B — texture

medias: `ddab0f5c-adb0-4b64-b8a8-68841ce66683` (tavola B pulita senza scritte), `7cf0287b-13a7-4025-9723-78e8a845b3d3`, `d899ee6e-fb91-4d33-afad-48ff95efd116` + audio di riferimento `<AUDIO_DA_CLIP_A_media_id>` (5-10 s della voce di A approvata).

```
Style & Mood: UGC iPhone aesthetic, soft neutral daylight from a window on the left in a bright white-tiled washroom, MIXED: starts with a locked-off static macro, then hard-cuts between front-facing selfie handheld beats and locked-off static beats — POV alternates per cut across the eight beats, social media vertical format, native 720p.

Narrative Summary: A warm, easy-going presenter with a relaxed, slightly low voice, speaking at a calm conversational pace with a gentle melody, genuine and never salesy — she speaks and moves exactly like that. In one calm 12-second close look at the balm texture she draws the MERIDIAN stick across the back of her hand, shows the clear trail in the window light, spreads it with a fingertip, passes it over her cheekbone and names the product simply, like telling a friend; her expression stays neutral and attentive, never smiling.

Dynamic Description:
Cut 1 (0-1.5s) — MACRO, static camera: the stroke is already moving in frame one — the translucent dome glides across the back of her left hand, which rests flat on the white shelf, her right fingers holding the stick near the dome so the printed part of the tube stays out of frame; a thin clear glossy trail appears behind the dome; her voice starts at once, hushed, inviting a closer look. Hard cut to.
Cut 2 (1.5-3s) — MEDIUM CLOSE-UP, selfie: her left arm extends toward the lens off-frame, her right hand lifts the stick upright beside her chin with the MERIDIAN wordmark facing the lens; her eyes rise to the lens, brows level and attentive, a small head tilt; calm observation in her voice. Hard cut to.
Cut 3 (3-4.5s) — WAIST-UP WIDE, static camera: by the window she raises her left hand into the daylight and slowly angles the back of it so the trail catches the light, her right hand holds the stick at her waist with her fingers wrapped around the printed part; her gaze stays on her hand, a short pause after "glides", then the rest of the line. Hard cut to.
Cut 4 (4.5-6s) — MACRO, static camera: her right index fingertip spreads the clear swatch on the back of her left hand in one smooth circle, the balm turning almost invisible with a soft sheen, short natural nails, no product in frame; her voice measured, quietly appreciative. Hard cut to.
Cut 5 (6-7.5s) — MEDIUM CLOSE-UP, selfie: her left arm extends toward the lens off-frame, her right hand draws the dome once across her right cheekbone, holding the tube low so her fingers cover the printed part; lids half-lowered, then a recovered glance back to the lens as she finds the next words. Hard cut to.
Cut 6 (7.5-9s) — THREE-QUARTER WIDE, static camera: she stands in near profile facing the window, the sheen on her cheekbone catching the daylight; her right hand holds the stick at chest height with her fingers around the printed part, left arm resting at her side; lips together, no voice — the quiet beat, a slow breath in through the nose. Hard cut to.
Cut 7 (9-10.5s) — TIGHT CLOSE-UP product shot, static camera: her right hand brings the stick upright toward the lens at chest height and holds it still, the MERIDIAN wordmark large, frontal, centered and sharp, identical to the product reference image, the translucent dome on top, the oat sweater softly behind; her voice simple and plain as she says the name, no announcer tone. Hard cut to.
Cut 8 (10.5-12s) — MEDIUM CLOSE-UP, selfie: her left arm extends toward the lens off-frame, the fingertips of her right hand rest lightly on her cheekbone, no product in frame; the last words land softly, then lips close and she holds a calm neutral gaze into the lens; the clip ends mid-motion as her fingertips lift away.

Static Description: The same bright washroom of matte white square tiles, one window on the left giving soft neutral daylight, exactly one folded plain white towel on a white shelf and nothing else; no mirror, no reflective surface, no other products. She wears a fully covered, high-neck oat ribbed knit sweater with long sleeves, dark natural curls gathered up with a tortoiseshell claw clip on top of the head, no jewelry, no earrings, plain earlobes, no makeup, short natural nails — identical to the character reference in every cut. The product is exactly one cream MERIDIAN balm stick, about 9 cm tall and 3 cm wide, palm-sized, uncapped for the whole clip, no cap anywhere; its wordmark is identical to the product reference image — MERIDIAN in thin serif capitals, horizontal, upright, reading left to right, never mirrored, never re-lettered.

Audio: She speaks to camera with a natural neutral American accent — a warm, relaxed, slightly low adult woman's voice, the same voice as in the attached audio reference — iPhone microphone audio with natural quiet room tone, close phone-mic sound, no music. How she talks: Talks to one friend standing next to her, not to an audience or a camera crew. Adult woman's voice, mid-low register, soft but clear; natural American English, neutral accent; uses contractions. Calm pace, about two and a half words per second; tiny natural pauses between steps; a soft breath before the first line. Sentences end with a gentle falling intonation: no upspeak, no announcer lift, no TV-ad energy. Steady volume, close phone-mic sound, quiet bathroom room tone; no music. Speaks only the script words: no added fillers, no laughter, no giggle, no "mm-hmm". Avoid: excitement, hype, whispering ASMR, exaggerated vocal fry, robotic flatness, rushing. Lines, in order, with emotion: Cuts 1-2 (hushed, inviting a closer look): "Look at the texture." Cut 3 (calm observation, small pause after "glides"): "It glides, no tugging." Cuts 4-5 (measured appreciation): "Clear on the skin, a soft sheen." Cut 6: silence, lips closed. Cuts 7-8 (simple, like saying the name to a friend, no announcer tone): "Meridian, the balm stick."

Facial features clear and undistorted, consistent clothing throughout, neutral attentive expression in every cut, no smile, no grin, no laugh. Shot on iPhone, natural lighting, social media aesthetic, handheld micro-shake during selfie cuts, locked-off frozen frame during static-camera cuts. No on-screen text, no subtitles, no captions, no step labels, no watermarks, no legible text on any object except the product's own MERIDIAN wordmark exactly as in the product reference image, no real brand logos anywhere, no cinematic grade, no film grain, no bokeh, no lens flare, no fisheye lens, no ultra-wide distortion, no slow motion, no beauty filter, no mirror, no reflection, no phone visible, no other people, no jewelry, no earrings, exactly one stick, no cap, exactly one towel, no third arm, no extra hands, no duplicated limbs, no deformed hands.
```

## 7. Prompt clip C — routine del mattino

medias: `cf8aa65b-d28f-4559-9530-94d8c35b969b` (tavola C pulita), `7cf0287b-13a7-4025-9723-78e8a845b3d3`, `d899ee6e-fb91-4d33-afad-48ff95efd116` + audio di riferimento `<AUDIO_DA_CLIP_A_media_id>`.

```
Style & Mood: UGC iPhone aesthetic, soft neutral early-morning daylight from a window on the left in a bright white-tiled washroom, MIXED: starts with a locked-off static camera, holds static through the opening routine beats, then hard-cuts between front-facing selfie handheld beats and locked-off static beats, social media vertical format, native 720p.

Narrative Summary: A warm, easy-going presenter with a relaxed, slightly low voice, speaking at a calm conversational pace with a gentle melody, genuine and never salesy — she speaks and moves exactly like that. In one quiet 12-second morning routine step she pats her face dry with a white towel, sets it down, uncaps the MERIDIAN balm stick, twists it up and passes it over her cheekbone, forehead and jawline, ending with a soft "Done."; her expression stays neutral, relaxed and a little sleepy, never smiling.

Dynamic Description:
Cut 1 (0-1.5s) — MEDIUM CLOSE-UP, static camera: already mid-pat in frame one — both hands press the single folded white towel against her cheeks and lift it a little, eyes half-closed, a slow morning exhale into the towel; the towel lowers just enough for her lips to start the first words, relaxed and a bit sleepy. Hard cut to.
Cut 2 (1.5-3s) — WAIST-UP WIDE, static camera: her right hand lays the folded towel down on the white window ledge, her left arm resting at her side; her head lowers slightly, a slow blink, weight shifting toward the ledge; no product in frame. Hard cut to.
Cut 3 (3-4.5s) — MACRO, static camera: close on her hands at chest height — her left hand grips the capped stick, her right fingers pull the cap straight up off the top in one clean motion and the cap leaves the frame upward; after this cut the cap never appears again; her voice turns rhythmic, one verb per beat. Hard cut to.
Cut 4 (4.5-6s) — MEDIUM, static camera: from the waist up, her left hand holds the uncapped tube upright at chest height with the MERIDIAN wordmark facing the lens, identical to the product reference image, her right fingertips twist the base and the translucent dome rises; eyes down on the stick, lips finishing the last verb. Hard cut to.
Cut 5 (6-7.5s) — TIGHT CLOSE-UP, selfie: her left arm extends toward the lens off-frame, her right hand draws the dome once across her right cheekbone, holding the tube low so her fingers cover the printed part; lids half-lowered, a curl at the temple moving with the stroke; practical, unhurried voice. Hard cut to.
Cut 6 (7.5-9s) — THREE-QUARTER WIDE, static camera: by the window her right hand glides the dome once across her forehead, fingers around the printed part, left arm resting at her side; chin lifts slightly, a small recovered pause as she finds the end of the sentence, then she continues calmly. Hard cut to.
Cut 7 (9-10.5s) — MACRO, static camera: the dome glides once along her jawline just below the ear, well away from the lips, a thin clear sheen left behind, her right fingers holding the tube, left hand out of frame; lips together, no voice — the quiet beat, only room tone. Hard cut to.
Cut 8 (10.5-12s) — MEDIUM CLOSE-UP, selfie: her left arm extends toward the lens off-frame, her right hand raises the stick upright near her shoulder with the MERIDIAN wordmark facing the lens; one short, soft, falling word, then lips close and she holds a calm neutral gaze into the lens; the clip ends mid-motion as the stick lowers.

Static Description: The same bright washroom of matte white square tiles, one window on the left giving soft neutral early daylight, exactly one folded plain white towel (on the ledge after cut 2) and nothing else; no mirror, no reflective surface, no other products. She wears a fully covered, high-neck oat ribbed knit sweater with long sleeves, dark natural curls gathered up with a tortoiseshell claw clip on top of the head, no jewelry, no earrings, plain earlobes, no makeup, short natural nails — identical to the character reference in every cut. The product is exactly one cream MERIDIAN balm stick, about 9 cm tall and 3 cm wide, palm-sized; the cap is on only until cut 3 and gone afterwards; its wordmark is identical to the product reference image — MERIDIAN in thin serif capitals, horizontal, upright, reading left to right, never mirrored, never re-lettered.

Audio: She speaks to camera with a natural neutral American accent — a warm, relaxed, slightly low adult woman's voice, the same voice as in the attached audio reference — iPhone microphone audio with natural quiet room tone, close phone-mic sound, the soft brush of the towel in cut 1 and a small plastic click of the cap in cut 3, no music. How she talks: Talks to one friend standing next to her, not to an audience or a camera crew. Adult woman's voice, mid-low register, soft but clear; natural American English, neutral accent; uses contractions. Calm pace, about two and a half words per second; tiny natural pauses between steps; a soft breath before the first line. Sentences end with a gentle falling intonation: no upspeak, no announcer lift, no TV-ad energy. Steady volume, close phone-mic sound, quiet bathroom room tone; no music. Speaks only the script words: no added fillers, no laughter, no giggle, no "mm-hmm". Avoid: excitement, hype, whispering ASMR, exaggerated vocal fry, robotic flatness, rushing. Lines, in order, with emotion: Cuts 1-2 (relaxed, a little sleepy): "Morning, before makeup." Cuts 3-4 (rhythmic, one verb per beat): "Pat dry, uncap, twist up." Cuts 5-6 (practical, calm): "Cheekbones first, then everywhere that feels dry." Cut 7: silence, lips closed. Cut 8 (short, soft, falling): "Done."

Facial features clear and undistorted, consistent clothing throughout, neutral relaxed expression in every cut, no smile, no grin, no laugh. Shot on iPhone, natural lighting, social media aesthetic, handheld micro-shake during selfie cuts, locked-off frozen frame during static-camera cuts. No on-screen text, no subtitles, no captions, no step labels, no watermarks, no legible text on any object except the product's own MERIDIAN wordmark exactly as in the product reference image, no real brand logos anywhere, no cinematic grade, no film grain, no bokeh, no lens flare, no fisheye lens, no ultra-wide distortion, no slow motion, no beauty filter, no mirror, no reflection, no phone visible, no other people, no jewelry, no earrings, exactly one stick, exactly one towel, no third arm, no extra hands, no duplicated limbs, no deformed hands.
```

## 8. Da verificare prima dei video (non verificato)
- Ruolo e formato dell'audio di riferimento in `seedance_2_5` con `omni_reference` (controllare con `models_explore`, zero crediti).
- Costo dei video a 720p: dal brief/PROCEDURE circa 7 crediti/s → circa 84 crediti a clip, 252 per tre (stima, non verificata con `get_cost`, vietato).
- Se la scritta nei video esce storpiata come nelle tavole pulite: è il punto debole del set.
