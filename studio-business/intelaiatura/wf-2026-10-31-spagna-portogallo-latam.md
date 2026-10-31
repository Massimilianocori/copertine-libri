# Spagna, Portogallo e America Latina: burocrazia, esami, passaporti e visti (31/10/2026)

Angolo di questo giro: i passaggi obbligati di chi vive o viaggia tra Spagna, Portogallo e America Latina (cita previa, NIE/TIE, arraigo, nazionalità per residenza con CCSE/DELE, AIMA e nazionalità portoghese, passaporti e visti di Brasile, Messico e Argentina). Esclusi gli esami EOI, già bocciati dal verificatore oggi.

**Letto prima:** skill `rete-siti`, `REGOLE-FISSE.md` (regole del 31/10: fronti nuovi, conta il fatturato, niente lavori a ore), `ESPLORATE.md` per intero, `idee-2026-10-31-lingue.md`, `ricerca-zona-latam-africa-2026-10-30.md`, studi 2, 4, 16 e 18 sulle stesse nicchie. Le idee già chiuse non le ho rivalutate; dove c'è un **fatto nuovo** lo scrivo.

**Metodo:** autocomplete di Google (`client=firefox`) con lingua e Paese giusti (es/es, es/mx, es/co, es/ar, es/pe, es/ve, pt-BR/br, pt-PT/pt, en/us, en/gb, en/in), letto il 31/10/2026; prima pagina con la ricerca web (dagli USA: non è il Google del Paese, lo segnalo dove conta); fonti con `curl` dal nostro server il 31/10/2026 (stato HTTP e dimensione). Stime: lordo annuo a 18 mesi dalla pubblicazione, formula del 30/10 (visite al mese × 12 × guadagno ogni 1.000 visite). File scaricati e script sono rimasti nella cartella temporanea della sessione: nel repository c'è solo questo file. Nessun blocco anti-robot aggirato: dove una fonte risponde 403, 000 o con una pagina di blocco, mi sono fermato.

---

## 0. Risposta in breve

**Nessuna idea passa l'asticella dei siti nuovi** (voto ≥ 7 e ≥ 5.000 €/anno centrali). La migliore come sito (esami di spagnolo DELE, SIELE e CCSE nel mondo) arriva a 6,5 con 2.600 €/anno centrali. **Una sezione piccola conviene costruirla subito** perché i dati li abbiamo già: "¿Cuánto dinero necesito para entrar a Europa?" in spagnolo e portoghese dentro Visa Income Checker.

| # | Idea | Dove, lingua | Chi paga | €/anno a 18 mesi (prudente / centrale / ottimista) | Ore | Voto |
|---|---|---|---|---|---|---|
| 1 | **Esami di spagnolo nel mondo: DELE, SIELE e CCSE** (date 2027, centri e prezzi per città, risultati, "avvisami"): il gemello di EsameB1 | sito nuovo; inglese + spagnolo + portoghese | italki/Preply (insegnanti di spagnolo), AdSense USA/UK/Spagna, Amazon | 600 / 2.600 / 9.600 | 45-60 | **6,5** |
| 2 | **"¿Cuánto dinero necesito para entrar a España / Europa?" e "Quanto dinheiro para entrar em Portugal / na Europa?"**: calcolatore per Paese Schengen, in valuta locale, con i requisiti di ingresso per chi non ha bisogno del visto | sezione di Visa Income Checker; spagnolo + portoghese | IATI (10 % a polizza, programmi CO/PE/PT/ES), AdSense, Wise | 150 / 700 / 3.200 | 10-14 | **6,5** (sezione da costruire) |
| 3 | **Passaporto spagnolo × 197 destinazioni** (visto, validità, eVisa) dalle schede del Ministero degli Esteri | sezione di Before You Fly in spagnolo | IATI ES, Heymondo, AdSense Spagna | 200 / 900 / 3.500 | 20-30 | 5,5 (fatto nuovo: la fonte ora risponde 200) |
| 4 | **Tempo di attesa per il visto USA per consolato** (Messico, Brasile, Colombia, Ecuador, Perù, Guatemala, Spagna) | sezione, spagnolo + portoghese | AdSense America Latina | 300 / 1.200 / 4.000 *solo se la fonte si legge* | 12-18 | 5 (oggi NO: travel.state.gov 403) |
| 5 | **Nazionalità spagnola: quanto ci vuole davvero** (dati ufficiali trimestrali per anno di domanda) | pagina in spagnolo | AdSense Spagna | 100 / 400 / 1.200 | 5-8 | 4,5 |
| 6 | Passaporti di Messico, Brasile, Colombia, Argentina × destinazioni ("¿necesito visa para…?") | sezione, spagnolo + portoghese | IATI CO/PE, AdSense | – | – | 3,5 (NO: fonti chiuse) |
| 7 | Portogallo: tempi della nazionalità e di AIMA | portoghese | AdSense PT/BR | – | – | 3 (NO: nessun dato per ufficio, AIMA 000) |
| 8 | Argentina nel Visa Waiver Program degli USA ("¿cuándo empieza?") | spagnolo | AdSense Argentina | – | – | 3 (NO: evento senza data, solo notizie) |
| 9 | Cita previa extranjería, huellas TIE, NIE per ufficio | spagnolo | – | – | – | NO confermato (nessun fatto nuovo: `icp…` 000, `inclusion.gob.es` 403) |
| 10 | Passaporto brasiliano: appuntamenti e tassa (Polícia Federal) | portoghese | – | – | – | NO (gov.br risponde con la pagina di blocco "Acesso Temporariamente Interrompido") |

**Cosa propongo:**
- **Costruire subito la n. 2** come sezione di Visa Income (rete fitta: costo quasi zero, i dati dei 29 Paesi Schengen sono già in `visaincome/dati/schengen_residenti.json`). Prima entrata: AdSense dal primo mese; IATI dopo l'iscrizione di Massimiliano al programma su Tradedoubler (10 minuti). Data utile: il salario minimo spagnolo 2027 cambia la cifra per la Spagna (oggi 122,10 € al giorno): pagina pronta prima del decreto, di solito tra gennaio e febbraio.
- **La n. 1 resta RISERVA alta** con un test scritto (sez. 1.6): si riprende solo se il test passa e se EsameB1 continua a crescere.
- La n. 3 aspetta i numeri delle sezioni passaporto di Before You Fly (oggi deboli). La n. 4 entra nel test già previsto da GitHub Actions per travel.state.gov.

---

## 1. Esami di spagnolo nel mondo: DELE, SIELE e CCSE (voto 6,5)

### 1.1 Cosa sarebbe
Un sito "Spanish exams: DELE, SIELE and CCSE dates, centres and fees" in tre lingue:
- **DELE** (diploma di spagnolo, A1-C2): calendario 2027, centri d'esame e prezzi **per città** (USA, Regno Unito, India, Filippine, Brasile, Germania, Francia, Italia, Marocco…), quando escono i risultati, "avvisami quando apre l'iscrizione";
- **CCSE** (esame di cultura per la nazionalità spagnola): 10 convocatorie 2027 con la nuova finestra di appuntamenti, prezzo, uscita delle notas;
- **DELE A2 per la nazionalità** (62.223 candidati nel 2024-25: il livello più fatto).

È lo stesso modello di EsameB1 (date, sedi per città, costo, risultati), con un pubblico in parte di lingua inglese (che vale di più in pubblicità) e che deve davvero imparare la lingua (italki e Preply servono).

### 1.2 Fatti nuovi rispetto alla riserva del 9/10 (studi 2 e 4)
- Il vecchio sito `examenes.cervantes.es` **non esiste più**: ogni pagina rimanda (301) a `cervantes.org/es/examenes/dele`, con la scritta "Estamos preparando una nueva web de exámenes del Instituto Cervantes". **Il vecchio cercatore dei centri (`examenes.cervantes.es/es/dele/donde`) non c'è più**: oggi nessuna fonte ufficiale dà l'elenco dei centri per città in una sola pagina. È un buco vero, ma potrebbe chiudersi quando esce la nuova web (rischio scritto).
- **Calendari 2027 già pubblicati** (pagina `cervantes.org/es/examenes/dele`, 200, 177 KB, letta il 31/10/2026): DELE il 5/3, 2/4, 21-22/5, 9/7, 10/9, 15/10, 12-13/11/2027, iscrizioni dal 18/11/2026; CCSE 10 convocatorie, iscrizioni dal 23/11/2026.
- **Il CCSE cambia nel 2027:** la tabella ha ora "Inicio de citas" e "Fin de citas" (es. gennaio: chiusura iscrizioni 7/1, appuntamenti dal 14 al 28/1). Il candidato sceglie un giorno nella finestra: la ricerca "cita examen ccse" (10 varianti) crescerà. La disponibilità dei giorni però sta nel negozio online `tienda.cervantes.org` (piattaforma Salesforce, pagine in JavaScript, robots aperto): non provata, e non va letta se richiede l'accesso.
- **Numeri ufficiali** (Memoria Cervantes 2024-25, PDF 200, 946 KB): **142.379 candidati DELE**, **1.307 centri DELE in 120 Paesi**; SIELE 18.412 certificati in 69 Paesi; CCSE 1.278.831 candidati dal 2015 in 221 centri (circa 130.000 l'anno).

### 1.3 Domanda
- en/us: "dele exam" 10 (**centers in usa**, cost, **nyc**, dates 2026/2027); "dele test centers" 10 (**usa, india, california, texas, mumbai, near me**); "dele exam cost" 10 (**fees in india, price philippines**, per livello A2-C2); "siele exam" 10 (cost, dates, centers, fees in india).
- en/gb: "dele exam" 10 (dates 2026/2027, fees, results). en/in: "dele exam" 10 (dates 2026 india, **in india**, fees, result).
- es/es: "examen ccse" 10 ("300 preguntas pdf 2026"…); "notas ccse" 6 (**per mese**: octubre 2025, noviembre 2025, abril 2026); "cita examen ccse" 10 (madrid, cambiar cita); "dele a2 nacionalidad" 10; "resultados dele" 10 (**per sessione e livello**: a2 mayo 2026, b2, c1, c2); "dele 2026" 10.
- pt-BR/br: "exame dele" 10 (espanhol 2026, b2, a2, c1); "dele 2027" 10.

Domanda per città, costo e risultati, come EsameB1, e in tre mercati.

### 1.4 Prima pagina e concorrenza
Ricerca "DELE exam centers in Texas 2027 dates fees": **nessuna pagina con i centri del Texas**; escono blog di scuole (aporeldele, fedele.org, spainexchange, gogoespana), pagine di singole università (Calgary, Exeter, Leicester, Santiago), una scuola di Brooklyn. Le date generali sono già coperte bene (fedele, aporeldele); **centri e prezzi per città no**. Per il CCSE in spagnolo: goveasy, machelindiaz, arc-legal, accademie; le notas mensili le danno i blog.

### 1.5 Fonti (31/10/2026)
| Fonte | HTTP | Note |
|---|---|---|
| `cervantes.org/es/examenes/dele` | 200, 177 KB | calendari DELE e CCSE 2026-2027 in HTML, leggibili con regole semplici |
| `cervantes.org/es/examenes/ccse` | 200, 172 KB | convocatorie CCSE restanti 2026 |
| Manuale CCSE 2026 (`cervantes.org/.../2026-10/manual-preparacion-prueba-ccse-2026.pdf`) | link presente | le 300 domande ufficiali (il mercato dei quiz è già pieno: non è il nostro terreno) |
| Istituto di Los Angeles (`cervantes.org/us/los-angeles/en/learning-teaching/certification/dele`) | 200, 90 KB | **prezzi** (A1 128 $, A2 130 $, B1 154 $, B2 176 $, C1 195 $, C2 210 $) e **tabella dei centri associati** per sessione |
| Istituto di Nuova Delhi (`nuevadelhi.cervantes.es/en/DELE_ingles/DELE_dates_and_fees.htm`) | 200, 128 KB | sessioni 2026 × centri (New Delhi, Bangalore, Jaipur, Kolkata, Mumbai, Dacca) |
| Istituti di New York, Londra (vecchio sito `*.cervantes.es`) | 200 | pagine DELE con indirizzi diversi per ogni istituto |
| Elenco degli istituti | dal menu di cervantes.org | **71 siti** `*.cervantes.es` più quelli già migrati su cervantes.org |
| `tienda.cervantes.org` | 200, 77 KB | negozio Salesforce in JavaScript; sitemap con 13 pagine generiche; dati dei centri non letti |
| Aviso legal di cervantes.org | – | non letto in questo giro: **da leggere prima di costruire** |

**Il difetto:** i centri e i prezzi stanno **istituto per istituto**, su due sistemi diversi (cervantes.org nuovo e 71 siti vecchi con indirizzi propri). È lo stesso rischio della Germania (85 sedi, 31 leggibili), anche se qui tutte le pagine provate rispondono 200 e hanno tabelle simili. E i 1.307 centri sono di più degli istituti: molti centri associati compaiono solo nella pagina dell'istituto del Paese.

### 1.6 Test tecnico prima di costruire (circa 6 ore, solo lettura)
- Trovare in automatico la pagina "DELE date e prezzi" di **almeno 40 istituti su 71** e leggerne sessioni, centri e prezzi; **≥ 28 controlli a mano su 30 giusti**.
- Coprire almeno: USA (6 istituti), Regno Unito, India, Filippine, Brasile, Germania, Francia, Italia, Marocco.
- Aviso legal di cervantes.org senza divieto di riuso dei fatti.
- Se la nuova web del Cervantes pubblica prima un cercatore dei centri, il test si ferma: il buco si chiude.

### 1.7 Stima
Pubblico: circa 290.000 candidati l'anno (DELE + SIELE + CCSE), circa 2,5 volte EsameB1, ma sparso su 120 Paesi e tre lingue. Guadagno ogni 1.000 visite: 8 € prudente (AdSense misto 3 + italki/Preply 4 + Amazon 1), 12 € centrale, 16 € ottimista (più quota USA/UK).
- Prudente: 6.000 visite × 12 × 8 € / 1.000 ≈ **600 €**
- Centrale: 18.000 × 12 × 12 € / 1.000 ≈ **2.600 €**
- Ottimista: 50.000 × 12 × 16 € / 1.000 ≈ **9.600 €**

Prime entrate: italki dal 2°-3° mese; picchi a novembre-gennaio (iscrizioni 2027 dal 18/11), aprile-maggio, settembre-ottobre.

**Ore 45-60** (lettori per 40-70 istituti, pagine città, CCSE, tre lingue, revisione). **Voto 6,5:** domanda ottima e per città, pubblico che vale, pagatore giusto; ma fonti sparse, buco che può chiudersi con la nuova web ufficiale e stima centrale sotto i 5.000 €. Non passa l'asticella dei siti nuovi.

---

## 2. "¿Cuánto dinero necesito para entrar a Europa?" in spagnolo e portoghese (voto 6,5, sezione)

### 2.1 Cosa sarebbe
Una sezione di Visa Income Checker in spagnolo (`/es/`) e portoghese (`/pt/`) per chi entra in Europa **senza visto** (messicani, colombiani, peruviani, argentini, cileni, venezuelani, brasiliani) o con il visto (ecuadoriani, boliviani, dominicani, cubani):
- una pagina per Paese Schengen: "¿Cuánto dinero necesito para entrar a España / Italia / Francia… en 2026?" e "Quanto dinheiro preciso para entrar em Portugal / na Espanha / na Itália…";
- calcolatore: giorni × persone × importo ufficiale, con il minimo (Spagna: 122,10 € al giorno, almeno 1.098,90 €), in euro, dollari, pesos messicani e real (cambi BCE già usati dal sito);
- cosa chiede la frontiera oltre ai soldi (biglietto di ritorno, alloggio, "carta de invitación" in Spagna), con link ufficiali;
- riquadro assicurazione viaggio (IATI) e, quando ci sarà una data, ETIAS.

### 2.2 Fonte
- **Già nel repository:** `visaincome/dati/schengen_residenti.json` contiene la tabella della Commissione europea sugli importi di riferimento per l'attraversamento delle frontiere (PDF dell'8/6/2026), con Spagna 10 % del salario minimo = **122,10 € al giorno e 1.098,90 € minimi**, Portogallo **75 € per ingresso + 40 € al giorno**, Italia 269,60 € per 1-5 giorni, Francia 120 / 65 / 32,50 €, Germania 45 €, e gli altri. Licenza dei documenti della Commissione: riuso consentito con citazione.
- Ministero dell'Interno spagnolo (`interior.gob.es`, pagina "Entrada: requisitos y condiciones"): **403** dal server; non serve, la cifra spagnola è già nella tabella UE e si ricava dal salario minimo (RD 126/2026: 1.221 €).
- **Data utile:** la cifra spagnola cambia quando esce il salario minimo 2027 (di solito decreto tra gennaio e febbraio): ondata "2027" con data, e citazione degli assistenti AI se siamo i primi ad aggiornare.

### 2.3 Domanda
- es/mx, es/co, es/ar, es/pe (identica in tutti): "cuanto dinero necesito para entrar a españa" 10 (**2026**, como turista, en efectivo, desde argentina).
- es/co: "cuanto dinero necesito para entrar a" 10 (**españa, europa, italia**, colombia, estados unidos, chile, canada, mexico, panama).
- es/ar: "cuanto dinero hay que llevar a europa" 10 (por 20 días 2026, por día, por un mes).
- es/ve e es/mx: "requisitos para entrar a españa" 10 (desde venezuela 2026, como turista mexicano, como colombiano).
- es/co: "carta de invitacion españa" 10 (para colombianos, precio, cuánto tarda, es obligatoria).
- pt-BR: "quanto dinheiro precisa para entrar na" 10 (**itália, europa, espanha, frança, irlanda**, turquia, suíça); "quanto dinheiro levar para portugal" 7 (por dia); "requisitos para entrar em portugal" 10 (como turista 2026).
- Assicurazione: "seguro de viaje obligatorio para europa" 5; "seguro viagem obrigatório europa" 3.

### 2.4 Prima pagina
"cuánto dinero necesito para entrar a España como turista 2026": parainmigrantes.info, immigrationspain.es, arc-legal, machelindiaz, infoviajera, ineaf, global66 (app di rimesse), **tuvisadoonline con una pagina per Paese di partenza** (Perù, Argentina, Venezuela) e la pagina del Ministero dell'Interno. **Concorrenza media-forte**, ma ognuno parla di un Paese e alcuni sbagliano la cifra (tuvisadoonline scrive sia 121,10 sia 122,10 €). Il nostro vantaggio: tutti i 29 Paesi con la stessa fonte ufficiale e la data, calcolatore in valuta locale, pagine portoghesi per il Brasile (più deboli in prima pagina).

### 2.5 Chi paga
- **IATI** su Tradedoubler: programmi per Colombia, Perù, Portogallo e Spagna; **10 % per vendita convalidata, cookie 7 giorni, in euro** (pagina del programma IATI CO letta il 31/10/2026). Una polizza Europa di 15 giorni costa circa 40-70 €: 4-7 € a vendita (stima).
- AdSense con pubblico latinoamericano: 1-2 € ogni 1.000 visite (stima).
- Wise (10 £ per cliente nuovo) per Brasile e Messico.

### 2.6 Stima
Guadagno ogni 1.000 visite: 4 € prudente (AdSense 1,5 + IATI 2,5), 6 € centrale, 9 € ottimista.
- Prudente: 3.000 × 12 × 4 € / 1.000 ≈ **150 €**
- Centrale: 10.000 × 12 × 6 € / 1.000 ≈ **700 €**
- Ottimista: 30.000 × 12 × 9 € / 1.000 ≈ **3.200 €**

**Ore 10-14** (dati già pronti: testi in due lingue, 29 + 29 pagine, calcolatore, valute, revisione). **Voto 6,5 come sezione:** domanda forte e con l'anno, fonte ufficiale già nostra, costo quasi zero, citabile dagli assistenti AI (lo stesso canale che porta metà delle visite di Visa Income). Non è un sito nuovo: entra nella coda "rete fitta" con una sola pubblicazione serale. **Soglia:** a 45 giorni almeno 300 impressioni al mese sulle pagine `/es/` e `/pt/`, altrimenti nessuna lingua in più.

---

## 3. Passaporto spagnolo × 197 destinazioni (voto 5,5)

**Fatto nuovo:** il 18/10 la fonte rispondeva 503 (ESPLORATE: "Documenti per chi viaggia da spagnolo, RISERVA"). Oggi `exteriores.gob.es` "Recomendaciones de viaje" risponde **200** (1,17 MB) con **197 schede Paese**; provate 12 schede (Thailandia, Stati Uniti, Giappone, Cina, Vietnam, Marocco, Egitto, Regno Unito, Messico, Colombia, Turchia, Capo Verde): **12 su 12 a 200**, 76-139 KB, con la sezione "Documentación y visados" e la data ("Última actualización el 3 de septiembre de 2026" per la Thailandia).

**Domanda (es/es):** "españoles necesitan visa para" 10 (estados unidos, japon, china, canada, cabo verde, mexico, londres, corea del sur, egipto, turquia); "visado para españoles" 10 (tailandia, vietnam, australia, colombia, sri lanka, filipinas); "necesito visado para viajar a" 10; "puedo viajar con dni a" 10 (italia, suiza, albania, colombia, brasil…); "pasaporte o dni para viajar a" 8.

**Prima pagina** ("españoles necesitan visado para Vietnam 2026"): **il Ministero stesso in testa** (scheda e pagina dell'ambasciata), poi tuvisadoonline, evisas.io, visago.dev, legalfournier, agenzie. Concorrenza forte, e chi cerca trova già la risposta ufficiale in spagnolo.

**Licenza: limite serio.** L'aviso legal dice che la licenza "se limita a la descarga de dicho contenido y el uso privado del mismo, siempre que los citados contenidos permanezcan íntegros y se cite la fuente". Si potrebbero usare solo i fatti (visto sì/no, mesi di validità, eVisa) scritti con parole nostre e il link: il verificatore deve decidere se basta.

**Chi paga:** IATI ES (10 %), Heymondo, AdSense Spagna (viaggi 3-5 € ogni 1.000 visite, stima).

**Stima:** 2.000 / 6.000 / 18.000 visite al mese × 12 × 8 / 12 / 16 € ≈ **200 / 900 / 3.500 €**. **Ore 20-30.** **Voto 5,5:** fonte leggibile e domanda grande, ma risponde già l'ente nella stessa lingua, licenza ristretta, e le sezioni passaporto di Before You Fly (UK, Canada, Australia) non hanno ancora numeri buoni. Si riapre con i numeri di fine novembre di Before You Fly.

---

## 4. Tempo di attesa per il visto USA per consolato, in spagnolo e portoghese (voto 5, oggi NO)

**Domanda fortissima per consolato** (angolo nuovo: il 17/10 era stata vista solo la domanda indiana):
- es/es e es/mx: "tiempo de espera visa americana" 10 (colombia, **mexico**, 2026, guatemala, ecuador, costa rica, **guadalajara**, peru, **en españa**);
- es/mx: "cita visa americana" 10 (guadalajara, cdmx, monterrey, merida, renovacion, precio);
- pt-BR: "tempo de espera visto americano" 10 (**são paulo, rio de janeiro, porto alegre, brasília, recife**, hoje).

**Fonte chiusa:** `travel.state.gov` (strumento "Global Visa Wait Times" e database) **403** (muro Akamai); anche `mx.usembassy.gov` e `br.usembassy.gov` **403**. Nessuna copia ufficiale altrove. Non si aggira.

**Chi paga:** solo AdSense America Latina (1-2 €), niente affiliazione adatta.

**Stima se la fonte si leggesse:** 20.000 / 50.000 / 120.000 visite al mese × 12 × 1,2 / 2 / 2,8 € ≈ **300 / 1.200 / 4.000 €**. **Voto 5** condizionato. **Azione a costo zero:** aggiungere l'indirizzo del database dei tempi d'attesa al test da GitHub Actions già previsto per il passaporto americano (ESPLORATE, idee-grandi-2026-10-17). Se risponde 200 da lì, la sezione si fa in 12-18 ore.

---

## 5. Nazionalità spagnola: quanto ci vuole davvero (voto 4,5)

**Fonte ufficiale trovata:** il Ministero della Giustizia pubblica ogni trimestre "Datos estadísticos básicos de nacionalidad". PDF al 30/09/2026 (`mjusticia.gob.es/.../Estadisticas nacionalidad 30-09-2026.pdf`): **200, 419 KB, creato il 21/10/2026**, testo leggibile con `pdftotext`. Contiene domande e concessioni per anno (2026: 210.911 domande, 200.278 concessioni, 20.266 dinieghi) e i **pendenti per anno di domanda** (243.206 in tutto: 188.520 del 2026, 40.812 del 2025, 6.720 del 2024, 4.029 del 2023…), più i dati sefarditi per Paese.

**Domanda (es/es):** "cuanto tarda la nacionalidad española" 10 (por residencia, 2026, por matrimonio, por vía telemática, por opción, ley de memoria democrática); "nacionalidad española por residencia" 10 (consulta, estado, "como va lo mio"); "tiempo resolucion nacionalidad" 3.

**Prima pagina:** machelindiaz e arc-legal commentano già ogni PDF trimestrale (31/3 e 30/6/2026), giornali (elderecho). Il dato è **uno solo, nazionale**, ogni tre mesi: niente pagine per città o per ufficio.

**Chi paga:** AdSense Spagna con pubblico immigrato (2-3 €). **Stima** 100 / 400 / 1.200 €. **Ore 5-8. Voto 4,5:** una pagina utile dentro una futura sezione spagnola (per esempio accanto alla n. 2 o alla n. 1 per il CCSE), non di più.

---

## 6. Le idee chiuse (NO, con le prove)

### 6.1 Passaporti di Messico, Brasile, Colombia, Argentina × destinazioni (3,5)
- Domanda ottima: "mexicanos necesitan visa para" 10, "paises sin visa para mexicanos" 9 (2026), "colombianos necesitan visa para" 10, "argentinos necesitan visa para" 10, "peruanos necesitan visa para" 10, "brasileiro precisa de visto para" 10 (portugal, mexico, espanha, canada, japão), "requisitos para viajar a" (es/co) 10.
- **Fonti chiuse dal server:** Messico `guiadelviajero.sre.gob.mx` **000** (il proxy risponde 502); Brasile `gov.br/mre/...portal-consular/vistos` **200 ma è la pagina di blocco "Acesso Temporariamente Interrompido"** (anti-robot: non si aggira); Colombia `cancilleria.gov.co` **403**; Argentina `cancilleria.gob.ar`: home 200, pagine visti 404 (indirizzo non trovato in questo giro). Senza fonte ufficiale per passaporto la sezione sarebbe una copia di Wikipedia e dei giornali (Expansión, La Razón).

### 6.2 Portogallo: tempi della nazionalità e di AIMA (3)
- Domanda: "nacionalidade portuguesa tempo de espera" (pt-BR, 10 con "por casamento", "netos"), "processo nacionalidade portuguesa" 10 ("parado", "consulta", "demorando"), "aima renovação" 10; ma "tempo de espera aima" solo 1.
- Fonti: `irn.justica.gov.pt` 200 (procedure, nessun tempo per ufficio); `dados.gov.pt` (API 200): per la nazionalità solo serie annuali INE (acquisizioni per anno, aggiornate il 28/9/2026), nessun pendente né tempo; **AIMA 000** (come il 31/10 mattina). La nuova legge (LO 1/2026) resta RISERVA con evento (ESPLORATE).

### 6.3 Argentina nel Visa Waiver Program (3)
- Domanda: "visa waiver argentina" 10 (2026, 2027, "cuando empieza", "progreso", "noticias"); "esta argentinos" non c'è (escono le partite dell'Argentinos Juniors).
- Fatto: dichiarazione d'intenti firmata il 28/7/2025; **nessuna data ufficiale** a ottobre 2026; notizie di pause nelle trattative. È una notizia, non un dato che si aggiorna. Se un giorno arriverà la data, basterà una pagina in Before You Fly (spagnolo) sull'ESTA.

### 6.4 Cita previa extranjería, huellas TIE, NIE (NO confermato)
- Domanda sempre fortissima: "cita previa extranjeria" 10 (toma de huellas, zaragoza, las palmas, bilbao, malaga…), "cita huella tie" 10 (madrid, barcelona, alicante, renovacion), "estado expediente extranjeria" 10 (mercurio, regularizacion, madrid, valencia, murcia, barcelona).
- Nessun fatto nuovo: `icp.administracionelectronica.gob.es` **000**, `sede.administracionespublicas.gob.es` **503**, `inclusion.gob.es` ed `extranjeros.inclusion.gob.es` **403**. Nessun dato ufficiale di disponibilità o di tempi per ufficio. Leggere le cite con un robot è ciò che la Polizia persegue (studio 16). Resta NO.

### 6.5 Passaporto brasiliano (NO)
- Domanda: "agendamento passaporte" 10 (polícia federal, rj, porto alegre, bh, df, curitiba, sc); "taxa passaporte 2026" 8 ("vai aumentar", "gru").
- `gov.br/pf/pt-br/assuntos/passaporte` ha risposto 200 a un primo controllo (150 KB), ma lo stesso dominio `gov.br` serve la pagina di blocco agli accessi automatici; `servicos.dpf.gov.br/agenda-web` 404. Nessun dato di disponibilità pubblico; la tassa è una sola cifra (giornali). Stesso verdetto del passaporto messicano (5, il 30/10).

---

## 7. Cosa ho imparato in questo angolo

1. **In America Latina i portali ufficiali dei ministeri degli Esteri sono chiusi ai robot** (Brasile con pagina di blocco, Colombia 403, Messico che non risponde). Il pubblico è enorme ma le fonti per passaporto non si leggono, e la pubblicità vale 1-2 € ogni 1.000 visite.
2. **Dove abbiamo già la fonte (tabella UE degli importi), la traduzione verso questi pubblici costa poco**: è il modo più rapido per prendere la domanda latinoamericana. Vale anche per altre sezioni di Visa Income con fonte UE (rifiuti dei visti per Paese: già bocciati in spagnolo il 21/10 per domanda scarsa; da non rifare).
3. **Spagna e Portogallo:** la burocrazia più cercata (cita previa, AIMA, estado del expediente) non ha dati pubblici per ufficio. I dati ufficiali che esistono sono nazionali e trimestrali (nazionalità spagnola) e li commentano già gli studi legali.
4. **Il Cervantes sta cambiando sito**: per qualche mese manca il cercatore ufficiale dei centri DELE. È l'unica finestra vera trovata oggi; il test della sez. 1.6 dice se si riesce a riempirla prima che chiuda.

---

## 8. Fonti principali (lette il 31/10/2026)

- Instituto Cervantes, "Información para las convocatorias DELE y CCSE 2027": https://cervantes.org/es/examenes/dele (200)
- Instituto Cervantes, CCSE: https://cervantes.org/es/examenes/ccse (200)
- Instituto Cervantes, Memoria 2024-2025 "en cifras": https://cervantes.org/sites/public/produccion/files/2025-12/memoria-2024-2025-instituto-cervantes-02-cifras-ic.pdf (200)
- Instituto Cervantes Los Angeles, DELE: https://cervantes.org/us/los-angeles/en/learning-teaching/certification/dele (200)
- Instituto Cervantes Nueva Delhi, DELE dates and fees: https://nuevadelhi.cervantes.es/en/DELE_ingles/DELE_dates_and_fees.htm (200)
- Ministerio de Justicia, Estadísticas nacionalidad 30/09/2026: https://www.mjusticia.gob.es/es/Ciudadano/Nacionalidad/Documents/Estadisticas%20nacionalidad%2030-09-2026.pdf (200)
- Ministerio de Asuntos Exteriores, Recomendaciones de viaje: https://www.exteriores.gob.es/es/ServiciosAlCiudadano/Paginas/Recomendaciones-de-viaje.aspx (200) e Aviso legal https://www.exteriores.gob.es/es/Paginas/AvisoLegal.aspx
- Commissione europea, importi di riferimento per le frontiere (PDF dell'8/6/2026), già in `visaincome/dati/schengen_residenti.json`
- IATI CO su Tradedoubler: https://directory.tradedoubler.com/en/programs/403047-IATI-CO (10 %, cookie 7 giorni)
- Fonti chiuse: travel.state.gov 403; mx.usembassy.gov e br.usembassy.gov 403; guiadelviajero.sre.gob.mx 000; gov.br (pagina di blocco); cancilleria.gov.co 403; interior.gob.es 403; inclusion.gob.es 403; icp.administracionelectronica.gob.es 000; aima.gov.pt 000
- Prima pagina: ricerche web dagli USA del 31/10/2026 (parainmigrantes.info, immigrationspain.es, arc-legal.es, machelindiaz.com, tuvisadoonline.com, fedele.org, aporeldele.com, spainexchange.com, gogoespana.com, expansion.mx)

## 9. Righe proposte per ESPLORATE (da copiare chi aggiorna il file; questo ricercatore non lo modifica)

| Nicchia | Esito | Studio |
|---|---|---|
| Esami di spagnolo nel mondo (DELE, SIELE, CCSE): centri e prezzi per città, en/es/pt | RISERVA alta (6,5; 600 / 2.600 / 9.600 €): cercatore ufficiale dei centri sparito con la nuova web del Cervantes; centri istituto per istituto (71 siti); test di 6 ore in sez. 1.6 | wf-2026-10-31-spagna-portogallo-latam |
| "Cuánto dinero necesito para entrar a España/Europa" (es) e "quanto dinheiro para entrar na Europa" (pt) | **SEZIONE da costruire** in Visa Income (6,5; 150 / 700 / 3.200 €; 10-14 ore; dati UE già nostri; IATI 10 %) | wf-2026-10-31-spagna-portogallo-latam |
| Passaporto spagnolo × 197 destinazioni (exteriores.gob.es) | RISERVA (5,5): fonte ora 200 (era 503), ma licenza "uso privado" e l'ente risponde già; dopo i numeri di Before You Fly | wf-2026-10-31-spagna-portogallo-latam |
| Tempi d'attesa del visto USA per consolato in es/pt | NO oggi (5 condizionato): travel.state.gov 403; nel test da GitHub Actions | wf-2026-10-31-spagna-portogallo-latam |
| Nazionalità spagnola, tempi (PDF trimestrale del Ministero) | NO come sezione a sé (4,5): un dato nazionale, già commentato dagli studi legali | wf-2026-10-31-spagna-portogallo-latam |
| Passaporti messicano, brasiliano, colombiano, argentino × destinazioni; tempi nazionalità portoghese/AIMA; Visa Waiver Argentina; passaporto brasiliano | NO (3-3,5): fonti chiuse o senza dati, evento senza data | wf-2026-10-31-spagna-portogallo-latam |
