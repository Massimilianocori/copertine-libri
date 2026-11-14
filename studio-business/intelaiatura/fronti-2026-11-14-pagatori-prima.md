# Fronte del 14/11/2026: prima il pagatore (programmi che scrivono ≥ 50 $ ad azione), poi la domanda misurata

Metodo: si parte dai programmi di affiliazione che **scrivono sulla propria pagina** un compenso di almeno 50 $ ad azione (cliente, iscrizione, vendita). Poi si misura la domanda di ricerca dove **chi cerca è chi compra**, e si guarda se un sito statico utile (calcolatore, tabelle ufficiali, pagine per Stato) può prenderne una parte. Vincoli: solo pubblicità, link di affiliazione e diritti d'autore; il programma deve accettare un editore italiano senza società.

**Esito in una riga: 15 famiglie di pagatori lette, 522 ricerche di volume. Nessuna idea arriva a 5.000 €/anno centrali come sito nuovo. I pagatori da 100-1.600 $ esistono e si leggono, ma stanno dove i primi posti sono dei pagatori stessi o di siti che vivono di quella commissione. Il guadagno vero è attaccare questi pagatori ai siti che abbiamo già (NAICS, Paycheck, Visa Income): quattro lavori da 4-30 ore che insieme valgono circa 8.300 €/anno centrali a 36 mesi (2.300 erano già contati nella riga 76 della classifica).**

## 1. Metodo e conti di base

- **Compensi.** «Letto» = cifra scritta sulla pagina ufficiale del programma o sulla pagina del programma nella rete (PartnerStack, Awin), scaricata oggi con curl. «Non letta» = cifra presa solo da elenchi di terzi: non entra nei conti.
- **Volumi.** `api.seodata.dev /v1/keyword`, 522 ricerche il 14/11/2026 (US 437, GB 56, AU 17, altri 12), 0 errori, 14 frasi a volume zero. Frasi con lo stesso numero dentro un gruppo: contate una volta. Un dato scartato perché chiaramente sbagliato: «cat insurance» 1.000.000.
- **Formula affiliazione.** ricerche/mese × quota di clic × 12 × conversione × compenso letto. Conversione centrale 0,3 % (fascia 0,15-0,5 % chiesta dal compito); per le azioni gratuite (prova, preventivo) 1-2 %, detto caso per caso.
- **Formula pubblicità.** visite × 1,3 pagine × 3,3 $ ogni 1.000 (6 $ dove il costo per clic letto è ≥ 10 $) × 0,92.
- **Cambio.** 1 $ = 0,92 €.
- **Concorrenti.** Pagine lette con curl; i 403 non sono stati aggirati e sono scritti.
- **Ammissione di un editore italiano.** Scritta dove la pagina la dice; altrimenti «non scritto, si vede alla domanda».

## 2. Tabella delle idee

| # | Idea | Pagatore (compenso letto) | Ricerche/mese misurate | CPC | 36 mesi p/c/o €/anno | Ore | €/ora (c.) | Voto | Esito |
|---|---|---|---|---|---|---|---|---|---|
| A | LLC per Stato dentro il sito NAICS (costi, rapporto annuale, agente registrato) + riquadro «stai aprendo questa attività?» | ZenBusiness 75/125/175 $, Northwest 100/150 $, Tailor Brands 50/150/250 $, Buykii 80-179 $ | ~197.000 su 10 Stati (~350.000 stimate su 50) + teste ~150.000 | 18-48 $ | 250 / 2.200 / 16.200 | 60 (riquadro da solo 4) | 37 | 5,5 | PROVA: riquadro subito + 5 Stati |
| B | Paghe lato datore nel sito Paycheck: secondo pagatore accanto a Patriot | Gusto 300 $, ADP fino a 1.000 $, Rippling 1.600 $, Patriot 150 $ | ~80.000 lato datore (riga 76) + 45.000 nuove | 15-183 $ | 300 / 3.000 / 19.000 | 6 in più | alto (poche ore) | 6 | IN CODA: domanda PartnerStack |
| C | Visti australiani in Visa Income: calcolatore dei punti + costi ufficiali, con agente registrato | Migration Expert 20 % della parcella (parcella non letta) | ~118.000 (AU) + 15.000 (GB, IN, US) | 1-6 $ | 100 / 1.900 / 11.000 | 30 | 63 | 5,5 | RISERVA alta: serve la parcella media |
| D | Corsi TEFL in Visa Income (conferma con i volumi) | International TEFL Academy ≥ 12 %; Bridge 15 %, The TEFL Academy 10 % (letti il 31/10) | ~58.000 | 2-8 $ | 250 / 1.160 / 3.700 | 16 | 72 | 6 | IN CODA (confermata) |
| E | Costo del dipendente all'estero, Paese per Paese (datore di lavoro per conto terzi, EOR) | Deel 1.500 $, Rippling 1.600 $, Remote 10-15 % per 12 mesi, Airwallex 200 $ | ~7.000 | 80-360 $ | 0 / 1.000 / 9.000 | 50 | 20 | 4 | NO come sito |
| F | Assicurazione d'impresa per mestiere e codice (NAICS → classe) | Next ~25 $ a preventivo **non letta**; Hiscox e Thimble 403 | ~120.000 | 28-75 $ | 60 / 660 / 6.000 | 25 | 26 | 5 | RISERVA: si riapre con la cifra letta in Impact |
| G | Tariffe e calcolatori per chi vende online (eBay, PayPal, Shopify, Square, Stripe) | Shopify 150 $ a negozio pagante (Impact, 175+ Paesi); Square senza cifra | ~125.000 | 2-20 $ | 70 / 640 / 5.500 | 30 | 21 | 4,5 | RISERVA bassa |
| H | Generatore di fatture e modelli per mestiere e per Paese | FreshBooks 10 $ a prova (PartnerStack) e fino a 200 $ a cliente pagante | ~480.000 | 5-21 $ | 60 / 600 / 4.800 | 35 | 17 | 4,5 | NO (lo strumento gratis è dei venditori) |
| I | Calcolatore di ore lavorate e cartellino nel sito Paycheck | Gusto 300 $, Connecteam 25 % per un anno; Homebase senza cifra | ~918.000 | 5-7 $ | 50 / 500 / 4.000 | 20 | 25 | 4,5 | RISERVA bassa (porta visite, non clienti) |
| J | VPN ed eSIM in Before You Fly: «internet in <Paese>» | NordVPN 100 % sul mensile, 40 % sugli altri piani, 30 % sui rinnovi; Surfshark 40 %; Saily 15 %; Airalo 10 % | ~20.000 | 4-24 $ | 10 / 100 / 900 | 3 | 33 | 4,5 | RIQUADRO (compenso sotto 50 $) |
| K | Traslochi internazionali in Visa Income | Sirelo 50 % del ricavo del contatto (importo non scritto, chiede fattura) | ~35.000 (GB + US) | 3-23 $ | 20 / 300 / 2.500 | 6 | 50 | 4,5 | RIQUADRO, dopo il parere sulla fattura |
| L | Software fiscale (USA, Regno Unito, espatriati, criptovalute) | Taxfix UK 25 £; MyExpatTaxes 10 % = 16-54 $; CoinLedger 25 % ricorrente; TurboTax su CJ senza cifra | > 700.000 | 0,4-15 $ | – / 200 / – | 30 | 7 | 3 | NO (sotto i 50 $, mercato dei grandi) |
| M | Conti per imprese e freelance | Airwallex 200 $ («conditions apply»); bunq 35/60 € (letto il 7/11); Mercury, Relay, Bluevine solo per commercialisti (non letto da me) | ~105.000 | 20-81 $ | – / 150 / – | 30 | 5 | 3,5 | NO |
| N | Assicurazione per animali | nessuna cifra ufficiale leggibile (Lemonade, Spot, Pumpkin 404; Embrace senza programma in pagina) | ~215.000 (US + GB) | 9-36 $ | – | – | – | 3 | NO |
| O | Mutui VA e pensione per autonomi (siti Military Pay e Limits) | nessuna cifra letta (Veterans United, Carry, Betterment) | ~390.000 | 2-55 $ | – | – | – | 3 | NO finché manca la cifra |

## 3. Le famiglie una per una

### A. Apertura di società USA: LLC per Stato dentro il sito NAICS (voto 5,5)

- **Pagatori letti.**
  - ZenBusiness: «Base payouts are $75 for the Starter package, $125 for Pro, and $175 for Premium», cookie 30 giorni, rete **Awin** (dove Massimiliano è già iscritto). `zenbusiness.com/affiliate-program/` 200.
  - Northwest Registered Agent: «$100 per signup for registered agent services, $150 per signup for business formation», programma diretto, approvazione in circa una settimana. `northwestregisteredagent.com/affiliate-program` 200.
  - Tailor Brands: Lite 50 $, Essential 150 $, Elite 250 $, 30 giorni. `tailorbrands.com/affiliate-program` 200.
  - Buykii (Awin 129099): LLC 20 % = 80-179 $, agente registrato fino a 45 $, cookie 90 giorni; serve clienti USA e non residenti. Scartato il suo servizio EIN a pagamento: il numero EIN è gratuito sul sito IRS.
  - Firstbase 40 $ (sotto soglia). Bizee su Awin senza cifra. Swyft Filings «up to 18 % per sale». doola: cifra solo dopo la domanda.
- **Ammissione.** Awin accetta l'editore italiano (conto già attivo). Northwest, Tailor Brands e Bizee: non scritto, si vede alla domanda.
- **Domanda misurata (US).** Dieci Stati (TX, FL, CA, NY, GA, OH, NC, MI, CO, AZ): «<Stato> llc» 83.300 (Texas e Florida 18.100 a 42-47 $, California 12.100 a 44 $); «how to start an llc in <Stato>» 51.100 (Texas 12.100, Florida e California 8.100; 18-33 $); «<Stato> registered agent» 36.700 (Texas e Florida 9.900; 20-32 $); «<Stato> llc cost» 14.100; «<Stato> annual report» 12.100. Totale 197.000; su 50 Stati circa 350.000 (stima, non misura). Teste: «how to start an llc» 27.100 a 22,9 $, «llc vs s corp» 33.100, «sole proprietorship vs llc» 27.100, «registered agent» 14.800 a 29,8 $, «wyoming llc» 9.900 a 48 $, «best llc service» 6.600 a 63 $, «form 2553» 22.200, «boi report» 135.000.
- **Concorrenti letti.** LLC University: Texas 3.527 parole, Michigan 3.272, Arizona 4.314, tutte con l'anno 2026 e 5-8 link ai siti statali; ha la tabella dei 50 Stati (4.349 parole) ed è a sua volta affiliato di Northwest. Northwest, pagina Texas: 1.599 parole, 5 link statali. ZenBusiness: indirizzi provati 404. Nolo 403. **Nessun vuoto**: è quota, non mancanza.
- **Il nostro vantaggio vero.** Non la pagina migliore, ma il visitatore: chi cerca «naics code for <attività>» sta compilando proprio il modulo di apertura della società o della licenza. Il sito NAICS ha già 1.490 pagine. Un riquadro lì costa 4 ore.
- **Conto centrale a 36 mesi.** Sezione: 350.000 × 0,15 % = 525 visite/mese = 6.300 l'anno × 0,3 % = 19 società × 125 $ = 2.360 $ → ~2.170 € + 45 € di pubblicità = **~2.200**. Prudente (quota 0,04 %, conversione 0,15 %): ~250. Ottimista (0,6 % e 0,5 %, 140 $): ~16.200.
- **Solo il riquadro (4 ore).** Se il sito NAICS arriva a 3.000 visite al mese e una su dieci sta aprendo un'attività: 3.600 l'anno × 0,3 % × 125 $ = ~1.240 €. È una stima sopra una stima (le visite del sito NAICS non ci sono ancora).
- **Prova proposta.** Riquadro in tutte le pagine NAICS + 5 Stati (Texas, Florida, California, New York, Georgia) con costi letti sul sito dello Stato, 15 ore in tutto. Si passa a 50 solo se in 60 giorni arrivano impressioni. È lo stesso blocco proposto il 31/10 («US Small Business by State», allora 10.000 centrali senza volumi): con i volumi veri e la quota dello 0,15 % scende a 2.200.

### B. Paghe e personale: secondo pagatore nel sito Paycheck (voto 6)

- **Pagatori letti (pagina del programma su PartnerStack, tutte 200).** Gusto «Earn $300 for every new customer (who runs payroll)»; ADP «up to $1,000+ for every new U.S. based RUN customer who actively runs payroll»; Rippling «$600 for a qualified demo, $1,000 when they sign» e «$1600 for every new paying customer»; Connecteam 25 % per il primo anno; Patriot 150 $ (già nel sito, riquadro spento). OnPay, SurePayroll, Homebase: 404 o 403.
- **Ammissione.** PartnerStack paga in dollari anche fuori dagli USA (lo dice FreshBooks per il proprio programma sulla stessa rete). I termini di Gusto sono dietro un blocco (403, non aggirato): Paesi ammessi non letti.
- **Domanda nuova misurata.** «payroll software for small business» 9.900 a 109 $; «payroll for small business» 3.600 a 183 $; «gusto pricing» 12.100 a 25 $; «adp pricing» 5.400 a 35,7 $; «payroll tax calculator» 18.100 a 14,8 $; «employer payroll tax calculator» 1.900; «employee cost calculator» e simili 3.900 a 6-20 $; «new hire paperwork» 1.900 a 31,5 $; «how to hire an employee» 1.000 a 39,7 $; «s corp payroll» 320 a 137 $. Le frasi sulle aliquote («suta tax rate» 390, «new employer suta rate» 0) sono piccole.
- **Conto.** Stesso traffico della riga 76 (800 visite/mese dal lato datore). Con Patriot: 14 clienti × 150 $ → ~2.000 €. Se entra anche Gusto e metà dei clienti sceglie Gusto: 14 × 225 $ → ~2.900 € + 275 di pubblicità = **~3.000** (era 2.300). Ore in più: 6 (secondo riquadro e pagina «Gusto, ADP o Patriot: prezzi ufficiali a confronto», solo listini letti).
- **Rischio.** La conversione dello 0,15 % resta una stima. I primi posti sono dei venditori.

### C. Immigrazione: visti australiani in Visa Income (voto 5,5)

- **Pagatori.** Migration Expert (agenti registrati MARA): «20% commission on the sale value (excluding any government fees)», pagina 200; la parcella non è in pagina (indirizzo dei prezzi 404). iVisa: «up to 20 % commission on our service fees», cookie 365 giorni (visti turistici, parcelle piccole). Boundless: nessuna pagina del programma trovata (404). US Green Card Office (Awin 52741, 30 %): **scartato**, vende l'iscrizione a una lotteria che sul sito del governo è gratuita.
- **Domanda misurata.** Australia: «482 visa» 33.100, «partner visa australia» 14.800 a 5,9 $, «491 visa» 14.800, «189 visa» 12.100, «190 visa» 9.900, «student visa australia» 9.900, «pr points calculator» 12.100, «australia pr points calculator» 5.400 (AU) e 5.400 (India), «migration agent» 5.400 a 8,8 $. Stati Uniti (senza pagatore): «i-130 processing time» 22.200, «n-400 fee» 14.800, «i-485 fee» 12.100, «uscis fee calculator» 8.100.
- **Che cosa costruiremmo.** In Visa Income: calcolatore dei punti con la tabella ufficiale e una pagina per sottoclasse con costo ufficiale e soglie. Solo dati ufficiali; il consiglio sul caso lo dà l'agente registrato (noi no: zona delicata).
- **Conto centrale.** 118.000 × 0,3 % = 350 visite/mese = 4.200 l'anno × 0,15 % = 6 clienti × 325 $ (20 % di una parcella **supposta** di 2.500 dollari australiani) → **~1.900 €**. Senza la parcella vera il conto vale poco.
- **Concorrenti.** Il Ministero australiano ha il suo calcolatore dei punti; decine di studi di agenti hanno pagine per sottoclasse. Vuoto non dimostrato.

### D. Formazione ad alto prezzo: corsi TEFL in Visa Income (voto 6, confermato)

- **Pagatori letti.** International TEFL Academy: «You will receive at least 12% commission for all purchases», pagata entro 7 giorni lavorativi; prezzo dei corsi non letto (404). Coursera 15-45 % (corsi da decine di dollari: sotto soglia). edX 10 %, niente master. Udacity, Codecademy, Magoosh, Becker, UWorld: nessuna cifra o 404.
- **Domanda misurata.** «tefl certification» 18.100 a 5,7 $, «teach english abroad» 8.100, «teach english online» 8.100, «online tefl certification» 5.400 a 7,7 $, «teach english in japan» 5.400, Spagna 3.600, Cina 1.900, Corea 1.600, Thailandia 1.300, Vietnam 720; GB «tefl course» 4.400. Totale ~58.000.
- **Conto centrale.** 58.000 × 0,3 % = 175 visite/mese = 2.100 l'anno × 0,4 % = 8 corsi × 150 $ (12 % di un corso supposto a 1.250 $) → **~1.160 €**. Uguale alla stima del 31/10 fatta senza volumi (1.150): la sezione resta in coda.
- **Altri esami misurati, senza pagatore letto.** «sie exam» 27.100, «google data analytics certificate» 22.200 a 11 $, «pmp certification cost» 14.800, «series 7 exam» 8.100, «cpa exam pass rate» 4.400 a 13 $, «best cpa review course» 590 a 24 $.

### E. Assunzioni all'estero (EOR) e paghe globali (voto 4, NO come sito)

- **Pagatori letti.** Deel «Earn $1500 for every new paying customer» (PartnerStack); Rippling 1.600 $; Remote «10% to 15% commission» sul ricavo per 12 mesi, cookie 90 giorni, rete Impact; Airwallex «$200 referral commissions for new Airwallex customer, conditions apply».
- **Domanda misurata.** Piccola e carissima: «employer of record» 2.400 a 192 $ (GB 1.300 a 147 £), «global payroll» 1.600 a 80 $, Germania 140 a 358 $, Regno Unito 170 a 327 $, Canada 320 a 184 $, «payroll in mexico» 170 a 308 $. Molte frasi a zero («hire in germany», «employer contributions germany», «notice period by country»). Totale ~7.000.
- **Perché no.** Chi cerca è il compratore, ma è un mercato da un cliente l'anno: 7.000 × 0,5 % = 35 visite/mese × 12 × 0,2 % = 0,8 clienti × 1.500 $ → ~1.000 € centrali, con zero nel caso prudente. Deel, Remote, Oyster e Papaya hanno già le guide Paese per Paese: sono i pagatori stessi.

### F. Assicurazione d'impresa per mestiere (voto 5, riserva)

- **Pagatori.** Nessuna cifra ufficiale leggibile: Next Insurance 404 sulla pagina provata (elenchi di terzi: 20-25 $ a preventivo, rete Impact, **non letta**); Hiscox e Thimble 403; Simply Business senza cifra.
- **Domanda misurata.** «small business insurance» 49.500 a 75 $, «business insurance for llc» 9.900 a 61 $, «llc insurance» 6.600 a 54 $, «business insurance cost» 8.100 a 28 $, «how much is business insurance» 6.600, «food truck insurance» 3.600 a 55 $, «handyman insurance» 2.900 a 70,5 $, «cleaning business insurance» 2.900 a 50 $, «workers compensation class codes» 4.400 a 13 $, «ncci class codes» 320 a 68 $. GB: «public liability insurance» 49.500 a 45,6 £.
- **Che cosa costruiremmo.** Nel sito NAICS: per ogni codice, la classe assicurativa collegata e il link al preventivo. I costi per clic sono i più alti dopo le paghe.
- **Conto (solo se la cifra di 25 $ viene letta).** 120.000 × 0,1 % = 120 visite/mese × 12 × 2 % di preventivi × 25 $ → ~660 €. Si riapre quando Massimiliano vede la cifra dentro Impact.

### G. Commercio online: tariffe e calcolatori per venditori (voto 4,5)

- **Pagatori letti.** Shopify: «$150 USD per qualified referral» (piano a pagamento; importo variabile per Paese del negozio), rete Impact, «175+ countries». Square: programma su Impact, «We accept affiliates from anywhere in the world», nessuna cifra. Lightspeed, Toast, Helcim: 404 o senza programma.
- **Domanda misurata.** «ebay fee calculator» 33.100 a 14 $, «paypal fee calculator» 22.200 a 12 $, «shopify fees» e «shopify pricing» 22.200, «square fees» 12.100, «ebay fees» 12.100, «credit card processing fees» 8.100 a 20 $, «amazon fba calculator» 5.400, «stripe fee calculator» 2.400, «etsy fee calculator» 1.900; «sellers permit» 12.100, «california sellers permit» 12.100, «resale certificate» 9.900.
- **Perché resta bassa.** Chi calcola la tariffa di eBay non sta comprando Shopify: conversione 0,15 %. 125.000 × 0,2 % → 3.000 visite l'anno × 0,15 % × 150 $ → ~640 € con la pubblicità.

### H. Contabilità e fatture (voto 4,5, NO)

- **Pagatori letti.** FreshBooks: «$10.00 for each FreshBooks trial generated» (PartnerStack) e «up to $200 per paid subscriber»; accetta editori di molti Paesi («subject to… regional restrictions»), paga in dollari; chiede contenuti originali. BILL 250 $, TaxDome 100 $, Ramp 300 $ (prodotti per aziende più grandi). Xero 404. QuickBooks: solo sconto per il cliente.
- **Domanda misurata.** «invoice template» 201.000 a 7,3 $, «invoice generator» 49.500 a 17,2 $, «free invoice generator» 27.100, «invoice maker» 14.800 a 18 $; GB 49.500 e 18.100; AU 27.100; CA 18.100; DE «rechnung schreiben» 12.100 a 21 €, «rechnung vorlage» 9.900; FR 8.100 + 8.100. Per mestiere: contractor 3.600, freelance 2.400, construction 2.400, consulting 1.900, photography 1.300. Anche «accounting software for small business» 27.100 a 58 $.
- **Concorrenti letti.** invoice-generator.com (strumento, 845 parole), FreshBooks stesso con i modelli gratuiti (1.740 parole), Invoice Simple 403. Lo strumento gratuito è l'esca dei venditori: Canva, Microsoft, Zoho, Wave.
- **Conto.** 480.000 × 0,05 % = 240 visite/mese: 29 prove × 10 $ + 4 clienti × 100 $ → ~600 €.

### I. Ore lavorate e cartellino (voto 4,5)

- **Domanda misurata.** «hours calculator» 368.000, «time card calculator» 201.000, «work hours calculator» 165.000, «time clock calculator» 135.000, «timesheet calculator» 49.500 (5-7 $); «overtime calculator» 22.200; «employee scheduling software» 14.800 a 70,7 $.
- **Perché bassa.** Chi cerca è quasi sempre il dipendente, non il datore: non è il compratore. Calculator.net ha già lo strumento (1.503 parole). Vale come porta d'ingresso al sito Paycheck: ~500 € centrali, quasi tutti di pubblicità.

### J. VPN ed eSIM per Before You Fly (voto 4,5, riquadro)

- **Pagatori letti.** NordVPN: 100 % sul piano mensile, 40 % sugli altri, 30 % sui rinnovi, cookie 30 giorni. Surfshark: 40 %, soglia di pagamento 100 $, Awin o Impact. Proton: fino al 100 %. Saily 15 %. Airalo 10 % (Impact). ExpressVPN senza cifra chiara. Per vendita restano **sotto i 50 $** (prezzi dei piani non letti oggi; stima 25-45 $).
- **Domanda misurata.** «best vpn for china» 3.600 a 11,3 $, «vpn for china» 2.400, «nordvpn china» 1.600, «great firewall» 2.900, «does whatsapp work in china» 1.000, «vpn for turkey» 1.000, «vpn for travel» + «best vpn for travel» 1.440 a 20-24 $, «vpn for uae» 390; «best esim for europe» 4.400, «esim for japan» 2.900. La testa «best vpn» (90.500) è dei siti di recensioni.
- **Conto.** 20.000 × 1 % = 200 visite/mese × 12 × 0,5 % × 35 $ → ~40 €; con il 2 % sulle pagine Cina ~100-170 €. Un riquadro da 3 ore nelle pagine di Cina, Emirati, Turchia, Russia, Iran; niente di più.

### K. Traslochi internazionali (voto 4,5, riquadro)

- **Pagatore letto.** Sirelo: «Earn 50 percent of the revenue from every valid moving lead», importo per contatto variabile e non scritto, 700 traslocatori in 60 Paesi, accetta siti di espatriati e immigrazione. **Chiede una fattura mensile** per la quota: da far vedere al commercialista prima di iscriversi. Allied 12 $ a preventivo: non letta. PODS, U-Haul, moveBuddha, International Van Lines: 404.
- **Domanda misurata.** GB: «moving to australia from uk» 5.400, «moving to spain from uk» 3.600, «removal costs» 1.600, «international removals» 1.000 a 15 £, «removals to spain» 590, «removals to france» 390 a 23 £. US: «moving to canada from us» 18.100, «international moving companies» 8.100 a 20,7 $, «moving cost calculator» 6.600 a 14,75 $, «car shipping cost» 12.100.
- **Conto.** Con 8 $ supposti a contatto e il 3 % dei lettori che chiede un preventivo: ~300 € centrali. Riquadro nelle pagine Paese di Visa Income.

### L. Software fiscale (voto 3, NO)

- **Pagatori.** Taxfix UK (ex TaxScouts): «£25 for every new customer», rete Partnerize, **solo promozione nel Regno Unito**. MyExpatTaxes: 10 %, «anywhere from $16 to $54». CoinLedger: 25 % ricorrente (letto sul suo blog). Koinly 403. TurboTax: programma su CJ, cifra non pubblica (terzi: 5-15 %). H&R Block, TaxSlayer, FreeTaxUSA 403. Quasi tutto sotto i 50 $.
- **Domanda misurata.** «tax calculator» 201.000 a 2,35 $, «free tax filing» 201.000 a 7,75 $, «capital gains tax calculator» 27.100, «foreign earned income exclusion» 14.800, «fbar filing» 9.900, «crypto tax» 6.600, «crypto tax calculator» 5.400, «expat tax» 4.400 a 15 $; GB «uk tax calculator» 74.000, «self employed tax calculator» 22.200, «making tax digital» 74.000.
- **Perché no.** Compensi bassi, primi posti dei venditori e dei grandi, e il calcolo delle imposte del singolo è zona delicata.

### M. Conti per imprese e freelance (voto 3,5, NO)

- **Pagatori.** Airwallex 200 $ (PartnerStack, «conditions apply»). bunq 35/60 € (letto il 7/11, solo IP di cinque Paesi). Mercury, Relay, Bluevine: programmi per commercialisti o aziende USA (da ricerca, pagine 403/404: non letto). Payoneer, Novo, Found, Lili: 404 o senza cifra.
- **Domanda misurata.** «business bank account» 40.500 a 57 $, «open business bank account online» 18.100 a 81 $, «business bank account for llc» 12.100, «best bank for small business» 12.100; GB «business bank account» 14.800 a 52 £; «us bank account for non residents» 590.
- **Perché no.** È il mercato dei comparatori (NerdWallet, Forbes); l'unico pagatore letto e aperto a noi è Airwallex. Vale un link nelle future pagine LLC (famiglia A), non un sito.

### N. Assicurazione per animali (voto 3, NO)

- Nessuna cifra ufficiale: Lemonade, Spot, Pumpkin 404; la pagina di Embrace non ha il programma. Da terzi (non lette): Lemonade 15 $ a contatto, Fetch 25 $.
- Domanda: «best pet insurance» 74.000 a 28,5 $, «pet insurance cost» 18.100, «is pet insurance worth it» 12.100, «dog dental cleaning cost» 12.100, «dog acl surgery cost» 4.400; GB «pet insurance» 90.500 a 16,7 £. Primi posti dei comparatori.

### O. Mutui VA e pensione per autonomi (voto 3, NO per ora)

- Domanda grande nei nostri siti: «va loan calculator» 135.000 a 14,8 $, «va loan rates» 27.100, «va loan requirements» 18.100 a 17,9 $, «military car insurance» 27.100 a 55 $; «solo 401k» 14.800 a 9,5 $, «best solo 401k» 3.600 a 16 $, «backdoor roth» 27.100, «401k rollover» 9.900 a 11 $, «gold ira» 9.900 a 37 $.
- Nessun compenso letto: Veterans United non ha il programma in pagina, Carry 404, Betterment ha solo l'invito tra amici. I contatti per i mutui passano da reti americane con regole proprie. Oro per la pensione: scartato (settore di vendite aggressive). Si riapre solo con una cifra scritta.

## 4. I primi cinque

| Posto | Idea | Compenso letto | Domanda misurata | Centrale 36 mesi | Ore | Che cosa serve |
|---|---|---|---|---|---|---|
| 1 | Secondo pagatore nel sito Paycheck (B) | Gusto 300 $, ADP fino a 1.000 $, Patriot 150 $ | ~125.000 lato datore | ~3.000 €/anno (era 2.300) | 6 | Iscrizione a PartnerStack (Gusto, ADP) e a Impact (Patriot) |
| 2 | Riquadro + LLC per Stato nel sito NAICS (A) | ZenBusiness 75-175 $, Northwest 100-150 $, Tailor Brands 50-250 $ | ~350.000 + teste | ~2.200 €/anno (riquadro da solo ~1.240) | 4 + 15 di prova | Domanda a ZenBusiness su Awin; domanda diretta a Northwest |
| 3 | Visti australiani in Visa Income (C) | Migration Expert 20 % | ~133.000 | ~1.900 €/anno (parcella supposta) | 30 | Chiedere la parcella media alla domanda |
| 4 | Corsi TEFL in Visa Income (D) | ITA ≥ 12 %, Bridge 15 % | ~58.000 | ~1.160 €/anno | 16 | Domanda a ITA e Bridge |
| 5 | Assicurazione d'impresa per codice nel sito NAICS (F) | Next ~25 $ non letta | ~120.000 a 28-75 $ | ~660 €/anno (se la cifra è vera) | 25 | Leggere la cifra dentro Impact |

Somma dei primi quattro: circa 8.300 €/anno centrali a 36 mesi con ~70 ore, tutti dentro siti che esistono (2.300 sono già nella riga 76: il guadagno nuovo è circa 6.000). Nessuno, da solo, giustifica un sito nuovo.

## 5. Che cosa ho imparato

1. **I compensi alti ci sono e si leggono**: 75-250 $ per una LLC, 150-1.000 $ per un cliente delle paghe, 1.500 $ per un cliente EOR, 150 $ per un negozio Shopify, 200 $ per un cliente FreshBooks o Airwallex.
2. **Dove il compenso è alto e la domanda è grande, la prima pagina è del pagatore o di chi vive di quel compenso** (LLC University, NerdWallet, Deel, FreshBooks con il suo strumento gratuito). Le pagine lette sono lunghe, aggiornate al 2026 e con le fonti statali: nessun vuoto da riempire.
3. **Dove il compenso è altissimo, la domanda è minuscola** (EOR: 7.000 ricerche al mese): un cliente l'anno, quindi un conto che può dare zero.
4. **Tanta domanda, ma chi cerca non compra**: ore lavorate (918.000), modelli di fattura (480.000), calcolatori fiscali. Lì resta la pubblicità.
5. **Sotto i 50 $**: VPN, eSIM, software fiscale, corsi economici. Buoni solo come riquadro.
6. **La leva che resta è il visitatore giusto che abbiamo già**: chi cerca un codice NAICS sta aprendo un'attività; chi usa il calcolatore del datore deve pagare un dipendente; chi legge Visa Income sta emigrando.

## 6. Che cosa deve fare Massimiliano (in ordine, ~40 minuti in tutto)

1. **PartnerStack**: creare il conto editore e chiedere Gusto e ADP (e FreshBooks, se si farà la pagina delle fatture). Guardare nei termini di Gusto se accetta editori fuori dagli USA: da qui non si leggono.
2. **Awin**: chiedere ZenBusiness (e Buykii 129099 per i non residenti).
3. **Northwest Registered Agent**: domanda diretta dal sito (risposta in circa una settimana).
4. **Impact**: Patriot (già previsto), poi dentro Impact leggere la cifra di Next Insurance e di Square.
5. **Sirelo**: solo dopo aver chiesto al commercialista se la fattura mensile a Sirelo è compatibile con il regime (è una provvigione, non una vendita).
6. Niente spese. Niente da firmare prima delle prime visite: le domande si fanno quando la pagina è online, perché i programmi guardano il sito.

## 7. Limiti

- Le conversioni (0,15-0,5 %) e le quote di clic sono stime, non dati nostri: nessuno dei nostri siti ha ancora una vendita di questo tipo.
- I 50 Stati della famiglia A sono misurati solo su 10: il totale di 350.000 è una stima.
- La parcella di Migration Expert e il prezzo dei corsi ITA non sono stati letti: i conti C e D poggiano su un prezzo supposto.
- Ammissione dell'editore italiano: scritta solo per Shopify (175+ Paesi), Square («anywhere in the world»), FreshBooks (molti Paesi, con restrizioni) e Awin (conto già attivo). Per Gusto, ADP, Northwest, Tailor Brands, Migration Expert, ITA si saprà alla domanda.
- Pagine non lette per blocco (non aggirato): Gusto (termini), Homebase, Hiscox, Thimble, Bluevine, Revolut Business, Koinly, CoinTracker, H&R Block, TaxSlayer, FreeTaxUSA, Expatfile, Preply, DataCamp, Nolo, Invoice Simple, Mercury (assistenza).
- I concorrenti sono stati letti a fondo solo per la famiglia A (6 pagine) e a campione per H e I; per le altre vale il giudizio sui primi posti noti, non una lettura di 5 esempi. Per questo nessun voto supera 6.
- I volumi sono medie mensili: le frasi con l'anno e le novità del 2026 mancano.

## 8. Fonti (lette il 14/11/2026)

- Formazione di società: `zenbusiness.com/affiliate-program/`, `northwestregisteredagent.com/affiliate-program`, `tailorbrands.com/affiliate-program`, `ui.awin.com/merchant-profile/129099`, `firstbase.io/affiliates`, `bizee.com/affiliates`, `swyftfilings.com/affiliates/`, `doola.com/affiliates/` e `market.partnerstack.com/page/doola`.
- Paghe e personale: `market.partnerstack.com/page/gusto`, `/adp`, `/rippling`, `/deel`, `/connecteam`; `remote.com/partners/affiliates`; `deel.com/partners/affiliates/` (senza cifra).
- Contabilità e pagamenti: `freshbooks.com/affiliate-program`, `market.partnerstack.com/page/freshbooks`, `/bill`, `/taxdome`, `/ramp`, `/airwallex`, `/quickbooks`; `shopify.com/affiliates`; `squareup.com/us/en/affiliate`.
- VPN ed eSIM: `nordvpn.com/affiliate/`, `surfshark.com/affiliate`, `proton.me/partners/affiliates`, `expressvpn.com/affiliates`, `saily.com/affiliate/`, `airalo.com/partner-with-us/affiliate-partners`.
- Formazione: `internationalteflacademy.com/affiliate-program`, `coursera.org/about/affiliates`, `edx.org/affiliate-program`.
- Fisco: `taxscouts.com/affiliates/`, `myexpattaxes.com/affiliate-program/`, `coinledger.io/blog/crypto-affiliate-programs`, `turbotax.intuit.com/affiliate`.
- Immigrazione e traslochi: `migrationexpert.com.au/affiliates/`, `ivisa.com/affiliates`, `ui.awin.com/merchant-profile/52741`, `ui.awin.com/merchant-profile/131119`, `sirelo.co.uk/for-affiliates/`.
- Concorrenti: `llcuniversity.com` (Texas, Michigan, Arizona, Georgia, tabella dei 50 Stati), `northwestregisteredagent.com/llc/texas/cost`, `invoice-generator.com`, `freshbooks.com/invoice-templates`, `calculator.net/time-card-calculator.html`.
- Cifre di terzi, **non lette** sulle pagine ufficiali: Next Insurance 20-25 $ a preventivo, Lemonade 15 $, Fetch 25 $, Allied 12 $ a preventivo, TurboTax 5-15 %, Koinly 20 %, Mercury, Relay e Bluevine per commercialisti.
- Volumi: `api.seodata.dev /v1/keyword`, 522 ricerche.
