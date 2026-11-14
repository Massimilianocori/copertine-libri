# Fronte del 14/11/2026: idee riaperte (fonte bloccata ≠ idea bocciata)

Compito: riprendere le idee messe in basso o in riserva **solo** perché una fonte non si leggeva (403, pagina in JavaScript, nessuna risposta) o perché un compenso era «non letto», e cercare un'altra via legittima: file ufficiale scaricabile, API ufficiale, portale di dati aperti, pagina gemella, copia d'archivio. Nessun blocco aggirato, nessuna pagina dietro login.

**Esito in una riga.** 3 idee riaperte con una via nuova che funziona (abilitazioni immobiliari, luce in Spagna, autotrasporto), 1 verifica chiusa (lemon law: il conto del 13/11 era giusto), 3 confermate NO o ferme (calendario pensioni, pompe di calore, compensi Next / Gusto-Paesi). Nessuna arriva a 5.000 €/anno centrali. La migliore è **abilitazioni immobiliari con il tasso di promozione ufficiale per scuola: voto 6, 2.800 €/anno centrali, 40 €/ora**, con una prova di 14 ore su 4 Stati.

## 1. Metodo

- **Fonti.** Provate con curl dal contenitore, senza cambiare l'identità del programma. «Letto» = risposta 200 con il dato dentro, oggi 14/11/2026.
- **Volumi.** `api.seodata.dev /v1/keyword`, 159 ricerche (US 136, ES 22, 1 di prova). Frasi con lo stesso numero nello stesso gruppo contate una volta.
- **Compensi.** «Letto» = cifra scritta sulla pagina ufficiale del programma o sulla sua pagina pubblica nella rete (PartnerStack, Awin). Gli elenchi di terzi non entrano nei conti.
- **Conti.** Pubblicità: visite × 1,3 pagine × 3,3 $ ogni 1.000 (6 $ dove il costo per clic è ≥ 10 $) × 0,92. Cambio 1 $ = 0,92 €. €/ora = €/anno centrali a 36 mesi diviso le ore.
- **Concorrenti.** Letti con curl per le idee finaliste; i 403 sono scritti e non aggirati.

## 2. Tabella

| Idea (riga in classifica) | Cosa era bloccato | Via nuova trovata (stato letto) | Dato riusabile? | 36 mesi p/c/o €/anno | Ore | €/ora | Voto | Esito |
|---|---|---|---|---|---|---|---|---|
| Abilitazioni immobiliari con il tasso ufficiale per scuola (77) | Texas: tabella in JavaScript; North Carolina e Washington non raggiunti; compensi delle scuole non letti | **Texas: file JSON ufficiale che la pagina stessa carica** (200, 30 scuole). Hawaii: bollettino PDF ufficiale (200). Compenso AceableAgent **letto**: 15-25 % a vendita, corsi Texas 449-669 $ | Sì (dato pubblico dello Stato, con data e fonte) | 200 / 2.800 / 15.000 | 70 | 40 | **6** (era 5) | **PROVA** 14 ore su Texas, Alabama, Nebraska, Hawaii |
| Autotrasporto USA: scadenze e tariffe (82) | Nessun compenso scritto; FMCSA 403 | **Coast (carta carburante) 300 $ a cliente approvato**, Motive 150 $ a cliente: letti sulle pagine pubbliche PartnerStack. Dati FMCSA sul portale aperto del Dipartimento dei Trasporti (200) | Sì per regole e tariffe; l'elenco dei vettori contiene nomi di persone: non si usa | 150 / 1.400 / 9.000 | 40 | 35 | **5** (era 3,5) | **RISERVA** con prova di 12 ore |
| Prezzo della luce ora per ora, Spagna (23) | PVPC: REE ed ESIOS 403 | **File ufficiale ESIOS del PVPC** (`archives/70`): 200 con le 24 ore di oggi, ma risponde poco più di una volta su due (9 buone su 17 richieste) | Dato giusto (uguale al concorrente); licenza ESIOS non letta | 95 / 560 / 2.250 | 27 | 21 | 4,5 (invariato) | **RISERVA sbloccata a metà**: prova di 1 ora dal posto degli aggiornamenti |
| Lemon law per Stato (49 e riga «DA VERIFICARE») | Dubbio: la stima contava solo le frasi informative? | Misurati tutti i 50 Stati: 131.870 al mese + 22.000 di frasi generali | – | 20 / 190 / 850 | 30 | 6 | 4 (invariato) | **Verifica chiusa**: il conto del 13/11 era giusto. Riserva bassa |
| Calendario dei pagamenti di pensioni USA e Canada (80) | ssa.gov 403, canada.ca non risponde | Copie d'archivio esistono (20/10/2026) ma dal contenitore non si scaricano; date USA calcolabili dalla regola | In parte | 40 / 150 / 1.100 | 20 | 7,5 | 4 | **NO confermato** (il motivo vero è la domanda a una riga, non la fonte) |
| Heat Pump Grants UK: concorrenti non letti (7) | Heatable, Energy Saving Trust 403; GreenMatch, Octopus in JavaScript | Nessuna: riprovati oggi, stesso esito | – | invariato | – | – | – | **Invariato** (sito già online) |
| Compensi non letti: Gusto (Paesi), Next, The CE Shop, 360training, LegalZoom (85, 89, 40) | Pagine dei termini 403 o dietro login | Gusto e ADP: cifre e scaglioni letti nei dati pubblici PartnerStack; contratto ADP letto (PDF). Paesi ammessi da Gusto: ancora non letti. Next, CE Shop: nessuna cifra pubblica. 360training: solo negozio con costo d'ingresso | – | – | – | – | – | Righe 85 e 89 **invariate**; 360training e CE Shop **NO come pagatori** |

## 3. Le idee una per una

### A. Abilitazioni immobiliari con il tasso di promozione ufficiale per scuola — voto 6, PROVA

- **Cosa era bloccato.** La notte del 14/11 il dato per scuola era stato letto solo in Alabama e Nebraska. Texas: «tabella in JavaScript, non letta». I compensi di AceableAgent, The CE Shop e 360training: non letti.
- **Via nuova.**
  - **Texas.** La pagina ufficiale `trec.texas.gov/education/education-provider-exam-passage-rates-sales-agents-and-brokers` carica un file pubblico dello stesso sito: `trec.texas.gov/sites/default/files/json/PassRatesRei.json` (200, 8,7 KB). Dentro: periodo 1/12/2023-30/11/2025, totale dello Stato 29.980 esami da agente con il 56,12 % di promossi, e 30 scuole con esami, promossi e percentuale (agente e broker). Esempi: AceableAgent 8.516 esami, 65,81 %; Champions School 15.547, 53,24 %; Kaplan 1.280, 53,20 %; The CE Shop 1.077, 56,45 %; 360training 290, 47,59 %. Per gli ispettori c'è un file gemello (`PassRatesInsi.json`).
  - **Hawaii.** Bollettino ufficiale della Commissione (`cca.hawaii.gov/wp-content/uploads/2026/07/sf2607.pdf`, 200): tabella per scuola, aprile-giugno 2026 e anno mobile.
  - **Non raggiunti da qui:** North Carolina (ncrec.gov 403), Colorado e Kansas (403), Washington e Arizona (i PDF trovati con la ricerca danno 404). Si riprovano dal browser o dal posto degli aggiornamenti: «DA RIPROVARE», non NO.
  - Totale: **4 Stati letti** (Texas, Alabama, Nebraska, Hawaii). Il Texas da solo è il secondo Stato per domanda.
- **Pagatore letto.** AceableAgent, pagina ufficiale `partnerships.aceable.com/affiliate`: «15–25% commission per sale, tiered by volume. 30-day attribution»; scaglione di partenza 15 % (1-25 vendite al mese); pagamento mensile con bonifico o PayPal; offerta «70 % il primo anno» solo per chi viene ammesso («Ask If You Qualify»): non contata. Prezzi dei corsi in Texas letti sulla pagina del corso: 449, 519, 669 $. Quindi **67-100 $ a vendita**, sopra la soglia di 50 $. Colibri (fino a 60 $ a vendita) era già letto. The CE Shop: la pagina ufficiale del programma non scrive cifre. 360training: 20-45 % ma solo con un negozio in concessione, costo d'ingresso e impegno annuo di fatturato: non adatto.
- **Domanda misurata.** «texas real estate license» 18.100 a 7,9 $ (stesso gruppo «real estate license texas»), «online real estate school texas» 1.900 a 12,8 $, «texas real estate exam» 720 a 9,1 $, Alabama 2.900, Hawaii 1.600 a 12,3 $, Nebraska 1.000. Recensioni delle scuole: «the ce shop reviews» 1.300, «colibri real estate reviews» 1.000, «aceable agent reviews» 720 a 93 $, «is aceable agent legit» 260 a 59 $. Le frasi sul tasso in sé restano piccole («trec pass rates» 30). Resta valido il totale della notte: ~300.000 al mese su 50 Stati.
- **Concorrenti letti (5).**
  - EstatePass, pagina «pass rate» (controllo fonti del 12/10/2026): per Texas, Florida, California e altri scrive «Comparable rate unknown; check official reports». **Non mostra la tabella per scuola.**
  - AceableAgent, pagina «pass rates» (2.587 parole): dice «Texas is 66 %» per sé, da sondaggi tra gli studenti; nessun confronto con le altre scuole.
  - Colibri, articolo generale (1.289 parole): nessun dato dello Stato per scuola.
  - EstatePass, articolo per Stato 2026 (887 parole): stime, non il dato per scuola.
  - Agent Marketing Essentials, «migliori scuole online» (2.638 parole): classifica senza il dato ufficiale.
  - Champions School: pagina dei tassi 404.
  - **Cosa manca a tutti:** la tabella ufficiale delle scuole di uno Stato, con periodo, numero di esami e fonte, accanto ai passi e ai costi della licenza. È un vuoto vero, almeno nei 4 Stati letti.
- **Conto centrale a 36 mesi.** 300.000 ricerche × 0,3 % = 900 visite al mese × 0,4 % di vendite × 50 € medi (15 % di ~480 $ con Aceable, fino a 60 $ con Colibri) × 12 = ~2.150 €. Pubblicità ~50 €. Insegnanti ~600 € (cifra di terzi, come la notte). **Totale ~2.800 €.** Prudente 200 (300 visite, 0,2 %). Ottimista 15.000 (2.700 visite, 0,6 %, scaglione al 20 %).
- **Ore.** 70 per 50 Stati; **prova 14 ore** su 4 Stati dentro un sito esistente (stesso modello «per Stato» di Statute Limits). Attesa della prova: ~35.000 ricerche con la coda × 0,5 % = 175 visite al mese, ~0,7 vendite al mese, ~500 €/anno.
- **Rischi.** Ammissione di un editore italiano non scritta (si vede alla domanda). Le scuole con pochi esami hanno percentuali che non dicono niente: mostrare sempre il numero di esami. Il dato del Texas cambia una volta l'anno: basta un controllo automatico della data nel file.
- **Azione di Massimiliano.** Domanda di affiliazione ad Aceable (modulo sulla pagina, 10 minuti), solo dopo le prime 300 visite al mese.

### B. Autotrasporto USA: scadenze, tariffe e carta carburante — voto 5, RISERVA con prova

- **Cosa era bloccato.** Voto 3,5 perché «nessun compenso scritto; si riapre con una cifra ≥ 50 $ da carte carburante o factoring». FMCSA 403.
- **Via nuova per il pagatore.** Le pagine pubbliche del mercato PartnerStack (`market.partnerstack.com/page/<programma>`, 200) scrivono l'offerta:
  - **Coast** (carta carburante per flotte, rete Visa): «Get $300 Per Approved Application»; scaglioni 400 e 500 $ dopo i primi 10 clienti. Termini ufficiali letti (`coastpay.com/affiliate-terms/`): il compenso scatta quando il cliente è approvato per la carta; vietata la pubblicità a pagamento sui motori di ricerca; i siti vanno dichiarati nella domanda. Dato pubblico della rete: 6,3 % di chi clicca compila la domanda.
  - **Motive** (registratore elettronico delle ore di guida): 150 $ a cliente pagante oppure 10 % del contratto annuo.
  - Altri letti: Truckstop 10-20 % (borsa carichi; 100 $ al primo carico con factoring), Alvys 250 $ a dimostrazione fatta + 300 $ a cliente (software per aziende di trasporto, compratore raro).
- **Via nuova per il dato.** `data.transportation.gov` (portale aperto, 200): 144 archivi FMCSA aggiornati ogni giorno (censimento dei vettori, autorizzazioni, BOC-3, assicurazioni, revoche). Attenzione: il censimento contiene nomi e indirizzi di padroncini, cioè persone: **non si pubblicano schede per vettore**. Servono solo regole, scadenze e tariffe (matrice IFTA, piano UCR, IRS modello 2290: già 200).
- **Domanda misurata.** Lato adempimenti: «ucr registration», «form 2290», «mcs-150», «dot number» 14.800 l'una a 10-18 $, «ifta» 12.100 a 9,6 $, «drug and alcohol clearinghouse» 9.900, «usdot number» 8.100 a 13 $, «boc-3» 4.400, «irp registration» 3.600, «ifta sticker» e «apportioned plates» 2.900: ~150.000 con quelle della notte. Lato acquisto: «fleet fuel cards» 5.400 a **100,7 $**, «fuel card» 3.600 a 67,9 $, «business fuel cards» 3.600 a 82 $, «fuel card for truckers» 2.900 a 26 $ e «fuel cards for truckers» 2.400 a 47 $, «eld for trucks» 4.400 e «eld devices» 2.900 a 25 $, «truck factoring companies» 2.900 a 86 $: ~32.000. «safer fmcsa» 22.200 e «dot number lookup» 12.100 sono ricerche del servizio ufficiale: non contate.
- **Concorrenti letti (5 pagine sull'UCR 2027).** Simplex Group (2.774 parole, tabella delle tariffe), Foley (2.633 parole, cita il Federal Register), Beancount (2.127 parole, 32 cifre), piano UCR ufficiale (200); otrucking.com 403. Le guide ci sono e sono complete: **nessun vuoto**, è quota. Nessuna delle quattro lette parla di carte carburante.
- **Conto centrale a 36 mesi.** Adempimenti: 150.000 × 0,4 % = 600 visite al mese, 2 % clicca il riquadro. Acquisto: 32.000 × 0,25 % = 80 visite, 15 % clicca. In tutto 24 clic al mese × 6,3 % di domande (dato PartnerStack) × 25 % di approvate (mia ipotesi) = 0,38 clienti al mese × 300 $ × 0,92 × 12 = ~1.250 €. Motive ~100 €. Pubblicità ~60 €. **Totale ~1.400 €.** Prudente 150. Ottimista 9.000 (visite triple, scaglione 500 $).
- **Ore.** 40 (+10 l'anno per tariffe e scadenze). Prova: 12 ore (6 pagine di scadenze con calcolo della tariffa + 1 pagina di confronto delle carte carburante dai listini ufficiali).
- **Rischi.** Chi cerca gli adempimenti è spesso un padroncino con un camion solo: Coast serve le flotte e può non approvarlo (è il punto più debole del conto). Ammissione di un editore italiano non scritta. Serve un sito nuovo o una sezione: non abbiamo un sito sul tema.
- **Esito.** RISERVA con prova, dietro alle prove già decise (paghe, LLC). Sale da NO perché ora il pagatore è scritto.

### C. Prezzo della luce ora per ora in Spagna — voto 4,5, riserva sbloccata a metà

- **Cosa era bloccato.** Il PVPC (prezzo regolato che la gente paga): `apidatos.ree.es`, `api.esios.ree.es`, `ree.es` davano 403.
- **Via nuova.** Il file pubblico ufficiale del PVPC, senza chiave: `api.esios.ree.es/archives/70/download_json?locale=es&date=AAAA-MM-GG`. Risposta **200** con le 24 ore (prezzo per Penisola e per Ceuta e Melilla, più le componenti). Letti il 13/11/2026 e il 14/11/2025 interi, e il 14/11/2026 (ore 00-01: 227,26 €/MWh). Controllo incrociato: tarifaluzhora.es scrive per la stessa ora 0,2273 €/kWh: **il dato coincide**.
  - **Limite:** lo stesso indirizzo ha risposto 200 nove volte e 403 otto volte su 17 richieste in mezz'ora (protezione anti-bot a monte). Non è stato aggirato niente: stesse richieste, stesso programma. Per il giorno dopo, di mattina, il file risponde «No values for specified archive»: i prezzi di domani escono la sera.
  - **Riserve lette:** OMIE (prezzo all'ingrosso, 200 già il 13/11) ed `api.energy-charts.info/price?bzn=ES` (istituto Fraunhofer, 200): danno l'ingrosso, non il PVPC. La API ESIOS con chiave personale gratuita esiste ma passa dallo stesso blocco. `apidatos.ree.es` resta 403.
  - **Licenza:** le condizioni d'uso di ESIOS stanno in una pagina in JavaScript, non lette. L'avviso legale di ree.es (200) riserva i diritti sul sito. I prezzi sono fatti pubblici e tutti i concorrenti li ripubblicano, ma la frase di riuso non l'ho letta: va letta dal browser prima di costruire.
- **Domanda misurata (es).** Confermata: «precio luz hoy» 1.000.000 a 1,26 €, «tarifa luz hoy» 301.000, «precio luz mañana» 201.000 a 2,57 €, «precio de la luz mañana» 90.500 a 6,72 €, «precio luz hoy por horas» 74.000, «precio luz hora» 22.200, «pvpc hoy» 14.800, «precio kwh hoy» 9.900, «horas baratas luz hoy» 5.400, «precio luz hoy canarias» 2.900. Lato acquisto: «comparador tarifas luz» 18.100 a 4,8 €, «comparador luz» 14.800 a 6,4 €.
- **Concorrenti letti.** tarifaluzhora.es (gruppo Selectra): 2.932 parole, tabella delle 24 ore aggiornata oggi, pagina di domani, 11 numeri di telefono per vendere contratti: **completo**. Papernest: 1.902 parole, 39 numeri di telefono, niente tabella oraria nella pagina scaricata. loentiendo.com: 1.566 parole, pochi prezzi. Repsol: tabella «no disponible» secondo la ricerca. Rastreator 403. I giornali ripubblicano ogni giorno. **Nessun vuoto: è quota (3 % o meno).**
- **Pagatore.** Solo pubblicità. Nessun programma spagnolo con cifra letta (pagine di affiliazione di Selectra 404 e di Papernest 403).
- **Conto.** Resta quello del 13/11: 95 / 560 / 2.250 €/anno. Ore 27 (25 + 2 per i tentativi ripetuti e la riserva OMIE). 21 €/ora.
- **Esito.** Non è più «bloccata dal dato», ma non sale: il limite adesso è il guadagno (clic da 1-2 €, concorrente completo), non la fonte. **Prova di 1 ora**: leggere il file per 7 giorni dal posto dove girano gli aggiornamenti automatici e contare le risposte buone. Si costruisce solo se risponde almeno 9 volte su 10 con tre tentativi distanziati, e solo come sezione di un sito in spagnolo che ancora non abbiamo.

### D. Lemon law per Stato — verifica chiusa, riserva bassa

- **Dubbio da chiudere.** La riga senza numero diceva «da rifare: la stima del 13/11 contava solo le frasi informative».
- **Misura.** «lemon law <Stato>» su tutti i 50 Stati: **131.870 al mese** (California 14.800 a 54 $, Texas 12.100, Florida 9.900, New Jersey e Georgia 5.400, Pennsylvania, Ohio, New York, Michigan 4.400). In più: «lemon law used cars» 8.100, «what is the lemon law» 8.100, «does lemon law apply to used cars» 3.600, «lemon law buyback» 1.600. Totale usabile ~155.000. Non contate: «lemon law» 60.500 (generica) e «lemon law lawyer/attorney» 27.100 a 84 $ (cerca un avvocato).
- **Esito.** Il file del 13/11 usava già ~145.000 con le teste: **il conto era giusto**. Con 155.000 × 0,35 % = 540 visite al mese × 25 $ ogni 1.000 pagine: ~190 €/anno centrali, 30 ore, 6 €/ora. Nessun pagatore oltre la pubblicità (i contatti per avvocati non sono per noi). Resta la prova di 8 ore solo se Statute Limits prende impressioni.

### E. Calendario dei pagamenti di pensioni e sussidi (USA e Canada) — NO confermato

- **Vie provate.** ssa.gov 403 su pagina, PDF del calendario 2026 e 2027 e blog; opm.gov 403; canada.ca non risponde dal contenitore (nessuna pagina del dominio); portale dati aperti canadese 200 ma senza un archivio delle date. L'archivio web ha copie del 20/10/2026 del calendario SSA 2027 e del calendario canadese (stato 200 nell'indice), ma dal contenitore lo scarico delle copie non passa: **via esistente, non letta**. Le date USA si calcolano dalla regola (giorno di nascita → secondo, terzo, quarto mercoledì). va.gov risponde 200 (tabelle dei compensi per invalidità).
- **Perché resta NO.** Il motivo vero non era la fonte: risposta di una riga che Google mostra da sola, primi posti agli enti e ai giornali, solo pubblicità. Centrale 150 €/anno, 7,5 €/ora.

### F. Compensi «non letti»

- **Gusto:** letto nei dati pubblici PartnerStack: 300 $ al primo cliente che fa una busta paga, poi 400, 500, 700, 1.000 $ dal quinto. Termini (`gusto.com/legal/terms/partnerstack-terms`): 403; copia d'archivio del 28/2/2026 esiste ma non si scarica da qui. **Paesi ammessi: ancora non letti.** Si vede alla domanda su PartnerStack (gratis, 10 minuti).
- **ADP (RUN):** contratto ufficiale letto (PDF di 13 pagine, versione 1/8/2025): 500 $ a cliente per i primi 4, 750 $ da 5 a 9, 1.000 $ da 10 in su; pagamento a 45 giorni; fino al 31/1/2027 premio doppio. Vale solo per clienti negli Stati Uniti; nessuna clausola letta sulla residenza del partner.
- **Next Insurance:** la pagina ufficiale non scrive cifre; l'iscrizione passa da Impact (login). «25 $ a preventivo» resta di terzi. Riga 89 invariata.
- **The CE Shop:** pagina ufficiale del programma letta, nessuna cifra. **360training:** 20-45 % solo con negozio in concessione, costo d'ingresso e impegno annuo. Tutti e due fuori dai conti.
- **LegalZoom, Rocket Lawyer:** pagine di affiliazione 302, 410, 404. Riga 40 invariata.
- **Migration Expert:** 20 % confermato sulla pagina ufficiale; parcella media ancora non trovata (pagina delle tariffe 404). Riga 87 invariata.

### G. Heat Pump Grants UK

Riprovati i concorrenti non letti l'11/11: Energy Saving Trust e Heatable 403; GreenMatch e Octopus restituiscono pagine vuote senza JavaScript (8-10 parole). Nessuna via diversa. La scheda pubblica Awin di Glow Green (200) non scrive ancora i Paesi degli editori ammessi. Niente cambia: il sito è online, la domanda Awin resta di Massimiliano.

## 4. Scoperte utili per i prossimi giri

1. **Le pagine in JavaScript spesso caricano un file pubblico.** Prima di scrivere «non letta», cercare nel codice della pagina l'indirizzo del file (`.json`, `.csv`) che la tabella scarica. Con Texas ha funzionato in due minuti.
2. **Il mercato pubblico di PartnerStack contiene i dati di 424 programmi** (offerta, scaglioni, quota di iscrizioni per clic) nella pagina `market.partnerstack.com/<categoria>`, senza login. Programmi con cifra ≥ 50 $ non ancora in classifica, da usare come semi nel prossimo giro «prima chi paga»: Coast 300 $, Motive 150 $, Forwardly fino a 1.000 $ per azienda USA, Melio 400 $ al primo pagamento, Airwallex fino a 400 $, Shopmonkey 300 $ a dimostrazione (officine), Thryv 250 $, TaxCycle 250 $, Alvys 250 + 300 $, Aircall 75 $ a contatto, Shippo 60 $.
3. **Portali di dati aperti come pagina gemella degli enti che danno 403:** `data.transportation.gov` per FMCSA, `data.texas.gov` per TREC (licenze, non i tassi), `oui.doleta.gov` (PDF federale con il sussidio di disoccupazione massimo di tutti gli Stati, 200: sostituisce le pagine statali 403; l'idea resta NO per la domanda).
4. **Le copie d'archivio** delle pagine ufficiali bloccate esistono quasi sempre, ma da questo contenitore non si scaricano: da leggere dal browser quando serve una frase precisa (termini Gusto, calendario SSA).

## 5. Cosa NON ho potuto leggere

- Tassi per scuola di North Carolina, Colorado, Kansas (403), Washington e Arizona (404 dagli indirizzi trovati).
- Condizioni d'uso dei dati ESIOS; il file PVPC del giorno dopo; l'affidabilità del file dal posto degli aggiornamenti automatici.
- Paesi ammessi da Gusto, Coast, Motive, Aceable per l'editore; compenso di Next Insurance e The CE Shop.
- Quota di domande Coast che viene approvata (usato 25 %: ipotesi mia, non un dato).
