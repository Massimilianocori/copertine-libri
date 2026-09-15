# Il campione gratuito — cosa è, cosa non è, come si consegna

Decisione 2026-09-15. Il campione che mandiamo nell'outreach si consegna **con filigrana**, non
utilizzabile commercialmente. Prima era promesso come "tuo, usalo come vuoi": era un errore, e questo
file lo corregge ovunque.

---

## 1. Perché la filigrana

Senza filigrana **il campione gratuito è il prodotto**. Un brand che voleva un video ne ha uno, gratis,
pronto da mandare in campagna: il tier da $179 non ha più nessuna ragione di esistere, e nemmeno lo
Starter da $845 per chi voleva solo provare.

Con la filigrana il campione fa il lavoro che deve fare — **dimostrare la qualità** — senza fare il
lavoro che deve essere pagato, cioè **consegnare un asset utilizzabile**. È lo stesso meccanismo degli
archivi di foto e video stock: l'anteprima si guarda tutta, non si pubblica.

Il compromesso accettato: un video con filigrana si condivide meno volentieri dentro l'azienda del
prospect ("guarda cosa ci hanno mandato"). Vale comunque la pena, perché la versione pulita è
esattamente ciò che chiediamo di comprare.

---

## 2. Campione gratuito vs ordine a pagamento

La distinzione va detta esplicitamente in ogni messaggio, altrimenti la prima domanda del prospect è
"se me lo fai gratis, cosa sto pagando?".

| | Campione gratuito | Singolo a $179 |
|---|---|---|
| Chi sceglie il prodotto | noi | il cliente |
| Chi scrive il copione | noi | su brief del cliente |
| Revisioni | nessuna | una |
| Filigrana | **sì** | no |
| Diritti d'uso | nessuno | pieni, inclusi |
| A cosa serve | far vedere la qualità | un ad vero, da mandare in campagna |

---

## 3. Come si applica la filigrana

L'overlay è pronto: **`watermark/sample-overlay-1080x1920.png`**, trasparente, già nel formato dei
nostri video. Due modi, stesso risultato.

### Final Cut (consigliato, nessun comando da scrivere)

1. Importa `sample-overlay-1080x1920.png` nella libreria.
2. Trascinalo sulla timeline **sopra** la traccia video, per tutta la durata della clip.
3. Verifica che sia a dimensione piena (la risoluzione coincide già: nessuna scalatura).
4. Esporta come al solito, poi ricomprimi per il web (vedi `10-video-veo3-prompt-pronti.md` §3bis:
   target 3-5 Mbps, non il 14+ Mbps del master).

### ffmpeg (per applicarlo a più video in serie)

```sh
ffmpeg -i pulito.mp4 -i watermark/sample-overlay-1080x1920.png \
  -filter_complex "[0:v][1:v]overlay=0:0" \
  -c:v libx264 -preset slow -crf 24 -pix_fmt yuv420p \
  -c:a copy -movflags +faststart sample.mp4
```

`[VERIFICATO in sessione 2026-09-15]` provato su `1.mp4`: volto e movimento restano perfettamente
giudicabili, il video non è utilizzabile come pubblicità. Nota: il binario ffmpeg usato in sessione
non includeva il filtro `drawtext`, per questo la filigrana è un PNG sovrapposto e non testo
disegnato al volo — ed è comunque la soluzione migliore, perché il PNG funziona identico in Final Cut.

**Regola: il file pulito non esce mai prima del pagamento.** Non mandarlo "in anteprima", non
allegarlo "tanto poi paga". Il file pulito è il prodotto.

---

## 4. Come si scrive nei messaggi

Il campione va offerto come dimostrazione, mai come regalo utilizzabile. Formule corrette:

- ✅ "a free sample ad for [Product] — watermarked, so you can see exactly what you'd get"
- ✅ "it's a preview: the clean, ready-to-run file comes with any order"
- ❌ "use it however you like"
- ❌ "no strings"
- ❌ "yours to keep and run"

Le tre formule sbagliate erano nei nostri script fino al 2026-09-15 e sono state corrette in
`05-A1-outreach-offer-EN.md`. Se ricompaiono, il tier singolo smette di avere senso.

---

## 5. Costo e capacità

Un campione costa ~45 minuti di produzione `[IPOTESI da rimisurare]`, identici a quelli di un video
venduto. È marketing, non produzione: va contato nel budget di acquisizione, non nella capacità
produttiva vendibile (~25 ore/mese, vedi `11-strategia-prezzi.md` §5).

Con 2-3 campioni al giorno si consumano ~2 ore al giorno solo di outreach. **Se il sito inizia a
ricevere traffico organico, la richiesta di campioni gratuiti diventa un problema di capacità prima
che di conversione.** In quel caso il filtro da aggiungere è una qualificazione leggera nel form
("for brands currently running paid ads"), non un limite arbitrario.
