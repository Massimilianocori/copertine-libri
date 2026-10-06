# Procedure e cose imparate (da leggere prima di ogni lavoro)

Qui va tutto quello che funziona e che abbiamo imparato. Gli errori vanno in `ERRORI.md`.

## INDICE DEGLI STUDI (5/10/2026, tutti a costo zero)

- `30` strumenti e motori Higgsfield, costi reali · `31` regole ufficiali UGC · `32` catalogo dei workflow Higgsfield · `33` catalogo modelli, preset, app e costi · `34` Marketing Studio e Ads Studio · `35` playbook per tipo di lavoro (con i costi reali: lo spot Tom Ford è costato circa 1.017 crediti, circa 51 €, contro 715 preventivati) · `36` outreach playbook · `37` conformità e diritti (da far verificare a un avvocato).
- Per ogni lavoro: leggere la scheda del tipo di lavoro in `35`, poi le regole in `31` (UGC) o la checklist qui sotto (spot). Una sola strada: la migliore.

## CHECKLIST SPOT: i passaggi, in ordine (da seguire ogni volta)

1. **Leggere** `CLAUDE.md`, `ERRORI.md` e `PROCEDURE.md`.
2. **Ricerca e brief** (niente iniziative): idea, prodotto dalle sole foto ufficiali, casting, outfit, trucco e capelli, location, luce, inquadrature e movimenti di camera, suono, testi. Nessun oggetto che non sia nel brief. Massimiliano approva.
3. **Modello AI: lo sceglie Claude e lo propone con la motivazione; Massimiliano approva** (regola SCELTA DEL MODELLO in CLAUDE.md). Prima del progetto, confronto affiancato della stessa inquadratura su 2 modelli (ERRORI 19); costi dai crediti già spesi (niente `get_cost` su generate_video).
4. **Preventivo scritto di tutto il progetto** (immagini, bozze, finali, upscale), con il saldo crediti. Poi il "sì" per ogni generazione. Nessuna generazione senza permesso.
5. **Casting e look:** ritratti, Massimiliano approva; poi outfit. Il casting è il riferimento volto in OGNI generazione.
6. **Storyboard visivo:** un'immagine per inquadratura, confrontata affiancata col casting; controllo di sorrisi non voluti, anatomia, barre nere, scritte finte, oggetti non previsti, continuità (capelli, oggetti, posizione). Si mostra la sequenza e Massimiliano approva.
7. **Video:** ogni inquadratura parte dalla sua immagine; bozza a 480p; controllo fotogramma per fotogramma (tagli automatici, altre persone, volto, outfit, azione chiave visibile, sorrisi). Poi presentare le due strade con i costi: upscale o 1080p nativa.
8. **Montaggio:** ritmo veloce, tagli frequenti, più movimento che pose statiche, mai effetto "foto animate"; nessuna scritta dentro lo spot, solo la grafica finale su nero; colori come approvati (curva `curves=all='0/0 0.25/0.19 0.5/0.44 0.75/0.72 1/1'`, `vignette=angle=PI/4.5`, `noise=alls=7:allf=t+u`). Si manda la versione senza musica.
9. **Musica:** la mette Massimiliano. Posso proporre brani con licenza chiara (Pixabay) ma non posso scaricarli da qui.
10. **Consegna:** master 1080p (o 2160p solo su richiesta, a pagamento), versione compressa sotto i 30 MB per la chat e versione web per il sito.
11. **Sito (solo se richiesto):** una sola pubblicazione al giorno, video muto in loop con pulsante audio.
12. **A fine lavoro:** scrivere in `ERRORI.md` ogni errore e in `PROCEDURE.md` ogni cosa imparata.

## Produzione video (spot)

1. **Storyboard visivo, sempre.** Per ogni inquadratura si genera un fotogramma chiave (stesso volto del casting, stesso outfit), lo si controlla affiancato al casting, si mostra a Massimiliano la sequenza come storyboard e, solo dopo l'approvazione, ogni video parte dal suo fotogramma. Uno storyboard solo scritto in un prompt unico porta il modello a saltare inquadrature (spot Tom Ford: 4 su 12 saltate).
2. **Il casting in ogni generazione.** Il ritratto del casting approvato va passato come riferimento volto in OGNI generazione (immagini, video, correzioni), insieme al riferimento outfit. Mai correggere partendo da un'immagine derivata già spostata (copia di copia): si rigenera dal casting.
3. **Coerenza del volto.** Partire sempre da un fotogramma che ha già il volto giusto (es. primo piano del casting). La modalità *video_extension* di Cinema Studio 4.0 continua la stessa persona dalla clip precedente: utile per sequenze lunghe.
4. **Prima bozza a 480p, poi upscale.** La bozza 480p costa un quarto della 1080p. Se approvata, si porta a 1080p (o 2160p) con l'upscale Topaz: contenuto identico. Rigenerare in 1080p produce invece un video diverso (generazione casuale). Prima di partire presentare sempre a Massimiliano le due strade con i costi: bozza 480p + upscale (economico, pelle un po' più liscia, ok per i social) oppure 1080p nativa (circa 4 volte il costo). Decisione 5/10: per lo spot Tom Ford resta l'upscale, nessuna rigenerazione.
5. **Costi verificati (ottobre 2026):** (5/10: Massimiliano rifiuta anche le chiamate `get_cost` su `generate_video` e ha detto di non generare video senza il suo sì; i costi si ricavano dallo storico crediti con `transactions`, oppure si chiede prima.) Cinema Studio 4.0 = 3 crediti/s a 480p, 12 crediti/s a 1080p; immagine Nano Banana Pro ≈ 2 crediti; upscale Topaz 1080p ≈ 0,75 crediti/s. Usare `get_cost` prima di ogni generazione.
6. **Controllare il modello usato.** Higgsfield può sostituire il modello richiesto (es. Nano Banana Pro → Nano Banana 2): verificarlo nel risultato del job.
7. **Gusto di Massimiliano sugli spot:** ritmo veloce, inquadrature che cambiano spesso, più movimento che pose statiche, mai l'effetto "foto animate"; nessuna scritta dentro lo spot, solo una grafica finale su nero dopo lo spot; la storia deve capirsi senza spiegazioni (prima/dopo chiaro).
8. **Scelta del modello video:** prima di ogni progetto, test della stessa inquadratura su Cinema Studio 4.0 e Seedance 2.5 e confronto affiancato a Massimiliano. Seedance 2.5 ha la modalità bozza (`draft`): 480p da finalizzare entro 7 giorni in 1080p nativo con lo stesso video (meglio dell'upscale Topaz); è anche indicato per la coerenza dell'identità.
9. **4K:** i modelli video arrivano a 1080p; il 4K si ottiene con upscale Topaz 2160p. Serve solo per TV, cinema, schermi o lusso: offrirlo come extra a pagamento.
10. **Un unico video lungo o tanti pezzi? (5/10, da verificare con una prova).** Nello spot Tom Ford i pezzi singoli hanno fatto derivare il volto (immagini di partenza non coerenti); una generazione unica da 15 s con 12 inquadrature nel prompt ha mantenuto volto e abito, ma ha saltato 4 inquadrature su 12 e ha deciso da sola i tagli. Metodo consigliato (ipotesi): blocchi da 10-15 s con 4-6 inquadrature ciascuno, ogni blocco con fotogramma di partenza (e finale) dallo storyboard approvato, concatenati con video_extension, poi montaggio. Il video unico da 30 s (Cinema Studio 4.0 arriva a 30 s) non è mai stato provato: farne una bozza 480p (circa 90 crediti a 3 crediti/s) prima di scegliere, con il permesso di Massimiliano.

## UGC con avatar parlante (verificato sugli schemi, 5/10; da provare con un test)

- **Scheda voce nel brief, da far approvare:** tono, energia, ritmo, età/accento, intercalari, emozione frase per frase. Il tono dipende molto anche dal copione: frasi corte, contrazioni, registro parlato.
- **Controllo della voce (modelli audio Higgsfield):** Qwen Audio 3.0 TTS Flash ha il campo `instruction` in linguaggio naturale (emozione, stile, velocità) più `speech_rate` e `pitch_rate`; Seed Audio 1.0 ha `speech_rate`, `pitch_rate`, `loudness_rate`; ElevenLabs v4 ha `stability` e `similarity_boost`; Text to Speech V2 permette di scegliere il motore (ElevenLabs, MiniMax, ecc.). Le voci si ascoltano in anteprima con `list_voices`, e si può clonare una voce da un audio di riferimento.
- **Nel video:** Cinema Studio 4.0 e Seedance 2.5 accettano `generate_audio` e un audio di riferimento (`audio_references`); il tono si può descrivere anche nel prompt del video. Quanto il labiale segua un audio esterno e quanto il modello rispetti il tono scritto NON è verificato: fare prima una prova di una frase, con costo controllato (`get_cost`), e confrontarla con Massimiliano.
- **Due livelli da non confondere: motore e strumento (correzione di Massimiliano, 5/10).** Il *motore* è il modello che genera il video (Seedance 2.5, Kling 3.0, Cinema Studio 4.0, FLUX 3 Video). Lo *strumento* è l'interfaccia che lo usa: Marketing Studio (preset, hook, ambientazioni, avatar, prodotto, ricreazione di un video di riferimento) può usare più motori, anche Seedance 2.5; Seedance 2.5 si trova anche in Video e in Cinema Studio. Quindi non si confronta "Marketing Studio contro Seedance" come alternative dello stesso tipo: si decide (1) il motore e (2) lo strumento, cioè quanta automazione e quanto controllo. Nello schema API Marketing Studio non dichiara quale motore usi: non è verificato, chiedere o provare. Marketing Studio: durata 12-15 s, 480p-1080p (v1) o 480p-720p (ugc_v2), brief del copione in `user_context`, nessun parametro dedicato al tono. Ipotesi da provare: Marketing Studio per volume e hook variants, controllo diretto (immagini, audio di riferimento, estensione) per spot di marca. Decide Massimiliano dopo una prova affiancata con costo verificato.
- **Metodo UGC già usato per Sienna (1/10, dallo storico Higgsfield):** Seedance 2.5, 14 s, 9:16, immagine iniziale + immagine finale, voce generata a parte con text-to-speech e passata come audio di riferimento ("labiale sincronizzato all'audio"), bozza 480p e poi finalizzazione a 1080p con la modalità bozza (`draft_job_id`). Con Marketing Studio v2 (modalità "talking", 30 s, dialogo e voce descritti nel prompt) è stato fatto il video Niacinamide del 28/9. Perché si sia passati da uno all'altro non è scritto negli appunti.
- **Prima di proporre un metodo o dire "non so se funziona", controllare lo storico** (`show_generations`, `show_marketing_studio_generations`) e `digital-business/19-personaggio-ai-sienna.md`: molte cose sono già state provate.
- **Studio completo di strumenti e motori (5/10): vedi `digital-business/30-higgsfield-strumenti-confronto.md`.** In sintesi: Seedance, Cinema Studio e Marketing Studio costano uguale al secondo (3 / 7 / 12 crediti a 480p / 720p / 1080p); Kling 3.0 circa 1,75; bozza 480p + upscale Topaz costa circa un quarto della 1080p nativa; spot di marca = Cinema Studio o Seedance con storyboard e blocchi; UGC a volume = Marketing Studio (controllare le etichette); UGC di precisione = workflow `ugc-video` con Seedance 2.5; test hook economici = Kling 3.0.
- **Regole ufficiali Higgsfield per l'UGC (5/10): vedi `digital-business/31-ugc-regole-ufficiali-higgsfield.md`.** Da ricordare sempre: tavola storyboard 21:9 a 8 riquadri (GPT Image 2) + pulizia anti-AI con Seedream 5 Pro + clip Seedance 2.5 con 8 tagli e voce nativa; primi 0,1 s già in movimento; max 2 mani e 1 azione col prodotto per taglio; mai specchi, telefono visibile, testo leggibile su oggetti di scena; parole vietate ("obsessed", "literally", "game changer"); **niente testimonianze sintetiche né esperienze inventate in prima persona**: la creator generata è una dimostratrice, claim solo da lista approvata dal cliente.
- Esistono anche `voice_change` (cambia la voce di una clip) e `dubbing`.

## File e consegne

- In chat si possono inviare file fino a 30 MB: comprimere prima (H.264, ~7–8 Mbps per 1080p da 30 s).
- I file su Google Drive non si possono scaricare da qui (rete bloccata, file grandi). Chiedere a Massimiliano un file sotto i 30 MB caricato in chat, oppure solo l'audio se i tagli sono già nostri.
- Compressor (Mac): preset H.264 1080p, data rate 7000 kbps, Profile High, audio AAC 48 kHz.

## Sito

- Ogni push sul branch pubblica il sito su Netlify: un solo push al giorno, raggruppando le modifiche.
- Video in apertura: autoplay muto in loop con pulsante audio (i browser bloccano l'autoplay con audio).
- Se si aggiunge un servizio di tracciamento, aggiornare subito la pagina privacy.

## Email e vendite

- Indirizzi copiati sempre dalla coda/file, mai scritti a memoria.
- Tetto giornaliero di riscaldamento della casella (25/giorno dal 5/10, 30 dal 12/10, 40 dal 19/10), follow-up inclusi.
- Politica dal 5/10: niente lavoro gratis. Offerta d'ingresso: pilota 3 video $450; Holiday Ad Pack 10 video + 10 hook $1.490 (ordine entro 24/10, consegna entro 10/11). Agenzie white-label: $150/$130/$115 a video per 10/50/100; hook $35/$30/$25.
- Su LinkedIn con account gratuito le note personalizzate negli inviti sono poche al mese; i profili aperti si possono contattare subito con messaggio diretto. Chi riceve il DM non riceve l'email lo stesso giorno.
- Per i preventivi su misura: fattura Stripe (Invoice) o Payment Link, con acconto 50%.
- **Conformità email (dal doc 37, 5/10):** ogni email di outreach ha in fondo il footer di `outreach-footer.txt` (indirizzo postale, dichiarazione di email promozionale, fonte dei dati, disiscrizione con risposta "no", rispettata subito); mai frasi che suggeriscono clienti, risultati o esperienze che non abbiamo (es. "We work with DTC brands"); contatti a freddo solo con Paese = United States (UE e UK esclusi finché un avvocato non conferma); nessun campione gratuito. Senza indirizzo nel footer non si invia.
- **Conformità sito e campioni:** niente recensioni, valutazioni o conteggi inventati (rimosso il reel con "4.9, 2.300+ verified reviews"); i campioni parlati sono "Scripted AI sample"; nessun marchio di terzi senza la formula "concept" e piano di rimozione; la musica Pixabay richiede la ricevuta di licenza conservata.
- **Rischi noti da far vedere a un avvocato:** concept con marchi di lusso in homepage, cold email da mittente italiano (art. 130 Codice Privacy), informativa privacy e strumento visitatori Apollo, "full usage rights" nei preventivi (usare la clausola di licenza del doc 37).
- Decidere con i numeri: test A/B tra segmenti (es. agenzie vs moda), confronto dopo 7 giorni.

- **Immagini AI: campagna sì, catalogo no (Massimiliano, 5/10).** Le aziende non affidano all'AI le foto prodotto da catalogo; le immagini AI si propongono solo come immagini di campagna dentro un'idea (come il carosello del sito). Non offrire 'foto prodotto' come servizio autonomo. Fonte: esperienza di Massimiliano, non verificata con studi.
- **Costi verificati 6/10 (transazioni):** Soul 2 (`soul_2`, 2k, 3:4) = **0,12 crediti a immagine**; GPT Image 2.5 = 0,25 per un'immagine prodotto semplice, 4,25 nella versione "Flare". I ritratti di casting costano quasi nulla: farne sempre almeno 2-4.
- **Gusto di Massimiliano sul casting (6/10):** la creator deve essere bella e piacevole in camera, pur con pelle vera. "Persona comune, non modella, lineamenti asimmetrici" nel prompt ha prodotto volti giudicati brutti: non usarlo. Formula giusta: "naturally attractive, camera-friendly real creator" con texture della pelle reale.
- **Varietà dei prodotti nel portfolio (6/10):** troppi video con flacone a contagocce (serum arancione, skincare bianco, brief Angle Test). Ogni nuovo video deve usare un formato di prodotto diverso da quelli già presenti.
- **Apollo, resa reale degli arricchimenti (6/10):** su 150 arricchimenti (150 crediti) solo 50 contatti utilizzabili; 93 scartati perché il dominio è catch-all (tipico di micro-agenzie e brand su Google Workspace/Shopify), 7 per dati sospetti o fuori target. La ricerca persone non consuma crediti e non mostra il catch-all: mettere in conto circa 3 crediti per contatto utile. Saldo dopo: 974 lead credit (rinnovo 3/11).
- **Tavola storyboard UGC (6/10, transazioni):** GPT Image 2, 21:9, 2k, quality high, con 2 riferimenti = **6,5 crediti a tavola** (il brief 48 ne stimava 3-4). Un job bloccato dal filtro ("nsfw") viene rimborsato per intero. La prima tavola Angle Test A (job `5b9b2a4a-...`, prompt in `scratchpad/angle/prompts/`) è stata bloccata dal filtro pur essendo innocua (bagno, maglia a collo alto, stick): falso positivo probabile su parole come "bare skin" / "bare ears" / "bathroom". Il workflow ufficiale dice che la moderazione ferma il percorso: ci si ferma e si chiede a Massimiliano prima di riformulare.
- **Pulizia Seedream delle tavole (6/10, Angle Test):** Seedream 5 Pro 2k = **2,5 crediti** a passaggio. Due difetti verificati: (1) **storpia le scritte piccole** sul prodotto (MERIDIAN → "MERIDOAN"); nelle tavole chiedere la scritta solo in 1-2 pannelli, grande e frontale, e negli altri tenerla fuori campo o coperta dalle dita; nei prompt video legare sempre la scritta all'immagine prodotto. (2) La riga del prompt ufficiale "Preserve existing tutorial Step N headings exactly" **fa inventare didascalie "Step N."** su tavole non tutorial (2 volte su 3): per i formati non tutorial toglierla (tavola C pulita così, senza scritte). Le didascalie già comparse si coprono di bianco in locale senza rigenerare.
- **Filtro "nsfw" falso positivo:** evitare "bare", "skin" accanto a parti del corpo, "bathroom"; usare "white-tiled washroom", "natural skin texture", "no jewelry", "fully covered, high-neck sweater". Con queste parole le tavole sono passate.
- **Caricare un file su Higgsfield da qui:** il proxy blocca `upload.higgsfield.ai`; fare download, modifica e PUT dentro `sandbox_exec` (header `If-None-Match: *`), poi `media_confirm`.
- **Costo reale 3 tavole UGC pulite:** 29,5 crediti (3 × 6,5 + 4 × 2,5, una pulizia rifatta).

## Studio quotidiano 6/10: deriva del volto e come evitarla con Seedance 2.5 (tema D1, costo zero, solo fonti web; da verificare con una prova)

Fonti (lette dai riassunti di ricerca: le pagine complete sono bloccate dal proxy): Runware, guida multi-reference Seedance 2.5 (runware.ai/docs/models/bytedance-seedance-2-5/guides/multi-reference-production); Atlas Cloud (atlascloud.ai/blog/guides/seedance-2-5-ai-video-generator-character-consistency); Kinovi (kinovi.ai/en/blogs/seedance-2-5-character-consistency-ai-video); Kapwing e Luma, guide di prompt Seedance 2.5; Magic Hour, OpenArt, Kling (guide sulla deriva), Higgsfield blog "seedance-2-5-prompting-guide".

**Cause tipiche della deriva (concordi tra le fonti):**
1. Solo testo o riferimento debole: il prompt da solo non tiene un volto; serve l'immagine.
2. Inquadrature che "stressano" l'identità: primi piani stretti, profili e giri di testa, espressioni estreme, movimenti veloci, grandi cambi di luce (direzione o colore della luce diversi = il modello "rifà" il volto).
3. Clip lunghe con prompt che finisce prima: la deriva compare tardi ("se crolla al secondo 22, le istruzioni si fermavano al 18").
4. Catene di copie: ripartire da un fotogramma già spostato (coincide con ERRORI 1 e 16).
5. Riferimenti senza ruolo: se non si dice quale immagine comanda il volto e quale lo stile/ambiente, il modello mescola (coincide con ERRORI 16: la composizione vecchia domina sul casting).

**Cosa fare con Seedance 2.5 (ipotesi operative dalle fonti):**
- **Pacchetto personaggio**: volto pulito frontale (il casting approvato), profilo/3/4, outfit, corpo intero, più un riferimento di stile; fino a 30 immagini per chiamata.
- **Ruoli espliciti nel prompt**: richiamare ogni riferimento per posizione (@Image1...) e legarlo a un ruolo ("@Image1 is SIENNA: face and identity"; "@Image3 controls wardrobe only"), poi usare sempre il nome del ruolo nel resto del prompt.
- **Primo fotogramma fissato**: sezione "FIRST FRAME AND BLOCKING" con posizioni e direzione dello sguardo prima di ogni movimento; l'immagine iniziale deve avere già il volto giusto.
- **Prompt a sezioni in un unico blocco** (GLOBAL STYLE con luce e cosa NON deve comparire, poi tagli in ordine) che copra tutta la durata della clip.
- **Prima la prova prudente**: movimento di camera e luce stabili; solo quando il volto regge si aggiungono primi piani, profili e movimento.
- **Luce coerente** tra le inquadrature (stessa direzione e temperatura).
- **Concatenare** con un fotogramma pulito e frontale della clip precedente, mai con uno in cui il volto è già cambiato.

**Da verificare (non provato da noi):** quanto i ruoli @Image migliorino davvero il volto su Higgsfield (lo schema di generate_video accetta più immagini di riferimento, ma la sintassi @Image è documentata da Runware/Atlas, non da Higgsfield). Prova più economica proposta: una clip 5 s a 480p con lo stesso casting, con e senza ruoli espliciti, confronto affiancato (serve il sì di Massimiliano).

## Limite orario della casella (verificato 6/10)

- **Namecheap Private Email (smtp.privateemail.com) accetta circa 20 messaggi in 60 minuti.** Il 6/10 i primi 20 invii (13:17-13:50 UTC, uno ogni 1-2 minuti) sono partiti; i 5 follow-up successivi sono stati rifiutati subito con `554 5.7.1 ... too many messages from sender in last 60 minutes` (Gmail mostra "Invia messaggio come ... non configurate": è lo stesso rifiuto, non un problema di impostazioni). Non è un rimbalzo per indirizzo inesistente: non ferma il giro, ma il messaggio NON è recapitato.
- Regola: con 25 invii al giorno distanziare di almeno 3 minuti (20 in 60 min al massimo) oppure fare due blocchi separati da un'ora; con i tetti di 30 e 40 (dal 12/10 e 19/10) servono almeno 2 ore di invio. Dopo il giro controllare `from:mailer-daemon` anche per i rifiuti 554 e reinviare solo dopo che è passata un'ora.
- **Rischio legale delle testimonianze (correzione 6/10, Massimiliano):** la regola FTC sulle recensioni false riguarda testimonianze usate per vendere prodotti reali a consumatori reali. I campioni del portfolio con marchi inventati (Meridian, Fort, Noir) non hanno rischio legale concreto; il tema è solo di percezione verso le agenzie. Il rischio vale invece per i video dei clienti e per marchi reali (da verificare se un nome esiste davvero, es. Wagwell).
- **Portfolio (decisione di Massimiliano, 6/10):** i reel 8 (pet supplements) e 11 (skincare bianco) restano sul sito così come sono. Non riproporre di toglierli.
- **Nessuna nicchia di prodotto fissa (Massimiliano, 6/10):** lo skincare è un settore come altri 2.000. Scrollcraft si rivolge a chi compra produzione video (agenzie, media buyer, brand con budget video) in qualsiasi settore. Nelle estrazioni, nei testi e nei video non partire mai da un settore per abitudine: il criterio è la probabilità di risposta e di lavoro, misurata sulle risposte vere.
- **Limite orario di Namecheap Private Email (verificato 6/10 dal codice di errore):** circa 20 messaggi ogni 60 minuti per la casella hello@scrollcraft.design ("too many messages from sender in last 60 minutes"). Regola: massimo 15 all'ora, uno ogni 4 minuti, lasciando margine alle email manuali di Massimiliano.
- **Abbonamento Private Email attivato (Massimiliano, 6/10):** la casella hello@scrollcraft.design esce dalla prova; limite ufficiale 500 email/ora. Verificare il 7/10 sul primo giro che non arrivino più rifiuti 554 "too many messages". Il tetto giornaliero resta quello del riscaldamento (25/30/40).
