# Procedure e cose imparate (da leggere prima di ogni lavoro)

Qui va tutto quello che funziona e che abbiamo imparato. Gli errori vanno in `ERRORI.md`.

## Produzione video (spot)

1. **Storyboard visivo, sempre.** Per ogni inquadratura si genera un fotogramma chiave (stesso volto del casting, stesso outfit), lo si controlla affiancato al casting, si mostra a Massimiliano la sequenza come storyboard e, solo dopo l'approvazione, ogni video parte dal suo fotogramma. Uno storyboard solo scritto in un prompt unico porta il modello a saltare inquadrature (spot Tom Ford: 4 su 12 saltate).
2. **Il casting in ogni generazione.** Il ritratto del casting approvato va passato come riferimento volto in OGNI generazione (immagini, video, correzioni), insieme al riferimento outfit. Mai correggere partendo da un'immagine derivata già spostata (copia di copia): si rigenera dal casting.
3. **Coerenza del volto.** Partire sempre da un fotogramma che ha già il volto giusto (es. primo piano del casting). La modalità *video_extension* di Cinema Studio 4.0 continua la stessa persona dalla clip precedente: utile per sequenze lunghe.
4. **Prima bozza a 480p, poi upscale.** La bozza 480p costa un quarto della 1080p. Se approvata, si porta a 1080p (o 2160p) con l'upscale Topaz: contenuto identico. Rigenerare in 1080p produce invece un video diverso (generazione casuale).
5. **Costi verificati (ottobre 2026):** Cinema Studio 4.0 = 3 crediti/s a 480p, 12 crediti/s a 1080p; immagine Nano Banana Pro ≈ 2 crediti; upscale Topaz 1080p ≈ 0,75 crediti/s. Usare `get_cost` prima di ogni generazione.
6. **Controllare il modello usato.** Higgsfield può sostituire il modello richiesto (es. Nano Banana Pro → Nano Banana 2): verificarlo nel risultato del job.
7. **Gusto di Massimiliano sugli spot:** ritmo veloce, inquadrature che cambiano spesso, più movimento che pose statiche, mai l'effetto "foto animate"; nessuna scritta dentro lo spot, solo una grafica finale su nero dopo lo spot; la storia deve capirsi senza spiegazioni (prima/dopo chiaro).
8. **4K:** i modelli video arrivano a 1080p; il 4K si ottiene con upscale Topaz 2160p. Serve solo per TV, cinema, schermi o lusso: offrirlo come extra a pagamento.

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
- Decidere con i numeri: test A/B tra segmenti (es. agenzie vs moda), confronto dopo 7 giorni.
