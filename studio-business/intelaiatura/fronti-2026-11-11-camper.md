# Fronte: "posso noleggiare o guidare un camper con la mia patente?" (11/11/2026, notte)

**Domanda del giro.** La pista lasciata dal giro della sera: CamperDays paga circa 105 € a prenotazione; esiste una domanda di chi NOLEGGIA, per patente e per Paese di destinazione, con un dato ufficiale leggibile e senza un concorrente che risponda già bene?

**Risposta breve: no, non come sito nuovo. Una sezione piccola di Before You Fly (voto 5,5) e due riserve. Nessuna idea a 7.**
Tre fatti lo decidono:
1. **La risposta a chi noleggia è quasi sempre "sì, basta la patente dell'auto"**, e la danno già i noleggiatori (che sono anche i pagatori) nelle loro pagine di domande. Una risposta uguale per tutti non regge un sito.
2. **La griglia patente × Paese non è cercata.** Autocomplete: "motorhome hire usa uk licence" 0, "can i drive an rv in america with a uk licence" 0, "campervan hire new zealand licence" 0, "wohnmobil mieten internationaler führerschein" 0, "noleggio camper usa patente" 0. Si cerca solo il Paese di destinazione ("what licence do i need to drive a motorhome in" 10) e l'età ("campervan hire under 25" 8).
3. **Il pagatore alto (CamperDays, 88-105 € a prenotazione) esiste solo in tedesco, olandese e francese.** In inglese si scende a circa 35 € (Motorhome Republic, RVshare).

Metodo: tutto letto l'11/11/2026 con curl dal server; "ricerca web" = usata solo per trovare gli indirizzi dei concorrenti, poi le pagine sono state lette. Cambio 1 £ = 1,15 €, 1 $ = 0,92 €, 1 NZD = 0,53 €. Parole cercate prima in `ESPLORATE.md`: camper, motorhome, wohnmobil, campervan, patente b, 4250, 2025/2205, IDP, driving abroad. Già esplorati e non ripetuti: camper oltre 3,5 t (pedaggi, limiti: NO l'11/11 sera), lunghezza camper nei campeggi USA, freedom camping NZ, "Driving abroad" (già online in Before You Fly: 113 pagine Paese × patente con DiscoverCars).

## 0. La domanda (autocomplete Google, numero di suggerimenti)

| Ricerca | Paese | N. | Che cosa dice |
|---|---|---|---|
| can i drive a motorhome on a car licence | UK, AU | 10 | varianti "uk", "7.5 tonne", "vw campervan": patente DI CASA, non destinazione |
| what size motorhome can i drive on a car licence | UK, AU | 6 | con "uk", "nz", "in australia" |
| c1 licence motorhome | UK | 10 | "cost", "how to get": proprietari, non noleggio |
| motorhome licence over 70 | UK | 6 | rinnovo a 70 anni: proprietari |
| **what licence do i need to drive a motorhome in** | CA, AU, NZ | **10** | **usa, nz, australia, canada, south africa, ireland**, ontario |
| do you need a special license to drive a motorhome in | US | 10 | canada, australia, ontario, california, texas, uk, florida, bc |
| do you need a special license / a cdl to drive an rv in | US | 10 + 10 | solo Stati USA (California, Texas, Florida, PA, Ohio, NY…): proprietari di camper grandi |
| **campervan hire under 25 / under 21** | UK | **8 / 7** | "uk", "scotland", "australia", "nz" |
| campervan hire age · campervan rental age | UK, AU · US | 8 · 10 | "age limit", "age 21", "new zealand age limit" |
| can you rent an rv under 25 · rv rental under 21 | US | 5 · 5 | "at 21", "at 18" |
| wohnmobil mieten führerschein | DE | 10 | b, c, c1, **kanada, usa**, "welcher", "pkw" |
| wohnmobil usa führerschein | DE | 6 | "mit deutschem führerschein", "klasse b" |
| camper huren rijbewijs · camper huren leeftijd | NL | 10 · 6 | "amerika"; età con **australie, canada, amerika** |
| louer camping car permis | FR | 10 | b, c, c1, "jeune permis" |
| camper patente b · noleggio camper patente | IT | 10 · 8 | "usati", "prezzo", "milano", "roma": acquisto e noleggio locale |
| **führerschein b 4 25 t · permis b 4250 kg · rijbewijs b 4250 kg** | DE · FR · NL | **10 · 10 · 10** | "ab wann", "2026", "belgië", "europa wanneer": la regola nuova dell'UE |
| A zero | | 0 | "motorhome hire usa uk licence", "can i drive an rv in america with a uk licence", "campervan hire new zealand licence" (UK e AU), "motorhome hire europe australian licence", "can i rent an rv with a foreign license", "campervan rental europe license", "wohnmobil mieten internationaler führerschein", "camper mieten neuseeland führerschein", "noleggio camper usa patente", "4.25 tonne licence" (UK), "can i drive a motorhome in europe on a uk licence" |

Lettura: tre domande vere e separate. (a) **Chi noleggia all'estero** chiede "che patente serve per il camper in [Paese]" e "che età serve": inglese (soprattutto da Canada, Australia, Nuova Zelanda), tedesco, olandese. (b) **Chi possiede o compra** chiede il peso (3,5 t, C1, 70 anni, Stato USA): non noleggia, CamperDays non c'entra. (c) **La regola UE nuova dei 4.250 kg**: fortissima in tedesco, francese, olandese; pubblico di proprietari.

## 1. Il dato ufficiale (prova "leggibile")

| Fonte | Esito | Che cosa contiene |
|---|---|---|
| GOV.UK `api/content/driving-motorhome` | 200 | "To drive a motorhome with a MAM of between 3.5 and 7.5 tonnes, you need a category C1 licence… over 7.5 tonnes, a category C licence" |
| GOV.UK `api/content/driving-licence-categories` (agg. 18/12/2024) | 200 | patente B prima del 1/1/1997: complesso fino a 8.250 kg; dopo: 3.500 kg |
| GOV.UK `api/content/old-driving-licence-categories` (agg. 15/1/2025) | 200 | tabelle vecchie/nuove categorie |
| GOV.UK, regola dei 4.250 kg per veicoli a zero emissioni | **non trovata** | la ricerca dell'API non la restituisce; indirizzo da trovare prima di citarla |
| EUR-Lex, direttiva (UE) 2025/2205 (GU 5/11/2025), HTML | 200, 43.000 parole | art. 6: con la B "a motor caravan with a maximum authorised mass exceeding 3 500 kg but not exceeding 4 250 kg" dopo corso o esame; art. 29: misure nazionali entro il **26/11/2028, applicate dal 26/11/2029**; solo l'equivalenza per i veicoli a carburante alternativo (art. 9.2 j, k) dal **26/11/2027**, e "Motor caravans shall not be covered by the equivalence" |
| EUR-Lex, pagina delle misure nazionali di recepimento (NIM) della 2025/2205 | 200 | elenco per Stato (oggi quasi vuoto: il termine è nel 2028) |
| Belgio, SPF Mobilité (pagina "nouvelle réglementation en perspective") | 200 | B da 2 anni valida fino a 4.250 kg per i veicoli a propulsione alternativa; "les camping-cars ne sont pas concernés" |
| Germania, FeV § 6 (gesetze-im-internet.de) | 200 | classi di patente |
| Francia, service-public.gouv.fr F2827 | 200 | categorie di patente |
| Texas DPS, classi di patente | 200 | classi A/B/C per peso (26.000 libbre) |
| usa.gov "non-citizen driving" | 200 | rimanda a ogni Stato |
| NZTA (Nuova Zelanda) | 200 ma 212 byte | pagina anti-robot, come già visto il 30/10: non letta |
| California DMV (manuale camper) | 404 | indirizzo cambiato, non cercato oltre |
| In casa: `beforeyoufly/dati/patenti.json` | — | permesso internazionale per 3 patenti × tutti i Paesi (GOV.UK, travel.gc.ca, Smartraveller): **0 volte "motorhome", "campervan", "3,500"** |

**Il buco del dato.** Le fonti ufficiali dicono (1) che cosa copre la patente a casa propria e (2) se serve il permesso internazionale. **Nessuna fonte ufficiale letta dice se una patente B straniera copre un camper oltre 3,5 t nel Paese di destinazione** (il caso tipico: camper americano a noleggio da 5-6,5 t). Lo dicono solo i noleggiatori, per la loro flotta. Quindi la prova "dato ufficiale" regge per il permesso e per la regola di casa, non per la domanda più interessante. L'età minima sta solo nelle condizioni dei noleggiatori (fonte primaria, non ufficiale).

## 2. I pagatori letti

| Pagatore | Rete | Cifra letta | A prenotazione | Possiamo entrare? |
|---|---|---|---|---|
| **CamperDays DE** | Awin 52889 | "3% Provision pro Buchung (ø 105 EUR)", "6 Euro Provision pro Lead", cookie 30 giorni; la stessa pagina dice "Buchungsanfragen werden nicht vergütet" | 105 € | Sì (siamo su Awin), ma serve un sito in tedesco |
| **CamperDays NL** | Awin 52891 | 3 %, "Ø 105 Euro" in un punto e "durchschnittlichen Provision von 88 Euro" in un altro; 8 € a richiesta qualificata; cookie 30 giorni | 88-105 € | Sì, ma serve l'olandese |
| **CamperDays FR** (nuovo, trovato oggi) | Awin 52893 | "3 % de commission par vente (Ø 88 euros)", 6-8 € a richiesta | 88 € | Sì, ma serve il francese |
| CamperDays UK / inglese | — | **nessun profilo trovato** (provati gli ID vicini 52887-52894: solo DE, NL, FR) | — | No |
| Motorhome Republic (Webjet NZ) | diretto ("Get in touch") | "Earn up to 8% revenue", "Average booking value in 2022 was over NZD $800"; nella stessa pagina i marchi venduti: Cruise America, Indie Campers, McRent, Roadsurfer | ~35 € (8 % di 800 NZD) | Da chiedere: non c'è modulo aperto |
| RVshare (USA, fra privati) | proprio / rete | "Earn 4% commission of the total booking value", "$900 average booking value", pagato dopo il check-in | ~33 € | Sì, ma pubblico americano che noleggia in casa |
| Cruise America | Impact | "Earn meaningful commission": **cifra non scritta** | ? | Impact: non ci siamo |
| roadsurfer DE/AT | Awin 76432 | cookie 30 giorni, **commissione non scritta** | ? | Sì, in tedesco |
| Indie Campers, McRent, Yescapa, Escape, Travellers Autobarn, Jucy | — | pagine "affiliate" 404 agli indirizzi provati | — | non letti |
| Outdoorsy, Goboony | — | 403 | — | non letti, non insistito |

**EPC, tasso di conversione, tasso di approvazione: non sono nelle pagine pubbliche di Awin** (si vedono solo dopo l'accesso). Chi ha l'accesso Awin può leggerli in due minuti nei profili 52889, 52891, 52893, 76432: è il numero che manca alle stime qui sotto.

## 3. I concorrenti letti (obbligo del 10/11)

Cinque esempi concreti, pagine lette con curl.

| Esempio | Concorrente 1 | Concorrente 2 | Concorrente 3 | Che cosa manca |
|---|---|---|---|---|
| **1. Patente UK, camper a noleggio negli USA** | Cruise America, pagina dedicata (750 parole): "a standard UK (category B) license is absolutely sufficient"; permesso internazionale "if your license is not in English… you'll need IDP 1949" | roadsurfer (1.160 parole): niente permesso per patenti UE/EFTA/UK; "EU/EFTA/UK category B/3 licenses… also cover campers over 3.5 tons in North America"; età 21 e patente da 1 anno | Escape Campervans: "some states in the USA require an international driver's license"; Motorhome Republic: "We recommend you carry an International Driver's Licence" | **Quattro risposte diverse sul permesso**, nessuna con una fonte ufficiale; nessuno dice da quale legge viene "la B copre oltre 3,5 t". Ma la risposta pratica ("sì") c'è già, scritta da chi consegna le chiavi |
| **2. Patente tedesca, camper negli USA / in Canada** | promobil (1.880 parole): "Für die meisten Wohnmobile… reicht der deutsche B-Führerschein", età "21 oder 25" | roadsurfer.de: B o classe 3; eccezione scritta per Québec, Labrador, Terranova (classe 5 fino a 4.500 kg) | ricerca web: canusa, ADAC, bussgeldkatalog, Indie Campers DE | Poco: la risposta c'è, con il dettaglio del Québec. Manca solo la fonte ufficiale |
| **3. Età minima per noleggiare (sotto i 21 / 25), per Paese e compagnia** | NZ Pocket Guide (6.800 parole, solo Nuova Zelanda; rimanda a DiscoverCars) | DriveNow Australia: tabella "Supplier Age Comparison" (ricerca web, non letta con curl) | roadsurfer e Indie Campers: età per area (Europa 18, UK/USA/Canada/Australia 21) | **Per USA, Canada ed Europa non c'è una tabella per compagnia**: è il vuoto più chiaro del giro. Ma il dato sono le condizioni dei noleggiatori (lette oggi: roadsurfer 200, Escape 200 "21, under 25 $10/day", Travellers Autobarn 200; Cruise America, Jucy, Britz, Apollo, Indie 404 agli indirizzi provati) |
| **4. "Do you need a special license to drive an RV in Texas"** | Escapees: guida Stato per Stato (2.600 parole, 17 Stati con regole speciali, link al DMV di ognuno) | Winnebago: regola generale delle 26.000 libbre | ricerca web: Outdoorsy (403), Campanda, godownsize, changingears, thervgeeks, everquote | **Niente**: già fatto Stato per Stato; e il pubblico possiede camper grandi, non noleggia |
| **5. Patente B fino a 4.250 kg per i camper: da quando, in quale Paese** | camping-car.com: "quatre ans pour transposer… 2029" | OpenVan.camp (sito di notizie per camperisti in 7 lingue, con sezione "RV Laws & Rules"): "by November 2028… not before 2029, contradicting a report that mentioned November 2027" | Touring.be: spiega solo il codice 96 per i rimorchi; SPF Mobilité: "les camping-cars ne sont pas concernés" (parla dell'altra regola); ADAC: "zukünftig… bis zu 4,25 t", senza data nella pagina letta | **Date in contrasto (2027, 2028, 2029) e due regole confuse fra loro** (carburanti alternativi dal 26/11/2027, camper dal 26/11/2029). Nessuno ha una pagina "Paese per Paese: a che punto è". Ma è una notizia: quando un Paese decide, ADAC, ANWB, NKC e i giornali lo scrivono lo stesso giorno |

Non lette (404/504 agli indirizzi provati, non insistito): le guide alla patente dei due club britannici e di Practical Motorhome. Per la domanda britannica "can i drive a motorhome on a car licence" il vuoto quindi **non è dimostrato** (voto massimo 5) e GOV.UK risponde in tre frasi.

## 4. Classifica

| # | Idea | Voto | Prudente / centrale / ottimista €/anno a 18 mesi | Dove |
|---|---|---|---|---|
| 1 | Noleggio camper all'estero: patente, permesso internazionale ed età minima per Paese di destinazione | **5,5** | 20 / 300 / 2.800 | **sezione di Before You Fly** (inglese, poi /it/), coda bassa |
| 2 | Patente B fino a 4.250 kg per i camper: da quando, Paese per Paese (direttiva 2025/2205) | **5** | 30 / 200 / 2.200 | riserva con data: si riapre al primo recepimento nazionale |
| 3 | La stessa idea 1 in tedesco e olandese per CamperDays | **4,5** | 25 / 460 / 6.200 | NO adesso (nessun sito nostro in tedesco; vuoto non dimostrato) |
| — | Patente speciale per camper negli Stati USA | 3,5 | 20 / 150 / 1.200 | NO |
| — | "Can I drive a motorhome on a car licence" (UK: C1, 1997, 70 anni) | 4 | 20 / 150 / 1.500 | NO (solo una pagina dentro l'idea 1, se si fa) |

Nessuna passa l'asticella (voto ≥ 7 e ≥ 5.000 € centrali). Nessuna ha un ottimista ≥ 10.000 €.

## 5. Idea 1: sezione "Campervan hire abroad" in Before You Fly (voto 5,5)

**Che cos'è.** 12-15 pagine per Paese di destinazione (USA, Canada, Australia, Nuova Zelanda, Sudafrica, Irlanda, Regno Unito, Islanda, più 4-6 Paesi europei), ognuna con: (1) serve il permesso internazionale, per patente UK, canadese, australiana (dato già in casa, 113 pagine "Driving abroad"); (2) peso che copre la patente di casa (GOV.UK, direttiva UE) e la frase onesta "la legge del Paese di destinazione non è stata letta: vale ciò che scrive il noleggiatore"; (3) tabella dell'età minima e del supplemento giovani per compagnia, con la frase esatta delle condizioni e la data di lettura. Una pagina indice "what licence do I need to hire a campervan in…".

**Formula.** visite/anno × clic sul noleggio × prenotazioni per clic × 35 € + visite × 8 € ogni 1.000 (AdSense).
- Prudente: 150 visite/mese → 1.800 × 4 % × 0,5 % × 35 € = 13 € + 14 € = **circa 20 €**.
- Centrale: 600 visite/mese → 7.200 × 6 % × 1,5 % × 35 € = 227 € + 58 € = **circa 300 €**.
- Ottimista: 2.500 visite/mese → 30.000 × 8 % × 3 % × 35 € = 2.520 € + 240 € = **circa 2.800 €**.
Assunzioni: pagatore da 35 € (Motorhome Republic o RVshare), cookie 30 giorni su un acquisto da 800-3.000 € che si decide in settimane (per questo la conversione è bassa). **Ore:** 14-20 degli agenti, 15 minuti di Massimiliano (richiesta a Motorhome Republic). Rapporto centrale: circa 17 €/anno per ora.

**Le 4 prove.**
1. Domanda: **sì, media.** "what licence do i need to drive a motorhome in" 10 (6 Paesi), "campervan hire under 25" 8, "under 21" 7, "campervan rental age" 10. Ma le coppie patente × Paese sono a 0.
2. Dato ufficiale leggibile: **a metà.** Permesso e peso a casa sì (GOV.UK 200, già in casa); peso nel Paese di destinazione no; età solo dalle condizioni dei noleggiatori (3 lette su 8 provate).
3. Pagatore attivo a cui possiamo iscriverci: **debole in inglese.** Motorhome Republic va chiesto per email dal modulo del sito (non è cold email: è la loro pagina per i partner), RVshare serve solo agli americani, CamperDays non ha un programma inglese. DiscoverCars resta come ripiego (auto, non camper).
4. Nessuno fa già meglio: **vuoto parziale.** Dimostrato per l'età per compagnia in USA, Canada ed Europa e per le risposte in contrasto sul permesso; non dimostrato per la patente (i noleggiatori rispondono "sì" e sono in prima pagina).

**Perché non un sito nuovo.** La risposta è corta, il pagatore inglese è da 35 €, la stima centrale è 300 €. In Before You Fly costa poco perché metà del dato c'è già e le pagine "Driving abroad" portano i collegamenti interni.

**Rischi.** Le condizioni dei noleggiatori cambiano senza data (serve rilettura mensile); regola del 7/11 "niente più viaggi" (è un'aggiunta a una sezione che esiste, non un fronte nuovo); se Motorhome Republic non risponde resta solo AdSense (centrale circa 60 €).

## 6. Idea 2: patente B fino a 4.250 kg per i camper, Paese per Paese (voto 5, riserva con data)

**Fonte esterna.** Direttiva (UE) 2025/2205, GU del 5/11/2025: regola nuova con data. **Domanda:** "führerschein b 4 25 t" 10 (con "ab wann"), "permis b 4250 kg" 10 (con "2026", "belgique", "france"), "rijbewijs b 4250 kg" 10 (con "belgië", "europa wanneer"), "b96 wohnmobil" 9; Italia 2, Spagna 2, Polonia 0, Regno Unito 0.
**Dato:** testo ufficiale 200 con le due date (26/11/2027 per i veicoli a carburante alternativo, camper esclusi; 26/11/2028 adozione e **26/11/2029 applicazione** per i camper); pagina NIM di EUR-Lex 200 con le misure di ogni Stato appena vengono comunicate.
**Vuoto:** dimostrato sulle date (tre concorrenti, tre anni diversi; la pagina belga ufficiale parla dell'altra regola), ma è una notizia che i grandi (ADAC, ANWB, NKC, camping-car.com) copriranno a ogni passo.
**Pagatore:** solo AdSense; chi cerca possiede o compra un camper, non noleggia; le scuole guida per il corso non hanno affiliazione. **Prova 3 non superata.**
**Formula.** visite × 6-8 € ogni 1.000 + poche prenotazioni CamperDays (88-105 €). Prudente 400 visite/mese → 30 €; centrale 1.500/mese → 18.000 × 6 € = 108 € + 1 prenotazione = circa 200 €; ottimista 15.000/mese → 180.000 × 8 € = 1.440 € + 8 prenotazioni = circa 2.200 €. **Ore:** 20-28, in tre lingue che non abbiamo.
**Quando si riapre:** al primo Stato che pubblica la sua misura sulla pagina NIM (atteso 2027-2028). Il picco di ricerche sarà nel 2028-2029, oltre i 18 mesi della stima.

## 7. Idea 3: la sezione in tedesco e olandese per CamperDays (voto 4,5, NO adesso)

È l'unica con il pagatore da 88-105 €. **Formula:** centrale 400 visite/mese → 4.800 × 6 % × 1,5 % × 100 € = 430 € + 30 € AdSense = circa 460 €; prudente 100/mese → 25 €; ottimista 2.500/mese → 30.000 × 8 % × 2,5 % × 100 € = 6.000 € + 240 € = circa 6.200 €. Cade su due prove: **vuoto non dimostrato** (roadsurfer.de e promobil rispondono già, con il dettaglio del Québec; CamperDays stesso ha le condizioni di ogni offerta) e **nessun sito nostro in tedesco o olandese** su cui appoggiarla (un dominio nuovo parte da zero contro promobil, ADAC, ANWB). Si riapre solo se nasce un sito tedesco della rete (per esempio quello delle patenti nautiche in Croazia, in coda dal giro della sera: stesso pubblico di chi noleggia in vacanza, stessa rete Awin).

## 8. Che cosa fare

1. **Niente sito nuovo sul camper.** Il fronte camper è chiuso per i siti nuovi: due giri (sera e notte dell'11/11), nessun voto sopra 5,5.
2. Idea 1 in **coda bassa** di Before You Fly, dopo le sezioni già decise; prima di costruirla, una sola verifica: chi ha l'accesso Awin legge EPC e conversione di CamperDays e roadsurfer, e si chiede a Motorhome Republic la percentuale reale.
3. Idea 2: controllo della pagina NIM di EUR-Lex una volta al mese nella routine (un curl); si riapre al primo recepimento.
4. Fatto utile per altri giri: **CamperDays ha anche il programma francese (Awin 52893, 88 € medi)**; i tre programmi pagano anche 6-8 € per ogni richiesta di prenotazione qualificata.
