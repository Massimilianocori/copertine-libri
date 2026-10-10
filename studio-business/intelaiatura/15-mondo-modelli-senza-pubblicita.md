# Angolo D: guadagnare nel mondo senza siti a pubblicità

Ricerca del **10 ottobre 2026** per Massimiliano Cori. Pagine lette con `curl` dal server e con la ricerca web. I file scaricati sono in `globale/D/dl/` e sono stati letti solo con `python3 -I`; gli script sono in `globale/D/script/`. Non ho toccato il repository.
Gli studi 1-14 non vengono ripetuti: dove un canale era già stato valutato (studio 7: Apify, RapidAPI, Chrome, Notion, Figma, GitHub, Zapier; studio 13: app sugli scioperi e avvisi a pagamento) aggiungo solo le prove nuove.

---

## 0. Risposta in breve

1. **Nessun modello di questo angolo cambia l'ordine di grandezza.** Sommati con prudenza, i canali che reggono valgono **250-1.500 €/anno a 18 mesi**, non di più. Nel 2026 quasi tutti i negozi che pagano i creatori hanno **chiuso le porte ai nuovi** oppure **tagliato le quote**:
   - Envato non accetta nuovi autori da marzo 2026.
   - Figma è chiuso ai nuovi venditori.
   - Canva ha sospeso le iscrizioni per foto ed elementi.
   - Alamy ha portato al 15-20 % la quota dei piccoli dal 1/9/2026.
   - Amazon Merch ha dimezzato le royalty di chi non porta traffico da fuori (1/6/2026).
   - Getty/iStock ha saltato il pagamento degli interessi sui debiti il 1/9/2026.
2. **L'idea migliore è anche la più vecchia: dare in licenza l'archivio fotografico che Massimiliano ha già.** Le foto si caricano su Adobe Stock, e su Shutterstock in secondo piano. Non è lavoro da fotografo: non si scatta niente. Claude sceglie le foto e scrive titoli e parole chiave; l'agenzia vende e paga una royalty. **Il venditore è l'agenzia.** Probabilmente è anche il caso fiscale più pulito di tutti: è la licenza di foto proprie, cioè il mestiere per cui la P.IVA è già aperta (da confermare con il professionista). I soldi sono pochi: **100-450 €/anno a 18 mesi** con 1.000-2.000 foto accettate. È **facoltativo**, perché tocca il tema fotografia.
3. **Apify resta un test passivo, e i dati nuovi dicono di non allargarlo.** Ho scaricato le statistiche del negozio: chi ha pubblicato **149 e 495 Actor** su dati pubblici ha in media **1,3-4,8 utenti al mese per Actor** (mediana 1). **Il venditore resta Massimiliano** (Apify emette le fatture a suo nome).
4. **Calendari Calvendo con le stesse foto:** Calvendo fa da editore, vende su Amazon e nelle librerie e paga royalty come KDP. Costo zero, ma il catalogo supera i 100.000 calendari e la media storica è di **meno di 10 copie per titolo all'anno**. È un piccolo extra, da fare solo se lo stock mostra che le foto vendono.
5. **Gumroad è "merchant of record" dal 1/1/2025** (lo dice la sua pagina prezzi). Non porta clienti, ma è lo strumento per vendere più avanti un PDF o un feed dai siti che abbiamo, **senza gestire l'IVA estera**. Non apre però nessun canale nuovo. E un MoR **non toglie il cancello fiscale**: il reddito resta di Massimiliano.

---

## 1. Tabella di tutti i modelli esaminati

Legenda: **venditore** = chi vende legalmente al cliente finale (chi incassa e chi applica l'IVA). "Lui" = Massimiliano.

| # | Modello | Chi paga e come | Venditore | Lavoro di lui | Prova decisiva (sez. 3-4) | 18 mesi prudente | Verdetto |
|---|---|---|---|---|---|---|---|
| 1 | **Archivio foto su Adobe Stock** (+ Shutterstock) | L'agenzia paga una royalty: Adobe 33 %, Shutterstock 15-40 % a scaglioni | **Agenzia** (Adobe, Shutterstock) | 20 min di iscrizione e modulo W-8BEN; poi ~5 min a settimana per caricare i lotti già pronti | Fotografo professionista, set. 2026: Adobe 93 $ al mese con 4.927 immagini = **0,23 $/immagine/anno**; Shutterstock 0,036 $ | **100-450 €/anno** | **SÌ, facoltativo** (test 200 foto) |
| 1b | Arcangel (foto per copertine di libri) | 50 %, licenze diritti gestiti in esclusiva | Agenzia | 15 min di candidatura | ~200 $ netti per licenza, ma 5 vendite all'anno su 6.736 immagini; rifiuti 74-95 % | 0-400 € (biglietto della lotteria) | Facoltativo, con le stesse foto |
| 2 | **Apify Store** (Actor a pagamento per evento) | Gli utenti pagano per evento; Apify trattiene il 20 % più i costi | **Lui** (Store Terms §4.1; fatture emesse da Apify a suo nome) | 10 min di account; KYC solo al primo pagamento | 149 Actor = 717 utenti al mese; 495 Actor = 637; per Actor mediana 1 | **100-800 €/anno** | **Test passivo come da studio 7, senza allargarlo** |
| 3 | **Calendari Calvendo** | Royalty dell'editore su ogni copia | **Calvendo** (contratto editoriale) | 20-30 min per calendario nell'editor online | Oltre 100.000 calendari in catalogo; <10 copie/titolo/anno (dato 2014) | 30-200 €/anno | Piccolo SÌ, dopo lo stock |
| 4 | **Gumroad** (MoR dal 2025) | Clienti diretti; Gumroad trattiene 10 % + 0,50 $ (30 % da Discover) | **Gumroad per l'IVA**, lui per il reddito | 15 min | La pagina prezzi lo conferma; il traffico va portato da sé | 0 € da solo | **Strumento** per i siti esistenti, non un canale |
| 5 | Canva Creators (template, foto) | Fondo royalty mensile per uso (riservato) | **Canva** | 5 min (lista d'interesse) | Iscrizioni per gli "elementi" (foto) **sospese**; template su candidatura, "beta", mesi di attesa | 0 € (non misurabile) | Solo lista d'interesse |
| 6 | Hugging Face / Kaggle | Nessun pagamento ai creatori di dataset | — | — | Nessun programma trovato; Kaggle paga solo premi di gara (lavoro, non rendita) | 0 € | NO |
| 7 | AWS Data Exchange | Abbonati aziendali | Lui (AWS riscuote) | Account AWS con carta, apertura di una pratica al supporto, costi di archiviazione | Un privato residente UE può entrare, ma costa e nessuno trova un fornitore sconosciuto | 0 € | NO |
| 8 | Datarade | Aziende, trattative fuori piattaforma | Lui | Trattative B2B | Piano gratis: 30 % di commissione, 3 schede, 3 contatti; i contratti si chiudono "off-platform" | 0 € | NO |
| 9 | Snowflake Marketplace | Aziende tramite Stripe | Lui | Account pagato | Serve un account "full (non-trial)": costi fissi | 0 € | NO |
| 10 | RapidAPI | — | — | — | Già scartato (studio 7: 25 %, solo PayPal); nessuna prova nuova | — | NO |
| 11 | Estensioni Chrome | — | Lui | — | Già scartato (studio 7: nessun pagamento nello store, mediana 18 utenti) | — | NO |
| 12 | App Google Play | Google incassa (15 %) o AdMob | **Google** per gli acquisti in app | 25 $ + **12 tester veri per 14 giorni** + verifica d'identità | Regola per gli account personali creati dopo nov. 2023; RevenueCat: 15.000 nuove app in abbonamento al mese | 0-300 € | NO |
| 13 | App Store Apple | Apple incassa | Apple | **99 $/anno** | Costo fisso prima degli incassi: viola la regola 1 | — | NO |
| 14 | Microsoft Store (PWA) | Pubblicità o pagamento proprio (0 % a Microsoft per le app non-gioco) | Lui o Microsoft | 10 min, iscrizione gratis dal 2025 | Gratis, ma il traffico dello store è minimo e nessuno paga per una PWA di servizio | 0 € | NO (al massimo una vetrina in più per i siti) |
| 15 | Template Notion | 8 % + 0,40 $ | Lui (Notion gestisce l'IVA) | Lista d'attesa di mesi | Studio 7; nessuna prova nuova | 0-200 € | NO |
| 16 | Figma Community | — | — | — | «We are not approving new creators to sell paid files» (letto il 10/10/2026) | — | NO (chiuso) |
| 17 | Envato (Elements e Market) | 50 % fisso dal 1/7/2026 | Envato/autore | — | **Nuove candidature chiuse da marzo 2026** (fonti secondarie concordi) | — | NO (chiuso) |
| 18 | Creative Market | 50 % | Creative Market (riscuote le tasse USA) | Candidatura con 10-20 lavori | 50 % di commissione, prodotti di design che hanno bisogno di gusto umano, mercato pieno di grafica generata dall'IA | 0-100 € | NO |
| 19 | Framer / Webflow template | Framer: 0 % di commissione | Lui | Lavoro nell'editor visuale + revisione | Si costruiscono a mano nell'editor; Claude non lo controlla | 0 € | NO |
| 20 | Fogli Google/Excel | — | Lui (Etsy, Gumroad) | — | Nessun negozio che porti traffico e paghi; su Etsy sarebbe un doppione del negozio che c'è già | — | NO |
| 21 | GPT Store / app in ChatGPT | — | Lo sviluppatore | — | Il programma di ricavi per i GPT (annunciato a gennaio 2024 solo per gli USA) non risulta attivo; le app ChatGPT vendono solo **beni fisici** con pagamento sul sito dello sviluppatore | 0 € | NO |
| 22 | Amazon Merch on Demand | Royalty Amazon | Amazon | Candidatura su invito | **Dal 1/6/2026 royalty dimezzata** per chi vende solo con il traffico Amazon (19,99 $: da 4,88 a 2,44 $) | 0-150 € | NO |
| 23 | Redbubble / TeePublic | Margine dell'artista | Piattaforma | — | Ricavi del gruppo in calo (FY26 408,5 M A$, −30 M); commissioni sugli account degli artisti | 0 € | NO |
| 24 | Grafica vettoriale fatta da Claude su Adobe Stock | Royalty 33 % | Adobe | Come il n. 1 | Metà della libreria è già IA; limiti di caricamento dal 2025; sondaggio: 77 % dei contributori IA guadagna da 0 a 100 $ al mese | 0-100 € | Solo come mini-prova dentro il n. 1 |
| 25 | Newsletter con sponsor | Rete pubblicitaria beehiiv o sponsor diretti | beehiiv / lui | — | La rete pubblicitaria richiede un **piano a pagamento**; le Boosts via email sono chiuse dal 10/4/2026; gli sponsor diretti vogliono contatti a freddo | 0 € da sola | NO (resta la lista email dei siti, già in strategia) |
| 26 | YouTube "senza volto" | AdSense dentro YPP | Google | Account + caricamenti | 1.000 iscritti + 4.000 ore; regola "inauthentic content" (15/7/2025); **i caricamenti via API da progetti non verificati restano privati** | 0 € a 12 mesi | NO |
| 27 | Podcast | Spotify Partner Program | Spotify | Voce, tempo | **Italia non tra i Paesi ammessi**; soglia di 2.000 ore di ascolto in 30 giorni | 0 € | NO |
| 28 | Medium Partner Program | Pagato dagli abbonati di Medium | Medium | — | Italia ammessa, ma «AI-generated writing … is not allowed to be paywalled» | 0 € | NO |
| 29 | Dataset di foto per addestrare l'IA (Wirestock, contributi Adobe/Shutterstock) | Bonus o pagamenti una tantum | Piattaforma | Dentro il n. 1 | Fotografo pro: 53 $ di bonus Adobe Firefly + 25 $/mese da Wirestock | +20-60 €/anno | Arriva da sola con il n. 1 |

---

## 2. Le idee migliori, con le prove

### 2.1 IDEA 1 (facoltativa): l'archivio fotografico in licenza su Adobe Stock (e Shutterstock)

**È lavoro da fotografo?** No: non si scatta, non si incontra nessun cliente e non c'è nessun evento. Si caricano foto che esistono già. Lo presento comunque come **facoltativo**, perché Massimiliano ha detto no alla fotografia come mestiere. Decide lui.

**Chi paga, chi vende**
- **Adobe Stock**: il cliente compra la licenza da Adobe; il contributore riceve il **33 %** sul prezzo netto per foto, vettoriali e illustrazioni (35 % per i video). Pagamento da **25 $** su PayPal, Payoneer o Skrill, dopo almeno 45 giorni dalla prima vendita ([Adobe, royalty rates](https://helpx.adobe.com/stock/contributor/payments-earnings/royalties-pricing/royalty-rates-assets.html); [pricing & payment](https://helpx.adobe.com/stock/contributor/payments-earnings/royalties-pricing/pricing-payment-guidelines.html), pagine di giugno-luglio 2026). Ritenuta USA per l'Italia **8 %** con il W-8BEN, **30 %** senza ([tabella Adobe per Paese](https://helpx.adobe.com/stock/contributor/payments-earnings/payment-taxes/tax-witholding-rates-country.html)).
- **Shutterstock**: 6 livelli **dal 15 al 40 %**, che ripartono dal livello 1 ogni 1° gennaio ([submit.shutterstock.com](https://submit.shutterstock.com/help/en/articles/10594604)). Per un nuovo contributore sono di fatto 0,10-0,25 $ a download (fonte secondaria).
- **Venditore: l'agenzia.** Massimiliano concede la licenza e riceve una royalty. È lo stesso schema di KDP.

**Prove di quanto rende un'immagine (dati veri, settembre 2026).** Alexandre Rotenberg, fotografo di viaggio da 12 anni, pubblica ogni mese le sue entrate. Settembre 2026 ([report](https://brutallyhonestmicrostock.com/2026/10/01/september-2026-earnings-and-news-report/), letto il 10/10/2026):

| Agenzia | Immagini | Netto settembre | Resa per immagine all'anno (calcolo mio) |
|---|---|---|---|
| Adobe Stock | 4.927 | 93 $ (+53 $ di bonus Firefly IA) | **0,23 $** |
| iStock (Getty) | 9.365 | 56 $ | 0,07 $ |
| Alamy | 17.500 | 40 $ | 0,03 $ |
| Shutterstock | 12.849 | 38 $ ("il peggior risultato dal 2014") | 0,036 $ |
| DepositPhotos / Dreamstime | 8.884 / 9.876 | 7 $ / 3 $ | 0,01 $ / 0,004 $ |
| Arcangel (copertine di libri, esclusiva) | 6.736 | 200 $ (una licenza) | ~0,36 $ |
| **Totale immagini** | | **578 $** (tutto incluso con i video: 765 $; settembre 2025: 857 $) | |

Il mercato si restringe:
- Getty ha saltato il pagamento degli interessi il 1/9/2026 e si parla di Chapter 11 ([stesso autore, 30/9/2026](https://brutallyhonestmicrostock.com/2026/09/30/getty-images-on-the-brink-what-a-potential-chapter-11-could-mean-for-contributors/)).
- La fusione Getty-Shutterstock è saltata il 30/6/2026 ([10-Q Shutterstock](https://www.sec.gov/Archives/edgar/data/0001549346/000154934626000029/sstk-20260630.htm)).
- Alamy dal 1/9/2026 paga **15 %** sotto i 250 $ l'anno e **20 %** fino a 3.000 $ ([Rotenberg, 13/7/2026](https://brutallyhonestmicrostock.com/2026/07/13/alamys-new-olympic-event-the-commission-cut/)).

**Conclusione: si carica solo su Adobe** (la più redditizia: anche il sondaggio di Microstock Life la indica «far and away» come prima) **e su Shutterstock** (costo zero, stesso file). Niente iStock finché Getty non chiarisce, niente Alamy.

**Cosa può andare e cosa no**
- **Sì:** paesaggi, città e dettagli italiani, cibo, oggetti, texture, architettura pubblica.
- **No:** **le foto dei matrimoni e dei clienti.** Sono persone riconoscibili senza liberatoria e quindi dati personali: si viola la regola "niente dati personali" e il diritto d'immagine. Lo stesso per marchi e loghi in vista e per luoghi privati senza liberatoria.

**Lavoro di Claude**
- Scegliere le foto adatte guardandole a lotti (Claude legge le immagini).
- Scrivere in inglese titolo e 25-49 parole chiave.
- Inserirli nei file (IPTC) oppure prepararli come **CSV**: Adobe accetta CSV per collegare titoli, parole chiave e categorie fino a 5.000 righe ([Adobe, upload CSV](https://helpx.adobe.com/stock/contributor/manage-your-portfolio/upload-csv-file.html)).
- Un registro di cosa è stato caricato, accettato e venduto.
- La spedizione automatica via SFTP non è confermata (il server passa solo HTTPS), quindi **il caricamento lo fa lui** trascinando la cartella pronta.

**Lavoro di lui**
- Account Adobe Stock Contributor e Shutterstock Contributor, modulo W-8BEN online, PayPal: **~20 minuti una volta**.
- Condividere una cartella dell'archivio (Google Drive).
- Poi **~5 minuti a settimana** per trascinare il lotto. Per i nuovi account Adobe parte da limiti bassi, ~50 file a settimana secondo il forum ([community Adobe](https://community.adobe.com/questions-38/submission-limit-reached-after-uploading-only-2-3-photos-need-help-1640160); i limiti esistono da maggio 2025, [cined](https://www.cined.com/ai-flood-on-adobe-stock-nearly-half-of-all-images-now-ai-generated/)).
- È l'unico canale di questo rapporto con un piccolo lavoro ricorrente, per 4-6 mesi.

**Fiscale (domanda da aggiungere alla consulenza, non è un parere).** Le royalty che le agenzie pagano per foto proprie sembrano rientrare nel mestiere per cui la P.IVA da fotografo è già aperta: niente Camera di Commercio e niente INPS commercianti, a differenza di AdSense e degli affiliati. Domanda da fare: *"Le royalty di Adobe Stock/Shutterstock per mie foto rientrano nel mio codice da fotografo, in Gestione Separata?"*. Se la risposta è sì, è **l'unico ricavo di questa ricerca che non apre il cancello fiscale**.

**Stima prudente.** Ipotesi:
- accettate 1.000-2.000 foto entro il mese 12;
- resa a regime **0,08-0,23 $/immagine/anno su Adobe** (il minimo è un terzo del dato del professionista, perché il portafoglio è nuovo e generico) e **0,02-0,036 $ su Shutterstock**;
- il primo pagamento non arriva prima del mese 3-4.

| | 12 mesi (cumulato) | 18 mesi (all'anno) |
|---|---|---|
| Adobe | 25-150 € | 80-400 € |
| Shutterstock + bonus IA | 5-40 € | 20-60 € |
| **Totale** | **30-190 €** | **100-450 €/anno** |

**Rischi:** l'IA generativa riduce la domanda di foto generiche (metà della libreria Adobe è già IA); le agenzie tagliano le quote; ci sono limiti di caricamento; le foto con persone non si possono usare.

**Test a costo zero, con soglie scritte prima**
1. Claude sceglie **200 foto** e prepara i metadati; lui le carica in 4 settimane.
2. **Passa** se a 60 giorni dall'ultima accettazione: **accettazione ≥ 60 %** e **≥ 5 download** in tutto su Adobe.
3. Se passa si continua fino a 1.000-2.000 foto. **Si ferma** se al giorno 180, con ≥ 800 foto online, la media resta **sotto i 10 $ al mese** (cioè sotto 0,15 $/immagine/anno).

**Facoltativo, a parte: Arcangel** (foto per copertine di libri, mercato che Massimiliano conosce da KDP). Paga il 50 % su licenze "rights-managed" esclusive: in media ~200 $ netti a licenza (Rotenberg), ma solo 5 vendite in un anno su 6.736 immagini e un tasso di rifiuto del 74-95 % ([Rotenberg 2021](https://brutallyhonestmicrostock.com/2021/04/23/making-sense-of-95-rejection-rate-at-arcangel-images-book-covers)). Si può candidare con 20 foto "narrative" (sagome, atmosfere, senza volti riconoscibili). Non entra nelle stime.

### 2.2 IDEA 2: Apify, il punto con i dati nuovi (resta un test passivo)

Lo studio 7 aveva già scaricato il catalogo (mediana 4 utenti in 30 giorni; tra i 1.000 Actor più recenti, uno solo con ≥ 10 utenti). Oggi ho aggiunto due cose: 20 ricerche per nicchia su fonti stabili (dati ufficiali o API pubbliche, non siti fragili) e i portafogli di chi fa esattamente quello che farebbe Claude, cioè molti Actor su dati pubblici. Fonte: API pubblica `api.apify.com/v2/store`, 10/10/2026, file in `dl/apify/`.

| Nicchia (ricerca) | Actor | Migliore (utenti 30 gg / totali) | Actor con ≥ 10 utenti/mese |
|---|---|---|---|
| whois domini | 554 | 64 / 251 | 3 |
| marchi (USPTO, EUIPO) | 225 | 35 / 75 | 6 |
| brevetti | 3.941 | 35 / 105 | 2 |
| registri imprese | 2.644 | 30 / 304 (Brasile CNPJ) | 5 |
| gare pubbliche UK/EU (TED) | 404 / 335 | 11 / 16; 12 / 43 | 2 / 1 |
| cambi valute, sanzioni, Eurostat, qualità dell'aria | 60-2.652 | 2-6 | 0-1 |
| voli (scraper di Google Flights) | 3.390 | 380 / 2.859 | 20 (ma fragili e a rischio condizioni d'uso) |

| Creatore con molti Actor su dati pubblici | Actor | Utenti in 30 gg (somma) | Per Actor | Mediana |
|---|---|---|---|---|
| ryanclinton | 149 | 717 | 4,8 | 1 |
| nexgendata | 495 | 637 | 1,3 | 1 |
| automation-lab (anche social e e-commerce) | 765 | 12.745 | 16,7 | 2 |

**Unico dato di ricavo trovato:** un pacchetto di 2 Actor venduto su Microns a marzo 2026 aveva **4 clienti paganti**, **157 $ lordi nel mese migliore** e ~200 visite al mese da Google. Funzionava a "noleggio" a 50 $ al mese, un modello **ritirato da Apify il 1/10/2026** ([microns.io](https://www.microns.io/startup-listings/apify-actor-suite)).
- **Venditore: Massimiliano.** «the contractual relationship … is established between you and the User» (Store Publishing Terms §4.1, già citato nello studio 7). Apify emette le fatture a suo nome (self-billing). È quindi una **vendita diretta di servizi**, ferma come le altre finché non arriva la risposta fiscale. Si può però pubblicare e accumulare: i saldi decadono solo dopo 12 mesi senza KYC.
- **Lavoro:** Claude 3-6 ore per Actor più ~1 ora al mese di manutenzione per fonti stabili. Lui: 10 minuti di account (piano gratis, senza carta).
- **Stima prudente** (rivista leggermente al ribasso rispetto allo studio 7): 3-5 Actor su fonti stabili con domanda vista, cioè scioperi MIT, marchi EUIPO, gare TED. Si attendono 1,3-4,8 utenti per Actor al mese, che spendono 1-3 $ → **12 mesi 50-400 €; 18 mesi 100-800 €/anno**.
- **Avvertenza dati personali:** registri imprese, whois e marchi contengono nomi di persone. Si scelgono solo fonti senza dati personali (TED, scioperi, carburanti) oppure si filtrano i campi.
- **Test:** pubblicare 3 Actor. **Passa** se al giorno 120 sono **≥ 15 utenti in 30 giorni in tutto e ≥ 20 $ maturati**; altrimenti si congela senza costruirne altri. **Non va allargato a decine di Actor:** chi lo ha fatto ha comunque 1-5 utenti per Actor.

### 2.3 IDEA 3 (piccola): calendari Calvendo con le stesse foto

- **Chi paga, chi vende:** Calvendo (Monaco) è un **editore**: «CALVENDO verlangt keine Gebühren und keine Kostenbeteiligung» e paga un «Honorar» come «prozentualer Anteil an den … erzielten Nettoeinnahmen», secondo tabelle di royalty non pubbliche ([condizioni generali 2024](https://download.calvendo.de/CALVENDO_AGB_2024.pdf), §1.2 e §6.3). I calendari hanno l'ISBN e sono venduti su Amazon e in 14 siti in UK, DE, FR, ES, IT e CH (testimonianza su [calvendo.com](https://www.calvendo.com/)). **Venditore: Calvendo e i negozi.** Il contratto è editoriale, come KDP.
- **Prove sulla domanda:** nel 2014 c'erano oltre 70.000 titoli con ISBN, cioè «less than 10 copies per title per year» in media ([eurolitnetwork](https://www.eurolitnetwork.com/a-leaf-out-of-the-calendar-publishers-book-by-dirk-rumberg/)). Oggi il negozio dichiara **oltre 100.000 calendari**. Calvendo accetta anche immagini IA, quindi la concorrenza cresce.
- **Lavoro:** una giuria approva; il calendario si compone nell'**editor online di Calvendo**. Claude sceglie le 13 foto, scrive titolo e testi e prepara le immagini; lui le inserisce nell'editor (20-30 minuti per calendario). Si lavora per la stagione: un calendario per il 2028 va presentato in primavera-estate 2027.
- **Stima:** 5 calendari × 3-10 copie × 2-4 € (stima mia: la tabella delle royalty non è pubblica) = **30-200 €/anno**.
- **Test:** 2 calendari a tema italiano (es. "Dolomiti", "Borghi della Toscana", scelti tra le foto che vendono su Adobe). **Passa** se nella prima stagione vendono **≥ 10 copie in tutto**. Si fa **solo se l'idea 1 è passata**: stesse foto, segnale gratis.

### 2.4 STRUMENTO (non canale): Gumroad come merchant of record

- Pagina prezzi ufficiale, letta il 10/10/2026: «**Since January 1, 2025, Gumroad handles ALL your tax obligations** … We're a Merchant of Record». Commissione **10 % + 0,50 $**, oppure **30 %** sulle vendite che arrivano dal suo marketplace Discover ([gumroad.com/pricing](https://gumroad.com/pricing)).
- **A cosa serve:** quando arriverà la risposta fiscale, si possono vendere dai siti già online (Italy Strikes, EsameB1) un "Pro feed", un PDF o un pacchetto di avvisi **senza aprire posizioni IVA all'estero**. Lo studio 13 indicava Lemon Squeezy o Paddle: Gumroad è un'alternativa con le stesse caratteristiche.
- **Cosa non fa:** non porta clienti (nessun dato di vendite per i nuovi su Discover) e **non toglie il cancello fiscale**, perché il reddito resta di Massimiliano. Costo zero, nessuna azione ora.

### 2.5 Da fare in 5 minuti, senza aspettative: lista d'interesse Canva Creators

Canva paga i creatori da un fondo mensile, in base a quante volte i loro contenuti vengono usati, anche dagli utenti gratuiti; l'entità del fondo è riservata ([Canva help](https://www.canva.com/help/canva-creators-program/)). **Il venditore è Canva.** Oggi però **le iscrizioni per foto ed elementi sono sospese** («The Element Creators application is currently paused», pagina [canva.com/creators](https://www.canva.com/creators/)); i template passano da una candidatura "in beta" con mesi di attesa. Azione possibile: registrarsi alla lista d'interesse, per caricare un giorno le stesse foto anche su Canva. Nessuna stima. Nota: il connettore Canva di questa sessione non è autorizzato.

---

## 3. Gli scartati, con la prova principale

- **Hugging Face / Kaggle:** non pagano chi pubblica dataset. Kaggle paga solo premi di gara, che sono lavoro e non rendita. Nessun programma trovato.
- **AWS Data Exchange:** un privato residente nell'UE è ammesso, ma servono un account AWS (con carta), l'apertura di una pratica al supporto, costi di archiviazione e commissioni a scaglioni. I compratori sono grandi aziende che cercano fornitori noti ([guida AWS](https://docs.aws.amazon.com/data-exchange/latest/userguide/provider-getting-started.html); [prezzi](https://aws.amazon.com/data-exchange/pricing/)). **Venditore: lui.**
- **Datarade:** piano gratis con **30 %** di commissione, 3 schede e 3 richieste di contatto; i contratti si negoziano fuori piattaforma. È vendita B2B, cioè lavoro commerciale ([providers.datarade.ai](https://providers.datarade.ai/apply)).
- **Snowflake Marketplace:** per vendere serve un account **"full (non-trial)"**, cioè a pagamento ([docs Snowflake](https://docs.snowflake.com/collaboration/provider-becoming)).
- **RapidAPI, Chrome, Notion, GitHub, Zapier/Make:** nessuna prova nuova rispetto allo studio 7 (sez. 2.5).
- **Figma:** «We are not approving new creators to sell paid files on Community at this time» ([help.figma.com](https://help.figma.com/hc/en-us/articles/12067637274519), riletta il 10/10/2026).
- **Envato:** da marzo 2026 non accetta nuove candidature ([payhip](https://payhip.com/blog/envato-alternatives/)); dal 1/7/2026 la quota è il 50 % per tutti e i forum sono chiusi dal 15/8 ([ChargePanda](https://www.chargepanda.com/blog/post/envato-july-2026-changes-wordpress-authors-guide)). Fonti secondarie concordi, l'annuncio ufficiale ora dà 404.
- **Creative Market:** trattiene il 50 % e vuole una candidatura con portfolio; vende design, dove l'offerta generata dall'IA è enorme e serve gusto umano verificato ([Freemius](https://freemius.com/blog/creative-market-marketplace-breakdown/)).
- **Framer / Webflow:** Framer non trattiene commissioni ([framer.com/creators](https://framer.com/creators)), ma i template si costruiscono a mano nell'editor visuale e passano una revisione: non è un lavoro che Claude fa in automatico.
- **GPT Store / app ChatGPT:** il programma di ricavi annunciato nel 2024 (solo USA) non risulta operativo. La documentazione OpenAI di oggi dice che chi sviluppa sceglie come monetizzare con un «external checkout» sul proprio sito, e che «current approval is limited to plugins for physical goods purchases» ([developers.openai.com](https://developers.openai.com/apps-sdk/build/monetization)). **Venditore: lo sviluppatore.**
- **App Google Play:** 25 $ di iscrizione; un account personale nuovo deve fare un test chiuso con **12 tester per 14 giorni** prima di pubblicare ([testerscommunity](https://www.testerscommunity.com/blog/google-play-closed-testing-requirements-2026)). Lo studio 13 aveva trovato che l'app leader sugli scioperi aveva 1.000 download in 16 mesi. RevenueCat 2026: 15.000 nuove app in abbonamento al mese, quartile più basso a −33 % ([9to5mac](https://9to5mac.com/?p=1042212)). **Apple:** 99 $ l'anno, cioè un costo fisso prima degli incassi.
- **Microsoft Store:** iscrizione gratis per i privati dal 2025 ([blog Windows, 10/9/2025](https://blogs.windows.com/windowsdeveloper/2025/09/10/free-developer-registration-for-individual-developers-on-microsoft-store/)), ma nessuno paga una PWA di servizio e il traffico è minimo. Al massimo è una vetrina in più per Italy Strikes, non un ricavo.
- **Amazon Merch on Demand:** su invito. Dal 1/6/2026 la royalty è **dimezzata** per chi vende col solo traffico Amazon: maglietta da 19,99 $ da 4,88 a 2,44 $; si sale solo con ≥ 15 % di vendite da pubblicità o social ([Merch Titans](https://merchtitans.com/blog/amazon-merch-royalty-changes-june-2026); fonti secondarie concordi).
- **Redbubble / TeePublic:** il gruppo Articore ha ricavi FY26 a 408,5 M A$, in calo di 30 M, e ha migliorato il conto anche con commissioni sugli account degli artisti ([ragtrader](https://www.ragtrader.com.au/news/profits-go-green-for-redbubble-parent-articore)).
- **Grafica vettoriale generata da Claude su Adobe:** metà della libreria Adobe è già IA ([cined](https://www.cined.com/ai-flood-on-adobe-stock-nearly-half-of-all-images-now-ai-generated/)). Nel sondaggio Microstock Life tra chi carica IA, il **14 % non ha mai guadagnato** e il **63 % guadagna da 1 a 100 $ al mese** ([newsletter](https://microstocklife.beehiiv.com/p/much-money-people-earning-ai), dati 2024). Al massimo 20 file di prova dentro l'idea 1, etichettati come IA.
- **Newsletter con sponsor:** la rete pubblicitaria beehiiv richiede un piano a pagamento; le Boosts via email sono chiuse dal 10/4/2026 ([beehiiv](https://www.beehiiv.com/support/article/29786467662871)); gli sponsor diretti vanno cercati con contatti a freddo, che sono vietati. La lista email resta dentro i siti (strategia, sez. 3.4).
- **YouTube senza volto:** per i ricavi pubblicitari servono 1.000 iscritti e 4.000 ore di visione (o 10 milioni di visualizzazioni Shorts in 90 giorni). La regola "inauthentic content" del 15/7/2025 colpisce i video in serie fatti con modelli ([ppc.land](https://ppc.land/youtube-clarifies-inauthentic-content-policy-changes/)). Soprattutto, **i video caricati via API da progetti non verificati restano privati** finché Google non fa un audit ([docs YouTube API](https://developers.google.cn/youtube/v3/docs/videos?hl=en)): l'automazione completa non è possibile a costo zero.
- **Podcast:** lo Spotify Partner Program **non è disponibile in Italia** e chiede 2.000 ore di ascolto in 30 giorni ([Spotify](https://support.spotify.com/ie/creators/article/spotify-partner-program/)).
- **Medium:** l'Italia è ammessa, ma «AI-generated writing … is not allowed to be paywalled as part of our Partner Program» ([help.medium.com](https://help.medium.com/hc/en-us/articles/31090080813591)). Un canale scritto da Claude non è onestamente ammissibile.

---

## 4. Cosa cambia per la strategia (proposta, decide Massimiliano)

1. **Se dice sì allo stock (facoltativo):** test di 200 foto, 20 minuti di iscrizione e 5 minuti a settimana. È l'unico ricavo nuovo che probabilmente **non apre il cancello fiscale**. Va aggiunta una riga alla domanda per il professionista (sez. 2.1).
2. **Apify:** resta com'era nello studio 7 (3 Actor, test passivo); i dati nuovi dicono di **non allargarlo**.
3. **Gumroad (MoR):** si annota come strumento per vendere dai siti esistenti dopo la risposta fiscale. Nessuna azione ora.
4. **Calvendo e Canva:** solo dopo l'esito dello stock (Calvendo) o alla riapertura delle iscrizioni (Canva).
5. **Somma prudente di questo angolo a 18 mesi: 250-1.500 €/anno.** È un'aggiunta piccola alla strategia dei siti, non un'alternativa. Nessuna delle idee arriva da sola a 3.000 €/anno.

## 5. Limiti dichiarati

- Nessuna agenzia stock, né Apify, né Calvendo, né Canva pubblica i guadagni dei singoli. I numeri per immagine vengono da **un solo fotografo professionista** con 12 anni di archivio: per un portafoglio nuovo ho preso un minimo pari a un terzo dei suoi valori.
- Le pagine di Adobe, Canva e Alamy sono bloccate dal server (403 o DNS): i testi vengono dai risultati di ricerca che le citano.
- Le notizie su Envato e Amazon Merch vengono da fonti secondarie concordi; gli annunci ufficiali non sono raggiungibili.
- Le royalty di Calvendo (tabelle) e le condizioni di Wirestock non sono pubbliche.
- Non conosco quante foto dell'archivio di Massimiliano siano utilizzabili (senza persone riconoscibili): il test da 200 foto serve anche a misurarlo.
