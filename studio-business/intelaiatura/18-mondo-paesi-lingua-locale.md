# Ricerca A — Paesi con "barriera della lingua": cosa cercano in inglese turisti, nomadi digitali ed espatriati, quando la regola ufficiale è scritta solo nella lingua locale

Data: **10 ottobre 2026**. Lavoro fatto dal server della sessione (curl con User-Agent da browser, ricerche web, autocomplete Google).
File grezzi in `scratchpad/globale/A/dl/` (autocomplete: `ac1.json`…`ac4.json`, 257 parole chiave × 3 mercati = 771 chiamate; download delle fonti: PDF, XML, HTML, letti solo con `python3 -I`). Script in `scratchpad/globale/A/script/`. Nessun file del repository è stato toccato.

**Criterio scritto prima del lavoro.** Un'idea PASSA se: (1) la domanda in inglese compare nell'autocomplete Google in almeno 2 mercati su 3 (USA, Regno Unito, Australia); (2) esiste una fonte ufficiale gratuita, stabile, scritta soprattutto nella lingua locale, che Claude può leggere o almeno controllare in automatico; massimo 3 fonti "madri" per modulo (sono ammesse tabelle di regole che cambiano 1-2 volte l'anno, se c'è un controllo automatico dei cambiamenti); (3) chi risponde oggi in inglese è debole (blog, giornali, tabelle vecchie, PDF) e non un sito ufficiale in inglese o un aggregatore forte; (4) nessun consiglio legale, medico o finanziario e nessun dato personale; (5) ricavo prudente **≥ 1.500 €/anno a 18 mesi** per passare da solo; sotto questa cifra è "satellite" (si fa solo se costa poche ore e si appoggia a un sito che passa).

Cosa NON ho ripetuto: lo studio 14 aveva già guardato le pagine "stato oggi" (treni, tifoni, vulcani, strade, scioperi, musei chiusi oggi). Qui il taglio è diverso: **regole e tariffe ufficiali che cambiano poche volte l'anno** (tasse, tariffe, zone a basse emissioni, calendari), che la gente cerca **prima del viaggio** e che nessuno tiene aggiornate in inglese.

---

## 0. Risposta in breve

- **La scoperta più forte: le tasse di soggiorno ("tourist tax").** È la stessa forma della domanda degli scioperi (tante pagine piccole, una per luogo, con una cifra che cambia), ma molto più larga: **92 parole chiave controllate, 89 con suggerimenti in tutti e 3 i mercati**; tra i suggerimenti ci sono **93 richieste di "calculator"** (es. "mallorca tourist tax calculator", "greece tourist tax 2026 calculator", "kyoto accommodation tax calculator", "turkey tourist tax calculator from uk") e **18 richieste legate ai tour operator inglesi** ("ibiza tourist tax tui calculator", "rhodes tourist tax jet2", "turkey tourist tax easyjet"). Le regole stanno in leggi e delibere in giapponese, greco, catalano, turco, croato, portoghese. In inglese rispondono blog, articoli e una tabella di Holidu ferma a maggio 2025; **nessun calcolatore multi-destinazione aggiornato** (verificato con 5 ricerche web). I numeri in giro **si contraddicono** (es. Barcelona "€15" secondo un sito, "€12 a 5 stelle" secondo un altro).
- **Il Giappone ha la fonte unica perfetta per questo**: il Ministero degli Affari Interni (MIC) pubblica l'elenco ufficiale di tutti i comuni con tassa di soggiorno (PDF del 1/10/2026: **49 enti già in vigore + 18 già approvati con data di partenza fino a ottobre 2027**, tra cui Niseko, Hakuba, Nozawa Onsen, Okinawa, Ishigaki) e un PDF per ogni nuova tassa con importo e data. Solo in giapponese. Ho provato a leggerli in automatico: 7 PDF su 7 letti, nome dell'ente sempre giusto, data 5/7, importo completo 4/7 (gli altri li controlla Claude).
- **Le candidate che passano (6, in ordine):**
  1. **"Tourist Tax Calculator"**: tasse di soggiorno di 40-60 destinazioni (Europa, Giappone, Messico, Bali, Turchia, Egitto, Marocco) con calcolatore e data dell'ultimo controllo. **Passa** (la migliore: 1,0-4,5k €/anno a 18 mesi, stima prudente).
  2. **Modulo Giappone "accommodation tax by town"** (fonte unica MIC): è il primo pezzo da costruire del n. 1. **Passa come parte del n. 1**; da solo 0,2-0,9k €/anno.
  3. **Zone a basse emissioni per auto straniere e a noleggio** (Spagna con dati ufficiali DGT in XML aperto, Francia, Germania, Bruxelles, Lisbona, Cracovia). **Passa con riserva** (concorrenza media: 0,4-1,8k €/anno).
  4. **Calcolatore "tax-free / VAT refund"** (Giappone cambia sistema dal 1/11/2026, Corea, Thailandia, Taiwan, UE). **Satellite** del n. 1 (0,1-0,6k €/anno).
  5. **Tariffe ufficiali dei taxi contro le truffe** (Istanbul cambia 2 volte l'anno, Budapest, Praga, Lisbona, Buenos Aires). **Riserva** (per Istanbul esiste già un concorrente aggiornato).
  6. **Thailandia "is alcohol banned today?"** (giorni buddisti, elezioni, orari cambiati a fine 2025). **Piccola** (fonti ufficiali bloccate dal server, manutenzione a mano).
- **Onestà sui numeri**: nessuna di queste è "grande". La n. 1 è dello stesso ordine del sito scioperi (qualche migliaio di euro l'anno a regime), con due vantaggi: **non dipende da un solo Paese** e **ha lo stesso pubblico** di Italy Strikes Today (la tassa di soggiorno di Roma, Venezia, Firenze è tra i suggerimenti: "tourist tax italy/rome/venice", "italy tourist tax calculator rome"). Il rischio principale è che Google risponda da solo con la sua risposta AI alle domande semplici ("how much is tourist tax in X"); il calcolatore con le regole complete (stelle, stagione, età, tetto di notti) è la difesa.

---

## 1. Tabella di tutto quello che ho controllato

Legenda domanda: "3/3" = suggerimenti in USA, UK e Australia (`client=firefox&hl=en`, `gl=us|gb|au`). L'autocomplete misura la **presenza** della domanda, non il volume (Google Trends dal server risponde 429, come nello studio 14).
Verdetto: **PASSA** / **SATELLITE** (piccola, solo dentro un sito che passa) / **RISERVA** (da riprovare con una condizione) / **NO**.

| # | Paese | Bisogno | Domanda (esempi di suggerimenti) | Fonte ufficiale provata (HTTP dal server) | Concorrenza in inglese | Verdetto |
|---|---|---|---|---|---|---|
| 1 | Multi (UE + mondo) | Tassa di soggiorno + calcolatore | 3/3 su 89 parole su 92; 93 suggerimenti "calculator"; 18 con TUI/Jet2/easyJet/"from uk" | una per destinazione (tabella sez. 2.1): 200 per Kyoto, Baleari, Vienna, Porto, Edimburgo, Bali, Visitax Messico, Budapest; 403/404 per Amsterdam, Lisbona, Parigi, Berlino, AADE Grecia, GIB Turchia agli indirizzi provati | blog, giornali, Holidu (tabella maggio 2025), mappr, radicalstorage, ETOA (solo soci), pagine TUI/First Choice; nessun calcolatore multi-destinazione aggiornato | **PASSA** |
| 2 | Giappone | Tassa di soggiorno per comune | 3/3: "japan accommodation tax 2026/calculator", "kyoto accommodation tax 2026 calculator", "osaka…calculator", "niseko/hakuba/sapporo/okinawa/kanazawa/hiroshima accommodation tax", "tokyo accommodation tax april 2027" | **MIC**: `soumu.go.jp/main_content/001094503.pdf` (200, PDF testo, "法定外税の状況" al 1/10/2026); PDF di ogni nuova tassa (200); feed RSS `soumu.go.jp/news.rdf` (200) | livejapan, watabi, machiya-inn, real-japan-guide: buoni su Tokyo/Kyoto/Osaka, **assenti sui comuni piccoli** (Hakuba: solo schede hotel) | **PASSA** (dentro il n. 1) |
| 3 | Spagna, Francia, Germania, Belgio, Portogallo, Polonia | Zone a basse emissioni per auto straniere/noleggio | 3/3: "madrid low emission zone rules for tourists", "barcelona low emission zone rental car / foreign vehicles", "brussels lez register foreign vehicle", "lisbon low emission zone rental car", "krakow low emission zone registration", "germany environmental sticker where to buy" | Spagna **DGT NAP**: 45 file DATEX2 (200, XML, CC BY 4.0); Francia **BNZFE** su transport.data.gouv.fr (200, GeoJSON, disponibilità 100 % negli ultimi 30 giorni); Germania UBA (dataset geodatabase, pagina provata 404) | autoviatest.com (sito programmatico in molte lingue), green-zones.eu (vende bollini), urbanaccessregulations.eu (UE), The Local, ambasciate | **PASSA con riserva** |
| 4 | Giappone, Corea, Thailandia, Taiwan, UE | Calcolatore tax-free / rimborso IVA | 3/3: "japan tax free shopping november 2026", "japan tax refund calculator for foreigners", "korea tax refund calculator", "thailand vat refund table", "vat refund calculator france/italy/spain/germany/greece" | regole nazionali (una per Paese, stabili) | Global Blue/Planet (operatori), travelcostcalculator.org, molte pagine spam | **SATELLITE** del n. 1 |
| 5 | Turchia, Ungheria, Rep. Ceca, Portogallo, Argentina, Thailandia, Giappone | Tariffa ufficiale del taxi (anti-truffa) | 3/3: "istanbul taxi fare calculator", "istanbul airport to sultanahmet taxi fare", "budapest taxi fare calculator", "prague taxi fare calculator", "lisbon taxi fare calculator", "buenos aires taxi fare calculator", "bangkok taxi fare calculator", "tokyo taxi fare calculator" | **İBB** `tuhim.ibb.gov.tr/media/27490/2027ucretler.pdf` (200, PDF testo: apertura 71,94 TL, 47,92 TL/km, minimo 230 TL dal 20/7/2026); **BKK** Budapest pagina inglese (200, senza tabella completa); Buenos Aires 404; Praga connessione rifiutata | **hemenhesap.com** già aggiornato alla tariffa di luglio 2026 (Turchia); taxi-calculator.com (Turchia non supportata), worldtaximeter, gobytaxi (dati sbagliati) | **RISERVA** |
| 6 | Thailandia | Divieto di vendita alcol oggi / giorni buddisti / orari | 3/3: "is alcohol banned today in thailand", "thailand alcohol ban dates 2026", "is alcohol banned in thailand tomorrow", "alcohol sales times thailand today" | Commissione elettorale `ect.go.th` **403**; Gazzetta reale **403**; thaigov **403**; Banca di Thailandia festività: pagina 200 ma date caricate da API con chiave | solo notizie (Nation, Khaosod, Thaiger), nessuna pagina "oggi" | **piccola / manuale** |
| 7 | Thailandia | Parchi marini aperti/chiusi (Similan, Surin) e biglietti stranieri | 3/3: "similan islands open season 2026", "similan islands closed 2026", "koh tachai closed"; 0/3 su "thailand national parks closed season" | DNP `dnp.go.th` **bloccato da Incapsula**; `e-ticket.dnp.go.th` 200 ma app JavaScript | agenzie (tisland.travel), blog subacquei | NO come sito; 1 pagina nel n. 1 |
| 8 | Thailandia / Indonesia / Brasile / Messico | Moduli d'ingresso (TDAC, arrival card Indonesia, Bali levy, Visitax, e-visa Brasile) | 3/3, forte: "thailand tdac official website", "bali levy official website", "visitax official website" | siti ufficiali già in inglese: `tdac.immigration.go.th` 200, `lovebali.baliprov.go.id` 200, `visitax.gob.mx` 200 | siti copia/truffa: chi cerca vuole il sito ufficiale | **NO** (rischio di sembrare un sito copia; l'ente risponde già) |
| 9 | Perù | Disponibilità biglietti Machu Picchu / Inca Trail | 3/3: "machu picchu tickets availability", "machu picchu circuit 2 availability", "official inca trail permit availability" | `api-tuboleto.cultura.pe` **401** (serve autorizzazione); `machupicchu.gob.pe` errore certificato; `tuboleto.cultura.pe` app | decine di agenzie con calendari di disponibilità | **NO** |
| 10 | Spagna, Portogallo, Germania | Appuntamenti NIE / AIMA / Anmeldung | 3/3 fortissima: "nie appointment madrid", "aima appointment check", "anmeldung appointment berlin finder" | sistemi con login e captcha | strumenti già esistenti ("finder"), All About Berlin | **NO** (zona amministrativa-legale, scraping vietato) |
| 11 | Spagna, Portogallo, mondo | Requisiti visti nomadi digitali / D7 | 3/3: "spain digital nomad visa income requirements 2026", "portugal d7 visa requirements" | consolati, siti ufficiali | studi legali, grandi blog | **NO** (consulenza legale) |
| 12 | Corea, Taiwan, Thailandia, Messico, Brasile, Grecia, Portogallo, Turchia, Marocco, Colombia, Argentina | Festività 2027 / "is today a holiday" | 3/3 ovunque; "japan/vietnam/spain holidays 2027" porta però a **pacchetti vacanza** (TUI, Jet2) | calendari ufficiali statici | timeanddate (403 dal server), officeholidays: dominanti (già scartato nello studio 14) | **NO** |
| 13 | Germania, Olanda, Spagna, Francia, Polonia, Rep. Ceca, Giappone | Vacanze scolastiche 2027 (affollamento) | 3/3: "germany school holidays 2027", "netherlands school holidays 2027", "french school holidays 2027 zone c" | KMK Germania: PDF per anno (200) | `schoolholidayseurope.eu` (200, inglese, completo), schulferien.org | **NO** (concorrenza già in inglese) |
| 14 | Polonia | Domeniche con negozi aperti ("trading Sundays") | 3/3: "poland trading sundays 2026", "are stores open on sunday in poland", "non trading sundays poland" | regola fissa di legge (calcolabile); ISAP **403**; gov.pl reindirizza alla home | debole (nakordoni.eu) | **SATELLITE piccolissimo** (2 ore; pubblico piccolo) |
| 15 | Ungheria | Sabati lavorativi | 3/3: "hungary working saturdays 2026" | decreto annuale; `njt.hu` connessione vuota | debole | **NO** (pubblico minuscolo) |
| 16 | Germania | Domeniche commerciali | 3/3: "germany sunday shopping law/days" | una decisione per città (centinaia) | — | **NO** (> 3 fonti) |
| 17 | Germania | Chiusure autostrade (Autobahn) | solo 3 suggerimenti ("german autobahn closures") | API Autobahn (non provata) | — | **NO** (domanda inglese debole) |
| 18 | Messico, Colombia, Brasile | Hoy No Circula, pico y placa, rodízio | 3/3 ma **in spagnolo/portoghese** ("pico y placa medellin hoy"); in inglese solo rumore ("pico in english from spanish") | decreti comunali | media locali fortissimi | **NO** (non è un buco "inglese") |
| 19 | Messico | Contingencia ambiental CDMX | solo rumore ("tijd in mexico city") | — | — | **NO** |
| 20 | Messico | Pedaggi (toll calculator) | 3/3: "tollguru mexico toll calculator" | SCT "Traza tu ruta" (non provata) | TollGuru già nei suggerimenti | **NO** |
| 21 | Rep. Ceca, Ungheria, Portogallo | Vignette / pedaggi elettronici | 3/3: "czech vignette official site", "hungary vignette official website" | siti ufficiali in inglese: `edalnice.gov.cz/en` 200, `nemzetiutdij.hu/en` 200 | rivenditori di vignette | **NO** (l'ente risponde in inglese) |
| 22 | Argentina | Dólar blue | 3/3 ma soprattutto in spagnolo | non ufficiale per natura | bluelytics.com.ar (200, inglese), dolarhoy | **NO** (finanza + concorrenza) |
| 23 | Giappone, Corea, Thailandia | Patente internazionale | 3/3: "japan international driving permit 1949" | regole convenzioni ONU | JAF, ambasciate, venditori di IDP | **NO** (zona legale) |
| 24 | Vietnam | Patente moto per stranieri | 3/3: "vietnam motorbike license for foreigners" | legge vietnamita | blog | **NO** (zona legale, effetti sull'assicurazione) |
| 25 | Giappone, Corea | Regole rifiuti | 3/3: "japan garbage rules" | centinaia di comuni | — | **NO** (> 3 fonti) |
| 26 | Egitto | Prezzi biglietti musei/GEM | 3/3: "grand egyptian museum tickets price for foreigners" | `egymonuments.gov.eg/en/tickets` **404** (indirizzo provato) | venditori di tour, sito ufficiale GEM | **RISERVA** non verificata |
| 27 | Indonesia, Ecuador, Bhutan, EAU | Tasse d'ingresso (Komodo, Galápagos, Bhutan SDF, Tourism Dirham Dubai) | 3/3: "komodo national park fees 2026", "galapagos entrance fee 2026", "bhutan sdf for us citizens", "dubai tourism dirham fee" | una per destinazione (Dubai DET 403) | blog | dentro il n. 1 (pagine, non sito) |
| 28 | Croazia | Tassa di soggiorno per comune | 3/3: "croatia tourist tax 2026 calculator", "dubrovnik tourist tax 2026" | decisioni delle 20 contee (PDF, es. `bbz.hr`); nessun elenco nazionale trovato | blog, ETOA (solo soci) | dentro il n. 1 (solo città principali) |
| 29 | Grecia | Tassa "resilienza climatica" | 3/3: "greece tourist tax 2026 calculator", "crete/rhodes/santorini tourist tax 2026 calculator" | legge nazionale (tabella unica per stelle e stagione); `aade.gr` **403** | blog, giornali; ricerca "rhodes tourist tax calculator 2026": **nessun risultato pertinente** | dentro il n. 1 (ottima) |
| 30 | Turchia | Tassa di soggiorno 2 % | 3/3: "turkey tourist tax calculator from uk", "turkey tourist tax jet2/tui/easyjet" | legge nazionale 7194/2023 (pagina GIB provata 404) | blog, EY, vatcalc; **nessun calcolatore** trovato | dentro il n. 1 (ottima) |
| 31 | Giappone | Tassa di partenza (aumento 2026) | 3/3: "japan departure tax increase 2026", "japan departure tax july 2026" | MLIT/JTA inglese 200 | giornali | pagina dentro il n. 1 |
| 32 | Corea | K-ETA / tasse turistiche | "korea tourist tax" = solo rimborso IVA | — | — | confluisce nel n. 4 |

---

## 2. Le candidate che passano

**Ipotesi comuni per i soldi** (non sono promesse):
- **Pubblicità**: AdSense all'inizio 3-8 $ per 1.000 pagine viste (pubblico USA/UK/AU, viaggi); con **Mediavine Journey** (serve 1.000 sessioni da USA/UK/CA/AU in 30 giorni, [requisiti Mediavine](https://www.mediavine.com/mediavine-requirements/)) 10-18 $ (caso documentato di un blog viaggi: 18 $ a gennaio, studio 12).
- **Affiliazioni con commissioni pubbliche**: DiscoverCars **70 % del margine sul noleggio + 30 % sulla copertura totale, cookie 365 giorni** ([pagina ufficiale](https://www.discovercars.com/uk/affiliate)); GetYourGuide **7-8 %** (Awin 7 % base, FlexOffers "minimo 8 %", cookie 30 giorni); Booking.com **fino al 4 %** sulle prenotazioni tramite CJ/Awin (il programma diretto è stato chiuso a giugno 2025 secondo [track360](https://track360.io/blog/booking-com-affiliate-partner-program-operator-teardown-2026); il 25-40 % che si legge in giro non è confermato da fonti ufficiali); Welcome Pickups **8 % (Travelpayouts) oppure 5 € fissi a transfer (Tapfiliate)**, cookie 45 giorni; Airalo 10 %, SafetyWing 10 % (studio 12). Resa prudente delle affiliazioni: **2-5 $ ogni 1.000 visite** (studio 12).
- Cambio 1 $ ≈ 0,92 €. I volumi non si misurano dal server: le visite sotto sono ordini di grandezza.

### 2.1 Candidata 1 — "Tourist Tax Calculator": quanto paghi di tassa di soggiorno, destinazione per destinazione (PASSA)

**L'idea in una riga.** Un sito in inglese con una pagina per destinazione ("Barcelona tourist tax 2027: €X per night — calculator") e un calcolatore che gestisce i casi veri: importo fisso a persona, percentuale del prezzo (Amsterdam, Edimburgo, Vienna, Turchia), fasce di prezzo (Kyoto, Osaka, Tokyo, Hakuba), stelle e stagione (Baleari, Grecia), tetto di notti (Lisbona 7, Edimburgo 5), esenzioni per età. Sotto ogni cifra: **link all'atto ufficiale e data dell'ultimo controllo**. Le pagine "2027" escono a novembre-dicembre, quando cambiano le tariffe (1 gennaio, 1 aprile).

**Prove di domanda** (autocomplete 10/10/2026, `ac1.json`, `ac2.json`, `ac4.json`):
- 92 parole chiave sulle tasse turistiche, **89 con suggerimenti in tutti e 3 i mercati**; 789 suggerimenti diversi, **93 contengono "calculator"**, 59 contengono "2026" (in ottobre compaiono già i primi "2027": "tokyo accommodation tax 2027", "greece tourist tax 2027").
- Esempi: "tourist tax calculator majorca / greece / spain / amsterdam / budapest / barcelona / tunisia / menorca / ibiza"; "croatia tourist tax calculator for foreigners"; "prague tourist tax calculator"; "edinburgh visitor levy calculator"; "egypt tourist tax calculator"; "morocco tourist tax calculator"; "quintana roo tourist tax calculator"; "italy tourist tax calculator rome".
- **Pubblico UK da pacchetto vacanze** (Tier 1, ad alta intenzione d'acquisto): "ibiza tourist tax tui calculator", "rhodes tourist tax jet2", "turkey tourist tax calculator from uk", "turkey tourist tax easyjet", "crete tourist tax 2026 tui", "morocco tourist tax easyjet".
- Stesso pubblico del sito scioperi: "tourist tax italy", "tourist tax venice", "tourist tax rome".

**Fonti ufficiali** (scaricate il 10/10/2026; tutte gratuite e pubbliche, sono leggi o delibere, quindi riportabili citando la fonte):

| Destinazione | Fonte | HTTP | Formato | Lingua | Note |
|---|---|---|---|---|---|
| Giappone (tutti i comuni) | MIC, "法定外税の状況" `https://www.soumu.go.jp/main_content/001094503.pdf` + un PDF per ogni nuova tassa | 200 | PDF testo | giapponese | vedi candidata 2 |
| Kyoto | `https://www.city.kyoto.lg.jp/gyozai/page/0000236942.html` | 200 | HTML | giapponese | fasce 200 / 400 / 1.000 / 4.000 / 10.000 ¥ (lette nel file) |
| Baleari | `https://www.illesbalears.travel/en/baleares/sustainable-tourism-tax` | 200 | HTML (contenuto via JavaScript) | inglese/spagnolo | controllo a mano |
| Vienna | `https://www.wien.gv.at/amtswege/ortstaxe` | 200 | HTML | tedesco | |
| Porto | `https://www.porto.pt/pt/pagina/taxa-municipal-turistica` | 200 | HTML | portoghese | |
| Edimburgo | `https://www.edinburgh.gov.uk/visitorlevy` | 200 | HTML | inglese | 5 % dal 24/7/2026 |
| Bali | `https://lovebali.baliprov.go.id/` | 200 | HTML | inglese | "Tourist Levy IDR 150,000" letto nel file |
| Quintana Roo (Cancún, Tulum) | `https://www.visitax.gob.mx/sitio/` | 200 | HTML | spagnolo/inglese | |
| Budapest | `https://budapest.hu/` | 200 | HTML | ungherese | pagina della tassa da individuare |
| Amsterdam | `amsterdam.nl/en/municipal-taxes/tourist-tax/` | **403** (anti-robot) | – | – | controllo a mano trimestrale |
| Lisbona | `informacoeseservicos.lisboa.pt/.../taxa-municipal-turistica` | **403** | – | – | controllo a mano |
| Catalogna/Barcellona, Parigi, Berlino, Turchia (GIB), Grecia (AADE), Tokyo | indirizzi provati **404/403** | – | – | – | URL da ritrovare nel test (sez. "test") |
| Croazia | decisioni delle contee (es. `bbz.hr/.../Odluka-o-visini-turističke-pristojbe-...-2027.pdf`) | non scaricato | PDF | croato | solo Dubrovnik, Spalato, Zagabria, Pola, Rovigno |

Onestà sulla regola "≤ 3 fonti": qui le fonti sono **una per destinazione** (40-60), ma ognuna cambia 1-2 volte l'anno in date note. Soluzione a costo zero: (a) un controllo automatico settimanale (GitHub Actions) che salva l'impronta di ogni pagina leggibile e avvisa Claude quando cambia; (b) per le 403 un controllo a mano di Claude nella routine del lunedì, una volta al trimestre e nelle settimane "calde" (dicembre-gennaio, marzo-aprile). Il Giappone (1 fonte per ~67 enti) è l'unica parte davvero automatica.

**Concorrenza** (ricerche web del 10/10/2026):
- "tourist tax calculator Europe cities" e "tourist tax calculator by city per night": solo articoli (lovemoney, Time Out, mappr, radicalstorage, thrillophilia, travelextra) e la tabella di **Holidu ferma a maggio 2025** (ad esempio dava Edimburgo senza tassa); il calcolatore Holidu indicato da Time Out oggi dà **404** (`holidu.co.uk/tourist-tax-calculator`, `holidu.com/tourist-tax-calculator`).
- "kyoto accommodation tax 2026 calculator": "non c'è un calcolatore dedicato"; solo pagine di hotel e blog.
- "mallorca tourist tax calculator": nessun calcolatore; fonti in disaccordo sulle tariffe.
- "croatia tourist tax 2026 calculator": nessun calcolatore; ETOA ha le tariffe **solo per i soci** ("This content is exclusive to ETOA members", pagina scaricata).
- "rhodes tourist tax calculator 2026": **nessun risultato pertinente** (Google mostra Rhode Island e un sito di taxi).
- "turkey tourist tax calculator from uk": nessun calcolatore; EY, vatcalc, un blog.
- Unico concorrente "multi-strumento": travelcostcalculator.org (sito generico con 24 calcolatori, fa i rimborsi IVA, non le tasse di soggiorno per città).
- Concorrenza indiretta forte: pagine dei tour operator (First Choice/TUI "Destination tourist taxes") per i loro clienti, e la risposta AI di Google.

**Chi paga e quanto.** Pubblicità (pubblico UK/USA in fase di prenotazione, travel RPM buono) + affiliazioni coerenti con la pagina: hotel (Booking via CJ/Awin fino al 4 %), transfer dall'aeroporto (Welcome Pickups 8 % o 5 €), attività (GetYourGuide 7-8 %), auto (DiscoverCars 70 % del margine), eSIM e assicurazione (10 %). Nessun prodotto venduto da noi.

**Ricavo prudente** (assunzioni scritte):
- 40 destinazioni al lancio + pagine "2027" + calcolatore + ~67 pagine Giappone (candidata 2) ≈ 120-150 pagine.
- Indicizzazione nei mesi 2-4; picco di stagione gennaio-luglio (prenotazioni estive UK).
- **12 mesi** (ott 2027): 30.000-120.000 visite totali × (4-10 $ pubblicità + 2-5 $ affiliati) / 1.000 → **0,2-1,6k €**.
- **18 mesi** (run-rate apr 2028): 8.000-30.000 visite/mese × 12 × (10-16 $ con Journey + 2-5 $) / 1.000 → 1,0-6,9k €; scrivo **1,0-4,5k €/anno** come forbice prudente (la parte alta richiede di stare nei primi 3 risultati su molte città).
- Più piccolo dei sogni, più grande delle altre idee di questa ricerca. Passa la soglia di 1.500 € nello scenario centrale.

**Ore di costruzione** (riuso del motore Python di Italy Strikes Today: layout, pagine statiche, workflow, riquadro affiliati): **25-35 ore** per 40 destinazioni + calcolatore (in JavaScript nella pagina, nessun server) + dati in un file per destinazione (importo, unità, fasce, stagioni, età, tetto notti, fonte, data controllo) + controllo settimanale delle impronte. **Massimiliano**: 10 minuti (Netlify + Search Console), poi AdSense quando ci sono ≥ 20 pagine indicizzate.

**Rischi.**
- Una cifra sbagliata o vecchia → danno di fiducia. Difese: data "checked on" su ogni pagina, link all'atto ufficiale, frase "stima: l'importo esatto lo applica la struttura", nessun consiglio (è un'informazione pubblica, come il calcolatore del codice fiscale già approvato).
- Pagine ufficiali che bloccano i robot (Amsterdam, Lisbona, AADE): controllo a mano trimestrale, già messo nei costi.
- Risposta AI di Google sulle domande semplici: il calcolatore con 4-6 variabili è meno sostituibile; misurarlo nel test.
- Stagionalità forte (inverno debole, tranne Giappone neve).
- I tour operator possono migliorare le loro pagine.

**Test tecnico a costo zero (prima di costruire, 2-3 giorni di Claude):**
1. **Fonti**: elenco di 40 destinazioni con più suggerimenti; per ognuna trovare l'atto ufficiale con tutti i parametri (importo, unità, esenzioni, tetto). **Passa se ≥ 34/40 (85 %)** hanno la fonte ufficiale completa e **≥ 24/40 (60 %)** sono leggibili dal server (200 con l'importo nel testo) → controllabili in automatico.
2. **Buco reale**: per le stesse 40, i primi 5 risultati della ricerca web. **Passa se in ≥ 20/40 (50 %)** nessun risultato mostra la tariffa dell'anno in corso con calcolatore, oppure almeno 2 risultati si contraddicono.
3. **Controllo cambiamenti**: 14 giorni di impronte settimanali sulle pagine leggibili → **≤ 1 falso allarme a settimana ogni 10 fonti**.
4. **Dopo la pubblicazione (45 giorni)**: ≥ 70 % delle pagine indicizzate; **≥ 1.000 impressioni/settimana** in Search Console al giorno 45; chiusura o revisione se **< 200 impressioni/settimana al giorno 60**.

### 2.2 Candidata 2 — Giappone: "accommodation tax by town" con fonte unica del Ministero (PASSA, come primo modulo della 1)

**Perché è speciale.** È l'unico pezzo di questa ricerca con **una fonte ufficiale madre** che copre tutto il Paese, scritta solo in giapponese, che cambia spesso (il 2026 è l'anno della "corsa al 宿泊税": nuove tasse approvate il 13/2, il 30/6 e il 30/9/2026), con un pubblico ricchissimo (Australia sulla neve: Niseko, Hakuba, Nozawa Onsen; USA a Okinawa/Tokyo/Kyoto).

**Prove di domanda**: 3/3 su "japan accommodation tax" (con 2026, calculator, increase, for foreigners, osaka, kyoto, tokyo), "japan hotel tax calculator", "japan lodging tax expansion 20 regions", "kyoto accommodation tax 2026 calculator", "osaka accommodation tax calculator", "tokyo accommodation tax april 2027", "niseko town accommodation tax", "hakuba village accommodation tax", "sapporo/hiroshima/nagano/miyagi/kanazawa/fukuoka/okinawa accommodation tax"; 0/3 solo su "nozawa onsen accommodation tax" e "japan accommodation tax by city".

**Fonte** (scaricata e letta il 10/10/2026):
- `https://www.soumu.go.jp/main_content/001094503.pdf` — "法定外税の状況 (令和8年10月1日現在)", 200, 458 KB, 1 pagina di testo: **7 prefetture + 42 comuni in vigore** (Tokyo, Osaka, Fukuoka, Miyagi, Hokkaido, Hiroshima, Nagano; Kyoto, Kanazawa, Kutchan/Niseko, Sapporo, Hakuba, Nozawa Onsen, Karuizawa, Kumamoto…) e **18 enti già approvati** con data (Oita da gen 2027; Okinawa, Ishigaki, Miyakojima, Nago, Motobu, Onna, Chatan 1/2/2027; Wakkanai e Shirahama 1/3/2027; Tomakomai, Yamagata, Fujiyoshida, Fujikawaguchiko, Unzen, Kagoshima, Ibusuki 1/4/2027; Kitahiroshima ottobre 2027).
- PDF di ogni nuova tassa (`/main_content/001093327.pdf` Ibusuki, `001080171` Tomakomai "3 % del prezzo", `001055669` Matsumoto, `001033234` Yugawara, `001021347` Hakodate, `001082739` Toyako, `001082762` Nagano): 200, testo strutturato (課税団体, 税率, 課税免除, 条例施行).
- Avvisi: feed `https://www.soumu.go.jp/news.rdf` (200, XML) e pagina 法定外税 `.../czaisei_seido/149767_24.html` (200).
- Licenza: contenuti dei ministeri giapponesi riutilizzabili con citazione (Public Data License 1.0, come per la JMA nello studio 14; da riconfermare sul sito MIC).

**Prova di lettura automatica** (`script/mic.py`): su 7 PDF di tasse di soggiorno → **ente 7/7, data di partenza 5/7, importo completo 4/7** (le fasce su più righe vanno sistemate). Quindi: lettura automatica + controllo di Claude su ogni nuova delibera (sono 5-20 l'anno, a blocchi).

**Concorrenza**: livejapan.com (grande portale, articolo generale 2026), watabi.org, machiya-inn-japan, real-japan-guide ("non è un elenco di tutti i comuni"). Sui comuni piccoli non c'è nessuno: la ricerca "hakuba accommodation tax 2026 how much per night" restituisce solo schede di hotel (ikyu, tiket, Marriott) e si contraddice sulla parte prefettizia.

**Soldi**: dentro la candidata 1. Da solo: 10.000-40.000 visite/anno a 18 mesi → **0,2-0,9k €/anno** (pubblicità + eSIM/JR/attività/hotel). Non passa da solo, passa come parte del sito.

**Ore**: 8-12 (lettore PDF MIC, ~67 pagine-ente generate, pagina "new taxes coming in 2027", calcolatore a fasce).

**Rischi**: il MIC può cambiare il nome del file a ogni aggiornamento (l'indirizzo si ritrova dalla pagina 149767_24); dettagli come la "doppia tassa" prefettura + comune vanno spiegati bene (Nagano + Hakuba).

**Test tecnico a costo zero (30 giorni, solo Claude)**: lettura giornaliera di `news.rdf` e settimanale della pagina 149767_24 → **≥ 95 % risposte 200**; su tutti i nuovi PDF "宿泊税" del periodo e sui 7 già scaricati: **ente 100 %, data ≥ 80 %, importo ≥ 80 %** in automatico dopo la correzione del lettore; confronto con 10 pagine ufficiali dei comuni: **≥ 9/10 coincidenze**.

### 2.3 Candidata 3 — Zone a basse emissioni per auto straniere e a noleggio (PASSA con riserva)

**L'idea.** "Can I drive my UK/foreign car (or rental car) into the Madrid / Barcelona / Malaga / Valencia / Lyon / Brussels / Lisbon / Krakow low emission zone?" Una pagina per città con: chi può entrare (bollino richiesto), orari, se l'auto straniera deve registrarsi e dove, multa, e una frase semplice per l'auto a noleggio. Pubblico: inglesi in auto o camper verso Spagna e Francia, turisti con auto a noleggio.

**Prove di domanda**: 3/3 su "madrid low emission zone rules for tourists (map)", "madrid low emission zone foreign cars / rental car / registration", "barcelona low emission zone tourist / rental car / foreign vehicles / registration", "zbe spain map / registration / sticker", "spain low emission zone foreign cars", "brussels lez register foreign vehicle / day pass", "antwerp lez registration", "lisbon low emission zone rental car", "krakow low emission zone registration / fine", "warsaw low emission zone", "belgium low emission zone registration", "netherlands low emission zone registration", "germany environmental sticker where to buy / anwb", "italy low emission zone rental car".

**Fonti** (10/10/2026):
- **Spagna**: DGT, Punto de Acceso Nacional, dataset "Low Emission Zones (LEZ)" `https://nap.dgt.es/en/dataset/zonas-de-bajas-emisiones` (200): **45 file** `https://nap.dgt.es/datex2/v3/dgt/zbe/ControledZonePublication/<Città>.xml` (scaricati Madrid 7,3 MB, Málaga, Valencia, Barcellona, Palma, Bilbao: tutti 200). Formato DATEX2 v3 con contorno, bollini ammessi (es. Málaga: vietato a chi non ha "0, ECO, C, B"), orari, data d'inizio, link all'ordinanza. Licenza **CC BY 4.0**, aggiornamento "a ogni cambio" (dalla scheda). Limite: **la regola per le targhe straniere non è nei dati** (va presa dalle ordinanze) e alcune date di pubblicazione sono del 2025.
- **Francia**: Base nazionale BNZFE su `https://transport.data.gouv.fr/resources/79568` (200; file `aires.geojson` e `voies.geojson`, regole per bollino Crit'Air e date; disponibilità 100 % negli ultimi 30 giorni). data.gouv.fr ha rifiutato la connessione dal server (reset), il portale trasporti no.
- **Germania**: dataset UBA "Umweltzonen in Deutschland" (geodatabase su INSPIRE, ultima revisione 24/6/2025); 35 zone attive secondo fonti secondarie; quasi tutte "bollino verde" → una sola pagina.
- **Bruxelles** `https://lez.brussels/mytax/en/` (200, inglese), **Olanda** `https://www.milieuzones.nl/english` (200, inglese), **Cracovia** pagina comunale (200, polacco).
- Fonti madri: 3 (DGT, BNZFE, UBA) + 4-6 pagine città per le regole sulle targhe straniere.

**Concorrenza**: forte-media. **autoviatest.com** (sito programmatico con la stessa pagina in decine di versioni regionali, primo su "madrid low emission zone rules for tourists"), green-zones.eu (vende bollini), urbanaccessregulations.eu (progetto UE), The Local, ambasciata tedesca, Parclick. È lo stesso schema "pagine per città", già occupato in parte.

**Chi paga**: pubblicità (pubblico auto/viaggi) + **DiscoverCars 70 % del margine** (chi chiede "rental car" sta noleggiando) + parcheggi (Parclick ha un programma? **non trovato**) + eventuale venditore di bollini (programma **non verificato**).

**Ricavo prudente**: 12 mesi **0,1-0,6k €**; 18 mesi **0,4-1,8k €/anno** (30.000-100.000 visite/anno). Passa la soglia solo nello scenario alto: lo dico chiaramente.

**Ore**: 15-25 (lettore DATEX2 e GeoJSON, mappa semplice opzionale, 50-60 pagine città, testo per targhe straniere).

**Rischi**: responsabilità (una multa presa dopo aver letto la pagina) → solo "lo dice l'ordinanza del [data]" con link; regole in movimento (Francia: dibattito politico sull'abolizione delle ZFE nel 2025, stato da verificare); concorrente programmatico già posizionato.

**Test tecnico (5 giorni, solo Claude)**: scaricare i 45 XML DGT per 14 giorni → **≥ 95 % 200**; lettura di bollini e orari **≥ 90 % delle zone**; confronto con il sito ufficiale di 10 città a caso → **≥ 9/10 coincidenze**; regola "targa straniera" trovata su fonte ufficiale per **≥ 12 delle 15 città** più cercate. Se una di queste soglie non passa → NO.

### 2.4 Candidata 4 — Calcolatore "tax-free shopping / VAT refund" (SATELLITE della 1)

- **Domanda**: 3/3 su "japan tax free shopping november 2026", "japan tax free shopping changes 2026", "japan tax refund calculator for foreigners", "japan tax free limit per person", "korea tax refund calculator (tourist)", "korea tax refund hotel list", "thailand vat refund table / calculator", "taiwan tax refund rate", "vat refund calculator france / italy / spain / germany / greece / uae / denmark", "tax free shopping calculator spain".
- **Fonte**: una regola nazionale per Paese (aliquota, minimo d'acquisto, tempi). Il Giappone passa al **sistema a rimborso dal 1/11/2026** (minimo 5.000 ¥, niente tetto di 500.000 ¥ per i consumabili, 90 giorni: da fonti secondarie gltjp, japantravel; atto ufficiale del Ministero delle Finanze/JTA **da collegare nel test**).
- **Concorrenza**: Global Blue e Planet (gli operatori dei rimborsi hanno i loro calcolatori), travelcostcalculator.org, molte pagine spam ("Global Blue refund calculator + tips" su domini casuali). Media-forte.
- **Soldi**: pubblicità; affiliazioni deboli (lo shopping non ha un programma naturale). **0,1-0,6k €/anno a 18 mesi.**
- **Ore**: 6-10 dentro il sito 1. **Test**: regola ufficiale trovata per **≥ 9/10** Paesi (JP, KR, TH, TW, ES, FR, IT, DE, GR, PT); se meno → solo Giappone e Corea.

### 2.5 Candidata 5 — Tariffe ufficiali dei taxi contro le truffe (RISERVA)

- **Domanda**: 3/3 su "[città] taxi fare calculator" per Istanbul, Budapest, Praga, Lisbona, Buenos Aires, Bangkok, Tokyo, Marrakech; "istanbul airport to sultanahmet / taksim / kadikoy taxi fare"; "budapest taxi price per km"; "prague taxi prices from airport".
- **Fonti**: Istanbul **İBB** `https://tuhim.ibb.gov.tr/media/27490/2027ucretler.pdf` (200, 17 pagine di testo: taxi, dolmuş, minibus; dal 20/7/2026 apertura 71,94 TL, 47,92 TL/km, minimo 230 TL; cambia ~2 volte l'anno con l'inflazione, e l'indirizzo cambia a ogni versione); Budapest BKK `https://bkk.hu/en/travel-information/taxi-services/` (200, in inglese; supplemento aeroporto 2.100 HUF da agosto 2026); Buenos Aires indirizzo provato 404; Praga connessione rifiutata.
- **Concorrenza**: **hemenhesap.com** ha già pagine inglesi con la tariffa ufficiale di luglio 2026 e un "Turkey Taxi Price Index" (cioè il buco su Istanbul è già chiuso da un sito automatico); per le altre città, taxi-calculator.com, worldtaximeter.com, gobytaxi (dati sbagliati, es. "base fee 1 HUF"). Le ricerche web mostrano molte cifre vecchie (Istanbul "₺35/km", "₺54"), segno che il buco esiste fuori dalla Turchia.
- **Soldi**: transfer (Welcome Pickups 8 % o 5 €) + pubblicità. **0,3-1,2k €/anno a 18 mesi.**
- **Ore**: 10-15 (tariffe + 8-10 tragitti aeroporto→quartieri calcolati una volta con le distanze di OpenStreetMap).
- **Perché riserva**: per Istanbul c'è già un concorrente aggiornato; serve prima il test "≥ 7 città su 10 con tariffa ufficiale leggibile e ≥ 5 su 10 con risultati inglesi vecchi o sbagliati". Se passa, diventa una sezione del sito 1 ("travel costs set by law"), non un sito a parte.

### 2.6 Candidata 6 — Thailandia: "Is alcohol banned today?" (PICCOLA)

- **Domanda**: 3/3 su "thailand alcohol ban today", "is alcohol banned today in thailand", "is alcohol banned in thailand tomorrow", "thailand alcohol ban dates 2026", "alcohol sales times thailand today", "is today a buddhist holiday in thailand".
- **Perché interessa**: le regole sono cambiate (fine 2025: orari 11-24 e sospensione in prova del divieto 14-17 per 180 giorni, secondo Food Manufacturing e Free Malaysia Today; esito della prova **non trovato**), ci sono divieti nei giorni buddisti (es. 29-30/7/2026) e nelle elezioni (7-8/2/2026; Bangkok e Pattaya 27-28/6/2026). In inglese rispondono solo notizie del giorno.
- **Fonti**: tutte le ufficiali provate sono **bloccate dal server** (Commissione elettorale 403, Gazzetta reale 403, governo 403; festività della Banca di Thailandia caricate da un'API con chiave). Le date buddiste si conoscono con un anno di anticipo, le elezioni no.
- **Soldi**: **0,1-0,5k €/anno**. Ore: 4-6. Manutenzione a mano (Claude, 5-8 date l'anno). Da fare solo se avanza tempo, come pagina dentro il sito 1 ("Thailand: fees and rules for visitors").

---

## 3. Idee scartate, con il motivo e la prova

| Idea | Motivo | Prova (10/10/2026) |
|---|---|---|
| Moduli d'ingresso (Thailandia TDAC, Indonesia arrival card, Bali levy, Visitax, e-visa Brasile) | chi cerca vuole il **sito ufficiale**, che esiste già in inglese; un sito terzo sembrerebbe una copia (regola: niente pagine che imitano enti) | `tdac.immigration.go.th` 200 (reindirizza al modulo), `lovebali.baliprov.go.id` 200 in inglese, `visitax.gob.mx` 200; suggerimenti "…official website" in tutti i casi |
| Disponibilità biglietti Machu Picchu / Inca Trail | fonte chiusa e mercato delle agenzie | `api-tuboleto.cultura.pe/.../disponibilidad` **401**; `machupicchu.gob.pe` errore di certificato; `tuboleto.cultura.pe` app JavaScript |
| Appuntamenti NIE, AIMA, Anmeldung | sistemi con login/captcha, area amministrativo-legale, strumenti già esistenti | suggerimenti "anmeldung appointment berlin finder", "aima appointment check" |
| Visti nomadi digitali, D7, residenza | consulenza legale (esclusa) | suggerimenti "…income requirements 2026" |
| Festività 2027 per Paese, "is today a holiday" | timeanddate/officeholidays dominano (già scartato nello studio 14); "japan/vietnam/spain holidays 2027" = pacchetti TUI/Jet2 | `timeanddate.com/holidays/thailand/2027` 403 dal server; suggerimenti "japan holidays 2027 tui" |
| Vacanze scolastiche europee | concorrente inglese completo | `schoolholidayseurope.eu` 200; KMK 200 (`FER2026_27.pdf`) ma già ripreso da tutti |
| Domeniche commerciali Polonia | domanda 3/3 ma pubblico piccolo e ricavo minimo | regola fissa di legge; ISAP 403; unico concorrente nakordoni.eu |
| Sabati lavorativi Ungheria | pubblico minuscolo | `njt.hu` risposta vuota |
| Domeniche commerciali Germania | una fonte per città | — |
| Chiusure Autobahn | domanda inglese quasi assente | solo "german autobahn closures" |
| Hoy No Circula, pico y placa, rodízio | domanda locale in spagnolo/portoghese, non "buco inglese" | suggerimenti in spagnolo; "pico y placa medellin english" = traduzioni |
| Contingencia ambiental Città del Messico | nessuna domanda in inglese | suggerimenti fuori tema ("tijd in mexico city") |
| Pedaggi Messico | TollGuru già nei suggerimenti | "tollguru mexico toll calculator" |
| Vignette Rep. Ceca/Ungheria, pedaggi Portogallo | ente già in inglese, venditori forti | `edalnice.gov.cz/en` 200, `nemzetiutdij.hu/en` 200 |
| Dólar blue Argentina | dato finanziario e concorrenza in inglese | `bluelytics.com.ar` 200 |
| Patente internazionale, patente moto Vietnam | area legale (e assicurativa) | suggerimenti "…1949", "…for foreigners" |
| Regole dei rifiuti Giappone/Corea | centinaia di comuni | — |
| Parchi marini thailandesi (Similan) come sito | fonte bloccata, date fisse note (15/10-15/5) coperte da agenzie | `dnp.go.th` blocco Incapsula; e-ticket app JS |
| Prezzi musei Egitto / GEM | indirizzo ufficiale provato 404; da riprovare | `egymonuments.gov.eg/en/tickets` 404 |
| Nyepi, Tết, Kurban Bayramı (date) | date statiche, ricerche soprattutto in lingua locale | "nyepi 2027 tanggal berapa", "tet 2027 ngay nao" |

---

## 4. Cosa farei (ordine e tempi)

1. **Test tecnici a costo zero** (Claude, 3-5 giorni, nessun credito Netlify): prima il **Giappone MIC** (30 giorni di lettura silenziosa del feed, ma il controllo delle fonti si fa subito), poi l'**audit delle 40 destinazioni** della candidata 1 con le soglie scritte sopra.
2. Se passano: **un solo sito nuovo "Tourist Tax Calculator"** (25-35 ore + 8-12 per il Giappone), con la sezione Italia (Roma, Venezia, Firenze, Milano: stesso pubblico di Italy Strikes Today, link incrociati). Uscita delle pagine "2027" entro dicembre 2026, quando cambiano le tariffe e cominciano le prenotazioni estive UK.
3. Zone a basse emissioni (candidata 3) solo dopo i verdetti del 23-24/11 sui siti attuali e solo se il suo test passa; calcolatore tax-free e taxi come sezioni del sito 1, non siti separati.
4. Massimiliano: 10 minuti (Netlify + Search Console) quando il sito è pronto; AdSense dopo ≥ 20 pagine indicizzate; iscrizioni affiliati già in corso (GetYourGuide, DiscoverCars, Welcome Pickups via Travelpayouts, Booking via CJ/Awin).

**Numeri onesti per il portafoglio di questa ricerca** (candidate 1 + 2 + 4 come un sito solo): **12 mesi 0,3-1,8k €; 18 mesi 1,2-5k €/anno**. Con la candidata 3 in più: +0,4-1,8k €. Non cambia la conclusione della strategia ("somma di molte pagine piccole"), ma aggiunge una famiglia di pagine **non legata a un solo Paese** e con domanda già misurata.

---

## 5. Cosa resta non provato
- Volumi di ricerca reali (Trends 429 dal server; Search Console li darà solo dopo la pubblicazione).
- Indirizzi esatti delle pagine ufficiali di Catalogna/Barcellona, Parigi, Berlino, Turchia (GIB), Grecia (AADE), Tokyo: quelli provati danno 404/403; vanno ritrovati nel test (sono atti pubblici, esistono).
- Licenza esplicita del MIC (presunta come per gli altri ministeri giapponesi: da confermare).
- Programmi di affiliazione per bollini ZTL/ZBE e parcheggi: non trovati.
- Stato politico delle ZFE francesi nel 2026: da verificare prima di costruire la candidata 3.
