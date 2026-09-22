# Sienna — Personaggio 1 (AI creator, legata a Scrollcraft)

Creato il 22/9. Nicchia: skincare/beauty. Volto fissato come Elemento riutilizzabile Higgsfield.
**Usare `skincare-creator-v2` (id `6246992b-bae7-4de9-93d0-3286a70ccb48`)**, non il vecchio
`skincare-creator` (id `061d0104-b580-46fa-967a-1ecb4590c491`, ancora presente ma con una sola
foto di riferimento — sostituito il 23/9 perché insufficiente per il lock di identità nei video,
vedi sotto). Vedi `00-STATO-PROGETTO.md` per il contesto strategico completo (perché legato a
Scrollcraft, perché dichiarato AI, ecc.).

## Ricetta verificata per i video Kling 3.0 (23/9 — testata con crediti, prima di comprare il pass)

Prima di aprire il pass illimitato, abbiamo testato la fattibilità reale con 4 generazioni a
crediti (Ordinary Niacinamide + Sienna). I primi 3 tentativi hanno fallito in modi diversi e
istruttivi; il 4° ha funzionato. Regole emerse, da rispettare per **tutti** i 55 concept:

1. **Sempre passare un `start_image` esplicito** (una foto reale di Sienna, non solo il placeholder
   `<<<element_id>>>` nel prompt) — il solo placeholder testuale ha prodotto un volto completamente
   diverso nel primo test (capelli scuri invece che rame). Il placeholder da solo non basta a
   bloccare l'identità nei video, nelle immagini sì.
2. **Elemento personaggio con più foto** (`skincare-creator-v2`, 5 angolazioni: mirror selfie
   originale, frontale, 3/4, profilo, corpo intero) invece di una sola — rinforza il lock insieme
   allo start_image.
3. **Mai una scena con il telefono in mano se c'è anche un prodotto da manipolare.** Causa
   confermata del difetto più grave visto: con telefono in una mano e flacone+tappo+contagocce
   nell'altra, il modello perde l'oggetto a metà video (il flacone sparisce, resta il tappo
   "fluttuante"). Tolto il telefono dalla scena (fotocamera fissa/treppiede, entrambe le mani
   libere per il prodotto), il problema è sparito. Fonte: i props tenuti in mano sono il punto più
   fragile per i modelli video — meglio generare il soggetto senza l'oggetto, poi introdurlo nella
   scena vera, non farli comparire insieme dal primo frame con altro già in mano.
4. **Descrivere esplicitamente texture/colore del prodotto nel prompt** (es. "liquido trasparente e
   incolore come l'acqua, mai bianco o opaco, una goccia dal contagocce") — senza questa
   descrizione il modello ha reso un siero trasparente come una crema bianca densa applicata a
   mano, ignorando la foto di riferimento del prodotto.
5. **La durata breve (5s) non è il problema** — anzi, le clip corte mantengono la coerenza meglio
   di quelle lunghe (il drift aumenta col tempo). Nessun bisogno di allungare i test per stabilità.
6. Modalità **std** (non pro/4k) è già la più economica disponibile per Kling 3.0 in questa API —
   non esiste un'opzione 480p più leggera da scegliere. È anche già il punto giusto per Instagram:
   produce 720x1280, e IG comprime comunque tutto in upload — nessun motivo di pagare pro/4k.
7. **Kling 3.0 genera voce vera sincronizzata dal testo tra virgolette nel prompt** (`sound: "on"`),
   non solo audio ambientale — verificato con un test dedicato il 23/9. La banca voce di Sienna
   (sezione sotto) è quindi utilizzabile direttamente nei prompt di produzione.
8. **Limite reale confermato, non uno pseudo-limite**: la tecnica "storyboard a 8 pannelli →
   video" che garantisce la sequenza causale corretta (es. goccia→dito→guancia) **funziona solo
   con Seedance 2.5** (`mode: "omni_reference"`), non con Kling 3.0. Testato passando la storyboard
   come `start_image` a Kling: il risultato è la storyboard stessa quasi statica, nel formato
   orizzontale 21:9 originale (ignora l'aspect_ratio richiesto), non un video verticale animato.
   Kling non ha un meccanismo equivalente a `omni_reference` per leggere una sequenza di pannelli
   come tagli da animare. **Per i concept con meccanica prodotto precisa e multi-step, usare
   Seedance 2.5, non Kling**, anche se questo esce dal piano economico del pass illimitato Kling.
   Per i concept "solo parlato" senza coreografia complessa (routine semplici, myth-busting,
   spiegazioni ingredienti), Kling 3.0 con la ricetta sopra (punti 1-4) resta valido e più
   economico.
9. **Anche il parametro nativo `multi_shots`/`multi_prompt` di Kling (documentato per l'API Kling
   diretta: fino a 6 scene, ognuna con prompt e durata propria) non funziona in modo affidabile
   tramite questo strumento** — testato con 4 scene da 15s totali, il risultato è stato quasi
   completamente statico (solo il volto fermo che sbatte le palpebre, nessun prodotto, nessuna
   delle azioni richieste), come se i parametri fossero stati ignorati. **Verdetto chiuso dopo 3
   tentativi diversi** (storyboard-immagine, multi_shots nativo, e in precedenza start/end image):
   **Kling 3.0 non supporta cambi di inquadratura/tagli multipli in modo affidabile tramite questo
   strumento.** L'unica tecnica verificata che funziona per dare dinamismo dentro un piano Kling è
   il movimento diretto nel prompt (es. "si gira verso la camera nei primi 2 secondi", vedi sezione
   sul cambio di inquadratura sopra) — un solo piano continuo, non tagli veri. Per contenuti che
   richiedono davvero più inquadrature separate in un video, usare Seedance 2.5.
10. **Seedance 2.5 con la tecnica storyboard funziona, verificato il 23/9**: stessa storyboard di
    Sienna+Ordinary Niacinamide passata a `seedance_2_5` (`mode: "omni_reference"`, 15s, 1080p,
    audio on) invece che a Kling — risultato nettamente superiore, formato verticale corretto
    rispettato, macro fotorealistiche (dettaglio pelle a livello di poro sul polpastrello). Due
    difetti minori rilevati nel frame della pressione del bulbo: (a) il livello del liquido nel
    flacone scende in modo poco realistico (troppo, per una sola goccia), (b) l'etichetta del
    flacone diventa testo confuso invece di "The Ordinary" in quel frame specifico. Rientra nello
    scarto normale atteso in produzione (20-40%), non un fallimento strutturale — probabilmente
    basta rigenerare la singola clip in produzione, non serve ripensare l'approccio.
11. **Costo Seedance 2.5**: 70 crediti per 10s a 720p (contro 20 di Kling std) — circa 3,5x più
    caro a generazione. Nessun pass illimitato per Seedance risulta nel listino visibile tramite
    questo strumento (solo Kling 3.0 e Nano Banana hanno "7-Day Unlimited"); Massimiliano riporta
    di aver trovato sul sito un'offerta Seedance illimitata a 120€/24h non visibile da qui.
12. **Seedance 2.0 (65€) vs Seedance 2.5 (120€) — verificato il 23/9 tramite specifiche modello,
    non con un test video reale**: 2.0 ha gli stessi ruoli media di 2.5 (`start_image`, `end_image`,
    `image_references`, `video_references`, `audio_references`), quindi la tecnica storyboard
    con riferimenti multipli è disponibile in linea di principio anche su 2.0, non è esclusiva
    di 2.5. Differenze reali che contano per Sienna: (a) **2.0 è limitato a 15s per generazione,
    2.5 arriva a 30s** — esattamente il cap che oggi ci ha già costretto a tagliare Routine/
    Ingredienti/Personale da 45-90s a 20-30s; con 2.0 tornerebbero tutti a un tetto di 15s, come
    Kling; (b) **2.0 non ha le modalità `video_edit`/`video_extension`** che 2.5 offre (2.0 non ha
    nemmeno il parametro `mode` — niente `omni_reference` esplicito, i riferimenti multipli si
    passano comunque ma senza quella modalità dedicata), quindi manca lo strumento per allungare
    una clip già fatta oltre il suo limite; (c) 2.0 guadagna 4K e una modalità "fast" più economica,
    entrambe irrilevanti dato che produciamo a 720p. **Conclusione**: 65€ non è semplicemente lo
    stesso prodotto a un prezzo più basso — è un tetto di durata più stretto (15s, come Kling) e
    nessun modo nativo di estendere una clip. Dato che il piano attuale è comunque produzione a
    crediti standard e non pass illimitato (vedi punto 11 e sezione "Formato e lunghezza"), la
    scelta tra i due pass da comprare non si pone nell'immediato; se in futuro si riconsiderasse
    un pass illimitato, 2.5 resta la scelta corretta per il contenuto con inquadrature multiple
    più lunghe di 15s, non 2.0.

---

## Character bible — chi è Sienna (riscritto il 23/9 — vedi nota sotto sul perché)

**Nota sul cambio di impostazione (23/9)**: la versione precedente di questa sezione costruiva
Sienna come una "recensore onesta" con un vissuto personale sulla pelle (acne da adolescente,
percorso di anni). Problema individuato in chat: **un personaggio dichiarato AI non ha una pelle
reale, quindi non può aver vissuto quel percorso** — è un'esperienza fisica inventata, lo stesso
rischio di credibilità di "l'ho provato per un mese e ho notato X", solo spostato nel backstory
invece che nel singolo post. Non regge, e infatti un'AI che sta lì a leggere/recensire prodotti
che non può davvero provare non ispira fiducia. Sostituita con un'identità basata su personalità e
identità visiva riconoscibile (quello che funziona davvero nei profili AI reali osservati: Miquela,
Imma — non recensioni, un mondo visivo e un carattere riconoscibili), non su un'autorità che finge
un'esperienza che non ha.

**Identità**: donna, metà anni '20. Non rivendica un percorso personale con la pelle né competenza
clinica — non è quello il punto. È un personaggio eclettico con gusti/opinioni forti e un'estetica
riconoscibile; la skincare è il suo interesse del momento (letteralmente: vedi "entusiasmi a
scadenza" sotto), non una missione da esperta.

**Personalità — eclettica, un po' "matta"** (deciso il 23/9, sostituisce la versione "calda/onesta
recensore"):
- **Entusiasmi impulsivi a scadenza**: si fissa ossessivamente su qualcosa (un ingrediente, un
  rituale, un prodotto) per un periodo limitato, ne parla con un'intensità sproporzionata, poi lo
  molla platealmente dichiarandolo "finito" — genera aspettativa su cosa segue
- **Umorismo assurdo/sproporzionato**: tratta argomenti minori (la texture di una crema) con la
  stessa drammaticità di un evento serio, paragoni fuori contesto, mai seria fino in fondo
- **Vena anticonformista**: prende platealmente le distanze dal marketing e dai trend, ha
  "nemici" ricorrenti (un tipo di claim, un trend — mai un brand specifico, per evitare rischi
  legali), lo dice senza filtri ma mai in modo cattivo verso chi la pensa diversamente
- **Un interesse random ricorrente, non skincare** — le dà tridimensionalità, non è "solo
  skincare", torna ogni tanto e crea un piccolo appuntamento fisso col pubblico (dettaglio preciso
  da definire in fase di script, es. un hobby specifico e stravagante)

**Identità visiva** (il vero motore di riconoscibilità, non le opinioni): volto/capelli fissati
nell'Elemento `skincare-creator-v2` (non cambiano mai, è il lock di identità). Quello che invece
**oscilla apertamente da post a post** è il "mood" del giorno — outfit, ambientazione, color
grading — tra un piccolo set di registri ricorrenti: un giorno cupo/editoriale, un giorno
caotico/da cameretta disordinata, un giorno luminoso e pop. Vedi i pool di outfit/location/capelli
sotto, usati apposta per non ripetere mai la stessa combinazione — la varietà stilistica è voluta,
non un difetto di coerenza.

**Voce/registro**: colloquiale, diretta, in inglese americano casual (mercato target USA) —
frasi brevi, qualche intercalare naturale ("honestly", "not gonna lie"), zero linguaggio clinico
o da comunicato stampa. Vedi sezione "Voce di Sienna" sotto per esempi concreti.

**Valori non negoziabili**:
- Dichiara sempre di essere un contenuto AI/Scrollcraft quando richiesto o rilevante (bio inclusa)
- **Non simula mai un'esperienza fisica personale con un prodotto** — niente "l'ho provato e mi ha
  dato X", niente "dopo un mese ho notato", niente "reazione onesta" alla prima applicazione. Il
  prodotto può comparire in scena come oggetto/prop (lo tiene, lo mostra, fa parte della scena),
  ma il commento resta su fatti esterni verificabili (concentrazione, prezzo, INCI, cosa dicono
  fonti/altre recensioni reali citate come tali), mai su una sensazione/risultato che avrebbe
  vissuto lei. Le **opinioni** restano libere (un personaggio ha diritto a un parere, anche
  esagerato) — il limite riguarda solo l'esperienza fisica simulata.
- Ogni fatto oggettivo su ingredienti/prezzo/efficacia citato è verificato con una ricerca reale
  prima di scrivere lo script — mai inventato (vedi discussione del 22/9 in chat: rischio
  reputazionale e di responsabilità)
- Nessun claim medico o clinico assoluto ("cura", "elimina") — solo informazione generale accettata
- Scettica verso l'hype, mai scettica verso la scienza vera

**Bio account (bozza, aggiornata 23/9)**: "AI creator · made with AI by Scrollcraft · currently
obsessed with skincare (ask me again next month)"

---

## Pilastri di contenuto (ristrutturati il 23/9 — personaggio prima dell'argomento)

**Nota sul cambio (23/9)**: la versione precedente organizzava i pilastri per tipo di contenuto
informativo (routine, ingredienti, miti, demo) con la personalità trattata come un pilastro a
parte (~10%). Problema: la ricerca sotto dice che il legame col pubblico viene dall'"attrattiva
sociale"/personalità, non dal valore informativo — quindi la personalità non può essere un
pilastro tra tanti, deve essere il filo che attraversa tutti e 55. Restano validi i dati sotto
sull'attrattiva sociale e sulla vulnerabilità come fattore di fiducia; cambia solo come li
applichiamo — non più "recensioni oneste" come meccanismo centrale (vedi nota sul character bible
sul perché un'AI dichiarata non può fingere di aver provato un prodotto), ma personalità eclettica
+ identità visiva riconoscibile.

Ricerca su cosa crea davvero legame con il pubblico (fonti: studi su parasocial interaction e beauty
influencer, vedi note in fondo): **l'attrattiva fisica non è il fattore che spiega il legame con
chi segue un creator — conta l'"attrattiva sociale"** (personalità coinvolgente, sembrare vicini).
La vulnerabilità/onestà è il fattore più citato per costruire fiducia — qui si traduce in onestà
sulle proprie opinioni/entusiasmi/mollate, non in un finto resoconto di esperienza fisica.

1. **Ossessioni a scadenza** (~16) — l'entusiasmo impulsivo del momento (un ingrediente, un
   prodotto, un rituale), raccontato con intensità sproporzionata; include il formato **GRWM (get
   ready with me)** come cornice naturale per mostrare l'ossessione in azione. I prodotti reali
   compaiono qui come oggetto della fissazione, con fatti oggettivi (non esperienza simulata)
2. **Rant anticonformista** (~12) — opinioni nette contro marketing/trend/claim gonfiati, hot take,
   confronti prezzo/ingredienti — territorio di opinione libera, zero bisogno di aver "provato"
   qualcosa
3. **Assurdo/umorismo** (~9) — reazioni sproporzionate, paragoni fuori contesto, bit comici che
   trattano la skincare con più dramma di quanto meriti
4. **Interesse random ricorrente** (~6) — il suo hobby/ossessione non-skincare che torna ogni
   tanto, dà tridimensionalità e crea un piccolo appuntamento fisso col pubblico
5. **Estetica/mood del giorno** (~12, prevalentemente foto/carousel) — puro contenuto visivo,
   varietà di outfit/location/color grading, prodotto come elemento di stile senza commento su
   efficacia — qui il mondo visivo di Sienna si costruisce, non si spiega

## Formato e lunghezza (rivisto il 23/9, poi corretto lo stesso giorno per un tetto tecnico reale)

**Decisione di produzione (23/9)**: niente pass illimitato — si produce a crediti normali,
**720p** (non 1080p, IG comprime comunque tutto in upload — stesso ragionamento già fatto per
Kling), al ritmo di 3-5 video/settimana curati singolarmente, non 55 in un giorno solo.

Dati reali (studio su 6 milioni di Reels, fonti in fondo) dicono che 45-60s è la fascia con più
engagement e che l'educational sopra i 60s genera più salvataggi — **ma questo si scontra con un
tetto tecnico reale**: **Seedance 2.5 non supera i 30s per singola generazione, Kling 3.0 non
supera i 15s** (verificato: chiedere 60s a Seedance viene silenziosamente ridotto a 30s). Quindi
la durata "ideale" da dati Instagram non è sempre raggiungibile in una generazione sola — si
cappa al massimo tecnico, senza inseguire i 45-90s per gli approfondimenti (richiederebbe cucire
più clip insieme, complessità in più non necessaria per il ritmo settimanale):

| Pilastro | Natura del contenuto | Durata reale (cap 30s Seedance / 15s Kling) |
|---|---|---|
| Rant anticonformista | hot-take, hook veloce, reach | 15-30s |
| Assurdo/umorismo | bit comico, reach | 15-25s |
| Ossessioni a scadenza | GRWM/racconto dell'entusiasmo del momento | 20-30s |
| Interesse random ricorrente | storytelling breve | 20-30s |
| Estetica/mood del giorno | prevalentemente foto/carousel, poco video | — |

**Costo reale a 720p** (verificato 23/9, `seedance_2_5`, `omni_reference`, audio on): ~7
crediti/secondo, lineare. Una clip da 25s ≈ 175 crediti. A 3-5 video/settimana ≈ 525-875
crediti/settimana ≈ 26-44€/settimana ≈ 105-175€/mese — molto meno del pass a 120€/24h, e permette
di scartare/rigenerare le singole clip che non riescono (come il difetto del contagocce del primo
test) senza sprecare un pass a tempo.

- **Mix 60% foto/carousel — 40% video** (rivisto il 23/9, non più 30-40%): i dati mostrano che i
  carousel hanno ~4x l'engagement medio dei reel, e la raccomandazione per crescere un profilo AI è
  minimo 2 carousel/foto ogni 1-2 reel a settimana. Il video resta comunque necessario dove il
  parlato/movimento è il punto del concept (GRWM, rant con ritmo, bit comici che vivono di
  tempismo) — non tutto può diventare foto senza perdere forza. Mix effettivo nella lista sotto: 22
  video (40%), 33 foto/carousel (60%)

Location, outfit e pettinatura vanno curati come farebbe una persona vera — mai la stessa
combinazione ripetuta, dettagli specifici (non "casual" generico, ma il capo esatto). Vedi i pool
dettagliati subito sotto la lista concept, usati per assegnare ogni singola riga.

### Come si gestisce il "cambio di inquadratura" (rivisto il 23/9, verificato su un video di riferimento reale)

Ogni generazione Kling resta **una sola clip continua di una location** — non è un editor, non
può tagliare tra due scene diverse dentro la stessa generazione. Ma **il soggetto può muoversi
dentro l'inquadratura**, e questo basta per dare la sensazione di "cambio di camera" senza
montaggio. Verificato su un video di riferimento reale (UGC skincare, 15s): comincia con Sienna
di spalle/profilo, capelli bagnati; nei primi 1-2s **si gira verso la camera** con un movimento
naturale; poi resta in un unico piano selfie fisso per il resto della clip mentre applica il
prodotto. Nessun taglio, nessuna clip separata — solo un'azione diretta nel prompt.

Quindi, per la produzione:

1. **Default**: piano fisso, il prompt include un movimento/reveal iniziale quando ha senso per il
   concept (es. "si gira per guardare in camera", "solleva lo sguardo dallo specchio", "si volta
   mentre finisce di parlare al telefono") — dà dinamismo senza bisogno di editing.
2. **Sequenza foto (carosello di 3-6 immagini)** resta utile ma per un motivo diverso: non per
   simulare un cambio di inquadratura (che il video fa già da solo), ma per contenuti che coprono
   **momenti/location davvero distinti e non contigui** nel tempo (es. un GRWM che passa dal bagno
   alla camera, o un prima/dopo a settimane di distanza) — lì un'unica generazione video non basta
   perché non è la stessa scena continua.

---

## Pool di varietà (usati per costruire ogni riga sotto — mai la stessa combinazione due volte)

**Capelli (12)**: H1 onde naturali sciolte, riga centrale · H2 chignon basso disordinato con ciocche
libere · H3 coda alta liscia · H4 capelli bagnati, appena lavati · H5 raccolto a metà con pinza ·
H6 treccia laterale morbida · H7 onde da spiaggia leggermente umide · H8 tirati indietro bagnati,
effetto slick · H9 due space bun · H10 coda bassa, riga laterale · H11 raccolti con pinza ad
artiglio, ciocche libere davanti · H12 sciolti al naturale, dietro l'orecchio

**Outfit (18)**: O1 cardigan color avena a trecce su top bianco · O2 canotta a coste verde salvia ·
O3 felpa grigia oversize, maniche tirate su · O4 pigiama in raso color crema · O5 giacca di jeans su
t-shirt bianca · O6 vestaglia in pile lilla · O7 maglia a manica lunga nera a coste · O8 camicia di
lino terracotta, bottoni alti slacciati · O9 t-shirt oversize slavata · O10 leggings neri da
allenamento + top sportivo · O11 maglione lavorato a maglia panna · O12 camicia chambray azzurra,
maniche arrotolate · O13 giacca utility verde oliva su canotta · O14 camicia da notte a righe ·
O15 completo homewear in velluto bordeaux · O16 canotta bianca con collanina dorata sottile ·
O17 camicia di flanella oversize a quadri rosso/nero · O18 slip dress nero semplice (uscire)

**Location (15)**: L1 bagno piccolo, piastrelle bianche, specchio tondo, rubinetteria ottone ·
L2 camera, lenzuola di lino disfatte, luce del mattino tra le tende · L3 cucina, piano in marmo,
piantina aromatica · L4 bagno con vasca su piedini, pavimento piastrellato vintage · L5 angolo
lettura in camera, poltrona, lampada calda · L6 balcone con lucine, vista città al tramonto ·
L7 interno auto, parcheggiata, specchietto abbassato · L8 spogliatoio palestra, armadietti sullo
sfondo · L9 panchina in un parco, foglie autunnali · L10 divano soggiorno, plaid, candela accesa ·
L11 bagno con finestra grande, luce naturale, piante sul davanzale · L12 toeletta in camera,
specchio con luci · L13 isola cucina, sera, luce calda a sospensione · L14 ingresso/veranda,
appendiabiti, luce del mattino · L15 specchio bagno d'hotel (contenuti "pronta per uscire")

## Voce di Sienna — perché deve seguirla per come parla, non solo per il topic

Il punto sollevato il 23/9: un elenco di 55 hook/topic non basta a rendere Sienna un personaggio da
seguire — serve un modo di parlare riconoscibile, coerente con la character bible (calda, diretta,
un po' nerd sugli ingredienti, onesta fino alla schiettezza, mai clinica). Non si scrivono qui i 55
script completi (restano da scrivere al momento della produzione, per non bloccarsi su testo che
può cambiare), ma si fissa ora una banca di frasi reali che danno il timbro esatto della sua voce,
da riusare/adattare in ogni script:

**Aperture (i primi 2 secondi decidono se si continua a guardare)**:
- "Okay so I need to talk about this because I was WRONG about it for months."
- "Nobody asked but I'm going to tell you anyway."
- "Day 47 of just being honest about my skin on the internet."
- "This is not sponsored, I just have opinions."

**Transizioni/marche di stile (durante il parlato)**:
- "...and honestly? Kind of annoying, because it actually works."
- "Not gonna lie, I almost didn't post this because the results are so boring/normal."
- "This is the part where I'd normally lie to you and say it's perfect. It's not."
- "Real talk—" (seguito da un'ammissione onesta o un dato)

**Ossessione del momento (mai come esperienza fisica provata — sempre come fissazione/opinione)**:
- "I am so normal about this ingredient right now. Completely normal."
- "We're one week into the [prodotto] obsession. I'll let you know when it's over, historically that's about 10 days."
- "$6 and it's a better formula than things that cost 40. I don't make the rules, I just read labels."
- "This is going to be a whole personality trait for me until it isn't, so, enjoy it while it lasts."

**Anticonformista (mai cattiva, ma senza filtri sulle opinioni)**:
- "'Clean girl' isn't a skin type, it's a marketing team."
- "Cannot be bought, I don't have a face to break out, I just have opinions and a search engine."
- "Ask me why 'natural' means nothing on a label. I'll wait."

**Assurdo/umorismo (dramma sproporzionato su cose minori)**:
- "This dropper moved in slow motion and I felt things."
- "Not me having a whole emotional arc about a moisturizer."

**Chiusure/CTA (mai da comunicato stampa)**:
- "That's it, that's the whole tip."
- "Anyway. Use sunscreen. Bye."
- "Tell me I'm wrong, I have time today."

**Regole di scrittura per tutti gli script (da applicare quando si trasformano le 55 righe in
prompt completi)**:
- Frasi brevi, mai un periodo che spiega tre cose insieme
- **Mai simulare un'esperienza fisica con il prodotto** — niente "l'ho provato/mi ha dato/ho
  notato dopo". Il prodotto resta un oggetto in scena o argomento di opinione/fatto oggettivo
  (vedi "Valori non negoziabili" nel character bible)
- Zero superlativi assoluti ("the best", "life-changing") salvo per prenderli in giro
- Se non ha un'opinione netta su qualcosa, meglio non forzarla — la schiettezza selettiva è più
  credibile di un'opinione su tutto

## Prodotti reali usati in scena (verificati il 22/9 — mai inventare un prodotto o un claim)

Dopo il cambio di impostazione del 23/9 (vedi character bible), questi prodotti non sono più
"recensiti" da un'esperienza fisica che Sienna non ha — compaiono come oggetto delle sue
ossessioni a scadenza, dei rant anticonformisti (confronti prezzo/ingredienti), o semplicemente
come prop nelle foto estetiche. I fatti sotto (prezzo, concentrazioni, pro/contro da fonti reali)
restano utilizzabili negli script **come fatti oggettivi citati**, mai come "cosa mi è successo
usandolo". Se in futuro si aggiungono altri prodotti, stesso principio: cercare prima, scrivere lo
script dopo.

1. **The Ordinary Niacinamide 10% + Zinc 1%** — $6, niente profumo/parabeni, ottimo per pelle grassa/pori.
   Pro: prezzo bassissimo per la concentrazione. Contro: il 10% può irritare pelli sensibili, non ideale su pelle secca.
   **Foto reali salvate**: elemento `ordinary-niacinamide` (id `13013370-8421-4d68-a60b-6a7305c39dd4`) —
   flacone chiuso, contagocce aperto, confezione con scatola. Processo per gli altri 10: Massimiliano
   manda foto pulite del prodotto (senza interfaccia del sito) → upload su Higgsfield (`media_upload` →
   PUT → `media_confirm`) → salvataggio come Elemento categoria `prop` → agganciabile nei prompt insieme
   all'elemento `skincare-creator` con placeholder multipli nello stesso prompt.
2. **Paula's Choice 2% BHA Liquid Exfoliant** — $35 (formato pieno), acido salicilico 2%, fragrance-free.
   Pro: risultati clinicamente provati in 48h su pori/texture. Contro: prezzo alto, leggero odore residuo per alcuni.
   **Foto reali salvate**: elemento `paulaschoice-bha` (id `24d2c6d3-a437-4213-a4c1-c5104e76fa46`) —
   vista frontale, vista da dietro, in mano con texture sul palmo.
3. **The Ordinary Granactive Retinoid 2% Emulsion** (NON la versione "in Squalane" — packaging diverso,
   verificato il 23/9 dalle foto reali) — 0,2% Hydroxypinacolone Retinoate + retinolo incapsulato,
   arricchito con glicerina, texture cremosa/latte non oleosa, assorbe in pochi secondi lasciando finish
   satinato. Pro: risultati su pelle luminosa/pori/linee sottili senza desquamazione per la maggior parte
   degli utenti. Contro reale: **più forte della versione in Squalane** a parità di dicitura "2%" — può
   irritare pelli sensibili più di quanto ci si aspetti dal nome.
   **Foto reali salvate**: elemento `ordinary-granactive-emulsion` (id `08c56ff0-9e25-4e9b-8194-db6b1f79504f`).
4. **CeraVe Moisturizing Cream** — $18-20, 3 ceramidi + acido ialuronico + MVE technology. Pro: prodotto
   "cult" della community skincare, adatto quasi a tutti i tipi di pelle. Contro: texture ricca, poco adatta
   sotto trucco per chi ha pelle grassa.
   **Foto reali salvate**: elemento `cerave-moisturizing-cream` (id `e65570a6-cd7f-4df8-878d-ea87d9639533`) —
   fronte, retro con ingredienti, texture isolata. Esclusa una quarta foto con scritta pubblicitaria
   incorporata nell'immagine.
5. **Glow Recipe Watermelon Glow Niacinamide Dew Drops** — fascia prezzo medio-alta. Recensioni polarizzate:
   molti lodano l'effetto "glow"/glass skin, ma critiche reali su profumazione forte e alcuni report di
   irritazione/orticaria. Buon prodotto per un pro/contro onesto, non solo entusiasmo.
   **Foto reali salvate**: elemento `glowrecipe-watermelon-dewdrops` (id `3ea3c42c-4a3e-40c7-8350-44d9d5159138`) —
   bottiglia su sfondo bianco, shot lifestyle con anguria.
6. **Laneige Lip Sleeping Mask** — fascia prezzo medio-alta. Opinioni reali divise: chi lo trova
   trasformativo, chi nota solo un miglioramento modesto e lo trova troppo denso per uso diurno. Perfetto
   per un "would I repurchase this" onesto, non scontato.
   **Foto reali salvate**: elemento `laneige-lip-sleeping-mask` (id `c820da72-1f0a-4f23-93e3-c7e39e4a1d8c`) —
   vasetto Berry Fruits Rouges su sfondo bianco.
7. **Supergoop! Unseen Sunscreen** — versione EU/UK in mano (etichetta **SPF 30**, water resistant — stessa
   formula della SPF 40 venduta USA, differenza dovuta solo ai criteri di test SPF diversi tra le due
   normative), $38-44, filtri chimici (avobenzone 3%, octisalate 5%, homosalate 10%). Pro reale: finish
   completamente invisibile anche su pelli scure, texture gel leggera, ottima base trucco. Contro reale:
   prezzo alto, può pizzicare gli occhi, contiene irritanti comuni senza benefici aggiuntivi per la pelle.
   **Foto reali salvate**: elemento `supergoop-unseen-sunscreen-1` (id `3758938a-112d-4620-ad50-be28683a9f05`) —
   tubo su sfondo bianco, e swirl di texture dal tubo (la seconda foto era capovolta, corretta con rotazione
   180° prima di salvarla).
8. **Youth To The People Superfood Cleanser** — detergente delicato (tensioattivi da cocco, non solfati
   aggressivi), kale/spinaci/tè verde. Pro: best-seller reale da Sephora, adatto a pelle sensibile. Contro:
   gli antiossidanti vegetali si degradano in fretta nella formula, contiene comunque profumo/conservanti.
   **Foto reali salvate**: elemento `youth-to-the-people-cleanser` (id `d8f45538-fad8-44ba-aa63-ded0fc7cd84b`) —
   flacone con dispenser + scatola, e flacone singolo, su sfondo bianco.
9. **Vaseline (petrolatum puro)** — economicissimo (~$5). Alla base del trend "slugging": i dermatologi
   confermano che riduce davvero la perdita d'acqua transepidermica fino al 98%, ma **sconsigliato su pelle
   incline all'acne** secondo l'American Academy of Dermatology — buon equilibrio pro/contro reale.
   **Foto reali salvate**: elemento `vaseline-petroleum-jelly` (id `bd8bf5b0-72a6-47b2-8c42-048d74ee1d93`) —
   vasetto chiuso e aperto (due angolazioni), su sfondo bianco.
10. **Bubble Skincare Slam Dunk Hydrating Moisturizer** — $16, brand rivolto a teenager (Walmart), aloe +
    olio di avocado. Pro: idrata bene, prezzo accessibile. Contro onesto: **non è un prodotto trattamento**
    — niente peptidi/ceramidi/niacinamide, va abbinato ad altro se servono attivi specifici.
    **Foto reali salvate**: elemento `bubble-slamdunk-moisturizer` (id `653126a3-85fa-4571-8969-b5fe7d1f9290`) —
    flacone su sfondo bianco, e affiancato alla scatola.
11. **Mario Badescu Drying Lotion** — $17-20, formula bifasica (alcol isopropilico + acqua sopra, calamina +
    zolfo colloidale + acido salicilico sul fondo). Pro reale: riduce brufoli superficiali in poche ore,
    rituale iconico — **non va agitata**, si intinge un cotton fioc solo nel sedimento rosa sul fondo e si
    applica a puntini sul brufolo prima di dormire (da non confondere: agitarla diluisce il sedimento e la
    rende meno efficace). Contro reale: troppo seccante per pelli sensibili, poco efficace su acne cistica
    profonda, contiene alcol e profumo.

## Lista concept per la giornata di produzione (55) — riscritta il 23/9 sui nuovi pilastri

Formato per riga: **Pilastro | Formato/durata | Location | Outfit | Capelli | Concept/hook**

Nessuna riga descrive un'esperienza fisica vissuta da Sienna (niente "l'ho provato", "mi ha dato
X", "dopo un mese ho notato") — vedi la regola nel character bible. Dove un prodotto compare, il
suo ruolo è oggetto dell'ossessione/opinione/scena, mai soggetto di un test personale.

### Ossessioni a scadenza (16)

1. Ossessioni | Video 30s | L1 | O4 | H1 | "Day 3 of being insufferable about niacinamide" — **The Ordinary Niacinamide 10%+Zinc 1%**, $6, fatto: il 10% è una concentrazione alta, non ideale per pelli sensibili
2. Ossessioni | Video 28s | L3 | O12 | H6 | **GRWM**: monologo ossessivo sul perché ha comprato tre doppioni dello stesso siero
3. Ossessioni | Foto | L4 | O9 | H2 | Scaffale con **CeraVe Moisturizing Cream, The Ordinary Niacinamide, Supergoop! Unseen Sunscreen** allineati con cura maniacale, caption sull'ossessione del momento
4. Ossessioni | Video 30s | L5 | O6 | H8 | "The retinoid obsession update: still going strong, my skincare shelf is not" — **The Ordinary Granactive Retinoid 2% Emulsion**, fatto oggettivo: più forte della versione in Squalane secondo l'INCI
5. Ossessioni | Foto | L2 | O14 | H4 | Siero in mano, espressione da "sto per spiegarti la mia vita", caption "$6 and it's basically my whole personality now" — Niacinamide
6. Ossessioni | Foto | L11 | O7 | H2 | **CeraVe Moisturizing Cream** tenuta come un trofeo, caption ironica sulle ceramidi spiegate
7. Ossessioni | Video 30s | L12 | O1 | H3 | **GRWM sera**, monologo ossessivo su "the dropper technique" — **Paula's Choice 2% BHA**
8. Ossessioni | Foto | L1 | O16 | H4 | Flacone in primo piano, dito puntato verso l'etichetta, caption da lezione con troppo entusiasmo sullo zinco — Niacinamide+Zinc
9. Ossessioni | Foto | L15 | O18 | H3 | **Supergoop! Unseen Sunscreen** sempre in borsa, caption sulla fissazione per la riapplicazione
10. Ossessioni | Video 28s | L5 | O13 | H11 | Rituale ossessivo passo-passo **Mario Badescu Drying Lotion** — NON si agita, si intinge il cotton fioc solo nel sedimento rosa sul fondo
11. Ossessioni | Video 30s | L1 | O3 | H7 | "Laneige lip mask szn is back and I have no chill about it" — **Laneige Lip Sleeping Mask**
12. Ossessioni | Foto | L9 | O13 | H11 | **Supergoop! Unseen Sunscreen** al parco, ossessione da riapplicazione ogni due ore
13. Ossessioni | Video 22s | L2 | O6 | H8 | "The Bubble Skincare obsession that snuck up on me" — **Bubble Skincare Slam Dunk**, fatto onesto: non è un trattamento, solo idratante
14. Ossessioni | Video 30s | L10 | O9 | H2 | Unboxing ossessivo di **Paula's Choice 2% BHA** e **Youth To The People Superfood Cleanser**
15. Ossessioni | Foto | L13 | O17 | H11 | Formati da viaggio di **CeraVe** e **The Ordinary Niacinamide** disposti con cura maniacale
16. Ossessioni | Foto | L4 | O11 | H1 | Selfie allo specchio con il prodotto in mano, caption "Explaining Granactive Retinoid to my mirror like she asked" — **The Ordinary Granactive Retinoid 2% Emulsion**

### Rant anticonformista (12)

17. Rant | Foto | L10 | O3 | H9 | Espressione scettica in primo piano, caption con l'elenco di trend sopravvalutati
18. Rant | Video 25s | L1 | O9 | H4 | Rant sul trend "slugging" — **Vaseline**, avvertimento vero secondo l'American Academy of Dermatology: non per pelle acneica
19. Rant | Foto | L3 | O12 | H6 | Sguardo diretto in camera, caption con l'hot take per intero: il "clean girl" skincare è più hype che scienza
20. Rant | Foto | L12 | O1 | H2 | **Bubble Skincare Slam Dunk** — caption diretta: idrata bene ma non è un trattamento, punto
21. Rant | Video 25s | L4 | O6 | H8 | Perché il "purging" non è sempre quello che i video virali dicono
22. Rant | Foto | L5 | O17 | H1 | Espressione neutra/annoiata, caption "Prodotti che il marketing ama e io no" con la lista nel testo, nessun prodotto in scena
23. Rant | Video 20s | L6 | O18 | H3 | Rant al tramonto su un consiglio virale di skincare
24. Rant | Foto | L11 | O7 | H5 | **The Ordinary Niacinamide ($6)** vs **Glow Recipe Dew Drops (fascia alta)** — confronto prezzo/INCI, caption tagliente
25. Rant | Video 22s | L2 | O14 | H7 | Perché "natural" non vuol dire automaticamente sicuro
26. Rant | Foto | L13 | O11 | H10 | Primo piano con sopracciglio alzato, caption "unpopular skincare opinion" formato rapido
27. Rant | Video 30s | L1 | O9 | H11 | Rant con fonti su un mito virale specifico, tono da arringa
28. Rant | Video 25s | L1 | O7 | H3 | "Più costoso = meglio"? Smontato con i numeri, senza pietà

### Assurdo/umorismo (9)

29. Assurdo | Video 20s | L7 | O5 | H10 | Dramma teatrale per un contagocce lento — "I felt things"
30. Assurdo | Video 18s | L2 | O4 | H5 | Monologo assurdo su una crema come fosse una rottura sentimentale
31. Assurdo | Foto | L6 | O13 | H10 | Posa da copertina di rivista con un vasetto di **Vaseline**, caption ironica sul contrasto
32. Assurdo | Video 25s | L8 | O10 | H7 | Paragone assurdo tra la sua routine skincare e un allenamento in palestra
33. Assurdo | Foto | L14 | O5 | H12 | Espressione shockata leggendo un'etichetta, caption "POV: reagisco a un'etichetta INCI come se fosse un plot twist"
34. Assurdo | Foto | L3 | O12 | H1 | Espressione shockata guardando un prezzo, nessun prodotto specifico nominato
35. Assurdo | Video 20s | L1 | O16 | H9 | Sketch veloce: si fa un'autointervista assurda sul rituale serale
36. Assurdo | Video 22s | L9 | O10 | H7 | Racconta con dramma sproporzionato un banale contrattempo (la crema finita nel momento sbagliato)
37. Assurdo | Foto | L2 | O14 | H4 | Espressione esasperata al risveglio, caption comica, nessun prodotto in scena

### Interesse random ricorrente (6)

38. Random | Video 25s | L6 | O13 | H10 | Torna il suo hobby stravagante ricorrente, con un commento di striscio sulla skincare
39. Random | Foto | L9 | O13 | H11 | Momento dedicato all'hobby ricorrente, ambientazione esterna, nessun prodotto in scena
40. Random | Video 20s | L7 | O5 | H10 | Racconta un aneddoto legato all'interesse random mentre è in auto
41. Random | Video 28s | L3 | O12 | H1 | L'hobby ricorrente diventa la scusa per procrastinare la routine serale
42. Random | Foto | L14 | O5 | H12 | Still life legato all'interesse ricorrente, tono nostalgico
43. Random | Foto | L8 | O10 | H7 | Still life che accosta l'hobby ricorrente a un prodotto skincare, caption che li confronta scherzosamente

### Estetica/mood del giorno (12, prevalentemente foto/carousel)

44. Estetica | Foto | L2 | O15 | H9 | Mood cupo/editoriale, luce del mattino tra le tende, nessuna caption informativa
45. Estetica | Foto | L6 | O18 | H3 | Mood luminoso/pop al tramonto, outfit da uscita
46. Estetica | Foto | L10 | O6 | H8 | Mood caotico da cameretta, plaid e candela accesa
47. Estetica | Carosello 3 foto | L1 | O2 | H4 | Piccola sequenza GRWM mattina, solo visivo, nessuna spiegazione
48. Estetica | Foto | L12 | O1 | H5 | Toeletta, luci allo specchio, still life con un prodotto come elemento di stile (nessun commento su efficacia)
49. Estetica | Foto | L7 | O5 | H10 | Interno auto, specchietto abbassato, mood "pronta per uscire"
50. Estetica | Foto | L8 | O10 | H7 | Spogliatoio palestra, mood energico, capelli raccolti
51. Estetica | Carosello 3 foto | L11 | O7 | H2 | Sequenza in bagno con luce naturale, dettagli texture/pelle senza parlare di prodotti
52. Estetica | Foto | L14 | O5 | H12 | Ingresso/veranda, luce del mattino, mood quieto
53. Estetica | Foto | L3 | O12 | H1 | Cucina, piano in marmo, still life con pianta aromatica, mood casalingo
54. Estetica | Foto | L15 | O18 | H3 | Specchio bagno d'hotel, mood da viaggio
55. Estetica | Carosello 4 foto | L2 | O14 | H4 | Sequenza risveglio→pronta, arco narrativo solo visivo

---

## Prossimi passi

- [x] **Ripensato il personaggio da "recensore onesta" a "eclettica/personalità-first" (23/9)**:
      dopo aver notato che i profili AI di successo (Miquela, Imma) vincono per identità visiva e
      personalità, non per credibilità da recensione — e che un'AI dichiarata non può comunque
      fingere di aver provato fisicamente un prodotto — character bible, pilastri e i 55 concept
      sono stati riscritti da zero su questa base. Vedi le note "cambio di impostazione" nelle
      rispettive sezioni sopra per il ragionamento completo.
- [x] ~~Aprire il pass illimitato Kling 3.0~~ — **deciso il 23/9: niente pass, si produce a crediti
      normali** al ritmo di 3-5 video/settimana (dati reali: è il volume ottimale per la crescita,
      non serve di più) invece che 55 in un giorno solo. Permette di curare ogni video singolarmente
      e scartare/rigenerare senza sprecare un pass a tempo. Modello: Seedance 2.5 con la tecnica
      storyboard per i concept con meccanica prodotto precisa (Demo, alcuni Ingredienti/Routine),
      Kling 3.0 per il resto (parlato semplice, piano singolo). Sempre **720p**, mai 1080p/pro/4k.
- [ ] Trasformare ogni riga sopra in un prompt completo (storyboard 8-slot per Seedance, prompt
      singolo per Kling) — farlo con calma prima di produrre, non improvvisare durante, per evitare
      errori costosi come quelli scoperti nei test del 23/9 (medias mancanti, aspect ratio ignorato)
- [ ] Durante la produzione: controllo qualità per coerenza volto e assenza di artefatti,
      aspettarsi scarto 20-40%
- [ ] **Attenzione extra sulle mani con Kling** (verificato 23/9): Kling 3.0 ha un difetto noto e
      documentato su mani/dita/oggetti in mano durante il movimento ("floating arms, morphing
      hands"). Per i concept Kling che comunque coinvolgono un prodotto in mano, controllare le mani
      per prime in fase di QC, non solo il volto. Seedance con la tecnica storyboard non ha mostrato
      questo problema nei test.
- [x] **Nano Banana Pro Unlimited per le foto — attivo ma solo dal sito web** (verificato 23/9): lo
      strumento usato da Claude per generare (`use_unlim: true`) lo rifiuta ("Unlimited generations
      aren't supported for nano_banana_pro"), ma **generando direttamente su higgsfield.ai con il
      toggle "Unlimited" acceso, il test reale ha consumato 0 crediti**. Per tutte le foto/carousel
      (30-40% del piano), generare dal sito, non tramite Claude, per sfruttare le foto gratis.
- [ ] **Limite di Nano Banana Pro sul testo piccolo/denso** (verificato 23/9): in un test con
      etichetta INCI, il titolo principale ("Niacinamide 10% + Zinc 1%") è uscito corretto, ma il
      testo fine della lista ingredienti è uscito illeggibile/inventato (non sono ingredienti veri).
      Per i concept che richiedono un'etichetta leggibile in scena (es. #19), non contare sul
      modello per renderla giusta — sovrapporre l'etichetta reale in post, o inquadrare senza
      pretendere che il testo fine sia leggibile.
- [ ] Definire Personaggio 2 (non ancora iniziato)

---

## Fonti (personalità/attrattiva per il pubblico, verificate 22/9)

- UAB — studio su personalità e efficacia degli influencer: autenticità, vulnerabilità, fiducia
- Studio su parasocial interaction e beauty influencer: l'attrattiva fisica non predice il legame
  parasociale, conta l'attrattiva sociale/onestà nelle recensioni; formato GRWM citato come il più
  efficace per intimità parasociale nel beauty specifico

## Fonti (durata ottimale Reels per tipo di contenuto, verificate 23/9)

- [SocialInsider — Instagram Reels Length](https://www.socialinsider.io/blog/instagram-reels-length/) —
  studio su 6 milioni di Reels: 45-60s = più view/engagement in assoluto
- [ByteCap — Best Instagram Reels Length 2026](https://www.bytecap.io/research/best-instagram-reels-length) —
  7-30s per reach/completamento, 60-180s per tutorial/educational (salvataggi/condivisioni)
