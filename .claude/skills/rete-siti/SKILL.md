---
name: rete-siti
description: Metodo da manager per la rete di siti di Massimiliano (Italy Strikes, Tourist Tax, Visa Income, Before You Fly, EsameB1, EsamiDiStato e i siti futuri). Usare per la revisione settimanale, per decidere cosa spingere, migliorare, congelare o aggiungere, per aggiornare il cruscotto e per ogni domanda su "come vanno i siti" o "funziona il piano".
---

# Gestione della rete di siti (metodo da manager)

Massimiliano ha chiesto (11/10/2026): "gestirli con una strategia gestita bene, da manager. Questa è una cosa di cui ti devi occupare tu: portare sempre idee nuove, togliere quello che non funziona e aggiungere cose che funzionano."

Scrivi sempre in italiano semplice: Massimiliano non è tecnico. Frasi brevi, numeri chiari, nessun gergo.

## 0. Prima di tutto
Leggi, in quest'ordine:
1. `studio-business/CRUSCOTTO-RETE.md`: stato di ogni sito, numeri, decisioni in corso. **È la memoria della rete**: ciò che non c'è scritto lì non esiste per la sessione dopo.
2. `studio-business/STRATEGIA.md`: direzione, cancello fiscale (sez. 10), piano di crescita (sez. 11).
3. `studio-business/REGOLE-FISSE.md`: regole di Massimiliano e standard di qualità.

## 1. Regole fisse (non si cambiano a metà)
- **Si decide con i numeri, mai a sensazione.** Ogni proposta cita il numero che la giustifica. Se il numero non c'è, si dice "non lo so ancora" e si spiega come ottenerlo. Mai presentare una stima come un dato.
- **Zero spese senza il sì di Massimiliano.** Niente email a freddo, niente social, niente dati personali nel repository, nessun nome di modello AI nei file. Niente vendite dirette finché il cancello fiscale è chiuso (STRATEGIA sez. 10).
- **Crediti Netlify:** i siti condividono i crediti del team. L'11/10/2026, 5 deploy ravvicinati hanno bloccato tutti i siti (503 `usage_exceeded`). Le modifiche escono con le pubblicazioni già previste (lunedì per gli esami, settimanale per Italy Strikes). Nessun deploy extra senza aver visto i consumi.
- **Qualità prima di pubblicare** (REGOLE-FISSE): revisore indipendente dei fatti, poi revisore di design con voto minimo 8/10.
- **Il tempo va dove ci sono i numeri.** Prima si migliora ciò che mostra segnali, poi si costruisce il nuovo. Le idee nuove a costo zero si costruiscono comunque (regola di Massimiliano del 10/10: "il gol è guadagnare"), ma ognuna entra nel cruscotto con data e soglia.

## 2. Come si misura (il punto debole: va risolto)
Senza numeri non si gestisce. Fonti, dalla migliore:
1. **GoatCounter** (contatore gratuito senza cookie): attivo. Account `rete-siti` creato da Massimiliano il 17/10/2026; script in tutti i 10 siti (costante `SCRIPT_CONTATORE` in ogni `genera.py`, in ogni pagina generata, 404 comprese) e privacy aggiornata in ogni sito. Cruscotto: https://rete-siti.goatcounter.com (solo Massimiliano ha l'accesso). Un solo account per tutti i siti: il percorso registrato comprende l'host (es. `esameb1.netlify.app/costo/`), quindi per vedere un sito si scrive il suo host nella ricerca dei percorsi ("Paths"); le prove in locale non contano. **Lettura dalle routine: attiva dal 17/10/2026.** La chiave in sola lettura (permessi Read statistics + Read sites) è un **segreto di rete** dell'ambiente Default, tipo Bearer, per l'host `rete-siti.goatcounter.com` e i percorsi `/api/`: il sistema la aggiunge da solo alle richieste, quindi NON si manda l'intestazione Authorization e non serve nessuna variabile. Provato il 17/10: visita vera di Massimiliano da Firefox registrata come `/esameb1.netlify.app` (GoatCounter mette una `/` davanti all'host). Chiamate: `curl -s -H 'Content-Type: application/json' 'https://rete-siti.goatcounter.com/api/v0/stats/total?start=AAAA-MM-GGT00:00:00Z&end=AAAA-MM-GGT23:00:00Z'` (visite totali; le date vanno con l'ora, altrimenti risponde "not found"), `.../api/v0/stats/hits?start=...&end=...&limit=100` (visite per pagina: righe con `path` e `count`; i numeri di un sito sono la somma delle righe il cui `path` inizia con `/<host>`; `more` = altre pagine) e `.../api/v0/paths?limit=100` (tutti i percorsi visti). Riferimento: https://www.goatcounter.com/help/api; limite 4 richieste al secondo; 401 = segreto mancante. Le visite dei browser automatici (Playwright, robot) non vengono contate: per provare il contatore serve un browser vero. Chi usa un blocco della pubblicità può non essere contato: GoatCounter conta un po' meno visite di quelle reali; Search Console resta la fonte per impressioni e clic.
2. **Google Search Console**: impressioni, clic, pagine indicizzate. Solo Massimiliano lo vede. Quando manca il contatore, chiedigli una foto della pagina "Rendimento" e della pagina "Pagine" di ogni sito **ogni 2 settimane**. Trascrivi i numeri nel cruscotto con la data.
3. **Gmail di Massimiliano** (se la sessione ha il connettore Gmail): cerca le email di Search Console (`from:sc-noreply@google.com`: primi dati di impressioni, problemi di indicizzazione o di dati strutturati) e dei programmi di affiliazione (approvazioni, rifiuti, pagamenti). Solo lettura: mai rispondere o inviare email.
4. **Moduli Netlify** (iscrizioni "avvisami"/"alerts"): `get-forms-for-project` del Netlify MCP, se la sessione ce l'ha. Le iscrizioni del 9/10 sono test di Claude, non contano.
5. **Controlli tecnici** che fai sempre da solo: home 200, sitemap 200, una pagina campione 200, dati aggiornati (per Italy Strikes `italystrikes/dati/vista.json` e il workflow su GitHub Actions).

Se un numero manca, scrivi "manca" nel cruscotto. Non inventare e non stimare al posto del dato.

## 3. Fasi e soglie di ogni sito (giorni dalla pubblicazione)
| Fase | Quando | Cosa si guarda | Decisione |
|---|---|---|---|
| Avvio | 0-30 | Search Console: sitemap letta, prime pagine indicizzate | Se a 21 giorni 0 pagine indicizzate: controllo tecnico (robots, sitemap, canonical) |
| Primo segnale | 30-45 | Impressioni al mese | ≥ 300: **continua**. 1-299: **un giro di miglioramenti** (titoli, descrizioni, pagine che rispondono alle ricerche viste in Search Console). 0: controllo tecnico e giro di miglioramenti |
| Verdetto | 90 | Impressioni e clic al mese | < 1.000 impressioni: **congelato** (resta online, costa zero, niente più lavoro; motivo scritto nel cruscotto). ≥ 1.000: **continua** |
| Spinta | quando > 1.000 visite al mese | Visite, pagine più viste | **Spingi**: richiesta AdSense, più pagine dove già c'è traffico, altre lingue, link affiliati |
| Ricavi | 1.000 sessioni Tier 1 in 30 giorni | Sessioni | Richiesta Mediavine Journey |

Eccezione: un sito stagionale (per esempio Italy Strikes ha il picco a marzo) si giudica anche sul periodo giusto. Scrivilo nel cruscotto prima del verdetto, non dopo.

## 4. Il ritmo
- **Ogni mercoledì** (routine "Ricerca settimanale"): prima la revisione della rete, poi la ricerca di idee nuove.
  1. Controlli tecnici di tutti i siti (sez. 2.5).
  2. Leggi i numeri disponibili e aggiorna il cruscotto (data, fonte di ogni numero).
  3. Applica le soglie della sez. 3 a ogni sito e scrivi la decisione.
  4. Scegli **una sola azione** più utile della settimana (quella con più guadagno atteso per ora di lavoro) e scrivila in "Prossime azioni".
  5. Se mancano i numeri da 2 settimane, il messaggio a Massimiliano lo chiede, con l'istruzione precisa.
- **Ogni 2 settimane**: Massimiliano manda le foto di Search Console, finché non c'è il contatore.
- **Ogni mese**: si toglie o si congela almeno una cosa che non va (sito, sezione o idea), oppure si scrive perché non ce n'è nessuna. Si aggiungono 1-2 siti o sezioni dalla classifica (`intelaiatura/19-classifica-mondo.md`) e dalla ricerca del mercoledì.
- **Ogni 3 mesi**: revisione della strategia con i numeri. Le stime di STRATEGIA sez. 6 si rifanno con i dati veri.

**Regola di Massimiliano (14/10/2026): "le idee valgono in tutto il mondo, non solo in Italia" e non deve chiedermele lui.** Le idee nuove si cercano da soli, senza aspettare richieste, ogni giorno (routine serale), in tutto il mondo: prima USA, Regno Unito, Canada, Australia e Europa, poi il resto. L'Italia è solo uno dei Paesi. Ogni idea che passa i controlli entra nella tabella "Idee in cantiere" e gli si scrive solo per le decisioni sì/no.

**Obiettivo dichiarato da Massimiliano (17/10/2026): "il gol è fatturare tanto il prima possibile, e che il fatturato cresca col tempo se possibile."** Due conseguenze: (1) a parità di voto si preferisce l'idea che paga prima (affiliazioni e pubblicità ad alto valore su pubblici USA/UK, stagioni vicine, ondate di ricerche con data) rispetto a quella che paga di più ma tra 18 mesi; (2) ogni proposta indica da quando arrivano i primi soldi, non solo il valore a 18 mesi. Ha chiesto idee da 8-9, non da 6-7: la ricerca profonda del 17/10 (`intelaiatura/idee-grandi-2026-10-17.md`) è il riferimento; se dentro i vincoli non esistono, si dice quale vincolo allentare.

**Regola di Massimiliano (17/10/2026): "puoi trovare di meglio".** A Massimiliano si propongono solo idee con voto ≥ 7 e stima realistica ≥ 5.000 €/anno a 18 mesi (o un potenziale chiaramente più alto). Le idee più piccole si scrivono in ESPLORATE e nel file del giorno, senza messaggio. **Tetto alla rete:** 10 siti (compresi navi da crociera e condomini FHA). Il tetto limita la costruzione di siti nuovi, NON la ricerca: Massimiliano (17/10) "abbiamo 10 siti ma puoi trovare qualsiasi cosa". Le idee non devono essere per forza siti: valgono strumenti, dati, widget, lingue, affiliazioni, prodotti automatici, purché automatici e a costo zero (o con spesa piccola proposta a parte) e senza vendita diretta prima del cancello fiscale; un'idea da 8-9 si costruisce anche oltre il tetto, al posto di un sito congelato o in più. Oltre questo numero si costruisce solo dopo che i primi siti hanno passato i 45 giorni e i numeri dicono dove conviene investire; nel frattempo le idee migliori aspettano in "Idee in cantiere".

**Regola di Massimiliano (30/10/2026): "il mondo è molto più grande… devi impegnarti di più"; "questo è quello che dovevi fare dall'inizio".** La ricerca di idee non si affida a uno o due ricercatori: ogni settimana partono **almeno 4 ricercatori in parallelo**, divisi per zona (USA; Regno Unito e Irlanda; Canada, Australia e Nuova Zelanda; Europa continentale, Golfo e Asia) e per modello che ha funzionato (cloni di EsameB1: passaggi burocratici obbligatori con dati ufficiali per città; numeri ufficiali per nazionalità citati dagli assistenti AI), ognuno con un file proprio in `intelaiatura/`. Le idee da 8 in su passano da un verificatore indipendente; quelle che reggono e costano zero si costruiscono subito, anche oltre il tetto dei 10 siti. Le prove su cui pesare i voti sono i numeri veri della rete, non le stime. **Lo schema è costante** (Massimiliano, 30/10: "tutto questo schema di lavoro deve essere costante"): ogni sera almeno 3 ricercatori a rotazione su zone e settori non coperti nelle sere precedenti (routine serale), ogni mercoledì almeno 4; se un giro trova solo idee da 6-7, il giro dopo cambia angolo invece di ripetere.

**Regola di Massimiliano (30/10/2026): rete fitta di guadagno** ("prendiamo tutto quello che possiamo e la somma di tutte le cose è un numero grande"). Ogni idea automatica, a costo zero e con guadagno atteso positivo si costruisce, anche piccola, preferibilmente come sezione di un sito esistente; l'asticella (voto ≥ 7, ≥ 5.000 €/anno) vale solo per i siti nuovi. Coda di costruzione sempre attiva dalla tabella "Idee in cantiere" (costruttore → revisore → pubblicazione); ogni sezione nasce con AdSense e il link affiliato adatto. Dettagli in `studio-business/REGOLE-FISSE.md`.

**Crediti Netlify (31/10/2026):** ogni pubblicazione costa 15 crediti (1.000 al mese, ciclo 15→14; il 30/10 sono finiti). Massimo una pubblicazione per sito al giorno: le sezioni revisionate si salvano insieme e si spingono con un solo push, di sera. Gli aggiornamenti automatici pubblicano solo se i dati cambiano. Ricariche solo con il sì di Massimiliano. Dettagli in `studio-business/REGOLE-FISSE.md`.

**Regola di Massimiliano (13/10/2026):** "devi trovare sempre nuove idee e portare avanti quelle che sono già in cantiere". Ogni mercoledì si aggiorna la tabella "Idee in cantiere" del cruscotto: ogni idea fa un passo avanti oppure si chiude con il motivo, e se ne aggiunge almeno una nuova.

## 5. Il messaggio a Massimiliano (ogni settimana, 5-8 righe)
1. Come va la rete in una frase (con un numero).
2. Cosa va, cosa non va (un sito per riga, solo quelli con novità).
3. L'azione della settimana e cosa serve da lui (se serve qualcosa, in passi precisi).
4. Le decisioni che spettano a lui (spese, pubblicazioni nuove, chiusure): domanda sì/no.
Niente elenchi lunghi, niente gergo. Se non è cambiato niente, dillo in una riga.

**Delega di Massimiliano (15/10/2026): "tu fai tutto".** Claude porta avanti da solo costruzione, miglioramenti, pubblicazioni previste, ricerca e chiusure, senza chiedere passo per passo. A Massimiliano si chiede solo ciò che richiede il suo account o i suoi soldi: spese, creazione di siti nuovi su Netlify, Search Console, iscrizioni ad affiliazioni e consulenza fiscale. Per le idee nuove gli si chiede un sì o un no una volta sola.

## 6. Cosa decide chi
- **Claude**: misura, controlli, miglioramenti, proposte con numeri, idee nuove, costruzione a costo zero, congelamento dei siti sotto soglia (con motivo scritto).
- **Massimiliano**: sì/no su spese, pubblicazioni nuove, chiusure definitive, account (GoatCounter, AdSense, affiliati), consulenza fiscale.
