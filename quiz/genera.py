"""Genera il sito statico "Quiz Ufficiali" (italiano) in quiz/sito/: le banche ufficiali dei quiz per tesserino dei tartufi,
patentino fitosanitario e ruolo dei conducenti taxi/NCC, con simulatore nel browser e la risposta dell'ente accanto a ogni domanda.

Uso (dalla radice del repository):
    python3 -I quiz/raccolta/fonti.py      # scarica i PDF ufficiali -> raccolta/_grezzi/, dati/fonti.json (impronte SHA-256)
    python3 -I quiz/raccolta/estrai.py     # legge i PDF -> dati/banche/*.json
    python3 quiz/genera.py                 # pagine in quiz/sito/
    python3 quiz/verifica.py --browser     # controlli (rilegge i PDF con un lettore separato)

Regole: solo banche con la chiave ufficiale delle risposte; testo delle domande e delle risposte uguale al PDF; nessuna spiegazione
inventata (i documenti di oggi non ne hanno: il sito mostra solo la risposta ufficiale e la pagina del PDF); le regole d'esame vengono
da frasi controllate nei documenti degli enti (dati/fonti.json). Una pagina per banca, con tutte le sue domande.
"""
import hashlib
import json
import re
import shutil
import sys
from collections import Counter
from datetime import date
from html import escape, unescape
from pathlib import Path
from urllib.parse import quote_plus

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
sys.path.insert(0, str(RADICE))
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402
import stile  # noqa: E402

URL_SITO = "https://quiz-ufficiali.netlify.app"  # unico punto da cambiare se il nome del sito su Netlify è diverso (anche in verifica.py)
NOME = "Quiz Ufficiali"
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti): non rimuoverlo
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"  # contatore condiviso della rete, senza cookie
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
CHIAVE_INDEXNOW = "b5a26a844a465f58552debee2c8a0114"  # = CHIAVE in studio-business/strumenti/indexnow.py
SITO_ID = "quiz"  # nome del sito in monetizzazione.json
MIN_PAROLE_ADSENSE = 400  # niente pubblicità nelle pagine noindex o con poco testo (lezione AdSense «scarso valore»)
OGGI = date(2026, 11, 12)  # data dei controlli scritta nelle pagine (aggiornarla quando si rilanciano fonti ed estrazione)

MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]


def carica(nome):
    return json.loads((DATI / nome).read_text(encoding="utf-8"))


FJ = carica("fonti.json")
AFF = carica("affiliati.json")


def h(x):
    return escape(str(x), quote=True)


def data_lunga(d):
    if not d:
        return ""
    if isinstance(d, str):
        d = date.fromisoformat(d)
    return f"{d.day} {MESI[d.month - 1]} {d.year}"


def num(n):
    return f"{n:,}".replace(",", ".")


# ---------------------------------------------------------------- moduli e banche (testi: solo fatti scritti nelle fonti citate)
MODULI = {
    "patente-nautica": {
        "nome": "Patente nautica", "breve": "Patente nautica", "icona": "anchor",
        "titolo": "Quiz patente nautica: l'elenco ufficiale del Ministero",
        "descr": "Quiz della patente nautica dall'elenco unico nazionale del Ministero: quiz base e quiz vela con la risposta esatta e un simulatore gratuito.",
        "h1": "Quiz patente nautica: le domande ufficiali del Ministero",
        "sub": "L'elenco unico nazionale dei quesiti del Ministero delle infrastrutture e dei trasporti, con la risposta esatta indicata nel documento e un simulatore con le regole dell'esame.",
    },
    "tartufi": {
        "nome": "Tesserino per la raccolta dei tartufi", "breve": "Tartufi", "icona": "truffle",
        "titolo": "Quiz per il tesserino dei tartufi: banche ufficiali per Regione",
        "descr": "Esame per il tesserino di raccolta dei tartufi: le domande ufficiali delle Regioni con la risposta esatta e un simulatore gratuito.",
        "h1": "Quiz per il tesserino dei tartufi, Regione per Regione",
        "sub": "Le domande d'esame pubblicate dalle Regioni, con la risposta esatta indicata dall'ente e un simulatore che estrae le domande come all'esame.",
    },
    "patentino-fitosanitario": {
        "nome": "Patentino fitosanitario", "breve": "Patentino fitosanitario", "icona": "leaf",
        "titolo": "Quiz patentino fitosanitario: banche ufficiali per Regione",
        "descr": "Patentino fitosanitario (acquisto e utilizzo, consulente): le domande d'esame pubblicate dalle Regioni con la risposta ufficiale e il simulatore.",
        "h1": "Quiz del patentino fitosanitario, Regione per Regione",
        "sub": "Certificato di abilitazione all'acquisto e all'utilizzo dei prodotti fitosanitari e certificato per i consulenti: le domande pubblicate dalle Regioni, con la risposta ufficiale.",
    },
    "ruolo-conducenti": {
        "nome": "Ruolo dei conducenti taxi e NCC", "breve": "Taxi e NCC", "icona": "car",
        "titolo": "Quiz ruolo conducenti taxi e NCC: domande ufficiali",
        "descr": "Esame per il ruolo dei conducenti di taxi e NCC: le banche quiz e le schede corrette pubblicate dalle Camere di Commercio, con simulatore.",
        "h1": "Quiz per il ruolo dei conducenti di taxi e NCC",
        "sub": "Le banche quiz e le schede d'esame corrette pubblicate dalle Camere di Commercio, con la risposta esatta e la pagina del PDF.",
    },
}

# regole: n = domande estratte all'esame; max_errori o soglia (percentuale); minuti. None = non scritto nei documenti letti.
BANCHE = [
    {"id": "nautica-base", "modulo": "patente-nautica", "slug": "quiz-base", "luogo": "Quiz base", "fonte": "nautica_allegato_a",
     "ente": "Ministero delle infrastrutture e dei trasporti", "ente_di": "del Ministero delle infrastrutture e dei trasporti",
     "esame": "esame per la patente nautica (quiz base, entro 12 miglia e senza limiti dalla costa)",
     "titolo": "Quiz patente nautica: le {n} domande ufficiali del quiz base",
     "descr": "Le {n} domande del quiz base della patente nautica dall'elenco unico del Ministero, con la risposta esatta: simulazione da 20 domande in 30 minuti.",
     "n": 20, "max_errori": 4, "soglia": None, "minuti": 30, "fonti_regole": ["nautica_allegato_a"],
     "regole": [
         ("La prova di teoria comincia con il carteggio: entro 12 miglia un quiz su elementi di carteggio (5 quesiti, almeno 4 esatti, 20 minuti); senza limiti una prova di carteggio nautico (4 quesiti, almeno 3 esatti, 60 minuti). Chi non la supera non passa al quiz base.", "nautica_allegato_a"),
         ("Il quiz base ha 20 domande con tre risposte ciascuna, in 30 minuti.", "nautica_allegato_a"),
         ("È superato con 4 errori al massimo: con il quinto errore il candidato non è idoneo. Le risposte omesse o corrette a mano contano come errori.", "nautica_allegato_a"),
         ("Le 20 domande sono distribuite per tema: 1 di teoria dello scafo, 1 di motori, 3 di sicurezza, 4 di manovre e condotta, 2 di COLREG e segnalamento marittimo, "
          "2 di meteorologia, 4 di navigazione cartografica ed elettronica, 3 di normativa diportistica e ambientale. Il simulatore estrae le domande con la stessa distribuzione.", "nautica_dm323"),
         ("Chi chiede la patente senza limiti dalla costa e ha già l'abilitazione entro le 12 miglia non rifà il quiz base.", "nautica_dm323"),
         (f"L'elenco è ancora quello del 2022: nella pagina «Patenti nautiche: normativa» del Ministero, letta il {data_lunga(FJ['file']['pag_mit_nautica']['letto_il'])}, dopo il decreto 131 del "
          "31 maggio 2022 nessun decreto sostituisce l'elenco dei quesiti per le patenti di categoria A, B e C. Il decreto 62 del 18 aprile 2025 approva un elenco "
          "separato per la patente D1, che in questo sito non c'è.", "pag_mit_nautica"),
     ],
     "quote": {"Teoria dello scafo": 1, "Motori": 1, "Sicurezza della navigazione": 3, "Manovra e condotta": 4, "Colreg e segnalamento marittimo": 2,
               "Meteorologia": 2, "Navigazione cartografica ed elettronica": 4, "Normativa diportistica e ambientale": 3},
     "regola_sim": "20 domande estratte per tema come all'esame (1 scafo, 1 motori, 3 sicurezza, 4 manovre, 2 COLREG, 2 meteorologia, 4 navigazione, 3 normativa), superato con 4 errori al massimo, 30 minuti",
     "origine": ("Allegato A al decreto direttoriale 131 del 31 maggio 2022, l'elenco unico nazionale dei quesiti per le patenti nautiche pubblicato dal "
                 "Ministero (sostituisce l'allegato del decreto 106/2022). Ogni risposta ha accanto la colonna V/F: la risposta esatta è quella segnata V. "
                 "Il quiz base del PDF ha 1.472 domande."),
     "nota": ("All'esame ci sono anche domande con una figura, che in questo sito non ci sono: nell'elenco ufficiale del quiz base sono {figure} su {totale_pdf}. "
              "Non riproduciamo le figure del Ministero né le carte nautiche dell'Istituto Idrografico della Marina (servono per le prove di carteggio), "
              "quindi qui trovi solo le domande di testo: le domande con figura studiale nel PDF del Ministero, alla fonte 1."),
     "altre_fonti": ["nautica_dd131", "pag_mit_nautica"]},
    {"id": "nautica-vela", "modulo": "patente-nautica", "slug": "quiz-vela", "luogo": "Quiz vela", "fonte": "nautica_allegato_a",
     "ente": "Ministero delle infrastrutture e dei trasporti", "ente_di": "del Ministero delle infrastrutture e dei trasporti",
     "esame": "esame per la patente nautica con abilitazione alla vela (quiz vela)",
     "titolo": "Quiz vela patente nautica: le {n} domande ufficiali",
     "descr": "Le {n} domande vero o falso del quiz vela della patente nautica, dall'elenco del Ministero con la risposta esatta: simulazione da 5 in 15 minuti.",
     "n": 5, "max_errori": 1, "soglia": None, "minuti": 15, "fonti_regole": ["nautica_allegato_a"],
     "regole": [
         ("Il quiz vela è solo per chi chiede l'abilitazione alla vela: 5 quesiti a risposta singola.", "nautica_allegato_a"),
         ("È superato con almeno 4 risposte esatte in 15 minuti; le risposte omesse o corrette a mano contano come errori.", "nautica_allegato_a"),
         ("Chi non lo supera può chiedere di continuare l'esame per la patente limitata alle unità a motore.", "nautica_allegato_a"),
     ],
     "origine": ("Allegato A al decreto direttoriale 131 del 31 maggio 2022, sezione «Quiz vela»: 250 affermazioni con le risposte VERO e FALSO e la "
                 "colonna V/F che indica quella esatta."),
     "nota": ("All'esame possono uscire anche le domande con una figura, che in questo sito non ci sono: nell'elenco ufficiale del quiz vela sono {figure} su {totale_pdf}. "
              "Guardale nel PDF del Ministero, alla fonte 1."),
     "altre_fonti": ["nautica_dd131"]},
    {"id": "tartufi-lazio", "modulo": "tartufi", "slug": "lazio", "luogo": "Lazio", "fonte": "tart_lazio_2015",
     "ente": "Regione Lazio", "ente_di": "della Regione Lazio", "esame": "esame per il tesserino di idoneità alla ricerca e raccolta dei tartufi",
     "titolo": "Quiz tesserino tartufi Lazio: le {n} domande ufficiali",
     "descr": "Le {n} domande ufficiali della Regione Lazio per il tesserino dei tartufi, con la risposta esatta e un simulatore da 25 domande come all'esame.",
     "n": 25, "max_errori": 8, "orale_da": 6, "soglia": None, "minuti": None, "fonti_regole": ["pag_lazio_tartufi", "tart_lazio_dd"],
     "quote": {"Conoscenza delle specie": 5, "Biologia del tartufo": 5, "Normativa su ricerca, raccolta e commercio": 15},
     "regola_sim": "25 domande estratte come nell'autotest della Regione (5 sulle specie, 5 di biologia, 15 di normativa): idoneo fino a 5 errori, orale da 6 a 8 errori, non idoneo da 9 errori",
     "regola_breve": "8 errori al massimo (da 6 a 8: orale)",
     "regole": [
         ("Per il tesserino servono 14 anni compiuti e il superamento di un esame scritto.", "pag_lazio_tartufi"),
         ("La prova è un questionario di 25 domande estratte a sorte.", "pag_lazio_tartufi"),
         ("Con 9 errori o più il candidato non ottiene il tesserino e deve ripetere l'esame.", "pag_lazio_tartufi"),
         ("Nell'autotest pubblicato dalla Regione (file Excel salvato il 18 marzo 2022) le 25 domande sono 5 sul riconoscimento delle specie, 5 di biologia e 15 di normativa, "
          "e l'esito è «idoneo» fino a 5 errori, «rimandato all'orale» da 6 a 8 errori, «non idoneo» da 9 errori. Il simulatore usa la stessa distribuzione e gli stessi tre esiti.", "tart_lazio_autotest"),
         ("L'elenco ufficiale ha 275 quesiti: 64 sul riconoscimento delle specie, 65 sulla biologia, 146 sulla normativa di ricerca, raccolta e commercio.", "tart_lazio_dd"),
     ],
     "origine": ("Elenco «Quesiti oggetto della prova d'esame» approvato con la determinazione G10268 del 27 agosto 2015. La risposta esatta è "
                 "evidenziata in giallo nel PDF. Lo stesso elenco, con le stesse risposte evidenziate, è nella guida all'esame pubblicata dalla "
                 "Regione nel 2021: lo abbiamo confrontato domanda per domanda e coincide. Anche l'autotest Excel della Regione contiene i 275 quesiti con "
                 "la risposta esatta: l'abbiamo confrontato con la nostra chiave e le 275 risposte coincidono."),
     "nota": ("La determinazione del 2015 parlava di una scheda da 20 quesiti; la pagina attuale della Regione e il suo autotest parlano di 25 domande: "
              "il simulatore segue la pagina attuale. Per l'orale e per la data della tua sessione fa fede la convocazione dell'Area decentrata agricoltura."),
     "altre_fonti": ["tart_lazio_guida", "tart_lazio_autotest"]},
    {"id": "fitosanitario-valle-d-aosta", "modulo": "patentino-fitosanitario", "slug": "valle-d-aosta", "luogo": "Valle d'Aosta", "fonte": "fito_vda",
     "ente": "Regione Autonoma Valle d'Aosta", "ente_di": "della Regione Valle d'Aosta", "esame": "esame per il certificato di abilitazione all'acquisto e all'utilizzo dei prodotti fitosanitari",
     "titolo": "Quiz patentino fitosanitario Valle d'Aosta: {n} domande",
     "descr": "Le {n} domande adottate dalla Regione Valle d'Aosta per il patentino fitosanitario, con la risposta ufficiale e un'esercitazione da 20 domande.",
     "n": 20, "max_errori": None, "soglia": None, "minuti": None, "fonti_regole": ["fito_vda_dgr"],
     "regole": [
         ("L'esame si svolge con un test di domande a risposta multipla.", "fito_vda_dgr"),
         ("Se il test non raggiunge la soglia minima, la commissione può completare la valutazione con un colloquio orale.", "fito_vda_dgr"),
         ("Il numero di domande e la soglia non sono scritti nella delibera: il simulatore propone un'esercitazione da 20 domande e mostra solo il punteggio.", "fito_vda_dgr"),
     ],
     "origine": ("Elenco «Quesiti adottati dalla Regione Autonoma Valle d'Aosta per il conseguimento del certificato di abilitazione all'acquisto e "
                 "utilizzo di prodotti fitosanitari» (d.lgs. 150/2012, DM 22 gennaio 2014, DGR 1930/2015). Il documento dice: «Le risposte corrette "
                 "sono evidenziate in giallo»."),
     "nota": "Il documento non porta una data; il file pubblicato dalla Regione è del febbraio 2022 (data interna del PDF)."},
    {"id": "fitosanitario-sicilia-utilizzatori", "modulo": "patentino-fitosanitario", "slug": "sicilia-utilizzatori", "luogo": "Sicilia",
     "fonte": "fito_sicilia_util", "ente": "Regione Siciliana, Servizio fitosanitario regionale", "ente_di": "della Regione Siciliana",
     "esame": "esame per il certificato di abilitazione all'acquisto e all'utilizzo dei prodotti fitosanitari",
     "titolo": "Quiz patentino fitosanitario Sicilia: {n} domande ufficiali",
     "descr": "Le {n} domande della Regione Siciliana per il patentino fitosanitario (acquisto e utilizzo) con la risposta ufficiale: simulazione da 25 domande.",
     "n": 25, "max_errori": 5, "soglia": None, "minuti": 60, "fonti_regole": ["fito_sicilia_util"],
     "regole": [
         ("La commissione sceglie 25 domande dall'elenco.", "fito_sicilia_util"),
         ("Si hanno 60 minuti per rispondere.", "fito_sicilia_util"),
         ("Il test è superato con 5 errori al massimo; le domande senza risposta contano come errori.", "fito_sicilia_util"),
         (f"L'elenco è quello che il Servizio fitosanitario regionale pubblica oggi nella pagina «Misura formazione» (ultimo aggiornamento della pagina: 22 ottobre 2021; "
          f"letta il {data_lunga(FJ['file']['pag_sicilia_fito']['letto_il'])}).", "pag_sicilia_fito"),
     ],
     "data_doc": "file del 2016",
     "origine": ("«Elenco domande di esame per il rilascio del certificato di abilitazione all'acquisto e all'utilizzo dei prodotti fitosanitari» "
                 "del Servizio fitosanitario regionale. La risposta esatta è segnata con ✓ accanto alla lettera; in fondo al PDF c'è anche una tabella "
                 "delle risposte esatte, che abbiamo confrontato con i segni."),
     "nota": ("Il documento non porta una data: il file è dell'agosto 2016 (data interna del PDF) e alcune domande usano parole di allora, come «patentino» e "
              "«molto tossico, tossico o nocivo». Le risposte sono quelle dell'elenco ufficiale; prima dell'esame chiedi al Servizio fitosanitario "
              "regionale se la tua commissione usa ancora questo elenco.")},
    {"id": "fitosanitario-sicilia-consulenti", "modulo": "patentino-fitosanitario", "slug": "sicilia-consulenti", "luogo": "Sicilia (consulenti)",
     "fonte": "fito_sicilia_cons", "ente": "Regione Siciliana, Servizio fitosanitario regionale", "ente_di": "della Regione Siciliana",
     "esame": "esame per il certificato di abilitazione all'attività di consulente sui prodotti fitosanitari",
     "titolo": "Quiz consulente fitosanitario Sicilia: {n} domande ufficiali",
     "descr": "Le {n} domande della Regione Siciliana per il certificato di consulente fitosanitario, con la risposta ufficiale: simulazione da 30 domande.",
     "n": 30, "max_errori": 5, "soglia": None, "minuti": 90, "fonti_regole": ["fito_sicilia_cons"],
     "regole": [
         ("La commissione sceglie 30 domande dall'elenco.", "fito_sicilia_cons"),
         ("Si hanno 90 minuti per rispondere.", "fito_sicilia_cons"),
         ("Il test è superato con 5 errori al massimo; le domande senza risposta contano come errori.", "fito_sicilia_cons"),
         (f"L'elenco è quello che il Servizio fitosanitario regionale pubblica oggi nella pagina «Misura formazione» (ultimo aggiornamento della pagina: 22 ottobre 2021; "
          f"letta il {data_lunga(FJ['file']['pag_sicilia_fito']['letto_il'])}).", "pag_sicilia_fito"),
     ],
     "data_doc": "file del 2021",
     "origine": ("«Elenco domande di esame per il rilascio del certificato di abilitazione per l'attività di consulente» del Servizio fitosanitario "
                 "regionale. Il documento dice: «Le risposte esatte sono contrassegnate da un asterisco»; in fondo c'è anche una tabella delle risposte "
                 "esatte, che abbiamo confrontato con gli asterischi."),
     "nota": "Il documento non porta una data: il file pubblicato dalla Regione è del maggio 2021 (data interna del PDF)."},
    {"id": "taxi-ncc-palermo-enna", "modulo": "ruolo-conducenti", "slug": "palermo-enna", "luogo": "Palermo ed Enna", "fonte": "paen_35",
     "ente": "Camera di Commercio di Palermo ed Enna", "ente_di": "della Camera di Commercio di Palermo ed Enna", "esame": "esame di idoneità per il ruolo dei conducenti di taxi e NCC",
     "titolo": "Quiz ruolo conducenti Palermo-Enna: {n} domande uscite agli esami",
     "descr": "Le {n} domande uscite agli esami 2021-2026 per il ruolo conducenti taxi e NCC di Palermo ed Enna, dalle schede corrette della Camera di Commercio.",
     "sub": "Le domande uscite alle sedute d'esame dal 2021 al 2026, dalle schede corrette pubblicate dalla Camera di Commercio di Palermo ed Enna, con la risposta "
            "esatta segnata dalla commissione. Non è la banca dati completa della Camera, che non è pubblicata.",
     "unita": "domande uscite agli esami 2021-2026", "data_doc": "sedute dal 31/03/2021 al 22/05/2026",
     "cifra_n": "domande uscite agli esami 2021-2026, con la risposta segnata dalla commissione",
     "n": 20, "max_errori": 2, "soglia": None, "minuti": 20, "fonti_regole": ["paen_regolamento"],
     "regole": [
         ("La commissione estrae 20 domande a risposta multipla dalla banca dati dei quesiti (programma ARCA di InfoCamere).", "paen_regolamento"),
         ("La prova dura 20 minuti.", "paen_regolamento"),
         ("All'orale passa chi risponde esattamente ad almeno 18 domande su 20 (2 errori al massimo); doppia segnatura, cancellatura o risposta mancante contano come errore.", "paen_regolamento"),
     ],
     "origine": ("Dopo ogni seduta la Camera pubblica il «Questionario corretto», con [*] accanto alla risposta esatta. Abbiamo letto le {sedute} schede "
                 "pubblicate dal marzo 2021 al maggio 2026: {lette} domande, di cui {doppie} ripetute in più sedute (contate una volta sola, con la stessa "
                 "risposta in ogni scheda) e {nulle} segnata «Domanda nulla» dalla commissione (tolta). Non è l'intera banca dati della Camera, che non è pubblicata: "
                 "sono le domande uscite davvero agli esami."),
     "nota": ("Non è la banca dati completa: sono le domande uscite alle sedute d'esame dal 31 marzo 2021 al 22 maggio 2026. All'esame la commissione estrae le 20 "
              "domande dall'intera banca dati, quindi possono uscire domande che qui non ci sono. Il simulatore estrae 20 domande fra quelle già uscite.")},
    {"id": "taxi-ncc-sassari", "modulo": "ruolo-conducenti", "slug": "sassari", "luogo": "Sassari", "fonte": "taxi_sassari",
     "ente": "Camera di Commercio di Sassari", "ente_di": "della Camera di Commercio di Sassari", "esame": "esame di idoneità per il ruolo dei conducenti di taxi e NCC",
     "titolo": "Quiz ruolo conducenti taxi NCC Sassari: {n} domande ufficiali",
     "descr": "La banca dati quiz della Camera di Commercio di Sassari per il ruolo conducenti taxi e NCC: {n} domande con la risposta esatta e simulazione da 40.",
     "n": 40, "max_errori": None, "soglia": 70, "minuti": 80, "fonti_regole": ["pag_sassari", "dgr_sardegna"],
     "regole": [
         ("A ogni candidato vengono estratte 40 domande sulle materie d'esame.", "pag_sassari"),
         ("L'esame è superato con almeno il 70% di risposte esatte (28 su 40) in un'ora e venti minuti.", "pag_sassari"),
         ("La lingua straniera è a scelta del candidato tra inglese, francese, spagnolo e tedesco: il simulatore usa solo quella che scegli.", "dgr_sardegna"),
     ],
     "origine": ("«Banca dati quiz d'esame» della Camera di Commercio di Sassari, aggiornata al 4 aprile 2022: una tabella con categoria, numero, "
                 "riferimento normativo, domanda, tre risposte e la colonna «Esatta»."),
     "nota": None},
    {"id": "taxi-ncc-cagliari-oristano", "modulo": "ruolo-conducenti", "slug": "cagliari-oristano", "luogo": "Cagliari e Oristano", "fonte": "taxi_caor",
     "ente": "Camera di Commercio di Cagliari-Oristano", "ente_di": "della Camera di Commercio di Cagliari-Oristano", "esame": "esame di idoneità per il ruolo dei conducenti di taxi e NCC",
     "titolo": "Quiz ruolo conducenti Cagliari e Oristano: {n} domande",
     "descr": "La banca dati quiz della Camera di Commercio di Cagliari-Oristano (gennaio 2025): {n} domande con la risposta esatta e un'esercitazione da 30.",
     "n": 30, "max_errori": None, "soglia": 70, "minuti": None, "fonti_regole": ["pag_caor", "dgr_sardegna"],
     "regole": [
         ("La prova è un test a risposta multipla, superato con almeno il 70% di risposte esatte.", "pag_caor"),
         ("Quante domande ha la prova non è scritto nella pagina della Camera: il simulatore ne propone 30 e usa la soglia del 70%.", "pag_caor"),
         ("La lingua straniera è a scelta del candidato tra inglese, francese, spagnolo e tedesco; la toponomastica riguarda il capoluogo: nel simulatore scegli lingua e città.", "dgr_sardegna"),
     ],
     "origine": ("«Banca dati quiz aggiornata al 29 gennaio 2025», pubblicata dalla Camera con l'avviso d'esame: [*] accanto alla risposta esatta, "
                 "domande divise in 12 materie (nel sito numerate di seguito; il numero della materia è nella riga sotto ogni domanda)."),
     "nota": None},
]
for _b in BANCHE:
    _b["path"] = f"{_b['modulo']}/{_b['slug']}/"
    _b["dati"] = carica(f"banche/{_b['id']}.json")
    _b["D"] = _b["dati"]["domande"]
    if _b["id"].startswith("nautica-"):
        _b["nota"] = _b["nota"].format(figure=sum(1 for e in _b["dati"]["escluse"] if "figura" in e["motivo"]), totale_pdf=num(_b["dati"]["totale_pdf"]))


def errori_txt(n):
    return f"{n} errore al massimo" if n == 1 else f"{n} errori al massimo"

CAPTION_ARGOMENTI = {
    "tartufi-lazio": "Il PDF titola solo la prima parte: gli argomenti seguono la determinazione G10268 (64, 65 e 146 quesiti, in quest'ordine).",
    "taxi-ncc-palermo-enna": "Le schede corrette non dividono le domande per argomento.",
    "taxi-ncc-sassari": "Categorie della colonna «Categoria» della tabella; la G divisa per lingua secondo la colonna «Riferimento normativo».",
}

# Banche trovate ma non online (senza chiave ufficiale, file non raggiungibile o non ancora caricato)
NON_ONLINE = {
    "patente-nautica": [
        {"luogo": "Quiz su elementi di carteggio e prova di carteggio", "fonte": "nautica_allegato_a",
         "motivo": "si risolvono sulle carte nautiche dell'Istituto Idrografico della Marina: non riproduciamo carte e figure"},
        {"luogo": "Domande con figura del quiz base e del quiz vela", "fonte": "nautica_allegato_a",
         "motivo": "rimandano a un disegno dell'allegato: le immagini non si riproducono, quindi le domande restano fuori"},
    ],
    "tartufi": [
        {"luogo": "Emilia-Romagna", "fonte": "tart_er", "motivo": "domande senza risposte ufficiali: il PDF «Esempi di quiz» non indica la risposta esatta"},
        {"luogo": "Toscana", "fonte": "tart_toscana_dd5332", "motivo": "il decreto 5332/2017 approva domande (allegato A) e risposte (allegato B), ma i due allegati oggi non si scaricano più dal sito della Regione (errore 404)"},
        {"luogo": "Campania (Provincia di Caserta)", "fonte": "tart_campania", "motivo": "guida del 2008 con una rassegna di quiz senza risposte indicate"},
    ],
    "patentino-fitosanitario": [
        {"luogo": "Sardegna (vendita)", "fonte": "fito_oristano", "motivo": "domande senza risposte ufficiali: il PDF «Elenco domande e soluzioni» non segna la risposta esatta"},
        {"luogo": "Umbria", "url": FJ["non_raggiunte"]["fito_umbria"]["url"], "titolo": FJ["non_raggiunte"]["fito_umbria"]["titolo"],
         "motivo": "il sito della Regione non ha risposto alle nostre richieste del 12 novembre 2026: lo riproveremo"},
    ],
    "ruolo-conducenti": [
        {"luogo": "Roma", "url": FJ["non_raggiunte"]["taxi_roma"]["url"], "titolo": FJ["non_raggiunte"]["taxi_roma"]["titolo"],
         "motivo": "il server dei documenti della Città metropolitana non ha risposto alle nostre richieste del 12 novembre 2026: lo riproveremo"},
    ],
}

# ---------------------------------------------------------------- fonti e rimandi numerati
FONTI_DEF = {fid: f for fid, f in FJ["file"].items()}


class Rimandi:
    def __init__(self):
        self.ordine = []

    def ref(self, ids):
        if isinstance(ids, str):
            ids = [ids]
        nums = []
        for i in ids:
            if i not in FONTI_DEF:
                raise SystemExit(f"fonte sconosciuta: {i}")
            if FONTI_DEF[i].get("http") != 200:
                raise SystemExit(f"fonte non letta: {i}")
            if i not in self.ordine:
                self.ordine.append(i)
            nums.append(self.ordine.index(i) + 1)
        return '<sup class="ref">' + ",".join(f'<a href="#f{n}" aria-label="fonte {n}">[{n}]</a>' for n in sorted(set(nums))) + "</sup>"

    def elenco(self):
        if not self.ordine:
            return ""
        voci = []
        for n, i in enumerate(self.ordine, 1):
            f = FONTI_DEF[i]
            dt = f" Documento del {data_lunga(f['data'])}." if f.get("data") else ""
            voci.append(f'<li id="f{n}"><a href="{h(f["url"])}" rel="noopener">{h(f["titolo"])}</a> · {h(f["chi"])}.{dt} '
                        f'<span class="small">Letto il {data_lunga(f["letto_il"])}; impronta SHA-256 {f["sha256"][:12]}.</span></li>')
        return (f'<section class="fonti-box" aria-labelledby="fonti-h"><h2 id="fonti-h">{ico("doc")}Fonti</h2><ol>{"".join(voci)}</ol>'
                '<p class="small">Domande e risposte sono riprodotte dai documenti pubblicati dagli enti sui loro siti, indicati qui sopra con ente, data e link '
                '(per i testi degli atti ufficiali delle amministrazioni pubbliche vale l\'art. 5 della legge 633/1941); impaginazione, conteggi e simulatore sono nostri. '
                'Come lavoriamo: <a href="/come-lavoriamo/">metodo e controlli</a>.</p></section>')


# ---------------------------------------------------------------- risorse
def _impronta(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:10]


CSS = re.sub(r"\n", "", stile.CSS)
SPRITE = ('<svg xmlns="http://www.w3.org/2000/svg">' + "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in stile.ICONE.items()) + "</svg>\n")
APP_JS = stile.APP_JS.strip() + "\n"
ASSET = {f"site.{_impronta(CSS)}.css": CSS, f"app.{_impronta(APP_JS)}.js": APP_JS,
         f"favicon.{_impronta(stile.FAVICON_SVG)}.svg": stile.FAVICON_SVG, f"icons.{_impronta(SPRITE)}.svg": SPRITE}
CSS_FILE, JS_FILE, FAVICON_FILE, ICONS_FILE = ASSET
LOGO = f'<img src="/assets/{FAVICON_FILE}" width="34" height="34" alt="">'


def ico(nome, cls="ico"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="/assets/{ICONS_FILE}#i-{nome}"/></svg>'


# ---------------------------------------------------------------- Amazon (solo dove ci sono manuali d'esame veri: vedi dati/affiliati.json)
FRASE_AMAZON = "In qualità di Affiliato Amazon, ricevo un guadagno dagli acquisti idonei."
PRIVACY_AMAZON = ("<h2>Programma di Affiliazione Amazon</h2><p>Partecipiamo al Programma di Affiliazione Amazon EU, un programma di "
                  "affiliazione che permette ai siti di ricevere una commissione pubblicitaria pubblicizzando e fornendo link al sito Amazon.it. "
                  f"{FRASE_AMAZON} I link ad Amazon.it portano a ricerche di libri: prezzi e disponibilità li vedi solo su Amazon e possono cambiare.</p>")


def url_amazon(modulo):
    voce = AFF.get("amazon") or {}
    parole = (voce.get("ricerche") or {}).get(modulo) or ""
    if not voce.get("attivo") or not parole:
        return ""
    url = f"https://www.amazon.it/s?k={quote_plus(parole)}&i=stripbooks&tag={voce['tag']}"
    if not MON.dominio_ammesso(url) or "tag=guideesami-21" not in url:
        raise SystemExit(f"affiliati.json: link Amazon non ammesso: {url}")
    return url


def ci_sono_affiliati():
    return any(url_amazon(m) for m in MODULI)


TESTI_MANUALI = {
    "ruolo-conducenti": ("Oltre alle domande ufficiali, per l'orale e per le materie scritte aiuta un manuale aggiornato. Prima di comprare controlla "
                         "l'anno di edizione e che il libro riguardi la tua provincia o Regione.", "Libri sul ruolo conducenti taxi e NCC su Amazon"),
    "patente-nautica": ("Per il carteggio e per la prova pratica servono un manuale e le carte nautiche, che qui non ci sono. Prima di comprare controlla "
                        "che il libro segua l'elenco dei quesiti del 2022.", "Manuali e quiz della patente nautica su Amazon"),
}


def riquadro_manuali(modulo):
    url = url_amazon(modulo)
    if not url:
        return ""
    return f"""<section class="card manuali" aria-labelledby="manuali-titolo" style="margin-top:28px">
<h2 id="manuali-titolo" style="margin-top:0">{ico("book")}Libri per prepararsi</h2>
<p>{h(TESTI_MANUALI[modulo][0])}</p>
<p class="manuali-link"><a href="{h(url)}" rel="sponsored noopener" target="_blank">{h(TESTI_MANUALI[modulo][1])}</a></p>
<p class="small aff-nota">{FRASE_AMAZON}</p>
{MON.nota_trasparenza("it")}
</section>"""


# ---------------------------------------------------------------- scheletro
URLS = []
AD = '<div class="ad-slot" aria-hidden="true"></div>'
MENU = [("patente-nautica/", "Patente nautica"), ("tartufi/", "Tartufi"), ("patentino-fitosanitario/", "Patentino fitosanitario"), ("ruolo-conducenti/", "Taxi e NCC"),
        ("come-lavoriamo/", "Come lavoriamo")]
DISCLAIMER = ("<strong>Sito indipendente.</strong> Le domande e le risposte sono quelle dei documenti ufficiali del Ministero, delle Regioni e "
              "delle Camere di Commercio, con il link al PDF; il sito non è affiliato a nessun ente e non organizza esami. Le banche possono cambiare: prima "
              "dell'esame controlla sul sito dell'ente la versione in vigore e le regole della tua sessione.")


def parole_principali(corpo):
    t = re.sub(r"<(form|script|style|svg)\b.*?</\1>", " ", corpo, flags=re.S | re.I)
    t = unescape(re.sub(r"<[^>]+>", " ", t))
    return len(re.findall(r"\w+", t))


def menu_html(percorso):
    out = ""
    for u, t in MENU:
        cur = ' aria-current="page"' if percorso and percorso.startswith(u) else ""
        out += f'<a href="/{u}"{cur}>{h(t)}</a>'
    return out


def pagina(percorso, titolo, descrizione, corpo, testata="", briciole=None, jsonld=None, indicizza=True, file=None):
    file = file or (percorso + "index.html" if percorso else "index.html")
    url_pag = f"{URL_SITO}/{percorso}"
    if indicizza:
        URLS.append(percorso)
    ld = list(jsonld or [])
    bc = ""
    if briciole:
        voci = [{"@type": "ListItem", "position": i, "name": n, "item": f"{URL_SITO}/{p}"} for i, (n, p) in enumerate(briciole, 1)]
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": voci})
        bc = ('<nav class="briciole" aria-label="Percorso">' + " › ".join([f'<a href="/{p}">{h(n)}</a>' for n, p in briciole[:-1]] + [h(briciole[-1][0])]) + "</nav>")
    testata = testata.replace("{bc}", bc)
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    con_pub = indicizza and parole_principali(testata + corpo) >= MIN_PAROLE_ADSENSE
    adsense = MON.script_adsense(SITO_ID, con_pub)
    if not con_pub:
        corpo = corpo.replace(AD, "")
    corpo_tr = corpo + MON.riga_trasparenza(corpo, "it")
    testo = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="{GOOGLE_VERIFICA}">{adsense}
<title>{h(titolo)}</title>
<meta name="description" content="{h(descrizione)}">
{f'<link rel="canonical" href="{url_pag}">' if indicizza else '<meta name="robots" content="noindex">'}
<meta property="og:title" content="{h(titolo)}">
<meta property="og:description" content="{h(descrizione)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url_pag}">
<meta property="og:site_name" content="{NOME}">
<meta property="og:locale" content="it_IT">
<meta property="og:image" content="{URL_SITO}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#18213F">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="/assets/{FAVICON_FILE}" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/public-sans.woff2" as="font" type="font/woff2" crossorigin>
<script>{stile.TEMA_JS}</script>
<link rel="stylesheet" href="/assets/{CSS_FILE}">
{ld_html}
</head>
<body>
<a class="skip" href="#main">Vai al contenuto</a>
<header class="top"><div class="wrap">
<a class="logo" href="/">{LOGO}<span>Quiz <b>Ufficiali</b></span></a>
<nav class="menu" aria-label="Principale">{menu_html(percorso)}</nav>
<button type="button" class="tema" data-tema aria-label="Tema chiaro o scuro">{ico("moon", "ico i-moon")}{ico("sun", "ico i-sun")}</button>
<details class="nav-m"><summary aria-label="Menu">{ico("menu")}</summary><nav aria-label="Principale">{menu_html(percorso)}</nav></details>
</div></header>
<main id="main">
{testata}
<div class="wrap">
{corpo_tr}
<p class="disclaimer">{DISCLAIMER}</p>
</div>
</main>
<footer><div class="wrap">
<div class="f-grid"><div>
<a class="logo" href="/">{LOGO}<span>Quiz <b>Ufficiali</b></span></a>
<p><strong>{NOME}</strong> mette online, gratis, le banche ufficiali dei quiz d'esame pubblicate da Ministero, Regioni e Camere di Commercio, con la risposta
esatta indicata dall'ente e la pagina del PDF. È un sito indipendente, non affiliato a nessun ente.</p>
</div><div>
<h2>Esami</h2><ul>{"".join(f'<li><a href="/{m}/">{h(v["nome"])}</a></li>' for m, v in MODULI.items())}</ul>
</div><div>
<h2>Il sito</h2><ul><li><a href="/come-lavoriamo/">Come lavoriamo</a></li><li><a href="/come-lavoriamo/#segnala">Segnala un errore</a></li>
<li><a href="/chi-siamo/">Chi siamo</a></li><li><a href="/privacy/">Privacy</a></li></ul>
</div></div>
<p class="f-base">Domande e risposte: documenti ufficiali degli enti, citati in ogni pagina. Controlli del {data_lunga(OGGI)}.</p>
</div></footer>
<script src="/assets/{JS_FILE}" defer></script>
{SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")


def banda(eyebrow, titolo, sub, extra="", corta=False, icona="doc"):
    return f"""<section class="band{' corta' if corta else ''}"><div class="wrap band-in">{{bc}}
<p class="eyebrow">{ico(icona)}{h(eyebrow)}</p>
<h1>{h(titolo)}</h1>
<p class="sub">{sub}</p>{extra}
</div></section>"""


def tabella(intest, righe, caption="", num_=None):
    num_ = num_ or []
    th = "".join(f'<th scope="col"{" class=\"n\"" if i in num_ else ""}>{x}</th>' for i, x in enumerate(intest))
    body = "".join("<tr>" + "".join(f'<td{" class=\"n\"" if i in num_ else ""}>{x}</td>' for i, x in enumerate(r)) + "</tr>" for r in righe)
    cap = f"<caption>{caption}</caption>" if caption else ""
    return f'<div class="tab"><table class="dati">{cap}<thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def nota(testo, tipo="info", icona="info"):
    return f'<div class="nota {tipo}">{ico(icona)}<p>{testo}</p></div>'


# ---------------------------------------------------------------- sezioni delle banche
LINGUE = ["Inglese", "Francese", "Spagnolo", "Tedesco"]
ETICHETTE = {"Colreg e segnalamento marittimo": "COLREG e segnalamento marittimo", "Attrezzatura delle unita' a vela": "Attrezzatura delle unità a vela",
             "Manovre delle unita' a vela": "Manovre delle unità a vela"}


def sezione_vista(b, d):
    """Nome dell'argomento mostrato nel sito (Sassari: la categoria della tabella; la G divisa per lingua dal riferimento)."""
    if b["id"] == "taxi-ncc-sassari":
        if d["sezione"] == "G":
            lingua = d["riferimento"].split()[-1]
            return f"Categoria G, lingua straniera: {lingua.lower()}"
        return f"Categoria {d['sezione']}"
    return ETICHETTE.get(d["sezione"], d["sezione"]) or "Domande"


def sezioni(b):
    nomi = list(dict.fromkeys(sezione_vista(b, d) for d in b["D"]))
    return nomi


def scelte(b, nomi):
    """Gruppi di argomenti fra cui il candidato sceglie (lingua straniera, città della toponomastica)."""
    out = []
    lingue = [(l, [i for i, s in enumerate(nomi) if s.lower().endswith(l.lower()) or s.lower().endswith(l.lower()[:-1] + "a")]) for l in LINGUE]
    lingue = [(l, ix) for l, ix in lingue if ix]
    if len(lingue) > 1:
        out.append({"etichetta": "Lingua straniera", "opzioni": lingue})
    if b["id"] == "taxi-ncc-cagliari-oristano":
        citta = [(c, [i for i, s in enumerate(nomi) if s == f"Toponomastica {c}"]) for c in ("Cagliari", "Oristano")]
        out.append({"etichetta": "Toponomastica", "opzioni": citta})
    return out


def riferimento_sassari(b, d):
    return f" · riferimento: {h(d['riferimento'])}" if d.get("riferimento") else ""


def meta_domanda(b, d):
    p = f"Pagina {d['pagina']} del PDF"
    if b["id"] == "taxi-ncc-palermo-enna":
        sed = [d["seduta"]] + d.get("altre_sedute", [])
        return f"Uscita nella seduta del {', '.join(sed)}" + (" (più sedute)" if len(sed) > 1 else "") + f" · scheda del {d['seduta']}, pagina {d['pagina']}"
    if b["id"] == "taxi-ncc-cagliari-oristano":
        return f"{p} · domanda {d['n_sezione']} della materia «{h(d['sezione'])}»"
    if b["id"].startswith("nautica-"):
        return f"{p} · numero ufficiale {d['n']} · progressivo {h(d['progressivo'])} · {h(d['voce'])}"
    if b["id"] == "taxi-ncc-sassari":
        return f"{p} · numero ufficiale {d['n']}{riferimento_sassari(b, d)}"
    extra = f" · {h(d['nota_pdf'])}" if d.get("nota_pdf") else ""
    return f"{p} · numero ufficiale {d['n']}{extra}"


def elenco_domande(b, nomi):
    blocchi = []
    for si, s in enumerate(nomi):
        dd = [d for d in b["D"] if sezione_vista(b, d) == s]
        voci = []
        for d in dd:
            opz = "".join(f'<li{" class=\"esatta\"" if k == d["esatta"] else ""}><span class="r">{h(r)}</span>'
                          f'{" <span class=\"tag ok\">risposta ufficiale</span>" if k == d["esatta"] else ""}</li>' for k, r in enumerate(d["risposte"]))
            voci.append(f'<li id="d-{d["n"]}" data-dom data-n="{d["n"]}" data-s="{si}" data-e="{d["esatta"]}" data-p="{d["pagina"]}" data-sez="{h(s)}">'
                        f'<p class="dq"><span class="num">{d["n"]}.</span> <span class="t">{h(d["testo"])}</span></p>'
                        f'<ol class="opz" type="a">{opz}</ol><p class="dmeta">{meta_domanda(b, d)}</p></li>')
        blocchi.append(f'<details class="sezione-dom"{" open" if len(nomi) == 1 else ""}><summary>{h(s)} <span>{num(len(dd))} domande</span></summary>'
                       f'<ol class="domande">{"".join(voci)}</ol></details>')
    return "".join(blocchi)


def quiz_html(b, nomi):
    sc = scelte(b, nomi)
    regola = ""
    if b["max_errori"] is not None:
        regola = f"{b['n']} domande a caso, superato con {errori_txt(b['max_errori'])}"
    elif b["soglia"]:
        regola = f"{b['n']} domande a caso, superato con almeno il {b['soglia']}% di risposte esatte"
    else:
        regola = f"{b['n']} domande a caso, solo il punteggio"
    if b["minuti"]:
        regola += f", {b['minuti']} minuti"
    regola = b.get("regola_sim", regola)
    quote = [[nomi.index(ETICHETTE.get(k, k)), v] for k, v in b.get("quote", {}).items()]
    if quote and sum(v for _, v in quote) != b["n"]:
        raise SystemExit(f"{b['id']}: le quote per argomento non sommano a {b['n']}")
    sel_sc = "".join(f'<label>{h(g["etichetta"])}<select data-scelta="{gi}">' + "".join(f'<option value="{oi}">{h(o[0])}</option>' for oi, o in enumerate(g["opzioni"]))
                     + "</select></label>" for gi, g in enumerate(sc))
    opz_sez = "".join(f'<option value="{i}">{h(s)} ({sum(1 for d in b["D"] if sezione_vista(b, d) == s)})</option>' for i, s in enumerate(nomi))
    sc_json = json.dumps([{"etichetta": g["etichetta"], "opzioni": [[o[0], o[1]] for o in g["opzioni"]]} for g in sc], ensure_ascii=False)
    return f"""<section class="card quiz" id="simulatore" data-quiz data-n="{b['n']}" data-max-errori="{'' if b['max_errori'] is None else b['max_errori']}"
data-soglia="{b['soglia'] or ''}" data-minuti="{b['minuti'] or ''}" data-scelte="{h(sc_json)}" data-quote="{h(json.dumps(quote))}" data-orale="{b.get('orale_da') or ''}">
<div class="quiz-h"><h2>{ico("play")}Simulatore</h2><span class="pill">gratis, nel browser</span></div>
<p class="quiz-nojs" data-nojs>Il simulatore funziona con JavaScript attivo. Qui sotto trovi comunque tutte le domande con la risposta ufficiale.</p>
<div class="quiz-avvio" data-avvio hidden>
{f'<div class="scelte">{sel_sc}</div>' if sel_sc else ''}
<div class="blocco"><h3>{"Simulazione d'esame" if (b["max_errori"] is not None or b["soglia"]) else "Esercitazione"}</h3><p>{h(regola)}.</p>
<button type="button" class="btn" data-avvia="esame">{ico("play")}Inizia</button></div>
<div class="blocco"><h3>Ripasso per argomento</h3><label>Argomento<select data-sezione>{opz_sez}</select></label>
<button type="button" class="btn sec" data-avvia="ripasso">Ripassa tutte le domande</button></div>
</div>
<div class="quiz-gioco" data-gioco hidden>
<div class="quiz-barra"><span data-pos></span><span data-tempo aria-live="off"></span></div>
<div class="quiz-prog"><i data-prog></i></div>
<p class="quiz-q" data-q></p>
<div class="quiz-opz" data-opz></div>
<div class="quiz-fb" data-fb hidden aria-live="polite"></div>
<div class="quiz-azioni"><button type="button" class="btn" data-avanti hidden>Avanti</button></div>
</div>
<div class="quiz-fine" data-fine hidden aria-live="polite"></div>
</section>"""


def pagina_banca(b):
    rim = Rimandi()
    D, nomi = b["D"], sezioni(b)
    f = FONTI_DEF[b["fonte"]]
    n = len(D)
    regola_breve = b.get("regola_breve") or (errori_txt(b["max_errori"]) if b["max_errori"] is not None else
                    f"almeno il {b['soglia']}% giuste" if b["soglia"] else "soglia non scritta")
    testata = banda(f"{MODULI[b['modulo']]['breve']} · {b['luogo']}", b["titolo"].format(n=num(n)),
                    h(b["sub"]) if b.get("sub") else
                    f"Le domande ufficiali {h(b['ente_di'])} per l'{h(b['esame'])}, con la risposta esatta indicata dall'ente e la pagina del PDF. "
                    "Nessuna spiegazione aggiunta: solo il testo ufficiale.", icona=MODULI[b["modulo"]]["icona"])
    data_doc = b.get("data_doc") or (data_lunga(f["data"]) if f.get("data") else "senza data")
    fonte_riga = f"Fonte: {b['ente']}, " + (f"documento del {data_lunga(f['data'])}" if f.get("data") else data_doc if b.get("data_doc") else "documento senza data") + "."
    cifre = (f'<div class="card cifre pull">'
             f'<div class="cifra main"><b>{num(n)}</b><span>{h(b.get("cifra_n", "domande nel sito, tutte con la risposta ufficiale"))}</span></div>'
             f'<div class="cifra"><b>{b["n"]}</b><span>domande {"all&#39;esame" if b["max_errori"] is not None or b["soglia"] else "nell&#39;esercitazione"}</span></div>'
             f'<div class="cifra"><b>{h(regola_breve)}</b><span>per superare la prova{rim.ref(b["fonti_regole"][0])}</span></div>'
             f'<div class="cifra"><b>{h(data_doc)}</b><span>data del documento{rim.ref(b["fonte"])}</span></div>'
             f'<p class="asof">{ico("check")} {h(fonte_riga)} PDF ufficiale letto il {data_lunga(f["letto_il"])}; ogni domanda è stata ricontrollata sul PDF '
             f'(impronta SHA-256 {f["sha256"][:12]}).</p></div>')
    corpo = cifre + quiz_html(b, nomi)
    corpo += '<h2 id="esame">Com\'è l\'esame</h2><div class="testo"><ul>'
    corpo += "".join(f"<li>{h(t)}{rim.ref(fid)}</li>" for t, fid in b["regole"]) + "</ul></div>"
    if b.get("nota"):
        corpo += nota(h(b["nota"]))
    dd = b["dati"]
    orig = b["origine"]
    if b["id"] == "taxi-ncc-palermo-enna":
        sedute = sorted({d["seduta"] for d in D} | {s for d in D for s in d.get("altre_sedute", [])})
        orig = orig.format(sedute=len([k for k in FONTI_DEF if re.fullmatch(r"paen_\d+", k)]), lette=n + dd["scartate"]["doppie"] + dd["scartate"]["nulle"],
                           doppie=dd["scartate"]["doppie"], nulle=dd["scartate"]["nulle"])
        del sedute
    corpo += f'<h2 id="origine">Da dove vengono le domande</h2><div class="testo"><p>{h(orig)}{rim.ref(b["fonte"])}'
    for x in b.get("altre_fonti", []):
        corpo += rim.ref(x)
    corpo += "</p>"
    esc = dd.get("escluse") or []
    if esc and "motivo" in esc[0]:
        per = {}
        for e in esc:
            per.setdefault(e["motivo"], []).append(e["n"])
        corpo += (f"<p>Del documento ufficiale restano fuori {num(len(esc))} domande: "
                  + "; ".join(f"{len(v)} perché {h(k)} (n. {', '.join(str(x) for x in v)})" for k, v in per.items()) + ".</p>")
        esc = []
    if esc:
        corpo += (f'<p>{"Una domanda è rimasta fuori" if len(esc) == 1 else f"{len(esc)} domande sono rimaste fuori"} dal sito perché nel PDF la risposta segnata '
                  "nel testo e quella della tabella finale non coincidono: "
                  + "; ".join(f"n. {e['n']} (pagina {e['pagina']}: nel testo {e['segno_nel_testo']}), in tabella {e['tabella_finale']})" for e in esc)
                  + ". Chiedi all'ente quale vale.</p>")
    corr = [d for d in D if d.get("nota_pdf")]
    for d in corr:
        corpo += f"<p>Domanda n. {d['n']}: {h(d['nota_pdf'])}.</p>"
    corpo += (f'<p>Non aggiungiamo spiegazioni: il documento ufficiale non ne ha e non vogliamo mettere parole nostre accanto alla risposta dell\'ente. '
              f'Se trovi una differenza con il PDF, <a href="/come-lavoriamo/#segnala">segnalacela</a>.</p></div>')
    corpo += AD
    righe = [[h(s), num(sum(1 for d in D if sezione_vista(b, d) == s))] for s in nomi]
    corpo += '<h2 id="argomenti">Le domande per argomento</h2>' + tabella(["Argomento", "Domande"], righe, num_=[1],
                                                                          caption=CAPTION_ARGOMENTI.get(b["id"], "Argomenti come nel documento ufficiale."))
    corpo += (f'<h2 id="domande">Tutte le {num(n)} domande con la risposta ufficiale</h2><p class="small">Apri un argomento per vedere le domande. La risposta '
              'esatta è quella indicata dall\'ente; sotto ogni domanda c\'è la pagina del PDF per controllarla.</p>' + elenco_domande(b, nomi))
    corpo += riquadro_manuali(b["modulo"])
    altre = [x for x in BANCHE if x["modulo"] == b["modulo"] and x is not b]
    if altre:
        corpo += (f'<h2>Altre banche: {h(MODULI[b["modulo"]]["nome"].lower())}</h2><ul class="griglia">'
                  + "".join(f'<li><a href="/{x["path"]}"><b>{h(x["luogo"])}</b><span><em>{num(len(x["D"]))}</em> {h(x.get("unita", "domande"))} · {h(x["ente"])}</span></a></li>' for x in altre)
                  + "</ul>")
    corpo += rim.elenco()
    ld = [{"@context": "https://schema.org", "@type": "Quiz", "name": b["titolo"].format(n=num(n)), "inLanguage": "it", "educationalLevel": "esame di abilitazione",
           "about": b["esame"], "isBasedOn": f["url"], "numberOfQuestions": n}]
    pagina(b["path"], b["titolo"].format(n=num(n)), b["descr"].format(n=num(n)), corpo, testata,
           briciole=[("Home", ""), (MODULI[b["modulo"]]["nome"], f"{b['modulo']}/"), (b["luogo"], b["path"])], jsonld=ld)


def pagina_modulo(m):
    M = MODULI[m]
    rim = Rimandi()
    vive = [b for b in BANCHE if b["modulo"] == m]
    testata = banda(M["nome"], M["h1"], h(M["sub"]), icona=M["icona"])
    if m == "patente-nautica":
        corpo = ('<div class="card pull testo"><p style="margin:0"><strong>Un solo elenco per tutta Italia.</strong> Le domande scritte della patente nautica '
                 'vengono dall\'elenco unico nazionale del Ministero: ogni pagina ha tutte le domande di testo con la risposta esatta, le regole della prova '
                 'scritte nel documento e un simulatore che estrae le domande come all\'esame.</p></div>')
    else:
        corpo = '<div class="card pull testo"><p style="margin:0"><strong>Come usare queste pagine.</strong> Scegli la tua Regione o provincia: ogni pagina ha tutte le domande del documento ufficiale con la risposta esatta, le regole della prova scritte dall\'ente e un simulatore che estrae le domande come all\'esame. Le banche cambiano da un ente all\'altro: studia quella dell\'ente che ti esamina.</p></div>'
    corpo += f'<h2 id="banche">Le banche con la risposta ufficiale ({len(vive)})</h2><ul class="griglia">'
    for b in vive:
        corpo += (f'<li><a href="/{b["path"]}"><b>{h(b["luogo"])}</b><span><em>{num(len(b["D"]))}</em> {h(b.get("unita", "domande"))} · {h(b["ente"])}</span>'
                  f'<span>{h(b["regole"][0][0])}</span></a></li>')
    corpo += "</ul>"
    corpo += '<h2 id="esami">Le regole d\'esame, ente per ente</h2>'
    righe = []
    for b in vive:
        if b["max_errori"] is not None:
            reg = f"{b['n']} domande, {b.get('regola_breve') or errori_txt(b['max_errori'])}"
        elif b["soglia"]:
            reg = (f"{b['n']} domande, " if b["id"] != "taxi-ncc-cagliari-oristano" else "numero di domande non scritto, ") + f"almeno il {b['soglia']}% giuste"
        else:
            reg = "test a risposta multipla, numero di domande e soglia non scritti"
        tempo = f"{b['minuti']} minuti" if b["minuti"] else "non scritto"
        righe.append([f'<a href="/{b["path"]}">{h(b["luogo"])}</a>', h(reg) + rim.ref(b["fonti_regole"][0]), h(tempo), num(len(b["D"]))])
    corpo += tabella(["Banca", "Prova scritta", "Tempo", "Domande nel sito"], righe, num_=[3],
                     caption="Regole lette nei documenti degli enti (fonti in fondo alla pagina).")
    if m == "patente-nautica":
        base = next(b for b in vive if b["id"] == "nautica-base")
        corpo += ('<h2 id="prove">Quali prove scritte per quale patente</h2><p>Il decreto ministeriale 323 del 2021 stabilisce le prove scritte in base '
                  f'all\'abilitazione richiesta.{rim.ref("nautica_dm323")} Si comincia sempre dal carteggio; chi non lo supera non passa al quiz base.</p>')
        corpo += tabella(["Abilitazione richiesta", "Prove scritte, nell'ordine"], [
            ["Entro 12 miglia dalla costa, solo motore", "1. quiz su elementi di carteggio nautico; 2. quiz base"],
            ["Entro 12 miglia dalla costa, vela, motore e propulsione mista", "1. quiz su elementi di carteggio nautico; 2. quiz base; 3. quiz vela"],
            ["Senza limiti dalla costa, solo motore", "1. prova di carteggio nautico; 2. quiz base (solo per chi non ha già l'abilitazione entro le 12 miglia)"],
            ["Senza limiti dalla costa, vela, motore e propulsione mista", "1. prova di carteggio nautico; 2. quiz base (solo per chi non ha già l'abilitazione entro le 12 miglia); 3. quiz vela"],
        ], caption="Articolo sugli esami per le patenti di categoria A e C del decreto ministeriale 323/2021.")
        corpo += (f'<h2 id="temi">Le 20 domande del quiz base, tema per tema</h2><p>L\'allegato C dello stesso decreto dice quante domande escono per ogni tema.'
                  f'{rim.ref("nautica_dm323")} Il nostro simulatore del quiz base estrae le domande con questa distribuzione.</p>')
        nomi_b = sezioni(base)
        corpo += tabella(["Tema", "Domande all'esame", "Domande di testo nel sito"],
                         [[h(ETICHETTE.get(k, k)), str(v), num(sum(1 for d in base["D"] if sezione_vista(base, d) == ETICHETTE.get(k, k)))] for k, v in base["quote"].items()]
                         + [["Totale", str(sum(base["quote"].values())), num(len(base["D"]))]], num_=[1, 2],
                         caption="Distribuzione dell'allegato C al decreto ministeriale 323/2021; nel sito mancano le domande con figura.")
        del nomi_b
        corpo += (f'<h2 id="in-vigore">L\'elenco del 2022 è ancora quello in uso?</h2><div class="testo"><p>Sì, per quello che pubblica il Ministero. Il decreto 131 del '
                  f'31 maggio 2022 ha sostituito l\'allegato A con l\'elenco dei quesiti{rim.ref("nautica_dd131")}, e nella pagina «Patenti nautiche: normativa», letta il '
                  f'{data_lunga(FONTI_DEF["pag_mit_nautica"]["letto_il"])}, non c\'è nessun decreto successivo che lo cambia per le patenti di categoria A, B e C'
                  f'{rim.ref("pag_mit_nautica")}. I decreti più recenti riguardano altro: il decreto 62 del 18 aprile 2025 approva un elenco separato per la patente D1 '
                  '(non è in questo sito). Ricontrolliamo la pagina del Ministero a ogni aggiornamento.</p></div>')
    corpo += AD
    no = NON_ONLINE.get(m, [])
    if no:
        corpo += ('<h2 id="non-online">Domande senza risposte ufficiali e banche non ancora online</h2><p>Mettiamo online solo le banche con la risposta '
                  'esatta indicata dall\'ente. Queste le abbiamo trovate, ma per ora restano fuori dal simulatore:</p>')
        rr = []
        for x in no:
            if x.get("fonte"):
                f = FONTI_DEF[x["fonte"]]
                doc = f'<a href="{h(f["url"])}" rel="noopener">{h(f["titolo"])}</a>{rim.ref(x["fonte"])}'
            else:
                doc = f'<a href="{h(x["url"])}" rel="noopener">{h(x["titolo"])}</a>'
            rr.append([h(x["luogo"]), doc, h(x["motivo"])])
        corpo += tabella(["Che cosa", "Documento", "Perché non è nel simulatore"], rr)
    corpo += riquadro_manuali(m)
    corpo += rim.elenco()
    pagina(f"{m}/", M["titolo"], M["descr"], corpo, testata, briciole=[("Home", ""), (M["nome"], f"{m}/")])


def home():
    rim = Rimandi()
    tot = sum(len(b["D"]) for b in BANCHE)
    testata = banda("Quiz d'esame ufficiali, gratis", "Le domande vere dell'esame, con la risposta dell'ente",
                    f"<strong>{num(tot)} domande</strong> da {len(BANCHE)} banche ufficiali del Ministero, delle Regioni e delle Camere di Commercio: "
                    "patente nautica, patentino fitosanitario, tesserino dei tartufi, ruolo dei conducenti di taxi e NCC. Ogni risposta ha accanto la "
                    "pagina del PDF da cui viene.", icona="check")
    corpo = '<div class="card cifre pull">'
    for m, M in MODULI.items():
        bb = [b for b in BANCHE if b["modulo"] == m]
        corpo += (f'<div class="cifra"><b>{num(sum(len(b["D"]) for b in bb))}</b><span><a href="/{m}/">{h(M["nome"])}</a>: '
                  f'{len(bb)} {"banca" if len(bb) == 1 else "banche"}</span></div>')
    corpo += f'<p class="asof">{ico("check")} Documenti ufficiali riletti il {data_lunga(OGGI)}; ogni domanda è ricontrollata sul PDF.</p></div>'
    for m, M in MODULI.items():
        bb = [b for b in BANCHE if b["modulo"] == m]
        corpo += f'<h2 id="{m}">{ico(M["icona"])} <a href="/{m}/">{h(M["nome"])}</a></h2><ul class="griglia">'
        for b in bb:
            corpo += (f'<li><a href="/{b["path"]}"><b>{h(b["luogo"])}</b><span><em>{num(len(b["D"]))}</em> {h(b.get("unita", "domande"))} · {h(b["ente"])}</span></a></li>')
        corpo += "</ul>"
    corpo += AD
    corpo += ('<h2 id="come">Come funziona</h2><div class="testo"><ol>'
              '<li><strong>Prendiamo il documento ufficiale.</strong> Solo PDF pubblicati da Ministero, Regioni e Camere di Commercio, con il link e la data. '
              'Le banche senza la risposta esatta indicata dall\'ente restano fuori dal simulatore.</li>'
              '<li><strong>Lo trascriviamo e lo ricontrolliamo.</strong> Un programma legge il PDF; un secondo programma, scritto a parte, lo rilegge e confronta '
              'numero di domande, risposte e chiave. Accanto a ogni domanda c\'è la pagina del PDF.</li>'
              '<li><strong>Simuli l\'esame con le regole dell\'ente.</strong> Il simulatore estrae a caso il numero di domande della prova e conta gli errori come '
              'scritto nei documenti (per esempio 20 domande in 30 minuti e 4 errori al massimo per il quiz base della patente nautica).</li></ol>'
              '<p>Non scriviamo spiegazioni nostre: mostriamo la risposta ufficiale e basta. Il sito è gratuito; si sostiene con la pubblicità.</p>'
              '<p><strong>Che cosa non trovi qui.</strong> Le domande con figura della patente nautica e le prove di carteggio (non riproduciamo figure e carte); '
              'le banche che gli enti pubblicano senza la risposta esatta; per Palermo ed Enna la banca dati completa, che la Camera non pubblica: ci sono le domande '
              'uscite alle sedute d\'esame dal 2021 al 2026. Ogni pagina dice che cosa manca e perché.</p></div>')
    corpo += rim.elenco()
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": NOME, "url": URL_SITO + "/", "inLanguage": "it"}]
    pagina("", "Quiz Ufficiali: domande d'esame vere con la risposta dell'ente",
           f"{num(tot)} domande ufficiali con la risposta esatta: patente nautica, patentino fitosanitario, tartufi, ruolo conducenti taxi e NCC. Simulatore gratis.",
           corpo, testata, jsonld=ld)


MODULO_FORM = """<form name="segnalazioni" method="POST" data-netlify="true" netlify-honeypot="bot-field" class="form card">
<input type="hidden" name="form-name" value="segnalazioni">
<p class="hp"><label>Lascia vuoto questo campo <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Pagina e numero della domanda<input type="text" name="pagina" required maxlength="300" placeholder="Per esempio /tartufi/lazio/ domanda 12"></label>
<label>Cosa non torna con il PDF ufficiale?<textarea name="messaggio" required rows="5" maxlength="3000"></textarea></label>
<label>Fonte ufficiale (facoltativa)<input type="url" name="fonte" maxlength="500" placeholder="https://"></label>
<label>La tua email (facoltativa, solo se vuoi una risposta)<input type="email" name="email" maxlength="200" autocomplete="email"></label>
<label class="check"><input type="checkbox" name="consenso" value="si" required><span>Accetto che il messaggio, e l'email se l'ho scritta, siano conservati per controllare e rispondere alla segnalazione (vedi la <a href="/privacy/#segnalazioni">privacy</a>).</span></label>
<button type="submit" class="btn">Invia la segnalazione</button>
</form>"""


def come_lavoriamo():
    rim = Rimandi()
    BB = {b["id"]: b for b in BANCHE}
    LZ = BB["tartufi-lazio"]
    n_esc = sum(len(BB[k]["dati"].get("escluse") or []) for k in ("fitosanitario-sicilia-utilizzatori", "fitosanitario-sicilia-consulenti"))
    n_nulle = BB["taxi-ncc-palermo-enna"]["dati"]["scartate"]["nulle"]
    corpo = ('<div class="card pull"><p style="margin:0"><strong>Pubblichiamo solo domande con la risposta indicata dall\'ente.</strong> Il testo è quello '
             'del PDF ufficiale; non aggiungiamo spiegazioni e non correggiamo le risposte. Se un documento è ambiguo, la domanda resta fuori.</p></div>')
    corpo += '<h2 id="documenti">I documenti che usiamo</h2>'
    rr = []
    for b in BANCHE:
        f = FONTI_DEF[b["fonte"]]
        if b["id"] == "taxi-ncc-palermo-enna":
            ids = [k for k in FONTI_DEF if re.fullmatch(r"paen_\d+", k)]
            doc = f'{len(ids)} schede corrette delle sedute (marzo 2021 - maggio 2026){rim.ref(b["fonte"])}'
            impr = "una per scheda"
        else:
            doc = f'<a href="{h(f["url"])}" rel="noopener">{h(f["titolo"])}</a>{rim.ref(b["fonte"])}'
            impr = f'<code>{f["sha256"][:12]}</code>'
        rr.append([f'<a href="/{b["path"]}">{h(b["luogo"])}</a>', doc, num(len(b["D"])), impr])
    corpo += tabella(["Banca", "Documento", "Domande", "Impronta"], rr, num_=[2],
                     caption="L'impronta SHA-256 (prime 12 cifre) identifica il file letto: se l'ente pubblica un file nuovo, cambia e rifacciamo i controlli.")
    corpo += ('<h2 id="riuso">Perché possiamo pubblicarle</h2><div class="testo"><p>L\'articolo 5 della legge sul diritto d\'autore (legge 633/1941) esclude dalla '
              'tutela «i testi degli atti ufficiali dello Stato e delle amministrazioni pubbliche». L\'elenco dei quesiti della patente nautica è l\'allegato di un '
              'decreto del Ministero; i quesiti del Lazio sono l\'allegato di una determinazione regionale; quelli della Valle d\'Aosta sono «adottati dalla Regione»; '
              'gli elenchi della Sicilia sono pubblicati dal Servizio fitosanitario regionale.</p>'
              '<p>Le banche dati e le schede d\'esame corrette delle Camere di Commercio (Palermo ed Enna, Sassari, Cagliari-Oristano) sono documenti che le Camere '
              'pubblicano sul proprio sito per chi prepara l\'esame: le riportiamo indicando sempre la fonte («Camera di Commercio di…»), la data del documento e il '
              'link al file originale. Se un ente ritiene che un suo documento non debba stare qui, lo togliamo: basta scriverci dal modulo in fondo a questa pagina.</p>'
              '<p>Non riproduciamo immagini, carte o dispense di autori privati; i documenti di formazione non firmati come atti dell\'ente non li usiamo. Per la patente '
              'nautica non riproduciamo le figure dell\'elenco né le carte nautiche dell\'Istituto Idrografico della Marina.</p></div>')
    corpo += '<h2 id="metodo">Come leggiamo i PDF</h2><div class="testo"><ol>'
    corpo += ('<li><strong>La chiave è quella dell\'ente.</strong> Patente nautica: la colonna V/F accanto a ogni risposta nell\'elenco del Ministero; le domande con '
              'figura e quelle con la colonna V/F illeggibile o con due V restano fuori. Lazio e Valle d\'Aosta: la risposta esatta è evidenziata in giallo nel PDF, e il programma legge '
              'il colore. Sicilia: un segno (✓ o asterisco) accanto alla risposta, e in fondo una tabella delle risposte; le confrontiamo. Camere di Commercio '
              'di Palermo ed Enna e di Cagliari-Oristano: [*] accanto alla risposta. Sassari: la colonna «Esatta» della tabella.</li>'
              '<li><strong>Due letture indipendenti.</strong> Un programma estrae le domande; un secondo programma, scritto in modo diverso, rilegge tutti i PDF, '
              'confronta numero di domande e chiave di ogni banca e 50 domande per banca, testo e risposte, scelte a caso.</li>'
              f'<li><strong>I casi dubbi restano fuori.</strong> In Sicilia {n_esc} domande hanno una risposta nel testo e un\'altra nella tabella finale: non sono nel '
              f'sito. A Palermo {n_nulle} {"domanda segnata" if n_nulle == 1 else "domande segnate"} «Domanda nulla» dalla commissione {"è stata tolta" if n_nulle == 1 else "sono state tolte"}.</li>'
              '<li><strong>Le irregolarità del PDF sono scritte.</strong> Quando il PDF ha un difetto di stampa (una lettera mancante, due «b»), la pagina della banca '
              'lo dice e indica come l\'abbiamo letto.</li>'
              + (f'<li><strong>Lazio, doppio controllo.</strong> Le {num(len(LZ["D"]))} domande della determinazione del 2015 coincidono, risposte comprese, con quelle della guida '
                 'pubblicata dalla Regione nel 2021.</li>' if LZ["dati"]["confronto_guida_2021"]["differenze"] == 0 else '') + '</ol></div>')
    corpo += ('<h2 id="regole">Le regole del simulatore</h2><div class="testo"><p>Numero di domande, tempo ed errori ammessi vengono da frasi lette nei documenti '
              'degli enti e ricontrollate a ogni aggiornamento. Dove l\'ente non scrive un numero, la pagina lo dice e il simulatore propone un\'esercitazione.</p></div>')
    corpo += ('<h2 id="aggiornamenti">Ogni quanto aggiorniamo</h2><div class="testo"><p>Ogni mese riscarichiamo i documenti: se l\'impronta di un file cambia, '
              'rileggiamo la banca e rifacciamo tutti i controlli. Le schede delle sedute di Palermo ed Enna si aggiungono quando la Camera le pubblica.</p></div>')
    corpo += ('<h2 id="segnala">Segnala un errore</h2><p>Hai trovato una domanda diversa dal PDF ufficiale, o una banca più recente? Scrivici la pagina e il numero '
              'della domanda. L\'email è facoltativa.</p>' + MODULO_FORM)
    corpo += rim.elenco()
    testata = banda("Come lavoriamo", "Come leggiamo e controlliamo le banche ufficiali",
                    "Quali documenti usiamo, come leggiamo la risposta esatta, quali domande restano fuori e ogni quanto aggiorniamo.", corta=True, icona="shield")
    pagina("come-lavoriamo/", "Come lavoriamo: documenti ufficiali e controlli",
           "Come Quiz Ufficiali legge le banche d'esame di Ministero, Regioni e Camere di Commercio: chiave ufficiale, doppia lettura dei PDF, domande escluse.",
           corpo, testata, briciole=[("Home", ""), ("Come lavoriamo", "come-lavoriamo/")])


def chi_siamo():
    corpo = ('<div class="card pull testo"><p><strong>Quiz Ufficiali è un sito informativo indipendente e gratuito.</strong> Raccoglie le banche dei quiz d\'esame '
             'pubblicate da Ministero, Regioni e Camere di Commercio e le rende facili da studiare, con un simulatore nel browser.</p></div>'
             '<h2>Perché esiste</h2><div class="testo"><p>Le domande ufficiali di molti esami (patente nautica, patentino fitosanitario, tartufi, ruolo dei conducenti) '
             'sono PDF lunghi, difficili da usare al telefono. Qui trovi le stesse domande, con la risposta dell\'ente e la pagina del PDF per controllarla.</p></div>'
             '<h2>Cosa non siamo</h2><div class="testo"><ul><li>Non siamo un ministero, una Regione, una Camera di Commercio o una scuola, e non siamo affiliati a nessun ente.</li>'
             '<li>Non organizziamo esami e non vendiamo corsi o accessi.</li><li>Non scriviamo spiegazioni nostre accanto alle risposte ufficiali.</li></ul></div>'
             '<h2>Come si sostiene</h2><div class="testo"><p>Il sito può mostrare pubblicità di Google AdSense nelle pagine con più contenuto e, solo dove esistono '
             'manuali d\'esame, un link segnalato ai libri su Amazon. La pubblicità non cambia nessuna domanda e nessuno paga per comparire.</p><p>Quiz Ufficiali fa parte '
             'di una piccola rete di siti informativi gratuiti dello stesso gestore. Come controlliamo i dati: <a href="/come-lavoriamo/">come lavoriamo</a>.</p></div>')
    testata = banda("Chi siamo", "Chi siamo", "Un sito indipendente che rende facili da studiare le banche ufficiali dei quiz d'esame.", corta=True, icona="info")
    pagina("chi-siamo/", "Chi siamo | Quiz Ufficiali",
           "Quiz Ufficiali è un sito indipendente e gratuito, non affiliato agli enti, con le banche ufficiali dei quiz d'esame e un simulatore.",
           corpo, testata, briciole=[("Home", ""), ("Chi siamo", "chi-siamo/")])


def privacy():
    aff = ci_sono_affiliati()
    cookie = MON.privacy_cookie("it", SITO_ID, aff) or ('<h2>Cookie e contatore visite</h2><p>Per contare le visite usiamo GoatCounter, che non usa cookie. '
                                                       'Il sito non usa cookie di profilazione e non mostra pubblicità.</p>')
    corpo = ('<div class="card pull testo"><p>Questa pagina spiega quali dati tratta Quiz Ufficiali. In breve: pochissimi.</p></div>'
             '<div class="testo"><h2>Chi tratta i dati</h2><p>Titolare del trattamento è Massimiliano Cori (Italia), che gestisce Quiz Ufficiali come progetto indipendente. '
             'Puoi scriverci con il modulo <a href="/come-lavoriamo/#segnala">«Segnala un errore»</a>, anche per le richieste sui tuoi dati.</p>'
             '<h2>Il simulatore</h2><p>Il simulatore funziona solo nel tuo browser: le risposte che dai e i punteggi non vengono inviati né salvati. Il sito ricorda '
             'nel browser solo la scelta del tema chiaro o scuro (memoria locale).</p>'
             f'{cookie}{PRIVACY_AMAZON if aff else ""}'
             '<h2>Hosting</h2><p>Il sito è ospitato da Netlify, Inc., che tratta dati tecnici (come l\'indirizzo IP) per consegnare le pagine e proteggere il servizio. '
             'Netlify può trattare i dati fuori dall\'UE con le garanzie previste dal GDPR (clausole contrattuali standard). Non vendiamo né cediamo i tuoi dati.</p>'
             '<h2 id="segnalazioni">Modulo «Segnala un errore»</h2><p>Se usi il modulo riceviamo la pagina che indichi, il messaggio, il link alla fonte e, solo se la scrivi, '
             'la tua email. Il modulo è gestito da Netlify Forms per nostro conto. Usiamo questi dati solo per controllare la segnalazione e, se hai lasciato l\'email, '
             'risponderti; li cancelliamo quando la segnalazione è chiusa. La base giuridica è il consenso dato con la casella del modulo (art. 6.1.a GDPR), che puoi '
             'ritirare quando vuoi: per chiedere la cancellazione basta un\'altra segnalazione. Non ci sono account né newsletter.</p>'
             '<h2>I tuoi diritti</h2><p>Puoi chiedere accesso, correzione, cancellazione, limitazione, portabilità e opposizione (artt. 15-22 GDPR) e fare reclamo al Garante per la protezione dei dati '
             'personali (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>).</p>'
             f'<h2>Modifiche</h2><p>Aggiorniamo questa pagina quando il sito cambia. Ultimo aggiornamento: {data_lunga(OGGI)}.</p></div>')
    breve = MON.privacy_breve("it", SITO_ID, aff) or "Cosa raccogliamo (pochissimo) e come funziona il contatore delle visite."
    testata = banda("Privacy", "Privacy", h(breve), corta=True, icona="lock")
    pagina("privacy/", "Privacy | Quiz Ufficiali",
           "Privacy di Quiz Ufficiali: simulatore che resta nel browser, contatore delle visite senza cookie e pubblicità solo con il tuo consenso.",
           corpo, testata, briciole=[("Home", ""), ("Privacy", "privacy/")])


def pagina_404():
    corpo = ('<div class="card pull"><p>La pagina che cerchi non esiste. Torna alla <a href="/">home</a> o scegli un esame: '
             + ", ".join(f'<a href="/{m}/">{h(M["nome"].lower())}</a>' for m, M in MODULI.items()) + ".</p></div>")
    testata = banda("Errore 404", "Pagina non trovata", "Questo indirizzo non ha una pagina.", corta=True, icona="alert")
    pagina("", "Pagina non trovata | Quiz Ufficiali", "Pagina non trovata.", corpo, testata.replace("{bc}", ""), indicizza=False, file="404.html")


def extra():
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n", encoding="utf-8")
    (SITO / f"{CHIAVE_INDEXNOW}.txt").write_text(CHIAVE_INDEXNOW, encoding="utf-8")
    MON.scrivi_ads_txt(SITO_ID, SITO)
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{OGGI.isoformat()}</lastmod></url>" for u in URLS)
    (SITO / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n', encoding="utf-8")
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Pubblica solo se è cambiato qualcosa in quiz/sito (ogni pubblicazione consuma crediti Netlify).
  # Impostazioni del sito su Netlify: Base directory = quiz/sito, Build command vuoto, Publish directory = "."
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."

[[headers]]
  for = "/*"
  [headers.values]
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    X-Frame-Options = "DENY"
    Permissions-Policy = "camera=(), microphone=(), geolocation=()"

[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=604800"
""", encoding="utf-8")


def copia_grafica():
    (SITO / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (RADICE / "grafica" / "fonts").glob("*.woff2"):
        shutil.copy(f, SITO / "assets" / "fonts" / f.name)
    og = RADICE / "grafica" / "og.png"
    if og.exists():
        shutil.copy(og, SITO / "assets" / "og.png")
    for nome, t in ASSET.items():
        (SITO / "assets" / nome).write_text(t, encoding="utf-8")


def controlli():
    err = []
    for fid, f in FJ["file"].items():
        if f.get("http") != 200:
            err.append(f"fonte {fid}: HTTP {f.get('http')}")
        manca = [c[:60] for c, ok in f.get("frasi", {}).items() if not ok]
        if manca:
            err.append(f"fonte {fid}: frasi non trovate {manca}")
    for b in BANCHE:
        for d in b["D"]:
            if not (0 <= d["esatta"] < len(d["risposte"])) or len(d["risposte"]) not in (2, 3):
                err.append(f"{b['id']} n. {d['n']}: risposte o chiave non valide")
        for t in (b["titolo"].format(n=len(b["D"])), b["descr"].format(n=len(b["D"]))):
            pass
    if err:
        raise SystemExit("ERRORI NEI DATI:\n" + "\n".join(err))


def main():
    controlli()
    conserva = {}
    if SITO.exists():
        conserva = {p.name: p.read_bytes() for p in SITO.glob("google*.html")}
        shutil.rmtree(SITO)
    SITO.mkdir()
    for nome, contenuto in conserva.items():
        (SITO / nome).write_bytes(contenuto)
    copia_grafica()
    home()
    for m in MODULI:
        pagina_modulo(m)
    for b in BANCHE:
        pagina_banca(b)
    come_lavoriamo()
    chi_siamo()
    privacy()
    pagina_404()
    extra()
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili + 404; {len(BANCHE)} banche, "
          f"{sum(len(b['D']) for b in BANCHE)} domande.")


if __name__ == "__main__":
    main()
