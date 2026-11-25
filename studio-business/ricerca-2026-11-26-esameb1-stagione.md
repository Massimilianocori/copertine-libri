# Ricerca del 26/11/2026: EsameB1 e la stagione di gennaio-febbraio 2027

Solo ricerca. Nessun sito toccato, nessun commit.
Regola usata: ogni affermazione ha un numero e una fonte. Dove il dato non c'è, c'è scritto **manca** o **ipotesi**.

## In una riga

Le pagine nuove che passano tutte le prove sono 4, non 10. Insieme valgono da 7 a 21 visite a settimana in più (oggi il sito ne fa 401). Cinque dei sette temi proposti esistono già e fanno meno di 2 visite a settimana ciascuno. Quello che cresce da solo prima di un esame sono le pagine con i file ufficiali: `/esempi/cils/` è passata da 8 a 15 visite al giorno a 9 giorni dall'esame.

## Come sono stati presi i dati

- **GoatCounter**: API pubblica `stats/hits`, 7 settimane dal 12/10 al 25/11/2026, paginazione con `exclude_paths`, una chiamata ogni 1,5 secondi, 21 chiamate per le pagine e circa 50 per la provenienza. Totali uguali al cruscotto: 1.009 (2-8/11), 1.792 (9-15/11), 1.222 (16-22/11). Lette il 25/11/2026 tra le 22:50 e le 23:40 UTC.
- **Provenienza**: `stats/hits/{id}` per 26 pagine di EsameB1, periodo 12/10-25/11.
- Host vecchio e nuovo sommati (`esameb1.netlify.app` 915 visite, `esameb1.eu` 1.298).
- **Volumi**: lo strumento non è in `studio-business/strumenti/`. È l'API `api.seodata.dev/v1/keyword` descritta in `intelaiatura/BRIEF-RICERCA.md`. 117 frasi chieste, Paese `it`. La chiave non è stata stampata né scritta.
- **Limite dello strumento**: per 83 frasi su 117 risponde «volume 0» con errore 404. Vuol dire «frase non in archivio», non «zero ricerche». In questo file quelle frasi hanno **manca**.
- **Suggerimenti di Google**: 70 inizi di frase, lingua e Paese `it`, letti il 25/11/2026.
- **Reddit e forum**: **non letti**. Reddit risponde 403 alla lettura diretta. La ricerca web non può aprire reddit.com. Il forum Tapatalk «italiancitizenship» risponde 403. La ricerca web ha dato solo pagine di enti e scuole, nessuna discussione.
- **Cosa chiedono a ChatGPT**: le domande non si vedono. Si vede solo su quale pagina arriva chi clicca. È un segnale indiretto.
- Il sito è online dal 9/10/2026. **La stagione dell'anno scorso manca.** Si vedono solo tre esami: CELI 11/11, PLIDA 18/11, CILS 3/12.

---

## 1. Cosa cercano nelle settimane prima dell'esame

### 1.1 Quali pagine sono cresciute prima degli esami (GoatCounter)

Visite a settimana di EsameB1, per sezione:

| Sezione | 19-25/10 | 26/10-1/11 | 2-8/11 | 9-15/11 | 16-22/11 | 23-25/11 (3 giorni) |
|---|---|---|---|---|---|---|
| Tutto il sito | 114 | 342 | 475 | 635 | 401 | 236 |
| `/citta/` | 74 | 195 | 233 | 252 | 118 | 70 |
| `/esempi/` | 0 | 4 | 72 | 98 | **148** | 99 |
| Home | 22 | 48 | 67 | 106 | 39 | 20 |
| `/ente/` | 7 | 22 | 44 | 42 | 28 | 11 |
| `/en/` | 0 | 0 | 19 | 51 | 27 | 11 |
| `/risultati/` | 2 | 14 | 6 | 25 | 5 | 0 |
| `/costo/` | 5 | 18 | 13 | 17 | 7 | 4 |
| `/come-funziona/` | 3 | 21 | 6 | 11 | 8 | 2 |

Tre fatti misurati, giorno per giorno:

1. **CILS del 3/12.** `/esempi/cils/`: 58 visite nella settimana 16-22/11 (8,3 al giorno). Poi 7, 18 e 20 visite il 23, 24 e 25/11 (15 al giorno). A 9 giorni dall'esame il ritmo è **1,8 volte** quello della settimana prima.
2. **PLIDA del 18/11.** `/esempi/plida/`: 6 e 10 visite il 16 e 17/11, cioè nei 2 giorni prima dell'esame. La settimana prima faceva 2,4 visite al giorno. Dopo l'esame: 4 visite in 3 giorni.
3. **CELI dell'11/11.** `/esempi/celi/`: 7 visite il giorno stesso dell'esame, contro 2 al giorno nella settimana prima.

Dopo l'esame cresce un'altra pagina:

4. `/risultati/cils/`: 14 visite in 3 giorni (11-13/11), 11 da Google. Sono 21-23 giorni dopo l'esame CILS del 21/10.

Cosa **non** è cresciuto prima degli esami: `/costo/`, `/come-funziona/`, `/esenzioni-e-domande/`. Restano piatte o calano.

### 1.2 Da dove arrivano (12/10-25/11)

| Pagina | Visite con provenienza | ChatGPT | Google | Interne |
|---|---|---|---|---|
| `/esempi/cils/` | 162 | **88** | 0 | 58 |
| `/esempi/` | 105 | **55** | 0 (Bing 12) | 28 |
| `/esempi/plida/` | 56 | **38** | 0 | 14 |
| `/esempi/celi/` | 40 | **20** | 0 | 12 |
| `/esempi/b2/` | 18 | **17** | 0 | 0 |
| `/esempi/a2/` | 11 | **9** | 0 | 1 |
| `/citta/milano/` | 161 | 17 | **104** | 12 |
| `/citta/torino/` | 53 | 4 | **40** | 4 |
| `/ente/cils/` | 84 | 5 | **52** | 13 |
| `/en/b1-exam-dates/` | 41 | 2 | **26** | 6 |
| `/risultati/cils/` | 19 | 0 | **11** | 5 |
| `/costo/` | 64 | 0 | 0 | quasi tutte |
| `/esempi/confronto/` | 13 | 0 | 5 | 6 |

Lettura:

- **ChatGPT manda le persone solo sulle pagine con i file ufficiali da scaricare.** Su 6 pagine di file: 227 visite da ChatGPT e 0 da Google.
- **Google manda le persone sulle pagine «ente + data» e «città + data».** Lì ChatGPT pesa dal 5 all'11 %.
- **`/costo/` e `/come-funziona/` non ricevono nessuno da fuori.** Vivono dei link interni delle pagine città.

Quindi nelle 4-8 settimane prima dell'esame la domanda ha due forme:

- **a ChatGPT**: «dove trovo le prove ufficiali di X con audio e soluzioni»;
- **a Google**: «esame B1 a Milano», «CILS B1 cittadinanza date», «iscrizione».

### 1.3 Volumi di ricerca (media mensile, Italia)

| Tema | Frasi con volume | Ricerche al mese |
|---|---|---|
| Risultati | risultati cils 1.900; risultati esami cils 880; www cvcl it risultati 880; risultati esami cils b1 cittadinanza 480; celi b1 cittadinanza risultati 480 | **oltre 4.600** |
| Prova online, simulazione, PDF | test lingua italiana b1 per cittadinanza online 1.300; simulazione test cittadinanza italiana b1 pdf 1.000; test italiano b1 online gratis 1.000; test b1 italiano 880; cils b1 cittadinanza pdf 480; test b1 italiano per stranieri pdf 480 | **oltre 5.100** |
| Ente e esame | cils b1 cittadinanza 1.000; esame b1 italiano per cittadinanza 720; esame b1 cittadinanza 390 | 2.110 |
| Dove farlo | test lingua italiana b1 per cittadinanza dove farlo 480; sedi esami cils b1 cittadinanza 110 | 590 |
| Iscrizione | iscrizioni cils 210; iscrizione esame b1 per cittadinanza 140 | **350** |
| Prove CELI B1 | celi b1 prove d'esame pdf 170; celi 2 b1 prove d'esame 110 | 280 |
| Corsi | corso b1 italiano 320; corso b1 italiano per cittadinanza online 110 | 430 |
| Test A2 per la carta di soggiorno | test italiano a2 1.600; test lingua italiana per carta di soggiorno 320; test italiano per carta di soggiorno 210 | 2.130 |
| Cosa portare, senza diploma, esonero, 4 settimane, orale, ascolto, punteggio | nessuna frase in archivio | **manca** |

### 1.4 Suggerimenti di Google (25/11/2026)

Quante frasi suggerisce Google per ogni tema:

| Tema | Frasi suggerite | Esempi |
|---|---|---|
| Prove, PDF, simulazione | 20 circa | «cils b1 cittadinanza prove d'esame pdf», «esame cils b1 cittadinanza simulazione» |
| Città | 25 e più | «esame b1 cittadinanza milano», «… mantova», «… varese» |
| Iscrizione | 13 | «cils b1 cittadinanza iscrizione online», «iscrizione esame b1 per cittadinanza bergamo» |
| Orale | 10 | «cils b1 cittadinanza prova orale», «argomento esame orale cils b1 cittadinanza», «plida b1 prova orale» |
| Risultati | 15 e più | «risultati cils giugno 2026», «risultati esame b1 cittadinanza italiana perugia» |
| Libro | 6 | «cils b1 cittadinanza libro», «libro esame b1 cittadinanza», «celi b1 cittadinanza libro» |
| Ascolto | 4 | «cils b1 cittadinanza ascolto», «plida b1 ascolto» |
| Punteggio | 4 | «cils b1 cittadinanza punteggio minimo» |
| Anno 2027 | 3 | «cils b1 cittadinanza date 2027», «b1 cittadinanza esame 2027» |
| Senza B1 | 2 | «cittadinanza italiana senza b1», «cittadinanza italiana per matrimonio senza b1» |
| Carta di soggiorno con B1 | 1 | «esame b1 per carta di soggiorno» |
| **Cosa portare** | **0** | nessun suggerimento |
| **Senza diploma, analfabeti, over 65** | **0** | nessun suggerimento |
| **Scadenza, febbraio, gennaio, dicembre** | **0** (solo «febbraio 2025») | nessun suggerimento |
| **Come prepararsi, 4 settimane, è difficile** | **0** per l'italiano | i suggerimenti parlano dell'esame di inglese |
| **Quando escono i risultati** | **0** per il B1 | i suggerimenti parlano di altri concorsi |

### 1.5 Forum e Reddit

**Manca.** Vedi «Come sono stati presi i dati». Unico segnale indiretto: l'Istituto di Cultura di Stoccarda pubblica un foglio «Informazioni per i candidati B1 Cittadinanza» con «documento e penna nera». Quindi la domanda «cosa portare» esiste, ma risponde la sede.

---

## 2. Quali pagine mancano davvero

Prima il controllo sui 7 temi candidati. Ho letto la sitemap (10 file) e il testo delle pagine in `esameb1/sito`.

| Tema candidato | C'è già? | Visite della pagina che c'è (7 settimane) | Domanda misurata | Verdetto |
|---|---|---|---|---|
| Scadenze iscrizione per ente, sessioni di febbraio | **In parte.** Le date sono in home, `/ente/` e `/citta/`. Nessuna pagina ha «iscrizione» nel titolo | – | 350 ricerche al mese, 13 suggerimenti | **Manca la pagina. Da costruire** |
| Scadenze per città | **No.** Le sedi decidono la propria scadenza. Le sedi sono 643 | `/citta/`: 118 a settimana oggi | 7 città nei suggerimenti con «iscrizione» | Non una pagina: una riga in più nelle 8 città più viste, solo se la sede pubblica il bando |
| Quando escono i risultati | **Sì.** `/risultati/` più 4 pagine ente, `/dopo-esame/` con la tabella sessione per sessione | 52 in tutto; `/risultati/celi/` 1, `/risultati/plida/` 4 | oltre 4.600 al mese | Non manca. Non costruire |
| Cosa portare il giorno dell'esame | **Sì.** `/come-funziona/` ha la sezione e le parole nel titolo. «Cosa portare» compare in 42 pagine | 51, quasi tutte da link interni | 0 suggerimenti, volume manca | Non costruire |
| Esame B1 senza diploma | **In parte.** «Titolo di studio» è in `/esonero-test-italiano/` e `/esenzioni-e-domande/`. «Senza diploma» non è scritto da nessuna parte | 7 e 11 | 0 suggerimenti, volume manca | Non costruire |
| Esenzioni | **Sì, due volte** | 7 e 11 | 2 suggerimenti («senza b1») | Non costruire. Solo un ritocco al titolo |
| Certificato B1 per la carta di soggiorno | **Sì.** `/carta-di-soggiorno/`, `/test-italiano-a2/`, sezione «Un certificato, due usi» | **0 e 0** | 2.130 al mese sul test A2 | Non costruire. Google non manda nessuno su queste pagine. Chi le legge non compra un libro B1 |
| Preparazione in 4 settimane | **No** | pagine simili: `/esempi/simulazione/` 2, `/esempi/prova-scritta/` 3 | 0 suggerimenti, volume manca | Non costruire |

Poi ho cercato che cosa manca tra i tipi di pagina che **funzionano** (file ufficiali per ChatGPT, ente e data per Google):

| Controllo | Risultato |
|---|---|
| Esami B1 validi per la cittadinanza senza una pagina di file | Uno solo: il **CELI 2** generale. Nel sito non c'è nessun link a `celi-2-prove-esame`. L'esame è il 9/3/2027 |
| Prove dell'esame senza una pagina | **Orale** e **ascolto**. C'è solo `/esempi/prova-scritta/` |
| Città dei suggerimenti senza pagina | Nessuna (Mantova, Varese, Firenze, Bergamo, Monza, Perugia: ci sono) |

### Un'avvertenza che cambia le stime

`/esempi/prova-scritta/` rispetta già lo schema «una frase con dato, fonte e data, più una tabella». Apre così: «Secondo i documenti ufficiali dei 4 enti, controllati l'11 novembre 2026…». Ha fatto **3 visite in 3 settimane e 0 da ChatGPT**.

Quindi lo schema da solo non basta. Le pagine citate hanno una cosa in più: **il titolo e la prima frase promettono file da scaricare** («9 file, PDF e MP3, gratis»). Le pagine nuove vanno scritte così, oppure faranno come `/esempi/prova-scritta/`.

---

## 3. Le pagine proposte

### Come sono fatte le stime

Quattro misure prese dai nostri dati:

- **M1. Pagina di file nuova, prima settimana, da ChatGPT**: `/esempi/b2/` 12, `/esempi/a2/` 6.
- **M2. Pagina di file per ente, a regime, da ChatGPT**: `/esempi/celi/` 20 visite in 4 settimane, cioè 5 a settimana.
- **M3. Quota di Google**: `/ente/cils/` ha preso 52 visite da Google in 5 settimane, cioè 10,4 a settimana. La frase «cils b1 cittadinanza» fa 1.000 ricerche al mese, cioè 233 a settimana. Quota: 10,4 / 233 = **4,5 %**. Dopo il cambio di dominio Google è al 38 % di prima (92 / 241). Quota prudente: 4,5 % × 0,38 = **1,7 %**.
- **M4. Guida in prosa**: `/esempi/prova-scritta/` 1 visita a settimana, `/esempi/simulazione/` 0,7.

Le stime sono visite a settimana dopo 3-4 settimane online. Sono stime, non numeri.

### Tabella in ordine di visite attese

| # | Pagina | Prova di domanda | Visite/sett. prudente | Visite/sett. centrale | Conti | Online entro |
|---|---|---|---|---|---|---|
| 1 | `/esempi/ascolto/`: gli audio ufficiali MP3 dei 4 esami B1, con trascrizioni e chiavi | 4 suggerimenti di Google. Volume: manca. Le pagine con MP3 sono le più citate: 88 visite da ChatGPT su `/esempi/cils/` | **2** | **6** | Centrale = M1 basso (6). Prudente = un terzo, perché gli stessi MP3 sono già elencati in `/esempi/cils/` | **14/12** |
| 2 | `/esempi/celi-2/`: i file ufficiali del CELI 2 (B1 generale) | 280 ricerche al mese. Esame il 9/3/2027, iscrizione entro il 9/2 | **2** | **6** | ChatGPT: 2 (40 % di M2) e 5 (M2). Google: 280 / 4,3 = 65 a settimana × 1,7 % = 1. Prudente senza Google, perché oggi Google manda 0 visite su `/esempi/` | **4/1/2027** |
| 3 | `/esempi/prova-orale/`: i file ufficiali dell'orale (tracce, immagini, criteri) | 10 suggerimenti di Google. Volume: manca | **1** | **5** | Prudente = M4 (1). Centrale = M1 basso meno 1 (5), solo se la pagina apre con i file | **14/12** |
| 4 | `/iscrizione/`: le 4 scadenze di iscrizione per gli esami di febbraio 2027 | 350 ricerche al mese, 13 suggerimenti | **2** | **4** (7 dal 4 al 22/1) | Google: 350 / 4,3 = 81 a settimana. × 1,7 % = 1,4. × 4,5 % = 3,6. ChatGPT sulle pagine di date: 0,3-0,7 a settimana (`/ente/celi/` 3 in 5 settimane, `/citta/torino/` 4 in 6). Picco: × 1,8 misurato su `/esempi/cils/` | **30/11**, al più tardi 7/12 |
| 5 | Non è una pagina nuova: riga «scadenza della sede» nelle 8 pagine città più viste | 7 città nei suggerimenti con «iscrizione». Le 8 città fanno il 51 % delle visite di `/citta/` (480 su 946) | 0 | 6 | **Ipotesi**: + 10 % su 60 visite a settimana. Nessuna misura | 7/12, solo se i bandi ci sono |
| | **Totale delle 4 pagine nuove** | | **7** | **21** | | |

Non ci sono altre pagine che passano le prove. La tabella si ferma a 5 righe.

### Scheda di ogni pagina

**1. `/esempi/ascolto/`**

- Prima frase: quanti file audio ufficiali ci sono, di quale ente, controllati in quale data.
- Tabella: ente, file, durata, trascrizione, chiavi.
- Fonti controllate il 25/11/2026 alle 23:33 UTC:
  - CILS: `https://cils.unistrasi.it/1/89/382/Prove_Liv._B1_c.htm` (200); MP3 `…/382/UNO_B1%20cittadinanza.mp3` (risponde, audio/mpeg); `…/382/TRASCRIZIONI%20B1%20Cittadinanza.pdf` (risponde).
  - PLIDA: `https://plida.dante.global/it/preparati-allesame/` (200); `https://cms.plida.dante.global/wp-content/uploads/2024/03/PLIDA-B1_prova-esempio-1.zip` (risponde).
  - CELI: `https://cvcl.unistrapg.it/pagine/esami-celi-immigrati` (200). **I file stanno su `www.unistrapg.it`, che stasera non si apre da qui** (errore di certificato con curl, 503 con l'altro strumento). Il link c'è nella pagina ufficiale. Va riprovato prima di pubblicare.
  - CERT.IT: `https://certificazioneitaliano.uniroma3.it/il-sistema-di-certificazione/livello-b1-livello-soglia/` (200). Solo descrizione, come oggi.
- Riquadro del libro: subito sotto il titolo (`libro_in_alto`), con la riga «17 tracce audio del libro gratis» verso `/audio-libro/`. Etichetta dei clic: `libro-ascolto`.
- Rischio: toglie visite a `/esempi/cils/`, che elenca già lo stesso MP3.

**2. `/esempi/celi-2/`**

- Prima frase: quanti file ufficiali ha il CELI 2, fonte Università per Stranieri di Perugia, data.
- Tabella: i 9 file elencati stasera nella pagina ufficiale: facsimile, 2 archivi di prove d'esame, descrizione della prova, valutazione, conversione dei punteggi, competenze richieste, punteggi dello scritto, punteggi dell'orale.
- Fonte: `https://cvcl.unistrapg.it/pagine/esami-celi-generici` (200 stasera, i 9 link ci sono). **I file su `www.unistrapg.it` stasera non si aprono da qui**: contenuto e dimensioni non letti.
- Riquadro del libro: sotto il titolo. Etichetta: `libro-celi2`.
- È lo stesso tipo di `/esempi/cils-b1-standard/`, costruita ieri.

**3. `/esempi/prova-orale/`**

- Prima frase: quanti file ufficiali esistono per l'orale, ente per ente, data.
- Tabella: ente, file, cosa contiene, durata dell'orale.
- Fonti controllate stasera:
  - CILS: `https://cils.unistrasi.it/public/articoli/382/Input%20aggiuntivo_B1citt_1_PO.pdf` (risponde); `…/382/Criteri%20di%20valutazione%20B1%20cittadinanza_nuovi.pdf` (risponde).
  - PLIDA: `…/2022/11/PLIDA-B1-Criteri-valutazione-prove-Parlare.pdf` (risponde); `…/2026/10/Quaderno-delle-specifiche-PLIDA-B1.pdf` (risponde).
  - CELI: 3 file elencati nella pagina ufficiale `esami-celi-immigrati` (200): esempi di input orale, vademecum orale, criteri di valutazione orale. **File non raggiungibili stasera** (stesso problema di `www.unistrapg.it`).
  - CERT.IT: `https://certificazioneitaliano.uniroma3.it/gli-esami/indicazioni-sullo-svolgimento/` (200).
- Riquadro del libro: sotto il titolo. Il riquadro «Preparati alla prova orale» che c'è già resta più in basso. Etichetta: `libro-orale`.
- Rischio alto: la pagina gemella della prova scritta fa 1 visita a settimana.

**4. `/iscrizione/`**

- Prima frase: la prossima scadenza di iscrizione, con ente, fonte e data del controllo.
- Tabella, tutta riletta stasera sulle fonti:

| Ente | Esame | Iscrizione | Fonte (stato stasera) |
|---|---|---|---|
| PLIDA B1 | 10/2/2027 | la decide ogni centro | `https://cms.plida.dante.global/wp-content/uploads/2026/11/Calendario-esami-PLIDA-2027-per-il-sito.pdf` (risponde). Risultati: 23/3/2027 urgenti, 25/5/2027 ordinari |
| CERT.IT B1 | 11/2/2027 | **dal 4/1 al 21/1/2027** | `https://certificazioneitaliano.uniroma3.it/` (200) |
| CELI 2 i cittadinanza | 17/2/2027 | entro il 22/1/2027 | `https://cvcl.unistrapg.it/pagine/calendario-esami-celi-e-dils-pg-000` (200) |
| CILS B1 Cittadinanza | 18/2/2027 | entro il 18/1/2027 | `https://cils.unistrasi.it/public/articoli/428/LETTERA%20date%20MAE_2027_pdf.pdf` (risponde) |
| CELI 2 | 9/3/2027 | entro il 9/2/2027 | stessa pagina CELI |

- Come ci si iscrive: `https://cils.unistrasi.it/1/88/71/Iscrizione_agli_esami_CILS.htm` (200), `https://cvcl.unistrapg.it/pagine/iscrizione-esami-celi-000` (200), `https://certificazioneitaliano.uniroma3.it/gli-esami/iscrizione-agli-esami/` (200).
- La pagina deve aggiornarsi da sola dopo il 22/1 e mostrare le scadenze di aprile (CILS 8/4, iscrizione entro l'8/3).
- Riquadro del libro: dopo la tabella, non prima. Chi arriva vuole la data. Testo: «Iscritto? Mancano N settimane». Etichetta: `libro-iscrizione`.
- **Nota:** ieri `ricerca-2026-11-25-asset.md` (sez. 2.4) ha scritto che una pagina «sessione di febbraio» non serve, perché home e città mostrano già la data. Sono d'accordo sulla data d'esame. Qui la pagina risponde a un'altra parola, «iscrizione», che oggi non è nel titolo di nessuna pagina. Il valore atteso resta basso: 2-4 visite a settimana.

**5. Riga «scadenza della sede» nelle pagine città**

- Solo per Milano, Torino, Bologna, Parma, Verona, Roma, Brescia, Bari.
- Solo se la sede pubblica un bando ufficiale per febbraio 2027. **Stasera non ne ho verificato nessuno.** Nel repo c'è un solo bando di sede, quello di UniMi per febbraio 2026.
- Se i bandi non ci sono, non si fa.

### Le 3 da costruire per prime

L'ordine è per scadenza, non per visite.

1. **`/iscrizione/`, con la pubblicazione di lunedì 30/11.** È la sola che dipende da Google, e Google chiede settimane. La finestra si chiude il 22/1. Se esce dopo il 14/12 non vale la pena.
2. **`/esempi/ascolto/`, entro lunedì 14/12.** ChatGPT cita in fretta: `/esempi/b2/` ha avuto 12 visite nella prima settimana. Chi studia per febbraio comincia a metà dicembre.
3. **`/esempi/prova-orale/`, entro lunedì 14/12**, insieme alla 2.

`/esempi/celi-2/` può aspettare il 4/1: l'esame è il 9/3.

Prova a costo zero prima di costruire la 3: riscrivere il titolo e la prima frase di `/esempi/prova-scritta/` mettendo avanti i file («N tracce ufficiali in PDF»). Se in 2 settimane ChatGPT comincia a citarla, la pagina dell'orale vale. Se resta a 0, no.

---

## 4. Cosa NON costruire, con i dati

| Pagina | Perché no |
|---|---|
| «Cosa portare il giorno dell'esame» | 0 suggerimenti di Google. Volume: manca. C'è già in `/come-funziona/`, che non riceve visite da fuori |
| «Esame B1 senza diploma» | 0 suggerimenti. Volume: manca. Nessuna fonte ufficiale usa queste parole |
| Altre pagine sulle esenzioni | Ce ne sono 2. Fanno 7 e 11 visite in 7 settimane |
| «B1 per la carta di soggiorno» | Le 2 pagine che ci sono fanno **0 visite in 7 settimane**, con 2.130 ricerche al mese sul tema. Il test è A2: chi legge non compra il libro B1 |
| «Preparazione in 4 settimane» | 0 suggerimenti. È una guida in prosa: `/esempi/simulazione/` 2 visite in 3 settimane, `/esempi/prova-scritta/` 3, ChatGPT 0 su entrambe |
| Pagine «risultati» per singola sessione | È il tema più cercato (oltre 4.600 al mese). Ma CILS scrive solo «dopo circa 3 mesi» e non pubblica lo stato sessione per sessione. Non si può scrivere «usciti» o «non usciti» da una fonte. Le date PLIDA sono già in `/risultati/plida/`. E chi cerca i risultati ha già dato l'esame |
| «Punteggio minimo» | 4 suggerimenti, ma il dato è già in 13 pagine. Precedente: `/costo/` ha un dato ufficiale in apertura e riceve 0 visite da Google e 0 da ChatGPT |
| Pagina per ogni sessione («CILS 18 febbraio 2027») | Dal 4/12 il titolo di `/ente/cils/` porta già quella data. Sarebbe un doppione |
| Pagine sui corsi | `/cpia/` ha 13 pagine e 2 visite in 7 settimane |
| Altre pagine in inglese | `/en/b1-exam-dates/` funziona (26 visite da Google in 3,5 settimane) e contiene già le date. La home `/en/` fa 29 visite. Le altre pagine `/en/` fanno da 0 a 8 visite ciascuna in 7 settimane |

---

## 5. Tre correzioni senza pagina nuova

1. **CERT.IT, sessione dell'11/2/2027.** In `sessioni.json` la scadenza è vuota. Stasera la home di Roma Tre scrive «Iscrizioni aperte dal 4 gennaio 2027 al 21 gennaio 2027». Con questo dato `/ente/certit/` e le pagine città mostrano una scadenza vera.
2. **Titolo di `/esonero-test-italiano/`.** Google suggerisce «cittadinanza italiana senza b1» e «cittadinanza italiana per matrimonio senza b1». Le parole «senza B1» non sono nel titolo. La pagina fa 7 visite in 7 settimane.
3. **Riquadro del libro in alto su tutte le pagine `/esempi/`.** È la sezione che cresce prima dell'esame (148 visite a settimana, 67 % da ChatGPT). Ieri la misura era 10 clic ogni 100 visite con il riquadro in alto e 0,4 in basso (`ricerca-2026-11-25-asset.md`, sez. 2.1).

---

## 6. Due cose fuori dalla regola, da decidere

La regola di questa ricerca è «solo pagine da fonti ufficiali». Queste due non la rispettano. Le segnalo perché la domanda è misurata.

- **Una pagina del libro sul sito.** Google suggerisce 6 frasi con «libro»: «libro esame b1 cittadinanza», «cils b1 cittadinanza libro», «celi b1 cittadinanza libro», «libro per esame b1 italiano per cittadinanza». Volume: manca. Oggi sul sito c'è solo `/audio-libro/`, che in 7 settimane non compare tra le pagine visitate. Chi scrive «libro» vuole comprare.
- **Una prova del libro da fare online.** «Test lingua italiana b1 per cittadinanza online» fa 1.300 ricerche al mese, «test italiano b1 online gratis» 1.000. Le prove ufficiali non si possono copiare. Una delle 4 simulazioni del libro sì, perché è nostra.

---

## 7. Detto chiaro

- Le 4 pagine nuove portano da 7 a 21 visite a settimana. Google ne ha tolte 149 (da 241 a 92). **Le pagine nuove non coprono il buco.**
- In clic sul libro: 21 visite × 3 clic ogni 100 = meno di 1 clic a settimana.
- La crescita vera della stagione verrà dalle pagine che ci sono già. `/esempi/cils/` fa da sola 58 visite a settimana e sale a 1,8 volte vicino all'esame. A febbraio gli esami sono 4 in 9 giorni.
- Per questo la correzione n. 3 (riquadro in alto su `/esempi/`) vale più di tutte le pagine nuove messe insieme.

## 8. Cosa resta incerto

- La stagione dell'anno scorso manca. Il «× 1,8 prima dell'esame» viene da un solo esame e da 3 giorni di dati.
- Per 83 frasi su 117 lo strumento dei volumi non ha dati. Orale, ascolto, cosa portare, senza diploma: nessun numero di ricerche.
- Reddit e forum non letti.
- Le domande fatte a ChatGPT non si vedono. Si vedono solo le pagine di arrivo.
- I file di `www.unistrapg.it` (CELI) stasera non si aprono da questa sessione. Vanno riletti prima di costruire le pagine 1, 2 e 3.
- I bandi delle singole sedi per febbraio 2027 non sono stati cercati.
- Nel repo ci sono modifiche di altri non ancora pubblicate (`genera.py`, `genera_livelli.py`, pagine `/esempi/a1/`, `/c1/`, `/c2/`, `/cils-b1-standard/`). Non le ho toccate. Le pagine nuove non hanno ancora visite: non so come vanno.
