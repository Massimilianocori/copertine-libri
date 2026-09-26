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
- **Un interesse random ricorrente, non skincare — definito il 23/9 in produzione: disegno/schizzi
  su un taccuino.** Le dà tridimensionalità, non è "solo skincare", torna ogni tanto e crea un
  piccolo appuntamento fisso col pubblico. Prop fisso e riconoscibile (taccuino + matite colorate),
  economico da generare, riusabile in tutte le righe del pilastro "Interesse random ricorrente"

**Identità visiva** (il vero motore di riconoscibilità, non le opinioni): volto/capelli fissati
nell'Elemento `skincare-creator-v2` (non cambiano mai, è il lock di identità). Quello che invece
**oscilla apertamente da post a post** è il "mood" del giorno — outfit, ambientazione, color
grading — tra un piccolo set di registri ricorrenti: un giorno cupo/editoriale, un giorno
caotico/da cameretta disordinata, un giorno luminoso e pop. Vedi i pool di outfit/location/capelli
sotto, usati apposta per non ripetere mai la stessa combinazione — la varietà stilistica è voluta,
non un difetto di coerenza. Non serve che ogni singola foto sia al massimo dell'eccentricità — vanno
bene anche scatti più tranquilli/normali, ma restano comunque suoi: stessa energia/espressione
riconoscibile, mai una posa o un'inquadratura anonima che potrebbe essere di chiunque. La varietà è
tra "diversi registri di Sienna", non tra "Sienna eccentrica" e "una selfie qualsiasi".

**Voce/registro**: colloquiale, diretta, in inglese americano casual (mercato target USA) —
frasi brevi, qualche intercalare naturale ("honestly", "not gonna lie"), zero linguaggio clinico
o da comunicato stampa. Vedi sezione "Voce di Sienna" sotto per esempi concreti.

**Valori non negoziabili**:
- **Non è una pubblicità** (aggiunto il 23/9, corretto lo stesso giorno dopo un errore ripetuto):
  stiamo costruendo un personaggio, non promuovendo prodotti. La prima versione di questa regola
  vietava solo i brand/prodotti reali — non basta: **un vasetto/flacone generico tenuto in mano
  verso la camera, o "come un trofeo", centra comunque il prodotto come soggetto della foto**,
  identico nell'effetto a una pubblicità anche senza logo. Regola corretta: **il prodotto, con o
  senza brand, non è mai l'oggetto principale dell'inquadratura.** Se compare, resta sullo sfondo o
  è solo un argomento citato a parole — mai in mano, mai al centro, mai motivo della foto. Vedi la
  nota nella sezione "Pilastri di contenuto" per il precedente che ha portato alla prima versione
  della regola
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
   rituale, un'abitudine, un'idea strana), raccontato con intensità sproporzionata; include il
   formato **GRWM (get ready with me)** come cornice naturale per mostrare l'ossessione in azione.
   **Nessun brand/prodotto reale come oggetto strutturale** (vedi nota sotto sul perché) — al
   massimo un ingrediente citato in astratto (niacinamide, retinoidi), mai un flacone specifico
   riconoscibile
2. **Rant anticonformista** (~12) — opinioni nette contro marketing/trend/claim gonfiati, hot take,
   confronti prezzo/ingredienti in astratto — territorio di opinione libera, zero bisogno di aver
   "provato" qualcosa e zero bisogno di mostrare un prodotto reale in scena
3. **Assurdo/umorismo** (~9) — reazioni sproporzionate, paragoni fuori contesto, bit comici che
   trattano la skincare con più dramma di quanto meriti
4. **Interesse random ricorrente** (~6) — il suo hobby/ossessione non-skincare che torna ogni
   tanto, dà tridimensionalità e crea un piccolo appuntamento fisso col pubblico
5. **Estetica/mood del giorno** (~12, prevalentemente foto/carousel) — puro contenuto visivo,
   varietà di outfit/location/color grading, nessun prodotto reale richiesto — qui il mondo visivo
   di Sienna si costruisce, non si spiega

## Correzione pesi pilastri e stile — confronto con Lil Mayo (25/9)

Analizzato in chat il profilo @lilmayo (alieno fotorealistico su corpo umano in scenari reali
assurdi — jail, casinò, pool hall, yacht, party — 1,4M follower, 259 post, engagement 19-63k
like/post). Non è un profilo skincare, ma è il caso più chiaro visto finora di un personaggio AI
che sfrutta a pieno i meccanismi di attrattività/riconoscibilità che la ricerca in fondo a questo
documento già indicava. Cinque leve identificate, con cosa cambia per Sienna da qui in avanti:

1. **Segno visivo distintivo fisso, non solo i capelli.** La testa da alieno è impossibile da
   confondere, sempre presente a prescindere da outfit/location. I capelli rame di Sienna sono un
   inizio ma non bastano da soli a fare da "firma" a colpo d'occhio. **Regola nuova**: il taccuino/
   matite colorate del pilastro "Interesse random ricorrente" (già introdotto il 23/9) va trattato
   come secondo segno fisso, non solo come prop occasionale — va reintrodotto più spesso, anche fuori
   dalle righe dedicate a quel pilastro, come elemento che torna a prescindere dal registro del giorno.
2. **Il pilastro Assurdo è il motore principale del profilo comp, non un pilastro tra tanti.**
   Nella distribuzione attuale dei 55 concept è solo ~16% (9/55), il più piccolo dopo Random.
   **Correzione di peso per le prossime produzioni**: aumentare sensibilmente la quota di Assurdo/
   umorismo a scapito di Estetica/mood (che resta utile per costruire il mondo visivo ma non deve
   restare il pilastro più numeroso) — indicativamente riportare Assurdo verso il 25-30% del totale
   nel prossimo batch di concept, Estetica verso il 15-20%. Non riscritta la lista dei 55 esistente
   (resta valida per l'uso corrente), ma il prossimo batch di concept da scrivere segue questo nuovo
   equilibrio.
3. **Stile "candid", non editoriale, per almeno metà della produzione futura.** Le foto di Lil Mayo
   leggono come scattate da un passante/con un telefono, non come un servizio fotografico — è
   proprio questa "imperfezione" a renderle credibili invece che leggersi come "prodotte". Le foto/
   video di Sienna finora (compreso lo stile Palm Springs "da operatore cinematografico") vanno nella
   direzione opposta. **Regola nuova**: per almeno metà dei prossimi concept, specificare
   esplicitamente nel prompt un'inquadratura da foto scattata al volo (leggermente storta, meno
   simmetrica, luce meno curata, meno profondità di campo cercata) invece del linguaggio cinematico
   di default (35mm, dolly, chiaroscuro) — soprattutto per il pilastro Assurdo, dove l'effetto
   "sembra reale" amplifica la gag.
4. **Comparse che reagiscono in scena.** Lil Mayo interagisce spesso con persone reali (polizia,
   commessi, sconosciuti) che reagiscono visibilmente a lui — dà l'idea di un mondo che la nota, non
   un set vuoto. **Regola nuova**: dove la scena lo permette, includere una comparsa sullo sfondo con
   una reazione leggibile (sorpresa, distrazione, un'occhiata) invece di scene sempre a soggetto
   singolo — da usare soprattutto nei concept Assurdo con location pubbliche (L1 negozio dischi, L9
   mercatino, L13 diner, L14 cinema).
5. **Caption a battuta/testo diretto sull'immagine**, non descrittive — già in parte in uso (vedi
   "Voce di Sienna"), va confermato come standard per Assurdo e Ossessioni: la caption è la battuta
   stessa o una riga di finto dialogo, mai una didascalia che spiega la foto.

Non adottato: il volume di pubblicazione di Lil Mayo (259 post) non è comparabile al nostro ritmo
3-5/settimana per vincoli di budget — si compensa con gag più dense per post (vedi caroselli-
storia), non inseguendo il volume.

## Format ricorrente "Scoperta della settimana" (25/9) — sotto-formato di Ossessioni

Introdotto per coprire una metrica che nessun pilastro esistente copriva: i pilastri Assurdo/Rant/
Ossessioni generano like e commenti (legame parasociale), ma nessuno punta ai **salvataggi** — che i
dati (SocialInsider, ByteCap, vedi fonti in fondo) associano specificamente ai contenuti
educational. Non diventa un settimo pilastro: resta un sotto-formato di Ossessioni, con cadenza
fissa (1 episodio a settimana) invece che sparso nella lista dei 55 concept.

**Perché non è un tip-tutorial generico**: un fatto verificato raccontato in tono da lezione la
metterebbe nel ruolo di "esperta che dispensa consigli", esattamente il posizionamento escluso dal
character bible (non ha competenza clinica dichiarata, è un personaggio con opinioni/entusiasmi, non
un'autorità). Stesso fatto, stessa fonte verificata — cambia solo l'inquadratura: non "il tip che ti
serve", ma "la sua scoperta/entusiasmo della settimana", nel registro genuino già definito per
Ossessioni (veloce, si accavalla, mai ironico a distanza).

**Meccanica dell'episodio (20-30s)**:
1. Hook genuino stile Ossessioni — "Okay wait, I did NOT know this—"
2. Il fatto, verificato con ricerca reale prima di scrivere lo script (stessa regola non negoziabile
   di sempre — mai un brand/prodotto reale nominato, resta un ingrediente/meccanismo in astratto)
3. Lo scrive nel taccuino mentre parla, negli ultimi secondi del piano — nessun testo sovrimpresso
   (il modello lo rende illeggibile sui dettagli fini, già verificato altrove nel documento): la
   pagina scritta a mano è il frame pensato per essere salvato, e rinforza il taccuino come secondo
   segno visivo fisso (vedi correzione Lil Mayo sopra)
4. Chiusura con la sua reazione/opinione personale, mai un imperativo da tutorial ("salvalo!" — la
   sua vena anticonformista lo prenderebbe in giro)

**Maschera**: se in scena, sempre una sheet mask leggera in tessuto, mai la maschera rigida
bianca/peel-off usata nella serie spa — quella si muove male con la bocca che parla, la sheet mask
invece è il tipo che si vede addosso a chi fa altro nel frattempo (coerente con lo stile candid).

**Location fissa, non a rotazione** (a differenza di tutti gli altri concept, dove location/outfit
cambiano apposta ogni volta): un format settimanale ricorrente funziona al contrario — stesso angolo
di casa ogni volta, rinforza la sensazione di appuntamento fisso. Definita: **bagno di casa sua**,
specchio ovale anni '20 con lampadine tonde intorno (stesso registro della toeletta L12 del pool, ma
personalizzato come suo spazio privato, non un camerino pubblico), carta da parati botanica vintage
sullo sfondo, mensola con oggetti personali disordinati ma caratteristici (boccette assortite, uno
specchietto, gioielli lasciati lì), taccuino e matite sempre appoggiati pronti sulla mensola, luce
calda dalle lampadine intorno allo specchio.

**Tecnico**: `seedance_2_5`, `mode: "omni_reference"`, non Kling 3.0 — verificato il 25/9 che Kling
non regge l'identità di Sienna in modo coerente (stesso esito già emerso con la mini-serie Palm
Springs il 24/9). Tutti i riferimenti buoni dell'elemento passati esplicitamente come `medias`
(`image_references`), escludendo quello scartato ("corpo intero") — stessa tecnica appena validata
per le foto. Piano fisso con un piccolo movimento/reveal iniziale (es. si china verso lo specchio),
9:16, 720p, audio on. Costo stimato ~140-175 crediti a episodio (20-25s × ~7 crediti/sec) — con il
saldo reale verificato il 25/9 (1465 crediti), un episodio a settimana è ampiamente sostenibile.

**Caption tipo**: breve, mai da post educativo — *"wrote this down so I don't forget it again"*

**Esempi di episodi (stile, non script completi)**:
- Perché il retinolo si applica la sera, non prima del sole (fotosensibilità — fatto dermatologico
  reale)
- La differenza vera tra "fragrance-free" e "unscented" (quasi nessuno la conosce, verificabile da
  INCI)
- Perché il "purging" dura davvero 4-6 settimane, non mesi (ciclo di rinnovamento cellulare)

**Nota sui prodotti reali (23/9, seconda correzione della giornata)**: nel primo banco di prova
generato, i concept che citavano un prodotto reale sono finiti visivamente centrati sul flacone
(tenuto in mano verso la camera, confrontato, allineato su una mensola) — esattamente
l'inquadratura da product photography/recensione da cui ci eravamo allontanati con il cambio di
personaggio. Punto sollevato in chat: **stiamo costruendo un personaggio, non una pubblicità — non
c'è motivo per cui debba avere un prodotto reale in scena.** I flaconi/vasetti veri e i loro fatti
verificati restano documentati sotto ("Prodotti reali usati in scena") come banca dati consultabile
per un eventuale uso futuro puntuale (es. un vero post sponsorizzato, se mai capiterà), ma **non
sono più un elemento strutturale dei 55 concept** — dove serve un ingrediente/oggetto in scena,
resta generico (un flacone senza brand, un ingrediente citato in astratto), mai un prodotto reale
riconoscibile.

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
  video (40%), 33 foto/carousel (60%). **Aggiornamento 23/9**: il mix 60/40 resta l'obiettivo a
  lungo termine, ma per l'apertura delle pagine si parte **100% foto/carousel** — vedi nota in
  "Prossimi passi" sul video Kling messo in pausa per problemi di affidabilità/realismo. Le 22 righe
  video della lista restano scritte ma non si producono finché il video non viene ripreso.

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

**Outfit (18) — riscritto il 23/9, deve restare eclettico/stonato, mai homewear generico da
"selfie a casa"**: O1 pelliccia sintetica leopardata aperta su semplice top bianco · O2 kimono
vintage patchwork a stampe miste sopra pigiama a righe · O3 tuta ginnica anni '80 fluo con collant
a righe spaiati · O4 vestito fiorito vintage con collant colorati non abbinati · O5 giacca di jeans
ricoperta di spille/pin improbabili su abito nero semplice · O6 vestaglia in velluto bordeaux con
boa di piume · O7 maglione natalizio fuori stagione su gonna di paillettes · O8 salopette denim con
una gamba arrotolata, bandana annodata al collo · O9 slip dress in seta stampa animalier con
blazer oversize completamente spaiato · O10 tuta da lavoro vintage dipinta a mano · O11 cardigan
"da nonna" a righe multicolore su reggiseno sportivo · O12 vestito a pois anni '50 con occhiali da
sole a farfalla giganti · O13 giacca utility militare ricoperta di toppe improbabili · O14
vestaglia di raso con turbante coordinato vistoso · O15 completo homewear in velluto smeraldo con
collana vistosa di perle finte oversize · O16 canotta bianca con collane a strati totalmente
spaiate (una di corda, una di plastica, una di metallo) · O17 camicia hawaiana sopra pigiama a
quadri · O18 abito da sera nero con anfibi da combattimento e calzini spaiati a vista

**Location (15) — riscritto il 23/9, deve restare un posto specifico e riconoscibile, mai "casa
generica"**: L1 negozio di dischi vintage, neon rosa/blu, palla da discoteca, scaffali di vinili ·
L2 camera con carta da parati anni '70 a fiori, poster ovunque, lampada lava accesa · L3 cucina
retrò anni '50, elettrodomestici pastello, pavimento a scacchi · L4 bagno con vasca vittoriana su
piedini, piante enormi ovunque, carta da parati botanica · L5 angolo lettura massimalista, libri
impilati ovunque, luci di Natale accese tutto l'anno · L6 balcone con lucine, tappeti sovrapposti,
vista città al tramonto · L7 interno di un maggiolino Volkswagen decappottabile d'epoca, parcheggiato
· L8 camerino/backstage teatrale, specchi con lampadine tonde, costumi di scena appesi · L9
mercatino vintage/dell'usato all'aperto, bancarelle colorate · L10 salotto massimalista, stampe
multiple che non si abbinano, piante enormi, luce calda · L11 serra botanica, luce naturale filtrata,
piante tropicali enormi · L12 toeletta anni '20, specchio ovale, lampadine teatrali intorno · L13
diner/tavola calda vintage, sedute in vinile colorato, insegne al neon · L14 ingresso di un cinema
d'epoca, insegne al neon accese, locandine vintage · L15 bagno di un hotel boutique eccentrico,
carta da parati animalier, vasca freestanding colorata

## Voce di Sienna — perché deve seguirla per come parla, non solo per il topic

Il punto sollevato il 23/9: un elenco di 55 hook/topic non basta a rendere Sienna un personaggio da
seguire — serve un modo di parlare riconoscibile, coerente con la character bible (calda, diretta,
un po' nerd sugli ingredienti, onesta fino alla schiettezza, mai clinica). Non si scrivono qui i 55
script completi (restano da scrivere al momento della produzione, per non bloccarsi su testo che
può cambiare), ma si fissa ora una banca di frasi reali che danno il timbro esatto della sua voce,
da riusare/adattare in ogni script:

**Registro per pilastro (aggiunto 23/9 — prima tutte le frasi sotto avevano la stessa cadenza
ironica/distaccata indipendentemente dal pilastro, che non è varietà reale, solo temi diversi nello
stesso tono).** Ogni pilastro deve suonare diverso, non solo parlare di cose diverse:

- **Ossessioni a scadenza → entusiasmo genuino, non ironico.** Parla veloce, si accavalla, si
  interrompe da sola, ride mentre si emoziona davvero (non a distanza di sicurezza). Es.: "Wait no
  okay so—", "I NEED you to understand something right now", "I've said her name four times today
  and it's not even noon"
- **Rant anticonformista → diretta e tagliente, frasi corte.** Meno battute, più affermazioni
  nette, quasi infastidita, ritmo secco senza rallentamenti. Es.: "No.", "That's marketing. That's
  it. That's the whole thing.", "I'm not doing the bit today, I'm just annoyed"
- **Assurdo/umorismo → teatrale, pause lunghe, mock-serio.** Escalation lenta, tono da narratore
  di documentario applicato a niente, silenzi prima della battuta. Es.: "...and that's when I knew.
  [pausa] Nothing. Nothing happened. I just felt like pausing.", "This is fine. This is completely
  fine. [non lo è]"
- **Interesse random ricorrente → più lenta, sincera, senza ironia di difesa.** Quasi nostalgica,
  frasi più lunghe, nessuna battuta a chiudere. Es.: "I don't really know why I still do this, I
  just do", "This has nothing to do with anything, I just wanted to show you"
- **Estetica/mood del giorno → di norma nessun parlato** (solo foto/caption minimale) — quando c'è
  una caption, resta breve e non nello stesso registro ironico degli altri pilastri

Le frasi sotto (aperture/transizioni/chiusure) restano valide come ganci generali, ma **vanno
adattate al registro del pilastro sopra**, non usate sempre con la stessa cadenza piatta.

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
- **Ogni script deve avere un punto preciso a cui arriva, non solo un'apertura** (regola aggiunta
  il 23/9 dopo un test reale fallito su questo: lo script usava l'apertura "I need to talk about
  this because I was wrong about it for months", poi mostrava solo l'azione e finiva — mai detto
  su cosa esattamente avesse torto. Un'apertura da sola promette una rivelazione/opinione/fatto,
  non lo sostituisce). Le frasi della banca sopra sono ganci per i primi secondi, **non uno script
  completo** — vanno sempre chiuse con l'informazione/opinione/battuta specifica a cui portano.
  Stesso test già usato altrove nel documento: se togli l'apertura, deve restare qualcosa in piedi
- Frasi brevi, mai un periodo che spiega tre cose insieme
- **Mai simulare un'esperienza fisica con il prodotto** — niente "l'ho provato/mi ha dato/ho
  notato dopo". Il prodotto resta un oggetto in scena o argomento di opinione/fatto oggettivo
  (vedi "Valori non negoziabili" nel character bible)
- Zero superlativi assoluti ("the best", "life-changing") salvo per prenderli in giro
- Se non ha un'opinione netta su qualcosa, meglio non forzarla — la schiettezza selettiva è più
  credibile di un'opinione su tutto

## Banca prodotti reali (verificati il 22/9 — dormiente dal 23/9, non più usata nei 55 concept)

**Stato aggiornato il 23/9 (seconda correzione della giornata)**: dopo aver visto che i concept con
un prodotto reale finivano visivamente centrati sul flacone (product photography, non personaggio —
vedi nota in "Pilastri di contenuto"), i 55 concept sono stati riscritti senza nessun brand/prodotto
reale come elemento strutturale. Questa sezione resta come **banca dati consultabile**, non più
collegata di default alla lista concept — utile solo se in futuro serve davvero un post puntuale con
un prodotto reale (es. una vera collaborazione sponsorizzata). I fatti sotto (prezzo, concentrazioni,
pro/contro da fonti reali) restano corretti e verificati, ma **non vanno più assegnati automaticamente
a una riga della lista concept**. Se in futuro si aggiungono altri prodotti per un uso puntuale, stesso
principio: cercare prima, scrivere lo script dopo, e mai come "cosa mi è successo usandolo" (vedi
regola non negoziabile nel character bible).

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
X", "dopo un mese ho notato") — vedi la regola nel character bible. E dopo la nota sui prodotti
sopra: **nessuna riga richiede più un prodotto reale/brand riconoscibile in scena** — è un
personaggio, non una pubblicità. Dove compare un flacone/vasetto, resta generico o è un ingrediente
citato solo a parole.

### Ossessioni a scadenza (16)

1. Ossessioni | Video 30s | L1 | O4 | H1 | "Day 3 of being insufferable about niacinamide" — monologo ossessivo sull'ingrediente in astratto (percentuali, perché ne parlano tutti), nessun brand in scena
2. Ossessioni | Video 28s | L3 | O12 | H6 | **GRWM**: monologo ossessivo sul perché ha comprato tre doppioni dello stesso siero (generico, mai nominato)
3. Ossessioni | Foto | L4 | O9 | H2 | Riorganizza lo scaffale skincare per colore invece che per funzione, con cura maniacale, flaconi generici senza etichette leggibili, caption sull'ossessione del momento
4. Ossessioni | Video 30s | L5 | O6 | H8 | "The retinoid obsession update: still going strong, my skincare shelf is not" — monologo ossessivo sui retinoidi in generale, nessun prodotto specifico nominato
5. Ossessioni | Foto | L2 | O14 | H4 | Espressione da "sto per spiegarti la mia vita", mani che gesticolano a mezz'aria, nessun oggetto in mano, caption "it's basically my whole personality now"
6. Ossessioni | Foto | L11 | O7 | H2 | Espressione fiera/soddisfatta come chi ha appena vinto qualcosa, nessun oggetto in mano, caption ironica sulle ceramidi spiegate
7. Ossessioni | Video 30s | L12 | O1 | H3 | **GRWM sera**, monologo ossessivo sulla sua personalissima "dropper technique", nessun brand nominato
8. Ossessioni | Foto | L1 | O16 | H4 | Dito puntato verso la camera come in una lezione immaginaria, nessun oggetto in scena, caption da lezione con troppo entusiasmo sullo zinco come ingrediente
9. Ossessioni | Foto | L15 | O18 | H3 | Ossessionata dal contare quante volte si tocca la faccia in un giorno, tally teatrale sulle dita, nessun prodotto in scena
10. Ossessioni | Video 28s | L5 | O13 | H11 | Rituale ossessivo passo-passo con un trattamento spot generico bifasico — NON si agita, si aspetta che il sedimento si depositi sul fondo prima di usarlo
11. Ossessioni | Video 30s | L1 | O3 | H7 | "Lip mask szn is back and I have no chill about it" — maschera labbra generica, nessun brand
12. Ossessioni | Foto | L9 | O13 | H11 | Inventa un suo personale rituale di "skin cycling", lo spiega con diagrammi immaginari disegnati a mano nell'aria
13. Ossessioni | Video 22s | L2 | O6 | H8 | "The [nome buffo che si inventa] obsession that snuck up on me" — un idratante economico trovato per caso, ne parla come se avesse scoperto l'oro
14. Ossessioni | Video 30s | L10 | O9 | H2 | Unboxing ossessivo di due prodotti skincare generici appena arrivati, reazione sproporzionata all'imballaggio
15. Ossessioni | Foto | L13 | O17 | H11 | Prepara il beauty case da viaggio con precisione militare, ogni oggetto in un ordine preciso e non negoziabile
16. Ossessioni | Foto | L4 | O11 | H1 | Selfie allo specchio, mani che gesticolano spiegando qualcosa al proprio riflesso, nessun oggetto in mano, caption "Explaining retinoids to my mirror like she asked"

### Rant anticonformista (12)

17. Rant | Foto | L10 | O3 | H9 | Espressione scettica in primo piano, caption con l'elenco di trend sopravvalutati
18. Rant | Video 25s | L1 | O9 | H4 | Rant sul trend "slugging" — avvertimento vero secondo l'American Academy of Dermatology: il petrolato non è per pelle acneica, nessun brand nominato
19. Rant | Foto | L3 | O12 | H6 | Sguardo diretto in camera, caption con l'hot take per intero: il "clean girl" skincare è più hype che scienza
20. Rant | Foto | L12 | O1 | H2 | Rant su un idratante economico virale su TikTok (nessun brand mostrato) — caption diretta: idrata bene ma non è un trattamento, punto
21. Rant | Video 25s | L4 | O6 | H8 | Perché il "purging" non è sempre quello che i video virali dicono
22. Rant | Foto | L5 | O17 | H1 | Espressione neutra/annoiata, caption "Prodotti che il marketing ama e io no" con la lista nel testo, nessun prodotto in scena
23. Rant | Video 20s | L6 | O18 | H3 | Rant al tramonto su un consiglio virale di skincare
24. Rant | Foto | L11 | O7 | H5 | Sguardo diretto in camera, caption tagliente su un prodotto economico con lo stesso ingrediente attivo di uno 7 volte più caro — confronto in astratto, nessun brand mostrato in scena
25. Rant | Video 22s | L2 | O14 | H7 | Perché "natural" non vuol dire automaticamente sicuro
26. Rant | Foto | L13 | O11 | H10 | Primo piano con sopracciglio alzato, caption "unpopular skincare opinion" formato rapido
27. Rant | Video 30s | L1 | O9 | H11 | Rant con fonti su un mito virale specifico, tono da arringa
28. Rant | Video 25s | L1 | O7 | H3 | "Più costoso = meglio"? Smontato con i numeri, senza pietà

### Assurdo/umorismo (9)

29. Assurdo | Video 20s | L7 | O5 | H10 | Dramma teatrale per un contagocce lento — "I felt things"
30. Assurdo | Video 18s | L2 | O4 | H5 | Monologo assurdo su una crema come fosse una rottura sentimentale
31. Assurdo | Foto | L6 | O13 | H10 | Posa da copertina di rivista esagerata sul balcone al tramonto, nessun prodotto in scena, tutto il dramma sta nella posa
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
43. Random | Foto | L8 | O10 | H7 | Still life che accosta l'hobby ricorrente a un momento qualsiasi della sua giornata, caption che li confronta scherzosamente

### Estetica/mood del giorno (12, prevalentemente foto/carousel)

44. Estetica | Foto | L2 | O15 | H9 | Mood cupo/editoriale, luce del mattino tra le tende, nessuna caption informativa
45. Estetica | Foto | L6 | O18 | H3 | Mood luminoso/pop al tramonto, outfit da uscita
46. Estetica | Foto | L10 | O6 | H8 | Mood caotico da cameretta, plaid e candela accesa
47. Estetica | Carosello 3 foto | L1 | O2 | H4 | Piccola sequenza GRWM mattina, solo visivo, nessuna spiegazione
48. Estetica | Foto | L12 | O1 | H5 | Toeletta, luci allo specchio, still life con oggetti personali (specchietto, gioielli, un quaderno) come elemento di stile, nessun prodotto skincare in scena
49. Estetica | Foto | L7 | O5 | H10 | Interno auto, specchietto abbassato, mood "pronta per uscire"
50. Estetica | Foto | L8 | O10 | H7 | Spogliatoio palestra, mood energico, capelli raccolti
51. Estetica | Carosello 3 foto | L11 | O7 | H2 | Sequenza in bagno con luce naturale, dettagli texture/pelle senza parlare di prodotti
52. Estetica | Foto | L14 | O5 | H12 | Ingresso/veranda, luce del mattino, mood quieto
53. Estetica | Foto | L3 | O12 | H1 | Cucina, piano in marmo, still life con pianta aromatica, mood casalingo
54. Estetica | Foto | L15 | O18 | H3 | Specchio bagno d'hotel, mood da viaggio
55. Estetica | Carosello 4 foto | L2 | O14 | H4 | Sequenza risveglio→pronta, arco narrativo solo visivo

---

## Prossimi passi

- [ ] **CORREZIONE WORKFLOW DA APPLICARE SEMPRE D'ORA IN POI (26/9)**: tutte le foto di Sienna
      generate in questa sessione (spa, negozio dischi, test corpo) sono state fatte nel modo
      sbagliato — personaggio, location e outfit generati **tutti insieme in un solo prompt**,
      ignorando il workflow già fissato il 21/9 in `18-higgsfield-workflow-guida.md` (sezione 3-4),
      che dice esplicitamente di **generare l'ambiente separatamente** (solo testo, senza
      personaggio) e poi **combinarlo con il Character Sheet + un'istruzione di relighting
      esplicita** (es. "relight the subject with amber key light from above and cyan rim light
      behind"), altrimenti il personaggio rischia di sembrare "ritagliato e incollato" sullo sfondo.
      **Da questa data in poi, per ogni nuova location**: (1) generare l'ambiente vuoto da solo,
      (2) generarlo di nuovo insieme ai riferimenti di Sienna con relighting esplicito nel prompt,
      mai più tutto insieme dal primo tentativo. Le location già usate senza questo metodo
      (bagno spa, sala tè, negozio dischi versione originale) restano valide così come sono uscite,
      non vanno rifatte tutte — il metodo corretto si applica alle produzioni successive.
- [x] **Video in pausa, si punta solo sulle foto per l'apertura (23/9)**: due test video Kling con
      il nuovo pool eclettico — uno (Ossessioni, angolo lettura) ha seguito la scena correttamente,
      l'altro (Rant, diner) ha ignorato completamente la scena richiesta e ha solo animato la foto
      di partenza (bagno/specchio/telefono), probabilmente per un'interferenza del sistema di
      raccomandazione preset di Higgsfield ("IN THE DARK" si attivava sul prompt col diner/neon).
      Anche il video riuscito aveva un problema più di fondo: pelle e denti troppo lisci/perfetti,
      lettura da "generato" anche a scena corretta — un tentativo di correggerlo con linguaggio
      esplicito da realismo (grana fotocamera telefono, texture pelle imperfetta, non patinato) era
      in corso quando si è deciso di fermarsi. **Conclusione: il modello video attuale non è ancora
      abbastanza affidabile/realistico per l'apertura delle pagine** — le foto invece hanno retto
      bene tutta la giornata (identità stabile, texture credibile). Si riprende il video in futuro,
      quando i modelli migliorano o si vuole investire più tempo nel debug; **per ora si procede
      solo con contenuto fotografico** per aprire Instagram/TikTok.
- [x] **Aggiornamento stesso giorno: il video torna nel banco di lancio, ma solo con Seedance 2.5 +
      storyboard + de-slop, mai Kling per il parlato** (23/9): la pausa sopra è durata poco — Kling
      non era il problema di fondo, era la tecnica usata. Scrollcraft produce già tutti i suoi video
      con Seedance 2.5, quindi il modello è affidabile; il primo test con Seedance però era stato
      fatto scorciando il metodo (una sola foto di riferimento + testo lungo, senza storyboard),
      risultando comunque innaturale. Rifatto con la tecnica completa e validata: storyboard a 3
      pannelli (gpt_image_2) → de-slop obbligatorio (seedream_v5_pro, prompt esatto del workflow
      `ugc-review-video`) → video finale (`seedance_2_5`, `mode: "omni_reference"`,
      `generate_audio: true`, **9:16, 720p** — mai più dimenticare l'aspect ratio, è già successo
      una volta e ha sprecato 70 crediti in un video orizzontale inutilizzabile). Risultato: identità
      stabile, movimento naturale, buono. **Unico avvertimento da tenere per ogni script futuro:
      calcolare le parole rispetto alla durata reale** (~2,5 parole/secondo a ritmo naturale) — il
      primo tentativo aveva uno script troppo lungo per i 10s dati, risultato in un parlato innaturalmente
      veloce; corretto accorciando il testo, non allungando la durata (costa di più). **Banco di
      lancio finale: 6 foto + 2 video da 10s = 8 contenuti**, dentro il target 8-12. Budget: partiti
      da 415 crediti nella sessione video di oggi, restano circa 118.
- [x] **Tolti i brand/prodotti reali dai 55 concept (23/9)**: il primo banco di 6 foto di prova ha
      mostrato che i concept con un prodotto reale finivano centrati sul flacone come una
      pubblicità — punto sollevato in chat ("stiamo costruendo un personaggio, non facendo
      pubblicità"). Tutte le righe che citavano un brand sono state riscritte generiche/in astratto,
      la banca degli 11 prodotti reali resta come riferimento dormiente, non più assegnata di
      default. Vedi note in "Pilastri di contenuto" e "Banca prodotti reali".
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
- [ ] **Idea futura: mini-serie "Palm Springs" (non prioritaria, pianificata il 23/9)** — vlog-style
      in 3 post separati (non un video unico, il tetto di 30s/generazione lo impedirebbe comunque):
      1. Arrivo al motel vintage midcentury (Ossessioni, ~15-18s, scende dal Maggiolino, foulard/
         occhiali oversize, entusiasmo genuino)
      2. Piscina midcentury, costume vintage anni '60, poco/nessun parlato (Estetica, ~18-20s,
         editoriale/sicura di sé, non esplicito — vedi nota sotto sul perché)
      3. Gelato che cola mentre prende il sole, reazione teatrale deadpan (Assurdo, ~15-18s, stesso
         registro "documentario applicato a niente" del video del contagocce)
      **Nota su "sexy" (23/9)**: richiesta esplicita di un corpo "molto sexy" — rifiutato di
      reinventare il corpo (resta quello fissato nell'Elemento `skincare-creator-v2`, mai rigenerato)
      e di spingere verso contenuto esplicito: rischio concreto di penalizzazione/rimozione su IG e
      soprattutto TikTok per un account ancora senza base di follower. Tenuto un registro
      editoriale/sicuro di sé (stesso tono della foto alla toeletta anni '20), non esplicito.
      **Vincolo tecnico**: location con testo/insegne in lingua straniera scartate (rischio "AI slop"
      sul testo, già visto coi caratteri latini figurarsi con altri sistemi di scrittura) — per questo
      scelta una destinazione USA (Palm Springs, non un paese estero), coerente anche con l'identità
      già newyorkese/americana di Sienna. Costo stimato ~140 crediti a scena a 720p — da fare quando
      il budget lo permette, non con gli ultimi ~5 crediti di oggi.
- [ ] Definire Personaggio 2 (non ancora iniziato)
- [ ] **Prossimo batch di concept da scrivere secondo la correzione di peso del 25/9** (vedi
      "Correzione pesi pilastri e stile — confronto con Lil Mayo"): più Assurdo (25-30%), meno
      Estetica (15-20%), stile candid per almeno metà delle righe, comparse che reagiscono dove la
      location lo permette, taccuino/matite come secondo segno visivo ricorrente anche fuori dal
      pilastro Random. Non ancora scritto, i 55 concept attuali restano validi per l'uso corrente.

## Produzione mini-serie "Palm Springs" — vlog cinematografico (24/9)

Ripresa dell'idea sospesa sopra (vedi "Prossimi passi", 23/9), portata in produzione reale.

**Banco foto Palm Springs (24/9, prima della sessione vlog)**: 6+ foto generate con
`skincare-creator-v2`, approvate: salto in piscina (`6849a0b3-7d12-4d57-94c5-1aeed5435ff4`), uscita
dal diner al neon (`c1a21c83-e170-41cd-960c-b5a1ee631204`), gelato che cola (`25b44362-aad7-48b5-
9a52-e87dea4284e9`), parete neon (`3f16fafb-b364-435a-9640-00f3dbd191a5`). Formato 4:5, non 9:16 —
**da ricontrollare/rigenerare in 9:16 prima di usarle come frame di partenza video**, disallineamento
non ancora risolto.

**Decisione di formato (24/9)**: niente più piano-sequenza singolo alla Kling. Vlog da 45s = **8
shot separati da 4-7s cuciti in Final Cut dall'utente** (non da noi), non un'unica generazione lunga
(cap tecnico Seedance 30s comunque lo impedirebbe). Shot list completa (scena piscina + scena
diner/gelato, inquadrature/luce/camera per ognuno) discussa e approvata in chat il 24/9 — **da
trascrivere qui per intero alla prossima sessione**, non ancora fatto.

**Regola nuova: niente più selfie POV.** Su richiesta esplicita, tutta la sequenza è girata come da
operatore esterno (documentario/movie), non telefono in mano — coerente con l'osservazione che un
telefono in scena è comunque un rischio (vedi punto 3 nella ricetta Kling sopra, anche se lì per
motivi di continuità oggetto, non di stile). **Regola aggiuntiva**: mai un operatore/ombra/riflesso
di chi filma visibile in scena, salvo che non abbia un senso narrativo — non ancora definito un
personaggio "amico che filma", quindi per ora sempre invisibile per convenzione cinematografica.

**Lezioni tecniche nuove (24/9)**:
- **Mai scrivere il dialogo in italiano nel prompt** anche se la conversazione in chat è in
  italiano — Sienna è un personaggio americano (vedi character bible), il modello sintetizza la
  lingua letterale del prompt. Già successo una volta, riconosciuto e corretto.
- **`audio_references` con un job_id di un video intero non funziona** (422 "mode omni_reference
  requires at least one reference media item" prima, poi 422 generico dopo aver aggiunto il ref)
  — il campo si aspetta un audio isolato già estratto/caricato (`media_confirm(type='audio')`), non
  un video. **Non esiste ancora una voce clonata/ancorata per Sienna** nonostante i video precedenti
  la facciano parlare — quella voce è sintetizzata al volo dal modello ogni volta dal testo del
  prompt, mai salvata come asset. Per un vero voice-lock servirebbe `create_voice_from_confirmed_
  audio` con un file audio isolato (costo di clonazione extra, non ancora fatto) — rimandato:
  non conviene per un solo video con 2 battute, da rivalutare se il formato "Sienna che parla"
  diventa ricorrente.
- **Filtro NSFW su `nano_banana_2`/`nano_banana_flash` sembra reagire all'inquadratura, non al
  costume**: stesso bikini nero (`plain solid black triangle bikini`, già usato senza problemi nelle
  foto approvate) bloccato ripetutamente su primi piani/campo medio ravvicinato ("mouth open
  mid-speech", "water level", "eyes closed"), passato senza problemi appena allargato a campo
  largo/campo medio-largo con soggetto a distanza. **Non risolvere cambiando il costume** (rischio
  di finire su un costume "da nonna" fuori personaggio, già successo e corretto) — risolvere
  allargando l'inquadratura o ammorbidendo il fraseggio sul volto/corpo.
- **Costo Seedance 2.5 per risoluzione, confermato 24/9**: ~3 crediti/sec a 480p, ~7/sec a 720p,
  ~12/sec a 1080p — lineare, coerente col punto 11 sopra. **480p poi upscale non conviene**: costo
  upscale non prevedibile (nessun `get_cost` su quello strumento) e comunque parte da un source
  480p — soffitto qualitativo più basso di un 720p nativo, a parità di costo stimato. Deciso: 720p
  diretto per contenuto che deve sembrare reale (facce/pelle/acqua in primo piano).
- **Job in coda ancora cancellabile senza addebito**: dalla UI web (hover sul tile → Cancel) finché
  è in stato "queued"; se già "processing" e fallisce, rimborso automatico comunque. Nessun tool
  MCP equivalente disponibile per farlo da qui.

**Stato al 24/9 (sessione interrotta, da riprendere)**: shot 1 (piscina, arrivo, battuta in inglese,
720p) generato con successo (job `579939d2-1b96-4633-a26c-40a92a97428a`, non ancora verificato/
mostrato). 5 storyboard di riferimento per gli shot 1/3/4/6/8 generati e approvati (dopo correzione
costume). Shot 2/5/7 usano le foto Palm Springs già approvate come frame di partenza. **Prossimo
passo concordato**: generare 1 shot pilota completo (video, non solo storyboard) per validare lo
stile "da operatore" prima di lanciare tutti gli 8 — non ancora fatto.

**Nota 26/9 — chi genera i video**: come da regola nuova in `18-higgsfield-workflow-guida.md`
(sezione 9), i video vanno generati da Massimiliano direttamente sul sito higgsfield.ai (per
sfruttare pass illimitati/tariffa fissa quando conviene), non da Claude tramite i tool MCP —
generare da qui consumerebbe sempre crediti a pagamento anche con un pass attivo. Il ruolo di
Claude su questo shot pilota resta preparare il prompt esatto e gli id di reference da incollare,
non lanciare la generazione.

**Completato 26/9**: Massimiliano ha montato lui stesso in Final Cut il vlog Palm Springs (38s,
piscina all'alba/tramonto + gelato al neon + altre scene), pubblicato su
`digital-business/portfolio/index.html` (`sienna.mp4`, sezione griglia standard, id `sienna`).
Sostituiva un clip sbagliato da 4s finito online per errore (job isolato `48aa8b7b...`, generato
con `duration:4` esplicito — non era un taglio del video giusto, era proprio un'altra generazione).
File originale caricato in `.mov` (H.264 video + audio PCM non compresso) convertito da Claude in
H.264+AAC con `movflags +faststart` prima della pubblicazione, stessa regola già fissata in
`18-higgsfield-workflow-guida.md` sezione 8. Nota tecnica: **`ffmpeg` non è installato come
binario di sistema in questo ambiente, ma il pacchetto Python `imageio-ffmpeg` lo include** —
eseguibile trovato via `python3 -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"`,
utilizzabile per future conversioni quando serve senza dover installare altro.

## Esperimento "spin/reveal" Genjutsu (26/9) — accantonato

Test di motion transfer (Higgsfield Genjutsu) partendo da un video di riferimento trovato online
(soggetto anime che ruota su un piedistallo, sfondo a gel colorato ciclico) per recastare Sienna
sopra. Due tentativi fatti da Massimiliano sul sito: il primo con espressione/location sbagliate
(errore di prompt di Claude — scritto "studio backdrop" invece del negozio dischi, ed espressione
dimenticata), il secondo non ancora tentato con la versione corretta del prompt. **Decisione presa
da Massimiliano il 26/9: non rigenerare, non ne vale la pena** — è un contenuto accessorio, non
nella lista dei 55 concept né nel banco già pubblicato, e i crediti vanno riservati a produzione
che serve davvero. Non riprendere questa pista salvo richiesta esplicita futura.

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
