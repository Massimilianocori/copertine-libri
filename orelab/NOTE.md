# Note di costruzione

## Fase 0 — pagina di verifica (9 ottobre 2026): ONLINE su https://orelab.netlify.app
- Progetto Netlify `orelab`, site id `f261888c-d3f4-44cb-89ea-7cbf033eb6be`, form `waitlist` id `6ac8af0d43f7880008d74fd8`.
- Pubblicata da Massimiliano con Netlify Drop (lo strumento di deploy da sessione riceve 403). Prova d'invio riuscita e poi cancellata: contatore a 0.
- **Inizio test: 9/10/2026. Soglia: 30 iscritti entro il 23/10/2026.** Conteggio: manage-form-submissions sul form `waitlist`.
- `orelab/sito/index.html` (lista d'attesa, form Netlify "waitlist"), `privacy.html`, `netlify.toml`.
- `orelab/outreach/BOZZE.md` (regole delle comunità e 4 bozze), `REGISTRO.md` (da compilare a ogni pubblicazione).
- Provata in browser: validazione, invio riuscito, messaggio di errore, campo `source` dal parametro `?ref=`, nessun cookie, nessun errore JS, chiaro/scuro, mobile 375 px senza scroll orizzontale.

## Bloccanti per andare online
1. ~~Rete della sessione~~ (risolto 9/10; il deploy da sessione resta bloccato con 403, quindi si pubblica con Netlify Drop o collegando GitHub). Prima: `api.netlify.com` e `netlify-mcp.netlify.app` sono bloccati (verificato di nuovo il 9/10). Serve "Network access" completo nelle impostazioni dell'ambiente. Poi: creare il progetto Netlify `orelab` (o simile), attivare i moduli (update-forms), pubblicare `orelab/sito/`.
2. ~~Notifica email delle iscrizioni~~ (attivata da Massimiliano il 9/10: Forms → Submission notifications → email su "New form submission" del form waitlist).

## Scelte fatte qui (da confermare se serve)
- **Contatore iscritti:** non mostrato in pagina. Le regole Netlify sconsigliano contatori su Blobs, e un contatore basso farebbe più danno che bene. Il conteggio per la soglia (30 in 14 giorni) si legge dalle submission con lo strumento Netlify (manage-form-submissions) o dal pannello.
- **Contatto in privacy:** "rispondendo a una nostra email". Prima di raccogliere molti dati conviene un indirizzo dedicato (es. sul dominio definitivo).
- **Nome:** "orelab" è provvisorio. Per il mercato in inglese va verificato (dominio libero, marchi) prima del lancio del prodotto.
- **Prezzi in pagina:** quelli di DECISIONE.md (19/39/79 $), indicati come "launch prices".

## Suggerimento di business (per Fable/Massimiliano, non applicato)
- Offrire ai primi iscritti un "prezzo bloccato a vita" potrebbe aumentare le iscrizioni: è una decisione di prezzo, quindi non l'ho messa in pagina.
