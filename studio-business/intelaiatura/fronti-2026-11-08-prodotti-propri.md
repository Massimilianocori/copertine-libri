# Fronte mai toccato: prodotti e strumenti propri che la gente paga direttamente (8/11/2026)

Ricerca 8/11. Modello diverso dai siti informativi: niente affiliazione, niente pubblicità. Il cliente paga noi, tramite un negozio con traffico proprio (Udemy, Gumroad Discover, Etsy, App Store, marketplace Notion) oppure tramite una pagina nostra trovata da Google.

**Settori del 6-7/11 non ripetuti** (settori nuovi USA, mercati non inglesi, fonti esterne, classifiche reti, sera). Non ripetuti neanche i prodotti già studiati: libri KDP legati ai siti e kit B1/visto/cittadinanza (`fronti-2026-10-31-prodotti.md`), stock, stampa su richiesta, puzzle e cessione per l'IA (`fronti-2026-10-31-archivio-foto.md`), app HubSpot/Pipedrive e negozi per sviluppatori (`H-software-marketplace.md`, studi 7 e 15), restauro foto (`D-prova-di-domanda.md`), ricette "film simulation" (NO di Massimiliano del 7/11).

## Fonti lette con curl l'8/11/2026

- **Gumroad Discover**: 34 ricerche ordinate per "most_reviewed", con il JSON della pagina (numero di prodotti, recensioni, prezzo). Le recensioni non sono le vendite: di solito le vendite sono 10-40 volte le recensioni, ma il rapporto non è pubblico.
- **Gumroad, pagina prezzi** (letta): "10% + $0.50 per transaction" sulle vendite dai propri link; "**30%** per transaction when new customers find and buy from you through our discover marketplace"; "**We're a Merchant of Record. Since January 1, 2025, Gumroad handles ALL your tax obligations**".
- **App Store**: iTunes Search API (Italia e USA, numero di valutazioni, prezzo, data di uscita) e la classifica RSS "top a pagamento", Foto e video, Italia.
- **Marketplace Notion**: 4.098 modelli nella categoria Finanza (campo `templatesCount`); ci sono modelli a pagamento (campo `price`: 97/147/197).
- **Autocomplete di Google**: 58 domande (IT, US, DE, ES).
- **Wikipedia (testo grezzo)**: Udemy ha 81 milioni di utenti (2025).
- **TAU Visual** (associazione nazionale dei fotografi professionisti), home: ha un sito apposta "Privacy, liberatorie, GDPR e cookies" e servizi per i soci.
- **Bloccati e non aggirati**: Etsy (403 su ricerca, market e pagine d'aiuto), Udemy (403 su sito, API, pagine d'aiuto e condizioni per gli istruttori), Envato/GraphicRiver, Creative Market, Creative Fabrica, Design Bundles, The Hungry JPEG, Canva Creators, Skillshare, Payhip, Class Central (tutti 403), Amazon.it (503), Domestika (200, ma l'elenco dei corsi si carica solo con JavaScript). Mancano quindi le vendite su Etsy e gli studenti su Udemy: sono i due dati più utili e li segno come inneschi.

## Nota fiscale (da segnalare, non risolvere)

- **IVA OSS.** Un servizio elettronico venduto direttamente a privati di altri Paesi UE segue le regole italiane solo fino a 10.000 € l'anno in tutta la UE (direttiva 2017/2455, art. 59-quater della direttiva IVA; testo non riletto oggi). Sopra la soglia si applica l'IVA del Paese del cliente tramite OSS: per un forfettario va chiesto al CAF come funziona. **Con un "merchant of record"** (Gumroad dall'1/1/2025, Udemy, App Store) il venditore verso il cliente è la piattaforma e il problema OSS non tocca Massimiliano. Resta da chiarire che tipo di reddito è (diritti, formazione, vendita commerciale), con le stesse domande già scritte in `fronti-2026-10-31-prodotti.md` sez. 1 e in `CAF-domande-2026-10-31.md`.
- **Vendite dalla pagina nostra con Stripe o PayPal**: in quel caso il venditore è Massimiliano, e restano sia l'OSS sopra 10.000 € UE sia il cancello fiscale di STRATEGIA sez. 3. Per questo tutte le stime sotto usano un merchant of record.
- **App iOS**: per pubblicare serve l'Apple Developer Program (99 $/anno, è una spesa e serve il sì di Massimiliano) e c'è la questione del codice 62.10 (REGOLE-FISSE, nodo del 9/10).

---

## 0. Risposta in breve

| # | Idea | Fonte esterna | Voto | €/anno a 18 mesi prudente / centrale / ottimista | Ore agenti + ore di Massimiliano |
|---|---|---|---|---|---|
| 1 | **Corsi registrati di fotografia in italiano su Udemy** (base con fotocamera, smartphone, Lightroom; modulo "foto immobiliari per agenti") | autocomplete "udemy fotografia" 10 (con "iphone", "masterclass", "corso"), "corso fotografia online" 10, "corso lightroom" 10; Udemy 81 milioni di utenti; Gumroad IT: CorsoFotografico.com 19,90 € con 10 recensioni | **5,5** | 480 / **2.900** / 11.300 | 40-60 + **80-100** (registrazione di 3 corsi) |
| 2 | **Kit di modulistica per fotografi in italiano** (contratto eventi, liberatoria maggiorenni/minorenni, preventivo, listino, consegna file, informativa GDPR) con pagina SEO e liberatoria gratuita | "liberatoria fotografica" 9 (word, pdf, minorenni), "contratto fotografo" 8, "preventivo fotografo" 9 (matrimonio, battesimo, comunione), "listino prezzi fotografo" 5; Gumroad: "contratto" 19 prodotti e "liberatoria" 9, nessuno per fotografi | **5** | 360 / **2.900** / 12.700 | 30-40 + 6-8 (+ revisione di un avvocato, spesa 150-300 € solo col sì) |
| 3 | Fogli di calcolo per forfettari (tasse e contributi, acconti, registro incassi) | "foglio excel forfettario" 10 (anche "gratis"), "regime forfettario calcolo" 10; Gumroad "forfettario" 12 prodotti, massimo 4 recensioni; App Store: 8 app gratuite per forfettari (5 uscite tra 2025 e 2026) | **4** | 100 / **700** / 2.500 | 20-30 + 2 |
| 4 | Modelli in inglese per fotografi (guida prezzi, guida di benvenuto per il cliente, proposta, contratto) su Etsy e Gumroad | US "photography pricing guide template" 10, "photography contract template" 10, "photography client guide template" 4; Gumroad "Project Proposal Deck – Wedding Photographer" 200 $ con 10 recensioni, "photographer pricing guide" 21 prodotti in tutto | **4** | 100 / **900** / 4.000 | 30-40 + 5 |
| 5 | Planner e agenda 2027 in italiano (PDF da stampare, digitale, budget) | "planner 2027" 10 (da stampare, gratis, pdf), "planner budget" 10 (excel, etsy, amazon) | **3,5** | 50 / **400** / 1.500 | 15-20 + 0 |
| 6 | Preset Lightroom (generali o per foto immobiliari) | Gumroad 4.640 prodotti "lightroom presets", i più recensiti gratuiti (1.856 e 819 recensioni) o di chi ha un pubblico social (5 $ con 1.874; 25 $ con 651); "lightroom presets italiano" 0 prodotti; IT "preset lightroom" 10 con "gratis" e "free"; US "real estate photography presets" 10 con "free" | **3** | 50 / **400** / 2.000 | 10-15 + 8-10 |
| 7 | Modelli Notion in italiano (budget, università, partita IVA) | marketplace Notion: 4.098 modelli nella sola categoria Finanza; IT "template notion" 10 con "italiano gratis"; Gumroad: i Notion più recensiti sono gratuiti (4.882, 4.341) | **3** | 50 / **300** / 1.500 | 15-20 + 0 |
| 8 | Modelli Canva per agenti immobiliari (volantini, schede immobile) | IT "template canva immobiliare" 0 suggerimenti, "volantino immobiliare" 6; Gumroad "realtor canva" 32 prodotti, massimo 8 recensioni; Canva Creators 403 | **3** | 50 / **300** / 1.200 | 15-20 + 0 |
| 9 | Mini-app a pagamento per professionisti (calcolo forfettario, preventivo del fotografo) | App Store IT: TaxMan 218 valutazioni (gratis), Fattura Elettronica APP 2.551, Fatture in Cloud 13.745, Super Preventivi 1.363, tutte gratuite; le app di fotografia a pagamento in classifica sono fotocamere e strumenti di ripresa (Chromagraph 14,99 €, PhotoPills 12,99 €, Cadrage 24,99 €) | **3** | 0 / **300** / 2.000 | 60-80 + 2 (+ 99 $/anno) |
| 10 | Servizio automatico foto tessera o passaporto online | IT "foto tessera online" 10 (4 con "gratis"), "foto passaporto online" 8; US "passport photo online" 10 (è il nome di un'azienda, con "reviews" e "reddit") | **3** | 0 / **300** / 2.000 | 40-60 + 2 |
| 11 | Report automatici a pagamento da registri pubblici (visure catastali e ipotecarie) | IT "visura catastale online" 10 con "gratis agenzia entrate", "con spid", "costo"; "visura ipotecaria" 10 | **2,5** | 0 / **200** / 1.500 | 40-60 + 0 (+ convenzione a pagamento) |

**Le 3 migliori:** n. 1 (corsi Udemy), n. 2 (modulistica per fotografi), n. 3 (fogli per forfettari, tenuto perché richiesto, ma a pari voto con il n. 4).

**Nessuna passa l'asticella** (voto ≥ 7 e ≥ 5.000 €/anno centrali). **Ottimista ≥ 10.000 €**: n. 1 (11.300) e n. 2 (12.700).

**Lezione del fronte.** Sui negozi leggibili (Gumroad, App Store, Notion) quasi tutti i prodotti con migliaia di recensioni sono **gratuiti**, oppure li vende chi ha già un pubblico sui social. Il traffico del negozio da solo vende poco, e in italiano ancora meno: i prodotti italiani più recensiti su Gumroad hanno 40-70 recensioni in tutto (dispense Blender 29,85 € con 55, guida TFA 9,90 € con 71). Le domande in italiano su modelli, fogli e preset sono piene di "gratis", "word", "pdf". L'unico negozio che porta compratori da solo, senza social, e dove il mestiere di Massimiliano conta, è **Udemy**. Proprio lì però i dati sono chiusi a curl (403).

---

## 1. Corsi registrati di fotografia in italiano su Udemy — voto 5,5 (approfondita)

**Domanda.** Autocomplete IT: "udemy fotografia" 10 suggerimenti ("udemy fotografia iphone", "udemy corso fotografia", "udemy masterclass fotografia"): c'è chi cerca il corso **direttamente su Udemy**. "corso fotografia online" 10 (ma "gratuito", "riconosciuto gratis", "gratis nikon/canon"), "corso fotografia base" 10 (quasi tutte città: corsi in aula), "corso lightroom" 10 ("gratis", "classic", "online", "mobile"), "corso photoshop online" 9 ("con attestato"). "corso fotografia immobiliare" 2, "corso fotografia matrimonio" 1. Stessa forma in DE ("fotografie kurs online" 10 con "smartphone" e "handy") e in ES ("curso fotografia online" 10).

**Chi paga e come.** Lo studente paga Udemy, che vende, incassa e gestisce l'IVA; l'istruttore riceve una quota. **Quota non letta** (pagine Udemy 403). Da conoscenza, non da fonte di oggi: circa il 37 % sulle vendite arrivate dal negozio, di più su quelle portate dall'istruttore; prezzi di listino 20-60 €, ma le vendite avvengono quasi sempre in promozione a 10-15 €. Netto stimato: **circa 4 € a vendita**.

**Concorrenza.** Su Udemy i corsi di fotografia in italiano esistono, ma non ho potuto contarli né leggere gli studenti. Fuori da Udemy ci sono i corsi gratuiti su YouTube e quelli dei marchi (gratis Nikon e Canon nell'autocomplete), e i venditori italiani su Gumroad sono piccoli: CorsoFotografico.com "Composizione Intuitiva" 19,90 € con 10 recensioni, "iFoto Pro" (iPhone) 37 € con 2.

**Cosa si costruisce.** Tre corsi da 2-3 ore ciascuno: (a) "Fotografia da zero con la tua fotocamera", (b) "Fotografare bene con lo smartphone" (il pubblico più largo: "udemy fotografia iphone", DE "smartphone fotografie kurs"), (c) "Lightroom dalla A alla Z", con un modulo sulle foto di casa per agenti e proprietari. Gli agenti preparano scaletta, slide, esercizi, sottotitoli, testi della scheda e quiz. Massimiliano registra lo schermo e la voce, più qualche ripresa sul campo.

**Ore.** Agenti 40-60. Massimiliano **80-100 ore in tutto**: circa 25-35 a corso, tra registrazione, rifacimenti e scatti d'esempio, cioè circa 5 ore a settimana per 4-5 mesi.

**Stima a 18 mesi.** Il primo corso esce verso il mese 3, gli altri al 6 e al 9. Netto 4 € a vendita; vendite organiche al mese per corso a regime:
- Prudente: 2 corsi × 5 vendite × 4 € × 12 = **480 €**
- Centrale: 3 corsi × 20 × 4 € × 12 = **2.880 €** (arrotondato a 2.900)
- Ottimista: 3 corsi × 70 × 4,5 € × 12 = **11.340 €** (serve un corso nelle prime posizioni della ricerca "fotografia" di Udemy Italia, oppure l'ingresso in Udemy Business, che però sceglie lei i corsi)

**Rischi.** La quota e le promozioni le decide Udemy, e le ha già abbassate in passato. I primi mesi di un corso nuovo senza recensioni sono lenti. Le ore di Massimiliano sono tante e anticipate, e niente garantisce il ritorno. Il fisco dipende dal tipo di reddito (formazione o diritti: domanda per il CAF), mentre l'OSS non lo tocca perché vende Udemy.

**Innesco per salire a 6,5-7.** Massimiliano apre Udemy dal browser (5 minuti, non lo può fare curl), cerca "fotografia" con lingua italiano e annota il numero di studenti e di recensioni dei primi 20 corsi e la data di uscita. Si va avanti solo se **almeno 3 corsi usciti negli ultimi 2 anni hanno più di 300 recensioni**, segno che chi arriva adesso vende ancora. Altrimenti NO, come per i libri tongue drum (vince chi c'è già).

## 2. Kit di modulistica per fotografi in italiano — voto 5 (approfondita)

**Domanda.** "liberatoria fotografica" 9 suggerimenti ("minorenni word", "pdf", "per minorenni", "word", "per maggiorenni"), "contratto fotografo" 8 ("pdf", "matrimonio pdf", "freelance", "tra fotografo e cliente", "esempio"), "preventivo fotografo" 9 ("matrimonio", "matrimonio pdf", "battesimo", "comunione"), "listino prezzi fotografo" 5. "modello preventivo fotografo" e "modello contratto fotografo" danno 1 e 0 suggerimenti. Quasi ogni domanda chiede un file ("word", "pdf", "esempio"): chi cerca vuole un modello, spesso gratis.

**Concorrenza.** TAU Visual (associazione nazionale dei fotografi professionisti) ha un sito apposta "Privacy, liberatorie, GDPR e cookies" e servizi riservati ai soci. Ci sono poi blog di avvocati e siti di moduli gratuiti (non verificati: i motori di ricerca sono chiusi a curl). Su Gumroad "contratto" dà 19 prodotti e "liberatoria" 9, nessuno per fotografi: in italiano lì non c'è né concorrenza né traffico.

**Chi paga.** Fotografi all'inizio e fotografi d'eventi (battesimi, comunioni, matrimoni), cioè proprio il mestiere di Massimiliano. Prezzo 19-29 € il kit, venduto con Gumroad come merchant of record (dai propri link: 10 % + 0,50 $). Netto circa 20 €.

**Canale senza social.** Una pagina (sezione di un sito esistente o sito piccolo nuovo) con la liberatoria base gratuita in Word e PDF, che porta le visite, e il kit completo a pagamento: contratto eventi, liberatoria minorenni, preventivo e listino modificabili, informativa GDPR, modulo di consegna file.

**Ore.** Agenti 30-40 (modelli, pagina, guide "cosa scrivere nel contratto"). Massimiliano 6-8 ore: rivede i modelli con quello che usa davvero con i suoi clienti, e decide se pagare una revisione legale (150-300 €, solo col suo sì).

**Stima a 18 mesi.** Visite al mese 300 / 1.200 / 4.000, conversione 0,5 % / 1 % / 1,2 %, netto 20 / 20 / 22 €:
- Prudente: 300 × 0,5 % × 20 × 12 = **360 €**
- Centrale: 1.200 × 1 % × 20 × 12 = **2.880 €** (arrotondato a 2.900)
- Ottimista: 4.000 × 1,2 % × 22 × 12 = **12.670 €**

**Rischi.** Responsabilità se un contratto è scritto male (per questo la revisione legale). Chi cerca vuole il modello gratis. TAU Visual e i blog legali hanno più autorità. Il pubblico è piccolo: i fotografi in Italia sono decine di migliaia, numero ISTAT non letto oggi.

**Innesco.** Nessuno con i dati di oggi. Si riapre se Search Console di un sito della rete mostra già visite su "liberatoria" o "contratto fotografo", oppure se Etsy (letto da Massimiliano dal browser) mostra kit italiani per fotografi con più di 100 vendite.

## 3. Fogli di calcolo per forfettari — voto 4 (approfondita)

**Domanda.** "foglio excel forfettario" 10 ("regime forfettario", "gestione forfettario", "calcolo regime forfettario **gratis**", "calcolo tasse", "contabilità"), "regime forfettario calcolo" 10 ("tasse", "netto", "inps", "netto online", "tasse e contributi"), "calcolo tasse forfettario excel" 3, "gestionale forfettario" 1. I forfettari sono circa 2 milioni (dato MEF, non riletto oggi).

**Concorrenza (letta).** App Store IT, tutte gratuite: TaxMan (218 valutazioni), ForfettApp (34), Tasse Forfettario (21), Forfee (uscita 20/10/2025), Forfettario Simulator 2026 (26/4/2026), Salvadanaio Forfettario (30/4/2026), netto (15/7/2026), Konto (8/9/2026): **5 strumenti gratuiti nuovi in 12 mesi**. A questi si aggiungono Fiscozen (app e calcolatori gratuiti), Fatture in Cloud (13.745 valutazioni) e i calcolatori online gratuiti. Su Gumroad "forfettario" dà 12 prodotti: "Bussola Partita IVA" 19,90 € con 0 recensioni, "Forfettario Inarcassa 5.1" 19,90 € con 0, "Excel - Preventivi e Gestione Costi" con 4. Il prodotto c'è, ma nessuno lo compra.

**Canale.** Gumroad non porta compratori italiani (vedi sopra), Etsy Italia è piccolo e illeggibile, la SEO su "calcolo forfettario" se la contendono Fiscozen, Fatture in Cloud e i commercialisti online.

**Ore.** Agenti 20-30. Massimiliano 2 (prova del foglio sui suoi numeri).

**Stima.** A 20 € netti a copia: 5 / 35 / 125 copie **all'anno** = 100 / **700** / 2.500 €/anno. L'ottimista richiede una pagina nostra in prima pagina su "foglio excel forfettario", davanti a Fiscozen e Fatture in Cloud. Voto basso per tre motivi: si cerca "gratis", è pieno di strumenti gratuiti nuovi e c'è la responsabilità di un calcolo fiscale sbagliato.

---

## 4. Le altre righe in breve

- **4. Modelli in inglese per fotografi (Etsy/Gumroad), voto 4.** La domanda USA c'è ("photography contract template" 10, ma con "free", "word", "google docs", "uk", "australia"), e i prezzi sono alti: la proposta per fotografi di matrimonio costa 200 $ e ha 10 recensioni. Il negozio giusto sarebbe Etsy, che però è illeggibile (403); un tentativo su Etsy è già fallito per mancanza di distribuzione (STRATEGIA sez. 1). I contratti americani cambiano da Stato a Stato. Commissioni Etsy: 6,5 % + 3 % + 0,25 $ + 0,20 $ a inserzione, Offsite Ads 12-15 % (`H-software-marketplace.md`).
- **5. Planner 2027, voto 3,5.** Domanda forte ma stagionale (settembre-gennaio: siamo già a novembre) e piena di "gratis". La forma che vende senza social è l'agenda KDP, che è la corsia libri già esistente: se mai, va lì.
- **6. Preset Lightroom, voto 3.** 4.640 prodotti solo su Gumroad, e chi vende ha un pubblico sui social. In più assomiglia alle ricette con le foto di Massimiliano, a cui il 7/11 ha detto "lascia stare".
- **7-8. Notion e Canva in italiano, voto 3.** Le domande italiane hanno "gratis", su Canva immobiliare non c'è nessun suggerimento, e i modelli più usati sono gratuiti.
- **9. Mini-app a pagamento, voto 3.** In Italia le app per forfettari e preventivi sono tutte gratuite. In più servono 99 $ l'anno e c'è il nodo del codice 62.10.
- **10. Foto tessera o passaporto automatica, voto 3.** Domanda "gratis" e concorrenti grandi con pubblicità. È vicina ai documenti di viaggio, cioè a temi già coperti.
- **11. Visure automatiche, voto 2,5.** L'Agenzia delle Entrate dà la visura catastale gratis con lo SPID (si vede nell'autocomplete). Rivenderla richiede una convenzione a pagamento, e i rivenditori fanno già pubblicità.

## 5. Cosa chiedere a Massimiliano (5 minuti dal browser, nessuna spesa)

1. **Udemy**: ricerca "fotografia" in italiano, i primi 20 corsi con studenti, recensioni e data di uscita (innesco del n. 1).
2. **Etsy**: "contratto fotografo", "liberatoria fotografica", "photography pricing guide template": numero di vendite dei primi 10 negozi (innesco dei n. 2 e 4).
3. Se il n. 1 passa l'innesco: è disposto a mettere circa 5 ore a settimana per 4-5 mesi a registrare?
