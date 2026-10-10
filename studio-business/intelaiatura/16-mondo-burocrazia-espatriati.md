# Angolo B — Burocrazia per chi si trasferisce / nomadi digitali (fuori dall'Italia)

Data: **10 ottobre 2026**. Ricerca fatta dal server della sessione con autocomplete Google, ricerche web e prove `curl` sulle fonti ufficiali.
Cartella: `scratchpad/globale/B/`. Dentro ci sono `dl/` (71 file scaricati, 8 MB, letti solo con `python3 -I`; autocomplete grezzo in `ac1.json`, `ac2.json`, `ac_fr.json`) e `script/` (scanner e liste di parole).
Nessun file del repository è stato toccato.

**Criterio, scritto prima di cominciare** (è lo stesso degli studi 7 e 14, adattato). Un'idea passa se ha tutte e quattro queste cose:
1. Domanda confermata nell'autocomplete in almeno 2 mercati su 3 (USA, Regno Unito, Australia), oppure nella lingua locale se il pubblico è locale.
2. Al massimo 3 fonti ufficiali per pagina, leggibili dal server (risposta 200), con licenza o natura di atto pubblico che permetta di riusarle.
3. Nessun sito dominante che risponda già bene. Sono ammessi i siti ufficiali, purché non abbiano pagine indicizzabili per ogni caso.
4. Un ricavo prudente realistico e un rischio legale basso: lo strumento applica solo regole pubblicate, cita la fonte con la data e dice "verifica con l'ente".

Avvertenza onesta: **i volumi di ricerca non si possono misurare dal server** (Google Trends risponde 429, come nello studio 14). Le visite qui sotto sono quindi **stime di ordine di grandezza**, non misure.

---

## 0. Risposta in breve

- Ho provato **130 parole chiave** (108 inglesi in 3 mercati USA, UK, AU, più 22 in francese) e **circa 70 URL ufficiali**. La domanda c'è quasi ovunque: 105 parole chiave inglesi su 108 hanno suggerimenti in 3 mercati su 3. Come nello studio 14, **il collo di bottiglia è la fonte**, e in più qui pesa la **concorrenza**: i temi "visto" sono pieni di studi legali e di nuovi siti scritti con l'AI.
- **Ho trovato una fonte molto forte e poco sfruttata**: il dataset ufficiale francese **"Tarifs taxe de séjour – DELTA"** della DGFiP. Ha **1.504.175 righe**, licenza **Licence Ouverte 2.0**, aggiornamento del 29/06/2026, **10.645 comuni con tariffe 2026**, un'API JSON senza chiave e il totale con le maggiorazioni già calcolato. Parigi 2026 coincide al centesimo con Which? (palace 15,93 €, 5 stelle 11,70 €, 4 stelle 8,45 €), mentre altri siti riportano numeri sbagliati.
- **Le 3 idee migliori:**
  1. **Tourist Tax Calculator** (Francia comune per comune, più Spagna, Grecia e circa 12 città). È la migliore per la fonte, è lo stesso pubblico di Italy Strikes e risponde a una domanda "calculator" in decine di città.
  2. **Visa Income Checker**: soglie di reddito per visti nomadi, pensionati e Blue Card, calcolate da indici ufficiali (salario minimo, IPREM, salario medio) e cambio BCE del giorno. È quella che rende meglio per visita (assicurazioni, Wise, avvocati al 5 %), ma ha la concorrenza più forte.
  3. **Driving Licence Exchange Checker** (Germania con l'Anlage 11 FeV e Spagna con la tabella DGT, aggiornata il 26/06/2026). La fonte è ottima e la concorrenza media, ma rende poco.
- **Nessuna è grande.** Stime prudenti a 18 mesi: 0,5–2,1k €/anno (tasse di soggiorno), 0,6–3k €/anno (visti), 0,2–0,9k €/anno (patenti). Sono **satelliti** dello stesso motore, non un nuovo "Italy Strikes".

---

## 1. Tabella di tutte le verifiche (con verdetto)

Legenda della domanda: "3/3" significa suggerimenti presenti in USA, UK e AU. Legenda delle fonti: 200 = leggibile dal server; 403/404/SSL = bloccata o rotta.

| # | Idea | Domanda (autocomplete, esempi reali) | Fonte ufficiale provata (HTTP) | Concorrenza (ricerca web) | Verdetto |
|---|---|---|---|---|---|
| 1 | **Tasse di soggiorno Francia** (comune per comune) | FR: "taxe de séjour par commune", "calcul taxe de séjour non classé", "taxe de séjour 2026 le lavandou / biarritz / saint hilaire de riez", "calcul taxe de séjour arcachon / la rochelle / marseille"; EN 3/3: "paris tourist tax calculator / per night / children / airbnb" | **DGFiP DELTA** `data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/delta_deliberation_ts_tarif0` → **200**, JSON, 1,5 M righe, 10.645 comuni 2026, Licence Ouverte 2.0. Seconda fonte per scegliere i comuni turistici: **INSEE** "Capacité des communes en hébergement touristique 2026" (200, CSV/XLSX) | C'è un simulatore ufficiale (app, senza pagine per comune) più blog e uffici del turismo. Per "Le Lavandou 2026" nessuna griglia chiara nei risultati; per Parigi un sito (Insurte) dà solo la tariffa base, cioè un numero sbagliato | **PASSA (la migliore)** |
| 2 | **Tasse di soggiorno Spagna** (Catalogna/Barcellona, Baleari) | 3/3: "barcelona tourist tax calculator / 3 star hotel / airbnb 2026", "mallorca tourist tax calculator / children / how to pay", "tourist tax calculator spain / ibiza / menorca" | ATC Generalitat `atc.gencat.cat/ca/tributs/ieet/` **200** (con l'elenco dei nuovi recàrrecs municipali dal **01/10/2026**: Castelldefels, L'Hospitalet, El Prat, Sabadell, Sant Cugat…); ATIB Baleari **200** (poco testo, serve la legge sul BOIB); pagina di Barcellona 404 | Hostaway (guida per città), Holidu (calcolatore), ETOA (tabelle "last reviewed" a febbraio-marzo **2025**: vecchie), hotel e blog con cifre in conflitto (Barcellona 12 € oppure 15 €) | **PASSA** come parte della n. 1 |
| 3 | Tasse di soggiorno in altre città (Vienna, Berlino, Praga, Budapest, Amsterdam, Lisbona, Porto, Atene/Grecia, Dubrovnik, Edimburgo) | 3/3 per tutte, con "calculator" in Amsterdam, Praga, Vienna, Berlino, Budapest, Dubrovnik ed Edimburgo; "greek climate tax calculator" | Vienna **200** (3,2 % fino al 30/6/2026, **5 % dall'1/7/2026, 8 % dall'1/7/2027**); Edimburgo 200; Amsterdam 403; Lisbona 403; AADE (Grecia) 403; Praga errore SSL; mint.gov.hr errore SSL; Berlino 404 (indirizzo sbagliato) | Hostaway, Holidu, mappr, radicalstorage, Time Out e Which? (articoli). Sono frammentati e spesso in disaccordo tra loro | **PASSA con riserva**: una pagina per città, fonte di riserva = testo di legge o ordinanza; controllo annuale |
| 4 | **Soglie di reddito per visti** (nomadi, pensionati, Blue Card) con familiari a carico e valute | 3/3 e ricchissima: "spain digital nomad visa income requirements family of 4 / with spouse / in php / for filipinos", "portugal d7 visa income requirements 2026", "croatia / estonia / cyprus / czech … income requirements", "digital nomad visa income requirements by country", "eu blue card salary threshold germany 2026 / hungary / netherlands", "highly skilled migrant salary 2026" | BCE (cambi) `data-api.ecb.europa.eu` **200** CSV (USD, GBP, PHP, INR, THB, MXN al 09/10/2026); BOE (SMI 2026: RD 126/2026, **1.221 €×14 = 17.094 €/anno**); Portogallo vistos.mne.gov.pt **200** ("four monthly minimum guaranteed remuneration") più RMMG 2026 **920 €** (DL 139/2025); **Croazia** MUP **200** ("2,5 salari netti medi… oggi **3.622,50 €**"); Grecia, Cechia, Estonia, Ungheria, EAU 404; Malta 403; AIMA errore SSL; Spagna inclusion.gob.es 403 | **Forte**: Portugalist, remoteworkeurope, movingto, nomad.watch, citizenremote, studi legali (Costa Luz, NIM, Migratiolex) e molti siti nuovi fatti con l'AI. Però **i numeri sono spesso sbagliati**: Spagna "2.762 €" contro i corretti **2.849 €**; Croazia "3.295 €" contro gli ufficiali **3.622,50 €**; Portogallo "3.480 €" (2025) contro **3.680 €** | **PASSA con riserva** (concorrenza forte; il vantaggio è il calcolo automatico più il cambio) |
| 5 | **Conversione della patente** (posso cambiare la mia patente USA/UK/IN… in DE/ES/PT/NL/IE/FR?) | 3/3: "can i exchange my us driver's license in spain / germany / france", "which countries can exchange driving license in germany / spain", "indian / pakistani / bangladeshi driving licence exchange in portugal", "exchange driving licence netherlands 30 ruling" | **Germania**: FeV Anlage 11 `gesetze-im-internet.de/fev_2010/xml.zip` **200** (XML ufficiale, Stand "geändert 12.8.2026", con stati USA, province canadesi e prove richieste per classe; atto pubblico); **Spagna**: DGT "Países con convenio de canjes" **200**, tabella HTML con **32 Paesi**, aggiornata il **26/06/2026** (USA, Canada, Australia e India **non** ci sono); Portogallo IMT 200 (da analizzare); RDW NL 200 ma la lista è caricata con JavaScript; NDLS Irlanda 403 Cloudflare; Francia: nessuna lista attuale leggibile (ANTS è JavaScript; l'unico PDF prefettizio è del 2020) | The Local (articolo del 2024), simplegermany, pagina dell'ambasciata, gestorie spagnole. Le liste "non coincidono", lo dicono gli stessi risultati | **PASSA (piccola)**: solo DE ed ES all'inizio |
| 6 | "Cita previa" NIE/TIE/extranjería: posti disponibili | 3/3 fortissima ("nie appointment madrid / barcelona", "cita previa extranjeria huella") | **Nessun dato ufficiale di disponibilità**. Leggerla con un robot vorrebbe dire usare bot sul sistema della Polizia | Polizia spagnola: **69 arresti (maggio 2023)** per bot che bloccavano e rivendevano citas; 2 arresti a Valencia (settembre 2024); "mercato nero" ancora attivo (The Local, marzo 2025) | **SCARTATA** (rischio legale e nessuna fonte) |
| 7 | Anmeldung Berlino: trovare un appuntamento | 3/3 ("anmeldung appointment finder", "anmeldung berlin termin") | service.berlin.de (non provato: bot) | **allaboutberlin.com/appointments** c'è già dal 2022, "approvato dalla città di Berlino", più bot su GitHub | **SCARTATA** (c'è già) |
| 8 | Portogallo NHR/IFICI, Spagna Beckham law: calcolatori | 3/3 ("ifici tax calculator", "beckham law salary calculator") | Leggi pubbliche | Studi fiscali, Big4 | **SCARTATA**: è consulenza fiscale (vietata dalle regole) |
| 9 | Golden visa: soglie (GR, PT, ES) | 3/3 ("greece golden visa 2026 / properties") | Grecia gov 403 (studio 14); in Spagna il golden visa è stato abolito, in Portogallo la via immobiliare è stata tolta | Studi legali e agenzie immobiliari dominano | **SCARTATA** (consulenza d'investimento, soglie statiche) |
| 10 | Blue Card, 30 % ruling, HSM, Critical Skills: soglie di stipendio | 3/3 | Ufficiali, una all'anno | **Forte**: The Local, EY, Make it in Germany (ufficiale e in inglese), studi legali; la cifra tedesca 2026 (50.700 €) è giusta ovunque | **Solo come modulo della n. 4**, non come sito a sé |
| 11 | Messico: reddito per la residenza temporanea o permanente | 3/3 ("mexico residency requirements by consulate", "mexico minimum wage 2026 in usd") | gob.mx risponde "Challenge Validation" (1.805 byte) su SRE e CONASAMI; l'API Banxico vuole un token. **Ogni consolato applica cifre proprie** | Mexperience e simili | **RISERVA** (fonte bloccata e responsabilità: la cifra la decide il consolato) |
| 12 | Costa Rica, Panama, Colombia, Thailandia (DTV/LTR), Bali E33G, EAU, Georgia, Turchia | 3/3 per quasi tutte (Costa Rica "pensionado income" e Colombia "m visa income" 0/3) | Costa Rica 403; Panama 200; Colombia 200; Thailandia (app) 200; Indonesia 200; EAU 404; Turchia 200 | Moltissimi blog | Solo come **schede della n. 4** quando la soglia è fissa (USD o THB) e la pagina ufficiale risponde 200 |
| 13 | Calendari scolastici per famiglie espatriate | 3/3 ("france school holidays 2026 zone b", "spain school holidays 2026 madrid", "germany … bavaria") | **Ottime**: Francia `data.education.gouv.fr` **200** (218 righe per il 2026-27); Olanda `opendata.rijksoverheid.nl` **200** JSON; KMK 200; Portogallo DGE 200 | **Forte**: Connexion, FrenchEntrée, service-public in inglese, sortiraparis. Le date sono fissate un anno prima: nessun vantaggio "live" | **SCARTATA come sito**; al massimo una pagina utile dentro altri siti |
| 14 | Apostille: lista dei Paesi | 3/3 ma soprattutto Pakistan e India ("apostille countries list mofa") | HCCH (status table) | HCCH domina; pubblico a basso RPM | **SCARTATA** |
| 15 | Iscrizione al sistema sanitario: passaggi | – | Nessun dato strutturato, solo testi | Guide e forum | **SCARTATA** (testo libero, responsabilità) |
| 16 | Validatori NIE/NIF/BSN/PPSN (cifra di controllo) | 3/3 ("nif portugal check / generator", "bsn number format", "nie number how many digits") | Algoritmi pubblici, nessun dato da aggiornare | Molti strumenti gratuiti | **SCARTATA come sito**; al massimo widget gratuiti dentro la n. 4 |
| 17 | Crit'Air / zone a basse emissioni | 3/3 ("crit air sticker official website uk") | – | green-zones, urbanaccessregulations, ufficiale ANTS; molti siti truffa | **SCARTATA** (fuori dal nostro angolo, concorrenza e rischio "sito non ufficiale") |
| 18 | Festivi e aperture domenicali | 3/3 | Calendari statici | timeanddate domina (già scartata nello studio 14) | **SCARTATA** |
| 19 | Schengen 90/180, ETIAS | – | – | Già scartata nello studio 7 | **SCARTATA** |
| 20 | (nota per l'Italia) Imposta di soggiorno comune per comune | – | **Nessun dataset nazionale**: solo delibere PDF sul portale del federalismo fiscale | – | Oggi non costruibile; la Francia sì |

---

## 2. Le candidate che passano, con tutte le prove

Ipotesi comuni per i ricavi (le stesse degli studi 7, 12 e 14): RPM pubblicità per pubblico Tier 1 **5–12 $** (prudente 6 $); pubblico francese **2–4 €** (stima mia, non misurata); pubblico di Filippine, India e Pakistan **≤ 1–2 $**. Cambio 1 $ ≈ 0,92 €. Programmi di affiliazione (cifre pubbliche):
- SafetyWing 10 %, cioè 6,27 $ a vendita Essential (studio 12);
- **Genki** 5 % "refer a friend" / 10 % "professional partner" sul piano Explorer, 2,5 % / 5 % sul piano Resident, 100–300 € una tantum sui piani Native (tabella ufficiale su staygenki.notion.site);
- **Wise** CPA da **10 £** per cliente privato e da 50 £ per cliente business (guida ufficiale per gli affiliati);
- **NIM Immigration Lawyers (Barcellona)**: **5 %** sul servizio pagato, tracciamento 90 giorni, pagamento anche da 0 € (pagina "refer and earn", letta oggi). Il loro prezzo non l'ho verificato: con 1.000–2.000 € a pratica sarebbero 50–100 € a cliente;
- **Legal Fournier**: programma partner, cifra non pubblica;
- **Smoobu** (software per chi affitta case) **10 % ricorrente**; Lodgify 20–30 % (dato di un aggregatore);
- **Booking.com**: dal giugno 2025 ha **chiuso i piccoli affiliati diretti** (Skift, 30/5/2025), ora si passa da CJ o Awin (circa 4 % dichiarato, non verificato); **Stay22** non pubblica la sua quota (secondo le testimonianze, dal 30 al 55 % della commissione).

### 2.1 "Tourist Tax Calculator Europe" (inglese, più francese per la Francia) — **la migliore**

**Cosa fa.** Una pagina per città o comune risponde a: "quanto pago di tassa di soggiorno a X, per N notti, M adulti, bambini, categoria Y?". Mostra il totale, la tariffa ufficiale, la data dell'atto e il link. Ha anche una tabella "cosa cambia il prossimo 1° gennaio / 1° luglio" (esempi veri: Vienna 5 % → 8 % dall'1/7/2027; Catalogna, nuove maggiorazioni comunali dall'1/10/2026; Barcellona +1 €/anno fino a 8 €).

**Domanda** (autocomplete, 10/10/2026):
- EN 3/3: "barcelona / paris / amsterdam / vienna / prague / budapest / dubrovnik / berlin / edinburgh / mallorca tourist tax **calculator**", "tourist tax calculator spain / greece / ibiza / menorca", "greek climate tax calculator", "… 3 star hotel", "… children", "… airbnb 2026";
- FR: "taxe de séjour **par commune**", "calcul taxe de séjour non classé / airbnb / 2026", "taxe de séjour 2026 le lavandou / biarritz / lyon / nice / saint hilaire de riez", "tarif taxe de séjour la rochelle / aix-les-bains / canet-en-roussillon / sainte-maxime", "taxe de séjour airbnb italie / espagne / portugal / allemagne".

Ci sono due pubblici: i **viaggiatori** (lo stesso di Italy Strikes Today) e chi **affitta casa** (in Francia, molti proprietari britannici di gîte). Chi affitta ha un bisogno ripetuto: deve riscuotere e versare la tassa.

**Fonti** (massimo 3 per pagina):
- **Francia**: (1) DGFiP DELTA. Risposta 200, API JSON senza chiave, **Licence Ouverte 2.0**, ultima modifica 29/06/2026, 272.750 righe con data d'effetto 2026, 10.645 comuni. Ogni riga ha categoria, tariffa, unità (€ oppure % per i non classificati), periodi, maggiorazioni dipartimentali e regionali e `tarif_total`. Controlli fatti oggi:
  - Parigi 2026: 5 stelle **11,70 €**, 4 stelle **8,45 €**, palace **15,93 €**, non classificati 5 % fino a 16,25 € (in linea con Which? e con il tetto di 15,93 € citato da Ulysse ed economie.gouv);
  - Chamonix 2026: 4 stelle 2,60 €;
  - Nizza 2025: 4 stelle 2,60 €, non classificati 5 % (totale 6,70 € con la maggiorazione).
  
  (2) INSEE, capacità ricettiva per comune 2026 (200, CSV), per scegliere i 300–500 comuni più turistici e non pubblicare 10.000 pagine vuote.
- **Spagna**: ATC Generalitat (IEET con l'elenco dei recàrrecs, 200) e legge o ATIB per le Baleari (200).
- **Grecia**: legge nazionale sulla "climate resilience fee". AADE risponde 403, quindi serve il testo di legge.
- **Altre città**: una pagina ufficiale ciascuna (Vienna 200, Edimburgo 200). Dove il sito blocca (Amsterdam, Lisbona) si usa l'ordinanza pubblicata nel bollettino ufficiale.

**Concorrenza.** Per l'inglese: Hostaway (guide per host, forte), Holidu (calcolatore unico), mappr, radicalstorage, ETOA (tabelle riviste nel 2025, quindi vecchie) e articoli di giornale. Per il francese: simulatore ufficiale (app), uffici del turismo, Chekin, Ulysse. **Prova della debolezza**: per Barcellona, nei risultati, le cifre vanno da 12 a 15 €; per Parigi, Insurte dà solo la tariffa base (3,50 €), e per "Le Lavandou 2026" nessuna pagina mostra la griglia ufficiale.

**Ricavo prudente** (stime, non misure):
- **12 mesi: 150–700 €.** Su 20–60k pagine viste: pubblicità 100–400 € (mix di traffico EN e FR) più affiliazioni 50–300 € (hotel via Stay22 o CJ, GetYourGuide, Smoobu per gli host, Welcome Pickups).
- **18 mesi: 0,5–2,1k €/anno.** Su 60–200k pagine viste: pubblicità 350–1.500 € più affiliazioni 150–600 €.
- La stagionalità è bassa: si viaggia tutto l'anno e gli host dichiarano ogni trimestre.

**Ore**: 20–30. Servono il lettore DELTA e INSEE, lo schema "città → regole", il calcolatore nel browser, circa 40 pagine EN delle città principali, 300–500 pagine FR per comune e un controllo mensile della data `modified` del dataset più un controllo settimanale dell'impronta (hash) delle pagine ufficiali.

**Rischi**:
- Rischio legale **basso**: si applica una tariffa pubblicata, con la data e la scritta "l'importo finale lo decide la struttura e il comune".
- La struttura DELTA ha delle stranezze: 2025 e 2026 mescolati e Parigi registrata come "VILLE DE PARIS". Si mostra solo l'anno più recente per categoria e si confrontano a campione i 30 comuni principali.
- Google potrebbe considerare "sottili" (poco utili) troppe pagine per comune: per questo si parte solo da quelle con capacità ricettiva ≥ soglia INSEE.
- Il canale hotel di Booking è chiuso ai piccoli: resta Stay22 o CJ.

**Test tecnico a costo zero (soglie scritte prima):**
1. **Copertura**: dei 100 comuni francesi con più posti letto (INSEE), almeno **90** devono avere righe DELTA con data d'effetto 2026, oppure 2025 senza un atto successivo. Sotto 90, solo pagine EN delle città.
2. **Esattezza**: per 30 comuni confronto con la pagina ufficiale del comune o dell'ufficio del turismo. Serve almeno **28/30** di coincidenza al centesimo, altrimenti non si pubblica il francese.
3. **Fonti estere**: per 12 città, almeno **8** devono avere una fonte ufficiale leggibile dal server (pagina o bollettino) con la tariffa in vigore. Sotto 8, si pubblicano solo Francia e Spagna.
4. **Mercato** (dopo la pubblicazione, con la pubblicazione settimanale): a 45 giorni almeno **25 pagine indicizzate** e almeno **300 impressioni/settimana** in Search Console. Se non ci sono, si chiude come gli altri siti al verdetto.

### 2.2 "Visa Income Checker" (inglese): "Ho abbastanza reddito per il visto X, con la mia famiglia, nella mia valuta?"

**Cosa fa.** Si sceglie il visto, il numero di familiari e la valuta, e si inserisce il reddito. Lo strumento risponde "sopra o sotto la soglia ufficiale del 2026" e mostra il calcolo: indice ufficiale × percentuale di legge × cambio BCE del giorno. Esempi calcolati oggi da fonti ufficiali:
- **Spagna visto nomadi** = 200 % dello SMI = 2 × 17.094/12 = **2.849 €/mese** (≈ 3.193 $ o 200.561 PHP al cambio BCE del 9/10); più 75 % dello SMI per il primo familiare e 25 % per ogni altro;
- **Spagna non lucrativo** = 400 % dell'IPREM = 2.400 €/mese, più 100 % per ogni familiare (IPREM 600 €, dato di fonti secondarie ancora da verificare sul BOE);
- **Portogallo visto nomadi** = 4 × RMMG = **3.680 €**, **D7** = 920 €;
- **Croazia** = 2,5 salari netti medi = **3.622,50 €** (lo dice il MUP), più 10 % per familiare.

Il pezzo automatico: quando cambia l'indice (SMI, RMMG, salario medio croato o ceco, Beitragsbemessungsgrenze per la Blue Card) la pagina si aggiorna da sola, e il cambio cambia ogni giorno.

**Domanda.** È la più forte di tutto lo studio: "income requirements **family of 4 / family of 3 / with spouse / in php / for filipinos**", "portugal d7 visa income requirements 2026", "non lucrative visa income requirements for a couple", "digital nomad visa income requirements by country", "eu blue card salary threshold hungary 2026 / netherlands / spain", "thailand retirement visa requirements for uk citizens", "panama pensionado visa income requirements". È proprio una domanda da calcolatore: familiari e valuta.

**Fonti** (massimo 3 per scheda): l'indice nazionale (BOE, Diário da República tramite DGERT, statistica croata o ceca), la pagina del ministero o del consolato con la regola, e i **cambi BCE** (`data-api.ecb.europa.eu`, 200, ogni giorno lavorativo; nella lista ci sono PHP, INR, THB, MXN, USD, GBP, AUD, CAD; mancano PKR e NGN). Su 20 visti provati, la pagina ufficiale risponde 200 per circa la metà (Portogallo, Croazia, Thailandia, Panama, Colombia, Indonesia, Turchia, BOE). Gli altri sono bloccati o hanno cambiato indirizzo, e per loro bisogna partire dal testo di legge.

**Concorrenza: forte.** Ci sono Portugalist, remoteworkeurope (già aggiornati a 3.680 €), movingto, nomad.watch, citizenremote, Global Citizen Solutions, studi legali spagnoli e decine di siti AI nuovi (wheretoemigrate, lottalingo, expatlife.ai). Però **molti numeri sono sbagliati** (Spagna 2.762 contro 2.849, Croazia 3.295 contro 3.622,50, famiglie calcolate male) e **nessuno fa il calcolo con familiari e valuta su più Paesi** a partire dall'indice ufficiale. Il vantaggio c'è, ma è stretto.

**Ricavo prudente:**
- **12 mesi: 200–1.200 €.** Su 10–40k visite, pubblicità con RPM misto basso (molta Asia) 50–250 €; assicurazione sanitaria per il visto (Genki 5–10 %, SafetyWing 6 $) 50–400 €; Wise 10 £ per cliente 30–150 €; 0–4 clienti avvocato al 5 % (NIM), 0–400 €.
- **18 mesi: 0,6–3k €/anno.** Il tetto più alto arriva solo con un accordo scritto per contatto con uno studio (come la regola già decisa per Smart Move Italy: ≥ 150 €/cliente).

**Ore**: 25–40 (15–20 visti, regole con familiari, BCE, controlli delle pagine ufficiali, testi "check with the consulate").

**Rischi**:
- **Responsabilità media**: i consolati possono chiedere di più (lo dicono le stesse fonti: "your consulate can ask for more"). Va sempre scritto "minimo legale, il consolato decide", senza promesse di "qualifichi".
- Gli indici a volte vengono **prorogati** e non pubblicati (l'IPREM "in attesa della legge di bilancio"): la pagina deve dire "in vigore dal… secondo…".
- La concorrenza è forte: potremmo non entrare nella prima pagina di Google.

**Test tecnico a costo zero:**
1. Per 20 visti, almeno **15** devono avere una regola scritta in una fonte ufficiale leggibile (200) e un indice ufficiale con data. Sotto 15, si fa solo Europa (ES, PT, HR, GR, CZ).
2. I numeri ufficiali già pubblicati (Croazia 3.622,50; Portogallo 4×920; Spagna 200 % SMI) devono essere riprodotti **al centesimo 3 su 3**.
3. Lettore BCE silenzioso per 14 giorni: almeno **95 %** di risposte 200 e nuovo dato ogni giorno lavorativo.
4. Mercato a 60 giorni: almeno **500 impressioni/settimana** sulle query "income requirements" e almeno 1 clic affiliato ogni 200 visite. Se non ci sono, resta solo come pagina interna di Retire/Move to Italy.

### 2.3 "Driving Licence Exchange Checker" (inglese): "Posso convertire la mia patente di [stato/Paese] in [Germania/Spagna]?"

**Domanda**: 3/3 ("can i exchange my us driver's license in spain / germany / france", "which countries can exchange driving license in germany / spain", "exchange uk driving licence in spain", "indian / pakistani / bangladeshi driving licence exchange in portugal", "exchange driving licence netherlands 30 ruling").

**Fonti**:
- **Germania**: FeV Anlage 11 in XML ufficiale (200, modifica del 12/8/2026). Contiene Paese o **stato USA o provincia canadese**, classi, e se servono la prova teorica e/o pratica. Esempio letto: "Pennsylvania C nein nein", "Texas C … nein", "Republik Korea 1, 2 nein nein". È un atto pubblico, riusabile.
- **Spagna**: tabella DGT con **32 Paesi** (aggiornata il 26/06/2026), con data dell'accordo, permessi, prove e tassa.
- Poi Portogallo (IMT 200, da analizzare). Olanda e Irlanda sono oggi illeggibili (JavaScript, Cloudflare); la Francia non ha una lista attuale leggibile.

**Concorrenza: media.** The Local (articolo del 2024), simplegermany, l'ambasciata tedesca e le gestorie spagnole: secondo gli stessi risultati di ricerca, "le liste non coincidono".

**Ricavo prudente**:
- **12 mesi: 50–300 €** (5–25k visite);
- **18 mesi: 0,2–0,9k €/anno**.

Le affiliazioni sono deboli: Wise, corsi di lingua, al massimo assicurazione auto. Resta soprattutto la pubblicità per un pubblico USA/UK.

**Ore**: 12–20. Il rischio legale è basso (si riporta l'atto e si scrive "la Führerscheinstelle o la DGT decide"). Bisogna però stare attenti alle **note a piè di pagina** dell'Anlage 11 (numeri 1–22), che cambiano il senso: vanno tradotte una per una.

**Test tecnico**:
1. Il parser dell'Anlage 11 deve estrarre **100 %** delle righe (Paesi più stati USA) e coincidere con la pagina HTML ufficiale a campione (20 righe, **20/20**).
2. La tabella DGT deve dare 32 Paesi con tutte le colonne; il controllo settimanale della data "Fecha actualización" deve segnalare le modifiche entro 7 giorni.
3. Mercato a 60 giorni: almeno 15 pagine indicizzate e almeno 150 impressioni/settimana. Altrimenti diventa solo una sezione del sito Visa/Move.

### 2.4 (Riserva piccola) Calendari scolastici FR/NL in inglese
Le fonti sono le migliori di tutte (Francia: API data.education.gouv.fr 200, 218 righe per il 2026-27; Olanda: API rijksoverheid 200). Però la concorrenza inglese è forte e le date sono fissate un anno prima. **Da fare solo come pagina gratuita dentro il Tourist Tax** ("quando le spiagge francesi sono piene"): 2–4 ore, ricavo trascurabile da sola.

---

## 3. Scartate e perché (con prova)

| Idea | Prova |
|---|---|
| Cita previa NIE/TIE | Nessun dato ufficiale di disponibilità. Leggerla in automatico è ciò che la Polizia persegue: 69 arresti nel maggio 2023 per bot che rivendevano appuntamenti a 30–200 €; nuovi arresti a Valencia nel settembre 2024; The Local (marzo 2025): il mercato nero continua |
| Anmeldung Berlino | allaboutberlin.com/appointments esiste dal 2022, "approved by the city of Berlin", interroga ogni 3 minuti; in più ci sono bot open source su GitHub |
| NHR/IFICI, Beckham law | Domanda alta ("ifici tax calculator", "beckham law salary calculator"), ma è consulenza fiscale: esclusa dalle regole |
| Golden visa / residenza per investimento | Consulenza d'investimento; siti governativi greci 403; dominano studi legali e agenzie immobiliari; soglie che cambiano per legge, non per indice |
| Blue Card / 30 % ruling / HSM / Critical Skills come sito | La cifra giusta (DE 2026: 50.700 €, ridotta 45.934,20 €) è già ovunque, anche sul portale ufficiale in inglese: solo come modulo della 2.2 |
| Messico residenza | gob.mx risponde "Challenge Validation"; l'API Banxico vuole un token; le cifre cambiano da consolato a consolato ("requirements by consulate" è proprio la domanda) |
| Costa Rica rentista/pensionado | migracion.go.cr 403; "costa rica pensionado income" 0/3 |
| Apostille | HCCH domina; domanda soprattutto da PK/IN ("apostille countries list mofa") |
| Sanità: iscrizione | Nessuna fonte strutturata; testo libero con responsabilità |
| Validatori NIE/NIF/BSN | Nessun dato da aggiornare, molti strumenti già gratuiti, nessun ricavo; al massimo widget |
| Crit'Air / ZFE | Fuori dal nostro angolo; green-zones e urbanaccessregulations dominano; molti siti truffa che fanno pagare l'adesivo |
| Festivi, Schengen, ETIAS | Già scartati negli studi 7 e 14 (timeanddate, siti UE ufficiali) |
| Imposta di soggiorno Italia | Nessun dataset nazionale (solo delibere PDF): non costruibile oggi, a differenza della Francia |

---

## 4. Ordine consigliato e onestà sulle dimensioni

1. **Tourist Tax Calculator**: prima il test tecnico DELTA e INSEE (circa 2 ore, solo Claude). Se passa, si costruisce come **satellite di Italy Strikes Today** (stesso pubblico di viaggiatori, stesse affiliazioni) più la sezione francese per gli host.
2. **Visa Income Checker**: si costruisce come pezzo del futuro "Retire / Move to Italy", allargato all'Europa del Sud (stesso pubblico relocation, stessi partner). Ha senso soprattutto se arriva un accordo scritto con uno studio (NIM 5 %, Legal Fournier, o un partner con cifra ≥ 150 €/cliente).
3. **Driving Licence Checker**: solo dopo i verdetti del 23–24/11, come sezione dello stesso sito relocation.

**Quanto è grande tutto questo?** Messo insieme, a 18 mesi, la stima prudente è **1,3–6k €/anno lordi**, e solo se Google indicizza. È la stessa conclusione degli studi 7 e 14: **tanti satelliti piccoli sullo stesso motore**, nessuna miniera. La Francia (DELTA) è la scoperta migliore di questo studio: è l'unica fonte "tutti i comuni, aperta, aggiornata" trovata nell'angolo relocation e viaggi. Il visto ha il valore per cliente più alto ma la concorrenza più dura.

**Cosa deve fare Massimiliano**: niente per i test (nessun account). Per i ricavi servono le iscrizioni (10 minuti ciascuna, quando si accende un sito): Stay22, Wise, Genki partner, NIM "refer and earn". Nessuna email a freddo: sono tutte iscrizioni a programmi pubblici.

---

## 5. Fonti principali (lette oggi)
- DGFiP DELTA: `data.economie.gouv.fr/explore/dataset/delta_deliberation_ts_tarif0` (Licence Ouverte 2.0, 1.504.175 righe, modificato il 29/06/2026); abbattimenti: `delta_deliberation_ts_abattement`.
- INSEE: `insee.fr/fr/statistiques/2021703` (capacità ricettiva 2026, CSV/XLSX).
- ATC Catalogna: `atc.gencat.cat/ca/tributs/ieet/`; Vienna Ortstaxe: `wien.gv.at/.../ortstaxe.html`.
- BCE: `data-api.ecb.europa.eu/service/data/EXR/...` (cambi del 9/10/2026).
- Spagna SMI 2026: RD 126/2026 (BOE 19/2/2026), 1.221 €/mese e 17.094 €/anno (legaltoday, Fieldfisher).
- Portogallo RMMG 2026: DL 139/2025, 920 € (DGERT); vistos.mne.gov.pt (regola dei "four monthly minimum").
- Croazia: `mup.gov.hr/.../temporary-stay-of-digital-nomads/286833` (3.622,50 €).
- Germania: `gesetze-im-internet.de/fev_2010/anlage_11.html` e `xml.zip`.
- Spagna DGT: `dgt.es/.../paises-con-convenio-de-canjes/` (aggiornata il 26/06/2026).
- Affiliazioni: wise.com/gb/blog/affiliate-onboarding-guide; staygenki.notion.site (tabella delle commissioni); nimextranjeria.com/immigration-lawyers-barcelona/refer-and-earn/; legalfournier.com/en/partners/; smoobu.com (partner 10 %); skift.com (30/5/2025, Booking taglia gli affiliati).
- Concorrenza e prove: Which? (tasse di soggiorno 2026), ulysse.com (Parigi 15,93 €), insurte.com (cifre base), etoa.org (tabelle del 2025), hostaway.com, holidu, mappr.co; portugalist.com, remoteworkeurope.eu, migratiolex, gpa.net (2.762 €); thelocal.de/.es; allaboutberlin.com/appointments.
