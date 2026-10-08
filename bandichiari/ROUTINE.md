# BandiChiari — routine settimanale (eseguita da Claude in automatico)

Ogni lunedì una sessione programmata di Claude esegue questi passi, in ordine.
Regola d'oro: **nessun dato non verificato va online o in un'email.** In caso di dubbio un bando si esclude.

## 1. Aggiornare i bandi (`dati/bandi.json`)

1. Per ogni bando già presente: ricontrollare stato e scadenza (almeno 2 fonti o la fonte ufficiale). Se è chiuso o esaurito, impostare `scadenza` alla data di chiusura (la pagina mostra "Chiuso"). Aggiornare `ultima_verifica`.
2. Cercare i bandi nuovi della settimana: nazionali (MIMIT, Invitalia, Agenzia Entrate, Simest, INAIL) e regionali (regioni, finanziarie regionali, Camere di commercio), con priorità per micro e piccole imprese.
3. Aggiungere solo bandi confermati, con lo stesso schema delle voci esistenti; `affidabilita` = "alta" o "media".
4. Salvare i nuovi bandi in `dati/ricerca/AAAA-MM-GG.json`, poi lanciare `python3 bandichiari/unisci.py` e `python3 bandichiari/genera.py`: devono finire senza errori.
5. Priorità di copertura: prima le regioni con meno bandi regionali (oggi Umbria, Abruzzo, Molise, Campania, Calabria, Basilicata).

## 2. Pubblicare

Commit con messaggio `BandiChiari: aggiornamento bandi AAAA-MM-GG (N nuovi, M chiusi)` e push sul branch di lavoro.
Pubblicare `bandichiari/sito/` sul progetto Netlify **bandichiari** (site id `c5743216-ab6d-419a-9d02-d2d6ce0f7b64`) con lo strumento Netlify deploy-site, lanciando il comando dalla cartella `bandichiari/sito`. Se la rete blocca Netlify, annotarlo nel rapporto.

## 3. Email agli iscritti

- **Iscritti:** email di notifica di Netlify Forms (form "iscrizione") arrivate nella casella del servizio. Profilo = regione, dimensione, attività, temi, piano.
- **Studio (paganti):** moduli "studio" di Netlify Forms + email di Stripe "pagamento riuscito" con lo stesso indirizzo. A ogni nuovo abbonato Studio scrivere per chiedere i profili dei clienti (regione, dimensione, settore, investimenti previsti, massimo 20) e salvarli in `dati/studi/` (fuori dal sito pubblico).
- **Cancellati:** chi ha risposto "CANCELLA" non riceve più nulla; si annota in `dati/cancellati.txt` (solo l'hash dell'email, non l'indirizzo).
- **Imprese (gratis):** solo i bandi compatibili con regione, dimensione e temi, ciascuno con importo, 2 righe di spiegazione, documenti da preparare e link alla scheda; in cima quelli che scadono entro 15 giorni. In fondo una riga: "Il tuo commercialista segue molti clienti? Digli di BandiChiari Studio."
- **Studio:** un'unica email con una sezione per ogni cliente, stessa logica.
- Ogni email finisce con: "Per non ricevere più queste email rispondi CANCELLA."
- Se non c'è niente di nuovo per un iscritto, non si manda nulla.
- Rispondere alle domande degli abbonati Su misura arrivate per email, solo con informazioni presenti nei bandi ufficiali.

## 4. Rapporto

Aggiungere una riga a `METRICHE.md`: data, bandi totali/aperti/nuovi/chiusi, iscritti gratis, abbonati, email inviate, disiscrizioni.
