# Intelaiatura – Opportunità "grandi" (≥10.000 €/anno) con il filtro duro sulle fonti

Data della ricerca: 10 ottobre 2026. Autore: Claude (sessione di ricerca per Massimiliano Cori).
Segue `3-opportunita-diverse.md` (metodo, candidate B e C scartate), `posteggi-test-tecnico.md` (perché BandiPosteggi è fallita: copertura ~1% dai BUR, estrazione corretta 55–65%) e `4-altri-paesi.md` (candidate estere già trovate, qui non ripetute).
Regola: ogni affermazione porta fonte linkata e datata; dove il dato manca, lo dico. Le cifre di ricavo sono stime con assunzioni esplicite. **Un NO documentato vale quanto un sì.**

## 0. Metodo, filtro duro, limiti

**Filtro duro (applicato per primo, prima di tutto il resto)**: i dati necessari devono venire da **al massimo 20 fonti ufficiali strutturate** (API, registri nazionali/regionali, gazzette, albi unici, feed), **raggiungibili da script** (HTTP status e formato verificati dal server il 10/10/2026) e con **copertura ≥90% del fenomeno**. Scartato subito tutto ciò che vive su migliaia di siti comunali, albi pretori, siti di singole aziende o di singoli enti di formazione (è la causa dei due fallimenti BandiChiari e BandiPosteggi).

Poi le 5 condizioni: (1) pagano aziende/professionisti e **si paga già** per informazioni simili (prezzi, concorrenti); (2) = filtro duro; (3) domanda Google long-tail con SERP debole (PDF/istituzionali, nessun aggregatore) o comunità/directory dove quel pubblico cerca; (4) due parti da collegare; (5) zero lavoro umano, zero responsabilità legale/medica/finanziaria; Italia o inglese.

**Strumenti**: `curl` dal server (status, content-type, dimensione, `Last-Modified`), Google Autocomplete (`suggestqueries.google.com`, hl=it/gl=it, en/gb, en/us; ~130 query), ricerca web per prezzi e composizione delle SERP, download e lettura dei file aperti (ANAC SOA: 100 MB letti e contati). Script e campioni in `scratchpad/ric5/` (sessione).
**Limiti dichiarati**: nessun Keyword Planner/Semrush. **Dal nostro proxy**: gse.it risponde 403 (anti-bot F5), fondimpresa.it, rna.gov.it e bandi.openpolis.it non rispondono (000); il WebFetch non risolve contrattipubblici.org, telemat.it, go.laingbuisson.com, api-portal.service.cqc.org.uk (per questi ho usato `curl`, che funziona, e gli estratti di ricerca). L'API CKAN di dati.anticorruzione.it è dietro un WAF che rifiuta a intermittenza ("Request Rejected"): i file di download diretto rispondono 200, ma un secondo download dello stesso CSV ha dato 403. Dal computer di Massimiliano tutto è raggiungibile normalmente.

---

## 1. Il filtro duro, direzione per direzione (tutte verificate il 10/10/2026)

| # | Direzione | Fonti (n.) | HTTP / formato (dal server) | Copertura | **Filtro duro** |
|---|---|---|---|---|---|
| I1 | **ANAC BDNCP: chi vince cosa** (aggiudicatari, affidamenti diretti, subappalti) per Comune e fornitore | **1** (dati.anticorruzione.it) | catalogo 200; dataset `cig` mensile `20261001-cig_json.zip` **200, 137 MB, Last-Modified 5/10/2026**; OCDS bulk 2026/03.json 200 (748 MB); `aggiudicatari_csv.zip` 403 al 2° tentativo (WAF); API CKAN 403 | per legge tutti i CIG passano dalla BDNCP ([ANAC, Relazione 2025: 287.421 appalti ≥40k](https://www.lavoripubblici.it/news/stampa/35699)); l'OCDS copre solo >40.000 € ([OCP](https://data.open-contracting.org/en/publication/117)); copertura sotto-soglia **da misurare** | **PASSA** (con test) |
| I2 | **ANAC attestazioni SOA** (imprese qualificate per categoria/regione, scadenze) | **1** | `attestato_CKAN.csv` **200, 100,6 MB, Last-Modified 9/9/2026**; letto: 474.434 righe, 16 colonne, **35.918 attestazioni valide ("PUBBLICO"), 35.540 imprese**; `categorie_rilasciate_CKAN.csv` 200 (60 MB) poi 403 | 100% (è il casellario ufficiale) | **PASSA** |
| I3 | **Aliquote IMU/TARI/addizionali per Comune** | **1** (MEF, Portale federalismo fiscale; prospetto aliquote obbligatorio dal 2025, [QuotidianoPiù](https://www.quotidianopiu.it/dettaglio/10783129/imu-prospetto-delle-aliquote-e-aggiornamento-delle-linee-guida)) | [portale 200](https://www.portalefederalismofiscale.gov.it/portale/); [consultazione delibere 200](https://www1.finanze.gov.it/finanze2/dipartimentopolitichefiscali/fiscalitalocale/IUC_newDF/sceltaregione.htm) (HTML, nessun CSV unico trovato) | 100% | PASSA |
| I4 | **Prezzari regionali opere pubbliche** | **20** (Regioni) | Lombardia: PDF/XLS/HTML/**XML**, ~40.000 voci, DGR 27/4/2026 ([Regione](https://www.regione.lombardia.it/infrastrutture-trasporti-e-mobilita/opere-pubbliche/prezzario-regionale-dei-lavori-pubblici/ser-prezzario-infr)); Veneto on-line ([200](https://www.regione.veneto.it/web/lavori-pubblici/prezzario-regionale)); Puglia DGR 774 del 16/6/2026 | 100% | PASSA |
| I5 | Comunità energetiche (CER) ammesse | 1 (GSE) | gse.it **403** dal server; la mappa GSE è un'app ([edotto](https://edotto.com/articolo/comunita-energetiche-online-la-vetrina-gse-come-funziona-per-le-imprese)) | 100% | PASSA (ma vedi cond. 3) |
| I6 | Impianti FER in richiesta di connessione / autorizzazione | 1 (Terna Econnextion) + MASE + 20 Regioni | [Terna 200](https://www.terna.it/it/sistema-elettrico/dati-sistema-elettrico/econnextion) ma app JS senza link CSV; copia regionale su [dati.puglia.it](https://dati.puglia.it/ckan/dataset/richieste-di-connessione-alla-rete-per-impianti-da-fonti-rinnovabili-regione-puglia/resource/6d0a10ca-3cdf-4ff4-ac48-be0a5da339e6) (CSV, 17/12/2025) | alta per >1 MW | PASSA (con headless) |
| I7 | CCNL: rinnovi, tabelle, minimi | 1 (CNEL) | [Archivio 200](https://www.cnel.it/Archivio-Contratti-Collettivi) | 100% | PASSA |
| I8 | Corsi OSS autorizzati (date iscrizione, sedi, prezzi) | 20 Regioni **in teoria**; in pratica le date stanno sui siti di centinaia di enti | Lazio: solo "banca dati offerta formativa" + avvisi corsi irregolari ([Regione Lazio](https://regione.lazio.it/notizie/formazione/corsi-regolarmente-autorizzati-regione)); Piemonte: elenco agenzie, "per i prossimi corsi rivolgersi alle agenzie" ([Regione Piemonte](https://www.regione.piemonte.it/web/node/16433)); Sicilia: un DDS in PDF per ogni corso ([DA 756/2026](https://www.regione.sicilia.it/sites/default/files/2026-07/DA_756_3.pdf)); Veneto/Toscana/Campania: delibere, nessun elenco con date | <50% dalle Regioni | **NON PASSA** (stesso schema di Germania/posteggi) |
| I9 | Corsi gratuiti finanziati (GOL/FSE) per Regione | 20 cataloghi regionali | formati eterogenei (app JS, PDF, Excel); non misurati uno a uno perché la cond. 3 fallisce (sotto) | ? | sospesa |
| I10 | Patentino fitosanitario: corsi/esami per Regione | 20 | Sicilia e Lazio pubblicano locandine/elenchi PDF ufficiali ([Sicilia](https://www.regione.sicilia.it/la-regione-informa/dlgs-15012-corso-formazione-rilasciorinnovo-certificato-fitosanitario-0); [Lazio 2025](https://regione.lazio.it/sites/default/files/2025-03/Corsi-Fitosanitari-2025.pdf)); al Nord i corsi sono degli enti accreditati | 50–70% stimata | **NON PASSA** (solo Sud) |
| I11 | Concorsi sedi farmaceutiche | 20 + [piattaforma ministeriale](https://www.quotidianosanita.it/?p=12943) | nessun bando 2026 trovato (Puglia: ultimo straordinario 2013–2016) | – | flusso ≈ 0 |
| I12 | Albo gestori ambientali (iscritti, esame RT) | 1 | home 200; ricerca iscritti = motore ufficiale (`/Public/RicercaIscritti` 404: path cambiato) | 100% | PASSA (ma motore ufficiale) |
| I13 | Fondi interprofessionali: avvisi | ~20 fondi | fondimpresa.it 000 dal proxy | 100% | esclusa (bandi/incentivi) |
| I14 | Registro Nazionale Aiuti | 1 | rna.gov.it 000 dal proxy | 100% | esclusa (bandi/incentivi) |
| I15 | Startup innovative (open data settimanale) | 1 | [200](https://startup.registroimprese.it/isin/static/startup/index.html) | 100% | PASSA (ma motore ufficiale) |
| I16 | Posteggi, taxi/NCC, chioschi, bandi comunali di ogni tipo, albo pretorio, SCIA, permessi di costruire | migliaia di Comuni | – | – | **NON PASSA** (regola) |
| E1 | **UK CQC: nuove case di cura/registrazioni** | **1** (CQC API, England; +2 per Scozia/Galles) | `api.service.cqc.org.uk` 502, `api.cqc.org.uk` **403 senza chiave**; chiave gratuita dal [developer portal 200](https://api-portal.service.cqc.org.uk/) (Azure APIM, header `Ocp-Apim-Subscription-Key`, [guida Nexla](https://docs.nexla.com/user-guides/connectors/care_quality_commission_api/care_quality_commission_api_auth)); dati OGL, aggiornati ogni giorno, con data di inizio registrazione ([CQC](https://cqc.org.uk/about-us/transparency/using-cqc-data)) | 100% (England) | **PASSA** |
| E2 | UK Contracts Finder (aggiudicazioni) | 1 | [OCDS API 200, JSON](https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search?stages=award&limit=1) | 100% >£12k | PASSA |
| E3 | UK Food Hygiene Ratings (nuove attività alimentari) | 1 (FSA) | [JSON per authority 200, 1,8 MB](https://ratings.food.gov.uk/api/open-data-files/FHRS408en-GB.json) | 100% | PASSA |
| E4 | UK planning applications | ~330 council (PlanIt è un aggregatore terzo, non ufficiale) | – | – | **NON PASSA** |
| E5 | US OSHA inspections/citations | 1 (DOL) | [enforcedata 200](https://enforcedata.dol.gov/views/data_catalogs.php); API DOL gratuita con chiave | 100% federale | PASSA |
| E6 | US FMCSA nuovi vettori (MC authority) | 1 | [L&I register 200](https://li-public.fmcsa.dot.gov/LIVIEW/pkg_register.prc_reg_list) (i venditori dicono che il report legacy è stato ritirato a maggio 2026, [Apify](https://apify.com/foo121/fmcsa-new-authority.md)) | 100% | PASSA |
| E7 | US SAM.gov/USAspending awards; FDA warning letters/510(k); TTB permits; USPTO; SEC Form D; NIH RePORTER | 1 ciascuno | non testati singolarmente: falliscono la cond. 3 (sotto) | 100% | PASSA |
| E8 | US WARN (licenziamenti), licenze liquori/cannabis/edilizia | 50 Stati | – | – | **NON PASSA** |
| E9 | EU TED, Safety Gate, EUIPO, EMA, CORDIS | 1 ciascuno | – | 100% | PASSA (ma cond. 3/esclusioni) |

**Esito del filtro duro**: passano I1, I2, I3, I4, I5, I6, I7, E1, E2, E3, E5, E6 (+ E7/E9 in blocco). Falliscono per fonti disperse: I8, I10, I16, E4, E8. È già un risultato: le uniche fonti "≤20 e ≥90%" in Italia sono registri nazionali (ANAC, MEF, CNEL, GSE, Terna) e i 20 prezzari; tutto ciò che è "corso/avviso/bando con una data" sta su centinaia di siti e ripete il fallimento dei posteggi.

---

## 2. Le direzioni che passano il filtro duro, contro le altre condizioni

### 2.1 Chi fallisce la condizione 3 (aggregatore forte o "l'ente ha già il motore") – con prova

| Direzione | Perché NO | Prova (10/10/2026) |
|---|---|---|
| I3 IMU/TARI per Comune | Domanda fortissima per città ("aliquote imu 2026 comune di roma/milano/torino/genova/napoli/bari", "tari 2026 comune di napoli/sassari/pescara/bari", "addizionale comunale irpef 2026 roma/genova/napoli") **ma** la SERP ha già pagine-città di aggregatori e il pagante B2B compra già da editori | SERP "aliquote IMU 2026 Verona": PDF del Comune + [tuttocalcolato.it/calcolo/imu/verona (200)](https://tuttocalcolato.it/calcolo/imu/verona/) + [mappa PMI.it](https://www.pmi.it/card/imu-mappa-delle-aliquote/doc/7); banca dati a pagamento per commercialisti di [Eutekne](https://www.eutekne.info/Sezioni/Art_679084_aliquote_imu_tasi_tari_e_addizionali_irpef_in_un_unico_servizio.aspx) e aliquote "di tutti i Comuni" già dentro il software [Namirial](https://aggiornamenti-software-vsp.namirial.com/aggiornamenti/namirial/manuali/Ns0018-saldo-imu---flusso-operativo_1.pdf). Chi cerca è il proprietario (consumer), chi paga ha già il dato. |
| I4 Prezzari regionali | Domanda forte per Regione ("prezzario 2026 piemonte/campania/puglia/emilia romagna/basilicata/abruzzo…", "prezzario regionale lombardia 2026 pdf") **ma** aggregatori con pagine per Regione e software già pagato | [TeamSystem "prezzari – tutte le regioni" (200)](https://www.teamsystem.com/construction/prezzari/tutte-le-regioni/) con pagine per edizione (Puglia 2026, Lombardia 2026); [testo-unico-sicurezza.com](https://www.testo-unico-sicurezza.com/prezzari-regionali-download.html); DEI a pagamento; Lombardia e Piemonte hanno già piattaforme digitali di consultazione. Nessuna "due parti". |
| I5 CER | Il GSE ha già la **mappa nazionale delle CER con i contatti (Vetrina)** per chi vuole aderire | [edotto, Vetrina GSE](https://edotto.com/articolo/comunita-energetiche-online-la-vetrina-gse-come-funziona-per-le-imprese); oltre 4.800 configurazioni al 31/8/2026 ([segretaricomunalivighenzi](https://www.segretaricomunalivighenzi.it/?p=71557)). Regola "l'ente ha il motore" → scarto. Autocomplete "elenco comunità energetiche gse/veneto/lombardia" conferma che la gente cerca proprio il GSE. |
| I6 Impianti FER | Terna ha già la mappa/dashboard pubblica (Econnextion); autocomplete per Comune **vuoto** ("impianto fotovoltaico comune di", "parco eolico comune di", "agrivoltaico comune di" → nessuna proposta; "econnextion" → "dashboard econnextion") | Terna 200 (app JS). Domanda inesistente nella forma "per Comune"; pubblico pagante (developer) compra report da società specializzate, vendita B2B senza pubblico. |
| I7 CCNL | SERP presidiata da testate e studi (lavoroediritti, pmi.it, money.it, sindacati) e il dato richiede interpretazione | autocomplete "ccnl commercio 2026 tabelle retributive", "rinnovo ccnl 2026 bancari/commercio/metalmeccanici" = domanda enorme ma già servita; cond. 5 debole (tabelle da interpretare). |
| I8 Corsi OSS | Oltre a fallire il filtro duro: aggregatori forti sulla stessa query | autocomplete per 12 città ("corso oss torino 2026", "corso oss palermo gratuito 2026", "corso oss regione lazio gratuito 2026 roma/frosinone/viterbo/latina"); SERP "corso oss gratuito bologna 2026" = [ticonsiglio.com](https://www.ticonsiglio.com/corso-gratuito-lavorare-operatore-socio-sanitario-oss-bologna/) ×4 + [Emagister](https://www.emagister.it/corsi_oss-ek38424.htm) (pagine per città); SERP "corso oss torino 2026" = ENAIP, ticonsiglio, Emagister. Emagister vende lead ai centri (CPL "fino a 15 €", [affi.io](https://affi.io/m/emagister)): si paga, ma il mercato dei lead è già suo. |
| I9 Corsi GOL/gratuiti per Regione | Idem: ticonsiglio.com domina | SERP "corsi gratuiti finanziati dalla regione puglia 2026" = 5 risultati ticonsiglio + Emagister ([ricerca](https://www.ticonsiglio.com/corsi-formazione-gratuiti-puglia-qualifica-professionale/)). |
| I12 Albo gestori ambientali | L'Albo ha il motore "ricerca iscritti" (autocomplete: "albo gestori ambientali ricerca iscritti/autorizzazioni"); "smaltimento rifiuti speciali [città]" = Google local | – |
| I15 Startup innovative | Motore ufficiale con ricerca; domanda minima ("startup innovative elenco", "milano") | – |
| E2 UK Contracts Finder | Autocomplete **vuoto** per "who won the contract council"; aggregatori paganti già forti (Tussell, BiP) | – |
| E3 UK FSA | Domanda solo consumer ("food hygiene rating check/near me"); [scoresonthedoors](https://www.scoresonthedoors.org.uk/) e ratings.food.gov.uk già fanno le pagine; il taglio B2B "nuove attività alimentari" è la candidata C USA già scartata in `3-opportunita-diverse.md` | – |
| E5 US OSHA | "osha violations list by company" ha domanda, ma osha.gov ha l'establishment search e [Violation Tracker](https://violationtracker.goodjobsfirst.org/) (403 dal server, è un sito forte); già venduto a 3,5–15 $/1.000 record su Apify e 29 $/mese ([ricerca](https://apify.com/tagadanar/osha-inspection-leads)) | si paga (prova), ma SERP e vendita già occupate |
| E6 US FMCSA | "new mc authority list" ha domanda, ma decine di venditori di lead (Apify 3,5–20 $/1.000; abbonamenti 49–497 $/mese citati) occupano le SERP; la fonte legacy sarebbe stata ritirata a maggio 2026 (non verificato) | – |
| E7 US federali (SAM, FDA, USPTO, SEC, NIH) | GovTribe/HigherGov, FDAzilla, Google Patents/Justia, Crunchbase, SciLeads: aggregatori forti e motori ufficiali; vendita B2B negli USA senza pubblico (stessa conclusione della candidata C) | – |
| E9 EU | TED: decine di aggregatori; Safety Gate/RASFF: alert gratuiti ufficiali via email (motore dell'ente); EUIPO: esclusa (sorveglianza marchi); EMA: medica; CORDIS: motore ufficiale | – |

### 2.2 Le tre che restano in piedi: tabelle delle 5 condizioni

#### A. "ChiLavoraColComune" – esiti ANAC per Comune e per fornitore (Italia) — **taglio verticale di una direzione esclusa: da confermare con Massimiliano**

**Idea in una riga**: una pagina per ogni stazione appaltante (7.900 Comuni + ASL, università, partecipate) con gli **affidamenti diretti e le aggiudicazioni** degli ultimi 12 mesi (fornitore, oggetto, importo, procedura, data, CIG, link ANAC) e una pagina per ogni fornitore (cosa ha vinto, dove). Gratis: le liste. A pagamento: avviso "nuovo affidamento nella tua provincia/categoria" e "contratti del tuo settore in scadenza nei prossimi 6 mesi" (= la gara sta per uscire). Fase 2: bacheca subappalti/ATI (chi ha vinto cerca subappaltatori locali; dataset `subappalti` ANAC).

| Cond. | Esito | Prova |
|---|---|---|
| 1. Soldi + si paga già | **SÌ** | Mercato: 287.421 appalti ≥40k nel 2025 per 309,7 mld €; **il 95% di servizi/forniture è affidamento diretto** ([Relazione ANAC 2025 via Teleborsa, 21/4/2026](https://www.teleborsa.it/News/2026/04/21/corruzione-anac-boom-di-affidamenti-diretti-e-consulenze-109.html); [LavoriPubblici](https://www.lavoripubblici.it/news/stampa/35699)). Si paga già: **Atoka PA (Cerved)**, "il motore di ricerca dei contratti pubblici italiani", 68 milioni di contratti, 1,7 milioni di fornitori, prova gratuita 7 giorni poi a pagamento, venduto per "trovare nuovi clienti… anticipare l'uscita di nuovi bandi analizzando le scadenze dei contratti" ([contrattipubblici.org, 200, testo letto dal server](https://contrattipubblici.org/)); Telemat vende abbonamenti (sconto abbonati di 70–100 € sui corsi, [listino corso 17/7/2026](https://www.telemat.it/wp-content/uploads/2026/06/TEL38.16Wa_Assicurazioni_17luglio2026.pdf)); InfoPlus vende servizi "Novità, Navigazione, MepaFull" in abbonamento ([appendice](https://infoplus.appalti.org/Documenti/Appendice_generale_consulenza_CON_SERVIZI_INTEGRATI.pdf)). **Prezzo di Telemat/InfoPlus non trovato pubblicamente** (lo dico). |
| 2. Filtro duro | **SÌ, con un test** | 1 fonte: `cig` mensile (JSON zip 137 MB, 5/10/2026), `aggiudicatari`, `partecipanti`, `subappalti`, `stazioni-appaltanti`, OCDS bulk (748 MB/mese). Licenza CC BY 4.0 ([OCP](https://data.open-contracting.org/en/publication/117)). **Da misurare**: (a) quota degli affidamenti sotto 40.000 € presente nel dataset `cig`/`smartcig` (OCDS li esclude); (b) WAF: 403 intermittenti sui download; (c) peso: non gira su Netlify, serve una macchina (GitHub Actions gratuito: 7 GB RAM, 6 h/job). |
| 3. Domanda + SERP debole | **SÌ sul taglio "per ente"**, NO sul taglio "per fornitore" | Autocomplete: "affidamento diretto comune di milano / genova", "affidamenti diretti comune san ferdinando di puglia", "appalti aggiudicati anas / rfi / anac", "esito gara appalto vigilanza estar toscana", "esito gara tpl campania", "determina di aggiudicazione affidamento diretto", "aggiudicazioni anac". SERP "affidamento diretto comune di milano 2026": **solo PDF di determine** (Verona, ARERA, Polimi, Comune di Firenze) ([ricerca](https://www.arera.it/stampa-bandi-gara/dettaglio/fornituraacquamilano25)); la dashboard ANAC Analytics (Superset, [200](https://dati.anticorruzione.it/superset/dashboard/appalti/)) non è indicizzata; Atoka PA è dietro registrazione. **Sul fornitore** invece atoka.io ha già pagine pubbliche per azienda ([es.](https://atoka.io/public/it/azienda/publika-servizi-srl/b6f842577336)) e "appalti vinti da" non ha autocomplete → le pagine-fornitore non porterebbero traffico. |
| 4. Due parti | **SÌ** | Vincitori (devono subappaltare/comprare in loco) ↔ fornitori locali/subappaltatori; stazioni appaltanti ↔ fornitori per i prossimi affidamenti. Dataset `subappalti` esiste. |
| 5. Lavoro ~0, responsabilità | **SÌ con cautela** | Si ripubblicano dati aperti CC BY con link al CIG. Cautela: le ditte individuali hanno nome = dato personale (mostrare solo società, o solo denominazione senza dati ulteriori). Nessuna consulenza. |

**Gratis/a pagamento**: gratis pagine ente, pagine provincia, "come funziona l'affidamento diretto" (link ANAC); a pagamento 190 €/anno "avvisi affidamenti nella mia provincia e categoria" + "contratti in scadenza", 390 €/anno per consulenti/associazioni con export.
**Stima prudente** (assunzioni: 8.000 pagine-ente, indicizzazione lenta nei mesi 1–4; mese 6 ≈ 1.500 visite/mese, mese 12 ≈ 5.000; totale 12 mesi ≈ 30.000; pubblico quasi solo B2B; iscritti all'avviso 5% = 1.500; paganti 2% a 190 € = 30 → 5.700 €; 5 abbonati a 390 € = 1.950 €): **12 mesi ≈ 5.000–7.500 €; 18 mesi run-rate ≈ 10.000–14.000 €/anno** (iscritti 3.000; paganti 60 a 190 € + 12 a 390 €). Soglia 10k: raggiungibile **solo** se il test tecnico passa e se Massimiliano scioglie l'esclusione "gare d'appalto" (qui si pubblicano esiti, non bandi).
**Ore di costruzione (riuso del motore)**: 35–45 h: pipeline dati pesante (scarico mensile 137 MB, parsing JSON, normalizzazione stazioni appaltanti su codice ISTAT comune) + `genera.py` riusato per pagine ente/provincia/regione (riuso ≈ 60%, perché cambia la struttura dati da "sessioni" a "contratti") + modulo Avvisami con filtri categoria/provincia.
**Rischi**: (a) esclusione di Massimiliano; (b) copertura sotto-soglia sconosciuta; (c) WAF ANAC (403 a intermittenza, già visto 3 volte oggi); (d) Cerved/Atoka può aprire pagine-ente pubbliche in un giorno; (e) ritardi: ANAC aggiorna il 2 del mese, i dati arrivano 30–60 giorni dopo l'affidamento (poco utile per "scadenze"); (f) dati personali delle ditte individuali.

#### B. "CareOpenings" – nuove case di cura registrate CQC, per città (Regno Unito, inglese)

**Idea in una riga**: pagina per ogni città/contea con le case di cura, agenzie domiciliari e cliniche **appena registrate** (dalla data di inizio registrazione dell'API CQC) e quelle in apertura; gratis la lista e l'avviso mensile per contea; a pagamento il feed settimanale con filtri (tipo, posti, gruppo) per fornitori, agenzie di personale, farmacie, studi legali del settore.

| Cond. | Esito | Prova |
|---|---|---|
| 1 | **SÌ, prezzi alti** | LaingBuisson CareSearch: **Essential £1.575, Premium £2.999, Complete £5.445 + VAT/anno** ("refine by geography, CQC rating, group operator, registered beds, build status", [go.laingbuisson.com/caresearch, 200](https://go.laingbuisson.com/caresearch), pagina non datata); Carterwood Analytics in abbonamento ([Caring Times](https://caring-times.co.uk/?p=31007)); CareDB vende export bulk dall'API CQC ([caredb.co.uk](https://caredb.co.uk/bulk-data)); Apify 8 $/1.000 record con "monitor mode: only new registrations" ([Apify](https://apify.com/scrapesage/uk-cqc-care-provider-leads)). |
| 2 | **SÌ** | 1 fonte (England), API gratuita con chiave, dati OGL aggiornati ogni giorno con `registrationDate` ([CQC](https://cqc.org.uk/about-us/transparency/using-cqc-data)); dal server 403/502 senza chiave: la chiave va creata dal PC di Massimiliano (gratis, 2 minuti). Scozia e Galles: 2 regolatori in più (non testati). |
| 3 | **PARZIALE** | Autocomplete en-GB: "new care homes opening in birmingham / kent / surrey / 2026", "new care homes opening 2026 near me", "care homes opening soon". SERP "new care homes opening in Kent 2026": notizie [LaingBuisson News](https://www.laingbuissonnews.com/care-markets-content/oakland-care-opens-72-bedroom-setting-in-kent/) (a pagamento), Caring Times, pagine degli operatori: **nessuna lista per città** → vuoto reale, ma **domanda piccola** (3 città in autocomplete; "new care home registrations", "newly registered care homes", "new care home jobs 2026" → vuoti). |
| 4 | SÌ | Nuove strutture (devono assumere e comprare) ↔ personale/fornitori/agenzie. |
| 5 | SÌ | Si ripubblica il registro (OGL, con attribuzione CQC). Nessun giudizio sulla qualità delle cure (non mostrare i rating). |

**Stima prudente** (assunzioni: 400 pagine città/contea; mese 12 ≈ 3.000 visite/mese; totale 12 mesi 18.000; iscritti 5% = 900; feed B2B £290/anno al 1% = 9 → £2.600; lead a fornitori £0): **12 mesi ≈ £2.000–3.000; 18 mesi run-rate ≈ £4.000–6.000**. Sotto i 10k: la domanda è piccola e la vendita B2B in inglese parte da zero. **Ore**: 15–20 (riuso di `genera.py` ≈ 80%: "sede" = location, "sessione" = data di registrazione). **Rischi**: CQC potrebbe aggiungere un filtro "newly registered" al suo motore; LaingBuisson/Carterwood hanno già i clienti.

#### C. "SOA in scadenza" – casellario ANAC delle attestazioni (Italia) — RISERVA

| Cond. | Esito | Prova |
|---|---|---|
| 1 | SÌ | 35.540 imprese attestate; l'attestazione si paga alla SOA con tariffa regolata (coefficiente R 2026 = 1,550, [ANAC 1/4/2026 via LavoriPubblici](https://www.lavoripubblici.it/news/tariffe-soa-2026-coefficiente-r-anac-1550-37827)); verifica triennale obbligatoria entro 90 giorni dalla scadenza; dal file: **6.116 attestazioni valide scadono (triennale) nel 2026, 9.274 nel 2027, 9.437 nel 2028**. Le SOA (≈15 società) e i consulenti SOA vivono di queste scadenze; "soa in vendita / aziende soa in vendita / soa og1-og2-og3 in vendita" e "cessione soa" in autocomplete = mercato di compravendita di imprese attestate. |
| 2 | **SÌ** | 1 CSV ufficiale (100 MB, 9/9/2026), 16 colonne con stato, SOA, provincia, tre date di scadenza. |
| 3 | **NO per regola** | ANAC ha già il motore pubblico ([RicercaAttestazioniWebApp, 200](https://servizi.anticorruzione.it/RicercaAttestazioniWebApp/)) con "elenco imprese qualificate per Regione, categoria e classifica" ([UniPa](https://www.unipa.it/Servizi-On-Line-ANAC/)); l'autocomplete lo conferma ("anac imprese con attestazione soa"). Resta solo il taglio "scadenze per SOA/consulenti" (= liste per contatto a freddo, vietate dalla regola 3) e il taglio "SOA in vendita" (marketplace M&A). |
| 4 | SÌ | Imprese ↔ SOA/consulenti; venditori ↔ compratori di imprese attestate. |
| 5 | **NO sul marketplace** | La cessione di quote/ramo con SOA è materia legale delicata (Cass. 22075/2023: la SOA non passa automaticamente, [LexCED](https://www.lexced.com/?p=872784)); responsabilità e lavoro umano non azzerabili. |

**Verdetto C**: fonte perfetta, ma l'unico vuoto è un marketplace legale-finanziario. Da tenere come dataset di arricchimento per A (pagina-fornitore con categorie SOA) e per EsamiDiStato, non come sito a sé. Stima se fatta comunque (solo directory + avviso scadenza all'impresa stessa a 29 €): 12 mesi ≈ 1.000–2.000 €.

### 2.3 Note a margine utili alla pipeline esistente (non sono "opportunità grandi")
- **Esame guida turistica nazionale** (1 fonte, MiTur): autocomplete "esame guida turistica 2026 date / calendario orali / risultati / quando" → pagina da aggiungere a **EsamiDiStato** (pagina MiTur spostata: 404 sul vecchio URL).
- **Esame OAM** ("esame oam 2026 date / calendario"), **esame Responsabile Tecnico Albo gestori** ("esame responsabile tecnico albo gestori ambientali", "quiz…"): 1 fonte ciascuno, piccoli, stessa destinazione.
- **Patentino fitosanitario per Regione** (I10): domanda forte al Sud ("patentino fitosanitario sicilia/piemonte/basilicata/sardegna/lazio 2026"), fonti ufficiali regionali in PDF solo dove la Regione tiene i corsi; possibile sito piccolo (≤3k €/anno), non grande.

---

## 3. Classifica e verdetto

| # | Candidata | Filtro duro | Cond. 1 | 3 | 4 | 5 | Pubblico pagante | 12 mesi | 18 mesi (run-rate) | Ore |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **A – Esiti ANAC per ente ("ChiLavoraColComune")** | SÌ (1 fonte; test su sotto-soglia e WAF) | SÌ (Atoka PA, Telemat, InfoPlus) | SÌ per ente / NO per fornitore | SÌ | SÌ con cautela | fornitori PA, consulenti gare, associazioni | 5.000–7.500 € | **10.000–14.000 €** | 35–45 |
| 2 | B – Nuove strutture CQC (UK) | SÌ (1 fonte, chiave gratuita) | SÌ (LaingBuisson £1.575–5.445) | PARZIALE (domanda piccola) | SÌ | SÌ | fornitori/agenzie del care | £2.000–3.000 | £4.000–6.000 | 15–20 |
| 3 | C – SOA in scadenza | SÌ (1 CSV) | SÌ | NO (motore ANAC) | SÌ | NO (marketplace) | SOA, consulenti, compratori | 1.000–2.000 € | 2.000–3.000 € | 10–15 |
| – | IMU, prezzari, CER, Terna, CCNL, OSS, GOL, Albo gestori, startup, Contracts Finder, FSA, OSHA, FMCSA, US federali, EU | vari | – | **NO** (prove in 2.1) | – | – | – | – | – | – |

**VERDETTO NETTO**: con il filtro duro applicato per primo, **nessuna direzione supera tutte le condizioni con una stima prudente ≥10.000 €/anno entro 18 mesi senza una condizione aperta**. La sola che ci arriva sulla carta è **A**, e ci arriva con due "se": (1) Massimiliano deve dire sì a un taglio verticale di una categoria che aveva escluso (si pubblicano **esiti**, non bandi: le SERP degli esiti sono PDF di determine, quelle dei bandi sono di Telemat & C.); (2) il test tecnico sotto deve dimostrare che il dataset copre gli affidamenti sotto 40.000 € (dove sta il 95% dei contratti e il pubblico dei piccoli fornitori) e che i file si scaricano stabilmente. **B** è un buon sito "da 3–5k" in inglese, non uno da 10k; **C** è un dataset da riusare, non un sito.

Il motivo di fondo è strutturale e vale per le prossime ricerche: in Italia i dati "≤20 fonti, ≥90%" esistono solo nei registri nazionali (ANAC, MEF, CNEL, GSE, Terna, Registro imprese) e lì **l'ente ha già il motore o un editore ha già l'aggregatore**; i dati con una **data e una scadenza** per cui si pagherebbe un avviso (corsi, bandi, avvisi, posteggi) stanno quasi sempre su centinaia o migliaia di siti. Le eccezioni sono gli esami nazionali a poche fonti (il modello EsameB1/EsamiDiStato), che però valgono 2–4k l'uno.

---

## 4. Test tecnico a costo zero per A (1–3 giorni, solo Claude) — da fare SOLO dopo il sì di Massimiliano sull'esclusione

**Giorno 1 – scarico e copertura**
1. Scaricare da `dati.anticorruzione.it` (UA browser, 1 richiesta ogni 2 s, cartella fuori dal repository): `20261001-cig_json.zip` (137 MB), `20260901-cig_json.zip`, `aggiudicatari_json.zip`, `stazioni-appaltanti_json.zip`, `subappalti` (se il WAF lo lascia). Registrare per ogni file: status, byte, tempo. **Soglia**: 5 file su 5 scaricati al primo o secondo tentativo; altrimenti STOP (fonte non stabile).
2. Contare nel `cig` di ottobre: n. CIG pubblicati nel mese, n. con importo < 40.000 €, n. con importo < 5.000 €, n. con aggiudicatario valorizzato (incrocio con `aggiudicatari`), n. stazioni appaltanti distinte di tipo Comune (codice ISTAT). **Soglie**: ≥ 100.000 CIG/mese, di cui ≥ 50% sotto 40.000 € con aggiudicatario presente in ≥ 60% dei casi; ≥ 4.000 Comuni con almeno un affidamento nel mese.
3. Campione di verità: prendere 20 affidamenti diretti pubblicati tra l'1/7 e il 31/8/2026 nelle sezioni "Amministrazione trasparente" di 5 enti (Comune di Firenze `affidamenti.comune.fi.it`, Comune di Verona, ARERA, Politecnico di Milano, un Comune Municipium) e cercarli per CIG nei dataset. **Soglie**: ≥ 16/20 presenti (80%); fornitore, importo e oggetto corretti in ≥ 18 dei presenti (90%); ritardo mediano tra determina e presenza nel dataset ≤ 60 giorni.

**Giorno 2 – pipeline e pagine**
4. Parsing completo di un mese in ≤ 60 minuti e ≤ 6 GB di RAM (limiti di un runner GitHub Actions gratuito); generazione di 50 pagine-ente di prova (Milano, Genova, Firenze, Bari, Verona + 45 Comuni medi) con `genera.py` adattato. **Soglia**: ogni pagina ha ≥ 10 affidamenti 2026 nei 5 grandi e ≥ 3 nei 45 medi.
5. Verifica dati personali: quota di aggiudicatari che sono persone fisiche/ditte individuali; regola di pubblicazione (solo società, oppure solo denominazione e CIG).

**Giorno 3 – domanda**
6. Search Console non c'è ancora: usare l'autocomplete su 30 Comuni ("affidamento diretto comune di X", "affidamenti comune di X", "fornitori comune di X") e annotare quante proposte compaiono. **Soglia**: ≥ 10 Comuni su 30 con almeno una proposta pertinente.

**Decisione**: COSTRUIRE se tutte le soglie dei punti 1–4 sono superate e il punto 6 dà ≥10/30; costruire SOLO le pagine-ente (niente pagine-fornitore). FERMARE se il punto 1 o il punto 3 falliscono: una fonte che non si scarica o non copre i piccoli affidamenti non vale 35–45 ore. Il test a 45 giorni dopo la pubblicazione resta quello standard (≥40 pagine indicizzate, ≥200 clic, ≥60 iscritti di cui ≥10 B2B dichiarati).

---

## 5. Riepilogo HTTP status delle fonti chiave (10/10/2026, `curl` dal server, UA browser)

| Fonte | Status | Nota |
|---|---|---|
| dati.anticorruzione.it/opendata (catalogo, dataset cig/aggiudicatari/subappalti/SOA/stazioni) | 200 | 20 dataset; download diretti 200; `aggiudicatari_csv.zip` 403 al 2° tentativo; API CKAN "Request Rejected" (WAF F5) |
| `…/cig/filesystem/20261001-cig_json.zip` | 200, 137,6 MB, 5/10/2026 | mensile |
| `…/ocds/filesystem/bulk/2026/03.json` | 200, 748 MB, 8/4/2026 | 01, 06–10 del 2026: 404 |
| `…/attestazioni-soa-v2/filesystem/attestato_CKAN.csv` | 200, 100,6 MB, 9/9/2026 | letto e contato |
| servizi.anticorruzione.it/RicercaAttestazioniWebApp | 200 | motore ufficiale SOA |
| dati.anticorruzione.it/superset/dashboard/appalti | 200 | Analytics ufficiale (non indicizzata) |
| contrattipubblici.org (Atoka PA) | 200 | aggregatore a pagamento, 68 M contratti |
| portalefederalismofiscale.gov.it; www1.finanze.gov.it IUC | 200 | HTML, nessun CSV unico |
| tuttocalcolato.it/calcolo/imu/verona | 200 | aggregatore IMU per città |
| teamsystem.com/construction/prezzari/tutte-le-regioni | 200 | aggregatore prezzari |
| regione.lombardia.it prezzario; regione.veneto.it prezzario | 200 | XML/online |
| cnel.it Archivio contratti | 200 | – |
| gse.it (home, mappe) | 403 | anti-bot dal nostro proxy |
| terna.it Econnextion | 200 | app JS, nessun CSV |
| startup.registroimprese.it | 200 | – |
| albonazionalegestoriambientali.it | 200 (home) / 404 (vecchio path ricerca) | – |
| rna.gov.it, fondimpresa.it, bandi.openpolis.it | 000 | non raggiungibili dal proxy |
| regione.sicilia.it (DDS corsi OSS, locandine fitosanitario) | 200 | PDF singoli |
| api.cqc.org.uk /public/v1 | 403 (senza chiave) | api.service.cqc.org.uk 502; portal 200 |
| go.laingbuisson.com/caresearch | 200 | prezzi letti dall'estratto di ricerca |
| ratings.food.gov.uk (FHRS JSON) | 200 | 1,8 MB per authority |
| contractsfinder OCDS Search | 200 JSON | – |
| enforcedata.dol.gov (OSHA) | 200 | – |
| li-public.fmcsa.dot.gov register | 200 | – |
| violationtracker.goodjobsfirst.org | 403 | sito forte, anti-bot |
| ministeroturismo.gov.it esame guida turistica | 404 | pagina spostata |
