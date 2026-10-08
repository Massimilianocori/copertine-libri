# BandiChiari — stato e decisioni

Aggiornato: 8 ottobre 2026.

## Decisioni
- Gratis per le imprese; si paga solo il piano Studio per commercialisti e consulenti (49 €/mese o 490 €/anno, fino a 20 clienti). Motivo: le informazioni sui bandi sono gratis ovunque, il bisogno ricorrente è di chi segue molti clienti.
- Massimiliano **non ha partita IVA**. Pagamenti Stripe **non attivi** finché non c'è: il modulo Studio raccoglie le richieste ("ti scriviamo per attivare").
- La partita IVA si apre quando almeno **3 studi** hanno chiesto il piano Studio, così il minimo INPS (circa 3.000 €/anno se Gestione Commercianti in forfettario) non si paga prima della domanda reale. Regime forfettario; codice ATECO e gestione INPS da confermare con il commercialista.
- Dominio bandichiari.it: si compra con i primi iscritti; fino ad allora bandichiari.netlify.app.

## Da fare (Massimiliano)
1. Impostazioni ambiente cloud → Network access completo (oggi blocca Netlify e i siti ufficiali).
2. Routine "BandiChiari - aggiornamento settimanale" (claude.ai → Routines): aggiungere repository copertine-libri e connettori Netlify e Gmail.
3. Alla soglia dei 3 studi interessati: commercialista + partita IVA, poi i due link Stripe (49 €/mese, 490 €/anno).

## Da fare (Claude)
- Pubblicare il sito su Netlify appena la rete lo permette.
- Completare i bandi di Umbria, Abruzzo, Molise, Campania, Calabria, Basilicata.
- Con la partita IVA: inserirla nel footer e cambiare "IVA inclusa" in "operazione senza IVA, regime forfettario".

## Previsione economica (dettaglio: `python3 bandichiari/previsione.py`)
- Prima della partita IVA: spesa massima circa 40 €/anno (dominio + email). Hosting, routine e lavoro di Claude: 0 € extra.
- Pareggio con INPS Commercianti: **7 studi abbonati** (costi fissi circa 290 €/mese). Con Gestione Separata: 1–2 studi.
- 12 mesi (ott 26 - set 27), INPS Commercianti: Pessimista -40 €, Prudente -498 €, Realistico +2.641 €, Ottimista +10.701 €.
- Regola di stop: se 3 mesi dopo l'apertura della partita IVA gli studi abbonati sono meno di 7, si rivede il piano (prezzo, canale o chiusura) prima di spendere altro.
