# Brief: UGC siero 15 s per il portfolio (6/10/2026) — DA APPROVARE, nessuna generazione fatta

Sostituisce nel portfolio il reel skincare con lo specchio (`11.mp4`). Basato su: `31` (regole ufficiali Higgsfield), `46` (cosa funziona), `47` (voce naturale), `45` (confronto concorrenza), `19` (scheda Sienna), ERRORI.md e PROCEDURE.md. Le fonti web sono deboli (riassunti di blog); dove è ipotesi è scritto.

## 1. Concept
Review-demo da presentatrice (non cliente), forma "dimostrazione": azione d'impatto in apertura, un solo siero, cinque gesti diversi, texture e etichetta leggibili. Nessun claim su risultati, nessuna esperienza in prima persona (FTC, doc 37). Obiettivo portfolio: mostrare gesti, coerenza, prodotto leggibile, ritmo (doc 46 §4, ipotesi).

## 2. Prodotto
Flacone smerigliato con contagocce, etichetta crema con scritta serif **MERIDIAN** (stesso marchio inventato dei reel 2 e 4, nessuna scritta in più). Nessun marchio reale. Riferimento prodotto: **non esiste ancora** un'immagine del flacone con contagocce con questa etichetta: va creata e approvata prima del video (immagine, circa 2-4 crediti).

## 3. Modella (casting)
Proposta: **Sienna**, elemento `skincare-creator-v2` (volto già bloccato, scheda `19`): zero costo di casting, coerenza garantita, creator AI di Scrollcraft dichiarata. Compromesso: il reel "serum demo" arancione è già Sienna, quindi nel portfolio comparirebbe due volte. Riferimento volto = solo il casting approvato; confronto affiancato di ogni immagine di partenza prima del video.

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
Voce nativa di Seedance 2.5, con un campione audio di 5-10 s come riferimento di timbro. Persona (una frase, identica in ogni prompt): "A warm, easy-going presenter with a relaxed, slightly low voice, speaking at a calm conversational pace with a gentle melody, genuine and never salesy." Voce proposta: `sienna-1` (già posseduta). **Non l'ho ascoltata e non so se è naturale**: prima del video si genera un campione di una battuta (1,1 crediti) che Massimiliano ascolta e approva. L'italiano non è previsto. Accento: americano neutro (da approvare).

## 9. Suono, testi, post
Nessuna musica nel modello; ambiente (room tone) nativo. In post: sottotitoli sul parlato in fascia centrale, riga finale "AI creator · scripted brand demo". Nessun testo generato dal modello.

## 10. Modello, costi, passi (un "sì" per ogni passo che spende)
Modello: **Seedance 2.5** in modalità riferimenti (workflow `ugc-video`), bozza 480p, finalizzazione 1080p con `draft_job_id` oppure upscale Topaz.
| Passo | Cosa | Crediti (stima) |
|---|---|---|
| A | Campione voce, 1 battuta | 1,1 |
| B | Immagine prodotto (flacone MERIDIAN con contagocce) | 2-4 |
| C | Tavola da 8 riquadri + pulizia Seedream 5 Pro | tavola 3-4; pulizia **non verificata** |
| D | Bozza video 15 s a 480p | circa 45 |
| E | Upscale Topaz | circa 5 |
Un tentativo completo: circa 60-70 crediti; due tentativi: circa 130-150 (restano circa 380 su 529,88).

## 11. Controlli prima e dopo
Prima: ogni immagine di partenza confrontata con il casting (volto, outfit, molletta, unghie); etichetta leggibile. Dopo, fotogramma per fotogramma: tagli automatici, altre persone, volto, outfit, mani (massimo 2), un solo flacone, etichetta in ogni taglio, sorrisi non voluti, voce con lo stesso timbro dal primo all'ultimo secondo, labiale, parole identiche al copione. Se un punto fallisce si scarta e si rifà prima di altri crediti.

## 12. Cosa non è verificato
Che l'ordine hook-prodotto-texture batta altre sequenze; che 15 s sia la durata ottima; il timbro di `sienna-1`; il costo della pulizia Seedream; la resa dell'etichetta MERIDIAN sul flacone con contagocce.
