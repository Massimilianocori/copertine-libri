# Fronte nuovo: visite da canali diversi da Google (31/10/2026)

Richiesta: portare visite da canali diversi da Google, senza social, senza contatti a freddo, senza spese senza il sì di Massimiliano. Per ogni canale: traffico realistico, rischio, ore, voto. Alla fine i 3 esperimenti migliori con metrica e data di verifica.

Letti prima: skill `rete-siti`, `REGOLE-FISSE.md`, `ricerca-profonda-2026-10-28-assistenti.md`, `idee-2026-10-31-vincenti.md` (sez. 1, numeri GoatCounter), `CRUSCOTTO-RETE.md` (voci IndexNow e provenienze), `studio-business/strumenti/indexnow.py`, i file `robots.txt`, le pagine generate e i calendari `.ics` dei siti.

Voto 0-10 = traffico atteso per ora di lavoro, con rischio e costo dentro. Le stime di traffico sono stime (scritto il calcolo); i numeri della rete sono dati.

---

## 0. In breve

- **Provenienze vere 17-31/10 (GoatCounter `stats/toprefs`, letto oggi):** Google 276, **chatgpt.com 159**, diretto 91, **bing.com 3**, gemini.google.com 1, WeChat 1. Perplexity, Copilot, DuckDuckGo: **0**. ChatGPT è circa il 30 % delle visite che arrivano da fuori; Visa Income vive quasi solo di ChatGPT (94 su 130).
- **Il canale che già funziona è uno solo (ChatGPT)**: conviene raddoppiarlo con un esperimento misurato, non aprire dieci canali piccoli.
- **Bing quasi non porta niente** (3 visite in 15 giorni, IndexNow attivo dal 26/10) e **non abbiamo Bing Webmaster Tools**: è l'unico strumento gratuito che mostra le citazioni negli assistenti di Microsoft (rapporto "AI Performance").
- **Da non fare:** `llms.txt` (nessun effetto misurato), Apple News (domande chiuse), link nostri su Wikipedia (vietato dalle regole sul conflitto di interessi), directory generiche (spam).

| # | Canale | Visite/mese realistiche a 3 mesi | Rischio | Ore | Voto |
|---|---|---|---|---|---|
| 1a | ChatGPT (ricerca) con pagine più "citabili" | +100-400 (oggi ~320) | basso | 4-8 | **8** |
| 1b | Copilot / Bing AI | +10-50 | nullo | 1 + 10 min di Massimiliano | 7 (insieme al 2a) |
| 1c | Perplexity | 0-30 | nullo | 0 (nessuna azione propria) | 4 |
| 1d | Google AI Overviews / AI Mode | come Google (non si separa) | nullo | 0 | – |
| 1e | `llms.txt` | 0 | nullo | 0,5 | 2 |
| 2a | Bing Webmaster Tools + IndexNow (Bing, DuckDuckGo, Yahoo, Ecosia) | +20-60 | nullo | 1 + 10 min di Massimiliano | **7** |
| 2b | Yandex, Naver, Seznam | 0-5 | nullo | 0 (già coperti da IndexNow) | 2 |
| 3a | Google Discover (immagini grandi) | 0-100, imprevedibile | nullo | 1-2 | 4 |
| 3b | Google News | 0-20 (solo Italy Strikes) | basso | 2-4 | 3 |
| 3c | Apple News | 0 | – | – | 1 |
| 4a | CSV aperti sui nostri siti + schema Dataset (Google Dataset Search) | +10-40 | nullo | 4-6 | **6** |
| 4b | GitHub (archivio dati pulito) + Zenodo (DOI, citabile) | +5-20 | basso | 2-3 + 10 min di Massimiliano | 5 |
| 4c | Kaggle | +5-20 | basso (un account) | 2 | 4 |
| 4d | data.world | 0-5 | basso | 2 | 2 |
| 4e | Wikidata / Wikipedia | 0 da noi (solo se altri ci citano) | **alto** se lo facciamo noi | – | 1 |
| 5a | Calendari `.ics` (già esistono) misurati e resi stabili | +10-40 | nullo | 1-2 | 5 |
| 5b | Widget/riquadro da incorporare con link di ritorno | 0-30 | medio (link spam se fatto male) | 6-10 | 4 |
| 5c | Feed RSS (Italy Strikes, cambi di tasse) | 0-15 | nullo | 2 | 4 |
| 6a | data.europa.eu, modulo "Tell us your story" (riuso di dati UE) | 0-30, più un link istituzionale | nullo | 1 | 5 |
| 6b | Elenchi su GitHub (es. liste di dataset pubblici) con proposta di modifica | 0-10 | basso | 1 | 3 |
| 6c | Directory web generiche | 0 | **alto** (spam) | – | 1 |

---

## 1. Assistenti AI

### Cosa dicono i nostri numeri
- Le pagine citate da ChatGPT sono quelle con **un numero ufficiale in alto, con periodo, fonte e data** ("45.9% not issued (40,026 of 87,247 decisions)"), tabelle HTML, un indirizzo per ogni nazionalità, titolo uguale alla domanda (ricerca del 28/10, sez. 2). Pakistan: 16 visite su 18 da ChatGPT; Aste Roma 7 su 8; EsameB1 "esempi d'esame" 11 su 17.
- ChatGPT aggiunge `utm_source=chatgpt.com` ai link, e GoatCounter lo legge come provenienza: **il canale si misura già pagina per pagina** (`stats/hits/{id}`).

### Cosa dicono le prove esterne
- **Freschezza.** Ahrefs (17 milioni di citazioni): gli assistenti citano pagine in media il 25,7 % "più giovani" dei risultati normali di Google; **ChatGPT è il più sensibile** (pagine 393-458 giorni più recenti dei risultati di Google); fa eccezione AI Overviews. Fonte: ahrefs.com/blog/do-ai-assistants-prefer-to-cite-fresh-content.
- **Numeri e fonti nel testo.** Studio GEO (Princeton e altri, KDD 2024, arXiv 2311.09735): aggiungere statistiche, citazioni e fonti alza la visibilità nelle risposte generate fino a circa il 30-40 % (misura del loro banco di prova, non di ChatGPT reale). Il riempimento di parole chiave non serve. È esattamente la forma delle nostre pagine: va resa ancora più evidente, non cambiata.
- **`llms.txt`: nessun effetto.** SE Ranking (~300.000 domini): nessuna differenza nelle citazioni tra chi ha il file e chi no; Ahrefs: il 97 % dei siti con il file non ha ricevuto nemmeno una richiesta in un mese; Google dice che non lo usa. Fonte: searchenginejournal.com/llms-txt-shows-no-clear-effect-on-ai-citations-based-on-300k-domains/561542/. **Non si fa** (o al massimo come file da 5 minuti senza aspettarsi nulla).
- **Accesso del robot di ricerca.** OpenAI: per comparire nelle risposte di ricerca va permesso `OAI-SearchBot` nel robots.txt; nessuna domanda da fare. Nei nostri siti `robots.txt` = `Allow: /` per tutti: **a posto**. Lo stesso vale per PerplexityBot e Bingbot.
- **Quanto conta Bing per ChatGPT: le prove si contraddicono.** Seer Interactive (2024): l'87 % delle citazioni coincide con i primi risultati di Bing; Ahrefs (luglio 2025): sovrapposizione intorno al 10 % sia con Bing sia con Google. Conclusione onesta: Bing aiuta a farsi trovare (indicizzazione), ma non è la chiave unica. IndexNow resta utile e gratuito.
- **Copilot si può misurare**: Bing Webmaster Tools ha il rapporto "AI Performance" (anteprima pubblica dal febbraio 2026): quante volte ogni pagina è citata da Copilot e dalle risposte AI di Bing, con le domande che le hanno fatte citare. Niente clic, ma è l'unico dato ufficiale di citazioni AI che possiamo avere gratis. Non include ChatGPT.

### Cosa manca oggi nelle nostre pagine (controllato nei file generati)
- Nessuna data "aggiornato il" visibile e nessun `dateModified` nei dati strutturati delle pagine rifiuti e `moved-to` (la data c'è solo nella riga della fonte, "downloaded …").
- Nessuno schema `Dataset` e nessun CSV scaricabile sulle pagine con le tabelle (lo schema `Dataset` c'è solo in una pagina di Cruise Health Scores).
- Lo schema presente è `FAQPage` e `BreadcrumbList`: va bene, si tiene.

### Voti
- **1a ChatGPT: 8.** Già il secondo canale della rete, cresce da solo (31 → 68 → ~80 visite a settimana), e ogni pagina nuova con la stessa forma ne prende un pezzo. Il lavoro utile: freschezza visibile, dato in alto, CSV e schema, più pagine "matrice". Rischio basso: non c'è niente di ingannevole, sono dati ufficiali.
- **1b Copilot: 7** insieme al 2a (stesso lavoro).
- **1c Perplexity: 4.** Zero visite finora; non c'è nulla di specifico da fare oltre a quanto sopra.
- **1d AI Overviews:** segue Google e le sue regole; nessun lavoro separato.
- **1e `llms.txt`: 2.**

---

## 2. Altri motori di ricerca

- **Bing (con DuckDuckGo, Yahoo ed Ecosia, che usano i suoi risultati):** IndexNow è attivo dal 26/10 su tutti i siti (Italy Strikes da reinviare dopo il 1/11, come scritto nel cruscotto), ma Bing ha portato **3 visite in 15 giorni** contro 276 di Google. Mancano **Bing Webmaster Tools**: si collega importando i siti da Search Console (pulsante "Import your sites from GSC", 10 minuti, gratis, account di Massimiliano). Dà: pagine indicizzate da Bing, eventuali blocchi, parole cercate e il rapporto AI Performance. Stima: Bing e famiglia valgono di solito il 5-15 % del traffico di Google per siti in inglese → +20-60 visite al mese a 3 mesi. **Voto 7** (più per la misura delle citazioni che per le visite).
- **Yandex, Naver, Seznam:** ricevono già i nostri URL via IndexNow, senza lavoro. Pubblico sbagliato (russo, coreano, ceco). Nei 15 giorni: Yandex 1 visita (cruscotto). **Voto 2**, nessuna ora in più.
- **Motori nazionali** (Baidu, Yahoo Japan, Daum): pubblico non nostro o lingua diversa. Non si fa.

---

## 3. Google Discover, Google News, Apple News

- **Discover:** non serve nessuna domanda. Requisiti di Google: immagini di almeno 1.200 px di larghezza e il permesso `max-image-preview:large` (meta robots), contenuto che interessa. Nelle nostre pagine c'è `og:image`, ma **nessuna pagina ha `max-image-preview:large`** (grep sui `genera.py`). Il costo è piccolo (una riga in ogni `genera.py`, immagini 1200 px già quasi tutte). Ma Discover premia notizie e siti con pubblico affezionato: per pagine di dati su sottodomini `.netlify.app` il traffico è imprevedibile (spesso zero, a volte un picco). **Voto 4**: si aggiunge la riga alla prossima pubblicazione prevista, senza aspettarsi nulla.
- **Google News:** non si fa domanda (inclusione automatica dei contenuti di notizie). Solo Italy Strikes ha contenuti con data che somigliano a notizie, ma servono pagine con autore e notizie vere. **Voto 3.**
- **Apple News:** secondo il forum degli sviluppatori Apple, Apple risponde "non accettiamo nuove domande"; i canali da RSS sono sconsigliati e approvati raramente. **Voto 1.**

---

## 4. Dataset pubblici e citazioni

Le licenze lo permettono: Eurostat e Commissione europea CC BY 4.0 (riuso con fonte), Home Office OGL, dati USA di pubblico dominio, MIT CC BY 4.0. Pubblicare i nostri file puliti con la fonte è lecito; la nostra licenza va scritta (CC BY 4.0, "fonte: [ente]; elaborazione: [sito]").

- **4a CSV sui nostri siti + schema `Dataset` (voto 6).** Google ha un motore apposta, **Google Dataset Search**: legge lo schema `Dataset` (nome, descrizione di 50-5.000 caratteri, licenza, `distribution` con il link al CSV) dalle pagine nella sitemap; nessun modulo da compilare. È anche la forma che gli assistenti trovano per le domande "dataset/statistics". Lavoro: un CSV per tabella e il blocco JSON-LD nel `genera.py` (4-6 ore per Visa Income, Cruise, Tourist Tax). Traffico +10-40 al mese; vantaggio maggiore: giornalisti e ricercatori che citano la pagina con link.
- **4b GitHub + Zenodo (voto 5).** L'archivio del lavoro `Massimilianocori/copertine-libri` è **già pubblico** (controllato oggi): contiene anche gli appunti di `studio-business/`, quindi non è il posto giusto da mostrare. Meglio un archivio separato e pulito solo con i CSV, la licenza e un README, aggiornato dalle routine. Zenodo si collega a GitHub con un accesso di Massimiliano (una volta, gratis) e dà un **DOI** a ogni versione: i ricercatori citano i DOI, e Zenodo è indicizzato da Google Scholar e Dataset Search. Traffico +5-20 al mese, crescita lenta.
- **4c Kaggle (voto 4).** Le pagine dei dataset di Kaggle si posizionano bene su Google per "[tema] dataset", ma serve un account (poca manutenzione: aggiornamento del file) e il link verso di noi sta nella descrizione. Traffico +5-20 al mese. Si fa solo dopo 4a e 4b, se Massimiliano accetta un account in più.
- **4d data.world (voto 2):** pubblico piccolo, stesso lavoro di Kaggle.
- **4e Wikidata/Wikipedia (voto 1).** Le regole di Wikipedia (WP:ELNO n. 4 e WP:COI) vietano di aggiungere link al proprio sito per promuoverlo; la via ammessa è proporlo nella pagina di discussione e lasciare decidere ad altri, cosa che qui equivale a cercare contatti. Rischio: link tolti e dominio segnalato come spam. **Non si fa.** Le citazioni su Wikipedia arrivano solo se un redattore trova da solo i nostri dati (4a e 4b lo rendono più probabile).

---

## 5. Widget, feed, calendari

- **5a Calendari `.ics` (voto 5).** Esistono già: Italy Strikes (19 calendari per città e settore, 45 eventi in quello nazionale) e Before You Fly (date di uscita dei biglietti: Vaticano, Sagrada Família, Cenacolo, Pompei, Anne Frank). Ogni evento ha già il link alla pagina del sito. Due difetti trovati:
  1. **I clic dai calendari non si vedono**: arrivano come "diretto". Basta aggiungere `?utm_source=calendar` ai link degli eventi: GoatCounter lo mostra come provenienza (come fa con `chatgpt.com`). Costo minimo, esce con la pubblicazione prevista (i calendari di Italy Strikes non consumano nemmeno crediti Netlify: sono serviti da GitHub).
  2. **I calendari di Italy Strikes sono serviti da `raw.githubusercontent.com/…/ccr-b7fd6b9e-n096cr/…`**: se quel ramo cambia nome o viene cancellato, tutti gli abbonamenti si rompono senza avviso. Da tenere fermo il ramo (scriverlo nelle note di Italy Strikes) o, alla prossima pubblicazione prevista, servire una copia anche da `italy-strikes-today.netlify.app/calendars/`.
  Traffico: +10-40 al mese (chi è abbonato apre l'evento il giorno dello sciopero o dell'uscita dei biglietti).
- **5b Widget da incorporare (voto 4).** Esempio: riquadro "prossimi scioperi a Roma" per siti di B&B e agenzie, o calcolatore della tassa di soggiorno per affittacamere. Senza farlo conoscere (niente contatti a freddo) lo trova solo chi cerca "strike widget": pochi. Regola di Google sullo spam di link: i link con parole chiave dentro i widget distribuiti su molti siti sono "link spam"; il link di ritorno va con il solo nome del sito e `rel="nofollow"`, quindi conta solo per i clic, non per Google. 6-10 ore per 0-30 visite al mese. Da tenere per quando Italy Strikes o Tourist Tax avranno visite.
- **5c RSS (voto 4).** Un feed per Italy Strikes (nuovi scioperi) e per Tourist Tax (cambi di tariffe) costa 2 ore. Serve a chi usa lettori di feed (pochi) e aiuta i motori a vedere le novità. Non è un canale di visite vero.

---

## 6. Directory e risorse ufficiali con modulo

- **6a data.europa.eu, "Tell us your story" (voto 5).** Il portale dei dati aperti dell'UE ha un modulo per segnalare un riuso dei dati europei e un catalogo di casi d'uso con link. Visa Income (statistiche visti della Commissione, Eurostat sui primi permessi) è un riuso vero. È un modulo pubblico, non un contatto a freddo; il modulo chiede se accettiamo di essere ricontattati (si può dire sì: sono loro a chiedere). Un link da un sito istituzionale UE vale anche per la fiducia agli occhi dei motori e degli assistenti. 1 ora. Va compilato a nome di Massimiliano o con il nome del sito: **chiedergli il sì** prima.
- **6b Elenchi su GitHub** (liste di dataset pubblici, liste di calendari): si propone una modifica con una richiesta di modifica (pull request), che è il canale previsto dai curatori. Serve l'account GitHub di Massimiliano (già esiste). 0-10 visite al mese. Voto 3.
- **6c Directory generiche e "invia il tuo sito"**: spam, nessun valore per Google, rischio. Voto 1.
- **Per EsameB1 / EsamiDiStato** non ho trovato elenchi ufficiali con modulo (gli enti certificatori elencano solo le proprie sedi): niente da fare.

---

## 7. I 3 esperimenti migliori

Tutti a costo zero, senza deploy in più: escono con le pubblicazioni già previste (una per sito al giorno, la sera).

### E1. "Pagine citabili": prova A/B sulle pagine rifiuti di Visa Income (voto 8)
- **Cosa:** le pagine nazionalità di `visa-refusal-rates/` (circa 75) si dividono in due gruppi **a coppie simili** (stesso ordine di grandezza di domande di visto 2025, per esempio Pakistan con Nigeria, Iraq con Bangladesh), e in ogni coppia una pagina a caso riceve: (1) la riga visibile in alto "Updated 2 November 2026 · Data: European Commission, 2025"; (2) `dateModified` e uno schema `Dataset` con il CSV della tabella; (3) un riquadro "Key figures" di 3 righe con i numeri e la fonte. L'altra pagina resta com'è. La lista dei due gruppi si scrive nel cruscotto prima di pubblicare. Stessa cosa sui `?utm_source=calendar` dei calendari (5a) nello stesso giro.
- **Metrica:** visite da `chatgpt.com` (GoatCounter `stats/hits/{id}`) per pagina, gruppo trattato contro gruppo di controllo; in più le citazioni Copilot per pagina (E2) quando ci sono.
- **Soglia:** trattato ≥ 1,5 volte il controllo **e** almeno +30 visite al mese. Se sì, la stessa forma si applica a tutte le pagine di dati della rete (Visa Income, Cruise, Tourist Tax, Before You Fly, EsameB1). Se no, si tiene solo la data visibile (utile comunque per i lettori).
- **Limite onesto:** con ~190 visite al mese da ChatGPT su tutta la sezione, la prova vede solo effetti grandi; per questo il confronto è fatto a coppie.
- **Ore:** 4-6. **Verifica:** prima lettura **30/11/2026**, verdetto **28/12/2026**.

### E2. Bing Webmaster Tools e citazioni Copilot (voto 7)
- **Cosa:** Massimiliano entra in bing.com/webmasters con il suo account e importa i 10 siti da Search Console (10 minuti, gratis; nessuna verifica da fare sui file). Claude reinvia Italy Strikes a IndexNow dopo il 1/11 e controlla le pagine escluse dall'indice di Bing.
- **Metrica:** (a) pagine indicizzate da Bing per sito; (b) citazioni nel rapporto AI Performance per pagina; (c) visite da `bing.com` + `duckduckgo.com` + `copilot.microsoft.com` in GoatCounter.
- **Soglia:** entro il 30/11 almeno il 50 % degli URL delle sitemap indicizzati da Bing e almeno 30 visite al mese da Bing e famiglia (oggi 3 in 15 giorni). Se l'indice di Bing è basso, si sistemano le pagine escluse (stesso lavoro tecnico di Google).
- **Ore:** 1 di Claude + 10 minuti di Massimiliano. **Verifica:** **15/11/2026** (indice) e **30/11/2026** (visite e citazioni). Le foto della pagina AI Performance si chiedono insieme a quelle di Search Console ogni 2 settimane.

### E3. Pacchetto di dati aperti (voto 6)
- **Cosa:** tre CSV puliti con licenza CC BY 4.0 e fonte: (1) rifiuti dei visti Schengen 2025 per nazionalità e Paese (Commissione europea); (2) primi permessi di soggiorno 2025 per cittadinanza e Paese (Eurostat, sezione `moved-to`); (3) punteggi delle ispezioni sanitarie delle navi da crociera (CDC, Cruise Health Scores). Ognuno: link di scarico sulla pagina del sito con schema `Dataset` (Google Dataset Search), più un archivio GitHub separato e pulito con README, aggiornato dalle routine, collegato a Zenodo per il DOI (accesso di Massimiliano una volta). Poi il modulo data.europa.eu (6a) per i due dataset UE, **solo col sì di Massimiliano**.
- **Metrica:** (a) dataset visibili in Google Dataset Search (sì/no per ognuno); (b) visite con provenienza `github.com`, `zenodo.org`, `datasetsearch.research.google.com`, `data.europa.eu`; (c) scarichi del CSV (percorso del file in GoatCounter, se contato come pagina; altrimenti i download di Zenodo).
- **Soglia:** entro il 31/12 almeno 2 dataset su 3 in Dataset Search e almeno 20 visite al mese dalle nuove provenienze. Se sì, si aggiungono Tourist Tax (tariffe per città) e Before You Fly (`available-in`). Se no, si tengono i file (costo zero) e si smette.
- **Ore:** 6-9. **Verifica:** **15/12/2026** (indicizzazione) e **31/12/2026** (visite).

---

## 8. Cosa serve da Massimiliano (sì/no)
1. Collegare Bing Webmaster Tools importando da Search Console (10 minuti, gratis).
2. Collegare Zenodo al suo account GitHub (5 minuti, gratis) per il DOI dei dataset.
3. Sì o no al modulo di data.europa.eu (segnalazione del riuso, con il nome del sito).
Nessuna spesa. Nessun account social. Nessun contatto a freddo.

## Fonti esterne usate (31/10/2026)
- Ahrefs, studio su 17 milioni di citazioni e freschezza: https://ahrefs.com/blog/do-ai-assistants-prefer-to-cite-fresh-content/
- SE Ranking via Search Engine Journal, `llms.txt` su ~300.000 domini: https://www.searchenginejournal.com/llms-txt-shows-no-clear-effect-on-ai-citations-based-on-300k-domains/561542/
- Studio GEO (arXiv 2311.09735), sintesi: https://searchengineland.com/generative-engine-optimization-framework-introduced-research-paper-435855
- Seer Interactive, citazioni e risultati di Bing: https://www.seerinteractive.com/insights/87-percent-of-searchgpt-citations-match-bings-top-results ; Ahrefs, sovrapposizione: https://ahrefs.com/blog/ai-search-overlap/
- OpenAI, robot di ricerca (OAI-SearchBot), riassunto: https://umbrex.com/resources/generative-engine-optimization-resource-directory/openai-publisher-and-crawler-guidance/
- Bing Webmaster Tools, rapporto AI Performance: https://searchengineland.com/bing-webmaster-tools-testing-new-ai-performance-report-468039 ; https://www.searchinfluence.com/blog/bing-ai-performance-report-copilot-citations/
- Google, dati strutturati Dataset: https://developers.google.com/search/docs/data-types/dataset ; Discover: https://developers.google.com/search/docs/advanced/mobile/google-discover
- Apple News, domande chiuse (forum sviluppatori): https://developer.apple.com/forums/thread/782314
- Wikipedia, regole sui link esterni: https://en.wikipedia.org/wiki/Wikipedia:External_links
- data.europa.eu, modulo "Tell us your story": https://data.europa.eu/en/impact-studies/tell-us-your-story
