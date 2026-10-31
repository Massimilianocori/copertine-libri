# Canada, Australia, Nuova Zelanda: tempi dei visti, working holiday, cittadinanza, costi (31/10/2026)

Angolo assegnato: tempi di elaborazione ufficiali dei visti e permessi per tipo e Paese (IRCC, Home Affairs, INZ), working holiday per nazionalità con quote e date, esami di cittadinanza, costi ufficiali.

Prima di partire ho letto il metodo e l'asticella (`.claude/skills/rete-siti/SKILL.md`), le regole del 30-31/10 (`REGOLE-FISSE.md`: fronti nuovi, conta il fatturato, niente lavori a ore di Massimiliano) e `ESPLORATE.md`. Molti temi dell'angolo erano già chiusi: tempi IRCC (NO 14/10, 23/10, 27/10, 30/10: `canada.ca` 000), tempi del visto turistico canadese per Paese (NO 27/10), working holiday Canada IEC (NO 18/10), quote del visto 462 (NO 27/10, voto 4), codici postali degli 88 giorni (NO 28/10), tempi dei visti australiani (NO 28/10: "nessun numero nell'HTML"), percentuali di promossi ai test di cittadinanza (NO 20/10), attesa per la cerimonia di cittadinanza per council (RISERVA 21/10: la tabella non rispondeva). **Non li ho ripetuti alla cieca: li ho riprovati con le fonti di oggi**, perché due blocchi tecnici del passato oggi non ci sono più (vedi "In breve").

Prove raccolte il 31/10/2026: `curl` dal nostro server (stato HTTP, formato, data, licenza), Google Autocomplete con Paese e lingua giusti (`gl=au/nz/ca/in/es/ar/fr`, client firefox: il numero dopo la query è quante varianti propone, massimo 10), ricerche web per vedere chi c'è oggi in prima pagina, mappe dei siti dei concorrenti.

## In breve

- **Nessuna idea passa l'asticella dei siti nuovi** (voto ≥ 7 e ≥ 5.000 €/anno centrali). Anche mettendo insieme tutte le idee australiane in un solo sito il caso centrale resta sotto i 3.000 €/anno (oltre alla sezione "approval rates" già in cantiere).
- **Il fatto nuovo del giro: il sito dell'immigrazione australiana dà i suoi numeri in JSON.** Le pagine di Home Affairs non hanno i numeri nell'HTML: li chiedono a tre indirizzi pubblici del sito stesso, che rispondono a una normale richiesta POST senza chiave, senza captcha e senza nessuna protezione da aggirare (è lo stesso indirizzo che usa il browser di chiunque apra la pagina):
  - tempi di lavorazione di tutti i visti (`/_layouts/15/api/GPT.aspx/GetVisaGlobalProcessingTime`): **200**, 94 righe per 47 sottoclassi, con il 25°, 50°, 75° e 90° percentile, "Updated 29 September 2026", dati fino al 31/8/2026;
  - **attesa per la cerimonia di cittadinanza per council** (`/_layouts/15/api/Data.aspx/GetListData`, lista `citizenshipCeremony`): **200**, **539 council**, aggiornata il 16/10/2026. È la riserva del 21/10 che allora rispondeva "List data is currently unavailable": **oggi si legge**;
  - prezzi dei visti (`/_layouts/15/api/data.aspx/GetVisaPrices`): risponde, ma in parte con l'errore "Visa prices are currently unavailable".
  - Licenza di tutto il sito: **Creative Commons Attribution 3.0 Australia** (pagina "Copyright and disclaimer" letta: "All material presented on this website is provided under a Creative Commons Attribution 3.0 Australia licence"), da attribuire a "Australian Government Department of Home Affairs".
- **Perché conta per noi:** i numeri che arrivano da uno script non li vedono né Google né gli assistenti AI che leggono le pagine senza eseguire gli script. Infatti cercando "Blacktown / Casey citizenship ceremony wait time" la ricerca web non trova nessun numero attuale: solo richieste di accesso agli atti (righttoknow.org.au, 2021-2024) e le pagine dei council che rimandano al numero di telefono 131 880. **Una pagina statica per council con il numero ufficiale è esattamente il formato che gli assistenti citano** (lezione di Visa Income: un terzo delle visite arriva da ChatGPT).
- **Il resto dell'angolo è chiuso o già occupato:**
  - Canada: `www.canada.ca` ancora **000** (la connessione si ferma durante la stretta di mano cifrata: non si aggira). Si leggono solo `ircc.canada.ca` (centro di aiuto e **lista delle tariffe**, 200, modificata il 21/9/2026) e alcuni file aperti IRCC se si conosce il nome esatto (elenco della cartella 403). Tempi IRCC, pool IEC e test di cittadinanza restano chiusi.
  - Nuova Zelanda: **tutto `immigration.govt.nz` è dietro Incapsula** (pagina di 212 byte con lo script anti-robot, anche su tempi, working holiday e statistiche); `passports.govt.nz` 403. Non si aggira: NO.
  - Tempi dei visti australiani per sottoclasse: **widen.com.au** (studio di migrazione) ha già 44 pagine "processing-times/<sottoclasse>" e un rapporto mensile, aggiornate dal 29/9 e "checked by us 31 October", con la frase pronta "50% of applications decided within 22 months and 90% within 30 months"; più comparemigrationagents.pages.dev e visatasker. Occupato.
- **Lezione del giro:** in questa zona la fonte australiana è la più aperta del mondo anglosassone (JSON, licenza CC BY, aggiornamento mensile), Canada e Nuova Zelanda sono chiuse dal nostro server. Dove l'Australia pubblica un numero "per luogo" (council) nessuno lo ha ancora messo in pagine statiche; dove pubblica un numero "per visto" gli studi di migrazione lo hanno già fatto, perché da quelle ricerche nascono clienti.
- **Proposta:** costruire l'idea 1 come **sezione di Visa Income Checker** (costo zero, guadagno atteso positivo, 10-15 ore), e aggiungere le idee 2 e 3 come righe in più della sezione australiana "visa approval rates" già in cantiere (pochissime ore, stessi file).
- **Prossimo angolo consigliato:** cercare nel resto del mondo altri "numeri per luogo" che un ente pubblica solo dentro uno script (tabelle caricate da JSON): sono invisibili a Google e agli assistenti, e quindi il buco è più probabile. Esempi da provare: attese per ufficio dei permessi di soggiorno, attese per sede degli esami di guida, tempi per tribunale.

## Tabella delle idee

| # | Idea | Dove | Voto | €/anno a 18 mesi (prud. / centr. / ott.) | Ore | Esito |
|---|---|---|---|---|---|---|
| 1 | Attesa per la cerimonia di cittadinanza australiana, council per council (539), con persone in attesa, % sotto 3 mesi, 3-6 mesi, oltre 6, storico mese per mese + tempi nazionali della cittadinanza | sezione di Visa Income Checker | 6,5 | 300 / 1.000 / 3.000 | 10-15 | **PASSA come sezione** (costo zero, guadagno positivo) |
| 2 | Tempi di lavorazione di tutti i visti australiani (47 sottoclassi, percentili 25-90) con storico mensile | riga in più nella sezione australiana in cantiere | 4,5 | 50 / 200 / 600 | 3-4 | Solo aggiunta: widen.com.au già primo |
| 3 | Visto 462: posti usati e rimasti per Paese (quota ufficiale + visti concessi dal file mensile BP0017), in inglese, spagnolo e portoghese | sezione di Before You Fly o di Visa Income Checker | 5,5 | 150 / 600 / 2.200 | 8-12 | RISERVA alta: aggiunta economica; da fare se SafetyWing è iscritto |
| 4 | Working holiday per nazionalità, tutte le destinazioni (età, quote, aperture, costi) | sito nuovo | 5 | 300 / 1.250 / 4.000 | 40-60 | NO come sito: Canada e Nuova Zelanda chiusi dal server; pvtistes, yomeanimo, gooverseas forti |
| 5 | Costi ufficiali dei visti australiani e canadesi nella valuta di chi paga (INR, PKR, CNY, PHP…) | aggiunta a Visa Income Checker | 5 | 100 / 400 / 1.200 | 10-15 | RISERVA: prezzi australiani a metà ("currently unavailable"), Nuova Zelanda chiusa |
| 6 | Test di cittadinanza australiano: pratica in inglese, cinese e vietnamita | sito nuovo o sezione | 4,5 | 100 / 500 / 2.000 | 25-35 | NO: più di 15 app, ausmocktest.pages.dev, easy-prep, studi legali; domande vere non pubbliche |
| 7 | Visti per genitori (143/103/804/864): date di rilascio della coda | aggiunta | 4 | 30 / 150 / 500 | 3-5 | NO come pagina a sé; al massimo una riga |
| 8 | Canada: tempi IRCC, pool IEC per Paese, test di cittadinanza | – | 3 | – | – | NO confermato: `canada.ca` 000 |
| 9 | Nuova Zelanda: tempi INZ, schemi working holiday con quote e date, cittadinanza | – | 3 | – | – | NO: Incapsula su tutto `immigration.govt.nz`, `passports.govt.nz` 403 |

Ipotesi comuni per i calcoli (le stesse dei giri precedenti, non ancora misurate): pagine viste per visita 1,3-1,5; pubblicità per pubblico australiano in inglese **8-12 €** ogni 1.000 pagine viste; pubblico latinoamericano in spagnolo 2-4 €; pubblico indiano/pakistano 1,5-3 €. Le visite sono stime a 18 mesi, non dati. I primi soldi arrivano solo quando la pubblicità (AdSense) è attiva sui siti; le affiliazioni nominate richiedono l'iscrizione di Massimiliano. Per confronto, i numeri veri della rete: EsameB1 114 visite a settimana, Visa Income 62 (settimana 19-26/10).

---

## 1. Attesa per la cerimonia di cittadinanza, council per council (voto 6,5, PASSA come sezione)

**Cosa.** Una pagina per ogni council australiano (539) con il numero ufficiale di persone approvate che aspettano la cerimonia e la percentuale che aspetta meno di 3 mesi, 3-6 mesi, oltre 6 mesi; una pagina per Stato con la classifica dei council più lenti e più veloci; una pagina nazionale con i tempi della cittadinanza per conferimento (dalla domanda alla decisione, dalla decisione alla cerimonia) e il numero di domande in lavorazione. Gli agenti leggono il JSON ogni mese e **tengono lo storico** (Home Affairs mostra solo l'ultimo mese: lo storico diventa nostro). Frase pronta per gli assistenti: "City of Casey: 2.416 approved applicants waiting; 97% attend a ceremony within 3 months (Home Affairs, updated 16 October 2026)".

**Fonte ufficiale (curl).**
- Pagina: `immi.homeaffairs.gov.au/citizenship/citizenship-processing-times/ceremony-wait-times` **200** (1,3 MB, la tabella non è nell'HTML).
- Dati: POST `https://immi.homeaffairs.gov.au/_layouts/15/api/Data.aspx/GetListData` con `{"webUrl": "/", "listName":"citizenshipCeremony"}` (gli stessi parametri scritti nella pagina) → **200, JSON 147.804 byte, 539 righe**, campi `Title` (council), `State`, `TotalApprovedApplicants`, `LessThanThreeMonths`, `WaitTime3To6Months`, `Wait_x0020_time_x0020_more_x0020` (oltre 6 mesi), `Modified` = **16/10/2026** su tutte le righe. Per Stato: WA 139, NSW 128, VIC 79, QLD 77, SA 68, TAS 29, NT 18, ACT 1. In tutto **67.636 persone approvate in attesa** (senza contare i council con "<5").
- I più grandi, letti: City of Casey 2.416 (97 % sotto 3 mesi), Blacktown 2.262 (92 %), Brisbane 2.074 (92 %; 5 % oltre 6 mesi), Canterbury-Bankstown 1.763 (72 %; 28 % 3-6 mesi), Moreton Bay 1.676 (72 %), Parramatta 1.610 (86 %), Gold Coast 1.527 (84 %; 7 % oltre 6 mesi), Hume 1.452 (97 %), Brimbank 1.434 (68 %; 31 % 3-6 mesi), Ipswich 1.238 (74 %), Stirling 1.195 (75 %), Wanneroo 1.154 (77 %).
- Tempi nazionali della cittadinanza: `immi.homeaffairs.gov.au/citizenship/citizenship-processing-times/citizenship-processing-times` **200**, "Last updated 16/10/2026"; i numeri stanno in un campo nascosto della pagina, leggibile: "90% of applications are processed within 5 months; 90% of approved applicants will have the opportunity to attend a ceremony within 6 months of approval", più la tabella per percentile e il numero di domande in lavorazione.
- Licenza: CC BY 3.0 AU (letta), attribuzione a Home Affairs.
- Date delle cerimonie: **non raccoglibili in modo affidabile**. Le pagine dei council provate: Blacktown 403, Parramatta 403, Brisbane e Gold Coast 404 sull'indirizzo provato, Casey 200 ma senza date ("unable to provide further information"), Penrith e North Sydney 200 senza date per il 2026-2027. La sezione si limita ai numeri ufficiali e rimanda al council per le date.

**Domanda (autocomplete Australia, inglese).**
- "citizenship ceremony wait times" → 10: "…by council", "…brisbane", "…melton council", "…canberra", "…cumberland council", "…wyndham council", "…gold coast".
- "australian citizenship processing time" → 10, compreso "**…by council**" e "…after test".
- Per council, sempre 10: "blacktown citizenship ceremony" (con "…wait times", "…dates 2026"), "casey citizenship ceremony" (con "casey council citizenship ceremony wait time"), "brisbane city council citizenship ceremony" (con "…waiting time"), "parramatta citizenship ceremony" (con "…wait time", "…dates 2027").
- Pubblico: circa 200.000 nuovi cittadini l'anno; oggi 67.636 persone approvate in attesa, ognuna cerca più volte il proprio council.

**Chi c'è su Google (ricerca web di oggi).** La pagina ufficiale (con la ricerca che funziona solo via script), le pagine dei singoli council (che dicono "3-6 mesi" a voce o rimandano al 131 880), righttoknow.org.au con richieste di accesso agli atti vecchie (Blacktown 1.472 in attesa nel 2024, Brisbane 9.535 nel 2021), myimmitracker con casi singoli del 2022-2023. **Nessun sito mette i numeri ufficiali council per council.** widen.com.au ha una sola pagina generica ("citizenship-ceremony-wait-time-after-approval"), nessuna per council (mappa del sito letta: 3.657 indirizzi). Battibile sulle ricerche per council e sugli assistenti AI; sulla ricerca "[council] citizenship ceremony" il council resta primo.

**Chi paga.** Solo pubblicità (AdSense quando attivo, pubblico australiano). Nessun affiliato adatto trovato: il passaggio successivo (passaporto australiano) non ha programmi. Nessun costo.

**Stima (calcolo).**
- Prudente: 25.000 visite l'anno × 1,4 pagine × 8 € / 1.000 = 280 € → **300 €**.
- Centrale: 70.000 visite (circa 5.800 al mese: 1-2 % della domanda per council più gli assistenti) × 1,4 × 10 € / 1.000 = 980 € → **1.000 €**.
- Ottimista: 180.000 visite × 1,4 × 12 € / 1.000 = 3.024 € → **3.000 €**.
- Primi soldi: 2-3 mesi dopo la pubblicazione (indicizzazione + citazioni), solo con AdSense attivo. Il traffico è costante tutto l'anno, con picchi intorno al 26 gennaio (Australia Day) e al 17 settembre (Citizenship Day), quando i council fanno le cerimonie grandi.

**Ore.** 10-15: un lettore del JSON (539 righe), un generatore di 539 pagine + 8 pagine di Stato + 1 nazionale, lo storico in un file, l'aggiornamento mensile **solo se `Modified` cambia** (regola dei crediti Netlify: una pubblicazione al mese).

**Rischi.** Se Home Affairs cambia il nome della lista o l'indirizzo, il lettore si ferma (la pagina ufficiale resta il riscontro). Pagine molto simili tra loro: servono il confronto con i council vicini, la posizione nello Stato e lo storico per non sembrare copie.

**Voto 6,5.** Dato ufficiale per luogo, fresco, con licenza aperta, che nessuno ha in pagine statiche; domanda vera per ogni council; perfetto per gli assistenti. Ma paga solo la pubblicità e il pubblico è di una sola nazione. Sotto l'asticella dei siti nuovi; **sopra quella delle sezioni**: si costruisce.

---

## 2. Tempi di lavorazione di tutti i visti australiani (voto 4,5, solo aggiunta)

**Cosa.** Una tabella con i tempi ufficiali di tutte le sottoclassi (visitatore, studente per settore, working holiday, lavoro, partner, genitori, qualificati) e lo storico mese per mese tenuto da noi.

**Fonte ufficiale (curl).** POST `https://immi.homeaffairs.gov.au/_layouts/15/api/GPT.aspx/GetVisaGlobalProcessingTime` con l'elenco delle sottoclassi → **200**, `success: true`, **94 righe per 47 sottoclassi**, campi `Percent25/50/75/90`, `Updated` "29 September 2026", `EndDate` "31 August 2026". Esempi letti: turista 600 mediana 21 giorni, 90 % in 33 giorni; working holiday 417 mediana 2 giorni, 90 % in 58; 462 mediana 3 giorni, 90 % in 44; studente 500 università mediana 16 giorni, 90 % in 4 mesi, formazione professionale mediana 53 giorni, 90 % in 7 mesi; partner 820 mediana 22 mesi, 90 % in 30; partner 309 mediana 21 mesi, 90 % in 32; 189 a punti mediana 61 giorni, 90 % in 8 mesi; 190 mediana 4 mesi, 90 % in 16; 482 Core Skills mediana 4 mesi; 188 "Processing times are not available". Licenza CC BY 3.0 AU. Non c'è il dato per Paese di chi chiede: solo per tipo di visto.

**Domanda.** Fortissima: "australia visa processing time" 10, "partner visa 820 processing time" 9 (con "2026", "reddit"), "subclass 500 processing time" 10 (con "…for pakistan"), "189 visa processing time" 10, "visitor visa australia processing time" 10 (con "…from india", "…philippines"); in India e Nepal "australia student visa processing time" 10 (con "…from india/pakistan/bangladesh").

**Chi c'è su Google.** widen.com.au: 44 pagine "processing-times/<sottoclasse>" + rapporti mensili "processing-times-report/2026-08" e "2026-09" (mappa del sito letta), pagina 820 aggiornata al 29/9 con la risposta in una riga; comparemigrationagents.pages.dev (sito automatico, "Updated 11 June 2026"); visatasker.com; decine di studi di migrazione con articoli "2026". Il formato che volevamo fare esiste già, fatto da chi guadagna con i clienti.

**Chi paga.** Pubblicità; nessun affiliato (i clienti valgono per gli studi di migrazione, che non pagano commissioni pubbliche).

**Stima.** 4.000 / 15.000 / 40.000 visite × 1,4 × 8-11 € / 1.000 = **50 / 200 / 600 €**.

**Ore.** 3-4 se si aggiunge alla sezione australiana "visa approval rates" in cantiere (stesso lettore Home Affairs, una tabella in più per pagina di visto).

**Voto 4,5.** Fonte ottima, ma un concorrente automatico e motivato c'è già. Vale solo come colonna in più dove abbiamo già il pubblico (tasso di approvazione + tempo + costo nella stessa pagina è un pacchetto che widen non ha per nazionalità).

---

## 3. Visto 462: posti usati e posti rimasti per Paese (voto 5,5, RISERVA alta)

**Cosa.** Per ognuno dei 30 Paesi con quota del Work and Holiday (462): quota annuale, stato di oggi (aperto, in pausa, sorteggio), **quanti primi visti sono già stati concessi nell'anno e quanti posti restano**, e l'anno scorso quanto si è riempita la quota. Pagine in inglese, spagnolo ("quedan cupos working holiday australia para chilenos") e portoghese (Brasile, Portogallo). Più i Paesi senza quota (USA, 417).

**Fonte ufficiale (curl).**
- Quote e stato: `immi.homeaffairs.gov.au/what-we-do/whm-program/status-of-country-caps` **200**, numeri nell'HTML, "Last updated 28/10/2026". Letto: Argentina aperto 3.400, Cile aperto 3.400, Spagna aperto 3.400, Perù aperto 1.500, Uruguay aperto 1.500, Brasile **in pausa** 500, Ecuador **in pausa** 100, Mongolia in pausa 100, Cina/India/Vietnam sorteggio (5.000 / 1.000 / 1.500), Indonesia sorteggio dal 2026 (5.000), Israele 2.500, Singapore 2.500, Thailandia 2.000, Polonia 1.500, Slovacchia 1.000, Malesia 1.100, Portogallo 500, Austria 500.
- Visti concessi: data.gov.au "Working Holiday Maker visa program" (BP0017), file `bp0017l-working-holiday-maker-visas` **200, XLSX 874.183 byte, last-modified 20/10/2026**, licenza **CC BY 3.0 AU**; tabella pivot con 112.885 righe (anno fiscale, trimestre, sottoclasse, sesso, età, cittadinanza, primo/secondo/terzo visto), fino al **30/9/2026**.
- Calcolo fatto oggi sull'anno 2025-26 (primi visti 462 / quota): Spagna 3.400/3.400 (**100 %**), Vietnam 1.500/1.500, India 1.000/1.000, Brasile 500/500, Mongolia e Papua 100/100, Portogallo 496/500, Malesia 1.091/1.100, Thailandia 1.911/2.000, Cile 2.880/3.400 (**85 %**), Perù 1.236/1.500 (82 %), Argentina 2.341/3.400 (**69 %**), Israele 1.226/2.500 (49 %), Polonia 514/1.500 (34 %), Singapore 484/2.500 (19 %), Uruguay 200/1.500 (13 %), Slovacchia 137/1.000, Grecia 48/500. Anno 2026-27 al 30/9: Cile 137, Spagna 126, Argentina 113, Stati Uniti 401 (senza quota). È il numero che chiede chi cerca "quedan cupos".

**Domanda.** Spagnolo: "working holiday australia cupo" → 10 ("cupos … para chilenos", "…peru", "…para argentinos", "…para españoles", "**quedan cupos working holiday australia**", "cupos disponibles…"); USA/inglese: "462 visa cap" 8 ("462 visa country caps", "462 visa quota"), "462 visa ballot" 10 ("…results date", "…india"); Argentina "working holiday 2026" 10.

**Chi c'è su Google.** yomeanimo.com (Cile: pagine per ogni working holiday, "Estos países ya no reciben solicitudes…", articolo sui Paesi in pausa aggiornato a luglio 2026, con assicurazione di viaggio in vendita), Chilevisión, T13, The Clinic, SBS in spagnolo (notizie), minrel.gov.cl. Nessuno pubblica i posti già usati calcolati dal file ufficiale; ma yomeanimo è forte e risponde alla domanda "c'è posto?" con lo stato aperto/in pausa.

**Chi paga.** Pubblicità (bassa per l'America Latina) + **assicurazione per lunghi soggiorni**: SafetyWing paga il **10 %** ai suoi "ambassador" (cifra riportata da directory di affiliazione e blog; la pagina ufficiale `safetywing.com/ambassador` non la scrive; `safetywing.com/affiliates` 404). Una copertura annuale costa diverse centinaia di dollari: commissione media prudente 25 € a polizza. SafetyWing è già nella lista della STRATEGIA ma **non ancora iscritto**.

**Stima (calcolo).**
- Prudente: 8.000 visite × 1,3 × 3 € / 1.000 = 31 € + 4 polizze (0,05 %) × 25 € = 100 € → **150 €**.
- Centrale: 25.000 visite × 1,3 × 4 € / 1.000 = 130 € + 20 polizze (0,08 %) × 25 € = 500 € → **600 €**.
- Ottimista: 60.000 visite × 1,4 × 5 € / 1.000 = 420 € + 60 polizze (0,1 %) × 30 € = 1.800 € → **2.200 €**.
- Primi soldi: luglio 2027 (nuovo anno delle quote, quando la ricerca esplode), solo con SafetyWing iscritto e AdSense attivo.

**Ore.** 8-12 (lettore della tabella pivot già scritto per BP0015 il 20/10: stesso formato; 30 pagine Paese in 3 lingue).

**Voto 5,5.** Numero nuovo e preciso, fonte aperta mensile, domanda reale in spagnolo; ma un concorrente locale forte, pubblico che vale poco in pubblicità, e la paga dipende da un affiliato non ancora attivo. Il 27/10 era 4 perché si guardava solo la pagina delle quote: con il calcolo dei posti rimasti sale, ma resta un'aggiunta.

---

## 4. Working holiday per nazionalità, tutte le destinazioni (voto 5, NO come sito)

**Cosa.** Per ogni passaporto (60 circa): in quali Paesi può fare la working holiday, età massima, quota, date di apertura, costo, durata, stato di oggi.

**Fonti (curl).** Australia aperta (sopra). Regno Unito (Youth Mobility, sorteggi per India, Giappone, Taiwan, Corea, Hong Kong): gov.uk aperto, già letto nei giri precedenti. **Canada IEC: `canada.ca` 000. Nuova Zelanda: `immigration.govt.nz` Incapsula (212 byte) su "working-holiday-visas".** Irlanda `dfa.ie` 403 (giro del 23/10). Canada e Nuova Zelanda sono le due destinazioni più cercate dopo l'Australia: senza di loro la tabella sarebbe incompleta o copiata da terzi.

**Domanda.** Molto ampia: "working holiday visa for" → 10 ("…us citizens", "…americans", "…mexican citizens", "…canadians", "…us citizens over 30"); "working holiday visa countries for" → 10 ("…uk citizens", "…indians", "…indonesian", "…singaporeans", "…malaysian"); "working holiday visa age limit" 8; Spagna "visa working holiday" 10; Francia "pvt canada 2026" 10 ("…quota", "…tirage", "…ronde").

**Chi c'è su Google.** pvtistes.net (francese, fortissimo), yomeanimo (Cile), gooverseas, theteflacademy, interexchange, smartertravel, wherecani.live, beyondthestates: guide per nazionalità già scritte, molte con assicurazioni affiliate.

**Chi paga.** Assicurazioni lunghe (SafetyWing 10 %, non iscritto), pubblicità.

**Stima.** Centrale: 60.000 visite × 1,4 × 6 € / 1.000 = 500 € + 30 polizze × 25 € = 750 € → **1.250 €**; prudente 300 €, ottimista 4.000 €.

**Ore.** 40-60 (sito nuovo, 60 nazionalità × 15 destinazioni, molte regole in prosa da controllare a mano).

**Voto 5.** Domanda grande, ma due fonti principali chiuse dal server e concorrenti forti in ogni lingua. NO come sito; le parti australiane entrano nell'idea 3.

---

## 5. Costi ufficiali dei visti australiani e canadesi nella valuta di chi paga (voto 5, RISERVA)

**Cosa.** Tariffa ufficiale di ogni visto (Australia, Canada) convertita in rupie indiane e pakistane, yuan, peso filippino, naira, con la data del prossimo aumento (Australia ogni 1° luglio; Canada "fee changes").

**Fonti (curl).** Australia: POST `/_layouts/15/api/data.aspx/GetVisaPrices` → risposta con dati parziali (studente 500: **AUD 2.500** base, 1.530 per adulto in più, 500 per minore) e l'errore "Visa prices are currently unavailable" per altre sottoclassi: fonte instabile. Canada: `ircc.canada.ca/english/information/fees/fees.asp` **200**, "Date modified 2026-09-21": la lista delle tariffe si legge. Nuova Zelanda chiusa. Cambi: BCE senza PKR, NGN, BDT (giro del 30/10); servirebbero la Reserve Bank of Australia o la Bank of Canada (non provate oggi).

**Domanda.** "australia visa fees" 10 ("…for indian", "…in indian rupees", "…for pakistani", "…increase 2026"); India: "australia student visa fees" 10 ("…in indian rupees 2026", "…in inr"), "australia visitor visa fees" 10 ("…in indian rupees"); Canada: "ircc fees" 10, "canada citizenship fees" 10 ("…2026", "…increase").

**Chi c'è su Google.** Le pagine ufficiali (stimatore dei prezzi australiano, lista IRCC), consulenti indiani (canapprove, ecc.), studi di migrazione. Il buco è solo la valuta locale.

**Chi paga.** Pubblicità con pubblico indiano/pakistano (bassa) + Wise per chi paga dall'estero (non iscritto, cifra per cliente non letta oggi).

**Stima.** Centrale: 50.000 visite × 1,3 × 3 € / 1.000 = 195 € + Wise circa 200 € → **400 €**; prudente 100 €, ottimista 1.200 €.

**Ore.** 10-15.

**Voto 5.** Simile al "costo del visto di studio nella valuta di chi paga" del 30/10 (voto 6): oggi in più c'è la lista canadese leggibile, ma la fonte australiana dei prezzi è a metà. Da aggiungere solo se la sezione australiana in cantiere va bene.

---

## 6. Test di cittadinanza australiano: pratica in inglese, cinese e vietnamita (voto 4,5, NO)

**Fonte.** Il libretto ufficiale "Our Common Bond" (Home Affairs, CC BY 3.0 AU, tradotto in molte lingue). Le domande vere del test **non sono pubbliche**: le domande di pratica andrebbero scritte da noi, con rischio di errori. Regole note e ripetute da tutti: 20 domande, 45 minuti, 75 %, le 5 domande sui valori tutte giuste.

**Domanda.** Forte: "australian citizenship test" 10 ("…practice", "…practice free", "…50 questions pdf", "…2026"); cinese "澳洲入籍考试" 10 ("题库2026", "中英文题库", "app"); vietnamita "thi quốc tịch úc" 10 ("…bằng tiếng việt", "luyện thi…"). In hindi, nepalese e punjabi quasi niente (0-4).

**Chi c'è su Google.** Più di 15 app ("Citizenship Test AU 2026", "Australian Citizenship 2026"…), ausmocktest.pages.dev (automatico), easy-prep.org, emigratelawyers (50 domande), firstmigrationservice (in cinese), SBS in cinese con video per capitolo.

**Chi paga.** Pubblicità. **Stima** 100 / 500 / 2.000 €; **ore** 25-35.

**Voto 4,5.** Mercato pieno, contenuto da inventare (non è un dato ufficiale da riportare), nessun vantaggio per gli assistenti AI. NO.

---

## 7. Visti per genitori (143, 103, 804, 864): date di rilascio della coda (voto 4, NO come pagina a sé)

**Fonte.** Pagine Home Affairs "Parent visas – queue release dates and processing times" (la pagina delle priorità familiari `…/visa-processing-priorities/family-visa` **200**, "Last updated 7/10/2026", rimanda alla pagina delle date; l'indirizzo provato per la pagina delle date dava 404, da ritrovare).

**Domanda.** "143 visa queue" 10 ("…calculator", "…release date"), "parent visa queue release" 9, "contributory parent visa processing time" 10.

**Chi c'è.** Studi di migrazione con calcolatori della coda. Un numero per sottoclasse, che cambia poche volte l'anno.

**Stima** 30 / 150 / 500 €; **ore** 3-5. **Voto 4**: al massimo una riga nella tabella dei tempi (idea 2).

---

## 8. Canada: tempi IRCC, pool IEC, test di cittadinanza (voto 3, NO confermato)

- `https://www.canada.ca/content/dam/ircc/documents/json/data-ptime-en.json` → **000** (la connessione arriva al server e si ferma durante la stretta di mano cifrata; anche `canada.ca/en.html`). È un blocco del server verso di noi: non si aggira.
- Si leggono: `ircc.canada.ca/english/helpcentre/…` **200**; lista delle tariffe IRCC **200** (21/9/2026); file aperti IRCC solo con il nome esatto: `www.ircc.canada.ca/opendata-donneesouvertes/data/IRCC_AdhocSR_TR_0003_E.csv` 200, `IRCC_AdhocSR_PR_0004_E.csv` 200, `EN_ODP-TR-Work-IMP_PT_program_sign.xlsx` 200; l'elenco della cartella è **403**, `open.canada.ca` **000**. Il file IEC per Paese non l'ho trovato (8 nomi provati, tutti 404).
- Domanda forte ("ircc processing time" 10, "pvt canada 2026 quota/tirage/ronde" 10), ma senza la fonte non si fa. Resta NO, come il 14/10, 18/10, 23/10, 27/10 e 30/10.

## 9. Nuova Zelanda: INZ e cittadinanza (voto 3, NO)

- `www.immigration.govt.nz/` e tutte le pagine provate (tempi, working holiday, statistiche) → 200 ma **212 byte con lo script Incapsula** (protezione anti-robot): non si aggira.
- `passports.govt.nz` **403**; pagina cittadinanza di `govt.nz` 200 ma senza tempi; `dia.govt.nz/Citizenship-Processing-times` 404.
- Domanda c'è ("nz citizenship processing time" 10, "nz visa processing time" 10 con "…for indians", "nz working holiday visa" 10), ma la fonte è chiusa. NO.

---

## Fonti lette il 31/10/2026

- Home Affairs, tempi di tutti i visti: POST `https://immi.homeaffairs.gov.au/_layouts/15/api/GPT.aspx/GetVisaGlobalProcessingTime` (corpo `{"gptRequest":[{"VisaSubclassCode":"600","StreamCode":""},…]}`), 200, JSON, aggiornato 29/9/2026; script della pagina `immi.homeaffairs.gov.au/AssetLibrary/dist/js/app.gpt.js`
- Home Affairs, attesa cerimonie per council: POST `https://immi.homeaffairs.gov.au/_layouts/15/api/Data.aspx/GetListData` (corpo `{"webUrl": "/", "listName":"citizenshipCeremony"}`), 200, 539 righe, 16/10/2026; pagina `https://immi.homeaffairs.gov.au/citizenship/citizenship-processing-times/ceremony-wait-times`
- Home Affairs, tempi della cittadinanza: `https://immi.homeaffairs.gov.au/citizenship/citizenship-processing-times/citizenship-processing-times` (200, 16/10/2026)
- Home Affairs, prezzi: POST `https://immi.homeaffairs.gov.au/_layouts/15/api/data.aspx/GetVisaPrices` (risposta parziale)
- Home Affairs, quote 462: `https://immi.homeaffairs.gov.au/what-we-do/whm-program/status-of-country-caps` (200, 28/10/2026)
- Home Affairs, licenza: `https://www.homeaffairs.gov.au/access-and-accountability/using-our-website/copyright-and-disclaimer` (200, CC BY 3.0 AU)
- data.gov.au, Working Holiday Maker visa program (BP0017): `https://data.gov.au/data/dataset/602f74a0-a588-4dea-ae28-0fe123cbb182/resource/5c1d8ab0-6d3e-4667-bc63-dfd12dfa6055/download/bp0017l-working-holiday-maker-visas` (200, 20/10/2026, CC BY 3.0 AU)
- IRCC: `https://ircc.canada.ca/english/information/fees/fees.asp` (200, 21/9/2026); `https://www.canada.ca/…/data-ptime-en.json` (000)
- INZ: `https://www.immigration.govt.nz/…` (Incapsula)
- Concorrenti letti: `https://www.widen.com.au/processing-times/820/` e mappa `https://www.widen.com.au/sitemap-0.xml` (3.657 indirizzi, 44 pagine di tempi, 1 pagina generica sulle cerimonie); `https://comparemigrationagents.pages.dev/processing-times/`; `https://www.visatasker.com/australian-visa-processing-times/`; yomeanimo.com; ausmocktest.pages.dev
- Affiliazione: SafetyWing 10 % (affilimate.com, referly; pagina ufficiale `https://safetywing.com/ambassador` senza cifra)
