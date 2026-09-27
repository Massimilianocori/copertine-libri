# Algoritmi Instagram/TikTok 2026 — strategia e percorso giornaliero per Sienna

2026-09-27. Richiesta diretta: studiare nel dettaglio come muoversi per l'algoritmo di Instagram e
TikTok, e dare ogni giorno un percorso concreto per ambito. Vincolo posto subito dopo: **un video al
giorno costa troppo — quando si produce un video per Instagram, va pubblicato anche su TikTok**,
niente produzione doppia/dedicata per piattaforma.

---

## 1. Diagnosi — perché il profilo è fermo

- **Volume troppo basso e incostante**: 12 post totali su IG in giorni, TikTok con solo 5 video
  storici (e zero visualizzazioni per 4 giorni per un problema di didascalie ormai risolto, vedi
  `00-STATO-PROGETTO.md`). Entrambi gli algoritmi 2026 penalizzano l'incostanza più che in passato.
- **TikTok non sfrutta la sua unica vera scorciatoia per un account a zero follower: i suoni
  trending.** Un video con audio trending arriva a pubblico nuovo anche con pochi follower, perché
  TikTok lo mostra a chi già interagisce con quel suono, indipendentemente da chi ti segue —
  **+58% engagement medio verificato**. Sienna ha sempre voce originale sincronizzata, mai un suono
  trending in sottofondo.
- **Nessuna gestione della prima ora**: nel 2026 TikTok testa un video nuovo su un piccolo pubblico
  (200-500 persone) e decide se espanderlo in base a salvataggi/condivisioni/watch time in quella
  finestra. Mai gestita finora.
- **Instagram**: quasi solo foto/carosello finora — buono per i salvataggi, ma i reel restano
  l'unico formato che porta pubblico davvero nuovo (reach), non solo profondità con chi già segue.

---

## 2. Come funzionano davvero i due algoritmi nel 2026 (sintesi ricerca)

### Instagram
- **Reel**: fattori di ranking confermati da Mosseri, in ordine — **watch time/replay** (il #1),
  **invii per reach** (3-5 volte più preziosi dei like per raggiungere pubblico nuovo), **like per
  reach**. I primi 3 secondi determinano se il reel viene distribuito oltre il test iniziale.
  Limite pratico di reach oltre i 3 minuti, anche se tecnicamente si può caricare fino a 20 min.
- **Carosello vs Reel**: i caroselli hanno engagement rate più alto (0,50-0,55% contro 0,50-0,52%
  dei reel) e ~2x i salvataggi per impression — ma i **reel restano il formato che porta reach/
  pubblico nuovo**, i caroselli approfondiscono con chi già ti segue. Non sono intercambiabili.
- **Hashtag**: contano meno di prima. Instagram nel 2026 limita l'utilità a **3-5 hashtag di
  nicchia**, meglio se nella didascalia stessa (indicizzata per SEO) che in una lista lunga — le
  parole chiave nel testo della didascalia pesano più degli hashtag.
- **Frequenza consigliata**: reel 3-5/settimana, feed/carosello 2-3/settimana, stories 1-3/giorno.
- **Orari migliori (dati aggregati 2026)**: mercoledì 12-18, giovedì 9-14, martedì 13-19.

### TikTok
- **Fattori di ranking**: completion rate + watch time pesano ~40-50% del punteggio (il singolo
  fattore più importante), poi salvataggi/condivisioni, poi like — l'ordine è cambiato rispetto a
  prima, i like contano relativamente meno.
- **Cold start 2026**: un account a zero follower **salta il test sui follower** e va dritto a un
  piccolo pubblico non-follower con interessi simili. Se quel pubblico interagisce (salva/
  condivide/guarda fino in fondo) nella prima ora, il video passa al pool successivo, più ampio —
  altrimenti muore lì. 200-500 interazioni di qualità nella prima ora fanno la differenza tra un
  video fermo a 800 visualizzazioni e uno che continua a crescere.
- **Suoni trending**: usarli entro le prime 24h della loro ascesa dà fino a 3x le visualizzazioni;
  un video con suono trending può arrivare a milioni di view anche con un account piccolo, perché
  TikTok lo abbina a chi già ascolta/interagisce con quel suono.
- **Hook nei primi 3 secondi**: il 71% degli utenti decide se continuare a guardare in quel lasso —
  ancora più critico che su Instagram.
- **Orari migliori**: martedì-venerdì 14-18, ma il **sabato è il giorno migliore in assoluto**.

---

## 3. Strategia adattata al vincolo di budget (niente produzione doppia)

**Principio**: ogni contenuto si produce **una sola volta** e si pubblica su entrambe le
piattaforme, adattando solo la fase di pubblicazione (non la produzione) alle regole di ciascun
algoritmo:

1. **Ogni video prodotto per Instagram (3-5/settimana, budget invariato ~105-175€/mese) va
   ripubblicato su TikTok lo stesso giorno o il giorno dopo**, usando lo stesso file. Zero
   produzione aggiuntiva.
2. **Solo le foto/carousel di tipo educational/informativo vanno anche su TikTok come post
   fotografico/slideshow** — non tutte le foto. Dati 2026 (aggiornati dopo un confronto diretto con
   Massimiliano, che aveva già scartato le foto su TikTok in passato): il photo mode di TikTok ha
   reach alto **solo per contenuti educational/informativi**, ma **fallisce per contenuti
   personality-driven/intrattenimento** — che è la natura della maggior parte dei pilastri di
   Sienna (Ossessioni, Rant, Assurdo). Quindi:
   - **Estetica/mood, Ossessioni, Rant, Assurdo** → restano solo su Instagram (carosello), su
     TikTok andrebbero comunque male.
   - **Solo il formato settimanale "Scoperta della settimana"** (l'episodio educational/informativo
     già previsto, un fatto verificato raccontato una volta a settimana) è adatto anche a TikTok
     come slideshow — è l'unico contenuto della lista che è davvero informativo, non
     personalità/intrattenimento.
3. **Risultato**: i video restano il grosso del volume cross-postato (3-5/settimana), più 1
   episodio educational/settimana anche come foto su TikTok — non tutte le 2-3 foto/settimana come
   avevo detto in una prima versione di questo file, corretto dopo il confronto con Massimiliano.

### Cosa cambia solo in fase di pubblicazione (costo zero)

- **Su TikTok, al momento della pubblicazione** (dentro il flusso `tiktok_prepare_publish`, fase
  "music selection"): scegliere un suono trending pertinente come sottofondo a basso volume sotto
  la voce di Sienna, invece di lasciare solo l'audio originale — unica leva a costo zero con il
  maggior impatto misurato (+58% engagement).
- **Prima ora dopo ogni pubblicazione TikTok**: Massimiliano guarda il video, lo salva/condivide a
  qualche contatto reale, risponde subito a ogni commento — 5 minuti, ma è la finestra che decide
  se il video passa al pool successivo o muore a poche centinaia di view.
- **Didascalie**: parole chiave di nicchia nel testo (non liste di hashtag), 3-5 hashtag mirati alla
  fine — stessa regola su entrambe le piattaforme.
- **Orari di pubblicazione**: mercoledì/giovedì pomeriggio per Instagram, martedì-venerdì
  pomeriggio o sabato per TikTok — se un contenuto è cross-postato lo stesso giorno, si privilegia
  l'orario migliore per la piattaforma su cui conta di più quel pezzo (video → TikTok, carosello →
  Instagram).

---

## 4. Percorso giornaliero (aggiornato al vincolo budget)

### Giorni di produzione (3-5 volte/settimana, quando esce un video nuovo)
1. Genero il video per Instagram come già previsto (pipeline Higgsfield esistente).
2. Pubblico su Instagram come Reel.
3. Pubblico lo stesso file su TikTok con `tiktok_prepare_publish` — **tu confermi il widget e scegli
   un suono trending in fase di pubblicazione** (ti segnalo quali sono pertinenti quel giorno).
4. **Tu, nella prima ora dopo la pubblicazione TikTok**: guarda/salva/condividi/rispondi ai commenti
   (5 minuti).

### Giorni foto/carosello (2-3 volte/settimana)
1. Genero le foto come già previsto.
2. Pubblico su Instagram come carosello.
3. **Solo se è l'episodio settimanale "Scoperta della settimana" (educational)**: pubblico le
   stesse foto anche su TikTok come post fotografico con musica. Tutti gli altri caroselli
   (Estetica, Ossessioni, Rant, Assurdo) restano solo su Instagram.

### Ogni giorno, a prescindere dalla produzione
- Controllo risposte/commenti in sospeso su entrambe le piattaforme (5 min).
- Ti segnalo se un contenuto sta performando sopra/sotto la media, per capire cosa ripetere.

### Verifica dopo 4 settimane
- Guardare i dati reali (follower, view medie, salvataggi) prima di decidere se aumentare ancora il
  volume o cambiare mix — non prima, servono almeno 15-20 post cross-postati per avere segnale.

---

## Fonti

- [Sprout Social — TikTok Algorithm 2026](https://sproutsocial.com/insights/tiktok-algorithm/)
- [Hootsuite — Instagram Algorithm 2026](https://blog.hootsuite.com/instagram-algorithm/)
- [Hootsuite — TikTok Algorithm 2026](https://blog.hootsuite.com/tiktok-algorithm/)
- [Dash Social — Trending TikTok Audio 2026](https://www.dashsocial.com/blog/tiktok-sounds)
- [NetInfluencer — Cold Start TikTok 2026](https://www.netinfluencer.com/how-to-cold-start-tiktok-shop-in-2026-according-to-20-creator-marketing-experts/)
- [Buffer — Best Time to Post on Instagram 2026](https://buffer.com/resources/when-is-the-best-time-to-post-on-instagram/)
- [Buffer — Best Time to Post on TikTok 2026](https://buffer.com/resources/best-time-to-post-on-tiktok/)
- [Sked Social — Instagram Hashtags 2026](https://skedsocial.com/blog/how-to-use-hashtags-on-instagram-in-2026-hashtag-tips-to-up-your-insta-game)
- [Storrito — Instagram Carousels vs Reels 2026](https://storrito.com/resources/how-instagram-carousels-beat-reels-for-engagement-in-2026-and-when-to-use-each/)
