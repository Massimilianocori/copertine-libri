# Istruzioni di costruzione — SaaS "ore e fatture a prezzo fisso" (nome provvisorio: orelab)

Per la sessione che costruisce (Opus). Decisioni di business già prese: `studio-business/saas/DECISIONE.md` e `CONFRONTO-FINALE.md`. Non cambiarle; se qualcosa non torna, annotalo in `orelab/NOTE.md` e vai avanti.

## Vincoli
- Lingua del prodotto: **inglese**. Mercato: mondiale (freelance e micro-agenzie 1-15 persone).
- Prezzo: **fisso per team**, non per utente: Solo 19 $/mese (1 utente), Team 39 $/mese (fino a 5), Agency 79 $/mese (fino a 15). Prova 14 giorni **con carta** (converte 3x). Annuale: 2 mesi gratis.
- Pagamenti: Stripe Checkout + Customer Portal (account Stripe di Massimiliano; i link e le chiavi le inserisce lui come variabili d'ambiente, mai nel repo).
- Hosting: Netlify (account già usato per Scrollcraft e BandiChiari). Database: Netlify Database (Postgres) se il piano lo consente, altrimenti Neon (UE). Dati in UE.
- Niente email a freddo. Niente spese prima dell'ok di Massimiliano.
- Nessun identificativo di modello AI in commit, codice o pagine.

## Fase 0 (prima di tutto): pagina di verifica — 1 giorno
Pagina singola `orelab/sito/index.html` + Netlify Forms (form "waitlist"):
- titolo: "Time tracking and invoicing. One flat price. No usage fees."
- confronto prezzi: Harvest (flex billing, esempi Bloomberg 211→2.547 $/anno) vs noi (39 $/mese fisso);
- "Import from Harvest, Clockify or Toggl in one click";
- modulo: email + "which tool do you use today?" + team size;
- privacy breve; nessun cookie di tracciamento; contatore iscritti letto dalle submission.
Soglia: **30 iscritti in 14 giorni**. Massimiliano la linka nei thread "Harvest alternative" (Reddit, G2, forum) con le bozze preparate in `orelab/outreach/`.

## Fase 1: prodotto minimo — settimane 1-6
Stack: Next.js (App Router) + TypeScript + Postgres (Drizzle) + Netlify Functions + Netlify Identity o Auth.js; Tailwind; Stripe.
Funzioni, in quest'ordine:
1. Account, workspace, inviti (ruoli: owner, member).
2. Clienti e progetti (con tariffa oraria per progetto, budget ore opzionale).
3. Timer (start/stop) + inserimento manuale + timesheet settimanale; app web responsive (mobile).
4. Report: ore per cliente/progetto/persona/periodo, fatturabili vs non; export CSV.
5. Fatture: da ore non fatturate → fattura PDF (numerazione, IVA opzionale, valuta), invio per email, link di pagamento Stripe opzionale per il cliente finale, stato pagata/non pagata.
6. **Importatori**: CSV di Harvest (clients, projects, time entries), Clockify (detailed report CSV), Toggl (detailed CSV). Devono funzionare al primo colpo: sono il motivo per cui la gente passa a noi.
7. Abbonamento Stripe con prova 14 giorni con carta; blocco gentile a prova scaduta.
8. Pagine pubbliche: home, pricing, "Harvest alternative", "Clockify alternative", "Toggl alternative", "Harvest pricing explained", privacy, terms.
Qualità: test automatici su timer, calcoli report, totali fattura e importatori; prova in browser (Playwright, già disponibile) su desktop e mobile; nessun errore in console.

## Fase 2: lancio — settimane 7-10
- Listing su G2, Capterra, AlternativeTo (schede e screenshot pronti; registra Massimiliano).
- Email di benvenuto, promemoria fine prova, richiesta recensione dopo 30 giorni (Gmail/Resend).
- Pagina "Migrate from Harvest" con guida passo passo.
- Metriche: visite → prove → paganti → disdette, in `orelab/METRICHE.md` ogni settimana.

## Ruoli
- Opus: tutto il codice, le pagine, i test, i listing, le bozze.
- Massimiliano: account Reddit/LinkedIn/G2 a suo nome (aprirli SUBITO), pubblica le bozze, risponde ai clienti, Stripe e chiavi, variazione ATECO quando arrivano i primi paganti.
- Fable (questa sessione): solo decisioni di business, prezzi, strategia, se serve.

## Regola di stop
90 giorni dal lancio senza 10 paganti → si rivede o si chiude (vedi DECISIONE.md).
