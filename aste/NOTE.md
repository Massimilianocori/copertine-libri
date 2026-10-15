# Aste in Chiaro (case all'asta + valori OMI di zona) – note di lavoro

Approvato da Massimiliano il 15/10/2026 (parte (a) di `studio-business/intelaiatura/affari-test-fonti.md`).
Costruito il 15/10/2026. Sito statico in italiano: per ogni casa all'asta del Portale delle Vendite Pubbliche (PVP) mostra
prezzo base, offerta minima, data, comune, occupazione, superficie (se scritta) e il prezzo al m² confrontato con la media OMI
della zona («Agenzia delle Entrate – OMI», CC BY 4.0), con il link alla scheda ufficiale.
Indirizzo previsto: `https://aste-giudiziarie-sconti.netlify.app` (costante `URL_SITO` in `genera.py`, unico punto da cambiare).
Il sito Netlify NON è stato creato: lo crea Massimiliano (impostazioni sotto).

## Comandi

| Quando | Comando (dalla radice del repository) | Cosa fa |
|---|---|---|
| **Ogni sera** (routine) | `python3 aste/raccolta/aggiorna.py && git add aste/dati && (git diff --cached --quiet \|\| git commit -m "Aste: dati del giorno") && git pull --rebase origin ccr-b7fd6b9e-n096cr && git push origin ccr-b7fd6b9e-n096cr` | rilegge le aste attive sul PVP (≈25 richieste), scarica al massimo 700 dettagli nuovi (uno ogni 3 s), trova le zone OMI dei lotti nuovi, riscrive `aste/dati/` (anche `live.json`). **Nessuna pubblicazione Netlify**: `aste/dati/` è fuori da `aste/sito/` |
| Ogni settimana | il comando sopra, poi `python3 aste/genera.py && python3 aste/verifica.py --browser` e commit di `aste/` | rigenera le pagine (nuove aste, nuove città); il commit di `aste/sito/` fa partire una pubblicazione |
| Se il PVP è fermo | `python3 aste/raccolta/aggiorna.py --senza-pvp` (o `--offline`) | rielabora dalla cache; con il portale fermo `aggiorna.py` si ferma con un messaggio e **non** tocca i dati |
| Controllo a campione | `python3 aste/raccolta/controllo.py` | 10 lotti riletti senza cache su PVP e OMI, tabella Markdown |
| Immagine di condivisione | `node aste/grafica/og.js` | rigenera `grafica/og.png` |

Tempi: elenco 1-2 minuti; dettagli nuovi di un giorno normale (100-200 lotti) 5-10 minuti; la prima esecuzione completa (≈3.600
dettagli) richiede più giorni con il tetto di 700 al giorno. Senza cache (sessione nuova) i lotti già elaborati si riprendono da
`dati/lotti.json` (campo `fonte: "dettaglio"`): si scaricano solo i dettagli dei lotti nuovi.

## Freschezza senza pubblicazioni giornaliere

- Ogni pagina con aste carica `https://raw.githubusercontent.com/massimilianocori/copertine-libri/ccr-b7fd6b9e-n096cr/aste/dati/live.json`
  (stesso metodo di `italystrikes` con `vista.json`). Se il file è più recente della pagina: aggiorna prezzo base, offerta minima,
  data e ricalcola €/m² e sconto; **nasconde** i lotti che non ci sono più (asta svolta, sospesa, aggiudicata, tolta) e mostra
  accanto al conteggio «nascoste N aste già svolte o tolte dal PVP».
- Anche senza `live.json` (rete assente) il browser nasconde da solo le aste con data/ora passata (ora di Roma).
- `live.json` contiene solo i lotti pubblicati: `{"letto_il", "n", "lotti": {"id": [base, minima, "AAAA-MM-GGTHH:MM"]}}`.
- Provato con Playwright (`verifica_browser.js`): un `live.json` finto senza un lotto e con un prezzo cambiato → lotto nascosto,
  prezzo aggiornato.

## Netlify (da fare: Massimiliano)

- Nuovo sito da Git, repository `Massimilianocori/copertine-libri`, branch `ccr-b7fd6b9e-n096cr`.
- **Base directory: `aste/sito`**, **Build command: vuoto**, **Publish directory: `aste/sito`** (cioè «.» dentro la base).
- Nome del sito: `aste-giudiziarie-sconti` (se è preso, cambiare `URL_SITO` in `genera.py` e rigenerare).
- `aste/sito/netlify.toml` (generato) ha la stessa regola di `floodcost`: `ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."`
  → pubblica solo se è cambiato qualcosa in `aste/sito/`. I commit giornalieri di `aste/dati/` non consumano crediti.
- Search Console: meta di verifica già in ogni pagina (`GOOGLE_VERIFICA`, stesso account degli altri siti); poi inviare `sitemap.xml`.
- Modulo `contatti` (Netlify Forms): attivare le notifiche email.

## File

| File | A cosa serve |
|---|---|
| `raccolta/rete.py` | richieste gentili (firma da browser, PVP una richiesta ogni ~3 s, GEOPOI ~1,5 s, nuovi tentativi 20/40/80/120 s); ricava ogni volta gli indirizzi versionati del PVP (`fe-config/lista-annunci` → `msUrl`); `dettaglio_pulito()` scarta `soggetti`, allegati, procedura, pegno e dati catastali **prima** di salvare |
| `raccolta/aggiorna.py` | elenco, dettagli, superficie, diritto venduto, zona OMI, quotazioni; scrive `dati/` |
| `raccolta/controllo.py` | controllo a campione su PVP e OMI senza cache |
| `genera.py` | sito in `sito/` (asset esterni con impronta nel nome, tema chiaro/scuro, sitemap, robots, privacy, 404, `netlify.toml`) |
| `verifica.py` | link, sitemap, meta, dati personali (email, codici fiscali, telefoni, campi PVP personali) in pagine, dati e cache, attribuzione OMI e semestre, link PVP per ogni lotto, date, parole vietate, riquadro mutuo, nomi di servizi di IA, `live.json`; `--browser` lancia Playwright |
| `verifica_browser.js` | Playwright 390/1280 px, chiaro/scuro: scorrimento orizzontale, errori JS, richieste fallite, tema, filtri, ordinamento, `live.json` |
| `dati/lotti.json`, `auto.json`, `omi.json`, `live.json` | dati pubblicati (nessun dato personale) |
| `dati/affiliati.json` | riquadro «mutuo per l'asta»: **nascosto** finché `mutuo.url` è vuoto. Solo URL veri di un programma (es. Awin), mai inventati |
| `grafica/` | font (Figtree, Source Serif 4, OFL), `og.html` + `og.js` → `og.png` |
| `cache/` (fuori da git) | risposte grezze: elenco, dettagli già ripuliti, perimetri e schede OMI, screenshot |

## Edizione del 15/10/2026 (PVP letto alle 19:22, OMI 2° semestre 2025)

| Tipo di pagina | Quante | Regola |
|---|---|---|
| Home | 1 | numeri nazionali, città, per 8 città le 2 aste (pubblicate nelle ultime 3 settimane, se ci sono) con lo sconto più alto sull'offerta minima, guide |
| Città | 188 | comuni con almeno **8** aste di case attive dopo le esclusioni (Roma 159, Policoro 82, Torino 70, Napoli 61, Messina 59, Palermo 56, Catania 56, Bari 42, Genova 40, Milano 27…). Bologna (3), Venezia (7), Verona (6) oggi **non** arrivano a 8: la pagina nasce da sola quando ci arrivano |
| Fasce di prezzo | 124 | città con almeno 15 aste; fascia (sul prezzo base: fino a 50.000, 50-100.000, 100-200.000, oltre 200.000 €) con almeno 5 aste e non più del 70% delle aste della città (altrimenti sarebbe un doppione) |
| Zone OMI | 110 | almeno 4 aste nella zona e non più del 70% della città; con tabella delle quotazioni della zona |
| Auto all'asta | 1 | nazionale, 1.043 veicoli (436 auto, 326 commerciali, 84 moto, 197 altri): per tipo le 40 aste più vicine; niente targa né testo dell'annuncio |
| Guide | 6 + indice | come funziona l'asta, offerta minima, casa occupata, rischi, mutuo, valori OMI; ogni regola con l'articolo su Normattiva (riletti il 15/10/2026: artt. 490, 560, 568-573, 579, 585-587, 591, 591-bis c.p.c.; 2922-2923 c.c.; art. 63 disp. att. c.c.; D.M. 32/2015) |
| Fisse | 5 + 404 | indice città, metodo, chi siamo, contatti (modulo Netlify), privacy |
| **Totale** | **436 indicizzabili** + 404 | tutte nella sitemap; 16 MB in tutto (pagina più pesante: Roma, 371 kB non compressi) |

Dati rielaborati il 15/10/2026 sera dopo la revisione indipendente (vedi sotto): stessa lettura del PVP delle 19:22.
Lotti: **3.090** case all'asta pubblicate (vendita da adesso in poi; 56 lotti con asta già passata alle 20 esclusi dalla generazione),
di cui **696 con il confronto €/m²** sulla media OMI (1.352 con superficie, 1.916 con zona OMI; 202 «quota o diritto parziale?»,
97 «superficie da verificare»).
Occupazione: non indicata 1.589, occupato 830, libero 483, occupato senza titolo 139, in liberazione 48.
Mediana dello sconto con l'offerta minima: −41% (63 lotti sopra la media, 18 in linea).
804 lotti sono ancora pubblicati con i soli campi dell'elenco (dettaglio non ancora letto: vedi problemi aperti).
OMI: 830 zone in 191 comuni. Esclusi: 140 lotti senza comune, 47 con campi mancanti, 63 con esito (sospesi/aggiudicati/deserti),
114 non abitazioni (box, garage, cantine, negozi, uffici, terreni), 103 in comuni sotto soglia; date impossibili (es. 2918, 2202,
2109) già scartate nell'elenco.

## Regole (scritte anche nella pagina Metodo)

- **Mai «affare» o «occasione»** (controllato da `verifica.py`): si scrivono fatti (prezzo, m², media OMI della zona, occupazione) e
  «sotto / sopra / in linea con la media OMI di zona». Avviso in ogni pagina con aste: valore indicativo, leggere avviso e perizia,
  chiedere al delegato; nel piè di pagina: non è consulenza legale, fiscale o finanziaria.
- **Privacy**: solo campi del lotto. Mai `soggetti` (nomi, email, cellulari, codici fiscali di delegati, custodi, giudice), dati del
  debitore, allegati, PDF, dati catastali, descrizioni libere (possono contenere nomi o targhe). La strada si pubblica **senza numero
  civico**; le coordinate servono solo a trovare la zona e non escono. `verifica.py` cerca email, codici fiscali, cellulari e i nomi
  dei campi personali nelle pagine, in `dati/` e nella cache dei dettagli.
- **Superficie**: un solo valore riferito all'abitazione o la superficie commerciale/lorda/complessiva; numeri accanto a giardino, box,
  terrazzo, cantina, terreno… scartati, e così i numeri che seguono una categoria catastale C/2-C/7 (cantina, box, magazzino) e le
  misure di un singolo vano («soggiorno di 22 m²»): se il testo dà solo le misure dei vani, niente m². Lotti con più abitazioni senza
  m². Senza m²: «Superficie non indicata», nessun €/m².
- **Non abitazioni**: lotti che il PVP classifica come residenziali ma che sono solo box, garage, cantine, negozi, uffici o terreni
  (titolo dell'annuncio, solo categorie catastali C/…, solo A/10 «ufficio») si scartano (`non_abitazione()` in `aggiorna.py`).
- **Zona OMI**: GEOPOI scrive le zone fatte di più pezzi come un solo poligono con più anelli; il punto è nella zona se cade in un
  numero dispari di anelli della zona (regola pari/dispari su tutti gli anelli, non solo il primo).
- **Quote**: frazioni (1/2, ½, 1/3…), «quota/proprietà indivisa», nuda proprietà, usufrutto, diritto di superficie → nessun confronto
  e badge «Quota o diritto parziale?» (con il punto di domanda: è una lettura del testo, si rimanda all'avviso). Si ignorano le quote
  citate per ipoteche o pignoramenti, i diritti estinti e le quote di soli accessori.
- **Sconto** solo se €/m² con l'offerta minima tra 0,25 e 2,25 volte la media OMI e col prezzo base tra 0,25 e 3 volte: fuori da
  qui «superficie da verificare». Tipologia OMI: signorile/civile/economica/villa secondo la categoria del PVP; per «appartamento» la
  tipologia prevalente della zona; stato «normale»; media = (min + max) / 2.
- **OMI**: ogni numero €/m² ha accanto il semestre («2° sem. 2025»); attribuzione «Agenzia delle Entrate – OMI» e licenza CC BY 4.0 nel
  riquadro fonti e nel piè di pagina di ogni pagina.

## Controllo a campione (15/10/2026, `raccolta/controllo.py`, senza cache)

Ogni lotto riletto sulla scheda pubblica del PVP (prezzo base, offerta minima, data, m² nel testo) e ogni zona riletta su GEOPOI
(minimo e massimo della tipologia usata). Torino 4627919 e Milano 4633354 coincidono anche con gli esempi del test delle fonti
(C2 Dante −37%; B20 Porta Romana −15%, con offerta minima uguale al prezzo base come sul PVP).

| Lotto PVP | Dove | Base / minima € | Asta | m² | Zona OMI e valori €/m² | Sconto min. | Controllo PVP | Controllo OMI |
|---|---|---|---|---|---|---|---|---|
| [4639092](https://pvp.giustizia.it/pvp/it/detail_annuncio.page?idAnnuncio=4639092) | Genova, Via Giovanni Gribodo | 53.900 / 40.425 | 2026-12-16 | 51 | C03: abitazioni di tipo economico 940-1.400 (media 1.170) | -32% | ok; m² nel testo ok | ok |
| [4624851](https://pvp.giustizia.it/pvp/it/detail_annuncio.page?idAnnuncio=4624851) | Bari, Via Alessandro Maria Calefati | 134.250 / 100.688 | 2026-12-22 | 86 | B9: abitazioni di tipo economico 2.100-2.500 (media 2.300) | -49% | ok; m² nel testo ok | ok |
| [4643954](https://pvp.giustizia.it/pvp/it/detail_annuncio.page?idAnnuncio=4643954) | Palermo, Via Papa S. Leone II | 65.962 / 49.472 | 2026-12-03 | 100 | C4: abitazioni di tipo economico 900-1.150 (media 1.025) | -52% | ok; m² nel testo ok | ok |
| [4612593](https://pvp.giustizia.it/pvp/it/detail_annuncio.page?idAnnuncio=4612593) | Catania, Viale delle Medaglie D’Oro | 56.812 / 42.609 | 2026-11-18 | 130 | D3: abitazioni di tipo economico 660-980 (media 820) | -60% | ok; m² nel testo ok | ok |
| [4603541](https://pvp.giustizia.it/pvp/it/detail_annuncio.page?idAnnuncio=4603541) | Roma, Via Mario de Renzi | 274.014 / 205.510 | 2026-11-10 | 114 | D76: abitazioni civili 2.250-3.200 (media 2.725) | -34% | ok; m² nel testo ok | ok |
| [4628945](https://pvp.giustizia.it/pvp/it/detail_annuncio.page?idAnnuncio=4628945) | Napoli, Traversa II Fosso del Lupo | 90.375 / 67.781 | 2026-12-01 | 65 | E46: abitazioni civili 1.300-2.000 (media 1.650) | -37% | ok; m² nel testo ok | ok |
| [4627919](https://pvp.giustizia.it/pvp/it/detail_annuncio.page?idAnnuncio=4627919) | Torino, Via Tiziano Vecellio | 96.000 / 72.000 | 2026-12-15 | 65 | C2: abitazioni di tipo economico 1.400-2.100 (media 1.750) | -37% | ok; m² nel testo ok | ok |
| [4633354](https://pvp.giustizia.it/pvp/it/detail_annuncio.page?idAnnuncio=4633354) | Milano, V.le Col di Lana | 325.000 / 325.000 | 2026-11-18 | 62 | B20: abitazioni civili 5.200-7.200 (media 6.200) | -15% | ok; m² nel testo ok | ok |
| [4640249](https://pvp.giustizia.it/pvp/it/detail_annuncio.page?idAnnuncio=4640249) | Pescia, Via del Seminario | 280.500 / 280.500 | 2027-01-20 | 583 | B4: abitazioni civili 1.150-1.350 (media 1.250) | -62% | ok; m² nel testo ok | ok |
| ~~[4629767](https://pvp.giustizia.it/pvp/it/detail_annuncio.page?idAnnuncio=4629767)~~ | Cuneo, Via Donato Bramante | 22.800 / 17.100 | 2026-11-10 | ~~37~~ | — | — | **era un garage** (C/6) classificato «abitazione civile» dal PVP: ora escluso | — |

## Revisione indipendente (15/10/2026 sera)

Revisore diverso da chi ha costruito il sito. 14 lotti **diversi** dai 10 sopra, riletti sulla scheda pubblica del PVP (una richiesta
ogni 3,5 s) e zone/quotazioni rilette su GEOPOI con un calcolo proprio del punto nel poligono.

| Lotto | Dove | Base / minima € | Asta | Occupazione | m² | Zona OMI (media €/m²) | Sconto min. sul sito | Esito |
|---|---|---|---|---|---|---|---|---|
| 4617400 | Roma | 49.300 / 36.975 | 10/12/2026 14:00 | libero | 57 (commerciale lorda) | E165, economiche 1.450 | −55% | ok |
| 4590183 | Milano | 618.400 / 463.800 | 16/10/2026 17:00 | occupato | 182 (campo PVP) | E8, civili 2.275 | +12% | ok |
| 4645953 | Napoli | 122.450 / 91.837 | 19/01/2027 15:30 | non indicata | 102 | E29, economiche 1.155 | −22% | ok |
| 4631569 | Torino | 74.000 / 55.500 | 16/11/2026 15:30 | libero | 88 | D21, civili 1.045 | −40% | ok |
| 4635060 | Salerno | 538.002 / 403.502 | 18/11/2026 12:00 | non indicata | 474 (campo PVP) | E2, ville 1.300 | −35% | ok |
| 4639189 | Perugia | 54.000 / 40.500 | 03/02/2027 12:00 | occupato | 53 | D5, civili 850 | −10% | ok |
| 4638058 | Siracusa | 85.500 / 64.125 | 14/01/2027 10:00 | libero | 148 | D3, civili 1.155 | −62% | ok |
| 4624653 | Sassari | 237.537 / 178.153 | 03/11/2026 17:00 | non indicata | 140 | **C1** (non R1), economiche 1.050 | era +52%, ora +21% | **corretto** |
| 4630354 | Livorno | 78.000 / 58.500 | 10/12/2026 10:00 | non indicata | 64 | C3, civili 1.600 | −43% | ok |
| 4599922 | Ragusa | 37.760 / 28.320 | 26/11/2026 11:00 | non indicata | 88 | D3, economiche 895 | −64% | ok |
| 4634695 | Cosenza | 119.200 / 89.400 | 11/12/2026 10:45 | libero | 109 | D6, economiche 1.025 | −20% | ok |
| 4614226 | Modica | 18.938 / 14.203 | 29/10/2026 16:00 | non indicata | **22 era il solo soggiorno**: ora «non indicata» | **C1** (non R1) | era +37%, ora nessuno | **corretto** |
| 4639560 | Trapani | 12.765 / 12.765 | 16/12/2026 10:00 | non indicata | 48 | C1, economiche 765 | −65% | ok |
| 4644169 | Lamezia Terme | 21.323 / 15.992 | 04/12/2026 15:00 | libero | — (quota 1/2) | R2 | nessuno (quota parziale) | ok |

Errori trovati e corretti in `aggiorna.py` (dati rielaborati dalla cache, OMI delle zone nuove lette su GEOPOI):
1. **Zone OMI**: si guardava solo il primo anello di ogni zona; GEOPOI mette i pezzi di una zona come anelli dello stesso poligono.
   Effetto: 482 lotti senza zona e circa 130 con la zona sbagliata (es. Sassari, Modica). Ora regola pari/dispari su tutti gli anelli.
2. **Garage e cantine come case**: 38 garage/cantine/depositi di un condominio di Cuneo (categoria PVP «abitazione civile», C/6)
   e 15 garage di Cassino erano pubblicati come case con sconti del −44/−69% (anche il 10° lotto del controllo sopra). Ora 114 lotti
   «non abitazione» esclusi da titolo e categorie catastali.
3. **Superficie di un vano**: «soggiorno (sup. netta circa 22,00 m2)» veniva preso come superficie della casa; e i m² dopo una
   categoria C/6 o C/2 (box, magazzino) venivano attribuiti all'abitazione. Ora scartati.
4. **Strade**: nomi tagliati («Via IV», «Via Pietro» per Via Pietro Nenni, «Via Quattro»), «Via Via …», «snc», «is. 397», maiuscole.
5. Testi: guida rischi (art. 2922 c.c.: «impugnata per lesione», non «annullata perché il prezzo era troppo alto»), guida offerta
   minima (prezzo base fissato dal giudice o dal delegato, art. 591-bis), Metodo (offerta minima 75%, misure dei vani, coordinate
   approssimative, esclusione dei box), nomi delle zone (accenti «Libertà», «Pietà»; sigle interne di Genova «TU.M»/«AAB.M»;
   «Monza, Crescenzago, Gorla» invece di «Monza»), frase città con una sola data, «l'11%/l'8%», avviso delle aste nascoste.
Norme rilette su Normattiva dal revisore: artt. 490, 560, 569, 571, 572, 579, 585, 586, 587, 591, 591-bis c.p.c.; 2922, 2923 c.c.;
art. 63 disp. att. c.c. Nessun errore di sostanza nelle guide oltre ai due punti sopra.
Rischio residuo noto: la superficie letta dal testo resta un'euristica (es. Floridia 4625406: 24 m² sono una copertura sul terrazzo):
per questo la scheda rimanda sempre alla perizia.

## Revisione fatta prima della consegna

- **Aspetto**: schermate di ogni tipo di pagina a 390 e 1280 px, tema chiaro e scuro (`cache/screenshot/`). Corretto durante le
  prove: bordo decorativo della testata che lasciava pezzi bianchi; link alla scheda PVP spostato in fondo alla scheda su telefono;
  nomi delle zone OMI ripuliti e accorciati («QUART.MURAT -TRA C.SO VITT.VENETO,…» → «Quart. Murat»); numero ripetuto nello sconto; plurali
  («1 asta già svolta… è nascosta»); ora del PVP sempre in ora di Roma; veicoli ridotti a 40 per tipo; niente pagine di fascia o zona
  quasi uguali alla pagina città.
- **Casi limite provati**: lotto senza superficie, senza occupazione, con quota parziale, con superficie dubbia, senza zona OMI,
  sconto sopra la media (+73%, rosso), in linea (0%), città con 8 aste (`citta-piccola`), lotto tolto o con prezzo cambiato in
  `live.json` (nascosto/aggiornato), filtro «Solo libere», ordinamento, tema.
- **Testi**: italiano semplice, date «22 dicembre 2026», importi «119.000 €», m² e €/m² con punto delle migliaia. Guide con articolo di
  legge per ogni regola e avviso «Informazioni generali, non consulenza legale».

## Problemi aperti

1. **Blocco temporaneo del PVP**: dopo ~1.100 dettagli in 40 minuti (una richiesta ogni ~1,5 s) il portale ha risposto «Server
   Unavailable» (503) per circa 15 minuti. Ora: una richiesta ogni ~3 s, massimo 700 dettagli per esecuzione, stop al primo errore.
   Mancano ancora i dettagli di **804 lotti** pubblicati (si completano in 1-2 sere): fino ad allora la loro scheda non ha termine
   offerte né modalità, e la superficie si cerca solo nel titolo breve.
2. **Indirizzi JSON del PVP versionati**: `rete.endpoint_pvp()` li rilegge ogni volta da `fe-config`; se cambia la struttura, la
   routine si ferma con «PVP non raggiungibile» e i dati restano quelli del giorno prima (le pagine nascondono comunque le aste passate).
3. **OMI dalla consultazione pubblica GEOPOI**, non dal download ufficiale semestrale (richiede SPID): stessi dati e stessa licenza;
   con il nuovo semestre (2026/1) `aggiorna.py` lo vede da solo e rilegge le zone necessarie. Il download con SPID resta un'opzione.
4. **Sconti molto alti**: la mediana è −41% perché l'offerta minima è già il 75% del prezzo base e molti lotti sono a 2°-4° tentativo,
   ma alcuni casi possono avere metri quadri o zona sbagliati nel PVP (coordinate errate). La pagina lo dice e rimanda alla perizia.
5. **Tentativo d'asta**: il PVP non lo dà in un campo; non lo mostriamo.
6. Città grandi con poche aste oggi: Bologna, Venezia e Verona (sotto le 8 aste: nessuna pagina), Padova (9), Firenze (9) e Brescia (8) (pagina sì, senza fasce né zone).
7. Pubblicità e riquadro mutuo: solo posti vuoti (`ad-slot` nascosto, `dati/affiliati.json` senza URL).
