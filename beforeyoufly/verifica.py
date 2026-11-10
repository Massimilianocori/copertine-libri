"""Controlli prima di pubblicare Before You Fly.

Uso (dalla radice del repository, dopo python3 beforeyoufly/genera.py):
    python3 beforeyoufly/verifica.py            # tutti i controlli, compreso il browser a 375 px (serve node + Playwright)
    BYF_NO_BROWSER=1 python3 beforeyoufly/verifica.py   # senza il browser

1. Casi del passaporto calcolati a mano (TEST.md): il motore Python deve dare l'esito e la data minima attesi.
2. Il motore JS (lo stesso testo delle pagine) deve dare gli stessi risultati del Python, sui casi a mano e su 3.000 casi casuali.
3. Nessun link interno rotto in sito/.
4. Ogni pagina con una regola mostra la fonte ufficiale (URL) e la data del controllo; le frasi citate sono nella pagina.
5. Meta di verifica Google in ogni pagina; 404 con link assoluti, noindex e senza canonical; sitemap e robots.
6. Nessun nome di modelli o servizi di intelligenza artificiale nei file del sito e nei dati.
7. Browser a 375 px (Playwright): 5 pagine senza scorrimento orizzontale e senza errori in console; il controllo del passaporto risponde;
   il testo del controllo nella home ha contrasto di almeno 4,5:1 in tema chiaro e scuro; sezione visti e FAQ visibili.
8. Visti: ogni riassunto di una riga deriva da uno schema riconosciuto (ricalcolato da raccolta/passaporti.py sul testo salvato e confrontato
   con modelli fissi); i numeri del riassunto sono nella frase ufficiale; senza riassunto la pagina mostra solo la citazione (o dice che manca);
   nessun "senza visto" se il testo parla di ETA, tasse, tessere o moduli online prima del viaggio; nessun "serve un visto" se il visto è un ETA/eVisitor;
   le pagine Schengen rimandano a EES/ETIAS nella sezione visti.
9. Liquidi: risposta diretta in alto (regola + sintesi) e frase diretta senza numeri estranei; FAQ (JSON-LD FAQPage = testo visibile) da 4 a 6
   domande: ogni risposta è fatta di citazioni ufficiali intere (pagina dell'aeroporto, o GOV.UK / Your Europe per il Paese giusto) e/o di una
   frase nostra che è solo regola + sintesi del file (prima e ultima domanda) o uno dei modelli fissi che dicono che la pagina non lo dice.
10. Titoli <= 65 caratteri (salvo quando nessuna forma prevista ci sta) e descrizioni <= 160 in tutte le pagine.
11. Passaporti canadese e australiano: ogni riassunto (validità e visto) è ricalcolato con raccolta/passaporti_ca.py o passaporti_au.py sul testo
    salvato, deve corrispondere a un modello fisso e i suoi numeri devono stare nella frase ufficiale; controllo indipendente: nessun "senza visto"
    se il testo d'ingresso parla di eTA/ETA/ESTA/ETIAS (salvo ETIAS "Applications are not yet open." detto nel riassunto), e-visa, arrival card,
    moduli o registrazioni prima del viaggio, tessere o tasse; nessun "serve un visto" se il visto è elettronico o all'arrivo; ogni pagina cita il
    testo ufficiale intero, mostra fonte, data della pagina ufficiale, data del controllo, licenza (OGL Canada / CC BY 4.0 con l'attribuzione
    richiesta) e dice che il sito non è del governo; indice e collegamenti con le pagine britanniche della stessa destinazione (andata e ritorno);
    pagina solo per le destinazioni con testo specifico del Paese (genera.ha_testo_specifico), le altre senza pagina e fuori dalla sitemap.
    Nel browser (punto 7) anche 4 pagine nuove (2 canadesi, 2 australiane) a 375 px, tema chiaro e scuro.
12. Bagaglio a mano (dati/bagagli.json): ogni misura ha la citazione ufficiale (i suoi numeri, in cm e pollici se la fonte li scrive, sono nella
    frase citata; i cm non ufficiali sono la conversione esatta dei pollici ufficiali), l'URL https della fonte e la data del controllo, e la
    pagina li mostra; risposta diretta in alto; FAQ (JSON-LD e testo visibile) fatte solo di citazioni ufficiali intere; il confronto
    "ordinato" di genera.entra_borsa uguale a un controllo indipendente sulle 6 rotazioni (4.000 casi casuali) e il motore JS uguale al
    Python (3.000 casi); le pagine per misura elencano esattamente le compagnie calcolate dai dati; indice con ricerca e compagnie escluse con
    il motivo; pagina UE con tutte le citazioni, le fonti ufficiali UE, le tappe dell'iter e la data; collegamenti da home e liquidi;
    link affiliati solo verso i domini ammessi di monetizzazione.json (dal 30/10/2026; prima nessun link affiliato). Nel browser (punto 7): 5 pagine nuove a 375 px e
    10 casi dello strumento "Does my bag fit?" (borsa ruotata, misure uguali, decimali con punto e virgola, pollici, valore non valido),
    confrontati compagnia per compagnia con il Python; menu e home senza scorrimento orizzontale a 820 px.
13. Documenti per chi ha la cittadinanza italiana (dati/documenti_it.json, fonte Viaggiare Sicuri): la cache delle schede (raccolta/.cache/it/,
    fuori dal repository) deve avere le stesse impronte SHA-256 dei campi da cui sono stati scritti i fatti; ogni fatto è ricalcolato con
    raccolta/documenti_it.py sul campo salvato (o è un fatto scritto a mano con l'impronta del campo ancora valida) ed è legato a un campo
    («Passaporto», «Visto di ingresso») con la data della scheda; ogni citazione è nel campo parola per parola (al massimo 20 parole) e i numeri
    delle frasi nostre sono nelle citazioni; controlli indipendenti (CIE nominata, nessuna seconda validità, nessun «non serve il visto» che taccia
    ESTA/eTA/ETA/card/moduli); nessuna pagina italiana ha più di 25 parole di fila uguali a un testo di una scheda (tutte le sezioni di tutte le
    schede); pagina solo per le schede con contenuto specifico, con lingua it, canonical, GoatCounter, fonte, data, avvertenze, citazioni, FAQ
    (JSON-LD = testo visibile = fatti); link con le pagine britanniche (andata e ritorno); indice con tutte le schede, ricerca e metodo.
    Nel browser (punto 7) anche 4 pagine italiane a 375 px, tema chiaro e scuro, e la ricerca dell'indice.
14. Liquidi del 21/10/2026: ogni blocco FAQPage del sito è JSON valido e ben formato; titolo e H1 di ogni aeroporto con sigla, "liquid rules 2026",
    "hand luggage" e la regola vera (2 litri / 100 ml / per varco o viaggio / pagine in contrasto), mai "2 litri" con regola 100 ml; sottotitolo
    "100ml rule at"; gli 11 aeroporti nuovi (LCY, LPL, NCL, LBA, BFS, CWL, SOU, EXT, BOH, ORK, JER) nei dati con data 21/10, citazioni e URL https,
    con pagina e riga nell'indice; Birmingham, Glasgow e Belfast City tra gli esclusi con il motivo; nessun incluso tra gli esclusi; Jersey collegata
    agli aeroporti della stessa area; riquadro sui liquidi (citazione GOV.UK, link all'indice) in ogni pagina compagnia, con una sola FAQPage.
15. Blocco "Other useful tools for your trip" (in italiano nelle pagine it/documenti/) in ogni pagina indicizzabile: gli stessi link di
    genera.ALTRI_SITI / ALTRI_SITI_IT, nell'ordine, mai a questo sito, tutti rel="noopener" e senza nofollow o sponsored.
16. File chiave IndexNow.
17. "Is [service] available in [country]?" (dati/servizi.json da raccolta/servizi.py): impronta = lista; se c'è la cache delle pagine grezze
    (raccolta/.cache/servizi/, fuori dal repository) le liste sono ricalcolate dalle pagine salvate e le frasi citate ci sono ancora; la tabella
    di ogni servizio ha una riga per ognuno dei 250 codici con l'etichetta attesa (ricalcolata qui in modo indipendente); pagine servizio × Paese
    esattamente per le coppie di dati/servizi_domanda.json, con la risposta sì/no nella prima frase, fonte, data, la nota della fonte, la frase
    "non nella lista non vuol dire vietato", le citazioni, la FAQ (JSON-LD = testo visibile = prima frase), titolo <= 70 con la domanda, lastmod
    della sitemap = data della lettura; nessun nome di assistente di intelligenza artificiale e nessun consiglio per aggirare blocchi (VPN,
    proxy...); link da home, menu e About. Nel browser (punto 7) 5 pagine nuove a 375 px in tema chiaro e scuro e 2 a 820 px.
    Dal 7/11/2026 anche Google Wallet (riga "Tap to pay" della fonte nella prima frase, lista Google Pay online), Wise ("Not supported" per i
    Paesi non serviti, frase sull'invio = lista "send to"), Uber e Stripe; le liste in più (online, invio) sono ricalcolate dalla cache e
    fanno parte dell'impronta.
18. "Driving abroad" (dati/patenti.json da raccolta/patenti.py, 28/10/2026): se ci sono i grezzi (raccolta/.cache/patenti/, .cache/ca/, .cache/au/,
    fuori dal repository) esiti, frasi, convenzioni, impronte e testo sono ricalcolati e devono essere uguali al file; ogni frase citata è nel testo
    ufficiale salvato; impronte = testo; i fatti scritti a mano (dati/patenti_manuali.json) sono applicati e non scaduti; controllo indipendente
    dell'esito sulle frasi citate (es. "Recommended" solo con should/recommend); convenzione solo se la fonte la scrive; fonti solo gov.uk,
    travel.gc.ca, data.international.gc.ca, smartraveller.gov.au; pagine Paese × patente esattamente per le coppie cercate che nominano la patente
    (e con una risposta della fonte), con prima frase = modello fisso (risposta, frase dell'ente, fonte, data), frasi ufficiali, link alla fonte,
    "not legal advice", frase su dove si ottiene il permesso, link alle pagine passaporto dello stesso Paese, FAQ (JSON-LD = testo visibile =
    prima frase), titolo <= 70 con "IDP" e l'anno, sitemap con lastmod = data della lettura; tabelle per patente uguali ai dati; nessun link
    di noleggio o rete non ammessa: dal 30/10/2026 solo il riquadro "Hire a car" con il link generale DiscoverCars e il nostro a_aid (rel
    "sponsored noopener", target _blank, riga di trasparenza nel riquadro, sempre dopo la risposta e le regole ufficiali, avviso evidente
    sul permesso con esito "IDP needed" / "Local permit needed"; DiscoverCars altrove solo nella riga della home), nessun nome di assistente; link da home, About, pagine passaporto e "Available in?".
    Nel browser (punto 7) 5 pagine nuove a 375 px in tema chiaro e scuro e 2 a 820 px.
20. "Tolls with a rental car" (dati/pedaggi.json da raccolta/pedaggi.py, 30/10/2026): fonti solo dei gestori e dei governi (domini ammessi), lette
    con HTTP 200; se c'è la cache (raccolta/.cache/pedaggi/) ogni frase citata e ogni prova di prezzo è nel testo salvato e l'impronta della zona
    citata è uguale al file; dati = dati/pedaggi_manuali.json; una pagina per Paese + indice, in sitemap con lastmod = data della lettura; prima
    frase = fonte, data e risposta; citazioni, link e date delle fonti nella pagina; numeri dei prezzi presi dalla prova e nessun numero nelle frasi
    nostre che non sia in una citazione o in una prova; "Rental cars" detto solo con una frase ufficiale sulle auto a noleggio; FAQ da ricerche
    vere di dati/pedaggi_domanda.json (JSON-LD = testo visibile); titoli <= 70 con l'anno; tabella dell'indice = dati; solo il link generale
    DiscoverCars con il nostro a_aid, dopo la risposta e le regole (stesso controllo del punto 18); niente nomi di compagnie di noleggio,
    reti o assistenti; link andata e ritorno con le pagine Driving abroad dello stesso Paese, link da home, About e indice Driving abroad.
    Nel browser (punto 7) 3 pagine a 375 px in tema chiaro e scuro e l'indice a 820 px.
21. "Winter tyres and snow chains with a rental car" (dati/gomme.json da raccolta/gomme.py, 30/10/2026): fonti solo di ministeri, polizia,
    agenzie per la sicurezza stradale e portali dei governi (domini ammessi), lette con HTTP 200; dalla cache (raccolta/.cache/gomme/) ogni frase
    citata è nel testo salvato e l'impronta della zona citata è uguale al file; dati = dati/gomme_manuali.json; pagine Paese solo per i Paesi con
    almeno 5 ricerche vere in dati/gomme_domanda.json (ricalcolate); prima frase = fonte, data e risposta; citazioni, traduzioni (per le fonti non
    in inglese), link e date nella pagina; nessun numero nelle frasi nostre che non stia in una citazione; frase "ask the rental company whether
    winter tyres or chains are included and at what cost"; FAQ da ricerche vere (JSON-LD = testo visibile); titoli <= 70 con la stagione 2026-27;
    tabella dell'indice = dati, con il link alle fonti; solo il link generale DiscoverCars con il nostro a_aid, dopo la risposta e le regole;
    link andata e ritorno con le pagine Driving abroad e Tolls dello stesso Paese, link da home, About, 404 e dagli indici Driving abroad e Tolls.
    Nel browser (punto 7) 3 pagine a 375 px in tema chiaro e scuro e l'indice a 375 e 820 px.
22. "When do tickets go on sale?" (dati/biglietti.json da raccolta/biglietti.py, 30/10/2026): fonti solo dei siti ufficiali delle attrazioni
    (domini ammessi), lette con HTTP 200; dalla cache (raccolta/.cache/biglietti/) ogni frase citata è nel testo salvato e l'impronta della zona
    citata è uguale al file; dati = dati/biglietti_manuali.json; date dei prossimi 6 mesi ricalcolate qui in modo indipendente (giorno per giorno,
    Pasqua da una tabella scritta a mano) e coerenti con la regola (giorno della settimana nominato dalla citazione, sei settimane dopo, mercoledì
    prima della prima domenica); tabella della pagina = date calcolate; file .ics validi (CRLF, righe <= 75 byte, VCALENDAR/VEVENT, UID unici,
    DTSTAMP, DTSTART, SUMMARY, DESCRIPTION) con le stesse date e la stessa ora locale; prima frase = fonte, data e risposta con la prossima data;
    citazioni, link e date delle fonti nella pagina; nessun numero nelle frasi nostre che non stia in una citazione; FAQ da ricerche vere di
    dati/biglietti_domanda.json (JSON-LD = testo visibile); titoli <= 70 con gli anni 2026-27; pagine in sitemap; link esterni solo verso i siti
    ufficiali e le biglietterie che indicano (più Google Calendar e il blocco degli altri siti), riquadro della biglietteria ufficiale con
    "resellers may charge more", nessun rivenditore nominato; riquadro Viator spento finché VIATOR_TOUR è vuoto; link da home, About e 404;
    Stay22 (31/10/2026): i 6 link attesi, ognuno solo sulla pagina della sua attrazione e tutti nell'indice, rel="sponsored noopener",
    target _blank, etichetta Affiliate e riga di trasparenza nel riquadro, dopo la biglietteria ufficiale, Pompei = hotel a Napoli; stay22 altrove = errore.
23. "Driving in Canada, Australia and New Zealand on a foreign licence" (dati/patente_straniera.json da raccolta/patente_straniera.py, 31/10/2026):
    fonti solo degli enti delle patenti e dei governi (domini ammessi), lette con HTTP 200; dalla cache (raccolta/.cache/patente_straniera/) ogni
    frase citata è nel testo salvato e l'impronta della zona citata è uguale al file; dati = dati/patente_straniera_manuali.json; le pagine
    ufficiali che non si aprono (403 o anti-robot, registrate dalla raccolta) non hanno regole né pagina propria e l'indice dice "Not read";
    pagine = giurisdizioni lette + indice (nessuna pagina patente × destinazione); prima frase = fonte, data e risposta; citazioni, link e date
    nella pagina; nessun numero nelle frasi nostre che non stia in una citazione; "UK/US licence exchange: Yes" solo se la citazione nomina il
    Paese; FAQ da ricerche vere (JSON-LD = testo visibile); titoli <= 70 con l'anno; riquadro DiscoverCars dopo la risposta e le regole; link da
    home, About, 404, indice Driving abroad e pagine Driving abroad di Canada, Australia e Nuova Zelanda. Nel browser (punto 7) 4 pagine a 375 px
    in tema chiaro e scuro e l'indice a 820 px.
24. "Before you ride: public transport rules by city" (dati/trasporti.json da raccolta/trasporti.py, 31/10/2026): fonti solo delle aziende e
    autorità dei trasporti (domini ammessi), lette con HTTP 200; dalla copia salvata (raccolta/.cache/trasporti/) ogni citazione è nel testo
    parola per parola e l'impronta della zona citata è uguale al file; dati = dati/trasporti_manuali.json; città non lette senza dati né pagina,
    con la prova registrata (e un errore se la pagina ufficiale ora risponde 200 con testo); pagine = città lette + indice; prima frase = fonte,
    data e risposta; citazioni, traduzioni, link e date nella pagina; nessun numero nelle frasi nostre (riassunti, risposta, nota, cambio, FAQ,
    traduzioni) che non stia in una citazione; FAQ da ricerche vere (JSON-LD = testo visibile, traduzione dichiarata); titoli <= 70 con l'anno;
    sitemap con lastmod della lettura; nessun link di affiliazione (nessun link Wise attivo nei dati); link da home, About, 404, indice Driving
    abroad, pagine Driving abroad dei Paesi con una città letta (mai Canada, Australia, Nuova Zelanda: pagine già revisionate) e pagine
    "When do tickets go on sale?" di Milano, Amsterdam e Barcellona. Nel browser (punto 7) indice e 3 città a 375 px chiaro/scuro, indice a 820 px.
25. "Luggage rules on European trains" e "Eurostar check-in times" (dati/treni_bagagli.json da raccolta/treni_bagagli.py, 31/10/2026): fonti solo
    dei domini delle compagnie ferroviarie, lette con HTTP 200 e con data; dalla copia salvata (raccolta/.cache/treni_bagagli/) ogni citazione
    è nel testo parola per parola, ogni riga della tabella Eurostar (minuti per stazione) è nel testo della tabella ufficiale ricomposta e
    l'impronta della zona citata è uguale al file; dati = dati/treni_bagagli_manuali.json; compagnie non lette senza dati né pagina, con la
    prova registrata nei domini previsti; pagine = compagnie lette + indice + pagina Eurostar; prima frase = fonte, data e risposta;
    citazioni, traduzioni, link e date nella pagina; nessun numero nelle frasi nostre (riassunti, risposta, nota, FAQ, traduzioni) che non
    stia in una citazione della stessa compagnia; tabella Eurostar nella pagina = dati; FAQ da ricerche vere (JSON-LD = testo visibile,
    traduzione dichiarata); titoli <= 70 con l'anno; sitemap con lastmod della lettura; nessun link di affiliazione né nomi di rivenditori
    o depositi bagagli; link da home, About, 404, pagina EES, indice del bagaglio a mano, e nessun link nelle pagine già revisionate
    (trasporto pubblico, patente straniera). Nel browser (punto 7) indice, 3 compagnie e la pagina Eurostar a 375 px chiaro/scuro, indice
    e pagina Eurostar a 820 px.
26. "Pets: from the UK to the EU" (dati/animali.json da raccolta/animali.py, 31/10/2026): fonti solo GOV.UK e Commissione europea, HTTP 200
    e data; dalla copia salvata (raccolta/.cache/animali/) ogni citazione è nel testo, l'impronta è uguale, le tabelle GOV.UK delle rotte
    approvate e i link della Commissione per Paese sono uguali ai dati; dati = dati/animali_manuali.json; pagine = indice, calcolatore,
    passaporto 2027, rotte e un Paese solo con una ricerca vera che nomina il Paese e il Regno Unito; prima frase con fonte e data; ogni
    paragrafo tra virgolette è una citazione dei dati; numeri delle frasi nostre solo dalle citazioni; FAQ da ricerche vere (JSON-LD =
    testo visibile); lista del verme solitario ricavata dalla frase di GOV.UK; righe delle rotte nella pagina = tabelle; nessun consiglio
    veterinario ("Check with your vet and the official page" in ogni pagina), nessun link di affiliazione; calcolatore: 18 casi fatti a
    mano (tra cui l'esempio di GOV.UK), JS = Python su 3.000 casi casuali, Playwright a 375 px (chiaro e scuro) e 1280 px con 3 casi e
    ?dest=; passaporto 2027: errore da giugno 2027 (pagina da riscrivere); link andata e ritorno con Driving abroad (patente britannica) e Tolls.
20. (aggiunta del 31/10/2026) Croazia: caselli fino al 28/2/2027 e pedaggio senza caselli dal 1/3/2027, con la frase della legge (NN 156/2025,
    art. 67) citata e presente nella copia salvata della Gazzetta ufficiale, fonti Crolibertas linkate, traduzione di ogni citazione non
    inglese, riquadro del cambio non scaduto (errore dal 1/3/2027: pagina da riscrivere al presente) e frase "ask the rental company".
27. "India e-Visa fee by nationality" (dati/india_evisa.json da raccolta/india_evisa.py, 31/10/2026): fonti solo indianvisaonline.gov.in e
    boi.gov.in, HTTP 200 e data; i due PDF salvati hanno l'impronta SHA-256 registrata; SECONDA LETTURA INDIPENDENTE dei PDF (pdfplumber,
    o pdftotext -raw se manca): numero di righe = numero di Paesi dei dati = ultimo numero d'ordine, ogni nome e ogni valore uguale ai dati;
    citazioni (al massimo 40 parole) ed elenchi dei porti parola per parola nella copia salvata; pagine = indice + nazionalità ricalcolate
    dalle ricerche vere (almeno 2 sul costo che nominano la nazionalità) + visto all'arrivo + e-Arrival card + tedesco e francese (solo con
    ricerche vere nella lingua); ogni cella delle tabelle nelle pagine = PDF (non le funzioni di genera.py); prima frase con fonte e data;
    avviso "only on the official site" con il link ufficiale prima del primo titolo; nel contenuto solo link ufficiali o SafetyWing
    sponsorizzato (etichetta, trasparenza, dopo le informazioni ufficiali, solo in inglese); nessun rivenditore di visti; FAQ da ricerche vere
    (JSON-LD = testo visibile); titoli <= 70 con l'anno; sitemap; link in entrata; nessun link nelle sezioni già revisionate; Playwright a
    375 px (chiaro e scuro) e 1280 px su 8 pagine, con il filtro per Paese e per tipo di visto.
29. "Blue Badge abroad" (dati/bluebadge.json da raccolta/bluebadge.py, 4/11/2026): fonti solo GOV.UK (API dei contenuti), Your Europe e
    Commissione europea, disabilita.governo.it, service-public.gouv.fr, HTTP 200, data e impronta; dalla copia salvata ogni citazione parola
    per parola, l'impronta della zona citata e del testo, la tabella GOV.UK e le note di modifica; esiti = celle GOV.UK lette in modo
    indipendente; Paesi con pagina = ricerche vere ricalcolate; prima frase con fonte e date; citazioni, traduzioni, link e date nelle pagine;
    numeri nostri solo dalle citazioni; FAQ da ricerche vere (JSON-LD = testo visibile); titoli <= 70 con l'anno; sitemap; nessun link FIA né
    di affiliazione, solo link esterni ufficiali; link andata e ritorno con Driving abroad (solo patente britannica); home, About, 404.
    Nel browser (punto 7) indice, Italia, Spagna, carte europee e Amsterdam (trasporto pubblico) a 375 px chiaro/scuro.
30. Liquidi del 5/11/2026: i 37 aeroporti nuovi (elenco scritto qui) nei dati con lettura diretta, HTTP 200, data, impronta e URL https,
    con pagina, riga e fonte nell'indice e nella sitemap; nome del titolo da una ricerca vera (dati/liquidi_domanda.json); titolo <= 70 con
    l'anno; fonte nel riquadro in alto con la risposta; fonte di gruppo (Aena, HIAL) detta nella frase diretta; esclusi del 5/11 con il motivo.
    Riquadri di guadagno: "Hire a car at <aeroporto>" (solo DiscoverCars, link generale con il nostro a_aid, rel="sponsored noopener",
    target _blank, trasparenza nel riquadro, dopo la risposta, la regola e le eccezioni ufficiali, prima delle FAQ) esattamente sulle pagine
    degli aeroporti di vacanza ricalcolate qui (Spagna, Portogallo, Italia, Grecia, Malta, Croazia, Islanda e Antalya), mai su Regno Unito,
    Irlanda, isole della Manica, USA, Canada e scali di transito; "Where to stay in <città>" (Stay22) solo su Barcellona, Fiumicino, Linate,
    Malpensa e Granada con il link della stessa città scritto qui, dopo il riquadro noleggio, con etichetta, trasparenza e senza promesse.
31. Amazon nel bagaglio a mano ed eSIM (6/11/2026): ogni link verso un dominio Amazon in tutto il sito è https://www.amazon.co.uk o
    https://www.amazon.com, percorso /s con solo k e tag, tag giusto per il dominio (scritti qui: beforeyoufly-21 e beforeyoufl08-20),
    nessun ASIN né pagina prodotto, rel="sponsored noopener", e la pagina mostra «As an Amazon Associate we earn from qualifying
    purchases.»; link solo nelle 40 pagine del bagaglio a mano (indice, strumento, compagnie, misure), con il mercato ricalcolato qui
    (Europa e pagine per misura: .co.uk; USA e Canada: .com; Medio Oriente e Australia, indice e strumento: entrambi) e la misura della
    pagina nella ricerca; frase anche nella privacy. eSIM: link Awin con awinmid 118127, awinaffid 3145171 e ued verso roamable.co;
    riquadro «Before you go» solo nelle pagine passaporto (britannico, canadese, australiano) e nella pagina EES/ETIAS.
    Dal 10/11/2026 anche Vodafone Travel eSIM (awinmid 123870) e Pocket eSIM (awinmid 131040), awinaffid 3145171 (parametri scritti qui):
    elenchi dei Paesi in dati/esim.json validi (HTTP 200, almeno 100 Paesi ISO, data); in ogni pagina destinazione fornitori e ordine
    ricalcolati qui dall'elenco (Vodafone primo se l'elenco comprende il Paese e assente se no; Roamable; Pocket solo se l'elenco lo
    comprende); frase «list of destinations includes X (checked on <data>)» solo se X è nell'elenco e con la data della lettura; indici e
    EES/ETIAS con Roamable per primo e il testo generico; rel="sponsored noopener" su ogni link eSIM.
AVVISI (10/11/2026): le copie delle fonti in raccolta/.cache/ non sono nel repository. Il ricalcolo dalla copia (frasi, impronte, tabelle,
seconda lettura dei PDF) dei punti 13, 17, 18, 20-29 si salta con un avviso (stampato, contato, elencato in fondo, non è un errore) se la
copia manca, se è una pagina di blocco o anti-robot (titolo), o se è più recente dell'ultima lettura buona dei dati (la raccolta ha
rifiutato di scrivere il JSON). Con una copia della stessa lettura dei dati gli errori restano errori; gli altri controlli non cambiano.
Monetizzazione (30/10/2026, controllo comune di studio-business/strumenti/monetizzazione.py): i link di affiliazione sono
ammessi solo verso i domini di monetizzazione.json, con rel="sponsored noopener" e la riga di trasparenza nella pagina;
domini bloccati e link sponsorizzati verso altri domini sono errori; script AdSense, ads.txt e sezione privacy ci sono
solo se AdSense è acceso per questo sito in monetizzazione.json.
Esce con codice 1 se qualcosa non va.
"""
import hashlib
import json
import os
import random
import re
import subprocess
import sys
import tempfile
from html import escape
from html.parser import HTMLParser
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import genera as G  # noqa: E402
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("raccolta_passaporti", Path(__file__).resolve().parent / "raccolta" / "passaporti.py")
RP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RP)

SITO = G.SITO
P = {p["slug"]: p for p in G.PASS["paesi"]}

# ---------------------------------------------------------------- avvisi sulle copie salvate (10/11/2026)
# Le copie delle fonti in raccolta/.cache/ non sono nel repository (gitignore): ogni contenitore nuovo parte vuoto o con le sole raccolte
# rilanciate. Il RICALCOLO DALLA COPIA di una fonte (frasi parola per parola, impronte, tabelle, seconda lettura dei PDF) si salta con un
# AVVISO (stampato, contato, elencato in fondo) e non con un errore solo in tre casi:
#   1) la copia manca;
#   2) la copia è una pagina di blocco o anti-robot (il blocco non si aggira: restano i dati dell'ultima lettura buona);
#   3) la copia è più recente dell'ultima lettura buona scritta nei dati (la raccolta ha rifiutato di aggiornare il JSON): gli errori
#      del ricalcolo di quella fonte diventano avvisi, perché la copia non è quella da cui vengono i dati.
# Se la copia è della stessa lettura dei dati, gli errori del ricalcolo restano errori. Tutti gli altri controlli (dati = pagine,
# citazioni nei nostri JSON, prezzi solo dai dati, link, JSON-LD) restano errori come prima.
AVVISI = []
_CARTELLE_ASSENTI = set()
_RE_BLOCCO = re.compile(r"accesso negato|access denied|access to this page has been denied|just a moment|attention required|"
                        r"quick security check|are you a robot|verify you are (a )?human|request (was )?(blocked|rejected)|captcha|"
                        r"\b40[13] forbidden\b|^forbidden$|zugriff verweigert|acc[eè]s refus[ée]", re.I)


def avviso(punto, testo):
    AVVISI.append((str(punto), testo))


def pagina_di_blocco(raw):
    """True se la copia salvata è una pagina di blocco o anti-robot: si guarda solo il <title> (un testo normale può nominare i controlli)."""
    if isinstance(raw, bytes):
        if raw[:5] == b"%PDF-":
            return False
        raw = raw.decode("utf-8", errors="replace")
    m = re.search(r"<title[^>]*>(.*?)</title>", raw[:200000], re.I | re.S)
    return bool(m and _RE_BLOCCO.search(re.sub(r"\s+", " ", m.group(1)).strip()))


def copia_usabile(punto, fid, f_c, raccolta):
    """Copia salvata da usare per il ricalcolo: True, oppure False con l'avviso (copia mancante o pagina di blocco)."""
    if f_c is None or not Path(f_c).exists():
        cartella = Path(f_c).parent if f_c is not None else None
        if cartella is not None and not cartella.exists():
            if (punto, str(cartella)) not in _CARTELLE_ASSENTI:
                _CARTELLE_ASSENTI.add((punto, str(cartella)))
                avviso(punto, f"copie salvate assenti ({cartella.relative_to(SITO.parent)}/, fuori dal repository): ricalcolo dalle copie "
                              f"saltato per tutte le fonti; dati dell'ultima lettura buona (per ricrearle: python3 -I beforeyoufly/raccolta/{raccolta})")
        else:
            avviso(punto, f"fonte {fid}: copia salvata mancante: ricalcolo dalla copia saltato (python3 -I beforeyoufly/raccolta/{raccolta})")
        return False
    if pagina_di_blocco(Path(f_c).read_bytes()):
        avviso(punto, f"fonte {fid}: la copia salvata è una pagina di blocco o anti-robot (non si aggira): ricalcolo dalla copia saltato, "
                      "dati dell'ultima lettura buona")
        return False
    return True


def esito_copia(punto, fid, ef, f_c, letto_il):
    """Errori del ricalcolo dalla copia di una fonte: restano errori se la copia è della lettura dei dati (o più vecchia); diventano avvisi
    se la copia è più recente dell'ultima lettura buona (la raccolta ha rifiutato di aggiornare il JSON e ha tenuto i dati vecchi)."""
    if not ef:
        return []
    giorno = date.fromtimestamp(Path(f_c).stat().st_mtime).isoformat()
    if letto_il and giorno > str(letto_il)[:10]:
        for e in ef:
            avviso(punto, f"{e} [copia del {giorno}, dati dell'ultima lettura buona del {str(letto_il)[:10]}: la raccolta non ha aggiornato il JSON]")
        return []
    return ef

# (descrizione, paese, emissione, scadenza, arrivo, partenza, esito atteso, date minime attese in ordine dei controlli)
CASI = [
    ("1 Spagna (Schengen): tutto in regola", "spain", "2017-03-01", "2027-06-01", "2026-11-01", "2026-11-10", "ok", ["2027-02-10", "2016-11-02"]),
    ("2 Spagna: emesso esattamente 10 anni prima dell'arrivo -> NO (serve 'less than')", "spain", "2016-11-01", "2027-06-01", "2026-11-01", "2026-11-10", "no", ["2027-02-10", "2016-11-02"]),
    ("3 Spagna: emesso 10 anni meno un giorno prima -> sì", "spain", "2016-11-02", "2027-06-01", "2026-11-01", "2026-11-10", "ok", ["2027-02-10", "2016-11-02"]),
    ("4 Spagna: scadenza esattamente 3 mesi dopo l'uscita -> sì (al limite)", "spain", "2020-01-01", "2027-02-10", "2026-11-01", "2026-11-10", "ok", ["2027-02-10", "2016-11-02"]),
    ("5 Spagna: scadenza un giorno prima -> no", "spain", "2020-01-01", "2027-02-09", "2026-11-01", "2026-11-10", "no", ["2027-02-10", "2016-11-02"]),
    ("6 Thailandia: 31/8 + 6 mesi = 28/2 (fine mese) -> sì", "thailand", "", "2027-02-28", "2026-08-31", "2026-09-14", "ok", ["2027-02-28"]),
    ("7 Thailandia: 31/8/2027 + 6 mesi = 29/2/2028 (bisestile), scade il 28/2 -> no", "thailand", "", "2028-02-28", "2027-08-31", "2027-09-14", "no", ["2028-02-29"]),
    ("8 Belize 'more than 3 months': scadenza esattamente a 3 mesi -> no", "belize", "", "2027-03-01", "2026-12-01", "2026-12-10", "no", ["2027-03-02"]),
    ("9 Belize: un giorno in più -> sì", "belize", "", "2027-03-02", "2026-12-01", "2026-12-10", "ok", ["2027-03-02"]),
    ("10 USA durata del soggiorno: scade il giorno della partenza -> sì", "usa", "", "2026-12-20", "2026-12-01", "2026-12-20", "ok", ["2026-12-20"]),
    ("11 USA: scade il giorno prima della partenza -> no", "usa", "", "2026-12-19", "2026-12-01", "2026-12-20", "no", ["2026-12-20"]),
    ("12 Cile 'after the day you plan to leave': scade il giorno della partenza -> no", "chile", "", "2026-12-20", "2026-12-01", "2026-12-20", "no", ["2026-12-21"]),
    ("13 Costa Rica 'at least 1 day after': scade il giorno dopo -> sì", "costa-rica", "", "2026-12-21", "2026-12-01", "2026-12-20", "ok", ["2026-12-21"]),
    ("14 Turchia 150 giorni dall'arrivo: 10/10/2026 + 150 = 9/3/2027 -> sì", "turkey", "", "2027-03-09", "2026-10-10", "2026-10-20", "ok", ["2027-03-09"]),
    ("15 Turchia: 8/3/2027 -> no", "turkey", "", "2027-03-08", "2026-10-10", "2026-10-20", "no", ["2027-03-09"]),
    ("16 Cuba: 6 mesi dall'arrivo sì ma 3 mesi dalla partenza no", "cuba", "", "2027-06-01", "2026-11-01", "2027-03-15", "no", ["2027-05-01", "2027-06-15"]),
    ("17 Cuba: entrambe le condizioni -> sì", "cuba", "", "2027-06-15", "2026-11-01", "2027-03-15", "ok", ["2027-05-01", "2027-06-15"]),
    ("18 Hong Kong 1 mese dopo la partenza: 31/1 + 1 mese = 28/2 -> sì", "hong-kong", "", "2027-02-28", "2027-01-20", "2027-01-31", "ok", ["2027-02-28"]),
    ("19 Israele 90 giorni: 1/12/2026 + 90 = 1/3/2027 -> sì", "israel", "", "2027-03-01", "2026-12-01", "2026-12-08", "ok", ["2027-03-01"]),
    ("20 Bosnia 90 giorni dopo l'uscita + regola dei 10 anni", "bosnia-and-herzegovina", "2019-05-05", "2027-01-18", "2026-10-13", "2026-10-20", "ok", ["2027-01-18", "2016-10-14"]),
    ("21 Gibilterra, arrivo 29/2/2028: emesso 28/2/2018 -> no", "gibraltar", "2018-02-28", "2029-01-01", "2028-02-29", "2028-03-05", "no", ["2028-06-05", "2018-03-01"]),
    ("22 Gibilterra, arrivo 29/2/2028: emesso 1/3/2018 -> sì", "gibraltar", "2018-03-01", "2029-01-01", "2028-02-29", "2028-03-05", "ok", ["2028-06-05", "2018-03-01"]),
    ("23 Maldive 1 mese dall'arrivo: regola rispettata ma il passaporto scade prima della partenza -> NO", "maldives", "", "2026-12-05", "2026-11-01", "2026-12-15", "no", ["2026-12-01"]),
    ("24 Colombia: regola da leggere, nessun calcolo", "colombia", "", "2027-01-01", "2026-11-01", "2026-11-10", "manuale", []),
    ("25 Spagna senza data di emissione -> errore 'issue'", "spain", "", "2030-01-01", "2026-11-01", "2026-11-10", "errore", []),
    ("26 Partenza prima dell'arrivo -> errore 'order'", "thailand", "", "2030-01-01", "2026-11-10", "2026-11-01", "errore", []),
    ("27 Singapore: 31/3 + 6 mesi = 30/9 -> sì", "singapore", "", "2026-09-30", "2026-03-31", "2026-04-05", "ok", ["2026-09-30"]),
    ("28 Thailandia: 6 mesi dall'arrivo esatti ma scade prima della partenza -> NO", "thailand", "", "2027-04-10", "2026-10-10", "2027-05-01", "no", ["2027-04-10"]),
    ("29 Thailandia: soggiorno lungo, scade il giorno della partenza -> sì", "thailand", "", "2027-05-01", "2026-10-10", "2027-05-01", "ok", ["2027-04-10"]),
    ("30 Turchia: 150 giorni rispettati ma scade prima della partenza -> NO", "turkey", "", "2027-03-20", "2026-10-10", "2027-04-01", "no", ["2027-03-09"]),
    ("31 Israele: 90 giorni rispettati ma scade prima della partenza -> NO", "israel", "", "2027-03-05", "2026-12-01", "2027-03-10", "no", ["2027-03-01"]),
    ("32 Kazakistan: 30 giorni rispettati ma scade prima della partenza -> NO", "kazakhstan", "", "2026-12-10", "2026-11-01", "2026-12-20", "no", ["2026-12-01"]),
    ("33 Kazakistan: 30 giorni, scade dopo la partenza -> sì", "kazakhstan", "", "2026-12-21", "2026-11-01", "2026-12-20", "ok", ["2026-12-01"]),
]
SCADE_PRIMA = {"23 Maldive", "11 USA", "28 Thailandia", "30 Turchia", "31 Israele", "32 Kazakistan"}


def controlla_casi():
    errori = []
    for descr, slug, em, sc, ar, pa, atteso, minime in CASI:
        o = G.verifica_passaporto(P[slug]["regola"], em, sc, ar, pa)
        if o["esito"] != atteso:
            errori.append(f"CASO SBAGLIATO: {descr}: atteso {atteso}, calcolato {o['esito']}")
        if [c["minima"] for c in o["controlli"]] != minime:
            errori.append(f"DATA MINIMA SBAGLIATA: {descr}: attese {minime}, calcolate {[c['minima'] for c in o['controlli']]}")
        if any(descr.startswith(k) for k in SCADE_PRIMA) != o["scade_prima"]:
            errori.append(f"AVVISO 'scade prima della partenza' sbagliato: {descr}")
        if o["scade_prima"] and o["esito"] == "ok":
            errori.append(f"ESITO VERDE con passaporto che scade prima della partenza: {descr}")
    return errori


def data_casuale(rnd):
    return f"{rnd.randint(2015, 2031):04d}-{rnd.randint(1, 12):02d}-{rnd.choice([1, 15, 28, 29, 30, 31]):02d}"


def valida(d):
    try:
        G.date.fromisoformat(d)
        return d
    except ValueError:
        return f"{d[:8]}28"


def casi_casuali(n=3000, seme=7):
    rnd = random.Random(seme)
    slugs = sorted(P)
    out = []
    for _ in range(n):
        ar = valida(data_casuale(rnd))
        pa = G.piu_giorni(ar, rnd.randint(-3, 400))
        out.append([rnd.choice(slugs), rnd.choice(["", valida(data_casuale(rnd))]), valida(data_casuale(rnd)), ar, pa])
    return out


def controlla_js(casi):
    regole = {s: P[s]["regola"] for s in P}
    tutti = casi + [[c[1], c[2], c[3], c[4], c[5]] for c in CASI]
    script = ("var REG=" + json.dumps(regole) + ";\n" + G.MOTORE_JS + "\nvar casi=" + json.dumps(tutti) + ";\n"
              "console.log(JSON.stringify(casi.map(function(c){return verificaPassaporto(REG[c[0]],c[1],c[2],c[3],c[4]);})));")
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(script)
    try:
        r = subprocess.run(["node", fh.name], capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        return ["node non trovato: confronto JS saltato"]
    finally:
        os.unlink(fh.name)
    if r.returncode != 0:
        return ["Errore JS: " + r.stderr[:500]]
    js = json.loads(r.stdout)
    errori = []
    for c, j in zip(tutti, js):
        py = G.verifica_passaporto(regole[c[0]], c[1], c[2], c[3], c[4])
        if json.dumps(py, sort_keys=True) != json.dumps(j, sort_keys=True):
            errori.append(f"JS diverso dal Python per {c}: py {py} js {j}")
    return errori[:20]


class Link(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href = []

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k in ("href", "src") and v:
                self.href.append(v)


def controlla_link():
    errori = []
    pagine = list(SITO.rglob("*.html"))
    for f in pagine:
        p = Link()
        p.feed(f.read_text(encoding="utf-8"))
        for h in p.href:
            if h.startswith(("http://", "https://", "webcal://", "mailto:", "data:", "#", "javascript:")):
                continue
            h = h.split("#")[0].split("?")[0]
            if not h:
                continue
            dest = (SITO / h.lstrip("/")) if h.startswith("/") else (f.parent / h)
            dest = dest.resolve()
            if dest.is_dir():
                dest = dest / "index.html"
            if not dest.exists():
                errori.append(f"LINK ROTTO in {f.relative_to(SITO)}: {h}")
    return errori, len(pagine)


def leggi(rel):
    return (SITO / rel).read_text(encoding="utf-8")


def controlla_fonti():
    errori = []
    chk = "checked on " + G.data_lunga(G.PASS["controllato_il"])
    for p in G.PAESI:
        t = leggi(f"passport-validity/{p['slug']}/index.html")
        if escape(p["url_ingresso"]) not in t or chk not in t or "page last updated " + G.data_lunga(p["aggiornata"]) not in t:
            errori.append(f"passaporto {p['slug']}: fonte, data di aggiornamento o data del controllo mancanti")
        for b in p["testo"]:
            if escape(b["x"]) not in t:
                errori.append(f"passaporto {p['slug']}: testo ufficiale mancante: {b['x'][:60]}")
        if "Open Government Licence v3.0" not in t:
            errori.append(f"passaporto {p['slug']}: attribuzione OGL mancante")
    for a in G.AER["aeroporti"] + G.AER["nazionali"]:
        t = leggi(f"liquids/{a['slug']}/index.html")
        if escape(a["url"]) not in t or "checked on " + G.data_lunga(a["controllato_il"]) not in t:
            errori.append(f"liquidi {a['slug']}: fonte o data mancanti")
        for q in a["citazioni"] + a.get("eccezioni", []):
            if escape(q) not in t:
                errori.append(f"liquidi {a['slug']}: citazione mancante: {q[:60]}")
        if a.get("contrasto") and escape(a["contrasto"]["citazione"]) not in t:
            errori.append(f"liquidi {a['slug']}: seconda fonte (contrasto) mancante")
    t = leggi("ees-etias/index.html")
    for f in G.EES["frasi"]:
        if f["trovata"] and escape(f["frase"]) not in t:
            errori.append(f"EES/ETIAS: frase mancante: {f['frase'][:60]}")
    for k, pg in G.EES["pagine"].items():
        if escape(pg["url"]) not in t:
            errori.append(f"EES/ETIAS: fonte {k} mancante")
    if "checked on " + G.data_lunga(G.EES["controllato_il"]) not in t:
        errori.append("EES/ETIAS: data del controllo mancante")
    return errori


def controlla_struttura():
    errori = []
    for f in SITO.rglob("*.html"):
        t = f.read_text(encoding="utf-8")
        if re.search(r"(check|checked|re-check|re-checked|re-read|updated)( [a-z]+)? (every (week|month)|weekly|monthly)", t, re.I):
            errori.append(f"promessa di ricontrollo periodico in {f.relative_to(SITO)}")
    for p in G.PAESI:
        t = leggi(f"passport-validity/{p['slug']}/index.html")
        if not p["regola"] and ("with a checker for your dates" in t or "data-checker data-dati" in t):
            errori.append(f"{p['slug']}: pagina senza controllo che promette il controllo")
    ie = leggi("passport-validity/ireland/index.html")
    if "not legally required to show a passport" not in ie or "airlines and ferry operators" not in ie:
        errori.append("Irlanda: spiegazione Common Travel Area mancante")
    gib = leggi("passport-validity/gibraltar/index.html")
    if "Gibraltar or the Schengen Area" not in gib or "Schengen: " in gib:
        errori.append("Gibilterra: riassunto o gruppo Schengen sbagliato")
    for f in SITO.rglob("*.html"):
        t = f.read_text(encoding="utf-8")
        if f'<meta name="google-site-verification" content="{G.GOOGLE_VERIFICA}">' not in t:
            errori.append(f"meta Google mancante in {f.relative_to(SITO)}")
        if f.name != "404.html" and f'<link rel="canonical" href="{G.URL_SITO}/' not in t:
            errori.append(f"canonical mancante in {f.relative_to(SITO)}")
        # ammessi solo il contatore GoatCounter e lo script AdSense (quello lo controlla il punto 19, monetizzazione.py)
        if re.search(r'<script[^>]+src="(?!https://gc\.zgo\.at/count\.js"|https://pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js\?client=ca-pub-\d{16}")', t):
            errori.append(f"script esterno in {f.relative_to(SITO)}")
    nf = leggi("404.html")
    rel = [h for h in re.findall(r'href="([^"]+)"', nf) if not h.startswith(("/", "http", "data:", "#", "mailto:"))]
    if rel:
        errori.append(f"404: link relativi {rel[:3]}")
    if 'rel="canonical"' in nf or 'content="noindex"' not in nf:
        errori.append("404: deve essere noindex e senza canonical")
    sm = leggi("sitemap.xml")
    n_pagine = sum(1 for f in SITO.rglob("*.html") if f.name != "404.html" and not f.name.startswith("google"))
    if sm.count("<url>") != n_pagine or "404.html" in sm:
        errori.append("sitemap: numero di URL sbagliato o 404 presente")
    if f"Sitemap: {G.URL_SITO}/sitemap.xml" not in (SITO / "robots.txt").read_text():
        errori.append("robots.txt senza sitemap")
    if 'ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."' not in (SITO / "netlify.toml").read_text():
        errori.append("netlify.toml: regola ignore mancante")
    if G.URL_SITO not in leggi("index.html"):
        errori.append("URL_SITO non usato")
    return errori


# Modelli fissi dei riassunti dei visti: un riassunto che non corrisponde a uno di questi è un errore.
MODELLI_VISTO = [re.compile(x) for x in [
    r"^You can visit the Schengen area \((?:including|and) [^)]+\) without a visa for up to 90 days in any 180-day period(?:, for the reasons listed in the FCDO text)?$",
    r"^You can visit .+ without a visa for (?:up to )?(?:\d+|one) (?:days?|months?|years?)(?: in any \d+-(?:day|month) period| in a \d+-(?:day|month) period"
    r"| within a \d+-(?:day|month) period| in a year)?(?: for (?:tourism or business|business or tourism|tourism|business)| as a tourist)?"
    r"(?: \(for the reasons listed in the FCDO text\))?$",
    r"^You can visit .+ without a visa \(the FCDO text says how long you can stay\)$",
    r"^You need a visa to (?:visit|enter|enter or travel through|travel to) .+?(?: as a visitor| for tourism| for tourism or business)?(?: and you must apply in advance)?$",
    r"^You need a visa before you travel to .+$"]]
SENZA_VISTO_VIETATO = re.compile(r"\b(?:ETA|eTA|ESTA|NZeTA|ETIAS)\b|travel authori[sz]ation|electronic travel|entry fee|administration fee|tourist card"
                                 r"|embarkation card|approval to travel|e-travel|form online before", re.I)
# "serve un visto" solo se il visto non è un'autorizzazione elettronica (ETA, eVisitor): altrimenti solo la citazione
VISTO_ELETTRONICO_VIETATO = re.compile(r"\b(?:ETA|eTA|ESTA|NZeTA|ETIAS)\b|eVisitor|electronic visitor visa|electronic travel authori[sz]ation", re.I)


def controlla_visti():
    errori = []
    con, solo, senza = 0, 0, 0
    for p in G.PAESI:
        V = p.get("visto")
        if V is None:
            errori.append(f"visti {p['slug']}: dati del visto mancanti (rilanciare raccolta/passaporti.py)")
            continue
        t = leggi(f"passport-validity/{p['slug']}/index.html")
        if f"Do I need a visa for {escape(p['nome'])} with a British passport?" not in t:
            errori.append(f"visti {p['slug']}: domanda sul visto mancante")
        schema, sintesi, frase, _ = RP.sintesi_visto(V["testo"], p["nome"], p["slug"])
        if (schema, sintesi, frase) != (V["schema"], V["sintesi"], V["frase"]):
            errori.append(f"visti {p['slug']}: il riassunto salvato non è quello che dà lo schema sul testo salvato")
        for b in V["testo"]:
            if escape(b["x"]) not in t:
                errori.append(f"visti {p['slug']}: testo ufficiale mancante: {b['x'][:60]}")
        if not V["testo"]:
            senza += 1
            if "had no “Visa requirements” section" not in t or "In short:" in t:
                errori.append(f"visti {p['slug']}: manca l'avviso 'nessuna sezione visti' o c'è un riassunto")
            continue
        if escape(p["url_ingresso"]) not in t:
            errori.append(f"visti {p['slug']}: fonte GOV.UK mancante")
        if not V["sintesi"]:
            solo += 1
            if "In short:" in t:
                errori.append(f"visti {p['slug']}: riassunto mostrato senza schema riconosciuto")
            continue
        con += 1
        if not any(m.match(V["sintesi"]) for m in MODELLI_VISTO):
            errori.append(f"visti {p['slug']}: riassunto fuori dai modelli fissi: {V['sintesi']}")
        if not V["frase"] or not V["testo"][0]["x"].startswith(V["frase"]):
            errori.append(f"visti {p['slug']}: la frase di partenza non è l'inizio del testo ufficiale")
        for num in re.findall(r"\b(\d+|one)\b", V["sintesi"]):
            if not re.search(r"\b" + num + r"\b", V["frase"] or ""):
                errori.append(f"visti {p['slug']}: il numero {num} del riassunto non è nella frase ufficiale")
        if V["sintesi"].startswith("You can visit") and SENZA_VISTO_VIETATO.search(" ".join(b["x"] for b in V["testo"])):
            errori.append(f"visti {p['slug']}: 'senza visto' ma il testo parla di autorizzazione, tassa o tessera")
        if V["sintesi"].startswith("You need a visa") and VISTO_ELETTRONICO_VIETATO.search(" ".join(b["x"] for b in V["testo"])):
            errori.append(f"visti {p['slug']}: 'serve un visto' ma il testo parla di ETA o visto elettronico")
        if V["schema"] == "schengen" and 'href="../../ees-etias/"' not in t.split('id="visa"')[1].split("Official source:")[0]:
            errori.append(f"visti {p['slug']}: pagina Schengen senza il rimando a EES/ETIAS nella sezione visti")
        if f"In short: <strong>{escape(V['sintesi'])}.</strong>" not in t:
            errori.append(f"visti {p['slug']}: riassunto non mostrato nella pagina")
    return errori, (con, solo, senza)


class LD(HTMLParser):
    def __init__(self):
        super().__init__()
        self.dentro, self.blocchi, self.h3 = False, [], 0

    def handle_starttag(self, tag, attrs):
        if tag == "script" and ("type", "application/ld+json") in attrs:
            self.dentro = True
            self.blocchi.append("")

    def handle_endtag(self, tag):
        if tag == "script":
            self.dentro = False

    def handle_data(self, data):
        if self.dentro:
            self.blocchi[-1] += data


def citazioni_faq(testo, ammesse):
    """Scompone '“a” “b”' in citazioni ammesse (intere); None se resta testo che non è una citazione ufficiale."""
    if not testo:
        return []
    for q in sorted(ammesse, key=len, reverse=True):
        pezzo = f"“{q}”"
        if testo.startswith(pezzo):
            resto = testo[len(pezzo):]
            if resto.startswith(" ") or not resto:
                dopo = citazioni_faq(resto[1:] if resto else "", ammesse)
                if dopo is not None:
                    return [q] + dopo
    return None


def _blocchi_faq(testo):
    """Scompone una risposta FAQ dei liquidi in (testo nostro, [(fonte, data, testo citato)]):
    'frase nostra Quoted from F (checked on D): “a” “b” Quoted from G (checked on D2): “c”'. None se la forma non è questa."""
    parti = re.split(r"(?:^| )Quoted from ", testo)
    blocchi = []
    for p in parti[1:]:
        m = re.match(r"(.+?) \(checked on ([^)]+)\): (.*)$", p, re.S)
        if not m:
            return None
        blocchi.append((m.group(1), m.group(2), m.group(3)))
    return parti[0], blocchi


# Modelli fissi delle frasi nostre nelle FAQ dei liquidi (quando la pagina ufficiale non dice il dettaglio): nessun numero, nessuna regola inventata.
MODELLI_FAQ_LIQ = [re.compile(x) for x in [
    r"^The passages we quote from the official page do not say whether .+ uses CT scanners or whether liquids can stay in your bag: follow the signs and the staff at the checkpoint\.$",
    r"^The passages we quote from the official page do not (?:mention a plastic bag or a limit on the number of bags|list exemptions for baby food or medicines"
    r"|cover duty-free liquids bought at another airport)\. (?:GOV\.UK sets out the standard rule and exemptions for UK airports on its hand luggage "
    r"restrictions page; |Your Europe sets out the standard EU rule and exemptions; )?[Cc]heck with the airport and your airline before you pack\.$",
    # 5/11/2026: nota fissa quando la risposta cita anche la seconda fonte ufficiale (Dubrovnik, notizia sugli scanner)
    r"^The second source quoted below does not mention any change to the liquids limit on the official page quoted first\.$"]]


def controlla_liquidi_nuovi():
    """9. Liquidi: risposta diretta in alto (regola + sintesi del file, più la frase diretta); FAQ (JSON-LD FAQPage = testo visibile) da 4 a 6 domande,
    ogni risposta fatta di citazioni ufficiali intere (pagina dell'aeroporto, o GOV.UK / Your Europe dove la pagina non dice il dettaglio) e/o di una
    frase nostra che è SOLO regola + sintesi del file (prima e ultima domanda) o uno dei modelli fissi che dichiarano che la pagina non lo dice."""
    errori, n_faq, n_cit, n_nostre = [], 0, 0, 0
    contesto = {C["titolo"]: C for C in G.AER["contesto"]}
    for a in G.AER["aeroporti"] + G.AER["nazionali"]:
        t = leggi(f"liquids/{a['slug']}/index.html")
        naz = a in G.AER["nazionali"]
        # risposta diretta: sì/no dalla regola (o la sfumatura scritta nel file), più la sintesi del file
        attesa = (a.get("risposta") or {"2l": "Yes", "100ml": "No", "dipende": "It depends", "contraddice": "Not clear"}[a["regola"]])
        m = re.search(r"Can I take liquids over 100 ml through security at [^<]+\? <strong>([^<]+)", t)
        if not m or not m.group(1).startswith(escape(attesa)) or escape(a["sintesi"]) not in m.group(1):
            errori.append(f"liquidi {a['slug']}: risposta diretta in alto mancante o diversa dalla regola")
        if a.get("risposta") and a["regola"] in ("2l", "100ml") and not a["risposta"].startswith({"2l": "Yes", "100ml": "No"}[a["regola"]]):
            errori.append(f"liquidi {a['slug']}: 'risposta' in contrasto con la regola")
        # frase diretta (1-2 frasi) subito sotto: parte dalla risposta e contiene la sintesi del file, senza altri numeri
        md = re.search(r'<p class="lead">([^<]+)</p>', t)
        lead = md.group(1) if md else ""
        from html import unescape
        if not lead.startswith(escape(attesa)) or escape(a["sintesi"][1:]) not in lead or \
                set(re.findall(r"\d[\d,.]*", unescape(lead))) - set(re.findall(r"\d[\d,.]*", a["sintesi"] + " " + attesa)) - {"100"}:
            errori.append(f"liquidi {a['slug']}: frase diretta mancante, diversa dalla regola o con numeri non presenti nella sintesi")
        ammesse = list(a["citazioni"]) + list(a.get("eccezioni", []))
        K = a.get("contrasto")
        if a["regola"] == "contraddice" and K and K.get("url") == a["url"]:
            ammesse.append(K["citazione"])
        p = LD()
        p.feed(t)
        faq = [json.loads(x) for x in p.blocchi if '"FAQPage"' in x]
        if len(faq) != 1:
            errori.append(f"liquidi {a['slug']}: JSON-LD FAQPage assente o doppio")
            continue
        voci = faq[0]["mainEntity"]
        if not 4 <= len(voci) <= 6 or t.count("<h3>") < len(voci):
            errori.append(f"liquidi {a['slug']}: numero di domande FAQ sbagliato ({len(voci)})")
        data_a = G.data_lunga(a["controllato_il"])
        prima, ultima = f"{attesa if not a.get('risposta') else a['risposta']}. {a['sintesi']}." if not a.get("risposta") else f"{a['risposta']}. {a['sintesi']}.", None
        prima = f"{a.get('risposta') or {'2l': 'Yes', '100ml': 'No', 'dipende': 'It depends on the checkpoint', 'contraddice': 'Not clear: the official texts disagree'}[a['regola']]}. {a['sintesi']}."
        ultima = (f"As of {data_a}, the official page says: {prima} Rules can change at short notice and the airport's page is our only source, "
                  f"so check it again before you fly.")
        for i, v in enumerate(voci):
            n_faq += 1
            q, testo = v["name"], v["acceptedAnswer"]["text"]
            if escape(q) not in t:
                errori.append(f"liquidi {a['slug']}: domanda FAQ non visibile nella pagina: {q}")
                continue
            seg = t.split(f"<h3>{escape(q)}</h3>", 1)[1].split("<h3>", 1)[0]
            sc = _blocchi_faq(testo)
            if sc is None:
                errori.append(f"liquidi {a['slug']}: risposta FAQ senza la forma 'Quoted from <fonte> (checked on <data>)': {q}")
                continue
            intro, blocchi = sc
            if i == 0 and intro != prima:
                errori.append(f"liquidi {a['slug']}: la prima risposta FAQ non parte da regola + sintesi: {intro[:80]}")
            elif i == len(voci) - 1 and intro != ultima:
                errori.append(f"liquidi {a['slug']}: l'ultima risposta FAQ non è regola + sintesi + avviso: {intro[:80]}")
            elif 0 < i < len(voci) - 1 and intro and (not any(r.match(intro) for r in MODELLI_FAQ_LIQ) or re.search(r"\d", intro)):
                errori.append(f"liquidi {a['slug']}: frase nostra fuori dai modelli fissi (o con numeri) nella FAQ: {intro[:80]}")
            if intro:
                n_nostre += 1
                if f"<p>{escape(intro)}</p>" not in seg:
                    errori.append(f"liquidi {a['slug']}: frase nostra della FAQ non visibile: {q}")
            if not intro and not blocchi:
                errori.append(f"liquidi {a['slug']}: risposta FAQ vuota: {q}")
            for fonte, data, cit in blocchi:
                if fonte == a["titolo_fonte"] and data == data_a:
                    pool = ammesse
                elif a.get("fonte2") and fonte == a["fonte2"]["titolo"] and data == data_a:  # seconda pagina ufficiale (dal 5/11/2026)
                    pool = a["fonte2"]["citazioni"]
                    if escape(f"Quoted from {fonte} (checked on {data}).") not in seg:
                        errori.append(f"liquidi {a['slug']}: seconda fonte non indicata sotto la citazione: {q}")
                elif fonte in contesto and data == G.data_lunga(contesto[fonte]["controllato_il"]):
                    C = contesto[fonte]
                    pool = C["citazioni"]
                    if (C["id"] == "uk" and a.get("paese") != "United Kingdom") or (C["id"] == "eu" and a.get("paese") not in G.PAESI_UE):
                        errori.append(f"liquidi {a['slug']}: citata la pagina di governo sbagliata ({C['id']}) per {a.get('paese')}")
                    if escape(f"Quoted from {fonte} (checked on {data}).") not in seg:
                        errori.append(f"liquidi {a['slug']}: fonte di governo non indicata sotto la citazione: {q}")
                else:
                    errori.append(f"liquidi {a['slug']}: risposta FAQ con fonte o data sconosciuta: {fonte} / {data}")
                    continue
                cc = citazioni_faq(cit, pool)
                if not cc:
                    errori.append(f"liquidi {a['slug']}: risposta FAQ con testo non citato dalla pagina ufficiale: {cit[:80]}")
                    continue
                n_cit += 1
                if ("<blockquote class=\"cit\">" + "".join(f"<p>{escape(x)}</p>" for x in cc) + "</blockquote>") not in seg:
                    errori.append(f"liquidi {a['slug']}: citazioni della FAQ visibili diverse dal JSON-LD: {q}")
        if not naz:
            altri = [b for b in G.AER["aeroporti"] if b is not a and b["paese"] == a["paese"]]
            for b in altri:
                if f'href="../../liquids/{b["slug"]}/"' not in t:
                    errori.append(f"liquidi {a['slug']}: manca il collegamento a {b['slug']} (stesso Paese)")
    return errori, (n_faq, n_cit, n_nostre)


# ---------------------------------------------------------------- 14. liquidi del 21/10/2026: titoli con la regola, FAQ JSON-LD valide, aeroporti nuovi, riquadro nelle pagine compagnie
NUOVI_LIQ_2110 = ["london-city", "liverpool", "newcastle", "leeds-bradford", "belfast-international", "cardiff", "southampton", "exeter", "bournemouth", "cork", "jersey"]
ESCLUSI_LIQ_2110 = ["Birmingham", "Glasgow", "Belfast City"]


def _faq_ld_valida(x):
    """Struttura schema.org FAQPage: @context, @type, mainEntity di Question con name e acceptedAnswer Answer con text non vuoto."""
    if x.get("@context") != "https://schema.org" or x.get("@type") != "FAQPage" or not isinstance(x.get("mainEntity"), list) or not x["mainEntity"]:
        return False
    for q in x["mainEntity"]:
        if q.get("@type") != "Question" or not q.get("name", "").strip() or not isinstance(q.get("acceptedAnswer"), dict):
            return False
        r = q["acceptedAnswer"]
        if r.get("@type") != "Answer" or not isinstance(r.get("text"), str) or not r["text"].strip():
            return False
    return True


def controlla_liquidi_2110():
    errori, conti = [], {"faq_ld": 0, "nuovi": 0, "compagnie": 0}
    from html import unescape
    # a) ogni blocco FAQPage del sito è JSON valido e ben formato (schema.org)
    for f in SITO.rglob("*.html"):
        t = f.read_text(encoding="utf-8")
        for blocco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
            try:
                x = json.loads(blocco)
            except ValueError:
                errori.append(f"JSON-LD non valido in {f.relative_to(SITO)}")
                continue
            if x.get("@type") == "FAQPage":
                conti["faq_ld"] += 1
                if not _faq_ld_valida(x):
                    errori.append(f"FAQPage mal formata in {f.relative_to(SITO)}")
    # b) titolo e H1 con la regola vera dell'aeroporto e le parole cercate ("liquid rules 2026", sigla, "100ml", "hand luggage")
    for a in G.AER["aeroporti"]:
        t = leggi(f"liquids/{a['slug']}/index.html")
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        h1 = unescape(re.search(r"<h1>(.*?)</h1>", t, re.S).group(1))
        atteso = {"2l": ("2 Litres", "2 litres"), "100ml": ("100ml Limit", "100ml limit"), "dipende": ("by Checkpoint", "depending on the checkpoint"),
                  "contraddice": ("Pages Disagree", "pages disagree")}[a["regola"]]
        if a.get("etichetta", "").lower() == "depends on journey":
            atteso = ("by Journey", "depending on the journey")
        if f"({a['iata']}) Liquid Rules {G.ANNO}" not in tit or (atteso[0] not in tit and not tit.endswith(f"Liquid Rules {G.ANNO}")):
            errori.append(f"liquidi {a['slug']}: titolo senza sigla, 'Liquid Rules {G.ANNO}' o regola: {tit}")
        if f"({a['iata']}) liquid rules {G.ANNO}:" not in h1 or atteso[1] not in h1 or "hand luggage" not in h1:
            errori.append(f"liquidi {a['slug']}: H1 senza sigla, 'liquid rules {G.ANNO}', regola o 'hand luggage': {h1}")
        if a["regola"] == "100ml" and ("2 Litres" in tit or "2 litres" in h1):
            errori.append(f"liquidi {a['slug']}: titolo o H1 promettono 2 litri con regola 100 ml")
        if '<h2>100ml rule at ' not in t:
            errori.append(f"liquidi {a['slug']}: manca il sottotitolo '100ml rule at'")
    # c) aeroporti nuovi del 21/10/2026: nei dati con data e citazioni, nell'indice, con pagina; gli esclusi con il motivo; nessun incluso tra gli esclusi
    idx = leggi("liquids/index.html")
    per_slug = {a["slug"]: a for a in G.AER["aeroporti"]}
    for s in NUOVI_LIQ_2110:
        a = per_slug.get(s)
        if not a or a["controllato_il"] != "2026-10-21" or not a["citazioni"] or not a["url"].startswith("https://"):
            errori.append(f"liquidi nuovo {s}: manca nei dati, data diversa dal 21/10/2026, senza citazioni o URL non https")
            continue
        conti["nuovi"] += 1
        if not (SITO / "liquids" / s / "index.html").exists():
            errori.append(f"liquidi nuovo {s}: pagina mancante")
        if f'href="../liquids/{s}/"' not in idx or f'href="{escape(a["url"])}"' not in idx:
            errori.append(f"liquidi nuovo {s}: manca nell'indice (riga o fonte)")
        if a["area"] != "UK and Ireland":
            errori.append(f"liquidi nuovo {s}: area diversa da 'UK and Ireland'")
    nomi_esclusi = [e["nome"] for e in G.AER["esclusi"]]
    for n in ESCLUSI_LIQ_2110:
        if not any(n in x for x in nomi_esclusi) or n not in idx:
            errori.append(f"liquidi: {n} deve restare tra gli esclusi con il motivo, anche nell'indice")
    for a in G.AER["aeroporti"]:
        if any(a["nome"] == e["nome"] or a["nome"] in e["nome"].split(", ") for e in G.AER["esclusi"]):
            errori.append(f"liquidi: {a['nome']} è incluso ma compare anche tra gli esclusi")
    if "Jersey (JER)" not in leggi("liquids/heathrow/index.html") and 'href="../../liquids/heathrow/"' not in leggi("liquids/jersey/index.html"):
        errori.append("liquidi: la pagina di Jersey (unico aeroporto del suo Paese) non rimanda agli altri aeroporti della stessa area")
    # d) riquadro sui liquidi in ogni pagina compagnia: regola generale citata da GOV.UK, link all'indice dei liquidi, una sola FAQPage
    gov = next(C for C in G.AER["contesto"] if C["id"] == "uk")
    for C in G.COMPAGNIE:
        t = leggi(f"{G.BAG_BASE}/{C['slug']}/index.html")
        if 'aria-label="Liquids in hand luggage"' not in t or f'href="../../liquids/"' not in t or escape(gov["citazioni"][0]) not in t or escape(gov["url"]) not in t:
            errori.append(f"bagagli {C['slug']}: riquadro sui liquidi mancante o senza citazione GOV.UK / link all'indice")
        elif t.count('"FAQPage"') != 1:
            errori.append(f"bagagli {C['slug']}: numero di FAQPage diverso da 1")
        else:
            conti["compagnie"] += 1
    return errori, conti


# ---------------------------------------------------------------- 30. liquidi del 5/11/2026: 37 aeroporti nuovi e riquadri di guadagno
NUOVI_LIQ_0511 = {  # slug: (sigla, regola), scritti qui a mano dalla lettura del 5/11/2026
    "valencia": ("VLC", "100ml"), "seville": ("SVQ", "100ml"), "reus": ("REU", "100ml"), "murcia": ("RMU", "100ml"), "almeria": ("LEI", "100ml"),
    "la-palma": ("SPC", "100ml"), "bilbao": ("BIO", "100ml"), "girona": ("GRO", "100ml"), "tenerife-north": ("TFN", "100ml"),
    "santiago-de-compostela": ("SCQ", "100ml"), "jerez": ("XRY", "100ml"), "granada": ("GRX", "100ml"),
    "thessaloniki": ("SKG", "100ml"), "corfu": ("CFU", "100ml"), "chania": ("CHQ", "100ml"), "kefalonia": ("EFL", "100ml"), "zakynthos": ("ZTH", "100ml"),
    "rhodes": ("RHO", "100ml"), "kos": ("KGS", "100ml"), "mykonos": ("JMK", "100ml"), "santorini": ("JTR", "100ml"), "preveza-aktion": ("PVK", "100ml"),
    "kavala": ("KVA", "100ml"), "mytilene": ("MJT", "100ml"), "samos": ("SMI", "100ml"), "skiathos": ("JSI", "100ml"),
    "milan-bergamo": ("BGY", "2l"), "bologna": ("BLQ", "2l"), "dubrovnik": ("DBV", "100ml"), "zadar": ("ZAD", "100ml"), "antalya": ("AYT", "100ml"),
    "keflavik": ("KEF", "100ml"), "inverness": ("INV", "100ml"), "glasgow-prestwick": ("PIK", "100ml"), "teesside": ("MME", "100ml"),
    "guernsey": ("GCI", "100ml"), "knock": ("NOC", "2l")}
ESCLUSI_LIQ_0511 = ["Larnaca", "Paphos", "Naples", "Venice", "Palermo", "Catania", "Pisa", "Ponta Delgada (Azores)", "Cagliari", "Olbia", "Turin",
                    "Rotterdam The Hague", "Norwich", "Heraklion", "Split", "Dalaman", "Bodrum"]
# Paesi dove chi legge arriva in vacanza (riquadri di guadagno); in Türkiye solo Antalya (Istanbul è uno scalo di transito)
PAESI_VACANZA_LIQ = {"Spain", "Portugal", "Italy", "Greece", "Malta", "Croatia", "Iceland", "Cyprus"}
SOLO_AEROPORTI_VACANZA_LIQ = {"antalya"}
PARTENZA_LIQ = {"United Kingdom", "Ireland", "Jersey", "Guernsey", "United States", "Canada"}


def LIQ_VACANZA_PAGINE():
    """Pagine liquidi che devono avere il riquadro "Hire a car": ricalcolate qui dal Paese, non dall'elenco di affiliati.json."""
    if not G.NOLEGGIO_AUTO:
        return set()
    return {f"liquids/{a['slug']}/index.html" for a in G.AER["aeroporti"]
            if (a["paese"] in PAESI_VACANZA_LIQ or a["slug"] in SOLO_AEROPORTI_VACANZA_LIQ) and a["area"] != "UK and Ireland"}


def controlla_liquidi_0511():
    from html import unescape
    errori, conti = [], {"nuovi": 0, "noleggio": 0, "stay22": 0, "senza": 0}
    per_slug = {a["slug"]: a for a in G.AER["aeroporti"]}
    dom = json.loads((SITO.parent / "dati" / "liquidi_domanda.json").read_text(encoding="utf-8"))["aeroporti"]
    idx, sm = leggi("liquids/index.html"), leggi("sitemap.xml")
    # a) aeroporti nuovi: dati, pagina, indice, sitemap, titolo da una ricerca vera, fonte in alto con la risposta
    if set(dom) != set(NUOVI_LIQ_0511):
        errori.append(f"liquidi_domanda.json: aeroporti diversi dai 37 attesi: {sorted(set(dom) ^ set(NUOVI_LIQ_0511))}")
    for s_, (iata, regola) in NUOVI_LIQ_0511.items():
        a = per_slug.get(s_)
        if not a or a["iata"] != iata or a["regola"] != regola:
            errori.append(f"liquidi nuovo {s_}: manca nei dati o sigla/regola diversa da {iata}/{regola}")
            continue
        if a["controllato_il"] != "2026-11-05" or a.get("lettura") != "diretta" or a.get("http") != 200 or not re.fullmatch(r"[0-9a-f]{16}", a.get("impronta", "")) \
                or not a["url"].startswith("https://") or not a["citazioni"]:
            errori.append(f"liquidi nuovo {s_}: data, lettura diretta, HTTP 200, impronta, URL https o citazioni mancanti")
        rel = f"liquids/{s_}/index.html"
        if not (SITO / rel).exists():
            errori.append(f"liquidi nuovo {s_}: pagina mancante")
            continue
        conti["nuovi"] += 1
        t = leggi(rel)
        if f'href="../liquids/{s_}/"' not in idx or f'href="{escape(a["url"])}"' not in idx or f"<loc>{G.URL_SITO}/liquids/{s_}/</loc>" not in sm:
            errori.append(f"liquidi nuovo {s_}: manca nell'indice (riga o fonte) o nella sitemap")
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        nome_t = tit.split(" Airport (")[0].split(f" ({iata})")[0]
        sugg = dom.get(s_, {}).get("uk", []) + dom.get(s_, {}).get("us", [])
        if len(tit) > 70 or str(G.ANNO) not in tit or f"({iata})" not in tit:
            errori.append(f"liquidi nuovo {s_}: titolo oltre 70 caratteri, senza l'anno o senza la sigla: {tit}")
        if not any(x.startswith(nome_t.lower() + " airport liquid") for x in sugg):
            errori.append(f"liquidi nuovo {s_}: il nome del titolo «{nome_t}» non viene da una ricerca vera «… airport liquid…»")
        som = t.split('<section class="card summary"', 1)[-1].split("</section>", 1)[0]
        if "Can I take liquids over 100 ml through security at" not in som or f'Official source: <a href="{escape(a["url"])}"' not in som:
            errori.append(f"liquidi nuovo {s_}: la risposta in alto non ha accanto la fonte ufficiale")
        gruppo = {"aena": "Aena's general hand-luggage page", "hial": "the security page of HIAL"}.get(a.get("gestore"))
        if gruppo and escape(gruppo) not in som:
            errori.append(f"liquidi nuovo {s_}: la frase in alto non dice che la fonte è una pagina di gruppo ({a.get('gestore')})")
        if a.get("gestore") == "fraport-greece" and "open with a click" not in a.get("nota", ""):
            errori.append(f"liquidi nuovo {s_}: la nota non dice che il testo ufficiale si apre con un clic")
        if a.get("fonte2") and (escape(a["fonte2"]["url"]) not in t or not re.fullmatch(r"[0-9a-f]{16}", a["fonte2"].get("impronta", ""))):
            errori.append(f"liquidi nuovo {s_}: seconda fonte senza link nella pagina o senza impronta")
    # esclusi: un nome una volta sola, mai il nome di un aeroporto incluso (revisione del 5/11/2026: Bologna, Napoli)
    nomi_e = [n for e in G.AER["esclusi"] for n in e["nome"].split(", ")]
    if len(nomi_e) != len(set(nomi_e)):
        errori.append(f"liquidi: nomi ripetuti tra gli esclusi: {sorted({n for n in nomi_e if nomi_e.count(n) > 1})}")
    for a in G.AER["aeroporti"]:
        if G.nome_titolo(a) in nomi_e or a["nome"] in nomi_e:
            errori.append(f"liquidi: {a['nome']} è incluso ma il suo nome è tra gli esclusi")
    # le 23 pagine Aena: stessa pagina, stessa data, lettura diretta, stessa impronta, stessa nota (con la pagina dell'aeroporto su aena.es)
    aena = [a for a in G.AER["aeroporti"] if a.get("gestore") == "aena"]
    if len(aena) != 23 or len({(a["url"], a["controllato_il"], a.get("lettura"), a.get("impronta")) for a in aena}) != 1 or \
            any(a.get("pagina_gestore", "").split("/")[-1] not in a.get("nota", "") or "is one of the airports Aena lists" not in a.get("nota", "") for a in aena):
        errori.append("liquidi: le pagine Aena non hanno tutte la stessa fonte, data, lettura, impronta e nota")
    for n in ESCLUSI_LIQ_0511:
        if not any(n in e["nome"].split(", ") for e in G.AER["esclusi"]) or escape(n) not in idx:
            errori.append(f"liquidi: {n} (non letto il 5/11/2026) deve stare tra gli esclusi con il motivo, anche nell'indice")
    # b) riquadri di guadagno: noleggio esattamente sugli aeroporti di vacanza, Stay22 solo dove previsto, mai su partenza/transito
    vac = LIQ_VACANZA_PAGINE()
    attesi_s22 = {f"liquids/{x}/index.html": STAY22_ATTESI[k] for x, k in STAY22_LIQ.items()} if G.STAY22_BIG and G.NOLEGGIO_AUTO else {}
    for a in G.AER["aeroporti"] + G.AER["nazionali"]:
        rel = f"liquids/{a['slug']}/index.html"
        t = leggi(rel)
        voci = G.MON.link_affiliati(t)
        dc = [(h, r) for h, host, r in voci if G.MON.dominio_in(host, ["discovercars.com"])]
        s22 = [(h, r) for h, host, r in voci if G.MON.dominio_in(host, ["stay22.com"])]
        if rel not in vac:
            if dc or s22 or "data-noleggio" in t or "data-alloggio" in t:
                errori.append(f"{rel}: riquadro di guadagno su un aeroporto che non è di vacanza ({a.get('paese')})")
            if a.get("area") == "UK and Ireland" or a.get("paese") in PARTENZA_LIQ or a in G.AER["nazionali"]:
                conti["senza"] += 1
            continue
        if a.get("area") == "UK and Ireland" or a.get("paese") in PARTENZA_LIQ:
            errori.append(f"{rel}: aeroporto di partenza tra quelli di vacanza")
        # noleggio
        if len(dc) != 1:
            errori.append(f"{rel}: attesi 1 link DiscoverCars, trovati {len(dc)}")
            continue
        href, r = dc[0]
        if not link_noleggio_ok(href) or href != G.NOLEGGIO_AUTO:
            errori.append(f"{rel}: link di noleggio diverso dal link generale DiscoverCars con a_aid={NOLEGGIO_AID}: {href}")
        if not {"sponsored", "noopener"} <= r:
            errori.append(f"{rel}: link DiscoverCars senza rel=\"sponsored noopener\"")
        tag = re.search(r'<a\b[^>]*href="' + re.escape(escape(href)) + r'"[^>]*>', t)
        if not tag or 'target="_blank"' not in tag.group(0):
            errori.append(f"{rel}: link DiscoverCars senza target=\"_blank\"")
        i = t.find("data-noleggio")
        blocco = t[i:t.find("</section>", i)] if i >= 0 else ""
        if i < 0 or escape(href) not in blocco or G.MON.RIGA_EN not in blocco:
            errori.append(f"{rel}: link DiscoverCars fuori dal riquadro o riga di trasparenza mancante nel riquadro")
        if f'<h2 id="hire-a-car">Hire a car at {escape(a["nome"])} Airport</h2>' not in t:
            errori.append(f"{rel}: titolo del riquadro diverso da 'Hire a car at {a['nome']} Airport'")
        prima = ['<p class="cifra">Can I take liquids over 100 ml', "<h2>100ml rule at "] + [escape(q) for q in a["citazioni"] + a.get("eccezioni", [])]
        prima += [escape(a["contrasto"]["citazione"])] if a.get("contrasto") else []
        prima += [escape(q) for q in (a.get("fonte2") or {}).get("citazioni", [])]
        for x in prima:
            j = t.find(x)
            if j < 0 or j > i:
                errori.append(f"{rel}: riquadro noleggio non dopo «{unescape(x)[:50]}»")
        if 0 <= t.find('<section class="faq"') < i:
            errori.append(f"{rel}: riquadro noleggio dopo le FAQ (deve stare subito dopo la regola ufficiale)")
        if re.search(r"cheapest|best price|lowest price|guaranteed|book now", unescape(blocco), re.I):
            errori.append(f"{rel}: promessa di prezzo nel riquadro noleggio")
        conti["noleggio"] += 1
        # Stay22
        att = attesi_s22.get(rel)
        if not att:
            if s22 or "data-alloggio" in t:
                errori.append(f"{rel}: riquadro Stay22 dove non c'è un link della stessa città")
            continue
        if [h for h, _ in s22] != [att]:
            errori.append(f"{rel}: link Stay22 {[h for h, _ in s22]} invece di {att}")
            continue
        h, r = s22[0]
        k = t.find("data-alloggio")
        b2 = t[k:t.find("</section>", k)] if k >= 0 else ""
        tag = re.search(r'<a\b[^>]*href="' + re.escape(escape(h)) + r'"[^>]*>', t)
        citta = next(v["citta"] for x, v in G.STAY22_BIG.items() if v["url"] == att)
        if not {"sponsored", "noopener"} <= r or not tag or 'target="_blank"' not in tag.group(0):
            errori.append(f"{rel}: link Stay22 senza rel=\"sponsored noopener\" o target=\"_blank\"")
        if k < i or escape(h) not in b2 or G.MON.RIGA_EN not in b2 or '<span class="aff-tag">Affiliate</span>' not in t[t.rfind("<h2", 0, k):k]:
            errori.append(f"{rel}: riquadro Stay22 prima del noleggio, senza trasparenza o senza l'etichetta Affiliate")
        if citta != a["citta"] or f"hotels across {escape(citta)}" not in b2:
            errori.append(f"{rel}: il riquadro Stay22 non è della città dell'aeroporto ({citta} / {a['citta']})")
        if re.search(r"cheapest|best price|lowest price|guaranteed|available now|book now", unescape(b2), re.I):
            errori.append(f"{rel}: promessa di prezzo o disponibilità nel riquadro Stay22")
        conti["stay22"] += 1
    if G.NOLEGGIO_AUTO and set(f"liquids/{x}/index.html" for x in G.NOLEGGIO_LIQ) != vac:
        errori.append(f"affiliati.json, _discovercars_noleggio.liquidi diverso dagli aeroporti di vacanza ricalcolati: "
                      f"{sorted(set(f'liquids/{x}/index.html' for x in G.NOLEGGIO_LIQ) ^ vac)}")
    if G.STAY22_BIG and G.ALLOGGI_LIQ != STAY22_LIQ:
        errori.append(f"affiliati.json, _stay22_alloggi.liquidi diverso da quello atteso: {G.ALLOGGI_LIQ}")
    return errori, conti


def controlla_meta():
    errori, lunghi = [], []
    attesi = {f"passport-validity/{p['slug']}/index.html": G.titoli_passaporto(p) for p in G.PAESI}
    attesi.update({f"liquids/{a['slug']}/index.html": G.titoli_liquidi(a) for a in G.AER["aeroporti"]})
    attesi.update({f"liquids/{a['slug']}/index.html": G.titoli_liquidi(a, True) for a in G.AER["nazionali"]})
    for k in G.ESTERI:
        attesi.update({v["url_pag"] + "index.html": G.titoli_estero(v) for v in G.VOCI[k]})
    attesi.update({f"{G.BAG_BASE}/{C['slug']}/index.html": G.titoli_bag(C) for C in G.COMPAGNIE})
    attesi.update({f"{G.BAG_BASE}/size/{sl}/index.html": G.titoli_misura(sl) for sl, _ in G.MISURE_COMUNI})
    attesi.update({v["url_pag"] + "index.html": G.titoli_it(v) for v in G.VOCI_IT})
    attesi.update({G.url_srv(S, c) + "index.html": G.titoli_srv(S, c) for S in G.SERVIZI_SRV for c in G.pagine_srv(S)})
    pat = {G.url_pat(k, c) + "index.html": G.titoli_pat(k, c) for k in G.PATENTI for c in G.PAGINE_PAT[k]}
    pat.update({G.url_pat(k) + "index.html": G.titoli_patente(k) for k in G.PATENTI})
    from html import unescape
    for f in SITO.rglob("*.html"):
        if f.name.startswith("google"):
            continue
        t = f.read_text(encoding="utf-8")
        rel = str(f.relative_to(SITO))
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        des = unescape(re.search(r'<meta name="description" content="(.*?)">', t).group(1))
        if len(des) > G.LIMITE_DESCRIZIONE:
            errori.append(f"descrizione di {len(des)} caratteri (> 160) in {rel}")
        if rel.startswith(G.GOM_BASE + "/"):  # sezione "Winter tyres with a rental car": fino a 70 caratteri con la stagione 2026-27 (il punto 21 controlla il resto)
            if len(tit) > G.LIMITE_TITOLO_GOM or G.STAGIONE_GOM not in tit:
                errori.append(f"titolo di {len(tit)} caratteri (> {G.LIMITE_TITOLO_GOM}) o senza la stagione in {rel}: {tit}")
            continue
        if rel.startswith(G.SC_BASE + "/"):  # sezione "Scooter rental: which licence?": fino a 70 caratteri con l'anno (il punto 28 controlla il resto)
            if len(tit) > G.LIMITE_TITOLO_SC or str(G.ANNO) not in tit:
                errori.append(f"titolo di {len(tit)} caratteri (> {G.LIMITE_TITOLO_SC}) o senza l'anno in {rel}: {tit}")
            continue
        if rel.startswith(G.BIG_BASE + "/"):  # sezione "When do tickets go on sale?": fino a 70 caratteri con gli anni 2026-27 (il punto 22 controlla il resto)
            if len(tit) > G.LIMITE_TITOLO_BIG or G.STAGIONE_BIG not in tit:
                errori.append(f"titolo di {len(tit)} caratteri (> {G.LIMITE_TITOLO_BIG}) o senza gli anni in {rel}: {tit}")
            continue
        if rel.startswith(G.TR_BASE + "/"):  # sezione "Public transport rules": fino a 70 caratteri con l'anno (il punto 24 controlla il resto)
            if len(tit) > G.LIMITE_TITOLO_TR or str(G.ANNO) not in tit:
                errori.append(f"titolo di {len(tit)} caratteri (> {G.LIMITE_TITOLO_TR}) o senza l'anno in {rel}: {tit}")
            continue
        if rel.startswith(G.TB_BASE + "/") or rel.startswith(G.TB_ES + "/"):  # bagagli sui treni e orari Eurostar: fino a 70 con l'anno (punto 25)
            if len(tit) > G.LIMITE_TITOLO_TB or str(G.ANNO) not in tit:
                errori.append(f"titolo di {len(tit)} caratteri (> {G.LIMITE_TITOLO_TB}) o senza l'anno in {rel}: {tit}")
            continue
        if rel.startswith(G.FL_BASE + "/"):  # sezione "Foreign licence in Canada, Australia and NZ": fino a 70 caratteri con l'anno (il punto 23 controlla il resto)
            if len(tit) > G.LIMITE_TITOLO_FL or str(G.ANNO) not in tit:
                errori.append(f"titolo di {len(tit)} caratteri (> {G.LIMITE_TITOLO_FL}) o senza l'anno in {rel}: {tit}")
            continue
        if rel.startswith(G.PET_BASE + "/"):  # sezione "Pets: from the UK to the EU": fino a 70 caratteri con l'anno (il punto 26 controlla il resto)
            if len(tit) > G.LIMITE_TITOLO_PET or str(G.ANNO) not in tit:
                errori.append(f"titolo di {len(tit)} caratteri (> {G.LIMITE_TITOLO_PET}) o senza l'anno in {rel}: {tit}")
            continue
        if rel.startswith((G.IN_BASE + "/", G.IN_VOA + "/", G.IN_ARR + "/")):  # sezione "India e-Visa fee": fino a 70 caratteri con l'anno (il punto 27 controlla il resto)
            if len(tit) > G.LIMITE_TITOLO_IN or str(G.ANNO) not in tit:
                errori.append(f"titolo di {len(tit)} caratteri (> {G.LIMITE_TITOLO_IN}) o senza l'anno in {rel}: {tit}")
            continue
        if rel.startswith(G.BB_BASE + "/"):  # sezione "Blue Badge abroad": fino a 70 caratteri con l'anno (il punto 29 controlla il resto)
            if len(tit) > G.LIMITE_TITOLO_BB or str(G.ANNO) not in tit:
                errori.append(f"titolo di {len(tit)} caratteri (> {G.LIMITE_TITOLO_BB}) o senza l'anno in {rel}: {tit}")
            continue
        if rel.startswith(G.PED_BASE + "/"):  # sezione "Tolls with a rental car": fino a 70 caratteri con l'anno (il punto 20 controlla il resto)
            if len(tit) > G.LIMITE_TITOLO_PED or str(G.ANNO) not in tit:
                errori.append(f"titolo di {len(tit)} caratteri (> {G.LIMITE_TITOLO_PED}) o senza l'anno in {rel}: {tit}")
            continue
        if rel in pat or rel == f"{G.PAT_BASE}/index.html":  # sezione "Driving abroad": titoli fino a 70 caratteri con l'anno
            if len(tit) > G.LIMITE_TITOLO_PAT or str(G.ANNO) not in tit:
                errori.append(f"titolo di {len(tit)} caratteri (> {G.LIMITE_TITOLO_PAT}) o senza l'anno in {rel}: {tit}")
            if rel in pat and tit != G.scegli(pat[rel], G.LIMITE_TITOLO_PAT):
                errori.append(f"titolo non scelto tra le forme previste in {rel}")
            continue
        if len(tit) > G.LIMITE_TITOLO:
            if rel in attesi and all(len(c) > G.LIMITE_TITOLO for c in attesi[rel]):
                lunghi.append(rel)
            else:
                errori.append(f"titolo di {len(tit)} caratteri (> 65) in {rel}: {tit}")
        if rel in attesi and tit != G.scegli(attesi[rel], G.LIMITE_TITOLO):
            errori.append(f"titolo non scelto tra le forme previste in {rel}")
    return errori, lunghi


# ---------------------------------------------------------------- 11. passaporti canadese e australiano
def _carica(nome):
    spec = importlib.util.spec_from_file_location(nome, Path(__file__).resolve().parent / "raccolta" / f"{nome}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


RCA = _carica("passaporti_ca")
RAU = _carica("passaporti_au")
CODA_VAL = r"(?:, and (?:be in good condition|(?:have|must contain|contain|include|should have) [^()]+))?(?: \(the official text adds more details\))?$"
MODELLI_VAL = {
    "ca": [re.compile(x + CODA_VAL) for x in [
        r"^Valid (?:for at least |at least |for a minimum of |a minimum of |for )?\d+ (?:months?|days?) beyond the date you expect to leave .+?",
        r"^Valid (?:for at least |at least |for a minimum of |a minimum of |for )?\d+ (?:months?|days?) from the date you enter(?: .+?)?",
        r"^Valid for (?:at least )?the (?:expected )?duration of your stay(?: in .+?)?",
        r"^Valid beyond the date you expect to leave .+?"]],
    "au": [re.compile(x) for x in [r"^Valid for (?:at least )?\d+ (?:months?|days?) (?:after the date you leave|from the date you arrive in) .+$",
                                   r"^At least \d+ (?:months?|days?) of validity remaining when you enter .+$"]],
}
ETIAS_CODA = r"(?:; ETIAS will be required, but “Applications are not yet open”, says the same page)?$"
MODELLI_VIS = {
    "ca": [re.compile(x + ETIAS_CODA) for x in [
        r"^Tourist visa not required for stays (?:of )?(?:up to a maximum of|up to|less than|fewer than) (?:\d+|six) (?:days|months|weeks)"
        r"(?: in any \d+-day period| in a \d+-day period| in a 180 day period| within any \d+-day period| within a \d+-day period"
        r"| within any 180-day period)?(?:, counted across the whole Schengen area)?",
        r"^Tourist visa not required for stays of \d+ (?:days|months) or less(?: in any \d+-day period)?",
        r"^Tourist visa not required \(read the official text for how long you can stay\)",
        r"^Tourist visa required"]],
    "au": [re.compile(x) for x in [r"^You don't need a visa to visit .+ for (?:up to |less than )?\d+ (?:days|months)(?: for tourism)?$",
                                   r"^(?:Tourists can visit|You can stay in) .+ for (?:up to )?\d+ (?:days|months) without a visa$",
                                   r"^Australian tourists can enter .+ without a visa for (?:up to )?\d+ (?:days|months)$",
                                   r"^You don't need a visa to visit .+ (?:for tourism|as a tourist) \(read the official text for how long you can stay\)$",
                                   r"^You need a visa (?:to (?:visit|enter|travel to)|before you enter) .+$"]],
}
# controllo indipendente (più largo di quello della raccolta): niente "senza visto" se il testo d'ingresso parla di autorizzazioni, visti elettronici,
# moduli o registrazioni prima del viaggio, tessere o tasse d'ingresso; niente "serve un visto" se il visto è elettronico o si ottiene all'arrivo
VIETATO_SENZA = re.compile(r"\b(?:ETA|eTA|ESTA|NZeTA|K-ETA|ETIAS|EVW)\b|eVisitor|travel authori[sz]ation|electronic authori[sz]ation|\be-?visa|electronic visa|arrival card|arrival declaration|e-arrival"
                           r"|declaration form|immigration form|embarkation|landing card|tourist card|migration card|ED card|entry fee|entry tax|tourism fee|tourist tax"
                           r"|pre-?regist|pre-?arrival|register online|online registration|e-?Travel|online form|QR code|online visa|visa online", re.I)
VIETATO_RICHIESTO = re.compile(r"\b(?:ETA|eTA|ESTA|NZeTA|K-ETA)\b|eVisitor|\be-?visa|electronic visa|electronic travel|online visa|visa online|on arrival|upon arrival|"
                               r"ports? of entry|points? of entry|at the airport", re.I)
PAROLE_NUM = {"six": "6", "three": "3", "one": "1", "two": "2"}


def _numeri_ok(sintesi, frase):
    f = frase or ""
    for k, v in PAROLE_NUM.items():
        f = re.sub(r"\b" + k + r"\b", v, f)
    return all(re.search(r"\b" + n + r"\b", f) for n in re.findall(r"\b(\d+)\b", sintesi) if n not in ("180",) or "180" in f)


def _sezioni_au(p):
    sez = {"Passport": p["passaporto"]["testo"], RAU.VISTI: p["visto"]["testo"]}
    for a in p.get("altre_sezioni", []):
        sez[a["titolo"]] = a["testo"]
    return sez


def controlla_esteri():
    errori, conti = [], {}
    for k, c in G.ESTERI.items():
        D = c["dati"]
        voci = G.VOCI[k]
        conti[k] = {"pagine": 0, "val": 0, "vis": 0, "val_cit": 0, "vis_cit": 0}
        if not D:
            continue
        if len(voci) < 0.8 * D["pagine_indice"]:
            errori.append(f"{k}: solo {len(voci)} pagine su {D['pagine_indice']} destinazioni della fonte")
        t_ind = leggi(f"{c['base']}/index.html")
        for v in voci:
            p = v["p"]
            P, V = p["passaporto"], p["visto"]
            conti[k]["pagine"] += 1
            # a) i riassunti salvati sono quelli che danno gli schemi sul testo salvato
            if k == "ca":
                ss = RCA.sezioni(p["ingresso"])
                rv = RCA.calcola_validita(P["testo"], P["titolo_sezione"], p["nome"], p["iso"], p.get("schengen", False))
                if (rv[0], rv[1], rv[2], rv[3]) != (P["schema"], P["sintesi"], P["breve"], P["frase"]):
                    errori.append(f"{k} {v['slug']}: riassunto della validità diverso da quello dello schema sul testo salvato")
                visti_ss = next((b for t, b in ss if t and RCA.TITOLO_VISTI.match(t)), [])
                if [b["x"] for b in visti_ss] != [b["x"] for b in V["testo"]]:
                    errori.append(f"{k} {v['slug']}: testo dei visti diverso dalla sezione d'ingresso salvata")
                rs = RCA.sintesi_visto(V["testo"], ss)
                if (rs[0], rs[1], rs[2]) != (V["schema"], V["sintesi"], V["frase"]):
                    errori.append(f"{k} {v['slug']}: riassunto del visto diverso da quello dello schema sul testo salvato")
                etias = [(t, b) for t, b in ss if t and "ETIAS" in t and any(RCA.ETIAS_NON_APERTO in x["x"] and RCA.ETIAS_FUTURO in x["x"] for x in b)]
                resto = " ".join(x["x"] for t, b in ss if (t, b) not in etias for x in b) + " " + " ".join(t or "" for t, b in ss if (t, b) not in etias)
                tutto_visti = " ".join(b["x"] for b in V["testo"])
            else:
                sez = _sezioni_au(p)
                rv = RAU.sintesi_validita(sez, p["nome"], p["slug_fonte"])
                if (rv[0], rv[1], rv[2], rv[3]) != (P["schema"], P["sintesi"], P["breve"], P["frase"]):
                    errori.append(f"{k} {v['slug']}: riassunto della validità diverso da quello dello schema sul testo salvato")
                rs = RAU.sintesi_visto(sez, p["nome"], p["slug_fonte"])
                if (rs[0], rs[1], rs[2]) != (V["schema"], V["sintesi"], V["frase"]):
                    errori.append(f"{k} {v['slug']}: riassunto del visto diverso da quello dello schema sul testo salvato")
                etias = []
                resto = " ".join(b["x"] for t, bb in sez.items() if t != "Passport" for b in bb if not b.get("generico"))
                tutto_visti = resto
            # b) modelli fissi, numeri nella frase ufficiale, frase = inizio del testo citato
            if P["sintesi"]:
                conti[k]["val"] += 1
                if not any(m.match(P["sintesi"]) for m in MODELLI_VAL[k]):
                    errori.append(f"{k} {v['slug']}: riassunto della validità fuori dai modelli fissi: {P['sintesi']}")
                if not _numeri_ok(P["sintesi"], P["frase"]):
                    errori.append(f"{k} {v['slug']}: un numero del riassunto della validità non è nella frase ufficiale")
                if not any(b["x"].startswith(P["frase"]) or P["frase"] in b["x"] for b in P["testo"]):
                    errori.append(f"{k} {v['slug']}: la frase della validità non è nel testo citato")
            elif P["testo"]:
                conti[k]["val_cit"] += 1
            if V["sintesi"]:
                conti[k]["vis"] += 1
                if not any(m.match(V["sintesi"]) for m in MODELLI_VIS[k]):
                    errori.append(f"{k} {v['slug']}: riassunto del visto fuori dai modelli fissi: {V['sintesi']}")
                if not _numeri_ok(V["sintesi"], V["frase"]):
                    errori.append(f"{k} {v['slug']}: un numero del riassunto del visto non è nella frase ufficiale")
                if not any(b["x"].startswith(V["frase"]) for b in V["testo"]):
                    errori.append(f"{k} {v['slug']}: la frase del visto non è nel testo citato")
                senza = re.search(r"not required|don't need|without a visa", V["sintesi"])
                if senza and VIETATO_SENZA.search(resto):
                    errori.append(f"{k} {v['slug']}: 'senza visto' ma il testo d'ingresso parla di autorizzazione, e-visa, modulo, tessera o tassa: "
                                  f"{VIETATO_SENZA.search(resto).group(0)}")
                if etias and "ETIAS" not in V["sintesi"]:
                    errori.append(f"{k} {v['slug']}: il testo parla di ETIAS ma il riassunto no")
                if not senza and VIETATO_RICHIESTO.search(tutto_visti):
                    errori.append(f"{k} {v['slug']}: 'serve un visto' ma il visto è elettronico o si ottiene all'arrivo")
            elif V["testo"]:
                conti[k]["vis_cit"] += 1
            # c) la pagina: citazioni intere, riassunti solo se ci sono, fonte, date, licenza, nessuna aria di sito governativo
            t = leggi(v["url_pag"] + "index.html")
            for b in G.passaporto_da_mostrare(k, P["testo"]) + V["testo"]:
                if escape(b["x"]) not in t:
                    errori.append(f"{k} {v['slug']}: testo ufficiale mancante nella pagina: {b['x'][:60]}")
            if not (P["testo"] or V["testo"]):
                errori.append(f"{k} {v['slug']}: pagina senza nessuna citazione ufficiale")
            n_brevi = sum(1 for x in (P["sintesi"], V["sintesi"]) if x)
            if t.count("In short: <strong>") != n_brevi:
                errori.append(f"{k} {v['slug']}: {t.count('In short: <strong>')} riassunti nella pagina invece di {n_brevi}")
            for x in (P["sintesi"], V["sintesi"]):
                if x and f"In short: <strong>{escape(x)}.</strong>" not in t:
                    errori.append(f"{k} {v['slug']}: riassunto non mostrato com'è nei dati")
            if escape(p["url"]) not in t or "checked on " + G.data_lunga(D["controllato_il"]) not in t:
                errori.append(f"{k} {v['slug']}: fonte o data del controllo mancanti")
            if p.get("aggiornata") and G.data_lunga(p["aggiornata"]) not in t:
                errori.append(f"{k} {v['slug']}: data di aggiornamento della pagina ufficiale mancante")
            if k == "ca" and ("Contains information licensed under the" not in t or escape(D["licenza_url"]) not in t
                              or "not a Government of Canada site" not in t):
                errori.append(f"{k} {v['slug']}: attribuzione OGL Canada o avviso 'non governativo' mancanti")
            if k == "au" and (escape(D["attribuzione"]) not in t or D["licenza_url"] not in t or "not an Australian Government site" not in t):
                errori.append(f"{k} {v['slug']}: attribuzione Smartraveller (CC BY 4.0) o avviso 'non governativo' mancanti")
            if f"Do {c['pop']} need a visa for {escape(G.nome_frase(v))}?" not in t or 'id="passport"' not in t:
                errori.append(f"{k} {v['slug']}: domande sul visto o sulla validità mancanti")
            # d) collegamenti: indice, pagine britanniche della stessa destinazione (andata e ritorno)
            if f'href="../{v["url_pag"]}"' not in t_ind:
                errori.append(f"{k} {v['slug']}: manca nell'indice {c['base']}/")
            for s in v["uk"]:
                tu = leggi(f"passport-validity/{s}/index.html")
                if f'href="../../{v["url_pag"]}"' not in tu:
                    errori.append(f"{k} {v['slug']}: la pagina britannica {s} non collega la pagina {c['agg']}")
                if f'href="../../passport-validity/{s}/"' not in t:
                    errori.append(f"{k} {v['slug']}: manca il collegamento alla pagina britannica {s}")
        slugs = [v["slug"] for v in voci]
        if len(set(slugs)) != len(slugs):
            errori.append(f"{k}: slug duplicati")
        # e) contenuto sottile (revisione del 17/10/2026): pagina solo con testo specifico del Paese; le altre senza pagina, fuori dalla sitemap,
        #    elencate nell'indice con il link alla fonte
        sm = leggi("sitemap.xml")
        for v in voci:
            if not G.ha_testo_specifico(k, v["p"]):
                errori.append(f"{k} {v['slug']}: pagina senza testo specifico del Paese")
        for p in G.SENZA_PAGINA_ESTERI[k]:
            if escape(p["url"]) not in t_ind:
                errori.append(f"{k}: {p['nome']} senza pagina ma non elencato nell'indice con il link ufficiale")
            for cand in {p.get("slug_fonte", ""), G._chiave_nome(p["nome"]).replace(" ", "-")}:
                if cand and ((SITO / c["base"] / cand).exists() or f"/{c['base']}/{cand}/<" in sm):
                    errori.append(f"{k}: {p['nome']} non deve avere una pagina né stare nella sitemap")
    return errori, conti


# ---------------------------------------------------------------- 12. bagaglio a mano per compagnia aerea
NUM = re.compile(r"\d+(?:[.,]\d+)?")


def _numeri(testo):
    return {round(float(x.replace(",", ".")), 2) for x in NUM.findall(testo)}


def _entra_permutazioni(m, unita, b):
    """Controllo indipendente da genera.entra_borsa: la borsa entra se ALMENO UNA delle 6 rotazioni rispetta i tre limiti nell'ordine della fonte."""
    import itertools
    if unita == "in" and b.get("pollici") and b.get("pollici_ufficiali"):
        lim, mis, u = b["pollici"], m, "in"
    else:
        lim, mis, u = b["cm"], [x * 2.54 for x in m] if unita == "in" else m, "cm"
    if b.get("totale") and sum(mis) > b["totale"][u] + 1e-6:
        return False
    return any(all(p[i] <= lim[i] + 1e-6 for i in range(3)) for p in itertools.permutations(mis))


# 10 casi del controllo "Does my bag fit?" provati nel browser (valori come li scrive l'utente)
CASI_BORSA = [
    ("40x30x20 cm", ["40", "30", "20"], "cm"),
    ("ruotata 20x40x30 cm", ["20", "40", "30"], "cm"),
    ("55x40x20 cm", ["55", "40", "20"], "cm"),
    ("misure uguali 30x30x30 cm", ["30", "30", "30"], "cm"),
    ("decimale 40.5x30x20 cm", ["40.5", "30", "20"], "cm"),
    ("virgola 45,5x36x20 cm", ["45,5", "36", "20"], "cm"),
    ("pollici 22x14x9 in", ["22", "14", "9"], "in"),
    ("pollici 22x14x9.5 in", ["22", "14", "9.5"], "in"),
    ("56x45x25 cm", ["56", "45", "25"], "cm"),
    ("non valida 0x30x20", ["0", "30", "20"], "cm"),
]


def _attesi_borsa(valori, unita):
    try:
        m = [float(v.replace(",", ".")) for v in valori]
    except ValueError:
        return None
    if any(x <= 0 for x in m):
        return None
    return {C["slug"]: G.esito_compagnia(m, unita, C)[0] for C in G.COMPAGNIE}


def controlla_bagagli():
    from html import unescape
    errori, conti = [], {"compagnie": len(G.COMPAGNIE), "misure": 0, "citazioni": 0, "faq": 0}
    oggi = G.OGGI.isoformat()
    # link di affiliazione: dal 30/10/2026 (monetizzazione sbloccata) sono ammessi, ma solo verso i domini di monetizzazione.json;
    # rel="sponsored noopener" e riga di trasparenza in ogni pagina li controlla il controllo comune (monetizzazione.py, punto 19)
    for k, v in G.AFFILIATI.items():
        if isinstance(v, dict) and v.get("url") and not G.MON.dominio_ammesso(v["url"]):
            errori.append(f"affiliati.json: la voce '{k}' punta a un dominio non ammesso in monetizzazione.json")
    if "bagagli" not in G.AFFILIATI:
        errori.append("affiliati.json: manca la voce 'bagagli'")
    for C in G.COMPAGNIE:
        rel = f"{G.BAG_BASE}/{C['slug']}/index.html"
        if not (SITO / rel).exists():
            errori.append(f"bagagli {C['slug']}: pagina mancante")
            continue
        t = leggi(rel)
        d = C["controllato_il"]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) or d > oggi:
            errori.append(f"bagagli {C['slug']}: data del controllo non valida {d}")
        if "checked on " + G.data_lunga(d) not in t:
            errori.append(f"bagagli {C['slug']}: data del controllo non mostrata")
        for k, f in C["fonti"].items():
            if not f.get("url", "").startswith("https://") or not f.get("titolo") or escape(f["url"]) not in t:
                errori.append(f"bagagli {C['slug']}: fonte {k} senza URL https, titolo o link nella pagina")
        tutte = [c for b in C["borse"] for c in b["cit"]] + [c for x in C["tariffe"] for c in x["cit"]] + C["avvisi"] + C.get("extra", [])
        for c in tutte:
            conti["citazioni"] += 1
            if c["f"] not in C["fonti"] or not c["righe"]:
                errori.append(f"bagagli {C['slug']}: citazione senza fonte o vuota")
            for r in c["righe"]:
                if escape(r) not in t:
                    errori.append(f"bagagli {C['slug']}: citazione ufficiale non mostrata: {r[:60]}")
        numeri_tutti = set().union(*[_numeri(" ".join(c["righe"])) for c in tutte])
        for b in C["borse"]:
            conti["misure"] += 1
            nb = set().union(*[_numeri(" ".join(c["righe"])) for c in b["cit"]]) if b["cit"] else set()
            if not b["cit"]:
                errori.append(f"bagagli {C['slug']}/{b['id']}: misura senza citazione ufficiale")
            if b["cm_ufficiali"] and not all(round(x, 2) in nb for x in b["cm"]):
                errori.append(f"bagagli {C['slug']}/{b['id']}: i centimetri {b['cm']} non sono tutti nella frase ufficiale")
            if b.get("pollici_ufficiali") and not all(round(x, 2) in nb for x in b["pollici"]):
                errori.append(f"bagagli {C['slug']}/{b['id']}: i pollici {b['pollici']} non sono tutti nella frase ufficiale")
            if not b["cm_ufficiali"] and (not b.get("pollici_ufficiali") or [round(x * 2.54, 2) for x in b["pollici"]] != [round(x, 2) for x in b["cm"]]):
                errori.append(f"bagagli {C['slug']}/{b['id']}: centimetri non ufficiali che non sono la conversione dei pollici ufficiali")
            if b.get("totale") and not (round(b["totale"]["cm"], 2) in nb and round(b["totale"]["in"], 2) in nb):
                errori.append(f"bagagli {C['slug']}/{b['id']}: totale non presente nella frase ufficiale")
            if b.get("peso") and not _numeri(b["peso"]) <= numeri_tutti:
                errori.append(f"bagagli {C['slug']}/{b['id']}: peso '{b['peso']}' non presente nelle frasi ufficiali")
            if escape(G.misura_testo(b, C)) not in t:
                errori.append(f"bagagli {C['slug']}/{b['id']}: misura non mostrata nella tabella")
        if escape(G.risposta_bag(C)) not in t:
            errori.append(f"bagagli {C['slug']}: risposta diretta in alto mancante")
        # FAQ: JSON-LD e testo visibile fatti solo di citazioni ufficiali intere
        ammesse = [" ".join(c["righe"]) for c in tutte]
        for blocco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t):
            x = json.loads(blocco)
            if x.get("@type") != "FAQPage":
                continue
            for q in x["mainEntity"]:
                conti["faq"] += 1
                testo = q["acceptedAnswer"]["text"]
                m = re.match(r"Quoted from (.+?) \(checked on ([^)]+)\): (.*)$", testo, re.S)
                if not m or m.group(2) != G.data_lunga(d) or any(n not in [f["titolo"] for f in C["fonti"].values()] for n in m.group(1).split("; ")):
                    errori.append(f"bagagli {C['slug']}: FAQ senza fonte o data corretta: {q['name']}")
                    continue
                if citazioni_faq(m.group(3), ammesse) is None:
                    errori.append(f"bagagli {C['slug']}: risposta FAQ con testo non ufficiale: {q['name']}")
                if escape(q["name"]) not in t:
                    errori.append(f"bagagli {C['slug']}: domanda FAQ non visibile: {q['name']}")
        if 'href="../../cabin-bags/does-my-bag-fit/"' not in t:
            errori.append(f"bagagli {C['slug']}: manca il collegamento allo strumento")
    # confronto: ordinamento (genera) contro le 6 rotazioni (indipendente) su casi casuali, in cm e pollici
    rnd = random.Random(11)
    for _ in range(4000):
        u = rnd.choice(["cm", "in"])
        m = [round(rnd.uniform(5, 70 if u == "cm" else 28), rnd.choice([0, 1, 2])) for _ in range(3)]
        for C in G.COMPAGNIE:
            for b in C["borse"]:
                if G.entra_borsa(m, u, b) != _entra_permutazioni(m, u, b):
                    errori.append(f"confronto borsa: ordinamento e rotazioni danno esiti diversi per {m} {u} su {C['slug']}/{b['id']}")
    # pagine per misura coerenti con i dati
    for sl, m in G.MISURE_COMUNI:
        rel = f"{G.BAG_BASE}/size/{sl}/index.html"
        t = leggi(rel)
        trovate = dict((s, e) for e, s in re.findall(r'<tr data-esito="(\w+)" data-slug="([\w-]+)"', t))
        atteso = {C["slug"]: G.esito_compagnia(list(m), "cm", C)[0] for C in G.COMPAGNIE}
        indip = {}
        for C in G.COMPAGNIE:
            e = "no"
            for b in C["borse"]:
                if _entra_permutazioni(list(m), "cm", b):
                    e = "gratis" if b["incluso"] == "tutte" else (e if e == "gratis" else "altre")
            indip[C["slug"]] = e
        if trovate != atteso or atteso != indip:
            errori.append(f"misura {sl}: elenco della pagina diverso dai dati ({ {k: (trovate.get(k), atteso[k], indip[k]) for k in atteso if not (trovate.get(k) == atteso[k] == indip[k])} })")
        for k in G.ESITO:
            n = sum(1 for v in atteso.values() if v == k)
            if k == "gratis" and f"<strong>{n} airline{'s' if n != 1 else ''}</strong>" not in t:
                errori.append(f"misura {sl}: conteggio 'free with every fare' sbagliato in alto")
    # indice, strumento, pagina UE, collegamenti
    ti = leggi(f"{G.BAG_BASE}/index.html")
    for C in G.COMPAGNIE:
        if f'href="../{G.BAG_BASE}/{C["slug"]}/"' not in ti:
            errori.append(f"indice bagagli: manca {C['slug']}")
    for E in G.BAG["escluse"]:
        if escape(E["nome"]) not in ti or escape(E["motivo"]) not in ti:
            errori.append(f"indice bagagli: compagnia esclusa {E['nome']} senza motivo")
    if "data-filtro-multi" not in ti:
        errori.append("indice bagagli: ricerca mancante")
    ts = leggi(G.BAG_STRUMENTO + "index.html")
    if "data-borsa" not in ts or 'id="borse-dati"' not in ts or "longest side" not in ts or "official rule decides" not in ts:
        errori.append("strumento: modulo, dati o spiegazione del confronto mancanti")
    U = G.BAG["ue"]
    tu = leggi(G.BAG_UE + "index.html")
    for c in U["citazioni"]:
        for r in c["righe"]:
            if escape(r) not in tu:
                errori.append(f"pagina UE: citazione mancante {r[:60]}")
    for k, f in U["fonti"].items():
        if escape(f["url"]) not in tu or not any(h in f["url"] for h in ("europa.eu",)):
            errori.append(f"pagina UE: fonte {k} mancante o non ufficiale UE")
    for x in U["iter"]:
        if f'{G.data_lunga(x["data"])}</td><td data-l="Step">{escape(x["evento"])}' not in tu:
            errori.append(f"pagina UE: tappa {x['data']} mancante")
    if "checked on " + G.data_lunga(U["controllato_il"]) not in tu or "It shall apply from 23 October 2027." not in tu:
        errori.append("pagina UE: data del controllo o data di applicazione mancanti")
    for a in G.AER["aeroporti"] + G.AER["nazionali"]:
        if 'href="../../cabin-bags/"' not in leggi(f"liquids/{a['slug']}/index.html"):
            errori.append(f"liquidi {a['slug']}: manca il collegamento a Cabin bag size by airline")
    th = leggi("index.html")
    if 'href="cabin-bags/"' not in th or ">Cabin bags</a>" not in th:
        errori.append("home: manca il collegamento (riquadro o menu) ai bagagli")
    return errori, conti


def controlla_js_borsa():
    """Motore JS del controllo (stesso testo delle pagine) contro Python su 3.000 casi casuali, in cm e pollici."""
    rnd = random.Random(5)
    casi = []
    for _ in range(3000):
        u = rnd.choice(["cm", "in"])
        casi.append([[round(rnd.uniform(5, 70 if u == "cm" else 28), rnd.choice([0, 1, 2])) for _ in range(3)], u])
    motore = G.BAG_JS.split("(function(){")[0]
    script = (motore + "\nvar D=" + json.dumps(G.dati_bag_client()) + ";var casi=" + json.dumps(casi) + ";\n"
              "console.log(JSON.stringify(casi.map(function(c){return D.map(function(C){return bfCompagnia(c[0],c[1],C).esito;});})));")
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(script)
    try:
        r = subprocess.run(["node", fh.name], capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        return ["node non trovato: confronto JS della borsa saltato"]
    finally:
        os.unlink(fh.name)
    if r.returncode != 0:
        return ["Errore JS borsa: " + r.stderr[:500]]
    errori = []
    for (m, u), js in zip(casi, json.loads(r.stdout)):
        py = [G.esito_compagnia(m, u, C)[0] for C in G.COMPAGNIE]
        if py != js:
            errori.append(f"borsa: JS diverso dal Python per {m} {u}")
    return errori[:20]


# ---------------------------------------------------------------- 13. documenti per chi ha la cittadinanza italiana (Viaggiare Sicuri)
RIT = _carica("documenti_it")
MAX_COPIA = 25  # nessuna pagina italiana può avere più di 25 parole di fila uguali a un testo delle schede
N_GRAM = 10
# controllo indipendente (più semplice della raccolta): parole che indicano un'autorizzazione o un modulo obbligatorio
AUT_IND = re.compile(r"\bESTA\b|\beTA\b|\bETA\b|NZeTA|K-ETA|ETA-IL|(?i:autorizzazione (?:elettronica|di viaggio|all['’]\s?ingresso|preventiva)|arrival card|"
                     r"modulo ED|e-ticket|travel authori[sz]ation|tarjeta de turista)")
ALTRO_IND = re.compile(r"transit|\bscal[oi]\b|Irlanda del Nord|residen|esent|non (?:è|e['’]) richiest|consiglia|invit|raccomand", re.I)
PROMESSE_IT = re.compile(r"aggiornat[oaie] ogni (?:settimana|mese|giorno)|ogni (?:settimana|mese) ricontroll|settimanalmente|mensilmente|ricontrolliamo ogni", re.I)
NUM_PAROLA = {"1": "un|uno|una|primo", "2": "due", "3": "tre", "5": "cinque", "6": "sei", "12": "dodici", "30": "trenta", "90": "novanta"}


def _parole_it(testo):
    return re.findall(r"\w+", testo.replace("’", "'").lower())


def _testo_visibile(html_):
    from html import unescape
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", html_, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return unescape(t)


def _testi_fonte(j):
    """Tutti i testi di una scheda (ogni sezione), senza HTML."""
    out = []

    def giro(x):
        if isinstance(x, dict):
            for y in x.values():
                giro(y)
        elif isinstance(x, list):
            for y in x:
                giro(y)
        elif isinstance(x, str) and len(x) > 40:
            out.append(_testo_visibile(x))
    giro(j)
    return out


def _ngram_fonti():
    g = set()
    for f in RIT.CACHE.glob("[A-Z][A-Z][A-Z].json"):
        for t in _testi_fonte(json.loads(f.read_text(encoding="utf-8"))):
            w = _parole_it(t)
            for i in range(len(w) - N_GRAM + 1):
                g.add(hash(tuple(w[i:i + N_GRAM])))
    return g


def _run_massimo(parole_pag, g):
    """Lunghezza della più lunga sequenza di parole della pagina uguale a una sequenza della fonte (approssimata dalle finestre di N_GRAM parole)."""
    migliore, corrente = 0, 0
    for i in range(len(parole_pag) - N_GRAM + 1):
        if hash(tuple(parole_pag[i:i + N_GRAM])) in g:
            corrente += 1
            migliore = max(migliore, corrente)
        else:
            corrente = 0
    return migliore + N_GRAM - 1 if migliore else 0


def _citazioni_fatto(f):
    qq = list(f.get("citazioni") or ([f["citazione"]] if f.get("citazione") else []))
    qq += list(f.get("citazioni_note", [])) + [x["citazione"] for x in f.get("formalita", [])]
    for c in ("condizione", "durata"):
        if f.get(c):
            qq.append(f[c])
    return qq


def _numero_in(n, testo):
    alt = str(n) + ("|" + NUM_PAROLA[str(n)] if str(n) in NUM_PAROLA else "")
    return bool(re.search(r"(?<![\d])(?:" + alt + r")(?![\d])", testo, re.I))


def controlla_italiani():
    errori, conti = [], {"pagine": 0, "senza": 0, "doc": 0, "val": 0, "vis": 0, "manuali": 0, "citazioni": 0, "faq": 0, "copia_max": 0}
    D = G.DOC_IT
    if not D:
        return ["documenti per italiani: manca dati/documenti_it.json"], conti
    # copie delle schede (raccolta/.cache/it/, fuori dal repository per la licenza incerta): se mancano, il ricalcolo dalla copia si salta
    # con un avviso (10/11/2026); i controlli dati = pagine qui sotto restano tutti
    n_copie = len(list(RIT.CACHE.glob("[A-Z][A-Z][A-Z].json"))) if RIT.CACHE.exists() else 0
    con_copie = n_copie >= 0.8 * D["schede_elenco"]
    if not con_copie:
        avviso(13, f"copie delle schede Viaggiare Sicuri assenti o incomplete ({n_copie} su {D['schede_elenco']} in {RIT.CACHE.relative_to(SITO.parent)}/, "
                   "fuori dal repository): ricalcolo dei fatti, citazioni nel campo della scheda e testo copiato saltati; dati dell'ultima lettura buona "
                   f"({D.get('controllato_il')}); per ricrearle: python3 -I beforeyoufly/raccolta/documenti_it.py")
    if len(D["paesi"]) < 0.8 * D["schede_elenco"]:
        errori.append(f"documenti per italiani: lette {len(D['paesi'])} schede su {D['schede_elenco']}")
    manuali = json.loads(RIT.FILE_MANUALI.read_text(encoding="utf-8"))["paesi"] if RIT.FILE_MANUALI.exists() else {}
    con_pagina = {v["p"]["iso3"]: v for v in G.VOCI_IT}
    for p in D["paesi"]:
        iso = p["iso3"]
        # a) la cache è la stessa versione della scheda da cui vengono i fatti (impronte), e i fatti sono quelli che dà la lettura sul campo salvato
        #    (solo con la copia: senza copia, o con una copia più recente dei dati, avviso e niente ricalcolo per questa scheda)
        campi, testi, imp = None, None, dict(p["impronte"])
        f_c = RIT.CACHE / f"{iso}.json"
        if con_copie and copia_usabile(13, iso, f_c, "documenti_it.py"):
            campi, j = RIT.campi_da_cache(iso)
            imp_c = {k: RIT.impronta(v) for k, v in campi.items()}
            ef = []
            if imp_c != p["impronte"]:
                ef.append(f"{iso}: la scheda in cache non è quella da cui sono stati scritti i fatti (impronte diverse): rilanciare la raccolta e genera.py")
            else:
                if p["aggiornata"] != RIT.data_scheda(j.get("updateDate", "")):
                    ef.append(f"{iso}: data della scheda diversa dalla cache")
                rec, _, scaduti = RIT.leggi_paese({"Codice-3": iso, "Codice-2": p["iso2"], "Nome": p["nome_fonte"]}, j)
                for k in ("documento", "validita", "visto", "note_extra", "cronologia"):
                    if rec.get(k) != p.get(k):
                        ef.append(f"{iso}: fatto «{k}» diverso da quello ricalcolato sul campo salvato")
                if scaduti:
                    ef.append(f"{iso}: fatti scritti a mano su una versione vecchia della scheda: {scaduti}")
            ef = esito_copia(13, iso, ef, f_c, D.get("controllato_il"))
            errori += ef
            if ef or imp_c != p["impronte"]:
                campi = None  # copia diversa dai dati: i controlli sul campo salvato non hanno senso
            else:
                imp = imp_c
                testi = {k: RIT.testo(v) for k, v in campi.items()}
        if not p["url"].startswith(RIT.PAGINA) or not p["aggiornata"]:
            errori.append(f"{iso}: link o data della scheda mancanti")
        # b) ogni fatto è legato a un campo della scheda e ogni citazione è in quel campo, parola per parola, al massimo 20 parole
        fatti = [(k, p[k]) for k in ("documento", "validita", "visto")] + [("note_extra", x) for x in p.get("note_extra", [])]
        for k, f in fatti:
            if not f.get("esito") and k != "note_extra":
                if not f.get("motivo"):
                    errori.append(f"{iso} {k}: niente riassunto ma nessun motivo")
                continue
            campo = f.get("campo")
            if campo not in imp:
                errori.append(f"{iso} {k}: fatto senza campo della scheda")
                continue
            qq = _citazioni_fatto(f)
            if not qq:
                errori.append(f"{iso} {k}: fatto senza citazione")
            for q in qq:
                conti["citazioni"] += 1
                if testi is not None and not RIT.in_campo(q, testi[campo]):
                    errori.append(f"{iso} {k}: citazione non trovata nel campo «{campo}»: {q[:70]}")
                if len(q.replace(RIT.ELISIONE, " ").split()) > RIT.MAX_PAROLE:
                    errori.append(f"{iso} {k}: citazione di più di {RIT.MAX_PAROLE} parole")
            for q in f.get("obblighi_pp", []):  # obblighi scritti solo nel riquadro "In primo piano": citazione breve da quel campo
                conti["citazioni"] += 1
                if testi is not None and not RIT.in_campo(q, testi["primo_piano"]):
                    errori.append(f"{iso} {k}: citazione del riquadro «In primo piano» non trovata: {q[:70]}")
                if len(q.replace(RIT.ELISIONE, " ").split()) > RIT.MAX_PAROLE:
                    errori.append(f"{iso} {k}: citazione del riquadro «In primo piano» di più di {RIT.MAX_PAROLE} parole")
            if f.get("manuale") and not f.get("scritto_il"):
                errori.append(f"{iso} {k}: fatto scritto a mano senza data")
            nostre = " ".join([f.get("sintesi", ""), f.get("testo", "")] + list(f.get("note", [])))
            for n in re.findall(r"\d+", nostre):
                if not any(_numero_in(n, q) for q in qq):
                    errori.append(f"{iso} {k}: il numero {n} della frase nostra non è in nessuna citazione")
            if f.get("manuale"):
                conti["manuali"] += 1
                if iso not in manuali or not imp[campo].startswith(manuali[iso]["campi"][campo]):
                    errori.append(f"{iso} {k}: fatto manuale senza impronta valida")
            # c) controlli indipendenti sui fatti automatici (sul campo salvato: solo con la copia)
            if f.get("manuale") or campi is None:
                continue
            if k == "documento":
                tp = testi["passaporto"]
                if f["esito"] == "cie" and not re.search(r"\bCIE\b", tp):
                    errori.append(f"{iso}: «passaporto o CIE» ma il campo non nomina la CIE")
                if f["esito"] == "passaporto" and re.search(r"\bCIE\b|carta d['’]\s?identit[àa] (?:elettronica|valida)|carta di identit[àa] (?:elettronica|valida)", tp):
                    errori.append(f"{iso}: «serve il passaporto» ma il campo nomina la carta d'identità")
                if f["esito"] == "solo_passaporto" and not re.search(r"UNICAMENTE|soltanto|esclusivamente|Non è ammesso alcun altro documento", tp):
                    errori.append(f"{iso}: «solo passaporto» senza una frase che lo dica")
            if k == "validita" and f["esito"] == "numero":
                if not _numero_in(f["n"], f["citazione"]) or not re.search(r"validit|scadenza|valid[oa]", f["citazione"], re.I):
                    errori.append(f"{iso}: validità di {f['n']} {f['unita']} senza il numero nella citazione")
                altri = set()
                for fr in RIT.tutte_frasi(campi["passaporto"]):
                    if re.search(r"massima|residen|provvisori|variazion|modifich|per recarsi|extra-?UE|pi[ùu] di \d|oltre i \d|permesso di soggiorno", fr, re.I):
                        continue
                    for m in re.finditer(r"(\d+|tre|sei|cinque)\s*(?:\(\w+\)\s*)?(mesi|giorni)[^.;]{0,25}?validit|validit\S*\s+(?:residua\s+)?(?:\S+\s+){0,4}?(\d+|tre|sei|cinque)\s*(?:\(\w+\)\s*)?(mesi|giorni)", fr, re.I):
                        x = (m.group(1) or m.group(3)).lower()
                        altri.add(RIT.NUMERI_P.get(x) or int(x))
                if altri - {f["n"]}:
                    errori.append(f"{iso}: la scheda indica anche altre validità ({sorted(altri)}) ma la pagina ne riassume una sola")
            if k == "visto" and f["esito"] == "non_necessario":
                nomi = [x["nome"].split(" (")[0] for x in f.get("formalita", [])]
                for fr in RIT.tutte_frasi(campi["visto"]):
                    m = AUT_IND.search(fr)
                    if m and not any(nm.split()[0] in fr for nm in nomi) and not ALTRO_IND.search(fr):
                        errori.append(f"{iso}: «non serve il visto» ma la scheda parla di «{m.group(0)}» e la pagina non lo dice: {fr[:80]}")
        # d) pagina: c'è solo se la scheda ha un contenuto specifico; mostra fonte, data, avvertenze, citazioni, FAQ dai fatti
        if iso not in con_pagina:
            conti["senza"] += 1
            if (G.SITO / G.IT_BASE / G.NOMI_IT[iso]["slug"] / "index.html").exists():
                errori.append(f"{iso}: pagina pubblicata per una scheda senza contenuto da riassumere")
            continue
        v = con_pagina[iso]
        conti["pagine"] += 1
        conti["doc"] += bool(p["documento"].get("esito"))
        conti["val"] += bool(p["validita"].get("esito"))
        conti["vis"] += bool(p["visto"].get("esito"))
        t = leggi(v["url_pag"] + "index.html")
        for atteso in ('<html lang="it">', escape(p["url"]), f"scheda aggiornata {G.con_art('il', G.data_it(p['aggiornata']))}", "non è della Farnesina",
                       "controlla la scheda ufficiale prima di partire", G.GOATCOUNTER_URL, f'<link rel="canonical" href="{G.URL_SITO}/{v["url_pag"]}">',
                       'id="documento"', 'id="validita"', 'id="visto"'):
            if atteso not in t:
                errori.append(f"{iso}: nella pagina manca «{atteso[:50]}»")
        for k, f in fatti:
            for q in (_citazioni_fatto(f) if (f.get("esito") or k == "note_extra") else []):
                if escape(q) not in t:
                    errori.append(f"{iso} {k}: citazione non mostrata nella pagina: {q[:60]}")
            if not f.get("esito") and k != "note_extra" and "Consulta la scheda ufficiale" not in t:
                errori.append(f"{iso} {k}: senza riassunto ma la pagina non dice di consultare la scheda")
            for q in f.get("obblighi_pp", []):
                if escape(q) not in t:
                    errori.append(f"{iso} {k}: obbligo del riquadro «In primo piano» non mostrato nella pagina: {q[:60]}")
            if f.get("manuale") and f"Riassunto scritto a mano da noi {G.con_art('il', G.data_it(f['scritto_il']))}" not in t:
                errori.append(f"{iso} {k}: fatto scritto a mano senza la data nella pagina")
        if PROMESSE_IT.search(t):
            errori.append(f"{iso}: promessa di aggiornamento periodico")
        faq = G.faq_it(v)
        conti["faq"] += len(faq)
        ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t)]
        fq = next((x for x in ld if x.get("@type") == "FAQPage"), None)
        if faq and (not fq or [(e["name"], e["acceptedAnswer"]["text"]) for e in fq["mainEntity"]] != faq):
            errori.append(f"{iso}: FAQ JSON-LD diversa dalle domande ricavate dai fatti")
        for q, a in faq:
            if f"<h3>{escape(q)}</h3><p>{escape(a)}</p>" not in t:
                errori.append(f"{iso}: FAQ visibile diversa dal JSON-LD: {q}")
        # e) collegamenti con la pagina britannica della stessa destinazione (andata e ritorno)
        for s in v["uk"]:
            if f'passport-validity/{s}/' not in t:
                errori.append(f"{iso}: manca il link alla pagina britannica {s}")
            tuk = leggi(f"passport-validity/{s}/index.html")
            if f'{v["url_pag"]}"' not in tuk or "Italian citizens: " not in tuk:
                errori.append(f"{s}: manca il link «Italian citizens: documenti per italiani» verso {v['url_pag']}")
    # f) nessun testo lungo copiato: più di MAX_COPIA parole di fila uguali a una scheda (tutte le sezioni di tutte le schede; solo con le copie)
    g = _ngram_fonti() if con_copie else set()
    pagine_it = list((G.SITO / "it").rglob("*.html")) if con_copie else []
    for f in pagine_it:
        r = _run_massimo(_parole_it(_testo_visibile(f.read_text(encoding="utf-8"))), g)
        conti["copia_max"] = max(conti["copia_max"], r)
        if r > MAX_COPIA:
            errori.append(f"{f.relative_to(G.SITO)}: {r} parole di fila uguali al testo di una scheda (massimo {MAX_COPIA})")
    # g) indice: tutte le schede, ricerca, link alle pagine o alla scheda ufficiale; sezione metodo con fonte e licenza
    ti = leggi(f"{G.IT_BASE}/index.html")
    if ti.count("<tr data-voce>") != len(D["paesi"]) or 'data-filtro="lista-it"' not in ti or 'id="metodo"' not in ti:
        errori.append("indice italiano: righe, ricerca o sezione metodo mancanti")
    for v in G.SENZA_PAGINA_IT:
        if escape(v["p"]["url"]) not in ti:
            errori.append(f"indice italiano: {v['nome']} senza pagina e senza link alla scheda ufficiale")
    for v in G.VOCI_IT:
        if f'href="../../{v["url_pag"]}"' not in ti:
            errori.append(f"indice italiano: manca il link a {v['url_pag']}")
    if "non indica una licenza" not in ti:
        errori.append("indice italiano: manca la spiegazione sulla licenza dei testi")
    sm = leggi("sitemap.xml")
    for v in G.SENZA_PAGINA_IT:
        if f"/{v['url_pag']}<" in sm:
            errori.append(f"sitemap: {v['url_pag']} senza pagina")
    if "it/documenti/" not in leggi("index.html") or "documenti per italiani" not in leggi("passport-validity/index.html"):
        errori.append("home o indice britannico senza link alla sezione italiana")
    return errori, conti


# Parole vietate scritte al contrario, così questo file non le contiene in chiaro.
_AL_CONTRARIO = ["edualc", "ciporhtna", "ianepo", "tpgtahc", "inimeg", "tolipoc", "amall", "lartsim", "supo", "tennos", "ukiah"]
VIETATE = re.compile(r"\b(" + "|".join(w[::-1] for w in _AL_CONTRARIO) + r"|gpt-\d)\b", re.I)


def controlla_parole():
    errori = []
    cartelle = [SITO, SITO.parent / "dati", SITO.parent / "raccolta"]
    for c in cartelle:
        for f in c.rglob("*"):
            if ".cache" in f.parts:  # testi grezzi delle fonti ufficiali (fuori dal repository): non sono file nostri
                continue
            if f.is_file() and f.suffix in (".html", ".xml", ".txt", ".toml", ".json", ".py", ".md"):
                m = VIETATE.search(f.read_text(encoding="utf-8"))
                if m:
                    errori.append(f"Parola vietata '{m.group(0)}' in {f}")
    for f in (SITO.parent / "NOTE.md", SITO.parent / "TEST.md", SITO.parent / "genera.py"):
        if f.exists():
            m = VIETATE.search(f.read_text(encoding="utf-8"))
            if m:
                errori.append(f"Parola vietata '{m.group(0)}' in {f}")
    return errori


BROWSER_JS = r"""
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const http = require('http'); const fs = require('fs'); const path = require('path');
const ROOT = process.argv[2];
const TIPI = {'.html':'text/html; charset=utf-8','.xml':'application/xml','.txt':'text/plain','.json':'application/json'};
const srv = http.createServer((req, res) => { let p = decodeURIComponent(req.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html';
  const f = path.join(ROOT, p); if (!f.startsWith(ROOT) || !fs.existsSync(f)) { res.writeHead(404); res.end(fs.readFileSync(path.join(ROOT,'404.html'))); return; }
  res.writeHead(200, {'Content-Type': TIPI[path.extname(f)] || 'application/octet-stream'}); res.end(fs.readFileSync(f)); });
srv.listen(0, async () => {
  const base = 'http://127.0.0.1:' + srv.address().port; const out = {pagine: [], prove: []};
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  for (const tema of ['light', 'dark']) {
    const ctx = await b.newContext({ viewport: { width: 375, height: 800 }, colorScheme: tema });
    for (const u of ['/', '/passport-validity/spain/', '/liquids/', '/liquids/barcelona/', '/passport-validity/egypt/'].concat(JSON.parse(process.argv[4])).concat(JSON.parse(process.argv[6])).concat(JSON.parse(process.argv[7]))) {
      const p = await ctx.newPage(); const err = [];
      p.on('console', m => { if (m.type() === 'error' && !m.text().startsWith('[Report Only]')) err.push(m.text()); /* CSP «Report Only» dei riquadri di Google (AdSense acceso): avvisi, non errori della pagina */ }); p.on('pageerror', e => err.push(String(e)));
      await p.goto(base + u, { waitUntil: 'load' });
      const w = await p.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
      out.pagine.push({ url: u, tema: tema, scroll: w[0], larghezza: w[1], errori: err });
      if (tema === 'light' && u === '/passport-validity/spain/') {
        out.prove.push({ caso: 'spagna-etichette', testo: await p.textContent('[data-checker] form') + ' | ' + await p.textContent('[data-nota-schengen]') });
        await p.fill('[name=scadenza]', '2027-02-09'); await p.fill('[name=emissione]', '2020-01-01');
        await p.fill('[name=arrivo]', '2026-11-01'); await p.fill('[name=partenza]', '2026-11-10');
        out.prove.push({ caso: 'spagna-no', testo: await p.textContent('[data-out]') });
        await p.fill('[name=scadenza]', '2027-02-10');
        out.prove.push({ caso: 'spagna-ok', testo: await p.textContent('[data-out]') });
        await p.screenshot({ path: process.argv[3] + '/spagna-375.png', fullPage: false });
      }
      if (tema === 'light' && u === '/liquids/barcelona/') {
        out.prove.push({ caso: 'barcellona', testo: await p.textContent('main'), faq: await p.$$eval('.faq h3', e => e.filter(x => x.getBoundingClientRect().height > 0).length) });
      }
      if (tema === 'light' && u === '/passport-validity/egypt/') {
        const vis = await p.$eval('#visa', e => e.getBoundingClientRect().height > 0);
        await p.click('details.card > summary');
        out.prove.push({ caso: 'egitto', testo: await p.textContent('main'), visa: vis, aperto: await p.$eval('details.card', e => e.open) });
        await p.screenshot({ path: process.argv[3] + '/egitto-375.png', fullPage: false });
      }
      if (tema === 'light' && u === '/cabin-bags/does-my-bag-fit/') {
        const casi = JSON.parse(process.argv[5]);
        for (let i = 0; i < casi.length; i++) { const c = casi[i];
          await p.fill('[name=a]', c[1][0]); await p.fill('[name=b]', c[1][1]); await p.fill('[name=c]', c[1][2]); await p.selectOption('[name=unita]', c[2]);
          const r = await p.evaluate(() => { const m = {}; document.querySelectorAll('[data-gruppo] li[data-slug]').forEach(li => { m[li.dataset.slug] = li.closest('[data-gruppo]').dataset.gruppo; });
            return { mappa: m, errore: !!document.querySelector('[data-errore-borsa]'), testo: document.querySelector('[data-out]').textContent }; });
          out.prove.push({ caso: 'borsa:' + i, testo: r.testo, mappa: r.mappa, errore: r.errore });
          if (i === 0) await p.screenshot({ path: process.argv[3] + '/borsa-375.png', fullPage: false }); }
      }
      if (u.startsWith('/cabin-bags/')) {
        out.prove.push({ caso: 'bag:' + tema + ':' + u, testo: await p.textContent('main'),
                         citazioni: await p.$$eval('blockquote.cit', e => e.filter(x => x.getBoundingClientRect().height > 0).length) });
        if (tema === 'light') await p.screenshot({ path: process.argv[3] + '/' + u.split('/').filter(Boolean).join('-') + '-375.png', fullPage: true });
      }
      if (u.startsWith('/canadian-passport/') || u.startsWith('/australian-passport/')) {
        const vis = async (sel) => p.$eval(sel, e => { const r = e.getBoundingClientRect(); return r.height > 0 && r.width > 0 && r.width <= window.innerWidth; }).catch(() => false);
        out.prove.push({ caso: 'estero:' + tema + ':' + u, testo: await p.textContent('main'), visa: await vis('#visa'), passport: await vis('#passport'),
                         citazioni: await p.$$eval('blockquote.cit', e => e.filter(x => x.getBoundingClientRect().height > 0).length) });
        if (tema === 'light') await p.screenshot({ path: process.argv[3] + '/' + u.split('/').filter(Boolean).join('-') + '-375.png', fullPage: false });
      }
      if (u.startsWith('/tolls-rental-car/') || u.startsWith('/winter-tyres-rental-car/') || u.startsWith('/foreign-licence-canada-australia-nz/') || u.startsWith('/public-transport-rules/') ||
          u.startsWith('/train-luggage-rules/') || u.startsWith('/eurostar-check-in-times/') || u.startsWith('/scooter-rental-licence/') || u.startsWith('/ticket-release-dates/') || u.startsWith('/blue-badge-abroad/')) {
        const vis = async (sel) => p.$eval(sel, e => { const r = e.getBoundingClientRect(); return r.height > 0 && r.width > 0 && r.width <= window.innerWidth; }).catch(() => false);
        out.prove.push({ caso: 'ped:' + tema + ':' + u, testo: await p.textContent('main'), risposta: await vis('#answer'), btn: await vis('[data-noleggio] a.btn'),
                         citazioni: await p.$$eval('blockquote.cit', e => e.filter(x => x.getBoundingClientRect().height > 0).length) });
        if (tema === 'light') await p.screenshot({ path: process.argv[3] + '/' + u.split('/').filter(Boolean).join('-') + '-375.png', fullPage: false });
      }
      if (u.startsWith('/driving-abroad/')) {
        out.prove.push({ caso: 'pat:' + tema + ':' + u, testo: await p.textContent('main'),
                         risposta: await p.$eval('#answer', e => { const r = e.getBoundingClientRect(); return r.height > 0 && r.width <= window.innerWidth; }).catch(() => false),
                         citazioni: await p.$$eval('blockquote.cit', e => e.filter(x => x.getBoundingClientRect().height > 0).length) });
        if (tema === 'light') await p.screenshot({ path: process.argv[3] + '/' + u.split('/').filter(Boolean).join('-') + '-375.png', fullPage: false });
      }
      if (u.startsWith('/it/documenti/')) {
        const vis = async (sel) => p.$eval(sel, e => { const r = e.getBoundingClientRect(); return r.height > 0 && r.width > 0 && r.width <= window.innerWidth; }).catch(() => false);
        const x = { caso: 'it:' + tema + ':' + u, testo: await p.textContent('main'), lang: await p.$eval('html', e => e.lang),
                    documento: await vis('#documento'), visto: await vis('#visto'), citazioni: await p.$$eval('blockquote.cit', e => e.filter(y => y.getBoundingClientRect().height > 0).length) };
        if (u === '/it/documenti/') {
          await p.fill('[data-filtro=lista-it]', 'egit');
          x.righe = await p.$$eval('#lista-it tr[data-voce]', e => e.filter(y => !y.hidden).map(y => y.textContent.trim().slice(0, 40)));
          await p.fill('[data-filtro=lista-it]', '');
        }
        out.prove.push(x);
        if (tema === 'light') await p.screenshot({ path: process.argv[3] + '/' + u.split('/').filter(Boolean).join('-') + '-375.png', fullPage: false });
      }
      if (tema === 'light' && u === '/') {
        const scegli = async (nome) => { const i = await p.evaluate((n) => { const s = document.querySelector('[name=paese]'); return [...s.options].findIndex(o => o.textContent === n); }, nome);
          await p.selectOption('[name=paese]', String(i - 1)); };
        await scegli('Colombia');
        out.prove.push({ caso: 'colombia-manuale', testo: await p.textContent('[data-out]') });
        await scegli('Ireland');
        out.prove.push({ caso: 'irlanda', testo: await p.textContent('[data-out]') });
        await scegli('Thailand');
        await p.fill('[name=scadenza]', '2027-04-10'); await p.fill('[name=arrivo]', '2026-10-10'); await p.fill('[name=partenza]', '2027-05-01');
        out.prove.push({ caso: 'thailandia-scade', testo: await p.textContent('[data-out]'), verde: await p.$$eval('[data-out] .esito.si', e => e.length) });
        await scegli('Belize');
        await p.fill('[name=scadenza]', '2027-01-15'); await p.fill('[name=arrivo]', '2026-10-10'); await p.fill('[name=partenza]', '2026-10-20');
        out.prove.push({ caso: 'belize-avviso', testo: await p.textContent('[data-out]') });
        await p.screenshot({ path: process.argv[3] + '/home-375.png', fullPage: false });
      }
      if (u === '/') {
        // contrasto del risultato del controllo (dentro la fascia scura della home) in entrambi i temi
        const scegli2 = async (nome) => { const i = await p.evaluate((n) => { const s = document.querySelector('[name=paese]'); return [...s.options].findIndex(o => o.textContent === n); }, nome);
          await p.selectOption('[name=paese]', String(i - 1)); };
        await scegli2('Spain');
        await p.fill('[name=scadenza]', '2027-02-10'); await p.fill('[name=emissione]', '2017-03-01'); await p.fill('[name=arrivo]', '2026-12-20'); await p.fill('[name=partenza]', '2027-01-03');
        const minimo = await p.evaluate(() => {
          const lum = c => { const a = c.match(/[\d.]+/g).map(Number); const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return .2126 * f(a[0]) + .7152 * f(a[1]) + .0722 * f(a[2]); };
          const sfondo = el => { while (el) { const b = getComputedStyle(el).backgroundColor; const m = b.match(/[\d.]+/g); if (m && (m[3] === undefined || +m[3] > .5)) return b; el = el.parentElement; } return 'rgb(255,255,255)'; };
          let peggiore = [99, ''];
          for (const el of document.querySelectorAll('[data-checker] *')) {
            const t = [...el.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim()).map(n => n.textContent.trim()).join(' ');
            if (!t || !el.getBoundingClientRect().width) continue;
            const l1 = lum(getComputedStyle(el).color), l2 = lum(sfondo(el)); const r = (Math.max(l1, l2) + .05) / (Math.min(l1, l2) + .05);
            if (r < peggiore[0]) peggiore = [r, t.slice(0, 40)];
          }
          return peggiore; });
        out.prove.push({ caso: 'contrasto-' + tema, testo: minimo[1], rapporto: minimo[0] });
      }
      await p.close(); }
    await ctx.close(); }
  const largo = await b.newContext({ viewport: { width: 820, height: 900 } });
  for (const u of ['/', '/cabin-bags/', '/cabin-bags/ryanair/', '/available-in/', '/available-in/apple-pay/', '/driving-abroad/', '/driving-abroad/canadian-licence/', '/tolls-rental-car/', '/winter-tyres-rental-car/', '/foreign-licence-canada-australia-nz/', '/public-transport-rules/', '/train-luggage-rules/', '/eurostar-check-in-times/']) { const p = await largo.newPage(); await p.goto(base + u, { waitUntil: 'load' });
    const w = await p.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]); out.pagine.push({ url: u, tema: '820px', scroll: w[0], larghezza: w[1], errori: [] }); await p.close(); }
  await largo.close();
  await b.close(); srv.close(); console.log(JSON.stringify(out)); });
"""


def _pagine_estere():
    """4 pagine nuove per la prova a 375 px: 2 canadesi e 2 australiane (Giappone e Francia, se esistono; altrimenti le prime disponibili)."""
    out = []
    for k in G.ESTERI:
        vv = G.VOCI[k]
        scelte = [v for v in vv if v["slug"] in ("japan", "france")] or vv[:2]
        if len(scelte) < 2:
            scelte += [v for v in vv if v not in scelte][:2 - len(scelte)]
        out += ["/" + v["url_pag"] for v in scelte[:2]]
    return out


PAGINE_ESTERE_BROWSER = _pagine_estere()
PAGINE_IT_BROWSER = ["/it/documenti/", "/it/documenti/egitto/", "/it/documenti/spagna/", "/it/documenti/stati-uniti/"]
PAGINE_SRV_BROWSER = ["/available-in/", "/available-in/starlink/", "/available-in/starlink/pakistan/", "/available-in/spotify/china/",
                      "/available-in/youtube-premium/russia/", "/available-in/google-wallet/", "/available-in/google-wallet/india/",
                      "/available-in/wise/pakistan/", "/available-in/uber/united-arab-emirates/"]  # ultime 4 dal 7/11/2026
PAGINE_PAT_BROWSER = ["/driving-abroad/", "/driving-abroad/uk-licence/", "/driving-abroad/uk-licence/japan/", "/driving-abroad/canadian-licence/italy/",
                      "/driving-abroad/australian-licence/united-states/"]
PAGINE_PED_BROWSER = ["/tolls-rental-car/", "/tolls-rental-car/portugal/", "/tolls-rental-car/austria/", "/tolls-rental-car/france/"]
PAGINE_GOM_BROWSER = ["/winter-tyres-rental-car/", "/winter-tyres-rental-car/italy/", "/winter-tyres-rental-car/austria/", "/winter-tyres-rental-car/france/"]
PAGINE_TR_BROWSER = ["/public-transport-rules/", "/public-transport-rules/prague/", "/public-transport-rules/milan/", "/public-transport-rules/budapest/"]
PAGINE_TB_BROWSER = ["/train-luggage-rules/", "/train-luggage-rules/eurostar/", "/train-luggage-rules/ouigo-spain/", "/train-luggage-rules/avlo/",
                     "/eurostar-check-in-times/"]
PAGINE_SC_BROWSER = ["/scooter-rental-licence/", "/scooter-rental-licence/france/", "/scooter-rental-licence/greece/",
                     "/ticket-release-dates/ghibli-museum/", "/ticket-release-dates/washington-monument/", "/ticket-release-dates/grand-sumo-tournaments/"]
PAGINE_BB_BROWSER = ["/blue-badge-abroad/", "/blue-badge-abroad/italy/", "/blue-badge-abroad/spain/", "/blue-badge-abroad/european-disability-card/",
                     "/public-transport-rules/amsterdam/"]
PAGINE_FL_BROWSER = ["/foreign-licence-canada-australia-nz/", "/foreign-licence-canada-australia-nz/canada/ontario/", "/foreign-licence-canada-australia-nz/australia/new-south-wales/", "/foreign-licence-canada-australia-nz/new-zealand/"]
PAGINE_BAG_BROWSER = ["/cabin-bags/", "/cabin-bags/ryanair/", "/cabin-bags/does-my-bag-fit/", "/cabin-bags/size/40x30x20/", "/cabin-bags/eu-personal-item-rule/"]


def controlla_browser():
    if os.environ.get("BYF_NO_BROWSER") == "1":
        return ["controllo nel browser saltato (BYF_NO_BROWSER=1)"], None
    cartella = tempfile.mkdtemp()
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(BROWSER_JS)
    try:
        r = subprocess.run(["node", fh.name, str(SITO), cartella, json.dumps(PAGINE_ESTERE_BROWSER), json.dumps(CASI_BORSA), json.dumps(PAGINE_BAG_BROWSER),
                            json.dumps(PAGINE_IT_BROWSER + PAGINE_SRV_BROWSER + PAGINE_PAT_BROWSER + PAGINE_PED_BROWSER + PAGINE_GOM_BROWSER + PAGINE_FL_BROWSER + PAGINE_TR_BROWSER + PAGINE_TB_BROWSER + PAGINE_SC_BROWSER + PAGINE_BB_BROWSER)],
                           capture_output=True, text=True, timeout=600)
    finally:
        os.unlink(fh.name)
    if r.returncode != 0:
        return ["Errore Playwright: " + r.stderr[:800]], None
    o = json.loads(r.stdout)
    errori = []
    for p in o["pagine"]:
        if p["scroll"] > p["larghezza"]:
            errori.append(f"Scorrimento orizzontale in {p['url']} ({p['tema']}): {p['scroll']} > {p['larghezza']}")
        if p["errori"]:
            errori.append(f"Errori in console in {p['url']} ({p['tema']}): {p['errori'][:2]}")
    prove = {x["caso"]: x["testo"] for x in o["prove"]}
    if "do NOT meet" not in prove.get("spagna-no", "") or "1 day short" not in prove.get("spagna-no", ""):
        errori.append(f"Prova Spagna 'no' fallita: {prove.get('spagna-no', '')[:200]}")
    if "Your dates meet the rule" not in prove.get("spagna-ok", "") or "0 days to spare" not in prove.get("spagna-ok", ""):
        errori.append(f"Prova Spagna 'ok' fallita: {prove.get('spagna-ok', '')[:200]}")
    if "No automatic check for this destination" not in prove.get("colombia-manuale", ""):
        errori.append(f"Prova Colombia 'manuale' fallita: {prove.get('colombia-manuale', '')[:200]}")
    if "Date you first enter the Schengen area" not in prove.get("spagna-etichette", "") or "Date you leave the Schengen area" not in prove.get("spagna-etichette", ""):
        errori.append("Etichette Schengen mancanti sulla pagina Spagna")
    ir = prove.get("irlanda", "")
    if "Irish immigration officers are entitled to ask for proof of British nationality in the course of their work." not in ir:
        errori.append(f"Irlanda: testo ufficiale tagliato o mancante nel risultato: {ir[-200:]}")
    th = next((x for x in o["prove"] if x["caso"] == "thailandia-scade"), {})
    if "expires before you leave" not in th.get("testo", "") or th.get("verde"):
        errori.append(f"Thailandia: manca l'avviso rosso o compare il verde: {th.get('testo', '')[:200]}")
    if "Some airlines may refuse boarding" not in prove.get("belize-avviso", ""):
        errori.append("Belize: avviso delle compagnie aeree assente dal risultato")
    for x in o["prove"]:
        if x["caso"].startswith("contrasto-") and x.get("rapporto", 0) < 4.5:
            errori.append(f"Contrasto insufficiente nel controllo della home ({x['caso'][10:]}): {x['rapporto']:.2f}:1 su “{x['testo']}”")
    bc = next((x for x in o["prove"] if x["caso"] == "barcellona"), {})
    if "Can I take liquids over 100 ml through security at Barcelona-El Prat (BCN)?" not in bc.get("testo", "") or not bc.get("faq"):
        errori.append("Barcellona: risposta diretta o FAQ non visibili nel browser")
    eg = next((x for x in o["prove"] if x["caso"] == "egitto"), {})
    if not eg.get("visa") or "normally need a visa" not in eg.get("testo", "") or not eg.get("aperto"):
        errori.append("Egitto: sezione visti non visibile o dettagli che non si aprono")
    for u in PAGINE_ESTERE_BROWSER:
        for tema in ("light", "dark"):
            x = next((y for y in o["prove"] if y["caso"] == f"estero:{tema}:{u}"), None)
            if not x:
                errori.append(f"{u} ({tema}): prova nel browser non eseguita")
                continue
            pop = "Canadians" if u.startswith("/canadian") else "Australians"
            if not x["visa"] or not x["passport"] or x["citazioni"] < 2 or f"Do {pop} need a visa for" not in x["testo"]:
                errori.append(f"{u} ({tema}): sezione visti o validità non visibile, o citazioni ufficiali mancanti a 375 px")
    if len(PAGINE_ESTERE_BROWSER) < 4:
        errori.append(f"prova nel browser su {len(PAGINE_ESTERE_BROWSER)} pagine nuove invece di 4 (mancano i dati di un passaporto?)")
    for i, (nome, valori, unita) in enumerate(CASI_BORSA):
        x = next((y for y in o["prove"] if y["caso"] == f"borsa:{i}"), None)
        atteso = _attesi_borsa(valori, unita)
        if not x:
            errori.append(f"strumento borsa: caso '{nome}' non eseguito")
        elif atteso is None:
            if not x["errore"] or x["mappa"]:
                errori.append(f"strumento borsa: caso '{nome}' doveva dare un messaggio d'errore e nessun risultato")
        elif x["mappa"] != atteso:
            diff = {k: (x["mappa"].get(k), v) for k, v in atteso.items() if x["mappa"].get(k) != v}
            errori.append(f"strumento borsa: caso '{nome}' diverso dal Python (browser, atteso): {diff}")
    p0 = next((y for y in o["prove"] if y["caso"] == "borsa:0"), {}); p1 = next((y for y in o["prove"] if y["caso"] == "borsa:1"), {})
    if not p0.get("mappa") or p0.get("mappa") != p1.get("mappa"):
        errori.append("strumento borsa: la borsa ruotata non dà lo stesso risultato")
    for u in PAGINE_BAG_BROWSER:
        for tema in ("light", "dark"):
            x = next((y for y in o["prove"] if y["caso"] == f"bag:{tema}:{u}"), None)
            if not x or (u != "/cabin-bags/does-my-bag-fit/" and u != "/cabin-bags/" and u != "/cabin-bags/size/40x30x20/" and x["citazioni"] < 2):
                errori.append(f"{u} ({tema}): pagina non provata o citazioni ufficiali non visibili a 375 px")
    rb = next((y for y in o["prove"] if y["caso"] == "bag:light:/cabin-bags/ryanair/"), {})
    if "Ryanair free bag: 40 x 30 x 20 cm under the seat" not in rb.get("testo", ""):
        errori.append("Ryanair: risposta diretta non visibile nel browser")
    for u in PAGINE_IT_BROWSER:
        for tema in ("light", "dark"):
            x = next((y for y in o["prove"] if y["caso"] == f"it:{tema}:{u}"), None)
            if not x:
                errori.append(f"{u} ({tema}): prova nel browser non eseguita")
                continue
            if x["lang"] != "it" or "Le regole cambiano" not in x["testo"]:
                errori.append(f"{u} ({tema}): lingua o avvertenza mancanti")
            if u != "/it/documenti/" and (not x["documento"] or not x["visto"] or x["citazioni"] < 2):
                errori.append(f"{u} ({tema}): sezioni documento/visto o citazioni non visibili a 375 px")
            if u == "/it/documenti/" and tema == "light" and (len(x.get("righe", [])) != 1 or "Egitto" not in x["righe"][0]):
                errori.append(f"indice italiano: la ricerca «egit» non lascia solo l'Egitto: {x.get('righe')}")
    for u in PAGINE_PAT_BROWSER:
        for tema in ("light", "dark"):
            x = next((y for y in o["prove"] if y["caso"] == f"pat:{tema}:{u}"), None)
            if not x or not x["risposta"] or (u.count("/") == 4 and x["citazioni"] < 2):
                errori.append(f"{u} ({tema}): risposta in alto o citazioni ufficiali non visibili a 375 px")
    for u in PAGINE_PED_BROWSER + PAGINE_GOM_BROWSER:
        for tema in ("light", "dark"):
            x = next((y for y in o["prove"] if y["caso"] == f"ped:{tema}:{u}"), None)
            if not x or not x["risposta"] or (G.NOLEGGIO_AUTO and not x["btn"]) or (u.count("/") == 3 and x["citazioni"] < 3):
                errori.append(f"{u} ({tema}): risposta, pulsante DiscoverCars o citazioni non visibili a 375 px")
    for u in PAGINE_FL_BROWSER:
        for tema in ("light", "dark"):
            x = next((y for y in o["prove"] if y["caso"] == f"ped:{tema}:{u}"), None)
            if not x or not x["risposta"] or (G.NOLEGGIO_AUTO and not x["btn"]) or (u != "/foreign-licence-canada-australia-nz/" and x["citazioni"] < 3):
                errori.append(f"{u} ({tema}): risposta, pulsante DiscoverCars o citazioni non visibili a 375 px")
    for u in PAGINE_TR_BROWSER:
        for tema in ("light", "dark"):
            x = next((y for y in o["prove"] if y["caso"] == f"ped:{tema}:{u}"), None)
            if not x or not x["risposta"] or x["btn"] or (u != "/public-transport-rules/" and x["citazioni"] < 3):
                errori.append(f"{u} ({tema}): risposta o citazioni non visibili a 375 px, o riquadro di affiliazione presente")
    for u in PAGINE_TB_BROWSER:
        for tema in ("light", "dark"):
            x = next((y for y in o["prove"] if y["caso"] == f"ped:{tema}:{u}"), None)
            if not x or not x["risposta"] or x["btn"] or (u != "/train-luggage-rules/" and x["citazioni"] < 3):
                errori.append(f"{u} ({tema}): risposta o citazioni non visibili a 375 px, o riquadro di affiliazione presente")
    for u in PAGINE_SC_BROWSER:  # scooter e biglietti (31/10/2026): risposta e citazioni visibili a 375 px, nessun riquadro di noleggio
        for tema in ("light", "dark"):
            x = next((y for y in o["prove"] if y["caso"] == f"ped:{tema}:{u}"), None)
            if not x or not x["risposta"] or x["btn"] or (u != "/scooter-rental-licence/" and x["citazioni"] < 2):
                errori.append(f"{u} ({tema}): risposta o citazioni non visibili a 375 px, o riquadro di noleggio presente")
    for u in PAGINE_BB_BROWSER:  # Blue Badge (4/11/2026) e Amsterdam: risposta e citazioni visibili a 375 px, nessun riquadro di affiliazione
        for tema in ("light", "dark"):
            x = next((y for y in o["prove"] if y["caso"] == f"ped:{tema}:{u}"), None)
            if not x or not x["risposta"] or x["btn"] or x["citazioni"] < 3:
                errori.append(f"{u} ({tema}): risposta o citazioni non visibili a 375 px, o riquadro di affiliazione presente")
    if sum(1 for x in o["prove"] if x["caso"].startswith("contrasto-")) != 2:
        errori.append("Prova del contrasto del controllo (tema chiaro e scuro) non eseguita")
    return errori, (o, cartella)


def controlla_altri_siti():
    """15. Blocco "Other useful tools for your trip" in ogni pagina indicizzabile: gli stessi link di genera.ALTRI_SITI (ALTRI_SITI_IT nelle pagine italiane),
    nell'ordine, da 3 a 4, mai a questo sito, tutti con rel="noopener" e senza nofollow o sponsored."""
    errori = []
    n = 0
    for f in sorted(SITO.rglob("*.html")):
        rel = f.relative_to(SITO).as_posix()
        if f.name == "404.html" or f.name.startswith("google"):
            continue
        n += 1
        t = f.read_text(encoding="utf-8")
        blocchi = re.findall(r'<div class="f-altri"><h2>(.*?)</h2><ul>(.*?)</ul></div>', t, re.S)
        if len(blocchi) != 1:
            errori.append(f"blocco altri siti mancante o doppio in {rel}")
            continue
        titolo, voci = blocchi[0]
        it = rel.startswith(G.IT_BASE + "/")
        attesi, titolo_atteso = (G.ALTRI_SITI_IT, "Altri strumenti utili per il viaggio") if it else (G.ALTRI_SITI, "Other useful tools for your trip")
        if titolo != titolo_atteso:
            errori.append(f"titolo del blocco altri siti sbagliato in {rel}: {titolo}")
        link = re.findall(r"<a ([^>]*)>", voci)
        url = [re.search(r'href="([^"]+)"', a).group(1) for a in link]
        if url != [u for u, _, _ in attesi] or not 3 <= len(url) <= 4:
            errori.append(f"link del blocco altri siti diversi da genera.py in {rel}: {url}")
        for a, u in zip(link, url):
            if u.startswith(G.URL_SITO) or 'rel="noopener"' not in a or "nofollow" in a or "sponsored" in a:
                errori.append(f"link sbagliato nel blocco altri siti in {rel}: {a}")
    return errori, n


# ---------------------------------------------------------------- 17. "Is [service] available in [country]?" (28/10/2026)
_spec_srv = importlib.util.spec_from_file_location("raccolta_servizi", Path(__file__).resolve().parent / "raccolta" / "servizi.py")
RS = importlib.util.module_from_spec(_spec_srv)
_spec_srv.loader.exec_module(RS)
# Nomi di assistenti e modelli di intelligenza artificiale (al contrario, come _AL_CONTRARIO): mai nelle pagine nuove
_AI_CONTRARIO = _AL_CONTRARIO + ["keespeed", "ytixelprep", "korg", "drab"]
VIETATE_SRV = re.compile(r"\b(" + "|".join(w[::-1] for w in _AI_CONTRARIO) + r")\b", re.I)
# Consigli per aggirare blocchi o leggi: mai nelle pagine nuove (le affiliazioni VPN non sono attive e non si consigliano)
AGGIRARE = re.compile(r"\bVPN\b|\bproxy\b|smart ?DNS|get around|bypass|circumvent|change your (?:region|location)|unblock", re.I)


def _attesa_breve(slug, voce, invio=False):
    """Etichetta attesa, scritta qui di nuovo (controllo indipendente da genera.breve_srv). invio = Wise, Paese nella lista "send to"."""
    if voce is None:
        return "Not for holding money" if (slug == "wise" and invio) else "Not on the list"
    st = voce["stato"]
    if st == "si":
        # Google Wallet (7/11/2026): app nella lista ma croce rossa sulla riga "Tap to pay"
        return "Yes, no tap to pay" if slug == "google-wallet" and voce.get("tocco") is False else "Yes"
    if st == "in_arrivo":
        return "Coming soon"
    if st == "per_regione":  # Starlink "exclude": il Paese è colorato regione per regione (revisione del 28/10/2026)
        return "By region"
    if slug == "starlink":
        return "No service shown"
    if slug == "youtube-premium":
        return voce["nota"][0].upper() + voce["nota"][1:]
    if slug == "wise":  # tra i Paesi dove Wise non offre i servizi (7/11/2026)
        return "Not supported"
    return "Not listed"


def _attesa_inizio(slug, voce, invio=False):
    if voce is None:
        if slug == "wise" and invio:  # revisione del 7/11/2026: niente "No" per chi può inviare denaro
            return "Not for holding money:"
        return "Not known." if slug == "starlink" else "No, not according to the official list."
    return {"si": "Yes.", "in_arrivo": "Not yet.", "per_regione": "It depends on the region.", "no": "No"}[voce["stato"]]


def controlla_servizi():
    from html import unescape
    errori = []
    conti = {"servizi": 0, "pagine": 0, "righe": 0, "faq": 0, "citazioni": 0, "cache": "assente"}
    f = SITO.parent / "dati" / "servizi.json"
    if not f.exists():
        return ["dati/servizi.json mancante (lanciare raccolta/servizi.py)"], conti
    D = json.loads(f.read_text(encoding="utf-8"))
    dom = json.loads((SITO.parent / "dati" / "servizi_domanda.json").read_text(encoding="utf-8"))["servizi"]
    iso = {p["iso2"] for p in json.loads((SITO.parent / "dati" / "paesi_iso.json").read_text(encoding="utf-8"))["paesi"]}
    sm = leggi("sitemap.xml")
    # ricalcolo dalla cache delle pagine grezze (fuori dal repository): le liste del JSON devono essere quelle delle pagine salvate
    cache = RS.CACHE
    if all((cache / f"{k}.{F['tipo']}").exists() for k, F in RS.FONTI.items()):
        conti["cache"] = "presente"
        grezzi = {k: (cache / f"{k}.{F['tipo']}").read_text(encoding="utf-8") for k, F in RS.FONTI.items()}
        ef = []
        for S in D["servizi"]:
            paesi, extra = RS.costruisci(S["slug"], grezzi)
            if paesi != S["paesi"]:
                ef.append(f"servizi {S['slug']}: la lista del JSON non è quella ricalcolata dalla pagina salvata")
            for k in RS.LISTE_IN_PIU:  # Google Pay online, Wise invio (7/11/2026)
                if extra.get(k) != S.get("extra", {}).get(k):
                    ef.append(f"servizi {S['slug']}: lista in più '{k}' diversa da quella ricalcolata dalla pagina salvata")
        for k, x in D["frasi"].items():
            if x["frase"] not in RS.testo(grezzi[x["fonte"]]):
                ef.append(f"servizi: frase {k} non più nella pagina salvata")
        f_rec = max((cache / f"{k}.{F['tipo']}" for k, F in RS.FONTI.items()), key=lambda f: f.stat().st_mtime)
        errori += esito_copia(17, "servizi", ef, f_rec, D.get("letto_il"))
    else:
        avviso(17, f"copie salvate delle liste ufficiali assenti o incomplete ({cache.relative_to(SITO.parent)}/, fuori dal repository): ricalcolo "
                   "delle liste e delle frasi dalle copie saltato; dati dell'ultima lettura buona (python3 -I beforeyoufly/raccolta/servizi.py)")
    if {S["slug"] for S in D["servizi"]} & {w[::-1] for w in _AI_CONTRARIO} or VIETATE_SRV.search(json.dumps(D, ensure_ascii=False)):
        errori.append("servizi: un assistente di intelligenza artificiale tra i servizi")
    for S in D["servizi"]:
        conti["servizi"] += 1
        sl = S["slug"]
        if RS.impronta(S["paesi"], S.get("extra")) != S["impronta"]:
            errori.append(f"servizi {sl}: impronta diversa dalla lista")
        if not S["url_fonte"].startswith("https://") or not S["pagina"].startswith("https://") or S.get("http") != 200:
            errori.append(f"servizi {sl}: fonte non https o lettura non 200")
        if set(S["paesi"]) - iso:
            errori.append(f"servizi {sl}: codici non ISO {sorted(set(S['paesi']) - iso)[:5]}")
        t = leggi(f"{G.SRV_BASE}/{sl}/index.html")
        d = G.data_lunga(S["letto_il"])
        if escape(S["pagina"]) not in t or f"checked on {d}" not in t:
            errori.append(f"servizi {sl}: pagina del servizio senza fonte o data")
        righe = dict(re.findall(r'<tr data-voce id="([a-z]{2})"><td[^>]*>.*?</td><td[^>]*><span class="badge[^"]*">([^<]*)</span>', t))
        if len(righe) != len(iso):
            errori.append(f"servizi {sl}: {len(righe)} righe nella tabella invece di {len(iso)}")
        for c in iso:
            atteso = _attesa_breve(sl, S["paesi"].get(c), c in S.get("extra", {}).get("invio", []))
            if unescape(righe.get(c.lower(), "")) != atteso:
                errori.append(f"servizi {sl}: riga {c} '{righe.get(c.lower())}' invece di '{atteso}'")
            conti["righe"] += 1
        if f"<loc>{G.URL_SITO}/{G.SRV_BASE}/{sl}/</loc><lastmod>{S['letto_il']}</lastmod>" not in sm:
            errori.append(f"servizi {sl}: pagina del servizio non in sitemap o lastmod diverso dalla lettura")
        # pagine servizio × Paese: esistono esattamente per le coppie con ricerche vere
        attese = {c for c in dom.get(sl, {}) if c in iso}
        cartella = SITO / G.SRV_BASE / sl
        trovate = {p.parent.name for p in cartella.glob("*/index.html")}
        if trovate != {G.slug_srv(c) for c in attese}:
            errori.append(f"servizi {sl}: pagine Paese diverse dalle coppie con domanda: {sorted(trovate ^ {G.slug_srv(c) for c in attese})[:6]}")
        for c in attese:
            rel = f"{G.SRV_BASE}/{sl}/{G.slug_srv(c)}/"
            if not (SITO / rel / "index.html").exists():
                continue
            conti["pagine"] += 1
            t = leggi(rel + "index.html")
            voce = S["paesi"].get(c)
            m = re.search(r'<p class="lead" id="answer">(.*?)</p>', t)
            r = unescape(m.group(1)) if m else ""
            invio = c in S.get("extra", {}).get("invio", [])
            if not r.startswith(_attesa_inizio(sl, voce, invio)) or f"checked on {d})" not in r:
                errori.append(f"{rel}: prima frase senza la risposta attesa, la fonte o la data: {r[:90]}")
            if voce and voce.get("nota") and voce["stato"] != "no" and f"“{voce['nota']}”" not in r:
                errori.append(f"{rel}: la nota della fonte non è nella risposta")
            # Google Wallet: la riga "Tap to pay" della fonte nella prima frase; FAQ Google Pay con la lista online (7/11/2026)
            if sl == "google-wallet" and voce and voce["stato"] == "si":
                atteso_t = "as available there." if voce["tocco"] else "as not available there."
                if f"shows tap to pay (contactless payments in shops) {atteso_t}" not in r:
                    errori.append(f"{rel}: la riga 'Tap to pay' della fonte non è nella risposta")
            if sl == "google-wallet":
                on = c in S["extra"]["online"]
                frase_on = "Google Pay on participating websites and apps includes" if on else "is not on Google's list of countries where you can pay with Google Pay"
                if frase_on not in unescape(t):
                    errori.append(f"{rel}: frase su Google Pay online diversa dalla lista")
            # revisione del 7/11/2026: Uber elenca città, Stripe è per le aziende ed etichette non spiegate
            if sl == "uber" and voce and "Uber's page lists cities, not whole countries" not in r:
                errori.append(f"{rel}: manca la frase fissa sulle città di Uber nella risposta")
            if sl == "stripe" and ("businesses opening a Stripe account" not in unescape(t)
                                   or (voce and voce.get("nota") and "Stripe's page does not explain these labels" not in r)):
                errori.append(f"{rel}: manca la frase su chi riguarda la lista Stripe o sulle etichette non spiegate")
            if sl == "wise" and voce is None and invio and ("Not for holding money" not in t or 'class="esito e-srv no"' in t):
                errori.append(f"{rel}: Paese della lista 'send to' mostrato come un No")
            if sl == "wise":
                inv = c in S["extra"]["invio"]
                if inv != ("is on Wise's list of countries and regions you can send money to" in unescape(t)):
                    errori.append(f"{rel}: frase sull'invio con Wise diversa dalla lista")
            if voce is None and "is not the same as being banned" not in t and sl != "starlink" and not (sl == "wise" and invio):
                errori.append(f"{rel}: manca la frase 'non nella lista non vuol dire vietato'")
            if re.search(r"\b(?:is|are) (?:banned|illegal|blocked|prohibited)\b", unescape(t), re.I):
                errori.append(f"{rel}: la pagina dice 'vietato/bloccato', che nessuna fonte dice")
            if escape(S["pagina"]) not in t or f'href="../../../{G.SRV_BASE}/{sl}/"' not in t or f'href="../../../{G.SRV_BASE}/"' not in t:
                errori.append(f"{rel}: link alla fonte, alla pagina del servizio o all'indice mancanti")
            for k in G.CIT_SRV[sl][0] + G.CIT_SRV[sl][1]:
                conti["citazioni"] += 1
                if escape(D["frasi"][k]["frase"]) not in t:
                    errori.append(f"{rel}: citazione {k} mancante")
            if f"<loc>{G.URL_SITO}/{rel}</loc><lastmod>{S['letto_il']}</lastmod>" not in sm:
                errori.append(f"{rel}: non in sitemap o lastmod diverso dalla lettura")
            # FAQ: JSON-LD = testo visibile, prima risposta = prima frase della pagina
            ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t)]
            faq = [x for x in ld if x.get("@type") == "FAQPage"]
            vis = [(unescape(q), unescape(a)) for q, a in re.findall(r"<h3>(.*?)</h3><p>(.*?)</p>", t[t.find('<section class="faq">'):])]
            if len(faq) != 1 or [(x["name"], x["acceptedAnswer"]["text"]) for x in faq[0]["mainEntity"]] != vis or not vis or vis[0][1] != r:
                errori.append(f"{rel}: FAQ JSON-LD diversa dal testo visibile o dalla prima frase")
            conti["faq"] += len(vis)
            tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
            if len(tit) > 70 or not tit.startswith((f"Is {S['nome']} Available in", f"{S['nome']} in")):
                errori.append(f"{rel}: titolo oltre 70 caratteri o senza la domanda: {tit}")
    # tutte le pagine nuove: niente nomi di assistenti, niente consigli per aggirare, link da home, menu e About
    for p in (SITO / G.SRV_BASE).rglob("*.html"):
        t = unescape(re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8")))
        m = VIETATE_SRV.search(t) or AGGIRARE.search(t)
        if m:
            errori.append(f"{p.relative_to(SITO)}: parola vietata '{m.group(0)}'")
    home = leggi("index.html")
    if f'href="{G.SRV_BASE}/"' not in home or "Apps by country" not in home:
        errori.append("home senza link alla sezione 'Apps by country'")
    if f'href="../{G.SRV_BASE}/"' not in leggi("about/index.html") or 'id="available-in"' not in leggi("about/index.html"):
        errori.append("About senza la sezione o senza il link 'Apps by country'")
    if f"<loc>{G.URL_SITO}/{G.SRV_BASE}/</loc>" not in sm:
        errori.append("indice available-in non in sitemap")
    return errori, conti


# ---------------------------------------------------------------- 18. Guidare all'estero: serve il permesso internazionale? (28/10/2026)
_spec_pat = importlib.util.spec_from_file_location("raccolta_patenti", Path(__file__).resolve().parent / "raccolta" / "patenti.py")
RPAT = importlib.util.module_from_spec(_spec_pat)
_spec_pat.loader.exec_module(RPAT)
FONTI_UFFICIALI_PAT = re.compile(r"^https://(?:www\.gov\.uk/|travel\.gc\.ca/|data\.international\.gc\.ca/|www\.smartraveller\.gov\.au/)")
# noleggi e reti non ammessi: mai nelle pagine di questa sezione (nomi vietati anche come testo).
AFFILIATI_PAT = re.compile(r'rentalcars|economybookings|localrent|qeeq|travelpayouts|tp\.media|'
                           r'impact\.com|partnerize|cj\.com|kayak\.|skyscanner|booking\.com|expedia', re.I)
# Dal 30/10/2026 l'UNICO link di affiliazione ammesso nella sezione (e nella riga della home che la presenta) è DiscoverCars, link generale
# con il nostro a_aid (dati/affiliati.json, "_discovercars_noleggio"): https, host discovercars.com, nessun percorso profondo inventato,
# rel="sponsored noopener", target="_blank", riga di trasparenza nel riquadro, riquadro dopo la risposta e le regole ufficiali.
NOLEGGIO_AID = "Massimilianocori"


def link_noleggio_ok(href):
    from urllib.parse import parse_qs, urlparse
    u = urlparse(href)
    return (u.scheme == "https" and u.hostname in ("www.discovercars.com", "discovercars.com") and u.path in ("", "/")
            and parse_qs(u.query) == {"a_aid": [NOLEGGIO_AID]})


def controlla_noleggio(t, nome, dopo):
    """Errori sul riquadro "Hire a car" di una pagina della sezione (o della home). dopo = testi che devono stare PRIMA del riquadro
    (risposta, regole ufficiali). Con NOLEGGIO_AUTO vuoto: nessun link di affiliazione."""
    errori = []
    voci = G.MON.link_affiliati(t)
    if not G.NOLEGGIO_AUTO:
        return [f"{nome}: link di affiliazione con il riquadro noleggio spento ({h})" for h, _, _ in voci]
    if len(voci) != 1:
        return [f"{nome}: attesi 1 link DiscoverCars, trovati {len(voci)} link di affiliazione"]
    href, _, rel = voci[0]
    if not link_noleggio_ok(href) or href != G.NOLEGGIO_AUTO:
        errori.append(f"{nome}: link di noleggio diverso da DiscoverCars con a_aid={NOLEGGIO_AID}: {href}")
    if not {"sponsored", "noopener"} <= rel:
        errori.append(f"{nome}: link DiscoverCars senza rel=\"sponsored noopener\"")
    tag = re.search(r'<a\b[^>]*href="' + re.escape(escape(href)) + r'"[^>]*>', t)
    if not tag or 'target="_blank"' not in tag.group(0):
        errori.append(f"{nome}: link DiscoverCars senza target=\"_blank\"")
    i = t.find("data-noleggio")
    if i < 0:
        return errori + [f"{nome}: link DiscoverCars fuori dal riquadro 'Hire a car' (data-noleggio)"]
    blocco = t[i:t.find("</section>", i) if "<section" in t[t.rfind("<", 0, i):i] else t.find("</p>", i)]
    if G.MON.RIGA_EN not in blocco:
        errori.append(f"{nome}: riga di trasparenza non nel riquadro noleggio")
    for x in dopo:
        j = t.find(x)
        if j < 0 or j > i:
            errori.append(f"{nome}: riquadro noleggio non dopo «{x[:50]}»")
    return errori
# controlli indipendenti dal classificatore: cosa devono contenere le frasi che decidono ogni esito
IND_PAT = {
    "si": re.compile(r"international driv\w* (?:permit|licen)|\bIDPs?\b|international driver", re.I),
    "no": re.compile(r"\b(?:can|may) (?:use|drive)|\bdo not need an IDP|isn't required|not mandatory|\beither\b|is valid|are valid|will be accepted|are accepted|you need either", re.I),
    "dipende": re.compile(r"\bup to\b|\bfor (?:the first )?(?:\d|one|two|three|four|six|twelve)|\blonger|\bmore than|\bless than|\bif\b|\bmay\b|\bsome\b|\bhire|\brent|"
                          r"translat|notari|\bvar(?:y|ies)\b|\bin some cases|\bdays?\b|\bmonths?\b|\byears?\b|\bduration|\bexcept|\bwhile\b|\bprovinces?\b|travel between", re.I),
    "consigliato": re.compile(r"\bshould\b|recommend|helpful|useful", re.I),
    "locale": re.compile(r"\blocal\b|temporary|visitor|not (?:recogni[sz]ed|valid|permitted|allowed)|aren't (?:valid|recognised)|\bconvert\b|Chinese|Cambodian|Myanmar|"
                         r"St Kitts and Nevis driving licence|recognition|does not recogni[sz]e", re.I),
}


def _impronta_pat(v):
    parti = [b["x"] for b in v["testo"]]
    if v.get("tabella"):
        parti = [f"TABELLA: {v['tabella']['nome']} | {v['tabella']['tipo']} | {v['tabella']['nota']}"] + parti
    import hashlib
    return hashlib.sha256("\n".join(parti).encode("utf-8")).hexdigest()[:16]


def controlla_patenti():
    from html import unescape
    errori = []
    conti = {"paesi": 0, "voci": 0, "manuali": 0, "pagine": 0, "faq": 0, "citazioni": 0, "cache": "assente", "righe": 0, "noleggio": 0, "avvisi_idp": 0}
    f = SITO.parent / "dati" / "patenti.json"
    if not f.exists():
        return ["dati/patenti.json mancante (lanciare raccolta/patenti.py)"], conti
    D = json.loads(f.read_text(encoding="utf-8"))
    M = json.loads((SITO.parent / "dati" / "patenti_manuali.json").read_text(encoding="utf-8"))
    dom = json.loads((SITO.parent / "dati" / "patenti_domanda.json").read_text(encoding="utf-8"))
    iso = {p["iso2"] for p in json.loads((SITO.parent / "dati" / "paesi_iso.json").read_text(encoding="utf-8"))["paesi"]}
    sm = leggi("sitemap.xml")
    per = {p["iso2"]: p for p in D["paesi"]}
    # a) ricalcolo dai grezzi salvati (fuori dal repository): stessi esiti, frasi e impronte del file
    if (RPAT.CACHE / "govuk-driving-abroad.json").exists() and (RPAT.CACHE / "uk").exists() and any(RPAT.CACHE_CA.glob("cta-cap-*.json")):
        conti["cache"] = "presente"
        ef = []
        if not RPAT.CACHE_AU.exists() or not any(RPAT.CACHE_AU.iterdir()):
            avviso(18, "copie Smartraveller (raccolta/.cache/au/) assenti: ricalcolo della patente australiana saltato "
                       "(python3 -I beforeyoufly/raccolta/passaporti_au.py, poi patenti.py)")
        RPAT.OFFLINE = True
        try:
            g = RPAT.scarica_tutto()
            uk, _, _ = RPAT.leggi_uk(g)
            ca, _ = RPAT.leggi_ca(g)
            au, _ = RPAT.leggi_au(g)
            avv = []
            for pat, src in (("uk", uk), ("ca", ca), ("au", au)):
                for c, v in src.items():
                    w = RPAT.voce(pat, c, v, M, avv)
                    d = (per.get(c) or {}).get(pat)
                    if not d:
                        ef.append(f"patenti {pat} {c}: nei grezzi ma non in dati/patenti.json")
                        continue
                    for k in ("esito", "frasi", "convenzione", "impronta", "testo"):
                        if w[k] != d[k]:
                            ef.append(f"patenti {pat} {c}: '{k}' diverso dal ricalcolo sui grezzi salvati")
                            break
            if avv:
                ef += [f"patenti: {a}" for a in avv if a.startswith("FATTO MANUALE")]
        finally:
            RPAT.OFFLINE = os.environ.get("BYF_OFFLINE") == "1"
        errori += esito_copia(18, "patenti", ef, RPAT.CACHE / "govuk-driving-abroad.json", D.get("controllato_il"))
    else:
        avviso(18, "copie salvate GOV.UK / FCDO / travel.gc.ca assenti (raccolta/.cache/patenti/ e .cache/ca/, fuori dal repository): ricalcolo "
                   "degli esiti dalle copie saltato; dati dell'ultima lettura buona (python3 -I beforeyoufly/raccolta/patenti.py)")
    # b) dati: esiti ammessi, frasi parola per parola, impronte, fonti ufficiali, date, controlli indipendenti
    for p in D["paesi"]:
        conti["paesi"] += 1
        if p["iso2"] not in iso:
            errori.append(f"patenti {p['iso2']}: codice non ISO")
        for pat in ("uk", "ca", "au"):
            v = p[pat]
            if not v:
                continue
            conti["voci"] += 1
            c = p["iso2"]
            if v["esito"] not in ("si", "no", "dipende", "consigliato", "locale", "non_detto"):
                errori.append(f"patenti {pat} {c}: esito '{v['esito']}' non ammesso (nessuna pagina può restare 'da leggere')")
            if _impronta_pat(v) != v["impronta"]:
                errori.append(f"patenti {pat} {c}: impronta diversa dal testo salvato")
            # testo ufficiale: blocchi uno per uno e, per gli elenchi, la frase che li introduce unita alle voci ("…: voce; voce"), come le cita la pagina
            testo = RPAT.piano("\n".join(([f"TABELLA: {v['tabella']['nome']} | {v['tabella']['tipo']} | {v['tabella']['nota']}"] if v.get("tabella") else [])
                                         + [b["x"] for b in v["testo"]] + [t for t, _ in RPAT.affermazioni(v["testo"])]))
            for x in v["frasi"]:
                if RPAT.piano(x) not in testo:
                    errori.append(f"patenti {pat} {c}: frase citata non nel testo ufficiale: {x[:70]}")
            if v["esito"] in IND_PAT and not IND_PAT[v["esito"]].search(" ".join(v["frasi"])):
                errori.append(f"patenti {pat} {c}: esito '{v['esito']}' non sostenuto dalle frasi citate (controllo indipendente)")
            if v["esito"] == "non_detto" and re.search(r"\b(?:must (?:have|carry|get|hold)|(?:is|are) required|you(?:'ll| will) need|(?<!if )you need (?:an?|the|both))\b[^.]{0,60}(?:IDP|international driv)",
                                                         " ".join(v["frasi"]), re.I):
                errori.append(f"patenti {pat} {c}: 'Not stated' ma la frase citata parla di un permesso richiesto")
            if v["esito"] in ("si", "no", "dipende", "consigliato", "locale") and not v["frasi"]:
                errori.append(f"patenti {pat} {c}: esito senza frase ufficiale")
            if v.get("url") and not FONTI_UFFICIALI_PAT.match(v["url"]):
                errori.append(f"patenti {pat} {c}: fonte non ufficiale {v['url']}")
            if not v.get("letto_il") and not (pat == "uk" and v.get("tabella")):
                errori.append(f"patenti {pat} {c}: manca la data di lettura")
            conv = v.get("convenzione")
            if conv and pat == "uk" and v.get("tabella") and conv != v["tabella"]["tipo"]:
                errori.append(f"patenti uk {c}: convenzione diversa dalla tabella GOV.UK")
            if conv and not (pat == "uk" and v.get("tabella")) and conv not in " ".join(v["frasi"]) + " ".join(b["x"] for b in v["testo"]):
                errori.append(f"patenti {pat} {c}: convenzione {conv} non scritta dalla fonte")
            if v["regola"] == "manuale":
                conti["manuali"] += 1
    for pat, mm in M.items():
        if pat.startswith("_") or not isinstance(mm, dict):
            continue
        for c, m in mm.items():
            v = (per.get(c) or {}).get(pat)
            if not v or v["impronta"] != m["impronta"] or v["esito"] != m["esito"] or v["frasi"] != m["frasi"]:
                errori.append(f"patenti {pat} {c}: fatto manuale non applicato o scaduto (impronta del testo cambiata?)")
    for k, x in D["fonti"].items():
        for chiave in ("pagina_idp", "api", "fcdo_api", "dati", "pagina_aaa"):
            if x.get(chiave) and not FONTI_UFFICIALI_PAT.match(x[chiave]):
                errori.append(f"patenti: fonte generale {k}.{chiave} non ufficiale")
    # c) pagine: esattamente le coppie con ricerche che nominano la patente e una risposta della fonte
    for pat in G.PATENTI:
        T = G.PATENTI[pat]
        attese = {c for c in dom["pagine"].get(pat, []) if c in iso and (per.get(c) or {}).get(pat) and per[c][pat]["esito"] != "non_detto"}
        cartella = SITO / G.PAT_BASE / T["slug"]
        trovate = {q.parent.name for q in cartella.glob("*/index.html")}
        if trovate != {G.slug_srv(c) for c in attese}:
            errori.append(f"patenti {pat}: pagine Paese diverse dalle coppie con domanda: {sorted(trovate ^ {G.slug_srv(c) for c in attese})[:6]}")
        for q in dom["pagine"].get(pat, []):
            if not any(RPAT.RX_PAT[pat].search(x.split(" [gl=")[0]) for x in dom["patenti"][pat].get(q, [])):
                errori.append(f"patenti {pat} {q}: pagina senza una ricerca che nomini la patente")
        t_pat = leggi(f"{G.url_pat(pat)}index.html")
        if f"<loc>{G.URL_SITO}/{G.url_pat(pat)}</loc>" not in sm:
            errori.append(f"{G.url_pat(pat)}: non in sitemap")
        m = re.search(r'<p class="lead" id="answer">(.*?)</p>', t_pat)
        if not m or unescape(m.group(1)) != G.prima_frase_patente(pat):
            errori.append(f"{G.url_pat(pat)}: prima frase diversa dai conteggi")
        righe = dict(re.findall(r'<tr data-voce id="([a-z]{2})"><td[^>]*>.*?</td><td[^>]*><span class="badge[^"]*">([^<]*)</span>', t_pat))
        for c, p in per.items():
            if p[pat] and c in iso:
                conti["righe"] += 1
                if unescape(righe.get(c.lower(), "")) != G.ESITI_PAT[p[pat]["esito"]][0]:
                    errori.append(f"{G.url_pat(pat)}: riga {c} '{righe.get(c.lower())}' invece di '{G.ESITI_PAT[p[pat]['esito']][0]}'")
        for c in attese:
            rel = G.url_pat(pat, c)
            if not (SITO / rel / "index.html").exists():
                continue
            conti["pagine"] += 1
            t = leggi(rel + "index.html")
            v = per[c][pat]
            m = re.search(r'<p class="lead" id="answer">(.*?)</p>', t)
            r = unescape(m.group(1)) if m else ""
            atteso_inizio = G.ESITI_PAT[v["esito"]][2]
            d = G.data_lunga(G.data_pat(pat, v))
            if r != G.risposta_pat(pat, c) or not r.startswith(atteso_inizio) or f"checked on {d})." not in r:
                errori.append(f"{rel}: prima frase senza la risposta attesa, la frase dell'ente, la fonte o la data: {r[:90]}")
            if v["esito"] == "dipende" and not r.startswith("It depends on "):
                errori.append(f"{rel}: 'It depends' senza dire da cosa (durata, noleggio, traduzione, regione)")
            if G.conv_fcdo_diversa(pat, v) and not all(x in t for x in G.conv_fcdo_diversa(pat, v)):
                errori.append(f"{rel}: tabella GOV.UK e FCDO nominano convenzioni diverse, la pagina ne mostra una sola")
            for x in v["frasi"]:
                conti["citazioni"] += 1
                if escape(x.rstrip(":").strip()) not in t:
                    errori.append(f"{rel}: frase ufficiale non nella pagina: {x[:60]}")
            if v.get("url") and escape(v["url"]) not in t:
                errori.append(f"{rel}: manca il link alla fonte ufficiale")
            if "not legal advice" not in t:
                errori.append(f"{rel}: manca 'not legal advice'")
            if AFFILIATI_PAT.search(t):
                errori.append(f"{rel}: link affiliato o di noleggio ({AFFILIATI_PAT.search(t).group(0)})")
            errori += controlla_noleggio(t, rel, ['id="answer"', "<h2>What the official source says</h2>", "<h2>What to bring and where to get an IDP</h2>"])
            avv = re.findall(r'<p class="avviso avviso-idp" data-avviso-idp>(.*?)</p>', t)
            if G.NOLEGGIO_AUTO and v["esito"] in ("si", "locale"):
                conti["avvisi_idp"] += 1
                if len(avv) != 1 or escape(G.FRASE_NOLEGGIO) not in avv[0] or t.find("data-avviso-idp") > t.find("data-noleggio"):
                    errori.append(f"{rel}: esito '{v['esito']}' senza l'avviso evidente sul permesso prima del riquadro noleggio")
            elif avv:
                errori.append(f"{rel}: avviso sul permesso con esito '{v['esito']}'")
            for x in G.ingresso_srv(c, "../../../"):
                if x not in t:
                    errori.append(f"{rel}: manca il link alla pagina passaporto/visto dello stesso Paese")
            if f"<loc>{G.URL_SITO}/{rel}</loc><lastmod>{G.data_pat(pat, v)}</lastmod>" not in sm:
                errori.append(f"{rel}: non in sitemap o lastmod diverso dalla lettura")
            ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t)]
            faq = [x for x in ld if x.get("@type") == "FAQPage"]
            vis = [(unescape(q), unescape(a)) for q, a in re.findall(r"<h3>(.*?)</h3><p>(.*?)</p>", t[t.find('<section class="faq">'):])]
            if len(faq) != 1 or [(x["name"], x["acceptedAnswer"]["text"]) for x in faq[0]["mainEntity"]] != vis or not vis or vis[0][1] != r:
                errori.append(f"{rel}: FAQ JSON-LD diversa dal testo visibile o dalla prima frase")
            conti["faq"] += len(vis)
            tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
            if len(tit) > G.LIMITE_TITOLO_PAT or "IDP" not in tit or str(G.ANNO) not in tit:
                errori.append(f"{rel}: titolo oltre {G.LIMITE_TITOLO_PAT} caratteri, senza 'IDP' o senza l'anno: {tit}")
            k_dove = {"uk": "uk_paypoint", "ca": "ca_caa", "au": "au_aaa"}[pat]
            if escape(D["frasi_generali"][k_dove]) not in t:
                errori.append(f"{rel}: manca la frase ufficiale su dove si ottiene il permesso")
    # d) tutta la sezione: niente assistenti AI, nessun affiliato tranne DiscoverCars (riquadro "Hire a car"), collegamenti in entrata
    if G.NOLEGGIO_AUTO and not link_noleggio_ok(G.NOLEGGIO_AUTO):
        errori.append(f"NOLEGGIO_AUTO (dati/affiliati.json, _discovercars_noleggio) non è il link generale DiscoverCars con a_aid={NOLEGGIO_AID}: {G.NOLEGGIO_AUTO}")
    for q in (SITO / G.PAT_BASE).rglob("*.html"):
        t = q.read_text(encoding="utf-8")
        nome = q.relative_to(SITO).as_posix()
        m = VIETATE_SRV.search(unescape(re.sub(r"<[^>]+>", " ", t))) or AFFILIATI_PAT.search(t)
        if m:
            errori.append(f"{nome}: parola o link vietati '{m.group(0)}'")
        prof = len(q.relative_to(SITO / G.PAT_BASE).parts)
        if prof == 1:  # indice: dopo la tabella di tutti i Paesi
            errori += controlla_noleggio(t, nome, ['id="answer"', "<h2>Every country, every licence</h2>", "</table>"])
        elif prof == 2:  # pagina per patente: dopo la tabella e "dove si ottiene il permesso"
            errori += controlla_noleggio(t, nome, ['id="answer"', "</table>", "<h2>Where to get an international driving permit</h2>"])
        elif prof != 3:
            errori.append(f"{nome}: pagina inattesa nella sezione")
        if G.NOLEGGIO_AUTO and G.MON.link_affiliati(t):
            conti["noleggio"] += 1
    # DiscoverCars solo nella sezione e nella home (riga della sezione Driving abroad)
    for q in SITO.rglob("*.html"):
        nome = q.relative_to(SITO).as_posix()
        if nome.startswith((G.PAT_BASE + "/", G.PED_BASE + "/", G.GOM_BASE + "/", G.FL_BASE + "/")) or nome == "index.html":
            continue
        if nome in LIQ_VACANZA_PAGINE():  # dal 5/11/2026 pagine liquidi degli aeroporti di vacanza: le controlla il punto 30
            continue
        if "discovercars" in q.read_text(encoding="utf-8").lower():
            errori.append(f"{nome}: link DiscoverCars fuori dalle sezioni Driving abroad, Tolls e Winter tyres with a rental car, dalle pagine "
                          f"liquidi degli aeroporti di vacanza e dalla home")
    for nome in ("patenti.json", "patenti_manuali.json", "patenti_domanda.json"):
        if VIETATE_SRV.search((SITO.parent / "dati" / nome).read_text(encoding="utf-8")):
            errori.append(f"dati/{nome}: nome di un assistente di intelligenza artificiale")
    home = leggi("index.html")
    if f'href="{G.PAT_BASE}/"' not in home:
        errori.append("home senza link alla sezione 'Driving abroad'")
    errori += controlla_noleggio(home, "index.html (home)", ["<h2>Driving abroad: do you need an international driving permit?</h2>", f'href="{G.PAT_BASE}/"'])
    ab = leggi("about/index.html")
    if 'id="driving-abroad"' not in ab:
        errori.append("About senza la sezione 'Driving abroad'")
    if f"<loc>{G.URL_SITO}/{G.PAT_BASE}/</loc>" not in sm:
        errori.append("indice driving-abroad non in sitemap")
    prove = [("passport-validity/japan/index.html", "../../driving-abroad/uk-licence/japan/"), ("canadian-passport/italy/index.html", "../../driving-abroad/canadian-licence/italy/"),
             ("australian-passport/japan/index.html", "../../driving-abroad/australian-licence/japan/"), ("available-in/starlink/canada/index.html", "../../../driving-abroad/uk-licence/canada/")]
    for pag, link in prove:
        if (SITO / pag).exists() and f'href="{link}"' not in leggi(pag):
            errori.append(f"{pag}: manca il link alla pagina 'Driving in'")
    return errori, conti


# ---------------------------------------------------------------- 20. Pedaggi con l'auto a noleggio (30/10/2026)
_spec_ped = importlib.util.spec_from_file_location("raccolta_pedaggi", Path(__file__).resolve().parent / "raccolta" / "pedaggi.py")
RPED = importlib.util.module_from_spec(_spec_ped)
_spec_ped.loader.exec_module(RPED)
# Fonti ammesse: gestori delle autostrade o dei sistemi di pedaggio e governi (nessun rivenditore, nessuna compagnia di noleggio)
FONTI_UFFICIALI_PED = re.compile(r"^https://(?:www\.pttolls\.com|www\.eflow\.ie|www\.tii\.ie|www\.autopass\.no|www\.autostrade\.it|www\.aliae\.com|"
                                 r"peagereinvente\.aprr\.fr|www\.autopistas\.com|www\.hac\.hr|www\.aodos\.gr|help\.asfinag\.at|shop\.asfinag\.at|"
                                 r"www\.bazg\.admin\.ch|www\.gov\.si|edalnice\.gov\.cz|nemzetiutdij\.hu|crolibertas\.hr|narodne-novine\.nn\.hr)/")
# Croazia (31/10/2026): caselli fino al 28/2/2027, pedaggio senza caselli dal 1/3/2027 per legge (Zakon o naplati cestarine, NN 156/2025, art. 67).
# Frase della legge che fissa la data, scritta qui a mano: deve essere citata nella pagina e trovarsi nel testo salvato della Gazzetta ufficiale.
HR_DATA_LEGGE = "koji stupaju na snagu 1. ožujka 2027."
# Frase di HAC (sito Crolibertas, notizia del 24/12/2025) con la stessa data: citata nella pagina e presente nella copia salvata (revisione del 31/10/2026).
HR_DATA_HAC = "the new system will be fully applied starting 1 March 2027."
HR_FONTI_2027 = ("hr_zakon", "hr_crolibertas", "hr_crolibertas_test", "hr_crolibertas_zakon")
NOMI_NOLEGGIO_PED = re.compile(r"\b(?:hertz|avis|budget|enterprise|alamo|europcar|sixt|thrifty|dollar rent|goldcar|rentalcars|autoslash|tollguru|"
                               r"platepass|e-toll|tollpass)\b", re.I)


def _numeri_ped(s):
    """Numeri di un testo, senza separatori delle migliaia ('5,550', '5 550' -> '5550'; '15,00' -> '15.00')."""
    s = re.sub(r"\b\d{1,2} (?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4}\b", " ", s)  # date
    s = re.sub(r"(?<=\d)[ ,](?=\d{3}\b)", "", s)
    s = re.sub(r"(?<=\d),(?=\d{2}\b)", ".", s)
    out = set()
    for n in re.findall(r"\d+(?:\.\d+)?", s):
        out.add(n)
        if n.endswith(".00"):
            out.add(n[:-3])
    return out


def controlla_pedaggi():
    """Punto 20: dati = fonti = pagine; titoli; sitemap; FAQ da ricerche vere; solo DiscoverCars con il nostro a_aid; link con Driving abroad."""
    from html import unescape
    errori = []
    conti = {"paesi": 0, "fonti": 0, "citazioni": 0, "prezzi": 0, "faq": 0, "cache": "no", "noleggio": 0, "link_guida": 0, "croazia_2027": 0}
    if not G.PED:
        return ["dati/pedaggi.json mancante (rilanciare raccolta/pedaggi.py)"], conti
    M = json.loads((SITO.parent / "dati" / "pedaggi_manuali.json").read_text(encoding="utf-8"))
    if M["paesi"] != G.PED["paesi"]:
        errori.append("dati/pedaggi.json non è aggiornato rispetto a dati/pedaggi_manuali.json (rilanciare raccolta/pedaggi.py)")
    D = json.loads((SITO.parent / "dati" / "pedaggi_domanda.json").read_text(encoding="utf-8"))
    ricerche = {s for g in D["paesi"].values() for qq in g.values() for ss in qq.values() for s in ss}
    # a) fonti: HTTP 200, solo domini ufficiali, data di lettura; se c'è la cache le frasi e l'impronta si ricalcolano dal testo salvato
    cache = RPED.CACHE.exists()
    for fid, F in G.PED["fonti"].items():
        conti["fonti"] += 1
        if F["http"] != 200:
            errori.append(f"fonte {fid}: HTTP {F['http']}")
        if not FONTI_UFFICIALI_PED.match(F["url"]) or not FONTI_UFFICIALI_PED.match(F["pagina"]):
            errori.append(f"fonte {fid}: dominio non ufficiale o non previsto: {F['url']}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", F["letto_il"] or "") or F["letto_il"] > G.OGGI.isoformat():
            errori.append(f"fonte {fid}: data di lettura non valida {F['letto_il']}")
        f_c = RPED.CACHE / f"{fid}.{'json' if RPED.FONTI[fid].get('tipo') == 'api_hu' else 'html'}"
        if copia_usabile(20, fid, f_c, "pedaggi.py"):
            ef = []
            t = RPED.testo_fonte(f_c.read_text(encoding="utf-8"), RPED.FONTI[fid].get("tipo", "html"))
            frasi = RPED.frasi_fonte(G.PED, fid)
            for x in frasi:
                if x not in t:
                    ef.append(f"fonte {fid}: la frase non è nel testo salvato: {x[:70]}")
            if RPED.impronta_zona(t, frasi) != F["impronta"]:
                ef.append(f"fonte {fid}: impronta diversa dal testo salvato (rilanciare raccolta/pedaggi.py)")
            errori += esito_copia(20, fid, ef, f_c, F["letto_il"])
            conti["cache"] = "sì"
    sm = leggi("sitemap.xml")
    # b) una pagina per Paese, coerente con i dati
    attese = {G.url_ped(p["iso2"]) + "index.html" for p in G.PED_PAESI} | {f"{G.PED_BASE}/index.html"}
    trovate = {q.relative_to(SITO).as_posix() for q in (SITO / G.PED_BASE).rglob("index.html")} if (SITO / G.PED_BASE).exists() else set()
    if attese != trovate:
        errori.append(f"pagine della sezione diverse dai dati: in più {sorted(trovate - attese)}, mancanti {sorted(attese - trovate)}")
    for p in G.PED_PAESI:
        c, rel = p["iso2"], G.url_ped(p["iso2"]) + "index.html"
        conti["paesi"] += 1
        if not (SITO / rel).exists():
            continue
        t = leggi(rel)
        vis = unescape(re.sub(r"<[^>]+>", " ", t))
        if f"<loc>{G.URL_SITO}/{G.url_ped(c)}</loc><lastmod>{G.data_ped(p)}</lastmod>" not in sm:
            errori.append(f"{rel}: non in sitemap o lastmod diverso dalla data di lettura {G.data_ped(p)}")
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if tit != p["titolo"] or len(tit) > G.LIMITE_TITOLO_PED or str(G.ANNO) not in tit or p["nome"].split()[0][:5].lower() not in tit.lower().replace("swiss", "switz"):
            errori.append(f"{rel}: titolo oltre {G.LIMITE_TITOLO_PED} caratteri, senza anno o senza il Paese: {tit}")
        # prima frase: chi, data, risposta
        m = re.search(r'<p class="lead" id="answer">(.*?)</p>', t)
        attesa = f"According to {p['chi']}, checked on {G.data_lunga(G.data_ped(p))}, {p['risposta']}"
        if not m or unescape(m.group(1)) != attesa:
            errori.append(f"{rel}: prima frase diversa da 'According to <fonte>, checked on <data>, <risposta>'")
        # citazioni e prezzi: nella pagina, con il link e la data della fonte
        for x in p["citazioni"]:
            conti["citazioni"] += 1
            if escape(x["x"], quote=False) not in t and escape(x["x"]) not in t:
                errori.append(f"{rel}: citazione mancante: {x['x'][:60]}")
            if x["f"] not in G.PED["fonti"]:
                errori.append(f"{rel}: citazione con fonte sconosciuta {x['f']}")
        for f in G.fonti_ped(p):
            F = G.PED["fonti"][f]
            if f'href="{escape(F["pagina"])}"' not in t or f"checked on {G.data_lunga(F['letto_il'])}" not in vis:
                errori.append(f"{rel}: manca il link o la data della fonte {f}")
        for pr in p.get("prezzi", []):
            conti["prezzi"] += 1
            if not _numeri_ped(pr["importo"]) <= _numeri_ped(pr["prova"]):
                errori.append(f"{rel}: prezzo «{pr['importo']}» con numeri che non sono nella prova «{pr['prova']}»")
            if escape(pr["importo"]) not in t:
                errori.append(f"{rel}: prezzo mancante nella tabella: {pr['importo']}")
        # nessun numero inventato nelle frasi nostre: ogni numero è in una citazione o in una prova
        ammessi = set().union(*[_numeri_ped(x["x"]) for x in p["citazioni"]], *[_numeri_ped(pr["prova"]) for pr in p.get("prezzi", [])], {str(G.ANNO)})
        ammessi |= {"1", "10", "30", "2", "5"} & set().union(*[_numeri_ped(x["x"]) for x in p["citazioni"]], *[_numeri_ped(pr["prova"] + " " + pr["voce"]) for pr in p.get("prezzi", [])])
        for campo in ("risposta", "come", "prezzo_breve", "noleggio_breve", "nota", "cambio"):
            testo_campo = " ".join(p["cambio"]["frasi"] + [p["cambio"]["titolo"]]) if campo == "cambio" and p.get("cambio") else (p.get(campo) or "") if campo != "cambio" else ""
            extra = _numeri_ped(testo_campo) - ammessi
            if extra:
                errori.append(f"{rel}: numeri non presi dalle fonti in '{campo}': {sorted(extra)}")
        for q in p["faq"]:
            extra = _numeri_ped(q["pre"] + " " + q["post"]) - ammessi
            if extra:
                errori.append(f"{rel}: numeri non presi dalle fonti nella FAQ «{q['q']}»: {sorted(extra)}")
        # citazioni non in inglese: ognuna con la sua traduzione nella pagina (francese, spagnolo, croato...)
        for x in p["citazioni"]:
            if G.PED["fonti"][x["f"]]["lingua"] != "en":
                tr = p.get("traduzioni", {}).get(x["id"])
                if not tr or escape(tr, quote=False) not in t and escape(tr) not in t:
                    errori.append(f"{rel}: citazione in {G.PED['fonti'][x['f']]['lingua']} senza traduzione nella pagina: {x['id']}")
        # cambio con data (riquadro "From ... (by law)"): presente, e non ancora scaduto (dopo la data la pagina va riscritta al presente)
        if p.get("cambio"):
            C = p["cambio"]
            if f'data-cambio="{C["dal"]}"' not in t:
                errori.append(f"{rel}: manca il riquadro del cambio del {C['dal']}")
            if G.OGGI.isoformat() >= C["dal"]:
                errori.append(f"{rel}: il cambio del {C['dal']} è già in vigore: riscrivere la pagina al presente (risposta, come, titolo, riquadro)")
            if any(x["f"] not in G.PED["fonti"] for x in p["citazioni"] if x["tema"] == "dal_2027") or not any(x["tema"] == "dal_2027" for x in p["citazioni"]):
                errori.append(f"{rel}: cambio senza citazioni ufficiali del tema 'dal_2027'")
        if c == "HR":
            conti["croazia_2027"] = 0
            for frase in ("28 February 2027", "1 March 2027"):
                if frase not in p["risposta"] or frase not in p["come"] or frase not in vis:
                    errori.append(f"{rel}: la Croazia deve dire '{frase}' nella risposta, in 'How you pay' e nella pagina")
            if "2027" not in tit:
                errori.append(f"{rel}: titolo della Croazia senza il 2027: {tit}")
            for fid in HR_FONTI_2027:
                F = G.PED["fonti"].get(fid)
                if not F or F["http"] != 200 or f'href="{escape(F["pagina"])}"' not in t:
                    errori.append(f"{rel}: fonte {fid} (HAC/Crolibertas o legge) mancante, non letta con HTTP 200 o non linkata")
                else:
                    conti["croazia_2027"] += 1
            legge = [x for x in p["citazioni"] if x["f"] == "hr_zakon" and HR_DATA_LEGGE in x["x"]]
            if not legge or escape(legge[0]["x"], quote=False) not in t:
                errori.append(f"{rel}: manca la frase della legge con la data ({HR_DATA_LEGGE!r})")
            f_z = RPED.CACHE / "hr_zakon.html"
            if f_z.exists() and not pagina_di_blocco(f_z.read_bytes()) and HR_DATA_LEGGE not in RPED.testo_fonte(f_z.read_text(encoding="utf-8")):
                errori += esito_copia(20, "hr_zakon", [f"{rel}: la data della legge non è più nel testo salvato della Gazzetta ufficiale"],
                                      f_z, G.PED["fonti"].get("hr_zakon", {}).get("letto_il"))
            hac = [x for x in p["citazioni"] if x["f"] == "hr_crolibertas_zakon" and HR_DATA_HAC in x["x"]]
            if not hac or escape(hac[0]["x"], quote=False) not in t:
                errori.append(f"{rel}: manca la frase di HAC (Crolibertas) con la data ({HR_DATA_HAC!r})")
            f_h = RPED.CACHE / "hr_crolibertas_zakon.html"
            if f_h.exists() and not pagina_di_blocco(f_h.read_bytes()) and HR_DATA_HAC not in RPED.testo_fonte(f_h.read_text(encoding="utf-8")):
                errori += esito_copia(20, "hr_crolibertas_zakon", [f"{rel}: la data di HAC non è più nel testo salvato del sito Crolibertas"],
                                      f_h, G.PED["fonti"].get("hr_crolibertas_zakon", {}).get("letto_il"))
            if "does not give a start date" in vis:
                errori.append(f"{rel}: la pagina dice che HAC non scrive la data, ma la notizia Crolibertas del 24/12/2025 la scrive")
            if p["noleggio"] == "detto" or "ask the rental company" not in vis.lower():
                errori.append(f"{rel}: le fonti non parlano delle auto a noleggio: la pagina deve dirlo e consigliare di chiedere al noleggiatore")
            if "Toll plazas: ticket at the entry, pay at the exit" in t:
                errori.append(f"{rel}: frase vecchia sui caselli senza la data del 28/2/2027")
        # noleggio: "detto" solo con una frase ufficiale che parla di auto a noleggio; altrimenti la frase fissa
        nol = [x for x in p["citazioni"] if x["tema"] == "noleggio"]
        if p["noleggio"] == "detto" and not any(re.search(r"rent|rental|hire", x["x"], re.I) for x in nol):
            errori.append(f"{rel}: 'Rental cars' detto senza una frase ufficiale sulle auto a noleggio")
        if p["noleggio"] != "detto" and "data-nol-non-detto" not in t:
            errori.append(f"{rel}: manca la frase 'The official pages we read do not mention rental cars'")
        # FAQ: domande da ricerche vere, JSON-LD = testo visibile, citazioni intere
        faq_ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t)]
        faq_ld = next((x for x in faq_ld if x.get("@type") == "FAQPage"), None)
        attese_faq = G.faq_ped(p)
        if not faq_ld or [(e["name"], e["acceptedAnswer"]["text"]) for e in faq_ld["mainEntity"]] != attese_faq:
            errori.append(f"{rel}: FAQ JSON-LD diversa dalle domande previste")
        for qd, a in attese_faq:
            conti["faq"] += 1
            if f"<h3>{escape(qd)}</h3><p>{escape(a)}</p>" not in t:
                errori.append(f"{rel}: FAQ visibile diversa dal JSON-LD: {qd}")
        for q in p["faq"]:
            if q["query"] not in ricerche:
                errori.append(f"{rel}: FAQ «{q['q']}» senza una ricerca vera ({q['query']!r} non è in dati/pedaggi_domanda.json)")
        # riquadro DiscoverCars: solo il nostro link generale, dopo la risposta e le regole ufficiali; niente altri noleggi
        errori += controlla_noleggio(t, rel, ['id="answer"', 'id="official"', 'id="rental"'])
        if G.NOLEGGIO_AUTO and G.MON.link_affiliati(t):
            conti["noleggio"] += 1
        vis_en = unescape(re.sub(r"<[^>]+>", " ", re.sub(r'(?s)<blockquote class="cit" lang="(?!en)[a-z]+">.*?</blockquote>', " ", t)))  # citazioni in francese/spagnolo escluse ("avis de paiement")
        mm = NOMI_NOLEGGIO_PED.search(vis_en) or AFFILIATI_PAT.search(t) or VIETATE_SRV.search(vis)
        if mm:
            errori.append(f"{rel}: nome vietato (noleggio, rete o assistente) '{mm.group(0)}'")
        if "not legal advice" not in vis:
            errori.append(f"{rel}: manca 'not legal advice'")
        # link con le pagine Driving abroad dello stesso Paese (andata e ritorno)
        for k in G.PATENTI:
            if c in G.PAGINE_PAT[k]:
                conti["link_guida"] += 1
                if f'href="../../{G.url_pat(k, c)}"' not in t:
                    errori.append(f"{rel}: manca il link a {G.url_pat(k, c)}")
                if f'href="../../../{G.url_ped(c)}"' not in leggi(G.url_pat(k, c) + "index.html"):
                    errori.append(f"{G.url_pat(k, c)}: manca il link alla pagina dei pedaggi {G.url_ped(c)}")
        if f'href="{G.url_ped(c)}"' not in leggi("index.html"):
            errori.append(f"home senza link a {G.url_ped(c)}")
    # c) indice: in sitemap, tabella uguale ai dati, riquadro dopo la tabella, titolo
    idx = f"{G.PED_BASE}/index.html"
    if (SITO / idx).exists():
        t = leggi(idx)
        if f"<loc>{G.URL_SITO}/{G.PED_BASE}/</loc><lastmod>{G.PED['controllato_il']}</lastmod>" not in sm:
            errori.append("indice tolls-rental-car non in sitemap o lastmod diverso")
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(tit) > G.LIMITE_TITOLO_PED or str(G.ANNO) not in tit:
            errori.append(f"{idx}: titolo oltre {G.LIMITE_TITOLO_PED} caratteri o senza l'anno: {tit}")
        righe = re.findall(r'<tr data-voce id="([a-z]{2})">(.*?)</tr>', t)
        if [r[0].upper() for r in righe] != [p["iso2"] for p in G.PED_PAESI]:
            errori.append(f"{idx}: righe della tabella diverse dai Paesi dei dati")
        for (cod, r), p in zip(righe, G.PED_PAESI):
            celle = [unescape(re.sub(r"<[^>]+>", "", x)) for x in re.findall(r"<td[^>]*>(.*?)</td>", r)]
            if celle != [p["nome"], p["come"], "Yes" if p["vignetta"] else "No", p["prezzo_breve"], p["noleggio_breve"], G.data_lunga(G.data_ped(p))]:
                errori.append(f"{idx}: riga {cod.upper()} diversa dai dati: {celle}")
        errori += controlla_noleggio(t, idx, ['id="answer"', "</table>"])
        mm = NOMI_NOLEGGIO_PED.search(unescape(re.sub(r"<[^>]+>", " ", t))) or AFFILIATI_PAT.search(t)
        if mm:
            errori.append(f"{idx}: nome vietato '{mm.group(0)}'")
        if G.NOLEGGIO_AUTO and G.MON.link_affiliati(t):
            conti["noleggio"] += 1
    # d) collegamenti in entrata e dati senza nomi di assistenti
    if f'href="{G.PED_BASE}/"' not in leggi("index.html"):
        errori.append("home senza link alla sezione 'Tolls with a rental car'")
    if 'id="tolls-rental-car"' not in leggi("about/index.html"):
        errori.append("About senza la sezione 'Tolls with a rental car'")
    if f'href="../{G.PED_BASE}/"' not in leggi(f"{G.PAT_BASE}/index.html"):
        errori.append("indice Driving abroad senza link alla sezione dei pedaggi")
    for nome in ("pedaggi.json", "pedaggi_manuali.json", "pedaggi_domanda.json"):
        if VIETATE_SRV.search((SITO.parent / "dati" / nome).read_text(encoding="utf-8")):
            errori.append(f"dati/{nome}: nome di un assistente di intelligenza artificiale")
    return errori, conti


_spec_gom = importlib.util.spec_from_file_location("raccolta_gomme", Path(__file__).resolve().parent / "raccolta" / "gomme.py")
RGOM = importlib.util.module_from_spec(_spec_gom)
_spec_gom.loader.exec_module(RGOM)
# Fonti ammesse: ministeri, polizia, agenzie pubbliche per la sicurezza stradale, portali e raccolte di leggi dei governi (niente club, produttori, noleggi)
FONTI_UFFICIALI_GOM = re.compile(r"^https://(?:www\.mit\.gov\.it|www\.poliziadistato\.it|www\.bmimi\.gv\.at|www\.bmv\.de|www\.gesetze-im-internet\.de|"
                                 r"www\.service-public\.gouv\.fr|www\.ch\.ch|portalspv\.avp-rs\.si|www\.slovenia\.info|zagrebacka-policija\.gov\.hr|md\.gov\.cz|"
                                 r"www\.slovensko\.sk|www\.vegvesen\.no|www\.transportstyrelsen\.se|traficom\.fi|www\.dgt\.es|www\.govern\.ad|www\.mobilitat\.ad)/")
FRASE_NOLEGGIO_GOM = "ask the rental company whether winter tyres or chains are included and at what cost"


def _numeri_gom(s):
    """Numeri di un testo (date complete escluse; '5 000' -> '5000'; '3,5' -> '3.5'; '1st' -> '1')."""
    s = re.sub(r"(?<=\d),(?=\d\b)", ".", s)  # "3,5 t" -> 3.5
    return _numeri_ped(re.sub(r"\b\d{1,2} (?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4}\b", " ", s))


def controlla_gomme():
    """Punto 21: dati = fonti = pagine; pagine solo con ricerche vere; prima frase; traduzioni; numeri; FAQ; DiscoverCars; link andata e ritorno."""
    from html import unescape
    errori = []
    conti = {"paesi": 0, "pagine": 0, "fonti": 0, "citazioni": 0, "faq": 0, "cache": "no", "noleggio": 0, "link": 0}
    if not G.GOM:
        return ["dati/gomme.json mancante (rilanciare raccolta/gomme.py)"], conti
    M = json.loads((SITO.parent / "dati" / "gomme_manuali.json").read_text(encoding="utf-8"))
    if M["paesi"] != G.GOM["paesi"]:
        errori.append("dati/gomme.json non è aggiornato rispetto a dati/gomme_manuali.json (rilanciare raccolta/gomme.py)")
    D = json.loads((SITO.parent / "dati" / "gomme_domanda.json").read_text(encoding="utf-8"))
    ricerche = {s for g in D["paesi"].values() for qq in g.values() for ss in qq.values() for s in ss}
    # a) fonti: HTTP 200, solo domini ufficiali, data; dalla cache frasi e impronte ricalcolate
    cache = RGOM.CACHE.exists()
    for fid, F in G.GOM["fonti"].items():
        conti["fonti"] += 1
        if F["http"] != 200:
            errori.append(f"fonte {fid}: HTTP {F['http']}")
        if not FONTI_UFFICIALI_GOM.match(F["url"]):
            errori.append(f"fonte {fid}: dominio non ufficiale o non previsto: {F['url']}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", F["letto_il"] or "") or F["letto_il"] > G.OGGI.isoformat():
            errori.append(f"fonte {fid}: data di lettura non valida {F['letto_il']}")
        f_c = RGOM.file_cache(fid)
        if copia_usabile(21, fid, f_c, "gomme.py"):
            ef = []
            t = RGOM.testo_fonte(f_c.read_bytes(), RGOM.FONTI[fid].get("tipo", "html"))
            frasi = RGOM.frasi_fonte(G.GOM, fid)
            for x in frasi:
                if x not in t:
                    ef.append(f"fonte {fid}: la frase non è nel testo salvato: {x[:70]}")
            if RGOM.impronta_zona(t, frasi) != F["impronta"]:
                ef.append(f"fonte {fid}: impronta diversa dal testo salvato (rilanciare raccolta/gomme.py)")
            errori += esito_copia(21, fid, ef, f_c, F["letto_il"])
            conti["cache"] = "sì"
    # b) pagine Paese solo dove ci sono ricerche vere (ricalcolate da gomme_domanda.json)
    attese_pag = sorted(p["iso2"] for p in M["paesi"] if len(RGOM.ricerche_paese(D, p["iso2"])) >= RGOM.MIN_RICERCHE)
    if attese_pag != sorted(G.GOM_PAGINE):
        errori.append(f"pagine Paese diverse dalle ricerche vere: attese {attese_pag}, nei dati {sorted(G.GOM_PAGINE)}")
    sm = leggi("sitemap.xml")
    attese = {G.url_gom(c) + "index.html" for c in attese_pag} | {f"{G.GOM_BASE}/index.html"}
    trovate = {q.relative_to(SITO).as_posix() for q in (SITO / G.GOM_BASE).rglob("index.html")} if (SITO / G.GOM_BASE).exists() else set()
    if attese != trovate:
        errori.append(f"pagine winter-tyres diverse dai dati: mancano {sorted(attese - trovate)}, in più {sorted(trovate - attese)}")
    for p in G.GOM_PAESI:
        c = p["iso2"]
        conti["paesi"] += 1
        tr = p.get("traduzioni", {})
        # parole nostre: nessun numero che non stia in una citazione (o nella sua traduzione, controllata a parte)
        ammessi = set().union(*[_numeri_gom(x["x"]) for x in p["citazioni"]], {"2026", "27"})
        for campo in ("risposta", "obbligo_breve", "periodo_breve", "catene_breve", "nota", "chi"):
            extra = _numeri_gom(p.get(campo) or "") - ammessi
            if extra:
                errori.append(f"gomme {c}: numeri non presi dalle fonti in '{campo}': {sorted(extra)}")
        for i, testo in tr.items():
            x = next((y for y in p["citazioni"] if y["id"] == i), None)
            if not x:
                errori.append(f"gomme {c}: traduzione di una citazione che non c'è: {i}")
            elif _numeri_gom(testo) - _numeri_gom(x["x"]) - {"6", "4", "7", "1"}:  # "Article 6(4)(e)", "7(1)": numeri dell'articolo riscritti
                errori.append(f"gomme {c}: la traduzione di {i} ha numeri che non sono nella citazione: {sorted(_numeri_gom(testo) - _numeri_gom(x['x']))}")
        for x in p["citazioni"]:
            if G.GOM["fonti"][x["f"]]["lingua"] != "en" and x["id"] not in tr:
                errori.append(f"gomme {c}: citazione {x['id']} non in inglese senza traduzione")
        for q in p["faq"]:
            extra = _numeri_gom(q["pre"] + " " + q["post"]) - ammessi
            if extra:
                errori.append(f"gomme {c}: numeri non presi dalle fonti nella FAQ «{q['q']}»: {sorted(extra)}")
            if q["query"] not in ricerche:
                errori.append(f"gomme {c}: FAQ «{q['q']}» senza una ricerca vera ({q['query']!r} non è in dati/gomme_domanda.json)")
            lingue = {G.GOM["fonti"][cit_x["f"]]["lingua"] for cit_x in p["citazioni"] if cit_x["id"] in q["cit"]}
            if lingue - {"en"} and "our translation from" not in q["pre"]:
                errori.append(f"gomme {c}: FAQ «{q['q']}» cita una traduzione senza dirlo")
        if p["noleggio"] != "non_detto" or any(re.search(r"\b(?:rent|rental|hire)", x["x"], re.I) for x in p["citazioni"]):
            errori.append(f"gomme {c}: la sezione dice 'non menzionano le auto a noleggio': controllare noleggio e citazioni")
        if c not in G.GOM_PAGINE:
            continue
        rel = G.url_gom(c) + "index.html"
        if not (SITO / rel).exists():
            continue
        conti["pagine"] += 1
        t = leggi(rel)
        vis = unescape(re.sub(r"<[^>]+>", " ", t))
        if f"<loc>{G.URL_SITO}/{G.url_gom(c)}</loc><lastmod>{G.data_gom(p)}</lastmod>" not in sm:
            errori.append(f"{rel}: non in sitemap o lastmod diverso dalla data di lettura {G.data_gom(p)}")
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if tit != p["titolo"] or len(tit) > G.LIMITE_TITOLO_GOM or G.STAGIONE_GOM not in tit or p["nome"] not in tit:
            errori.append(f"{rel}: titolo oltre {G.LIMITE_TITOLO_GOM} caratteri, senza la stagione o senza il Paese: {tit}")
        m = re.search(r'<p class="lead" id="answer">(.*?)</p>', t)
        attesa = f"According to {p['chi']}, checked on {G.data_lunga(G.data_gom(p))}, {p['risposta']}"
        if not m or unescape(m.group(1)) != attesa:
            errori.append(f"{rel}: prima frase diversa da 'According to <fonte>, checked on <data>, <risposta>'")
        for x in p["citazioni"]:
            conti["citazioni"] += 1
            if escape(x["x"], quote=False) not in t and escape(x["x"]) not in t:
                errori.append(f"{rel}: citazione mancante: {x['x'][:60]}")
            if x["id"] in tr and escape(tr[x["id"]]) not in t and escape(tr[x["id"]], quote=False) not in t:
                errori.append(f"{rel}: traduzione mancante: {x['id']}")
        for f in G.fonti_gom(p):
            F = G.GOM["fonti"][f]
            if f'href="{escape(F["pagina"])}"' not in t or f"checked on {G.data_lunga(F['letto_il'])}" not in vis:
                errori.append(f"{rel}: manca il link o la data della fonte {f}")
        sez = re.search(r'id="rental">.*?</h2>\s*<p data-nol-non-detto>(.*?)</p>', t, re.S)
        if not sez or FRASE_NOLEGGIO_GOM not in unescape(sez.group(1)).lower() or "do not say whether rental cars come with winter tyres or chains" not in unescape(sez.group(1)):
            errori.append(f"{rel}: manca la frase 'ask the rental company whether winter tyres or chains are included and at what cost'")
        faq_ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t)]
        faq_ld = next((x for x in faq_ld if x.get("@type") == "FAQPage"), None)
        attese_faq = G.faq_gom(p)
        if not faq_ld or [(e["name"], e["acceptedAnswer"]["text"]) for e in faq_ld["mainEntity"]] != attese_faq:
            errori.append(f"{rel}: FAQ JSON-LD diversa dalle domande previste")
        for qd, a in attese_faq:
            conti["faq"] += 1
            if f"<h3>{escape(qd)}</h3><p>{escape(a)}</p>" not in t:
                errori.append(f"{rel}: FAQ visibile diversa dal JSON-LD: {qd}")
        errori += controlla_noleggio(t, rel, ['id="answer"', 'id="official"', 'id="rental"'])
        if G.NOLEGGIO_AUTO and G.MON.link_affiliati(t):
            conti["noleggio"] += 1
        vis_en = unescape(re.sub(r"<[^>]+>", " ", re.sub(r'(?s)<blockquote class="cit" lang="(?!en)[a-z]+">.*?</blockquote>', " ", t)))
        mm = NOMI_NOLEGGIO_PED.search(vis_en) or AFFILIATI_PAT.search(t) or VIETATE_SRV.search(vis)
        if mm:
            errori.append(f"{rel}: nome vietato (noleggio, rete o assistente) '{mm.group(0)}'")
        if "not legal advice" not in vis:
            errori.append(f"{rel}: manca 'not legal advice'")
        # link andata e ritorno: Driving abroad e Tolls dello stesso Paese
        for k in G.PATENTI:
            if c in G.PAGINE_PAT[k]:
                conti["link"] += 1
                if f'href="../../{G.url_pat(k, c)}"' not in t:
                    errori.append(f"{rel}: manca il link a {G.url_pat(k, c)}")
                if f'href="../../../{G.url_gom(c)}"' not in leggi(G.url_pat(k, c) + "index.html"):
                    errori.append(f"{G.url_pat(k, c)}: manca il link alla pagina delle gomme {G.url_gom(c)}")
        if c in G.PED_PER:
            conti["link"] += 1
            if f'href="../../{G.url_ped(c)}"' not in t:
                errori.append(f"{rel}: manca il link a {G.url_ped(c)}")
            if f'href="../../{G.url_gom(c)}"' not in leggi(G.url_ped(c) + "index.html"):
                errori.append(f"{G.url_ped(c)}: manca il link alla pagina delle gomme {G.url_gom(c)}")
        if f'href="{G.url_gom(c)}"' not in leggi("index.html"):
            errori.append(f"home senza link a {G.url_gom(c)}")
    # c) indice: sitemap, titolo, tabella = dati, FAQ da ricerche vere, riquadro dopo la tabella
    idx = f"{G.GOM_BASE}/index.html"
    if (SITO / idx).exists():
        t = leggi(idx)
        if f"<loc>{G.URL_SITO}/{G.GOM_BASE}/</loc><lastmod>{G.GOM['controllato_il']}</lastmod>" not in sm:
            errori.append("indice winter-tyres-rental-car non in sitemap o lastmod diverso")
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(tit) > G.LIMITE_TITOLO_GOM or G.STAGIONE_GOM not in tit:
            errori.append(f"{idx}: titolo oltre {G.LIMITE_TITOLO_GOM} caratteri o senza la stagione: {tit}")
        m = re.search(r'<p class="lead" id="answer">(.*?)</p>', t)
        if not m or unescape(m.group(1)) != G.prima_frase_gom() or f"last checked on {G.data_lunga(G.GOM['controllato_il'])}" not in unescape(m.group(1)):
            errori.append(f"{idx}: prima frase diversa dai conteggi o senza la data")
        righe = re.findall(r'<tr data-voce id="([a-z]{2})">(.*?)</tr>', t)
        if [r[0].upper() for r in righe] != [p["iso2"] for p in G.GOM_PAESI]:
            errori.append(f"{idx}: righe della tabella diverse dai Paesi dei dati")
        for (cod, r), p in zip(righe, G.GOM_PAESI):
            celle = [unescape(re.sub(r"<[^>]+>", "", x)) for x in re.findall(r"<td[^>]*>(.*?)</td>", r)]
            fonti = " · ".join(e for e, _ in G.enti_gom(p))
            if celle != [p["nome"], f"{G.OBBLIGO_GOM[p['obbligo']]} – {p['obbligo_breve']}", p["periodo_breve"], p["catene_breve"], "Not covered", fonti,
                         G.data_lunga(G.data_gom(p))]:
                errori.append(f"{idx}: riga {cod.upper()} diversa dai dati: {celle}")
            for _, f in G.enti_gom(p):
                if f'href="{escape(G.GOM["fonti"][f]["pagina"])}"' not in r:
                    errori.append(f"{idx}: riga {cod.upper()} senza il link alla fonte {f}")
        for f in M.get("faq_indice", []):
            if f["query"] not in ricerche:
                errori.append(f"{idx}: FAQ «{f['q']}» senza una ricerca vera")
        if [q for q, _ in G.faq_indice_gom()] != [f["q"] for f in M.get("faq_indice", [])]:
            errori.append(f"{idx}: FAQ diverse da faq_indice")
        for q, a in G.faq_indice_gom():
            conti["faq"] += 1
            if f"<h3>{escape(q)}</h3><p>{escape(a)}</p>" not in t:
                errori.append(f"{idx}: FAQ mancante: {q}")
        errori += controlla_noleggio(t, idx, ['id="answer"', "</table>"])
        mm = NOMI_NOLEGGIO_PED.search(unescape(re.sub(r"<[^>]+>", " ", t))) or AFFILIATI_PAT.search(t) or VIETATE_SRV.search(t)
        if mm:
            errori.append(f"{idx}: nome vietato '{mm.group(0)}'")
        if G.NOLEGGIO_AUTO and G.MON.link_affiliati(t):
            conti["noleggio"] += 1
    else:
        errori.append("indice winter-tyres-rental-car mancante")
    # d) collegamenti in entrata e dati senza nomi di assistenti
    if f'href="{G.GOM_BASE}/"' not in leggi("index.html"):
        errori.append("home senza link alla sezione 'Winter tyres with a rental car'")
    if 'id="winter-tyres-rental-car"' not in leggi("about/index.html"):
        errori.append("About senza la sezione 'Winter tyres with a rental car'")
    for pag in (f"{G.PAT_BASE}/index.html", f"{G.PED_BASE}/index.html"):
        if f'href="../{G.GOM_BASE}/"' not in leggi(pag):
            errori.append(f"{pag}: manca il link alla sezione delle gomme")
    if 'href="/winter-tyres-rental-car/"' not in leggi("404.html"):
        errori.append("404 senza link alla sezione delle gomme")
    for nome in ("gomme.json", "gomme_manuali.json", "gomme_domanda.json"):
        if VIETATE_SRV.search((SITO.parent / "dati" / nome).read_text(encoding="utf-8")):
            errori.append(f"dati/{nome}: nome di un assistente di intelligenza artificiale")
    return errori, conti


# ---------------------------------------------------------------- 23. Patente straniera in Canada, Australia e Nuova Zelanda (31/10/2026)
_spec_fl = importlib.util.spec_from_file_location("raccolta_patente_straniera", Path(__file__).resolve().parent / "raccolta" / "patente_straniera.py")
RFL = importlib.util.module_from_spec(_spec_fl)
_spec_fl.loader.exec_module(RFL)
# Fonti ammesse: enti delle patenti e governi di province, stati e territori, NZ Transport Agency, LegisQuébec (niente broker, scuole guida, blog)
FONTI_UFFICIALI_FL = re.compile(r"^https://(?:www\.ontario\.ca|icbc\.com|www\.legisquebec\.gouv\.qc\.ca|www\.alberta\.ca|www\.mpi\.mb\.ca|sgi\.sk\.ca|novascotia\.ca|"
                                r"www\.gnb\.ca|www\.gov\.nl\.ca|www\.idmv\.inf\.gov\.nt\.ca|www\.nsw\.gov\.au|www\.qld\.gov\.au|www\.transport\.wa\.gov\.au|"
                                r"www\.nzta\.govt\.nz)/")
FONTI_BLOCCATE_FL = re.compile(r"^https://(?:saaq\.gouv\.qc\.ca|www\.princeedwardisland\.ca|yukon\.ca|www\.gov\.nu\.ca|www\.vicroads\.vic\.gov\.au|www\.sa\.gov\.au|"
                               r"www\.transport\.tas\.gov\.au|www\.accesscanberra\.act\.gov\.au|nt\.gov\.au|www\.nzta\.govt\.nz)/")


def controlla_patente_straniera():
    """Punto 23: fonti = dati = pagine; pagine non lette senza regole; prima frase; numeri; FAQ; DiscoverCars; link in entrata."""
    from html import unescape
    errori = []
    conti = {"giur": 0, "lette": 0, "pagine": 0, "fonti": 0, "citazioni": 0, "faq": 0, "cache": "no", "noleggio": 0, "bloccate": 0, "link": 0}
    if not G.FL:
        return ["dati/patente_straniera.json mancante (rilanciare raccolta/patente_straniera.py)"], conti
    M = json.loads((SITO.parent / "dati" / "patente_straniera_manuali.json").read_text(encoding="utf-8"))
    if M["giurisdizioni"] != G.FL["giurisdizioni"] or M.get("faq_indice", []) != G.FL.get("faq_indice", []):
        errori.append("dati/patente_straniera.json non è aggiornato rispetto a dati/patente_straniera_manuali.json (rilanciare la raccolta)")
    D = json.loads((SITO.parent / "dati" / "patente_straniera_domanda.json").read_text(encoding="utf-8"))
    ricerche = RFL.tutte_ricerche(D)
    # a) fonti lette: HTTP 200, domini ufficiali, data; dalla cache frasi e impronte ricalcolate
    cache = RFL.CACHE.exists()
    for fid, F in G.FL["fonti"].items():
        conti["fonti"] += 1
        if F["http"] != 200:
            errori.append(f"fonte {fid}: HTTP {F['http']}")
        if not FONTI_UFFICIALI_FL.match(F["url"]):
            errori.append(f"fonte {fid}: dominio non ufficiale o non previsto: {F['url']}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", F["letto_il"] or "") or F["letto_il"] > G.OGGI.isoformat():
            errori.append(f"fonte {fid}: data di lettura non valida {F['letto_il']}")
        f_c = RFL.file_cache(fid)
        if copia_usabile(23, fid, f_c, "patente_straniera.py"):
            ef = []
            t = RFL.testo_fonte(f_c.read_bytes(), RFL.FONTI[fid].get("tipo", "html"))
            frasi = RFL.frasi_fonte(G.FL, fid)
            for x in frasi:
                if x not in t:
                    ef.append(f"fonte {fid}: la frase non è nel testo salvato: {x[:70]}")
            if RFL.impronta_zona(t, frasi) != F["impronta"]:
                ef.append(f"fonte {fid}: impronta diversa dal testo salvato (rilanciare la raccolta)")
            conti["cache"] = "sì"
            errori += esito_copia(23, fid, ef, f_c, F["letto_il"])
    # b) pagine bloccate: davvero non aperte (codice diverso da 200 o pagina anti-robot), domini ufficiali, nessuna regola
    for bid, B in G.FL["bloccate"].items():
        conti["bloccate"] += 1
        if not FONTI_BLOCCATE_FL.match(B["url"]):
            errori.append(f"pagina bloccata {bid}: dominio non previsto {B['url']}")
        if B["http"] == 200 and not B["antirobot"]:
            errori.append(f"pagina bloccata {bid}: ora risponde 200 senza controllo anti-robot: leggerla e scrivere le regole")
    # c) pagine = giurisdizioni lette + indice (nessuna pagina "patente × destinazione")
    sm = leggi("sitemap.xml")
    attese = {G.url_fl(g) + "index.html" for g in G.FL_LETTE} | {f"{G.FL_BASE}/index.html"}
    trovate = {q.relative_to(SITO).as_posix() for q in (SITO / G.FL_BASE).rglob("*.html")} if (SITO / G.FL_BASE).exists() else set()
    if attese != trovate:
        errori.append(f"pagine {G.FL_BASE} diverse dai dati: mancano {sorted(attese - trovate)}, in più {sorted(trovate - attese)}")
    tutti_numeri = set().union(*[_numeri_gom(x["x"]) for g in G.FL_GIUR for x in g["citazioni"]])
    for g in G.FL_GIUR:
        conti["giur"] += 1
        if not g["letta"]:
            if g["citazioni"] or g.get("bloccata") not in G.FL["bloccate"] or (SITO / G.url_fl(g)).exists():
                errori.append(f"{g['id']}: giurisdizione non letta con citazioni, senza pagina bloccata o con una pagina propria")
            continue
        conti["lette"] += 1
        ammessi = set().union(*[_numeri_gom(x["x"]) for x in g["citazioni"]], *[_numeri_gom(G.FL["fonti"][f]["titolo"]) for f in G.fonti_fl(g)], {str(G.ANNO)})
        for campo in ("risposta", "visitatori", "residenti", "idp", "uk_breve", "us_breve", "nota", "chi"):
            extra = _numeri_gom(g.get(campo) or "") - ammessi
            if extra:
                errori.append(f"{g['id']}: numeri non presi dalle fonti in '{campo}': {sorted(extra)}")
        for q in g["faq"]:
            extra = _numeri_gom(q["pre"] + " " + q["post"] + " " + q["q"]) - ammessi
            if extra:
                errori.append(f"{g['id']}: numeri non presi dalle fonti nella FAQ «{q['q']}»: {sorted(extra)}")
            if q["query"] not in ricerche:
                errori.append(f"{g['id']}: FAQ «{q['q']}» senza una ricerca vera ({q['query']!r})")
        ids = {x["id"] for x in g["citazioni"]}
        if g["uk_cit"] not in ids or g["us_cit"] not in ids:
            errori.append(f"{g['id']}: scambio UK/US senza citazione")
        if g["uk"] == "si" and not re.search(r"United Kingdom|Great Britain|England", cit_testo := G.cit_fl(g, g["uk_cit"])["x"]):
            errori.append(f"{g['id']}: 'UK licence exchange: Yes' ma la citazione non nomina il Regno Unito: {cit_testo[:60]}")
        if g["us"] == "si" and not re.search(r"United States|US states|U\.S\. States|US state", G.cit_fl(g, g["us_cit"])["x"]):
            errori.append(f"{g['id']}: 'US licence exchange: Yes' ma la citazione non nomina gli Stati Uniti")
        rel = G.url_fl(g) + "index.html"
        if not (SITO / rel).exists():
            continue
        conti["pagine"] += 1
        t = leggi(rel)
        vis = unescape(re.sub(r"<[^>]+>", " ", t))
        if f"<loc>{G.URL_SITO}/{G.url_fl(g)}</loc><lastmod>{G.data_fl(g)}</lastmod>" not in sm:
            errori.append(f"{rel}: non in sitemap o lastmod diverso dalla data di lettura {G.data_fl(g)}")
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(tit) > G.LIMITE_TITOLO_FL or str(G.ANNO) not in tit or (g["nome"] not in tit and g["paese"] != "NZ") or tit != G.scegli(G.titoli_fl(g), G.LIMITE_TITOLO_FL):
            errori.append(f"{rel}: titolo oltre {G.LIMITE_TITOLO_FL} caratteri, senza l'anno o il nome, o non tra le forme previste: {tit}")
        m = re.search(r'<p class="lead" id="answer">(.*?)</p>', t)
        attesa = f"According to {g['chi']}, checked on {G.data_lunga(G.data_fl(g))}, {g['risposta']}"
        if not m or unescape(m.group(1)) != attesa:
            errori.append(f"{rel}: prima frase diversa da 'According to <fonte>, checked on <data>, <risposta>'")
        for x in g["citazioni"]:
            conti["citazioni"] += 1
            if escape(x["x"], quote=False) not in t and escape(x["x"]) not in t:
                errori.append(f"{rel}: citazione mancante: {x['x'][:60]}")
        for f in G.fonti_fl(g):
            F = G.FL["fonti"][f]
            if f'href="{escape(F["url"])}"' not in t or f"checked on {G.data_lunga(F['letto_il'])}" not in vis:
                errori.append(f"{rel}: manca il link o la data della fonte {f}")
        if g.get("fonte_non_letta") and ("data-non-letta" not in t or f'href="{escape(G.FL["bloccate"][g["fonte_non_letta"]]["url"])}"' not in t):
            errori.append(f"{rel}: manca la riga sulla fonte ufficiale che non si è aperta")
        faq_ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t)]
        faq_ld = next((x for x in faq_ld if x.get("@type") == "FAQPage"), None)
        attese_faq = G.faq_fl(g)
        if not faq_ld or [(e["name"], e["acceptedAnswer"]["text"]) for e in faq_ld["mainEntity"]] != attese_faq:
            errori.append(f"{rel}: FAQ JSON-LD diversa dalle domande previste")
        for qd, a in attese_faq:
            conti["faq"] += 1
            if f"<h3>{escape(qd)}</h3><p>{escape(a)}</p>" not in t:
                errori.append(f"{rel}: FAQ visibile diversa dal JSON-LD: {qd}")
        errori += controlla_noleggio(t, rel, ['id="answer"', 'id="official"', '<blockquote class="cit">'])
        if G.NOLEGGIO_AUTO and G.MON.link_affiliati(t):
            conti["noleggio"] += 1
        mm = NOMI_NOLEGGIO_PED.search(vis) or AFFILIATI_PAT.search(t) or VIETATE_SRV.search(vis) or AGGIRARE.search(vis)
        if mm:
            errori.append(f"{rel}: parola vietata (noleggio, rete, assistente o aggiramento) '{mm.group(0)}'")
        if "not legal advice" not in vis:
            errori.append(f"{rel}: manca 'not legal advice'")
        if f'href="{"../" * G.url_fl(g).count("/")}{G.FL_BASE}/"' not in t:
            errori.append(f"{rel}: manca il link all'indice della sezione")
    # d) indice: sitemap, titolo, prima frase, righe = dati, righe "Not read", FAQ, riquadro dopo le tabelle
    idx = f"{G.FL_BASE}/index.html"
    if (SITO / idx).exists():
        t = leggi(idx)
        vis = unescape(re.sub(r"<[^>]+>", " ", t))
        if f"<loc>{G.URL_SITO}/{G.FL_BASE}/</loc><lastmod>{G.FL['controllato_il']}</lastmod>" not in sm:
            errori.append(f"indice {G.FL_BASE} non in sitemap o lastmod diverso")
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(tit) > G.LIMITE_TITOLO_FL or str(G.ANNO) not in tit:
            errori.append(f"{idx}: titolo oltre {G.LIMITE_TITOLO_FL} caratteri o senza l'anno: {tit}")
        m = re.search(r'<p class="lead" id="answer">(.*?)</p>', t)
        if not m or unescape(m.group(1)) != G.prima_frase_fl() or f"checked on {G.data_lunga(G.FL['controllato_il'])}" not in unescape(m.group(1)):
            errori.append(f"{idx}: prima frase diversa dai conteggi o senza la data")
        righe = re.findall(r'<tr data-voce id="([a-z_]+)">(.*?)</tr>', t)
        if [r[0] for r in righe] != [g["id"] for g in G.FL_GIUR]:
            errori.append(f"{idx}: righe delle tabelle diverse dalle giurisdizioni dei dati")
        for (cod, r), g in zip(righe, G.FL_GIUR):
            celle = [unescape(re.sub(r"<[^>]+>", "", x)) for x in re.findall(r"<td[^>]*>(.*?)</td>", r)]
            if not g["letta"]:
                if not celle or not celle[-1].startswith("Not read.") or "did not open for our check" not in celle[-1]:
                    errori.append(f"{idx}: riga {cod} non letta senza 'Not read'")
                continue
            if celle[:6] != [g["nome"], g["visitatori"], g["residenti"], g["idp"], G.SCAMBIO_FL[g["uk"]], G.SCAMBIO_FL[g["us"]]]:
                errori.append(f"{idx}: riga {cod} diversa dai dati: {celle[:6]}")
            if f'href="../{G.url_fl(g)}"' not in r:
                errori.append(f"{idx}: riga {cod} senza il link alla pagina")
        for f in M.get("faq_indice", []):
            if f["query"] not in ricerche:
                errori.append(f"{idx}: FAQ «{f['q']}» senza una ricerca vera")
        if [q for q, _ in G.faq_indice_fl()] != [f["q"] for f in M.get("faq_indice", [])]:
            errori.append(f"{idx}: FAQ diverse da faq_indice")
        for q, a in G.faq_indice_fl():
            conti["faq"] += 1
            if f"<h3>{escape(q)}</h3><p>{escape(a)}</p>" not in t:
                errori.append(f"{idx}: FAQ mancante: {q}")
            extra = _numeri_gom(a) - tutti_numeri - {str(G.ANNO)}
            if extra:
                errori.append(f"{idx}: numeri non presi dalle fonti nella FAQ «{q}»: {sorted(extra)}")
        errori += controlla_noleggio(t, idx, ['id="answer"', "</table>"])
        if G.NOLEGGIO_AUTO and G.MON.link_affiliati(t):
            conti["noleggio"] += 1
        mm = NOMI_NOLEGGIO_PED.search(vis) or AFFILIATI_PAT.search(t) or VIETATE_SRV.search(vis) or AGGIRARE.search(vis)
        if mm:
            errori.append(f"{idx}: parola vietata '{mm.group(0)}'")
    else:
        errori.append(f"indice {G.FL_BASE} mancante")
    # e) collegamenti in entrata: home, About, 404, indice Driving abroad, pagine Driving abroad di Canada, Australia e Nuova Zelanda
    if f'href="{G.FL_BASE}/"' not in leggi("index.html"):
        errori.append("home senza link alla sezione della patente straniera")
    if f'id="{G.FL_BASE}"' not in leggi("about/index.html"):
        errori.append("About senza la sezione della patente straniera")
    if f'href="/{G.FL_BASE}/"' not in leggi("404.html"):
        errori.append("404 senza link alla sezione della patente straniera")
    if f'href="../{G.FL_BASE}/"' not in leggi(f"{G.PAT_BASE}/index.html"):
        errori.append(f"{G.PAT_BASE}/index.html: manca il link alla sezione della patente straniera")
    for k in G.PATENTI:
        for c in ("CA", "AU", "NZ"):
            if c in G.PAGINE_PAT[k]:
                conti["link"] += 1
                atteso = G.url_fl(G.FL_PER["nz"]) if c == "NZ" else f"{G.FL_BASE}/#{G.FL_PAESI[c][1]}"
                if f'href="../../../{atteso}"' not in leggi(G.url_pat(k, c) + "index.html"):
                    errori.append(f"{G.url_pat(k, c)}: manca il link a {atteso}")
    for nome in ("patente_straniera.json", "patente_straniera_manuali.json", "patente_straniera_domanda.json"):
        if VIETATE_SRV.search((SITO.parent / "dati" / nome).read_text(encoding="utf-8")):
            errori.append(f"dati/{nome}: nome di un assistente di intelligenza artificiale")
    return errori, conti


_spec_big = importlib.util.spec_from_file_location("raccolta_biglietti", Path(__file__).resolve().parent / "raccolta" / "biglietti.py")
RBIG = importlib.util.module_from_spec(_spec_big)
_spec_big.loader.exec_module(RBIG)
# Domini ufficiali: siti delle attrazioni e biglietterie che le loro pagine ufficiali indicano (nessun rivenditore, nessuna guida)
DOMINI_UFFICIALI_BIG = {"cenacolovinciano.org", "cenacolovinciano.vivaticket.it", "www.museivaticani.va", "tickets.museivaticani.va",
                        "www.annefrank.org", "pompeiisites.org", "pompeii.vivaticket.it", "www.alhambra-patronato.es", "tickets.alhambra-patronato.es",
                        "sagradafamilia.org",
                        # Giappone e USA (31/10/2026): siti ufficiali e biglietterie che le pagine ufficiali indicano
                        "www.ghibli-museum.jp", "ghibli-park.jp", "l-tike.com", "museum.nintendo.com", "museum-tickets.nintendo.com",
                        "www.sumo.or.jp", "sumo.pia.jp", "sankan.kunaicho.go.jp", "www.recreation.gov", "www.nps.gov"}
# Mesi e numeri ordinali in inglese, scritti qui di nuovo (controllo indipendente da genera.py)
MESI_EN_BIG = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def _ordinale_big(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def _ore_in_testo_big(x):
    """Orari scritti nella frase ufficiale ("10 a.m.", "10a.m.", "2 p.m.", "5.00 a.m.", "10:00am", "3:00 pm", "10 AM", "12 noon") -> {"HH:MM"}."""
    out = set()
    for h, m, ap in re.findall(r"\b(\d{1,2})(?:[.:](\d{2}))?\s?(a\.m\.|p\.m\.|am|pm|AM|PM|noon)", x):
        h, m = int(h), int(m or 0)
        ap = ap.lower().replace(".", "")
        if ap == "pm" and h != 12:
            h += 12
        if ap == "am" and h == 12:
            h = 0
        out.add(f"{h:02d}:{m:02d}")
    return out


def _data_md_big(t):
    """"January 10th" / "June 30th" -> (mese, giorno)."""
    m = re.fullmatch(r"([A-Z][a-z]+) (\d{1,2})(?:st|nd|rd|th)", t)
    return (MESI_EN_BIG.index(m.group(1)) + 1, int(m.group(2))) if m and m.group(1) in MESI_EN_BIG else None
# Rivenditori e venditori di visite: mai nominati né linkati nella sezione (Viator solo nel riquadro, quando VIATOR_TOUR sarà acceso)
RIVENDITORI_BIG = re.compile(r"lastsupperticket|tiqets|getyourguide|headout|musement|civitatis|klook|ticketbar|tickitto|isango|city ?wonders|"
                             r"walks of italy|take walks|viator|tripadvisor|ticketone|vaticanmuseum\.co|thevaticantickets|lastsupper\.shop", re.I)
# Pasqua scritta qui a mano (calendario gregoriano), indipendente dal calcolo di genera.pasqua
PASQUA_BIG = {2026: date(2026, 4, 5), 2027: date(2027, 3, 28), 2028: date(2028, 4, 16), 2029: date(2029, 4, 1), 2030: date(2030, 4, 21)}


# Stay22 (alloggi, verso Booking.com): link brevi del pannello di Massimiliano, AID massimilianocori, scritti qui a mano (31/10/2026)
HOST_STAY22 = "booking.stay22.com"
STAY22_ATTESI = {"last-supper-milan": "https://booking.stay22.com/massimilianocori/oRlYad6Fi0",
                 "vatican-museums": "https://booking.stay22.com/massimilianocori/VSsB9hodRs",
                 "anne-frank-house": "https://booking.stay22.com/massimilianocori/ozO_-oUfr2",
                 "pompeii": "https://booking.stay22.com/massimilianocori/u-N-WOGcIm",
                 "alhambra": "https://booking.stay22.com/massimilianocori/0UazHB16fM",
                 "sagrada-familia": "https://booking.stay22.com/massimilianocori/Sshoexu46U"}


def controlla_stay22_big(attese, idx, conti):
    """Link Stay22: dati = elenco atteso; ogni link solo sulla sua pagina attrazione e nell'indice; rel, target, trasparenza, etichetta,
    posizione dopo la biglietteria ufficiale; per Pompei il testo dice Napoli; stay22 in nessun'altra pagina del sito."""
    from html import unescape
    errori = []
    conti["stay22"] = 0
    dati = {s: v["url"] for s, v in G.STAY22_BIG.items()}
    if dati and dati != STAY22_ATTESI:
        errori.append(f"affiliati.json, _stay22_alloggi: link diversi da quelli attesi: {sorted(set(dati.items()) ^ set(STAY22_ATTESI.items()))}")
    if "pompeii" in G.STAY22_BIG and G.STAY22_BIG["pompeii"]["citta"] != "Naples":
        errori.append("Stay22 pompeii: il link porta agli hotel di Napoli, la città nei dati deve essere Naples")
    pagine = {G.url_big(a["slug"]) + "index.html": a["slug"] for a in G.BIG_ATT}
    for p in sorted(attese):
        if not (SITO / p).exists():
            continue
        t = leggi(p)
        voci = [(h, r) for h, host, r in G.MON.link_affiliati(t) if G.MON.dominio_in(host, ["stay22.com"])]
        attesi = set(dati.values()) if p == idx else ({dati[pagine[p]]} if pagine.get(p) in dati else set())
        trovati = [h for h, _ in voci]
        if set(trovati) != attesi or len(trovati) != len(attesi):
            errori.append(f"{p}: link Stay22 {sorted(trovati)} invece di {sorted(attesi)}")
        for h, r in voci:
            conti["stay22"] += 1
            if not {"sponsored", "noopener"} <= r:
                errori.append(f"{p}: link Stay22 senza rel=\"sponsored noopener\" ({h})")
            tag = re.search(r'<a\b[^>]*href="' + re.escape(escape(h)) + r'"[^>]*>', t)
            if not tag or 'target="_blank"' not in tag.group(0):
                errori.append(f"{p}: link Stay22 senza target=\"_blank\" ({h})")
        if not attesi:
            if "data-alloggio" in t:
                errori.append(f"{p}: riquadro 'Where to stay' senza link")
            continue
        i = t.find("data-alloggio")
        if i < 0 or any(t.find(f'href="{escape(h)}"') < i for h in trovati):
            errori.append(f"{p}: link Stay22 fuori dal riquadro 'Where to stay' (data-alloggio)")
            continue
        blocco = t[i:t.find("</section>", i)]
        if G.MON.RIGA_EN not in blocco:
            errori.append(f"{p}: riga di trasparenza non nel riquadro 'Where to stay'")
        if '<span class="aff-tag">Affiliate</span>' not in t[t.rfind('id="where-to-stay"', 0, i):i]:
            errori.append(f"{p}: riquadro 'Where to stay' senza l'etichetta Affiliate")
        prima = 'id="official-tickets"' if p != idx else 'id="calendars"'
        if not 0 <= t.find(prima) < i:
            errori.append(f"{p}: riquadro 'Where to stay' non dopo «{prima}»")
        if p != idx and pagine[p] == "pompeii" and "hotels in Naples, not in Pompeii" not in unescape(blocco):
            errori.append(f"{p}: il riquadro Stay22 di Pompei non dice che il link mostra hotel a Napoli")
        if re.search(r"cheapest|best price|lowest price|guaranteed|available now|book now", unescape(blocco), re.I):
            errori.append(f"{p}: promessa di prezzo o disponibilità nel riquadro 'Where to stay'")
    # stay22 in nessun'altra pagina del sito
    for q in SITO.rglob("*.html"):
        nome = q.relative_to(SITO).as_posix()
        if nome not in attese and nome not in {f"liquids/{x}/index.html" for x in STAY22_LIQ} and "stay22" in q.read_text(encoding="utf-8").lower():
            errori.append(f"{nome}: link Stay22 fuori dalla sezione Ticket release dates e dalle pagine liquidi previste (punto 30)")
    return errori


# Stay22 nelle pagine liquidi (5/11/2026): aeroporto -> attrazione della stessa città (link in STAY22_ATTESI), scritto qui a mano
STAY22_LIQ = {"barcelona": "sagrada-familia", "rome-fiumicino": "vatican-museums", "milan-linate": "last-supper-milan",
              "milan-malpensa": "last-supper-milan", "granada": "alhambra"}


def _fine_finestra_big(oggi, mesi):
    y, m = oggi.year + (oggi.month - 1 + mesi) // 12, (oggi.month - 1 + mesi) % 12 + 1
    ultimo = (date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)).day
    return date(y, m, min(oggi.day, ultimo))


def _attesi_big(a, oggi):
    """Ricalcolo indipendente: per ogni giorno della finestra, quali regole lo toccano. Insieme di (data, ora, tipo, regola)."""
    fine = _fine_finestra_big(oggi, G.MESI_BIG)
    out, d = set(), oggi
    while d <= fine:
        md = d.strftime("%m-%d")
        prima_dom = d.weekday() == 6 and d.day <= 7
        ultima_dom = d.weekday() == 6 and (d + timedelta(days=7)).month != d.month
        for r in a["uscite"]:
            if r["tipo"] == "settimanale" and d.weekday() == r["giorno"]:
                out.add((d.isoformat(), r["ora"], "uscita", r["id"]))
            if r["tipo"] == "prima_domenica":
                s = d + timedelta(days=r["giorni_prima"])
                if s.weekday() == 6 and s.day <= 7:
                    out.add((d.isoformat(), r["ora"], "uscita", r["id"]))
            if r["tipo"] == "mensile" and d.day == r["giorno"]:
                out.add((d.isoformat(), r["ora"], "uscita", r["id"]))
            if r["tipo"] == "date" and d.isoformat() in {x["data"] for x in r["date"]}:
                out.add((d.isoformat(), r["ora"], "uscita", r["id"]))
        g = a.get("gratis")
        if g and ((g["tipo"] == "prima_domenica" and prima_dom) or (g["tipo"] == "ultima_domenica" and ultima_dom)):
            if d.year not in PASQUA_BIG:
                raise SystemExit(f"verifica.py: aggiungere la Pasqua {d.year} a PASQUA_BIG")
            if not (md in g.get("eccezioni_md", []) or (g.get("pasqua") and d == PASQUA_BIG[d.year])):
                out.add((d.isoformat(), None, "gratis", g["tipo"]))
        if md in a["chiusure"]["md"] or d.isoformat() in a["chiusure"]["date"]:
            out.add((d.isoformat(), None, "chiusura", "chiusure"))
        if any(o.get("md") == md or o.get("data") == d.isoformat() for o in a["orari_speciali"]):
            out.add((d.isoformat(), None, "orario", "orari"))
        d += timedelta(days=1)
    return out


def _numeri_big(s):
    return {int(x) for x in re.findall(r"\d+", s)}


def _ics_righe(testo, nome, errori):
    """Controlli di forma RFC 5545 essenziali; restituisce le righe "aperte" (unfold)."""
    if not testo.endswith("\r\n") or re.search(r"(?<!\r)\n", testo):
        errori.append(f"{nome}: righe non terminate da CRLF")
    fisiche = testo.split("\r\n")[:-1]
    for r in fisiche:
        if len(r.encode("utf-8")) > 75:
            errori.append(f"{nome}: riga di {len(r.encode('utf-8'))} byte (> 75)")
            break
    aperte = []
    for r in fisiche:
        if r.startswith(" ") and aperte:
            aperte[-1] += r[1:]
        else:
            aperte.append(r)
    return aperte


def controlla_biglietti():
    """Punto 22: dati = fonti = pagine; date ricalcolate in modo indipendente; .ics validi e uguali alle date; titoli; solo link ufficiali."""
    from html import unescape
    from zoneinfo import ZoneInfo
    errori = []
    conti = {"attrazioni": 0, "fonti": 0, "citazioni": 0, "faq": 0, "date": 0, "eventi_ics": 0, "cache": "no", "link_esterni": 0}
    if not G.BIG:
        return ["dati/biglietti.json mancante (rilanciare raccolta/biglietti.py)"], conti
    M = json.loads((SITO.parent / "dati" / "biglietti_manuali.json").read_text(encoding="utf-8"))
    escl_dati = [{k: v for k, v in x.items() if k not in ("http", "letto_il", "frasi_uscita")} for x in G.BIG["escluse"]]
    if M["attrazioni"] != G.BIG["attrazioni"] or M["escluse"] != escl_dati:
        errori.append("dati/biglietti.json non è aggiornato rispetto a dati/biglietti_manuali.json (rilanciare raccolta/biglietti.py)")
    D = json.loads((SITO.parent / "dati" / "biglietti_domanda.json").read_text(encoding="utf-8"))
    ricerche = RBIG.tutte_ricerche(D)
    # a) fonti: HTTP 200, solo domini ufficiali, data; dalla cache frasi e impronte ricalcolate
    cache = RBIG.CACHE.exists()
    for fid, F in G.BIG["fonti"].items():
        conti["fonti"] += 1
        if F["http"] != 200:
            errori.append(f"fonte {fid}: HTTP {F['http']}")
        if urlparse(F["url"]).hostname not in DOMINI_UFFICIALI_BIG or not F["url"].startswith("https://"):
            errori.append(f"fonte {fid}: dominio non ufficiale o non previsto: {F['url']}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", F["letto_il"] or "") or F["letto_il"] > G.OGGI.isoformat():
            errori.append(f"fonte {fid}: data di lettura non valida {F['letto_il']}")
        f_c = RBIG.file_cache(fid)
        if copia_usabile(22, fid, f_c, "biglietti.py"):
            ef = []
            t = RBIG.testo_fonte(f_c.read_bytes())
            frasi = RBIG.frasi_fonte(G.BIG, fid)
            for x in frasi:
                if x not in t:
                    ef.append(f"fonte {fid}: la frase non è nel testo salvato: {x[:70]}")
            if RBIG.impronta_zona(t, frasi) != F["impronta"]:
                ef.append(f"fonte {fid}: impronta diversa dal testo salvato (rilanciare raccolta/biglietti.py)")
            conti["cache"] = "sì"
            errori += esito_copia(22, fid, ef, f_c, F["letto_il"])
    # a2) attrazioni escluse con un indirizzo provato: il motivo scritto deve essere coerente con l'esito della rilettura
    for x in G.BIG["escluse"]:
        if not x.get("url"):
            continue
        conti["escluse_provate"] = conti.get("escluse_provate", 0) + 1
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", x.get("letto_il") or "") or x["letto_il"] > G.OGGI.isoformat():
            errori.append(f"esclusa {x['nome']}: data della rilettura mancante")
        elif G.data_lunga(x["letto_il"]) not in x["motivo"]:
            errori.append(f"esclusa {x['nome']}: il motivo non ha la data della rilettura ({x['letto_il']})")
        if x.get("tipo") == "nessuna_regola" and (x.get("http") != 200 or x.get("frasi_uscita") != 0 or "answered" not in x["motivo"]):
            errori.append(f"esclusa {x['nome']}: 'nessuna regola' ma HTTP {x.get('http')} o {x.get('frasi_uscita')} frasi d'uscita nella pagina")
        if x.get("tipo") == "non_risponde" and (x.get("http") == 200 or "did not answer" not in x["motivo"]):
            errori.append(f"esclusa {x['nome']}: 'non risponde' ma HTTP {x.get('http')}")
        if x.get("tipo") not in ("nessuna_regola", "non_risponde"):
            errori.append(f"esclusa {x['nome']}: tipo non valido {x.get('tipo')}")
    # b) pagine: esattamente indice + una per attrazione, in sitemap; nessun'altra pagina nella sezione
    sm = leggi("sitemap.xml")
    attese = {G.url_big(a["slug"]) + "index.html" for a in G.BIG_ATT} | {f"{G.BIG_BASE}/index.html"}
    trovate = {q.relative_to(SITO).as_posix() for q in (SITO / G.BIG_BASE).rglob("index.html")} if (SITO / G.BIG_BASE).exists() else set()
    if attese != trovate:
        errori.append(f"pagine ticket-release-dates diverse dai dati: mancano {sorted(attese - trovate)}, in più {sorted(trovate - attese)}")
    for p in sorted(attese):
        if f"<loc>{G.URL_SITO}/{p[:-len('index.html')]}</loc>" not in sm:
            errori.append(f"{p}: non in sitemap")
    host_altri = {urlparse(u).hostname for u, _, _ in G.ALTRI_SITI}
    ammessi_host = DOMINI_UFFICIALI_BIG | host_altri | {urlparse(G.URL_SITO).hostname, "calendar.google.com"}
    if G.VIATOR_TOUR:
        ammessi_host.add(urlparse(G.VIATOR_TOUR).hostname)
    if G.STAY22_BIG:
        ammessi_host.add(HOST_STAY22)
    oggi = G.OGGI
    for a in G.BIG_ATT:
        conti["attrazioni"] += 1
        s = a["slug"]
        ids = {c["id"] for c in a["citazioni"]}
        # parole nostre: nessun numero che non stia in una citazione, nel titolo di una fonte o tra gli anni della finestra
        ammessi = set().union(*[_numeri_big(c["x"]) for c in a["citazioni"]], *[_numeri_big(G.BIG["fonti"][f]["titolo"]) for f in G.fonti_big(a)],
                              {2026, 2027})
        campi = [("risposta", re.sub(r"\{[^}]+\}", " ", a["risposta"])), ("orari", a["orari"]["breve"]), ("chiusure", a["chiusure"]["breve"])]
        campi += [("gratis", a["gratis"]["breve"])] if a.get("gratis") else []
        campi += [(f"uscita {r['id']}", r["breve"] + " " + r.get("indice", "")) for r in a["uscite"]]
        campi += [(f"testo {t['titolo']}", t["nota"]) for t in a["uscite_testo"]] + [("escluse", x) for x in a["chiusure"].get("escluse_md", {}).values()]
        campi += [(f"orario {o.get('md') or o.get('data')}", o["testo"]) for o in a["orari_speciali"]]
        campi += [(f"date {r['id']}", x["per"]) for r in a["uscite"] if r["tipo"] == "date" for x in r["date"]]
        campi += [(f"etichetta {r['id']}", r.get("etichetta", "")) for r in a["uscite"]] + [("nota chiusure", a["chiusure"].get("nota", ""))]
        campi += [(f"FAQ «{q['q']}»", q["pre"] + " " + q["post"]) for q in a["faq"]]
        for nome, testo in campi:
            extra = _numeri_big(testo) - ammessi
            if extra:
                errori.append(f"biglietti {s}: numeri non presi dalle fonti in {nome}: {sorted(extra)}")
        for q in a["faq"]:
            if q["query"] not in ricerche:
                errori.append(f"biglietti {s}: FAQ «{q['q']}» senza una ricerca vera ({q['query']!r} non è in dati/biglietti_domanda.json)")
        B = a["biglietteria"]
        if urlparse(B["url"]).hostname not in DOMINI_UFFICIALI_BIG or not B["url"].startswith("https://") or not B["cit"]:
            errori.append(f"biglietti {s}: biglietteria non ufficiale o senza la frase ufficiale che la indica: {B['url']}")
        # c) date: ricalcolo indipendente = genera.eventi_big; coerenza con la regola
        ev = G.eventi_big(a)
        attesi = _attesi_big(a, oggi)
        fatti = {(e["data"], e["ora"], e["tipo"], e["regola"]) for e in ev}
        if attesi != fatti or len(ev) != len(fatti):
            errori.append(f"biglietti {s}: date calcolate diverse dal ricalcolo indipendente: mancano {sorted(attesi - fatti)[:3]}, in più {sorted(fatti - attesi)[:3]}")
        for e in ev:
            conti["date"] += 1
            d = date.fromisoformat(e["data"])
            if e["tipo"] == "uscita":
                r = next(x for x in a["uscite"] if x["id"] == e["regola"])
                if r["tipo"] == "settimanale" and (d.weekday() != r["giorno"] or (r.get("visita_dopo_giorni") and
                                                                                  e["visita"] != (d + timedelta(days=r["visita_dopo_giorni"])).isoformat())):
                    errori.append(f"biglietti {s}: uscita {e['data']} non coerente con la regola settimanale")
                if r["tipo"] == "prima_domenica" and (date.fromisoformat(e["visita"]) - d).days != r["giorni_prima"]:
                    errori.append(f"biglietti {s}: uscita {e['data']} non coerente con la prima domenica {e['visita']}")
                giorno_cit = G.GIORNI_SETT[d.weekday()]
                if r["tipo"] == "settimanale" and not any(giorno_cit in G.cit_big(a, i)["x"] for i in r["cit"]):
                    errori.append(f"biglietti {s}: la citazione della regola {r['id']} non nomina {giorno_cit}")
                if r["tipo"] == "mensile":
                    mm = d.month - 1 + r["mesi_dopo"]
                    v = date(d.year + mm // 12, mm % 12 + 1, 1)
                    if d.day != r["giorno"] or e["visita"] != v.isoformat() or e.get("per") != f"{MESI_EN_BIG[v.month - 1]} {v.year}":
                        errori.append(f"biglietti {s}: uscita {e['data']} non coerente con la regola mensile ({e.get('per')})")
                if r["tipo"] == "date":
                    x = next((x for x in r["date"] if x["data"] == e["data"]), None)
                    if not x or e.get("per") != x["per"]:
                        errori.append(f"biglietti {s}: uscita {e['data']} non nella tabella ufficiale")
        # c2) le regole dicono quello che dice la frase ufficiale: giorno del mese, ora, date della tabella, giorni di anticipo, esempio ufficiale
        for r in a["uscite"]:
            testo_cit = " ".join(G.cit_big(a, i)["x"] for i in r["cit"])
            if r.get("ora") and r["ora"] not in _ore_in_testo_big(testo_cit):
                errori.append(f"biglietti {s}: l'ora {r['ora']} della regola {r['id']} non è nella frase ufficiale")
            if r["tipo"] == "mensile" and not re.search(r"\b" + _ordinale_big(r["giorno"]) + r"\b", testo_cit):
                errori.append(f"biglietti {s}: il giorno {_ordinale_big(r['giorno'])} della regola {r['id']} non è nella frase ufficiale")
            if r["tipo"] == "date":
                for x in r["date"]:
                    dd = date.fromisoformat(x["data"])
                    if f"{MESI_EN_BIG[dd.month - 1]} {dd.day}, {dd.year}" not in testo_cit:
                        errori.append(f"biglietti {s}: la data {x['data']} non è nella tabella ufficiale citata")
            if r["tipo"] == "anticipo" and not re.search(r"\b(?:%d days?|day before)\b" % r["giorni"], testo_cit + " " + r["breve"]):
                errori.append(f"biglietti {s}: i {r['giorni']} giorni di anticipo della regola {r['id']} non sono nella frase ufficiale")
            P = r.get("prova")
            if P:
                xp = G.cit_big(a, P["cit"])["x"]
                v, q = _data_md_big(P["vendita"]), _data_md_big(P["per"])
                if P["vendita"] not in xp or P["per"] not in xp or not v or not q:
                    errori.append(f"biglietti {s}: l'esempio ufficiale della regola {r['id']} non è nella citazione")
                elif r["tipo"] == "mensile" and (v[1] != r["giorno"] or (v[0] - 1 + r["mesi_dopo"]) % 12 + 1 != q[0]):
                    errori.append(f"biglietti {s}: l'esempio ufficiale ({P['vendita']} -> {P['per']}) contraddice la regola {r['id']}")
                elif r["tipo"] == "anticipo" and (date(2027, *q) - timedelta(days=r["giorni"])) != date(2027, *v):
                    errori.append(f"biglietti {s}: l'esempio ufficiale ({P['vendita']} -> {P['per']}) contraddice i {r['giorni']} giorni")
                conti["esempi"] = conti.get("esempi", 0) + 1
        if not (oggi.isoformat() <= min((e["data"] for e in ev), default=oggi.isoformat())
                and max((e["data"] for e in ev), default=oggi.isoformat()) <= _fine_finestra_big(oggi, G.MESI_BIG).isoformat()):
            errori.append(f"biglietti {s}: date fuori dalla finestra di {G.MESI_BIG} mesi")
        if s == "anne-frank-house" and len([e for e in ev if e["tipo"] == "uscita"]) < 25:
            errori.append(f"biglietti {s}: meno di 25 martedì di uscita in sei mesi")
        # d) pagina
        rel = G.url_big(s) + "index.html"
        if not (SITO / rel).exists():
            continue
        t = leggi(rel)
        vis = unescape(re.sub(r"<[^>]+>", " ", t))
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if tit != a["titolo"] or len(tit) > G.LIMITE_TITOLO_BIG or G.STAGIONE_BIG not in tit:
            errori.append(f"{rel}: titolo oltre {G.LIMITE_TITOLO_BIG} caratteri, senza gli anni o diverso dai dati: {tit}")
        m = re.search(r'<p class="lead" id="answer">(.*?)</p>', t)
        prima = unescape(re.sub(r"<[^>]+>", "", m.group(1))) if m else ""
        if "data-vecchie=" not in t or ("{next" in a["risposta"] and "data-prox=" not in (m.group(1) if m else "")):
            errori.append(f"{rel}: mancano le date 'prossime' aggiornate nel browser o l'avviso per le date passate")
        if prima != G.risposta_big(a) or not prima.startswith(f"According to {a['chi']}, checked on {G.data_lunga(G.data_big(a))}, "):
            errori.append(f"{rel}: prima frase diversa da 'According to <fonte>, checked on <data>, <risposta>'")
        for r in a["uscite"]:
            e0 = G.prossimo_big(a, "uscita", r["id"])
            if f"{{next:{r['id']}}}" in a["risposta"] and (not e0 or G.giorno_lungo(e0["data"]) not in prima):
                errori.append(f"{rel}: la prima frase non ha la prossima uscita calcolata ({r['id']})")
            if f"{{anticipo:{r['id']}}}" in a["risposta"]:
                d30 = oggi + timedelta(days=r["giorni"])
                attesa = f"{G.GIORNI_SETT[d30.weekday()]} {d30.day} {MESI_EN_BIG[d30.month - 1]} {d30.year}"
                if attesa not in prima or f'data-anticipo="{r["giorni"]}"' not in m.group(1):
                    errori.append(f"{rel}: la prima frase non ha la data di oggi + {r['giorni']} giorni ({attesa}) aggiornata nel browser")
            # ora della prossima uscita a New York (o Londra), ricalcolata qui
            if e0 and e0["ora"]:
                hh, mi = (int(x) for x in e0["ora"].split(":"))
                d0 = date.fromisoformat(e0["data"])
                u = datetime(d0.year, d0.month, d0.day, hh, mi, tzinfo=ZoneInfo(a["fuso"]))
                citta, z = ("London", "Europe/London") if a["fuso"] == "America/New_York" else ("New York", "America/New_York")
                if f"{u.astimezone(ZoneInfo(z)).strftime('%H:%M')} in {citta}" not in vis:
                    errori.append(f"{rel}: manca l'ora della prossima uscita ({r['id']}) a {citta}")
        righe = re.findall(r'<tr data-data="(\d{4}-\d{2}-\d{2})" data-tipo="([a-z]+)">', t)
        if sorted(righe) != sorted((e["data"], e["tipo"]) for e in ev):
            errori.append(f"{rel}: righe della tabella diverse dalle date calcolate")
        for c in a["citazioni"]:
            conti["citazioni"] += 1
            if escape(c["x"], quote=False) not in t and escape(c["x"]) not in t:
                errori.append(f"{rel}: citazione mancante: {c['x'][:60]}")
        for f in G.fonti_big(a):
            F = G.BIG["fonti"][f]
            if f'href="{escape(F["pagina"])}"' not in t or f"checked on {G.data_lunga(F['letto_il'])}" not in vis:
                errori.append(f"{rel}: manca il link o la data della fonte {f}")
        if f"Official tickets for the {a['nome_lungo']} {a['biglietteria'].get('verbo', 'are sold at')}" not in vis or "resellers may charge more" not in vis \
                or f'href="{escape(a["biglietteria"]["url"])}"' not in t:
            errori.append(f"{rel}: manca il riquadro della biglietteria ufficiale con l'avviso sui rivenditori")
        faq_ld = next((x for x in (json.loads(y) for y in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t)) if x.get("@type") == "FAQPage"), None)
        attese_faq = G.faq_big(a)
        if not faq_ld or [(e["name"], e["acceptedAnswer"]["text"]) for e in faq_ld["mainEntity"]] != attese_faq:
            errori.append(f"{rel}: FAQ JSON-LD diversa dalle domande previste")
        for qd, r_ in attese_faq:
            conti["faq"] += 1
            if f"<h3>{escape(qd)}</h3><p>{escape(r_)}</p>" not in t:
                errori.append(f"{rel}: FAQ visibile diversa dal JSON-LD: {qd}")
        # e) .ics: forma, eventi = date calcolate, ora locale = regola
        f_ics = SITO / G.url_ics_big(s)
        if not f_ics.exists():
            errori.append(f"{G.url_ics_big(s)}: file mancante")
            continue
        if f'href="../../{G.url_ics_big(s)}"' not in t or "webcal://" not in t:
            errori.append(f"{rel}: mancano i link al calendario")
        with open(f_ics, encoding="utf-8", newline="") as fh:
            testo_ics = fh.read()
        aperte = _ics_righe(testo_ics, G.url_ics_big(s), errori)
        if aperte[:2] != ["BEGIN:VCALENDAR", "VERSION:2.0"] or aperte[-1] != "END:VCALENDAR" or not any(x.startswith("PRODID:") for x in aperte):
            errori.append(f"{G.url_ics_big(s)}: intestazione o chiusura VCALENDAR non valide")
        eventi, cur = [], None
        for x in aperte:
            if x == "BEGIN:VEVENT":
                cur = {}
            elif x == "END:VEVENT":
                eventi.append(cur)
                cur = None
            elif cur is not None:
                k, _, v = x.partition(":")
                cur[k] = v
        if testo_ics.count("BEGIN:VEVENT") != testo_ics.count("END:VEVENT") or len(eventi) != len(ev):
            errori.append(f"{G.url_ics_big(s)}: {len(eventi)} eventi invece di {len(ev)}")
        uid = [e.get("UID") for e in eventi]
        if len(set(uid)) != len(uid) or not all(uid):
            errori.append(f"{G.url_ics_big(s)}: UID mancanti o duplicati")
        dal_ics = set()
        for e in eventi:
            conti["eventi_ics"] += 1
            if not all(k in e for k in ("DTSTAMP", "SUMMARY", "DESCRIPTION")) or not ("DTSTART" in e or "DTSTART;VALUE=DATE" in e):
                errori.append(f"{G.url_ics_big(s)}: evento senza DTSTAMP, DTSTART, SUMMARY o DESCRIPTION: {e.get('UID')}")
                continue
            if "DTSTART;VALUE=DATE" in e:
                dd = e["DTSTART;VALUE=DATE"]
                dal_ics.add((f"{dd[:4]}-{dd[4:6]}-{dd[6:]}", None))
            else:
                u = datetime.strptime(e["DTSTART"], "%Y%m%dT%H%M%SZ").replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo(a["fuso"]))
                dal_ics.add((u.date().isoformat(), u.strftime("%H:%M")))
        if dal_ics != {(e["data"], e["ora"]) for e in ev}:
            errori.append(f"{G.url_ics_big(s)}: date o ore diverse dalle date calcolate")
        # f) link esterni solo ufficiali; nessun rivenditore nominato
        for h in re.findall(r'href="((?:https?|webcal)://[^"]+)"', t.split('<main id="main">', 1)[-1].split("</main>", 1)[0]):
            conti["link_esterni"] += 1
            if urlparse(unescape(h)).hostname not in ammessi_host:
                errori.append(f"{rel}: link non ufficiale {h[:80]}")
        mm = RIVENDITORI_BIG.search(vis) or VIETATE_SRV.search(vis)
        if mm and not (G.VIATOR_TOUR and mm.group(0).lower() == "viator"):
            errori.append(f"{rel}: nome di rivenditore o assistente '{mm.group(0)}'")
        if "not affiliated with any museum or ticket seller" not in vis:
            errori.append(f"{rel}: manca l'avviso di indipendenza")
    # g) indice
    idx = f"{G.BIG_BASE}/index.html"
    if (SITO / idx).exists():
        t = leggi(idx)
        vis = unescape(re.sub(r"<[^>]+>", " ", t))
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(tit) > G.LIMITE_TITOLO_BIG or G.STAGIONE_BIG not in tit:
            errori.append(f"{idx}: titolo oltre {G.LIMITE_TITOLO_BIG} caratteri o senza gli anni: {tit}")
        m = re.search(r'<p class="lead" id="answer">(.*?)</p>', t)
        if not m or unescape(re.sub(r"<[^>]+>", "", m.group(1))) != G.prima_frase_big() or f"last checked on {G.data_lunga(G.BIG['controllato_il'])}" not in unescape(m.group(1)) \
                or "data-prox=" not in m.group(1) or "data-vecchie=" not in t:
            errori.append(f"{idx}: prima frase diversa dai dati o senza la data")
        righe = re.findall(r'<tr data-voce id="([a-z-]+)">(.*?)</tr>', t)
        if [r[0] for r in righe] != [a["slug"] for a in G.BIG_ATT]:
            errori.append(f"{idx}: righe della tabella diverse dalle attrazioni dei dati")
        for (sl, r), a in zip(righe, G.BIG_ATT):
            e = G.prossimo_big(a, "uscita")
            ogni_giorno = any(x["tipo"] == "anticipo" for x in a["uscite"])
            if (e and G.giorno_lungo(e["data"]) not in unescape(r)) or (not e and ("Every day (rolling)" if ogni_giorno else "No exact date published") not in r):
                errori.append(f"{idx}: riga {sl} con la prossima uscita diversa dal calcolo")
            if f'href="{escape(a["biglietteria"]["url"])}"' not in r:
                errori.append(f"{idx}: riga {sl} senza la biglietteria ufficiale")
        for a in G.BIG_ATT:
            if f'href="../{G.url_ics_big(a["slug"])}"' not in t:
                errori.append(f"{idx}: manca il calendario di {a['slug']}")
        for qd, r_ in G.faq_indice_big():
            conti["faq"] += 1
            if f"<h3>{escape(qd)}</h3><p>{escape(r_)}</p>" not in t:
                errori.append(f"{idx}: FAQ mancante: {qd}")
        for h in re.findall(r'href="((?:https?|webcal)://[^"]+)"', t.split('<main id="main">', 1)[-1].split("</main>", 1)[0]):
            conti["link_esterni"] += 1
            if urlparse(unescape(h)).hostname not in ammessi_host:
                errori.append(f"{idx}: link non ufficiale {h[:80]}")
        mm = RIVENDITORI_BIG.search(vis) or VIETATE_SRV.search(vis)
        if mm and not (G.VIATOR_TOUR and mm.group(0).lower() == "viator"):
            errori.append(f"{idx}: nome di rivenditore o assistente '{mm.group(0)}'")
        for x in G.BIG["escluse"]:
            if escape(x["nome"]) not in t:
                errori.append(f"{idx}: manca l'attrazione esclusa {x['nome']}")
    else:
        errori.append("indice ticket-release-dates mancante")
    # h) Viator: spento = nessun riquadro né link; acceso = solo viator.com, sponsored, trasparenza, dopo la biglietteria ufficiale
    for p in sorted(attese):
        if not (SITO / p).exists():
            continue
        t = leggi(p)
        if not G.VIATOR_TOUR:
            if "data-tour" in t or "viator.com" in t or 'id="guided-tours"' in t:
                errori.append(f"{p}: riquadro Viator presente con VIATOR_TOUR vuoto")
        else:
            errori += [f"{p}: {e}" for e in G.MON.controlla_link_pagina(t, p, "en")[0]]
            if p != idx and t.find("data-tour") < t.find('id="official-tickets"'):
                errori.append(f"{p}: riquadro Viator prima della biglietteria ufficiale")
            # link Viator della pagina: quello dell'attrazione (VIATOR_PER_ATTRAZIONE) o il generale; https, viator.com, stesso pid
            slug_p = p[len(G.BIG_BASE) + 1:-len("/index.html")] if p != idx else None
            atteso = G.VIATOR_PER_ATTRAZIONE.get(slug_p, G.VIATOR_TOUR) if slug_p else G.VIATOR_TOUR
            from html import unescape as _unesc
            trovati = {_unesc(u) for u in re.findall(r'href="([^"]*viator\.com[^"]*)"', t)}
            if trovati != {atteso} or not G.viator_link_valido(atteso):
                errori.append(f"{p}: link Viator {sorted(trovati)} diverso da quello atteso {atteso} o non valido (https, viator.com, pid)")
    for s_ in G.VIATOR_PER_ATTRAZIONE:
        if s_ not in G.BIG_PER:
            errori.append(f"VIATOR_PER_ATTRAZIONE: attrazione sconosciuta {s_}")
    # h2) Stay22 ("Where to stay"): ogni link dei dati SOLO sulla pagina della sua attrazione (e nell'indice, che li ha tutti), con
    # rel="sponsored noopener", target="_blank", riga di trasparenza ed etichetta "Affiliate" nel riquadro, dopo la biglietteria ufficiale
    errori += controlla_stay22_big(attese, idx, conti)
    # i) collegamenti in entrata e dati senza nomi di assistenti
    if f'href="{G.BIG_BASE}/"' not in leggi("index.html"):
        errori.append("home senza link alla sezione 'Ticket release dates'")
    if 'id="ticket-release-dates"' not in leggi("about/index.html"):
        errori.append("About senza la sezione 'Ticket release dates'")
    if 'href="/ticket-release-dates/"' not in leggi("404.html"):
        errori.append("404 senza link alla sezione dei biglietti")
    for nome in ("biglietti.json", "biglietti_manuali.json", "biglietti_domanda.json"):
        if VIETATE_SRV.search((SITO.parent / "dati" / nome).read_text(encoding="utf-8")):
            errori.append(f"dati/{nome}: nome di un assistente di intelligenza artificiale")
    return errori, conti


# ---------------------------------------------------------------- 24. Regole del trasporto pubblico per città (31/10/2026)
_spec_tr = importlib.util.spec_from_file_location("raccolta_trasporti", Path(__file__).resolve().parent / "raccolta" / "trasporti.py")
RTR = importlib.util.module_from_spec(_spec_tr)
_spec_tr.loader.exec_module(RTR)
# Fonti ammesse: aziende di trasporto, autorità e consorzi dei trasporti delle città (niente blog, guide, forum, rivenditori)
FONTI_UFFICIALI_TR = re.compile(r"^https://(?:www\.gvb\.nl|www\.oasa\.gr|www\.tmb\.cat|www\.bvg\.de|www\.stib-mivb\.be|bkk\.hu|www\.transportforireland\.ie|"
                                r"edinburghtrams\.com|www\.tpg\.ch|www\.hvv\.de|www\.metrolisboa\.pt|www\.metromadrid\.es|www\.atm\.it|nuovosistematariffario\.atm\.it|www\.stm\.info|"
                                r"www\.mvg\.de|ruter\.no|www\.dpp\.cz|pid\.cz|www\.ttc\.ca|www\.translink\.ca|www\.zvv\.ch|ztp\.krakow\.pl)/")
# Pagine provate per le città non lette: aziende e autorità dei trasporti delle città
FONTI_NON_LETTE_TR = re.compile(r"^https://(?:www\.gvb\.nl|tfl\.gov\.uk|www\.iledefrance-mobilites\.fr|www\.atac\.roma\.it|www\.wienerlinien\.at|www\.mta\.info|www\.hsl\.fi|"
                                r"sl\.se|www\.wtp\.waw\.pl|www\.opal\.com\.au|www\.gtt\.to\.it|www\.anm\.it|www\.tcl\.fr|www\.rigassatiksme\.lv|ztp\.krakow\.pl|"
                                r"www\.metrovalencia\.es|m\.dk|www\.at-bus\.it|avm\.avmspa\.it|www\.tper\.it|en\.metrodoporto\.pt)/")
# Nessun link di affiliazione nella sezione (nessun link Wise attivo nei dati al 31/10/2026): nemmeno nomi di reti o rivenditori di biglietti
VIETATI_TR = re.compile(r"\bwise\b|prf\.hn|partnerize|trainline|omio|rail ?europe|getyourguide|tiqets|klook|viator|discovercars", re.I)


def controlla_trasporti():
    """Punto 24: fonti = dati = pagine; città non lette senza dati; prima frase; citazioni parola per parola contro la copia della fonte;
    numeri delle frasi nostre solo dalle citazioni; FAQ da ricerche vere (JSON-LD = testo visibile); titoli; sitemap; nessuna affiliazione;
    link in entrata (home, About, 404, Driving abroad, ticket-release-dates)."""
    from html import unescape
    errori = []
    conti = {"citta": 0, "lette": 0, "pagine": 0, "fonti": 0, "citazioni": 0, "faq": 0, "cache": "no", "non_lette": 0, "link": 0}
    if not G.TR:
        return ["dati/trasporti.json mancante (rilanciare raccolta/trasporti.py)"], conti
    M = json.loads((SITO.parent / "dati" / "trasporti_manuali.json").read_text(encoding="utf-8"))
    if M["citta"] != G.TR["citta"] or M.get("faq_indice", []) != G.TR.get("faq_indice", []):
        errori.append("dati/trasporti.json non è aggiornato rispetto a dati/trasporti_manuali.json (rilanciare la raccolta)")
    D = json.loads((SITO.parent / "dati" / "trasporti_domanda.json").read_text(encoding="utf-8"))
    ricerche = RTR.tutte_ricerche(D)
    # a) fonti: HTTP 200, domini ufficiali, data; dalla copia salvata ogni citazione parola per parola e l'impronta della zona citata
    cache = RTR.CACHE.exists()
    for fid, F in G.TR["fonti"].items():
        conti["fonti"] += 1
        if F["http"] != 200:
            errori.append(f"fonte {fid}: HTTP {F['http']}")
        if not FONTI_UFFICIALI_TR.match(F["url"]):
            errori.append(f"fonte {fid}: dominio non ufficiale o non previsto: {F['url']}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", F["letto_il"] or "") or F["letto_il"] > G.OGGI.isoformat():
            errori.append(f"fonte {fid}: data di lettura non valida {F['letto_il']}")
        f_c = RTR.file_cache(fid) if fid in RTR.FONTI else None
        if copia_usabile(24, fid, f_c, "trasporti.py"):
            ef = []
            t = RTR.testo_fonte(f_c.read_bytes(), RTR.FONTI[fid].get("tipo", "html"))
            frasi = RTR.frasi_fonte(G.TR, fid)
            for x in frasi:
                if x not in t:
                    ef.append(f"fonte {fid}: la citazione non è parola per parola nella copia della fonte: {x[:70]}")
            if RTR.impronta_zona(t, frasi) != F["impronta"]:
                ef.append(f"fonte {fid}: impronta diversa dalla copia salvata (rilanciare la raccolta)")
            conti["cache"] = "sì"
            errori += esito_copia(24, fid, ef, f_c, F["letto_il"])
    # b) pagine = città lette + indice
    sm = leggi("sitemap.xml")
    attese = {G.url_tr(c) + "index.html" for c in G.TR_LETTE} | {f"{G.TR_BASE}/index.html"}
    trovate = {q.relative_to(SITO).as_posix() for q in (SITO / G.TR_BASE).rglob("*.html")} if (SITO / G.TR_BASE).exists() else set()
    if attese != trovate:
        errori.append(f"pagine {G.TR_BASE} diverse dai dati: mancano {sorted(attese - trovate)}, in più {sorted(trovate - attese)}")
    tutti_numeri = set().union(*[_numeri_gom(x["x"]) for c in G.TR_LETTE for x in c["citazioni"]])
    for c in G.TR_CITTA:
        conti["citta"] += 1
        # c) città non lette: nessun dato, nessuna pagina, prova registrata su una pagina ufficiale
        if not c["letta"]:
            conti["non_lette"] += 1
            P = (G.TR.get("non_lette") or {}).get(c["id"])
            if c.get("citazioni") or c.get("multa") or (SITO / G.url_tr(c)).exists() or not P:
                errori.append(f"{c['id']}: città non letta con dati, con una pagina propria o senza la prova registrata")
            if not FONTI_NON_LETTE_TR.match(c["url_provato"]):
                errori.append(f"{c['id']}: pagina provata fuori dai domini previsti: {c['url_provato']}")
            # (se la pagina ora risponde 200 con testo lo segnala raccolta/trasporti.py con «ATTENZIONE»: alcuni siti rispondono 403 a intermittenza)
            continue
        conti["lette"] += 1
        # d) numeri delle parole nostre solo dalle citazioni della città (e dal titolo delle sue fonti)
        ammessi = set().union(*[_numeri_gom(x["x"]) for x in c["citazioni"]], *[_numeri_gom(G.TR["fonti"][f]["titolo"]) for f in G.fonti_tr(c)], {str(G.ANNO)})
        nostre = [c.get(k) or "" for k in ("chi", "rete", "multa", "contactless_breve", "convalida_breve", "pagamento", "risposta", "nota")]
        nostre += [(c.get("cambio") or {}).get("testo", "")] + [x.get("tr", "") for x in c["citazioni"]]
        for s in nostre:
            extra = _numeri_gom(s) - ammessi
            if extra:
                errori.append(f"{c['id']}: numeri non presi dalle fonti: {sorted(extra)} in «{s[:60]}»")
        if not any(x["tema"] == "multa" for x in c["citazioni"]):
            errori.append(f"{c['id']}: pagina senza citazione sulla multa")
        if c.get("cambio"):
            x = G.cit_tr(c, c["cambio"]["cit"])
            if x["tema"] not in ("cambio", "multa"):
                errori.append(f"{c['id']}: il cambio annunciato non è legato a una citazione sul cambio o sulla multa")
        for q in c["faq"]:
            extra = _numeri_gom(q["pre"] + " " + q["post"] + " " + q["q"]) - ammessi
            if extra:
                errori.append(f"{c['id']}: numeri non presi dalle fonti nella FAQ «{q['q']}»: {sorted(extra)}")
            if q["query"] not in ricerche:
                errori.append(f"{c['id']}: FAQ «{q['q']}» senza una ricerca vera ({q['query']!r})")
            if any(G.TR["fonti"][G.cit_tr(c, i)["f"]]["lingua"] != "en" for i in q["cit"]) and "our translation" not in q["pre"]:
                errori.append(f"{c['id']}: FAQ «{q['q']}» con citazione tradotta senza dirlo")
        rel = G.url_tr(c) + "index.html"
        if not (SITO / rel).exists():
            continue
        conti["pagine"] += 1
        t = leggi(rel)
        vis = unescape(re.sub(r"<[^>]+>", " ", t))
        if f"<loc>{G.URL_SITO}/{G.url_tr(c)}</loc><lastmod>{G.data_tr(c)}</lastmod>" not in sm:
            errori.append(f"{rel}: non in sitemap o lastmod diverso dalla data di lettura {G.data_tr(c)}")
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(tit) > G.LIMITE_TITOLO_TR or str(G.ANNO) not in tit or c["nome"] not in tit or tit != G.scegli(G.titoli_tr(c), G.LIMITE_TITOLO_TR):
            errori.append(f"{rel}: titolo oltre {G.LIMITE_TITOLO_TR} caratteri, senza l'anno o il nome, o non tra le forme previste: {tit}")
        m = re.search(r'<p class="lead" id="answer">(.*?)</p>', t)
        attesa = f"According to {c['chi']}, checked on {G.data_lunga(G.data_tr(c))}, {c['risposta']}"
        if not m or unescape(m.group(1)) != attesa:
            errori.append(f"{rel}: prima frase diversa da 'According to <fonte>, checked on <data>, <risposta>'")
        t_sic = t.replace(" [sic]", "")  # «[sic]» dopo una parola sbagliata nella fonte (campo 'sic'): la citazione resta parola per parola
        for x in c["citazioni"]:
            conti["citazioni"] += 1
            if escape(x["x"], quote=False) not in t_sic and escape(x["x"]) not in t_sic:
                errori.append(f"{rel}: citazione mancante: {x['x'][:60]}")
            for w in x.get("sic", []):
                if w not in x["x"] or f"{escape(w)} [sic]" not in t:
                    errori.append(f"{rel}: [sic] mancante o parola non nella citazione: {w}")
            if x.get("tr") and escape(x["tr"], quote=False) not in t and escape(x["tr"]) not in t:
                errori.append(f"{rel}: traduzione mancante: {x['tr'][:60]}")
        for f in G.fonti_tr(c):
            F = G.TR["fonti"][f]
            if f'href="{escape(F["url"])}"' not in t or f"checked on {G.data_lunga(F['letto_il'])}" not in vis:
                errori.append(f"{rel}: manca il link o la data della fonte {f}")
        if c.get("nota") and "data-nota" not in t:
            errori.append(f"{rel}: manca la nota di prudenza")
        faq_ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t)]
        faq_ld = next((x for x in faq_ld if x.get("@type") == "FAQPage"), None)
        attese_faq = G.faq_tr(c)
        if not faq_ld or [(e["name"], e["acceptedAnswer"]["text"]) for e in faq_ld["mainEntity"]] != attese_faq:
            errori.append(f"{rel}: FAQ JSON-LD diversa dalle domande previste")
        for qd, a in attese_faq:
            conti["faq"] += 1
            if f"<h3>{escape(qd)}</h3><p>{escape(a)}</p>" not in t:
                errori.append(f"{rel}: FAQ visibile diversa dal JSON-LD: {qd}")
        if G.MON.link_affiliati(t) or 'rel="sponsored' in t:
            errori.append(f"{rel}: link di affiliazione nella sezione (nessun link Wise attivo nei dati)")
        mm = VIETATI_TR.search(vis) or VIETATE_SRV.search(vis) or AGGIRARE.search(vis)
        if mm:
            errori.append(f"{rel}: parola vietata (affiliazione, rivenditore, assistente o aggiramento) '{mm.group(0)}'")
        if "not legal advice" not in vis:
            errori.append(f"{rel}: manca 'not legal advice'")
        if f'href="../../{G.TR_BASE}/"' not in t:
            errori.append(f"{rel}: manca il link all'indice della sezione")
    # e) indice: sitemap, titolo, prima frase, righe = dati, righe "Not read", FAQ
    idx = f"{G.TR_BASE}/index.html"
    if (SITO / idx).exists():
        t = leggi(idx)
        vis = unescape(re.sub(r"<[^>]+>", " ", t))
        if f"<loc>{G.URL_SITO}/{G.TR_BASE}/</loc><lastmod>{G.TR['controllato_il']}</lastmod>" not in sm:
            errori.append(f"indice {G.TR_BASE} non in sitemap o lastmod diverso")
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(tit) > G.LIMITE_TITOLO_TR or str(G.ANNO) not in tit:
            errori.append(f"{idx}: titolo oltre {G.LIMITE_TITOLO_TR} caratteri o senza l'anno: {tit}")
        m = re.search(r'<p class="lead" id="answer">(.*?)</p>', t)
        if not m or unescape(m.group(1)) != G.prima_frase_tr() or f"read on {G.data_lunga(G.TR['controllato_il'])}" not in unescape(m.group(1)):
            errori.append(f"{idx}: prima frase diversa dai conteggi o senza la data")
        righe = re.findall(r'<tr data-voce id="([a-z-]+)">(.*?)</tr>', t)
        if [r[0] for r in righe] != [c["id"] for c in G.TR_CITTA]:
            errori.append(f"{idx}: righe della tabella diverse dalle città dei dati")
        for (cod, r), c in zip(righe, G.TR_CITTA):
            celle = [unescape(re.sub(r"<[^>]+>", "", x)) for x in re.findall(r"<td[^>]*>(.*?)</td>", r)]
            if not c["letta"]:
                resto = re.sub(r"\(checked on \d{1,2} \w+ \d{4}\)", "", celle[1] if len(celle) == 2 else "").replace(c["motivo"], "")
                if len(celle) != 2 or not celle[1].startswith("Not read") or c["motivo"] not in celle[1] or re.search(r"\d", resto):
                    errori.append(f"{idx}: riga {cod} non letta senza 'Not read' e il motivo, o con dati")
                continue
            if celle[1:4] != [c["multa"], G.CONTACTLESS_TR[c["contactless"]], G.CONVALIDA_TR[c["convalida"]]]:
                errori.append(f"{idx}: riga {cod} diversa dai dati: {celle[1:4]}")
            if f'href="../{G.url_tr(c)}"' not in r:
                errori.append(f"{idx}: riga {cod} senza il link alla pagina")
        for f in M.get("faq_indice", []):
            if f["query"] not in ricerche:
                errori.append(f"{idx}: FAQ «{f['q']}» senza una ricerca vera")
        for q, a in G.faq_indice_tr():
            conti["faq"] += 1
            if f"<h3>{escape(q)}</h3><p>{escape(a)}</p>" not in t:
                errori.append(f"{idx}: FAQ mancante: {q}")
            extra = _numeri_gom(a) - tutti_numeri - {str(G.ANNO)}
            if extra:
                errori.append(f"{idx}: numeri non presi dalle fonti nella FAQ «{q}»: {sorted(extra)}")
        if G.MON.link_affiliati(t) or 'rel="sponsored' in t:
            errori.append(f"{idx}: link di affiliazione nella sezione")
        mm = VIETATI_TR.search(vis) or VIETATE_SRV.search(vis) or AGGIRARE.search(vis)
        if mm:
            errori.append(f"{idx}: parola vietata '{mm.group(0)}'")
    else:
        errori.append(f"indice {G.TR_BASE} mancante")
    # f) collegamenti in entrata: home, About, 404, indice Driving abroad, pagine Driving abroad dei Paesi con una città letta (non CA/AU/NZ),
    #    pagine "When do tickets go on sale?" delle attrazioni in una città letta
    if f'href="{G.TR_BASE}/"' not in leggi("index.html"):
        errori.append("home senza link alla sezione del trasporto pubblico")
    if f'id="{G.TR_BASE}"' not in leggi("about/index.html"):
        errori.append("About senza la sezione del trasporto pubblico")
    if f'href="/{G.TR_BASE}/"' not in leggi("404.html"):
        errori.append("404 senza link alla sezione del trasporto pubblico")
    if f'href="../{G.TR_BASE}/"' not in leggi(f"{G.PAT_BASE}/index.html"):
        errori.append(f"{G.PAT_BASE}/index.html: manca il link alla sezione del trasporto pubblico")
    for k in G.PATENTI:
        for iso in G.PAGINE_PAT[k]:
            t = leggi(G.url_pat(k, iso) + "index.html")
            cc = [c for c in G.TR_LETTE if c["iso2"] == iso]
            for c in cc:
                presente = f'href="../../../{G.url_tr(c)}"' in t
                if iso in G.TR_NO_LINK_PAT and presente:
                    errori.append(f"{G.url_pat(k, iso)}: link aggiunto a una pagina Canada/Australia/NZ già revisionata")
                elif iso not in G.TR_NO_LINK_PAT:
                    conti["link"] += 1
                    if not presente:
                        errori.append(f"{G.url_pat(k, iso)}: manca il link a {G.url_tr(c)}")
    for slug, cid in G.TR_BIG.items():
        c = G.TR_PER.get(cid)
        if c and c["letta"] and (SITO / G.url_big(slug)).exists():
            conti["link"] += 1
            if f'href="../../{G.url_tr(c)}"' not in leggi(G.url_big(slug) + "index.html"):
                errori.append(f"{G.url_big(slug)}: manca il link a {G.url_tr(c)}")
    for nome in ("trasporti.json", "trasporti_manuali.json", "trasporti_domanda.json"):
        if VIETATE_SRV.search((SITO.parent / "dati" / nome).read_text(encoding="utf-8")):
            errori.append(f"dati/{nome}: nome di un assistente di intelligenza artificiale")
    return errori, conti


# ---------------------------------------------------------------- 25. Bagagli sui treni per compagnia + orari Eurostar con l'EES (31/10/2026)
_spec_tb = importlib.util.spec_from_file_location("raccolta_treni_bagagli", Path(__file__).resolve().parent / "raccolta" / "treni_bagagli.py")
RTB = importlib.util.module_from_spec(_spec_tb)
_spec_tb.loader.exec_module(RTB)
# Fonti ammesse: siti delle compagnie ferroviarie (e SNCF Connect, il sito di vendita di SNCF); niente blog, guide, rivenditori, depositi bagagli
FONTI_UFFICIALI_TB = re.compile(r"^https://(?:www\.eurostar\.com|help\.eurostar\.com|www\.sncf-connect\.com|www\.ouigo\.com|www\.renfe\.com|"
                                r"www\.trenitalia\.com|www\.italotreno\.com|int\.bahn\.de|www\.oebb\.at|www\.nightjet\.com|www\.nsinternational\.com|"
                                r"www\.tgv-lyria\.com|www\.lumo\.co\.uk|www\.avantiwestcoast\.co\.uk)/")
# Pagine provate per le compagnie non lette
FONTI_NON_LETTE_TB = re.compile(r"^https://(?:iryo\.eu|trenitalia\.fr|www\.sbb\.ch|www\.lner\.co\.uk)/")
# Nessun link di affiliazione nella sezione (nessun programma attivo pertinente): nemmeno nomi di rivenditori di biglietti o servizi bagagli
VIETATI_TB = re.compile(r"\bwise\b|prf\.hn|partnerize|trainline|omio|rail ?europe|getyourguide|tiqets|klook|viator|discovercars|"
                        r"radical ?storage|stasher|luggage ?buddy|sherpr|send ?my ?bag|zyppy|bagaglio facile", re.I)


def controlla_treni_bagagli():
    """Punto 25: fonti = dati = pagine; compagnie non lette senza dati; prima frase; citazioni e righe della tabella Eurostar parola per parola
    contro la copia della fonte; numeri delle frasi nostre solo dalle citazioni; FAQ da ricerche vere (JSON-LD = testo visibile); titoli;
    sitemap; nessuna affiliazione; link in entrata (e nessun link nelle pagine già revisionate)."""
    from html import unescape
    errori = []
    conti = {"compagnie": 0, "lette": 0, "non_lette": 0, "pagine": 0, "fonti": 0, "citazioni": 0, "faq": 0, "stazioni": 0, "cache": "no", "link": 0}
    if not G.TB:
        return ["dati/treni_bagagli.json mancante (rilanciare raccolta/treni_bagagli.py)"], conti
    M = json.loads((SITO.parent / "dati" / "treni_bagagli_manuali.json").read_text(encoding="utf-8"))
    if M["compagnie"] != G.TB["compagnie"] or M.get("faq_indice", []) != G.TB.get("faq_indice", []) or M.get("eurostar") != G.TB.get("eurostar"):
        errori.append("dati/treni_bagagli.json non è aggiornato rispetto a dati/treni_bagagli_manuali.json (rilanciare la raccolta)")
    D = json.loads((SITO.parent / "dati" / "treni_bagagli_domanda.json").read_text(encoding="utf-8"))
    ricerche = RTB.tutte_ricerche(D)
    E = G.TB_EUR
    # a) fonti: HTTP 200, domini ufficiali, data; dalla copia salvata ogni citazione e ogni riga della tabella Eurostar, impronta
    cache = RTB.CACHE.exists()
    for fid, F in G.TB["fonti"].items():
        conti["fonti"] += 1
        if F["http"] != 200:
            errori.append(f"fonte {fid}: HTTP {F['http']}")
        if not FONTI_UFFICIALI_TB.match(F["url"]):
            errori.append(f"fonte {fid}: dominio non ufficiale o non previsto: {F['url']}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", F["letto_il"] or "") or F["letto_il"] > G.OGGI.isoformat():
            errori.append(f"fonte {fid}: data di lettura non valida {F['letto_il']}")
        f_c = RTB.file_cache(fid)
        if copia_usabile(25, fid, f_c, "treni_bagagli.py"):
            ef = []
            t = RTB.testo_fonte(f_c.read_bytes())
            frasi = RTB.frasi_fonte(G.TB, fid)
            for x in frasi:
                if x not in t:
                    ef.append(f"fonte {fid}: testo non parola per parola nella copia della fonte: {x[:70]}")
            if E and fid == E["fonte_tabella"]:
                conti["stazioni"] = sum(1 for s in E["stazioni"] if RTB.riga_stazione(s) in t)
            if RTB.impronta_zona(t, frasi) != F["impronta"]:
                ef.append(f"fonte {fid}: impronta diversa dalla copia salvata (rilanciare la raccolta)")
            conti["cache"] = "sì"
            errori += esito_copia(25, fid, ef, f_c, F["letto_il"])
    # b) pagine = compagnie lette + indice + pagina Eurostar
    sm = leggi("sitemap.xml")
    attese = {G.url_tb(c) + "index.html" for c in G.TB_LETTE} | {f"{G.TB_BASE}/index.html"}
    trovate = {q.relative_to(SITO).as_posix() for q in (SITO / G.TB_BASE).rglob("*.html")} if (SITO / G.TB_BASE).exists() else set()
    if attese != trovate:
        errori.append(f"pagine {G.TB_BASE} diverse dai dati: mancano {sorted(attese - trovate)}, in più {sorted(trovate - attese)}")
    if bool(E) != (SITO / G.TB_ES / "index.html").exists():
        errori.append("pagina Eurostar presente senza dati o dati senza pagina")
    tutti_numeri = set().union(*[_numeri_gom(x["x"]) for c in G.TB_LETTE for x in c["citazioni"]])

    def controlla_pagina(rel, t, cc, faq_attese, prima_attesa, titolo_atteso, lastmod):
        vis = unescape(re.sub(r"<[^>]+>", " ", t))
        if f"<loc>{G.URL_SITO}/{rel[:-len('index.html')]}</loc><lastmod>{lastmod}</lastmod>" not in sm:
            errori.append(f"{rel}: non in sitemap o lastmod diverso dalla data di lettura {lastmod}")
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(tit) > G.LIMITE_TITOLO_TB or str(G.ANNO) not in tit or tit != titolo_atteso:
            errori.append(f"{rel}: titolo oltre {G.LIMITE_TITOLO_TB} caratteri, senza l'anno o non tra le forme previste: {tit}")
        m = re.search(r'<p class="lead" id="answer">(.*?)</p>', t)
        if not m or unescape(m.group(1)) != prima_attesa or not unescape(m.group(1)).startswith("According to ") or ", checked on " not in m.group(1):
            errori.append(f"{rel}: prima frase diversa da 'According to <fonte>, checked on <data>, ...'")
        for x in cc:
            conti["citazioni"] += 1
            if escape(x["x"], quote=False) not in t and escape(x["x"]) not in t:
                errori.append(f"{rel}: citazione mancante: {x['x'][:60]}")
            if x.get("tr") and escape(x["tr"], quote=False) not in t and escape(x["tr"]) not in t:
                errori.append(f"{rel}: traduzione mancante: {x['tr'][:60]}")
        for f in G.fonti_tb(cc):
            F = G.TB["fonti"][f]
            if f'href="{escape(F["url"])}"' not in t or f"checked on {G.data_lunga(F['letto_il'])}" not in vis:
                errori.append(f"{rel}: manca il link o la data della fonte {f}")
        faq_ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t)]
        faq_ld = next((x for x in faq_ld if x.get("@type") == "FAQPage"), None)
        if not faq_ld or [(e["name"], e["acceptedAnswer"]["text"]) for e in faq_ld["mainEntity"]] != faq_attese:
            errori.append(f"{rel}: FAQ JSON-LD diversa dalle domande previste")
        for qd, a in faq_attese:
            conti["faq"] += 1
            if f"<h3>{escape(qd)}</h3><p>{escape(a)}</p>" not in t:
                errori.append(f"{rel}: FAQ visibile diversa dal JSON-LD: {qd}")
        if G.MON.link_affiliati(t) or 'rel="sponsored' in t:
            errori.append(f"{rel}: link di affiliazione nella sezione")
        mm = VIETATI_TB.search(vis) or VIETATE_SRV.search(vis) or AGGIRARE.search(vis)
        if mm:
            errori.append(f"{rel}: parola vietata (affiliazione, rivenditore, servizio bagagli, assistente o aggiramento) '{mm.group(0)}'")
        return vis

    for c in G.TB_COMP:
        conti["compagnie"] += 1
        # c) compagnie non lette: nessun dato, nessuna pagina, prova registrata su una pagina ufficiale
        if not c["letta"]:
            conti["non_lette"] += 1
            P = (G.TB.get("non_lette") or {}).get(c["id"])
            if c.get("citazioni") or c.get("numero") or (SITO / G.url_tb(c)).exists() or not P:
                errori.append(f"{c['id']}: compagnia non letta con dati, con una pagina propria o senza la prova registrata")
            if not FONTI_NON_LETTE_TB.match(c["url_provato"]):
                errori.append(f"{c['id']}: pagina provata fuori dai domini previsti: {c['url_provato']}")
            continue
        conti["lette"] += 1
        # d) numeri delle parole nostre solo dalle citazioni della compagnia (e dal titolo delle sue fonti)
        ammessi = set().union(*[_numeri_gom(x["x"]) for x in c["citazioni"]], *[_numeri_gom(G.TB["fonti"][f]["titolo"]) for f in G.fonti_tb(c["citazioni"])],
                              {str(G.ANNO)})
        nostre = [c.get(k) or "" for k in ("chi", "treni", "numero", "misure", "peso", "extra", "speciali", "risposta", "nota")]
        nostre += [x.get("tr", "") for x in c["citazioni"]]
        for s in nostre:
            extra = _numeri_gom(s) - ammessi
            if extra:
                errori.append(f"{c['id']}: numeri non presi dalle fonti: {sorted(extra)} in «{s[:60]}»")
        ids = {x["id"] for x in c["citazioni"]}
        for q in c["faq"]:
            extra = _numeri_gom(q["pre"] + " " + q["post"] + " " + q["q"]) - ammessi
            if extra:
                errori.append(f"{c['id']}: numeri non presi dalle fonti nella FAQ «{q['q']}»: {sorted(extra)}")
            if q["query"] not in ricerche:
                errori.append(f"{c['id']}: FAQ «{q['q']}» senza una ricerca vera ({q['query']!r})")
            if any(i not in ids for i in q["cit"]):
                errori.append(f"{c['id']}: FAQ «{q['q']}» con una citazione sconosciuta")
            elif any(G.TB["fonti"][G.cit_tb(c["citazioni"], i)["f"]]["lingua"] != "en" for i in q["cit"]) and "our translation" not in q["pre"]:
                errori.append(f"{c['id']}: FAQ «{q['q']}» con citazione tradotta senza dirlo")
        for x in c["citazioni"]:
            if G.TB["fonti"][x["f"]]["lingua"] != "en" and not x.get("tr"):
                errori.append(f"{c['id']}: citazione {x['id']} non in inglese senza traduzione")
        rel = G.url_tb(c) + "index.html"
        if not (SITO / rel).exists():
            continue
        conti["pagine"] += 1
        t = leggi(rel)
        vis = controlla_pagina(rel, t, c["citazioni"], G.faq_tb(c), G.risposta_tb(c), G.scegli(G.titoli_tb(c), G.LIMITE_TITOLO_TB), G.data_tb(c))
        if c.get("nota") and "data-nota" not in t:
            errori.append(f"{rel}: manca la nota")
        for k in ("numero", "misure", "peso", "extra", "speciali"):
            if f"<td>{escape(c[k])}</td>" not in t:
                errori.append(f"{rel}: riga «At a glance» mancante o diversa dai dati ({k})")
        if f'href="../../{G.TB_BASE}/"' not in t:
            errori.append(f"{rel}: manca il link all'indice della sezione")
        if c["id"] == "eurostar" and E and f'href="../../{G.TB_ES}/"' not in t:
            errori.append(f"{rel}: manca il link alla pagina degli orari Eurostar")
    # e) indice: sitemap, titolo, prima frase, righe = dati, righe "Not read", FAQ
    idx = f"{G.TB_BASE}/index.html"
    if (SITO / idx).exists():
        t = leggi(idx)
        vis = unescape(re.sub(r"<[^>]+>", " ", t))
        conti["pagine"] += 1
        if f"<loc>{G.URL_SITO}/{G.TB_BASE}/</loc><lastmod>{G.TB['controllato_il']}</lastmod>" not in sm:
            errori.append(f"indice {G.TB_BASE} non in sitemap o lastmod diverso")
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(tit) > G.LIMITE_TITOLO_TB or str(G.ANNO) not in tit:
            errori.append(f"{idx}: titolo oltre {G.LIMITE_TITOLO_TB} caratteri o senza l'anno: {tit}")
        m = re.search(r'<p class="lead" id="answer">(.*?)</p>', t)
        if not m or unescape(m.group(1)) != G.prima_frase_tb() or f"read on {G.data_lunga(G.TB['controllato_il'])}" not in unescape(m.group(1)):
            errori.append(f"{idx}: prima frase diversa dai conteggi o senza la data")
        righe = re.findall(r'<tr data-voce id="([a-z-]+)">(.*?)</tr>', t)
        if [r[0] for r in righe] != [c["id"] for c in G.TB_COMP]:
            errori.append(f"{idx}: righe della tabella diverse dalle compagnie dei dati")
        for (cod, r), c in zip(righe, G.TB_COMP):
            celle = [unescape(re.sub(r"<[^>]+>", "", x)) for x in re.findall(r"<td[^>]*>(.*?)</td>", r)]
            if not c["letta"]:
                resto = re.sub(r"\(checked on \d{1,2} \w+ \d{4}\)", "", celle[1] if len(celle) == 2 else "").replace(c["motivo"], "")
                if len(celle) != 2 or not celle[1].startswith("Not read") or c["motivo"] not in celle[1] or re.search(r"\d", resto):
                    errori.append(f"{idx}: riga {cod} non letta senza 'Not read' e il motivo, o con dati")
                continue
            if celle[1:4] != [c["numero"], c["misure"], c["extra"]]:
                errori.append(f"{idx}: riga {cod} diversa dai dati: {celle[1:4]}")
            if f'href="../{G.url_tb(c)}"' not in r:
                errori.append(f"{idx}: riga {cod} senza il link alla pagina")
        for f in M.get("faq_indice", []):
            if f["query"] not in ricerche:
                errori.append(f"{idx}: FAQ «{f['q']}» senza una ricerca vera")
        for q, a in G.faq_indice_tb():
            conti["faq"] += 1
            if f"<h3>{escape(q)}</h3><p>{escape(a)}</p>" not in t:
                errori.append(f"{idx}: FAQ mancante: {q}")
            extra = _numeri_gom(a) - tutti_numeri - {str(G.ANNO)}
            if extra:
                errori.append(f"{idx}: numeri non presi dalle fonti nella FAQ «{q}»: {sorted(extra)}")
        if G.MON.link_affiliati(t) or 'rel="sponsored' in t:
            errori.append(f"{idx}: link di affiliazione nella sezione")
        mm = VIETATI_TB.search(vis) or VIETATE_SRV.search(vis) or AGGIRARE.search(vis)
        if mm:
            errori.append(f"{idx}: parola vietata '{mm.group(0)}'")
    else:
        errori.append(f"indice {G.TB_BASE} mancante")
    # f) pagina Eurostar: tabella = dati, numeri delle frasi nostre dalle righe ufficiali e dalle citazioni, FAQ, EES della Commissione
    if E and (SITO / G.TB_ES / "index.html").exists():
        rel = f"{G.TB_ES}/index.html"
        t = leggi(rel)
        conti["pagine"] += 1
        vis = controlla_pagina(rel, t, E["citazioni"], G.faq_es(), G.prima_frase_es(), G.scegli(G.titolo_es(), G.LIMITE_TITOLO_TB), G.data_es())
        righe = re.findall(r'<tr data-voce id="([a-z]+)">(.*?)</tr>', t)
        if [r[0] for r in righe] != [s["id"] for s in E["stazioni"]]:
            errori.append(f"{rel}: righe della tabella diverse dalle stazioni dei dati")
        for (sid, r), s in zip(righe, E["stazioni"]):
            celle = [unescape(re.sub(r"<[^>]+>", "", x)) for x in re.findall(r"<td[^>]*>(.*?)</td>", r)]
            att = [s["nome"]] + [f"{s['arrivo'][k]} min" for k, _ in G.CLASSI_ES] + [
                f"{s['chiusura']['standard']} min (Premier {s['chiusura']['premier']} min; accessible travel {s['chiusura']['accessibile']} min)"]
            if celle != att:
                errori.append(f"{rel}: riga {sid} diversa dai dati: {celle}")
        num_righe = set().union(*[_numeri_gom(RTB.riga_stazione(s)) for s in E["stazioni"]])
        num_ees = set().union(*[_numeri_gom(f["frase"]) for f in G.frasi_ees_es()[0]], set())
        ammessi = num_righe | num_ees | set().union(*[_numeri_gom(x["x"]) for x in E["citazioni"]]) | {str(G.ANNO)}
        for s in [G.prima_frase_es(), E["nota_ees"]] + [a for _, a in G.faq_es()] + [f["q"] for f in E["faq"]]:
            extra = _numeri_gom(s) - ammessi
            if extra:
                errori.append(f"{rel}: numeri non presi dalle fonti: {sorted(extra)} in «{s[:60]}»")
        for f in E["faq"]:
            if f["query"] not in ricerche:
                errori.append(f"{rel}: FAQ «{f['q']}» senza una ricerca vera ({f['query']!r})")
        com, gov = G.frasi_ees_es()
        if not com or any(escape(x["frase"], quote=False) not in t for x in com) or any(escape(x, quote=False) not in t for x in gov):
            errori.append(f"{rel}: manca la frase della Commissione sul pieno funzionamento dell'EES o la frase GOV.UK su St Pancras")
        if "not legal advice" not in vis:
            errori.append(f"{rel}: manca 'not legal advice'")
        if f'href="../{G.url_tb(G.TB_PER["eurostar"])}"' not in t or f'href="../{G.TB_BASE}/"' not in t:
            errori.append(f"{rel}: mancano i link alla pagina bagagli Eurostar o all'indice")
    # g) collegamenti in entrata; nessun link nelle pagine già revisionate (trasporto pubblico, patente straniera)
    entrata = [("index.html", f'href="{G.TB_BASE}/"'), ("index.html", f'href="{G.TB_ES}/"'), ("about/index.html", f'id="{G.TB_BASE}"'),
               ("404.html", f'href="/{G.TB_BASE}/"'), ("404.html", f'href="/{G.TB_ES}/"'), ("ees-etias/index.html", f'href="../{G.TB_ES}/"'),
               (f"{G.BAG_BASE}/index.html", f'href="../{G.TB_BASE}/"')]
    for f, h in entrata:
        conti["link"] += 1
        if h not in leggi(f):
            errori.append(f"{f}: manca il link {h}")
    for base in (G.TR_BASE, G.FL_BASE):
        for q in (SITO / base).rglob("*.html"):
            tq = q.read_text(encoding="utf-8")
            if G.TB_BASE in tq or G.TB_ES in tq:
                errori.append(f"{q.relative_to(SITO)}: link aggiunto a una pagina già revisionata")
    for nome in ("treni_bagagli.json", "treni_bagagli_manuali.json", "treni_bagagli_domanda.json"):
        if VIETATE_SRV.search((SITO.parent / "dati" / nome).read_text(encoding="utf-8")):
            errori.append(f"dati/{nome}: nome di un assistente di intelligenza artificiale")
    return errori, conti


# ---------------------------------------------------------------- 26. Animali: dal Regno Unito all'UE con cane, gatto o furetto (31/10/2026)
_spec_ani = importlib.util.spec_from_file_location("raccolta_animali", Path(__file__).resolve().parent / "raccolta" / "animali.py")
RANI = importlib.util.module_from_spec(_spec_ani)
_spec_ani.loader.exec_module(RANI)
# Fonti ammesse: GOV.UK (APHA, Defra) e Commissione europea (DG SANTE)
FONTI_UFFICIALI_PET = re.compile(r"^https://(?:www\.gov\.uk|food\.ec\.europa\.eu)/")
# Paesi della lista del verme solitario, ricavati qui dalla frase di GOV.UK (elenco), non dalla costante di genera.py
NOMI_ISO_PET = {"Finland": "FI", "Ireland": "IE", "Malta": "MT", "Norway": "NO"}
# Frasi da consiglio veterinario o da vendita: mai nelle frasi nostre della sezione (citazioni escluse)
CONSIGLIO_VET = re.compile(r"\b(?:dose|dosage|mg/kg|we recommend|our advice|you should (?:give|vaccinate|treat|use)|best (?:vaccine|tapeworm|product)|buy)\b", re.I)
# Casi del calcolatore fatti a mano (date contate sul calendario, indipendenti da genera.calcola_pet): ingresso, campi attesi del risultato
CASI_PET = [
    ("esempio GOV.UK: vaccino 1/10, attesa 30 giorni, certificato dal 1/11, ingresso fino al 10/11 compreso",
     {"da": "gb", "specie": "gatto", "dest": "FR", "chip": "2026-10-01", "vaccino": "2026-10-01", "tipo": "primo", "attesa": "30", "arrivo": "2026-11-10"},
     {"esito": "ok", "attesa.pronto": "2026-11-01", "ahc.dal": "2026-11-01", "ahc.al": "2026-11-10"}),
    ("21 giorni pieni: vaccino 1/10, primo giorno 23/10; arrivo il 22/10 troppo presto",
     {"da": "gb", "specie": "cane", "dest": "ES", "chip": "2026-09-30", "vaccino": "2026-10-01", "tipo": "primo", "attesa": "21", "arrivo": "2026-10-22"},
     {"esito": "no", "attesa.pronto": "2026-10-23", "ahc.primo": "2026-10-23", "ahc.ultimo": "2026-11-01"}),
    ("21 giorni pieni: arrivo il 23/10, certificato solo il 23/10",
     {"da": "gb", "specie": "cane", "dest": "ES", "chip": "2026-10-01", "vaccino": "2026-10-01", "arrivo": "2026-10-23"},
     {"esito": "ok", "ahc.dal": "2026-10-23", "ahc.al": "2026-10-23"}),
    ("microchip dopo il vaccino", {"da": "gb", "specie": "cane", "dest": "IT", "chip": "2026-10-02", "vaccino": "2026-10-01", "arrivo": "2026-12-01"},
     {"esito": "no", "chip": "no"}),
    ("12 settimane: nato il 1/7, 12 settimane il 23/9, vaccino il 22/9", {"da": "gb", "specie": "cane", "dest": "IT", "nascita": "2026-07-01", "chip": "2026-09-01",
     "vaccino": "2026-09-22", "arrivo": "2026-12-01"}, {"esito": "no", "eta": "no", "eta.dodici": "2026-09-23"}),
    ("12 settimane: vaccino il 23/9", {"da": "gb", "specie": "cane", "dest": "IT", "nascita": "2026-07-01", "chip": "2026-09-01", "vaccino": "2026-09-23",
     "arrivo": "2026-12-01"}, {"esito": "ok", "eta": "ok"}),
    ("verme solitario per l'Irlanda: arrivo 10/11 alle 13:00, trattamento dal 5/11 13:00 al 9/11 13:00 (esempio GOV.UK: lunedì 13:00 -> da martedì a sabato)",
     {"da": "gb", "specie": "cane", "dest": "IE", "chip": "2026-01-01", "vaccino": "2026-01-01", "arrivo": "2026-11-10", "ora_arrivo": "13:00"},
     {"esito": "ok", "tenia.dal": "2026-11-05T13:00", "tenia.al": "2026-11-09T13:00"}),
    ("gatto in Irlanda: niente verme solitario", {"da": "gb", "specie": "gatto", "dest": "IE", "chip": "2026-01-01", "vaccino": "2026-01-01", "arrivo": "2026-11-10"},
     {"esito": "ok", "tenia": None}),
    ("rientro meno di 6 mesi: ingresso 31/8/2026, ultimo giorno 27/2/2027", {"da": "gb", "specie": "gatto", "dest": "PT", "chip": "2026-01-01", "vaccino": "2026-01-01",
     "arrivo": "2026-08-31", "ritorno": "2027-02-27"}, {"esito": "ok", "ritorno.ultimo": "2027-02-27"}),
    ("rientro il 28/2/2027: troppo tardi", {"da": "gb", "specie": "gatto", "dest": "PT", "chip": "2026-01-01", "vaccino": "2026-01-01", "arrivo": "2026-08-31",
     "ritorno": "2027-02-28"}, {"esito": "no", "ritorno": "no"}),
    ("verme solitario al rientro dalla Francia: rientro 20/11 alle 09:30", {"da": "gb", "specie": "cane", "dest": "FR", "chip": "2026-01-01", "vaccino": "2026-01-01",
     "arrivo": "2026-11-10", "ritorno": "2026-11-20", "ora_ritorno": "09:30"}, {"esito": "ok", "tenia_ritorno.dal": "2026-11-15T09:30", "tenia_ritorno.al": "2026-11-19T09:30"}),
    ("rientro dalla Norvegia: niente verme solitario al rientro", {"da": "gb", "specie": "cane", "dest": "NO", "chip": "2026-01-01", "vaccino": "2026-01-01",
     "arrivo": "2026-11-10", "ritorno": "2026-11-20"}, {"esito": "ok", "tenia_ritorno_no": "info"}),
    ("richiamo senza interruzione: nessuna attesa", {"da": "gb", "specie": "cane", "dest": "DE", "chip": "2025-01-01", "vaccino": "2026-11-01", "tipo": "richiamo",
     "arrivo": "2026-11-01"}, {"esito": "ok", "ahc.dal": "2026-11-01", "ahc.al": "2026-11-01"}),
    ("esame del sangue: prelievo 30 giorni dopo il vaccino, certificato 90 giorni dopo il prelievo", {"da": "non_elenco", "specie": "cane", "dest": "DE",
     "chip": "2026-01-10", "vaccino": "2026-01-10", "prelievo": "2026-02-09", "arrivo": "2026-05-10"}, {"esito": "ok", "sangue.minimo": "2026-02-09",
     "sangue.ahc_dal": "2026-05-10", "ahc.dal": "2026-05-10"}),
    ("esame del sangue troppo presto (29 giorni)", {"da": "non_elenco", "specie": "cane", "dest": "DE", "chip": "2026-01-10", "vaccino": "2026-01-10",
     "prelievo": "2026-02-08", "arrivo": "2026-06-10"}, {"esito": "no", "sangue": "no"}),
    ("attesa sotto i 21 giorni: errore", {"da": "gb", "specie": "cane", "dest": "FR", "chip": "2026-01-01", "vaccino": "2026-01-01", "attesa": "20", "arrivo": "2026-03-01"},
     {"errore": "attesa"}),
    ("data impossibile: errore sul campo", {"da": "gb", "specie": "cane", "dest": "FR", "chip": "2026-02-30", "vaccino": "2026-01-01", "arrivo": "2026-03-01"},
     {"errore": "data", "campo": "chip"}),
    ("arrivo prima del vaccino: errore", {"da": "gb", "specie": "cane", "dest": "FR", "chip": "2026-01-01", "vaccino": "2026-03-01", "arrivo": "2026-02-01"},
     {"errore": "ordine", "campo": "arrivo"}),
]
# Casi provati nel browser (375 e 1280 px): i testi devono contenere le date lunghe attese
CASI_PET_BROWSER = [
    ({"da": "gb", "specie": "gatto", "dest": "FR", "chip": "2026-10-01", "vaccino": "2026-10-01", "attesa": "30", "arrivo": "2026-11-10"},
     ["1 November 2026", "10 November 2026"], "si"),
    ({"da": "gb", "specie": "cane", "dest": "IE", "chip": "2026-01-01", "vaccino": "2026-01-01", "arrivo": "2026-11-10", "ora_arrivo": "13:00", "ritorno": "2026-11-20"},
     ["5 November 2026 at 13:00", "9 November 2026 at 13:00", "No tapeworm treatment is needed to come back"], "si"),
    ({"da": "gb", "specie": "cane", "dest": "ES", "chip": "2026-10-02", "vaccino": "2026-10-01", "arrivo": "2026-10-22"},
     ["vaccinated again", "23 October 2026"], "no"),
]


def _campo_pet(R, chiave):
    if chiave in ("esito", "errore", "campo"):
        return R[chiave]
    pid, _, k = chiave.partition(".")
    x = next((p for p in R["passi"] if p["id"] == pid), None)
    if x is None:
        return None
    return x["esito"] if not k else x["d"].get(k)


def _entrate_casuali_pet(n=3000, seme=11):
    rnd = random.Random(seme)
    paesi = [p["iso2"] for p in G.PET_PAESI]
    base = date(2025, 6, 1)
    out = []
    for _ in range(n):
        g = lambda a, b: (base + timedelta(days=rnd.randint(a, b))).isoformat()
        v = rnd.randint(0, 500)
        I = {"da": rnd.choice(["gb", "gb", "elenco", "non_elenco", "x"]), "specie": rnd.choice(["cane", "gatto", "furetto"]), "dest": rnd.choice(paesi + ["XX"]),
             "chip": g(v - 40, v + 3), "vaccino": (base + timedelta(days=v)).isoformat(), "tipo": rnd.choice(["primo", "primo", "richiamo"]),
             "attesa": rnd.choice(["21", "21", "30", "20", "abc", "", "366"]), "arrivo": g(v - 5, v + 200),
             "ora_arrivo": rnd.choice(["12:00", "00:15", "23:59", "07:05", "25:00", ""]), "nascita": rnd.choice(["", g(v - 120, v - 60)]),
             "prelievo": g(v + 20, v + 60), "ritorno": rnd.choice(["", g(v + 10, v + 400)]), "ora_ritorno": rnd.choice(["12:00", "18:30", ""])}
        if rnd.random() < 0.03:
            I[rnd.choice(["chip", "vaccino", "arrivo", "prelievo"])] = rnd.choice(["2026-02-29", "2026-13-01", "1980-01-01", "x"])
        out.append(I)
    return out


def controlla_js_pet():
    """Motore JS del calcolatore (lo stesso testo della pagina) contro Python: casi a mano + 3.000 casuali."""
    casi = [c[1] for c in CASI_PET] + _entrate_casuali_pet()
    paesi = [p["iso2"] for p in G.PET_PAESI]
    script = (G.PET_MOTORE_JS + "\nvar P=" + json.dumps(paesi) + ";var casi=" + json.dumps(casi) + ";\n"
              "console.log(JSON.stringify(casi.map(function(c){return calcolaPet(c,P);})));")
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(script)
    try:
        r = subprocess.run(["node", fh.name], capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        return ["node non trovato: confronto JS del calcolatore animali saltato"], 0
    finally:
        os.unlink(fh.name)
    if r.returncode != 0:
        return ["Errore JS calcolatore animali: " + r.stderr[:500]], 0
    errori = []
    for c, js in zip(casi, json.loads(r.stdout)):
        py = G.calcola_pet(c)
        if json.dumps(py, sort_keys=True) != json.dumps(js, sort_keys=True):
            errori.append(f"calcolatore animali: JS diverso dal Python per {c}: py {py} js {js}")
    return errori[:20], len(casi)


BROWSER_PET_JS = r"""
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const http = require('http'); const fs = require('fs'); const path = require('path');
const ROOT = process.argv[2], PAGINE = JSON.parse(process.argv[3]), CASI = JSON.parse(process.argv[4]), CARTELLA = process.argv[5];
const srv = http.createServer((req, res) => { let p = decodeURIComponent(req.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html';
  const f = path.join(ROOT, p); if (!f.startsWith(ROOT) || !fs.existsSync(f)) { res.writeHead(404); res.end('404'); return; }
  res.writeHead(200, {'Content-Type': p.endsWith('.html') ? 'text/html; charset=utf-8' : 'application/octet-stream'}); res.end(fs.readFileSync(f)); });
srv.listen(0, async () => {
  const base = 'http://127.0.0.1:' + srv.address().port; const out = {pagine: [], casi: []};
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  for (const [larghezza, tema] of [[375, 'light'], [375, 'dark'], [1280, 'light']]) {
    const ctx = await b.newContext({ viewport: { width: larghezza, height: 900 }, colorScheme: tema });
    for (const u of PAGINE) {
      const p = await ctx.newPage(); const err = [];
      p.on('console', m => { if (m.type() === 'error' && !m.text().startsWith('[Report Only]')) err.push(m.text()); }); p.on('pageerror', e => err.push(String(e)));
      await p.goto(base + u, { waitUntil: 'load' });
      const w = await p.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
      const risp = await p.$eval('#answer', e => { const r = e.getBoundingClientRect(); return r.height > 0 && r.width <= window.innerWidth; }).catch(() => false);
      const cit = await p.$$eval('blockquote.cit', e => e.filter(x => x.getBoundingClientRect().height > 0).length);
      out.pagine.push({ url: u, larghezza: larghezza, tema: tema, scroll: w[0], vista: w[1], errori: err, risposta: risp, citazioni: cit });
      if (tema === 'light') await p.screenshot({ path: CARTELLA + '/' + (u.split('/').filter(Boolean).join('-') || 'home') + '-' + larghezza + '.png', fullPage: false });
      if (u.indexOf('date-calculator') >= 0) {
        for (let i = 0; i < CASI.length; i++) { const c = CASI[i][0];
          await p.goto(base + u, { waitUntil: 'load' });
          for (const k of ['da', 'specie', 'dest', 'tipo']) if (c[k]) await p.selectOption('[name=' + k + ']', c[k]);
          for (const k of ['chip', 'vaccino', 'attesa', 'nascita', 'prelievo', 'arrivo', 'ora_arrivo', 'ritorno', 'ora_ritorno']) if (c[k] !== undefined) await p.fill('[name=' + k + ']', c[k]);
          const r = await p.evaluate(() => ({ testo: document.querySelector('[data-out]').textContent, si: !!document.querySelector('[data-out] .esito.si'), no: !!document.querySelector('[data-out] .esito.no') }));
          const w2 = await p.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
          out.casi.push({ caso: i, larghezza: larghezza, tema: tema, testo: r.testo, si: r.si, no: r.no, scroll: w2[0], vista: w2[1] });
          if (i === 1 && tema === 'light') await p.screenshot({ path: CARTELLA + '/calcolatore-irlanda-' + larghezza + '.png', fullPage: true }); }
        await p.goto(base + u + '?dest=MT', { waitUntil: 'load' });
        out.dest = await p.$eval('[name=dest]', e => e.value);
      }
      await p.close(); }
    await ctx.close(); }
  await b.close(); srv.close(); console.log(JSON.stringify(out)); });
"""


def controlla_browser_pet(pagine):
    if os.environ.get("BYF_NO_BROWSER") == "1":
        return [], "saltato (BYF_NO_BROWSER=1)"
    cartella = tempfile.mkdtemp(prefix="pets-")
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(BROWSER_PET_JS)
    try:
        r = subprocess.run(["node", fh.name, str(SITO), json.dumps(pagine), json.dumps(CASI_PET_BROWSER), cartella], capture_output=True, text=True, timeout=600)
    except FileNotFoundError:
        return ["node non trovato: prova nel browser della sezione animali saltata"], "no"
    finally:
        os.unlink(fh.name)
    if r.returncode != 0:
        return ["Errore Playwright (animali): " + r.stderr[:800]], "no"
    o = json.loads(r.stdout)
    errori = []
    for x in o["pagine"]:
        if x["scroll"] > x["vista"]:
            errori.append(f"{x['url']} ({x['larghezza']} px, {x['tema']}): scorrimento orizzontale {x['scroll']} > {x['vista']}")
        if x["errori"]:
            errori.append(f"{x['url']} ({x['larghezza']} px, {x['tema']}): errori in console {x['errori'][:2]}")
        if not x["risposta"] or x["citazioni"] < 1:
            errori.append(f"{x['url']} ({x['larghezza']} px, {x['tema']}): risposta in alto o citazioni non visibili")
    for x in o["casi"]:
        atteso, colore = CASI_PET_BROWSER[x["caso"]][1], CASI_PET_BROWSER[x["caso"]][2]
        if any(a not in x["testo"] for a in atteso) or not x[colore]:
            errori.append(f"calcolatore nel browser ({x['larghezza']} px, {x['tema']}), caso {x['caso']}: atteso {atteso} ({colore}), letto {x['testo'][:300]}")
        if x["scroll"] > x["vista"]:
            errori.append(f"calcolatore ({x['larghezza']} px): scorrimento orizzontale con il risultato")
    if len(o["casi"]) != 3 * len(CASI_PET_BROWSER):
        errori.append(f"calcolatore: provati {len(o['casi'])} casi nel browser invece di {3 * len(CASI_PET_BROWSER)}")
    if o.get("dest") != "MT":
        errori.append("calcolatore: ?dest=MT non preseleziona Malta")
    return errori, f"{len(o['pagine'])} viste (375 px chiaro/scuro e 1280 px), {len(o['casi'])} prove del calcolatore, schermate in {cartella}"


def controlla_animali():
    """Punto 26: fonti e citazioni, tabelle e link ricalcolati dalla copia salvata, pagine = dati, prima frase, numeri, FAQ, nessun consiglio
    veterinario né affiliazione, calcolatore (casi a mano, JS = Python, browser a 375 e 1280 px), collegamenti, data del 2027."""
    from html import unescape
    errori = []
    conti = {"fonti": 0, "cache": "no", "pagine": 0, "paesi": 0, "citazioni": 0, "faq": 0, "righe_rotte": 0, "casi": 0, "js": 0, "browser": "", "link": 0}
    if not G.PET:
        return ["dati/animali.json mancante (rilanciare raccolta/animali.py)"], conti
    M = json.loads((SITO.parent / "dati" / "animali_manuali.json").read_text(encoding="utf-8"))
    if M["citazioni"] != G.PET["citazioni"] or M["faq"] != G.PET["faq"]:
        errori.append("dati/animali.json non è aggiornato rispetto a dati/animali_manuali.json (rilanciare raccolta/animali.py)")
    ricerche = set()
    D = json.loads((SITO.parent / "dati" / "animali_domanda.json").read_text(encoding="utf-8"))
    for d in list(D["paesi"].values()) + [D["generali"]]:
        for ss in d.values():
            ricerche.update(ss)
    # a) fonti: HTTP 200, domini ufficiali, data; dalla copia salvata: frasi, impronte, tabelle e link per Paese ricalcolati
    cache = RANI.CACHE.exists()
    for fid, F in G.PET["fonti"].items():
        conti["fonti"] += 1
        if F["http"] != 200:
            errori.append(f"fonte {fid}: HTTP {F['http']}")
        if not FONTI_UFFICIALI_PET.match(F["url"]) or not FONTI_UFFICIALI_PET.match(F["pagina"]):
            errori.append(f"fonte {fid}: dominio non ufficiale {F['url']}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", F["letto_il"] or "") or F["letto_il"] > G.OGGI.isoformat():
            errori.append(f"fonte {fid}: data di lettura non valida {F['letto_il']}")
        tipo = RANI.FONTI[fid].get("tipo", "html")
        f_c = RANI.CACHE / f"{fid}.{'json' if tipo == 'govuk' else 'html'}"
        if copia_usabile(26, fid, f_c, "animali.py"):
            ef = []
            raw = f_c.read_text(encoding="utf-8")
            t = RANI.testo_fonte(raw, tipo)
            frasi = [c["x"] for c in G.PET["citazioni"] if c["f"] == fid]
            for x in frasi:
                if x not in t:
                    ef.append(f"fonte {fid}: frase non più nel testo salvato: {x[:70]}")
            if frasi and RANI.impronta_zona(t, frasi) != F["impronta"]:
                ef.append(f"fonte {fid}: impronta diversa dal testo salvato (rilanciare raccolta/animali.py)")
            if fid == "gov_aria":
                ta = RANI.tabelle_aria(raw)
                if [r for r in ta if r["tipo"] == "commerciale"] != G.PET["rotte"]["aria"] or sum(1 for r in ta if r["tipo"] == "charter") != G.PET["rotte"]["charter"]:
                    ef.append("tabella delle compagnie aeree (o numero dei charter) diversa dalla copia salvata di GOV.UK")
            if fid == "gov_mare":
                m = RANI.tabelle_mare(raw)
                if any(m[k] != G.PET["rotte"][k] for k in ("mare", "crociera", "treno")):
                    ef.append("tabelle di traghetti, crociere e treni diverse dalla copia salvata di GOV.UK")
            if fid == "ue_ingresso":
                L = RANI.link_ue(raw)
                for p in G.PET_PAESI:
                    if L.get(p["nome_ue"]) != p["ingresso"]:
                        ef.append(f"{p['iso2']}: link della Commissione ai punti di ingresso diverso dalla copia salvata")
            conti["cache"] = "sì"
            errori += esito_copia(26, fid, ef, f_c, F["letto_il"])
    for c in G.PET["citazioni"]:
        if c.get("elenco") and " ".join(c["elenco"]) != c["x"]:
            errori.append(f"citazione {c['id']}: le voci dell'elenco non ricompongono la frase")
    tenia_fonte = {NOMI_ISO_PET[x] for x in G.PET_CIT["e_tenia"]["elenco"][1:] if x in NOMI_ISO_PET}
    if tenia_fonte != set(G.TENIA_PET):
        errori.append(f"lista del verme solitario diversa dalla frase di GOV.UK: {sorted(tenia_fonte)} contro {G.TENIA_PET}")
    # b) pagine = dati, sitemap, titoli
    sm = leggi("sitemap.xml")
    attese = {G.PET_BASE + "/", G.PET_CALC, G.PET_PASS, G.PET_ROTTE} | {G.url_pet(p) for p in G.PET_PAGINE}
    trovate = {q.parent.relative_to(SITO).as_posix() + "/" for q in (SITO / G.PET_BASE).rglob("index.html")} if (SITO / G.PET_BASE).exists() else set()
    if attese != trovate:
        errori.append(f"pagine della sezione pets diverse dai dati: in più {sorted(trovate - attese)}, mancanti {sorted(attese - trovate)}")
    for p in G.PET_PAESI:
        r = G.ricerca_paese_pet(p)
        if (r is not None) != (p in G.PET_PAGINE) or (r and r not in ricerche) or (r and G.query_pet(p) not in r):
            errori.append(f"{p['iso2']}: pagina Paese senza una ricerca vera che nomina il Paese e il Regno Unito (o ricerca senza pagina)")
    citazioni_x = {c["x"] for c in G.PET["citazioni"] if not c.get("elenco")} | {c["elenco"][0] for c in G.PET["citazioni"] if c.get("elenco")}
    voci_elenco = {v for c in G.PET["citazioni"] if c.get("elenco") for v in c["elenco"][1:]}
    numeri_cit = set().union(*[_numeri_ped(c["x"]) for c in G.PET["citazioni"]])
    ref_home = leggi("index.html")
    for rel in sorted(attese):
        f = SITO / rel / "index.html"
        if not f.exists():
            continue
        conti["pagine"] += 1
        t = f.read_text(encoding="utf-8")
        vis = unescape(re.sub(r"<[^>]+>", " ", t))
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(tit) > G.LIMITE_TITOLO_PET or str(G.ANNO) not in tit:
            errori.append(f"{rel}: titolo oltre {G.LIMITE_TITOLO_PET} caratteri o senza l'anno: {tit}")
        lm = re.search(re.escape(f"<loc>{G.URL_SITO}/{rel}</loc><lastmod>") + r"(\d{4}-\d{2}-\d{2})</lastmod>", sm)
        if not lm or lm.group(1) not in {F["letto_il"] for F in G.PET["fonti"].values()}:
            errori.append(f"{rel}: non in sitemap o lastmod diverso da una data di lettura delle fonti")
        m = re.search(r'<p class="lead" id="answer">(.*?)</p>', t, re.S)
        lead = unescape(re.sub(r"<[^>]+>", "", m.group(1))) if m else ""
        if not re.match(r"According to (?:GOV\.UK|GOV\.UK and the European Commission)\b[^,]*, (?:in lists updated on \d{1,2} \w+ \d{4} and )?checked on \d{1,2} \w+ \d{4}, ", lead):
            errori.append(f"{rel}: la prima frase non dice fonte e data ('According to GOV.UK ..., checked on <data>, ...'): {lead[:120]}")
        # citazioni: ogni paragrafo e voce dei riquadri è una frase ufficiale; link e data della fonte
        for bq in re.findall(r'(?s)<blockquote class="cit">(.*?)</blockquote>', t):
            for x in re.findall(r"(?s)<p>(.*?)</p>", bq):
                conti["citazioni"] += 1
                if unescape(x) not in citazioni_x:
                    errori.append(f"{rel}: testo tra virgolette che non è una citazione dei dati: {unescape(x)[:70]}")
            for x in re.findall(r"(?s)<li>(.*?)</li>", bq):
                if unescape(x) not in voci_elenco:
                    errori.append(f"{rel}: voce di elenco citata che non è nei dati: {unescape(x)[:70]}")
        for fid, F in G.PET["fonti"].items():
            if f'href="{escape(F["pagina"])}"' in t and f"checked on {G.data_lunga(F['letto_il'])}" not in vis:
                errori.append(f"{rel}: fonte {fid} linkata senza la data del controllo")
        # frasi nostre: niente numeri che non siano nelle citazioni (salvo date, anno e conteggi delle tabelle), niente consigli veterinari
        t_main = t[t.find("<main"):t.find("</main>")]
        nostre = unescape(re.sub(r"<[^>]+>", " ", re.sub(r'(?s)<blockquote class="cit">.*?</blockquote>|<script.*?</script>|<div class="tab tab-b">.*?</table></div>|<footer.*?</footer>|'
                                                      r'<div class="card checker".*?</noscript></div>', " ", t_main)))
        nostre = re.sub(r"\b(?:Regulation|Implementing Regulation|Delegated Regulation) \(EU\)(?: No)? \d+/\d+", " ", nostre)
        extra_ok = {str(G.ANNO), "2027", "3.0", "1", "2", "3", "4", "5", "6"} | ({str(len(G.PET["rotte"][k])) for k in ("mare", "treno", "crociera")} |
                                                                                 {str(len(G.PET["rotte"]["aria"])), str(G.PET["rotte"]["charter"])}
                                                                                 if rel == G.PET_ROTTE else set())
        extra_ok |= {str(len(G.rotte_ritorno_pet(p))) for p in G.PET_PAGINE if G.url_pet(p) == rel}  # "N by sea or rail" (righe della tabella GOV.UK)
        if rel == G.PET_CALC:
            extra_ok |= {"22", "9", "84"}  # "How we count": 21 + 1, 10 - 1, 12 settimane = 84 giorni (spiegati nella pagina)
        extra = _numeri_ped(nostre) - numeri_cit - extra_ok
        if extra:
            errori.append(f"{rel}: numeri nelle frasi nostre che non sono nelle citazioni: {sorted(extra)[:8]}")
        mm = CONSIGLIO_VET.search(nostre)
        if mm:
            errori.append(f"{rel}: frase da consiglio veterinario o da vendita: '{mm.group(0)}'")
        if "Check with your vet and the official page" not in vis:
            errori.append(f"{rel}: manca 'Check with your vet and the official page'")
        if G.MON.link_affiliati(t) or 'rel="sponsored' in t:
            errori.append(f"{rel}: link di affiliazione nella sezione pets (nessun programma pertinente attivo)")
        mm = VIETATE_SRV.search(vis)
        if mm:
            errori.append(f"{rel}: nome vietato '{mm.group(0)}'")
        # FAQ: ricerche vere, JSON-LD = testo visibile
        faq_ld = next((x for x in (json.loads(y) for y in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t)) if x.get("@type") == "FAQPage"), None)
        vis_faq = re.findall(r"(?s)<section class=\"faq\">.*?</section>", t)
        if not faq_ld or not vis_faq:
            errori.append(f"{rel}: FAQ mancanti")
        else:
            for e in faq_ld["mainEntity"]:
                conti["faq"] += 1
                if f"<h3>{escape(e['name'])}</h3><p>{escape(e['acceptedAnswer']['text'])}</p>" not in vis_faq[0]:
                    errori.append(f"{rel}: FAQ visibile diversa dal JSON-LD: {e['name']}")
        if f'href="{rel}"' not in ref_home and rel != G.PET_BASE + "/" and not any(p for p in G.PET_PAGINE if G.url_pet(p) == rel):
            errori.append(f"home senza link a {rel}")
    for chiave in ("indice", "calcolatore", "passaporto", "rotte"):
        for q in G.PET["faq"][chiave]:
            if q["query"] not in ricerche:
                errori.append(f"FAQ «{q['q']}» senza una ricerca vera ({q['query']!r})")
            extra = _numeri_ped(q["pre"] + " " + q["post"]) - numeri_cit
            if extra:
                errori.append(f"FAQ «{q['q']}»: numeri non presi dalle citazioni {sorted(extra)}")
    # c) pagine Paese: verme solitario, link della Commissione, rotte di ritorno, FAQ da ricerche vere, collegamenti con le sezioni sulla guida
    hub = leggi(f"{G.PET_BASE}/index.html")
    for p in G.PET_PAGINE:
        c, rel = p["iso2"], G.url_pet(p)
        conti["paesi"] += 1
        t = leggi(rel + "index.html")
        vis = unescape(re.sub(r"<[^>]+>", " ", t))
        cella = re.search(r'Tapeworm to enter \(dogs\)</th><td>(.*?)</td>', t)
        if not cella or cella.group(1).startswith("Yes") != (c in tenia_fonte):
            errori.append(f"{rel}: riga 'Tapeworm to enter' diversa dalla lista di GOV.UK")
        if (c in tenia_fonte) != ("is on GOV.UK's tapeworm list" in vis):
            errori.append(f"{rel}: prima frase sul verme solitario diversa dalla lista di GOV.UK")
        for u in p["ingresso"] + p["info"]:
            if f'href="{escape(u)}"' not in t:
                errori.append(f"{rel}: manca il link della Commissione {u[:60]}")
        rotte = G.rotte_ritorno_pet(p)
        if c != "IE":
            for r in rotte:
                conti["righe_rotte"] += 1
                if f'<td data-l="Route">{escape(r["rotta"])}</td><td data-l="Company">{escape(r["compagnia"])}</td>' not in t:
                    errori.append(f"{rel}: rotta di ritorno mancante {r['rotta']}")
        elif "You do not need to use an approved route if you’re travelling within the UK or from Ireland." not in unescape(t):
            errori.append(f"{rel}: manca la frase di GOV.UK sulle rotte dall'Irlanda")
        for q in G.faq_paese_pet(p):
            if q["query"] not in ricerche or G.query_pet(p) not in q["query"]:
                errori.append(f"{rel}: FAQ «{q['q']}» senza una ricerca vera sul Paese ({q['query']!r})")
            extra = _numeri_ped(q["pre"] + " " + q["post"]) - numeri_cit
            if extra:
                errori.append(f"{rel}: numeri non presi dalle citazioni nella FAQ «{q['q']}»: {sorted(extra)}")
        if f'href="../{G.url_pet(p)[len(G.PET_BASE) + 1:]}"' not in hub and f'href="../{rel}"' not in hub:
            errori.append(f"indice pets senza link a {rel}")
        if f'href="../../{G.PET_CALC}?dest={c}"' not in t:
            errori.append(f"{rel}: manca il link al calcolatore con il Paese scelto")
        if G.PAT and c in G.PAGINE_PAT.get("uk", []):
            conti["link"] += 1
            if f'href="../../{G.url_pat("uk", c)}"' not in t or f'href="../../../{rel}"' not in leggi(G.url_pat("uk", c) + "index.html"):
                errori.append(f"{rel}: manca il link andata e ritorno con {G.url_pat('uk', c)}")
        if G.PED and c in G.PED_PER:
            conti["link"] += 1
            if f'href="../../{G.url_ped(c)}"' not in t or f'href="../../{rel}"' not in leggi(G.url_ped(c) + "index.html"):
                errori.append(f"{rel}: manca il link andata e ritorno con {G.url_ped(c)}")
    # d) rotte: tabelle della pagina = dati
    tr = leggi(G.PET_ROTTE + "index.html")
    n_righe = len(re.findall(r"<tr data-voce>", tr))
    attese_righe = sum(len(G.PET["rotte"][k]) for k in ("aria", "mare", "crociera", "treno"))
    conti["righe_rotte"] += n_righe
    if n_righe != attese_righe:
        errori.append(f"{G.PET_ROTTE}: {n_righe} righe nelle tabelle invece di {attese_righe}")
    # gli operatori charter (571 righe, voli privati) non si copiano: alcuni nomi coincidono con nomi di assistenti di IA; link alla sezione di GOV.UK
    if "#charter-airlines" not in tr:
        errori.append(f"{G.PET_ROTTE}: manca il link alla sezione 'Charter airlines' di GOV.UK")
    # e) passaporto 2027: la pagina segue la data di GOV.UK
    tp = unescape(leggi(G.PET_PASS + "index.html"))
    if "It is our intention that the agreement will take effect in mid-2027." not in tp:
        errori.append(f"{G.PET_PASS}: manca la frase di GOV.UK sulla data (mid-2027)")
    if G.OGGI.isoformat() >= "2027-06-01":
        errori.append(f"{G.PET_PASS}: è già metà 2027: rileggere GOV.UK e riscrivere la pagina del passaporto (e il riquadro 'Changes expected in 2027')")
    # f) calcolatore: casi a mano, esempio GOV.UK nella pagina, JS = Python, browser
    for nome, I, atteso in CASI_PET:
        conti["casi"] += 1
        R = G.calcola_pet(I)
        diversi = {k: (_campo_pet(R, k), v) for k, v in atteso.items() if _campo_pet(R, k) != v}
        if diversi:
            errori.append(f"calcolatore, caso «{nome}»: {diversi}")
    tc = unescape(leggi(G.PET_CALC + "index.html"))
    if "between 1 November 2026 and 10 November 2026" not in tc or "up to and including 10 November" not in tc:
        errori.append(f"{G.PET_CALC}: l'esempio di GOV.UK non dà le stesse date nel calcolatore")
    e_js, n_js = controlla_js_pet()
    errori += e_js
    conti["js"] = n_js
    e_b, conti["browser"] = controlla_browser_pet(["/" + x for x in [G.PET_BASE + "/", G.PET_CALC, G.PET_PASS, G.PET_ROTTE] + [G.url_pet(p) for p in G.PET_PAGINE[:4]]])
    errori += e_b
    # g) collegamenti in entrata e dati senza nomi di assistenti
    if f'href="{G.PET_BASE}/"' not in ref_home:
        errori.append("home senza link alla sezione pets")
    if f'id="{G.PET_BASE}"' not in leggi("about/index.html"):
        errori.append("About senza la sezione pets")
    for nome in ("animali.json", "animali_manuali.json", "animali_domanda.json"):
        if VIETATE_SRV.search((SITO.parent / "dati" / nome).read_text(encoding="utf-8")):
            errori.append(f"dati/{nome}: nome di un assistente di intelligenza artificiale")
    return errori, conti


# ---------------------------------------------------------------- 27. e-Visa per l'India: costo per nazionalità, visto all'arrivo, e-Arrival card (31/10/2026)
_spec_in = importlib.util.spec_from_file_location("raccolta_india_evisa", Path(__file__).resolve().parent / "raccolta" / "india_evisa.py")
RIN = importlib.util.module_from_spec(_spec_in)
_spec_in.loader.exec_module(RIN)
# Fonti ammesse: portale ufficiale del governo indiano per i visti e Bureau of Immigration
FONTI_UFFICIALI_IN = re.compile(r"^https://(?:indianvisaonline\.gov\.in|boi\.gov\.in)/")
# Link esterni ammessi nelle pagine della sezione (oltre ai link interni): solo siti ufficiali e, sponsorizzato, SafetyWing
LINK_AMMESSI_IN = re.compile(r"^https://(?:indianvisaonline\.gov\.in/|boi\.gov\.in/|airsuvidha\.civilaviation\.gov\.in/|before-you-fly\.netlify\.app/"
                             r"|safetywing\.com/nomad-insurance\?referenceID=26614957&(?:amp;)?campaign=india-e-visa&)")
# Rivenditori e "servizi visto": mai nominati né linkati nella sezione
RIVENDITORI_IN = re.compile(r"ivisa|visahq|travisa|cibt|visacentral|atlys|visa ?guide\.world|india-?visa-?online(?!\.gov)|indian-?visa-?online(?!\.gov)"
                            r"|evisa-?india|e-?visa-?india\.|india-?evisa\.|visa-?india\.|indiavisa\.|onlinevisa|visasnews|holidify|immihelp|sbnri"
                            r"|visafeecalculator|calendar-uk|discovercars|stay22|booking\.com|viator", re.I)
COLONNE_PDF_IN = {"fee_tv": 4, "fee_altri": 3}


def righe_pdf_indipendenti(f, k):
    """Seconda lettura del PDF, indipendente da raccolta/india_evisa.py: pdfplumber (pdfminer) se c'è, altrimenti pdftotext -raw.
    Righe "N Nome v1 v2 ..." con i nomi su due righe ricomposti; restituisce ([(n, nome, [grezzi])], metodo)."""
    try:
        import pdfplumber
        with pdfplumber.open(str(f)) as pdf:
            testo = "\n".join(pg.extract_text() or "" for pg in pdf.pages)
        metodo = "pdfplumber"
    except ImportError:
        testo = subprocess.run(["pdftotext", "-raw", str(f), "-"], capture_output=True, text=True, check=True).stdout
        metodo = "pdftotext -raw"
    rx = re.compile(r"^(\d{1,3}) (.+?) ((?:\d+|-)(?: (?:\d+|-)){%d})$" % (k - 1))
    righe, prec = [], None
    for linea in testo.splitlines():
        linea = re.sub(r"\s+", " ", linea).strip()
        m = rx.match(linea)
        if m:
            righe.append([int(m.group(1)), m.group(2), m.group(3).split()])
            prec = righe[-1]
        elif prec is not None and re.fullmatch(r"[A-Za-z][A-Za-z .'&()-]*", linea) and not linea.startswith("Note"):
            prec[1] += " " + linea
            prec = None
        else:
            prec = None
    return righe, metodo


def _vis_in(t):
    from html import unescape
    return unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?s)<style>.*?</style>|<script.*?</script>", " ", t)))


def _numeri_in(s):
    return set(re.findall(r"\d+(?:[.,]\d+)?", s))


def controlla_india():
    """Punto 27: PDF salvati = dati (seconda lettura indipendente: numero di Paesi e ogni valore), fonti ufficiali, citazioni parola per parola,
    pagine = dati (nazionalità solo con ricerche vere), tabelle nelle pagine = PDF, prima frase con fonte e data, avviso sul sito ufficiale,
    nessun rivenditore di visti, solo link ufficiali o SafetyWing sponsorizzato, FAQ da ricerche vere (JSON-LD = testo visibile), titoli,
    sitemap, pagine in tedesco e francese, collegamenti in entrata; browser a 375 e 1280 px con il filtro della tabella."""
    from html import unescape
    errori = []
    conti = {"fonti": 0, "paesi": 0, "righe_tv": 0, "righe_altri": 0, "valori": 0, "metodo": "-", "pagine": 0, "citazioni": 0, "faq": 0,
             "link": 0, "browser": "-", "nazionalita": 0}
    I = G.IN
    if not I:
        return ["dati/india_evisa.json mancante (rilanciare raccolta/india_evisa.py)"], conti
    M = json.loads((SITO.parent / "dati" / "india_evisa_manuali.json").read_text(encoding="utf-8"))
    D = json.loads((SITO.parent / "dati" / "india_evisa_domanda.json").read_text(encoding="utf-8"))
    if M["citazioni"] != I["citazioni"] or M["faq"] != I["faq"] or M["porti"] != I["porti"] or M["pagine_lingua"] != I["pagine_lingua"]:
        errori.append("dati/india_evisa.json non è aggiornato rispetto a dati/india_evisa_manuali.json (rilanciare la raccolta)")
    ricerche = RIN.tutte_ricerche(D)
    # a) fonti: dominio ufficiale, HTTP 200, date; PDF salvati con la stessa impronta; citazioni nel testo salvato; elenchi dei porti
    for fid, F in I["fonti"].items():
        conti["fonti"] += 1
        if F["http"] != 200 or not FONTI_UFFICIALI_IN.match(F["url"]):
            errori.append(f"fonte {fid}: HTTP {F['http']} o dominio non ufficiale {F['url']}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", F["letto_il"] or "") or F["letto_il"] > G.OGGI.isoformat():
            errori.append(f"fonte {fid}: data di lettura non valida")
        f_c = RIN.file_cache(fid)
        if not copia_usabile(27, fid, f_c, "india_evisa.py"):
            continue
        ef = []
        if F["tipo"] == "pdf" and hashlib.sha256(f_c.read_bytes()).hexdigest() != F["sha256"]:
            ef.append(f"fonte {fid}: il PDF salvato non è quello da cui sono stati estratti i dati (rilanciare la raccolta)")
        t = RIN.testo_fonte(fid, f_c)
        for c in I["citazioni"]:
            if c["f"] == fid and c["x"] not in t:
                ef.append(f"fonte {fid}: citazione {c['id']} non parola per parola nel testo salvato")
        if fid == "evisa":
            ef += RIN.controlla_porti(M, t)
        errori += esito_copia(27, fid, ef, f_c, F["letto_il"])
    for c in I["citazioni"]:
        if len(c["x"].split()) > RIN.MAX_PAROLE:
            errori.append(f"citazione {c['id']} oltre {RIN.MAX_PAROLE} parole")
    # b) seconda lettura dei PDF: stesso numero di righe e di Paesi, numeri d'ordine 1..N, stessi nomi e stessi valori dei dati
    pdf = {}
    for fid, k in COLONNE_PDF_IN.items():
        T = I["tabelle"][fid]
        f_pdf = RIN.file_cache(fid)
        if not f_pdf.exists() or hashlib.sha256(f_pdf.read_bytes()).hexdigest() != I["fonti"][fid]["sha256"]:
            # PDF salvato mancante (avviso già dato sopra) o diverso da quello dei dati (errore o avviso sopra): niente seconda lettura;
            # le celle delle pagine si controllano contro i valori grezzi dei dati (sotto, punto c)
            if f_pdf.exists():
                avviso(27, f"{fid}: seconda lettura del PDF saltata (il PDF salvato non è quello dei dati): pagine controllate contro i dati")
            else:
                avviso(27, f"{fid}: seconda lettura del PDF saltata (PDF salvato mancante): pagine controllate contro i dati")
            conti["righe_tv" if fid == "fee_tv" else "righe_altri"] = len(T["righe"])
            pdf[fid] = {d["iso2"]: dict(zip([c for c, _ in T["colonne"]], d["grezzi"])) for d in T["righe"]}
            continue
        righe, metodo = righe_pdf_indipendenti(f_pdf, k)
        conti["metodo"] = metodo
        conti["righe_tv" if fid == "fee_tv" else "righe_altri"] = len(righe)
        if [r[0] for r in righe] != list(range(1, len(righe) + 1)):
            errori.append(f"{fid}: la seconda lettura del PDF non dà numeri d'ordine consecutivi")
        if len(righe) != len(T["righe"]) or len(righe) != I["fonti"][fid]["righe"]:
            errori.append(f"{fid}: {len(righe)} righe nel PDF (seconda lettura) contro {len(T['righe'])} nei dati")
        for r, d in zip(righe, T["righe"]):
            if r[0] != d["n"] or r[1] != d["nome_pdf"] or r[2] != d["grezzi"]:
                errori.append(f"{fid}: riga {r[0]} diversa: PDF {r[1]} {r[2]}, dati {d['nome_pdf']} {d['grezzi']}")
            atteso = {c: (None if g == "-" else int(g)) for (c, _), g in zip(T["colonne"], r[2])}
            if atteso != d["valori"]:
                errori.append(f"{fid}: riga {r[0]} {r[1]}: valori dei dati diversi dal PDF")
            conti["valori"] += len(r[2])
        pdf[fid] = {d["iso2"]: dict(zip([c for c, _ in T["colonne"]], r[2])) for r, d in zip(righe, T["righe"])}
    union = set(pdf["fee_tv"]) | set(pdf["fee_altri"])
    conti["paesi"] = len(union)
    if {p["iso2"] for p in G.IN_PAESI} != union or len(G.IN_PAESI) != len(union):
        errori.append("Paesi dei dati diversi dall'unione delle due tabelle del PDF")

    def attesa_cella(iso, k):
        """Testo atteso di una cella, dal PDF (seconda lettura), non dalle funzioni di genera.py."""
        fid = "fee_tv" if k.startswith("tv") else "fee_altri"
        g = pdf[fid].get(iso, {}).get(k)
        if g is None:
            return "not in table"
        return "“-” (no fee given)" if g == "-" else f"${int(g)}"

    # c) pagine = dati: indice, nazionalità con ricerche vere (ricalcolate dall'autocompletamento), visto all'arrivo, e-Arrival, tedesco, francese
    pag_attese = RIN.pagine_paese(D, union)
    conti["nazionalita"] = len(pag_attese)
    if [(g["iso2"], g["faq"], g["voa"]) for g in pag_attese] != [(g["iso2"], g["faq"], g["voa"]) for g in G.IN_PAGINE]:
        errori.append("pagine per nazionalità diverse da quelle ricalcolate dalle ricerche vere")
    for g in pag_attese:
        if len(g["ricerche"]) < RIN.MIN_RICERCHE or any(not RIN.parla_di(s, RIN.NAZIONALITA[g["iso2"]]["parole"]) or s not in ricerche for s in g["ricerche"]):
            errori.append(f"{g['iso2']}: pagina senza ricerche vere sufficienti sulla nazionalità")
    attese = ({G.url_in(g) + "index.html" for g in G.IN_PAGINE} | {f"{G.IN_BASE}/index.html", f"{G.IN_DE}/index.html", f"{G.IN_FR}/index.html"})
    trovate = {q.relative_to(SITO).as_posix() for q in (SITO / G.IN_BASE).rglob("*.html")} if (SITO / G.IN_BASE).exists() else set()
    if attese != trovate:
        errori.append(f"pagine {G.IN_BASE} diverse dai dati: mancano {sorted(attese - trovate)}, in più {sorted(trovate - attese)}")
    sm = leggi("sitemap.xml")
    tutte = sorted(attese) + [f"{G.IN_VOA}/index.html", f"{G.IN_ARR}/index.html"]
    tutti_numeri = set().union(*[_numeri_in(c["x"]) for c in I["citazioni"]])

    def comune(rel, t, lingua):
        """Controlli di ogni pagina della sezione."""
        conti["pagine"] += 1
        vis = _vis_in(t)
        if f"<loc>{G.URL_SITO}/{rel[:-len('index.html')]}</loc><lastmod>{I['controllato_il']}</lastmod>" not in sm:
            errori.append(f"{rel}: non in sitemap o lastmod diverso dalla data di lettura")
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(tit) > G.LIMITE_TITOLO_IN or str(G.ANNO) not in tit:
            errori.append(f"{rel}: titolo oltre {G.LIMITE_TITOLO_IN} caratteri o senza l'anno: {tit}")
        if f'<html lang="{lingua}">' not in t:
            errori.append(f"{rel}: lingua della pagina diversa da {lingua}")
        if lingua != "en" and ('<header class="top" lang="en">' not in t or '<footer lang="en">' not in t):
            errori.append(f"{rel}: menu e piè di pagina in inglese senza lang=\"en\"")
        m = re.search(r'<p class="lead" id="answer">(.*?)</p>', t)
        inizio = {"en": "According to ", "de": "Laut ", "fr": "Selon "}[lingua]
        data = {"en": G.data_lunga, "de": G.data_de, "fr": G.data_fr}[lingua](I["controllato_il"])
        if not m or not unescape(m.group(1)).startswith(inizio) or data not in unescape(m.group(1)):
            errori.append(f"{rel}: prima frase senza fonte o senza la data di controllo")
        # avviso evidente sul sito ufficiale, con il link ufficiale
        av = re.search(r'<p class="avviso avviso-idp" data-avviso-ufficiale>(.*?)</p>', t)
        if not av or 'href="https://indianvisaonline.gov.in/' not in av.group(1) or t.find("data-avviso-ufficiale") > t.find('<h2'):
            errori.append(f"{rel}: avviso sul sito ufficiale mancante, senza link ufficiale o non prima del primo titolo")
        elif lingua == "en" and not re.search(r"(Pay|Use) only on the official site|Use only the official site", av.group(1)):
            errori.append(f"{rel}: avviso senza 'only on the official site'")
        # link esterni: solo ufficiali (o SafetyWing sponsorizzato); nessun rivenditore nominato
        corpo = t[t.find("<main"):t.find("</main>")]  # contenuto della pagina (menu, piè di pagina e siti fratelli sono uguali in tutto il sito)
        for h in re.findall(r'<a [^>]*href="(https?://[^"]+)"', corpo):
            if not LINK_AMMESSI_IN.match(h):
                errori.append(f"{rel}: link esterno non ammesso {h}")
        mm = (RIVENDITORI_IN.search(_vis_in(corpo)) or RIVENDITORI_IN.search(" ".join(re.findall(r'href="([^"]+)"', corpo))) or VIETATE_SRV.search(vis)
              or AGGIRARE.search(vis))
        if mm:
            errori.append(f"{rel}: parola vietata (rivenditore di visti, altra affiliazione, assistente o aggiramento) '{mm.group(0)}'")
        sp = re.findall(r'<a [^>]*rel="sponsored[^"]*"[^>]*>', t)
        for a in sp:
            if "safetywing.com" not in a or 'target="_blank"' not in a or 'rel="sponsored noopener"' not in a:
                errori.append(f"{rel}: link sponsorizzato non ammesso o senza rel/target: {a[:80]}")
        if sp and (lingua != "en" or G.MON.RIGA_EN not in vis or 'class="aff-tag">Affiliate<' not in t):
            errori.append(f"{rel}: link sponsorizzato senza etichetta o riga di trasparenza, o in una pagina non inglese")
        if sp and t.find("data-assicurazione") < max(t.find('id="how-to-pay"'), t.find("Everyone else: the e-Visa")):
            errori.append(f"{rel}: riquadro SafetyWing prima delle informazioni ufficiali")
        # citazioni: ogni paragrafo tra virgolette (blockquote, lang en) è una citazione dei dati, al massimo 40 parole
        testi = {c["x"] for c in I["citazioni"]}
        for b in re.findall(r'<blockquote class="cit">(.*?)</blockquote>', t, re.S):
            for x in re.findall(r'<p lang="en">(.*?)</p>', b):
                conti["citazioni"] += 1
                if unescape(x) not in testi:
                    errori.append(f"{rel}: citazione non nei dati: {unescape(x)[:60]}")
        for fid in {c["f"] for c in I["citazioni"] if escape(c["x"], quote=False) in t or escape(c["x"]) in t}:
            if f'href="{escape(I["fonti"][fid]["url"])}"' not in t:
                errori.append(f"{rel}: manca il link alla fonte {fid}")
        # FAQ: JSON-LD = testo visibile
        ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t)]
        fq = next((x for x in ld if x.get("@type") == "FAQPage"), None)
        if not fq:
            errori.append(f"{rel}: FAQ JSON-LD mancante")
        else:
            for e in fq["mainEntity"]:
                conti["faq"] += 1
                if f"<h3>{escape(e['name'])}</h3><p>{escape(e['acceptedAnswer']['text'])}</p>" not in t:
                    errori.append(f"{rel}: FAQ visibile diversa dal JSON-LD: {e['name']}")
        if not re.search(r"not legal advice|keine Rechtsberatung|pas un conseil juridique", vis):
            errori.append(f"{rel}: manca 'not legal advice'")
        return vis, fq

    # d) indice: righe = PDF (seconda lettura), filtro, FAQ da ricerche vere, numeri delle risposte solo dalle tabelle e dalle citazioni
    idx = f"{G.IN_BASE}/index.html"
    if (SITO / idx).exists():
        t = leggi(idx)
        vis, fq = comune(idx, t, "en")
        righe = re.findall(r'<tr data-voce id="([a-z]{2})" data-alias="[^"]*">(.*?)</tr>', t)
        if sorted(r[0].upper() for r in righe) != sorted(union):
            errori.append(f"{idx}: righe della tabella diverse dai Paesi del PDF ({len(righe)} contro {len(union)})")
        for iso, r in righe:
            celle = re.findall(r'<td[^>]*data-c="([a-z0-9_]+)"[^>]*>(.*?)</td>', r)
            if [c for c, _ in celle] != [k for k, _ in G.COL_IN]:
                errori.append(f"{idx}: riga {iso} con colonne diverse")
                continue
            for k, cel in celle:
                if unescape(re.sub(r"<[^>]+>", "", cel)) != attesa_cella(iso.upper(), k):
                    errori.append(f"{idx}: riga {iso}, {k}: «{unescape(re.sub(r'<[^>]+>', '', cel))}» invece di «{attesa_cella(iso.upper(), k)}»")
        for g in G.IN_PAGINE:
            if f'href="../{G.url_in(g)}"' not in t:
                errori.append(f"{idx}: manca il link alla pagina {g['iso2']}")
        for x in ("data-in-cerca", "data-in-tipo", "data-in-tab", f'href="../{G.IN_DE}/"', f'href="../{G.IN_FR}/"', 'id="ports"'):
            if x not in t:
                errori.append(f"{idx}: manca {x}")
        for f in M["faq"]["indice"]:
            if f["query"] not in ricerche:
                errori.append(f"{idx}: FAQ «{f['q']}» senza ricerca vera")
        valori = {str(int(v)) for tab in pdf.values() for r in tab.values() for v in r.values() if v != "-"}
        for q, a in G.faq_indice_in():
            # cifre in dollari solo dalle tabelle (o dalle citazioni); i numeri fino al numero dei Paesi sono conteggi delle righe
            extra = {n for n in _numeri_in(a) if "." not in n and "," not in n and int(n) > len(union)} - valori - tutti_numeri - {str(G.ANNO)}
            if extra:
                errori.append(f"{idx}: numeri non presi dalle tabelle nella FAQ «{q}»: {sorted(extra)}")
    else:
        errori.append(f"indice {G.IN_BASE} mancante")
    # e) pagine per nazionalità: tabella = PDF, prima frase con le cifre del PDF, FAQ da ricerche vere sulla nazionalità
    for g in G.IN_PAGINE:
        rel = G.url_in(g) + "index.html"
        if not (SITO / rel).exists():
            continue
        t = leggi(rel)
        vis, fq = comune(rel, t, "en")
        iso = g["iso2"]
        for k, n in G.COL_IN:
            m = re.search(r'<tr data-c="%s"><th scope="row">[^<]*</th><td[^>]*>(.*?)</td>' % k, t)
            att = attesa_cella(iso, k)
            letto = unescape(m.group(1)) if m else None
            if att == "not in table":
                ok = letto == "Not in the e-Tourist table"
            elif att.startswith("“-”"):
                ok = letto == "“-” in the table (no fee given)"
            else:
                ok = letto == att
            if not ok:
                errori.append(f"{rel}: riga {k} «{letto}» diversa dal PDF «{att}»")
        lead = unescape(re.search(r'<p class="lead" id="answer">(.*?)</p>', t).group(1))
        val = {str(int(v)) for r in (pdf["fee_tv"].get(iso, {}), pdf["fee_altri"].get(iso, {})) for v in r.values() if v != "-"}
        giorno_controllo = str(int(G.IN["controllato_il"][8:10]))  # «checked on 4 November 2026»: il giorno cambia a ogni rilettura
        extra = {n for n in _numeri_in(lead) if n not in val and n not in {"8", "15", "31", "2026", "3", "30", giorno_controllo}}
        if extra:
            errori.append(f"{rel}: numeri della prima frase non presi dalla riga del PDF: {sorted(extra)}")
        for f in g["faq"]:
            if f["query"] not in ricerche or not RIN.parla_di(f["query"], RIN.NAZIONALITA[iso]["parole"]):
                errori.append(f"{rel}: FAQ senza una ricerca vera sulla nazionalità ({f['query']!r})")
        if fq and len(fq["mainEntity"]) != len(g["faq"]) + (1 if g.get("voa") else 0):
            errori.append(f"{rel}: numero di FAQ diverso dalle ricerche vere")
        if f'href="../../{G.IN_BASE}/"' not in t or f'href="../../{G.IN_ARR}/"' not in t:
            errori.append(f"{rel}: mancano i link all'indice o alla e-Arrival card")
    # f) visto all'arrivo ed e-Arrival card
    for rel, gruppo in ((f"{G.IN_VOA}/index.html", "voa"), (f"{G.IN_ARR}/index.html", "arrivo")):
        if not (SITO / rel).exists():
            errori.append(f"{rel} mancante")
            continue
        t = leggi(rel)
        comune(rel, t, "en")
        for f in M["faq"][gruppo]:
            if f["query"] not in ricerche:
                errori.append(f"{rel}: FAQ «{f['q']}» senza ricerca vera")
            extra = _numeri_in(f.get("pre", "") + " " + f.get("post", "")) - tutti_numeri
            if extra:
                errori.append(f"{rel}: numeri nelle parole nostre non presi dalle citazioni: {sorted(extra)}")
    if (SITO / f"{G.IN_ARR}/index.html").exists() and f'href="{G.IN_EARRIVAL}"' not in leggi(f"{G.IN_ARR}/index.html"):
        errori.append("e-Arrival: manca il link al modulo ufficiale")
    # g) pagine in tedesco e francese: tabella = PDF, ricerche vere nella lingua
    for lingua, base in (("de", G.IN_DE), ("fr", G.IN_FR)):
        rel = f"{base}/index.html"
        if not (SITO / rel).exists():
            continue
        t = leggi(rel)
        comune(rel, t, lingua)
        sugg = set(RIN.suggerimenti(D, lingua))
        if len(sugg) < 10:
            errori.append(f"{rel}: troppe poche ricerche vere in {lingua} per giustificare la pagina")
        for f in M["faq"][lingua]:
            if f["query"] not in sugg:
                errori.append(f"{rel}: FAQ «{f['q']}» senza ricerca vera in {lingua}")
        righe = re.findall(r'<tr data-voce id="([a-z]{2})">(.*?)</tr>', t)
        if [r[0].upper() for r in righe] != I["pagine_lingua"][lingua]["paesi"]:
            errori.append(f"{rel}: righe diverse dai Paesi previsti")
        for iso, r in righe:
            celle = [unescape(re.sub(r"<[^>]+>", "", x)) for x in re.findall(r'<td class="n"[^>]*>(.*?)</td>', r)]
            if celle != [attesa_cella(iso.upper(), k) for k, _ in G.COL_IN]:
                errori.append(f"{rel}: riga {iso} diversa dal PDF: {celle}")
    # h) collegamenti in entrata; nessun link nelle pagine già revisionate e non pubblicate (animali, pedaggi)
    entrata = [("index.html", f'href="{G.IN_BASE}/"'), ("about/index.html", f'id="{G.IN_BASE}"'), ("404.html", f'href="/{G.IN_BASE}/"'),
               ("passport-validity/india/index.html", f'href="../../{G.IN_BASE}/united-kingdom/"'),
               ("canadian-passport/india/index.html", f'href="../../{G.IN_BASE}/canada/"'),
               ("australian-passport/india/index.html", f'href="../../{G.IN_BASE}/australia/"')]
    for f, h in entrata:
        conti["link"] += 1
        if h not in leggi(f):
            errori.append(f"{f}: manca il link {h}")
    for base in (G.PET_BASE, G.PED_BASE, G.TB_BASE, G.TR_BASE, G.FL_BASE):
        for q in (SITO / base).rglob("*.html"):
            if G.IN_BASE in q.read_text(encoding="utf-8"):
                errori.append(f"{q.relative_to(SITO)}: link aggiunto a una pagina già revisionata")
    for nome in ("india_evisa.json", "india_evisa_manuali.json", "india_evisa_domanda.json"):
        if VIETATE_SRV.search((SITO.parent / "dati" / nome).read_text(encoding="utf-8")):
            errori.append(f"dati/{nome}: nome di un assistente di intelligenza artificiale")
    # i) browser: 375 px (chiaro e scuro) e 1280 px, filtro della tabella
    e, conti["browser"] = controlla_browser_in()
    errori += e
    return errori, conti


BROWSER_IN_JS = r"""
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const http = require('http'); const fs = require('fs'); const path = require('path');
const ROOT = process.argv[2]; const PAGINE = JSON.parse(process.argv[3]); const CARTELLA = process.argv[4];
const TIPI = {'.html':'text/html; charset=utf-8','.xml':'application/xml','.txt':'text/plain'};
const srv = http.createServer((req, res) => { let p = decodeURIComponent(req.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html';
  const f = path.join(ROOT, p); if (!f.startsWith(ROOT) || !fs.existsSync(f)) { res.writeHead(404); res.end(''); return; }
  res.writeHead(200, {'Content-Type': TIPI[path.extname(f)] || 'application/octet-stream'}); res.end(fs.readFileSync(f)); });
srv.listen(0, async () => {
  const base = 'http://127.0.0.1:' + srv.address().port; const out = {pagine: [], filtro: []};
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  for (const [w, tema] of [[375, 'light'], [375, 'dark'], [1280, 'light']]) {
    const ctx = await b.newContext({ viewport: { width: w, height: 900 }, colorScheme: tema });
    for (const u of PAGINE) {
      const p = await ctx.newPage(); const err = [];
      p.on('console', m => { if (m.type() === 'error' && !m.text().startsWith('[Report Only]')) err.push(m.text()); }); p.on('pageerror', e => err.push(String(e)));
      await p.goto(base + u, { waitUntil: 'load' });
      const r = await p.evaluate(() => ({ scroll: document.documentElement.scrollWidth, vista: window.innerWidth,
        risposta: (() => { const a = document.querySelector('#answer'); return !!a && a.getBoundingClientRect().height > 0; })(),
        avviso: (() => { const a = document.querySelector('[data-avviso-ufficiale]'); return !!a && a.getBoundingClientRect().height > 0 && a.getBoundingClientRect().top < 2600; })() }));
      out.pagine.push(Object.assign({ url: u, larghezza: w, tema: tema, errori: err }, r));
      if (tema === 'light') await p.screenshot({ path: CARTELLA + '/' + (u.split('/').filter(Boolean).join('-') || 'home') + '-' + w + '.png', fullPage: false });
      if (u === '/india-e-visa-fee/' && tema === 'light') {
        await p.fill('[data-in-cerca]', 'united kingdom');
        const uk = await p.evaluate(() => [...document.querySelectorAll('tr[data-voce]')].filter(r => !r.hidden).map(r => r.id));
        await p.fill('[data-in-cerca]', 'usa');
        const us = await p.evaluate(() => [...document.querySelectorAll('tr[data-voce]')].filter(r => !r.hidden).map(r => r.id));
        await p.fill('[data-in-cerca]', 'gb'); await p.fill('[data-in-cerca]', '');
        await p.selectOption('[data-in-tipo]', 'tv5');
        const col = await p.evaluate(() => { const r = document.querySelector('tr[data-voce]#gb');
          return [...r.cells].filter(c => getComputedStyle(c).display !== 'none').map(c => c.textContent.trim()); });
        const n = await p.textContent('[data-in-n]');
        const sw = await p.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
        out.filtro.push({ larghezza: w, uk: uk, us: us, colonne: col, n: n, scroll: sw[0], vista: sw[1] });
        await p.screenshot({ path: CARTELLA + '/indice-filtro-' + w + '.png', fullPage: false });
      }
      await p.close();
    }
    await ctx.close();
  }
  await b.close(); srv.close(); console.log(JSON.stringify(out));
});
"""
PAGINE_IN_BROWSER = ["/india-e-visa-fee/", "/india-e-visa-fee/united-kingdom/", "/india-e-visa-fee/united-states/", "/india-e-visa-fee/bangladesh/",
                     "/india-e-visa-fee/indien-e-visum-kosten/", "/india-e-visa-fee/prix-e-visa-inde/", "/india-visa-on-arrival/", "/india-e-arrival-card/"]


def controlla_browser_in():
    if os.environ.get("BYF_NO_BROWSER") == "1":
        return [], "saltato (BYF_NO_BROWSER=1)"
    cartella = tempfile.mkdtemp(prefix="india-")
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(BROWSER_IN_JS)
    try:
        r = subprocess.run(["node", fh.name, str(SITO), json.dumps(PAGINE_IN_BROWSER), cartella], capture_output=True, text=True, timeout=600)
    except FileNotFoundError:
        return ["node non trovato: prova nel browser della sezione India saltata"], "no"
    finally:
        os.unlink(fh.name)
    if r.returncode != 0:
        return ["Errore Playwright (India): " + r.stderr[:800]], "no"
    o = json.loads(r.stdout)
    errori = []
    for x in o["pagine"]:
        if x["scroll"] > x["vista"]:
            errori.append(f"{x['url']} ({x['larghezza']} px, {x['tema']}): scorrimento orizzontale {x['scroll']} > {x['vista']}")
        if x["errori"]:
            errori.append(f"{x['url']} ({x['larghezza']} px, {x['tema']}): errori in console {x['errori'][:2]}")
        if not x["risposta"] or not x["avviso"]:
            errori.append(f"{x['url']} ({x['larghezza']} px, {x['tema']}): risposta o avviso sul sito ufficiale non visibili in alto")
    tv5 = G.val_in(G.IN_PER["GB"], "tv5")
    for f in o["filtro"]:
        if f["uk"] != ["gb"] or f["us"] != ["us"]:
            errori.append(f"filtro ({f['larghezza']} px): 'united kingdom' -> {f['uk']}, 'usa' -> {f['us']}")
        if len(f["colonne"]) != 2 or f["colonne"][1] != f"${tv5}":
            errori.append(f"filtro per tipo ({f['larghezza']} px): colonne visibili {f['colonne']} invece di Paese + ${tv5}")
        if f["n"] != str(len(G.IN_PAESI)) or f["scroll"] > f["vista"]:
            errori.append(f"filtro ({f['larghezza']} px): conteggio {f['n']} o scorrimento orizzontale")
    if len(o["filtro"]) != 2:
        errori.append("filtro della tabella non provato a 375 e 1280 px")
    return errori, f"{len(o['pagine'])} viste (8 pagine a 375 px chiaro/scuro e 1280 px), filtro per Paese e per tipo provato a 375 e 1280 px, schermate in {cartella}"


def controlla_indexnow():
    """File chiave IndexNow in sito/: presente, con dentro solo la chiave, fuori dalla sitemap (scritto da genera.py accanto a robots.txt)."""
    errori = []
    f = SITO / f"{G.CHIAVE_INDEXNOW}.txt"
    if not f.exists():
        errori.append(f"file chiave IndexNow mancante: {f.name}")
    elif f.read_text(encoding="utf-8").strip() != G.CHIAVE_INDEXNOW:
        errori.append(f"file chiave IndexNow con contenuto sbagliato: {f.name}")
    if f.name in (SITO / "sitemap.xml").read_text(encoding="utf-8"):
        errori.append("file chiave IndexNow citato nella sitemap")
    return errori


# ---------------------------------------------------------------- 28. Scooter e motorini in vacanza: quale patente? (31/10/2026)
_spec_sc = importlib.util.spec_from_file_location("raccolta_scooter", Path(__file__).resolve().parent / "raccolta" / "scooter.py")
RSC = importlib.util.module_from_spec(_spec_sc)
_spec_sc.loader.exec_module(RSC)
# Fonti ammesse: portale dell'amministrazione francese, Boletín Oficial del Estado, leggi federali tedesche, API dei consigli di viaggio di GOV.UK
FONTI_UFFICIALI_SC = re.compile(r"^https://(?:www\.service-public\.gouv\.fr|www\.boe\.es|www\.gesetze-im-internet\.de|www\.gov\.uk/api/content/foreign-travel-advice)/")
LINK_UFFICIALI_SC = re.compile(r"^https://(?:www\.service-public\.gouv\.fr|www\.boe\.es|www\.gesetze-im-internet\.de|www\.gov\.uk/foreign-travel-advice)/")
# Indirizzi provati per i Paesi non letti: banche dati delle leggi, dipartimenti dei trasporti, API di GOV.UK
FONTI_NON_LETTE_SC = re.compile(r"^https://(?:www\.normattiva\.it|www\.ris\.bka\.gv\.at|hidot\.hawaii\.gov)/")
# Nessun link di affiliazione né nome di noleggiatore nella sezione (DiscoverCars noleggia auto; BikesBooking passa da Travelpayouts, in pausa)
VIETATI_SC = re.compile(r"discovercars|bikesbooking|travelpayouts|tp\.media|stay22|viator|getyourguide|riderly|safetywing|rentalcars|klook", re.I)
# Promesse vietate: la sezione non garantisce che il noleggiatore accetti la patente
PROMESSE_SC = re.compile(r"\bguarantee|\bno problem\b|\byou(?:'ll| will) be fine\b|\balways accepted\b|\bdon't worry\b|\bsure to\b|\bcheapest\b", re.I)


def controlla_scooter():
    """Punto 28: dati = fonti = pagine; citazioni nel testo salvato (cache) con impronta; traduzioni; numeri solo dalle fonti; esiti con
    citazione; prima frase con fonte e data; FAQ da ricerche vere; Paesi non letti coerenti con la rilettura; nessuna affiliazione né promessa."""
    from html import unescape
    errori = []
    conti = {"paesi": 0, "pagine": 0, "fonti": 0, "citazioni": 0, "traduzioni": 0, "faq": 0, "non_letti": 0, "cache": "no", "link": 0}
    if not G.SC:
        return ["dati/scooter.json mancante (rilanciare raccolta/scooter.py)"], conti
    M = json.loads((SITO.parent / "dati" / "scooter_manuali.json").read_text(encoding="utf-8"))
    nl_dati = [{k: v for k, v in x.items() if k not in ("http", "letto_il", "frasi_regola", "aggiornata_il")} for x in G.SC["non_letti"]]
    if M["paesi"] != G.SC["paesi"] or M["generali"] != G.SC["generali"] or M["non_letti"] != nl_dati:
        errori.append("dati/scooter.json non è aggiornato rispetto a dati/scooter_manuali.json (rilanciare raccolta/scooter.py)")
    D = json.loads((SITO.parent / "dati" / "scooter_domanda.json").read_text(encoding="utf-8"))
    ricerche = RSC.tutte_ricerche(D)
    # a) fonti: HTTP 200, domini ammessi, data; dalla cache frasi e impronte ricalcolate
    for fid, F in G.SC["fonti"].items():
        conti["fonti"] += 1
        if F["http"] != 200 or not FONTI_UFFICIALI_SC.match(F["url"]) or not LINK_UFFICIALI_SC.match(F["pagina"]):
            errori.append(f"scooter fonte {fid}: HTTP {F['http']} o indirizzo non ufficiale ({F['url']}, {F['pagina']})")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", F["letto_il"] or "") or F["letto_il"] > G.OGGI.isoformat():
            errori.append(f"scooter fonte {fid}: data di lettura non valida {F['letto_il']}")
        f_c = RSC.file_cache(fid)
        if copia_usabile(28, fid, f_c, "scooter.py"):
            ef = []
            t = RSC.testo_fonte(fid, f_c.read_bytes(), F.get("charset"))
            frasi = RSC.frasi_fonte(G.SC, fid)
            for x in frasi:
                if x not in t:
                    ef.append(f"scooter fonte {fid}: la frase non è nel testo salvato: {x[:70]}")
            if RSC.impronta_zona(t, frasi) != F["impronta"]:
                ef.append(f"scooter fonte {fid}: impronta diversa dal testo salvato (rilanciare raccolta/scooter.py)")
            conti["cache"] = "sì"
            errori += esito_copia(28, fid, ef, f_c, F["letto_il"])
    # b) Paesi non letti: motivo coerente con la rilettura (non risponde = HTTP diverso da 200; regola assente = HTTP 200 e 0 frasi)
    for x in G.SC["non_letti"]:
        conti["non_letti"] += 1
        u = RSC.FCDO_API + x["fcdo"] if x.get("fcdo") else x.get("url", "")
        if not (x.get("fcdo") or FONTI_NON_LETTE_SC.match(u)):
            errori.append(f"scooter non letto {x['nome']}: indirizzo non previsto {u}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", x.get("letto_il") or "") or G.data_lunga(x["letto_il"]) not in x["motivo"]:
            errori.append(f"scooter non letto {x['nome']}: data della rilettura mancante nel motivo")
        if x["tipo"] == "regola_assente" and (x.get("http") != 200 or x.get("frasi_regola") != 0):
            errori.append(f"scooter non letto {x['nome']}: 'regola assente' ma HTTP {x.get('http')} e {x.get('frasi_regola')} frasi con la regola")
        if x["tipo"] == "non_risponde" and (x.get("http") == 200 or "did not answer" not in x["motivo"]):
            errori.append(f"scooter non letto {x['nome']}: 'non risponde' ma HTTP {x.get('http')}")
        if x["tipo"] not in ("regola_assente", "non_risponde") or x["iso2"] in G.SC_PER:
            errori.append(f"scooter non letto {x['nome']}: tipo non valido o Paese con una pagina")
        if x.get("query") and x["query"] not in ricerche:
            errori.append(f"scooter non letto {x['nome']}: ricerca {x['query']!r} non in dati/scooter_domanda.json")
    # c) pagine: esattamente indice + una per Paese, in sitemap con lastmod
    sm = leggi("sitemap.xml")
    attese = {G.url_sc(p) + "index.html" for p in G.SC_PAESI} | {f"{G.SC_BASE}/index.html"}
    trovate = {q.relative_to(SITO).as_posix() for q in (SITO / G.SC_BASE).rglob("index.html")} if (SITO / G.SC_BASE).exists() else set()
    if attese != trovate:
        errori.append(f"pagine scooter diverse dai dati: mancano {sorted(attese - trovate)}, in più {sorted(trovate - attese)}")
    for q in sorted(attese):
        if f"<loc>{G.URL_SITO}/{q[:-len('index.html')]}</loc>" not in sm:
            errori.append(f"{q}: non in sitemap")
    host_altri = {urlparse(u).hostname for u, _, _ in G.ALTRI_SITI}
    for p in G.SC_PAESI:
        conti["paesi"] += 1
        ids = {c["id"] for c in p["citazioni"]}
        # numeri nostri solo dalle citazioni (originale e traduzione) e dall'anno
        ammessi = set().union(*[_numeri_big(c["x"]) for c in p["citazioni"]], {G.ANNO})
        campi = [("risposta", p["risposta"]), ("h1", p["h1"]), ("titolo", p["titolo"])]
        campi += [(f"caso {k}", v["breve"] + " " + v.get("nota", "")) for k, v in p["casi"].items()]
        campi += [(f"patente {k}", v["breve"] + " " + v.get("nota", "")) for k, v in p["patenti"].items()]
        campi += [(f"FAQ «{q['q']}»", q["pre"] + " " + q["post"]) for q in p["faq"]]  # la domanda è una ricerca vera: i suoi numeri non sono nostri
        campi += [(f"traduzione {c['id']}", c["tr"]) for c in p["citazioni"] if c.get("tr")] + [(f"altro {a['titolo']}", a["titolo"]) for a in p["altro"]]
        for nome, testo in campi:
            extra = _numeri_big(testo.replace("0.1", "0,1")) - ammessi
            if extra:
                errori.append(f"scooter {p['slug']}: numeri non presi dalle fonti in {nome}: {sorted(extra)}")
        for c in p["citazioni"]:
            if G.SC["fonti"][c["f"]]["lingua"] != "en" and not c.get("tr"):
                errori.append(f"scooter {p['slug']}: citazione {c['id']} non in inglese senza traduzione")
            if G.SC["fonti"][c["f"]]["lingua"] == "en" and c.get("tr"):
                errori.append(f"scooter {p['slug']}: citazione inglese {c['id']} con traduzione")
        for k, v in list(p["casi"].items()) + list(p["patenti"].items()):
            if v["esito"] not in G.ESITI_SC or (v["esito"] != "non_detto" and not v["cit"]) or any(i not in ids for i in v["cit"]):
                errori.append(f"scooter {p['slug']}: voce {k} senza citazione o con citazione sconosciuta")
            if v["esito"] == "non_detto" and v["cit"]:
                errori.append(f"scooter {p['slug']}: voce {k} 'Not stated' con citazioni")
        if p["query"] not in ricerche:
            errori.append(f"scooter {p['slug']}: la pagina non ha una ricerca vera ({p['query']!r})")
        for q in p["faq"]:
            if q["query"] not in ricerche:
                errori.append(f"scooter {p['slug']}: FAQ «{q['q']}» senza una ricerca vera ({q['query']!r})")
        rel = G.url_sc(p) + "index.html"
        if not (SITO / rel).exists():
            continue
        conti["pagine"] += 1
        t = leggi(rel)
        main_ = t.split('<main id="main">', 1)[-1].split("</main>", 1)[0]
        vis = unescape(re.sub(r"<[^>]+>", " ", main_))
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if tit != p["titolo"] or len(tit) > G.LIMITE_TITOLO_SC or str(G.ANNO) not in tit:
            errori.append(f"{rel}: titolo oltre {G.LIMITE_TITOLO_SC} caratteri, senza l'anno o diverso dai dati: {tit}")
        m = re.search(r'<p class="lead" id="answer">(.*?)</p>', t)
        prima = unescape(re.sub(r"<[^>]+>", "", m.group(1))) if m else ""
        d = G.data_lunga(max(G.SC["fonti"][f]["letto_il"] for f in dict.fromkeys(c["f"] for c in p["citazioni"])))
        if prima != f"According to {p['chi']}, checked on {d}, {p['risposta']}":
            errori.append(f"{rel}: prima frase diversa da 'According to <fonte>, checked on <data>, <risposta>'")
        for c in p["citazioni"] + G.SC["generali"]:
            conti["citazioni"] += 1
            if escape(c["x"], quote=False) not in t and escape(c["x"]) not in t:
                errori.append(f"{rel}: citazione mancante: {c['x'][:60]}")
            if c.get("tr"):
                conti["traduzioni"] += 1
                if f'<em>Our translation:</em> {escape(c["tr"], quote=False)}' not in t and f'<em>Our translation:</em> {escape(c["tr"])}' not in t:
                    errori.append(f"{rel}: traduzione mancante per {c['id']}")
        for f in dict.fromkeys(c["f"] for c in p["citazioni"]):
            F = G.SC["fonti"][f]
            if f'href="{escape(F["pagina"])}"' not in t or f"checked on {G.data_lunga(F['letto_il'])}" not in vis:
                errori.append(f"{rel}: manca il link o la data della fonte {f}")
        # tabella dei casi = dati
        for k, _ in G.CASI_SC:
            r_ = re.search(r'<tr data-voce data-caso="' + k + r'">(.*?)</tr>', t)
            if not r_ or G.ESITI_SC[p["casi"][k]["esito"]][0] not in unescape(r_.group(1)):
                errori.append(f"{rel}: riga del caso {k} diversa dai dati")
        for k, _ in G.PATENTI_SC:
            r_ = re.search(r'<tr data-voce data-patente="' + k + r'">(.*?)</tr>', t)
            if not r_ or G.ESITI_SC[p["patenti"][k]["esito"]][0] not in unescape(r_.group(1)):
                errori.append(f"{rel}: riga della patente {k} diversa dai dati")
        faq_ld = next((x for x in (json.loads(y) for y in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t)) if x.get("@type") == "FAQPage"), None)
        attese_faq = G.faq_sc(p)
        if not faq_ld or [(e["name"], e["acceptedAnswer"]["text"]) for e in faq_ld["mainEntity"]] != attese_faq:
            errori.append(f"{rel}: FAQ JSON-LD diversa dalle domande previste")
        for qd, r_ in attese_faq:
            conti["faq"] += 1
            if f"<h3>{escape(qd)}</h3><p>{escape(r_)}</p>" not in t:
                errori.append(f"{rel}: FAQ visibile diversa dal JSON-LD: {qd}")
        if "Check with the rental company and the official page before you ride." not in vis:
            errori.append(f"{rel}: manca l'avviso 'check with the rental company and the official page'")
        # link: Driving abroad dello stesso Paese (andata e ritorno)
        for k in G.PATENTI:
            if p["iso2"] in G.PAGINE_PAT[k]:
                conti["link"] += 1
                if f'href="../../{G.url_pat(k, p["iso2"])}"' not in t:
                    errori.append(f"{rel}: manca il link a Driving abroad ({k})")
                tp = leggi(G.url_pat(k, p["iso2"]) + "index.html")
                if f'href="../../../{G.url_sc(p)}"' not in tp:
                    errori.append(f"{G.url_pat(k, p['iso2'])}: manca il link alla pagina scooter")
    # d) indice
    idx = f"{G.SC_BASE}/index.html"
    if (SITO / idx).exists():
        t = leggi(idx)
        m = re.search(r'<p class="lead" id="answer">(.*?)</p>', t)
        if not m or unescape(m.group(1)) != G.prima_frase_sc() or f"last checked on {G.data_lunga(G.SC['controllato_il'])}" not in unescape(m.group(1)):
            errori.append(f"{idx}: prima frase diversa dai dati o senza la data")
        righe = re.findall(r'<tr data-voce id="([a-z-]+)">(.*?)</tr>', t)
        if [r[0] for r in righe] != [p["slug"] for p in G.SC_PAESI]:
            errori.append(f"{idx}: righe della tabella diverse dai Paesi dei dati")
        for (sl, r), p in zip(righe, G.SC_PAESI):
            if [unescape(x) for x in re.findall(r'<span class="badge [^"]+">([^<]+)</span>', r)] != [G.ESITI_SC[p["casi"][k]["esito"]][0] for k, _ in G.CASI_SC]:
                errori.append(f"{idx}: riga {sl} con esiti diversi dai dati")
        for x in G.SC["non_letti"]:
            if escape(x["motivo"], quote=False) not in t and escape(x["motivo"]) not in t:
                errori.append(f"{idx}: manca il Paese non letto {x['nome']} con il motivo")
        if "Check with the rental company and the official page before you ride." not in unescape(t):
            errori.append(f"{idx}: manca l'avviso 'check with the rental company and the official page'")
    else:
        errori.append("indice scooter-rental-licence mancante")
    # e) in tutta la sezione: link esterni solo ufficiali, nessuna affiliazione, nessuna promessa, nessun nome di assistente
    for q in sorted(attese):
        if not (SITO / q).exists():
            continue
        t = leggi(q)
        main_ = t.split('<main id="main">', 1)[-1].split("</main>", 1)[0]
        for h in re.findall(r'href="(https?://[^"]+)"', main_):
            hh = unescape(h)
            if not (LINK_UFFICIALI_SC.match(hh) or urlparse(hh).hostname in host_altri):
                errori.append(f"{q}: link non ufficiale {hh[:80]}")
        vis = unescape(re.sub(r"<[^>]+>", " ", main_))
        for rx, cosa in ((VIETATI_SC, "affiliazione o noleggiatore"), (PROMESSE_SC, "promessa"), (VIETATE_SRV, "nome di un assistente")):
            mm = rx.search(main_) or rx.search(vis)
            if mm:
                errori.append(f"{q}: {cosa} '{mm.group(0)}'")
        if 'rel="sponsored' in main_ or "data-noleggio" in main_:
            errori.append(f"{q}: riquadro o link di affiliazione nella sezione scooter")
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(tit) > G.LIMITE_TITOLO_SC:
            errori.append(f"{q}: titolo oltre {G.LIMITE_TITOLO_SC} caratteri")
    # f) collegamenti in entrata e dati senza nomi di assistenti
    if f'href="{G.SC_BASE}/"' not in leggi("index.html"):
        errori.append("home senza link alla sezione scooter")
    if 'id="scooter-rental-licence"' not in leggi("about/index.html"):
        errori.append("About senza la sezione scooter")
    if f'href="/{G.SC_BASE}/"' not in leggi("404.html"):
        errori.append("404 senza link alla sezione scooter")
    if f'href="../{G.SC_BASE}/"' not in leggi(f"{G.PAT_BASE}/index.html"):
        errori.append("indice Driving abroad senza link alla sezione scooter")
    for nome in ("scooter.json", "scooter_manuali.json", "scooter_domanda.json"):
        if VIETATE_SRV.search((SITO.parent / "dati" / nome).read_text(encoding="utf-8")):
            errori.append(f"dati/{nome}: nome di un assistente di intelligenza artificiale")
    return errori, conti


# ---------------------------------------------------------------- 29. Blue Badge all'estero (4/11/2026)
_spec_bb = importlib.util.spec_from_file_location("raccolta_bluebadge", Path(__file__).resolve().parent / "raccolta" / "bluebadge.py")
RBB = importlib.util.module_from_spec(_spec_bb)
_spec_bb.loader.exec_module(RBB)
# Fonti ammesse: GOV.UK (API dei contenuti), Your Europe e Commissione europea, governo italiano (disabilità), governo francese (service-public)
FONTI_UFFICIALI_BB = re.compile(r"^https://(?:www\.gov\.uk/api/content/|europa\.eu/youreurope/|commission\.europa\.eu/|www\.disabilita\.governo\.it/|www\.service-public\.gouv\.fr/)")
LINK_UFFICIALI_BB = re.compile(r"^https://(?:www\.gov\.uk/|europa\.eu/youreurope/|commission\.europa\.eu/|www\.disabilita\.governo\.it/|www\.service-public\.gouv\.fr/)")
# Pagine non pubbliche collegate dalla guida GOV.UK (FIA): mai nella sezione; niente affiliazioni né noleggi
VIETATI_BB = re.compile(r"disabledmotoring\.fia|disabledmotorists\.eu|\bFIA\b|discovercars|rentalcars|\bwise\b|viator|stay22|safetywing|booking\.com", re.I)
ESITO_CELLA_BB = {"Yes": "si", "Accepts non-EU parking cards.": "non_ue", "Non-EU parking cards accepted in some regions only.": "regioni",
                  "May not recognise non-EU issue parking card.": "forse_no", "No information": "non_detto"}


def _esito_cella_bb(cella):
    """Lettura indipendente della cella GOV.UK (non usa le etichette di genera.py): "Yes" e le formule fisse; Spagna = decisa localmente."""
    if cella in ESITO_CELLA_BB:
        return ESITO_CELLA_BB[cella]
    return "locale" if re.search(r"decided by local administrations", cella) else None


def controlla_bluebadge():
    """Punto 29: dati = manuali; fonti ufficiali con HTTP 200, data e impronta, citazioni e tabella GOV.UK ricalcolate dalla copia salvata; esiti
    = celle GOV.UK; pagine = Paesi con ricerche vere + indice + carte europee; prima frase con fonte e data; citazioni, traduzioni, fonti e
    date nelle pagine; numeri delle parole nostre solo dalle citazioni; FAQ da ricerche vere (JSON-LD = testo visibile); titoli <= 70 con
    l'anno; sitemap; nessun link FIA, nessuna affiliazione; link andata e ritorno con Driving abroad; home, About, 404."""
    from html import unescape
    errori = []
    conti = {"paesi": 0, "pagine": 0, "fonti": 0, "citazioni": 0, "traduzioni": 0, "faq": 0, "righe": 0, "cache": "no", "link": 0}
    if not G.BB:
        return ["dati/bluebadge.json mancante (rilanciare raccolta/bluebadge.py)"], conti
    M = json.loads((SITO.parent / "dati" / "bluebadge_manuali.json").read_text(encoding="utf-8"))
    campi = ("nome_gov", "fcdo_nomina", "ye", "ricerche", "pagina")
    if (M["citazioni"] != G.BB["citazioni"] or M["generali"] != G.BB["generali"] or M["faq_indice"] != G.BB["faq_indice"] or M["faq_carte"] != G.BB["faq_carte"]
            or M["paesi"] != [{k: v for k, v in p.items() if k not in campi} for p in G.BB["paesi"]]):
        errori.append("dati/bluebadge.json non è aggiornato rispetto a dati/bluebadge_manuali.json (rilanciare raccolta/bluebadge.py)")
    if len({(c["f"], c["x"]) for c in G.BB["citazioni"]}) != len(G.BB["citazioni"]) or len(G.BB_CIT) != len(G.BB["citazioni"]):
        errori.append("blue badge: citazioni o id ripetuti")
    D = json.loads((SITO.parent / "dati" / "bluebadge_domanda.json").read_text(encoding="utf-8"))
    ricerche = RBB.tutte_ricerche(D)
    # a) fonti: HTTP 200, domini ufficiali, date, impronta; dalla copia salvata frasi, impronte e tabella GOV.UK ricalcolate
    for fid, F in G.BB["fonti"].items():
        conti["fonti"] += 1
        if F["http"] != 200 or not FONTI_UFFICIALI_BB.match(F["url"]) or not LINK_UFFICIALI_BB.match(F["pagina"]) or fid not in RBB.FONTI:
            errori.append(f"blue badge fonte {fid}: HTTP {F['http']} o indirizzo non ufficiale ({F['url']})")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", F["letto_il"] or "") or F["letto_il"] > G.OGGI.isoformat():
            errori.append(f"blue badge fonte {fid}: data di lettura non valida {F['letto_il']}")
        if F["frasi"] and not F.get("impronta") or not F.get("impronta_testo"):
            errori.append(f"blue badge fonte {fid}: impronta mancante")
        f_c = RBB.file_cache(fid) if fid in RBB.FONTI else None
        if copia_usabile(29, fid, f_c, "bluebadge.py"):
            ef = []
            raw = f_c.read_bytes()
            t = RBB.testo_fonte(raw, F["tipo"])
            frasi = RBB.frasi_fonte(G.BB, fid)
            for x in frasi:
                if x not in t:
                    ef.append(f"blue badge fonte {fid}: la citazione non è parola per parola nella copia salvata: {x[:70]}")
            if frasi and RBB.impronta_zona(t, frasi) != F["impronta"]:
                ef.append(f"blue badge fonte {fid}: impronta diversa dalla copia salvata (rilanciare la raccolta)")
            if RBB.impronta(t) != F["impronta_testo"]:
                ef.append(f"blue badge fonte {fid}: impronta del testo diversa dalla copia salvata")
            if fid == "gov_eu" and RBB.tabella_govuk(raw) != G.BB["tabella_govuk"]:
                ef.append("blue badge: tabella GOV.UK diversa dalla copia salvata")
            if fid == "gov_pub" and RBB.storico_govuk(raw) != G.BB["storico_govuk"]:
                ef.append("blue badge: note di modifica GOV.UK diverse dalla copia salvata")
            if fid.startswith("fcdo_") and ("Blue Badge" in t) != G.BB_PER[fid[5:]]["fcdo_nomina"]:
                ef.append(f"blue badge fonte {fid}: 'nomina il Blue Badge' diverso dal testo salvato")
            conti["cache"] = "sì"
            errori += esito_copia(29, fid, ef, f_c, F["letto_il"])
    for c in G.BB["citazioni"]:
        F = G.BB["fonti"].get(c["f"])
        if not F:
            errori.append(f"blue badge: citazione {c['id']} da una fonte sconosciuta")
        elif F["lingua"] != "en" and not c.get("tr"):
            errori.append(f"blue badge: citazione {c['id']} senza traduzione")
    # b) esiti = celle della tabella GOV.UK (lettura indipendente); Paesi con pagina = ricerche vere ricalcolate
    righe = {r["paese"]: r for r in G.BB["tabella_govuk"]}
    if len(righe) != len(G.BB_PAESI):
        errori.append(f"blue badge: {len(righe)} righe GOV.UK per {len(G.BB_PAESI)} Paesi")
    attese = {f"{G.BB_BASE}/index.html", G.BB_CARTE + "index.html"}
    for p in G.BB_PAESI:
        conti["paesi"] += 1
        r = righe.get(p["nome_gov"])
        if not r or r["riconosciuto"] != p["riconosciuto"] or r["info"] != p["info"] or _esito_cella_bb(r["riconosciuto"]) != p["esito"]:
            errori.append(f"blue badge {p['iso2']}: esito o cella diversi dalla tabella GOV.UK ({r})")
        qq = next(x[5] for x in RBB.PAESI if x[0] == p["iso2"])
        cerca = RBB.ricerche_paese(D, qq)
        if cerca != p["ricerche"] or bool(cerca) != p["pagina"]:
            errori.append(f"blue badge {p['iso2']}: ricerche o pagina diverse dal ricalcolo")
        if p["pagina"]:
            attese.add(G.url_bb(p) + "index.html")
    trovate = {q.relative_to(SITO).as_posix() for q in (SITO / G.BB_BASE).rglob("*.html")} if (SITO / G.BB_BASE).exists() else set()
    if attese != trovate:
        errori.append(f"pagine {G.BB_BASE} diverse dai dati: mancano {sorted(attese - trovate)}, in più {sorted(trovate - attese)}")
    sm = leggi("sitemap.xml")
    cit_numeri = set().union(*[_numeri_gom(c["x"]) for c in G.BB["citazioni"]])

    def faq_ok(rel, t, voci, numeri):
        faq_ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t)]
        faq_ld = next((x for x in faq_ld if x.get("@type") == "FAQPage"), None)
        attese_faq = G.faq_bb(voci)
        if not faq_ld or [(e["name"], e["acceptedAnswer"]["text"]) for e in faq_ld["mainEntity"]] != attese_faq:
            errori.append(f"{rel}: FAQ JSON-LD diversa dalle domande previste")
        for (qd, a), q in zip(attese_faq, voci):
            conti["faq"] += 1
            if f"<h3>{escape(qd)}</h3><p>{escape(a)}</p>" not in t:
                errori.append(f"{rel}: FAQ visibile diversa dal JSON-LD: {qd}")
            if q["query"] not in ricerche:
                errori.append(f"{rel}: FAQ «{qd}» senza una ricerca vera ({q['query']!r})")
            if any(G.BB["fonti"][G.BB_CIT[i]["f"]]["lingua"] != "en" for i in q["cit"]) and "our translation" not in q["pre"]:
                errori.append(f"{rel}: FAQ «{qd}» con citazione tradotta senza dirlo")
            for i in q["cit"]:
                if G.BB_CIT[i].get("tr") and (G.BB_CIT[i]["tr"] not in a or G.BB_CIT[i]["x"] in a):
                    errori.append(f"{rel}: FAQ «{qd}» senza la traduzione nostra della citazione {i}")
            extra = _numeri_gom(q["pre"] + " " + q["post"] + " " + q["q"]) - numeri
            if extra:
                errori.append(f"{rel}: numeri non presi dalle fonti nella FAQ «{qd}»: {sorted(extra)}")

    def comune(rel, t, ids, attesa_prima):
        vis = unescape(re.sub(r"<[^>]+>", " ", t))
        m = re.search(r'<p class="lead" id="answer">(.*?)</p>', t)
        if not m or unescape(m.group(1)) != attesa_prima:
            errori.append(f"{rel}: prima frase diversa da quella prevista (fonte, data, risposta)")
        for i in ids:
            c = G.BB_CIT[i]
            conti["citazioni"] += 1
            if escape(c["x"], quote=False) not in t and escape(c["x"]) not in t:
                errori.append(f"{rel}: citazione mancante: {c['x'][:60]}")
            if c.get("tr"):
                conti["traduzioni"] += 1
                if escape(c["tr"], quote=False) not in t and escape(c["tr"]) not in t:
                    errori.append(f"{rel}: traduzione mancante: {c['tr'][:60]}")
            F = G.BB["fonti"][c["f"]]
            if f'href="{escape(F["pagina"])}"' not in t or f"checked on {G.data_lunga(F['letto_il'])}" not in vis:
                errori.append(f"{rel}: manca il link o la data della fonte {c['f']}")
            if F.get("aggiornato_il") and f"page updated on {G.data_lunga(F['aggiornato_il'])}" not in vis:
                errori.append(f"{rel}: manca la data di aggiornamento della fonte {c['f']}")
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if len(tit) > G.LIMITE_TITOLO_BB or str(G.ANNO) not in tit:
            errori.append(f"{rel}: titolo oltre {G.LIMITE_TITOLO_BB} caratteri o senza l'anno: {tit}")
        if G.MON.link_affiliati(t) or 'rel="sponsored' in t:
            errori.append(f"{rel}: link di affiliazione nella sezione")
        mm = VIETATI_BB.search(t) or VIETATE_SRV.search(vis) or AGGIRARE.search(vis)
        if mm:
            errori.append(f"{rel}: parola o link vietati '{mm.group(0)}'")
        if "not legal advice" not in vis:
            errori.append(f"{rel}: manca 'not legal advice'")
        for u in re.findall(r'<main.*?</main>', t, re.S)[:1]:
            for h in re.findall(r'href="(https?://[^"]+)"', u):
                if not LINK_UFFICIALI_BB.match(h) and not h.startswith(G.OGL):
                    errori.append(f"{rel}: link esterno non ufficiale {h}")
        return vis, tit

    # c) pagine Paese
    for p in G.BB_PAGINE:
        rel = G.url_bb(p) + "index.html"
        if not (SITO / rel).exists():
            continue
        conti["pagine"] += 1
        t = leggi(rel)
        ids = G.ids_pagina_bb(p)
        vis, tit = comune(rel, t, ids, G.prefisso_bb() + p["risposta"])
        F = G.BB["fonti"]["gov_eu"]
        if not G.prefisso_bb().startswith(f"According to GOV.UK (Department for Transport), in guidance updated on {G.data_lunga(F['aggiornato_il'])} and checked on {G.data_lunga(F['letto_il'])}"):
            errori.append("blue badge: prefisso della prima frase senza le date della guida GOV.UK")
        if p["nome"] not in tit and G.nf_bb(p) not in tit or tit != G.scegli(G.titoli_bb(p), G.LIMITE_TITOLO_BB):
            errori.append(f"{rel}: titolo senza il Paese o non tra le forme previste: {tit}")
        if f"<loc>{G.URL_SITO}/{G.url_bb(p)}</loc><lastmod>{G.data_pagina_bb(p)}</lastmod>" not in sm:
            errori.append(f"{rel}: non in sitemap o lastmod diverso dalla data di lettura")
        riga = f"<td>{escape(p['nome_gov'])}</td><td>{escape(p['riconosciuto'])}</td>"
        if riga not in t:
            errori.append(f"{rel}: riga GOV.UK mancante o diversa")
        if p.get("nota") and "data-nota" not in t:
            errori.append(f"{rel}: manca la nota")
        ammessi = set().union(*[_numeri_gom(G.BB_CIT[i]["x"]) for i in ids], {str(G.ANNO)})
        for s in (p["risposta"], p.get("nota", "")):
            extra = _numeri_gom(s) - ammessi - cit_numeri
            if extra:
                errori.append(f"{rel}: numeri non presi dalle fonti: {sorted(extra)} in «{s[:60]}»")
        faq_ok(rel, t, p["faq"], ammessi | cit_numeri)
        if not G.BB["generali"]["fcdo"].get(p["iso2"]) and "does not mention the Blue Badge" not in vis:
            errori.append(f"{rel}: manca la frase sul consiglio FCDO che non nomina il Blue Badge")
        if f'href="../../{G.BB_BASE}/"' not in t or f'href="../../{G.BB_CARTE}"' not in t:
            errori.append(f"{rel}: manca il link all'indice o alla pagina delle carte europee")
        if G.PAT and p["iso2"] in G.PAGINE_PAT["uk"]:
            conti["link"] += 2
            if f'href="../../{G.url_pat("uk", p["iso2"])}"' not in t:
                errori.append(f"{rel}: manca il link a Driving abroad ({G.url_pat('uk', p['iso2'])})")
            if f'href="../../../{G.url_bb(p)}"' not in leggi(G.url_pat("uk", p["iso2"]) + "index.html"):
                errori.append(f"{G.url_pat('uk', p['iso2'])}: manca il link di ritorno a {G.url_bb(p)}")
    # nessun link Blue Badge nelle pagine Driving abroad di altre patenti né dei Paesi senza pagina
    for k in G.PATENTI:
        for iso in G.PAGINE_PAT[k]:
            t = leggi(G.url_pat(k, iso) + "index.html")
            if f'{G.BB_BASE}/' in t and (k != "uk" or not G.ha_pagina_bb(iso)):
                errori.append(f"{G.url_pat(k, iso)}: link alla sezione Blue Badge non previsto")
    # d) indice: prima frase con i conteggi ricalcolati dalle celle, righe = tabella GOV.UK, FAQ
    idx = f"{G.BB_BASE}/index.html"
    if (SITO / idx).exists():
        t = leggi(idx)
        vis, _ = comune(idx, t, G.BB["generali"]["indice"] + ["ec_when"], G.prima_frase_bb())
        es = [_esito_cella_bb(r["riconosciuto"]) for r in G.BB["tabella_govuk"]]
        pf = G.prima_frase_bb()
        if f"in {es.count('si')} of the {len(es)} European countries" not in pf or f"{es.count('non_ue')} more accept non-EU parking cards" not in pf:
            errori.append(f"{idx}: conteggi della prima frase diversi dalla tabella GOV.UK")
        if f"<loc>{G.URL_SITO}/{G.BB_BASE}/</loc><lastmod>{G.BB['controllato_il']}</lastmod>" not in sm:
            errori.append(f"{idx}: non in sitemap o lastmod diverso")
        righe_html = re.findall(r'<tr data-voce id="([a-z]{2})">(.*?)</tr>', t)
        if [r[0] for r in righe_html] != [p["iso2"].lower() for p in G.BB_PAESI]:
            errori.append(f"{idx}: righe della tabella diverse dai Paesi dei dati")
        for (cod, r), p in zip(righe_html, G.BB_PAESI):
            conti["righe"] += 1
            celle = [unescape(re.sub(r"<[^>]+>", "", x)) for x in re.findall(r"<td[^>]*>(.*?)</td>", r)]
            if celle[1:3] != [righe[p["nome_gov"]]["riconosciuto"], righe[p["nome_gov"]]["info"] or "–"]:
                errori.append(f"{idx}: riga {cod} diversa dalla tabella GOV.UK: {celle}")
            if p["pagina"] != (f'href="../{G.url_bb(p)}"' in r):
                errori.append(f"{idx}: riga {cod} con o senza link alla pagina in modo diverso dai dati")
        faq_ok(idx, t, G.BB["faq_indice"], cit_numeri | {str(G.ANNO)})
        if f'href="../{G.PAT_BASE}/"' not in t:
            errori.append(f"{idx}: manca il link a Driving abroad")
    else:
        errori.append(f"indice {G.BB_BASE} mancante")
    # e) carte europee: prima frase, date della tabella tutte nelle citazioni
    rel = G.BB_CARTE + "index.html"
    if (SITO / rel).exists():
        t = leggi(rel)
        G_ = G.BB["generali"]
        ids = ["ec_when", "ec_gaps", "ec_replace"] + G_["carte_cosa"] + G_["carte_chi"] + G_["carte_parcheggio"] + G_["carte_pilota"] + G_["carte_poi"]
        vis, _ = comune(rel, t, list(dict.fromkeys(ids)), G.prima_frase_carte_bb())
        quando = G.BB_CIT["ec_when"]["x"]
        if "By 5 June 2027" not in quando or "from 5 June 2028" not in quando or "by 5 June 2027" not in G.prima_frase_carte_bb() or "from 5 June 2028" not in G.prima_frase_carte_bb():
            errori.append(f"{rel}: le date del 5/6/2027 e del 5/6/2028 non coincidono con la citazione della Commissione")
        testo_cit = " ".join(G.BB_CIT[i]["x"] for i in ids)
        for d_ in re.findall(r'<td data-l="When">(.*?)</td>', t):
            if unescape(d_) not in testo_cit:
                errori.append(f"{rel}: data della tabella non presente nelle citazioni: {d_}")
        faq_ok(rel, t, G.BB["faq_carte"], cit_numeri | {str(G.ANNO)})
        if f"<loc>{G.URL_SITO}/{G.BB_CARTE}</loc><lastmod>{G.BB['fonti']['ec_carte']['letto_il']}</lastmod>" not in sm:
            errori.append(f"{rel}: non in sitemap o lastmod diverso")
    else:
        errori.append(f"{rel} mancante")
    # f) collegamenti in entrata
    if f'href="{G.BB_BASE}/"' not in leggi("index.html"):
        errori.append("home senza link alla sezione Blue Badge")
    if f'id="{G.BB_BASE}"' not in leggi("about/index.html"):
        errori.append("About senza la sezione Blue Badge")
    if f'href="/{G.BB_BASE}/"' not in leggi("404.html"):
        errori.append("404 senza link alla sezione Blue Badge")
    if f'href="../{G.BB_BASE}/"' not in leggi(f"{G.PAT_BASE}/index.html"):
        errori.append(f"{G.PAT_BASE}/index.html: manca il link alla sezione Blue Badge")
    for nome in ("bluebadge.json", "bluebadge_manuali.json", "bluebadge_domanda.json"):
        if VIETATE_SRV.search((SITO.parent / "dati" / nome).read_text(encoding="utf-8")):
            errori.append(f"dati/{nome}: nome di un assistente di intelligenza artificiale")
    return errori, conti


# ---------------------------------------------------------------- 31. Amazon nel bagaglio a mano ed eSIM Roamable (6/11/2026)
# Scritti qui a mano, indipendenti da genera.py e da affiliati.json: tag Amazon per dominio, frase obbligatoria, link eSIM atteso.
AMAZON_TAG_ATTESI = {"www.amazon.co.uk": "beforeyoufly-21", "www.amazon.com": "beforeyoufl08-20"}
AMAZON_FRASE = "As an Amazon Associate we earn from qualifying purchases."
# mercato atteso per area della compagnia (pubblico della pagina)
AMAZON_MERCATO_AREA = {"Europe": {"www.amazon.co.uk"}, "North America": {"www.amazon.com"},
                       "Middle East and Australia": {"www.amazon.co.uk", "www.amazon.com"}}
ESIM_PARAMETRI = {"awinmid": "118127", "awinaffid": "3145171", "ued": "https://roamable.co/"}
# eSIM Awin del 9/11/2026 (accesi il 10/11): voce di affiliati.json -> parametri attesi del link e nome del fornitore in dati/esim.json
ESIM_ALTRI = {"esim_vodafone": ({"awinmid": "123870", "awinaffid": "3145171"}, "vodafone"),
              "esim_pocket": ({"awinmid": "131040", "awinaffid": "3145171"}, "pocket")}
ESIM_MINIMO_PAESI = 100
# cartelle dove il riquadro generico «Before you go» (eSIM) è ammesso: viaggi all'estero
ESIM_CARTELLE = ("passport-validity/", "canadian-passport/", "australian-passport/", "ees-etias/")
_RE_ASIN = re.compile(r"(/dp/|/gp/product|/gp/aw/d/|/exec/obidos|/o/ASIN|\bB0[A-Z0-9]{8}\b|[?&](asin|ASIN)=)")


def controlla_amazon_esim():
    from html import unescape
    from urllib.parse import parse_qs
    errori, c = [], {"amazon_pagine": 0, "amazon_link": 0, "uk": 0, "us": 0, "entrambi": 0, "esim_pagine": 0,
                     "esim_link": {"esim": 0, "esim_vodafone": 0, "esim_pocket": 0}, "esim_ordine": 0}
    attese = {f"{G.BAG_BASE}/index.html": None, f"{G.BAG_STRUMENTO}index.html": None}
    for C in G.COMPAGNIE:
        attese[f"{G.BAG_BASE}/{C['slug']}/index.html"] = C
    for sl, _ in G.MISURE_COMUNI:
        attese[f"{G.BAG_BASE}/size/{sl}/index.html"] = sl
    acceso = bool((G.AFFILIATI.get("bagagli") or {}).get("url"))
    esim = (G.AFFILIATI.get("esim") or {}).get("url") or ""
    if esim:
        u = urlparse(esim)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        if u.scheme != "https" or u.hostname != "www.awin1.com" or u.path != "/cread.php" or q != ESIM_PARAMETRI:
            errori.append(f"eSIM: link Awin diverso da quello atteso (awinmid 118127, awinaffid 3145171, ued https://roamable.co/): {esim}")
    link_esim = {esim: "esim"} if esim else {}
    for k, (par, forn) in ESIM_ALTRI.items():
        url = (G.AFFILIATI.get(k) or {}).get("url") or ""
        if not url:
            continue
        u = urlparse(url)
        q = {a: b[0] for a, b in parse_qs(u.query).items()}
        if u.scheme != "https" or u.hostname != "www.awin1.com" or u.path != "/cread.php" or q != par:
            errori.append(f"eSIM {k}: link Awin diverso da quello atteso ({par}): {url}")
        F = G.ESIM["fornitori"].get(forn)
        if not F or F.get("http") != 200 or len(F.get("paesi", {})) < ESIM_MINIMO_PAESI or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", F.get("letto_il") or "") \
                or F["letto_il"] > G.OGGI.isoformat() or (G.AFFILIATI[k].get("elenco") != forn):
            errori.append(f"eSIM {k}: elenco dei Paesi '{forn}' mancante o non valido in dati/esim.json (rilanciare raccolta/esim.py)")
        elif not set(F["paesi"]) <= set(G.PAESI_ISO):
            errori.append(f"eSIM {k}: codici non ISO nell'elenco '{forn}'")
        link_esim[url] = k
    pagine_esim = set()
    righe_esim = {}  # pagina -> [(voce, testo della riga)] nell'ordine della pagina
    for f in sorted(SITO.rglob("*.html")):
        rel = str(f.relative_to(SITO))
        t = f.read_text(encoding="utf-8", errors="replace")
        testo = G.MON.testo_visibile(t)
        n_amz, host_pagina, ricerche = 0, set(), []
        for m in re.finditer(r"<a\b[^>]*>", t):
            tag_a = m.group(0)
            href = unescape((re.search(r'href="([^"]*)"', tag_a) or [None, ""])[1])
            if not href.startswith(("http://", "https://", "//")):
                continue
            u = urlparse(href if not href.startswith("//") else "https:" + href)
            host = (u.hostname or "").lower()
            if href in link_esim:
                pagine_esim.add(rel)
                c["esim_link"][link_esim[href]] += 1
                if not {"sponsored", "noopener"} <= set((re.search(r'rel="([^"]*)"', tag_a) or [None, ""])[1].split()):
                    errori.append(f"{rel}: link eSIM senza rel=\"sponsored noopener\"")
                riga = re.search(r"</a>\s*<span class=\"small\">(.*?)</span>", t[m.end():m.end() + 1200], re.S)
                righe_esim.setdefault(rel, []).append((link_esim[href], unescape(riga.group(1)) if riga else ""))
            if not re.search(r"(^|\.)amazon\.[a-z.]+$", host) and not re.search(r"(^|\.)(amzn\.to|amzn\.eu|a\.co)$", host):
                continue
            n_amz += 1
            if host not in AMAZON_TAG_ATTESI:
                errori.append(f"{rel}: link Amazon verso un dominio non ammesso ({host}): solo www.amazon.co.uk e www.amazon.com")
                continue
            q = parse_qs(u.query)
            if u.scheme != "https" or u.path != "/s" or set(q) != {"k", "tag"} or len(q["tag"]) != 1:
                errori.append(f"{rel}: link Amazon che non è una ricerca /s?k=…&tag=… ({href[:90]})")
            elif q["tag"][0] != AMAZON_TAG_ATTESI[host]:
                errori.append(f"{rel}: link {host} con il tag {q['tag'][0]} invece di {AMAZON_TAG_ATTESI[host]}")
            if _RE_ASIN.search(href):
                errori.append(f"{rel}: link Amazon con un ASIN o una pagina prodotto ({href[:90]})")
            r = set((re.search(r'rel="([^"]*)"', tag_a) or [None, ""])[1].split())
            if not {"sponsored", "noopener"} <= r:
                errori.append(f"{rel}: link Amazon senza rel=\"sponsored noopener\"")
            host_pagina.add(host)
            ricerche.append((host, (q.get("k") or [""])[0]))
        if n_amz:
            c["amazon_pagine"] += 1
            c["amazon_link"] += n_amz
            if AMAZON_FRASE not in testo:
                errori.append(f"{rel}: link Amazon senza la frase «{AMAZON_FRASE}»")
            if rel not in attese:
                errori.append(f"{rel}: link Amazon fuori dalle pagine del bagaglio a mano")
                continue
        if rel not in attese or not acceso:
            continue
        if not n_amz:
            errori.append(f"{rel}: pagina del bagaglio a mano senza link Amazon (voce 'bagagli' accesa)")
            continue
        voce = attese[rel]
        if isinstance(voce, dict):  # pagina compagnia: mercato dall'area, ogni ricerca con una misura ufficiale della compagnia
            atteso = AMAZON_MERCATO_AREA.get(voce["area"], {"www.amazon.co.uk", "www.amazon.com"})
            misure = set()
            for b in voce["borse"]:
                misure.add("x".join(f"{round(x, 2):g}" for x in sorted(b["cm"], reverse=True)))
                if b.get("pollici") and b.get("pollici_ufficiali"):
                    misure.add("x".join(f"{round(x, 2):g}" for x in sorted(b["pollici"], reverse=True)))
            for h, k in ricerche:
                if k.split(" ")[0] not in misure:
                    errori.append(f"{rel}: ricerca Amazon «{k}» senza una misura ufficiale di {voce['nome']}")
        elif isinstance(voce, str):  # pagina per misura: solo .co.uk, con la misura dello slug
            atteso = {"www.amazon.co.uk"}
            for h, k in ricerche:
                if not k.startswith(voce + " "):
                    errori.append(f"{rel}: ricerca Amazon «{k}» senza la misura {voce}")
        else:  # indice e strumento: pubblico misto
            atteso = {"www.amazon.co.uk", "www.amazon.com"}
        if host_pagina != atteso:
            errori.append(f"{rel}: mercati Amazon {sorted(host_pagina)} invece di {sorted(atteso)}")
        c["entrambi" if len(atteso) == 2 else ("uk" if "www.amazon.co.uk" in atteso else "us")] += 1
    if acceso:
        priv = (SITO / "privacy.html").read_text(encoding="utf-8")
        if AMAZON_FRASE not in G.MON.testo_visibile(priv):
            errori.append(f"privacy.html: manca la frase «{AMAZON_FRASE}»")
    # eSIM (riquadro generico «Before you go»): solo nelle pagine dei viaggi all'estero, e in tutte quelle che hanno il riquadro
    for rel in sorted(pagine_esim):
        if not rel.startswith(ESIM_CARTELLE):
            errori.append(f"{rel}: link eSIM fuori dalle pagine dei viaggi all'estero (passaporti, EES/ETIAS)")
    if esim:
        for rel in ("passport-validity/index.html", "passport-validity/spain/index.html", "canadian-passport/index.html",
                    "australian-passport/index.html", "ees-etias/index.html"):
            if rel not in pagine_esim:
                errori.append(f"{rel}: riquadro eSIM mancante")
        for rel in ("index.html", "liquids/index.html", "liquids/malaga/index.html", f"{G.BAG_BASE}/index.html"):
            if rel in pagine_esim:
                errori.append(f"{rel}: riquadro eSIM in una pagina dove non c'entra")
    # eSIM: ordine e frasi dei tre fornitori ricalcolati qui da dati/esim.json (non dalle funzioni di genera.py)
    for rel, righe in sorted(righe_esim.items()):
        voci = [k for k, _ in righe]
        testi = dict(righe)
        if len(voci) != len(set(voci)):
            errori.append(f"{rel}: un fornitore eSIM ripetuto nel riquadro")
        destinazione = rel.count("/") == 2 and not rel.startswith("ees-etias/")
        for k, (_, forn) in ESIM_ALTRI.items():
            if k not in testi:
                continue
            F = G.ESIM["fornitori"].get(forn) or {}
            mm = re.search(r"list of destinations includes (.+?) \(checked on (.+?)\)\.", testi[k])
            if mm:
                if not destinazione:
                    errori.append(f"{rel}: frase «includes …» di {k} in una pagina senza destinazione")
                if mm.group(2) != G.data_lunga(F.get("letto_il", "")):
                    errori.append(f"{rel}: data di lettura dell'elenco {forn} diversa da dati/esim.json")
                nome = re.sub(r"^the ", "", mm.group(1))
                codici = {cc for cc, pp in G.PAESI_ISO.items() if nome in [pp["nome"]] + (pp.get("alias") or [])}
                if not codici & set(F.get("paesi", {})):
                    errori.append(f"{rel}: {k} dice che il suo elenco comprende {nome}, ma {nome} non è nell'elenco '{forn}' di dati/esim.json")
                if k == "esim_vodafone":
                    c["esim_ordine"] += 1
                    if voci[0] != "esim_vodafone":
                        errori.append(f"{rel}: Vodafone comprende la destinazione ma non è il primo del riquadro eSIM")
            elif destinazione and "check that your destination is on" not in testi[k].lower():
                errori.append(f"{rel}: riga {k} senza la frase sulla destinazione e senza il testo generico")
            elif not destinazione and "check that your destination is on" not in testi[k].lower():
                errori.append(f"{rel}: riga {k} senza il testo generico in una pagina senza destinazione")
        if not destinazione and voci and voci[0] != "esim":
            errori.append(f"{rel}: in una pagina senza destinazione il riquadro eSIM deve iniziare con Roamable")
        if destinazione and "esim_vodafone" in voci and voci[0] != "esim_vodafone" and "includes" in testi["esim_vodafone"]:
            errori.append(f"{rel}: Vodafone non è il primo")
    # ogni pagina destinazione: fornitori e ordine attesi ricalcolati qui (Vodafone primo se l'elenco comprende il Paese, assente se non lo
    # comprende; poi Roamable; Pocket solo se il suo elenco lo comprende; destinazione senza codice ISO: Roamable, Vodafone, Pocket)
    accese = [k for k in ("esim", "esim_vodafone", "esim_pocket") if (G.AFFILIATI.get(k) or {}).get("url")]
    el = {k: set((G.ESIM["fornitori"].get(f) or {}).get("paesi", {})) for k, (_, f) in ESIM_ALTRI.items()}
    dest = [(f"passport-validity/{P['slug']}/index.html", G.iso_destinazione(P["nome"], P["url"])) for P in G.PAESI]
    for k in G.ESTERI:
        for v in G.VOCI[k]:
            dest.append((v["url_pag"] + "index.html", v["p"].get("iso") or G.iso_destinazione(v["nome"], v["p"].get("url", ""))))
    c["esim_senza_iso"] = 0
    for rel, iso in dest:
        if iso:
            attese = [k for k in ("esim_vodafone", "esim", "esim_pocket") if k in accese and (k == "esim" or iso in el[k])]
        else:
            c["esim_senza_iso"] += 1
            attese = [k for k in ("esim", "esim_vodafone", "esim_pocket") if k in accese]
        trovate = [k for k, _ in righe_esim.get(rel, [])]
        if trovate != attese:
            errori.append(f"{rel}: fornitori eSIM {trovate} invece di {attese} (ricalcolati da dati/esim.json, Paese {iso})")
    c["esim_pagine"] = len(pagine_esim)
    return errori, c


def main():
    e1 = controlla_casi()
    print(f"1. Casi del passaporto calcolati a mano: {len(CASI)}, {len(e1)} errori")
    e2 = controlla_js(casi_casuali())
    print(f"2. Motore JS contro Python: {len(e2)} differenze (3.000 casi casuali + {len(CASI)} casi a mano)")
    e3, n = controlla_link()
    print(f"3. Link interni: {n} pagine, {len(e3)} link rotti")
    e4 = controlla_fonti()
    print(f"4. Fonti, date e citazioni nelle pagine: {len(G.PAESI)} paesi, {len(G.AER['aeroporti']) + len(G.AER['nazionali'])} pagine liquidi, EES/ETIAS: {len(e4)} errori")
    e5 = controlla_struttura()
    print(f"5. Struttura (meta Google, canonical, 404, sitemap, robots, netlify.toml): {len(e5)} errori")
    e6 = controlla_parole()
    print(f"6. Parole vietate: {len(e6)}")
    e7, info = controlla_browser()
    if info:
        o, cartella = info
        n375 = sum(1 for x in o["pagine"] if x["tema"] in ("light", "dark"))
        print(f"7. Browser 375 px: {len(o['pagine'])} viste ({n375 // 2} pagine × tema chiaro e scuro + {len(o['pagine']) - n375} a 820 px; nuove: "
              f"{', '.join(PAGINE_ESTERE_BROWSER + PAGINE_BAG_BROWSER + PAGINE_IT_BROWSER + PAGINE_SRV_BROWSER + PAGINE_PAT_BROWSER + PAGINE_PED_BROWSER + PAGINE_GOM_BROWSER + PAGINE_FL_BROWSER + PAGINE_TR_BROWSER + PAGINE_TB_BROWSER + PAGINE_SC_BROWSER + PAGINE_BB_BROWSER)}; {len(CASI_BORSA)} casi dello strumento borsa), "
              f"{len(o['prove'])} prove, {len(e7)} errori; schermate in {cartella}")
    else:
        print(f"7. Browser 375 px: {e7[0] if e7 else ''}")
    e8, (con, solo, senza) = controlla_visti()
    print(f"8. Visti: {con} riassunti da schema riconosciuto, {solo} solo citazione, {senza} senza sezione visti: {len(e8)} errori")
    e9, (n_faq, n_cit, n_nostre) = controlla_liquidi_nuovi()
    print(f"9. Liquidi: risposta diretta e frase diretta su {len(G.AER['aeroporti']) + len(G.AER['nazionali'])} pagine; {n_faq} risposte FAQ "
          f"({n_cit} blocchi di citazioni ufficiali intere, {n_nostre} frasi nostre da regola/sintesi o modelli fissi): {len(e9)} errori")
    e10, lunghi = controlla_meta()
    print(f"10. Titoli <= 65 e descrizioni <= 160: {len(e10)} errori" + (f"; titoli più lunghi senza alternativa più corta prevista: {lunghi}" if lunghi else ""))
    e11, conti = controlla_esteri()
    for k, c in conti.items():
        print(f"11. Passaporto {G.ESTERI[k]['agg']}: {c['pagine']} pagine; validità {c['val']} riassunti, {c['val_cit']} solo citazione; "
              f"visto {c['vis']} riassunti, {c['vis_cit']} solo citazione")
    print(f"11. Passaporti canadese e australiano (riassunti ricalcolati, modelli fissi, citazioni, fonti, licenze, link): {len(e11)} errori")
    e12, cb = controlla_bagagli()
    e12 += controlla_js_borsa()
    print(f"12. Bagaglio a mano: {cb['compagnie']} compagnie, {cb['misure']} misure, {cb['citazioni']} citazioni, {cb['faq']} risposte FAQ, "
          f"{len(G.MISURE_COMUNI)} pagine per misura, motore JS e rotazioni, pagina UE, affiliati solo ammessi: {len(e12)} errori")
    e13, ci = controlla_italiani()
    print(f"13. Documenti per italiani: {ci['pagine']} pagine Paese ({ci['senza']} schede senza pagina); riassunti: documento {ci['doc']}, validità {ci['val']}, "
          f"visto {ci['vis']} ({ci['manuali']} fatti scritti a mano); {ci['citazioni']} citazioni controllate sul campo della scheda; {ci['faq']} risposte FAQ; "
          f"testo uguale alla fonte al massimo {ci['copia_max']} parole di fila (limite {MAX_COPIA}): {len(e13)} errori")
    e14, c14 = controlla_liquidi_2110()
    print(f"14. Liquidi 21/10: {c14['faq_ld']} blocchi FAQPage validi in tutto il sito; titoli e H1 con la regola su {len(G.AER['aeroporti'])} aeroporti; "
          f"{c14['nuovi']} aeroporti nuovi (dati, indice, pagine), esclusi con il motivo; riquadro liquidi in {c14['compagnie']} pagine compagnie: {len(e14)} errori")
    e15, n15 = controlla_altri_siti()
    print(f"15. Blocco \"Other useful tools for your trip\" ({len(G.ALTRI_SITI)} link, {len(G.ALTRI_SITI_IT)} nelle pagine italiane) in {n15} pagine indicizzabili: {len(e15)} errori")
    e16 = controlla_indexnow()
    print(f"16. File chiave IndexNow {G.CHIAVE_INDEXNOW}.txt in sito/ (contenuto giusto, fuori dalla sitemap): {len(e16)} errori")
    e17, c17 = controlla_servizi()
    print(f"17. Available in?: {c17['servizi']} servizi, {c17['righe']} righe di tabella uguali ai dati, {c17['pagine']} pagine servizio × Paese "
          f"(solo coppie con ricerche vere), {c17['faq']} risposte FAQ, {c17['citazioni']} citazioni; liste ricalcolate dalla cache: {c17['cache']}; "
          f"sitemap con lastmod della lettura, nessun nome di assistente né consiglio per aggirare: {len(e17)} errori")
    e18, c18 = controlla_patenti()
    print(f"18. Driving abroad: {c18['paesi']} Paesi, {c18['voci']} voci Paese × patente ({c18['manuali']} fatti scritti a mano), ricalcolo dai grezzi: {c18['cache']}; "
          f"{c18['righe']} righe delle tabelle per patente uguali ai dati; {c18['pagine']} pagine Paese × patente (solo coppie cercate), {c18['citazioni']} frasi ufficiali "
          f"nelle pagine, {c18['faq']} risposte FAQ; titoli <= {G.LIMITE_TITOLO_PAT}, sitemap con lastmod della lettura, riquadro DiscoverCars (a_aid, dopo le regole) in {c18['noleggio']} pagine della sezione + home, {c18['avvisi_idp']} avvisi evidenti sul permesso; nessun altro noleggio né nome di assistente: {len(e18)} errori")
    e20, c20 = controlla_pedaggi()
    print(f"20. Tolls with a rental car: {c20['paesi']} Paesi, {c20['fonti']} fonti ufficiali (HTTP 200, domini ammessi; frasi e impronte ricalcolate dal testo salvato: {c20['cache']}), "
          f"{c20['citazioni']} citazioni e {c20['prezzi']} prezzi nelle pagine (numeri solo dalle fonti), {c20['faq']} risposte FAQ da ricerche vere (JSON-LD = testo visibile), "
          f"titoli <= {G.LIMITE_TITOLO_PED} con l'anno, sitemap con lastmod della lettura, riquadro DiscoverCars (a_aid, dopo le regole) in {c20['noleggio']} pagine, "
          f"{c20['link_guida']} link andata e ritorno con Driving abroad; Croazia: caselli fino al 28/2/2027 e pedaggio senza caselli dal 1/3/2027 con "
          f"{c20['croazia_2027']} fonti (legge NN 156/2025 citata con la data, Crolibertas), traduzioni, riquadro con data non scaduta, frase sul noleggio; "
          f"nessun altro noleggio né nome di assistente: {len(e20)} errori")
    e21, c21 = controlla_gomme()
    print(f"21. Winter tyres with a rental car: {c21['paesi']} Paesi, {c21['pagine']} pagine Paese (solo con ricerche vere), {c21['fonti']} fonti ufficiali "
          f"(HTTP 200, domini ammessi; frasi e impronte ricalcolate dal testo salvato: {c21['cache']}), {c21['citazioni']} citazioni con traduzione se non in inglese, "
          f"{c21['faq']} risposte FAQ da ricerche vere (JSON-LD = testo visibile), titoli <= {G.LIMITE_TITOLO_GOM} con la stagione {G.STAGIONE_GOM}, numeri solo dalle fonti, "
          f"frase sul noleggio, riquadro DiscoverCars (a_aid, dopo le regole) in {c21['noleggio']} pagine, {c21['link']} link andata e ritorno con Driving abroad e Tolls: {len(e21)} errori")
    e22, c22 = controlla_biglietti()
    print(f"22. Ticket release dates: {c22['attrazioni']} attrazioni, {c22['fonti']} fonti ufficiali (HTTP 200, domini ammessi; frasi e impronte ricalcolate dal testo salvato: {c22['cache']}), "
          f"{c22['citazioni']} citazioni nelle pagine, {c22['date']} date calcolate uguali al ricalcolo indipendente e coerenti con la regola (settimanale, mensile, "
          f"date della tabella, anticipo; ore e giorni presenti nella frase ufficiale, {c22.get('esempi', 0)} esempi ufficiali coerenti con la regola, ora a New York/Londra ricalcolata), "
          f"{c22.get('escluse_provate', 0)} attrazioni escluse con motivo coerente con la rilettura, {c22['eventi_ics']} eventi .ics validi "
          f"(CRLF, righe <= 75 byte, UID unici, date e ore = tabella), {c22['faq']} risposte FAQ da ricerche vere (JSON-LD = testo visibile), titoli <= {G.LIMITE_TITOLO_BIG} con gli anni {G.STAGIONE_BIG}, "
          f"pagine in sitemap, {c22['link_esterni']} link esterni tutti ufficiali, nessun rivenditore, riquadro Viator {'acceso' if G.VIATOR_TOUR else 'spento'}, "
          f"{c22.get('stay22', 0)} link Stay22 (ognuno solo sulla sua pagina e nell'indice, sponsored, dopo la biglietteria ufficiale): {len(e22)} errori")
    e23, c23 = controlla_patente_straniera()
    print(f"23. Foreign licence Canada/Australia/NZ: {c23['giur']} giurisdizioni ({c23['lette']} lette, {c23['bloccate']} pagine ufficiali che non si aprono, "
          f"nessuna regola scritta per quelle), {c23['pagine']} pagine (nessuna pagina patente × destinazione), {c23['fonti']} fonti ufficiali (HTTP 200, domini ammessi; "
          f"frasi e impronte ricalcolate dal testo salvato: {c23['cache']}), {c23['citazioni']} citazioni, numeri solo dalle fonti, {c23['faq']} risposte FAQ da ricerche vere "
          f"(JSON-LD = testo visibile), titoli <= {G.LIMITE_TITOLO_FL} con l'anno, sitemap con lastmod della lettura, riquadro DiscoverCars (a_aid, dopo le regole) in "
          f"{c23['noleggio']} pagine, {c23['link']} link dalle pagine Driving abroad: {len(e23)} errori")
    e24, c24 = controlla_trasporti()
    print(f"24. Public transport rules: {c24['citta']} città ({c24['lette']} lette, {c24['non_lette']} non lette senza dati né pagina), {c24['pagine']} pagine città, "
          f"{c24['fonti']} fonti ufficiali (HTTP 200, domini ammessi; citazioni parola per parola e impronte ricalcolate dalla copia salvata: {c24['cache']}), "
          f"{c24['citazioni']} citazioni nelle pagine, numeri solo dalle fonti, {c24['faq']} risposte FAQ da ricerche vere (JSON-LD = testo visibile), "
          f"titoli <= {G.LIMITE_TITOLO_TR} con l'anno, sitemap con lastmod della lettura, nessun link di affiliazione, {c24['link']} link da Driving abroad "
          f"e ticket-release-dates: {len(e24)} errori")
    e25, c25 = controlla_treni_bagagli()
    print(f"25. Train luggage rules + Eurostar check-in: {c25['compagnie']} compagnie ({c25['lette']} lette, {c25['non_lette']} non lette senza dati né pagina), "
          f"{c25['pagine']} pagine, {c25['fonti']} fonti ufficiali (HTTP 200, domini ammessi; citazioni parola per parola, {c25['stazioni']} righe "
          f"della tabella Eurostar e impronte ricalcolate dalla copia salvata: {c25['cache']}), {c25['citazioni']} citazioni nelle pagine, numeri "
          f"solo dalle fonti, {c25['faq']} risposte FAQ da ricerche vere (JSON-LD = testo visibile), titoli <= {G.LIMITE_TITOLO_TB} con l'anno, "
          f"sitemap con lastmod della lettura, nessun link di affiliazione, {c25['link']} link in entrata: {len(e25)} errori")
    e26, c26 = controlla_animali()
    print(f"26. Pets UK to EU: {c26['fonti']} fonti ufficiali (GOV.UK e Commissione, HTTP 200; frasi, impronte, tabelle delle rotte e link per Paese ricalcolati "
          f"dalla copia salvata: {c26['cache']}), {c26['pagine']} pagine (indice, calcolatore, passaporto 2027, rotte, {c26['paesi']} Paesi con ricerche vere), "
          f"{c26['citazioni']} paragrafi citati tutti uguali ai dati, prima frase con fonte e data, numeri solo dalle citazioni, {c26['faq']} risposte FAQ da "
          f"ricerche vere (JSON-LD = testo visibile), verme solitario = lista di GOV.UK, {c26['righe_rotte']} righe di rotte = tabelle GOV.UK, "
          f"calcolatore: {c26['casi']} casi a mano e {c26['js']} casi JS = Python, browser: {c26['browser']}; {c26['link']} link andata e ritorno con "
          f"Driving abroad e Tolls; nessun consiglio veterinario, nessuna affiliazione, data del passaporto 2027 non scaduta: {len(e26)} errori")
    e27, c27 = controlla_india()
    print(f"27. India e-Visa fee: {c27['fonti']} fonti ufficiali (indianvisaonline.gov.in e boi.gov.in, HTTP 200; PDF salvati con la stessa impronta, "
          f"citazioni e elenchi dei porti parola per parola nel testo salvato), seconda lettura indipendente dei PDF ({c27['metodo']}): "
          f"{c27['righe_tv']} righe e-Tourist e {c27['righe_altri']} righe e-Business/e-Medical = dati, {c27['valori']} valori uguali, {c27['paesi']} Paesi; "
          f"{c27['pagine']} pagine ({c27['nazionalita']} nazionalità solo con ricerche vere, tedesco e francese con ricerche vere), tabelle nelle pagine = PDF, "
          f"prima frase con fonte e data, avviso sul sito ufficiale in alto, solo link ufficiali o SafetyWing sponsorizzato, nessun rivenditore di visti, "
          f"{c27['citazioni']} citazioni <= {RIN.MAX_PAROLE} parole tutte nei dati, {c27['faq']} risposte FAQ (JSON-LD = testo visibile), titoli <= {G.LIMITE_TITOLO_IN}, "
          f"sitemap con lastmod, {c27['link']} link in entrata; browser: {c27['browser']}: {len(e27)} errori")
    e28, c28 = controlla_scooter()
    print(f"28. Scooter rental licence: {c28['paesi']} Paesi con pagina ({c28['pagine']} pagine + indice), {c28['non_letti']} Paesi non letti (motivo "
          f"coerente con la rilettura: HTTP e frasi con la regola), {c28['fonti']} fonti ufficiali (HTTP 200, domini ammessi; frasi e impronte "
          f"ricalcolate dal testo salvato: {c28['cache']}), {c28['citazioni']} citazioni e {c28['traduzioni']} traduzioni nelle pagine, numeri solo "
          f"dalle fonti, esiti con citazione, prima frase con fonte e data, {c28['faq']} risposte FAQ da ricerche vere (JSON-LD = testo visibile), "
          f"titoli <= {G.LIMITE_TITOLO_SC} con l'anno, {c28['link']} link andata e ritorno con Driving abroad, nessuna affiliazione né promessa: {len(e28)} errori")
    e29, c29 = controlla_bluebadge()
    print(f"29. Blue Badge abroad: {c29['paesi']} Paesi della tabella GOV.UK ({c29['righe']} righe dell'indice = tabella ricalcolata dalla copia salvata, "
          f"esiti = celle lette in modo indipendente), {c29['pagine']} pagine Paese (solo con ricerche vere) + indice + carte europee, {c29['fonti']} fonti "
          f"ufficiali (GOV.UK, FCDO, Your Europe, Commissione, governi italiano e francese; HTTP 200, impronte e citazioni ricalcolate dalla copia salvata: "
          f"{c29['cache']}), {c29['citazioni']} citazioni e {c29['traduzioni']} traduzioni nelle pagine, numeri solo dalle fonti, prima frase con fonte e data, "
          f"{c29['faq']} risposte FAQ da ricerche vere (JSON-LD = testo visibile), titoli <= {G.LIMITE_TITOLO_BB} con l'anno, nessun link FIA né affiliazione, "
          f"{c29['link']} link andata e ritorno con Driving abroad: {len(e29)} errori")
    e30, c30 = controlla_liquidi_0511()
    print(f"30. Liquidi 5/11: {c30['nuovi']} aeroporti nuovi su {len(NUOVI_LIQ_0511)} (lettura diretta, HTTP 200, impronta, indice, sitemap, titolo da "
          f"ricerche vere, fonte accanto alla risposta), esclusi del 5/11 con il motivo; riquadro 'Hire a car at' (DiscoverCars) su {c30['noleggio']} "
          f"pagine di vacanza, 'Where to stay' (Stay22) su {c30['stay22']}, nessun riquadro su {c30['senza']} pagine di partenza (UK, Irlanda, "
          f"isole della Manica, USA, Canada): {len(e30)} errori")
    e31, c31 = controlla_amazon_esim()
    print(f"31. Amazon ed eSIM: {c31['amazon_link']} link Amazon in {c31['amazon_pagine']} pagine del bagaglio a mano (solo .co.uk: {c31['uk']}, "
          f"solo .com: {c31['us']}, entrambi: {c31['entrambi']}), tag giusto per dominio, solo ricerche /s senza ASIN, misura della pagina, "
          f"frase di Amazon nelle pagine e nella privacy; eSIM (Awin) in {c31['esim_pagine']} pagine di viaggi all'estero, link Roamable "
          f"{c31['esim_link']['esim']}, Vodafone {c31['esim_link']['esim_vodafone']}, Pocket {c31['esim_link']['esim_pocket']}; Vodafone primo "
          f"(elenco con la destinazione) in {c31['esim_ordine']} pagine, ordine e presenza ricalcolati da dati/esim.json, {c31.get('esim_senza_iso', 0)} "
          f"destinazioni senza codice ISO (testo generico): {len(e31)} errori")
    e19, i19 = G.MON.controlla_sito(G.SITO_ID, SITO)  # controllo comune di monetizzazione (monetizzazione.py)
    print("19. " + G.MON.riepilogo(G.SITO_ID, i19, e19))
    tutti = e1 + e2 + e3 + e4 + e5 + e6 + (e7 if info else []) + e8 + e9 + e10 + e11 + e12 + e13 + e14 + e15 + e16 + e17 + e18 + e19 + e20 + e21 + e22 + e23 + e24 + e25 + e26 + e27 + e28 + e29 + e30 + e31
    if AVVISI:  # ricalcoli dalle copie salvati saltati (copia mancante, pagina di blocco, raccolta che non ha aggiornato il JSON): non sono errori
        per_punto = {}
        for k, _ in AVVISI:
            per_punto[k] = per_punto.get(k, 0) + 1
        print(f"AVVISI: {len(AVVISI)} (" + ", ".join(f"punto {k}: {n}" for k, n in sorted(per_punto.items(), key=lambda x: int(x[0]))) +
              "); ricalcoli dalle copie saltati, tutti gli altri controlli fatti:")
        for k, a in AVVISI:
            print(f" ~ [{k}] {a}")
    for e in tutti:
        print(" -", e)
    if tutti:
        sys.exit(1)
    print("TUTTO OK" + (f" (con {len(AVVISI)} avvisi)" if AVVISI else ""))


if __name__ == "__main__":
    main()
