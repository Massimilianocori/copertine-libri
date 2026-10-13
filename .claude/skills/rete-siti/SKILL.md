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
1. **GoatCounter** (contatore gratuito senza cookie): da attivare. Massimiliano crea l'account e dice il nome scelto. Poi si aggiunge lo script ai siti con le pubblicazioni già previste e si aggiorna la privacy di ogni sito, che oggi dice "nessuno strumento di analisi". Per leggerlo dalle routine serve una chiave API in sola lettura messa tra i segreti dell'ambiente: spiegare a Massimiliano i passi quando arriva.
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

**Regola di Massimiliano (13/10/2026):** "devi trovare sempre nuove idee e portare avanti quelle che sono già in cantiere". Ogni mercoledì si aggiorna la tabella "Idee in cantiere" del cruscotto: ogni idea fa un passo avanti oppure si chiude con il motivo, e se ne aggiunge almeno una nuova.

## 5. Il messaggio a Massimiliano (ogni settimana, 5-8 righe)
1. Come va la rete in una frase (con un numero).
2. Cosa va, cosa non va (un sito per riga, solo quelli con novità).
3. L'azione della settimana e cosa serve da lui (se serve qualcosa, in passi precisi).
4. Le decisioni che spettano a lui (spese, pubblicazioni nuove, chiusure): domanda sì/no.
Niente elenchi lunghi, niente gergo. Se non è cambiato niente, dillo in una riga.

## 6. Cosa decide chi
- **Claude**: misura, controlli, miglioramenti, proposte con numeri, idee nuove, costruzione a costo zero, congelamento dei siti sotto soglia (con motivo scritto).
- **Massimiliano**: sì/no su spese, pubblicazioni nuove, chiusure definitive, account (GoatCounter, AdSense, affiliati), consulenza fiscale.
