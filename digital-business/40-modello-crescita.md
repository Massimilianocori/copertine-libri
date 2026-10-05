# Modello di crescita Scrollcraft — 2026-10-05

> **Riconciliazione del 5/10 (Claude, dopo lettura dei doc 38 e 40):** (1) il pilota resta **$450** (doc 38, approvato da Massimiliano): i "3 piloti fondatori a $250" di questo studio non si adottano; (2) "10 campioni inviati" va letto come **10 preventivi inviati**, perché la regola è niente gratis; (3) Higgsfield **non è cancellato**: il piano Ultra è attivo, con 529,88 crediti (verificato il 5/10). Le soglie di decisione (500-1.000 contatti, risposte positive 0,5-1%) restano valide.


Protocollo: `[VERIFICATO]` = dato da fonte in "Fonti" (o da file interni citati); `[IPOTESI]` = nostra stima.
Limite onesto: le fonti web sono snippet di ricerca (pagine non lette per intero) e molte sono blog di
vendor con interesse commerciale; i casi "da zero a 10k" sono post di founder, non dati auditati.
Legge con `11`, `14`, `16`, `28`, `29`, `00-STATO-PROGETTO`.

---

## 1. Come crescono i servizi produttizzati (da zero a 5-10k/mese)

`[VERIFICATO, qualità bassa]` Casi pubblici: video production produttizzato a 8k MRR in 3 mesi (Indie
Hackers, post pre-2025); servizio produttizzato 0 -> 10k MRR in 3,5 mesi, ma dopo ~30 tentativi in 5 anni;
un'agenzia ferma a 3k/mese che ha rifatto tutto come servizio produttizzato ed è arrivata vicino a 10k.
Sono racconti di sopravvissuti, non tassi di successo, e non sono del 2025-26.
`[VERIFICATO, guru]` Vari "AI video agency" (Sora ads a 6.200 $ per 3 mesi, 24k->56k in un mese) vendono a
servizi locali (cucine, ecc.), con ads a pagamento e call: non sono il nostro caso (DTC USA, cold email).

Pattern ricorrente `[IPOTESI da questi casi]`: (a) prima chiusura da rete o canale caldo, non da freddo
puro; (b) offerta unica, stretta, prezzo fisso; (c) il salto a 5-10k arriva con i retainer, non con i
singoli. Errori tipici: troppi canali insieme (noi a fine settembre: email, IG, Sienna, Upwork, Outlier),
prezzo troppo basso senza scala, nessun caso con numeri.

Tempi realistici per noi `[IPOTESI]`: partenza da zero clienti, dominio nuovo, nessun contatto USA ->
primo pagamento in 4-10 settimane, primo retainer in 3-4 mesi, 5k/mese in 6-9 mesi nel caso base.

## 2. Unit economics

| Voce | Dato | Stato |
|---|---|---|
| Costo credito per video 15 s skincare (video 11) | 191,6 crediti = ~9,6 EUR (1 credito = 0,05 EUR) | VERIFICATO (00-STATO). Sopra il range "1,3-5 EUR" del brief: quel range non vale per il 15 s 1080p Seedance con voce |
| 4 cicli di rigenerazione (come il video 1) | ~38 EUR a video | IPOTESI su dato reale |
| Prezzo di vendita | 115-179 $ (Single 179, Growth 158/video) | listino `11` |
| Margine lordo su crediti, 1 ciclo / 4 cicli | ~94% / ~74% a 158 $ | calcolo |
| Tempo per video | 45 min | IPOTESI, mai misurata su 10 video |
| Margine vero | dominato dal tempo, non dai crediti | calcolo |

Capacità. `[VERIFICATO, bassa]` utilizzo target solo-freelancer 70-90%, agenzie produttizzate 60-75% per
persona (kolonell). Il file `14` assume 112 h/mese di produzione (65% di 173 h) e ~150 video teorici:
`[OTTIMISTICO]`. Nei primi 3 mesi outreach, campioni, QA, risposte, fatturazione consumano più del 35%
del tempo, e Massimiliano è non tecnico e dichiara 20-30 min/giorno nei file `28`/`29` (~10 h/mese!), con
Claude che produce. Quindi il limite reale è la **approvazione umana**, non le ore di generazione.
Stima prudente `[IPOTESI]`: 40-60 video/mese consegnabili con QA fotogramma-per-fotogramma (regola
CLAUDE.md) = 6-9k $/mese al listino Growth. Resta sopra l'obiettivo a 180 giorni: la capacità non è il
vincolo prima di ~8k/mese.

Subappalto/assunzione `[VERIFICATO, bassa: selfemployed.com, kolonell]`: assumere quando ci sono 8-12k/mese
per 3 mesi consecutivi E si rifiuta lavoro; subappalto tipico paga il fornitore 40-60% del prezzo,
margine 40-60%. Per noi `[IPOTESI]`: prima subappaltare QA/montaggio (ore umane), non la direzione.
Non prima di 3 mesi sopra 6k.

## 3. Retention

- `[VERIFICATO]` Retainer: vita media 56 mesi e churn annuo 18% per agenzie consolidate; piccole agenzie
  (<10 persone) churn >30%; nel 2026 solo il 3% delle agenzie si aspetta clienti oltre 36 mesi, i più
  12-24 mesi; per un'agenzia AI sana: churn <5%/mese, vita >12 mesi, NRR >100% (Swydo, SEJ, dev.to).
- `[VERIFICATO]` Domanda di creatività: budget 5-15k/mese -> 3-5 nuovi creativi a settimana; 15-50k ->
  8-15 a settimana; ogni 10 creativi 1-3 vincenti; a 1.000 $/giorno un creativo si stanca in 7-14 giorni
  (Billo, Admetrics, Superscale). Il Growth (12 video + 12 varianti/mese) copre il fascio piccolo: il
  retainer di "testing hook mensile" è giustificato da dati.
- `[VERIFICATO]` Upsell su clienti esistenti converte 60-70% contro 5-20% su nuovi prospect (Copper,
  generico). Nessuna fonte dà il tasso pilota -> retainer per servizi creativi: **non esiste dato**.
- `[IPOTESI]` Per noi (piccoli DTC, zero track record): churn 8-12%/mese, vita 8-12 mesi. LTV Growth
  (1.890 $ x 8-12 mesi x ~85% margine) = ~13-19k $ lordi; LTV Starter una tantum = 845 $. Pilota ->
  pacchetto 25-35%, pacchetto -> retainer 20-30% (da misurare, non assumere).
- Scala di salita: campione gratis -> pilota 250 $ -> Starter 845 $ -> Growth 1.890 $/mese. Il salto
  250 -> 1.890 è 7,5x: troppo largo; serve un passo intermedio (vedi §7).

## 4. Riconciliazione con le stime esistenti

| Punto | Nostra stima | Dato verificato | Giudizio |
|---|---|---|---|
| Risposta email (`14`: base 6%) | 6% | media 3,43%; 2,09% su 1,37M email; top 25% >5,5% (Mailshake, Prospeo) | OTTIMISTICA: la base è già top-quartile |
| Chiusura netta (`14`: base 1,1%) | 1,1% | ~0,2% media (1 su 464); email->meeting 0,1-0,5% | OTTIMISTICA 5x; il pessimistico 0,4% è già sopra media |
| Mese 2 base 4.550 $, mese 3 base 6.700 $ | | a 0,2% su 650-800 email = 1-2 clienti/mese | Ottimistiche ~4x. Lo scenario realistico = il pessimistico di `14` |
| `28`: 15 risposte/400 contatti, 3% e 8-10% | | 3,4% media; 5,5% top 25% | 8-10% col campione = IPOTESI non verificata; plausibile 4-6% |
| Prezzi: `11` (845 Starter, 1.890 Growth) vs `28`/`29` (5 annunci 250 $, mensile 6+6 a 900 $) | | | INCOERENTE: due listini. 250 $/5 = 50 $/pezzo; 900/12 = 75 $/pezzo, cioè 55-70% sotto il mercato AI-UGC (140-200 $) |
| Capacità `14` (150 video, 12-17k $) | | utilizzo 60-75%, approvazione umana 20-30 min/giorno | OTTIMISTICA; vedi §2 |
| Costo UGC 15 s 1,3-5 EUR | | misurato 9,6 EUR | SOTTOSTIMATO ~2x per il 15 s con voce |
| Soglia `29`: "≥1 cliente su ~500 contatti" | | | DEBOLE: a tasso medio 0,2%, P(0 clienti su 500) = 0,998^500 = ~37%; su 1.000 = ~13% |
| Stato reale (22/9) | | ~40+ email, 1 risposta = rifiuto | Compatibile con tasso medio, nessuna prova di canale rotto né funzionante |

## 5. KPI e soglie di decisione

Principio: non decidere su "clienti" con campioni piccoli; decidere su tassi a monte, con volumi minimi.
Tutte le soglie sono `[IPOTESI]` calibrate sui benchmark del §4.

| Indicatore | Verde | Giallo | Rosso | Azione |
|---|---|---|---|---|
| Consegnabilità (inbox placement, bounce <3%) | ok | | spam/bounce alti | si risolve prima di giudicare l'offerta |
| Risposte positive / email (min 500) | >=1% | 0,5-1% | <0,5% | rosso: cambiare nicchia/messaggio, non fermarsi |
| Campione inviato -> risposta | >=15% | 8-15% | <8% | rosso: campione/oggetto da rifare |
| Risposta positiva -> pilota pagato | >=25% | 10-25% | <10% | rosso: prezzo/offerta |
| Pilota -> pacchetto/retainer (min 4 piloti) | >=30% | 15-30% | <15% | rosso: qualità/risultati, non il canale |
| Ore reali per video (media su 10) | <=35 min | 35-60 | >60 | rosso: processo o prezzo su |
| Margine lordo (crediti + sub) | >=75% | 60-75% | <60% | rosso: più cicli di QA del previsto |
| Concentrazione | nessun cliente >50% | | >60% | cercare il secondo |

Regole: **Insistere** se consegnabilità ok e (positive >=0,5% oppure >=1 pilota entro 1.000 contatti).
**Cambiare nicchia** (es. agenzie paid social, brand >5k$/mese di ads) se a 1.000 contatti e >=10
campioni mandati le positive sono <0,5% e zero piloti. **Scalare** (seconda mailbox, subappalto QA) solo con
2 retainer attivi da >=2 mesi, margine >=75%, ore di produzione >=70% della capacità.

## 6. Rischi

1. **Dipendenza da Higgsfield** `[VERIFICATO]` I costi dipendono dal modello e cambiano: un clip Seedance
   2.0 5 s 720p ~22 crediti vs Kling 3.0 ~7 (3x); crediti da pacchetto scadono in 90 giorni, quelli
   da abbonamento non si accumulano; l'unlimited è un prodotto a pass (listino 99 $/giorno luglio 2026,
   contro i 35 EUR/24 h visti da Massimiliano: prezzi che si muovono). Veo 3.1 via Google AI Pro ($19,99,
   20 crediti a clip) è già un secondo canale verificato (`11`). `[IPOTESI]` Mitigazione: workflow
   scritto per modello (non per piattaforma), un secondo fornitore testato su 1 brief entro 90 giorni,
   credito mensile non oltre 1 mese di consumo. Incoerenza interna da chiarire: `14` dà Higgsfield
   cancellato, `00-STATO` lo dà Ultra attivo.
2. **Commoditizzazione** `[VERIFICATO, vendor]` AI-UGC a 5-30 $ a video contro 150-500 $ umani; Creatify
   1,65-3,90 $ per ad; abbonamenti Arcads ~110 $/mese, MakeUGC 59, HeyGen 29, Creatify 39. Il nostro
   prezzo (140-179 $) è 5-30x il costo tool: si regge su direzione, QA di coerenza, testing
   strutturato e non dover imparare il tool. Chi sa usare i tool direttamente ci sostituisce.
3. **Piattaforme che vendono ai brand** `[VERIFICATO]` Le piattaforme sono self-serve e si
   posizionano su "ecommerce testing". `[IPOTESI]` Il segmento che non le usa: brand piccoli senza tempo,
   agenzie che vogliono volume white-label. Per questo l'agenzia come cliente (un cliente = molti brand) è
   più difendibile del brand piccolo.
4. **Rischio normativo** `[VERIFICATO]` FTC su testimonial sintetici non dichiarati: dichiarare sempre
   l'AI (già nella nostra regola).
5. **Rischio di processo** `[IPOTESI]` Disperdersi su Sienna/IG/Upwork mentre l'unica leva misurabile è
   il canale outbound: ogni ora fuori dall'outbound ritarda il dato che decide tutto.

## 7. Raccomandazione unica: piano 30/90/180 giorni

**Modello**: servizio unico, brand DTC skincare/beauty piccoli (+ agenzie paid social come secondo
bersaglio), outbound email+LinkedIn, scala di salita a 4 passi, un solo listino. Decisione sull'imbuto,
non sul fatturato.

**Un solo listino (risolve l'incoerenza 11 vs 28/29)** `[IPOTESI]`:
- Campione gratuito (solo per i 5/giorno migliori).
- **Pilota fondatore: 3 posti a 250 $** (5 annunci), solo in cambio di numeri di risultato + permesso
  caso; dopo i primi 3 il pilota sparisce e si parte da Starter 845 $.
- **Starter 845 $** (5 video + 5 varianti) come primo acquisto standard.
- **Retainer di ingresso 900-1.200 $/mese** (6 video + 6 varianti, 3 mesi) per i primi 2 clienti, poi
  Growth 1.890 $. Il salto 250 -> 900 -> 1.890 è graduale; la scalata di prezzo è guidata dai casi, non
  dal calendario.

**Giorni 0-30 (5 ott - 4 nov): misurare l'imbuto**
- Obiettivo: 500 contatti cumulativi (compresi i già inviati), consegnabilità >95%, 10 campioni inviati,
  >=5 risposte positive, 1 pilota pagato (250-845 $).
- Misurare ore reali e crediti reali sui primi 10 video (chiude l'IPOTESI dei 45 min).
- Solo outbound + LinkedIn manuale; Sienna/IG ridotti a 1 post/settimana.
- Passaggio: positive >=1% -> fase 2; 0,5-1% -> cambiare oggetto/campione e andare a 800; <0,5% con
  consegnabilità ok -> cambiare messaggio, non ancora la nicchia.

**Giorni 31-90 (a ~3 gennaio): primo cliente ricorrente e primo caso**
- Obiettivo: 1.000-1.500 contatti cumulativi; 3 piloti completati; **1 retainer attivo** (MRR 900-1.900 $);
  1 caso con numeri (CTR/CPA del cliente); ricavi cumulativi >=3.000 $; margine >=75%; tempo/video <=35-45 min.
- Aggiungere seconda mailbox/dominio solo se consegnabilità ok e positive >=1%.
- Provare 1 fornitore alternativo di generazione su un brief reale.
- Passaggio a fase 3: >=1 retainer + >=1 caso. Se a 1.000 contatti zero piloti e positive <0,5%:
  **cambiare nicchia** (agenzie o brand con ads >5k$/mese), tenendo listino e processo.

**Giorni 91-180 (a ~3 aprile 2027): ricorrente stabile**
- Obiettivo caso base `[IPOTESI]`: MRR 3.000-5.000 $ (2-3 retainer Growth/ingresso) + 1-3 Starter al mese;
  churn <=8%/mese; 1 cliente agenzia o 1 partner white-label; nessun cliente >50% del ricavo.
- Caso ottimistico 8-10k $ MRR (~7.500-9.000 EUR): possibile ma non è il piano; richiede che il tasso
  di chiusura superi 1% e che i retainer superino i 12 mesi.
- Scalare solo con 2 retainer da >=2 mesi: subappaltare QA/montaggio; assumere o aprire a freelance
  solo dopo 3 mesi consecutivi sopra 6-8k.
- **Fermarsi/ripensare** se a 180 giorni, con >=1.500 contatti in due nicchie, MRR <1.000 $: il mercato
  sta dicendo che l'offerta non è comprata; a quel punto riconvertire in formato white-label per agenzie
  o in un prodotto diverso, non investire altro in outbound.

**Numeri da correggere subito nei file esistenti**: tasso di risposta base 6% -> 3-4%; chiusura base 1,1%
-> 0,2-0,5%; costo UGC 15 s -> ~10 EUR a ciclo; soglia di decisione di `29` da "1 cliente su 500" a
"positive >=0,5-1% su 500-1.000".

---

## Fonti (consultate 2026-10-05, da snippet di ricerca)

- Indie Hackers — Growing a productized service to $10k MRR: https://www.indiehackers.com/post/growing-a-productized-service-to-the-coveted-milestone-of-10k-mrr-AauqiXvpQbDGOZMrQfrn
- Indie Hackers — 0 to 10k MRR in 3,5 mesi: https://www.indiehackers.com/post/0-10k-mrr-in-3-5-months-a-step-by-step-guide-on-exactly-what-i-did-1f3ce44511
- Indie Hackers — video production produttizzato a 8k MRR in 3 mesi: https://www.indiehackers.com/post/8k-mrr-in-3-months-after-launch-the-power-of-productized-services-021d0b8c83
- Gist.ly — agenzia con Sora ads (claim non verificabile): https://gist.ly/youtube-summarizer/how-to-build-a-100kmonth-agency-with-sora-ads
- dev.to — retention clienti per agenzie AI: https://dev.to/scalelogix_ai/how-to-retain-ai-agency-clients-a-playbook-for-long-term-operator-success-521a
- SHNO — statistiche agenzie marketing (churn): https://www.shno.co/marketing-statistics/marketing-agency-statistics
- Swydo — KPI churn clienti agenzie: https://www.swydo.com/?p=21556
- Search Engine Journal — Agency Playbook 2026: https://www.searchenginejournal.com/rundowns/2026-marketing-agency-playbook-data-backed-ai-pivots-that-ignite-growth
- Mailshake — Cold Email Benchmarks 2026: https://mailshake.com/blog/cold-email-benchmarks-2026/
- Prospeo — Cold Email Benchmarks 2026: https://prospeo.io/s/cold-email-benchmarks
- SmartReach — State of Cold Email 2026: https://smartreach.io/reports/state-of-cold-email/
- Billo — How many ad creatives do you need (2026): https://billo.app/blog/how-many-ad-creatives-do-you-need/
- Admetrics — Creative Scaling Meta Ads 2026: https://www.admetrics.io/post/creative-scaling-the-ultimate-guide
- Superscale — Creative testing benchmarks (luglio 2026): https://superscale.ai/learn/creative-testing-benchmarks/
- Creatify — 8 best AI UGC ad tools 2026 (vendor concorrente, prezzi tool): https://creatify.ai/blog/the-8-best-ai-ugc-ad-tools-in-2026
- Krea — Higgsfield pricing 2026: https://www.krea.ai/blog/higgsfield-pricing-explained-2026-unlimited-credits-and-real-monthly-costs
- Creatify — Higgsfield review 2026 (vendor concorrente): https://creatify.ai/blog/higgsfield-ai-review-(2026)-is-it-worth-it
- Self-Employed — quando assumere subappaltatori: https://www.selfemployed.com/when-to-hire-subcontractors-solopreneur/
- Kolonell — da freelancer ad agenzia 2026: https://kolonell.com/en/blog/freelancer-to-web-agency-scaling-team-2026
- Copper — da progetti singoli a retainer: https://try.copper.com/resources/9-strategies-to-turn-one-time-projects-into-retainer-clients
- Stackmatix — struttura pilot di agenzia: https://www.stackmatix.com/blog/marketing-agency-pilot-scope-startups
- File interni: 11-strategia-prezzi, 14-stime-fatturato-mesi-1-3, 16-strategia-volume-outreach, 28, 29, 00-STATO-PROGETTO.

Non verificato: tasso pilota -> retainer per servizi creativi (nessuna fonte); churn di AI-UGC studio solisti;
tempo reale per video; stato di Higgsfield (cancellato o attivo); prezzi unlimited (due valori diversi).
