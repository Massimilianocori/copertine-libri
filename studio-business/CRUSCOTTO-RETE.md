# Cruscotto della rete di siti

Aggiornato da Claude ogni mercoledì (routine "Ricerca settimanale") e quando arrivano numeri nuovi. Metodo e soglie: `.claude/skills/rete-siti/SKILL.md`.
Regola: ogni numero ha data e fonte. Se un numero manca, si scrive "manca". Le stime non sono numeri.

Ultimo aggiornamento: 14/10/2026 (revisione del mercoledì).

## 1. I siti

| Sito | Indirizzo | Online dal | Lingua e pubblico | Come guadagnerà | Fase |
|---|---|---|---|---|---|
| Italy Strikes Today | https://italy-strikes-today.netlify.app | 10/10/2026 | EN + IT, turisti in Italia | Pubblicità, affiliati viaggio, avvisi | Avvio |
| Tourist Tax Calculator | https://tourist-tax-calculator.netlify.app | 10/10/2026 | EN, viaggiatori in Europa | Pubblicità, affiliati hotel | Avvio |
| Visa Income Checker | https://visa-income-checker.netlify.app | 10/10/2026 | EN, chi si trasferisce (nomadi digitali, pensionati) | Pubblicità, affiliati (assicurazioni, conti) | Avvio |
| Before You Fly | https://before-you-fly.netlify.app | 11/10/2026 | EN, chi vola in Europa | Pubblicità, affiliati (voli, eSIM) | Avvio |
| EsameB1 | https://esameb1.netlify.app | 09/10/2026 | IT, stranieri per la cittadinanza | Pubblicità, contatti per scuole (dopo il cancello fiscale) | Avvio |
| EsamiDiStato | https://esamidistato.netlify.app | 10/10/2026 | IT, neolaureati | Pubblicità, corsi di preparazione (affiliati) | Avvio |

Archiviati (non fanno parte della rete): orelab (abbandonato, vedi REGOLE-FISSE), BandiChiari.

## 2. Numeri

| Data | Sito | Pagine indicizzate | Impressioni (28 gg) | Clic (28 gg) | Visite (contatore) | Iscritti | Fonte |
|---|---|---|---|---|---|---|---|
| 11/10/2026 | tutti | manca | manca | manca | nessun contatore | 0 | Netlify Forms (i 2 invii del 9/10 sono test) |
| 12/10/2026 | EsameB1 | manca | **> 0 dal 9/10** (primo segnale: Google lo mostra già in alcune ricerche) | manca | nessun contatore | 0 | Email di Search Console dell'11/10 |
| 12/10/2026 | EsameB1 | manca | manca | manca | nessun contatore | **1 (primo iscritto vero)**: arrivato da Google, città Genova | Netlify Forms + email di notifica |
| 14/10/2026 | tutti | manca | manca | manca | nessun contatore | EsameB1 1, EsamiDiStato 0, Italy Strikes 0 (alerts, contact, business) | Netlify Forms; nessuna email nuova di Search Console o affiliati dal 12/10 |

## 2b. Stima dei ricavi a 18 mesi (14/10/2026). Sono stime, non numeri: si rifanno con i dati veri.

| Sito | Prudente €/anno | Ottimista €/anno | Fonte della stima |
|---|---|---|---|
| Italy Strikes (EN + IT + satelliti) | 2.500 | 11.000 | STRATEGIA sez. 6, classifica 19 |
| Tourist Tax Calculator | 1.000 | 4.500 | classifica 19 |
| Visa Income Checker | 600 | 3.000 | classifica 19 |
| Before You Fly | 800 | 3.400 | classifica 19 (liquidi + passaporti) |
| EsameB1 | 500 | 3.500 | studi EsameB1 (l'ottimista comprende i contatti per le scuole, dopo il cancello fiscale) |
| EsamiDiStato | 500 | 2.500 | studi EsamiDiStato |
| Case all'asta (da costruire) | 500 | 3.000 | affari-test-fonti (primo anno 0-1.000) |
| Passi alpini (da testare) | 800 | 2.500 | ricerca-2026-10-14 |
| **Totale se tutti funzionano** | **7.200** | **33.400** | |
| **Realistico** (di solito metà dei siti passa) | **5.000** | **12.000** | |

A 12 mesi: realistico 1.000-4.000 €. Cifre lorde, prima di tasse e contributi. Libri KDP esclusi.

## 3. Decisioni per sito

| Sito | Prossimo controllo | Soglia di quel controllo | Decisione attuale |
|---|---|---|---|
| Italy Strikes Today | 9/11 (30 gg) e 24/11 (45 gg) | ≥ 300 impressioni al mese a 45 gg | Continua. Sito stagionale: picco scioperi a marzo, verdetto a 90 gg da rileggere anche a marzo 2027 |
| Tourist Tax Calculator | 9/11 e 24/11 | ≥ 300 impressioni al mese a 45 gg | Continua. Tariffe da rigenerare il 1/1/2027 (vedi `touristtax/NOTE.md`) |
| Visa Income Checker | 9/11 e 24/11 | ≥ 300 impressioni al mese a 45 gg | Continua. Cambi aggiornati dal workflow di Italy Strikes |
| Before You Fly | 10/11 e 25/11 | ≥ 300 impressioni al mese a 45 gg | Continua |
| EsameB1 | 8/11 e 23/11 | ≥ 300 impressioni al mese a 45 gg | Continua |
| EsamiDiStato | 9/11 e 24/11 | ≥ 300 impressioni al mese a 45 gg | Continua. Domanda stagionale (sessioni d'esame): leggere i numeri vicino alle scadenze |

## 4. Lavori in sospeso

- **Restyling:** voti della seconda revisione ≥ 8/10 per 5 siti. EsamiDiStato era a 7,5: 4 correzioni fatte l'11/10 (commit f3e0ff1), da rivotare. Uscite:
  - Italy Strikes con la pubblicazione del 17/10;
  - EsameB1 ed EsamiDiStato con la routine del lunedì;
  - i tre siti di viaggio con un deploy ciascuno, appena si vedono i consumi Netlify.
- **Dati strutturati EsameB1:** Search Console (email del 10/10) segnala 4 campi mancanti negli eventi, non critici. `endDate` e `image` sono già nel generatore e escono con la prossima pubblicazione. `performer` e `offers` restano: non critici, si aggiungono solo con dati certi (costo dell'esame per ente).
- **Crediti Netlify:** manca la foto della pagina Usage/Billing. L'11/10 tutti i siti hanno dato 503 per crediti esauriti.

## 5. Misurazione (il punto da risolvere per primo)

- [ ] Massimiliano crea l'account GoatCounter (gratis) e dice il nome scelto. Ha detto che lo farà, senza fretta (11/10).
- [ ] Script GoatCounter nei 6 siti, insieme alle pubblicazioni già previste, e privacy aggiornata in ogni sito.
- [ ] Chiave API in sola lettura tra i segreti dell'ambiente, così le routine leggono le visite da sole.
- [ ] Fino ad allora: foto di Search Console ("Rendimento" e "Pagine") ogni 2 settimane. Prima richiesta: 23/10.

## 6. Prossime azioni (una per settimana, la più utile)

| Settimana | Azione | Perché (numero) | Stato |
|---|---|---|---|
| 14/10 | Attivare la misurazione (sez. 5) | Oggi 0 numeri su 6 siti: senza misura non si decide | In attesa dell'account di Massimiliano |
| 21/10 | Primo sito con segnali (EsameB1): verificare dopo la pubblicazione del 15/10 che le pagine nuove (costo, risultati) siano lette da Google | Unico sito con un iscritto vero e impressioni dal 9/10 | Programmata |

## 7. Affiliazioni

| Programma | Stato | Data | Prossimo passo |
|---|---|---|---|
| SafetyWing Ambassador | Attivo, link nel sito | 10/10/2026 | Nessuno |
| Airalo (Impact) | **Respinto** ("non è il momento giusto", porta aperta) | 12/10/2026 | Ripresentare la domanda quando un sito supera 1.000 visite al mese, con i numeri |
| Travelpayouts (Omio, Welcome Pickups, EKTA) | Account approvato, sito da verificare | 10/10/2026 | In pausa: la verifica chiede uno script con cookie di tracciamento, non compatibile con la privacy attuale senza banner dei cookie |

## 7a. Idee in cantiere (si portano avanti ogni settimana)

| Idea | Stato | Prossimo passo | Data |
|---|---|---|---|
| Sito "affari": case all'asta (Portale Vendite Pubbliche) con lo sconto rispetto ai valori OMI di zona | **Test fonti 14/10: case PASSA** (18.023 lotti immobiliari attivi, sconto calcolabile su valori OMI CC BY 4.0), con riserva sulla concorrenza (immobiliare, casa.it, idealista ripubblicano le aste). **eBay NON PASSA** (API solo per partner approvati, annunci da aggiornare ogni 6 ore, commissioni 1-4%). Primo anno realistico 0-1.000 € (`intelaiatura/affari-test-fonti.md`) | Decisione di Massimiliano: costruire o no. Se sì: download OMI con SPID (10 min) e verifica della commissione MutuiSupermarket su Awin | 14/10 |
| Zone a basse emissioni in Europa | **Chiusa come sito** (14/10, 4ª valutazione): urbanaccessregulations.eu, green-zones e autoviatest già primi su Google; dati francesi vecchi (BNZFE del 26/3/2026), fonte tedesca UBA sparita (404). Stima 0,4-1,8k €/anno a 18 mesi | Nessuno. Al massimo 3-5 pagine dentro "Passi alpini", se quella passa | 14/10 |
| Richiami auto (NHTSA, DVSA, Safety Gate) | **Chiusa** (14/10): dati ottimi (API e CSV ufficiali aggiornati ogni giorno), ma clearvin e gli strumenti ufficiali occupano Google, e un "nessun richiamo" sbagliato è un rischio per la sicurezza. Stima 0,3-1,5k €/anno a 18 mesi | Nessuno (si riapre solo con un registro UE unico e aperto dei richiami auto) | 14/10 |
| Incentivi auto elettriche | **Chiusa** (14/10): una sola API solo per gli USA (AFDC); in Europa le fonti sono sparse. Google occupato da recharged, Autotrader e giornali; "sei idoneo" ha effetti economici. Stima 0,2-1k €/anno a 18 mesi | Nessuno | 14/10 |
| **Passi alpini aperti oggi?** (Stelvio, Gavia, Giau, Sella, Grossglockner, Galibier… EN + IT, motore di Italy Strikes) | **Proposta** (idea nuova del 14/10, `intelaiatura/ricerca-2026-10-14.md`). Domanda forte EN/IT ("stelvio pass open today", "passo gavia aperto oggi/domani"); nessuna pagina con lo stato di oggi per i passi italiani (solo notizie vecchie e forum); concorrente solo per i 26 passi svizzeri. Stima 0,3-1,2k € a 12 mesi, 0,8-2,5k €/anno a 18 mesi; 20-30 ore | Test delle fonti 15/10-15/11 durante le chiusure invernali. Soglie: ≥ 30 passi su 40 leggibili da fonte ufficiale; ≥ 5 dei 7 passi italiani più cercati; data di chiusura giusta ≥ 90 %; zero "aperto" quando era chiuso. Se passa: costruzione a febbraio-marzo 2027 e soglia di 300 impressioni al mese entro il 15/6/2027. Da Massimiliano: token gratuito opentransportdata.swiss (5 minuti) | 14/10 |
| Prezzi carburanti (UK Fuel Finder, bollettino UE) | **Chiusa** (14/10): fuel-prices.eu, stationwatch, petrolfinder e Google Maps già coprono | Al massimo un riquadro dentro "Passi alpini" | 14/10 |

## 7b. Idee a pagamento in attesa (decisione di Massimiliano del 12/10: "da fare, adesso non è urgente")

Si riprendono solo quando la soglia è raggiunta. Prima vengono i libri KDP già in coda con voto 9.

| Idea | Come si incassa | Soglia per riprenderla | Cosa serve |
|---|---|---|---|
| Libro Kindle "Esame B1 cittadinanza: guida e prove" con link da EsameB1 | Diritti d'autore Amazon (niente vendite dirette) | EsameB1 ≥ 1.000 visite al mese oppure ≥ 30 iscritti, e coda libri KDP con voto 9 smaltita | Foto BookBeam di 2-3 ricerche ("esame B1 cittadinanza", "CILS B1 cittadinanza", "test italiano cittadinanza"), poi verifica secondo la skill KDP |
| Contatti per scuole di italiano (EsameB1) | Le scuole pagano per contatto con consenso | ≥ 100 iscritti EsameB1; prima solo una casella "voglio essere contattato" per misurare la domanda | Risposta del consulente fiscale |
| Dati scioperi per aziende (Italy Strikes "For businesses") | Abbonamento B2B | Italy Strikes ≥ 1.000 visite al mese o una richiesta vera dal modulo | Risposta del consulente fiscale |

## 8. Registro delle decisioni

- 14/10/2026 sera: anche Tourist Tax, Visa Income e Before You Fly sono online con il nuovo aspetto. Il ramo di produzione su Netlify era già quello giusto: la pubblicazione era solo più lenta. Restyling completo su 5 siti; Italy Strikes esce il 17/10.

- 14/10/2026: restyling pubblicato. EsameB1 (con pagine costo e risultati) ed EsamiDiStato sono online. Tourist Tax, Visa Income e Before You Fly sono stati costruiti solo come anteprima di ramo (ccr-b7fd6b9e-n096cr--<sito>.netlify.app): su Netlify il loro ramo di produzione non è il nostro, oppure la pubblicazione automatica è bloccata. Serve un'impostazione di Massimiliano su Netlify.

- 14/10/2026: revisione del mercoledì. 6 siti su 6 rispondono (home, sitemap, pagine campione 200). Registro scioperi aggiornato il 13/10 alle 22:43. Nessuna soglia raggiunta: tutti i siti in fase Avvio, decisioni invariate. La ricerca settimanale è spostata alle 23 di oggi, insieme al test delle fonti per il sito degli affari, per risparmiare crediti.

- 12/10/2026: test di facilità per le app HubSpot (`saas/6-test-facilita-hubspot.md`) → **DIFFICILE**. Nessun gruppo di richieste supera la soglia; i primi utenti arrivano solo con messaggi privati, cioè vendita personale. In più, dal 19/8/2026 ogni utente deve usare davvero l'app ogni mese. L'idea resta chiusa.

- 12/10/2026: app HubSpot in abbonamento (unica idea "grande" che passa la ricerca, `saas/5-app-alto-potenziale.md`) **non si fa**: i primi clienti richiederebbero vendita personale di Massimiliano sui forum. Restano i libri KDP (già al massimo di 2 a settimana) e la rete di siti.

- 12/10/2026: primo iscritto vero su EsameB1 (da Google). Scoperto che le routine che aprono una sessione nuova non possono salvare su GitHub (la routine del lunedì 12/10 non ha pubblicato). Le routine del lunedì, del mercoledì e del 3 del mese ora girano nella sessione principale. Il restyling di EsameB1, EsamiDiStato e dei tre siti di viaggio si pubblica il 15/10, dopo il rinnovo dei crediti Netlify.

- 12/10/2026: Airalo respinge la domanda. Motivo probabile: siti nuovi, senza traffico. Nessun cambiamento ai siti (il link Airalo non era ancora online). Si ripresenta con i numeri.

- 11/10/2026: creata la gestione da manager su richiesta di Massimiliano. Soglie fissate prima di vedere i numeri (skill `rete-siti`, sez. 3).
