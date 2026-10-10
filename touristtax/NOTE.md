# Tourist Tax Calculator – note di lavoro

Stato al **10 ottobre 2026**: sito costruito, **non pubblicato**. Nome: Tourist Tax Calculator. Indirizzo previsto:
`https://tourist-tax-calculator.netlify.app` (costante `URL_SITO` in `genera.py`, unico punto da cambiare).
Origine: studio `studio-business/intelaiatura/18-mondo-paesi-lingua-locale.md` sez. 2.1 e studio 16 sez. 2.1.
Risultati del test a costo zero e dei controlli: `TEST.md` (29 destinazioni con dati ufficiali completi, soglia 25).

## Struttura

| File | Cosa fa |
|---|---|
| `genera.py` | un comando costruisce tutto `sito/` (pagine, sitemap, robots, 404, `netlify.toml`, `data/fr.json`) |
| `verifica.py` | esempi a mano, confronto motore JS/Python, link interni, fonte + data su ogni pagina |
| `raccolta/francia.py` | scarica il dataset DGFiP DELTA (solo righe 2026) e la capacità turistica INSEE 2026, scrive `dati/francia.json` e `dati/francia_top.json` |
| `dati/destinazioni.json` | una voce per destinazione: paese, nome, slug, valuta, tipo di regola, tariffe (con date e mesi), età esenti, notti massime, riduzioni, fonti (URL, HTTP, formato, data del controllo), note |
| `dati/affiliati.json` | riquadro affiliati: **vuoto** (URL vuoti → non compare nulla). Da riempire con Stay22 / Booking / assicurazione dopo l'iscrizione |
| `sito/` | il sito statico da pubblicare (base directory su Netlify: `touristtax/sito`) |

Comandi (dalla radice del repository):

```
python3 -I touristtax/raccolta/francia.py --cache /tmp/touristtax-fr   # solo quando si aggiorna la Francia
python3 touristtax/genera.py
python3 touristtax/verifica.py
```

Tipi di regola nel calcolatore: `per_person` (importo fisso a persona per notte), `per_room` (a camera/unità per notte:
Grecia, Islanda), `percent` (percentuale del prezzo: Amsterdam, Berlino, Vienna, Edimburgo, Turchia, Kutchan),
`bands` (fasce di prezzo a persona: Kyoto, Tokyo, Sapporo, Hakuba), `per_trip` (una volta per viaggio: Bali), `france`
(tariffa comunale + tasse aggiuntive; non classificati = % del costo a persona con tetto). Le tariffe hanno date
(`dal`/`al`) e mesi: il calcolatore guarda la data di ogni notte, quindi gestisce i cambi a metà soggiorno
(Vienna 1/7, Turchia 1/5/2026, Milano 1/4/2026, Catalogna 1/4/2027) e le stagioni (Baleari, Grecia).
La formula usata è stampata sotto il calcolatore in ogni pagina.

## Fonti (tutte controllate il 10/10/2026; elenco completo con URL in `dati/destinazioni.json` e nella pagina /about/)

- Francia: DGFiP "Tarifs taxe de séjour – DELTA" (Licence Ouverte 2.0, aggiornato 29/06/2026), regole: service-public F31635 e guida DGCL (fiche 4 e 6, giugno 2026). Pagine comunali: 150 comuni con più posti turistici INSEE 2026.
- Spagna: ATC Catalogna (Barcellona e resto), BOE testo consolidato legge 2/2016 Baleari.
- Grecia: ΦΕΚ Α' 198/2024 (legge 5162/2024 art. 24). AADE dà 403.
- Turchia: Resmî Gazete 1/5/2026 (Decisione 11263, 1% fino al 31/12/2026) + guida GİB.
- Amsterdam: CVDR703815 (ordinanza 2024 ancora in vigore). amsterdam.nl dà 403.
- Berlino, Vienna, Praga, Edimburgo, Roma, Firenze, Milano, Kyoto, Tokyo, Sapporo, Kutchan, Hakuba, Bali, Islanda: pagine o atti ufficiali (vedi JSON).

## Cosa controllare ogni trimestre (routine del lunedì, una settimana su tredici) e prima del 1° gennaio e del 1° aprile

1. Rilanciare `verifica.py` e aprire tutte le fonti di `dati/destinazioni.json` (le 200 si leggono anche in automatico; AADE, amsterdam.nl danno 403: controllo a mano).
2. Date di cambio già note:
   - **31/12/2026** Turchia: scade la Decisione 11263 (1%); dal 1/1/2027 torna il 2% di legge salvo nuova decisione nella Gazzetta.
   - **31/12/2026** Milano: le tariffe 2026 finiscono; cercare le tariffe 2027 su comune.milano.it.
   - **gennaio 2027** Oita (Giappone) e **1/2/2027** Okinawa, Ishigaki, Miyakojima, Nago, Motobu, Onna, Chatan: nuove tasse (elenco MIC) → nuove pagine.
   - **1/3/2027** Wakkanai, Shirahama; **1/4/2027** Tomakomai, Yamagata, Fujiyoshida, Fujikawaguchiko, Unzen, Kagoshima, Ibusuki (elenco MIC).
   - **31/3/2027** Barcellona: la tabella ATC non ha ancora la tariffa generale da aprile 2027 (il calcolatore si ferma); il supplemento sale a €6. Catalogna: tariffe dal 1/4/2027 già inserite.
   - **1/4/2027** Tokyo: passaggio previsto al 3% con soglia ¥13.000, inclusi minpaku e simple lodging (pagina del Bureau of Taxation: "予定") → aggiornare quando confermato.
   - **1/7/2027** Vienna: 8% (già inserito).
   - **1/6/2029** Hakuba e Nagano: fine delle tariffe ridotte dei primi 3 anni (già inserito).
   - **giugno-luglio** di ogni anno: nuovo aggiornamento DELTA (le delibere per l'anno dopo vanno prese prima del 1° luglio) → rilanciare `raccolta/francia.py` con `ANNO` = anno successivo quando compaiono le righe con data d'effetto 2027 e pubblicare le pagine "2027" a novembre-dicembre.
3. Nuove destinazioni: controllare l'elenco MIC (`soumu.go.jp`, "法定外税の状況") e il feed `soumu.go.jp/news.rdf`.

## Destinazioni escluse (da verificare)

| Destinazione | Motivo | Cosa serve per aggiungerla |
|---|---|---|
| Venezia (imposta + contributo d'accesso) | comune.venezia.it e cda.ve.it danno 403 | lettura a mano della delibera tariffe e del calendario dei giorni di accesso, o una fonte ufficiale alternativa leggibile |
| Lisbona | lisboa.pt 403 | regolamento pubblicato nel Diário da República |
| Porto | porto.pt non serve il contenuto della pagina | regolamento nel Diário da República o PDF ufficiale |
| Algarve | nessun regolamento comunale letto | regolamenti di Albufeira, Faro, Lagos, Portimão, Loulé |
| Budapest | tassa decisa dai distretti | delibere dei distretti centrali (V, VI, VII, VIII) |
| Dubrovnik, Spalato | decisioni delle contee 2026 non trovate | Gazzetta ufficiale delle contee |
| Osaka | pref.osaka.lg.jp risponde 408 al server | lettura a mano o consenso MIC sul cambio 2025 |
| Glasgow | glasgow.gov.uk 403 | pagina del Council o schema ufficiale |
| Quintana Roo (Visitax) | l'importo in pesos non è sulla pagina ufficiale (2,5 UMA) | Ley de Derechos art. 51 octies + valore UMA ufficiale |
| Okinawa | in vigore solo dal 1/2/2027 | pagina da aggiungere a gennaio 2027 |
| Egitto, Marocco, Canarie | nessuna fonte ufficiale con tariffa | – |
| Francia: comuni senza righe 2026 nel file DGFiP (es. Nizza, Marsiglia, Tolosa) | le tariffe nel file sono di anni precedenti | non si mostrano: la ricerca dice di chiedere al comune |

## Note e limiti noti

- Bali: sul portale ufficiale c'è l'importo (IDR 150.000) ma il PDF del regolamento dà 403; non scriviamo "per visita" né l'elenco delle esenzioni.
- Kutchan: il 3% è il totale (Hokkaido + comune) secondo il poster ufficiale dell'Hokkaido; Niseko Town, Rusutsu, Akaigawa hanno regole proprie, non coperte.
- Hakuba: si sommano tassa del villaggio e tassa di Nagano (metà della tariffa prefettizia, come da consenso MIC).
- Francia: due comuni hanno righe in conflitto nel file (Le Barcarès, Saméon): nessuna tariffa mostrata.
- Nessuno script esterno, nessun cookie. Spazio pubblicità: `<div class="ad-slot">` (vuoto, nascosto finché vuoto).
- Link "Spotted a change? Tell us" in ogni pagina → modulo contatti Netlify Forms con honeypot.

## Pubblicazione (da fare da Massimiliano)

1. Netlify → Add new site → Import from Git → repository `copertine-libri`, branch `ccr-b7fd6b9e-n096cr`,
   **base directory `touristtax/sito`**, build command vuoto, publish directory `.` (lo dice anche `sito/netlify.toml`).
   Nome del sito: `tourist-tax-calculator` (se è preso, cambiare `URL_SITO` in `genera.py` e rigenerare).
   Il file `netlify.toml` pubblica solo quando cambia qualcosa in `touristtax/sito` (crediti Netlify condivisi).
2. Netlify → Forms: attivare il rilevamento dei moduli (modulo "contact") e le notifiche email.
3. Google Search Console: aggiungere la proprietà `https://tourist-tax-calculator.netlify.app/`, verificare con il file
   HTML (va in `touristtax/sito/`, `genera.py` lo conserva) e inviare `sitemap.xml`.
