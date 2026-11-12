# Verifica indipendente: clone tedesco di EsameB1 (Einbürgerungstest + DTZ/B1 per città) — 12/11/2026

Riapre la riserva della ricerca `ricerca-cloni-esameb1-2026-10-30.md` (sez. 3.1, voto 7,5) e il test `de-test/ESITO.md` (30/10: 31 sedi su 85 con date leggibili, soglia 60 %). Tutto letto oggi dal server, senza browser e senza aggirare blocchi (robots.txt rispettato, 403/429 lasciati stare).

## Verdetto: NO (voto 4,5 — era 7,5 e poi 7)

Due motivi, ognuno basta da solo:

1. **La soglia non si raggiunge.** Oggi le sedi con almeno una data futura leggibile sono **33 su 85 (38,8 %)** con lo stesso metodo del 30/10, e **38 su 85 (44,7 %)** aggiungendo una fonte nuova trovata oggi (il catalogo nazionale delle VHS, vedi sez. 1.3). La soglia era 60 %. Novembre non ha cambiato il quadro: le date del 2027 sono uscite nelle sedi che già pubblicavano, non nelle altre.
2. **Il buco non c'è più.** Esiste un sito tedesco che fa esattamente questo, e lo fa meglio di quanto potremmo fare noi: **einbuergerungstest-termine.de** (Impressum datato ottobre 2026, quindi nato nelle ultime settimane; non compariva nella ricerca del 30/10). Legge da solo 227 sedi in 209 città più volte al giorno, mostra per ogni data se ci sono posti, ha 292 pagine città per l'Einbürgerungstest, 112 per la B1 e 27 sul DTZ, in 5 lingue, con un avviso via email a pagamento (12,90 €). Con la regola del 10/11 (senza un vuoto dimostrato il voto massimo è 5) l'idea scende sotto l'asticella.

Stima a 18 mesi se si costruisse lo stesso: **150 / 900 / 4.000 €/anno** (prudente / centrale / ottimista), contro i 5.000 centrali richiesti per un sito nuovo. Ore: 35-45. Non si costruisce.

---

## 1. Date leggibili oggi

### 1.1 Stesso test del 30/10, rifatto (85 sedi, 20 città)

Stessi script (`cerca_date.py`, poi `estrai_date.py`), stessa lista di sedi BAMF, data di oggi. I risultati nuovi stanno in file separati (`grezzi/date_2026-11-12/`, `grezzi/estratte_2026-11-12.json`): quelli del 30/10 non sono stati toccati.

| | 30/10 | 12/11 |
|---|---|---|
| Sedi con almeno una data futura dell'Einbürgerungstest | 31 | **32** |
| Sedi con almeno una data futura di Einbürgerungstest o DTZ | 32 | **33 (38,8 %)** |
| di cui con almeno una data nel 2027 | n.d. | 25 |
| Sedi con una tariffa in euro leggibile vicino al nome del test | n.d. | 33 |
| Sedi con date **e** tariffa | n.d. | 28 |
| Date d'esame lette in tutto | n.d. | 160 (110 nel 2027) |

Cambi rispetto al 30/10: entra la VHS Chemnitz, esce la VHS Wiesbaden (oggi nessuna data futura sulla pagina). Tutto il resto è uguale.

Tariffe: 28 sedi scrivono 25 € (la tariffa nazionale dell'Einbürgerungstest); per gli esami di lingua si leggono importi tra 140 e 200 € in 8 sedi. Il conteggio delle tariffe è largo (un importo a meno di 200 caratteri dal nome del test), non è stato controllato a mano.

Avvertenza sul 33: a Dortmund una delle due "sedi con date" ha in parte finestre di prenotazione ("Terminanmeldung… von… bis…") lette come date d'esame, l'errore già segnalato il 30/10. Oggi però la stessa pagina ha anche una data vera (11/12/2026, 25,00 €), quindi la sede resta nel conto.

| Città | Sedi BAMF | con date (crawl) | con date (crawl + catalogo VHS) |
|---|---|---|---|
| Hamburg | 9 | 4 | 4 |
| Berlin | 12 | 2 | 2 |
| Frankfurt | 6 | 1 | 2 |
| München | 7 | 2 | 2 |
| Köln | 4 | 3 | 3 |
| Stuttgart | 1 | 1 | 1 |
| Essen | 2 | 1 | 2 |
| Leipzig | 6 | 3 | 3 |
| Ulm | 1 | 1 | 1 |
| Düsseldorf | 8 | 4 | 5 |
| Hannover | 7 | 4 | 4 |
| Nürnberg | 2 | 0 | 0 |
| Mannheim | 2 | 1 | 1 |
| Karlsruhe | 1 | 0 | 0 |
| Wiesbaden | 5 | 1 | 1 |
| Erfurt | 2 | 0 | 0 |
| Regensburg | 1 | 0 | 1 |
| Dortmund | 2 | 2 | 2 |
| Augsburg | 1 | 0 | 1 |
| Chemnitz | 6 | 3 | 3 |
| **Totale** | **85** | **33 (38,8 %)** | **38 (44,7 %)** |

Città con almeno 3 sedi con date: solo **6 su 20** (Hamburg, Köln, Leipzig, Düsseldorf, Hannover, Chemnitz). Città senza nessuna data: Nürnberg, Karlsruhe, Erfurt (più Regensburg e Augsburg senza il catalogo VHS). Berlino resta a 2 su 12: le altre 10 VHS rimandano agli appuntamenti su service.berlin.de.

### 1.2 Elenchi ufficiali del BAMF

- Le pagine `bamf.de/…/Pruefstellen-<LAND>.html` rispondono ancora 200 (riletta NRW) e continuano a dare solo indirizzi, **senza date**.
- BAMF-NAvI (`bamf-navi.bamf.de`, 200) cerca corsi di integrazione e corsi di lingua per il lavoro, non le date dell'Einbürgerungstest.
- telc: la pagina "Prüfungszentrum finden" risponde 200 ma è vuota senza JavaScript; la pagina delle date d'esame dà 404. g.a.s.t.: pagina DTZ 404. KURSNET (Agenzia del lavoro): 200, ma è una ricerca in JavaScript sui corsi, non sugli esami.

Nessun calendario ufficiale unico dal BAMF, da telc o da g.a.s.t.

### 1.3 Fonte nuova: il catalogo nazionale delle VHS

La pagina `volkshochschule.de/kursfinder` (Deutscher Volkshochschul-Verband) è vuota senza JavaScript, ma i dati arrivano da un indirizzo JSON pubblico: `api.volkshochschule.de/3/veranstaltungen`. Risponde 200 senza chiave e il suo robots.txt non vieta nulla. Script: `de-test/leggi_api_vhs.py`; dati essenziali (senza testi): `de-test/grezzi/api_vhs_2026-11-12.json`.

Letto oggi (eventi futuri il cui titolo è un esame, non un corso di preparazione):

| | Einbürgerungstest / Leben in Deutschland | Esami B1 (DTZ, telc B1, A2-B1) |
|---|---|---|
| Eventi futuri | 630 | 276 |
| VHS diverse | 156 | 93 |
| Luoghi | 167 | 100 |
| Con prezzo > 0 | 609 (555 a 25,00 €) | 217 (tra 150 e 190 € i più comuni) |
| Con stato dei posti (liberi / pochi / lista d'attesa) | 568 | 275 |
| Nel 2027 | 407 | 139 |

È la fonte "unica" che il 30/10 mancava, ma non basta per la soglia:
- copre **solo le VHS che caricano i corsi nel catalogo nazionale** (156 su circa 660 sedi BAMF);
- nelle 20 città aggiunge 5 sedi che il crawl non leggeva (VHS Frankfurt, Essen, Regensburg, Augsburg; VHS Düsseldorf solo per la B1), per un totale di 38 su 85;
- **Hamburg, Berlin, Leipzig, Nürnberg, Mannheim, Karlsruhe, Wiesbaden, Erfurt e Chemnitz non hanno nessun esame nel catalogo**; München e Köln ne hanno 3 e 4;
- i luoghi più ricchi sono città medie e piccole (Neuwied 32 eventi, Ludwigshafen 24, Braunschweig 18, Hamm 14, Wolfsburg 14), dove la domanda è più bassa;
- le condizioni di riuso non sono scritte da nessuna parte (l'Impressum di volkshochschule.de non parla dell'API): prima di pubblicare servirebbe il permesso del DVV.

Resta un ritrovamento utile da tenere a mente: è un catalogo aperto di tutti i corsi VHS con data, prezzo e posti.

## 2. Domanda (autocomplete Google, hl=de gl=de, 12/11/2026)

Dati completi: `de-test/grezzi/autocomplete/domanda_2026-11-12.json`. La domanda è confermata e forte; non è questo il problema.

Frasi generali (numero di suggerimenti):

| Frase | N. | Cosa esce |
|---|---|---|
| einbürgerungstest anmeldung | 10 | online, berlin, münchen, formular, vhs, hamburg, köln, frankfurt, stuttgart |
| einbürgerungstest termine | 10 | in der nähe, berlin, hamburg, leipzig, düsseldorf, nürnberg, nrw, hannover, dortmund |
| einbürgerungstest ergebnis | 10 | online, dauer, bamf, bayern, nrw, hamburg, dauer 2026, nicht erhalten, hessen |
| einbürgerungstest in der nähe | 10 | termine, münchen, vhs, freie termine in der nähe |
| einbürgerungstest freie termine | 9 | neuss, hamburg, bayern, nrw, münchen, berlin |
| leben in deutschland test termine | 10 | in der nähe, berlin, online, nrw, dortmund, leipzig, münchen, hamburg, stuttgart |
| dtz prüfung termine | 10 | in der nähe, berlin, 2026, frankfurt, essen, münchen, hamburg |
| b1 prüfung termine | 10 | in der nähe, berlin, köln, hamburg, nrw, dtz, nürnberg, erfurt, bielefeld |
| telc b1 prüfung termine | 10 | in der nähe, berlin, frankfurt, bielefeld, nürnberg, bremen, düsseldorf, münchen, nrw |
| b1 prüfung einbürgerung | 8 | telc, vhs, online, dtz, welche b1 prüfung |
| b1 prüfung anmeldung | 5 | nürnberg, dtz, telc |
| einbürgerungstest termine 2027 | 0 | (nessuno cerca ancora l'anno nuovo) |

Per città (suggerimenti per "einbürgerungstest X" / "einbürgerungstest termine X" / "dtz prüfung X" / "b1 prüfung X" / "telc b1 prüfung X" / "leben in deutschland test X"; somma su 60):

| Città | Conteggi | Somma |
|---|---|---|
| Hamburg | 10 / 8 / 10 / 10 / 9 / 10 | 57 |
| Berlin | 10 / 9 / 8 / 10 / 10 / 10 | 57 |
| Frankfurt | 10 / 6 / 9 / 10 / 10 / 9 | 54 |
| München | 10 / 6 / 5 / 10 / 10 / 10 | 51 |
| Stuttgart | 10 / 5 / 5 / 10 / 9 / 6 | 45 |
| Köln | 10 / 6 / 4 / 10 / 5 / 8 | 43 |
| Düsseldorf | 10 / 4 / 4 / 10 / 9 / 4 | 41 |
| Hannover | 10 / 4 / 4 / 10 / 5 / 6 | 39 |
| Nürnberg | 10 / 3 / 5 / 10 / 5 / 6 | 39 |
| Dortmund | 10 / 3 / 6 / 10 / 6 / 3 | 38 |
| Bremen (fuori dalle 20) | 10 / 4 / 4 / 10 / 5 / 4 | 37 |
| Mannheim | 10 / 4 / 3 / 10 / 4 / 4 | 35 |
| Essen, Leipzig, Ulm, Augsburg, Bonn | | 32 ciascuna |
| Karlsruhe, Regensburg, Freiburg | | 30 |
| Wiesbaden | | 29 |
| Erfurt | | 24 |
| Chemnitz | | 20 |

Le città con più domanda (Hamburg, Berlin, Frankfurt, München, Stuttgart) sono proprio quelle dove leggiamo meno sedi: 4 su 9, 2 su 12, 2 su 6, 2 su 7, 1 su 1.

**Naturalizzazioni (Destatis, tabella "Einbürgerungen nach Altersgruppen…", letta oggi, 200):** 333.343 nel 2025, di cui 185.512 tra 20 e 45 anni; Europa 143.592, Paesi UE 36.641 (Romania 8.302, Polonia 6.292, Italia 4.134). Conferma la cifra usata il 30/10. Da quest'anno Destatis pubblica anche le domande presentate; la cifra non era nella pagina letta.

## 3. Concorrenti su 5 città (Köln, Hamburg, München, Leipzig, Nürnberg)

| Sito | Sedi per città | Date | Tariffe | Fonte e data del controllo | Guadagna con |
|---|---|---|---|---|---|
| **einbuergerungstest-termine.de** | sì, con la distanza (Köln 61 sedi entro 100 km, Hamburg 20, München 14, Leipzig 11, Nürnberg 11) | **sì**: Köln 107 date diverse, Leipzig 29, Nürnberg 20, Hamburg 15, München 10, con lo stato "posti liberi / pochi / pieno / lista d'attesa" e la data di apertura delle iscrizioni | solo i 25 € nazionali in una guida; nessuna tariffa per sede, nemmeno per la B1 | sì: link a ogni sede e "geprüft heute, 17:00 Uhr" | avviso via email a 12,90 € (60 giorni, rimborso se non arriva nessun avviso) + un link Awin (traduzioni giurate); nessuna pubblicità |
| einbuergerungstest-online.de | elenco per Land copiato dal BAMF (nome e indirizzo) | no | no | "wenden Sie sich an das BAMF" | quiz, pubblicità |
| lebenindeutschland.eu | lo stesso elenco per Land | no | no | no | quiz |
| einbuergerungstest-online.eu | elenco per Land | no | no | no | quiz |
| migrando.de | pagine "Einbürgerung in Köln / Hamburg / …" sull'ufficio e sulla pratica; nessuna sede d'esame | no | 25 € nazionali | no | consulenza a pagamento |
| Pagine delle VHS | la propria sede | sì dove pubblicano (vedi sez. 1) | sì (25 €; B1 150-200 €) | sono la fonte | — |
| b1-pruefung.de | una sola scuola di Francoforte | le proprie | non lette | — | vende i propri esami |
| lebenindeutschland.org | non letto (429) | | | | |
| Make it in Germany | non letto (pagina di blocco anti-robot) | | | | |
| Giornali locali | non letti: i motori di ricerca non rispondono al server (DuckDuckGo 202 con verifica) | | | | |

Il sito einbuergerungstest-termine.de in numeri (home e sitemap lette oggi):
- "Wir prüfen 227 Prüfstellen in 209 Städten mehrmals am Tag"; in elenco 307 sedi, di cui 227 lette da programma e 80 con il solo link. Oggi: 28 con posti liberi, 3 con pochi posti o lista d'attesa, 11 piene, 137 "Plätze unklar", 128 senza date online;
- sitemap: 476 indirizzi, di cui 292 pagine `/termine/<città>`, 112 `/b1-pruefung/<città>`, 27 sul DTZ (compiti di scrittura con controllo automatico del testo, novità DTZ dal 1/11/2026), guide, e le versioni in turco, inglese, arabo e persiano;
- un riquadro da incorporare nei siti di altri (`/einbetten`), cioè un modo per farsi linkare da VHS e associazioni;
- pagine città piene: Köln circa 4.100 parole e 77 link esterni, le altre circa 2.000 parole.

Anche lui legge da programma circa un terzo delle sedi BAMF (227 su circa 660): è lo stesso tetto che abbiamo misurato noi. La differenza è che lui c'è già, copre tutta la Germania, controlla più volte al giorno e dice se c'è posto.

**Cosa gli manca** (letto sulle 5 città): la tariffa sede per sede degli esami B1, i tempi dei risultati per Land ("einbürgerungstest ergebnisse nrw / bayern / hessen" hanno domanda), le sedi Goethe, e le lingue russa, ucraina, romena, polacca e italiana. Sono aggiunte, non un sito: nessuna regge da sola 5.000 €/anno, e la parte che porta le visite (date per città) è già presa.

## 4. Chi paga (cifre lette oggi)

| Programma | Cifra letta | Stato |
|---|---|---|
| italki | la pagina pubblica scrive "at least $10 USD" per ogni studente nuovo che compra; il nostro link attivo su EsameB1 rende 18 $ (NOTE di EsameB1) | attivo, vale per qualsiasi lingua |
| Amazon.de (PartnerNet, tabella delle commissioni, 200) | libri nel gruppo al 4,5 % (lettura dal testo senza impaginazione: da ricontrollare nel pannello); su un libro da 15-20 € sono 0,70-0,90 € | **nessun account Amazon.de**: nel repository ci sono solo i tag Italia (`-21`), Regno Unito e Stati Uniti. Servirebbe un'iscrizione nuova |
| Lingoda | "competitive commission rates… every payout is tailored to every unique partnership": **nessuna cifra scritta** | non usabile nelle stime |
| Babbel | pagina del programma non trovata (404 su babbel.com/affiliates; pagine Awin 404). I "fino a 75 € a vendita" del 26/10 non sono stati riletti | non confermato oggi |
| Preply | 403 (rinvio al login) | non letto |
| AdSense Germania | nessuna cifra ufficiale; nei nostri file l'ipotesi è circa 14 $ ogni 1.000 pagine viste (modello adstimate del 29/7/2026, dichiarato come stima) | ipotesi, non cifra letta |

Il concorrente non usa né AdSense né corsi di lingua: vende l'avviso a 12,90 €. Per noi i pagamenti restano fuori (regole fisse: solo quando i ricavi coprono il costo fisso), quindi non possiamo rispondere con lo stesso prodotto.

## 5. Stima se si costruisse comunque (non proposto)

Disegno ridotto possibile: pagine città solo dove almeno 3 sedi hanno date (6 città delle 20; con il catalogo VHS su tutta la Germania forse 25-35 luoghi), elenco BAMF per il resto, niente pagine sottili.

- **Prudente 150 €/anno**: 1.000 visite al mese (secondi dietro un sito più completo e aggiornato più spesso) × 12 × 12 € ogni 1.000.
- **Centrale 900 €/anno**: 3.000 visite al mese × 12 × 25 €.
- **Ottimista 4.000 €/anno**: 12.000 visite al mese × 12 × 27 €, solo se il concorrente si ferma.
- Ore: 35-45 (lettori per sito, testi in tedesco, revisione), più l'Impressum tedesco obbligatorio con nome e indirizzo.
- Rischi: AdSense «contenuti di scarso valore» (pagine città con 1-2 sedi e poche date sono proprio il caso che ha fatto rifiutare EsameB1 l'8/11); Berlino, la seconda città per domanda, resta quasi vuota; permesso del DVV per il catalogo.

Sotto l'asticella dei siti nuovi (voto ≥ 7 e ≥ 5.000 €/anno centrali) in tutti e tre i casi tranne l'ottimista, che non la raggiunge comunque.

**Voto 4,5.** Domanda provata (resta), fonte a metà (38 su 85), vuoto chiuso da un concorrente diretto, pagatori deboli (un solo programma con cifra scritta, 10-18 $).

## 6. Cosa farebbe cambiare il verdetto

1. **Il concorrente si ferma.** Controllo semplice tra 3 mesi (febbraio 2027): la riga "Zuletzt geprüft" in home e il `lastmod` della sitemap. Se sono vecchi di settimane, il vuoto si riapre e il catalogo VHS (sez. 1.3) dà una base migliore di quella del 30/10.
2. **Berlino pubblica le date** fuori dal sistema di appuntamenti, oppure telc / g.a.s.t. / BAMF pubblicano un calendario per sede: la quota leggibile salirebbe sopra il 60 %.
3. **Un pagatore con cifra scritta più alta** per chi prepara la B1 in Germania (per esempio Babbel o Lingoda con una tariffa pubblica a vendita), abbastanza da reggere anche con poche visite.

Senza almeno la 1 o la 2, non riaprire.

## File

| File | Contenuto |
|---|---|
| `de-test/cerca_date.py`, `de-test/estrai_date.py` | ora leggono la data e il suffisso dei file dalle variabili `DE_TEST_OGGI` e `DE_TEST_SUFFISSO` (senza variabili si comportano come il 30/10); l'estrattore conta anche le tariffe |
| `de-test/grezzi/date_2026-11-12/`, `date_risultati_2026-11-12.json`, `estratte_2026-11-12.json` | la passata di oggi sulle 85 sedi (solo date, tipo, tariffe e pagina fonte; nessun testo) |
| `de-test/leggi_api_vhs.py`, `de-test/grezzi/api_vhs_2026-11-12.json` | lettore del catalogo nazionale delle VHS e i 906 eventi d'esame futuri letti oggi. Lo script è la versione ripulita di quello usato oggi (toglie i segni di evidenziazione dai titoli prima di classificarli): rilanciato può dare conteggi di poco diversi |
| `de-test/grezzi/autocomplete/domanda_2026-11-12.json` | i suggerimenti di Google di oggi (15 frasi generali, 23 città × 6 frasi) |
