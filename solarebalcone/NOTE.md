# Balcony Solar Europe (solarebalcone) – note di lavoro

Stato all'**8 novembre 2026**: sito costruito, **non pubblicato, da revisionare**. Serve il collegamento su Netlify da parte di
Massimiliano (passi in fondo). Indirizzo previsto: `https://balcony-solar-europe.netlify.app` (costante `URL_SITO` in `genera.py`,
unico punto da cambiare). Origine: studio `studio-business/intelaiatura/fronti-2026-11-07-mercati-non-inglesi.md`, idea 2.2
(Balkonkraftwerk città per città; voto 6, 750 / 4.600 / 15.000 €/anno con le quattro lingue) e riga "SITO NUOVO" della coda in
`studio-business/DA-PUBBLICARE.md`.

Fotovoltaico da balcone in **italiano, spagnolo e francese**: per ogni Paese, nella sua lingua, le regole ufficiali (con le fonti
numerate e la data di lettura) e un calcolatore di produzione e risparmio con i dati PVGIS della Commissione europea e il prezzo
dell'elettricità Eurostat. **Tedesco (`/de/`) previsto ma spento**: in Germania serve l'Impressum con nome, indirizzo e partita IVA
del titolare; si accende quando Massimiliano conferma che possono stare sul sito pubblico (vedi "Germania" sotto).

## Pagine (29 indicizzabili + 404)

| Lingua | Pagine |
|---|---|
| radice `/` | scelta del Paese (x-default), in inglese con i titoli nelle tre lingue |
| `it/` | home con calcolatore e tabella di 26 città, `regole-fotovoltaico-balcone/`, `domande-frequenti/` (10 FAQ), 9 città (`fotovoltaico-balcone-<città>/`: Roma, Milano, Torino, Palermo, Bologna, Verona, Padova, Parma, Modena), `contatti/`, `privacy/` |
| `es/` | home (24 città), `normativa-placas-solares-balcon/`, `preguntas-frecuentes/` (6 FAQ), 1 città (`placas-solares-balcon-barcelona/`), `contacto/`, `privacidad/` |
| `fr/` | home (25 città), `reglementation-panneau-solaire-balcon/`, `questions-frequentes/` (6 FAQ), 3 città (`panneau-solaire-balcon-<ville>/`: Paris, Toulouse, Nantes), `contact/`, `confidentialite/` |

**Pagine città solo con domanda vera** (`raccolta/domanda.py`, autocompletamento Google `gl`/`hl` del Paese, 8/11/2026): una città ha la
sua pagina se un suggerimento contiene la ricerca e la città ("fotovoltaico da balcone roma", "placas solares balcon barcelona",
"panneau solaire balcon paris", "kit solaire plug and play toulouse"). Le altre 62 città sono solo nel calcolatore e nella tabella della
home (nessuna pagina sottile). Ogni pagina città ha dati propri: stime annue nei due montaggi, 12 mesi, risparmio con 40/60/80% usato in
casa, rientro per kit da 300/500/800 €, posizione tra le città del Paese, 2 FAQ con JSON-LD.

hreflang: home, regole, FAQ, contatti e privacy collegate tra `it-IT`, `es-ES`, `fr-FR` (le home anche verso `x-default` = `/`).
Le pagine città non hanno equivalenti nelle altre lingue (città diverse).

## File

| File | Cosa fa |
|---|---|
| `genera.py` | un comando costruisce tutto `sito/` (pagine, sitemap, robots, 404, `netlify.toml`, `ads.txt`, chiave IndexNow) |
| `verifica.py` | controlli (vedi sotto); `--rete` rilegge le fonti e ricalcola 5 città su PVGIS; `--browser` lancia `verifica_browser.js` |
| `verifica_browser.js` | Playwright: tutte le pagine a 375 e 1280 px, chiaro e scuro, calcolatore, tema, menu del telefono; screenshot in `cache/screenshot/` |
| `raccolta/pvgis.py` | PVGIS `api/v5_3/PVcalc` per ogni città di `dati/citta.json`: 0,8 kWp, perdite 14%, sud, 35° e 90° → `dati/pvgis.json` (URL esatto e sha256 della risposta) |
| `raccolta/prezzi.py` | Eurostat `nrg_pc_204` (famiglie, 2.500-4.999 kWh, tasse comprese, EUR/kWh, ultimo semestre) → `dati/prezzi.json` |
| `raccolta/domanda.py` | autocompletamento Google (città e domande frequenti) → `dati/domanda.json` |
| `raccolta/fonti.py` | rilegge con curl le fonti di `dati/regole.json` → `dati/fonti.json` (HTTP, sha256 del testo, frasi di controllo trovate) |
| `dati/regole.json` | regole e FAQ per Paese, ogni affermazione con le sue fonti; "nota" = frase nostra (prudenza o "non abbiamo trovato"), mostrata come tale |
| `dati/citta.json` | città del calcolatore con coordinate (centro città, 0,01°) |
| `dati/affiliati.json` | riquadro affiliati **spento** (url vuoti) |
| `grafica/` | caratteri Fraunces e Manrope (licenza OFL inclusa), `og.html` + `og.js` → `og.png` |

Comandi (dalla radice del repository):
```
python3 solarebalcone/raccolta/fonti.py        # prima di ogni pubblicazione con regole cambiate
python3 solarebalcone/raccolta/prezzi.py       # quando Eurostat pubblica un semestre nuovo (aprile e ottobre circa)
python3 solarebalcone/raccolta/pvgis.py        # solo se cambiano città o versione di PVGIS
python3 solarebalcone/raccolta/domanda.py      # ogni 2-3 mesi: nuove città con domanda = nuove pagine
python3 solarebalcone/genera.py
python3 solarebalcone/verifica.py --rete --browser   # deve finire con "Tutti i controlli superati."
```
Se si cambia `verificato_il` in `dati/regole.json`, farlo solo dopo aver riletto le fonti.

## Fonti lette l'8/11/2026 (18 con HTTP 200 e frasi di controllo trovate, 3 non lette con motivo)

- **Comuni:** PVGIS (pagina API: limite 30 chiamate/s; pagina "Geospatial Data Download": "free for public use if the source is
  acknowledged (PVGIS © European Communities, 2001-2026)"); avviso legale della Commissione (CC BY 4.0); Eurostat (avviso sul copyright:
  riuso "authorised provided the source is acknowledged"; dati `nrg_pc_204` aggiornati il 19/10/2026, semestre 2026-S1: IT 0,3142,
  ES 0,2509, FR 0,2485, DE 0,3618 €/kWh).
- **Italia:** ARERA, scheda tecnica e pagina della delibera 315/2020/R/eel (impianti < 800 W, Comunicazione Unica al distributore,
  gratis, titolo abilitante, nessun compenso per l'energia immessa, Plug & Play ≤ 350 W con presa dedicata, CEI 0-21, GAUDÌ);
  Codice civile art. 1122-bis su Normattiva (serve il cookie di sessione: `raccolta/fonti.py` lo gestisce); Agenzia delle Entrate,
  "Ristrutturazioni edilizie: che cos'è" (agg. 29/7/2026: 36%/50% abitazione principale nel 2025-2026, 30%/36% nel 2027).
  **Non lette:** Norma CEI 0-21 (a pagamento); Tuir art. 16-bis su Normattiva (tempo scaduto due volte): la pagina dice che non
  sappiamo se un kit con la spina rientri nella detrazione.
- **Spagna:** BOE, RD 244/2019 consolidato (agg. 21/03/2026: sin/con excedentes, antivertido, esenzione permessi, registro de oficio
  < 100 kW in BT, batterie che condividono misura e protezioni); IDAE, Guía profesional de tramitación del autoconsumo v.6 (luglio
  2024, PDF sulla libreria MITECO: < 800 VA senza circuito dedicato, documentazione dal fabbricante/venditore del kit, corrente di
  fuga ≤ 10 mA); Ley de Propiedad Horizontal (agg. 03/10/2026, artt. 7 e 17.1); TRLRHL art. 74.5 (bonifica IBI fino al 50%).
  Nessuna regola specifica per i kit "enchufables" né limite di 800 W trovato: la pagina lo dice.
- **Francia:** Enedis, "Autoconsommer la totalité…" (dichiarazione obbligatoria anche senza immissione, Enedis-Connect, Consuel o
  attestazione, dispensa per plug & play NF EN 50549-1); CACSI Enedis-FOR-RAC_43E v6 del 01/01/2025 (≤ 36 kVA, 15 giorni, Consuel
  oltre 3 kVA o con batteria, condizioni dell'attestazione); Service-Public F36798 (tetto: déclaration préalable) e F31923 (a terra
  < 3 kW e ≤ 1,80 m: nessuna formalità); photovoltaique.info (Hespul, centro di risorse: marcato come non ente pubblico).
  **Non letta:** legge 65-557 sulla copropriété (Légifrance 403): la pagina lo dice e rimanda al syndic. Nessuna fonte ufficiale
  sul kit appeso al garde-corps: la pagina rimanda alla mairie.

## Calcolatore (assunzioni scritte in ogni pagina)

produzione = E_y PVGIS del kit da 800 Wp × potenza/800 · usata in casa = produzione × quota (ipotesi 60%, modificabile) ·
risparmio = usata × prezzo Eurostat (modificabile) · rientro = prezzo del kit (esempio 500 €, non un prezzo rilevato) ÷ risparmio.
Niente compenso per l'energia immessa (Italia: ARERA; Spagna sin excedentes; Francia CACSI), niente interessi, degrado o variazioni
di prezzo. Stessa formula in Python (`genera.calcola`) e JS (`calcola` in `assets/app.*.js`), stesso arrotondamento (metà per eccesso)
e stesso formato dei numeri (`fmt`): `verifica.py` li confronta su 300 casi.

## Monetizzazione

- **AdSense acceso** (codice `ca-pub-3750093987658434`, lo stesso degli altri siti): `solarebalcone` aggiunto a `adsense_siti` in
  `studio-business/strumenti/monetizzazione.json`; script nel `<head>` di ogni pagina, `ads.txt`, privacy con la sezione sulla
  pubblicità nella lingua della pagina. In AdSense: aggiungere il sito (Siti → Aggiungi) quando è online.
- `monetizzazione.py` ora sa anche lo **spagnolo e il francese** (riga di trasparenza, sezioni privacy su cookie, affiliazioni e
  AdSense; pagine privacy `privacidad/` e `confidentialite/`); gli altri siti non cambiano (Visa Income es/pt continua a usare la riga
  inglese, ammessa). `amazon.es` e `amazon.fr` aggiunti ai domini Amazon (link solo con `tag=`).
- **Riquadro affiliati SPENTO** (`dati/affiliati.json`, url vuoti): EcoFlow, Zendure, Amazon .it/.es/.fr per lingua. Per accenderlo:
  mettere l'URL vero (EcoFlow via Awin `awin1.com`, già ammesso; Zendure: aggiungere prima il dominio dei suoi link in
  `monetizzazione.json`; Amazon: `url` qualsiasi non vuoto + `tag` del Paese, il link diventa una ricerca). Compare nella pagina regole
  e nelle pagine città, con etichetta, `rel="sponsored noopener"`, riga di trasparenza, frase Amazon nella lingua e sezione nella privacy.
- IndexNow: host aggiunto a `studio-business/strumenti/indexnow.py` ma in `NON_ONLINE` (saltato nell'invio di tutti i siti finché
  la chiave non è online). Il giorno della pubblicazione: togliere l'host da `NON_ONLINE` e lanciare
  `python3 studio-business/strumenti/indexnow.py --solo balcony-solar-europe.netlify.app`.

## Dati personali

Nessun nome o indirizzo di Massimiliano nel sito: la privacy indica come titolare "il gestore di questo sito, una persona fisica con
sede in Italia" e il modulo di contatto (Netlify Forms, nome `contatto`, campo nascosto `lingua`). Gli altri siti della rete hanno il
nome nella privacy: se Massimiliano vuole, si può aggiungere (decisione sua).

## Controlli dell'8/11/2026 (`python3 solarebalcone/verifica.py --rete --browser`: "Tutti i controlli superati")

1. Fonti: 18 lette con HTTP 200, impronta e frasi di controllo presenti (rilette in rete), 3 non lette con motivo; ogni affermazione ha
   fonti esistenti o è una nota nostra. 2. PVGIS: 75 città × 2 montaggi, mesi = totale annuo, URL e impronta coerenti; 5 città a caso
   ricalcolate sull'API (scarto 0). 3. Calcolatore: 300 casi JS = Python; 52 numeri stampati nelle pagine città = calcolo; dati
   incorporati = `dati/pvgis.json`. 4. FAQ: 48 domande, JSON-LD = testo; ogni FAQ viene da una ricerca salvata. 5. hreflang reciproci
   (16 pagine), link e ancore interni validi, sitemap = 29 pagine con canonical, titoli ≤ 70 caratteri, descrizioni 70-165, `/de/`
   assente. 6. Monetizzazione: AdSense coerente, 0 link di affiliazione (riquadro spento). 7. Niente dati personali né nomi di modelli
   AI. Browser: 30 pagine × 375/1280 px × chiaro/scuro, nessuno scorrimento orizzontale, nessun errore JS, calcolatore corretto
   dopo cambio di città/montaggio/potenza, avviso oltre la soglia, tema e menu del telefono funzionanti.

**Da fare prima di pubblicare:** revisione indipendente su fatti e aspetto (regola del 15/10/2026), in particolare: testi spagnoli e
francesi letti da un revisore, risposta FAQ "comunidad de vecinos", frase sulla detrazione italiana.

## Germania (spenta)

`regole.json` → `paesi.de.attiva = false`; `genera.py` si ferma se la si accende senza la versione tedesca. Da fare quando Massimiliano
conferma l'Impressum: testi `T["de"]`, fonti (Bundesnetzagentur/MaStR per la registrazione, EEG e Solarspitzengesetz su
gesetze-im-internet.de per gli 800 VA, WEG § 20 per il condominio, contributi comunali con scadenza), città con domanda
("balkonkraftwerk <stadt>"), prezzo DE già in `dati/prezzi.json`, pagina Impressum, cartella `sito/de/`.

## Impostazioni Netlify (da fare da Massimiliano)

1. Netlify → Add new site → Import an existing project → GitHub → repository `copertine-libri`, ramo `ccr-b7fd6b9e-n096cr`.
2. **Base directory: `solarebalcone/sito`** · **Build command: vuoto** · **Publish directory: `.`** (lo dice anche
   `sito/netlify.toml`, con la regola che pubblica solo se cambia `solarebalcone/sito`).
3. Site name: `balcony-solar-europe` (se è preso, sceglierne un altro e dirlo: si cambia `URL_SITO` in `genera.py` e si rigenera).
4. Forms → attivare le notifiche email del modulo `contatto`.
5. Search Console: la meta di verifica è già in ogni pagina (stesso account degli altri siti); aggiungere la proprietà e inviare
   `sitemap.xml`. AdSense: Siti → Aggiungi.
Crediti Netlify: 15 per pubblicazione; questo sito si aggiorna di rado (fonti e prezzi due volte l'anno).
