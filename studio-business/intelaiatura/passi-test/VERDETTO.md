# Verdetto del test «Il passo è aperto oggi?» (15/10 – 15/11/2026)

Scritto il 16/11/2026 dalla routine «Verdetto passi alpini», sulle 29 letture di `registro.jsonl` (`sonda.py --riepilogo`) e sulle soglie della sez. 6 di PIANO.md.

## Esito: NON PASSA (per ora). Idea in RISERVA, nuova prova a maggio 2027 solo con fonti ufficiali

| # | Soglia | Esito | Perché |
|---|---|---|---|
| 1 | ≥ 30 passi su 40 coperti | **NO (dubbio)** | Enti pubblici e gestori (Bolzano, Piemonte, Savoia, Hautes-Alpes, Alpes-Maritimes, GROHAG): ~19 passi, letture regolari e chiusure segnalate (Nivolet, Agnello, Iseran, Galibier, Bonette, Madeleine, Moncenisio, Lombarda, Piccolo San Bernardo, Staller, Rombo, Stelvio, Grossglockner). Con il TCS si arriva a ~31, ma il TCS non è un ente pubblico e ha almeno un caso dubbio (sotto). Il CCISS conta solo dove ha segnalato una chiusura (Gavia, Foscagno, San Pellegrino, Piccolo San Bernardo, Stelvio): per gli altri 9 passi «aperto» vuol dire solo «nessuna chiusura segnalata». |
| 2 | ≥ 5 dei 7 italiani più cercati | **SÌ** | Stelvio e Rombo (Bolzano, chiusi il 9/11), Sella, Pordoi, Gardena (Bolzano, aperti tutto il periodo, coerente: restano aperti d'inverno), Gavia (CCISS, chiuso dal 23/10). Giau: solo CCISS, mai una chiusura vista. |
| 3 | Data di chiusura giusta ≥ 90 % | **NON MISURABILE** | Manca una «verità» indipendente: abbiamo solo le fonti stesse. Dove due fonti coprono lo stesso passo: Lombarda, Moncenisio, Agnello, Piccolo San Bernardo concordano sul giorno; Stelvio no (Bolzano 9/11, CCISS 13/11: 4 giorni di ritardo del CCISS); Galibier Savoia 16/10 contro Hautes-Alpes 21/10. |
| 4 | Zero «aperto» quando era chiuso | **NO** | Spluga: TCS (fonte principale) sempre «aperto», CCISS «chiuso» 30/10 – 1/11. Gran San Bernardo: TCS «chiuso» dal 19/10, CCISS sempre «aperto» (il CCISS non segnala chiusure che il TCS vede). Basta un caso sulla fonte principale per fallire, e lo Spluga lo è finché non si prova il contrario. |

## Cosa vale comunque

- Le fonti ufficiali regionali (Bolzano RSS, Piemonte, Savoia, Alpes-Maritimes, Hautes-Alpes, GROHAG) si leggono da script ogni giorno in pochi secondi e hanno segnalato le chiusure con date coerenti tra loro.
- La domanda è stagionale: le ricerche «is X pass open» salgono a maggio-giugno (aperture) e ottobre-novembre (chiusure). Ora la stagione è finita.

## Decisione

- **NO al sito adesso** (soglie 1 e 4 non passate; stagione chiusa; idea solo pubblicità, centrale bassa).
- **RISERVA con nuova prova dal 1/5/2027 al 15/6/2027** (stagione delle aperture), solo sui passi coperti da enti pubblici e gestori (~19) più la Svizzera con i dati ufficiali di opentransportdata.swiss (token gratuito: 5 minuti di Massimiliano, da chiedere ad aprile 2027). TCS e CCISS solo come seconda fonte, mai come fonte principale.
- La sonda si ferma (non è più nella routine serale dal 16/11).
