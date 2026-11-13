# Fronte nuovo: spese delle famiglie USA che cambiano nell'inverno 2026-27 — energia (gasolio da riscaldamento e propano) e cibo (additivi vietati dal 2027) (13/11/2026 sera)

Settori di partenza: **energia per il riscaldamento** e **cibo/etichette**, lontani da viaggi, visti, cittadinanza, esami, casa per stranieri, assicurazioni ed eSIM. Mai toccati prima: "heating oil", "propane", "kerosene", "red 40", "dye", "additivi" danno 0 righe in ESPLORATE.md. Solo ricerca: nessun sito modificato.

## In breve

- **Il dato che emerge davvero: il gasolio da riscaldamento USA costa il 59 % in più di un anno fa.** Media nazionale EIA (prezzo al consumo, senza tasse): 3,721 $/gallone il 10/11/2025, **5,915 $ il 9/11/2026**; salto partito a marzo 2026 (4,27 → 5,57 $ in quattro settimane). Propano +15 % (2,448 → 2,826 $). Lo strumento dei volumi dà medie a 12 mesi, quindi sottostima questo inverno.
- **Idea 1 (la migliore): prezzi ufficiali settimanali del gasolio da riscaldamento (22 Stati) e del propano (38 Stati), con storico dal 1990, confronto con l'anno scorso e costo del pieno della cisterna.** Circa 86.600 ricerche al mese misurate, 3,3-8,5 $ a clic sulle frasi per Stato. Centrale a 36 mesi **1.000 €/anno**, 18 ore come sezione del calcolatore dell'inflazione (55 €/ora). Voto 5,5. **IN CODA come sezione**, da mettere online entro dicembre per prendere l'inverno.
- **Idea 2: additivi vietati o con avviso in etichetta dal 2027** (FDA: Red 3 fuori dai cibi dal 15/1/2027; California AB 418: Red 3, bromato di potassio, BVO e propilparaben dal 1/1/2027; Texas SB 25: avviso su 44 ingredienti per le etichette nuove dal 1/1/2027). Domanda grande (circa 570.000 al mese, "red 40" 165.000) ma clic quasi a zero (0-1,7 $), coda per prodotto minima (17 prodotti = 3.100) e risposte immediate di Google. Centrale 600 €/anno, 17 €/ora, voto 3,5. **NO come sito.**
- Nessuna idea arriva a 8 né a 5.000 €/anno centrali: **nessuna «DA VERIFICARE»**.
- Strumento dei volumi: circa 400 ricerche su 20 famiglie di semi (tabella in fondo), nessun errore.

## 1. Come ho cercato

- Volumi: strumento indicato in `BRIEF-RICERCA.md` (Paese per Paese, medie a 12 mesi). "Misurata" = somma delle frasi lette, contando una volta i gruppi con lo stesso numero (es. "heating oil prices" e "home heating oil prices" = 27.100 una volta sola).
- Crescita: per un tema nuovo il volume medio non basta, quindi ho letto la serie ufficiale (EIA settimanale dal 1990) e il completamento automatico di Google USA.
- Formula: ricerche al mese × 12 × quota × 1,3 pagine a visita × incasso per 1.000 pagine × 0,92 ($/€). Incasso per 1.000 pagine scelto dentro la forbice di taratura (13-31 $) in base al costo per clic letto. A 12 mesi circa un terzo del centrale.
- Concorrenti: letti con curl (solo la pagina principale dove indicato). Bloccati e non aggirati: cspi.org (verifica anti-robot), ewg.org 403, maine.gov 403, nyserda.ny.gov 403, leginfo.legislature.ca.gov 403, liheapch.acf.gov (nessuna connessione), acf.hhs.gov 202, motore di ricerca DuckDuckGo 202.

## 2. Idea 1 — Gasolio da riscaldamento e propano: prezzi ufficiali per Stato (USA)

**Dato ufficiale (scaricato, 200):** EIA, "Weekly Heating Oil and Propane Prices" (State Heating Oil and Propane Program): tabella HTML `pet_pri_wfr_a_EPD2F_prs_dpgal_w.htm` (gasolio, 22 Stati: CT, ME, MA, NH, RI, VT, DE, MD, NJ, NY, PA, NC, VA, IL, IN, IA, KY, MI, MN, NE, OH, WI), `..._EPLLPA_...` (propano, 38 Stati), file XLS con lo storico (431 KB), pagine della serie dal 1990. Dominio pubblico. Aggiornamento ogni settimana da ottobre a marzo. Esempio: Connecticut 6,015 → 5,667 $ tra il 5/10 e il 9/11/2026; Massachusetts 6,137 → 5,962 $.

**Domanda misurata (USA, al mese):**

| Gruppo | Frasi e volumi | Totale |
|---|---|---|
| Teste | "heating oil prices" 27.100 a 4,72 $; "propane cost/price per gallon" 14.800 a 4,76-5,36 $; "propane prices" 12.100 a 4,98 $; "heating oil delivery" 2.900 a 10,80 $; "kerosene prices" 2.400; "heating oil price per gallon" 1.300 | 60.600 |
| Gasolio per Stato | CT 3.600, MA 2.900 (6,13 $), ME 1.900 (5,80 $), RI 1.900, Long Island 1.600, NJ 1.000, NH 1.000 (5,57 $), NY 880, PA 880, VT 320, MD 20 | 16.000 |
| Gasolio per città | Westchester 590, Worcester 210, Bangor 170, Cape Cod 110, Hartford 70 | 1.150 |
| Propano per Stato | ME 1.600 (8,32 $), MI 1.000 (8,51 $), NH 1.000, WI 880, MN 720, PA 480, OH 480, IA 390 (7,62 $), NC 260, VT 260, NY 210, TX 210 | 7.490 |
| Altro | "heating assistance" 720, "… ct" 390, previsioni 160, "cost to fill oil tank" 90 (16 $) | 1.360 |
| **Totale misurato** | | **86.600** |
| Non contato nel centrale | LIHEAP (aiuto pubblico per le bollette): "liheap" 74.000, "liheap application" 27.100, "liheap pa" 4.400, "heap ny" 1.900 (0,9-3,1 $) | 107.400 |

Usata nel centrale: 100.000 (aggiunti 26 Stati del propano non misurati, ~250 l'uno). Il LIHEAP resta solo nell'ottimista: i dati federali per Stato (liheapch.acf.gov) non si leggono dal server.

**Concorrenti (5 esempi, 4 siti letti):**

| Ricerca | Chi risponde | Cosa manca |
|---|---|---|
| heating oil prices ct (3.600) | NewEnglandOil.com (prezzi dei fornitori per paese, 5 Stati del New England, «© 2019»); HeatFleet (mercato con preventivo per CAP e pagine per città); CheapestOil (11 Stati + cherosene, ricerca per CAP) | nessuno mostra la media ufficiale, lo storico o il +59 % sull'anno |
| propane prices maine (1.600) | indagine ufficiale del Maine (403 dal server); FuelWonk (solo modulo per i preventivi, nessun prezzo in pagina) | prezzo in pagina, confronto tra Stati |
| price of propane per gallon (14.800) | tabella EIA (poco leggibile, pagina vecchio stile); FuelWonk senza cifre; HeatFleet solo gasolio | propano per i 38 Stati, una pagina ciascuno |
| heating oil prices long island (1.600) | HeatFleet e fornitori locali (non letti) | – |
| propane prices michigan (1.000) | non letti (commissione statale del Michigan e fornitori) | – |

Vuoto: **medio**. I siti dei fornitori danno il prezzo del giorno vicino a casa (quello che cerca chi deve ordinare), noi daremmo solo la media dello Stato. In cambio nessuno ha propano Stato per Stato, storico, confronto con l'anno scorso, costo del pieno (100/150/275 galloni) e "conviene bloccare il prezzo?" con i numeri ufficiali.

**Chi paga:** solo AdSense. Costo per clic letto: 3,3-8,5 $ sulle frasi per Stato, 10,80 $ su "heating oil delivery". Nessun programma di affiliazione pubblico trovato: le pagine di HeatFleet e FuelWonk non nominano "affiliate" o "partner". Libro KDP: no.

**Stima (€/anno):**

| | Quota | Incasso per 1.000 pagine | 12 mesi | 36 mesi |
|---|---|---|---|---|
| Prudente | 1 % | 15 $ | 70 | 200 |
| Centrale | 3 % | 24 $ | 330 | **1.000** |
| Ottimista | 6 % + LIHEAP 3 %, domanda ×1,3 per il prezzo alto | 30 $ | 1.300 | 4.000 |

Calcolo centrale: 100.000 × 3 % = 3.000 visite × 1,3 = 3.900 pagine × 24 $ = 94 $/mese ≈ 1.030 €/anno. Rischi: il primo inverno è in gran parte perso (indicizzazione lenta); se il prezzo torna a 3,7 $ la domanda scende verso la media; stagione di 6 mesi.

**Ore:** 18 come sezione del calcolatore dell'inflazione (lettura dell'XLS/HTML EIA, 60 pagine Stato × combustibile + pagina nazionale, grafico dello storico, calcolatore del pieno, aggiornamento automatico settimanale da ottobre a marzo); 25 come sito nuovo (+ dominio e AdSense di Massimiliano). Manutenzione 5 ore l'anno. **€/ora: 55 (sezione), 40 (sito nuovo).** Zero-click: medio (Google risponde con la media nazionale, meno con quella dello Stato).

**Voto severo: 5,5.** Verdetto: **IN CODA come sezione del sito dell'inflazione** (stesso tema: prezzi ufficiali USA), prima pagina online entro metà dicembre. Prova: 10 Stati del gasolio + 10 del propano; si allarga a 60 pagine se a fine febbraio prendono impressioni.

## 3. Idea 2 — Additivi vietati o con avviso in etichetta dal 2027 (USA)

**Obblighi nuovi con data (fonti):**
- FDA, pagina "FD&C Red No. 3" (200): ordine del 16/1/2025; i produttori hanno tempo fino al **15/1/2027** per i cibi e al 18/1/2028 per i farmaci da ingerire.
- Texas SB 25 (testo approvato, capitol.texas.gov, 200): avviso obbligatorio "WARNING: This product contains an ingredient that is not recommended for human consumption by the appropriate authority in Australia, Canada, the European Union, or the United Kingdom" per **44 ingredienti** (tra cui red 3, red 40, yellow 5, yellow 6, titanium dioxide, potassium bromate, propylparaben); vale per le etichette create dal **1/1/2027**. Controllare lo stato di eventuali ricorsi prima di scrivere.
- California AB 418: Red 3, bromato di potassio, olio vegetale bromurato e propilparaben vietati dal **1/1/2027** (testo ufficiale 403 dal server; data confermata da Wikipedia "Erythrosine").
- Prodotti: USDA FoodData Central, cibi di marca CSV del 29/10/2026 (452 MB, 200, dominio pubblico) con l'elenco ingredienti; Open Food Facts (API 200, licenza ODbL) conta già **5.856 prodotti USA con E127 (Red 3)**.

**Domanda misurata (USA):** "red 40" 165.000 a 0,48 $; "red dye 3" 60.500 a 0,04 $; "red dye 40" 60.500; "titanium dioxide" 49.500 (soprattutto cosmetici); "blue 1" 33.100; "red 3" 22.200; "natural food coloring" 22.200; "foods with red dye 3" 18.100 a 0,03 $; "yellow 5" 18.100; "food dye ban" 14.800 a 2,46 $; "food dyes" 14.800; "potassium bromate" 9.900 (17,7 $, isolato); "is red 40 banned" 8.100; "dye free candy" 8.100; "dye free sprinkles" 6.600; "brominated vegetable oil" 5.400; "propylparaben" 4.400; "texas sb 25" 880; "texas food warning label" 0; "california food ban 2027" 0. Coda per prodotto: 17 prodotti misurati 3.100 in tutto (gatorade 720 + 390, cheetos 590, takis 390, doritos 320, hot cheetos 320; skittles 170; m&ms, pop tarts, trix, jello 0). Altri Paesi: "red 40" GB 12.100, CA 12.100, AU 6.600, a 0-0,11 $. Totale circa 570.000 al mese, clic pesato circa 0,6 $.

Completamento automatico: "red dye 3 ban effective date", "food dye ban 2027", "brands removing artificial dyes", "dye free m&ms / skittles / gatorade", "list of foods with red dye 40 australia / canada / uk".

**Concorrenti:** Healthline "Red Dye 40" (modificata il 22/8/2024: zero menzioni di 2027, Texas, California, impegni delle aziende); Open Food Facts (pagina per prodotto e per additivo, 5.856 prodotti con Red 3); CSPI ed EWG (bloccati). Vuoto: un solo posto con le scadenze 2027, i 44 ingredienti del Texas e gli impegni dei marchi. Ma la domanda di quel vuoto è piccola ("texas sb 25" 880, "brands removing dyes" 0).

**Chi paga:** AdSense con clic a 0-1,7 $; iHerb "fino al 25 %" sulle vendite (letto sulla pagina affiliati; vende coloranti naturali e caramelle senza coloranti); Thrive Market senza cifra in pagina; Amazon (tabella non leggibile dal server). Ordine medio basso: pochi euro a vendita.

**Stima a 36 mesi:** 200 / 600 / 3.000 €/anno (quota 0,3 / 0,8 / 2,5 % sulle teste, 2-3 % sulla coda; 9-15 $ ogni 1.000 pagine); a 12 mesi 70 / 200 / 1.000. Interesse che scende dopo il 2027, quando i coloranti spariscono dagli scaffali. 35 ore → **17 €/ora**. Zero-click alto. **Voto 3,5. NO come sito**; al massimo una pagina se un giorno nasce un sito su cibo e salute.

## 4. Semi misurati e scartati (tutti mai toccati prima)

| Seme | Volumi letti | Perché no |
|---|---|---|
| Auto elettrica in salary sacrifice e tassa sull'auto aziendale per modello (GB) | "salary sacrifice car" 12.100 a 4,46 £, "company car tax calculator" 12.100, "electric car lease" 14.800 a 3,25 £; per modello 0-110 ("tesla model 3 bik" 40) | nessuna coda per modello; calcolatori di Octopus EV, Tusker, Parkers |
| Employment Rights Act, fasi 2026-27 (GB) | "statutory sick pay" 90.500 a 3,19 £, "statutory maternity pay" 60.500, "statutory redundancy pay" 22.200, "employment rights bill" 14.800 a 5,27 £, "martyn's law" 12.100 | teste di GOV.UK e ACAS con calcolatori ufficiali, nessuna coda per entità |
| Spedizioni USA/GB (USPS, UPS, Royal Mail) | "usps shipping calculator" 90.500 a 0,71 $, "ups shipping rates" 74.000, "usps ground advantage" 60.500, "how much is a stamp" 40.500 | navigazione verso i corrieri e Pirate Ship; non in crescita |
| No tax on overtime (USA) | 246.000 di media a 0,42 $ (domande del 2025 "when does it start"), "overtime tax calculator" 6.600 a 14 $ | stesso motivo del NO "no tax on tips": regola unica, calcolatori dei grandi |
| Premium Bonds (GB) | 368.000 a 4,56 £, ma "checker" 165.000 è navigazione verso NS&I; "winners" 49.500 a 0,33 £ | domanda di navigazione |
| Child Trust Fund (GB) | 74.000 a 2,53 £ | strumento HMRC, non in crescita |
| Pickleball | "pickleball paddle" 246.000 a 1,6 $; elenchi delle racchette omologate 70-880 | Pickleheads e PickleballEffect con banche dati per racchetta |
| SPID a pagamento (IT) | "spid a pagamento" 14.800 a 3,58 €; "spid aruba", "spid infocert" 33.100 = accesso; "quale spid scegliere" 90 | navigazione, nessun pagatore |
| AI Act, obbligo di formazione (DE, IT) | "eu ai act" 8.100, "ki verordnung" 5.400, "ki schulung pflicht" 320 | domanda piccola |
| Fine del supporto di Windows 10 e dei telefoni | "windows 10 end of life" 49.500 a 15,7 $ (picco 2025), "windows 11 compatible cpu" 1.000, per telefono 0-90 | picco passato, nessuna coda |
| Obbligo di lavoro per Medicaid dal 2027 (USA) | "medicaid work requirements" 12.100 a 11,75 $; per Stato 0 | nessuna coda |
| Targa e assicurazione del monopattino (IT) | 9.900 + 6.600 a 0,07-0,8 € | piccola, nessun pagatore letto |
| Tariffe elettriche per azienda (USA) | 300-3.600 per azienda a 2-12 $; "electricity providers" 12.100 a 29,6 $ | vicino al Price to Compare già bocciato (pagatore EPC 0,09 $) |
| Class action aperte (USA) | "class action settlements" 33.100 a 1,86 $ | TopClassActions, ClaimDepot |
| Robot tosaerba | 60.500 a 1,1 $ | non approfondito (recensioni di prodotto) |

## 5. Lezione

L'«emergente» vero l'ha mostrato la serie ufficiale (EIA, +59 % in un anno), non lo strumento dei volumi, che fa la media su 12 mesi. Per i prossimi fronti conviene partire dalle serie di prezzi ufficiali che hanno appena fatto un salto (energia, cibo, tariffe) e poi misurare le frasi per Stato o per entità.
