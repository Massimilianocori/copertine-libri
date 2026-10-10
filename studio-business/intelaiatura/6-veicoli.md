# Intelaiatura – Veicoli: antismog, mezzi pesanti, targhe, Motorizzazione, open data

Data della ricerca: 10 ottobre 2026. Autore: Claude (sessione di ricerca per Massimiliano Cori).
Domanda di Massimiliano: "si può fare qualcosa con i veicoli? motorizzazione civile, targhe".
Metodo: quello di `5-opportunita-grandi.md` (filtro duro per primo: dati da ≤20 fonti ufficiali strutturate, raggiungibili da script, copertura ≥90%; poi le 5 condizioni), con le lezioni di `posteggi-test-tecnico.md` (copertura ~1% dai BUR, estrazione a regole 55–65%) e `affidamenti-test-tecnico.md` (copertura reale 33%, domanda 0/30 nei Comuni medi). Esclusioni già decise e qui applicate: niente dati sparsi su migliaia di siti comunali, niente dati personali (intestatari di targhe).
Regola: ogni affermazione porta fonte linkata e datata; ogni HTTP status è stato misurato dal server con `curl` (User-Agent browser) il 10/10/2026. Le cifre di ricavo sono stime con assunzioni esplicite. **Un NO documentato vale quanto un sì.**

## 0. Esito in breve

| Direzione | Filtro duro | Cond. 1 (si paga già) | 3 (domanda + vuoto) | 4 (due parti) | 5 (zero lavoro/responsabilità) | 12 mesi | 18 mesi (run-rate) |
|---|---|---|---|---|---|---|---|
| **1. Antismog: "posso circolare oggi con la mia Euro X a Y"** | **PASSA con test** (5 fonti per il "semaforo" di oggi, 3 sono app JS; regole in ~25 atti regionali/comunali + 1 PDF UNRAE) | PARZIALE (consumer no: gli avvisi ufficiali sono gratis; flotte sì in Europa, prezzi non pubblici) | **SÌ** (domanda enorme: 16/16 città con "oggi/domani"; SERP = testate, nessun aggregatore "oggi per città") | DEBOLE | SÌ con cautela (multa 168 € se la pagina sbaglia) | 1.000–2.500 € | 3.000–6.000 €/anno |
| 2. Calendario divieti mezzi pesanti | PASSA (1 decreto) | NO (si paga per software gestionali, non per il calendario) | NO (MIT, Polizia, Certifico, Ingenio, FleetMagazine, SicurAuto, ANCE, app gratuite, nakordoni per 16 Paesi) | NO | SÌ | 0–500 € | ≤1.000 € |
| 3. Verifica targa (revisione/bollo/RC/classe) | **NON PASSA** (nessun dataset: solo interrogazione per singola targa, dato personale) | SÌ (carVertical 29,99 €) ma mercato occupato | NO (il Portale dell'Automobilista ha i motori gratuiti) | NO | **NO** (dati personali) | – | – |
| 4. Motorizzazione (esami patente, istruttori, revisioni, storiche) | NON PASSA (calendari esami: PDF mensili per ~100 uffici; istruttori: 100 Province) / motori ufficiali (centri revisione) | NO | debole | NO | – | – | – |
| 5. Open data (PUN colonnine, autovelox, parco ACI, ISTAT, ZTL) | PUN: app ArcGIS senza API/CSV trovati; autovelox: 1 fonte già ripubblicata ogni settimana; ACI/ISTAT: statistiche; ZTL: migliaia di Comuni | NO | NO (PlugShare/Nextcharge/Google Maps; Waze/Radarbot/auto.it) | NO | – | – | – |

**VERDETTO NETTO**: nessuna direzione "veicoli" supera tutte le condizioni con una stima prudente ≥10.000 €/anno entro 18 mesi. **L'unica che merita un test tecnico è la 1 (antismog)**: è l'unica con fonti ≤20 e domanda enorme e stagionale con SERP senza aggregatore "oggi"; ma è un **sito da 3–6k l'anno**, consumer, con pubblico che non paga (gli enti mandano già avvisi gratuiti) e con una responsabilità da gestire (la risposta "puoi circolare" vale una multa). Le altre quattro falliscono il filtro duro o la condizione 3 con prove. Test in sez. 7.

---

## 1. Metodo, strumenti, limiti

- **Strumenti**: `curl` dal server (status, content-type, byte, `Last-Modified`), lettura dei sorgenti delle app JS per cercare endpoint dati, Google Autocomplete (`suggestqueries.google.com`, hl=it/gl=it, 130 query: 57 sull'antismog con 422 proposte, 73 sulle altre direzioni con 516 proposte; file in `dati-6-veicoli/`), ricerca web per SERP, prezzi e concorrenti, lettura di PDF (`pdftotext`).
- **Limiti dichiarati**: nessun Keyword Planner/Semrush; la SERP è letta tramite ricerca web da server USA e non dalla Google italiana di Massimiliano (la composizione per tipo di sito è però netta). **Dal nostro proxy non rispondono**: `mit.gov.it` (000, anche con WebFetch: DNS), `regione.piemonte.it` per alcune pagine (000/reset), `movein.regione.piemonte.it` e `movein.regione.emilia-romagna.it` (000), `opendata.aci.it` (502), `dgtsud.it` (certificato TLS non valido); `nakordoni.eu` e `fleetmagazine.com` rispondono 403 (anti-bot). Dal computer di Massimiliano tutto è raggiungibile normalmente.
- Nessuna pagina è stata costruita; nessun dato personale raccolto.

---

## 2. Direzione 1 – Limitazioni antismog e blocchi del traffico per città e classe Euro

### 2.1 Come funziona (per capire quante fonti servono)

Il fenomeno ha due strati:
1. **Regole strutturali** (valide tutto l'inverno o tutto l'anno): decise da **delibere regionali** nel Bacino Padano e da ordinanze comunali altrove. Esempio Torino: dal 15/9/2026 al 15/4/2027, livello 0 (verde): diesel Euro 3 e 4 fermi nei feriali 8–19; livello 1 (arancio): diesel Euro 3, 4 e 5 fermi tutti i giorni 8–19 ([Città di Torino, Ordinanza 2537/2025, pagina 200](https://www.comune.torino.it/schede-informative/misure-antismog-tutela-della-salute)). Roma Fascia Verde: permanenti benzina fino a Euro 2 e diesel fino a Euro 3; livello arancio aggiunge benzina Euro 3 e diesel Euro 4; livello rosso aggiunge diesel Euro 5 e 6 dalle 7.30 alle 20.30 ([Roma Mobilità, Delibera 371/2022 e Ordinanza 145/2025, 200](https://romamobilita.it/it/servizi/ztl/fascia-verde)).
2. **Il "semaforo" giornaliero** (livello 0/1/2 per comune o provincia) emesso dalle ARPA regionali nei giorni di controllo, che fa scattare le misure emergenziali dal giorno dopo. È il dato per cui esiste la domanda "oggi/domani".

Il **blocco strutturale nazionale dei diesel Euro 5** (art. 51 DL 183/2020, Bacino Padano) è stato rinviato dal Consiglio dei ministri al **1° ottobre 2027** ([Sky TG24, 25/9/2026](https://tg24.sky.it/motori/2026/09/25/blocco-diesel-euro-5-rinvio-2027); [HDmotori, 27/9/2026](https://www.hdmotori.it/focus/mercato/normative/blocco-diesel-euro-5-rinviato-2027/); [L'Automobile ACI](https://www.lautomobile.aci.it/attualita/diesel-euro-5-niente-blocco-in-lombardia-cosa-cambia-dal-1-ottobre/)); restano le limitazioni regionali e comunali già in vigore. Le testate si contraddicono tra loro sulla Lombardia ([SicurAuto 22/9/2026](https://www.sicurauto.it/news/attualita-e-curiosita/stop-diesel-euro-5-in-lombardia-la-situazione-a-pochi-giorni-dal-1-ottobre/) contro [Il Giorno 17/9/2026](https://www.ilgiorno.it/politica/blocco-diesel-euro-5-1-ottobre-igtvfkis)): è esattamente la confusione che alimenta la domanda. Parco interessato: **3,7 milioni di diesel Euro 5 in Italia (8,8%)**, di cui 484.000 in Lombardia, 340.000 in Veneto, 368.000 in Emilia-Romagna, 236.000 in Piemonte ([Il Post, 9/7/2025, dati ACI](https://www.ilpost.it/2025/07/09/quante-sono-auto-euro-5/)).

### 2.2 Le fonti ufficiali (verificate il 10/10/2026)

| Fonte | Cosa dà | URL | HTTP / formato | Frequenza | API/feed |
|---|---|---|---|---|---|
| **ARPAE Emilia-Romagna – Bollettino Liberiamo l'aria** | misure emergenziali (bollino rosso) per provincia; stato corrente in chiaro ("Nessuna misura emergenziale – Misure strutturali"); archivio stagionale | [bollettino](https://www.arpae.it/it/temi-ambientali/aria/liberiamo-laria/bollettino-misure-emergenziali) | **200, HTML leggibile** (ultima modifica 29/9/2026); [archivio 200](https://www.arpae.it/it/temi-ambientali/aria/liberiamo-laria/bollettino-misure-emergenziali/archivio-bollettini-emergenziali) | lun/mer/ven entro le 11, da ottobre a marzo; il primo bollettino il 30/9 | no feed, ma HTML stabile |
| **ARPAE – Limitazioni per comune** | ordinanze comunali raccolte dall'ARPA: **20 pagine-comune per la stagione 2026-2027** già online (Carpi, Castenaso, Cento, Ferrara, Forlì, Formigine, Imola, Lugo…) + comuni di pianura + ordinanze Move-In | [ordinanze 2026-2027](https://www.arpae.it/it/temi-ambientali/aria/liberiamo-laria/limitazioni-per-comune/ordinanze-2026-2027) | 200, HTML + PDF | annuale | – |
| **ARPAV Veneto – Bollettino livelli di allerta PM10** | livello verde/arancio/rosso **per ciascun comune** della regione (esclusa zona Prealpi e Alpi), 1/10–30/4 | [bollettino](https://www.arpa.veneto.it/dati-ambientali/bollettini/aria/bollettino-livelli-di-allerta-pm10) | 200, HTML 250 KB; **la tabella è caricata da JS (React)**: nell'HTML statico c'è "Nessun dato disponibile"; [tabella corrispondenza aree-comuni PDF](https://www.arpa.veneto.it/temi-ambientali/aria/file-e-allegati/tabella-corrispondenza-aree_comuni.pdf/@@download/file) | lun/mer/ven | **iscrizione email ufficiale ai bollettini** ([200](https://www.arpa.veneto.it/servizi/iscrizione-bollettini-e-servizi)) |
| **ARPA Piemonte – semaforo antismog** (76 comuni: agglomerato di Torino + comuni >10.000 ab. di Pianura e Collina, 15/9–15/4; controlli lun/mer/ven) | livello per comune, oggi e domani | [aria.ambiente.piemonte.it/semaforo](https://aria.ambiente.piemonte.it/semaforo) (200, 4 KB: app Vue); [webgis.arpa.piemonte.it/aria_piemonte](https://webgis.arpa.piemonte.it/aria_piemonte/) (200, app Angular, "Limitazioni livello 1/2"); [protocollo operativo ARPA, PDF 1,4 MB](https://www.arpa.piemonte.it/media/8230) | app JS: nei bundle ho trovato solo i servizi delle centraline (`ariaweb/awws/airdbService`) e il WFS `geomap.reteunitaria.piemonte.it` (200, layer "Aggregazioni" e "Modellistica", **nessun layer semaforo**); l'endpoint del semaforo non è emerso | lun/mer/ven | nessuno trovato: serve headless o ispezione di rete dal browser |
| **Regione Lombardia – misure temporanee** (d.G.R. 5613 del 12/1/2026: livello 1 dopo 2 giorni di superamento, livello 2 dopo 7; controlli lun/gio; traffico limitato nei comuni >30.000 ab.) | regole + stato di attivazione per provincia | [pagina regionale 200](https://www.regione.lombardia.it/ambiente-e-territorio/qualita-dell-aria/red-misure-temporanee-per-miglioramento-qualita-aria), [DGR 5613 PDF](https://www.regione.lombardia.it/content/dam/rl/canali-tematici-servizi/06-ambiente-e-territorio/20-qualita-dell-aria/red-misure-temporanee-per-migliorare-qualita-aria/allegati/DGR%205613%20del%2012%20genn%202026.pdf); **INFOARIA** [stato attivazione](https://www.infoaria.regione.lombardia.it/infoaria/#/stato-attivazione) (200, app Angular; 3 endpoint ipotizzati → 404; `getFile/3` = PDF 264 KB) | app JS | lun/gio | **INFOARIA ha un servizio di notifiche previa registrazione** (dichiarato nella pagina regionale) |
| Milano Area B | regole per classe, "verifica targa" ufficiale | [200](https://www.comune.milano.it/argomenti/mobilita/area-b) | HTML | – | motore ufficiale |
| Move-In (Lombardia; attivo anche Piemonte, Veneto, Emilia-Romagna) | deroghe chilometriche | [200](https://www.movein.regione.lombardia.it/movein/) | HTML | – | – |
| **Roma – ZTL Fascia Verde** | regole permanenti + livello arancio/rosso | [Roma Mobilità 200](https://romamobilita.it/it/servizi/ztl/fascia-verde) | HTML leggibile | il livello è dichiarato da Roma Capitale su dati ARPA Lazio ([arpalazio.it 200](https://www.arpalazio.it/)) | – |
| Torino | ordinanza 2537/2025 con tabella livelli | [200](https://www.comune.torino.it/schede-informative/misure-antismog-tutela-della-salute) | HTML | annuale | – |
| Comuni veneti (Verona, Padova, Vicenza, Treviso, Venezia…) | ordinanze stagionali per livello | es. [Verona ord. 36/2025](https://www.comune.verona.it/content/download/13461/298201/file/Ordinanza%20n%2036%2030-09-2025.stamped.pdf), [Padova ord. 38/2025](https://www.comune.padova.it/sites/default/files/2025-09/Ordinanza%20n.%2038%20del%2030-09-2025%20Istituzione%20delle%20domeniche%20ecologiche%20del%2005-10-2025%2C%2009-11-2025%2C%2007-12-2025%2C%2025-01-2026%2C%2022-02-2026%2C%2022.pdf) | PDF | annuale | la [Provincia di Vicenza raccoglie le ordinanze](https://aria.provincia.vicenza.it/ordinanze-comunali/files/prot_par_0019948_del_27_11_2020___documento_ordinanza_30_2020.pdf) |
| **UNRAE – "Limitazione circolazione", edizione 2026/08** | compendio di **tutte** le limitazioni per Regione e città (Lombardia, Lazio, Piemonte, Bolzano, Trento, Veneto, Liguria, Emilia-Romagna, Toscana, Marche, Campania, Sicilia), con orari, classi, deroghe | [PDF 1,5 MB, 115 pagine, dati al 5/8/2026](https://unrae.it/files/Limitazione%20circolazione_Edizione_2026_8_6a744b9bdc246.pdf) | 200, PDF testuale | mensile (edizione 2026/08) | – |
| Portale dell'Automobilista – verifica classe ambientale per targa | serve all'utente per sapere la sua Euro | [200](https://www.ilportaledellautomobilista.it/web/portale-automobilista/ext/verifica-classe-ambientale-veicolo) | HTML (una targa alla volta) | – | motore ufficiale |

**Conteggio**: il "semaforo di oggi" sta in **5 fonti** (ARPAE, ARPAV, ARPA Piemonte, Regione Lombardia/INFOARIA, Roma Mobilità), di cui **2 leggibili in HTML (ARPAE, Roma) e 3 app JavaScript senza endpoint pubblico trovato** (ARPAV, Piemonte, INFOARIA). Le **regole** per livello e classe stanno in 4 delibere regionali + ~20–30 ordinanze comunali (ER raccolte da ARPAE; Veneto sui siti comunali/provinciali; Torino, Roma, Firenze, Napoli) e sono già compilate nel PDF UNRAE (115 pagine, aggiornato mensilmente). **Copertura**: i sistemi a livelli esistono solo nelle 4 regioni del Bacino Padano e a Roma; Firenze ha limitazioni strutturali (diesel fino a Euro 5 feriali 8.30–18.30 nella zona tra piazza Beccaria e piazza della Libertà, [PMI.it](https://www.pmi.it/?p=480453)), Napoli e Palermo solo ordinanze occasionali. Le 16 città dell'autocomplete stanno tutte in queste 5 fonti → copertura della domanda ≈ 100%.

**Filtro duro: PASSA con un test** — le fonti sono ≤20 e ufficiali, ma 3 su 5 richiedono di trovare l'endpoint dall'ispezione di rete nel browser di Massimiliano o un browser headless (Playwright su GitHub Actions: fattibile, non gratuito in tempo di sviluppo).

### 2.3 La domanda (Google Autocomplete, 10/10/2026, `dati-6-veicoli/autocomplete-antismog.json`)

- **"blocco traffico [città]"**: 16 città su 16 (Torino, Milano, Roma, Bologna, Modena, Padova, Napoli, Firenze, Palermo, Verona, Brescia, Parma, Reggio Emilia, Treviso, Vicenza, Bergamo) con proposte "oggi" o "domani"; 5 con "mappa"; 4 con la classe Euro nel testo ("blocco traffico bologna euro 5", "blocco traffico firenze euro 4/euro 5", "blocco del traffico euro 5 torino", "blocco traffico parma euro 5").
- **"euro 5 diesel [città]"**: Torino 10 proposte ("oggi", "domani", "proroga", "blocco", "2026"), Milano 10 ("area b", "move in", "residenti", "sabato e domenica"), Roma 10 ("fino a quando potranno circolare", "fascia verde", "2027"), Bologna 9, Brescia 7, Padova 4. "euro 4 diesel milano": 10. "euro 6 diesel blocco" e "euro 3 benzina blocco": 10 ciascuna, con città e regioni.
- **"semaforo antismog"**: Torino, Asti, Alba, Cuneo, Alessandria, "oggi", "domani", "oggi e domani", "arpa piemonte".
- **"misure antismog"**: Torino, Emilia-Romagna, Bologna, Modena "oggi", Milano "oggi", Lombardia, Verona; "comune di torino misure antismog oggi".
- **"blocco euro 5 [regione]"**: Piemonte 10, Lombardia 10 ("rinvio", "ultime notizie", "mappa", "orari", "deroghe"), Veneto 10 ("comuni interessati"), Emilia-Romagna 5.
- "posso circolare oggi" → "posso circolare oggi a roma". "fascia verde roma euro" → Euro 4, 4 diesel, 5 diesel, 3 benzina, 5, 3, 6, 4 benzina, 2 benzina.
- "move in lombardia/piemonte": 10 proposte ciascuna ("costo", "quanti km", "rinnovo", "euro 5 diesel").

È la domanda più grande incontrata in tutte le ricerche di questa serie, **stagionale** (ottobre–aprile) e **a eventi** (picco nei giorni di attivazione).

### 2.4 Le SERP (10 query città×Euro, ricerca web 10/10/2026)

| Query | Chi compare | Aggregatore "oggi per città"? |
|---|---|---|
| blocco traffico torino oggi euro 5 diesel | greenme, motorionline, motorbox, [SicurAuto (notizia 24–25/2/2026)](https://www.sicurauto.it/news/attualita-e-curiosita/torino-blocco-del-traffico-24-25-febbraio-2026-per-allerta-smog/), motor1, mentelocale | no |
| euro 5 diesel bologna oggi limitazioni | [il Resto del Carlino ×5](https://www.ilrestodelcarlino.it/emilia-romagna/cronaca/blocco-traffico-dove-e-quando-qev1d9al), auto.it, [infografica ARPAE PDF](https://www.arpae.it/it/temi-ambientali/aria/liberiamo-laria/infografica_misure_liberiamo_l_aria_pair2030_a4.pdf), autoblog, motorimagazine | no |
| misure antismog modena oggi | Resto del Carlino, [ordinanza Modena su ARPAE (PDF 2022-23)](https://arpae.it/it/temi-ambientali/aria/liberiamo-laria/limitazioni-per-comune/ordinanze-2022-2023/modena_2022_2023/modena_ordinanza_antismog_2022_2023.pdf), reggionline, Confindustria Emilia, motorimagazine, quifinanza | no |
| blocco traffico parma oggi euro 5 | SicurAuto (domenica ecologica), Resto del Carlino, [money.it](https://www.money.it/blocco-auto-diesel-euro-5-obbligo-1-ottobre-e-modelli-colpiti), greenme, hdmotori, Il Giorno, businessonline | no |
| blocco traffico vicenza oggi mappa euro | [Telepass Moveo](https://moveo.telepass.com/domenica-ecologica-vicenza/), motor1, PDF del Comune di Vicenza (2016–2022), alvolante | no |
| euro 4 diesel milano area b oggi | motorionline, Il Post e Open (2019), Il Giorno, SicurAuto, insella | no |
| fascia verde roma euro 4 diesel 2026 | hdmotori, businessonline, quotidiano.net, SicurAuto, [PDF Roma Mobilità 1/2026](https://romamobilita.it/wp-content/uploads/2026/01/ilovepdf_merged-17_compressed.pdf), missionline, AGI | no |
| blocco traffico firenze euro 5 2026 | PMI.it, Il Giorno, La Nazione, SicurAuto, L'Automobile ACI, mentelocale | no |
| blocco traffico brescia domani euro 5 diesel | Telepass Moveo, Avvenire, Il Giorno, SicurAuto, money.it, finanza.com | no |
| blocco traffico reggio emilia oggi euro 5 arpae | Resto del Carlino, reggionline, motorimagazine, greenme | no |

Nessuna delle 10 SERP mostra una pagina che risponda "oggi, nella tua città, per la tua classe Euro"; rispondono **articoli di testate** (spesso del 2019–2025) e PDF di ordinanze. Gli strumenti ufficiali che hanno il dato di oggi (INFOARIA, webapp Aria Piemonte, bollettino ARPAV, bollettino ARPAE) sono **app o pagine regionali non indicizzate per città** e non compaiono. Esiste però una ricerca del tipo "elenco città" già servita: [Motor1 "elenco città per città"](https://it.motor1.com/news/447334/blocco-del-traffico-benzina-diesel-elenco-citta/), [automobilista.it](https://www.automobilista.it/quali-auto-non-potranno-piu-circolare-nel-2026-a-causa-di-blocchi-del-traffico-e-ztl-ambientali/), [SicurAuto "blocco auto Veneto 2025 e 2026"](https://www.sicurauto.it/news/attualita-e-curiosita/blocco-auto-veneto-2025-2026-misure-antismog/), [Telepass Moveo "Euro 5: in quali città"](https://moveo.telepass.com/stop-auto-diesel-euro-5-quali-citta/) (datePublished 29/7/2025).

**Concorrenti**: (a) **gli enti** hanno già il motore e l'avviso: INFOARIA con notifiche previa registrazione (Lombardia), app/webapp "Aria Piemonte" con il semaforo di oggi e domani per comune, iscrizione email ai bollettini ARPAV, bollettino ARPAE, Area B "verifica targa" a Milano, allerta SMS gratuita della Città Metropolitana di Bologna ([reggionline, 2018](https://www.reggionline.com/allerta-smog-reggio-emilia-modena-bologna-ferrara/)); (b) **testate e grandi siti** (il Resto del Carlino, Il Giorno, SicurAuto, Motor1, Telepass Moveo, money.it, HDmotori) con un articolo per ogni attivazione; (c) **UNRAE** regala ai concessionari il compendio di 115 pagine; (d) app: **nessuna app italiana trovata** che avvisi per classe Euro e città (ricerca negli store: [ZTL Alert](https://apps.apple.com/it/app/ztl-alert-free/id806239134) copre varchi ZTL, non i blocchi antismog; [Green-Zones](https://apps.apple.com/app/id1279719525) copre le zone ambientali europee, con aggiornamento alle 20:00 per il giorno dopo). L'app "Che aria tira" non esiste nell'autocomplete (è il titolo di un programma TV).

### 2.5 Chi pagherebbe, e prove che si paga già per qualcosa di simile

| Pubblico | Cosa pagherebbe | Prova che si paga | Giudizio |
|---|---|---|---|
| Privati con diesel Euro 4/5 (1,4 M nel Bacino Padano) | avviso "domani la tua auto è ferma a Torino" | pagano per **circolare** (Move-In: max 50 € il primo anno = 30 € scatola nera + 20 € servizio, poi 20 €/anno, [brochure Regione Emilia-Romagna](https://notizie.regione.emilia-romagna.it/comunicati/2022/dicembre/qualita-dell2019aria-dal-1deg-gennaio-i-cittadini-dell2019emilia-romagna-potranno-iscriversi-a-move-in-un-sistema-di-monitoraggio-per-ridurre-l2019impatto-emissivo-dei-veicoli-e-promuovere-stili-di-guida-piu-sostenibili-via-libera-in-giunta-a-modalita-di/brochure_move-in.pdf/@@download/file/brochure_Move%20In.pdf); 35.000 adesioni in Lombardia, [automoto.it, non datato](https://www.automoto.it/news/scatola-nera-move-in-per-i-vecchi-diesel-euro-5-soluzione-o-fregatura-video.html)) e per i **varchi ZTL** (Henable ZTL 3,59 €/anno, [iPhoneItalia](https://www.iphoneitalia.com/?p=459403); app "ZTL" 1,99 €); **ma non per l'avviso antismog**, che gli enti mandano gratis | NO: al massimo una donazione/"premium" da pochi euro |
| Flotte, trasporto leggero, corrieri, artigiani con furgoni diesel Euro 4/5 | avviso per targa/classe su più città; export | in Europa esiste: Green-Zones Fleet-App "per autisti di camion e bus con contratto di servizio a pagamento" ([App Store](https://apps.apple.com/app/id1459984538)); nella versione consumer l'abilitazione camion costa **79,99 €/anno** (store DE) / 72,99 $ (US); contratto flotte: prezzo non pubblico | SÌ in teoria, ma si vendono con il commerciale (vietato dal metodo) e il mercato italiano del "blocco antismog per flotte" non ha prove |
| Concessionari, rottamazione, noleggio, installatori Move-In (TSP) | lead "la mia Euro 5 è ferma: che faccio?" | i concessionari hanno già UNRAE gratis; programmi di affiliazione per valutazione/permuta: trovato solo [carVertical affiliate](https://www.carvertical.com/it/affiliate-program) (commissione sul report da 29,99 €, importo non dichiarato); l'AGCM ha sanzionato siti di "valutazione gratuita" ingannevoli ([PS8879](https://www.agcm.it/dotcmsDOC/allegati-news/PS8879.pdf)) | POSSIBILE ma non provato; è pubblicità, non il modello lista→abbonamento |
| Assicurazioni | – | nessuna prova trovata | NO |

### 2.6 Tabella delle 5 condizioni

| Cond. | Esito | Prova |
|---|---|---|
| 1. Soldi + si paga già | **PARZIALE** | privati: no (avvisi ufficiali gratuiti; si paga 20–50 €/anno per Move-In e 2–4 € per app ZTL, non per l'informazione antismog); flotte: sì in Europa (Green-Zones, 79,99 €/anno per il camion nella versione consumer), ma senza vendita diretta non si raggiungono |
| 2. Filtro duro | **SÌ con test** | 5 fonti per il semaforo (2 HTML, 3 app JS senza endpoint trovato), ~25 atti per le regole + UNRAE; copertura ≈ 100% della domanda |
| 3. Domanda + vuoto | **SÌ** | 16/16 città con "oggi/domani", 6 città × Euro 5 con 4–10 proposte; 10/10 SERP senza aggregatore "oggi per città"; attenzione: 4 enti su 5 hanno già un motore o un avviso regionale (non indicizzato per città) |
| 4. Due parti | **DEBOLE** | chi ha l'auto ferma ↔ concessionari/TSP Move-In: lead pubblicitari, non intermediazione; nessun prezzo di lead trovato |
| 5. Lavoro ~0, responsabilità | **SÌ con cautela** | tutto automatico (sez. 2.8), ma un "puoi circolare" sbagliato vale **168 €** di multa (Torino, [auto.it](https://www.auto.it/news/attualita/2025/05/19-8137201/stop_ai_diesel_euro_5_la_ghigliottina_inizia_a_torino)) o 163–658 € (Roma, [SicurAuto](https://www.sicurauto.it/news/attualita-e-curiosita/ztl-roma-orari-mappa-e-permessi/)): ogni pagina deve linkare il bollettino e l'ordinanza del giorno e dichiarare la fonte; le regole cambiano in corsa (rinvio del 25/9/2026, Firenze che non estende l'alt agli Euro 5 post-2014) |

### 2.7 Stima prudente

Assunzioni: ~30 pagine-città + 6 pagine-classe + 4 pagine-regione; indicizzazione lenta contro testate con alta autorità; stagione 1 (ott 2026–apr 2027) quasi persa per il ritardo di costruzione; stagione 2 (ott 2027–apr 2028) a regime. Visite: mese 6 ≈ 2.000/mese; inverno 2027-28 ≈ 8.000–12.000/mese; **totale 12 mesi ≈ 35.000–45.000**. Iscritti all'avviso gratuito "domani blocco per la tua città e la tua Euro": 3% = 1.000–1.300. Paganti: privati "premium" 9 €/anno al 2% = 20–26 → ≈ 200 €; flotte/aziende arrivate da sole a 149 €/anno all'1% = 10–13 → ≈ 1.500–1.900 €; lead a concessionari/TSP: non contati (nessun prezzo provato). **12 mesi ≈ 1.000–2.500 €; 18 mesi run-rate ≈ 3.000–6.000 €/anno** (iscritti 3.000; 25 flotte a 149 € + 60 premium + eventuale affiliazione). Pubblicità display non è nel modello: con 40.000 visite/anno varrebbe comunque solo 100–300 €. **Non arriva a 10k.**

### 2.8 Cosa farebbe Claude in automatico

- **Ogni giorno alle 11:30** (GitHub Actions): legge ARPAE (lun/mer/ven), ARPAV (lun/mer/ven), semaforo Piemonte (lun/mer/ven), INFOARIA (lun/gio), Roma Mobilità; aggiorna lo stato oggi/domani di ogni città; rigenera le pagine con `genera.py` (riuso: "sede" → città, "sessione" → giorno con livello e classi ferme); invia l'avviso agli iscritti filtrati per città e classe (Netlify Forms + servizio email gratuito).
- **Ogni settembre**: rilegge le delibere regionali, le pagine ARPAE per comune, le ordinanze di Torino/Roma/comuni veneti e il PDF UNRAE del mese; ricostruisce la tabella città × livello × classe × orario; segnala le differenze a Massimiliano.
- **A ogni notizia** (rinvii nazionali): aggiorna la pagina "stato del blocco Euro 5" con fonte e data.
- Lavoro umano: ~0 a regime; 1–2 ore a stagione per controllare la tabella delle regole.

### 2.9 Rischi

1. **Le 3 app JS**: se l'endpoint non si trova, serve Playwright (più fragile; ARPAV ha cambiato sito, Piemonte ha due app diverse).
2. **Responsabilità**: la risposta "sì/no" è giuridicamente delicata; mitigazione con link al bollettino e all'ordinanza e con un testo che riporta le regole, non un verdetto; comunque un rischio reputazionale.
3. **Gli enti chiudono il vuoto**: INFOARIA e Aria Piemonte hanno già notifiche e mappa; basterebbe un indice per città.
4. **Testate**: il Resto del Carlino/Il Giorno pubblicano un articolo a ogni attivazione con alta autorità; un sito nuovo arriva dopo.
5. **Norme instabili**: tre rinvii in due anni; regole diverse tra regioni e dentro la stessa regione (Milano Area B, Firenze).
6. **Stagionalità**: 6 mesi su 12 senza traffico.

### 2.10 Ore di costruzione (riuso del motore)

**25–35 h**: 5 lettori di bollettini (di cui 3 da scoprire/headless: 10–15 h), tabella delle regole per 30 città da delibere + UNRAE (5 h), adattamento di `genera.py` (pagine città/classe/regione, riuso ≈ 50% perché cambia il modello dati: non "sessioni d'esame" ma "stato giornaliero × classi": 6–8 h), modulo avvisi con filtro città/classe (4–6 h).

---

## 3. Direzione 2 – Calendario nazionale dei divieti di circolazione dei mezzi pesanti

- **Fonte**: una sola: DM MIT **n. 325 del 12 dicembre 2025**, GU n. 302 del 31/12/2025 ([scheda MIT](https://www.mit.gov.it/normativa/decreto-ministeriale-n-325-del-12-dicembre-2025), [pagina MIT del calendario](https://mit.gov.it/node/21641): **000 dal nostro proxy**, DNS non risolto anche con WebFetch; [ANCE Cremona, circ. 661/25 del 24/12/2025](https://cremona.ance.it/2025/12/24/circ-661-25-limitazioni-al-traffico-veicolare-calendario-dei-giorni-vietati-alla-circolazione-anno-2026/?print=pdf)); veicoli >7,5 t, strade extraurbane; 79–80 giornate; deroga Milano-Cortina 1/1–31/3/2026; novità sui trattori isolati ([Ingenio](https://www.ingenio-web.it/articoli/divieti-di-circolazione-mezzi-pesanti-pubblicato-il-calendario-2026/)). `gazzettaufficiale.it` risponde 200 dal server. **Filtro duro: PASSA** (1 fonte, PDF annuale).
- **Domanda** (autocomplete): "divieti circolazione mezzi pesanti 2026 / pdf / agosto / luglio / francia", "calendario divieti mezzi pesanti 2026 pdf / fai / da stampare / francia / mit", "divieti mezzi pesanti oggi / austria oggi", "divieti mezzi pesanti 2026 europa / slovenia / autostrade per l'italia", "deroghe divieti mezzi pesanti 2026". Forte, con una coda europea (Francia, Austria, Slovenia).
- **SERP "calendario divieti mezzi pesanti 2026 pdf"**: MIT (nodo 21641), Certifico (Full Plus a pagamento), Ingenio, FleetMagazine (403 dal server, calendario completo con orari), SicurAuto ("dove controllare il calendario 2026", 200), circolari ANCE, Confartigianato/CNA, [nakordoni.eu](https://nakordoni.eu/it/for_truck_drivers/traffic_bans/italy) (403 dal server; pubblica **pagine settimanali in italiano** "16 Paesi applicano divieti questa settimana" e un'app Android gratuita "Truck Bans" per tutta Europa, [Motor1 app list](https://it.motor1.com/features/525655/app-divieti-camion-calendario-2021/)). Le "deroghe regionali" sono autorizzazioni prefettizie (100 Prefetture) → fuori filtro. **Condizione 3: NO** (l'ente ha il PDF, cinque aggregatori gratuiti e un sito europeo settimanale).
- **Chi paga**: gli autotrasportatori pagano software di gestione e telematica, non il calendario; nessuna prova di abbonamento al calendario (Certifico vende l'abbonamento a tutta la banca normativa, non questo). **Condizione 1: NO.**
- **Stima**: 0–500 € a 12 mesi; ≤1.000 €/anno a 18. **Ore**: 3–5 (una pagina + ICS scaricabile + avviso settimanale). **Uso sensato**: una pagina "divieti di questa settimana" dentro un sito veicoli, non un sito. Per l'Europa (Francia, Austria, Germania, Slovenia): fonti ufficiali 1 per Paese (≤20), ma nakordoni, Green-Zones e le app lo fanno già gratis.

---

## 4. Direzione 3 – Verifica targa / revisione / bollo / assicurazione

- **Fonti ufficiali** (tutte 200 dal server): Portale dell'Automobilista [verifica classe ambientale](https://www.ilportaledellautomobilista.it/web/portale-automobilista/ext/verifica-classe-ambientale-veicolo), [verifica copertura RC](https://www.ilportaledellautomobilista.it/web/portale-automobilista/ext/verifica-copertura-rc), [revisioni](https://www.ilportaledellautomobilista.it/web/portale-automobilista/veicoli/revisioni), [ricerca officine autorizzate](https://www.ilportaledellautomobilista.it/web/portale-automobilista/servizi-online-ricerca-officine-autorizzate); ACI (bollo, visure PRA: pagine 200 ma gusci JS da 730 byte). Sono **interrogazioni per singola targa**, senza alcun dataset scaricabile: non esiste una fonte "strutturata" da cui costruire pagine. **Filtro duro: NON PASSA.**
- **Dati personali**: la targa è considerata dato personale (ricorso del Garante accolto in Cassazione, [Studio Cataldi](https://www.studiocataldi.it/articoli/46496-la-targa-dell-autovettura-e-un-dato-personale.asp)); le guide spiegano che le verifiche gratuite danno solo dati tecnici (classe, revisione, RC) e che l'intestatario si ottiene solo con la **visura PRA a pagamento** ([automobilista.it](https://www.automobilista.it/come-verificare-una-targa-gratis-online-in-modo-legale-e-sicuro/)). Costruire pagine per targa = ripubblicare dati personali → **esclusione di Massimiliano, condizione 5: NO**.
- **Domanda**: fortissima ("verifica targa gratis online", "scadenza revisione targa", "verifica bollo auto con targa senza spid", "visura targa immediata gratis", "proprietario veicolo da targa gratis") ma **servita dai motori ufficiali** (in autocomplete: "controllo targa gratis portale automobilista / aci", "aci verifica targa revisione") e da report commerciali: carVertical **29,99 €** a report ([HDmotori](https://www.hdmotori.it/carvertical-come-funziona-risparmiare-migliaia-euro-acquisto-auto/)), con affiliazione. **Condizione 3: NO** (ente con il motore + aggregatore pagante). Scartata con prove.

---

## 5. Direzione 4 – Motorizzazione civile

| Sotto-direzione | Fonti | Esito |
|---|---|---|
| Esami patente (date delle sedute di teoria/pratica) | calendari **PDF mensili per ufficio** sui siti delle Direzioni territoriali: [DGT Nord-Est, Forlì-Cesena luglio 2026](https://www.dgtne.it/wp-content/uploads/2026/06/Calendario-esami-patente-di-guida-luglio-2026.pdf), [Aosta marzo 2026](https://trasporti.regione.vda.it/Media/Trasporti/Allegati/MTCAO_Modulistica_Patente/CALENDARIO_ESAMI_MARZO_2026.pdf); `dgtne.it`, `dgtno.it`, `dgtcentro.it` 200, `dgtsud.it` certificato TLS non valido | ~100 uffici, PDF non uniformi, pubblicati a tratti; la prenotazione passa dall'autoscuola o dal Portale ("date esame patente b motorizzazione 2026" ha domanda, "esame patente date" quasi nulla). **Filtro duro: NON PASSA; pubblico non pagante** |
| Esami istruttore/insegnante autoscuola | 100 Province | già scartato per copertura; autocomplete minimo ("esame istruttore autoscuola 2026", "programma") |
| Centri di revisione | directory ufficiale del Portale (200) | l'ente ha il motore; "centri revisione vicino a me" = Google local. NO |
| Immatricolazioni/collaudi/targhe prova | nessun calendario pubblico; "targa prova" = domanda informativa (assicurazione, costo) | NO |
| Veicoli storici (ASI/FMI) | [asifed.it 200](https://asifed.it/); elenchi club per città ("asi auto storiche roma/napoli/salerno") | directory consumer, nessun pagante, esenzione bollo per regione = pagine già coperte. NO |
| Motorizzazione civile [città] (orari, telefono, prenotazione) | 100 uffici | domanda forte ("motorizzazione civile torino telefono/orari/prenotazioni online") ma è "contatti di un ufficio": Google local + sito MIT. NO |

---

## 6. Direzione 5 – Open data veicoli

| Dataset | Fonte e stato (10/10/2026) | Domanda | Concorrenti | Esito |
|---|---|---|---|---|
| **Colonnine di ricarica (PUN/MASE-GSE)** | [piattaformaunicanazionale.it](https://www.piattaformaunicanazionale.it/) 200 (guscio React da 1.371 byte su ogni path, anche `/api/v1/` e `/opendata`); nel bundle solo dashboard ArcGIS GSE e FeatureServer di scuole/ospedali/stazioni; **nessuna API né CSV trovati** (ricerche web: nessuna fonte parla di open data PUN; solo il Comune di Ferrara ha un CSV locale); >32.000 punti al lancio ([HDmotori, 2024](https://www.hdmotori.it/auto/articoli/n580175/mase-piattaforma-unica-nazionale-punti-ricarica/)) | forte ma consumer e "vicino a me" ("colonnine ricarica milano/roma/torino/bologna", "gratis", "mappa") | Google Maps, PlugShare, Nextcharge, Chargemap, app dei CPO | **NO** (fonte non estraibile; SERP = mappe; nessun pagante) |
| **Autovelox (Polizia di Stato)** | [pagina "Autovelox e tutor: dove sono?"](https://www.poliziadistato.it/articolo/175) 200: dichiara l'elenco "aggiornato settimanalmente" e la "programmazione dei servizi con apparecchiature mobili" per regione, ma nell'HTML i PDF linkati sono del 26/8/2021 (postazioni fisse); i file settimanali non sono linkati nell'HTML letto dal server | forte e regionale ("autovelox oggi sardegna/puglia/sicilia/lombardia", "autovelox mobili oggi torino/roma", "autovelox torino questa settimana"); vuota per città medie (Napoli, Brescia, Treviso, Padova: 0 proposte) | [auto.it ripubblica il calendario settimanale](https://www.auto.it/news/attualita/2026/09/01-9068844/autovelox_mobili_controlli_mirati_dove_sono_fino_al_6_settembre_in_ogni_regione) (25/8 e 1/9/2026), testate locali, Waze, Radarbot, Coyote | **NO** (1 fonte, ma già ripubblicata ogni settimana; nessun pagante oltre le app di navigazione) |
| Parco circolante ACI per comune | `opendata.aci.it` **502** dal proxy; pagine aci.it 200 ma gusci JS | "parco circolante italia 2025", "parco auto circolante per comune" (1 proposta) | ACI stessa, Autoritratto, testate | NO (statistiche, nessun pagante) |
| Incidenti ISTAT per comune | [esploradati.istat.it 200](https://esploradati.istat.it/databrowser/); [pagina ISTAT 200](https://www.istat.it/informazioni-sulla-rilevazione/incidenti-stradali/) | "incidenti stradali comune di milano/roma/napoli", "statistiche per comune" | ISTAT/ACI, tuttitalia e simili | NO |
| ZTL per comune | migliaia di Comuni | enorme ("ztl orari roma/palermo/milano…") | SicurAuto, Telepass, app ZTL | NO per regola |
| Aree sosta camper | nessuna fonte ufficiale unica | forte, consumer | CamperOnLine, Park4Night | NO |

---

## 7. Classifica, verdetto, test tecnico

| # | Direzione | Filtro duro | 1 | 3 | 4 | 5 | 12 mesi | 18 mesi | Ore |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Antismog per città e classe Euro** | SÌ con test (3 app JS) | PARZIALE | SÌ | DEBOLE | SÌ con cautela | 1.000–2.500 € | 3.000–6.000 € | 25–35 |
| 2 | Divieti mezzi pesanti | SÌ | NO | NO | NO | SÌ | 0–500 € | ≤1.000 € | 3–5 |
| 3 | Verifica targa | NO | SÌ (ma occupato) | NO | NO | NO | – | – | – |
| 4 | Motorizzazione | NO | NO | debole | NO | – | – | – | – |
| 5 | Open data (PUN, autovelox, ACI, ISTAT, ZTL) | NO/già coperto | NO | NO | NO | – | – | – | – |

**VERDETTO**: **nessuna direzione "veicoli" supera i filtri con una stima prudente ≥10.000 €/anno**. Le prove: targhe = dati personali senza dataset (sez. 4); Motorizzazione = 100 uffici con PDF o motori ufficiali (sez. 5); PUN senza API, autovelox già ripubblicati, ACI/ISTAT statistiche (sez. 6); mezzi pesanti = 1 fonte ma 6+ aggregatori gratuiti e un sito europeo settimanale (sez. 3). **L'antismog è la sola con fonti poche e domanda grande**, ed è un sito da 3–6k/anno, stagionale, con pubblico che non paga e con responsabilità da gestire. È lo stesso schema delle candidate "esami nazionali" (EsameB1/EsamiDiStato): poche fonti, domanda vera, ricavi piccoli. Va fatto **solo se Massimiliano accetta un terzo sito piccolo** e solo se il test seguente passa.

### 7.1 Test tecnico a costo zero per la direzione 1 (2–3 giorni, solo Claude)

**Giorno 1 – i 5 semafori si leggono da script?**
1. Dal computer di Massimiliano (o con Playwright su GitHub Actions): aprire INFOARIA stato-attivazione, webgis Aria Piemonte e bollettino ARPAV con la scheda "Rete" del browser e annotare le chiamate dati (URL, formato). Se un endpoint esiste, provarlo con `curl` dal server. **Soglia**: 3 fonti su 3 con un endpoint leggibile o con una pagina resa in headless in ≤60 s; altrimenti STOP (senza il semaforo del Nord il sito non ha il dato per cui la gente cerca).
2. Leggere ARPAE e Roma Mobilità in HTML e ricavare il livello per provincia/città. **Soglia**: livello estratto uguale a quello letto a mano in 3 giorni di controllo consecutivi (lun/mer/ven) su tutte e 5 le fonti: 15/15.
3. Misurare il numero di comuni con un livello: **soglia ≥150** (76 Piemonte + comuni lombardi >30.000 ab. + 30 ER + Area 1 Veneto + Roma).

**Giorno 2 – la tabella delle regole**
4. Costruire la tabella città × livello × classe × orario per 30 città (le 16 dell'autocomplete + 14 tra Monza, Como, Varese, Novara, Alessandria, Asti, Cuneo, Piacenza, Ferrara, Rimini, Ravenna, Venezia/Mestre, Rovigo, Prato) dalle delibere regionali, dalle pagine ARPAE per comune, da Torino/Roma, dalle ordinanze venete e dal PDF UNRAE 2026/08. **Soglia**: ≥27/30 città con regole concordanti tra fonte primaria e UNRAE; le discordanze annotate con link.
5. Generare 30 pagine-città e 6 pagine-classe con `genera.py` adattato; ogni pagina deve avere: stato di oggi e domani, fonte del bollettino con data e ora, link all'ordinanza, testo delle regole senza verdetto personale, modulo "avvisami". **Soglia**: generazione completa in ≤5 minuti su GitHub Actions.

**Giorno 3 – domanda e vuoto dalla Google italiana**
6. Autocomplete su 40 città ("blocco traffico X oggi", "euro 5 diesel X", "misure antismog X oggi"): **soglia ≥30/40** con almeno una proposta "oggi/domani".
7. Dal computer di Massimiliano, 20 query città×Euro: contare quante hanno nei primi 3 risultati una pagina (ufficiale o no) che dice lo stato di oggi per quella città. **Soglia**: vuoto confermato in ≥15/20.

**Decisione**: COSTRUIRE (25–35 h) solo se passano 1, 2, 4, 6 e 7, e solo come sito piccolo con obiettivo dichiarato 3–6k/anno; FERMARE se fallisce il punto 1 (fonti JS illeggibili) o il 7 (gli enti o le testate hanno già la pagina "oggi per città"). Test a 45 giorni dalla pubblicazione (in stagione): ≥40 pagine indicizzate, ≥300 clic, ≥100 iscritti all'avviso, ≥5 iscritti che si dichiarano azienda/flotta.

---

## 8. Riepilogo HTTP status delle fonti chiave (10/10/2026, `curl` dal server, UA browser)

| Fonte | Status | Nota |
|---|---|---|
| arpae.it bollettino misure emergenziali; archivio; limitazioni per comune; ordinanze 2026-2027 | 200 | HTML leggibile; 20 pagine-comune 2026-27 |
| arpa.veneto.it bollettino livelli di allerta PM10; iscrizione bollettini | 200 | tabella via JS (React) |
| aria.ambiente.piemonte.it/semaforo; webgis.arpa.piemonte.it/aria_piemonte | 200 | app Vue/Angular; WFS geomap 200 senza layer semaforo |
| arpa.piemonte.it/media/8230 (protocollo) | 200 | PDF 1,4 MB |
| regione.piemonte.it (node 17270, pagine aria) | 000 / reset | dal proxy |
| regione.lombardia.it misure temporanee; DGR 5613/2026 | 200 | HTML + PDF |
| infoaria.regione.lombardia.it | 200 (SPA); `/api/...` 404; `getFile/3` 200 PDF | – |
| movein.regione.lombardia.it | 200 | – |
| movein Piemonte / Emilia-Romagna | 000 | dal proxy |
| comune.torino.it misure antismog | 200 | HTML con tabella livelli |
| comune.milano.it Area B | 200 | – |
| romamobilita.it fascia verde | 200 | HTML con livelli |
| arpalazio.it | 200 | – |
| comune.bologna.it misure emergenziali | 200 | – |
| unrae.it Limitazione circolazione 2026/08 | 200 | PDF 115 pagine |
| moveo.telepass.com | 200 | articoli 2025 |
| ilportaledellautomobilista.it (classe ambientale, RC, revisioni, officine) | 200 | una targa alla volta |
| aci.it (bollo, visure, open data, Autoritratto) | 200 | gusci JS 730–746 byte |
| opendata.aci.it | 502 | dal proxy |
| istat.it incidenti; esploradati.istat.it | 200 | – |
| piattaformaunicanazionale.it (tutti i path) | 200 | guscio React 1.371 byte; nessuna API |
| poliziadistato.it/articolo/175 (autovelox) | 200 | PDF linkati del 2021 |
| mit.gov.it (nodi 21641, 21666) | 000 | DNS non risolto dal proxy |
| gazzettaufficiale.it | 200 | – |
| dgtne.it, dgtno.it, dgtcentro.it | 200 | calendari PDF per ufficio |
| dgtsud.it | TLS non valido | – |
| asifed.it | 200 | – |
| nakordoni.eu; fleetmagazine.com | 403 | anti-bot |
| sicurauto.it (pesanti 2026) | 200 | – |
| suggestqueries.google.com | 200 (130/130) | – |

File di prova: `studio-business/intelaiatura/dati-6-veicoli/autocomplete-antismog.json` (57 query) e `autocomplete-altre-direzioni.json` (73 query).
