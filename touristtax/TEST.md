# Tourist Tax Calculator – test a costo zero (fase 0) e controlli di qualità

Data dei controlli: **10 ottobre 2026**. Download con curl (User-Agent da browser) nella cartella di lavoro della sessione
(`scratchpad/touristtax/dl/`), file letti solo con `python3 -I`. Nessun account creato, nessuna pubblicazione.

## 1. Fase 0: 41 destinazioni candidate (più 4 aggiunte)

Regola: una destinazione passa solo se una **fonte ufficiale** (legge, delibera/ordinanza, pagina dell'autorità fiscale
comunale/regionale/nazionale o dati aperti ufficiali) dà **la tariffa 2026 completa** (importo, unità, regole). Se la fonte
principale blocca (403/404) serve una seconda fonte ufficiale; altrimenti la destinazione è esclusa. Blog e aggregatori mai.

| # | Destinazione | Fonte ufficiale usata | HTTP | Formato | Tariffa 2026 completa | Lettura automatica | Esito |
|---|---|---|---|---|---|---|---|
| 1 | **Francia** (gruppo: 10.908 comuni) | data.economie.gouv.fr, dataset DGFiP `delta_deliberation_ts_tarif0` (API) + regole: service-public.gouv.fr F31635, guida DGCL (fiche 4 e 6, giugno 2026) | 200 | API JSON/CSV; PDF | Sì per le comuni con righe 2026 (Nizza, Marsiglia, Tolosa non hanno righe 2026: non mostrate) | Sì (`raccolta/francia.py`) | **PASSA** |
| 2 | Barcellona | atc.gencat.cat/ca/tributs/ieet/quota-tributaria/ (+ pagina IEET) | 200 | HTML | Sì (1/4/2026–31/3/2027) | Sì | **PASSA** |
| 3 | Catalogna (resto) | stessa fonte ATC | 200 | HTML | Sì (2026-27 e dal 1/4/2027) | Sì | **PASSA** |
| 4 | Maiorca | BOE, testo consolidato Ley 2/2016 (BOE-A-2016-4175), art. 5 e 13 | 200 | HTML | Sì | Sì | **PASSA** |
| 5 | Ibiza | idem | 200 | HTML | Sì | Sì | **PASSA** |
| 6 | Minorca | idem | 200 | HTML | Sì | Sì | **PASSA** |
| 7 | Formentera | idem | 200 | HTML | Sì | Sì | **PASSA** |
| 8 | Canarie | nessuna tassa regionale; solo il comune di Mogán (fonte non letta) | – | – | No | – | ESCLUSA |
| 9 | Atene | Gazzetta ufficiale ΦΕΚ Α' 198/05.12.2024, legge 5162/2024 art. 24 (copia ufficiale su archivio search.et.gr); AADE dà 403 | 200 (AADE 403) | PDF testo | Sì (dal 2025, nessuna modifica successiva trovata) | Sì | **PASSA** |
| 10 | Santorini | idem (tariffa nazionale) | 200 | PDF | Sì | Sì | **PASSA** |
| 11 | Mykonos | idem | 200 | PDF | Sì | Sì | **PASSA** |
| 12 | Creta | idem | 200 | PDF | Sì | Sì | **PASSA** |
| 13 | Rodi | idem | 200 | PDF | Sì | Sì | **PASSA** |
| 14 | Corfù | idem | 200 | PDF | Sì | Sì | **PASSA** |
| 15 | Turchia (pagine: Turchia, Istanbul, Antalya, Bodrum) | Resmî Gazete n. 33240 del 1/5/2026, Decisione presidenziale 11263 (1% fino al 31/12/2026) + guida GİB (2%, base senza IVA) | 200 | PDF (Gazzetta: testo non estraibile, letta come immagine) | Sì | Parziale | **PASSA** |
| 16 | Dubrovnik | decisione della contea di Dubrovnik-Neretva 2026 non trovata | – | – | No | – | ESCLUSA |
| 17 | Spalato | decisione della contea di Spalato-Dalmazia 2026 non letta | – | – | No | – | ESCLUSA |
| 18 | Lisbona | informacoeseservicos.lisboa.pt e lisboa.pt | 403 | – | No (Diário da República non raggiunto) | No | ESCLUSA |
| 19 | Porto | porto.pt (pagine taxa municipal turística) | 200 ma pagina "not found" (app Next.js) | – | No | No | ESCLUSA |
| 20 | Algarve (Albufeira, Faro, Lagos, Portimão, Loulé) | nessun regolamento comunale letto (solo notizie) | – | – | No | – | ESCLUSA |
| 21 | Amsterdam | amsterdam.nl 403 → seconda fonte ufficiale: Verordening Toeristenbelasting 2024, repository CVDR703815 (ancora la versione in vigore) | 200 (sito comune 403) | XML | Sì (12,5%) | Sì | **PASSA** |
| 22 | Berlino | berlin.de, modulo ufficiale ÜnSt 2a (7,5% dal 1/1/2025) + disegno di legge parlament-berlin.de (§4 base, §5 aliquota) | 200 | PDF | Sì | Sì | **PASSA** |
| 23 | Vienna | wien.gv.at/amtswege/ortstaxe | 200 | HTML | Sì (3,2% fino al 30/6/2026, 5% dal 1/7/2026, 8% dal 1/7/2027) | Sì | **PASSA** |
| 24 | Budapest | tassa decisa dai 23 distretti; nessuna fonte unica letta | – | – | No | – | ESCLUSA |
| 25 | Praga | sbirkapp.gov.cz (ordinanze 18/2019 e 19/2021) + e-sbirka.gov.cz (legge 565/1990, esenzioni); praha.eu bloccato dal proxy (502) | 200 | PDF, JSON | Sì (50 CZK) | Sì | **PASSA** |
| 26 | Edimburgo | edinburgh.gov.uk/business/visitor-levy-edinburgh (+ esenzioni) | 200 | HTML | Sì (5%, max 5 notti, dal 24/7/2026) | Sì | **PASSA** |
| 27 | Venezia | comune.venezia.it (tariffe imposta di soggiorno) e cda.ve.it (contributo d'accesso) | 403 | – | No | No | ESCLUSA |
| 28 | Roma | comune.roma.it: PDF tariffe dal 1/10/2023 + scheda servizio + regolamento 34/2024 | 200 | PDF, HTML | Sì | Sì | **PASSA** |
| 29 | Firenze | servizi.comune.fi.it: delibera 535/2024 (dal 1/2/2025) + pagina informativa | 200 | PDF, HTML | Sì | Sì | **PASSA** |
| 30 | Milano | comune.milano.it: PDF tariffe 2026 (gen-mar e dal 1/4/2026) + avviso ufficiale esenzioni | 200 | PDF | Sì (fino al 31/12/2026) | Sì | **PASSA** |
| 31 | Kyoto | city.kyoto.lg.jp/gyozai/page/0000236942.html | 200 | HTML | Sì (dal 1/3/2026) | Sì | **PASSA** |
| 32 | Tokyo | tax.metro.tokyo.lg.jp/shitsumon/leisure/general_01 | 200 | HTML | Sì (fino al 31/3/2027) | Sì | **PASSA** |
| 33 | Osaka | pref.osaka.lg.jp (tutte le pagine) | 408 | – | No (seconda fonte ufficiale non trovata) | No | ESCLUSA |
| 34 | Niseko / Kutchan | soumu.go.jp (consenso MIC 31/7/2025) + poster ufficiale Hokkaido per Kutchan + elenco MIC 1/10/2026 | 200 | PDF, immagine | Sì (3% totale dal 1/4/2026) | Parziale (poster letto come immagine) | **PASSA** |
| 35 | Hakuba | soumu.go.jp: consenso Hakuba (bande) + consenso Nagano + elenco MIC | 200 | PDF | Sì (dal 1/6/2026) | Sì | **PASSA** |
| 36 | Okinawa | elenco MIC 1/10/2026: approvata, in vigore dal 1/2/2027 | 200 | PDF | No per il 2026 | Sì | ESCLUSA (da aggiungere a gennaio 2027) |
| 37 | Bali | lovebali.baliprov.go.id | 200 | HTML | Sì l'importo (IDR 150.000); il PDF del regolamento dà 403 | Sì | **PASSA** (con nota: "per visita" ed esenzioni non riportati) |
| 38 | Quintana Roo (Visitax) | visitax.gob.mx | 200 | HTML | No: l'importo non è in pagina (2,5 UMA secondo fonti non ufficiali) | No | ESCLUSA |
| 39 | Egitto | nessuna fonte ufficiale trovata | – | – | No | – | ESCLUSA |
| 40 | Marocco | tassa comunale; nessuna delibera ufficiale letta | – | – | No | – | ESCLUSA |
| 41 | Islanda | althingi.is (legge 87/2011 al 1/10/2026) + skatturinn.is | 200 | HTML | Sì | Sì | **PASSA** |
| 42 | Sapporo (aggiunta) | city.sapporo.jp + consenso MIC Hokkaido | 200 | HTML, PDF | Sì (dal 1/4/2026) | Sì | **PASSA** |
| 43 | Glasgow (aggiunta) | glasgow.gov.uk/visitorlevy | 403 | – | No | No | ESCLUSA |
| 44-45 | Zante, Kos (aggiunte) | come Grecia | 200 | PDF | Sì | Sì | **PASSA** |

**Risultato:** sulle 41 candidate, **28 passano** (Francia contata come un solo gruppo), 13 escluse; con Sapporo le
destinazioni con dati ufficiali completi sono **29** → soglia di lancio (≥ 25) **superata**.

Onestà sul conteggio: le 29 destinazioni poggiano su **21 regole ufficiali distinte** (la Grecia è una sola legge nazionale
per 6 isole/città, le Baleari una sola legge per 4 isole, la Turchia una sola regola). Rispetto al criterio più severo dello
studio 18 (≥ 85% delle 40 con fonte completa) siamo al 68%: le esclusioni riguardano soprattutto siti comunali che bloccano
i robot (Lisbona, Venezia, Osaka, Glasgow) e tasse decise da contee o distretti (Croazia, Budapest).

Sito costruito: 33 pagine di destinazione (29 sopra + Turchia/Istanbul/Antalya/Bodrum come 4 pagine e Zante/Kos),
150 pagine comunali francesi, ricerca su 10.908 comuni francesi.

## 2. Esempi calcolati a mano (controllati da `verifica.py`, tutti OK)

| # | Caso | Calcolo a mano | Atteso | Motore |
|---|---|---|---|---|
| 1 | Barcellona 5 stelle, 15/10/2026, 9 notti, 2 adulti + 1 ragazzo di 16 | 7 notti (max) × (7,00 + 5,00) × 2 | €168,00 | OK |
| 2 | Maiorca hotel 4* sup, 28/10/2026, 10 notti, 2 adulti + 1 bambino | 4 notti × 8 + 4 notti × 2 (bassa stagione −75%) + 2 notti × 1 (dal 9° giorno −50%) | €42,00 | OK |
| 3 | Santorini hotel 4*, 1 camera, 30/10/2026, 4 notti | 2 × 10 (apr-ott) + 2 × 3 (nov-mar) | €26,00 | OK |
| 4 | Amsterdam €200/notte senza IVA, 3 notti | 12,5% × 200 × 3 | €75,00 | OK |
| 5 | Vienna €100/notte, 29/6/2026, 4 notti | 2 × (3,2% × 89% × 100) + 2 × (5% × 100) = 5,696 + 10 | €15,70 | OK |
| 6 | Edimburgo £120/notte, 7 notti | 5 notti (max) × 5% × 120 | £30,00 | OK |
| 7 | Kyoto camera ¥30.000 per 2, 3 notti | ¥15.000 a persona → fascia ¥400 × 2 × 3 | ¥2.400 | OK |
| 8 | Tokyo camera ¥25.000 per 2, 2 notti | ¥12.500 a persona → ¥100 × 2 × 2 | ¥400 | OK |
| 9 | Hakuba camera ¥45.000 per 2, 3 notti (dic. 2026) | ¥22.500 a persona → (¥300 villaggio + ¥100 Nagano) × 2 × 3 | ¥2.400 | OK |
| 10 | Parigi non classificato €150, 2 adulti + 2 minori, 2 notti (caso 1 della guida DGCL) | 5% × 37,50 = 1,88 → × 3,25 (10% + 200% + 15%) = 6,11 × 2 adulti × 2 notti | €24,44 | OK |
| 11 | Parigi non classificato €800, 4 adulti, 1 notte | 5% × 200 = 10 → tetto €4,90 → × 3,25 = 15,93 × 4 | €63,72 | OK |
| 12 | Parigi hotel 4*, 2 adulti, 3 notti | 8,45 (2,60 + 225%) × 2 × 3 | €50,70 | OK |
| 13 | Praga, 2 adulti + 1 bambino, 4 notti | 50 × 2 × 4 | 400 CZK | OK (il primo calcolo a mano, 200, era sbagliato: corretto) |
| 14 | Praga, 61 notti | soggiorni oltre 60 giorni fuori dalla tassa | 0 | OK |
| 15 | Roma 5 stelle, 2 adulti + bambino di 8, 12 notti | 10 × 2 × 10 (max) | €200,00 | OK |
| 16 | Milano 5 stelle, 30/3/2026, 4 notti, 2 adulti | 2 × (10 × 2) + 2 × (12 × 2) | €88,00 | OK |
| 17 | Turchia TRY 5.000/notte senza IVA, 29/4/2026, 4 notti | 2 × 2% × 5.000 + 2 × 1% × 5.000 | TRY 300,00 | OK |
| 18 | Islanda hotel, 2 camere, 3 notti | 800 × 2 × 3 | ISK 4.800 | OK |
| 19 | Bali, 3 viaggiatori | 150.000 × 3 | IDR 450.000 | OK |
| 20 | Berlino €150/notte senza IVA, 2 notti | 7,5% × 150 × 2 | €22,50 | OK |
| 21 | Firenze 4 stelle, 2 adulti, 10 notti | 7 × 2 × 7 (max) | €98,00 | OK |
| 22 | Sapporo camera ¥24.000 per 2, 3 notti | ¥12.000 a persona → ¥300 × 2 × 3 | ¥1.800 | OK |
| 23 | Kutchan ¥60.000/notte, 3 notti | 3% × 60.000 × 3 | ¥5.400 | OK |
| 24 | Catalogna 5 stelle, 30/3/2027, 3 notti, 2 adulti | 2 × (4,50 × 2) + 1 × (6,00 × 2) | €30,00 | OK |

## 3. Altri controlli (10/10/2026)

- `python3 touristtax/genera.py`: nessun errore; 202 pagine indicizzabili (33 destinazioni, 150 comuni francesi,
  12 pagine paese, Francia, Europa 2026, come funziona, fonti, contatti, privacy) + 404, `data/fr.json` (930 KB, caricato
  solo quando si cerca una comune).
- `python3 touristtax/verifica.py`: 24/24 esempi OK; motore JS = motore Python su 2.024 casi (24 esempi + 2.000 casuali,
  anche Francia con tetto e periodi), 0 differenze; 4.767 link interni controllati, 0 rotti; sitemap senza pagine mancanti;
  183/183 pagine di destinazione e comunali con URL della fonte ufficiale e data del controllo.
- Playwright (Chromium, larghezza 375 px): `/`, `/barcelona/`, `/france/paris/`, `/mallorca/`, `/kyoto/`, `/france/` →
  `scrollWidth` = 375 (nessuno scorrimento orizzontale; le tabelle larghe scorrono dentro il loro riquadro), 0 errori in console.
  Prove nel browser: Kyoto scelto dalla home ¥2.400, Barcellona €168,00, Maiorca €42,00, Parigi non classificato €24,44
  (uguali agli esempi 7, 1, 2, 10); ricerca "chamon" → Chamonix-Mont-Blanc, calcolatore attivo.

## 4. Dopo la revisione indipendente (10/10/2026)

Nuovi esempi a mano, tutti OK in `verifica.py` (35 in totale):

| Caso | Atteso |
|---|---|
| Praga 60 notti (61 giorni di calendario) | 0 |
| Praga 59 notti (60 giorni), 2 adulti | 50 × 2 × 59 = 5.900 CZK |
| Milano locazione breve, 20 notti, 2 adulti | 9,50 × 2 × 20 = €380,00 |
| Milano casa per ferie non profit, 20 notti | 7 × 2 × 14 = €196,00 |
| Milano casa per ferie (altri gestori), 20 notti | 7 × 2 × 20 = €280,00 |
| Vienna €100, 1/7 → 1/10/2026 (92 notti, esattamente 3 mesi) | 5% × 100 × 92 = €460,00 |
| Vienna 93 notti / 100 notti (più di 3 mesi) | 0 / 0 |
| Castelldefels 5 stelle, 15/10/2026, 3 notti, 2 adulti | (4,50 + 4,00) × 2 × 3 = €51,00 |
| Esplugues 5 stelle (nessun supplemento per questa categoria) | 4,50 × 2 × 3 = €27,00 |
| Edimburgo £100 dal 22/7/2026, 6 notti | 2 notti prima del 24/7, notti 3-5 tassate, notte 6 oltre il limite: 3 × 5 = £15,00 |

- Confronto motore JS/Python: 2.035 casi (anche soggiorni lunghi 55-100 notti e supplementi comunali), 0 differenze, note comprese.
- Link interni: 4.767, 0 rotti. Fonte + data: 183/183 pagine.
- Playwright 375 px: `/`, `/barcelona/`, `/france/paris/`, `/mallorca/`, `/kyoto/`, `/france/`, `/catalonia/` → scrollWidth 375, 0 errori.
  Nel browser: Castelldefels €51,00; Praga 60 notti 0 CZK con spiegazione; Vienna 93 notti €0,00 e 92 notti €460,00;
  Edimburgo £15,00 con "2 night(s) before 24 July 2026: no tax yet"; Milano locazione breve 20 notti €380,00.
