# Paga CCNL – note di lavoro (12/11/2026)

Sito statico in italiano: minimo mensile, paga oraria e giornaliera, part time e aumenti già firmati per contratto × livello.
Nato dalla verifica dati CCNL del 12/11/2026 (`studio-business/intelaiatura/fronti-2026-11-12-radar-settori-diversi.md`, ultima sezione).
Indirizzo `https://pagaccnl.com` (costante `URL_SITO` in `genera.py`, unico punto da cambiare): pubblicato il 13/11/2026 sul dominio proprio,
con rinvio 301 dal vecchio indirizzo netlify.app (commit della pubblicazione). La sezione «Da fare per pubblicare» in fondo è storica.

## Pagine (63 indicizzabili + 404)

| Pagina | Contenuto |
|---|---|
| `/` | ricerca nella tabella di tutti i 53 livelli (minimo, paga oraria, data), metodo, 4 FAQ |
| `/<contratto>/` (5) | cifre chiave, tabella dei livelli, calendario degli aumenti, regole usate (divisori, mensilità, orario con articolo), cifre escluse con motivo, FAQ, documenti ufficiali |
| `/<contratto>/<livello>/` (53) | minimo con le sue voci e il controllo fatto, paga oraria e giornaliera con formula e articolo, calcolo per ore settimanali (solo lordo), tabella 20/24/30/tempo pieno, minimo annuo con le mensilità, aumenti futuri, minimi precedenti, livelli vicini, declaratoria citata dal contratto (domestico, commercio, metalmeccanici), FAQ dove esiste una ricerca vera, fonti numerate, «Controllato il» |
| `/colf-badanti/` | guida per le famiglie: livello, convivente o a ore, tabella B, vitto e alloggio (tabella F con controllo della somma), notturno (D, E), sostituzioni (G), indennità (H, I, L), tredicesima, aumenti 2027-2028, calcolo a ore, 4 FAQ |
| `/come-lavoriamo/`, `/chi-siamo/`, `/privacy/`, `404.html` | metodo, elenco dei 19 documenti con impronta, cifre escluse, modulo «segnala un errore» (Netlify Forms, email facoltativa, consenso) |

Pagine livello per contratto: lavoro domestico 8 (A, AS, B, BS, C, CS, D, DS), commercio 8 (Quadro, 1°-7°), metalmeccanici 9 (D1-A1),
multiservizi 8 (1°-7°, Quadro), logistica 20 (non viaggiante Q, 1, 2, 3S, 3, 4, 4J, 5, 6; viaggiante C3, B3, A3, E2, D2; driver e rider H1, G1,
I primi 6 mesi, I, L 7-15 mesi, L).

## Fonti e regola di qualità

Una cifra si pubblica solo se (1) le voci stampate sommano al totale stampato e (2) una seconda fonte indipendente riporta lo stesso importo al
centesimo. `raccolta/estrai.py` scrive tutto in `dati/contratti.json` (anche le righe escluse, con il motivo); `verifica.py` rifà somma e confronto da zero.

| Contratto | Fonte A | Fonte B | Regole (frase controllata nel testo) |
|---|---|---|---|
| Lavoro domestico (H501) | tabella 2026 del Ministero (`min_domestico_2026`) | stessa tabella depositata al CNEL con il verbale 11/2/2026 (accordo 245798) | CCNL 28/10/2025 (245143): 1/26 giornaliero, 13 mensilità art. 39, 54/40 ore art. 14, aumenti art. 55 |
| Terziario Confcommercio (H011) | testo unico 3/2/2026 (246574), pagine 363-364 lette con OCR (cifre in caratteri codificati) | tabelle dei minimi di Filcams CGIL (pagina web) | art. 215 divisore 168 (182/195), art. 214 divisore 26, artt. 224-225, art. 133 (40 ore) |
| Metalmeccanici (C011) | tabelle impiegati/operai del decreto n. 94 del 26/10/2026 (annuo ÷ 12, divisione esatta) | ipotesi di accordo 22/11/2025, pag. 2 (Federmeccanica, scansione con OCR) | CCNL 5/2/2021 (157071): divisore 173 (Sez. IV Tit. IV artt. 3 e 5), tredicesima (art. 7), 40 ore |
| Multiservizi (K511) | tabelle del decreto n. 25 del 30/3/2026, pagine «NAZIONALE» (annuo ÷ 12), 8 date fino a marzo 2029 | accordo integrativo 6/8/2025 (234752, scansione con OCR + 32 correzioni in `dati/correzioni_ocr.json`) | CCNL 31/5/2011 (105782): art. 19 divisore 173 e 22/26, artt. 20-21, art. 30 (40 ore). Controllo in più: aumento stampato = differenza tra due date |
| Logistica (I100) | testo 25/9/2025 (223634), tabella minimi + EPA | decreto n. 135 del 19/12/2025 (annuo ÷ 12) | art. 61 c. 3 divisori 168 / 22 / 26, artt. 18-19, artt. 9 e 11 (39 ore) |

Tutte le fonti sono lette da `raccolta/fonti.py` (HTTP, byte, SHA-256, pagine, frasi) in `dati/fonti.json`; i file grezzi stanno in
`raccolta/_grezzi/` (fuori da git, ~35 MB, si riscaricano). OCR: tesseract 5, italiano, 300 dpi, `--psm 4`; testo in `_grezzi/ocr/`.
Confcommercio e FIM CISL rispondono 403 al robots: non usati. Federmeccanica: robots permesso, pausa di 3 secondi rispettata.

### Cifre escluse (e perché)
- Logistica F2 (viaggiante), tutte le date: minimo + EPA ≠ totale stampato (6 centesimi; il testo ufficiale è così).
- Logistica non viaggiante dal 1/1/2027 (9 livelli): i totali stampati usano già il minimo di giugno 2027; le voci coincidono col Ministero ma il totale no. La data compare con «—» e una nota; dal 1/6/2027 tutto torna.
- Logistica L primi 6 mesi (parametro 110) dal 2026: il Ministero stampa EPA 120,00 annui (10 al mese) invece di 16,67 al mese: nessuna pagina.
- Metalmeccanici giugno 2027 e 2028: solo nell'accordo (e possono salire con l'IPCA): testo senza cifre fino al decreto del Ministero.
- Multiservizi 2° livello parametro 115 e logistica 6° Junior (solo 2025): nessuna pagina (manca la seconda fonte / non più in tabella).
- Operatori di vendita del commercio: solo nella tabella della pagina contratto (somma e Filcams tornano), senza pagina propria.

## Controlli (`python3 ccnl/verifica.py --browser`, 12/11/2026: 0 errori, 0 avvisi)
1. Fonti: HTTP 200, impronta del file uguale a quella registrata, tutte le frasi trovate; `cnel_monitor.json` presente.
2. Regole: ogni divisore/mensilità/orario ha una frase che è tra quelle controllate e contiene il valore; le citazioni delle declaratorie sono nel testo (o nell'OCR).
3. Cifre: 211 righe livello × data ricalcolate da `estratti.json` (177 pubblicabili, 34 escluse) e confrontate con `contratti.json`; in ogni pagina livello si cercano minimo, paga oraria, giornaliera, annuo, part time 20/24/30/pieno e aumenti futuri; gli attributi del calcolo coincidono con i dati.
4. Pagine: titolo ≤ 65 e descrizione 70-160 caratteri, unici; un h1; canonical; sitemap = canonical; link interni e ancore; risorse; GoatCounter in ogni pagina (404 compresa); robots, chiave IndexNow, netlify.toml, og.png.
5. FAQ: 82 domande (dal 13/11), ogni ricerca è tra i 931 suggerimenti salvati (`dati/domanda.json`, hl=it gl=it) oppure è una frase misurata con almeno 100 ricerche al mese (volume dichiarato = volume nel file); risposta rifatta da `estratti.json` e ritrovata in pagina; citazioni ritrovate nel testo ufficiale; JSON-LD = testo visibile; nessun segnaposto rimasto. Titoli decisi da frasi misurate: vedi la sezione del 13/11.
6. Testi: nessun nome di modello o servizio di IA, nessun dato personale, nessun netto.
7. Monetizzazione: `monetizzazione.controlla_sito` (AdSense acceso, ads.txt, privacy) — anche `python3 studio-business/strumenti/monetizzazione.py verifica ccnl`.
8. JS = Python: il calcolo del browser (interi in centesimi, mezzo verso l'alto) su 1.828 casi.
9. Browser (Playwright, ogni richiesta esterna bloccata con `page.route`): home, commercio 4° livello, domestico CS, contratto logistica, metalmeccanici C2 e guida colf e badanti (dal 13/11) a 375 e 1280 px, chiaro e scuro; niente scorrimento orizzontale, testi ≥ 11 px, sfondo coerente col tema, calcolo a 24 ore, pulsanti delle ore, ricerca della home, pulsante del tema, nessun errore JS. Screenshot in `cache/screenshot/` (fuori da git).

## Aggiornamento
**Ogni mese (1 ora):**
1. `python3 ccnl/raccolta/fonti.py --rete` — riscarica tutto; guardare in `dati/cnel_monitor.json` se per H501, H011, C011, K511, I100 c'è un accordo nuovo (campo `ultimi`, confrontare gli id con la tabella qui sopra) e se un'impronta è cambiata (`git diff ccnl/dati/fonti.json`).
2. Rileggere le pagine di settore del Ministero (metalmeccanico, pulizia e multiservizi, logistica; elenco decreti dell'anno) per decreti nuovi.
3. `python3 ccnl/raccolta/estrai.py && python3 ccnl/genera.py && python3 ccnl/verifica.py --browser`; aggiornare `controllato_il` in `dati/contratti_meta.json`.

**Scadenze note:**
- Gennaio 2027: nuova tabella del lavoro domestico (Ministero + deposito CNEL). **Il sito non si ferma più**: dal 1/1/2027 le pagine del lavoro domestico (livelli, contratto, guida, home) restano sulla tabella 2026 con la nota «Tabella 2026» in alto e la dicitura «con decorrenza» al posto di «in vigore dal»; `genera.py` e `verifica.py` danno un avviso. Da fare appena esce: aggiungere la fonte in `fonti.py` (anno nuovo) e la data in `estrai.py` (`righe_livello`, ramo domestico).
- 1/1/2027 logistica non viaggiante (9 livelli): la riga resta esclusa (il totale stampato nel contratto usa già il minimo di giugno). **Il sito non si ferma più**: le 9 pagine restano sull'ultimo minimo verificato (1/1/2026) con la nota «Cifra da aggiornare» in alto, che riporta le due voci confermate da contratto e Ministero, il totale stampato e la loro somma; titolo di testata «Ultimo minimo verificato», storico «(ultimo verificato)», asterisco nelle tabelle di contratto e home, FAQ della pagina livello tolte (testo e JSON-LD). Dal 1/6/2027 la riga torna pubblicabile e la nota sparisce da sola. Decisione ancora aperta (di chi gestisce il sito): pubblicare la somma delle voci verificate al posto dell'ultimo minimo; oggi NON lo facciamo, per la regola «somma = totale stampato».
- 1/6/2027 e 1/6/2028 metalmeccanici: stessa regola. Finché il decreto del Ministero non c'è, le 9 pagine restano sul minimo di giugno 2026 con la nota «Cifra da aggiornare» (senza la cifra dell'accordo, che è in una fonte sola).
- FAQ che citano «il prossimo aumento»: quando la data passa e non c'è più un aumento futuro verificato, `genera.py` salta la domanda con un avviso (non si ferma). Riscriverla in `dati/faq.json`.
- Prova di una data futura: `CCNL_OGGI=2027-01-02 python3 ccnl/genera.py && CCNL_OGGI=2027-01-02 python3 ccnl/verifica.py`, poi rigenerare senza variabile prima di pubblicare. Provato il 12/11/2026 con 2027-01-02, 2027-02-02, 2027-06-02, 2028-09-02 e 2029-04-01: 0 errori.
- 1/2/2027 commercio: ultima rata già caricata; il contratto scade il 31/3/2027 → controllare il rinnovo al CNEL.
- Giugno 2027 metalmeccanici: verbale IPCA e poi decreto del Ministero → nuova fonte A (tabelle del decreto) e controllo con l'accordo.
- Multiservizi: nessun lavoro fino al 2029 salvo conguagli (clausola consuntivo art. 73).

Ricerche (FAQ): `python3 ccnl/raccolta/domanda.py` ogni 3 mesi; `verifica.py` segnala le FAQ la cui ricerca non c'è più.

## Monetizzazione
AdSense acceso come gli altri siti: `ccnl` aggiunto a `SITI` in `studio-business/strumenti/monetizzazione.py` e ad `adsense_siti` e `_siti_della_rete`
in `monetizzazione.json`; `ads.txt` scritto da `genera.py`; script solo nelle pagine indicizzabili con almeno 400 parole di contenuto
(regola di EsameB1, per la lezione AdSense «scarso valore» dell'11-12/11): oggi tutte tranne la 404 e una pagina breve. Ogni pagina livello ha
cifre proprie (voci, divisore, part time, aumenti, storico, livelli vicini, declaratoria). Nessuna affiliazione.

## Da fare per pubblicare (passi di Massimiliano)
1. Netlify: «Add new site» → «Import an existing project» → GitHub, repository di questo progetto, **branch `ccr-b7fd6b9e-n096cr`**;
   Base directory `ccnl/sito`, Build command vuoto, Publish directory `.` (il file `ccnl/sito/netlify.toml` lo conferma);
   nome del sito `paga-ccnl` (se diverso, cambiare `URL_SITO` in `ccnl/genera.py` e rigenerare).
2. Netlify → Forms: lasciare acceso il rilevamento dei moduli (modulo `segnalazioni`) e impostare la notifica email.
3. Search Console: proprietà `https://paga-ccnl.netlify.app/` (meta di verifica già nelle pagine), inviare `sitemap.xml`.
4. Dopo la pubblicazione: aggiungere l'host a `SITI` in `studio-business/strumenti/indexnow.py` (cartella `ccnl`) e lanciare l'invio.

## Revisione indipendente del 12/11/2026 (decisioni sui dubbi)
Fonti riscaricate da zero (19 file, stesse impronte) e cifre ricalcolate con un programma diverso da `estrai.py`: tabelle del commercio decodificate dal testo del PDF (non con la lettura ottica), Ministero e contratto riletti con espressioni proprie. 53 pagine livello, 1.182 confronti (minimo, voci, paga oraria e giornaliera, annuo, part time, aumenti futuri, storico): 0 differenze.

- **Multiservizi (divisore 173, 14 mensilità, 40 ore dal testo 2011)**: confermato. Le tabelle del decreto n. 25 del 30/3/2026 calcolano la «retribuzione oraria» come retribuzione mensile ÷ 173 (1.325,63 ÷ 173 = 7,66) e contano tredicesima e quattordicesima. Le pagine dicono «art. 19 del CCNL 31 maggio 2011»; la pagina contratto spiega perché si usa quel testo. L'art. 18 definisce «retribuzione base» = tabellare + contingenza: è la cifra che pubblichiamo; l'E.D.R. di 10,33 € resta dichiarato a parte.
- **Metalmeccanici (173 e tredicesima dal testo 2021)**: confermato; le pagine citano «CCNL 5 febbraio 2021» e il decreto n. 94/2026 conta la tredicesima. Resta da rileggere il testo coordinato del rinnovo quando il CNEL lo deposita.
- **Lavoro domestico D/DS**: la somma è corretta (art. 34, comma 2, lett. a: la retribuzione minima è «comprensiva» dell'indennità di funzione). Corretto il rischio di sottostima: testata e descrizione ora danno il totale (1.612,20 € e 1.682,42 €) con le due voci; confronto tra livelli, tabella della guida e home mostrano «minimo + indennità». La riga della somma dice che è una somma nostra.
- **Logistica I e L**: le etichette NON vengono solo dal Ministero. L'art. 6 del contratto scrive: lettera I (cicli) parametro 110, dopo 6 mesi 116; lettera L (ciclomotori e motocicli) parametro 110, dopo 6 mesi 116, dopo altri 9 mesi 119. Ora le pagine lo citano.
- **Part time**: la proporzione sulle ore è un calcolo dichiarato in pagina («minimo × ore ÷ 40/39»), coerente con il principio di riproporzionamento; resta un'indicazione lorda sul minimo, non un calcolo di busta paga.
- **Logistica, EDR dell'accordo 18/5/2021**: mancava. Il contratto lo paga a parte per 13 mensilità (10,00 € al 3° Super, riparametrato) e «non ha incidenza su alcun istituto»: ora è scritto in ogni pagina livello e nella pagina contratto come voce non compresa nel minimo.
- **Link ai documenti del CNEL**: l'indirizzo del file salvato in `fonti.json` risponde 403 (serve una firma temporanea): erano oltre 170 link rotti. Ora i documenti del CNEL rimandano alla pagina dell'archivio dei contratti, con il codice del contratto accanto (`url_fonte`, `nota_cnel` in `genera.py`). `fonti.py` continua a scaricarli dal servizio pubblico.
- **Chi è inquadrato**: aggiunte le declaratorie citate dal contratto anche per logistica (20 livelli, art. 6) e multiservizi (8 livelli, art. 10 del testo 2011), con profili di esempio; `verifica.py` ritrova ogni citazione nel testo ufficiale. Tutte le 53 pagine livello hanno ora un testo proprio oltre alle cifre.
- **Privacy**: nominato il titolare del trattamento come negli altri siti della rete (solo nella pagina privacy; `verifica.py` lo ammette una volta e solo lì), contatto tramite il modulo, base giuridica con l'articolo, diritti completi, Netlify fuori UE.

Dubbi che restano: (1) quota di testo comune tra pagine livello dello stesso contratto 65-80% (misurata a gruppi di 5 parole): è normale per pagine di dati, ma è il punto da tenere d'occhio per AdSense; (2) per il lavoro domestico le «due fonti» sono la stessa tabella in due copie (Ministero e deposito CNEL): detto in pagina; (3) Filcams è una parte firmataria, non un ente pubblico: detto in pagina; (4) classificazione del multiservizi letta dal testo 2011 (dichiarato in pagina).

## Domanda misurata, titoli e FAQ (13/11/2026)
**Misura.** 342 richieste a `api.seodata.dev` (country=it) con `raccolta/volumi.py` (stesso programma di farmaci; la chiave si legge dal file
locale e non va mai scritta). Risultati in `dati/volumi-2026-11-13.json`: 157 frasi con volume, 185 non nel database dello strumento (404 =
«nessun dato», non «zero»: quasi tutte le forme con «2026», «tabelle retributive X 2026», «minimi contrattuali…» e tutte le forme per livello
della logistica), 1.211 frasi con volume contando le «simili». Volume di una pagina = la frase più cercata attribuita a lei, mai la somma.

**Cosa cercano le persone (volumi mensili).** Teste: ccnl metalmeccanici 33.100, ccnl commercio 22.200, livelli metalmeccanici 18.100,
quattordicesima 12.100, ccnl commercio tabelle retributive 8.100, scatti di anzianità 8.100, livelli ccnl commercio 6.600, salario minimo
italia 6.600, quando si prende la quattordicesima 5.400, ccnl logistica e trasporti 4.400, ccnl multiservizi 3.600. Livelli: **ccnl commercio
5 livello 4.400**, 4 livello 2.400, 3 livello 1.600, 2 livello 720, 1 livello 390, quadro 480, 6 livello 260 (7 livello: 404); «N livello commercio
stipendio netto» 3° 2.400, 4° 1.600, 2° 1.300, 1° 720, 5° 590; **livello c2 / c3 metalmeccanico 3.600**, d2 2.900, b1 e b2 1.900, c1 1.600,
b3 1.300, d1 1.000, a1 590 (le forme «stipendio c3 metalmeccanico», «metalmeccanico livello c3 stipendio» sono 404); ccnl multiservizi 1 e 2
livello 170, 3 livello 110, ccnl pulizie paga oraria 590, ccnl pulizie multiservizi 1.000; badante livello c e cs 1.000, livello a colf 390,
livello bs badante 320, colf livello b retribuzione 320, badante livello ds 260. Colf e badanti: contratto badante 1.900, stipendio badante
convivente 1.600, paga oraria badante a ore 1.600, contratto colf 1.000, ccnl lavoro domestico 1.000, calcolare tredicesima colf 880,
quanto costa una badante 880 (costo con i contributi: non lo calcoliamo). Mestieri: stipendio camionista 1.900 (quanto guadagna un camionista
2.400), stipendio magazziniere 1.300, quanto guadagna un rider 880, stipendio commesso 720, stipendio corriere 480, stipendio oss 3.600,
stipendio guardia giurata 2.900.

**Cosa fa `genera.py` con i volumi** (`MISURE`, `MIN_VOLUME = 100`, `scelta_livello`, `registra_titolo`; scrive `dati/titoli_misurati.json`):
- titolo e h1 delle pagine livello con la forma più cercata del contratto: «CCNL commercio 5° livello: stipendio minimo e paga oraria 2026»,
  «Livello C3 metalmeccanico: stipendio minimo e paga oraria 2026», «CCNL multiservizi 2° livello: paga oraria e minimo 2026»; il modello vale
  per tutti i livelli del contratto, la frase registrata è quella del livello (nessuna per commercio 7°, multiservizi 4°-7° e Quadro).
  Logistica: titoli di prima (nessuna forma per livello misurata). Lavoro domestico: «Colf livello A/B» e «Badante livello BS/CS/DS» solo
  dove il nome è vero per i profili dell'art. 9 (`NOME_DOMESTICO`); AS, C (cuoco) e D restano «Colf e badanti livello …».
- descrizioni: commercio e metalmeccanici con «stipendio minimo … lordi al mese», lavoro domestico con «l'ora per chi lavora a ore».
- pagine contratto, home e guida con la frase più cercata che il titolo contiene per intero (tabella sotto).
- FAQ: 33 nuove e 2 riscritte, solo da frasi misurate (≥ 100) e solo con le cifre già verificate (segnaposto riempiti dai dati). Una risposta che
  cita un livello con la riga in vigore sospesa ora si salta come quelle con un aumento passato (prima mostrava l'ultimo minimo verificato come
  in vigore): con `CCNL_OGGI=2027-01-02` si saltano 3 FAQ (logistica non viaggiante), dal 2/6/2027 anche quelle con il C3 dei metalmeccanici
  (7 in tutto); `genera.py` lo scrive come avviso, da riscrivere quando arriva il decreto.

| | Prima (12/11) | Dopo (13/11) |
|---|---|---|
| Pagine con titolo deciso da una frase misurata (≥ 100/mese) | 0 | 31 (titoli cambiati 37, h1 37, descrizioni 29) |
| FAQ (di cui da frasi misurate) | 49 (0) | **82 (35)**; pagine livello con almeno una FAQ 24 → 31 |
| Home | Paga CCNL: minimi e paga oraria per contratto e livello | Tabelle retributive CCNL 2026: minimi e paga oraria per livello (tabelle retributive ccnl 390) |
| Commercio | CCNL commercio 2026: minimi e paga oraria per livello | CCNL commercio 2026: tabelle retributive, livelli e paga oraria (8.100; FAQ livelli 6.600) |
| Commercio 5° | 5° livello CCNL commercio: paga oraria e minimo 2026 | CCNL commercio 5° livello: stipendio minimo e paga oraria 2026 (4.400) |
| Commercio 3° | 3° livello CCNL commercio: paga oraria e minimo 2026 | CCNL commercio 3° livello: stipendio minimo e paga oraria 2026 (1.600; FAQ netto 2.400) |
| Metalmeccanici | CCNL metalmeccanici 2026: minimi e paga oraria per livello | CCNL metalmeccanici 2026: livelli e tabelle retributive (18.100; FAQ livelli, tabelle, tredicesima) |
| Metalmeccanici C3 | Livello C3 CCNL metalmeccanici: paga oraria e minimo 2026 | Livello C3 metalmeccanico: stipendio minimo e paga oraria 2026 (3.600) |
| Multiservizi | CCNL multiservizi 2026: minimi e paga oraria per livello | CCNL multiservizi e pulizie 2026: livelli e paga oraria (1.000; FAQ paga oraria 590) |
| Logistica | CCNL logistica 2026: minimi e paga oraria per livello | CCNL logistica e trasporti 2026: livelli, minimi e paga oraria (4.400; FAQ camionista, magazziniere, rider, corriere) |
| Lavoro domestico | Colf e badanti 2026: minimi per livello, a ore e conviventi | CCNL lavoro domestico 2026: livelli e minimi di colf e badanti (1.000; FAQ tredicesima 880) |
| Domestico CS | Colf e badanti livello C Super (CS): paga oraria e stipendio 2026 | Badante livello CS: paga oraria e stipendio 2026 (1.000) |
| Domestico C | 0 FAQ | FAQ «Il livello C è quello della badante?» (badante livello c 1.000: no, è il cuoco; rimanda al CS) |
| Guida colf e badanti | Assumere colf o badante: minimi 2026, orari e vitto | Stipendio badante convivente e paga oraria colf 2026 (1.600; FAQ a ore 1.600) |

FAQ «netto» (commercio 1°-5°): rispondono che il contratto fissa solo il lordo, danno il lordo e dicono perché il netto non lo calcoliamo
(nessuna cifra netta). Le FAQ sui mestieri (camionista, corriere, rider, magazziniere) citano solo i livelli in cui l'art. 6 mette quei profili.

**Controlli nuovi in `verifica.py`:** FAQ da frase misurata solo con volume ≥ 100 uguale a quello del file; ogni risposta rifatta con i segnaposto
riempiti da `estratti.json` (non da genera) e ritrovata nella sua pagina, oppure assente se cita un aumento passato o una riga sospesa;
`citazioni` (18 frasi: tredicesima metalmeccanici e colf, cuoco al livello C, profili di magazzino, patenti C-E/C/B, cicli e motocicli, pulizie)
ritrovate nel testo ufficiale; nessun netto in cifre nelle risposte; titoli e h1 = `dati/titoli_misurati.json`, frase con quel volume nel file e
tutte le sue parole nel titolo; «badante»/«colf» nel titolo solo se la declaratoria dice che il livello assiste persone o no. Browser: aggiunte
metalmeccanici C2 e la guida. Prova a mano: cifra alterata in pagina, volume sbagliato, citazione alterata, frase del titolo inventata → 5 errori
su 4 alterazioni. Date future 2027-01-02, 2027-02-02, 2027-06-02, 2028-09-02: 0 errori.

**CCNL non coperti per domanda** (ricerca «ccnl X», con la forma vicina più cercata) e tabella ufficiale leggibile (scaricata il 13/11, senza
aggirare protezioni). Regola del sito: due fonti indipendenti uguali al centesimo; nessun contratto aggiunto oggi.

| CCNL | Domanda/mese | Tabella ufficiale | Esito |
|---|---|---|---|
| Cooperative sociali (T151) | 6.600 (stipendio oss 3.600) | Ministero, decreto n. 30 del 14/6/2024: PDF con testo, minimi conglobati annui per livello A1-F2 fino a gennaio 2026. CNEL 179967 (rinnovo 24/1/2024): scansione, serve la lettura ottica | **Primo candidato.** Due fonti esistono; contratto scaduto il 31/12/2025, rinnovo da controllare al CNEL prima di pubblicare |
| Studi professionali (H442) | 5.400 | CNEL 195625 (testo 16/2/2024, 97 pagine): scansione. Nessuna tabella del Ministero | Una sola fonte ufficiale: no, salvo tabella di una parte firmataria |
| Chimico farmaceutico | 4.400 (ccnl chimici 1.600) | Nessuna tabella del Ministero | Non controllato al CNEL |
| Alimentari industria, telecomunicazioni, metalmeccanici artigiani | 3.600 ciascuno | Nessuna tabella del Ministero (per le TLC solo call center, decreto n. 16/2026) | Non controllati al CNEL |
| Turismo (H052) + pubblici esercizi (H05Y) | 2.900 + 1.900 | CNEL 194291 e 192253: scansioni. Ministero: alberghi fermo al 2013; ristorazione collettiva decreto n. 63/2025 | Una fonte leggibile solo per la ristorazione collettiva (140) |
| Edilizia (F012) | 2.400 | Ministero decreto n. 40 del 13/5/2026: PDF con testo ma per provincia e a ore (102 pagine). CNEL 212523 (rinnovo 2025): scansione | Possibile, ma cifre provinciali |
| Bancari, autoferrotranvieri, gomma plastica | 2.400 ciascuno | Nessuna tabella del Ministero | Non controllati |
| Vigilanza privata | 1.000 (stipendio guardia giurata 2.900) | Ministero decreto n. 50 dell'8/8/2024: PDF con testo, paga base tabellare conglobata annua | Secondo candidato; testo del CNEL da cercare |
| UNEBA, AIOP, ANINSEI, AGIDAE, sanità privata | 1.300 / 880 (contratto aiop 1.900) / 720 (contratto aninsei 1.600) / 390 (contratto agidae 1.000) / 720 | Non controllate | — |

Idee per la prossima misura: «scatti di anzianità commercio» 590 (scatti anzianità commercio 1.600) e «scatti anzianità metalmeccanici» 2.900
sono nei testi già scaricati (testo unico del commercio; per i metalmeccanici art. 6 «Aumenti periodici di anzianità» del CCNL 2021): una tabella degli scatti con la frase citata e il doppio
controllo sarebbe la prossima aggiunta per le pagine esistenti. «quando si prende la quattordicesima» 5.400 è già coperta dalla FAQ del commercio
(art. 225) ma con un'altra domanda. Non usate: «salario minimo italia» 6.600 e «paga oraria minima» 720 (non sono cifre dei contratti).

## Revisione indipendente del 13/11/2026 (titoli e FAQ)
Fonti riscaricate da zero (13 file: Ministero domestico 2026, dd 94, dd 135, dd 25 operai, CNEL 245143, 245798, 223634, 157071, 246574, 105782,
Filcams, Federmeccanica; stesse impronte), commercio e accordo Federmeccanica riletti con lettura ottica propria: 0 differenze nelle cifre di titoli,
descrizioni e FAQ; profili dell'art. 9 (domestico) e dell'art. 6 (logistica) confermati. Correzioni:
- FAQ: «tabelle retributive» del commercio (il totale di Filcams aggiunge il terzo elemento nazionale di 2,07 €, art. 219, con citazione); home
  (la seconda fonte del commercio è Filcams, non un ente pubblico); pulizie (1° livello per i primi nove mesi, con citazione); camionista (F2 escluso);
  anno 2026 detto nelle risposte del livello C e della tredicesima colf.
- Segnaposto con data fissa `{cid/lid:mensile_AAAAMMGG}` (genera e verifica): le risposte su un aumento già avvenuto (commercio novembre 2026,
  multiservizi 2026) mostravano dal 2027 la cifra di una tranche successiva.
- Lavoro domestico: con la tabella dell'anno prima (gennaio, prima di quella nuova) le FAQ con cifre si saltano come quelle sospese (19 a
  `CCNL_OGGI=2027-01-02`): la pagina dice «Tabella 2026», la risposta pronta e il JSON-LD no. Descrizioni con l'anno della tabella, non fisso.
- Descrizione delle pagine con riga sospesa: «ultimo minimo verificato … quello in vigore oggi è più alto» invece di «stipendio minimo … dal».
- Da ricordare: la FAQ «tabelle retributive metalmeccanici» nomina il decreto n. 94/2026: riscriverla quando arriva il decreto di giugno 2027.

## Paga CCNL per chi assume: prova di domanda (27/11/2026)
Scheda: `studio-business/schede/2026-11-27-pagaccnl-annuncio.md` (deviazioni in fondo). Codice in `genera_annuncio.py`, dati in `dati/annuncio.json`.
- `/annuncio-di-lavoro/`: riga pronta per l'annuncio da contratto e livello (53 livelli), tempo pieno, part time in ore o in percentuale; lavoro domestico convivente o a ore. Stessi dati delle pagine livello (`valori`, `prorata`, `orario52`). Il browser sceglie il passo del giorno: se la riga in vigore è sospesa non dà nessuna riga.
- `/annuncio-di-lavoro/cosa-scrivere/`: art. 5 del D.Lgs. 96/2026 citato dai frammenti salvati (art. 2, 5, 13). Nessun importo di sanzione. Il lavoro domestico è escluso dal decreto (art. 2, comma 2).
- `/per-consulenti-e-aziende/` (modulo Netlify `pro`) e `/api/` (modulo `api`, esempio JSON vero, file fermo `/api/esempio.json`): prezzi 149 €/anno, 19 €/mese, 49 €/mese. **Niente è in vendita**: nessun pagamento, nessun servizio API.
- Riquadro `<!--annuncio-->` in home, 5 pagine contratto e 53 pagine livello.
- Eventi GoatCounter: `pagaccnl.com/clic/annuncio-calcolo`, `annuncio-copia`, `pro-prezzo`, `api-chiave`.
- `verifica.py`, `controlla_annuncio()`: stato di ogni livello rifatto da `estratti.json` a oggi e a ogni data futura; circa 18.000 righe del codice del browser (node) uguali alla riga riscritta in Python; citazioni = frammenti e impronta; moduli con netlify e campo trappola; eventi; nessun link di pagamento; esempio API ricalcolato; 59 riquadri; frase nella privacy. `--browser` prova anche le 4 pagine nuove.
- Soglia al 15/1/2027: almeno 300 usi e 10 email Pro, oppure 2 richieste di chiave. Stop al 31/1/2027 sotto 100 usi o 3 email.
- Se il testo di legge cambia: rileggere Normattiva, aggiornare i frammenti e `impronta_frammenti` in `dati/annuncio.json`.
- Secondo giro (27/11): due righe (breve per l'annuncio, completa per il fascicolo), campo «retribuzione offerta» che dà la fascia «da… a…», ore solo intere, evento `api-prezzo`, servizio detto «in valutazione».
- **Lastmod per pagina** (`dati/lastmod.json`, `impronta_contenuto` e `date_lastmod` in `genera.py`): la data di una pagina in sitemap cambia solo se cambia il suo contenuto (titolo, descrizione, JSON-LD, `<main>`); non contano date di controllo e di lettura, file in `/assets/`, riquadro dell'annuncio, menu e piede. `verifica.py` (`controlla_lastmod`) rifà l'impronta. Con `CCNL_OGGI` il registro non si riscrive. Dopo il giro mensile (`controllato_il` nuovo) le pagine con le stesse cifre tengono la loro data.
- Impegno in privacy: dati dei moduli `pro` e `api` cancellati entro il 31/3/2027 se non si apre.

## Pacchetto d'inverno: preavviso e tredicesima (27/11/2026)
Scheda: `studio-business/schede/2026-11-27-pagaccnl-inverno.md` (deviazioni in fondo). Codice in `genera_inverno.py`, dati in `dati/inverno.json` (scritto da `raccolta/inverno.py`).
- 12 pagine nuove: `/preavviso/` + 5 `/preavviso/<contratto>/`; `/tredicesima/` (con il calcolo) + 5 `/tredicesima/<contratto>/`. Totale sito: 79 indicizzabili + 404.
- **Giorni di preavviso**: solo dal testo del contratto in `raccolta/_grezzi` (commercio artt. 251 e 256; metalmeccanici Sez. IV Tit. VIII art. 1 del CCNL 2021; multiservizi art. 57 del CCNL 2011; logistica art. 36; lavoro domestico art. 40). Ogni cella ha la sua frase in `inverno.json` (`mesi`, `giorni`, `unita`: cal = «di calendario», lav = «lavorativi», gg = il contratto non lo dice). Le dimissioni «ridotte della metà» (multiservizi e logistica impiegati, lavoro domestico da 25 ore) sono tabelle derivate (`deriva`, 1/2) con la frase citata. Mai giorni da siti terzi.
- **Cosa il testo non dice, e la pagina lo scrive**: logistica, qualifica 1 (G, H) e lettere I, L non nominate dall'art. 36 (nessun giorno e nessun euro per quei 6 livelli); lavoro domestico sotto le 25 ore senza riduzione per le dimissioni; metalmeccanici «10 giorni» senza «di calendario»; per metalmeccanici e multiservizi il testo completo è quello del 2021 e del 2011 (nota «Quale testo leggiamo»).
- **Indennità sostitutiva in euro** (sul minimo verificato, `G.valori`): metalmeccanici = minimo × mensilità scritte nel contratto; lavoro domestico = minimo ÷ 30 × giorni (chiarimento a verbale n. 2); commercio, multiservizi, logistica = mese di 30 giorni, **conto nostro dichiarato in pagina** (il contratto non lo scrive); operai della logistica = 6 giorni × minimo ÷ 22 oppure ÷ 26 (art. 61 c. 3). Ratei di 13ª e 14ª solo nell'esempio svolto (× 14 ÷ 12) dove il contratto li nomina: commercio art. 252, logistica artt. 18-19 c. 3. Operai in tabella: multiservizi livelli 1-5, logistica 3S-6 (declaratorie).
- **Tredicesima**: importo = minimo mensile; dodicesimi = minimo × mesi ÷ 12 al centesimo (stesso arrotondamento di `prorata`); part time prima sul mensile; colf a ore con `orario52`. Regola delle frazioni di mese citata per contratto (15 giorni o più: commercio art. 208, domestico chiarimento n. 4; più di 15: gli altri tre). Quattordicesima dove `mensilita` = 14. Vitto e alloggio dei conviventi: detto, non sommato.
- **Date**: ogni blocco con cifre (`<!--b:nome-->`) ha già il pezzo della prossima data in cui un minimo cambia, nascosto con `data-dal` (come le pagine livello). Livello con riga sospesa: «da aggiornare», nessun importo. Il calcolo usa i passi di `genera_annuncio._passi`.
- Riquadro `<!--inverno-->` in 53 pagine livello e 5 pagine contratto: fuori dall'impronta del lastmod (`_RE_RIQUADRO`), nessuna data delle pagine esistenti è cambiata. Link anche nel piede.
- `verifica.py`, `controlla_inverno()`: 60 termini riletti dalle frasi e ritrovati nel loro articolo sotto la loro intestazione; livelli riletti dalla frase; 76 citazioni nel testo; tabelle dei termini e 1.139 importi ricalcolati da `estratti.json` cella per cella, oggi e alla prossima data; ogni cifra in euro delle pagine nuove deve essere tra quelle ricalcolate; calcolo del browser (node) = ricalcolo su 242.650 casi (ogni livello, 12 mesi, part time 1-99%, colf 1-40 ore, date future); 58 riquadri; cancello delle 400 parole; «verifica con il tuo consulente». `--browser`: 5 pagine nuove e il calcolo.
- Giro mensile: niente da fare se i testi non cambiano. Con un contratto rinnovato: aggiornare le frasi in `raccolta/inverno.py`, rilanciarlo, poi `genera.py` e `verifica.py`. A gennaio le pagine `/tredicesima/` cambiano anno nel titolo alla prima generazione (lastmod nuovo, vero).
- Già così prima di questo lavoro: con `CCNL_OGGI` nel 2027 `verifica.py` dà 9 errori «manca il pezzo nascosto per la tabella del …» sulle pagine livello con riga sospesa (logistica non viaggiante, metalmeccanici): da guardare a parte.
- Stop della scheda: se al 31/1/2027 le pagine nuove hanno meno di 20 visite in tutto, niente altre pagine di questo tipo.

### Secondo giro dopo la revisione indipendente (27/11/2026, voto 8,2)
- **Quattordicesima**: non è più detta «uguale alla tredicesima». Commercio (art. 225 «in atto al 30 giugno») e logistica (art. 19 «in vigore al 30 giugno»): tabella `quattordicesima` con il minimo che le tabelle già firmate danno per il prossimo 30 giugno (`giorno_14`, `tab_quattordicesima`), con la data della tabella; multiservizi: stessa tabella, e la pagina dice che l'art. 21 non indica il mese. Nel calcolo la riga dice «sul minimo di oggi» (`q14` nei dati).
- **Testi vecchi**: nota «Quale testo leggiamo» subito sotto «In breve». Metalmeccanici: letta per intero l'ipotesi del 22/11/2025 (51 pagine, lettura ottica): non tocca Sez. IV Tit. VIII art. 1 né Tit. IV art. 7. Multiservizi: l'ipotesi del 13/6/2025 (14 pagine) riscrive gli artt. 1, 33, 51, 52-bis, 72, 73, 73-bis, 73-ter, non 20, 21, 57; il rinnovo dell'8 giugno 2021 (così lo chiamano i nostri file) non lo abbiamo e la pagina lo dice. **Controllo fatto a mano**: la lettura ottica completa dei due documenti non è in `_grezzi` (tesseract qui impiega oltre 3 minuti a pagina); in `_grezzi/ocr` c'è in più solo la pag. 6 di `cnel_234754` (art. 33, citato), aggiunta a `fonti.py` e a `fonti.json`.
- **Indennità con i ratei**: commercio e logistica hanno la colonna «con i ratei» (× 14 ÷ 12 sull'importo già arrotondato) in ogni tabella, ricalcolata da `verifica.py`.
- **«Letto il»**: nelle 12 pagine il testo del contratto porta «Letto il 27 novembre 2026: articoli citati in questa pagina (file scaricato il 12 novembre 2026)» (`letto_il` in `inverno.json`, `fonti_box`).
- Citazioni nuove: commercio art. 256 (azienda che chiude prima), logistica art. 36 c. 5, multiservizi art. 33 nel testo 2025, ferie e malattia durante il preavviso (metalmeccanici, multiservizi, logistica, domestico; per il commercio la pagina dice che gli artt. 251, 252 e 256 non ne parlano, e `verifica.py` lo ricontrolla).
- `/preavviso/`: paragrafo sulla procedura online delle dimissioni dalla pagina del Ministero del Lavoro (salvata in `_grezzi/min_dimissioni_2026.html`, 4 frammenti in `inverno.json`, 2 citati) e sezione ferie e malattia.
- Metà dei termini con il numero quando è intero («la metà di 1 mese (15 giorni)»); fasce con le parole del contratto («Oltre 5 e fino a 10 anni»); «da 15 a 120 giorni di calendario».
- `verifica.py`: 85 citazioni, 1.339 importi; controlli nuovi su ratei, tabella della quattordicesima, etichetta del calcolo, data di lettura, frammenti del Ministero.

### Terzo giro prima della pubblicazione (27/11/2026, voto 8,8)
- Tabelle dell'indennità (`.t-euro`, stile in pagina `STILE_EURO`): la cifra «con ratei» sta nella stessa cella, su una seconda riga piccola; intestazioni corte («Fino a 5 anni», «Oltre 5, fino a 10», «Oltre 10»). Sul telefono la colonna «Minimo» è nascosta (resta dai 700 px in su). Nessuna tabella scorre di lato a 375 e 390 px: `verifica.py --browser` lo controlla.
- «SPID o CIE»: c'è nella pagina salvata del Ministero (frammento `spid`); la frase resta.
- Commercio, ferie e malattia: citato l'art. 190 («Il periodo di malattia è considerato utile…»); sulle ferie la pagina dice che non c'è una frase negli artt. 251, 252, 256 e 162-168 (ricontrollato da `verifica.py`).
- Riquadro delle fonti delle 12 pagine: una riga sola, «Articoli del contratto letti il 27 novembre 2026; minimi in euro del giro di controllo del 12 novembre 2026».

