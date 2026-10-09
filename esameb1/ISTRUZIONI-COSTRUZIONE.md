# EsameB1 — istruzioni di costruzione (Fase 1: test a costo zero)

Decisione del 9/10/2026 (studio: `studio-business/intelaiatura/1-candidati.md`). Massimiliano ha detto "facciamolo".
Chi costruisce legge PRIMA: questo file, `studio-business/REGOLE-FISSE.md`, lo studio citato sopra.

## Cosa costruiamo
Un sito gratuito, in italiano semplice, che raccoglie in un solo posto **tutte le date, le scadenze d'iscrizione e le sedi in Italia dell'esame di italiano B1 per la cittadinanza** dei 4 enti riconosciuti (CILS, CELI, PLIDA, CERT.IT), con un modulo "Avvisami" (email + città) per ricevere un avviso quando esce una data nella propria città.
Nome provvisorio: **EsameB1** (dominio dopo il test; per ora `esameb1.netlify.app` o simile).

## Obiettivo del test (45 giorni dalla pubblicazione)
- **Continua** se: ≥20 pagine indicizzate da Google, ≥300 clic da Google, ≥100 iscritti al modulo, almeno 5 pagine-città tra i primi 20 risultati.
- **Passa alla candidata B** (esami di Stato) se l'indicizzazione è ok ma gli iscritti sono <40.
- **Stop** se <100 clic e <20 iscritti.
I numeri si leggono in Search Console (Massimiliano la collega) e nelle submission del modulo Netlify.

## Vincoli (non negoziabili)
1. **Zero spese.** Netlify gratuito, niente dominio, niente pubblicità, niente strumenti a pagamento.
2. **Ogni data/sede/prezzo porta fonte (link) e data di verifica.** Niente dati inventati o "probabili": se un dato manca, si scrive "da confermare con la sede" e si linka la sede. Un dato sbagliato fa perdere mesi a chi aspetta la cittadinanza: l'affidabilità è il prodotto.
3. In ogni pagina: avviso chiaro "Verifica sempre sul sito della sede prima di iscriverti" + nessuna consulenza legale (non si spiega la pratica di cittadinanza, si linkano Prefettura/Ministero).
4. **Nessun identificatore di modello AI** nel codice, nelle pagine, nei commit.
5. Privacy GDPR: titolare Massimiliano Cori; modulo con consenso esplicito; Netlify come responsabile; niente cookie né analytics (si usa Search Console).
6. Niente email a freddo. L'unica distribuzione del test è Google (sitemap + Search Console). Facoltativo e solo con il sì di Massimiliano: segnalare il sito ai CPIA e alle sedi (è informazione istituzionale, non marketing) e nei gruppi Facebook, sempre dichiarando chi siamo.
7. Trademark: CILS, CELI, PLIDA, CERT.IT sono marchi degli enti; nota "sito indipendente, non affiliato".
8. Italiano semplice (il pubblico è straniero, livello B1): frasi corte, niente burocratese. Titoli e meta-description con le parole che la gente cerca ("esame B1 cittadinanza Milano date 2026").

## Fonti già verificate (raggiungibili dalla sessione il 9/10/2026, HTTP 200)
I testi estratti dai PDF sono già in `esameb1/dati/fonti/` (celi2026, plida2026, certit-cal2026, certit-centri).
- **CELI** (Università per Stranieri di Perugia): calendario 2026 in `dati/fonti/celi2026.txt` (fonte: PDF CEIS, gen. 2026, URL nel file). Sessioni B1 valide per cittadinanza: "CELI 2 i cittadinanza" 18/2, 6/5, 16/9/2026 (scadenze 16/1, 10/4, 14/8) + sessioni generiche B1 (CELI 2) 11/3, 10/6, 11/11 (scadenze 13/2, 8/5, 9/10). Cercare anche il calendario ufficiale 2027 sul sito CVCL. Centri: motore ufficiale `https://dils.unistrapg.it/ricercasedi/homericerca.aspx?qst=cic` (ASP.NET, form POST con __VIEWSTATE; voce menu "Centri d'esame convenzionati CELI"). Se il motore è complicato, estrarre l'elenco centri per regione con Playwright.
- **PLIDA** (Società Dante Alighieri): calendario 2026 in `dati/fonti/plida2026.txt` (B1: 11/2, 10/6, 9/9, 18/11/2026, "tutti i centri"; iscrizioni direttamente presso il centro). Centri in Italia: `https://plida.dante.global/` → pagina "Centri" (300 centri nel mondo; filtrare Italia).
- **CERT.IT** (Università Roma Tre): calendario 2026 in `dati/fonti/certit-cal2026.txt` (A2/B1: 3/3, 25/6, 6/10/2026, iscrizioni dal 12/1, 8/4, 27/8; "piazza telematica"); 33 centri italiani in `dati/fonti/certit-centri.txt` (PDF set. 2025, con regione, indirizzo, email, telefono).
- **CILS** (Università per Stranieri di Siena): home `https://cils.unistrasi.it/` → `https://cils.unistrasi.it/1/98/Esami_CILS.htm`; trovare il calendario 2026-27 (nel 2023: 10 sessioni/anno; sessione nota: 3/12/2026 con scadenze diverse per sede, es. Palermo 22/10) e l'elenco delle sedi italiane. Le date sono nazionali; scadenze e tasse variano per sede (es. 100 € Padova, 120 € Stoccarda).
- Normativa: B1 obbligatorio per cittadinanza per residenza e matrimonio (art. 9.1 L. 91/1992, dal 4/12/2018) — linkare la pagina del Ministero dell'Interno/Prefettura, non riassumere la legge.

## Struttura dati (`esameb1/dati/`)
- `enti.json`: 4 enti (nome, sigla, sito, pagina calendario, note su quale esame vale per la cittadinanza).
- `sessioni.json`: una voce per sessione: ente, data esame, livello/nome esame, scadenza iscrizione (nazionale o "varia per sede"), fonte (URL), verificato_il.
- `sedi.json`: sede: ente, nome, città, provincia, regione, indirizzo, sito/email/telefono (solo se pubblici sul sito dell'ente), fonte, verificato_il. Opzionale: scadenza e tassa specifiche se trovate sul sito della sede, con fonte.
- `citta.json`: le 20 città del test con slug: Milano, Roma, Torino, Napoli, Bologna, Firenze, Genova, Bari, Palermo, Catania, Verona, Padova, Brescia, Venezia, Bergamo, Modena, Parma, Reggio Emilia, Prato, Perugia. (Google suggerisce già: milano, torino, firenze, ravenna, roma, bologna → aggiungere Ravenna se si trovano sedi.)

## Sito (`esameb1/sito/`, statico, generato da `esameb1/genera.py`)
- `index.html`: "Esame B1 per la cittadinanza: tutte le date 2026-2027" — tabella unica ordinata per data (ente, esame, data, scadenza, dove), filtro per città/ente in JS semplice, modulo Avvisami in alto e in fondo.
- `/citta/<slug>/`: "Esame B1 cittadinanza a <Città>: date e sedi 2026" — sedi in città e provincia per ciascun ente, prossime date, scadenze, modulo Avvisami precompilato con la città. Se una città non ha sedi di un ente, dirlo e indicare la sede più vicina.
- `/ente/<sigla>/`: pagina per ente con calendario completo e lista sedi italiane.
- `/come-funziona/`: differenze tra i 4 esami in parole semplici (durata, costo indicativo, dove), con fonti; nessun consiglio legale.
- `privacy.html`, `sitemap.xml`, `robots.txt`, `netlify.toml` (header di sicurezza come orelab).
- Modulo Netlify `avvisami`: email, città (select dalle 20 + "altra"), ente preferito (opzionale), consenso obbligatorio, honeypot, campo nascosto `source`; invio AJAX come in `orelab/sito/index.html`. Messaggio di conferma chiaro.
- Stile: come orelab (token su :root, chiaro/scuro, mobile 375 px senza scroll orizzontale, nessuna libreria esterna, font di sistema). Testo grande e leggibile.
- Dati strutturati JSON-LD `Event` per ogni sessione (aiuta Google).

## Verifica prima di consegnare
- `python3 esameb1/genera.py` senza errori; nessun link interno rotto; Playwright: home, 2 pagine città, modulo (invio simulato ok/errore), mobile.
- Controllo dati: ogni sessione ha fonte + data; nessuna data passata presentata come futura; scadenze coerenti (prima della data esame).
- Zip `scratchpad/esameb1-sito.zip` per Netlify Drop + istruzioni per Massimiliano (Netlify Drop, Forms → Submission notifications, Search Console con verifica via file HTML da mettere in `sito/`, Routine di aggiornamento settimanale).
- `esameb1/NOTE.md`: stato, cosa manca, scelte fatte, data inizio test e soglie.

## Dopo il test (non ora)
Avvisi a pagamento (~5-10 €), accordi con scuole di preparazione (quota per iscritto), Fase 2 (prenotazione garantita candidati ↔ sedi). Dominio, Stripe e codice ATECO solo con i primi incassi.

## Ruoli
- Claude: tutto il lavoro sopra, aggiornamento settimanale dei dati, lettura dei numeri.
- Massimiliano: pubblicazione su Netlify (Drop o collegamento GitHub), Search Console, Routine; nessuna spesa.
