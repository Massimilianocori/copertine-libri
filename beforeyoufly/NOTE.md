# Before You Fly – note di lavoro

Costruito il 10/10/2026. Sito statico in inglese, generato da `genera.py` in `sito/` (286 pagine indicizzabili + 404 dal 17/10/2026; erano 272).
Indirizzo previsto: `https://before-you-fly.netlify.app` (costante `URL_SITO` in `genera.py`, unico punto da cambiare).
Meta di Search Console: `GOOGLE_VERIFICA` in `genera.py` (stesso account degli altri siti), presente in ogni pagina.
Non pubblicato, nessun account creato. Pubblicazione Netlify: cartella `beforeyoufly/sito` (il file `sito/netlify.toml` contiene la regola `ignore`, così Netlify ricostruisce solo quando cambia questa cartella).

## Cosa contiene

| Sezione | Pagine | Fonte |
|---|---|---|
| Validità del passaporto e visti (passaporto britannico) | indice con controllo e ricerca + 225 pagine paese | FCDO, GOV.UK Content API (`/api/content/foreign-travel-advice/<paese>`), sezioni "Passport validity requirements" e "Visa requirements", OGL v3 |
| Liquidi in aeroporto (100 ml o 2 litri) | indice/tabella + 52 aeroporti + 2 regole nazionali (USA TSA, Canada CATSA) | pagina ufficiale di ogni aeroporto (o del gestore/autorità indicati) |
| EES / ETIAS | 1 pagina di stato | Commissione europea (home-affairs.ec.europa.eu) + GOV.UK (FCDO, Spagna, sezione "New Schengen entry requirements") |
| Servizio | home, about/fonti, contatti (Netlify Forms + honeypot), privacy, 404 (link assoluti, noindex) | – |

Riquadro affiliati: `dati/affiliati.json` (assicurazione, eSIM, parcheggi/lounge). Nascosto finché gli URL sono vuoti. Spazio pubblicità: `<div class="ad-slot">` vuoto (nascosto da CSS).

## File

| File | A cosa serve |
|---|---|
| `genera.py` | genera tutte le pagine; contiene il motore del controllo passaporto in Python e lo stesso in JS |
| `raccolta/passaporti.py` | scarica le 226 pagine FCDO (date nell'ora del Regno Unito), estrae le sezioni "Passport validity requirements" e "Visa requirements", classifica la regola e il visto, scrive `dati/passaporti.json`; se legge meno di 200 pagine non sovrascrive; registra i testi cambiati in `dati/passaporti_cambi.json` |
| `raccolta/liquidi.py` | ricontrollo mensile: per ogni aeroporto verifica che le frasi citate siano ancora sulla pagina ufficiale (`BYF_BROWSER=1` per i siti letti con il browser) |
| `raccolta/eesetias.py` | controlla che le frasi ufficiali su EES/ETIAS siano ancora presenti (esce con 1 se ne sparisce una, es. "ETIAS is currently not in operation") |
| `dati/passaporti.json` | 226 paesi: testo ufficiale parola per parola, regola riconosciuta (o `manuale` + motivo), data di aggiornamento della pagina, note di modifica |
| `dati/aeroporti.json` | regole sui liquidi lette a mano: frasi citate, eccezioni, regola, URL, data del controllo, modo di lettura; aeroporti esclusi con il motivo |
| `dati/ees_etias.json` | frasi ufficiali EES/ETIAS e GOV.UK con esito della ricerca, date di modifica delle pagine |
| `verifica.py` | 33 casi a mano, JS contro Python su 3.000 casi, link, fonti/date/citazioni, struttura, parole vietate, Playwright a 375 px (5 pagine), visti (riassunti solo da schema), FAQ dei liquidi solo da citazioni, titoli ≤ 65 e descrizioni ≤ 160 |

## Passaporti: come si legge la regola (nessuna interpretazione)

- La regola diventa un calcolo SOLO se la frase FCDO corrisponde a uno di questi schemi: "expiry date at least / more than N months/days after the date you arrive", "valid for at least N months from the date you arrive", "... after the date you plan to leave", "expiry date after the day you plan to leave", "valid for the duration/length of your stay", Schengen e simili ("date of issue less than 10 years before the date you arrive" + "at least 3 months/90 days after the day you plan to leave"), Gibilterra ("issued within the previous 10 years ... at least 3 months after the day you intend to leave").
- Frasi riferite ad altri gruppi (residenti, titolari di visto, transito) non cambiano la regola per chi visita; vengono comunque mostrate nel testo ufficiale.
- Se la frase principale contiene "visa application", "visa expires", "Entry Permit", "recommend", "Up until", "valid on entry", "However", "usually", "plus an additional", oppure se il testo contiene un'altra regola diversa, o regole diverse per più territori: stato `manuale`, si mostra solo la frase ufficiale tra virgolette e il controllo dice di leggerla.
- Esito del 10/10/2026: **213 regole automatiche, 13 da leggere** (Afghanistan, Antartide (sezione vuota: nessuna pagina), Azerbaigian ("usually"), Bangladesh (rimanda al visto), Colombia ("valid on entry. However ... recommend"), Isole Cook/Tokelau/Niue (tre territori), Repubblica Dominicana ("Up until 31 December 2026"), Irlanda (nessuna sezione di validità: si cita "Passport and ID requirements"), Pakistan e Sierra Leone (dalla domanda di visto), Russia (dalla scadenza del visto), Georgia del Sud (Entry Permit + 4 settimane), Sant'Elena/Ascensione/Tristan da Cunha (territori diversi)). La ricerca del 10/10 parlava di 17 casi particolari: con lo schema attuale ne restano 13; gli altri (es. Israele 90 giorni, Costa Rica 1 giorno, St Lucia "dopo il giorno di uscita", Turchia 150 giorni, Cuba doppia condizione) hanno frasi esatte e sono calcolati.
- Ho controllato a occhio tutte le 213 regole riconosciute contro la frase ufficiale (elenco in `dati/passaporti.json`, campo `regola.frase`).
- Conteggio dei mesi: stesso giorno N mesi dopo; se il giorno non esiste, ultimo giorno del mese (31/8 + 6 mesi = 28/2 o 29/2). "More than" = almeno un giorno dopo. "Duration of stay" = non scade prima del giorno di partenza (scadenza il giorno stesso = valido). "Less than 10 years before the date you arrive" = emesso dopo lo stesso giorno di 10 anni prima (esattamente 10 anni = non valido). Margine sotto 7 giorni: il sito avvisa "Only just".

## Liquidi: aeroporti inclusi (38) e lettura

Tutti letti il 10/10/2026. Regola: 9 fino a 2 litri (LHR, LGW, EDI, BRS, DUB, VIE, FCO, LIN, KRK), 23 a 100 ml, 5 dipende dal varco/terminal (FRA, BER, MXP, PRG, OPO), 1 con pagine ufficiali in contraddizione (MUC). Dove la pagina lo dice, è citata la condizione delle borracce metalliche/termiche vuote (LHR, LGW, EDI, BRS, VIE, BER) e dei contenitori oltre 2 litri solo vuoti (FCO).
- Lettura "diretta" (richiesta HTTP normale, 200): LHR, LGW, MAN, STN, LTN, EMA, ABZ, DUB, FRA, HEL, EIN, PRG, KRK, GOV.UK.
- Lettura con browser automatico (il sito blocca le richieste semplici o carica il testo con JavaScript): EDI, BRS, MUC, BER, VIE, FCO, LIN, MXP, ARN, GOT, MMX, CPH, LIS, OPO, FAO, FNC, Aena (MAD, BCN, AGP, PMI, ALC), IST, DOH, HKG, BNE, TSA, CATSA, Your Europe.
- Casi particolari:
  - **Francoforte** (dopo la revisione del 10/10: 'dipende'): la pagina "Security check" dice 2 litri alla maggior parte dei varchi del T1 e a tutti quelli del T3; 100 ml ai gate C1, C2, C4, C6, a "Certain special security checkpoints in Terminal 1" e ai varchi transfer; consiglio ufficiale di controllare il gate sotto "Departures". Il PDF "Flying with liquids is easy" collegato dalla pagina è un volantino UE generico (100 ml, senza data): mostrato come tale, non come regola di Francoforte.
  - **Monaco**: la pagina dice "Liquids (up to two liters per container)" con i CT e "You may carry several containers totaling less than two liters", ma la didascalia delle foto dei CT sulla stessa pagina dice "liquids up to 100 ml". Mostrate entrambe, nessuna scelta nostra.
  - **Spagna**: nessuna pagina per aeroporto trovata; si cita la pagina generale sul bagaglio a mano di Aena (gestore degli aeroporti pubblici spagnoli). La pagina non elenca eccezioni per aeroporto o per varco e non dice che vale ovunque: lo scriviamo così, senza aggiungere altro.
  - **Hong Kong**: fonte = Civil Aviation Department (autorità), non il sito dell'aeroporto (pagina attuale non trovata). La pagina parla di misure in vigore dal 21/3/2007 e riporta "Last revision date: 1 June 2024": lo diciamo sulla pagina.
  - **Aberdeen**: la pagina contiene anche un vecchio avviso ("from midnight on Saturday 8 June"): entrambi i testi dicono 100 ml.
  - **Helsinki**: 100 ml per contenitore, totale 2 litri, liquidi nella borsa (pagina Finavia); controllo transfer: 100 ml in busta da 1 litro (FAQ Finavia, seconda fonte citata).
  - **USA e Canada**: una regola nazionale ciascuno (TSA, CATSA), pagine `liquids/us-airports-tsa/` e `liquids/canada-airports-catsa/`.
- Contesto citato nell'indice: GOV.UK (DfT, "The rules ... depend on the airport"; OGL) e Your Europe ("no container may hold more than 100 ml", "Last checked: 16/06/2026"; non cita i CT approvati: lo diciamo e rimandiamo alla pagina dell'aeroporto).
- Una pagina ufficiale della Commissione europea specifica sui 2 litri (luglio 2025) non è stata trovata leggibile: la data 26/7/2025 è citata solo come la scrive la pagina ufficiale di Fiumicino.

## Liquidi: aeroporti esclusi (pagina ufficiale bloccata, non trovata o poco chiara)

Amsterdam Schiphol (403 anche nel browser) · Parigi CDG/Orly (403) · Birmingham, Glasgow, Newcastle, London City (403) · Belfast International, Belfast City, Bournemouth, Liverpool, Cardiff, Leeds Bradford, Southend, Exeter (404, non raggiungibile, pagina vuota o senza frase sui liquidi) · Atene (403 / redirect) · Bruxelles (pagina letta ma senza frase sui liquidi) · Zurigo, Ginevra, Oslo, Amburgo, Düsseldorf, Colonia-Bonn, Stoccarda (404/403) · Nizza, Lione, Venezia, Napoli, Bologna, Budapest, Varsavia, Bucarest, Malta (pagina non trovata/bloccata/anti-robot) · Dubai, Singapore (nessun limite chiaro per contenitore), Auckland, Sydney, Melbourne (non trovate/bloccate) · Toronto (la pagina rimanda a CATSA: coperto dalla regola nazionale del Canada).
L'elenco è anche nella pagina `liquids/` del sito. Si aggiungono quando la pagina ufficiale è leggibile e chiara.

## EES / ETIAS

- Commissione europea, pagina Smart Borders (modificata il 14/7/2026): "ETIAS is currently not in operation and no applications for travel authorisations are collected at this point. The European Union will inform about the specific date for the start of ETIAS several months prior to its launch." e "The Entry Exit System is fully operational since 10 April 2026."
- Pagina EES (modificata il 10/4/2026) e notizia del 30/3/2026 (avvio progressivo il 12/10/2025, pieno funzionamento il 10/4/2026).
- GOV.UK, travel advice Spagna, "New Schengen entry requirements": cosa fare ora (registrazione biometrica gratuita, nessuna azione prima del confine, tempi più lunghi, Dover/Eurotunnel/St Pancras, record valido 3 anni, esenzione per residenti di lungo periodo).
- travel-europe.europa.eu (sito ufficiale EES/ETIAS): non leggibile dal server (catena del certificato TLS incompleta). Non si è disattivata la verifica TLS: solo link.
- Nessuna data di avvio di ETIAS oltre le frasi ufficiali.

## Ricontrolli (nessuna promessa sul sito)

Il sito non promette aggiornamenti periodici: mostra solo "Last checked: <data>" (data del controllo) e, per GOV.UK, la data di aggiornamento della pagina ufficiale (ora del Regno Unito).
Il ricontrollo mensile viene programmato dalla sessione principale. **I dati cambiano sul sito solo quando si rigenera e si ripubblica** (genera.py → commit → Netlify).

| Cosa | Comando | Se cambia qualcosa |
|---|---|---|
| Passaporti (226 pagine FCDO) | `python3 -I beforeyoufly/raccolta/passaporti.py` | voci nuove in `dati/passaporti_cambi.json`: rileggere quelle pagine, controllare la regola riconosciuta e i casi di `verifica.py` |
| EES / ETIAS | `python3 -I beforeyoufly/raccolta/eesetias.py` | esce con 1 se una frase ufficiale sparisce (es. "ETIAS is currently not in operation"): riscrivere la pagina a mano, senza date non ufficiali |
| Liquidi (38 aeroporti + 2 nazionali) | `BYF_BROWSER=1 python3 -I beforeyoufly/raccolta/liquidi.py` | per ogni "[CAMBIATA?]" o "[DA CONTROLLARE A MANO]": aprire la pagina, leggerla, aggiornare `dati/aeroporti.json` (frasi, regola, `controllato_il`); riprovare anche gli esclusi |
| Sempre, dopo un cambio | `python3 beforeyoufly/genera.py && python3 beforeyoufly/verifica.py` | commit e pubblicazione (massimo una volta a settimana per i crediti Netlify condivisi) |

## Da fare per Massimiliano (quando decide di pubblicare)
1. Netlify: nuovo sito dalla cartella `beforeyoufly/sito` con nome `before-you-fly` (se il nome è preso, cambiare `URL_SITO` in `genera.py` e rigenerare).
2. Search Console: aggiungere la proprietà (la meta di verifica è già nelle pagine) e inviare `sitemap.xml`.
3. Notifiche email dei moduli Netlify.

## Correzioni dopo la revisione indipendente (10/10/2026, `scratchpad/beforeyoufly/REVISIONE.md`)
1. Mai esito verde se il passaporto scade prima della partenza (anche con regole contate dall'arrivo): riquadro rosso "Your passport expires before you leave". Nuovi casi 28-33 (Thailandia, Turchia, Israele, Kazakistan) e caso 23 (Maldive) ora "no".
2. Schengen: le date si chiamano "Date you first enter the Schengen area" / "Date you leave the Schengen area (last Schengen country)", con la nota sui viaggi in più paesi Schengen.
3. Gibilterra: non è Schengen; riassunto con le parole FCDO "issued within the previous 10 years" e "leave Gibraltar or the Schengen Area", gruppo a parte.
4. Le 12 pagine senza controllo non promettono più il controllo; Irlanda: "No passport is legally required for British nationals under the Common Travel Area, but your airline or ferry may require one" + le due frasi FCDO citate.
5. Nel riquadro del risultato compaiono le frasi FCDO che cambiano la risposta pratica (compagnie aeree in Belize e Laos, raccomandazione dell'ambasciata del Messico, transito 6 mesi per USA/Canada/Australia/Messico/Nuova Zelanda) e le regole per altri casi (residenti, transito UAE, visti: 21 paesi), citate separatamente.
6-9. Francoforte (varchi speciali T1 + consiglio sul gate), Monaco (più contenitori sotto i 2 litri in totale), borracce vuote (LHR, EDI, BRS, VIE; FCO contenitori oltre 2 litri vuoti), Aena (solo ciò che la pagina dice).
10. Tolte le frasi "updated weekly / re-checked every week/month": solo "Last checked".
11. Il testo ufficiale nel risultato è mostrato a blocchi interi e separati (niente tagli a metà, niente elenchi cuciti con "; ").
Piccole: date GOV.UK nell'ora del Regno Unito (Cile: 9/10), note di modifica senza a capo finali, motivo breve per l'Irlanda nella pagina About, link EES/ETIAS con testi diversi, Hong Kong con data della pagina, frasi "should" presentate come "FCDO advice".

## Pubblicazione (11/10/2026)
- Online su https://before-you-fly.netlify.app (Netlify, base `beforeyoufly/sito`), 272 pagine in sitemap. Search Console con il meta tag dell'account (stesso degli altri siti) e sitemap inviata. Verdetto: al 9/12/2026 o al 10/12, soglia ≥ 200 impression a settimana. Ricontrollo mensile delle fonti: routine del 3 di ogni mese.

## 17/10/2026: liquidi e visti, sulle ricerche vere di Search Console

**Perché.** Search Console, 24 ore (16-17/10): 270 impressioni, 0 clic, posizione media 42,9. Pagine: `liquids/us-airports-tsa` 55, `liquids/barcelona` 27, `liquids/berlin` 14, `liquids/` 13, `stockholm-arlanda` 11, `eindhoven` 11, `passport-validity/mexico` 11, `passport-validity/spain` 9, `milan-malpensa` 8, `gothenburg-landvetter` 6. Ricerche: "prague airport liquid rules 2026", "barcelona airport liquid rules", "do i need a visa for egypt with a british passport", "liquid limit", "berlin airport liquid rules 2026", "berlin brandenburg liquid rules", "palma airport liquid rules 2026", "stockholm airport liquid rules", "passport validity for travel", "spain passport expiration rules". Google prova soprattutto le pagine liquidi, ma troppo in basso; la ricerca sul visto dell'Egitto apre una famiglia nuova (visti) che le pagine passaporto non coprivano.

**Liquidi.**
- Titoli scritti come le ricerche, con l'anno e la sigla: "Berlin Brandenburg Airport (BER) Liquid Rules 2026: 100 ml or 2L?", "Barcelona Airport (BCN) Liquid Rules 2026: 100 ml or 2 litres?", "US Airport Liquid Rules 2026 (TSA): 100 ml or More?". Si sceglie la prima forma che sta in 65 caratteri (funzioni `titoli_liquidi` e `scegli`); nel titolo il nome breve come lo cerca la gente (Barcelona, Malaga, Alicante, Athens, Dubai, Malta…: `NOMI_TITOLO`), nel titolo H1 e nel testo il nome completo del file.
- In cima a ogni pagina: "Can I take liquids over 100 ml through security at <aeroporto> (<sigla>)?" e una risposta in una frase: Yes / No / It depends on the checkpoint / Not clear (dalla `regola`) + la `sintesi` del file. Dove serve una sfumatura c'è il campo `risposta` in `dati/aeroporti.json` (Fiumicino "Yes, with exceptions", Brisbane "No, on international flights", Zurigo "It depends on where your journey starts"). Per gli aeroporti Aena la pagina dice che la fonte è la pagina generale di Aena, non una pagina dell'aeroporto.
- FAQ (da 1 a 4 domande vere: oltre 100 ml, busta di plastica, togliere i liquidi dalla borsa, terminal/varchi, borracce) con JSON-LD FAQPage. Le risposte sono SOLO citazioni ufficiali intere (`citazioni`, `eccezioni`, e per Monaco la seconda frase della stessa pagina), precedute da "Quoted from <fonte> (checked on <data>)". Nessuna frase nostra. 54 pagine, 130 risposte; per le regole che dipendono dal varco la prima risposta riporta tutto il testo ufficiale nell'ordine della pagina, per non perdere il contesto.
- Collegamenti agli altri aeroporti dello stesso Paese con la sigla (la Spagna ora ne ha 11).
- Descrizioni ≤ 160 caratteri con la domanda e la risposta.
- **14 aeroporti nuovi (38 → 52)**, letti il 17/10/2026 con frasi copiate parola per parola:
  - riprovati dagli esclusi con Playwright: Amsterdam Schiphol (100 ml; l'indirizzo schiphol.com apre la pagina, schiphol.nl aperto direttamente mostra un controllo anti-robot), Atene (100 ml), Malta (2 litri; contenitori oltre 2 litri solo vuoti), Zurigo (dipende: 2 litri per chi parte da Zurigo, 100 ml per chi è in transito), Düsseldorf (100 ml; ai varchi CT i liquidi restano nella borsa), Bruxelles (100 ml: ora c'è una pagina "Liquids and gels"), Dubai (100 ml, massimo 10 contenitori), Budapest (100 ml);
  - Aena, stessa pagina generale già citata (le pagine di Palma, Málaga, Alicante e Madrid c'erano già dal 10/10): Tenerife South, Lanzarote (César Manrique), Gran Canaria, Ibiza, Fuerteventura, Menorca. Ognuno è elencato da Aena sul proprio sito (indirizzo nella nota della pagina); la pagina dice che la fonte è la pagina generale di Aena, non una pagina dell'aeroporto.
  - ancora esclusi (riprovati il 17/10): Parigi (pagina senza testo nel browser), Birmingham, Glasgow, Newcastle, London City (403 anche nel browser), Liverpool, Belfast International, Leeds Bradford (404 o non raggiungibili), Belfast City e Venezia (nessuna frase sui liquidi), Ginevra e Varsavia (regola in sezioni che il browser non legge), Oslo (solo "1-liter bags", nessun limite per contenitore), Singapore (nessun limite chiaro), Amburgo e Napoli. Non riprovati: Bournemouth, Cardiff, Southend, Exeter, Colonia-Bonn, Stoccarda, Nizza, Lione, Bologna, Bucarest, Auckland, Sydney, Melbourne.
- `raccolta/liquidi.py` con `BYF_BROWSER=1` il 17/10: 55 pagine su 55 invariate (52 aeroporti, 2 nazionali, FAQ Finavia). Atene e Schiphol a volte mostrano prima un controllo anti-robot: lo script ora riprova fino a 3 volte con attese più lunghe; se uno dei due torna "[DA CONTROLLARE A MANO]", rilanciare prima di toccare i dati. Le date "checked on" dei 38 aeroporti del 10/10 restano al 10/10 (lettura a mano); i 14 nuovi hanno il 17/10.

**Visti sulle pagine passaporto.**
- `raccolta/passaporti.py` salva ora anche la sezione "Visa requirements" della pagina FCDO "Entry requirements", parola per parola (campo `visto`: `titolo_sezione`, `testo`, `frase`, `schema`, `sintesi`, `motivo`). Lettura del 17/10/2026: 226 pagine su 226, nessun testo di validità cambiato rispetto al 10/10.
- Riassunto di una riga SOLO se la prima frase corrisponde per intero a uno di questi schemi (`SCHEMI_VISTO`): Schengen ("You can travel without a visa to the Schengen area, which includes X, for up to 90 days in any 180-day period"), "You can visit X without a visa for up to N days/months …" (e varianti con "for tourism", "in any 180-day period", "within a 6-month period"), "You do not need a visa to visit X", "You can visit X without a visa", "You must have/get a visa to visit/enter X", "You need a visa to visit X and you must apply in advance", "You must get a visa before you travel". La frase deve parlare proprio del paese della pagina (la pagina Palestina cita Israele: niente riassunto). Niente riassunto se compaiono "usually", "normally", "until", "from <data>", "discretion", "however", "unless", "except", "if you", "may", "check", "most"…, se il resto del paragrafo aggiunge "however/but/unless/except", o, per i riassunti "senza visto", se la sezione parla di ETA/eTA/ESTA/ETIAS, autorizzazione di viaggio, tassa d'ingresso o tessera turistica (USA, Canada, Nuova Zelanda, St Kitts, Cile, Suriname, Madagascar restano senza riassunto).
- Esito (dopo la revisione, sotto): **135 paesi con il riassunto, 87 solo con la citazione** (tra questi Egitto "normally need a visa", Messico, Thailandia, USA, Emirati, India, Giappone, Israele), **3 pagine senza sezione visti** (Afghanistan, Territorio britannico dell'Oceano Indiano, Georgia del Sud: la pagina lo dice e rimanda a GOV.UK). Riassunti controllati a occhio contro la frase FCDO.
- Sulla pagina: riga "Visa (FCDO)" nel riquadro in alto, sezione "Do I need a visa for <Paese> with a British passport?" con il riassunto (se c'è, dichiarato come nostro), la prima parte del testo ufficiale tra virgolette, il resto della sezione in un riquadro apribile, fonte e date. Titolo "<Paese> Visa & Passport Validity for British Passport Holders 2026" (o la prima forma più corta che sta in 65 caratteri: solo "South Georgia and the South Sandwich Islands Visa & Passport 2026" arriva a 64), H1 "<Paese> entry requirements for British passport holders (2026): visa and passport validity", descrizione con la domanda sul visto. L'indice ha la colonna "Visa (short)".
- I cambi del testo dei visti vanno in `dati/passaporti_cambi.json` con `"sezione": "visa"` (l'indice mostra solo quelli della validità).

**Controlli nuovi in `verifica.py`** (tutti passati il 17/10, anche nel browser a 375 px con Barcellona ed Egitto): 8) ogni riassunto del visto è ricalcolato dallo schema sul testo salvato, deve corrispondere a un modello fisso e i suoi numeri devono stare nella frase FCDO; senza riassunto la pagina non ne mostra; 9) risposta diretta coerente con la regola e FAQ (JSON-LD e testo visibile) fatte solo di citazioni ufficiali intere, collegamenti a tutti gli aeroporti dello stesso Paese; 10) titoli ≤ 65 caratteri (salvo nessuna forma prevista più corta) e descrizioni ≤ 160 in tutte le pagine. Home, indici e pagine di servizio hanno titoli e descrizioni accorciati.

**Da fare / aperto.** Pubblicazione con il commit dopo la revisione indipendente; tra 2-4 settimane rileggere Search Console (posizione delle pagine liquidi e delle ricerche "visa"); riprovare gli esclusi (Ginevra e Varsavia aprendo le sezioni a fisarmonica, Parigi, Birmingham/Glasgow/London City); valutare uno schema in più per i visti all'arrivo (Maldive, Giappone) solo se la frase è inequivocabile.

**Revisione indipendente del 17/10/2026 (correzioni applicate, non pubblicate).**
- Visti: riletti dalla GOV.UK Content API tutti i 226 paesi (testo salvato = fonte, salvo differenze di soli a capo) e confrontati i 140 riassunti con la sezione intera. 16 riassunti corretti: tolti 5 (Australia e Arabia Saudita: il "visto" è un eVisitor/ETA; Aruba, Barbados, Filippine: senza visto ma con modulo/registrazione online obbligatoria prima del viaggio – embarkation card con "approval to travel", modulo online, e-travel con QR senza il quale le compagnie possono rifiutare l'imbarco); completati 11 (Taiwan: "for the reasons listed in the FCDO text"; 10 "You can visit X without a visa" senza durata nella prima frase – Antigua, Dominica, Falkland, Grenada, Giamaica, Paraguay, St Lucia, St Vincent, Gambia, Turks e Caicos – ora con "(the FCDO text says how long you can stay)"). Regole nuove in `raccolta/passaporti.py` (`AUTORIZZAZIONE_I` estesa, `VISTO_ELETTRONICO`, `SENZA_DURATA`) e controlli in `verifica.py`. Esito: 135 riassunti, 87 solo citazione, 3 senza sezione.
- Pagine passaporto: oltre al primo paragrafo sono visibili (non più chiusi nel riquadro apribile) i sottotitoli "Applying for …", ETA/autorizzazioni e moduli/arrival card (es. Australia eVisitor/ETA, USA ESTA, Egitto e-visa, Thailandia Digital Arrival Card); per i casi ETA/moduli la pagina dice il motivo per cui non riassume. Le 30 pagine Schengen hanno una riga su EES (pienamente operativo, nessuna azione prima del confine secondo GOV.UK) ed ETIAS (non in funzione) con il rimando alla pagina EES/ETIAS.
- Liquidi: ricontrollate con Playwright le 14 pagine nuove (tutte le frasi presenti parola per parola, regole giuste). Aena: la pagina generale non nomina nessun aeroporto e non dice che vale per tutti; ora la risposta in alto è "No, according to Aena's general hand-luggage page" (11 aeroporti), più due frasi della stessa pagina (una busta a persona; buste nelle vaschette). Praga: frasi rimesse nell'ordine della pagina (Terminal 1 / Terminal 2), riletta il 17/10. Düsseldorf: aggiunta la frase sui varchi normali (liquidi separati). Zurigo: etichetta "Depends on journey" (non dipende dal varco).
- FAQ: filtri più stretti (la busta solo se la frase parla di busta di plastica/richiudibile; terminal/varco solo se la frase nomina terminal, gate, aree, transfer, CT…) e frasi raggruppate col loro titolo (`intestazioni`: Zurigo, Francoforte, Berlino; frasi che finiscono con ":"); `faq_salta` per Zurigo e Linate. Tolte 13 risposte fuori tema (es. "plastic bag?" risposto con "Leave liquids in your cabin bag" a Heathrow/Edimburgo/Vienna; "terminal?" con frasi generiche su "the checkpoint" ad Aberdeen, Malta, USA; Zurigo con la regola transfer presentata come generale o col solo titolo). 132 risposte.
- Testi: sintesi di Monaco in inglese britannico ("litres"); titolo del riquadro eccezioni "Exceptions and other details (official)".
