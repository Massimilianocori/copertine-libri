# Fronte nuovo: gli assistenti AI come canale di visite e di guadagno (4/11/2026)

Domande: (1) quali pagine e quali dati gli assistenti citano di più, con prove; (2) quali programmi esistono per gli editori; (3) cosa si può fare a costo zero sui siti che abbiamo; (4) se c'è un modo di farsi pagare dagli assistenti per i nostri dati. Per ognuna: numeri, stima e voto severo.

Letti prima: brief comune, skill `rete-siti`, `REGOLE-FISSE.md` (30/10 e 31/10), `STRATEGIA.md`, `ESPLORATE.md`, `ricerca-profonda-2026-10-28-assistenti.md`, `fronti-2026-10-31-traffico.md` (sez. 1-2 e i tre esperimenti), `idee-2026-10-26.md` (spunto 16: compensi dagli assistenti, già NO con voto 3), `esperimento-citazioni-2026-10-31.md` (Visa Income, in corso: **non ripetuto e non toccato**), `CRUSCOTTO-RETE.md` (voce del 4/11).

Cosa è nuovo rispetto al 31/10: i numeri veri di 18 giorni per sito e per pagina, le prove esterne del 2026 (studi con gruppo di controllo, non solo correlazioni), lo stato verificato oggi di 12 programmi che pagano gli editori, e le azioni a costo zero che restano fuori dall'esperimento.

Metodo: API di GoatCounter (`stats/total`, `stats/toprefs`, `stats/toprefs/chatgpt.com`, `stats/hits` con paginazione) dal 17/10 al 3/11/2026; `curl` dal server sulle pagine dei programmi (stato HTTP e testo letto); ricerca web per gli studi (i risultati sono come da un computer negli USA). ahrefs.com non si apre da questo server (rete non permessa): i suoi studi sono letti dai riassunti di altre testate, e lo scrivo. Brave Search risponde 429 con un captcha: **non l'ho aggirato**. Le stime sono stime e hanno il calcolo accanto.

---

## 0. In breve

- **Il canale c'è, ma è più piccolo di "un terzo".** Dal 17/10 al 3/11: 1.111 visite, **230 da chatgpt.com**: il **21 %** di tutte le visite, il **27 %** di quelle che arrivano da fuori (tolti i clic interni tra pagine dei nostri siti), quasi **metà di Google** (473). Ultimi 7 giorni: 140 su 726. Per settimana: 39 → 116 → circa 130. Perplexity, Copilot e Claude: **0**; Gemini 2, Bing 3. Nella media del web le visite dagli assistenti sono lo 0,3-1,1 % del totale: noi siamo 20-60 volte sopra, perché facciamo proprio le pagine che citano.
- **Cosa citano (prova nostra):** pagine con **un numero ufficiale come risposta in cima**, una pagina per ogni voce di una matrice (nazionalità, città, nave), su temi dove l'assistente **non sa rispondere a memoria**. Visa Income: 58 % delle visite da ChatGPT; Aste in Chiaro: 69 %. Tourist Tax ha la stessa forma (risposta in cima, tabelle) ma **0 visite da ChatGPT**: la forma aiuta, ma decide il buco.
- **Prove esterne:** i titoli uguali alla domanda contano (Ahrefs, 1,4 milioni di domande); il 44 % delle citazioni viene dal primo 30 % della pagina; i dati e le tabelle originali sono citati più delle guide; **aggiungere solo lo schema JSON-LD non sposta le citazioni** (prova di Ahrefs con gruppo di controllo, maggio 2026); `llms.txt` non serve a nulla.
- **Farsi pagare per i dati: no, non oggi e non per siti come i nostri.** Tutti i programmi che pagano (Perplexity, Microsoft, ProRata, RSL, TollBit, Cloudflare, Dappier) o sono riservati alle grandi testate, o non hanno ancora un compratore che paga, o chiedono di bloccare i robot (e spegnerebbero ChatGPT, cioè il 58 % delle visite di Visa Income). Voto **2**.
- **Il soldo vero è il clic**, monetizzato da noi (AdSense, affiliazioni) sulle pagine che gli assistenti citano. Valore del canale a 12 mesi: **50 / 300 / 1.700 €/anno** (prudente / centrale / ottimista). È un acceleratore delle sezioni, non un'attività a sé.
- **Nessuna idea da 8.** Le due migliori sono a costo zero e senza ore di Massimiliano oltre 10 minuti: Bing Webmaster Tools con il rapporto delle citazioni (proposto il 31/10, **non ancora fatto**) e la regola di scelta delle sezioni nuove "dove l'assistente non sa rispondere".

| # | Idea | Dove | Voto | €/anno 12 mesi (prud. / centr. / ott.) | Ore |
|---|---|---|---|---|---|
| 1 | Bing Webmaster Tools + rapporto "AI Performance" (citazioni in Copilot e Bing) | tutti i siti | **7** | indiretto (misura) + 0-100 | 1 + 10 min di Massimiliano |
| 2 | Regola per la coda: sezioni nuove solo dove l'assistente non sa rispondere a memoria (matrici di numeri ufficiali), misurata con la quota ChatGPT per sezione | coda di costruzione | **7** | è il canale stesso: 50 / 300 / 1.700 | 0 (criterio) |
| 3 | Offerta adatta sulle pagine che gli assistenti citano (sulle pagine rifiuti: assicurazione per il visto Schengen al posto di quella da nomadi; **solo dopo il 28/12**) | Visa Income, poi Aste | **6** | 20 / 120 / 500 | 1-2 |
| 4 | Rapporto settimanale "quota assistenti" per sezione e "pagine citate per la prima volta" | `studio-business/strumenti/` | **6** | indiretto | 1-2 |
| 5 | "Is [assistente] available in [Paese]?" nella sezione `available-in/` | Before You Fly | **4** | 10 / 60 / 250 | 3-4 |
| 6 | App dentro ChatGPT (Apps SDK) o server MCP con i nostri dati | nuovo | **3** | 0 | 15-25 |
| 7 | GPT personalizzato nel GPT Store | nuovo | **2** | 0 (serve un abbonamento: spesa) | 2 |
| 8 | Perplexity Publishers Program / Comet Plus (80 % ai partner) | programma | **2** | 0 | 10 min (email: sì di Massimiliano) |
| 9 | Microsoft Publisher Content Marketplace (Copilot paga per contenuti licenziati) | programma | **2** | 0 | 10 min (modulo) |
| 10 | RSL Collective (licenze collettive, gratuito) | programma | **2** | 0 | 30 min |
| 11 | ProRata / Gist (50 % dei ricavi delle risposte) | programma | **2** | 0 | – |
| 12 | Dappier (vendere le risposte a pagamento per domanda) | programma | **2** | 0-20 | 4-6 |
| 13 | Vendere i dataset (AWS Data Exchange, Snowflake, API a pagamento) | prodotto | **2** | 0-50 | 6-10 |
| 14 | TollBit (far pagare i robot) | programma | **1** | negativo | – |
| 15 | Cloudflare "pay per crawl" | programma | **1** | 0 | serve un dominio |
| – | `llms.txt`, solo schema JSON-LD in più, bloccare i robot di addestramento | – | 2 / 3 / 1 | 0 | – |

---

## 1. I numeri veri della rete (GoatCounter, 17/10-3/11/2026, letti oggi)

**Provenienze (`stats/toprefs`).** Google 473 · **chatgpt.com 230** · diretto 149 · clic interni tra le nostre pagine 256 · bing.com 3 · gemini.google.com 2 · Yandex 2 · altri 3. Nessuna visita da perplexity.ai, copilot.microsoft.com, claude.ai, duckduckgo.com.

**Per settimana (`stats/toprefs/chatgpt.com`).** 17-23/10: 39 · 24-30/10: 116 · 31/10-3/11 (4 giorni): 75, cioè circa 130 a settimana. La crescita rallenta (da ×3 a +15-20 %): le pagine citate sono quasi sempre le stesse.

**Per sito (visite totali e quota ChatGPT).**
| Sito | Visite | Da ChatGPT | Quota |
|---|---|---|---|
| EsameB1 | 626 | 56 | 9 % |
| Visa Income | 216 | 126 | **58 %** |
| Before You Fly | 152 | 12 | 8 % |
| Cruise Health Scores | 55 | 11 | 20 % |
| Aste in Chiaro | 35 | 24 | **69 %** |
| Tourist Tax | 26 | 0 | 0 % |
| Italy Strikes | 1 | 0 | 0 % |

**Pagine più citate (ChatGPT / visite totali).** Visa Income Pakistan 17/20; EsameB1 `esempi-esame-b1` 11/17 (oggi rimanda a `/esempi/`, 4/9); Iraq 7/8; Bangladesh 7/7; **Aste Roma 7/8**; Türkiye 6/6; Regno Unito 6/6; EsameB1 Milano 6/**76** (lì vince Google); Before You Fly Starlink 3/7. In tutto 115 pagine diverse hanno ricevuto almeno una visita da ChatGPT (su 308 pagine visitate).

**Cosa dicono questi numeri.**
1. **Le pagine citate hanno tutte la risposta in un numero in cima**, presa da una fonte ufficiale: "45,9 % not issued" (rifiuti), "153 case all'asta, prezzo base mediano 182.000 €, 63 su 64 sotto la media OMI" (Aste Roma), "86/100, maggio 2024" (navi), "173 Paesi Available" (Starlink).
2. **La forma non basta.** Le pagine di Tourist Tax hanno titolo con la cifra, la risposta nella prima frase e tabelle ("Menorca tourist tax 2026: €1-€4 per person per night"), ma 0 visite da ChatGPT su 26: la tassa di soggiorno la sanno già cento siti e l'assistente risponde da solo. Aste Roma invece ha 15.000 parole e nessuna `<table>`, ma un numero che nessun altro calcola: è citata.
3. **Le pagine con molte ricerche su Google prendono poco dagli assistenti** (EsameB1 Milano 6 su 76): il canale assistenti non sostituisce Google, copre le domande "di numero" che Google serve male.
4. **ChatGPT da solo fa tutto.** Gli altri assistenti insieme: 2 visite. Copilot si appoggia a Bing, che ci conosce poco (3 visite); Claude si appoggia a Brave Search; Perplexity ha un suo robot (permesso da noi). Niente lavoro separato possibile per ognuno, salvo Bing (sez. 4, idea 1).

**Accesso dei robot (provato oggi su 6 siti).** `robots.txt` = `Allow: /` per tutti; la home risponde 200 a OAI-SearchBot, ChatGPT-User, GPTBot, Claude-SearchBot, Claude-User, PerplexityBot, Perplexity-User e bingbot. **Niente da sistemare.**

---

## 2. Quali pagine e quali dati vengono citati: le prove

In ordine di solidità. La maggior parte degli studi sono di aziende che vendono strumenti di misura: li uso per la direzione, non per la cifra esatta.

| Prova | Cosa dice | Quanto fidarsi |
|---|---|---|
| **I nostri numeri** (sez. 1) | Citate: numero ufficiale in cima, una pagina per voce di una matrice, tema senza risposta a memoria. Non citate: temi già coperti da molti (tassa di soggiorno), notizie del giorno (scioperi) | alta per noi, campione piccolo (230 visite) |
| **Ahrefs, gruppo di controllo** (maggio 2026): 1.885 pagine che hanno aggiunto JSON-LD contro 4.000 di controllo | Citazioni in ChatGPT **+2,2 %**, in AI Mode +2,4 %: **non distinguibili da zero**. Le pagine citate hanno più spesso lo schema, ma aggiungerlo non le fa citare | alta (unico studio con controllo) |
| searchVIU (riassunto di terzi) | Quando l'assistente legge una pagina, prende **solo il testo visibile**: JSON-LD e microdati nascosti ignorati | media |
| **Ahrefs, 1,4 milioni di domande a ChatGPT** | ChatGPT cita circa **metà** delle pagine che legge. Somiglianza titolo-domanda: pagine citate 0,602, non citate 0,484; con le sotto-domande che l'assistente si fa da solo ("fan-out") 0,656. Le differenze di data e di estratto viste prima erano, dicono loro, distorte | media-alta |
| Kevin Indig, Growth Memo (18.012 citazioni verificate) | **44 %** delle citazioni dal primo 30 % della pagina, 31 % dal centro, 25 % dalla fine; il testo citato contiene il doppio delle volte un punto di domanda; il 78 % delle citazioni legate a domande viene dai titoli di sezione | media (articolo a pagamento, numeri dai riassunti) |
| Ahrefs, 17 milioni di citazioni (già nel file del 31/10) | Gli assistenti citano pagine più recenti dei risultati di Google; ChatGPT è il più sensibile alla freschezza | media-alta |
| Studio GEO (Princeton e altri, KDD 2024) | Statistiche, citazioni e fonti nel testo: visibilità +30-40 % nel loro banco di prova | media (non è ChatGPT vero) |
| Texta (50.247 domande commerciali), Search Engine Land (150.000 pagine) | Pagine con dati originali e tabelle citate di più (41 % contro 34 % delle guide; "dati e riepiloghi d'anno" 61 %, "come fare" 12 %) | bassa-media, cifre che non si confrontano |
| Promptwatch (luglio 2026) | Le schede prodotto sono un terzo delle citazioni di ChatGPT Search (erano il 18 % a marzo): la parte "acquisti" cresce | media, non riguarda noi |
| SE Ranking (~300.000 domini) e Ahrefs | `llms.txt`: nessuna differenza nelle citazioni | alta |
| Google, "AI features and your website" (pagina letta oggi, 200) | Per AI Overviews e AI Mode "non ci sono requisiti aggiuntivi… non servono file leggibili dalle macchine, file di testo per l'IA o markup" | ufficiale |
| OpenAI, pagina dei robot (letta oggi, 200) | Per comparire nelle risposte di ricerca va permesso **OAI-SearchBot**; GPTBot (addestramento) è indipendente | ufficiale |
| Seer Interactive (2024) contro Ahrefs (2025) | 87 % delle citazioni di ChatGPT coincide con i primi risultati di Bing; secondo Ahrefs la sovrapposizione è intorno al 10-26 %. Altri parlano di un indice proprio di OpenAI | contraddittorio |

**Conclusione pratica.**
- Il testo visibile conta, il markup nascosto quasi no. Se l'esperimento del 31/10 passa, il merito sarà probabilmente della riga "Updated on" e del riquadro "Key figures", non dello schema `Dataset` (da tenere a mente al verdetto del 28/12, senza cambiare nulla adesso).
- **Titolo uguale alla domanda e alle sue sotto-domande**: la sotto-pagina `pakistan/easiest-schengen-visa` riceve già 3 visite da ChatGPT su 7; le sotto-domande tipiche ("which Schengen country is easiest for Pakistanis", "family visa refusal rate UK") meritano pagine proprie, come già facciamo.
- **Risposta nel primo terzo**: tutte le nostre pagine di dati lo fanno già.
- **Scegliere il tema conta più della forma** (Tourist Tax contro Aste).

---

## 3. Programmi per editori: chi paga, chi può entrare (verificato il 4/11/2026)

| Programma | Cosa paga | Chi può entrare | Stato verificato | Per noi | Voto |
|---|---|---|---|---|---|
| **Perplexity Publishers Program / Comet Plus** | Abbonamento Comet Plus da 5 $ al mese: **80 % ai partner**, diviso per visite umane, citazioni e azioni degli agenti; fondo iniziale di 42,5 milioni $ | "Publishers interested in participating can join the program by emailing us via publishers@perplexity.ai" (pagina del 25/8/2025, letta oggi, 200). `perplexity.ai/publishers` 404. Partner nominati: Condé Nast, CNN, Washington Post, Le Monde, TIME, Der Spiegel | aperto via email, criteri non scritti | **0 visite da Perplexity in 18 giorni**: la nostra parte di un fondo diviso per citazioni e visite sarebbe di centesimi. L'email è un contatto: solo col sì di Massimiliano | **2** |
| **Microsoft Publisher Content Marketplace (PCM)** | Pagamento a consumo quando un contenuto licenziato serve una risposta di Copilot; l'editore fissa le condizioni | Annuncio del 3/2/2026 (letto oggi, 200): "will support publishers of all sizes… specialized and independent voices", ma pilota con AP, Condé Nast, Hearst, People Inc, USA TODAY, Vox; modulo d'interesse su Microsoft Forms | pilota, modulo pubblico | Cerca **contenuti premium** (spesso a pagamento); i nostri sono dati ufficiali gratuiti ripresi con licenza CC BY/OGL. E Bing ci conosce poco. Da riaprire solo se il rapporto AI Performance (idea 1) mostra citazioni in Copilot | **2** |
| **RSL Collective** (Really Simple Licensing) | Diritti raccolti dagli assistenti e girati ai membri (a citazione, a lettura, ad abbonamento) | Gratuito, non esclusivo; più di 50 partner (Vox, BuzzFeed, USA Today) | **nessuna azienda di IA ha ancora firmato** (settembre 2026); stanno cercando editori prima di trattare | Iscrizione gratuita ma oggi rende 0. Rischio: dichiarare licenze su contenuti che in parte sono dati CC BY/OGL di altri (si licenzia solo il nostro testo) | **2** |
| **ProRata / Gist** | 50 % dei ricavi (pubblicità e abbonamenti) delle risposte di gist.ai, diviso per uso dei contenuti | Accordi con circa 750 testate, spesso tramite associazioni | gist.ai 200, prorata.ai 200 (pagine in JavaScript) | FIPP 2026: "non sa indicare un solo editore che ne ricavi un reddito significativo". Pubblico di gist.ai piccolo | **2** |
| **TollBit** | Fa pagare i robot che leggono le pagine; gratuito per l'editore | Aperto ("Get started free"); clienti in pagina: CNN, Fast Company, PCMag, Ballotpedia | tollbit.com 200 | I robot che non pagano vengono bloccati o rimandati: **spegnerebbe ChatGPT**. E il rapporto clic/letture degli assistenti è basso (0,27 % a fine 2025, secondo TollBit) | **1** |
| **Cloudflare pay per crawl** | Prezzo per lettura fissato dall'editore | "Private beta", domanda con modulo (pagina 200) | richiede il sito su Cloudflare | Serve un **dominio nostro gestito da Cloudflare**: oggi siamo su `.netlify.app` e i domini si comprano solo dopo il verdetto (Massimiliano, 17/10) | **1** |
| **Dappier** | L'editore mette in vendita i suoi contenuti come "modello di dati" a prezzo per domanda | Aperto anche ai piccoli (2024); piano gratuito secondo terzi | dappier.com 200, marketplace 403 | Chi compra? Sviluppatori che possono prendere gli stessi dati gratis dalla Commissione o da Eurostat. Vendita diretta: rientra nel codice 58.19.00, ma il volume atteso è zero | **2** |
| Amazon (mercato per editori) | – | Notizia del Wall Street Journal, febbraio 2026: in costruzione | non aperto | – | – |
| Accordi OpenAI, Google, Amazon con le testate | Milioni l'anno | Solo grandi gruppi (News Corp, Axel Springer, AP…) | trattativa diretta | Fuori portata | **0** |
| **App in ChatGPT (Apps SDK) / server MCP** | Oggi niente: secondo il forum degli sviluppatori (gennaio 2026) non si possono pubblicare app con vendite di beni digitali; il pagamento dentro ChatGPT è solo per partner in prova | Directory aperta alle candidature, con verifica dello sviluppatore | developers.openai.com/apps-sdk 200 | Porterebbe visibilità, non soldi. Serve un server sempre acceso (le funzioni di Netlify consumano crediti, GitHub Pages non basta), l'account e l'identità di Massimiliano, la revisione di OpenAI | **3** |
| GPT personalizzato nel GPT Store | Programma di ricavi per i creatori annunciato nel 2024 solo per gli USA; stato 2026 non verificato | Serve un abbonamento a pagamento per crearlo | – | Spesa fissa, ricavo 0 | **2** |
| Mercati di dati (AWS Data Exchange, Snowflake, API a pagamento) | Vendita o abbonamento ai dataset | Aperti, con account e dati fiscali | – | Dati pubblici rielaborati: chi li vuole li scarica gratis dalla fonte. Utile solo il CSV gratuito con link (già nell'esperimento E3 del 31/10) | **2** |

**Risposta alla domanda "possiamo farci pagare per i nostri dati?": no, non nel 2026.** Tre ragioni con prove: (1) i programmi che pagano davvero (accordi diretti, PCM) cercano contenuti premium di grandi testate; (2) quelli aperti a tutti (RSL, Dappier, TollBit) non hanno ancora compratori che pagano, oppure pagano solo chi blocca i robot; (3) i nostri contenuti sono dati ufficiali con licenza aperta: il valore è la pulizia e la pagina, che si incassa con il clic, non con la licenza. **Innesco per riaprire:** un programma con iscrizione automatica per siti piccoli che paghi per citazione senza bloccare la ricerca, oppure ≥ 100 citazioni al mese in Copilot nel rapporto di Bing (idea 1). Da ricontrollare a febbraio 2027 (un anno dopo il lancio di PCM).

---

## 4. Cosa si può fare a costo zero sui siti che abbiamo

Escluso dal conteggio: tutto ciò che è già nell'esperimento del 31/10 (data visibile, riquadro "Key figures", CSV e `Dataset` sulle pagine rifiuti), che **non si tocca fino al 28/12**.

### Idea 1. Bing Webmaster Tools e rapporto "AI Performance" (voto 7)
- **Cosa:** Massimiliano entra in bing.com/webmasters e importa i siti da Search Console (10 minuti, gratis). Proposta il 31/10 (`fronti-2026-10-31-traffico.md`, E2), **non ancora fatta** (nessuna traccia nel cruscotto né in `DA-FARE-MASSIMILIANO.md`).
- **Perché adesso vale di più:** (a) è l'**unico dato ufficiale e gratuito di citazioni** negli assistenti (Copilot, risposte AI di Bing e partner), con le "grounding queries", cioè le domande che hanno fatto citare la pagina, in anteprima pubblica dal 10/2/2026; (b) per una parte degli studi ChatGPT pesca molto da Bing, e Bing oggi ci manda 3 visite in 18 giorni contro 473 di Google: se le pagine non sono nel suo indice lo scopriamo e lo sistemiamo; (c) le domande che hanno fatto citare le pagine sono il miglior elenco di sotto-pagine da costruire.
- **Metrica:** pagine indicizzate da Bing per sito; citazioni AI per pagina; visite da bing.com + copilot.microsoft.com + duckduckgo.com.
- **Soglia (dal 31/10, invariata):** entro 30 giorni dal collegamento almeno il 50 % degli URL delle sitemap nell'indice di Bing e 30 visite al mese da Bing e famiglia.
- **Ore:** 1 di Claude + 10 minuti di Massimiliano. **Euro:** indiretti; 0-100 €/anno di visite in più.

### Idea 2. Regola per scegliere le sezioni nuove: "dove l'assistente non sa rispondere" (voto 7)
- **Cosa:** nella coda di costruzione si dà la precedenza alle famiglie che hanno insieme (a) una domanda "di numero" per voce ("rejection rate Pakistan", "case all'asta Roma prezzo"), (b) un numero ufficiale che nessuno ha già messo in pagina, (c) molte voci (matrice). È quello che già funziona, ma oggi non è scritto come criterio con un numero: lo diventa la **quota ChatGPT per sezione** dopo 30 giorni (Visa Income 58 %, Aste 69 %, Cruise 20 %, Tourist Tax 0 %).
- **Prova del criterio:** Tourist Tax (forma giusta, tema già coperto) 0 %; Aste (forma imperfetta, numero unico) 69 %.
- **Da applicare per prima a:** la sezione "quanti [nazionalità] si trasferiscono in [Paese]" (`moved-to`, ricerca del 28/10, già 2 visite da ChatGPT su `moved-to/nigerians`) e alle sotto-domande delle pagine Paese **dopo il 28/12** (per non toccare l'esperimento).
- **Ore:** 0 (criterio). **Euro:** è il valore del canale (sez. 6).

### Idea 3. L'offerta giusta sulle pagine che gli assistenti citano (voto 6)
- **Cosa visto oggi:** le pagine rifiuti più citate (Pakistan, Iraq) hanno AdSense e un link **SafetyWing**, assicurazione per nomadi digitali. Chi arriva da ChatGPT su quelle pagine sta chiedendo un **visto Schengen da turista**, e per il visto serve un'assicurazione di viaggio con copertura di 30.000 €: l'offerta adatta è quella per il visto (AXA Schengen su Tradedoubler, 10 % sulle vendite, aperto "irrespective of size", da `idee-2026-10-26.md`), se il programma è approvato. Aste Roma (69 % da ChatGPT) ha solo AdSense.
- **Quando:** le pagine Paese dei rifiuti **non si cambiano fino al verdetto del 28/12** (regola dell'esperimento). Il cambio si fa il 28/12 su tutte insieme, oppure prima solo se applicato in modo identico ai due gruppi con l'aggiornamento delle impronte (`esperimento_citazioni.py impronte --motivo …`), come prevede il file dell'esperimento. Per Aste, l'offerta adatta (mutui per l'acquisto all'asta) è un lavoro di monetizzazione da valutare a parte.
- **Euro:** 600 visite al mese da ChatGPT sulla rete, metà sulle pagine rifiuti; 300 × 1 % clic × 3 % acquisti × 3 € = 0,3 € al mese oggi: **20 €/anno prudente, 120 centrale, 500 ottimista** con il canale cresciuto (sez. 6). **Ore:** 1-2.

### Idea 4. Rapporto settimanale "quota assistenti" (voto 6)
- **Cosa:** uno script in `studio-business/strumenti/` che ogni mercoledì legge GoatCounter (`stats/toprefs/chatgpt.com` e le provenienze `gemini.google.com`, `perplexity.ai`, `copilot.microsoft.com`, `claude.ai`, `bing.com`) e scrive nel cruscotto: visite dagli assistenti per sito e per sezione, quota sul totale, **pagine citate per la prima volta** nella settimana. Serve all'idea 2 (decidere la coda con un numero) e a vedere subito se un altro assistente comincia a mandare visite.
- **Ore:** 1-2, nessuna pubblicazione Netlify. **Euro:** indiretti.

### Idea 5. "Is [assistente] available in [country]?" in Before You Fly (voto 4)
- **Domanda (autocomplete en-US, 4/11):** "is chatgpt available in" → 10 (china, hong kong, russia, mexico, india, japan, venezuela, "all countries"…); "chatgpt supported countries" → 10 ("list", "and regions", "not supported countries"…); "is claude available in" → 10 (china, hong kong, india, taiwan, russia, europe, philippines…); "gemini available countries" → 10 (mescolate con l'exchange di criptovalute "Gemini").
- **Fonti (curl 4/11):** anthropic.com/supported-countries **200**; support.google.com/gemini/answer/13575153 **200**; platform.openai.com/docs/supported-countries **200** (ma è la lista dell'API, non dell'app); help.openai.com (lista dell'app) **403**. La sezione `available-in/` esiste già (Starlink, Apple Pay, Apple Music, Apple TV, Spotify, YouTube Premium) e Starlink prende già visite da ChatGPT.
- **Perché solo 4:** la lista più cercata (quella dell'app ChatGPT) non si legge dal server; chi vive in un Paese escluso cerca un modo di aggirare il blocco (VPN), che non possiamo né vogliamo suggerire, quindi niente affiliazione; pubblico a pubblicità bassa (Cina, Russia, Venezuela); i fornitori rispondono già con la loro pagina. Dubbio da chiarire prima: la regola "nessun nome di modello AI nei file" vale anche per i nomi dei prodotti nelle pagine pubbliche?
- **Euro:** 10 / 60 / 250 €/anno. **Ore:** 3-4 con il motore esistente.

### Da non fare (con la prova)
- **`llms.txt`:** nessun effetto su 300.000 domini; Google dice che non serve (voto 2).
- **Aggiungere solo JSON-LD (FAQ, schema in più) sperando in citazioni:** nessun aumento misurabile nella prova con gruppo di controllo; gli assistenti leggono il testo visibile (voto 3). Lo schema resta dove descrive il testo visibile (regola di Google).
- **Bloccare GPTBot o gli altri robot di addestramento:** non porta soldi (nessuno paga lo sblocco a siti come i nostri) e non cambia le citazioni di ricerca; lasciare tutto aperto (voto 1).
- **Claude/Brave e Perplexity:** nessuno strumento per i proprietari dei siti; i robot sono permessi; 0 visite. Niente da fare oltre a ciò che serve per ChatGPT e Google.
- **Gemini / AI Overviews / AI Mode:** seguono l'indice di Google, nessun requisito in più (pagina ufficiale): il lavoro è quello solito su Google.

---

## 5. C'è un modo di farsi pagare dagli assistenti AI per i nostri dati?

**No, oggi no.** Riassunto della sez. 3 in una tabella di decisione:

| Strada | Perché non ora | Cosa la riaprirebbe |
|---|---|---|
| Programmi a ripartizione (Perplexity, ProRata) | Ripartiscono per citazioni e visite: da Perplexity 0, gist.ai piccolo | ≥ 50 visite al mese da perplexity.ai |
| Mercati di licenze (Microsoft PCM, Amazon) | Pilota con grandi testate e contenuti premium | iscrizione aperta a tutti + citazioni in Copilot nel rapporto di Bing |
| Licenze collettive (RSL) | Nessun assistente ha ancora firmato | il primo accordo firmato con un'azienda di IA |
| Pagamento per lettura (TollBit, Cloudflare) | Blocca chi non paga, cioè ChatGPT; Cloudflare vuole un dominio | un assistente grande che paghi le letture di ricerca (oggi nessuno) |
| Vendere i dataset | Dati ufficiali gratuiti alla fonte | un dataset nostro che non esiste altrove (per esempio una serie storica raccolta ogni giorno, come il registro degli scioperi) |

L'unico guadagno vero dagli assistenti oggi è **la visita**, pagata da AdSense e dalle affiliazioni sulle nostre pagine. Il fronte "farsi pagare" ha voto **2**: si ricontrolla a febbraio 2027, senza ore prima.

---

## 6. Quanto vale il canale (stima, con le ipotesi)

**Oggi:** circa **600 visite al mese** da ChatGPT (140 negli ultimi 7 giorni). Valore per visita: AdSense in revisione (dal 30/10), pubblici a pubblicità bassa (Pakistan, Iraq, Bangladesh 0,5-2 € ogni 1.000 pagine; Italia 1,5-4 €), circa 1,3 pagine per visita; affiliazioni poco adatte (sez. 4, idea 3). Risultato: **circa 2-3 € ogni 1.000 visite**, cioè 15-25 €/anno oggi.

| Scenario a 12 mesi | Visite al mese dagli assistenti | Ipotesi | €/anno |
|---|---|---|---|
| Prudente | 1.000 | le pagine citate restano le stesse; RPM 2 €; affiliazioni 0,5 % clic × 2 % acquisti × 20 € | **~50** |
| Centrale | 3.000 | sezione `moved-to` e 2-3 sezioni nuove scelte con l'idea 2; Bing collegato; RPM 2,5 €; 0,5 % × 3 % × 25 € | **~300** |
| Ottimista | 10.000 | il canale degli assistenti continua a raddoppiare in un anno come nel resto del web (Similarweb: visite dagli assistenti più che raddoppiate tra giugno 2025 e maggio 2026); 4-5 sezioni nuove citate; offerte adatte; RPM 4 €; 1 % × 3 % × 30 € | **~1.700** |

**Licenze e programmi per editori:** 0 € nel prudente e nel centrale, 0-50 € nell'ottimista.

**Il valore che non si vede negli euro:** gli assistenti portano le prime visite a pagine nuove settimane prima di Google (Visa Income: 58 % delle visite senza posizioni alte su Google). Il canale va letto come **acceleratore delle sezioni**, non come attività a sé; per questo nessuna idea di questo fronte supera l'asticella dei siti nuovi (≥ 7 e ≥ 5.000 €/anno), e nessuna chiede un sito nuovo.

**Voto severo del fronte.**
- Assistenti come **canale di visite** per le sezioni esistenti: **7** (reale, misurato, a costo zero, ma piccolo in euro).
- Assistenti come **fonte di pagamenti** per i dati: **2**.

---

## 7. Cosa serve da Massimiliano (sì/no)
1. **Bing Webmaster Tools:** importare i siti da Search Console (10 minuti, gratis). È la stessa richiesta del 31/10, ancora aperta.
2. Nessuna email a Perplexity, nessun modulo a Microsoft e nessuna iscrizione a RSL per ora: rendono 0. Se un giorno vorrà provarli, sono 10-30 minuti ciascuno e vanno fatti col suo nome.
3. Chiarire se la regola "nessun nome di modello AI nei file" vale anche per i nomi dei prodotti nelle pagine pubbliche (serve solo per l'idea 5).

Nessuna spesa. Nessun account social. Nessun contatto a freddo.

---

## 8. Fonti (lette il 4/11/2026)

**Numeri nostri:** `rete-siti.goatcounter.com/api/v0/stats/total`, `stats/toprefs`, `stats/toprefs/chatgpt.com` (per settimana e per tutto il periodo), `stats/hits` (308 percorsi, 1.111 visite), 17/10-3/11/2026. Pagine controllate con `curl`: Visa Income Pakistan e Iraq, Aste Roma, EsameB1 `/esempi/` e Milano, Before You Fly Starlink, Cruise MSC Magnifica, Tourist Tax home, Catalogna, Minorca; `robots.txt` e risposte ai robot di 6 siti.

**Pagine dei programmi (curl, stato HTTP):**
- Perplexity, Comet Plus: https://www.perplexity.ai/hub/blog/introducing-comet-plus (200) · Publishers Program: https://www.perplexity.ai/hub/blog/introducing-the-perplexity-publishers-program (200) · https://www.perplexity.ai/publishers (404)
- Microsoft PCM: https://about.ads.microsoft.com/en/blog/post/february-2026/building-toward-a-sustainable-content-economy-for-the-agentic-web (200)
- Cloudflare pay per crawl: https://www.cloudflare.com/paypercrawl-signup/ (200) · TollBit: https://tollbit.com (200) · RSL Collective: https://rslcollective.org (200) · Gist: https://gist.ai (200) · ProRata: https://www.prorata.ai (200) · Dappier: https://dappier.com (200), marketplace 403
- OpenAI, robot: https://platform.openai.com/docs/bots (200) · Apps SDK: https://developers.openai.com/apps-sdk (200)
- Google, AI features: https://developers.google.com/search/docs/appearance/ai-features (200)
- Liste dei Paesi: https://www.anthropic.com/supported-countries (200), https://support.google.com/gemini/answer/13575153 (200), https://platform.openai.com/docs/supported-countries (200), https://help.openai.com/en/articles/7947663-chatgpt-supported-countries (403)

**Studi e notizie (ricerca web; ahrefs.com non raggiungibile da questo server, letto tramite riassunti):**
- Ahrefs, schema e citazioni (gruppo di controllo): https://ahrefs.com/blog/schema-ai-citations/ ; riassunto: https://analyzify.com/hub/schema-markup-ai-citations-research
- Ahrefs, 1,4 milioni di domande: https://ahrefs.com/blog/why-chatgpt-cites-pages/ ; https://www.searchenginejournal.com/chatgpt-often-retrieves-but-rarely-cites-reddit-pages-data-shows/572243/
- Kevin Indig, posizione delle citazioni: https://searchengineland.com/chatgpt-citations-content-study-469483
- Contenuti con dati e tabelle: https://www.texta.ai/blog/original-research-ai-answers-commercial-queries ; https://www.gogochimp.com/blog/state-of-ai-cro-citations-2026
- Promptwatch, tipi di citazione: https://promptwatch.com/data/chatgpt-citation-types-over-time-july-2026
- Quota delle visite dagli assistenti: https://www.similarweb.com/blog/marketing/geo/gen-ai-stats/ ; https://missiongrowth.io/blog/ai-referral-traffic-statistics
- TollBit, clic dagli assistenti: https://searchengineland.com/google-more-visitors-ai-systems-report-462905 ; https://blankspace.so/blog/ai-bot-traffic-statistics-2026/
- Conversioni dagli assistenti (risultati contrastanti): https://searchengineland.com/llms-google-referral-conversion-study-463747
- Bing AI Performance: https://www.seroundtable.com/bing-webmaster-tools-ai-performance-report-40911.html ; https://locomotive.agency/blog/ai-performance-bing-webmaster-tools-seo-geo/
- ChatGPT e gli indici di ricerca: https://www.seroundtable.com/bing-powers-chatgpt-search-38345.html ; https://www.mediapost.com/publications/article/407692/chatgpt-uses-google-for-back-up-answers-test-conf.html
- Claude e Brave Search: https://techcrunch.com/2025/03/21/anthropic-appears-to-be-using-brave-to-power-web-searches-for-its-claude-chatbot/
- Comet Plus, condizioni: https://www.subscriptioninsider.com/article-type/news/perplexity-unveils-42-5m-revenue-sharing-model-as-comet-browser-takes-aim-at-google
- Microsoft PCM, partner: https://mediacopilot.ai/microsoft-publisher-content-marketplace-ai-licensing/
- RSL, stato: https://digiday.com/media/arena-group-buzzfeed-usa-today-co-vox-media-join-rsls-ai-content-licensing-efforts/ ; https://wan-ifra.org/2026/04/rsls-ai-use-compensation-plan-for-news-we-think-this-is-a-100-billion-opportunity-for-publishers/
- ProRata/Gist: https://digiday.com/media/boston-globe-future-vox-media-join-proratas-generative-ai-licensing-model/ ; https://whatsnewinpublishing.substack.com/p/fipp-congress-2026-publishers-split
- Dappier: https://techcrunch.com/2024/06/26/dappier-is-building-a-marketplace-for-publishers-to-sell-their-content-to-llm-builders
- App in ChatGPT, vendite: https://community.openai.com/t/chatgpt-app-monetization-apps-sdk/1372343
