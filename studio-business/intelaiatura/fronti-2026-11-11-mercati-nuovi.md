# Fronte: mercati mai toccati (Giappone, Corea, Brasile, più Polonia e Messico), 11/11/2026

**Domanda del giro.** Che cosa nasce adesso (leggi, obblighi, programmi 2026-2027) nei grandi mercati dove non abbiamo siti, e lì qualcuno può pagare un titolare italiano?

**Risposta breve: nessuna idea grande passa le 4 prove.** Nessuna arriva a voto 7; nessuna ha un ottimista ≥ 10.000 €/anno (la migliore si ferma a circa 9.000). Due idee piccole a costo zero hanno le quattro prove quasi complete e, per la regola del 10/11 (nessuna soglia minima), possono entrare in coda: i codici del KSeF in polacco e le multe ai ciclisti in Giappone in più lingue. Tre piste che sembravano grandi sono cadute alla verifica: Brasile riforma tributaria (un concorrente fa già tutto), Corea contributi auto elettriche (fonte offuscata), calcolatore dello stipendio netto in Giappone (nicchia invasa).

Il fatto più importante del giro è sui **pagatori**: nei tre mercati asiatici e in Brasile l'unico pagatore certo per noi resta AdSense.

| Mercato | Rete locale | Possiamo entrare ed essere pagati? | Fonte letta |
|---|---|---|---|
| Giappone | A8.net | **No**: serve un conto in una banca giapponese e un indirizzo in Giappone; "non facciamo bonifici su conti esteri"; solo siti in giapponese | FAQ ufficiali A8 (support.a8.net, voci del 2006-2008: datate, ma mai smentite) |
| Giappone | ValueCommerce, Rakuten, Amazon.co.jp | Non verificato oggi (nessuna pagina letta); il 7/11 Amazon.co.jp risultava 0,5 % sugli elettrodomestici | – |
| Corea | Coupang Partners | **Molto probabilmente no**: fonti non ufficiali parlano di residenza in Corea e verifica con telefono coreano; pagina ufficiale non letta | blog coreani (non ufficiale) |
| Corea | LinkPrice | Non verificato | – |
| Brasile | Amazon Associados, Lomadee | **No** (verifica del 7/11: conto legato a CPF/CNPJ, Lomadee paga via Pix) | ESPLORATE, riga del 7/11 |
| Brasile | Hotmart | **Non dimostrato**: la pagina di aiuto sui prelievi per i non brasiliani risponde 404; l'aiuto dice che i saldi in euro vanno su un conto "abilitato a ricevere euro", ma non dice se un affiliato senza CPF incassa le vendite fatte a brasiliani | help.hotmart.com (riassunto di ricerca) |
| Polonia | Fakturownia, wFirma, iFirma (programmi diretti) | **Sì in linea di principio** (UE, bonifico SEPA); cifre lette sotto; da chiedere al commercialista: fattura a società UE in regime forfettario (iscrizione VIES) | pagine dei programmi, lette oggi |
| Tutti | AdSense | **Sì**, paga a prescindere dalla lingua del sito. Il rendimento per 1.000 visite non è leggibile da nessuna fonte ufficiale: nelle stime sotto è un'**assunzione** (Giappone 2-4 €, Polonia 2-4 €, Brasile e Messico 0,5-1,5 €) | – |

Fonti esterne da cui nascono le idee: autocomplete Google nei Paesi (gl=jp/kr/br/mx/pl e in inglese, circa 150 domande), le API ufficiali lette con curl (Receita Federal brasiliana, Ministero delle Finanze polacco, e-Gov giapponese), le pagine dei programmi di affiliazione polacchi, le FAQ di A8.net.

Limiti dichiarati: Turchia e Indonesia **non indagate** (solo scartate per l'assunzione di pubblicità bassa); per la Corea in coreano ho misurato la domanda ma non letto i concorrenti; Google, Bing e Naver non sono leggibili con curl, quindi i concorrenti sono stati trovati con la ricerca web e poi letti uno per uno.

## Classifica

| # | Idea | Lingua / dove | Voto | Prudente / centrale / ottimista €/anno a 18 mesi | Ore | Le 4 prove |
|---|---|---|---|---|---|---|
| 1 | **Codici di errore e di stato del KSeF, uno per pagina** (fatturazione elettronica obbligatoria in Polonia) | polacco, sito nuovo | **5** | 50 / 850 / 9.000 | 20-30 + 30 min di Massimiliano (conto Fakturownia, domanda al commercialista) | domanda SÌ, dati SÌ, pagatore SÌ (da confermare il lato fiscale), vuoto **A METÀ** |
| 2 | **Multe ai ciclisti in Giappone: tutte le violazioni con l'importo, in più lingue** (cartellino blu dal 1/4/2026) | inglese + giapponese + lingue dei residenti stranieri, sito nuovo piccolo | **5** | 25 / 220 / 1.900 | 12-18 + 0 | domanda SÌ, dati SÌ, pagatore solo AdSense, vuoto SÌ |
| 3 | Brasile: riforma tributaria, codice cClassTrib e NCM uno per pagina | portoghese | **3,5 (NO)** | 30 / 200 / 2.500 | – | domanda SÌ, dati SÌ, pagatore NO, vuoto NO |
| 4 | Corea: contributi auto elettriche per Comune e modello, posti rimasti | coreano | **3 (NO)** | – | – | domanda SÌ, dati NO, pagatore solo AdSense, vuoto non provato |
| 5 | Giappone: calcolatore dello stipendio netto 2026 per stranieri | inglese | **4 (NO)** | – | – | domanda SÌ, vuoto NO |
| 6 | Brasile: quiz dell'esame teorico con la nuova "CNH do Brasil" | portoghese | **4 (NO)** | – | – | domanda SÌ, dati NO |

Formula usata: visite all'anno × (pubblicità + affiliazione) per 1.000 visite. Le visite sono ipotesi, non misure: nessun nostro sito esiste ancora in queste lingue.

---

## 1. Polonia: i codici del KSeF (voto 5)

**Che cosa nasce.** Il KSeF (Krajowy System e-Faktur) è la fatturazione elettronica obbligatoria polacca. L'autocomplete mostra le domande sulle date ("ksef od kiedy obowiązkowy dla wszystkich", "ksef 2027", "ksef kary od 2027", "ksef limit 10 tys", "przesunięcie/odroczenie ksef 2027"): le date esatte delle fasi non le ho lette su una pagina ufficiale oggi, vanno lette prima di costruire.

**Domanda (gl=pl, hl=pl).** Le persone cercano il codice che il programma mostra loro:
- "ksef błąd" 10 (450, 440, 401, 400, 415, 403, 600), "ksef kod błędu" 10 (anche 445, 429, 150, 200), "ksef status 4" 10 (440, 450, 400, 415, 403, 445, 401, 410, 404, 460);
- codici tecnici: "ksef 21" 10 (21180, 21301 brak autoryzacji, 21001, 21111, "exceptioncode 21180");
- contorno: "ksef czy działa dziś / awaria" 10, "ksef token / certyfikat" 10, "ksef tryb offline" 10, "ksef kod qr" 10, "ksef dla rolników / KGW / stowarzyszeń / JDG" 10.

**Dati leggibili.** `https://api.ksef.mf.gov.pl/docs/v2/openapi.json` risponde 200 (652 KB, "KSeF API v2", 63 percorsi): dentro ci sono **78 codici** distinti con descrizione ufficiale (stati di sessione e fattura 100-600; errori 21001-21470, 25001-25011, 26001-26002, 71001-71005, 9101-9105). Esempi letti: 440 "Duplikat faktury", 445 "Błąd weryfikacji, brak poprawnych faktur", 21180 "Status sesji nie pozwala na wykonanie operacji", 21301 "Brak autoryzacji". Anche `raw.githubusercontent.com/CIRFMF/ksef-docs` risponde 200 (l'API di GitHub invece 403: non usata).

**Concorrenti letti su 5 codici.**

| Codice | fakturowo.pl (aiuto del programma) | wFirma (pagina "wyjaśnienia błędów") | Fakturownia |
|---|---|---|---|
| 440 duplicato | pagina dedicata, buona, senza data | una frase | articolo sul duplicato |
| 415 senza permessi | pagina dedicata, buona | – | – |
| 450 | pagina, ma il significato cambia da fonte a fonte: nell'API ufficiale 450 è anche "token errato" in autenticazione, loro lo spiegano solo come errore di validazione | – | – |
| 445 | **assente** (0 occorrenze nella pagina generale degli errori) | **assente** | – |
| 21180 | **assente** | **assente** (0 occorrenze) | – |

Che cosa manca a loro: l'elenco completo (ne coprono 4-6 su 78), i codici tecnici 21xxx e 25xxx, la distinzione tra lo stesso numero in contesti diversi, una data di aggiornamento, e una spiegazione che non dipenda dal loro programma. Che cosa hanno e noi no: il polacco nativo, l'autorevolezza, e i codici più cercati (440, 415, 450) già coperti bene. **Vuoto dimostrato solo sulla coda lunga: per questo il voto resta 5.**

**Chi paga (cifre lette oggi).**
- Fakturownia: **30 % di ogni abbonamento pagato per 24 mesi** dalla registrazione; unica condizione scritta: avere un conto Fakturownia (il piano Micro è 0 zł fino a 3 fatture al mese). Prezzi degli abbonamenti non leggibili (pagina in JavaScript).
- wFirma: **30 % a vita**, link valido 90 giorni.
- iFirma: **100 zł** per uno studio contabile, **50 zł** per la contabilità online, **10 zł** per Faktura+.
- inFakt: pagina vuota a curl (342 caratteri), nessuna cifra.

**Stima (assunzioni).** Abbonamento medio 300 zł/anno → 30 % × 2 anni ≈ 180 zł ≈ 42 € a cliente. Chi cerca un codice di errore ha già un programma: conversione bassa.
- Prudente: 1.500 visite/mese, solo pubblicità a 2,5 €/1.000 → **circa 50 €/anno**.
- Centrale: 8.000 visite/mese, pubblicità 3 € + affiliazione 6 € (1 cliente ogni 7.000 visite) = 9 €/1.000 → **circa 850 €/anno**.
- Ottimista: 40.000 visite/mese, 4 € + 15 € = 19 €/1.000 → **circa 9.000 €/anno**.

**Rischi.** Tema fiscale in una lingua che non controlliamo (ogni pagina deve riportare il testo ufficiale e non inventare rimedi); i venditori possono completare le loro pagine in una settimana; fattura a società polacca dal regime forfettario da chiarire.

## 2. Giappone: tutte le multe ai ciclisti (voto 5)

**Che cosa nasce.** Dal 1/4/2026 la polizia giapponese dà il "cartellino blu" (青切符) anche ai ciclisti dai 16 anni: 113 tipi di violazione, fino a 12.000 yen. Nel primo mese 2.147 cartellini e 135.855 richiami verbali (dati provvisori della polizia, letti in un articolo di agenzia).

**Domanda.**
- Giapponese (gl=jp): "自転車 青切符" 10, tra cui **"自転車 青切符 113種類 一覧"**, "対象 一覧", "金額", "払い方", "何歳から"; "反則金 一覧" 10 (5 su 10 parlano di biciclette); "自転車 歩道 青切符" 10; "自転車 青切符 件数" 9 (per Tokyo, Aichi, Osaka, Miyagi); "自転車 青切符 英語" 3, tra cui **"113種類 一覧 英語"** (qualcuno cerca l'elenco in inglese, probabilmente datori di lavoro e scuole).
- Inglese: "japan bicycle fines" 10 (anche "japan cycling fines 2026", "japan bicycle traffic fines 2026"), "japan traffic fines" 10, "japan speeding fine" 10, "japan e scooter rules" 5. Coda lunga per singola violazione debole (1-5 suggerimenti).

**Dati leggibili.** API ufficiale e-Gov delle leggi: `https://laws.e-gov.go.jp/api/1/lawdata/335CO0000000270` (decreto di attuazione del codice della strada) risponde 200, XML di 1,3 MB. La tabella 別表第六 dà l'importo per ogni violazione e per classe di veicolo (大型車 / 普通車 / 二輪車 / 原付等, dove 原付等 comprende i veicoli leggeri come le biciclette) e la definizione di ogni violazione con l'articolo di legge. Letti: uso del telefono 12.000 yen; 68 righe di tabella. Da fare in costruzione: contare che le righe applicabili alle biciclette siano davvero 113. La pagina del regolamento in PDF della polizia nazionale che ho provato risponde 404.

**Concorrenti letti.**
- GTN Magazine (inglese, aggiornato il 15/4/2026): **un solo importo nel testo** (12.000 yen), il resto in un'immagine; frasi vaghe ("recommended obligation", "may be subject to enforcement").
- Ricerca in inglese sull'elenco completo: Japan Times, Time Out, nippon.com, Tokyo Weekender danno 4-6 importi di esempio; **nessuno ha le 113 violazioni**; i PDF in inglese sono di singole polizie di provincia (Akita, Fukushima) con esempi.
- Ricerca in giapponese "113種類 一覧": Comuni (Shizuoka, Kumamoto, Aomori), DIME, Toyo Keizai, Motor-Fan con "un esempio" di 6-8 importi; **l'elenco completo non compare** nei primi risultati.
Su 5 esempi (telefono 12.000, passaggio a livello 7.000, semaforo 6.000, fianco a fianco 3.000, auricolari): i primi quattro si trovano in ordine sparso, gli auricolari hanno una sola fonte giornalistica (5.000 yen) non confermata dagli altri.

**Chi paga.** Solo AdSense (assunzione 2-4 €/1.000 visite per visitatori in Giappone). A8.net è chiusa per noi. Nessuna affiliazione verificata.

**Stima.** Prudente 1.000 visite/mese × 2 € → **circa 25 €/anno**; centrale 6.000 × 3 € → **circa 220 €**; ottimista 40.000 (giapponese + inglese + vietnamita, cinese, nepalese; più tutte le multe per auto e moto dalla stessa tabella) × 4 € → **circa 1.900 €**.

**Giudizio.** Vuoto vero e dati perfetti, ma soldi piccoli: è una riga della coda, non un'idea grande. Vale il modello "lingue degli immigrati" già vincente con EsameB1.

## 3. Brasile: riforma tributaria, cClassTrib e NCM (voto 3,5, NO)

- **Domanda forte e per codice:** "cclasstrib" 10 (410999, 000001, 200003, 410029, 410002), "cst ibs cbs" 10 (410, 200, 000, 620), "ncm ibs cbs" 8, "calculadora cbs ibs" 10, "reforma tributária 2026" 10 (anche "curso").
- **Dati ottimi:** API aperta della Receita Federal `piloto-cbs.tributos.gov.br/.../calculadora/dados-abertos/` risponde 200 in JSON: 170 classificazioni con riduzioni e crediti, situazioni tributarie, NCM con imposta selettiva (letto: 2202.10.00, 10 %), aliquote di riferimento per Unione, Stato e Comune (oggi 0,9 %, 0,1 %, 0 %), fondamenti legali (177 KB).
- **Vuoto: non c'è.** `buscadorncm.com.br` ha già una pagina per ogni cClassTrib (letti 410999 e 200003: 29-30.000 caratteri ciascuna) e per ogni NCM (letto 2202.10.00: 46.000 caratteri), più ICMS, ISS per 5.571 Comuni, NFS-e; sitemap aggiornata oggi; è una rete di siti fatta come la nostra. `taxradar.app` ha 10.516 pagine NCM con cClassTrib ("base consultata em 09/11/2026"). Poi taxup, IOB, Systax, nfe.io.
- **Pagatore: nessuno dimostrato** (CPF/CNPJ; Hotmart non verificabile). Resta AdSense.
- In inglese la domanda non c'è: "cclasstrib english" 0, "brazil cbs ibs rate" 0.

## 4. Le altre piste, in breve

- **Corea, contributi auto elettriche per Comune** ("전기차 보조금 2026" 10: 현황, 소진, 지자체, 테슬라). La pagina ufficiale `ev.or.kr` risponde 200 ma il contenuto è cifrato da uno script di protezione: è un blocco, non si aggira. Hyundai ha già la ricerca per regione con i posti rimasti; glasswallet.com ha il confronto delle 17 regioni. **NO (3).**
- **Corea, programmi nuovi in coreano** ("청년미래적금" 10, "모두의카드" 10, "민생회복 소비쿠폰" 10, "상생페이백" 10, "농어촌 기본소득" 10): domanda enorme, concorrenti non letti (quindi voto massimo 5), pagatore solo AdSense, e in Corea una parte grande delle ricerche passa da Naver, che non conosciamo. **Non proposta.**
- **Giappone, calcolatore dello stipendio netto per stranieri** ("japan salary calculator" 10, anche "2026" e "for foreigners"): almeno 12 calcolatori, molti nati nel 2026 su pages.dev, più Expatica e relocate.me; le fonti non concordano nemmeno sull'aliquota dei contributi (14,42 % contro 14,69 %), ma la nicchia è invasa. **NO (4).**
- **Giappone in giapponese, leggi 2026** ("子ども子育て支援金" 10, "高校無償化 2026" 10, "年収の壁 2026" 10, "こども誰でも通園制度" 10 con i nomi delle città): domanda fortissima, ma fonti sparse su 1.700 Comuni e grandi testate; concorrenti non letti. **Non proposta.**
- **Brasile, "CNH do Brasil"** (patente senza autoscuola obbligatoria; "cnh sem autoescola" 10, "simulado detran 2026" 10 con gli Stati): l'esame usa una banca nazionale di domande, ma non ho trovato nessuna pubblicazione ufficiale della banca (solo dentro l'app); doutormultas, app e simulatori dei Detran già presenti. **NO (4)**; si riapre se la banca viene pubblicata.
- **Brasile, altro** ("cnpj alfanumérico" 10, "pix automático" 10, "ipva 2027" 10 con gli Stati, "nova carteira de identidade" 10 con gli Stati): domanda alta, pubblicità bassa, nessun pagatore; concorrenti non letti. **Non proposte.**
- **Messico** ("curp biométrica" 10 con gli Stati, "registro de celular con curp" 10 per operatore, "semana de 40 horas" 10): stessa situazione del Brasile; non approfondito. **Non proposto.**
- **Polonia, programmi per le famiglie** ("bon ciepłowniczy" 10 con le città, "czyste powietrze 2026 progi dochodowe" 10, "mój prąd 7.0" 10): non approfonditi; la Polonia è l'unico di questi mercati dove un pagatore ci può pagare senza ostacoli, merita un giro suo.
- **Per gli stranieri in Giappone e Corea, in inglese** ("gaimen kirikae" 10, "japan pension refund" 10, "korea arc card" 10): già in ESPLORATE come riserve (patente, pensione, costi del permesso); niente di nuovo oltre alle multe in bicicletta.

## Che cosa si impara

1. Fuori dall'Europa il collo di bottiglia non è la domanda (dappertutto 10 suggerimenti) ma **chi ci paga**: A8.net, Coupang, Amazon Brasile e Lomadee chiedono conto o documento locale. Con il solo AdSense servono centinaia di migliaia di visite al mese per arrivare a 10.000 €.
2. Il modello "un codice ufficiale per pagina" in Brasile è già occupato da una rete uguale alla nostra. In Polonia lo occupano solo i venditori di programmi, e solo per i codici più comuni.
3. Mercato da guardare meglio: **Polonia** (UE, bonifico, programmi con percentuali scritte dal 30 % in su).
