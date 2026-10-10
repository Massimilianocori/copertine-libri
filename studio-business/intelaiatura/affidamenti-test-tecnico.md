# ChiLavoraColComune (affidamenti ANAC per ente) – Test tecnico delle fonti

Data del test: 10 ottobre 2026 (tutti gli HTTP status, le date `Last-Modified` e i conteggi sono di questa data). Riferimento: `5-opportunita-grandi.md`, candidata A e sezione 4 "Test tecnico a costo zero per A".
Dati e script: `affidamenti/` (elenco in fondo). Spesa: zero. Download in una cartella fuori dal repository, cancellati dopo l'elaborazione.

## 0. Esito in breve

| # | Soglia (dal rapporto) | Richiesto | Misurato | Esito |
|---|---|---|---|---|
| 1 | Download ANAC riusciti al 1° o 2° tentativo | 5 su 5 | **24 file su 24** esistenti (20 al 1° tentativo, 4 al 2° dopo un 403) | **raggiunta** |
| 2a | CIG pubblicati nel mese | ≥ 100.000 | **6 mesi su 7** (mar 105.276 · apr 119.991 · mag 116.896 · giu 123.971 · lug 127.467 · **ago 80.272** · set 112.063) | raggiunta tranne agosto |
| 2b | … di cui sotto 40.000 € | ≥ 50% | **69,5–71,2%** in tutti i mesi | raggiunta |
| 2c | … aggiudicatario presente | ≥ 60% | **82–86%** in 5 mesi; **28,4% (marzo) e 21,4% (giugno)**: i delta aggiudicatari del 1/4 e del 1/7 sono quasi vuoti | raggiunta in 5 mesi su 7 |
| 3 | Comuni distinti con almeno un CIG nel mese | ≥ 4.000 | **5.649–6.258** (agosto 5.689) | raggiunta |
| 4a | Affidamenti delle determine presenti in ANAC | ≥ 16/20 | **9/20** (45%); su un campione largo **181 CIG su 541 = 33%** | **NON raggiunta** |
| 4b | Campi corretti (importo, aggiudicatario, oggetto) tra i presenti | ≥ 90% | **19 campi su 23 = 83%** (importo 4/5, aggiudicatario 6/9, oggetto 9/9); record del tutto corretti 5/9 | **NON raggiunta** |
| 4c | Ritardo di pubblicazione | ≤ 60 giorni | mediana **20 giorni**; 7 casi su 8 entro 60 | raggiunta |
| 5 | Elaborazione di un mese | ≤ 60 min, ≤ 6 GB | **29 s, 0,7 GB** (un delta); 7 delta insieme 186 s, 3,3 GB | raggiunta |
| 6 | Autocomplete pertinente su 30 Comuni | ≥ 10/30 | **0/30** (15 Comuni hanno solo "albo fornitori comune di X") | **NON raggiunta** |

**VERDETTO: NON COSTRUIRE.** Due soglie decisive su sei falliscono, e il piano diceva di fermarsi se falliva la soglia 4. I dati aperti ANAC contengono circa un affidamento su tre di quelli che i Comuni deliberano. Le gare sopra soglia ci sono quasi tutte, gli affidamenti diretti piccoli in gran parte no. Il prodotto avrebbe senso proprio per questi ultimi. Inoltre nessuno cerca su Google gli esiti dei Comuni medi. Motivi e condizioni per riaprire nella sez. 8.

## 1. Metodo

- **Fonte**: portale open data ANAC, [dati.anticorruzione.it/opendata](https://dati.anticorruzione.it/opendata) (licenza CC BY-SA 4.0, indicata nella pagina del dataset). Sono stati usati i dataset "CIG aggiornamenti delta" (`cig`), `aggiudicatari`, `aggiudicazioni` e `stazioni-appaltanti`, in JSON a righe compresso. Il portale tiene solo gli **ultimi 7 delta mensili** (dal 1/4/2026 al 1/10/2026: il file del 1/2/2026 dà 404). Il file "completo" è annuale: esiste [`cig-2025/.../cig_json_2025_06.zip`](https://dati.anticorruzione.it/opendata/download/dataset/cig-2025/filesystem/cig_json_2025_06.zip) (Last-Modified 16/1/2026), il 2026 non c'è ancora.
- **Richieste**: una alla volta, User-Agent `ChiLavoraColComune-test/0.1 (test di fattibilita su dati aperti ANAC)`, pausa di 10–15 s tra un file e l'altro, nuovi tentativi dopo 15/45/120/300 s (`scarica.py`). Ogni tentativo è registrato in `dati/registro-download-anac.json`.
- **Conteggi** (`analizza_mese.py`): lettura in streaming degli zip, deduplica per CIG (vale l'ultima versione), mese = mese di `data_pubblicazione`. "Comune" = stazione appaltante con denominazione "COMUNE DI …" nell'anagrafica ANAC (8.159 voci attive). "Persona fisica" = codice fiscale di 16 caratteri.
- **Controllo di verità** (`atti_maggioli.py`, `verita.py`, `copertura_cig.py`): estrazione casuale di Comuni medi (15.000–60.000 abitanti, non capoluoghi, popolazione ISTAT al 1/1/2026, `comuni_istat.py`, seme 20261011). Ho preso i Comuni **nell'ordine estratto**, saltando quelli con la sezione trasparenza non leggibile da script (10 su 15: motivi in `dati/comuni-estratti-verita.tsv`) e con un'estrazione supplementare (seme 20261012) per il quinto.
  - La fonte indipendente sono le **determine** in "Amministrazione trasparente > Provvedimenti dirigenti". Le sezioni "Bandi di gara e contratti" invece dal 1/1/2024 rimandano alla BDNCP (es. [Follonica](https://www.comune.follonica.gr.it/Amministrazione-Trasparente/Bandi-di-gara-e-contratti): "il collegamento ipertestuale alla Banca Dati Nazionale dei Contratti Pubblici"), quindi confrontarle con l'ANAC sarebbe circolare.
  - Per ente: 4 determine di affidamento o aggiudicazione con CIG nell'oggetto, pubblicate dall'1/7 al 31/8/2026 (seme 20261010). Il testo è letto dal PDF dell'atto; il confronto è fatto a mano, con una nota per ogni caso.
- **Domanda** (`autocomplete.py`): API pubblica `suggestqueries.google.com` (hl=it, gl=it), 5 prefissi per Comune, 20 Comuni medi + 10 capoluoghi estratti a caso (seme 20261010). Le proposte sono rilette a mano: vedi sez. 3.6.
- **Dati personali**: il campione pubblicato contiene solo società ed enti con forma giuridica. Le ditte individuali del controllo di verità sono indicate come "[ditta individuale: nome omesso]". Le iniziali di un utente di un servizio sociale nell'oggetto di una determina sono state tolte. Nessuna pagina è stata costruita.

## 2. Tabella delle fonti (verificate il 10/10/2026)

| Fonte | URL | HTTP (tentativi) | Formato | Dimensione | Tempo | Last-Modified |
|---|---|---|---|---|---|---|
| CIG delta 1/10 | [20261001-cig_json.zip](https://dati.anticorruzione.it/opendata/download/dataset/cig/filesystem/20261001-cig_json.zip) | 200 (1) | zip → JSON a righe 1,26 GB, 565.864 righe | 137,6 MB | 121 s | 5/10/2026 |
| CIG delta 1/9 | [20260901-cig_json.zip](https://dati.anticorruzione.it/opendata/download/dataset/cig/filesystem/20260901-cig_json.zip) | 200 (1) | idem, 168.977 righe | 41,5 MB | 38 s | 2/9/2026 |
| CIG delta 1/8 | [20260801-cig_json.zip](https://dati.anticorruzione.it/opendata/download/dataset/cig/filesystem/20260801-cig_json.zip) | 200 (1) | idem | 76,7 MB | 66 s | 6/8/2026 |
| CIG delta 1/7 | [20260701-cig_json.zip](https://dati.anticorruzione.it/opendata/download/dataset/cig/filesystem/20260701-cig_json.zip) | 200 (1) | idem | 57,9 MB | 51 s | 8/7/2026 |
| CIG delta 1/6 | [20260601-cig_json.zip](https://dati.anticorruzione.it/opendata/download/dataset/cig/filesystem/20260601-cig_json.zip) | 200 (1) | idem | 107,8 MB | 93 s | 11/6/2026 |
| CIG delta 1/5 | [20260501-cig_json.zip](https://dati.anticorruzione.it/opendata/download/dataset/cig/filesystem/20260501-cig_json.zip) | 200 (1) | idem | **310,5 MB** | 272 s | **22/5/2026** |
| CIG delta 1/4 | [20260401-cig_json.zip](https://dati.anticorruzione.it/opendata/download/dataset/cig/filesystem/20260401-cig_json.zip) | 200 (1) | idem | 108,9 MB | 96 s | 2/4/2026 |
| CIG delta 1/2 | `…/cig/filesystem/20260201-cig_json.zip` | 404, 404, 404, 403 | – | – | – | non più pubblicato |
| Aggiudicatari delta 1/4 … 1/10 | [es. 20261001-aggiudicatari_json.zip](https://dati.anticorruzione.it/opendata/download/dataset/aggiudicatari/filesystem/20261001-aggiudicatari_json.zip) | 7 × 200 (2 al 2° tentativo dopo 403) | JSON a righe | 7,9 / 4,5 / 6,1 / **0,06** / 9,6 / 7,2 / **0,05** MB (ott → apr) | 1–10 s | stesse date dei CIG |
| Aggiudicazioni delta 1/4 … 1/10 | [es. 20261001-aggiudicazioni_json.zip](https://dati.anticorruzione.it/opendata/download/dataset/aggiudicazioni/filesystem/20261001-aggiudicazioni_json.zip) | 7 × 200 (1 al 2° tentativo) | JSON a righe | 4,4–14,2 MB | 5–15 s | – |
| Anagrafica stazioni appaltanti | [stazioni-appaltanti_json.zip](https://dati.anticorruzione.it/opendata/download/dataset/stazioni-appaltanti/filesystem/stazioni-appaltanti_json.zip) | 200 (1) | JSON a righe, 48.040 enti | 3,8 MB | 4 s | – |
| CIG annuale 2025, giugno (controllo) | [cig_json_2025_06.zip](https://dati.anticorruzione.it/opendata/download/dataset/cig-2025/filesystem/cig_json_2025_06.zip) | 200 (1) | JSON a righe, 121.416 CIG | 28,9 MB | 26 s | 16/1/2026 |
| Aggiudicatari "completo" | [aggiudicatari_json.zip](https://dati.anticorruzione.it/opendata/download/dataset/aggiudicatari/filesystem/aggiudicatari_json.zip) / [csv](https://dati.anticorruzione.it/opendata/download/dataset/aggiudicatari/filesystem/aggiudicatari_csv.zip) | 206 (richiesta parziale) | zip | JSON 1,35 MB (!), CSV 151 MB | – | 23/1/2026 |
| Pagine HTML del catalogo, pagina `smartcig`, metadati `.jsonld` | [dati.anticorruzione.it/opendata/dataset](https://dati.anticorruzione.it/opendata/dataset) | 403 oppure **200 con "Request Rejected"** (WAF F5) in 8 prove su 8 | HTML | 269–312 byte | – | – |
| ISTAT elenco Comuni | [Elenco-comuni-italiani.csv](https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.csv) | 200 | CSV latin-1 | 1,1 MB | 1 s | – |
| ISTAT popolazione 1/1/2026 | [POSAS_2026_it_Comuni.zip](https://demo.istat.it/data/posas/POSAS_2026_it_Comuni.zip) | 200 | CSV in zip | 4,6 MB | 1 s | – |
| Google Autocomplete | `https://suggestqueries.google.com/complete/search?client=firefox&hl=it&gl=it&q=…` | 200 (200 query, 0 senza risposta) | JSON | – | 1,5 s/query | – |
| Determine dei 5 Comuni + Grugliasco | griglie Maggioli `…trasparenza-valutazione-merito.it/web/trasparenza/papca-p/-/papca/igrid/…` (URL in `comuni-estratti-verita.tsv`) | 200 | HTML (Liferay) + PDF allegati | oltre 10.000 righe lette | 1,5 s/pagina | – |

Le uscite dei delta sono **irregolari**: il 2, 22, 11, 8, 6, 2 e 5 del mese (Last-Modified da aprile a ottobre). Il delta di maggio è uscito con tre settimane di ritardo e pesa il triplo degli altri (310 MB: contiene molti record vecchi ripubblicati).

## 3. I numeri, soglia per soglia

### 3.1 Soglia 1 – stabilità dei download
- 38 tentativi in tutto. I **24 file esistenti** sono scaricati tutti: 20 al primo tentativo, 4 al secondo dopo un 403 del WAF (aggiudicazioni 1/10, aggiudicatari 1/9, aggiudicatari 1/5, e il primo sondaggio parziale del file CIG). In tutto **5 risposte 403**.
- Gli altri tentativi falliti sono file inesistenti: il delta del 1/2 è uscito dalla finestra dei 7 mesi, e i nomi `…-smartcig_json.zip` erano ipotizzati da me (la pagina del dataset non si legge: WAF).
- I file si scaricano bene. **Le pagine del catalogo e l'API CKAN no**: per scoprire i nomi dei file nuovi bisogna conoscerne lo schema (`AAAAMMGG-<dataset>_json.zip`), perché le pagine indice sono bloccate quasi sempre.

### 3.2 Soglia 2 – volume, quota sotto 40.000 €, aggiudicatario (`dati/riassunto-mensile-anac.json`)

| Mese di pubblicazione | CIG | < 40.000 € | < 5.000 € | con aggiudicatario | … tra i < 40k | con aggiudicazione | affidamenti diretti |
|---|---|---|---|---|---|---|---|
| 2026-03 | 105.276 | 70,2% | 12,1% | **28,4%** | 25,8% | 86,9% | 85.502 |
| 2026-04 | 119.991 | 71,0% | 13,0% | 82,4% | 86,1% | 86,6% | 99.234 |
| 2026-05 | 116.896 | 71,2% | 12,4% | 85,5% | 90,0% | 87,1% | 97.226 |
| 2026-06 | 123.971 | 69,8% | 13,6% | **21,4%** | 20,1% | 87,0% | 106.070 |
| 2026-07 | 127.467 | 70,5% | 12,9% | 83,1% | 87,9% | 86,2% | 108.549 |
| 2026-08 | **80.272** | 69,5% | 11,9% | 82,4% | 88,6% | 82,4% | 67.234 |
| 2026-09 | 112.063 | 71,1% | 11,2% | 83,0% | 88,4% | 83,0% | 95.539 |

- Unione dei 7 delta: 3.436.722 righe, 2.560.766 CIG distinti. Il file annuale di giugno 2025 ha 121.416 CIG: il volume dei delta è coerente con quello definitivo. Il file annuale **non aggiunge** CIG che i delta non abbiano.
- **Buchi nei dati**: i delta aggiudicatari del 1/4/2026 (1.630 righe) e del 1/7/2026 (2.242 righe) sono quasi vuoti, contro 151.768–343.387 righe negli altri mesi. Per i CIG di marzo e di giugno l'aggiudicatario manca nei dati aperti (l'aggiudicazione con importo c'è). Non è stato verificato se il prossimo file annuale li recupererà.
- **Qualità**: tipo di aggiudicatario nel delta di ottobre: 193.025 "IMPRESA", 15.703 "DITTA INDIVIDUALE", 22.810 "NON PRESENTE IN ANAGRAFE" e **14.287 "STAZIONE APPALTANTE"** (cioè l'ente stesso come aggiudicatario, il 5,4%). Persone fisiche (codice fiscale di 16 caratteri): **8,3–11,3%** degli aggiudicatari, con nomi e cognomi.

### 3.3 Soglia 3 – enti coperti
Stazioni appaltanti distinte al mese: 12.336–15.463. **Comuni distinti al mese: 5.649–6.258** (agosto 5.689). Di questi, Comuni con almeno un affidamento sotto 40.000 € con aggiudicatario: 5.022–5.662 (1.527 e 1.814 nei mesi con il buco). Soglia superata, **ma** vale per "almeno un CIG": la soglia 4 mostra che per ciascun Comune manca la maggior parte degli affidamenti.

### 3.4 Soglia 4 – controllo di verità (`dati/verita-20.json`)

5 enti: Castelvetrano (TP), Abbiategrasso (MI), Albenga (SV), Bussolengo (VR), Pontecagnano Faiano (SA). Atti in "Provvedimenti dirigenti", pubblicati dall'1/7 al 31/8/2026.

| # | Ente | CIG | Atto (sintesi) | Importo nell'atto | In ANAC | Importo | Aggiud. | Oggetto | Ritardo |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Castelvetrano | BC6ED480C4 | gonfiabili Estate Selinuntina | 1.629 + IVA | **no** | – | – | – | – |
| 2 | Castelvetrano | BC5EEB9F3D | lavori allagamenti cimitero | 8.499 (8.244 + 255 oneri) | sì | sì (8.244, senza oneri) | sì | sì | 22 gg |
| 3 | Castelvetrano | BCB28F9B1B | Notte Bianca del Mare 2026 | 5.999 | sì | sì | sì | sì | 19 gg |
| 4 | Castelvetrano | BCAE874CD8 | conferimento rifiuti indifferenziati | 139.900 + IVA | sì | **no: 300 €** (prezzo a tonnellata) | sì | sì | 13 gg |
| 5 | Abbiategrasso | BC2966987B | ispezioni ponti (AINOP) | 4.900 | **no** | – | – | – | – |
| 6 | Abbiategrasso | BC4FD72383 | consulenza stranieri, trattativa diretta MePA | 3.172 + IVA | **no** | – | – | – | – |
| 7 | Abbiategrasso | BC92DF975D | certificati firma digitale | ~440 + IVA | **no** | – | – | – | – |
| 8 | Abbiategrasso | BC9DCDEB35 | bilancio consolidato 2026–2030 | 34.200 | **no** | – | – | – | – |
| 9 | Albenga | BC4E7AAA0B | service audio-luci evento | 3.538 IVA incl. | **no** | – | – | – | – |
| 10 | Albenga | BC0B45DC46 | presidi antincendio Palio | 366 IVA incl. | **no** | – | – | – | – |
| 11 | Albenga | BB28D21772 | trasporto disabili gen–giu | 3.675 | **no** | – | – | – | – |
| 12 | Albenga | BCA5F49B08 | movimentazione palchi Fior d'Albenga | 9.188 + IVA | sì | sì | sì | sì | 21 gg |
| 13 | Bussolengo | BC6B5063DB | giubbottini antitaglio PL | 2.675,50 + IVA | **no** (*) | – | – | – | – |
| 14 | Bussolengo | BC41094B71 | porta campo calcio, modifica | 620 + IVA | **no** | – | – | – | – |
| 15 | Bussolengo | B9428829E9 | controllo accessi ecocentro, modifica | 400 (modifica) | sì (originario 20.963) | non verificabile | **no** (assente) | sì | n.m. |
| 16 | Bussolengo | BC158BB027 | strade comunali, aggiudicazione | 481.841,75 | sì | sì | sì | sì | 6 gg |
| 17 | Pontecagnano F. | BAE37B5956 | restauro ex convento, aggiudicazione | non scaricabile | sì (ente = CUC) | non verificabile | sì | sì | ≤ 35 gg |
| 18 | Pontecagnano F. | BBF019E8BD | PFTE polo scolastico, aggiudicazione | non scaricabile | sì (solo gara) | non verificabile | **no** (assente) | sì | > 60 gg |
| 19 | Pontecagnano F. | BC1B001599 | supporto al RUP, aggiudicazione | non scaricabile | **no** | – | – | – | – |
| 20 | Pontecagnano F. | BC1C192464 | servizi di ingegneria PFTE/DL | non scaricabile | sì | non verificabile | **no** (buco del 1/7) | sì | 0 gg |

(*) il 7/10/2026 Bussolengo ha riaffidato la stessa fornitura con un nuovo CIG (BD3F9508B0): il CIG di luglio potrebbe essere stato annullato. Anche contandolo come presente, il risultato resta 10/20.

**Esito: presenti 9/20 (45%) contro 16/20 richiesti.** Campi corretti tra i presenti: importo 4/5 verificabili, aggiudicatario 6/9, oggetto 9/9, cioè **19/23 = 83%** (record del tutto corretti 5/9). Ritardo: mediana 20 giorni, 7 casi su 8 entro 60.

**Campione largo** (`dati/copertura-cig-determine.json`): tutti i CIG citati nelle determine di 6 Comuni (i 5 sopra più Grugliasco) e generati nel periodo coperto dai delta. Il codice CIG cresce nel tempo: gli intervalli di prefisso sono ricavati dall'indice ANAC.

| Determine pubblicate | CIG | presenti in ANAC | gare (proc. aperta/negoziata) | affidamenti diretti dichiarati | procedura non dichiarata |
|---|---|---|---|---|---|
| luglio–agosto 2026 | 333 | **113 (33,9%)** | 30/36 (83%) | 35/97 (36%) | 48/200 (24%) |
| aprile–maggio 2026 (4–6 mesi dopo) | 208 | **68 (32,7%)** | 16/18 (89%) | 34/69 (49%) | 18/121 (15%) |

Per ente (luglio–agosto): Castelvetrano 41%, Abbiategrasso 19%, Albenga 21%, Bussolengo 43%, Pontecagnano 52%, Grugliasco 48%. **La quota non cresce con il tempo** (33% a 2 mesi, 33% a 4–6 mesi): non è ritardo, gli affidamenti mancanti non arrivano. Ho escluso anche l'ipotesi del dataset SMARTCIG: i CIG mancanti sono tutti nel formato PCP "B…" del dataset `cig`, mentre gli SmartCIG "Z…" non esistono più dal 2024 (la pagina del dataset non è stata leggibile per il WAF).

Limite dichiarato: i 5 enti usati sono tutti su piattaforma Maggioli, perché è l'unica che si è lasciata leggere da script; gli altri 10 estratti sono stati saltati per siti irraggiungibili o elenchi non leggibili. Il risultato è però omogeneo tra Nord e Sud (19–52%).

### 3.5 Soglia 5 – risorse
- Un delta (ottobre, 565.864 righe CIG + aggiudicatari + aggiudicazioni + anagrafica): **29 s, 727 MB** di memoria massima.
- 7 delta insieme (3,4 milioni di righe, con indice TSV di 290 MB): **186 s, 3,3 GB**.
- Download di un mese tipico: 1–5 minuti. Tutto sta comodamente nei limiti di un runner gratuito di GitHub Actions.

### 3.6 Soglia 6 – domanda (`dati/autocomplete-30-comuni.json`)
- 30 Comuni (20 medi + 10 capoluoghi) × 5 prefissi = 150 query, tutte con risposta.
- Lo script segnalava 15 Comuni "pertinenti" (5 medi, 10 capoluoghi). Rileggendoli, **tutte e 15 le proposte sono "albo fornitori comune di X"**: chi le cerca vuole **iscriversi** all'elenco dei fornitori, non sapere chi ha vinto. Lo script ora tiene "albo fornitori" a parte.
- **Proposte su affidamenti, aggiudicazioni o esiti: 0/30.** Per i 20 Comuni medi non c'è nessuna proposta su questi temi, nemmeno per "affidamenti comune di X".
- Contesto, fuori campione (`dati/autocomplete-10-grandi-citta.json`): nelle 10 città più grandi la domanda c'è in **5 su 10** ("affidamento diretto comune di milano", "comune di torino affidamenti diretti", "affidamenti comune di napoli", "appalti e affidamenti comune di genova", "affidamenti comune di firenze"); non c'è per Palermo, Bologna, Bari e Verona, e per Roma c'è solo "portale fornitori".
- La SERP di "affidamenti diretti comune di milano 2026" mostra solo PDF di enti (Politecnico, ARERA, Comune di Firenze): nessun aggregatore. Ma la domanda è limitata a poche grandi città.

## 4. Stima della copertura (sopra e sotto 40.000 €)

| Fascia | Misura diretta | Stima |
|---|---|---|
| **Sopra 40.000 €** (in pratica gare: procedure aperte, negoziate, ristrette) | 5/5 nei 20 controlli; gare 46/54 = 85% nel campione largo | **85–100%** |
| **Sotto 40.000 €** (affidamenti diretti) | 4/14 nei 20 controlli (29%); affidamenti diretti dichiarati 69/166 = 42%; atti senza procedura dichiarata, in genere piccoli, 66/321 = 21% | **25–45%, valore centrale circa un terzo** |
| Tutti i CIG citati nelle determine | 181/541 | **33%** |

Il volume pubblicato sotto 40.000 € (55.761–89.886 CIG al mese) è quindi plausibilmente **un terzo del flusso reale**. È una stima con l'ipotesi dichiarata che i 6 Comuni Maggioli siano rappresentativi. A questo si aggiungono due mesi su sette senza aggiudicatari e importi talvolta sbagliati (caso 4: un appalto da 139.900 € registrato come 300 €, finito così tra i "sotto 5.000").

Per il prodotto significa che una pagina "Chi lavora con il Comune di Albenga" mostrerebbe circa 1 affidamento su 5 di quelli che il Comune delibera, e i piccoli fornitori locali, cioè il pubblico che dovrebbe pagare, non ci troverebbero i propri affidamenti.

## 5. Ore di manutenzione settimanale (stima)

| Scenario | Lavoro | Ore/settimana |
|---|---|---|
| Solo dati aperti ANAC (come testato) | scarico mensile automatico (5 min di macchina); controllo che il delta sia uscito (date dal 2 al 22 del mese) e che non sia vuoto (2 casi su 7); aggiornamento dei nomi file perché il catalogo è dietro WAF; gestione dei 403 | **0,5–1 h** in media, con 2–4 h nei mesi con anomalie; ma le pagine resterebbero incomplete al 33% |
| ANAC + determine dei Comuni per colmare il buco | crawler per piattaforma (Maggioli, Halley, ISWEB, Municipium, siti fatti a mano), estrazione di CIG, ditta e importo dagli oggetti e dai PDF; nel test 10 Comuni su 15 non erano leggibili da script | **10+ h**: è lo stesso schema "migliaia di siti comunali" che ha fatto fallire BandiPosteggi; escluso dal filtro duro |

## 6. Rischi

1. **Copertura strutturale bassa sotto soglia** (sez. 3.4 e 4): è il rischio (b) del rapporto, ora misurato: circa un terzo.
2. **WAF F5 di ANAC**: 5 risposte 403 su 38 sui file. Pagine del catalogo, pagine dei dataset e metadati `.jsonld` rifiutati in tutte le 8 prove di oggi ("Request Rejected" anche con HTTP 200, che va riconosciuto dal contenuto); la sessione di ricerca precedente, alla stessa data, era riuscita a leggerle. Una pipeline deve indovinare i nomi dei file.
3. **Cambi e anomalie del formato**: file "completo" degli aggiudicatari in JSON di 1,35 MB (contro 151 MB del CSV); due delta mensili quasi vuoti; delta di maggio uscito il 22 e triplo; finestra di soli 7 delta (chi salta un mese per più di 7 mesi perde i dati fino al file annuale di gennaio); campi in minuscolo e in maiuscolo mescolati nello stesso record (`cig`, `COD_ESITO`…).
4. **Qualità dei campi**: importi unitari al posto del valore del contratto (caso 4); l'ente indicato è la Centrale unica di committenza e non il Comune (casi 17–18); il 5,4% degli "aggiudicatari" è la stazione appaltante stessa; 22.810 aggiudicatari "non presenti in anagrafe".
5. **Dati personali**: l'8–11% degli aggiudicatari ha un codice fiscale di persona fisica (ditte individuali e professionisti), con nome e cognome. Le pagine per ente dovrebbero escluderli o mascherarli, e si perderebbe un'altra quota di affidamenti.
6. **Concorrenti**: Atoka PA (Cerved) dichiara 68 milioni di contratti e ha pagine pubbliche per azienda ([es. atoka.io](https://atoka.io/public/it/azienda/publika-servizi-srl/b6f842577336), dal rapporto del 10/10/2026). Telemat e InfoPlus vendono abbonamenti. Non ho verificato da quali fonti attingano: se usano solo i dati ANAC hanno lo stesso buco; in ogni caso coprono già la fascia ben servita (gare sopra 40.000 €). La dashboard ufficiale [ANAC Analytics](https://dati.anticorruzione.it/superset/dashboard/appalti/) non è indicizzata.
7. **Domanda**: 0/30 nei Comuni medi; esiste solo in 5 grandi città, dove già i Comuni pubblicano elenchi propri (es. [affidamenti.comune.fi.it](https://affidamenti.comune.fi.it/)).

## 7. Cosa resta utile
- Gli script (`affidamenti/raccolta/`) funzionano e sono riusabili: download robusto al WAF, analisi in streaming di un mese in 30 s, lettura delle griglie Maggioli (oltre 10.000 righe di atti lette in tutto), misura della copertura per qualunque insieme di determine.
- Il dato ANAC è affidabile per le **gare sopra 40.000 €** (85–100% di presenza; importo e aggiudicatario corretti nei casi verificati) e lo è per tutta Italia.

## 8. Verdetto

### 8.1 VERDETTO: NON COSTRUIRE
1. **Soglia 4 fallita** (regola di stop del piano): 9/20 presenti (45%), e 33% su 541 CIG; la quota non cresce dopo 4–6 mesi. Campi corretti 83% contro 90%.
2. **Soglia 6 fallita**: 0/30 Comuni con una ricerca sugli esiti; le uniche proposte sono "albo fornitori".
3. Le soglie 1, 3 e 5 passano, la 2 passa in 4 mesi su 7. Ma i volumi del dataset (100.000+ CIG al mese) **sovrastimano** la copertura: sono circa un terzo del flusso reale sotto soglia.

**"COSTRUIRE SOLO PER …" è stato valutato e scartato.** Il sottoinsieme che regge sui dati è quello delle **gare sopra 40.000 €** (85–100%). Lì però (a) la domanda dei Comuni medi è 0/30 e quella delle grandi città è 5/10; (b) è la fascia già coperta da Atoka PA, Telemat, InfoPlus e dal formato OCDS di ANAC; (c) il pubblico dei piccoli fornitori locali, che giustificava il prodotto (95% dei contratti di servizi e forniture affidati in modo diretto, Relazione ANAC 2025), resta fuori. Non c'è una prova che il sottoinsieme porti traffico o abbonati, quindi non lo propongo.

### 8.2 Condizioni per riaprire il caso (test a costo zero, già scriptati)
1. **Copertura ANAC sotto soglia ≥ 80%**: rieseguire ogni 3 mesi `copertura_cig.py` sulle determine dei 6 Comuni di questo test (stessi script e stesse griglie). Si riapre se la quota degli affidamenti diretti presenti supera l'80% per due trimestri di fila (oggi 36–49%). Può succedere se ANAC completa la pubblicazione dei dati della piattaforma PCP o rilascia il file annuale 2026 con i CIG mancanti: da controllare a gennaio 2027.
2. **Domanda**: si riapre solo se, insieme alla condizione 1, l'autocomplete dà ≥ 10/30 su un nuovo campione casuale, oppure se Search Console di un sito già esistente mostra impressioni per "affidamenti comune di X".

## 9. File consegnati e come rieseguire

- `affidamenti/raccolta/` (tutti con docstring in italiano, da eseguire con `python3 -I` e cartelle di download fuori dal repository):
  - `scarica.py`: download con nuovi tentativi e registro.
  - `comuni_istat.py`: anagrafica dei Comuni con popolazione ed estrazione casuale.
  - `analizza_mese.py`: soglie 2, 3, 5; indice TSV e campione.
  - `atti_maggioli.py`: determine dalle griglie "Provvedimenti dirigenti" Maggioli.
  - `verita.py`: estrazione dei 20 casi, PDF e confronto con l'indice.
  - `copertura_cig.py`: copertura su campione largo, per procedura.
  - `autocomplete.py`: soglia 6, con `--riclassifica`.
- `affidamenti/dati/` (solo riassunti e campioni, 120 KB in tutto):
  - `riassunto-mensile-anac.json`: tutti i conteggi per mese.
  - `registro-download-anac.json`: 38 tentativi e date Last-Modified.
  - `verita-20.json`: i 20 controlli con esiti e note.
  - `copertura-cig-determine.json`: campione largo, con i CIG mancanti per ente.
  - `comuni-estratti-verita.tsv`: 17 Comuni estratti, usati o saltati con motivo.
  - `campione-settembre-2026.json`: 25 affidamenti di Comuni, solo società ed enti.
  - `autocomplete-30-comuni.json` e `autocomplete-10-grandi-citta.json`.
- Giro completo: download dei 7 mesi ≈ 15 min; analisi ≈ 3 min; determine di 6 Comuni ≈ 10 min; autocomplete ≈ 5 min.
