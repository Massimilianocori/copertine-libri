# Scoperta a volumi fuori dagli USA: paghe e fisco, energia e carburanti, calendari, auto in 11 Paesi (13/11/2026)

Solo ricerca: nessun sito modificato. Settori di partenza lontani dalle zone battute: **buste paga e imposte, IVA, prezzo dell'energia ora per ora, carburanti per distributore, sussidi, bollo auto, calendari scolastici**. Lingue locali. Metodo: prima il volume vero, poi il dato ufficiale letto con curl, poi i concorrenti.

## In breve

- **Circa 1.650 ricerche di volume** (1.500 con risposta, 150 senza dato): de 237, fr 187, es 147, gb 171, nl 135, au 118, ca 108, br 108, in 100, pl 90, mx 68, altri 12 (ie, nz, za, it, ae, sg, at, ch).
- **Nessuna famiglia arriva a "DA VERIFICARE"** (centrale ≥ 3.000 €/anno a 36 mesi e ≥ 60 €/ora). La migliore è a 900 €/anno e 56 €/ora.
- I volumi ci sono e sono grandi (Regno Unito 2 milioni al mese sui calcolatori di stipendio, Spagna 1,5 milioni sul prezzo della luce), ma dove il clic vale qualcosa i primi posti sono occupati da siti con vent'anni di età o dall'ente pubblico, e dove i risultati sono deboli il clic vale centesimi (Brasile, Messico, India, Polonia).
- **Due blocchi piccoli da mettere in coda come sezioni del calcolatore dell'inflazione** (già online): calcolatore IVA/GST in 13 Paesi (16 ore, 56 €/ora) e inflazione per Regno Unito, Canada, Australia e Germania (12 ore, 34 €/ora). Vanno dopo le diarie federali (74 €/ora) e i limiti 401(k) (68 €/ora) del file di stamattina.
- **Una riserva grande bloccata dal dato**: prezzo della luce ora per ora in Spagna. Il prezzo regolato (PVPC) sta sul sito del gestore di rete, che al server risponde 403; il prezzo all'ingrosso del giorno dopo si legge.
- Fatto nuovo sui carburanti: i file ufficiali di **Francia e Spagna oggi si leggono** (il 12/11 quello francese non rispondeva). Non basta: la domanda va sulle mappe.

Limiti, detti prima dei numeri:
- Volumi = medie mensili Google Ads. Frasi vicine con lo stesso numero sono un gruppo solo: contate una volta. Dove due gruppi possono sovrapporsi ho usato meno della somma.
- La pagina dei risultati di Google non è stata letta (i motori bloccano il server). Il rischio "risposta nel riquadro" è un giudizio, non una misura.
- Quote più basse dello 0,5-3 % della taratura dove i primi sono marchi forti: lezione della verifica di oggi sui prefissi (0,2 % era già troppo).
- Formula della casa: ricerche al mese × 12 × quota × 1,3 pagine a visita × incasso per 1.000 pagine (in euro). A 12 mesi: un terzo del centrale.
- Incasso per 1.000 pagine ipotizzato, non misurato: Regno Unito 10-18 €, Australia e Canada 8-14 €, Germania 5-10 €, Paesi Bassi 4-8 €, Spagna 4-8 €, Francia 3-7 €, Polonia, Brasile e Messico 2-3,5 €, India circa 1 €.

## 1. Le dieci famiglie, in ordine di €/ora

Cifre in €/anno. "Senza clic" = rischio che Google risponda da solo.

| # | Famiglia | Paesi | Ricerche al mese usate | Costo per clic | Dato e licenza (letto oggi) | Senza clic | 12 mesi | 36 mesi prudente / centrale / ottimista | Ore | €/ora | Voto | Esito |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Calcolatore IVA/GST (aggiungi, togli, aliquote ufficiali), una pagina per Paese e lingua | GB, AU, IE, CA, NZ, ZA, AE + DE, FR, IT, NL, ES, PL, IN | 480.000 in inglese + 710.000 altre lingue | GB 8,0 £; AU 5,2-10,5 $; IE 5,3 €; Québec 12 $; DE 0,6; FR 0,8; IT 1,4; IN 0,2 | Aliquote: gov.uk 200 (OGL), revenue.ie 200, ird.govt.nz 200; ATO 403, canada.ca non risponde | Basso: serve uno strumento | 300 | 165 / 900 / 3.500 | 16 | 56 | 5 | **IN CODA** come sezione del calcolatore dell'inflazione |
| 2 | Calcolatore dell'inflazione e serie dei prezzi fuori dagli USA | GB, CA, AU, DE (+ IN, ES, IT) | 240.000 Paesi ricchi + 95.000 altri | GB 2,0-2,9 £; CA 1,7-2,8 $; AU fino a 10 $; DE 1,2-1,3 € | ONS, CSV 200 (OGL); StatCan, zip 200 (licenza aperta canadese); Destatis Genesis 200 (DL-DE BY 2.0); ABS non raggiunta | Basso sul calcolatore, alto su "inflation rate" (contato al 25 %) | 135 | 90 / 410 / 1.680 | 12 | 34 | 4,5 | **IN CODA** come sezione, dopo la n. 1 |
| 3 | Prezzo della luce ora per ora, oggi e domani | ES | 1.500.000 | 1,3-2,6 €; "precio de la luz mañana" 6,7 € | **PVPC: REE e ESIOS 403 (blocco anti-bot)**. OMIE, prezzo all'ingrosso di oggi e domani: 200, "citare la fonte" | Medio-basso: tabella di 24 ore | 190 | 95 / 560 / 2.250 | 25 | 22 | 4,5 | RISERVA bloccata dal dato |
| 4 | Stipendio netto e imposte + pagine "£X after tax" | GB (+ NZ 74.000, IE) | 2.000.000 | 1,7-8,2 £ ("X after tax" 0) | gov.uk aliquote 2026-27: 200, OGL | Basso | 290 | 155 / 870 / 3.370 | 60 | 15 | 4 | RISERVA |
| 5 | Bollo auto dalla targa (wegenbelasting) + BPM e bijtelling | NL | 280.000 | 0,6-1,2 € | RDW, API 200 (CC0); tariffe: strumento del fisco 200, file delle tariffe non trovato | Basso | 85 | 50 / 260 / 870 | 25 | 10 | 3,5 | NO |
| 6 | Imposte sul reddito, tabelle settimanali, imposta di registro per Stato | AU | 1.050.000 | 0,5-5 $ | ATO 403; legge federale 200 (legislation.gov.au); uffici statali non letti | Basso | 120 | 65 / 360 / 1.380 | 50 | 7 | 3,5 | NO |
| 7 | Calendari con clic alto: bank holidays e half term (GB), public holidays (AU), Ferien per Land (DE), schoolvakanties (NL) | GB, AU, DE, NL | 3.400.000 | GB 2,3-6,8 £; DE 1,0-2,7 €; NL 0,5-1,7 €; AU quasi tutto 0 | gov.uk 200; data.gov.au 200; KMK 200; Paesi Bassi: elenco ufficiale 200 | **Alto** sui festivi, medio sulle vacanze per regione | 90 | 50 / 265 / 1.490 | 40 | 7 | 2,5 | NO confermato (festivi già NO il 17/10 e il 25/10; calendari scolastici NO oggi, file vacanze-scolastiche) |
| 8 | Calcolatori dei sussidi (Wohngeld, Bürgergeld, Kinderzuschlag, Elterngeld, BAföG, Unterhalt, Rente) | DE | 1.020.000 | 0,1-0,8 €; Bürgergeld 3,9; Kinderzuschlag 4,5 | Leggi su gesetze-im-internet 200 (testi ufficiali liberi) | Basso | 110 | 80 / 335 / 1.590 | 70 | 5 | 3 | NO |
| 9 | Imposte e busta paga per provincia | CA | 480.000 | 0,5-5 $ | **canada.ca non risponde al server** (come stamattina) | Basso | 55 | 30 / 165 / 630 | 35 | 5 | 3 | NO, bloccata dal dato |
| 10 | Carburanti per distributore dai file ufficiali | DE, FR, ES | 945.000 (escluse le ricerche "vicino a me") | DE 0,2-1,0 €; FR 0,5-1,7; ES 0,2-3,1 | FR: 200, Licence Ouverte 2.0, 9.834 impianti; ES: 200, 11.503 impianti; DE: Tankerkönig 200, CC BY 4.0, chiave gratuita | **Alto**: Google Maps mostra i prezzi | 50 | 22 / 150 / 620 | 45 | 3 | 3 | NO confermato |

Quote (prudente / centrale / ottimista) e incasso per 1.000 pagine: 1) 0,2 / 0,7 / 2 %; inglese 8 / 12 / 16 €, altre lingue 2 / 3,5 / 5 €. 2) 0,3 / 1 / 3 %; 7 / 10 / 14 € e 2,5 €. 3) 0,1 / 0,4 / 1,2 %; 4 / 6 / 8 €. 4) 0,05 / 0,2 / 0,6 %; 10 / 14 / 18 €. 5) 0,3 / 1 / 2,5 %; 4 / 6 / 8 €. 6) 0,05 / 0,2 / 0,6 %; 8 / 11 / 14 €. 7) 0,03 / 0,1 / 0,4 %; 3 / 5 / 7 €. 8) 0,1 / 0,3 / 1 %; 5 / 7 / 10 €. 9) 0,05 / 0,2 / 0,6 %; 8 / 11 / 14 €. 10) 0,05 / 0,2 / 0,6 %; 3 / 5 / 7 €.

## 2. Le prime quattro: volumi, dato, concorrenti

### 1. Calcolatore IVA/GST — in coda come sezione

| Voce | Che cosa ho letto |
|---|---|
| Volumi | gb "vat calculator" 201.000 (8,03 £), "vat calculator uk" 27.100 (6,18); au "gst calculator" 110.000 (5,23 $), "gst calculator australia" 14.800 (10,5); ie 14.800 (5,29 €); ca "gst calculator" 14.800, "hst calculator" 14.800 (5,5), Québec 14.800 (12); nz 33.100; za 22.200; ae 12.100 (2,0). de "mwst rechner" 74.000 (0,62 €); fr "calculateur tva" 74.000 (0,76), "ttc ht" 60.500; it "calcolo iva" 49.500 (1,43), "scorporo iva" 40.500; nl "btw berekenen" 74.000 (0,65); es 60.500 (0,08); pl 33.100; in 246.000 (0,23) |
| Concorrenti letti | vatcalculator.co.uk (1.509 parole, AdSense), gstcalculator.com.au (678 parole, AdSense), gstcalculator.net (363 parole), calculator.net (1.062), mehrwertsteuerrechner.de (1.824), calculertva.com (861), btw-berekenen.nl (462, senza pubblicità) |
| Che cosa manca a loro | Poco. Sono siti di una pagina con il nome esatto nel dominio. Nessuno dei letti mette nella stessa pagina le aliquote ridotte per tipo di bene con la fonte ufficiale e la data |
| Dove va | Sezione del calcolatore dell'inflazione (stesso pubblico: chi fa un conto) |
| Rischi | Domini con il nome esatto e molti anni; la quota 0,7 % vuol dire prima pagina in fondo per le teste; le aliquote canadesi e australiane vanno prese da fonti secondarie finché i siti ufficiali non rispondono |

### 2. Inflazione fuori dagli USA — in coda come sezione

| Voce | Che cosa ho letto |
|---|---|
| Volumi | gb "inflation calculator" 74.000 (2,85 £), "inflation calculator uk" 33.100, "inflation rate uk" 49.500 (1,48); ca 40.500 (1,72 $), "inflation calculator canada" 14.800, "inflation rate canada" 40.500 (2,8); au 14.800, "inflation rate australia" 40.500 (10,1 $); de "inflationsrechner" 18.100 (1,31 €), "inflation deutschland" 49.500 (1,15), "verbraucherpreisindex" 18.100; in 49.500 (0,15); es "calculadora ipc" 14.800; it "rivalutazione istat" 18.100 (0) |
| Concorrenti letti | Bank of England (1.651 parole, dal 1209), Bank of Canada (1.496), RBA (1.629), Hargreaves Lansdown (1.265): tutti calcolatori ufficiali o di marchio |
| Che cosa manca a loro | Le pagine pronte "quanto valgono 100 £ del 1990 oggi", anno per anno: i calcolatori ufficiali hanno una pagina sola |
| Rischio | Chi cerca "inflation rate uk" vuole una cifra che Google mostra |

### 3. Prezzo della luce in Spagna — riserva bloccata dal dato

| Voce | Che cosa ho letto |
|---|---|
| Volumi (es) | "precio luz hoy" 1.000.000 (1,26 €), "precio de la luz hoy" 1.000.000 (1,52: stesso gruppo), "tarifa luz hoy" 301.000 (2,13), "luz hoy" 201.000, "precio luz mañana" 201.000 (2,57), "precio de la luz mañana" 90.500 (6,72), "tarifa luz" 74.000 (4,04), "precio luz hoy por horas" 74.000, "precio luz" 60.500 (2,41), "hora luz hoy" 49.500, "esios pvpc" 12.100 (3,29) |
| Dato | Il prezzo che la gente paga è il PVPC, pubblicato dal gestore di rete: `apidatos.ree.es`, `api.esios.ree.es`, `ree.es` rispondono tutti 403 con pagina anti-bot. Non si aggira. OMIE (gestore del mercato): file del prezzo all'ingrosso ora per ora, 200 per oggi e per domani; avviso legale: usare citando la fonte. Manca la parte regolata (pedaggi, oneri, servizi di aggiustamento) |
| Concorrenti | tarifaluzhora.es, Selectra, El Economista: 403, non letti. preciodelaluz.org: letto, 238 parole, senza pubblicità. epdata: 1.547 parole. La riga del 7/11 citava anche OCU e i quotidiani, che pubblicano un articolo al giorno |
| Perché riserva | Volume e clic sono i più alti del file tra i Paesi non inglesi, ma senza il PVPC esatto la pagina è peggiore di quelle che ci sono. Si riapre se il file PVPC si legge dal posto dove gira l'aggiornamento automatico (da provare una volta, senza aggirare blocchi) |

### 4. Stipendio netto nel Regno Unito — riserva

| Voce | Che cosa ho letto |
|---|---|
| Volumi (gb) | "salary calculator" 450.000 (3,48 £), "take home pay calculator" 368.000 (2,02), "tax calculator" 301.000 (4,24), "payroll calculator uk" 165.000 (8,23), "tax income calculator" 110.000 (4,71), "uk tax brackets" 74.000, "average salary uk" 74.000 (3,48), "redundancy calculator" 49.500 (3,55), "wage calculator" 40.500, "self employed tax calculator" 22.200 (4,77), "paye calculator" 22.200, "holiday entitlement calculator" 22.200 (3,67), "dividend tax calculator" 9.900 (7,05). "40000 after tax" 12.100, 30.000/35.000/45.000/50.000: 8.100-9.900 l'una, tutte a 0 £ |
| Vicini | nz "paye calculator" 74.000 (3,16 $); ie "tax calculator" 8.100 (11,95 €) |
| Concorrenti letti | thesalarycalculator.co.uk (2.464 parole, AdSense, 2026), income-tax.co.uk (**ha già una pagina per ogni stipendio: "£30,000 After Tax 2026/2027"**, 1.100 parole), MoneySavingExpert (1.932), Reed (316). uktaxcalculators: 403 |
| Che cosa manca a loro | Niente di misurabile. È solo quota |
| Paghe del servizio sanitario | "nhs pay bands" 40.500 (2,8 £), band 5/6/7 18.100-22.200 a 0, "nhs pay calculator" 22.200, "nhs pay rise 2025" 49.500: circa 230.000. nhsbands.co.uk ha già fasce 2026/27 con il netto. NHS Employers 200. Non cambia il conto |

## 3. Semi misurati e scartati

| Seme | Paese | Volume al mese | Costo per clic | Perché no |
|---|---|---|---|---|
| brutto netto rechner, gehaltsrechner, stundenlohnrechner | DE | 2.240.000 / 246.000 / 135.000 | 0,05-0,7 € | clic nullo sulla testa, molti calcolatori |
| tvöd rechner, tv-l rechner, tvöd vka, entgelttabelle | DE | 135.000 / 74.000 / 60.500 / 22.200 | 0-2,6 € | un sito solo le copre tutte da anni (non letto: non risponde al server) |
| heizölpreise, pelletpreise | DE | 1.220.000 / 49.500 | 0,5 € | prezzi dei venditori, nessun dato ufficiale aperto |
| clever tanken, tankstelle in der nähe | DE | 1.000.000 / 550.000 | 0,06-0,85 € | nome di un marchio; ricerca da mappa |
| prozentrechner; percentage calculator | DE; GB | 368.000; 368.000 | 2,8 €; 2,1 £ | nessun dato ufficiale: conto generico, fuori tema |
| kfz steuer rechner, bußgeldkatalog, kreditrechner, zinsrechner | DE | 135.000 / 135.000 / 165.000 / 74.000 | 0,8-2,3 € | già riserva o NO; banche e comparatori |
| brut en net, simulateur impôt, simulateur apl | FR | 550.000 / 90.500 / 246.000 | 0,15 / 2,0 / 0,4 € | strumenti ufficiali (URSSAF, fisco, CAF) |
| vacances scolaires, calendrier 2025, jours fériés 2025 | FR | 368.000 / 1.220.000 / 301.000 | 0,03-0,05 € | clic nullo |
| dvf, prix au m2 | FR | 246.000 / 14.800 | 2,9 / 1,6 € | "dvf" è il nome dello strumento pubblico; file 200 (98 MB) ma coda piccola |
| heures creuses, tempo edf, plafond livret a, taux livret a | FR | 135.000 / 90.500 / 201.000 / 165.000 | 1,7-2,5 € | una cifra o un colore al giorno: riquadro; già NO il 7/11 |
| taxe foncière, kbis, siret, points permis | FR | 165.000 / 90.500 / 60.500 / 201.000 | 0,7-7,7 € | navigazione verso il servizio ufficiale |
| gasolineras; cita itv; multas dgt; euribor | ES | 2.240.000; 368.000; 135.000; 368.000 | 0,1-2,4 € | mappa, prenotazione, servizio ufficiale, licenza |
| calculadora sueldo neto, simulador jubilación, calcular irpf | ES | 165.000 / 110.000 / 60.500 | 0,07-0,8 € | clic nullo |
| notas de corte | ES | 60.500 (+ 22.200) | 1,4-5,6 € | code per corso 1.300-6.600; nessun file unico (già NO il 12/11) |
| calculo rescisão, calculadora férias, salário líquido | BR | 673.000 / 201.000 / 246.000 | 0,01-0,03 | clic nullo |
| ipva, sisu, cid 10, das mei, cnae, cbo | BR | 450.000 / 1.220.000 / 301.000 / 550.000 / 110.000 / 90.500 | 0,2-1,3 | navigazione verso lo Stato o il portale; codici già riserva stamattina |
| salario mínimo 2025, semanas cotizadas, tenencia edomex, hoy no circula, calendario escolar | MX | 450.000 / 550.000 / 301.000 / 368.000 / 110.000 | 0-1,1 | clic nullo o servizio ufficiale |
| kalkulator wynagrodzeń, brutto netto, waloryzacja, kalendarz 2025 | PL | 450.000 / 201.000 / 368.000 / 550.000 | 0,04-0,7 | resa bassa, portali forti |
| sip, emi, gratuity, gst, income tax calculator; 8th pay commission; pay matrix | IN | 4.090.000 / 3.350.000 / 246.000 / 246.000 / 550.000; 368.000; 110.000 | 0,01-0,5 $ | clic da centesimi |
| kentekencheck, bruto netto, zorgtoeslag, hypotheek berekenen | NL | 673.000 / 135.000 / 90.500 / 246.000 | 0,03-1,1 € | clic nullo o banche; dato RDW libero ma marchi forti |
| mot check, car tax check, council tax, child benefit, stamp duty calculator | GB | 4.090.000 / 673.000 / 368.000 / 301.000 / 368.000 | 0,25-2,4 £ | servizio gov.uk |
| council tax band checker, council tax bands | GB | 74.000 / 90.500 | 4,6 / 0 £ | la fascia è per indirizzo: servizio ufficiale |
| mortgage calculator | GB, CA, AU | 550.000 / 550.000 / 110.000 | 0,7-1,2 | banche |
| fuel watch, fuel check, rego check, pay calculator | AU | 201.000 / 60.500 / 450.000 / 368.000 | 1,1-6,3 $ | nomi di servizi pubblici o di un sito |
| gas prices tomorrow, gas price toronto | CA | 201.000 / 60.500 | 3,7 / 2,9 $ | è una previsione, non un dato ufficiale |
| minimum wage ontario, crs calculator, sunshine list | CA | 165.000 / 135.000 / 74.000 | 7,1 / 5,4 / 0 $ | già riserva; immigrazione (zona battuta); nomi di persone |
| atar calculator, myschool, university rankings uk | AU, GB | 90.500 / 27.100 / 40.500 | 1,0-7,1 | dati di graduatoria non aperti |

Frasi con l'anno 2026 (festivi, vacanze, salario minimo, tabelle): quasi sempre senza dato, perché lo strumento fa la media dei 12 mesi passati. Ho misurato le stesse frasi con il 2025.

## 4. Che cosa cambia nella coda

| Azione | Dettaglio |
|---|---|
| In coda, sezione nuova | Calcolatore IVA/GST in 13 Paesi sul sito dell'inflazione: 16 ore, centrale 900 €/anno a 36 mesi, 56 €/ora. Sotto l'asticella "DA VERIFICARE": non serve verificatore, si decide con le altre sezioni |
| In coda, sezione nuova | Inflazione per GB, CA, AU, DE sul sito dell'inflazione: 12 ore, centrale 410 €/anno, 34 €/ora |
| Da provare una volta | Lettura del PVPC spagnolo dal posto dove girano gli aggiornamenti automatici. Se risponde, la n. 3 si ricalcola (ottimista 2.250 €/anno) |
| Niente siti nuovi | Nessuna delle dieci regge un sito nuovo |
