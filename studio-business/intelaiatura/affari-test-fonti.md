# Sito "affari" (case all'asta con sconto sull'OMI + eBay) – Test tecnico delle fonti

Data del test: **14 ottobre 2026** (tutti i conteggi, gli HTTP status e le citazioni sono di questa data). Test leggero, non ricerca profonda. Spesa: zero. Nessuna pagina costruita, nessun dato personale salvato o pubblicato.
Riferimenti: le 5 condizioni di `1-candidati.md` (sez. 0) e il modello di `STRATEGIA.md` (sito gratuito da dati pubblici, ricavi da pubblicità/affiliati, tutto automatico, niente email a freddo, niente dati personali, niente vendite dirette prima della risposta fiscale).
Nota: il 9/10/2026 le aste PVP erano state scartate per la **condizione 3** (aggregatori enormi, `1-candidati.md` sez. 4). Questo test serve a capire se l'angolo nuovo, **"sconto rispetto al valore OMI di zona"**, cambia il quadro.

## 0. Esito in breve

| Parte | Verdetto | Perché, in una riga |
|---|---|---|
| **(a) Case all'asta + valori OMI** | **PASSA** (con una riserva sulla concorrenza) | Il PVP ha un'interfaccia JSON pubblica senza login con prezzo base, offerta minima, data, comune, coordinate e stato di occupazione; l'OMI è **CC BY 4.0** con perimetri di zona leggibili; il calcolo "sconto sull'OMI" funziona (5 esempi sotto) e nessun concorrente trovato lo mostra. Riserva: i siti grandi ripubblicano già le stesse aste, quindi si punta solo alle ricerche di coda lunga (zona, fascia di prezzo). |
| **(b) Annunci eBay (Browse API + EPN)** | **NON PASSA** (per ora) | L'uso delle Buy API in produzione "is intended for eBay partners only" e richiede una domanda approvata da eBay senza garanzia; commissioni 1-4 % con tetto e finestra di 24 ore; veicoli su eBay.it marginali; non esiste un "valore ufficiale" con cui dire che un oggetto è un affare. Resa stimata troppo bassa per il lavoro richiesto. |

Le 5 condizioni per la parte (a):

| # | Condizione | Esito | Prova principale |
|---|---|---|---|
| 1 | Soldi in gioco | **SÌ** | Case da 30.000 a oltre 1 milione di euro; chi compra cerca anche il mutuo ("mutuo per casa all'asta" e 9 varianti in autocomplete, sez. 5). |
| 2 | Dati raccolti in automatico ≥ 80 % da fonti pubbliche | **SÌ per le aste, PARZIALE per lo sconto** | Prezzo base, offerta minima, data, comune: ~100 %. Coordinate ~76 % nelle tre città (Roma 86 %, Milano 73 %, Torino 42 %). Metri quadri scritti nel testo dell'annuncio solo nel **~40 %** dei lotti residenziali (12 su 28 nel campione): per il resto servirebbe leggere il PDF dell'avviso (sez. 1.4). |
| 3 | Canale gratuito + concorrenti deboli | **DEBOLE** | La domanda c'è (sez. 5), ma su "case all'asta [città]" ci sono immobiliare.it, idealista, casa.it, asteannunci, astegiudiziarie, Wikicasa. Nessuno mostra lo sconto sull'OMI per lotto (sez. 4). |
| 4 | Due parti da mettere in contatto (fase 2) | **SÌ** | Chi compra all'asta ↔ mediatori del credito (mutuo per l'asta) e professionisti che assistono nelle aste. |
| 5 | Lavoro umano quasi zero, nessuna responsabilità personale | **SÌ, con regole scritte** | Tutto è automatico. Rischi gestibili: mai dati del debitore, mai la parola "affare" come promessa, link sempre al PVP (sez. 6). |

## 1. Portale delle Vendite Pubbliche (PVP)

### 1.1 Si può leggere in automatico? Sì, con un'interfaccia JSON pubblica

Il sito [pvp.giustizia.it](https://pvp.giustizia.it/pvp/) è una pagina Angular che chiama servizi JSON **senza login, senza chiave e senza cookie**. Li ho trovati guardando le richieste del browser e li ho richiamati con `curl`:

| Servizio | Metodo e indirizzo | Esito 14/10 | Cosa dà |
|---|---|---|---|
| Ricerca vendite | `POST https://pvp.giustizia.it/ric-496b258c-986a1b71/ric-ms/ricerca/vendite?language=it&page=0&size=100&sort=dataOraVendita,desc` con corpo `{"tipoLotto":"IMMOBILI","flagRicerca":1,"localita":"Roma"}` oppure `{"tipoLotto":"IMMOBILI","tribunale":"Tribunale di ROMA"}` | **200**, 100 risultati per pagina | id, tipo e categoria, indirizzo con **coordinate**, n. lotto, n. procedura, **prezzo base**, **offerta minima**, rilancio minimo, **data e ora della vendita**, data di pubblicazione, **disponibilità** (LIBER / OCCUP / OCCST / INCOR / NON_SPECIFICATA), descrizione breve, tribunale, **esito** (aggiudicato / non aggiudicato) |
| Dettaglio | `GET https://pvp.giustizia.it/ve-3f723b85-986a1b71/ve-ms/vendite/{id}/restricted` | **200** | in più: tipo di vendita (senza incanto, asincrona telematica…), termine per le offerte, descrizione lunga dei beni, dati catastali (foglio, particella, subalterno), codice ISTAT del comune, siti dove è pubblicato, elenco allegati (ordinanza, avviso, perizia) e **"soggetti"** (vedi sotto) |
| Vendite precedenti | `GET .../ve-ms/vendite/lotti/{idLotto}/vendite-precedenti` | **200** ma vuoto | dovrebbe dare i tentativi precedenti; era vuoto anche per un lotto con "II Avviso di vendita" nel nome del file: **non affidabile** |
| Filtri | `GET .../bo-ms/filtriRicercaVendite` | **200** | elenco regioni, province e comuni con codici ISTAT |

Nella ricerca **non c'è un filtro per data**: restituisce anche le aste dal 2018. Il metodo che funziona è ordinare per data decrescente e fermarsi alla prima pagina con aste già passate.

**Non esistono** open data, file da scaricare o API documentate per il pubblico. Le [specifiche tecniche 2024](https://pst.giustizia.it/PST/resources/cms/documents/PVP_ST_Allegato_A_V1.2_18092024.pdf) (versione 1.2 del 18/9/2024) descrivono un'"area pubblica a cui si accede senza l'impiego di apposite credenziali, per la ricerca e la visualizzazione delle inserzioni", più la newsletter ufficiale per zona e la prenotazione della visita. Gli indirizzi JSON sopra **contengono codici di versione** (`ric-496b258c-986a1b71`): possono cambiare a ogni aggiornamento del portale, quindi lo script deve ricavarli ogni volta dalla home page (si trovano nel codice della pagina) e avvisare se smettono di rispondere.

### 1.2 Quali campi ci sono davvero (richiesti nel test)

| Campo richiesto | Presente? | Note |
|---|---|---|
| Prezzo base | **sì**, ~100 % | `prezzoBaseAsta` |
| Offerta minima | **sì**, ~100 % (Roma 399/402) | a Milano risulta spesso **uguale** al prezzo base (es. lotti 4639587 e 4633354): va controllato nell'avviso, potrebbe essere un errore di inserimento |
| Numero del tentativo d'asta | **no, come campo** | si ricava solo dal nome del file dell'avviso ("I_ esperimento", "II Avviso di vendita"): nel campione 6 lotti su 28 (21 %). Il servizio "vendite precedenti" è vuoto |
| Comune | **sì** | `citta` + codice ISTAT nel dettaglio |
| Indirizzo | **sì** | testo libero, a volte con il numero catastale diverso da quello reale |
| Coordinate | **sì, ~76 %** | Roma 347/402, Milano 40/55, Torino 51/121 (a Torino serve trasformare l'indirizzo in coordinate) |
| Stato di occupazione | **sì, ma metà non specificato** | Roma comune: libero 57, occupato 66, non specificato 154 su 311 |
| Date | **sì** | data/ora vendita, termine offerte, data pubblicazione. **Errori di battitura**: alcune aste risultano nel 2088, 2918, 3019 → si scartano le date oltre i 24 mesi |
| Superficie (m²) | **no, come campo** (`superficie: null`) | solo nel testo: ~40 % dei lotti residenziali (campione di 28 dettagli: 12) |

### 1.3 Quante aste attive (vendita dal 14/10/2026 in poi)

Conteggio con l'interfaccia JSON, ordinando per data e fermandosi alle aste passate.

| | Lotti immobiliari attivi | di cui nel comune | di cui residenziali (comune) | Archivio totale (tutte le date) |
|---|---|---|---|---|
| **Roma** – ricerca per località "Roma" | 402 | **321** (Roma città) | 164 (Tribunale di Roma) | 5.431 |
| **Roma** – Tribunale di Roma | **490** | 311 | 164 | 6.602 |
| **Milano** – ricerca per località | 55 | **55** | 28 | 1.821 |
| **Milano** – Tribunale di Milano | **271** | 52 | 28 | 7.440 |
| **Torino** – ricerca per località | 121 | **113** | 74 | 2.568 |
| **Torino** – Tribunale di Torino | **291** | 109 | 72 | 5.311 |
| **Italia, beni mobili** | **6.197** (6.151 con data plausibile) | – | – | 50.808 |
| … di cui autoveicoli e cicli | **1.389** (autovetture 559, mezzi commerciali 448) | Milano 74, Roma 56, Torino 45 per provincia | – | – |
| **Italia, immobili** | **18.023** (17.991 con data plausibile; residenziali 9.724) | – | – | 272.395 |

Le date delle aste attive vanno da oggi a fine gennaio 2027 (le aste si pubblicano 45-90 giorni prima). Il 14/10 la home mostrava già lotti pubblicati lo stesso giorno: **i dati si aggiornano ogni giorno**. Milano città ha poche aste rispetto al suo tribunale (55 contro 271): la maggior parte è nell'hinterland.

Per confronto, il 14/10 una ricerca web mostrava per Roma "2.992 annunci" su immobiliare.it, "2.890" su casa.it, "405" su idealista e "387" su asteannunci ([risultati](https://www.asteannunci.it/aste-giudiziarie-roma)). I numeri molto più alti dei due portali grandi fanno pensare che contino anche provincia e aste concluse: è un punto debole loro (freschezza), non verificato perché i loro siti rispondono 403 al nostro server.

### 1.4 Dati personali dentro il PVP (punto delicato)

- Il dettaglio JSON contiene nella voce `soggetti` **nome, cognome, email e codice fiscale** del professionista delegato e del custode, e il nome del giudice. Sono dati pubblicati per legge per la procedura, ma **il nostro sito non li deve mai salvare né mostrare**: lo script legge solo i campi della scheda del bene e scarta `soggetti` e `allegati` già in lettura.
- Gli allegati (perizia, avviso, foto) dovrebbero essere oscurati dal delegato, che se ne assume la responsabilità. Le specifiche 2024 ricordano l'obbligo di "rimuovere dalla documentazione allegata le generalità e gli altri dati identificativi delle persone fisiche cui appartengono i beni". I nomi dei file nel campione ("PERIZIA PRIVACY", "PERIZIA SENZA NOMI", "Integrazione CTU_Omissis") confermano che l'oscuramento si fa, ma **non sempre si può verificare**: noi non copiamo, non riassumiamo e non indicizziamo mai i PDF. Mostriamo solo il link al PVP.
- Se un giorno servono i metri quadri dal PDF dell'avviso, lo script estrae **solo il numero** in memoria e butta il resto.
- Il JSON ha anche i campi `aiGenerated` e `duplicato`: il portale stesso segnala annunci doppi.

### 1.5 Condizioni d'uso: si può ripubblicare?

- Il PVP **non ha una pagina di note legali o di licenza**. Ho letto la [Guida al sito](https://pvp.giustizia.it/pvp/it/guida.page) e l'[Informativa e consenso cookie](https://pvp.giustizia.it/pvp/it/consent_cookie.page): nessun divieto di riuso, nessuna licenza. L'informativa dice: "I dati giudiziari vengono trattati e diffusi solo ove autorizzato, consentito o imposto da espressa disposizione di legge" e "Il Ministero della Giustizia non risponde del trattamento di dati effettuato dai siti web esterni che cooperano con il Portale".
- Senza una licenza espressa vale la regola generale italiana "open by default" (art. 52, comma 2, del Codice dell'amministrazione digitale): i dati pubblicati da una PA senza licenza si considerano dati aperti, **esclusi i dati personali**. È la mia lettura, non un parere legale.
- Nella pratica la ripubblicazione è già diffusa: il PVP stesso elenca per ogni lotto i siti dove compare ("Pubblicato anche in: asteannunci.it, fallcoaste.it, astegiudiziarie.it, idealista.it, tribunale.roma.it, casa.it", lotto [4638162](https://pvp.giustizia.it/pvp/it/detail_annuncio.page?idAnnuncio=4638162)) e Wikicasa scrive di essere una "ripubblicazione gratuita e indipendente" del PVP (riassunto della ricerca web del 14/10).
- **Attenzione**: alcuni PDF di ordinanze riportano un avviso del tipo "documento destinato a uso esclusivo personale, vietata la ripubblicazione o riproduzione a scopo commerciale" (riassunto della ricerca web su un'ordinanza del Tribunale di Bari). Altra ragione per **non toccare mai i PDF**: si usano solo i campi strutturati e il link.

### 1.6 Blocchi anti-robot (osservati)

- `robots.txt`: assente (404).
- Il firewall del Ministero **blocca il browser automatico con la sua firma standard** ("The URL you requested has been blocked"); con una firma da browser normale passa.
- Dopo circa 60-150 richieste di fila a 1,5-3 secondi l'una arrivano **"Connection reset by peer"**: il conteggio nazionale (181 pagine da 100, a 3 s l'una) ha avuto 5 reset, superati con nuovi tentativi dopo 20-120 s. Per un sito servono **poche centinaia di richieste al giorno** (solo pagine nuove + controllo esiti), a 3 secondi l'una, con nuovi tentativi: si regge.
- Il portale ha fermi programmati (es. "FERMO del Portale... 11 Settembre 2026" nelle notizie): lo script deve tollerare giorni senza dati.

## 2. Valori OMI (Agenzia delle Entrate)

### 2.1 Licenza e accesso

Dalla pagina [Forniture dati OMI](https://www.agenziaentrate.gov.it/portale/schede/fabbricatiterreni/omi/forniture-dati-omi) ("Ultimo aggiornamento: 5 ottobre 2026"), citazioni testuali:

- "Il servizio "Forniture dati OMI" consente il download gratuito delle quotazioni immobiliari, dei perimetri delle zone OMI e dei volumi di compravendita (dettaglio comunale) ... ed è destinato agli utenti che accedono ai servizi telematici disponibili nell'area riservata dell'Agenzia."
- "I servizi di consultazione e fruizione delle banche dati dell'Osservatorio del mercato immobiliare dell'Agenzia delle Entrate sono disponibili con licenza **CC-BY 4.0**."
- "... è obbligatorio citarne correttamente la titolarità: «Agenzia delle Entrate – OMI»."
- "L'Agenzia non è altresì responsabile nei casi in cui, dall'utilizzo dei servizi, anche mediante collegamento con altre fonti informative, siano ricostruite, inferite o divulgate informazioni riconducibili a persone fisiche identificate o identificabili."
- "Nel caso di attività dell'utente che possano compromettere, limitare o disturbare il corretto funzionamento dei servizi, l'accesso allo stesso potrebbe essere sospeso o limitato."
- Perimetri: "Possono essere richiesti, gratuitamente, per l'intero territorio nazionale ... i perimetri (file in formato kml) delle zone OMI ... dal 2° semestre 2010."

Quindi: **riuso commerciale permesso** con la citazione "Agenzia delle Entrate – OMI". Il download completo (CSV dei valori + KML delle zone, tutta Italia) richiede l'accesso all'area riservata con SPID: **10 minuti di Massimiliano ogni semestre**.

### 2.2 Abbinare un indirizzo d'asta alla zona OMI: funziona

Anche senza login, la consultazione pubblica [GEOPOI](https://www1.agenziaentrate.gov.it/servizi/geopoi_omi/index.htm) usa tre indirizzi leggibili:

| Indirizzo | Esito 14/10 | Cosa dà |
|---|---|---|
| `zoneomi.php?richiesta=5` | 200 | semestri disponibili: l'ultimo è **2025/2** |
| `zoneomi.php?richiesta=6&codcom=H501&semestre=20252` | 200, 6,5 MB | **poligoni GeoJSON** di tutte le zone OMI del comune (Roma: **233 zone**; Milano F205: 1,3 MB; Torino L219: 1,1 MB) |
| `zoneomi.php?richiesta=8&codcom=H501&semestre=20252&zo=C1` + `stampaomi.php?...` | 200 | valori €/m² min/max per tipologia (abitazioni civili, economiche, signorili, ville, box), stato conservativo, superficie lorda/netta, affitti |

Metodo: coordinate del lotto dal PVP → punto dentro il poligono → codice zona → valori. L'ho fatto per i 6 lotti della sez. 2.3 senza errori. Per il sito si usa il **download ufficiale semestrale** (stessi dati, licenza chiara, nessun carico sul servizio pubblico); GEOPOI resta come riserva per pochi comuni.

Limiti: le quotazioni sono **del semestre precedente** (oggi 2025/2) e sono "indicazioni di valore di larga massima" (lo dice l'Agenzia stessa, citata da [Fiscal Focus](https://www.fiscal-focus.it/news-24/ore-19-00-quotazioni-immobiliari,3,140492)); i valori sono per lo più per m² **lordi**, mentre le perizie usano m² "commerciali" o catastali (simili, non identici).

### 2.3 Cinque esempi reali di "sconto rispetto all'OMI" (dati del 14/10/2026)

Metodo: €/m² del lotto = prezzo ÷ m² scritti nell'annuncio; valore OMI = media tra minimo e massimo della tipologia giusta (civile o economica secondo la categoria catastale), stato "normale", semestre 2025/2.

| # | Lotto PVP | Zona OMI | m² | Prezzo base → €/m² | Offerta minima → €/m² | OMI zona €/m² (media) | Sconto prezzo base | Sconto offerta minima | Stato |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Roma, Via San Godenzo 189A ([4638162](https://pvp.giustizia.it/pvp/it/detail_annuncio.page?idAnnuncio=4638162)), asta 20/01/2027, 1° tentativo | D31 Cassia Due Ponti, civili 2.300-3.400 | 68 | 188.000 € → 2.765 | 141.000 € → 2.074 | 2.850 | **-3 %** | **-27 %** | Libero |
| 2 | Roma, Via Lidia Bianchi 109 ([4638413](https://pvp.giustizia.it/pvp/it/detail_annuncio.page?idAnnuncio=4638413)), asta 10/12/2026, 2° tentativo | E113 Casalotti Selva Candida, economiche 1.700-2.400 | 57 (catastali) | 100.000 € → 1.754 | 75.000 € → 1.316 | 2.050 | **-14 %** | **-36 %** | Libero, ma con difformità da sanare |
| 3 | Milano, Via Padova 256 ([4639587](https://pvp.giustizia.it/pvp/it/detail_annuncio.page?idAnnuncio=4639587)), asta 19/11/2026 | D35 Monza/Crescenzago/Gorla, economiche 2.100-2.800 | 64 | 148.000 € → 2.313 | 148.000 € (come da PVP) | 2.450 | **-6 %** | -6 % (da verificare nell'avviso) | Libero |
| 4 | Milano, Viale Col di Lana 5 ([4633354](https://pvp.giustizia.it/pvp/it/detail_annuncio.page?idAnnuncio=4633354)), asta 18/11/2026 | B20 Porta Vigentina/Porta Romana, civili 5.200-7.200 | 62 | 325.000 € → 5.242 | 325.000 € (come da PVP) | 6.200 | **-15 %** | -15 % (da verificare) | Libero |
| 5 | Torino, Via Tiziano Vecellio 31 ([4627919](https://pvp.giustizia.it/pvp/it/detail_annuncio.page?idAnnuncio=4627919)), asta 15/12/2026 | C2 Dante (San Salvario), economiche 1.400-2.100 | 65 | 96.000 € → 1.476 | 72.000 € → 1.107 | 1.750 | **-16 %** | **-37 %** | Libero |
| esempio di rischio | Roma, Via Monza 9 ([4626051](https://pvp.giustizia.it/pvp/it/detail_annuncio.page?idAnnuncio=4626051)), asta 15/12/2026 | C7 Appio Villa Fiorelli, civili 3.500-5.000 | 75 | 274.000 € → 3.653 | 205.500 € → 2.740 | 4.250 | -14 % | -36 % | **Occupato** con affitto opponibile fino al 14/07/2027 |

Cosa insegnano:
- Lo sconto sul **prezzo base** è piccolo (-3/-16 %): è normale, perché il prezzo base parte già dalla stima del perito ridotta (es. il Tribunale di Savona indica il valore di mercato "al netto della riduzione forfettaria del 15%", [direttiva estimatori](https://tribunale-savona.giustizia.it/cmsresources/cms/documents/Direttiva_per_gli_estimatori_-_2016.pdf)). Lo sconto interessante è quello sull'**offerta minima** (-25 % in più) e quello che cresce a ogni asta deserta.
- Un numero da solo inganna: l'esempio 2 ha abusi da sanare, quello di Via Monza è affittato fino al 2027. La scheda deve mostrare **sempre accanto** stato di occupazione, tentativo e il link all'avviso.

## 3. eBay Browse API + eBay Partner Network (EPN)

- **Accesso**: dalla pagina [Buy APIs Requirements](https://www.edp.ebay.com/api-docs/buy/static/buy-requirements.html) (letta il 14/10): "Many of the Buy APIs are a (Limited Release). The use of eBay's Buy APIs in production is intended for eBay partners only. You must apply for production access through the eBay Partner Network. Acceptance of applications is based on the proposed business model ... There is no guarantee that your application for production use of the APIs will be approved." Servono account eBay, account sviluppatori, iscrizione EPN e il tracciamento affiliato nell'applicazione. Per un nuovo affiliato italiano senza traffico l'approvazione è **incerta**. Nessun costo.
- **Limiti di chiamate**: la pagina [API Call Limits](https://www.edp.ebay.com/develop/api/sell/api_call_limits) dice "Buy APIs require an additional license"; il limite di base delle Browse indicato da fonti secondarie è **5.000 chiamate al giorno**, aumentabile con l'"Application Growth Check" gratuito. Non confermato sulla pagina ufficiale (la riga Browse non è leggibile dal nostro server).
- **Regole di visualizzazione** ([API License Agreement](https://www.edp.ebay.com/join/api-license-agreement), letto il 14/10): "Displayed item listing information may not be more than six (6) hours older than information displayed on the eBay Site" (altrimenti va dichiarato quanto è vecchio); serve il "permesso scritto" di eBay per usare i contenuti in modo da ricavare "any site-wide statistics across eBay Sites" o tassi di conversione; vietato usare i contenuti eBay per addestrare sistemi di intelligenza artificiale; vietato incorniciare pagine eBay. Quindi: una pagina statica pubblicata una volta a settimana **non rispetta** le 6 ore; servirebbe una pagina che chiama l'API a ogni visita (o almeno ogni 6 ore), cioè un server o una funzione, non il nostro modello statico gratuito.
- **Commissioni** ([Rate Card](https://partnernetwork.ebay.it/our-program/rate-card), [PDF globale](https://secureir.ebaystatic.com/cr/v/c1/EPN/Rate%20Card.pdf), letti il 14/10): Business & Industrial 2,5 % (tetto 225 $), Collezionismo 3 %, Elettronica 2 % (Computer 1,5 %), Moda 4 %, Casa e giardino 3 %, Media 3 %, **Ricambi e accessori veicoli 3 %** (tetto 550 $), **"eBay Motors" 4 % con tetto 100 $**, Real Estate 1 % (tetto 100 $), altro 4 %. Tetti in dollari, per transazione.
- **Finestra cookie**: "Makes a purchase within **24 hours** after clicking your affiliate link for a "Buy It Now" item; Places a bid on an auction within 24 hours ... and then wins that auction within 10 days".
- **Veicoli in Italia**: "eBay Motors" è la sezione veicoli degli USA. Su eBay.it le auto sono una parte piccola e spesso si chiudono fuori piattaforma (annuncio e trattativa diretta: nessuna transazione, nessuna commissione); a EICMA 2025 eBay ha detto che "la vendita di auto nuove non è ancora il nostro focus principale" ([auto.it, 8/11/2025](https://www.auto.it/news/attualita/2025/11/08-8502524/ebay_auto_e_ricambi_milano_2025)). Ricambi sì (3 %).
- **Il problema di fondo**: per gli oggetti eBay non esiste un valore ufficiale come l'OMI. Dire "affare" vorrebbe dire calcolare noi un prezzo tipico da altri annunci eBay, cosa che il contratto limita (statistiche ricavate dai contenuti eBay). Resa: un ricambio da 60 € al 3 % = 1,80 € a vendita, solo se si compra entro 24 ore.

**Verdetto eBay: NON PASSA** come parte dell'MVP. Si può riaprire solo se Massimiliano ottiene l'iscrizione EPN e l'accesso Browse in produzione per un altro progetto; in quel caso un riquadro "ricambi e accessori" con link affiliati semplici (senza API) è possibile, ma è una briciola.

## 4. Concorrenza su Google

Limite dichiarato: dal nostro server Google mostra la pagina "traffico insolito", DuckDuckGo risponde 202 vuoto e Bing dà risultati non pertinenti; immobiliare.it, idealista, casa.it, asteannunci e gobid rispondono **403** a uno script. Ho quindi usato la ricerca web (14/10) e i siti raggiungibili; le posizioni esatte su google.it vanno lette con Search Console o a mano da Massimiliano (5 minuti).

| Chi compare per "case all'asta / aste immobiliari / aste giudiziarie [città]" | Cosa mostra | Cosa manca |
|---|---|---|
| **immobiliare.it** (aste), **casa.it** (aste), **idealista** (aste giudiziarie) | elenco con foto, prezzo base, mappa, filtri; per Roma dichiarano 2.992 / 2.890 / 405 annunci | nessun confronto con l'OMI per lotto; numeri gonfiati da aste vecchie o di provincia (da verificare); spiegazioni generiche |
| **asteannunci.it** ("Aste Giudiziarie Tribunale di Roma: 387 annunci"), **astegiudiziarie.it**, **astalegale.net**, **fallcoaste.it / IVG** | siti ufficiali di pubblicità legale: scheda, avviso, perizia, newsletter | pensati per chi già conosce le aste; nessuno sconto sull'OMI; interfaccia da addetti ai lavori |
| **Wikicasa** | ripubblica il PVP per lotto (prezzo base, offerta minima, rilancio, date) | stessa scheda del PVP, nessun valore di zona |
| **asteimmobili.it**, **quimmo.it**, **reteaste.it** (notai) | aste di tribunali e di enti | copertura parziale |
| Testate (idealista news, Il Giorno, InvestireOggi, motor1, alVolante per le auto) | articoli "come funziona", "conviene?", "rischi" | non collegano l'articolo alle aste vere di oggi |

Ricerca mirata del 14/10: **nessun sito trovato che mostri per ogni asta lo sconto rispetto al valore OMI di zona**; le perizie usano l'OMI al loro interno, e gli articoli citano solo medie (es. idealista: "l'89% si chiude sotto il valore di stima con sconto medio del 33,5%", [idealista news](https://www.idealista.it/news/node/431140), dato del Tribunale di Firenze 2016-2020).

Lacune che un sito nuovo può coprire: (1) **sconto €/m² sull'OMI di zona**, sul prezzo base e sull'offerta minima; (2) **solo aste ancora aperte**, aggiornate ogni giorno; (3) **pagine per zona e fascia di prezzo** ("case all'asta Roma Prati", "Milano zona Bocconi", "Roma fino a 50 mila euro", che Google propone già); (4) **spiegazioni semplici** accanto a ogni lotto (libero/occupato, tentativo, cosa vuol dire offerta minima); (5) avvisi email per zona (più semplici della newsletter PVP).

## 5. Domanda: Google Autocomplete (it/it, 14/10/2026)

| Ricerca | Proposte di Google (estratto) |
|---|---|
| aste immobiliari | roma, milano, bologna, brescia, torino, padova, verona, vicenza, trento |
| aste immobiliari roma | centro, nord, tribunale, eur, e provincia, sud, prati |
| aste immobiliari milano | e provincia, centro, "per zona", tribunale, città studi, centro storico, sud, "astageniale" |
| aste immobiliari torino | e provincia, centro, tribunale, crocetta, santa rita |
| case all'asta | **vicino a me**, roma, milano, torino, brescia, catania, bergamo, verona, padova |
| case all'asta roma | **fino a 50 mila euro**, centro, **e provincia 20.000 euro**, nord, san pietro, prati |
| case all'asta milano | centro, e provincia, porta venezia, navigli, porta vittoria, **zona bocconi**, porta romana, **da 20.000 euro** |
| case all'asta torino | e provincia, centro, precollina, zona san paolo, crocetta, zona politecnico, mirafiori sud, santa rita |
| aste giudiziarie roma / milano / torino | immobili, **auto**, centro, beni mobili, e provincia, tribunale, calendario; milano: moto, veicoli, aler; torino: moto, appartamenti |
| auto all'asta | **per privati**, giudiziaria, italia, per privati milano, torino, per privati torino, veneto, padova, milano |
| auto all'asta roma / milano / torino | e provincia, box auto, auto usate, giudiziaria, sequestrate, per privati, tribunale, comune di torino |
| comprare casa all'asta | senza soldi, **rischi**, come funziona, **con mutuo**, conviene, tramite agenzia, con mutuo 100 |
| mutuo per casa all'asta | con abusi edilizi, come funziona, intesa san paolo, chiedere, consap, prima casa, 100 per cento unicredit, con difformità |
| valore omi / quotazioni omi | agenzia delle entrate, immobili, terreni, roma, 2026, geopoi, cosa sono |

Lettura: la domanda per città e **per quartiere/fascia di prezzo** è reale e combacia con le pagine che possiamo generare (zona OMI = quartiere). C'è domanda anche su mutuo e rischi (pagine guida + affiliati). Le auto all'asta sono cercate ("per privati"), ma i veicoli sul PVP sono 1.389 in tutta Italia con prezzo mediano 2.500 € e molti mezzi commerciali: parte secondaria, non trainante.

## 6. Rischi

1. **Privacy dei debitori**: mai salvare né mostrare `soggetti`, nomi nei testi, PDF, foto degli interni (possono ritrarre persone o oggetti personali), dati catastali completi insieme al nome. Filtro automatico sul testo della descrizione: se compare un codice fiscale o "sig./sig.ra" + nome, la descrizione non si mostra. Riferimenti: specifiche PVP 2024 (sez. 1.5) e prescrizione del Garante del 7/2/2008 sulla pubblicità delle vendite giudiziarie, citata nelle specifiche.
2. **Responsabilità per la parola "affare"**: non si scrive mai "affare" o "occasione" come giudizio sul singolo lotto. Si scrive un fatto: "prezzo base 2.765 €/m², media OMI di zona 2.850 €/m² (Agenzia delle Entrate – OMI, 2° semestre 2025): -3 %". Accanto, sempre: stato di occupazione, "i valori OMI sono indicativi, leggi avviso e perizia sul PVP", link alla scheda ufficiale. Il titolo del sito può parlare di "aste sotto la media di zona", non di "affari garantiti". Nessun consiglio d'acquisto personalizzato.
3. **Freschezza**: le aste cambiano (rinvii, sospensioni, esiti). Lettura ogni giorno; la scheda mostra "dati PVP letti il [data]"; le aste passate escono dalle pagine entro 24 ore (o mostrano l'esito, che il PVP fornisce). Con la pubblicazione settimanale attuale (crediti Netlify) le pagine sarebbero vecchie fino a 7 giorni: per questo sito serve un aggiornamento **giornaliero** dei soli dati (file JSON letto dalla pagina) senza rifare il deploy completo, da verificare con il motore esistente.
4. **Occupazione**: metà dei lotti ha "non specificata". Va mostrato com'è, senza indovinare; un filtro "solo liberi" usa solo il dato esplicito.
5. **Qualità dei dati PVP**: date impossibili, offerta minima uguale al base a Milano, coordinate mancanti (~24 % nelle tre città, 58 % a Torino), m² nel testo solo ~40 %. Regole: scartare date oltre 24 mesi; calcolare lo sconto solo se ci sono coordinate e m² certi; altrimenti mostrare solo la fascia OMI di zona.
6. **Tecnico**: indirizzi JSON non documentati che possono cambiare; firewall e reset di connessione. Ritmo lento (3 s), nuovi tentativi, avviso se due giorni di fila senza dati.

## 7. Cosa sarebbe l'MVP (parte a)

1. **Raccolta** (GitHub Actions, ogni giorno, 0 €): aste immobiliari attive di Roma, Milano, Torino (tribunale + comune), poi altre città dall'autocomplete; solo campi strutturati, niente `soggetti`, niente allegati.
2. **OMI**: download ufficiale semestrale (Massimiliano, 10 minuti con SPID, licenza CC BY 4.0) di valori e zone; abbinamento lotto → zona con le coordinate.
3. **Pagine** (statiche, generate dal motore esistente): città; **zona OMI** (= quartiere: "Case all'asta a Roma – Parioli"); **fasce di prezzo** ("fino a 50.000 €", "fino a 100.000 €"); "solo liberi". Ogni lotto: prezzo base, offerta minima, data, libero/occupato, tentativo (se noto), €/m² contro la media OMI di zona, link al PVP.
4. **Guide semplici**: come funziona l'asta, offerta minima e ribassi, libero/occupato, mutuo per l'asta, rischi (abusi, difformità), cos'è l'OMI.
5. **Avvisi email per zona** (modulo già usato negli altri siti): "nuove aste nella tua zona sotto la media OMI".
6. **Auto**: solo una pagina nazionale "auto all'asta oggi" dai 1.389 lotti PVP, senza confronto di valore.
7. Stima lavoro: 2-3 giorni di costruzione, poi automatico. Soglia a 45 giorni come gli altri siti (impression su Search Console per le pagine di zona; iscritti agli avvisi).

## 8. Percorso di ricavo (STIME, non dati misurati)

- **Pubblicità**: RPM su traffico italiano stimato **3-6 €** negli studi precedenti (`12-traffico-a-pagamento.md`, stima interna dello studio 7); per argomenti casa/mutuo può stare nella parte alta, ipotesi **4-8 €** (nessun dato primario trovato: da misurare con AdSense). Con **10.000 visite/mese** a 12 mesi (scenario medio, se le pagine di zona indicizzano) = **40-80 €/mese**; con 30.000 = 120-240 €/mese.
- **Affiliati mutuo**: MutuiSupermarket ha un programma "a lead" sulla rete Awin (stato "aperto su Awin, chiuso su Webgains" secondo [affi.io](https://affi.io/m/mutuisupermarket); compenso **non pubblico**, vietato il PPC). MutuiOnline e Facile.it: nessun programma affiliati pubblico trovato. Da verificare con l'iscrizione Awin di Massimiliano (gratuita). Stima prudente: 0,2-0,5 % dei visitatori chiede un preventivo → 20-50 richieste/mese su 10.000 visite; il valore per richiesta va letto su Awin prima di qualsiasi conto.
- **Fase 2 (dopo il cancello fiscale)**: contatto con professionisti che assistono nelle aste o con mediatori del credito (quota per contatto, con consenso separato). Non prima della risposta fiscale.
- **eBay**: escluso (sez. 3).
- Ordine di grandezza onesto: **0-1.000 €/anno nel primo anno**, più probabile nella parte bassa, simile agli altri siti della rete. Vale la pena solo perché costa poco e riusa il motore.

## 9. Fonti e prove (lette il 14/10/2026)

- PVP: [home](https://pvp.giustizia.it/pvp/), [guida](https://pvp.giustizia.it/pvp/it/guida.page), [informativa](https://pvp.giustizia.it/pvp/it/consent_cookie.page), [specifiche tecniche 2024](https://pst.giustizia.it/PST/resources/cms/documents/PVP_ST_Allegato_A_V1.2_18092024.pdf), [provvedimento di adozione 2024](https://pst.giustizia.it/PST/resources/cms/documents/m_dg.DOG07.25092024.0004943.ID_20240920_Provvedimento_adozione_ST_si.pdf); interfaccia JSON descritta nella sez. 1.1.
- OMI: [Forniture dati OMI](https://www.agenziaentrate.gov.it/portale/schede/fabbricatiterreni/omi/forniture-dati-omi) (CC BY 4.0), [GEOPOI](https://www1.agenziaentrate.gov.it/servizi/geopoi_omi/index.htm).
- eBay: [Buy APIs Requirements](https://www.edp.ebay.com/api-docs/buy/static/buy-requirements.html), [API License Agreement](https://www.edp.ebay.com/join/api-license-agreement), [API Call Limits](https://www.edp.ebay.com/develop/api/sell/api_call_limits), [EPN Rate Card](https://partnernetwork.ebay.it/our-program/rate-card) e [PDF](https://secureir.ebaystatic.com/cr/v/c1/EPN/Rate%20Card.pdf).
- Concorrenza e domanda: ricerca web e autocomplete `suggestqueries.google.com` (hl=it, gl=it) del 14/10/2026; pagine citate nella sez. 4.
- Gli script del test e i file scaricati sono rimasti nella cartella temporanea della sessione (non nel repository): contenevano anche i campi `soggetti` del PVP, che non vanno conservati.
