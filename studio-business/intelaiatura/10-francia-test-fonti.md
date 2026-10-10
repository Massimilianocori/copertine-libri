# Test tecnico delle fonti francesi per "Europe strikes today"

Data del test: **10 ottobre 2026** (download fatti dal server della sessione tra le 15:00 e le 15:20 UTC).
File scaricati: `francia/dl/` (non eseguiti: letti solo con `python3 -I`). Script di lettura: `francia/script/`.
Regola del test (STRATEGIA.md, sez. 4 punto 3): servono **almeno 3 fonti ufficiali, gratuite e leggibili in automatico**, che coprano **treni + trasporto urbano di Parigi + voli**.

---

## 0. Il punto principale, in breve

- In Italia abbiamo **un registro pubblico unico** (MIT) con tutti gli scioperi già proclamati, **10 o più giorni prima**.
- **In Francia questo registro non esiste.** Il preavviso sindacale (5 giorni "francs" nei servizi pubblici, art. L2512-2 Code du travail) va al datore di lavoro e **non viene pubblicato in un elenco ufficiale**. Non ho trovato nessun elenco pubblico dei preavvisi (né ministero, né transport.data.gouv.fr, né service-public).
- Le fonti ufficiali leggibili in automatico sono i **flussi di informazione ai viaggiatori** degli operatori. Lì lo sciopero compare **pochi giorni prima** (negli esempi di oggi: 2-3 giorni), di solito quando la legge obbliga a informare i passeggeri (24 ore prima).
- **Treni SNCF: sì, fonte ottima** (gratis, senza chiave, testo già anche in inglese).
- **Parigi (metro/RER/bus): solo con token gratuito PRIM**, che non ho potuto provare (serve un account con email e SMS). Senza token: solo un dataset IDFM di "bandi" (banner), oggi senza scioperi.
- **Voli: nessuna fonte ufficiale leggibile in automatico.** DGAC irraggiungibile dal server e senza un formato stabile; Eurocontrol, DSNA e NOTAM non hanno un'API pubblica aperta; Air France e Aéroports de Paris bloccano le richieste automatiche.
- Lo sciopero più importante delle prossime settimane per i turisti (**personale di volo, 17-21 ottobre 2026**, notizia di stampa del 19/09/2026) **non compare in nessuna fonte ufficiale leggibile in automatico**.

**Verdetto: NON PASSA** (dettagli nella sezione 2).

---

## 1. Tabella delle fonti

Legenda "Auto": sì = leggibile in automatico dal server oggi; parziale = leggibile ma con limiti seri; no = non leggibile o non adatto.

| # | Fonte (chi la pubblica) | URL esatto provato | HTTP dal server | Formato | Token / login | Licenza | Aggiornamento | Anticipo dello sciopero | Auto |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **SNCF Voyageurs – SIRI SX Lite** (TGV, Intercités, TER, OUIGO) | `https://proxy.transport.data.gouv.fr/resource/sncf-siri-lite-situation-exchange` | **200** (3,7 MB; un primo tentativo è stato interrotto, il secondo è andato) | XML SIRI | **nessuno** | ODbL (scheda SNCF `temps-reel-siri-sx-lite`) | ogni 2 minuti | 2-3 giorni negli esempi di oggi | **sì** |
| 2 | **SNCF Voyageurs – GTFS-RT Service Alerts** (stesso contenuto) | `https://proxy.transport.data.gouv.fr/resource/sncf-gtfs-rt-service-alerts` | **200** (990 KB) | Protobuf GTFS-RT | nessuno | ODbL | ogni 2 minuti | come sopra | **sì** (ma vedi nota 1) |
| 3 | SNCF – API Navitia (`api.sncf.com`) | `https://api.sncf.com/v1/coverage/sncf/disruptions` | **401** "no token" | JSON | **chiave gratuita** con registrazione su numerique.sncf.com/startup/api (150.000 richieste al mese, 5.000 al giorno, letto oggi) | condizioni d'uso API SNCF (non Licence Ouverte) | tempo reale | non provato (senza chiave) | parziale (non provato) |
| 4 | SNCF – pagine web info traffico / sciopero | `https://www.sncf-voyageurs.com/fr/voyagez-avec-nous/horaires-et-itineraires/info-trafic/` ; `https://www.sncf-connect.com/app/trafic` ; `https://www.ter.sncf.com/hauts-de-france/se-deplacer/info-trafic` | **403** (captcha anti-robot) | HTML | – | – | – | – | **no** |
| 5 | SNCF – portale open data (ricerca "grève") | `https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets?where="grève"` | 200 | JSON | nessuno | ODbL | – | nessun dataset sugli scioperi (163 dataset controllati; solo "Régularité mensuelle Transilien") | no |
| 6 | **IDFM – API PRIM "Info Trafic" (requête globale)** (metro, RER, bus, tram, Transilien) | `https://prim.iledefrance-mobilites.fr/marketplace/disruptions_bulk/disruptions/v2` | **401** "No API key found in request" | JSON (Navitia) | **token gratuito** con account IDFM Connect (verifica email + SMS), da generare in "mon jeton d'API" | Licence Mobilités (scheda IDFM su transport.data.gouv.fr) | tempo reale | **non verificato** (serve token) | parziale (non provato) |
| 7 | IDFM – API PRIM "messages affichés sur les écrans" (SIRI Lite general-message) | `https://prim.iledefrance-mobilites.fr/marketplace/general-message?LineRef=ALL` | **401** | XML/JSON SIRI | token gratuito PRIM | Licence Mobilités | tempo reale | non verificato | parziale (non provato) |
| 8 | IDFM – dataset "Messages d'actualité me-déplacer" (banner del sito/app IDFM) | `https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/actualites/records?limit=100` | **200** | JSON | **nessuno** | Licence Ouverte v2.0 (Etalab) | aggiornato oggi alle 15:10 UTC | oggi 1 solo messaggio (lavori del weekend); nessuno sciopero; storico non disponibile | parziale |
| 9 | RATP – pagine info traffico / mouvement social | `https://www.ratp.fr/infos-trafic` ; `https://www.ratp.fr/actualites/mouvement-social` | **403** (blocco anti-robot) | HTML | – | – | – | – | **no** |
| 10 | RATP Groupe – comunicati stampa "Prévisions à H-48" | `https://ratpgroup.com/fr/medias-et-publications/communiques-et-dossiers-de-presse/` + PDF tipo `https://ratpgroup.com/api/media/cp-previsions-a-h-48-mouvement-social-du-18-septembre-2025--16-septembre.pdf` | **200** / **200** | HTML + PDF | nessuno | non indicata | a evento | 48 ore | parziale: nel PDF i numeri delle linee sono **immagini**, il testo dice solo "Trafic normal / perturbé" |
| 11 | RATP open data | `https://data.ratp.fr/api/explore/v2.1/catalog/datasets?limit=100` | 200 | JSON | nessuno | Licence Ouverte | – | 16 dataset, nessuno su traffico o scioperi | no |
| 12 | **DGAC** (comunicati "préavis de grève", "demande de réduction de programme") su ecologie.gouv.fr | `https://www.ecologie.gouv.fr/` , `/presse` , `/rss.xml` | **000: connessione chiusa** (3 tentativi; anche WebFetch: dominio non risolto) | HTML | – | Licence Ouverte (sito del ministero) | a evento | in stampa: richieste di riduzione voli 1-2 giorni prima | **no** (non raggiungibile oggi; nessun comunicato 2026 trovato con la ricerca) |
| 13 | DGAC – SOFIA-Briefing (NOTAM: le riduzioni di voli passano dai NOTAM) | `https://sofia-briefing.aviation-civile.gouv.fr/sofia/pages/homepage.html` | 200 | HTML + JavaScript interno | per alcune funzioni login | – | – | – | **no** (nessuna API documentata; testo NOTAM tecnico) |
| 14 | DSNA – portale CDM | `https://cdm.dsna.fr/api/dsnatoday/` e `/api/warning/situationdsna/` → 200 ; `/api/warning/warnings/` → **401** "Auth token is not supplied" | 200 / 401 | JSON (API interna non documentata) | gli avvisi richiedono login professionale | non indicata | 5 minuti | solo ritardi e voli del giorno, nessun annuncio di sciopero | **no** |
| 15 | Eurocontrol NOP (Network Headline News) | `https://www.public.nm.eurocontrol.int/PUBPORTAL/gateway/spec/index.html` | 200 | applicazione GWT (niente dati nel HTML); `/rss` → 404 | B2B solo per professionisti registrati | – | – | – | **no** |
| 16 | Aéroports de Paris (ADP) | `https://www.parisaeroport.fr/` | **403** | HTML | – | – | – | – | **no** |
| 17 | Air France – pagina "mouvement social" / newsroom | `https://www.airfrance.fr/information/passagers/mouvement-social` ; `https://corporate.airfrance.com/fr/rss.xml` | **000** (errore HTTP/2) / **403** | HTML | – | – | – | – | **no** |
| 18 | Air France-KLM – API Flight Status | `https://api.airfranceklm.com/opendata/flightstatus` | **403** "Developer Inactive" (senza chiave) | JSON | chiave gratuita con registrazione su developer.airfranceklm.com (da fonti terze; non verificato) | condizioni AF-KLM | tempo reale | solo voli già cancellati, solo AF/KLM | parziale (non provato; non è un annuncio di sciopero) |
| 19 | Transavia | `https://www.transavia.com/fr-FR/service/informations-voyage/` | **403** | HTML | – | – | – | – | no |
| 20 | **Eurostar – GTFS-RT** (alert + ritardi) | `https://integration-storage.dm.eurostar.com/gtfs-prod/gtfs_rt_v2.bin` | **200** (333 KB) | Protobuf GTFS-RT | nessuno | Licence Ouverte v2.0 (scheda su transport.data.gouv.fr) | tempo reale | 2 giorni nell'esempio di oggi | **sì** (opzionale) |
| 21 | service-public.fr (actualités) | `https://www.service-public.fr/particuliers/actualites` | 200 | HTML | nessuno | Licence Ouverte | – | nessuna informazione su scioperi | no |
| 22 | Légifrance (testi di legge) | `https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006902590` | **403** | HTML | – | – | – | (solo per verificare le regole) | – |

Nota 1. Nel GTFS-RT SNCF il campo "causa" non è mai STRIKE (459 avvisi: 232 MAINTENANCE, 69 OTHER, 158 vuoti). Nel SIRI SX il campo motivo è sempre vuoto (521 avvisi, `UndefinedReason` vuoto). **Lo sciopero si riconosce solo dal testo** ("Mouvement social", "grève", in inglese "Labour strike"). Il SIRI SX conteneva anche lo sciopero locale della Normandia, che nel GTFS-RT non ho trovato: **il SIRI SX è più completo**.

Nota 2. I blocchi 403 e le connessioni chiuse sono stati misurati dal server di questa sessione. Da GitHub Actions il risultato può essere diverso (in meglio o in peggio), ma i siti con captcha (SNCF Connect, RATP, ADP) bloccano tutti i server per scelta.

---

## 1b. Esempi reali scaricati oggi (10/10/2026)

**A. SNCF SIRI SX – sciopero locale Normandia (treni Paris Saint-Lazare ↔ Normandia)**
```
CreationTime 2026-10-07T12:09:42Z   ParticipantRef NOR
ValidityPeriod 2026-10-07T14:09+02:00 → 2026-10-11T02:00+02:00
Summary FR "Mouvement social local"   Summary EN "Local social movement"
Detail EN "Train service will operate normally on most of the NOMAD network on Friday,
October 9, and Saturday, October 10. Disruptions are expected on routes between
Paris St. Lazare and Normandy due to a local labour strike. ... starting at 5 p.m. the day before."
```
Pubblicato il 7 ottobre per uno sciopero del 9-10 ottobre: **2 giorni di anticipo**.

**B. SNCF SIRI SX / GTFS-RT – sciopero delle ferrovie belghe (treni transfrontalieri Hauts-de-France)**
```
CreationTime 2026-10-09T14:10:19Z   ParticipantRef NPC
ValidityPeriod 2026-10-09T16:10+02:00 → 2026-10-12T00:00+02:00
Summary EN "Labour strike in Belgium on Monday, October 12, 2026"
Detail EN "A SNCB labour strike will disrupt cross-border TER Hauts-de-France service on
Monday, October 12, 2026, on the following lines: Lille Flandres–Kortrijk (K80),
Maubeuge–Charleroi (K82), Lille Flandres–Tournai (P81)"
```
Pubblicato il 9 ottobre per il 12 ottobre: **3 giorni di anticipo**. Confronto con la stampa: Paris Match Belgique aveva confermato lo sciopero il 3 ottobre (6 giorni prima del flusso SNCF).
Attenzione: il **periodo di validità del messaggio non coincide con il giorno dello sciopero** (il messaggio scade l'11/10 a mezzanotte, lo sciopero è il 12/10). La data vera è solo nel testo.

**C. Eurostar GTFS-RT**
```
header EN "Cancelled 9141 and 9148 train·s on the Eurostar network on 12/10/2026"
desc   EN "Due to strike action on the Eurostar network, your train is cancelled. ..."
```
Anche qui: campo causa vuoto, sciopero riconoscibile solo dal testo; data nel testo (formato gg/mm/aaaa).

**D. IDFM "actualites" (senza chiave)**
```
id "weekend1011", type "0" (0 = crise), title "🚧 Travaux du week-end",
createddate 2026-10-09T12:00:37+0000
```
Oggi nessun messaggio di sciopero. Il dataset mostra solo i banner attivi, senza storico: non ho potuto verificare come appare uno sciopero.

**E. RATP – PDF "Prévisions de trafic à 48 heures" (18 settembre 2025, pubblicato il 16)**
```
Mouvement social le jeudi 18 septembre 2025 – Prévisions de trafic à 48 heures
Métro : Trafic normal / Trafic perturbé et assuré uniquement aux heures de pointe / ...
```
I numeri delle linee sono icone: il testo estratto non dice quale linea è in quale stato.

**F. Voli** – nessun esempio: nessuna fonte ufficiale leggibile in automatico ha restituito dati sugli scioperi.

---

## 1c. Scioperi delle prossime settimane: stampa contro fonti ufficiali

| Sciopero (stampa) | Fonte di stampa | Compare in una fonte ufficiale automatica? |
|---|---|---|
| Personale di volo (piloti e assistenti di volo, intersindacale UNSA PNC, SNPNC-FO, SNGAF, SNPL, UNAC), **17-21 ottobre 2026**, Air France, Transavia, Corsair e altri | air-journal.fr (19/09/2026), deplacementspros.com, ulysse.com, tourmag.com ("potrebbe non avere luogo") | **No.** Nessuna fonte aerea leggibile; i siti di Air France e Transavia bloccano il server. |
| Sciopero delle ferrovie belghe (SNCB), **12 ottobre 2026**: treni transfrontalieri e Eurostar | parismatch.be (03/10 e 08/10/2026) | **Sì**: SNCF SIRI SX e GTFS-RT (dal 9/10), Eurostar GTFS-RT |
| Sciopero locale SNCF Normandia, **9-10 ottobre 2026** | non trovato in stampa (trovati solo episodi di luglio e agosto 2026) | **Sì**: SNCF SIRI SX (dal 7/10) |
| Sciopero dei controllori di volo a inizio ottobre | la stampa parla del preavviso SNCTA del 7-9 ottobre **2025**, poi sospeso; per ottobre 2026 nessun preavviso trovato | – |
| RATP / Parigi a ottobre 2026 | nessuno sciopero trovato (l'ultimo: 29 settembre 2026, RER C, D, E e Transilien) | non verificabile (PRIM richiede token) |
| "Mobilitazione generale" del 5 novembre 2026 | connexionfrance.com (calendario; possibile confusione con il 2025) | non ancora (troppo presto per i flussi degli operatori) |

---

## 1d. Le regole francesi sui tempi (perché l'anticipo è breve)

- **Preavviso nei servizi pubblici**: 5 giorni "francs" prima dello sciopero, presentato dal sindacato al datore di lavoro (art. L2512-2 Code du travail; testo letto tramite travail-industrie.com e fonti sindacali; Légifrance bloccato dal server). **Non è pubblicato in un registro.**
- **Trasporti terrestri (legge del 21 agosto 2007 sul "service minimum")**: prima del preavviso c'è una procedura di "alarme sociale" (in tutto circa 13 giorni secondo l'Assemblée nationale); ogni dipendente deve dichiarare **48 ore prima** se sciopera (art. L1324-7 Code des transports); l'azienda deve dare ai viaggiatori il piano dei trasporti **al più tardi 24 ore prima** (regola confermata da FNAUT e da una domanda al Senato del 2022; numero di articolo L1222-8 non letto direttamente perché Légifrance blocca il server).
- **Trasporto aereo ("loi Diard" del 19 marzo 2012)**: dichiarazione individuale **48 ore prima** (art. L1114-3) e informazione ai passeggeri **al più tardi 24 ore prima** (art. L1114-7, citato dalla Corte di cassazione). I controllori di volo: le riduzioni dei voli sono chieste dalla DGAC alle compagnie tramite NOTAM, di solito 1-2 giorni prima.
- **Conseguenza**: con le fonti ufficiali si può pubblicare con **1-3 giorni di anticipo** (contro i 10+ giorni dell'Italia). Le pagine "france strikes october 2026" o "this week" avrebbero dati ufficiali solo a ridosso dello sciopero; le date annunciate settimane prima esistono solo nella stampa e nei comunicati sindacali.

---

## 2. Verdetto: **NON PASSA**

Perché:
1. **Voli: zero fonti ufficiali leggibili in automatico.** La DGAC non ha un feed (sito del ministero irraggiungibile oggi, nessun comunicato 2026 trovato, formato HTML libero); Eurocontrol NOP, DSNA e i NOTAM non hanno un'API pubblica aperta; ADP, Air France e Transavia bloccano i server. L'API Air France-KLM vede solo i voli già cancellati di AF/KLM.
2. **Parigi: solo con token PRIM**, gratuito ma non provato (serve un account IDFM Connect con email e numero di cellulare per l'SMS: lo deve creare Massimiliano). La fonte senza chiave (banner IDFM) oggi non contiene scioperi e non ha storico; RATP blocca il server.
3. **Treni: sì.** Il SIRI SX SNCF è eccellente: gratis, senza chiave, aggiornato ogni 2 minuti, ODbL, testo già tradotto in inglese dalla SNCF.
4. **Nessun registro centrale degli scioperi**: anche dove i dati ci sono, lo sciopero appare 2-3 giorni prima, e solo nel testo (nessun campo "sciopero", date dentro le frasi).

Conteggio: fonti ufficiali gratuite **sicuramente** leggibili oggi = SNCF SIRI SX (e la sua copia GTFS-RT), Eurostar GTFS-RT, IDFM banner (parziale). Coprono **treni**, non Parigi in modo affidabile, **non i voli**. La condizione "≥3 fonti che coprono treni + Parigi + voli" non è soddisfatta.

---

## 3. (Se passasse) – non applicabile

Non applicabile, perché il test non passa. Lo schema dei dati e la stima delle ore per la via parziale sono nella sezione 4.

---

## 4. Cosa manca e via parziale possibile

**Cosa manca**
- Una fonte ufficiale e automatica per i **voli** (scioperi dei controllori di volo e del personale delle compagnie). Oggi non esiste.
- Un **token PRIM** per Parigi (si ottiene gratis, ma serve l'account di Massimiliano; poi va provato con un vero giorno di sciopero).
- Un **calendario anticipato** (settimane prima): in Francia esiste solo nella stampa e nei siti sindacali, cioè non è una fonte ufficiale.

**Via parziale (da decidere con Massimiliano; non rispetta la regola della strategia)**
"France train & Paris transit strikes" = SNCF SIRI SX + PRIM (token) + Eurostar GTFS-RT, con i voli **esclusi** o gestiti a mano dalla routine settimanale con link ai comunicati.

Schema dei dati comune (per ogni messaggio):
`id_fonte` (es. SituationNumber), `fonte` (sncf-sx / prim / eurostar), `operatore` (SNCF Voyageurs, TER Normandie = ParticipantRef NOR, RATP, Eurostar), `modo` (treno / metro / RER / bus / tram), `ambito` (nazionale / regionale / linea), `linee_o_treni` (numeri treno o linee), `citta` (Paris, Lille... da regole fisse), `data_inizio_sciopero`, `data_fine_sciopero` (dal testo), `pubblicato_il` (CreationTime), `valido_dal` / `valido_fino` (ValidityPeriod: solo visualizzazione), `titolo_en`, `testo_en` (SNCF ed Eurostar lo danno già), `titolo_fr`, `testo_fr`, `stato` (annunciato / in corso / concluso / sparito dal flusso), `link_ufficiale`.

Stima del lavoro (via parziale):
- Lettore SIRI SX SNCF, filtro "Mouvement social / grève / strike", estrazione date dal testo, storico come per il MIT: **8-10 ore**.
- Lettore PRIM (dopo il token) con prova su un giorno di sciopero vero: **6-8 ore**.
- Eurostar GTFS-RT (decodificatore già scritto per questo test): **2-3 ore**.
- Pagine Francia nel generatore (oggi/domani/settimana, Parigi, 5-6 città, guide, link): **12-16 ore**.
- Prove e workflow GitHub Actions: **4-6 ore**.
- Totale: **circa 32-43 ore**, voli esclusi.

Rischi:
- **Date solo nel testo**: le frasi cambiano ("le lundi 12 octobre", "les vendredi 9 et samedi 10 octobre", "12/10/2026"); servono regole fisse e un controllo, altrimenti si pubblicano date sbagliate.
- **Il periodo di validità non è il giorno dello sciopero** (esempio belga): non va usato come data.
- **Anticipo breve (2-3 giorni)**: le query "october 2026" e "this week" troverebbero pagine quasi vuote fino a pochi giorni prima.
- **Token PRIM**: ne esiste uno per account; generarne uno nuovo annulla il vecchio; limite di 1.000 richieste al giorno per i token recenti (dato letto tramite ricerca, pagina PRIM bloccata dal server). Va salvato come secret di GitHub.
- **Licenze**: ODbL (SNCF) obbliga a citare la fonte e a ridistribuire con la stessa licenza i dati derivati (il nostro `vista.json` pubblico); Licence Mobilités (IDFM) ha regole simili. Da scrivere nella pagina About.
- **Formati**: il flusso SNCF è dichiarato "prima pubblicazione"; il proxy transport.data.gouv.fr oggi ha chiuso una connessione al primo tentativo (serve un secondo tentativo automatico).
- **Lingua**: SNCF ed Eurostar danno già l'inglese; per PRIM e RATP il testo è solo in francese (regole fisse come per l'Italia).

**Consiglio**: non costruire l'hub Francia adesso. Se si vuole tenere aperta la porta: (1) Massimiliano crea l'account PRIM e il token; (2) un piccolo lettore SIRI SX SNCF raccoglie in silenzio per 4-6 settimane, così si misura quanti scioperi compaiono e con quanto anticipo; (3) si ripete il test voli dopo uno sciopero dei controllori di volo, per vedere se la DGAC pubblica qualcosa in un formato stabile.

---

## Fonti di stampa e documenti usati
- air-journal.fr, 19/09/2026: https://www.air-journal.fr/2026-09-19-reforme-du-cumul-emploi-retraite-les-pilotes-et-personnels-de-cabine-appeles-a-la-greve-du-17-au-21-octobre-5277588.html
- deplacementspros.com: https://www.deplacementspros.com/transport/aerien-les-pnc-appellent-a-5-jours-de-greve-nationale-du-17-au-21-octobre-2026
- tourmag.com: https://www.tourmag.com/Aerien-le-preavis-de-greve-nationale-pourrait-il-etre-leve_a133542.html
- parismatch.be, 03/10/2026: https://www.parismatch.be/actualites/economie/2026/10/03/un-mouvement-de-greve-sur-le-rail-confirme-le-12-octobre-4JEXFBCAHBF43ILS7HL25R6XKM/
- parismatch.be, 08/10/2026: https://www.parismatch.be/actualites/societe/2026/10/08/manifestation-nationale-de-ce-vendredi-9-et-greve-du-lundi-12-octobre-voici-les-perturbations-prevues-UYOXOP5T35FNHJWH26HMKJXTMQ/
- sortiraparis.com (29/09/2026): https://www.sortiraparis.com/en/news/in-paris/articles/352813-strike-on-september-29-three-rer-lines-and-two-transilien-lines-disrupt-traffic-forecasts
- lechotouristique.com (riduzioni DGAC via NOTAM): https://www.lechotouristique.com/article/greve-du-controle-aerien-quels-vols-sont-maintenus
- PRIM, quote dell'API disruptions_bulk (tramite ricerca): https://prim.iledefrance-mobilites.fr/en/apis/idfm-disruptions_bulk
- Art. L2512-2 Code du travail: https://travail-industrie.com/code-du-travail/l2512-2
- L1324-7 (48 ore, legge 2007): https://ledroitouvrier.cgt.fr/IMG/pdf/201306_juris_basic.pdf ; L1114-7 (aereo, 24 ore): https://www.labase-lextenso.fr/jp-commente/cc/2021-09/19-21-025-CC-08092021-19_21025 ; 24 ore ai viaggiatori (terra): https://fnaut.fr/uploads/2018/03/180322loep.pdf , https://www.senat.fr/questions/base/2022/qSEQ220700931.html
