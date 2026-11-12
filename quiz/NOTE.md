# Quiz Ufficiali – note di lavoro (12/11/2026)

Sito statico in italiano: le banche ufficiali dei quiz d'esame pubblicate da Ministero, Regioni e Camere di Commercio, una pagina per banca
con tutte le domande, la risposta esatta indicata dall'ente, la pagina del PDF e un simulatore gratuito nel browser.
Nato dal fronte `studio-business/intelaiatura/fronti-2026-11-12-quiz-ufficiali.md` (idea «un motore + collana KDP», voto 6,5,
600 / 6.000 / 35.000 €/anno) e dall'idea taxi/NCC di `fronti-2026-11-12-siti-in-vendita.md` (sez. 4.1), costruito con il via libera
permanente di Massimiliano (REGOLE-FISSE, 12/11/2026). Indirizzo di lavoro `https://quiz-ufficiali.netlify.app` (costante `URL_SITO`
in `genera.py` e in `verifica.py`, da cambiare insieme). Il 12/11/2026 il nome Netlify `quiz-ufficiali` era libero (curl: 404).
**Il sito Netlify non esiste ancora**: i passi sono in fondo.

**Priorità (12/11/2026 sera, volumi misurati in `studio-business/intelaiatura/volumi-2026-11-12.md`):** patente nautica circa 5.650 ricerche
di quiz al mese, fitosanitario circa 1.060, tartufi circa 300, ruolo conducenti nessun dato. Per questo la **patente nautica è il modulo
principale** (primo nel menu e in home); fitosanitario resta; ruolo conducenti solo per le province già lette; tartufi solo il Lazio, già fatto.

Nome: «Quiz Ufficiali» è descrittivo; ricerca del 12/11/2026 senza siti o marchi con questo nome. Ogni pagina dice «Sito indipendente…
non affiliato a nessun ente». Se si cambia nome: `NOME`, il logo in `pagina()`, `grafica/og.html` (poi `python3 quiz/grafica/og.py`).

## Regole del sito
- Online solo le banche **con la chiave ufficiale** delle risposte. Le altre sono elencate nella pagina del modulo come
  «domande senza risposte ufficiali» o «non ancora online», con il link al PDF e il motivo, senza simulatore.
- Testo di domande e risposte uguale al PDF (tolti solo a capo e spazi doppi; refusi compresi). Nessuna spiegazione: i documenti
  di oggi non ne hanno, quindi il sito mostra solo la risposta ufficiale e la pagina del PDF.
- Regole della prova (numero di domande, tempo, errori o soglia) solo da frasi lette nei documenti degli enti (`dati/fonti.json`,
  campo `frasi`, ricontrollate da `verifica.py`). Dove l'ente non scrive un numero, la pagina lo dice e il simulatore fa un'esercitazione.
- Nessuna immagine riprodotta (niente carte, foto, mappe mute), nessuna dispensa di autori privati, nessuna funzione a pagamento.

## Base del riuso
Art. 5 della legge 633/1941: «Le disposizioni di questa legge non si applicano ai testi degli atti ufficiali dello Stato e delle
amministrazioni pubbliche». Le banche online sono atti o documenti pubblicati dagli enti stessi: allegato a una determinazione (Lazio),
elenco «adottato dalla Regione» (Valle d'Aosta), elenchi del Servizio fitosanitario regionale (Sicilia), banche dati e schede corrette
delle commissioni camerali (Palermo ed Enna, Sassari, Cagliari-Oristano). Escluse per prudenza: la guida della Provincia di Caserta (2008)
e gli «Esempi di quiz» dell'Emilia-Romagna (nessuna chiave in ogni caso).

## Banche online (12/11/2026)
| Pagina | Documento (ente, data) | Domande | Chiave | Simulatore |
|---|---|---|---|---|
| `/patente-nautica/quiz-base/` | Ministero delle infrastrutture e dei trasporti, allegato A al decreto direttoriale 131 del 31/05/2022 (elenco unico nazionale; sostituisce l'allegato del DD 106/2022), quiz base: 1.472 nel PDF | 1.350 (122 fuori: 118 con figura, 3 con la colonna V/F illeggibile, 1 con due V) | colonna V/F accanto a ogni risposta | 20 domande, 30 min, max 4 errori (regole scritte nell'allegato) |
| `/patente-nautica/quiz-vela/` | stesso allegato, quiz vela: 250 affermazioni VERO/FALSO | 246 (3 con figura, 1 senza V) | colonna V/F | 5 domande, 15 min, almeno 4 esatte |
| `/tartufi/lazio/` | Regione Lazio, allegato alla determinazione G10268 del 27/08/2015 (275 quesiti); identico, chiave compresa, nella guida regionale 2021 | 275 | evidenziato in giallo | 25 domande, max 8 errori (pagina regionale attuale) |
| `/patentino-fitosanitario/valle-d-aosta/` | Regione Valle d'Aosta, quesiti adottati (DGR 1930/2015), file del 2022 | 174 | giallo («Le risposte corrette sono evidenziate in giallo») | esercitazione da 20, solo punteggio (numero e soglia non scritti nella DGR) |
| `/patentino-fitosanitario/sicilia-utilizzatori/` | Regione Siciliana, elenco domande utilizzatori (file 2016) | 199 (+1 esclusa) | ✓ e tabella finale | 25 domande, 60 min, max 5 errori |
| `/patentino-fitosanitario/sicilia-consulenti/` | Regione Siciliana, elenco domande consulenti (file 2021) | 278 (+2 escluse) | asterisco e tabella finale | 30 domande, 90 min, max 5 errori |
| `/ruolo-conducenti/palermo-enna/` | CCIAA Palermo ed Enna, 35 «Questionari corretti» delle sedute 31/03/2021-22/05/2026 | 482 (726 lette: 243 doppie, 1 nulla) | [*] | 20 domande, 20 min, max 2 errori (regolamento in vigore dal 25/03/2026) |
| `/ruolo-conducenti/sassari/` | CCIAA Sassari, banca dati quiz aggiornata al 04/04/2022 | 400 | colonna «Esatta» | 40 domande, 80 min, 70 %; lingua straniera a scelta (DGR Sardegna 12/30 del 2012) |
| `/ruolo-conducenti/cagliari-oristano/` | CCIAA Cagliari-Oristano, banca dati quiz aggiornata al 29/01/2025 | 476 | [*] | esercitazione da 30 con soglia 70 % (numero di domande non scritto); scelta di lingua e città |

Totale 3.880 domande. Pagine: home, 4 moduli, 9 banche, come lavoriamo, chi siamo, privacy (17 indicizzate) + 404.

**Escluse dal simulatore, con il motivo scritto nel sito:** domande dove le due chiavi ufficiali dello stesso PDF non coincidono
(Sicilia utilizzatori n. 199: ✓ su a, tabella c; consulenti n. 204: asterisco sulla terza risposta, che nel PDF ha di nuovo la lettera «b.»,
tabella b; n. 225: asterisco b, tabella c); Palermo: 1 domanda «Domanda nulla» (seduta 28/02/2024). Irregolarità lette a mano e dichiarate
nella pagina: Sicilia utilizzatori n. 85 (la terza risposta non ha la lettera «c)»); Cagliari-Oristano, «Riferimenti regionali e locali»
n. 23 (terza risposta stampata «D»). Le doppie di Palermo hanno sempre la stessa chiave (controllato: altrimenti `estrai.py` si ferma).

**Patente nautica, scelte.** Fonte: pagina «Patenti nautiche: normativa» del Ministero (decreti 10/2022, 106/2022, 131/2022 sui quesiti A;
62/2025 sulla patente D1; 31/2026, 199/2026, 167/2026 su D1 e altri temi; nessuno successivo sostituisce l'allegato A del 131/2022).
Fuori: quiz su elementi di carteggio e prova di carteggio (si fanno sulle carte 5/D e 42/D dell'Istituto Idrografico; le figure e le carte non
si riproducono), le 121 domande che rimandano a una figura (colonna IMMAGINE piena o testo con «figura», «disegno», «freccia»…), le righe
con la chiave illeggibile o non univoca (quiz base n. 8, 71, 226, 692; vela n. 49). L'elenco ripete una domanda (quiz base n. 1148 e 1214,
stessa chiave): restano tutte e due, come nel documento. Il simulatore estrae 20 domande dalle sole domande di testo (all'esame possono uscire
anche quelle con figura: la pagina lo dice). Il server di `mit.gov.it` non invia il certificato intermedio della sua catena TLS: `fonti.py`
lo aggiunge da `raccolta/certificati/` (scaricato dall'indirizzo Authority Information Access del certificato, come fanno i browser; la
verifica resta completa). La patente D1 (decreto 62/2025, elenco proprio) non è ancora caricata.

**Non online:** tartufi Emilia-Romagna («Esempi di quiz», senza chiave), Toscana (decreto 5332/2017: gli allegati A domande e B risposte
oggi danno 404; il decreto ne riporta le impronte SHA-256 `121359f4…` e `41dd87b9…`, utili se ricompaiono), Campania/Caserta (guida 2008
senza chiave); fitosanitario Sardegna-vendita (ASL Oristano, «Elenco domande e soluzioni» senza soluzioni segnate), Umbria (server
`regione.umbria.it`: connessione chiusa il 12/11/2026); taxi Roma (server `static.cittametropolitanaroma.it`: il proxy risponde 502,
l'host non è raggiungibile da qui il 12/11/2026). Altre banche trovate e non ancora caricate: Nuoro (CCIAA, «Lista domande quiz ruolo
conducenti dic 24», 54 pagine, risposta segnata con X: regole d'esame non trovate), Toscana taxi (esempi di quiz parte normativa e
tecnica con colonna «Esatta»; la parte tecnica usa una carta muta, l'estrazione a tabella spezza alcune celle: serve un lettore apposta),
caccia (Vercelli), gestore dei trasporti e consulente automobilistico (Province).

## Fonti e file
`raccolta/fonti.py` scarica i PDF in `raccolta/_grezzi/` (fuori da git) e scrive `dati/fonti.json`: URL, HTTP, byte, SHA-256, pagine,
data di lettura e frasi controllate (57 file). Non scarica gli elenchi di candidati, convocati o idonei (dati personali).
`raccolta/estrai.py` scrive `dati/banche/<id>.json`: per domanda numero, argomento, testo, tre risposte, indice della risposta esatta,
file e pagina del PDF (Palermo: seduta e altre sedute; Cagliari: numero nella materia; Sassari: riferimento normativo).
Come legge la chiave: patente nautica colonna V/F della tabella (`find_tables`, una riga per domanda, colonne IMMAGINE/DOMANDA/RISPOSTA/V/F/
PROGRESSIVO/CAPITOLO/TEMA/VOCE; le immagini si riconoscono dalla loro posizione nella riga); Lazio e Valle d'Aosta colore dei rettangoli (1,1,0) sotto la riga; Sicilia ✓/asterisco e confronto con la tabella
finale; Palermo e Cagliari `[*]`; Sassari colonna «Esatta» (`extract_tables`). Si ferma se una domanda non ha esattamente una risposta
esatta, se i numeri non sono consecutivi o se la tabella siciliana non torna (oltre 5 differenze).

## Controlli (`python3 quiz/verifica.py --browser`, 12/11/2026: 0 errori, 0 avvisi)
1. Fonti: SHA-256 dei file = `fonti.json`; HTTP 200; tutte le frasi delle regole ritrovate.
2. Banche rilette dai PDF con un lettore separato: Lazio e Valle d'Aosta ritagliando ogni rettangolo giallo e cercando la risposta
   esatta nelle aree della sua domanda (ritrovata dalla riga «a)» in ordine di documento), più nessuna seconda risposta evidenziata;
   righe «a)» contate = domande (275 / 174); Sicilia tabella finale riletta = chiave di ogni domanda, segni ✓/* contati = domande + escluse;
   Palermo e Cagliari `[*]` contati (Palermo: 726 = 482 + 243 doppie + 1 nulla) e risposta esatta ritrovata sulla riga `[*]` del suo file;
   Sassari colonna «Esatta» letta per posizione delle parole (400/400 uguali); patente nautica lettere V/F lette per posizione sotto le
   intestazioni «V/F» di ogni pagina (1.472 + 250 righe numerate trovate; 1.350 + 246 chiavi uguali al JSON; nessuna domanda con «figura»,
   «disegno», «immagine», «freccia»); 50 domande a caso per banca con testo e risposte ritrovati
   nella pagina indicata del PDF.
3. Pagine: titoli ≤ 65 e descrizioni ≤ 160 uniche, un h1, canonical = URL, sitemap = canonical, noindex (solo 404) senza canonical né
   AdSense, link interni e ancore, ogni pagina banca con tutte le domande e la stessa chiave del JSON, GoatCounter, robots, IndexNow,
   netlify.toml con `ignore`, og.png.
4. Testi: nessun nome di modello di IA (escluso il testo ufficiale delle domande: nella banca di Cagliari c'è un vento che ha il nome di un modello),
   nessuna email, il titolare solo nella privacy, nessuna «spiegazione».
5. Monetizzazione: `python3 studio-business/strumenti/monetizzazione.py verifica quiz` (AdSense acceso, ads.txt, privacy, 7 link Amazon
   con tag e riga di trasparenza); Easy-Quizzz spento.
6. Browser (Playwright, ogni richiesta che non è un file del sito bloccata con `page.route`: il simulatore funziona senza rete) su home,
   patente nautica quiz base, Sassari, Sicilia utilizzatori a 375 e 1280 px, chiaro e scuro: niente scorrimento orizzontale, testi ≥ 11 px, sfondo del tema,
   pulsante del tema, nessun errore JS; simulatore: esame completo tutto giusto («Superato», 20/20, 40/40, 25/25) e tutto sbagliato
   («Non superato», 0), nessuna domanda ripetuta, con il francese a Sassari nessuna domanda di altre lingue, ripasso del primo argomento
   con tutte le sue domande. Screenshot in `cache/screenshot/` (fuori da git).

## Aggiornamento (ogni mese, 10 minuti)
```
python3 -I quiz/raccolta/fonti.py --rete     # riscarica tutto; fonti.json dice se un'impronta è cambiata
python3 -I quiz/raccolta/estrai.py
python3 quiz/genera.py                       # aggiornare prima OGGI in genera.py
python3 quiz/verifica.py --browser
python3 studio-business/strumenti/monetizzazione.py verifica quiz
```
`git diff quiz/dati/fonti.json` mostra i file cambiati. Palermo ed Enna pubblica una scheda nuova dopo ogni seduta: aggiungere il percorso
in `PAEN_FILE` di `raccolta/fonti.py` (pagina «Ruolo dei conducenti» della Camera; solo i file «QUIZ CORRETTO», mai convocati o idonei).
Il file `QUIZ CORRETTO.pdf` alla radice del sito camerale è una scansione senza testo: non usato. Se un ente cambia l'indirizzo del PDF,
cambiarlo in `FONTI`. Si pubblica solo se `quiz/sito` cambia (regola `ignore` di Netlify).
Per riprovare le fonti non raggiunte: `curl -sI` sugli URL di `NON_RAGGIUNTE` in `raccolta/fonti.py`; se rispondono, aggiungerle a `FONTI`,
scrivere il lettore in `estrai.py` e il controllo in `verifica.py`, poi la voce in `BANCHE` di `genera.py`.

## Monetizzazione
`quiz` aggiunto a `SITI` in `studio-business/strumenti/monetizzazione.py` e ad `adsense_siti` e `_siti_della_rete` in `monetizzazione.json`;
`ads.txt` scritto da `genera.py`. AdSense solo nelle pagine indicizzate con almeno 400 parole (`MIN_PAROLE_ADSENSE`).
Amazon.it (tag `guideesami-21`, `dati/affiliati.json`): solo nei moduli patente nautica (ricerca libri «quiz patente nautica») e taxi/NCC
(«ruolo conducenti taxi ncc quiz»): pagina del modulo e pagine delle banche, 7 link. Sono gli esami con un suggerimento nell'autocompletamento
libri di Amazon e manuali in commercio (ricerca del 12/11, sez. 4); tartufi e fitosanitario senza link (nessun manuale d'esame verificabile: amazon.it risponde 503 al server). Easy-Quizzz: voce spenta in
`affiliati.json` (nessun link nel repository; programma al 20 %, va acceso solo dove non c'è il nostro simulatore completo).

## Da fare per pubblicare (passi di Massimiliano)
1. Netlify: «Add new site» → «Import an existing project» → GitHub, repository di questo progetto, **branch `ccr-b7fd6b9e-n096cr`**;
   Base directory `quiz/sito`, Build command vuoto, Publish directory `.` (il file `quiz/sito/netlify.toml` lo conferma);
   nome del sito `quiz-ufficiali` (se diverso, cambiare `URL_SITO` in `quiz/genera.py` e `quiz/verifica.py` e rigenerare).
2. Netlify → Forms: lasciare acceso il rilevamento dei moduli (modulo `segnalazioni`) e impostare la notifica email.
3. Search Console: proprietà `https://quiz-ufficiali.netlify.app/` (meta di verifica dell'account già nelle pagine), inviare `sitemap.xml`.
4. Dopo la pubblicazione: aggiungere l'host a `SITI` in `studio-business/strumenti/indexnow.py` (cartella `quiz`) e lanciare l'invio.

## Dubbi per il revisore indipendente
0. Patente nautica: l'allegato A del DD 131/2022 è ancora l'elenco in uso? La pagina «normativa» del Ministero non elenca decreti successivi
   sui quesiti A; la circolare del 13/05/2022 dice che il software d'esame usa il data base pubblicato. Le domande con figura (121) restano fuori:
   il simulatore non le propone, ma all'esame possono uscire. Il quiz base è uguale per entro 12 miglia e senza limiti (cambia la prima fase).
1. Palermo ed Enna: le schede corrette sono le domande uscite alle sedute, non l'intera banca ARCA (non pubblicata). Il sito lo dice;
   va bene come «banca» o è meglio chiamarla «domande delle sedute»?
2. Lazio: la determinazione 2015 diceva 20 quesiti (orale con più di 8 errori); la pagina regionale attuale dice 25 domande e «9 o più
   errori» = non superato. Il simulatore segue la pagina attuale.
3. Valle d'Aosta e Cagliari-Oristano: numero di domande della prova non trovato nei documenti; il simulatore fa un'esercitazione
   (20 e 30) e lo dice. Cercare l'avviso d'esame della CCIAA di Cagliari-Oristano e la determina di nomina della commissione valdostana.
4. Sicilia utilizzatori: file del 2016 con termini precedenti al PAN («autorizzazione», «patentino»): è ancora l'elenco in uso? La pagina
   regionale che lo pubblica non è stata letta (link diretto al file).
5. Argomenti del Lazio: il PDF titola solo «Conoscenza delle specie»; biologia e normativa sono assegnate per numero (65-129, 130-275)
   secondo i conteggi della determinazione (controllato a campione sulle domande 64/65 e 129/130).
6. Sassari: le categorie A-G non hanno un nome nel PDF; il sito mostra «Categoria A…» e la G divisa per lingua dalla colonna riferimento.
7. Riuso: le schede corrette camerali e le banche dati ARCA sono documenti della commissione d'esame; trattate come atti della PA (art. 5).
