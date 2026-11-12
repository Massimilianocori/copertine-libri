# Riesame delle idee scartate per la concorrenza (12/11/2026 sera)

Regola nuova del proprietario (12/11 sera, `REGOLE-FISSE.md`): la concorrenza non scarta più un'idea. Al posto della prova "nessuno fa meglio" si stima **quota × domanda × resa per mille visite**. Restano bloccanti solo: dati non leggibili o non riusabili, nessuna domanda, rischio legale.

Qui sono rifatte con quel metodo le dieci idee che erano state scartate o limitate soprattutto perché "c'è già un concorrente" o "manca il vuoto dimostrato".

## 0. Risposta in breve

1. **Nessuna delle dieci diventa un'idea grande.** La migliore vale circa 750 €/anno centrali a 18 mesi (1.500 a 36). Tutte hanno euro attesi positivi, ma pochi.
2. **Due si possono costruire, in coda, non in testa:** il sito inglese sugli impianti di casa nel Regno Unito (pompe di calore per council + costo del solare per regione e città; circa 19 € centrali per ora di lavoro) e la sezione "date dei sorteggi delle gare" di Before You Fly allargata alle 8 Major (circa 13 € per ora).
3. **Le altre otto restano NO**, ma ora per un motivo diverso: non "c'è un concorrente", bensì "con una quota realistica rendono meno di 10 € per ora di lavoro", e tre hanno anche un blocco di dati o di legge (Germania, fertilità, Filippine).
4. **Perché i numeri non sono saliti.** Le stime vecchie contenevano già una quota (2-10 %): la regola nuova toglie il tetto al voto, non aggiunge visite. In più oggi per la prima volta ho letto i **volumi di ricerca veri** (sezione 1), e in quattro casi su dieci sono più bassi di quanto faceva pensare l'autocomplete. Esempio: in Germania le ricerche su date e iscrizione all'Einbürgerungstest sono circa 12.000 al mese nelle frasi principali, non centinaia di migliaia.
5. **Il ritrovamento utile è la fonte dei volumi.** Una fonte pubblica dà volume mensile e costo per clic di Google Ads per 50 Paesi, 20 ricerche gratis al giorno senza account. Da oggi ogni stima può partire da un numero letto invece che dal conteggio dei suggerimenti.
6. Per confronto: le idee già in riserva che **non** erano bloccate dalla concorrenza rendono di più per ora secondo le loro stesse stime (Price to Compare USA circa 74 €/ora, matrimonio in Italia circa 44). Se si costruisce qualcosa per prima, conviene partire da lì e rifare anche quelle con i volumi veri.

## 1. Fonte nuova: volumi di ricerca veri

`seodata.dev` (API `api.seodata.dev/v1/keyword?q=…&country=xx`, letta oggi, 200). Dichiara: medie mensili dall'API di Google Ads, gli stessi numeri di Google Ads. `robots.txt` senza divieti. Limite: 20 ricerche al giorno senza account (finite oggi), 500 al mese con un indirizzo email, senza limiti a 4,99 $ al mese. Ho mandato solo parole chiave generiche, nessun dato nostro.

Avvertenze: è una fonte terza, non Google. Dove risponde 0 il dato manca, non vuol dire "nessuna ricerca" (succede per le frasi con il mese o l'anno). Le varianti vicine hanno lo stesso numero perché Google le raggruppa: le ho contate una volta sola.

| Paese | Ricerca | Al mese | Costo per clic |
|---|---|---|---|
| DE | einbürgerungstest (quasi tutta ricerca di quiz) | 60.500 | 0,17 |
| DE | einbürgerungstest online | 8.100 | 0,16 |
| DE | einbürgerungstest termin / termine / termine in der nähe | 4.400 / 1.900 / 1.300 | 0,21-1,11 |
| DE | einbürgerungstest vhs / anmeldung / online termin | 1.600 / 880 / 590 | 0,31-0,94 |
| DE | b1 prüfung termin(e) / telc b1 prüfung termine | 2.400 / 1.300 | 0,88-1,49 |
| DE | dtz prüfung / dtz prüfung b1 | 4.400 / 5.400 | 0,77-1,45 |
| ES | examen ccse / instituto cervantes examen ccse | 2.400 / 1.600 | 0,70-0,80 |
| ES | instituto cervantes nacionalidad / … examen nacionalidad | 3.600 / 1.000 | 0,89-1,00 |
| US | deck permit / fence permit / shed permit / roof permit | 3.600 / 2.900 / 1.300 / 720 | 29,05 / 4,81 / 5,07 / 9,95 |
| US | do i need a permit to build a shed / fence / deck | 1.300 / 880 / 590 | 2,36-7,04 |
| US | water heater permit / building permit cost / how long does it take to get a building permit | 480 / 1.300 / 590 | 15,39 / 3,49 / 15,93 |
| US | adu cost | 2.400 | 5,68 |
| US | ivf success rates / does insurance cover ivf | 6.600 / 8.100 | 4,57 / 9,12 |
| GB | ivf success rates | 2.900 | 3,24 |
| US | nyc marathon lottery / registration / application | 9.900 / 3.600 / 1.300 | 8,99 / 14,16 / 28,79 |
| US | trademark cost / trademark registration cost | 3.600 / 4.400 | 10,12 / 16,74 |
| GB | solar panels cost / cost of solar panels uk / solar pv panels prices | 9.900 / 6.600 / 5.400 | 10,24-13,88 |
| GB | heat pump grant / air source heat pump grant / government grants for heat pumps | 5.400 / 2.900 / 1.600 | 11,42-14,32 |
| US | 1 euro houses / 1 euro houses italy | 12.100 / 6.600 | 0,05-0,22 |
| US | buy a home in italy / buying house in italy / buy property in italy | 1.900 / 1.600 / 1.300 | 0,39-2,04 |
| PH | manila minimum wage / minimum wage philippines / minimum wage metro manila | 49.500 / 33.100 / 14.800 | 0-1,28 |

Non letti (risposta 0 o limite finito): london marathon ballot (GB), resultados ccse, dele a2, einbürgerungstest ergebnis, madrid protocol fees, tablas salariales convenio. Da rileggere domani.

Altro fatto nuovo letto oggi: Destatis conta **467.400 domande di naturalizzazione** registrate in Germania nel 2025 (332.500 concluse).

## 2. Metodo

- **Domanda** = somma delle frasi principali lette (sezione 1) × un moltiplicatore per la coda lunga (città, Stato, anno). Il moltiplicatore è una mia ipotesi, scritta in ogni nota: da 2 (domanda concentrata) a 7 (domanda locale sparsa su migliaia di luoghi). È il punto più debole del conto.
- **Quota** = parte di tutte le ricerche del gruppo che arriva a noi come visita. Tiene conto del fatto che il sito ufficiale e le risposte dirette di Google prendono già più di metà dei clic. Concorrenti forti e autorevoli: 0,2-1 % sulle frasi principali, 1-5 % sulla coda lunga. Concorrenti deboli o giovani: 3-12 %.
- **Resa per 1.000 visite** dalle cifre vere degli annunci di siti in vendita (`fronti-2026-11-12-siti-in-vendita.md`: sola pubblicità 33 $ ogni 1.000 visitatori di mediana, ma con reti di fascia alta e pubblico USA; pubblicità + affiliazioni 52 $; pubblico non inglese 2-5 $) e dal costo per clic letto. Per un sito nostro con AdSense uso: USA e Regno Unito casa/legale 25-55 €, sport e viaggi 12 €, Germania 9 €, Spagna 4,5 €, Filippine 1 €.
- **36 mesi** = 18 mesi × circa 2 se il sito resta aggiornato (l'autorità cresce), × 1,8 dove la domanda è stagionale.
- **Voto nuovo**: dipende dagli euro attesi per ora e dai blocchi rimasti, senza il tetto a 5.
- **Costruire** = euro attesi positivi, dati leggibili, nessun rischio legale **e** almeno circa 12 € centrali per ora a 18 mesi. Sotto quella soglia il lavoro rende di più altrove (la coda attuale parte da 15 €/ora).

## 3. Classifica (per € centrali all'anno per ora di agente, a 18 mesi)

| # | Idea | Domanda stimata (ricerche/anno) | Quota prud. / centr. / ott. | Resa € per 1.000 visite | € anno a 18 mesi (prud. / centr. / ott.) | € anno a 36 mesi (prud. / centr. / ott.) | Ore agenti | € centrali per ora (18 → 36 mesi) | Voto nuovo (prima) | Esito |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Impianti di casa nel Regno Unito**: pompe di calore con il contributo per council + costo del solare per regione e città (un solo sito) | 1,14 milioni (solare 720.000 + pompe di calore 420.000) | 0,3 / 1,2 / 4 % | 25 / 52 / 115 | 85 / 750 / 5.400 | 150 / 1.500 / 9.000 | 40 | **19 → 37** | 5,5 (solare 4, pompe 5,5) | **COSTRUIRE in coda**, con due azioni del proprietario |
| 2 | **Date dei sorteggi delle gare**: sezione di Before You Fly, le 8 Major + 40-60 gare oltre le Major | 1,7 milioni (Major 1,2 + altre 0,5) | 0,6 / 1,9 / 6 % | 6 / 12 / 20 | 70 / 400 / 2.000 | 120 / 750 / 3.500 | 31 | **13 → 24** | 5,5 (hub Major 3,5; oltre le Major 5,5) | **COSTRUIRE in coda** |
| 3 | Tasse dei marchi per Paese e classe, con calcolatore | 300.000 nei mercati che pagano + 300.000 altrove | 0,5 / 2,5 / 8 % | 20 / 50 / 110 | 35 / 400 / 2.700 | 70 / 800 / 5.000 | 42 | 9,5 → 19 | 5 (5,5) | NO per ora |
| 4 | Permessi per i lavori di casa negli USA (Stato × lavoro + tempi dai dati aperti di 20 città) | 1,56 milioni | 0,3 / 1,2 / 4 % | 12 / 30 / 70 | 55 / 560 / 4.400 | 110 / 1.100 / 7.000 | 70 | 8 → 16 | 4,5 (3-4,5) | NO per ora |
| 5 | Spagna: CCSE + DELE A2 (date, citas, prezzi, "quando escono i risultati") | 1,2 milioni | 1,5 / 5 / 12 % | 2,5 / 4,5 / 8 | 45 / 270 / 1.150 | 90 / 550 / 2.000 | 35 | 7,7 → 16 | 5 (5,5) | NO |
| 6 | Spagna: tabelle salariali dei convenios | 4,8 milioni (non letta, ipotesi) | 0,5 / 3 / 10 % | 3 / 4 / 6 | 70 / 600 / 2.900 | 150 / 1.200 / 5.800 | 90 | 6,7 → 13 | 4,5 (NO) | NO, si riguarda quando Paga CCNL ha visite |
| 7 | Germania: Einbürgerungstest + DTZ/B1 per città | 540.000 | 1,5 / 5 / 12 % | 5 / 9 / 14 | 40 / 245 / 900 | 80 / 500 / 1.800 | 40 | 6 → 12 | 4,5 (4,5) | NO (anche dubbio legale sui dati) |
| 8 | Comprare casa in Italia da stranieri, per nazionalità, con calcolatore dei costi | 240.000 | 0,5 / 2 / 6 % | 8 / 20 / 45 | 10 / 100 / 650 | 20 / 200 / 1.200 | 17 | 5,9 → 12 | 4 (4,5) | NO da sola; 3-4 pagine dentro la sezione case a 1 euro |
| 9 | Percentuali di successo delle cliniche di fertilità (Regno Unito, USA) | 1,5 milioni | 0,3 / 1 / 4 % | 5 / 9 / 16 | 20 / 135 / 960 | 40 / 250 / 1.700 | 30 | 4,5 → 8 | 3,5 (3) | NO (dati a metà) |
| 10 | Filippine: salario minimo per città | 3 milioni | 0,5 / 2 / 6 % | 0,6 / 1 / 1,4 | 10 / 60 / 250 | 20 / 120 / 450 | 15 | 4 → 8 | 3,5 (4,5) | NO |

Warm Homes (prestiti nel Regno Unito): non rifatta, il blocco legale c'è ancora.

Somma delle due da costruire: circa **1.150 €/anno centrali a 18 mesi, 2.250 a 36**, con 71 ore di agenti.

## 4. Note per idea

### 1. Impianti di casa nel Regno Unito (pompe di calore + solare) — COSTRUIRE in coda

- **Cosa cambia.** Il "costo del solare per regione e città" era NO da solo perché ExpertSure e The Eco Experts lo fanno già. Con la regola nuova diventa la metà che porta le visite di un sito il cui pezzo unico sono i numeri per council delle pompe di calore (già riserva costruibile).
- **Domanda letta.** Solare: 9.900 + 6.600 + 5.400 al mese nelle frasi principali, costo per clic 10-14 £. Pompe di calore: 5.400 + 2.900 + 1.600, costo per clic 11-14 £. Con le città ("solar panels leeds" 10 suggerimenti) stimo 60.000 e 35.000 ricerche al mese (moltiplicatore 2,7 e 3,5).
- **Concorrenti e quota.** Molto forti e aggiornati: The Eco Experts (pagina del 19/10/2026), ExpertSure (pagine per città), MoneySavingExpert, Which?, Energy Saving Trust, GOV.UK, Octopus. Sulle frasi principali un dominio nuovo prende quasi niente; la quota viene dalle pagine di città e di council. Solare 0,2 / 0,8 / 3 %; pompe di calore 0,5 / 2 / 6 % (il numero per council non lo ha nessuno).
- **Resa.** Il costo per clic più alto di tutte le dieci idee. Pubblicità 25-35 € per 1.000 visite; Glow Green su Awin paga 300 £ per impianto solare e 250 £ per pompa di calore (cifre lette l'11-12/11), con conversione ipotizzata 0,02-0,1 % delle visite.
- **Dati.** Leggibili e liberi (file DESNZ, licenza OGL): solare in £ per kW per regione, impianti per collegio, contributi per council. Il costo delle pompe di calore per regione non esiste in forma aperta: non si promette.
- **Rischi.** Glow Green può non accettare il sito; AdSense è ancora in revisione sui nostri domini; pagine di città con lo stesso numero regionale (modello ripetuto). Nessun rischio legale: si parla di impianti, mai di prestiti.
- **Serve dal proprietario:** un dominio (circa 10 €, spesa da approvare) e la domanda a Glow Green e BOXT dentro Awin.

### 2. Date dei sorteggi delle gare (Before You Fly) — COSTRUIRE in coda

- **Cosa cambia.** L'hub delle 8 Major era NO (3,5) perché marathonballot.com lo fa già. Ora entra nella stessa sezione delle 40-60 gare oltre le Major (già in coda bassa).
- **Domanda letta.** New York: 9.900 + 3.600 + 1.300 al mese negli USA, costo per clic 9-29 $ (pagano agenzie di viaggio e pettorali di beneficenza). Londra non letta (1.338.544 domande al sorteggio, dato ufficiale). Stimo 100.000 ricerche al mese per le Major in inglese e 40.000 per le altre gare.
- **Concorrenti e quota.** Siti ufficiali (prendono la maggior parte dei clic), marathonballot.com (443 pagine, mappa del sito aggiornata oggi), fatmarathoner, Runner's World. Major 0,5 / 1,5 / 5 %; altre gare 1 / 3 / 8 %.
- **Resa.** 12 € per 1.000 visite: pubblicità più gli hotel del fine settimana di gara con Stay22 (già attivo).
- **Dati.** Pagine ufficiali, circa due terzi leggibili. Stesso motore delle pagine "ticket release dates" e degli .ics.
- **Rischi.** Domanda a picchi; un lettore per gara da ricontrollare una volta l'anno. Nessun rischio legale, nessun dominio nuovo.

### 3. Tasse dei marchi — NO per ora

Domanda letta negli USA: 3.600 + 4.400 al mese, costo per clic 10-17 $. Ma metà della coda lunga ("trademark cost in india / nigeria") viene da Paesi che i pagatori non servono. Concorrenti: USPTO, LegalZoom, Trademark Engine, studi legali sulle frasi principali; iGERENT, IP-Coster, tmarkmetric (346 pagine, aggiornato il 10/11) sulla coda. Trademark Factory paga 100 $ a vendita, ma chi cerca la tassa ufficiale di solito deposita da solo (conversione ipotizzata 0,05 %). La stima vecchia di 1.500 € centrali chiedeva circa il 10 % della domanda che paga: troppo. Si riapre con una commissione letta di un servizio europeo o se la domanda "madrid protocol fees" risulta alta alla prossima lettura.

### 4. Permessi per i lavori di casa negli USA — NO per ora

Frasi principali lette: circa 18.600 ricerche al mese in tutto, costo per clic da 2 a 29 $ ("deck permit" 29 $, "water heater permit" 15 $). Con la coda per città e Stato stimo 130.000 al mese (moltiplicatore 7). I siti dei Comuni prendono la metà dei clic; il resto si divide fra almeno 8 siti automatici (buildpermitguide 659 pagine, aggiornato il 10/11; permitsguide 404) e i blog delle imprese. La versione fatta bene (50 città lette a mano) costa 150-200 ore, cioè 3 € per ora; la versione leggera (50 Stati × 6 lavori dai codici statali + tempi misurati in 20 città con dati aperti) costa 70 ore. È il mercato con la resa più alta dopo il Regno Unito, ma il rischio "pagine a modello" per AdSense è lo stesso che ha fatto respingere un nostro sito. Si riapre se un programma di contatti accetta il sito con una cifra scritta di almeno 20 $ a contatto.

### 5. Spagna, CCSE + DELE A2 — NO

Le frasi lette sono in gran parte ricerche del sito del Cervantes (3.600, 2.400, 1.600 al mese). I candidati sono tanti (230-240.000 CCSE e 80-100.000 DELE A2 l'anno), ma la resa spagnola è bassa (costo per clic 0,7-1 €) e i centri non si possono ripubblicare (diritti riservati del Cervantes: lì il blocco è legale). Anche con il 12 % di quota resta sotto 1.200 €/anno.

### 6. Spagna, tabelle dei convenios — NO per ora

Domanda larghissima all'autocomplete, volume non letto oggi. Due concorrenti completi (1.883 e 1.205 contratti, aggiornati ai bollettini di settembre-ottobre 2026) e circa 50 bollettini provinciali da leggere: 90 ore per i primi 200 contratti. Il nostro sito italiano gemello ha ancora zero visite: prima si prova lì che il modello porta traffico, poi la Spagna è il primo mercato da aprire.

### 7. Germania, Einbürgerungstest + DTZ/B1 — NO

- **Domanda vera più piccola del previsto**: circa 12.400 ricerche al mese sulle frasi di date e iscrizione, circa 5.000 sulle date della B1. Con le città stimo 45.000 al mese. Le 60.500 di "einbürgerungstest" sono ricerche di quiz, mercato pieno di app.
- **Concorrente**: einbuergerungstest-termine.de è vivo ("Zuletzt geprüft: 12.11.2026, 20:30 Uhr", 476 pagine, mappa del sito di oggi). È un dominio di un mese: non ha ancora autorità, quindi una quota del 5 % è possibile. Ma guadagna vendendo l'avviso a 12,90 €, che a noi è vietato dalle regole fisse (niente pagamenti finché i ricavi non coprono i costi). Con sola pubblicità tedesca a basso costo per clic (0,2-1,4 €) il centrale è 245 €/anno.
- **Blocchi rimasti**: le condizioni di riuso del catalogo nazionale delle VHS non sono scritte (serve il permesso: dubbio legale); serve un Impressum con nome e indirizzo (azione del proprietario).
- Si riapre se i pagamenti diventano possibili: lì il mercato vale (un avviso venduto allo 0,5 % delle visite rende più di dieci volte la pubblicità).

### 8. Comprare casa in Italia da stranieri — NO da sola

Negli USA 1.000-1.900 ricerche al mese per frase, costo per clic 0,4-2 $. Dieci guide del 2026 in prima pagina (studi legali, Wise, Expatica). Vale come 3-4 pagine dentro la sezione delle case a 1 euro, quando si costruisce. Nota per quella sezione: "1 euro houses" ha 12.100 ricerche al mese negli USA ma un costo per clic di 0,05-0,22 $, quindi è traffico di curiosità: la pubblicità lì rende pochissimo, come già scritto nella stima.

### 9. Fertilità, percentuali di successo per clinica — NO

Domanda buona (USA 6.600 e 8.100 al mese, Regno Unito 2.900), ma i dati restano a metà: il file americano è fermo al 2022, quello britannico non si legge e non ha una licenza scritta. TreatCompare ha 2.305 pagine aggiornate l'11/11. Pubblicità su tema sensibile, nessun pagatore con cifra. Il pezzo "l'assicurazione copre la FIVET in <Stato>" (8.100 al mese, costo per clic 9 $) da solo vale circa 70 €/anno.

### 10. Filippine, salario minimo — NO

È la domanda più grande di tutte (49.500 + 33.100 + 14.800 al mese solo le frasi principali), ma la pubblicità filippina rende circa 1 € per 1.000 visite: anche con il 6 % di quota sono 250 €/anno. In più la regola filippina sull'uso a fini di lucro degli atti del governo non è stata letta.

## 5. Altre righe di ESPLORATE.md frenate soprattutto dalla concorrenza, con domanda alta

Non rifatte oggi (limite dei volumi finito). In ordine di interesse:

| Riga | Motivo scritto allora | Cosa fare |
|---|---|---|
| ETIAS per nazionalità (righe 151, 390, 644) | "muro di concorrenti", nessuna data | Domanda enorme e sezione passaporti già pronta in Before You Fly: rifare il conto con il volume vero e lo stato della data. Costo basso (8-10 ore) |
| Tassa alberghiera per città negli USA (riga 394) | centinaia di fonti, roommaster.com già automatico | Tourist Tax esiste già: provare le prime 50 città a mano (25-35 ore); leggere prima i volumi di "hotel tax <città>" |
| Visto di transito per aeroporto e nazionalità (riga 1183) | notizie e Atlys rispondono, pubblico di poco valore | Domanda grande, resa bassa: probabilmente resta NO, ma va misurata |
| Assistenza agli anziani: care home fees (GB), assisted living per Stato (US), Pflegegrad (DE), EHPAD (FR) (riga 968) | concorrenti grandi (Age UK, A Place for Mom, pflege.de) | Costo per clic alto e pagatori a contatto: è una ricerca nuova, non un riesame; serve prima una fonte ufficiale leggibile per struttura |
| Liste d'attesa NHS per ospedale (riga 231) | treatcompare.com e lo strumento ufficiale | Resta NO: il file ufficiale non si legge dal server (blocco di dati, non di concorrenza) |
| Piani Medicare Advantage che chiudono nel 2027 (riga 522) | "già coperto" | Resta NO: promozione di piani sanitari regolata negli USA (rischio legale) e finestra quasi chiusa |
| "Il broker X è regolato?" (riga 1245) | ForexBrokers e BrokerChooser | Resta NO: promozione finanziaria regolata |
| Nulla osta al matrimonio, costo del matrimonio civile per comune, calcolo del voto di laurea, fibra per Comune in Germania (righe 1133, 1134, 1266, 1246) | "concorrenti non letti: voto massimo 5" | Il tetto non vale più, ma il freno vero era il pagatore (solo pubblicità italiana) o il dato sparso: non salgono |

Righe in riserva per l'asticella e non per la concorrenza, con € per ora più alti di tutte le dieci di oggi secondo le stime dei loro file: Price to Compare USA (2.600 € centrali, 30-40 ore), pompe di calore UK (1.300, 20-25 ore; qui dentro l'idea 1), matrimonio in Italia (1.530, 30-40 ore). Vanno rifatte con i volumi veri prima di costruirle: le loro stime sono nate senza.

## 6. Cosa propongo

1. Mettere in coda le due idee "COSTRUIRE": prima la sezione delle gare (nessuna dipendenza, sito esistente), poi il sito britannico quando il proprietario ha detto sì al dominio e ha fatto domanda a Glow Green.
2. Da domani usare i volumi veri in ogni ricerca (20 al giorno gratis). Con un indirizzo email del proprietario si sale a 500 al mese gratis; 4,99 $ al mese senza limiti (spesa da approvare).
3. Rifare con i volumi veri le tre riserve del punto 5 e l'ETIAS, che sulla carta rendono più di queste dieci.

## 7. Limiti di questa ricerca

- I volumi sono di una fonte terza e coprono solo le frasi principali; la coda lunga è un moltiplicatore ipotizzato.
- La composizione dei risultati di Google non si legge dal server: le quote sono giudizi sui concorrenti letti (pagine, mappe del sito, date di aggiornamento), non misure.
- Le rese per 1.000 visite sono ipotesi ancorate agli annunci dei siti in vendita; AdSense sui nostri domini è ancora in revisione.
- Nessun blocco aggirato; le pagine dei concorrenti lette oggi sono solo home, `robots.txt` e mappe del sito.

## 8. Fonti lette oggi

- Volumi: `api.seodata.dev/v1/keyword` (17 ricerche riuscite) e 14 pagine `seodata.dev/keyword/…`.
- Concorrenti (200): einbuergerungstest-termine.de (home, robots.txt, mappa: 476 indirizzi, ultimo aggiornamento 12/11), marathonballot.com (443, 12/11), treatcompare.com (2.305, 11/11), buildpermitguide.com (659, 10/11), permitsguide.com (404, 2/10), sweldoph.com (236, 9/11), tmarkmetric.com (346, 10/11). convenioscolectivos.org: mappa 404.
- `api.volkshochschule.de/3/veranstaltungen`: 200 (il catalogo risponde ancora). `ccse.cervantes.es`: ancora la pagina di manutenzione.
- Destatis, comunicato n. 186 del 2026 (domande e naturalizzazioni 2025), letto dai risultati di ricerca.
- Autocomplete Google (15 frasi, DE/ES/US/GB/PH) per conferma della forma della domanda.
- File di partenza: `verifica-2026-11-12-einbuergerungstest.md`, `fronti-2026-11-12-permessi-casa-usa.md`, `fronti-2026-11-12-fertilita.md`, `fronti-2026-11-12-gare-di-massa.md`, `idee-2026-11-06-spagna-ccse.md`, `fronti-2026-11-11-casa-italia-stranieri.md`, `fronti-2026-11-12-radar-pagatori.md`, `fronti-2026-11-11-impianti-uk.md`, `fronti-2026-11-12-paghe-altri-mercati.md`, `fronti-2026-11-12-siti-in-vendita.md`.
