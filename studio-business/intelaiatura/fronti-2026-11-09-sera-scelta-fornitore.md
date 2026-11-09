# Fronte mai toccato: scegliere il fornitore nei mercati regolati (luce negli USA, sanità privata e servizi alle famiglie in Australia, ricarica auto nel Regno Unito) (9/11/2026, sera)

Angolo del compito: un settore dove (1) il dato chiave lo pubblica un ente pubblico o neutrale e si legge con curl, (2) chi paga NON è anche chi pubblica la risposta, (3) la domanda cresce adesso. Lezione di oggi: nel software per piccole imprese chi paga è anche il concorrente; nel collezionismo chi ha i dati chiude il server.

Controllato prima su ESPLORATE.md (parole chiave energia, bollette, tariff, price cap, hospital, waiting, dentist, childcare, school, EV, charging, MOT, emission): già esclusi il tetto Ofgem (MoneySavingExpert primo), i piani luce australiani e la DMO (billhero per codice postale, voto 5), gli aumenti delle bollette per azienda elettrica USA (voto 5, 50 commissioni senza file unico), le tariffe di rete tedesche, il salderingsregeling, le liste d'attesa NHS, irlandesi e canadesi, i dentisti NHS, le zone a basse emissioni, il MOT. **Nuovo qui:** il "Price to Compare" (il prezzo del servizio di base che il cittadino confronta con le offerte) negli Stati USA con libera scelta del fornitore, le assicurazioni sanitarie private australiane (sovrattassa Medicare e caricamento Lifetime Health Cover), il sussidio per i nidi in Australia (garanzia dei 3 giorni dal 2026), i prezzi della ricarica pubblica nel Regno Unito.

## Fonti esterne lette con curl il 9/11/2026

- **papowerswitch.com** (sito ufficiale della commissione della Pennsylvania): home 200; la pagina dei risultati per codice postale `shop-for-rates-results/?zip=18101&serviceType=residential` risponde **200** con una normale richiesta: "Current Price to Compare for 18101 – PPL Electric Utilities – RS Regular Residential Service **$0.13079 per kWh**", con le offerte dei fornitori (885 KB). La home carica uno script anti-robot, che non è stato toccato: la pagina dei risultati risponde senza.
- **energychoice.ohio.gov** (commissione dell'Ohio, tabella "apples to apples"): 200, 718 KB: "Ohio Power Company's (formerly AEP Ohio) residential Price to Compare for the period of **October 1, 2026 through December 31, 2026 is $0.1019/kWh**", 131 offerte a prezzo fisso, una trentina di fornitori. In Ohio il prezzo cambia ogni trimestre.
- **plugin.illinois.gov** (commissione dell'Illinois): 200. "The ComEd Price to Compare effective October 1, 2026 is **10.103 cents per kWh**" (fino al 31/5/2027); pagine ufficiali "Historical Prices to Compare" in PDF ed Excel (pagina 200, file non scaricato).
- **energyswitchma.gov** (Massachusetts) 200; **energizect.com** (Connecticut) 403, non aggirato; siti di New Jersey e Maryland: 301 verso nuovi indirizzi (non seguiti per budget); **puc.pa.gov** sezione elettricità 200, comunicati 404 all'indirizzo provato.
- **Chi paga nella luce USA** (pagine lette):
  - **electricityrates.com/affiliate-program/**: 200, programma su Impact: "Affiliates can earn a **competitive commission** for every new customer they enroll", **nessuna cifra**. Lo stesso sito pubblica le pagine "ppl electric" e "ppl electric rate increase june 2026": è pagatore e concorrente insieme.
  - **energybot.com/partners/channel-partners.html**: 200, "Earn commissions when customers sign up for an energy plan", pagamento mensile, link affiliato; **nessuna cifra**. Anche EnergyBot pubblica le pagine per azienda elettrica.
  - **affiliate.comparepower.com/agreement** (Texas): 200, contratto completo; le cifre stanno nel "Compensation Schedule" del portale, dietro login. **Nessuna cifra pubblica.**
  - **ui.awin.com/merchant-profile/68048, SmartEnergy** (fornitore di luce, non comparatore): 200. Programma nuovo "a lead" (CPL) con concorso "un anno di luce gratis fino a 1.500 $", **solo Delaware, Massachusetts, Maine, New Hampshire, New Jersey, Ohio, Pennsylvania**, proprietari di casa sopra i 35 anni; "clear path toward a CPA". Cifra **non pubblica**. È l'unico pagatore trovato che non pubblica anche le risposte.
  - **firstenergycorp.com, Customer Referral Program (Pennsylvania)**: 200. Prezzo fisso per 12 mesi al **7 % sotto il Price to Compare**; ogni iscrizione accettata costa al fornitore **30,00 $**. Non è un programma per editori: è il valore minimo di un cliente per un fornitore.
  - **chooseenergy.com/affiliates/** (Red Ventures): 200, pagina di atterraggio per i clienti Capital One con "**$100 reward**" a ordine completato. Indica che un ordine vale almeno 100 $ per il comparatore; nessun programma aperto agli editori letto.
  - Non trovati o 404: CleanChoice, Inspire, Rhythm, Energy Ogre, Arcadia (pagine affiliati); FlexOffers 429 (anti-robot, non aggirato); Impact pagine pubbliche dei marchi 404.
- **Sanità e famiglie in Australia**:
  - **myhospitalsapi.aihw.gov.au** (tempi d'attesa per ospedale): **403** su due indirizzi; **aihw.gov.au** e **bhi.nsw.gov.au**: pagina anti-robot (403), non aggirata; **health.gov.au** (aumenti dei premi per assicuratore): nessuna risposta (000).
  - **privatehealth.gov.au** (confronto ufficiale di tutte le polizze, del Commonwealth Ombudsman): 200.
  - **Compare the Market, pagina "How do we make money?"** (ctm-everpress-static-site.pages.dev/health-insurance/disclosures/): 200. "Our standard fee is split into two instalments: **25 % of the first year premium**, paid upfront; and **6 % of the second year premium**". È quanto i fondi pagano al comparatore; nessun programma per editori.
  - **australianunity.com.au/health-insurance/affiliate/amway**: solo punti Amway, nessuna cifra in denaro.

## Autocomplete Google (numero di suggerimenti)

| Paese | Domanda | N | Note |
|---|---|---|---|
| US | price to compare | 10 | ppl, electric pa, ohio, met ed, comed, default service |
| US | ppl price to compare | 10 | **2026, history, june 2026, december 2026**, december 2025 |
| US | peco price to compare | 10 | history, june 2026, 2026, gas |
| US | comed price to compare | 10 | **october 2026**, june 2026, historical |
| US | pseg price to compare | 10 | 2026, gas, nj |
| US | aep ohio price to compare | 5 | june 2026 |
| US | bge price to compare | 5 | |
| US | eversource standard service rate | 7 | **2026, 2027**, ct |
| US | national grid supply rate | 10 | massachusetts, increase, upstate ny |
| US | price to compare june 2026 | 2 | |
| US | electric supplier | 10 | in pa, ohio, ct, ma, rates |
| US | should i switch electric supplier | 10 | "now or wait" (in parte Regno Unito) |
| US | electric rates going up / electric bill going up | 10 / 10 | **in pa, ohio, nj, texas; "2026"; "because of data centers"; virginia** |
| US | papowerswitch / energy choice ohio | 10 / 10 | ricerche di navigazione verso i siti ufficiali |
| AU | elective surgery waiting times / public hospital waiting list | 10 / 10 | per Stato, aihw |
| AU | hip / knee replacement waiting list, cataract surgery waiting list | 10 ciascuna | metà dei suggerimenti sono UK, Irlanda, NZ |
| AU | private health insurance premium increase | 10 | 2026, by state, medibank, "will ... increase in 2026" |
| AU | is private health insurance worth it | 10 | pensioners, pregnancy, **calculator**, reddit |
| AU | medicare levy surcharge | 10 | **threshold 2026, 2027**, calculator, exemption |
| AU | lifetime health cover loading | 10 | **calculator**, exemption, couples |
| AU | default market offer 2026 | 3 | 2026-27, aer |
| AU | child care subsidy calculator / childcare subsidy 3 day guarantee | 10 / 9 | per Stato, 2026, centrelink, eligibility |
| GB | public ev charging prices / ev charging cost per kwh | 10 / 10 | uk map, calculator; metà dei suggerimenti sono India |

Composizione dei risultati di Google: non letta direttamente (nessuna pagina dei risultati leggibile dal server). Una ricerca web su "PPL price to compare history December 2026" restituisce **electricityrates.com** (pagina PPL con lo storico del Price to Compare: 10,77 ¢ dic 2024-mag 2025, 12,49 ¢ giu-nov 2025, 12,95 ¢ dic 2025-mag 2026, 13,14 ¢ giugno 2026, 13,08 ¢ luglio-novembre 2026) e il suo articolo "ppl electric rate increase june 2026"; il resto sono pagine di borsa (PPL è anche un titolo). Il valore ufficiale letto oggi (13,079 ¢) coincide con quello del concorrente.

---

## 0. Risposta in breve

| # | Idea | Fonte esterna da cui nasce | Chi paga (cifra letta) | €/anno a 18 mesi prudente / centrale / ottimista | Ore | Voto |
|---|---|---|---|---|---|---|
| 1 | **Price to Compare per ogni azienda elettrica USA a libera scelta, con storico, prossima data di cambio e "conviene cambiare?"** (PA, OH, IL, NJ, MD, MA, CT, NY, DE, NH, ME) | autocomplete USA (10 su "price to compare" e per azienda, con "history", "june/december 2026", "october 2026"; "electric bill going up 2026", "because of data centers"); pagine ufficiali PA, OH, IL lette | SmartEnergy su Awin (CPL, cifra non pubblica); ElectricityRates su Impact ed EnergyBot (commissione senza cifra); valore di un cliente: 30 $ (FirstEnergy, letto), ≥ 100 $ (Choose Energy → Capital One, letto) | 250 / **2.600** / 12.000 | 30-40 agenti + 15 min ogni cambio di semestre di Massimiliano (iscrizioni) | **5,5** |
| 2 | Assicurazione sanitaria privata in Australia: sovrattassa Medicare 2026-27, caricamento Lifetime Health Cover, "conviene?" con calcolatore | autocomplete AU (10 su "medicare levy surcharge threshold 2026/2027", "lifetime health cover loading calculator", "is private health insurance worth it calculator") | i fondi pagano ai comparatori il **25 % del premio del 1° anno + 6 % del 2°** (Compare the Market, letto), ma nessun programma per editori trovato | 100 / **700** / 4.000 | 20-30 | **4** |
| 3 | Tempi d'attesa negli ospedali pubblici australiani per Stato e intervento, con "pubblico o privato?" | autocomplete AU (10 su "public hospital waiting list", "elective surgery waiting times") | come la 2 (nessuna cifra per editori) | 0 / **300** / 2.000 | 25-35 | **3,5** |

**Nessuna idea arriva a 8 e nessuna passa l'asticella del sito nuovo** (voto ≥ 7 e ≥ 5.000 €/anno centrali). L'idea 1 ha un ottimista ≥ 10.000 € (12.000 €) e la domanda in crescita più chiara della giornata, ma fallisce il criterio (2): i programmi che pagano per la luce USA sono quasi tutti di comparatori (ElectricityRates, EnergyBot, ComparePower, Choose Energy) che pubblicano già le stesse pagine per azienda elettrica, e nessuno mostra la cifra. L'unico pagatore "puro" (un fornitore, SmartEnergy) è un programma a lead appena lanciato, con cifra visibile solo dopo l'iscrizione.

---

## 1. Price to Compare per azienda elettrica (USA, Stati a libera scelta) — voto 5,5

**Fonte esterna:** autocomplete USA. "price to compare" ha 10 suggerimenti e ogni azienda elettrica grande ha la sua serie da 10 (PPL, PECO, ComEd, PSEG; AEP Ohio e BGE 5). Le forme con la data ("ppl price to compare december 2026", "comed price to compare october 2026", "eversource standard service rate 2027") e con "history" mostrano che la gente cerca il numero nuovo e il confronto con il passato. Accanto, la domanda di fondo cresce: "electric bill going up 2026", "electric bills going up because of data centers", "electric rates going up in pa / ohio / nj". Il motivo è reale e datato: le aste di capacità della rete PJM hanno alzato i prezzi dal giugno 2025 e dal giugno 2026 (PPL da 10,77 ¢ a 13,08 ¢ in diciotto mesi, +21 %).

**Il nostro modo:** una pagina per azienda elettrica (circa 40-50 tra PA, OH, IL, NJ, MD, DE, DC, MA, CT, NY, NH, ME) con: Price to Compare di oggi (cifra, periodo, fonte ufficiale e data), storico in tabella e grafico, **prossima data di cambio** (PA 1/6 e 1/12, Ohio ogni trimestre, ComEd 1/6 e 1/10, CT 1/1 e 1/7), quanto costa in un mese a 700/1.000 kWh, e "conviene cambiare?": quante offerte fisse sono sotto il prezzo oggi (dalla tabella ufficiale), con i rischi (prezzi variabili, penali). Un riepilogo nazionale "price to compare per Stato" con le date dei prossimi cambi. È il formato che gli assistenti AI citano: un numero ufficiale, una data, una fonte.

**Dati ufficiali:** buoni dove letti. Pennsylvania: pagina dei risultati per codice postale 200 (PTC e offerte); Ohio: tabella "apples to apples" 200 con il PTC del trimestre e 131 offerte fisse; Illinois: PTC di ComEd 200 e storico ufficiale in Excel/PDF. Massachusetts 200. Connecticut 403 (il dato "standard service" si prenderebbe dai comunicati delle aziende). New Jersey e Maryland da riverificare (indirizzi cambiati). Lo storico si costruisce dalle fonti ufficiali dove esiste (Illinois) e, per gli altri Stati, dai valori raccolti a ogni cambio: all'inizio lo storico sarà più corto di quello di electricityrates.com.

**Chi paga:**
- **SmartEnergy su Awin** (fornitore, non comparatore): programma CPL in DE, MA, ME, NH, NJ, OH, PA, proprio gli Stati del sito; cifra non pubblica, passaggio a CPA "per chi porta qualità". Massimiliano ha già Awin: l'iscrizione costa 0 €.
- **ElectricityRates.com su Impact** e **EnergyBot** (link affiliato, pagamento mensile): commissione "competitiva" senza cifra; sono anche concorrenti diretti sulle stesse pagine.
- **Valore di un cliente** letto su pagine pubbliche: 30 $ per iscrizione nel programma di FirstEnergy in Pennsylvania; 100 $ di premio Capital One per un ordine su Choose Energy. Ipotesi di lavoro per la stima: 25-40 € a iscrizione accettata, **non letta su un programma per editori**.
- **AdSense**: energia e bollette USA hanno annunci di comparatori e fornitori (cifra non letta; stima 8-12 € ogni 1.000 visite).

**Concorrenti:** electricityrates.com (pagina PPL con lo storico, articoli sugli aumenti), EnergyBot, Choose Energy e SaveOnEnergy (Red Ventures), findenergy.com, i siti ufficiali (PAPowerSwitch ed Energy Choice Ohio compaiono nell'autocomplete), le aziende elettriche stesse. Il buco non è "nessuno ha il numero": è "nessuno ha tutti gli Stati con le date dei prossimi cambi in una tabella neutrale". È un buco più stretto di quelli che hanno funzionato (EsameB1, Visa Income).

**Stima a 18 mesi (maggio 2028).** Visite: prudente 2.000/mese, centrale 8.000, ottimista 30.000 (i picchi sono due volte l'anno, a giugno e dicembre, più gli annunci delle aste PJM).
- Prudente: nessun programma accetta il sito, solo AdSense a 10 €/1.000 → **250 €**.
- Centrale: AdSense 8.000 × 12 × 10 € / 1.000 = 960 €; affiliazione accettata (SmartEnergy o ElectricityRates), 0,15 % delle visite diventa un'iscrizione accettata a 30 € → 144 × 30 = 4.300 €, con probabilità di approvazione e mantenimento circa 40 % → 1.700 €; totale **circa 2.600 €**.
- Ottimista: 30.000 visite, AdSense 3.600 € + 0,25 % a 35 € = 9.400 € → **circa 12.000 €** (ottimista ≥ 10.000 €, da segnalare).

**Ore:** 30-40 di agenti (raccolta da 8-11 fonti statali, 40-50 pagine, grafici, revisione dei fatti e del design); aggiornamento automatico dove la fonte si legge (PA, OH, IL, MA), a mano per CT e per i comunicati; Massimiliano 15 minuti per l'iscrizione ai programmi (Awin già aperto, Impact da aprire) e la pubblicazione su Netlify.

**Rischi:**
- **Licenze:** in Pennsylvania e in Ohio chi "vende" o procura contratti di luce deve avere una licenza di broker dalla commissione statale. Un link affiliato verso un comparatore con licenza di solito basta, ma va letto il contratto del programma prima di accendere i link (non letto stasera).
- Pagatore e concorrente coincidono (ElectricityRates, EnergyBot): possono rifiutare l'iscrizione o pagare poco.
- Il cambio di fornitore negli USA ha una cattiva fama (truffe porta a porta, prezzi variabili): la pagina deve restare neutrale e dire quando NON conviene, il che abbassa le conversioni.
- Stati in cui il Price to Compare sale molto (PA, NJ, MD) = domanda alta ma offerte fisse spesso vicine al prezzo base: il risparmio mostrato può essere piccolo.
- Nessun nostro sito ha questo pubblico: servirebbe un sito nuovo, sotto l'asticella dei 5.000 €.

**Dove va:** RISERVA ALTA. Non si costruisce come sito nuovo (2.600 € centrali, voto 5,5). Si riapre e si passa al verificatore se, entro marzo 2027 (prima del cambio del 1/6/2027, il picco di domanda): (a) SmartEnergy su Awin mostra una cifra ≥ 15 $ a lead o ≥ 40 $ a cliente dopo l'iscrizione di Massimiliano, **oppure** (b) un fornitore grande (Constellation, CleanChoice, Direct Energy) apre un programma con cifra pubblica su una rete. Con (a) o (b) la stima centrale sale sopra i 5.000 € e il voto a 7.

## 2. Assicurazione sanitaria privata in Australia (sovrattassa Medicare, Lifetime Health Cover, "conviene?") — voto 4

**Fonte esterna:** autocomplete AU: 10 suggerimenti su "medicare levy surcharge" (con "threshold 2026", "threshold 2027", "calculator", "exemption"), su "lifetime health cover loading" (con "calculator", "couples") e su "is private health insurance worth it" (con "calculator", "pensioners", "pregnancy"). Ogni aprile i premi salgono (autocomplete "private health insurance premium increase 2026", "by state", "medibank").

**Il nostro modo:** un calcolatore "quanto mi costa NON avere l'assicurazione privata": sovrattassa Medicare per reddito (soglie ufficiali dell'anno), caricamento Lifetime Health Cover per età (2 % per anno dopo i 31), confronto con la polizza ospedaliera più economica che evita la sovrattassa (da privatehealth.gov.au).

**Dati ufficiali:** privatehealth.gov.au 200 (polizze); le soglie stanno sul sito delle entrate australiane (non provato stasera); gli aumenti dei premi per assicuratore stanno su health.gov.au, che **non risponde** dal server.

**Chi paga:** i fondi sanitari pagano i comparatori molto bene (**25 % del premio del primo anno + 6 % del secondo**, letto sulla pagina di Compare the Market), ma nessun programma per editori con cifra trovato (Australian Unity solo punti Amway). I comparatori (Compare the Market, iSelect, Canstar, finder) sono anche i primi editori delle risposte: stesso errore del software per piccole imprese.

**Stima a 18 mesi:** solo AdSense australiano (8-12 € ogni 1.000 visite, stima): prudente 100 €, centrale **700 €** (6.000 visite/mese), ottimista 4.000 €. Ore 20-30. Rischi: tema "soldi e salute" (YMYL), comparatori molto forti, nessun pagatore.

**Dove va:** NO. Si riapre solo se un fondo sanitario (nib, ahm, HCF, Bupa) apre un programma per editori con cifra pubblica.

## 3. Tempi d'attesa negli ospedali pubblici australiani, con "pubblico o privato?" — voto 3,5

**Fonte esterna:** autocomplete AU: 10 su "public hospital waiting list" (vic, wa, nsw, "for hip replacement") e su "elective surgery waiting times" (aihw, qld, nsw, victoria); 10 su "how long is the waiting list for" con "cataract surgery" e "knee replacement".

**Dati ufficiali:** **bloccati**. API MyHospitals dell'AIHW 403, aihw.gov.au e bhi.nsw.gov.au con pagina anti-robot (403), health.gov.au senza risposta. Non aggirati. Senza dati leggibili dal server il sito non si aggiorna.

**Chi paga:** come l'idea 2 (nessun programma per editori). In più le liste d'attesa sono già state bocciate nel Regno Unito, in Irlanda e in Canada (ESPLORATE.md): stessa famiglia.

**Stima:** 0 / **300** / 2.000 €. **Dove va:** NO.

## 4. Altre nicchie del fronte, scartate subito

| Nicchia | Prova | Voto |
|---|---|---|
| Sussidio per i nidi in Australia e "garanzia dei 3 giorni" (dal 2026) | "child care subsidy calculator" 10 (per Stato, 2026, centrelink), "childcare subsidy 3 day guarantee" 9; c'è un calcolatore ufficiale di Services Australia (non provato) e nessun pagatore trovato per i nidi | 3 |
| Prezzi della ricarica pubblica per auto elettriche (Regno Unito) | "public ev charging prices" 10 (uk map, calculator), "ev charging cost per kwh" 10 ma metà indiani; Zapmap fa già mappa e prezzi; nessun pagatore letto (non approfondita) | 3,5 |
| Default Market Offer e VDO 2026-27 (Australia) | "default market offer 2026" 3 suggerimenti; già bocciata il 30/10 (billhero, voto 5) | — |
| Standard service di Eversource e "supply rate" di National Grid (CT, MA, NY) | 7 e 10 suggerimenti; entra nell'idea 1 come pagine per azienda, non è un'idea a parte (Connecticut 403) | — |

---

## 5. Lezione del fronte

Nei mercati dove il cittadino sceglie il fornitore (luce USA, assicurazione sanitaria australiana) il dato ufficiale c'è ed è spesso leggibile (Pennsylvania, Ohio, Illinois, privatehealth.gov.au) e la domanda sale davvero (bollette USA +21 % in 18 mesi per PPL, "because of data centers"). Ma il denaro passa quasi tutto dai **comparatori**, che sono anche i primi editori delle risposte e non mostrano le cifre: la stessa trappola del software per piccole imprese, in forma più leggera. Il pagatore "puro" esiste solo dove un **fornitore** compra clienti direttamente su una rete (SmartEnergy su Awin, nuovo e senza cifra pubblica). Regola pratica per i prossimi fronti: cercare prima, sulle reti (Awin, Impact, CJ), i **fornitori** che comprano clienti con una cifra pubblica, e solo dopo il dato ufficiale che porta quei clienti; se il pagatore con cifra è solo un comparatore, il voto non supera 5,5.

Azione a costo zero che non richiede decisioni: quando Massimiliano entra in Awin per altri motivi, può chiedere l'iscrizione a SmartEnergy (ID 68048) solo per leggere la cifra; se è ≥ 15 $ a lead, l'idea 1 va al verificatore.
