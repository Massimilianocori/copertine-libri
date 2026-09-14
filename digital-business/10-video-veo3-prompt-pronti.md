# Video con persona che parla — Veo 3.1 (prompt pronti da incollare)

Sostituisce Creatify **solo** per i video con avatar parlante. Creatify resta per i video
solo-prodotto e le varianti in volume dell'outreach (vedi `04-piano-A1-ecommerce.md` §5).

Protocollo: `[VERIFICATO]` con fonte, `[IPOTESI]` altrimenti.

---

## 0. Perché abbiamo cambiato (autocorrezione, 2026-09-14)

`[VERIFICATO]` Creatify non compete sul realismo per posizionamento dichiarato: *"Creatify isn't
trying to win on realism. It's trying to win on throughput."* Scelta mia ottimizzata su costo e
volume — obiettivo giusto per l'outreach di massa, sbagliato per il video-vetrina.

`[VERIFICATO]` Creatify, HeyGen e Arcads sono tutti **avatar + lip-sync**: incollano un audio su una
faccia preesistente. È la causa strutturale dei difetti osservati — *"AI lip sync fails in three
distinct ways: word corruption, sync drift, and mouth realism failure. Teeth can swim and the mouth
shapes appear rubbery."*

`[VERIFICATO]` Veo 3.1 genera **video e parlato insieme**: *"generates UGC with synced speech audio —
mouth movement matching words, natural gesture, believable room tone."* Il difetto non viene
attenuato: non esiste come categoria.

---

## 1. Accesso e costi `[VERIFICATO]`

| Via | Costo | Resa |
|---|---|---|
| **Google Flow, gratis** | €0 | **50 crediti/giorno** ai non abbonati → usare questa per il test |
| **Google AI Pro** | $19,99/mese | 1.000 crediti Flow ≈ 100 clip Lite / 50 Fast / 10 Quality |
| Google AI Ultra | $249,99/mese | 25.000 crediti — fuori scala per ora |
| API Gemini | $0,40–4,80 per clip da 8s | solo se automatizziamo in fase 2 |

Arcads, scartato `[VERIFICATO]`: $110/mese per **10 video** ($11/video), nessun free trial, nessuno
sconto annuale, pricing page non pubblica. 5,5× il costo di Veo per 1/10 dei video, ed è comunque
lip-sync.

**Regola: prima il test gratuito su Flow. L'abbonamento si fa solo se il risultato supera l'asticella.**

---

## 2. Vincolo di formato `[VERIFICATO]`

Veo 3.1 genera clip da **8 secondi** (durata richiesta da Google per l'output 1080p). Un ad UGC da
16-18s = **2 clip concatenate in CapCut**. Impostazioni: **1080p, 9:16**.

---

## 3. Struttura del prompt che funziona `[VERIFICATO]`

Un unico paragrafo, in quest'ordine fisso:

1. **Inquadratura e comportamento camera** (selfie a distanza di braccio, ~28mm, eyeline leggermente
   fuori centro, micro-tremolio a mano libera)
2. **Soggetto** (età, aspetto, ambiente — ambienti *ordinari*, non perfetti)
3. **Azione fisica col prodotto**
4. **La battuta esatta, tra virgolette**
5. **Tappeto audio** (room tone naturale, niente musica)
6. **Cosa NON vuoi** (la lista negativa)

`[VERIFICATO]` Cosa tradisce l'AI e va negato esplicitamente: *"plastic over-smoothed skin, dead
unblinking eyes, a black void in the mouth, warped hands, bad lip sync, stiff motion"* e *"overly
perfect backgrounds, whereas real UGC often has normal counters, imperfect lighting, handheld
framing, and practical spaces."*

**Lista negativa da incollare in coda a ogni prompt** (chiamata sotto `[NEG]`):

> No text overlays, no captions, no logos, no brand names, no studio lighting, no color grading, no
> slow motion, no cinematic camera moves, no over-smoothed plastic skin, no perfect background, no
> stock-footage look.

**Continuità tra clip A e clip B:** ripetere **alla lettera** la descrizione di soggetto, vestiti,
ambiente e luce. In più, se Flow espone la funzione immagini di riferimento ("ingredients"),
caricare un fermo-immagine della clip A prima di generare la clip B
`[DA VERIFICARE nell'interfaccia al primo utilizzo]`.

---

## 4. I 4 video della pagina — prompt pronti (men's grooming)

Ogni video = clip A + clip B, montate in CapCut. Prodotto sempre **generico e senza marchio**: questi
sono campioni di stile, non ad di un brand reale.

### VIDEO 1 — Skeptic hook (sostituisce `1.mp4`)

**Clip A**
> Selfie-style handheld video shot on a phone front camera at arm's length, around 28mm, slightly
> off-center eyeline, subtle handheld micro-shake. A man in his early thirties, short dark hair,
> light stubble, plain grey t-shirt, standing in a small ordinary bathroom with white tile and a
> cluttered counter, lit only by regular overhead light. He is holding a small unbranded white
> skincare tube, glances down at it, then back at the camera, and says in a flat, skeptical tone:
> "I'll be honest with you, I did not think a moisturizer was going to fix anything." Natural room
> tone, faint bathroom reverb, no music. [NEG]

**Clip B**
> Selfie-style handheld video shot on a phone front camera at arm's length, around 28mm, slightly
> off-center eyeline, subtle handheld micro-shake. The same man in his early thirties, short dark
> hair, light stubble, plain grey t-shirt, same small ordinary bathroom with white tile and a
> cluttered counter, same overhead light. He unscrews the cap, squeezes a small amount onto his
> fingers, pats it onto his cheek while still looking at the camera, and says casually: "Three weeks
> in, my face just doesn't feel tight anymore. That's it. That's the whole review." He shrugs
> slightly and lowers the phone. Natural room tone, faint bathroom reverb, no music. [NEG]

### VIDEO 2 — Problem/solution (`2.mp4`)

**Clip A**
> Selfie-style handheld video shot on a phone front camera at arm's length, around 28mm, slightly
> off-center eyeline, subtle handheld micro-shake. A man in his late twenties, messy hair, wearing a
> hoodie, standing in an ordinary kitchen in the morning with dishes still on the counter, lit by
> daylight through a window. He rubs his jaw with one hand and says, mid-thought: "If your skin gets
> dry and irritated every single time you shave, this is the part nobody tells you." Natural room
> tone, faint kitchen ambience, no music. [NEG]

**Clip B**
> Selfie-style handheld video shot on a phone front camera at arm's length, around 28mm, slightly
> off-center eyeline, subtle handheld micro-shake. The same man in his late twenties, messy hair,
> hoodie, same ordinary kitchen with dishes on the counter, same morning daylight. He picks up a
> small unbranded bottle, turns it once in his hand to show it to the camera, and says: "I changed
> one step in my routine, not the whole thing. One. And it stopped being a problem." Natural room
> tone, faint kitchen ambience, no music. [NEG]

### VIDEO 3 — Testimonial in auto (`3.mp4`)

`[VERIFICATO]` L'inquadratura in auto è uno dei contesti UGC più credibili perché l'ambiente è
naturalmente imperfetto: luce mista, riflessi, rumore di fondo.

**Clip A**
> Selfie-style handheld video shot on a phone front camera at arm's length, around 28mm, slightly
> off-center eyeline, subtle handheld micro-shake. A man in his mid thirties sitting in the driver's
> seat of a parked car, seatbelt off, wearing a dark jacket, daylight coming through the windscreen
> with visible reflections on the glass. He looks straight at the camera and says, like he is talking
> to a friend: "Okay I need to talk about this because I was the most skeptical person about it."
> Natural room tone, faint traffic outside the car, no music. [NEG]

**Clip B**
> Selfie-style handheld video shot on a phone front camera at arm's length, around 28mm, slightly
> off-center eyeline, subtle handheld micro-shake. The same man in his mid thirties in the same
> parked car driver's seat, same dark jacket, same daylight and windscreen reflections. He holds up a
> small unbranded grooming product briefly, lowers it again, and says: "I'm not going back. That's
> the only thing I can tell you. Just putting it on your radar." Natural room tone, faint traffic
> outside the car, no music. [NEG]

### VIDEO 4 — Routine camouflage (`4.mp4`)

**Clip A**
> Selfie-style handheld video shot on a phone front camera propped up at chest height, around 28mm,
> slightly off-center eyeline, subtle handheld micro-shake. A man in his early thirties, towel over
> one shoulder, standing at an ordinary bathroom sink with several products already on the counter,
> lit by regular overhead light. He is mid-routine, not performing, and says casually while reaching
> for something: "This is just what I do in the morning, nothing complicated." Natural room tone,
> running water in the background, no music. [NEG]

**Clip B**
> Selfie-style handheld video shot on a phone front camera propped up at chest height, around 28mm,
> slightly off-center eyeline, subtle handheld micro-shake. The same man in his early thirties, towel
> over one shoulder, same ordinary bathroom sink with products on the counter, same overhead light.
> He applies a small unbranded product to his face with two fingers, checks himself quickly in the
> mirror, glances at the camera and says: "Added this one in about a month ago. It stayed." Natural
> room tone, running water in the background, no music. [NEG]

---

## 5. Procedura operativa (per ogni video)

1. Apri **Google Flow** (labs.google/flow), accedi col tuo account Google. Non abbonarti: usa i
   **50 crediti gratis giornalieri**.
2. Genera la **clip A**. Impostazioni: **9:16, 1080p, 8 secondi**. Modello: parti da **Veo 3.1 Fast**
   (rapporto crediti/qualità migliore per il test); se il parlato non convince, rigenera quella clip
   in **Quality**.
3. Guarda la clip con l'unico criterio che conta: **bocca, denti, occhi**. Se uno dei tre non regge,
   **rigenera senza modificare il prompt** (il modello è stocastico: la seconda estrazione è spesso
   migliore). Massimo 3 tentativi, poi cambia ambiente nel prompt.
4. Genera la **clip B** ripetendo alla lettera la descrizione di soggetto/ambiente.
5. **CapCut**: concatena A+B, taglia le code morte fino a **15-18 secondi**, aggiungi i **sottotitoli
   automatici** (font grande, stile TikTok), nessuna musica o musica molto bassa.
6. Esporta 1080×1920, rinomina `1.mp4`…`4.mp4`, mettilo in `digital-business/portfolio/`.

**Criterio di accettazione — non negoziabile:** se guardandolo a schermo intero **tu** noti che è AI
nei primi 3 secondi, non va sul sito. Questo è il video che vende il servizio: è l'unico asset su cui
non si applica il compromesso del volume.

---

## 6. Divisione del lavoro tra i due strumenti

| Cosa | Strumento | Perché |
|---|---|---|
| 4 video vetrina della pagina | **Veo 3.1** | devono essere impeccabili |
| Campioni personalizzati per i prospect grossi (Manscaped, Stryx, Tiege Hanley) | **Veo 3.1** | è il primo contatto, decide la risposta |
| Campioni per il volume quotidiano (2-3/giorno) | **Creatify** | URL-to-video parte dall'URL prodotto del brand: velocità imbattibile |
| Video solo-prodotto, b-roll, varianti A/B | **Creatify** | nessun volto parlante = nessun problema di lip-sync |

L'abbonamento Creatify non è sprecato: cambia ruolo, dal video-vetrina alla produzione di massa, dove
il throughput è esattamente la qualità richiesta.

---

## Fonti

- HyperFX — Arcads vs Creatify vs Higgsfield, confronto realismo 2026:
  https://www.hyperfx.ai/blog/arcads-vs-creatify-vs-higgs-field-vs-hyper-2026
- Fluxnote — Arcads pricing 2026 ($110 Starter / $220 Creator / $11 a video):
  https://fluxnote.io/guides/arcads-pricing-2026
- Wireflow — Arcads pricing, crediti e assenza di free trial: https://www.wireflow.ai/blog/arcads-pricing
- diyai.io — Google Veo pricing 2026, crediti Flow e accesso gratuito:
  https://diyai.io/ai-tools/video-generation/google-veo-pricing/
- aifreeapi — Veo 3.1 pricing guide 2026, piani e costo API per secondo:
  https://www.aifreeapi.com/en/posts/veo-3-1-pricing
- UGC Vids AI — come scrivere prompt Veo 3.1 per ad di prodotto (struttura del paragrafo, 8s/1080p/9:16):
  https://ugcvids.ai/blog/how-to-write-veo-3-1-prompts-for-product-ads
- Dupple — UGC con angoli camera realistici in Veo 3.1:
  https://www.dupple.com/tutorial/produce-ugc-style-marketing-videos-with-realistic-camera-angles-using-veo-3-1
- salesaicourse — perché il video AI sembra finto (elenco dei tell): https://salesaicourse.com/why-ai-video-looks-fake/
- Oakgen — checklist pratica per AI UGC realistiche: https://oakgen.ai/blog/realistic-ai-ugc-ads-checklist
- opencreator — workflow lip-sync e modalità di fallimento: https://opencreator.io/blog/ai-lip-sync-workflow
