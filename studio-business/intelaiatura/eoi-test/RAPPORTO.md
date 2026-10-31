# Test EOI: calendari unici delle 17 comunità (31/10/2026)

Secondo test dell'idea "Esami EOI, pruebas de certificación" (voto 7) di `idee-2026-10-31-lingue.md`, sezione 2.5. Serve a decidere se il voto sale a 8.

## Verdetto: SALE A 8 (con una riserva sui risultati)

| Condizione per l'8 | Soglia | Risultato | Esito |
|---|---|---|---|
| Comunità con calendario unico ufficiale, letto dal server | almeno 12 su 17 | **13 su 17** | sì |
| Abitanti coperti | almeno 80 % | **90,4 %** (44,27 milioni su 48,96) | sì |
| Andalucía e Cataluña comprese | tutte e due | Andalucía (BOJA, 41 date) e Cataluña (pagina del Departament, 34 date, **già 2027**) | sì |
| Controlli a mano | almeno 28 su 30 | **30 su 30** | sì |
| Date d'esame per lingua e livello | – | **665 date** lette da 13 lettori | – |
| Finestre di iscrizione con date | – | 10 comunità su 17 (82,6 % degli abitanti); in altre 2 la finestra è "15 o 10 giorni lavorativi dalla pubblicazione" | sì |
| Data di uscita dei risultati | – | solo **Cataluña e Canarias** (21,2 % degli abitanti) | **no** |

**Perché sale.** Il difetto della Germania (date diverse sede per sede) qui non c'è: in tutte le 13 comunità lette le **prove scritte** di B1, B2, C1 e C2 hanno lo stesso giorno in tutta la comunità, fissato da un documento ufficiale. Le date per lingua e livello si leggono in automatico, i controlli sono tutti giusti, e la soglia scritta in sezione 2.5 è superata con margine.

**La riserva.** Due cose restano "per scuola" in tutte le comunità, come in Germania:
- **le prove orali**: ogni EOI pubblica giorno e ora (Valencia "entro il 15/5", Murcia "entro l'11/5", Baleari "entro l'1/6");
- **le notas**: solo Cataluña (23/6 e 30/6/2027) e Canarias (19/6 e 11/9/2026) danno una data unica. Castilla y León lo scrive in chiaro: "las escuelas oficiales de idiomas establecerán las fechas en las que harán públicas las calificaciones".

Se "uscita dei risultati" va letta come parte obbligatoria del calendario unico, la condizione **non** passa (2 comunità su 17) e il voto **resta 7**. Io la leggo come la soglia scritta in sezione 2.5, che chiede il calendario delle prove e non nomina i risultati. Le pagine "notas eoi [città]" vanno quindi fatte come pagine di rinvio alla scuola, senza promettere una data.

Il test è solo tecnico. Resta aperta l'obiezione economica della sezione 2.7: stima centrale sotto i 5.000 €.

---

## 1. Tabella per comunità

Popolazione: INE, Cifras de Población al 1/1/2025 (dato definitivo, tabella 56940, letta dall'API JSON dell'INE il 31/10/2026). Percentuale sul totale delle 17 comunità (48.957.663, senza Ceuta e Melilla).

"Uniche" = le prove scritte hanno la stessa data in tutte le EOI della comunità.

| Comunità | Abitanti | % | Fonte ufficiale | HTTP | Formato | Date uniche? | Anno | Date estratte | Iscrizioni | Risultati |
|---|---|---|---|---|---|---|---|---|---|---|
| Andalucía | 8.676.713 | 17,7 | [BOJA n. 46, 9/3/2026, anexos I-III](https://www.juntadeandalucia.es/boja/2026/46/BOJA26-046-00026-3164-01_00334384.pdf) | 200 | PDF, **griglia** | sì (orali: ogni EOI) | 2026 | **41** | 1-16/4 | ogni EOI |
| Cataluña | 8.124.126 | 16,6 | [Pagina "Calendari" del Departament d'Educació](https://educacio.gencat.cat/ca/serveis-tramits/proves/proves-lliures-obtencio-titols/convocat-ordinaria-idiomes/calendari/) | 200 | HTML, elenco | sì (orali: data data il giorno dello scritto) | **2027** | **34** | 22-26/2/2027 | **23/6 e 30/6/2027** |
| Madrid | 7.113.886 | 14,5 | [BOCM 25/3/2026, Anexo I](https://bocm.es/boletin/CM_Orden_BOCM/2026/03/25/BOCM-20260325-12.PDF) | 200 | PDF, tabella | sì | 2026 | **29** | 7-21/4; liste 28/4 e 6/5; matricola 7-20/5 | ogni EOI |
| Comunitat Valenciana | 5.425.182 | 11,1 | [DOGV n. 10296, 5/2/2026, anexos I-III](https://dogv.gva.es/datos/2026/02/05/pdf/2026_3622_es.pdf) | 200 (in una prova precedente la connessione si era chiusa) | PDF, **griglia** | sì (orali: ogni EOI entro il 15/5) | 2026 | **90** | 16-20/2 + turni per livello; liste 23/3 e 22/4 | ogni EOI |
| Galicia | 2.714.741 | 5,5 | Instrución 1/2026 della Dirección Xeral de FP, anexos IV e V (sito della Consellería) | **000** | – | sì secondo le guide e i calendari copiati dalle EOI (A Coruña: inglese B2 27/5/2026), **non verificato dal server** | – | 0 | – | – |
| Castilla y León | 2.401.221 | 4,9 | [BOCYL 24/2/2026, anexo III](https://bocyl.jcyl.es/boletines/2026/02/24/pdf/BOCYL-D-24022026-37-28.pdf) | 200 (sito instabile: l'altra delibera dello stesso giorno 000) | PDF, tabella a 2 colonne | sì per B1-C2; A1-A2 ogni EOI | 2026 | **68** | 2-9/3 | ogni EOI (scritto) |
| Canarias | 2.258.866 | 4,6 | [BOC n. 77, 22/4/2026, apéndice II](https://www.gobiernodecanarias.org/cmsgob1/export/sites/educacion/web/_galerias/descargas/otros/apendice-2-pruebas-certificacion-aspirantes-libres-escolarizados-25-26.pdf) (sul sito della Consejería) | 200 | PDF, tabella | sì (orali: ogni EOI tra 29/5 e 18/6) | 2026 | **66** | 29/4-13/5; liste definitive 25/5 | **19/6 e 11/9/2026** |
| País Vasco | 2.242.343 | 4,6 | [Anexo II 2026-27](https://www.euskadi.eus/contenidos/informacion/eoi_matricula_libre/es_def/adjuntos/Calendario-Examenes-Anexo-II2026_2027-definitivo-1.pdf) + anexo 2025-26 + delibera di matricola 2026-27 | 200 | PDF, tabella | sì (orali: ogni EOI) | 2026 e **2027** | **64** (32 + 32) | 25/1-4/2/2027; liste 2/3/2027 | ogni EOI |
| Castilla-La Mancha | 2.126.378 | 4,3 | [DOCM n. 28, 11/2/2026, anexo I](https://docm.jccm.es/docm/descargarArchivo.do?ruta=2026%2F02%2F11%2Fpdf%2F2026_727.pdf&tipo=rutaDocm) | 200 | PDF, **griglia** (calendario mensile) | sì, anche A2 (orali: ogni EOI) | 2026 | **60** | 10 giorni lavorativi dal DOCM | ogni EOI |
| Región de Murcia | 1.586.989 | 3,2 | [BORM n. 14, 19/1/2026, anexo III](https://www.borm.es/services/anuncio/ano/2026/numero/181/pdf?id=840845) | 200 | PDF, tabella | **sì per B1-C2** ("el mismo para todas las EOI"); A1-A2 e orali ogni EOI | 2026 | **19** | 3-10/2; lista provvisoria 24/2 | ogni EOI |
| Aragón | 1.364.621 | 2,8 | [Delibera 13/3/2026 (BOA)](https://www.boa.aragon.es/cgi-bin/EBOA/BRSCGI?CMD=VEROBJ&MLKOB=1441023330505), anexos II, III e V sul [trámite 1189](https://www.aragon.es/tramitador/-/tramite/escuelas-oficiales-de-idiomas/pruebas-de-certificacion-alumnado-oficial-y-libre) | 200 | PDF, tabella | sì per B1-C2 (orali: ogni EOI) | 2026 | **36** | 1-9/4; lista definitiva 14/4 | consultazione online, senza data |
| Illes Balears | 1.249.844 | 2,6 | [BOIB n. 17, 5/2/2026, annex 1](https://www.caib.es/eboibfront/pdf/ca/2026/17/1211874) + BOIB n. 14 | 200 | PDF, elenco in catalano | sì (orali: ogni EOI entro l'1/6) | 2026 | **76** | 13-27/3 | ogni EOI |
| Extremadura | 1.053.345 | 2,2 | [DOE n. 21, 2/2/2026](https://doe.juntaex.es/pdfs/doe/2026/210o/26060238.pdf) e [pagina del trámite](https://www.juntaex.es/w/0648923) | 200 | PDF e HTML | **no**: "Cada EOI publicará … la información sobre las fechas de examen" | – | 0 | 15 giorni lavorativi dal DOE | ogni EOI |
| Principado de Asturias | 1.015.128 | 2,1 | [BOPA n. 28, 11/2/2026, apartado 17°](https://www.asturias.es/bopa/2026/02/11/2026-00845.pdf) | 200 (`www.asturias.es`; `miprincipado.asturias.es` 000) | PDF, tabella con una data ogni 2 lingue | sì (orali: ogni EOI) | 2026 | **40** | 15 giorni lavorativi dal BOPA; liste in tabella sfalsata, non lette | ogni EOI |
| Navarra | 683.854 | 1,4 | [Anexo 2° 2026-27, calendario delle prove unificate](https://www.educacion.navarra.es/documents/27590/0/ANEXO+2%C2%BA+calendario+ex+escritos+26-27.pdf/3755a7a2-075b-3b76-97d7-917214618cb2) | 200 | PDF, tabella | sì (orali: ogni EOI) | **2027** | **42** | non nel documento | ogni EOI |
| Cantabria | 593.623 | 1,2 | BOC 26/2/2026 (CVE-2026-1414), anexo IV | **000** | – | probabilmente sì (anexo IV "calendario"), **non verificato dal server** | – | 0 | 2-10/3 e 16-24/3 (da ricerca web) | – |
| La Rioja | 326.803 | 0,7 | Guide 2025-26 della Consejería (sez. VI, calendario) | **000** | – | probabilmente sì (3 EOI, una sola delibera), **non verificato dal server** | – | 0 | 16/2-6/3 (da ricerca web) | – |

**Totale: 665 date d'esame** (lingua × livello × giorno, a volte con l'ora o il turno) e 36 tappe (iscrizioni, liste, risultati), in `date_estratte.json`.

**Copertura:**
- 13 comunità lette = 44.269.151 abitanti = **90,4 %** (90,1 % della Spagna con Ceuta e Melilla);
- con Galicia, Cantabria e La Rioja (calendario probabilmente unico, ma il server non le raggiunge) si arriverebbe al 97,8 %;
- resta fuori Extremadura (2,2 %): la Junta rinvia a ogni EOI.

**Correzione del primo test.** Murcia **non** lascia le date alle scuole. L'anexo III del BORM ha una tabella unica per B1-C2 ("El calendario de celebración de las pruebas es el mismo para todas las EOI y extensiones", tutte alle 16:30). Alle scuole restano solo A1-A2 e le orali. Il primo giro aveva letto la frase sulle orali ("no más tarde del 11 de mayo") come se valesse per tutto.

## 2. Il criterio della Germania, applicato qui

In Germania servivano 85 siti di 85 sedi, ognuno con le sue date: è passato il 36 %. Qui la data della prova scritta la fissa la comunità, per tutte le sue EOI, in **un documento all'anno**: 17 documenti in tutto. Lo stesso difetto della Germania resta su due cose:

1. **le orali**, pubblicate da ogni EOI (circa 300 tra scuole ed extensiones);
2. **le notas**, tranne Cataluña e Canarias.

Il sito può promettere con sicurezza "data dello scritto, per lingua e livello, nella tua comunità". Per orali e notas può solo rimandare alla scuola, o dare la finestra ufficiale quando c'è.

## 3. Gli script

Tutti in questa cartella. I file scaricati non sono nel repository (rigenerabili).

| File | Cosa fa |
|---|---|
| `fonti.py` | URL ufficiali, formato, ruolo di ogni documento; popolazione INE |
| `scarica.py <cartella>` | scarica tutto con un user-agent da browser e una pausa di 1,5 s. Riprova 3 volte **solo** gli errori di rete (000), mai i 403 o i 429. Converte i PDF con `pdftotext -layout`. Scrive `stato.json` |
| `estrai.py <cartella> <uscita.json>` | 13 lettori con 3 pezzi in comune: `griglia()` per i calendari a griglia (Andalucía, Valencia, Castilla-La Mancha), `blocchi()` per le tabelle con la lingua scritta una volta per gruppo (País Vasco, Canarias, Navarra), espressioni regolari per le altre |
| `campione.py` | sceglie i 30 controlli (seme fisso 2026, 2 per comunità + 4 tappe) e stampa le righe della fonte da guardare |
| `date_estratte.json` | le 665 date e le 36 tappe |
| `controlli_30.json` | i 30 controlli, con la riga della fonte e l'esito |
| `stato_http.json` | codice HTTP e peso di ogni fonte nell'ultimo giro di `scarica.py` (31/10/2026; l'apéndice I delle Canarie è stato aggiunto dopo: 200, 211 KB) |

**Riuso dei lettori del primo test.** Quelli di Madrid e dei Paesi Baschi erano ancora nello scratchpad (`parse_eoi.py`):
- **Madrid**: stessa espressione, ma i caratteri di controllo si tolgono prima di leggere. Escono 29 su 29 al primo colpo, senza correzioni a mano;
- **Paesi Baschi**: il lettore lasciava "pendenti" i livelli, perché il nome della lingua è a metà del gruppo. L'ho rifatto con `blocchi()`: si apre un gruppo nuovo quando il livello torna indietro (C1 → A2). Escono 32 + 32;
- **Valencia**: la griglia che al primo test dava 0 date ora ne dà 90.

**Conteggi verificati a mano.** Per ognuna delle 13 comunità ho contato a mano le righe del documento: tutti i 13 totali coincidono con quelli del programma.

**Errori trovati e corretti prima dei controlli** (onestà sul metodo: senza queste correzioni 3 dei 30 controlli avrebbero potuto cadere su date sbagliate):
- **Valencia, straordinaria**: due celle vicine ("VALENCIANO B1, VALENCIANO B2,") erano attaccate da un solo spazio, e sono finite nella stessa colonna. Risultato: 3 date sbagliate. Inoltre la tabella degli orari, sotto il calendario, veniva letta come celle. Ora le celle si separano anche alla virgola davanti al nome di una lingua, e la lettura si ferma alla nota sulle orali;
- **Navarra**: le date di settembre erano marcate come convocatoria ordinaria (soglia di colonna sbagliata di 5 caratteri). Le date erano giuste, l'etichetta no;
- **Asturias, tappe**: tabella a due colonne con il testo sfalsato rispetto alla data. 3 righe su 4 venivano attribuite male, quindi non le estraggo. Le date d'esame di Asturias sono a posto.

Ogni comunità ha un formato suo: 3 griglie, 6 tabelle diverse, 2 elenchi in prosa (catalano), 1 HTML. Ogni anno va rifatto il controllo dei conteggi: un cambio di impaginazione rompe il lettore senza errori visibili. Il lavoro stimato in sezione 2.7 (1-2 ore per lettore) torna con quello che ho visto.

## 4. I 30 controlli a mano

Campione casuale (seme 2026): 2 date d'esame per ognuna delle 13 comunità e 4 tappe. Per ogni riga ho letto la fonte e confrontato lingua, livello, giorno, convocatoria e ora o turno.

**Risultato: 30 giuste su 30.**

| # | Comunità | Cosa | Estratto | Nella fonte |
|---|---|---|---|---|
| 1 | Andalucía | árabe B2, ord. | 1/6/2026 | lunedì 1 giugno, mattina: ÁRABE NI B1, NI B2 |
| 2 | Andalucía | portugués B2, ord. | 10/6/2026 | mercoledì 10 giugno, pomeriggio: PORTUGUÉS NI B1, NI B2 |
| 3 | Aragón | francés C2, straord. | 7/9/2026 10:00 | Francés C2 … Lunes, 7 de septiembre 10:00 |
| 4 | Aragón | catalán B2, ord. | 1/6/2026 10:00 | Nivel B2: Catalán … Lunes, 1 de junio 10:00 |
| 5 | Canarias | francés A2, ord. | 9/6/2026 | FRANCÉS Básico A2 09-06-2026 |
| 6 | Canarias | italiano B2, straord. | 4/9/2026 | ITALIANO Intermedio B2 … 04-09-2026 |
| 7 | Castilla y León | portugués C1, ord. | 10/6/2026 | PORTUGUÉS C1 TARDE 10 DE JUNIO |
| 8 | Castilla y León | italiano C2, ord. | 5/6/2026 | ITALIANO C2 TARDE 5 DE JUNIO |
| 9 | Castilla-La Mancha | francés B1, ord. | 12/6/2026 10:00 | venerdì 12: 10:00 B1 Francés |
| 10 | Castilla-La Mancha | inglés A2, ord. | 22/5/2026 16:00 | venerdì 22: 16:00 A2 Inglés |
| 11 | Cataluña | euskera B1 | 2/6/2027 16:00 | B1, Èuscar: 2 de juny de 2027, a la tarda |
| 12 | Cataluña | griego B1 | 9/6/2027 16:00 | B1, Grec: 9 de juny de 2027, a la tarda |
| 13 | C. Valenciana | japonés B2, ord. | 16/6/2026 8:30 | 16 junio 8.30: ÁRABE B2 / JAPONÉS B2 |
| 14 | C. Valenciana | francés B1, ord. | 5/6/2026 8:30 | 5 junio 8.30: FRANCÉS B1, FRANCÉS C1 |
| 15 | Illes Balears | español B1, straord. | 11/9/2026 16:00 | Espanyol B1: prova escrita dia 11 de setembre, 16.00h |
| 16 | Illes Balears | alemán B1, ord. | 1/6/2026 16:00 | Alemany B1: prova escrita dia 1 de juny, 16.00h |
| 17 | Madrid | portugués A2 | 29/5/2026 15:45 | Nivel Básico (A2) Portugués 29 de mayo 15:45 |
| 18 | Madrid | portugués B2 | 29/5/2026 15:45 | Nivel Intermedio (B2) Portugués 29 de mayo 15:45 |
| 19 | Navarra | inglés C1, ord. | 21/5/2027 | Inglés C1: 21/5 (tarde) |
| 20 | Navarra | francés B1, straord. | 2/9/2027 | Francés B1 … 2/9 (mañana) |
| 21 | País Vasco | portugués B2 | 31/5/2027 | PORTUGUÉS N. INTERMEDIO (B2) 31/05/2027 |
| 22 | País Vasco | inglés B2 | 15/5/2026 | INGLÉS N. INTERMEDIO (B2) 15/05/2026 |
| 23 | Asturias | italiano B1, ord. | 11/6/2026 mattina | B1: Italiano Mañana / 11 de junio / Inglés Tarde |
| 24 | Asturias | italiano C2, straord. | 4/9/2026 pomeriggio | C2 y A2: Alemán Mañana / 4 de septiembre / Italiano Tarde |
| 25 | Murcia | francés C2 | 11/6/2026 16:30 | FRANCÉS … NAC2 11 de JUNIO |
| 26 | Murcia | inglés B1 | 17/6/2026 16:30 | INGLÉS NIB1 17 de JUNIO |
| 27 | Illes Balears | iscrizione | 13-27/3/2026 | dia 13 de març … dia 27 de març de 2026 |
| 28 | País Vasco | iscrizione | 25/1-4/2/2027 | entre el 25 de enero y el 4 de febrero |
| 29 | C. Valenciana | lista provvisoria | 23/3/2026 | 23 de marzo de 2026. Publicación de listados provisionales |
| 30 | País Vasco | lista definitiva | 2/3/2027 | el día 2 de marzo de 2027 … situación definitiva |

## 5. Server, blocchi e limiti

- **Siti non raggiungibili dal server.** Per Galicia (`edu.xunta.gal`, `centros.edu.xunta.gal`), Cantabria (`boc.cantabria.es`, `educantabria.es`) e La Rioja (`larioja.org`, ma il BOR su `ias1.larioja.org` risponde) la connessione si chiude subito dopo l'apertura: 517 byte inviati, 39 ricevuti, sempre. Stessa cosa per `educastur.es`, `educa.jcyl.es` e `portal.edu.gva.es`, ma lì il Boletín risponde e basta quello. Ho riprovato più volte a distanza di minuti, senza cambiare rete né strumenti: **nessun aggiramento**. Probabile filtro sugli indirizzi stranieri; prima di costruire va verificato a mano da un browser in Spagna. Se resta così, sono 3 documenti all'anno da inserire a mano.
- **Dati 2027.** Per ora sono pubblicati solo da Cataluña, País Vasco e Navarra. Le altre comunità escono tra gennaio e aprile 2027 (Murcia a gennaio, Valencia e Baleari a inizio febbraio, Andalucía e Aragón a marzo, Canarias ad aprile). Il test ha usato i calendari 2026: stessi documenti, stesso impaginato, anno dopo anno.
- **Due convocatorie e casi speciali** che il sito deve mostrare:
  - Navarra ha una parte scritta anticipata ad aprile/maggio solo per la scuola a distanza (EOIDNA);
  - in Andalucía l'inglese C1 è il 5/6 solo per l'EOI Corduba (modello 2);
  - in Navarra il francese A2 è l'8/5 solo per l'EOI di Tudela.

  Il lettore li marca nella colonna `nota` o nella convocatoria.
- **Licenze.** Sono boletines e pagine di amministrazioni pubbliche: date e fatti, con la fonte citata. Valutazione di buon senso, non un parere legale.

## 6. Fonti

- Boletines: [BOJA 46/2026](https://www.juntadeandalucia.es/boja/2026/46/BOJA26-046-00026-3164-01_00334384.pdf), [BOCM 25/3/2026](https://bocm.es/boletin/CM_Orden_BOCM/2026/03/25/BOCM-20260325-12.PDF), [DOGV 10296](https://dogv.gva.es/datos/2026/02/05/pdf/2026_3622_es.pdf), [BOCYL 24/2/2026](https://bocyl.jcyl.es/boletines/2026/02/24/pdf/BOCYL-D-24022026-37-28.pdf), [DOCM 28/2026](https://docm.jccm.es/docm/descargarArchivo.do?ruta=2026%2F02%2F11%2Fpdf%2F2026_727.pdf&tipo=rutaDocm), [BORM 14/2026](https://www.borm.es/services/anuncio/ano/2026/numero/181/pdf?id=840845), [BOIB 17/2026](https://www.caib.es/eboibfront/pdf/ca/2026/17/1211874), [BOIB 14/2026](https://www.caib.es/eboibfront/pdf/ca/2026/14/1211310), [BOPA 28/2026](https://www.asturias.es/bopa/2026/02/11/2026-00845.pdf), [DOE 21/2026](https://doe.juntaex.es/pdfs/doe/2026/210o/26060238.pdf), [BOA, delibera 13/3/2026](https://www.boa.aragon.es/cgi-bin/EBOA/BRSCGI?CMD=VEROBJ&MLKOB=1441023330505).
- Pagine e allegati delle Consejerías:
  - [Cataluña, calendari](https://educacio.gencat.cat/ca/serveis-tramits/proves/proves-lliures-obtencio-titols/convocat-ordinaria-idiomes/calendari/);
  - [Canarias](https://www.gobiernodecanarias.org/educacion/web/idiomas/pruebas/pruebas_certificacion/pruebas_certificacion_idiomas_eoi/) (apéndices I e II del BOC 77/2026);
  - [Euskadi, calendario 2026-27](https://www.euskadi.eus/contenidos/informacion/eoi_matricula_libre/es_def/adjuntos/Calendario-Examenes-Anexo-II2026_2027-definitivo-1.pdf);
  - [Navarra, calendario 2026-27](https://www.educacion.navarra.es/documents/27590/0/ANEXO+2%C2%BA+calendario+ex+escritos+26-27.pdf/3755a7a2-075b-3b76-97d7-917214618cb2);
  - [Aragón, trámite 1189](https://www.aragon.es/tramitador/-/tramite/escuelas-oficiales-de-idiomas/pruebas-de-certificacion-alumnado-oficial-y-libre);
  - [Extremadura, trámite](https://www.juntaex.es/w/0648923).
- Galicia, Cantabria e La Rioja: lette solo tramite i risultati della ricerca web (guide e calendari copiati dalle EOI), **non** dal server. Restano da confermare.
- INE: API JSON `servicios.ine.es/wstempus/js/ES/DATOS_TABLA/56940` (Cifras de Población, 1/1/2025).
