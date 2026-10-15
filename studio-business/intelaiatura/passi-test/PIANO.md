# Test delle fonti: "Il passo è aperto oggi?" (EN + IT)

Periodo del test: **15 ottobre – 15 novembre 2026**. Avvio: 15/10/2026 alle 17:55 (prima lettura fatta).
Idea di partenza: `../ricerca-2026-10-14.md`, sezione 4 (idea N1).
File di questa cartella:

- `sonda.py`: lo script che legge le fonti. Usa solo la libreria standard di Python.
- `registro.jsonl`: una riga per ogni passo e per ogni fonte, a ogni lettura. Nessun HTML salvato.
- `domanda.json`: le prove della domanda (suggerimenti di Google) per i 40 passi scelti e per i 17 scartati.

---

## 1. In breve (giorno 1)

- **40 passi scelti** in base ai suggerimenti di Google (inglese USA e italiano).
- La sonda legge **9 fonti** in **circa 5 secondi** e scrive 50 righe (40 passi, 10 con una seconda fonte).
- Copertura del giorno 1, in tre livelli:

| Livello | Passi | Quali |
|---|---|---|
| A. Ente pubblico o gestore, stato scritto chiaro | 13 | Rombo, Valparola, Stalle (Bolzano); Agnello, Nivolet, Lombarda (Piemonte); Iseran, Galibier, Moncenisio, Madeleine, Piccolo San Bernardo (Savoia); Bonette (Alpes-Maritimes); Großglockner (GROHAG) |
| B. Ente pubblico, il passo è nella lista ufficiale ma il testo dice solo i divieti (es. "vietato ai rimorchi") | 6 | Stelvio, Gardena, Sella, Pordoi, Falzarego, Giovo (Bolzano) |
| C. TCS (Touring Club Svizzero: un club, non un ente pubblico), stato scritto chiaro | 12 | Gottardo, Furka, Bernina, San Bernardino, Susten, Grimsel, Novena, Flüela, Albula, Umbrail, Gran San Bernardo, Spluga |
| D. CCISS (Ministero): mostra **solo le chiusure**. "Aperto" vuol dire "nessuna chiusura segnalata" | 9 | Gavia, Giau, Rolle, Fedaia, Foscagno, San Pellegrino, Mortirolo, Manghen, Fauniera |

- Per Paese (fonte principale): **Italia 24 passi** (13 da enti con lista dei passi, 2 da TCS, 9 solo da CCISS); **Svizzera 10** (tutti da TCS); **Francia 5** (tutti da enti); **Austria 1** (gestore).
- **I 7 passi italiani più cercati**: Stelvio, Sella, Pordoi, Gardena e Rombo sono nella lista ufficiale della Provincia di Bolzano (5 su 7). **Gavia e Giau** hanno solo il CCISS, che segnala le chiusure ma non dice mai "aperto".
- **Senza il TCS e senza il CCISS** i passi coperti oggi sono **19 su 40**. Con il TCS diventano 31. Il test serve proprio a capire se TCS e CCISS sono affidabili durante le chiusure.

---

## 2. I 40 passi e le loro fonti

Domanda = numero di suggerimenti di Google con il nome del passo e una parola di stato (open, closed, today, opening, aperto, chiuso, oggi, domani…). EN: `hl=en gl=us`, query "`<passo> open`" e "`is <passo> open`". IT: `hl=it gl=it`, query "`<passo> aperto`" e "`<passo> chiuso`". Massimo 10 suggerimenti per query (20 per lingua). Esempi in `domanda.json` (es. "is stelvio pass open today", "passo gavia aperto oggi", "great st bernard pass open today", "colle del nivolet aperto oggi").

Lettura: **esplicita** = la fonte scrive "aperto/chiuso"; **implicita** = vedi livelli B e D sopra.

| # | Passo | Paese | Domanda EN / IT | Fonte principale | Lettura | Stato 15/10 | Seconda fonte (stato) |
|---|---|---|---|---|---|---|---|
| 1 | Passo dello Stelvio / Stilfserjoch | IT | 20 / 15 | Prov. Bolzano (RSS) | implicita | aperto | CCISS (aperto) |
| 2 | Passo del San Gottardo / Gotthardpass | CH | 20 / 5 | TCS | esplicita | aperto | - |
| 3 | Passo della Furka / Furkapass | CH | 20 / 1 | TCS | esplicita | aperto | - |
| 4 | Großglockner Hochalpenstraße | AT | 18 / 2 | GROHAG | esplicita | aperto | - |
| 5 | Passo del Bernina | CH | 13 / 6 | TCS | esplicita | aperto | - |
| 6 | Passo Gardena / Grödnerjoch | IT | 2 / 16 | Prov. Bolzano (RSS) | implicita | aperto | - |
| 7 | Passo del Rombo / Timmelsjoch | IT/AT | 14 / 4 | Prov. Bolzano (RSS) | esplicita | aperto | Timmelsjoch AG (aperto) |
| 8 | Passo di Gavia | IT | 4 / 10 | CCISS | implicita | aperto | - |
| 9 | Passo Giau | IT | 6 / 8 | CCISS | implicita | aperto | - |
| 10 | Colle del Gran San Bernardo / Grand-St-Bernard | IT/CH | 7 / 6 | TCS | esplicita | aperto | CCISS (aperto) |
| 11 | Col de l'Iseran | FR | 10 / 3 | Savoia | esplicita | aperto | - |
| 12 | Passo del San Bernardino | CH | 7 / 5 | TCS | esplicita | aperto | - |
| 13 | Col du Galibier | FR | 10 / 2 | Savoia | esplicita | aperto | Hautes-Alpes (aperto) |
| 14 | Passo dello Spluga / Splügenpass | IT/CH | 5 / 6 | TCS | esplicita | aperto | CCISS (aperto) |
| 15 | Passo del Susten / Sustenpass | CH | 9 / 2 | TCS | esplicita | aperto | - |
| 16 | Passo Rolle | IT | 4 / 6 | CCISS | implicita | aperto | - |
| 17 | Passo del Grimsel / Grimselpass | CH | 9 / 1 | TCS | esplicita | aperto | - |
| 18 | Passo Sella / Sellajoch | IT | 0 / 9 | Prov. Bolzano (RSS) | implicita | aperto | - |
| 19 | Passo Fedaia | IT | 1 / 8 | CCISS | implicita | aperto | - |
| 20 | Colle dell'Agnello / Col Agnel | IT/FR | 2 / 7 | Regione Piemonte | esplicita | aperto | Hautes-Alpes (aperto) |
| 21 | Passo Falzarego | IT | 1 / 7 | Prov. Bolzano (RSS) | implicita | aperto | CCISS (aperto) |
| 22 | Passo Valparola | IT | 1 / 7 | Prov. Bolzano (RSS) | esplicita | aperto | - |
| 23 | Passo del Foscagno | IT | 2 / 6 | CCISS | implicita | aperto | - |
| 24 | Colle del Nivolet | IT | 1 / 7 | Regione Piemonte | esplicita | **CHIUSO** (dal 15/10 ore 12 al 15/05/2027) | - |
| 25 | Passo Pordoi / Pordoijoch | IT | 1 / 6 | Prov. Bolzano (RSS) | implicita | aperto | - |
| 26 | Passo del Giovo / Jaufenpass | IT | 3 / 4 | Prov. Bolzano (RSS) | implicita | aperto | - |
| 27 | Passo San Pellegrino | IT | 1 / 6 | CCISS | implicita | aperto | - |
| 28 | Colle del Moncenisio / Col du Mont-Cenis | FR/IT | 3 / 4 | Savoia | esplicita | aperto | Regione Piemonte (aperto) |
| 29 | Passo della Novena / Nufenenpass | CH | 5 / 2 | TCS | esplicita | aperto | - |
| 30 | Passo del Flüela / Flüelapass | CH | 6 / 1 | TCS | esplicita | aperto | - |
| 31 | Col de la Bonette | FR | 5 / 2 | Alpes-Maritimes | esplicita | aperto | - |
| 32 | Passo Stalle / Staller Sattel | IT/AT | 1 / 6 | Prov. Bolzano (RSS) | esplicita | aperto | - |
| 33 | Passo del Mortirolo | IT | 1 / 5 | CCISS | implicita | aperto | - |
| 34 | Passo Manghen | IT | 1 / 5 | CCISS | implicita | aperto | - |
| 35 | Colle Fauniera (dei Morti) | IT | 1 / 5 | CCISS | implicita | aperto | - |
| 36 | Passo dell'Albula / Albulapass | CH | 4 / 2 | TCS | esplicita | aperto | - |
| 37 | Col de la Madeleine | FR | 6 / 0 | Savoia | esplicita | aperto | - |
| 38 | Passo Umbrail / Pass Umbrail | CH/IT | 3 / 2 | TCS | esplicita | aperto | - |
| 39 | Colle del Piccolo San Bernardo / Col du Petit-Saint-Bernard | IT/FR | 2 / 3 | Savoia | esplicita | aperto | CCISS (aperto) |
| 40 | Colle della Lombarda / Col de la Lombarde | IT/FR | 1 / 4 | Regione Piemonte | esplicita | aperto | Alpes-Maritimes (aperto) |

Scartati (domanda più bassa): Campolongo, Tonale, Passo delle Erbe, Tre Croci, Colle delle Finestre, Oberalp, Klausen, Izoard, Silvretta, Nockalmstraße, Cayolle, Vars, Croix de Fer, Sölkpass, Kaunertal. Scartati perché aperti tutto l'anno (nessuna chiusura da misurare): Maloja e Julier.
Il Bernina è aperto anche d'inverno, ma resta per la domanda alta: serve a verificare che la fonte non dica "chiuso" per sbaglio.

---

## 3. Le fonti (provate il 15/10/2026 dal server)

### Usate dalla sonda

| Fonte | Chi la pubblica | URL | Formato | HTTP | Dice aperto/chiuso? | Date di chiusura/apertura? |
|---|---|---|---|---|---|---|
| Passi e strade di montagna | Provincia autonoma di Bolzano, Centrale viabilità | `https://static-verkehr.provinz.bz.it/publications/rss/berg-und-passstrassen.xml` (+ `aktuelle-lage.xml` per gli avvisi del giorno) | RSS (XML), in tedesco | 200 | Sì, una voce per passo (20 passi). Oggi spesso solo divieti per i mezzi pesanti; si attende "Wintersperre" alla chiusura | A volte (es. Timmelsjoch "ogni giorno dalle 7 alle 20") |
| Cols en Suisse | TCS (club, dati da polizie cantonali e Viasuisse) | `https://www.tcs.ch/fr/tools/inforoute-situation-trafic/cols-en-suisse.php` | HTML statico, 77 passi | 200 | Sì ("ouvert / fermé" + icona), ora di aggiornamento | Sì, a volte (es. Gran San Bernardo: "chiusura invernale da lunedì 19 ottobre alle 8") |
| I colli alpini in Piemonte | Regione Piemonte / 5T (Muoversi in Piemonte) | `https://www.muoversinpiemonte.it/passes` | HTML con JSON interno (`__NEXT_DATA__`, campi `closed_from` / `closed_until`) | 200 | Sì | **Sì**: inizio e fine della chiusura (Nivolet: 15/10/2026 12:00 → 15/05/2027 12:00) |
| Inforoute 05 | Département des Hautes-Alpes | `https://www.inforoute05.fr/ws/geojson/fr/col/TODAY` | JSON | 200 | Sì (`etatCol`: OUVERT / FERME) | Sì, nel testo dell'evento ("fermée depuis le … jusqu'aux environs du …") |
| Savoie-Route | Département de la Savoie | `https://savoie-route.fr/api/v1/evenements/carto` (POST `{"id":5}`) + dettaglio `…/allDataCarto` (POST `{"idAll":<id>}`) | JSON (API del sito, senza login) | 200 | Sì (`Etat` 2 = verde/aperto, 0 = rosso; testo `FREtat`: OUVERT) | Solo la regola abituale nel commento (Iseran: "chiuso dal 1° lunedì di novembre al 2° venerdì di giugno") |
| Inforoutes 06 | Département des Alpes-Maritimes / Métropole Nice Côte d'Azur | `https://www.inforoutes06.fr/mod_turbolead/mod/inforoute/index.php?action=374&protect=1` | GeoJSON (codici "C14 Ouvert", "C14 fermé", "fermeture_hivernale") | 200 | Sì | Sì ("A partir du 14/10/26 10:00") |
| Großglockner Hochalpenstraße | GROHAG (società del Land Salisburgo / Carinzia) | `https://www.grossglockner.at/de` | HTML | 200 | Sì ("Aktueller Status für PKW: Geöffnet") | Solo orari e stagione ("da inizio maggio a inizio novembre") |
| Timmelsjoch Hochalpenstraße | Timmelsjoch Hochalpenstraße AG (gestore) | `https://www.timmelsjoch.com/` | HTML | 200 | Sì ("hat von 7 bis 20 Uhr geöffnet") | No |
| CCISS, situazione della viabilità | Ministero delle Infrastrutture (eventi di ANAS, Province, Veneto Strade, gestori) | `https://www.cciss.it/web/cciss/situazione-della-viabilita?p_p_id=2_WAR_ccissservizimapsportlet&p_p_lifecycle=2…&_2_WAR_ccissservizimapsportlet_so=44.0,6.6&…_ne=47.1,13.0&…_z=9` | JSON (richiesta della mappa per area) | 200 | **Solo "chiuso"** (67 chiusure oggi in tutte le Alpi italiane). Nessuna voce "aperto" | Sì, nel testo ("dalle 09:00 del 8 novembre 2025 alle 23:59 del …") |

### Provate e non usate

| Fonte | URL | Esito | Motivo |
|---|---|---|---|
| ANAS (Stelvio lato Lombardia, Gavia, Spluga, Foscagno, Tonale) | `https://www.stradeanas.it/it/le-strade/viabilita` | **000** (connessione chiusa dal server) | Non raggiungibile. Gli eventi ANAS arrivano comunque al CCISS |
| Svizzera, dati ufficiali (USTRA/ASTRA) | `https://api.opentransportdata.swiss/TDP/Soap_Datex2/TrafficSituations/Pull` | **401** | Serve un **token gratuito con registrazione** (account di Massimiliano). Non fatto |
| Cantone dei Grigioni | `https://strassen.gr.ch/` | 200 ma pagina "Request Rejected" | Blocco anti-robot |
| Trentino, viabilità | `https://viabilita.provincia.tn.it/`, `https://www.infomobilita.provincia.tn.it/` | **000** | Non raggiungibili. Gli eventi della Provincia di Trento arrivano al CCISS (fonte "Province") |
| Veneto Strade (Giau, Fedaia lato Belluno) | `https://www.venetostrade.it/myportal/VSSPA/home` | 200 | Portale solo JavaScript, nessun dato nel testo. Gli eventi arrivano al CCISS |
| CCISS, RSS | `https://www.cciss.it/rss` | 200 | Solo gli ultimi 100 avvisi di tutta Italia: troppo pochi |
| Alto Adige, app della Centrale viabilità | `https://verkehr.provinz.bz.it/json/traffic.json` | 404 | Sostituito dal feed RSS sopra (trovato nei dati del CMS del sito) |
| Inforoute 04 (Alpes-de-Haute-Provence) | `https://www.inforoute04.fr/mod_turbolead/mod/inforoute/index.php?action=374&protect=1` | 200 JSON | **Dati vecchi**: Cayolle "ouvert depuis le 21/11/25" mentre lo stesso giorno Inforoutes 06 annuncia il lato 04 chiuso per lavori dal 5 al 19/10. Esempio del rischio "aperto quando è chiuso" |
| Département de la Savoie, vecchio indirizzo | `https://www.savoie-route.fr/` | 000 | Il sito giusto è senza "www": `https://savoie-route.fr/` |
| alpen-paesse.ch | `https://www.alpen-paesse.ch/en/` | 200 | Concorrente privato, non è una fonte ufficiale |

---

## 4. Cosa fa la lettura giornaliera

**Comando** (dalla radice del repository):

```
python3 studio-business/intelaiatura/passi-test/sonda.py
```

- **Quando**: due volte al giorno, alle **9:00 e alle 17:00** (ora italiana), dal 15/10 al 15/11/2026. Due letture perché molte chiusure partono a mezzogiorno o la sera; a quelle ore non cadono le chiusure notturne (es. Furka chiusa dalle 18 alle 8).
- **Cosa fa**: scarica le 9 fonti in parallelo (timeout 25 secondi per fonte, 150 secondi in tutto; oggi ci mette circa 5 secondi). Per ogni passo e per ogni sua fonte aggiunge una riga a `registro.jsonl`:

```
{"date": "2026-10-15", "ts": "2026-10-15T17:55+0200", "pass": "nivolet", "status": "closed",
 "basis": "esplicito", "raw_snippet": "Colle del Nivolet: closed_from 15/10/2026 12:00 closed_until 15/05/2027 12:00",
 "source": "piemonte", "source_level": "ente", "source_url": "https://www.muoversinpiemonte.it/passes",
 "primary": true, "http": 200}
```

  - `status`: `open`, `closed` o `unknown` (fonte caduta, passo non trovato, testo non chiaro).
  - `basis`: `esplicito`, oppure `implicito (…)` (livelli B e D), oppure `errore`.
  - `raw_snippet`: massimo 240 caratteri di testo della fonte, per poter ricontrollare. Niente HTML.
  - `primary`: `true` per la fonte principale del passo, `false` per la seconda.
- **Se una fonte cade**, i suoi passi finiscono come `unknown` con il motivo, e le altre fonti vanno avanti. Lo script stampa "FONTE CADUTA …".
- **Dimensione**: circa 20 KB per lettura, circa 1,2 MB per tutto il mese.
- Dopo ogni lettura: `git add studio-business/intelaiatura/passi-test/registro.jsonl` e commit "Test passi: lettura gg/mm mattina|sera".
- **Riepilogo** in qualsiasi momento: `python3 studio-business/intelaiatura/passi-test/sonda.py --riepilogo` (per ogni passo e fonte: primo giorno "chiuso" e la sequenza A/C/?).
- **Prova senza scrivere**: aggiungere `--prova`.

---

## 5. Come si controlla la verità a fine test (16-20 novembre)

Per ogni passo si cerca **la notizia datata della chiusura** (o la conferma che è rimasto aperto):

1. **Comunicati ufficiali**: Provincia di Bolzano (comunicati stampa e "Wintersperre"), Provincia di Trento (ufficio stampa, comunicati della viabilità), ANAS (comunicati stampa), Veneto Strade e Provincia di Belluno, Regione Piemonte / Provincia di Cuneo / Città metropolitana di Torino, Regione Valle d'Aosta, Cantoni Vallese (vs.ch), Uri, Berna, Grigioni (gr.ch, "Passstrassen"), Ticino, Départements Savoie, Hautes-Alpes, Alpes-Maritimes, GROHAG e Timmelsjoch AG.
2. **Notizie locali con data**: ildolomiti.it, altoadige.it, salto.bz, Il Giorno Sondrio, La Provincia di Sondrio, valtellinamobile.it, aostasera.it, targatocn.it, 1815.ch, bluewin.ch, swissinfo.ch, Le Dauphiné, Nice-Matin, ORF Tirol / Salzburg.
3. Per ogni passo si scrive in una tabella: data e ora della chiusura secondo la notizia, link, primo "chiuso" nel registro (fonte principale e seconda fonte).

**Regole di confronto**:

- **Data giusta** = il primo "chiuso" nel registro cade **nello stesso giorno** della chiusura. Se la chiusura parte dopo la lettura delle 17:00, vale anche la lettura delle 9:00 del giorno dopo.
- **Errore grave** = una lettura dice `open` dopo l'ora di chiusura (anche se il `basis` è "implicito"). Le chiusure solo notturne non contano come chiusure del giorno.
- I passi che non chiudono nel mese (es. Sella, Gardena, Pordoi, Bernina, spesso Falzarego e Giovo) contano per la regola 4: non devono mai risultare "chiusi" senza una notizia di chiusura.
- Chiusure già annunciate da tenere d'occhio: Nivolet (15/10 ore 12, già vista dalla sonda il primo giorno), Gran San Bernardo (19/10 ore 8, annunciata dal TCS), Iseran (di solito il primo lunedì di novembre = 2/11), Großglockner (di solito inizio novembre).

---

## 6. Soglie (dalla ricerca del 14/10/2026). Se una soglia non passa → NO

| # | Soglia | Come si conta |
|---|---|---|
| 1 | Almeno **30 passi su 40** con stato leggibile da script da una fonte ufficiale | Un passo è coperto se la fonte è stata letta in almeno il 90 % delle letture **e** se, quando il passo ha chiuso, la fonte lo ha detto. Si danno due numeri: (a) solo enti pubblici e gestori; (b) contando anche il TCS. Il CCISS (livello D) conta solo per i passi di cui ha davvero segnalato la chiusura. Oggi: 19 (a), 31 (b), 40 con il CCISS ancora da provare |
| 2 | Almeno **5 dei 7 passi italiani più cercati** coperti (Stelvio, Gavia, Giau, Sella, Pordoi, Gardena, Rombo) | Stessa regola. Oggi 5 su 7 dalla Provincia di Bolzano; Gavia e Giau dipendono dal CCISS |
| 3 | **Data di chiusura giusta per almeno il 90 %** delle chiusure viste | Chiusure con data giusta / chiusure con notizia datata, sulla fonte principale |
| 4 | **Zero casi "aperto" quando era chiuso** | Anche un solo caso sulla fonte principale fa fallire il test. Si annotano anche i casi sulla seconda fonte |

Esito da scrivere alla fine in `../ricerca-2026-10-14.md`, sezione 4: PASSA / NON PASSA, con la tabella delle chiusure.

**Unico blocco aperto**: il token gratuito di opentransportdata.swiss (dati ufficiali svizzeri). Senza token la Svizzera dipende dal TCS. Se il TCS sbaglia anche una sola chiusura, per la Svizzera serve il token, cioè la registrazione di Massimiliano (5 minuti).
