# I grandi mercati non in inglese: spagnolo, portoghese, francese, arabo, urdu/hindi (31/10/2026)

Angolo di questo giro: passaggi obbligatori (o quasi) in mercati grandi che non parlano inglese, con date, sedi o risultati ufficiali per città o Paese, domanda vera e qualcuno che paga. Modello di riferimento: EsameB1.

**Letto prima:** skill `rete-siti`, `REGOLE-FISSE.md`, ESPLORATE per intero (anche le righe aggiunte oggi da altri ricercatori), `ricerca-cloni-esameb1-2026-10-30.md`, `de-test/ESITO.md`.

**La lezione della Germania, applicata qui.** Il test tedesco è caduto perché le date stavano **sede per sede** (85 Prüfstellen, 85 siti diversi, solo 31 leggibili) e non in una fonte unica. In questo giro un'idea passa il filtro delle fonti solo se le date le fissa **un ente per regione o per Paese, in un documento unico**, non ogni sede per conto suo. Dove la data la assegna l'ufficio (Fachsprachprüfung, Ley de nietos) o la decide ogni scuola (Murcia), l'ho scritto e ho abbassato il voto.

**Metodo:** autocomplete di Google (`client=firefox`) con hl/gl della lingua e del Paese, letto il 31/10/2026; prima pagina con ricerca web dagli USA (non è il Google del Paese, lo segnalo dove conta); fonti con `curl` dal nostro server il 31/10/2026, con stato HTTP e dimensione. Stime: lordo annuo a 18 mesi dalla pubblicazione, 1 $ ≈ 0,9 €, formula del 30/10 (visite al mese × 12 × guadagno ogni 1.000 visite). Script e file scaricati sono rimasti nella cartella temporanea della sessione: nel repository c'è solo questo file.

---

## 0. Risposta in breve

**Una sola idea arriva a 7, e non passa l'asticella dei siti nuovi** (stima centrale sotto i 5.000 €/anno). Nessuna idea di questo giro è da proporre a Massimiliano come sito nuovo.

| # | Idea | Lingua, Paese | Chi paga | €/anno a 18 mesi (prudente / centrale / ottimista) | Ore | Voto |
|---|---|---|---|---|---|---|
| 1 | **Esami EOI (pruebas de certificación) per comunità e per scuola**: date per lingua e livello, iscrizioni, tasse, uscita delle "notas" | spagnolo, Spagna | italki, Preply, Amazon.es, AdSense ES; dopo il cancello fiscale contatti per le accademie | 650 / 2.800 / 9.700 (**~18.700 con la fase 2**) | 40-55 | **7** |
| 2 | **Dopo la regolarizzazione 2026: rinnovo 2027 e "cursos válidos" per l'arraigo socioformativo, città per città** | spagnolo, Spagna | AdSense ES, Wise e app di rimesse; dopo il cancello fiscale contatti per i centri di formazione | 240 / 1.100 / 5.400 (**~17.400 con la fase 2**) | 35-45 | 6 |
| 3 | Francia: nuovi livelli di lingua 2026 (A2/B1/B2), TCF/TEF IRN; TCF Québec per città | francese, Francia e Québec | italki francese, Amazon.fr, AdSense | (riserva del 30/10, nessun fatto nuovo sulle fonti) | – | 6 (invariato) |
| 4 | Portogallo: nuova legge sulla nazionalità (LO 1/2026, in vigore dal 19/5/2026) e test di conoscenza | portoghese, Portogallo e Brasile | AdSense PT/BR, italki | 300 / 1.500 / 4.000 *solo se il test avrà sedi e date* | 20-30 | 5,5 (riserva con evento) |
| 5 | Arabia Saudita, Skill Verification Program (SVP): centri d'esame per città in India, Pakistan, Bangladesh | inglese, urdu, hindi | quasi nessuno (AdSense India/Pakistan) | 50 / 240 / 860 | 15-20 | 5 |
| 6 | Hajj 2027: prezzi ufficiali per Paese e per città d'imbarco | inglese, urdu, indonesiano | AdSense (basso tranne UK/USA), hotel e assicurazioni da verificare | 150 / 600 / 2.500 | 20-30 | 5 |
| 7 | Fachsprachprüfung dei medici stranieri per Ärztekammer (angolo tedesco diverso) | tedesco, arabo | corsi di tedesco medico, AdSense DE | 150 / 600 / 2.000 | 15-20 | 5 |
| 8 | Ley de nietos: a che punto è ogni consolato | spagnolo, Argentina, Cuba, Messico | AdSense America Latina | 100 / 430 / 1.900 | 15-20 | 4,5 |
| 9 | Décrets de naturalisation: calendario dal Journal officiel | francese, Francia | AdSense FR | 100 / 400 / 1.500 | 8-12 | 4 |
| 10 | Traductores jurados ufficiali per lingua e provincia | spagnolo, Spagna | AdSense ES; contatti ai traduttori (vendita diretta) | 200 / 700 / 2.000 | 10-15 | 4 |
| 11 | USA ispanici: licencia de manejo sin papeles ed examen de manejo en español per Stato | spagnolo, USA | AdSense USA, assicurazioni auto | 150 / 600 / 2.500 | 25-35 | 3,5 |

**Le due con potenziale ≥ 10.000 €/anno** sono la 1 e la 2, ma **solo con la fase 2** (contatti venduti ad accademie e centri di formazione), cioè dopo il cancello fiscale (STRATEGIA sez. 10). Con i soli AdSense e affiliazioni nessuna delle due arriva a 10.000 nemmeno nel caso ottimista. Lo scrivo chiaro perché la regola chiede numeri, non speranze.

**Prova tecnica sulla migliore (EOI):** le date si leggono in automatico **dove la comunità pubblica un calendario unico**: Madrid 29 date su 29 (BOCM, dopo aver tolto dei caratteri di controllo; 27 su 29 senza), Paesi Baschi 32 su 32 per il 2026 e 32 su 32 per il 2027 (già pubblicato). Valencia è leggibile ma a griglia (serve un lettore su misura), le Canarie danno le finestre in una pagina HTML, **Murcia lascia le date a ogni scuola** (stesso difetto della Germania). Andalucia e Catalogna non le ho trovate in tempo. Dettagli in sez. 2.

**Cosa propongo:** niente sito nuovo oggi. La EOI resta **RISERVA alta**: si riprende con un secondo test (le 17 comunità, soglia scritta in sez. 2.5) quando ci sarà un posto libero, e prima dell'ondata delle iscrizioni (febbraio-aprile 2027).

---

## 1. Perché in questi mercati il modello rende meno

Tre cose, viste in quasi tutte le idee:

1. **Chi paga vale poco quando il pubblico parla già la lingua.** italki è il pagatore migliore di EsameB1 perché chi fa il B1 deve imparare l'italiano. Un argentino per la Ley de nietos, un marocchino per il titre de séjour, un brasiliano per la nazionalità portoghese parlano già la lingua dell'esame o non ne hanno bisogno. Resta AdSense, che in America Latina, India e Pakistan vale 0,3-1,5 € ogni 1.000 visite.
2. **Dove il pubblico vale (Spagna, Francia, Germania), le fonti sono chiuse o sparse.** In Francia CCIP vieta la riproduzione e FEI ha l'anti-robot (30/10); `inclusion.gob.es` (Ministero spagnolo dell'immigrazione) risponde **403**, `sede.inclusion.gob.es` non risponde.
3. **La data la assegna l'ufficio** in molti passaggi grandi (Ley de nietos, Fachsprachprüfung, cita previa, Skill Verification): la gente non sceglie sede e giorno, quindi la pagina "date per città" non serve.

L'unica eccezione trovata è proprio l'**EOI spagnola**: pubblico spagnolo (pubblicità che vale), esame che si prepara (italki e Preply servono davvero: si studia inglese, francese, tedesco), date fissate da **un documento per comunità**.

---

## 2. Idea 1: esami EOI, pruebas de certificación (voto 7)

### 2.1 Cosa sarebbe
Un sito in spagnolo "Exámenes EOI 2027: fechas, inscripción, tasas y notas en tu comunidad y en tu escuela":
- una pagina per comunità autonoma (17) con il calendario degli scritti per lingua e livello (A2-C2), le finestre di iscrizione per i "libres", la convocatoria straordinaria di settembre;
- una pagina per scuola (circa 300 EOI ed extensiones: "puc eoi elche", "notas eoi valencia") con la data delle prove e il giorno in cui escono le notas;
- tasse per comunità ("tasas eoi madrid/coruña/zaragoza/salamanca/andalucia/murcia");
- avvisami: "si apre l'iscrizione", "escono le notas";
- la prova C1 di inglese di Madrid di febbraio (iscrizione a dicembre): prima ondata utile, tra un mese.

È un passaggio quasi obbligatorio: il B1 serve per laurearsi in molte università, B2 e C1 per i docenti dei programmi bilingui e per molti concorsi. Gli alunni EOI erano **335.414** nel 2024-25 (Ministerio de Educación, "Datos y cifras" 2025-26), più i candidati "libres" che non sono iscritti ai corsi. È circa 3 volte il pubblico di EsameB1.

### 2.2 Domanda (es/es, 31/10/2026)
- "eoi inscripción" → 2026 2027, 2027, examen, valencia, examen libre, septiembre, alicante (10)
- "pruebas certificación eoi" → canarias, madrid, castilla la mancha, 2026, valencia, asturias, comunidad valenciana (10)
- "notas eoi" → valencia, salamanca, elche, sagunto, gandia, extraordinaria, torrelavega, burgos (10): **per scuola**, come i "risultati" di EsameB1
- "puc eoi" → castellon, gva, quatre carreres, elche, benicalap, alicante, sagunt, saidia (10)
- "calendario examenes eoi" → 2026, getxo, bilbao, barakaldo, guadalajara, granada, vitoria, coruña (10)
- "tasas eoi" → gva, 2026, madrid, coruña, zaragoza, salamanca, andalucia, gijon, murcia (10)
- "examen eoi libre" → 2026, ingles, madrid, zaragoza, c1, guadalajara, valencia, coruña (10)
- "eoi c1 ingles" → examenes, online, speaking, modelo examen, madrid, libre, precio, valencia (10)
- "pec andalucia" 5; "fecha examen eoi" 5 (2026, c1 ingles, b2 ingles)

Domanda per città e per scuola ricca quanto quella di EsameB1, con le tre cose che contano lì: **date, risultati, costo**.

### 2.3 Composizione della prima pagina
Ricerca "pruebas de certificación EOI 2027 fechas inscripción Madrid" (dagli USA): pagine ufficiali della Comunidad de Madrid, PDF del BOCM, PDF di singole EOI (Rivas, Torrent, Xàtiva), Canarie, Euskadi, un sindacato (CSIF), un giornale (Valencia Plaza), un documento Google. **Nessuna pagina che metta insieme le comunità e le scuole.** Sotto i nomi delle scuole ci sono i siti delle scuole stesse. Il buco è reale; da confermare sul Google spagnolo (gl=es) prima di costruire.

### 2.4 Chi paga
- **italki** (18 $ per studente nuovo, link già attivo su EsameB1) e **Preply**: chi prepara un B2 o un C1 di inglese o di francese è il cliente giusto per un insegnante;
- **Amazon.es**: libri di preparazione EOI e Cambridge;
- **AdSense** con pubblico spagnolo e tema istruzione (3-5 € ogni 1.000 visite, stima);
- **fase 2, dopo il cancello fiscale**: contatti per le accademie di inglese (il mercato spagnolo della preparazione B2/C1 è grande), come previsto per EsameB1.

### 2.5 Prova tecnica minima: le date si leggono in automatico?
Scaricati i documenti ufficiali dal nostro server il 31/10/2026, convertiti in testo (`pdftotext -layout`), lette le date con due lettori semplici (uno per la tabella di Madrid, uno per quella basca).

| Comunità (abitanti, circa) | Documento | HTTP | Risultato |
|---|---|---|---|
| Madrid (7,0 M) | BOCM 25/3/2026, Anexo I | 200, 150 KB, PDF | **29 date su 29** (lingua × livello × giorno × ora 15:45). Al primo giro 27: due righe avevano caratteri di controllo nel PDF; tolti quelli, 29. Finestre di iscrizione (7-21/4), liste provvisorie (28/4) e matricola (7-20/5) in prosa, leggibili con regole semplici |
| Paesi Baschi (2,2 M) | Calendario 2025-26 e **Anexo II 2026-27 (già pubblicato)** | 200, 138 e 265 KB | **32 su 32** per anno, 8 lingue × 4 livelli. Controllo a mano su 6 righe del 2027 (inglese B2 14/5, C1 18/5, A2 e B1 20/5; euskara C1 17/5; russo C1 8/6): tutte giuste |
| Valencia (5,3 M) | Calendario PUC straordinaria 2026 (sito ufficiale di una EOI su `portal.edu.gva.es`) | 200, 207 KB | Leggibile, ma è **una griglia** (giorni in colonna, lingue e livelli nelle celle): il lettore semplice trova 0 date. Serve un lettore su misura (3-4 ore). Il calendario ordinario (sito di un'altra EOI) non risponde dal server (000) |
| Canarie (2,3 M) | Pagina ufficiale del Gobierno de Canarias | 200, 93 KB, HTML | Finestre di iscrizione, liste, convocatoria ordinaria (29/5-18/6/2026) e straordinaria (2-10/9/2026) in testo; 16 righe con date |
| Murcia (1,6 M) | BORM 2026 n. 181 | 200, 424 KB | **Le date le pubblica ogni scuola** "no más tarde del 11 de mayo": **stesso difetto della Germania** |
| Andalucia (8,6 M) | BOJA 17/11/2025 | 200, 308 KB | Documento sbagliato (corsi di spagnolo quadrimestrali). La convocatoria principale 2026 non l'ho trovata in tempo; il BOJA risponde |
| Catalogna (8,1 M), Galizia, Castiglia e León, Aragona, altre 7 | – | – | Non cercate in questo giro |

**Esito:** dove esiste il calendario unico, **le date si leggono in automatico e sono giuste** (61 su 61 nei controlli). Comunità con calendario unico leggibile: 4 su 7 controllate (Madrid, Paesi Baschi, Valencia, Canarie), circa il 34 % degli abitanti. Una (Murcia) delega alle scuole. Andalucia e Catalogna (un terzo della Spagna) restano da vedere.

**Differenza dalla Germania:** lì servivano 85 lettori di 85 siti; qui 17 documenti, uno per comunità, con tabelle quasi uguali ogni anno. Il rischio è più piccolo, ma non è zero.

**Soglia per salire a 8 (secondo test, circa 6 ore):** almeno **12 comunità su 17**, con almeno l'**80 % degli abitanti**, hanno un calendario unico leggibile dal server; data giusta in almeno 28 controlli a mano su 30; Andalucia e Catalogna devono esserci entrambe.

### 2.6 Stima
Riferimento EsameB1 a 18 mesi: 3.000-10.000 visite al mese. Pubblico EOI circa 3 volte, ma più sparso tra lingue e livelli e con le scuole che hanno già le loro pagine. Guadagno ogni 1.000 visite: 9 € prudente (AdSense 3 + italki/Preply 5 + Amazon 1), 13 € centrale, 18 € ottimista.
- **Prudente:** 6.000 visite × 12 × 9 € / 1.000 ≈ **650 €**
- **Centrale:** 18.000 × 12 × 13 € / 1.000 ≈ **2.800 €**
- **Ottimista:** 45.000 × 12 × 18 € / 1.000 ≈ **9.700 €**
- **Fase 2, dopo il cancello fiscale (ottimista):** 50 contatti al mese per le accademie × 15 € × 12 ≈ +9.000 € → **circa 18.700 €**

Prime entrate: italki al 2°-3° mese dalla pubblicazione; picchi da febbraio ad aprile (iscrizioni), da maggio a luglio (esami e notas), settembre (straordinaria), dicembre (C1 di Madrid).

### 2.7 Ore e voto
**Ore 40-55**: 17 lettori di calendari (tabelle simili, 1-2 ore ciascuno), pagine per scuola (circa 300, dall'elenco ufficiale dei centri), tasse per comunità, notas, avvisami; riuso di `esameb1/genera.py`; revisione indipendente 3 ore.

**Voto 7.** Domanda per scuola e per città forte, fonti per comunità leggibili dove esistono, buco reale, pagatore che c'entra. Non sale a 8: copertura delle fonti provata solo per un terzo della Spagna, pagatore medio (non una commissione alta), stima centrale **sotto i 5.000 €**: **non passa l'asticella dei siti nuovi**. Sopra i 5.000 € solo nel caso ottimista o con la fase 2.

---

## 3. Idea 2: dopo la regolarizzazione 2026 (voto 6)

**Il fatto nuovo.** Il Real Decreto 316/2026 (BOE 15/4/2026) ha aperto la regolarizzazione straordinaria dal 16/4 al 30/6/2026: **oltre 1,17 milioni di domande** (cifra riportata da ARC Legal il 10/7/2026 e da Priego Digital, con 609.737 pratiche già lavorate secondo il Ministero di Inclusione; dato ufficiale non letto dal server). Il permesso dura **un anno**, poi si rinnova o si passa ai permessi ordinari: tra la primavera e l'estate 2027 arriva un'ondata di rinnovi. Intanto il nuovo regolamento (RD 1155/2024) ha creato l'**arraigo socioformativo**, che richiede l'iscrizione a un corso valido.

**Cosa sarebbe.** Pagine "cursos válidos para el arraigo socioformativo en [ciudad]" con i centri autorizzati e le finestre di iscrizione all'FP per adulti di ogni comunità; più "renovación de la regularización 2027: requisitos y plazos".

**Domanda (es/es):**
- "cursos arraigo socioformativo" → madrid, barcelona, sepe, valencia, malaga, sevilla, alicante, gratis, granada (10): **per città**;
- "arraigo socioformativo cursos" → validos, madrid, sepe, gratis (10);
- "regularización extraordinaria" → 2026 boe, cita previa, formulario, consultar expediente, consultar estado, como va mi solicitud (10);
- "regularización extraordinaria madrid" e "… barcelona" → entidades colaboradoras, informe de vulnerabilidad, cita (5 ciascuna);
- "tiempo de resolucion arraigo" solo 2; "regularización extraordinaria resolución" 2.

**Fonti:**
- BOE (API dati aperti) 200: testo del RD 316/2026 e del regolamento;
- FAQ ufficiali sul sito della Moncloa (PDF del 16/4/2026), 200;
- `todofp.es` 200; Registro statale dei centri (`educacion.gob.es/centros`) 200 al primo tentativo, vuoto al secondo: **instabile**;
- **`inclusion.gob.es` 403, `sede.inclusion.gob.es` non risponde**: il Ministero che decide non si legge dal server;
- i corsi validi non sono in un elenco ufficiale unico: FP di grado medio, certificati di professionalità, offerta SEPE per le occupazioni difficili da coprire, ognuno con la sua fonte e con 17 calendari di ammissione regionali. Le stesse fonti di settore non sono d'accordo su cosa valga (online sì o no, livelli dei certificati).

**Prima pagina** ("cursos arraigo socioformativo Valencia válidos centros"): immigrationspain.es, grupo2000.es (decine di pagine "centros válidos", "dónde estudiar"), cursosfemxa.es (vende i corsi), cohenyaguirre.es, studi legali. **Concorrenza forte e commerciale**: chi vende i corsi fa già le pagine.

**Chi paga:** AdSense con pubblico immigrato in Spagna (2-4 € ogni 1.000 visite, stima); Wise (10 £) e app di rimesse (commissioni da leggere); **fase 2**: contatti ai centri di formazione (un corso costa 1.000-2.500 €, un contatto può valere 20-30 €), solo dopo il cancello fiscale.

**Stima:** guadagno ogni 1.000 visite 4 / 6 / 9 €.
- Prudente 5.000 × 12 × 4 € / 1.000 ≈ **240 €**; centrale 15.000 × 12 × 6 € ≈ **1.100 €**; ottimista 50.000 × 12 × 9 € ≈ **5.400 €**;
- fase 2 (ottimista): 40 contatti al mese × 25 € × 12 ≈ +12.000 € → **circa 17.400 €**.

**Ore 35-45. Voto 6:** pubblico enorme e un'ondata con una data, ma niente dato ufficiale per città da dare che i concorrenti non diano già, Ministero chiuso dal server, regole contese. Si riapre se il Ministero pubblica un elenco ufficiale dei corsi validi o i dati dei rinnovi per provincia.

---

## 4. Le altre idee

### 4.1 Francia e Québec: livelli di lingua 2026, TCF/TEF IRN, TCF Québec (6, riserva invariata)
- **Domanda** (fr/fr): "carte de résident b1" 10 (a2 ou b1, 10 ans, test, formation, delf); "naturalisation b2" 10 (2026, b2 ou b1, marseille, tcf); "tcf irn" 10 (lyon, paris, exemple 2026). fr/ca: "tcf québec" 10 (rendez-vous trois-rivières, montréal, drummondville, inscription en ligne).
- **Fonti:** nessun fatto nuovo. CCIP (TEF) vieta la riproduzione, FEI (TCF) ha l'anti-robot (letto il 30/10). Il dataset dei centri su data.gouv.fr: l'API ha risposto 200 una volta (48 KB), poi il collegamento si è chiuso a metà e il nome non si risolve più da questa sessione. Chi lo pubblica e con quale licenza resta da leggere.
- **Voto 6, come il 30/10.** Si riapre solo con il permesso scritto di CCIP o FEI.

### 4.2 Portogallo: nuova legge sulla nazionalità e test di conoscenza (5,5, riserva con evento)
- **Fatto nuovo:** la Lei Orgânica 1/2026 è in vigore dal 19/5/2026 (eco.sapo.pt, Sovereign Group, notizie brasiliane). Chiede di conoscere lingua, storia, cultura e organizzazione dello Stato "por meio de teste ou certificado". Il regolamento del test non c'è ancora: le fonti non sono d'accordo su quando arriva.
- **Domanda:** "nova lei da nacionalidade" 10 (o que muda, casamento, pode afetar brasileiros, quando entra em vigor); "nacionalidade portuguesa" 10 (consulta processo, para brasileiros); ma "teste de nacionalidade portuguesa" solo 3 e "prova de conhecimento…" 0. Il test oggi non si cerca, perché non esiste ancora.
- **Fonti:** IRN 200 (282 KB), Diário da República 200 ma pagina vuota da 2 KB (JavaScript), **AIMA non risponde** (000), CAPLE 200 (il CIPLE resta NO dal 24/10).
- **Voto 5,5.** Diventa interessante solo se il regolamento crea un test **con sedi e date scelte dal candidato** (come l'examen civique). Da ricontrollare quando esce il regolamento.

### 4.3 Arabia Saudita, Skill Verification Program: centri d'esame per città (5)
- **Domanda forte, per città** (en/in, en/pk, ur/pk): "svp test centre" → in india, kerala, chennai, hyderabad, tamilnadu, patna bihar, madurai, lucknow, delhi (10); "svp exam centre in" → mumbai, bangalore, kolkata (10); "takamol test centre" → india, pakistan, lahore (9); "saudi skill verification program india fees" (10). Dal luglio 2026 il certificato serve al momento della domanda del visto (Ekantipur 22/7/2026); il Nepal ha chiuso il suo centro e l'Arabia ha fermato i visti (Kathmandu Post 30/7/2026).
- **Fonte: ottima.** Il sito è passato a `svp-international.qiwa.sa`; il suo **API pubblico** (`svp-international-api.pacc.sa/api/v1/visitor_space/test_centers`) dà **280 centri** con città e indirizzo, senza login: India 58, Pakistan 53, Bangladesh 24, USA 16, Cina 11, Egitto 10. Anche le 297 occupazioni sono pubbliche. **Le date per centro non lo sono** (`activity_dates` 404 senza login). Le condizioni d'uso del portale non sono ancora lette.
- **Prima pagina:** NAVTTC (PDF), Gulf News, Wego, ARY News, edoxi; una guida dice ancora "solo New Delhi e Mumbai". Nessun elenco per città aggiornato: **il buco c'è**.
- **Chi paga: quasi nessuno.** AdSense India e Pakistan vale 0,3-0,8 € ogni 1.000 visite; chi fa l'esame non ha ancora uno stipendio saudita per le rimesse.
- **Stima:** 8.000 × 12 × 0,5 € ≈ **50 €**; 25.000 × 12 × 0,8 € ≈ **240 €**; 60.000 × 12 × 1,2 € ≈ **860 €**. **Ore 15-20. Voto 5:** fonte e domanda da 8, pagatore da 2. Utile solo come pagina dentro un sito con pubblico del Golfo, se un giorno ci sarà.

### 4.4 Hajj 2027: prezzi ufficiali per Paese e città d'imbarco (5)
- **Domanda:** en/in "haj 2027" 10 (last date, waiting list, price in india government, selection list); en/pk "hajj 2027" 10 (government package, payment schedule, price in pakistan); en/gb "hajj 2027 price" 10 (india, pakistan, nigeria, uk, ghana); "nusuk hajj 2027" 10 (uk, usa, south africa, france); "nusuk hajj packages" 10.
- **Fonti:** Haj Committee of India 200 (circolari Haj 2027 in HTML e PDF), Ministero pakistano degli Affari religiosi 200, Nusuk Hajj 200 (robots aperto, elenco Paesi e fornitori pubblici), ma **i prezzi dei pacchetti Nusuk sono dietro login**.
- **Prima pagina:** i giornali di ogni Paese danno il prezzo il giorno dell'annuncio (Times of India, Dawn, Premium Times); per UK e USA agenzie e forum.
- **Chi paga:** AdSense, alto solo per UK e USA; hotel alla Mecca e assicurazioni da verificare.
- **Stima** 150 / 600 / 2.500 €. **Ore 20-30. Voto 5:** una cifra all'anno per Paese, la danno già i giornali.

### 4.5 Fachsprachprüfung dei medici stranieri per Ärztekammer (5): l'angolo tedesco diverso
- **Domanda** (de/de): "fachsprachprüfung ärztekammer" 9 (nordrhein, berlin, niedersachsen, baden württemberg, westfalen-lippe); "fsp prüfung" 10 (beispiel, medizin, vorbereitung, termine, zahnmedizin); "fachsprachprüfung termine" 5 (düsseldorf, münster); "kenntnisprüfung wartezeit" 2. In arabo (ar/de) "امتحان اللغة الطبية في المانيا" 4.
- **Fonti:** 17 Ärztekammern, siti raggiungibili (Nordrhein, Baviera, Berlino, Westfalia-Lippe: 200). **Ma la data la assegna la Kammer** dopo il pagamento (Nordrhein: 430 €, "wird dem Antragsteller ein Prüfungstermin zugeordnet"). Il modello non vale: si può confrontare solo costi e procedure per Land.
- **Chi paga:** corsi di tedesco medico (cari, ma senza affiliazioni note), AdSense DE.
- **Stima** 150 / 600 / 2.000 €. **Ore 15-20. Voto 5.**

### 4.6 Ley de nietos: a che punto è ogni consolato (4,5)
- **Domanda** (es/ar, es/mx, es/us): "ley de nietos consulado" 10 (buenos aires, rosario, cordoba, bahia blanca, mendoza, miami); "ley de nietos turnos" 5; "ley de nietos demora" 4 (miami); "ley de nietos estado" 6.
- **Fonti:** `exteriores.gob.es` oggi risponde (era 503 il 18/10). Dati nazionali ufficiali al 31/5/2026: 1.225.188 domande presentate, 571.761 accolte, 1.389.194 richieste di appuntamento ancora da esaminare. **Solo Buenos Aires** pubblica ogni mese a che punto è, nel bollettino PDF (letto: agosto, settembre e ottobre 2026 dicono tutti "expedientes recibidos… en septiembre de 2023"; il PDF si legge con `pdftotext`). Per Rosario, Córdoba, L'Avana e Messico la ricerca non ha trovato aggiornamenti: **la stessa "risposta a metà" della Germania**.
- **Prima pagina:** Cronista, BAE Negocios, Infobae, gruppi Facebook, studi legali.
- **Chi paga:** AdSense Argentina e Cuba (0,5-2 € ogni 1.000 visite).
- **Stima:** 10.000 × 12 × 0,8 € ≈ **100 €**; 30.000 × 12 × 1,2 € ≈ **430 €**; 80.000 × 12 × 2 € ≈ **1.900 €**. **Voto 4,5.**

### 4.7 Décrets de naturalisation dal Journal officiel (4)
- **Domanda** (fr/fr): "décret de naturalisation" 10 (2026, journal officiel, septembre 2026, juillet 2026, aout 2026). Si cerca il decreto del mese.
- **Fonte: ottima e aperta.** I file JORF della DILA (`echanges.dila.gouv.fr/OPENDATA/JORF/`, 200) contengono titolo e data di ogni decreto e il numero del JO. Letti 60 file di ottobre 2026: c'è per esempio il decreto dell'8/10/2026 "portant naturalisation…" (Accès protégé: i nomi non sono nei dati aperti, ed è giusto così).
- **Prima pagina: già coperta.** franceaccueil.com ha una pagina per ogni decreto ("Décret de naturalisation du 20 octobre 2026 paru au JO n° 0245", 594 menzioni) e il riepilogo del mese; assistances-juridiques.fr segue.
- **Chi paga:** AdSense FR, basso. **Stima** 100 / 400 / 1.500 €. **Voto 4.**

### 4.8 Traductores jurados per lingua e provincia (4)
- **Domanda** (es/es): "traductor jurado" 10 (madrid, barcelona, arabe español, valencia, maec, online); "traductor jurado ingles" 10 (madrid, barcelona, valencia, online); "lista traductores jurados" 10 (maec 2026 pdf).
- **Fonte:** pagina del Ministero degli Esteri 200 (57 KB), con un motore di ricerca sull'elenco ufficiale. L'elenco ha **nomi, telefoni ed email di persone**: ripubblicarlo è un trattamento di dati personali, contro le regole della rete.
- **Prima pagina:** agenzie con le loro pagine città (juridiomas, cblingua) e recensioni.
- **Chi paga:** AdSense ES con intenzione commerciale; i contatti ai traduttori sarebbero vendita diretta. **Stima** 200 / 700 / 2.000 €. **Voto 4.**

### 4.9 USA ispanici: licenza senza documenti ed esame di guida in spagnolo (3,5)
- **Domanda** (es/us): "examen de manejo en español" 10 (dmv nueva york, az, texas, idaho, 2026); "examen teorico de manejo" 10 (ny, nj 2026, california, illinois 2026, texas, georgia); ma "licencia de conducir sin papeles" 4, "licencia de manejo para indocumentados" 2, "seguro de carro sin licencia" 6.
- **Fonti:** DMV California 404 sul percorso, New York 403, Illinois non risponde. 50 enti diversi.
- **Prima pagina:** siti di quiz già grandi (mercato pieno, come i quiz di cittadinanza).
- **Stima** 150 / 600 / 2.500 €. **Voto 3,5.**

---

## 5. Righe per ESPLORATE (aggiunte)

Vedi la sezione "Ricerca lingue non inglesi (31/10/2026)" in ESPLORATE.

---

## 6. Fonti lette dal server (31/10/2026)

| Fonte | Stato | Nota |
|---|---|---|
| BOCM 25/3/2026 (EOI Madrid, alunni liberi) | 200, 150 KB | Anexo I: 29 date lette in automatico |
| Euskadi, calendari EOI 2025-26 e 2026-27 | 200, 138 e 265 KB | 32 + 32 date lette |
| `portal.edu.gva.es` (EOI Quart, straordinaria 2026) | 200, 207 KB | Griglia |
| `portal.edu.gva.es` (EOI Elx, PUC ordinaria) | 000 | – |
| Gobierno de Canarias, pruebas de certificación | 200, 93 KB | Finestre in HTML |
| BORM 2026 n. 181 (Murcia) | 200, 424 KB | Date a carico di ogni EOI |
| BOJA 221 del 17/11/2025 | 200, 308 KB | Documento sui corsi quadrimestrali di spagnolo |
| BOE, API dati aperti (sumario) | 200 con `Accept: application/json` | – |
| `inclusion.gob.es` / `sede.inclusion.gob.es` | 403 / 000 | – |
| `educacion.gob.es/centros` | 200, poi risposta vuota | Instabile |
| `todofp.es` | 200 | – |
| `exteriores.gob.es`, traduttori giurati | 200, 57 KB | Elenco con dati personali |
| `exteriores.gob.es`, bollettini del consolato di Buenos Aires (agosto, settembre, ottobre 2026) | 200 (255, 769, 625 KB) | Stato Ley de nietos in testo |
| `data.gouv.fr` (dataset examen civique) | 200 una volta, poi tunnel chiuso e nome non risolto | Da rileggere |
| `echanges.dila.gouv.fr/OPENDATA/JORF/` | 200 | 60 file di ottobre letti |
| `legifrance.gouv.fr` / `immigration.interieur.gouv.fr` | 403 / 403 | – |
| `svp-international.pacc.sa` → `svp-international.qiwa.sa` | 301 → 200 (applicazione JavaScript) | – |
| `svp-international-api.pacc.sa/api/v1/visitor_space/test_centers` | 200 | 280 centri, 14 pagine |
| `…/visitor_space/test_centers/<id>/activity_dates` | 404 | Date non pubbliche |
| `hajcommittee.gov.in` / `mora.gov.pk` / `hajj.nusuk.sa` | 200 / 200 / 200 | Prezzi Nusuk dietro login |
| `aekno.de` Fachsprachprüfung | 200, 45 KB | 430 €, data assegnata |
| `irn.justica.gov.pt` / `diariodarepublica.pt` / `aima.gov.pt` | 200 / 200 (2 KB, JavaScript) / 000 | – |
| `quebec.ca` francisation / `donneesquebec.ca` API | 200 / 200 | Dati aperti solo sulle imprese |
| DMV California / New York / Illinois | 404 / 403 / 000 | – |

Ricerche web (dagli USA, 31/10/2026):
- [BOCM 25/3/2026](https://bocm.es/boletin/CM_Orden_BOCM/2026/03/25/BOCM-20260325-12.PDF), [Euskadi calendario 2026-27](https://www.euskadi.eus/contenidos/informacion/eoi_matricula_libre/es_def/adjuntos/Calendario-Examenes-Anexo-II2026_2027-definitivo-1.pdf), [Canarias](https://www.gobiernodecanarias.org/educacion/web/idiomas/pruebas/pruebas_certificacion/pruebas_certificacion_idiomas_eoi/), [Valencia Plaza](https://valenciaplaza.com/educacion-abre-plazo-inscripcion-matricula-pruebas-certificacion-eoi);
- [FAQ regolarizzazione (Moncloa)](https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/inclusion/Documents/2026/160426-preguntas-frecuentes-regularizacion-extraordinaria.pdf), [ARC Legal](https://www.arc-legal.es/category/regularizacion/), [immigrationspain, corsi validi](https://www.immigrationspain.es/cursos-validos-arraigo-formacion/), [grupo2000](https://www.grupo2000.es/category/centros-validos-para-arraigo-socioformativo/);
- [Exteriores, Ley de nietos in cifre](https://www.exteriores.gob.es/es/Comunicacion/Exteriores-Explica/Paginas/2026_Articulos/Ley-nietos-memoria-democratica-nacionalidad-espanola.aspx), [bollettino Buenos Aires ottobre 2026](https://www.exteriores.gob.es/Consulados/buenosaires/es/Comunicacion/PublishingImages/Paginas/Boletin-informativo/Bolet%c3%adn_octubre_2026.pdf);
- [franceaccueil, decreti di ottobre 2026](https://franceaccueil.com/decrets-de-naturalisation-octobre-2026-journal-officiel/);
- [eco.sapo.pt, legge sulla nazionalità](https://eco.sapo.pt/descodificador/o-que-muda-com-a-lei-da-nacionalidade/), [Sovereign Group](https://www.sovereigngroup.com/news/portugal-nationality-law-update/);
- [Ekantipur, certificato SVP per il visto](https://ekantipur.com/news/2026/07/22/en/saudi-arabia-asks-for-skills-test-certificate-in-work-visa-application-22-25.html), [Kathmandu Post](https://kathmandupost.com/national/2026/07/30/saudi-arabia-halts-visas-for-nepali-workers-needing-skill-certificates-after-nepal-seals-testing-centre), [NAVTTC](https://navttc.gov.pk/?p=979);
- Ministerio de Educación, "Datos y cifras" 2025-26 (335.414 alunni EOI nel 2024-25), cifra riportata dalla ricerca web: da confermare sul PDF ufficiale prima di citarla in un sito.
