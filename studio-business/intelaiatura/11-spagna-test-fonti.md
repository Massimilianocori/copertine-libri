# Spagna: test delle fonti per "Europe strikes today"

Data del test: **10 ottobre 2026**. Tutti i download sono stati fatti dal server della sessione e si trovano in `spagna/dl/`. Sono stati letti solo con `python3 -I`, `pdftotext` e `pdfinfo`, senza eseguire nulla. Gli script sono in `spagna/script/`. Le tabelle calcolate sono in `spagna/tabella.json` (188 resoluciones) e in `spagna/anticipo.txt` (ultimi 12 mesi).

**Criterio (non modificato).** Il test PASSA se c'è almeno una fonte ufficiale, gratuita e leggibile in automatico senza login, che pubblichi gli scioperi dei trasporti (treni, aerei/aeroporti, trasporto urbano di Madrid e Barcellona) **almeno 5 giorni prima**, con date, settore e ambito geografico. In alternativa bastano **al massimo 3 fonti ufficiali** che insieme coprano treni, voli e Madrid/Barcellona con lo stesso anticipo.

---

## 0. In breve

- **Legge (verificata sul BOE).** L'art. 4 del Real Decreto-ley 17/1977 dice: *"Cuando la huelga afecte a empresas encargadas de cualquier clase de servicios públicos, el preaviso del comienzo de huelga al empresario y a la autoridad laboral habrá de ser, al menos, de diez días naturales."* (https://www.boe.es/buscar/act.php?id=BOE-A-1977-6061, HTTP 200). Il preavviso va però **all'azienda e all'autorità del lavoro**. Non va in un registro pubblico: lo stesso succede in Francia. L'art. 10 dà all'"Autoridad gubernativa" il potere di fissare i servizi minimi.
- **Un registro pubblico degli scioperi proclamati, come quello del MIT, non esiste.** Non l'ho trovato né a livello statale né nelle comunità autonome. La pagina della Junta de Extremadura sulla "Comunicación de huelga" conferma che il preavviso serve solo perché l'autorità del lavoro "tenga conocimiento".
- **La fonte ufficiale migliore è il Ministerio de Transportes**, con **due pagine HTML** che elencano le *resoluciones de servicios mínimos*: una per gli aerei e gli aeroporti, una per i treni. Sono complete, gratuite, senza login e riutilizzabili. Il problema è che **la resolución esce quasi sempre 1-4 giorni prima dello sciopero**. Negli ultimi 12 mesi, su 64 resoluciones per scioperi nuovi, **solo 8 (12 %) sono uscite con almeno 5 giorni di anticipo**. L'anticipo mediano è di **2-3 giorni**.
- **Il ministero conosce lo sciopero molto prima.** Esempi presi dalle resoluciones stesse: per Renfe il 15/7/2026 la convocatoria è arrivata il 18/6 (27 giorni prima), ma la resolución è stata pubblicata il 9/7. Per Groundforce il 27/3/2026 la convocatoria è del 16/3, la resolución del 26/3. Fino alla resolución, però, non pubblica niente.
- **Il BOE non pubblica queste resoluciones.** Ho letto con l'API i 324 sommari dal 1/10/2025 al 10/10/2026 e non c'è **nessuna** resolución di servizi minimi per i trasporti: ci sono solo ordini per l'energia e gli idrocarburi (TED) e per la vigilanza privata.
- **Madrid (Metro, EMT) e Barcellona (TMB).** I servizi minimi li fissano la Comunidad de Madrid e la Generalitat (Departament d'Empresa i Treball), con comunicati **1 giorno prima**. Non ho trovato un elenco ufficiale leggibile in automatico. Il sito di Metro de Madrid blocca il server ("Acceso no disponible"). TMB ha un RSS ufficiale, ma la notizia dello sciopero del bus dell'8/10/2026 è uscita il 7/10 alle 15:00.

**Verdetto: NON PASSA** (sezione 2).

---

## 1. Tabella delle fonti

"Auto": **sì** = leggibile in automatico dal server oggi; **parziale** = leggibile ma con limiti seri; **no** = non leggibile o inutile.

| # | Fonte (chi la pubblica) | URL esatto provato | HTTP dal server | Formato | Login / token | Licenza | Frequenza | Anticipo sullo sciopero | Auto |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Ministerio de Transportes (MITRAMS)**: servicios mínimos **aéreos** (aeroporti, handling, controllori, pulizie, equipaggi) | `https://www.transportes.gob.es/aviacion-civil/informacion-util-al-pasajero/huelga-servicios-minimos` | **200** (149 KB) | HTML (fisarmonica per anno 2022-2026) + un PDF per resolución su `cdn.transportes.gob.es` | nessuno | riuso libero, anche commerciale, citando la fonte e la data dell'ultimo aggiornamento (aviso legal del ministero, letto oggi) | a evento: 40 resoluciones nel 2026 (circa 4-8 al mese) | **mediana 2 giorni**; ≥5 giorni in 7 casi su 38 (scioperi nuovi, ultimi 12 mesi); massimo 7 | **parziale**: niente RSS, niente data di pubblicazione sulla pagina (si ricava dal `Last-Modified` del PDF o dalla prima volta che lo vediamo), testo libero in spagnolo |
| 2 | **MITRAMS**: servicios mínimos **ferroviarios** (Renfe con Cercanías/Rodalies, Ouigo, Iryo, Adif, LogiRAIL, merci) | `https://www.transportes.gob.es/transporte-terrestre/resoluciones-de-servicios-minimos-ferroviarios` | **200** (89 KB) | HTML (anni 2025-2026) + PDF | nessuno | come sopra | a evento: 17 voci nel 2026, ma per **un solo sciopero** (9-11/2/2026) ci sono 13 resoluciones | **mediana 3 giorni**; ≥5 giorni in 1 caso su 26; massimo 6 (marzo 2025: 10 giorni, fuori dalla finestra) | **parziale** (come sopra) |
| 3 | PDF delle resoluciones (CDN del ministero) | es. `https://cdn.transportes.gob.es/portal-web-transportes/aereo/huelga-servicios-minimos/49_26-10-01----resolucion-ssmm-huelga-groundforce-bcn_vi.pdf` | **187 su 188 → 200** (1 vecchio PDF del 2023 → 404) | PDF di testo (estraibile con pdftotext), 10-20 pagine, con data e ora della firma ("FIRMADO … A fecha: 28/09/2026 06:05 PM") | nessuno | come sopra | – | come sopra | sì (per i dettagli) |
| 4 | **BOE**: API open data, sommario giornaliero | `https://www.boe.es/datosabiertos/api/boe/sumario/AAAAMMGG` (header `Accept: application/xml`) | **200** in 324 giorni; **404** nei 51 giorni senza BOE (domeniche) | XML | nessuno | licenza BOE non riletta oggi (l'aviso legal del BOE dovrebbe consentire il riuso: **da verificare**) | quotidiana | **non pubblica i servizi minimi dei trasporti**: 0 risultati in 12 mesi | sì, ma **inutile** |
| 5 | BOE: testo consolidato del RDL 17/1977 | `https://www.boe.es/buscar/act.php?id=BOE-A-1977-6061` | 200 | HTML | nessuno | – | – | (solo per verificare la regola dei 10 giorni) | – |
| 6 | **Renfe**: GTFS-RT "Incidencias y avisos" (solo Cercanías/Rodalies) | `https://gtfsrt.renfe.com/alerts.json` (e `.pb`); scheda `https://data.renfe.com/api/3/action/package_show?id=incidencias-avisos` | **200** / 200 | JSON / Protobuf GTFS-RT | nessuno | **CC BY 4.0** (scheda data.renfe.com) | ogni 20 secondi | tempo reale; oggi 69 avvisi, campo `cause` **sempre vuoto**, nessuno sciopero in corso: **anticipo non verificabile oggi** | sì (ma solo Cercanías, all'ultimo momento) |
| 7 | Renfe: pagine web (avvisi, scioperi) | `https://www.renfe.com/es/es/viajar/informacion-util/avisos`, `.../huelgas`, `.../grupo-renfe/sala-de-prensa`, `.../comunicacion/renfe-al-dia/avisos` | 404 / 404 / 404 / 302; home 200 | HTML | – | – | – | nessuna pagina "huelga" trovata | no |
| 8 | Adif | `https://www.adif.es/` (200); `https://www.adif.es/sobre-adif/sala-de-prensa` (404) | 200 / 404 | HTML | – | – | – | nessun elenco di scioperi trovato | no |
| 9 | Aena | `https://www.aena.es/es/pasajeros/pasajeros.html` (200); `https://www.aena.es/es/prensa.html` e `/es/prensa/notas-de-prensa.html` (404) | 200 / 404 | HTML | – | – | – | nessun elenco di scioperi trovato | no |
| 10 | ENAIRE (controllo aereo) | `https://www.enaire.es/` | **403** | – | – | – | – | – (gli scioperi dei controllori finiscono comunque nella fonte 1, es. SAERCO) | no |
| 11 | Metro de Madrid | `https://www.metromadrid.es/es` , `/es/viaja-en-metro/avisos` | 200, ma pagina **"Acceso no disponible"** (blocco anti-robot) | – | – | – | – | – | no |
| 12 | EMT Madrid: RSS notizie | `https://feeds.feedburner.com/emtmadrid` | **200** (350 KB) | RSS | nessuno | non indicata | più volte al giorno | oggi solo lavori ed eventi, nessuno sciopero: **anticipo non verificato** | parziale |
| 13 | Consorcio Regional de Transportes de Madrid (CRTM): avvisi | `https://www.crtm.es/comunicacion/actualidad-del-servicio/avisos/` (200); `/feed/` (404) | 200 / 404 | HTML | – | – | **fermo**: la notizia più recente è del 01/12/2025 | – | no |
| 14 | Comunidad de Madrid: BOCM (sommari XML) | `https://www.bocm.es/boletin/CM_Boletin_BOCM/2026/10/10/BOCM-20261010242.xml` | 200 | XML | nessuno | – | quotidiana | nessuna orden di servizi minimi per Metro/EMT trovata nel BOCM (solo scuola e sanità). Per il 15/10/2025 i minimi sono usciti con un comunicato del **14/10/2025** (eldiario.es) | no (per i trasporti) |
| 15 | **TMB** (metro e bus di Barcellona): RSS sala stampa | `https://noticies.tmb.cat/rss` | **200** | RSS (in catalano) | nessuno | non indicata | più volte a settimana | sciopero bus dell'8/10/2026: notizia del **07/10/2026 alle 15:00** (1 giorno prima), solo per quel giorno | parziale |
| 16 | Generalitat de Catalunya: RSS delle note stampa (il Departament de Treball annuncia lì i servizi minimi) | `https://govern.cat/salapremsa/api/v1/rss/search?objectType=1` | **200** | RSS | nessuno | – | decine di note al giorno; il feed ha solo le ultime 20 e il filtro per testo viene ignorato | non misurato (dalla stampa: 1-2 giorni) | parziale |
| 17 | DOGC (Diari Oficial de la Generalitat) | `https://dogc.gencat.cat/ca/` | 200 | HTML | – | – | quotidiana | nessuna API trovata; nessuna resolució di servizi minimi per i trasporti 2026 trovata | no |
| 18 | Rodalies de Catalunya | `https://rodalies.gencat.cat/ca/inici/` (200); `/ca/atencio_al_client/avisos/` (404) | 200 / 404 | HTML | – | – | – | – (gli scioperi Renfe/Rodalies sono comunque nella fonte 2) | no |
| 19 | Ouigo / Iryo | `https://www.ouigo.com/es/` / `https://iryo.eu/es/home` | 200 / **403** | HTML | – | – | – | – | no |
| 20 | Ministero: RSS | `https://www.transportes.gob.es/rss` | 404 | – | – | – | – | – | no |

Note:
- **Data di pubblicazione.** Le pagine del ministero non mostrano la data di pubblicazione. Ho usato il `Last-Modified` del PDF sul CDN, che quasi sempre coincide con il giorno della firma o con quello dopo. Un nostro lettore automatico userebbe "la prima volta che compare", che è lo stesso giorno o più tardi.
- **Proroghe.** Molte voci degli aerei rinnovano scioperi **indefiniti già in corso** (SAERCO, Groundforce BCN, Outsmart SATE Madrid: "efectos del 1 de octubre hasta el 30 de noviembre de 2026"). Per queste l'anticipo conta poco, perché lo sciopero è già nell'elenco. Le ho escluse dal calcolo dell'anticipo (marcate "P" in `anticipo.txt`).
- **Lingua.** Tutto è solo in **spagnolo**. TMB e la Generalitat scrivono in **catalano**. Nessuna fonte ufficiale ha l'inglese. Servono regole fisse di traduzione come per l'italiano, su testi più lunghi e meno regolari di quelli del registro MIT. Le voci della fonte 1 sono frasi libere, per esempio "los lunes, jueves, viernes, sábados y domingos, con paros parciales de 5:00h. a 7:00h…".

---

## 1b. Esempi reali con le date

| Sciopero | Quando il ministero l'ha saputo (scritto nella resolución) | Firma della resolución | PDF pubblicato | Inizio | Anticipo pubblico |
|---|---|---|---|---|---|
| Renfe, SF-Intersindical, tutto il gruppo, tutta la Spagna | convocatoria "recibida" il 18/06/2026 | 09/07/2026 | 09/07/2026 | 15/07/2026 | **6 giorni** (il ministero lo sapeva da 27) |
| Renfe Viajeros, SF-I, macchinisti e capitreno | convocatoria ricevuta il 20/07/2026 | 28/07/2026 | 29/07/2026 | 31/07/2026 | **2 giorni** |
| Grupo Renfe + Adif + Ouigo + Iryo + altri (sciopero ferroviario nazionale) | (convocatorie del comité general e di SEMAF, CCOO, UGT, CGT, SF-I, ALFERRO) | 04-06/02/2026 | 06/02/2026 | 09/02/2026 | **3 giorni** |
| Groundforce (handling), 13 aeroporti tra cui Madrid e Barcellona | convocato con scritto del 16/03/2026 | 26/03/2026 | 26/03/2026 | 27/03/2026 | **1 giorno** |
| Menzies (handling), 13 aeroporti | convocato con scritto del 17/03/2026 | 26/03/2026 | 26/03/2026 | 28/03/2026 | **2 giorni** |
| SAERCO (controllori), 9 aeroporti | richiesta dei minimi dell'azienda: 14/04/2026 | 15/04/2026 | 15/04/2026 | 17/04/2026 | **2 giorni** |
| Groundforce BCN (CGT), Barcellona-El Prat | convocato con scritto alla Generalitat del 17/07/2026 | 29/07/2026 | 29/07/2026 | 04/08/2026 | **6 giorni** |
| Bus TMB Barcellona (stop parziali) | – | Generalitat (data non trovata) | RSS TMB 07/10/2026 15:00 | 08/10/2026 | **1 giorno** |

**Scioperi annunciati dalla stampa per le prossime settimane, confrontati con le fonti ufficiali (oggi, 10/10/2026):**
- **Ouigo, SEMAF (macchinisti).** Stop di 24 ore il 30/10 e il 2/11; parziali (6-12 e 18-23:59) il 6/11 e il 9/11, il 4/12 e l'8/12. Fonte: COPE, articolo del 08/10/2026. **Non compare in nessuna fonte ufficiale**: la pagina dei treni del ministero ha come ultima voce lo sciopero Renfe del 31/07/2026. In base alla storia, la resolución arriverà verso il 27-28/10.
- **Bus TMB Barcellona.** Stop parziali l'8, 14, 15, 20, 22, 27 e 29/10 (catalunyapress.cat, 08/10/2026). In fonte ufficiale leggibile c'è **solo il giorno 8**, sul RSS TMB del 7/10.
- **Aeroporti, scioperi già in corso fino al 30/11/2026.** SAERCO (Jerez, A Coruña, Madrid-Cuatro Vientos, Sevilla, Vigo, El Hierro, Fuerteventura, Lanzarote, La Palma), Groundforce BCN (El Prat) e Outsmart, nastri bagagli di Madrid-Barajas. **Sono presenti** sulla pagina degli aerei del ministero (resoluciones firmate il 28/09/2026).

**Volume (1/10/2025 – 10/10/2026), pagine del ministero:** **78 resoluciones**, di cui **50 per aerei e aeroporti** e **28 per i treni**. Per mese: ott-25 11, nov-25 5, dic-25 5, gen-26 2, feb-26 15, mar-26 7, apr-26 2, mag-26 7, giu-26 9, lug-26 8, ago-26 3, set-26 4.
- Gli **scioperi distinti** sono meno: per i treni circa 10 eventi (un solo sciopero, quello del 9-11/2/2026, ha 13 resoluciones).
- Molte voci degli aerei riguardano lavoratori con poco impatto sul viaggiatore: pulizie a Bilbao, metalmeccanici di A Coruña, passerelle.

Distribuzione dell'anticipo (64 resoluciones per scioperi nuovi; giorni tra la pubblicazione del PDF e l'inizio):

| Anticipo | Resoluciones |
|---|---|
| pubblicato dopo l'inizio | 3 |
| 0 giorni | 5 |
| 1 giorno | 14 |
| 2 giorni | 8 |
| 3 giorni | 20 |
| 4 giorni | 6 |
| 5 giorni | 2 |
| 6 giorni | 5 |
| 7 giorni | 1 |

---

## 2. Verdetto: **NON PASSA**

Applico il criterio così com'è scritto.

- **Fonte ufficiale unica con ≥5 giorni: no.** Le pagine del ministero sono ufficiali, gratuite, senza login e coprono treni e aerei con date, settore e ambito. Però l'anticipo reale è di 2-3 giorni (mediana) e **solo il 12 % degli scioperi compare con 5 giorni o più**. Inoltre le due pagine **non coprono Metro, EMT e TMB**, che spettano alle comunità autonome.
- **Fino a 3 fonti che insieme coprano tutto con ≥5 giorni: no.** Per Madrid e Barcellona l'unica traccia ufficiale leggibile è il giorno prima (RSS TMB, comunicati della Comunidad e della Generalitat). Metro de Madrid blocca il server. Il BOE e il BOCM non pubblicano questi atti, il DOGC non ha un'API.
- **Il registro con preavviso di 10 giorni non è pubblico.** L'art. 4 del RDL 17/1977 c'è, ma il preavviso resta tra sindacato, azienda e autorità del lavoro: è lo stesso schema della Francia.

---

## 3. (Non si applica: il test non passa)

---

## 4. Cosa manca e la via parziale migliore

**Cosa manca**
1. Un elenco pubblico degli scioperi **proclamati**, pubblicato al momento della convocatoria (10 giorni prima). In Spagna la data in cui il ministero riceve la convocatoria si legge solo **dopo**, dentro la resolución.
2. Una fonte ufficiale leggibile in automatico per **Metro de Madrid, EMT e TMB** con più di 1 giorno di anticipo.
3. Testi ufficiali in inglese: non ce ne sono.

**Via parziale migliore** (se si decide di andare avanti lo stesso, fuori dal criterio)
- **Fonte di base: le 2 pagine del ministero** (aerei + treni), lette 2 volte al giorno come in Italia. Danno uno sciopero "confermato ufficialmente" con 1-4 giorni di anticipo, nomi delle aziende, aeroporti coinvolti, date e fasce orarie, percentuali dei servizi minimi (nel PDF). Coprono anche gli scioperi indefiniti in corso con il loro periodo di validità. Questo **basta per le pagine "today" e "tomorrow"** ("spain strike today", "spain airport strike today"), ma **non** per "this week" o "next week", né per il calendario a 30 giorni come in Italia.
- **Aggiunte per Madrid e Barcellona** (solo come "annuncio del giorno prima"): RSS TMB e RSS EMT. Il Metro de Madrid manca.
- **Cosa non si può fare senza cambiare modello:** coprire gli annunci con 2-4 settimane di anticipo (es. Ouigo, già noto il 8/10 per il 30/10). Servirebbe la stampa o i sindacati, quindi fonti non ufficiali e lettura manuale. Il modello "una fonte ufficiale unica" non regge.
- **Stima del lavoro per questa via parziale (indicativa):** circa **25-35 ore**.

| Lavoro | Ore |
|---|---|
| Lettore delle 2 pagine con gestione di proroghe, modifiche e voci duplicate | 6-8 |
| Estrazione dai PDF (date, fasce, aeroporti, percentuali) | 6-8 |
| Regole fisse di traduzione spagnolo → inglese per frasi libere | 8-12 |
| Mappa aziende → aeroporti / città | 3-4 |
| Pagine | 4-6 |

- **Rischi:**
  - nessuna data di pubblicazione e nessun RSS: dipendiamo dalla struttura HTML (fisarmonica per anno) e dai nomi dei file, che non sono regolari;
  - testi lunghi e liberi: traduzione automatica a regole fragile;
  - molte resoluciones minori da filtrare;
  - le resoluciones arrivano spesso il venerdì per il lunedì: con 2 letture al giorno va bene, con la routine settimanale di riserva no;
  - il server del ministero (CloudFront) oggi risponde 200, ma da GitHub Actions non è provato;
  - un sito "Spain strikes" con avvisi solo 2-3 giorni prima perde il vantaggio principale del sito italiano (il calendario a 30 giorni).

**Fonti di stampa usate solo per il confronto (non ufficiali):**
- COPE, 08/10/2026 (Ouigo): https://www.cope.es/programas/la-linterna/clases-de-economia/audios/nueva-huelga-transporte-ferroviario-anuncian-paros-24-horas-maquinistas-ouigo-puente-todos-santos-paros-parciales-6-9-noviembre-puente-constitucion-20261008_3452913.html
- Catalunyapress, 08/10/2026 (bus TMB): https://www.catalunyapress.cat/article/societat/2026-10-08/6044287-arrenca-vaga-dautobusos-barcelona-dates-horaris-dels-aturs-i-serveis-minims-previstos
- eldiario.es, 14/10/2025 (minimi di Madrid per il 15/10/2025): https://www.eldiario.es/madrid/somos/servicios-minimos-metro-madrid-emt-huelgas-gaza-15-mitad-trenes-horas-valle_1_12683220.html
- Junta de Extremadura, "Comunicación de huelga": https://www.juntaex.es/w/2799
