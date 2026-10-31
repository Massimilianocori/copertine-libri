# India e indiani all'estero (NRI): passaporto, OCI, visti, esami, rimesse (31/10/2026)

Angolo assegnato: India e indiani all'estero, in inglese e hindi. Passaporto (Passport Seva Kendra per città e tempi), OCI, visti degli indiani verso Regno Unito, USA, Schengen, Canada e Australia (tempi d'attesa per appuntamento), esami internazionali (IELTS, PTE, TOEFL: date e centri per città), rimesse.

Letti prima: skill `rete-siti`, `REGOLE-FISSE.md` (con le regole del 31/10: fronti nuovi, conta il fatturato, niente lavori a ore di Massimiliano), `ESPLORATE.md` per intero sui temi vicini. **Già chiusi e non rifatti da capo:** passaporto indiano e Paesi senza visto (NO 17/10), tempi di appuntamento Schengen per città (NO 21/10), attese del visto USA per consolato (NO, `travel.state.gov` 403), tempi di consegna dei passaporti per Paese (NO 23/10), tempi del visto turistico canadese (NO 27/10), tempi dei visti australiani (NO 28/10), punteggi IELTS per nazionalità (RISERVA per licenza, 23/10), rimesse per corridoio e tassa dell'1 % sulle rimesse (NO 18/10 e 28/10), guide in hindi/urdu (NO 21/10 e 31/10). Dove tocco uno di questi temi scrivo solo il fatto nuovo.

**Metodo e prove (tutte del 31/10/2026):** `curl` sulle fonti (stato HTTP, dimensione, `Last-Modified`), PDF letti con `pdftotext`; suggerimenti di Google (`suggestqueries.google.com`, `client=firefox`) con lingua e Paese giusti (en/in, hi/in, en/us, en/gb, en/ca, en/au, en/ae, de/de, fr/fr); ricerca web per vedere chi c'è nei risultati (risultati come da un computer negli USA). Nessun blocco aggirato: il portale Passport Seva è un'applicazione JavaScript e non ne ho cercato le interfacce nascoste. Le stime sono stime, non dati: ognuna ha il calcolo.

Voto con la griglia delle ricerche precedenti: domanda 0-3 · buco nei risultati 0-2 · fonte ufficiale leggibile e riusabile 0-2 · valore del pubblico e chi paga 0-2 · rischi e ore 0-1.

Formula delle stime: visite al mese a 18 mesi × 12 × € ogni 1.000 visite ÷ 1.000. Riferimento AdSense del cruscotto (30/10): 6-10 € ogni 1.000 visite in inglese da USA e Regno Unito, 3-5 € in italiano; stima per lettori in India 1-3 € (finanza e tasse verso l'alto, hindi verso il basso). Nessun dato nostro: AdSense non ha ancora incassi.

---

## 0. Risposta in breve

**Nessuna idea passa l'asticella dei siti nuovi** (voto ≥ 7 e ≥ 5.000 €/anno nel caso centrale). Una sola arriva a 7, come sezione di un sito esistente.

| # | Idea | Dove | Voto | Prudente / centrale / ottimista €/anno a 18 mesi | Ore | Chi paga |
|---|---|---|---|---|---|---|
| 1 | **Visto elettronico per l'India: costo per nazionalità e tipo, porti, visto all'arrivo, e-Arrival card** (tabella ufficiale dell'8/9/2026, 172 Paesi) | sezione Before You Fly | **7** | 130 / 480 / 1.870 | 10-14 | AdSense USA/UK/DE, assicurazione viaggio, eSIM |
| 2 | Servizi consolari indiani all'estero per sede: rinnovo del passaporto, OCI, certificato di rinuncia, PCC (costi con ICWF e VFS, documenti) | sezione Visa Income | 6 | 110 / 400 / 1.340 | 20-30 | AdSense USA/UK/CA/AU, Wise |
| 3 | Cambio ufficiale per le tasse indiane: SBI TT buying rate e tasso di riferimento RBI giorno per giorno (redditi esteri, RSU, quadro FA al 31/12) | nessun sito adatto: RISERVA | 6 | 40 / 180 / 720 | 8-12 | AdSense India (finanza) |
| 4 | Disponibilità degli appuntamenti Passport Seva Kendra per città (anche in hindi) | – | 3 NO | – | – | – |
| 5 | Tempi d'attesa dei visti per gli indiani per consolato o centro VFS (USA, UK, Canada, Australia, Schengen) | – | 3,5 NO (confermato) | – | – | – |
| 6 | Date e centri IELTS / PTE / TOEFL per città indiana | – | 3,5 NO | – | – | – |
| 7 | Oro da Dubai all'India: franchigia e dazio (Baggage Rules 2026) | – | 4,5 NO | – | – | – |
| 8 | Rimesse verso l'India: miglior cambio, limiti, rimesse per Stato | – | 3 NO (confermato) | – | – | – |
| 9 | Costo del visto USA in rupie (cambio consolare) | – | 3,5 NO | – | – | – |

**Lezione del giro.** Dentro questo angolo il pubblico che vale (lettori da USA, Regno Unito, Germania) non è l'indiano in India ma **chi va in India** (idea 1) e **l'indiano che vive negli USA o nel Regno Unito** (idea 2). Le domande più grandi degli indiani in India (appuntamenti per il passaporto, attese dei visti, date degli esami) hanno tutte la stessa forma: **il dato ce l'ha l'ente dentro il suo sistema** (Passport Seva in JavaScript con captcha, VFS 403, `travel.state.gov` 403, `canada.ca` senza risposta, IDP e Pearson con il proprio motore di ricerca delle date). È la stessa lezione del 23/10 ("le domande *quanto ci vuole per X* sono dell'ente"), confermata sull'India.

**Fatto nuovo utile subito (idea 1):** il governo indiano ha pubblicato l'8/9/2026 una tabella dei costi del visto elettronico per nazionalità (PDF modificato sul server il 30/10/2026) con cifre diverse da quelle che si leggono oggi nei risultati di Google: per il Regno Unito il visto turistico di 5 anni costa **484 $** (i primi risultati dicono ancora 80 $), per gli USA **160 $**, e c'è una tabella separata per i visti d'affari e medici (Regno Unito 242 $ e 129 $, USA 140 $ e 100 $). È il tipo di numero ufficiale preciso che gli assistenti AI citano.

---

## 1. Visto elettronico per l'India: costo per nazionalità e tipo — voto 7, SEZIONE di Before You Fly

**L'idea in una riga.** Una pagina per nazionalità ("India e-Visa fee for UK citizens", 172 Paesi) con il costo ufficiale di ogni tipo di visto elettronico (turistico 30 giorni in bassa e alta stagione, 1 anno, 5 anni; affari; medico e accompagnatore medico), il 3 % di commissione bancaria, i Paesi gratuiti, il visto all'arrivo (solo Giappone, Corea del Sud e in parte Emirati), i 33 aeroporti e i porti per le crociere ammessi, e la e-Arrival card obbligatoria 72 ore prima. Calcolatore: nazionalità + tipo + mese di viaggio → costo totale in dollari, sterline ed euro (cambi BCE).

**Fonte ufficiale (verificata con curl).**
- `https://indianvisaonline.gov.in/evisa/images/Etourist_fee_final.pdf`: **200**, PDF di 561 KB, `Last-Modified: Fri, 30 Oct 2026 11:39:36 GMT`, testo leggibile, intestazione "Country/Territory Wise e-Tourist Visa Fee (in US $)", firmato "08-September-2026", **172 righe**. Lettura fatta: valore normale 10 / 25 / 40 / 200 $ (30 giorni aprile-giugno / 30 giorni luglio-marzo / 1 anno / 5 anni); **Regno Unito 10 / 25 / 40 / 484 $**, Gibilterra, Guernsey, Jersey, Isola di Man uguali al Regno Unito; **USA 10 / 25 / 40 / 160 $**; Giappone 10 / 25 / 25 / 25; Sri Lanka 10 / 25 / 25 / 25; Singapore 10 / 25 / 25 / 200; Sudafrica 0 / 0 / 25 / 25; Russia 0 / 0 / 40 / 120; Mozambico 5 anni 220 $; gratuiti del tutto Argentina, Indonesia, Giamaica, Mauritius, Mongolia, Myanmar, Seychelles, Uruguay e le isole del Pacifico; nota "Bank charge of 3% will be charged additional".
- `https://indianvisaonline.gov.in/evisa/images/eTV_revised_fee_final.pdf`: **200**, `Last-Modified: 30 Oct 2026 11:39:38 GMT`, "Country/Territory Wise e-Visa Fee (e-Business, e-Medical, e-Medical Attendant and e-Conference Visa)": normale 120 / 80 / 80 $; **Regno Unito 242 / 129 / 129**, **USA 140 / 100 / 100**, **Australia affari 215 $**, Bangladesh medico 0.
- `https://indianvisaonline.gov.in/evisa/tvoa.html`: **200**, 193 KB, in HTML leggibile: domande frequenti con i 33 aeroporti ("You may arrive at 33 designated Airports…"), i porti per le crociere, il visto all'arrivo solo per Giappone, Corea del Sud ed Emirati (questi ultimi solo se hanno già avuto un visto indiano), la e-Arrival card ("within 72 hours before their arrival… at boi.gov.in or indianvisaonline.gov.in", anche per chi ha la OCI).
- **Aggiornamento:** tabelle cambiate più volte (dicembre 2025, 8/9/2026); si rileggono ogni settimana con la routine e si confronta il PDF (pubblicazione solo se cambia).
- **Licenza:** il portale non ha una pagina di copyright collegata; i siti del governo indiano di solito chiedono il permesso per riprodurre i testi (vedi idea 2, ambasciata di Washington). Qui si pubblicano **cifre** (fatti) in tabelle e testi nostri, con link e data della fonte, come per le altre sezioni: rischio basso ma da scrivere nella pagina "fonti".

**Domanda (autocomplete).**
- en/us "india e visa fee" **10**: "fees for us citizens", "from canada", "for singaporean", "for uk citizens", "for malaysian", "germany", "for canadian citizens", "for 5 years".
- en/gb "india visa cost uk" **10**: "uk citizen", "uk passport", "30 days", "5 years", "e visa cost uk", "transit visa cost uk".
- en/us "india visa for us citizens" **10** (cost, official website, minor, processing time, born in pakistan); en/au "india e visa" **10** (australia, for australian citizen).
- en/us "india business visa fee" **10** (for malaysian, singaporean, cost for us citizens, cost uk, e business visa fee).
- en/us e en/in "india e arrival card" **10** (for oci holders, for us citizens, website not working).
- Altre lingue: de/de "indien visum kosten" **10** ("2026", "kosten euro", "schweiz", "e visum kosten"); fr/fr "visa inde prix" **10** ("e visa inde prix", "belgique", "suisse", "oci visa inde prix"). Possibile seconda fase in tedesco e francese.

**Chi c'è oggi su Google** ("india e visa fees for uk citizens 5 years"): calendar-uk.co.uk (pagine di domande generate), discourse/bluetext (spam), holidify, visasnews, agatetravel, sbnri, immihelp, leverageedu, **visafeecalculator.com** (sito automatico, non raggiungibile da questo server), cgibirmingham.gov.in (visto cartaceo). La sintesi dei risultati dà **80 $** per il visto di 5 anni dei britannici, una fonte dice 84,05 $, un'altra 144,64 $: **nessuno ha i 484 $ della tabella dell'8/9/2026**. Il portale ufficiale è primo per le ricerche generiche ma la tabella è un PDF di 172 righe senza pagina per nazionalità. **Battibile** sulle ricerche "fee for [nazionalità]" e "[tipo] visa fee", e molto citabile dagli assistenti AI (numero ufficiale, data, differenza dalle cifre vecchie).

**Chi paga e quanto.**
- AdSense: lettori da USA, Regno Unito, Canada, Australia, Germania (6-10 € ogni 1.000 visite secondo il cruscotto), ma metà delle nazionalità sono asiatiche e africane (Malesia, Singapore, Bangladesh per i visti medici): media stimata 6-8 €.
- Assicurazione viaggio e eSIM: Before You Fly nasce già con "voli, eSIM" nel cruscotto; nessuna commissione nuova letta oggi per l'India: valore stimato 1-3 € ogni 1.000 visite, **da confermare** con le iscrizioni.
- Esclusi i rivenditori di visti (iVisa e simili): regola del 10/10 sui rivenditori legati al visto, e chi cerca "official website" li vuole evitare.

**Stima a 18 mesi.** Visite al mese 1.500 / 4.000 / 12.000 (172 pagine nazionalità + 4 pagine per tipo + calcolatore; domanda in 5 Paesi ricchi). € ogni 1.000 visite: 7 / 10 / 13 (AdSense 1,5 pagine × 4,5-7,5 € + assicurazione/eSIM 0,5-2 €).
- Prudente 1.500 × 12 × 7 ÷ 1.000 = **126 €** (arrotondo 130)
- Centrale 4.000 × 12 × 10 ÷ 1.000 = **480 €**
- Ottimista 12.000 × 12 × 13 ÷ 1.000 = **1.872 €** (arrotondo 1.870); con tedesco e francese +20-30 %.
- Primi soldi: AdSense dopo l'approvazione, Google in 2-4 mesi; gli assistenti AI prima (la sezione rifiuti di Visa Income ha preso visite da ChatGPT in pochi giorni).

**Ore di costruzione:** 10-14 (lettore dei due PDF con controllo delle 172 righe, pagine per nazionalità con i dati che Before You Fly ha già sull'India dai consigli britannici, canadesi e australiani, calcolatore, routine settimanale che confronta i PDF).

**Rischi.** Cifre che cambiano senza preavviso (proprio il nostro vantaggio, se la routine le rilegge); pagine per nazionalità simili tra loro (si aggiungono i dati propri: stagione, visto all'arrivo, porti, consiglio di viaggio del proprio governo); siti truffa che comprano annunci su "india e visa".

**Voto 7** (domanda 3 · buco 1 · fonte 1,5 · valore 1 · rischi e ore 0,5). **SEZIONE da costruire** in Before You Fly, a costo zero, con guadagno atteso positivo (regola della rete fitta). Sotto l'asticella dei siti nuovi.

---

## 2. Servizi consolari indiani all'estero per sede — voto 6, RISERVA come sezione di Visa Income

**L'idea.** Per ogni ambasciata e consolato indiano nei Paesi ricchi (USA 5-6 sedi, Regno Unito, Canada, Australia, Emirati, Singapore): costo di rinnovo del passaporto (normale, tatkal, 36/60 pagine, minori, smarrito), OCI nuova e riemissione, **certificato di rinuncia (surrender certificate)** dopo la cittadinanza straniera con le penali, certificato penale (PCC), con il contributo ICWF e la tariffa VFS, documenti e indirizzi dei centri.

**Fonti (curl).**
- Ambasciata a Washington `indianembassyusa.gov.in/pages/MjU,` **200**: tabella letta: passaporto normale 36 pagine **125 $ + 2 $ ICWF = 127 $**, 60 pagine 177 $, tatkal 252 $ / 302 $, minori 92 $, PCC 42 $, surrender certificate **40 $ + 3 $ = 43 $**, più **19 $ di VFS**; OCI nuova **275 $ + 3 $ ICWF + 19 $ VFS** (`pages/MjY,` 200). **Incoerenza sulla stessa sede:** la pagina della rinuncia (`extra?id=76`) dice in un punto "US$ 25 plus US$ 3" e in un altro "US$ 40 plus US$ 3".
- Ottawa `hciottawa.gov.in` **200**, Canberra `hcicanberra.gov.in` **200**, Abu Dhabi `indembassyuae.gov.in` **200**, Dubai `cgidubai.gov.in` **200**, San Francisco `cgisf.gov.in` **200**.
- **Chiuse:** Londra `hcilondon.gov.in` **403**, Toronto `cgitoronto.gov.in` **403**, New York `cginewyork.gov.in` **000**, VFS (`services.vfsglobal.com/usa/en/ind/`, `visa.vfsglobal.com/ind/en/gbr/`) **403**; `ociservices.gov.in` 200 ma 677 byte (pagina vuota), `mha.gov.in` 200.
- **Licenza:** ambasciata a Washington, "Copyright policy": *"The contents of this website may not be reproduced partially or fully, without due permission… If referred to as a part of another publication, the source must be appropriately acknowledged."* Si possono dare le cifre con la fonte, non copiare i testi.
- Aggiornamento: pagine HTML diverse per ogni sede, cambiano raramente e senza data.

**Domanda.** en/us "indian passport renewal in usa" **10** (checklist, fees, processing time, timeline); en/gb "indian passport renewal uk" **10** (cost, appointment); en/ca **10** (fees, processing time, vancouver); en/au **10** (fees, tatkal fees); en/ae "indian passport renewal dubai" **10** (al hind, price, appointment); en/us "oci card processing time" **10** (usa, houston, canada, atlanta, uk); en/gb "oci fees uk" **10**; en/us "indian passport surrender" **10** (in usa, fee, houston, after us citizenship); en/us "surrender certificate" **10**.

**Google oggi** ("oci card processing time usa"): visament, usadunia, immihelp (forum), nriway, tripbeam, visaverge, due siti automatici su `pages.dev` (thenriguide, one-dollar-passport-photo), più spam. Tempi senza fonte ufficiale (VFS dice "6-7 settimane dalla ricevuta"). Il buco è la tabella dei costi **per sede, confrontata**, con la data; ma VFS (partner ufficiale) è primo per le ricerche con il nome della città.

**Chi paga.** AdSense con lettori indiani negli USA, Regno Unito, Canada e Australia (stima 6-8 € ogni 1.000 visite); Wise (10 £ per cliente nuovo, già nella lista del 17/10) per chi manda soldi in India: stima 0,2 % di iscrizioni × 11 € = 2 € ogni 1.000 visite. Nessuna altra commissione letta.

**Stima.** Visite al mese 1.000 / 3.000 / 8.000 × 9 / 11 / 14 € → **108 / 396 / 1.344 €/anno** (110 / 400 / 1.340). **Ore** 20-30 (una pagina diversa per sede, controllo a mano delle incoerenze, metà delle sedi più grandi chiuse al server).

**Voto 6** (domanda 3 · buco 1 · fonte 0,5 · valore 1 · rischi e ore 0,5). **RISERVA**: si fa solo se Londra e New York si leggono (prova da GitHub Actions insieme agli altri siti chiusi al server) o come una sola pagina USA (Washington + San Francisco, 4-6 ore) dentro Visa Income.

---

## 3. Cambio ufficiale per le tasse indiane (SBI TT buying rate, RBI) — voto 6, RISERVA

**L'idea.** Una pagina per giorno e per mese con il tasso SBI "TT buying" (quello che la regola 26 delle Income Tax Rules indica per i redditi in valuta, le RSU e i capital gain esteri) e il tasso di riferimento RBI, con le date che contano: ultimo giorno di ogni mese, **31 dicembre** (quadro FA delle attività estere, anno solare) e 31 marzo.

**Fonti.** `https://sbi.bank.in/documents/16012/1400784/FOREX_CARD_RATES.pdf` **200** (PDF giornaliero, letto: "Date 31-10-2026 Time 10:11 AM", "To be used as reference rates", USD/INR TT buy **94,36**, EUR 104,86, GBP 125,56, AED 25,18). SBI **non pubblica lo storico**: c'è solo il PDF del giorno. RBI `rbi.org.in/scripts/ReferenceRateArchive.aspx` **200** (archivio ufficiale con modulo). L'archivio storico completo esiste solo nel progetto GitHub `sahilgupta/sbi-fx-ratekeeper` (dal 2020), **senza licenza** dichiarata: non riusabile. Quindi il nostro storico partirebbe da oggi; il 31/12/2026, che servirà a luglio 2027, si cattura se la lettura giornaliera parte prima di fine anno.

**Domanda.** en/in "sbi tt buying rate" **10** ("as on 31 march 2026", "history", "history pdf", "as on 31 december 2025", "historical data", "for income tax"); en/in "rbi reference rate" **10** ("as on 31st march 2026", "archive").

**Google oggi** ("sbi tt buying rate as on 31 december 2025 usd"): il repository GitHub, Scribd, xflowpay, fogli di banche pakistane; **nessuna pagina pulita per data**. Buco vero.

**Chi paga.** AdSense con lettori in India su un tema di tasse (stima 2-4 € ogni 1.000 visite); nessun programma con commissione letta (piattaforme per azioni USA e servizi di dichiarazione: cifre non lette). Picchi solo a giugno-luglio (dichiarazione) e a fine anno.

**Stima.** Visite al mese (media dell'anno) 1.500 / 5.000 / 15.000 × 2 / 3 / 4 € → **36 / 180 / 720 €/anno**. **Ore** 8-12 (lettore del PDF una volta al giorno, archivio, pagine per data).

**Voto 6** (domanda 2,5 · buco 1,5 · fonte 1 · valore 0,5 · rischi e ore 0,5). **RISERVA**: nessun sito della rete ha questo pubblico (contribuenti indiani). Unica azione utile a costo quasi zero: **salvare il PDF SBI ogni giorno da adesso** (una richiesta al giorno) per avere il 31/12/2026 se un giorno si decide di farlo.

---

## 4. Appuntamenti Passport Seva Kendra per città — NO (3)

Domanda enorme: en/in "passport seva kendra" **10** con le città (Pune, Kolkata, Ghaziabad, Bangalore, Thane, Jaipur, Chandigarh), "psk appointment" **10** ("availability", "availability check"), "passport appointment availability" **10** (Bangalore, Chennai, Mumbai, Pune, Hyderabad, Delhi, tatkal); hi/in "पासपोर्ट" **10** ("पासपोर्ट सेवा", "पासपोर्ट बनाने का खर्चा", "पासपोर्ट स्टेटस"). Ma la fonte non è pubblica: `www.passportindia.gov.in/psp` **200 di 849 byte** (applicazione JavaScript vuota senza browser), `portal2.passportindia.gov.in` **000**, `services1`/`portal1` **000**, la vecchia pagina `apptAvailStatus` **404**; la disponibilità si vede solo dentro il portale, con captcha. Non si aggira. In hindi la pubblicità vale pochissimo e Google traduce già in hindi (lezione del 31/10). **Voto 3** (domanda 3 · buco 0 · fonte 0 · valore 0 · rischi 0).

## 5. Tempi d'attesa dei visti per gli indiani per consolato o centro VFS — NO (3,5), confermato

Domanda conferma: en/us "us visa wait time" **10** (india, chennai, for indians); en/in "us visa appointment wait time" **10** (Delhi, Mumbai, Hyderabad, Chennai, Kolkata); en/in "uk visa processing time" **10** (india, in mumbai); "canada visitor visa processing time" **10** (from india 2026); "australia visitor visa processing time" **10** (from india); "schengen visa appointment" **10** (Mumbai, Delhi, Bangalore, Chennai, Pune). **Nessun fatto nuovo sulle fonti:** `travel.state.gov` **403** (oggi), `canada.ca` JSON dei tempi **000**, VFS **403**, `in.usembassy.gov/visas/` **403**, `ais.usvisa-info.com/en-in/niv` **404**; Home Affairs `global-visa-processing-times` **200** ma solo tempi globali per sottoclasse (già NO il 28/10); gov.uk 200 ma solo lo standard di 3 settimane, non per Paese. Resta valido il TEST "da GitHub Actions" del 17/10 per `travel.state.gov`. **Voto 3,5**.

## 6. Date e centri IELTS / PTE / TOEFL per città indiana — NO (3,5)

Domanda: en/in "pte exam centres in" **10** (Kerala, Hyderabad, Vijayawada, Coimbatore, Vizag, Ahmedabad); "ielts exam date" **10** ("2026 in india", "in october 2026", "2027 in india"). Fonti: `pearsonpte.com/test-centers-and-fees/` **200** (ma ha già il suo motore per città e data), `ielts.org/take-a-test/test-dates` **404**, IDP India (pagina date) **404**; le date si prenotano dentro i sistemi degli enti ("l'ente ha il motore", lezione degli esami nordici del 20/10). Licenze IELTS ed ETS già lette il 23/10: vietano la ripubblicazione. Pubblico in India: pubblicità 1-2 €. Già coperto per il Regno Unito dalla sezione SELT di Visa Income. **Voto 3,5**.

## 7. Oro da Dubai all'India: franchigia e dazio — NO (4,5)

Domanda forte: en/ae "gold limit from dubai to india" **10** ("for tourist visa", "for nri", "2026", "per person"). Fatto: **Baggage Rules 2026**, notifica 14/2026-Customs (N.T.) del 1/2/2026, in vigore dal 2/2/2026 (secondo le testate: gioielli 40 g per le donne e 20 g per gli altri, senza tetto di valore, per chi vive all'estero da più di un anno; franchigia generale 75.000 rupie). Ma: **una regola sola**, già scritta da Khaleej Times, Gulf News, Upstox, Taxscan, Outlook Traveller, taxguru; la parte che cambia (valore tariffario dell'oro ogni 15 giorni) sta su CBIC, **000 da questo server su tutti i sottodomini** (`cbic.gov.in`, `taxinformation.cbic.gov.in`, `old.cbic.gov.in`, `cbic-gst.gov.in`), e `egazette.gov.in` **000**. Nessun pagatore oltre a AdSense Emirati/India. **Voto 4,5** (domanda 3 · buco 0,5 · fonte 0 · valore 0,5 · rischi 0,5).

## 8. Rimesse verso l'India — NO (3), confermato

Domanda: en/ae "send money to india" **10** ma con marche ("tabby", "aspora", "from uae credit card"), en/in "nri remittance" **9** ("limit", "tax", "state wise"). Il tema è già chiuso due volte (18/10 e 28/10): Wise, Remitly, Monito, Ria sono la risposta e hanno i tassi in tempo reale. La sola parte con dati ufficiali (rimesse per Stato indiano dall'indagine RBI) è un numero ogni qualche anno. Al massimo Wise come link nelle sezioni delle idee 1 e 2. **Voto 3**.

## 9. Costo del visto USA in rupie — NO (3,5)

Domanda: en/in "us visa fee in inr" **10** ("us embassy fee in inr", "us visa application fee in inr", "us h1b visa fees in inr"). Una cifra (185 $ al cambio consolare) più la nuova tassa d'integrità; fonti chiuse: `in.usembassy.gov/visas/` **403**, `ais.usvisa-info.com/en-in/niv` **404**, `ustraveldocs.com/in/` 200 di 4,7 KB (rimanda altrove). **Voto 3,5**.

---

## 10. Cambio d'angolo tentato dentro lo stesso tema

Trovate solo idee piccole sugli indiani in India, ho girato l'angolo due volte:
1. **Dal viaggiatore indiano a chi va in India** (idea 1): è il pubblico ricco del tema (USA, Regno Unito, Germania, Francia) e ha un fatto nuovo (tabelle dell'8/9/2026). È l'unica idea da 7.
2. **Dall'indiano in India all'indiano che vive in Occidente** (idee 2 e 3): pubblico che vale di più, ma fonti frammentate per sede (idea 2) o senza sito adatto nella rete (idea 3).

Nessuna delle due strade porta un sito nuovo da ≥ 5.000 €/anno: la somma delle tre sezioni nel caso centrale è circa **1.060 €/anno** (480 + 400 + 180).

## 11. Cosa propongo (in ordine di guadagno per ora)

1. **Idea 1 in coda di costruzione** come sezione di Before You Fly (`/india-e-visa-fee/`), 10-14 ore, con il controllo settimanale dei due PDF. Prima che le cifre vecchie si sistemino nei risultati: il vantaggio è la novità dell'8/9/2026.
2. **Idea 2 ridotta** a una pagina USA (Washington e San Francisco, 4-6 ore) dentro Visa Income, segnalando l'incoerenza 25/40 $ sulla rinuncia; il resto solo se Londra e New York si leggono da GitHub Actions.
3. **Idea 3**: solo il salvataggio giornaliero del PDF SBI (costo quasi zero) per non perdere il 31/12/2026; decisione sulla pagina dopo il verdetto di fine anno sui siti.

Nessun messaggio a Massimiliano: nessuna idea supera l'asticella dei siti nuovi.

## Fonti lette (31/10/2026)
- https://indianvisaonline.gov.in/evisa/images/Etourist_fee_final.pdf (200, Last-Modified 30/10/2026, firmato 08-September-2026)
- https://indianvisaonline.gov.in/evisa/images/eTV_revised_fee_final.pdf (200, Last-Modified 30/10/2026)
- https://indianvisaonline.gov.in/evisa/tvoa.html (200)
- https://indianembassyusa.gov.in/pages/MjU, ; https://indianembassyusa.gov.in/pages/MjY, ; https://indianembassyusa.gov.in/extra?id=76 ; https://indianembassyusa.gov.in/footer_pages?id=1 (200)
- https://sbi.bank.in/documents/16012/1400784/FOREX_CARD_RATES.pdf (200) ; https://www.rbi.org.in/scripts/ReferenceRateArchive.aspx (200)
- https://raw.githubusercontent.com/sahilgupta/sbi-fx-ratekeeper/main/README.md (200, progetto senza licenza)
- https://www.pearsonpte.com/test-centers-and-fees/ (200)
- Chiuse o vuote: passportindia.gov.in (app JS 849 byte; portal1/portal2/services1 000), travel.state.gov 403, canada.ca 000, VFS 403, hcilondon 403, cgitoronto 403, cginewyork 000, CBIC (tutti i sottodomini) 000, egazette 000, incometaxindia 403, in.usembassy.gov 403, data.gov.in 000.
- Risultati di ricerca consultati (composizione della prima pagina): calendar-uk.co.uk, holidify.com, sbnri.com, immihelp.com, visasnews.com, visafeecalculator.com, cgibirmingham.gov.in; visament.com, nriway.com, visaverge.com, thenriguide.pages.dev; khaleejtimes.com, gulfnews.com, upstox.com, taxscan.in; github.com/sahilgupta/sbi_forex_rates, scribd.com, xflowpay.com.
