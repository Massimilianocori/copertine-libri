# Ricerca di zona del 30/10/2026: Canada, Australia, Nuova Zelanda

Richiesta di Massimiliano: "il mondo è molto più grande, ci sono più opportunità e tu non le stai trovando". Obiettivo: idee da voto 8-9 per siti o sezioni automatici (script Python, dati ufficiali, Netlify), pagati da AdSense e da affiliazioni con nome.

Vincoli di sempre: nessuna spesa senza il suo sì, niente email a freddo, niente social, niente vendita diretta, niente consulenza legale, medica o finanziaria personalizzata.

**Zona di questa ricerca:** Canada, Australia, Nuova Zelanda. Altri ricercatori seguono i "cloni di EsameB1" (esami e pratiche per stranieri), i "numeri ufficiali che spostano soldi", gli USA e il Regno Unito: ho evitato di sovrapporre il lavoro.

**Riletti prima:** `ESPLORATE.md` per intero e i tre rapporti `ricerca-profonda-2026-10-28-*.md`. Non ho rivalutato le idee già chiuse. Quando un fatto nuovo cambia un voto, lo scrivo.

---

## 0. Risposta in breve

**Nessuna idea arriva a 8 in questa zona con le prove di oggi.** Ho guardato 21 famiglie in 8 settori: casa, tasse locali, energia, salute, scuola, lavoro e immigrazione, auto, viaggi interni. Ho fatto 70 interrogazioni all'autocomplete (gl=ca, au, nz), 12 ricerche su Google e circa 45 prove con curl dal server.

**La migliore è una sezione nuova a voto 7: "Guidare in Canada, Australia e Nuova Zelanda con una patente straniera", provincia per provincia e Paese per Paese.** Ha tre punti a favore:
- la domanda è enorme e ripetuta;
- in Google ci sono blog e pagine automatiche deboli;
- chi cerca vive spesso già in Canada o in Australia, quindi la pubblicità vale come per un pubblico canadese o australiano, non come per il Paese d'origine.

Non arriva a 8 per tre motivi:
- metà delle fonti ufficiali non si legge dal server (Victoria, South Australia, Tasmania, ACT, Northern Territory, Nuova Zelanda, Québec);
- chi paga per i nuovi arrivati (preventivi auto) paga poco o non pubblica la cifra;
- la stima prudente resta sotto i 1.000 €/anno.

**Lezione della zona.** Canada, Australia e Nuova Zelanda pubblicano molti dati aperti. Proprio per questo i buchi "grandi" sono già occupati, spesso da siti automatici nuovi su `pages.dev`:
- `billhero.com.au` fa una pagina per ogni codice postale con i piani elettrici;
- `whysolar.com.au` confronta i rimborsi del fotovoltaico per venditore;
- `catax-tools.pages.dev` ha l'aliquota della tassa sulla casa per ogni città dell'Ontario;
- `the-northern-office.pages.dev` copre la sanità fuori provincia;
- `anzscosearch.com` copre i punteggi per occupazione.

Il buco resta dove la regola è **scritta in prosa, diversa per provincia o Stato, e cambia con una data**. La patente straniera è proprio questo caso: nel Nuovo Galles del Sud la regola è cambiata il 1/2/2026, in Western Australia cambia il 31/10/2026.

| # | Candidata | Tipo | Voto | €/anno a 12 mesi (prud. / centr. / ott.) | €/anno a 18 mesi (prud. / centr. / ott.) | Prima entrata | Ore |
|---|---|---|---|---|---|---|---|
| 1 | **Guidare con la patente straniera in CA/AU/NZ** (visitatori, nuovi residenti, conversione per Paese, passaggio tra province) | sezione nuova di Before You Fly (o sito nuovo) | **7** | 100 / 450 / 2.000 | 300 / 1.200 / 5.500 | AdSense dal 2°-3° mese; DiscoverCars dopo l'iscrizione | 22-35 |
| 2 | Snowbird canadesi: giorni fuori provincia per non perdere la sanità, giorni negli USA, contatore | sezione di Visa Income Checker | 6 | 50 / 200 / 800 | 150 / 500 / 2.000 | AdSense; Red Helm 3 $ a contatto | 10-15 |
| 3 | Piani elettrici australiani per codice postale (fonte CDR nuova e perfetta) | sito nuovo | 5 | – | 100 / 400 / 1.500 | – | 30-45 |
| 4 | Affitto medio per sobborgo dai depositi cauzionali (NSW, VIC, QLD) | sito nuovo | 5 | – | – | – | – |
| – | Altre 17 famiglie | | NO (2,5-4,5) | | | | |

**Il passo che costa zero e vale di più** è costruire la n. 1 insieme a due idee già in lista, perché usano lo stesso partner (DiscoverCars) e lo stesso motore delle sezioni passaporto di Before You Fly:
- "guidare all'estero con la tua patente" (28/10, voto 7,5);
- "pedaggi con l'auto a noleggio" (29/10, voto 7).

Insieme formano un unico blocco "Before you drive" in entrambe le direzioni: chi parte da CA/AU/UK e chi arriva in CA/AU/NZ. È la regola del 29/10: i 5.000 € si raggiungono sommando sezioni con lo stesso partner e lo stesso pubblico. Anche sommate, la stima prudente resta intorno a 1.500-4.000 €/anno.

---

## 1. Candidata 1 (voto 7): guidare in Canada, Australia e Nuova Zelanda con una patente straniera

### 1.1 L'idea in una riga
Una pagina per ogni coppia "provincia o Stato × patente di provenienza". Ogni pagina risponde a quattro domande:
1. Posso guidare da visitatore, e per quanto?
2. Serve il permesso internazionale o una traduzione?
3. Da residente, posso convertire senza esami, oppure devo fare l'esame teorico e la prova su strada? Vale l'esperienza?
4. Che cosa è cambiato e da quando?

Ogni pagina riporta la frase ufficiale, il link e la data di controllo. Ci sono poi pagine per i passaggi tra province ("can I drive in BC with an Ontario G2").

### 1.2 Domanda (autocomplete del 30/10)
- ca: "can i drive in canada with" → 10: *us license, uk license, **indian license**, australian license, international license, uae license, **philippine license**, german license, g1, us learner's permit*.
- ca: "can i drive in ontario with" → 10, tra cui *indian license, foreign license, philippine license, uk licence, bc license, alberta license, quebec learners permit*. "can i drive in bc with" → 10, tra cui *indian license as a student, foreign license, uk license, ontario g2*. "can i drive in alberta with" → 10, tra cui *indian license, foreign license, uk license, ontario license*.
- au: "can i drive in australia with" → 10: *uk license, us license, **indian license**, nz license, international license, malaysia license, foreign license, canadian license, indonesia license*. "can i drive in nsw with" → 10, tra cui *overseas licence, indian license, uk licence, vic license*. "overseas licence conversion" → 10, tra cui *victoria, nsw, nz, south australia, qld, tasmania*.
- nz: "can i drive in nz with" → 10: *aus license, **indian license**, canadian license, philippine license, us license, uk licence*. "convert overseas licence nz" → 10, tra cui *fees*.
- ca: "how long can i drive an out of province car in" → *ontario, bc, alberta, saskatchewan*. "car insurance for newcomers" → 10, tra cui *to canada, calgary, alberta, best… ontario, cheapest… to canada*.

Sono più di 10 famiglie da 10 varianti, ripetute in tre Paesi. È la stessa forma della domanda "do I need an international driving permit for [Paese]" (28/10), ma nella direzione opposta: chi arriva, non chi parte.

### 1.3 Google oggi
- "can i drive in canada with indian license": in prima pagina `calendar-uk.co.uk` (pagine FAQ automatiche di bassa qualità), pickyourtrail, `uk.qeeq.com` (noleggio, coppie di Paesi automatiche), il forum di settlement.org, `tyremap.com/as-tourist/driving-in-canada-as-india-tourist/` (coppie automatiche), giornali indiani, Remitly, brokerlink. **Nessuna pagina provinciale ufficiale.** I risultati si contraddicono: 60 giorni, 90 giorni, 3 mesi, 6 mesi.
- "can i drive in australia with indian license": stessi `calendar-uk.co.uk` (tre pagine), giornali indiani, SBS Punjabi, paytm, qeeq. Il riassunto di Google stesso avverte che una fonte "di bassa qualità" scrive "indefinitely".
- "can I drive in Ontario with Indian license convert G2 experience": guide per nuovi arrivati (translayte, drivezee, trubicars), `welcomeaide.com` (pagine in 7 lingue sull'Ontario 2026: concorrente nuovo da seguire), un caso dell'Ombudsman dell'Ontario.
- Pagina per Paese senza provincia: `drivingintheworld.pages.dev/destinations/canada/`, già visto il 28/10 per la direzione opposta.

**Il buco:** nessuno incrocia provincia o Stato, Paese della patente e data del cambio. Per Ontario e Alberta le pagine ufficiali esistono ma non sono in prima pagina per le query con il nome del Paese. La pagina ufficiale dell'Ontario per i visitatori porta "Updated: May 14, 2021".

### 1.4 Fonti (curl dal server, 30/10/2026)
| Giurisdizione | URL | Esito | Cosa c'è |
|---|---|---|---|
| Ontario, conversione | `ontario.ca/page/exchange-out-province-drivers-licence` | **200**, 104 KB | elenco dei Paesi con accordo nell'HTML: Australia, Austria, Belgio, Croazia, Francia, Germania, Gran Bretagna, Ungheria, Danimarca, Isola di Man, Giappone, Corea del Sud, Kosovo, Nuova Zelanda, Irlanda, Svizzera, Taiwan, Ucraina |
| Ontario, visitatori | `ontario.ca/page/drive-ontario-visitors` | **200** | "less than 3 months… valid driver's licence" |
| Alberta | `alberta.ca/exchange-non-alberta-licences` + PDF `transportation.alberta.ca/.../ReciprocalLicensing.pdf` | **200** / **200** | Paesi con la classe (es. "Poland (Class 5)", "Taiwan (Class 5)"); licenza Open Government Licence – Alberta |
| British Columbia | `icbc.com/driver-licensing/moving-bc` | **200**, 219 KB | 90 giorni per convertire; pagine per USA, Cina, India, Regno Unito; "© ICBC. All rights reserved" (si riprendono i fatti, non i testi) |
| Nova Scotia | `novascotia.ca/exchange-your-out-of-province-drivers-licence/` | **200** | tabella Paese × classe straniera × classe NS |
| Québec (SAAQ) | percorso provato | 404 | da trovare l'URL giusto |
| Saskatchewan (SGI) | percorso provato | 404 | da trovare |
| Manitoba (MPI) | home | 200 | pagina da trovare |
| Nuovo Galles del Sud | `nsw.gov.au/.../knowledge-and-driving-test-exemptions` | **200**, 143 KB | elenco dei Paesi + "From 1 February 2026, Experienced Driver Status from certain countries ceased to operate in NSW"; licenza CC BY 4.0 del governo NSW |
| Queensland | `qld.gov.au/transport/licensing/driver-licensing/overseas/transfer/exempt-countries` | **200** | elenco; "Last updated: 29 May 2026" |
| Western Australia | `transport.wa.gov.au/.../transfer-recognised-jurisdiction` | **200**, 293 KB | Paesi nuovi dal **31/10/2026** (Polonia, Corea del Sud, Taiwan, Romania, Slovenia, secondo la ricerca su Google; nell'HTML statico la data non compare: forse in una sottopagina) |
| Victoria (VicRoads) | `vicroads.vic.gov.au/licences/overseas-drivers/...` | **403** | chiuso |
| South Australia | PDF `sa.gov.au/.../Overseas_Licence_Holders-05-25.pdf` | **403** | chiuso |
| Tasmania | `transport.tas.gov.au/.../converting_an_overseas_licence` | **000** | chiuso |
| ACT, Northern Territory | `transport.act.gov.au`, `nt.gov.au/driving/...` | **403** | chiusi |
| Nuova Zelanda (NZTA) | `nzta.govt.nz/driver-licences/new-residents-and-visitors/...` | 200 ma 212-962 byte: **pagina anti-robot Incapsula** | chiuso |

Si leggono **7 giurisdizioni su 21**: Ontario, Alberta, BC, Nova Scotia, NSW, Queensland, Western Australia. Sono però le più cercate, tranne Victoria. Gli elenchi cambiano poche volte l'anno. Lo script legge le pagine aperte e segnala ogni cambiamento del testo. Per quelle chiuse servono una lettura da GitHub Actions (da provare) oppure un elenco scritto a mano con data e link. Questa seconda strada va contro la regola "tutto automatico" e quindi abbassa il voto.

### 1.5 Chi paga
- **AdSense.** Chi cerca "can I drive in Ontario with Indian license" o "car insurance for newcomers Ontario" di solito vive già in Canada. Gli annunci sono quelli dell'assicurazione auto canadese, tra le parole più care del mercato. Valore assunto: 6-10 € ogni 1.000 pagine viste sulle pagine dei nuovi residenti; meno sulle pagine dei visitatori indiani e filippini.
- **DiscoverCars** (pagina affiliati 200 il 30/10): "~$20 per booking", "Cookie Lifetime: 365 days", conversione media dichiarata 3-5 %. Vale per i visitatori da USA, Regno Unito, Germania, Malesia, Indonesia. È lo stesso partner delle idee del 28 e 29/10.
- **Preventivi auto per i nuovi arrivati (Canada).** Kanetix: 1-4 $ a contatto, cifra presa da un elenco di terzi (affpaying), non dal programma. RATESDOTCA: "will pay you for each valid lead", cifra non pubblica; la pagina affiliati risponde 000/403 dal server. È da verificare se accettano un iscritto italiano.
- **Wise** per i nuovi residenti che spostano soldi (programma già nel piano).

### 1.6 Stima
Circa 600-800 pagine (13 giurisdizioni canadesi e 8 australiane × circa 25 Paesi di patente, più la Nuova Zelanda e i passaggi tra province). Ne entra nell'indice una parte.

| | 12 mesi | 18 mesi |
|---|---|---|
| Pagine viste al mese (prud. / centr. / ott.) | 1.000 / 4.000 / 12.000 | 2.500 / 8.000 / 25.000 |
| € ogni 1.000 pagine (AdSense + affiliazioni) | 8 / 10 / 14 | 8 / 12 / 18 |
| **€/anno** | **100 / 450 / 2.000** | **300 / 1.200 / 5.500** |

### 1.7 Ore (riusando i motori)
22-35 ore:
- parser per 7 pagine ufficiali e classificazione delle frasi in "si converte" / "esami" / "esperienza riconosciuta": 8-12;
- tabella Paese × giurisdizione con il motore per nazionalità di `visaincome/`: 6-8;
- pagine, indici per provincia e per Paese, dati strutturati: 6-10;
- controllo settimanale dei cambiamenti: 2-5.

### 1.8 Voto
**7**: domanda 3 · buco 1,5 · fonte 1 (7 su 21, licenze miste ma si riprendono fatti) · valore 1 · rischi e ore 0,5.

**Cosa la porta a 8:**
1. VicRoads, SA e NZTA leggibili da GitHub Actions (prova di 1 ora);
2. un programma di preventivi auto canadese che accetta l'iscrizione con almeno 10 $ a contatto;
3. almeno 150 visite a settimana a 30 giorni dalla pubblicazione delle prime 100 pagine (Ontario, BC, Alberta, NSW, Queensland × 15 Paesi).

**Rischi.**
- È vicina alla corsia "pratiche per stranieri" di un altro ricercatore: va coordinata.
- Non scrivere mai "puoi guidare" senza la riga su assicurazione e noleggio.
- Before You Fly è ancora lontano dalla prima pagina: se la sezione nasce lì, ne eredita la debolezza.

---

## 2. Candidata 2 (voto 6): snowbird canadesi

**Domanda.**
- ca: "snowbird rules" → 10 (*for canadians, usa, changing, tax rules, new snowbird rules*);
- "how long can you be out of province for ohip" e "out of province medical coverage" → 10 per provincia (*ontario, bc, pei, newfoundland, alberta, quebec, saskatchewan, manitoba*);
- "how many days can a canadian stay in the us" → 10;
- "snowbird insurance" → 10 (*cost, cost per month, florida*);
- "travel insurance for seniors over 70/75/80 canada" → 10.

**Fonti.** ontario.ca OHIP 200 (regola dei 212 giorni). Gli URL provati per BC e Alberta rispondono 404 (le pagine esistono con altri percorsi). RAMQ del Québec 403, travel.gc.ca (percorso provato) 404.

**Google.** `the-northern-office.pages.dev/provincial-health-coverage-residency/on/` (pagine automatiche per provincia), healthquotes.ca, snowbirds.org, Canada Life, finiki. Le fonti si contraddicono sulla copertura dell'Ontario fuori dal Paese.

**Chi paga.** Il pubblico è ricco, ma TuGo accetta solo affiliati "Canadian individual or organization" e quindi è escluso. Red Helm paga 3 $ a contatto. Resta AdSense con annunci di assicurazioni per anziani.

**Limiti.** Le pagine sono poche (13 province più 4-5 Stati USA). Il tema è vicino alla salute.

**Voto 6.** Sezione di Visa Income Checker accanto all'attesa per la tessera sanitaria (riserva del 29/10): 150-2.000 €/anno a 18 mesi, 10-15 ore.

---

## 3. Fonte nuova da ricordare (voto 5 come idea): i piani energetici australiani in formato CDR

**Fatto nuovo.** L'ente regolatore australiano pubblica **tutti i piani luce e gas di tutti i venditori** in formato aperto e senza chiave, per legge (Consumer Data Right, "Product Reference Data"):
- elenco dei venditori: `api.cdr.gov.au/cdr-register/v1/energy/data-holders/brands/summary` (header `x-v: 1`) → **200, 84 venditori**;
- piani: `cdr.energymadeeasy.gov.au/{venditore}/cds-au/v1/energy/plans?page-size=1000` (header `x-v: 1`) → **200**: AGL da solo ha 941 piani elettrici a mercato libero, con codici postali e rete di distribuzione;
- dettaglio: `.../plans/{planId}` (header `x-v: 3`) → **200**, con prezzi per fascia oraria, quota fissa e rimborsi del fotovoltaico (es. AGL 0,02 $/kWh dal venditore, 0,44 $/kWh dal premio governativo).

L'API dà solo i piani in vigore oggi: niente storico, niente piani futuri. Non ho trovato il testo della licenza: la pagina `aer.gov.au` risponde 000 dal server.

**Domanda.**
- au: "best solar feed in tariff" → 10 (*nsw, qld, victoria, sa, brisbane, adelaide, qld 2026*);
- "cheapest electricity plans" → 10 per Stato;
- "default market offer" → 10 (*2026-27, nsw, south australia, victoria, qld*);
- "battery rebate" → 10 per Stato.

**Google.**
- Rimborsi del fotovoltaico: solarcalculator.com.au, solarquotes, `whysolar.com.au/feed-in-tariffs/nsw/origin-energy` (pagine automatiche per venditore, "396 plans"), IPART, energymatters.
- Piani più economici: `billhero.com.au/electricity/lota-4179` (**una pagina per codice postale**), wattever per rete, finder, `switch-save.pages.dev`, `wattcompare.pages.dev`.

**Verdetto.** Il buco è chiuso: altri usano già questa fonte con pagine per codice postale. **Voto 5. NO come sito**, ma la fonte va annotata.

Probabilmente esiste la stessa API anche per i prodotti bancari (tassi dei conti di risparmio per banca), che il 21/10 avevamo dato per inesistente. **Non l'ho provata**, e Canstar, finder, RateCity e Mozo sono comunque fortissimi.

---

## 4. Le altre famiglie (bocciate, con la prova principale)

| Famiglia | Prova | Voto |
|---|---|---|
| Affitto medio per sobborgo (AU, depositi cauzionali NSW/VIC/QLD, CC BY) | au "median rent" → 10 per città; Google per "median rent Parramatta 2026": OnTheHouse (centinaia di pagine automatiche), microburbs, blog con cifre che vanno da 480 a 700 $/settimana. La fonte ufficiale manca dai risultati, ma OnTheHouse e realestate/Domain sono troppo forti | 5 (RISERVA debole) |
| Affitto medio per città (CA) | ca "average rent in" → 10; rentals.ca, zumper, liv.rent con i rapporti mensili (non ricontrollato stasera) | 4 |
| Aliquota della tassa sulla casa per città (Ontario) | ca "property tax rate" → 10; in Google `catax-tools.pages.dev/property-tax-<città>/` con l'aliquota 2026 per ogni città, liv.rent, ifinancecanada | NO (3,5) |
| Land transfer tax, stamp duty, aiuti alla prima casa | autocomplete 10 per Stato/provincia, ma calcolatori ufficiali di ogni ufficio delle entrate, banche, broker | NO (3) |
| Piani elettrici, DMO/VDO, fotovoltaico (AU) | sez. 3 | 5 |
| Tariffe elettriche per provincia (CA) | ca "electricity rates" → 10 per città; ogni azienda e il regolatore rispondono (non approfondita) | 4 |
| Attese per gli interventi chirurgici per provincia (CA) | ca "surgery wait times" → 10 per provincia; motore ufficiale BC per ospedale, chirurgo e intervento (`swt.hlth.gov.bc.ca`, 000 dal server), dataset BC su open.canada.ca; tema sanitario | NO (4) |
| Liste d'attesa per il medico di famiglia (CA) | ca "family doctor waitlist" → 10 per provincia; la domanda è "come iscriversi", risponde la provincia | NO (3,5) |
| Risultati NAPLAN per scuola (AU) | au "naplan results by school 2026" → 10; nessuna classifica ufficiale, My School pubblica scuola per scuola; in Google pagine spazzatura (`old.media-azi.md`), Better Education, giornali. I termini di riuso di My School vanno letti prima (non letti stasera) | NO (3,5) |
| Punteggi minimi delle selective school (NSW) | au "selective school cut off marks" → 10; scuole di ripetizione già prime; nessuno che paghi (non approfondita) | 4 |
| Corsi TAFE gratuiti 2027 per Stato (AU) | au "free tafe courses 2027" → 8 per Stato; elenchi degli Stati e dei TAFE; nessuna affiliazione verificata (non approfondita) | 4,5 |
| Inviti SkillSelect per occupazione (189/190/491) | au "189 invitation points" → 10, "190 nsw invitation round" → 10; data.gov.au non ha il dataset (ricerca "skillselect": 1 risultato non pertinente); anzscosearch.com domina | NO (3,5) |
| Estrazioni PNP per provincia (OINP, BC PNP, AAIP) | ca "oinp/bc pnp/aaip draw" → 10 ciascuna; pagine provinciali e CIC News. Express Entry già NO il 14/10; `canada.ca` risponde **000** anche oggi, quindi i JSON delle estrazioni e dei tempi IRCC restano chiusi | NO (4) |
| Tempi IRCC per tipo di domanda | ca "ircc processing time" → 10; `canada.ca` 000; NO confermato (14/10, 23/10, 27/10) | NO (3) |
| Elenco dei datori LMIA (CA), datori accreditati AEWV (NZ) | autocomplete 6 e 10; stessa famiglia degli elenchi degli sponsor (NO il 14/10); pubblico all'estero che vale poco | NO (4) |
| Costo della registrazione auto per Stato (AU, "rego") | au "how much is rego in qld for" → 10 (*4/6/8 cilindri*, *pensioner*); la risposta è la tabella dell'ente; pochi soldi oltre AdSense (non approfondita) | 4,5 |
| Multe per velocità e punti della patente per Stato (AU) | au "speeding fines" e "demerit points" → 10 per Stato; tabelle ufficiali di ogni Stato, studi legali (non approfondita) | 4 |
| Assicurazione auto per codice postale (Ontario) | ca "car insurance rates by postal code ontario" → 7; nessun dato ufficiale per codice postale | NO (3) |
| Aumenti della tassa comunale per consiglio (NZ) | nz "rates increase" → 10 per città; 78 consigli con piani propri (filtro duro), giornali | NO (4) |
| Prenotazioni Parks Canada, Great Walks (NZ) | autocomplete 10; risponde l'ente (stesso verdetto dei parchi NPS del 14/10) | NO (3) |

---

## 5. Righe proposte per `ESPLORATE.md` (da copiare a mano: questo rapporto non modifica altri file)

```
## Ricerca di zona del 30/10/2026: Canada, Australia, Nuova Zelanda
Nessuna idea a 8. Lezione: i dati aperti della zona sono già usati da siti automatici su pages.dev e da comparatori (billhero per codice postale, whysolar, catax-tools, the-northern-office, anzscosearch); il buco resta dove la regola è in prosa, diversa per provincia o Stato e con una data di cambio. Prove in `ricerca-zona-canada-australia-2026-10-30.md`.
| Nicchia | Esito | Studio |
|---|---|---|
| **Guidare in Canada, Australia e NZ con la patente straniera, per provincia/Stato × Paese** (Ontario, Alberta, BC, Nova Scotia, NSW, QLD, WA 200; VIC, SA, TAS, ACT, NT 403/000; NZTA Incapsula; NSW cambiato il 1/2/2026, WA il 31/10/2026; DiscoverCars ~20 $, cookie 365 giorni) | **PASSA sotto l'asticella** (voto 7; 300-5.500 €/anno a 18 mesi, centrale 1.200; 22-35 ore) come parte del blocco "Before you drive" di Before You Fly insieme a patente all'estero (28/10) e pedaggi (29/10) | ricerca-zona-canada-australia-2026-10-30 |
| Snowbird canadesi: giorni fuori provincia e negli USA | RISERVA (6): the-northern-office.pages.dev già per provincia; TuGo solo per residenti canadesi; Red Helm 3 $ | ricerca-zona-canada-australia-2026-10-30 |
| Piani elettrici australiani per codice postale (API CDR dell'AER: 84 venditori, 200 senza chiave) | NO come sito (5): billhero.com.au per codice postale, whysolar per venditore; fonte da ricordare | ricerca-zona-canada-australia-2026-10-30 |
| Affitti per sobborgo (AU), affitti per città (CA), tassa sulla casa per città (ON), stamp duty, NAPLAN, attese chirurgiche, medico di famiglia, SkillSelect, estrazioni PNP, tempi IRCC, LMIA/AEWV, rego, multe, assicurazione auto per CAP, tasse comunali NZ, parchi | NO o riserve deboli (3-5) | ricerca-zona-canada-australia-2026-10-30 |
```

---

## 6. Metodo e limiti

- **Autocomplete:** circa 70 interrogazioni con `client=firefox`, gl=ca/au/nz, hl=en (30/10/2026).
- **Google:** 12 ricerche. Lo strumento di ricerca usa la versione USA: per le query australiane e canadesi l'ordine può essere diverso da quello locale.
- **Fonti:** circa 45 curl dal server, con l'esito HTTP scritto accanto a ogni fonte.
- **Non verificato:**
  - la licenza dell'API CDR;
  - l'elenco WA in vigore dal 31/10 nell'HTML (preso da Google);
  - le cifre per contatto di Kanetix (da un elenco di terzi) e di RATESDOTCA (non pubbliche);
  - l'accettazione di un iscritto italiano nei programmi canadesi.
- I valori AdSense per Canada e Australia sono assunzioni, non misure.

## 7. Link principali
- Ontario: https://www.ontario.ca/page/exchange-out-province-drivers-licence ; https://www.ontario.ca/page/drive-ontario-visitors
- Alberta: https://www.alberta.ca/exchange-non-alberta-licences ; https://www.transportation.alberta.ca/content/docType45/Production/ReciprocalLicensing.pdf
- BC: https://www.icbc.com/driver-licensing/moving-bc
- Nova Scotia: https://novascotia.ca/exchange-your-out-of-province-drivers-licence/
- NSW: https://www.nsw.gov.au/driving-boating-and-transport/driver-and-rider-licences/visiting-or-moving-to-nsw/moving-your-overseas-licence/knowledge-and-driving-test-exemptions
- Queensland: https://www.qld.gov.au/transport/licensing/driver-licensing/overseas/transfer/exempt-countries
- WA: https://www.transport.wa.gov.au/licensing/drivers-licence/visit-move-wa/moving-from-overseas/transfer-recognised-jurisdiction
- DiscoverCars: https://www.discovercars.com/affiliate
- CDR energia: https://api.cdr.gov.au/cdr-register/v1/energy/data-holders/brands/summary ; https://cdr.energymadeeasy.gov.au/agl/cds-au/v1/energy/plans ; https://www.aer.gov.au/energy-product-reference-data
- Concorrenti visti: https://billhero.com.au/electricity/lota-4179 ; https://www.whysolar.com.au/feed-in-tariffs/nsw ; https://catax-tools.pages.dev/property-tax-toronto/ ; https://the-northern-office.pages.dev/provincial-health-coverage-residency/on/ ; https://calendar-uk.co.uk/frequently-asked-questions/can-i-drive-in-canada-with-indian-license ; https://tyremap.com/as-tourist/driving-in-canada-as-india-tourist/ ; https://welcomeaide.com/hi/blog/driver-license-conversion-ontario-2026 ; https://drivingintheworld.pages.dev/destinations/canada/
- Programmi: https://insurancenewsnet.com/oarticle/tugo-launches-revenue-generating-affiliate-program-for-unlicensed-individuals-and-organizations ; https://redhelm.ca/?p=5075 ; https://www.affpaying.com/kanetixca
