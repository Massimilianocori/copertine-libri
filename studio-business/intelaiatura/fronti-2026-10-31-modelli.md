# Fronte nuovo del 31/10/2026: guadagnare in modi diversi da AdSense e affiliazioni

**Domanda.** Con gli asset che abbiamo (dati ufficiali puliti e aggiornati da soli, pagine con traffico, costruzione veloce), si può guadagnare in altri modi? Cinque famiglie: (1) vendita o licenza di dati e API su negozi che trovano i clienti al posto nostro; (2) avvisi a pagamento su piattaforme self-service; (3) sponsorizzazioni tramite negozi di sponsor; (4) contatti (lead) pagati a prezzo fisso tramite reti; (5) widget per aziende. In più ho valutato una sesta via nata nel 2025-2026: farsi pagare dai robot delle IA.

**Letti prima:** skill `rete-siti`, `REGOLE-FISSE.md`, `ESPLORATE.md`, `idee-2026-10-31-soldi.md`, `CRUSCOTTO-RETE.md` (numeri veri), `STRATEGIA.md` sez. 10 (cancello fiscale). Ci sono già studi su questo terreno e **qui non li rifaccio**: studio 7 (Apify e RapidAPI), studio 13 (scioperi per aziende), studio 15 (AWS Data Exchange, Datarade, Snowflake, Kaggle, newsletter con sponsor), `idee-grandi-2026-10-17` sez. 4 (contatti dopo il consulente), `affari-test-fonti` (licenze PVP e OMI). Aggiungo solo le prove nuove del 31/10.

**Prove, tutte del 31/10/2026:** `curl` dal nostro server (codice HTTP e testo letto), API pubblica del negozio Apify (ricerca per parola, utenti totali e degli ultimi 30 giorni), Google Autocomplete (`suggestqueries.google.com`, `client=firefox`, Paese e lingua scritti ogni volta), ricerca web. Le cifre lette solo su elenchi di terzi sono segnate **"non letto sulla pagina ufficiale"**. Le stime sono a 18 mesi, in euro lordi all'anno, con il conto scritto (1 $ = 0,9 €). Sono stime, non dati.

**Il punto di partenza vero (cruscotto, 28 e 30/10):** circa 1.300 visite al mese su tutta la rete. EsameB1 ~750, Visa Income ~55 a settimana (quasi tutte da ChatGPT), **FloodCost 0, ApprovedCondos 0, Italy Strikes 0, Aste in Chiaro 3-5 a settimana**. Modulo "business" di Italy Strikes: **0 richieste dal 10/10**. Ogni stima qui sotto dipende da traffico che oggi in gran parte non c'è.

**Avvertenza fiscale (non è consulenza, da chiedere al CAF).** Massimiliano ha P.IVA forfettaria con codici ATECO di fotografia ed editoria. Le vie si dividono in due gruppi:
- **Gruppo A, "come la pubblicità":** paga una rete (CJ, FlexOffers, Awin) a prezzo fisso per un modulo compilato. Il cliente finale non compra niente da noi. Domanda per il CAF: questi compensi rientrano nei codici attuali o serve un codice in più (pubblicità o portali web)?
- **Gruppo B, "vendita a molti clienti":** dati, API, avvisi a pagamento, widget, sponsor. Su Apify il venditore resta Massimiliano: la piattaforma emette le fatture a suo nome (studio 15). È la stessa domanda della regola 2: vendita continuativa, quindi forse un codice nuovo e forse INPS commercianti, circa 4.000 €/anno (STRATEGIA sez. 10). Con questo costo il gruppo B ha senso solo sopra i 5.000 €/anno, e nessuna riga ci arriva.

---

## 0. Risposta in breve

| # | Via | Chi paga e quanto (fonte) | Voto | 18 mesi €/anno (prudente / centrale / ottimista) | Ore | Esito |
|---|---|---|---|---|---|---|
| 1 | **Contatti per assicurazione casa e alluvione USA a prezzo fisso** (FloodCost) | Lemonade 15 $ a contatto (letto il 17/10); Liberty Mutual ~10 $ a preventivo, Hippo 25 $, Allstate fino a 28 $ (CJ e FlexOffers, **non letti sulla pagina ufficiale**) | **5,5** | 190 / 1.440 / 6.700 | 4-6 | **Una delle 2 migliori**: si accende con le iscrizioni alle reti, senza vendita diretta |
| 2 | **Contatti per mutuo FHA a prezzo fisso** (ApprovedCondos) | LendingTree fino a 35 $ a modulo via CJ (`idee-grandi-2026-10-17`, n. 29) | **5,5** | 220 / 1.620 / 7.200 | 3-4 | **Una delle 2 migliori** (stessa logica della 1) |
| 3 | API delle tasse di soggiorno (Apify + Zyla) | Sviluppatori di gestionali per affitti brevi; Trippz vende un'API simile alle piattaforme (prezzo non pubblico); Zyla dà l'80 % al fornitore | 4,5 | 0 / 250 / 2.400 | 8-12 | RISERVA: si pubblica solo dopo la domanda al CAF |
| 4 | Dataset e API delle aste con sconto sul valore OMI (Apify) | 5 Actor sulle aste italiane già in vendita: 11-29 utenti in tutto, 1-4 al mese | 4 | 50 / 290 / 1.900 | 6-10 | RISERVA debole: concorrenti già presenti, mercato di pochi utenti |
| 5 | Contatti in Italia (mutuo per l'asta, traduzioni giurate) | MutuiSupermarket paga per ogni domanda di mutuo (cifra non pubblica); traduzioni chiuse il 26/10 | 3 | 0 / 150 / 900 | 4-6 | NO per ora: nessuna cifra scritta, nodo della mediazione creditizia |
| 6 | API degli scioperi italiani (Apify) | Nessun compratore trovato (studio 13); "italy strike api" e "scioperi api" senza suggerimenti | 3 | 0 / 100 / 600 | 2-4 | Solo test passivo, come già deciso (studio 7) |
| 7 | Pagamento dai robot delle IA (TollBit, Cloudflare) | TollBit: gratis per gli editori, ~7.000 siti, ~20 % ha incassato qualcosa (Digiday); Cloudflare: "closed beta" | 2,5 | 0 / 30 / 300 | 6-10 + dominio | NO: Netlify non è tra le integrazioni, rischio di perdere le citazioni di ChatGPT |
| 8 | Avvisi a pagamento (scioperi, aste per zona, date dell'esame B1) | Gumroad 10 % + 0,50 $ e fa da venditore per l'IVA; Substack 10 %, ma non gestisce l'IVA; beehiiv 0 % ma piano da 49 $/mese | 2,5 | 20 / 110 / 360 | 6-10 | NO prima dei 500 iscritti (regola già scritta) |
| 9 | Widget a pagamento per aziende (calcolatore della tassa per gli host, scioperi per le agenzie) | Freemius 3,8 % + 0,50 $ (+2,3 % per WordPress), fa da venditore per l'IVA | 2,5 | 0 / 50 / 400 | 10-15 | NO a pagamento; **SÌ gratis** come leva di link (già in STRATEGIA 11.3) |
| 10 | Dataset dei rifiuti dei visti per consolato | Nessuno: la Commissione UE e il Dipartimento di Stato USA li danno gratis | 2 | 0 / 0 / 200 | 3-5 | NO: valgono come pagine citate da ChatGPT, non come merce |
| 11 | Sponsor tramite negozi di sponsor (EthicalAds, Carbon, BuySellAds, Passionfroot, articoli sponsorizzati) | EthicalAds chiede almeno 50.000 pagine viste al mese (letto); Carbon serve pubblico di sviluppatori; Passionfroot serve a chi ha newsletter e canali | 1,5 | 0 / 0 / 500 | 2-4 | NO: soglie lontane, i link venduti mettono a rischio la rete su Google |
| 12 | AWS Data Exchange, Snowflake, Datarade | Costi fissi o trattative B2B fuori piattaforma (studio 15; pagina prezzi AWS letta oggi) | 1 | 0 / 0 / 0 | – | NO, confermato |

**Somma centrale: ~4.000 €/anno**, e per l'80 % dipende dalle righe 1 e 2, cioè da due siti con 0 visite oggi. La lezione:
- **I nostri dati ufficiali valgono come pagine, non come merce.** Le fonti (MIT, Commissione UE, Dipartimento di Stato, FEMA, HUD, OMI) sono gratis per tutti, spesso già liberate da altri (onData per gli scioperi), e sui negozi di API ci sono già concorrenti con 1-4 utenti al mese.
- **Chi paga di più per visitatore sono le reti che comprano contatti negli USA**, a prezzo fisso e scritto. Lì il nostro dato (costo dell'assicurazione per zona, condominio approvato FHA) porta proprio il visitatore che vale.

**Le 2 migliori: righe 1 e 2.** Sono "pubblicità a contatto": paga una rete, nessuna vendita diretta, nessun cliente da cercare.
- Sono già decise come idea n. 29 del 17/10 (stato PASSA), ma oggi aggiungo tre programmi per la casa (Liberty Mutual, Hippo, Allstate).
- Oggi non rendono niente perché FloodCost e ApprovedCondos hanno 0 visite.
- Il lavoro vero è portare traffico a quei due siti, non costruire prodotti nuovi.

**Vincolo da allentare.**
- **Niente email a freddo:** non si allenta. Per le aziende italiane è vietato (art. 130). È anche l'unico modo per trovare clienti B2B per i dati (gestionali, agenzie), quindi le righe 3, 4 e 6 restano piccole.
- **Niente social:** nessuna prova che servano a queste vie.
- **Niente spese:** non c'è niente che valga la pena comprare. Il dominio per TollBit (10-15 €/anno) rende al massimo 300 €/anno e rischia il canale di ChatGPT, che oggi porta 62-68 visite a settimana.
- **L'unico vincolo che conviene toccare è il "quando" della consulenza fiscale.** Oggi aspetta il primo incasso (decisione del 10/10). Propongo di anticiparla adesso: è gratis e prende circa 30 minuti. I numeri:
  - Decide se le righe 1 e 2 (centrale 3.060 €, ottimista 13.900 €) entrano nei codici attuali.
  - Decide se le righe 3, 4 e 6 (centrale ~640 €) si possono pubblicare su Apify senza aprire la posizione commerciale da ~4.000 €.
  - Se la risposta per il gruppo B è "serve INPS commercianti", si chiude il gruppo B per sempre, con il motivo scritto.

---

## 1. Riga 1: contatti per assicurazione casa e alluvione USA a prezzo fisso (FloodCost), voto 5,5

**Chi paga e quanto.**
- Lemonade: 15 $ a contatto casa e affitto (Awin/Impact; letto nello studio del 17/10).
- Liberty Mutual: ~10 $ a preventivo casa completato, via CJ (uppromote e Phonexa, **non letto sulla pagina ufficiale**).
- Hippo: 25 $ a contatto, pagamento mensile, minimo 50 $ (elenco QualityUnit, **non letto**; `hippo.com/affiliates` risponde **404** dal server).
- Allstate: fino a 28 $ a preventivo casa (FlexOffers via Affilimate, **non letto**).
- Hiscox 25 $: è per le assicurazioni delle imprese, non serve a FloodCost.
- **Nessun programma trovato che paghi un preventivo solo per l'alluvione.** Neptune Flood non ha una pagina affiliati trovabile. Si usano i programmi per la casa, che nelle zone a rischio vendono anche l'alluvione privata.

**Domanda.** "flood insurance leads" compare nell'autocomplete us/en: chi compra contatti li cerca, quindi il mercato c'è. La domanda dei proprietari (costo dell'assicurazione per zona) è quella già misurata quando è nato FloodCost (`idee-mondo-2026-10-14` n. 1).

**Legale (da verificare, non è un parere).**
- La rete compra il contatto a prezzo fisso, che non dipende dalla vendita della polizza. È lo schema di tutti i siti di confronto.
- Le regole sul consenso alle telefonate (TCPA) le gestisce il modulo della rete, non il nostro. La regola FCC del "consenso uno a uno" è stata annullata da un tribunale federale d'appello a gennaio 2025: lo so dalle mie conoscenze, **non l'ho riletto oggi**.
- Noi non raccogliamo dati personali: il visitatore compila il modulo sul sito della rete.

**Fiscale.** Gruppo A. Pagamento dagli USA tramite CJ o FlexOffers con il modulo W-8BEN.

**Ore.** 4-6: riquadro "preventivo" sulle 2.920 pagine e iscrizioni di Massimiliano, 10 minuti per rete.

**Stima.**
- Per 1.000 visite: 3 % clicca il riquadro = 30 clic; il 15 % completa il preventivo = 4,5 contatti; a ~13,5 € di media (15 $) fa **~60 €**. Nel prudente uso 40 €.
- Visite al mese a 18 mesi: 400 / 2.000 / 8.000 (oggi 0).
- **Prudente** 400 × 12 × 0,04 = **190 €**. **Centrale** 2.000 × 12 × 0,06 = **1.440 €**. **Ottimista** 8.000 × 12 × 0,07 = **6.700 €**.
- **Primi soldi:** il mese dopo l'iscrizione approvata, se arrivano visite.

**Voto.** Domanda 2 + concorrenza debole 0,5 (i comparatori sono forti su Google) + fonte 2 (FEMA, dominio pubblico) + soldi per visitatore 1 (cifre non lette sulle pagine ufficiali) + rischi e ore 0 (dipende da un sito senza visite) = **5,5**.

## 2. Riga 2: contatti per mutuo FHA (ApprovedCondos), voto 5,5

**Chi paga e quanto.** LendingTree, fino a 35 $ per modulo compilato, via CJ (studio del 17/10, n. 29).

**Legale.** La regola USA sui compensi per segnalazione nei mutui (RESPA, sezione 8) colpisce chi orienta il cliente verso un prestatore. Un parere del CFPB del febbraio 2023 riguardava proprio le piattaforme di confronto. Non ho trovato oggi la conferma che sia stato ritirato: **da verificare**. Un compenso fisso da una rete, senza classifiche pagate di banche, è lo schema a basso rischio.

**Ore.** 3-4.

**Stima.**
- Per 1.000 visite: 25 clic; il 12 % compila = 3 moduli; a ~30 € fa **90 €**. Nel prudente uso 60 €.
- Visite al mese a 18 mesi: 300 / 1.500 / 6.000 (oggi 0).
- **Prudente** 300 × 12 × 0,06 = **220 €**. **Centrale** 1.500 × 12 × 0,09 = **1.620 €**. **Ottimista** 6.000 × 12 × 0,10 = **7.200 €**.

**Voto.** **5,5**, con lo stesso conto della riga 1.

## 3. Riga 3: API delle tasse di soggiorno, voto 4,5

**Domanda.** Autocomplete gb/en "city tax api" → **"tourist tax api"** tra i suggerimenti: è l'unico segnale B2B trovato oggi. Invece "tourist tax plugin" (us), "imposta di soggiorno plugin" e "imposta di soggiorno calcolo automatico" (it) non danno nessun suggerimento.

**Chi compra.**
- Gestionali per affitti brevi e piccoli sviluppatori.
- Il concorrente vero è Trippz: "Tax Content API" aggiornata ogni mese e "Location Tax API" aggiornata ogni giorno, prezzo non pubblico (scheda su softwareadvice).
- Altri: Holidu per la Francia; PayTourist, solo per l'Italia, integrato nei gestionali (Smartness).
- I grandi comprano con un contratto e un livello di servizio garantito, cioè con vendita diretta. Su un negozio di API arrivano solo i piccoli.

**Negozi.**
- Apify: "tourist tax" dà 36 risultati, **nessuno sulle tasse di soggiorno**.
- Zyla API Hub: nessun costo di caricamento, **80 % al fornitore** (centro assistenza Zyla via ricerca; la pagina risponde 525 dal server). Zuplo nota che il fornitore non sceglie i prezzi.

**Licenza.** Le tariffe vengono da delibere e regolamenti comunali. Gli atti ufficiali non sono protetti dal diritto d'autore (art. 5 della legge sul diritto d'autore, mia lettura); la raccolta è nostra.

**Rischio.** Un errore di tariffa finisce nelle ricevute degli host. Servono un avviso "nessuna garanzia" e un aggiornamento al 1/1 di ogni anno.

**Fiscale.** Gruppo B.

**Stima.** Prudente 0. Centrale 2 piccoli clienti × 10 $/mese × 12 × 0,8 × 0,9 = **~170-250 €**. Ottimista: 1 gestionale piccolo a ~200 $/mese più 3 piccoli = **~2.400 €**.

**Esito.** RISERVA, dopo la domanda al CAF.

## 4. Riga 4: dataset e API delle aste con sconto sul valore OMI, voto 4

**Negozio Apify, ricerca del 31/10.**

| Actor già in vendita | Utenti in tutto | Utenti negli ultimi 30 giorni |
|---|---|---|
| "Estrai aste giudiziarie PVP: Perizie e monitor" | 29 | 4 |
| "Italy Judicial Real Estate Auctions (AsteGiudiziarie.it)" | 26 | 3 |
| "Italy AsteAnnunci Judicial Auctions Scraper" | 12 | 1 |
| **"Italy Property Auctions API: PVP Judicial Auctions in English"** | 11 | 3 |
| "Italy Auction Lots Scraper: Up to 88% Below Market Value" | 2 | 1 |

Il nostro angolo, lo sconto sul valore di mercato, **è già in vendita**. Il mercato è di pochi utenti.

**Licenze.**
- OMI: **CC BY 4.0**, riuso commerciale permesso con la citazione "Agenzia delle Entrate – OMI" (letto nel nostro `affari-test-fonti.md` sez. 2.1). Un progetto di onData su GitHub, più vecchio, scriveva invece che la licenza "non è aperta" e non diceva se l'uso commerciale fosse permesso: vale la pagina ufficiale letta da noi, ma va riletta prima di vendere.
- PVP: nessuna licenza scritta, quindi vale "aperto per legge" (art. 52 del Codice dell'amministrazione digitale), **esclusi i dati personali**.
- Alcuni PDF del Ministero portano la scritta "vietata ogni ripubblicazione o riproduzione a scopo commerciale" (ricerca del 31/10). Vendere un dataset del PVP è più esposto che pubblicare pagine con il link: solo campi strutturati, mai PDF né nomi.
- In Senato è circolato un emendamento con il titolo "Divieto di estrazione, utilizzazione e aggregazione" dei dati (non ho visto se sia diventato legge): **da verificare prima di vendere**.

**Domanda.** "dataset aste giudiziarie", "alert aste giudiziarie", "avviso nuove aste", "aste giudiziarie notifiche" (it/it): **nessun suggerimento**.

**Stima** (80 % al creatore, meno i costi delle esecuzioni).
- Prudente: 2 utenti × 3 $/mese × 12 × 0,8 × 0,9 = **~50 €**.
- Centrale: 6 × 5 $ = **~290 €**.
- Ottimista: 20 × 10 $ = **~1.700-1.900 €**.

**Esito.** RISERVA debole.

## 5. Riga 5: contatti in Italia (mutuo per l'asta, traduzioni giurate), voto 3

- **MutuiSupermarket:** il programma su affi.io paga "per ogni domanda di mutuo", non per il mutuo concesso. Vieta gli annunci sulle parole chiave. **Cifra non pubblica.**
- **MutuiOnline:** nessuna pagina affiliati trovata.
- **Traduzioni giurate:** già chiuse il 26/10 (ESPLORATE: "servizi locali ed enti senza affiliazione").
- **Nodo legale:** la mediazione creditizia è un'attività riservata in Italia (TUB e OAM). Un editore pagato a contatto da una rete è "pubblicità" o "segnalazione"? **Da chiedere**, non da presumere.
- **Traffico:** Aste in Chiaro fa 3-5 visite a settimana.
- **Stima:** 0 / 150 / 900 €.
- **Esito:** NO finché non c'è una cifra scritta.

## 6. Riga 6: API degli scioperi italiani, voto 3

Novità rispetto allo studio 13:
- Autocomplete us/en "italy strike api" e it/it "scioperi api": **nessun suggerimento**.
- Modulo "business" del sito: 0 richieste in 3 settimane.
- Le piattaforme di rischio di viaggio (Datasurfr di MitKat, Riskline, Crisis24) coprono già l'Italia.
- Su Apify non c'è nessun Actor sugli scioperi italiani: l'unica "lacuna" vera, ma senza domanda.
- Il registro del MIT è chiuso agli indirizzi esteri dal 23/10 (cruscotto): un Actor dovrebbe passare dalla Commissione di garanzia.

**Stima:** 0 / 100 / 600 €. **Esito:** test passivo come già deciso, nessun lavoro in più.

## 7. Riga 7: pagamento dai robot delle IA, voto 2,5

**TollBit.**
- Gratis per gli editori; i robot vengono mandati a un sottodominio con il "paywall" e l'editore fissa il prezzo.
- Pagina FAQ letta (200). Le integrazioni elencate sono Cloudflare, Fastly, Akamai, AWS CloudFront, Azure, **Vercel**, WordPress VIP e Imperva: **Netlify non c'è**.
- Digiday: circa il 20 % dei ~7.000 siti ha incassato qualcosa, da centinaia a decine di migliaia di dollari al mese. Sono i grandi giornali.

**Cloudflare Pay per crawl.** Pagina ufficiale aggiornata al 28/7/2026: "currently in **closed beta**". Serve anche un dominio proprio sotto Cloudflare.

**Il rischio vero.**
- ChatGPT ci manda 62-68 visite a settimana citando le nostre tabelle: oggi è il secondo canale della rete.
- Far pagare il robot che cerca per ChatGPT può spegnere le citazioni.
- Far pagare solo i robot che raccolgono dati per l'addestramento non porta visite e, a questi volumi, porta pochi centesimi.

**Stima:** 0 / 30 / 300 €. Serve una spesa (dominio) e il trasloco di almeno un sito.

**Esito.** NO. Si rilegge solo se Netlify entra tra le integrazioni o se un sito supera 50.000 visite al mese.

## 8. Riga 8: avvisi a pagamento su piattaforme self-service, voto 2,5

**Piattaforme.**
- Gumroad: 10 % + 0,50 $; dal 2025 fa da venditore per l'IVA (studio 15).
- Substack: 10 % più Stripe; più fonti concordano che **non** fa da venditore e che l'IVA resta a carico dell'autore (la pagina di supporto risponde 403 dal server).
- beehiiv: 0 % sugli abbonamenti, ma solo dal piano Lite da **49 $/mese** (pagina prezzi letta): costo fisso, viola la regola 1.
- Nessuna di queste porta clienti nuovi: la lista va portata da noi.

**Dove avremmo una lista.**
- EsameB1: 11 iscritti veri al 28/10.
- Italy Strikes: 0 iscritti.
- Aste: nessuna domanda di avvisi su Google ("alert aste giudiziarie" e simili: nessun suggerimento). I portali autorizzati, come astegiudiziaria.com, danno già avvisi gratis.

**Stima (EsameB1).** Lista a 18 mesi di 300 / 1.000 / 1.500 iscritti, convertiti tra lo 0,62 % (mediana beehiiv, Press Gazette 2026) e il 2 %, a 12 €/anno: **~20 / 110 / 360 €**.

**Esito.** NO prima dei 500 iscritti (regola già in STRATEGIA). Sotto quella soglia la lista rende di più gratis (studio 13 sez. 2.4).

## 9. Riga 9: widget a pagamento per aziende, voto 2,5

- **Freemius:** fa da venditore per l'IVA; 3,8 % + 0,50 $ più le spese del circuito, +2,3 % per i plugin WordPress; nessun costo fisso (pagina prezzi letta).
- **Domanda:** nessun suggerimento per "tourist tax plugin", "imposta di soggiorno plugin" e "imposta di soggiorno calcolo automatico".
- **Concorrenza:** i gestionali italiani, per esempio quelli integrati con PayTourist, la tassa la calcolano già.
- **Stima:** 0 / 50 / 400 €.
- **Esito:** NO a pagamento. Il widget **gratuito** con il link di ritorno resta nel piano (STRATEGIA 11.3), come leva di traffico.

## 10. Riga 10: dataset dei rifiuti dei visti, voto 2

- **Domanda:** "schengen visa statistics" ha 10 suggerimenti (2024, 2025, 2026, per Paese, India, Türkiye). Sono lettori e giornalisti, non compratori.
- **Fonti gratuite:** la Commissione UE pubblica i dati con riuso commerciale permesso citando la fonte (decisione 2011/833/UE, mia conoscenza, non riletta oggi); il Dipartimento di Stato USA è di dominio pubblico.
- **Valore:** non c'è niente da vendere che il compratore non abbia gratis. Il valore è nelle pagine che ChatGPT cita.
- **Stima:** 0 / 0 / 200 €.

## 11. Riga 11: sponsor tramite negozi di sponsor, voto 1,5

- **EthicalAds** (FAQ letta, 200): "Your site needs at least **50,000 pageviews per month**"; di solito circa 2,50 $ ogni 1.000 pagine viste; pubblico di sviluppatori.
- **Carbon Ads** (pagina letta): reti di siti per sviluppatori; per gli inserzionisti "The minimum is **$5,000 a month**".
- **BuySellAds:** pagina editori letta (200), senza soglia scritta; fonti di terzi parlano di circa 100.000 pagine viste raccomandate e di iscrizione su candidatura.
- **Passionfroot** (pagina prezzi letta): gratis, 15 % sugli sponsor portati dalla sua rete. È fatto per chi ha newsletter, YouTube, LinkedIn o podcast, cioè canali che non abbiamo (niente social).
- **Negozi di articoli sponsorizzati** (Collaborator.pro e simili): nessuna soglia trovata. Le regole antispam di Google vogliono quei link marcati `rel="sponsored"` e prevedono azioni manuali contro chi vende link: rischio su tutta la rete. **Escluso.**
- **La nostra rete:** ~1.300 visite al mese, 40 volte sotto la soglia più bassa.
- **Stima:** 0 / 0 / 500 €.

## 12. Riga 12: AWS Data Exchange, Snowflake, Datarade, voto 1

Studio 15 confermato. Pagina prezzi AWS Data Exchange (letta, 200): costi di archiviazione dei file, "tiered fulfillment fees" sulle vendite e un account AWS con carta. Datarade: pagina prezzi **403** dal server; lo studio 15 aveva letto il piano gratuito al 30 % di commissione con le trattative fuori piattaforma. Nessun cliente arriva da solo a un fornitore sconosciuto. **NO.**

---

## 13. Cosa fare adesso (in ordine)

1. **Nessun lavoro nuovo di costruzione per questo fronte.** Il guadagno atteso per ora è più alto spingendo il traffico di FloodCost e ApprovedCondos (righe 1 e 2), che oggi hanno 0 visite: è un tema per la revisione del mercoledì, non per questo file.
2. **Proposta a Massimiliano, a costo zero:** anticipare adesso la domanda fiscale gratuita (CAF o servizio online) invece di aspettare il primo incasso. Due domande sì/no:
   - (a) "Compensi fissi per contatto da reti americane (CJ, FlexOffers) per pubblicità sul mio sito: rientrano nei miei codici attuali o serve aggiungerne uno?"
   - (b) "Vendita di dati via Apify, con fatture emesse dalla piattaforma a mio nome: serve la posizione commerciale INPS?"
3. **Iscrizioni** (10 minuti l'una, quando Massimiliano vuole, dopo i libri da 9): CJ (LendingTree, Liberty Mutual), FlexOffers (Allstate). Hippo solo se si trova la pagina ufficiale del programma.
4. **Gruppo B** (righe 3, 4, 6): si pubblica su Apify o Zyla solo se la risposta (b) è "no, basta il codice". Altrimenti resta chiuso.
5. **Righe 7-12:** chiuse con le prove sopra. Da scrivere in ESPLORATE alla prossima revisione (questo file non tocca altri file).

## 14. Fonti lette il 31/10/2026

**Pagine ufficiali (curl):**

| Pagina | Codice | Cosa dice |
|---|---|---|
| ethicalads.io/publishers/faq/ | 200 | minimo 50.000 pagine viste, ~2,50 $ ogni 1.000 |
| carbonads.net | 200 | minimo 5.000 $/mese per gli inserzionisti |
| buysellads.com/publishers | 200 | nessuna soglia scritta |
| help.passionfroot.me, articolo 11552638 | 200 | gratis, 15 % sulla rete, 5 % al partner |
| docs.tollbit.com/faq | 200 | elenco delle integrazioni, senza Netlify |
| developers.cloudflare.com, AI Crawl Control / Pay per crawl | 200 | "closed beta", aggiornata al 28/7/2026 |
| aws.amazon.com/data-exchange/pricing | 200 | archiviazione e "tiered fulfillment fees" |
| freemius.com/pricing | 200 | 3,8 % + 0,50 $, +2,3 % per WordPress, fa da venditore per l'IVA |
| beehiiv.com/pricing | 200 | abbonamenti a pagamento dal piano da 49 $/mese |

**Non leggibili dal server:** datarade.ai/pricing (403), support.substack.com (403), help.zylalabs.com (525), hippo.com/affiliates (404), lemonade.com/affiliates (404).

**API Apify** (`api.apify.com/v2/store?search=`): "tourist tax", "visa requirements", "strike", "auction italy", "aste", "flood insurance", "fha".

**Autocomplete:** us/en, gb/en, it/it; 15 interrogazioni (elenco nelle sezioni sopra).

**Ricerca web** (cifre di terzi, **non lette sulle pagine ufficiali**):
- programmi casa: Liberty Mutual ~10 $ (uppromote, Phonexa), Hippo 25 $ (QualityUnit), Allstate fino a 28 $ (Affilimate);
- MutuiSupermarket (affi.io); Zyla 80/20 (centro assistenza Zyla, Zuplo); Trippz (softwareadvice);
- TollBit su Digiday (~7.000 siti, ~20 % paganti);
- licenza OMI (GitHub di onData); avviso "vietata riproduzione a scopo commerciale" (documento del Ministero della Giustizia);
- parere CFPB 2023 (ALTA, Foley); regole antispam di Google sui link pagati (fonti di terzi);
- Substack 10 % e IVA a carico dell'autore (più fonti di terzi); Press Gazette (beehiiv 0,62 %).

**Dal repository:** `CRUSCOTTO-RETE.md` (visite, iscritti, provenienze), `affari-test-fonti.md` (licenze OMI e PVP), studi 7, 13 e 15, `idee-grandi-2026-10-17.md`.
