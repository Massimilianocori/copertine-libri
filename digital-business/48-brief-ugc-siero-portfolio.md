# Brief: UGC siero 15 s per il portfolio (6/10/2026) — DA APPROVARE, nessuna generazione fatta

> **STATO 6/10: SOSPESO.** Valutato con Massimiliano: il video nuovo non serve ora. Dopo aver tolto i due reel deboli (8 e 11) il portfolio ha comunque 6 reel più lo spot in hero, e la skincare è coperta da 3 reel (2, 4, 12). Non ci sono dati che un video in più porti clienti, e i crediti (529,88) servono per consegnare il primo pilota pagato. Si riapre se un cliente di moda/lusso risponde o se i reel restano un ostacolo nelle risposte. Il brief resta pronto.

Sostituisce nel portfolio il reel skincare con lo specchio (`11.mp4`). Basato su: `31` (regole ufficiali Higgsfield), `46` (cosa funziona), `47` (voce naturale), `45` (confronto concorrenza), `19` (scheda Sienna), ERRORI.md e PROCEDURE.md. Le fonti web sono deboli (riassunti di blog); dove è ipotesi è scritto.

## 1. Concept
Review-demo da presentatrice (non cliente), forma "dimostrazione": azione d'impatto in apertura, un solo siero, cinque gesti diversi, texture e etichetta leggibili. Nessun claim su risultati, nessuna esperienza in prima persona (FTC, doc 37). Obiettivo portfolio: mostrare gesti, coerenza, prodotto leggibile, ritmo (doc 46 §4, ipotesi).

## 2. Prodotto
Flacone smerigliato con contagocce, etichetta crema con scritta serif **MERIDIAN** (stesso marchio inventato dei reel 2 e 4, nessuna scritta in più). Nessun marchio reale. Riferimento prodotto: **non esiste ancora** un'immagine del flacone con contagocce con questa etichetta: va creata e approvata prima del video (immagine, circa 2-4 crediti).

## 3. Modella (casting) — AGGIORNATO 6/10
Sienna **esclusa**: è già nel reel "serum demo" (Massimiliano, 6/10). Serve un volto nuovo, da approvare prima di tutto. Proposta (una sola): donna adulta con **pelle scura e capelli ricci naturali raccolti**. Motivo (ipotesi): il portfolio ha oggi due donne asiatiche, una bruna (reel 11, da togliere), una rossa (Sienna) e due uomini; manca una donna con pelle scura e capelli ricci, e mostrare la texture della pelle su una carnagione scura è un caso difficile che alle agenzie fa vedere la gamma del lavoro. Rischio: il modello può rendere la pelle scura in modo meno convincente; il controllo fotogramma per fotogramma è più severo. Il casting si crea con 2 immagini candidate da cui Massimiliano sceglie; la scelta diventa il riferimento volto unico per tutto il video. Età non descritta nel prompt del video (doc 31).

## 4. Styling, trucco, capelli, unghie
Maglia a costine color avena, nessun gioiello; capelli raccolti con molletta dal primo taglio; trucco assente (pelle con texture visibile); unghie corte naturali. Identici in tutti i tagli (regola di coerenza). Da approvare.

## 5. Location e luce
Bagno luminoso con luce di finestra morbida, **nessuno specchio né riflessi** (doc 31), nessun'altra persona, nessun telefono visibile (la camera è il telefono). Luce unica, diurna, senza bagliore HDR né bokeh da cinema.

## 6. Inquadrature e movimento
Tavola da 8 riquadri 9:16 (doc 31): mezzo busto, primo piano guancia, mezzo busto con respiro, flacone all'altezza del mento, macro contagocce, macro polpastrello, guancia, mezzo busto di chiusura. Camera con micromovimento a mano, prodotto fermo. Tagli netti, un'interazione col prodotto per taglio, massimo 2 mani, il prodotto entra al 40% (secondo 6).

## 7. Copione (inglese americano, 29 parole) e tempi
| Taglio | Secondi | Azione | Voce |
|---|---|---|---|
| 1 | 0,0-2,0 | Già in movimento: fissa la molletta, sguardo in camera | "Hair back. Here's the routine." |
| 2 | 2,0-4,0 | Punte delle dita sulla pelle asciutta | "Clean, dry skin." |
| 3 | 4,0-6,0 | Respiro, mano aperta, sguardo di lato | (bocca chiusa) |
| 4 | 6,0-7,8 | Alza il flacone, etichetta frontale | "This is Meridian, the dropper serum." |
| 5 | 7,8-9,6 | Una goccia sul polpastrello | "One drop on the fingertip." |
| 6 | 9,6-11,4 | Macro texture, pollice e indice | "Light, a little slippery." |
| 7 | 11,4-13,2 | Stesa sulla guancia, un gesto | "Press in, cheek outward." |
| 8 | 13,2-15,0 | Flacone accanto al viso, sguardo in camera | "Link's below." |
"Light, a little slippery" è solo una sensazione osservabile: non esiste una lista di claim approvata per questo marchio inventato, quindi nessun'altra affermazione. Nessuna parola vietata (doc 31 §5). La prima parola non è "Okay/So/Wait".

## 8. Voce
Voce nativa di Seedance 2.5, con un campione audio di 5-10 s come riferimento di timbro. Persona (una frase, identica in ogni prompt): "A warm, easy-going presenter with a relaxed, slightly low voice, speaking at a calm conversational pace with a gentle melody, genuine and never salesy." Con un volto nuovo **`sienna-1` non va usata** (sarebbe la voce di Sienna su un'altra donna). La voce si sceglie ascoltando le anteprime dei preset nell'app Higgsfield (nessun credito): Massimiliano indica quella che gli sembra più naturale per il personaggio; poi si genera la battuta di prova. Prima del video si genera un campione di una battuta (1,1 crediti) con la voce scelta, che Massimiliano ascolta e approva. L'italiano non è previsto. Accento: americano neutro (da approvare).

## 9. Suono, testi, post
Nessuna musica nel modello; ambiente (room tone) nativo. In post: sottotitoli sul parlato in fascia centrale, riga finale "AI creator · scripted brand demo". Nessun testo generato dal modello.

## 10. Modello, costi, passi (un "sì" per ogni passo che spende)
Modello: **Seedance 2.5** in modalità riferimenti (workflow `ugc-video`), bozza 480p, finalizzazione 1080p con `draft_job_id` oppure upscale Topaz.
| Passo | Cosa | Crediti (stima) |
|---|---|---|
| 0 | Casting: 2 immagini candidate del volto nuovo (poi riferimento unico) | circa 4-8 (da verificare) |
| A | Campione voce, 1 battuta, voce scelta da Massimiliano | 1,1 |
| B | Immagine prodotto (flacone MERIDIAN con contagocce) | 2-4 |
| C | Tavola da 8 riquadri + pulizia Seedream 5 Pro | tavola 3-4; pulizia **non verificata** |
| D | Bozza video 15 s a 480p | circa 45 |
| E | Upscale Topaz | circa 5 |
Un tentativo completo: circa 65-80 crediti compreso il casting; due tentativi: circa 135-160 (restano circa 370 su 529,88).

## 11. Controlli prima e dopo
Prima: ogni immagine di partenza confrontata con il casting (volto, outfit, molletta, unghie); etichetta leggibile. Dopo, fotogramma per fotogramma: tagli automatici, altre persone, volto, outfit, mani (massimo 2), un solo flacone, etichetta in ogni taglio, sorrisi non voluti, voce con lo stesso timbro dal primo all'ultimo secondo, labiale, parole identiche al copione. Se un punto fallisce si scarta e si rifà prima di altri crediti.

## 12. Cosa non è verificato
Che l'ordine hook-prodotto-texture batta altre sequenze; che 15 s sia la durata ottima; il timbro della voce che sceglierà Massimiliano; la resa della pelle scura e dei capelli ricci nel modello; il costo della pulizia Seedream; la resa dell'etichetta MERIDIAN sul flacone con contagocce.
