# Sito nuovo clone di EsameB1 per la Spagna: CCSE + DELE A2 per la nacionalidad (6/11/2026)

**Domanda del giro:** EsameB1 è il sito che cresce di più della rete (226 → 362 visite a settimana, 36 iscritti all'avviso, citato da ChatGPT). La regola del 6/11 dice di allargare ciò che cresce: il gemello spagnolo (CCSE + DELE A2) passa l'asticella dei siti nuovi (voto ≥ 7 e ≥ 5.000 €/anno centrali)?

**Già valutata:** studio 2 (candidata G, "riserva lingua", 2-3k €/anno), 30/10 (5,5: città deboli, sito Cervantes in JavaScript), 31/10 (4,5: calendario 2027 leggibile, centri no). **Fatti nuovi di oggi:** la crescita di EsameB1, il record delle domande di nazionalità in Spagna (295.107 nel 2025), e i portali d'iscrizione del Cervantes (`ccse.cervantes.es`, `dele.cervantes.es`) **in manutenzione** a 17 giorni dall'apertura delle iscrizioni 2027.

**Verdetto: NON passa. Voto 5,5. Centrale circa 800 €/anno a 18 mesi (prudente 250, ottimista 2.500).** Resta RISERVA. Il mercato è più grande di quello italiano, ma la domanda per città è debole, i centri d'esame non sono leggibili (Salesforce in JavaScript e diritti riservati) e chi paga paga poco: i latinoamericani parlano già spagnolo e non comprano lezioni.

## 1. Domanda (autocomplete Google, 6/11/2026)

112 richieste a suggestqueries.google.com (client=firefox), script nello scratchpad della sessione, non nel repository.

| Ricerca (gl/hl) | Suggerimenti | Cosa contengono |
|---|---|---|
| "examen ccse" (es, mx, co, ve, ar, pe, ec, ma) | 10 ovunque | 7 su 10 sono **preguntas / 300 preguntas pdf / 2026 pdf**: la domanda è di esercizio |
| "examen nacionalidad española" (es e 6 Paesi latinoamericani) | 10 | ejemplo, pdf, preguntas, "2026 dele a2" |
| "resultados ccse" (es) | **10** | **un mese per suggerimento**: septiembre, julio, junio, mayo, abril 2026, octubre e noviembre 2025… |
| "resultados examen ccse" | 10 | stessi mesi più "instituto cervantes" |
| "examen ccse cita" | 10 | cita previa, 2026, pedir cita, "cita examen ccse madrid" |
| "dele a2 nacionalidad" / "… española" | 10 / 10 | test, libro, 2026, curso |
| "dele a2 2027" | 8 | convocatoria, cita previa 2027, fecha de examen |
| "ccse fechas" | 5 | 2026, examen, 2025, cervantes |
| "ccse precio" | 5 | 2026, 2025, cervantes, nacionalidad |
| "dele a2 fechas" / "precio" | 4 / 3 | – |
| "ccse 2027" / "examen ccse 2027" | 2 / 1 | domanda 2027 non ancora nata |
| "ccse exento" / "dele a2 exento" | 2 / 0 | esenzioni poco cercate |
| "centros examen ccse" / "donde hacer el examen ccse" | 1 / 2 | **le sedi si cercano poco** |
| "nacionalidad española por residencia" | 10 | consulta, requisitos, online, sede.mjusticia |

**Città (gl=es, 20 città):** tutte hanno almeno "examen ccse <città>", ma sono 1-2 varianti. Solo Madrid (ccse 5, dele a2 4, examen ccse 4) e Barcellona (5, 7, 5) hanno più varianti; Palma 4, Valencia 2-4; Siviglia, Málaga, Alicante, Murcia, Saragozza, Bilbao, Las Palmas, Tenerife, Granada, Almería, Girona, Tarragona, Castellón, Valladolid e Vigo 1-2; Córdoba 0-1. "dele a2 <città>" è 0 in 9 città su 20. Per confronto, EsameB1 vive di ricerche per città in Italia.

**Marocco (gl=ma, hl=fr ed es):** "examen ccse" e "examen dele a2" 10 (in spagnolo, pdf e nacionalidad 2026), ma "dele a2 maroc / casablanca / tanger" 0 e "examen nationalité espagnole" 1-2. I marocchini residenti cercano dalla Spagna e in spagnolo.

**Lettura:** la domanda c'è ed è grande, ma va su tre cose: (1) **domande d'esercizio** (mercato pieno di app e PDF, anche il Cervantes ha l'app gratuita); (2) **risultati per mese**, personali e dietro login, ma "quando escono" è una domanda pubblica (arc-legal scrive un articolo per ogni convocatoria); (3) **date e cita**. Le sedi per città, il cuore di EsameB1, qui sono la parte più debole.

## 2. Fonti ufficiali (curl, 6/11/2026)

| URL | Esito | Cosa c'è |
|---|---|---|
| `examenes.cervantes.es/` e `/es/ccse`, `/fechas`, `/donde` | 200, 177 KB, tutti reindirizzati a `cervantes.org/es/examenes/dele` | "Información para las convocatorias DELE y CCSE 2027" (sito esami in rifacimento) |
| `cervantes.org/es/examenes/ccse` | **200, HTML leggibile** | Calendario CCSE 2027: iscrizioni dal **23/11/2026**, 10 convocatorie (28/1, 25/2, 18/3, 29/4, 27/5, 24/6, 29/7, 30/9, 28/10, 25/11/2027), ognuna con chiusura iscrizioni, inizio e fine delle citas; restanti 2026: 29/10 (chiusa l'8/10) e 26/11 (chiusa il 5/11). Nessun prezzo, nessun centro, nessuna data dei risultati |
| `cervantes.org/es/examenes/dele` | 200, HTML leggibile | DELE 2027: iscrizioni dal **18/11/2026**; A2 in tutte e 8 le sessioni (5/3, 2/4, 22/5, 9/7, 10/9, 15/10, 12-13/11…) con chiusure (es. 20/1/2027 per il 5/3). Nessun prezzo |
| `cervantes.org/es/examenes/ccse/centros`, `/centros-examen`, `sitemap.xml` | 404 | Nessun elenco pubblico dei centri |
| `tienda.cervantes.org` | 200, 77 KB guscio Salesforce (LWC) | Iscrizione, centri e prezzi caricati da JavaScript: non leggibili con curl |
| `ccse.cervantes.es`, `dele.cervantes.es` | 200 → `comunes.cervantes.es/mantenimiento/` | **"Estamos realizando tareas de mantenimiento"**: i portali d'iscrizione sono fermi |
| `cervantes.org/es/aviso-legal` | 200 | Tutti i contenuti con diritti riservati: vietato "reproducirlos, distribuirlos"; ammessi solo i link. Le date sono fatti, ma un elenco dei centri copiato sarebbe una banca dati protetta |
| `boe.es` Ley 19/2015 (BOE-A-2015-7851) | 200, testo leggibile | Art. 21.5 CC: DELE A2 o superiore; **esenti dal DELE i cittadini di Paesi con lo spagnolo lingua ufficiale**; esenti da entrambe le prove i minori di 18 anni e le persone con capacità modificata giudizialmente |
| `sede.mjusticia.gob.es/es/tramites/nacionalidad-espanola` | 200 | Pagina del trámite, dispensa dalle prove per chi non sa leggere e scrivere o ha difficoltà di apprendimento, modello 790 |
| `mjusticia.gob.es/.../Estadisticas_nacionalidad_31_12_2025.pdf` | 200, PDF leggibile | Domande e concessioni per anno (sotto); i PDF 30/06 e 30/09/2026 danno 404 |
| `ine.es/dyngs/Prensa/es/EANER2025.htm` | 200 | 299.732 acquisizioni 2025 (sotto) |
| `mjusticia.gob.es/es/ciudadania/nacionalidad/nacionalidad-residencia` | 404 | – |
| `inclusion.gob.es/web/opi/estadisticas` | 403 "Acceso no permitido" | Chiusa: non aggirata |
| Prezzi | Solo fonti secondarie | CCSE **85 €** uniforme nel 2026, due tentativi (Universidad de Sevilla, institutodeidiomas.us.es/node/783). DELE A2 in Spagna: **124 € non verificato** (nessuna fonte ufficiale letta) |

Sefarditi: la via della Ley 12/2015 è chiusa (domande fino al 2019) e non riguarda chi fa il CCSE per residenza oggi; il PDF del Ministero ha solo la coda dei vecchi fascicoli.

## 3. Numeri del mercato

- **Ministero della Giustizia, al 31/12/2025:** domande di nazionalità per residenza 86.773 (2020), 146.980 (2021), 171.328 (2022), 199.703 (2023), 246.663 (2024), **295.107 (2025, record, +20 %)**; concessioni 221.466 (2024) e **221.284 (2025)**; 256.393 fascicoli in attesa (218.659 del 2025).
- **INE, 28/5/2026:** 299.732 stranieri residenti hanno acquisito la nazionalità nel 2025 (+18,7 %, massimo della serie), 253.836 per residenza; prime nazionalità d'origine Marocco 42.114, Colombia 37.712, Venezuela 36.271.
- **Candidati CCSE:** 804.929 cumulati dall'ottobre 2015 (Cifras 2023) e 1.278.831 (Memoria Cervantes 2024-25, studio 2): circa **230-240.000 l'anno**, in crescita con le domande. 221 centri d'esame (studio 2).
- **DELE A2:** 33.944 iscritti alla sessione di novembre 2025 (arc-legal, non ufficiale), 7.500 a settembre 2025: a occhio 80-100.000 l'anno, quasi tutti non ispanofoni (Marocco, Pakistan, Cina, Senegal, Ucraina, Romania…).
- Confronto: in numeri di candidati la Spagna (230-240.000 CCSE più 80-100.000 DELE A2 l'anno) è con ogni probabilità diverse volte il B1 italiano per la cittadinanza (stima, non contata).

## 4. Concorrenza (cosa esce oggi per queste ricerche)

Ricerche web dagli USA (Google spagnolo non interrogabile: niente aggiramenti).
- **Instituto Cervantes** (cervantes.org): calendario ufficiale, manuale, app gratuita "CCSE Nacionalidad Española". Il **sito esami nuovo è in preparazione**: quando uscirà avrà con buona probabilità il cercatore dei centri.
- **arc-legal.es** (studio legale): un articolo per ogni convocatoria ("CCSE convocatoria de octubre 2025: publicación de los resultados", anche in inglese), statistiche trimestrali della nazionalità in PDF. È il padrone delle ricerche "resultados ccse <mes>".
- **parainmigrantes.info:** "Listado de centros de examen de nacionalidad española", pagina unica con indirizzi ed email per città (aggiornata il 4/5/2026), più guide su iscrizione e pagamento.
- **machelindiaz.com** (statistiche, manuale CCSE 2026), **fedele.org** (federazione delle scuole, date e documenti), **università** (Sevilla, Jaén, Alicante, Valencia, Barcelona) con le date delle proprie sedi, **accademie** (Hablamos, CastiLa, inhispania, AIL, LAE, Lingua Schools).
- **Quiz:** flysky-certs.pages.dev (316 domande, 4,99 $ a settimana), cohenyaguirre.es, molte app.

**Il buco:** nessuno ha **una pagina per città** con i centri, le convocatorie che ciascun centro offre, le scadenze 2027 e un "avísame" quando si aprono le iscrizioni o escono i risultati. È lo stesso buco di EsameB1, ma (a) i centri per città non si possono leggere da una fonte ufficiale riusabile, (b) le ricerche per città sono poche, (c) i risultati sono già coperti da arc-legal.

## 5. Chi paga e quanto

| Pagatore | Stato | Quanto | Nota |
|---|---|---|---|
| **italki** (stesso link di EsameB1, 18 $ a cliente nuovo) | Attivo nella rete | Basso | Solo il pubblico DELE A2 (circa un quarto dei visitatori); i latinoamericani sono **esenti** dal DELE e il CCSE è un quiz di cultura, non di lingua. Pubblico marocchino e asiatico che spende poco |
| **Amazon.es** (libri "Preparación DELE A2", "libro dele a2 nacionalidad española" è nei suggerimenti) | **Serve l'iscrizione su afiliados.amazon.es con un ID negozio .es** (il tag `guideesami-21` vale per Amazon.it): azione di Massimiliano, gratis. Tabella delle commissioni non letta (503 con controllo anti-robot) | 1-1,5 € a libro (5 % per analogia con Amazon.it, non verificato) | Il manuale CCSE è un PDF gratuito del Cervantes: poco da vendere sul CCSE |
| **AdSense in spagnolo** | Account di rete già attivo | 2-5 € ogni 1.000 visite (stima: pubblico residente in Spagna, avvocati di extranjería che fanno pubblicità; CPC spagnolo 0,2-0,8 €) | La voce principale |
| Accademie e corsi online | Nessun programma di affiliazione nominato trovato per il CCSE/DELE A2 (Emagister lavora a contatti, non verificato) | 0 | Contattarle sarebbe email a freddo: vietato |
| Gestorie e avvocati per la domanda di nazionalità (100-400 € a pratica) | Nessun programma nominato | 0 | Stesso limite |
| Quiz a pagamento (stile FlySky) | Si potrebbe vendere un prodotto proprio | – | Attività commerciale (Camera di Commercio e INPS, vedi EsameB1) e mercato pieno |

## 6. Stima a 18 mesi (€/anno)

Assunzioni: sito nuovo in spagnolo su sottodominio Netlify, nessun dominio comprato; visite da Google e assistenti IA; 1,4 pagine per visita; un quarto dei visitatori è nel percorso DELE A2.

| Scenario | Visite/anno | AdSense | italki | Amazon.es | Totale |
|---|---|---|---|---|---|
| Prudente | 30.000 (≈ 600/sett.) | 30.000 × 3 €/1.000 = 90 € | 30.000 × 25 % × 1 % clic × 8 % = 6 clienti × 16 € ≈ 100 € | 30 libri × 1,2 € ≈ 40 € (se Massimiliano si iscrive) | **≈ 250 €** |
| Centrale | 80.000 (≈ 1.500/sett., 4 volte EsameB1 oggi) | 80.000 × 4 €/1.000 = 320 € | 80.000 × 25 % × 1,5 % × 10 % = 30 × 16 € ≈ 480 € | 70 × 1,2 € ≈ 80 € | **≈ 800-900 €** |
| Ottimista | 200.000 (≈ 3.800/sett.) | 200.000 × 5 €/1.000 = 1.000 € | 75 clienti ≈ 1.200 € | 200 × 1,2 € ≈ 250 € | **≈ 2.500 €** |

Anche raddoppiando tutte le cifre dello scenario ottimista non si arriva a 5.000 €: per arrivarci servirebbero circa 400.000 visite l'anno con le stesse rese, cioè una quota di mercato che oggi hanno solo il Cervantes e arc-legal.

**Ore di costruzione:** 25-35 (generatore in spagnolo copiato da EsameB1, calendario 2027 CCSE e DELE da cervantes.org, esenzioni dal BOE, pagine "resultados <mes>" con la data attesa, 20 pagine città senza un elenco dei centri riusabile, avísame). La raccolta automatica dei centri non è fattibile: Salesforce in JavaScript e diritti riservati.

**Rischi:**
1. Il **nuovo sito esami del Cervantes** è in arrivo (portali in manutenzione oggi): se pubblica centri e date per città, il buco si chiude.
2. Centri non riusabili: le pagine città restano senza il dato che le rende utili, oppure si scrivono a mano da fonti sparse (università e accademie), che è lavoro senza fine.
3. Domanda per città da 1-2 varianti fuori da Madrid e Barcellona.
4. Pagatori deboli: italki inutile per la maggioranza ispanofona; Amazon.es da attivare a parte; AdSense spagnolo basso.
5. Concorrenti con autorità (arc-legal, parainmigrantes, università) già primi su risultati e centri.
6. Incassi commerciali: stesso nodo fiscale di EsameB1 (Camera di Commercio e INPS prima del primo incasso).

**Voto severo: 5,5** (domanda grande e in crescita, calendario ufficiale leggibile e momento buono con il Cervantes in manutenzione; ma città deboli, centri chiusi, soldi pochi).

## 7. Decisione

**NON passa l'asticella dei siti nuovi** (5,5 < 7; circa 800 € centrali < 5.000 €). Resta **RISERVA**, con due inneschi scritti:
- se il nuovo sito esami del Cervantes pubblica un elenco dei centri leggibile **e** con licenza di riuso (controllo a fine gennaio 2027, come già scritto il 31/10);
- se EsameB1 supera le 1.500 visite a settimana con italki e Amazon che pagano davvero (prova che il modello rende), allora si rifà il conto con le rese vere al posto di quelle stimate.

Niente sezione dentro un sito esistente: EsameB1 è in italiano per chi fa l'esame in Italia, e una pagina spagnola lì non avrebbe né pubblico né autorità.

## Fonti
- [Instituto Cervantes, Prueba CCSE (calendario 2027)](https://cervantes.org/es/examenes/ccse), [DELE 2027](https://cervantes.org/es/examenes/dele), [aviso legal](https://cervantes.org/es/aviso-legal)
- [BOE, Ley 19/2015, art. 21.5 CC](https://www.boe.es/buscar/act.php?id=BOE-A-2015-7851)
- [Ministerio de Justicia, estadísticas de nacionalidad al 31/12/2025 (PDF)](https://www.mjusticia.gob.es/es/Ciudadano/Nacionalidad/Documents/Estadisticas_nacionalidad_31_12_2025.pdf), [sede, trámite nacionalidad por residencia](https://sede.mjusticia.gob.es/es/tramites/nacionalidad-espanola)
- [INE, adquisiciones de nacionalidad 2025](https://ine.es/dyngs/Prensa/es/EANER2025.htm)
- [Universidad de Sevilla, CCSE 85 €](https://institutodeidiomas.us.es/node/783)
- [parainmigrantes, listado de centros](https://www.parainmigrantes.info/listado-de-centros-de-examen-de-nacionalidad-espanola/), [arc-legal, resultados CCSE octubre 2025](https://www.arc-legal.es/ccse-convocatoria-de-octubre-2025-publicacion-de-los-resultados/), [arc-legal, DELE A2 noviembre 2025](https://www.arc-legal.es/en/dele-a2-exam-results-released-november-2025-session-summary/), [FlySky CCSE](https://flysky-certs.pages.dev/spanish-citizenship-ccse/)
