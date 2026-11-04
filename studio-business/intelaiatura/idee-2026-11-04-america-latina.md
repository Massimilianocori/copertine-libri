# America Latina e i suoi emigrati: casa, soldi e tasse, cittadinanza per discendenza, documenti, pagine es/pt (4/11/2026)

Zona: Messico, Brasile, Argentina, Colombia, Cile, Perù e chi da lì va in Spagna, Italia, USA e Portogallo. Settori di questo giro: casa e affitti, soldi e tasse, cittadinanza per discendenza (italiana, spagnola, portoghese), documenti e apostille. In più: pagine in spagnolo e portoghese per i siti che abbiamo già (Visa Income ha `/es/` e `/pt/` dal 31/10).

**Letto prima:** skill `rete-siti`, `REGOLE-FISSE.md` (30/10 e 31/10), `STRATEGIA.md`, `ESPLORATE.md` (righe LatAm, apostille, discendenza, rimesse, affitti), `ricerca-zona-latam-africa-2026-10-30.md`, `wf-2026-10-31-spagna-portogallo-latam.md`, `idee-2026-10-31-lingue.md`, `fronti-2026-10-31-lingue-immigrati.md`, `visaincome/NOTE.md`. Non ho rivalutato da capo le nicchie chiuse; dove c'è un fatto nuovo lo scrivo.

**Metodo:** circa 140 interrogazioni all'autocomplete di Google (`client=firefox`, gl e hl del Paese: ar/es, mx/es, co/es, pe/es, cl/es, ve/es, ec/es, es/es, br/pt-BR, us/en, us/es), lette il 4/11/2026; "10" = 10 suggerimenti, il massimo. Circa 60 prove con `curl` dal server (stato HTTP, dimensione, formato). Prima pagina con la ricerca web (vista dagli USA). GoatCounter (sola lettura) per i numeri veri della rete. Stime: lordo annuo a 18 mesi = visite al mese × 12 × euro ogni 1.000 visite; sono stime, non dati. Nessun blocco aggirato: dove una fonte risponde 403, 401 o 000 mi sono fermato.

**Numeri veri della rete usati (GoatCounter 5/10-4/11/2026):** EsameB1 653 visite, Visa Income 139, Before You Fly 107, Cruise 26, Tourist Tax 20, Aste 11. Le pagine `/es/` e `/pt/` di Visa Income (pubblicate il 31/10) hanno **1 visita** (`/es/cuanto-dinero-para-entrar-a-italia`): troppo presto per giudicarle.

---

## 0. Risposta in breve

**Nessuna idea arriva a 8. Nessun sito nuovo.** La migliore è una **sezione di Visa Income in spagnolo e portoghese da 7: "visti di lunga durata per nazionalità"** (Spagna non lucrativa, nomadi digitali, studio; Portogallo D7, D8, studio, CPLP, ricerca di lavoro; Italia studio), con la **tassa del consolato nella valuta del Paese**, la soglia di reddito convertita in pesos/real/soles e le regole che cambiano per nazionalità. È la domanda più forte trovata oggi ("visa no lucrativa españa para colombianos / mexicanos / argentinos / chilenos / peruanos / ecuador", "visa de estudiante españa para [nacionalidad]", "visto d7 portugal para brasileiros": 10 suggerimenti ognuna) e c'è un buco vero: in prima pagina si legge "circa 80 €", mentre i listini ufficiali dei consolati dicono altro (gratis per colombiani e cileni; 1.905-9.101 pesos messicani a seconda della voce; 152.000 pesos argentini; 110 € il visto nazionale portoghese).

| # | Idea | Dove | Chi paga | €/anno a 18 mesi (prudente / centrale / ottimista) | Ore | Voto |
|---|---|---|---|---|---|---|
| 1 | **Visti di lunga durata per nazionalità, in es/pt** (tassa del consolato in valuta locale, soglia di reddito in valuta locale, stato del visto portoghese di ricerca lavoro, CPLP) | sezione di Visa Income `/es/` `/pt/` | AdSense, IATI Estudiantes (10 %), Wise | 70 / 420 / 2.000 | 18-26 | **7** |
| 2 | **Tourist Tax in spagnolo e portoghese** (Roma, Venezia, Barcellona, Parigi, Lisbona, Porto, Amsterdam…, per categoria di albergo) | sezione di Tourist Tax `/es/` `/pt/` | AdSense, Booking/Stay22 | 100 / 500 / 2.000 | 12-18 | **6,5** |
| 3 | Acquisti di cittadinanza per cittadinanza precedente (Eurostat `migr_acq`) | righe in "Who moved where" di Visa Income | AdSense | 20 / 100 / 400 | 2-4 | 5 |
| 4 | Affitti in Spagna: zone tensionate, indice di riferimento, deposito della cauzione per comunità | sito nuovo in spagnolo | AdSense ES, assicurazioni contro l'affitto non pagato (programma non letto) | 200 / 900 / 3.500 | 30-40 | 5,5 (RISERVA) |
| 5 | Portogallo IFICI ("NHR 2.0") | Visa Income | AdSense | – | – | 5 (RISERVA, fonte non provata) |
| 6 | Apostille per Stato (USA, en/es), per Stato brasiliano, per Stato messicano | – | – | – | – | 4-4,5 (NO) |
| 7 | Cittadinanza per discendenza italiana in es/pt | – | – | – | – | 4 (NO) |
| 8 | Ley de nietos (Spagna) dopo la chiusura | – | – | – | – | 3,5 (NO) |
| 9 | Cittadinanza portoghese per i nipoti (LO 1/2026) | – | – | – | – | 4 (resta RISERVA con evento) |
| 10 | Doppie imposizioni, pensioni tra Paesi, DSDP brasiliana | – | – | – | – | 3-4 (NO) |
| 11 | Voto degli spagnoli all'estero, elezioni del 29/11/2026 | – | – | – | – | 3,5 (NO) |

**Da costruire subito a costo zero (rete fitta):** la n. 1 (Visa Income, una sola pubblicazione serale) e, nella stessa coda della versione francese già in ESPLORATE, la n. 2. La n. 3 è un'aggiunta di 2-4 ore alla sezione "Who moved where".

---

## 1. Visti di lunga durata per nazionalità, in spagnolo e portoghese (voto 7, sezione di Visa Income)

### 1.1 Cosa sarebbe
Dentro `/es/` e `/pt/` di Visa Income, una pagina per **visto × nazionalità** solo dove i fatti cambiano davvero da un Paese all'altro:
- **Spagna:** residencia no lucrativa (400 % IPREM), nómada digital (200 % SMI), estudiante (100 % IPREM), per colombiani, messicani, argentini, cileni, peruviani, venezuelani, ecuadoriani (7 × 3 = 21 pagine) + 3 pagine portoghesi per brasiliani;
- **Portogallo:** D7, D8, estudante, CPLP per brasiliani (pt) e D7/estudante per colombiani, messicani, peruviani, venezuelani (es) (circa 10 pagine);
- **Italia:** visto per studio (467,65 €/mese, già nella sezione "Study in Italy") per argentini, messicani, colombiani, peruviani, cileni, ecuadoriani (6 pagine), più il visto nomadi;
- in ogni pagina: **la tassa del consolato del Paese nella sua valuta** (dal listino ufficiale, con data), la soglia di reddito o di risparmio **in pesos, real, soles** (calcolatore con familiari, come le pagine inglesi), il consolato competente, i documenti da apostillare in quel Paese (con il link all'ente che li rilascia), il riquadro assicurazione.

Totale 40-45 pagine, più 3 pagine indice. Non è una traduzione delle 756 pagine inglesi: ogni pagina ha numeri propri di quella nazionalità (regola contro i contenuti in serie).

### 1.2 Fonti (provate il 4/11/2026)
| Fonte | HTTP | Cosa dà |
|---|---|---|
| Consolato di Spagna a Bogotá, listino visti (`exteriores.gob.es/DocumentosAuxiliaresSC/Colombia/BOGOTÁ (C)/TASAS DE VISADOS AÑO 2024 junio.pdf`) | 200, PDF 313 KB, testo leggibile | **visti nazionali gratuiti per Andorra, Cile, Colombia, Corea del Sud, Costa Rica, Croazia, El Salvador, Honduras, Giappone, Nicaragua, Panamá, Paraguay, San Marino** ("según acuerdos y convenios"); altri Paesi 346.400 COP. Listino del 5/6/2024; il consolato annuncia "actualización de las tasas a partir del 1 de octubre de 2026" (notizia del 15/9/2026, 200) senza il nuovo PDF nella notizia |
| Consolato di Buenos Aires, "Hoja informativa tasas consulares a 1 de enero de 2026" | 200, PDF 197 KB | **visto nazionale 152.000 pesos**, Schengen 152.000; per australiani, canadesi, statunitensi, etiopi, irlandesi, britannici la tassa si chiede per email (reciprocità) |
| Consolato di Santiago del Cile, "Tasas consulares" (dal 1/1/2026) | 200, PDF 29 KB | visti nazionali gratuiti per la stessa lista di Paesi; altri **96.080 CLP**; autorizzazione di residenza 11.680 CLP |
| Consolato di Lima, "Tasas consulares 2026" (file chiamato 2024) | 200, PDF 30 KB | Schengen 352,10 soles; righe "Residencia no lucrativa 42,80 soles" (da capire se è la sola autorizzazione: va letto con il revisore) |
| Consolato di Città del Messico, "Tasas visados" dal 1/1/2025 | 200, PDF 440 KB | **Visado 1.905 MXN**; "Visados de estudios 3.226 MXN", "Vis estudiante 9.101 MXN", "Visado residencia no lucrativa 13.166 MXN", "Vis trabajadores cualificados 59.478 MXN" (righe diverse per lo stesso visto: probabile reciprocità per alcune nazionalità; **da interpretare riga per riga prima di costruire**; listino del 2025, da ricontrollare) |
| Consolato di Caracas, "Tasas 01.04.2026" | 200, PDF 251 KB | stesse voci in bolívares (es. residencia no lucrativa 319.710) |
| Pagine dei consolati spagnoli in America Latina | 200 per 20 su 29 provati (Messico, Guadalajara, Monterrey, Bogotá, Lima, Buenos Aires, Córdoba, Rosario, Mendoza, Santiago, Caracas, Quito, Guayaquil, Santa Cruz, Montevideo, L'Avana, Santo Domingo, San Paolo, Rio, Salvador, Porto Alegre); 404 per le sedi che sono ambasciate (percorso `/Embajadas/`); San Paolo in portoghese 401 | i listini sono in sottopagine o PDF con nomi diversi: **elenco a mano di circa 25 indirizzi**, poi controllo automatico dell'impronta |
| MNE Portogallo, "Emolumentos" visti nazionali (`vistos.mne.gov.pt/pt/vistos-nacionais/informacao-geral/emolumentos`) | 200 | **"As taxas a pagar… de um pedido de visto nacional é de 110€"** (fatto nuovo: si legge spesso 90 €) |
| MNE Portogallo, "Procura de Trabalho Qualificado" | 200 | **"AINDA NÃO DISPONÍVEL NOS POSTOS CONSULARES PORTUGUESES. A aguardar a necessária regulamentação do artigo 57.º-A da Lei de Estrangeiros"**: risponde alle ricerche "voltou / vai voltar / está suspenso" |
| MNE Portogallo, "Meios de subsistência" e "Documentação instrutória – Residência" | 200 | riferimento alla retribuição mínima mensal garantida (già usata dalle pagine D7/D8) |
| Cambi: BCE (BRL 6,1579, MXN 21,0086 al 4/11/2026); Colombia TRM su `datos.gov.co` (JSON, 3.235,59 COP per dollaro il 4/11); BCRA `api.bcra.gob.ar` (JSON, quotazioni del 4/11); BCRP `estadisticas.bcrp.gob.pe` API (JSON, soles per dollaro); SII Cile `sii.cl/valores_y_fechas/dolar/dolar2026.htm` (HTML, dólar observado) | tutti 200 | tutte le valute senza chiavi; Banxico invece chiede un token (non serve: MXN c'è nella BCE) |

**Licenza:** testi e listini di amministrazioni pubbliche, si citano i fatti (importi, date) con il link; le pagine di `exteriores.gob.es` hanno l'aviso legal "uso privado" (letto il 31/10): si usano solo cifre e date con parole nostre, come per i passaporti spagnoli (decisione del revisore).

### 1.3 Domanda (autocomplete del 4/11/2026)
- co/es, ar/es, pe/es, cl/es: "visa no lucrativa españa" 10 (**para colombianos, mexicanos, argentinos, chilenos, peruanos, ecuador**, 2026 requisitos); "visa nomada digital españa" 10 (**para mexicanos, colombianos, venezolanos, argentina, salario minimo, familia, impuestos**); "visa de estudiante españa" 10 (**para peruanos, mexicanos, venezolanos, colombianos, ecuatorianos, hondureños**, "para mexicanos precio").
- co/es: "visa d7 portugal" 10 (**para colombianos, mexicanos, argentinos, chilenos**, "en español"); "visa de estudiante portugal" 10 (para colombianos, mexicanos, venezolanos, peruanos); "visa de estudiante italia" 10 (para mexicanos, argentinos, perú, colombia, chilenos, ecuador, "costo"); ar/es "visa de trabajo italia" 10 (per 9 nazionalità).
- mx/es: "cuanto cuesta la visa de españa" 10 ("en ecuador", "en cuba", "de estudiante", "de trabajo", "desde colombia").
- br/pt-BR: "visto d7 portugal" 9 (2026, requisitos, **valor**, **para brasileiros**, quanto tempo demora); "visto nomade digital portugal" 10 (valor, renda, para brasileiros); "visto nômade digital espanha" 10 (**renda mínima**, para brasileiros); "visto de procura de trabalho portugal" 10 (**voltou, ainda existe, esta suspenso, vai voltar**, valor); "visto cplp portugal" 10 (valor, **ainda existe**, 2026); "taxa visto portugal" 8 (estudante, trabalho, consulado); "visto de estudante portugal" 9 (preço, comprovação financeira); "visto espanha estudante" 10 (valor, Rio, Porto Alegre, Brasília).
- Deboli: "visa no lucrativa españa en pesos" 0, "visto d7 em reais" 0: la gente non cerca la valuta, cerca la nazionalità e il prezzo. La valuta è il nostro valore aggiunto dentro la pagina, non il titolo.

### 1.4 Prima pagina
"visa no lucrativa españa para colombianos 2026": studi legali spagnoli (costaluzlawyers, migratiolex, cohenyaguirre), `visago.dev/es/` (pagine automatiche "from-colombia" in spagnolo), `visaatlas.org` (sito automatico inglese: sitemap con 8.131 indirizzi, 1.439 pagine "from X to Y"; la pagina colombiani/non lucrativa dice "fees vary by nationality" senza cifra), nomad.watch, tuvisadoonline, global66. "cuánto cuesta la visa de estudiante para España desde México": studyineurope.eu, study-abroad.org, università; **tutti dicono "circa 80 €" o "60-80 €"**, nessuno riporta il listino del consolato né la gratuità per colombiani e cileni. Concorrenza **forte sul tema generale, debole sul numero per nazionalità**: è lo stesso schema della sezione rifiuti dei visti, l'unica della rete citata dagli assistenti AI.

### 1.5 Chi paga
- **AdSense** (attivo sulla rete dal 30/10): pubblico latinoamericano 1-2 € ogni 1.000 visite (stima), più alto per chi legge dalla Spagna.
- **IATI** su Tradedoubler: programmi ES, CO, PE, PT; **10 % per vendita convalidata, cookie 7 giorni** (pagina IATI ES 403039 letta il 4/11). IATI vende l'assicurazione per studenti usata per il visto di studio: una polizza annuale costa qualche centinaio di euro, quindi decine di euro a vendita (stima, prezzo non letto). Per non lucrativa e nomadi serve un'assicurazione sanitaria spagnola senza franchigie: **nessun programma di Sanitas, Adeslas, DKV o ASISA trovato** su Awin/Tradedoubler in questo giro; Student Insurance (study-abroad.org) ha un programma di affiliazione ma la commissione non è pubblica. Iscrizione di Massimiliano a IATI: già nella proposta del 31/10 (10 minuti).
- **Wise** (10 £ per cliente nuovo) per chi deve dimostrare i risparmi e spostarli.

### 1.6 Stima
Guadagno ogni 1.000 visite: 4 € prudente (AdSense 1,5 + IATI 2 + Wise 0,5), 7 € centrale, 11 € ottimista (più lettori dalla Spagna, studenti).
- Prudente: 1.500 visite al mese × 12 × 4 € / 1.000 ≈ **70 €**
- Centrale: 5.000 × 12 × 7 € / 1.000 ≈ **420 €**
- Ottimista: 15.000 × 12 × 11 € / 1.000 ≈ **2.000 €**

Prime entrate: AdSense dal primo mese di visite; IATI dopo l'iscrizione. Stagione: visti di studio tra marzo e agosto (inizio dei corsi a settembre), quindi le pagine vanno online entro gennaio 2027.

### 1.7 Ore, motore, rischi
**18-26 ore:** elenco a mano dei ~25 listini consolari (Spagna) con controllo dell'impronta ogni settimana (avviso se il PDF cambia: il 1/10/2026 Bogotá ha già annunciato tariffe nuove), 4 lettori di cambio piccoli (COP, ARS, PEN, CLP; BRL e MXN ci sono già), pagine, testi in due lingue, revisione dei fatti. Il motore di calcolo è quello già usato dalle pagine inglesi (`dati/programmi.json`).

**Rischi:** (1) listini con nomi e formati diversi, alcuni vecchi (Bogotá giugno 2024, Messico gennaio 2025): dove il listino non è dell'anno si scrive la data e si rimanda al consolato; (2) righe ambigue (Messico, Lima): si pubblicano solo quelle che il revisore sa spiegare; (3) pubblicità latinoamericana povera; (4) le pagine `/es/` e `/pt/` del 31/10 hanno ancora 1 visita: **soglia** a 45 giorni dalla pubblicazione di questa sezione: almeno 300 impressioni al mese sulle pagine nuove, altrimenti niente altre nazionalità.

**Voto 7** (domanda 3 · buco 1,5 · fonte 1,5 · chi paga 0,5 · ore e rischi 0,5). Non arriva a 8 perché paga poco e il canale (Google in spagnolo e portoghese) per la rete non è ancora provato.

---

## 2. Tourist Tax in spagnolo e portoghese (voto 6,5, sezione)

**Domanda:** mx/es e es/es "tasa turistica roma" 10 (2026, **hotel 4 estrellas, hotel 3 estrellas**, niños, airbnb, booking, apartamento), "tasa turistica venecia" 10 (dónde se paga, por noche, **agosto 2026**, Mestre), "tasa turistica barcelona" 10 (**2027**, hotel 3/4 estrellas, edad, excepciones), "tasa turistica paris" 10 (por persona, hotel 3/4 estrellas, niños, Disneyland); es/es "tasa turistica lisboa" 4, "amsterdam" 4. br/pt-BR "taxa turistica lisboa" 10 (2026, 4 €, isenção, crianças, quem paga), "barcelona" 9, "roma" 9, "paris" 7, "portugal" 7, "italia" 6; "taxa de acesso veneza" 1.

Le domande sono **per categoria di albergo, età ed esenzioni**: è esattamente quello che il calcolatore di Tourist Tax fa già (65 cartelle nel sito, Roma, Venezia, Barcellona, Parigi, Lisbona, Porto, Amsterdam comprese).

**Prima pagina** ("tasa turística Roma 2026 hotel 4 estrellas"): conociendoitalia, promociones-aereas.com.ar, infoviajera, hosteltur, finestresullarte, idealista; cifre in contrasto (7,50 € contro "fino a 10 €" per 4 e 5 stelle). Nessun calcolatore in spagnolo con la data della fonte.

**Chi paga:** AdSense (Spagna viaggi 3-5 € ogni 1.000 visite, America Latina 1-2 €: stima), Booking/Stay22 dove approvati. **Stima:** 1.500 / 6.000 / 15.000 visite al mese × 12 × 5 / 7 / 11 € ≈ **100 / 500 / 2.000 €** (prudente arrotondato: la base inglese di Tourist Tax oggi fa 20 visite al mese). **Ore 12-18** se fatta insieme alla versione francese già in coda (31/10, voto 6,5): lo stesso lavoro di "lingue" del generatore serve a tre lingue; solo le 12-15 città più cercate, mai tutte.

**Rischio:** Tourist Tax in inglese non è ancora partito su Google (20 visite in 30 giorni): le versioni nuove partono con lo stesso dominio debole. **Voto 6,5.** Soglia: 300 impressioni al mese sulle pagine es/pt a 45 giorni.

---

## 3. Acquisti di cittadinanza per cittadinanza precedente (voto 5, aggiunta)

Eurostat `migr_acq` (API JSON 200, aggiornato il 27/3/2026, dati fino al 2024): per esempio la Spagna per colombiani, venezuelani, marocchini, peruviani. Domanda debole: es/es "nacionalidad española concedidas" 0, en/us "italian citizenship statistics" 0, pt-BR "quantos brasileiros tem cidadania portuguesa" 3. Vale solo come riga in più nelle pagine "Who moved where" (che già leggono Eurostat), per le domande che si fanno agli assistenti AI. 2-4 ore, 20 / 100 / 400 €.

---

## 4. Riserve

### 4.1 Affitti in Spagna: zone tensionate, indice di riferimento, cauzione per comunità (5,5)
- Domanda forte e per Comune: es/es "es zona tensionada" 10 (Madrid, Valencia, Bilbao, Barcelona, **Martorell, Reus**), "zonas tensionadas" 10 (Asturias, Bizkaia, Cataluña 2026), "municipios zona tensionada" 7 (Navarra, Gipuzkoa, "listado"), "indice de referencia alquiler" 10 (2026, Madrid, Bilbao), "fianza alquiler" 10 e "deposito fianza alquiler" 10 (**una per comunità**: Madrid, GVA, Gobierno Vasco, Junta de Andalucía, Xunta, DGA, Castilla-La Mancha); ar/es "requisitos para alquilar en españa siendo extranjero" 10.
- Fonti: `mivau.gob.es` **403** (zone tensionate e sistema di riferimento); `serpavi.mivau.gob.es` 200 ma è un'applicazione; le dichiarazioni sono nel BOE (non provato in questo giro); la cauzione è una legge per comunità (17 fonti).
- Chi paga: AdSense Spagna; "seguro impago alquiler" 10 (Mapfre, Mutua Madrileña, Arag), ma nessun programma di affiliazione letto.
- Pubblico soprattutto spagnolo, non latinoamericano: sarebbe un sito nuovo in spagnolo sotto l'asticella. **Si riapre** se il BOE dà l'elenco dei Comuni in un formato leggibile e si trova un'assicurazione con commissione scritta. Stima 200 / 900 / 3.500 €, 30-40 ore.

### 4.2 Portogallo IFICI ("NHR 2.0") (5)
br/pt-BR "ifici portugal" 10 (requisitos, 2026, eligibility, apply: metà in inglese, quindi espatriati di ogni Paese). Fonte (Portaria con l'elenco delle professioni, Autoridade Tributária) non provata in questo giro; prima pagina di studi legali e consulenti. Al massimo una pagina inglese in Visa Income accanto a D7/D8, dopo la prova della fonte.

---

## 5. NO, con le prove

| Nicchia | Voto | Prove |
|---|---|---|
| **Apostille per Stato USA** (en/es: "apostille birth certificate" 10 con California, Texas, Florida, New York; "how much is an apostille in" 10; us/es "apostillar acta de nacimiento americana" 10 con Texas, California, "en méxico", "doble nacionalidad") | 4,5 | Domanda grande e pubblico USA, ma in prima pagina ci sono già `recordinglaw.com/tools/apostille-finder/` per Stato, `apostilleguideusa.pages.dev` (sito automatico per Stato e documento), `notarygeek.net` con i tempi ufficiali, `internationalapostille.com` per città, apostilletexas.org con i tempi dal 20/4/2026; la fonte è 51 pagine statali diverse; nessun programma di affiliazione trovato. Fatto nuovo rispetto al NO del 10/10 (lista HCCH): il NO resta, per un motivo diverso |
| Apostila de Haia "valor por estado" (Brasile) e apostille per Stato messicano | 4 | br "apostila de haia valor" 10 con SP, RJ, RS, DF, PR, SC, "por estado"; mx "apostillar acta de nacimiento en" 10 (Xalapa, Puebla, CDMX, Oaxaca, Cancún, Toluca, Chihuahua, Guanajuato); ar "apostilla de la haya argentina" 10 (TAD, precio, urgente). Ma 27 tabelle di emolumenti statali o 32 leggi di entrate statali (siti messicani dietro Radware, studio del 30/10), pubblicità brasiliana e messicana bassa, nessun pagatore. Conferma il NO del 26/10 (traduzioni e apostille) |
| Cittadinanza italiana per discendenza in spagnolo e portoghese | 4 | Domanda alta: ar "ciudadania italiana 2026" 10 (precio, tasas, bisnietos, cambios), br "cidadania italiana nova lei" 10 ("pode cair", bisneto, via judicial). Ma la regola è una (L. 74/2025, confermata dalla Consulta a marzo 2026, Cassazione 13818/2026), tassa unica di 600 €, prima pagina piena di "assessorias" e studi legali, nessun programma (avvocati: art. 37 del Codice deontologico); conferma la RISERVA debole del 28/10 |
| Ley de nietos (Spagna) | 3,5 | ar "ley de nietos" 10 ("sigue vigente", "últimas noticias", consolato di Buenos Aires), ma la finestra è chiusa (ottobre 2025): restano lo stato delle pratiche (NO del 31/10) e le notizie |
| Cittadinanza portoghese per i nipoti (LO 1/2026) | 4 | br "cidadania portuguesa para netos" 10 (quanto tempo, valor, 2026), "nova lei" 8; la via dei nipoti resta con la "ligação efetiva" e i requisiti dell'art. 6; domande presentate entro il 18/5/2026 con la legge vecchia. Prima pagina: blog commerciali brasiliani. **Possibile fatto nuovo, non verificato:** un blog scrive che il Consiglio dei ministri ha approvato il 29/10/2026 il decreto che regola la legge (prova di conoscenza): va controllato sul Diário da República; se vero, riapre la RISERVA del 31/10 sul test |
| Doppie imposizioni Spagna-Paese | 4 | co "convenio doble imposicion españa" 10 (USA, Messico, Argentina, Italia…): un PDF per trattato, tema legale, consulenti in pagina |
| Pensioni tra Paesi (convenio iberoamericano, INSS dal Portogallo, IMSS dall'estero, jubilación argentina in Spagna) | 3 | 1-6 suggerimenti per corridoio; solo "convenio multilateral iberoamericano" 10, che è il nome della legge |
| Declaração de Saída Definitiva (Brasile) | 4 | br 10 suggerimenti, ma una regola, Receita Federal su `gov.br` (pagina di blocco agli accessi automatici, studio del 31/10), commercialisti in pagina |
| Voto degli spagnoli all'estero, elezioni generali del 29/11/2026 | 3,5 | Fatto nuovo trovato sulle pagine dei consolati (notizia del 7/10/2026: censo chiuso al 1/8, reclami 12-19/10). Domanda di notizie ("elecciones generales 29 de noviembre" 10, ma su sondaggi e partiti; "votar desde el extranjero" 3), finestra di 25 giorni, tema politico, solo AdSense |
| Affitto in Portogallo dal Brasile ("alugar casa em portugal" 10) | 3 | domanda da annunci (Idealista, Custojusto), nessun numero ufficiale |
| Visto di lavoro per discendenti di italiani | 3 | br "visto de trabalho para descendentes de italianos" 2, ar 0; il decreto flussi è già in ESPLORATE (31/10) |

---

## 6. Cosa ho imparato

1. **Nell'emigrazione latinoamericana la domanda si scrive con la nazionalità** ("para colombianos", "para brasileiros"), e il dato che cambia davvero con la nazionalità è la **tassa del consolato**: gratis per alcuni Paesi per accordo, a reciprocità per altri, sempre in valuta locale. In prima pagina tutti scrivono "circa 80 €". È la forma della sezione rifiuti di Visa Income (numero ufficiale per nazionalità), l'unica della rete che porta visite dagli assistenti AI.
2. **I listini dei consolati spagnoli si leggono** (PDF di testo, 200), ma sono sparsi e con nomi diversi: si fa un elenco a mano e si controlla l'impronta, come per la Thailandia DTV.
3. **Documenti e apostille:** la domanda c'è in tutti i Paesi, ma è locale (Stato per Stato) e senza pagatore; negli USA è già coperta da siti automatici per Stato.
4. **Cittadinanza per discendenza:** dopo le leggi del 2025-2026 la domanda è "posso ancora?" e "quanto costa?": una regola, una tassa, e un mercato di consulenti che non pagano affiliazioni. Non è il nostro terreno.
5. **Casa e soldi:** per gli emigrati le domande forti (affitti in Spagna, imposte) sono le stesse dei residenti, con pubblico spagnolo o portoghese: siti nuovi, non sezioni, e sotto l'asticella.

---

## 7. Fonti principali (lette il 4/11/2026)

- Consolato di Spagna a Bogotá, listino visti: https://www.exteriores.gob.es/DocumentosAuxiliaresSC/Colombia/BOGOT%C3%81%20(C)/TASAS%20DE%20VISADOS%20A%C3%91O%202024%20junio.pdf (200) e notizia "Actualización tasas a partir de 1 de octubre 2026": https://www.exteriores.gob.es/Consulados/bogota/es/Comunicacion/Noticias/Paginas/Articulos/ACTUALIZACI%c3%93N-TASAS-A-PARTIR-DE-1-DE-OCTUBRE-2026.aspx (200)
- Consolato di Buenos Aires, tasas al 1/1/2026: https://www.exteriores.gob.es/Consulados/buenosaires/es/ServiciosConsulares/PublishingImages/Paginas/Tasas-consulares/Hoja%20informativa%20tasas%20consulares%20a%201%20de%20enero%20de%202026.pdf (200)
- Consolato di Santiago del Cile: https://www.exteriores.gob.es/DocumentosAuxiliaresSC/Chile/SANTIAGO%20DE%20CHILE%20(C)/TASAS%20CONSULARES.pdf (200)
- Consolato di Lima: https://www.exteriores.gob.es/DocumentosAuxiliaresSC/Per%c3%ba/LIMA%20%28C%29/Tasas%20consulares%202024.pdf (200)
- Consolato di Città del Messico: https://www.exteriores.gob.es/DocumentosAuxiliaresSC/M%c3%a9xico/M%c3%89XICO%20(C)/VIS/TASAS%20VISADOS%2001.01.25%20ACTUALIZADA.xlsx.pdf (200)
- Consolato di Caracas: https://www.exteriores.gob.es/DocumentosAuxiliaresSC/Venezuela/CARACAS%20%28C%29/Tasas%2001.04.2026.pdf (200)
- MNE Portogallo: https://vistos.mne.gov.pt/pt/vistos-nacionais/informacao-geral/emolumentos , https://vistos.mne.gov.pt/pt/vistos-nacionais/documentacao-instrutoria/procura-de-trabalho , https://vistos.mne.gov.pt/pt/vistos-nacionais/documentacao-instrutoria/meios-de-subsistencia (200)
- Cambi: https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml ; https://www.datos.gov.co/resource/32sa-8pi3.json ; https://api.bcra.gob.ar/estadisticascambiarias/v1.0/Cotizaciones ; https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04640PD/json ; https://www.sii.cl/valores_y_fechas/dolar/dolar2026.htm (tutti 200)
- IATI ES su Tradedoubler: https://directory.tradedoubler.com/en/programs/403039-IATI-ES (10 %, cookie 7 giorni)
- Eurostat `migr_acq`: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/migr_acq (200)
- Fonti chiuse: `mivau.gob.es` 403; consolato spagnolo di San Paolo in portoghese 401; Banxico (serve un token)
- Prima pagina: ricerche web dagli USA del 4/11/2026 (visaatlas.org, visago.dev, costaluzlawyers.com, migratiolex.com, studyineurope.eu, study-abroad.org, recordinglaw.com, apostilleguideusa.pages.dev, notarygeek.net, conociendoitalia.com, infoviajera.com, cidadaniaevisto.com.br)
