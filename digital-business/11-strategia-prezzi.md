# Strategia prezzi — listino a scala (video singolo + pacchetti + abbonamento)

Sostituisce il listino in `05-A1-outreach-offer-EN.md` §OFFER e la sezione prezzi di
`portfolio/index.html`. Protocollo: `[VERIFICATO]` con fonte, `[IPOTESI]` altrimenti.

---

## 0. La tesi — il vincolo è il tempo, non il costo dello strumento

Il costo marginale di un video è quasi nullo: Veo 3.1 costa **20 crediti**, cioè ~$0,40 con Google AI
Pro ($19,99 per 1.000 crediti) `[VERIFICATO in sessione, vedi 10-video-veo3-prompt-pronti.md §1]`.
Il costo vero è **il tuo tempo**: generazione, verifica a fotogrammi, rigenerazioni, montaggio,
export. Il video 1 della vetrina ha richiesto **4 cicli di rigenerazione** prima di essere
pubblicabile.

Quindi la strategia giusta non è "vendere più video", è **alzare il ricavo per ora di produzione**.
Tutto il listino sotto è costruito su questo principio, e l'elemento a margine più alto non è un
pacchetto più grosso: è la **variante di hook** (§4), che riusa un video già prodotto.

**Stima di lavoro per video `[IPOTESI, basata sulla sessione reale]`: ~45 minuti** tutto compreso
(generazione + QA + rigenerazioni + montaggio + export). Da rimisurare dopo i primi 10 video reali.

---

## 1. Dove siamo nel mercato `[VERIFICATO]`

| Riferimento | Prezzo |
|---|---|
| UGC short-form, creator principiante | $50–150 / video |
| UGC short-form, tipico | $150–500 / video |
| UGC creator esperto, con diritti pubblicitari | $300–1.000+ / video |
| Costo per asset nel testing di hook | $175–398 / asset |
| Diritti d'uso pubblicitari | +30–50% sul base |
| Diritti perpetui | +100–150% |
| Whitelisting / Spark Ads | +30% al mese |
| Consegna rush | +25–50% |
| Sconto pacchetti prepagati | −10–25%, validità 6–12 mesi |
| Abbonamenti a crediti | $99–999+/mese per 10–200 video |

Due divisioni di mercato importanti `[VERIFICATO]`:
1. **Il flat per video vince fino a ~10 video/mese**; l'abbonamento vince dai 20+ in su, dove il flat
   costerebbe 3–10×. Non sono alternative: sono **due clienti diversi**. Servirli entrambi non è
   incoerenza, è copertura.
2. Nel testing di hook **le varianti perdenti costano quanto quella vincente** ($175–398 l'una). È
   esattamente il punto dove l'AI ha un vantaggio strutturale, ed è il nostro argomento di vendita
   più forte.

---

## 2. Il problema del listino attuale

| Piano attuale | Video | Prezzo | $/video | $/ora stimata |
|---|---|---|---|---|
| First project | 5 una tantum | $400 | $80 | ~$107 |
| Starter | 18/mese | $999/mese | $55 | ~$73 |
| Growth | 36/mese | $1.799/mese | $50 | ~$67 |

Tre difetti:

1. **Niente per chi vuole un solo video.** Chi vuole provare con uno solo oggi non compra nulla: il
   minimo è un pacchetto da 5. È un "no" che non arriva nemmeno in trattativa.
2. **Costringe all'abbonamento chi sta in mezzo.** Chi ha bisogno di più di 5 video ma non di un
   impegno mensile non ha alcuna casella da spuntare — esattamente il buco che avevi individuato.
3. **Il piano Growth non è consegnabile.** 36 video × 45 minuti = **27 ore al mese** di sola
   produzione, senza un minuto per l'outreach. Il tier più costoso è quello che ti manderebbe in
   blocco per primo.

---

## 3. Il listino — versione finale `[approvata 2026-09-15]`

Principio che risolve la tensione tra due vincoli in conflitto — *stare in linea col mercato* e
*non far mai salire il prezzo unitario salendo di tier*: **le varianti di hook sono incluse nei
pacchetti**. Costano 10 minuti l'una e cambiano la metrica che il cliente guarda davvero.

| Tier | Video | Varianti incluse | Asset totali | Prezzo | $/video | **$/asset** |
|---|---|---|---|---|---|---|
| Singolo | 1 | — | 1 | $179 una tantum | $179 | $179 |
| Starter | 5 | 5 | 10 | $845 una tantum | $169 | **$85** |
| **Growth** | 12/mese | 12 | 24 | $1.890/mese | $158 | **$79** |
| Scale | 25/mese | 30 | 55 | $3.490/mese | $140 | **$63** |

Il prezzo per video **scende** a ogni gradino (179 → 169 → 158 → 140), quindi non si ripresenta il
difetto del listino vecchio. Ma il numero che il cliente confronta con i concorrenti è il **costo per
asset utilizzabile**, che crolla da $179 a $63 — perché nel testing di hook le varianti perdenti
costano quanto quella vincente ($175–398 l'una sul mercato `[VERIFICATO]`).

**Una tantum anche sui tier alti:** Growth e Scale si possono comprare senza abbonamento a **+15%**,
crediti validi 90 giorni. Nessuno è costretto a un impegno mensile — l'abbonamento è semplicemente la
casella più conveniente.

**Il singolo a $179 non è il primo acquisto** `[corretto 2026-09-15]`. Il primo contatto è il
**campione gratuito**, che è la CTA principale del sito e di tutto l'outreach: finché regaliamo un
video, nessuno paga $179 per il primo. Il singolo a pagamento serve al passo *dopo* — "già avuto il
campione? ordinane uno su tuo brief" — e la differenza dev'essere detta esplicitamente:

| | Campione gratuito | Singolo a $179 |
|---|---|---|
| Chi sceglie il prodotto | noi | il cliente |
| Chi scrive il copione | noi | su brief del cliente |
| Revisioni | nessuna | una |
| Scopo | dimostrare la qualità | un ad vero su un prodotto specifico |

Senza questa distinzione il tier singolo è morto: è la prima cosa che un prospect fa notare.

### Verifica contro il mercato

| | Noi | Mercato AI UGC `[VERIFICATO]` | Scarto |
|---|---|---|---|
| Video singolo | $179 | $140–200 (benchmark $150 per testimonial con avatar) | **in linea** |
| 12 video/mese | $158/video | ~$212/video (AI Vidia) | −25% |
| 25 video/mese | $3.490/mese | retainer tipici $2.000–10.000/mese | **dentro la fascia** |
| Scale per video | $140 | $212 | −34% |

Posizione scelta: **in linea sul singolo, 25–34% sotto sui tier alti.** Abbastanza sotto da essere il
preventivo più conveniente sul tavolo, non così sotto da far sospettare che il lavoro sia di serie B.
Il riferimento a $4.500 per 12 video (pacchetti full-service) non è comparabile: quelli includono
strategia e media buying che noi non vendiamo.

---

## 4. Add-on — dove sta davvero il margine

| Add-on | Prezzo | Perché |
|---|---|---|
| **Variante di hook** oltre quelle incluse | **$49** | Si rigenerano i primi 3 secondi, il resto si riusa: ~10 minuti di lavoro. Il mercato fa pagare l'asset pieno ($175–398) per ogni hook testato `[VERIFICATO]`. |
| **Rush 24h** | **+40%** | Standard di mercato 25–50% `[VERIFICATO]`. Stesso lavoro, solo prima in coda. |
| **Diritti d'uso pubblicitari** | **inclusi** | Il mercato li fa pagare +30–50%, i perpetui +100–150% `[VERIFICATO]`. A noi non costano niente: non c'è un creator umano da pagare. |

**La variante è il prodotto a resa più alta del listino** — vedi §5. Ed è anche quello di cui il
cliente ha più bisogno, perché il testing di hook è il motivo per cui compra creative. Per questo ne
includiamo una per video in ogni pacchetto: è il regalo che ci costa meno e vale di più.

I diritti inclusi sono un differenziatore gratuito per noi e costoso per i concorrenti: da dire
esplicitamente in ogni trattativa.

---

## 5. Resa per ora — la tabella che decide tutto

A 45 minuti per video e 10 minuti per variante:

| Prodotto | Ore di lavoro | Ricavo | **$/ora** |
|---|---|---|---|
| **Variante di hook singola** | 0,17 | $49 | **~$294** |
| Video singolo | 0,75 | $179 | ~$239 |
| Starter (5 + 5) | 4,6 | $845 | ~$184 |
| Growth (12 + 12) | 11,0 | $1.890 | ~$172 |
| Scale (25 + 30) | 23,75 | $3.490 | ~$147 |
| *(vecchio Growth, 36/mese)* | *27,0* | *$1.799* | *~$67* |

Tre conseguenze operative:

1. **Il pavimento si alza da ~$67 a ~$147/ora.** Il tier peggiore del listino nuovo rende più del
   doppio del tier peggiore di quello vecchio.
2. **Il tetto realistico è ~$3.800/mese da solo.** Con ~25 ore/mese di produzione sostenibili accanto
   all'outreach: un cliente Scale (23,75 ore → $3.490) oppure **due clienti Growth** (22 ore →
   $3.780, la combinazione migliore). Non servono dieci clienti: ne servono due giusti.
3. **Le varianti restano il prodotto migliore al minuto.** Includerle nei pacchetti non è generosità:
   è il modo di alzare il valore percepito senza toccare il prezzo per video, e di tenersi la leva
   dell'upsell a $49 per chi ne vuole ancora.

---

## 6. Come è presentato sul sito `[FATTO 2026-09-15]`

- **Quattro schede pari** Single ad / Starter / Growth / Scale, in ordine di prezzo crescente, con
  badge "Most popular" su Growth (miglior equilibrio tra resa oraria e dimensione dell'ordine).
  `[corretto 2026-09-15]` Il singolo era stato messo come riga stretta sotto la griglia: sbagliato,
  è un prodotto che vendiamo come gli altri e va presentato allo stesso modo. Il suo posizionamento
  rispetto al campione gratuito si dice nella nota sotto il bottone ("The step after your free
  sample"), non rimpicciolendo la scheda.
- Le schede senza badge riservano comunque l'altezza del badge (`.price:not(.featured)::before`), così
  titoli, prezzi e bottoni restano allineati su tutta la riga.
- Il titolo della sezione dice la cosa differenziante, non "Pricing": *"Every video ships with a
  second hook, free."*
- La metrica in evidenza su ogni scheda è il **costo per ad asset** ($85 / $79 / $63), non il costo
  per video: è il numero su cui vinciamo il confronto.
- Nel confronto col mercato la riga nostra dice **"From $63 / ad asset"** contro i $150–500 per video
  dei creator umani. Prima diceva "a fraction of that", che con $179 sul singolo non sarebbe più
  stato vero.
- Diritti d'uso inclusi ripetuti su ogni scheda e in una voce FAQ dedicata: è gratis per noi e
  costoso per tutti gli altri.
- Una voce FAQ dedicata alla domanda che arriverà di sicuro: *"se il campione è gratis, cosa sto
  pagando?"* — vedi la tabella in §3.

**Trappola tecnica scoperta sul campo `[VERIFICATO 2026-09-15]`:** la riga del video singolo era
invisibile sul sito pur essendo presente nell'HTML. Causa: la classe CSS si chiamava `single-ad`, e
**gli ad blocker nascondono gli elementi con "ad" nel nome della classe** (EasyList e simili hanno
regole generiche su `-ad`, `ad-`, `banner`, `sponsor`, `promo`). Rinominata in `.oneoff`.
**Regola per il futuro:** su un sito che vende pubblicità, mai usare `ad`, `banner`, `promo` o
`sponsor` nei nomi di classi e id. Un'opzione di prezzo nascosta da un ad blocker non dà nessun
errore — semplicemente non incassi, e non te ne accorgi.

---

## 7. Cosa resta da verificare

- I **$179 del singolo** sono al limite alto del range di mercato ($140–200) `[VERIFICATO]`. Sono
  stati scelti per dare spazio alla scala sopra: essendo la scala decrescente, il singolo fa da
  soffitto a tutto il listino. Se il singolo non converte mai in outreach, è il primo numero da
  rivedere — ma prima di abbassarlo, testare un'offerta a tempo sul primo acquisto, che non intacca
  l'ancora.
- I **45 minuti/video** sono `[IPOTESI]` da rimisurare sui primi 10 video reali. Se scendono a 30,
  tutta la colonna $/ora sale del 50%.
- La **validità 90 giorni** è più stretta dello standard di mercato (6–12 mesi) `[VERIFICATO]`: crea
  urgenza e margine su crediti non usati, ma aumenta l'attrito. Se un prospect obietta, concederla a
  180 giorni è una leva di chiusura a costo zero.
- **Il vincolo vero non è il prezzo, è la capacità.** A due clienti Growth siamo pieni. Il terzo
  cliente o alza i prezzi o richiede di velocizzare la produzione: non esiste una terza via
  sostenibile da solo.

---

## 8. Incasso — Stripe Payment Links `[DA COMPLETARE dall'utente]`

Il sito è statico su Netlify: niente backend, quindi la via corretta sono i **Payment Links** di
Stripe (link generati dalla dashboard, nessun codice da scrivere). I bottoni del sito puntano già a
quattro segnaposto `https://buy.stripe.com/REPLACE_*` da sostituire.

Quattro link da creare su dashboard.stripe.com → Payment links:

| Bottone nel sito | Tipo | Importo |
|---|---|---|
| `REPLACE_SINGLE` | pagamento singolo | $179 |
| `REPLACE_STARTER` | pagamento singolo | $845 |
| `REPLACE_GROWTH` | **ricorrente mensile** | $1.890 |
| `REPLACE_SCALE` | **ricorrente mensile** | $3.490 |

Su ogni link attivare i **campi personalizzati** "Product URL" e "Brand notes", così il brief arriva
insieme al pagamento e non serve una mail di andata e ritorno.

**Prerequisito fiscale `[DA VERIFICARE col commercialista]`:** per incassare serve una posizione
fiscale in regola (partita IVA) — Stripe in Italia richiede i dati dell'attività. Per servizi B2B a
clienti USA l'IVA di norma non si applica (operazione fuori campo), ma la fattura va comunque emessa
secondo le regole italiane. Questo è l'unico punto della strategia che non si risolve dal sito.

## Fonti

- Studioverse — UGC Pricing 2026, modelli di prezzo completi: https://studioverse.io/blog/ugc-pricing-2026-complete-guide
- Sepia — Pay As You Go vs abbonamenti mensili per AI video ad: https://sepia-lab.com/en/blog/pay-as-you-go-ai-video-ad-tools
- Novoads — sei modelli di sourcing UGC e costo reale per video: https://novoads.ai/en/blog/ugc-platforms-for-brands
- inBeat Agency — Performance Creative Pricing Guide 2026: https://inbeat.agency/blog/performance-creative-pricing-guide
- UgcAd AI — UGC Rates Guide 2026, add-on e diritti: https://ugcad.ai/blog/ugc-rates-guide-2026/
- SoloPricing — come prezzare i progetti rush 2026: https://www.solopricing.com/how-to-price-rush-projects-2026
