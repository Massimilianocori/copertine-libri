# Fronte nuovo, settore LAVORO E PAGHE in altri mercati e lingue (12/11/2026)

Settore dichiarato: lavoro e buste paga (lontano dalle zone già battute). Domanda di partenza: il bisogno che oggi serviamo in Italia con i minimi per contratto e livello esiste uguale in Messico, Spagna, Colombia, Argentina, Cile, Perù, Brasile e Filippine? Si può servire da fonti ufficiali, e qualcuno paga?

## Verdetto in tre righe

**Nessuna idea passa l'asticella dei siti nuovi (voto ≥ 7 e ≥ 5.000 €/anno centrali). Nessuna passa nemmeno le 4 prove.** La domanda c'è ovunque ed è enorme (10 suggerimenti su 10 quasi a ogni ricerca), ma in ogni mercato o il vuoto è già chiuso da siti dedicati e aggiornati, o la fonte ufficiale non si legge, e in tutti il pagatore è solo la pubblicità di Paesi dove rende poco. Voto più alto: 4,5.

Il risultato utile è un altro: **la Spagna dimostra che il modello "tabelle per contratto" regge un sito intero** (due concorrenti con 1.883 e 1.205 contratti, aggiornati al bollettino di settembre 2026). È una conferma per il sito italiano di oggi, non un mercato nuovo da aprire.

## Come è stata fatta la ricerca

- Domanda: completamento automatico di Google nel Paese e nella lingua giusti (`gl=mx, es, co, ar, cl, pe, br, ph`), circa 95 ricerche.
- Fonti ufficiali: provate con curl, rispettando robots.txt.
- Concorrenti: letti con curl sulle pagine vere; le classifiche vengono dallo strumento di ricerca web (i motori letti direttamente hanno risposto con blocchi anti-automa, **non aggirati**; per questo le posizioni esatte su Google non sono misurate).
- Limite dichiarato: nessuna cifra di volume mensile, solo numero di suggerimenti e loro forma.

## 1. La domanda, mercato per mercato (letta oggi)

| Mercato | Ricerca | Suggerimenti | Che cosa chiedono |
|---|---|---|---|
| Spagna | "tablas salariales convenio " | 10 | tutte settore × provincia × 2026: metal Madrid, metal Valencia, metal Pontevedra, limpieza Madrid, campo Sevilla, artes gráficas |
| Spagna | "tabla salarial convenio hosteleria " | 10 | 10 province diverse (Baleares, Cantabria, Alicante, Málaga, Bizkaia…) |
| Spagna | "convenio metal ", "convenio limpieza ", "convenio comercio ", "convenio construccion ", "convenio oficinas y despachos ", "convenio transporte mercancias " | 10 ciascuna | sempre provincia + anno; anche "pdf" e "boe" |
| Spagna | "salario convenio ", "categorias profesionales convenio " | 10, 10 | per settore e per mestiere ("conductor repartidor", "auxiliar administrativo") |
| Spagna | "calcular finiquito", "calcular indemnizacion despido", "smi 2027" | 10, 10, 10 | per tipo di cessazione; SMI 2027 "previsión", "12 pagas" |
| Messico | "aguinaldo ", "calculadora aguinaldo" | 10, 10 | 2026, proporcional, neto, ISR, pensionados IMSS/ISSSTE |
| Messico | "calcular finiquito", "finiquito " | 10, 10 | por renuncia, por despido, per Stato (Jalisco, CDMX) |
| Messico | "salario minimo 2027" | 10 | zona fronteriza e per Stato (Veracruz, Puebla, Tijuana): ma le zone sono solo due |
| Messico | "salario minimo profesional ", "salario minimo albañil" | 10, 10 | per mestiere: contador, auxiliar contable, chofer, albañil |
| Messico | "reparto de utilidades ", "vacaciones dignas tabla" | 10, 4 | date e calcolo; la tabella delle ferie ha poca domanda |
| Colombia | "prima de servicios ", "calcular liquidacion", "salario minimo 2027" | 10, 10, 10 | formula, 2026, "ministerio del trabajo" (la calcolatrice ufficiale è già nel suggerimento) |
| Colombia | "cesantias " | 10 | solo navigazione verso i fondi (Porvenir, Protección): non è domanda nostra |
| Argentina | "escala salarial ", "escala salarial comercio " | 10, 10 | una scala al mese (julio, agosto, septiembre, octubre 2026); nei suggerimenti ci sono già i nomi di due siti concorrenti |
| Argentina | "aguinaldo ", "calcular aguinaldo" | 10, 10 | jubilados, proporcional |
| Cile | "calcular finiquito", "gratificacion legal", "sueldo minimo 2027" | 10, 10, 10 | nei suggerimenti: "dt" (Dirección del Trabajo), "buk", "talana": ufficio pubblico e due software paghe |
| Perù | "calcular cts", "gratificacion ", "calcular liquidacion" | 10, 10, 10 | "sunafil" nel suggerimento; CTS di maggio e novembre |
| Brasile | "piso salarial ", "piso salarial 2026 ", "piso salarial vigilante ", "piso salarial pedreiro ", "piso salarial porteiro ", "piso salarial auxiliar administrativo " | 10 ciascuna | mestiere × Stato × anno (vigilante SP, RJ, MG, PR, SC, DF) |
| Brasile | "convenção coletiva ", "convenção coletiva vigilantes ", "salário mínimo regional " | 10, 10, 10 | per categoria e Stato, con "pdf" |
| Brasile | "calcular rescisão", "calculadora décimo terceiro" | 10, 10 | nei suggerimenti: "serasa", "g1" |
| Filippine | "minimum wage ", "minimum wage region ", "minimum wage cavite", "minimum wage laguna", "minimum wage cebu" | 10 ciascuna | regione, provincia e **singola città** (General Trias, Dasmariñas, Imus, Calamba, Cabuyao, San Pedro), "per hour", "monthly" |
| Filippine | "kasambahay minimum wage " | 10 | lavoro domestico per provincia |
| Filippine | "13th month pay ", "13th month pay computation" | 10, 10 | per 3, 4, 5, 6 mesi, paga giornaliera, con assenze |
| Filippine | "wage order ", "overtime pay computation", "night differential computation", "separation pay computation" | 10 ciascuna | numero dell'ordinanza con "pdf"; calcoli "dole" |

**Prova della domanda: SÌ in tutti i mercati.** La forma più simile al sito italiano (tabella × luogo × anno) è in Spagna, Brasile e Filippine.

## 2. Le fonti ufficiali (provate con curl)

| Fonte | Esito | Nota |
|---|---|---|
| BOE, sommario giornaliero `boe.es/datosabiertos/api/boe/sumario/AAAAMMGG` | 200, JSON | Letti 14 giorni. **Il BOE pubblica solo i contratti statali e d'azienda**: in 14 giorni 4 testi (Unidad Editorial ×2, Airbus, LogiRAIL). I contratti provinciali, cioè quasi tutta la domanda ("metal Madrid", "hostelería Málaga"), stanno in circa 50 bollettini provinciali e regionali diversi (BOCM, BOP di ogni provincia…), ognuno con formato suo |
| REGCON, registro dei contratti (`expinterweb.mites.gob.es/regcon/`) | 200 | Maschera di ricerca; nessun robots.txt (404). Non provato lo scarico in blocco |
| NWPC Filippine (`nwpc.dole.gov.ph`) | 200, robots permette | 17 ordinanze salariali in PDF dalla pagina iniziale, più una pagina per regione con le cifre. Ordinanza CALABARZON n. 23: 7 pagine **con testo**, cifre per città (es. Cavite City, Carmona, General Trias, Tagaytay, Trece Martires: 600 + 45 = 645 pesos al giorno, non agricolo). Ordinanza NCR n. 28: **scansione** (223 caratteri in 3 pagine), serve lettura ottica |
| DOLE Filippine (`dole.gov.ph`) | 403 al robots.txt | non insistito |
| CONASAMI Messico (`gob.mx/conasami`, tabella dei salari minimi generali e professionali) | 200 | 61 mestieri × 2 zone |
| Ley Federal del Trabajo (`diputados.gob.mx/LeyesBiblio/pdf/LFT.pdf`) | 200, 4,2 MB | testo vigente |
| DOF Messico (`dof.gob.mx`) | nessuna risposta | non insistito |
| Brasile, Mediador del Ministero del Lavoro (`www3.mte.gov.br/sistemas/mediador/`) | **403** | è l'archivio di tutte le convenzioni collettive: senza questo la prova dei dati in Brasile non c'è. Non aggirato |
| Colombia `mintrabajo.gov.co`, Perù `sunafil.gob.pe` | nessuna risposta (connessione chiusa) | non insistito |
| Argentina `argentina.gob.ar`, Cile `dt.gob.cl` | 200 al robots.txt | non approfonditi: scartati prima per pagatore e concorrenti |

Licenze: le condizioni di riuso del BOE e la regola filippina sulle opere del governo (uso a fini di lucro) **non sono state lette in questa sessione**: da leggere prima di qualsiasi costruzione. Non servono oggi perché nessuna idea arriva alla costruzione.

## 3. I concorrenti, letti

### Spagna: contratti collettivi (5 esempi: metal Madrid, hostelería Málaga, limpieza Zaragoza, metal Pontevedra, transporte Bizkaia; in più campo e oficinas y despachos)

| Concorrente | Che cosa ha | Che cosa manca |
|---|---|---|
| **convenioscolectivos.org** | 1.883 pagine di contratto nella mappa del sito. Metal Madrid: codice REGCON, vigenza, fonte con numero e data del bollettino (BOCM n. 59 dell'11/3/2026), scarico gratuito in Excel, XML per le paghe, JSON, avviso "se cambia". Hostelería Málaga: 64 importi in pagina, fonte BOPMA n. 70 del 14/4/2026. Limpieza Zaragoza: 366 importi, fonte BOP n. 216 del **19/9/2026**. Trovati anche metal Pontevedra, transporte Bizkaia (3 pagine), 17 contratti agricoli, 9 di oficinas y despachos. Nessuna pubblicità: vive di area professionale e API | Niente di rilevante sui 5 esempi. "Campo Sevilla" non trovato per nome |
| **convenioslaborales.com** | 2.350 pagine di tabelle per 1.205 contratti, una per anno. Metal Madrid 2026: scelta della categoria, "da 20.687 a 35.379 € lordi l'anno", aumento +2,0 %, costo per l'azienda, calcolo arretrati, link alla tabella ufficiale, aggiornata il 13/10/2026. 105 pagine sul lavoro agricolo | "Oficinas y despachos" non trovato nella mappa |
| **calculaminomina.com** | 36 contratti, più calcolatrici (netto, finiquito, indennità, disoccupazione), pubblicità presente | copertura piccola |
| Altri in classifica sullo stesso esempio | PDF dei sindacati (CCOO), associazione datoriale (AECIM), entiendetunomina.com, cvcompass.es | — |

**Vuoto dimostrato: NO.** Due siti dedicati coprono 5 esempi su 5 con le cifre vere, la fonte e la data, e uno regala anche i file. Arrivare terzi con 50 bollettini diversi da leggere non ha senso.

### Filippine: salario minimo per luogo (5 esempi: General Trias in Cavite, Bulacan al mese, lavoro domestico a Davao, Cebu, tredicesima a paga giornaliera)

| Concorrente | Che cosa ha | Che cosa manca |
|---|---|---|
| **sweldoph.com** | 236 pagine: 111 guide, 56 calcolatrici, 51 notizie; pubblicità presente. Pagina Cavite: **tabella di ogni località** con classe e importo (General Trias 645, Imus 645, Kawit 590…), ordinanza n. 23 citata, aggiornata il **26/10/2026**, cioè il giorno dell'entrata in vigore. Calcolatrice con scelta regione → provincia → città. Pagine per 17 regioni e 5 province (Batangas, Cavite, Laguna, Quezon, Rizal). Calcolatrici di tredicesima e paga proporzionale | Pagine di provincia fuori da CALABARZON (Bulacan, Pampanga, Cebu non hanno pagina propria); la paga oraria sulla pagina di Cavite non compare |
| **wageindicator.org** | pagina per regione con i settori (Bulacan: 600 non agricolo, 590 commercio, 570 agricolo), anche in filippino | nessuna riga per città, nessuna pubblicità |
| **nwpc.dole.gov.ph** (ufficiale) | pagina per regione con importi e scaglioni (Regione III: 500 + 30 + 30 = 560…) | nessuna risposta "al mese" o "all'ora", nessuna pagina per città |
| Altri | giornali (GMA, Inquirer, Tribune, SunStar) a ogni ordinanza; studi paghe (payrollsolutions.ph, fermo all'ordinanza 2025); per la tredicesima almeno 8 calcolatrici (omnihr, pesohub, totalcalchub, moneymax, sweldoph…) | — |

**Vuoto dimostrato: piccolo.** Resta scoperta solo la pagina per singola città fuori da CALABARZON e la conversione oraria. Ma fuori da CALABARZON molte regioni hanno una o due cifre per tutti: le pagine per città sarebbero lo stesso numero ripetuto, cioè proprio il modello per cui la pubblicità ha respinto un sito gemello.

### Messico: calcolatrici (5 esempi: aguinaldo proporzionale netto, finiquito per dimissioni, liquidazione per licenziamento, salario minimo professionale del muratore, ferie)

| Concorrente | Che cosa ha | Che cosa manca |
|---|---|---|
| **calculatuaguinaldo.mx** | aguinaldo, ISR e finiquito "con cifre ufficiali 2026", guide su ferie, straordinari, cedolino; pubblicità presente | PTU, mestieri |
| **calculadoralaboral.mx** | stipendio netto, finiquito, licenziamento ingiustificato, guide di confronto | aguinaldo, ferie; nessuna pubblicità |
| **calculadorafiniquito.mx** | finiquito e liquidazione con gli articoli di legge | titolo fermo al 2025 |
| Altri in classifica | software paghe con calcolatrice (Runa: 5 pagine; Buk: 2; Facturama; Alegra), reti di calcolatrici in molti Paesi (hacecuentas, calcforlife, calcuris, contable.app, fedratecalc), studi legali, in tutto circa 20 calcolatrici solo per il finiquito | Alcune usano valori vecchi (salario minimo 278,80 invece di 315,04; UMA 113,14 invece di 117,31): l'unico spazio è l'esattezza, che da sola non porta visite |
| Salario minimo professionale | lo danno i giornali a ogni gennaio (Uno TV, El Imparcial, N+, El Contribuyente): oficial de albañilería 363,44 generale e 440,87 frontiera | la tabella è di 61 righe × 2 zone: troppo poco per un sito |

**Vuoto dimostrato: NO.**

### Brasile, Argentina, Colombia, Cile, Perù (lettura più breve)

- **Brasile**: salario.com.br ("più di 10 mila mestieri e 1.300 settori per Stato e città", dati CAGED, con "piso salarial: media di convenzioni e accordi", in parte a pagamento, pubblicità presente) e numerando.com.br danno la media statistica. Per "piso salarial vigilante 2026 SP" la ricerca non ha trovato la cifra della convenzione 2026: solo PDF di sindacati e una notizia con l'aumento del 5,75 %. **Qui il vuoto c'è** (la cifra esatta della convenzione per categoria e Stato), **ma la fonte ufficiale risponde 403**.
- **Argentina**: una scala al mese per l'inflazione; iProfesional pubblica più articoli al mese per ogni scala, più due siti già citati per nome nei suggerimenti e calcularsueldo.com.ar. Pubblicità in pesos: il valore più basso di tutti.
- **Colombia**: calcolatrice ufficiale del Ministero (non calcola le indennità), più Actualícese, Softland, Alegra, Magneto, hacecuentas, calcuris, contable.app.
- **Cile e Perù**: l'ente pubblico e i software paghe sono già dentro i suggerimenti ("dt", "buk", "talana", "sunafil"). Fonti non lette, mercati piccoli.

## 4. Chi paga

- **Pubblicità**: è l'unico pagatore reale. Chi cerca è un lavoratore, non chi compra software. Resa per mille pagine **stimata, non letta**: Filippine 0,6-1,4 €; Messico, Colombia, Perù, Brasile 1-2,5 €; Argentina sotto 1 €; Spagna 3-6 €.
- **Software paghe e risorse umane**: nessun programma di affiliazione con cifra e condizioni scritte trovato. Lette: Holded (pagina "afiliados": solo sconti per i clienti, nessuna commissione scritta), Runa (pagina partner: nessuna cifra), Buk e Sesame (nessuna cifra), Factorial, Kenjo, Sprout (pagine 404). PayFit Spagna mostra "ogni azienda che ci raccomandi può darti 500 €" fino al 30/11/2026: è un invito a segnalare aziende, letto su un avviso, **senza condizioni lette**; e i nostri lettori sarebbero dipendenti, non titolari.
- **Prestiti a chi aspetta lo stipendio** (Messico, Filippine): esistono e pagano, ma è credito caro a persone in difficoltà: non proposto.

**Prova del pagatore: NO in tutti i mercati** (solo pubblicità a bassa resa; in Spagna resa discreta ma senza vuoto).

## 5. Le idee, in ordine

### 1) Filippine: salario minimo per città e provincia dalle ordinanze NWPC, con paga oraria, mensile, tredicesima, straordinario — voto 4,5

- Dove: sito nuovo in inglese. Ore: 14-16 di agenti (17 regioni, lettura ottica per le ordinanze in scansione), 0 di Massimiliano.
- Stima a 18 mesi: **40 / 300 / 2.000 €/anno**. Centrale: 25.000 pagine viste al mese × 12 × 1,0 € per mille. Ottimista: 120.000 al mese × 1,4 €.
- 4 prove: domanda **SÌ**; dati **SÌ a metà** (testo in alcune ordinanze, scansione in altre; regola sull'uso commerciale non letta); pagatore **NO**; nessuno fa meglio **NO** (sweldoph.com aggiornato il giorno stesso dell'ordinanza).
- Rischio: pagine per città con la stessa cifra = modello ripetuto.

### 2) Brasile: la cifra esatta del "piso" della convenzione per categoria × Stato × anno — voto 4

- Stima a 18 mesi: **0 / 400 / 4.000 €/anno**, valida solo se la fonte si aprisse. Ore: 40-60 di agenti (migliaia di convenzioni, una per sindacato e città).
- 4 prove: domanda **SÌ** (la più larga dopo la Spagna); dati **NO** (archivio ufficiale 403); pagatore **NO**; nessuno fa meglio **SÌ a metà** (salario.com.br dà la media, non la clausola).
- È l'unico mercato dove il vuoto esiste. Si riapre solo se un giorno l'archivio delle convenzioni risponde da una rete normale o pubblica un file aperto.

### 3) Spagna: tabelle salariali per contratto provinciale — voto 3

- Stima a 18 mesi: **30 / 200 / 2.500 €/anno**. Ore: 60-90 di agenti per 100 contratti (circa 50 bollettini diversi).
- 4 prove: domanda **SÌ** (la più simile all'Italia); dati **SÌ a metà** (API del BOE solo per i contratti statali; i provinciali sparsi); pagatore **a metà** (pubblicità con resa discreta, nessuna affiliazione scritta); nessuno fa meglio **NO** (1.883 e 1.205 contratti già online, aggiornati, con file gratuiti).

### Scartate senza stima

- **Messico, calcolatrici di aguinaldo, finiquito, PTU, ferie** — voto 3: circa 20 calcolatrici, tre siti dedicati, i software paghe in cima; poche pagine possibili, tutte di formula.
- **Messico, salario minimo professionale per mestiere** — voto 3: 61 righe, i giornali le pubblicano ogni gennaio.
- **Argentina, scale salariali mensili** — voto 2,5: aggiornamento ogni mese, giornali specializzati, resa minima.
- **Colombia, Cile, Perù** — voto 2,5: calcolatrice ufficiale più software paghe già nei suggerimenti.
- **Filippine, calcolatrice della tredicesima** — voto 2,5: almeno 8 calcolatrici, una stagione sola.

## 6. Che cosa portare a casa

1. **Non aprire nessuno di questi mercati.** Nessuna idea supera 4,5.
2. **Per il sito italiano di oggi, copiare ciò che in Spagna funziona** (è espansione di un sito esistente, non idea nuova): per ogni tabella il numero e la data dell'atto ufficiale in alto; scelta della categoria con risposta "quanto ti spetta"; pagina per anno; costo per l'azienda; calcolo degli arretrati dopo un rinnovo; avviso quando il contratto cambia; scarico del file. Il sito spagnolo senza pubblicità vive di area professionale e API: è un secondo pagatore possibile anche in Italia (consulenti del lavoro), da verificare a parte.
3. Unica porta da ricontrollare fra qualche mese: l'archivio brasiliano delle convenzioni.
