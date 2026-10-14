# EsameB1 — note di costruzione

## Fase 1 (9 ottobre 2026): ONLINE su https://esameb1.netlify.app
- Pubblicato da Massimiliano con Netlify Drop il 9/10/2026. Form `avvisami` id `6ac93ed49dcb990008cd22da`: prova d'invio riuscita e cancellata (contatore a 0).
- Progetto Netlify **esameb1**: site id `08c6548f-00a5-454d-a0bd-a3a029128b58`, indirizzo https://esameb1.netlify.app, moduli attivati.
- **Pubblicazione automatica da GitHub** (collegata il 9/10/2026): branch `ccr-b7fd6b9e-n096cr`, base e publish `esameb1/sito`. Netlify pubblica solo se cambia `esameb1/sito` (regola `ignore` in `netlify.toml`): ogni pubblicazione consuma crediti del piano gratuito, quindi al massimo un push del sito a settimana.
- **Routine settimanale** `trig_017HFNXZX5fKYcerETVg5zq4` (lunedì 7:59 ora italiana, nuova sessione, notifiche email e push): raccoglie le sedi, controlla i calendari, rigenera, aggiorna `METRICHE.md`, fa un push. Senza connettori: gli iscritti si leggono solo se la sessione ha gli strumenti Netlify.
- **Search Console verificata il 9/10/2026** (metodo: tag HTML, costante `GOOGLE_VERIFICA` in `genera.py` — non rimuoverla) e `sitemap.xml` inviata. Notifica email del modulo `avvisami` attiva.

## Cosa c'è
- `raccolta/raccogli.py`: scarica le fonti ufficiali e rigenera `dati/sedi.json` (644 sedi: 375 CILS, 155 CELI, 82 PLIDA, 32 CERT.IT); controlla le impronte delle pagine-calendario (`dati/impronte.json`) e avvisa se cambiano.
- `raccolta/cils_sedi.py`: parser delle tabelle regionali CILS (con correzioni manuali delle righe sbagliate nella fonte).
- `dati/sessioni.json`: 31 sessioni B1 2026-2027 curate a mano dalle fonti ufficiali (CILS 2026 e 2027, CELI 2026 e 2027, PLIDA 2026, CERT.IT 2026), ognuna con fonte e data di verifica.
- `genera.py`: sito statico in `sito/` — home con calendario e filtri, 77 pagine città (le 21 iniziali + dal 14/10/2026 ogni provincia con almeno 3 sedi; home con le 12 città principali e l'elenco completo per regione), 4 pagine ente con sedi per regione, "Come funziona", privacy, 404, sitemap, robots, netlify.toml. Il JS ricalcola nel browser le sessioni passate e le scadenze vicine, quindi il sito resta corretto anche tra un aggiornamento e l'altro.
- Provato in Chromium (desktop e 375 px): nessun errore JS, nessuno scroll orizzontale, filtri, modulo (blocco se vuoto, invio ok, campo `source` da `?ref=`), chiaro/scuro, 661 link interni senza rotture.

## Mancano / da fare
- Calendari 2027 di **PLIDA** e **CERT.IT**: non ancora pubblicati dagli enti (controllati il 9/10/2026). La routine li cerca ogni settimana.
- Le sessioni passate restano nel JSON (storico) ma non si vedono nel sito.
- Routine settimanale (attiva, vedi sopra): `python3 esameb1/raccolta/raccogli.py` → se "CALENDARI CAMBIATI", aggiornare `dati/sessioni.json` a mano con fonte → `python3 esameb1/genera.py` → commit e push → nuovo zip per Massimiliano (oppure deploy automatico se Netlify viene collegato a GitHub con base `esameb1/sito`).
- Email agli iscritti del modulo "avvisami": solo quando c'è una data nuova o una scadenza entro 15 giorni nella loro città. Da costruire quando ci sono iscritti.

## Test (45 giorni dalla pubblicazione)
- **Continua** se: ≥20 pagine indicizzate, ≥300 clic da Google, ≥100 iscritti, almeno 5 pagine città tra i primi 20 risultati.
- **Candidata B** (esami di Stato) se l'indicizzazione è ok ma gli iscritti sono <40.
- **Stop** se <100 clic e <20 iscritti.
- Data di inizio: **9/10/2026** (pubblicazione). Il conteggio dei 45 giorni parte da quando Google indicizza (Search Console collegata): verifica intermedia il 23/11/2026.

## Scelte fatte
- Mostrate anche le sessioni B1 "generali" (CELI 2, PLIDA B1, CERT.IT B1), etichettate "B1 valido per la cittadinanza": la Prefettura chiede una certificazione almeno B1 di uno dei 4 enti.
- CELI: usato il calendario ufficiale CVCL (9 giugno 2026), non quello della sede CEIS (10 giugno).
- CERT.IT: la data è "disponibilità della piazza telematica"; in pagina si chiede di confermare il giorno con il centro.
- Nessun prezzo inventato: solo due esempi reali con fonte (UniMi 90 €, Padova 100 €).

## Fisco (nodo aperto, decide quando attivare i pagamenti)
- Gli incassi previsti (avvisi a pagamento, quote dalle scuole, prenotazioni) sono di natura commerciale: con ogni probabilità servono Camera di Commercio e INPS Gestione Commercianti (minimo ~3.000 €/anno, ridotto del 35% per i forfettari ≈ 2.000 €), non basta aggiungere un codice ATECO alla P.IVA da fotografo. Da confermare con la consulenza gratuita di un servizio per forfettari PRIMA del primo incasso.
- Conseguenza: nessuna funzione a pagamento finché i ricavi attesi non superano chiaramente il costo fisso. La fase 1 resta gratuita e serve a costruire la lista; si attiva il pagamento quando una città ha abbastanza iscritti da vendere alle scuole/sedi.

## Grafica (11/10/2026)
- EsameB1: verde italiano, rosso mattone per le urgenze, carta calda, banda tricolore; marchio a fumetto "B1"; font Figtree.
- Identità propria del sito, tutta in `genera.py` (CSS con token su `:root`, chiaro/scuro automatico, icone SVG in linea con uno sprite per pagina, marchio SVG nel logo e nel favicon).
- In cima a home, pagine città/professione: scheda "risposta" con prossimo esame e prossima scadenza ancora aperta; il JS nasconde le voci scadute, quindi resta giusta anche tra un aggiornamento e l'altro.
- Font servito dal sito (`assets/fonts/`, licenza SIL OFL in `OFL.txt`, copiato in `sito/fonts/`): nessuna risorsa esterna.
- Immagine Open Graph 1200x630: `assets/og.png`, generata con Playwright da `assets/og-template.html` (istruzioni nel file).
- Moduli `avvisami`, titoli, description, canonical, h1, JSON-LD e URL invariati.
- Revisione design (11/10/2026): colonna laterale "sticky" con il solo modulo, città e sedi a tutta larghezza (sedi in griglia); schede data su una riga con la nota della scadenza detta una volta in testa all'elenco; elenco ridotto alle prossime 6 date con "Mostra tutte" e conteggio dopo il filtro; su mobile pillola data senza bordo curvo e bottoni a tutta larghezza; email multiple separate.

## Ricerche e intenti (12/10/2026)
- Suggerimenti di ricerca Google (it/it) del 12/10/2026, bisogni ricorrenti: date per ente e anno ("cils b1 cittadinanza date 2026", "plida b1 date 2026", "celi b1 cittadinanza date"), città ("esame cils b1 cittadinanza genova", "iscrizione esame b1 per cittadinanza milano"), **risultati** ("cils b1 cittadinanza risultati", "risultati celi perugia"), **costo** ("quanto costa esame b1 cittadinanza", "cils b1 cittadinanza costo", "plida b1 costo"), **durata** ("quanto dura esame b1 cittadinanza"), **esempi/simulazione/pdf**, **online**, "roma tre esame b1 cittadinanza". Nessun suggerimento per documenti, scadenza del certificato, mesi.
- Nuove pagine: `/costo/` e `/risultati/`. "Come funziona" ora copre durata, documenti, "si può fare online?" e prove d'esempio ufficiali. Domande frequenti della home aggiornate con link.
- Fatti per ente in `dati/enti.json` → `fatti` (costo, durata, risultati, documenti, esempi, nota), ognuno con fonti ufficiali e `verificato_il`. Se un ente non pubblica un dato (tempi dei risultati CERT.IT; la durata PLIDA è nel Quaderno delle specifiche B1, aggiunta il 12/10) la pagina lo dice e rimanda alla sede.
- Prezzi ufficiali trovati: CILS B1 Cittadinanza 100 € "in Italia e all'estero" (pagina B1 c di Unistrasi); CERT.IT B1 80 € solo alla sede di Roma Tre; CELI e PLIDA: il prezzo lo decide il centro (esempio UniMi 90 € = 65 + 25 di spese).
- Pagine ente: titolo e h1 con le parole cercate (`NOME_RICERCA` in `genera.py`), riquadro "in breve", ancore per regione (`/ente/cils/#liguria`, il riquadro si apre da solo) e link alle pagine città.
- Pagine città: schede "Prossime date ente per ente" (prossimo esame e prima scadenza nazionale aperta, tenute aggiornate dal JS), ancore `#sedi-<ente>`, link "Tutte le sedi X in <regione>", "Prima di iscriverti" (costo, come si svolge, risultati), città della stessa regione. Description con i soli enti presenti.
- JSON-LD Event: `performer` = ente certificatore con url; `offers` solo dove la tassa è ufficiale e unica (CILS B1 Cittadinanza, 100 EUR, url della pagina Unistrasi; `availability` solo se il termine nazionale è aperto). Per CELI, PLIDA e CERT.IT niente `offers`: un prezzo per tutte le sedi non esiste.
- Pagine CERT.IT/PLIDA senza date future: il titolo non promette un anno; nelle città la scheda dice "nessuna nuova data pubblicata" e invita ad "avvisami".
