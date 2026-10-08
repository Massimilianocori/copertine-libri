# Rispondoio — piano per il fatturato più alto (ottobre 2026)

## La scelta: Rispondoio, non un business nuovo

Tra tutto quello che hai già avviato, Rispondoio ha il fatturato potenziale più alto:

| | Rispondoio | Scrollcraft (video AI, USA) | PressedHeart / KDP |
|---|---|---|---|
| Incasso per cliente | € 79–229 **al mese** + € 149 attivazione | progetti singoli | € 3–8 a vendita |
| Ricorrente | Sì, impegno minimo 3–12 mesi | No | No |
| Clienti per arrivare a € 10.000/mese | **circa 70** (media € 149) | molti progetti al mese | oltre 1.500 vendite al mese |
| Mercato | Italia, in italiano, attività locali | USA, in inglese | marketplace saturi |
| Dati finora | prodotto costruito e testato | 116 email, 0 risposte (METRICHE 7/10) | 10 vendite in 2 mesi |

**Margine** (costo Retell circa $0,11–0,15 al minuto, fonti sotto): Basic con tutti i 200 minuti usati costa circa € 25 su € 79 (≈ 70% di margine); Pro con tutti i 1.000 minuti circa € 115 su € 229 (≈ 50%). La maggior parte dei clienti non usa tutti i minuti.

**Prezzi in linea col mercato italiano:** i concorrenti stanno tra € 50 e € 200 al mese (CloudTalk da € 99 + € 25/utente, Fonio € 99–499, My AI Front Desk € 20–99). Rispondoio si distingue perché è in italiano e configurato da noi.

## Il collo di bottiglia era la vendita, non il prodotto

Prima di oggi il sito perdeva ogni cliente pronto a comprare: tutti i pulsanti "Inizia con…" e "Procedi al pagamento" mostravano solo "checkout a breve". Nessun modulo, nessun telefono, nessuna pagina trovabile su Google oltre la home.

**Le email a freddo non sono una strada:** in Italia il Garante considera illecito l'email marketing senza consenso anche verso indirizzi aziendali o PEC pubbliche (art. 130 Codice privacy, provv. 149/2021). Quindi il motore deve portare clienti che **cercano** la soluzione.

## Il motore automatico costruito oggi

1. **Modulo di attivazione** (homepage e tutte le pagine): ogni pulsante di piano apre un modulo con piano e fatturazione già scelti. Le richieste arrivano in Netlify Forms con email di notifica; se il sito non è su Netlify si apre un'email già compilata. Nessuna richiesta va persa.
2. **Calcolatore "Quanto ti costano le chiamate perse?"**: il visitatore vede in euro quanto perde ogni mese e che Rispondoio si ripaga con 1–2 clienti.
3. **12 pagine per settore** (`per/dentisti/`, `per/parrucchieri/`, `per/ristoranti/`…): ognuna con un esempio di telefonata del settore, calcolatore con valori del settore, prezzi, FAQ e dati strutturati per Google. Fatte per le ricerche tipo "segreteria telefonica AI per dentisti". Si generano con `python3 strumenti/genera_pagine.py`; per aggiungere un settore basta una voce in `strumenti/settori.py`.
4. **sitemap.xml, robots.txt, informativa privacy.**

Flusso di vendita: richiesta → configuriamo l'assistente → il cliente lo prova → attiva il piano. Nessun pagamento prima della prova: è la promessa scritta nel modulo.

## Cosa serve da te (decisioni sì/no)

1. **Dominio rispondoio.net**: oggi non risponde (DNS inesistente), quindi anche io@rispondoio.net probabilmente non riceve email. Va registrato (circa € 10/anno) e collegata la casella. Senza questo, nessun cliente può scriverti.
2. **Pubblicare su Netlify** (gratis, stesso account di scrollcraft.design): serve perché il modulo funzioni. Poi in Netlify → Forms → attivare "form detection" e la notifica email verso la tua casella.
3. **P.IVA e dati legali in fondo al sito**: obbligatori per un sito commerciale in Italia; l'informativa privacy va fatta rivedere (ci sono i tuoi dati come titolare).
4. **Google Ads sulle ricerche ad alta intenzione** ("segreteria telefonica virtuale", "centralino AI"…) puntate sulle pagine settore: è il canale più rapido e legale. Proposta di partenza: € 10/giorno per 30 giorni, da decidere.

## Da verificare nei testi

- Le FAQ dicono che il cliente **non cambia numero** (inoltro di chiamata verso Rispondoio): confermare che è così che lo attivi.
- Il modulo promette di **ricontattare entro un giorno lavorativo**.

## Numeri da guardare ogni settimana

Visite alle pagine settore → richieste dal modulo (obiettivo: 2–4% delle visite) → prove fatte → piani attivati. Il campo `pagina` di ogni richiesta dice da quale pagina e quale pulsante arriva.

## Fonti

- Prezzi concorrenti Italia: [CloudTalk](https://www.cloudtalk.io/it/blog/quanto-costa-servizio-risposta-ia/), [Fonio](https://www.fonio.ai/it/prezzi), [My AI Front Desk](https://www.cloudtalk.io/it/blog/my-ai-front-desk-prezzi/)
- Costi Retell: [eesel.ai](https://eesel.ai/blog/retell-ai-pricing), [11x.ai](https://www.11x.ai/guides/retell-ai-pricing)
- Email marketing senza consenso: [Il Sole 24 Ore](https://ntplusdiritto.ilsole24ore.com/art/e-mail-pubblicitarie-illecito-invio-senza-consenso-nonostante-link-disiscriversi-AFrEGOM), [Money.it su PEC e provv. 149/2021](https://www.money.it/come-trovare-pec-aziendali-e-creare-liste-pronte-all-invio-guida-in-5-passaggi-senza-errori-legali)
