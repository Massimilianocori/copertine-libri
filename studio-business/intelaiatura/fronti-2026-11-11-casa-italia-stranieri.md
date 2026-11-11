# Fronte nuovo: stranieri che comprano (o hanno già) casa in Italia — 11/11/2026

Ricerca fatta dal nostro server con curl l'11/11/2026. Ogni cifra ha accanto come è stata letta.
Fonti esterne da cui nasce il fronte: autocomplete Google (US, GB, DE, NL, FR), file ufficiali del Dipartimento delle Finanze
(prospetti IMU 2026), pagine dei concorrenti lette una per una, pagine dei programmi di affiliazione.

**Verdetto in una riga: nessuna idea passa l'asticella dei siti nuovi (voto ≥ 7 e ≥ 5.000 €/anno centrali).**
La migliore è una sezione dentro Visa Income (case a 1 euro verificate comune per comune), voto 6, circa 900 €/anno centrali,
8.600 ottimisti. Le tre idee insieme: circa 200 / 1.750 / 13.600 €/anno a 18 mesi. Il pagatore grosso che il compito
ipotizzava (cambio valuta a 100 £ e più per cliente) **non ha una cifra leggibile**: resta non provato.

---

## 1. Domanda (autocomplete, numero di suggerimenti su 10)

| Ricerca | Paese | N. | Cosa dice |
|---|---|---|---|
| buying a house in italy | US / GB | 10 / 10 | "as an american", "as a foreigner", "as a us citizen", "as an australian", "from uk", "for 1 euro" |
| buying property in italy as | US | 10 | american, foreigner, us citizen, dual citizen, australian, canadian, uk citizen, british, eu citizen |
| can americans buy property in italy | US | 10 | anche "can australians / canadians buy property in italy" |
| 1 euro houses italy | US / GB | 10 / 10 | "for sale", "2026", "map", "sicily", "listings", "tuscany", "reddit" |
| 1 euro houses italy 2026 | US | 4 | "are there still 1 euro houses in italy", "list of 1 euro houses in italy" |
| 1 euro houses mussomeli / sambuca | US | 8 / 9 | domanda anche per singolo paese |
| 1 euro haus italien | DE | 10 | "angebote 2026", "liste", "karte", "am meer", "sardinien", "apulien", "toskana 2026" |
| 1 euro huis italië | NL | 9 | "2026", "kopen", "toscane", "noord italie" |
| cost of buying property in italy | US | 10 | "hidden costs", "cost of owning a house in italy" |
| italian property tax | GB | 10 | "for foreigners", "calculator", "imu", "annual", "per year" |
| imu italy | GB | 10 | "calculator", "tax rate", "payment", "2026", "calculator online" |
| how to pay imu | US | 10 (3 pertinenti) | "how to pay imu in italy", "how to pay imu from abroad", "online" |
| imu italien | DE | 10 | "berechnen", "ausländer", "rentner", "zweitwohnsitz", "online bezahlen", "verjährung", "2026" |
| grundsteuer italien | DE | 10 | "rechner", "berechnen", "bezahlen", "ferienhaus", "ausländer", "zweitwohnsitz" |
| imu italië | NL | 5 | "berekenen", "betalen in italië", "2026" |
| italy property auctions | US / GB | 7 / 7 | "italy house auctions", "italian government property auction" |
| buying a house at auction in italy | US | 5 | |
| italian mortgage for non residents | US | 5 | |
| property prices in lucca / puglia; house prices in abruzzo | US | 10 / 10 / 10 | per metà sono "property for sale" |
| cheapest places to buy property in italy | US | 10 | |
| 7 tax towns italy | US | 10 | già coperta dalla pagina "Italy 7% flat tax" di Visa Income |

**Domanda assente (0 suggerimenti):** "imu second home", "imu italy non resident", "italy property purchase tax calculator",
"italy buying costs calculator", "reciprocity italy property", "price per square meter italy" (3), "italian property auction
for foreigners", "currency transfer italy property". Quindi: le pagine "IMU per comune" e "prezzo al m² per comune" in inglese
**non hanno una domanda scritta così**; la domanda è sulle parole grandi e sui paesi delle case a 1 euro.

Composizione dei risultati: **non leggibile** (Google, DuckDuckGo, Brave, Mojeek chiusi dal server; Bing ha risposto in modo
utile a una sola ricerca su 14). L'unica letta, "can a us citizen buy property in italy": taxesforexpats, itamcap, Wise,
visaverge, ttandpartners (2 volte), livingitalyrealestate, Expatica, lovetovisititaly, movingto. Dieci guide, tutte del 2026.

---

## 2. Dati ufficiali: cosa si legge e cosa no

| Fonte | Esito | Nota |
|---|---|---|
| **Prospetti delle aliquote IMU 2026, comune per comune** (Dipartimento Finanze, `www1.finanze.gov.it/.../nuova_imu/dati/download.htm?anno=2026`) | **200, ottimo** | uno zip per regione (Molise 2,1 MB, Toscana 6 MB, Puglia 8 MB, Veneto 12 MB, Lombardia 29 MB, aggiornati fra il 29/10 e il 10/11/2026). Dentro un PDF per comune, generato dal portale, sempre uguale: comune, numero e data della delibera, aliquota "Altri fabbricati" (le seconde case), esenzioni. Molise: 119 prospetti su 136 comuni; **40 su 40 letti in automatico** con `pdftotext` (14 a 1,06 %, 10 a 0,86 %, 6 a 0,96 %, 6 a 1,01 %…). Il nome del file contiene il codice catastale del comune. Sicilia solo 3,4 MB: al Sud mancano molti comuni (per loro vale l'aliquota di base) |
| Valori OMI per zona (Agenzia delle Entrate, CC BY 4.0) | **già nostro** | `aste/dati/omi.json`, semestre 2026/1, stessa raccolta di Aste in Chiaro |
| Aste giudiziarie (Portale delle Vendite Pubbliche) | **già nostro** | `aste/dati/lotti.json`, aggiornato ogni sera |
| Imposta di registro, ipotecaria, catastale, IVA (prima casa / altra casa) | leggibile | regole di legge uguali per tutti; servono 2-3 fonti dell'Agenzia delle Entrate |
| **Condizione di reciprocità, Paese per Paese** (Ministero degli Esteri) | **NON leggibile** | `esteri.it` risponde con il captcha del filtro anti-robot. Non aggirato. Si può solo linkare |
| **Case a 1 euro** | **nessun elenco nazionale ufficiale** | l'elenco che tutti usano è di un sito privato (casea1euro.it). I siti dei comuni rispondono (10 su 10 con 200: Sambuca, Troina, Ollolai, Penne, Zungoli, Taranto, Mussomeli, Pratola Peligna, Grotte, Cinquefrondi), ma solo 4 su 10 nominano l'iniziativa in prima pagina e ogni sito è fatto a modo suo: è un controllo comune per comune, non uno scarico |
| Tariffe dei notai | nessuna tabella ufficiale in vigore | le tariffe sono libere dal 2012: si può dare solo un intervallo |

Limite da scrivere in pagina: l'IMU si calcola sulla **rendita catastale**, che è dell'immobile e non sta nei dati OMI. Quindi
"IMU all'anno per comune" si può dare solo come esempio (rendita scelta dall'utente), mai come cifra del comune.

---

## 3. Concorrenti letti (obbligo del 10/11): cosa hanno e cosa manca

| Esempio concreto | Chi è stato letto | Cosa hanno | Cosa manca |
|---|---|---|---|
| **1. "1 euro houses italy 2026 list"** | 1eurohouses.com / casea1euro.it (200), Idealista EN "Map of €1 houses in Italy 2026" del 23/1/2026 (200), Idealista DE (articoli di giugno 2026) | 109 pagine-paese; vende un e-book a 16,90-27,90 €; Idealista fa la mappa "secondo il sito ufficiale 1 Euro House", che ufficiale non è | **Nessuno dice se il bando è aperto oggi.** La pagina di Grotte (AG) è stata modificata l'ultima volta il 10/8/2021, parla della delibera di settembre 2020 e riporta la PEC di un comune della provincia di Foggia. Idealista scrive solo "schemes come and go". Nessuno mette accanto il prezzo vero di una casa normale lì (OMI) né le aste nello stesso comune |
| **2. "1 euro houses mussomeli / sambuca"** | siti dei due comuni (200), 1eurohouses | Mussomeli rimanda dal sito del comune a un sito di agenzia; Sambuca non ne parla in prima pagina | data dell'ultimo avviso, cauzione, termine dei lavori con il link all'atto |
| **3. "imu italy calculator" / "imu italien berechnen"** | movingto.com (guida 2026), Expatica (18/12/2025), Wise US, Idealista DE "Was Deutsche wissen müssen" (14/5/2026), Magic Towns (EN e DE), amministrazionicomunali.it | movingto dà la formula giusta (rendita × 1,05 × 160 × aliquota; 0,86 % di base, fino a 1,06 %); Idealista DE nomina l'IMU in una riga; amministrazionicomunali.it ha il calcolatore completo con le aliquote di ogni comune, **solo in italiano** | **l'aliquota 2026 del singolo comune in inglese o tedesco, con il numero della delibera**; come pagare dall'estero; la riduzione per i pensionati esteri. **Riserva:** non ho potuto leggere i risultati di Google, quindi non so se esiste già un calcolatore in tedesco o in inglese |
| **4. "property prices in lucca italy" / prezzo al m² di un comune piccolo** | Magic Towns (pagina di Bagni di Lucca, EN e DE), mercato-immobiliare.info, Numbeo; Idealista e Immobiliare.it **403** | Magic Towns: 7.896 comuni in 5 lingue (31.986 URL), ma i prezzi per zona sono **solo per gli abbonati** (149 €/anno o 13 €/mese); mercato-immobiliare.info dà i valori OMI per zona gratis, in italiano (Bagni di Lucca 580-1.155 €/m²) | una pagina gratuita in inglese con i valori OMI. **Ma** Idealista ha i rapporti prezzi per comune in inglese (`/en/press-room/property-price-reports/`, non leggibile da noi): qui il vuoto **non è dimostrato** |
| **5. "can a us citizen buy property in italy" / costi totali** | Wise US (3.425 parole), movingto (4.336 parole, 2026), Expatica (2.397 parole), Gate-away (pagina "purchase process", solo JavaScript), italianhousesforsale, Magic Towns "Ultimate Property Guide" (24 capitoli, 5 gratis) | reciprocità, codice fiscale, 2 %-9 %, IVA, notaio, IMU: c'è tutto, aggiornato al 2026 (movingto spiega anche il minimo di 1.000 € e i 18 mesi per la residenza) | un calcolatore vero (nessuno dei letti ce l'ha) e le aste. Non basta: dieci guide del 2026 in prima pagina |

**Lezione:** Magic Towns è il concorrente da tenere d'occhio. Ha già tutte le pagine-comune in inglese, tedesco, francese,
danese e italiano, la guida all'acquisto, un "Property Evaluator" e le pagine dei comuni del 7 %. Un sito nostro "un comune,
una pagina" arriverebbe secondo. Lo spazio che lascia è ciò che tiene a pagamento (i prezzi) e ciò che non ha (aliquota IMU,
stato dei bandi a 1 euro, aste).

---

## 4. Chi paga (cifre lette sulle pagine)

| Pagatore | Cifra | Letta? |
|---|---|---|
| **AnchorLess** (codice fiscale per stranieri) | servizio "Codice Fiscale" a **149 €** (listino 199 €); affiliazione **"from 10 % of every sale, up to 20 %"** → **14,90 €** a vendita | sì, 11/11/2026, `anchorless.io/italy` e `/affiliate`. Iscrizione nostra ancora in attesa |
| **Wise** | 10 £ a cliente nuovo (≈ 11,5 €) | letta il 17/10/2026 (riga di ESPLORATE); oggi la pagina del programma non mostra cifre. Wise spinge proprio chi compra casa: nella sua guida c'è una promozione sul "first large transfer" sopra 70.000 $ |
| Currencies Direct, TorFX, Lumon | — | **403** (filtro anti-robot). Non letti, non aggirati |
| Moneycorp, Xe, OFX, Key Currency, Smart Currency, Clear Currency | — | pagina vuota, 404 o 500: **nessuna cifra** |
| Translayte | 10 % | già nota |
| Idealista, Immobiliare.it, Gate-away | — | nessun programma di affiliazione trovato; Gate-away vende spazi alle agenzie |
| Mediatori di mutui per non residenti, geometri, avvocati | — | nessun programma leggibile: servirebbe un accordo scritto, cioè rincorsa di clienti (regola 3) |
| AdSense | stima 4-6 € per 1.000 visite | nostra stima, non letta |

**Il "100 £ e più a cliente" dei cambiavalute resta una voce.** È la stessa conclusione del 31/10 ("si riapre solo con una
cifra scritta"). Si sblocca in 15 minuti: Massimiliano apre dal suo browser le pagine "affiliates" di Currencies Direct e
TorFX e copia la cifra. Con 100 £ a cliente l'idea 3 cambierebbe (vedi sotto).

---

## 5. Le idee, in ordine

Formula comune: **€/anno = visite/anno × (AdSense per visita + quota che compra × commissione)**. Visite a 18 mesi stimate
partendo da Visa Income oggi (344 visite a settimana ≈ 18.000 l'anno su tutto il sito, dopo un mese di crescita).

### Idea 1 — Case a 1 euro: registro verificato comune per comune, con i prezzi veri e le aste (voto 6)

**Cosa:** sezione di Visa Income, in inglese (poi tedesco e olandese). Una pagina per comune (circa 100) e una pagina-elenco.
Per ogni comune: bando **aperto / chiuso / non trovato**, data dell'ultimo avviso letto sul sito del comune, link all'atto,
cauzione, termine dei lavori, data del nostro controllo. Accanto: quanto costa lì una casa normale (valori OMI per zona),
aliquota IMU 2026 del comune, e le case all'asta nello stesso comune o provincia (i nostri dati). Il messaggio onesto:
"la casa a 1 euro costa i lavori; qui a 200 metri una casa abitabile parte da X".

- **Vuoto dimostrato:** sì, su 3 concorrenti (1eurohouses/casea1euro, Idealista EN, Idealista DE): nessuno verifica lo stato, una pagina è ferma al 2021 con un contatto sbagliato.
- **Stima:** AdSense 0,004 €/visita; Wise 0,1 % × 11,5 €; AnchorLess 0,05 % × 14,9 € (centrale).
  - prudente: 8.000 visite → **~110 €/anno**
  - centrale: 40.000 visite → 160 + 460 + 300 = **~900 €/anno**
  - ottimista: 200.000 visite, Wise 0,2 %, AnchorLess 0,1 % → 1.000 + 4.600 + 2.980 = **~8.600 €/anno**
- **Ore:** 40-60 degli agenti (100 comuni da leggere uno per uno), 8 ogni trimestre per ricontrollare; Massimiliano 30 minuti (link Wise e AnchorLess). 0 €.
- **Rischi:** le parole grandi sono di CNN, Idealista e 1eurohouses; il pubblico sogna più di quanto compri (conversioni basse); il controllo è a mano e invecchia; un comune può avere il bando solo in PDF.
- **Perché non 7:** sotto i 5.000 € centrali; due pagatori su due non ancora collegati.

### Idea 2 — IMU per chi ha casa in Italia e vive all'estero: aliquota 2026 del comune e calcolatore, in tedesco e inglese (voto 5,5)

**Cosa:** sezione di Visa Income (`/de/` e inglese; olandese dopo). Un calcolatore (rendita, comune, mesi, quota) con
l'aliquota ufficiale 2026 di ogni comune presa dal prospetto, numero e data della delibera, scadenze 16 giugno e 16 dicembre,
come pagare dall'estero, riduzione per i pensionati esteri. Pagine singole solo per i 300-500 comuni con seconde case di
stranieri (laghi, Toscana, Liguria, Puglia, Sardegna), non per tutti i 7.896.

- **Prova più forte del fronte:** i dati. migliaia di PDF ufficiali tutti uguali (uno zip per regione), letti in automatico 40 su 40.
- **Domanda:** tedesca soprattutto ("imu italien" 10, "grundsteuer italien" 10 con rechner, ferienhaus, ausländer), poi inglese ("italian property tax calculator", "how to pay imu from abroad") e olandese. Ricorre due volte l'anno.
- **Vuoto:** dimostrato sulle 6 pagine lette (nessuna dà l'aliquota del comune né un calcolatore in tedesco o inglese). **Non dimostrato sui risultati di Google**, che non si leggono dal server: voto fermo a 5,5 finché un verificatore con la ricerca web non conferma.
- **Pagatore debole:** i tedeschi e gli olandesi pagano già in euro, Wise non serve. Resta AdSense, più Wise per britannici e americani.
- **Stima:** AdSense 0,006 €/visita; Wise 0,3 % dei soli visitatori in inglese (40 %).
  - prudente: 6.000 visite → **~60 €/anno**
  - centrale: 30.000 visite → 180 + 12.000 × 0,3 % × 11,5 = **~600 €/anno**
  - ottimista: 120.000 visite, Wise 0,5 % → 720 + 2.760 = **~3.500 €/anno**
- **Ore:** 25-35 degli agenti; Massimiliano 0. La scadenza del 16/12/2026 è troppo vicina: obiettivo 16/6/2027, pagine online entro marzo.
- **Rischi:** responsabilità sul calcolo (va scritto "esempio, chiedi al comune"); in Alto Adige e Trentino l'imposta è un'altra (IMI, IMIS); al Sud molti comuni non hanno il prospetto.

### Idea 3 — "Buying property in Italy" per nazionalità, con calcolatore dei costi d'acquisto (voto 4,5)

**Cosa:** pagine per americani, britannici, canadesi, australiani (le nazionalità dell'autocomplete), con calcolatore di
registro/ipotecaria/catastale/IVA, codice fiscale, link alla scheda di reciprocità.

- **Vuoto:** non c'è. Dieci guide del 2026 in prima pagina, movingto è completa e corretta. Manca solo il calcolatore, che nessuno cerca ("italy property purchase tax calculator" 0 suggerimenti). La reciprocità non si legge dal server.
- **Stima:** prudente **~30**, centrale **~250** (15.000 visite), ottimista **~1.500 €/anno**. Ore 15-20.
- **Si riapre a 6** solo con una cifra scritta da un cambiavalute: a 100 £ (≈ 115 €) per cliente, 15.000 visite × 0,1 % = 15 clienti → +1.700 €/anno.

### Scartate
- **Prezzo al m² per comune in inglese (valori OMI), una pagina per comune:** massimo 5. Idealista (non leggibile) ha già i rapporti per comune in inglese, Magic Towns ha le pagine di tutti i comuni, la domanda scritta è sulle città note. I valori OMI servono come riga dentro le idee 1 e 2, non come sezione.
- **Aste giudiziarie in inglese per stranieri:** domanda vera ("italy property auctions" 7) e dato tutto nostro, ma concorrenti non letti: massimo 5. Da provare senza costi come blocco dentro l'idea 1 e, se quelle pagine prendono visite, come pagine `/en/` di Aste in Chiaro.
- **Sito nuovo:** no. Nessuna idea regge da sola; Magic Towns occupa già "un comune, una pagina".

---

## 6. Le 4 prove

| Prova | Idea 1 (1 euro) | Idea 2 (IMU) | Idea 3 (guida) |
|---|---|---|---|
| Domanda | **sì** (10 suggerimenti in US, GB, DE; 9 in NL) | **sì** in tedesco, media in inglese | sì sulle parole grandi |
| Dati ufficiali leggibili | **a metà**: siti dei comuni uno per uno, nessun elenco ufficiale | **sì**, la migliore | a metà: reciprocità non leggibile |
| Pagatore attivo | a metà: AnchorLess 14,90 € letta ma iscrizione in attesa; Wise senza link nostro | **debole**: quasi solo AdSense | a metà, come l'idea 1 |
| Nessuno lo fa meglio | **sì** sullo stato dei bandi (3 concorrenti letti) | sì sulle pagine lette, **da confermare** sulla ricerca | **no** |

## 7. Dove va e cosa fare

1. **Nessun sito nuovo.** Tutto come sezione di Visa Income (pubblico inglese che si trasferisce, già 344 visite a settimana, ha già `/es/` e `/pt/`: un `/de/` è lo stesso lavoro).
2. Se si costruisce qualcosa: prima l'idea 1 con dentro la riga IMU e le aste; l'idea 2 entro marzo 2027 solo se il verificatore conferma il vuoto in tedesco.
3. Prima di costruire: verifica indipendente con la ricerca web (risultati di Google per "1 euro houses italy 2026", "imu italien rechner", "italian property tax calculator").
4. Massimiliano, 15 minuti, zero euro: leggere dal browser la cifra per cliente di Currencies Direct e TorFX. È l'unico modo per sapere se questo fronte può valere dieci volte tanto.

Non letti e non aggirati: esteri.it (captcha), idealista.it rapporti prezzi e immobiliare.it (403), Currencies Direct, TorFX,
Lumon, getlasso (403), globalpropertyguide (403), properstar (429), motori di ricerca.
