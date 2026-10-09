# BandiChiari — stato e decisioni

> **9 ottobre 2026: il SaaS per commercialisti è SCARTATO** dallo studio di fattibilità (`studio-business/fattibilita-saas/VERDETTO.md`). Il sito gratuito resta com'è; la routine settimanale va sospesa finché non si decide il business.

## REGOLE FISSE (decise il 9 ottobre 2026, non cambiano senza richiesta di Massimiliano)
- **Massimiliano fa solo, una volta:** (1) sblocco rete della sessione, (2) repository + connettori Netlify/Gmail sulla routine, (3) link di pagamento Stripe, (4) variazione partita IVA con un servizio online per forfettari quando arrivano i primi abbonati.
- **Claude fa tutto il resto:** software SaaS per studi, schede bandi, aggiornamenti settimanali, email agli iscritti, assistenza, scheda Capterra pronta da registrare.
- **Clienti solo da canali gratuiti gestiti da Claude:** Google (schede bandi), anteprima gratuita, newsletter degli iscritti, siti di confronto software. Niente email a freddo.
- **Mai chiedere soldi o tempo in più come condizione.** Pubblicità e LinkedIn sono facoltativi: solo se li propone Massimiliano.
- Prodotto: SaaS per commercialisti e per chi vende beni/servizi finanziati dai bandi. Anteprima gratuita con soli numeri; dettagli e rapporti PDF con logo dello studio solo in abbonamento (79 €/mese fino a 30 clienti, 149 €/mese fino a 100). Prezzi concorrenti verificati: Muffin 119-525 €/mese, BandzAI da 59 €/mese per azienda, BandoPilot 34,90-129,90 €/mese.


Aggiornato: 8 ottobre 2026.

## Decisioni
- Gratis per le imprese; si paga solo il piano Studio per commercialisti e consulenti (49 €/mese o 490 €/anno, fino a 20 clienti). Motivo: le informazioni sui bandi sono gratis ovunque, il bisogno ricorrente è di chi segue molti clienti.
- Massimiliano **ha già una partita IVA da fotografo**. Per BandiChiari non se ne apre una nuova: si **aggiunge un codice ATECO** (variazione gratuita, entro 30 giorni dall'inizio della nuova attività), da fare con un servizio online per forfettari (Massimiliano non ha un commercialista: ~40 €/mese, già previsto nella previsione) quando arrivano le prime richieste a pagamento (3 studi o la prima pratica "Ti prepariamo la domanda").
- Pagamenti Stripe **non attivi** fino alla variazione: i moduli raccolgono le richieste.
- Da chiedere al commercialista: (1) la nuova attività fa scattare l'iscrizione alla Gestione Commercianti INPS (minimo ~3.000 €/anno) o resta nella gestione attuale? (2) aliquota forfettaria (5% solo se la P.IVA ha meno di 5 anni, altrimenti 15%) e coefficiente del nuovo codice; (3) il limite di 85.000 € vale sulla somma di fotografia + BandiChiari.
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
