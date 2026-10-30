# Ricerca di zona del 30/10/2026: America Latina e Africa

Richiesta di Massimiliano: "il mondo è molto più grande, ci sono più opportunità e tu non le stai trovando". Obiettivo: idee da voto 8-9 per siti o sezioni automatici (script Python, dati ufficiali, Netlify), pagati da AdSense e da affiliazioni con nome. Regola del 30/10 ("rete fitta"): si costruisce anche ogni sezione piccola a costo zero con guadagno atteso positivo; l'asticella voto ≥ 7 e ≥ 5.000 €/anno vale solo per i siti nuovi.

**Zona:** Messico, Brasile, Argentina, Colombia, Cile, Perù, Costa Rica, Panama, Repubblica Dominicana; Nigeria, Kenya, Sudafrica, Ghana, Egitto, Marocco. Guardate in due direzioni: pubblici locali (spagnolo, portoghese, inglese) e stranieri che vanno lì (pensionati e nomadi, turisti).

**Riletti prima:** `ESPLORATE.md` per intero, i rapporti del 28-30/10 e gli studi 16 e 18 (che avevano già toccato Messico, Costa Rica, Panama, Colombia, dólar blue, Hoy No Circula, pedaggi messicani, moduli d'ingresso). Non ho rivalutato le idee chiuse; dove un fatto nuovo cambia un voto, lo scrivo.

**Lavoro fatto:** 86 interrogazioni all'autocomplete (gl = us, ca, gb, mx, br, co, ng, ke, za), circa 60 prove con curl dal server, 8 ricerche web per la prima pagina, lettura di 3 testi di legge ufficiali (Ley de Derechos del Quintana Roo, Ley Federal de Derechos del Messico, comunicato INEGI sulla UMA 2026).

---

## 0. Risposta in breve

**Nessuna idea arriva a 8 con le prove di oggi.** La zona conferma la lezione di Canada e Australia, con una differenza: qui i pubblici locali valgono poco in pubblicità e i portali ufficiali (WAEC, JAMB, SASSA, Detran, SRE) rispondono già. Il valore sta negli **stranieri che vanno nella zona**: turisti americani, canadesi e britannici in Messico, viaggiatori verso l'Africa e il Sud America che devono avere il certificato della febbre gialla, pensionati americani che cercano la residenza.

**La migliore è una sezione da 7,5: "Tasse per i turisti stranieri in Messico" dentro Tourist Tax Calculator** (Visitax del Quintana Roo per Cancún, Tulum, Playa del Carmen e Cozumel; diritto federale DNR; tassa sulle crociere che sale per legge; nuove tasse comunali di Puerto Vallarta e Los Cabos). Perché è la migliore:
- **la cifra ufficiale si calcola da sola**: la legge del Quintana Roo fissa il Visitax a **2,50 UMA** (art. 51-Octies), e l'INEGI pubblica la UMA ogni gennaio. Dal 1/2/2026: 2,50 × 117,31 = **293,28 pesos** (circa 15,5 $ al cambio BCE del 30/10). A gennaio 2026 valeva ancora 2,50 × 113,14 = 282,85 pesos;
- **in prima pagina le cifre si contraddicono**: 271, 283, 285, "280-300", 300 pesos, "15-18 $", e un rivenditore che chiede 35 $. Nessuno spiega la formula;
- **domanda enorme e pubblico che vale**: Cancún è la prima meta estera degli americani. "visitax", "cancun tourist tax", "quintana roo tourist tax", "mexico tourist tax" hanno 10 varianti ciascuna, con "2026", "official website", "airport", "tui", "royal caribbean", "cabo", "puerto vallarta";
- **è il momento giusto**: la stagione alta di Cancún va da dicembre ad aprile, e la UMA 2027 esce verso l'8 gennaio 2027 (in vigore dal 1/2/2027). Tourist Tax ha già la pagina-calendario dei cambi 2027.

Non arriva a 8 perché Tourist Tax ha pochissime visite (3 a settimana al 28/10), il sito ufficiale `visitax.gob.mx` è primo per le domande "official website", e giornali locali in inglese (The Cancun Sun, Riviera Maya News) scrivono un articolo a settimana sul tema.

| # | Candidata | Dove | Voto | €/anno a 12 mesi (prud. / centr. / ott.) | €/anno a 18 mesi (prud. / centr. / ott.) | Ore |
|---|---|---|---|---|---|---|
| 1 | **Tasse per i turisti stranieri in Messico** (Visitax = 2,5 UMA, DNR, crociere, Cozumel, Puerto Vallarta, Los Cabos, tassa d'uscita Costa Rica, tarjeta turística dominicana) | sezione di Tourist Tax Calculator | **7,5** | 150 / 600 / 2.500 | 400 / 1.500 / 5.000 | 12-18 |
| 2 | **Certificato della febbre gialla: serve per [Paese] se arrivo da / passo per [Paese]?** (CDC per destinazione, consigli britannici, lista OMS; Kenya, Sudafrica, Tanzania, Colombia, Brasile, Costa Rica, Egitto) | sezione di Before You Fly | **7** (condizionato al sì sul tema sanitario) | 100 / 400 / 1.500 | 300 / 900 / 3.000 | 14-20 |
| 3 | Reddito minimo per la residenza di pensionati e nomadi in America Latina (Messico, Costa Rica, Panama, Colombia, Brasile, Rep. Dominicana, Perù, Ecuador) + costi ufficiali dei permessi messicani | sezione di Visa Income Checker | 6,5 | 50 / 200 / 800 | 100 / 500 / 2.000 | 15-25 (4-6 per la sola pagina costi Messico) |
| 4 | Tariffe dei parchi per stranieri (Masai Mara, KWS, Kruger) | Tourist Tax | 5,5 (riserva) | – | – | – |
| 5 | Tassa di soggiorno in Marocco (Marrakech, Agadir) | Tourist Tax | 5,5 (riserva) | – | – | – |
| 6 | Guidare in Messico con l'auto americana (permesso TIP, deposito, assicurazione messicana obbligatoria) | Before You Fly, "Before you drive" | 5,5 (riserva) | – | – | – |
| 7 | Rinnovo del passaporto dal Regno Unito e dagli USA per nigeriani, ghanesi, sudafricani | Visa Income | 5,5 (riserva) | – | – | – |
| – | Altre 16 famiglie (esami e portali locali, salari minimi, passaporti locali, moduli d'ingresso) | | NO (2,5-5) | | | |

**Da costruire subito come sezioni (rete fitta):** la n. 1 (12-18 ore, prima di dicembre) e, dentro la n. 3, solo la pagina "Mexico residency fees 2026" con i costi della Ley Federal de Derechos (4-6 ore). La n. 2 si costruisce appena Massimiliano dice sì al tema "certificato sanitario d'ingresso" (non è un consiglio medico: è un documento di frontiera, ma parla di un vaccino).

---

## 1. Candidata 1 (voto 7,5): tasse per i turisti stranieri in Messico

### 1.1 L'idea in una riga
Una pagina per ogni meta messicana molto cercata (Cancún, Tulum, Playa del Carmen, Cozumel, Isla Mujeres, Holbox, Bacalar, Los Cabos, Puerto Vallarta, porti delle crociere) con: quanto si paga oggi e dal 1/2/2027, chi paga (bambini compresi), come si paga, cosa è già nel biglietto, cosa è in discussione. Calcolatore "quanto pago in tutto per la mia famiglia" in pesos, dollari, sterline, euro.

### 1.2 Fonti (provate dal server il 30/10/2026)
| Fonte | Esito | Cosa dà |
|---|---|---|
| Ley de Derechos del Estado de Quintana Roo, testo del 18/12/2025, `documentos.congresoqroo.gob.mx/leyes/L195-XVIII-20251218-L1820251216196-Ley-de-Derechos.pdf` | 200, PDF, testo estraibile con `pdftotext` | art. 51-Octies: "Las personas visitantes extranjeras al ingresar al Estado deberán pagar… **2.50 UMA**" |
| Elenco delle versioni della legge, `congresoqroo.gob.mx/leyes/195/` | 200 | lo script vede subito se esce una versione nuova |
| INEGI, comunicato UMA 2026, `inegi.org.mx/contenidos/saladeprensa/boletines/2026/uma/uma2026.pdf` | 200, PDF | UMA giornaliera **117,31 pesos dal 1/2/2026** (+3,69 %). Il percorso del 2027 si prova a gennaio |
| Ley Federal de Derechos, `diputados.gob.mx/LeyesBiblio/pdf/LFD.pdf` (ultima riforma DOF 7/11/2025) | 200, PDF 5 MB | art. 8 fr. I: **DNR 983,00 pesos** (visitante sin permiso, di solito dentro il biglietto aereo); art. 11: esenzione via terra fino a 7 giorni; art. 12: 231,55 pesos per i servizi migratori in aeroporto alla partenza |
| Portale ufficiale `visitax.gob.mx` | 200 | regole pratiche: pagano tutti i turisti stranieri, bambini compresi, anche chi parte da Cozumel. Nessun importo scritto: per questo la cifra va calcolata |
| Cambi BCE (già usati dalla rete) | 200 | MXN, USD, GBP, CAD (30/10: 1 $ = 18,91 pesos) |
| Comuni di Los Cabos, Puerto Vallarta, Cozumel | 200 (home) | da cercare la delibera; Baja California Sur (`cbcs.gob.mx`) 000 |
| Congresso di Jalisco (legge di Puerto Vallarta) | 200 | elenco delle leggi leggibile |

**Licenza:** testi di legge messicani, fatti pubblici; nessun divieto di riuso trovato. Si cita la fonte e la data in ogni pagina.

**Da trovare prima di costruire:** il decreto della tassa sulle crociere (5 $ dal 1/7/2025, 10 $ dal 1/8/2026, 15 $ da luglio 2027, 21 $ da agosto 2028 secondo TravelPulse, Cruise Hive, Fox: nel testo della Ley Federal de Derechos estratto non l'ho trovata, sarà in un articolo transitorio o in un decreto DOF a parte); lo stato giuridico della tassa di Puerto Vallarta (approvata da Jalisco, poi un ricorso, applicata "in forma modificata" secondo Mexico News Daily); la tassa di Los Cabos (Zeta Tijuana parla di 470 pesos a soggiorno proposti in Baja California Sur; il "saneamiento ambiental" di 36,30 pesos a camera e notte va controllato sulla legge comunale).

### 1.3 Domanda (autocomplete, 30/10/2026)
- `visitax` (us): 10 — "visitax cancun", "visitax official website", "visitax cancun airport", "visitax cancun 2026", "visitax quintana roo".
- `cancun tourist tax` (us): 10 — "official website", "2026", "reddit", "when to pay", "cost", "departure date", "airport", "tui".
- `quintana roo tourist tax` (us): 10 — "2026", "visitax", "departure date", "cost".
- `mexico tourist tax` (us): 10 — "cabo", "cancun", "puerto vallarta", "refund", "2026", "guadalajara", "royal caribbean", "tui".
- `cabo tourist tax` (us): 10 — "2026", "visitax", "hotel taxes", "tourist fee".
- `puerto vallarta tourist tax` (us): 10 — "new tourist tax", "foreign tourist tax", "how to pay", "does puerto vallarta have a tourist tax".
- `mexico cruise tax` (us): 10 — "increases", "changes", "passenger tax", "port tax".
- `cancun hotel tax` (us): 10 — "rate", "environmental tax", "taxes and fees".
- `costa rica departure tax` (us): 10 — "liberia", "air canada", "westjet", "united", "2026", "sunwing".
- `dominican republic tourist card` (us): 10 — "online", "fee", "refund".
- `cancun tourist tax tui` (gb), `tulum tourist tax` (us, 8), `cozumel tourist tax` (us, 7), `visitax children` (us, 3).
- `visitax 2027`: 0 oggi (comparirà a gennaio, come "2026" adesso).

### 1.4 Prima pagina di Google ("visitax quintana roo 2026 cost per person", "cancun tourist tax 2026")
Giornali e blog: The Cancun Sun (più articoli), Riviera Maya News ("285 pesos"), TravelPulse, Travel Off Path, Travel Market Report, siti automatici su `pages.dev` ("The $15 Tax Stopping Tourists"), venditori di eSIM. Cifre in contrasto: 271, 283, 285, "280-300", 300 pesos. **Nessuno mostra la formula 2,5 UMA**, nessuno spiega che la cifra cambia il 1° febbraio di ogni anno. Per le domande "official website" vince il portale ufficiale, ed è giusto: le nostre pagine rimandano lì per il pagamento.

### 1.5 Chi paga
- **AdSense** (acceso il 30/10): pubblico americano e canadese di viaggio, il più pagato della rete.
- **DiscoverCars** (affiliato già approvato, online in Before You Fly): l'auto a noleggio a Cancún è uno degli acquisti tipici; riquadro nelle pagine Quintana Roo.
- **Viator** (account creato, in analisi): escursioni a Chichén Itzá, Xcaret, cenotes, dalle stesse pagine.
- **Stay22** (da chiedere, già in lista per Tourist Tax): alberghi a Cancún e Tulum.
- Nessun programma vende il Visitax: non lo vendiamo e non imitiamo il portale (regola sulle pagine che imitano enti). Avviso evidente: "si paga solo su visitax.gob.mx; i siti che chiedono 35 $ non sono ufficiali".

### 1.6 Stima
- 12 mesi: prudente 150 €, centrale 600 €, ottimista 2.500 €.
- 18 mesi: prudente 400 €, centrale 1.500 €, ottimista 5.000 €.
- Conti della stima centrale a 18 mesi: 1.500-2.500 visite al mese nella stagione alta (dicembre-aprile) e 500-800 nel resto dell'anno; AdSense 6-10 € ogni 1.000 pagine viste; 2-5 noleggi DiscoverCars al mese nella stagione alta (circa 18-20 € l'uno), qualche escursione Viator.
- Rischio principale: Tourist Tax è debole su Google (3 visite a settimana). La stima prudente tiene conto di questo.

### 1.7 Ore e motore
12-18 ore riusando il motore di Tourist Tax (destinazioni, calcolatore, pagina-calendario 2027, cambi BCE):
- `raccolta/uma.py`: legge il comunicato INEGI di gennaio (fallback: valore scritto a mano con data) e la lista delle versioni della legge del Quintana Roo; avvisa se compare un PDF nuovo;
- 9-12 pagine destinazione + una pagina "Mexico tourist taxes 2026 and 2027" + righe nel calendario 2027 (Visitax dal 1/2/2027, crociere luglio 2027);
- 2 pagine piccole, stessa sezione: "Costa Rica departure tax" (29 $ già nel biglietto: risponde alle domande delle compagnie Air Canada, WestJet, United, Sunwing) e "Dominican Republic tourist card" (già nel biglietto, solo se la fonte ufficiale si legge: `migracion.gob.do` oggi 403).

### 1.8 Voto e soglie
**7,5.** Sale a **8** se a 30 giorni dalla pubblicazione le pagine Messico hanno almeno 1.500 impressioni al mese in Search Console, o se ChatGPT le cita (provenienza `chatgpt.com` in GoatCounter). Da costruire **prima di metà dicembre** per prendere la stagione alta. Se a 60 giorni le pagine sono sotto 300 impressioni al mese, nessuna destinazione nuova.

---

## 2. Candidata 2 (voto 7, condizionato): certificato della febbre gialla per Paese, provenienza e scalo

### 2.1 L'idea in una riga
"Mi serve il certificato della febbre gialla per entrare in [Kenya, Sudafrica, Tanzania, Costa Rica…] se arrivo da [Paese] o se faccio scalo a [Addis Abeba, Nairobi, Bogotá]?": una pagina per destinazione con la regola d'ingresso ufficiale, la data dell'ultimo aggiornamento e un controllo "da / via / per". Si parla solo del **documento richiesto alla frontiera**, non di chi deve vaccinarsi (per quello: "chiedi a un centro di medicina dei viaggi").

### 2.2 Fonti (provate il 30/10/2026)
| Fonte | Esito | Note |
|---|---|---|
| CDC, pagine destinazione, es. `wwwnc.cdc.gov/travel/destinations/traveler/none/kenya` | 200 (il resto di cdc.gov è 403) | testo strutturato "Country entry requirements": per il Kenya "Direct travel from United States: not required. Travel from countries with risk for YF virus transmission: required for travelers ≥1 year old", con data ("Updated April 23, 2025"). Pubblico dominio USA. Elenco Paesi: `wwwnc.cdc.gov/travel/destinations/list` 200 |
| Consigli di viaggio britannici, API `gov.uk/api/content/foreign-travel-advice/<paese>` | 200, JSON, licenza OGL | frase "Vaccine requirements" per Paese (Kenya: certificato se arrivi da un Paese a rischio) |
| OMS, elenco dei Paesi a rischio e dei Paesi che chiedono la vaccinazione | 200 (pagina), PDF su `cdn.who.int` | **fermo a novembre 2022, rivisto a gennaio 2023**; licenza OMS di solito CC BY-NC-SA (non commerciale): si usano solo i fatti con link, non il documento |
| CDC Yellow Book per Paese | 403 | non serve se bastano le pagine destinazione |
| NHS fitfortravel | 000 | – |
| NaTHNaC travelhealthpro | 200 | contenuti con copyright: solo link |

**Fatto nuovo che apre il buco:** l'OMS non aggiorna l'elenco dal 2023, mentre i Paesi cambiano regola da soli (Costa Rica dall'11/1/2025, focolai in Colombia e Brasile nel 2025-2026, valutazione OMS del rischio globale del 16/6/2026). Il Sudafrica scrive due regole diverse sullo scalo (oltre 12 ore in aeroporto secondo la pagina DIRCO attuale; "qualunque transito" in un documento più vecchio).

### 2.3 Domanda
- `yellow fever vaccine required` (us): 10 — "countries", "for kenya", "for tanzania", "for south africa", "for colombia", "for brazil", "for egypt", "for zambia", "for singapore".
- `yellow fever certificate` (gb): 10 — "kenya", "validity", "south africa", "price".
- `kenya yellow fever` (gb): 10; `south africa yellow fever` (gb): 10 con "exemption", "countries", "entry requirements"; `costa rica yellow fever` (us): 10 con "entry requirements", "exemption"; `colombia yellow fever vaccine requirement` (us): 6.
- `yellow fever transit` (us): 9 — "transit in ethiopia", "singapore", "south africa", "ethiopian airlines".

### 2.4 Prima pagina
CDC, NHS, travelhealthpro, cliniche (Passport Health), DIRCO con pagine vecchie, forum (FlyerTalk, voyageforum) che si contraddicono, blog automatici (`safarifind.com`, `elyforma.com`). Per le domande sullo scalo nessuna fonte dà una risposta chiara: è il buco.

### 2.5 Chi paga, stima, ore
- AdSense (pubblico USA/UK in partenza per safari e Sud America); SafetyWing (riacceso il 30/10) e le assicurazioni di viaggio della lista; nessun programma per i vaccini.
- 12 mesi: 100 / 400 / 1.500 €. 18 mesi: 300 / 900 / 3.000 €.
- 14-20 ore: lettura delle ~230 pagine CDC (una volta al mese), frase britannica come seconda fonte, tabella dei Paesi a rischio con data, controllo "da / via / per", pagine per i 25-30 Paesi più cercati. Stesso motore delle sezioni passaporto di Before You Fly.

### 2.6 Voto
**7**, ma solo con il sì di Massimiliano: il 9/10 la medicina era esclusa, e Google tratta i vaccini con prudenza. Se il tema resta escluso: **NO**. Da far confermare a un revisore indipendente che il testo resti "documento richiesto" e non "consiglio medico".

---

## 3. Candidata 3 (voto 6,5): residenza di pensionati e nomadi in America Latina

### 3.1 Cosa c'è già
Visa Income Checker copre 17 programmi europei e britannici; **nessun programma latinoamericano**. Lo studio 16 (10/10) aveva provato Messico, Costa Rica, Panama, Colombia; il fatto nuovo è che ora si leggono le leggi messicane e il cambio colombiano.

### 3.2 Fonti (30/10/2026)
| Paese | Fonte | Esito |
|---|---|---|
| Messico, soglie | consolati `consulmex.sre.gob.mx/<città>` | prime 3 pagine 200, poi **"Radware Captcha Page"** dal nostro server; le soglie "per consolato" non si leggono |
| Messico, soglie di legge | Lineamientos DOF dell'8/11/2012 (`dof.gob.mx/nota_detalle.php?codigo=5276966`) | 200, ma in "giorni di salario minimo"; i consolati oggi usano la UMA con moltiplicatori propri: le cifre ufficiali non coincidono con la pratica |
| Messico, costi dei permessi | Ley Federal de Derechos art. 8 | 200: residente temporaneo 1 anno **11.140,74 pesos**, 2 anni 16.693,36, 3 anni 21.142,58, 4 anni 25.057,82; **residente permanente 13.578,96** (riforma DOF 7/11/2025) |
| Messico, UMA | INEGI | 200 |
| Colombia, soglie | Cancillería (`cancilleria.gov.co/tramites_servicios/visa/...`) | **403** |
| Colombia, cambio | TRM su `datos.gov.co` (API Socrata, JSON) | 200: 3.166,91 pesos per dollaro il 30/10/2026 |
| Costa Rica | `migracion.go.cr` | **403**; SCIJ (`pgrweb.go.cr/scij/`) 200, legge da cercare |
| Panama | `migracion.gob.pa` | 200, ma gli importi non sono nell'HTML della home |
| Brasile | `gov.br/mre/.../vistos-temporarios` | 200, importi non trovati nell'HTML |
| Perù | `gob.pe/migraciones` | 200 |
| Rep. Dominicana | `migracion.gob.do` | **403** |
| Argentina | `migraciones.gov.ar` | 000 (`argentina.gob.ar/interior/migraciones` 200) |

### 3.3 Domanda e concorrenza
Domanda forte dagli USA e dal Canada: "mexico temporary residency" 10 (con "requirements 2026", "income requirements", "cost"), "costa rica pensionado" 10, "costa rica rentista" 10, "costa rica digital nomad visa" 10, "panama pensionado visa" 10 (con "income requirements"), "panama friendly nations visa" 10 (con "country list", "2026"), "colombia retirement visa" 10, "colombia digital nomad visa" 10 (con "for pakistani"), "brazil digital nomad visa" 10 (con "from pakistan", "for indians"), "ecuador pensioner visa" 10, "mexico residency fees 2026" 4.

Concorrenza forte: `mexicorelocationguide.com` ha già la tabella **per consolato**, più nomad.watch, getwherenext, International Living, Mexperience, borderpilot e vari siti automatici su `pages.dev` (mexpath-site, roamjobs, remote-work-tools).

### 3.4 Perché solo 6,5
- Le pagine "income requirements" di Visa Income hanno **0 visite** finora (le visite vengono dai rifiuti dei visti, dal 21/10): la stessa forma in America Latina parte con lo stesso svantaggio.
- La cifra più cercata (Messico per consolato) non si legge dal server; quella di legge non coincide con la pratica.
- Tre fonti su otto chiuse (Costa Rica, Colombia, Rep. Dominicana).

### 3.5 Cosa costruire comunque (rete fitta)
**Solo la pagina "Mexico residency fees 2026 (and 2027)"** dentro Visa Income: costi ufficiali dei permessi dalla Ley Federal de Derechos, convertiti in dollari ogni giorno, con data della riforma e controllo annuale a novembre-dicembre (la legge si riforma di solito a novembre). 4-6 ore, 100-400 €/anno a 18 mesi, ottimista 1.000. Da controllare prima: che il SAT non pubblichi importi aggiornati diversi (Anexo 19 della Resolución Miscelánea, non provato oggi).

Il resto della sezione (Costa Rica, Panama, Colombia, Brasile, Ecuador, Perù) si riapre se a fine novembre le pagine europee "income requirements" mostrano impressioni.

---

## 4. Riserve (voto 5-5,5)

| Nicchia | Voto | Prove | Si riapre se |
|---|---|---|---|
| **Tariffe dei parchi per stranieri: Masai Mara, parchi KWS, Kruger** | 5,5 | domanda forte e datata: "masai mara park fees for non residents 2026" (con "pdf"), "kenya park fees 2026" 7, "kruger park entrance fee 2026 / 2027 / international" 10; le tariffe SANParks cambiano ogni 1° novembre. Ma `kws.go.ke` 000, `sanparks.org` 403 (anche la pagina tariffe), Masai Mara gestita dalla contea di Narok; SafariBookings ha già una pagina "park fees" per ogni parco | `sanparks.org` e `kws.go.ke` si leggono da GitHub Actions |
| **Tassa di soggiorno in Marocco** (Marrakech, Agadir) | 5,5 | domanda britannica da pacchetto vacanza: "morocco tourist tax" 10 (con "in pounds", "4 star hotel", "calculator", "easyjet", "2026"), "marrakech tourist tax" 10, "agadir tourist tax" 10; cifre in contrasto (Eurowings 30/25/10/5 dirham, Wise 11 + 15, Upsilon 15/11/8 per la tassa di promozione turistica e 10-25 per la tassa di soggiorno). Ma la tariffa vera la fissa ogni Comune dentro una forbice (legge 47-06 modificata, gestione passata alla DGI con la legge 14-25); `sgg.gov.ma` 000, ricerca DGI 403 | si trova il testo ufficiale (Bulletin Officiel o DGI) con le forbici: allora pagina "da… a… dirham, chiedi all'hotel" in Tourist Tax, 3-5 ore |
| **Guidare in Messico con l'auto americana** (permesso TIP, deposito per anno del veicolo, zona libera, assicurazione messicana obbligatoria) | 5,5 | "banjercito tip" 10, "mexican car insurance" 10 (con "costco", "rocky point", "san ysidro"), "driving to mexico requirements" 5; Baja Bound ha un programma di affiliazione (pagamento mensile oltre 25 $, percentuale non pubblica). Ma `banjercito.com.mx` 000, regole doganali sparse, Baja Bound, MexPro, Sanborn's, Mexperience già in pagina | si legge Banjercito e Baja Bound pubblica la commissione: allora una pagina nel blocco "Before you drive" |
| **Rinnovo del passaporto dal Regno Unito e dagli USA per nigeriani, ghanesi, sudafricani** | 5,5 | domanda vera da pubblici che vivono in UK/USA: "nigerian passport renewal fee uk" 10 (con "10 years", "5 years", "fast track"), "nigerian passport renewal fee in usa" 10 (con New York, Atlanta, Washington), "ghana passport renewal uk" 10, "south african passport renewal uk" 10 (con "cost", "vfs", "processing time"). Ma una tabella di tariffe per Paese, ambasciate e giornali (Punch, Premium Times) già in pagina, nessuna affiliazione; `immigration.gov.ng` 200, `ecitizen.go.ke` 403, DHA 404, `passport.gov.gh` 000. Stessa famiglia del NO del 23/10 sui tempi dei passaporti | mai da sola; al massimo righe in una pagina di Visa Income |
| Costo del passaporto messicano negli Stati Uniti (in spagnolo) | 5 | "costo pasaporte mexicano 2026 en estados unidos" 7, "costo pasaporte mexicano 2026" 10; la legge (LFD art. 20) dà i pesos, ma i consolati incassano in dollari con un cambio loro e le pagine consolari sono dietro Radware; gob.mx e giornali (El Universal, Infobae) rispondono ogni gennaio | – |

---

## 5. NO (con le prove)

| Nicchia | Voto | Motivo |
|---|---|---|
| Risultati WAEC e JAMB (Nigeria) | 2,5 | "jamb result checker", "waec result checker" 10 ciascuna: chi cerca vuole il portale ufficiale; pubblico nigeriano che vale pochissimo |
| Punteggi minimi JAMB per università (Nigeria), KUCCPS (Kenya), APS (Sudafrica) | 3-3,5 | myschool.ng e simili, calcolatori già in pagina, pubblico locale |
| Date dei pagamenti SASSA (Sudafrica) | 3 | giornali in giornata, portale ufficiale |
| Salario minimo 2027 in Colombia, aguinaldo e prima | 3,5 | "salario mínimo 2027 colombia" 8, ma notizie del giorno; pubblico locale |
| Costi della patente brasiliana (CNH) per Stato | 4 | 27 Detran, portoghese, pubblicità brasiliana bassa |
| Tariffe dei passaporti in Nigeria, Kenya, Sudafrica (in patria) | 4 | domanda forte ("kenya passport fees 2026" 10, "south african passport price 2026" 10) ma una tabella dell'ente, giornali, pubblico locale |
| Visto all'arrivo in Egitto (costo) | 4 | "egypt visa on arrival cost" 10 (con "in pounds", "price increase"), ma una cifra; portale ufficiale e giornali |
| e-visa del Brasile per americani, ETA del Kenya, ETA del Sudafrica, e-ticket dominicano | 3-4 | moduli d'ingresso: chi cerca vuole il sito ufficiale (stesso NO dello studio 18) |
| Taxa de Preservação Ambiental di Fernando de Noronha | 5 | domanda in portoghese con "valor 2026", "isenção"; il sito ufficiale ha già la tabella per giorni; pubblico brasiliano |
| Biglietto del parco di Rapa Nui | 3 | una cifra, ente e agenzie |
| Appuntamenti consolari delle diaspore (MiConsulado, Colombia, Brasile, Nigeria) | 2,5 | prenotazioni ufficiali, nessun dato pubblico |
| Tassa sulle crociere in Messico da sola | 4 | confermato il NO del 28/10: entra come riga della candidata 1 |
| Esami nazionali (EXANI, ICFES, ENEM) | 3 | date nazionali, portali ufficiali, giornali |
| Cambio e limiti valuta (Argentina, Nigeria) | – | già NO (studio 18: dólar blue); nessun fatto nuovo |
| Hoy No Circula, pedaggi messicani | – | già NO (studio 18) |
| Confronto "Mexico vs Costa Rica vs Panama retirement" | 2 | autocomplete 0 |

---

## 6. Lezioni della zona

1. **I pubblici locali di America Latina e Africa non pagano la rete.** Le domande più forti (WAEC, JAMB, SASSA, salario minimo, passaporti) hanno un portale ufficiale che risponde e un pubblico che in pubblicità vale 0,2-1 € ogni 1.000 pagine viste.
2. **Il valore sta negli stranieri che ci vanno**, quando la regola è locale, scritta in spagnolo dentro una legge, e cambia con una data: è la forma che funziona in Tourist Tax e Before You Fly.
3. **In Messico molte cifre sono "UMA × un numero".** Se la legge è leggibile, la cifra di domani si calcola oggi: è la stessa leva di Visa Income (indice ufficiale × cambio del giorno). Oltre al Visitax, la UMA regola multe, tasse e soglie: vale la pena tenerla come indice nella rete (un file, aggiornato ogni gennaio).
4. **I siti del governo messicano chiudono i robot a tratti** (Radware sui consolati dopo tre richieste; DOF 000 sulla home ma 200 sulle singole note). Le leggi pubblicate dai Congressi (`diputados.gob.mx`, `congresoqroo.gob.mx`) sono la via sicura.

---

## 7. Righe proposte per `ESPLORATE.md` (da aggiungere da chi coordina)

| Nicchia | Verdetto | Rapporto |
|---|---|---|
| **Tasse per i turisti stranieri in Messico** (Visitax = 2,5 UMA dalla Ley de Derechos del Quintana Roo, 293,28 pesos dal 1/2/2026; DNR 983 pesos; crociere; Puerto Vallarta, Los Cabos, Cozumel; tassa d'uscita Costa Rica) | **PASSA** (voto 7,5; 400-1.500 €/anno a 18 mesi, ottimista 5.000; 12-18 ore) come sezione di Tourist Tax, prima di metà dicembre | ricerca-zona-latam-africa-2026-10-30 |
| **Certificato della febbre gialla per destinazione, provenienza e scalo** (CDC destinazioni 200 pubblico dominio, FCDO OGL; elenco OMS fermo al 2023) | **PASSA condizionata** (voto 7; 300-900 €/anno a 18 mesi; 14-20 ore) come sezione di Before You Fly, solo con il sì di Massimiliano sul tema | ricerca-zona-latam-africa-2026-10-30 |
| Reddito per la residenza di pensionati e nomadi in America Latina | RISERVA (6,5): consolati messicani dietro Radware, Costa Rica, Colombia e Rep. Dominicana 403, mexicorelocationguide con la tabella per consolato; si costruisce solo la pagina "Mexico residency fees" (4-6 ore) | ricerca-zona-latam-africa-2026-10-30 |
| Tariffe dei parchi (Masai Mara, KWS, Kruger); tassa di soggiorno in Marocco; guidare in Messico con l'auto americana; rinnovo del passaporto per nigeriani, ghanesi, sudafricani in UK/USA | RISERVE (5,5) | ricerca-zona-latam-africa-2026-10-30 |
| WAEC/JAMB, punteggi JAMB/KUCCPS/APS, SASSA, salario minimo Colombia, CNH Brasile, passaporti in patria (NG, KE, ZA), visto all'arrivo Egitto, e-visa Brasile, ETA Kenya/Sudafrica, e-ticket dominicano, Noronha, Rapa Nui, appuntamenti consolari, esami nazionali | NO (2-5) | ricerca-zona-latam-africa-2026-10-30 |
