"""Scrive ccnl/dati/inverno.json: termini di preavviso e regole di tredicesima e quattordicesima dei 5 contratti (27/11/2026).

Uso (dalla radice del repository, dopo raccolta/fonti.py):
    python3 ccnl/raccolta/inverno.py

Ogni frase scritta qui deve essere nel testo del contratto salvato in raccolta/_grezzi (spazi e a capo a parte): se una
frase non c'è, il programma si ferma e non scrive niente. Nessun giorno viene da siti terzi. verifica.py rifà poi il
controllo per conto suo: frase nel suo articolo, numeri riletti dalla frase, livelli nominati dalla frase."""
import json
import re
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]
G = R / "raccolta" / "_grezzi"


def norm(t):
    t = t.replace("’", "'").replace("‘", "'").replace(" ", " ")
    return re.sub(r"\s+", " ", t).strip()


TESTI = {}


def testo(fid):
    """Testo del documento: il file .txt più le pagine lette con la lettura ottica (come testo_fonte in verifica.py)."""
    if fid not in TESTI:
        TESTI[fid] = norm(" ".join(x.read_text(encoding="utf-8") for x in [G / f"{fid}.txt"] + sorted((G / "ocr").glob(f"{fid}_p*.txt")) if x.exists()))
    return TESTI[fid]


def f(fid, s):
    """La frase com'è nel testo (apostrofi diritti, spazi singoli); si ferma se non c'è."""
    s = norm(s)
    if s not in testo(fid):
        sys.exit(f"NON TROVATA in {fid}: {s}")
    return s


def cit(fid, dove, s, altra_fonte=False):
    return dict({"dove": dove, "testo": f(fid, s)}, **({"fonte": fid} if altra_fonte else {}))


def unita_di(frase):
    """Come il contratto conta i giorni: «di calendario», «lavorativi», oppure senza dirlo («gg»: mesi, o giorni e basta)."""
    return "lav" if "lavorativ" in frase else ("cal" if "calendario" in frase else "gg")


def voce(fid, frase, et, livelli, mesi=0, giorni=0, unita=None, **k):
    unita = unita_di(frase)
    return dict({"frase": f(fid, frase), "et": et, "livelli": livelli, "mesi": mesi, "giorni": giorni, "unita": unita}, **k)


C = {}

# ------------------------------------------------------------------ terziario
T = "cnel_246574"
righe_t = [("Quadri e I Livello", "Quadro e 1° livello", ["q", "i"]), ("Il e III Livello", "2° e 3° livello", ["ii", "iii"]),
           ("IV e V Livello", "4° e 5° livello", ["iv", "v"]), ("VI e VII Livello", "6° e 7° livello", ["vi", "vii"])]


def gruppi_t(intest, giorni):
    out = []
    for (banda, frase), gg in zip(intest, giorni):
        out.append({"banda": banda, "frase": f(T, frase),
                    "voci": [voce(T, f"{r} {g} giorni di calendario", et, liv, giorni=g) for (r, et, liv), g in zip(righe_t, gg)]})
    return out


# etichette delle fasce: seguono le parole del contratto («oltre i cinque anni e fino a dieci anni di servizio compiuti», «Oltre 5 fino a 10»)
BANDE_5_10 = [{"id": "a", "et": "Fino a 5 anni di servizio"}, {"id": "b", "et": "Oltre 5 e fino a 10 anni"}, {"id": "c", "et": "Oltre 10 anni"}]
BANDE_T = [{"id": "a", "et": "Fino a 5 anni di servizio compiuti"}, {"id": "b", "et": "Oltre 5 e fino a 10 anni compiuti"}, {"id": "c", "et": "Oltre 10 anni compiuti"}]
C["terziario"] = {
    "preavviso": {
        "fonte": T, "dove": "artt. 251, 252 e 256",
        "decorre_breve": "dal 1° o dal 16 del mese",
        "tabelle": [
            {"id": "lic", "caso": "licenziamento", "titolo": "Se ti licenzia l'azienda", "dove": "art. 251",
             "inizio": f(T, "Art. 251 - Termini di preavviso in caso di licenziamento I termini"), "fine": f(T, "Art. 252 - Indennità sostitutiva del preavviso Ai sensi"),
             "bande": BANDE_T,
             "gruppi": gruppi_t([("a", "a) fino a cinque anni di servizio compiuti:"), ("b", "b) oltre i cinque anni e fino a dieci anni di servizio compiuti:"),
                                 ("c", "c) oltre i dieci anni di servizio compiuti:")],
                                [[60, 30, 20, 15], [90, 45, 30, 20], [120, 60, 45, 20]])},
            {"id": "dim", "caso": "dimissioni", "titolo": "Se ti dimetti tu", "dove": "art. 256",
             "inizio": f(T, "Art. 256 - Dimissioni e preavviso In caso di dimissioni"), "fine": f(T, "Art. 257 - Dimissioni per matrimonio In conformità"),
             "bande": BANDE_T,
             "gruppi": gruppi_t([("a", "a) ﬁno a cinque anni di servizio compiuti:"), ("b", "b) oltre i cinque anni e ﬁno a dieci anni di servizio compiuti:"),
                                 ("c", "c) oltre i dieci anni di servizio compiuti:")],
                                [[45, 20, 15, 10], [60, 30, 20, 15], [90, 45, 30, 15]])},
        ],
        "cit": {
            "decorre": cit(T, "art. 251", "I termini di preavviso, a decorrere dal primo o dal sedicesimo giorno di ciascun mese, sono i seguenti:"),
            "decorre_dim": cit(T, "art. 256", "Le dimissioni devono essere rassegnate in ogni caso per iscritto, secondo le modalità previste dalla legge, e comunque con modalità utili a certiﬁcare la data di ricevimento e con rispetto dei seguenti termini di preavviso a decorrere dal primo o dal sedicesimo giorno di ciascun mese:"),
            "indennita": cit(T, "art. 252", "Ai sensi del secondo comma dell’art. 2118 c.c. in caso di mancato preavviso al lavoratore sarà corrisposta una indennità equivalente all’importo della retribuzione di fatto di cui all’art. 212 corrispon- dente al periodo di cui all’articolo precedente, comprensiva dei ratei di 13a e 14a mensilità."),
            "trattenuta": cit(T, "art. 256", "Ove il dipendente non abbia dato il preavviso, il datore di lavoro ha facoltà di ritenergli dalle competenze nette una somma pari al- l’importo della retribuzione di fatto di cui all’art. 212 corrispon- dente ai periodi di cui al comma precedente, comprensiva dei ratei di 13a e 14a mensilità."),
            "rinuncia": cit(T, "art. 256", "Su richiesta del dimissionario, il datore di lavoro può rinunciare al preavviso, facendo in tal caso cessare subito il rapporto di la- voro."),
            "anticipo": cit(T, "art. 256", "Ove invece il datore di lavoro intenda di sua iniziativa far cessare il rapporto prima della scadenza del preavviso, ne avrà fa- coltà, ma dovrà corrispondere al lavoratore l’indennità sostitutiva nelle misure di cui al comma precedente per il periodo di antici- pata risoluzione del rapporto di lavoro."),
            "malattia": cit(T, "art. 190", "Il periodo di malattia è considerato utile ai ﬁni del computo delle indennità di preavviso e di licenziamento."),
            "parttime": cit(T, "art. 100", "I termini di preavviso per i lavoratori occupati a tempo parziale hanno la stessa durata di quelli previsti per i lavoratori a tempo pieno e si calcolano in giorni di calendario indipendentemente dalla durata e dall’articolazione della prestazione lavorativa."),
            "mese": cit(T, "art. 213", "Essa si riferisce pertanto a tutte le giornate del mese di calendario."),
            "giornaliera": cit(T, "art. 214", "La quota giornaliera della retribuzione, sia normale che di fatto, si ottiene, in tutti i casi, dividendo l’importo mensile per il divisore convenzionale 26, fatto salvo quanto previsto dall’art. 194."),
        },
        "ratei": {"mensilita": 14, "cit": "indennita"},
        "esempio": {"tabella": "lic", "livello": "iv", "banda": "a"},
    },
    "tredicesima": {
        "fonte": T, "dove": "art. 224", "quando_breve": "alla vigilia di Natale", "frazione_breve": "15 giorni o più contano un mese",
        "cit": {
            "quanto": cit(T, "art. 224", "In coincidenza con la vigilia di Natale di ogni anno le aziende do- vranno corrispondere al personale dipendente un importo pari ad una mensilità della retribuzione di fatto di cui all’art. 212 (esclusi gli assegni familiari)."),
            "prorata": cit(T, "art. 224", "In caso di prestazione lavorativa ridotta, rispetto all’intero periodo di 12 mesi precedenti alla suddetta data, il lavoratore avrà diritto a tanti dodicesimi dell’ammontare della 13a mensilità quanti sono i mesi interi di servizio prestato"),
            "frazioni": cit(T, "art. 208", "Ad eccezione degli effetti derivanti dalla normativa sugli scatti di anzianità, le frazioni di anno saranno computate, a tutti gli effetti contrattuali, per dodicesimi, computandosi come mese intero le frazioni di mese superiori o uguali a 15 giorni."),
            "parttime": cit(T, "art. 88", "la proporzionalità del tratta- mento economico e normativo del lavoratore assunto a tempo parziale si determina sulla base del rapporto fra orario settimanale o mensile ridotto ed il corrispondente orario intero previsto dal presente contratto."),
            "parttime_anno": cit(T, "art. 99", "Per i lavoratori a tempo parziale, in caso di trasformazione del rap- porto nel corso dell’anno, l’importo della 13a e della 14a mensilità è determinato per dodicesimi, riproporzionando ciascuno di essi sulla base dei criteri previsti dal precedente art. 88."),
            "retribuzione": cit(T, "art. 212", "La retribuzione di fatto è costituita dalle voci di cui al precedente art. 210 nonché da tutti gli altri elementi retributivi aventi carattere continuativo"),
        },
        "quattordicesima": {
            "dove": "art. 225", "quando_breve": "il 1° luglio", "periodo_breve": "i 12 mesi prima del 1° luglio",
            "cit": {
                "quanto": cit(T, "art. 225", "Al personale compreso nella sfera di applicazione del presente con- tratto sarà corrisposto, il 1° luglio di ogni anno, un importo pari ad una mensilità della retribuzione di fatto di cui all’art. 212 in atto al 30 giugno immediatamente precedente (quattordicesima mensilità), esclusi gli assegni familiari."),
                "prorata": cit(T, "art. 225", "In caso di prestazione lavorativa ridotta, rispetto all’intero periodo di 12 mesi precedenti alla suddetta data, il lavoratore avrà diritto a tanti dodicesimi dell’ammontare della 14a mensilità quanti sono i mesi interi di servizio prestato"),
            }},
    },
}

# ------------------------------------------------------------------ metalmeccanici
M = "cnel_157071"
col_m = [("Livelli B2, B3 e A1", ["b2", "b3", "a1"]), ("Livelli C2, C3 e B1", ["c2", "c3", "b1"]), ("Livelli D1, D2 e C1", ["d1", "d2", "c1"])]


def riga_m(banda, pre, pezzi, mens):
    """pezzi: [(testo, mesi, giorni)], mens: [(testo, valore)] nelle tre colonne della tabella del contratto."""
    return {"banda": banda, "pre": pre, "frase": f(M, " ".join([pre] + [p[0] for p in pezzi])),
            "frase_mens": f(M, " ".join([pre] + [x[0] for x in mens])),
            "voci": [{"frase": p[0], "et": et, "livelli": liv, "mesi": p[1], "giorni": p[2], "unita": unita_di(p[0]), "frase_mens": x[0], "mens": x[1]}
                     for (et, liv), p, x in zip(col_m, pezzi, mens)]}


C["metalmeccanici"] = {
    "preavviso": {
        "fonte": M, "dove": "Sezione quarta, Titolo VIII, art. 1 del CCNL 5 febbraio 2021",
        "decorre_breve": "dal giorno dopo il ricevimento",
        "tabelle": [
            {"id": "tutti", "caso": "entrambi", "titolo": "Dimissioni e licenziamento (stessi termini)", "dove": "Sezione quarta, Titolo VIII, art. 1",
             "inizio": f(M, "Art. 1. - Preavviso di licenziamento e di dimissioni. Il rapporto"), "fine": f(M, "Art. 2. – Consegna dei documenti alla cessazionedel rapporto di lavoro. Entro"),
             "intestazione": f(M, "Anni di servizio Livelli B2, B3 e A1 Livelli C2, C3 e B1 Livelli D1, D2 e C1"),
             "bande": BANDE_5_10,
             "gruppi": [
                 riga_m("a", "Fino a 5 anni", [("2 mesi", 2, 0), ("1 mese e 15 giorni", 1, 15), ("10 giorni", 0, 10)],
                        [("2 mensilità", "2"), ("1,5 mensilità", "1.5"), ("0,33 mensilità", "0.33")]),
                 riga_m("b", "Oltre 5 fino a 10", [("3 mesi", 3, 0), ("2 mesi", 2, 0), ("20 giorni", 0, 20)],
                        [("3 mensilità", "3"), ("2 mensilità", "2"), ("0,67 mensilità", "0.67")]),
                 riga_m("c", "Oltre i 10 anni", [("4 mesi", 4, 0), ("2 mesi e 15 giorni", 2, 15), ("1 mese", 1, 0)],
                        [("4 mensilità", "4"), ("2,5 mensilità", "2.5"), ("1 mensilità", "1")]),
             ]},
        ],
        "cit": {
            "regola": cit(M, "Sezione quarta, Titolo VIII, art. 1", "Il rapporto di lavoro a tempo indeterminato non può essere risolto da nessuna delle due parti senza un preavviso i cui termini sono stabiliti come segue a seconda dell’anzianità e della categoria professionale cui appartiene il lavoratore."),
            "decorre": cit(M, "Sezione quarta, Titolo VIII, art. 1", "I termini di disdetta decorrono dal giorno del ricevimento dell’atto di dimis- sioni o di licenziamento e il periodo di preavviso si calcola dal giorno successivo."),
            "indennita": cit(M, "Sezione quarta, Titolo VIII, art. 1", "La parte che risolve il rapporto senza l’osservanza dei predetti termini di pre- avviso deve corrispondere all’altra un’indennità pari all’importo della retribuzione per il periodo di mancato preavviso come di seguito stabilito."),
            "permessi": cit(M, "Sezione quarta, Titolo VIII, art. 1", "Durante il compimento del periodo di preavviso in caso di licenziamento l’azienda concederà al lavoratore dei permessi per la ricerca di nuova occupazio- ne;"),
            "scritto": cit(M, "Sezione quarta, Titolo VIII, art. 1", "Tanto il licenziamento quanto le dimissioni saranno comunicate per iscritto."),
            "ferie": cit(M, "Sezione quarta, Titolo III, art. 10", "Il periodo di preavviso non può essere considerato periodo di ferie."),
            "infortunio": cit(M, "Sezione quarta, Titolo VI, art. 1", "L’infortunio sul lavoro sospende il decorso del preavviso nel caso di licen- ziamento, nei limiti ed agli effetti della normativa sulla conservazione del posto e sul trattamento economico di cui al presente articolo."),
        },
        "ratei": None,
        "esempio": {"tabella": "tutti", "livello": "c3", "banda": "a"},
    },
    "tredicesima": {
        "fonte": M, "dove": "Sezione quarta, Titolo IV, art. 7 del CCNL 5 febbraio 2021", "quando_breve": "di norma alla vigilia di Natale",
        "frazione_breve": "più di 15 giorni contano un mese",
        "cit": {
            "quanto": cit(M, "Sezione quarta, Titolo IV, art. 7", "L’azienda è tenuta a corrispondere per ciascun anno al lavoratore, in occasione della ricorrenza natalizia, una tredicesima mensilità di importo ragguagliato alla retribuzione globale di fatto."),
            "quando": cit(M, "Sezione quarta, Titolo IV, art. 7", "La corresponsione deve avvenire, normalmente, alla vigilia di Natale."),
            "prorata": cit(M, "Sezione quarta, Titolo IV, art. 7", "Nel caso di inizio o di cessazione del rapporto di lavoro durante il corso del- l’anno, il lavoratore ha diritto a tanti dodicesimi dell’ammontare della 13a men- silità quanti sono i mesi di anzianità di servizio presso l’azienda."),
            "frazioni": cit(M, "Sezione quarta, Titolo IV, art. 7", "La frazione di mese superiore a 15 giorni va considerata a questi effetti come mese intero."),
            "prova": cit(M, "Sezione quarta, Titolo IV, art. 7", "Il periodo di prova è utile per il calcolo dei dodicesimi di cui sopra."),
            "parttime": cit(M, "Sezione quarta, Titolo I, art. 4, lettera C", "Il lavoratore a tempo parziale beneficia dei mede- simi diritti di un lavoratore a tempo pieno comparabile e di un trattamento ripro- porzionato in ragione della ridotta entità della prestazione lavorativa."),
        },
        "quattordicesima": None,
    },
}

# ------------------------------------------------------------------ multiservizi
S = "cnel_105782"
imp_s = [("7° livello e Quadro", ["7", "q"]), ("6° livello", ["6"]), ("Dal 5° al 2° livello", ["5", "4", "3", "2"])]


def gruppo_s(banda, intest, voci):
    return {"banda": banda, "frase": f(S, intest), "voci": [voce(S, fr, et, liv, mesi=m, giorni=g) for (et, liv), (fr, m, g) in zip(imp_s, voci)]}


TUTTI_S = ["1", "2", "3", "4", "5"]  # 6° e 7° livello: funzioni di concetto e direttive (declaratoria)
C["multiservizi"] = {
    "preavviso": {
        "fonte": S, "dove": "art. 57 del CCNL 31 maggio 2011",
        "decorre_breve": "dalla metà o dalla fine del mese",
        "tabelle": [
            {"id": "lic_imp", "caso": "licenziamento", "chi": "impiegati", "titolo": "Impiegati: se ti licenzia l'azienda", "dove": "art. 57",
             "inizio": f(S, "Articolo 57 - PREAVVISO Il rapporto"), "fine": f(S, "Articolo 58 - CESSIONE, TRASFORMAZIONE, FALLIMENTO E CESSAZIONE"),
             "bande": BANDE_5_10,
             "gruppi": [
                 gruppo_s("a", "a) per gli impiegati che, avendo superato il periodo di prova, non hanno superato i 5 anni di servizio:",
                          [("1 – mesi 2 e 15 giorni per gli impiegati di 7° livello e Quadri;", 2, 15), ("2 – mesi 1 e 15 giorni per gli impiegati di 6° livello;", 1, 15),
                           ("3 – mesi 1 per gli impiegati dal 5° al 2° livello;", 1, 0)]),
                 gruppo_s("b", "b) per gli impiegati che hanno superato i 5 anni di servizio e non 10:",
                          [("1 – mesi 3 e 15 giorni per gli impiegati di 7° livello e Quadri;", 3, 15), ("2 – mesi 2 per gli impiegati di 6° livello;", 2, 0),
                           ("3 – mesi 1 e 15 giorni per gli impiegati dal 5° al 2° livello;", 1, 15)]),
                 gruppo_s("c", "c) per gli impiegati che hanno superato i 10 anni di servizio:",
                          [("1 – mesi 4 e 15 giorni per gli impiegati di 7° livello e Quadri;", 4, 15), ("2 – mesi 2 e 15 giorni per gli impiegati di 6° livello;", 2, 15),
                           ("3 – mesi 2 per gli impiegati dal 5° al 2° livello.", 2, 0)]),
             ]},
            {"id": "dim_imp", "caso": "dimissioni", "chi": "impiegati", "titolo": "Impiegati: se ti dimetti tu", "dove": "art. 57", "deriva": "lic_imp", "num": 1, "den": 2, "cit": "dimissioni"},
            {"id": "lic_ope", "caso": "licenziamento", "chi": "operai", "titolo": "Operai: se ti licenzia l'azienda", "dove": "art. 57",
             "inizio": f(S, "Articolo 57 - PREAVVISO Il rapporto"), "fine": f(S, "Articolo 58 - CESSIONE, TRASFORMAZIONE, FALLIMENTO E CESSAZIONE"),
             "bande": [{"id": "x", "et": "Qualsiasi anzianità"}],
             "gruppi": [{"banda": "x", "frase": f(S, "OPERAI Giorni 15 di calendario"),
                         "voci": [voce(S, "Giorni 15 di calendario per gli operai di qualsiasi livello, a prescindere dalla loro anzianità di servizio.", "Operai di qualsiasi livello", TUTTI_S, giorni=15)]}]},
            {"id": "dim_ope", "caso": "dimissioni", "chi": "operai", "titolo": "Operai: se ti dimetti tu", "dove": "art. 57",
             "inizio": f(S, "Articolo 57 - PREAVVISO Il rapporto"), "fine": f(S, "Articolo 58 - CESSIONE, TRASFORMAZIONE, FALLIMENTO E CESSAZIONE"),
             "bande": [{"id": "x", "et": "Qualsiasi anzianità"}],
             "gruppi": [{"banda": "x", "frase": f(S, "I termini di preavviso di cui al presente articolo sono ridotti"),
                         "voci": [voce(S, "a 7 giorni di calendario per gli operai qualora sia il lavoratore a dare il preavviso.", "Operai di qualsiasi livello", TUTTI_S, giorni=7)]}]},
        ],
        "cit": {
            "regola": cit(S, "art. 57", "Il rapporto di lavoro a tempo indeterminato non può essere risolto da nessuna delle due parti senza un preavviso, i cui termini sono stabiliti come segue:"),
            "operai": cit(S, "art. 57", "Giorni 15 di calendario per gli operai di qualsiasi livello, a prescindere dalla loro anzianità di servizio."),
            "dimissioni": cit(S, "art. 57", "I termini di preavviso di cui al presente articolo sono ridotti rispettivamente al 50% per gli impiegati e a 7 giorni di calendario per gli operai qualora sia il lavoratore a dare il preavviso."),
            "decorre": cit(S, "art. 57", "I termini della disdetta decorrono dalla metà e dalla fine di ciascun mese."),
            "indennita": cit(S, "art. 57", "La parte che risolve il rapporto senza osservanza dei predetti termini di preavviso, deve corrispondere all’altra un’indennità pari all’importo della retribuzione globale per il periodo di mancato preavviso."),
            "trattenuta": cit(S, "art. 57", "Il datore di lavoro ha diritto di ritenere, su quanto sia da lui dovuto al lavoratore un importo corrispondente alla retribuzione per il periodo di preavviso da questi eventualmente non dato."),
            "troncare": cit(S, "art. 57", "E' in facoltà della parte che riceve la disdetta ai sensi del comma 1 di troncare il rapporto, sia all’inizio sia nel corso del preavviso, senza che da ciò derivi alcun obbligo di indennizzo per il periodo di preavviso non compiuto."),
            "ferie": cit(S, "art. 42", "Il periodo di preavviso non può essere considerato periodo di ferie."),
            "giornaliera": cit(S, "art. 19", "La determinazione della retribuzione giornaliera si ottiene dividendo la retribuzione mensile per 22 nel caso di prestazione su 5 giorni settimanali e per 26 nel caso di prestazione su 6 giorni settimanali."),
        },
        "ratei": None,
        "esempio": {"tabella": "lic_ope", "livello": "2", "banda": "x"},
    },
    "tredicesima": {
        "fonte": S, "dove": "art. 20 del CCNL 31 maggio 2011", "quando_breve": "entro il 20 dicembre", "frazione_breve": "più di 15 giorni contano un mese",
        "cit": {
            "quanto": cit(S, "art. 20", "L’impresa corrisponderà una tredicesima mensilità pari alla retribuzione mensile globale percepita dal lavoratore entro il 20 dicembre."),
            "prorata": cit(S, "art. 20", "Nel caso di inizio o di cessazione del rapporto durante il corso dell’anno, il lavoratore non in prova avrà diritto a tanti dodicesimi dell’ammontare della tredicesima mensilità per quanti sono i mesi di servizio prestato presso l’azienda nel periodo di riferimento."),
            "frazioni": cit(S, "art. 20", "Le frazioni di mese non superiori ai 15 giorni non saranno calcolate, mentre saranno considerate come mese intero se superiori ai 15 giorni."),
            "parttime": cit("cnel_234754", "art. 33, nel testo dell'ipotesi di rinnovo del 13 giugno 2025", "Il trattamento economico e normativo del lavoratore assunto a tempo parziale si determina sulla base della regola di proporzionamento all'orario contrattualmente pattuito con riferimento al trattamento contrattuale dei lavoratori a tempo pieno.", altra_fonte=True),
        },
        "quattordicesima": {
            "dove": "art. 21 del CCNL 31 maggio 2011", "quando_breve": "entro il 15 luglio", "periodo_breve": "dal 1° luglio al 30 giugno",
            "cit": {
                "quanto": cit(S, "art. 21", "L’impresa corrisponderà entro il 15 luglio una 14° mensilità pari a una retribuzione globale mensile."),
                "periodo": cit(S, "art. 21", "Il periodo di riferimento è fissato dal 1° luglio al 30 giugno."),
                "prorata": cit(S, "art. 21", "Nel caso di inizio o di cessazione del rapporto durante il corso dell’anno, il lavoratore non in prova avrà diritto a tanti dodicesimi dell’ammontare della quattordicesima mensilità per quanti sono i mesi di servizio prestato presso l’azienda nel periodo di riferimento."),
            }},
    },
}

# ------------------------------------------------------------------ logistica
L = "cnel_223634"
imp_l = [("Quadro e 1° livello", ["q", "1"]), ("2° livello", ["2"]), ("Altri livelli", ["3s", "3", "4", "4j", "5", "6"])]
SPAN_L = {"inizio": f(L, "Art. 36 - Preavviso di licenziamento e di dimissioni 1. Il rapporto"), "fine": f(L, "Disposizione transitoria L’applicazione del presente articolo")}


def gruppo_l(banda, intest, voci):
    return {"banda": banda, "frase": f(L, intest), "voci": [voce(L, fr, et, liv, mesi=m, giorni=g) for (et, liv), (fr, m, g) in zip(imp_l, voci)]}


C["logistica"] = {
    "preavviso": {
        "fonte": L, "dove": "art. 36",
        "decorre_breve": "impiegati: dal 1° o dal 16 del mese; operai e viaggianti: da qualsiasi giorno",
        "tabelle": [
            dict({"id": "lic_imp", "caso": "licenziamento", "chi": "impiegati", "titolo": "Impiegati e quadri: se ti licenzia l'azienda", "dove": "art. 36, comma 1, lettere a, b, c",
                  "bande": BANDE_5_10,
                  "gruppi": [
                      gruppo_l("a", "a) Per gli impiegati che, avendo superato il periodo di prova, non hanno superato i cinque anni di servizio:",
                               [("- mesi due e quindici giorni per i quadri e gli impiegati del 1° livello;", 2, 15), ("- mesi uno e quindici giorni per gli impiegati del 2° livello;", 1, 15),
                                ("- mesi uno per gli impiegati degli altri livelli.", 1, 0)]),
                      gruppo_l("b", "b) Per gli impiegati che hanno superato i cinque anni di servizio e non dieci:",
                               [("- mesi tre e quindici giorni per i quadri e gli impiegati del 1° livello;", 3, 15), ("- mesi due per gli impiegati del 2° livello;", 2, 0),
                                ("- mesi uno e quindici giorni per gli impiegati degli altri livelli.", 1, 15)]),
                      gruppo_l("c", "c) Per gli impiegati che hanno superato i dieci anni di servizio:",
                               [("- mesi quattro e quindici giorni per i quadri e gli impiegati del 1° livello;", 4, 15), ("- mesi due e quindici giorni per gli impiegati del 2° livello;", 2, 15),
                                ("- mesi due per gli impiegati degli altri livelli.", 2, 0)]),
                  ]}, **SPAN_L),
            {"id": "dim_imp", "caso": "dimissioni", "chi": "impiegati", "titolo": "Impiegati e quadri: se ti dimetti tu", "dove": "art. 36, comma 1", "deriva": "lic_imp", "num": 1, "den": 2, "cit": "decorre"},
            dict({"id": "ope", "caso": "entrambi", "chi": "operai", "titolo": "Operai non viaggianti: dimissioni e licenziamento", "dove": "art. 36, comma 1, lettera d",
                  "bande": [{"id": "x", "et": "Qualsiasi anzianità"}],
                  "gruppi": [{"banda": "x", "frase": f(L, "d) Per gli operai non in prova,"),
                              "voci": [voce(L, "d) Per gli operai non in prova, sei giorni lavorativi, decorrenti da qualsiasi giorno della settimana.", "Operai non in prova",
                                            ["3s", "3", "4", "4j", "5", "6"], giorni=6, unita="lav")]}]}, **SPAN_L),
            dict({"id": "via", "caso": "entrambi", "chi": "viaggianti", "titolo": "Personale viaggiante: dimissioni e licenziamento", "dove": "art. 36, comma 1, lettera e",
                  "bande": [{"id": "x", "et": "Qualsiasi anzianità"}],
                  "gruppi": [{"banda": "x", "frase": f(L, "e) Per il personale viaggiante non in prova"),
                              "voci": [voce(L, "inquadrato alla qualifica 3 parametri A, B, C, venti giorni di calendario", "Qualifica 3, parametri A, B e C", ["c3", "b3", "a3"], giorni=20),
                                       voce(L, "inquadrato alla qualifica 2 parametri D, E, F quindici giorni di calendario", "Qualifica 2, parametri D, E e F", ["f2", "e2", "d2"], giorni=15)]}]}, **SPAN_L),
        ],
        "non_nominati": {"livelli": ["h1", "g1", "i_p110", "i_p116", "l_p110", "l_p116", "l_p119"]},
        "cit": {
            "regola": cit(L, "art. 36, comma 1", "Il rapporto di lavoro a tempo indeterminato, a meno che non si tratti di licenziamento per giusta causa, non può essere risolto da nessuna delle due parti senza un preavviso, i cui termini sono stabiliti come segue:"),
            "decorre": cit(L, "art. 36, comma 1", "Il periodo di preavviso decorre dal giorno 1 o dal giorno 16 di ciascun mese. Nel caso di dimissioni da parte dell'impiegato i termini di preavviso sono ridotti della metà."),
            "operai": cit(L, "art. 36, comma 1, lettera d", "d) Per gli operai non in prova, sei giorni lavorativi, decorrenti da qualsiasi giorno della settimana."),
            "viaggianti": cit(L, "art. 36, comma 1, lettera e", "e) Per il personale viaggiante non in prova inquadrato alla qualifica 3 parametri A, B, C, venti giorni di calendario decorrenti da qualsiasi giorno della settimana, e per il personale viaggiante non in prova inquadrato alla qualifica 2 parametri D, E, F quindici giorni di calendario decorrenti da qualsiasi giorno della settimana."),
            "indennita": cit(L, "art. 36, comma 2", "La parte che risolve il rapporto senza l'osservanza dei predetti termini di preavviso, deve corrispondere all'altra una indennità pari all'importo della retribuzione per il periodo di mancato preavviso."),
            "trattenuta": cit(L, "art. 36, comma 3", "Il datore di lavoro ha diritto di ritenere, su quanto sia da lui dovuto al lavoratore, un importo corrispondente alla retribuzione per il periodo di preavviso da questi eventualmente non prestato."),
            "troncare": cit(L, "art. 36, comma 5", "È in facoltà della parte che riceve la disdetta ai sensi del primo comma, di troncare il rapporto, sia all'inizio, sia nel corso del preavviso, senza che da ciò derivi alcun obbligo di indennizzo per il periodo di preavviso non compiuto."),
            "ferie": cit(L, "art. 24, comma 8", "L'assegnazione delle ferie non potrà aver luogo durante il periodo di preavviso, salvo richiesta scritta del lavoratore che sarà accolta compatibilmente con le esigenze organizzative aziendali."),
            "permessi": cit(L, "art. 36, comma 6", "Durante la decorrenza del preavviso il lavoratore ha diritto di ottenere permessi (retribuiti nel caso di licenziamento) in ragione di 2 ore giornaliere o di 12 ore settimanali per la ricerca di altra occupazione."),
            "giornaliera": cit(L, "art. 61, comma 3", "La retribuzione giornaliera del personale si ottiene dividendo la retribuzione mensile per 22. Per il personale non viaggiante, in caso di orario di lavoro settimanale distribuito su 6 giorni la retribuzione giornaliera si ottiene dividendo la retribuzione mensile per 26."),
            "ratei13": cit(L, "art. 18, comma 3", "La tredicesima mensilità va computata agli effetti del T.F.R. e della indennità sostitutiva di preavviso."),
            "ratei14": cit(L, "art. 19, comma 3", "La quattordicesima mensilità viene computata ai soli effetti del T.F.R. e dell'indennità sostitutiva del preavviso."),
        },
        "ratei": {"mensilita": 14, "cit": "ratei13"},
        "esempio": {"tabella": "via", "livello": "c3", "banda": "x"},
    },
    "tredicesima": {
        "fonte": L, "dove": "art. 18", "quando_breve": "di norma il 16 dicembre", "frazione_breve": "più di 15 giorni contano un mese",
        "cit": {
            "quanto": cit(L, "art. 18, comma 1", "L'azienda corrisponderà una tredicesima mensilità pari alla retribuzione globale mensile del lavoratore del mese di novembre, determinata in base alle voci previste dagli articoli 61 e 74 del presente CCNL."),
            "quando": cit(L, "art. 18, comma 1", "La corresponsione di tale mensilità avverrà normalmente il 16 dicembre."),
            "prorata": cit(L, "art. 18, comma 2", "Nel caso di inizio o di cessazione del rapporto durante il corso dell'anno, il lavoratore avrà diritto a tanti dodicesimi dell'ammontare della tredicesima mensilità per quanti sono i mesi di servizio prestato anche nel caso di cessazione del contratto a termine o di mancato superamento del periodo di prova."),
            "frazioni": cit(L, "art. 18, comma 2", "Le frazioni di mese non superiori ai 15 giorni non saranno calcolate mentre saranno considerate come mese intero se superiori a 15 giorni."),
            "parttime": cit(L, "art. 56, comma 19", "Il personale a tempo parziale è compensato in base alla retribuzione stabilita per il personale a tempo pieno, riproporzionata in funzione della ridotta durata della prestazione lavorativa."),
            "parttime_anno": cit(L, "art. 56, comma 22", "In caso di passaggio dal rapporto a tempo parziale al rapporto a tempo pieno e viceversa, nel relativo anno solare i ratei di retribuzione globale mensili relativi a tutti gli istituti contrattuali e legali sono calcolati in misura proporzionale all’effettiva durata della prestazione lavorativa nei due distinti periodi."),
        },
        "quattordicesima": {
            "dove": "art. 19", "quando_breve": "entro i primi dieci giorni di luglio", "periodo_breve": "dal 1° luglio al 30 giugno",
            "cit": {
                "quanto": cit(L, "art. 19, comma 1", "L'azienda corrisponderà una quattordicesima mensilità pari alla retribuzione globale mensile percepita dal lavoratore, determinata in base alle voci previste dagli articoli 61 e 74 del presente CCNL."),
                "periodo": cit(L, "art. 19, comma 2", "La corresponsione della suddetta quattordicesima mensilità avverrà entro la prima decade di luglio nella misura della retribuzione globale risultante in vigore al 30 giugno. La quattordicesima mensilità è riferita all'anno che precede la data di pagamento e quindi, precisamente, al periodo dall'1 luglio dell'anno precedente al 30 giugno dell'anno in corso."),
                "prorata": cit(L, "art. 19, comma 2", "Le frazioni di mese non superiori a 15 giorni non saranno calcolate, mentre saranno considerate come mese intero se superiori a 15 giorni."),
            }},
    },
}

# ------------------------------------------------------------------ lavoro domestico
Dm = "cnel_245143"
TUTTI_D = ["a", "as", "b", "bs", "c", "cs", "d", "ds"]
SPAN_D = {"inizio": f(Dm, "Art. 40 - Risoluzione del rapporto di lavoro e preavviso 1. Il rapporto"), "fine": f(Dm, "Art. 41 - Trattamento di fine rapporto (T.F.R.) 1.")}
C["domestico"] = {
    "preavviso": {
        "fonte": Dm, "dove": "art. 40",
        "decorre_breve": "il contratto non fissa un giorno del mese",
        "tabelle": [
            dict({"id": "lic25", "caso": "licenziamento", "chi": "25 ore o più a settimana", "titolo": "Rapporti di almeno 25 ore a settimana: se ti licenzia la famiglia", "dove": "art. 40, comma 1",
                  "bande": [{"id": "a", "et": "Fino a 5 anni con la stessa famiglia"}, {"id": "b", "et": "Oltre 5 anni"}],
                  "gruppi": [{"banda": "*", "frase": f(Dm, "per i rapporti non inferiori a 25 ore settimanali:"),
                              "voci": [voce(Dm, "- fino a 5 anni di anzianità presso lo stesso datore di lavoro: 15 giorni di calendario;", "Tutti i livelli", TUTTI_D, giorni=15, banda="a"),
                                       voce(Dm, "- oltre i 5 anni di anzianità presso lo stesso datore di lavoro: 30 giorni di calendario.", "Tutti i livelli", TUTTI_D, giorni=30, banda="b")]}]}, **SPAN_D),
            {"id": "dim25", "caso": "dimissioni", "chi": "25 ore o più a settimana", "titolo": "Rapporti di almeno 25 ore a settimana: se ti dimetti tu", "dove": "art. 40, comma 1", "deriva": "lic25", "num": 1, "den": 2, "cit": "dimissioni"},
            dict({"id": "meno25", "caso": "entrambi", "chi": "meno di 25 ore a settimana", "titolo": "Rapporti sotto le 25 ore a settimana", "dove": "art. 40, comma 1",
                  "bande": [{"id": "a", "et": "Fino a 2 anni con la stessa famiglia"}, {"id": "b", "et": "Oltre 2 anni"}],
                  "gruppi": [{"banda": "*", "frase": f(Dm, "Per i rapporti inferiori alle 25 ore settimanali:"),
                              "voci": [voce(Dm, "- fino a 2 anni di anzianità presso lo stesso datore di lavoro: 8 giorni di calendario;", "Tutti i livelli", TUTTI_D, giorni=8, banda="a"),
                                       voce(Dm, "- oltre i 2 anni di anzianità presso lo stesso datore di lavoro: 15 giorni di calendario.", "Tutti i livelli", TUTTI_D, giorni=15, banda="b")]}]}, **SPAN_D),
        ],
        "cit": {
            "regola": cit(Dm, "art. 40, comma 1", "Il rapporto di lavoro può essere risolto da ciascuna delle parti con l’osservanza dei seguenti termini di preavviso:"),
            "dimissioni": cit(Dm, "art. 40, comma 1", "I suddetti termini saranno ridotti del 50% nel caso di dimissioni da parte del lavoratore."),
            "maternita": cit(Dm, "art. 40, comma 2", "I termini di preavviso di cui al comma precedente saranno raddoppiati nell’eventualità in cui il datore di lavoro intimi il licenziamento prima del trentunesimo giorno successivo al termine del congedo per maternità."),
            "portieri": cit(Dm, "art. 40, comma 3", "Per i portieri privati, custodi di villa ed altri dipendenti che usufruiscono con la famiglia di alloggio indipendente di proprietà del datore di lavoro, e/o messo a disposizione dal medesimo, il preavviso è di: - 30 giorni di calendario, sino ad un anno di anzianità; - 60 giorni di calendario per anzianità superiore."),
            "indennita": cit(Dm, "art. 40, comma 4", "In caso di mancato o insufficiente preavviso, è dovuta dalla parte recedente un’indennità pari alla retribuzione corrispondente al periodo di preavviso non concesso."),
            "giusta_causa": cit(Dm, "art. 40, comma 6", "Al lavoratore che si dimette per giusta causa compete l’indennità di mancato preavviso."),
            "ferie": cit(Dm, "art. 17, comma 10", "Le ferie non possono essere godute durante il periodo di preavviso e di licenziamento, né durante il periodo di malattia o infortunio."),
            "malattia": cit(Dm, "art. 27, comma 10", "La malattia in periodo di prova o di preavviso sospende la decorrenza degli stessi."),
            "infortunio": cit(Dm, "art. 29, comma 8", "L’infortunio e la malattia professionale in periodo di prova o di preavviso sospendono la decorrenza degli stessi."),
            "trentesimi": cit(Dm, "chiarimenti a verbale, punto 2", "Quando nel contratto viene usata l’espressione “giorni di calendario” si considerano i trentesimi della mensilità (esempio: malattia)."),
            "globale": cit(Dm, "chiarimenti a verbale, punto 5", "Per “retribuzione globale di fatto” si intende quella comprensiva di tutte le indennità di cui alle tabelle allegate, ivi incluse le indennità di vitto e alloggio."),
            "ore": cit(Dm, "chiarimenti a verbale, punto 1", "paga oraria per numero di ore lavorate nella settimana per 52:12"),
        },
        "ratei": None,
        "esempio": {"tabella": "lic25", "livello": "cs", "banda": "a"},
    },
    "tredicesima": {
        "fonte": Dm, "dove": "art. 39", "quando_breve": "a Natale, comunque entro dicembre", "frazione_breve": "15 giorni o più contano un mese",
        "cit": {
            "quanto": cit(Dm, "art. 39, comma 1", "In occasione del Natale, e comunque entro il mese di dicembre, spetta al lavoratore una mensilità aggiuntiva, pari alla retribuzione globale di fatto, in essa compresa l’indennità sostitutiva di vitto e alloggio, così come chiarito nelle note a verbale apposte in calce al presente contratto."),
            "prorata": cit(Dm, "art. 39, comma 2", "Per coloro le cui prestazioni non raggiungano un anno di servizio, saranno corrisposti tanti dodicesimi di detta mensilità quanti sono i mesi del rapporto di lavoro."),
            "frazioni": cit(Dm, "chiarimenti a verbale, punto 4", "Le frazioni di anno si computano a mesi interi e le frazioni di mese, quando raggiungono o superano i 15 giorni di calendario, si computano a mese intero."),
            "assenze": cit(Dm, "art. 39, comma 3", "La tredicesima mensilità matura anche durante le assenze per malattia, infortunio sul lavoro, malattia professionale e maternità, nei limiti del periodo di conservazione del posto e per la parte non liquidata dagli enti preposti."),
            "globale": cit(Dm, "chiarimenti a verbale, punto 5", "Per “retribuzione globale di fatto” si intende quella comprensiva di tutte le indennità di cui alle tabelle allegate, ivi incluse le indennità di vitto e alloggio."),
            "ore": cit(Dm, "chiarimenti a verbale, punto 1", "paga oraria per numero di ore lavorate nella settimana per 52:12"),
        },
        "quattordicesima": None,
    },
}

# ------------------------------------------------------------------ procedura delle dimissioni: pagina del Ministero del Lavoro (letta il 27/11/2026)
import html as _html
_pag = (G / "min_dimissioni_2026.html").read_text(encoding="utf-8", errors="replace")
_pag = re.sub(r"<(script|style)\b.*?</\1>", " ", _pag, flags=re.S)
TESTI["min_dimissioni_2026"] = norm(_html.unescape(re.sub(r"<[^>]+>", " ", _pag)))
PROCEDURA = {
    "url": "https://www.lavoro.gov.it/strumenti-e-servizi/Dimissioni-volontarie/Pagine/default", "titolo": "Dimissioni volontarie",
    "chi": "Ministero del Lavoro e delle Politiche Sociali", "file": "min_dimissioni_2026.html", "letto_il": "2026-11-27",
    "frammenti": {
        "telematiche": f("min_dimissioni_2026", "a partire dal 12 marzo 2016 le dimissioni volontarie e la risoluzione consensuale del rapporto di lavoro dovranno essere effettuate in modalità esclusivamente telematiche"),
        "revoca": f("min_dimissioni_2026", "Il lavoratore ha sempre la possibilità di revocare le dimissioni o la risoluzione consensuale entro 7 giorni successivi alla comunicazione."),
        "esclusi": f("min_dimissioni_2026", "Restano fuori, dal campo di applicazione della presente norma, i rapporti di lavoro alle dipendenze delle pubbliche amministrazioni, il lavoro domestico,"),
        "spid": f("min_dimissioni_2026", "il nuovo modulo autonomamente tramite il sito del Ministero del Lavoro a cui è possibile accedere tramite SPID o CIE."),
        "abilitati": f("min_dimissioni_2026", "rivolgersi a un soggetto abilitato (patronato, organizzazione sindacale, ente bilaterale, commissioni di certificazione, consulenti del lavoro, sedi territoriali competenti dell'Ispettorato Nazionale del Lavoro)"),
    },
}

out = {
    "_nota": ("Pacchetto d'inverno del 27/11/2026 (studio-business/schede/2026-11-27-pagaccnl-inverno.md): preavviso e tredicesima per i 5 contratti. "
              "Ogni «frase» e ogni «testo» è copiato dal testo del contratto salvato in raccolta/_grezzi (apostrofi diritti, spazi singoli, a capo e "
              "trattini di sillabazione lasciati come nel file: «corrispon- dente»). mesi, giorni, unita e mens sono la lettura di quella frase (unita: cal = «di calendario», lav = «lavorativi», gg = il contratto non lo dice): verifica.py "
              "li rilegge dalla frase e ritrova ogni frase nel testo, nell'articolo e sotto l'intestazione indicati. Nessun giorno viene da siti terzi. "
              "Le cifre in euro non stanno qui: si calcolano dai minimi verificati (dati/contratti.json)."),
    "aggiornato_il": "2026-11-27",
    "letto_il": "2026-11-27",
    "procedura": PROCEDURA,
    "contratti": C,
}
(R / "dati" / "inverno.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("scritto", sum(len(json.dumps(x)) for x in C.values()), "caratteri")
