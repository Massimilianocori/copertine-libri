# Fronte: giro completo sulla Polonia (polacco, ucraino, inglese), 11/11/2026

**Domanda del giro.** In Polonia (unico grande mercato nuovo dove chi paga può pagarci: UE, bonifico SEPA) quali programmi e obblighi del 2026-2027 hanno domanda improvvisa, dati ufficiali leggibili e un pagatore a cui possiamo iscriverci?

**Risposta breve: nessuna idea arriva a 7.** La migliore è un 5,5: **i codici PKD uno per pagina con il passaggio dal vecchio al nuovo codice** (scadenza di legge 31/12/2026), da costruire insieme ai codici del KSeF di ieri come **un solo sito polacco per le piccole imprese** (centrale insieme circa 2.000 €/anno, ottimista circa 18.000). Tutto il resto cade su una delle quattro prove: i sussidi per la casa (dati ufficiali non leggibili da qui e nessun programma per editori), le zone a traffico pulito (un concorrente fa già tutto), il prezzo del teleriscaldamento (tariffe in PDF senza testo), gli ucraini (notizie già coperte da decine di testate; tempi per ufficio senza fonte regolare).

Il fatto nuovo sui **pagatori**: il programma diretto dell'assicurazione auto (Rankomat) è costruito per soggetti polacchi; i soli pagatori polacchi con cifra scritta e senza ostacoli visibili restano i programmi di contabilità (wFirma, Fakturownia, iFirma).

Fonti esterne da cui nascono le idee: autocomplete Google gl=pl (hl=pl, hl=uk, hl=en; circa 190 domande, più gl=de e gl=cz per Cracovia), i documenti ufficiali letti con curl (GUS, Gazzetta polacca, URE, Comune di Cracovia, Ufficio stranieri), le pagine dei programmi di affiliazione polacchi.

Limiti dichiarati: Google.pl non è leggibile con curl, quindi i concorrenti sono stati trovati con la ricerca web (indice americano) e poi letti uno per uno: **la composizione vera della prima pagina polacca va controllata dal verificatore**. Non raggiungibili da questo ambiente: `dane.gov.pl` e la sua API (connessione chiusa), `api.sejm.gov.pl` (503), `lista-zum.ios.edu.pl` e `czystepowietrze.gov.pl` (catena di certificati incompleta: non si disattiva la verifica), `mubi.pl` e `infakt.pl` (403), `visitukraine.today` (403).

## Chi paga in Polonia (letto oggi)

| Programma | Cifra letta | Possiamo entrare ed essere pagati? |
|---|---|---|
| wFirma (contabilità online) | **30 % di ogni pacchetto, a vita**, link valido 90 giorni | Sì in linea di principio (UE); regolamento non letto sul punto "soggetto estero" |
| iFirma | **100 zł** studio contabile, **50 zł** contabilità online, **10 zł** Faktura+; pagamento con fattura sopra 500 zł di provvigioni | Come sopra; serve un conto iFirma gratuito |
| Fakturownia | 30 % per 24 mesi (letto l'11/11 dal giro precedente; oggi pagina 200, cifra non riletta) | Come sopra |
| Rankomat (assicurazione auto, programma diretto) | **Nessuna cifra pubblica**: "numero di contatti × tariffa che concordiamo"; 50 zł di benvenuto; pagamento entro 2 mesi con fattura | **Di fatto no senza chiedere**: il modulo chiede il voivodato, un conto di **26 cifre** (formato polacco; un IBAN italiano ha 27 caratteri con lettere) e "fattura con IVA 23 % / senza IVA" |
| mubi.pl | pagina 403 | Non verificato |
| systempartnerski.pl (prodotti finanziari, 50.000 editori dichiarati) | tariffe solo dopo l'accesso | Non verificato |
| MyLead | catalogo pubblico: prestiti 147 programmi, conti 23, assicurazioni 12, energia 14; tariffe e pagamenti non letti | Non verificato |
| webePartners (negozi, a percentuale sulla vendita), Convertiser, Awin Polonia | nessuna cifra letta | Non verificato |
| Impianti solari e pompe di calore | **nessun programma per editori con cifra**; esiste solo un mercato di contatti tra aziende (annunci a 5-50 zł a contatto), cioè vendita diretta | No (esclusa dalle regole) |
| AdSense | resa per 1.000 visite non leggibile: **assunzione 2-4 €** | Sì |

## Classifica

| # | Idea | Lingua / dove | Voto | Prudente / centrale / ottimista €/anno a 18 mesi | Ore | Le 4 prove |
|---|---|---|---|---|---|---|
| 1 | **Codici PKD uno per pagina: vecchio codice 2007 → nuovi codici 2025, che cosa comprende e che cosa no, imposta forfettaria, IVA, registratore di cassa** | polacco; sezione del sito "codici ufficiali per le imprese" insieme al KSeF | **5,5** | 60 / 1.100 / 9.600 (con il KSeF: 110 / 1.950 / 18.600) | 30-40 + 30 min di Massimiliano | domanda SÌ, dati SÌ, pagatore SÌ (lato fiscale da confermare), vuoto **A METÀ** |
| 2 | Permesso di soggiorno per ufficio di voivodato: tempi, coda, stato della pratica, costi, foto | ucraino + inglese + polacco | **4,5** | 80 / 600 / 5.000 | 30-40 | domanda SÌ, dati **A METÀ**, pagatore debole, vuoto A METÀ |
| 3 | Zone a traffico pulito (Cracovia, Varsavia): "la mia auto entra?" in più lingue | polacco, tedesco, inglese | **4 (NO)** | 30 / 250 / 2.000 | – | domanda SÌ, dati SÌ, pagatore NO, vuoto NO |
| 4 | Prezzo del teleriscaldamento città per città (e buono riscaldamento) | polacco | **3,5 (NO)** | 20 / 200 / 1.500 | – | domanda SÌ, dati NO, pagatore solo AdSense, vuoto non provato |
| 5 | Sussidi casa: elenco dei dispositivi ammessi (lista ZUM), Czyste Powietrze, Mój Prąd | polacco | **3,5 (NO)** | – | – | domanda SÌ sui programmi e quasi zero per modello, dati NO da qui, pagatore NO |

Formula: visite all'anno × (pubblicità + affiliazione) per 1.000 visite. Le visite sono ipotesi: non abbiamo ancora nessun sito in polacco.

---

## 1. Codici PKD, uno per pagina (voto 5,5)

**Che cosa nasce.** La classificazione delle attività PKD 2025 ha sostituito la PKD 2007. Il regolamento (Dz.U. 2024 poz. 1936, PDF letto oggi) dice che la vecchia si può usare "non oltre il 31 dicembre 2026"; chi non aggiorna viene riclassificato d'ufficio dal 1/1/2027 con la tabella di passaggio. Le sottoclassi passano da 656 a 728 e molti codici cambiano significato. Esempio letto nel testo ufficiale: **47.91.Z** nel 2007 era la vendita al dettaglio via Internet; nella PKD 2025 è "intermediazione nella vendita al dettaglio non specializzata": chi vende online deve scegliere un altro codice. **62.01.Z** (software) si divide in 62.10.A (giochi) e 62.10.B (resto).

**Domanda (gl=pl, hl=pl).** Ogni codice ha la sua famiglia di domande:
- "pkd 62.01.z" 10 (2025, stawka ryczałtu, jaki ryczałt, a vat, **nowy kod**, "a 62.10 b"); "pkd 47.91.z" 10 (2025, 2026, jaki podatek, ryczałt, vat, **kasa fiskalna**, co obejmuje); "pkd 49.41.z" 10 (jaki ryczałt, co obejmuje, **jakie pkwiu**); "pkd 43.39.z" 10; "pkd 68.20.z" 10; "pkd 85.59.b" 10 (zwolnienie z vat); "pkd 96.02.z" 9 ("nowe pkd", "pkd 2007"); "pkd 74.20.z" 7; "pkd 56.10.a" 7; "pkd 62.10.b" 8;
- passaggio: "pkd 2007 na 2025" 10 (konwersja, **kalkulator**, klucz, mapowanie, wyszukiwarka), "zmiana pkd 2025" 10 (do kiedy, w krs, ceidg), "nowe pkd" 10 (dla fryzjerów, fizjoterapia, a stare), "pkd 2025" 10 (klucz powiązań, a 2007);
- per mestiere: "kod pkd" 10 (fryzjerstwo, budownictwo, fizjoterapia, transport, sprzedaż internetowa), "jakie pkd" 10 (dla influencera, na ryczałt 8,5, dla warsztatu), "pkd a ryczałt" 10 (wyszukiwarka).

**Dati leggibili.** `klasyfikacje.stat.gov.pl/static/pkd_25/pdf/KlasyfikacjaPKD2025.pdf` risponde 200 (8,3 MB; 3,2 MB di testo estratto): schema, note esplicative per sottoclasse ("comprende / non comprende"), **tabella di passaggio 2007 → 2025** (parte IV, da pag. 468) e 2025 → 2007 (parte V). Verificate nel testo estratto le righe di 62.01.Z, 43.39.Z (si divide in almeno sette codici nuovi, tra cui 43.23.Z, 43.31.Z, 43.35.Z, 81.22.B), 47.91.Z, 49.41.Z, 74.20.Z. Il regolamento con la scadenza: `eli.gov.pl/api/acts/DU/2024/1936/text/O/D20241936.pdf` 200. La versione a pagine del GUS è un'applicazione JavaScript (2,8 KB a curl): si usa il PDF. **Non letta oggi:** una fonte ufficiale che leghi PKD → PKWiU → aliquota forfettaria; l'aliquota dipende dal tipo di ricavo (PKWiU), non dal codice PKD, quindi quella parte va scritta come "orientativa, con l'articolo di legge", oppure lasciata fuori.

**Concorrenti letti su 5 codici** (62.01.Z → 62.10.B, 43.39.Z, 47.91.Z, 49.41.Z, 74.20.Z).

| | pkd.com.pl (iFirma) | pkd.pl (inFakt) | firmove.pl e Fakturownia (calcolatore e articolo sull'aliquota per PKD) |
|---|---|---|---|
| Che cos'è | una pagina per codice, **ancora PKD 2007** | **679 pagine, una per codice PKD 2025** (su 728), sitemap aggiornata oggi | pagine generali |
| Passaggio vecchio → nuovo | assente (0 occorrenze di "2007"); la pagina 62.10.B risponde 404 | **assente** (0 occorrenze di "2007" su 4 pagine) | assente |
| Aliquota forfettaria | assente | **presente**, con la percentuale dei loro clienti per regime fiscale (62.10.B: 70,3 % forfettario, aliquota 12 %) | per categoria, 0 codici su 5 nel testo |
| IVA, registratore di cassa, PKWiU, "non comprende" | assenti | assenti (0 occorrenze ciascuno); pagine corte, circa 2.400 caratteri | assenti |
| 43.39.Z | presente (2007) | **assente dalla sitemap** | – |

Ricerca web sul passaggio ("konwerter pkd 2007 na 2025", "74.20.Z nowy kod"): solo articoli generali di studi legali (Dudkowiak, RSM, KPMG, getsix), PARP, pit.pl e il PDF del GUS; **nessuno strumento per codice**; le fonti si contraddicono (62.01.A/B contro 62.10.A/B). Non letti: il motore ufficiale di biznes.gov.pl (JavaScript), rejestr.io (403), infakt.pl (403).

**Che cosa manca a loro:** il passaggio vecchio → nuovo codice per codice con il caso "il tuo codice si è diviso in N", le trappole (47.91.Z), "non comprende", IVA e registratore di cassa. **Che cosa hanno e noi no:** inFakt ha già le pagine per codice nuovo con l'aliquota e dati propri sui clienti, in polacco nativo, sul dominio pkd.pl. Il vuoto vero è **il passaggio**, e dura poco: la scadenza è fra 7 settimane; dopo resta la domanda "che codice mi hanno assegnato d'ufficio" e la coda stabile sui codici, dove inFakt è davanti. **Vuoto dimostrato a metà: voto 5,5.**

**Chi paga.** wFirma 30 % a vita, iFirma 50-100 zł, Fakturownia 30 % per 24 mesi. Il pubblico è quello giusto: chi apre o aggiorna una ditta individuale e sceglie regime fiscale e programma (più vicino all'acquisto di chi cerca un codice di errore).

**Stima (assunzioni).** Cliente ≈ 40 € (30 % di circa 500 zł l'anno, poco più di un anno di permanenza).
- Prudente: 2.000 visite/mese, solo pubblicità 2,5 € → **circa 60 €/anno**.
- Centrale: 10.000 visite/mese, pubblicità 3 € + affiliazione 6 € (1 cliente ogni 6.500 visite) → **circa 1.100 €/anno**.
- Ottimista: 50.000 visite/mese, 4 € + 12 € → **circa 9.600 €/anno**.

**Proposta.** Un solo sito in polacco "codici ufficiali per le imprese": PKD (circa 1.400 pagine: 656 vecchi + 728 nuovi) + i 78 codici del KSeF di ieri; stessa affiliazione, stesso pubblico. Insieme: 110 / 1.950 / 18.600 €/anno. Sotto l'asticella dei siti nuovi (voto 7): entra in coda come idea a costo zero, **solo se parte entro novembre** (la domanda sul passaggio ha il picco tra dicembre e febbraio).

**Rischi.** Tema fiscale in una lingua che non controlliamo: ogni pagina riporta il testo ufficiale, niente consigli; estrazione della tabella dal PDF da controllare riga per riga (celle su più righe); inFakt può aggiungere il passaggio in una settimana; fattura dal regime forfettario a società polacche da chiedere al commercialista.

## 2. Permesso di soggiorno per ufficio di voivodato (voto 4,5)

**Avvertenza:** è burocrazia per stranieri, tema escluso dai "fronti nuovi" (regola del 7/11); valutata perché richiesta dal compito. Il 30/10 la stessa idea aveva preso 3,5 per mancanza di dati.

**Che cosa nasce.** Dal 27/4/2026 le domande di soggiorno si presentano solo online (portale MOS); dal 4/5/2026 al 4/3/2027 gli ucraini con protezione temporanea possono chiedere la carta "CUKR" (pagina dell'Ufficio stranieri letta: "04.05.2026 r. – karta pobytu CUKR"). Termine di legge per la carta CUKR 180 giorni, con termini sospesi fino al 4/3/2027 (letto su hrappka.pl, non su fonte ufficiale).

**Domanda.**
- Polacco: "karta pobytu kolejka" 10 (warszawa, opole, katowice, wrocław, bydgoszcz, lublin, gdańsk, poznań), "karta pobytu czas oczekiwania" 9, "ile czeka się na kartę pobytu" 10, "karta pobytu status" 10 (online katowice, rzeszów, kraków, warszawa), "inpol status" 7 (**status 4, status 10**), "mos cudzoziemcy" 10 (nie działa, rejestracja), "status ukr" 10 (do kiedy 2027, do 2028), "cukr karta" 10, "zdjęcie do karty pobytu" 10 (mos, online, cukr).
- Ucraino (hl=uk): "карта побиту" 10 (познань, гданськ, варшава, вроцлав), "карта побиту ціна" 10 (per città), "карта cukr" 10 (скільки часу робиться, покрокова інструкція), "песель укр" 10, "статус укр" 10 (до 2028), "фото на карту побиту" 10 (per città), "присяжний перекладач" 10 (per città). Deboli: "800 плюс для українців" 3, "карта побиту скільки чекати" 4, stipendio e tasse 1-3.
- Inglese: "poland residence permit waiting time" 9, "karta pobytu status" 10, "inpol status" 10, "mos poland" 10, "poland work permit processing time" 10 (from india, from dubai, reddit).

**Dati.** A metà. I tempi medi per ufficio esistono solo nelle risposte del Ministero dell'Interno alle interrogazioni parlamentari: dal riassunto della ricerca (interrogazione 18089, dati al 6/7/2026) Mazowieckie 394 giorni per il soggiorno temporaneo (153 nel 2023); nel 2023-2025 il più rapido Małopolskie 172 giorni, il più lento Śląskie 640. **Oggi `api.sejm.gov.pl` risponde 503: tabella non letta direttamente.** La risposta del Ministero al Difensore civico del 12/8/2026 (PDF letto, 5.000 caratteri) non ha numeri per ufficio. `migracje.gov.pl` (statistiche) è in JavaScript; `dane.gov.pl` non raggiungibile. Nessun elenco ufficiale dei significati degli stati "inPOL" trovato.

**Concorrenti letti.** hrappka.pl (guida generale: nessun numero per voivodato); kadry.infor.pl ("fino a 3 anni di attesa": nessun numero per voivodato nel testo); visitukraine.today (titolo "tempi per provincia 2025", pagina 403: non letta). Sulla carta CUKR in ucraino la prima pagina è di testate e enti: Kyiv Post, 24tv, Fakty, Minfin, UNHCR, legalaid.ua, con date in conflitto tra loro. Su 5 uffici (Śląskie, Mazowieckie, Małopolskie, Opolskie, Dolnośląskie): nessuno dei due letti dà un tempo per ufficio; i siti commerciali citati dalla ricerca danno classifiche opposte senza fonte. **Vuoto reale sui tempi per ufficio, ma senza una fonte regolare da cui riempirlo.**

**Chi paga.** Foto per documenti (PhotoAiD, 15 % secondo la nostra verifica di ottobre; pagina del programma oggi 404 all'indirizzo provato) e Wise: nessuna cifra riletta oggi. Assicurazione sanitaria per stranieri ("ubezpieczenie dla cudzoziemca do karty pobytu" 5): nessun programma trovato. Rankomat chiuso (sopra).

**Stima.** Prudente 2.500 visite/mese × 2,5 € → circa **80 €**; centrale 12.000 × 4 € (3 pubblicità + 1 affiliazione) → circa **600 €**; ottimista 60.000 × 7 € → circa **5.000 €**.

**Giudizio.** Si riapre se le tabelle delle interrogazioni si leggono (riprovare `api.sejm.gov.pl`) e risultano almeno annuali: allora diventa una sezione "tempi per ufficio" in tre lingue. Oggi no.

## 3. Zone a traffico pulito: Cracovia e Varsavia (voto 4, NO)

- **Domanda:** "strefa czystego transportu" 10, "sct kraków" 10 (opłata, sprawdzenie pojazdu), "czy wjadę do krakowa" 10, "sct kraków opłata" 10 (2027, miesięczna), "sct warszawa 2026" 8, Wrocław 8; in tedesco "krakau umweltzone" 5 (strafe, registrierung); in inglese "krakow clean transport zone" 6; in ucraino 4.
- **Dati ufficiali letti** (krakow.pl, 200): benzina e GPL Euro 4 o dal 2005, diesel Euro 6 o dal 2014; per chi non è residente e non rispetta le soglie 2,50 zł l'ora; mensile 100 zł nel 2026, 250 nel 2027, 500 nel 2028; giornaliera 15 zł nel 2027; dal 2029 nessun pagamento possibile. Il controllo per targa è un'applicazione JavaScript del Comune.
- **Vuoto: non c'è.** `tyremap.com/pl/emission-zones/krakow/` (letto) ha già la pagina in polacco e in inglese: soglie, verifica "la mia auto entra?" per carburante e classe Euro, multa fino a 500 zł, obbligo di registrazione per le targhe estere, data di verifica; è una rete di pagine come la nostra. In tedesco ADAC e travelinformation.eu. Il Comune ha il controllo per targa e le pagine in inglese.
- **Pagatore:** nessuno a cui possiamo iscriverci (Rankomat sopra; programmi per i controlli dello storico auto non trovati: indirizzi provati 404). Coerente con le quattro bocciature delle zone a basse emissioni in Europa (14-18/10).

## 4. Prezzo del teleriscaldamento per città e buono riscaldamento (voto 3,5, NO)

- **Domanda:** "bon ciepłowniczy" 10 (2026 dla kogo, wniosek, kiedy wypłata, kraków, lublin), "ile kosztuje gj ciepła" 10 (w krakowie, w warszawie, w białymstoku), "cena ciepła gj" 10, "ogrzewanie miejskie cena" 6 (5 città). Ma "bon ciepłowniczy 2027" 1 e "cena ciepła 2027" 0: il buono (soglie 170 / 200 / 230 zł/GJ, domande 1/7-31/8/2026) finisce con il 2026.
- **Dati:** il bollettino dell'URE elenca le tariffe approvate (pagina 2026 letta: 340 decisioni, un PDF per azienda). Nel PDF di prova (PEC Lubartów, 1 MB) il testo estraibile è la sola decisione (10.000 caratteri, **nessun "zł/GJ"**): la tabella dei prezzi è un'immagine. Servirebbe il riconoscimento ottico su centinaia di PDF, con rischio di errori sui prezzi.
- **Concorrenti:** la ricerca non trova nessun confronto tra città (xyz.pl scrive che i prezzi non sono confrontabili da una città all'altra); non letti 3 concorrenti su 5 città, quindi vuoto non provato.
- **Pagatore:** solo AdSense (chi ha il teleriscaldamento non può cambiare fornitore).

## 5. Sussidi per la casa: lista ZUM, Czyste Powietrze, Mój Prąd (voto 3,5, NO)

- **Domanda sui programmi alta:** "czyste powietrze 2026" 10 (progi dochodowe jak obliczyć, zmiany od lipca), "mój prąd 7.0" 10 (kiedy, czy będzie, magazyn energii), "lista zum" 10 (pompy ciepła, piece na pellet, kotły, wycofane), "dofinansowanie" 10, "ulga termomodernizacyjna 2026" 10, "naszeauto" 10, "mój elektryk 2.0" 10. **Per modello quasi zero:** "lista zum viessmann" 1, "czy pompa ciepła kaisai jest na liście zum" 1, Panasonic 0.
- **Dati: non leggibili da qui.** `lista-zum.ios.edu.pl` e `czystepowietrze.gov.pl` falliscono la verifica del certificato (catena incompleta); la verifica non si disattiva.
- **Pagatore: nessuno.** Nessun programma per editori con cifra per fotovoltaico o pompe di calore; solo annunci di compravendita di contatti tra aziende (5-50 zł), cioè vendita diretta. Concorrenti non letti (gli installatori stessi).

## Piste viste e non proposte

- **Temi fiscali e del lavoro 2027** ("płaca minimalna 2027" 10, "ksef 2027" 10: kary, dla kogo, odroczenie; "renta wdowia 2027" 10 con kalkulator; "składki zus 2027" 5; "mały zus plus 2027" 5; "składka zdrowotna 2027" 6): un numero o una data sola per tutti, niente coda per luogo o per codice; concorrenti non letti (voto massimo 5).
- **Prezzo dell'elettricità** ("cena prądu 2026 za 1 kwh" 10 per venditore: PGE, Enea, Energa, Tauron; "taryfa g11 2026" 10): 5 venditori, non centinaia di pagine; "taryfa prądu 2027" 0; concorrenti non letti.
- **JPK_CIT, etichette dei conti** ("jpk cit znaczniki" 8): la pagina ufficiale delle strutture è in JavaScript (957 byte a curl); coprono Grant Thornton, Symfonia, poradnikprzedsiebiorcy, LTCA. Non proposta.
- **Tassa sugli immobili 2027 per Comune** (9, con Lublino e Varsavia): aliquote in 2.477 delibere comunali, nessuna fonte unica trovata.
- **Auto:** "średnia cena oc" 7, "oc kalkulator" 10 (dominio dei comparatori, che sono anche i pagatori chiusi a noi); "nowe prawo jazdy 2027" 7; "przegląd techniczny cena 2026" 5; "e-toll" 10 (accesso e mappa: servizio dello Stato).
- **Sistema della cauzione sulle bottiglie** ("system kaucyjny" 10): una regola nazionale, solo AdSense.
- **Stipendio netto per stranieri** ("poland salary calculator" 10: for foreigners, for indian, b2b; in ucraino 2-3): concorrenti non letti; ieri lo stesso tema in Giappone risultava invaso.
- **Traduttori giurati per lingua e città** ("tłumacz przysięgły ukraiński" 10, "присяжний перекладач" 10 con le città): il registro del Ministero della Giustizia è un elenco di persone con nome e contatti: dati personali, non si fa.

## Che cosa si impara

1. In Polonia chi paga un editore estero senza ostacoli è il **programma di contabilità per le piccole imprese** (30 % ricorrente). L'assicurazione auto, che paga di più, ha un modulo per soli conti polacchi. Quindi le idee polacche vanno cercate dove c'è l'imprenditore, non l'automobilista o la famiglia.
2. I venditori di contabilità presidiano già i codici con siti dedicati (pkd.com.pl di iFirma, pkd.pl di inFakt): lasciano scoperto solo ciò che cambia (il passaggio 2007 → 2025, i codici tecnici del KSeF). Sono vuoti a tempo.
3. Per sussidi, energia e stranieri i dati ufficiali polacchi sono spesso in applicazioni JavaScript, PDF senza testo o portali che da qui non rispondono: prima di un altro giro polacco conviene partire dall'elenco delle fonti leggibili, non dalla domanda.
