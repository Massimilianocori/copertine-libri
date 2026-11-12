"""Scarica i file ufficiali delle banche dati dei quiz e le pagine con le regole d'esame; ne registra impronta e frasi controllate.

Uso (dalla radice del repository):
    python3 -I quiz/raccolta/fonti.py            # scarica solo i file che mancano in raccolta/_grezzi/
    python3 -I quiz/raccolta/fonti.py --rete     # riscarica tutto (aggiornamento: impronta cambiata = banca nuova)

Scrive quiz/dati/fonti.json: per ogni fonte indirizzo pubblico, HTTP, byte, SHA-256, pagine, data di lettura e l'esito
di ogni frase cercata nel testo (le regole d'esame scritte nel sito vengono da queste frasi).

Si scaricano solo documenti pubblici degli enti (Regioni, Camere di Commercio). Non si scaricano gli elenchi di candidati,
convocati o idonei (contengono dati personali). Un file che non risponde resta registrato con l'errore e la sua banca
non va online. Nessun tentativo di aggirare blocchi: una richiesta, una pausa, nessun cambio di identità.
"""
import hashlib
import json
import ssl
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
GREZZI = RADICE / "raccolta" / "_grezzi"
DATI = RADICE / "dati"
UA = "Mozilla/5.0 (X11; Linux x86_64) quiz-ufficiali-raccolta"
MIT = "https://www.mit.gov.it"
# Il server di mit.gov.it non invia il certificato intermedio della sua catena (Sectigo DV R36): lo aggiungiamo noi, preso dall'indirizzo
# pubblicato nel certificato stesso (Authority Information Access, http://crt.sectigo.com/SectigoPublicServerAuthenticationCADVR36.crt),
# come fanno i browser. La verifica TLS resta completa fino alla radice di fiducia del sistema.
INTERMEDIO = Path(__file__).resolve().parent / "certificati" / "sectigo-public-server-authentication-ca-dv-r36.pem"
PAEN = "https://www.paen.camcom.gov.it/sites/default/files/Allegati_Sito/Elenchi_Albi_Ruoli/Esami_NCC-TAXI/"

# Banche e documenti con le regole. "frasi": testo cercato nel file (spazi normalizzati); se manca, verifica.py si ferma.
FONTI = {
    # ---------------------------------------------------------------- patente nautica (Ministero delle infrastrutture e dei trasporti)
    "nautica_allegato_a": {
        "url": MIT + "/nfsmitgov/files/media/normativa/2022-05/ALLEGATO%20A%20QUIZ%20PATENTI%20NAUTICHE%20DD%20131%20DEL%2031%20MAGGIO%202022.pdf",
        "nome": "mit/allegato_a_dd131_2022.pdf", "chi": "Ministero delle infrastrutture e dei trasporti, Direzione generale per la vigilanza sulle autorità di sistema portuale, il trasporto marittimo e per vie d'acqua interne",
        "titolo": "Allegato A al decreto direttoriale 131 del 31/05/2022: elenco unico nazionale dei quesiti per le patenti nautiche (quiz base e quiz vela)",
        "data": "2022-05-31",
        "frasi": ["La seconda fase consiste nella risoluzione di un questionario articolato su venti domande con tre risposte ciascuna",
                  "La prova è superata se si commette un numero massimo di quattro errori",
                  "Per lo svolgimento della prova è concesso un tempo massimo di trenta minuti",
                  "Il quiz vela è costituito da cinque quesiti a risposta singola inerenti le competenze di navigazione a vela",
                  "La prova è superata se il candidato fornisce almeno quattro risposte esatte nel tempo massimo di quindici minuti",
                  "Le risposte omesse o rettificate equivalgono a una risposta errata",
                  "PRIMA FASE ENTRO 12 MIGLIA DALLA COSTA - QUIZ SU ELEMENTI DI CARTEGGIO",
                  "PRIMA FASE SENZA LIMITI DALLA COSTA – PROVA DI CARTEGGIO NAUTICO"]},
    "nautica_dd131": {
        "url": MIT + "/nfsmitgov/files/media/normativa/2022-05/M_TRA.VPTM_.REG_Decreti%28R%29.0000131.31-05-2022.pdf",
        "nome": "mit/dd131_2022.pdf", "chi": "Ministero delle infrastrutture e della mobilità sostenibili",
        "titolo": "Decreto direttoriale 131 del 31/05/2022 (sostituisce l'allegato A dei quesiti per le patenti nautiche)", "data": "2022-05-31",
        "frasi": ["L’allegato “A” al decreto direttoriale n.106 del 12 maggio 2022 è sostituito dall’Allegato “A” al presente decreto"]},
    "pag_mit_nautica": {
        "url": MIT + "/temi/patenti-mezzi-abilitazioni/patenti-nautiche/normativa", "nome": "mit/pag_mit_normativa.html",
        "chi": "Ministero delle infrastrutture e dei trasporti", "titolo": "Patenti nautiche: normativa (pagina del Ministero)", "data": None,
        "frasi": ["Decreto Dirigenziale numero 131 del 31/05/2022 Questo Decreto provvede a correggere alcuni errori materiali",
                  "Decreto Dirigenziale numero 62 del 18/04/2025 Approvazione dell'elenco unico nazionale dei quesiti per lo svolgimento delle prove teoriche scritte per il conseguimento della patente nautica di categoria D, tipo D1"]},
    "nautica_dm323": {
        "url": MIT + "/nfsmitgov/files/media/normativa/2022-05/Decreto%20Ministeriale%20numero%20323%20del%2010%20agosto%202021.pdf",
        "nome": "mit/dm323_2021.pdf", "chi": "Ministero delle infrastrutture e della mobilità sostenibili",
        "titolo": "Decreto ministeriale 323 del 10/08/2021: programmi di esame per le patenti nautiche di categoria A, B e C e modalità di svolgimento delle prove",
        "data": "2021-08-10",
        "frasi": ["Il Quiz base è costituito da venti quesiti a risposta multipla",
                  "La prova è superata se il candidato fornisce almeno sedici risposte esatte nel tempo massimo di trenta minuti",
                  "Distribuzione dei quesiti secondo i temi previsti dal programma di esame",
                  "Navigazione cartografica ed elettronica 4", "Normativa diportistica e ambientale 3", "Manovre e condotta 4",
                  "Quiz base (solo in assenza di abilitazione"]},
    # ---------------------------------------------------------------- tartufi
    "tart_lazio_2015": {
        "url": "https://www.regione.lazio.it/sites/default/files/documentazione/AGC_DD_G10268_27_08_2015_Allegato1.pdf",
        "nome": "tart_lazio_2015.pdf", "chi": "Regione Lazio, Direzione Agricoltura e Sviluppo rurale, Caccia e Pesca",
        "titolo": "Quesiti oggetto della prova d'esame per il conseguimento del tesserino di idoneità alla ricerca e raccolta dei tartufi (allegato alla determinazione G10268 del 27/08/2015)",
        "data": "2015-08-27", "frasi": ["QUESITI OGGETTO DELLA PROVA D’ESAME PER IL CONSEGUIMENTO"]},
    "tart_lazio_dd": {
        "url": "https://www.regione.lazio.it/sites/default/files/documentazione/AGC_DD_G10268_27_08_2015.pdf",
        "nome": "tart_lazio_dd.pdf", "chi": "Regione Lazio",
        "titolo": "Determinazione G10268 del 27/08/2015 (approvazione dei quesiti d'esame per il tesserino dei tartufi)",
        "data": "2015-08-27",
        "frasi": ["costituito da numero 275 quesiti a risposta multipla",
                  "di cui n. 64 riguardanti il riconoscimento delle specie dei tartufi",
                  "n. 65 riguardanti gli elementi fondamentali di biologia, n 146 riguardanti gli aspetti normativi"]},
    "tart_lazio_guida": {
        "url": "https://regione.lazio.it/sites/default/files/2021-10/AGC-Guida-Preparazione-Esame-Abilitazione-Ricerca-e-Raccolta-Tartufi.pdf",
        "nome": "tart_lazio_guida.pdf", "chi": "Regione Lazio",
        "titolo": "Guida alla preparazione dell'esame di abilitazione alla ricerca e raccolta dei tartufi (2021)", "data": "2021-10-01",
        "frasi": ["Determinazione Dirigenziale n.10268 del 27/08/2015"]},
    # File Excel protetto: il testo delle celle non si legge dai byte (qui si controlla solo il nome del foglio). Regola d'esito letta il 12/11/2026
    # aprendo il file con LibreOffice (foglio «Questionario», cella X6): 25 risposte, fino a 5 errori «IDONEO», da 6 a 8 «RIMANDATO ALL'ORALE»,
    # da 9 «NON IDONEO»; estrazione: 5 quesiti sulle specie, 5 di biologia, 15 di normativa; foglio nascosto «quiz» con la chiave dei 275 quesiti.
    "tart_lazio_autotest": {
        "url": "https://www.regione.lazio.it/sites/default/files/2022-03/Autotest-agc-18-03-22.xls", "nome": "tart_lazio_autotest.xls", "chi": "Regione Lazio",
        "titolo": "Autotest valutazione tartufi (file Excel di autovalutazione pubblicato dalla Regione, salvato il 18/03/2022)", "data": "2022-03-18",
        "frasi": ["Quesiti D.D. n. G10268-2015"]},
    "pag_lazio_tartufi": {
        "url": "https://www.regione.lazio.it/cittadini/agricoltura/tartufi", "nome": "pag_lazio_tartufi.html", "chi": "Regione Lazio",
        "titolo": "Tartufi (pagina della Regione Lazio)", "data": None,
        "frasi": ["somministrazione di un questionario di 25 domande estratte a sorte",
                  "Il candidato che commette 9 o più errori non consegue il tesserino di idoneità e deve ripetere l’esame",
                  "abbiano compiuto il quattordicesimo anno di età"]},
    "tart_er": {
        "url": "https://agricoltura.regione.emilia-romagna.it/tartufi/pubblicazioni/quiz-esercitazioni/@@download/publicationFile/Tartufi%20-%20Esempi%20di%20quiz.pdf",
        "nome": "tart_er.pdf", "chi": "Regione Emilia-Romagna", "titolo": "Tartufi – Esempi di quiz", "data": None,
        "frasi": ["ESAMI PER IL RILASCIO DEL TESSERINO PER LA RACCOLTA DEI TARTUFI"]},
    "tart_toscana_dd5332": {
        "url": "https://www.regione.toscana.it/documents/10180/13325619/Decreto_n.5332_del_27-04-2017.pdf/fce1f481-cb1c-4bbf-bb35-9667cac0ea10",
        "nome": "tart_toscana_dd5332.pdf", "chi": "Regione Toscana",
        "titolo": "Decreto 5332 del 27/04/2017: elenco domande per i questionari d'esame del tartufo (allegati A e B non più scaricabili)",
        "data": "2017-04-27", "frasi": ["di approvare l’elenco delle risposte corrette di esame Allegato B"]},
    "tart_campania": {
        "url": "https://funghietartufi.regione.campania.it/docfunghietartufi/doc/dispensa_TARTUFI_CE.pdf",
        "nome": "tart_campania.pdf", "chi": "Provincia di Caserta (pubblicata dalla Regione Campania)",
        "titolo": "Guida per l'esame di abilitazione alla raccolta dei tartufi (aprile 2008)", "data": "2008-04-01",
        "frasi": ["GUIDA PER L’ESAME DI ABILITAZIONE"]},
    # ---------------------------------------------------------------- patentino fitosanitario
    "fito_vda": {
        "url": "https://gestionewww.regione.vda.it/allegato.aspx?pk=58816", "nome": "fito_vda.pdf",
        "chi": "Regione Autonoma Valle d'Aosta, Struttura produzioni vegetali e servizi fitosanitari",
        "titolo": "Quesiti adottati dalla Regione Autonoma Valle d'Aosta per il certificato di abilitazione all'acquisto e utilizzo di prodotti fitosanitari",
        "data": None, "frasi": ["Le risposte corrette sono evidenziate in giallo", "(d.lgs. 150/2012 – DM 22 gennaio 2014 – DGR 1930/2915)"]},
    "fito_vda_dgr": {
        "url": "https://gestionewww.regione.vda.it/allegato.aspx?pk=72153", "nome": "fito_vda_dgr.pdf", "chi": "Regione Autonoma Valle d'Aosta",
        "titolo": "Deliberazione della Giunta regionale 1930 del 23/12/2015 (sistema di formazione e rilascio delle abilitazioni)", "data": "2015-12-23",
        "frasi": ["L’esame si svolge attraverso la somministrazione di un test costituito da una serie di domande a risposta multipla",
                  "la commissione potrà completare la valutazione attraverso un colloquio orale"]},
    "fito_sicilia_util": {
        "url": "https://www.regione.sicilia.it/system/files/2021-10/Utilizzatori%20-%20Elenco%20domande%20e%20risposte_2.pdf",
        "nome": "fito_sicilia_util.pdf", "chi": "Regione Siciliana, Servizio fitosanitario regionale",
        "titolo": "Elenco domande di esame per il certificato di abilitazione all'acquisto e all'utilizzo dei prodotti fitosanitari",
        "data": None,
        "frasi": ["la Commissione d’esame ne individuerà n. 25 quale oggetto della prova di valutazione",
                  "hanno a disposizione 60 minuti per rispondere",
                  "Il test verrà superato qualora non si effettui un numero di errori superiore a 5",
                  "Le domande senza risposta vengono considerate errori"]},
    "fito_sicilia_cons": {
        "url": "https://regione.sicilia.it/system/files/2021-10/Consulenti-Elenco%20domande%20e%20risposte_0.pdf",
        "nome": "fito_sicilia_cons.pdf", "chi": "Regione Siciliana, Servizio fitosanitario regionale",
        "titolo": "Elenco domande di esame per il certificato di abilitazione per l'attività di consulente", "data": None,
        "frasi": ["la Commissione d’esame ne individuerà n. 30 quale oggetto della prova di valutazione",
                  "hanno a disposizione 90 minuti per rispondere",
                  "Il test verrà superato qualora non si effettui un numero di errori superiore a 5",
                  "Le risposte esatte sono contrassegnate da un asterisco"]},
    "pag_sicilia_fito": {
        "url": "https://www.regione.sicilia.it/istituzioni/regione/strutture-regionali/assessorato-agricoltura-sviluppo-rurale-pesca-mediterranea/dipartimento-agricoltura/servizi/servizio-fitosanitario-regionale/misura-formazione",
        "nome": "pag_sicilia_fito.html", "chi": "Regione Siciliana, Servizio fitosanitario regionale",
        "titolo": "Misura formazione (pagina del Servizio fitosanitario regionale che pubblica gli elenchi delle domande d'esame)", "data": None,
        "frasi": ["Utilizzatori - Elenco domande e risposte", "Consulenti-Elenco domande e risposte", "Ultimo aggiornamento 22/10/2021"]},
    "fito_oristano": {
        "url": "https://asl5oristano.it/wp-content/uploads/2024/09/All.-1-Elenco-domande-e-soluzioni.pdf",
        "nome": "fito_oristano.pdf", "chi": "Regione Autonoma della Sardegna (pubblicato da ASL 5 Oristano)",
        "titolo": "Elenco delle domande d'esame per il certificato di abilitazione alla vendita di prodotti fitosanitari (allegato 1 alla determinazione 582 del 15/06/2017)",
        "data": "2017-06-15", "frasi": ["Allegato 1 alla Determinazione n. 582 del 15 giugno 2017"]},
    # ---------------------------------------------------------------- ruolo conducenti taxi e NCC
    "taxi_sassari": {
        "url": "https://www.ss.camcom.it/sites/default/files/wp2/wpdm/Domande_Ruolo_Conducenti_SS%20-%2004_04_2022-1.pdf",
        "nome": "taxi_sassari.pdf", "chi": "Camera di Commercio di Sassari",
        "titolo": "Banca dati quiz d'esame del Ruolo dei conducenti (aggiornata al 04/04/2022)", "data": "2022-04-04",
        "frasi": ["Aggiornati al 04/04/2022"]},
    "pag_sassari": {
        "url": "https://www.ss.camcom.it/print/pdf/node/2774", "nome": "pag_sassari.pdf", "chi": "Camera di Commercio di Sassari",
        "titolo": "Ruolo conducenti: esame e iscrizione (pagina della Camera di Commercio di Sassari)", "data": None,
        "frasi": ["Verranno estratte, per ciascun candidato, n. 40 domande riguardanti le materie d’esame",
                  "L’esame si intenderà superato se il candidato risponderà correttamente al 70% delle domande proposte nel tempo massimo di un’ora e venti minuti"]},
    "taxi_caor": {
        "url": "https://www.caor.camcom.it/sites/default/files/contenuto_redazione/bando/allegati/2025-01-29/banca%20dati%20quiz%20aggiornata%20al%2029%20gennaio%202025.pdf",
        "nome": "taxi_caor.pdf", "chi": "Camera di Commercio di Cagliari-Oristano",
        "titolo": "Banca dati quiz del Ruolo dei conducenti (aggiornata al 29 gennaio 2025)", "data": "2025-01-29",
        "frasi": ["CODICE DELLA STRADA", "TOPONOMASTICA ORISTANO"]},
    "pag_caor": {
        "url": "https://www.caor.camcom.it/print/pdf/node/3463", "nome": "pag_caor.pdf", "chi": "Camera di Commercio di Cagliari-Oristano",
        "titolo": "Ruolo conducenti (pagina della Camera di Commercio di Cagliari-Oristano)", "data": None,
        "frasi": ["La prova d’esame consiste in un test a risposta multipla; l’esame si intende superato se il candidato risponde correttamente al 70% delle domande proposte",
                  "Banca dati quiz (aggiornata a gennaio 2025)"]},
    "dgr_sardegna": {
        "url": "http://www.regione.sardegna.it/documenti/1_274_20120503105707.pdf", "nome": "dgr_sardegna.pdf", "chi": "Regione Autonoma della Sardegna",
        "titolo": "Allegato alla deliberazione della Giunta regionale 12/30 del 20/03/2012 (ruolo dei conducenti, esame di idoneità)", "data": "2012-03-20",
        "frasi": ["L'esame di idoneità consiste in una prova scritta, effettuata su quesiti a risposta multipla",
                  "conoscenza di base di una lingua straniera a scelta del candidato tra inglese, francese, spagnolo e tedesco",
                  "La prova d'esame si intende positivamente superata se il candidato ha risposto positivamente ad almeno il 70% dei quesiti formulati"]},
    "paen_regolamento": {
        "url": "https://www.paen.camcom.gov.it/sites/default/files/NUOVO%20REGOLAMENTO%20ESAMI%20CONDUCENTI%20AGGIORNATO.pdf",
        "nome": "paen_regolamento.pdf", "chi": "Camera di Commercio di Palermo ed Enna",
        "titolo": "Regolamento sulle modalità di svolgimento dell'esame di idoneità per il Ruolo dei conducenti (in vigore dal 25/03/2026)",
        "data": "2026-03-25",
        "frasi": ["copia della scheda contente i 20 quiz", "La prova ha durata pari a venti minuti",
                  "almeno 18/20 (margine massimo di due errori)", "In vigore dal 25/03/2026"]},
}

# Schede d'esame corrette della Camera di Commercio di Palermo ed Enna (una per seduta; pagina «Ruolo dei conducenti»)
PAEN_FILE = [
    "2021_01/2021_01-31-03-2021%20ore%2011.00-QUIZ%20CORRETTO.pdf", "2021_01/2021_01-31-03-2021%20ore%2016.00-QUIZ%20CORRETTO.pdf",
    "2021_02/2021_02-15-11-2021%20ore%2011.00-QUIZ%20CORRETTO.pdf", "2022_01/2022_01-11-04-2022%20ore%2010.30-QUIZ%20CORRETTO.pdf",
    "2022_02/2022_02-04-07-2022%20ore%2011.00-QUIZ%20CORRETTO.pdf", "2022_03/2022_03-19-09-2022%20ore%2010%2C30-QUIZ%20CORRETTO.pdf",
    "2022_04/2022_04-28-11-2022%20ore%2010%2C30-QUIZ%20CORRETTO.pdf", "2023_01/23-01-2023-QUIZ%20CORRETTO.pdf",
    "2023_02/15-03-2023-QUIZ%20CORRETTO.pdf", "2023_03/12-04-2023-QUIZ%20CORRETTO.pdf", "2023_04/24-05-2023-QUIZ%20CORRETTO.pdf",
    "2023_05/19-07-2023-QUIZ%20CORRETTO.pdf", "2023_06/11-10-2023-QUIZ%20CORRETTO.pdf", "2023_07/22-11-2023-QUIZ%20CORRETTO.pdf",
    "2023_08/20-12-2023-QUIZ%20CORRETTO.pdf", "2024_01/21-02-2024-QUIZ%20CORRETTO.pdf", "2024_01/28-02-2024-QUIZ%20CORRETTO.pdf",
    "2024_02/03-04-2024-QUIZ%20CORRETTO.pdf", "2024_03/08-05-2024-QUIZ%20CORRETTO.pdf", "2024_04/19-06-2024-QUIZ%20CORRETTO.pdf",
    "2024_05/10-07-2024-QUIZ%20CORRETTO.pdf", "2024_06/11-09-2024-QUIZ%20CORRETTO.pdf", "2024_07/23-10-2024-QUIZ%20CORRETTO.pdf",
    "2025_01/09-01-2025-QUIZ%20CORRETTO.pdf", "2025_02/19-02-2025-QUIZ%20CORRETTO.pdf", "2025_03/19-02-2025-QUIZ%20CORRETTO.pdf",
    "2025_04/07-04-2025-QUIZ%20CORRETTO.pdf", "2025_05/06-05-2025-QUIZ%20CORRETTO.pdf", "2025_06/19-05-2025-QUIZ%20CORRETTO.pdf",
    "2025_07/25-06-2025-QUIZ%20CORRETTO.pdf", "2025_08/22-07-2025-QUIZ%20CORRETTO.pdf", "2025_09/02-09-2025-QUIZ%20CORRETTO.pdf",
    "2025_10/14-10-2025-QUIZ%20CORRETTO.pdf", "2025_11/02-12-2025-QUIZ%20CORRETTO.pdf",
]
for _i, _p in enumerate(PAEN_FILE, 1):
    FONTI[f"paen_{_i:02d}"] = {"url": PAEN + _p, "nome": f"paen/q{_i:02d}.pdf", "chi": "Camera di Commercio di Palermo ed Enna",
                               "titolo": "Questionario corretto della seduta d'esame del Ruolo dei conducenti", "data": None,
                               "frasi": ["Questionario CORRETTO"]}
FONTI["paen_35"] = {"url": "https://www.paen.camcom.gov.it/sites/default/files/QUIZ%20CORRETTI.pdf", "nome": "paen/q35.pdf",
                    "chi": "Camera di Commercio di Palermo ed Enna", "titolo": "Questionario corretto della seduta d'esame del Ruolo dei conducenti",
                    "data": None, "frasi": ["Questionario CORRETTO"]}
FONTI["pag_paen"] = {"url": "https://www.paen.camcom.gov.it/it/elenchi-albi-e-ruoli/ruoli/ruolo-dei-conducenti-di-veicoli-adibiti-ad-autoservizi-pubblici-non-di-linea",
                     "nome": "pag_paen.html", "chi": "Camera di Commercio di Palermo ed Enna",
                     "titolo": "Ruolo dei conducenti di veicoli adibiti ad autoservizi pubblici non di linea (pagina della Camera di Commercio)",
                     "data": None, "frasi": ["Regolamento Esami in vigore dal 25/03/2026"]}

# Fonti cercate ma non raggiungibili il 12/11/2026 (restano nell'elenco «non online» del sito, senza file)
NON_RAGGIUNTE = {
    "taxi_roma": {"url": "https://static.cittametropolitanaroma.it/uploads/Elenco-quiz-aggiornato-con-relativo-correttore-26.6.2024.pdf",
                  "chi": "Città metropolitana di Roma Capitale", "titolo": "Elenco quiz aggiornato con relativo correttore (26/06/2024)"},
    "fito_umbria": {"url": "https://www.regione.umbria.it/documents/18/26424422/DOMANDE+2026-combined.pdf/a969a1b1-c5c4-41e9-89ee-0ffc189b8281",
                    "chi": "Regione Umbria", "titolo": "Domande d'esame per il patentino fitosanitario (2026)"},
}


def testo_di(percorso):
    """Testo del file (PDF con pdftotext, HTML senza tag), con gli spazi normalizzati."""
    if percorso.suffix == ".pdf":
        t = subprocess.run(["pdftotext", "-layout", str(percorso), "-"], capture_output=True, text=True).stdout
    else:
        import html as H
        t = percorso.read_text(encoding="utf-8", errors="replace")
        t = re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S | re.I)
        t = H.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t)


def pagine_pdf(percorso):
    out = subprocess.run(["pdfinfo", str(percorso)], capture_output=True, text=True).stdout
    m = re.search(r"Pages:\s+(\d+)", out)
    return int(m.group(1)) if m else None


def scarica(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    ctx = ssl.create_default_context()
    if INTERMEDIO.exists():
        ctx.load_verify_locations(cafile=str(INTERMEDIO))
    try:
        with urllib.request.urlopen(req, timeout=180, context=ctx) as r:
            dati = r.read()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(dati)
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:  # rete: si registra l'errore, la banca non va online
        return f"errore: {e.__class__.__name__}"


def main(argv):
    rete = "--rete" in argv
    vecchio = json.loads((DATI / "fonti.json").read_text(encoding="utf-8")) if (DATI / "fonti.json").exists() else {"file": {}}
    out = {"_nota": "Scritto da raccolta/fonti.py. File grezzi in raccolta/_grezzi/ (fuori da git): l'impronta SHA-256 dice quale versione è stata letta.",
           "file": {}, "non_raggiunte": NON_RAGGIUNTE}
    for fid, f in FONTI.items():
        dest = GREZZI / f["nome"]
        prima = vecchio["file"].get(fid, {})
        http = prima.get("http", 200)
        letto = prima.get("letto_il")
        if rete or not dest.exists():
            http = scarica(f["url"], dest)
            letto = date.today().isoformat()
            time.sleep(1)
        voce = {k: f[k] for k in ("url", "chi", "titolo", "data")}
        voce.update({"file": f["nome"], "http": http, "letto_il": letto or date.today().isoformat()})
        if dest.exists() and http == 200:
            b = dest.read_bytes()
            voce["byte"] = len(b)
            voce["sha256"] = hashlib.sha256(b).hexdigest()
            if dest.suffix == ".pdf":
                voce["pagine"] = pagine_pdf(dest)
            t = testo_di(dest)
            voce["frasi"] = {fr: (re.sub(r"\s+", " ", fr) in t) for fr in f["frasi"]}
        out["file"][fid] = voce
        mancano = [k for k, ok in voce.get("frasi", {}).items() if not ok]
        print(f"{fid:22} {http} {voce.get('byte', '-')} {'frasi OK' if not mancano else 'FRASI MANCANTI: ' + str(mancano)}")
    (DATI / "fonti.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])
