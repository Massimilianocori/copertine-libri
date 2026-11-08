# Fronte mai toccato: obblighi e scadenze nuove 2026-2029 fuori dai nostri temi (8/11/2026, sera)

Angolo: partire da ciò che nasce adesso per legge o per decisione di un grande operatore, con una data, e che costringe molte persone a scegliere o comprare qualcosa. Settori mai toccati in ESPLORATE (controllate le parole chiave prima: rame/fibra/ADSL, broker di dati, prestiti per master e lauree professionali, tariffe di rete §14a). Esclusi per regola: viaggi, visti, immigrazione, esami di lingua, tasse locali, burocrazia per stranieri.

## Fonti esterne lette con curl l'8/11/2026

- **data.economie.gouv.fr**, dataset "Fermeture du réseau cuivre" (Ministères économiques et financiers, ultima modifica 20/10/2025; scheda su data.gouv.fr): API 200, **35.305 Comuni**, campi `fermeture_commerciale`, `fermeture_technique`, `lot`, `output_usager`. Chiusura tecnica: 766 Comuni il 27/1/2026, **2.155 il 31/1/2027**, 2.566 + 1.944 + 2.314 nel 2028 (31/1, 31/5, 31/10), 3.784 + 3.442 + 3.476 nel 2029; 14.688 senza data. (Export CSV interrotto dal proxy; i conteggi vengono dall'API con `group_by`.)
- **ariase.com**: sitemap lette. `box/test-fermeture-cuivre`, `box/carte-fin-adsl`, 441 articoli su cuivre/ADSL, **34.983 pagine Comune** (`/couverture/<dipartimento>/<comune>`): due pagine campione mostrano già "Fermeture commerciale: 31/01/2027 / Fermeture technique: Non communiqué".
- **degrouptest.com**: sitemap con 4.859 URL, articoli sulle liste dei Comuni ("les 2145 nouvelles communes…").
- **cppa.ca.gov/data_broker_registry/**: 200. Registro 2026 aggiornato il 30/10/2026, file `registry.csv` 200 con **625 righe** (nome, sito, email, categorie di dati raccolti: minori, geolocalizzazione precisa, salute riproduttiva, biometria; a chi vendono). Dal 1/1/2026 i residenti in California possono chiedere la cancellazione a tutti i broker con una sola richiesta (DROP). `cppa.ca.gov/drop/` 404.
- **optery.com/affiliate-program/**: 200, "**we pay 30% commission for 12 months**". La home ha già una "Data Broker Directory". Incogni, DeleteMe e Aura: pagine affiliati 404 o 403.
- **FlexOffers, Ascent Student Loans**: "**The payout is $40 per pre-qualified loan application** (submitted loan applications are excluded)", EPC 0,00 $ a 7/30/90 giorni (https://www.flexoffers.com/affiliate-programs/ascent-student-loans-affiliate-program/). Le pagine di Sallie Mae, College Ave, Earnest, Credible ed ELFI su FlexOffers sono la pagina di ripiego del sito (stesso testo "8 % / Mobile Phone Services"): **non valgono come cifra**. Poi FlexOffers ha risposto 429 e mi sono fermato. LendKey: programma attivo, "competitive payouts", nessuna cifra. College Ave, Earnest, Juno: 403 (pagina anti-bot, non aggirata).
- **College Scorecard API** (api.data.gov): con la chiave pubblica di prova risponde 429 (limite superato). Serve una chiave gratuita (registrazione con email).
- **abarequireddisclosures.org** (costi ufficiali delle facoltà di legge, Standard 509): pagina solo JavaScript. **LawHub / Law School Transparency** (LSAC) e **AccessLex**: 200, con i costi per facoltà e calcolatori.
- **tibber.com/de**: sitemap news con 3 articoli che spiegano le tariffe di rete variabili (nessuna tabella per gestore nella sitemap); pagina inviti senza cifra. Westnetz (gestore): 403. Verivox: 403. Finanztip, Bundesnetzagentur (pagina provata): 404. Check24 partner: pagina anti-bot. Rabot Energy, Octopus DE, 1KOMMA5°: pagine partner 404.
- **Bloccati e non usati**: DuckDuckGo (pagina anti-bot 202), Bing (nessun risultato leggibile). La composizione dei risultati di Google quindi non è letta: al suo posto ho letto i siti dei concorrenti attesi.

## Autocomplete Google (numero di suggerimenti)

| Paese | Domanda | N | Note |
|---|---|---|---|
| FR | fermeture cuivre / fermeture réseau cuivre / fermeture du cuivre / fin du cuivre / fermeture adsl / arrêt du cuivre | 10 ciascuna | "par commune", "dans ma commune", "lot 2…6", "carte", "date", "free/sfr/bouygues" |
| GB | digital switchover / landline switch off / pstn switch off / digital landline / bt digital voice / openreach stop sell | 10 ciascuna | "postcode checker openreach", "2027", "elderly", "stop sell exchange list" |
| DE | kupfer abschaltung / dsl abschaltung | 10 | "2030", "telekom", città |
| IT | spegnimento rame / switch off rame | 5 / 6 | domanda ancora piccola |
| US | grad plus loan / graduate loan limits / professional degree loan limit / private student loans for grad / rap repayment plan / parent plus loan cap | 10 ciascuna (grad plus elimination 9) | "2026", "big beautiful bill", "cap list", "calculator", "reddit" |
| US | medical school loan cap / law school loan cap / pa school loan limit / is nursing a professional degree / law school cost of attendance | 10 ciascuna | "med school loans capped at 200k", "is nursing a professional degree again", facoltà per nome |
| DE | zeitvariable netzentgelte / 14a modul 3 / steuerbare verbrauchseinrichtung / smart meter pflicht / dynamischer stromtarif | 10 ciascuna | gestori per nome: Westnetz, Bayernwerk, Netze BW, EWE; "tibber" |
| DE | modul 3 netzentgelte | 6 | |
| US | california drop / data broker / remove my information from / opt out of spokeo | 10 ciascuna | "portal", "tool", "for free", "without paying" |
| US | ada title ii / title ii web accessibility | 10 ciascuna | "deadline", "compliance" (pubblico di enti pubblici: non approfondito) |

---

## 0. Risposta in breve

| # | Idea | Fonte esterna da cui nasce | Chi paga (cifra letta) | €/anno a 18 mesi prudente / centrale / ottimista | Ore | Voto |
|---|---|---|---|---|---|---|
| 1 | **Quanto manca dopo i nuovi tetti dei prestiti federali, facoltà per facoltà** (USA, inglese: medicina, legge, PA, farmacia, infermieristica; tetti dal 1/7/2026) | autocomplete USA (10 su ogni forma, "professional degree loan cap list", "rap repayment plan calculator"); legge di bilancio USA 2025 | Ascent 40 $ a domanda pre-qualificata (FlexOffers, letta) | 800 / **3.700** / 19.000 | 50-70 agenti + 1 Massimiliano | **6** |
| 2 | Tariffe di rete variabili §14a "Modul 3" gestore per gestore (DE) | autocomplete DE (10 con i nomi dei gestori) | nessuna cifra letta | 150 / **1.200** / 4.000 | 40-60 | **5** |
| 3 | Broker di dati: scheda ufficiale per ogni broker del registro californiano + come chiedere la cancellazione | registro CPPA (625 righe, 30/10/2026), DROP dal 1/1/2026 | Optery 30 % per 12 mesi (letta) | 200 / **1.500** / 6.000 | 30-40 | **4,5** |
| 4 | Data di chiusura del rame Comune per Comune (FR) | dataset ministeriale 35.305 Comuni | nessuna cifra letta (pagine affiliati Bouygues/SFR 404) | 0 / **300** / 1.500 | 20-30 | **3,5** |

**Nessuna idea arriva a 8 e nessuna passa l'asticella del sito nuovo** (voto ≥ 7 e ≥ 5.000 €/anno centrali). La 1 ha l'**ottimista ≥ 10.000 €**.

---

## 1. Quanto manca dopo i nuovi tetti dei prestiti federali (USA) — voto 6 (approfondita)

**Fonte esterna da cui nasce:** il cambio di legge sui prestiti federali agli studenti (legge di bilancio USA del 2025): per chi inizia un master o una laurea professionale dal 1/7/2026 sparisce il Grad PLUS (che copriva tutto il costo), arrivano tetti annui e totali (secondo le pagine divulgative: 20.500 $ l'anno per i master, 50.000 $ per le lauree professionali, 200.000 $ totali; Parent PLUS con tetto). **Le cifre esatte non le ho lette su una fonte ufficiale stasera** (studentaid.gov è solo JavaScript, ed.gov risponde 403): vanno lette prima di costruire. La domanda in autocomplete è fortissima e nuova: "grad plus loans eliminated", "grandfathered in", "professional degree loan cap list", "is nursing a professional degree again", "med school loans capped at 200k", "pa school loan cap".

**Il nostro modo:** una pagina per facoltà e programma (prima legge, medicina, PA e farmacia, poi infermieristica e i master più cari) con: costo ufficiale di frequenza, tetto federale che si applica (professionale o no, con la data e la fonte), **quanto manca ogni anno e in totale**, se lo studente è "grandfathered" (iscritto prima del 1/7/2026), e il passo dopo: borse della facoltà, poi confronto dei prestiti privati con il link affiliato. Una pagina "is [programma] a professional degree" che si aggiorna quando il Ministero cambia la lista. Forma da citare per gli assistenti AI: tabella con cifra, data e fonte.

**Dati ufficiali:** College Scorecard (debito mediano e redditi per programma e facoltà; serve la chiave gratuita di api.data.gov), costi delle facoltà di legge dello Standard 509 dell'ABA (sito solo JavaScript: da capire se c'è un file), IPEDS per i costi medi dei master. Medicina: le tabelle AAMC non lette.

**Chi paga:** Ascent Student Loans su FlexOffers, **40 $ per domanda pre-qualificata** (non serve che il prestito venga erogato), letta. Gli altri grandi (Sallie Mae, College Ave, Earnest, SoFi, Credible, ELFI) hanno programmi, ma stasera nessuna cifra leggibile (403 o pagina di ripiego). In più AdSense con temi finanziari (valore per visita alto negli USA, non letto).

**Concorrenti:** NerdWallet, Bankrate, Forbes Advisor, The College Investor per le spiegazioni generali; **LawHub / Law School Transparency e AccessLex** hanno già i costi per facoltà di legge (enti senza scopo di lucro, molto autorevoli); AAMC per medicina. Il buco possibile è "costo meno nuovo tetto = quanto devo trovare", programma per programma, per PA, farmacia, infermieristica, fisioterapia e i master: non verificato su Google (motori bloccati).

**Stima a 18 mesi (maggio 2028; il picco è da febbraio ad agosto, quando si chiudono i finanziamenti per l'autunno):**
- prudente 800 €: 5.000 visite l'anno, 0,4 % fa la pre-qualifica (20 × 40 $) + poca pubblicità;
- centrale 3.700 €: 15.000 visite, 0,6 % pre-qualifica (90 × 40 $ = 3.600 $) + 400 € di pubblicità;
- ottimista 19.000 €: 60.000 visite (molte pagine programma indicizzate e citate dagli assistenti), 0,8 % (480 × 40 $) + 1.500 € di pubblicità.

**Ore:** 50-70 di agenti (lista dei programmi, costi ufficiali, regole del tetto, pagine, revisione dei fatti). Massimiliano: 1 ora (iscrizione a FlexOffers e chiave gratuita di api.data.gov).

**Rischi:** tema soldi e debiti (YMYL) su un dominio nuovo: Google lo spinge piano; regole ancora in movimento (lista dei corsi "professionali" contestata, infermieristica); l'approvazione di Ascent per un editore non americano non è sicura; 40 $ solo con pre-qualifica, quindi dipende da quanti cliccano; concorrenti senza scopo di lucro molto forti per la legge.

**Voto 6. Non passa** (centrale sotto 5.000 €); **ottimista ≥ 10.000 €**. Innesco per il 7: (a) lista ufficiale dei corsi "professionali" e dei tetti letta su una fonte federale; (b) un secondo pagatore con cifra letta (Sallie Mae, College Ave o SoFi) sopra i 50 $ a domanda; (c) prova che per PA, farmacia e infermieristica Google non ha già una pagina "gap" per facoltà. Con (a)+(b)+(c) il centrale sale a circa 5-6k e si propone come sito nuovo entro gennaio 2027 (per prendere la stagione dei finanziamenti 2027).

---

## 2. Tariffe di rete variabili §14a "Modul 3" gestore per gestore (Germania) — voto 5

**Fonte esterna:** regola tedesca sui consumi controllabili (pompe di calore, wallbox, batterie; §14a EnWG): dal 2025 chi ha questi apparecchi può scegliere il "Modul 3", con tariffe di rete diverse per fasce orarie decise da ogni gestore. Autocomplete: "zeitvariable netzentgelte" 10 (Bayernwerk, Netze BW, Westnetz, EWE, "tibber"), "14a modul 3" 10 ("beantragen", "voraussetzungen", "kosten", "separater zähler"), "smart meter pflicht" 10.

**Il nostro modo:** una pagina per gestore con fasce, prezzi in centesimi, risparmio stimato per una pompa di calore o un'auto, e il link al fornitore con tariffa dinamica.

**Dati:** ogni gestore pubblica il proprio listino (circa 860 gestori; i primi 20 coprono gran parte delle case). Westnetz 403, nessun file unico letto.

**Chi paga:** nessuna cifra letta (Tibber: invito senza importo; Check24 anti-bot; Rabot, Octopus DE, 1KOMMA5°: 404). Resta la pubblicità.

**Concorrenti:** i gestori stessi, Tibber con articoli che spiegano, Verivox (403, non letto).

**Stima:** 150 / 1.200 / 4.000 €/anno (solo pubblicità in tedesco; 15.000-200.000 pagine viste l'anno a 8-15 € ogni 1.000). **Ore:** 40-60, più l'aggiornamento a ogni nuovo listino (1° gennaio). **Voto 5. NO per ora.** Si riapre se compare un pagatore con cifra (Tibber, Rabot, Octopus o Check24 con importo per contratto) o un file unico dei listini della Bundesnetzagentur.

---

## 3. Broker di dati: scheda per broker e cancellazione (USA) — voto 4,5

**Fonte esterna:** registro dei broker di dati della California (CPPA), file `registry.csv` con 625 righe aggiornato il 30/10/2026; da gennaio 2026 la richiesta unica di cancellazione (DROP). Domanda forte: "california drop" 10 ("portal", "tool", "reddit"), "remove my information from" 10 (whitepages, spokeo, truepeoplesearch, fast people search), "opt out of spokeo" 10 ("without paying").

**Chi paga:** Optery, 30 % per 12 mesi (letta; prezzo dei piani non letto stasera: indicativamente 12-75 $ a cliente). Incogni, DeleteMe, Aura: nessuna cifra letta.

**Perché no:** chi paga è anche il primo concorrente. Optery ha già una "Data Broker Directory"; Incogni, DeleteMe, Permission Slip (Consumer Reports) ed elenchi gratuiti su GitHub coprono le stesse pagine broker per broker. Il registro ufficiale aggiunge poche colonne nuove (categorie di dati raccolti, a chi vendono), ma non cambia la risposta alla domanda vera ("come mi cancello").

**Stima:** 200 / 1.500 / 6.000 €/anno. **Ore:** 30-40. **Voto 4,5. NO.**

---

## 4. Chiusura della rete in rame Comune per Comune (Francia) — voto 3,5

**Fonte esterna:** il dataset del Ministero (35.305 Comuni, chiusure tecniche dal 2026 al 2029: 2.155 Comuni il 31/1/2027, 6.824 nel 2028, 10.702 nel 2029). La domanda è enorme e datata ("arrêt du cuivre dans ma commune", "fermeture cuivre lot 3/4/5/6").

**Perché no:** **Ariase**, il comparatore francese delle offerte internet, ha già una pagina per ognuno dei 34.983 Comuni con le due date (commerciale e tecnica), un test e una mappa, più 441 articoli; Degrouptest pubblica le liste a ogni lotto; lo Stato ha il suo strumento di ricerca (il campo `output_usager` del dataset è il testo che mostra). Nessun pagatore con cifra letta (Bouygues e SFR: pagine affiliati 404).

**Regno Unito (digital switchover entro il 31/1/2027):** domanda forte ("landline switch off postcode checker openreach"), ma il controllo per codice postale lo dà Openreach stesso e i comparatori di internet sono enormi. Non approfondito. **Germania e Italia:** chiusure fino al 2030, domanda ancora generica (IT 5-6 suggerimenti).

**Stima:** 0 / 300 / 1.500 €/anno. **Voto 3,5. NO.**

---

## Esito e lezione

- La migliore è la **1 (voto 6; 800 / 3.700 / 19.000 €/anno)**: la domanda è nuova e fortissima, il pagatore paga a domanda e non a prestito erogato, ma il tema è soldi e debiti su un dominio nuovo e la legge sta ancora cambiando. Resta **RISERVA alta con innesco scritto** (sez. 1), da ricontrollare entro dicembre 2026.
- **Lezione:** quando una data nuova di legge colpisce milioni di persone, il primo a rispondere bene è chi ci guadagna (Ariase per il rame, Optery per i broker), oppure un ente senza scopo di lucro (AccessLex e LawHub per la legge). Il buco resta solo dove il pagatore non ha ancora pagine sue: per i prestiti, i corsi che non sono legge né medicina (PA, farmacia, infermieristica, master).
- **Prossimo angolo suggerito:** non "legge nuova" ma "prodotto nuovo che si compra una volta e costa tanto" (mercati dell'usato di oggetti nuovi, ricambi, compatibilità), dove il pagatore è un negozio e non un comparatore.

## Cosa servirebbe da Massimiliano (solo se si apre la 1)
- Iscrizione gratuita a FlexOffers e domanda al programma Ascent (5-10 minuti).
- Chiave gratuita di api.data.gov per College Scorecard (2 minuti, solo email).
Nessuna spesa.
