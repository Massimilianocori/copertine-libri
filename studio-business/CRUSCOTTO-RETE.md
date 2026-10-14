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
| Sito "affari": case all'asta (Portale Vendite Pubbliche) con lo sconto rispetto ai valori OMI di zona; parte secondaria con annunci eBay via API ufficiale | Idea di Massimiliano del 13/10, promettente per le case | Test tecnico delle fonti, concorrenza e domanda | 14/10 ore 23:05 |
| Zone a basse emissioni in Europa, richiami auto (NHTSA/Safety Gate), incentivi auto elettriche | Da valutare | Ricerca del mercoledì | 14/10 |

## 7b. Idee a pagamento in attesa (decisione di Massimiliano del 12/10: "da fare, adesso non è urgente")

Si riprendono solo quando la soglia è raggiunta. Prima vengono i libri KDP già in coda con voto 9.

| Idea | Come si incassa | Soglia per riprenderla | Cosa serve |
|---|---|---|---|
| Libro Kindle "Esame B1 cittadinanza: guida e prove" con link da EsameB1 | Diritti d'autore Amazon (niente vendite dirette) | EsameB1 ≥ 1.000 visite al mese oppure ≥ 30 iscritti, e coda libri KDP con voto 9 smaltita | Foto BookBeam di 2-3 ricerche ("esame B1 cittadinanza", "CILS B1 cittadinanza", "test italiano cittadinanza"), poi verifica secondo la skill KDP |
| Contatti per scuole di italiano (EsameB1) | Le scuole pagano per contatto con consenso | ≥ 100 iscritti EsameB1; prima solo una casella "voglio essere contattato" per misurare la domanda | Risposta del consulente fiscale |
| Dati scioperi per aziende (Italy Strikes "For businesses") | Abbonamento B2B | Italy Strikes ≥ 1.000 visite al mese o una richiesta vera dal modulo | Risposta del consulente fiscale |

## 8. Registro delle decisioni

- 14/10/2026: revisione del mercoledì. 6 siti su 6 rispondono (home, sitemap, pagine campione 200). Registro scioperi aggiornato il 13/10 alle 22:43. Nessuna soglia raggiunta: tutti i siti in fase Avvio, decisioni invariate. La ricerca settimanale è spostata alle 23 di oggi, insieme al test delle fonti per il sito degli affari, per risparmiare crediti.

- 12/10/2026: test di facilità per le app HubSpot (`saas/6-test-facilita-hubspot.md`) → **DIFFICILE**. Nessun gruppo di richieste supera la soglia; i primi utenti arrivano solo con messaggi privati, cioè vendita personale. In più, dal 19/8/2026 ogni utente deve usare davvero l'app ogni mese. L'idea resta chiusa.

- 12/10/2026: app HubSpot in abbonamento (unica idea "grande" che passa la ricerca, `saas/5-app-alto-potenziale.md`) **non si fa**: i primi clienti richiederebbero vendita personale di Massimiliano sui forum. Restano i libri KDP (già al massimo di 2 a settimana) e la rete di siti.

- 12/10/2026: primo iscritto vero su EsameB1 (da Google). Scoperto che le routine che aprono una sessione nuova non possono salvare su GitHub (la routine del lunedì 12/10 non ha pubblicato). Le routine del lunedì, del mercoledì e del 3 del mese ora girano nella sessione principale. Il restyling di EsameB1, EsamiDiStato e dei tre siti di viaggio si pubblica il 15/10, dopo il rinnovo dei crediti Netlify.

- 12/10/2026: Airalo respinge la domanda. Motivo probabile: siti nuovi, senza traffico. Nessun cambiamento ai siti (il link Airalo non era ancora online). Si ripresenta con i numeri.

- 11/10/2026: creata la gestione da manager su richiesta di Massimiliano. Soglie fissate prima di vedere i numeri (skill `rete-siti`, sez. 3).
