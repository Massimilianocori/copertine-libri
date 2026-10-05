# Higgsfield: strumenti e motori a confronto (studio del 5/10/2026)

Richiesta di Massimiliano: studiare le differenze tra Marketing Studio, Video e Cinema Studio e dire cosa usare e come. Fonti: schemi dei modelli (`models_explore`), workflow ufficiale `ugc-video` di Higgsfield, storico delle generazioni, storico dei crediti realmente spesi (`transactions`), tre video UGC già fatti (visti fotogramma per fotogramma), appunti interni (`18-higgsfield-workflow-guida.md`, `19-personaggio-ai-sienna.md`).

## 1. Due livelli: strumento e motore

- **Motore** = il modello che genera: Seedance 2.5, Kling 3.0, Cinema Studio 4.0, FLUX 3 Video.
- **Strumento** = l'interfaccia che lo usa:
  - **Video**: scegli tu il motore e dai immagini, audio e prompt. Massimo controllo, più lavoro.
  - **Cinema Studio**: interfaccia da regista (camera, obiettivo, apertura, epoca, genere, ritmo, luce, palette) con regia automatica del prompt; modalità testo, riferimenti, modifica video, estensione video; 4-30 s; 480p-1080p.
  - **Marketing Studio**: automazione per annunci prodotto/UGC: formati (UGC, Tutorial, Unboxing, Product Review, Virtual Try On), hook, ambientazioni, 1 avatar, prodotto, ricreazione di un video di riferimento. Il motore usato sotto non è dichiarato nello schema; Massimiliano indica che include Seedance 2.5 (il costo al secondo coincide, vedi sotto).
- **Workflow ufficiale Higgsfield per l'UGC (`ugc-video`)**: tavola immagini (GPT Image 2 → Seedream 5 Pro → ispezione e pulizia) → clip con **Seedance 2.5** in modalità riferimenti con **audio nativo** (nessun TTS separato). Sei formati: review (creator che parla), product (solo prodotto con voce fuori campo), unboxing, try-on, tutorial, sito web.

## 2. Costi reali (dai crediti spesi, non stimati)

| Cosa | Crediti | Per secondo |
|---|---|---|
| Seedance 2.5, 480p (bozza) | 42 per 14 s; 30 per 10 s | 3 |
| Seedance 2.5, 720p | 56 per 8 s; 112 per 16 s | 7 |
| Seedance 2.5, 1080p (finalizzazione della bozza) | 168 per 14 s | 12 |
| Cinema Studio 4.0 | 480p: 36 per 12 s; 720p: 28 per 4 s; 1080p: 60 per 5 s | 3 / 7 / 12 |
| Marketing Studio Video (talking 30 s, 720p) | 208,2 | circa 6,9 |
| Kling 3.0 (std, 5 s) | 8,75 | circa 1,75 |
| Upscale Topaz a 1080p | 3 per 4 s; 5 per 15 s | meno di 1 |
| Voce: text-to-speech Seed Audio | 1,1 a battuta | - |
| Voce clonata (Voice Element, una tantum) | 40 | - |
| Immagini: Nano Banana Pro / Nano Banana 2 | 2 | - |

Conclusioni dai numeri:
- Seedance, Cinema Studio e Marketing Studio hanno la **stessa tariffa al secondo** (3, 7, 12). Il prezzo non decide: contano controllo, tempo e affidabilità. Coerente con l'idea che Marketing Studio giri su Seedance (non è una prova).
- **Bozza 480p + upscale Topaz costa circa un quarto della finalizzazione nativa in 1080p**: per 14 s, 42 + 5 = 47 crediti contro 42 + 168 = 210.
- **Kling 3.0 costa circa 4 volte meno al secondo** del 720p di Seedance.
- Con 1.000 crediti = 50 € (dato di Massimiliano): un UGC da 15 s costa circa 5 € in Marketing Studio, circa 1,3 € con Kling, circa 2,4 € con Seedance bozza + upscale. Rispetto ai prezzi di vendita (115-179 $ a video) il costo vero è nei rifacimenti e nel tempo, non nei crediti.

## 3. Cosa si vede nei tre video UGC già fatti (campione piccolo, prodotti e copioni diversi)

- **Marketing Studio, Sienna Niacinamide (28/9, 30 s, 720p):** aspetto da telefono vero (mano, camera che si muove, pelle con texture), etichetta del prodotto leggibile, una sola chiamata. Costo 208 crediti.
- **Marketing Studio, Meridian (17/9, 15 s, 720p):** stesso look autentico, ma l'etichetta del vasetto in alcuni fotogrammi è illeggibile o instabile.
- **Seedance 2.5, Sienna in arancione (1/10, 14 s, 1080p):** molto curato e controllato (fotogramma iniziale e finale, gesti del contagocce, voce nostra sincronizzata), ma aspetto più "messo in scena" e camera quasi fissa. Costo reale circa 300 crediti con 3 bozze + finale, circa 218 con un solo tentativo.

## 4. Cosa usare e come

1. **Spot di marca (lusso, moda, gioielli):** Cinema Studio 4.0 (o Seedance 2.5, stesso costo: da confrontare con una prova prima del prossimo spot). Metodo: storyboard visivo approvato, blocchi da 10-15 s, bozza 480p, controllo fotogramma per fotogramma, poi upscale Topaz. 1080p nativo o 4K solo come extra a pagamento.
2. **UGC con creator che parla, volume e varianti hook (nucleo del business):** partire da **Marketing Studio** (formato talking/UGC): una chiamata, look più autentico, circa 7 crediti al secondo. Controllare sempre l'etichetta del prodotto in ogni fotogramma. Copione e tono nel brief.
3. **UGC quando serve precisione** (gesti col prodotto, applicazione, 1080p): workflow ufficiale `ugc-video` con **Seedance 2.5** (tavola immagini approvata → clip con audio nativo, oppure fotogramma iniziale/finale + voce a parte come per Sienna). Bozza 480p, poi upscale.
4. **Clip economiche per testare hook semplici (parlato, un solo piano, fino a 15 s):** Kling 3.0 con la ricetta di `19-personaggio-ai-sienna.md` (fotogramma iniziale esplicito, Elemento personaggio, niente telefono in mano col prodotto, descrivere la texture del prodotto).
5. **Sempre:** voce descritta nella scheda voce e approvata; casting come riferimento in ogni generazione; costo dichiarato prima; il motore lo decide Massimiliano.

## 5. Non verificato

- Quale motore usi Marketing Studio sotto (solo indizio di costo).
- Qualità di Cinema Studio 4.0 contro Seedance 2.5 sulla stessa inquadratura.
- Quanto il tono scritto nel prompt di Marketing Studio sia rispettato (nessun parametro dedicato).
- Qualità dell'upscale Topaz contro 1080p nativo su volti: accettabile per i social secondo Massimiliano, differenza visibile solo da vicino.
- Il controllo dei costi con `get_cost` è stato rifiutato da Massimiliano: tutti i costi sopra vengono da crediti già spesi.

## 6. Prova proposta per decidere (serve il "sì" di Massimiliano)

Stesso prodotto (vitamina C) e stesso copione da 15 s in tre versioni: Marketing Studio (circa 104 crediti), Seedance 2.5 bozza + upscale (circa 60 compresi immagini e voce), Kling 3.0 (circa 26). Totale circa 190 crediti, 10 €.
