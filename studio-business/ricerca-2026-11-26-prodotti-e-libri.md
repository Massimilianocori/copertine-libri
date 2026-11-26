# Ricerca del 26/11/2026: prodotti nostri e libri dai dati dei siti

Solo ricerca. Nessun sito toccato. Nessun commit.
Regola usata: ogni numero ha una fonte. Dove il dato manca c'è scritto **manca** o **ipotesi**.

## In breve

- **Nessuna idea passa 7 su 10 oggi.** Il motivo è uno: le visite sono poche e i punteggi dei libri sono provvisori senza BookBeam.
- La migliore idea nuova è un **libro in inglese per il nuovo esame B2 della residenza nel Regno Unito** (regola dal 26/3/2027). Voto provvisorio 6,5. Può salire a 8-9 con le foto BookBeam.
- Il **kit di prove B1** rende di più per ora di lavoro, ma è fermo per due motivi: la regola «niente vendita diretta» del 13/11 e il dubbio fiscale. La forma senza dubbio fiscale è un secondo libro KDP.
- Dato nuovo e scomodo: la nicchia dei libri B1 si sta riempiendo. In una sola pagina di ricerca ci sono **16 titoli, tutti usciti tra luglio e novembre 2026**.
- Fuori da EsameB1 nessun sito ha abbastanza visite per un prodotto.
- In fondo ci sono le **3 opportunità migliori, ognuna con una prova di 2 settimane, una soglia e una regola di stop**.

## Come ho preso i dati

- **GoatCounter**, API pubblica `stats/hits`, paginazione con `exclude_paths`, una chiamata ogni 1,5 secondi. Due periodi: 29/10-25/11 (28 giorni, 4.860 visite, 1.367 pagine) e 19-26/11 (8 giorni, il 26/11 non è finito). Lette il 26/11/2026 mattina.
- **Suggerimenti di Amazon** (amazon.it e amazon.co.uk) e **di Google** (Italia e Regno Unito): 41 inizi di frase. Dicono che una ricerca esiste. Non dicono quante volte.
- **Pagine dei prezzi** di Gumroad, Lemon Squeezy, Polar e Paddle: lette oggi.
- **Trinity College London**, pagina SELT: letta oggi.
- **Ricerca web**: 10 ricerche (concorrenti, Udemy, dati del Ministero dell'Interno britannico).
- **Amazon, limite vero.** Ho letto una scheda di amazon.it (il nostro Kindle) e una pagina di ricerca di amazon.com.au. Poi Amazon ha risposto 503 (pagina anti-robot). Mi sono fermato, non ho aggirato il blocco. Quindi **nessun BSR dei concorrenti è stato letto oggi**. Uso i BSR di BookBeam del 6/11 scritti nel cruscotto.
- **Volumi di ricerca** (strumento seodata): non usato in questo turno. I volumi citati vengono dal file `ricerca-2026-11-26-esameb1-stagione.md`.
- **Non trovati nel repo**: `studio-business/BRIEF-RICERCA.md` (esiste solo in `intelaiatura/`, letto) e la cartella `claude/` con i tre file KDP. Il metodo KDP l'ho preso da REGOLE-FISSE e dal cruscotto.

## Due regole del repo che toccano questa ricerca

1. **«Niente vendita diretta» (Massimiliano, 13/11/2026).** Senza Camera di Commercio non si vendono prodotti nostri. Si guadagna con pubblicità, affiliazioni e libri KDP. Quindi ogni prodotto venduto con una piattaforma di pagamento è una **proposta da approvare**, non un lavoro da avviare.
2. **«Niente commercialista» (15/11/2026).** Il brief di oggi chiede la formula «da confermare col commercialista». Massimiliano non ne ha uno. In questo file «da confermare» vuol dire: interpello gratuito all'Agenzia delle Entrate, oppure assistenza dell'Agenzia o CAF. Io non sono un consulente fiscale.

---

# PARTE 0 — I numeri di partenza

## 0.1 Visite per sito, 28 giorni (29/10-25/11)

Host vecchio e nuovo sommati.

| Sito | Visite in 28 giorni | Sezione più vista |
|---|---|---|
| EsameB1 | 1.906 | `/citta/` 781, `/esempi/` 431, home 252 |
| Visa Income | 1.272 | rifiuti dei visti 453, cerimonie australiane 193, test d'inglese UK 150 |
| Before You Fly | 1.014 | `/available-in/` 355, liquidi 143 |
| Paga CCNL | 157 | multiservizi 53, logistica 49 |
| Cruise | 124 | navi 52 |
| Tourist Tax | 105 | Francia 27 |
| Aste in Chiaro | 99 | Roma 17, auto all'asta 11 |
| Italy Strikes | 79 | – |
| Payroll Tax by State | 58 | – |
| FHA, FloodCost, EsamiDiStato, Inflation, Quiz, ATECO | 16, 13, 8, 5, 2, 1 | – |

## 0.2 L'imbuto del libro B1 (19-26/11, 8 giorni)

| Passo | Numero | Fonte |
|---|---|---|
| Visite a EsameB1 | 430 | GoatCounter |
| Di cui su `/esempi/` | 174 | GoatCounter |
| Clic sul libro | 6 (home 4, esempi 1, altre pagine 1) | eventi `clic/libro-*` |
| Visite alla pagina dell'audio del libro | 0 in 28 giorni | GoatCounter |
| Copie vendute | 2 dal 15/11 | dato di Massimiliano |

- 2 copie in 11 giorni sono 0,18 copie al giorno. Su un anno: circa 66 copie, circa 370 €.
- Ogni stima qui sotto parte da questo numero vero, non dalle stime dell'11/11 (470 copie l'anno).

## 0.3 Il nostro libro su Amazon (scheda Kindle letta oggi)

- Kindle a **6,99 €**, dentro Kindle Unlimited («0,00 € o 6,99 €»). Cartaceo 14,99 € (mostrato a 14,41 €).
- Posizione: n. 932 in Grammatica, n. 5.405 in Studio e riferimento linguistico. La posizione generale non compare.
- **Conseguenza:** Kindle Unlimited chiede l'esclusiva dell'ebook. Lo stesso testo non si può vendere altrove (Gumroad, Kobo, Google Play). Un kit deve avere contenuti diversi dal libro.
- Il compenso a copia nel repo ha due valori: 5,64 € e 6,35 €. Uso 5,64 €.

## 0.4 La nicchia B1 si riempie (dato nuovo)

Ricerca «esame b1 cittadinanza simulazioni» su amazon.com.au, prima pagina, 26/11/2026:

- 16 titoli. **Tutti e 16 usciti tra il 16/7 e il 15/11/2026.** Uno è il nostro.
- Recensioni: 12 titoli a 0, due a 1, uno a 2.
- Concorrente diretto del kit: «Esame B1 Cittadinanza: Dieci simulazioni complete con audio» (B1 Cittadinanza Edizioni, 11/9/2026): 0 recensioni dopo 2 mesi e mezzo. Ha anche l'edizione spagnola.
- Altri: Edizioni Docente (3 titoli: PLIDA, CERT.IT, CELI), Giovanni Coletta (2), «Prova orale: 40 dialoghi» (Laura Bianchi, 12/11), «Prova scritta: l'email» (Olga Grunskaya, 21/8), una guida per arabofoni (23/10).
- Limite: è il negozio australiano. I titoli e le date sono gli stessi di amazon.it. Le posizioni italiane **mancano**.
- BookBeam del 6/11 (cruscotto): Percorso CILS 7-14 copie al giorno, Loescher 8-16, Diego J.S. «Parlare e scrivere» 2-4. Un solo autopubblicato sotto il n. 20.000.

Lettura: la domanda c'è, ma gli arrivi nuovi sono molti e quasi tutti senza recensioni. Un secondo titolo nostro prende una fetta piccola.

---

# PARTE A — Prodotti nostri dove il traffico c'è già

## A1. Kit «6 prove complete B1 con audio e correzioni» venduto con una piattaforma (voto 5)

**Cosa.** 6 prove nuove scritte da noi, PDF più MP3, chiavi commentate, griglia per correggere la prova scritta. Prezzo 9,90 €.

**Domanda.**
- `/esempi/` 431 visite in 28 giorni, 174 negli ultimi 8. Il 67 % arriva da ChatGPT (file del 25/11).
- Chi arriva cerca i file ufficiali **gratis**. È un pubblico freddo per un prodotto a pagamento.
- Google: «simulazione test cittadinanza italiana b1 pdf» 1.000 ricerche al mese, «test b1 online» 1.300 (file del 26/11).
- Suggerimenti di oggi: «libro simulazioni b1 cittadinanza» 0, «prove esame b1 cittadinanza con audio» 0, «corso online b1 cittadinanza» 2 (uno con «gratis»).

**Concorrenti e prezzi.**
- Percorso CILS Cittadinanza (Ornimi): 16,90 €, 3 prove, audio da scaricare.
- CERT.IT B1 (Hoepli): 20,62 € con MP3.
- Corso intensivo dell'Università di Palermo: 80 € per 18 ore. Corso online generico: 39 €.
- Nessuna simulazione online a pagamento con audio e correzione trovata. Il vuoto dell'11/11 resta.

**Piattaforme che fanno da venditore (merchant of record), lette oggi.**

| Piattaforma | Costo a vendita | Netto su 9,90 € | Note |
|---|---|---|---|
| Gumroad | 10 % + 0,50 $ (30 % se il cliente arriva dal suo mercato) | circa 8,4 € | «We're a Merchant of Record»: gestisce tutta l'IVA dal 1/1/2025 |
| Lemon Squeezy | 5 % + 0,50 $, più 1,5 % fuori dagli USA e costi di bonifico | circa 8,6 € | in trasloco verso Stripe (nota del 31/10) |
| Polar | 5 % + 0,50 $ per i conti nuovi dal 27/5/2026 | circa 8,9 € | pensata per il software |
| Paddle | 5 % + 0,50 $ | circa 8,9 € | chiede approvazione; vieta alcuni temi (nota del 31/10) |
| Payhip | pagina 403, non letta | – | incassa sul conto del venditore: **non adatta** |

Scelta: **Gumroad**. È la più chiara sull'IVA e non chiede approvazione.

**Conto (parte dalle copie vere del libro).**
- Oggi lo 0,27 % delle visite compra il libro (2 copie su circa 750 visite).
- Prudente: 24.800 visite l'anno × 0,15 % = 37 vendite × 8,4 € = 310 €. Tolgo il 20 % che ruba al libro: **250 €**.
- Centrale: 30.000 visite × 0,4 % = 120 vendite × 8,4 € = 1.000 €. Meno il 20 %: **800 €**.
- Le percentuali sono **ipotesi**. La prova in fondo serve a misurarle.

**Ore.** 18-20 degli agenti (6 prove, audio, pagina) più 2 di Massimiliano.

**Cosa deve fare Massimiliano.** Conto Gumroad a suo nome. Metodo di incasso. Modulo fiscale americano per stranieri (W-8BEN). Caricare i file. Nel repo va solo l'indirizzo pubblico del prodotto. Nessuna chiave, email o dato del conto nel repo.

**Fisco (forfettario). Tutto da confermare.**
- Verso il cliente vende Gumroad. L'IVA europea la gestisce Gumroad. Il problema OSS non tocca Massimiliano.
- Massimiliano incassa da una società americana. Probabile fattura senza IVA (art. 7-ter). **Da confermare.**
- Il nodo vero: questo incasso è «utilizzazione di un'opera dell'ingegno» dentro l'attività editoriale 58.19.00 (come KDP), oppure è vendita commerciale (art. 55 TUIR e art. 2195 c.c.)? Nel secondo caso servono Camera di Commercio e Gestione Commercianti, circa 4.600 € l'anno di minimo. Un prodotto da 800 € l'anno andrebbe in perdita.
- Nessuna risposta ufficiale trovata nel repo (`FISCO-PUBBLICITA.md`). La domanda è già scritta in `CAF-domande-2026-10-31.md`. **Senza risposta scritta questo prodotto non parte.**

**Diritti.** Solo prove scritte da noi. Mai i file ufficiali degli enti: quelli restano link alla fonte. I nomi CILS, CELI, PLIDA, CERT.IT si usano solo per descrivere, con la frase «non affiliato agli enti».

**Rischi.** Regola del 13/11. Dubbio fiscale. Pubblico arrivato per file gratis. Una parte delle vendite si toglie al libro.

## A2. Lo stesso kit come secondo libro KDP: «6 prove complete» (voto 5,5)

**Cosa.** Gli stessi contenuti in cartaceo e Kindle. Audio e correzione automatica gratis su una pagina del sito. Nessun dubbio fiscale: sono diritti d'autore come oggi.

**Domanda e concorrenti.** Vedi 0.2 e 0.4. Il libro attuale fa 0,18 copie al giorno. In più: chi ha comprato il primo libro e vuole altre prove.

**Conto.**
- Prudente: 0,07 copie al giorno = 26 copie × 5,64 € = **150 €**.
- Centrale: 0,22 copie al giorno = 80 copie × 5,64 € = **450 €**.
- Più del libro attuale solo se il sito recupera le visite da Google.

**Ore.** 30-40 degli agenti (dentro il limite KDP di 2 titoli a settimana). Massimiliano: pubblicazione KDP, 30 minuti.

**Rischi.** 15 concorrenti nuovi in 4 mesi. Nessun BSR italiano letto oggi. La pagina dell'audio del primo libro ha 0 visite: non sappiamo se chi compra usa il sito.

## A3. Corso «prove B1» su Udemy (voto 4)

- Udemy vende e incassa. All'autore va il 97 % se il cliente arriva dal nostro link e il 37 % se arriva da Udemy (pagina di supporto Udemy, tramite ricerca web).
- La ricerca web non trova un corso Udemy dedicato all'esame B1 di cittadinanza. Il sito Udemy risponde 403: la domanda interna **manca**.
- Le prove a quiz di Udemy non hanno l'audio (**ipotesi**, da verificare): servirebbe un corso video.
- Conto: prudente 80 €, centrale 400 € l'anno. Ore 25-35 più 3 di Massimiliano.
- Stesso dubbio fiscale di A1.

## A4. Edizione con copertina rigida del libro B1 (voto 4)

- Stesso testo, nuova copertina. 2 ore.
- **Ipotesi**: 5-10 % di copie in più. 20-40 € l'anno.
- Rende poco, ma costa quasi niente e non ha rischi.

## A5. Gli altri siti: nessun prodotto oggi

| Sito e sezione | Visite in 28 giorni | Prodotto possibile | Verdetto |
|---|---|---|---|
| Visa Income, test d'inglese UK | 150 | libro B2 per la residenza | **sì, come libro**: vedi B1 |
| Visa Income, rifiuti dei visti | 453 | modelli di lettera per il ricorso | no: è consulenza legale, rischio alto |
| Visa Income, cerimonie australiane | 193 | nessuno: hanno già passato il test | no |
| Before You Fly | 1.014 | nessuno: su Amazon queste ricerche portano a oggetti | no |
| Paga CCNL | 157 | libro sulla busta paga | debole: vedi B4 |
| Aste in Chiaro | 99 | guida all'asta | debole: vedi B5 |
| Cruise, Tourist Tax, Italy Strikes | 124, 105, 79 | nessuno: 0-1 suggerimenti su Amazon | no |

Con 100-150 visite al mese, anche l'1 % che compra fa 1 vendita al mese.

---

# PARTE B — Libri dai dati verificati dei siti

Metodo KDP: voto 9 solo con almeno 3 libri **indipendenti**, usciti negli ultimi 2 anni, con BSR sotto 20.000.
Oggi nessun BSR è leggibile. **Tutti i voti sono provvisori fino alle foto BookBeam di Massimiliano.**

## B1. «B2 English Speaking & Listening for ILR 2027» (voto provvisorio 6,5)

**Da dove nasce.** Dai nostri dati: `visaincome/dati/selt.json` riporta la regola HC 1691. Dal 26/3/2027 chi chiede la residenza nel Regno Unito deve avere il **B2 di parlato e ascolto**. Prima bastava il B1.

**Fatto nuovo di oggi.** Trinity ha già l'esame: **GESE Grade 7 (B2), 170 £**, «for ILR applications made on or after 26 March 2027» (pagina SELT di Trinity). Il 12/11 questo esame non risultava: per questo l'idea era stata scartata. Durata 15 minuti, tre fasi: argomento, fase interattiva, conversazione.

**Domanda.**
- 199.628 concessioni di residenza nell'anno fino a giugno 2026, +24 % (Ministero dell'Interno britannico, tramite ricerca web). Non tutti fanno l'esame: sono esentati i cittadini di Paesi anglofoni e chi ha una laurea in inglese. I 38.373 con visto BN(O) restano al B1.
- Google UK, «b2 english test for ilr»: **10 suggerimenti su 10** (sample, practice, 2027, questions, fees).
- Amazon UK, «b2 english test»: **10 su 10, tutti di libri** («b2 english test book 2026 trinity», «practice book», «trinity question bank»).
- «gese grade 7» su Google: 10 su 10 (topic form, conversation questions, interactive prompts).
- La nostra sezione `/uk-english-test/`: 150 visite in 28 giorni, sparse su 85 pagine.

**Concorrenti.**
- Trinity: guide e esempi **gratis** sul suo sito.
- Global ELT, «Preparing for Trinity ISE II»: è un altro esame (4 abilità), libro del 2015 ristampato.
- Heather Batyski, «Trinity GESE B1 (Grade 5) Exam Preparation Guide» (8/2025, 5 recensioni il 12/11): è il gemello B1.
- La ricerca web **non trova** un libro «GESE Grade 7 per la residenza 2027». Su Amazon non ho potuto controllare. È un'**ipotesi di vuoto**, non una prova.

**Conto.** Prezzo 11,99 £, compenso circa 5,7 € a copia (formula del 12/11, da ricontrollare nel calcolatore KDP).
- Prudente: 0,2 copie al giorno = 73 copie = **400 €**.
- Centrale: 0,7 copie al giorno = 255 copie = **1.450 €**.
- Il numero centrale è un'**ipotesi**. Si verifica con il BSR dei libri B1 di oggi (gemelli).

**Ore.** 40-60 degli agenti: struttura dell'esame dalla specifica ufficiale, argomenti e domande nostre, dialoghi modello, audio sul sito. Massimiliano: foto BookBeam (10 minuti) e pubblicazione (30 minuti).

**Tempo.** Vale se esce entro fine gennaio 2027. Dopo arrivano gli altri.

**Diritti.** Nessun testo, domanda o esempio di Trinity copiato. Solo materiale nostro. Nome dell'esame usato per descrivere, con «non affiliato a Trinity College London».

**Rischi.** Materiale ufficiale gratuito. Gli editori (Global ELT, Express) possono uscire presto. L'esame è orale: il libro deve avere audio buono. Le date della regola possono cambiare: rileggere GOV.UK prima di scrivere.

**Seguito possibile.** Lo stesso lettore deve fare anche il test Life in the UK (idea del 12/11, voto 5,5). Si valuta solo se questo libro vende.

## B2. Collana B1, secondo titolo «prove complete»

È l'idea A2. Voto 5,5. 150 / 450 € l'anno. 30-40 ore.

## B3. «CILS B2: prove complete con audio» (voto 5)

- Domanda: Amazon.it «cils b2» 5 suggerimenti (anche «2026»). Google «cils b2 prove» 10 su 10 (PDF, soluzioni, orale).
- Sul sito: `/esempi/b2/` 18 visite in 11 giorni, 17 da ChatGPT.
- Concorrenti: **non letti** (Amazon bloccato).
- Conto: prudente **100 €**, centrale **450 €**. Ore 35-50 (stesso motore del B1).
- Rischio: stessa ondata di autopubblicati del B1. Massimiliano il 13/11: «non preparo libri per vendere 10 copie».

## B4. «La busta paga spiegata» da Paga CCNL (voto 4,5)

- Domanda: Amazon.it «busta paga» 7 suggerimenti («in pratica», «senza segreti», «2026», «libro»).
- Concorrenti: Maggioli «Paghe e contributi 2026», 49 €, per professionisti. I due titoli dei suggerimenti: non letti.
- Noi abbiamo solo i minimi di alcuni contratti. Mancano fisco e contributi verificati (limite già scritto il 12/11).
- Conto: prudente **150 €**, centrale **600 €**. Ore 60-80.
- Rischio: un errore costa soldi al lettore.

## B5. Guida alle aste immobiliari da Aste in Chiaro (voto 3,5)

- Domanda: Amazon.it «aste immobiliari» 4 suggerimenti. Sito: 99 visite in 28 giorni.
- I libri che vendono sono manuali «come si fa». Noi abbiamo gli sconti per provincia, non il mestiere.
- Conto: prudente **50 €**, centrale **300 €**. Ore 60.

## B6. Scartati con il dato

| Idea | Dato | Verdetto |
|---|---|---|
| Codici ATECO | Amazon.it: 0 suggerimenti | no |
| Tassa di soggiorno, scioperi, crociere, visti | 0-1 suggerimenti; nessuno cerca un libro | no |
| Testo dei CCNL | «ccnl» 10 suggerimenti con l'anno, ma chi compra vuole il testo del contratto, che non è nostro | no |
| Esami di Stato | 10 suggerimenti per professione, ma noi abbiamo solo date e sedi; il sito chiude il 1/12 | no |
| Colf e badanti 2027 | NO di Massimiliano del 13/11; `/colf-badanti/` 1 visita in 28 giorni | resta no |
| Test A2, edizione inglese del B1 | NO di Massimiliano del 13/11; nessun dato nuovo che lo cambi | resta no |

---

# CLASSIFICA per € a ora (stima centrale)

| # | Idea | Voto | €/anno prudente / centrale | Ore | €/ora | Può partire oggi? |
|---|---|---|---|---|---|---|
| 1 | A1. Kit prove B1 con Gumroad | 5 | 250 / 800 | 20 + 2 | 36 | **No**: regola del 13/11 e fisco da confermare |
| 2 | B1. Libro B2 per la residenza UK | 6,5 provv. | 400 / 1.450 | 50 + 1 | 28 | Sì, dopo le foto BookBeam |
| 3 | A4. Copertina rigida del libro B1 | 4 | 20 / 30 | 2 | 15 | Sì |
| 4 | A2 = B2. Secondo libro B1 «prove complete» | 5,5 | 150 / 450 | 35 + 0,5 | 13 | Sì, dopo la prova di domanda |
| 5 | A3. Corso Udemy | 4 | 80 / 400 | 30 + 3 | 12 | No: fisco da confermare, domanda non letta |
| 6 | B3. CILS B2 | 5 | 100 / 450 | 42 | 11 | Solo dopo BookBeam |
| 7 | B4. Busta paga | 4,5 | 150 / 600 | 70 | 9 | No: mancano i dati di fisco e contributi |
| 8 | B5. Aste | 3,5 | 50 / 300 | 60 | 5 | No |

Somma centrale delle prime quattro senza doppioni (A1 e A2 sono lo stesso contenuto): circa **2.000-2.700 € l'anno**.

**Detto chiaro:** nessuna passa 7 su 10 con i dati di oggi. La prima in classifica è ferma per regole e fisco. La seconda dipende da un dato che può dare solo BookBeam. Per questo la ricerca non chiude con un «no»: chiude con tre prove.

---

# LE 3 OPPORTUNITÀ MIGLIORI, con prova, soglia e stop

## 1ª — Libro «B2 Speaking & Listening for ILR 2027»

- **Perché prima:** obbligo nuovo con data (26/3/2027), esame già in vendita a 170 £, suggerimenti Amazon tutti di libri, nessun libro dedicato trovato.
- **Prova (10 minuti di Massimiliano, entro una settimana):** 4 foto BookBeam su **amazon.co.uk**: «b2 english test book», «trinity gese grade 7», «trinity gese grade 5 b1», «b1 english test book 2026». Le due ricerche B1 misurano i gemelli che vendono già.
- **Seconda prova, gratis (dal 9/12, quando finisce il fermo su Visa Income):** una pagina «GESE Grade 7 per la residenza dal 26/3/2027» con il riquadro «libro in arrivo: avvisami» e contatore dei clic.
- **Soglia per scrivere:** almeno 3 libri indipendenti, usciti negli ultimi 2 anni, con BSR sotto 20.000 tra B1 e B2 (voto 9). Oppure almeno 1 sotto 20.000 e 3 sotto 50.000 (voto 7): si scrive lo stesso, un solo titolo.
- **Soglia per allargare** (Life in the UK, altri enti): 20 copie nei primi 30 giorni.
- **Stop:** nessun indipendente sotto 50.000. Non si scrive. Resta solo la pagina gratuita.
- **Scadenza:** decisione entro il 10/12, libro fuori entro il 31/1/2027.

## 2ª — Kit di prove B1 (prima come prova di domanda, poi come libro o prodotto)

- **Prova (14 giorni, dal 27/11 al 10/12; copre l'esame CILS del 3/12):** un riquadro onesto sulle pagine `/esempi/`: «6 prove nuove con audio e correzione, 9,90 €. In preparazione: lasciami l'email». Usa il modulo `avvisami` che c'è già. Un evento GoatCounter conta i clic. Nessuna vendita, quindi nessun nodo fiscale.
- **Visite attese:** circa 300 su `/esempi/` in 14 giorni (174 negli ultimi 8).
- **Soglia per costruire:** almeno 3 clic ogni 100 visite **e** almeno 12 email.
- **Dopo la soglia:** si costruisce come **secondo libro KDP** (A2), che non ha dubbi fiscali. La vendita con Gumroad (A1) si propone a Massimiliano solo con una risposta scritta sul fisco e con il suo sì, perché oggi la regola del 13/11 la vieta.
- **Soglia per allargare:** 15 copie nei primi 30 giorni. Allora si fa anche il titolo sulla prova orale.
- **Stop:** meno di 1 clic ogni 100 visite, oppure meno di 4 email in 14 giorni. Non si costruisce. Le pagine dei file ufficiali restano come sono.
- **Dato che serve comunque:** copie KDP al giorno dal 15/11, cartaceo e Kindle (10 minuti di Massimiliano).

## 3ª — «CILS B2: prove complete con audio»

- **Perché terza:** riusa il motore del B1, costa 35-50 ore, ma la domanda è piccola.
- **Prova (2 settimane):** 2 foto BookBeam su amazon.it («cils b2», «italiano b2 esame»). In più il riquadro «libro B2 in arrivo: avvisami» su `/esempi/b2/` con contatore.
- **Soglia:** 3 indipendenti recenti sotto 20.000 (voto 9). Oppure 1 sotto 20.000 **e** `/esempi/b2/` sopra 50 visite a settimana (è la stessa soglia fissata il 25/11 per il libro A2).
- **Stop:** nessuna delle due. Non si scrive. La pagina `/esempi/b2/` resta, perché porta visite da ChatGPT.

## Cosa deve fare Massimiliano, in tutto

1. 6 foto BookBeam (4 su amazon.co.uk, 2 su amazon.it): 15 minuti.
2. Copie KDP al giorno dal 15/11: 10 minuti.
3. Dire sì o no al riquadro di prova sulle pagine `/esempi/` (è una modifica piccola al sito, senza vendita).
4. Niente altro, finché le prove non danno i numeri.

## Cosa resta incerto

1. Tutti i BSR: nessuno letto oggi. Amazon ha bloccato dopo due pagine.
2. Quanti clic sul libro diventano copie: 6 clic e 2 copie sono troppo pochi per dirlo.
3. Se esiste già un libro per il GESE Grade 7: la ricerca web non lo trova, Amazon non l'ho potuto guardare.
4. Il trattamento fiscale di un prodotto venduto da una piattaforma: nessuna risposta ufficiale.
5. Quante persone faranno davvero l'esame B2: il totale delle residenze è noto (199.628), la quota esentata no.

## Fonti lette il 26/11/2026

- GoatCounter `rete-siti`, `stats/hits` (due periodi).
- amazon.it, scheda B0HQ2TTHPY; amazon.com.au, una pagina di ricerca.
- `completion.amazon.it` e `completion.amazon.co.uk`; suggerimenti di Google (Italia e Regno Unito).
- gumroad.com/pricing, lemonsqueezy.com/pricing, polar.sh/resources/pricing, paddle.com/pricing (200); payhip.com/pricing e supporto Udemy (403, non letti).
- trinitycollege.com/selt.
- Ricerca web: GOV.UK «Immigration system statistics, year ending June 2026»; supporto Udemy «Instructor revenue share»; italiano-bello.com (Percorso CILS); hoeplieditore.it (CERT.IT B1); unipa.it (corsi CILS); fiscoetasse.com (Paghe e contributi 2026).
- Nel repo: `REGOLE-FISSE.md`, `DA-PUBBLICARE.md` riga 80, `ricerca-2026-11-25-asset.md`, `ricerca-2026-11-26-esameb1-stagione.md`, `intelaiatura/fronti-2026-11-12-libri-dai-siti.md`, `intelaiatura/fronti-2026-11-11-pagatori-alti.md`, `intelaiatura/fronti-2026-10-31-prodotti.md`, `FISCO-PUBBLICITA.md`, `CRUSCOTTO-RETE.md`, `visaincome/dati/selt.json`.

## VERDETTO del 26/11 con le 4 foto BookBeam di Massimiliano (amazon.co.uk)

| Ricerca | Concorrenti | BSR medio | Migliori BSR (età, editore) |
|---|---|---|---|
| b2 english test book | 288 | – | B2-C1 Vocabulary 66.741 (2a 5m); Cambridge B2 First Complete Practice PLUS 79.216 (9 mesi, autopubblicato, Kostas Pan, sponsorizzato); Pass the B1 English Test 73.238 (9 anni, How2become); Collins Speaking B2 116.079 (12 anni) |
| trinity gese grade 7 | 101 | 728.523 | libri d'esame tutti tra 658.000 e 937.000; sotto 50.000 solo libri di musica Trinity (fuori tema) |
| trinity gese grade 5 b1 | 43 | 1.030.195 | Heather Batyski, guida GESE B1 (1a 3m, autopubblicata) 171.471; il resto sopra 800.000 |
| b1 english test book 2026 | 64 | 980.690 | Pass the B1 English Test (ILR, How2become, 9 anni, 255 recensioni) 73.238; Pass the B1 Speaking and Listening 130.363; LanguageCert SELT B1 (2 mesi) 253.819; DK English for Everyone 32.798 (generico) |

**Regola KDP:** voto 9 = 3 indipendenti recenti sotto 20.000; voto 7 = 1 sotto 20.000 e 3 sotto 50.000. **Nessun libro sotto 50.000 in tema** → regola di stop: **il libro B2 per l'ILR NON si scrive adesso** (voto 4,5).

**Cosa dicono i dati:** la domanda per i libri d'esame per la residenza c'è ma è piccola. Il libro di riferimento per il B1 (How2become, 9 anni) sta a 73.238, circa 1 copia al giorno o meno su amazon.co.uk. Le guide GESE non vendono (sopra 650.000). Il cambio B1 → B2 del 26/3/2027 sposterà quella domanda, ma oggi non ci sono ricerche B2 per l'ILR che vendono.

**Ricontrollo:** 15/2/2027 con le stesse 4 ricerche più «b2 english test ilr» e «languagecert b2». Si riapre solo se un libro B2 per l'ILR o per la residenza scende sotto 50.000. Promemoria in DA-PUBBLICARE.md.
