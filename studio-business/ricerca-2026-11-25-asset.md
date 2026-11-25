# Ricerca del 25/11/2026: assistenti AI e libro «Esame B1»

Solo ricerca. Nessun sito toccato, nessun commit.
Regola usata: ogni affermazione ha un numero e una fonte. Dove manca il dato c'è scritto **ipotesi** o **manca**.

## Come sono stati presi i dati

- Fonte: API GoatCounter `rete-siti`, lette il 25/11/2026 tra le 20:44 e le 21:47 UTC.
- `stats/hits` per settimana (lunedì-domenica), con paginazione `exclude_paths`. Totali uguali al cruscotto: 1.009 (2-8/11), 1.792 (9-15/11).
- `stats/hits/{id}` per la provenienza di ogni pagina, settimana per settimana: 1.050 coppie pagina-settimana lette una per una (tutte quelle con almeno 2 visite a settimana su EsameB1, Visa Income, Before You Fly, Aste, Cruise).
- Il resto (pagine con 1 visita) è letto a gruppi con `stats/toprefs?include_paths=`: il totale per sezione è esatto, il dettaglio per pagina no.
- Limite incontrato: l'API ferma a circa 500 chiamate per finestra. Per questo la coda lunga è a gruppi.
- Host vecchi e nuovi sommati (netlify.app + dominio proprio).
- Ultima settimana = 3 giorni soli (23-25/11). Non va confrontata con le altre.
- Eventi di prova `test-controllo` e `test-titolo-html` esclusi.

---

# PARTE 1 — Assistenti AI

## 1.1 Il dato che cambia il quadro

**Il sito che riceve più visite dagli assistenti non è Visa Income. È EsameB1.**

Visite da assistenti AI per sito e per settimana (chatgpt.com + gemini + perplexity; copilot e claude: 0):

| Sito | 26/10-1/11 | 2-8/11 | 9-15/11 | 16-22/11 | 23-25/11 (3 gg) | Quota AI sul sito, 16-22/11 |
|---|---|---|---|---|---|---|
| **EsameB1** | 34 | 47 | 95 | **129** | 62 | 32 % (129 su 397) |
| Visa Income | 59 | 66 | 113 | 125 | 57 | 46 % (125 su 273) |
| Before You Fly | 8 | 32 | 97 | 117 | 48 | 50 % (117 su 236) |
| Aste in Chiaro | 17 | 12 | 19 | 21 | 2 | 64 % (21 su 33) |
| Cruise | 6 | 9 | 3 | 2 | 0 | 5 % |
| Italy Strikes | 0 | 0 | 4 | 6 | 0 | 11 % |
| Paga CCNL | 0 | 0 | 0 | 4 | 1 | 3 % |
| Tourist Tax, EsamiDiStato, FHA, Payroll, FloodCost | 0 | 0 | 0 | 0 | 0 | 0 % |

Per fonte, tutta la rete:

| Fonte | 26/10-1/11 | 2-8/11 | 9-15/11 | 16-22/11 | 23-25/11 |
|---|---|---|---|---|---|
| chatgpt.com | 123 | 164 | 326 | 401 | 170 |
| gemini.google.com | 1 | 2 | 3 | 2 | 0 |
| perplexity | 0 | 0 | 2 | 1 | 0 |
| copilot, claude | 0 | 0 | 0 | 0 | 0 |

- ChatGPT è il 99 % del canale. Gli altri assistenti non contano.
- Nella settimana 16-22/11 ChatGPT (401) ha superato Google (392) su tutta la rete (`stats/toprefs`).
- Google nello stesso periodo: EsameB1 260 → 93, Visa 241 → 70, BYF 200 → 63. Il calo è quello già studiato in `STRATEGIA-RECUPERO.md`.

## 1.2 Quali sezioni vengono citate

Visite AI per sezione (AI / totale visite della sezione):

| Sezione | 2-8/11 | 9-15/11 | 16-22/11 | 23-25/11 | Pagine citate | Quota AI 16-22/11 |
|---|---|---|---|---|---|---|
| EsameB1 `/esempi/` | 23 / 72 | 57 / 98 | **99 / 148** | 49 / 96 | 7 | 67 % |
| Visa `/visa-refusal-rates/` | 54 / 75 | 91 / 154 | 90 / 119 | 39 / 60 | 64 | 76 % |
| BYF `/available-in/` | 18 / 63 | 43 / 108 | 65 / 119 | 11 / 37 | 28 | 55 % |
| EsameB1 `/citta/` | 23 / 233 | 30 / 252 | 19 / 118 | 5 / 66 | 33 | 16 % |
| BYF `/cabin-bags/` | 3 / 3 | 11 / 16 | 19 / 21 | 18 / 20 | 3 | 90 % |
| BYF `/ticket-release-dates/` | 8 / 20 | 11 / 26 | 19 / 25 | 10 / 13 | 5 | 76 % |
| Visa cerimonie australiane | 5 / 15 | 9 / 130 | 15 / 43 | 4 / 5 | 12 | 35 % |
| BYF `/liquids/` | 0 / 32 | 12 / 67 | 10 / 16 | 2 / 2 | 4 | 63 % |
| Visa `/uk-english-test/` | 0 / 52 | 4 / 55 | 11 / 35 | 4 / 6 | 4 | 31 % |
| BYF `/india-e-visa-fee/` | 2 / 9 | 14 / 35 | 1 / 10 | 2 / 2 | 8 | 10 % |

Dentro `/available-in/` conta **solo Starlink**: 38 visite AI lette pagina per pagina su 22 pagine, più circa 23 nella coda (16-22/11). Apple Pay, Spotify, YouTube Premium, Wise, Stripe, Uber, Bolt: da 0 a 2 visite AI a settimana ciascuno.

Le pagine più citate (visite AI per settimana: 2-8/11, 9-15/11, 16-22/11, 23-25/11):

| Pagina | AI | Totale visite 16-22/11 |
|---|---|---|
| EsameB1 `/esempi/cils/` | 4, 22, **36**, 25 | 58 |
| EsameB1 `/esempi/` | 8, 12, 20, 13 | 24 |
| EsameB1 `/esempi/plida/` | 6, 11, 18, 3 | 25 |
| EsameB1 `/esempi/b2/` (online dal 15/11) | –, –, **12**, 5 | 12 |
| EsameB1 `/esempi/celi/` | 5, 10, 5, 0 | 11 |
| EsameB1 `/esempi/a2/` (online dal 15/11) | –, –, 6, 3 | 6 |
| BYF `/cabin-bags/united/` | 1, 4, 9, **14** | 9 |
| BYF `/ticket-release-dates/vatican-museums/` | 7, 5, 8, 8 | 9 |
| BYF `/available-in/starlink/` | 6, 8, 6, 2 | 15 |
| BYF `/available-in/starlink/saudi-arabia/` | 5, 3, 5, 1 | 8 |
| Visa rifiuti Türkiye | 1, 3, 7, 9 | 9 |
| Visa rifiuti Bangladesh | 2, 10, 3, 3 | 3 |
| Visa rifiuti Algeria | 1, 10, 6, 2 | 6 |
| Visa rifiuti India | 3, 3, 6, 3 | 7 |
| Visa rifiuti Pakistan | 4, 4, 3, 0 | 3 |
| Visa `/visa-refusal-rates/canada-visas/` | 6, 1, 3, 0 | 3 |
| Visa `/visa-refusal-rates/australia-visas/` | 6, 2, 3, 1 | 3 |

## 1.3 Lo schema

**Che pagine sono.** Una pagina per ogni voce di un elenco lungo (ente, nazionalità, Paese, compagnia, museo). Il 92 % delle visite AI del 9-22/11 (circa 675 su 735) cade su pagine di questo tipo.

**Che forma ha la domanda.** Due forme sole.

1. **«Qual è il numero o lo stato ufficiale di X?»** Tasso di rifiuto per chi chiede il visto dal Pakistan. Starlink c'è in Arabia Saudita? Misura del bagaglio a mano United. Quando escono i biglietti dei Musei Vaticani.
2. **«Dove trovo i file ufficiali di X?»** Prova d'esempio CILS B1 in PDF con audio e chiavi. È la forma che cresce di più: `/esempi/` è passata da 23 a 99 visite AI in due settimane.

**Quanto la risposta è «un dato più una fonte».** Tutte le pagine citate aprono con una frase sola che contiene il dato, il nome della fonte ufficiale e la data del controllo. Esempi letti nei file: «In 2025, 45.9% of…» (Pakistan), «Not yet. Starlink's official availability map shows…» (Arabia Saudita), «9 x 10 x 17 in» (United), «9 file (PDF, MP3)… gratis» (CILS).

**Ma la forma non basta.** Tre prove contrarie nei nostri dati:

- `/costo/` di EsameB1 apre con un dato e una fonte (CILS 100 €). Visite AI: **0** su 37 visite in tre settimane. L'assistente quel dato lo sa già.
- Le guide in prosa di `/esempi/` (prova scritta, simulazione, confronto): **0** visite AI su 18 visite. Non hanno file da scaricare né un numero unico.
- Le sotto-pagine «easiest Schengen visa» dei rifiuti: 10 → 9 → 6 → 3 visite AI. Le pagine per Paese Schengen di destinazione: 6 visite AI in cinque settimane su 28 pagine.

**Regola pratica che esce dai dati.** Una pagina nuova viene citata se ha tutte e tre le cose:

1. una voce precisa di un elenco lungo (non un tema generale);
2. un dato ufficiale che cambia, oppure file ufficiali da scaricare;
3. una risposta che l'assistente non sa dare a memoria.

Le pagine nuove di questo tipo vengono citate in fretta: `/esempi/b2/` ha avuto 12 visite AI nella prima settimana online.

**Quanto rende una pagina citata.** Rifiuti: mediana 1 visita AI a settimana per pagina (42 pagine Paese lette, 9-22/11). Starlink: circa 0,3 per pagina, con poche pagine forti. `/esempi/`: 14 per pagina.

## 1.4 Quanto vale in euro (da dire chiaro)

- Tutto il canale AI oggi: circa 400 visite a settimana, cioè circa 21.000 l'anno.
- Con la sola pubblicità (1,7-3,3 $ per 1.000 pagine, calcolatore AdSense citato in `DA-PUBBLICARE.md`): **35-70 €/anno** su tutta la rete. E AdSense oggi incassa 0 (registro del cruscotto, sez. 2a).
- Quindi le pagine nuove su Visa e BYF portano visite, non soldi. Valgono per la soglia AdSense e Journey, non per l'incasso diretto.
- **L'unico punto dove una visita AI vale denaro oggi è EsameB1 `/esempi/`**, perché lì c'è un prodotto nostro (5,64 € a copia). Vedi parte 2.

## 1.5 Le 15 pagine o risposte che mancano

Visite attese = visite AI a settimana dopo 3-4 settimane, calcolate dalle pagine simili. Sono stime, non numeri.

Vincoli rispettati:
- Visa e BYF: niente prima del 9/12 (fermo di `STRATEGIA-RECUPERO.md`, azione 2).
- Le 72 pagine Paese dei rifiuti non si toccano fino al 28/12: sono dentro l'esperimento citazioni (`esperimento-citazioni-2026-10-31.md`). Per questo le aggiunte ai rifiuti sono pagine a parte.
- EsameB1 non è nel fermo: lì si può lavorare subito.

| # | Sito | Pagina o risposta mancante | Prova (pagine simili già citate) | Visite AI attese/sett. (prud. / centr.) | Quando |
|---|---|---|---|---|---|
| 1 | EsameB1 | `/esempi/cils-b1-standard/`: file ufficiali del CILS B1 **standard** (diverso dal B1 Cittadinanza) | `/esempi/cils/` 36 AI/sett.; l'esame di dicembre e giugno comprende il B1 standard (`sessioni.json`) | 4 / 10 | subito. **Da verificare** alla fonte che Siena pubblichi i file |
| 2 | EsameB1 | `/esempi/c1/`: prove ufficiali C1 dei 4 enti | `/esempi/b2/` 12 AI nella prima settimana | 3 / 8 | subito |
| 3 | EsameB1 | `/esempi/a1/`: prove ufficiali A1 | `/esempi/a2/` 6 AI nella prima settimana | 2 / 5 | subito |
| 4 | EsameB1 | `/esempi/c2/` | come il n. 2; domanda più piccola (**ipotesi**) | 1 / 3 | subito, insieme al n. 2 |
| 5 | EsameB1 | Dentro `/esempi/cils/`: elenco delle prove CILS B1 Cittadinanza delle sessioni passate, se l'Università le pubblica | la pagina cresce 4 → 22 → 36; chi arriva cerca «altre prove» (**ipotesi**: non misurato) | 0 / 8 | subito. **Da verificare**: se i file non esistono, non si fa |
| 6 | Visa | Pagina unica «US visa refusal rates by nationality» (visti B, tabella del Dipartimento di Stato) | le pagine uniche Canada e Australia: 1-6 AI/sett. ciascuna; gli USA mancano (`visaincome/NOTE.md` riga 195) | 3 / 6 | dopo il 9/12. La fonte risponde 403 dal server (riprovato oggi): il PDF lo scarica Massimiliano, 5 minuti |
| 7 | Visa | Pagine rifiuti per i Paesi sotto la soglia di 10.000 domande (Nepal, Ucraina, Ruanda, Zimbabwe, Siria, Giamaica…): circa 40 Paesi tra 1.000 e 10.000 domande in `rifiuti.json` (da ricontare) | 64 pagine citate; mediana 1 AI/sett. Paesi piccoli: metà (**ipotesi**) | 8 / 20 | dopo il 28/12 (fine esperimento), in un solo lotto |
| 8 | Visa | Riga «United States» dentro ogni pagina Paese dei rifiuti | come il n. 6 | 2 / 6 | dopo il 28/12 |
| 9 | Visa | `/uk-english-test/`: nessuna pagina nuova. Solo misurare | 0 → 4 → 11 AI/sett. su 85 pagine: cresce da sola | – | controllo il 9/12 |
| 10 | BYF | `/cabin-bags/`: 10 compagnie mancanti, prima le americane (Spirit, Allegiant, Hawaiian, Sun Country), poi Aer Lingus, SAS, Finnair, Swiss, Austrian, Transavia | United 1 → 4 → 9 → 14 (in 3 giorni); sezione al 90 % AI | 4 / 10 | dopo il 9/12 (già in coda come «compagnie saltate») |
| 11 | BYF | `/ticket-release-dates/`: 10 luoghi mancanti (Torre Eiffel, Uffizi, Galleria Borghese, Acropoli, Machu Picchu, Shibuya Sky, teamLab, Neuschwanstein, Park Güell, Cupola del Duomo di Firenze) | Vaticani 5-8/sett. stabili, Cenacolo 4, Colosseo 3, Ghibli 2; 19 AI/sett. su 34 pagine | 4 / 8 | dopo il 9/12 |
| 12 | BYF | Dentro le pagine Starlink: il prezzo mensile ufficiale nel Paese | Starlink ≈ 60 AI/sett.; è l'unico servizio citato | 0 / 8 | dopo il 9/12. **Ipotesi**: fonte da verificare prima |
| 13 | BYF | Pagina unica «Starlink coming soon: elenco dei Paesi e nota ufficiale» | indice Starlink 6-8 AI/sett.; Arabia Saudita («coming soon») è la pagina Paese più citata | 2 / 4 | dopo il 9/12 |
| 14 | BYF | **Non fare** altri servizi in `/available-in/` | 7 servizi su 8: 0-2 AI/sett. | 0 | – |
| 15 | Aste | Pagine «auto all'asta» per provincia (oggi una pagina sola) | `/auto-all-asta/` 4 AI su 4-5 visite a settimana; sito al 64 % AI | 3 / 6 | dicembre, con la valutazione del 1° del mese |

Somma centrale: circa **+100 visite AI a settimana** (oggi circa 400). Somma prudente: circa +35.

Cosa **non** fare, con il dato: altre sotto-pagine dei rifiuti (in calo 10 → 3), altre nazionalità per `india-e-visa-fee` (14 → 1), altri aeroporti per i liquidi (10-12 AI/sett. su 103 pagine).

---

# PARTE 2 — EsameB1 e il libro

## 2.1 L'imbuto misurato (19-25/11, 7 giorni; il 25/11 non è finito)

I clic si contano dal 18/11 sera (`DA-PUBBLICARE.md`, riga 28).

| Passo | Numero | Fonte |
|---|---|---|
| Visite a EsameB1 | 423 | `stats/hits`, giorno per giorno |
| Visite su pagine con il riquadro del libro | 357 (84 %) | pagine con `data-libro-proprio` nel sito pubblicato (`git show HEAD`) |
| Clic sul libro | **6** | eventi `esameb1.eu/clic/libro-*` |
| Clic ogni 100 visite con riquadro | **1,7** | 6 / 357 |
| Copie vendute | **manca** | il report KDP non è nel repo |

Dove sono nati i 6 clic:

| Riquadro | Posizione nella pagina pubblicata | Visite | Clic | Clic per 100 visite |
|---|---|---|---|---|
| Home, riquadro in alto (`libro-home`) | parola 66 su 2.934 | 40 | 4 | **10** |
| `/esempi/` e `/esempi/simulazione/`, riquadro grande (`libro-esempi`) | parola 1.172-1.265 su circa 2.050 (57-62 %) | 49 | 1 | 2 |
| Tutte le altre pagine, striscia (`libro-pagine`) | dal 55 % all'80 % della pagina | circa 270 | 1 | **0,4** |

Avvertenze oneste:
- 6 clic sono pochi. La differenza 10 contro 0,4 è grande, ma con questi numeri è un'indicazione, non una prova.
- 2 dei 4 clic della home sono del 20/11, lo stesso giorno delle prove del contatore. Potrebbero essere prove (**non verificabile da qui**).
- Chi usa un blocco pubblicità non viene contato. I clic veri sono di più.

**La pagina più visitata del sito ha il riquadro in fondo.** `/esempi/cils/`: 75 visite in 7 giorni, 62 % da ChatGPT, riquadro alla parola 1.435 su 2.052. Chi arriva lì cerca prove d'esame. Il libro contiene 4 simulazioni.

**Pagine senza nessun riquadro:** `/esempi/a2/`, `/esempi/b2/`, `/risultati/` e le sue 4 pagine.

**Lavoro già in corso stanotte.** Nel repo c'è una modifica non ancora pubblicata (`esameb1/genera.py`, `LIBRO_IN_ALTO`, ore 20:56): sposta il riquadro sotto il titolo nelle 10 pagine più viste. Copre circa 190 delle 317 visite settimanali fuori dalla home. Restano fuori circa 130 visite su circa 110 pagine, tra cui `/esempi/celi/`, `/esempi/certit/`, `/esempi/prova-scritta/`, `/esempi/simulazione/`.

## 2.2 Confronto con le vendite KDP

**Manca.** Ho cercato «royalty», «vendite», «KDP» in `studio-business/` e la cartella `claude/` non esiste nel repo. Ci sono solo:
- compenso a copia: **5,64 €** sul cartaceo a 14,99 € (`fronti-2026-11-12-libri-dai-siti.md`, riga 42). `ORGANIZZAZIONE.md` riga 21 dice 6,35 €: i due numeri non coincidono, va chiarito;
- concorrenti letti con BookBeam il 6/11: Percorso CILS 7-14 copie al giorno, Loescher 8-16, un autopubblicato nuovo 2-4 (`CRUSCOTTO-RETE.md`, righe 307-309).

Senza le copie vere non si può dire quanti clic diventano acquisti. Nelle stime sotto uso 10 % / 15 % / 25 % come **ipotesi**.

**Azione che può fare solo Massimiliano (10 minuti):** dal report KDP, copie al giorno dal 16/11, divise tra cartaceo e Kindle. Con quel numero l'imbuto si chiude.

## 2.3 Domanda di gennaio-febbraio 2027

**Stagionalità dell'anno scorso: manca.** Il sito è online dal 9/10/2026. I file dei volumi (`parole_*.json`) hanno solo medie mensili, non la serie mese per mese.

Quello che si sa dalle sessioni (`esameb1/dati/sessioni.json`):

| Data | Cosa |
|---|---|
| 3/12/2026 | Esame CILS (B1 Cittadinanza e standard) |
| **dal 4/12 al 9/2** | **nessun esame per 68 giorni** |
| 18/1/2027 | Scadenza iscrizione CILS (le sedi possono chiudere prima) |
| 22/1/2027 | Scadenza iscrizione CELI |
| 10/2/2027 | Esame PLIDA |
| 11/2/2027 | Esame CERT.IT |
| 17/2/2027 | Esame CELI cittadinanza |
| 18/2/2027 | Esame CILS cittadinanza |
| 9/3/2027 | Esame CELI generale |

- Febbraio ha 4 esami in 9 giorni. Novembre-dicembre ne ha 3 in 23 giorni.
- Chi fa l'esame a febbraio si iscrive entro metà gennaio e studia da metà dicembre. **Ipotesi**: gli acquisti del libro salgono dal 20/12 e toccano il massimo tra il 10/1 e il 10/2.

Quello che dicono i nostri dati sui giorni d'esame:
- 9-11/11 (esame CELI l'11/11): 140, 114, 128 visite al giorno. Nei giorni feriali della settimana prima: media 79. **+61 %**. Attenzione: il sito era anche in crescita e aveva appena cambiato dominio.
- 24/11 (9 giorni prima del CILS): 102 visite contro 45 del giorno prima; 18 su `/esempi/cils/`.

Stima per le 8,5 settimane dal 1/1 al 28/2 (sono ipotesi costruite su numeri misurati):

| Scenario | Visite/sett. | Clic per 100 visite | Clic → copia | Copie in 8,5 sett. | € |
|---|---|---|---|---|---|
| Prudente | 420 (livello di oggi) | 1,4 (misurato oggi) | 10 % | 5 | 28 |
| Centrale | 635 (settimana 9-15/11, misurata) | 3 (riquadro in alto ovunque: tra 0,4 e 10 misurati) | 15 % | 24 | 137 |
| Ottimista | 1.000 (**ipotesi**) | 5 | 25 % | 106 | 600 |

Queste sono solo le copie che partono dal sito. Le vendite che nascono dentro Amazon non si vedono da qui.

Su un anno intero, dal sito: **circa 170 € prudente, circa 730 € centrale**.

## 2.4 Le domande precise

**Quali pagine creare prima di dicembre?** Una sola vale il tempo: `/esempi/cils-b1-standard/` (n. 1 della parte 1), se i file ufficiali esistono. Le altre pagine d'esempio (C1, A1, C2) portano visite ma chi le legge non compra un libro B1. Una pagina «sessione di febbraio» non serve: dal 4/12 la home e le pagine città mostrano da sole la data del 10/2 (titoli generati dalle sessioni).

**Posizione del riquadro.** È la leva più forte misurata: 10 clic per 100 visite in alto contro 0,4 in basso. Prima pubblicare il lavoro di stanotte sulle 10 pagine, poi misurare 7 giorni, poi estendere a tutte.

**Libro A2.** **No, confermato dai dati.** `/esempi/a2/` ha 11 visite in 11 giorni e `/test-italiano-a2/` meno di 1 a settimana, contro 148 a settimana di `/esempi/` B1. La decisione di Massimiliano del 13/11 (circa 11 copie al mese, «non preparo libri per vendere 10 copie») regge. Si rivede solo se `/esempi/a2/` supera 50 visite a settimana.

**Prova di prezzo dell'ebook.** Il Kindle esiste (ASIN B0HQ2TTHPY in `genera.py`) ma il riquadro porta solo al cartaceo. Prezzo del Kindle: **manca** nel repo. Conto con le regole KDP standard (70 % tra 2,99 e 9,99 €, IVA 4 %; **da verificare nel calcolatore KDP**): a 9,99 € circa 6,5 € a copia, più del cartaceo; a 7,99 € circa 5,2 €; a 6,99 € circa 4,5 €. Chi ha l'esame tra 9 giorni non aspetta la spedizione. Prova proposta: secondo link «Kindle» nel riquadro; 14 giorni a 9,99 €, poi 14 giorni a 6,99 €; a 6,99 € servono almeno il 45 % di copie in più per pareggiare.

---

# TABELLA FINALE — azioni in ordine di € per ora

€/anno = solo incasso diretto stimabile oggi. Dove l'incasso dipende da un'ipotesi è scritto.

| # | Azione | Dato che la giustifica | €/anno prudente / centrale | Ore | €/ora (centr.) | Rischio | Quando |
|---|---|---|---|---|---|---|---|
| 1 | Pubblicare il riquadro del libro in alto sulle 10 pagine più viste (già costruito stanotte) e misurare 7 giorni per etichetta | home in alto 10 clic/100 visite (4 su 40); altrove 0,4 (1 su 270); `/esempi/cils/` 75 visite/sett. con riquadro al 70 % | 60 / 215 | 0,5 (resta solo pubblicare e misurare) | circa 430 | basso; 6 clic sono pochi | entro il 27/11, prima del CILS del 3/12 |
| 2 | Estendere il riquadro in alto a tutte le pagine che lo hanno in basso (circa 110 pagine, 130 visite/sett.) | stesso dato; `/esempi/celi/`, `/certit/`, `/simulazione/`, `/prova-scritta/` oggi al 60-70 % | 40 / 150 | 1 | circa 150 | basso; farlo solo se il n. 1 conferma almeno 2 clic/100 | 4/12 |
| 3 | Massimiliano: copie KDP al giorno dal 16/11 (cartaceo e Kindle) e prezzo del Kindle | manca il dato che chiude l'imbuto; due compensi diversi nel repo (5,64 e 6,35 €) | 0 (serve a decidere il resto) | 10 minuti suoi | – | nessuno | subito |
| 4 | Secondo link «Kindle» nel riquadro, poi prova di prezzo 9,99 → 6,99 € | Kindle a 9,99 € ≈ 6,5 € a copia (da verificare); 4 esami tra il 10 e il 18/2 | 0 / 145 (**ipotesi** +20 % di copie) | 0,5 + 10 minuti di Massimiliano | circa 290 | medio: è un'ipotesi; si misura in KDP | link subito; prezzi dal 20/12 |
| 5 | EsameB1: `/esempi/cils-b1-standard/` con riquadro in alto | `/esempi/cils/` 36 AI/sett.; pagine nuove citate in 7 giorni (`/b2/` 12) | 3 / 12 | 3 | 4 | medio: i file ufficiali vanno verificati | entro il 5/12 |
| 6 | Recupero dell'indicizzazione delle pagine città (già nel piano) | `/citta/` 252 → 118 visite/sett.; Google 157 → 57 | 40 / 110 | già previste | – | vedi `STRATEGIA-RECUPERO.md` | in corso |
| 7 | EsameB1: `/esempi/c1/`, `/a1/`, `/c2/` | `/b2/` 12 e `/a2/` 6 AI nella prima settimana | 1 / 3 | 6 | 0,5 | basso; portano visite, non copie | dicembre, a tempo perso |
| 8 | Visa: pagina unica dei rifiuti USA | Canada e Australia 1-6 AI/sett. per pagina | 0,5 / 1 | 4 + 5 minuti di Massimiliano (PDF) | 0,3 | medio: fonte bloccata dal server | dopo il 9/12 |
| 9 | BYF: 10 compagnie in `/cabin-bags/` e 10 luoghi in `/ticket-release-dates/` | United 14 AI in 3 giorni; Vaticani 5-8/sett. | 1 / 3 | 10 | 0,3 | basso; AdSense BYF respinto il 24/11 | dopo il 9/12 |
| 10 | Visa: circa 40 Paesi piccoli nei rifiuti + riga USA | mediana 1 AI/sett. per pagina | 1 / 3 | 5 | 0,6 | medio: pagine a modello durante il recupero | dopo il 28/12 |
| – | Libro A2 | `/esempi/a2/` 11 visite in 11 giorni | – | – | – | – | **no** |
| – | Altri servizi in `/available-in/` | 0-2 AI/sett. per servizio | – | – | – | – | **no** |

## In una riga

- Gli assistenti portano circa 400 visite a settimana e crescono. In pubblicità valgono 35-70 € l'anno.
- Valgono molto di più dove c'è il libro: `/esempi/` di EsameB1 riceve 99 visite AI a settimana e aveva il riquadro in fondo.
- Le prime quattro azioni costano 2 ore e 20 minuti di Massimiliano. Tutto il resto rende meno di 5 € l'ora.

## Cosa resta incerto

1. Quanti clic diventano copie: serve il report KDP.
2. La stagionalità di gennaio-febbraio: nessun dato dell'anno scorso. Si può chiedere a Massimiliano il grafico di 12 mesi di Google Trends per «esame b1 cittadinanza» (2 minuti).
3. Il dettaglio per pagina della coda lunga (pagine con 1 visita a settimana): letto solo a gruppi.
4. Se ChatGPT continua a crescere: 164 → 326 → 401 a settimana, ma 170 in 3 giorni dà un ritmo di circa 400. Potrebbe essersi fermato.
