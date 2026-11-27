# Ricerca della sera, 27/11/2026: far rendere le visite che abbiamo già, oltre AdSense

Approccio di stasera (diverso da quelli del 25, 26 e 27/11): **niente idee nuove e niente siti nuovi**. Solo una domanda: per ogni sito che ha visite vere, esiste un pagatore (affiliazione, contatti, sponsor, prodotto, altra rete pubblicitaria) che accetta una persona con partita IVA forfettaria, che c'entra con la pagina e che scrive quanto paga?

Non ripeto: `affiliazioni-2026-10-17.md` (8 programmi), `intelaiatura/monetizzazione-traffico-2026-11-13.md` (13 riquadri, 535 €/anno), `intelaiatura/reti-pubblicitarie-2026-11-13.md` (Journey, Ezoic, Raptive), `fronti-2026-11-07-alto-compenso.md` e `fronti-2026-11-11-pagatori-alti.md` (Wise, Remitly, Babbel, Lingoda), le ricerche del 25-27/11 e il pacchetto delle 4 prove (PIANO-FATTURATO sez. 9). Dove un tema era già stato chiuso, scrivo solo il **fatto nuovo** letto stasera.

---

## 0. In breve

1. **Stasera non ho trovato nessun pagatore nuovo che valga più di 50 € l'anno sul traffico di oggi.** Ne ho controllati 9. Tutti insieme: circa **23 € l'anno prudente e 130 € centrale**. Il motivo è un conto solo (sez. 2): con 61.500 visite l'anno la rete produce al massimo circa 43 acquisti l'anno su tutti i riquadri messi insieme.
2. **Quindi la decisione del 19/11 regge, con i numeri: le affiliazioni nuove restano spente.** 130 € l'anno non valgono il dubbio fiscale (Camera di Commercio + INPS ≈ 3.050 € l'anno).
3. **Il dato che manca davvero è un altro.** Abbiamo **1.742 link di affiliazione già accesi su 1.361 pagine** (conteggio di stasera nelle cartelle `sito/`) e **0 clic contati**. Valgono, a stima, **90 € l'anno prudente e 365 € centrale**, ma è una stima fatta con il solo tasso vero che abbiamo (1,4 %, il riquadro del libro). I numeri veri esistono già: sono nei pannelli dei programmi, attivi da 2-4 settimane.
4. **Le 3 scelte.** (1ª) Misura vera: tu leggi 6 pannelli (10 minuti), io metto il contatore dei clic su tutti i link. Parte il 28/11. Scheda scritta. (2ª) Amazon al posto della eSIM sulle pagine Starlink di Before You Fly: solo dopo il fermo, dal 10/12, e solo se la misura dice che la eSIM lì non prende clic. (3ª) WorldRemit (30 £ a cliente, il compenso più alto letto stasera) su EsameB1: **non parte**; si riapre solo se la misura mostra che Wise prende almeno 1 clic ogni 100 visite.
5. **Cose già decise e mai fatte**, trovate rileggendo i file (sez. 6): contatore dei clic (26/11), riga Wise su EsameB1 (11/11), Stay22 su Tourist Tax (13/11). La prima entra nella scheda di stasera.

---

## 1. Come ho preso i dati

- **Visite:** API pubblica di GoatCounter `stats/hits`, lette il 27/11/2026 sera. Due finestre: 28 giorni (30/10-26/11, 1.378 percorsi, 4.946 visite) e 7 giorni (20-26/11, 431 percorsi, 1.062 visite). Domini vecchi e nuovi sommati. Eventi `/clic/` tolti dalle visite.
- **Visite l'anno:** prudente = 7 giorni × 52. Centrale = 28 giorni × 13.
- **Quanti cliccano:** il solo dato nostro è il riquadro del libro su EsameB1: **6 clic su 441 visite in 7 giorni = 1,4 %**. Lo uso come base. Ogni altro tasso è scritto **ipotesi**.
- **Quanti comprano dopo il clic:** nessun dato nostro. Uso 3 % prudente e 5 % centrale (**ipotesi**).
- **Commissioni:** solo pagine ufficiali lette stasera. Dove la pagina dava 403 o 404 lo scrivo e non stimo, oppure segno **(terzi)**. Nessun blocco aggirato.
- **Volumi di ricerca:** `api.seodata.dev /v1/keyword`, 12 frasi, lette stasera.
- **Link accesi:** conteggio di `rel="sponsored"` nelle cartelle `sito/` del repository.
- Cambi usati: 1 £ = 1,15 €, 1 $ = 0,90 €.

---

## 2. Il conto che decide tutto

### 2.1 Visite vere per sito

| Sito | 28 giorni | 7 giorni | L'anno, prudente | L'anno, centrale | Sezioni che portano le visite (28 giorni) |
|---|---|---|---|---|---|
| EsameB1 | 1.921 | 441 | 22.900 | 25.000 | città 749, esempi 464, home 254, ente 133, /en/ 110, costo 50, cittadinanza 42 |
| Visa Income | 1.309 | 274 | 14.200 | 17.000 | rifiuti dei visti 454, cerimonie australiane 197, test di inglese UK 163, «moved to» 150, home 114, studiare in Italia 58 |
| Before You Fly | 1.029 | 210 | 10.900 | 13.400 | «available in» 369 (di cui Starlink 242), liquidi 136, biglietti 86, home 78, bagaglio a mano 62, e-visa India 56 |
| Paga CCNL | 163 | 33 | 1.700 | 2.100 | pulizie 55, logistica 51, home 37 |
| Cruise Scores | 128 | 28 | 1.450 | 1.650 | navi 52, compagnie 36, home 17 |
| Tourist Tax | 104 | 11 | 570 | 1.350 | Francia 28, Istanbul 12, USA 16 |
| Italy Strikes | 79 | 7 | 360 | 1.030 | pagine in italiano 28, guide 12, aeroporti 12 |
| **Totale dei 7** | **4.733** | **1.004** | **52.200** | **61.500** | |

### 2.2 Quanti acquisti può dare questo traffico

- 61.500 visite l'anno × 1,4 % di clic × 5 % di acquisti = **43 acquisti l'anno**, se ogni pagina avesse un riquadro perfetto.
- Con il conto prudente (52.200 × 0,7 % × 3 %): **11 acquisti l'anno**.
- Quindi il tetto dipende solo da **quanto paga un acquisto**:

| Compenso per acquisto | Esempio | Tetto l'anno, prudente | Tetto l'anno, centrale |
|---|---|---|---|
| 1-3 € | Amazon, eSIM, traduzioni | 11-33 € | 43-130 € |
| 10-16 € | Wise, italki | 110-175 € | 430-690 € |
| 35-50 € | WorldRemit, una crociera | 385-550 € | 1.500-2.150 € |

- Il tetto alto (35-50 €) non si raggiunge: un pagatore così c'entra solo con poche pagine. Nei conti sotto uso le visite delle sole pagine adatte.
- **Detto chiaro:** con queste visite un'affiliazione nuova non può cambiare il fatturato. Può farlo solo chi paga senza l'acquisto (pubblicità) o chi paga molto a cliente (prodotto nostro, scuole, avvocati: le 4 prove del piano).

---

## 3. I 9 pagatori controllati stasera, in ordine di € centrali

| # | Sito e pagine | Pagatore | Cosa paga (letto stasera) | Accetta un forfettario? | Visite l'anno sulle pagine adatte | € l'anno prudente / centrale | Ore | Voto |
|---|---|---|---|---|---|---|---|---|
| 1 | EsameB1: costo, cittadinanza, reddito | **WorldRemit** (rete Impact) | «Our default commission rate is £30 (min spend £50)», pagato 30 giorni dopo la fine del mese ([pagina ufficiale](https://www.worldremit.com/en-gb/partners-and-affiliates), 200) | Sì in teoria: iscrizione su Impact (account già aperto). Affiliazione **nuova** | 1.200 / 1.300 | **9 / 31** | 2 | 3,5 |
| 2 | Before You Fly: pagine Starlink | **Amazon USA e UK** (già acceso) con link di ricerca | «All Other Categories 4,00 %», computer 2,50 % ([tabella USA](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ), 200). Prezzo del kit Mini: 149-349 $ **(terzi, in conflitto)** | Sì, account già attivi | 3.100 / 3.150 | **4 / 28** | 1,5 | 3,5 |
| 3 | Cruise Scores: navi e compagnie | **CruiseDirect** (rete CJ) | 3 % della prenotazione, cookie 45 giorni, prenotazione media 1.600-2.200 $ **(terzi)**; le pagine ufficiali non scrivono la cifra | Incerto: CJ approva marchio per marchio; serve W-8BEN. Affiliazione **nuova** | 1.450 / 1.650 | **4 / 17** | 2 | 3 |
| 4 | Tourist Tax: tutte le pagine | **Stay22** (già acceso su BYF) | 30 % della commissione delle agenzie (studio del 13/11) | Sì, account attivo | 570 / 1.350 | **3 / 10** | 1,5 | 2,5 |
| 5 | EsameB1 cittadinanza + Visa studiare in Italia + Messico | **Translayte** (traduzioni giurate) | «Guadagna una commissione del 10 %», pagamento su PayPal o banca, risposta alla domanda «entro 3 giorni lavorativi» ([pagina in italiano](https://translayte.com/it/collabora-con-noi/affiliazione), 200). Soglia 100 $ **(da ricerca, non dalla pagina)** | Sì: «blogger e creatori di contenuti», nessuna soglia di traffico scritta. Affiliazione **nuova** | 1.300 / 1.450 | **2 / 8** | 2 | 2 |
| 6 | Paga CCNL: pagine livello | **Jooble** (offerte di lavoro, paga a clic) | «paid out monthly on a CPC and CPA basis», Net 45, Italia tra i 13 mercati principali; **tariffa non scritta** ([pagina ufficiale](https://jooble.org/affiliate), 200). Confronto: Indeed 0,05-0,10 $ a clic **(terzi, 2022)** | Sì: nessun minimo scritto, PayPal o Wise. Affiliazione **nuova** | 1.700 / 2.100 | **1 / 6** | 2 | 2 |
| 7 | Visa Income e BYF (traffico da USA, UK, Canada, Australia) | **Media.net** o **Microsoft pubCenter** (pubblicità, non affiliazione) | pubCenter: «no sign-up costs, revenue minimums, or volume requirements», ma **solo USA con lista d'attesa** per gli altri Paesi (articoli del 2023; pagina ufficiale 403). Media.net: requisiti ufficiali non leggibili (404); soglia di pagamento 100 $ **(terzi)** | pubCenter: **non verificabile** per l'Italia. Media.net: incerto | ~15.000 visite da quei Paesi | **0 / 30** (ipotesi 2 $ ogni 1.000 pagine) | 3 + banner dei cookie | 2,5 |
| 8 | EsameB1 | **Remitly Ambassador** | «at least 30 GBP for every transfer that qualifies», pagamento settimanale ([pagina UK](https://www.remitly.com/gb/en/partnerships/ambassador-program), 200) | Solo con un conto Remitly proprio, un corso obbligatorio e un codice personale: è per persone, non per siti (già scritto il 7/11) | – | non stimato | – | 2 |
| 9 | Italy Strikes: guida «voli durante gli scioperi» | rimborso voli (AirHelp via Travelpayouts, in pausa) | 15-16,6 % (studio del 17/10) | account in pausa per lo script | 80 | **0 / 1** | 1 | 1 |
| | **Totale** | | | | | **circa 23 / 131** | ~15 | |

### Note sui conti (un esempio per riga)

- **WorldRemit.** Pagine adatte di EsameB1: costo 50 + cittadinanza 42 + reddito 9 = 101 visite in 28 giorni, 1.300 l'anno. Centrale: 1.300 × 1,4 % × 5 % × 34,50 € = 31 €. Prudente: 1.200 × 0,7 % × 3 % × 34,50 € = 9 €. Su tutto il sito (25.000 visite, clic 0,5 % perché fuori tema): 215 € centrali, ma vuol dire un riquadro «manda soldi a casa» su ogni pagina d'esame, mentre AdSense sta valutando il sito. Non lo propongo.
- **Amazon su Starlink.** 242 visite in 28 giorni sulle pagine Starlink. «starlink mini» fa 165.000 ricerche al mese negli USA (seodata, stasera): il prodotto si vende. Centrale: 3.150 × 3 % × 6 % × 5 € = 28 €. Prudente: 3.100 × 1,4 % × 4 % × 2 € = 4 €. Vale un po' di più del numero: sono vendite che aiutano ad arrivare alle 3 vendite entro il 5/5/2027 che tengono aperti gli account Amazon UK e USA. **Contro:** l'audit AdSense del 26/11 dice che su Before You Fly i riquadri sono già troppi (643 pagine con 3 riquadri eSIM). Quindi solo **al posto** della eSIM, mai in più.
- **CruiseDirect.** È il compenso più alto per acquisto della rete (43-59 €), ma con 128 visite in 28 giorni: 1.650 × 2 % × 1 % × 50 € = 17 €. Dato utile letto stasera: «cruise insurance» negli USA ha 6.600 ricerche al mese e un costo per clic di 13,78 $. Su questo sito il valore sta nella pubblicità, quando AdSense approva.
- **Paga CCNL.** Chi legge le pagine livello (pulizie 2° livello, logistica G1) è un lavoratore che controlla la paga, non un'azienda che compra un programma paghe. «software paghe»: 210 ricerche al mese, costo per clic 11,90 €; «controllo busta paga»: 720 ricerche, 1,71 €; «offerte lavoro pulizie»: 1.000 ricerche, 0,48 €. I soldi stanno dal lato delle aziende: è la prova 3 del piano (strumento per l'annuncio), non un'affiliazione. Factorial non scrive le cifre (contratto dopo un modulo): non stimato.
- **Translayte.** «traduzione giurata»: 1.000 ricerche al mese, costo per clic 7,77 €; «documenti cittadinanza italiana»: 5.400 ricerche. La domanda c'è, ma le nostre pagine adatte fanno 111 visite in 28 giorni. Con la soglia di 100 $ servirebbero oltre 10 anni per il primo pagamento.

---

## 4. Le affiliazioni già accese: il numero che manca

### 4.1 Cosa c'è online (conteggio di stasera)

| Sito | Pagine con link di affiliazione | Link | Pagine con contatore di clic |
|---|---|---|---|
| Before You Fly | 547 | 606 | 0 |
| Visa Income | 381 | 592 | 0 |
| Cruise Scores | 257 | 257 | 0 |
| EsameB1 | 110 | 220 | 131 (solo libro, Pass e scuole: nessun link di affiliazione) |
| Italy Strikes | 61 | 62 | 0 |
| Tourist Tax | 5 | 5 | 0 |
| Paga CCNL | 0 | 0 | 2 (prova «per chi assume») |
| **Totale** | **1.361** | **1.742** | **0 sui link di affiliazione** |

### 4.2 Quanto valgono, a stima

- Visite in 28 giorni sulle pagine con un riquadro: circa 3.340 (EsameB1 ~1.630, Visa ~900, Before You Fly ~640, Cruise 128, Italy Strikes ~40). L'anno: circa 43.400.
- Centrale: 43.400 × 1,4 % = 608 clic × 5 % = 30 acquisti × 12 € = **365 € l'anno**.
- Prudente: 43.400 × 0,7 % × 3 % × 10 € = **91 € l'anno**.
- È una stima. Il tasso dell'1,4 % viene da un riquadro in alto, con la copertina, di un prodotto nostro. I riquadri di affiliazione stanno più in basso.

### 4.3 I clic che i pannelli dovrebbero mostrare oggi

Se il tasso dell'1,4 % vale anche per le affiliazioni, nei pannelli ci sono questi clic. Se ce ne sono molti meno, i riquadri non lavorano e si tolgono (meno promozione sulle pagine = aiuto alla domanda AdSense).

| Programma | Acceso dal | Dove | Nostre visite su quelle pagine, dal giorno di accensione al 26/11 | Clic attesi all'1,4 % |
|---|---|---|---|---|
| italki | 30/10 | EsameB1 (110 pagine) | fino a 1.921 | fino a 27 |
| italki | 30/10 | Visa Income, test di inglese UK | 163 | 2 |
| Amazon.it (`guideesami-21`) | 30/10 | EsameB1 | fino a 1.921 | fino a 27 |
| SafetyWing | 30/10 | Visa rifiuti 454 + Cruise 128 + Italy Strikes 79 + BYF India 56 | 717 | 10 |
| Wise | 14/11 | Visa (home, «moved to», calcolatori) + BYF «available in Wise» | circa 190 | 3 |
| eSIM su Awin (Roamable, Vodafone, Pocket) | 6-10/11 | BYF, soprattutto Starlink | circa 250 | 3-4 |
| Amazon UK e USA | 6/11 | BYF bagaglio 61 + liquidi 99 | 160 | 2 |
| Viator e Stay22 | novembre | BYF biglietti | 82 | 1 |
| **Totale** | | | | **circa 50-75 clic** |

Regola di lettura: **60 clic o più** in tutto = l'ipotesi dell'1,4 % regge. **Meno di 15** = i riquadri di affiliazione sono quasi fermi.

---

## 5. Le 3 scelte, con prova, soglia, stop e data

### 1ª — Misura vera delle affiliazioni già accese (parte il 28/11) — scheda scritta

- **Cosa.** (a) Massimiliano legge 6 pannelli, 10 minuti: clic e vendite dal giorno di accensione. (b) Contatore dei clic (evento GoatCounter, come quello del libro) su ogni link di affiliazione. Subito sui siti non fermi: EsameB1, Cruise, Italy Strikes, Tourist Tax (544 link su 433 pagine). Su Visa e Before You Fly (1.198 link su 928 pagine) alla prima pubblicazione dopo il fermo, dal 10/12.
- **Vale.** 0 € da sola. Ma decide tre cose: se i 90-365 € delle affiliazioni accese sono veri; quali riquadri togliere prima della prossima domanda AdSense; se la decisione del 19/11 va riaperta (la regola chiede «numeri veri»: questi lo sono).
- **Soglia (per programma e sezione).** Almeno 5 clic in 14 giorni: resta e sale più in alto.
- **Stop.** 0 clic in 28 giorni con almeno 200 visite sulle sue pagine: il riquadro si toglie da quella sezione.
- **Soglia di rete.** Se il 26/12 i clic contati sono almeno 1 ogni 100 visite sulle pagine con riquadro e i pannelli mostrano almeno 1 vendita: scrivo il conto vero per la decisione sulle affiliazioni. Sotto 0,3 clic ogni 100 visite: le affiliazioni non sono un canale a questo traffico e non si ripropongono fino a 50.000 visite al mese.
- **Date.** Partenza 28/11. Prima lettura 12/12. Verdetto 26/12.
- **Da Massimiliano.** 10 minuti, i 6 pannelli (lista in sez. 7). Nient'altro.
- **Scheda.** `studio-business/schede/2026-11-28-clic-affiliazioni.md`.

### 2ª — Before You Fly, pagine Starlink: Amazon al posto della eSIM (dal 10/12, condizionata) — nessuna scheda oggi

- **Cosa.** Sulle pagine Starlink un solo riquadro: link di ricerca Amazon (account già accesi) per antenna e accessori, al posto dei riquadri eSIM. Mai in più.
- **Perché non parte entro 48 ore.** Before You Fly è fermo fino al 9/12 e l'audit AdSense chiede meno riquadri. Costruire adesso sarebbe contro due regole.
- **Condizione.** Si fa solo se la misura della 1ª scelta mostra meno di 5 clic in 14 giorni sulla eSIM nelle pagine Starlink.
- **Vale.** 4 € prudente, 28 € centrale. In più: vendite verso le 3 che servono entro il 5/5/2027 per tenere aperti Amazon UK e USA.
- **Soglia.** Almeno 8 clic in 28 giorni e 1 vendita nel pannello Amazon entro il 31/1/2027. **Stop:** meno di 3 clic.
- **Date.** Decisione il 24/12 (dopo 14 giorni di contatore su Before You Fly). La scheda si scrive quel giorno.
- **Da Massimiliano.** Niente.

### 3ª — WorldRemit su EsameB1: non parte — nessuna scheda

- **Perché è la terza.** È il compenso più alto e più chiaro letto stasera: 30 £ per ogni nuovo cliente che invia almeno 50 £. Tre volte Wise.
- **Perché non parte.** Affiliazione nuova (regola del 19/11) per 9-31 € l'anno sulle pagine adatte. Per valere di più dovrebbe stare su tutte le pagine d'esame, fuori tema, con AdSense in valutazione.
- **Quando si riapre.** Solo se la misura mostra che Wise (già acceso, stesso tipo di offerta) prende almeno 1 clic ogni 100 visite su Visa Income «moved to» entro il 7/1/2027. Allora il conto diventa: 25.000 × 0,5 % × 5 % × 34,50 € = 215 € centrali, e si porta a Massimiliano con il numero vero.
- **Da Massimiliano.** Niente adesso.

---

## 6. Già deciso e non ancora fatto (trovato rileggendo i file)

| Cosa | Deciso il | Stato stasera | Cosa propongo |
|---|---|---|---|
| Contatore dei clic su tutte le affiliazioni («mossa 0») | 26/11 sera, da fare entro 48 ore | nessuna scheda, 0 eventi sui link | È la scheda di stasera |
| Riga Wise su EsameB1 («si mette il link Wise quando arriva») | 11/11; Wise approvato il 13/11 | `esameb1/dati/affiliati.json` ha solo italki e Amazon | Non farla: 101 visite in 28 giorni sulle pagine adatte non danno un numero leggibile (1-2 clic) |
| Stay22 su Tourist Tax | 13/11 («subito»); il 27/11 il piano dei siti minori lo dà per fermo | campo vuoto | Resta fermo: 3-10 € l'anno |
| Link Kindle nel riquadro del libro | piano, tappa del 4/12 | non ancora online | Nessun cambio: è già in calendario |

---

## 7. Cosa deve fare Massimiliano

Una cosa sola, 10 minuti, quando vuole entro il 5/12. Aprire i 6 pannelli e scrivermi **clic e vendite** dal giorno indicato:

1. **italki** (pannello affiliati): dal 30/10.
2. **Amazon.it Associates**, ID `guideesami-21`: clic e articoli ordinati dal 30/10.
3. **Amazon UK e USA Associates**: clic e articoli ordinati dal 6/11.
4. **SafetyWing Ambassador**: clic per campagna (`visa-refusal-rates`, `cruise-health-scores`, `italy-strikes-today`) dal 30/10.
5. **Wise su Partnerize**: clic e conversioni dal 14/11.
6. **Awin**: clic per inserzionista (Roamable, Vodafone, Pocket, Italo) dal 6/11.

Nessuna iscrizione nuova. Nessuna spesa.

---

## 8. Controllati stasera e scartati, in una riga

- **Preply:** pagina 403, non letta. Niente stima.
- **Remitly per siti (Impact):** nessuna cifra sulla pagina ufficiale; 1,60 $ a primo invio **(terzi)**. Scartato.
- **AXA Schengen:** le pagine provate danno 404; dalla ricerca: commissione «negotiable», iscrizione su Tradedoubler (domanda già fatta, senza risposta). Niente di nuovo.
- **Careerjet, Talent.com, Adzuna (offerte di lavoro):** nessuna tariffa scritta (Careerjet), solo accesso con account (Talent.com), 403 (Adzuna).
- **Factorial (programma paghe):** cifre solo dopo un contratto. Non stimabile.
- **Avvocati per la cittadinanza su EsameB1:** non proposto. **Da verificare prima del 10/12 per la prova 4 del piano:** il codice deontologico degli avvocati italiani vieta di pagare chi presenta un cliente (art. 37, non riletto stasera sulla fonte ufficiale). Se vale, un avvocato italiano può pagare una scheda o uno spazio, non un compenso a cliente firmato.
- **Donazioni:** già scartate da Massimiliano il 13/11. Non riproposte.

---

## 9. Cosa resta incerto

- I tassi dopo il clic (3-5 %) sono ipotesi. La 1ª scelta serve a sostituirli con numeri veri.
- La quota di visite sulle pagine con riquadro (circa 3.340 su 4.733 in 28 giorni) è una stima per sezione, non un conteggio pagina per pagina.
- CruiseDirect, soglia di Translayte, prezzo del kit Starlink, tariffe di Jooble e Media.net: non letti su pagina ufficiale.
- pubCenter in Italia: non verificabile da qui (403). Costa 5 minuti provarlo, ma chiede comunque un banner dei cookie: non lo metto tra le cose da fare.
- I pannelli possono contare i clic in modo diverso da GoatCounter (robot, clic doppi): il confronto vale per ordine di grandezza.

---

## Fonti lette il 27/11/2026

- GoatCounter `rete-siti.goatcounter.com/api/v0/stats/hits` (30/10-26/11, 20-26/11, 14-26/11, 6-26/11).
- `api.seodata.dev/v1/keyword`: traduzione giurata 1.000 (IT), documenti cittadinanza italiana 5.400, offerte lavoro pulizie 1.000, controllo busta paga 720, software paghe 210, lezioni di italiano online 170, inviare soldi all'estero 90, starlink mini 165.000 (USA), cruise insurance 6.600 (USA); a volume 0: traduzione giurata certificato di nascita, stipendio addetto pulizie, corso italiano b1 online.
- Lette (200): worldremit.com/en-gb/partners-and-affiliates · remitly.com/gb/en/partnerships/ambassador-program · translayte.com/it/collabora-con-noi/affiliazione · jooble.org/affiliate · careerjet.com/partners e /partners/publishers · affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ.
- Non leggibili, non aggirate: preply.com/en/affiliates (403) · pubcenter.microsoft.com (403) · adzuna.co.uk/publishers.html (403) · translayte.com/affiliate, remitly.com/us/en/affiliates, axa-schengen.com/en/affiliate-program, media.net/program-guidelines, about.ads.microsoft.com/…/pubcenter (404) · talent.com/publishers (solo accesso).
- Da ricerca web (terzi): searchengineland.com (pubCenter solo USA, 2023) · fmtc.co, affpaying.com, flexoffers.com (CruiseDirect 3 %, 45 giorni) · flexoffers.com e uppromote.com (Remitly 1,60 $) · translayte.com/refer-us (10 % e soglia 100 $) · notebookcheck.net, slickdeals.net (prezzo Starlink Mini).
- File del repository: `studio-business/strumenti/monetizzazione.json`, `*/dati/affiliati.json`, cartelle `*/sito/`, `ADSENSE-AUDIT-2026-11-26.md`, `STRATEGIA-RECUPERO.md`.
