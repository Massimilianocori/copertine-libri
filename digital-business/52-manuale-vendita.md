# Manuale di vendita e marketing B2B per Scrollcraft (6/10/2026)

Scopo: un manuale operativo, dalla prima email all'incasso e al cliente ricorrente. Spiegazioni in italiano, testi da usare con i clienti in inglese.
Legenda: **[V]** fonte autorevole (libro, ricerca pubblicata, documentazione ufficiale) · **[V debole]** blog di fornitore o riassunto di ricerca web, pagina non aperta · **[S]** letto nei nostri file · **[I]** ipotesi nostra, da misurare.
Limite onesto: gong.io, docs.stripe.com ed edelman.com sono bloccati dal proxy: i loro dati vengono dai riassunti di WebSearch. I metodi dei libri (SPIN, Challenger, Gap Selling, Sandler, Voss, Schwartz, Dunford, Enns) sono riassunti di opere note, non numeri da applicare alla lettera.
Non ripete `36` (consegnabilità, tetti, follow-up, regole legali), `37` (clausole), `38` (prezzi), `39`/`44` (canali): li richiama.

---

## 0. Cinque principi che reggono tutto il resto

1. **Il problema del cliente prima del nostro servizio.** Nessuno compra se la situazione attuale va bene (Gap Selling, Keenan [V]). "Diagnose before you prescribe" (Blair Enns, *Win Without Pitching* [V]). Nelle email e nelle call si parla prima del suo collo di bottiglia, poi di noi.
2. **Il cliente "assume" un servizio per un lavoro da fare** (Jobs-to-be-done, Christensen, HBR 2016 [V]). Il lavoro di un'agenzia non è "comprare video AI": è *consegnare al cliente più creatività nuova senza assumere né perdere margine*. Il lavoro di un media buyer: *tenere vive le campagne quando i creativi si stancano*. Il lavoro di un brand: *avere un aspetto da campagna senza il costo di uno shooting*.
3. **Insegnare qualcosa, poi guidare** (The Challenger Sale, Dixon e Adamson, ricerca CEB su 6.000+ venditori [V]). Il nostro "insight" verificabile: il sistema Meta (Andromeda) premia concetti davvero diversi, non varianti cosmetiche (`38` §1 [V debole]). Quindi vendiamo **angoli diversi**, non "hook variants".
4. **Il messaggio segue il livello di consapevolezza** (Eugene Schwartz, *Breakthrough Advertising*, 1966 [V]). Un contatto a freddo è "problem aware" o "solution aware", mai "product aware": prima riga sul suo problema, non sul nostro nome.
5. **Ascoltare più che parlare.** Nelle call vincenti il venditore parla circa il 43% e ascolta il 57% (Gong, 326.000 call [V debole]).

---

## 1. Email a freddo che ottengono risposta

### 1.1 Regole (con fonte)

| Elemento | Regola | Fonte |
|---|---|---|
| Lunghezza | Sotto 100 parole; meglio 50-80. Le email di 25-50 parole hanno il 65% di risposte in più di quelle da 125 | Gong Labs, 304.000 email [V debole]; Lavender benchmark 2026, 231.818 email [V debole] |
| Leggibilità | Frasi da quinta elementare (livello 3-5): una idea per frase | Lavender [V debole] |
| Oggetto | 2-4 parole, minuscole, che sembri una mail interna; niente "AI", prezzi, urgenza | Gong [V debole]; `36` §5 |
| Prima riga | Un fatto che può ricevere solo lui (lancio, assunzione, annuncio attivo, cliente pubblico). Se non c'è un fatto verificato, si apre con il suo problema, mai con "I run Scrollcraft" | Josh Braun [V debole]; Schwartz [V] |
| Corpo | Problema → chi siamo in una riga → una prova → una offerta | Braun, formula in 4 frasi [V debole] |
| Prova | Una sola: un link. Il lavoro è dimostrativo e va detto ("spec, not a client job") | FTC regola recensioni false [V]; `37` |
| CTA | **Di interesse, non di riunione**: "Worth a look?" batte "call this week?" e "Friday at 2pm?" | Gong, 304.174 email, CTA di interesse = la più efficace [V debole] |
| Una sola richiesta | Una offerta per email. Il listino completo va nella risposta, l'Holiday Pack nel follow-up (elemento nuovo) | `36` §5 [V debole]; [I] |
| Formato | Testo semplice, 1 link, niente immagini né pixel; footer con indirizzo postale e "reply no" (`outreach-footer-con-indirizzo.txt`) | `36` §3, `37` §3 [S] |
| Promesse | Niente clienti, risultati o "we work with" inventati; "licence" e non "full commercial rights" | `37` clausola 4 [S] |

### 1.2 Revisione critica dei 3 testi attuali (`build_queue.py`, `invii-6ott.json`)

Stato [S]: nella coda del 6/10 ci sono 27 email agenzie (AG) e 30 brand moda (MO, variante "A campaign film for {Brand}"); 20 già inviate. La variante media buyer è nello script ma non in questa coda.

| Difetto | Dove | Perché conta |
|---|---|---|
| ~110-120 parole | tutti | Oltre la soglia di 100 (Gong) e lontano dai 50-80 |
| Si apre con "I run Scrollcraft… 20 years" | AG, MB, BR | Parla di noi, non del suo problema (Schwartz, Braun). I 20 anni sono un punto forte, ma vanno messi come prova, non come apertura |
| Nessun fatto personale | tutti | L'unica personalizzazione è il nome dell'azienda nell'oggetto e nel testo; `36` §5 la indicava come da rimettere |
| Tre offerte in una email ($115, $450, $1.490) | AG, MB, BR | Troppe scelte: il lettore non sa a cosa rispondere. Una sola offerta (il pilota) |
| CTA "Worth a quick call this week?" | tutti | È una richiesta di riunione: secondo Gong rende meno di una domanda di interesse |
| "full commercial rights" | AG, MB, BR | Contrasta con `37` clausola 4: possiamo dare una licenza, non garantire copyright o esclusiva sull'AI |
| Oggetto AG "White-label AI video production for {Company}" (7+ parole, "AI") | AG | Lungo, sembra una campagna, la parola AI attiva il pregiudizio prima di vedere il lavoro |
| Oggetto MB "Creative production for your ad accounts" | MB | Generico, potrebbe essere di chiunque |
| Oggetto BR "Short-form video ads for {Company}" / MO "A campaign film for {Brand}" | BR, MO | Il secondo è buono (corto, concreto); il primo è generico |
| Lo spot Tom Ford citato col nome del marchio | MO | Rischio marchi (`37` §4): dire "spec spot, not commissioned" e mai suggerire un rapporto col marchio |
| "first batch in 5 business days" | tutti | Vero solo se il saldo crediti basta (`36` §4): verificare prima di ogni invio di massa |

Punti buoni da tenere: testo semplice, un link, "AI disclosed" (BR), "no branding" (AG), la frase MO "same model, same styling, same light in every shot… without the cost of a shoot" (beneficio concreto, coerente con la nostra regola di coerenza).

### 1.3 Le tre versioni migliorate (da usare così; `{HOOK}` solo se c'è un fatto verificato, altrimenti si toglie la riga)

**Agenzie (white-label)** · oggetto: `{Company} video overflow` · 72 parole
```
Hi {First},

{HOOK, e.g. "Saw {Company} runs paid social for {public client}."}

When a client suddenly needs ten new ad videos by Friday, who makes them?

That's what Scrollcraft does for agencies: finished 9:16 video ads, white-label, made with AI and checked frame by frame. I've spent 20 years in advertising. A recent spec piece (not a client job): {LINK}

A paid three-video pilot is $450.

Worth a look for {Company}?

Massimiliano
```

**Media buyer** · oggetto: `new angles, your name` · 74 parole
```
Hi {First},

{HOOK, e.g. "Saw you manage Meta and TikTok spend for {type of brands}."}

Meta now rewards genuinely different concepts, so most accounts need more new creative than clients can shoot.

Scrollcraft makes those videos for you to deliver under your name: three distinct angles per product, finished 9:16, made with AI and checked frame by frame. 20 years in advertising behind it. Spec example: {LINK}

Pilot: three videos, $450.

Open to trying it on one account?

Massimiliano
```

**Brand (anche moda)** · oggetto: `{Brand} campaign film idea` · 70 parole
```
Hi {First},

{HOOK, e.g. "Saw the {collection/product} launch."}

A campaign look usually means a shoot: crew, location, weeks.

I've worked in advertising for 20 years and now direct campaign films made with AI: same model, styling and light in every shot, AI disclosed. Our latest is a spec spot, not a commissioned job: {LINK}

A paid pilot for {Brand} is three videos for $450.

Would that be useful for {product}?

Massimiliano
```
Firma completa + footer con indirizzo sotto ogni email (`36` §6, `37` §3).

**Follow-up giorno 4 (tutti, elemento nuovo = Holiday Pack, finché vale):**
`Quick add, {First}: for Q4 we have a Holiday Ad Pack, 10 videos + 10 hook variants for $1,490, ordered by Oct 24, delivered by Nov 10. Relevant for {Company}?`
**Giorno 9:** quello di `36` §7 (chiusura gentile, poi stop).
Nota [I]: misurare le nuove versioni su almeno 100-150 invii per segmento prima di giudicarle (`36` §4); cambiare una variabile alla volta.

---

## 2. Quando qualcuno risponde

### 2.1 Tempi
- **Entro 1 ora lavorativa se possibile, sempre in giornata.** Ricerca HBR (Oldroyd e altri, 2011, 1,25 milioni di lead): chi contatta entro un'ora ha quasi 7 volte più probabilità di qualificare il lead rispetto a chi aspetta anche solo un'ora in più [V]. Lo studio riguarda richieste in entrata, non risposte a cold email: per noi è un'analogia [I], ma la direzione è chiara.
- Controllare Gmail e webmail Namecheap due volte al giorno (`36` §11 #8). Claude prepara la bozza, Massimiliano invia.

### 2.2 Struttura della risposta (sotto 120 parole)
1. Ringraziare e rispondere esattamente a ciò che ha chiesto (prezzo? prezzo in una riga).
2. Due-tre domande di qualificazione (§2.3), non di più.
3. Un passo successivo con due opzioni concrete: 15 minuti di call **oppure** brief scritto e pilota. Chi decide è lui.

```
Thanks, {First}. Short answer: {answer to their question}.

So I send the right thing, three quick questions:
1. What would the videos be for: new concepts, or fresh angles on ads already running?
2. Roughly how many videos a month do your clients need, and by when is the first batch due?
3. Is this your call, or does someone else sign off on new vendors?

Two ways forward: a 15-minute call ({two time slots, their time zone}), or if you already know the product, I send a one-page pilot proposal today.

Massimiliano
```

### 2.3 Domande di qualificazione (BANT adattato + Jobs-to-be-done)
BANT (Budget, Authority, Need, Timeline) nasce in IBM come filtro rapido [V debole sulla storia]; va usato come guida, non come interrogatorio.

| Cosa | Domanda (EN) | Segnale buono | Segnale di stop |
|---|---|---|---|
| Bisogno / lavoro | "What's the job here: more concepts, more variants, or a campaign look?" | Ha un collo di bottiglia concreto | "Just curious" |
| Volume | "How many new videos a month, across how many clients/products?" | ≥ 3 subito, ≥ 10/mese in prospettiva | Uno solo, una volta |
| Tempi | "When do you need the first batch live?" | Data entro 30 giorni | "Someday" |
| Budget | "What do you usually pay per finished video today, roughly?" | ≥ $150 o costi di shooting | Si aspetta $10-20 (fascia Arcads, `38` §1) |
| Chi decide | "Who else needs to see this before you say yes?" | Lui o un socio | Comitato, procurement |
| Materiali | "Do you have official product photos and an approved claims list?" | Sì | No (senza foto ufficiali non si parte, ERRORI #5) |

### 2.4 Call o pilota diretto?
- **Pilota diretto** se ha già indicato prodotto, volume e tempi: si manda il preventivo di una pagina (§5) lo stesso giorno. Meno passaggi = meno abbandoni [I].
- **Call di 15 minuti** se il bisogno è vago, se ci sono più decisori, o se si parla di volume ricorrente (agenzie, media buyer con più clienti).
- Mai lavoro gratuito come passo intermedio (politica 5/10). Alla richiesta di campione: obiezione §4.

---

## 3. Call di scoperta di 15 minuti (in inglese)

Struttura: contratto iniziale (Sandler "up-front contract": tempo, scopo, esito [V debole]) → stato attuale (Gap Selling: 60-70% del tempo [V debole]) → implicazioni (SPIN: domande di implicazione e di beneficio, Rackham, 35.000 vendite analizzate [V]) → stato futuro → proposta → passo successivo. Massimiliano parla circa 40%, ascolta 60%.

| Min | Fase | Cosa dire |
|---|---|---|
| 0-1 | Up-front contract | "Thanks for the time. We have 15 minutes. I'd like to understand how you produce ad creative today and where it gets stuck; then, if it fits, I'll tell you how a pilot works. At the end we decide together: a next step, or a clear no. Fair?" |
| 1-6 | Situazione e problema | "Walk me through how a new ad video gets made today, from brief to live." · "Who makes them: in-house, creators, a production company?" · "Where does it break: speed, cost, number of variants, quality?" |
| 6-9 | Implicazione e gap | "When creative runs out, what happens to the account?" · "How often does a client ask for new videos you can't deliver in time?" · "What does that cost you: margin, a client, your team's weekends?" · "If you could get ten new videos in a week, what would change?" |
| 9-12 | Proposta su misura | Una frase per ogni problema che ha detto lui, niente lista di funzioni: "You said {problem}. The pilot does {one thing}: three distinct angles on one product, brief and storyboard approved before anything is made, five business days after the brief." Mostrare un solo lavoro, detto per quello che è: "This is a spec piece, not a client job." |
| 12-14 | Prezzo e rischio | "The pilot is $450, 50% to start. If a video fails the checklist we agree in the brief, we redo it once; if it still fails, you don't pay for that video." (garanzia di processo da `38` §6: **solo dopo il sì di Massimiliano**) |
| 14-15 | Passo successivo | "Does it make sense to run the pilot on {product}? If yes, I'll send the one-page proposal today and you can start as soon as the deposit is in." Se esita: "Is it a bad idea to start with just one product?" (domanda orientata al no, Voss [V debole]) |

Dopo la call, entro un'ora: email di riepilogo con le sue parole (problema, data, volume) + preventivo di una pagina.

---

## 4. Obiezioni (risposte brevi, in inglese)

Metodo: riconoscere, una prova o un fatto, una domanda (`36` §8). Mai attaccare il fornitore attuale, mai promettere ciò che non si può mostrare. Complementare alla tabella di `36` §8.

| Obiezione | Risposta |
|---|---|
| **Quality: "AI ads look fake"** | "Fair, a lot of them do: wrong hands, melting labels, faces that change. Every clip of ours gets a frame-by-frame check against a written checklist before you see it. The pilot is small so you can judge on your own product, and if a video fails the checklist we redo it." |
| **"It's AI, our clients/audience won't like it"** | "Some audiences don't, and we never hide it: the ads are labelled, which Meta already requires for photorealistic AI people. Where it works best is volume testing and concepts you'd never shoot. Which part of your mix is that?" (dato Meta su etichetta: [V debole]; scetticismo dei consumatori: `38` §1) |
| **Price: "too expensive" / "Arcads is $11 a video"** | "If you have someone in-house to run those tools, that's the cheaper route. What you pay us for is direction, three different angles, the frame-by-frame check and finished files. Compared with what you pay now per video, where does $150 sit?" |
| **"We already have vendors/creators"** | "Makes sense, keep them. Teams use us for the overflow: the extra concepts that don't justify a shoot. What happens today when a client needs ten videos in a week?" |
| **Rights: "Who owns it? Can we use it anywhere?"** | "On full payment you get a perpetual, worldwide licence to use, edit and publish the videos for your advertising. We only use product images you have rights to, and the music comes with a licence certificate. AI-generated material can't be guaranteed copyright-exclusive, and I'd rather tell you that now." (clausola 4 di `37`, da far vedere a un avvocato) |
| **Timing: "We need it in 48 hours" / "5 days is too slow"** | "Five business days is what I can promise with the checks in place. If there's a hard date, tell me now and I'll say honestly whether we can make it before you pay anything." |
| **"Send me a free sample first"** | "We don't do free work, it's how we keep quality and focus on paying projects. The pilot is the small, fixed-price way to test us: $450 for three videos." |
| **"Who have you worked with?"** | "We're a new studio, so the work you see is spec, built on real or invented products, not client jobs. I've spent 20 years in advertising; that's where the direction comes from. That's also why the first step is a small pilot." |
| **"Not now"** | "Understood. Is there a launch or a season when it would matter? I'll write then, not before." (promemoria con data nel registro) |

---

## 5. Preventivo di una pagina e incasso

### 5.1 Modello (EN, una pagina)
```
SCROLLCRAFT · PILOT PROPOSAL                                   {date} · valid 7 days
For: {Client}, {contact}

Your goal (in your words): {problem/job they described}

What you get
- 3 finished 9:16 video ads, {15} s each, three distinct angles on {product}
- Script, voice, captions, edit; 2 rounds of revisions
- One-page brief + storyboard approved by you before production
- Delivery: 5 business days after deposit, approved brief and your official assets

What we need from you
- Official product photos/packshots, approved claims list, words to avoid, logo files

Price
- $450 total · 50% ($225) to start, 50% on approval of the previews
- Previews are watermarked; final files are released on full payment

Quality promise
- Each video is checked frame by frame against the checklist in the brief. If one fails, we redo it once; if it still fails, you don't pay for it. No guarantee on ad performance.

Licence and AI
- On full payment: perpetual, worldwide, non-exclusive licence to use, edit and publish for your advertising (full terms attached).
- Content is AI-generated and labelled as such; no testimonials or invented customer experiences.
- Portfolio: we may show the work after it is live unless you tell us not to.

Next step: reply "approved" and I'll send the deposit invoice today.
Massimiliano Cori · Scrollcraft · www.scrollcraft.design · {postal address}
```
Le clausole complete sono quelle di `37` §8 (da far vedere a un avvocato). La riga "quality promise" e la clausola portfolio richiedono il sì di Massimiliano [I].

### 5.2 Passi per incassare
| # | Passo | Dettaglio |
|---|---|---|
| 1 | "Approved" per email | Vale come accettazione scritta della proposta [I, conferma legale] |
| 2 | Fattura acconto | **Due fatture Stripe separate** (50% + 50%). La pagina di pagamento della fattura Stripe non permette al cliente di pagare un importo parziale [V debole, riassunto di docs.stripe.com/invoicing/partial-payments], quindi non si fa una fattura unica "da pagare a metà". Scadenza 7 giorni. Il modulo fatture Stripe va completato prima (`36` §9.2) |
| 3 | Si parte solo ad acconto incassato | Poi brief e storyboard → approvazione → preventivo crediti interno e sì di Massimiliano per ogni generazione (CLAUDE.md) |
| 4 | Anteprime con filigrana | Link privato (cartella condivisa); revisioni entro i 2 giri |
| 5 | Saldo | Fattura saldo all'approvazione delle anteprime; file finali senza filigrana dopo il pagamento |
| 6 | Consegna | Master + versioni per piattaforma, certificato musica, nota di consegna (claim usati, etichetta AI, limiti d'uso: `37` checklist C) |
| 7 | Fiscale | IVA e fatturazione a clienti esteri: commercialista prima della prima fattura (`36` §9.2) |

Holiday Pack ($1.490) e ordini white-label: stesso schema 50/50 [I].

---

## 6. Dal primo pilota al caso studio e al cliente ricorrente

1. **Permesso scritto già nel preventivo** (riga portfolio) e richiesta esplicita alla consegna: nome sì/no, logo sì/no, numeri sì/no. Agenzie white-label: di norma niente nome del cliente finale; si chiede almeno "an agency in {city}" e una frase dell'agenzia [I].
2. **Misurare durante il lavoro** (nostri dati, sempre utilizzabili senza permesso): giorni dal brief alla consegna, revisioni, video passati al primo controllo.
3. **Chiedere i numeri a 14 giorni dalla messa online**: hook rate/thumb-stop, CTR, CPA rispetto ai loro creativi abituali. Un creativo si stanca in 7-14 giorni a spese medio-alte (`40` §3 [V debole]): è il momento naturale anche per il riordino.
4. **Struttura del caso** (challenge → solution → results, titolo con il risultato, una citazione del cliente scritta da lui) [V debole: guide B2B case study]. I casi studio influenzano il 73% dei decisori B2B (CMI 2025, via blog [V debole]). Mai citazioni scritte da noi (FTC [V]).
5. **Ricorrenza: la proposta successiva si fa alla consegna, non dopo.** "Based on these three, here's what I'd test next" con 3 nuovi angoli e due opzioni: Holiday Pack (finché vale) o un ordine a volume. L'upsell su clienti esistenti converte molto più che su nuovi contatti (60-70% contro 5-20%, fonte generica in `40` §3 [V debole]).
6. **Credito del pilota sul primo pacchetto entro 30 giorni**: proposta di `38` §6, solo con il sì di Massimiliano.
7. **Calendario fisso**: check-in a 14 giorni (numeri), a 30 giorni (nuovo lotto). Dopo 2 ordini, proporre un volume mensile fisso; retainer solo dopo pilota + pacchetto (`38` §4).

---

## 7. Marketing

### 7.1 Posizionamento in una frase
Costruito col metodo di April Dunford (*Obviously Awesome*: alternative reali, attributi unici, valore, clienti migliori, categoria [V debole sui riassunti, metodo noto]). Alternative reali dei clienti: shooting, creator UGC umani, strumenti self-serve tipo Arcads, fare da sé.

> **"Scrollcraft is a white-label AI video studio for agencies and media buyers who need more ad creative than their clients can shoot: finished, frame-checked videos in genuinely different angles, directed by a 20-year advertising creative."**

Variante brand: "Campaign-look video ads without a shoot, directed by a 20-year advertising creative, AI disclosed."

### 7.2 Prova sociale onesta senza clienti
| Prova | Come | Stato |
|---|---|---|
| 20 anni di carriera | Profilo LinkedIn con lavori e agenzie reali del passato (solo se verificabili e senza suggerire che siano lavori Scrollcraft) | [I] chiedere a Massimiliano cosa si può citare |
| Processo visibile | Pagina "How we work": brief, storyboard, checklist a fotogrammi, licenza | [I] |
| Spec work dichiarato | Ogni lavoro con "spec / concept, not a client job"; marchi reali con la formula di `37` §4 | [S] in parte presente |
| Prezzi pubblici e pilota a prezzo fisso | Riduce il rischio percepito più di una recensione | [S] |
| Dietro le quinte con numeri veri | Crediti, ore, errori trovati e corretti | [I] |
| Primo caso reale | §6 | da fare |
Da evitare: recensioni, loghi, contatori, testimonianze inventate (FTC [V]; `37`).

**Incoerenze trovate nel materiale attuale [S]:** `LinkedIn-descrizione.txt` (scratchpad) offre ancora "We'll make a free sample" e "campaign-grade product photos": contraddice la politica niente gratis (5/10) e la regola "immagini AI solo di campagna, non foto prodotto" (`PROCEDURE.md`). Va corretto prima di usarlo.

### 7.3 LinkedIn che porta conversazioni
Dati: profili personali circa 2x le impression delle pagine aziendali; risultati misurabili dopo 4-6 mesi; 3 post a settimana (`39` §1 [V debole]). La thought leadership spinge i decisori a riconsiderare i fornitori attuali (Edelman-LinkedIn 2024, ~3.500 manager [V debole, rapporto non aperto]).

Regole [I]: pubblico = agenzie e media buyer, non altri creator; ogni post insegna una cosa utile, nessun post "siamo bravi"; nessuna offerta nel post; si chiude con una domanda vera; risposta ai commenti in giornata e, a chi commenta con un problema concreto, un messaggio privato senza pitch.

Quattro formati a rotazione (3 a settimana):
1. **Insight (Challenger):** "Meta's system now collapses lookalike variants into one signal. Here's what a genuinely different angle looks like" + 3 fotogrammi.
2. **Dietro le quinte con numeri:** "One 15-second ad: brief, storyboard, 3 drafts, X credits, Y hours, the 4 errors we caught."
3. **Errore e regola:** "The AI changed the model's face between shots. Here's the check that catches it" (dal nostro `ERRORI.md`: materiale vero e unico).
4. **Opinione netta da 20 anni di pubblicità:** "AI can draw anything. It can't decide what the ad should say."

Messaggio privato dopo un commento o una connessione accettata (nessun pitch):
`Thanks for the comment on {post}, {First}. Curious: when your clients need new video creative fast, what usually slows it down?`

Misure (da `39` §7): impression medie, commenti di agenzie/media buyer, DM in entrata, conversazioni nate da LinkedIn. Giudizio a 90 giorni.

---

## 8. Riepilogo operativo (una riga per fase)
Email ≤ 80 parole, problema prima, una offerta, CTA d'interesse → risposta in giornata con 3 domande e due strade → call 15' (60% ascolto) o preventivo diretto → obiezioni: riconosci, fatto, domanda → preventivo di una pagina, 50% su fattura Stripe separata, finali dopo il saldo → numeri a 14 giorni, caso con permesso, proposta successiva alla consegna → LinkedIn 3 post/settimana che insegnano.

---

## Fonti
**Libri e metodi (riassunti consultati):**
- Neil Rackham, *SPIN Selling* (1988, ricerca Huthwaite su 35.000 vendite): https://www.supersummary.com/spin-selling/summary/ · https://oreilly.com/library/view/spin-selling/9781260027099
- Dixon e Adamson, *The Challenger Sale* (2011, CEB, 6.000+ venditori): https://www.shortform.com/blog/de/ceb-research-challenger-sale/ · https://www.penguin.co.uk/books/192421/the-challenger-sale-by-adamson-matthew-dixon-and-brent/9780241996195
- Keenan, *Gap Selling*: https://builtin.com/articles/gap-selling-52754 · https://www.rox.com/articles/gap-selling
- Christensen, Hall, Dillon, Duncan, "Know Your Customers' Jobs to Be Done", HBR set. 2016: https://www.innosight.com/?p=19201
- Eugene Schwartz, *Breakthrough Advertising* (1966), livelli di consapevolezza: https://book.personalmba.com/levels-of-awareness/ · https://blog.adbeat.com/5-levels-customer-awareness/
- Blair Enns, *The Win Without Pitching Manifesto*: https://pulserevops.com/knowledge/bs0067 · https://www.digitalpigeon.com/improve-your-workflow/winning-work-without-pitching-4-thoughts-from-blair-enns/
- April Dunford, *Obviously Awesome*: https://miro.com/templates/april-dunfords-positioning-template/ · https://www.wudpecker.io/blog/obviously-awesome-the-guide-to-perfecting-your-product-positioning
- Sandler, up-front contract: https://info.borovitz.sandler.com/blog/fix-sales-meetings-with-upfront-contracts
- Chris Voss, *Never Split the Difference*, domande orientate al no: https://www.tropicalmba.com/neversplitthedifference
- BANT: https://salesmotion.io/blog/bant-sales-framework
- Josh Braun, cold outreach: https://www.11x.ai/guides/josh-braun-cold-outreach-method

**Dati:**
- Gong Labs, CTA in 304.174 email: https://www.gong.io/resources/labs/this-surprising-cold-email-cta-will-help-you-book-a-lot-more-meetings/ (bloccata, via riassunto) · https://prospeo.io/s/cold-email-call-to-action
- Gong, rapporto parlato/ascolto: https://brendonrod.substack.com/p/gong30-mind-blowing-sales-stats-that
- Lavender, Cold Email Benchmark Report 2026: https://www.lavender.ai/blog/the-cold-email-benchmark-report · https://hunter.io/blog/cold-email-word-count
- HBR, "The Short Life of Online Sales Leads" (Oldroyd, McElheran, Elkington, mar. 2011): https://hbr.org/2011/03/the-short-life-of-online-sales-leads (via riassunti: https://ventureharbour.com/how-fast-do-marketing-leads-turn-cold-and-how-to-stop-it-happening/)
- Stripe, pagamenti parziali delle fatture: https://docs.stripe.com/docs/invoicing/partial-payments (bloccata, via riassunto)
- Meta, etichetta "AI info" negli annunci: https://www.cinerads.com/blog/ai-ad-disclosure-requirements · https://commonthreadco.com/blogs/coachs-corner/meta-ai-ad-labels-mandatory-disclosure-ecommerce-2026
- Edelman-LinkedIn B2B Thought Leadership Impact Report 2024: https://www.edelman.com/insights/thought-leadership-gets-b2b-buyers-back-into-game
- LinkedIn algoritmo (van der Blom): https://dreamdata.io/blog/linkedin-algorithm-2024-richard-van-der-blom
- Struttura casi studio B2B: https://brixongroup.com/en/compelling-case-studies-how-to-create-impactful-b2b-success-stories-in · https://www.zoomforth.com/blog/case-study-template/
- FTC, regola su recensioni e testimonianze false: https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials

**Nostri file:** `CLAUDE.md`, `ERRORI.md`, `PROCEDURE.md`, `digital-business/36`, `37`, `38`, `39`, `40`, `44`, `45`, `46`; `scratchpad/code/build_queue.py`, `scratchpad/invii-6ott.json`, `scratchpad/outreach-footer.txt`, `scratchpad/LinkedIn-descrizione.txt`.

## Nota dal campo (6/10): brand che usano già UGC AI scadenti
Rhute (brand capelli) ha risposto "not looking to explore this type of collaboration" a un'email generica del 29/9, pur avendo UGC AI con labiale fuori sincrono e scritte finte sui prodotti. [I] Chi pubblica UGC AI scadenti di solito li produce in casa con strumenti self-serve economici e giudica il risultato "sufficiente": il prezzo pesa più della qualità. Regola per quando si torna a scrivere ai brand: aprire con il difetto specifico visibile nei loro video, con tatto (es. "the label text on your bottle shifts between shots; we keep it locked"), mai con una presentazione generica; e solo a una persona con nome, mai a hello@/info@.
