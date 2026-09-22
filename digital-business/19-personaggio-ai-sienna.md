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

---

## Character bible — chi è Sienna

**Identità**: donna, metà anni '20. Non è una dermatologa né una professionista sanitaria — è
un'appassionata di skincare che ha passato anni a studiare ingredienti per conto suo, partita da
un percorso personale con la pelle da adolescente (acne, pelle sensibile). Questo la rende credibile
senza farle mai dare consigli clinici personalizzati.

**Personalità**:
- Calda, curiosa, un po' "nerd" sugli ingredienti — le piace leggere INCI list per divertimento
- Onesta fino alla schiettezza: non ha paura di dire che un prodotto virale è sopravvalutato
- Auto-ironica, mostra anche le giornate di pelle brutta, non solo i risultati perfetti
- Diretta e con opinioni nette, mai cattiva o sprezzante verso chi ha gusti diversi

**Voce/registro**: colloquiale, diretta, in inglese americano casual (mercato target USA) —
frasi brevi, qualche intercalare naturale ("honestly", "not gonna lie"), zero linguaggio clinico
o da comunicato stampa.

**Valori non negoziabili**:
- Dichiara sempre di essere un contenuto AI/Scrollcraft quando richiesto o rilevante (bio inclusa)
- Ogni claim su ingredienti/efficacia è verificato con una ricerca reale prima di scrivere lo script
  — mai inventato (vedi discussione del 22/9 in chat: rischio reputazionale e di responsabilità)
- Nessun claim medico o clinico assoluto ("cura", "elimina") — solo informazione generale accettata
- Scettica verso l'hype, mai scettica verso la scienza vera

**Bio account (bozza)**: "AI skincare creator · made with AI by Scrollcraft · sharing what actually
works (and what doesn't)"

---

## Pilastri di contenuto (mix 70/30 confermato da Massimiliano, aggiustato il 22/9 con dati reali)

Ricerca su cosa crea davvero legame con il pubblico (fonti: studi su parasocial interaction e beauty
influencer, vedi note in fondo): **l'attrattiva fisica non è il fattore che spiega il legame con
chi segue un creator — conta l'"attrattiva sociale"** (personalità coinvolgente, sembrare vicini),
e nel settore skincare specifico **il pubblico si fida di chi fa recensioni oneste**, non di chi è
semplicemente bella. La vulnerabilità/onestà su difficoltà reali è il fattore più citato per
costruire fiducia — soprattutto per un account che parte da zero, dove relazionabilità conta più
del polish.

Di conseguenza: il contenuto "vulnerabile" non resta isolato in un pilastro a parte, va intrecciato
anche dentro routine e demo (piccole ammissioni oneste ovunque — "questo non mi ha convinta", "oggi
la pelle fa quello che vuole lei"), non solo confinato al 10% originale.

1. **Routine/lifestyle senza prodotto specifico** (~30%) — routine mattina/sera, cambio stagionale,
   giornata nella vita da skincare-obsessed. Include formato **GRWM (get ready with me)** — tutorial
   + narrazione casual, il formato con più prova di funzionare nel beauty specificamente
2. **Educazione ingredienti** (~20%) — come funziona un attivo, errori comuni di combinazione, SPF
3. **Myth-busting / opinioni nette** (~20%) — "questo trend è marketing, non scienza", hot take su
   prodotti virali — qui la componente "recensione onesta" è centrale, non decorativa
4. **Demo/recensione prodotto specifico** (~20%, la fetta "sponsor-style" dichiarata) — test reale,
   pro/contro onesti, mai solo positivi
5. **Contenuto personale/vulnerabile** (~10% dedicato, ma presente anche trasversalmente negli altri
   4) — giornate di pelle brutta, dubbi, percorso reale

## Formato e lunghezza (aggiornato: pass illimitato Kling cambia i vincoli di costo, non quelli di attenzione)

Anche con generazione illimitata, la lunghezza va decisa per performance sui social, non perché
"tanto è gratis" — un video lungo e abbandonato a metà penalizza comunque nell'algoritmo. Mix:

- **60% brevi (8-15s)**: hook rapido, routine, opinioni, myth-busting — il grosso del volume
- **25% medi (20-40s)**: demo prodotto con più passaggi, prima/dopo, piccoli tutorial
- **15% più lunghi (45-90s)**: approfondimenti su ingredienti, spiegazioni più tecniche — questi
  raddoppiano anche come materiale portfolio/LinkedIn per Scrollcraft, essendo più dimostrativi
- **30-40% del totale in foto/carousel**, non solo video, per varietà e velocità di produzione

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

**Recensioni/demo (il punto sponsor-style, mai solo entusiasmo)**:
- "The formula is genuinely good. The price is not. That's the whole review."
- "It did what it said it would do, which honestly should not be as rare as it is."
- "I wanted to hate this because everyone won't shut up about it. I don't hate it."
- "Three stars. Would repurchase only on sale, and I'm telling you that for free."

**Chiusure/CTA (mai da comunicato stampa)**:
- "That's it, that's the whole tip."
- "Anyway. Use sunscreen. Bye."
- "Tell me I'm wrong, I have time today."

**Regole di scrittura per tutti gli script (da applicare quando si trasformano le 55 righe in
prompt completi)**:
- Frasi brevi, mai un periodo che spiega tre cose insieme
- Almeno un'ammissione onesta/vulnerabile per script, anche nei Demo e Routine, non solo nel
  pilastro Personale (vedi nota sui pilastri sopra)
- Zero superlativi assoluti ("the best", "life-changing") salvo per prenderli in giro
- Se non ha un'opinione netta su qualcosa, meglio non forzarla — la schiettezza selettiva è più
  credibile di un'opinione su tutto

## Prodotti reali per le recensioni (verificati il 22/9 — mai inventare un prodotto o un claim)

Ogni riga "Demo" e le due righe "Myth" che citano un trend/prodotto specifico sono ancorate a un
prodotto vero, con fatti verificati tramite ricerca — non un placeholder. Se in futuro si aggiungono
altri concept di recensione, stesso principio: cercare prima, scrivere lo script dopo.

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

## Lista concept per la giornata di produzione (55)

Formato per riga: **Pilastro | Formato/durata | Location | Outfit | Capelli | Concept/hook**

### Routine / lifestyle (16)

1. Routine | Video 12s | L1 | O4 | H1 | **GRWM**: "My actual 5-step morning routine, no fluff" (+ "step 3 I skip half the time")
2. Routine | Video 10s | L2 | O14 | H4 | "What my skin looks like before any product touches it"
3. Routine | Foto | L4 | O9 | H2 | Scaffale con **CeraVe Moisturizing Cream, The Ordinary Niacinamide, Supergoop! Unseen Sunscreen** visibili, caption sulla routine serale
4. Routine | Video 15s | L3 | O12 | H6 | "Skincare while my coffee brews"
5. Routine | Video 30s | L5 | O6 | H8 | **GRWM sera**, passo-passo, "ngl some nights I just wash my face and go to bed"
6. Routine | Foto | L6 | O13 | H10 | SPF applicata al tramonto, caption su costanza quotidiana
7. Routine | Video 8s | L11 | — (avvolta in asciugamano) | capelli raccolti sotto asciugamano | "POV: skin after a good night's sleep"
8. Routine | Video 20s | L12 | O1 | H3 | Come cambia la routine in inverno vs estate
9. Routine | Foto | L1 | O16 | H9 | Formati da viaggio di **CeraVe Moisturizing Cream** e **The Ordinary Niacinamide**, caption su routine minimal
10. Routine | Video 12s | L9 | O10 | H7 | "Skincare on days I actually leave the house"
11. Routine | Video 10s | L2 | O4 | H5 | "Things I stopped doing to my skin"
12. Routine | Foto | L13 | O17 | H11 | Solo bicchiere d'acqua in mano, nessun integratore mostrato/nominato (evitiamo claim su prodotti non verificati) — caption su idratazione e costanza
13. Routine | Video 15s | L4 | O11 | H1 | "My 2-minute routine on lazy days"
14. Routine | Video 25s | L10 | O9 | H2 | Unboxing con **Paula's Choice 2% BHA** e **Youth To The People Superfood Cleanser**
15. Routine | Foto | L15 | O18 | H3 | Pelle al naturale prima di uscire, caption su fiducia senza trucco
16. Routine | Video 10s | L7 | O5 | H10 | "Reapplying SPF in the car, don't judge"

### Educazione ingredienti (11)

17. Ingredienti | Video 20s | L11 | O7 | H4 | Come funziona la niacinamide, in parole semplici
18. Ingredienti | Video 15s | L5 | O3 | H9 | Errore comune: mischiare retinolo e vitamina C
19. Ingredienti | Foto | L1 | O16 | H6 | Etichetta INCI reale di **The Ordinary Niacinamide** con evidenziatore, caption didattica
20. Ingredienti | Video 30s | L2 | O6 | H8 | Perché l'SPF va usato anche in casa
21. Ingredienti | Video 18s | L3 | O12 | H1 | Differenza tra esfoliante chimico e fisico
22. Ingredienti | Video 12s | L4 | O9 | H2 | "The ingredient everyone's obsessed with right now, explained"
23. Ingredienti | Foto | L12 | O1 | H5 | **CeraVe Moisturizing Cream** vs **Youth To The People Superfood Cleanser** a confronto, caption su come leggere le etichette
24. Ingredienti | Video 25s | L11 | O17 | H7 | Come costruire una routine da zero, ordine corretto
25. Ingredienti | Video 15s | L5 | O11 | H10 | Cos'è davvero la "barriera cutanea"
26. Ingredienti | Video 10s | L1 | O7 | H3 | Mito: "più costoso = meglio"? Spiegazione breve
27. Ingredienti | Foto | L9 | O13 | H11 | **Supergoop! Unseen Sunscreen** in borsa al parco (stesso prodotto del concept 44, la porta sempre con sé), caption su riapplicazione

### Myth-busting / opinioni (11)

28. Myth | Video 12s | L10 | O3 | H9 | "Trend che non funzionano come TikTok dice"
29. Myth | Video 15s | L1 | O9 | H4 | "I tried the viral slugging trend, honest results" — **Vaseline**, con il vero avvertimento dermatologico: non per pelle acneica
30. Myth | Video 10s | L3 | O12 | H6 | Hot take: il "clean girl" skincare è più hype che scienza
31. Myth | Foto | L12 | O1 | H2 | **Bubble Skincare Slam Dunk** — caption scettica ma onesta: idrata bene ma non è un trattamento
32. Myth | Video 20s | L4 | O6 | H8 | Perché il "purging" non è sempre quello che pensi
33. Myth | Video 12s | L5 | O17 | H1 | "Prodotti che TikTok ama ma io no" — solo a parole, nessun prodotto specifico mostrato in scena
34. Myth | Video 15s | L6 | O18 | H3 | Reagisce a un consiglio virale di skincare, al tramonto
35. Myth | Foto | L11 | O7 | H5 | **The Ordinary Niacinamide ($6)** vs **Glow Recipe Dew Drops (fascia alta)** — confronto prezzo/efficacia reale, caption diretta
36. Myth | Video 18s | L2 | O14 | H7 | Perché "natural" non vuol dire automaticamente sicuro
37. Myth | Video 10s | L13 | O11 | H10 | "Unpopular skincare opinion" formato rapido
38. Myth | Video 25s | L1 | O9 | H11 | Debunk di un mito virale specifico, con fonti

### Demo/recensione prodotto (11)

39. Demo | Video 20s | L4 | O16 | H4 | **The Ordinary Niacinamide 10%+Zinc 1%** — prima applicazione, reazione onesta
40. Demo | Video 15s | L5 | O1 | H9 | **The Ordinary Granactive Retinoid 2%** vs **Mario Badescu Drying Lotion** — chiarisce la differenza: uno è un trattamento anti-età da usare su tutto il viso, l'altro uno spot treatment mirato solo sui brufoli, non sono intercambiabili
41. Demo | Foto | L11 | O7 | H2 | **CeraVe Moisturizing Cream** — texture ricca in primo piano, ceramidi spiegate
42. Demo | Video 30s | L1 | O6 | H6 | **Bubble Skincare Slam Dunk** — routine completa economica con questo come protagonista
43. Demo | Video 12s | L12 | O9 | H1 | **The Ordinary Granactive Retinoid 2% Emulsion**, un mese dopo — contro reale: più forte della versione in Squalane, ha dato irritazione iniziale nonostante il nome "delicato"
44. Demo | Foto | L15 | O18 | H3 | **Supergoop! Unseen Sunscreen** in borsa prima di uscire, caption su riapplicazione
45. Demo | Video 18s | L4 | O17 | H8 | **Glow Recipe Watermelon Dew Drops** — pro/contro onesti (profumo forte, risultati non per tutti)
46. Demo | Video 10s | L2 | O11 | H5 | **Paula's Choice 2% BHA** — reazione al primo utilizzo
47. Demo | Foto | L3 | O12 | H10 | **Youth To The People Superfood Cleanser** — caption sulla formulazione "natural-leaning"
48. Demo | Video 15s | L1 | O3 | H7 | **Laneige Lip Sleeping Mask** — "would I repurchase this?" onesto, non scontato
49. Demo | Video 25s | L5 | O13 | H11 | **Mario Badescu Drying Lotion** — il rituale iconico passo-passo: NON si agita, si intinge il cotton fioc solo nel sedimento rosa sul fondo e si applica a puntini prima di dormire

### Personale/vulnerabile (6, ma intrecciato anche sopra)

50. Personale | Video 15s | L2 | O14 | H4 | "Bad skin day, being honest about it"
51. Personale | Foto | L11 | — (viso pulito, senza trucco) | H12 | Pelle al naturale senza filtro, caption su accettazione
52. Personale | Video 12s | L5 | O6 | H8 | Come gestisce uno stress-breakout
53. Personale | Video 20s | L9 | O13 | H7 | Il suo percorso con l'acne da adolescente, breve racconto
54. Personale | Foto | L12 | O4 | H1 | Specchio, caption su costanza e pazienza con la pelle
55. Personale | Video 15s | L1 | O9 | H2 | "What actually helped me, not what I wish worked"

---

## Prossimi passi

- [ ] Aprire il pass illimitato Kling 3.0 1080p (35€/24h) su Higgsfield quando pronti a produrre
- [ ] Trasformare ogni riga sopra in un prompt completo (ancorato all'elemento `skincare-creator`)
      solo al momento della produzione, non prima — evita di scrivere 55 prompt completi che
      potrebbero cambiare
- [ ] Durante la produzione: controllo qualità per coerenza volto e assenza di artefatti,
      aspettarsi scarto 20-40%
- [ ] **Attenzione extra sulle mani** (verificato 23/9): il video di riferimento usato per Sienna era
      generato con Seedance 2.5, ma in produzione useremo Kling 3.0 (per il pass illimitato). Kling 3.0
      è forte su fotorealismo/coerenza volto (migliorato molto rispetto a 2.6), ma ha un difetto noto e
      documentato su mani/dita/oggetti in mano durante il movimento ("floating arms, morphing hands").
      Molti concept della lista sono esattamente "tiene il prodotto", "applica sul viso", "intinge il
      cotton fioc" — quindi scarto atteso più alto del solito su questi, controllare le mani per prime
      in fase di QC, non solo il volto.
- [ ] Definire Personaggio 2 (non ancora iniziato)

---

## Fonti (personalità/attrattiva per il pubblico, verificate 22/9)

- UAB — studio su personalità e efficacia degli influencer: autenticità, vulnerabilità, fiducia
- Studio su parasocial interaction e beauty influencer: l'attrattiva fisica non predice il legame
  parasociale, conta l'attrattiva sociale/onestà nelle recensioni; formato GRWM citato come il più
  efficace per intimità parasociale nel beauty specifico
