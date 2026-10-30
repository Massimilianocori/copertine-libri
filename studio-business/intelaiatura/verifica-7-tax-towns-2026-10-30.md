# Verifica indipendente: "Italy 7 % tax towns" (30/10/2026)

Idea verificata: sezione di Visa Income Checker con l'elenco dei Comuni ammessi alla flat tax del 7 % per i pensionati stranieri (art. 24-ter TUIR). Voto del ricercatore: **8** (rapporto `ricerca-numeri-ufficiali-2026-10-30.md`, sez. 2.1, letto per intero).

Tutte le prove sono state raccolte il 30/10/2026 dal nostro server (curl, stato HTTP indicato) o con la ricerca web della stessa sera.

---

## Verdetto in breve

**DA ABBASSARE a 4,5.**

La legge è stata letta correttamente nel punto principale: la soglia a 30.000 abitanti esiste davvero. Anche i conteggi ISTAT sono giusti. Ma l'idea cade su tre prove:

1. **Il buco non c'è più.** magictowns.it pubblica **gratis**, in inglese, l'elenco completo che vogliamo costruire: 2.535 Comuni, una pagina per regione, una per Comune, una mappa con un punto per Comune e la regola corretta sull'anno di popolazione ("last verified 26 October 2026"). Il rapporto diceva "elenco completo solo per gli abbonati": oggi non è vero.
2. **Il rapporto sbaglia la regola sui Comuni del terremoto.** Il tetto dei 3.000 abitanti è stato abolito nel 2022. Oggi vale 30.000 anche lì, e si aggiungono circa 111 Comuni di Marche, Lazio e Umbria (Fabriano compresa). Le persone li cercano già: in autocomplete c'è "7 tax towns in umbria italy". L'idea era pensata su 8 regioni.
3. **Il rapporto usa l'anno di popolazione sbagliato.** Per l'Agenzia delle Entrate conta la popolazione ISTAT al **1° gennaio dell'anno prima** del trasferimento. Chi si trasferisce nel 2026 deve guardare i dati all'1/1/2025, non quelli all'1/1/2026. L'esempio di pagina del rapporto ("Ostuni: 29.803 residenti all'1/1/2026") usa l'anno sbagliato per il 2026. Grottaglie e Oristano sono **fuori** per chi si trasferisce nel 2026.

In più la legge cambia sede il 1° gennaio 2027: il TUIR attuale viene abrogato e la regola passa all'art. 247 del nuovo testo unico. Il concorrente lo scrive già.

---

## 1. La legge (Normattiva)

**Testo vigente dell'art. 24-ter TUIR** (Normattiva, 200, 175 KB, "Testo in vigore dal 7-4-2026 al 31-12-2026"):

- **Regioni:** Sicilia, Calabria, Sardegna, Campania, Basilicata, Abruzzo, Molise e Puglia.
- **Altri Comuni ammessi:**
  - i Comuni degli allegati 1, 2 e 2-bis al DL 189/2016 (terremoti del 2016-2017 in Centro Italia);
  - i Comuni colpiti dal terremoto del 6 aprile 2009 (L'Aquila).
- **Soglia:** "avente comunque una popolazione non superiore a ((30.000 abitanti))". La parola "comunque" vale per **tutti** i gruppi, quindi anche per i Comuni del terremoto.
- **Requisiti del pensionato:**
  - redditi da pensione pagati da soggetti esteri (art. 49, c. 2, lett. a);
  - nessuna residenza fiscale in Italia nei 5 periodi d'imposta precedenti;
  - trasferimento da un Paese con cui sono in vigore accordi di cooperazione amministrativa.
- **Durata:** "i primi nove periodi d'imposta successivi" a quello dell'opzione, cioè **10 anni in tutto**. Lo conferma la circolare 21/E: "l'anno … in cui il soggetto diventa fiscalmente residente in Italia e per gli ulteriori nove periodi di imposta".
- **Altre condizioni:** non c'è nessuna lista di "Comuni turistici" o altra condizione di luogo.

**Storia delle modifiche** (pagina "Aggiornamenti all'articolo" di Normattiva, 200):

| Data | Norma | Cosa cambia |
|---|---|---|
| 2018 | L. 145/2018 | introduce il regime |
| 2019 | DL 34/2019 | aggiunge i Comuni del sisma 2016 **fino a 3.000 abitanti**; durata portata a 10 anni |
| 2022 | DL 4/2022, art. 6-ter (L. 25/2022), in vigore dal 29/3/2022 | aggiunge il sisma 2009 e porta il tetto per tutti a **20.000** ("avente comunque") |
| 23/3/2026 | **L. 11 marzo 2026, n. 34, art. 26, c. 1** (GU n. 68) | **20.000 → 30.000**, in vigore dal **7/4/2026** |
| 3/7/2026 | **D.Lgs. 19 giugno 2026, n. 117**, art. 376, c. 1, lett. e) | **abroga l'intero TUIR dal 1/1/2027** |

Normattiva, versione al 2027-01-01 dell'art. 24-ter: "PROVVEDIMENTO ABROGATO DAL D.LGS. 19 GIUGNO 2026, N. 117".

**La legge 34/2026 esiste e cambia davvero la soglia.** Su questo il ricercatore aveva ragione.

**Dal 2027: art. 247 del nuovo Testo unico delle imposte sui redditi** (D.Lgs. 117/2026, Normattiva, articolo 247, 200):

- Il testo è lo stesso, con il titolo "Imposizione sostitutiva sui redditi da pensione di fonte estera dei soggetti che trasferiscono la residenza in Italia (articolo 24-ter …)".
- La prima versione (in vigore dal 4/7 al 6/8/2026) diceva per errore **20.000** abitanti.
- Il **D.Lgs. 5 agosto 2026, n. 141**, art. 2, c. 1, lett. ss) l'ha corretta a **30.000**, in vigore dal 7/8/2026.
- Si applica dal 1/1/2027 (art. 377).

Una pagina costruita oggi dovrebbe quindi citare due norme e cambiare riferimento il 1° gennaio.

**Errore del rapporto (sez. 2.1, tabella fonti e "Numeri contati"):** dice che i Comuni del terremoto entrano solo con "≤ 3.000 abitanti, circa un centinaio". È la regola del 2019, abolita il 29/3/2022.

---

## 2. Quale anno di popolazione conta

**Circolare 21/E del 17/7/2020** (agenziaentrate.gov.it, PDF ufficiale, 200, 191 KB), pagine 5-6:

> "si considera il dato della popolazione residente risultante dalla 'Rilevazione comunale annuale del movimento e calcolo della popolazione', pubblicata sul sito dell'ISTAT, riferito al 1° gennaio dell'anno precedente a quello in cui avviene il trasferimento della residenza fiscale in Italia."

Lo stesso dato vale per tutti i 10 anni, salvo cambio di Comune. Se la persona cambia Comune, si guarda la popolazione all'1/1 dell'anno prima del nuovo trasferimento.

**Scheda dell'Agenzia "Regime opzionale per i pensionati esteri – Che cos'è"** (agenziaentrate.gov.it, 200, "Ultimo aggiornamento: 8 maggio 2026"):

- "popolazione non superiore a 30mila abitanti (tale limite è in vigore dal 7 aprile 2026, in precedenza era 20mila abitanti)";
- "Possono beneficiarne anche i pensionati esteri che trasferiscono la residenza in uno dei comuni, **sempre con non più di 30mila abitanti**, interessati dagli eventi sismici del 6 aprile 2009 … o … del 2016";
- popolazione ISTAT "riferito al 1° gennaio dell'anno precedente il primo periodo di validità dell'opzione".

**Risposta a interpello n. 184/2026** (agenziaentrate.gov.it, 200; riguarda un IRA americano ereditato): riporta il testo con i 30.000 abitanti e richiama la circolare 21/E. Non dice nulla di nuovo sull'anno di riferimento.

**Cosa ne segue:**

- **Chi si trasferisce nel 2026 deve usare la popolazione all'1/1/2025.** Il "2.426 all'1/1/2026" del rapporto vale per chi si trasferisce nel 2027.
- Il file ISTAT 2026 è intestato "Popolazione residente per età e sesso al 1° gennaio 2026 **(stima)**": è un dato provvisorio. Per i Comuni vicini alla soglia può ancora cambiare.
- **Resta un punto incerto:** chi si è trasferito tra il 1° gennaio e il 6 aprile 2026 in un Comune tra 20.000 e 30.000 abitanti. Nessun documento ufficiale letto stasera lo chiarisce. Alcune testate (taxing.it, globalcitizensolutions) parlano di "caso per caso".

---

## 3. Dati ISTAT ricontati

**File scaricati e contati stasera:**

| File | Stato | Dimensione |
|---|---|---|
| `demo.istat.it/data/posas/POSAS_2025_it_Comuni.zip` | 200 | 8.522.158 byte |
| `demo.istat.it/data/posas/POSAS_2026_it_Comuni.zip` | 200 | 4.579.670 byte |
| `istat.it/.../Elenco-comuni-italiani.csv` | 200 | – |

Ci sono 7.896 Comuni in tutti e tre i file e nessun codice manca. Per ogni Comune ho preso la riga 999, cioè il totale.

| | 1/1/2025 (vale per chi si trasferisce nel 2026) | 1/1/2026, stima (vale per chi si trasferisce nel 2027) |
|---|---|---|
| Comuni delle 8 regioni | 2.551 | 2.551 |
| ≤ 30.000 | **2.424** | **2.426** |
| ≤ 20.000 | 2.344 | 2.345 |
| Nuovi tra 20.000 e 30.000 | 80 | 81 |
| Puglia ≤ 30.000 | 231 | 232 |
| Sicilia ≤ 30.000 | 359 | 359 |
| Molise ≤ 30.000 | 134 | 134 |

I conteggi del rapporto sono giusti. Puglia 231 con i dati 2025 coincide con la cifra di magictowns.

**Comuni del terremoto in Lazio, Marche e Umbria** (allegati 1, 2 e 2-bis letti su Normattiva, 62 + 69 + 9 nomi):

- 117 nomi sono fuori dalle 8 regioni.
- 106 di questi si trovano su ISTAT e hanno ≤ 30.000 abitanti.
- Altri 7 nomi sono di Comuni poi fusi o scritti in modo diverso (Acquacanina, Fiordimonte, Pievebovigliana, ecc.). Sono tutti piccoli.
- Restano fuori Rieti, Ascoli Piceno, Macerata e Spoleto (tra 35.000 e 45.000 abitanti) e Teramo (51.400, in Abruzzo).
- **Fabriano** (28.597 abitanti nel 2025) **entra**.
- magictowns conta **111** Comuni del terremoto (Marche 83, Lazio 14, Umbria 14): torna con il mio conto.
- Totale reale: circa **2.535**, non "2.426 più un centinaio sotto i 3.000".

**Comuni vicini alla soglia** (popolazione 2025 → 2026; i valori del rapporto sono confermati):

| Comune | 1/1/2025 | 1/1/2026 | Trasferimento nel 2026 | Trasferimento nel 2027 |
|---|---|---|---|---|
| Ostuni | 29.943 | 29.803 | dentro | dentro |
| Manduria | 29.665 | 29.528 | dentro | dentro |
| Oristano | 30.067 | 29.888 | **fuori** | dentro (dato provvisorio) |
| Grottaglie | 30.198 | 29.976 | **fuori** | dentro (dato provvisorio, 24 abitanti di margine) |
| Lucera | 30.591 | 30.335 | fuori | fuori |
| Comiso | 30.214 | 30.437 | fuori | fuori |
| Nardò | 30.752 | 30.784 | fuori | fuori |
| Avola | 30.710 | 30.683 | fuori | fuori |

---

## 4. Domanda e concorrenza

**Autocomplete del 30/10/2026** (`client=firefox`, `hl=en`; risultati uguali con `gl=us` e `gl=gb`):

- "italy 7 tax" → 10 (*regions, towns, towns map, map, scheme, regions map, regime, areas*);
- "7 tax towns" → 10 (*italy map, in italy, **in umbria italy**, map pdf, in puglia, in abruzzo italy, in sicily, in sardinia, in puglia map*);
- "italy 7 percent tax" → 9 (*on passive income, pension tax*);
- "italy flat tax pensioners" → 7;
- "puglia 7 tax" e "abruzzo 7 tax" → "… 7 tax towns" al primo posto;
- "ostuni 7" → "ostuni 7 tax"; "lecce 7 tax" → 10 (in coda);
- vuoti: "italy 7 tax towns list" (3, generici), "italy 7 flat tax towns" (0), "italy 7 tax 30000" (0), "italy 7 tax marche" (0);
- "sicily 7 tax", "sardinia 7 tax" e "calabria 7 tax" → solo taxi e tasse generiche.

La domanda è vera, ma è quasi tutta per **mappa, elenco e regione**. Le ricerche per singolo Comune ci sono solo per Ostuni e Lecce. Le 2.400 pagine per Comune non hanno domanda dimostrata.

**Concorrenza (pagine scaricate il 30/10/2026):**

- **magictowns.it/7-percent-towns/** (200, 716 KB):
  - "2,535 of Italy's 7,896 comuni qualify (last verified 26 October 2026)";
  - "Population is ISTAT's figure at 1 January of the year before you move … This list is for a move in 2026, on ISTAT population at 1 January 2025";
  - "article 24-ter … until 31 December 2026, and article 247 of the new TUIR (Legislative Decree 117/2026) from 1 January 2027";
  - "Some guides still print a separate 3,000-resident cap for earthquake towns: it was abolished in 2022";
  - mappa interattiva "Every eligible town, one dot each";
  - "The full list, region by region, is below";
  - avviso "This page explains the statute; it is not tax advice".
- **Pagine per regione di magictowns** (`/7-percent-towns/puglia/`, 200: 238 link a pagine di Comuni; `/earthquake-areas/`, 200: 111 Comuni, Fabriano compresa). **Sono gratis.** A pagamento ci sono solo il confronto tra Comuni, alcune mappe tematiche e la consulenza.
  - Ogni pagina ha per ogni Comune anche dati che noi non abbiamo: ospedale, internet, mare, altitudine, residenti di lingua inglese.
- **impatria.com**, "Comuni 7% Pensionati 2026: la Mappa Aggiornata" (25/8/2026, 200): in italiano, ha la regola giusta (anno prima, terremoto con tetto 30.000, 10 anni).
- **Altri nella prima pagina** (ricerca web): we-wealth, Feather, youroverseashome, imidaily, globalcitizensolutions, movingto (servizio a pagamento), frankvest, expatslivinginrome, una pagina Notion e una guida su `pages.dev` scritta in automatico.

**Conclusione: esiste già un elenco gratuito, completo, aggiornato e con la regola giusta, su un sito specializzato e con molta più profondità.** Noi arriveremmo secondi, con meno dati.

---

## 5. Rischi

1. **Consulenza fiscale.** Tema "soldi" (YMYL). Una pagina che dice "Grottaglie è ammessa" a chi si trasferisce nel 2026 dà un'informazione **sbagliata**, e il lettore potrebbe sceglierla per risparmiare decine di migliaia di euro in 10 anni. Il rapporto proponeva proprio questo errore (anno 2026 in alto).
2. **Errori nell'elenco.** Il rapporto aveva due errori di regola: il tetto dei 3.000 per i Comuni del terremoto e l'anno di popolazione. Con la revisione proposta (20 Comuni controllati su ISTAT) nessuno dei due sarebbe emerso, perché sono errori di **regola**, non di dati.
3. **Cambi di legge già in calendario:**
   - il 1/1/2027 cambia l'articolo (24-ter → 247 del D.Lgs. 117/2026);
   - la prima versione dell'art. 247 aveva un errore (20.000), corretto dopo un mese;
   - ogni anno ISTAT pubblica la stima e poi il dato definitivo.
   Servirebbe una manutenzione attenta, su un tema dove il concorrente è già più rapido (verifica del 26/10).
4. **Domanda per Comune non provata.** Le 2.400 pagine per Comune rischiano di essere pagine sottili, quasi uguali a quelle di magictowns.

---

## 6. Ricalcolo del voto

| Voce | Ricercatore | Verifica | Perché |
|---|---|---|---|
| Domanda | 2,5 | 2 | vera per mappa, elenco e regione; quasi nulla per Comune |
| Buco | 1,5 | **0** | elenco completo gratis su magictowns (verificato il 26/10/2026), più impatria |
| Fonte | 2 | 1,5 | ISTAT e Normattiva vanno bene, ma la regola va letta su 3 norme e 1 circolare; il dato 2026 è una stima |
| Valore | 1,5 | 1 | pagatori piccoli (italki, DiscoverCars, SafetyWing, Wise); nessuno vende casa o trasloco |
| Rischi e ore | 0,5 | 0 | errore costoso per il lettore; due cambi di norma in 9 mesi |
| **Totale** | **8** | **4,5** | |

---

## 7. Cosa fare invece (al massimo 2-3 ore, non 14-22)

Non costruire la sezione con 2.400 pagine. Se Massimiliano vuole comunque coprire il tema per il pubblico dei pensionati di Visa Income Checker, basta **una pagina di riferimento**, collegata dalla futura pagina sul visto di residenza elettiva. La pagina deve avere:

1. **La regola con le fonti e la data in alto:**
   - art. 24-ter TUIR fino al 31/12/2026, art. 247 del D.Lgs. 117/2026 dal 1/1/2027;
   - L. 34/2026 per la soglia di 30.000;
   - circolare 21/E e scheda dell'Agenzia dell'8/5/2026 per l'anno di popolazione.
2. **Una tabella per regione** con il conteggio e l'anno usato ("move in 2026 → ISTAT 1 Jan 2025") e le 3 righe dei Comuni del terremoto (Marche, Lazio, Umbria).
3. **Un riquadro "borderline"** con i Comuni tra 29.000 e 31.000 abitanti, con entrambi gli anni e il dato 2026 segnato come provvisorio.
4. **Frasi prudenti obbligatorie:**
   - "This page summarises the law; it is not tax advice";
   - "Eligibility depends on your pension, your previous country and your own tax position: confirm with an Italian tax adviser (commercialista) before you move";
   - "The population that counts is ISTAT's figure at 1 January of the year before your move".
5. **Link affiliati adatti:** Wise (trasferire la pensione in euro), SafetyWing (viaggi di sopralluogo, con i suoi limiti di età), DiscoverCars (sopralluoghi in auto), italki (italiano).

Si sale di voto solo con un fatto nuovo. Per esempio: magictowns rimette l'elenco a pagamento, oppure chiude.

---

## Fonti lette il 30/10/2026

- 200 `https://www.normattiva.it/uri-res/N2Ls?urn:nir:presidente.repubblica:decreto:1986-12-22;917~art24ter!vig=` (vigente: 30.000, dal 7/4/2026 al 31/12/2026)
- 200 stesso URN con `!vig=2027-01-01` (abrogato dal D.Lgs. 117/2026), `!vig=2026-04-06` (20.000, dal 29/3/2022), `!vig=2021-06-01` (tetto dei 3.000 per i Comuni del terremoto, 2019-2022)
- 200 Normattiva, "Aggiornamenti all'articolo" 24-ter (L. 34/2026 art. 26 c. 1; D.Lgs. 117/2026 art. 376 c. 1 lett. e)
- 200 Normattiva, D.Lgs. 19/6/2026 n. 117, art. 247 versione 1 (20.000) e 2 (30.000 dal 7/8/2026), aggiornamenti (D.Lgs. 5/8/2026 n. 141 art. 2 c. 1 lett. ss), art. 377 (dal 1/1/2027)
- 200 Normattiva, DL 189/2016, allegati 1, 2, 2-bis
- 200 `https://www.agenziaentrate.gov.it/portale/documents/20143/0/Circolare+n.+21E+del+17.07.2020.pdf/96191701-87ef-ce63-e163-a8a6e37e64ad`
- 200 `https://www.agenziaentrate.gov.it/portale/schede/agevolazioni/regime-opzionale-per-i-pensionati-esteri-che-cose-cittadini` (aggiornata l'8/5/2026)
- 200 `https://www.agenziaentrate.gov.it/portale/documents/20143/10360383/Risposta+n.+184_2026.pdf/e7e33151-596b-3aaa-2634-122c4d6bf366`
- 200 `https://demo.istat.it/data/posas/POSAS_2025_it_Comuni.zip`, `POSAS_2026_it_Comuni.zip`; `https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.csv`
- 200 `https://magictowns.it/7-percent-towns/`, `/7-percent-towns/puglia/`, `/7-percent-towns/earthquake-areas/`
- 200 `https://impatria.com/?p=9698`
- Autocomplete: `https://suggestqueries.google.com/complete/search?client=firefox&gl={us,gb}&hl=en&q=…` (20 query per Paese)
