# Dai nostri dati e dai motori di risposta: cosa funziona e cosa copiare (14/11/2026)

Solo ricerca: nessun sito modificato. Approcci del giro: n. 1 «Dai nostri dati» e n. 2 «Motori di risposta» della lista in `BRIEF-RICERCA.md`.

**Metodo.** Visite: API GoatCounter (`stats/hits` giorno per giorno con paginazione, `stats/total`, `stats/toprefs`, provenienze pagina per pagina con `stats/hits/<id>`), dal 31/10 al 13/11/2026, due settimane piene a confronto: **31/10-6/11** e **7-13/11**. Host vecchi e nuovi sommati (netlify + dominio). Provenienze lette sulle 233 pagine con almeno 2 visite nella seconda settimana (1.253 visite su 1.636). Domanda: 45 ricerche allo strumento dei volumi (medie mensili Google Ads, un Paese alla volta). Fonti ufficiali: provate oggi con curl, stato scritto accanto.

## 1. In breve

- **1.636 visite in 7 giorni contro 906 la settimana prima (+81 %).** Tre siti fanno il 93 %: EsameB1 625 (era 442), Visa Income 505 (era 178, ×2,8), Before You Fly 387 (era 175, ×2,2).
- **Da dove arrivano (7-13/11):** Google 672 (era 426), **ChatGPT 302 (era 141, raddoppiato: il 18 % di tutte le visite)**, diretto 328. Gli altri motori di risposta quasi non esistono: Gemini 4, Perplexity 2, Bing 1.
- **Google e ChatGPT premiano pagine diverse.** Google manda le persone sulle pagine «una cosa ufficiale in un luogo» (esame per città, cerimonia per council, liquidi per aeroporto). ChatGPT manda sulle pagine «un numero o un link ufficiale che lui non sa a memoria» (esempi d'esame ufficiali, percentuale di visti rifiutati per nazionalità, Starlink sì/no per Paese).
- **Le pagine che rendono di più per pagina sono poche e strette:** esempi d'esame 12 visite a pagina a settimana, pagine degli enti 9, risultati 4,8, città 3. Le griglie grandi rendono 0,1-0,2 (385 pagine «moved to»: 34 visite; 160 pagine H-1B: 6).
- **Sette candidati nuovi misurati**, tutti dentro siti esistenti. Nessuno è grande: insieme valgono circa **1.700 €/anno centrali a 36 mesi per circa 70 ore (24 €/ora)**. I due migliori (pagine «dopo l'esame» ed esempi A2/B2 su EsameB1) stanno a 37-38 €/ora, cioè appena sotto la soglia dei 40.

## 2. I numeri veri

### 2.1 Per sito (visite in 7 giorni)

| Sito | 31/10-6/11 | 7-13/11 | Pagine viste nella settimana |
|---|---|---|---|
| EsameB1 | 442 | **625** | 100 |
| Visa Income Checker | 178 | **505** | 231 |
| Before You Fly | 175 | **387** | 195 |
| Cruise Health Scores | 49 | 25 | 19 |
| Tourist Tax | 29 | 24 | 20 |
| Aste in Chiaro | 27 | 20 | 15 |
| Italy Strikes | 1 | 14 | 10 |
| Payroll Tax by State (nuovo) | 0 | 13 | 2 |
| FHA condos | 1 | 11 | 2 |
| Paga CCNL (nuovo) | 0 | 11 | 1 |
| FloodCost, EsamiDiStato | 4 | 1 | 1 |
| **Totale** | **906** | **1.636** | |

Giorno migliore: 10/11 con 322 visite. Il 14/11 (parziale, letto nel pomeriggio): 126.

### 2.2 Le sezioni, con visite per pagina e provenienza (7-13/11)

«Per pagina» = visite della settimana ÷ pagine che esistono nella sezione. C = ChatGPT, G = Google (solo pagine con ≥ 2 visite).

| Sezione | Sett. prima | 7-13/11 | Pagine esistenti | Per pagina | C | G |
|---|---|---|---|---|---|---|
| EsameB1, città | 229 | 261 | 87 | 3,0 | 25 | **155** |
| Visa Income, visti rifiutati | 78 | 137 | 154 | 0,9 | **70** | 6 |
| Visa Income, cerimonie di cittadinanza australiane per council | 10 | **112** | 174 | 0,6 | 5 | **58** |
| EsameB1, esempi d'esame ufficiali | 60 | 96 | 8 | **12** | **57** | 2 |
| Before You Fly, «available in» (quasi tutto Starlink) | 64 | 97 | 529 | 0,2 | 24 | 19 |
| Before You Fly, liquidi per aeroporto | 34 | 57 | 103 | 0,55 | 6 | 29 |
| Visa Income, test d'inglese SELT per città | 48 | 49 | 85 | 0,6 | 1 | 23 |
| EsameB1, pagine in inglese | 17 | 44 | 17 | 2,6 | 0 | 19 |
| EsameB1, enti (CILS, CELI, PLIDA, CERT.IT) | 41 | 36 | 4 | 9 | 2 | 23 |
| Visa Income, «moved to» | 13 | 34 | 385 | 0,09 | 2 | 9 |
| Before You Fly, uscita dei biglietti | 8 | 33 | 34 | 1,0 | 10 | 16 |
| Before You Fly, passaporto canadese | 1 | 27 | 230 | 0,12 | 0 | 5 |
| Before You Fly, e-Visa India | 8 | 26 | 26 | 1,0 | 7 | 8 |
| EsameB1, risultati | 5 | **24** | 5 | 4,8 | 0 | 11 |
| Visa Income, studiare in Italia | 10 | 23 | 15 | 1,5 | 1 | 6 |
| Visa Income, spagnolo | 3 | 22 | 41 | 0,5 | 0 | 12 |
| Visa Income, visti per le università migliori | 0 | 17 | 82 | 0,2 | 0 | 9 |
| Before You Fly, bagaglio a mano | 1 | 14 | 41 | 0,3 | 7 | 0 |
| Visa Income, H-1B | 0 | 6 | 160 | 0,04 | 0 | 2 |

### 2.3 Le pagine cresciute di più in una settimana

| Pagina | Prima | Dopo |
|---|---|---|
| Visa Income, home | 7 | 63 |
| EsameB1, home | 58 | 106 |
| Before You Fly, home | 12 | 47 (45 dirette: non è ricerca) |
| EsameB1 `/esempi/cils` | 14 | 37 (21 da ChatGPT) |
| EsameB1 `/citta/milano` | 28 | 49 (34 da Google) |
| EsameB1 `/risultati/cils` | 1 | 16 |
| Visa Income, indice delle cerimonie australiane | 0 | 15 |
| EsameB1 `/en` | 3 | 18 |
| Before You Fly `/available-in/starlink` | 10 | 21 |
| EsameB1 `/citta/como` | 1 | 12 |
| Visa Income `/top-university-visas/j-find` | 0 | 10 |
| Before You Fly `/available-in/wise` | 0 | 9 |
| Visa Income rifiuti Bangladesh / Algeria | 3 / 2 | 10 / 9 (tutte da ChatGPT) |
| Before You Fly biglietti Musei Vaticani / Ghibli | 6 / 0 | 12 / 6 |

### 2.4 Dove manda ChatGPT (228 visite lette pagina per pagina)

- EsameB1 85: `/esempi/cils` 21, `/esempi` 12, `/esempi/celi` 12, `/esempi/plida` 11 (da Google su queste quattro: 0), poi le città (Milano 6, Messina 3, Cagliari 3).
- Visa Income 81: quasi tutto sui rifiuti per Paese (Bangladesh 10, Algeria 9, Pakistan 5, Canada 4, Regno Unito 4, Sri Lanka 4, India 4, Cina 3, Uganda 3).
- Before You Fly 54: Starlink 10 + Paesi (Arabia Saudita 4, Thailandia 3), Musei Vaticani 7, Belfast liquidi 5, e-Visa India 4, bagaglio Wizz Air 4, United 3.
- Aste in Chiaro 6 (auto all'asta 4, Roma 2).
- Perplexity 2 (EsameB1 Roma, rifiuti Vietnam), Gemini 4 (tre pagine «studiare in Italia», una SELT), Bing 1.

## 3. Cosa hanno in comune le pagine che vincono

**Tipo A, «pagina da Google» (città, council, aeroporto).** Un servizio ufficiale + un luogo preciso + un dato che l'ente pubblica solo in elenchi o PDF. La frase cercata è piccola e senza concorrenti. Prova: le cerimonie australiane hanno un volume misurato di circa 3.000 ricerche al mese in tutto («citizenship ceremony» 1.900, «australian citizenship ceremony» 880, «citizenship ceremony dates» 170) e noi ne prendiamo 112 visite a settimana dopo 14 giorni. Dove il volume misurato è grande (H-1B, passaporti, «moved to») prendiamo quasi zero.

**Tipo B, «pagina da ChatGPT».** Quattro tipi di domanda ci fanno citare:
1. «Che percentuale di [nazionalità] viene rifiutata per [visto]?» → un numero ufficiale per nazionalità, con anno e fonte.
2. «Dove trovo le prove ufficiali di [esame]?» → elenco di link diretti ai file ufficiali (PDF e audio) che nessuno ha messo in ordine.
3. «[Servizio] funziona in [Paese]?» → sì/no con data e fonte.
4. «Quando escono i biglietti di X?» / «Che misura ha il bagaglio di Y?» → una regola o un numero secco.

In tutti i casi: risposta nella prima frase, fonte ufficiale con link, data di lettura, una pagina per ogni voce (Paese, ente, attrazione). Le pagine uniche con tutte le nazionalità in una tabella (Canada, Regno Unito, Australia: 4-5 visite l'una) rendono molto meno delle pagine per Paese (Bangladesh 10, Algeria 9).

**Cosa non funziona:** griglie di centinaia di pagine con lo stesso dato disposto in modo diverso (0,04-0,2 visite a pagina), e i temi con volume grande dove vince il sito ufficiale.

## 4. I candidati, in ordine di €/ora

Stima: visite a settimana attese a 36 mesi × 52 × incasso per 1.000 visite (12 € pubblico italiano, 22 € Regno Unito/Australia, 5-6 € Asia e Africa) + riquadri già attivi. Le visite attese partono dal rendimento vero per pagina delle sezioni gemelle (tabella 2.2).

| # | Candidato | Sito | Pagine nuove | Domanda misurata (al mese) | Chi paga | €/anno 36 m (p / c / o) | Ore | €/ora |
|---|---|---|---|---|---|---|---|---|
| 1 | **«Dopo l'esame»: risultati per sessione, quando arriva il certificato, cosa fare se non è superato** | EsameB1 | 6-8 | ~6.000 it: «risultati cils» 1.900, «esame cils risultati» 880, «www cvcl it risultati» 880, «risultati esami cils b1 cittadinanza» 480, «celi b1 cittadinanza risultati» 480, «risultati celi» 320, «certificato cils» 140 | pubblicità + libro B1 (6,35 € a copia) sulla pagina «non superato» | 70 / 230 / 700 | 6 | 38 |
| 2 | **Esempi ufficiali A2 e B2 (e pagine per ascolto e orale)** | EsameB1 | 8-10 | ~5.000 it: «italian test a2» 1.600, «esame italiano a2» 1.300, «simulazione test cittadinanza italiana b1 pdf» 1.000, «cils b2» 320, «cils a2 prove d'esame pdf» 210, «cils b2 prove d'esame pdf» 210, «cils a2» 170, «test italiano a2 esempio» 110 | pubblicità + libro + italki | 90 / 300 / 900 | 8 | 37 |
| 3 | **Prove d'esempio ufficiali dei test d'inglese SELT, per livello (A1, A2, B1, B2) e per ente** | Visa Income | 10-12 | ~3.000 gb: «b1 english test sample» 1.000, «b1 english exam practice» 1.000, «life skills ielts» 320, «ielts life skills b1» 210, «a1 english test sample» 170, «a1 spouse visa test sample pdf» 110; costo per clic 0,7-2,9 £ | pubblicità (pubblico britannico: conta per Journey) + libri Amazon | 80 / 290 / 1.000 | 10 | 29 |
| 4 | **Una pagina per ogni CPIA (129): sedi, iscrizioni, corsi di italiano, test A2** | EsameB1 | 129 | ~7.000 su 5 città («cpia milano» 2.900, «cpia 5 milano» 1.000, Bologna 1.600, Roma 880, Torino 880, Brescia 720) + «cpia» 18.100 + «cpia vicino a me» 880; costo per clic 2,2-4,4 € | pubblicità + corsi (italki, libro) | 90 / 340 / 1.300 | 14 | 24 |
| 5 | **Visti USA rifiutati per nazionalità** (PDF annuale del Dipartimento di Stato) | Visa Income | ~75 | us: «us visa rejection rate by country» 260, «us visa approval rate by country» 170, «us visa rejection rate» 110; in: 320 (poco misurato: è domanda da ChatGPT) | pubblicità + SafetyWing/HelloSafe già attivi | 40 / 150 / 600 | 8 | 19 |
| 6 | **Rifiuti di Canada, Regno Unito, Australia e Nuova Zelanda: una pagina per nazionalità** (oggi sono 4 pagine uniche) | Visa Income | ~180 | in: «canada visa rejection rate» 260, «visa success rate for canada from india» 210, «canada student visa rejection rate» 170, «uk visa rejection rate» 260, «uk student visa rejection rate» 170 | come sopra | 60 / 220 / 800 | 12 | 18 |
| 7 | **Date 2027 delle cerimonie nei 40 council più grandi** (dentro le pagine esistenti) | Visa Income | 0 (40 arricchite) | au: «citizenship ceremony» 1.900, «australian citizenship ceremony» 880, «citizenship ceremony dates» 170, Melbourne 140; «…dates 2027» 0 | pubblicità (Australia) + Wise | 30 / 120 / 400 | 12 | 10 |
| 8 | **Prezzo ufficiale di Starlink per Paese** (dentro le 216 pagine esistenti) | Before You Fly | 0 (216 arricchite) | ~27.000 su 4 Paesi: Nigeria ~8.000, Filippine ~6.500 (+ «starlink philippines» 27.100), Kenya ~4.600, India 8.100; costo per clic 0,05-0,2 $ | solo pubblicità (pubblico a bassa resa; il programma Starlink è già NO) | 20 / 90 / 400 | 12 | 7,5 |

### Note per candidato

1. **Dopo l'esame.** Prova nostra: `/risultati/` è passata da 5 a 24 visite in una settimana con 5 pagine, tutte da Google. Chi non ha superato l'esame è il lettore più adatto al libro. Fonti: pagine risultati degli enti già usate dal sito. Limite: molte ricerche sono «di navigazione» (vogliono il portale dell'ente).
2. **Esempi A2 e B2.** Prova nostra: le 8 pagine esempi B1 fanno 96 visite a settimana, 57 da ChatGPT e 2 da Google. Fonti oggi: indice prove CILS 200; pagina A2 CILS 500 (errore del loro server: da riprovare); CELI (cvcl.it) 200; PLIDA e CERT.IT già in `esempi.json`. L'A2 serve per la carta di soggiorno (guida A2 già online dal 14/11).
3. **Prove SELT.** È lo stesso schema degli esempi, per il pubblico della sezione SELT (49 visite a settimana, quasi tutte Google). Fonti oggi: gov.uk elenco SELT 200, Trinity 200, LanguageCert (preparazione) 200, Skills for English (prove) 200, Pearson PTE Home 200; IELTS Life Skills: indirizzo provato 404 e British Council senza risposta, da ritrovare.
4. **CPIA.** I CPIA compaiono già come riga nelle pagine città (idea del 26/10); la novità è la pagina propria, perché «cpia + città» ha un volume misurato più alto di «esame b1 + città». Fonte: anagrafe scuole del Ministero (dati aperti, 200). Limite: chi cerca vuole spesso il sito della scuola; quota bassa (2 %).
5. **Visti USA.** travel.state.gov risponde 403 anche oggi (pagina e PDF) e l'archivio web non è raggiungibile da qui: **DA RIPROVARE**, non bocciata. Via legittima: è un solo PDF l'anno; basta che Massimiliano lo scarichi dal suo browser e lo carichi (2 minuti).
6. **Una pagina per nazionalità.** I dati sono già nel sito (`rifiuti_altri.json`). Le pagine per Paese della parte Schengen prendono il doppio delle pagine uniche. Pubblico a bassa resa pubblicitaria: per questo la stima è piccola.
7. **Date delle cerimonie.** Era riserva (5) dal 12/11; ora c'è la prova che le pagine council ricevono visite. Resta il limite: 4 siti di council su 8 rispondevano 403.
8. **Prezzo Starlink.** starlink.com risponde 200 ma è una pagina vuota che si riempie con JavaScript: prezzo non leggibile con curl. **DA RIPROVARE** con il browser. Resa bassa: riserva.

## 5. Per i motori di risposta: regole di costruzione che i dati confermano

- Una pagina per ogni voce (nazionalità, ente, livello), mai una tabella unica.
- Prima frase = la risposta con il numero, l'anno e il nome dell'ente.
- Link diretto al file ufficiale e data di lettura sotto ogni cifra.
- Scegliere domande a cui l'assistente non sa rispondere a memoria: numeri che cambiano ogni anno, link a file sparsi, sì/no per Paese.
- I candidati 2, 3, 5 e 6 sono costruiti per questo canale; 1, 4 e 7 per Google.

## 6. Limiti

- GoatCounter conta meno delle visite vere (blocchi della pubblicità) e una parte del «diretto» può essere ChatGPT senza provenienza.
- Le provenienze sono lette solo sulle pagine con ≥ 2 visite (77 % delle visite).
- Due settimane sono poche: le sezioni nuove (cerimonie, passaporti) sono ancora in salita e il «per pagina» cambierà.
- I volumi sono medie Google Ads: sotto ~10 ricerche scrivono 0 e non vedono le domande fatte agli assistenti. Per i candidati 5 e 6 la stima poggia sul nostro rendimento per pagina, non sul volume.
- Le stime in euro usano 5-22 € ogni 1.000 visite: AdSense è ancora in revisione, quindi sono ipotesi.
- Nessun candidato supera i 40 €/ora: sono lavori da fare solo perché costano poche ore e usano dati che abbiamo già.
