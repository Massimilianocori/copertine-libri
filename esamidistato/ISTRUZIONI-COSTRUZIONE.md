# EsamiDiStato — istruzioni di costruzione (Fase 1: test a costo zero)

Candidata B dello studio `studio-business/intelaiatura/1-candidati.md` (sezione 2). Stesso motore di EsameB1 (`esameb1/`):
dati JSON curati con fonte → `genera.py` → sito statico su Netlify con modulo "Avvisami".
Chi costruisce legge PRIMA: questo file, `esameb1/ISTRUZIONI-COSTRUZIONE.md`, `studio-business/REGOLE-FISSE.md`.

## Cosa costruiamo
Un sito gratuito, in italiano semplice, con **date, scadenze delle domande e sedi** degli esami di Stato di abilitazione
per ogni professione, più il modulo "Avvisami" (email + professione + città). Nome provvisorio **EsamiDiStato**,
indirizzo previsto `https://esamidistato.netlify.app` (costante `URL_SITO` in `genera.py`).

## Vincoli (gli stessi di EsameB1, non negoziabili)
1. Zero spese (Netlify gratuito, niente dominio, niente pubblicità).
2. Ogni data/sede porta fonte (link) e data di verifica. Niente dati inventati: se un dato manca si scrive "leggi il bando della tua sede".
3. In ogni pagina: "leggi il bando della tua sede prima di fare la domanda"; nessuna consulenza.
4. Nessun identificatore di modello AI nel codice, nelle pagine, nei commit.
5. Privacy GDPR: titolare Massimiliano Cori; consenso esplicito nel modulo; Netlify responsabile; niente cookie né analytics.
6. Niente email a freddo. Distribuzione del test: Google (sitemap + Search Console).
7. Sito indipendente, non affiliato a MUR, MIM, Ministero della Giustizia, università, Ordini.
8. Italiano semplice; titoli con le parole cercate ("esame di stato ingegnere 2026 date").

## Fonti (tutte ufficiali)
- MUR: pagina esami di Stato + OM 692, 693, 694 del 27/5/2026 (PDF con la tabella delle sedi per professione).
- MIM: OM 76, 77, 78 del 9/5/2026 (agrotecnico, geometra, perito agrario), copia pubblicata dall'USR Veneto.
- Ministero della Giustizia: decreto 3/9/2026 e scheda di sintesi per l'esame di avvocato 2026.
- ISTAT: elenco dei comuni (provincia e regione delle sedi).

## Struttura
- `raccolta/raccogli.py`: scarica le ordinanze MUR e il decreto avvocato, legge le sedi, localizza con ISTAT, salva `dati/sedi.json`,
  i testi in `dati/fonti/` e le impronte delle pagine ufficiali (`dati/impronte.json`). `raccolta/siti_atenei.json`: siti degli atenei
  e pagine "esami di Stato" verificati a mano.
- `dati/professioni.json`, `dati/sessioni.json` (a mano, con fonte), `dati/citta.json` (24 città).
- `genera.py` → `sito/`: home con calendario e filtro, una pagina per professione, una per città, "Come funziona", privacy, 404,
  sitemap, robots, netlify.toml (con regola `ignore`).

## Verifica prima di consegnare
`python3 esamidistato/genera.py` senza errori; nessun link interno rotto; Playwright su home, pagine professione e città, modulo
(blocco se vuoto, invio ok), 375 px senza scroll orizzontale, nessun errore in console; zip per Netlify Drop.

## Ruoli
- Claude: dati, sito, aggiornamenti, lettura dei numeri.
- Massimiliano: pubblicazione su Netlify, Search Console, notifiche del modulo; nessuna spesa.
