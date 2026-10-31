# Verifica indipendente del 31/10/2026: "US Small Business by State" (idea 1A + 1B di `fronti-2026-10-31-nicchie-ricche.md`)

**Compito.** Provare a smontare l'idea proposta come sito nuovo: costi e scadenze delle LLC Stato per Stato (1A) + obblighi del datore di lavoro Stato per Stato (1B). Stima del ricercatore: voto 6,5, **1.450 / 17.900 / 97.200 €/anno** a 18 mesi, 60-85 ore. Asticella per un sito nuovo (skill `rete-siti`, regola del 17/10): voto ≥ 7 e ≥ 5.000 €/anno nella stima centrale.

**Prove, tutte del 31/10/2026, dal nostro server:** Google Autocomplete (`suggestqueries.google.com`, `client=firefox`, `hl=en gl=us`); Google Search (bloccato: risponde con una pagina di reindirizzamento, 0 risultati); Bing dal server (risponde, ma per 7 ricerche su 10 dà risultati senza senso: dizionari, Facebook, notiziari; usato solo per le 3 buone); ricerca web con motore di risposta dagli USA (10 ricerche: serve sia come prima pagina sia come prova di quali fonti citano gli assistenti); `curl` su 25 pagine ufficiali degli Stati e sulle pagine dei programmi di affiliazione (Northwest, ZenBusiness su Awin, Gusto su PartnerStack); i numeri veri della rete dal `CRUSCOTTO-RETE.md`. Cambio 1 $ = 0,92 € come nel file originale.

---

## 0. Risposta in breve

**NO come sito nuovo. Voto severo: 4,5/10. Stima ricalcolata: 210 / 1.370 / 12.700 €/anno** (contro 1.450 / 17.900 / 97.200). La stima centrale cade di 13 volte per tre motivi con prove: (1) la coda lunga "libera" non esiste: per ogni ricerca di Stato piccolo ci sono già 5-8 siti, metà dei quali automatici e già con "2026" e "verificato" nel titolo; (2) la conversione 0,5 % viene dal "12-15 %" che Northwest scrive sulla propria pagina pubblicitaria, riferito a "pagine di atterraggio su misura" di "editori di contenuti di alta gamma", non a pagine informative sulle tariffe; con i parametri di settore (clic 2 %, vendita sul clic 3-5 %) si arriva a 0,06-0,10 %; (3) le fonti ufficiali non sono leggibili in automatico: **15 pagine su 25 provate oggi non si leggono dal server** (403, 404 o connessione chiusa), quindi l'aggiornamento mensile di 51 Stati × 8 argomenti sarebbe lavoro a mano, non automatico, in una nicchia dove un numero sbagliato fa sciogliere la società del lettore. Si aggiunge un vincolo di accesso: i programmi Awin sono "ZenBusiness (US)" e "Northwest… (US)", approvazione a mano "in circa una settimana", su un sito nuovo in `.netlify.app` senza autore né storia; senza quell'approvazione il sito rende solo pubblicità (≈ 350 € centrali).

---

## 1. Domanda: c'è, ma è dominata e già servita

### 1.1 Autocomplete USA (gl=us), le 7 famiglie di 1A e le 5 di 1B
Confermo i numeri del ricercatore: tutte le 7 famiglie di 1A danno 10 varianti con Stati ("llc annual fee" → by state, california, illinois, texas, nj, virginia, nc, florida, new york; "how much does it cost to start an llc in" → texas, florida, california, pa, illinois, north carolina, michigan, ohio, indiana, georgia; "reinstate llc" → texas, georgia, florida, illinois, nc, tennessee, nj; "how to dissolve an llc in" → 10 Stati). Per 1B: "new employer sui rate" 10 (by state 2026, massachusetts, florida, colorado, louisiana), "unemployment tax rate for new employers" 10 Stati, "new hire reporting" 10 Stati. Però "how to register as an employer in" dà 10 voci di cui **solo 2 USA** (california, florida): le altre sono Filippine (sss, philhealth, pag ibig), Irlanda, Kenya (sha), Indeed. La famiglia "registrazione del datore di lavoro" è più piccola di quanto scritto.

### 1.2 La coda lunga: gli Stati piccoli
Ho provato dove dovrebbe stare il nostro spazio ("rapporto annuale di uno Stato piccolo, riattivazione, multa per il ritardo"):
- "llc annual fee vermont" 6 varianti, "south dakota" 5, "annual report fee north dakota" 6, "reinstate llc idaho" 5 (di cui 3 su Louisiana e Delaware, cioè Google non ha abbastanza ricerche su Idaho e completa con altri Stati), **"reinstate llc vermont" 0**, "how to dissolve an llc in montana" 4, **"new employer sui rate wyoming" 0**, "new employer unemployment rate alaska" 1.
- Lettura: la domanda per gli Stati piccoli è sottile; la domanda vera è concentrata su 10-12 Stati grandi (Texas, California, Florida, Georgia, Illinois, NC, NJ, NY, PA, Ohio), dove ci sono i marchi.

### 1.3 Quanto traffico può prendere un sito nuovo senza link in 18 mesi
Numeri veri della nostra rete (cruscotto, letti oggi):
- Il miglior sito della rete, EsameB1 (nicchia italiana quasi senza concorrenti), dopo 3 settimane fa 189 visite a settimana (~800 al mese) con posizione media 7,3.
- I due siti USA in inglese per un pubblico ricco, **FloodCost e ApprovedCondos: 0 visite** dopo 2 settimane. Before You Fly: 2.610 impressioni e 3 clic in 28 giorni (posizione media 42,7: Google lo mostra ma a pagina 4-5). Italy Strikes: 0 pagine indicizzate dopo 13 giorni, causa scritta nel cruscotto: "sito nuovo su indirizzo gratuito senza nessun link in entrata".
- Un terzo delle visite della rete arriva da ChatGPT (62 su ~180 nella settimana 19-26/10), ma tutte su Visa Income, cioè su tabelle che **nessun sito forte aveva** (rifiuti dei visti per nazionalità). Qui non è così (sez. 2.3).

Contesto 2024-2026 (fonti terze, non di Google): lo studio Ahrefs su ~300.000 parole chiave (dicembre 2023 → dicembre 2025) stima che su 100 clic che prima andavano ai siti in testa, Google ne trattiene 58; Pew: con una risposta AI il risultato tradizionale prende l'8 % dei clic invece del 15 %; sul core update di marzo 2026 un tracker (JetDigitalPro) dice che il 71 % dei siti di affiliazione ha perso posizioni. Sono numeri di venditori, non di Google, ma la direzione è una sola: le pagine "quanto costa X in Y" con riquadro affiliato, senza autore e senza marchio, sono il profilo che perde di più. E per le ricerche "llc annual fee texas" la risposta AI di Google dà la cifra direttamente, senza clic.

**Traffico realistico al mese 18** (sito nuovo, `.netlify.app`, nessun link, 700 pagine): prudente 150 visite/mese, centrale 600, ottimista 2.000 per il blocco A; 100 / 400 / 1.500 per il blocco B. Il ricercatore aveva 300 / 1.500 / 5.000 per ciascun blocco: nessun sito USA della rete oggi è vicino neanche al prudente.

---

## 2. Concorrenza: la prima pagina e la coda lunga sono già piene

### 2.1 Prima pagina per 10 ricerche tipiche (ricerca web dagli USA; Bing solo dove rispondeva bene)
| Ricerca | Chi c'è (ordine di comparsa) | Siti automatici già presenti |
|---|---|---|
| llc annual fee wyoming | LLC University (2 pagine), zenind (3 pagine "2026 Guide"), UpCounsel, howtostartanllc, ZenBusiness, bizreport, statebusinesscompliance ("2026"), ezel.ai, file.business | zenind, statebusinesscompliance, ezel.ai, file.business |
| vermont llc annual report fee | zenind (3), businessanywhere ("$45 Fee, Due Date"), UpCounsel, LLC University (2), getpalm, howtostartanllc, ZenBusiness, commenda, tailorbrands, bizee, ezel.ai, file.business | zenind, businessanywhere, ezel.ai, file.business |
| reinstate llc georgia | UpCounsel, llcbuddy, zenind (2), **Northwest** (2), wyomingllcattorney, Harbor Compliance, legalclarity, discern, statebusinesscompliance (2), file.business (2), businessanywhere, Rocket Lawyer, ZenBusiness help | zenind, statebusinesscompliance, file.business, businessanywhere |
| annual report fee north carolina llc | zenind (2), businessanywhere ("$200 Fee, April 15 Deadline"), statebusinesscompliance (2), corpnet, LegalZoom, sosnc.gov, LLC University, discern, ezel.ai, startbusinessbystate, file.business (2) | zenind, businessanywhere, statebusinesscompliance, ezel.ai, file.business |
| llc annual fees by state 2026 | LLC University (6 varianti), howtostartanllc, Inc Authority, llc-formation.pages.dev, businessglobalizer, terms.law, statebusinesscompliance, startbusinessbystate | llc-formation.pages.dev, statebusinesscompliance |
| how much does it cost to start an llc in texas (Bing) | LLC University, 1800accountant, tailorbrands, venturesmarter, texaslegal.guide, LegalZoom, corporationstx ("2026"), texasanswers, creditdonkey, UpCounsel | – |
| registered agent in florida (Bing) | **Northwest**, entityfiling, Forbes, LegalZoom, venturesmarter, florida-incorporations, registeredagentsinc, 2 siti dedicati alla Florida, **ZenBusiness** | – |
| new employer sui rate massachusetts 2026 | OnPay, Eddy (2), warp, Paylocity (4), **EY taxnews**, Patriot, beancount.io, hireborderless, timetrex, Ballotpedia, teamed.global | beancount, teamed |
| how to register as an employer in california | plane, zenind, remote.com, hibou, calpia (PDF), Indeed, lacity.gov, Patriot (2), **EDD** (3 pagine), eddy, ontheclock | zenind |
| llc annual fee + dissolve (Bing) | Bing dal server dà risultati senza senso: non usabili | – |

Cosa dice la tabella: (1) in testa ci sono i **pagatori stessi** (Northwest, ZenBusiness, LegalZoom) e LLC University, che Semrush stimava a **250-290.000 visite al mese** già a metà 2025; (2) la "coda lunga" degli Stati piccoli è già coperta da **almeno 6 siti automatici** con una pagina per Stato e per argomento, con il numero e la scadenza già nel titolo e "2026" già scritto (zenind, statebusinesscompliance, businessanywhere, file.business, ezel.ai, llc-formation.pages.dev): è esattamente il formato che il ricercatore propone come vantaggio; (3) per il blocco B la prima pagina è di società delle paghe (OnPay, Paylocity, Eddy, Patriot) e degli enti stessi (EDD, DUA), più EY.

### 2.2 Coda lunga "davvero libera"
Nessuna delle 10 ricerche ha meno di 10 risultati pertinenti. Le uniche pagine senza concorrente diretto sono quelle che **non hanno domanda** ("reinstate llc vermont" 0, "new employer sui rate wyoming" 0). Spazio libero = spazio senza ricerche.

### 2.3 Gli assistenti AI citano già fonti forti?
Sì. Il motore di risposta usato per le 10 ricerche (dagli USA) ha costruito ogni risposta citando LLC University, zenind, statebusinesscompliance, businessanywhere, UpCounsel, OnPay, Eddy, Paylocity, EY, Patriot, EDD. Non ho accesso diretto a ChatGPT dal server: è una prova indiretta, ma coerente. Il vantaggio "fonte ufficiale + data" che ha funzionato su Visa Income qui non è nostro: zenind e statebusinesscompliance mettono già "2026" e "last updated" in ogni pagina. La contraddizione tra fonti esiste davvero (Massachusetts nuovi datori 2,13 % o 2,42 % per il 2026; Vermont 35 o 45 $; NC multa 0 o 100 $; Delaware 300 → 400 $ con due letture diverse dell'anno), ma gli assistenti la risolvono già scegliendo la fonte più recente, non cercando un sito nuovo.

---

## 3. Pagatori: cifre vere, condizioni non verificabili dall'esterno, conversione gonfiata

### 3.1 Cosa ho letto oggi sulle pagine ufficiali
- **Northwest Registered Agent** (`northwestregisteredagent.com/affiliate-program`, 200; profilo Awin `ui.awin.com/merchant-profile/66946`, 200): "$100 per signup for registered agent services, $150 per signup for business formation"; cookie 30 giorni; "Once we've approved your application (it takes about a week)"; la frase sul 12-15 % è: "We build **custom landing pages** for many website owners and **publishers of high-end content** to deliver the highest conversion rates in the industry. Our publishers' conversion rates average from 12-15%". Cioè: conversione dei clic sulle pagine di atterraggio dei grandi editori (siti di recensioni "best registered agent"), non delle pagine informative. La pagina dei termini del programma su Awin (`merchant-profile-terms/66946`) è 404 senza login. Divieti noti da fonti terze: niente annunci sui marchi, niente "coupon".
- **ZenBusiness** (`zenbusiness.com/affiliate-program/`, 200; profilo Awin 102801, 200): "Base payouts are $75 for the Starter package, $125 for Pro, and $175 for Premium"; cookie 30 giorni; vietati coupon, cashback, brand bidding e "paid search activity in general"; programma chiamato **"ZenBusiness (US)"**; termini completi 404 senza login. Il piano Starter costa **0 $ il primo anno** (letto sul profilo Awin): la maggior parte delle vendite da pagine "quanto costa" finisce lì → 75 $, non 115 $.
- **Gusto** (`market.partnerstack.com/page/gusto`, 200): "Earn $300 for every new customer (**who runs payroll**) you refer"; i termini (`gusto.com/legal/terms/partnerstack-terms`) sono dietro un blocco anti-bot (403, "Enable JavaScript and cookies"): **non ho potuto leggere** durata del cookie, finestra per la prima busta paga, Paesi ammessi. Non aggiro il blocco.
- **Awin, editori non USA:** Awin ha la pagina editori in italiano (`awin.com/it/publisher`, 200) e un deposito di iscrizione (1 €/£/$ secondo il centro assistenza, 5 £ secondo la pagina compliance UK: cifre in contrasto). I termini editori USA (PDF, letto) prevedono autofatturazione, dati fiscali e IVA/ritenute: nulla vieta un editore italiano, ma **ogni advertiser "may approve or refuse" a propria discrezione** (clausola letta) e i due programmi sono marcati "(US)". Nessuna prova che accettino un sito nuovo su `.netlify.app` senza autore: è un rischio aperto, non un dettaglio.
- **Cookie:** 30 giorni per entrambi (letto sui profili Awin). Il sito dovrebbe avere il banner cookie/consenso per i link tracciati (il nostro contatore non usa cookie, Awin sì).

### 3.2 La conversione 0,5 % è credibile? No
Catena del ricercatore: 4 % dei visitatori clicca il riquadro × 12-15 % compra = 0,5-0,6 %. Prove contro:
- Parametri di settore (QualityUnit, due guide che si contraddicono): clic sui link affiliati 0,5 % "tipico", 1 % "eccellente", 2-5 % in un'altra tabella; vendita sul clic **1-3 % "solido"**, 5 % "eccellente". Le pagine "informative" (quanto costa, quando scade) "rarely convert directly" (agenzia, tabella ipotetica: 2 % × 2 %).
- Il 12-15 % di Northwest vale per pagine di atterraggio costruite da loro per editori grandi con lettori che stanno scegliendo un agente ("best registered agent"), non per chi cerca "wyoming annual report due date".
- Metà delle pagine proposte (rapporto annuale, scadenza, multa, franchise tax, SUI rate, new hire reporting) è letta da chi **ha già** una società o già fa le paghe: non compra una formazione.

Ipotesi mie, dichiarate: clic sul riquadro 2 % (centrale), vendita sul clic 3 / 5 / 10 % → **visita → vendita 0,06 % / 0,10 % / 0,30 %**. Commissione media 100 $ (mix: Starter ZenBusiness 75 $, agente Northwest 100 $, qualche formazione 150 $), al netto dei rifiuti di validazione dell'advertiser (clausola letta: "may approve or decline Sales… at their discretion"). Gusto: solo clienti che fanno davvero le paghe → 0,01 / 0,03 / 0,10 % delle visite.

### 3.3 Stima ricalcolata (ritmo annuo al mese 18; AdSense 20 $ per 1.000 pagine, 1,4 pagine per visita, come nel file originale)
**Blocco A (LLC):**
- Prudente: 150 visite/mese → 1.800/anno × 0,06 % = 1,1 vendite × 100 $ = 108 $ + AdSense 1.800 × 1,4 × 20 / 1.000 = 50 $ → 158 $ ≈ **145 €**
- Centrale: 600/mese → 7.200 × 0,10 % = 7,2 × 100 $ = 720 $ + 202 $ → 922 $ ≈ **850 €**
- Ottimista: 2.000/mese → 24.000 × 0,30 % = 72 × 100 $ = 7.200 $ + 672 $ → 7.872 $ ≈ **7.240 €**

**Blocco B (datore di lavoro):**
- Prudente: 100/mese → 1.200 × 0,01 % = 0,1 × 300 $ = 36 $ + 34 $ → 70 $ ≈ **65 €**
- Centrale: 400/mese → 4.800 × 0,03 % = 1,4 × 300 $ = 432 $ + 134 $ → 566 $ ≈ **520 €**
- Ottimista: 1.500/mese → 18.000 × 0,10 % = 18 × 300 $ = 5.400 $ + 504 $ → 5.904 $ ≈ **5.430 €**

**Insieme: 210 / 1.370 / 12.700 €/anno.** Se Awin o PartnerStack non approvano il sito (rischio reale, sez. 3.1): solo AdSense → 85 / 340 / 1.080 €. Per raggiungere i 5.000 € centrali servirebbero ~2.400 visite al mese con lo 0,10 %, cioè 3 volte EsameB1 oggi, in una nicchia USA dove i nostri due siti USA sono a 0.

---

## 4. Rischi

1. **Errori su scadenze e importi = danno concreto al lettore.** Wyoming: la LLC decade 60 giorni dopo la scadenza e serve una riattivazione; Georgia: riattivazione 250 $ più arretrati; Delaware: tassa annuale passata da 300 a 400 $ (HB 400) con due letture diverse dell'anno di decorrenza; Louisiana: rapporto annuale 30 → 35 $ e costituzione 100 → 125 $ dal 1/10/2026; New Jersey: costituzione 125 → 100 $ dal 1/7/2026; Massachusetts: aliquota nuovi datori 2,13 % (2025) copiata come 2026 da un concorrente, mentre la DUA dice 2,42 %. Anche i siti con redazione sbagliano; un sito senza redazione e senza accesso automatico alle fonti sbaglierebbe di più.
2. **Manutenzione di 51 fonti: non automatica.** Prova di oggi, 25 pagine ufficiali: leggibili 10 (Florida Sunbiz, NJ, Wyoming PDF, Delaware, Michigan, Pennsylvania, Missouri, EDD California, Minnesota già il 31/10, DOL PDF); **403** Texas SOS, Georgia SOS, New York DOS, DOL salario minimo, Mass.gov; **404** California SOS tariffe, NC SOS, Washington SOS, Arizona, Vermont, Louisiana, Tennessee, Georgia DOR; **connessione chiusa** Illinois, Ohio, Nevada; Texas TWC 202 senza contenuto. Cioè 15 su 25 non si leggono: l'obiettivo "≥ 45 Stati su 51 letti in automatico" della prova tecnica proposta è, per quanto visto oggi, fuori portata. Il controllo mensile di ~150 pagine sarebbe a mano; con 700 pagine pubblicate e cambi di tariffa in almeno 3 Stati nel solo 2026 (DE, LA, NJ), il rischio di pagine vecchie è strutturale.
3. **Editore italiano forfettario.** (a) Le commissioni Awin (Awin Ltd, UK) e PartnerStack arrivano come compensi per servizi con autofatturazione e dati fiscali richiesti (termini letti): è la stessa domanda aperta del cancello fiscale (STRATEGIA sez. 10, prima verifica 24/11/2026) e del codice ATECO da fotografo: non è un rischio nuovo, ma questo sito non parte senza quella risposta. (b) Contenuti fiscali e legali USA scritti da un editore non USA, senza autore nominato: servono un disclaimer ("informazioni generali, non consulenza legale o fiscale; verifica sul sito dello Stato") e il divieto assoluto di frasi di consiglio ("dovresti sciogliere", "ti conviene il Wyoming"): negli USA la "unauthorized practice of law" è un tema per chi spiega procedure legali, e le pagine "how to dissolve" sono al limite. (c) AdSense su pagine legali/fiscali senza autore ed E-E-A-T: approvazione non scontata.
4. **Lingua.** Inglese USA giuridico, diverso per Stato: Articles of Organization (quasi ovunque) ma Certificate of Formation (Texas, Delaware), Annual Registration (Georgia), Statement of Information (California, biennale), Periodic Report (Colorado), franchise tax (Texas, con soglia 2,47 o 2,65 M$ a seconda della fonte), "annual tax" (California, 800 $). Un errore di nome non è solo di stile: cambia il modulo che il lettore cerca.
5. **Sito nuovo in `.netlify.app` senza link e senza autore** è il profilo che oggi nella rete non viene indicizzato (Italy Strikes, 0 pagine in 13 giorni) e quello che gli aggiornamenti 2024-2026 penalizzano. Per un'affiliazione "(US)" con approvazione manuale è anche il profilo più facile da rifiutare.

---

## 5. Voto e decisione

**Griglia severa:** domanda 2 (forte, ma concentrata su 10 Stati dove stanno i marchi, e con risposta AI diretta) + Google battibile 0 (prima pagina = pagatori + LLC University + 6 siti automatici già sulla coda lunga) + fonte e licenza 0,5 (15 fonti su 25 non leggibili; licenza ok) + soldi per visitatore 1,5 (commissioni vere e lette, ma conversione provata solo dal venditore e approvazione incerta) + rischi e ore 0,5 (manutenzione a mano, danno al lettore, cancello fiscale) = **4,5/10**.

**Decisione: NO al sito nuovo.** Non passa né il voto (≥ 7) né i soldi (centrale 1.370 € contro 5.000 €). Cosa resta valido dell'idea, a costo quasi zero, come **RISERVA condizionata**:
- Il fatto nuovo vero è che Northwest e ZenBusiness scrivono la cifra. Vale per tutta la rete, non per questo sito: la riserva "LLC per non residenti" (autocomplete oggi: "llc for non us residents" 10 varianti, "wyoming llc for non residents", "best llc for non us residents") parla al pubblico che Visa Income già riceve da ChatGPT (Pakistan, Nigeria, India). È lì che la commissione da 100-150 $ ha un pubblico che non può aprire la società da solo allo sportello. Da riaprire **solo dopo** che Awin ha approvato un nostro sito esistente e il cancello fiscale ha una risposta.
- Prova a costo minimo (3-4 ore, non 60-85): una sola tabella "LLC annual fees by state, verified [data]" con le 51 righe e la fonte, come pagina dentro un sito USA esistente, dopo l'approvazione Awin. Se in 90 giorni fa ≥ 300 impressioni al mese e almeno 1 clic affiliato, si ridiscute; altrimenti si chiude anche la riserva.
- Il blocco B (datore di lavoro) non ha una strada: la fonte federale è buona (DOL, letto) ma la prima pagina è delle società delle paghe e degli enti, e Gusto paga solo chi fa davvero le paghe. NO anche come sezione.

---

## 6. Fonti lette oggi (31/10/2026)

- Google Autocomplete: 37 domande con `hl=en gl=us` (numeri nelle sez. 1.1-1.2). Google Search dal server: pagina di reindirizzamento (bloccato). Bing dal server: 10 ricerche, 3 usabili.
- Ricerca web dagli USA (prima pagina + fonti citate): "llc annual fee wyoming", "vermont llc annual report fee", "reinstate llc georgia", "annual report fee north carolina llc", "llc annual fees by state 2026", "new employer sui rate massachusetts 2026", "how to register as an employer in california", più ricerche su programmi e aggiornamenti Google.
- Northwest: https://www.northwestregisteredagent.com/affiliate-program (200); https://ui.awin.com/merchant-profile/66946 (200); termini https://ui.awin.com/merchant-profile-terms/66946 (404 senza login)
- ZenBusiness: https://www.zenbusiness.com/affiliate-program/ (200); https://ui.awin.com/merchant-profile/102801 (200, "ZenBusiness (US)"); termini (404 senza login)
- Gusto: https://market.partnerstack.com/page/gusto (200); https://gusto.com/legal/terms/partnerstack-terms (403, blocco anti-bot, non aggirato)
- Awin: termini editori USA (PDF 2023, letto con pdftotext); https://www.awin.com/it/publisher (200); centro assistenza sul deposito di iscrizione
- Pagine ufficiali provate (25, esiti in sez. 4.2): sos.state.tx.us, sos.ga.gov, dos.fl.gov, sos.ca.gov, ilsos.gov, nj.gov, sosnc.gov, sos.wyo.gov, dos.ny.gov, corp.delaware.gov, sos.wa.gov, sos.ohio.gov, michigan.gov, azcc.gov, sos.nv.gov, dos.pa.gov, sos.vermont.gov, sos.mo.gov, sos.la.gov, sos.tn.gov, dol.gov, edd.ca.gov, twc.texas.gov, mass.gov, dor.georgia.gov
- Semrush (pagina pubblica, luglio 2025): llcuniversity.com 246-289 mila visite al mese
- Studi citati (terzi): Ahrefs (58 clic su 100 trattenuti da Google), Pew (8 % contro 15 %), JetDigitalPro sul core update di marzo 2026 (71 % dei siti di affiliazione in calo)
- Numeri della rete: `studio-business/CRUSCOTTO-RETE.md` (settimane 14-28/10/2026); cancello fiscale: `studio-business/STRATEGIA.md` sez. 10
