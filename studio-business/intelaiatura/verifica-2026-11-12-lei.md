# Verifica indipendente: confronto neutrale dei prezzi del codice LEI + "controlla il tuo LEI" dai dati GLEIF, 12/11/2026

Approfondimento 1 di `fronti-2026-11-12-radar-pagatori.md` (voto del ricercatore 6; 300 / 2.400 / 12.000 €/anno; 25-35 ore). Tutto riletto oggi con curl dal server; dove un dato non è stato letto, è scritto. Cambio usato: 1 £ = 1,15 €, 1 $ = 0,92 €.

## 1. Verdetto

- **GO-piccolo** (versione ridotta da 14-16 ore, non il sito completo da 30). Entra in coda per €/anno ÷ ore; non scavalca le cose che rendono di più.
- **Voto: 5** (era 6).
- **Stima rifatta: 90 / 900 / 10.000 €/anno a 18 mesi** (era 300 / 2.400 / 12.000). Versione piccola: circa 60 / 650 / 7.000 con 15 ore più 1 ora al mese di rilettura dei prezzi.
- **Prove: 3 e mezza su 4.** Domanda sì (ma in gran parte "di marca", verso l'ente ufficiale). Dati sì, pieni. Pagatore sì con cifra scritta, ma **senza condizioni scritte** (mezza prova). Nessuno fa già meglio: sì per l'Italia; per Germania, Regno Unito e Paesi Bassi non ho potuto leggere i risultati di ricerca (limite dichiarato alla sezione 6).
- **Perché non di più: tre fatti nuovi che il ricercatore non aveva.**
  1. **L'ente ufficiale tiene il mercato molto più di "circa metà".** Contati oggi dall'API GLEIF sui codici attivi: InfoCamere 79 % in Italia, Camera di commercio olandese 89 %, INSEE 76 % in Francia, Registradores 79 % in Spagna, Bundesanzeiger + WM 73 % in Germania, Borsa di Londra 51 % nel Regno Unito. Chi rinnova lì riceve il promemoria dell'ente e non cerca.
  2. **L'ente ufficiale è quasi sempre il più economico sul rinnovo di un anno.** Paesi Bassi 49,20 € senza IVA, Francia 50 €, Regno Unito 50 £: gli agenti costano uguale o di più. Un confronto onesto, in questi Paesi, manda il lettore dall'ente che non paga commissioni.
  3. **Gli agenti convengono davvero solo sui piani da 3-5 anni** (45-49 € l'anno contro 65-70) e, per un anno, solo in Italia e Germania e di pochi euro. È lì, e solo lì, che il link affiliato è onesto.
- **Rischio più grande:** poche vendite. Non c'è un rischio legale serio (il LEI non è un prodotto finanziario; i prezzi sono pubblici), a patto di rispettare una clausola dei termini GLEIF (sezione 2).

## 2. Dati GLEIF

| Cosa | Letto oggi |
|---|---|
| Licenza | `gleif.org/en/meta/lei-data-terms-of-use` (200): "The Access Service … is provided for free. The data available through the Access Service are provided under the **CC0** licence". Vale per file e API. Uso commerciale libero, attribuzione non obbligatoria (la mettiamo lo stesso). |
| Clausola da rispettare | Stessa pagina, art. IV (c): vietato dare l'impressione che il servizio sia "provided or supported or authorized" da GLEIF o da un ente emittente, o di avere con loro un rapporto speciale; il logo GLEIF è un marchio registrato. **Penale scritta: 100.000 franchi svizzeri per ogni violazione**, foro di Basilea. Quindi: niente logo, niente "ufficiale" nel nome o nel dominio, frase fissa in ogni pagina "sito indipendente, non collegato a GLEIF né agli enti emittenti". |
| API | `api.gleif.org/api/v1/lei-records` 200 senza chiave. Risposta con `access-control-allow-origin: *`: **lo strumento può chiamarla dal browser del visitatore**, senza un nostro server. |
| Limite | Documentazione dell'API (200): "Rate limiting is currently set at 60 requests, per minute, per user". Con le chiamate dal browser il limite è del singolo visitatore: nessun problema. Per le statistiche bastano circa 300 chiamate al mese dal nostro raccoglitore. |
| Campi | Letti su un record vero: `entity.legalName`, `legalAddress` (via, città, CAP, Paese), `entity.status`, `registration.status` (ISSUED / LAPSED…), `registration.nextRenewalDate`, `registration.managingLou`, `initialRegistrationDate`, `registeredAs` (numero di registro). Filtri per Paese, stato, ente e intervallo di date: funzionano tutti (provati). |
| Emittenti | `lei-issuers` 200: 41, con nome e sito. |

**Numeri contati oggi (attivi / scaduti per sede legale):** Italia 174.037 / 68.044; Germania 187.042 / 55.810; Paesi Bassi 130.364 / 46.698; Regno Unito 95.197 / 117.652; Francia 97.018 / 74.963; Spagna 106.029 / 78.709; Irlanda 22.992 / 11.483. Coincidono con quelli del ricercatore.

**Quota dell'ente nazionale sui codici attivi (dato nuovo):**

| Paese | Ente nazionale | Suoi attivi | Quota | RapidLEI (l'ente dietro quasi tutti gli agenti) |
|---|---|---|---|---|
| Italia | InfoCamere | 137.816 | 79 % | 15.086 (9 %) |
| Paesi Bassi | Camera di commercio (KvK) | 115.943 | 89 % | 4.044 (3 %) |
| Francia | INSEE | 73.496 | 76 % | 3.261 (3 %) |
| Spagna | Registradores | 83.709 | 79 % | 7.143 (7 %) |
| Germania | Bundesanzeiger 82.852 + WM 53.312 | 136.164 | 73 % | 21.952 (12 %); EQS 15.082 |
| Regno Unito | Borsa di Londra | 48.648 | 51 % | 22.535 (24 %); Bloomberg 10.704 |
| Irlanda | Borsa irlandese (Euronext) | 5.555 | 24 % | 3.539 (15 %) |

Il ricercatore aveva scritto "circa metà" per l'Italia da un campione di 200: è 79 %. Il mercato libero vero è Regno Unito, Irlanda e, in parte, Germania.

**Stagionalità: piatta.** Rinnovi italiani in scadenza in 28 giorni di gennaio, aprile, luglio, ottobre 2027: 12.203, 12.351, 12.044, 14.329. Nessun picco: traffico costante tutto l'anno.

**Pagine "sottili" (rischio AdSense).** Una pagina per ogni codice sarebbe un modello ripetuto 3,5 milioni di volte con gli stessi 10 campi: è esattamente ciò che ha fatto bocciare il sito gemello, ed esiste già (lei-lookup.com ha una pagina per codice con stato, data di rinnovo, ente e pulsante "Renew now"; in più la ricerca ufficiale GLEIF). **Non si fa.** Il singolo codice si mostra solo dentro lo strumento, nel browser, senza pagina propria.

## 3. Prezzi (letti oggi, 12/11/2026)

**Enti ufficiali**

| Ente | Nuovo | Rinnovo 1 anno | IVA | Fonte |
|---|---|---|---|---|
| InfoCamere (IT) | 69 € | 65 € | esclusa; quota GLEIF di 11 $ compresa | lei-italy.infocamere.it (200) |
| Bundesanzeiger (DE) | 80 € | 70 € | non letta sulla pagina | leireg.de/de/preise (200) |
| WM Datenservice (DE) | – | – | – | pagina 200 ma prezzi caricati con JavaScript: **non letti** |
| KvK (NL) | 80 € | 49,20 € | "VAT exempt" | kvk.nl/en/lei (200) |
| INSEE (FR) | 110 € | 50 € | "net de taxe"; trasferimento gratuito | lei-france.insee.fr (200) |
| Borsa di Londra (UK) | 65 £ | 50 £ (47,50 £ se prepagato con la richiesta; 45 £ su 3 anni) | non letta | lseg.com (200) |
| Registradores (ES), Euronext (IE) | – | – | – | **non letti** (reindirizzamento infinito; applicazione senza testo) |

**Agenti ed emittenti privati**

| Venditore | 1 anno | 3 anni | 5 anni | Note |
|---|---|---|---|---|
| LEI Worldwide | 59 € | −2,5 % | −5 % | IVA non scritta; agente di RapidLEI |
| LEI Service (leiservice.com) | 64 € | 165 € | 225 € (45 €/anno) | IVA esclusa |
| Registro LEI / leicertificate (rete LEI Register) | 65 € | 165 € | 49 €/anno | + IVA |
| LEI Register (leinumber.com) | 75 $ | 195 $ | 275 $ | la pagina partner mostra ancora 60 / 165 / 245 $: **due listini diversi sullo stesso sito** |
| LEI-Registrar | 75 $ | 195 $ | 275 $ | – |
| RapidLEI (emittente) | 70 € / 50 £ / 70 $ | 200 € | 63 €/anno | stesso prezzo nuovo e rinnovo |
| lei.info | 64,20 $ nuovo; 50,42 $ rinnovo | 157,52 / 143,70 $ | 240,03 / 226,90 $ | – |
| LEI Ireland | 79 € nuovo; 65 € rinnovo | 195 € | 240 € | registra su EQS |
| NordLEI (emittente) | 99 € nuovo; 79 € rinnovo | 75 / 65 €/anno | 65 / 60 €/anno | – |

**Cosa dice un confronto onesto:**
- Rinnovo di 1 anno: Paesi Bassi, Francia, Regno Unito → **vince l'ente ufficiale** (o pareggia). Italia → LEI Worldwide costa 6 € meno di InfoCamere, gli altri uguale. Germania → LEI Worldwide 11 € meno del Bundesanzeiger.
- Piani da 5 anni → **vincono gli agenti**: 45-49 € l'anno contro 65-70. Risparmio vero: 80-125 € in cinque anni, pagando tutto in anticipo.
- Codice nuovo → in Francia (110 €) e nei Paesi Bassi (80 €) gli agenti (59-65 €) costano meno il primo anno, poi conviene trasferire all'ente: è un consiglio utile che nessun venditore scrive.

**È possibile ed è lecito?** Sì. Sono prezzi pubblici; riportarli con data e fonte è informazione. Il LEI è un identificativo, non un prodotto finanziario: nessuna autorizzazione serve per confrontarlo (diverso dal caso dei prestiti britannici dell'11/11). Obblighi: dichiarare i link affiliati, non usare loghi, rispettare la clausola GLEIF. Fatica vera: IVA scritta in modi diversi, valute diverse, listini che cambiano (LEI Register ne ha due oggi) → rilettura mensile obbligata, circa 1 ora.

## 4. Pagatori

| Programma | Scritto sulla pagina (letto oggi) | Non scritto |
|---|---|---|
| **LEI Worldwide** (lei-worldwide.com/partners.html, 200) | "**Earn 20% commission on each transaction**"; link personale; cruscotto; pagamento "in monthly billing cycles" con PayPal, bonifico, fattura o link di pagamento; iscrizione dal modulo | durata del cookie, soglia minima, Paesi ammessi, se vale sui rinnovi degli anni dopo. Nei termini generali del sito la parola "affiliate" **non c'è**: le condizioni non sono pubbliche. |
| **LEI Ireland** (lei-ireland.ie/become-a-partner, 200) | "commission rates **up to 50€ per referral**"; pagina con il marchio del partner; sconti fino al 25 % ai clienti; "contact our sales department for a personalised partnership offer" | la cifra vera: "up to" vale con ogni probabilità per i piani da 5 anni (240 €). È un programma per commercialisti e banche con clienti propri, **offerta su misura, non un programma aperto con cifra fissa**. E i suoi prezzi (65-79 €) non sono i migliori: da consigliare c'è poco. |
| LEI Register (leinumber.com/become-a-partner, 200) | "generate revenue from each referral", "referral program" compreso in LEIAdmin | **nessuna percentuale scritta**; il "fino al 30 %" resta non letto. Prova che il programma paga editori: leicertificate.org dichiara in fondo "7 Out Media AB is a partner of LEI Register" ed è nei primi 10 in Italia. |
| RapidLEI (rapidlei.com/partners, 200) | solo percorsi per agenti di registrazione e di validazione | nessuna affiliazione per editori |
| NordLEI | pagina "Referral Partner" 200 | nessuna cifra |

**Partita IVA italiana in regime forfettario:** nessuna pagina la esclude; LEI Worldwide è irlandese, quindi fattura della commissione a impresa UE (serve l'iscrizione al VIES). Da confermare all'iscrizione: è una delle domande della sezione 8.

**Commissione attesa (LEI Worldwide, 20 %):** 11,80 € su un anno; circa 34 € su tre anni; circa 56 € su cinque. Media prudente con 70 % di vendite annuali: **20 €**.

**È onesto consigliarli accanto all'ente ufficiale?** Sì, a tre condizioni: (1) l'ente ufficiale è sempre in tabella, con il suo link non affiliato; (2) l'ordine è per prezzo totale, non per commissione; (3) dove l'ente è più economico lo scriviamo in chiaro ("per un solo anno: rinnova da KvK"). Il link affiliato compare solo dove l'agente fa davvero risparmiare. Questo taglia i clic affiliati, ed è messo nel conto.

## 5. Domanda

Autocomplete Google letto oggi (numero di suggerimenti):

| Paese | Ricerche | Cosa mostrano |
|---|---|---|
| IT | "codice lei costo" 8; "rinnovo codice lei" 10; "verifica codice lei" 9; "codice lei scaduto" 4; "codice lei confronto" 0 | quasi tutti con "infocamere", "camera di commercio"; "verifica scadenza codice lei" c'è |
| DE | "lei nummer kosten" 6; "lei verlängern" 9; "lei nummer abfragen" 2; "lei nummer günstig" 2; "lei kosten vergleich" 1 | qui la ricerca di confronto esiste |
| NL | "lei code kosten" 4; "lei code verlengen" 2; "lei code opzoeken" 2 | "kvk" ovunque |
| GB | "lei renewal cost" 8; "lei number lookup" 10; "lei number check" 10; "cheapest lei" 0 (solo Leica) | molte code sull'India |
| FR | "renouvellement lei" 10; "code lei prix" 1; "recherche code lei" 3 | "insee" |
| ES | "renovar codigo lei" 7; "codigo lei precio" 2; "consultar codigo lei" 2 | "registradores" |
| IE | "lei renewal" 10; "lei number ireland" 6 | – |
| US | "lei comparison" 0; "lei number cost comparison" 0 | nessuno cerca "confronto" in inglese |

Lettura severa: la domanda c'è in 7 Paesi ma è **navigazionale** (la gente scrive il nome dell'ente). Le ricerche utili a noi sono costo, rinnovo, scaduto e "verifica": piccole. Nessun volume misurato (l'autocomplete non dà numeri).

## 6. Concorrenti

**Limite dichiarato.** Google non è leggibile dal server. DuckDuckGo ha risposto una volta sola (Italia), poi 202; Brave 429; Bing ha dato risultati fuori tema; Mojeek 403. Non ho aggirato nulla: **ho i primi 10 solo per "codice lei costo" (Italia, DuckDuckGo, non Google)**. Per Germania, Regno Unito e Paesi Bassi restano le letture del ricercatore, non verificate.

**"codice lei costo", primi 10:** InfoCamere e Registro Imprese (5 risultati su 10, compreso un PDF), registrolei.it (venditore, rete LEI Register), leiservice.com (2 risultati, venditore danese), leicertificate.org (**affiliato** di LEI Register con dominio da venditore), pro-aiuto.com (venditore di visure, articolo del 27/8/2026 con i soli prezzi InfoCamere). **Nessun comparatore neutrale.**

**Tre concorrenti su cinque esempi concreti:**

| Esempio | registrolei.it / leicertificate (rete LEI Register) | leiservice.com | lei-lookup.com |
|---|---|---|---|
| 1. Rinnovo 1 anno in Italia | solo il proprio: 65 € | proprio 64 € + **riquadro "Confronto dei prezzi" datato 10.11.2026**: InfoCamere 69 €, Italia LEI 89 € (solo il prezzo del nuovo; tace che il rinnovo InfoCamere è 65) | nessun prezzo |
| 2. Piano da 5 anni | 49 €/anno | 225 € | – |
| 3. "Dall'ente ufficiale costa meno?" (NL, FR, UK) | non lo dice; scrive solo "quando confronti… assicurati che ti comunichino il costo totale" | non lo dice | non lo dice |
| 4. Codice scaduto: stato, data, chi lo gestisce | – | – | **sì**: stato, prossima data di rinnovo, ente gestore, poi pulsante "Renew now" verso il proprio servizio |
| 5. Trasferire all'ente più economico | solo verso di sé ("gratuito") | solo verso di sé | solo verso di sé |

**Cosa manca a tutti:** la tabella con più fornitori e l'ente ufficiale insieme, il costo totale su 1, 3 e 5 anni con IVA, la frase "per te la strada più economica è…" dopo aver letto lo stato del codice, i numeri per ente (quanti codici, quanti scaduti). Il vuoto c'è. Ma i venditori hanno domini a nome esatto, anni di anzianità, reti di siti gemelli e un affiliato già piazzato: salire è lento.

## 7. Disegno delle pagine (profondità vera, circa 60 pagine, non milioni)

1. **Strumento "controlla il tuo LEI"** (una pagina per lingua). Codice o nome → chiamata dal browser all'API GLEIF → stato, giorni alla scadenza, ente gestore; sotto, **calcolato sul caso**: quanto costa rinnovare dove sei, quanto costerebbe trasferire (gratis) e rinnovare altrove per 1, 3, 5 anni, quanto risparmi. Nessuna pagina per codice. Intorno, testo fisso: cosa succede se scade, come si trasferisce.
2. **Pagine "quanto costa" per Paese** (IT, DE, UK, NL, FR, ES, IE, nella lingua del Paese): tabella ente ufficiale + 6-8 venditori con totale a 1, 3, 5 anni, IVA, valuta, data di lettura e link alla fonte; il vincitore per ogni caso; quota di mercato dell'ente dal dato GLEIF; codici attivi e scaduti del Paese.
3. **Pagine per emittente** (solo quelli con prezzo letto, 12-15 su 41): prezzi ufficiali, Paesi serviti, codici gestiti, quota di scaduti, come trasferire via da lì o verso di lì.
4. **Statistiche sugli scaduti**: classifica dei Paesi e degli emittenti per quota di codici scaduti, rinnovi in scadenza mese per mese, aggiornate ogni mese dall'API. È contenuto che nessun venditore pubblica e che si può citare.
5. **Guide brevi** (6-8): scaduto cosa succede, trasferimento passo passo, piano pluriennale sì o no (rischio di pagare in anticipo a un agente), ente o agente.

Ogni pagina ha dati propri e un confronto calcolato: niente modello × luogo.

**Versione piccola (GO-piccolo):** strumento in italiano e inglese; pagine costo per Italia, Regno Unito, Germania, Irlanda (dove gli agenti hanno senso); una pagina di statistiche; 3 guide. Circa 14 pagine, 14-16 ore. Paesi Bassi, Francia e Spagna dopo, e solo con pubblicità (lì l'affiliazione non rende: vince l'ente).

## 8. Ore, stima, voto

**Ore (agenti):** sito completo 30 (raccoglitore prezzi e API 8, strumento 6, pagine e traduzioni 12, controlli 4) + 1 ora al mese = 48 in 18 mesi. Versione piccola 15 + 1 al mese. **Massimiliano: 30 minuti** (sotto).

**Formula:** visite/anno × quota che clicca un link affiliato × quota che compra × 20 € + visite × 1,5 pagine × ricavo per mille pagine.

| | Visite/mese | Clic affiliato | Acquisto | Vendite/anno | Affiliazione | Pubblicità | **Totale** |
|---|---|---|---|---|---|---|---|
| Prudente | 200 | 3 % | 5 % | 4 | 70 € | 20 € (6 €/mille) | **90 €** |
| Centrale | 800 | 5 % | 8 % | 38 | 770 € | 115 € (8 €/mille) | **900 €** |
| Ottimista | 5.000 | 7 % | 10 % | 420 (a 22 €) | 9.240 € | 900 € (10 €/mille) | **10.000 €** |

Perché più basso del ricercatore (2.400 centrali): 79-89 % dei rinnovi passa dall'ente e non cerca; il confronto onesto manda all'ente gran parte di chi arriva; cookie e rinnovi futuri non sono garantiti per iscritto. Il caso ottimista chiede di superare venditori con domini a nome esatto: possibile solo se lo strumento e le statistiche vengono citati.

**€ centrali per ora:** completo 900 ÷ 48 = 19; piccolo 650 ÷ 33 = 20. Basso ma positivo, a costo zero.

**Voto 5.** Obbligo ricorrente, dato aperto perfetto, vuoto dimostrato in Italia: bene. Mercato piccolo, in mano agli enti, pagatore unico e senza condizioni scritte: male.

**Le 4 prove**
1. Domanda: **sì, modesta** (7 Paesi, in gran parte di marca).
2. Dati leggibili: **sì** (CC0, API aperta dal browser, 60 richieste al minuto, prezzi letti per 5 enti e 9 venditori; 3 enti non letti).
3. Pagatore attivo: **mezza** (20 % scritto e iscrizione aperta; cookie, soglia e Paesi non scritti; il secondo pagatore è un'offerta su misura).
4. Nessuno fa già meglio: **sì in Italia**; non verificato altrove.

## 9. Cosa deve fare Massimiliano (30 minuti, zero spese)

1. **Iscriversi al programma di LEI Worldwide** (modulo su lei-worldwide.com/partners.html) e chiedere per iscritto, prima che si costruisca: durata del cookie; soglia minima di pagamento; se la commissione vale anche sui rinnovi successivi; se accettano un sito editoriale italiano con partita IVA forfettaria; se il 20 % è sul prezzo senza IVA. **Senza queste risposte non si parte**: è la mezza prova che manca.
2. **Scrivere a LEI Register** (partner@leiadmin.com, indirizzo pubblicato sulla loro pagina) per avere la percentuale del programma segnalazioni: hanno i prezzi migliori sui 5 anni e un affiliato già attivo in Italia. È una richiesta a un programma partner pubblico, non un'email a freddo a clienti.
3. Verificare di essere nel VIES (fatture a imprese irlandesi ed estoni).
4. Dominio: **non serve comprarlo ora**. La versione piccola può uscire su un indirizzo gratuito o come sezione; il dominio si chiede solo dopo le prime vendite.

LEI Ireland: non iscriversi adesso (prezzi non competitivi, offerta su misura).

## 10. Fonti (lette oggi)

gleif.org/en/meta/lei-data-terms-of-use; api.gleif.org/docs; api.gleif.org/api/v1/lei-records e /lei-issuers (conteggi con filtri per Paese, stato, ente, data); lei-italy.infocamere.it; leireg.de/de/preise; kvk.nl/en/lei; lei-france.insee.fr; lseg.com (pagina LEI, "Fees and Payments"); lei-worldwide.com (prezzi, partners.html, termini); lei-ireland.ie (prezzi, become-a-partner, termini); leinumber.com (prezzi, become-a-partner); lei-registrar.com/en/pricing; rapidlei.com (lei-price, partners); lei.info; nordlei.org; registrolei.it/codice-lei-costo; leiservice.com/prezzi; leicertificate.org/it/tariffe-lei; pro-aiuto.com (articolo sul LEI); lei-lookup.com (pagina di un codice); suggestqueries.google.com (27 ricerche in 8 Paesi); html.duckduckgo.com (1 ricerca riuscita). Non letti: wm-leiportal.org (prezzi in JavaScript), justicia.lei.registradores.org, Euronext, risultati di ricerca per DE, UK, NL.
