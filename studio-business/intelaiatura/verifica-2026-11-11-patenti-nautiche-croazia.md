# Verifica indipendente: "La mia patente nautica vale in Croazia?" (11/11/2026)

Idea 1 di `fronti-2026-11-11-sera-nautica-camper.md` (voto del ricercatore 5,5; 60 / 1.700 / 14.700 €/anno). Tutto riletto oggi con curl dal server. Dove un dato non è stato letto, è scritto.

## 1. Verdetto

- **SITO NUOVO: NO-GO.** Non passa l'asticella dei siti nuovi (voto 5, centrale sotto 5.000 €), costa un dominio e crediti Netlify, e parte da zero su Google.
- **SEZIONE DI BEFORE YOU FLY: GO, piccola.** Costo zero, dati ufficiali confermati, pagatori aperti, vuoto vero in italiano e in tedesco e sulla "coda lunga" dei titoli. Entra in coda per €/ora (circa 24 €/ora centrali), online entro il 1° febbraio 2027.
- **Voto: 5** (era 5,5). **Stima come sezione: 15 / 430 / 5.000 €/anno a 18 mesi** (era 60 / 1.700 / 14.700).
- **Rischio più grande:** il vuoto è più stretto di quanto scritto dal ricercatore. SkipperCity ha già, in inglese, un cercatore dei titoli, il PDF del ministero e i limiti dei 6 titoli più comuni. Il nostro spazio è: italiano, tedesco, pagine per singolo titolo e i circa 170 titoli che SkipperCity elenca senza limiti.

## 2. Piano di costruzione (sezione di Before You Fly)

**Dove.** `beforeyoufly`, accanto a «Driving abroad» e «Scooter rental: which licence?» (stesso tipo di domanda: "la mia patente vale all'estero?"). Nessun dominio nuovo.

**Pagine della versione 1 (circa 75, online entro il 1° febbraio 2027; la stagione va da aprile a ottobre, le ricerche partono a febbraio).**

| Lingua | Indirizzo | Pagine |
|---|---|---|
| Inglese | `/boat-licence-croatia/` | 1 indice con cercatore di tutte le 178 righe (filtro per Paese e per nome del titolo) + 40 pagine Paese + circa 22 pagine titolo (RYA Day Skipper Shorebased, Day Skipper practical, Day Skipper Certificate of Competence, Powerboat Level 2, Coastal Skipper, ICC, ASA/US Sailing, Vaarbewijs I e II, permis francese, titoli irlandesi, polacchi, cechi, sloveni, svizzeri) + 1 pagina certificato radio VHF + 1 pagina "barca tua con bandiera straniera" |
| Italiano | `/it/patente-nautica-croazia/` | 1 indice + 3 pagine (entro 12 miglia, senza limiti, navi da diporto) + 1 pagina radio |
| Tedesco (versione 1.1) | `/de/bootsfuehrerschein-kroatien/` | 1 indice + SBF See, SSS, SHS (righe 11-13; **lo SKS non compare nella tabella**: va detto, è una ricerca da 10 suggerimenti), titoli austriaci e svizzeri (circa 10). **Nodo prima di farla:** una sezione in tedesco rivolta alla Germania chiede l'Impressum con nome e indirizzo (stesso nodo dei pannelli da balcone). Si fa solo dopo la decisione su quel punto |
| Olandese | – | Non ora: solo 2 righe nella tabella e Borrow A Boat ha già la risposta giusta in olandese |

Ogni pagina titolo: titolo con il nome che la gente scrive; prima frase «According to the table of recognised certificates of Croatia's Ministry of the Sea, Transport and Infrastructure dated 21 May 2026 (row N), …»; tabella con 5 righe (barca privata, barca a noleggio, yacht privato, yacht a noleggio, zona di navigazione); condizione del certificato radio; frase ufficiale parola per parola con il numero di riga; riquadro fisso «What the charter company may ask on top» e «Ask the charter company or the harbour master's office before you pay»; data della tabella e collegamento alla pagina ufficiale `mmpi.gov.hr/sea/nautics/8462`.

**Flusso dei dati (`raccolta/patenti_nautiche.py`).**
1. Legge la pagina ufficiale «Nautics» e prende l'indirizzo del file dal collegamento «Recognized certificates for operating boats and yachts» (non si scrive l'indirizzo a mano: il nome del file contiene la data e cambia a ogni versione).
2. Scarica il .docx, salva impronta SHA-256 e `Last-Modified` in `dati/`.
3. Lo apre con `zipfile` + `xml.etree` (nessuna libreria in più). Il file è spezzato in **96 tabelle** da 5 colonne (numero, Stato, ente, titolo, competenza) con 46 righe di intestazione ripetute: si scorrono in ordine, si saltano le intestazioni, si riporta lo Stato sulle righe dove la cella è vuota, si uniscono alla riga numerata precedente le **47 righe senza numero** (sono pezzi di riga andati a capo pagina).
4. Da ogni competenza estrae con regole fisse: lunghezza (18 m, 24 m), stazza (30, 100, 500 GT/BT), distanza dalla costa (1, 3, 6 miglia), zona (acque interne e mare territoriale / viaggi internazionali in Adriatico / senza limiti), condizione radio. **Se una regola non combacia con tutta la frase, la riga è «manuale»: la pagina mostra solo la frase ufficiale, senza la nostra tabella.**
5. Seconda lettura dal PDF ufficiale (`pdftotext`): stesso numero di righe numerate e stessi numeri per ogni riga, altrimenti errore.
6. I paragrafi fuori tabella (base legale; regola generale sull'ICC valido per «Coastal waters») si salvano a parte e diventano la pagina ICC.

**Controlli in `verifica.py` (blocco nuovo).**
- Impronta del .docx uguale a quella salvata; se la pagina ufficiale collega un file nuovo, errore «tabella cambiata» e la sezione non si pubblica finché non è riletta.
- 178 righe numerate, da 1 a 156 con le lettere; nessuna pagina nata da una riga senza numero.
- Ogni numero di una pagina (metri, GT, miglia) compare nella frase ufficiale di quella riga; la frase ufficiale è nella copia della fonte parola per parola.
- Ogni pagina ha: numero di riga, data «21 May 2026», collegamento alla pagina ufficiale, riquadro «ask the charter company / harbour master's office».
- Parole vietate: «guaranteed», «always accepted», «sempre valida», «garantito».
- Riquadro affiliato solo dopo la risposta ufficiale, con `rel="sponsored noopener"`, etichetta «Affiliate» e riga di trasparenza; domini in `monetizzazione.json`.
- Coppie hreflang inglese/italiano complete; sitemap con `lastmod` = data della lettura.

**Dove vanno i collegamenti che pagano.**
- Dopo la tabella e la frase ufficiale, mai sopra: «Charter a boat in Croatia». Ordine: SkipperCity (cookie 365 giorni, solo Croazia), SamBoat su Awin (IT nelle pagine italiane, UK nelle inglesi), yachting.com.
- Per i titoli con limiti stretti (per esempio Vaarbewijs I e «Żeglarz jachtowy»: solo barche, entro 1 miglio dalla costa): riquadro «charter with a skipper».
- AdSense nello spazio `{AD}` già usato dal sito.
- Trasparenza: la pagina Privacy del sito ha già la sezione sui collegamenti affiliati; in più la riga dentro ogni riquadro.

**Che cosa serve dal titolare (20 minuti, a dicembre):** richiesta di SamBoat IT e UK su Awin (account già attivo), modulo di yachting.com (approvazione immediata, scritto sulla loro pagina), modulo di SkipperCity. Nessuna spesa.

**Tempi.** Raccolta e lettura dei dati: 4 ore. Pagine inglesi e italiane: 8 ore. Revisione dei fatti riga per riga e del design: 5 ore. Totale **16-18 ore** di agenti (tedesco: altre 4). Costruzione a gennaio, pubblicazione entro il 1° febbraio con IndexNow. Da febbraio a settembre, controllo mensile del collegamento ufficiale (se cambia il file, rilettura).

**Prima di scrivere le pagine (obbligo del costruttore).** Leggere la definizione ufficiale di «boat» e «yacht» nella legge croata (oggi non letta: la tabella usa le due parole con limiti diversi) e scriverla con la fonte. Se non si legge, le pagine citano solo la frase ufficiale e non la spiegano.

## 3. Nuovo sito o sezione di Before You Fly? Il confronto

| | Sito nuovo | Sezione di Before You Fly |
|---|---|---|
| Costo | dominio circa 10 €/anno + 15 crediti Netlify a pubblicazione + un passaggio del titolare su Netlify | 0 € (esce con le pubblicazioni già previste) |
| Ore | 28-35 (identità, home, privacy, revisione del design da zero) | 16-18 (motore, design, controlli e monetizzazione già pronti) |
| Partenza su Google | da zero; nella rete un sito nuovo ha avuto 0 pagine indicizzate su 119 dopo 4 settimane (Italy Strikes) | dominio con 1.600 pagine e circa 300 visite a settimana, sezioni sorelle già online (patente all'estero, scooter, auto a noleggio), collegamenti interni dalle pagine Croazia |
| Lingue | libere (tedesco facile) | inglese e italiano pronti (`/it/` esiste); tedesco da aggiungere, con il nodo Impressum (che un sito nuovo in tedesco avrebbe uguale) |
| Affiliazioni | i programmi chiedono un sito online: si aspetta | sito già online e già su Awin: richiesta subito |
| Coerenza del tema | sito solo nautico: più chiaro | «Before you fly» parla di documenti di viaggio: una patente che vale o no all'estero è lo stesso tema; chi vola a Spalato per una settimana in barca è lo stesso pubblico |
| Stima centrale | circa 200 €/anno (metà visite per i primi 18 mesi) | circa 430 €/anno |
| €/ora centrale | circa 6 | circa 24 |

**Scelta: sezione di Before You Fly.** Il sito nuovo conviene solo se la sezione, dopo una stagione, supera 15.000 visite l'anno: allora si valuta di allargarla (Grecia, Spagna, Italia) e di darle un dominio.

## 4. Le prove raccolte oggi

### 4.1 Dati (prova: SÌ)

- Pagina ufficiale che lo annuncia: `https://mmpi.gov.hr/sea/nautics/8462` (HTTP 200), voce «OTHER DOCUMENTS – Recognized certificates for operating boats and yachts (.pdf / .docx)». Il file è già in inglese; la cartella si chiama «TABLICE MoU HR-EN», quindi esiste anche la versione croata (non scaricata).
- File: `…/dokumenti/MORE/More 5_26/TABLICE MoU HR-EN 21-5_26/TBL- MoU ENG 21-5_26.docx`, HTTP 200, 203.873 byte, `Last-Modified: Thu, 21 May 2026 13:12:07 GMT`; dentro il file: creato e modificato il 21/5/2026. PDF gemello: 1.085.194 byte.
- Letto con uno script di 30 righe: **96 tabelle, 271 righe di tabella, tutte da 5 colonne**. Di queste: 46 intestazioni ripetute, **178 righe numerate (da 1 a 156, con lettere: 69a…)**, 47 righe senza numero (pezzi di riga). **40 Paesi.** Il ricercatore scriveva «circa 230 titoli»: i titoli veri sono 178.
- Campi: Stato, ente che rilascia, nome del titolo, competenza. Nelle competenze: «18 m» in 70 righe, «24 m» in 37, «500 GT/BT» in 42, zona «internal waters and territorial sea» in 86, «Adriatic» in 48, distanza di 1 miglio in 5, condizione radio in 177.
- Fuori tabella: base legale (art. 4 dell'ordinanza su barche e yacht; art. 48 dell'ordinanza del 2020) e la regola generale sull'ICC: accettato se indicato come valido per «Coastal waters» e nei limiti scritti sul certificato.
- **La tabella vale per le barche con bandiera croata** (scritto in testa: «for operating Croatian flag boats and yachts»), cioè per i noleggi in Croazia. Per la barca propria con bandiera straniera la stessa pagina ufficiale dice che vale il titolo richiesto dallo Stato di bandiera.
- **Riuso:** le condizioni d'uso del sito del ministero (`/uvjeti-koristenja/76`) dicono che i contenuti si possono riprendere citando la fonte e senza permesso. Noi riportiamo i fatti con parole nostre, più la frase ufficiale tra virgolette con riga e data.
- **Frequenza di aggiornamento:** oggi ho letto solo la versione del 21/5/2026. Le versioni precedenti (2019, 2020, 2023, 2024) le cita il ricercatore: non riverificate. Ritmo probabile: una volta ogni 1-2 anni, senza data fissa. Per questo serve il controllo mensile dell'impronta.
- `robots.txt` del ministero: 404 (nessun divieto scritto).

**Attenzione, il testo ufficiale ha punti poco chiari.** Riga 8 (Italia, entro 12 miglia): «yachts used for private purposes up to 24 m in length and up to 30 GT, bareboat chartered yachts up to 24 m in length and up to 18 m». Quindi il limite di 30 GT vale per lo yacht privato; per lo yacht a noleggio il limite scritto è 18 m. **Il ricercatore aveva letto «fino a 24 m e 30 GT» per il noleggio: non è così.** Le pagine devono riportare la frase e non interpretare oltre.

I 5 titoli chiesti, come stanno nella tabella del 21/5/2026:

| Titolo | Riga | Yacht a noleggio | Zona | Radio |
|---|---|---|---|---|
| RYA Day Skipper Shorebased (teoria) | 69 | fino a 18 m | acque interne e mare territoriale croato | sì, se c'è il VHF |
| RYA Day Skipper practical course completion | 69a | fino a 18 m | viaggi internazionali in Adriatico | sì |
| ICC | regola generale | secondo i limiti scritti sul certificato | solo se valido per «Coastal waters» | – |
| SBF See (Germania) | 11 | fino a 18 m | acque interne e mare territoriale croato | sì |
| Patente italiana entro 12 miglia | 8 | fino a 18 m (privato: 24 m e 30 GT) | acque interne e mare territoriale croato | sì |
| Vaarbewijs I (Paesi Bassi) | 119 | **nessuno yacht: solo barche** | **entro 1 miglio dalla costa** | sì |

### 4.2 Concorrenti (prova «nessuno lo fa meglio»: SÌ a metà)

Che cosa dà ognuno sul limite esatto del singolo titolo (letto oggi):

| Titolo | SkipperCity (EN, 6.300 parole) | PlainSailing (EN) | Borrow A Boat (EN, DE, IT, NL) | yacht.de | ADAC Skipper-Portal | ÖAMTC | Sailwiz (IT) |
|---|---|---|---|---|---|---|---|
| Day Skipper teoria | solo il nome nell'elenco | non la distingue | EN: non la tratta nella pagina letta | – | – | – | – |
| Day Skipper pratica | **sì: 18 m, Adriatico (riga 69a)** | «sei qualificato», nessun limite | «accettato», nessun limite | – | – | – | – |
| ICC | **sì: regola «Coastal waters»** | «accettato» | «accettato» | – | – | – | – |
| SBF See | **sì: 18 m (riga 11)** | solo il nome | DE: «accettato in tutte le basi», **nessun 18 m**, nessuna fonte | articolo del 2015 sui vecchi titoli senza «See» | «anerkannt», nessun limite | «Bootsführerschein», nessun dettaglio | – |
| Patente entro 12 miglia | **sì, in breve: «da 18 m… a 500 GT, secondo l'abilitazione» (righe 8-10)** | solo «<24mt» | IT: «è riconosciuta», **nessun 18 m**, nessuna fonte | – | – | – | pagina di annunci, nessuna regola |
| Vaarbewijs I | solo il nome | solo il nome | **NL: sì, «entro 1 zeemijl», corretto** | – | – | – | – |

Altri fatti:
- **SkipperCity è più avanti di quanto scritto dal ricercatore**: ha un cercatore dei titoli in cima, una tabella «Common licences» con i limiti e il numero di riga per 6 titoli, la data 21 May 2026 e ospita il PDF del ministero (identico byte per byte a quello ufficiale). Non ha: i limiti degli altri titoli circa 170 (0 volte «internal waters», «territorial», «30 GT», «1 NM» nella pagina), pagine per titolo, altre lingue.
- Borrow A Boat ha già pagine in quattro lingue, senza fonte e senza limiti, salvo l'olandese.
- **Ricerca tedesca «sportbootführerschein see kroatien anerkannt»:** Google non si legge da qui; DuckDuckGo ha risposto con la pagina di blocco e Bing con un captcha: non insistito. Con lo strumento di ricerca della sessione (indice USA, non la prima pagina tedesca vera) escono: bootsschule1.de (5 pagine; da qui 403, non letto), yacht.de (2015), ÖAMTC, Borrow A Boat DE, ADAC, Nautal, Filovent. Il riassunto della ricerca attribuisce a una di queste pagine il limite di 18 m per lo SBF See (probabilmente bootsschule1: **non verificato**). In tedesco quindi il vuoto è «fonte ufficiale + pagine per titolo», non «nessuno dice 18 m».
- Italiano: Borrow A Boat IT, Click&Boat, Nautal, Filovent, Sailwiz. Nessuno di quelli letti dà il limite di 18 m o cita la tabella.
- Le due frasi di Borrow A Boat citate dal ricercatore («theory-only… not accepted», «only valid for certain small crafts») non sono nella pagina inglese che ho letto oggi: non riverificate.

**Conclusione:** vuoto dimostrato su 3 titoli su 6 in inglese (teoria Day Skipper, Vaarbewijs I, più tutta la coda lunga), su 2 su 2 in italiano e in tedesco per la fonte ufficiale. Non è un vuoto largo: SkipperCity può chiuderlo in un giorno.

### 4.3 Domanda (prova: SÌ, media)

Autocomplete Google di oggi (`client=firefox`, Paese e lingua giusti), numero di suggerimenti:

| Paese | Ricerca | N. | Suggerimenti sulla validità |
|---|---|---|---|
| Regno Unito | rya day skipper croatia | 10 | «is rya day skipper accepted in croatia», «rya day skipper practical croatia» |
| Regno Unito | icc croatia | 10 | «icc boat license croatia», «icc certificate croatia» |
| Regno Unito | boat licence croatia | 10 | «do you need a license to rent a boat in croatia», «are boat licence international» |
| Regno Unito | powerboat level 2 croatia | 8 | «rya powerboat level 2 croatia» |
| Stati Uniti | sailing license croatia | 10 | quasi tutti su corsi e scuole |
| Germania | sportbootführerschein kroatien | 10 | «in kroatien gültig», «see kroatien anerkannt», «deutscher sportbootführerschein kroatien» |
| Germania | sbf see kroatien | 7 | «sbf see in kroatien gültig» |
| Austria | küstenpatent kroatien | 10 | tutti sulla patente croata (altra idea) |
| Italia | patente nautica croazia | 10 | «patente nautica italiana in croazia», «regole», «obbligo»; gli altri sul prendere la patente in Croazia |
| Italia | patente nautica entro 12 miglia croazia | 0 | – |
| Paesi Bassi | vaarbewijs kroatië | 10 | «vaarbewijs 1 kroatië», «nodig», «regels»; gli altri sul prenderlo o comprarlo |
| Francia | permis bateau croatie | 4 | «permis bateau francais valable en croatie» |
| Polonia | patent żeglarski chorwacja | 3 | – |

Lettura severa: **circa metà dei suggerimenti parla di prendere la patente in Croazia** (corso, prezzo, comprare), non della validità del proprio titolo. La domanda sulla validità c'è in 5 Paesi ma è la parte minore.

**Stagione:** noleggi da aprile a ottobre; le ricerche sui documenti salgono da febbraio (prenotazioni) a luglio. Fuori stagione quasi zero: la sezione va giudicata su febbraio-agosto.

**Stima delle visite, con il metodo.** Non ho un dato di volume. Uso il ritmo vero della rete: Before You Fly fa circa 300 visite a settimana su 1.600 pagine, cioè 0,19 visite a pagina a settimana. Una sezione di 75 pagine a quel ritmo: 14 a settimana, circa **750-900 l'anno (prudente)**. Centrale: 5 volte la media del sito (domanda con frasi esatte in 5 Paesi, pagine con il nome del titolo nel titolo, dominio che cresce) = **4.500 l'anno**. Ottimista: **25.000 l'anno** (tedesco compreso e sezione fra i primi risultati per i nomi dei titoli). I 18.000 centrali del ricercatore non hanno un numero dietro.

### 4.4 Soldi (prova: SÌ, pagatori aperti; resa non misurabile da fuori)

| Programma | Letto oggi | Note |
|---|---|---|
| SamBoat IT (Awin 32681), UK (32677), US (32679) | profili pubblici 200: «commissioni comprese tra il 5% e il 8% sulle vendite», cookie 30 giorni | **EPC, tasso di conversione e tasso di approvazione non sono nel profilo pubblico** (si vedono solo entrando in Awin): da leggere dopo l'iscrizione |
| SkipperCity | 20 % della loro provvigione (25 % ai soci regolari); esempio «600 € → 120 €»; **cookie 365 giorni** e cliente attribuito a vita; pagamento mensile sopra 50 €, solo a noleggio iniziato | il più adatto: decisione lunga, solo Croazia. È anche il concorrente principale |
| yachting.com | «3% commission», noleggio medio circa 3.000 €, 90-100 € a ordine; «We will approve your registration immediately» | iscrizione con modulo |
| Borrow A Boat | pagina `/affiliates`: 404 | non letto |
| AdSense | già attivo sul sito | nessun dato nostro sulla resa di queste pagine: ipotesi 5-8 € ogni 1.000 visite |

**Conversione realistica.** Chi chiede «la mia patente vale?» spesso ha già prenotato (il noleggiatore chiede il titolo alla prenotazione) oppure ha una barca sua. Solo una parte sta ancora scegliendo. Nessun sito della rete ha mai venduto un noleggio da 2.000-3.000 €: le percentuali sotto sono ipotesi.

**Formula: visite × quota che clicca il noleggio × quota che prenota × provvigione + AdSense.**
- Prudente: 900 × 4 % × 0,5 % = 0,2 prenotazioni × 60 € = 11 € + AdSense 900 × 5/1.000 = 4 € → **circa 15 €/anno**.
- Centrale: 4.500 × 6 % × 1,5 % = 4 prenotazioni × 100 € = 405 € + AdSense 4.500 × 6/1.000 = 27 € → **circa 430 €/anno** (senza il tedesco: circa 250).
- Ottimista: 25.000 × 8 % × 2 % = 40 prenotazioni × 120 € = 4.800 € + AdSense 200 € → **circa 5.000 €/anno**.

Primi soldi: non prima di maggio-giugno 2027 (SkipperCity paga a noleggio iniziato).

### 4.5 Rischi

1. **Errore che costa caro al lettore** (resta a terra con la barca pagata, o multa). Rimedio: frase ufficiale con riga e data in ogni pagina; mai «vale» senza i limiti; riquadro fisso «il noleggiatore può chiedere di più: chiedi a lui o alla capitaneria prima di pagare»; righe poco chiare mostrate così come sono.
2. **Testo ufficiale ambiguo o con refusi** (riga 8; «BT» e «GT» usati insieme; parole «boat» e «yacht» non definite nella tabella). Rimedio: righe «manuali» senza la nostra tabella; definizione ufficiale da leggere prima di scrivere.
3. **Concorrente che è anche pagatore**: SkipperCity ha già metà del lavoro in inglese e può aggiungere il resto. Il nostro vantaggio dura solo nelle lingue e nelle pagine per titolo.
4. **Stagione**: 7 mesi utili su 12; se si esce dopo febbraio si perde l'anno.
5. **Manutenzione**: il nome del file cambia a ogni versione; senza il controllo mensile le pagine restano con una data vecchia. Costo: 10 minuti al mese, 2-3 ore a ogni tabella nuova.
6. **Tedesco**: è la domanda più grande, ma chiede la decisione sull'Impressum; senza tedesco la stima centrale scende a circa 250 €.
7. **Conversione sconosciuta** su acquisti da 2.000-3.000 €: può stare sotto la prudente.

## 5. Le 4 prove

| Prova | Esito | In una riga |
|---|---|---|
| Domanda | **Sì, media** | frasi esatte sulla validità in 5 Paesi, ma metà dei suggerimenti riguarda il prendere la patente in Croazia |
| Dati leggibili | **Sì** | .docx ufficiale 200, 178 titoli, 40 Paesi, riuso ammesso citando la fonte; file spezzato in 96 tabelle e con frasi ambigue |
| Pagatore a cui possiamo iscriverci | **Sì** | SamBoat su Awin (5-8 %), yachting.com (3 %, approvazione immediata), SkipperCity (20 % della loro provvigione, cookie 365 giorni) |
| Nessuno lo fa già meglio | **A metà** | in inglese SkipperCity copre i 6 titoli comuni; liberi: italiano, tedesco con fonte, pagine per titolo, coda lunga |

Tre prove e mezza su quattro: non basta per un sito nuovo, basta per una sezione a costo zero.

## 6. Correzioni al rapporto del ricercatore

- «Circa 230 titoli, 41 Paesi» → 178 righe numerate, 40 Paesi.
- «Italia entro 12 miglia: fino a 24 m e 30 GT» → per il noleggio la riga dice 18 m; 30 GT è per lo yacht privato.
- «SkipperCity: nessun limite» → ha i limiti di 6 titoli comuni e un cercatore.
- «Nessuno dà il limite olandese» → Borrow A Boat in olandese lo dà.
- 18.000 visite e 1.700 € centrali → 4.500 visite e 430 €.
- «Non c'è un sito adatto: meglio dominio nuovo» → Before You Fly è adatto e rende quattro volte di più per ora di lavoro.
