# Salute amministrativa: visite mediche per i visti, farmaci che chiedono un permesso, tessera europea, vaccini d'ingresso, assicurazioni obbligatorie (31/10/2026)

Angolo assegnato: settore salute amministrativa (non consigli medici). Assicurazione sanitaria per stranieri e studenti per Paese (iscrizioni, costi ufficiali), tessera europea e GHIC, farmaci che richiedono un permesso per viaggiare (liste ufficiali per Paese), vaccinazioni obbligatorie per l'ingresso (liste ufficiali OMS/CDC). Attenzione ai rischi.

Prima di partire ho letto il metodo e l'asticella (`.claude/skills/rete-siti/SKILL.md`), le regole del 30-31/10 (`REGOLE-FISSE.md`: fronti nuovi, conta il fatturato, niente lavori a ore di Massimiliano) e `ESPLORATE.md`. Molti temi dell'angolo erano già chiusi e **non li ho ripetuti**:
- GHIC Paese per Paese dal Regno Unito: SEZIONE in coda di Before You Fly (idee-2026-10-31-soldi);
- certificato della febbre gialla: voto 7 condizionato al sì sul tema sanitario (ricerca-zona-latam-africa-2026-10-30);
- OSHC, IHS e condizione 8501: NO (idee-2026-10-23, ricerca-numeri-ufficiali-2026-10-30);
- assicurazione sanitaria per i visti di residenza: NO, nessun programma pubblica la commissione (26/10 e 30/10);
- assicurazione per il visto Schengen: RISERVA (26/10 e 31/10);
- iscrizione alla sanità pubblica per espatriati (convenio especial, SSN volontario, IMSS): NO (30/10);
- casse malati tedesche e premi svizzeri: NO il 17/10 e il 30/10, e oggi coperte dal ricercatore Germania-Austria-Svizzera (`wf-2026-10-31-germania-austria-svizzera.md`);
- "can I bring food/medication into…": NO il 17/10, ma solo con l'autocomplete generica (dominata da stadi e parchi). Oggi l'ho **riaperta con un fatto nuovo**: le ricerche "farmaco × Paese" sono piene e precise (sez. 2), e il Giappone pubblica la lista dei farmaci controllati con licenza di riuso.
- Il test TB per il visto britannico è stato valutato oggi anche nel rapporto `wf-2026-10-31-africa-diaspora.md` (riquadro in coda bassa, 5,5). Qui lo allargo a tutti i 63 Paesi, alle città e alle altre visite mediche per i visti, con prove nuove (sez. 1).

Prove raccolte il 31/10/2026: `curl` dal nostro server (stato HTTP, formato, data, licenza), API di contenuto di GOV.UK, Google Autocomplete con Paese e lingua giusti (client firefox; il numero è quante varianti propone, massimo 10), ricerche web per vedere chi c'è oggi in prima pagina. Nessun blocco anti-robot è stato aggirato: le fonti chiuse sono scritte come chiuse.

## In breve

- **Nessuna idea passa l'asticella dei siti nuovi** (voto ≥ 7 e ≥ 5.000 €/anno centrali). La migliore arriva a 6 e a circa 300 €/anno nella stima centrale.
- **Il buco più grande dell'angolo sono le visite mediche obbligatorie per i visti, città per città** ("tb test for uk visa in lahore / hyderabad / lagos", "price in pakistan / nigeria / ghana", "canada medical test fee in pakistan", "gamca medical fees 2026"). La fonte britannica è perfetta: API GOV.UK, licenza OGL, **63 pagine Paese con cliniche, città e tariffe** (es. Pakistan: Islamabad, Lahore, Karachi, Mirpur, 14.000-15.000 rupie per gli adulti; Nigeria: Abuja, Benin City, Lagos, 94 $ o 120.000 naira), aggiornate dal 2023 al 2026. È il modello di EsameB1 (passaggio obbligatorio, città, costo) con il pubblico che oggi arriva a Visa Income da ChatGPT (Pakistan, Nigeria). Il limite è il pagatore: pubblico con pubblicità da 1 € ogni 1.000 pagine e nessuna affiliazione naturale, se non Wise.
- **Farmaci che chiedono un permesso:** domanda enorme e precisa per farmaco e Paese ("can i bring adderall/vyvanse/codeine to japan/italy/greece/turkey/dubai"), il Giappone pubblica la lista ufficiale sotto licenza di riuso (PDL 1.0), ma due siti automatici fanno già la tabella farmaco × Paese (goodsacrossborders.com, canibringto.com) e un errore può costare un arresto. Voto 5, solo con il sì di Massimiliano al tema.
- **Tessera europea per i cittadini UE in italiano, tedesco, francese e spagnolo:** la Commissione pubblica le regole e i costi Paese per Paese (32 pagine, 200, riuso libero); in italiano Google ha solo blog. È la gemella della sezione GHIC già in coda, ma con pubblicità da 2-4 € e nessuna commissione scritta. Il Ministero della Salute italiano è dietro un controllo anti-robot (Gcore): non si legge e non si aggira.
- **Lezione del giro:** nella salute amministrativa la domanda c'è sempre, le fonti pubbliche spesso sì, ma **chi paga manca**. Gli assicuratori sanitari e di viaggio non pubblicano le commissioni (Heymondo, ISO, IMG, Insubuy: pagine senza cifre, 403 o 404), e i pubblici con più domanda (chi chiede un visto da Pakistan, India, Nigeria) valgono poco in pubblicità. L'unico pagatore scritto e adatto resta Staysure (5 %, viaggiatori con malattie preesistenti), già nel piano della GHIC.
- **Prossimo angolo consigliato:** non insistere sulla salute. Meglio un angolo dove il pagatore è scritto prima della fonte: per esempio "chi trasferisce soldi per pagare un passaggio obbligatorio" (tasse universitarie, depositi, visti) con Wise e Remitly come pagatori, oppure i viaggiatori con malattie preesistenti dal Regno Unito (Staysure 5 %, InsureandGo 12 %) su temi non medici (destinazioni, compagnie, regole di bagaglio per apparecchi medici).

## Tabella delle idee

| # | Idea | Dove | Voto | €/anno a 18 mesi (prud. / centr. / ott.) | Ore | Esito |
|---|---|---|---|---|---|---|
| 1 | Visite mediche obbligatorie per i visti, città per città: test TB per il Regno Unito (63 Paesi, cliniche, tariffe, orari), poi Canada (medici del panel) quando la fonte risponde | sezione di Visa Income Checker | 6 | 40 / 300 / 1.500 | 10-14 | **SEZIONE in coda bassa** (costo zero, guadagno positivo); unisce il riquadro 5,5 del rapporto Africa-diaspora |
| 2 | Farmaci che chiedono un permesso, farmaco per farmaco e Paese per Paese (Giappone, Emirati, Singapore, Grecia, Turchia, Arabia Saudita, Schengen) | sezione di Before You Fly | 5 | 100 / 440 / 1.700 | 20-30 | RISERVA: solo con il sì di Massimiliano al tema sanitario e con revisione dei fatti più severa |
| 3 | Tessera europea (TEAM/EHIC/CEAM) Paese per Paese per i cittadini UE, in italiano, tedesco, francese, spagnolo: cosa è gratis, cosa si paga | Before You Fly, accanto alla sezione GHIC | 5,5 | 10 / 60 / 600 | 8-12 | RISERVA: si fa insieme alla GHIC solo se la GHIC mostra visite; fronte "lingue" |
| 4 | Vaccinazioni obbligatorie diverse dalla febbre gialla: meningite ACWY per Hajj e Umrah, polio per chi parte da Pakistan e Afghanistan | pagina di Before You Fly, accanto alla febbre gialla | 4 | 10 / 70 / 250 | 4-6 | RISERVA debole, legata al sì sul tema sanitario della febbre gialla |
| 5 | Assicurazione sanitaria obbligatoria per la working holiday, destinazione per destinazione (SafetyWing già approvato) | Visa Income Checker | 4,5 | 20 / 150 / 700 | 6-8 | RISERVA debole: Canada, Giappone e Nuova Zelanda chiusi dal server; pvtistes e hellosafe già primi |
| 6 | Assicurazione sanitaria universitaria per studenti stranieri negli USA (costo del piano dell'università, regole e scadenze del "waiver") | – | 3,5 | – | – | NO: nessuna fonte centrale, nessun pagatore verificato |
| 7 | Visite mediche per i visti del Golfo (GAMCA/Wafid) e certificato di idoneità degli Emirati | – | 3,5 | – | – | NO: tariffe solo dentro lo script di Wafid, Emirati chiusi o non letti, Google pieno |

Ipotesi comuni per i calcoli (le stesse dei giri precedenti, non ancora misurate perché AdSense non è aperto): pagine viste per visita 1,3-1,4; pubblicità ogni 1.000 pagine viste: pubblico Pakistan/India/Nigeria **0,8-1,5 €**, Italia/Germania/Francia **2-4 €**, Regno Unito/USA **8-12 €**. Wise paga "da 10 £" a cliente nuovo (pagina letta il 17/10, rete Partnerize) = circa 11,5 €. Staysure paga "5%+" del premio (pagina letta il 31/10 nel rapporto `idee-2026-10-31-soldi.md`); premio medio ipotizzato 60 £, cioè circa 3,5 € a polizza. Le visite sono stime a 18 mesi, non dati. Per confronto, i numeri veri della rete: Visa Income 55-62 visite a settimana, più della metà da ChatGPT, sulle pagine Pakistan e Nigeria dei rifiuti dei visti (CRUSCOTTO, 19-27/10).

---

## 1. Visite mediche obbligatorie per i visti, città per città (voto 6, SEZIONE in coda bassa)

**Cosa.** In Visa Income Checker, una pagina per Paese e una per città: "TB test for UK visa in Lahore: 2 approved clinics, 14,000-15,000 PKR for adults, 10,000-11,000 PKR under 11, opening days, what to bring, certificate valid 6 months", con la data dell'ultimo aggiornamento ufficiale e il cambio in sterline. In più: chi deve fare il test (soggiorno di 6 mesi o più, aver vissuto in un Paese della lista), Paesi senza clinica (Benin, Burkina Faso, Ciad: test in un altro Paese), storico delle tariffe (le cambiamo noi a ogni aggiornamento della pagina GOV.UK). Si pubblicano solo città, nome della clinica, tariffe e orari: **niente email né telefoni** (si rimanda alla pagina ufficiale).

**Fonte ufficiale (curl).**
- `gov.uk/api/content/tb-test-visa` **200**, JSON, licenza OGL: guida "Tuberculosis tests for visa applicants" con la lista dei Paesi e **72 collegamenti** alle pagine Paese.
- Scaricate le 72 pubblicazioni e le **63 pagine di dettaglio** (`/government/publications/…/tuberculosis-testing-in-…`): **63 su 63 hanno le tariffe**; circa **111 cliniche** (righe "Telephone"); data dell'ultima modifica: 17 pagine nel 2026, 11 nel 2025, 20 nel 2024, 15 nel 2023.
- Pakistan (aggiornata 20/2/2026), letto: Islamabad AMC "Below 11 years PKR 11,000 / 11 years and above PKR 15,000"; IOM Islamabad e Lahore "PKR 10,000 / PKR 14,000"; Karachi e Mirpur IOM.
- Nigeria (aggiornata 13/5/2026), letto: IOM Abuja, Benin City, Lagos "94 USD / 49 USD, reprint 16 USD", pagamento in naira al cambio ONU; altre cliniche "N120,000 / N60,000".
- India: pagina 200 (aggiornata 20/4/2026), Hyderabad Sanjiwani "INR 2,000 / 2,200" (dalla ricerca web sulla pagina ufficiale).
- Il servizio `govdiff.njk.onl` (200) conserva le versioni precedenti di ogni pagina GOV.UK: da lì si ricostruisce lo storico delle tariffe.
- Altri Paesi: Canada, lista dei medici del panel `secure.cic.gc.ca/pp-md/pp-list.aspx` **200 una volta (29 kB), poi connessione interrotta due volte**: instabile, da riprovare da GitHub Actions. USA `travel.state.gov` **403**. Australia e Nuova Zelanda: pagine dei medici del panel non trovate (404) e, secondo il rapporto Canada-Australia-NZ di oggi, `immigration.govt.nz` è dietro Incapsula. Golfo: vedi idea 7.

**Domanda (autocomplete).**
- gb/en "tb test for uk visa" **10**: "in hyderabad", "in pakistan", "in ghana", "in chennai", "in nigeria", "in bangalore", "price", "near me".
- gb/en "tb test for uk visa cost" **10**: "fees zimbabwe", "fees in nigeria", "price in pakistan", "price in ghana", "fees in uae", "in kenya cost", "cost … in bangladesh", "price south africa".
- pk/en "tb test for uk visa" **10** ("in lahore", "in islamabad", "karachi", "mirpur", "price in pakistan", "appointment"); pk/en "uk tb test" **10** ("online appointment islamabad / lahore / mirpur", "center lahore").
- ng/en "uk tb test" **10** ("centres in nigeria", "centres in lagos", "fee in nigeria", "booking"); in/en "uk tb test" **10** (hyderabad, bangalore, chennai, delhi, mumbai).
- gb/en "iom tb test" **10** ("fee", "booking lagos price", "booking harare", "online booking nigeria price").
- Fratelli con la stessa forma: "canada medical test fee in pakistan", "medical examination for canada visa in kenya / nigeria / ghana / ethiopia / karachi" (10), "australia visa medical test hyderabad / centres in india" (10), "us immigration medical exam cost in india / pakistan" (10).

**Chi c'è su Google.** La pagina GOV.UK del Paese (una sola per Paese, con tutte le città insieme), copie storiche su govdiff, blog di agenzie e studi legali (whytecroftford, ayjsolicitors, hotcoursesabroad), una "city guide" indiana con cifre senza fonte (immigrationstartguide.com), siti automatici di viaggio (mytravelready.ai). Per "tb test for uk visa price in pakistan" la ricerca web **non trova la cifra 2026** nei risultati: le tariffe ci sono solo dentro la pagina ufficiale. Battibile sulle ricerche per città e sul prezzo, e soprattutto negli assistenti AI (domanda precisa, risposta numerica ufficiale con data).

**Chi paga e quanto.** Pubblicità con pubblico di chi chiede il visto da Pakistan, India, Nigeria, Ghana, Bangladesh: 0,8-1,5 € ogni 1.000 pagine (ipotesi). **Wise** (Partnerize, "CPA rates start at £10", già usato in Visa Income) per chi deve pagare in sterline tasse universitarie, depositi e affitto: aggancio vero ma non immediato (chi fa il test TB sta per partire, il momento dei pagamenti è vicino). Nessun programma di cliniche o di assicurazioni adatto.

**Stima a 18 mesi (€/anno).**
- Prudente: 3.000 visite × 1,3 × 0,8 / 1.000 = 3 € di pubblicità; Wise 3.000 × 0,1 % = 3 clienti × 11,5 = 35 € → **circa 40 €**.
- Centrale: 12.000 visite × 1,3 × 1,2 / 1.000 = 19 €; Wise 12.000 × 0,2 % = 24 × 11,5 = 276 € → **circa 300 €**.
- Ottimista (con Canada e citazioni AI come oggi per i rifiuti dei visti): 40.000 × 1,4 × 1,5 / 1.000 = 84 €; Wise 40.000 × 0,3 % = 120 × 11,5 = 1.380 € → **circa 1.500 €**.
- Primi soldi: Wise subito dopo la pubblicazione (link già attivo nella rete); pubblicità solo con AdSense aperto. Domanda costante tutto l'anno, con picchi prima di settembre e gennaio (ingressi universitari).

**Ore.** 10-14: lettura delle 63 pagine dall'API (struttura testuale abbastanza regolare: città, "Test fees", fasce d'età), pagine Paese e città, controllo mensile del campo `public_updated_at` da parte degli agenti, nessuna pubblicazione se nulla cambia (regola dei crediti).

**Rischi.** Le tariffe cambiano senza preavviso (la pagina ufficiale resta il riferimento, con la data in vista); alcune pagine hanno il testo in tabelle diverse; tema medico solo di nome (è un requisito amministrativo, non un consiglio sanitario).

**Voto 6.** Fonte perfetta e aperta, domanda per città fortissima, pubblico che la rete già riceve da ChatGPT. Ma il valore per visita è il più basso possibile e Wise è un aggancio debole. Come sezione a costo zero ha guadagno atteso positivo: **entra nella coda bassa al posto del riquadro 5,5 del rapporto Africa-diaspora** (stessa cosa, più ampia).

---

## 2. Farmaci che chiedono un permesso, farmaco per farmaco e Paese per Paese (voto 5, RISERVA)

**Cosa.** In Before You Fly, una pagina per Paese di destinazione e per principio attivo dei farmaci più cercati (amfetamine e lisdexamfetamina per l'ADHD, metilfenidato, codeina, tramadolo, pseudoefedrina, benzodiazepine, oppioidi): vietato, permesso con certificato del medico, permesso con autorizzazione preventiva, quantità massima, il modulo e l'ufficio da contattare. Più il "certificato Schengen" (articolo 75) per chi viaggia nell'area Schengen.

**Fonte ufficiale (curl).**
- **Giappone**, Ministero della Salute, Dipartimento di controllo dei narcotici: `ncd.mhlw.go.jp/en/application2.html` **200** (procedure di importazione dei farmaci controllati portati a mano, aggiornate "Dec. 12, 2024"; letto: oltre un mese di scorta serve il permesso, i farmaci vanno portati di persona); lista PDF `dl_data/keitai/cotrolled_substances_list20241212 .pdf` **200**, 350 kB. Licenza: la pagina del Ministero sul diritto d'autore (`mhlw.go.jp/chosakuken/`, 200) dice che i contenuti si usano secondo il **"Public Data License 1.0"** (compatibile con CC BY 4.0). Vecchi indirizzi inglesi del Ministero e dell'ufficio regionale Kanto-Shinetsu: **404**.
- **INCB** (ONU), pagina "Country regulations" **200**: **96 Paesi con un PDF in inglese**, ma vecchi: 2007 (2), 2013 (11), 2014 (23), 2016 (10), 2017 (6), 2019-2021 (2), 2024 (30), 2025 (9), 2026 (3). Giappone 2014, USA 2014, Turchia 2017, Messico 2016; mancano Emirati, Singapore, Indonesia, Grecia, Corea, Cina, Regno Unito, India, Spagna; 93 righe "Information not yet provided". Pagine dei termini d'uso: 404 (licenza non letta).
- **Consigli di viaggio britannici** (API GOV.UK, OGL, 225 Paesi scaricati oggi): solo **21 Paesi** hanno una regola specifica sui farmaci oltre la frase standard (Colombia, Egitto, Georgia, Grecia, Italia, Giappone, Maldive, Montenegro, Nuova Zelanda, Oman, Qatar, Russia, Arabia Saudita, Singapore, Santa Lucia, Gambia, Turchia, Turkmenistan, Emirati, Uzbekistan, Vietnam). Esempio Emirati (aggiornato 27/10/2026): "up to 3 months' supply… reduced to one month's supply if the medication is included in the list requiring approval", richiesta online al Ministero della Salute.
- Chiuse o mute dal server: Ministero della Salute degli Emirati `mohap.gov.ae` **000**; Singapore HSA **404** sui vecchi indirizzi; Australia TGA **000**, ABF **404**; Canada **000**; USA CBP **403**; CDC "travel abroad with medicine" **200** (regole generali, non per Paese).

**Domanda (autocomplete us/en, sempre 10).** "can i bring adderall to japan" (ritalin, prescription, xr, "if i have a prescription"); "adderall japan" (arrested, customs, tourist, illegal); "yakkan shoumei" (form, application, list, pdf); "can i bring vyvanse to" → japan, italy, spain, mexico, china, south korea, france, canada, europe; "can i take codeine to" → turkey, greece, spain, japan, egypt, bali, usa, thailand, france, singapore; "can you bring adderall to" → japan, italy, mexico, china, the uk, thailand, spain, canada, france, korea; "bringing medication into dubai" (from uk, adhd, hiv); "controlled medication uae" (list, platform, abu dhabi); "travelling with adhd medication" (usa, uk, australia, europe, thailand, singapore, france, germany); gb/en "schengen certificate medication" 10 (pdf, english, uk, germany, australia, italy, form, france).

**Chi c'è su Google.** Per "can i bring adderall to japan": flyertalk, un podcast, miusa.org, japan-documented, **pillpassport.vercel.app**, **goodsacrossborders.com** (pagina farmaco × Paese, anche in versione stampabile), **canibringto.com** (guida 2026 e pagine in giapponese), mileasia, Reddit. Per Vyvanse in Italia: forum di Rick Steves, Reddit, goodsacrossborders (Germania, Francia, USA). La tabella farmaco × Paese **esiste già** in due siti automatici, gli stessi visti il 22/10 per le sigarette elettroniche.

**Chi paga e quanto.** Pubblicità con pubblico USA e Regno Unito (8-12 €, ipotesi; Google limita la pubblicità sui farmaci da prescrizione, ma la pagina è informativa). Affiliazione adatta: **Staysure** (5 %, specialista di chi viaggia con malattie preesistenti), circa 3,5 € a polizza. Nessun altro pagatore verificato.

**Stima a 18 mesi (€/anno).**
- Prudente: 6.000 × 1,3 × 8 / 1.000 = 62 €; Staysure 6.000 × 0,2 % = 12 × 3,5 = 42 € → **circa 100 €**.
- Centrale: 18.000 × 1,4 × 10 / 1.000 = 252 €; Staysure 18.000 × 0,3 % = 54 × 3,5 = 189 € → **circa 440 €**.
- Ottimista: 50.000 × 1,4 × 12 / 1.000 = 840 €; Staysure 50.000 × 0,5 % = 250 × 3,5 = 875 € → **circa 1.700 €**.
- Primi soldi: 3-4 mesi dopo la pubblicazione, e solo dopo l'iscrizione a Tradedoubler (già prevista per la GHIC).

**Ore.** 20-30: lista giapponese da PDF, 96 schede INCB (da leggere a mano, molte vecchie), 21 Paesi dai consigli britannici, una matrice di 8-10 principi attivi, revisione dei fatti farmaco per farmaco.

**Rischi (alti).** Un'informazione sbagliata può portare a confisca, arresto o espulsione (Giappone, Emirati); le liste nazionali cambiano e le fonti di molti Paesi sono chiuse o vecchie di 10 anni; Google tratta il tema come YMYL; è vicino alla regola "medicina esclusa" del 9/10. Se si fa: solo Paesi con fonte ufficiale letta e datata, frase "verifica con l'ambasciata" in alto, nessun consiglio su cosa prendere.

**Voto 5.** Domanda tra le più grandi viste nell'angolo e una fonte giapponese con licenza vera, ma i concorrenti automatici ci sono già, le fonti degli altri Paesi sono chiuse o vecchie e il rischio di danno è il più alto della rete. RISERVA, decide Massimiliano sul tema.

---

## 3. Tessera europea Paese per Paese per i cittadini UE, in quattro lingue (voto 5,5, RISERVA)

**Cosa.** La gemella della sezione GHIC già in coda (che parla ai britannici): per un italiano, tedesco, francese o spagnolo che va in un altro Paese UE, in Svizzera, Norvegia, Islanda, Liechtenstein o nel Regno Unito, cosa è gratis con la tessera (medico, ospedale, dentista, farmaci), cosa si paga e quanto, dove andare (solo strutture pubbliche), più l'elenco dei Paesi dove la tessera **non** vale (Turchia, Marocco, Egitto, USA, Thailandia…) con il rimando all'assicurazione di viaggio.

**Fonte ufficiale (curl).** Commissione europea, "How to use the card": `ec.europa.eu/social/main.jsp?catId=1021` **200**, con **32 pagine Paese** (27 UE + Islanda, Liechtenstein, Norvegia, Svizzera, Regno Unito), es. `…/how-use-card/spain-european-health-insurance-card_en` **200**: numeri d'emergenza, "Doctors: State-provided healthcare is free of charge", dentisti, ospedale, farmaci, rimborsi. Le versioni `_it` e `_de` restituiscono la stessa pagina in inglese (traduzione da fare noi). Riuso: politica di riuso dei documenti della Commissione (decisione 2011/833/UE, CC BY 4.0), da citare con fonte. **Ministero della Salute italiano** (`salute.gov.it`, pagine "assistenza sanitaria all'estero" e Paesi in convenzione): **200 ma è una pagina di controllo anti-robot Gcore** di 12 kB, non il contenuto. Non si aggira: le convenzioni bilaterali dell'Italia (Paesi extra-UE) restano non verificate.

**Domanda (autocomplete).** it/it "tessera sanitaria valida in" **10** (europa, svizzera, uk, romania, germania, francia, norvegia, **turchia**, spagna, **marocco**); "tessera sanitaria europea" 10 (cosa copre, spagna, come richiederla); "assistenza sanitaria all'estero" 10 (per turismo, modello S1, E111). de/de "ehic gültig" 5 (länder, großbritannien); "europäische krankenversicherungskarte" 10 (soprattutto per cassa: aok, tk, barmer: ricerca di navigazione). fr/fr "carte européenne d'assurance maladie" 10 (validité, **pays**, angleterre). es/es "tarjeta sanitaria europea" 10 (quasi tutto "solicitar"/"renovar": navigazione). nl/nl "ehic" 10 (per cassa). La parte con più "Paese" dentro è l'italiana.

**Chi c'è su Google.** In italiano, per "tessera sanitaria europea valida in Turchia, Marocco, Svizzera": helloroam (venditore di eSIM), un blog di viaggio, Adiconsum (PDF), lentepubblica, in3giorni, pagine della Commissione. **Nessuna pagina per Paese con i costi**: battibile in italiano. In tedesco e spagnolo vincono le casse e la previdenza (ricerche di navigazione).

**Chi paga e quanto.** Pubblicità Italia/Germania/Francia 2-4 € (ipotesi). Assicurazioni di viaggio per chi va dove la tessera non vale: **Heymondo** ha un programma (pagina `heymondo.com/affiliate-program/` 200, commissione non scritta nel testo leggibile, 30 giorni di cookie secondo il rapporto del 26/10): finché la cifra non è scritta non la conto. Staysure vale solo per chi parte dal Regno Unito.

**Stima a 18 mesi (€/anno).** Solo pubblicità.
- Prudente: 4.000 × 1,3 × 2 / 1.000 = **10 €**.
- Centrale: 15.000 × 1,4 × 3 / 1.000 = **60 €**.
- Ottimista: 40.000 × 1,4 × 4 / 1.000 = 224 €, più circa 380 € se Heymondo pagasse 10 % su premi da 40 € con lo 0,25 % di conversioni (ipotesi non verificata) → **circa 600 €**.

**Ore.** 8-12 (32 pagine Paese, testo strutturato, traduzione e revisione in 4 lingue; si riusa il motore della sezione GHIC).

**Voto 5,5.** Fonte aperta e buco vero in italiano, ed è un fronte nuovo di lingua per una sezione che costruiamo comunque. Ma vale pochissimo senza una commissione scritta. RISERVA: si fa insieme alla GHIC solo se la GHIC, una volta online, porta visite.

---

## 4. Vaccinazioni obbligatorie diverse dalla febbre gialla: meningite per Hajj e Umrah, polio (voto 4, RISERVA debole)

**Cosa.** Una pagina accanto a quella della febbre gialla (se Massimiliano dice sì al tema): l'Arabia Saudita chiede il certificato contro la meningite ACWY per Hajj e Umrah, almeno 10 giorni prima dell'arrivo; chi parte da Pakistan e Afghanistan può dover mostrare la vaccinazione contro la polio. Solo il documento richiesto alla frontiera, nessun consiglio medico.

**Fonte ufficiale (curl).** CDC, pagina destinazione Arabia Saudita **200** (pubblico dominio): "Meningococcal vaccine is required for those traveling to Saudi Arabia to take part in Hajj or Umrah"; febbre gialla "Updated April 23, 2025". Consigli britannici (API OGL): Arabia Saudita aggiornata il 27/10/2026, "You must have a valid certificate of vaccination against the ACWY strains of meningitis 10 days before arriving for Hajj and Umrah"; Pakistan: "provide proof of polio vaccination if asked". Contando nei 225 Paesi britannici: 15 citano la polio, 2 la meningite. Chiuse: Ministero della Salute saudita (vecchi indirizzi **404**, home **000**), pagina OMS delle vaccinazioni per Paese **404**, pagina dell'emergenza polio di GPEI **404**.

**Domanda.** gb/en "umrah vaccine" 10 (requirements 2026, for pakistan, dubai, **price**, abu dhabi, singapore, sharjah); "meningitis vaccine for umrah" 10 (cost, near me, certificate, lahore, visa, "is it compulsory", nhs); "hajj vaccine requirements" 10 (2026, uk, usa, pakistan, pdf); id/id "umrah vaccine" 10. pk/en "polio certificate" 10 (online, download, **nadra**, karachi, lahore, for international travel): è il certificato pakistano, ricerca di navigazione verso il sito del governo pakistano.

**Chi c'è su Google.** CDC, NHS fitfortravel e TravelHealthPro, cliniche di vaccinazione (Superdrug, Boots e cliniche private con il prezzo), agenzie di Hajj, giornali del Golfo. Le ricerche "price / near me / Lahore" vogliono una clinica, non una regola.

**Chi paga e quanto.** Solo pubblicità; le cliniche di vaccinazione sono servizi sanitari (non le proporrei come affiliazione). Pubblico britannico 8-10 €, del Golfo e del Pakistan molto meno.
- Prudente 2.000 × 1,3 × 5 / 1.000 = **13 €**; centrale 6.000 × 1,4 × 8 / 1.000 = **67 €**; ottimista 15.000 × 1,4 × 10 / 1.000 = **210 €** (arrotondato 250 con le pagine polio).

**Ore.** 4-6.

**Voto 4.** Una regola per un Paese, già scritta da CDC, NHS e agenzie; le varianti con soldi sono cliniche. Ha senso solo come riga della pagina febbre gialla, se quella si fa.

---

## 5. Assicurazione sanitaria obbligatoria per la working holiday, destinazione per destinazione (voto 4,5, RISERVA debole)

**Cosa.** Per ogni destinazione di working holiday (Canada, Nuova Zelanda, Giappone, Corea, Australia, Regno Unito, Irlanda, Germania…): l'assicurazione è obbligatoria? per quanto tempo e con quale copertura? la controllano all'arrivo? Con SafetyWing (già approvato e attivo nella rete) come pagatore.

**Fonte ufficiale (curl).** Regno Unito, Youth Mobility `gov.uk/api/content/youth-mobility` **200**: niente assicurazione, si paga la sovrattassa sanitaria "usually £776 per year". Australia 417 `immi.homeaffairs.gov.au/…/work-holiday-417` **200** (1,3 MB): nessuna frase sull'assicurazione obbligatoria trovata nel testo. Nuova Zelanda: home 200, pagina britannica della working holiday 200 ma la frase sull'assicurazione non è nel testo leggibile (una ricerca web trova la pagina ufficiale "formshelp/medical-insurance"); il ricercatore Canada-Australia-NZ di oggi segnala Incapsula su tutto il sito. Canada IEC `canada.ca` **000**. Giappone MOFA **403**.

**Domanda.** gb/en "working holiday insurance" 10 (australia, canada, new zealand, japan, uk, bupa); "iec insurance" 10 (canada, **requirements**, for australians, discount code, for uk citizens); au/en "working holiday visa insurance" 10 (requirement, japan, nz, hong kong, germany).

**Chi c'è su Google.** hellosafe (due pagine), **pvtistes.net** (fortissimo, guida per ogni destinazione e per i britannici), milesopedia, santexpat, ratehub, redhelm, comparetravelinsurance.co.nz e gli assicuratori. Le working holiday per nazionalità sono già state chiuse come sito oggi (rapporto Canada-Australia-NZ, voto 5).

**Chi paga e quanto.** SafetyWing Ambassador (già approvato, link attivi in 450 pagine dal 30/10); cifra per polizza non riletta oggi. Ipotesi: 10 % di circa 50 € al mese per 6 mesi in media = circa 30 € a cliente.
- Prudente: 1.500 visite × 0,05 % = 1 cliente ≈ 30 € (pubblicità trascurabile) → **circa 20-30 €**.
- Centrale: 5.000 × 1,4 × 8 / 1.000 = 56 € + 5.000 × 0,1 % = 5 clienti × 30 = 150 € → arrotondo **150 €** (stima prudente sul numero di clienti).
- Ottimista: 15.000 × 1,4 × 10 / 1.000 = 210 € + 15.000 × 0,1 % × 30 = 450 € → **circa 700 €**.

**Ore.** 6-8. **Voto 4,5.** Pagatore già in casa, ma fonti delle destinazioni principali chiuse e un concorrente (pvtistes) che fa esattamente questo da anni.

---

## 6. Assicurazione sanitaria universitaria per studenti stranieri negli USA (voto 3,5, NO)

**Cosa.** Per università: costo annuo del piano sanitario dell'ateneo, regole per rinunciarvi ("waiver"), scadenze, e piani alternativi accettati.

**Domanda.** us/en "student health insurance waiver" 10 (niu, gwu, nyu, usc, rowan, unc, howard, uiuc, uvm); "university health insurance waiver" 10 (pace, american, miami, rowan, suffolk, northeastern, howard, ohio, columbia); in/en "health insurance for international students in usa" 10 (cost, cheapest, best). Domanda vera e per ateneo.

**Fonte.** Nessuna fonte centrale: ogni università ha la sua pagina (oltre mille atenei), con formati diversi; solo il minimo dei visti J-1 è federale (regola unica). Lavoro da raccolta, non da dati.

**Chi paga.** Non trovato: `isoa.org/affiliate-program` **200 ma è la home page**, nessun programma; IMG `imglobal.com/affiliate-program` **403**; Insubuy **403**; International Student Insurance `/affiliates/` **404**; VisitorsCoverage **404**; studentinsurance.com e Compass **000**.

**Voto 3,5, NO.** Domanda per ateneo, ma nessuna fonte unica e nessun pagatore verificato; le ricerche "waiver + ateneo" sono di navigazione verso il portale dell'ateneo.

---

## 7. Visite mediche per i visti del Golfo (GAMCA/Wafid) e certificato di idoneità degli Emirati (voto 3,5, NO)

**Domanda.** Enorme: in/en "gamca medical" 10 (status, report check, fees, centre, patna); pk/en "gamca medical fee" 10 ("fees in pakistan 2026", "for saudi arabia 2026", "for bahrain", gujranwala); bd/en "wafid medical" 10 (check, status, slip, result); ae/en "medical test for visa" 10 (dubai, abu dhabi, renewal, sharjah, "24 hours"); "visa medical test price" 10 (fees in dubai, oman, saudi).

**Fonte.** `wafid.com` **200** e `wafid.com/book-appointment/` **200** (284 voci nel menu dei Paesi), ma **le tariffe si vedono solo dopo la scelta, dentro lo script**; è il portale saudita del sistema, licenza di riuso non trovata. Emirati: `ehs.gov.ae` **000**, `dha.gov.ae` home 200 ma la pagina dell'idoneità medica **404**; la ricerca web cita una lista prezzi di Dubai Health (26/3/2026) che non ho letto.

**Chi c'è su Google.** Per gli Emirati: uno strumento automatico (zavis.ai "visa medical test" per città), due siti automatici su `pages.dev` (uaeroadmap, typingcenter), gulfnews, virtuzone, takween, arnifi, dubaisouthbh. Per GAMCA: le ricerche più forti sono "status / report check" (servizio del portale, non battibile).

**Chi paga.** Nessuno: pubblico con pubblicità molto bassa (India, Pakistan, Bangladesh, Nepal) e nessuna affiliazione.

**Voto 3,5, NO.** Dati chiusi nello script, concorrenti automatici già presenti, nessun pagatore.

---

## Fonti e prove (31/10/2026)

**Lette con curl (200 se non scritto diversamente):**
- GOV.UK API: `api/content/tb-test-visa` (72 collegamenti); 72 pubblicazioni e 63 pagine "tuberculosis-testing-in-…" (Pakistan 20/2/2026, Nigeria 13/5/2026, India 20/4/2026); `api/content/foreign-travel-advice` (226 Paesi, tutti scaricati: 21 con regole specifiche sui farmaci, 15 con la polio, 2 con la meningite); `api/content/youth-mobility` (£776 l'anno).
- Giappone: `ncd.mhlw.go.jp/en/` e `/en/application2.html` 200; `dl_data/keitai/cotrolled_substances_list20241212 .pdf` 200 (350 kB); `mhlw.go.jp/chosakuken/index.html` 200 (licenza PDL 1.0). 404: `mhlw.go.jp/english/policy/health-medical/pharmaceuticals/01.html`, `kouseikyoku.mhlw.go.jp/kantoshinetsu/english/…`.
- INCB: `incb.org/incb/en/travellers/country-regulations.html` 200 (96 PDF in inglese, anni 2007-2026); `…/files/JPN_ENG_2024.pdf` 301; pagine dei termini d'uso 404.
- Commissione europea: `ec.europa.eu/social/main.jsp?catId=1021&langId=en` 200 (32 Paesi); pagina Spagna 200; `europa.eu/youreurope/…/temporary-stays/` 200.
- CDC: pagina Arabia Saudita 200; "travel abroad with medicine" 200.
- `wafid.com`, `wafid.com/book-appointment/` 200 (tariffe nello script); `dha.gov.ae` 200; `immi.homeaffairs.gov.au/…/work-holiday-417` 200; `immigration.govt.nz/visas/united-kingdom-working-holiday-visa/` 200.
- Affiliazioni: `heymondo.com/affiliate-program/` 200 (nessuna cifra nel testo); `isoa.org/affiliate-program` 200 (home page, nessun programma).

**Chiuse o mute dal server (non aggirate):** `salute.gov.it` (pagina anti-robot Gcore), `mohap.gov.ae` 000, `ehs.gov.ae` 000, `moh.gov.sa` 000/404, `tga.gov.au` 000, `canada.ca` 000, `secure.cic.gc.ca/pp-md/pp-list.aspx` 200 una volta poi connessione interrotta, `travel.state.gov` 403, `cbp.gov` 403, `mofa.go.jp` 403, `servicesaustralia.gov.au` 000, `hsa.gov.sg` 404 (vecchi indirizzi), `abf.gov.au` 404, pagina OMS delle vaccinazioni per Paese 404, `polioeradication.org` 404, `imglobal.com` 403, `insubuy.com` 403.

**Autocomplete:** circa 70 interrogazioni (us/en, gb/en, pk/en, ng/en, in/en, bd/en, ae/en, ph/en, au/en, id/id, it/it, de/de, fr/fr, es/es, nl/nl). **Ricerca web** (risultati come da un computer negli USA): "can I bring adderall to japan", "can you bring vyvanse to italy", "tb test for uk visa price in pakistan 2026", "tb test for uk visa in hyderabad cost clinic", "medical fitness test for visa dubai price 2026", "working holiday visa insurance requirement…", "tessera sanitaria europea valida in Turchia Marocco Svizzera".

## Cosa propongo

1. **Idea 1** (visite mediche per i visti, a partire dal test TB britannico): in coda bassa come sezione di Visa Income Checker, al posto del riquadro del rapporto Africa-diaspora; dentro una pubblicazione già prevista; misura a 30 giorni (soglia: ≥ 30 visite al mese sulle pagine città, provenienza ChatGPT inclusa).
2. **Idee 2 e 4**: aspettano il sì o il no di Massimiliano sul tema sanitario (la stessa domanda già aperta per la febbre gialla). Se sì, prima la 4 (piccola, accanto alla febbre gialla), poi la 2 limitata al Giappone e ai 21 Paesi con regola britannica scritta.
3. **Idea 3**: si decide dopo i primi numeri della sezione GHIC.
4. Idee 5, 6, 7: chiuse (riserva debole o NO), da annotare in ESPLORATE.
