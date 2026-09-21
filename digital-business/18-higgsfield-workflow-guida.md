# Guida operativa Higgsfield AI — workflow & ottimizzazione crediti

Fonte: sintesi della guida pratica di Youri van Hofwegen ("STOP Wasting Credits & Master
Higgsfield AI in 17 Minutes"), fissata come knowledge base permanente il 21/9/2026 su
richiesta di Massimiliano. Da consultare (e applicare) ogni volta che si pianifica una
scena o un video su Higgsfield, non solo la prima volta.

---

## 1. Principio guida: "draft cheap, upscale later" (risparmio crediti)

- **Il problema**: la variazione dei parametri può far oscillare il costo di una singola
  clip da 15 a oltre 110 crediti (o da 20 a 176+ crediti per il 4K nativo).
- **Regola**: non generare mai animazioni o video finali ad alta risoluzione al primo
  tentativo.
- **Workflow in 2 fasi**:
  1. **Bozza a bassa risoluzione (480p)**: risoluzione video al minimo (480p) con il
     modello (es. Seedance 2.5) per verificare fisica, movimento, tempismo, traiettorie
     e coerenza. Costa solo una frazione dei crediti.
  2. **Upscaling**: una volta validato il movimento, usare **Video Upscale** (modello
     *ByteDance Video Upscale*, preset *AIGC*) per portare il file da 480p a 2K.
     L'upscaling costa pochissimo e non altera struttura o movimento approvato.

## 2. Coerenza del personaggio: il Character Sheet

Non iniziare mai generando video direttamente da prompt testuali. Tutto parte dagli
still frame di riferimento.

### A. Creazione del Character Sheet (split-frame)
- **Workspace**: Image Workspace.
- **Modello consigliato**: GPT Image 2 (ottimale per fotorealismo e texture).
- **Rapporto & risoluzione**: 16:9, 2K.
- **Input**: una singola foto reale del soggetto come riferimento.
- **Struttura del prompt**:
  - **Composizione split**: immagine divisa al centro — metà sinistra a figura intera
    frontale (*full body shot*), metà destra primo piano stretto dal petto in su
    (*chest-up close-up*).
  - **Sfondo**: bianco puro, neutro e vuoto (evita elementi di disturbo che
    confonderebbero i modelli successivi).
  - **Micro-dettagli della pelle** (essenziali per evitare l'effetto plastico/AI):
    forzare rughe d'espressione, pori visibili, tono della pelle non uniforme
    (*visible pores, fine lines, uneven skin tone*). Vietare espressamente filtri
    bellezza o smoothing.
- **Utilizzo futuro**: una volta generato questo sheet, non si descrive mai più la
  faccia nel prompt — si allega semplicemente lo sheet come riferimento immagine.

## 3. Coerenza degli ambienti e illuminazione

L'ambiente va generato separatamente dal personaggio, per avere un'ancora visiva fissa.

- Solo prompt testuale (senza reference visiva iniziale se si parte da zero).
- **Separazione tramite temperatura colore**: sorgenti di luce a temperature opposte per
  staccare il soggetto dallo sfondo (es. luce calda/ambra sul soggetto, luce
  fredda/ciano sullo sfondo).
- **Luce dura vs luce morbida**: richiedere luci nette con rapida caduta d'ombra
  (*hard-edge light with fast falloff*). La luce morbida e diffusa è ciò che rende le
  immagini AI "slavate" e piatte; le ombre nette danno un look cinematografico.

## 4. Costruzione dei keyframe (inquadrature della scena)

Per unire personaggio e ambiente in inquadrature coerenti prima di passare
all'animazione:

1. **Doppia reference** nel prompt immagine:
   - Character Sheet (blocca volto/corpo).
   - Ambiente generato (blocca la stanza/location).
2. **Istruzione critica: "relighting"** — poiché il Character Sheet è su fondo bianco
   con luce piatta, il prompt deve esplicitamente ordinare al modello di
   **ri-illuminare il soggetto** con la luce dell'ambiente (es. *"relight the subject
   with amber key light from above and cyan rim light behind"*). Se omesso, il
   personaggio sembrerà ritagliato e incollato.
3. **Pianificazione cinematografica (focali e obiettivi)**:
   - *Grandangolo estremo (16mm, deep focus)*: mostra la scala reale dell'ambiente,
     dà credibilità spaziale.
   - *Dettaglio macro*: mette a fuoco micro-dettagli (es. goccia di sudore), sfocando
     lo sfondo — fa sembrare la clip un vero girato cinematografico.
   - *Angolo basso (24mm wide da terra)*: dà imponenza e forza al soggetto.
   - *Primo piano stretto (85mm, shallow depth of field)*: comprime la prospettiva ed
     elimina distrazioni sullo sfondo.
   - *Freeze moment*: inquadrare l'istante esatto dell'azione (es. impatto del pugno)
     per dare al modello video un punto di partenza geometricamente preciso.

## 5. Animazione video (Seedance 2.5)

### Regola d'oro del prompting video
**Non ridescrivere mai vestiti, volto, ambiente o luci nel prompt video se hai caricato
un'immagine di riferimento.** Descriverli di nuovo dà al modello la possibilità di
reinterpretare ciò che era già stabilito nello still frame. Il prompt video deve
contenere **esclusivamente**:
1. Movimento della camera (*camera panning, tracking shot, zoom*).
2. Azione/movimento del corpo del soggetto.

### Tre metodi di animazione
1. **Clip per clip (start frame singolo)**: carica ciascun keyframe come *Start Frame*.
   Modifica solo la durata e descrivi il movimento. Massima fedeltà per ogni singolo
   stacco.
2. **Scena continua multi-taglio (15s)**: carica la prima inquadratura come
   *Start Frame* e gli altri 4 keyframe come *Reference Images*. Chiedi tagli netti
   (*hard cuts*). Il modello mantiene la continuità senza dover inventare le
   transizioni.
3. **Senza still intermedi (sconsigliato per inquadrature precise)**: usare solo
   character sheet e ambiente porta a "framing drift" — il modello sa chi sei e dove
   sei, ma non rispetta le focali o le angolazioni volute.

### Errori di prompting da evitare nel video
- **Non nominare l'attrezzatura**: scrivere *"FPV drone shot"* farà spesso renderizzare
  un drone fisico volante dentro l'inquadratura. Descrivi invece la traiettoria fisica
  (*"fast descending continuous aerial motion over..."*).
- **Non descrivere pose fisse**: dire *"standing in a fighting pose"* genera manichini
  rigidi. Descrivi micro-movimenti attivi del corpo (*"shifting weight between feet,
  breathing heavily"*).

## 6. Workflow Cinema Studio (formato 21:9 & start/end frame)

Per produzioni cinematografiche di alto livello (nota: la guida fonte cita
Cinema Studio Video 3.0; per lo standard attuale usato da Scrollcraft vedi
Cinema Studio 4.0, confermato in `00-STATO-PROGETTO.md`, il principio del
workflow start/end frame resta identico):

- **Rapporto d'aspetto**: 21:9 (anamorfico/cinematografico).
- **Flusso start frame + end frame**:
  - Crea solo due immagini: il frame di partenza (es. primo piano casco pilota) e il
    frame di arrivo (es. auto che taglia il traguardo).
  - Inserisci il primo come *Start Frame* e il secondo come *End Frame* nel modulo
    video.
- **Prompting negativo esplicito (banning del "look AI")**:
  - Rimuovi i difetti nominandoli uno per uno: *"no HDR, no oversaturation, no digital
    sharpening, no plastic skin"*.
  - Aggiungi: *"natural film grain, gentle vignette"*.
  - Specifica *"unbranded, no logos, no text"* su veicoli/abbigliamento per evitare
    testo corrotto o allucinazioni.
- **Gestione dell'inerzia/velocità**: di default i modelli tendono a frenare o mettersi
  in posa verso l'End Frame. Per scene dinamiche, specificare ripetutamente che non c'è
  decelerazione: *"subject is already at full speed from frame 1, no deceleration at
  any point, maintains full velocity through the end frame"*.
- **Audio/Foley**: dettagliare il sound design inquadratura per inquadratura
  (*engine roar, tire squeal, flag snap*) e specificare *"no background music"*.

## 7. Soul ID: addestramento volto permanente

- **A cosa serve**: integrare in modo permanente il proprio volto nei modelli interni
  (Soul 2.0 / Soul Cinema) senza dover ricaricare immagini reference a ogni prompt.
- **Dataset (6 immagini neutre con GPT Image 2)**:
  1. Frontale
  2. 3/4 sinistro
  3. 3/4 destro
  4. Profilo sinistro
  5. Profilo destro
  6. Primo piano ravvicinato su texture della pelle
- **Regola critica di addestramento**: luce piatta da softbox frontale, sfondo grigio
  neutro (*mid-grey*), ottica 85mm. **NON** usare luci colorate o drammatiche (rim
  light, ombre marcate) nei frame di addestramento: il modello imparerebbe quella luce
  come caratteristica intrinseca del volto, riproducendola forzatamente in qualsiasi
  scena futura.
- **Nota di compatibilità**: Soul ID funziona solo con modelli *Soul* (solo still, non
  video — vedi anche nota in `00-STATO-PROGETTO.md` su Soul Character vs Reference
  Elements). Se si usano GPT Image 2, Cinema Studio, Seedream o Seedance, si continua a
  usare il Character Sheet come reference immagine.

---

## Istruzioni operative per Claude (da seguire sempre nei progetti Higgsfield)

1. Chiedere prima se esiste già un Character Sheet e gli ambienti di riferimento. Se
   mancano, aiutare a formulare i prompt per crearli prima di qualsiasi video.
2. Nei prompt video, eliminare tassativamente descrizioni fisiche ridondanti (volto,
   vestiti, ambiente, luci già fissati in un'immagine di riferimento) e nomi di
   attrezzature; concentrarsi solo su camera direction e cinetica dei corpi.
3. Se si pianificano sequenze complesse o test fisici, proporre sempre il workflow in
   480p + ByteDance Upscale a 2K per minimizzare il consumo di crediti.
