# Fronte nuovo del 31/10/2026: lo stesso modello, ma per un pubblico che vale molto

**Domanda di partenza.** I nostri siti parlano a stranieri e viaggiatori: in pubblicità valgono poco. Dove lo stesso modello (numeri ufficiali per luogo o categoria, aggiornati dagli agenti, citabili dagli assistenti AI) incontra proprietari di casa, imprese, datori di lavoro, investitori, pensionati, in USA, Regno Unito, Canada, Australia, Germania e Svizzera, con pubblicità alta e affiliazioni ricche?

**Letti prima:** skill `rete-siti`, `REGOLE-FISSE.md` (regole del 30-31/10), `ESPLORATE.md` (ricerca per parole chiave su tasse sulla casa, salario minimo, sales tax, Grundsteuer, affitti brevi, licenze, incentivi, assicurazioni, mutui), i file `idee-2026-10-*.md` e `fronti-2026-10-31-*.md`. Già chiusi e **non rifatti**: tassa sulla casa per contea USA (NO 21/10), salario minimo per Stato (NO 22/10), sales tax holidays (NO 17/10), tassa comunale UK, taxe foncière, Bodenrichtwert (NO 14/10), elettricità per CAP (NO 14/10), affitti brevi in Francia (NO 18/10), registro dei padroni di casa inglesi (PASSA 31/10), pompe di calore UK (NO 31/10), assicurazione casa Florida (NO 29/10), stamp duty e land transfer (NO 30/10).

**Prove, tutte del 31/10/2026:** `curl` dal nostro server (codice HTTP, dimensione, testo letto), Google Autocomplete (`suggestqueries.google.com`, `client=firefox`; `hl=en gl=us` per USA/Canada, `hl=de gl=de` per la Germania; il numero dopo la domanda è quante varianti propone, massimo 10), ricerca web per vedere chi c'è in prima pagina (fatta dagli USA).

**Griglia del voto** (come le ricerche precedenti): domanda 0-3, Google battibile 0-2, fonte e licenza 0-2, soldi per visitatore 0-2, rischi e ore 0-1. Stime a 18 mesi, in euro lordi all'anno, **con il conto scritto: sono stime, non dati**. Cambio usato: 1 $ = 0,92 € (ipotesi).

**Ipotesi di pubblicità** (dai file già in casa, non nuove): AdSense USA circa 20 $ ogni 1.000 pagine viste, Regno Unito 16 $, Germania 14 $, con moltiplicatore ×3 per la finanza (modello adstimate, 29/7/2026, citato in `7-modelli-diversi.md`); siti venduti su Empire Flippers, RPM mediano per nicchia: Finanza 48 $, Legale 39 $, Viaggi 55 $, Informazione 30 $ (`ricerca-profonda-2026-10-28-mercato.md`). Nelle stime uso **20 $** per le pagine "imprese e finanza" USA (prudente: senza il ×3) e 1,4 pagine viste per visita.

---

## 0. Risposta in breve

**Un solo progetto passa i 10.000 €/anno nella stima centrale: un sito nuovo "US Small Business by State" con due blocchi** (costi e scadenze delle società Stato per Stato; obblighi del datore di lavoro Stato per Stato). Il motivo è nuovo per la rete: **i pagatori pagano 100-300 $ per cliente, con la cifra letta sulle loro pagine ufficiali** (Northwest 100 $ / 150 $, ZenBusiness 75 / 125 / 175 $, Gusto 300 $). Con commissioni così bastano 1.500 visite al mese per arrivare a 10.000 €.
Il blocco A da solo arriva a 10.000 € (al limite); il blocco B da solo a 7.900 €. **La seconda idea indipendente da 10.000 € non l'ho trovata**: ho cambiato nicchia 5 volte (zone di opportunità, tetti agli affitti, aste fiscali, sales tax, Grundsteuer/Gewerbesteuer tedesca) e tutte si fermano tra 1.000 e 4.000 € nel caso centrale, perché pagano solo con la pubblicità. Il vincolo da allentare è scritto nella sez. 4.

| # | Idea | Paese, lingua | Chi paga (fonte) | Voto | 18 mesi €/anno (prudente / centrale / ottimista) | Ore | Esito |
|---|---|---|---|---|---|---|---|
| 1A | **Costi e scadenze delle società (LLC) Stato per Stato**: costo di apertura, rapporto annuale (importo e data), franchise tax, agente registrato, chiusura, riattivazione, con "verificato il" e registro dei cambi | USA, EN | **Northwest 100 $ (agente) / 150 $ (apertura)**, letto; **ZenBusiness 75 / 125 / 175 $**, letto; AdSense | **6,5** | 860 / **10.000** / 46.000 | 35-50 | **PASSA come sito nuovo** (con 1B) |
| 1B | **Datore di lavoro Stato per Stato**: registrazione, aliquota di disoccupazione per i nuovi datori e base imponibile (DOL), conto ritenute, denuncia dei nuovi assunti, contributi per i congedi pagati | USA, EN | **Gusto 300 $ per cliente che fa le paghe**, letto (PartnerStack); AdSense | **6** | 590 / **7.900** / 51.200 | 25-35 | blocco dello stesso sito |
| | **1A + 1B insieme** | | | **6,5** | **1.450 / 17.900 / 97.200** | 60-85 | **proposta a Massimiliano** |
| 2 | Zone di opportunità 2.0 (Opportunity Zones 2027-2036) per Stato, contea e città, con le zone perse e le nuove | USA, EN | solo AdSense finanza (nessun affiliato trovato) | 6 | 400 / 2.300 / 9.300 | 20-30 | **RISERVA con data**: si costruisce quando il Tesoro pubblica l'elenco (entro il 27/11, al più tardi il 28/12/2026) |
| 3 | Aumento massimo dell'affitto per giurisdizione (California per contea con AB 1482, città con rent control, Oregon, Washington, province canadesi) | USA + Canada, EN | AdSense casa; affiliati per padroni di casa senza cifra (Steadily) | 6 | 300 / 2.200 / 7.400 | 18-25 | RISERVA (sezione possibile di FloodCost o del sito 1) |
| 4 | Moratorie sulle disdette dell'assicurazione casa per CAP (California, dopo gli incendi) | USA, EN | AdSense assicurazioni; Lemonade 15 $ a contatto (letto il 17/10) | 5,5 | 40 / 400 / 1.400 | 4-6 | **SEZIONE di FloodCost** (rete fitta: costo zero) |
| 5 | Licenze di locazione (selective, additional, HMO) per council, con tariffe e date | Regno Unito, EN | AdSense UK; AXA Landlord su Awin (da verificare, come il 31/10) | 5,5 | 150 / 900 / 3.300 | 15-20 | sezione del sito "registro dei padroni di casa" (PASSA 31/10), non da sola |
| 6 | Hebesatz di Gewerbesteuer e Grundsteuer per Comune (10.753 Comuni) + costo della Gewerbeanmeldung | Germania, DE | AdSense DE; conti aziendali (Finom: "Provision variabel", nessuna cifra) | 5 | 250 / 1.600 / 6.300 | 25-35 | RISERVA (fatto nuovo: CSV ufficiale per Comune, ma concorrenti automatici già presenti) |
| 7 | Soglie della sales tax per chi vende online (economic nexus) Stato per Stato | USA, EN | Quaderno 30 % per 24 mesi (letto); AdSense | 5 | – | 8-12 | solo come pagine dentro il sito 1 |
| 8 | Requisiti e costi della licenza da impresa edile per Stato | USA, EN | Next Insurance ~25 $ a preventivo (non letto) | 5 | 150 / 900 / 3.600 | 20-30 | RISERVA debole |
| 9 | Aste fiscali (tax deed / tax lien) per contea | USA, EN | Tax Sale Resources 25 % ricorrente (letto) | 4,5 | – | – | NO: calendari RealAuction 403, fonti contea per contea |
| 10 | Permessi e regole per gli affitti brevi per città | USA, EN | host: Steadily, nessuna cifra | 4,5 | – | – | NO: 19.000 Comuni senza file unico, bnbcalc già con pagine per città in 8 lingue |
| 11 | Incentivi per pompe di calore e casa efficiente (HEAR/HOMES) per Stato | USA, EN | EnergySage 9,60 $ a contatto (non letto) | 4 | – | – | NO: la pagina DOE dice solo "coming soon", Rewiring America ha il calcolatore per CAP |

**Collegamento con Tourist Tax** (richiesto): gli affitti brevi USA non reggono (riga 10). Tourist Tax parla ai viaggiatori, non agli host; una versione "per host" (quanta tassa devo riscuotere e versare, a chi, quando) avrebbe un pubblico che vale di più, ma serve un programma per host con cifra scritta (Lodgify, Smoobu, Hospitable: non verificati oggi). Resta un'annotazione, non un'idea.

---

## 1. L'idea che passa: "US Small Business by State" (sito nuovo, inglese)

### 1A. Costi e scadenze delle società, Stato per Stato (voto 6,5)

**Cosa.** Circa 420 pagine: per ognuno dei 50 Stati più DC, 8 pagine (quanto costa aprire una LLC; rapporto annuale: importo, scadenza, multa per il ritardo; franchise tax e soglie; agente registrato obbligatorio; chiudere la società; riattivarla; registrarla in un altro Stato; cambiare nome o agente) più le tabelle nazionali ("LLC annual fees by state"). Ogni numero con la pagina ufficiale, la data del controllo e un registro dei cambi ("Louisiana: rapporto annuale da 30 a 35 $ dal 1/10/2026"). È la forma che ChatGPT cita: tabella, fonte, data.

**Fonte (curl 31/10).** Le pagine delle tariffe dei Secretary of State e degli uffici delle imposte dei 50 Stati. Lette: California FTB 200 (testo: "annual tax of $800", "Your LLC will not be subject to the annual $800 tax for its first tax year", tabella della LLC fee 900 / 2.500 / 6.000 / 11.790 $), California SOS moduli 200. **Bloccato: Texas SOS `sos.state.tx.us/corp/fees.shtml` 403.** Ipotesi da provare prima di costruire: 10-15 Stati su 51 non leggibili dal server (come per i DMV); per quelli si legge il PDF del modulo o il Comptroller. Licenza: atti pubblici degli Stati, numeri non tutelati. Aggiornamento: le tariffe cambiano poche volte l'anno, ma cambiano (la ricerca web trova per il 2026 Delaware, Louisiana, New Jersey) e i siti in prima pagina si contraddicono (soglia della franchise tax del Texas: 2,47 o 2,65 milioni $ a seconda della fonte). Lavoro dell'agente: un controllo al mese di ~150 pagine ufficiali, con un avviso quando un numero cambia.

**Domanda (autocomplete USA).** "llc annual fee" 10 (by state, california, illinois, texas, nj, virginia, nc, florida, new york); "llc cost in" 10 Stati; "how much does it cost to start an llc in" 10 Stati; "annual report fee" 10 (florida, nj, by states, massachusetts, wyoming, north carolina, illinois); "registered agent in" 10 Stati; "how to dissolve an llc in" 10 Stati; "reinstate llc" 10 Stati. Domanda per Stato provata su 7 famiglie di pagine.

**Chi c'è su Google.** Forte. LLC University (pagina per Stato e tabella nazionale), LegalZoom e ZenBusiness con la loro pagina per Stato (sono gli stessi pagatori), Inc Authority, zenind, venturesmarter, startbusinessbystate, jupid, più siti automatici nuovi (beancount.io, pagine su pages.dev). **Battibile?** Non su Google in testa, nei primi mesi. Lo spazio c'è sulla coda lunga (rapporto annuale di uno Stato piccolo, riattivazione, multa per il ritardo) e sugli assistenti AI, che oggi pescano da pagine che si contraddicono. Nella rete ChatGPT manda già un terzo delle visite proprio su tabelle con fonte e data.

**Chi paga (letto sulle pagine ufficiali il 31/10).**
- Northwest Registered Agent (`northwestregisteredagent.com/affiliate-program`, 200): "$100 per signup for registered agent services, $150 per signup for business formation", "Average conversion rate of 12-15%". Su Awin; cookie 30 giorni (fonte terza, non letto).
- ZenBusiness (`zenbusiness.com/affiliate-program/`, 200): "Base payouts are $75 for the Starter package, $125 for Pro, and $175 for Premium", su Awin.
- Next Insurance (assicurazione per piccole imprese): ~25 $ a preventivo secondo directory terze, **non letto** (pagina ufficiale senza cifra): non entra nel conto.
- **Fatto nuovo per la riserva del 31/10 "LLC per non residenti"** (`idee-2026-10-31-soldi.md`): quella riserva aspettava "una commissione letta sulla pagina del programma". Adesso ce ne sono due (Northwest, ZenBusiness). Diventa un terzo blocco naturale di questo sito, non un'idea a sé.

**Stima a 18 mesi (ritmo annuo al mese 18).** Commissione media 115 $ (mix agente 100 $, apertura 150 $, ZenBusiness 75-175 $). Conversione da visita a vendita: prudente 0,2 %, centrale 0,5 %, ottimista 0,7 % (ipotesi: 4 % delle visite clicca il riquadro sulle pagine "quanto costa aprire", "agente registrato", "riattivare"; Northwest dichiara il 12-15 % di vendite sui clic, cioè 0,5-0,6 %).
- Prudente: 300 visite/mese → 3.600 × 0,2 % = 7 vendite × 115 $ = 830 $ + AdSense 3.600 × 1,4 × 20 $ / 1.000 = 100 $ → 930 $ ≈ **860 €**.
- Centrale: 1.500 visite/mese → 18.000 × 0,5 % = 90 × 115 $ = 10.350 $ + AdSense 504 $ → 10.854 $ ≈ **10.000 €**.
- Ottimista: 5.000 visite/mese → 60.000 × 0,7 % = 420 × 115 $ = 48.300 $ + 1.680 $ → 49.980 $ ≈ **46.000 €**.
- **Primi soldi:** dal mese 3-4 se ChatGPT comincia a citare le tabelle (come per Visa Income), altrimenti dal mese 6-9. Serve l'iscrizione ad Awin (Massimiliano ha già l'account Awin in programma per altre sezioni).

**Rischi.** (1) Concorrenza fortissima su Google: la stima centrale regge solo se arrivano gli assistenti AI e la coda lunga. (2) Approvazione dei programmi su Awin: pagatori USA possono rifiutare un sito nuovo su `.netlify.app`; da chiedere dopo 30-40 pagine pubblicate. (3) Tema "legale": solo numeri ufficiali e procedure, niente consigli. (4) È un sito nuovo: la regola chiede voto ≥ 7 e ≥ 5.000 €; passa sui soldi, non sul voto (vedi sez. 5).

**Ore:** 35-50 (lettore delle ~150 pagine ufficiali con controllo mensile 15-20; generatore e tabelle 10-15; testi e revisione 10-15).

**Voto 6,5:** domanda 3 + Google 0,5 + fonte 1 (51 fonti, alcune 403) + soldi 2 + rischi e ore 0. Sale a 7,5 se la prova tecnica legge in automatico ≥ 45 Stati su 51 e se Awin approva Northwest o ZenBusiness.

### 1B. Il datore di lavoro, Stato per Stato (voto 6)

**Cosa.** Circa 300 pagine: per ogni Stato, come registrarsi come datore di lavoro (numero di ritenuta, conto di disoccupazione), aliquota per i nuovi datori e base imponibile 2026-2027, denuncia dei nuovi assunti, contributi per i congedi pagati dove esistono, salario minimo con la data (solo come riga, il tema da solo è NO dal 22/10), assicurazione infortuni obbligatoria sì/no.

**Fonte (curl 31/10).** **Una fonte unica federale per il pezzo più cercato:** Dipartimento del Lavoro, "Significant Provisions of State Unemployment Insurance Laws, effective July 2026" (`oui.doleta.gov/unemploy/content/sigpros/2020-2029/July2026.pdf`, 200, 270 KB, PDF a tabella, esce a gennaio e luglio; contiene per ogni Stato base imponibile, aliquote minima e massima e "New Employer Rate"; esempio letto: Alabama base 8.000 $, nuovi datori 2,70 %; Alaska 54.200 $). Opera del governo federale: pubblico dominio. Pagina indice `statelaws.asp` 200. Pagine dei singoli Stati per registrazione e congedi (Minnesota `paidleave.mn.gov/employers/premiums` 200). **Bloccate:** `dol.gov/agencies/whd/minimum-wage/state` 403.

**Domanda (autocomplete USA).** "new employer sui rate" 10 (by state 2026, 2025, massachusetts, florida, colorado, louisiana, "ui rate 2026"); "unemployment tax rate for new employers" 10 Stati (texas, utah, louisiana, colorado, virginia, maryland, arizona, pennsylvania, ohio, massachusetts); "how to register as an employer in" 10 (california, florida, ma anche Filippine e Irlanda); "state withholding account number" 10 (ohio, louisiana, kansas, colorado, illinois); "state payroll tax registration" 10. "paid family leave contribution 2027" 0 e "how to hire your first employee in" 0: quelle pagine non si fanno.

**Chi c'è su Google.** Le società delle paghe: OnPay (tabella 2026 aggiornata il 6/4/2026), Patriot Software, Gusto, Paycom, Eddy, Experian; più startbusinessbystate e siti automatici (teamed.global, metricrig su pages.dev). **Battibile?** In parte: nessuno ha "luglio 2026" dalla tabella federale con la data; le tabelle si contraddicono (Alaska 51.700 o 54.200 $). Per gli assistenti AI una tabella con fonte DOL e data è la risposta migliore.

**Chi paga.** **Gusto: "Earn $300 for every new customer (who runs payroll) you refer"** (letto su `market.partnerstack.com/page/gusto`, 200). Le pagine di aiuto di Gusto parlano anche di premi a scaglioni per i commercialisti (300-1.000 $), che non valgono per noi. Next Insurance (infortuni) non letto. AdSense.

**Stima a 18 mesi.** Conversione verso Gusto: 0,05 % / 0,15 % / 0,3 % delle visite (ipotesi: chi cerca "come mi registro come datore di lavoro" sta per fare le prime paghe; Gusto paga solo se le paghe partono davvero).
- Prudente: 300/mese → 3.600 × 0,05 % = 1,8 × 300 $ = 540 $ + 100 $ AdSense → 640 $ ≈ **590 €**.
- Centrale: 1.500/mese → 18.000 × 0,15 % = 27 × 300 $ = 8.100 $ + 504 $ → 8.604 $ ≈ **7.900 €**.
- Ottimista: 5.000/mese → 60.000 × 0,3 % = 180 × 300 $ = 54.000 $ + 1.680 $ → 55.680 $ ≈ **51.200 €**.
- Primi soldi: come 1A; il picco stagionale delle aliquote è a gennaio (nuove aliquote 2027) e luglio (nuova tabella DOL).

**Ore:** 25-35. **Voto 6:** domanda 2,5 + Google 0,5 + fonte 1,5 (una fonte federale per il pezzo principale) + soldi 1,5 (300 $ ma conversione più bassa) + rischi 0.

### Perché insieme

Stesso lettore in due momenti (apro la società → assumo il primo dipendente), stesso motore (pagine Stato × argomento con fonte e data), link interni naturali, un solo sito su Netlify e un solo passaggio di Massimiliano. **Insieme: 1.450 / 17.900 / 97.200 €/anno.** Il terzo blocco possibile è la riserva "LLC per non residenti" del 31/10 (pakistani, indiani, nigeriani che aprono una LLC: stessa commissione Northwest/ZenBusiness).

---

## 2. Le altre idee, una per una

### 2. Zone di opportunità 2.0 (Opportunity Zones 2027-2036), voto 6, RISERVA con data

**Fatto nuovo con data.** La legge OBBBA ha rifatto le zone. Rev. Proc. 2026-14 (`irs.gov/pub/irs-drop/rp-26-14.pdf`, 200, letta): i governatori nominano fino al 25 % dei tratti di censimento idonei; nomine entro il 28/10/2026 con la proroga; **il Tesoro certifica entro il 27/11/2026, al più tardi il 28/12/2026**; le zone valgono dal 1/1/2027 al 31/12/2036. Le zone del 2018 scadono il 31/12/2028 e devono essere rinominate da capo: molte spariranno (fonti terze: circa -24 %).
**Fonte.** CDFI Fund (`cdfifund.gov/opportunity-zones`, 200) con l'elenco 2018 in Excel (`designated-qozs.12.14.18.xlsx`); l'elenco 2027 uscirà nello stesso posto; mappa HUD (`opportunityzones.hud.gov`, 200); pagina IRS 200. Pubblico dominio.
**Domanda.** "opportunity zone" 10 ("2.0", "2.0 map", "2026", "california"); "new opportunity zones" 10 ("map", "2026", "rules 2027", "maps 2026"); "opportunity zone list" 4.
**Google.** Kiplinger, JD Supra, studi legali, NGA, EIG (guide per i governatori); Novogradac e EIG faranno la mappa. Nessuno oggi ha le pagine "zone nuove e zone perse in [contea/città]": è il buco, ma solo per qualche mese.
**Chi paga.** Solo AdSense finanza (investitori, costruttori, commercialisti). Nessun affiliato: i fondi sono titoli finanziari, vietato raccoglierli.
**Stima.** ~3.200 contee e ~1.000 città con tratti designati; pagine città e contea con l'elenco dei tratti, il confronto 2018/2027 e il "verificatore per indirizzo" via geocoder del Census (da provare). Visite al mese 18: 1.000 / 5.000 / 15.000; RPM 25 / 30 / 40 $ (finanza). Prudente 1.000 × 12 × 1,4 × 25 / 1.000 = 420 $ ≈ **400 €**; centrale 5.000 × 12 × 1,4 × 30 / 1.000 = 2.520 $ ≈ **2.300 €**; ottimista 15.000 × 12 × 1,4 × 40 / 1.000 = 10.080 $ ≈ **9.300 €**. Primi soldi: subito dopo l'elenco (dicembre 2026 - gennaio 2027), il momento con più ricerche.
**Ore:** 20-30. **Esito:** RISERVA con innesco: un controllo settimanale della pagina CDFI (1 ora per scriverlo); quando esce l'Excel 2027 si costruisce in 2-3 giorni, come sezione del sito 1 (stesso pubblico di imprese e investitori) o di ApprovedCondos.

### 3. Aumento massimo dell'affitto per giurisdizione, voto 6, RISERVA

**Fonte (curl 31/10).** Oregon OEA 200: "Maximum Annual Rent Increase, 2027 (Excel file)", "for the previous year, 2026, was 9.5%"; Ontario 200: "The guideline for 2027 is 1.9%"; British Columbia 200; California DIR, indice dei prezzi (`dir.ca.gov/OPRL/CPI/EntireCCPI.PDF`, 200); Washington Commerce 403. La California calcola il tetto AB 1482 come 5 % + CPI della zona (massimo 10 %): la ricerca web trova cifre diverse per la stessa zona (San Francisco 8,6 % o 8,8 %) e **nessuna tabella completa per contea**: il calcolatore della California Apartment Association è riservato ai soci.
**Domanda.** "allowable rent increase 2026" 10 (ontario, bc, quebec, "sf allowable rent increase 2026"); "rent increase cap 2027" 10 (oregon, bc, ontario, washington state, ca); "rso rent increase 2026" 9 (los angeles, calculator, la county).
**Google.** Gli enti rispondono da soli per la loro giurisdizione (Ontario, BC, Oregon, SF Rent Board); Steadily e gestori immobiliari per la California. Il buco: le 58 contee della California e le ~35 città con rent control, con il calcolo e la data.
**Chi paga.** AdSense casa (padroni di casa e inquilini); Steadily (assicurazione padroni di casa) paga ma senza cifra scritta ("Earn $$ for every Steadily referral").
**Stima.** Visite al mese 18: 1.000 / 6.000 / 15.000, RPM 18 / 22 / 30 $: prudente 1.000 × 12 × 1,4 × 18 / 1.000 = 302 $ ≈ **280-300 €**; centrale 6.000 × 12 × 1,4 × 22 / 1.000 = 2.218 $ ≈ **2.000 €** (+200 € se Steadily dà una cifra: **2.200**); ottimista 15.000 × 12 × 1,4 × 30 / 1.000 = 7.560 $ ≈ **7.000 €** + 400 € = **7.400 €**.
**Ore:** 18-25. **Esito:** RISERVA; meglio come sezione (FloodCost parla già ai proprietari di casa USA) che come sito.

### 4. Moratorie sulle disdette dell'assicurazione casa per CAP (California), voto 5,5, SEZIONE di FloodCost

**Fonte.** Bollettini del Commissario delle assicurazioni (CDI): Bulletin 2026-01 del 9/1/2026 (PDF 200, letto: moratoria di un anno sulle disdette per i CAP dentro o accanto al perimetro dell'incendio, art. 675.1 del codice delle assicurazioni; 30 CAP nel testo); bollettini 2025-1 (Palisades ed Eaton), 2025-6, 2025-13, 2025-17. Atti pubblici.
**Domanda.** "california non renewal" 10, con "moratorium" e "insurance"; domanda piccola ma di proprietari di casa.
**Google.** Il CDI, giornali (ABC7, Mercury News), MoneyGeek con l'analisi per contea. Nessuno ha "il mio CAP è protetto fino a quando?".
**Chi paga.** AdSense assicurazioni; Lemonade 15 $ a contatto (letto il 17/10, `idee-grandi-2026-10-17.md`).
**Stima.** 400 / 3.000 / 8.000 visite l'anno: prudente 400 × 1,4 × 25 / 1.000 = 14 $ + 2 contatti × 15 $ = 30 $ → 44 $ ≈ **40 €**; centrale 3.000 × 1,4 × 30 / 1.000 = 126 $ + 18 contatti × 15 $ = 270 $ → ~400 $ ≈ **400 €**; ottimista 8.000 × 1,4 × 40 / 1.000 = 448 $ + 70 × 15 $ = 1.050 $ → 1.498 $ ≈ **1.400 €**.
**Ore:** 4-6 (lettore dei PDF dei bollettini, una pagina per CAP con la scadenza). **Esito:** SEZIONE in coda di FloodCost (rete fitta: costo zero, guadagno positivo).

### 5. Licenze di locazione per council (Inghilterra), voto 5,5, dentro il sito del registro dei padroni di casa

**Fonte.** Nessun elenco ufficiale unico. Pagine dei council (Tower Hamlets, Nottingham, Havering, North East Lincolnshire: tariffe 2026 in PDF), NRLA con l'aggiornamento mensile. Fonti terze: "oltre 60 council" con schemi attivi o in arrivo; Hackney 925 £ (selective) e 1.400 £ (additional) dal 1/5/2026.
**Domanda.** "selective licensing" 10 (birmingham, postcode checker, harrow, leeds, leicester, luton, nottingham, croydon); "hmo licence fee" 10 (birmingham, edinburgh, london, southampton, tower hamlets, manchester, nottingham, bristol).
**Google.** londonpropertylicensing.co.uk (dedicato), NRLA, Hamptons, augustapp, e già siti automatici (rentercheck su vercel, pagine su pages.dev). Battibile solo con il controllo mensile di tutti i council e la data.
**Chi paga.** AdSense UK casa; AXA Landlord su Awin (non verificato, come il 31/10).
**Stima** (come sezione): 1.500 / 9.000 / 30.000 visite l'anno; RPM 16 / 20 / 25 £ ≈ 18 / 23 / 28 €; più affiliato solo nell'ottimista. Prudente 1.500 × 1,4 × 18 / 1.000 = 38 € + estensione del registro ≈ **150 €**; centrale 9.000 × 1,4 × 23 / 1.000 = 290 € + 600 € di affiliato se Awin dà una cifra ≈ **900 €**; ottimista 30.000 × 1,4 × 28 / 1.000 = 1.176 € + 2.100 € ≈ **3.300 €**.
**Ore:** 15-20 (~300 council, poi controllo mensile delle ~70 pagine di schemi). **Esito:** blocco del sito "registro dei padroni di casa" (PASSA 31/10), non idea a sé.

### 6. Hebesatz per Comune in Germania (Gewerbesteuer e Grundsteuer), voto 5, RISERVA aggiornata

**Fatto nuovo** (la Grundsteuer era RISERVA dal 14/10 per "nessuna fonte unica aggiornata"): Destatis pubblica un **CSV con tutti i 10.753 Comuni**: `service.destatis.de/DE/karten/hebesaetze-gemeinden-2024/data/hebesaetze-gemeinden-2024.csv` (200, 469 KB; colonne AGS, Name, Grundsteuer A, Grundsteuer B, Gewerbesteuer, Bevölkerung; es. Essen 255 / 670 / 480 %), licenza **DL-DE/BY 2.0** (riuso commerciale con citazione). Il rapporto "Realsteuervergleich 2025" (xlsx 200, "Erschienen am 15.10.2026") è solo per città extracircondariali e circondari (~400 righe); il file 2025 per Comune non c'è ancora (302). La Regionaldatenbank ora chiede l'accesso ("ohne Anmeldung zur Zeit nicht möglich"). **Quindi i dati ufficiali per Comune hanno 1-2 anni di ritardo**, e la Grundsteuer è cambiata in quasi tutti i Comuni con la riforma del 2025: per il 2026 servono le liste delle IHK (PDF per distretto: Gießen-Friedberg, Kronach, Bayreuth, Francoforte, Karlsruhe…) o le Hebesatzsatzungen comunali.
**Domanda (autocomplete DE).** "gewerbesteuer hebesatz" 10 (münchen, berlin, hamburg, köln, düsseldorf, frankfurt, stuttgart, grünwald, leipzig); "hebesatz gewerbesteuer 2026" 10 città; "grundsteuer hebesatz 2025" 10 (niedersachsen, köln, nrw, tabelle, hamburg, münchen, essen); "grundsteuer hebesatz" 10 con "erhöhung widerspruch muster"; "gewerbeanmeldung kosten" 10 (bayern, nrw, berlin, münchen, hessen).
**Google.** Già pagine automatiche per Comune con "2026": finanz-rechner-hub.de (una pagina per Comune con calcolatore), rechner-hub.de (classifica, "43 Comuni sotto il minimo del 280 %"), steuerschroeder, Finom (che è anche il pagatore), selbststaendig.de, IHK. Battibile solo sulla data e sulla fonte.
**Chi paga.** AdSense DE (14 $ base, più per la finanza); conti aziendali: Finom "Die Höhe der Provisionen ist variabel" (nessuna cifra), Qonto/Kontist non letti.
**Stima.** Visite al mese 18: 1.500 / 8.000 / 25.000, RPM 10 / 12 / 15 €: prudente 1.500 × 12 × 1,4 × 10 / 1.000 = **250 €**; centrale 8.000 × 12 × 1,4 × 12 / 1.000 = **1.600 €**; ottimista 25.000 × 12 × 1,4 × 15 / 1.000 = ≈ **6.300 €**.
**Ore:** 25-35. **Esito:** RISERVA; si riapre se esce il CSV per Comune 2025 o 2026 da Destatis o se un conto aziendale scrive una cifra.

### 7. Soglie della sales tax per chi vende online (economic nexus), voto 5

**Domanda forte:** "sales tax nexus" 10 ("by state", "by state chart", "threshold by state", "by state 2026", texas, california, new york); "economic nexus threshold" 10 ("by state 2026", california, texas, arizona, new york).
**Fonte:** 46 pagine statali; l'elenco del Streamlined Sales Tax (`streamlinedsalestax.org/.../remote-seller-state-guidance`) è 404 dal server. **Google:** Avalara, TaxJar, Sales Tax Institute, Numeral, Kintsugi: chi vende il software scrive la tabella. **Chi paga:** Quaderno "recurring 30% commission for up to 24 months" (letto, `quaderno.io/affiliates`), ma con "at least three active referrals" per essere pagati. **Esito:** non da sola (Google pieno di pagatori-concorrenti); 51 pagine dentro il sito 1, dove il lettore è lo stesso. Ore 8-12.

### 8. Licenza da impresa edile per Stato, voto 5, RISERVA debole

**Domanda:** "contractor license requirements" 10 (california, florida, mississippi, arkansas, sc, "by state", idaho, tennessee). **Fonte:** enti statali, es. CSLB California (`cslb.ca.gov/About_Us/Library/Fees.aspx`, 200); circa 35 Stati con licenza statale, il resto per contea o città. **Google:** Next Insurance (pagatore e concorrente), Procore, NASCLA, scuole di preparazione. **Chi paga:** Next Insurance ~25 $ a preventivo (directory terze, non letto). **Stima:** 150 / 900 / 3.600 € (visite 400 / 2.000 / 6.000 al mese, AdSense 20 $ e 0,05-0,1 % di preventivi a 25 $). **Ore:** 20-30. Possibile blocco futuro del sito 1, non prima di avere una cifra letta.

### 9. Aste fiscali per contea (tax deed e tax lien), voto 4,5, NO

**Domanda forte:** "tax deed sale" 10 (texas, florida, california, nc, orange county, georgia, hillsborough county), "tax lien sale" 10, "tax deed auction" 10. **Fonte:** i calendari delle contee che usano RealAuction (`hillsborough.realtaxdeed.com`, `realauction.com`) **403** dal server; le altre contee pubblicano in modi diversi. **Chi paga:** Tax Sale Resources 25 % ricorrente "indefinite" (letto), ma è anche il concorrente con la banca dati a pagamento. **Esito:** NO finché i calendari non sono leggibili; stesso problema degli affidamenti ANAC (copertura).

### 10. Permessi e regole per gli affitti brevi per città (USA), voto 4,5, NO

**Domanda:** "short term rental permit" 10 (san antonio, nashville, los angeles, sevier county, jersey city, albuquerque, colorado springs); "airbnb rules in" 10; "str permit" 10. **Fonte:** nessun file unico; ogni città ha la sua ordinanza e le sue tariffe (Del Mar 815 $, Grand Junction 275 $, Harrison 100 + 200 $: trovate solo città per città). **Google:** bnbcalc.com con una pagina per città **in 8 lingue**, AirDNA, gestori. **Esito:** NO (filtro duro: fonte frammentata e concorrente automatico già presente).

### 11. Incentivi per casa efficiente e pompe di calore per Stato (HEAR/HOMES), voto 4, NO

**Domanda:** "heat pump rebate" 10 per Stato, "home energy rebate" 10. **Fonte:** la pagina DOE (`energy.gov/scep/home-energy-rebates-programs`, 200) dice "available in select states… coming soon"; la pagina di stato è 404. **Google:** Rewiring America con il calcolatore per CAP, i programmi statali, le aziende elettriche. **Chi paga:** EnergySage 9,60 $ a contatto (directory terze, non letto). **Esito:** NO.

---

## 3. Cosa ho imparato (per i prossimi giri)

1. **Il salto di valore non viene dalla pubblicità ma dalla commissione per cliente.** A parità di visite, una pagina con un pagatore da 100-300 $ vale 10-30 volte una pagina con solo AdSense, anche "finanza". Le idee con solo pubblicità (zone di opportunità, tetti agli affitti, Hebesatz) restano a 1.600-2.300 € nel caso centrale anche con un pubblico ricco.
2. **I pagatori ricchi scrivono la cifra quando vendono a imprese** (Northwest, ZenBusiness, Gusto, Quaderno); quando vendono a persone (assicurazioni casa, conti aziendali tedeschi, pompe di calore) quasi mai.
3. **Dove le imprese cercano numeri ufficiali per Stato, il pagatore scrive già le pagine** (ZenBusiness, LegalZoom, Gusto, Avalara). Il nostro vantaggio possibile non è Google ma gli assistenti AI: fonte ufficiale, data, registro dei cambi, nessuna contraddizione. È lo stesso vantaggio che fa arrivare ChatGPT su Visa Income.
4. Fonti nuove da ricordare: CSV Destatis per Comune (DL-DE/BY 2.0); tabella DOL semestrale dei contributi di disoccupazione (pubblico dominio); calendario della Rev. Proc. 2026-14 per le zone di opportunità.

## 4. Il vincolo da allentare per una seconda idea da 10.000 €

Con le regole di oggi (niente vendita di contatti prima del cancello fiscale, niente spese), la seconda idea indipendente da 10.000 € centrali non l'ho trovata in questo fronte. Due strade, da decidere con i numeri:
- **Contatti venduti a prezzo fisso** (fase 2, dopo il consulente fiscale): FloodCost + tetti agli affitti + moratorie California verso assicurazioni casa (Lemonade 15 $, Allstate fino a 28 $; già in `fronti-2026-10-31-modelli.md`) porterebbe il blocco "proprietari di casa USA" verso 5-10.000 €.
- **Account su PartnerStack e Awin a nome di Massimiliano** (piccolo passo, zero euro): sblocca Gusto, Northwest, ZenBusiness e altri pagatori B2B per tutta la rete.

## 5. Proposta a Massimiliano (sì/no, una volta)

**Sito nuovo "US Small Business by State" (1A + 1B), voto 6,5, 1.450 / 17.900 / 97.200 €/anno a 18 mesi, 60-85 ore, 0 €.** Supera i 5.000 € centrali ma non il voto 7 per un sito nuovo: per la regola del 17/10 si propone "con potenziale chiaramente più alto". Prima di costruire (2-3 ore, senza chiedere nulla): **prova tecnica** dei 51 Stati (quanti si leggono in automatico, obiettivo ≥ 45) e controllo delle 30 cifre più cercate contro la fonte. Se passa: verificatore indipendente, poi costruzione al posto del primo sito congelato a fine novembre. A Massimiliano servirebbero: l'iscrizione ai programmi su Awin (Northwest, ZenBusiness) e su PartnerStack (Gusto) dopo le prime 40 pagine, e il nuovo sito su Netlify.

## 6. Fonti lette oggi (31/10/2026)

- Northwest Registered Agent, programma di affiliazione: https://www.northwestregisteredagent.com/affiliate-program (200)
- ZenBusiness, programma di affiliazione: https://www.zenbusiness.com/affiliate-program/ (200)
- Gusto su PartnerStack: https://market.partnerstack.com/page/gusto (200)
- Quaderno, affiliati: https://www.quaderno.io/affiliates (200)
- Tax Sale Resources, affiliati: https://affiliates.taxsaleresources.com/faq.php (200)
- California FTB, LLC: https://www.ftb.ca.gov/file/business/types/limited-liability-company/index.html (200); Texas SOS tariffe: https://www.sos.state.tx.us/corp/fees.shtml (403)
- DOL, Significant Provisions July 2026: https://oui.doleta.gov/unemploy/content/sigpros/2020-2029/July2026.pdf (200); https://oui.doleta.gov/unemploy/statelaws.asp (200)
- IRS Rev. Proc. 2026-14: https://www.irs.gov/pub/irs-drop/rp-26-14.pdf (200); CDFI Fund: https://www.cdfifund.gov/opportunity-zones (200); HUD: https://opportunityzones.hud.gov/ (200)
- Oregon OEA: https://www.oregon.gov/das/oea/Pages/Rent-Stabilization.aspx (200); Ontario: https://www.ontario.ca/page/rent-increase-guideline (200); California DIR: https://www.dir.ca.gov/OPRL/CPI/EntireCCPI.PDF (200); Washington Commerce (403)
- CDI Bulletin 2026-01: https://www.insurance.ca.gov/0250-insurers/0300-insurers/0200-bulletins/bulletin-notices-commiss-opinion/upload/Bulletin-2026-01-One-Year-Moratorium.pdf (200)
- Destatis, Hebesätze per Comune 2024 (CSV): https://service.destatis.de/DE/karten/hebesaetze-gemeinden-2024/data/hebesaetze-gemeinden-2024.csv (200); Realsteuervergleich 2025 (xlsx, 200); Regionaldatenbank (accesso richiesto)
- Finom, partner: https://finom.co/de-de/partnership/ (nessuna cifra)
- DOE Home Energy Rebates: https://www.energy.gov/scep/home-energy-rebates-programs (200, "coming soon")
- Minnesota Paid Leave: https://paidleave.mn.gov/employers/premiums (200); CSLB: https://www.cslb.ca.gov/About_Us/Library/Fees.aspx (200); BC affitti brevi: https://www2.gov.bc.ca/gov/content/housing-tenancy/short-term-rentals/principal-residence-requirement (200)
- Prima pagina (ricerca web dagli USA): llcuniversity.com, legalzoom.com, zenbusiness.com/texas-filing-fees, onpay.com/insights/sui-tax-rates, patriotsoftware.com, eddy.com, finanz-rechner-hub.de, rechner-hub.de, steuerschroeder.de, londonpropertylicensing.co.uk, nrla.org.uk, bnbcalc.com, steadily.com/blog, goodlifemgmt.com
