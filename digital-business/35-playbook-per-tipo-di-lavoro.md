# Playbook per tipo di lavoro (analisi del 5/10/2026)

Sintesi operativa di tutto il lavoro fatto dal 11/9 al 5/10. Non ripete i documenti esistenti: li richiama per numero. Prima di ogni lavoro creativo restano obbligatori `CLAUDE.md`, `ERRORI.md`, `PROCEDURE.md`.

**Legenda.** `[V]` = verificato, con fonte tra parentesi. `[I]` = ipotesi, da provare. 1.000 crediti = 50 € (dato di Massimiliano), quindi 1 credito = 0,05 €.

**Fonti usate.** Documenti 00, 15, 18, 19, 20-31, PIANO-OPERATIVO, 09-12; `ERRORI.md`; `PROCEDURE.md`; cronologia crediti Higgsfield (`transactions`, 15/9-5/10, letta per intero); storico generazioni video (primi 50 job, solo lettura); transcript di sessione (messaggi di Massimiliano e riepiloghi di contesto 1-5/10). Saldo Higgsfield al momento dell'analisi: 529,88 crediti (piano Ultra) `[V: balance]`.

---

## 1. Quanto è costato davvero (dallo storico crediti, non da stime)

| Lavoro | Crediti | Euro | Esito |
|---|---|---|---|
| Spot Tom Ford "Lost Cherry" (5/10): 18 clip Cinema Studio 4.0 a 1080p nativo (828) + 3 bozze 480p (93) + 3 upscale Topaz (11) + 19 immagini Nano Banana Pro (38) + prove iniziali Seedance 480p (30) e Kling (17,5) | circa 1.017 | circa 51 | Montato, non approvato da Massimiliano ("non sono soddisfatto"); volto non identico in 4 inquadrature `[V: transazioni, riepilogo sessione]` |
| Preventivo dello stesso spot | 715 | 36 | Reale +42% rispetto al preventivo (clip rifatte: spruzzo, passaggio capelli) `[V]` |
| Video DownRange (Cinema Studio 4.0, 17-19/9) | circa 1.047 | circa 52 | Pubblicato sul sito. Attribuzione dei costi a questo video: `[I]`, coincidono le date e il modello |
| Marketing Studio Video 15-17/9 (circa 12 chiamate da 30 a 140 crediti) | circa 1.090 | circa 55 | Un solo campione tenuto con certezza (Meridian). Quanti scartati: `[I]` |
| UGC Sienna Niacinamide, Marketing Studio 30 s 720p (28/9) | 208,2 | 10,4 | Buono, etichetta leggibile `[V: 30 §3]` |
| UGC skincare `11.mp4`, Seedance 15 s 1080p + immagini (21/9) | 191,6 | 9,6 | Pubblicato, QA fatto `[V: 00]` |
| UGC Sienna arancione, Seedance 14 s: 3 bozze 480p + finalizzazione 1080p (1/10) | 294 | 14,7 | Curato ma "messo in scena" `[V: 30 §3]` |
| Vlog Palm Springs di Sienna (24/9): circa 14 clip Seedance 480p-720p | circa 467 | circa 23 | Montato da Massimiliano, 38 s, pubblicato `[V: 19]` |
| Test Kling 3.0 per Sienna (22-23/9) | circa 157 | circa 8 | 3 test su 4 falliti, il 4° ok `[V: 19]` |
| Serie video Sienna "luxury" (2/10): 9 clip Seedance 8 s 720p da 56, 2 bloccate dal filtro NSFW e rimborsate | netti circa 392 | circa 20 | Esito qualitativo non documentato `[I]` |
| Foto (1/10-5/10): GPT Image 2.5 a 2,75 o 4,25, Nano Banana Pro a 2, Soul V2 a 0,12 | oltre 400 in totale | oltre 20 | Carosello sito rifatto più volte (vedi scheda 5) |
| Voce: TTS Seed Audio 0,7-1,1 a battuta; voce clonata 40 una tantum; Voice Change 2-4 | poco | - | `[V: transazioni]` |
| Soul ID (addestramento) | 25 a volta (3 volte) | 1,25 | `[V: transazioni]` |
| Apollo Basic | 59 $/mese | - | 523 contatti, poi 743 con 220 moda `[V: sessione]` |

Prezzi unitari osservati `[V: transazioni]`:

| Voce | Crediti |
|---|---|
| Seedance 2.5, Cinema Studio 4.0, Marketing Studio | 3/s a 480p, 7/s a 720p, 12/s a 1080p |
| Kling 3.0 std | 1,5-1,75/s (7,5-8,75 per 5 s) |
| Topaz 1080p | 3-5 per clip |
| Nano Banana Pro / Nano Banana 2 | 2 / 1,5 |
| GPT Image 2.5 | 2,75 (alta qualità 2k) o 4,25 |
| GPT Image 2.0 | 6,5 |
| Seedream 5 Pro | 2,5-3 |
| Soul V2 | 0,12 |
| Marketing Studio Image | 1,5-2 |

**Lettura.** Quasi tutto il costo è il video. Le immagini costano poco ma sono il punto dove si perde più tempo (rifacimenti). Il costo vero sono i rifacimenti: lo spot Tom Ford ha 18 clip a 1080p nativo (circa 828 crediti) e solo 3 bozze a 480p, cioè la regola "bozza 480p poi upscale" (18 §1, PROCEDURE) non è stata applicata alla maggior parte delle clip `[V: transazioni]`. Restano 3 crediti di upscale Topaz soltanto.

---

## 2. Schemi ricorrenti di errore (da ERRORI.md, doc 19, riepiloghi di sessione)

| # | Schema | Dove è successo | Regola per evitarlo |
|---|---|---|---|
| A | **Identità non coerente** (volto, outfit, capelli, unghie, rossetto) | Spot Tom Ford (ERRORI 1, 6, 11, 16); Sienna con solo placeholder testuale (19 §1) | Casting come unico riferimento in ogni generazione; confronto affiancato prima del video; mai copia di copia; per Kling anche start_image esplicito e Elemento con più foto |
| B | **Iniziative non ricercate** | Ciliegie e mandorla (ERRORI 4); scelta di Glow Recipe, Liquid Death, Heinz, Coca-Cola "perché c'erano"; Kling scelto da solo; foto generate senza permesso il 3/10 | Brief con ricerca punto per punto, poi "sì" per ogni generazione (CLAUDE.md) |
| C | **Prodotto/etichetta sbagliati** | Foto prodotto vecchia (ERRORI 5); testo piccolo inventato (19); etichetta Meridian instabile; flacone unbranded vuoto bocciato; verde etichetta diverso (1/10) | Solo foto ufficiali; testo sempre composto a mano o in post; controllare l'etichetta in ogni fotogramma |
| D | **Look "AI"** | YvaMarie ("sembra AI, il cinematografico lo accentua", 3/10); pelle e denti troppo lisci (19, 23/9); gocce false di ciliegia (5/10); "foto diventata video" (5/10) | Pulizia anti-AI con Seedream 5 Pro (31 §1); UGC deve sembrare telefono vero; nessun effetto fisico non verificato (liquidi, gocce) |
| E | **Il modello inventa o salta** | Cinema Studio inserisce tagli e una seconda donna (ERRORI 2); 4 inquadrature su 12 saltate in un solo prompt (PROCEDURE); Kling ignora multi_shots e storyboard (19 §8-9); spruzzo senza nebulizzazione (ERRORI 9) | Una clip per inquadratura, partendo dal suo fotogramma; "un'unica ripresa continua" nel prompt; azione chiave verificata prima di approvare |
| F | **Controlli tecnici saltati** | Aspect ratio dimenticato (70 crediti persi, 19); foto 4:5 usate come partenza di video 9:16 (19); clip da 4 s finita online per errore (19); HEVC illeggibile nel browser (18 §8); font di ripiego nelle anteprime (ERRORI 12) | Lista di controllo pre-generazione (vedi 3.0); H.264 prima di pubblicare |
| G | **Spesa senza preventivo o contro la procedura** | Upscale deciso e poi 1080p nativo; preventivo 715 contro circa 1.017 reali; "stai solo sprecando crediti" (3/10) | Preventivo scritto di tutto il progetto, con margine per i rifacimenti (almeno +40%, `[I]` dai dati sopra) |
| H | **Filtri della piattaforma** | NSFW su primi piani con Nano Banana e Seedance (2 job rifiutati il 2/10, 19 §24/9); gpt_image_2_5 su abito da sera; classificatore sugli invii email | Allargare l'inquadratura invece di cambiare il costume; riprovare con Massimiliano presente |
| I | **Consegna e sito** | Deploy ogni push (ERRORI 14, 17), sito Netlify sospeso il 5/10; file provvisori online | Un push al giorno, mai file provvisori |
| J | **Outreach** | Indirizzi generici e senza verifica, rimbalzi (22); limite Namecheap 20/ora, 19 mail non consegnate; indirizzo scritto a memoria (ERRORI 15); doppio invio Kin+Kind; colonna CSV sbagliata (ERRORI 18) | Solo indirizzi verificati, copiati dalla coda; script sulle colonne per nome |
| K | **Memoria** | Account Instagram di Sienna "non esistente" (26/9); limiti dichiarati senza leggere lo storico (ERRORI 20); workflow del 21/9 ignorato per le foto del 26/9 (19) | Leggere storico, `00` e `18` prima di proporre un metodo |

---

## 3. Schede per tipo di lavoro

### 3.0 Prima di ogni generazione (vale per tutte le schede)

1. Letti `CLAUDE.md`, `ERRORI.md`, `PROCEDURE.md`.
2. Brief con ricerca punto per punto approvato; preventivo scritto con saldo; "sì" esplicito per quella generazione.
3. Pre-volo: aspect ratio, durata, risoluzione, riferimenti caricati (casting, prodotto ufficiale, outfit), `declined_preset_id` se il sistema propone un preset non voluto `[V: riepilogo 5/10]`, modello effettivo verificato nel risultato (Higgsfield può sostituirlo, PROCEDURE).
4. Pass "unlimited" non usabili da qui: solo dal sito (18 §9).

### 3.1 Spot di marca (lusso, moda, profumo)

| Voce | Contenuto |
|---|---|
| Obiettivo | Pezzo di portfolio o spot per un brand, 16:9 o 9:16, senza "effetto foto animata" né AI evidente |
| Flusso | 1) Ricerca e brief (idea, prodotto da foto ufficiali, casting, outfit con checklist voce per voce, trucco, location, luce, camera, suono, testi), approvazione. 2) Prova affiancata della stessa inquadratura su 2 modelli, decide Massimiliano (ERRORI 19). 3) Preventivo di tutto con margine rifacimenti. 4) Casting e look approvati. 5) Storyboard visivo, un'immagine per inquadratura, confronto affiancato col casting e controllo di sorrisi, anatomia, barre nere, scritte finte, oggetti extra, continuità. 6) Bozza 480p di ogni clip, controllo fotogramma per fotogramma. 7) Solo le approvate: upscale o 1080p nativo, scelto da Massimiliano con i costi davanti. 8) Montaggio (PROCEDURE, checklist punto 8); musica la mette Massimiliano. 9) H.264, versione 30 MB. |
| Strumento | Cinema Studio 4.0 o Seedance 2.5, stessa tariffa al secondo `[V: 30 §2]`. Seedance: modalità draft 480p con finalizzazione 1080p dello stesso video, già usata per Sienna `[V: PROCEDURE]`. Quale dei due dia volti più stabili sulla stessa inquadratura: `[I]`, mai provato affiancato (ERRORI 19). Blocchi da 10-15 s con 4-6 inquadrature concatenati con video_extension: `[I]` (PROCEDURE punto 10). Kling 3.0 escluso per spot con più inquadrature `[V: 19 §9]` |
| Costi osservati | Tom Ford circa 1.017 crediti (circa 51 €) per 24 s montati; DownRange circa 1.047 `[I]`. Regola pratica: contare circa 40-50 crediti per secondo montato finale a 1080p nativo, `[I]` dai dati sopra |
| Errori da evitare | A, B, C, E, G della sezione 2. In più: Cinema Studio inserisce tagli interni (ERRORI 2); partire da una sola clip senza storyboard salta inquadrature; non mettere accessori non nel brief; passaggi narrativi (capelli raccolti poi sciolti) vanno girati, non saltati (ERRORI 11) |
| Controllo finale | Volto identico al casting in ogni inquadratura; outfit/trucco/unghie/capelli voce per voce; nessun sorriso; azione chiave visibile (spruzzo con nebulizzazione); nessun taglio o altra persona; nessuna barra o scritta finta; ritmo veloce con più movimento; colori come approvati; versione senza musica mandata a Massimiliano |

### 3.2 UGC con creator (avatar che parla, prodotto in mano)

| Voce | Contenuto |
|---|---|
| Obiettivo | Video 9:16 da 10-30 s che sembra girato con un telefono, per ads Meta e TikTok |
| Flusso | Seguire il workflow ufficiale riassunto in 31: creator bloccata, tavola 21:9 a 8 riquadri (GPT Image), pulizia Seedream 5 Pro, clip Seedance con 8 tagli, voce nativa. Prima: scheda voce e copione da dimostratrice con claim approvati dal cliente (31 §6), parole calcolate sulla durata (circa 2,5 parole/s, 19 §23/9), prima parola mai "Okay/So/Hey", primi 0,1 s già in movimento. Per volume e varianti hook: Marketing Studio (30 §4). Poi controllo etichetta in ogni fotogramma |
| Strumento | `[V]` Marketing Studio per aspetto autentico e una sola chiamata (Niacinamide 208 crediti per 30 s); Seedance 2.5 con riferimenti e storyboard per precisione e gesti (19 §10, 30). `[V]` Kling 3.0 solo per "parlato semplice, un piano" con ricetta 19 §1-4. Qual è meglio per un cliente reale: `[I]`, prova a tre proposta in 30 §6 mai eseguita |
| Costi osservati | Marketing Studio 15 s 720p circa 105; 30 s circa 208. Seedance 15 s 1080p circa 192 con immagini; 14 s con 3 bozze circa 294. Kling 5 s circa 8,75 |
| Errori da evitare | Prodotto che si deforma nelle mani e etichetta che si fonde con le dita (15; categoria di modelli, non lavoro sbagliato) quindi un'interazione col prodotto per taglio (31 §4); telefono in mano con prodotto fa sparire l'oggetto (19 §3); texture del prodotto da descrivere esplicitamente (19 §4); Kling non fa tagli né legge tavole (19 §8-9); `audio_references` vuole un audio isolato, non un video (19, 24/9); mai dialogo in italiano se il personaggio è americano (19); copioni in prima persona inventati (campione Meridian, "tre settimane fa", 31 §7) da riscrivere; HEVC (18 §8); aspect ratio |
| Controllo finale | Etichetta leggibile e stabile; una sola confezione; mani corrette; nessuno specchio o telefono visibile; labiale ok con un momento a bocca chiusa; voce coerente con la scheda; claim solo da lista approvata; "AI creator" dichiarato; non sembra "cinematografico" (feedback YvaMarie) |

Storico dei metodi precedenti: Creatify (avatar con lip-sync, scartato per il realismo, ancora indicato per solo-prodotto in volume, 10 §0, 6) e Veo 3.1 su Google Flow (20 crediti Flow per clip di 8 s, `[V: 10 §1]`, usato per `1.mp4`-`4.mp4`). Non rimisurati dopo il passaggio a Higgsfield.

### 3.3 Foto prodotto e still

| Voce | Contenuto |
|---|---|
| Obiettivo | Foto prodotto o editoriale di livello da campagna, "vere", non da AI |
| Flusso | 1) Massimiliano (fotografo) dirige estetica, luce, inquadratura; Claude prepara la parte tecnica e propone (25 "Foto prodotto"). 2) Ricerca di riferimenti reali e foto prodotto ufficiali. 3) Prodotti solo reali, luxury o persona con prodotto; mai prodotti da "quattro soldi" (3/10). 4) Per le persone: prima la scheda dei look (3 look a scelta, come con Bottega, `[V: riepilogo 5/10]`), poi la generazione. 5) Una prova, approvazione, poi serie. 6) Testo mai generato dall'AI: si compone in post (29 §3). 7) Uso privato per foto su prodotto di un brand reale, mai sul sito senza decisione (25) |
| Strumento | `[V]` Nano Banana Pro (2 crediti) bene per identità ed etichette; GPT Image 2.5 (2,75) migliore per etichette reali di marca, ma falsi positivi NSFW su abito da sera e fornisce volti diversi tra una chiamata e l'altra; Soul 2 (0,12) giudicato "medio-basso" da Massimiliano il 3/10; Soul V2 addestrato solo per le foto editoriali di Sienna e non per i video (00, 19). Pulizia anti-AI con Seedream 5 Pro `[V: 31]`. Ritocchi locali (PIL/OpenCV) per difetti puntuali `[V: riepilogo 3/10]` |
| Costi osservati | 0,12-6,5 crediti per immagine, 2-3 la norma. Giornate di lavoro foto: 1/10 circa 140; 3/10 circa 130; 5/10 foto profumo circa 60 più 38 per il Tom Ford |
| Errori da evitare | B, C, D della sezione 2. Prodotto tagliato a metà (Heinz); foto che non riempiono l'inquadratura; barre bianche laterali; stili casuali (Champagne LVMH); outfit "da mercato" (3/10); modella con una gamba sola; foto 4:5 quando serve 9:16; packshot su fondo bianco peggiore dell'originale del cliente (YvaMarie: "è meglio la sua", 3/10): verificare di migliorare davvero prima di offrire |
| Controllo finale | Idea in una frase; prodotto intero, etichetta e forma come le foto ufficiali; mani, anatomia, proporzioni ok; nessun marchio non voluto; nessuna riga o bordo; testo in post e leggibile (nero se lo sfondo è chiaro); con persone: viso e outfit coerenti; da "editore esperto" approvata da Massimiliano |

### 3.4 Caroselli e portfolio (sito, Instagram, LinkedIn)

| Voce | Contenuto |
|---|---|
| Obiettivo | Far sentire al cliente di essere "al top" appena entra; mostrare che sappiamo dirigere (29 §1) |
| Flusso | 1) Concept scritti e approvati (5 idee), poi una prova, poi la serie (riepilogo 3/10). 2) Foto come scheda 3.3. 3) Impaginazione: titolo 3-5 parole in serif italico, firma piccola, testo parte della composizione stile rivista (Vogue/Prada), non sopra il prodotto. 4) Immagini che riempiono la banda colorata dall'alto in basso, nessuno zoom, niente frecce. 5) Anteprima con i font reali (ERRORI 12) e identica al risultato (ERRORI 13). 6) Una sola pubblicazione al giorno. 7) Versione de-brandizzata se mostra un brand reale; "Concept / spec work. Not affiliated with [brand]", niente LVMH e Chanel (00) |
| Strumento | Sito statico `digital-business/portfolio/index.html` su Netlify, CSS con container query e testo in cqw (riepilogo 3/10). Bodoni Moda per i titoli `[V: sessione]`. Playwright per le anteprime, con font scaricati in locale (ERRORI 12) |
| Costi osservati | Crediti: vedi 3.3. Il carosello del 3/10 è stato rifatto interamente (5 immagini bocciate), e ancora il 5/10 per lo slide Tom Ford. Netlify: sospensione del piano gratuito il 5/10 `[V: riepilogo 5/10]` |
| Errori da evitare | Immagini "finte/AI" e prodotti economici (3/10); foto tagliate; testo staccato che resta fermo mentre la foto zooma; testo a caso; font diverso dall'anteprima; PDF non caricabile su LinkedIn (3/10, 20:19: usare immagini); ogni push pubblica (ERRORI 17); affermazioni false sul sito (20/9: FAQ "running on real ad accounts", corretta, 00) |
| Controllo finale | Checklist di 29 §3 (idea, confronto con i riferimenti, errori AI, marchi, approvazione) più: foto intere, nessuna riga, testo leggibile, stessa posizione del testo, video muto in loop con pulsante audio, H.264, un solo push |

### 3.5 Personaggi AI (Sienna)

| Voce | Contenuto |
|---|---|
| Obiettivo | Vetrina organica su Instagram e TikTok, personaggio sempre dichiarato AI (00, 19, 29 §6: a supporto, non motore) |
| Flusso | Per la bibbia del personaggio e i pilastri: 19. Per gli algoritmi e il piano giornaliero: 21. Operativo: 1) ambiente generato da solo (solo testo), 2) poi insieme a Character Sheet con istruzione di relighting (18 §3-4; correzione del 26/9, 19), 3) foto 9:16 prima del video, 4) video con Seedance con storyboard, 720p, 9:16 sempre, una clip per inquadratura, montaggio da Massimiliano, 5) lo stesso file su TikTok, suono trending scelto in fase di pubblicazione (21) |
| Strumento | `[V]` Elemento `skincare-creator-v2` (più foto) più start_image per video e Seedance con storyboard (19 §1-10); Soul ID `Sienna` per foto editoriali, non compatibile con i video (00); Nano Banana Pro per identità. Kling solo per parlato in un piano. Voce: non c'è una voce bloccata (24/9, 19): `create_voice` da audio isolato è `[I]` non fatto |
| Costi osservati | Vlog 38 s circa 470 crediti di video; 55 concept di produzione previsti ma il piano a 3-5 video a settimana è `[I]` mai eseguito a quel ritmo; stato account al 26/9: 12 post, 7 follower (00), 7-11 follower secondo 20 |
| Errori da evitare | Placeholder testuale senza start_image (volto diverso); telefono in mano con prodotto; Kling con più inquadrature (non funziona); NSFW su primi piani (allargare l'inquadratura); dialogo in italiano; script troppo lungo per la durata; formato 4:5 contro 9:16; operatore o ombra visibili; stato dell'account non scritto (26/9); la regola "video generati dal sito per sfruttare i pass" (18 §9) |
| Controllo finale | Stesso volto dell'Elemento in ogni fotogramma; pelle con texture (non liscia); mani; nessun operatore o riflesso; voce americana coerente; audio sincronizzato; "AI creator" in bio; didascalie con parole chiave (le didascalie sbagliate hanno dato 0 visualizzazioni per 4 giorni su TikTok, 21 §1) |

### 3.6 Sito web (scrollcraft.design)

| Voce | Contenuto |
|---|---|
| Obiettivo | Vetrina e raccolta richieste; link Stripe in modalità LIVE (00) |
| Flusso | Dire a Massimiliano cosa si vuole cambiare e aspettare l'ok (23). Raggruppare le modifiche, anteprima identica, un solo push al giorno (ERRORI 14, 17). Convertire i video in H.264 con faststart prima di pubblicare (18 §8). Nessun servizio di tracciamento senza aggiornare la privacy (PROCEDURE). Non toccare i Payment Link |
| Strumento | `[V]` Git push su `claude/digital-files-business-plan-f8y8gd`, Netlify `beamish-duckanoo-de8a46` (23). Playwright per le anteprime |
| Costi | 0 crediti. Netlify: sito sospeso il 5/10 per esaurimento del piano gratuito (riepilogo di sessione) |
| Errori da evitare | ERRORI 12, 13, 14, 17; claim falsi (00, 20/9); push di file provvisori; video HEVC |
| Controllo finale | Anteprima desktop e mobile con i font reali; ancore delle categorie funzionanti (`#skincare` ecc.); video che partono; nessun claim non vero (zero clienti reali finora); privacy aggiornata; pubblicazione del giorno non ancora fatta |

### 3.7 Outreach e vendite

| Voce | Contenuto |
|---|---|
| Obiettivo | Ottenere lavoro pagato; gli unici indicatori sono risposte e rimbalzi, non le aperture (22 §1) |
| Flusso | Strategia in 29 §5 (sostituisce 25-28). Liste da Apollo Basic (A-D più moda), solo indirizzi con stato verified o letti in chiaro (22 §2, 26); preferire piccole aziende senza budget per campagne tradizionali (richiesta del 5/10). Testo e regole: 22 §4-5 (circa 4 minuti tra una mail e l'altra, massimo 10 all'ora, scaglioni 25/30/40 al giorno, follow-up a 4 e 9 giorni). LinkedIn manuale: 27. Risposte: preparare la risposta e far approvare a Massimiliano. Offerta in vigore: PROCEDURE ("Email e vendite") |
| Strumento | `[V]` Gmail MCP (bozze e invio con Massimiliano presente), Apollo (1 credito per persona), tracker CSV/Drive. Vibe Prospecting: crediti gratuiti finiti (26). Routine giornaliera automatica 13:00 UTC lun-ven `[V: riepilogo 5/10]` |
| Costi osservati | Apollo 59 $/mese; nessun costo per email. Risultati al 5/10 `[V]`: circa 60 mail in 2 settimane, 1 rifiuto (Kin+Kind), 1 risposta di merito (YvaMarie: "sembra AI generato, vorrei qualità reale"), nessun cliente; il 5/10, 9 invii su 25, senza rimbalzi |
| Errori da evitare | Caselle generiche e indirizzi indovinati (22, 26); raffiche (20/ora Namecheap); duplicati (Kin+Kind, Camille Rose); colonne sbagliate (ERRORI 18); indirizzo a memoria (ERRORI 15); brand già acquisiti o con VC (00); promettere "campione gratis" quando la politica è "niente lavoro gratis" (vedi sezione 4); testi in prima persona inventati (31 §7); testi in italiano nelle bozze (1/10) |
| Controllo finale | Indirizzo letto dalla coda e confrontato dopo l'invio; non già contattato (Sent, bozze e tracker); decisore nominale; nessun claim non verificabile; link senza punto finale; distanza dall'ultimo invio; cap giornaliero; registro aggiornato |

---

## 4. Incongruenze tra documenti (da risolvere con Massimiliano)

| Tema | Documenti | Quale vale oggi |
|---|---|---|
| Campione gratuito | 12, 22, 29 (campione con filigrana) contro PROCEDURE 5/10 ("niente lavoro gratis"); i follow-up del 5/10 dicono ancora "free sample" | `[I]` vale PROCEDURE (più recente), ma i testi inviati dicono il contrario: da decidere |
| Prezzi | 11 ($179/$845/$1.890/$3.490), 28-29 (prova 5 annunci $250, mensile $900), PROCEDURE (pilota 3 video $450, Holiday Ad Pack $1.490, white-label) | PROCEDURE è il più recente |
| 480p più upscale | 18, PROCEDURE e 30 a favore; 19 (24/9) "non conviene"; 5/10 ha usato 1080p nativo | Decide Massimiliano caso per caso con i costi davanti |
| Limiti di invio | 00 (15-20 al giorno), 22 (20 al giorno), 29 e PROCEDURE (25/30/40) | PROCEDURE |
| Piano originale | PIANO-OPERATIVO (cliniche in Italia, 11/9) | Superato da 29 |

## 5. Non verificato o mancante

- Qualità di Cinema Studio 4.0 contro Seedance 2.5 sulla stessa inquadratura: mai provata (ERRORI 19).
- Motore sotto Marketing Studio; qualità Topaz contro 1080p nativo sui volti (30 §5).
- Esito qualitativo delle 9 clip Seedance del 2/10 e quanti dei circa 12 job Marketing Studio del 15-17/9 sono stati scartati.
- Voce bloccata di Sienna (non esiste); video lunghi in blocchi concatenati con video_extension.
- Tasso di risposta dell'outreach con l'indirizzo verificato: dati insufficienti (50 invii circa).
- Voci di costo marcate "circa": sono somme manuali dello storico transazioni, non attribuzioni job per job.
