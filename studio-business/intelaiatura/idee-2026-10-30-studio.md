# Caccia serale del 30/10/2026: studio all'estero e studenti internazionali

**Settore scelto apposta:** studiare all'estero, nel mondo. Soldi da dimostrare per il visto, ore di lavoro, visto dopo la laurea, tasse universitarie per chi viene da fuori UE, costo del visto, esami di inglese accettati, conti bloccati, alloggi, borse di studio.

**Cosa ho saltato perché era già in `ESPLORATE.md`** (rilette tutte le righe, comprese le sette ricerche di oggi):
- soldi da dimostrare per il visto di studio, Paese per Paese (RISERVA 6, 27/10);
- ore di lavoro per gli studenti (NO 5, 29/10);
- tasse universitarie per università e Paese (NO 4, 23/10);
- tasso di ammissione degli stranieri (NO, 23/10);
- tempi dei permessi di studio in Canada (NO, 23/10);
- rifiuti e approvazioni dei visti di studio per nazionalità (Regno Unito, Australia, Canada, Nuova Zelanda: già nella sezione rifiuti di Visa Income Checker);
- medie IELTS per nazionalità (licenza chiusa, 23/10);
- studenti per università (HESA 403), OSHC, anabin (30/10);
- TOLC (30/10), WUE (30/10), TOPIK (17/10).

Le ho riaperte solo quando ho trovato un fatto nuovo, e lo scrivo.

**Metodo.** Autocomplete di Google con il Paese giusto (`gl=in`, `pk`, `ng`, `bd`, `us`, `gb`); stato HTTP e lettura delle fonti ufficiali con curl dal server; ricerca web per la prima pagina e per i programmi di affiliazione. Ore di lavoro calcolate sul motore di `visaincome/genera.py` (5.512 righe). Il motore ha già la funzione `pagina()`, le fonti con data, i cambi BCE in `dati/cambi.json` e lo schema `raccolta/X.py` → `dati/X.json`. Riferimenti per le ore: PPSN 3-5 ore, SELT 15-22, DTV 22-32.

**Limiti.** Niente strumenti a pagamento per i volumi di ricerca. La ricerca web mostra i risultati come da un computer negli USA. Dal server sono chiusi:
- `canada.ca` (000, di nuovo);
- `ice.gov` e `studyinthestates.dhs.gov` (403);
- `irishimmigration.ie` (403);
- `france-visas.gouv.fr` (403).

`open.canada.ca` risponde con 245 byte vuoti.

## 1. Tabella delle candidate

| # | Idea | Dove | Esito | Voto | Stima a 18 mesi (prudente / centrale / ottimista) | Ore |
|---|---|---|---|---|---|---|
| 1 | **Borse di studio regionali (DSU), tasse e ISEE parificato per gli studenti extra-UE in Italia, in inglese**, regione per regione e università per università, con i mezzi di sussistenza per il visto di studio italiano | Visa Income Checker, sezione nuova `/study-in-italy/` | **PASSA sotto l'asticella** (sezione) | **7** | 500 / 1.800 / 5.000 € | 20-28 |
| 2 | **Tassa proposta da 70.000 $ sull'OPT (USA)**: pagina che segue lo stato della norma (proposta del 8/10/2026, commenti fino al 9/11/2026) | Visa Income Checker, una pagina | **PASSA** come pagina piccola | 6 | 150 / 600 / 2.000 € | 3-5 |
| 3 | **Costo ufficiale del visto di studio per destinazione e nazionalità, nella valuta di chi paga** (tariffa + sanità + SEVIS + tassa di integrità USA) | Visa Income Checker, accanto alla riserva "soldi da dimostrare" | **PASSA sotto l'asticella** (sezione piccola) | 6 | 200 / 700 / 2.000 € | 10-14 |
| 4 | **Visto dopo la laurea nel Regno Unito: 2 anni o 18 mesi?** (cambio del 1/1/2027) e confronto con gli altri Paesi | Visa Income Checker, una pagina | **PASSA** come pagina piccola; NO come sezione | 5,5 | 100 / 400 / 1.000 € | 2-3 |
| 5 | **Esami di inglese accettati per il visto di studio e punteggi minimi**, Paese per Paese ("is Duolingo accepted for…") | Visa Income Checker, insieme alla sezione SELT già in coda | **RISERVA alta** (aggiunta) | 6 | 300 / 700 / 1.500 € | 8-12 |
| 6 | Lista STEM OPT per codice CIP (USA) | – | RISERVA | 5,5 | – | – |
| 7 | Programmi ammessi al PGWP per college e codice CIP (Canada) | – | NO oggi | 4,5 | – | – |
| 8 | Contributo semestrale e tasse per gli extra-UE, università per università (Germania) | – | NO | 4,5 | – | – |
| 9 | Esonero dai "frais différenciés" per università (Francia) | – | RISERVA debole | 5 | – | – |
| 10 | Conto bloccato tedesco 2027 | riga nella riserva del 27/10 | NO come idea | 4 | – | – |
| 11 | Soldi per il visto di studio in Giappone, Corea, Irlanda, Nuova Zelanda, USA (I-20) | – | NO | 3,5 | – | – |
| 12 | Alloggi per studenti come idea a sé (Amber, University Living, HousingAnywhere, Spotahome, Uniplaces) | canale di guadagno della n. 1 | NO come idea | – | – | – |
| 13 | Tempi del certificato APS (India, Cina, Vietnam per la Germania) | – | NO | 4 | – | – |

**Nessuna idea arriva a 7 con 5.000 €/anno realistici**, quindi nessun sito nuovo da proporre. La n. 1 arriva a 7 come sezione. Le n. 1-4 sono sezioni o pagine automatiche (o quasi), a costo zero e con guadagno atteso positivo. Per la regola della rete fitta del 30/10 si costruiscono (sez. 3).

## 2. Schede

### N. 1. Borse DSU, tasse e ISEE parificato per gli studenti extra-UE in Italia (voto 7)

**L'idea in una riga.** Una sezione in inglese con:
- una pagina per ogni ente regionale del diritto allo studio (DSU Toscana, ER.GO, EDISU Piemonte, DiSCo Lazio, ESU Padova/Venezia/Verona, ERSU Catania/Palermo, ERDIS Marche, EDISU Pavia, ADISU Puglia…);
- per ogni ente: importo della borsa per fuori sede, pendolari e in sede; soglie ISEE e ISPE; scadenza; alloggio; dove fare l'ISEE parificato;
- una pagina per le 20 università più cercate dagli stranieri, con la regola delle tasse per chi viene da fuori UE e con il link all'ente DSU della città;
- una pagina sui mezzi di sussistenza per il visto di studio italiano.

**Fatto nuovo rispetto a ESPLORATE.** La famiglia "Italia per studenti stranieri" non era mai stata guardata. Il 23/10 si erano chiuse le tasse universitarie "per università e Paese" nel mondo, non le borse regionali italiane, che hanno decreti nazionali e bandi ufficiali.

**Domanda (autocomplete).**
- pk/en "dsu scholarship" → 10 (italy, **2026**, university of milan, official website, apply online, requirements…).
- ng/en "dsu scholarship" → 10 (university of pisa, university of florence, portal…).
- bd/en "dsu scholarship italy" → 10, compresi **"2027 deadline"** e "2026 deadline".
- in/en "dsu scholarship" → 10 ("for indian students", "eligibility").
- pk/en "regional scholarship italy" → 10 ("2026 deadline", "requirements", "university list").
- pk/en "isee parificato" → 10 (certificate, documents, calculation, apply, english, padova); in/en "isee for international students" → 9 ("calculator", "requirements").
- pk/en "italy scholarship amount" → 10 ("italy regional scholarship amount", "dsu scholarship italy amount").
- Per università: pk/en "politecnico di milano fees for" → 10; in/en "university of bologna fees for international" → 10; in/en "tuition fees in italy for international" → 10.
- in/en "student accommodation in milan" → 10.
- Vuote: "particularly poor countries list" (0), "list of particularly poor countries italy" (0). Si cerca solo "particularly poor countries polimi": l'elenco va in una colonna, non in una pagina.

**Prima pagina di Google** ("dsu scholarship italy 2026 amount ISEE parificato"):
- blog di consulenti e di borse: drscholars, kadamboverseas (tre pagine), opportunityinside, afterschoolafrica, y-axis, study-abroad.org, migaku, scholarshipsfuture;
- un blog su blogspot per l'Università di Pisa.

Nessun ente ufficiale e nessuna tabella per regione. **Le cifre si contraddicono**: "fino a 6.806 €", "fino a 8.300 € in contanti", "2-7k", "₹5.8L". Il dato ufficiale per il 2026/27 è **7.171,11 €** per i fuori sede. Per "isee parificato" rispondono le pagine delle singole università (Padova, Bergamo, Trento, Bocconi, Genova, Palermo, Foggia, Tor Vergata). Ogni università spiega solo il proprio caso, e alcune guide in alto sono del 2018-2019.

**Fonti (lette dal server).**
- **MUR, Decreto Direttoriale n. 175 del 10/2/2026** (PDF 200, 384 KB): importi minimi 2026/27 di **7.171,11 €** fuori sede, **4.190,71 €** pendolari e **2.890,16 €** in sede (2025/26: 7.072,10 / 4.132,85 / 2.850,26). L'aumento segue l'indice ISTAT FOI (art. 3, c. 10, DM 1320/2021).
- **DD n. 176/2026**: soglie massime **ISEE 28.339,88 €** e **ISPE 61.608,48 €** (cifre riportate da pmi.it, studentville, universita.it e informazionefiscale; il PDF del decreto è da leggere al momento della costruzione).
- Gli atti ufficiali dello Stato non sono protetti dal diritto d'autore (art. 5 L. 633/1941), quindi la licenza non è un problema per decreti e bandi pubblici.
- Enti regionali raggiunti dal server: dsu.toscana.it 200 (la pagina della borsa ha il bando 2026/27 e il pagamento della seconda rata dopo il 30/6/2027), er-go.it 200 (pagine "Soglie economiche", "Scadenze", "Importi" e una sezione "International Students"; domanda "scaduta il 24/08/2026"), laziodisco.it 200, esu.pd.it 200, esu.vr.it 200, esuvenezia.it 200 (6 KB, da guardare), ersucatania.it 200 (con la nota CAF 2026/27 e l'elenco MUR delle autorità extra-UE che rilasciano i documenti, PDF 200), ersupalermo.it 200, erdis.it 200, edisu.pv.it 200.
- Enti che rispondono 000 con l'indirizzo provato: edisu.piemonte.it, adisupuglia.it, adisurc.it, ardis.fvg.it, ardsu.sardegna.it, ersu.ca.it, adsuaq.it. Alcuni indirizzi potrebbero essere sbagliati: da ricontrollare uno per uno prima di costruire.
- Università: host raggiungibili (unipd.it/en/fees 200, unipi.it 200, unitn.it 200, polimi.it 200, universitaly.it 200). I percorsi delle pagine tasse vanno trovati uno per uno: 5 su 8 indirizzi provati a caso danno 404.
- **Mezzi di sussistenza per il visto di studio italiano**: il compendio consolare del 2017 indica 5.824,91 € l'anno, cioè l'assegno sociale 2017 (448,07 €) × 13. Con l'assegno sociale 2026 (546,24 €, già usato il 27/10) farebbe **7.101,12 €**, mentre i blog scrivono "circa 6.000 €". **Da verificare** sulla pagina ufficiale dei visti (Farnesina) prima di pubblicarlo: oggi è una deduzione, non un dato letto.

**Aggiornamento.** I decreti MUR escono a febbraio; i bandi regionali tra giugno e luglio, con scadenze tra agosto e settembre. Uno script controlla ogni settimana le pagine dei bandi e la pagina "atti e normativa" del MUR e segnala i cambi; i numeri dei bandi si trascrivono a mano una volta l'anno, con verifica. È una sezione **quasi automatica**: va bene per la rete fitta, non per un sito nuovo.

**Chi paga, con commissione.**
- **Uniplaces** (alloggi per studenti in Milano, Roma, Bologna, Firenze, Padova, Torino). I suoi termini per i partner dicono "commissione per ogni inquilino presentato che prenota". Gli aggregatori riportano 12 % e cookie di 14 giorni (shopper.com) o 30 giorni (FlexOffers, programma Italia); un elenco su affi.io lo dà "Closed". Vieta cashback e codici sconto. Va verificato iscrivendosi, è nuovo per la rete.
- **Wise** (da 10 £ per nuovo cliente; "da chiedere" nel cruscotto): gli studenti pagano tasse e affitto dall'estero e ricevono la borsa.
- **italki** (18 $ per nuovo studente, attivo su Awin): corsi di italiano, richiesti da molti bandi per il secondo anno.
- AdSense: pubblico di Pakistan, India, Bangladesh e Nigeria, quindi pubblicità bassa (0,5-1,5 € ogni 1.000 pagine viste).
- HousingAnywhere, Spotahome, Amber, University Living: pagina affiliati 404 dal server, nessun programma trovato.

**Stima a 18 mesi.**
- Prudente: 1.500 visite al mese, 0,05 % di prenotazioni Uniplaces a circa 30 € e 0,1 % di clienti Wise → **circa 500 €/anno**.
- Centrale: 4.000 visite al mese → **circa 1.800 €/anno**.
- Ottimista: 10.000 visite al mese in stagione (giugno-ottobre), conversione Uniplaces vicina a quella dei siti di alloggi → **circa 5.000 €/anno**.
- Primi soldi: con la stagione dei bandi 2027/28 (giugno-settembre 2027), dopo l'iscrizione a Uniplaces e Wise.

**Ore (riuso di `genera.py`).**
- `raccolta/dsu.py`: decreti MUR e controllo delle pagine degli enti, 4-6 ore.
- `dati/dsu.json`: 16-18 enti e 20 università trascritti e verificati, 8-10 ore.
- Pagine con la funzione `pagina()` esistente (hub, enti, università, ISEE parificato, visto), 5-7 ore.
- Controlli in `verifica.py` e revisione, 3-5 ore.
- Totale: **20-28 ore**.

**Voto severo: 7.**
- Domanda 2/2: forte, ripetuta ogni anno, in quattro Paesi, con "2027 deadline" già in autocomplete.
- Google debole 1,5/2: solo blog con cifre sbagliate, ma molti e già posizionati.
- Fonte 1,5/2: ufficiale e libera, ma regionale, in PDF e annuale; 7 enti su 16 non letti stasera.
- Chi paga 1/2: Uniplaces e Wise arrivano al momento giusto, la pubblicità vale poco.
- Lavoro e rischi 1/2: trascrizione annuale; errore costoso se una scadenza è sbagliata, da coprire con "verifica sul bando" e la data accanto a ogni cifra.

**Perché non 8.** Il pubblico vale poco in pubblicità. La parte più cercata (scadenze e importi regionali) non è un file unico. Uniplaces non è ancora verificato.

### N. 2. Tassa proposta da 70.000 $ sull'OPT (voto 6)

**Fatto nuovo.** Il Federal Register del **8/10/2026** pubblica una proposta del DHS, "Optional Practical Training Fees" (doc. 2026-20660): **70.000 $** per il primo OPT e **30.000 $** per ogni OPT successivo; commenti chiusi il **9/11/2026**. Letto dall'API del Federal Register (200, pubblico dominio), la stessa usata il 28/10.

**Domanda.**
- in/en "opt fee" → 10 ("2026", "news", "hike", "update", "proposal", "rule");
- us/en "opt fee 70000" → 7;
- in/en "opt 70000" → 10 ("rule", "trump", "dhs");
- in/en "opt fee proposal" → 10;
- in/en "stem opt fee" → 10.

**Google.** Notizie, NAFSA, studi legali, università, Reddit. Rispondono tutti, ma lo **stato** cambia (proposta, poi regola finale, poi entrata in vigore o causa in tribunale) e le notizie invecchiano. Gli assistenti AI chiedono proprio "è già in vigore?".

**Pagina.** Una pagina "OPT fee 2026: status" con lo stato letto ogni giorno dall'API del Federal Register (documenti collegati alla stessa norma), le date, chi è toccato, il collegamento alla proposta. Il numero dei commenti viene da regulations.gov: la chiave di prova `DEMO_KEY` risponde 429, quindi serve una chiave gratuita (registrazione di Massimiliano, 2 minuti).

**Chi paga.** AdSense con una parte di pubblico USA; Wise.

**Stima.** 150 / 600 / 2.000 €/anno; l'ottimista vale se la norma diventa definitiva e la domanda dura mesi.

**Ore.** 3-5 ore. **Da fare subito**: la domanda è adesso.

**Voto 6.** Domanda enorme ma di cronaca, concorrenza di testate e università, una sola norma.

### N. 3. Costo ufficiale del visto di studio per destinazione e nazionalità, nella valuta di chi paga (voto 6)

**Domanda.**
- in/en "student visa fee" → 10 ("for uk/australia/new zealand/usa/germany/ireland from india");
- ng/en "student visa fee for" → 10 ("uk from nigeria/pakistan/nepal/bangladesh", "australia from bangladesh");
- in/en "australia student visa fee" → 10 ("in indian rupees 2026", "fee increase", "with dependent");
- in/en "uk student visa fee 2026" → 10 ("ihs fee 2026", "fee increase 2026");
- in/en "ihs fee for students" → 10;
- in/en "france student visa fee" → 10 ("in indian rupees", "from pakistan", "in nigeria");
- in/en "germany student visa fee" → 10 ("in indian rupees", "price in pakistan", "cost in bangladesh");
- in/en "us student visa fee" → 9;
- in/en "visa integrity fee" → 10 ("start date", "refundable", "for indians").

**Fonti.**
- Lette: gov.uk 200, OGL (Student visa **£558** da fuori; Graduate **£937** + sanità **£1.035** l'anno); Home Affairs 200 (contenuto dentro il JSON della pagina; tariffa del visto 500 da leggere nel "pricing estimator", 200 ma 1,3 MB); fmjfee.com 200 (SEVIS I-901).
- Chiuse: canada.ca 000, travel.state.gov 403 (già noto), france-visas 403, irishimmigration 403.
- La **tassa di integrità del visto USA (250 $)** è legge, ma la riscossione è a macchia: alcune sedi la chiedono a F-1 e J-1 da maggio 2026 (Boston University, 19/5/2026), nessuna data ufficiale del Dipartimento di Stato. Va scritto così, è una correzione utile.
- Cambi: la BCE ha la rupia indiana ma non rupia pakistana, naira, taka e rupia nepalese (stesso buco del 27/10): serve una seconda fonte di cambi aperta.

**Google.** Consulenti indiani e portali (non controllata la prima pagina di ogni coppia: da fare prima di costruire).

**Chi paga.** Wise (pagamento delle tasse dall'estero); AdSense basso.

**Stima.** 200 / 700 / 2.000 €/anno.

**Ore.** 10-14 ore, con il calcolatore dei cambi già nel motore.

**Voto 6.** Domanda forte e a matrice, ma metà delle fonti chiuse e pubblico a bassa pubblicità. Si unisce alla riserva "soldi da dimostrare" (27/10) in un'unica sezione "student visa costs": insieme salgono a 6,5.

### N. 4. Visto Graduate britannico: 2 anni o 18 mesi? (voto 5,5)

**Fatto.** gov.uk (200, OGL): "**2 years if you apply on or before 31 December 2026; 18 months if you apply on or after 1 January 2027**; PhD 3 years". La ricerca web di stasera, chiedendo un confronto, ha risposto che il Regno Unito dà "2 anni, non 18 mesi": è proprio l'errore che una pagina con la data corregge.

**Domanda.**
- gb/en "graduate visa 18 months" → 10 ("reduced to 18 months", "change to 18 months", "2 years or 18 months");
- in/en "graduate route 18 months" → 5;
- in/en "post study work visa" → 10 (9 Paesi).

**Google** sul confronto tra Paesi: almeno 5 siti automatici su `pages.dev` (studyabroad-wiki, wheretoemigrate ×3, wheretostudyaway, unilink-co-git), più gradright, ICICI Lombard, consulenti. **Come sezione per Paese: NO**, è già coperta.

**Pagina.** Una pagina con il calcolatore "quando hai la laurea / quando fai domanda → 2 anni o 18 mesi", il costo (£937 + £1.035 l'anno di sanità) e il link alla pagina dei rifiuti britannici di studio già online.

**Stima.** 100 / 400 / 1.000 €/anno. **Ore** 2-3, da fare prima del 1/1/2027.

### N. 5. Esami di inglese accettati per il visto di studio, Paese per Paese (voto 6, RISERVA alta)

**Domanda.**
- in/en "is duolingo accepted for" → 10 (canada, uk, ireland, australia, germany student visa);
- in/en "pte score for australia student visa" → 10;
- in/en "ielts score for student visa" → 10;
- in/en "which countries accept duolingo" → 10 ("for visa", "for study visa").

**Fonte.** Home Affairs, pagina del visto 500 (200): tabella dei punteggi (IELTS 6.0 / 5.5 / 5.0; TOEFL iBT 64 / 46 / 35; Cambridge C1 Advanced 169 / 162 / 154; PTE), elenco dei test online **non** accettati (IELTS Online, TOEFL Home Edition, OET@Home…) e la regola nuova: **dal 21/1/2026** si deve scegliere "Taking TOEFL for Australia". Per il Regno Unito c'è già la sezione SELT in coda (cloni del 30/10). Canada e Germania non hanno un punteggio minimo per il visto (decide l'università): la risposta corretta è "dipende dall'università", da scrivere.

**Licenza** di Home Affairs non letta (la pagina del copyright dava 404 il 27/10): **da leggere prima di costruire**.

**Chi paga.** AdSense; corsi di preparazione non verificati stasera.

**Stima.** 300 / 700 / 1.500 €/anno. **Ore** 8-12 ore come aggiunta alla sezione SELT.

**Perché riserva.** Concorrenza forte (IDP, Pearson, Duolingo stesso, blog) e una sola tabella ufficiale ricca (Australia).

### N. 6-13. In breve

| # | Idea | Prove | Esito |
|---|---|---|---|
| 6 | Lista STEM OPT per codice CIP | in/en "stem opt eligible" 10 ("cip codes", "majors", "list"), in/en "is computer science stem" 10, "stem designated degree program list". Lista DHS su `ice.gov` (PDF 403) e `studyinthestates.dhs.gov` (403). Codici CIP NCES 200 (CSV 1,1 MB, pubblico dominio). Il Federal Register ha solo gli aggiornamenti (2022, 2023, 2024), non la lista intera. Rispondono già le università | RISERVA (5,5): si riapre se ice.gov si legge da GitHub Actions; collegata alla n. 2 |
| 7 | Programmi ammessi al PGWP (Canada) | Domanda enorme e per college (in/en "pgwp eligible programs list" 10: fanshawe, conestoga, bcit, nait, centennial, kpu; "pgwp eligible cip codes"). `canada.ca` 000 di nuovo, `ircc.canada.ca` 404, `open.canada.ca` 245 byte. I college pubblicano già i propri elenchi | NO oggi (4,5); si riapre se canada.ca si legge |
| 8 | Contributo semestrale e tasse per gli extra-UE in Germania | in/en "semester contribution" 10 per università (chemnitz, dresden, darmstadt, tuhh, jlu, bremen); "baden württemberg tuition fees for international students" 0. Circa 400 università con pagine proprie (filtro duro); `study-in-germany.de` 404; mygermanuniversity e blog | NO (4,5) |
| 9 | Esonero dai "frais différenciés" per università (Francia) | Campus France 200 (regole ed elenco delle istituzioni; ogni università decide gli esoneri parziali). in/en "exoneration frais differencies" 5 (solo Paris 8). Pubblicità francese e africana bassa | RISERVA debole (5) |
| 10 | Conto bloccato tedesco 2027 | in/en "blocked account amount 2027" 7, "germany 2027" 5. Nessuna cifra ufficiale per il 2027 (11.904 € dal 1/9/2024); la pagina dell'Auswärtiges Amt provata dà 400, make-it-in-germany 200. Fintiba, Expatrio, Coracle: di nuovo nessun programma pubblico (404) | NO come idea (4): una riga nella riserva del 27/10, con un controllo automatico della cifra |
| 11 | Soldi per il visto di studio in Giappone, Corea, Irlanda, Nuova Zelanda, USA | Giappone e Corea: nessun importo ufficiale ("sufficient funds"; in/en "japan student visa bank balance" 8). Irlanda 10.000 € (`irishimmigration.ie` 403). Nuova Zelanda in JavaScript (27/10). USA: I-20 diverso per università | NO (3,5): conferma la riserva del 27/10 |
| 12 | Alloggi per studenti come idea a sé | HousingAnywhere, Spotahome, University Living, student.com: pagine affiliati 404; amberstudent.com/partner 3 KB; Uniplaces con termini partner (vedi n. 1) | NO come idea: canale di guadagno della n. 1 |
| 13 | Tempi del certificato APS | in/en "aps certificate processing time" 7 ("india", "2025"). Pubblico indiano a bassa pubblicità; l'ente pubblica i tempi; fonte non letta stasera | NO (4) |

## 3. Sezioni da costruire (rete fitta: automatiche o quasi, costo zero, guadagno positivo)

Ordine per guadagno atteso per ora di lavoro e per urgenza:

| Ordine | Sezione | Sito | Stima a 18 mesi (prudente / centrale / ottimista) | Ore | Quando | Guadagno |
|---|---|---|---|---|---|---|
| 1 | Pagina "OPT fee 2026: status" (Federal Register API, poi regulations.gov) | Visa Income Checker | 150 / 600 / 2.000 € | 3-5 | **subito** (commenti fino al 9/11/2026) | AdSense, Wise |
| 2 | Pagina "UK Graduate visa: 2 years or 18 months?" con calcolatore della data | Visa Income Checker | 100 / 400 / 1.000 € | 2-3 | prima del 1/1/2027 | AdSense |
| 3 | Sezione "Study in Italy": borse DSU per ente, soglie ISEE/ISPE, ISEE parificato, tasse per università, mezzi per il visto | Visa Income Checker | 500 / 1.800 / 5.000 € | 20-28 | costruzione a novembre-dicembre con i dati 2026/27; aggiornamento a febbraio 2027 con i decreti nuovi, prima dei bandi di giugno | Uniplaces (da iscrivere), Wise, italki, AdSense |
| 4 | Sezione "Student visa costs" (costo del visto per destinazione × nazionalità, unita alla riserva "soldi da dimostrare" del 27/10) | Visa Income Checker | 200 / 700 / 2.000 € | 10-14 | dopo la n. 3 | Wise, AdSense |
| 5 | Esami di inglese per il visto di studio (aggiunta alla sezione SELT in coda) | Visa Income Checker | 300 / 700 / 1.500 € | 8-12 | con la sezione SELT, dopo aver letto la licenza di Home Affairs | AdSense |

**Totale delle cinque:** circa 1.250 / 4.200 / 11.500 €/anno a 18 mesi, per 43-62 ore. Tutte in Visa Income Checker: stesso pubblico (studenti e chi chiede un visto), stessi programmi, nessun sito nuovo e nessun passaggio su Netlify.

**Cosa serve da Massimiliano** (solo account, nessuna spesa):
- iscrizione a Uniplaces (dalla pagina partner o da FlexOffers/Awin, da verificare);
- Wise (già "da chiedere" nel cruscotto);
- chiave gratuita di api.data.gov per il numero dei commenti di regulations.gov (facoltativa: la pagina OPT funziona anche senza).

## 4. Lezione della serata

Nel settore dello studio all'estero i grandi Paesi anglosassoni sono già coperti da consulenti indiani e da siti automatici su `pages.dev`, e le fonti più cercate sono chiuse al server (Canada, USA, Irlanda). Il buco vero sta dove la regola è **italiana, ufficiale, in PDF regionali e con cifre sbagliate nei blog** (borse DSU), e dove una **data** cambia la risposta (OPT 2026, Graduate visa 1/1/2027). Prossimo angolo da provare: gli stessi buchi in Spagna (becas MEC e autonomiche per stranieri), in Francia (bourses CROUS per extra-UE) e in Germania (Deutschlandstipendium per università), più i pubblici che pagano di più: studenti americani in Europa (FAFSA all'estero, prestiti federali per università straniere).

## 5. Fonti principali

- Autocomplete: `https://suggestqueries.google.com/complete/search?client=firefox&gl=XX&hl=en&q=...` (gl = in, pk, ng, bd, us, gb), 30/10/2026.
- MUR, Decreto Direttoriale n. 175 del 10/2/2026: https://www.mur.gov.it/sites/default/files/2026-03/Decreto%20Direttoriale%20n.%20175%20del%2010-02-2026.pdf (200) e scheda https://www.mur.gov.it/it/atti-e-normativa/decreto-direttoriale-n-175-del-10-02-2026
- Soglie ISEE/ISPE 2026/27 (DD 176/2026) riportate da https://www.pmi.it/?p=467391 e https://www.studentville.it/borse-studio-universitarie-2026-27-aumenti-isee-ispe/
- DSU Toscana https://www.dsu.toscana.it/borsa-di-studio (200); ER.GO https://www.er-go.it/ (200); nota CAF 2026/27 di ERSU Catania (PDF 200).
- Blog con cifre in conflitto: https://kadamboverseas.com/dsu-scholarship-italy-indian-students-2026/, https://opportunityinside.com/scholarships/dsu-scholarship-italy-2026.html, https://drscholars.com/italy-dsu-scholarship/
- Uniplaces, termini partner: https://www.uniplaces.com/terms/partners; aggregatori: https://shopper.com/partnerships/uniplaces-com-affiliate-program, https://www.flexoffers.com/affiliate-programs/uniplaces-it-affiliate-program/, https://affi.io/m/uniplaces-ww
- Federal Register, "Optional Practical Training Fees" (proposta, 8/10/2026): https://www.federalregister.gov/documents/2026/10/08/2026-20660/optional-practical-training-fees
- gov.uk Graduate visa https://www.gov.uk/graduate-visa e Student visa https://www.gov.uk/student-visa (200, OGL).
- Home Affairs, Student visa 500 (200): https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/student-500
- Tassa di integrità del visto USA: https://www.bu.edu/isso/?p=16496, https://www.alliance-exchange.org/alliance-commentary/rollout-details-and-timing-of-new-visa-integrity-fee-remain-unclear
- Siti automatici sul visto dopo la laurea: https://studyabroad-wiki.pages.dev/posts/post-study-work-visa-comparison-2026, https://wheretoemigrate.pages.dev/blog/post-study-work-visas-compared-2026
- Campus France, tasse: https://www.campusfrance.org/en/tuition-fees-france (200).
- Mezzi per il visto di studio italiano (2017): https://static.tlscontact.com/media/dz/compendio_2017diramatostudenti-1.pdf
