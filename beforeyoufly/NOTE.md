# Before You Fly – note di lavoro

Costruito il 10/10/2026. Sito statico in inglese, generato da `genera.py` in `sito/` (272 pagine indicizzabili + 404).
Indirizzo previsto: `https://before-you-fly.netlify.app` (costante `URL_SITO` in `genera.py`, unico punto da cambiare).
Meta di Search Console: `GOOGLE_VERIFICA` in `genera.py` (stesso account degli altri siti), presente in ogni pagina.
Non pubblicato, nessun account creato. Pubblicazione Netlify: cartella `beforeyoufly/sito` (il file `sito/netlify.toml` contiene la regola `ignore`, così Netlify ricostruisce solo quando cambia questa cartella).

## Cosa contiene

| Sezione | Pagine | Fonte |
|---|---|---|
| Validità del passaporto (passaporto britannico) | indice con controllo e ricerca + 225 pagine paese | FCDO, GOV.UK Content API (`/api/content/foreign-travel-advice/<paese>`), OGL v3 |
| Liquidi in aeroporto (100 ml o 2 litri) | indice/tabella + 38 aeroporti + 2 regole nazionali (USA TSA, Canada CATSA) | pagina ufficiale di ogni aeroporto (o del gestore/autorità indicati) |
| EES / ETIAS | 1 pagina di stato | Commissione europea (home-affairs.ec.europa.eu) + GOV.UK (FCDO, Spagna, sezione "New Schengen entry requirements") |
| Servizio | home, about/fonti, contatti (Netlify Forms + honeypot), privacy, 404 (link assoluti, noindex) | – |

Riquadro affiliati: `dati/affiliati.json` (assicurazione, eSIM, parcheggi/lounge). Nascosto finché gli URL sono vuoti. Spazio pubblicità: `<div class="ad-slot">` vuoto (nascosto da CSS).

## File

| File | A cosa serve |
|---|---|
| `genera.py` | genera tutte le pagine; contiene il motore del controllo passaporto in Python e lo stesso in JS |
| `raccolta/passaporti.py` | scarica le 226 pagine FCDO, estrae la sezione "Passport validity requirements", classifica la regola, scrive `dati/passaporti.json`; se legge meno di 200 pagine non sovrascrive; registra i testi cambiati in `dati/passaporti_cambi.json` |
| `raccolta/liquidi.py` | ricontrollo mensile: per ogni aeroporto verifica che le frasi citate siano ancora sulla pagina ufficiale (`BYF_BROWSER=1` per i siti letti con il browser) |
| `raccolta/eesetias.py` | controlla che le frasi ufficiali su EES/ETIAS siano ancora presenti (esce con 1 se ne sparisce una, es. "ETIAS is currently not in operation") |
| `dati/passaporti.json` | 226 paesi: testo ufficiale parola per parola, regola riconosciuta (o `manuale` + motivo), data di aggiornamento della pagina, note di modifica |
| `dati/aeroporti.json` | regole sui liquidi lette a mano: frasi citate, eccezioni, regola, URL, data del controllo, modo di lettura; aeroporti esclusi con il motivo |
| `dati/ees_etias.json` | frasi ufficiali EES/ETIAS e GOV.UK con esito della ricerca, date di modifica delle pagine |
| `verifica.py` | 27 casi a mano, JS contro Python su 3.000 casi, link, fonti/date/citazioni, struttura, parole vietate, Playwright a 375 px |

## Passaporti: come si legge la regola (nessuna interpretazione)

- La regola diventa un calcolo SOLO se la frase FCDO corrisponde a uno di questi schemi: "expiry date at least / more than N months/days after the date you arrive", "valid for at least N months from the date you arrive", "... after the date you plan to leave", "expiry date after the day you plan to leave", "valid for the duration/length of your stay", Schengen e simili ("date of issue less than 10 years before the date you arrive" + "at least 3 months/90 days after the day you plan to leave"), Gibilterra ("issued within the previous 10 years ... at least 3 months after the day you intend to leave").
- Frasi riferite ad altri gruppi (residenti, titolari di visto, transito) non cambiano la regola per chi visita; vengono comunque mostrate nel testo ufficiale.
- Se la frase principale contiene "visa application", "visa expires", "Entry Permit", "recommend", "Up until", "valid on entry", "However", "usually", "plus an additional", oppure se il testo contiene un'altra regola diversa, o regole diverse per più territori: stato `manuale`, si mostra solo la frase ufficiale tra virgolette e il controllo dice di leggerla.
- Esito del 10/10/2026: **213 regole automatiche, 13 da leggere** (Afghanistan, Antartide (sezione vuota: nessuna pagina), Azerbaigian ("usually"), Bangladesh (rimanda al visto), Colombia ("valid on entry. However ... recommend"), Isole Cook/Tokelau/Niue (tre territori), Repubblica Dominicana ("Up until 31 December 2026"), Irlanda (nessuna sezione di validità: si cita "Passport and ID requirements"), Pakistan e Sierra Leone (dalla domanda di visto), Russia (dalla scadenza del visto), Georgia del Sud (Entry Permit + 4 settimane), Sant'Elena/Ascensione/Tristan da Cunha (territori diversi)). La ricerca del 10/10 parlava di 17 casi particolari: con lo schema attuale ne restano 13; gli altri (es. Israele 90 giorni, Costa Rica 1 giorno, St Lucia "dopo il giorno di uscita", Turchia 150 giorni, Cuba doppia condizione) hanno frasi esatte e sono calcolati.
- Ho controllato a occhio tutte le 213 regole riconosciute contro la frase ufficiale (elenco in `dati/passaporti.json`, campo `regola.frase`).
- Conteggio dei mesi: stesso giorno N mesi dopo; se il giorno non esiste, ultimo giorno del mese (31/8 + 6 mesi = 28/2 o 29/2). "More than" = almeno un giorno dopo. "Duration of stay" = non scade prima del giorno di partenza (scadenza il giorno stesso = valido). "Less than 10 years before the date you arrive" = emesso dopo lo stesso giorno di 10 anni prima (esattamente 10 anni = non valido). Margine sotto 7 giorni: il sito avvisa "Only just".

## Liquidi: aeroporti inclusi (38) e lettura

Tutti letti il 10/10/2026. Regola: 9 fino a 2 litri (LHR, LGW, EDI, BRS, DUB, VIE, FCO, LIN, KRK), 23 a 100 ml, 4 dipende dal varco/terminal (BER, MXP, PRG, OPO), 2 con pagine ufficiali in contraddizione (FRA, MUC).
- Lettura "diretta" (richiesta HTTP normale, 200): LHR, LGW, MAN, STN, LTN, EMA, ABZ, DUB, FRA, HEL, EIN, PRG, KRK, GOV.UK.
- Lettura con browser automatico (il sito blocca le richieste semplici o carica il testo con JavaScript): EDI, BRS, MUC, BER, VIE, FCO, LIN, MXP, ARN, GOT, MMX, CPH, LIS, OPO, FAO, FNC, Aena (MAD, BCN, AGP, PMI, ALC), IST, DOH, HKG, BNE, TSA, CATSA, Your Europe.
- Casi particolari:
  - **Francoforte**: la pagina "Security check" dice 2 litri alla maggior parte dei varchi del T1 e a tutti quelli del T3 (100 ml ai gate C1, C2, C4, C6, ai varchi transfer e speciali); il PDF "Flying with liquids is easy" collegato dalla stessa pagina dice ancora 100 ml. Mostrate entrambe, nessuna scelta nostra (consiglio prudente: 100 ml se non si può confermare).
  - **Monaco**: la pagina dice "Liquids (up to two liters per container)" con i CT, ma la didascalia delle foto dei CT sulla stessa pagina dice "liquids up to 100 ml". Trattata come Francoforte.
  - **Spagna**: nessuna pagina per aeroporto trovata; si usa la pagina di Aena (gestore di tutti gli aeroporti pubblici spagnoli), indicata come tale su ogni pagina.
  - **Hong Kong**: fonte = Civil Aviation Department (autorità), non il sito dell'aeroporto (non trovato).
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

## Calendario dei ricontrolli

| Cosa | Quando | Comando |
|---|---|---|
| Passaporti (226 pagine FCDO) | **ogni settimana** (lunedì) | `python3 -I beforeyoufly/raccolta/passaporti.py && python3 beforeyoufly/genera.py && python3 beforeyoufly/verifica.py` → se `passaporti_cambi.json` ha voci nuove, rileggere quelle pagine e i casi di `verifica.py` |
| EES / ETIAS | ogni settimana | `python3 -I beforeyoufly/raccolta/eesetias.py` (esce con 1 se una frase ufficiale sparisce: riscrivere la pagina a mano) |
| Liquidi (38 aeroporti + 2 nazionali) | **ogni mese** (1° lunedì), a mano | `BYF_BROWSER=1 python3 -I beforeyoufly/raccolta/liquidi.py`; per ogni "[CAMBIATA?]" o "[DA CONTROLLARE A MANO]": aprire la pagina, leggerla, aggiornare `dati/aeroporti.json` (frasi, regola, `controllato_il`), rigenerare e verificare. Provare anche gli esclusi. |

Limite Netlify (crediti gratuiti condivisi, vedi REGOLE-FISSE): ripubblicare al massimo una volta a settimana.

## Da fare per Massimiliano (quando decide di pubblicare)
1. Netlify: nuovo sito dalla cartella `beforeyoufly/sito` con nome `before-you-fly` (se il nome è preso, cambiare `URL_SITO` in `genera.py` e rigenerare).
2. Search Console: aggiungere la proprietà (la meta di verifica è già nelle pagine) e inviare `sitemap.xml`.
3. Notifiche email dei moduli Netlify.
