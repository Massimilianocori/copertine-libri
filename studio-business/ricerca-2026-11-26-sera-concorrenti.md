# Ricerca del 26/11/2026, sera: come guadagnano i siti che vincono nelle nostre nicchie

Approccio di stasera: non cerco idee nuove. Guardo chi vince già nelle nostre 3 nicchie e leggo da dove prende i soldi. Poi faccio il conto con le nostre visite vere.

Solo ricerca. Nessuna modifica ai siti. Nessun commit.

---

## 0. In breve

- **I vincitori guadagnano in 3 modi.** (1) Tanta pubblicità su tanto traffico. (2) Un servizio con una persona dentro, a prezzo alto: corso, lezione, consulenza. (3) La vendita nel momento in cui l'acquisto è obbligatorio: l'assicurazione per il visto Schengen.
- **Le mosse piccole le abbiamo già copiate.** Abbiamo 7 affiliazioni accese (Amazon, italki, Genki, Wise, Viator, Stay22, SafetyWing) più HelloSafe e le eSIM. Incasso scritto nel repo: 0 €.
- **Scoperta n. 1: non contiamo i clic sulle affiliazioni.** Il piano lo dice: «nessun clic o vendita scritti nel repo». I vincitori fanno passare ogni link da un indirizzo `/out/nome-partner` e contano tutto. Senza questo numero non possiamo decidere nulla sulle affiliazioni.
- **Scoperta n. 2: un conto del pomeriggio è sbagliato di 10 volte.** Il file `grandi-pubblico` scrive italki = 16 $ l'anno. Il conto giusto è 161 $ a 10 $ a studente, e 290 $ ai 18 $ veri del nostro contratto.
- **Scoperta n. 3: nel B1 nessun vincitore vende solo un prodotto automatico.** Tutti vendono una persona: corso a 400-500 €, lezione a 29-80 $ l'ora, consulenza a 89 €. Un gradino «con insegnante» sopra il Pass vale più di tutte le affiliazioni insieme. E aiuta anche il nodo fiscale (servizio di formazione, non commercio).
- **Detto chiaro: il pacchetto di stasera vale circa 260 € l'anno prudente e circa 1.760 € centrale.** Non cambia il quadro da solo. Rende di più il Pass, che è già in prova.

---

## 1. Come ho preso i dati

- **Le nostre visite.** API GoatCounter `rete-siti`, `stats/hits`, `stats/locations`, `stats/toprefs`, lette oggi. Periodi: 29/10-25/11 (28 giorni), 12-25/11 (14 giorni), 19-25/11 (7 giorni). Host vecchi e nuovi sommati.
- **Chi vince.** Google non si legge in automatico da qui (pagina vuota, errore 429 o 403 anche su Bing, Brave, DuckDuckGo). Ho usato la ricerca web dello strumento, che lavora dagli Stati Uniti. Quindi la lista dei siti è una buona approssimazione, non la classifica esatta di Google Italia.
- **Come guadagnano.** Ho scaricato 40 pagine dei concorrenti e ho cercato nel codice: reti pubblicitarie, link di affiliazione, carrello, moduli. Poi ho letto prezzi e offerte sulle pagine.
- **Quanto sono grandi.** Similarweb non si legge (403). Uso la classifica pubblica Tranco (posto fra i siti del mondo: numero più basso = sito più grande) e i numeri che i siti dichiarano.
- Cambio BCE: 1 € = 1,0935 $.

### Le nostre visite, base di tutti i conti

| Sito | 28 giorni | 14 giorni | 7 giorni | L'anno, prudente (7 g × 52) | L'anno, centrale (28 g × 13) |
|---|---|---|---|---|---|
| EsameB1 | 1.826 | 802 | 347 | 18.000 | 23.700 |
| Visa Income | 1.240 | 701 | 234 | 12.200 | 16.100 |
| Before You Fly | 979 | 524 | 184 | 9.600 | 12.700 |

Nota: i miei totali sono un po' più bassi di quelli del piano (4.692 contro 4.860 per la rete). Uso i miei, che sono più prudenti.

Le sezioni che contano:

| Sezione | 28 giorni | 7 giorni | Da dove arrivano |
|---|---|---|---|
| EsameB1 `/citta/` | 760 | 108 | Google |
| EsameB1 `/esempi/` | 390 | 131 | ChatGPT soprattutto |
| Visa `/visa-refusal-rates/` | 432 (356 su Paesi Schengen) | 100 (85) | ChatGPT 285, Google 33 |
| Visa cerimonie australiane | 190 | 23 | Google |
| Visa `/moved-to/` | 147 | 78 (cresce) | Google |
| Visa test d'inglese UK | 147 | 10 | Google |
| BYF `/available-in/` | 334 (Starlink 218, streaming 40) | 85 | Google e ChatGPT |
| BYF `/liquids/` | 143 | 15 | – |
| BYF `/ticket-release-dates/` | 79 | 21 | – |
| BYF `/cabin-bags/` | 55 | 30 | – |

Paesi dei lettori (28 giorni):
- EsameB1: Italia 1.563. Tutto il resto è poco.
- Visa: Australia 216, USA 162, Regno Unito 139, Italia 83, India 40. Sulle pagine dei rifiuti: USA 35, Turchia 25, Bangladesh 23, Regno Unito 23, Pakistan 21.
- BYF: USA 299, Regno Unito 95, Germania 52, Canada 48, Spagna 44.

---

## 2. Nicchia 1: esame B1 di italiano per la cittadinanza

| Sito | Come guadagna | Prezzi | Segnali di grandezza | Cosa ha che noi non abbiamo |
|---|---|---|---|---|
| **Europass Italian** (europassitalian.com) | Corso online di gruppo con insegnante. Carrello sul sito. Newsletter Mailchimp | 400 € (listino 500 €): 24 lezioni da 100 minuti, massimo 10 studenti. Tassa d'esame 100 € a parte | «4,8/5 su oltre 1.200 recensioni» (tutta la scuola). Tranco 1.048.470 | Un insegnante. Un prezzo 20 volte il nostro libro. Date di inizio fisse |
| **Happy Languages** (Londra) | Corso online su Zoom | 289 £ per 15 settimane, 1 ora a settimana, 15 studenti | Fuori dal milione Tranco. Alcuni corsi «esauriti» | Come sopra |
| **AIS Philadelphia** / **Italian Foundation** | Corso breve online prima dell'esame. Carrello, newsletter | 220 $ per 5 settimane | Fuori dal milione | Corso corto legato alla data d'esame |
| **Strommen** (strommeninc.com) | Mercato di insegnanti privati. Pagina fatta apposta: «CILS B1 Cittadinanza tutors» | da 29, 30 e 80 $ l'ora. Prova gratis di 30 minuti | «250+ insegnanti», «400+ recensioni». Tranco 1.178.547 | Una pagina che porta dritto a 3 insegnanti con nome, prezzo e prova gratis |
| **Italiano Bello / Ornimi** (italiano-bello.com) | Negozio proprio di libri di carta (WooCommerce, PayPal). Sconti per scuole e librerie | «Percorso CILS Cittadinanza B1» 16,90 €. Altri titoli 18,60-26,80 € | Tranco 569.372. Sul titolo B1: 0 recensioni | Vende dal suo carrello e tiene tutto il margine. Ha un catalogo intero, non un libro |
| **infoimmigrazione.com** | È il sito di uno studio legale. Vende la consulenza. Ha anche AdSense | **89 € IVA inclusa per 40 minuti**, pagamento online | 105 recensioni Google. Fuori dal milione | Il passo dopo l'esame: la domanda di cittadinanza, a pagamento |
| **Stranieri in Italia** (stranieriinitalia.it) | Solo pubblicità: AdSense, Ezoic, Google Ad Manager | – | Tranco 561.215 | Traffico grande e anni di storia |
| **OpenExamPrep** (open-exam-prep.com) | Quiz gratis per decine di esami. Pubblicità (Ezoic, AdSense). Link Amazon a un libro da 28,99 $. Crediti per un tutor AI | 100 $ per 100 crediti. 10 domande AI gratis al giorno | Tranco 198.731. «125+ domande» per il B1 | Un motore solo per tanti esami |
| Ready Set Italia | Corso in inglese | 575 € | 3 recensioni | Già visto oggi pomeriggio |

**Lettura.**
- Chi incassa di più vende **una persona**: 220-500 € a corso, 29-80 $ l'ora, 89 € a consulenza.
- Chi vende un libro lo vende **dal proprio carrello** e ha un catalogo.
- Chi vive di pubblicità ha traffico 50-100 volte il nostro.
- Tutti quelli con un carrello hanno **una lista email**.
- Nessuno ha quello che abbiamo noi: date, sedi e costi per città, aggiornati.

---

## 3. Nicchia 2: visti e requisiti di reddito

| Sito | Come guadagna | Prezzi | Segnali di grandezza | Cosa ha che noi non abbiamo |
|---|---|---|---|---|
| **SchengenVisaInfo** (+ visaguide.world, stessa rete di link) | AdSense. Soprattutto: pagina assicurazioni con link contati `/out/axa`, `/out/mutuaide`, `/out/mondialcare`, `/out/coverwise`, `/out/insubuy` | Polizze mostrate: AXA da 20 € per 7 giorni, Mutuaide da 10,50 €, Europ Assistance 21 €, MondialCare da 17 € | «250 milioni di utenti dal 2013» (dichiarato). Tranco **33.864**. ZoomInfo: sotto 5 milioni di $ di ricavi, 11-50 persone (stima di terzi) | Traffico enorme. Ogni clic verso un partner è contato. 6 assicuratori a confronto |
| **HelloSafe** (hellosafe.com) | Confronto di assicurazioni. La pagina «tassi di rifiuto Schengen per nazionalità» è un imbuto: 5 inviti al preventivo. Ha un programma per i siti: **Atlas** | Polizza Schengen media 45 € (loro conto). Ai partner «fino al 50 %», cookie 90 giorni | «+2 milioni di viaggiatori», «40+ assicuratori», «oltre 1.000 partner», Trustpilot 4,6 | Lo stesso tema nostro (rifiuti per nazionalità), ma con la polizza «rimborsata se il visto è rifiutato» dentro la pagina |
| **AXA Schengen**, **Insurte** | Sono assicuratori. Scrivono loro le guide «Paese più facile per il visto Schengen» | AXA «da 4,90 €» | Tranco 304.241 e 1.075.847 | Vendono il prodotto, non il link |
| **Mappr** (mappr.co) | Pubblicità **Mediavine**. Amazon. Newsletter | – | Tranco 252.655 | Traffico da Paesi ricchi sopra la soglia Mediavine |
| **Global Citizen Solutions**, **Immigrant Invest** | Contatti per consulenze su visti d'oro e residenze | preventivo | Tranco 158.722 e 126.537 | Un servizio da migliaia di euro a cliente |
| **Europe Visa Check** (sito piccolo, simile a noi) | Solo affiliazioni: SafetyWing, NordVPN, Saily. Niente pubblicità | – | Fuori dal milione | Niente. È al nostro livello |
| Nomads.com | Abbonamento | – | Tranco 74.001 | Una comunità |

**Lettura.**
- In questa nicchia i soldi veri sono **l'assicurazione Schengen**. È obbligatoria (30.000 € di copertura). Gli assicuratori scrivono loro stessi le pagine sui rifiuti.
- Le nostre pagine dei rifiuti sono la sezione più letta di Visa Income: 432 visite in 28 giorni, 356 su Paesi che chiedono il visto Schengen (Turchia, Bangladesh, Algeria, India, Pakistan, Nigeria).
- Oggi su quelle pagine c'è un riquadro SafetyWing. SafetyWing non dà il certificato Schengen come prodotto dedicato e il nostro stesso testo dice «nessuna garanzia».
- **HelloSafe Atlas è già approvato dal 7/11** (codice partner nel repo). È acceso solo su 3 pagine («Health insurance for visas»), che in 28 giorni hanno fatto **1 visita**. Il partner giusto è sulla pagina sbagliata.
- Motivo noto: le pagine dei rifiuti sono bloccate dall'esperimento sulle citazioni fino al 28/12, e Visa è fermo fino al 9/12.

---

## 4. Nicchia 3: regole di viaggio (liquidi, bagaglio a mano, passaporto)

| Sito | Come guadagna | Prezzi | Segnali di grandezza | Cosa ha che noi non abbiamo |
|---|---|---|---|---|
| **Which?**, **Time Out**, **Euronews**, **The Points Guy** | Giornali. Pubblicità programmatica, abbonamenti (Which?), carte di credito (TPG) | – | Tranco 10.662 (Which?), 17.450 (TPG) | Marchio e redazione. Non si copia |
| **Kayak**, **Skyscanner**, **Trip.com**, **Expedia** | Vendono voli. Le guide sul bagaglio portano alla ricerca voli | – | giganti | Il prodotto |
| **Monos**, **Travelpro**, **Rimowa**, **Horizn** | Vendono valigie. La guida «misure per compagnia» è la loro vetrina | valigie 150-400 € | Tranco 153.926 (Monos) | Il prodotto |
| **Deep Arrival** (deeparrival.com), sito indipendente | **Mediavine** + Amazon + 2 newsletter (beehiiv) | – | Tranco 369.818 | Traffico USA sopra la soglia Mediavine. Lista email |
| **Flight-Delayed** | Pratiche di rimborso voli. Trattiene una quota. Il blog sul bagaglio porta clienti | 25-35 % del rimborso (uso comune del settore: **da verificare**) | Tranco 2.515.739 | Un servizio proprio |
| **Earth SIMs** (pagine Starlink per Paese) | Affiliazioni: NordVPN in cima («Our Top Pick»), Airalo, Saily, SafetyWing | – | Tranco 3.811.315: piccolo | Niente. Noi abbiamo già le eSIM |
| **vaticanmuseum.co** | Affiliazioni GetYourGuide e Viator sulla pagina «biglietti esauriti» | 8 % circa della prenotazione | Fuori dal milione | Un riquadro preciso: «esaurito? entra con una visita guidata» |
| **Rustic Pathways** (controllo passaporto) | Vende viaggi per studenti. Lo strumento porta clienti | – | Tranco 477.948 | Il prodotto |

**Lettura.**
- Qui vincono i giganti e i negozi. Le guide sono la loro vetrina.
- Gli indipendenti (Deep Arrival, Mappr) vivono di **Mediavine**. Serve traffico da USA, Regno Unito, Canada e Australia.
- Gli indipendenti piccoli (Earth SIMs, vaticanmuseum.co) hanno le stesse affiliazioni che abbiamo noi, o simili.
- **Su Before You Fly non c'è una mossa nuova che renda.** Abbiamo già Amazon sulle pagine bagaglio, Viator e Stay22 sui biglietti, le eSIM. E l'audit AdSense di stamattina dice che i riquadri eSIM sono già troppi.

---

## 5. Cosa hanno i vincitori che noi non abbiamo, in una tabella

| Cosa | Chi | Noi oggi |
|---|---|---|
| Traffico 50-1.000 volte il nostro | SchengenVisaInfo, Which?, Stranieri in Italia | 4.700 visite in 28 giorni |
| Una persona nel prodotto (corso, lezione, consulenza) | Europass, Happy Languages, Strommen, infoimmigrazione | No. Libro a 5,64 € di diritti a copia; Pass automatico in prova |
| Conteggio di ogni clic verso i partner (`/out/…`) | SchengenVisaInfo, visaguide.world | **No.** Contiamo solo il libro e il prezzo del Pass |
| Il partner giusto sulla pagina più letta | HelloSafe, SchengenVisaInfo | HelloSafe su 3 pagine senza visite; SafetyWing sui rifiuti |
| Link che porta al prodotto preciso | Strommen (3 insegnanti con prezzo) | italki porta alla home di italki |
| Lista email usata per vendere | Europass, Italian Foundation, Deep Arrival, Mappr | 62 iscritti «avvisami». Nessuna email parte |
| Pubblicità Mediavine | Mappr, Deep Arrival | AdSense non ancora approvato |
| Carrello proprio | Italiano Bello, Europass | Regola «niente vendita diretta» + nodo fiscale |

---

## 6. Le mosse provate, con i nostri numeri

Regole dei conti:
- Visite l'anno: prudente = ultimi 7 giorni × 52. Centrale = 28 giorni × 13.
- Quanti cliccano: il nostro solo dato vero è il riquadro del libro, **1,4 %** (6 clic su 430 visite). Lo uso come base prudente.
- Ogni tasso senza un dato nostro è scritto **ipotesi**.

### Mossa 0 — Contare i clic su tutte le affiliazioni accese (non rende da sola, ma apre tutte le altre)

- **Chi lo fa.** SchengenVisaInfo e visaguide.world: ogni partner ha il suo indirizzo `/out/…`.
- **Da noi.** 7 programmi accesi, 0 clic contati. Il piano scrive «manca» in ogni casella.
- **€ l'anno.** 0 / 0. Ma la regola del 19/11 dice che le affiliazioni si riaprono solo con «numeri veri». Questi sono i numeri veri.
- **Cosa richiede.** Un evento GoatCounter su ogni link di affiliazione, come quello che c'è già sul libro. Nessuna affiliazione nuova. Nessuna spesa. Circa 2 ore. Su Visa dopo il 9/12; su EsameB1 e BYF subito.
- **Prova di 2 settimane.** Si contano i clic per programma e per pagina. **Soglia:** un programma con almeno 5 clic in 14 giorni resta e si sposta più in alto. **Stop:** un programma con 0 clic in 28 giorni si toglie dalle pagine (aiuta anche AdSense: meno riquadri).

### Mossa 1 — Un gradino «con insegnante» sopra il Pass EsameB1

- **Chi lo fa.** Tutti i vincitori del B1: Europass 400 €, Happy Languages 289 £, AIS 220 $, Strommen 29-80 $ l'ora, infoimmigrazione 89 € per 40 minuti.
- **L'idea, concreta.** Accanto al Pass a 19 € si mette un secondo prezzo: **«Pass + la tua prova scritta corretta da un insegnante: 49 €»**. La correzione la fa un insegnante pagato a pezzo.
- **Perché conta due volte.** Il piano (sez. 9) dice che la formazione con intervento umano è attività professionale: niente Camera di Commercio, INPS in percentuale. Il gradino con insegnante è la «strada 1» di quella nota. Va confermato dal CAF.
- **Conto.** Parto dai compratori del Pass già stimati oggi pomeriggio: 75 prudente, 224 centrale. Quota che sceglie il gradino da 49 €: 10 % / 20 % (**ipotesi**). Guadagno in più a vendita: 49 − 22 = 27 €. Costo dell'insegnante: 10 € a correzione (**ipotesi**: 10 minuti di lavoro).
  - Prudente: 75 × 10 % = 7,5 vendite × (27 − 10) = **circa 125 €**.
  - Centrale: 224 × 20 % = 45 vendite × (27 − 10) = **circa 765 €**.
- **Cosa richiede.** Il Pass costruito. Un insegnante a pezzo (lo trova Massimiliano o lo si cerca su italki). La risposta del CAF. Il sì di Massimiliano: tocca soldi e fisco.
- **Prova di 2 settimane, a costo zero.** Dentro la prova del Pass (11-31/12): due pulsanti con il prezzo, 19 € e 49 €. Nessuno dei due vende: aprono la lista d'attesa. Evento separato per ognuno. Visite attese in 14 giorni: circa 800. **Soglia:** almeno 3 clic sul 49 € e almeno il 30 % dei clic sul prezzo. **Stop:** 0 o 1 clic sul 49 € → resta solo il Pass automatico.

### Mossa 2 — HelloSafe (già approvato) sulle pagine dei rifiuti Schengen, al posto di SafetyWing

- **Chi lo fa.** HelloSafe sulla sua pagina dei rifiuti. SchengenVisaInfo con 6 assicuratori. AXA e Insurte con le loro guide.
- **Da noi.** 356 visite in 28 giorni sulle pagine dei Paesi Schengen. Partner approvato dal 7/11. Oggi lì c'è SafetyWing.
- **Conto.** Visite l'anno: 4.420 prudente (85 × 52), 4.628 centrale (356 × 13). Polizza media 45 € (dato HelloSafe).
  - HelloSafe, nel suo esempio per i partner, usa: 6 % inizia il preventivo, 15 % compra. Sono lo 0,9 % delle visite. I nostri lettori arrivano da ChatGPT per un numero: sono più freddi.
  - Prudente: 1,4 % clicca (dato nostro) × 10 % compra (**ipotesi**) = 0,14 %. 4.420 × 0,14 % = 6 polizze × 45 € × 15 % di commissione = **circa 42 €**.
  - Centrale: 3 % clicca × 15 % compra (metà dell'esempio HelloSafe, **ipotesi**) = 0,45 %. 4.628 × 0,45 % = 21 polizze × 45 € × 30 % = **circa 281 €**.
  - Il tasso vero di commissione si legge nel pannello HelloSafe dopo la prima vendita.
- **Cosa richiede.** Nessuna iscrizione nuova. Aspettare il verdetto dell'esperimento del 28/12 (già scritto in `visaincome/NOTE.md`). È un riquadro nuovo su pagine nuove: per la regola del 19/11 serve il sì di Massimiliano, con questi numeri davanti. Un solo riquadro assicurativo per pagina. Testo senza promesse sul visto.
- **Prova di 2 settimane.** 29/12-11/1. Riquadro HelloSafe con il Paese di residenza già impostato, su 20 pagine Paese; le altre restano con SafetyWing come confronto. Visite attese sulle 20 pagine: circa 150. **Soglia:** almeno 5 clic (3 %) in 14 giorni e almeno 1 polizza nel pannello entro 28 giorni → si estende a tutte. **Stop:** meno di 2 clic → tutto torna com'era.

### Mossa 3 — italki: link agli insegnanti dell'orale B1, non alla home (e conto corretto)

- **Chi lo fa.** Strommen: pagina «CILS B1 Cittadinanza tutors» con 3 insegnanti, prezzo e prova gratis.
- **Da noi.** italki è acceso su 93 pagine dal 30/10. Paga 18 $ a nuovo studente (nostro contratto). Il link porta alla home di italki. Clic contati: nessuno.
- **Correzione.** Il file `ricerca-2026-11-26-grandi-pubblico.md` scrive: «23.000 × 1,4 % × 5 % × 10 $ = 16 $». Il risultato giusto è **161 $**. Con 18 $ a studente è **290 $**.
- **Conto.**
  - Prudente: 18.000 visite × 0,7 % clicca × 3 % compra (**ipotesi**) = 3,8 studenti × 18 $ = 68 $ = **circa 62 €**.
  - Centrale: 23.700 × 1,4 % × 5 % (**ipotesi**) = 16,6 studenti × 18 $ = 299 $ = **circa 273 €**.
- **Cosa richiede.** Nessuna affiliazione nuova. Un riquadro «Prova l'orale con un insegnante» sulle pagine `/esempi/` (390 visite in 28 giorni), con il link di affiliazione che porta alla ricerca di insegnanti di italiano per esami. Va verificato nel pannello italki che il link profondo sia ammesso. Più l'evento di clic della mossa 0.
- **Prova di 2 settimane.** Subito (EsameB1 non è fermo). Visite attese: circa 800. **Soglia:** almeno 12 clic su italki (1,5 %) in 14 giorni → resta; poi almeno 1 studente nel pannello entro 28 giorni. **Stop:** meno di 4 clic → il riquadro italki esce dalle pagine e lascia il posto al Pass.

### Mossa 4 — Mediavine Journey al posto di AdSense (già nel file `grandi-pubblico`, qui solo la distanza)

- **Chi lo fa.** Mappr e Deep Arrival.
- **Da noi.** Journey chiede 1.000 sessioni in 30 giorni da USA, Regno Unito, Canada, Australia. In 28 giorni: BYF circa 471, Visa circa 546. Siamo a metà.
- **Conto.** Prudente **0 €** (non ammessi). Centrale, quando ammessi: 28.800 visite l'anno (Visa + BYF) × (12,69 $ − 3 $) ogni 1.000 = 279 $ = **circa 255 €** in più di AdSense. Il 12,69 $ è il dato di un solo blogger: **ipotesi**.
- **Cosa richiede.** AdSense approvato prima. Traffico doppio dai 4 Paesi.
- **Prova.** Nessuna adesso. **Soglia:** domanda a Journey il primo mese in cui un sito passa 1.000 sessioni dai 4 Paesi. **Stop:** nessuno, non costa niente.

### Mossa 5 — Una email automatica agli iscritti «avvisami» prima dell'esame

- **Chi lo fa.** Europass e Italian Foundation (Mailchimp), Deep Arrival (2 newsletter), Mappr.
- **Da noi.** 62 iscritti in circa 45 giorni. Nessuna email parte. Il piano conta 17 € per un solo invio.
- **Conto su un anno.** 62 in 45 giorni fanno circa 500 iscritti l'anno.
  - Prudente: 250 × 2 % compra il libro × 5,64 € = **circa 28 €**.
  - Centrale: 500 × 5 % × 5,64 € = **circa 142 €**. Con il Pass a 22 € al posto del libro diventerebbero circa 550 €, ma il Pass non c'è ancora.
- **Cosa richiede.** Che qualcuno mandi le email: Massimiliano, oppure uno strumento gratuito con il consenso già scritto nel modulo. Va controllato il testo del consenso. Decide Massimiliano.
- **Prova di 2 settimane.** Una sola email ai 62 iscritti con le date di febbraio e il libro. **Soglia:** almeno 6 clic sul libro (10 %) e almeno 1 copia → si rende automatica. **Stop:** meno di 2 clic o una protesta → non si ripete.

### Mosse 6, 7, 8 — Before You Fly: piccole, scritte solo per chiuderle

| Mossa | Chi lo fa | Conto centrale | Conto prudente | Giudizio |
|---|---|---|---|---|
| 6. VPN sulle pagine «streaming disponibile in…» | Earth SIMs, Europe Visa Check | 520 visite l'anno × 3 % × 4 % × 30 € = **19 €** | **0 €** | No. Affiliazione nuova, e più riquadri pesano sulla domanda AdSense |
| 7. «Esaurito? Entra con una visita guidata» sulle pagine dei biglietti (Viator è già acceso) | vaticanmuseum.co | 1.030 × 4 % × 5 % × 70 € × 8 % = **12 €** | 1.090 × 1,4 % × 3 % × 70 € × 8 % = **3 €** | Solo se costa 10 minuti |
| 8. Tre valigie precise al posto del link di ricerca Amazon | Deep Arrival, Monos | 1.560 × 5 % × 6 % × 70 $ × 4 % = **12 €** | **1 €** | No |

Le commissioni di NordVPN non le ho potute leggere oggi (pagina 403): i 30 € a vendita sono **da verificare**.

---

## 7. Classifica per € l'anno

| # | Mossa | Prudente | Centrale | Richiede | Affiliazione nuova? |
|---|---|---|---|---|---|
| 1 | Gradino «con insegnante» sopra il Pass (49 €) | 125 € | **765 €** | Pass costruito, insegnante a pezzo, CAF, sì di Massimiliano | no |
| 2 | HelloSafe sulle pagine dei rifiuti Schengen | 42 € | **281 €** | verdetto del 28/12, sì di Massimiliano | no (già approvato) |
| 3 | italki con link agli insegnanti dell'orale | 62 € | **273 €** | controllo del link nel pannello | no (già acceso) |
| 4 | Mediavine Journey | 0 € | **255 €** | AdSense approvato + traffico doppio dai 4 Paesi | no |
| 5 | Email agli iscritti «avvisami» | 28 € | **142 €** | decisione di Massimiliano sulle email | no |
| 6 | VPN sulle pagine streaming | 0 € | 19 € | programma nuovo | sì |
| 7 | Visita guidata sulle pagine «esaurito» | 3 € | 12 € | 10 minuti | no |
| 8 | Valigie precise su Amazon | 1 € | 12 € | 1 ora | no |
| 0 | Contare i clic su tutte le affiliazioni | 0 € | 0 € | 2 ore | no |
| | **Totale** | **circa 260 €** | **circa 1.760 €** | | |

**Detto chiaro.**
- Da solo questo pacchetto non cambia il fatturato. È sotto i 2.000 € anche nel caso centrale.
- Vale perché costa poco e perché usa cose già approvate: nessuna iscrizione nuova per le prime 5 mosse.
- La lezione più grande non è un'affiliazione. È il **prezzo**: nel B1 chi vince incassa 89-500 € a cliente perché dentro c'è una persona. Noi incassiamo 5,64 €.
- Le mosse per gli avvocati (consulenza a 89 €, infoimmigrazione) e per le sedi d'esame sono già nel pacchetto del piano, sez. 9, righe 2 e 4. Il prezzo di 89 € per 40 minuti è una prova in più che quel mercato paga.

---

## 8. Le 3 migliori, come prove concrete

### 1ª — Secondo prezzo «con insegnante» nella prova del Pass
- **Cosa.** Due pulsanti: «Pass 19 €» e «Pass + scritto corretto da un insegnante 49 €». Nessuno vende. Due eventi separati.
- **Quando.** 11-24/12, dentro la prova del Pass già decisa.
- **Soglia.** Almeno 3 clic sul 49 € e almeno il 30 % dei clic sul prezzo.
- **Stop.** 0 o 1 clic sul 49 €.
- **Vale.** 125 € prudente, 765 € centrale. E può togliere il costo fisso di 3.053 € l'anno, se il CAF conferma che è formazione.
- **Da Massimiliano.** La domanda al CAF che è già nel piano. Nient'altro fino al risultato.

### 2ª — HelloSafe sulle pagine dei rifiuti Schengen
- **Cosa.** Riquadro HelloSafe su 20 pagine Paese, al posto di SafetyWing. Le altre fanno da confronto. Clic contati.
- **Quando.** 29/12-11/1, dopo il verdetto dell'esperimento.
- **Soglia.** Almeno 5 clic in 14 giorni e 1 polizza nel pannello entro 28 giorni.
- **Stop.** Meno di 2 clic.
- **Vale.** 42 € prudente, 281 € centrale.
- **Da Massimiliano.** Un sì (riquadro nuovo). Poi 2 minuti per leggere il pannello HelloSafe.

### 3ª — Contare i clic e portare italki agli insegnanti dell'orale
- **Cosa.** Evento di clic su ogni affiliazione accesa (mossa 0). Su EsameB1, riquadro «Prova l'orale con un insegnante» sulle pagine `/esempi/`, con link alla ricerca di insegnanti.
- **Quando.** Subito, 27/11-10/12. EsameB1 non è fermo.
- **Soglia.** Almeno 12 clic su italki in 14 giorni. Poi 1 studente nel pannello entro 28 giorni.
- **Stop.** Meno di 4 clic: italki esce e lascia il posto al Pass.
- **Vale.** 62 € prudente, 273 € centrale. In più dà il primo numero vero su tutte le affiliazioni.
- **Da Massimiliano.** 2 minuti: guardare nel pannello italki se il link profondo è ammesso e quanti clic risultano dal 30/10.

---

## 9. Cosa resta incerto

- La lista dei siti che vincono viene da una ricerca fatta dagli Stati Uniti. Google Italia può mostrare altri siti per le frasi in italiano.
- Tranco non è il traffico. Dice solo chi è più grande di chi.
- I ricavi dei concorrenti non sono pubblici. L'unica cifra (SchengenVisaInfo sotto 5 milioni di $) è una stima di terzi.
- I tassi di acquisto dopo il clic sono ipotesi. Abbiamo un solo dato nostro: 1,4 % di clic sul libro.
- La commissione vera di HelloSafe («fino al 50 %») si conosce solo dal pannello.
- Il costo di 10 € a correzione per l'insegnante è un'ipotesi. Va chiesto a un insegnante vero.
- Se il link profondo di italki non è ammesso, la mossa 3 resta solo misura.
- Il nodo fiscale del gradino «con insegnante» va confermato dal CAF. Fino ad allora: nessuna vendita.

---

## Fonti lette il 26/11/2026

- GoatCounter `rete-siti`: `https://rete-siti.goatcounter.com/api/v0/stats/hits`, `/stats/locations`, `/stats/toprefs`.
- Tranco: `https://tranco-list.eu/api/ranks/domain/<dominio>` (dato del 25/11).
- B1: [Europass](https://www.europassitalian.com/courses/cils-online-preparation) · [Happy Languages](https://www.happylanguages.co.uk/product/cils-b1-online-course/) (da ricerca, pagina 403) · [AIS Philadelphia](https://www.aisphila.org/store/p/cp5) (da ricerca) · [Italian Foundation](https://italianfoundation.org/b1-citizenship-course/) · [Strommen](https://strommeninc.com/cils-b1-cittadinanza-citizenship-tutors/) · [Italiano Bello](https://italiano-bello.com/en/shop/percorso-cils-cittadinanza-b1/) · [infoimmigrazione, pagina B1](https://www.infoimmigrazione.com/dove-fare-test-italiano-cittadinanza/) e [consulenza online](https://www.infoimmigrazione.com/consulenza-legale-online/) · [Stranieri in Italia](https://www.stranieriinitalia.it/) · [OpenExamPrep](https://open-exam-prep.com/practice/it-b1-cils-citizenship) e [prezzi](https://open-exam-prep.com/pricing).
- Visti: [SchengenVisaInfo, statistiche](https://www.schengenvisainfo.com/statistics/) e [assicurazioni](https://www.schengenvisainfo.com/insurance/travel/) · [HelloSafe, rifiuti](https://www.hellosafe.com/schengen-visa/rejection) · [HelloSafe Atlas per i siti di visti](https://atlas.hellosafe.com/for/visa/) · [AXA Schengen, affiliazione](https://www.axa-schengen.com/en/affiliation-axa-schengen-travel-insurance) · [Insurte](https://insurte.com/easiest-country-schengen-visas) · [Mappr](https://www.mappr.co/starlink-availability-by-country/) · [Global Citizen Solutions](https://www.globalcitizensolutions.com/digital-nomad-visa/) · [Europe Visa Check](https://europevisacheck.com/affiliate-disclosure) · [ZoomInfo su SchengenVisaInfo](https://www.zoominfo.com/c/schengen-visainfo/465075737) (da ricerca).
- Viaggio: [Deep Arrival](https://deeparrival.com/travel-gear/united-carry-on-personal-item-size/) · [Monos](https://eu.monos.com/blogs/guides/carry-on-size-limits-by-airline-2026) · [Travelpro](https://travelpro.com/pages/united-airlines-carry-on-bag-size-rules-restrictions) · [Flight-Delayed](https://www.flight-delayed.com/en/blog/2026/04/10/hand-luggage-rules-2026-dimensions-and-weight-by-airline) · [Which?](https://www.which.co.uk/news/article/100ml-rule-at-uk-airport-security-new-scanners-avLDH4E9xSVg) · [Time Out](https://www.timeout.com/uk/news/eight-uk-airports-have-changed-the-100ml-liquids-rule-at-security-full-list-of-british-transport-hubs-that-dont-have-strict-liquid-limits-012626) · [Earth SIMs](https://www.earthsims.com/starlink/best-countries-starlink/) · [vaticanmuseum.co](https://vaticanmuseum.co/tickets/last-minute-vatican-museums-tickets/) · [Rustic Pathways](https://rusticpathways.com/blog/us-passport-validity-6-month-rule) · [The Points Guy](https://thepointsguy.com/guide/complete-guide-to-the-six-month-passport-validity-rule/).
- Reti pubblicitarie: [requisiti Mediavine e Journey](https://help.mediavine.com/what-does-it-take-to-get-approved-by-mediavine) · [requisiti Ezoic](https://support.ezoic.com/kb/article/getting-started-ezoics-requirements) (da febbraio 2026 minimo 250.000: chiuso per noi).
- Repo: `PIANO-FATTURATO.md` (sez. 1, 2, 8, 9), `REGOLE-FISSE.md`, `CRUSCOTTO-RETE.md`, `visaincome/dati/affiliati.json`, `visaincome/NOTE.md`, le 8 ricerche del 25-26/11.
