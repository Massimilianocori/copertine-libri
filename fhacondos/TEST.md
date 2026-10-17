# FHA Approved Condos – test della fonte (17/10/2026)

**Esito: SUPERATO.** Scarico completo di Virginia, Florida e Colorado (stato "approved"): **1.056 condomini su 1.056**
contati dal modulo HUD (100 %, soglia 95 %). **0 errori su 20 condomini** ricontrollati uno per uno sulla fonte
(nome, ID, indirizzo, città, contea, CAP, unità, stato, data di approvazione e di scadenza).

## La fonte

HUD FHA Condominium Lookup, `https://entp.hud.gov/idapp/html/condlook.cfm` (modulo ColdFusion). Dati "as of 10/17/2026"
(la data cambia ogni giorno: HUD aggiorna l'elenco quotidianamente).

Come funziona, verificato dal server il 17/10/2026:
1. `GET condlook.cfm` → il server dà i cookie di sessione (`CFID`, `CFTOKEN`, `cookie_entp`).
2. `POST condo1.cfm` con i campi del modulo (Stato, stato dell'approvazione, tipo di ricerca, date) e la pagina di
   provenienza (`Referer`). La risposta mostra 25 righe e il totale: "(367 records were selected, records 1 through 25 displayed)".
3. Pagine successive: `POST condo1.cfm` con gli stessi campi in maiuscolo più `startAt=26, 51, …` (è il modulo
   "getMoreData" della pagina, il pulsante "next"). Il parametro `maxRows` non cambia la dimensione: sempre 25 righe.
4. Tipo di ricerca: **"Project"** dà una riga per condominio; "Both" aggiunge le fasi ("submission") dello stesso
   condominio. Colorado: 367 progetti + 187 fasi = 554 righe "Both". Per questo i numeri dello studio del 15/10
   (Virginia 2.510, Colorado 553) erano righe "Both", non condomini. Il sito conta i **condomini** (progetti).
5. Filtro per date: con lo stato "Expired" filtra sulla data di scadenza, con "Withdrawn" sulla data dello stato.
   Serve per gli scaduti e ritirati recenti (ultimi 24 mesi) senza scaricare decenni di storico.
6. La scheda di dettaglio (`f17condo-maint.cfm`) risponde solo dalle 8 alle 22 (ora della costa est), dal lunedì al venerdì;
   non serve: tutti i campi utili sono già nell'elenco.

## Scarico dei 3 Stati

Comando: `python3 fhacondos/raccolta/scarica.py --stati CO,VA,FL --tipi A` (una richiesta ogni 1,2-2 secondi, una alla volta,
cache in `fhacondos/cache/2026-10-17/`, ripresa automatica: le pagine già salvate non si riscaricano).

| Stato | Condomini contati dal modulo | Righe lette | Pagine | Copertura |
|---|---|---|---|---|
| Virginia | 617 | 617 | 25 | 100 % |
| Florida | 72 | 72 | 3 | 100 % |
| Colorado | 367 | 367 | 15 | 100 % |
| **Totale** | **1.056** | **1.056** | 43 (+1 apertura sessione) | **100 %** |

Tempo: 69 secondi, 44 richieste, nessun errore. ID tutti distinti; ogni riga ha nome, ID, città, Stato, CAP, contea,
stato "Approved", data di approvazione e di scadenza (scadenze dal 19/10/2026 al 15/10/2029).

Qualità dei campi (1.056 righe):
- CAP, contea, città, via: presenti in tutte le righe dei 3 Stati (negli scaduti vecchi capita "00000" o la contea vuota:
  il CAP 00000 diventa "vuoto").
- **Unità**: HUD non ha un campo numerico, solo un testo libero ("Composition of Project", es. "48 UNITS, 9 BUILDINGS").
  Il numero si ricava con regole prudenti (`numero_unita` in `raccolta/estrai.py`): vale una forma con "total" o un solo
  numero seguito da "units"; numeri di edificio/fase ("BLDG 2 UNITS 101-108") e "12 units per building" sono esclusi.
  Risultato: unità note per **878 su 1.056** (83 %); per le altre il sito scrive "not stated" invece di indovinare.
- Il testo libero e i commenti **non si pubblicano**: contengono a volte sigle di funzionari HUD o note interne.
  Si pubblicano solo nome del complesso, indirizzo del complesso, contea, unità, quota FHA, date.

## 20 condomini ricontrollati uno per uno

Comando: `python3 fhacondos/raccolta/ricontrolla.py --edizione 2026-10-17 --stati VA,FL,CO --seme 20261017`.
Per ognuno una **ricerca nuova** sul modulo per Condo ID (tutti gli Stati, tutti gli stati di approvazione), senza cache.
Ogni campo è controllato due volte: (1) il valore letto dalla riga nuova è uguale al nostro; (2) il nostro valore compare
alla lettera nel testo della riga HUD (date nel formato della fonte), senza passare dal programma di lettura.

| # | Condo ID | Nome (HUD) | Città, Stato | CAP | Contea | Unità | Stato | Data stato | Scadenza | Esito |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | P022991 | MOORE'S LAKE CONDOMINIUM | CHESTER, VA | 23831 | CHESTERFIELD COUNTY | 238 | Approved | 10/09/2024 | 10/09/2027 | OK |
| 2 | P005983 | BRIARWOOD HEARTH | MIDLOTHIAN, VA | 23113 | CHESTERFIELD COUNTY | 225 | Approved | 12/05/2024 | 12/05/2027 | OK |
| 3 | D004837 | MOUNTAIN GATE AT KEN-CARYL II* | LITTLETON, CO | 80127 | JEFFERSON COUNTY | 174 | Approved | 12/23/2024 | 12/23/2027 | OK |
| 4 | P007879 | VIENNA TRAIL CONDOMINIUM | VIENNA, VA | 22180 | FAIRFAX COUNTY | 23 | Approved | 07/08/2024 | 07/08/2027 | OK |
| 5 | P007184 | PARKSIDE AT ALEXANDRIA A CONDO | ALEXANDRIA, VA | 22304 | ALEXANDRIA CITY | 378 | Approved | 05/02/2024 | 05/02/2027 | OK |
| 6 | D007107 | 960 COURTYARD TOWNHOMES* | DENVER, CO | 80203 | DENVER COUNTY | 16 | Approved | 05/14/2026 | 05/14/2029 | OK |
| 7 | A015345 | SHADOW BROOK MOBILE HOME SUB. | PALMETTO, FL | 34221 | MANATEE COUNTY | 392 | Approved | 02/18/2026 | 02/18/2029 | OK |
| 8 | P007825 | THE COVE CONDOMINIUM | FALLS CHURCH, VA | 22042 | FAIRFAX COUNTY | 196 | Approved | 11/21/2023 | 11/21/2026 | OK |
| 9 | D006578 | AVALON CONDOMINIUMS | AURORA, CO | 80014 | ARAPAHOE COUNTY | 64 | Approved | 10/01/2024 | 10/01/2027 | OK |
| 10 | D009516 | WAPITI COMMONS HOMEOWNERS ASSO | RIFLE, CO | 81650 | GARFIELD COUNTY | – | Approved | 01/30/2026 | 01/30/2029 | OK |
| 11 | D003207 | LEGACY VILLAS | WESTMINSTER, CO | 80031 | ADAMS COUNTY | 7 | Approved | 10/20/2023 | 10/20/2026 | OK |
| 12 | P006781 | BALLSTON PARK CONDOMINIUM | ARLINGTON, VA | 22201 | ARLINGTON COUNTY | 137 | Approved | 05/09/2024 | 05/09/2027 | OK |
| 13 | P007840 | THE PONDS AT CENTREVILLE CONDO | CLIFTON, VA | 20124 | FAIRFAX COUNTY | 248 | Approved | 07/02/2025 | 07/02/2028 | OK |
| 14 | P007912 | WATERGATE AT LANDMARK CONDO | ALEXANDRIA, VA | 22304 | ALEXANDRIA CITY | 1460 | Approved | 04/17/2024 | 04/17/2027 | OK |
| 15 | P007732 | SEMINARY WALK CONDOMINIUM | ALEXANDRIA, VA | 22314 | ALEXANDRIA CITY | 208 | Approved | 02/13/2025 | 02/13/2028 | OK |
| 16 | P019226 | BRYAN'S COVE RESIDENTIAL CONDO | CHESAPEAKE, VA | 23323 | CHESAPEAKE CITY | – | Approved | 02/13/2024 | 02/13/2027 | OK |
| 17 | A009913 | GRAMERCY PLACE | TALLAHASSEE, FL | 32308 | LEON COUNTY | – | Approved | 03/12/2025 | 03/12/2028 | OK |
| 18 | D005148 | HEATHERRIDGE SOUTH | AURORA, CO | 80014 | ARAPAHOE COUNTY | 176 | Approved | 04/03/2024 | 04/03/2027 | OK |
| 19 | P007427 | THE HEIGHTS AT PENDERBROOK* | FAIRFAX, VA | 22033 | FAIRFAX COUNTY | 450 | Approved | 03/13/2024 | 03/13/2027 | OK |
| 20 | P005499 | FAIRFIELD GARDENS CONDOMINIUM | VIRGINIA BEACH, VA | 23464 | VIRGINIA BEACH CITY | 156 | Approved | 03/27/2024 | 03/27/2027 | OK |

**0 errori su 20.** (Una richiesta su 22 è stata respinta una volta dal proxy di rete e ripetuta in automatico con una sessione nuova.)

## Rischi rimasti

1. Modulo vecchio: se HUD cambia i nomi dei campi o la tabella, `scarica.py` si ferma (pagina non attesa) ed `estrai.py`
   si ferma se le righe lette non coincidono con il totale dichiarato. Nessun dato sbagliato finisce nel sito.
2. Unità: per il 17 % dei condomini il testo HUD non permette un numero sicuro → "not stated".
3. Lo stato cambia ogni giorno: ogni pagina mostra "HUD data as of", rimanda al lookup ufficiale e avvisa di confermare
   con HUD e con la banca.

Conclusione: si costruisce (fase 2).
