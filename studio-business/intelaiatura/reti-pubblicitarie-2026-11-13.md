# Reti pubblicitarie oltre AdSense: quale, su quale sito, da quando (13/11/2026)

**Domanda.** Con ~7.200 visite al mese (GoatCounter 6-13/11) si può guadagnare per visita molto più che con AdSense? Quali reti display ci accettano, a che soglia, con quali vincoli (forfettario, ATECO 58.19.00, niente Camera di Commercio), e quanti euro in più a 12 mesi?

**Risposta in breve.**
1. **Oggi nessuna rete migliore di AdSense ci accetta.** Le soglie ufficiali sono cambiate nel 2025-2026: Ezoic ora chiede **250.000 utenti al mese** (prima nessuna soglia), Raptive **25.000 pagine viste** con il 50 % del traffico da USA/UK/CA/AU/NZ, Pubfuture 100.000 pagine viste, Playwire 100.000-500.000, Freestar ~1 milione, Publisher Collective (Snigel) 3 milioni o ~300 €/giorno. Monumetric Propel accetta solo siti WordPress o Blogger e chiede 99 $.
2. **L'unica porta vicina è Journey by Mediavine**: **1.000 sessioni da USA, Canada, UK e Australia in 30 giorni, per sito**, misurate con lo script Grow, che deve girare per almeno 30 giorni. Oggi Visa Income fa **~975 sessioni Tier 1 al mese** (51 % del suo traffico) e Before You Fly **~690** (48 %). Il primo è già alla soglia; il secondo la passa con un altro +45 %. EsameB1 (5 % Tier 1) non la passerà mai: per i siti italiani resta AdSense.
3. **Adsterra e Monetag (ex PropellerAds) no.** Le norme AdSense vietano gli annunci Google sui siti che *"contain or trigger pop-unders"*, e il pop-under è il loro formato principale. Metterli vuol dire perdere AdSense su tutta la rete, e Mediavine chiede di essere *"in good standing with Google AdSense"*.
4. **Euro in più a 12 mesi rispetto al solo AdSense: +40 / +325 / +2.340 €** (prudente / centrale / ottimista). Al mese 12 il ritmo annuo vale **+70 / +590 / +5.550 €/anno**. Quasi tutto viene da Journey su Visa Income e Before You Fly. Il resto viene da Auto ads ben regolati e, solo nello scenario ottimista, da Raptive su Before You Fly. **La pubblicità resta piccola rispetto alle affiliazioni e al libro** (`monetizzazione-traffico-2026-11-13.md`). La leva vera è il traffico Tier 1, non la rete.
5. **Azione di oggi (Massimiliano, 10 minuti):** account Grow gratuito, con dentro visaincomechecker.com e before-you-fly.com. Da lì partono i 30 giorni. Claude mette lo script nei due siti alla prossima pubblicazione.

**Metodo.** Solo pagine ufficiali delle reti, lette il 13/11/2026 (WebFetch/curl; nessun aggiramento di blocchi: dove la pagina dava 403 è scritto). Il dato RPM ufficiale viene dal calcolatore di AdSense (`adsense.google.com/start/calculator-data.json`, file del 9/12/2024; formula nel codice della pagina: guadagno annuo = pagine viste/1.000 × moltiplicatore × 12, quindi il moltiplicatore è $ per 1.000 pagine viste). Le cifre di terzi sono segnate **(terzi)**. Traffico: GoatCounter `stats/hits` (675 percorsi, 1.682 visite in ~8 giorni) e `stats/locations` filtrato per sito con `include_paths`.

## 1. Il nostro traffico per sito e per Paese (6-13/11/2026)

| Sito | Visite (~8 gg) | Al mese (stima) | Tier 1 (US, UK, CA, AU) | Asia del Sud (IN, PK, BD) | Primi Paesi |
|---|---|---|---|---|---|
| EsameB1 (.eu + netlify) | 666 | ~2.800 | **5 %** | 0 % | IT 553, US 22, DE 8, BE 8 |
| Visa Income (.com + netlify) | 510 | ~2.200 | **51 %** (~975/mese) | 9 % | AU 122, US 72, GB 57, IN 15, BD 14, PK 14 |
| Before You Fly (.com + netlify) | 385 | ~1.650 | **48 %** (~690/mese) | 4 % | US 114, GB 38, DE 21, CA 20 |
| Tutti gli altri (12 siti) | ~120 | ~550 | – | – | 9 siti US/UK nuovi del 13/11 ancora a 0 |

Rete intera: Italia 38 %, USA 17 %, Australia 9 %, UK 7 %, Canada 2,5 %. Provenienza: Google 687, diretto 338, ChatGPT 305. Nota: GoatCounter conta visite, Grow conta sessioni. Le cifre sono vicine ma non identiche, e per Journey conta solo Grow.

## 2. Le reti a confronto (fonti ufficiali)

| Rete | Soglia minima | Paesi / lingua / qualità | .netlify.app | Quota all'editore | Pagamento | Vincolo / affiliati / velocità | Per noi |
|---|---|---|---|---|---|---|---|
| **AdSense** | nessuna | tutte le lingue supportate; norme sui contenuti ("Low value content" già visto su EsameB1) | **Sì**: AdSense accetta i *"Subdomains on platforms that are already part of the public suffix list"* [A2], e `netlify.app` è nella Public Suffix List (riga 15019, letta oggi) | **80 %** dopo la quota della piattaforma dell'inserzionista (~68 % sugli annunci comprati via Google Ads) [A1] | saldo definitivo il 3, pagamento tra il 21 e il 26 del mese se il saldo al 20 supera la soglia [A3] (in Italia 70 €, da cruscotto) | nessun vincolo; affiliati ammessi; **vietati i pop-under** e più di 3 pop-up [A4] | **Base di tutti i siti.** Da regolare (sez. 3) |
| **Journey by Mediavine** | **1.000 sessioni Tier 1 (US, CA, UK, AU) in 30 giorni** [M1]; Grow installato da almeno 30 giorni, *"Running Grow is a requirement for Journey ads"* [M2] | contenuti originali; traffico pulito; *"in good standing with Google AdSense"* [M1]; Mediavine lavora con editori internazionali e *"Having an English-language site isn't a requirement"* [M4]. Asia del Sud ammessa se il traffico premium *"offset[s] any non-premium traffic"* [M5] | non dichiarato su nessuna pagina letta (meglio un dominio proprio; i 3 siti principali ce l'hanno già) | **70 %**, Net 65 (blog di Journey, journeymv.com [M6]; non nella tabella ufficiale 2026, che parte da Mediavine 75 % [M3]); passa a Mediavine pieno a 5.000 $ di ricavi annui | Net 65 dalla fine del mese; minimo 100 $; per l'estero PayPal, ACH internazionale, bonifico via Tipalti, cambio ~2 % [M4][M7] | sostituisce AdSense sul sito; affiliati ammessi (Mediavine chiede solo che i riquadri seguano le stesse regole di posizione [M8]); script per siti non WordPress esiste [M9]; *"doesn't destroy pagespeed"* (loro marketing). Contratto e preavviso: non letti | **Sì per Visa Income e Before You Fly** alla soglia |
| **Mediavine (pieno)** | 5.000 $ di ricavi pubblicitari annui [M1] | come sopra | non dichiarato | 75 % sotto 100.000 $/anno [M3] | Net 65 | esclusiva display | Arriva da Journey in automatico; per noi non entro 12 mesi (servono ~50.000 pagine viste al mese su un sito) |
| **Raptive** | **25.000 pagine viste al mese** (dal 16/10/2025) [R1]; tra 25.000 e 99.999 almeno **50 %** da US, UK, CA, AU, NZ (pagina d'aiuto, testo letto solo tramite motore di ricerca: il sito dà 403) [R2] | Google Analytics obbligatorio (lettura); una domanda per sito [R2] | non dichiarato | non pubblicata | non letta (403) | *"15% minimum RPM lift guarantee"* sul fornitore precedente (condizioni in pagina non leggibile) [R3] | Before You Fly e Visa Income a 25.000 pagine viste se il Tier 1 resta ≥ 50 % (oggi 48 % e 51 %: sul filo) |
| **Ezoic** | **250.000 utenti al mese** per i siti nuovi dal 19/2/2026; sotto, "Incubator" con 20 siti scelti al mese [E1][E2] | lingue supportate da AdSense; norme AdSense | non dichiarato | non pubblicata | – | – | **No** (100 volte la nostra soglia) |
| **Monumetric** | Propel 10.000-80.000 pagine viste per 3 mesi; Ascend da 80.000 [Mo1] | **solo siti WordPress o Blogger**, almeno 50 % US/UK/AU/CA, **99 $** di attivazione [Mo1] | – | commissione non scritta [Mo2] | in dollari | mese per mese, disdetta con 30 giorni di preavviso [Mo2] | **No** (siti statici, quota d'ingresso) |
| **Freestar** | *"typically requires a minimum of 1,000,000 pageviews monthly"* (FAQ Freestar, testo visto tramite motore di ricerca) [F1] | – | – | non pubblicata | – | – | No |
| **Snigel / Publisher Collective** | **3 milioni** di pagine viste al mese, oppure siti che fanno ~**300 €/giorno** [S1] | contratto firmato | – | non pubblicata | – | – | No |
| **Playwire** | "consigliato" da **100.000** pagine viste, con ≥ 20 % USA [P1]; la loro FAQ dice 500.000 (copia indicizzata) | – | – | non pubblicata | – | – | No |
| **Setupad** (Lituania/Lettonia, Prebid gestito) | non scritta sul sito; **100.000 visitatori al mese** (terzi) | – | – | 20 % di commissione, o 0,05 € CPM fisso [St1] | **Net 60** dalla fine del primo mese, minimo **100 €**; bonifico, PayPal, Payoneer, Wise, Revolut [St2] | lavora *"alongside Google AdX, AdSense"* [St2] | No fino a 100.000 visite su un sito |
| **Pubfuture** | **100.000 pagine viste al mese** (FAQ nel codice del sito) [Pf1] | contenuti senza nudità | – | non pubblicata | **Net-30** [Pf1] | formati interstitial e sticky | No fino a 100.000 |
| **Adsterra** | nessuna [Ad1] | qualsiasi | sì | non pubblicata | da 5 $ (Paxum), PayPal, bonifico [Ad1] | **pop-under**, Social Bar, Smartlink | **No: rischio alto** (sez. 4) |
| **Monetag (ex PropellerAds)** | nessuna [Mt1] | qualsiasi | sì | non pubblicata | da 5 $, ogni 1-2 settimane [Mt1] | pop-under, push, vignette; si dichiara *"compatible with AdSense"*, ma AdSense vieta i pop-under | **No: rischio alto** |
| **Ad Manager + header bidding in proprio** | serve un account AdSense valido; pensato *"for large publishers who have significant direct sales"* [G1]; gratis fino a 90 milioni di impressioni al mese (USA/CA/AU/NZ; altrove soglie diverse) [G2] | ogni SSP (Magnite, PubMatic…) ha la sua approvazione e le sue soglie; AdX diretto non è aperto ai piccoli (serve un partner) | – | – | – | lavoro tecnico (Prebid.js, consenso TCF per ogni SSP), più script lenti | **No** sotto 100.000 pagine viste: il guadagno non paga le ore |

**Regime fiscale.** Per tutte le reti accettabili (Mediavine/Journey, Raptive, Setupad, Pubfuture) vale lo schema già in uso per AdSense: società estera che paga per lo spazio pubblicitario, fattura con art. 7-ter, codice 58.19.00, Gestione Separata e **nessuna Camera di Commercio**. Mediavine paga tramite Tipalti e chiede il modulo fiscale (il W-8BEN c'è già per AdSense: va rifatto nel loro portale). Adsterra e Monetag pagano su Paxum, Skrill o criptovalute e rendono più difficile la contabilità: un motivo in più per escluderle.

## 3. RPM documentati

**Ufficiale, calcolatore AdSense** ($ guadagnati dall'editore ogni 1.000 pagine viste; dati del 9/12/2024; solo per grandi regioni, non per singolo Paese):

| Categoria | Americhe | Europa, Medio Oriente, Africa (qui c'è l'Italia) | Asia-Pacifico (qui ci sono Australia, India, Pakistan) | Nostri siti |
|---|---|---|---|---|
| Travel & Transportation | 2,95 | 3,25 | 2,08 | Before You Fly, Tourist Tax, Cruise, Italy Strikes |
| Law & Government | 3,05 | 2,59 | 4,39 | Visa Income, Statute Limits |
| Jobs & Education | 3,16 | 1,86 | 1,69 | EsameB1, EsamiDiStato, Quiz |
| Reference | 2,40 | 1,97 | 1,73 | Codici ATECO, NAICS |
| Finance | 3,34 | 4,29 | 5,29 | Inflation, Payroll Tax, Military Pay |
| Business & Industrial | 3,39 | 2,32 | 3,28 | Paga CCNL |

Conseguenza: **le stime del cruscotto (AdSense 3-5 € IT, 6-10 € EN) sono 2-3 volte troppo alte**. Il dato ufficiale dice ~1,5-2 € per 1.000 pagine viste in italiano e ~2,5-3 $ in inglese. In più, nel calcolatore il dato "Asia-Pacifico" unisce l'Australia (ricca) all'Asia del Sud (povera): per Pakistan, India e Bangladesh il valore reale è più basso, ma nessuna fonte ufficiale dà il numero per Paese.

**Premium (le reti non pubblicano RPM medi):** Raptive dichiara *"In January 2025, Raptive creators earned on average 18% higher RPMs year-over-year"* e una garanzia di +15 % sul fornitore precedente [R3]: nessuna cifra assoluta. Journey: solo racconti di singoli siti **(terzi)**, per esempio un blog con 17 $ per 1.000 pagine viste, "+277 % su AdSense". Attenzione: Mediavine misura l'RPM per sessione e AdSense per pagina, quindi i confronti di terzi gonfiano la differenza. Nel modello qui sotto Journey vale ×1,3 / ×1,7 / ×2,2 rispetto ad AdSense (prudente / centrale / ottimista), Raptive ×3 solo nell'ottimista.

## 4. Perché no ad Adsterra e Monetag (qualità e rischio)
- Le norme AdSense dicono: *"Publishers are not permitted to place Google ads on sites that contain or trigger pop-unders"* [A4]. Il pop-under è il loro formato di punta, quindi metterlo fa perdere AdSense sul sito. AdSense è anche il requisito di ingresso di Mediavine/Journey [M1].
- I loro annunci (Smartlink, push, redirect) sono la stessa cosa che AdSense ha già segnalato sui vecchi indirizzi netlify.app ("Site Behavior: Navigation"): fanno sembrare il sito uno che porta altrove. Sono un rischio anche per Google Search e per la fiducia di chi arriva da ChatGPT.
- Sui siti usati come fonte (scioperi, visti, regole d'imbarco) un annuncio di bassa qualità brucia la credibilità che porta le citazioni.
- L'unico uso concepibile sarebbe un sito senza AdSense e senza ambizioni di qualità: non ne abbiamo. **Verdetto: NO.**

## 5. Regolazioni di AdSense che alzano l'RPM (da fare appena i 3 domini sono approvati)
Pannello AdSense → Annunci → per sito → Auto ads (pagina ufficiale [A5]):
1. **Formati in pagina:** banner e **Multiplex** accesi; "related search" acceso solo dove la pagina non ha già i nostri link interni.
2. **Formati sovrapposti:** **anchor** acceso (mobile), **side rail** acceso (desktop), **vignette** acceso. Sono i formati che di solito rendono di più; nessuno dei tre è un pop-up vietato.
3. **Formati per intento** ("ad intents": link e chip sul testo) accesi sulle pagine in inglese. Su EsameB1 provarli solo con un esperimento, perché possono confondersi con i nostri link.
4. **Carico di annunci in pagina:** medio-alto, non al massimo. Le nostre pagine sono tabelle brevi: troppi annunci spingono giù il dato che la gente cerca e abbassano i clic da Google e le citazioni.
5. **"Existing ads" (ottimizza le unità esistenti)** acceso.
6. **Esperimento Auto ads** (50 % del traffico per 90 giorni [A5]): carico medio contro carico alto su Before You Fly, il sito con più pagine simili.
7. **Esclusioni:** pagine noindex (già senza AdSense: 307 su BYF, 495 su Visa Income) e moduli.
8. Messaggio di consenso UE/UK già pubblicato il 12/11. Chi non acconsente vede annunci limitati: è il motivo per cui l'Italia rende meno, e non si può cambiare.
Effetto stimato (stima nostra, nessuna fonte ufficiale dà una percentuale): +5 / +12 / +20 % sul ricavo AdSense.

I 3 vecchi indirizzi netlify.app con rinvio 301 restano "Needs attention" per sempre, perché rimandano altrove. Non si chiede la revisione per loro: gli annunci girano sui domini nuovi.

## 6. Piano: quale rete su quale sito, e quando

| Sito | Adesso | Scatto 1 | Scatto 2 |
|---|---|---|---|
| **Visa Income** | AdSense (in revisione) + Grow da subito | **Journey** quando Grow mostra ≥ 1.000 sessioni Tier 1 in 30 giorni (oggi ~975/mese: probabile domanda a metà dicembre, annunci a gennaio) | **Raptive** a 25.000 pagine viste al mese con Tier 1 ≥ 50 % (Google Analytics da installare a ~12.000 pagine viste, per avere lo storico) |
| **Before You Fly** | AdSense (in revisione) + Grow da subito | **Journey** a 1.000 sessioni Tier 1 (oggi ~690: +45 %, al ritmo attuale 3-6 settimane) | **Raptive** a 25.000 pagine viste, Tier 1 ≥ 50 % (oggi 48 %: spingere le pagine USA/UK) |
| **EsameB1** e tutti i siti italiani (EsamiDiStato, Aste, Paga CCNL, Codici ATECO, Farmaco, Quiz) | AdSense con Auto ads regolati | nessuno: Tier 1 al 5 %, e nessuna rete premium accetta traffico italiano sotto 100.000 visite | Setupad o Pubfuture **solo** se un sito supera 100.000 visite al mese (non in 12 mesi) |
| **9 siti US/UK del 13/11** (Military Pay, Inflation, NAICS, Statute, Heat Pump, Payroll…) | AdSense sull'indirizzo netlify.app (accettato) | a ~700 sessioni Tier 1 al mese su un sito: **dominio proprio** (10-15 €/anno, serve il sì) + Grow | Journey a 1.000 sessioni Tier 1 |
| Cruise, Tourist Tax, Italy Strikes, FHA, FloodCost, Balcony Solar | AdSense | come i siti US/UK se arrivano a 700 Tier 1 | – |
| Ezoic, Freestar, Snigel, Playwire, Monumetric, Adsterra, Monetag, Ad Manager in proprio | **mai in 12 mesi** | – | – |

**Regola di passaggio:** si lascia AdSense per Journey o Raptive su un sito solo dopo 30 giorni di confronto. L'RPM per sessione AdSense (ricavo AdSense ÷ sessioni Grow) va scritto nel cruscotto *prima* del cambio. Se dopo 60 giorni Journey non rende almeno il 20 % in più, si torna ad AdSense (Journey non dichiara vincoli di durata nelle pagine lette: da verificare nel contratto prima di firmare).

## 7. Azioni di Massimiliano (ognuna ≤ 10 minuti, nessuna richiede la Camera di Commercio)
1. **Oggi:** creare l'account gratuito su journeymv.com / Grow ("create a free publisher account"), aggiungere visaincomechecker.com e before-you-fly.com e passare a Claude il codice dello script Grow. Claude lo installa nei due siti alla prossima pubblicazione: da quel giorno contano i 30 giorni.
2. **Quando AdSense approva i 3 domini:** impostare gli Auto ads come nella sez. 5 (10 minuti per sito; Claude prepara la lista con le spunte).
3. **Quando Grow mostra 1.000 sessioni Tier 1 in 30 giorni** (Claude lo segnala dalla revisione del mercoledì): mandare la domanda Journey (5 minuti). All'approvazione: accettare il contratto, inserire IBAN e modulo fiscale in Tipalti (10 minuti). Claude sostituisce AdSense con lo script Journey e aggiorna `ads.txt`.
4. **A ~12.000 pagine viste al mese su BYF o Visa Income:** creare una proprietà Google Analytics 4 e dare a Claude l'ID (5 minuti). Serve per la domanda a Raptive a 25.000.
5. **Per ogni sito US/UK a ~700 sessioni Tier 1:** sì o no sull'acquisto del dominio (10-15 €/anno), poi DNS come per before-you-fly.com.
6. **Fatture:** stesso schema di AdSense (art. 7-ter, cliente estero). Nessuna registrazione nuova.

## 8. Euro in più rispetto al solo AdSense (12 mesi, dicembre 2026 - novembre 2027)

Modello: le pagine viste di ogni sito salgono in linea retta da oggi al valore del mese 12, con questi totali di rete al mese 12: prudente 19.000, centrale 48.000, ottimista 120.000 (gli stessi scenari della stima del cruscotto del 6/11). RPM AdSense sui dati ufficiali (EsameB1 1,6 €; Visa Income 2,2 €; BYF 2,5 €; siti US nuovi 2,6 €; altri 2,0 €; ×0,8 / ×1 / ×1,2 per scenario). AdSense parte a dicembre (prudente: gennaio). Journey su Visa Income dal mese 5 / 3 / 2 e su BYF dal mese 7 / 4 / 3; sui siti US nuovi solo nel centrale (un terzo del traffico dal mese 9) e nell'ottimista (metà, dal mese 6). Raptive solo nell'ottimista (BYF dal mese 10, Visa Income dall'11). Il calcolo è un foglio di poche righe, non salvato nel repo.

| Scenario | Solo AdSense (12 mesi) | Con il piano | **Differenza** | Ritmo annuo al mese 12: solo AdSense → piano |
|---|---|---|---|---|
| Prudente | 270 € | 305 € | **+40 €** | 400 → 470 €/anno (+70) |
| Centrale | 785 € | 1.110 € | **+325 €** | 1.300 → 1.890 €/anno (+590) |
| Ottimista | 2.265 € | 4.605 € | **+2.340 €** | 4.000 → 9.555 €/anno (+5.550) |

Da dove vengono i 325 € del centrale: Journey su Visa Income e BYF ~265; Journey sui siti US nuovi ~25; Auto ads regolati ~35. Nell'ottimista Raptive aggiunge ~390.

**Lettura onesta.** Con 7.200 visite al mese, di cui solo un terzo Tier 1, nessuna rete display porta cifre grandi in 12 mesi. Il salto vero (×2 sul ricavo pubblicitario) arriva solo se Before You Fly e Visa Income crescono al ritmo di queste settimane. Ogni ora su contenuti per lettori USA/UK/Australia vale più di qualsiasi cambio di rete: una pagina vista USA vale ~2 volte una italiana con AdSense e ~3-4 volte con Journey. Prossima verifica: revisione del mercoledì 16/12 (sessioni Tier 1 in Grow, primo RPM AdSense vero).

## Fonti (lette il 13/11/2026)
- [A1] AdSense, quota: https://support.google.com/adsense/answer/180195
- [A2] AdSense, cosa si può aggiungere ai siti: https://support.google.com/adsense/answer/12170421 · Public Suffix List: https://publicsuffix.org/list/public_suffix_list.dat
- [A3] AdSense, calendario pagamenti: https://support.google.com/adsense/answer/7164703
- [A4] AdSense, norme (pop-up, pop-under, navigazione): https://support.google.com/adsense/answer/1346295
- [A5] AdSense, impostazioni Auto ads: https://support.google.com/adsense/answer/9261307
- [A6] AdSense, dati del calcolatore: https://adsense.google.com/start/calculator-data.json (last-modified 9/12/2024)
- [M1] Mediavine, requisiti: https://www.mediavine.com/mediavine-requirements/ e https://help.mediavine.com/what-does-it-take-to-get-approved-by-mediavine
- [M2] Journey, home: https://www.journeymv.com/
- [M3] Mediavine, quote 2026: https://help.mediavine.com/revenue-share
- [M4] Mediavine, editori internazionali: https://help.mediavine.com/mediavine-international-publishers
- [M5] Journey, FAQ del programma: https://www.journeymv.com/?p=68755
- [M6] Journey, blog (70 %, Net 65): https://www.journeymv.com/?p=68646 (testo visto tramite motore di ricerca)
- [M7] Mediavine, pagamenti: https://help.mediavine.com/when-am-i-getting-paid e https://help.mediavine.com/mediavine-payment-methods (testo visto tramite motore di ricerca)
- [M8] Mediavine, blog sugli affiliati: https://www.mediavine.com/?p=9225 (tramite motore di ricerca)
- [M9] Mediavine, script su siti non WordPress: https://help.mediavine.com/installing-the-mediavine-script-wrapper-on-a-custom-built-site
- [R1] Raptive, soglia 25.000: https://raptive.com/blog/opening-the-door-to-more-creators-who-meet-raptive-quality-standards/
- [R2] Raptive, chi può entrare: https://help.raptive.com/hc/en-us/articles/360032840891 (403 al lettore; testo dal motore di ricerca)
- [R3] Raptive, creator di viaggio: https://raptive.com/travel-creators/
- [E1] Ezoic, requisiti: https://support.ezoic.com/kb/article/getting-started-ezoics-requirements · [E2] Incubator: https://www.ezoic.com/incubator
- [Mo1] Monumetric, requisiti: https://www.monumetric.com/requirements/ · [Mo2] https://www.monumetric.com/ascend/ (termini del contratto)
- [F1] Freestar FAQ: https://freestar.com/faq_category/amp (tramite motore di ricerca)
- [S1] Publisher Collective (Snigel), FAQ: https://publisher-collective.com/faq
- [P1] Playwire, criteri: https://www.playwire.com/qualification-criteria
- [St1] Setupad, home: https://setupad.com/ · [St2] FAQ: https://setupad.com/faqs/
- [Pf1] Pubfuture, FAQ dentro `https://pubfuture.com/static/js/main.c98d54b4.chunk.js` (la pagina è solo JavaScript)
- [Ad1] Adsterra: https://adsterra.com/publishers/ · [Mt1] Monetag: https://monetag.com/
- [G1] Ad Manager: https://support.google.com/admanager/answer/7084151 · [G2] fatturazione Ad Manager: https://support.google.com/admanager/answer/6214526 (tramite motore di ricerca)
- (terzi) racconti di RPM Journey: https://bloggingguide.com/journey-by-mediavine-review/ e simili: non usati come prova, solo come tetto ottimista
