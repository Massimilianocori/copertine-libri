# Regole ufficiali Higgsfield per l'UGC (workflow `ugc-video`): sintesi per Scrollcraft

Studio del 5/10/2026, a costo zero (nessuna generazione). Fonte: `get_workflow_instructions ugc-video` e i suoi file di riferimento (`ugc-clip.md`, `ugc-board.md`, `boards.md`, `monologue-craft.md`, `duration.md`, `formats/review.md`). Sono le regole che Higgsfield stessa usa per il suo UGC: applicarle prima di inventare un metodo.

## 1. Pipeline in sintesi

1. Intake: servono solo durata (10, 15, 30 o 45 s) e foto o genere della creator.
2. Creator: una sola identità bloccata (`character_media_id`) per tutte le tavole e le clip; mai rigenerarla né sostituirla con una descrizione. Se non c'è una foto: Soul 2, 3:4, 2k.
3. Copione (vedi sezione 5).
4. **Tavola storyboard** con GPT Image 2: 21:9, 2k, qualità alta; una riga di **8 riquadri verticali 9:16** (review e try-on) oppure 4 (product, unboxing, tutorial). Riferimenti in ordine: prodotto, creator, tavola precedente (per continuità).
5. **Pulizia obbligatoria** con Seedream 5 Pro, poi ispezione. Mai usare la tavola grezza. Prompt di pulizia: mantenere esattamente inquadratura, composizione, pose, identità, geometria ed etichetta del prodotto; cambiare solo il micro-realismo (texture di pelle e materiali, luce del giorno, rumore del sensore, aspetto da foto di telefono); evitare pelle cerosa, filtri bellezza, sovrasaturazione, bagliore HDR, sovra-nitidezza, bokeh cinematografico; niente testo né filigrana.
6. **Clip** con Seedance 2.5, modalità riferimenti, audio nativo acceso, 9:16, 1080p. Una clip = 4-15 s con **8 tagli interni** (uno per riquadro). Mai una chiamata separata per la voce.
7. Controllo di ogni clip (identità, prodotto, durata, inquadratura, parlato), poi montaggio e sottotitoli con `video-montage`.

## 2. Sei formati

review (creator che parla, il predefinito), product (prodotto protagonista con voce fuori campo), unboxing, try-on, tutorial (con etichette "Step N"), sito web. Un URL del prodotto identifica il prodotto, non il formato.

## 3. Durata e parole

- Video lunghi = più clip incollate: 16 s → 12+4; 19 → 15+4; 31 → 15+12+4; 46 → 15+15+12+4.
- Parole per clip: fino a 10 s circa 12-20; 11-12 s circa 20-28; 13-15 s circa 28-35.
- Tagli di durata uguale: a 15 s circa 1,9 s ciascuno.

## 4. Regole del prompt della clip (Seedance)

- Struttura fissa: Style & Mood → Narrative Summary → Dynamic Description (Cut 1... Cut 8, con "Hard cut to." tra un taglio e l'altro) → Static Description → Audio (copione parola per parola) → suffisso di qualità. Un solo prompt denso, in inglese.
- Tagli adiacenti con inquadratura diversa. Almeno 3 micro-comportamenti per taglio (sguardo, respiro, mano).
- **Regola dei primi 0,1 secondi:** il taglio 1 parte già in movimento (mai posa ferma, mai "aspetta di parlare") e la prima parola arriva entro 0,4 s.
- **Mani:** massimo 2, ruolo di ciascuna dichiarato. **Un'interazione col prodotto per taglio**, mai due. Vietato scrivere "spruzza di nuovo", "preme più volte", "avanti e indietro", "apre e chiude" (il modello li trasforma in cicli).
- **Prodotto:** un solo esemplare in ogni fotogramma; mostra solo l'etichetta frontale (non ruota); niente testo leggibile su altri oggetti di scena; la camera si muove, il prodotto no.
- **Bersaglio sul corpo:** profumo → polso o collo; crema o siero → polpastrello e poi viso; rossetto → solo labbra; bevanda → bocca; cipria → guancia; mascara → ciglia; prodotto per capelli → capelli.
- **Mai:** specchi e riflessi (generano arti in più), telefono visibile (la camera È il telefono), persone o oggetti extra, descrivere l'età del personaggio.
- Inquadrare: "umano, coinvolto, mai urlato" come registro predefinito. Musica solo se richiesta.

## 5. Copione e voce

- Dal 2° clip si riparte **a metà frase**: niente saluti né ripresentazione del prodotto.
- La prima parola non è mai "Okay / So / Wait / Hey / Alright / Well / Like". Meglio aprire con un'azione visibile ("Ecco la parte che si svita...").
- **Parole vietate:** "obsessed", "literally", "game changer", "holy grail", "changed my life", "hits different", "10/10", "100%", "you have to try this", "elevate", "seamless", "effortless".
- Maiuscole d'enfasi: al massimo 1-2 parole per riga; un picco di reazione per clip; un momento a bocca chiusa per clip (il labiale è la zona più debole).
- Inglese americano di default. Accento o tic solo se approvati; un campione audio di 5-10 s aiuta il modello a seguire l'accento. Una frase di "persona" della voce, ripetuta identica in ogni prompt, evita la deriva.
- Storia: scegliere UNA forma (19 disponibili: dimostrazione, meccanismo, confronto di meccaniche visibili, GRWM, mini-vlog, domanda e risposta, ASMR...) e UN "ma poi". Il prodotto entra come comprimario tra il 40% e il 60% della durata. Hook: scegliere uno degli 8 modelli (azione d'impatto, confessione a metà frase, pattern interrupt, reazione congelata, apertura ostile, tic, meccanismo, prodotto a freddo).

## 6. Verità e sicurezza (obbligatorie nel workflow)

- Creator **generata, adulta (21+)**; niente personaggi pubblici, celebrità, minori né imitazione di persone reali o della loro voce.
- Claim sul prodotto solo da una **lista approvata dal cliente**, parola per parola. Senza lista: solo meccaniche visibili e sensazioni osservabili.
- **Niente testimonianze sintetiche:** la creator generata è una presentatrice o dimostratrice, mai una cliente. Vietato inventare acquisto, uso ("lo uso da tre settimane"), risultati, prima/dopo, valutazioni, recensioni. La prima persona è ammessa solo se un utente reale fornisce il copione e conferma che è la sua esperienza.
- Inquadrare come **brand demo, creator concept o sponsored creative**, non come recensione organica; nel post mettere l'indicazione di contenuto pubblicitario.
- Prodotti vietati o limitati (adulti, gioco d'azzardo, farmaci, tabacco, armi, finanza ad alto rischio...) non si promuovono.

## 7. Cosa cambia per Scrollcraft

1. **I nostri campioni e copioni in prima persona vanno rivisti.** Per esempio il campione Meridian dice "Ho cambiato a Meridian tre settimane fa": è esperienza inventata. Per i clienti scrivere copioni da dimostratrice, con claim approvati, e dichiarare "AI creator" (già così per Sienna). Le piattaforme pubblicitarie e le regole sulle recensioni false trattano il rischio in modo severo: da verificare con ciascun cliente.
2. **La tavola a 8 riquadri è il nostro "storyboard visivo" in una sola immagine**: 1 immagine al posto di 8, e si anima in una clip con tagli netti. È il metodo da usare per storyboard anche dei video non UGC, dopo la pulizia di micro-realismo.
3. **Aggiungere la pulizia anti-"effetto AI"** (Seedream 5 Pro, prompt sopra) alle immagini degli storyboard, prima dei video.
4. **Nel brief UGC definire sempre:** formato, durata, persona della voce in una frase, registro, hook e forma di storia scelti, claim approvati, accento (sì/no), musica (sì/no).
5. Con il workflow ufficiale la voce è nativa di Seedance. Il metodo di Sienna del 1/10 (voce generata a parte come riferimento audio) è un'alternativa quando serve controllare esattamente le parole: costa 1,1 crediti a battuta.
