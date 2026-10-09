**Nota sul metodo:** il proxy ha bloccato il fetch diretto di incentivi.gov.it, mimit.gov.it, rna.gov.it, opencoesione.gov.it, fasi.eu e aziendabanca.it. Tutto quello che segue viene dai risultati di ricerca (estratti indicizzati), non da pagine o file che ho aperto.

## Verdetto netto
**No, non così com'è.** Con sessioni settimanali, un solista più Claude non ottiene un archivio "completo e affidabile" da vendere come fonte autorevole. Si può arrivare a circa il 60-70% dei bandi aperti rilevanti per le PMI (ipotesi), ma con stati (aperto/chiuso) spesso vecchi di giorni. Per un commercialista questo è il difetto che pesa di più. Diventa realistico solo a due condizioni:
- **(a)** uno scraper automatico che gira ogni giorno da solo, mentre le sessioni Claude servono solo a revisione e arricchimento;
- **(b)** un posizionamento come radar e pre-screening ("verifica sempre il bando ufficiale"), oppure un perimetro ristretto: una o due regioni più MIMIT e camere di commercio.

## 1. Volumi
**DATI VERIFICATI**
- **Relazione MIMIT 2025 (dati 2024, fonte RNA):** 2.374 interventi agevolativi attivi nel 2024, di cui 300 delle amministrazioni centrali e 2.074 regionali. Nel 2023 erano 2.723. Sono *misure*, non singoli bandi, e includono 101 misure fiscali automatiche e 62 strumenti di garanzia.
- **incentivi.gov.it nel 2024:** oltre 1.000 incentivi pubblicati e 374 amministrazioni (comunicato MIMIT, aprile 2024). Poco dopo, con il premio "PA a colori" (Forum PA 2024), oltre 1.400. Ripartizione per ente: Regioni e Province 32%, Comuni 31%, Camere di commercio 17%. Non ho trovato un conteggio del 2025 o del 2026.
- **FASI:** il contatore in homepage indica 1.866 "Agevolazioni Attive", 48.761 schede e 1.014 "Fonti". Il dato non è datato.
- **Muffin:** dichiara "oltre 3mila opportunità".

**IPOTESI**
- In un dato momento sono aperti circa 1.500-3.000 bandi in tutto.
- Escono circa 30-60 nuovi bandi a settimana. È una mia stima: non esiste un dato ufficiale. Una cifra di "2.900 bandi l'anno" attribuita al Sole 24 Ore non l'ho potuta verificare.
- I GAL sono circa 200 a livello nazionale (ho trovato solo conteggi regionali: Sicilia 23, Abruzzo 8, Veneto 9, Toscana 7). Le camere di commercio sono circa 60.

## 2. Fonti aperte
**DATI VERIFICATI**
- **incentivi.gov.it, sezione open data:** CSV compresso e JSON, licenza IODL 2.0, che consente il riuso commerciale con attribuzione. Esiste uno schema dei campi documentato (con la nota che alcuni campi sono ancora in via di definizione). Ogni record ha il campo `Data_ultimo_aggiornamento`.
  - I file hanno nomi datati, ad esempio `2025-4-5_opendata-export.csv`.
  - Non ho trovato una frequenza di aggiornamento dichiarata né un'API documentata.
- **OpenCoesione:** licenza CC-BY 4.0, riuso commerciale permesso, oltre 600 dataset. Contiene però progetti e beneficiari finanziati, non bandi aperti.
- **RNA:** è il registro degli aiuti *concessi*, utile per verifiche de minimis e cumulo. Non è un elenco di bandi aperti e non ho trovato un open data con licenza dichiarata.
- **Codice degli incentivi** (D.Lgs. 184/2025, in vigore dal 1/1/2026) e **bando-tipo** (DM 18/6/2026, GU 17/7/2026): spingono verso schede standardizzate e verso "Sistema Incentivi Italia", che collega incentivi.gov.it e RNA. Però l'art. 3 lascia agli enti le proprie piattaforme, quindi la pubblicazione centralizzata non risulta obbligatoria.
- **Portali regionali:** non ho trovato feed RSS o API dei bandi. Lombardia offre open data CC0 con API, ma non un dataset bandi confermato.

## 3. Concorrenti
**DATI VERIFICATI**
- **Muffin:** database aggiornato "in tempo reale" con "algoritmi proprietari basati sull'AI". Circa 30 persone più oltre 200 consulenti nel 2024; più di 65 collaboratori a fine 2025, obiettivo oltre 100 nel 2026; 6,5 M€ di fatturato 2025.
- **Bandosubito:** usa l'AI su "oltre 30 fonti pubbliche" monitorate ogni giorno; ha raccolto un round da 2 M€.
- **FASI:** dichiara 1.014 fonti; il metodo redazionale non è documentato.
- **TeamSystem e Cerved:** dichiarano un "database aggiornato" ma non descrivono il metodo.

**IPOTESI:** tutti usano un modello ibrido, cioè scraping e AI più revisione umana. Nessuno dichiara un processo di verifica.

## 4. Rischi di qualità
**DATI VERIFICATI**
- **Chiusure anticipate:**
  - Marchi+ 2025: aperto alle 12:00 del 4/12/2025, chiuso per esaurimento fondi con effetto dal giorno dopo.
  - CCIAA Cuneo: due bandi chiusi alle 16:30 del 5/5/2025 e alle 8:35 del 6/5/2025.
  - CCIAA Napoli PID: chiusura anticipata nel 2025; nel 2024 le richieste erano 3,7 volte i fondi disponibili.
  - Click day INAIL ISI: risorse esaurite in pochi minuti.
- **Proroghe frequenti**, pubblicate come determine o decreti sui siti degli enti o sul BUR: Unioncamere Lombardia, Regione Marche, Regione Sicilia (proroga dell'8/9/2026), CCIAA Cagliari-Oristano, CCIAA Rieti-Viterbo, tutte nel 2026.

**IPOTESI:** una quota non trascurabile dei bandi aperti cambia stato o date nel corso della propria vita. Con un ciclo settimanale, nei bandi a sportello le chiusure si scoprono anche fino a 7 giorni dopo.

## 5. Cosa resterebbe scoperto
Il processo realistico è questo:
1. import quotidiano automatico dell'open data di incentivi.gov.it (base IODL);
2. scraper sulle pagine bandi di MIMIT/Invitalia, 21 Regioni con le loro finanziarie, circa 60 camere di commercio e le pagine "chiusure/esaurimento fondi";
3. estrazione dei campi da PDF tramite LLM;
4. sessione Claude settimanale per controllo qualità e correzione degli scraper che si rompono.

Resterebbero scoperti o poco affidabili:
- comuni, GAL e fondazioni, centinaia di fonti eterogenee con PDF firmati e formati diversi;
- lo stato in tempo reale dei bandi a sportello e click day;
- i requisiti fini (ATECO, de minimis, cumulo), che vanno interpretati;
- la manutenzione degli scraper, che è il costo nascosto.

I concorrenti hanno da 30 a oltre 65 persone. Il punto in cui un solista può competere è una nicchia territoriale o tematica curata bene.

## Fonti
- https://www.incentivi.gov.it/it/open-data
- https://www.incentivi.gov.it/sites/default/files/2024-01/Metadati_Scheda_Incentivo_1.pdf
- https://www.incentivi.gov.it/sites/default/files/open-data/2025-4-5_opendata-export.csv
- https://www.mimit.gov.it/it/notizie-stampa/portale-incentivi-gov-it-oltre-1000-gli-incentivi-pubblicati-e-374-le-amministrazioni-coinvolte
- https://www.mimit.gov.it/it/notizie-stampa/mimit-il-portale-incentivi-gov-it-vince-il-premio-pa-a-colori-categoria-pa-semplice
- https://www.mimit.gov.it/images/stories/documenti/RELAZIONE_266_2025.pdf
- https://www.mimit.gov.it/images/stories/documenti/Relazione_2024.pdf
- https://www.mimit.gov.it/it/incentivi/bda-banca-dati-anagrafica-per-il-monitoraggio-delle-agevolazioni
- https://opencoesione.gov.it/en/licenza/
- https://opencoesione.gov.it/en/news/dati-aperti-online-2024
- https://www.programmagoverno.gov.it/it/notizie/incentivi-pubblicato-il-nuovo-codice-degli-incentivi/
- https://www.reteagevolazioni.it/bando-tipo-incentivi/
- https://getmuffin.io/ricerca-bandi/
- https://getmuffin.io/come-funziona/
- https://www.aziendabanca.it/notizie/imprese/muffin-fatturato-2025-e-obiettivi-per-il-2026
- https://www.aziendabanca.it/notizie/imprese/finanza-agevolata-creditsafe-muffin
- https://financecommunity.it/muffin-chiude-un-round-pre-seed-di-32-milioni-di-euro/
- https://financecommunity.it/round-da-2-milioni-di-euro-per-la-startup-torinese-bandosubito/
- https://www.teamsystem.com/fintech/ts-finanza-impresa/
- https://www.edotto.com/articolo/marchi-2025-istanze-al-via-dal-4-dicembre
- https://www.cn.camcom.it/sites/default/files/uploads/documents/Bandi/Bandi2025/monitoraggio%20risorse%20residue%20bandi%2013.06.pdf
- https://www.finanza.com/lavoro/click-day-inail-2025-domanda-fondi
- https://www.unioncamerelombardia.it/fileadmin/bandi/2025/Bando_export_su_misura/Determinazione_D.O._n._129-2026.pdf