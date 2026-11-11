# Fronte: nautica da diporto e camper, partendo da chi paga (sera dell'11/11/2026)

**Domanda del giro.** Nei settori mai toccati (barche, camper, sci, matrimoni all'estero, studio all'estero) c'è un pagatore che paga molto per un cliente E un dato ufficiale che risponde a una domanda frequente e mal servita?

**Risposta breve: un'idea da coda con vuoto dimostrato (voto 5,5), nessuna a 7.** Il pagatore più alto letto oggi è il **noleggio di barche: circa 100-150 € a prenotazione** (tre programmi letti, tutti europei). Il dato ufficiale che gli sta accanto esiste ed è leggibile: **la tabella del ministero croato delle patenti nautiche straniere riconosciute** (41 Paesi, circa 230 titoli, aggiornata al 21/5/2026), con per ogni titolo che cosa si può condurre e fin dove. I concorrenti copiano l'elenco dei nomi ma non i limiti, e uno dà due risposte in contrasto con la tabella. Il limite dell'idea: i concorrenti sono gli stessi che pagano (i noleggiatori scrivono le loro guide), e uno di loro ha già l'elenco aggiornato in inglese.

Metodo: partenza dalle pagine pubbliche dei programmi (profili Awin `ui.awin.com/merchant-profile/<id>`, pagine "affiliate" dei siti), poi dato ufficiale, poi autocomplete Google nel Paese giusto, poi lettura dei concorrenti. Tutto letto l'11/11/2026 con curl dal server; dove scrivo "ricerca web" è il riassunto dei risultati, usato solo per trovare gli indirizzi. Cambio: 1 £ = 1,15 €. Parole cercate prima in `ESPLORATE.md`: matrimoni, wedding, student, erasmus, traslochi, patente nautica, barca, charter, yacht, skipper, sci, camper, motorhome, camping. Già esplorati e non ripetuti: esame PER spagnolo, patente nautica USA/Canada, ormeggi, date esame patente nautica in Italia, lunghezza camper nei campeggi USA, freedom camping in Nuova Zelanda, alloggi per studenti, budget matrimonio.

Nota sulla regola del 7/11 (niente più viaggi e turismo): la nautica era fra i settori nuovi ammessi il 7/11; il camper è al confine con i viaggi e infatti non passa.

## 0. I pagatori letti (il fatto nuovo del giro)

| Pagatore | Rete | Cifra letta sulla pagina | A cliente | Possiamo entrare? | Indirizzo |
|---|---|---|---|---|---|
| **SamBoat** (noleggio barche, 50.000 barche) IT, UK, US, DE | Awin (ci siamo già) | "commissioni comprese tra il 5% e il 8% sulle vendite", cookie 30 giorni | 45-240 € (noleggio da 900 a 3.000 €) | Sì, programmi IT 32681, UK 32677, US 32679 | ui.awin.com/merchant-profile/32681 |
| **yachting.com** (charter, Rep. Ceca) | diretto | "Get 3% commission on sales", "earn an average of 100 euros per order" | ~100 € | Da chiedere (pagina aperta, UE) | yachting.com/en-gb/affiliate-program |
| **SkipperCity** (charter in Croazia) | diretto | 20 % della loro provvigione, fino al 25 %; esempio scritto: "600 € ... 120 € is yours" | ~120-150 € | Da chiedere | skippercity.com/yacht-charter-affiliate-program/ |
| **Bootsschule1** (corsi online per la patente nautica tedesca, radio SRC) | Awin | "bis zu 8%", "dreistellige Warenkorbwerte", cookie 120 giorni | 16-40 € | Sì, Awin 44985 | ui.awin.com/merchant-profile/44985 |
| **Le Boat DE** (case galleggianti senza patente) | Awin | "2 % Provision auf bestätigte Buchungen", cookie 364 giorni | ~30-50 € (stima su 1.500-2.500 €) | Sì, Awin 128185 | ui.awin.com/merchant-profile/128185 |
| **SailTies** (buoni regalo per corsi di vela, 850-1.500 £) | Awin | "10% commission on every voucher sale" | fino a 100-170 € | Sì, Awin 131417 | ui.awin.com/merchant-profile/131417 |
| **CamperDays** (noleggio camper) DE, NL | Awin | "3% Provision pro Buchung (ø 105 EUR)" + 6 € a richiesta (DE), 8 € (NL) | **105 € a prenotazione** | Sì, Awin 52889 (DE), 52891 (NL) | ui.awin.com/merchant-profile/52889 |
| Motorhome Republic | diretto | "up to 8%", prenotazione media oltre 800 NZD | ~35 € | già letto il 31/10 | motorhomerepublic.com/affiliates |
| Manawa DE (attività all'aperto) | Awin | "8 % Provision", carrello medio 250 € | 20 € | Sì, Awin 113290 | ui.awin.com/merchant-profile/113290 |

Non letti (pagine 404/403 da qui, non insistito): Click&Boat (ricerca web: su Impact, cifra non confermata), Zizoo, Sailogy, Boataround (405), Nautal (403), Indie Campers, Yescapa, roadsurfer (profilo Awin 76432 esiste, cifra non scritta), PaulCamper (ricerca web: passato a Partnerize).

Conclusione sui pagatori: **barche e camper pagano 100 € e più a prenotazione, come AnchorLess, ma su acquisti rari e cari** (cookie 30 giorni, decisione lunga). Servono pagine lette da chi sta per prenotare.

## 1. Classifica

| # | Idea | Voto | Prudente / centrale / ottimista €/anno a 18 mesi | Dove |
|---|---|---|---|---|
| 1 | "La mia patente nautica vale in Croazia?" titolo per titolo, con i limiti ufficiali | **5,5** | 60 / 1.700 / 14.700 | sito nuovo piccolo (DE, EN, IT), coda |
| 2 | Patente nautica croata (Küstenpatent B) per tedeschi, austriaci, italiani: regole ufficiali | 5 (vuoto non dimostrato) | 40 / 500 / 4.500 | sezione del sito 1, solo dopo |
| 3 | Barca senza patente: limite di potenza per Paese e per lago | 4,5 | 30 / 400 / 4.000 | sezione del sito 1, riserva |
| 4 | Camper oltre 3,5 t: pedaggi, limiti e multe per Paese (tedesco) | 4 | 30 / 250 / 2.000 | NO |

Nessuna passa l'asticella "voto ≥ 7 e ≥ 5.000 € centrali". La 1 ha ottimista ≥ 10.000 € e, per la regola del 10/11 (nessuna soglia minima), entra in coda con il suo rapporto €/ora.

## 2. Idea 1: "La mia patente nautica vale in Croazia?" (voto 5,5)

**Fonte esterna da cui nasce.** Profilo Awin di SamBoat (5-8 % sulle prenotazioni) → qual è la domanda che fa chi sta per noleggiare una barca? → autocomplete: la domanda sulla patente, quasi sempre con "Croazia".

**Il dato ufficiale (prova: leggibile).** Ministero croato del mare, tabella dei titoli stranieri riconosciuti, file Word "TBL- MoU ENG 21-5_26.docx" su mmpi.gov.hr: HTTP 200, 204 KB, letto con uno script semplice. Dentro: **271 righe di tabella, 41 Paesi, circa 230 titoli**. Per ogni titolo quattro colonne: Stato, chi lo rilascia, nome del titolo, **competenza** (che barca, fino a che lunghezza o stazza, in quali acque, e la condizione del certificato radio VHF: presente in 175 righe). Base legale scritta in testa (art. 4 dell'ordinanza su barche e yacht; art. 48 dell'ordinanza del 2020). Il ministero ripubblica la tabella ogni 1-2 anni (versioni trovate: 9/2019, 3/2020, 1/2023, 3/2024, 5/2026). Licenza di riuso non scritta: è un atto pubblico, si citano i fatti con la fonte e la data, non si copia il file.

Esempi letti nella tabella del 21/5/2026:
- Germania, Sportbootführerschein See: barche e yacht a noleggio **fino a 18 m**, acque interne e mare territoriale croato, con certificato radio se a bordo c'è il VHF.
- Italia, patente entro 12 miglia: fino a 24 m **e fino a 30 GT**; senza limiti: fino a 100 GT.
- Regno Unito, RYA "Day Skipper Shorebased Certificate" (solo teoria) e "Powerboat Level 2": **riconosciuti**, fino a 18 m, mare territoriale.
- Polonia, "Żeglarz jachtowy": solo barche, **fino a 1 miglio dalla costa**.
- Stati Uniti, ASA "Bareboat Chartering" (104): fino a 18 m; NauticEd SLC: fino a 50 GT.

**La domanda (prova: c'è).** Autocomplete Google, numero di suggerimenti:
- Germania: "sportbootführerschein kroatien" 10 (con "in kroatien gültig", "see kroatien anerkannt"), "sbf see kroatien" 7, "sks kroatien" 10.
- Austria: "küstenpatent kroatien" 10, "fb2 kroatien" 6.
- Italia: "patente nautica croazia" 10 (con "patente nautica italiana in croazia", "categoria b"), "la patente nautica italiana è valida in croazia".
- Regno Unito: "rya day skipper croatia" 10 (con "is rya day skipper accepted in croatia"), "icc croatia" 10, "boat licence croatia" 9, "powerboat level 2 croatia" 6, "do you need a licence to hire a boat in" 10 (Grecia, Croazia, Spagna).
- Paesi Bassi: "vaarbewijs kroatië" 10. Stati Uniti: "sailing license croatia" 10.
- Deboli: Polonia 1, Rep. Ceca 1, Ungheria 1, Francia 3, "asa 104 croatia" 0. Quindi le lingue sono tedesco, inglese, italiano, olandese; non polacco né ceco.

**I concorrenti letti (obbligo del 10/11).** Tre siti, tutti noleggiatori o intermediari (cioè anche pagatori), su 5 titoli:

| Titolo | SkipperCity (pagina "Skipper Licences & VHF Certificates for Croatia", 6.300 parole, cita la tabella del 21/5/2026) | PlainSailing ("Minimum qualifications for bareboat chartering") | Borrow A Boat (9 articoli in inglese, 10 in tedesco, 2 in italiano sulle patenti) |
|---|---|---|---|
| SBF See tedesco | nome in elenco, **nessun limite** (0 volte "internal waters", nessun "18 m" accanto al titolo) | nome in elenco, nessun limite | articolo tedesco generico, senza fonte |
| Patente italiana entro 12 miglia | nome in elenco, nessun limite | nome in elenco (solo "<24mt"), nessun limite di stazza | "è riconosciuta": **manca il limite di 30 GT** (riguarda i catamarani grandi) |
| RYA Day Skipper solo teoria | nome in elenco, nessun limite | non distingue teoria e pratica | **"Not accepted on their own: theory-only shorebased certificates"**: in contrasto con la riga 69 della tabella |
| RYA Powerboat Level 2 | nome in elenco | nome in elenco | **"only valid for certain small crafts"**: la tabella dice fino a 18 m |
| Polacco Żeglarz jachtowy | nome in elenco, **manca "1 miglio dalla costa"** | nome in elenco, manca il limite | nessuna pagina |

Altri visti: improvesailing.com allega una copia del PDF del 2021; klaric-nautika.hr allega un PDF; yachting.com ha un articolo generale; yacht.de (2020) parla ancora del vecchio limite di 30 GT per il SBF See; 12knots e bootsschule1 non leggibili da qui (403).

**Che cosa manca a tutti (il vuoto, dimostrato su 5 esempi su 5):** (1) **il limite per titolo** (lunghezza, stazza, distanza dalla costa, acque) in parole semplici; (2) la risposta **nella lingua di chi ha quel titolo** (tedesco, italiano, olandese: SkipperCity e PlainSailing sono solo in inglese); (3) una pagina per titolo con il nome che la gente scrive ("SBF See", "patente entro 12 miglia", "Day Skipper theory"); (4) che cosa è cambiato fra una versione e l'altra della tabella; (5) la differenza fra legge (questa tabella) e richiesta del noleggiatore, detta con onestà. **Limite del vuoto:** SkipperCity ha già l'elenco completo e aggiornato; il nostro vantaggio è nei limiti, nelle lingue e nelle pagine per titolo, non nell'esistenza dell'elenco.

**Che cosa si costruisce.** Sito statico piccolo: 41 pagine per Paese + circa 60 pagine per i titoli più cercati, in tedesco, inglese, italiano (olandese dopo), con ricerca "scrivi il tuo titolo". Sezioni vicine dalla stessa fonte ufficiale: serve il certificato radio?, barca senza patente in Croazia, tassa di soggiorno per chi sta in barca (domanda debole: "kurtaxe boot kroatien" 2). Riquadro "noleggia una barca in Croazia" (SamBoat) e, per chi ha un titolo non riconosciuto o troppo limitato, "barca con skipper" e corso (Bootsschule1).

**Stima a 18 mesi.** Formula: visite/anno × quota che clicca il noleggio × quota che prenota entro 30 giorni × provvigione media, più AdSense.
- Prudente: 3.600 visite × 5 % × 0,6 % × 45 € = 5 € + AdSense 3.600 × 8 €/1000 = 29 € + corsi 25 € → **circa 60 €**.
- Centrale: 18.000 visite × 8 % × 1,2 % = 17 prenotazioni × 90 € = 1.555 € + AdSense 144 € → **circa 1.700 €**.
- Ottimista: 72.000 visite × 10 % × 1,5 % = 108 prenotazioni × 130 € = 14.040 € + AdSense 576 € → **circa 14.700 €**.
Assunzioni dichiarate: provvigione 5 % su un noleggio da 900 € (prudente), 1.800 € (centrale), 6,5 % su 2.000 € (ottimista); le percentuali di clic e di prenotazione sono ipotesi, non dati (nessun nostro sito ha ancora venduto un noleggio da 2.000 €). Stagione: febbraio-agosto.

**Ore.** 25-35 ore di agenti (lettura del file, 3 lingue, revisione dei fatti e del design); Massimiliano 30 minuti (richiesta dei programmi SamBoat e Bootsschule1 su Awin, email di adesione a yachting.com). Costo: un dominio (circa 10 €/anno) oppure sezione di un sito esistente a costo zero (non c'è un sito adatto: meglio dominio nuovo, con il suo sì). €/ora centrale: circa 55 €.

**Rischi.** (1) I noleggiatori chiedono spesso più della legge (per esempio la pratica oltre alla teoria): va scritto in ogni pagina, altrimenti il lettore sbaglia. (2) I concorrenti sono i pagatori: SkipperCity può aggiungere i limiti in un giorno. (3) Prenotazioni care e rare: la conversione può essere sotto la prudente. (4) La tabella vale per le barche con bandiera croata; per le altre vale la bandiera: da dire. (5) Errori costosi per il lettore: ogni pagina con data della tabella e collegamento alla fonte.

**Le 4 prove.** Domanda: sì (10 suggerimenti in DE, AT, IT, UK, NL). Dato ufficiale leggibile: sì (docx 200, 271 righe). Pagatore con cifra che può pagarci: sì (SamBoat 5-8 % su Awin; yachting.com 3 %, media 100 €; SkipperCity 120 € nell'esempio). Vuoto dimostrato: sì ma stretto (limiti e lingue; l'elenco c'è già).

## 3. Idea 2: la patente nautica croata (Küstenpatent B) spiegata con le regole ufficiali (voto 5)

**Fonte esterna.** Autocomplete tedesco e austriaco intorno a "kroatien": la domanda più grande non è "la mia patente vale?" ma "prendo la patente in Croazia".
- Austria: "küstenpatent kroatien prüfung" 10 (prüfungsfragen, prüfungsfragen pdf, schwierig, erfahrungen, prüfungsgebühr), "küstenpatent b" 10 (wo gültig, was darf ich fahren, preis), "küstenpatent kroatien änderung 2027" presente.
- Germania: "bootsführerschein kroatien" 10 (machen, kosten, online, prüfungsfragen, gültigkeit, ab wieviel ps), "kroatisches küstenpatent" 10 (umschreiben auf international, gültigkeit, kosten).
- Italia: "patente nautica croata" 7 (vale in italia, conversione, categoria b). Croazia: "voditelj brodice b kategorije" 10 (skripta, pitanja i odgovori, cijena, città). Slovenia: "izpit za voditelja čolna" 10.

**Dato ufficiale.** Regole nell'ordinanza croata su barche e yacht (programma d'esame nell'allegato 7; ricerca web); il ministero ha una pagina "Ispiti" (200) e un contatto dedicato agli esami A e B. **Non trovati:** un calendario pubblico degli esami per capitaneria (il calendario 2026 pubblicato riguarda la navigazione interna), una banca ufficiale delle domande (un libro dichiara 80 domande raccolte assistendo agli esami), il testo vigente dell'ordinanza su Narodne novine (l'indirizzo provato risponde "contenuto non disponibile").

**Concorrenti letti** (3, su 6 fatti: età minima, tassa d'esame in euro, limite della barca, radio VHF compresa, dove vale all'estero, modifica 2027): kroati.de (età sì, tassa accennata, limite no, estero no, 2027 no, nessuna fonte); aviation.direct (articolo pubblicitario: "riforma", 18 m, VHF integrato, nessuna data né fonte); aaayacht.cz (scuola: corsi e date 2027, limite 30 GT, niente tassa ufficiale). **Nessuno cita l'ordinanza**, e si contraddicono sul limite (18 m contro 30 GT). È un indizio di vuoto, non una prova: non ho letto il testo ufficiale vigente, quindi non so chi ha ragione. Voto massimo 5.

**Pagatore.** Corsi online: 123nautik "Onlinekurs Boatskipper B" a 169 € su Digistore24 (quota per gli affiliati non letta); Bootsschule1 fino all'8 % su Awin ma vende la patente tedesca (se vende anche il corso croato non è verificato: sito 403). Le scuole sono anche gli editori che occupano la prima pagina.

**Stima:** 40 / 500 / 4.500 €/anno (centrale: 15.000 visite × 3 % × 4 % = 18 corsi × 20 € = 360 € + AdSense 120 €). Ore 15-20 come sezione del sito 1. **Si riapre a 6** se il testo vigente dell'ordinanza si legge e risolve le contraddizioni (limite, VHF, validità all'estero, modifica 2027).

## 4. Idea 3: barca senza patente, limite per Paese e per lago (voto 4,5)

Domanda forte e locale: "boot mieten ohne führerschein" 10 (Mallorca, Kroatien, Gardasee, Bodensee, Berlin, Mecklenburger Seenplatte), "noleggio barca senza patente" 10 (Lago di Garda, Tropea, Numana, Otranto, Gallipoli), "location bateau sans permis" 10 (Marseille, Annecy, Paris, Cannes). Pagatori: SamBoat 5-8 %, Le Boat 2 % con cookie di 364 giorni. Dato: i limiti di legge per Paese (potenza, lunghezza) sono pochi numeri, non un insieme di dati; l'elenco tedesco delle acque con "Charterbescheinigung" non è stato letto. Chi cerca "noleggio barca senza patente Tropea" vuole un noleggiatore del posto: prima pagina di attività locali, mappa e le pagine-elenco delle piattaforme (SamBoat ha la sua "noleggio barche senza patente", 200). **Concorrenti non letti su 5 esempi: voto massimo 5; per la ricerca locale do 4,5.** Stima 30 / 400 / 4.000. Solo come sezione del sito 1 (una pagina per Paese con il limite e la fonte di legge).

## 5. Idea 4: camper oltre 3,5 t in Europa, in tedesco (voto 4, NO)

Domanda vera: "maut wohnmobil über 3 5 t" 10 (Slowenien, Österreich, Slowakei, Belgien, Polen, Kroatien, Schweiz, Tschechien), "tempolimit wohnmobil über 3 5t" 10 (9 Paesi), "wohnmobil überladen strafe" 8 (8 Paesi), "go box wohnmobil" 10. In italiano, francese, olandese e inglese: 0. Cade su due prove: (1) **pagatore sbagliato**: chi ha un camper oltre 3,5 t è un proprietario, non noleggia (CamperDays 105 € a prenotazione non c'entra); restano AdSense e accessori; (2) **nessun vuoto**: promobil.de ha la guida ai pedaggi per Paese (letta: Slovenia, Svizzera, Croazia, Polonia, Danimarca presenti; 15 volte "über 3,5"), più ADAC, camperstyle, PiNCAMP, web.de. Stima 30 / 250 / 2.000.

## 6. Non indagati in questo giro (onestà)

Matrimoni all'estero, sci, studio all'estero, traslochi nell'UE, assicurazione animali: **non letti oggi**. Motivo: tempo speso sulle due verticali con il pagatore più alto a cliente. Un fatto utile per il prossimo giro: **CamperDays paga 105 € medi a prenotazione su Awin** (DE e NL): manca la domanda giusta di chi noleggia (per esempio "wohnmobil mieten führerschein" 10 in Germania, con Kanada e USA; "can i drive a motorhome on a car licence" 10 nel Regno Unito), con concorrenti da leggere.

## 7. Che cosa propongo

1. Mettere in coda l'idea 1 (sito "patenti nautiche riconosciute in Croazia", DE/EN/IT), con €/ora centrale circa 55 €. Prima della costruzione: un verificatore rilegge SkipperCity e conferma che i limiti per titolo non ci sono ancora, e controlla la prima pagina tedesca per "sportbootführerschein see kroatien anerkannt" (da qui Google non si legge).
2. A Massimiliano si chiede solo, al momento della costruzione: sì al dominio (circa 10 €/anno) e 30 minuti per le richieste dei programmi (SamBoat IT/UK/DE e Bootsschule1 su Awin).
3. Idee 2 e 3 solo come sezioni dello stesso sito, dopo i primi dati di visite.
