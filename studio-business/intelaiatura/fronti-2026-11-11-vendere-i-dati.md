# Fronte (a) del mercoledì 11/11/2026: si possono VENDERE i nostri dati?

Domanda: i dati che la rete raccoglie da sola (registro scioperi, passi alpini, bagagli a mano di 28 compagnie, liquidi in 100+ aeroporti, rifiuti dei visti, validità del passaporto, servizi "available in", aste con sconto sull'OMI, voti CDC delle navi, eSIM) possono rendere **oltre** le visite alle pagine? Quattro strade controllate: (1) API e feed a pagamento, (2) compratori aziendali, (3) app e connettori per gli assistenti, (4) avvisi e newsletter con livello a pagamento.

Tutto letto l'11/11/2026 con curl dal server, salvo dove scrivo "ricerca web" (titoli e riassunti dei risultati, usati solo per trovare gli indirizzi). Cambio usato: 1 $ = 0,90 €. Non ripeto gli studi 7, 13, 15 e `fronti-2026-11-04-assistenti-ai.md`: aggiungo solo prove nuove.

## 0. Risposta in breve

**No come fronte grande: nessuna strada passa le 4 prove e nessuna arriva a 1.000 € l'anno centrali.** I numeri letti oggi dicono tre cose.

1. **Chi vende dati uguali ai nostri oggi ha 0-2 clienti.** Un'API dei requisiti di visto con prezzo da 5,50 €/mese mostra in pagina **2 abbonati e 79 chiamate in 7 giorni** (Oanor). Sul negozio Apify i tre Actor di regole di visto hanno **1 utente al mese ciascuno**, quello dei bagagli a mano **1**, il server MCP costruito sulla nostra stessa fonte (consigli di viaggio GOV.UK) **0 utenti negli ultimi 30 giorni**.
2. **Gli assistenti non lasciano vendere.** Le regole di OpenAI lette oggi: "Selling digital products or services—including subscriptions, digital content, tokens, or credits—is not allowed" e "Plugins must not serve advertisements". Un'app nostra dentro ChatGPT non può incassare né mostrare pubblicità.
3. **I compratori grandi comprano da venditori grandi, con una rete commerciale** (Sherpa, Timatic, Riskline): prezzi su preventivo, contratti annuali. Per noi servirebbero telefonate e contatti a freddo, che sono vietati dalle regole.

L'unico punto dove ho trovato **gente che paga adesso e un vuoto dimostrato** è piccolo: i dati delle **aste giudiziarie** su Apify. Nove Actor in vendita, i due migliori con 8 utenti al mese e 213-273 esecuzioni al mese, e **nessuno dei quattro letti confronta il prezzo con i valori OMI di zona**, che è proprio ciò che il nostro sito calcola già ogni sera.

| # | Idea | Chi paga | Voto severo | Prudente / centrale / ottimista (€/anno a 18 mesi) | Ore (agenti + Massimiliano) | 4 prove |
|---|---|---|---|---|---|---|
| 1 | Actor Apify "aste PVP con valore OMI di zona e sconto" (pagamento a risultato) | Utenti Apify (società immobiliari, sviluppatori); Apify incassa e trattiene il 20 % | **5** | 0 / 200 / 1.300 | 5-7 + 0,5 (account e verifica d'identità) | 3 su 4 (domanda debole) |
| 2 | Avviso gratuito "aste sotto la media OMI nel tuo comune", livello a pagamento solo sopra 300 iscritti | Lettori di Aste in Chiaro | **4** | 0 / 150 / 2.500 | 3-4 + 0 (ora); 6-8 + 1 per il pagamento, più avanti | 1 su 4 |
| 3 | API "regole di visto e passaporto" sui mercati di API (Oanor, Zyla, RapidAPI, Apify) | Sviluppatori di app di viaggio | **3** | 0 / 30 / 400 | 8-12 + 0,5 | 1 su 4 |
| 4 | App in ChatGPT o server MCP con i nostri dati | Nessuno (vendita e pubblicità vietate) | **2** | 0 / 0 / 100 | 15-25 + 1 | 0 su 4 |

Fuori classifica perché già decise e non cambiate dalle prove di oggi: feed scioperi per aziende (studio 13, in attesa: soglia non raggiunta, Italy Strikes 5 visite nella settimana 4-10/11) e vendita a TMC, assicurazioni, logistica (voto 2, sezione 3).

**Cosa propongo:** l'idea 1 entra nella coda **in basso** (circa 30 € per ora di lavoro, contro le sezioni nuove dei siti che crescono), come unico test di vendita dei dati; l'idea 2 solo nella sua parte gratuita (modulo "avvisami" sulle pagine città), perché costa 3 ore e misura la domanda che l'autocomplete non mostra. Le idee 3 e 4 non si costruiscono.

---

## 1. API e feed a pagamento: cosa c'è in vendita e quanti comprano

### 1.1 Cosa si è potuto leggere

| Mercato | Letto? | Nota |
|---|---|---|
| Apify Store (`api.apify.com/v2/store`) | **Sì**, API pubblica con utenti e esecuzioni per Actor | Unico mercato che pubblica i numeri veri |
| Oanor (`oanor.com/api/visa-api`) | **Sì**, la pagina mostra abbonati e chiamate | |
| Interline (`interline-web.pages.dev/pricing`) | **Sì**, solo prezzi | |
| RapidAPI (`rapidapi.com/search/...` e pagine delle API) | **No**: 200 ma pagina vuota senza JavaScript; il contatore degli abbonati non è pubblico nemmeno nel browser (solo un indice di "popolarità"). L'interrogazione diretta al loro motore interno non è stata fatta (sarebbe aggirare) | Proprietà di Nokia dal 2024 (nel codice della pagina: domini approvati `@nokia.com`) |
| Zyla (`zylalabs.com`) | **No**: 403 | Dalla ricerca web: almeno 4 schede "Visa Requirements" |
| Datarade (`datarade.ai`) | **No**: 403 | |
| AWS Data Exchange | Nessuna scheda trovata per regole di viaggio (ricerca web) | |
| Travel Buddy (`travel-buddy.ai/api`) | **No**: 403 | È il nome che Google suggerisce: "travel buddy visa requirements api" |
| APILayer (`apilayer.com/marketplace`) | 200, nessuna API di visti o scioperi in elenco | |

### 1.2 Domanda: cosa cerca chi compra (autocomplete Google, 11/11)

| Ricerca | Paese | Suggerimenti |
|---|---|---|
| travel requirements api | US | **9** |
| visa requirements api | US | **7** (due nominano Travel Buddy) |
| passport index api | US | 3 |
| visa mcp server | US | 3 (riguardano la carta Visa, non i visti) |
| italy strike alert | US | 3 (uno solo pertinente) |
| aste giudiziarie api | IT | 3 (due sono un Comune e una società) |
| app aste giudiziarie | IT | 4 |
| software aste immobiliari | IT | 1 |
| italy strikes api (GB), scioperi api (IT), strike data api (US, solo fulmini e borsa), airline baggage api (US) | | **0** |
| avviso nuove aste immobiliari, alert aste giudiziarie, aste giudiziarie telegram, aste immobiliari newsletter, aste immobiliari sotto prezzo di mercato, avviso scioperi email, calendario scioperi aziende | IT | **0** |

Solo le API dei visti hanno una domanda scritta. Per scioperi, bagagli e avvisi sulle aste la domanda in autocomplete è zero.

### 1.3 Prezzi e clienti letti

| Venditore | Cosa vende | Prezzo letto | Clienti letti |
|---|---|---|---|
| Oanor, Visa Requirements API (199 passaporti × 199 destinazioni) | API | gratis 25.000 chiamate/mese; Basic 5,50 €/mese (350.000 chiamate); Pro 17 €/mese | **"Subscribers 2 active", "Total calls 79 last 7 days"** |
| Interline | API compagnie, aeroporti, visti | gratis 100 richieste/giorno (visti inclusi); Pro 29 $/mese; Premium 99 $/mese | non pubblicati |
| Orizn Visa (letto su apispine.com, fonte secondaria) | API visti per agenzie | Starter 99 $/mese per 50 chiamate | non pubblicati |
| Apify `s-r/travel-rules` (visti da avvisi ufficiali) | Actor | 0,005 $ a ricerca | 1 utente in 30 giorni, 31 esecuzioni |
| Apify `siteverdict/…visa-entry-requirements` ("from official government sources (GOV.UK FCDO…)") | Actor | 0,01 $ a controllo | 1 utente, 27 esecuzioni |
| Apify `expected_diet/visa-checker-by-nationality` | Actor | 0,001 $ a riga | 1 utente in 30 giorni (87 in tutto da gennaio) |
| Apify `messnomore/airline-baggage-allowance` (bagaglio a mano, misure e peso dai siti delle compagnie, avviso di cambio) | Actor | 0,02 $ a risultato, 0,05 $ ad avviso | **1 utente**, 32 esecuzioni |
| Apify `nexgenwatch/official-travel-advice-mcp` (GOV.UK Content API, la nostra stessa fonte) | server MCP | 0,05 $ a chiamata | **0 utenti in 30 e 90 giorni**, 19 esecuzioni in tutto |
| Apify `nexgendata/travel-mcp-server` (Airbnb, hotel, TripAdvisor: non dati ufficiali) | server MCP | 0,05 $ a chiamata | 17 utenti, 2.959 esecuzioni in 30 giorni |
| Apify, 9 Actor di aste giudiziarie italiane | Actor | 0,001-0,015 $ a lotto, 0-0,10 $ ad avvio | i due migliori **8 utenti** ciascuno in 30 giorni; gli altri 0-3 |
| Dato gratuito concorrente: `ilyankou/passport-index-dataset` su GitHub (199 Paesi, CSV) | file | 0 | |

Lettura: i dati di viaggio "regola per Paese" sono già in vendita da molti a prezzi vicini a zero e **quasi nessuno li compra**. Il motivo è lo stesso scritto il 4/11: sono dati ufficiali con licenza aperta, chi li vuole li prende gratis. Gli scioperi non hanno nemmeno un venditore su questi mercati (ricerca "strike" su Apify: 817 risultati, nessuno sugli scioperi dei trasporti) e nessuna domanda in autocomplete.

---

## 2. Idea 1 (voto 5): Actor Apify "aste PVP con valore OMI di zona"

**Fonte esterna da cui nasce:** le statistiche pubbliche del negozio Apify lette oggi (ricerca "aste giudiziarie": 9 Actor).

### 2.1 Chi vende oggi e quanto si muove

| Actor | Fonte | Prezzo | Utenti 30 gg / 90 gg | Esecuzioni 30 gg / totali | In vendita dal |
|---|---|---|---|---|---|
| `promptica/aste-giudiziarie-pvp` | PVP | 0,05 $ ad avvio + 0,005 $ a lotto | 8 / 16 | 273 / 1.428 | 12/10/2026 (prezzo attuale) |
| `webdata_labs/italy-pvp-auctions-api` | PVP | 0,002 $ a lotto | 8 / 11 | 213 / 506 | 19/7/2026 |
| `ayrtondavoli97/italy-judicial-real-estate-auctions-astegiudiziarie-it` | astegiudiziarie.it | 0,10 $ ad avvio + 0,001 $ a lotto | 3 / 6 | 87 / 940 | 30/6/2026 |
| `studio-amba/astegiudiziarie-scraper` | astegiudiziarie.it | 0,012 $ a lotto | 1 / 2 | 42 / 238 | 31/7/2026 |
| `promptica/aste-giudiziarie-pro` | PVP + perizie | 0,10 $ ad avvio + 0,015 $ a lotto + 0,02 $ a perizia | 1 / 1 | 18 / 42 | 24/10/2026 |
| `ayrtondavoli97/Aste-objects-scraper` | 4 portali (beni mobili e immobili) | 0,0008 $ a lotto | 1 / 1 | 29 / 212 | 8/5/2026 |
| altri 3 | astegiudiziarie.it, asteannunci.it | 0,001-0,004 $ | 0-1 | 3-29 | giugno-novembre 2026 |

Fatti utili: il mercato è nato da 6 mesi (primo Actor a maggio 2026, cinque su nove da luglio in poi) e i due Actor sul PVP hanno superato in fretta quelli più vecchi. Uno dei nove (`realestateapi/…`) scrive nella sua scheda che le condizioni d'uso di astegiudiziarie.it "prohibit automated mass retrieval": chi legge il PVP, come noi, non ha quel problema.

### 2.2 Verifica dei concorrenti (obbligo del 10/11): cosa manca a loro

Ho letto le schede complete (`apify.com/<autore>/<actor>.md`) dei 4 concorrenti più probabili e ho cercato 5 cose concrete che un investitore chiede e che il nostro file `aste/dati/lotti.json` contiene già (3.295 lotti; esempio letto: lotto 4650547, Acireale, base 340.000 €, minima 272.000 €, zona OMI B1, abitazioni civili 940-1.400 €/m²).

| Cosa chiede l'investitore | promptica PVP | webdata_labs PVP | promptica Pro | ayrtondavoli97 oggetti | Noi (già nei dati) |
|---|---|---|---|---|---|
| 1. Valore OMI di zona (€/m² minimo e massimo, zona, semestre) | no (0 occorrenze di "OMI" e di "zona") | no | no (solo "catasto… checked against the Agenzia delle Entrate map") | no | **sì** |
| 2. Sconto sul **mercato della zona** (non sulla stima del perito) | no | "derived discount %" = base contro offerta minima | sconto sul valore di stima della perizia | "market discount" su fonte non dichiarata | **sì** |
| 3. Superficie in m² | dalla perizia, "quando il PDF è leggibile" | no | dalla perizia | no | sì, dal testo (con i limiti scritti nelle note) |
| 4. Stato di occupazione | sì (perizia) | sì | sì | no | sì |
| 5. Solo case vere (esclusi box, cantine, quote, date impossibili) | no | no | no | no | **sì** (regole di pulizia del 15/10) |

**Vuoto dimostrato:** nessuno dà il confronto con i valori OMI di zona (righe 1 e 2) e nessuno pulisce l'elenco (riga 5). **Dove sono più forti loro:** la perizia letta dal PDF (valore di stima, metratura) e il monitor delle novità; noi non leggiamo le perizie.

### 2.3 Stima (assunzioni scritte)

- Incasso del primo in classifica: 273 esecuzioni al mese × 0,05 $ = 13,65 $ certi, più i lotti. Con 100 lotti a esecuzione (ipotesi mia, il dato non è pubblico): 273 × 100 × 0,005 = 136 $. Quindi **il leader incassa tra 14 e 150 $ lordi al mese**; Apify trattiene il 20 % e i costi di calcolo.
- **Prudente 0 €**: lo studio 15 ha misurato una mediana di 1 utente per Actor; saremmo il decimo Actor della nicchia.
- **Centrale 200 €/anno**: 3 utenti, 60 esecuzioni al mese, 100 lotti a 0,004 $ + 0,05 $ ad avvio = 27 $ lordi al mese, meno 20 % = 21,6 $, circa 19 € al mese.
- **Ottimista 1.300 €/anno**: raggiungere la fascia alta del leader (150 $ lordi al mese).
- Ore: 5-7 degli agenti (l'Actor non rilegge il PVP: serve i dati già calcolati ogni sera, quindi costo di calcolo vicino a zero), 30 minuti di Massimiliano (account e, al primo pagamento, verifica d'identità: "To become a Verified Creator and receive a payout, you must successfully complete identity verification and the Know Your Customer (KYC) process").
- Rendimento: 200 € ÷ 6 ore ≈ **33 € per ora**, in fondo alla coda.

### 2.4 Rischi e vincoli

- **Fiscale:** il venditore è Massimiliano (studio 7 e 15: Apify emette le fatture a suo nome). È una vendita diretta di servizi: vale il cancello fiscale già scritto (consulenza gratuita prima di incassare il primo pagamento). I saldi restano 12 mesi senza verifica.
- **Licenza:** vedi sezione 6. OMI è CC BY 4.0 (rivendita ammessa con attribuzione). Il PVP non pubblica una licenza di riuso (la pagina delle note legali risponde 404): è il punto debole, uguale per tutti e nove i concorrenti. Nessun dato personale (già escluso dai nostri file).
- **Decisione precedente:** lo studio 15 diceva "Apify resta un test passivo, non allargarlo". I tre Actor di prova non risultano pubblicati (nessuna riga nel cruscotto). Questa idea non lo allarga: lo sostituisce con l'unico Actor che ha compratori contati e un vuoto letto.

### 2.5 Le 4 prove

| Prova | Esito |
|---|---|
| Domanda | **Debole**: 16 utenti al mese sommando i due leader, "aste giudiziarie api" 1 suggerimento pertinente |
| Dati leggibili | Sì: sono già nel repository, aggiornati ogni sera |
| Pagatore attivo | Sì: Apify paga i creatori, i concorrenti hanno utenti paganti a risultato |
| Nessuno fa già meglio | Sì sul confronto OMI; no sulle perizie |

Tre su quattro: non è un sito nuovo e costa zero, quindi può entrare in coda, ma **non è un'idea da 8 e non va al verificatore**.

---

## 3. Compratori aziendali: chi vende oggi dati come i nostri

| Compratore | Chi gli vende oggi | Prezzo letto | Perché non noi |
|---|---|---|---|
| Compagnie aeree, agenzie online | **Sherpa** (`joinsherpa.com`, 200) | Nessun listino: "Speak to us". Il modello non è vendere il dato: è la **vendita dei visti elettronici** dentro la prenotazione ("$6.80 per passenger", "40% conversion" nella pagina enterprise). Il dato sulle regole è il gancio gratuito | Serve un accordo commerciale e l'integrazione nel flusso di prenotazione |
| Compagnie aeree (controllo documenti all'imbarco) | **Timatic** (IATA) | Non pubblico | Standard di settore con responsabilità legale sul dato |
| Viaggi d'affari (TMC, TravelPerk, TripIt Pro) | **Riskline**, International SOS, Crisis24 | Studio 13: 10-50 mila $ l'anno con contratto; pagina prezzi di Riskline oggi 404 | Coprono già l'Italia; contratto e assistenza 24 ore |
| Feed di eventi di rischio | RSOE EDIS (ricerca web) | 4.000 € l'anno per l'API | Disastri, non scioperi; prezzo di riferimento per un feed serio |
| Siti di viaggio piccoli | **VisaDB** (`visadb.io/api`, 200) | Widget di visti e sicurezza "Completely free unless branded" | Il concorrente regala il widget in cambio del marchio |
| Assicurazioni (copertura sciopero), logistica italiana | Nessun venditore di dati sugli scioperi trovato; nessuna domanda in autocomplete | – | Vendita con trattativa: telefonate e contatti a freddo, vietati dalle regole; il dato è gratuito alla fonte (MIT, CGSSE, onData) |
| Società di relocation (rifiuti dei visti) | Nessuno: file gratuiti della Commissione europea e dell'Home Office | 0 | Chi lavora nel settore scarica il file |

Voto 2. Stima 0 / 0 / 500 €/anno: l'unico caso positivo sarebbe una richiesta che arriva da sola dal modulo "For businesses" di Italy Strikes, già online; la soglia dello studio 13 (3 richieste vere in 90 giorni o 1.000 visite al mese) resta valida e non è raggiunta.

---

## 4. Idea 4 (voto 2): app e connettori per gli assistenti

Regole lette oggi sui documenti ufficiali (`developers.openai.com/apps-sdk/app-submission-guidelines.md` e `…/build/monetization.md`, entrambi 200):

- "Currently, plugins may conduct commerce only for physical goods. Selling digital products or services—including subscriptions, digital content, tokens, or credits—is not allowed, whether offered directly or indirectly (for example, through freemium upsells)."
- "Plugins must not display subscription plans, initiate new subscriptions, or promote upgrades."
- "Plugins must not serve advertisements and must not exist primarily as an advertising vehicle."
- "Do not advertise pricing, subscriptions, free trials, discounts, or promotions."
- Pagamento dentro la conversazione: "limited to select marketplaces today" (beta privata).
- Forum degli sviluppatori (30/1/2026): "You cannot submit an app with monetization for any digital products/services."

Quindi oggi un'app nostra non può vendere, non può mostrare pubblicità e non può nascere come veicolo per link affiliati. Resta solo la visibilità, che abbiamo già gratis: ChatGPT porta il 17 % delle visite citando le pagine.

Server MCP a pagamento:

- Registro ufficiale (`registry.modelcontextprotocol.io/v0/servers?search=…`, 200): **56 voci per "visa"** (tra cui `com.canienter/visa-check`), **100 o più per "travel"** (il tetto della risposta), 40 per "auction" (nessuna italiana tra le prime). L'elenco è gratuito e non paga nessuno.
- L'unico canale che paga a chiamata è Apify (20 % di commissione). I numeri della sezione 1.3: il server sui consigli di viaggio ufficiali ha 0 utenti in 90 giorni; quello che guadagna vende ricerche di alloggi, non dati ufficiali.
- Ricerca web (blog, da prendere con cautela): 17.000 server indicizzati, 3-6 % con un prezzo, "oltre il 95 % a ricavo zero"; un autore racconta una prima commissione di 0,21 $.

Stima 0 / 0 / 100 €/anno, 15-25 ore, un server sempre acceso. **Non si costruisce.** Innesco per riaprire: OpenAI apre la vendita di beni digitali o un programma di ricavi per le app (ricontrollo a febbraio 2027, insieme alla riga del 4/11).

---

## 5. Avvisi e newsletter a pagamento

### 5.1 Idea 2 (voto 4): avviso "aste sotto la media OMI nel tuo comune"

**Fonte esterna:** l'esistenza di 9 Actor a pagamento sulle aste (sezione 2) dice che qualcuno paga per sapere prima; "app aste giudiziarie" ha 4 suggerimenti.

Cosa ho letto dei concorrenti:

| Concorrente | Letto? | Cosa offre |
|---|---|---|
| astegiudiziarie.it (Aste Giudiziarie Inlinea S.p.A.) | 200 | Newsletter gratuita con guida ("Ricevi subito GRATIS la guida alle aste!"), area riservata per professionisti; nessun prezzo per chi compra; la ricerca è in JavaScript, non leggibile per comune |
| Portale delle Vendite Pubbliche | 200 | Elenco ufficiale gratuito; nessun confronto con il mercato |
| immobiliare.it aste, Wikicasa Auction, asteannunci.it, astalegale.net, immobiliallasta.it | **403 o errore** | Non leggibili dal server: non so se hanno avvisi con lo sconto sul mercato |
| Newsletter o canali a pagamento sulle aste | Due ricerche web | **Nessuno trovato** con un prezzo |

Il vuoto **non è dimostrato**: cinque concorrenti su sette non si leggono, quindi non posso scrivere i 5 esempi per comune. Per la regola del 10/11 il voto non può superare 5. E "nessuno vende avvisi a pagamento" qui vale come segnale di domanda assente, non come occasione: tutte e cinque le ricerche sugli avvisi d'asta hanno 0 suggerimenti, e Milano Finanza scrive (ricerca web, giugno 2026) che il 65 % degli aggiudicatari sono famiglie, che comprano una volta sola.

Stima a 18 mesi: Aste in Chiaro ha 22 visite a settimana. Se cresce di 10 volte (11.000 visite l'anno), 2 % di iscritti = 230, 3 % paganti a 39 €/anno = 7 persone = **circa 270 € lordi, 150 € centrali** dopo commissioni. Prudente 0. Ottimista 2.500 € (2.000 iscritti, 3 % a 49 €). Per incassare servono un servizio di pagamento e l'invio delle email, e vale il cancello fiscale.

**Cosa si fa a costo zero:** solo il modulo gratuito "avvisami per questo comune" sulle 188 pagine città (3-4 ore, stesso modulo Netlify di Italy Strikes). Serve a contare la domanda. Soglia scritta prima: **300 iscritti** per fare un sondaggio sul prezzo; sotto, resta una leva per far tornare i lettori.

### 5.2 Avvisi sugli scioperi a pagamento

Nessuna prova nuova contro lo studio 13 (app a pagamento con 500 download e zero valutazioni; TripIt Pro 48,99 $/anno riceve gli avvisi da Riskline). Oggi: "italy strike alert" 3 suggerimenti di cui 1 pertinente, "avviso scioperi email" e "calendario scioperi aziende" 0, Italy Strikes 5 visite a settimana. Resta in attesa con le soglie già scritte (500 iscritti per il sondaggio, 5.000 per vendere).

---

## 6. Licenze delle fonti: cosa si può rivendere

| Dato | Fonte | Licenza letta | Rivendita come feed |
|---|---|---|---|
| Scioperi dei trasporti | MIT, dataset "Scioperi dei trasporti" su dati.gov.it (letto oggi dall'API del catalogo, aggiornato l'8/1/2026) | **CC-BY-4.0** | Sì, citando il Ministero |
| Scioperi (riserva) | CGSSE nella copia di onData | CC BY 4.0 | Sì, citando entrambi |
| Voti delle navi | CDC Vessel Sanitation Program (`cdc.gov/other/agencymaterials.html`, 200) | "not subject to copyright, is in the public domain"; obbligo: "Attribution to the agency…" e nessuna apparenza di approvazione del CDC | Sì |
| Rifiuti Schengen | Commissione europea (`commission.europa.eu/legal-notice_en`, 200) | "licensed under the Creative Commons Attribution 4.0" | Sì |
| Rifiuti e regole del Regno Unito | Home Office, FCDO (GOV.UK) | OGL v3 (note del sito) | Sì |
| Regole per passaporto canadese e australiano | Global Affairs Canada; Smartraveller | OGL Canada 2.0; Creative Commons Attribution (note del 17/10) | Sì |
| Valori immobiliari | Agenzia delle Entrate, OMI | CC BY 4.0 | Sì |
| Aste | Portale delle Vendite Pubbliche | **Nessuna licenza pubblicata** (note legali 404). Avvisi pubblici per legge; dati personali da escludere sempre | Zona grigia: solo dati di fatto del lotto con link alla scheda, come fanno i 9 concorrenti |
| Misure dei bagagli, liquidi per aeroporto | Siti di compagnie e aeroporti | Nessuna licenza: fatti citati con la fonte | Sulle pagine sì; come banca dati in vendita **no** (condizioni d'uso dei siti, diritto sulle banche dati) |
| Servizi per Paese (Spotify, Apple, Wise, Starlink…) | Liste dei fornitori | Condizioni dei fornitori | Come sopra: **no** |
| Schede per cittadini italiani | Ministero degli Esteri | Licenza ristretta (nel repository teniamo solo fatti e impronte) | **No** |
| Passi alpini | Enti stradali di più Paesi (in prova) | Da leggere fonte per fonte | Non valutabile oggi |

Conclusione: i dati che potremmo rivendere senza rischi (scioperi, CDC, Schengen, GOV.UK, OMI) sono proprio quelli che chiunque scarica gratis; quelli più difficili da raccogliere (bagagli, liquidi, servizi per Paese) non hanno una licenza che permetta di venderli come banca dati.

---

## 7. Perché il verdetto è severo, e cosa lo cambierebbe

- Il valore dei nostri dati è nella pagina che risponde a una persona, non nel file: lo provano i 2 abbonati di Oanor e gli Actor con 1 utente.
- I soldi veri del settore (Sherpa: 6,80 $ a passeggero) vengono dalla **vendita del visto**, non dal dato. La strada equivalente per noi è già aperta ed è l'affiliazione sulle pagine (assicurazione Schengen, eSIM, visti elettronici), non la licenza.
- Inneschi per riaprire: (a) una richiesta vera dal modulo "For businesses"; (b) l'Actor delle aste oltre 10 utenti al mese per due mesi (allora si aggiungono le perizie e un secondo Actor); (c) 300 iscritti all'avviso gratuito delle aste; (d) OpenAI apre i pagamenti per i beni digitali.

## 8. Fonti lette (11/11/2026)

- Apify Store, API pubblica: `https://api.apify.com/v2/store?search=aste%20giudiziarie` (9), `…search=visa%20requirements` (880), `…search=baggage` (115), `…search=travel%20mcp` (119), `…search=strike` (817), `…search=cruise` (108); schede: `https://apify.com/promptica/aste-giudiziarie-pvp.md`, `https://apify.com/webdata_labs/italy-pvp-auctions-api.md`, `https://apify.com/promptica/aste-giudiziarie-pro.md`, `https://apify.com/ayrtondavoli97/Aste-objects-scraper.md`; condizioni: `https://docs.apify.com/legal/store-publishing-terms-and-conditions`
- Oanor: `https://oanor.com/api/visa-api` · Interline: `https://interline-web.pages.dev/pricing` · Orizn (fonte secondaria): `https://apispine.com/orizn-visa/pricing` · VisaDB: `https://visadb.io/api`
- Sherpa: `https://www.joinsherpa.com/pricing` e `https://www.joinsherpa.com/pricing/enterprise-pricing`
- OpenAI: `https://developers.openai.com/apps-sdk/app-submission-guidelines.md`, `https://developers.openai.com/apps-sdk/build/monetization.md`, `https://community.openai.com/t/chatgpt-app-monetization-apps-sdk/1372343`
- Registro MCP: `https://registry.modelcontextprotocol.io/v0/servers?search=visa` (anche travel, strike, auction)
- Licenze: `https://www.dati.gov.it/opendata/api/3/action/package_search?q=scioperi+trasporti`, `https://www.cdc.gov/other/agencymaterials.html`, `https://commission.europa.eu/legal-notice_en`
- Aste: `https://www.astegiudiziarie.it/` (200), `https://pvp.giustizia.it/pvp/` (200)
- Non leggibili (nessun tentativo di aggirare): rapidapi.com (pagine vuote senza JavaScript), zylalabs.com 403, datarade.ai 403, travel-buddy.ai 403, asteannunci.it 403, wikicasa.it 403, astalegale.net 403, immobiliare.it 403, immobiliallasta.it errore 530, riskline.com/pricing 404, developers.sherpa.ai senza risposta
- Ricerca web (solo per trovare indirizzi e per le voci marcate): stato della monetizzazione MCP (dev.to, signalcensus), RSOE EDIS 4.000 €/anno, quota delle famiglie tra gli aggiudicatari (milanofinanza.it, quotidiano.net)
