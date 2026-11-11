# Verifica indipendente: sito inglese sul "Warm Homes Plan" (prestiti + contributi per council), 11/11/2026

Idee 1 e 2 di `fronti-2026-11-11-casa-uk.md` (voto del ricercatore 6 e 5; insieme 140 / 2.150 / 19.800 €/anno, 30-40 ore). Tutto riletto oggi con curl dal server; dove un dato viene dalla ricerca web o non è stato letto, è scritto. Cambio 1 £ = 1,15 €.

## 1. Verdetto

- **SITO NUOVO: NO-GO.** Passano 2 prove su 4. Va in "Riserva costruibile", non in coda.
- **Voto: 4** (era 6 e 5).
- **Stima rifatta: 45 / 470 / 8.200 €/anno a 18 mesi** (era 140 / 2.150 / 19.800), 30-40 ore più una rilettura mensile: circa 13 € centrali per ora.
- **Due motivi, ognuno basta da solo:**
  1. **Legge.** Una tabella che confronta finanziatori e manda il lettore alle loro pagine è, per l'autorità britannica (FCA), "presentare un cliente a un finanziatore": serve l'autorizzazione anche **senza compenso dal finanziatore**. L'idea del ricercatore ("niente soldi dai finanziatori, quindi siamo fuori") non regge (sezione 2).
  2. **Dati.** I tassi non ci sono: **solo 3 finanziatori su 10 scrivono un tasso**. Sei su dieci non accettano domande dal pubblico: il prestito si chiede all'installatore, e il tasso lo dà l'installatore. La tabella "10 finanziatori a confronto" non si può riempire, né oggi né con più lavoro (sezione 3). Il ricercatore aveva scritto la soglia: "se meno di 7 su 10 pubblicano il tasso, la tabella perde valore".
- **Rischio più grande:** quello legale. Esercitare un'attività regolata senza autorizzazione nel Regno Unito è reato (art. 19 della legge sui servizi finanziari, citato nella nota ufficiale all'ordinanza letta oggi). Non si rischia per 470 € l'anno.
- **Cosa resta di buono:** il pagatore. Glow Green e BOXT su Awin hanno la cifra scritta (riletta oggi) e valgono per pagine sugli **impianti** (prezzi, Boiler Upgrade Scheme), non sui prestiti.

## 2. Valutazione legale (intermediazione del credito)

Letto oggi:
- **Ordinanza sulle attività regolate (SI 2001/544), art. 36A**, da legislation.gov.uk (200). È attività di intermediazione del credito, fra le altre: (a) "effecting an introduction", cioè presentare a un finanziatore una persona che vuole un prestito; (c) presentarla a **chi fa a sua volta intermediazione** (per esempio un installatore che propone il finanziamento).
- **Art. 36C** (200): l'esclusione "nessun compenso" vale **solo per le lettere (d), (e), (f)** (offrire il contratto, lavoro preparatorio, firmare per conto del finanziatore). **Non vale per le presentazioni (a)-(c).**
- **FCA, Policy Statement PS15/23** (PDF, 200), risposta a chi chiedeva di escludere le segnalazioni non pagate: "effecting an introduction to a lender or broker will require permission if they are undertaken by way of business. Receipt of a fee or commission is not a necessary element of the 'by way of business' test."
- **Manuale FCA (PERG 2.7.7E, CONC, SUP 16 allegato 38D): non letto.** Il sito del manuale è un'applicazione che curl non legge. Dalla ricerca web (riassunto, non letto da me): l'allegato 38D porta come esempio di intermediazione "un sito di confronto prezzi che presenta clienti a finanziatori terzi, **che guadagni o no un compenso**".

Applicazione al nostro caso:
- Il sito sarebbe un'attività ("by way of business"): pubblicità e commissioni dagli installatori. Che i soldi non arrivino dai finanziatori non cambia la lettura.
- Peggio: i pagatori (Glow Green: "set up finance" nella scheda Awin; E.ON; BOXT) propongono loro stessi il finanziamento. Un link affiliato a un installatore, dentro una pagina sui prestiti, è una presentazione a un intermediario (lettera c) **pagata a commissione**.
- C'è anche il divieto di "financial promotion" (art. 21 della stessa legge): invitare a prendere un prestito, da parte di chi non è autorizzato, richiede l'approvazione di un soggetto autorizzato. Regola nota, non riletta oggi.
- Uswitch, che ha la guida sul tema, è un intermediario autorizzato. FMB e Homebuilding elencano i nomi senza tassi e senza confronto: è il formato giornalistico, l'unico prudente.
- Essere in Italia non mette al riparo: il sito sarebbe rivolto a consumatori britannici.

**Disegno prudente (l'unico con cui si potrebbe riaprire):** pagina informativa, non comparatore. Nomi dei finanziatori come testo, con il solo link all'elenco di GOV.UK; nessun link alle pagine dei finanziatori; nessuna classifica, nessun "migliore", nessun "richiedi"; cifre solo come citazione datata della fonte; calcolatore di rata generico (formula, senza nomi); **nessun link affiliato nelle pagine sui prestiti**; link agli installatori solo nelle pagine sugli impianti, con la frase "preventivo", mai "finanziamento". Anche così il rischio non è zero (serve un parere scritto), e così il sito perde proprio ciò che lo distingueva.

## 3. Dati

### Prestiti: i 10 finanziatori (GOV.UK, guida del 28/10/2026, 200, licenza OGL)
GOV.UK elenca i nomi **senza link** e scrive di contattarli per tassi e durate. Pagine dei finanziatori lette oggi:

| Finanziatore | Pagina (stato) | Domanda diretta del pubblico? | Tasso scritto? |
|---|---|---|---|
| South Manchester Credit Union | /warm-homes-loan/ (200) | sì | **sì**: 1.000-15.000 £, "from 3.6% APR", esempi a 3,6 % e 9,4 %, 3-10 anni |
| Sunsave Energy | pagina guida (200) | sì, ma solo sui suoi impianti | **sì**: esempio 0 % su 36 rate; fuori schema 8,9 % TAEG |
| HomeServe Finance | homeservefinance.com (200) | no: finanziamento al punto vendita | solo tramite E.ON: "up to 5 years 0% APR" (eonnext.com/solar-panels, 200) |
| Tandem Bank | /borrow/warm-homes-loan-scheme (200) | **no**: "customers cannot apply directly to Tandem" | no |
| Secure Trust Bank (V12) | /retail-finance/warm-homes-loan-scheme (200) | **no**: solo tramite rivenditori | no |
| Selina Finance | guida per proprietari (200) | **no**: si parte dalla proposta dell'installatore | no (il campo del tasso è un segnaposto vuoto nella pagina); durata 5 anni, penali di estinzione 5-1 % |
| thisbank | /loans (200) | **no**: "you can't apply for a loan directly through us" | no |
| Propensio | whls.propensio.co.uk (200) | no: lo strumento è per gli installatori | no |
| Hometree Finance | hometreefinance.co.uk (200) | non detto | no |
| The Money Co-op | 4 indirizzi provati, nessuna risposta | non letto | non letto |

**Risultato: 9 siti leggibili su 10, tasso scritto per 3 su 10.** Per 6 il tasso non è un dato pubblico: lo decide l'accordo fra finanziatore e installatore. Il lettore, in pratica, sceglie l'installatore, non il finanziatore.

### Contributi per council (Warm Homes: Local Grant)
- Elenco dei council finanziati: pagina GOV.UK, aggiornata il 2/7/2026 (200, OGL).
- Codici postali idonei: xlsx di 4,2 MB, "updated February 2026" (200, OGL). Aggiornamenti visti: ottobre e novembre 2024, febbraio 2026: circa una volta l'anno.
- **Il controllo ufficiale esiste già:** GOV.UK "Check your eligibility and apply" chiede il codice postale, verifica e passa la domanda al council, che richiama entro 10 giorni lavorativi. Un nostro controllo farebbe meno (non può inoltrare la domanda) con dati vecchi fino a un anno.
- Manca nei file ciò che il lettore vuole sapere: se nel suo council le domande sono aperte e chi fa i lavori.

## 4. Concorrenti (letti oggi)

5 finanziatori: HomeServe/E.ON, South Manchester CU, Sunsave, Tandem, Hometree. 5 council: Birmingham, Cornwall, Leeds, Nottingham, Blackpool.

| Concorrente | Pagina e data | Finanziatori nominati | Tassi per finanziatore | Council nominati su 5 |
|---|---|---|---|---|
| MoneySavingExpert, prestiti | notizia del 26/10/2026 (200) | 9 su 10 | 0 su 5 (solo "5,9 % i prestiti normali più economici") | 0 |
| MoneySavingExpert, contributi | guida aggiornata il **9/11/2026** (200) | – | – | 0 (rimanda al controllo ufficiale) |
| Uswitch, prestiti | guida del 30/10/2026 (200) | 10 su 10 | 0 su 5 | 0 |
| Uswitch, contributi | guida del 23/10/2025 (200) | – | – | 0 |
| FMB | 3/11/2026 (200) | 10 su 10 | 0 su 5 | 0 |
| Sunsave | guida del 25/9/2026 (200) | 9 su 10 | 1 su 5 (il suo) | 0 |
| The Eco Experts, contributi | guida del 18/2/2026 (200) | – | – | **3 su 5** |
| Which? | indirizzi provati 404: non letto | – | – | – |
| Energy Saving Trust, Heatable, Selectra | 403 (protezione anti-bot, non aggirata); le loro guide esistono (ricerca web) | – | – | – |

Lettura: nessuno ha la tabella dei tassi, **perché i tassi non sono pubblici**, non perché nessuno ci ha pensato. Le parole principali sono già prese da GOV.UK, MoneySavingExpert, Uswitch, Sunsave, Energy Saving Trust, Heatable, FMB. Sui contributi: il council risponde sul proprio nome, GOV.UK ha il controllo, MoneySavingExpert ha aggiornato la guida due giorni fa.

## 5. Domanda (autocomplete Google, gl=gb, oggi)

| Ricerca | Suggerimenti |
|---|---|
| warm homes loan scheme | 10 (lenders, rules, launch date) |
| warm homes loan scheme lenders | 5 (list, **portal, handbook**) |
| warm homes loan scheme interest rate | 1 (stamattina 0) |
| tandem / eon / sunsave / south manchester credit union + warm homes loan | 3 / 3 / 2 / 2 (quasi tutti "portal" e "loans") |
| selina, propensio + warm homes | 1 ciascuno |
| warm homes loan calculator | 0 |
| warm homes local grant | 10 (eligibility, eligible postcodes, Birmingham, Liverpool) |
| warm homes local grant postcode checker | 4 (uno è "uk gov") |
| warm homes plan | 10 |

La domanda c'è e cresce (i nomi dei finanziatori stamattina davano 0). Ma "portal" e "handbook" sono ricerche di installatori, non di famiglie. Volumi non misurabili da qui: la stima sotto è una quota ipotizzata, non un conteggio.

## 6. Chi paga (schede pubbliche Awin, rilette oggi, 200)

| Programma | Cifra | Note |
|---|---|---|
| Glow Green (73922) | 300 £ solare, 250 £ pompa di calore, 100 £ caldaia, 50 £ batteria, 25 £ climatizzatore, 10 £ colonnina | confermato. Nella scheda: già partner di MoneySuperMarket e Uswitch. Conversione, EPC, zone e accettazione di editori non britannici: **non visibili** |
| BOXT (13574) | 35 £ a vendita completata | confermato; niente pubblicità "native" |
| Heatable (18758) | "industry high", nessuna cifra | non conta |
| OVO Solar & Heating (122556), EDF Zero Carbon Homes (129571) | cifra non visibile | da leggere dal pannello Awin |
| Octopus, Sunsave | nessun programma per editori letto | non contati |

AdSense Regno Unito: ipotesi 8-14 € per 1.000 visite (casa e finanza), non misurata.

**Formula** (pagine prestiti in forma prudente, più pagine contributi): visite × clic verso l'installatore × vendita × 230 € + visite × RPM.
- **Prudente:** prestiti 2.000 × 2 % × 0,15 % × 230 = 1 € + 16 € di pubblicità; contributi 4.000 × 6 € = 24 € → **~45 €**
- **Centrale:** prestiti 10.000 × 3 % × 0,3 % × 230 = 207 € + 100 €; contributi 20.000 × 8 € = 160 € → **~470 €**
- **Ottimista:** prestiti 60.000 × 5 % × 0,8 % × 230 = 5.520 € + 840 €; contributi 150.000 × 12 € = 1.800 € → **~8.200 €**

Visite ridotte a un terzo rispetto al ricercatore: senza tabella dei tassi e senza link ai finanziatori la pagina è una guida come le sette già online, su un dominio nuovo e su un tema di soldi.

## 7. Le 4 prove

| Prova | Esito |
|---|---|
| Domanda | **sì**, in crescita |
| Dati leggibili | **no** per i prestiti (3 tassi su 10); sì per i contributi |
| Pagatore che possiamo usare | **sì con riserva**: cifre confermate, ma non utilizzabili accanto ai prestiti; accettazione da chiedere |
| Nessuno lo fa già meglio | **no**: per i contributi c'è il controllo ufficiale; per i prestiti il vuoto è un dato che non esiste |

**2 su 4.**

## 8. Quando riaprire

Tutte e tre insieme:
1. almeno 7 finanziatori su 10 pubblicano tasso e durata e accettano domande dirette (GOV.UK annuncia "altri finanziatori e prodotti in arrivo": rileggere a febbraio 2027);
2. un parere scritto (o una pagina del manuale FCA letta per intero) che il formato informativo senza link resta fuori dall'intermediazione;
3. l'approvazione di Glow Green per il nostro conto Awin.

Da tenere comunque: per ogni futura pagina su caldaie, solare o pompe di calore nel Regno Unito il pagatore con cifra esiste (Glow Green, BOXT), purché la pagina parli dell'impianto e non del prestito.

## 9. Dominio (solo per memoria)

Controllo sul registro .com: warmhomesloans.com e warmhomescheck.com già presi (200); warmhomesplanguide.com, warmhomesdata.com, warmhomesfinder.com liberi (404). I .co.uk non sono stati controllati.

## 10. Indirizzi letti

gov.uk/api/content/warm-homes-loan-scheme, /apply-warm-homes-local-grant, /government/publications/warm-homes-local-grant, /government/publications/warm-homes-local-grant-successful-local-authorities; legislation.gov.uk/uksi/2001/544/article/36A, 36C, 36D, 36G; fca.org.uk/publication/policy/ps15-23.pdf; tandem.co.uk, securetrustbank.com, selinafinance.co.uk, smcreditunion.co.uk, sunsave.energy, homeservefinance.com, eonnext.com/solar-panels, thisbank.co.uk/loans, hometreefinance.co.uk, propensio.co.uk e whls.propensio.co.uk; moneysavingexpert.com (notizia e guida), uswitch.com (due guide), fmb.org.uk, theecoexperts.co.uk; ui.awin.com/merchant-profile/73922, 13574, 18758, 122556, 129571; rdap.verisign.com (200 salvo dove scritto). Non letti: handbook.fca.org.uk (applicazione), The Money Co-op (nessuna risposta), Which? (404), energysavingtrust.org.uk, heatable.co.uk, selectra.co.uk (403, non aggirati).
