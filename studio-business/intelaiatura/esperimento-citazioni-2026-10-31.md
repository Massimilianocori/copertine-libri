# Esperimento 1: pagine più facili da citare per gli assistenti (Visa Income, 31/10/2026)

Origine: `fronti-2026-10-31-traffico.md`, sez. 1 (voto 8) e sez. 7, esperimento E1. Costruito il 31/10/2026, **pubblicato il 31/10/2026 alle 14:20 circa (ora di Roma)**: il conteggio parte dal 1/11/2026 (`--dal 2026-11-01`).

## Domanda
Le pagine con data di aggiornamento visibile, `dateModified`, un riquadro di cifre ufficiali in frasi complete e un CSV con schema `Dataset` ricevono più visite da ChatGPT (provenienza `chatgpt.com`) delle pagine uguali senza queste aggiunte?

## Pagine e gruppi
- **Pagine:** le 74 pagine Paese di `/visa-refusal-rates/<paese>/` (Paesi con almeno 10.000 domande Schengen nel 2025, `genera.PAESI_RIF`).
- **Escluse (2):** `united-kingdom` e `united-arab-emirates`: cambiate oggi per la sezione "Schengen visa from the UK / from Dubai" (titolo, H1, primo paragrafo), quindi le loro visite dopo il 31/10 non sono confrontabili e quel contenuto revisionato non si tocca.
- **72 pagine → 36 coppie.** Ordine: visite da `chatgpt.com` dal 17/10 (primo giorno del contatore) al 31/10, poi visite totali, poi domande di visto 2025 (dimensione del Paese), poi slug; si accoppiano le vicine. In ogni coppia `random.Random(20261031)` sceglie la trattata (prima pagina se `random() < 0,5`). Le visite sono state lette dall'API di GoatCounter il 31/10/2026.
- **Elenco salvato:** `visaincome/dati/esperimento_citazioni.json` (seme, metodo, linea di base per pagina, coppie, gruppi, impronte delle pagine di controllo). Il controllo 25 di `verifica.py` rifà l'assegnazione dal seme e dalla linea di base salvata e deve dare lo stesso risultato.

Formato: Paese (visite da ChatGPT / visite totali 17-31/10; domande Schengen 2025).

| # | Trattata | Controllo |
|---|---|---|
| 1 | Pakistan (16/18; 89.270) | Iraq (5/6; 70.312) |
| 2 | Bangladesh (5/5; 38.642) | Tunisia (5/5; 188.579) |
| 3 | Türkiye (4/4; 1.268.376) | Nigeria (4/4; 113.359) |
| 4 | India (3/4; 1.153.748) | Iran (4/4; 107.512) |
| 5 | Philippines (3/4; 235.674) | Morocco (3/3; 619.827) |
| 6 | Algeria (2/2; 444.577) | Azerbaijan (2/2; 104.143) |
| 7 | China (1/1; 1.915.149) | Qatar (1/2; 102.930) |
| 8 | Egypt (1/1; 226.865) | Indonesia (1/1; 223.862) |
| 9 | Jordan (1/1; 73.264) | United States (1/1; 187.033) |
| 10 | Sri Lanka (1/1; 25.663) | Ireland (1/1; 30.696) |
| 11 | Georgia (1/1; 10.642) | Serbia (1/1; 19.656) |
| 12 | Singapore (0/1; 39.226) | Kazakhstan (0/1; 182.002) |
| 13 | Australia (0/1; 19.163) | Russia (0/0; 679.425) |
| 14 | Saudi Arabia (0/0; 553.967) | Thailand (0/0; 264.190) |
| 15 | Belarus (0/0; 157.028) | South Africa (0/0; 195.946) |
| 16 | Kuwait (0/0; 146.194) | Lebanon (0/0; 120.364) |
| 17 | Armenia (0/0; 111.550) | Vietnam (0/0; 116.289) |
| 18 | Côte d'Ivoire (0/0; 81.886) | Ecuador (0/0; 106.167) |
| 19 | Kenya (0/0; 77.760) | Angola (0/0; 72.766) |
| 20 | Ghana (0/0; 63.725) | Senegal (0/0; 71.923) |
| 21 | Uzbekistan (0/0; 61.328) | Cameroon (0/0; 57.469) |
| 22 | Oman (0/0; 53.700) | Dominican Republic (0/0; 52.063) |
| 23 | Canada (0/0; 43.982) | DR Congo (0/0; 52.048) |
| 24 | Libya (0/0; 43.701) | Cuba (0/0; 38.585) |
| 25 | Kyrgyzstan (0/0; 30.843) | Israel (0/0; 31.500) |
| 26 | Cape Verde (0/0; 27.598) | Ethiopia (0/0; 26.166) |
| 27 | Republic of the Congo (0/0; 25.693) | Mauritania (0/0; 25.265) |
| 28 | Guinea (0/0; 22.335) | Bahrain (0/0; 25.110) |
| 29 | Mongolia (0/0; 21.997) | Mozambique (0/0; 21.695) |
| 30 | Uganda (0/0; 20.691) | Suriname (0/0; 21.281) |
| 31 | Gabon (0/0; 17.270) | Madagascar (0/0; 16.489) |
| 32 | Japan (0/0; 16.369) | Bolivia (0/0; 16.230) |
| 33 | Tanzania (0/0; 16.227) | Hong Kong (0/0; 15.954) |
| 34 | Benin (0/0; 15.364) | Cambodia (0/0; 14.228) |
| 35 | Cyprus (0/0; 12.980) | Mali (0/0; 11.336) |
| 36 | Togo (0/0; 10.427) | Equatorial Guinea (0/0; 10.139) |

**Linea di base 17-31/10 (15 giorni):** trattate 38 visite da ChatGPT (44 in tutto), controllo 28 (31). Rapporto di partenza **1,36**, quasi tutto per la coppia 1 (Pakistan 16 contro Iraq 5): senza la coppia 1, 22 contro 23. Per questo il verdetto guarda anche il rapporto corretto per la partenza (sotto).

## Cosa ricevono solo le 36 trattate (in `genera.py`, blocco "Esperimento")
1. Riga **"Updated on 31 October 2026 · Data: European Commission, 2025"** subito sotto il titolo. La data è quella del registro `dati/lastmod.json` (ultima modifica del contenuto, la stessa della sitemap): si muove solo quando il contenuto cambia davvero, non a ogni generazione.
2. **`dateModified`** nel JSON-LD (nodo `WebPage` nuovo e nodo `Dataset`), stessa data. `datePublished` non c'era e non è stato aggiunto.
3. Riquadro **"Key figures"** in cima (prima del riepilogo), 4 frasi brevi e complete, ognuna con anno e Paese: domande 2025; tasso "not issued" con non rilasciati e decisioni; visti uniformi rilasciati; tasso 2024 e differenza in punti. Sotto: fonte con link al file XLSX della Commissione e data di scaricamento (15/10/2026), formula del tasso, licenza, link al CSV.
4. **Schema `Dataset`** (nome, descrizione, `isBasedOn` con i due file della Commissione, `temporalCoverage` 2024/2025, `spatialCoverage`, `license` CC BY 4.0, `creditText`, `distribution` → `DataDownload` `text/csv`) e **`/visa-refusal-rates/<paese>/data.csv`** generato dagli stessi dati di `dati/rifiuti.json`: una riga per anno × Stato Schengen più il totale, colonne `year, place_of_application, schengen_country, applications, uniform_visas_issued, multiple_entry_visas_issued, ltv_visas_issued, not_issued, decisions, not_issued_rate_percent`. Il CSV non va in sitemap (non è una pagina); la pagina sì, come prima.
5. Poche regole CSS solo nelle pagine trattate (`css_extra`), così le pagine di controllo restano uguali byte per byte.

**Licenza (verificata il 31/10/2026):** avviso legale della Commissione https://commission.europa.eu/legal-notice_en (HTTP 200): "The Commission's reuse policy is implemented by the Commission Decision of 12 December 2011 on the reuse of Commission documents [2011/833/UE]. Unless otherwise indicated … content owned by the EU on this website is licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0) licence. This means that reuse is allowed, provided appropriate credit is given and changes are indicated." Nel file XLSX 2025 (copia in `visaincome/raccolta/_grezzi/`) non c'è nessun avviso di copyright o di licenza diverso (cercato nel testo di tutti i fogli). In pagina: "© European Union; reuse allowed under CC BY 4.0 (Commission legal notice, Decision 2011/833/EU)", fonte con link e data, e la formula del tasso (cambio indicato: è un nostro ricalcolo). Il CSV è CC BY 4.0 con la stessa attribuzione (`creditText`). Il testo della decisione su EUR-Lex non è leggibile dal server (risposta 202 vuota, come già scritto in `visaincome/NOTE.md`): si cita tramite l'avviso legale.

## Controllo invariato (prova del 31/10/2026)
- Copia di `visaincome/sito/` prima della modifica, poi `genera.py` con l'esperimento: cambiate **solo** le 36 pagine trattate e aggiunti i 36 `data.csv`; le **36 di controllo identiche byte per byte**; sitemap e `dati/lastmod.json` uguali (le pagine Paese avevano già il lastmod del 31/10). Seconda generazione: nessuna differenza.
- Le impronte (contenuto e SHA-256 del file) delle 36 pagine di controllo sono nel JSON; il controllo 25 di `verifica.py` le confronta a ogni verifica e fallisce se una pagina di controllo cambia o riceve un elemento del trattamento. Prova al contrario fatta: un numero cambiato nel CSV o nel riquadro, "Updated on" o una parola cambiata in una pagina di controllo, `dateModified` diverso → errore.
- **Durante l'esperimento** non si cambiano le pagine Paese dei rifiuti. Se un aggiornamento dei dati è necessario (per esempio il giro mensile di `rifiuti_altri.json`, che cambia i due gruppi allo stesso modo): `python3 visaincome/genera.py`, poi `python3 visaincome/raccolta/esperimento_citazioni.py impronte --motivo "..."` (riscrive le impronte solo se nessuna pagina di controllo ha elementi del trattamento e annota data e motivo nel JSON), e una riga qui sotto.

## Metrica, soglia, date
- **Metrica:** visite con provenienza `chatgpt.com` per pagina (GoatCounter `stats/hits/{id}`, campo `refs`), sommate per gruppo, dal giorno dopo la pubblicazione.
- **Soglia di successo:** trattate **≥ 1,5 volte** le controllo **e ≥ 30 visite al mese in più** (differenza riportata a 30 giorni). Per non contare il vantaggio di partenza, anche il **rapporto corretto** (rapporto del periodo ÷ 1,36) deve essere ≥ 1,5. Lo script stampa anche il risultato senza la coppia 1 e una prova a permutazione sulle coppie (quanto spesso il caso dà una differenza così grande): servono a dire quanto fidarsi, non cambiano la soglia.
- **Limite onesto:** circa 70 visite da ChatGPT in 15 giorni su queste pagine; la prova vede solo effetti grandi.
- **Prima lettura: lunedì 30/11/2026** (periodo dal giorno dopo la pubblicazione al 29/11). **Verdetto: lunedì 28/12/2026** (dal giorno dopo la pubblicazione al 27/12).
- **Se sì:** la stessa forma va su tutte le pagine Paese dei rifiuti e poi sulle pagine di dati della rete (Visa Income, Cruise, Tourist Tax, Before You Fly, EsameB1). **Se no:** si tiene la data visibile e il CSV su tutte (utili ai lettori e a Dataset Search), senza aspettarsi visite in più.

## Come si misura
```
python3 visaincome/raccolta/esperimento_citazioni.py misura --dal <giorno dopo la pubblicazione> --al 2026-11-29   # prima lettura
python3 visaincome/raccolta/esperimento_citazioni.py misura --dal <giorno dopo la pubblicazione> --al 2026-12-27   # verdetto
```
Lo script chiama, senza nessun token nel codice o in questo file:
- `GET https://rete-siti.goatcounter.com/api/v0/stats/hits?start=AAAA-MM-GGT00:00:00Z&end=AAAA-MM-GGT23:00:00Z&limit=100` (con `exclude_paths` per le pagine successive) → percorsi `/visa-income-checker.netlify.app/visa-refusal-rates/<paese>` e loro `path_id`;
- `GET https://rete-siti.goatcounter.com/api/v0/stats/hits/{path_id}?start=…&end=…&limit=100` → `refs`, si somma `count` dove `name` è `chatgpt.com`.

**Dove sta la chiave:** è un segreto di rete dell'ambiente Default (sola lettura, Bearer, host `rete-siti.goatcounter.com`, percorsi `/api/`), aggiunto dal sistema a ogni richiesta: non si scrive e non si manda l'intestazione `Authorization`. Descritto in `.claude/skills/rete-siti/SKILL.md` (voce GoatCounter) e in `studio-business/CRUSCOTTO-RETE.md` (voce "Chiave API in sola lettura"). 401 = segreto mancante. Limite: 4 richieste al secondo (lo script attende 0,3 s tra le chiamate).

## File
- `visaincome/genera.py`: blocco "Esperimento" (dopo le costanti della sezione rifiuti), `pagina_rif_paese`, `pagina(css_extra=…)`, `impronta_contenuto` (data normalizzata), `extra()` (scrive la data dopo il registro lastmod).
- `visaincome/dati/esperimento_citazioni.json`: coppie, gruppi, linea di base, impronte del controllo.
- `visaincome/raccolta/esperimento_citazioni.py`: `assegna` (fatto il 31/10/2026), `misura`, `impronte`.
- `visaincome/verifica.py`: controllo 25.

## Registro
- 31/10/2026: assegnazione, costruzione, controlli (verifica offline TUTTO OK, monetizzazione 0 errori, Playwright 375/1280 su Pakistan trattata e Iraq controllo: nessuno scorrimento orizzontale, nessun errore JS, CSV 200). Da pubblicare dopo la revisione; annotare qui la data di pubblicazione.
- 27/11/2026, **lettura prima dell'aggiornamento dei dati del Home Office** (`misura --dal 2026-11-01 --al 2026-11-26`, 26 giorni, solo percorsi `/visaincomechecker.com/…`): trattate **121**, controllo **46** visite da `chatgpt.com`; rapporto 2,63; differenza 75 (≈ 87 al mese); coppie vinte 18, pari 10, perse 8. Soglia 1): superata. Rapporto corretto 2,63 ÷ 1,36 = **1,94** (≥ 1,5). Senza la coppia 1: 114 contro 45, rapporto 2,53. Prova a permutazione: p ≈ 0,016. Prime: Türkiye 22, Algeria 18, Bangladesh 16, India 13 (trattate); Russia 11, Morocco 6 (controllo). Il piano delle visite del 27/11 scrive 138 contro 54 perché somma anche il vecchio indirizzo `visa-income-checker.netlify.app` (1–8/11); lo script conta solo il dominio nuovo: il rapporto è lo stesso (2,6). Non è la prima lettura ufficiale (30/11) né il verdetto (28/12): serve a fissare i numeri prima del cambio.
- 27/11/2026, **cambio voluto, uguale nei due gruppi** (non pubblicato): dati del Home Office «year ending September 2026» (blocco UK, fonte e date) sulle 74 pagine Paese, e riga «More about <Paese>» dopo il blocco UK (link per regola verso l'hub `moved-to/<nazionalità>/`, `uk-english-test/<paese>/` e `nurses-abroad/<paese>/` in indice, al massimo 3, fuori dall'impronta del `lastmod`). Titoli delle 74 pagine uguali a prima. `impronte --motivo …` eseguito: impronte delle 36 di controllo riscritte, nessuna con elementi del trattamento. **Da sapere per la lettura**: la regola è la stessa, ma la riga ha almeno un link su 21 trattate (32 link) e su 16 di controllo (20 link), perché dipende da quali Paesi hanno pagine nelle altre sezioni. La riga porta lettori fuori dalla pagina e non cambia ciò che un assistente cita; se il revisore dell'esperimento la ritiene un disturbo, si toglie (blocco tra `<!--stessa-naz-->` e `<!--/stessa-naz-->`) e si rimette dopo il 28/12. **Il verdetto del 28/12 riporta anche il risultato sulle sole 23 coppie bilanciate** (riga presente in tutte e due le pagine o in nessuna; elenco ricalcolabile dal blocco `<!--stessa-naz-->` delle pagine). Nella stessa generazione: nota dell'asterisco sotto la tabella UK (soglie vere: 100 decisioni, 500 per il partner) e impronta del `lastmod` senza le date di lettura/scaricamento delle fonti; impronte di controllo riscritte una volta sola, motivo in `impronte_aggiornate`.
