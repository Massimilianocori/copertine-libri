# Fronte dell'11/11/2026: impianti per la casa nel Regno Unito (pompe di calore, solare) dai dati ufficiali

Domanda: con i pagatori trovati stamattina (Glow Green e BOXT su Awin), un sito inglese sugli **impianti** (mai sui prestiti) costruito sui dati ufficiali ha le 4 prove?

Tutto letto l'11-12/11/2026 con curl dal server, salvo dove scrivo "ricerca web" (titoli e riassunti, usati per vedere chi esce nei risultati: Google e DuckDuckGo non si leggono da qui). Cambio 1 £ = 1,15 €. Autocomplete Google con `gl=gb&hl=en`. Parole cercate prima in `ESPLORATE.md`: heat pump, pompe di calore, MCS, Boiler Upgrade, solar, Glow Green, BOXT. Precedenti: "pompe di calore e Boiler Upgrade Scheme per Comune" NO il 31/10 (voto 3-3,5) perché mancava un pagatore con cifra; il pagatore ora c'è, quindi l'idea si riapre e si rifà da zero.

## 0. Risposta in breve

**Nessuna idea passa l'asticella dei siti nuovi (voto ≥ 7 e ≥ 5.000 € centrali).** La migliore ha voto 5,5 e 1.300 € centrali; arriva a 18.000 € solo nell'ottimista.

| # | Idea | Chi paga (cifra letta) | Voto severo | Prudente / centrale / ottimista (€/anno a 18 mesi) | Ore (agenti + proprietario) | 4 prove |
|---|---|---|---|---|---|---|
| 1 | **Pompe di calore con il contributo, council per council** (318 council, 575 collegi, 10 regioni: impianti pagati dal Boiler Upgrade Scheme, anno per anno, costo mediano ufficiale, quanto resta da pagare dopo 7.500 o 9.000 £, regole) + solare domestico per collegio | Glow Green (Awin 73922): 250 £ a pompa di calore, 300 £ a impianto solare, 50 £ a batteria; BOXT (13574): 35 £ a vendita; AdSense | **5,5** | 40 / 1.300 / 18.000 | 20-25 + 1 | 3 su 4 (vuoto dimostrato sui numeri per council, ma la gente cerca "installatori a <città>", non il numero) |
| 2 | Costo del solare per regione e città (£ per kW dalla tabella ufficiale) | Glow Green 300 £ | **4** | 30 / 600 / 6.000 | 15-20 + 0 | 2 su 4 (**nessun vuoto**: ExpertSure e The Eco Experts lo fanno già con le stesse fonti) |
| 3 | Guida e controllo "ho diritto al contributo?" (regole nuove del 2026: 2.500 £ aria-aria, 9.000 £ fuori dalla rete del gas, attestato energetico non più obbligatorio) | Glow Green 250 £ | **4** | 20 / 400 / 4.000 | 8-10 + 0 | 2 su 4 (risponde GOV.UK; concorrenti non letti su 5 esempi: per regola voto massimo 5) |

**Proposta:** l'idea 1 non è una sezione di un sito esistente (nessuno dei nostri siti parla di case britanniche): sarebbe un sito nuovo in inglese, e come sito nuovo non passa. Va in **riserva costruibile**, in coda per €/ora (circa 55 € centrali per ora) dietro a ciò che rende di più. Le idee 2 e 3 hanno senso solo come pagine dentro l'idea 1, mai da sole. Tre cose da sapere prima di costruire sono in fondo (sezione 8).

**La scoperta utile sui dati:** il costo medio delle pompe di calore **per regione o per council non esiste in forma aperta**. Il file ufficiale dà il costo solo per l'intera Inghilterra e Galles (per trimestre e per potenza). Per regione lo mostra solo il cruscotto MCS, che è un'applicazione non leggibile con curl e senza licenza aperta scritta. Quindi "average cost of a heat pump in <region>" con fonte ufficiale non si può fare in automatico; "is the £7,500 grant enough in <region>" nemmeno.

## 1. Fonte esterna da cui nasce

- Awin, schede pubbliche dei programmi (rilette il 12/11): Glow Green 73922 e BOXT 13574, le uniche due con la cifra scritta per questi impianti.
- GOV.UK, "Boiler Upgrade Scheme statistics: September 2026" (pubblicato il 29/10/2026): settembre 2026 è il mese con più domande da quando esiste lo schema (9.738, +138 % su settembre 2025); dal 21/7/2026 il contributo sale a 9.000 £ per le case fuori dalla rete del gas scaldate a gasolio o GPL; dal 28/4/2026 c'è il contributo di 2.500 £ per le pompe aria-aria. Bilancio 2026/27: 400 milioni di sterline; schema finanziato fino al 2029/30.

## 2. Dati ufficiali (letti e aperti)

| Fonte | Cosa contiene | Dettaglio geografico | Aggiornamento | Licenza | Stato |
|---|---|---|---|---|---|
| DESNZ, Boiler Upgrade Scheme statistics (xlsx 1,1 MB, 30 fogli) | domande, buoni emessi, contributi pagati; costo mediano e quartili; potenza | contributi pagati per **318 council** (foglio Q1.2), per **collegio** (Q1.3), per anno (A1.7, A1.8); domande per regione ogni mese (M1.2) e ogni 10.000 famiglie (1.2B) | mensile; council e costi ogni tre mesi | OGL | 200 |
| stesso file, fogli Q1.1A e A1.3A | **costo**: mediana aria-acqua 12.826 £ nel terzo trimestre 2026 (quartili 10.717 e 15.461 £), geotermica 34.630 £; costo per fascia di potenza (da 11.494 £ per 4-6 kW a 15.498 £ per 14-16 kW nel 2025/26) | **solo Inghilterra e Galles insieme: nessuna regione, nessun council** | trimestrale | OGL | 200 |
| DESNZ, Heat pump deployment statistics (xlsx 57 KB) | pompe di calore installate su case esistenti, dal registro MCS | regione e trimestre (12 aree, Scozia compresa); nessun costo | trimestrale (ultimo: 10/9/2026) | OGL | 200 |
| DESNZ, Solar PV cost data (xlsx) | costo medio del solare in **£ per kW per regione** (11 aree, tre anni, tre fasce di potenza). 2025/26, fascia 0-4 kW: da 1.878 £ (Nord Est) a 2.177 £ (Londra e Sud Ovest) | regione | **annuale** (28/5/2026; prossimo 27/5/2027) | OGL | 200 |
| DESNZ, Solar photovoltaics deployment (ET 6.3, xlsx 0,9 MB) | impianti solari domestici e potenza | **per collegio** (circa 650; es. Bishop Auckland 3.755 impianti) e per regione | mensile | OGL | 200 |
| DESNZ, Renewable electricity by local authority 2014-2025 (xlsx 3,4 MB) | impianti e potenza solare per council | council | annuale (29/9/2026) | OGL | 200, fogli non aperti |
| GOV.UK, "Apply for the Boiler Upgrade Scheme" | regole: proprietario dell'immobile, sostituzione di un impianto a combustibile fossile, un contributo per immobile, niente sistemi ibridi, installatore MCS, 120 giorni per installare, biomassa solo in zona rurale fuori rete | Inghilterra e Galles | quando cambia | OGL | 200 |
| **Cruscotto MCS** (datadashboard.mcscertified.com) | impianti, costi medi e potenza per tecnologia e luogo, aggiornato ogni 24 ore; esportazioni scaricabili | regione e council | giornaliero | **nessuna licenza aperta letta**; MCS scrive "gratuito, senza limiti di accesso" e che gli piace vedere i dati "condivisi" | **non leggibile**: è un'applicazione (la pagina data a curl è vuota); l'unica risposta leggibile è il numero di versione, 3.0.8 |

Esempi letti dal file dei contributi (pompe di calore pagate, maggio 2022 - settembre 2026): Cornwall 3.448, Wiltshire 1.794, Leeds 889, Bristol 689, Birmingham 530, Gwynedd 340, Camden 154. Totale 96.185; Sud Est 19.069, Sud Ovest 17.168, Nord Est 3.033.

Limiti scritti chiari:
- 62 council su 318 hanno almeno una cella oscurata per numeri piccoli (quasi sempre la biomassa, non le pompe di calore).
- Il contributo vale solo in Inghilterra e Galles: per Scozia e Irlanda del Nord non c'è un numero per council.
- La guida GOV.UK scrive "1.500 £ in più fino a marzo 2027" per le case a gasolio o GPL; il file statistico scrive "9.000 £". È la stessa cosa detta in due modi: la pagina deve citare tutte e due le fonti con la data.
- Le cifre del cruscotto MCS si potrebbero copiare a mano con la citazione (lo fa The Eco Experts), ma servirebbe una persona con un browser ogni mese e il permesso non è scritto. Non ci conto.

## 3. Domanda (autocomplete Google, gl=gb, 12/11)

| Ricerca | Suggerimenti | Lettura |
|---|---|---|
| boiler upgrade scheme | 10 (eligibility, air to air, statistics, end date, rules) | forte, nazionale |
| boiler upgrade scheme eligibility | 10 (criteria, **checker**, gov uk, wales) | forte, risponde GOV.UK |
| heat pump grant 9000 | 10 | nuova (luglio 2026) |
| air to air heat pump grant | 10 (2500, eligibility, england) | nuova (aprile 2026) |
| is the 7500 heat pump grant | 8 (worth it, good) | c'è |
| heat pump cost after grant | 9 | c'è |
| average cost of heat pump installation uk | 8 | c'è, nazionale |
| heat pump cost scotland / london | 10 / 8 | regionale: c'è |
| heat pump cost south west | 4 | regionale: debole |
| heat pump installers cornwall / leeds | 7 / 9 | locale: **si cercano gli installatori** |
| heat pump grant cornwall | 7 (cornwall council) | locale: c'è |
| boiler upgrade scheme cornwall / leeds | 4 / 3 (quasi tutti "council") | locale: debole |
| boiler upgrade scheme statistics | 8 | piccola, da addetti |
| how many heat pumps installed in | 10, **tutti nazionali** (uk, ireland) | **nessuna ricerca per council** |
| solar panels leeds / bristol / birmingham | 10 / 10 / 10 (cost, grants, installation, free) | locale: forte |
| solar panels cost leeds | 8 | locale: c'è |
| solar panel cost per kw uk | 4 | debole |
| mcs data dashboard | 5 | piccola |

Lettura onesta: la domanda locale esiste, ma è "installatori a <città>", "solare a <città> costo", "contributo a <council>". **Il numero che abbiamo solo noi ("quante pompe di calore a <council>") non lo cerca nessuno**: può stare nella pagina come prova e come aggancio per la stampa locale, non come motivo della visita. Volumi non misurabili da qui: le stime sotto sono quote ipotizzate.

## 4. Concorrenti letti su 5 esempi concreti

Esempi: (a) costo di una pompa di calore nel Sud Ovest; (b) Boiler Upgrade Scheme in Cornwall; (c) costo del solare a Leeds; (d) quante pompe di calore a Birmingham; (e) £ per kW del solare a Londra.

| Concorrente (pagina letta, stato) | Cifra ufficiale per l'area, con fonte | Cosa manca |
|---|---|---|
| **The Eco Experts**, costo del solare (200, aggiornata il 19/10/2026, 7.500 parole) | **sì per (e)**: tabella £ per kW e spesa media per regione, fonte dichiarata "MCS Data Dashboard" | nessun council, nessuna città (Leeds 0 volte) |
| The Eco Experts, costo delle pompe di calore (200, 5.400 parole) | **no**: nessuna regione, nessun council, nessuna mediana ufficiale | tutto il dettaglio geografico |
| **ExpertSure**, "solar panel costs by region" (200, 5.600 parole) e pagina "solar panels Leeds" (200, 4.600 parole) | **sì per (c) ed (e)**: £ per kW per regione, fonte dichiarata "DESNZ 2025/26, maggio 2026"; pagina per città con prezzo regionale, ore di sole, produzione | il numero di impianti del council o del collegio non c'è; le sue cifre (Londra 1.759 £/kW) non coincidono con la tabella che ho letto io (Londra 2.007 £/kW di media): forse usa l'altra base di calcolo, non verificato |
| **ukheatpumpguide.pages.dev**, "installers/bristol" (200, 950 parole; sito automatico con pagina per città) | **no**: "50+ installatori MCS", nessun numero ufficiale di Bristol (689), nessuna fonte per le cifre | dati; scrive "non affiliato con alcun installatore" |
| heatpumpcheck-uk.pages.dev, costi (200) | **no**: fasce per regione ("Sud Ovest 9.500-14.000 £") senza fonte verificabile | fonte |
| tradecost-uk.pages.dev, Southwark (200; 260 città) | **no**: fascia "10.400-20.800 £" senza fonte | fonte |
| Fuse Energy, "heat pump Birmingham" (200, 1.250 parole; venditore, una pagina per città) | **no**: nessun numero di Birmingham | dati; parla di sé |
| OVO, "heat pump installation / south west" (200, 670 parole; venditore) | **no** | dati; parla di sé |
| hamuch.com, costo per zona (200) | **no** | fonte |
| Cruscotto MCS | sì, ma è uno strumento da addetti, non una pagina che esce su Google | non risponde "quanto pago io" |
| Cornwall Council (ricerca web) | no: "il council non ha alcun ruolo nello schema, contattate gli installatori" | – |
| Heatable, Checkatrade (403, protezione anti-bot non aggirata); GreenMatch e Octopus (pagine che si compongono nel browser: testo non leggibile) | non letti | – |

**Risultato sui 5 esempi:**
- (b) e (d), numeri del contributo per council: **0 pagine su 9 lette**. La ricerca web su "quante pompe di calore a Birmingham" e "Boiler Upgrade Scheme Cornwall" non trova la cifra da nessuna parte (solo un articolo del 2023). **Vuoto dimostrato.**
- (a), costo della pompa di calore per regione con fonte: 0 su 9, ma **il dato aperto non esiste nemmeno per noi**. Non è un vuoto che possiamo riempire.
- (c) ed (e), solare per regione e città: **già fatto** da due siti con le nostre stesse fonti. Nessun vuoto.

Seconda lettura, meno comoda: su "installatori a <città>" e "costo a <città>" ci sono già **almeno cinque siti automatici con una pagina per città** (tre su pages.dev, hamuch, ExpertSure) più i venditori (Fuse, OVO). Sono poveri di dati, ma occupano le parole. Il nostro vantaggio sarebbe solo la cifra ufficiale con la fonte.

## 5. Chi paga

| Programma | Cifra | Dove letta | Per noi |
|---|---|---|---|
| **Glow Green** (Awin 73922) | **300 £ solare, 250 £ pompa di calore, 100 £ caldaia, 50 £ batteria, 25 £ climatizzatore, 10 £ colonnina**; cookie 30 giorni | scheda pubblica Awin, 200, riletta il 12/11 | cifra confermata. **Non visibili** nella scheda: EPC, tasso di conversione, zone servite, tempi di convalida, accettazione di editori non britannici. Il sito glowgreen.co.uk dà 403: zone non lette |
| **BOXT** (Awin 13574) | **35 £ a vendita completata**, "installazione in tutto il Paese"; cookie 30 giorni | scheda pubblica Awin, 200 | confermata; cifra bassa per impianti da 10.000 £ |
| Heatable (18758) | nessuna cifra | scheda, 200 | non conta |
| OVO Solar & Heating (122556), EDF Zero Carbon Homes (129571) | nessuna cifra nella scheda pubblica | schede, 200 | da leggere dal pannello Awin |
| **Octopus** | 100 £ in buono regalo a testa per pompa di calore o solare | pagina "lct-referral", 200 | **non usabile**: è un invito fra clienti (serve aver comprato un impianto Octopus; premio in buoni, a impianto finito; vietato sullo stesso indirizzo). Il programma per editori di Octopus (50 £) riguarda i contratti di fornitura, non gli impianti (ricerca web, non letto) |
| Altri su Awin trovati dalla ricerca web (Renogy, Sunjoy 5 %, Shelly 4 %, Symphony 5 %) | percentuali su prodotti da scaffale | schede, 200 | fuori tema (non sono installatori) |
| Sunsave, Otovo, Aira, Good Energy, MakeMyHouseGreen | nessun programma per editori trovato | ricerca web | non contati |

Quindi: **un solo pagatore vero** (Glow Green). Se rifiuta il nostro conto o chiude il programma, resta BOXT a 35 £ e la pubblicità.

Regola legale (dalla verifica di stamattina): nessuna pagina sui prestiti, nessuna parola "finance", "loan", "0 %", "monthly payments"; il link all'installatore dice solo "get a quote". Glow Green e OVO propongono il finanziamento sulle loro pagine: il nostro link deve stare solo in pagine sull'impianto. Il rischio residuo è piccolo ma non è zero, e va fatto leggere al verificatore.

## 6. Stima (idea 1, con dentro le pagine delle idee 2 e 3)

**Formula:** visite × clic verso l'installatore × impianti completati per clic × commissione media (260 £ = 300 €) + visite × pubblicità per 1.000 visite.

| Scenario | Visite/anno a 18 mesi | Clic | Impianti per clic | Commissioni | Pubblicità | Totale |
|---|---|---|---|---|---|---|
| Prudente | 5.000 | 3 % | 0,15 % | 7 € | 6 € × 5 = 30 € | **~40 €** |
| Centrale | 24.000 | 5 % | 0,3 % | 3,6 impianti = 1.080 € | 10 € × 24 = 240 € | **~1.300 €** |
| Ottimista | 150.000 | 6 % | 0,6 % | 54 impianti = 16.200 € | 12 € × 150 = 1.800 € | **~18.000 €** |

Assunzioni e perché sono basse:
- Visite: circa 900 pagine (318 council, 575 collegi, regioni, guide) su un dominio nuovo, in un tema dove scrivono GOV.UK, The Eco Experts, Heatable, Octopus e cinque siti automatici. Centrale: 2.000 visite al mese. Le tre verifiche del 10/11 hanno tagliato le stime dei ricercatori di metà o più: qui parto già bassa.
- Impianti per clic: una pompa di calore costa 12.800 £, richiede un sopralluogo e mesi di decisione; il cookie dura 30 giorni. 0,3 % è un'ipotesi, **non un dato**: la scheda Awin non mostra né conversione né EPC. È il numero che sposta tutto: a 0,1 % il centrale scende a 600 €.
- Pubblicità: 6-12 € per 1.000 visite (tema casa, Regno Unito), non misurata.
- Ore: 20-25 di agenti (lettura dei 4 file, pagine, controlli) + 1 di Massimiliano (richiesta ad Awin). Aggiornamento: un comando al mese (i file hanno nome diverso ogni mese, ma l'indirizzo si legge dall'API di GOV.UK).

Idea 2 da sola (solare per regione e città): 30 / 600 / 6.000 €. Idea 3 da sola (regole del contributo): 20 / 400 / 4.000 €. Non si sommano all'idea 1: sono le stesse visite.

## 7. Le 4 prove

| Prova | Idea 1 (contributo per council) | Idea 2 (solare per regione) | Idea 3 (regole) |
|---|---|---|---|
| Domanda | **a metà**: forte sul contributo e sugli installatori per città; zero sul numero per council | sì | sì, forte |
| Dati ufficiali leggibili | **sì** per i conteggi (OGL, mensili); **no** per il costo per regione | sì, ma annuali | sì |
| Pagatore che possiamo usare | **sì con riserva**: cifra letta, accettazione e conversione ignote; un solo pagatore | idem | idem |
| Nessuno lo fa già meglio | **sì** per i numeri per council (0 su 9); no per le parole "installatori a <città>" | **no** (ExpertSure, The Eco Experts) | **no** (GOV.UK; concorrenti non letti) |
| Totale | **3 su 4** | 2 su 4 | 2 su 4 |

Voti: **5,5**, **4**, **4**. Il voto dell'idea 1 resta sotto 6 perché il vuoto dimostrato è su un numero che nessuno cerca, e il pagatore è uno solo e non verificato.

## 8. Dove va e cosa chiedere prima

- **Dove:** sito nuovo in inglese, non una sezione (Before You Fly parla di voli, gli altri siti di Italia e Stati Uniti). Come sito nuovo non passa l'asticella: **riserva costruibile**. Ottimista sopra 10.000 €: segnalato.
- **Tre cose che la farebbero salire a 6,5-7:**
  1. Glow Green accetta il nostro conto Awin e dal pannello si leggono conversione ed EPC (azione di Massimiliano, 10 minuti; costo 0 €). Con una conversione vera sopra 0,5 % il centrale passa 2.000 €.
  2. OVO o EDF mostrano nel pannello una cifra per impianto: i pagatori diventano due o tre.
  3. MCS risponde per iscritto che le cifre del cruscotto si possono ripubblicare con la citazione: allora si aggiunge il costo medio per regione, che è la domanda più cercata e che oggi nessuno può fare con una fonte aperta. (Sarebbe un'email a un ente, non a un cliente: da decidere con Massimiliano.)
- **Uso più economico dello stesso lavoro:** i conteggi per council sono notizie pronte per i giornali locali (la ricerca web mostra articoli tipo "South Hams in testa per le pompe di calore" e "13.000 case a Leeds con il solare"). Non lo conto nella stima: le regole vietano le email a freddo.

## 9. Indirizzi letti

gov.uk/api/content: government/collections/boiler-upgrade-scheme-statistics, government/statistics/boiler-upgrade-scheme-statistics-september-2026, government/collections/heat-pump-deployment-statistics, government/statistics/heat-pump-deployment-statistics-june-2026, government/statistics/solar-pv-cost-data, government/statistics/energy-trends-section-6-renewables, government/statistics/regional-renewable-statistics, apply-boiler-upgrade-scheme. File aperti da assets.publishing.service.gov.uk: Boiler_Upgrade_Scheme_BUS_Statistics_September_2026.xlsx, heat-pump-deployment-tables-q2-2026.xlsx, Solar_Costs_2025-26__DNC_.xlsx, ET_6.3_SOLAR_PV_OCT_26.xlsx. datadashboard.mcscertified.com (applicazione, non leggibile), mcscertified.com/low-carbon-landscapes/mcs-data-dashboard e /terms-and-conditions. ui.awin.com/merchant-profile/73922, 13574, 18758, 122556, 129571, 127461, 122838, 121796, 118669. octopus.energy/smart-home-tech/lct-referral. Concorrenti: theecoexperts.co.uk (due pagine), expertsure.com (due pagine), ukheatpumpguide.pages.dev, heatpumpcheck-uk.pages.dev, tradecost-uk.pages.dev, fuseenergy.com, solar-and-heating.ovo.com, hamuch.com. Non letti: glowgreen.co.uk, heatable.co.uk, checkatrade.com (403, non aggirati); greenmatch.co.uk e octopus.energy/heat-pumps (testo composto nel browser); Renewable electricity by local authority (scaricabile, fogli non aperti); risultati di Google e DuckDuckGo (bloccati: usata la ricerca web).
