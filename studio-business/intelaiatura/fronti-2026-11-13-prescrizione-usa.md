# Fronte nuovo, settore diritto civile USA: termini di prescrizione ("statute of limitations") per Stato × tipo di causa (13/11/2026)

Solo ricerca: nessun sito modificato. Settore lontano dalle zone già battute (non viaggi, visti, esami, assicurazioni). In `ESPLORATE.md` c'erano due righe vicine: "limite small claims per Stato" (NO del 19/10, scartata per la sola concorrenza, regola poi cambiata il 12/11) e "statute of limitations: da misurare" (12/11). Questo file chiude la seconda e rivaluta la prima.

## In breve

- **I dati ufficiali si leggono.** Prova fatta: 10 Stati × 5 tipi di causa = **50 testi di legge su 50 letti** dai siti dei parlamenti statali, con il numero di anni e l'articolo. Su 15 Stati provati, 10 si leggono subito, 2 (California, New York) bloccano i robot sul sito ma offrono una via ufficiale alternativa (archivio da scaricare, API con chiave gratuita), 3 danno problemi (Illinois, Pennsylvania, Georgia).
- **La domanda è misurata solo in parte, ma paga molto a clic.** "statute of limitations california personal injury" 1.600 ricerche al mese a **28 $**; "statute of limitations car accident" 2.400-4.400 a **21-43 $**; "wrongful death" 1.300 a **29 $**; "statute of limitations florida" 5.400 a **41 $**; debiti 4.400 a 4-8 $. La coda Stato × causa è misurata per una sola coppia (California × lesioni personali); il resto è stimato dal completamento automatico.
- **I concorrenti sono forti ma hanno buchi dimostrati:** tre tabelle note riportano ancora "Louisiana 1 anno" (dal 1/7/2024 sono 2), una "Florida 4 anni" (dal 24/3/2023 sono 2), una "Ohio contratti verbali 6 anni" (la legge letta oggi dice 4). Il concorrente migliore (Casefleet) è aggiornato e cita ogni articolo, ma è **una pagina sola**, senza pagine per Stato × causa.
- **Stima (sito nuovo, 51 giurisdizioni × 11 cause):** prudente / centrale / ottimista **35 / 450 / 5.000 €/anno a 18 mesi; 100 / 1.100 / 10.000 a 36 mesi**. Voto **5**. Sotto l'asticella dei siti nuovi (voto ≥ 7 e ≥ 5.000 € centrali), ma con euro attesi positivi e nessun blocco legale.
- **Decisione: COSTRUIRE come prova piccola, in coda** (10 Stati già letti × 6 cause che pagano di più = 60 pagine + calcolatore della scadenza, circa 25 ore di agenti), dentro un sito unico "scadenze e limiti di legge per Stato" che ospita anche le due famiglie vicine (interessi sulle sentenze, limiti small claims). Si allarga a 51 Stati solo se arrivano impressioni. Serve un dominio: spesa da chiedere a Massimiliano (circa 10-12 €/anno).

## 1. Come ho misurato e che cosa non so

- **Volumi:** la chiave dello strumento era bloccata per limite di frequenza (errore 429). Ho usato le ricerche gratuite senza chiave: **15 hanno risposto** (3 con "0" = nessun dato), 10 respinte. Ogni risposta porta dieci frasi simili.
- **Non misurati:** "medical malpractice statute of limitations", debiti per singolo Stato, tutte le coppie Stato × causa tranne California × lesioni, interessi sulle sentenze, durata delle sentenze, sfratti. Per questi c'è solo il completamento automatico di Google (gl=us).
- **Zero non vuol dire zero:** "statute of limitations sexual abuse", "eviction notice period by state", "wage garnishment limits by state" sono tornate senza dato.
- **La pagina dei risultati di Google non è stata letta.** Non so quante ricerche Google chiude con il riquadro di risposta ("2 years") senza clic: per domande con risposta di un numero è probabile che siano molte. È il rischio principale della stima.
- **Nolo, FindLaw, Justia, Avvo, LawInfo e Forbes rispondono con un blocco anti-robot (403).** Non li ho aggirati: non ho letto le loro pagine. Ho letto AllLaw (rete Nolo, stessa tabella), LegalMatch, Miller & Zois (studio legale), World Population Review, Casefleet, Terms.Law, USLegal.
- Cambio usato: 1 $ = 0,92 €.

## 2. Leggibilità dei dati ufficiali

### 2.1 Prova 10 Stati × 5 cause (curl, 13/11/2026)

Per ogni cella: pagina ufficiale scaricata, testo dell'articolo trovato con il termine. **50 su 50.**

| Stato | Fonte ufficiale | Lesioni personali | Colpa medica | Contratto | Diffamazione | Quinta causa |
|---|---|---|---|---|---|---|
| Texas | tcss.legis.texas.gov (Civil Practice & Remedies Code) | 2 anni, § 16.003 | § 74.251 | 4 anni, § 16.051 (residuale) | 1 anno, § 16.002 | debito 4 anni, § 16.004 |
| Florida | leg.state.fl.us, § 95.11 | 2 anni, (5)(a) | 2 anni, (5)(c) | scritto: (2)(b) | (5)(h) | morte ingiusta (5)(e) |
| Ohio | codes.ohio.gov | 2 anni, § 2305.10 | 1 anno, § 2305.113 | scritto 6 anni, § 2305.06; verbale 4 anni, § 2305.07 | 1 anno, § 2305.11 | morte ingiusta 2 anni, § 2125.02 |
| Washington | app.leg.wa.gov (RCW) | 3 anni, 4.16.080 | 3 anni (o 1 dalla scoperta), 4.16.350 | scritto 6 anni, 4.16.040 | 2 anni, 4.16.100 | verbale 3 anni, 4.16.080(3) |
| Virginia | law.lis.virginia.gov | 2 anni, § 8.01-243 | § 8.01-243 (estensioni) | scritto 5 anni, § 8.01-246 | 1 anno, § 8.01-247.1 | morte ingiusta 2 anni, § 8.01-244 |
| North Carolina | ncleg.gov | 3 anni, § 1-52 | § 1-15 | 3 anni, § 1-52(1) | 1 anno, § 1-54(3) | 2 anni, § 1-53 |
| Michigan | legislature.mi.gov | 3 anni, MCL 600.5805(2) | 2 anni, 600.5805(8); 6 mesi dalla scoperta, 600.5838a | 6 anni, 600.5807(9) | 1 anno, 600.5805(11) | — |
| Arizona | azleg.gov | 2 anni, § 12-542 | 2 anni, § 12-542 | scritto 6 anni, § 12-548 | 1 anno, § 12-541 | verbale 3 anni, § 12-543 |
| Massachusetts | malegislature.gov | 3 anni, c. 260 § 2A | c. 260 § 4 | 6 anni, c. 260 § 2 | c. 260 § 4 | morte ingiusta 3 anni, c. 229 § 2 |
| Minnesota | revisor.mn.gov | 6 anni (colpa), § 541.05; 2 anni (dolo), § 541.07 | 4 anni, § 541.076 | 6 anni, § 541.05 | 2 anni, § 541.07 | morte ingiusta 3 anni, § 573.02; salari § 541.07(5) |

I numeri di questa tabella vanno ricontrollati da un revisore indipendente prima di pubblicarli: qui servono solo a dimostrare che il testo si legge.

### 2.2 Stati con ostacoli

| Stato | Che cosa succede | Via ufficiale alternativa |
|---|---|---|
| California | leginfo.legislature.ca.gov: blocco anti-robot (403). Non aggirato | Archivio ufficiale da scaricare `downloads.leginfo.legislature.ca.gov` (risponde 200, file "pubinfo") |
| New York | nysenate.gov: blocco anti-robot (403). Non aggirato | API ufficiale `legislation.nysenate.gov/api/3` con chiave gratuita (risponde "serve una chiave"): la chiave la deve chiedere Massimiliano |
| Illinois | ilga.gov: errore di certificato dal loro lato. Non ho disattivato il controllo | Riprovare; altrimenti nessuna |
| Pennsylvania | palegis.us: la pagina arriva senza il testo dell'articolo (caricato dal browser) | Da cercare (PDF del titolo 42) |
| Georgia, Colorado | Il codice ufficiale sta su LexisNexis, con condizioni d'uso proprie | Da valutare; il testo di legge in sé non ha diritto d'autore |
| New Jersey | Archivio ufficiale completo da scaricare (41 MB, risponde 200) | — |
| Wyoming | Titolo 1 in PDF ufficiale (risponde 200) | — |

**Diritto di riuso:** i testi di legge degli Stati USA non sono coperti da diritto d'autore (dottrina degli "edicts of government", confermata dalla Corte Suprema in Georgia v. Public.Resource.Org, 2020). Si può citare il testo dell'articolo con il link alla fonte.

**Debiti prescritti:** la regola federale è il Regulation F del CFPB (12 CFR 1006.26: chi riscuote non può fare causa né minacciarla su un debito prescritto). Letta oggi la scheda del CFPB (rivista il 28/10/2026, risponde 200). Il testo del regolamento su eCFR non l'ho letto oggi (richiesta sbagliata da parte mia).

## 3. Domanda

### 3.1 Volumi misurati (Google Ads, USA, media mensile)

| Frase | Volume | Costo per clic |
|---|---|---|
| statute of limitations | 90.500 | 6,87 $ |
| statute of limitations by state | 2.900 | 14,10 $ |
| statute of limitations texas | 6.600 | 3,50-9,89 $ |
| statute of limitations florida | 5.400 | 0,80-41,20 $ |
| statute of limitations new york | 2.900 | 0-3,69 $ |
| statute of limitations ohio | 2.400 | 0 |
| statute of limitations california personal injury (e varianti) | 1.600 + 1.300 | 22,85-29 $ |
| personal injury statute of limitations | 1.300 | 27,76 $ |
| statute of limitations personal injury by state | 390 | 10,63 $ |
| statute of limitations car accident / auto accident | 2.400 / 4.400 | 21,15-42,68 $ |
| wrongful death statute of limitations | 1.000-1.300 | 21-30 $ |
| statute of limitations on debt | 4.400 | 3,96-8,11 $ |
| statute of limitations on debt collection | 2.400 | 5-5,89 $ |
| statute of limitations credit card debt | 1.600 | 6,54-7,49 $ |
| what is the statute of limitations on debt | 1.300 | 9,38 $ |
| statute of limitations by state for debt collection | 880 | 3,01 $ |
| time barred debt | 390 | 15,34 $ |
| breach of contract statute of limitations | 880 | 2,68-4,40 $ |
| defamation / libel / slander statute of limitations | 720 | 0 |
| statute of limitations for sexual assault | 8.100 | 0 (ricerca soprattutto penale) |
| small claims court | 49.500 | 6,05 $ |
| small claims court limit | 3.600 | 3,46-9,25 $ |
| how to file a small claims court (e varianti) | 3.600-6.600 | 2,14-7,59 $ |

Lettura: le cause dove gli studi legali comprano clienti (incidenti, lesioni, morte ingiusta) valgono **20-40 $ a clic**; debiti e small claims 4-9 $; contratti 3-4 $; diffamazione e ricerche penali zero.

### 3.2 Ampiezza dal completamento automatico

"statute of limitations <causa> <Stato>", numero di suggerimenti (massimo 10) in quattro Stati: due grandi, uno medio, uno piccolo.

| Causa | California | Texas | Ohio | Wyoming |
|---|---|---|---|---|
| personal injury | 8 | 10 | 6 | 6 |
| medical malpractice | 9 | 9 | 3 | 3 |
| debt | 10 | 10 | 10 | 8 |
| breach of contract | 10 | 6 | 3 | 3 |
| property damage | 10 | 8 | 8 | 4 |
| wrongful death | 4 | 7 | 5 | 4 |
| defamation | 8 | 7 | 6 | 0 |
| fraud | 10 | 10 | 9 | 2 |
| child sexual abuse | 4 | 0 | 0 | 0 |
| wage claim | 3 | 3 | 3 | 0 |
| small claims | 4 | 4 | 3 | 0 |

- **Debiti, lesioni, danni alle cose e frode** hanno domanda in ogni Stato, anche piccolo. I suggerimenti sui debiti si dividono per tipo (medico, carta di credito, sentenza, fiscale): sono pagine diverse con articoli diversi.
- **Abusi su minori, salari, small claims:** domanda quasi solo negli Stati grandi. Gli abusi su minori li terrei fuori dalla prova: tema delicato, pubblicità limitata, norme che cambiano spesso con "finestre" temporanee.
- I suggerimenti chiedono proprio ciò che una tabella generica non dà: "minor", "discovery rule", "exceptions", "written / oral", "medical debt", "judgement". **La profondità per pagina è richiesta dalla domanda stessa.**
- Altre frasi con 10 suggerimenti su 10: "statute of limitations calculator" (anche per Texas, Florida, New York, California), "statute of limitations car accident <Stato>", "dog bite statute of limitations <Stato>", "how long do i have to sue…".

### 3.3 Domanda totale usata nella stima (ipotesi dichiarata)

- Ricerche "statute of limitations <Stato>": quattro Stati misurati sommano 17.300 e hanno il 25 % della popolazione → circa **68.000 al mese** in tutto il Paese. Una parte è penale (i suggerimenti mostrano "theft", "felony").
- Cause senza Stato (incidenti, lesioni, morte ingiusta, debiti, contratti, diffamazione): circa **25.000** misurate.
- Stato × causa: California × lesioni circa 3.000; California è il 12 % della popolazione → circa 25.000 per le lesioni in tutti gli Stati. Per le altre cause **non misurato**: ipotesi 60.000-100.000 in tutto.
- **Totale di lavoro: circa 200.000 ricerche al mese** (metà misurata o estrapolata da misure, metà ipotesi). La testa "statute of limitations" (90.500) resta fuori: è una ricerca di definizione.

## 4. Concorrenti: che cosa ho letto e che cosa manca

| Sito | Che cosa offre | Data | Cita l'articolo | Buco trovato |
|---|---|---|---|---|
| Nolo, FindLaw, Justia, Avvo, LawInfo | Non letti (blocco anti-robot). Dai risultati di ricerca: tabelle per Stato e pagine per Stato; sono i primi | — | — | — |
| AllLaw (rete Nolo), lesioni personali | Tabella 50 Stati, una riga per Stato | modificata 14/8/2023; articoli datati "(2020)" | sì, senza link | **Louisiana 1 anno** (dal 1/7/2024: 2 anni). Minnesota "2 anni" (per colpa sono 6, § 541.05 letto oggi) |
| LegalMatch | Tabella 50 Stati | "aggiornata 23/7/2025" | sì, senza link | **Florida 4 anni** (dal 24/3/2023: 2, § 95.11(5)(a) letto oggi); Louisiana 1 anno |
| Miller & Zois (studio legale) | Tabella 50 Stati, 23 link a siti ufficiali | senza data | sì | Louisiana 1 anno |
| World Population Review | Tabella: contratti scritti, verbali, lesioni, cose, reati | 11/11/2026 | **no**, zero link ufficiali | **Ohio contratti verbali 6 anni** (§ 2305.07 letto oggi: 4 anni). Nessuna regola di sospensione |
| Casefleet | Strumento: 51 giurisdizioni × 9 cause, 459 citazioni con link al codice ufficiale, registro delle modifiche (Florida, Louisiana, Nevada) | verificato 29/4/2026 | sì, con link | **Nessun buco nei dati.** Ma è una pagina sola (nessun indirizzo per Stato × causa), fatta per vendere un programma agli studi legali |
| Terms.Law | Mappa 50 Stati × 8 cause con calcolatore | marzo 2026 | no (2 link ufficiali in tutto) | Pagina sola |
| USLegal | Pagine per Stato | senza data | no | Testo generico |

La modifica della Louisiana (Act 423 del 2024) l'ho letta su Casefleet, non sul sito ufficiale (legis.la.gov non mi ha dato la pagina giusta): va verificata sulla fonte.

**Che cosa manca a tutti quelli letti:** una pagina per ogni coppia Stato × causa con 1) il testo dell'articolo, 2) il link al codice ufficiale, 3) la data di verifica, 4) le regole che spostano la scadenza (minori, scoperta tardiva, assenza dallo Stato, termine massimo "statute of repose", preavviso più breve per le cause contro enti pubblici), 5) le modifiche recenti con la data da cui valgono. Le tabelle danno un numero solo, e in tre casi su quattro quel numero è vecchio.

**Quota realistica.** Dominio nuovo, tema legale (Google è severo con i siti che toccano soldi e diritti), primi posti di Nolo, FindLaw, Justia e degli studi legali locali, più il riquadro di risposta di Google. Stima delle visite sul totale delle ricerche: **0,1 % / 0,5 % / 2 % a 18 mesi; 0,3 % / 1,2 % / 4 % a 36 mesi.** È sotto la fascia 3-15 % indicata nelle regole: qui i concorrenti forti sono molti e la risposta è un numero che Google mostra da solo.

## 5. Chi paga

| Fonte | Cifra letta | Dove |
|---|---|---|
| Pubblicità | Sito USA di ricerca in archivi legali: 46 $ ogni 1.000 pagine | annuncio di vendita 55704, `fronti-2026-11-12-siti-in-vendita.md` (dati 2019-2021) |
| Pubblicità, costo per clic degli inserzionisti | 21-43 $ incidenti e lesioni; 4-9 $ debiti | misure di oggi (§ 3.1) |
| Rocket Lawyer | 24 % delle vendite; guadagno per 100 clic a 90 giorni 0,25 $ | scheda FlexOffers letta oggi (modificata 14/8/2026) |
| LegalZoom | 15 % per vendita | da elenchi di terzi, **non letta** sulla pagina del programma |
| LegalShield | 20-30 % (fonti discordi) | da elenchi di terzi, **non letta** |
| Contatti per studi legali (lesioni) | 7 $ a contatto | risultato di ricerca su una scheda FlexOffers; la scheda oggi ha risposto 429, **non letta** |

- **Il pagatore vero è la pubblicità.** Uso 12 / 25 / 60 $ ogni 1.000 pagine (prudente / centrale / ottimista). L'ottimista vale solo se il traffico cade sulle pagine incidenti e lesioni.
- **Le affiliazioni legali rendono poco:** Rocket Lawyer dichiara 0,25 $ ogni 100 clic. Chi cerca una scadenza non compra un modulo. Nella stima contano meno del 10 %.
- **Niente intermediazione di debiti o crediti** (consolidamento, "debt relief", prestiti): attività regolata negli USA e fuori dai nostri vincoli. Sulle pagine dei debiti: solo pubblicità automatica e link al CFPB.
- **Niente modulo di raccolta contatti nostro:** raccoglieremmo dati personali (anche sanitari, per le lesioni) da un titolare italiano. Al massimo un link verso il modulo dell'inserzionista.

## 6. Rischi legali

- **Informazione, non consulenza.** Pubblicare il testo della legge con la fonte non è esercizio della professione. Esempio letto oggi: Texas Government Code § 81.101(c) esclude dalla "practice of law" la pubblicazione su un sito di materiali scritti che dichiarino in modo chiaro di non sostituire il parere di un avvocato.
- **Regole fisse per ogni pagina:** frase fissa "informazione generale, non consulenza legale; la scadenza del tuo caso può essere diversa: chiedi a un avvocato abilitato nel tuo Stato"; nessuna risposta su casi singoli; nessun "puoi ancora fare causa"; data di verifica e link all'articolo.
- **Il calcolatore** deve restituire "il termine generale scade il…", elencare le eccezioni e non dare mai un esito sul caso. È il punto più delicato: un utente che perde una scadenza per un numero sbagliato è il danno peggiore possibile. Per questo: revisore indipendente su ogni cella e ricontrollo almeno annuale.
- **Pagamenti per segnalare avvocati:** le regole deontologiche USA (ABA Model Rule 7.2(b)) vietano agli avvocati di pagare chi li raccomanda. Riguardano loro, non noi, ma è un altro motivo per non fare raccomandazioni di singoli studi.
- **Nessun rischio bloccante trovato.** Restano fuori: abusi su minori (delicato) e intermediazione di debiti.

## 7. Profondità per pagina (lezione AdSense)

Ogni pagina Stato × causa deve contenere, presi dalla fonte ufficiale:

1. Il termine in anni e **il testo dell'articolo** citato tra virgolette, con numero e link.
2. Da quando decorre (fatto, scoperta, ultimo pagamento per i debiti).
3. Le regole di sospensione di quello Stato: minori, incapacità, scoperta tardiva, assenza del convenuto, termine massimo.
4. Il preavviso per le cause contro enti pubblici, se c'è (spesso 6 mesi-1 anno).
5. Le modifiche recenti con data di entrata in vigore (Florida 2023, Louisiana 2024, Ohio 2021).
6. Data dell'ultima verifica.

Una pagina che cambia solo il nome dello Stato e un numero non va pubblicata. Gli Stati senza articolo letto restano fuori finché non si legge.

## 8. Lavoro

| Fase | Ore di agenti | Ore di Massimiliano |
|---|---|---|
| Prova: 10 Stati già letti × 6 cause (incidenti e lesioni, colpa medica, morte ingiusta, debiti, contratto scritto/verbale, danni alle cose) = 60 pagine + 10 pagine di Stato + calcolatore | 25 (di cui 6 di revisione indipendente) | 0,5 (dominio) |
| Estensione a 51 giurisdizioni × 11 cause (circa 560 celle), solo se la prova prende impressioni | 60-80 (di cui 25 di revisione) | 0,5 (chiave API New York) |
| Mantenimento: ricontrollo annuale e modifiche di legge | 15-20 l'anno | 0 |

Spese: dominio circa 10-12 €/anno (da chiedere).

## 9. Stima

Sito completo (51 × 11). Domanda di lavoro 200.000 ricerche al mese.

| | Quota | Visite al mese | Pagine al mese | $ per 1.000 pagine | €/anno pubblicità | + affiliazioni | **Totale €/anno** |
|---|---|---|---|---|---|---|---|
| 18 mesi, prudente | 0,1 % | 200 | 260 | 12 | 35 | 0 | **35** |
| 18 mesi, centrale | 0,5 % | 1.000 | 1.500 | 25 | 415 | 35 | **450** |
| 18 mesi, ottimista | 2 % | 4.000 | 6.400 | 60 | 4.240 | 760 | **5.000** |
| 36 mesi, prudente | 0,3 % | 600 | 780 | 12 | 100 | 0 | **100** |
| 36 mesi, centrale | 1,2 % | 2.400 | 3.600 | 25 | 1.000 | 100 | **1.100** |
| 36 mesi, ottimista | 4 % | 8.000 | 12.800 | 60 | 8.500 | 1.500 | **10.000** |

La sola prova (10 Stati, un terzo della popolazione): circa un terzo di queste cifre, cioè centrale 150 €/anno a 18 mesi e 350 a 36.

Che cosa farebbe salire la stima: misurare la coda Stato × causa (se fosse il doppio dell'ipotesi, tutto raddoppia) e vedere, dopo la prova, quale prezzo per 1.000 pagine paga davvero la pubblicità sulle pagine "incidenti". Che cosa la farebbe scendere: riquadri di risposta di Google che tolgono i clic.

**Voto: 5.** Dati leggibili e riusabili, costo per clic tra i più alti visti finora, buchi dimostrati nei concorrenti; contro: concorrenti molto forti, tema dove Google premia l'autorevolezza, coda non misurata, ritorno centrale basso rispetto alle ore (circa 100 ore per 1.100 €/anno a 36 mesi).

**COSTRUIRE: sì, come prova in coda** (regola del 12/11: euro attesi positivi, nessun blocco). Non passa l'asticella dei siti nuovi presa da sola; per questo conviene farla nascere dentro un sito unico con le famiglie del § 10.

## 10. Due famiglie vicine con dati ufficiali

### 10.1 Interessi sulle sentenze e durata delle sentenze per Stato (con calcolatore)

- **Dato ufficiale:** tasso fissato per legge o pubblicato a scadenze. Florida: tabella trimestrale del Chief Financial Officer letta oggi (dal 1/10/2026 **7,87 %**; dal 1/7/2026 8,06 %). Texas (OCCC) e tribunali federali (uscourts.gov) rispondono 200, ma il numero non è nel testo scaricato: da leggere meglio.
- **Domanda:** completamento 10 su 10 per "legal interest rate on judgments" (California, Michigan, Florida, Kansas, Texas, Georgia), "judgment interest rate texas", "how long does a judgment last in <Stato>". **Volume non misurato** (limite dello strumento).
- **Perché interessa:** il dato cambia ogni tre o sei mesi, quindi chi lo usa (studi legali, creditori, proprietari) torna; un calcolatore di interessi tiene la visita. I concorrenti non letti.
- **Stima (ipotesi 40.000 ricerche al mese, pubblico professionale):** 20 / 250 / 2.500 €/anno a 18 mesi; 60 / 700 / 6.000 a 36. 20 ore + 10 l'anno. **Voto 4,5. COSTRUIRE come seconda sezione dello stesso sito**, dopo aver misurato i volumi.

### 10.2 Limite e costi delle cause "small claims" per Stato

- **Dato ufficiale:** siti dei tribunali statali. California letta oggi (selfhelp.courts.ca.gov: fino a 12.500 $, 6.250 $ per le imprese). I costi per contea (circa 3.000 contee) sono troppo sparsi: si parte dal livello statale.
- **Domanda misurata:** "small claims court" 49.500 a 6,05 $; "small claims court limit" 3.600 a 3,46-9,25 $; "how to file…" 3.600-6.600 a 2-7,6 $. Completamento 10 su 10 per "small claims court limit <Stato>"; 0 per i costi della contea di Los Angeles, 5 per Harris County.
- **Storia:** scartata il 19/10 (voto 3) solo perché Nolo e gli studi legali rispondono già; con la regola del 12/11 si ristima la quota.
- **Stima (domanda di lavoro 80.000 al mese, 8 / 15 / 30 $ per 1.000 pagine):** 30 / 300 / 3.000 €/anno a 18 mesi; 80 / 700 / 6.000 a 36. 18 ore + 8 l'anno. **Voto 4,5. COSTRUIRE come terza sezione dello stesso sito.**

### 10.3 Altre famiglie viste di passaggio (solo completamento automatico, non stimate)

- Preavvisi e tempi di sfratto per Stato: "how long does an eviction take in <Stato>" 10 su 10; "notice to vacate" e "3 day notice to quit florida" 10 su 10, ma quasi tutti cercano un modulo ("template", "pdf", "form"). Noi non forniamo moduli: resterebbe un link a un venditore di moduli (Rocket Lawyer 24 %).
- Limiti di pignoramento dello stipendio per Stato, termine per restituire la caparra, esenzione della casa nel fallimento: 10 su 10 ciascuna.

## 11. Classifica

| # | Idea | Voto | €/anno 18 mesi (prud. / centr. / ott.) | €/anno 36 mesi | Chi paga | Quota | Rischio legale | Decisione |
|---|---|---|---|---|---|---|---|---|
| 1 | Prescrizione USA per Stato × causa, con testo di legge e calcolatore | 5 | 35 / 450 / 5.000 | 100 / 1.100 / 10.000 | pubblicità (21-43 $ a clic sugli incidenti); affiliazioni sotto il 10 % | 0,5 % a 18 mesi, 1,2 % a 36 | basso con le regole del § 6; nessun blocco | COSTRUIRE: prova di 60 pagine in coda |
| 2 | Interessi e durata delle sentenze per Stato | 4,5 | 20 / 250 / 2.500 | 60 / 700 / 6.000 | pubblicità | non stimabile: volume non misurato | basso | COSTRUIRE come seconda sezione, dopo la misura |
| 3 | Limiti small claims per Stato | 4,5 | 30 / 300 / 3.000 | 80 / 700 / 6.000 | pubblicità | 0,4 % a 18 mesi | basso | COSTRUIRE come terza sezione |
| — | Le tre insieme, un sito solo | 5,5 | 85 / 1.000 / 10.500 | 240 / 2.500 / 22.000 | | | | sotto l'asticella dei siti nuovi al centrale; passa solo all'ottimista |

Alla prossima quota di ricerche (circa 40): "medical malpractice statute of limitations", debiti per Texas, Florida e California, cinque coppie Stato × causa fuori dalla California, "post judgment interest rate", "how long does a judgment last", "small claims court limit" per tre Stati.
