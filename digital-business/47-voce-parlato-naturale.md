# 47. Voce e parlato naturale negli UGC AI (studio a costo zero, 6/10/2026)

Nessuna generazione, nessun `get_cost`, nessuna creazione di voce. Usati solo: file del progetto (CLAUDE.md, ERRORI.md, PROCEDURE.md, doc 19, 31, 33), `get_workflow_instructions ugc-video`, `get_workflow_bundle_file` (`references/monologue-craft.md`, `references/formats/review.md`), `models_explore` (seed_audio, seedance_2_5), `list_voices`, WebSearch. I siti esterni (seedance.tv, cutout.pro) erano bloccati: delle pagine web ho solo gli estratti dei risultati di ricerca, quindi sono fonti secondarie.

Legenda: **V** = verificato (file letto o schema del tool); **W** = riportato da fonte web secondaria; **I** = ipotesi da provare.

## 1. Cosa dicono le regole ufficiali Higgsfield (V)

Fonte: `monologue-craft.md`, `review.md`, `ugc-video` SKILL, riassunti anche nel doc 31.

- **Voce nativa di Seedance 2.5** (`mode: omni_reference`, `generate_audio: true`). Il workflow vieta una chiamata separata di voce/TTS. Lingua predefinita: inglese americano. Accento o tic solo se approvati.
- **Parole per clip:** fino a 10 s 12-20; 11-12 s 20-28; 13-15 s 28-35.
- **Persona della voce:** una sola frase per video, scelta nel registro NATURALE (default: calda, genuina, "girl-next-door / easy-going / dry-witty"). Regola dura: nella frase persona nessuna parola di energia (`squeal`, `scream`, `stretched vowels`, `explosive`). L'energia viene dal registro; la persona dà solo atteggiamento, melodia, cadenza, mai volume. La frase si ripete identica nel prompt del personaggio, di ogni tavola e di ogni clip, altrimenti deriva.
- **Accento:** solo testo = funziona circa 1 volta su 3. Con un campione audio di 5-10 s come riferimento audio ("solo accento e delivery, non copiare le parole, solo accento, melodia, timbro") migliora; si offre una volta, non blocca.
- **Respiri, pause, bocca chiusa:** un momento a bocca chiusa per clip (il labiale è la zona più debole); 3 micro-comportamenti per taglio (sguardo, respiro, mano); primi 0,1 s già in movimento, prima parola entro 0,4 s. **Mai scrivere pause "ingegnerizzate o drammatiche"**: gonfiano la battuta e rompono il render.
- **Copione:** prima parola mai Okay/So/Wait/Hey/Alright/Well/Like/Um; meglio un'azione visibile ("Here is the part that twists open."). Parole vietate: literally, obsessed, game-changer, holy grail, changed my life, hits different, elevate, seamless, effortless (più 10/10, 100%). Maiuscole d'enfasi 1-2 per riga, un solo picco di reazione per clip, picco "a misura umana" (un "oh" vero, mai urlato). Dal 2° clip si riparte a metà frase.
- **Verità:** creator generata adulta = presentatrice/dimostratrice, mai cliente. Vietati acquisto, uso, risultati, prima/dopo, recensioni. Claim solo da lista approvata parola per parola; senza lista, solo meccaniche visibili e sensazioni osservabili. Inquadrare come brand demo / creator concept / sponsored creative.
- **Nota di coerenza con l'errore 20:** Higgsfield descrive come default la voce nativa; il nostro metodo Sienna del 1/10 (TTS a parte come riferimento audio) è documentato in PROCEDURE.md ma il risultato qualitativo non è scritto: non so se fosse migliore o peggiore.

## 2. Tecniche per far suonare naturale la voce

### 2a. Audio nativo Seedance 2.5

- **Verificato dal nostro storico (doc 19, 23/9):** lo script troppo lungo per la durata dà parlato innaturalmente veloce; si corregge accorciando il testo, non allungando la durata (~2,5 parole/s a ritmo naturale). Mai dialogo in italiano nel prompt per un personaggio americano: il modello sintetizza la lingua letterale del prompt (24/9). Kling non si usa per il parlato (23/9).
- **V schema:** Seedance 2.5 accetta `audio_references`, `draft` (480p, finalizzabile in 1080p entro 7 giorni), `video_edit`, `video_extension`, durata 4-30 s.
- **W:** il dialogo nativo funziona meglio in inglese; altre lingue esistono ma pronuncia, timing e labiale sono meno affidabili; l'italiano non è citato tra le lingue elencate nei risultati. Per dialogo critico si tratta la voce nativa come "segnaposto" e si fa ADR in post (Cutout.pro, via ricerca). Segmenti di dialogo sotto i 15 s (stessa fonte).
- **I:** il prompt audio va specifico (voce, distanza dal microfono del telefono, stanza), come per gli effetti sonori ("ambient café sounds ..." batte "coffee shop sounds", W).

### 2b. Voce a parte (Seed Audio, clonata)

- **V schema Seed Audio 1.0:** `speech_rate` -50..100, `pitch_rate` -12..12, `loudness_rate` -50..100, formato wav/mp3, preset o voice element, riferimento audio o immagine; ha unlim; costo osservato 1,1 / 0,7 crediti a battuta (doc 33). Qwen Audio 3.0 TTS Flash ha `instruction` in linguaggio naturale, supporta `it` (doc 33): è l'unico con lingua italiana dichiarata.
- **V storico:** esiste già un voice element `sienna-1` (clonazione 40 crediti il 28/9, doc 33; la nota del 24/9 nel doc 19 dice che ancora non esisteva, è superata). Sul timbro e sulla qualità di `sienna-1` non ho dati: va ascoltata l'anteprima.
- **W:** voci clonate da 30-60 s di audio sono quasi indistinguibili dalla fonte; il segnale residuo è una dinamica emotiva un po' piatta. Il consiglio ricorrente è generare prima una clip di riferimento e iterare finché tono e ritmo sono giusti, poi usarla come voce di tutto (ugccopilot.ai, oakgen.ai, via ricerca).
- **Limite pratico (V, doc 19):** `audio_references` vuole un audio isolato caricato (`media_confirm type=audio`), non un video intero.

### 2c. Scrittura del copione (valida per entrambe)

- **W (Bland, Creatify, getimg):** frasi corte; contrazioni ("it's", "you'll") al posto delle forme piene; ordine soggetto-verbo-oggetto, attivo, come si dice a voce; punteggiatura per il respiro (virgole, trattini, punti dove una persona respira); blocchi di 1-2 frasi, non paragrafi lunghi; enfasi solo sulle parole che contano; nomi e numeri controllati per la pronuncia; voce adatta al messaggio. La voce "robotica" nasce quasi sempre dalla prosodia: tono piatto, ritmo uguale, enfasi debole, emozione non coerente con le parole.
- **V (monologue-craft):** emozione dentro le parole (il modello video rende poco la prosa piatta): un picco con vocale allungata o frase spezzata ("it's— okay wait. LOOK."), poi arco piatto, picco, assestamento. Sotto il registro NATURALE il picco resta di misura umana.
- **I:** esitazioni ("um", "uh") e interiezioni: usarne una al massimo per clip e solo dove arrivano dopo un'azione visibile; non verificato come reagisce Seedance 2.5; da provare con la clip di test.

## 3. Difetti più citati e mitigazioni

| Difetto | Fonte | Mitigazione |
|---|---|---|
| Tono da pubblicità (squilli, enfasi uniforme, parole da spot) | V monologue-craft; W | Registro NATURALE, frase persona senza parole di energia, parole vietate, apertura con azione visibile |
| Prosodia piatta / ritmo uguale | W | Frasi corte di lunghezza diversa, punteggiatura per il respiro, un picco per clip, `instruction` (Qwen) o `speech_rate` (Seed Audio) |
| Parlato troppo veloce | V doc 19 | Contare le parole sulla durata reale; accorciare il testo |
| Labiale debole | V review/monologue | Un momento a bocca chiusa per clip; mai primi piani lunghi con la bocca aperta senza respiro |
| Accento non rispettato | V monologue-craft | Campione audio 5-10 s come riferimento; senza campione 1 volta su 3 |
| Deriva della voce fra clip | V monologue-craft | Stessa frase persona identica ovunque; stesso campione; stessa durata e formato |
| Lingua sbagliata / pronuncia non inglese | V doc 19; W | Una lingua per video, scritta nella lingua parlata; per l'italiano non c'è prova (vedi sotto) |
| Voce clonata percepita come clonata | W | Iterare sulla clip di riferimento; non esagerare con le correzioni di velocità e tono |

## 4. Quanto parlato sta in 15 s e il copione skincare

- **Inglese (V):** 28-35 parole per 13-15 s; per 15 s con un momento a bocca chiusa conviene puntare a 26-30. Tagli interni da 1,9 s a 15 s.
- **Italiano (I):** l'italiano usa più sillabe per parola dell'inglese (W: ~7 sillabe/s di media, ma meno informazione per sillaba). Stima per 15 s: 24-30 parole, da misurare con una prova. Nessun dato verificato su Seedance 2.5 in italiano: `ita` è dichiarata solo per Dubbing e Qwen TTS (V doc 33).
- **Struttura (V):** una forma di storia (es. Demonstration / Mechanism Loop), un solo "ma poi", il prodotto entra tra 40% e 60% della durata; per skincare: partenza a pelle nuda (V monologue-craft, quiet process-led), un'interazione col prodotto per taglio, bersaglio corretto (siero/crema = polpastrello poi viso).
- **Niente claim né testimonianze (V):** nessun "uso da", nessun risultato, nessun "pelle più...". Senza lista claim approvata dal cliente: solo texture, gesto, packaging osservabili.
- **Esempio di copione 15 s, 26 parole (struttura da provare; la meccanica "twists open" è un segnaposto da sostituire con quella reale del prodotto):**
  "Here's the part that twists open. One drop on my fingertip, see how light it is? Now across the cheek, small circles. [bocca chiusa: pressa con le dita] That's the whole step."
  Controllo: prima parola non vietata (V), nessuna parola vietata, nessun risultato, nessuna esperienza personale, solo "my fingertip" come gesto dimostrativo.

## 5. Voci disponibili in `list_voices` (V, lette 6/10/2026)

Il tool restituisce per ogni voce solo nome, genere, tipo e anteprima audio: **nessuna età, accento o caratteristica di stile**. Si possono ascoltare solo le anteprime (non fatto qui). Totale circa 115 voci.

- **Voice element (clonata, nostra):** `sienna-1`.
- **Preset femminili:** Ainsley, Brielle, Faye, Delia, Celine, Elodie, Ginger, Giselle, Helena, Isla, Juno, Maeve, Nadine, Opal, Petra, Raina, Romy, Soraya, Talia, Livia, Daisy, Una, Evie, Kaia, Vera, Gracie, Hallie, Willow, Xenia, Yara, Annie, Zelda, Bella, Cora, Emily, Naomi, Onyx, Pixie, Remy, Tamsin, Kayla, Ines, Marisol, Roxie, Tallulah, Hana, Skye, Mabel, Maya, Quinn, Imogen, Zoe, Gia, Sloane, Luna, Vesper, Chloe, Elena, Nora, **Sienna** (nome uguale al nostro personaggio: è un preset diverso da `sienna-1`), Amanda, Anika, Anush, Karen, Kiki, Olena, Liza, Lucy, Linda, Isabella.
- **Preset maschili:** Grady, Holden, Arthur, Archie, Fraser, Benji, Cillian, Dylan, Reid, Emmett, Desmond, Ian, Cody, Evan, Jasper, Alden, Knox, Barrett, Landon, Callan, Miles, John, Callum, Bram, Marcus, Brooks, Gideon, Sterling, Harrison, Alistair, Kevin, Caspian, Julian, Mark, Orion, Andre, Xavier, Vlad, Alexey, Bob, Jake, Ken, Luc.
- Alcuni nomi suggeriscono origini diverse (Elena, Ines, Marisol, Olena, Anush, Alexey), ma **è una supposizione (I)**: nessun campo lo dichiara.

## 6. Raccomandazione (una sola)

**Metodo:** voce nativa di Seedance 2.5 (workflow ufficiale `ugc-video`, formato review in versione "presentatrice"), un clip da 15 s, con in più un campione audio di 5-10 s come riferimento di accento e delivery per bloccare la voce. Il campione si ricava da una voce preset scelta ascoltando le anteprime, generato con Seed Audio (1,1 crediti a battuta, `use_unlim` se Massimiliano lo chiede) oppure dalla voce `sienna-1` se la voce di Sienna è quella voluta. La voce a parte con labiale sincronizzato resta solo se serve un controllo parola per parola.

**Persona della voce (una frase, identica ovunque):** "A warm, easy-going presenter with a relaxed, slightly low voice, speaking at a calm conversational pace with a gentle melody, genuine and never salesy." (da approvare da Massimiliano, in inglese perché il prompt è in inglese; niente parole di energia).

**Regole di copione:**
1. 26-30 parole in 15 s (inglese); italiano da misurare (I).
2. Frasi corte, contrazioni, forma parlata, punteggiatura per il respiro; 1-2 frasi per blocco.
3. Si apre con un'azione visibile; prima parola non vietata; niente parole vietate.
4. Un momento a bocca chiusa e un solo picco di reazione "a misura umana"; nessuna pausa scritta.
5. Solo meccaniche osservabili (nessun claim senza lista approvata, nessuna esperienza in prima persona oltre al gesto dimostrativo).
6. Lingua unica per tutto il copione, scritta nella lingua del parlato.

**Prova più economica (non eseguita, richiede il "sì" di Massimiliano e il costo verificato):** una bozza 480p (`draft`) di 15 s, circa 45 crediti a 3 crediti/s (V doc 33, PROCEDURE), più l'eventuale campione Seed Audio (1,1 crediti). Se la voce è convincente, si finalizza in 1080p con `draft_job_id`.

**Cosa controllare sul video finito:**
- Voce: stesso timbro del campione dall'inizio alla fine; nessun tono da spot; nessuna accelerazione; respiri e pause credibili; accento come approvato; nessuna parola diversa dal copione (leggere i sottotitoli automatici).
- Labiale: bocca che segue ogni parola, momento a bocca chiusa pulito, nessuno sfasamento audio/video, nessuna bocca che si muove a vuoto.
- Frame per frame (CLAUDE.md): nessun taglio automatico, altre persone, volto cambiato, outfit cambiato, sorrisi non voluti.
- Verità: nessun claim, nessun "da settimane", "ho provato", "funziona"; prodotto con etichetta corretta; indicazione "AI creator / contenuto pubblicitario" in post.

## Fonti

File letti (V): `CLAUDE.md`, `ERRORI.md`, `PROCEDURE.md`, `digital-business/19-personaggio-ai-sienna.md` (righe 426-474, 690-720, 798-811), `31-ugc-regole-ufficiali-higgsfield.md`, `33-higgsfield-catalogo-modelli-preset.md`.

Tool Higgsfield di sola lettura (V): `get_workflow_instructions ugc-video`; `get_workflow_bundle_file ugc-video references/monologue-craft.md` e `references/formats/review.md`; `models_explore seed_audio` e `seedance_2_5`; `list_voices` (6 pagine).

Ricerca web (W, via WebSearch, pagine non apribili):
- Seedance 2.0 Audio Guide: https://www.cutout.pro/learn/blog-seedance-2-0-audio-guide/
- Seedance 2.0 Limitations: https://videoai.me/blog/seedance-2-0-limitations
- How to Make Text-to-Speech Sound More Natural (Bland): https://www.bland.ai/blog/how-to-make-text-to-speech-sound-more-natural
- How to add AI voice to video without it sounding like a robot (Creatify): https://creatify.ai/blog/how-to-add-ai-voice-to-video
- How to Generate Realistic Voices with AI (getimg): https://getimg.ai/blog/how-to-generate-realistic-voice-with-ai
- AI Voice Cloning Technology: https://ugccopilot.ai/glossary/voice-cloning/
- Realistic AI UGC ads checklist: https://oakgen.ai/blog/realistic-ai-ugc-ads-checklist
- Velocità di eloquio in italiano: https://www.polyglottistlanguageacademy.com/language-culture-travelling-blog/2025/8/17/why-italians-seem-to-speak-so-fast-and-how-to-keep-up

Non verificato: qualità di Seedance 2.5 nativo in italiano; risultato qualitativo del metodo Sienna 1/10 con voce a parte; timbro delle voci preset (solo anteprime non ascoltate); effetto di esitazioni e interiezioni scritte; parole per clip in italiano.
