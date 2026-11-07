# Fronte mai toccato: grandi mercati NON inglesi × settori di consumo (7/11/2026)

Domanda: nei grandi mercati che non parlano inglese (Germania, Francia, Spagna, Brasile, Giappone, Messico, Italia) esiste una domanda di consumo con **dati ufficiali aggiornabili in automatico**, **primi risultati deboli** e **qualcuno che paga con una cifra scritta**? Regole del 6-7/11: decido io sui dati; fuori da viaggi, visti, immigrazione, esami di lingua, tasse locali e burocrazia per stranieri; Massimiliano può metterci ore sue.

Parole cercate prima in `ESPLORATE.md` (0 risultati salvo dove indicato): Balkon, PVGIS, EPREL, PVPC, precio luz, esios, SMARD, Tibber, THG, Wallbox, FIPE, ANEEL, bandeira, INMETRO, CFE, gasolina, Afore, CETES (1, altro tema), CDB, Hotmart, A8, Rakuten, 補助金, DPE, Kita, Elterngeld, Gehalt/sueldo/salário, ITV, verificación, MaStR, Typklasse, perro/bienestar animal. Già visti e **non riproposti**: pannello solare da balcone **solo USA e Regno Unito** (sezione FHA Condos, 6/11), prezzo della corrente per Comune in Svizzera (NO 17/10), prezzi carburanti (NO 14/10), durezza dell'acqua per Comune FR/IT/DE/ES (NO 7/11), colonnine PUN Italia (NO), DVF e valori catastali (NO).

Metodo: autocomplete Google con `gl` e `hl` del Paese (numero di suggerimenti 0-10, 77 domande); composizione dei risultati con la ricerca web; programmi e fonti letti con curl (codice HTTP). "Letta" = cifra scritta sulla pagina scaricata oggi. Cambi: 1 € = 6,3 R$ = 20 MX$ = 160 ¥. Stime lorde a 18 mesi.

## Esito in breve

**Nessuna idea passa l'asticella del sito nuovo** (voto ≥ 7 e ≥ 5.000 €/anno centrali). Due idee hanno l'**ottimista ≥ 10.000 €** e vanno segnalate:

1. **Brasile: quanto consuma e quanto costa in bolletta ogni condizionatore, modello per modello** (tabella ufficiale INMETRO × tariffa ANEEL della propria distributrice). Voto **6,5**; 1.100 / **5.400** / 18.000 €/anno; 30-40 ore. Ha la centrale sopra 5.000 ma il voto si ferma a 6,5: Canaltech, Buscapé e Zoom occupano i primi posti e il pagamento di Amazon.com.br a un italiano senza CPF va verificato.
2. **Germania (poi Francia, Spagna, Italia): Balkonkraftwerk città per città** (rendimento PVGIS, impianti registrati nel MaStR, contributi comunali con scadenza). Voto **6**; 750 / **4.600** / 15.000 €/anno; 30-40 ore + 10 per lingua. Pagano EcoFlow (≥ 5 %, ordine medio > 1.000 €, letta) e Zendure (5-10 %, cookie 30 giorni, letta), ma rispondono già i venditori stessi (priwatt, Kleines Kraftwerk, Solakon, Anker) e Finanztip.

Terza approfondita: **Messico, consumo dei minisplit e costo con la tariffa CFE del proprio clima** (voto 5): risultati davvero deboli (spam e blog), ma nessuna tabella ufficiale per modello letta e Amazon.com.mx paga il 5 %.

**Lezione.** Nei mercati non inglesi i primi risultati sono più deboli solo nelle code lunghe di Paesi a basso valore per visita (Messico, Brasile). Dove la visita vale molto (Germania, Francia) rispondono comparatori grandi (Check24, Verivox, Finanztip, ADAC, Kelwatt, Selectra) e i venditori stessi con blog in ogni lingua. Il punto d'incontro più vicino all'asticella è il **Brasile**: Amazon.com.br paga l'**8 % sugli elettrodomestici e l'11 % sugli animali** (letta), il doppio di Amazon.de (2,5 % grandi elettrodomestici), e i dati ufficiali per modello esistono.

## 1. Le idee, mercato per mercato

| Mercato | Idea | Domanda (autocomplete, n. suggerimenti) | Dati ufficiali (curl) | Chi paga (letta?) | Primi risultati | €/anno prud. / centr. / ott. | Ore | Voto |
|---|---|---|---|---|---|---|---|---|
| **Germania** | Balkonkraftwerk città per città: rendimento, impianti registrati, contributi | "balkonkraftwerk förderung" 10 (Sachsen, NRW, Bayern, MV, München), "… berlin" 10, "… köln" 6, "… hamburg" 2; "ertrag" 10 (Rechner, Tabelle, pro Tag, Winter); "anmelden" 10 (Länder, Marktstammdatenregister); "mit speicher" 10; "2000w" 10; "test" 10 | PVGIS API 200 (Monaco, 800 W → 909 kWh/anno); MaStR JSON 200 per Comune (Colonia: 25.778 impianti solari); Gesamtdatenexport del 7/11/2026 | EcoFlow ≥ 5 %, ordine medio > 1.000 € (letta); Zendure 5 % base, fino al 10 %, cookie 30 giorni (letta); Amazon.de Baumarkt 5 % (letta) | Finanztip, Vattenfall, Anker SOLIX per Land, priwatt, Kleines Kraftwerk (mappa e calcolatore), Solakon e homeandsmart (calcolatore per CAP), nexvyra (automatico), elektronik-zeit; "una panoramica completa e aggiornata non esiste" (ema-energiewelt) | 750 / 4.600 / 15.000 (con FR, ES, IT) | 30-40 | **6** |
| Germania | Prezzo della corrente di domani, ora per ora (tariffe dinamiche) | "strompreis morgen" 10 (Börse, Tibber, stündlich); "dynamischer stromtarif" 10 (Vergleich, Testsieger) | SMARD JSON 200 (Bundesnetzagentur) | Tibber, Ostrom: solo "50 € per amico" a clienti (letta Ostrom), non usabile; Rabot 200 senza cifre | Tibber, aWATTar, energy-charts (Fraunhofer), comparatori | 0 / 400 / 2.000 | 15 | 4 |
| Germania | Contributo per l'auto elettrica 2026 (fino a 6.000 €, con reddito e figli) | "e auto förderung 2026" 10 (Rechner, beantragen, Rentner, wie lange noch) | regole BAFA/Förderzentrale (non lette) | leasing e carwow (non letti) | ADAC con calcolatore (6 pagine nei primi 18), carwow, GIGA, mydealz, EnBW | 0 / 300 / 2.000 | 15 | 4 |
| Germania | THG-Quote 2026, Wallbox Förderung, Typklasse, Kita Gebühren, assicurazione del cane | tutte 10 | GDV, Länder (non letti) | comparatori | Check24, Verivox, ADAC, GDV, Comuni | – | – | 3-4 |
| **Francia** | Colore Tempo di oggi e domani | "tempo couleur" 10 ("du jour et du lendemain", "demain") | api-couleur-tempo.fr 200 (non ufficiale; RTE con registrazione) | comparatori energia (non letti) | fournisseurs-electricite (Selectra) con previsioni a 9 giorni, Kelwatt con previsioni a 7, EDF | 0 / 300 / 1.500 | 10 | 3,5 |
| Francia | Kit solare plug and play, rendimento per città | "panneau solaire balcon" 10 (copropriété, Lidl, batterie); "kit solaire plug and play" 10 (1000-3000 W, batterie); "prime panneau solaire" 10 (Toulouse Métropole, Corse) | PVGIS (sopra) | EcoFlow, Zendure (sito .fr nell'elenco paesi), Amazon.fr (pagina 000) | negozi, Leroy Merlin, blog delle marche | dentro l'idea tedesca | +10 | – |
| Francia | Bonus écologique / leasing social, elenco modelli | "leasing social" 10, "bonus écologique" 10 | elenco éco-score ADEME (non letto) | leasing (non letti) | Automobile Propre, stampa auto, costruttori | – | – | 4 |
| **Spagna** | Prezzo della luce domani ora per ora (PVPC) | "precio luz mañana" 10, con le date di ieri e oggi | apidatos.ree.es **403** dal server (non aggirato) | AdSense, comparatori | tarifaluzhora, OCU, preciodelaluz, Selectra, giornali | 0 / 500 / 3.000 | 15 | 3,5 |
| Spagna | Assicurazione obbligatoria del cane (Ley 7/2023) | "seguro perro obligatorio" 10 (precio, barato, Madrid), "seguro responsabilidad civil perro" 10; per Comunidad 0 | nessuno strutturato (manca il regolamento) | nessun programma con cifra: Barkibu, Santévet, Kozoo, Kiwoko, Tiendanimal 404 | Selectra, Acierto, Roams, Bankinter, BBVA, giornali | 0 / 300 / 2.000 | 10 | 4 |
| Spagna | Kit solar balcón | "kit solar balcón" 10 (Lidl, 800 W, batería, Leroy Merlin), "placas solares balcón" 10 | PVGIS | Amazon.es Bricolaje 5 % (letta) | negozi | dentro l'idea tedesca | +10 | – |
| **Brasile** | **Consumo e costo in bolletta di ogni condizionatore (INMETRO × ANEEL)** | "consumo ar condicionado" 10 (9.000-24.000 BTU, inverter); "quanto gasta um ar condicionado" 10; "ar condicionado mais econômico" 10; "tabela inmetro ar condicionado" 10 (2026, pdf); "quantos btus para [m²]" 10; "tarifa kwh enel" 4 | INMETRO PDF 200 (3,9 MB, aggiornato 31/12/2025, consumo annuo kWh e IDRS per modello; 1.063 righe Split Hi-Wall; Gree, Hisense, Samsung, Elgin, Carrier, TCL, Midea…); ANEEL CSV tariffe generato il 7/11/2026 | **Amazon.com.br Eletrodomésticos 8 %, Pet Shop 11 %** (letta) | Canaltech, Buscapé, Zoom (comparatori di prezzo), webarcondicionado (negozio), tecnoblog, blog di affiliazione; le classifiche citate usano la tabella 2023 | 1.100 / 5.400 / 18.000 | 30-40 | **6,5** |
| Brasile | Bandeira tarifária del mese e tariffa per distributrice | "bandeira tarifária" 10 (mesi 2026, amarela) | ANEEL CSV 200 | AdSense (RPM basso) | ANEEL, distributrici, giornali | 0 / 300 / 1.500 | 10 | 4 (sezione dell'idea sopra) |
| Brasile | Tabela FIPE, piso salarial, rendimento poupança/CDB, ração | tutte 10 | FIPE, Novo CAGED, BCB | Amazon Pet 11 % per ração | siti enormi (FIPE, salario.com.br, calcolatori di banche) | – | – | 2-4 |
| **Giappone** | Contributi per batterie domestiche e auto elettriche per Comune | "蓄電池 補助金" 10 (東京都, 埼玉県, 千葉県, 愛知県); "電気自動車 補助金" 10 | Comuni in prosa; nessun elenco ufficiale unico | A8.net preventivi (cifre dietro login); Amazon.co.jp 0,5 % elettrodomestici (letta) | tainavi, taiyoko-kakaku, hojyokin-portal, mynavi, Anker Japan | 0 / 300 / 3.000 | 40 | 3,5 |
| Giappone | Furusato nozei, NISA, assicurazione animali | 10 | – | A8 (non letto) | portali enormi (Rakuten, Satofull), banche | – | – | 2 |
| **Messico** | Consumo dei minisplit e costo con la tariffa CFE del proprio clima (1, 1A-1F) | "cuanto consume un minisplit" 10 (1-2 toneladas, inverter, 12000 btu); "minisplit mas ahorrador" 6 ("segun profeco", "en mexico"); "tarifa 1f cfe" 10 (Sinaloa, Mexicali); "cuánto cobra cfe por kwh" 10 | app.cfe.mx **nessuna risposta** (000); Profeco 404; CONUEE 200 senza tabella per modello | Amazon.com.mx Electrodomésticos 5 %, Mascotas 8 % (letta) | **deboli**: blog voltflow, wiki.dronebotworkshop e siti violati, forum, Midea Centroamérica | 200 / 1.200 / 5.000 | 20 (sezione del sito brasiliano) | 5 |
| Messico | Precio gasolina, verificación, CETES/Afore | 10 | CRE/CNE, Banxico | nessuno con cifra | gasolinamexico, Profeco, governo, El Financiero | – | – | 3-3,5 |
| **Italia** | Fotovoltaico da balcone: rendimento per città e regole (Modello Unico, condominio) | "fotovoltaico balcone" 10 (accumulo, condominio, 800 W, Enel), "pannelli solari balcone" 10 (conviene, incentivi), "… conviene" 4 | PVGIS; incentivi regionali per famiglie **non trovati** | Amazon.it, EcoFlow, Zendure | edilizia.com, greenMe, Fastweb, pmi.it, Anker | dentro l'idea tedesca | +10 | – |
| Italia | Consumo del condizionatore e del frigorifero per modello | "condizionatore consumo" 10, "consumo frigorifero" 10 | EPREL API **403** (serve chiave) | Amazon.it (grandi elettrodomestici bassi) | Enel, Sorgenia, giornali | 0 / 300 / 1.500 | 20 | 3,5 |

Idee lasciate senza scheda perché toccano temi esclusi: bollo auto elettrica per Regione (tassa locale), Elterngeld (burocrazia), ITV per provincia (ispezione con tariffe regionali, AdSense soltanto), verificación vehicular (burocrazia).

## 2. Le tre approfondite

### 2.1 Brasile: "quanto gasta o seu ar-condicionado", modello per modello e distributrice per distributrice (voto 6,5)

**Domanda.** Ampia e stagionale (estate dicembre-marzo): "consumo ar condicionado 12000 btus (inverter)", "quanto gasta um ar condicionado de 12000 btus (ligado 8 horas por dia)", "ar condicionado mais econômico (12000 btus, do mercado, 2026)", "tabela inmetro ar condicionado 2026 (pdf)", "quantos btus para 20/30/40 metros quadrados". Tutte con 10 suggerimenti.

**Fonti lette oggi.**
- INMETRO, tabella di efficienza dei condizionatori `…/tabelas-de-eficiencia-energetica/condicionadores-de-ar/condicionadores-de-ar.pdf/@@download/file` **200** (3,9 MB, "Data de Atualização: 31/12/2025"; per modello: marca, unità interna ed esterna, tipo, capacità, potenza a carico pieno e parziale, IDRS, **consumo annuo di energia in kWh**, classe, numero di registro). Più la versione 2025 (3,7 MB). Il PDF si legge con `pdftotext -layout`: 11.881 righe, 1.063 righe "Split Hi-Wall"; marchi più presenti Gree, Hisense, Samsung, Elgin, Carrier, TCL, Midea, Philco.
- ANEEL, dati aperti `tarifas-homologadas-distribuidoras-energia-eletrica.csv` **200**, colonna `DatGeracaoConjuntoDados` = 2026-11-07 (rigenerato ogni giorno), con TUSD e TE per distributrice, classe e sottogruppo: la tariffa residenziale B1 di ogni distributrice si calcola in automatico.

**Pagine.** Una per modello ("Samsung WindFree 12.000 BTU: consumo e quanto custa por mês na Enel SP, Cemig, Light…"), una per taglia ("os 20 ar-condicionados 12.000 BTU mais econômicos segundo o INMETRO 2026"), una per distributrice ("quanto custa 1 kWh na Enel CE hoje"), un calcolatore BTU per m². Tutto rigenerato quando INMETRO o ANEEL aggiornano.

**Concorrenza.** Canaltech (articoli "qual é o ar-condicionado de 12.000 BTU mais econômico de 2026"), Buscapé e Zoom (comparatori di prezzo con guide), webarcondicionado (negozio con blog), tecnoblog, promotop e melhoresparacomprar. Le classifiche "secondo l'INMETRO" citate nei risultati usano la tabella **2023**; nessuno ha una pagina per modello con il costo per distributrice.

**Soldi (assunzioni).** Amazon.com.br: Eletrodomésticos **8 %** (letta). Condizionatore medio R$ 2.500 → R$ 200 ≈ 32 € a vendita. Ogni 1.000 visite: 5 % di clic, 2 % di acquisti → 1 vendita ≈ 30 € + AdSense Brasile circa 1 € → circa 30 € ogni 1.000 visite. Prudente 3.000 visite al mese ≈ **1.100 €/anno**; centrale 15.000 ≈ **5.400 €**; ottimista 50.000 (con Messico e i frigoriferi, stessa tabella INMETRO) ≈ **18.000 €**.

**Ore.** 30-40 (lettore del PDF, unione modelli-tariffe, 1.000 pagine modello, 60 distributrici, testi in portoghese). Massimiliano: 0 ore.

**Rischi.** (1) **Pagamento**: Amazon Associados Brasil potrebbe chiedere CPF o CNPJ e conto brasiliano (da verificare prima di costruire; alternativa Lomadee o Parceiro Magalu, cifre non lette). (2) Comparatori di prezzo forti sulle domande generiche. (3) Stagionalità. (4) PDF senza formato fisso: il lettore va controllato a ogni versione. (5) Portoghese brasiliano da scrivere bene.

**Voto 6,5** come sito nuovo: centrale sopra 5.000 €, ma voto sotto 7 per il rischio di pagamento e i comparatori. **Innesco per passare a 7:** confermare che Amazon.com.br (o Lomadee/Magalu con cifra scritta) paga un titolare italiano.

### 2.2 Germania: Balkonkraftwerk città per città (voto 6; poi FR, ES, IT)

**Domanda.** La più larga del fronte: "balkonkraftwerk förderung" con Länder e città (Berlino 10, Colonia 6, Amburgo 2), "ertrag" (Rechner, Tabelle, pro Tag, im Winter), "anmelden" (Länder, Marktstammdatenregister), "mit speicher" (Testsieger, 2000 W, Anker), "test" (Stiftung Warentest). Stesso tema in Francia ("kit solaire plug and play" 10), Spagna ("kit solar balcón" 10) e Italia ("fotovoltaico balcone" 10).

**Fonti lette oggi.**
- PVGIS (Commissione europea, JRC) `re.jrc.ec.europa.eu/api/v5_3/PVcalc` **200** JSON: Monaco, 800 W, 35°, sud → **909 kWh/anno**. Si calcola per ogni città d'Europa, mese per mese.
- Marktstammdatenregister: `GetErweiterteOeffentlicheEinheitStromerzeugung` **200** JSON con filtri (6.641.876 impianti solari; Colonia 25.778), campi Gemeinde, Plz, Bruttoleistung, data di messa in esercizio; esportazione completa del **7/11/2026**. Gli impianti da balcone si isolano dalla potenza (≤ 2 kW) o dal campo del file completo.
- Contributi comunali: in prosa, sulle pagine dei Comuni (Gelsenkirchen 100 € fino al 13/12/2026, Gottinga 150 € dal 1/6/2026, Friburgo 150-300 €, Monaco attivo, Berlino chiuso, Sassonia chiusa il 30/6/2026: dalla ricerca). Una ventina di programmi, cambiano spesso: aggiornamento a mano.

**Chi paga.** EcoFlow DE `de.ecoflow.com/pages/affiliate-program` **200**: "mindestens 5 % Provision", "durchschnittlicher Bestellwert liegt bei über 1.000 €" (letta). Zendure `zendure.de/pages/affiliate-program` **200**: "5 % Basisprovision", "bis zu 10 %", "Cookie-Dauer von 30 Tagen" (letta). Amazon.de: Baumarkt e Elektrowerkzeuge 5 %, Haushaltsgroßgeräte 2,5 % (letta). Anker SOLIX ha un programma (link nel piede pagina, cifre non lette); priwatt, Kleines Kraftwerk, Solakon, Yuma 404 alla pagina affiliati.

**Concorrenza.** Forte: Finanztip, Vattenfall, Anker SOLIX con una pagina per Land, priwatt, Kleines Kraftwerk (mappa interattiva dei contributi e calcolatore), Solakon e homeandsmart (calcolatore per CAP con dati DWD), nexvyra (sito automatico), elektronik-zeit, PC-Welt, t-online. Il buco: una pagina per città con impianti registrati, rendimento e contributo con data di scadenza verificata.

**Soldi (assunzioni).** Ogni 1.000 visite: 6 % di clic, 2,5 % di acquisti → 1,5 vendite × 40 € (5 % di 800 €) = 60 € + AdSense 4 € ≈ 64 €. Prudente 1.000 visite al mese ≈ **750 €/anno**; centrale 6.000 ≈ **4.600 €**; ottimista 20.000 con Francia, Spagna e Italia ≈ **15.000 €**.

**Ore.** 30-40 per la Germania (PVGIS per 400 città, conteggi MaStR per Comune, elenco dei contributi, testi in tedesco) + circa 10 per lingua. Massimiliano: 0 ore necessarie.

**Rischi.** (1) In Germania un sito commerciale deve avere l'**Impressum** con nome e indirizzo del titolare (dato personale di Massimiliano pubblicato) e c'è il rischio di diffide a pagamento (Abmahnung) per errori su trasparenza dell'affiliazione e cookie. (2) Concorrenza delle marche, che pubblicano in ogni lingua. (3) Stagionalità primavera-estate. (4) Contributi che chiudono senza preavviso.

**Voto 6** come sito nuovo (centrale sotto 5.000 €). Si potrebbe mettere in coda una **sezione europea** della sezione "balcony solar" già decisa per FHA Condos solo se FHA Condos cresce; altrimenti RISERVA.

### 2.3 Messico: consumo dei minisplit con la tariffa CFE del proprio clima (voto 5)

**Domanda.** "cuanto consume un minisplit de 1 tonelada (inverter)" 10, "… de 2 toneladas", "… de 12000 btu"; "minisplit mas ahorrador (segun profeco, en mexico)" 6; "tarifa 1f cfe (que significa, precio, Sinaloa, Mexicali, 2026)" 10; "cuánto cobra cfe por kwh (2026)" 10.

**Risultati.** I più deboli del fronte: blog voltflow, wiki.dronebotworkshop e altri siti violati, forum promodescuentos, Midea Centroamérica, un PDF universitario CFE del 2022. Nessuna risposta per tariffa e Comune.

**Fonti.** `app.cfe.mx/…/Tarifa1F.aspx` **nessuna risposta** dal server (000, non aggirato); `profeco.gob.mx/revista/estudios-de-calidad` 404; CONUEE 200 ma senza tabella per modello. Manca il dato per modello che in Brasile c'è.

**Chi paga.** Amazon.com.mx Electrodomésticos **5 %**, Mascotas 8 % (letta). Minisplit 1 tonnellata circa MX$ 8.000 → MX$ 400 ≈ 20 € a vendita.

**Soldi.** 200 / 1.200 / 5.000 €/anno come **sezione in spagnolo** del sito brasiliano (stesso motore, taglie e consumi tipici, tariffe CFE per blocchi). **Ore:** 20. **Voto 5.**

## 3. Fonti lette oggi (curl, HTTP)

| Fonte | HTTP | Contenuto |
|---|---|---|
| re.jrc.ec.europa.eu/api/v5_3/PVcalc (PVGIS) | 200 JSON | rendimento per coordinate (Monaco 800 W = 909 kWh/anno) |
| marktstammdatenregister.de/MaStR/Einheit/EinheitJson/GetErweiterteOeffentlicheEinheitStromerzeugung | 200 JSON | 6.641.876 impianti solari, filtro per Comune (Colonia 25.778) |
| marktstammdatenregister.de/MaStR/Datendownload | 200 | Gesamtdatenexport_20261107 |
| de.ecoflow.com/pages/affiliate-program | 200 | ≥ 5 %, ordine medio > 1.000 € |
| zendure.de/pages/affiliate-program | 200 | 5 % base, fino al 10 %, cookie 30 giorni |
| partnernet.amazon.de/help/node/topic/GRXPHT8U84RAYDXZ | 200 | Baumarkt 5 %, grandi elettrodomestici 2,5 % |
| afiliados.amazon.es (stessa pagina) | 200 | Bricolaje 5 %, Electrodomésticos 2,5 % |
| associados.amazon.com.br (stessa pagina) | 200 | Eletrodomésticos 8 %, Pet Shop 11 % |
| afiliados.amazon.com.mx (stessa pagina) | 200 | Electrodomésticos 5 %, Mascotas 8 % |
| affiliate.amazon.co.jp (stessa pagina) | 200 | 家電 0,5 %, ペット用品 4,5 % |
| programma-affiliazione.amazon.it (stessa pagina) | 200 | tabella presente |
| programme-partenaires.amazon.fr | 000 | nessuna risposta |
| gov.br/inmetro/…/condicionadores-de-ar.pdf | 200 PDF 3,9 MB | consumo annuo per modello, aggiornato 31/12/2025 |
| dadosabertos.aneel.gov.br/…/tarifas-homologadas-distribuidoras-energia-eletrica.csv | 206 (parziale) | generato il 7/11/2026 |
| smard.de/app/chart_data/4169/DE/index_hour.json | 200 JSON | prezzi orari di borsa (Germania) |
| api-couleur-tempo.fr/api/jourTempo/today | 200 JSON | "Bleu" il 7/11/2026 (non ufficiale) |
| apidatos.ree.es (precios mercados) | 403 | non aggirato |
| eprel.ec.europa.eu/api/products/… | 403 | serve chiave |
| app.cfe.mx (Tarifa 1F) | 000 | nessuna risposta |
| profeco.gob.mx/revista/estudios-de-calidad | 404 | – |
| priwatt, kleineskraftwerk, solakon, yuma, tibber, ostrom (pagine affiliati) | 404 | – |
| barkibu, santevet, kozoo, kiwoko, tiendanimal, mascotaplanet, zooplus.es, cobasi (affiliati) | 404 | – |
| petlove.com.br/afiliados | 403 | – |
