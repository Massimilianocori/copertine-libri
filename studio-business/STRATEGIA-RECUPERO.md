# Strategia di recupero dopo il cambio di dominio

Scritta il 24/11/2026. Siti: Before You Fly (BYF), Visa Income, EsameB1; in coda pagaccnl.com e payrolltaxbystate.com.

Regola del documento: ogni indicazione ha una fonte ufficiale Google o un caso documentato. Dove ragiono io senza fonte diretta scrivo **ipotesi**. Le citazioni in inglese sono copiate dalle pagine lette il 24/11/2026.

## In breve

1. Il cambio di dominio è fatto bene dal lato tecnico (301 pagina per pagina, canonical, sitemap, robots: ricontrollati oggi). **Non si torna indietro e non si cambiano più gli URL.**
2. Il crollo del 16–17/11 non è il comportamento che Google descrive per uno spostamento. Nello stesso periodo abbiamo sommato quattro cose: spostamento (8/11), aggiornamento principale di Google (10–24/11), noindex di massa più centinaia di pagine e titoli nuovi (11–18/11), Cambio di indirizzo (~17/11). Con i dati che abbiamo oggi **non si può dire quale delle quattro pesa di più**. Servono 6 controlli in Search Console (sezione 1.3), 20 minuti in tutto.
3. La spiegazione più probabile (ipotesi) è la qualità percepita del sito intero su un dominio nuovo, non la tecnica dello spostamento: EsameB1 ha fatto lo stesso identico spostamento lo stesso giorno e ha 6 pagine su 8 indicizzate.
4. Quindi: prima misurare, poi poche azioni additive e reversibili, **un solo** intervento di sfoltimento deciso con dati migliori (non stanotte), e nessuna nuova ondata di modifiche di massa per 14 giorni.
5. Tempi ufficiali: «a few weeks» per lo spostamento, «several months» per una rivalutazione della qualità. Non esiste un'azione che riporti il traffico in pochi giorni.

---

## 1. Diagnosi

### 1.1 Fatti verificati

| # | Fatto | Da dove viene |
|---|---|---|
| F1 | I vecchi indirizzi rispondono 301 verso la stessa pagina del nuovo dominio; www e http portano al dominio giusto; robots.txt aperto; canonical sul nuovo dominio; nessun noindex sulle pagine in sitemap; sitemap online = 1.553 (BYF) e 813 (Visa) URL | Controllo fatto oggi con richieste dirette e lettura di `sito/` |
| F2 | Google ha distribuito il **November 2026 core update dal 10/11 al 24/11** (chiuso oggi alle 14:03 UTC). Oggi ha preannunciato un **December 2026 core update** | https://status.search.google.com/summary |
| F3 | Tra l'11/11 e il 18/11 sono uscite, sui domini appena spostati: +210 pagine Visa (11/11), Starlink in 215 Paesi su BYF (13/11), noindex su 307 pagine BYF e 495 Visa (13/11), 128 titoli cambiati su Visa (14/11), 701 titoli cambiati su BYF (18/11) | Storia dei commit del repository |
| F4 | BYF: vecchia proprietà ~2.000 impressioni/giorno fino al 15/11, ~0 dal 16/11; nuova proprietà 1.500–3.500/giorno il 9–15/11, ~0 dal 17/11. Cambio di indirizzo inviato «intorno al 17/11» | Schermate del titolare |
| F5 | Controllo URL: BYF 2 su 10 indicizzate, home indicizzata con ultima scansione 11/11, `/cabin-bags/ryanair/` «Rilevata, ma attualmente non indicizzata», mai scansionata. Visa 0 su 9. EsameB1 6 su 8. Nessuna azione manuale | Schermate del titolare |
| F6 | GoatCounter, visite totali al giorno (tutte le sorgenti): BYF 59 (9–15/11) → 31 (17–23/11); Visa 82 → 40; EsameB1 91 → 56. Il traffico non è a zero | API GoatCounter, letta oggi |
| F7 | Struttura dei link: tutte le pagine in sitemap sono a 1 o 2 clic dalla home (BYF: 219 a 1 clic, 1.332 a 2; Visa: 165, 601, e 45 a 3 clic). La home di BYF ha 231 link interni, quella di Visa 168. BYF ha 181 pagine con 2 link in entrata o meno | Analisi di `sito/` fatta oggi |
| F8 | Le pagine in noindex hanno ricevuto 13 visite (BYF) e 42 (Visa) in tutto il periodo: il noindex del 13/11 ha tolto poco traffico diretto | GoatCounter × `sito/` |
| F9 | La sitemap di BYF scrive come `lastmod` la data del giorno per quasi tutte le pagine (829 URL con 20/11, 521 con 16/11) | `beforeyoufly/genera.py`, riga del `lastmod` |
| F10 | AdSense ha rifiutato before-you-fly.com il 24/11 per «Low value content» | Titolare |

### 1.2 Che cosa dice Google, e come ci tocca

**Spostamento.** Google prevede oscillazioni, non l'azzeramento: «Expect temporary fluctuation in site ranking during the move»; per un sito medio «it can take a few weeks or more for Google to gradually start showing the new URLs instead of the old ones»; lo spostamento è finito solo quando «Googlebot will have to visit every URL on your old and new site at least once». Si aspetta anche che il traffico passi da un sito all'altro: «Ideally the traffic on the old site will go down, while on the new site the traffic goes up».
Fonte: https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes

**Una cosa alla volta.** «Change only one thing at a time» e «Plan your changes to your site one after the other, not everything at the same time» (stessa pagina). La pagina dello strumento Cambio di indirizzo aggiunge: «If you combine a site move with a redesign of the site's content and URL structure in the new location, you will probably see some traffic loss as Google might need to relearn and reassess the individual pages».
Fonte: https://support.google.com/webmasters/answer/9370220
Noi (F3) abbiamo cambiato contenuti, titoli e stato di indicizzazione di centinaia di pagine nei 10 giorni dopo lo spostamento. Questo è un fatto; che sia la causa è un'ipotesi.

**Cambio di indirizzo.** «it tells Google to emphasize crawling and indexing your new site over crawling your old site. It also forwards various signals from the old site to the new site, and tells Google to prefer the new site over the old when determining canonical pages. These actions continue for 180 days». E: «Google does not erase the old site from the index». Lo strumento quindi **non dovrebbe** azzerare le impressioni; sposta la preferenza sul nuovo sito.
Fonte: https://support.google.com/webmasters/answer/9370220

**Il reindirizzamento non garantisce l'indicizzazione della destinazione.** Stato «Page with redirect»: «The target URL of the redirect might or might not be indexed, depending on what Google thinks about that target URL».
Fonte: https://support.google.com/webmasters/answer/7440203

**«Rilevata, ma attualmente non indicizzata».** Definizione ufficiale: «The page was found by Google, but not crawled yet. Typically, Google wanted to crawl the URL but this was expected to overload the site; therefore Google rescheduled the crawl» (stessa fonte). Su Netlify il sovraccarico è poco credibile; resta la seconda lettura, documentata da Google stessa:
- John Mueller, 11/11/2026: «Usually this is a sign that Google's quality systems are unconvinced about your site» e «Just making the site smaller doesn't significantly raise the overall quality of the site». Fonte: https://www.seroundtable.com/google-crawled-discovered-currently-not-indexed-42507.html
- Mueller e Splitt, podcast di Google, luglio 2026: quando i sistemi sono «seriously worried about the quality of the website … we'll probably crawl a lot less. We'll index a lot less»; alla domanda se «discovered not indexed» sia un problema di qualità: «Sometimes». Fonte: https://www.searchenginejournal.com/google-explains-seo-connection-of-site-quality-to-non-indexed-pages/582683

**Budget di scansione.** La guida dice di sé che serve a siti con oltre 10.000 pagine che cambiano ogni giorno o oltre 1 milione di pagine: non è il nostro caso per dimensione. Ma spiega il meccanismo che ci riguarda: «Every site starts with the same default, conservative crawl capacity limit» (un host nuovo parte basso); la richiesta di scansione dipende da «a site's size, update frequency, page quality, and relevance»; «Even if the crawl capacity limit isn't reached, if crawl demand is low, Google will crawl your site less». E per Google ogni host è un sito a sé: il nuovo dominio non eredita il ritmo di scansione del vecchio.
Fonte: https://developers.google.com/crawling/docs/crawl-budget

**Indicizzazione non garantita.** «Indexing isn't guaranteed; not every page that Google processes will be indexed»; tra le cause: «The quality of the content on page is low».
Fonte: https://developers.google.com/search/docs/fundamentals/how-search-works

**Contenuti in scala.** «Scaled content abuse is when many pages are generated for the primary purpose of manipulating search rankings and not helping users… no matter how it's created». Segnali d'allarme della guida ai contenuti utili: «Are you using extensive automation to produce content on many topics?», «Are you producing lots of content on many different topics in hopes that some of it might perform well in search results?». Non abbiamo azioni manuali, quindi non c'è una violazione accertata; ma BYF è passato da 1.141 a 1.858 pagine in due settimane su una ventina di argomenti diversi, ed è il profilo che questi testi descrivono.
Fonti: https://developers.google.com/search/docs/essentials/spam-policies e https://developers.google.com/search/docs/fundamentals/creating-helpful-content

**Segnali di sito.** «Site-wide signals and classifiers are also used and contribute to our understanding of pages».
Fonte: https://developers.google.com/search/docs/appearance/ranking-systems-guide

**Aggiornamenti principali.** «We recommend waiting at least a full week after a core update completes before analyzing your site in Search Console». Dopo i miglioramenti: «some changes can take effect in a few days, but it could take several months for our systems to learn and confirm that the site as a whole is now producing helpful, reliable, people-first content».
Fonte: https://developers.google.com/search/docs/appearance/core-updates

### 1.3 Perché vecchia e nuova proprietà vanno a ~0 insieme: ipotesi in ordine di probabilità

Nessuna di queste è dimostrata. Accanto a ognuna c'è il controllo che la conferma o la smentisce.

| Ipotesi | Che cosa la sostiene | Che cosa la indebolisce | Controllo che decide |
|---|---|---|---|
| **I1. Qualità del sito sul dominio nuovo** (la più probabile). Google ha tolto le vecchie pagine perché reindirizzano, ma non ha messo in indice le nuove perché «non è convinto» del sito. Il Cambio di indirizzo ha reso il passaggio contemporaneo su tutto il sito invece che pagina per pagina | F5 (mai scansionata; home ferma all'11/11); le due dichiarazioni di Mueller; il confronto con EsameB1, stesso spostamento e stesso giorno ma 6 su 8 indicizzate, e con un profilo diverso (207 pagine, 629 clic in 28 giorni contro 212 clic su 42.000 impressioni di BYF); il segnale AdSense «low value content» sugli stessi due siti | Il 9–15/11 la nuova proprietà aveva impressioni: qualcosa era servito | C1, C2, C3 |
| **I2. Aggiornamento principale di novembre.** Le pagine sono in indice ma scese fuori dalle posizioni visibili | F2: il crollo cade dentro la finestra 10–24/11 | Non spiega «Rilevata, mai scansionata» | C1: se le pagine indicizzate sono stabili e le impressioni a zero, è posizione e non indice |
| **I3. Troppe modifiche insieme** (F3): Google sta «rileggendo e rivalutando» pagine cambiate subito dopo lo spostamento | Citazione dello strumento Cambio di indirizzo; date dei commit | Vale anche per EsameB1 solo in parte: lì non ci sono state ondate di pagine nuove | C3, C6 |
| **I4. Tempi dello spostamento.** Semplice ritardo: il vecchio è stato tolto prima che il nuovo fosse scansionato | Host nuovo con limite di scansione iniziale basso | Google descrive un passaggio graduale, non un vuoto; 16 giorni e la home non è stata riscansionata | C2 |
| **I5. Dato incompleto.** Le schermate mostrano «~0», ma GoatCounter registra ancora visite da Google (BYF 63 nella settimana 16–22/11) | F6 | Il calo del 70 % dei referral Google è reale | C4 |

Il ruolo del Cambio di indirizzo (I1): la fonte dice che «prefer the new site over the old when determining canonical pages». Se le pagine nuove non sono in indice, preferirle significa non mostrare niente. È una lettura coerente con le date, ma è **ipotesi**: la data esatta dell'invio non è certa («intorno al 17/11») e il calo della vecchia proprietà comincia il 16/11.

**I 6 controlli da fare in Search Console prima di ogni altra cosa** (per BYF e Visa, proprietà nuova e vecchia):

- **C1.** Indicizzazione delle pagine, proprietà nuova: numero di pagine indicizzate giorno per giorno dall'8/11; conteggi di «Rilevata, ma attualmente non indicizzata», «Scansionata, ma attualmente non indicizzata», «Esclusa dal tag noindex».
- **C2.** Impostazioni → Statistiche di scansione, proprietà nuova: richieste al giorno dall'8/11, divise per risposta e per scopo (rilevamento / aggiornamento); stato dell'host.
- **C3.** Indicizzazione delle pagine, proprietà vecchia: pagine ancora indicizzate e pagine in «Pagina con reindirizzamento».
- **C4.** Rendimento, esportazione giornaliera di clic e impressioni delle due proprietà dall'1/11, da mettere accanto ai referral Google di GoatCounter giorno per giorno.
- **C5.** Data esatta del Cambio di indirizzo e stato dell'avviso («spostamento in corso»).
- **C6.** Rendimento della proprietà nuova, 9–15/11, scheda Pagine: quali URL avevano impressioni. Controllo URL su 10 di questi oggi.

In più, dalla proprietà **vecchia**: esportare la scheda Pagine degli ultimi 3 mesi (impressioni per URL). Serve per lo sfoltimento (sezione 2, azione 7).

---

## 2. Piano in ordine

Giorno 0 = 25/11. Controlli a 3 giorni (28/11), 7 giorni (2/12), 14 giorni (9/12).

Gli obiettivi numerici sono **ipotesi** mie: Google non pubblica soglie. Servono a decidere, non a prevedere.

### Azione 1 — Fare i 6 controlli e fissare la base (25/11)

- **Cosa:** C1–C6 qui sopra, più un campione fisso di 20 URL per sito (le prime 20 pagine di quel sito nella lista della sezione 5) da ricontrollare sempre uguali con Controllo URL, senza richiesta.
- **Fonte:** «Search Console is your friend, especially during a site move. Verify data for each property» — https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes
- **Effetto atteso:** sapere quale ipotesi regge. Nessun effetto sul traffico.
- **Rischio:** nessuno.
- **Misura:** i numeri di C1–C3 e il campione diventano la riga «giorno 0» della tabella in sezione 4.

### Azione 2 — Fermare le modifiche di massa per 14 giorni (dal 25/11 al 9/12)

- **Cosa:** su BYF e Visa niente sezioni nuove, niente riscritture di titoli in blocco, niente nuove ondate di noindex, nessun cambio di URL. Restano permesse: correzioni di dati, le azioni 3–6 di questo piano (una pubblicazione sola per sito), l'azione 7 nella data prevista.
- **Fonte:** «Change only one thing at a time» (site move); «you will probably see some traffic loss as Google might need to relearn and reassess the individual pages» — https://support.google.com/webmasters/answer/9370220
- **Effetto atteso:** Google riesce a completare lo spostamento; noi riusciamo a capire che cosa funziona.
- **Rischio:** si rimanda lavoro nuovo su due siti. Costo basso: oggi le pagine nuove non entrano comunque in indice.
- **Misura:** 3/7/14 giorni: zero pubblicazioni fuori piano nei commit.

### Azione 3 — Sitemap: stesse pagine, divise per sezione, con `lastmod` vero, più una sitemap temporanea dei vecchi indirizzi (una pubblicazione, 25–26/11)

- **Cosa:**
  1. `sitemap.xml` diventa un indice che punta a una sitemap per sezione (`sitemap-liquids.xml`, `sitemap-available-in.xml`, …). **Stesso elenco di pagine di oggi**: tutte le indicizzabili, nessuna in noindex.
  2. `lastmod` = data dell'ultimo cambio vero del contenuto della pagina (impronta del testo principale), non la data della generazione.
  3. Sitemap temporanea `sitemap-vecchi-indirizzi.xml` con i vecchi URL `*.netlify.app`, ospitata sul nuovo dominio e inviata in Search Console (le due proprietà sono verificate dallo stesso account). Si toglie quando la proprietà vecchia mostra ~0 pagine indicizzate.
- **Fonti:**
  - Sitemap doppia nello spostamento: «Submit the two sitemaps you saved earlier from the mapping. Initially, the sitemap containing the new URLs would have zero pages indexed, while the sitemap of the old URLs would have many pages indexed… Search Console may show warnings for the sitemap that contains the old URLs about the URLs redirecting; this is normal» — https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes
  - Sitemap di un altro sito verificato: «How to cross-submit sitemaps for multiple sites» — https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
  - `lastmod`: «Google uses the <lastmod> value if it's consistently and verifiably … accurate»; «Google ignores <priority> and <changefreq>» — stessa pagina
  - Limiti: 50.000 URL o 50 MB per file — stessa pagina. Le nostre 1.553 e 813 sono lontanissime dal limite.
  - Che cosa mettere: «be sure to include all the content that you want Google to crawl» — https://developers.google.com/crawling/docs/crawl-budget
- **Sulla sitemap «ridotta alle pagine con visite»:** non ho trovato nessuna fonte ufficiale che dica che una sitemap più corta aiuta l'indicizzazione. La sitemap è un aiuto alla scoperta («it doesn't guarantee that all the items in your sitemap will be crawled and indexed» — https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview). Togliere dalla sitemap pagine che restano collegate e indicizzabili non cambia come Google giudica il sito. **Non la consiglio come misura a sé.**
- **Effetto atteso:** Google rivede i vecchi URL e registra i 301 più in fretta; in Search Console si legge l'indicizzazione sezione per sezione; `lastmod` torna credibile (ipotesi: oggi viene ignorato perché cambia a ogni generazione).
- **Rischio:** basso. Avvisi «reindirizzamento» sulla sitemap dei vecchi indirizzi: sono previsti dalla guida.
- **Misura:** 3 giorni: tutte le sitemap «Operazione riuscita», numero di URL rilevati = atteso. 7 e 14 giorni: pagine indicizzate per sezione (Indicizzazione delle pagine filtrata per sitemap); pagine indicizzate nella proprietà vecchia in calo.

### Azione 4 — Richieste di indicizzazione, 10 al giorno per 5 giorni (25–29/11)

- **Cosa:** la lista in sezione 5. Prima il Controllo URL senza richiesta; se la pagina è già indicizzata si salta e si prende la successiva. Una sola richiesta per pagina.
- **Fonti:** «there's a quota for submitting individual URLs and requesting a recrawl multiple times for the same URL won't get it crawled any faster»; «Crawling can take anywhere from a few days to a few weeks» — https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl . «There is a daily limit of inspection requests for each property that you own» — https://support.google.com/webmasters/answer/9012289 (la guida dice «per proprietà»; il titolare vede circa 10 al giorno per account: si lavora con 10).
- **Effetto atteso:** scansione delle pagine con più valore e degli indici di sezione, da cui Google raggiunge le altre («Google primarily finds pages through links from other pages it already crawled» — https://developers.google.com/search/docs/fundamentals/seo-starter-guide). La richiesta fa scansionare, non garantisce l'ingresso in indice.
- **Rischio:** nessuno. È anche un test: se le pagine richieste vengono scansionate ma restano «Scansionata, ma attualmente non indicizzata», l'ipotesi I1 (qualità) è confermata.
- **Misura:** 3 giorni: quante delle prime 30 richieste risultano scansionate (data di scansione presente). 7 giorni: quante delle 50 sono indicizzate. 14 giorni: lo stesso, più impressioni di quelle 50 pagine nel Rendimento. Soglie (ipotesi): a 7 giorni ≥ 50 % indicizzate = lo spostamento sta passando; < 20 % con pagine scansionate = problema di qualità.
- **Nota:** IndexNow non compare tra i metodi che Google elenca per chiedere una scansione (la pagina qui sopra elenca solo Controllo URL e sitemap). Per Google non serve.

### Azione 5 — Link dalla home e dagli indici alle pagine più forti (stessa pubblicazione dell'azione 3)

- **Cosa:**
  1. In home, in alto, un blocco «Most used» con le 20–30 pagine con più visite (sezione 5), con testo del link descrittivo.
  2. Nell'indice di ogni sezione, le 5–10 pagine più visitate della sezione in evidenza sopra la tabella.
  3. BYF: portare a 3 o più i link in entrata delle 181 pagine che ne hanno 2 o meno (blocco «Related» tra pagine della stessa sezione e dello stesso Paese).
  4. Togliere dalla home i link diretti a pagine in noindex (11 su BYF, 2 su Visa, 7 su EsameB1) o sostituirli con la pagina indicizzabile più vicina.
- **Fonti:** «Proper linking means that all pages that you deem important can be reached through some form of navigation» — https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview ; link scansionabili e testo del link — https://developers.google.com/search/docs/crawling-indexing/links-crawlable ; aggiornare i link interni dopo lo spostamento — https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes
- **Effetto atteso:** piccolo. I dati (F7) dicono che la struttura è già buona: tutto è a 1–2 clic. Il guadagno è nel dire a Google e agli utenti quali pagine contano. Il punto 4 è **ipotesi** (nessuna fonte dice che i link a pagine noindex danneggiano).
- **Rischio:** basso, purché non si cambino URL né titoli.
- **Misura:** 3 giorni: verifica nel sito pubblicato (numero di link in entrata per le 30 pagine). 7 e 14 giorni: stato di indicizzazione delle 30 pagine nel campione fisso.

### Azione 6 — Pagine di fiducia (stessa pubblicazione)

- **Cosa:**
  1. BYF: aggiungere in cima alla pagina About un paragrafo «Who runs it» come quello di Visa (chi pubblica il sito, come si paga, come segnalare un errore). EsameB1: pagina «Contatti» propria (oggi manca come pagina).
  2. Una pagina breve «How we check» per BYF, sul modello di «How it works» di Visa: da dove vengono i dati, ogni quanto si rileggono, che cosa succede quando la fonte cambia, quali parti sono generate in automatico da dati ufficiali.
  3. Su ogni pagina: data dell'ultimo controllo e link alla fonte ufficiale, visibili in alto (dove mancano).
  4. `privacy.html` e contatti nel piè di pagina di tutte le pagine e in sitemap.
- **Fonti:** la guida chiede «clear sourcing, evidence of the expertise involved, background about the author or the site that publishes it, such as through links to an author page or a site's About page», e di dichiarare «Who, How, and Why» compreso l'uso dell'automazione — https://developers.google.com/search/docs/fundamentals/creating-helpful-content . AdSense chiede navigazione chiara e contenuto che dia «a reason to visit and return» — https://support.google.com/adsense/answer/10015918
- **Effetto atteso:** nessun effetto rapido sull'indicizzazione (ipotesi). Conta per la valutazione di sito nel tempo e per la revisione AdSense.
- **Rischio:** nessuno. Nessun dato personale oltre a quello che il titolare decide di pubblicare.
- **Misura:** 3 giorni: pagine online e collegate da ogni pagina. 7 e 14 giorni: nessuna misura diretta.

### Azione 7 — Sfoltimento: uno solo, per famiglie, deciso il 2/12 con dati migliori

**I nostri numeri (GoatCounter, 17/10–24/11: i dati partono dal 17/10, quindi 39 giorni e non 60; visite da tutte le sorgenti; vecchio e nuovo dominio sommati).**

| | In sitemap | Con ≥ 1 visita | Con ≥ 2 | Con ≥ 3 | Con 0 visite |
|---|---|---|---|---|---|
| Before You Fly | 1.553 | **330 (21 %)** | 154 | 89 | 1.223 |
| Visa Income | 813 | **362 (45 %)** | 212 | 138 | 451 |
| EsameB1 | 207 | 133 (64 %) | 102 | 83 | 74 |

BYF per famiglia (pagine / con visite / visite totali):
available-in 449 / 96 / 314 · canadian-passport 229 / 35 / 40 · passport-validity 225 / 18 / 27 · australian-passport 173 / 22 / 36 · driving-abroad 116 / 22 / 29 · liquids 102 / 41 / 161 · cabin-bags 53 / 13 / 42 · ticket-release-dates 33 / 13 / 70 · india-e-visa-fee 25 / 15 / 44 · blue-badge-abroad 24 / 3 / 5 · public-transport-rules 20 / 13 / 24 · pets 17 / 5 / 18 · winter-tyres 14 / 4 / 7 · foreign-licence 14 / 3 / 5 · train-luggage 14 / 6 / 10 · tolls 13 / 3 / 4 · scooter 4 / 0 / 0.
Le tre famiglie «passaporto» e driving-abroad sono 743 pagine (48 % della sitemap) e portano 132 visite (13 %).

Visa per famiglia:
ceremony-wait-times 173 / 73 / 173 · visa-refusal-rates 153 / 100 / 490 · moved-to 94 / 45 / 103 · uk-english-test 84 / 49 / 139 · h1b-wage-level 55 / 11 / 13 · pagine singole 48 / 31 / 205 · es 40 / 13 / 38 · thailand-dtv 22 / 4 / 5 · pt 20 / 3 / 5 · nurses-abroad 16 / 6 / 7 · study-in-italy 14 / 13 / 50 · country 13 / 1 / 1 · mexico-residency 12 / 2 / 2 · top-university 12 / 7 / 28.

**Limiti di questi numeri, da dire chiaro:**
- Una pagina mai indicizzata o pubblicata dopo l'1/11 non può avere visite da Google. «Zero visite» oggi misura anche il danno, non solo la domanda.
- Google dice che poco traffico non vuol dire bassa qualità, e che rimpicciolire il sito da solo non basta: «Just making the site smaller doesn't significantly raise the overall quality of the site» (Mueller, 11/11/2026, fonte sopra). E: «Deleting content is a last resort… if you're considering deleting entire sections of your site, that's likely a sign those sections were created for search engines first… If that's the case for your site, then deleting the unhelpful content can help the good content on your site perform better» — https://developers.google.com/search/docs/appearance/core-updates
- A favore dello sfoltimento: «low-quality content on some parts of a website can impact the whole site's rankings, and thus removing low quality pages, merging or improving the content of individual shallow pages into more useful pages… could eventually help» — https://developers.google.com/search/blog/2011/05/more-guidance-on-building-high-quality . Mueller, 2018: «We only look at the index pages when it comes to understanding the quality of a website» — https://www.seroundtable.com/google-site-quality-indexed-pages-25593.html

**Decisione proposta.** Non fare stanotte una seconda ondata di noindex basata solo su GoatCounter. Farne **una sola il 2/12**, dopo il controllo a 7 giorni, con questa regola:

Una pagina **resta indicizzabile** se vale almeno una di queste:
1. ≥ 1 visita in GoatCounter nel periodo;
2. ≥ 10 impressioni negli ultimi 3 mesi nella proprietà **vecchia** di Search Console (esportazione dell'azione 1);
3. è la home, un indice di sezione o una pagina di servizio;
4. è stata pubblicata da meno di 28 giorni;
5. appartiene a una famiglia scritta a mano da fonti lette una per una (liquids, cabin-bags, ticket-release-dates, india-e-visa-fee, pets, public-transport-rules, train-luggage, tolls, winter-tyres su BYF; study-in-italy, pagine dei singoli visti su Visa).

Le altre si trattano **per famiglia**, non una per una:
- **Famiglia con meno del 15 % di pagine vive (regole 1–2) e meno di 0,3 visite per pagina** → le pagine senza visite e senza impressioni vanno in `noindex` e senza codice AdSense; le pagine vive restano. Oggi, con il solo GoatCounter, rientrerebbero: passport-validity (8 %), australian-passport (13 %), blue-badge-abroad (13 %), e al limite canadian-passport (15 %); su Visa: country (8 %) e al limite pt (15 %). Il dato di Search Console può salvarne una parte.
- **Famiglia tra il 15 % e il 40 %** (available-in, driving-abroad su BYF; h1b-wage-level, es, mexico-residency, thailand-dtv su Visa) → resta com'è per ora; niente AdSense sulle pagine senza visite; si rivaluta il 23/12.
- **Sopra il 40 %** → non si tocca.

**Noindex, unione o cancellazione?**
- **Noindex** adesso, perché è reversibile e non cambia nessun URL nel mezzo di uno spostamento. Google lo rispetta così: «Google will drop that page entirely from Google Search results» — https://developers.google.com/search/docs/crawling-indexing/block-indexing . Costo: Google continua a richiedere quelle pagine («Don't use noindex, as Google will still request, but then drop the page» — guida al budget di scansione); per un sito della nostra dimensione è un costo piccolo (ipotesi).
- **Unione** (301 verso l'indice della sezione, che ha già la riga con il dato del Paese) solo dal 23/12 in poi e solo per le famiglie rimaste morte: è ciò che chiedono sia Google («if you have consolidated content previously hosted on multiple pages to a new single page, you can redirect the older URLs to that new, consolidated page») sia AdSense («If you have many pages that are similar or have very similar content, consider expanding each page or consolidating the pages into one» — https://support.google.com/adsense/answer/10015918). Farlo ora sarebbe un secondo cambio di URL. In quel caso i vecchi indirizzi netlify vanno puntati direttamente alla destinazione finale («Avoid chaining redirects»).
- **Cancellazione (404/410)** solo per pagine senza un indice che ne contenga il dato. Mai 301 verso la home: «might be treated as a soft 404 error».
- Le pagine in noindex escono dalla sitemap (già così oggi).

- **Effetto atteso:** incerto. Togliere pagine senza visite costa zero traffico per definizione. Il beneficio sulla valutazione del sito è possibile ma non garantito e non rapido (mesi).
- **Rischio:** medio. È un altro cambio grosso durante lo spostamento; per questo è uno solo, dopo 7 giorni, e reversibile. Se il 2/12 i controlli mostrano che l'indicizzazione sta risalendo da sola (≥ 50 % del campione indicizzato), **si rimanda al 9/12**.
- **Misura:** 3 giorni dopo l'intervento: pagine «Esclusa dal tag noindex» in crescita in C1. 7 e 14 giorni: quota di pagine indicizzate sul totale indicizzabile; impressioni/giorno della proprietà nuova.

### Azione 8 — AdSense: quando chiedere la nuova revisione

- **Che cosa chiede AdSense:** «Your site has content quality issues. We believe that there isn't enough original, rich content that would be of value to users»; «Don't place the ad code on auto-generated pages or pages with little to no original content»; «Keep in mind that we may review all pages of your site, not just the sign-up URL»; tra i problemi di navigazione cita «redirects». Dopo le correzioni: «sign in to AdSense and confirm that you've resolved the issues on your site». E: «Building a high-quality site takes effort and time. When you've addressed the above points, submit your site for review… The review process usually takes a few days».
  Fonti: https://support.google.com/adsense/answer/81904 · https://support.google.com/adsense/answer/10015918 · https://support.google.com/adsense/answer/7299563
- **Non ho trovato** una regola ufficiale sul tempo minimo tra due richieste, né una frase che leghi l'approvazione all'indicizzazione in Google. Quello che segue è quindi **ipotesi** prudente.
- **BYF: chiedere la revisione solo quando sono vere tutte e quattro:**
  1. il codice AdSense è presente solo su pagine con contenuto scritto a mano o con visite (via dalle famiglie a modello, come già fatto il 13/11 sulle pagine in noindex);
  2. azioni 5, 6 e 7 pubblicate da almeno 14 giorni;
  3. almeno 20 delle 30 pagine di punta risultano indicizzate (Controllo URL) e la proprietà nuova ha impressioni tutti i giorni da 7 giorni;
  4. nessuna pubblicazione di massa negli ultimi 14 giorni.
  Con il calendario di questo piano: **non prima del 16/12**. Se il punto 3 non è raggiunto, si aspetta: una seconda bocciatura a breve non aggiunge informazione.
- **Visa ed EsameB1:** revisioni in corso, non toccare la richiesta. Su Visa applicare comunque il punto 1.
- **Rischio:** aspettare costa poco: con ~30 visite al giorno il ricavo pubblicitario di BYF oggi sarebbe trascurabile.
- **Misura:** 14 giorni: i quattro criteri, sì/no.

### Azione 9 — pagaccnl.com e payrolltaxbystate.com

- **Cosa:** solo i controlli C1–C3 e, se le proprietà vecchie esistono in Search Console, il Cambio di indirizzo e la sitemap dei vecchi indirizzi come nell'azione 3. Nessun'altra modifica finché BYF e Visa non danno un risultato leggibile.
- **Fonte:** «Try not to combine multiple moves…», «Change only one thing at a time» — fonti sopra.
- **Misura:** come azione 1.

---

## 3. Cosa non fare

| Non fare | Perché | Fonte |
|---|---|---|
| Tornare ai domini netlify.app | Sarebbe un secondo spostamento: altre settimane di oscillazione, e lo strumento dice «Don't chain site moves» | https://support.google.com/webmasters/answer/9370220 |
| Annullare il Cambio di indirizzo | Annullarlo richiede di togliere i 301; l'effetto dura 180 giorni e serve a trasferire i segnali | stessa fonte |
| Cambiare di nuovo URL o struttura delle cartelle | «keeping the same site architecture in the new location helps to pass the signals more directly» | stessa fonte |
| Togliere o allentare i 301 | «Keep the redirects for as long as possible, generally at least 1 year» | https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes |
| Richiedere più volte la stessa pagina, o cercare modi per superare la quota | «requesting a recrawl multiple times for the same URL won't get it crawled any faster» | https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl |
| Usare l'Indexing API per queste pagine | È riservata ad annunci di lavoro e dirette video | https://developers.google.com/search/apis/indexing-api/v3/quota |
| Bloccare con robots.txt le pagine da togliere | Google non vedrebbe più il noindex: «the crawler will never see the noindex rule» | https://developers.google.com/search/docs/crawling-indexing/block-indexing |
| Pubblicare altre sezioni o altre centinaia di pagine su BYF e Visa prima del 9/12 | È il profilo descritto dalla norma sui contenuti in scala e dai segnali d'allarme della guida | https://developers.google.com/search/docs/essentials/spam-policies |
| Aggiungere o togliere contenuti solo per sembrare «freschi», o toccare `lastmod` senza un cambio vero | «Are you adding a lot of new content or removing a lot of older content primarily because you believe it will help your search rankings… (No, it won't)» | https://developers.google.com/search/docs/fundamentals/creating-helpful-content |
| Reindirizzare le pagine tolte verso la home | «might be treated as a soft 404 error» | guida allo spostamento |
| Giudicare l'effetto dell'aggiornamento di novembre prima dell'1/12 | «waiting at least a full week after a core update completes» | https://developers.google.com/search/docs/appearance/core-updates |
| Chiedere subito la nuova revisione AdSense di BYF | Niente è cambiato dal rifiuto del 24/11 | https://support.google.com/adsense/answer/81904 |
| Toccare EsameB1 nella struttura | È il sito che ha retto; il suo calo è anche stagionale (sessioni finite a metà novembre). «Seasonality» è tra le cause normali di calo | https://developers.google.com/search/docs/monitor-debug/debugging-search-traffic-drops |

---

## 4. Calendario dei controlli

Stessi numeri, stessa ora, per BYF e Visa (EsameB1: solo righe 1, 5, 6).

| # | Misura | Dove | Giorno 0 (25/11) | 3 gg (28/11) | 7 gg (2/12) | 14 gg (9/12) |
|---|---|---|---|---|---|---|
| 1 | Pagine indicizzate, proprietà nuova | Indicizzazione delle pagine | base | ≥ base | in crescita | ≥ 30 % delle indicizzabili (ipotesi) |
| 2 | «Rilevata, non indicizzata» e «Scansionata, non indicizzata» | idem | base | — | la prima scende | la seconda non supera la prima (se sì: qualità) |
| 3 | Richieste di scansione al giorno, host nuovo | Statistiche di scansione | base | > base | > base | stabile o in crescita |
| 4 | Pagine indicizzate, proprietà vecchia | Indicizzazione delle pagine | base | — | in calo | verso 0 |
| 5 | Campione fisso di 20 URL: quante indicizzate | Controllo URL, senza richiesta | BYF 2/10 noto | ≥ 5/20 | ≥ 10/20 | ≥ 14/20 |
| 6 | Impressioni e clic al giorno, proprietà nuova | Rendimento | ~0 | > 0 ogni giorno | in crescita | ≥ 500 impressioni/giorno su BYF (ipotesi: un quarto di prima) |
| 7 | Referral Google della settimana | GoatCounter | BYF 63, Visa 70 | — | ≥ settimana prima | ≥ 100 |
| 8 | Sitemap per sezione: URL rilevati | Sitemap | dopo l'invio | tutte lette | — | — |

**Regole di decisione**
- **2/12:** se riga 5 ≥ 10/20 → lo spostamento sta passando: rimandare l'azione 7 al 9/12. Se riga 5 < 5/20 e le pagine richieste risultano scansionate ma non indicizzate → qualità: eseguire l'azione 7.
- **2/12:** prima lettura dell'effetto dell'aggiornamento di novembre (una settimana dalla chiusura).
- **9/12:** se le righe 1 e 6 sono ancora ferme → il problema è la valutazione del sito. Si passa a migliorare a fondo le 30–50 pagine migliori e a unire le famiglie morte dal 23/12; tempi attesi «several months». Nessun ritorno indietro sul dominio.
- **16/12:** prima data possibile per la revisione AdSense di BYF, se i quattro criteri dell'azione 8 sono veri.
- **23/12:** rivalutazione delle famiglie «tra 15 % e 40 %».
- **Dicembre:** è preannunciato un altro aggiornamento principale. Annotare la data di inizio e di fine da https://status.search.google.com/summary e non attribuirgli a caldo i nostri cambi.

---

## 5. Richieste di indicizzazione, 25–29/11 (10 al giorno)

Ordine per valore atteso: prima gli indici (aprono la strada alle pagine collegate), poi le pagine con più visite nel periodo 17/10–24/11 (numero tra parentesi). Prima di chiedere: Controllo URL; se è già indicizzata, o è una delle 8 + 2 già richieste, saltarla e prendere la prima della riserva. Le prime 20 pagine di ogni sito in questa lista sono anche il campione fisso dell'azione 1.

**Mercoledì 25/11**
1. https://visaincomechecker.com/ (109)
2. https://visaincomechecker.com/visa-refusal-rates/ (indice; 490 visite nella sezione)
3. https://visaincomechecker.com/australian-citizenship-ceremony-wait-times/ (17; 173 nella sezione)
4. https://visaincomechecker.com/uk-english-test/ (indice; 139)
5. https://visaincomechecker.com/moved-to/ (indice; 103)
6. https://before-you-fly.com/available-in/starlink/ (52)
7. https://before-you-fly.com/available-in/ (indice; 314 nella sezione)
8. https://before-you-fly.com/liquids/ (13; 161 nella sezione)
9. https://before-you-fly.com/ticket-release-dates/ (indice; 70)
10. https://before-you-fly.com/cabin-bags/ (9; 42)

**Giovedì 26/11**
1. https://visaincomechecker.com/visa-refusal-rates/pakistan/ (32)
2. https://visaincomechecker.com/visa-refusal-rates/turkiye/ (24)
3. https://visaincomechecker.com/visa-refusal-rates/bangladesh/ (21)
4. https://visaincomechecker.com/visa-refusal-rates/algeria/ (20)
5. https://visaincomechecker.com/visa-refusal-rates/australia-visas/ (20)
6. https://before-you-fly.com/ticket-release-dates/vatican-museums/ (28)
7. https://before-you-fly.com/cabin-bags/united/ (22)
8. https://before-you-fly.com/available-in/starlink/saudi-arabia/ (22)
9. https://before-you-fly.com/liquids/us-airports-tsa/ (17)
10. https://before-you-fly.com/liquids/barcelona/ (15)

**Venerdì 27/11**
1. https://visaincomechecker.com/visa-refusal-rates/nigeria/ (19)
2. https://visaincomechecker.com/visa-refusal-rates/india/ (18)
3. https://visaincomechecker.com/top-university-visas/j-find/ (18)
4. https://visaincomechecker.com/study-in-italy/isee-parificato/ (16)
5. https://visaincomechecker.com/visa-refusal-rates/iraq/ (15)
6. https://before-you-fly.com/pets/uk-pet-passport-2027/ (14)
7. https://before-you-fly.com/available-in/apple-pay/ (14)
8. https://before-you-fly.com/available-in/starlink/turkey/ (14)
9. https://before-you-fly.com/india-e-visa-fee/ (11; 44 nella sezione)
10. https://before-you-fly.com/liquids/berlin/ (12)

**Sabato 28/11**
1. https://visaincomechecker.com/australian-citizenship-ceremony-wait-times/casey/ (14)
2. https://visaincomechecker.com/visa-refusal-rates/uk/ (13)
3. https://visaincomechecker.com/moved-to/nigerians/ (13)
4. https://visaincomechecker.com/study-in-italy/ (indice; 50)
5. https://visaincomechecker.com/study-in-italy/student-visa-funds/ (12)
6. https://before-you-fly.com/available-in/wise/ (11)
7. https://before-you-fly.com/ticket-release-dates/nintendo-museum/ (9)
8. https://before-you-fly.com/india-e-visa-fee/australia/ (9)
9. https://before-you-fly.com/cabin-bags/wizz-air/ (8)
10. https://before-you-fly.com/available-in/starlink/germany/ (9)

**Domenica 29/11**
1. https://visaincomechecker.com/visa-refusal-rates/china/ (12)
2. https://visaincomechecker.com/visa-refusal-rates/russia/ (12)
3. https://visaincomechecker.com/visa-refusal-rates/sri-lanka/ (12)
4. https://visaincomechecker.com/visa-refusal-rates/canada-visas/ (12)
5. https://visaincomechecker.com/es/cuanto-dinero-para-entrar-a-italia/ (10)
6. https://before-you-fly.com/available-in/stripe/ (8)
7. https://before-you-fly.com/ticket-release-dates/last-supper-milan/ (8)
8. https://before-you-fly.com/ticket-release-dates/ghibli-museum/ (8)
9. https://before-you-fly.com/liquids/budapest/ (8)
10. https://before-you-fly.com/liquids/belfast-international/ (8)

**Riserva, nell'ordine** (per sostituire le pagine già indicizzate o già richieste):
- Visa: `/visa-refusal-rates/tunisia/` (11), `/uk-english-test/india/` (11), `/visa-refusal-rates/china/easiest-schengen-visa/` (10), `/visa-refusal-rates/iran/` (9), `/moved-to/americans/` (9), `/uk-english-test/bristol/` (9), `/uk-graduate-visa/cost/` (7), `/work-visa-salary-thresholds/` (6).
- BYF: `/cabin-bags/ryanair/` (se non è tra le 8 già richieste), `/liquids/milan-malpensa/` (7), `/liquids/dubai/` (7), `/available-in/starlink/taiwan/` (7), `/available-in/starlink/cambodia/` (7), `/india-e-visa-fee/singapore/` (6), `/liquids/madrid/` (6), `/public-transport-rules/milan/` (5).
- EsameB1 (solo se il Controllo URL le dà non indicizzate): `/citta/milano/` (151), `/esempi/cils/` (125), `/esempi/` (82), `/ente/cils/` (80), `/costo/` (61).
- pagaccnl.com: la home, dopo i controlli dell'azione 9.

EsameB1 non ha righe nei cinque giorni perché ha già 6 pagine su 8 indicizzate e 2 richieste fatte: le richieste rendono di più dove l'indice è vuoto (ipotesi).

---

## 6. Che cosa resta incerto

- La causa principale del crollo (sezione 1.3): si chiarisce con C1–C6, non prima.
- Se lo sfoltimento aiuti: le fonti Google sono in tensione tra loro (2011: togliere può aiutare; 2026: rimpicciolire da solo non basta). Per questo è un intervento solo, reversibile, dopo la misura.
- I criteri AdSense per la nuova revisione sono miei, non di Google.
- I conteggi GoatCounter coprono 39 giorni, comprendono tutte le sorgenti, e penalizzano le pagine recenti o mai indicizzate.
- Le dichiarazioni di Mueller del 2026 sono lette da resoconti di Search Engine Roundtable e Search Engine Journal, non dalla fonte originale.

## Verifica del 25/11 sera: abbiamo rotto qualcosa noi?

Domanda di Massimiliano: «anche i siti nostri dall'inizio sono andati a zero». Controllato con i dati:

- **robots.txt, intestazioni, canonical**: tutto regolare sui 5 domini (Allow: /, nessun X-Robots-Tag, salute.py 0 errori).
- **Noindex del 13/11** (BYF 307 pagine, Visa 495): su quelle pagine c'era lo 0-1% delle visite dell'1-12/11 (BYF 4 su 491, Visa 2 su 594, EsameB1 3 su 956). Non sono la causa.
- **Titoli cambiati** (14-18/11): EsameB1 ha cambiato titolo al 68% del traffico delle sue 15 pagine migliori ed è il sito che tiene di più (26 visite Google il 24/11). Visa ne ha cambiato il 4% ed è a zero. I titoli non spiegano il crollo.
- **Paga CCNL**: nessuna pubblicazione dopo il 14/11, eppure crolla il 21/11 (da 12-25 al giorno a 0-2). Il calo è avvenuto senza nostre modifiche.
- **Payroll Tax**: stesse modifiche (dominio nuovo il 13/11, titoli il 14/11) e regge.

Visite da Google al giorno (GoatCounter):

| giorno | BYF | EsameB1 | Visa | CCNL |
|---|---|---|---|---|
| 10/11 | 33 | 52 | 52 | 0 |
| 13/11 | 33 | 44 | 33 | 0 |
| 16/11 | 16 | 15 | 18 | 16 |
| 18/11 | 2 | 15 | 15 | 17 |
| 21/11 | 5 | 11 | 1 | 2 |
| 24/11 | 3 | 26 | 1 | 1 |

Conclusione con i dati: nessun guasto tecnico nostro. Le pagine interne dei domini nuovi sono «Rilevata, non indicizzata»: Google le conosce ma non le scansiona. Questo succede quando giudica il sito poco prioritario. È coerente con l'aggiornamento di Google del 10-24/11 più il cambio di dominio. Il nostro errore resta questo: 3 domini spostati e centinaia di pagine toccate nella stessa settimana, senza un piano dei rischi. Le azioni restano quelle di questo file.

### Tutti i siti della rete, visite da Google a settimana (GoatCounter, 25/11)

| host | 27/10 | 3/11 | 10/11 | 17/11 |
|---|---|---|---|---|
| visaincomechecker.com + vecchio netlify | 13 | 95 | 240 | 53 |
| before-you-fly.com + vecchio netlify | 62 | 144 | 186 | 53 |
| esameb1.eu + vecchio netlify | 155 | 241 | 217 | 92 |
| pagaccnl.com (nuovo 13/11) | 0 | 0 | 24 | 68 (quasi 0 dal 21/11) |
| payrolltaxbystate.com (nuovo 13/11) | 0 | 0 | 2 | 4 |
| tourist-tax-calculator.netlify.app | 11 | 8 | 26 | 22 |
| italy-strikes-today.netlify.app | 0 | 2 | 12 | 31 |
| cruise-health-scores.netlify.app | 9 | 16 | 6 | 17 |
| flood-insurance-cost.netlify.app | 0 | 1 | 1 | 7 |
| altri siti .netlify.app | 0-1 | 0-1 | 0-1 | 0-1 |

Lettura: **calano solo i siti sui domini nuovi** (spostati l'8/11 e il 13/11). I siti rimasti su .netlify.app nello stesso periodo tengono o crescono (Italy Strikes 2 → 31, Tourist Tax 8 → 22). Dopo lo spostamento Visa e BYF erano saliti (settimana 10/11 la migliore di sempre), poi sono crollati dal 17/11. Il problema riguarda i domini nuovi, non un guasto comune a tutti i siti. Per i siti .netlify.app non serve nessun intervento strutturale: si continua con la manutenzione normale.

## Correzioni della revisione indipendente (25/11 sera, voto 7,5) — valgono sopra il testo precedente

Revisione completa in `studio-business/REVISIONE-STRATEGIA-RECUPERO.md`.

1. **Azione 9 corretta.** pagaccnl.com e payrolltaxbystate.com sono siti nati sul dominio l'11-12/11, non spostamenti di contenuti con traffico. Niente Cambio di indirizzo e niente sitemap dei vecchi indirizzi per loro. Solo C1-C3. «Payroll regge» non è dimostrato (2-4 visite a settimana): non si usa come prova.
2. **`lastmod` vero, con queste condizioni.** Il registro delle impronte parte con le date vere già note (data del commit che ha cambiato il testo principale della pagina, da `git log`), non con la data di stanotte. L'impronta esclude i blocchi «Most used», «Related», la data di generazione e il piè di pagina. Visa ha già il `lastmod` vero: si tiene. BYF ed EsameB1 si allineano allo stesso metodo.
3. **Sitemap dei vecchi indirizzi:** solo BYF, Visa ed EsameB1, file separato (`sitemap-vecchi-indirizzi.xml`), solo gli URL che esistevano prima dell'8/11.
4. **Azioni 5 e 6 ridotte, per non fare un'altra modifica di massa.** Blocco «Related» solo sulle 181 pagine BYF con 2 link in entrata o meno. Data e fonte in alto solo sulle pagine dove mancano, non su tutte. Il punto 6.4 (privacy e contatti nel piè di pagina) è già fatto. Pagine nuove di fiducia: sì.
5. **Diagnosi scritta come ipotesi.** I quattro domini nuovi salgono e poi crollano 7-10 giorni dopo; pagaccnl crolla senza nostre modifiche e senza Cambio di indirizzo. Questo rafforza l'ipotesi I1 (Google rivaluta i siti su domini nuovi e li giudica poco prioritari) e indebolisce I2. La conclusione della «Verifica del 25/11» è un'ipotesi, non un fatto: i siti di confronto sono piccoli.
6. **Citazioni.** La guida al budget di scansione ci riguarda (molti URL «Rilevata, attualmente non indicizzata»): si usa. «Try not to combine multiple moves» era fuori contesto: non si usa come motivo.
7. **Aggiunte.** La home di BYF entra nelle richieste di indicizzazione (prima della riserva). Le pubblicazioni BYF del 19 e 20/11 vanno contate tra le modifiche (F3).

**Decisioni per stanotte:** azione 3 VIA (con i punti 2 e 3); azione 5 VIA (blocco in home, indici di sezione, link a pagine noindex tolti dalla home; «Related» solo sulle 181 pagine); azione 6 VIA per le pagine nuove; azione 9 solo controlli.

**Seconda lettura del revisore: 8,6 → si esegue.** Note che restano: (a) «pagaccnl senza Cambio di indirizzo» va confermato in Search Console; (b) le date da `git log` si controllano a campione (un commit che rigenera tutto dà la stessa data a tutte le pagine); dove il dato ha una data propria (`letto_il`, `controllato_il`) si usa quella; (c) stanotte escono tre azioni insieme (sitemap, link interni, pagine di fiducia): non si potrà dire quale ha funzionato, si misura l'effetto d'insieme; (d) correzioni minori delle citazioni nel file di revisione.

### Dato del 26/11 mattina (foto di Massimiliano, Search Console esameb1.eu, 28 giorni)
112 clic, 2.930 impressioni, CTR 3,8 %, posizione media 7. Picco l'11/11 (circa 25 clic e 600 impressioni al giorno), quasi 0 dal 16 al 21/11, piccola risalita dal 22/11 (2-3 clic al giorno fino al 24/11). La risalita comincia **prima** dei lavori del 25/11 (sitemap, link, riquadro): è il punto di partenza per la misura del 28/11 e del 2/12, non un effetto dei lavori. Query in testa: «esame b1 italiano per cittadinanza milano 2026», «unistrasi.it risultati». L'avviso «1 dei tuoi altri siti verrà trasferito a questo sito» dice che il Cambio di indirizzo è ancora in corso.
