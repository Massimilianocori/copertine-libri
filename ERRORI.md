# Registro errori (da leggere prima di ogni lavoro creativo)

Ogni riga: errore → regola permanente.

## Spot Tom Ford Lost Cherry (ottobre 2026)

1. **Volto della modella diverso tra le inquadrature** (5, 6, 8, 9 fatte con nano, volto ≠ casting) → Ogni immagine di partenza si genera con il casting approvato come unico riferimento volto e si confronta affiancata al casting prima di fare il video. Volto non identico = scartata.
2. **Taglio automatico di Cinema Studio con un'altra donna** (clip 6) → Nel prompt: un'unica ripresa continua, nessun taglio. Ogni clip si controlla fotogramma per fotogramma prima del montaggio.
3. **La modella ride** (inquadratura 6) → Mai sorrisi o risate se non richiesti. Controllo esplicito dell'espressione in ogni immagine e clip.
4. **Elementi aggiunti di iniziativa** (ciliegie, mandorla accanto al flacone) → Mai aggiungere oggetti non presenti nel brief approvato o nelle foto prodotto ufficiali.
5. **Riferimento prodotto sbagliato** (foto vecchia con flacone sbagliato) → Usare solo le foto prodotto ufficiali fornite da Massimiliano.
6. **Outfit incoerente** (giacca su abito da sera; tessuto metallico; lunghezza midi invece che lunga; unghie nude; rossetto che cambia) → Checklist outfit/trucco approvato verificata voce per voce su ogni immagine.
7. **Anatomia** (una gamba sola, mano strana) → Controllo anatomico di ogni immagine e clip.
8. **Barre/pannelli neri, scritte finte** (scena 8, scena 10, soletta sandali) → Controllo bordi e testi finti in ogni immagine.
9. **Azione senza effetto** (spruzzo senza nebulizzazione) → Verificare che l'azione chiave si veda davvero (spruzzo, gesto) prima di approvare la clip.
10. **Inquadratura senza volto dove serviva** (secondo 2) → Rispettare lo storyboard: se la scena prevede volto e abito, devono esserci entrambi.
11. **Passaggio narrativo mancante** (capelli raccolti → sciolti senza la scena del gesto) → Controllare la continuità tra un'inquadratura e la successiva (capelli, oggetti, posizione) prima di chiudere lo storyboard.

## Sito / grafica

12. **Font diverso da quello richiesto** (anteprime con font di ripiego) → Usare i font reali in locale per le anteprime e verificare che coincidano con il sito.
13. **Anteprima diversa dal risultato approvato** → Mostrare esattamente quello che andrà online.
14. **Deploy Netlify troppo frequenti** (sito sospeso) → Massimo 1 pubblicazione al giorno.

## Email

15. **Indirizzo email scritto a memoria e sbagliato** (tim@somnee.com invece di tim@somneesleep.com, 5/10) → Prima di ogni invio leggo la riga della coda (`invii-*.tsv`) nello stesso passaggio e copio l'indirizzo da lì, carattere per carattere. Dopo ogni invio confronto il destinatario con la coda.

## Spot (continua)

16. **Immagine di partenza con un'immagine di composizione vecchia come riferimento** (spruzzo rifatto: il volto resta quello vecchio, il riferimento di composizione domina sul casting) → Per cambiare volto non dare mai l'immagine col volto sbagliato come riferimento. Partire da un fotogramma che ha già il volto giusto.

## Sito (continua)

17. **Ogni push sul branch pubblica il sito** (Netlify fa il deploy automatico in produzione su `claude/digital-files-business-plan-f8y8gd`; i push di `ERRORI.md` e la hero provvisoria senza musica sono andati online, 5/10) → Raggruppare tutte le modifiche e fare un solo push al giorno. Non fare push di file provvisori del sito.
18. **Script di aggiornamento CSV sulla colonna sbagliata** ("inviata" scritto in `Stato` invece di `Stato invio`, 5/10) → Negli script selezionare le colonne per nome esatto (`h.index('Stato invio')`), mai per parola contenuta.
19. **Modello video scelto senza confronto** (spot Tom Ford fatto tutto con Cinema Studio 4.0 senza testare Seedance 2.5, che era nel brief e ha la modalità bozza 480p → finale 1080p nativo dello stesso video, 5/10) → Prima di ogni progetto video: stessa inquadratura di prova su 2 modelli, confronto affiancato a Massimiliano, decide lui.

## Memoria del lavoro già fatto

20. **Dubbi e proposte senza controllare lo storico** (5/10: ho detto di non poter verificare il labiale con voce esterna e la finalizzazione 1080p di Seedance, ma erano già stati usati per Sienna il 1/10) → Prima di proporre un metodo o dichiarare un limite, controllare lo storico delle generazioni (normali e Marketing Studio) e i documenti in `digital-business/`.

21. **Conclusione sull'autenticazione email tratta solo dal DNS, senza vedere come parte la posta** (6/10: ho scritto che l'SPF non copriva le email perché partivano "via Gmail"; lo screenshot di Gmail mostra invece che `hello@scrollcraft.design` invia tramite `smtp.privateemail.com` porta 587, quindi l'SPF di Namecheap è quello giusto) → Prima di dichiarare un problema di consegna, verificare l'intero percorso (impostazioni di invio, header di un'email reale: `spf/dkim/dmarc=pass`), non solo i record DNS. Test reale del 6/10 (header di un'email da `hello@scrollcraft.design` a Gmail): `spf=pass`, `dkim=pass` (selettore `privateemail`, non `google` né `default` come avevo provato), `dmarc=pass`. Prima di dire che un DKIM manca, cercare il selettore reale negli header (`DKIM-Signature: s=...`).

22. **Giudizio sul portfolio dato senza rileggere gli studi già fatti** (6/10: ho definito "forte" il reel Meridian problem/solution e detto che il portfolio bastava, ma i doc 34 e 37 avevano già trovato che Meridian, Wagwell, Noir e Fort hanno testimonianze in prima persona inventate, e che in Meridian parlato l'etichetta si specchia) → Prima di giudicare un lavoro esistente, rileggere ciò che gli studi hanno già trovato su quel lavoro (doc 34, 37, 45) oltre a guardare i fotogrammi.

23. **Strumento installato e mai controllato** (6/10: il tracker visitatori Apollo è sul sito dal 5/10 ma non l'ho inserito nel controllo giornaliero; Massimiliano ha dovuto chiedere) → Ogni strumento che installo entra subito nel piano giornaliero con un controllo e una riga nel report. Prima di chiudere un lavoro chiedersi: chi lo controlla domani?

24. **Voce fuori campo invece di parlato in camera** (6/10, clip A Angle Test: si sente la voce ma lei non muove le labbra; le battute erano raggruppate nella sezione Audio e molti tagli erano macro o con lo sguardo in basso) → Nel prompt video ogni battuta va dentro il suo taglio ("she says: '...', lips in sync"), solo nei tagli con viso in camera e bocca visibile; i macro restano muti. Nel controllo: confrontare i momenti di parlato (energia audio) con i fotogrammi per vedere se la bocca si muove, e far ascoltare a Massimiliano prima di procedere. Costo dell'errore: 84 crediti pagati da Massimiliano; progetto fermato.
