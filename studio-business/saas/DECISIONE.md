# Decisione (9 ottobre 2026): time tracking + fatturazione a prezzo fisso per freelance e micro-agenzie

Criterio di Massimiliano: ciò che può fatturare di più, con prove. Studi: `1-nicchie-con-ricavi.md`, `2-lacune-e-lamentele.md`, `3-canali-primi-100-clienti.md`.

## Perché questo
- **Mercato più grande e provato tra i candidati:** Harvest ~123 M$ di ricavi annui (stima Latka 2023), Toggl 15-33 M$, Clockify ~26 M$ (2023). Decine di migliaia di clienti paganti a 9-14 $/utente/mese.
- **Clienti in fuga ORA:** dopo l'acquisizione da Bending Spoons, Harvest ha introdotto la fatturazione "a consumo": Bloomberg (13/8/2026) riporta rinnovi da 211 $ a 2.547 $/anno; BBC: da 130 a 2.110 $/mese. Clockify ha svuotato il piano gratuito (21/4/2026, Trustpilot a 3,1).
- **Costruibile in 4-6 settimane:** timer, progetti, clienti, report, fatture con Stripe, importazione da Harvest/Clockify/Toggl.
- **Prezzo che regge il costo di acquisizione:** 29-49 $/mese fisso per team (non per utente) → un cliente ripaga 100-150 $ di CAC in 3-4 mesi.

## Differenza rispetto ai concorrenti
Prezzo **fisso e pubblico** per team (proprio ciò che Harvest ha rotto), nessun costo a consumo, importazione in 1 clic, semplicità. Non competiamo su funzioni con Toggl/TimeCamp: competiamo su prevedibilità e prezzo.

## Rischi (veri)
- Categoria affollata: Toggl, TimeCamp, Productive, Teamwork cacciano gli stessi clienti.
- Harvest potrebbe fare marcia indietro.
- Servono integrazioni (QuickBooks/Xero) per i clienti più grandi: non nella prima versione.
- Fatturato realistico, non garantito: 100 clienti ≈ 3-4k $/mese; 300 clienti ≈ 10-14k $/mese entro 12-18 mesi (ipotesi).

## Scartati e perché
- App Shopify inventario: canale App Store "quasi nullo a zero recensioni"; Shopify può uccidere l'app cambiando API (caso Checkout X).
- Verticali per professione (palestre, scuole di musica): buoni ricavi ma vendita lenta e USA-centrica.
- Peppol/e-fattura, IVA B2B Shopify, ricevute Xero: domanda più piccola o fornitori locali gratuiti.

## Strategia di vendita (dopo il prodotto)
1. **Primi 10 (sett. 1-6):** importatore gratuito da Harvest/Clockify; risposte nei thread "Harvest alternative" su Reddit/G2/forum (account di Massimiliano da maturare subito); pagina di confronto prezzi.
2. **10→50 (mesi 2-5):** listing G2/Capterra/AlternativeTo; pagine SEO "Harvest alternative", "Clockify alternative", "Harvest pricing"; recensioni chieste a ogni cliente.
3. **50→100+ (mesi 5-10):** test Google Ads solo su parole esatte "harvest alternative" (CPC ~2 $), tetto 100-300 €/mese, stop se un cliente costa più di 3 mesi di abbonamento.

## Ruoli
- **Claude:** prodotto, sito, importatori, pagine di confronto, listing, modelli di risposta, metriche, report CAC.
- **Massimiliano:** account Reddit/LinkedIn/G2 a suo nome; risposte ai thread e ai clienti (bozze mie); telefonate con agenzie interessate; Stripe e fatture; variazione ATECO (software) con il servizio per forfettari.

## Regola di stop
Se 90 giorni dopo il lancio non ci sono almeno 10 clienti paganti, si rivede (prezzo, nicchia) o si chiude.
