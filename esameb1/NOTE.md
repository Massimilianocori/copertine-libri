# EsameB1 — note di costruzione

## Fase 1 (9 ottobre 2026): sito pronto, da pubblicare
- Progetto Netlify **esameb1**: site id `08c6548f-00a5-454d-a0bd-a3a029128b58`, indirizzo https://esameb1.netlify.app, moduli attivati.
- Pubblicazione: Massimiliano carica `esameb1-sito.zip` con Netlify Drop nella pagina del progetto (il deploy dalla sessione riceve 403). Poi Forms → Submission notifications → email per il modulo `avvisami`.
- Dopo la pubblicazione: Search Console (verifica con file HTML `google*.html` da mettere in `esameb1/sito/`; `genera.py` lo conserva) e invio di `sitemap.xml`.

## Cosa c'è
- `raccolta/raccogli.py`: scarica le fonti ufficiali e rigenera `dati/sedi.json` (644 sedi: 375 CILS, 155 CELI, 82 PLIDA, 32 CERT.IT); controlla le impronte delle pagine-calendario (`dati/impronte.json`) e avvisa se cambiano.
- `raccolta/cils_sedi.py`: parser delle tabelle regionali CILS (con correzioni manuali delle righe sbagliate nella fonte).
- `dati/sessioni.json`: 31 sessioni B1 2026-2027 curate a mano dalle fonti ufficiali (CILS 2026 e 2027, CELI 2026 e 2027, PLIDA 2026, CERT.IT 2026), ognuna con fonte e data di verifica.
- `genera.py`: sito statico in `sito/` — home con calendario e filtri, 21 pagine città (20 + Ravenna, suggerita da Google), 4 pagine ente con sedi per regione, "Come funziona", privacy, 404, sitemap, robots, netlify.toml. Il JS ricalcola nel browser le sessioni passate e le scadenze vicine, quindi il sito resta corretto anche tra un aggiornamento e l'altro.
- Provato in Chromium (desktop e 375 px): nessun errore JS, nessuno scroll orizzontale, filtri, modulo (blocco se vuoto, invio ok, campo `source` da `?ref=`), chiaro/scuro, 661 link interni senza rotture.

## Mancano / da fare
- Calendari 2027 di **PLIDA** e **CERT.IT**: non ancora pubblicati dagli enti (controllati il 9/10/2026). La routine li cerca ogni settimana.
- Le sessioni passate restano nel JSON (storico) ma non si vedono nel sito.
- Routine settimanale (da attivare): `python3 esameb1/raccolta/raccogli.py` → se "CALENDARI CAMBIATI", aggiornare `dati/sessioni.json` a mano con fonte → `python3 esameb1/genera.py` → commit e push → nuovo zip per Massimiliano (oppure deploy automatico se Netlify viene collegato a GitHub con base `esameb1/sito`).
- Email agli iscritti del modulo "avvisami": solo quando c'è una data nuova o una scadenza entro 15 giorni nella loro città. Da costruire quando ci sono iscritti.

## Test (45 giorni dalla pubblicazione)
- **Continua** se: ≥20 pagine indicizzate, ≥300 clic da Google, ≥100 iscritti, almeno 5 pagine città tra i primi 20 risultati.
- **Candidata B** (esami di Stato) se l'indicizzazione è ok ma gli iscritti sono <40.
- **Stop** se <100 clic e <20 iscritti.
- Data di inizio: il giorno della pubblicazione (da annotare qui).

## Scelte fatte
- Mostrate anche le sessioni B1 "generali" (CELI 2, PLIDA B1, CERT.IT B1), etichettate "B1 valido per la cittadinanza": la Prefettura chiede una certificazione almeno B1 di uno dei 4 enti.
- CELI: usato il calendario ufficiale CVCL (9 giugno 2026), non quello della sede CEIS (10 giugno).
- CERT.IT: la data è "disponibilità della piazza telematica"; in pagina si chiede di confermare il giorno con il centro.
- Nessun prezzo inventato: solo due esempi reali con fonte (UniMi 90 €, Padova 100 €).
