# NAICS Code Lookup – note di lavoro (13/11/2026)

Sito statico in inglese (pubblico USA): classificazione NAICS 2022 del Census Bureau con codici 2017 e raccordo SIC 1987. Famiglia 1 di
`studio-business/intelaiatura/fronti-2026-11-12-volumi-prima.md` («naics code» 90.500/mese a 6 $, «naics code lookup» 49.500 a 8 $).
Stesso motore di `ateco/` (genera, verifica, stile, misura dell'indicizzazione). Indirizzo previsto `https://naics-code-lookup.netlify.app`
(libero il 13/11/2026: 404). `URL_SITO` in `genera.py` e `verifica.py` (cambiarle insieme). **Il sito Netlify non esiste ancora.**

## Fonti (dati/fonti.json: URL, data, SHA-256; file grezzi in raccolta/_grezzi, fuori da git)
Census Bureau: codici 2-6 cifre, struttura (indicatori di cambio), descrizioni, indice (20.373 voci), rimandi, tabella dei conteggi;
concordanze 2022↔2017, 2017←2012←2007←2002←1997; **concordanza ufficiale SIC 1987 ↔ NAICS 1997** (in tutte e due le direzioni);
manuale NAICS 2022 (PDF, 25 frasi controllate); IRS, istruzioni Schedule C 2025 (3 frasi). Tutto dominio pubblico.
Le pagine HTML di census.gov rispondono 403 (Cloudflare): non aggirate, si leggono solo i file (200).
Refuso ufficiale gestito: 323120 «Support Activites for Printing» nella concordanza 2022→2017 (si usa il titolo della struttura).

## Controlli su albero e conteggi (`raccolta/estrai.py` si ferma se non tornano)
2.125 codici: 20 settori, 96 sottosettori, 308 gruppi, 689 industrie a 5 cifre, 1.012 a 6 cifre = tabella ufficiale per ogni settore
(anche le 522 «same as 5-digit»). Padri 2→3→4→5→6 (31-33, 44-45, 48-49), stessi codici e titoli in codici/struttura/descrizioni,
indice e concordanze solo verso codici esistenti.

## Pagine (1.446 HTML: 991 indicizzabili, 455 noindex compresa la 404)
`/` ricerca (due JSON: codici+titoli 209 KB, 46 KB compressi, al primo clic; voci dell'indice 913 KB, 188 KB compressi, scaricate solo quando si scrive una parola, mai per un numero; cerca codici 2022, 2017 e SIC; se nessun codice ha tutte le parole mostra quelli che ne hanno di più), 20 settori, come si legge un
codice, 9 FAQ · `/54/` settori · `/541/` sottosettori · `/5415/` gruppi (con i capitoli `#n-54151` delle industrie a 5 cifre con più figli) ·
`/541511/` industrie a 6 cifre (descrizione, esempi, tutte le voci dell'indice, rimandi linkati, codici 2017, SIC, albero, vicini) ·
`/naics-2017-to-2022/` (1.057 codici 2017, ancore `#v-454110`) · `/sic-to-naics/` (1.005 SIC, ancore `#sic-7371`) ·
40 pagine `/naics-code-for-…/` + indice `/naics-code-for/` (vedi 13/11 sera) · `/how-we-check/` (modulo correzioni Netlify Forms: solo pagina, messaggio e fonte, nessuna email né casella, come milpay), `/about/`, `/privacy/`.

**5 cifre:** nessuna pagina propria. 522 hanno un solo figlio (stesso titolo, «See industry description for …»): l'indirizzo è la pagina a
6 cifre. 167 con più figli: capitolo nella pagina del gruppo. **Indicizzazione:** pagina di codice indicizzata con ≥ 120 gruppi di 5 parole
propri e < 55% in comune con la più simile, escludendo le frasi di modello (presenti in ≥ 5% delle pagine). Oggi: 6 cifre 835 sì / 177 no,
4 cifre 74/234 (quasi tutti senza descrizione ufficiale), 3 cifre 55/41, settori 18/2.
**Codici cercati (revisione del 13/11):** una pagina a 6 cifre corta ma con domanda dimostrata resta indicizzata con soglie più basse (≥ 60 gruppi propri, < 65% in comune). «Domanda dimostrata» = il codice è scritto per numero in un suggerimento salvato (`domanda.json`) oppure è in `dati/richieste.json` con il suggerimento che lo giustifica (genera e verifica controllano che il suggerimento esista e che le sue parole siano nei testi ufficiali del codice). Oggi 25 pagine: 812113 nail salon, 811192 car wash, 524210 insurance agency, 484110 trucking, 541213 tax preparation, 541519, 541618, 531311/531312 property management, 541120 notary… Per aggiungerne una: riga in `richieste.json`.
**Rimandi in arrivo:** ogni pagina a 6 cifre mostra anche i rimandi ufficiali di altri codici che la citano («What other industries send to …»); il blocco è marcato `data-ripreso` e non conta come testo proprio nella misura. Le indicizzate tra 120 e 150 hanno mediana 540 parole.

**SIC:** l'unica concordanza ufficiale è SIC 1987 ↔ NAICS 1997. Per il 2022 si seguono le concordanze ufficiali passo per passo. «Diretto»
(702 industrie con SIC: stesso codice e contenuto dal 1997) = riga ufficiale tale e quale; 306 «via catena» = derivazione nostra, detta in pagina («There is no official SIC line for …»). Nelle pagine via catena i SIC sono divisi in due: **principali** (il codice del 1997 è finito tutto in questo codice 2022, oppure aveva lo stesso titolo: 200 pagine) e **parziali**, chiusi in un riquadro con la spiegazione; 106 pagine hanno solo parziali e lo dicono nel titolo («partial match» o «no single equivalent», es. 425120 con 71 righe). La scheda in alto e la tabella SIC → NAICS seguono la stessa regola (prima il codice 2022 con lo stesso titolo del 1997). 4 industrie senza SIC (112130, 481219, 541120, 551114). `naics.json` ha anche `titoli_1997`.

**FAQ:** 20 (aggiunta ecommerce / 454110 nella pagina 2017 → 2022, solo dalla concordanza e dall'indice), ognuna da un suggerimento vero (`dati/domanda.json`, 151 radici gl=us, 13/11/2026), risposte solo da manuale, IRS o dati.
SBA: solo la frase del manuale («NAICS categories do not distinguish between small and large business… SBA develops size standards»),
nessuna soglia. Nessuna conseguenza fiscale: solo dove va il codice nello Schedule C (riga B).

**Volumi:** (superato dalla misura del 13/11 sera, sotto) `api.seodata.dev` il 13/11/2026 mattina rispondeva 429 (quota esaurita, con e senza chiave): 0 ricerche usate. Volumi in `dati/volumi.json`
dal file dei fronti (12/11). Pagine attività solo con volume misurato: consulting 3.600, construction 3.600 + general contractor 1.900, cleaning
services 1.300. Da misurare (autocompletamento le mostra): real estate, restaurant, rental property, holding company, trucking, ecommerce…
Per aggiungerne una: volume in `volumi.json`, voce in `dati/attivita.json`, FAQ in `dati/faq.json`, genera e verifica.

## Controlli (`python3 naics/verifica.py --browser`, 13/11/2026: 0 errori)
Aggiunti dalla revisione indipendente: catena SIC rifatta dai file grezzi per tutti i 1.012 codici (serve `xlrd`) e presentazione principali/parziali; modulo senza dati personali e testo della privacy coerente; codici con domanda dimostrata e soglie basse; peso compresso dei due JSON; le voci dell'indice non si scaricano per una ricerca numerica; tabelle non più larghe dello schermo a 375 px; invio del modulo.
Fonti e frasi; dati riletti con un lettore xlsx proprio (codici, titoli, albero, conteggi, 50 codici a caso contro descrizioni, esempi,
indice, 2017, SIC e pagina); 2.125 codici nella loro pagina/ancora; 20.373 voci dell'indice nelle pagine; tabelle complete; titoli ≤ 65 unici,
descrizioni ≤ 160; canonical = sitemap; noindex senza pubblicità; link e ancore; FAQ JSON-LD = testo visibile; indicizzazione ricalcolata;
testi (niente IA, dati personali, chiavi, consigli, SBA/fisco); monetizzazione; Playwright 375/1280 chiaro/scuro su home, 541511, 5415,
SIC e 2017 (richieste esterne bloccate, 8 ricerche, filtri, tema, niente scorrimento orizzontale né errori JS).

## Aggiornamento (ogni mese)
```
pip install xlrd   # se manca (concordanze .xls)
python3 -I naics/raccolta/fonti.py --rete && python3 -I naics/raccolta/estrai.py
python3 naics/genera.py && python3 naics/verifica.py --browser
```
NAICS 2027: quando il Census pubblica i file, nuovi URL in `fonti.py`, concordanza 2027↔2022 nella catena.

## Monetizzazione
AdSense come gli altri: `naics` in `SITI` di monetizzazione.py e in `adsense_siti`/`_siti_della_rete`; ads.txt; script solo nelle pagine
indicizzate con ≥ 400 parole. **Nessun affiliato.** Possibili: formazione LLC / registered agent (CPC «llc cost» 13 $ dal file dei fronti);
nessuna commissione letta oggi.

## Da fare per pubblicare (Massimiliano)
1. Netlify: Import da GitHub, branch `ccr-b7fd6b9e-n096cr`, Base directory `naics/sito`, Build command vuoto, Publish `.`; nome `naics-code-lookup`.
2. Netlify → Forms: rilevamento acceso (modulo `corrections`), notifica email.
3. Search Console: proprietà `https://naics-code-lookup.netlify.app/`, inviare `sitemap.xml`.
4. Poi togliere l'host da `NON_ONLINE` in `studio-business/strumenti/indexnow.py` e lanciare l'invio.

## Pagine «NAICS code for …» (13/11/2026 sera, NON pubblicato: revisione indipendente, poi pubblicazione 14/11)
**Misura.** 252 ricerche `api.seodata.dev` (US) il 13/11: 125 attività × «naics code for X» e «X naics code» + 2 frasi delle FAQ esistenti, in
`dati/volumi-attivita-2026-11-13.json` (volume, cpc, data del dato nello strumento, frasi simili con volume; 404 = frase non nel database). 82
attività ≥ 100/mese. Le due forme sono varianti vicine con lo stesso volume: **volume di una pagina = la frase più cercata, non la somma**
(`volume()` in genera e verifica). Soglia `MIN_VOLUME_ATTIVITA = 100`; tetto ~40 pagine → attività vicine riunite in una pagina (es. restaurant +
bar + coffee shop + bakery; rental property + Airbnb + short-term rental; hair/beauty/nail salon + barber; HVAC + plumbing; logistics + freight
broker + courier). Pagine (volume): restaurant 3.600, consulting 3.600, construction 3.600, real estate 2.400, trucking 1.600, landscaping 1.600,
cleaning 1.300, transportation 1.300, nonprofit 1.300, ecommerce 1.300, real estate investment 1.000, HVAC 1.000, church 1.000, rental property 880,
handyman 880, hair salon 880, staffing 880, manufacturing 880, food truck 720, property management 720, roofing 720, event planning 720, software 720,
marketing 720, hotel 720, holding company 590, electrician 590, home health care 590, daycare 590, retail store 590, logistics 480, photography 480,
law firm 480, insurance agency 480, engineering 480, auto repair 480, rideshare/delivery drivers 390, physical therapy 390, gym 320, accounting 320.
Misurate ≥ 100 ma senza pagina (tetto): pest control, pressure washing (FAQ nella pagina cleaning), interior design, bakery (nella pagina restaurant),
moving (nella pagina trucking), dental office, medical billing, life coach, investment, tutoring, credit repair, content creator, medical office, education.
**Contenuto.** Dati in `dati/attivita.json` (regex sull'indice ufficiale, `prefissi` dei codici ammessi, `evidenza`, `scelte` = voci dell'indice
scelte a mano, `citazioni` = paragrafi di descrizioni ufficiali, `settore`). Ogni pagina: introduzione nostra (titoli ufficiali solo da segnaposto),
tabella «Which code» (voci dell'indice citate parola per parola → codice), descrizioni ufficiali, «codes to look at first», tutte le voci che
corrispondono per codice, FAQ (solo da frasi con volume misurato, anche le «simili»; JSON-LD = testo visibile). Settori (23, 31-33, 44-45, 48-49):
tutti i codici a 6 cifre con la prima voce dell'indice se ≤ 40, altrimenti 2 esempi per sottosettore. Nessun nome di piattaforma nell'indice
(Amazon, Uber, DoorDash, Airbnb): la pagina lo dice e dà il codice del servizio. Le FAQ esistenti delle tre pagine vecchie ora citano frasi misurate.
**Regola dei codici (genera si ferma, verifica ricontrolla):** ogni codice a 6 cifre mostrato (link o numero) ha nella pagina almeno una voce
`<q class="vi" data-c=…>` dell'indice; verifica rilegge la struttura 2022 e il file grezzo dell'indice e delle descrizioni con il suo lettore xlsx;
unico numero ammesso fuori struttura: codici 2017 soppressi con link alla tabella 2017 → 2022 (454110). Prova di manomissione fatta: errori trovati.
**Link:** indice `/naics-code-for/` (menu «By activity», home con le 7 più cercate, sitemap), breadcrumb, blocco «Guides by activity» nelle pagine
dei codici in evidenza e dei 4 settori (in `<section data-ripreso>`: non conta nella misura del testo proprio delle pagine di codice, invariata 982/1.436).
**Indicizzazione:** stessa regola delle pagine di codice (≥ 120 gruppi di 5 parole che non sono in nessun'altra pagina, < 55% in comune con la più
simile; modello = frasi in ≥ 5% delle pagine di codice o ≥ 25% delle pagine attività). Le voci e descrizioni citate sono anche nelle pagine dei
codici e contano come testo in comune. Una pagina attività sotto soglia diventa noindex, fuori sitemap, senza pubblicità. Oggi tutte e 40 passano
(minimo 233 gruppi propri, law firm; massimo 32% in comune, rideshare ↔ logistics). Attenzione: i gruppi propri comprendono anche gli accostamenti di
voci ufficiali diverse nella stessa riga; se una revisione li giudica poco, alzare la soglia per le sole pagine attività.
**Controlli** (`verifica.py --browser`, 13/11 sera: 0 errori, 0 avvisi; `monetizzazione.py verifica naics`: 0 errori): nuova sezione 6b (voci e codici
sui file grezzi, descrizioni citate, tabella delle scelte = evidenza, link di ritorno, indice delle guide, sitemap, testo proprio ricalcolato); FAQ
attività solo da ricerche misurate; pagina solo con volume ≥ 100; controllo fisco/SBA sulle pagine attività solo sul testo nostro (le citazioni
ufficiali sono controllate parola per parola: es. «deductions» nella descrizione ufficiale di 541214); Playwright anche su /naics-code-for/,
restaurant e manufacturing. Il controllo della chiave ora è scritto in modo che nemmeno il .pyc contenga il prefisso.

**Revisione indipendente (13/11 sera, dopo la costruzione).** File ufficiali riscaricati dal Census (indice, descrizioni, struttura, concordanza 2017→2022; impronte = fonti.json) e letti con un lettore proprio: 2.608 voci citate in 40 pagine + indice, 0 differenze (solo spazi finali nel file ufficiale); titoli, 217 descrizioni citate e conteggi delle tabelle = file; 454110 → 42 codici 2022 confermato; esempio 531210 nelle istruzioni Schedule C confermato. Corretti: introduzione restaurant («most are in 7225» falso: 29 voci su 81); frasi assolute sulle aziende («never names a company» → nessuna voce nomina Uber, Lyft, DoorDash, Amazon: cercato nel file); FAQ trucking (owner-operator: ora solo la voce e la descrizione del 484, nessuna deduzione nostra); 4 FAQ riscritte perché la domanda corrisponda alla ricerca misurata (electrical contractor, roofing contractor, religious organizations, transportation services); voci «online» di ecommerce descritte per quello che sono. **Regola più severa per le pagine attività:** le voci citate spezzano il testo (gli accostamenti di voci non contano più come testo proprio; minimo ora 145 gruppi, engineering/law firm) e testo in comune < 40% (`MAX_SOVRAPPOSIZIONE_ATTIVITA`): manufacturing (50% in comune con /31-33/, esempi alfabetici poco utili) diventa noindex, fuori sitemap, senza pubblicità. 39 indicizzate.

## «LLC by State» + riquadro dei partner (14/11/2026, NON pubblicato: serve la revisione indipendente)
Idea n. 2 di `studio-business/intelaiatura/fronti-2026-11-14-pagatori-prima.md`.
**Pagine nuove (9):** `/llc/` (tabella degli Stati, Stati non coperti, 4 FAQ) e `/llc/<stato>/` per Texas, Florida, California, New York, North Carolina, Michigan, Colorado, Arizona. Voce di menu «LLC by state», link nel piè di pagina e nella home.
**Stati esclusi: Georgia e Ohio.** `sos.ga.gov` (tariffe, guide, eCorp) e `ohiosos.gov` (pagine e PDF) rispondono 403 dal nostro server: non aggirati, nessuna cifra presa altrove (`esclusi` in `dati/llc-stati.json`; la pagina /llc/ lo dice). Leggibili ma non usati perché non sono la Segreteria di Stato: `georgia.gov/register-llc` e `codes.ohio.gov` (ORC 111.16): decisione da prendere in revisione.
**Dati.** `dati/llc-stati.json` (a mano): per Stato i fatti `filing`, `annual`, `tax`, `extra` (pubblicazione NY e AZ), `processing`, `agent`, ognuno con valore, nota nostra e le frasi ufficiali citate parola per parola (70 frasi, 28 pagine ufficiali: Secretary of State o ufficio equivalente, Comptroller del Texas, FTB della California, Tax Department di New York). `raccolta/llc.py` scarica le pagine in `raccolta/_grezzi/llc/` (fuori da git), ritrova ogni frase e scrive `dati/llc-fonti.json` (HTTP, byte, data, frase per frase). Confronto senza spazi (le righe di tabella sono citate cella per cella), PDF con `pdftotext -layout`.
**Regole (genera si ferma, verifica ricontrolla con un lettore suo):** ogni frase citata è nel file grezzo e nella pagina con il link alla fonte e la data; ogni cifra scritta da noi (valore, nota, introduzione, FAQ) è in una frase citata dello stesso Stato (prova di manomissione: 300 → 310, fermato); pagina solo con ≥ 100 ricerche misurate; nessun nome degli Stati esclusi; «information, not legal advice» e disclaimer proprio (`DISCLAIMER_LLC`); testo in comune tra due Stati al massimo 37% (soglia 55%); fonti più vecchie di 45 giorni = avviso. Dove la pagina ufficiale non dà un dato (tassa statale separata, tempi normali) la pagina scrive «not on the pages we read», non una cifra. Texas: la pagina dei tempi di lavorazione risponde 403, quindi nessun tempo.
**Cifre lette (14/11/2026):** TX 300 $ (Form 205 rev. 09/26), nessun rapporto alla Segreteria, franchise tax entro il 15 maggio, soglia 2.650.000 $ per 2026-2027 · FL 125 $ (100 + 25), rapporto annuale 138,75 $ dal 1/1 al 1/5, mora 400 $ · CA 70 $, Statement of Information 20 $ entro 90 giorni e ogni due anni, tassa annuale FTB 800 $ · NY 200 $, pubblicazione su due giornali per sei settimane + certificato 50 $ entro 120 giorni, Biennial Statement 9 $, IT-204-LL da 25 $ · NC 125 $, rapporto annuale 200 $ (203 online) entro il 15 aprile · MI 50 $, Annual Statement 25 $ entro il 15 febbraio · CO 50 $, Periodic Report 25 $ (mora 50 $), deposito online in tempo reale · AZ 50 $ (85 accelerato), nessun rapporto annuale per le LLC, 14-16 giorni (3-5 accelerato).
**Domanda misurata** (`raccolta/volumi_llc.py`, 93 ricerche seodata il 14/11, `dati/volumi-llc-2026-11-14.json`; chiave letta solo dentro curl). «<Stato> llc»: TX 18.100, FL 18.100, CA 12.100, MI 6.600, NY 5.400, NC 5.400, AZ 5.400, CO 2.400 (CPC 22-48 $). «how to start an llc in <Stato>»: TX 12.100, FL 8.100, CA 8.100, NC 3.600, MI 3.600, AZ 3.600, NY 2.900, CO 1.900. «<Stato> registered agent»: TX 9.900, FL 9.900, CA 3.600, NC 2.400, CO 1.900, NY 1.600, MI 1.600, AZ 880. Altre: texas franchise tax 14.800, florida annual report 6.600, california statement of information 5.400, california llc fee 2.900, new york biennial statement 2.400, florida llc annual report 1.900, texas llc filing fee 1.900, nc llc annual report 1.300, colorado periodic report 1.300, llc filing fees by state 1.000, naics code for llc 480, what is a registered agent 4.400. Senza volume: «how long does it take to get an llc in <Stato>» (8 su 8). Titoli («<Stato> LLC Cost: Filing Fee, Annual Report, Registered Agent») e 37 FAQ solo da frasi con volume (in `llc-stati.json`; quella sul codice NAICS di una LLC in `faq.json`, pagina `llc`).
**Riquadro dei partner «Starting this business?»: SPENTO.** `dati/affiliati.json` (`avvio.attivo` false; ZenBusiness, Northwest Registered Agent, Tailor Brands tutti false, link segnaposto `.invalid`). Spento = nessun riquadro, nessun nome, nessun link in nessuna pagina (verifica lo controlla). Nessuna iscrizione fatta e nessun link di affiliazione esiste: non inventarne. Per accenderlo: link tracciato vero in `link`, dominio in `monetizzazione.json` (awin1.com c'è già; un programma diretto va aggiunto), `attivo` true sul partner e su `avvio`, genera e verifica. Esce nelle 40 pagine attività, nelle pagine dei codici indicati dalle guide e nelle 9 pagine LLC (218 pagine nella prova locale), con «Advertisement · affiliate links», `rel="sponsored nofollow noopener"`, riga di trasparenza; privacy e about cambiano da soli. Il testo non descrive i servizi dei partner (non letti né provati). Prova locale con un link di prova fatta e tolta: verifica e monetizzazione 0 errori da acceso e da spento.
Sempre presente (anche da spento), nelle stesse pagine attività e di codice: blocco interno «Forming an LLC for this business?» con il link a `/llc/` (in `<section data-ripreso>`: non conta nel testo proprio; indicizzazione invariata 982/1.436 e 39 attività).
**Controlli (14/11):** `python3 naics/verifica.py --browser` 0 errori, 0 avvisi (nuova sezione 6c; Playwright 375/1280 chiaro/scuro anche su /llc/, /llc/texas/, /llc/new-york/, /llc/michigan/: niente scorrimento orizzontale, tabelle dentro lo schermo); `monetizzazione.py verifica naics` 0 errori. 1.037 pagine in sitemap (erano 1.028). Il CSS e il menu sono cambiati: tutte le pagine di `sito/` risultano modificate.
**Aggiornamento mensile:** `python3 -I naics/raccolta/llc.py --rete` prima di genera; una frase non ritrovata = rileggere la pagina e riscrivere il fatto (mai correggere la cifra a mano), oppure togliere lo Stato.
**Da fare:** revisione indipendente di tutte le cifre contro le pagine statali; iscrizione a ZenBusiness su Awin e a Northwest (li fa l'editore); se arrivano impressioni in 60 giorni, altri Stati (per Georgia e Ohio serve una fonte ufficiale leggibile).
**Revisione indipendente (14/11/2026):** 28 pagine ufficiali riscaricate e 70 frasi ritrovate con un lettore diverso; tutte le cifre delle 9 pagine confermate (nessuna correzione ai dati). Corretto in `stile.py`: con la sesta voce di menu la barra usciva dallo schermo tra 901 e ~935 px (scorrimento orizzontale su tutte le pagine) → il menu a comparsa ora parte da 1.000 px; a 320 px l'intestazione usciva di 5 px (già prima) → logo più piccolo sotto 340 px. Riquadro dei partner provato acceso con un link di prova e rimesso spento (`affiliati.json` identico). Nota: le righe del PDF del Michigan sono citate senza i puntini di guida della tabella.
