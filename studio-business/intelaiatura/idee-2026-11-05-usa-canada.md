# Ricerca a rotazione del 5/11/2026: Stati Uniti e Canada

Compito: trovare cloni dei due modelli che funzionano, con il nome di chi paga e la cifra:
- **EsameB1**: un passaggio burocratico obbligatorio con calendario, sedi o costi ufficiali per città;
- **Visa Income**: numeri ufficiali per nazionalità o per luogo, che le persone cercano e gli assistenti AI citano.

Preferenza per sezioni di siti esistenti.

**Letti prima:**
- `ESPLORATE.md` per intero (823 righe);
- `ricerca-zona-usa-2026-10-30.md` e `ricerca-zona-canada-australia-2026-10-30.md`;
- `wf-2026-10-31-usa-amministrazione.md` e `wf-2026-10-31-esami-mondo.md`, per non rifare CPA, bar exam, GED, DMV, notai, passaporti e USCIS.

Non ho rivalutato le famiglie già chiuse. Le principali: affitti con tetto (AB 1482, Ontario), travel ban e visa bond, rifiuti dei visti USA, I-864, proof of funds del Canada, TEF/TCF, patente straniera in Canada, snowbird, salario minimo, ServSafe "near me", patente nautica e PCOC, licenze e reciprocità, salari H-1B per datore (14/10).

**Prove** (tutte del 5/11/2026):
- circa 60 interrogazioni all'autocomplete (`client=firefox`, gl=us/ca/gb/de/it);
- 7 ricerche web (strumento USA);
- circa 50 curl dal server, con lo stato HTTP scritto accanto a ogni fonte.

Limiti: niente volumi di ricerca veri, quindi le cifre in euro sono stime con le assunzioni scritte. Le pagine affiliati lette direttamente sono poche: lo dico ogni volta che una cifra viene da terzi.

---

## 0. Risposta in breve

| # | Idea | Modello | Dove | Voto | €/anno a 18 mesi (prud. / centr. / ott.) | Ore | Chi paga |
|---|---|---|---|---|---|---|---|
| 1 | **Livello salariale H-1B per occupazione × area e probabilità nella lotteria pesata** (OFLC luglio 2026-giugno 2027, regola del 29/12/2025) | Visa Income (soglia di reddito per luogo) | sezione di **Visa Income** | **7** | 200 / 1.050 / 4.200 | 12-18 | AdSense (già acceso), pubblico USA tech e immigrazione |
| 2 | **Tassa sugli alberghi nelle città di USA e Canada** (percentuali + tasse fisse + date: Chicago TID 1,5 % da maggio 2026, NYC 1,50 $ + 2 $ a notte, contee della Florida, città del Texas, MAT di Toronto) | Visa Income per luogo / Tourist Tax | modulo di **Tourist Tax** | **6,5** | 150 / 700 / 2.500 | 15-25 | AdSense (acceso); DiscoverCars ~20 $ a noleggio (link già attivo su Tourist Tax); Stay22 dopo l'iscrizione |
| 3 | Tasso di promossi all'esame da agente immobiliare per scuola e Stato | EsameB1 (esame obbligatorio) | sito nuovo o nessuno | 5 | – | – | Aceable via CJ: 10-20 % o 25 $ a vendita (cifre di terzi) |
| 4 | CELPIP, IELTS General e PTE Core per città (Canada ed estero) per residenza permanente e cittadinanza | EsameB1 | – | 5 (RISERVA) | – | – | preparazione ai test: nessun programma letto |
| 5 | Licenza di matrimonio: costo e attesa per contea o provincia | EsameB1 (passaggio obbligatorio per contea) | – | NO (4,5) | – | – | HitchSwitch 10-15 % (già letto il 31/10) |
| 6 | Food handler card e licenza per servire alcolici per Stato e provincia (TABC, RBS, Smart Serve, Serving It Right, ProServe) | EsameB1 | – | NO (4,5) | – | – | corsi da 7-15 $, programmi non letti |
| 7 | Tetto settimanale dei workers' comp per Stato e massimale WCB per provincia | Visa Income per luogo | – | RISERVA debole (5, non approfondita) | – | – | AdSense con annunci legali |

**La migliore è la n. 1, che però non arriva a 8.** Mette in pagina, per la prima volta, il salario che serve per avere 1, 2, 3 o 4 biglietti nella lotteria H-1B, per occupazione e per area. Sono dati ufficiali completi, scaricati e letti stasera. È la forma "soglia di reddito per luogo" di Visa Income e ha una scadenza naturale: la registrazione per l'anno fiscale 2028 apre a marzo 2027.

Le manca un pagatore con nome oltre ad AdSense: per questo resta a 7.

**Nessuna idea a 8.** La lezione è la stessa del 30/10: negli USA quasi ogni passaggio obbligatorio per Stato (licenze, corsi obbligatori per lavorare, matrimoni) ha già in prima pagina chi vende il corso, oppure siti automatici su `pages.dev`. Restano liberi i numeri ufficiali nuovi, nati da una regola recente: la lotteria pesata dal 27/2/2026 e la tassa del distretto turistico di Chicago da maggio 2026.

**Costruibili subito a costo zero come sezione:**
- **Visa Income, `/h1b-wage-level/`**: una pagina per ogni coppia occupazione × area, più un calcolatore. Fonte: `flag.dol.gov/sites/default/files/wages/OFLC_Wages_2026-27.zip` (200, 12,6 MB, CSV) e Federal Register API (200).
- **Tourist Tax, modulo "US & Canada hotel tax"**: circa 50 città scritte a mano dalle pagine ufficiali, le 67 contee della Florida e le città del Texas. Fonti: `floridarevenue.com/Forms_library/current/dr15tdt.pdf` (200, revisione 10/26) e `data.texas.gov/resource/er34-v24h.json` (200).

---

## 1. Idea 1 (voto 7): livello salariale H-1B per occupazione × area e probabilità nella lotteria pesata

### 1.1 In una riga
Una sezione di Visa Income con una pagina per ogni coppia occupazione × area. Esempio: "Software Developers (15-1252) in San Jose: Level I 152.797 $, II 187.075 $, III 221.374 $, IV 255.653 $ — the salary you need for 1, 2, 3 or 4 lottery entries". Ogni pagina riporta:
- la probabilità stimata per livello, con il calcolo scritto;
- la fonte OFLC con la data;
- la regola della lotteria pesata con il link al Federal Register.

Si aggiungono un calcolatore (stipendio + occupazione + contea → livello → biglietti → probabilità) e pagine indice per occupazione e per città.

### 1.2 Perché non è un'idea già chiusa
Il 14/10 "salari H-1B" era NO: si parlava dei salari pagati da ogni datore (dati LCA), un campo dominato da h1bdata.info e myvisajobs.

Qui la domanda è un'altra e prima non esisteva. Dalla regola finale del 29/12/2025, in vigore dal 27/2/2026 per la lotteria dell'anno fiscale 2027, **il livello salariale OEWS dell'area decide quanti biglietti si hanno** (Level I = 1 biglietto, Level IV = 4). Lo stesso stipendio vale quindi un livello diverso a San Jose e ad Atlanta.

### 1.3 Fonte (curl e lettura del 5/11/2026)
- `https://flag.dol.gov/wage-data/wage-data-downloads` → **200**, con i link agli zip di ogni anno.
- `https://flag.dol.gov/sites/default/files/wages/OFLC_Wages_2026-27.zip` → **200**, application/zip, 12.652.309 byte, last-modified 1/7/2026. Contiene:
  - `ALC_Export.csv`: 449.441 righe, colonne `Area, SocCode, GeoLvl, Level1, Level2, Level3, Level4, Average`, salari orari;
  - `Geography.csv`: area con nome, Stato e contea;
  - `oes_soc_occs.csv`: nomi delle occupazioni;
  - le note tecniche.
- Esempio calcolato stasera (15-1252 Software Developers, salario orario × 2.080 ore):

| Area | Level I | Level II | Level III | Level IV |
|---|---|---|---|---|
| San Jose-Sunnyvale-Santa Clara, CA | 152.797 $ | 187.075 $ | 221.374 $ | 255.653 $ |
| New York-Newark-Jersey City | 109.845 $ | 137.717 $ | 165.589 $ | 193.461 $ |
| Seattle-Tacoma-Bellevue | 111.613 $ | 143.104 $ | 174.595 $ | 206.086 $ |
| Dallas-Fort Worth-Arlington | 95.202 $ | 116.896 $ | 138.590 $ | 160.285 $ |
| Atlanta-Sandy Springs-Roswell | 91.915 $ | 113.776 $ | 135.658 $ | 157.518 $ |

- Federal Register API (`federalregister.gov/api/v1/documents.json`) → **200**. Documenti trovati:
  - 29/12/2025, regola finale "Weighted Selection Process…";
  - 25/8/2026, proposta "Fee for Certain H-1B Petitions";
  - 23/9/2026, proclamazione "Restriction on Entry of Certain Nonimmigrant Workers".

  Lo script può seguire i cambi di regola da solo.
- Licenza: dati del governo federale, pubblico dominio.
- I dati si aggiornano ogni luglio; il prossimo file uscirà a luglio 2027.

### 1.4 Domanda (autocomplete gl=us, 5/11)
- "h1b wage level" → 10: *check, calculator, 2 salary range, 3 salary range, 4 salary range, salary range, map, increase, 1 salary range*;
- "h1b weighted lottery" → 10: *rule, reddit, system, wage levels, salary weighted…*;
- "h1b lottery odds" → 10: *2026, 2027, reddit, masters, odds calculator, chances, probability*.

La domanda per livello e per stipendio esiste ed è recente, perché la regola è del 2026.

### 1.5 Google oggi
In prima pagina per "h1b wage level calculator weighted lottery odds":
- studi legali e giornali di settore: Seyfarth, Mayer Brown, JD Supra, Pryor Cashman, Adams and Reese, CILawGroup, Brown Immigration, mondaq;
- un simulatore di Lawfully, che lavora per livello e non per area;
- blog (visa-pros, legalservicesincorporated).

**Nessuno ha una pagina per occupazione × area con le quattro soglie in dollari l'anno e le probabilità.** Lo strumento ufficiale (flcdatacenter.com, ricerca salari) dà le soglie in un modulo scomodo e non dice nulla della lotteria.

Probabilità citate dalle fonti, da riportare come stime DHS con il link: circa 15 % al Level I, 30 % al II, 45 % al III, contro circa 29,6 % con il vecchio sistema.

### 1.6 Chi paga
- **AdSense**, già acceso su Visa Income. Il pubblico è fatto di laureati e lavoratori tech negli USA, più datori e risorse umane. Ipotesi: 8-14 € ogni 1.000 pagine viste, perché gli annunci di immigrazione e di software per le risorse umane valgono molto.
- **Nessuna affiliazione con nome verificata stasera.** Gli studi legali comprano contatti, ma non pubblicano un programma per editori. Wise (già nel piano, "CPA rates start at £10") è debole qui. Per onestà non conto altro.

### 1.7 Stima (18 mesi)
Pagine: circa 40 occupazioni H-1B frequenti × circa 60 aree principali = 2.400, più 100 indici e il calcolatore. Picco tra gennaio e marzo, prima della registrazione.

| | prudente | centrale | ottimista |
|---|---|---|---|
| pagine viste al mese (media) | 2.000 | 8.000 | 25.000 |
| € ogni 1.000 pagine | 8 | 11 | 14 |
| **€/anno** | **~200** | **~1.050** | **~4.200** |

### 1.8 Ore, rischi, voto
**Ore: 12-18.** Un solo CSV con il join verso area e occupazione, il motore di pagine di Visa Income, il calcolatore in JavaScript e il controllo del Federal Register.

**Rischi:**
- la regola è contestata in tribunale e potrebbe cadere;
- il livello dipende anche dalle mansioni scelte dal datore, non solo dallo stipendio: ogni pagina deve dire "stima, non consulenza legale";
- la proposta di tassa sulle petizioni (25/8/2026) può cambiare il quadro: è una ragione in più per la pagina, ma va seguita;
- nessun pagatore oltre AdSense.

**Voto 7:** domanda 2,5 · buco 1,5 · fonte 2 · soldi 0,5 · rischi e ore 0,5.

**Cosa la porta a 8:**
1. un programma di affiliazione legato all'H-1B, con cifra letta (servizi legali a prezzo fisso, software per le risorse umane);
2. almeno 100 visite a settimana entro 30 giorni dalle prime 300 pagine, da pubblicare entro metà gennaio 2027.

---

## 2. Idea 2 (voto 6,5): tassa sugli alberghi nelle città di USA e Canada (modulo di Tourist Tax)

### 2.1 In una riga
Tourist Tax copre oggi 17 Paesi e nessuna città di USA o Canada. Il modulo nuovo aggiunge circa 50 città:
- USA: NYC, Chicago, Las Vegas, Orlando, Miami, Honolulu, San Francisco, Los Angeles, Anaheim, New Orleans, Nashville, Boston, Washington DC, Seattle, Austin, Houston, Dallas, San Antonio…;
- Canada: Toronto, Ottawa, Vancouver, Montréal, Québec, Banff, Niagara Falls.

Per ogni città: il conto con le percentuali sommate (Stato, contea, città, distretto turistico) e le tasse fisse a notte. Il motore ha già il tipo `percent` e le date `dal`/`al`; servono la quota fissa per camera e le soglie di prezzo di NYC.

Due file ufficiali coprono in automatico le 67 contee della Florida e le città del Texas.

### 2.2 Domanda (autocomplete del 5/11)
- us: "hotel tax in" → 10 (*florida, texas, nyc, california, washington dc, chicago, las vegas, tennessee, indiana, hawaii*);
- us: 10 suggerimenti ciascuna per "nyc / chicago / hawaii / las vegas / orlando / san francisco / nashville / new orleans hotel tax", quasi tutte con *rate, taxes and fees, calculator*, spesso *2026* e *increase 2026*;
- ca: "toronto / vancouver / montreal hotel tax" 10 ciascuna, "municipal accommodation tax" 10 (*ontario, toronto, ottawa, wasaga beach, mississauga*), "quebec lodging tax" 10;
- gb: "new york hotel tax" 10 e "hotel tax new york" 10;
- it: "tassa soggiorno new york" 9 (*2026, booking, manhattan, yotel*). Il pubblico europeo che va negli USA cerca nella sua lingua.

### 2.3 Fonti (curl 5/11)
| Fonte | Esito | Cosa c'è |
|---|---|---|
| `floridarevenue.com/Forms_library/current/dr15tdt.pdf` | **200**, PDF, "R. 10/26" | aliquota della tassa turistica di ognuna delle 67 contee e chi la incassa |
| `comptroller.texas.gov/transparency/local/hotel-reporting/` + `data.texas.gov/resource/er34-v24h.json` | **200**, JSON Socrata | aliquota comunale (cap. 351, es. Abilene 7 %) e di contea (cap. 334), anno fiscale 2025 |
| `comptroller.texas.gov/taxes/hotel/` | 200 | 6 % statale |
| `nyc.gov/.../business-hotel-room-occupancy-tax.page` | **200** | 5,875 %, quote fisse per fascia di prezzo, "Hotel Unit Fee ($1.50 per unit per day)" |
| `chicago.gov/.../hotel_accommodationstax.html` | **200** | 4,5 % comunale + **TID 1,5 % da maggio 2026** per i codici postali 60610-60661 |
| `toronto.ca/.../municipal-accommodation-tax/` | 200 | pagina in JavaScript: va letta con Playwright o a mano |
| `vancouver.ca`, `revenuquebec.ca` (taxe sur l'hébergement) | **403** | chiuse |
| `tax.hawaii.gov` (percorso TAT provato), `dor.wa.gov` (tabelle trimestrali delle tasse sull'alloggio) | 404 | URL da cercare; WA pubblica le tabelle trimestrali secondo Bloomberg Tax |
| `www2.gov.bc.ca` (MRDT) | 404 | URL da cercare |

### 2.4 Google oggi
Il buco **non è vuoto**:
- `roommaster.com/hotel-tax/<stato>` e `/hotel-tax/chicago` hanno pagine automatiche per Stato e per città;
- `taxo-com.pages.dev` ha guide 2026;
- `engine.com` ha un calcolatore delle 100 città, che dichiara dati 2024-2025;
- `19pine.ai` ha un calcolatore per città, che per Chicago dichiara incompleta la parte di contea;
- `str-tax-lookup.pages.dev` copre gli affitti brevi;
- c'è il rapporto HVS (a pagamento);
- ci sono le notizie sulla tassa di Chicago al 19 %, con date che si contraddicono (1/5 o 1/7/2026).

I nostri vantaggi:
- la fonte ufficiale con la data su ogni città;
- il calcolatore che cambia aliquota alla data esatta;
- le pagine in italiano e spagnolo, se il motore di Tourist Tax le regge.

Le pagine `pages.dev` sono in inglese.

### 2.5 Chi paga
- **AdSense**, già acceso su Tourist Tax. Pubblico USA di viaggio: 6-12 € ogni 1.000 pagine viste, la stessa ipotesi dei parchi del 30/10.
- **DiscoverCars**: "~$20 per booking", cookie 365 giorni. Il link `?a_aid=Massimilianocori` è già attivo sulle pagine del Messico. Vale per Orlando, Las Vegas, Honolulu, Miami e Banff, dove si noleggia.
- **Stay22**: il dominio è già nell'elenco ammesso di `monetizzazione.json`, ma l'iscrizione non risulta. Paga una quota della commissione degli alberghi e porta il valore più alto proprio su queste pagine, perché chi cerca "hotel tax" sta prenotando.

### 2.6 Stima, ore, voto
Circa 50 città + 67 contee della Florida + circa 150 città del Texas con aliquota sopra lo 0 = 250-300 pagine.

A 18 mesi: **150 / 700 / 2.500 €/anno**, con 1.500 / 6.000 / 18.000 pagine viste al mese a 8-11 € ogni 1.000.

**Ore: 15-25:**
- 50 città a mano con link e data;
- parser della Florida (PDF a 2 colonne) e del Texas (JSON);
- tipo di regola "percentuale + fisso per camera" nel motore;
- controllo trimestrale.

**Rischi:**
- le aliquote locali cambiano spesso: la Florida avverte "Not all counties notify the Department of changes";
- metà delle città richiede lettura a mano, contro la regola "tutto automatico";
- i concorrenti automatici ci sono già.

**Voto 6,5:** domanda 2,5 · buco 1 · fonte 1 · soldi 1,5 · rischi 0,5.

**Cosa la porta a 7,5:** l'iscrizione a Stay22 attiva, e almeno 50 visite a settimana sulle prime 10 città entro 30 giorni.

---

## 3. Le altre idee (sotto 6)

| # | Idea | Prove (5/11/2026) | Voto |
|---|---|---|---|
| 3 | **Promossi all'esame da agente immobiliare per scuola** | Domanda: us "real estate exam pass rate" 10 (*by state, california, florida, texas, first time, nj*), "real estate school pass rates" 10 (*nc, allied, highest pass rate*), "best real estate school in texas" 10 (*houston, dallas, austin*). Fonti ufficiali sparse: Alabama AREC mensile (riportato dai Realtors), Nebraska PDF per scuola, North Carolina (vecchio); TREC (percorsi provati) 404. Pagatori: Aceable su CJ (10 %, 20 % o 25 $ secondo tre elenchi di terzi; la pagina ufficiale non dà cifre); The CE Shop e Colibri senza cifre trovate. Google: scuole e siti di recensioni (testprepinsight, Fortune). Poche fonti per scuola e prima pagina commerciale | RISERVA (5) |
| 4 | **CELPIP, IELTS General e PTE Core per città** (test obbligatori per la residenza permanente e la cittadinanza canadesi) | Domanda: ca "celpip test dates" 10 (*edmonton, toronto, punjab, nigeria, pakistan, lagos, ghana*), "celpip test centre" 10, "ielts test dates" 10. Fonti: `celpip.ca` **403** (tutte le pagine), `paragontesting.ca` 403, `ielts.ca` 403, `tefcanada.ca` 000; aperti `ielts.idp.com/canada/test-dates` 200 (898 KB) e `pearsonpte.com/pte-core` 200. Il test più cercato (CELPIP) è chiuso. Stesso verdetto di TEF/TCF del 30/10 | RISERVA (5) |
| 5 | **Licenza di matrimonio per contea (USA) o provincia (Canada)**: costo, attesa, sconto per il corso prematrimoniale, sovrapprezzo per i non residenti (Texas: +100 $ dal Local Gov't Code §118.018) | Domanda enorme: us "how much is a marriage license in" 10 Stati, "marriage license cost" 10, "how to get a marriage license in" 10, ca "marriage licence" 10, "marriage licence ontario" 10. Ma Google ha già `marriagelicensebystate.pages.dev` (per Stato: costi, attese, requisiti), `civillywedd.pages.dev` (per città), recordinglaw, latestcost. Le fonti sono 3.000 cancellerie di contea (filtro duro). HitchSwitch paga 10-15 % sul cambio di cognome (studio del 31/10) | NO (4,5) |
| 6 | **Food handler card e licenza per servire alcolici** (CA, TX, IL, WA, OR, AZ, NV, NM, UT; Smart Serve ON, Serving It Right BC, ProServe AB) | Domanda forte: us "food handlers card" 10 Stati e città, "tabc certification" 10, "rbs certification" 10, "bartender license" 10; ca "food handler certificate" 10 province, "smart serve" 10, "serving it right" 10, "proserve" 10. Google per "food handlers card washington": blog di Toast e Otter, NEXT Insurance e molto spam, cioè un buco vero. Ma: fonti aperte solo WA DOH 200 e IDPH Illinois 200; DSHS Texas, TABC, AGCO, go2hr, AGLC 404 (percorsi cambiati); ABC California e directory ANAB 403. Corsi da 7-15 $; programmi di 360training ed eFoodHandlers non trovati (404); ACE Food Handler ha un programma senza cifra. Pubblico giovane che vale poco. "ServSafe near me" era già NO (20/10) | NO (4,5) |
| 7 | **Tetto settimanale dei workers' comp per Stato (USA) e massimale assicurabile WCB per provincia (Canada)** | Domanda: us "workers comp max weekly benefit" 7, "max workers comp benefit" 7 (*ny, texas*); ca "wcb max insurable earnings" 10 (*2026, by province, bc*), "wsib max" 7. Annunci di studi legali, cioè AdSense caro. Fonti non provate: 50 enti statali e 12 WCB. Non approfondita: da riprendere solo se un'altra sezione "lavoro" ne ha bisogno | RISERVA debole (5) |

---

## 4. Cosa fare (zero spese, nessuna ora di Massimiliano)

1. **Visa Income, `/h1b-wage-level/`** (voto 7), da pubblicare **entro metà gennaio 2027**, prima della registrazione di marzo:
   - script che scarica lo zip OFLC e fa il join di `ALC_Export.csv`, `Geography.csv` e `oes_soc_occs.csv`;
   - pagine per 40 occupazioni × 60 aree, più il calcolatore;
   - controllo del Federal Register per la regola e per la tassa sulle petizioni.
2. **Tourist Tax, modulo USA e Canada** (voto 6,5):
   - prima Florida e Texas dai file ufficiali, poi le 15 città più cercate scritte a mano;
   - l'iscrizione a Stay22 resta il passo che vale di più su tutto il sito.
3. Niente sulle idee 3-7 finché non cambia una fonte o un pagatore.

---

## 5. Fonti lette il 5/11/2026 (stato HTTP dal server)

| Fonte | Stato |
|---|---|
| `flag.dol.gov/wage-data/wage-data-downloads` | 200 |
| `flag.dol.gov/sites/default/files/wages/OFLC_Wages_2026-27.zip` | 200 (12,6 MB; ALC_Export.csv 449.441 righe) |
| `federalregister.gov/api/v1/documents.json` (H-1B weighted selection) | 200 |
| `floridarevenue.com/Forms_library/current/dr15tdt.pdf` | 200 (R. 10/26) |
| `floridarevenue.com/taxes/taxesfees/Pages/local_option.aspx` | 200 |
| `comptroller.texas.gov/taxes/hotel/`, `/transparency/local/hotel-reporting/` | 200 |
| `data.texas.gov/resource/er34-v24h.json` | 200 |
| `nyc.gov/site/finance/business/business-hotel-room-occupancy-tax.page` | 200 |
| `chicago.gov/.../hotel_accommodationstax.html` | 200 |
| `toronto.ca/.../municipal-accommodation-tax/` | 200 (JavaScript) |
| `tax.nv.gov` | 200 |
| `vancouver.ca`, `revenuquebec.ca` | 403 |
| `tax.hawaii.gov/geninfo/a5_3txcolact_tat/`, `dor.wa.gov/.../lodging-tax-rates`, `www2.gov.bc.ca/.../mrdt` | 404 |
| `cdtfa.ca.gov` | 200 |
| `doh.wa.gov/.../food-worker-card` | 200 |
| `dph.illinois.gov/.../food-handler-training.html` | 200 |
| `dshs.texas.gov` (2 percorsi), `tabc.texas.gov/.../seller-server-training/`, `agco.ca/.../smart-serve`, `go2hr.ca/serving-it-right`, `aglc.ca/.../proserve` | 404 |
| `abc.ca.gov/education/rbs/`, `anabpd.ansi.org` | 403 |
| `foodworkercard.wa.gov` | 000 |
| `360training.com/affiliates`, `statefoodsafety.com/affiliates`, `efoodhandlers.com/affiliate`, `premierfoodsafety.com/affiliate-program` | 404 |
| `celpip.ca` (3 percorsi), `paragontesting.ca`, `ielts.ca` | 403 |
| `tefcanada.ca` | 000 |
| `ielts.idp.com/canada/test-dates` | 200 |
| `pearsonpte.com/pte-core/` | 200 |
| `e2language.com/affiliates` | 404 |
| `trec.texas.gov` (2 percorsi sui promossi) | 404 |

Concorrenti visti con la ricerca web:
- tassa sugli alberghi: `roommaster.com/hotel-tax/chicago`, `taxo-com.pages.dev`, `engine.com/business-travel-guide/hotel-tax-calculator`, `19pine.ai/tools/occupancy-tax-calculator`, `str-tax-lookup.pages.dev`;
- licenza di matrimonio: `marriagelicensebystate.pages.dev`, `civillywedd.pages.dev`;
- H-1B: `lawfully.com/data/h1b-lottery-simulator`;
- Aceable: `partnerships.aceable.com/affiliate`.
