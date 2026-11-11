# Fronte nuovo dell'11/11/2026: dati ufficiali sulla CASA nel Regno Unito

Domanda: fra i dati ufficiali britannici sulla casa (tasse comunali, energia, acqua, banda larga, contributi, traslochi, zone a pagamento) ce n'è uno con le 4 prove (domanda, dati leggibili, pagatore che possiamo usare, nessuno che lo fa già meglio)?

Tutto letto l'11/11/2026 con curl dal server, salvo dove scrivo "ricerca web" (titoli e riassunti: usati per trovare gli indirizzi e, dove lo dico, per cifre non lette da me). Cambio: 1 £ = 1,15 €. Autocomplete Google con `gl=gb&hl=en`. Parole cercate prima in `ESPLORATE.md`: council tax, EPC, Ofgem, price cap, heat pump, Boiler Upgrade, broadband, Land Registry, ULEZ, clean air zone, conveyancing, removals, stamp duty, MOT, water bill, TV licence, warm homes. Già decisi e non ripetuti: council tax 2027 per council (NO, siti automatici già presenti), maggiorazione seconde case (riserva 4,5), EPC per area (NO), zone a basse emissioni (NO, 4 volte), MOT per modello (NO), pompe di calore per council (NO il 31/10 perché "nessun programma per editori con cifra": **questo fatto è cambiato**, vedi sotto).

## 0. Risposta in breve

**Una sola cosa nuova regge, ed è nata due settimane fa.** Il 27-28/10/2026 il governo britannico ha aperto il **Warm Homes Loan Scheme**: prestiti a tasso zero o ridotto (fino a 5 punti in meno) per pannelli solari, batterie e pompe di calore, in tutto il Regno Unito, dati da **10 finanziatori** elencati su GOV.UK. GOV.UK scrive: "contattate i finanziatori per tassi e durate". **Nessuno dei tre concorrenti letti (Uswitch, FMB, Homebuilding) scrive un solo tasso**: elencano i 10 nomi e basta. I tassi esistono sulle pagine dei finanziatori (letti 3 su 10). E per la prima volta c'è un pagatore con la cifra scritta su Awin per chi compra questi impianti: **Glow Green 300 £ a impianto solare, 250 £ a pompa di calore, 100 £ a caldaia, 50 £ a batteria**; BOXT 35 £ a vendita.

Il resto del fronte "casa UK" è occupato: per tariffe dell'energia, acqua, banda larga, traslochi, prezzi delle case e zone a pagamento rispondono già l'ente ufficiale, MoneySavingExpert, Uswitch e i pagatori stessi.

**Nessuna idea passa l'asticella dei siti nuovi (voto ≥ 7 e ≥ 5.000 € centrali).** La migliore ha voto 6 e 2.150 € centrali: entra in coda per la regola del 10/11 (nessuna soglia, ordine per €/ora), con verificatore prima di costruire perché tocca soldi e credito.

| # | Idea | Chi paga (cifra letta) | Voto severo | Prudente / centrale / ottimista (€/anno a 18 mesi) | Ore (agenti + proprietario) | 4 prove |
|---|---|---|---|---|---|---|
| 1 | **Prestiti Warm Homes: i 10 finanziatori a confronto** (tasso, durata, importo massimo, tecnologie, installatori ammessi) + calcolo della rata | Glow Green su Awin: 300 £ solare, 250 £ pompa di calore, 50 £ batteria; BOXT 35 £; AdSense | **6** | 90 / 1.740 / 16.800 | 15-20 + 1 | 3,5 su 4 (vuoto dimostrato ma fragile; tassi letti per 3 finanziatori su 10) |
| 2 | **Warm Homes: Local Grant per council** (279 council, fondi assegnati, capofila del consorzio, codici postali idonei) nello stesso sito | AdSense; BOXT 35 £ per chi non ha diritto | **5** | 50 / 410 / 3.000 | 15-20 + 0 | 3 su 4 (ogni council risponde per sé) |
| 3 | Tariffe dei council per la casa (rifiuti da giardino, ingombranti, passo carrabile, permesso di sosta) | Solo AdSense | **4,5** | 50 / 840 / 4.500 | 60-90 + 0 | 2 su 4 (dati sparsi su ~300 siti, nessun pagatore) |
| 4 | Spegnimento del telefono fisso per centrale (Openreach "stop sell") | BT 25 £ a contratto, MoneySuperMarket 10 £ | **4** | 20 / 250 / 2.000 | 12-15 + 0 | 2 su 4 (scadenza 31/1/2027 troppo vicina, un controllo per codice postale esiste già) |

**Proposta:** le idee 1 e 2 sono lo stesso sito in inglese ("Warm Homes Plan con i dati ufficiali": prestiti + contributi), **non una sezione di Before You Fly** (tema senza legame con i voli). Insieme: **140 / 2.150 / 19.800 €/anno**, 30-40 ore, cioè circa 60 € centrali per ora. Prima di costruire: verificatore indipendente su tre punti (sezione 6).

## 1. Fonte esterna da cui nasce

- GOV.UK, guida "Warm Homes Loan Scheme" pubblicata il **28/10/2026** e scheda del **27/10/2026** (letti dall'API dei contenuti di GOV.UK): prestiti per chi possiede la casa, in tutto il Regno Unito; importi massimi: solare 15.000 £, batteria 15.000 £, pompa di calore aria-acqua 20.000 £, geotermica 35.000 £; "fino a 5 punti percentuali in meno", "alcuni senza interessi", "fino a trent'anni in alcuni casi"; cumulabile con il Boiler Upgrade Scheme (la scheda dice "fino a 9.000 £"); installatore certificato MCS obbligatorio; "altri finanziatori e prodotti in arrivo".
- I 10 finanziatori: HomeServe Finance (con E.ON), Hometree Finance, The Money Co-op, Propensio, Secure Trust Bank, Selina Finance, South Manchester Credit Union, Sunsave, Tandem Bank, thisbank.
- Awin, schede pubbliche dei programmi (lette): Glow Green (ID 73922), BOXT (ID 13574), OVO Solar & Heating (ID 122556), EDF Zero Carbon Homes (ID 129571), Heatable (ID 18758).

## 2. Idea 1: prestiti Warm Homes, i finanziatori a confronto

### Domanda (autocomplete, gl=gb)
| Ricerca | Suggerimenti |
|---|---|
| warm homes loan scheme … | 10 (lenders, rules, launch date, start date, when, gov) |
| warm homes loan … | 10 (scheme lenders, **providers**) |
| warm homes plan loans … | 10 (loan scheme, consumer loans, **0 loan**, low interest, interest free, solar loans) |
| warm homes plan solar … | 10 (solar loan, solar and battery, plug in solar) |
| 0 interest solar panels … | 10 (0 finance solar panels uk, no interest solar panel loans) |
| interest free heat pump … | 10 (loan, installation, government interest free loan for heat pump) |
| warm homes plan | 10 (2026 start date, loans, 2027, how to apply) |
| warm homes loan scheme interest rate | **0** |
| warm homes loan scheme + lettera (b, n, h) | **0** (i nomi dei finanziatori non sono ancora cercati) |

Lettura onesta: la domanda c'è sulle parole generali ed è giovane (due settimane); **non c'è ancora coda lunga per finanziatore**. Crescerà solo se lo schema prende piede.

### Dati leggibili
- GOV.UK: elenco finanziatori, importi massimi, regole (PDF "scheme rules" di settembre 2026): 200, licenza aperta OGL.
- Tassi, letti su 3 finanziatori su 10: **HomeServe/E.ON** "senza interessi fino a 5 anni per il solare e 6 per le pompe di calore, oppure 10 anni al 4,6 % TAEG", reddito minimo 12.000 £ (pagina eonnext.com, 200); **South Manchester Credit Union** "da 1.000 a 15.000 £, dal 3,6 % TAEG" (home page, 200); **Sunsave** "prestito allo 0 %" con più durate (200). Tandem, Hometree e Secure Trust: gli indirizzi provati danno 404 (pagina non trovata, non un blocco); The Money Co-op non ha risposto. **Da completare a mano prima di costruire: 7 finanziatori.**
- Non è un file unico: sono 10 pagine da rileggere ogni mese (i tassi cambiano e i finanziatori aumentano). È lavoro di routine, non un dato scaricabile.

### Concorrenti letti su 5 esempi concreti
Esempi: il tasso di 5 finanziatori (HomeServe/E.ON, South Manchester CU, Sunsave, Tandem, Hometree).

| Concorrente (data della pagina) | Nomina i 10 finanziatori | Tassi scritti su 5 | Cosa manca |
|---|---|---|---|
| Uswitch, guida "warm-homes-loan-scheme" (200) | sì | **0 su 5** | nessun tasso, nessuna durata, nessun confronto |
| FMB HomePicks (3/11/2026, 200) | sì, una volta ciascuno | **0 su 5** | idem |
| Homebuilding & Renovating (28/10/2026, 200) | 9 su 10 | **0 su 5** | idem |
| Sunsave (finanziatore e venditore, 200) | sì | 1 su 5 (solo il suo) | parla di sé |
| E.ON Next (venditore, 200) | no | 1 su 5 (solo il suo) | parla di sé |
| Heatable, Energy Saving Trust, Selectra | non letti: 403 (protezione anti-bot, non aggirata) | – | – |
| MoneySavingExpert | nessuna guida trovata all'indirizzo provato (404); solo una notizia di gennaio | – | – |

**Vuoto dimostrato oggi:** una tabella sola con tasso, durata, importo, tecnologie, zone e "con quali installatori" per ogni finanziatore non esiste nelle pagine lette. **È fragile:** MoneySavingExpert, Which? e i comparatori possono farla in pochi giorni; Uswitch è già in pagina con il titolo giusto.

### Chi paga
| Programma | Cifra | Dove letta | Per noi |
|---|---|---|---|
| Glow Green (Awin 73922) | **100 £ caldaia, 300 £ solare, 250 £ pompa di calore, 50 £ batteria, 25 £ climatizzatore, 10 £ colonnina**; cookie 30 giorni | scheda Awin, letta | Awin UK lo usiamo già; l'approvazione di un editore italiano va chiesta (non verificabile da qui) |
| BOXT (Awin 13574) | **35 £ a vendita completata** (caldaie, solare, batterie, pompe di calore, climatizzatori, colonnine); cookie 30 giorni | scheda Awin, letta (una directory riportava 42 £: vale la scheda) | idem |
| Heatable (Awin 18758) | "tariffe alte, negoziabili": nessuna cifra | scheda Awin, letta | senza cifra non conta |
| OVO Solar & Heating (122556), EDF Zero Carbon Homes (129571) | cifra non visibile senza accesso | schede Awin, lette | da leggere dal pannello Awin |
| Quotatis | 40 £ a richiesta di preventivo solare | solo ricerca web, post Awin senza data | non contata |

EPC e tasso di conversione non sono nelle schede pubbliche: la stima usa conversioni severe.

### Stima a 18 mesi
Formula: visite × clic verso l'installatore × vendita completata × 230 € (media prudente fra 300, 250 e 50 £) + visite × RPM AdSense.
- **Prudente:** 5.000 × 3 % × 0,15 % × 230 = ~50 € + 5.000 × 8 €/1.000 = 40 € → **90 €**
- **Centrale:** 30.000 × 5 % × 0,4 % × 230 = 1.380 € (6 vendite) + 30.000 × 12 €/1.000 = 360 € → **1.740 €**
- **Ottimista:** 110.000 × 6 % × 1 % × 230 = 15.180 € (66 vendite) + 110.000 × 15 €/1.000 = 1.650 € → **16.800 €**

Le visite centrali presuppongono di arrivare fra i primi 5 risultati su "warm homes loan scheme lenders" e sulle ricerche "0 % solar loan" entro l'estate 2027: non scontato contro Uswitch.

### Rischi
1. **Credito regolato.** Presentare clienti a un finanziatore in cambio di denaro nel Regno Unito è intermediazione del credito (serve autorizzazione FCA). Quindi: **nessun compenso dai finanziatori**, solo collegamenti semplici alle loro pagine; il guadagno viene dagli installatori (vendita di un impianto) e dalla pubblicità. Da far confermare al verificatore prima di costruire.
2. Vuoto che si può chiudere in fretta (vedi sopra).
3. Pagine su soldi e casa: Google chiede fonti e autorevolezza; un dominio nuovo parte in salita.
4. Tassi che cambiano: un tasso sbagliato è un danno per il lettore → data di lettura accanto a ogni cifra e controllo mensile.
5. Schema nuovo: se l'adesione è bassa, la domanda resta piccola.

## 3. Idea 2: Warm Homes: Local Grant per council

Contributo fino a 30.000 £ di lavori gratuiti per famiglie a basso reddito (≤ 36.000 £), case private con classe energetica D-G, solo Inghilterra, consegnato dai council fino al 2028. Con la fine di ECO4 è la via principale ai lavori gratuiti.

- **Domanda:** "warm homes local grant" + lettera dà 10 suggerimenti con i nomi dei council per ogni lettera provata (b: Birmingham, Bradford, Bristol, Blackpool, Bedford, Barnsley, Bucks, Brent; c: Cornwall, Coventry, Cumberland, Calderdale; n: Nottingham, Newcastle, Norwich, North Yorkshire, North Tyneside, Northumberland, Norfolk, Northampton; s: Sheffield, Somerset, Sefton); "eligible postcodes" 10; "warm homes grant" 10 (Cornwall, Leeds, North Yorkshire). È la domanda più forte trovata oggi.
- **Dati (GOV.UK, OGL, 200):** elenco dei council finanziati con la cifra e i membri di ogni consorzio (pagina HTML, es. Blackpool 35.324.700 £ per 13 council del Lancashire; Bristol 12.662.001 £ con Bath e North Somerset); file xlsx dei **codici postali idonei: 254.014 codici, 6.751 zone, 279 council** (Birmingham 376 zone, Manchester 162, Bradford 149; contati da me sul file); statistiche trimestrali (5.300 famiglie fino a luglio 2026; costo medio per misura). Manca nei file: chi esegue i lavori e se le domande sono aperte, council per council (da leggere su ~100 siti dei capofila).
- **Concorrenti su 5 esempi (Birmingham, Cornwall, Leeds, Nottingham, Blackpool):** Uswitch (guida 2025-2028), MoneySavingExpert e FMB: **0 su 5 council nominati**, rimandano al controllo di GOV.UK. Ma **ogni council risponde per sé**: Birmingham scrive le sole 6 zone prioritarie e la piattaforma per la domanda; Cornwall dà l'indirizzo dell'ufficio (ricerca web sui siti dei council). E GOV.UK ha il controllo per codice postale che passa i dati al council.
- **Vuoto:** nessuno mette insieme fondi, capofila, zone idonee e stato per council; chi abita in un council "membro" (es. Burnley) non trova che il capofila è Blackpool. Vuoto parziale: stessa forma della maggiorazione sulla council tax (4,5), dove il council arriva primo sul proprio nome.
- **Chi paga:** pubblico a basso reddito → quasi solo AdSense; BOXT 35 £ per chi non rientra.
- **Stima:** visite × RPM: 8.000 × 6 € = **~50 €**; 45.000 × 9 € = **~410 €**; 250.000 × 12 € = **~3.000 €**.
- **Voto 5.** Da sola non vale un sito; come seconda gamba dell'idea 1 porta visite e collegamenti interni (chi supera i 36.000 £ va alla pagina prestiti).

## 4. Idea 3: tariffe dei council per la casa

- **Domanda:** "garden waste subscription" 10 (Colchester, Somerset, St Albans, Basildon, Nottingham, Wirral), "how much is garden waste collection in" 10, "brown bin charge" 10, "dropped kerb cost" 10 (Liverpool, Glasgow, Birmingham, Nottingham, Doncaster), "parking permit cost" 10, "bulky waste collection" 10, "council pest control" 10.
- **Dati:** nessun file unico; le cifre stanno nei listini di ~300 council (pagine e PDF delle delibere), da rileggere ogni primavera. Non ho provato quanti siti sono leggibili.
- **Concorrenti:** la ricerca web non trova un elenco completo (solo singoli council e guide con forbici: "50-400 £" per il passo carrabile). Non ho letto 3 concorrenti su 5 esempi → voto massimo 5 per regola. Ogni council risponde per sé.
- **Chi paga:** nessun programma; solo AdSense. Stima: 10.000 × 5 € = 50 €; 120.000 × 7 € = 840 €; 500.000 × 9 € = 4.500 €, con 60-90 ore e un rifacimento annuale: il peggior rapporto €/ora della lista.
- **Voto 4,5.** Riserva.

## 5. Idea 4: spegnimento del telefono fisso per centrale

- **Domanda:** "landline switch off" 10 (**postcode checker** ×4, 2027, date), "openreach stop sell" 10 (exchange list, areas, locations 2026), "when is my landline going digital" 10.
- **Dati:** elenco del piano fibra scaricabile da openreach.com (200); pagina "stop sell" sul portale Openreach (200); le tranche (112 centrali a ottobre 2026) escono ogni trimestre.
- **Concorrenti:** broadbandswitch.uk ha già un "landline switch-off checker" (200), ISPreview pubblica ogni tranche, i venditori di telefoni digitali pubblicano gli elenchi. **Scadenza nazionale 31/1/2027:** un sito nuovo non fa in tempo.
- **Chi paga (Awin, letto):** BT 25 £ a nuovo contratto di banda larga, 20 £ TV; MoneySuperMarket Broadband 10 £. Hyperoptic 75 £ solo da ricerca web.
- **Voto 4**; 20 / 250 / 2.000 €.

## 6. Dove va e cosa serve prima di costruire

Sito nuovo in inglese sul piano "Warm Homes" (prestiti + contributi + Boiler Upgrade Scheme), non sezione di Before You Fly. Entra in coda con ~60 € centrali per ora. Il verificatore deve confermare:
1. che collegare i finanziatori senza compenso e guadagnare dagli installatori resta fuori dall'intermediazione del credito;
2. i tassi dei 7 finanziatori non letti (se meno di 7 su 10 pubblicano il tasso, la tabella perde valore);
3. che il vuoto esiste ancora (MoneySavingExpert, Which?, Uswitch) nel giorno della verifica.
Azioni del proprietario (1 ora, dopo il sì del verificatore): pubblicazione su Netlify e richiesta ai programmi Glow Green e BOXT dal conto Awin.

## 7. Scartate oggi, con il motivo

| Dato | Motivo |
|---|---|
| Tetto Ofgem per regione ("price cap unit rates" 10, "standing charge by region" 8) | Ofgem pubblica la tabella per regione; MoneySavingExpert e ogni fornitore la ripetono: nessun vuoto (concorrenti non letti: voto massimo 5 comunque) |
| Bollette dell'acqua 2027 per società ("water bill increase 2027" 10 con Southern, Thames, Anglian) | l'acqua non si può cambiare: nessun pagatore; picco solo a febbraio-aprile; stampa e MoneySavingExpert |
| Banda larga per città, reti alternative ("community fibre vs" 10, "is hyperoptic available" 10) | pagatori buoni ma i dati aperti di Ofcom non dicono quale rete c'è; comparatori e siti di copertura già presenti |
| Costi di trasloco e notai ("removal costs" 10, "conveyancing fees for" 10) | reallymoving e Compare My Move vendono contatti alle imprese, **nessun programma per editori trovato** (/affiliates 404 su entrambi); i pagatori pubblicano già le guide ai costi |
| Clean air zone per città ("clean air zone charge" 10 con 8 città) | già NO quattro volte; controllo ufficiale per targa; chi compra auto usate pubblica il suo |
| EPC, prezzi del Land Registry, canone TV, scuole, MOT, council tax per fascia | già in ESPLORATE o risposta ufficiale per singola casa |

## 8. Fatto cambiato rispetto al 31/10

"Pompe di calore e Boiler Upgrade Scheme per council: NO, nessun programma per editori con cifra" → **il programma con la cifra esiste**: Glow Green su Awin paga 250 £ a pompa di calore e 300 £ a impianto solare. Il NO resta per la forma "per council" (la domanda è per nazione, non per council), ma il pagatore va tenuto per ogni pagina futura su casa ed energia nel Regno Unito.

## 9. Indirizzi letti

gov.uk/api/content/warm-homes-loan-scheme, /government/news/warm-homes-loan-scheme-factsheet, /apply-warm-homes-local-grant, /government/publications/warm-homes-local-grant (xlsx codici postali), /warm-homes-local-grant-successful-local-authorities, /government/statistics/warm-homes-local-grant-statistics-august-2026 (200); ui.awin.com/merchant-profile/73922, 13574, 18758, 122556, 129571, 3041, 25756 (200); uswitch.com guide warm-homes-loan-scheme e warm-homes-local-grant-scheme, fmb.org.uk/homepicks (due pagine), homebuilding.co.uk, sunsave.energy (due pagine), eonnext.com, smcreditunion.co.uk, moneysavingexpert.com/utilities/warm-homes-local-grant, broadbandswitch.uk, openreach.com (200); heatable.co.uk, energysavingtrust.org.uk, selectra.co.uk (403, non aggirati); reallymoving.com/affiliates, comparemymove.com/affiliates, boxt.co.uk/affiliates, uswitch.com/affiliates (404).
