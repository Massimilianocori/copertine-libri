"""Quattro guide del 13/11/2026 (ricerca delle parole chiave: studio-business/intelaiatura/esameb1-parole-2026-11-13.md):

    /test-italiano-a2/            test di italiano A2 per il permesso UE di lungo periodo (domanda, prove, esito)
    /carta-di-soggiorno/          permesso UE per soggiornanti di lungo periodo (requisiti, documenti, costi, rinnovo)
    /cittadinanza-per-matrimonio/ cittadinanza per matrimonio (art. 5 legge 91/1992, B1, domanda, tempi)
    /pratica-cittadinanza/        stato della pratica (K10), decreto (SEND) e giuramento

Solo fatti letti nelle fonti ufficiali di dati/guide_cittadinanza.json (frasi controllate dal vivo con
raccolta/guide.py) e nei dati già controllati del sito (cittadinanza.json, ricongiungimento.json, prefetture_locali.json).
Le domande frequenti usano solo ricerche misurate (campo «ricerca» in FAQ, con il volume mensile in Italia del 13/11/2026).
Chiamato da main() di genera.py: genera(G) scrive le pagine e restituisce gli URL per la sitemap; controlli(G) ferma la
generazione se una cifra della pagina non è più nelle frasi citate.

Dal 14/11/2026 anche tre guide sul ricongiungimento familiare (tema n. 1 della stessa ricerca, 9.900 ricerche al mese):

    /ricongiungimento-familiare/            chi, per quali familiari, requisiti, domanda, nulla osta, visto, arrivo
    /ricongiungimento-familiare-documenti/  documenti (art. 6 DPR 394/1999, elenco della Prefettura di Firenze), modelli S1-S2-S3, idoneità alloggiativa
    /permesso-soggiorno-motivi-familiari/   permesso per motivi familiari (art. 30), coesione familiare, familiare di cittadino italiano

Stesse regole. Le frasi tra «» delle tre pagine sono prese con _q() dalle citazioni di guide_cittadinanza.json (quindi parola per parola,
ricontrollate da raccolta/guide.py); le ricerche delle domande frequenti sono in dati/parole_ricongiungimento.json (controllo in controlli()).

Dal 14/11/2026 (sera) anche /idoneita-alloggiativa/ (8.100 ricerche al mese): legge nazionale e pagine ufficiali dei Comuni di Roma, Torino,
Napoli, Bologna e Firenze (fonti ida_*); ricerche in dati/parole_idoneita.json. Stesse regole delle tre pagine sul ricongiungimento."""
import json
import re
from decimal import Decimal
from html import escape, unescape

GUIDE = None  # dati/guide_cittadinanza.json, letto in genera()

PAGINE = ["test-italiano-a2/", "carta-di-soggiorno/", "cittadinanza-per-matrimonio/", "pratica-cittadinanza/",
          "ricongiungimento-familiare/", "ricongiungimento-familiare-documenti/", "permesso-soggiorno-motivi-familiari/",
          "idoneita-alloggiativa/"]
RICERCHE = {}  # pagina → ricerche misurate delle sue domande frequenti (solo le tre pagine del 14/11/2026; controlli())

# Cifre scritte nelle pagine → frase della fonte che le contiene (controlli()): se una fonte cambia e raccolta/guide.py
# viene aggiornato, la generazione si ferma finché il testo della pagina non è allineato.
CIFRE = {
    "test-italiano-a2/": [("60 giorni", "entro 60 giorni"), ("80%", "ottanta per cento"), ("90 giorni", "dopo 90 giorni"),
                          ("25 minuti", "(durata 25 minuti)"), ("10 minuti", "(durata 10 minuti)"), ("14 anni", "14 anni")],
    "carta-di-soggiorno/": [("5 anni", "da almeno cinque anni"), ("10 anni", "valido per dieci anni"), ("90 giorni", "entro novanta giorni"),
                            ("16 €", "16 euro per la marca da bollo"), ("30,00 €", "30,00 euro all'operatore"), ("30,46 €", "30,46 euro per la produzione"),
                            ("100,00 €", "100.00 €"), ("130,46 €", "Un bollettino da 130.46€"),
                            ("12 mesi", "dodici mesi consecutivi"), ("6 anni", "superiore a sei anni"), ("6 mesi", "inferiori a sei mesi consecutivi"),
                            ("10 mesi", "dieci mesi nel quinquennio")],
    "cittadinanza-per-matrimonio/": [("2 anni", "almeno due anni"), ("3 anni", "dopo tre anni"), ("250 €", "euro 250,00"),
                                     ("24 mesi", "ventiquattro mesi"), ("36 mesi", "trentasei mesi"), ("48 mesi", "quarantotto mesi"),
                                     ("20 dicembre 2020", "20 dicembre 2020"), ("195", "n. 195"), ("132", "n. 132"),
                                     ("16 €", "marca da bollo da euro 16,00"), ("n. 74", "Legge 23 maggio 2025, n. 74")],
    "pratica-cittadinanza/": [("6 mesi", "entro sei mesi"), ("180 giorni", "180 giorni"), ("120 giorni", "120 giorni"),
                              ("10° giorno", "10° giorno"), ("90 giorni", "90 giorni"), ("258", "n. 258"), ("9.30", "9.30"), ("17.30", "17.30")],
    "reddito-ricongiungimento-familiare/": [("2 anni di soggiorno legale", "almeno due anni"), ("11 dicembre 2024", "11-12-2024")],  # frase aggiunta il 14/11/2026 in genera.py
    "ricongiungimento-familiare/": [("150 giorni", "centocinquanta giorni"), ("2 anni", "almeno due anni"), ("1 anno", "non inferiore a un anno"),
                                    ("18 anni", "non inferiore ai diciotto anni"), ("65 anni", "ultrasessantacinquenni"), ("14 anni", "inferiore agli anni quattordici"),
                                    ("6 mesi", "validità di 6 mesi"), ("365 giorni", "validità di 365 giorni"), ("8 giorni", "Entro 8 giorni"), ("48 ore", "Entro 48 ore"),
                                    ("30 giorni", "entro trenta giorni"), ("90 giorni", "entro novanta giorni"), ("16 €", "n. 1 marca da bollo da euro 16,00"),
                                    ("10 giorni", "termine perentorio di 10 giorni"), ("10.651,68 €", "10.651,68"), ("3.550,56 €", "pari a 3.550,56"),
                                    ("14.202,24 €", "(euro 14.202,24)"), ("11 dicembre 2024", "11-12-2024"), ("4 ottobre 2025", "4-10-2025")],
    "ricongiungimento-familiare-documenti/": [("16 €", "n. 1 marca da bollo da euro 16,00"), ("2 MB", "dimensioni massime di 2MB"), ("5 familiari", "pari a 5"),
                                              ("6 mesi", "non inferiore a sei mesi"), ("10 giorni", "termine perentorio di 10 giorni"), ("3 buste paga", "ultime tre buste paga"),
                                              ("1 mese", "non anteriore di mesi 1"), ("30 giorni", "non anteriore a trenta giorni"), ("14 anni", "minore di anni 14"),
                                              ("65 anni", "sopra i 65 anni"), ("48 ore", "entro 48 ore"), ("10.651,68 €", "10.651,68"), ("14.202,24 €", "(euro 14.202,24)"),
                                              ("17.752,80 €", "euro 17.752,80"), ("3.550,56 €", "pari a 3.550,56"), ("11524", "prot. n. 11524"),
                                              ("5 luglio 1975", "5 luglio 1975")],
    "permesso-soggiorno-motivi-familiari/": [("5 anni", "valido cinque anni"), ("1 anno", "da almeno un anno"), ("18 anni", "diciottesimo anno"),
                                             ("16,00 €", "marca da bollo 16.00 €"), ("30,46 €", "30.46 €"), ("40,00 €", "40.00 €"), ("50,00 €", "50.00 €"),
                                             ("30,00 €", "30.00 €"), ("22 luglio 2024", "22/07/2024"), ("4 novembre 2024", "04/11/2024"),
                                             ("11 agosto 2023", "11-8-2023")],
    "idoneita-alloggiativa/": [("14 m²", "mq 14"), ("10 m²", "mq 10"), ("28 m²", "mq 28"), ("38 m²", "mq 38"), ("5 luglio 1975", "5 luglio 1975"),
                               ("18 dicembre 2025", "18-12-2025"), ("18 luglio 1975", "18 luglio 1975"), ("16 €", "marca da bollo da 16 euro"), ("60,00 €", "€ 60,00"),
                               ("20,00 €", "€ 20.00"), ("10,00 €", "€ 10.00"), ("120 giorni", "Entro 120 giorni"), ("90 giorni", "entro 90 giorni"),
                               ("30 giorni", "Termine 30 giorni"), ("10 giorni", "ridotta a 10 gg"), ("2 giorni lavorativi", "entro due giorni lavorativi"),
                               ("6 mesi", "6 mesi dalla data di emissione"), ("1 anno", "validità di un anno"), ("6 luglio 2026", "aggiornato il 06/07/2026"),
                               ("14 anni", "inferiore agli anni quattordici")],
}


def _cit(fonte=None):
    return " ".join(c["testo"] for c in GUIDE["citazioni"] if fonte is None or c["fonte"] == fonte)


def _q(k, inizio):
    """Frase citata parola per parola: la citazione della fonte k (guide_cittadinanza.json) che comincia con «inizio», tra virgolette.
    Se la frase non c'è più tra le citazioni la generazione si ferma: il testo tra «» non si riscrive a mano."""
    trovate = [c["testo"] for c in GUIDE["citazioni"] if c["fonte"] == k and c["testo"].lower().startswith(inizio.lower())]
    if len(trovate) != 1:
        raise SystemExit(f"genera_guide: citazione di «{k}» che comincia con «{inizio}»: trovate {len(trovate)}")
    return "«" + escape(trovate[0]) + "»"


def _a(G, k, testo=None):
    f = GUIDE["fonti"][k]
    return f'<a href="{escape(f["url"])}" rel="noopener">{escape(testo or f["nome"])}</a>'


def _fonte(G, *chiavi, extra=""):
    v = G.data_breve(GUIDE["verificato_il"])
    link = " · ".join(_a(G, k) for k in chiavi) + extra
    return f'<div class="fonte">{G.ic("doc")}<span>{"Fonte" if len(chiavi) == 1 and not extra else "Fonti"}: {link} · {"letta" if len(chiavi) == 1 and not extra else "lette"} il {v}</span></div>'


def _dm2021(G):
    """Link al decreto 7 dicembre 2021 (fonte e frasi in dati/esoneri.json, controllate da raccolta/esempi.py)."""
    f = G.esoneri["fonti"]["dm2021"]
    return f' · <a href="{escape(f["url"])}" rel="noopener">{escape(f["nome"])}</a>'


def _faq(G, faq):
    """faq: (domanda, risposta, ricerca misurata). JSON-LD = testo visibile."""
    coppie = [(q, r) for q, r, _ in faq]
    return G.faq_html_e_jsonld(coppie)


def _scheda(G, icona, titolo, testo, *chiavi):
    return f'<div class="fatto"><div class="f-et">{G.ic(icona)}<span>{titolo}</span></div><p>{testo}</p>{_fonte(G, *chiavi)}</div>'


def _corpo_finale(G, rel, salta):
    return f"""<section>
<h2>{G.ic("info")}Altre guide</h2>
{G.link_guide(rel, salta=salta)}
</section>"""


# ---------------------------------------------------------------- /test-italiano-a2/
def pagina_test_a2(G):
    v = G.data_breve(GUIDE["verificato_il"])
    Fe = G.esoneri["fonti"]
    faq = [
        ("Come si prenota il test di italiano A2?",
         "Si fa la domanda online alla Prefettura della provincia dove abiti, sul Portale Servizi del Ministero dell'Interno (anche tramite un patronato). "
         "La Prefettura ti convoca entro 60 giorni e indica data e sede dell'esame. Secondo la Prefettura di Lecco la domanda del test va inviata prima della richiesta "
         "della carta di soggiorno o insieme.", "prenotazione test italiano a2"),
        ("Come si verifica il risultato del test di italiano?",
         "Secondo il Ministero dell'Interno il risultato si consulta sullo stesso sito dove hai fatto la domanda. Non c'è un attestato su carta: "
         "se lo superi, la Prefettura lo comunica in via telematica alla Questura. La Prefettura di Lecco aggiunge che il risultato può essere pubblicato anche sul sito del CPIA.",
         "verifica test di italiano"),
        ("C'è un esempio del test di italiano A2 per la carta di soggiorno?",
         "Nelle pagine ufficiali che abbiamo letto (Ministero dell'Interno e Prefettura di Lecco) non c'è un fac-simile da scaricare. La Prefettura di Lecco descrive le prove: "
         "ascolto di due testi brevi (25 minuti), lettura di due testi brevi (25 minuti), con domande a scelta multipla o vero/falso, e un breve testo da scrivere (10 minuti).",
         "test italiano a2 per carta di soggiorno esempio"),
        ("Il test di italiano A2 si può fare online?",
         "Online si fa solo la domanda. Il test si svolge nella sede indicata nella convocazione: per esempio, a Lecco, nei Centri per l'istruzione degli adulti (CPIA). "
         "Il decreto del Ministro dell'Interno del 7 dicembre 2021 (art. 3) prevede il test con modalità informatiche e, a richiesta dell'interessato, su carta.", "test italiano a2 online gratis"),
    ]
    jsonld, faq_html = _faq(G, faq)
    prove = [("Comprensione orale", "ascolto di due testi brevi, poi domande a scelta multipla o vero/falso", 25),
             ("Comprensione scritta", "lettura di due testi brevi, poi domande a scelta multipla o vero/falso", 25),
             ("Interazione scritta", "un breve testo su un argomento indicato (per esempio: dove sei, cosa stai facendo)", 10)]
    tab = ('<div class="tab-wrap ris-tab"><table class="conf"><thead><tr><th scope="col">Prova</th><th scope="col">Cosa fai</th><th scope="col">Tempo</th></tr></thead><tbody>'
           + "".join(f'<tr><td><strong>{p}</strong></td><td data-l="Cosa fai">{escape(c)}</td><td data-l="Tempo">{m} minuti</td></tr>' for p, c, m in prove)
           + f'<tr><td><strong>In tutto</strong></td><td data-l="Cosa fai">somma dei tempi scritti dalla Prefettura di Lecco</td><td data-l="Tempo">{sum(m for *_, m in prove)} minuti</td></tr>'
           + "</tbody></table></div>")
    corpo = f"""<section class="hero">
{G.briciole(("EsameB1", "../"), ("Test di italiano A2", None))}
<span class="occhiello">{G.ic("scudo")}Ministero dell'Interno e Prefettura · lette il {v}</span>
<h1>Test di italiano A2 per la carta di soggiorno: domanda, prove e risultato</h1>
<p class="lead">Secondo il Ministero dell'Interno (pagina «Test di conoscenza della lingua italiana», letta il {v}), chi chiede il permesso di soggiorno UE per soggiornanti di lungo periodo
deve superare un test di italiano: la domanda si invia online alla Prefettura, che convoca entro 60 giorni; il risultato si consulta sullo stesso sito. Per il decreto del 7 dicembre 2021 il test si supera con almeno l'80% del punteggio.</p>
<div class="risposta">
<div class="slot"><div class="r-et">{G.ic("cal")}Convocazione</div><div class="r-data">60 giorni <small>al massimo</small></div><div class="r-cosa">dalla domanda online alla Prefettura</div></div>
<div class="slot"><div class="r-et">{G.ic("ok")}Per superarlo</div><div class="r-data">80% <small>del punteggio</small></div><div class="r-cosa">livello A2 · se non lo superi, nuova domanda dopo 90 giorni</div></div>
<div class="r-piede"><a href="#esito">Come vedere il risultato {G.ic("freccia")}</a><span>{G.ic("doc")}Fonti: Ministero dell'Interno, decreto 7 dicembre 2021, Prefettura di Lecco</span></div>
</div>
</section>
{G.avviso("Questa pagina riassume le fonti ufficiali. <strong>Decidono la Prefettura</strong> (test) <strong>e la Questura</strong> (permesso): per il tuo caso chiedi a loro o a un patronato. Questo sito non è del Ministero.")}
<div class="due">
<section>
<h2 id="chi">{G.ic("lista")}Chi deve fare il test</h2>
<p>Lo chiede l'art. 9 del Testo unico immigrazione per il <a href="../carta-di-soggiorno/">permesso UE per soggiornanti di lungo periodo</a> (la «carta di soggiorno»).
La Prefettura di Lecco scrive che lo fa chi è in Italia regolarmente da almeno cinque anni, ha un permesso di soggiorno valido e ha compiuto 14 anni.
Il Testo unico non lo chiede a chi ha la protezione internazionale.</p>
{_fonte(G, "tu9", "lecco")}
<p><strong>Non fai il test</strong> se hai già un certificato di italiano almeno A2 di un ente riconosciuto (vale anche il <a href="../#date">B1 per la cittadinanza</a>),
un diploma di scuola media o superiore italiana, un titolo A2 di un corso al CPIA, o gravi limitazioni certificate da una struttura sanitaria pubblica.
Sono esclusi anche i figli sotto i 14 anni. <a href="../esonero-test-italiano/#carta-di-soggiorno">Tutti i casi di esonero, con le fonti</a>.</p>
</section>
<aside>{G.modulo().replace("Avvisami quando ci sono nuove date", "Ti serve anche il B1? Avvisami per le date").replace("Gratis. Ti scriviamo", "Questo avviso riguarda l'esame B1 per la cittadinanza, non il test A2: la data del test A2 te la comunica la Prefettura. Gratis. Ti scriviamo")}</aside>
</div>
<section>
<h2 id="domanda">{G.ic("web")}Come si prenota, passo per passo</h2>
<ol class="passi">
<li><div><strong>Domanda online alla Prefettura</strong> della provincia dove abiti, sul {_a(G, "portale", "Portale Servizi del Ministero dell'Interno")}.
<p>La Prefettura di Lecco precisa che si può fare anche tramite i patronati e le associazioni abilitati, e che la domanda del test va inviata prima della richiesta della carta di soggiorno oppure insieme.
La sua pagina (del 31 maggio 2024) indica un altro indirizzo del sistema del Ministero (nullaostalavoro.dlci.interno.it): segui quello della convocazione e della tua Prefettura.</p></div></li>
<li><div><strong>Convocazione entro 60 giorni</strong>, online, con data e sede dell'esame.</div></li>
<li><div><strong>Il giorno del test</strong> porti la lettera di convocazione, il permesso di soggiorno e un documento di riconoscimento.
<p>Secondo la Prefettura di Lecco bisogna arrivare puntuali e venire da soli: figli e accompagnatori non sono ammessi.</p></div></li>
<li><div><strong>Risultato</strong>: si consulta online; se lo superi, la Prefettura lo comunica alla Questura, che rilascia il permesso se ci sono gli altri requisiti.</div></li>
</ol>
{_fonte(G, "minint_test", "lecco")}
</section>
<section>
<h2 id="prove">{G.ic("matita")}Com'è fatto il test</h2>
<p>Il livello è l'A2: capire frasi ed espressioni di uso frequente. La Prefettura di Lecco descrive tre prove, che tutti i candidati fanno nello stesso momento, nei CPIA della provincia, con una commissione
presieduta dal dirigente della scuola. Per superarlo serve almeno l'ottanta per cento del punteggio complessivo (lo scrive anche l'art. 3 del decreto del 7 dicembre 2021).</p>
{tab}
{_fonte(G, "lecco", extra=_dm2021(G))}
<p><strong>Un esempio ufficiale da scaricare?</strong> Nelle pagine del Ministero e della Prefettura di Lecco che abbiamo letto non c'è. Per allenarti ad ascoltare e leggere puoi usare le
<a href="../esempi/">prove d'esempio ufficiali degli enti certificatori</a>: sono di livello B1, quindi più difficili dell'A2, e per ogni prova trovi i tempi.
Gli enti pubblicano anche esempi dei loro esami di livello A2, che sono un esame diverso dal test in Prefettura: <a href="../esempi/a2/">prove d'esempio A2 con PDF e audio</a>.</p>
</section>
<section>
<h2 id="esito">{G.ic("ok")}Il risultato: dove verificarlo</h2>
<ul>
<li>Il Ministero scrive che il risultato si consulta <strong>sullo stesso sito</strong> della domanda.</li>
<li>Non viene rilasciato <strong>nessun attestato</strong>: la Questura vede l'esito direttamente nel sistema (Prefettura di Lecco).</li>
<li>La Prefettura di Lecco aggiunge che il risultato può comparire anche sul sito del CPIA, nella sezione notizie.</li>
</ul>
{_fonte(G, "minint_test", "lecco")}
</section>
<section>
<h2 id="non-superato">{G.ic("attenzione")}Se non lo superi o non ti presenti</h2>
<p>Puoi chiedere di ripetere il test con la stessa procedura, ma <strong>solo dopo 90 giorni</strong> dalla data del test precedente. La Prefettura di Lecco applica gli stessi 90 giorni a chi
non si presenta senza giustificazione: l'unica giustificazione sono i motivi di salute, con il certificato del medico, da consegnare il giorno del test.
Se avevi già chiesto la carta di soggiorno, la domanda viene rifiutata, ma tieni il permesso di soggiorno che hai.</p>
<p class="small">I 90 giorni sono scritti nella pagina del Ministero e in quella della Prefettura di Lecco. Il decreto del 7 dicembre 2021 (art. 3), che ha sostituito quello del 4 giugno 2010 citato dal Ministero,
dice solo che in caso di esito negativo si può ripetere la prova con una nuova richiesta, senza indicare un numero di giorni: chiedi alla tua Prefettura quando puoi ripresentare la domanda.</p>
{_fonte(G, "minint_test", "lecco", extra=_dm2021(G))}
</section>
<section>
<h2 id="domande">{G.ic("info")}Domande frequenti</h2>
{faq_html}
</section>
{_corpo_finale(G, "../", None)}"""
    G.pagina("test-italiano-a2/index.html",
             G.titolo_pagina("Test di italiano A2 per la carta di soggiorno: domanda ed esito"),
             G.descrizione_pagina("Test di italiano A2 per la carta di soggiorno: come si prenota in Prefettura, com'è fatto, 80% per superarlo, "
                                  "dove verificare il risultato."), corpo, jsonld)


# ---------------------------------------------------------------- /carta-di-soggiorno/
def pagina_carta(G):
    v = G.data_breve(GUIDE["verificato_il"])
    A = G.RICONG["assegno_sociale"]
    anno = G.RICONG["anno"]
    annuo = G.cent(A["annuo"])
    meta = annuo // 2
    faq = [
        ("Quali sono i requisiti per la carta di soggiorno?",
         f"Secondo l'art. 9 del Testo unico immigrazione: un permesso di soggiorno valido da almeno 5 anni, un reddito non inferiore all'assegno sociale "
         f"({G.euro_c(annuo)} l'anno nel {anno}; con i familiari, di più), il test di italiano A2, salvo esonero, e un alloggio idoneo (il Portale Immigrazione chiede il certificato di idoneità alloggiativa nelle domande con i figli minori). "
         "Non si può chiedere, per esempio, con un permesso per studio, per protezione temporanea o di breve durata. Decide la Questura.",
         "carta di soggiorno requisiti"),
        ("Quali documenti servono per la carta di soggiorno?",
         "Secondo il Portale Immigrazione (codice 09): i moduli 1 e 2 del kit compilati e firmati, la fotocopia di tutto il passaporto, la dichiarazione dei redditi o il CUD "
         "dell'anno precedente, il certificato del casellario giudiziario e quello dei procedimenti penali in corso. Per i figli minori servono anche la certificazione anagrafica "
         "e il certificato di idoneità alloggiativa.", "documenti carta soggiorno"),
        ("Come si rinnova la carta di soggiorno?",
         "Il permesso UE per soggiornanti di lungo periodo vale 10 anni (5 per i minorenni) e, secondo l'art. 9 del Testo unico, alla scadenza si rinnova automaticamente "
         "presentando la domanda con nuove fotografie. Il rinnovo e l'aggiornamento si chiedono anche negli uffici postali Sportello Amico.",
         "rinnovo carta di soggiorno"),
        ("Cos'è il permesso di soggiorno UE per soggiornanti di lungo periodo?",
         "È il titolo di soggiorno che ha preso il posto della vecchia «carta di soggiorno»: attesta uno status permanente, vale 10 anni (5 per i minorenni) "
         "e, finché è in corso di validità, è anche un documento di identificazione personale. Si chiede al questore del luogo di residenza, per sé e per i familiari.",
         "permesso di soggiorno ue per soggiornanti di lungo periodo"),
    ]
    jsonld, faq_html = _faq(G, faq)
    tab = ('<div class="tab-wrap ris-tab"><table class="conf"><thead><tr><th scope="col">Domanda per</th><th scope="col">Reddito minimo annuo ' + str(anno) + '</th></tr></thead><tbody>'
           + "".join(f'<tr><td><strong>{t}</strong></td><td data-l="Reddito {anno}">{G.euro_c(annuo + meta * n)}</td></tr>'
                     for n, t in ((0, "Solo te"), (1, "Te e 1 familiare"), (2, "Te e 2 familiari"), (3, "Te e 3 familiari")))
           + "</tbody></table></div>")
    corpo = f"""<section class="hero">
{G.briciole(("EsameB1", "../"), ("Carta di soggiorno", None))}
<span class="occhiello">{G.ic("doc")}Legge, Portale Immigrazione e Poste · letti il {v}</span>
<h1>Permesso di soggiorno UE di lungo periodo (carta di soggiorno): requisiti, documenti, costi</h1>
<p class="lead">Secondo l'art. 9 del Testo unico immigrazione (testo in vigore letto su Normattiva il {v}), chiede al questore il permesso UE per soggiornanti di lungo periodo chi ha
da almeno 5 anni un permesso di soggiorno valido e un reddito non inferiore all'assegno sociale ({G.euro_c(annuo)} l'anno nel {anno}); serve anche il test di italiano A2.
Il permesso vale 10 anni (5 per i minorenni) e alla scadenza si rinnova con nuove fotografie.</p>
<div class="risposta">
<div class="slot"><div class="r-et">{G.ic("orologio")}Permesso valido da</div><div class="r-data">5 anni <small>almeno</small></div><div class="r-cosa">con un permesso che si può rinnovare senza limiti</div></div>
<div class="slot"><div class="r-et">{G.ic("euro")}Reddito {anno}</div><div class="r-data">{G.euro_c(annuo)} <small>l'anno</small></div><div class="r-cosa">solo per te · + {G.euro_c(meta)} per ogni familiare</div></div>
<div class="r-piede"><a href="#documenti">Documenti e costi {G.ic("freccia")}</a><span>{G.ic("doc")}Fonti: Testo unico, INPS, Portale Immigrazione, Poste</span></div>
</div>
</section>
{G.avviso("Questa pagina riassume le fonti ufficiali, ma <strong>decide la Questura</strong>. Questo sito non dà consulenza: per il tuo caso chiedi alla Questura o a un patronato.")}
<section>
<h2 id="requisiti">{G.ic("lista")}I requisiti</h2>
<div class="fatti">
{_scheda(G, "orologio", "Almeno 5 anni con un permesso valido", "Il Portale Immigrazione precisa: un permesso per un motivo che si può rinnovare senza limiti (famiglia, lavoro subordinato a tempo indeterminato, lavoro autonomo, asilo, motivi religiosi, apolidia). Le assenze dall'Italia non interrompono i 5 anni se sono inferiori a 6 mesi consecutivi e in tutto non più di 10 mesi, salvo gravi motivi documentati.", "tu9", "portale_imm")}
{_scheda(G, "euro", "Reddito almeno pari all'assegno sociale", f"Nel {anno} l'assegno sociale è {G.euro_c(annuo)} l'anno. Se chiedi il permesso anche per i familiari vale la regola del ricongiungimento: + {G.euro_c(meta)} per ognuno. <a href=\"../reddito-minimo-cittadinanza/#carta-di-soggiorno\">Calcolatore e dettagli</a>.", "tu9")}
{_scheda(G, "edificio", "Un alloggio idoneo", "Un alloggio nei parametri della legge regionale per l'edilizia residenziale pubblica, oppure con l'idoneità igienico-sanitaria accertata dall'ASL. Il Portale Immigrazione chiede la fotocopia del certificato di idoneità alloggiativa nelle domande con i figli minori. Ai titolari di protezione internazionale la documentazione sull'alloggio non è richiesta. Nel testo dell'art. 9 l'alloggio è scritto insieme al reddito per i familiari: se chiedi il permesso solo per te, chiedi alla Questura se vuole questo documento. <a href=\"../idoneita-alloggiativa/\">Idoneità alloggiativa: come si chiede al Comune</a>.", "tu9", "portale_imm")}
{_scheda(G, "voce", "Il test di italiano A2", "Il rilascio dipende dal superamento di un test di italiano, salvo esonero (per esempio con un certificato A2 o B1 di un ente riconosciuto). <a href=\"../test-italiano-a2/\">Come funziona il test A2</a>.", "tu9")}
</div>
<p><strong>Chi non può chiederlo</strong> (art. 9, comma 3), tra gli altri: chi è in Italia per studio o formazione professionale, per protezione temporanea o cure mediche, chi aspetta la decisione sulla protezione internazionale,
chi ha un permesso di breve durata. Non si rilascia a chi è pericoloso per l'ordine pubblico o la sicurezza dello Stato.</p>
{_fonte(G, "tu9")}
<h3 id="reddito">Reddito minimo {anno}</h3>
{tab}
<p class="small">Importi annui: assegno sociale {anno} ({escape(A["fonte"].split("«")[0].strip().rstrip(","))}) più la metà per ogni familiare. L'art. 9 rinvia ai parametri del ricongiungimento (art. 29, comma 3, lettera b),
che per due o più figli sotto i 14 anni chiede «in ogni caso» un reddito non inferiore al doppio dell'assegno sociale ({G.euro_c(annuo * 2)}): come si applica al tuo caso lo conferma la Questura. <a href="../reddito-ricongiungimento-familiare/">Tabella del ricongiungimento</a>.</p>
</section>
<section>
<h2 id="documenti">{G.ic("doc")}Documenti da allegare</h2>
<p>Secondo il Portale Immigrazione (codice 09, il motivo da scegliere nel kit), per te:</p>
<ul>
<li>i <strong>moduli 1 e 2</strong> del kit, compilati e firmati;</li>
<li>fotocopia di <strong>tutto il passaporto</strong> o di un documento equivalente;</li>
<li>fotocopia della <strong>dichiarazione dei redditi o del CUD</strong> dell'anno precedente (per chi non deve fare la dichiarazione, per esempio i collaboratori domestici, buste paga o contributi INPS);</li>
<li><strong>certificato del casellario giudiziario</strong> e certificato dei procedimenti penali in corso.</li>
</ul>
<p>Per i <strong>figli minori</strong>: la certificazione anagrafica che dice che sono tuoi figli (se viene dall'estero: tradotta, legalizzata e validata dal consolato italiano, salvo accordi;
non serve se il figlio è entrato con il visto per ricongiungimento) e il certificato di idoneità alloggiativa. Il coniuge e i figli sopra i 14 anni compilano un proprio modulo 1.
Alla domanda aggiungi il certificato di italiano o il documento dell'esonero, se non fai il test.</p>
{_fonte(G, "portale_imm")}
</section>
<section>
<h2 id="domanda">{G.ic("web")}Dove si presenta e quanto costa</h2>
<ol class="passi">
<li><div><strong>Kit a banda gialla</strong> degli uffici postali, da compilare da solo o con l'aiuto gratuito dei Comuni e dei patronati abilitati.</div></li>
<li><div><strong>Consegna all'ufficio postale Sportello Amico</strong>, in busta aperta, con le fotocopie dei documenti e la ricevuta del bollettino.</div></li>
<li><div><strong>Ricevuta e lettera di convocazione in Questura</strong>: alla data indicata ti presenti in Questura. Secondo l'art. 9 del Testo unico il permesso è rilasciato entro 90 giorni dalla richiesta.</div></li>
</ol>
<div class="tab-wrap ris-tab"><table class="conf"><thead><tr><th scope="col">Costo</th><th scope="col">Importo</th></tr></thead><tbody>
<tr><td><strong>Marca da bollo</strong></td><td data-l="Importo">16 €</td></tr>
<tr><td><strong>All'operatore dell'ufficio postale</strong></td><td data-l="Importo">30,00 €</td></tr>
<tr><td><strong>Produzione del permesso elettronico</strong> (bollettino)</td><td data-l="Importo">30,46 €</td></tr>
<tr><td><strong>Contributo per il permesso UE di lungo periodo</strong> (stesso bollettino)</td><td data-l="Importo">100,00 €</td></tr>
<tr><td><strong>In tutto</strong> (somma nostra, per un adulto)</td><td data-l="Importo">176,46 €</td></tr>
</tbody></table></div>
<p class="small">Poste Italiane scrive che al bollettino si aggiunge «l'eventuale contributo ove dovuto». La tabella dei costi del Portale Immigrazione indica per il permesso UE per soggiornanti di lungo periodo
un contributo di 100,00 € e un solo bollettino da 130,46 € (30,46 + 100,00); per i minori di 18 anni il contributo è «non previsto» (bollettino da 30,46 €). Prima di pagare controlla l'importo all'ufficio postale.</p>
{_fonte(G, "poste", "portale_costi", "tu9")}
</section>
<section>
<h2 id="rinnovo">{G.ic("orologio")}Quanto dura, rinnovo e quando si perde</h2>
<p>Il permesso attesta uno <strong>status permanente</strong> e vale <strong>10 anni</strong> (5 per chi ha meno di 18 anni). Alla scadenza si rinnova automaticamente presentando la domanda con nuove fotografie.
L'art. 9, comma 2, dice che il permesso «in corso di validità» è anche un documento di identificazione personale: quindi per tutta la durata scritta sul permesso (10 anni, 5 per i minorenni).
Il Portale Immigrazione scrive ancora che vale come documento di identificazione «per non oltre cinque anni dalla data del rilascio o del rinnovo»: le due fonti non coincidono, e il testo di legge in vigore è quello dell'art. 9.
Guarda la data di scadenza scritta sul tuo permesso; se ti serve come documento di identificazione e hai un dubbio, chiedi alla Questura.</p>
<p>Si perde, tra l'altro, dopo <strong>12 mesi</strong> consecutivi fuori dall'Unione europea o dopo più di <strong>6 anni</strong> fuori dall'Italia.</p>
{_fonte(G, "tu9", "portale_imm")}
</section>
<section>
<h2 id="cittadinanza">{G.ic("scudo")}Carta di soggiorno e cittadinanza</h2>
<p>Chi ha il permesso UE per soggiornanti di lungo periodo non deve presentare il certificato B1 quando chiede la cittadinanza (art. 9.1 della legge 91/1992):
<a href="../esonero-test-italiano/#cittadinanza">chi è esonerato dal B1</a> · <a href="../cittadinanza/">come si fa la domanda di cittadinanza</a> · <a href="../reddito-minimo-cittadinanza/">reddito minimo per la cittadinanza</a>.</p>
</section>
<section>
<h2 id="domande">{G.ic("info")}Domande frequenti</h2>
{faq_html}
</section>
{_corpo_finale(G, "../", None)}"""
    G.pagina("carta-di-soggiorno/index.html",
             G.titolo_pagina(f"Carta di soggiorno {anno}: requisiti, documenti e costi", "Carta di soggiorno: requisiti, documenti e costi"),
             G.descrizione_pagina(f"Permesso UE di lungo periodo: 5 anni di permesso, reddito {G.euro_c(annuo)} nel {anno}, test A2, documenti del kit, "
                                  "costi alla posta, rinnovo."), corpo, jsonld)


# ---------------------------------------------------------------- /cittadinanza-per-matrimonio/
def pagina_matrimonio(G):
    v = G.data_breve(GUIDE["verificato_il"])
    contributo = G.CITT["contributo_eur"]
    faq = [
        ("Quali sono i requisiti per la cittadinanza italiana per matrimonio?",
         "Secondo l'art. 5 della legge 91/1992: 2 anni di residenza legale in Italia dopo il matrimonio, oppure 3 anni dalla data del matrimonio se vivete all'estero, "
         "ridotti della metà se avete figli nati o adottati. Il matrimonio deve durare fino al decreto: niente scioglimento, annullamento o separazione personale. "
         "Serve anche la conoscenza dell'italiano almeno B1, salvo esonero.", "requisiti cittadinanza italiana per matrimonio"),
        ("La cittadinanza italiana per matrimonio è automatica?",
         "No. La legge dice che il coniuge straniero «può acquistare» la cittadinanza: si presenta una domanda e decide il prefetto della provincia di residenza "
         "(il Dipartimento per le libertà civili e l'immigrazione se il coniuge vive all'estero), con un decreto.", "cittadinanza italiana per matrimonio automatica"),
        ("Quali documenti servono per la cittadinanza per matrimonio?",
         f"La pagina del Ministero dell'Interno elenca: documento di riconoscimento, atto di nascita e certificato penale del Paese di origine, certificato di italiano almeno B1 "
         f"(salvo esoneri), ricevuta del contributo di {contributo} € ed estremi della marca da bollo telematica (16 € secondo la Prefettura di Catania). Altri documenti li può chiedere la tua Prefettura.",
         "documenti per cittadinanza italiana per matrimonio"),
        ("La richiesta di cittadinanza per matrimonio si fa online?",
         "Sì: sul portale del Ministero dell'Interno, con SPID o CIE se vivi in Italia; chi vive all'estero entra nello stesso portale con le proprie credenziali.",
         "richiesta cittadinanza italiana per matrimonio online"),
        ("Quali sono le nuove regole per la cittadinanza italiana per matrimonio?",
         "Nelle fonti che abbiamo letto: dal 2018 (legge 1° dicembre 2018 n. 132) serve il certificato di italiano; per le domande dal 20 dicembre 2020 il termine è di 24 mesi, "
         "prorogabili fino a 36 (prima erano 48); dal 2022 (sentenza n. 195 della Corte costituzionale) la morte del coniuge durante il procedimento non impedisce più la cittadinanza. "
         "Il testo dell'art. 5 in vigore su Normattiva non riporta modifiche del decreto-legge 28 marzo 2025 n. 36 (legge 23 maggio 2025 n. 74).",
         "nuove regole cittadinanza italiana per matrimonio"),
    ]
    jsonld, faq_html = _faq(G, faq)
    corpo = f"""<section class="hero">
{G.briciole(("EsameB1", "../"), ("Cittadinanza per matrimonio", None))}
<span class="occhiello">{G.ic("scudo")}Legge 91/1992 e Ministero dell'Interno · letti il {v}</span>
<h1>Cittadinanza italiana per matrimonio: requisiti, esame B1 e domanda</h1>
<p class="lead">Secondo l'art. 5 della legge 91/1992 (testo in vigore letto su Normattiva il {v}), il coniuge straniero di un cittadino italiano può chiedere la cittadinanza dopo 2 anni di residenza legale
in Italia dal matrimonio, oppure dopo 3 anni dal matrimonio se vive all'estero; i tempi si dimezzano se la coppia ha figli nati o adottati. Serve il certificato di italiano almeno B1.</p>
<div class="risposta">
<div class="slot"><div class="r-et">{G.ic("pin")}Se vivete in Italia</div><div class="r-data">2 anni <small>di residenza legale</small></div><div class="r-cosa">dopo il matrimonio · 1 anno con figli</div></div>
<div class="slot"><div class="r-et">{G.ic("web")}Se vivete all'estero</div><div class="r-data">3 anni <small>dal matrimonio</small></div><div class="r-cosa">1 anno e mezzo con figli</div></div>
<div class="r-piede"><a href="#domanda">Come si fa la domanda {G.ic("freccia")}</a><span>{G.ic("doc")}Fonti: legge 91/1992, Ministero dell'Interno</span></div>
</div>
</section>
{G.avviso("Questa pagina riassume la legge e le pagine del Ministero, ma <strong>decide il prefetto</strong> (o il Ministero se vivi all'estero). Questo sito non dà consulenza: per il tuo caso chiedi alla Prefettura o a un patronato.")}
<div class="due">
<section>
<h2 id="requisiti">{G.ic("lista")}I requisiti</h2>
<div class="fatti">
{_scheda(G, "orologio", "Anni di matrimonio e di residenza", "2 anni di residenza legale in Italia dopo il matrimonio, o 3 anni dalla data del matrimonio se risiedi all'estero. I termini sono ridotti della metà in presenza di figli nati o adottati dai coniugi.", "l91_art5", "dlci_matrimonio")}
{_scheda(G, "ok", "Il matrimonio deve durare fino al decreto", "Quando viene adottato il decreto non ci devono essere scioglimento, annullamento o cessazione degli effetti civili del matrimonio, né separazione personale. Con la sentenza n. 195 del 2022 la Corte costituzionale ha stabilito che la morte del coniuge durante il procedimento non è più un ostacolo.", "l91_art5")}
{_scheda(G, "voce", "Italiano almeno B1", "La legge 1° dicembre 2018 n. 132 ha introdotto la conoscenza dell'italiano anche per la cittadinanza per matrimonio. Serve un certificato almeno B1 di un ente riconosciuto, salvo esoneri (per esempio chi ha il permesso UE per soggiornanti di lungo periodo).", "dlci_matrimonio", "domanda")}
</div>
<p><a href="../#date">Date dell'esame B1</a> · <a href="../esempi/">Prove d'esempio ufficiali</a> · <a href="../esonero-test-italiano/#cittadinanza">Chi è esonerato dal B1</a> · <a href="../costo/">Quanto costa l'esame</a></p>
</section>
<aside>{G.modulo()}</aside>
</div>
<section>
<h2 id="chi-decide">{G.ic("edificio")}Chi decide</h2>
<p>Se vivi in Italia decide il <strong>prefetto</strong> della provincia di residenza. Se il coniuge straniero vive all'estero decide il Capo del Dipartimento per le libertà civili e l'immigrazione
(il Ministro dell'Interno se ci sono ragioni di sicurezza della Repubblica). <a href="../cittadinanza/">Contatti degli uffici cittadinanza, prefettura per prefettura</a>.</p>
{_fonte(G, "dlci_matrimonio", "cittadinanza")}
</section>
<section>
<h2 id="domanda">{G.ic("web")}La domanda, passo per passo</h2>
<ol class="passi">
<li><div><strong>Online</strong> sul portale del Ministero dell'Interno: con SPID o CIE se vivi in Italia; chi vive all'estero entra con le proprie credenziali personali.</div></li>
<li><div><strong>Documenti da allegare</strong> secondo il Ministero: documento di riconoscimento; atto di nascita e certificato penale del Paese di origine; certificato di italiano almeno B1 (salvo esoneri);
ricevuta del contributo di <strong>{contributo} €</strong>; estremi della marca da bollo telematica. Altri documenti li può chiedere la Prefettura: guarda la sua pagina nell'<a href="../cittadinanza/">elenco delle prefetture</a>.
<p>Un esempio: la {_a(G, "catania_matrimonio", "Prefettura di Catania")}, nella scheda sulla cittadinanza per matrimonio, chiede l'atto di nascita e il certificato penale tradotti e legalizzati, il titolo di soggiorno
e una marca da bollo da <strong>16 €</strong>; contributo e bollo si pagano con PagoPA dal portale, insieme alla domanda.</p></div></li>
<li><div><strong>Dopo l'invio</strong> la pratica ha un numero K10; lo stato si controlla online. <a href="../pratica-cittadinanza/">Stato della pratica, decreto e giuramento</a>.</div></li>
</ol>
{_fonte(G, "domanda", "consulta", "catania_matrimonio")}
</section>
<section>
<h2 id="tempi">{G.ic("orologio")}Quanto tempo ci vuole</h2>
<p>Per le domande presentate dal <strong>20 dicembre 2020</strong> il termine massimo del procedimento è di <strong>24 mesi</strong>, prorogabili fino a <strong>36 mesi</strong>; per quelle presentate prima,
<strong>48 mesi</strong>. È un termine di legge, non una previsione dei tempi reali.</p>
<p class="small">Il decreto-legge 28 marzo 2025 n. 36 (legge 23 maggio 2025 n. 74), che il Ministero elenca tra le norme sulla cittadinanza, non ha cambiato queste regole:
il testo dell'art. 5 e dell'art. 9-ter in vigore su Normattiva il {v} non riporta sue modifiche.</p>
{_fonte(G, "dlci_matrimonio", "l91_art9ter", "cittadinanza")}
</section>
<section>
<h2 id="domande">{G.ic("info")}Domande frequenti</h2>
{faq_html}
</section>
{_corpo_finale(G, "../", None)}"""
    G.pagina("cittadinanza-per-matrimonio/index.html",
             G.titolo_pagina("Cittadinanza italiana per matrimonio: requisiti, B1, domanda"),
             G.descrizione_pagina(f"Cittadinanza per matrimonio (art. 5 legge 91/1992): 2 anni in Italia o 3 all'estero, metà con figli, esame B1, domanda online, "
                                  f"contributo {contributo} €, tempi."), corpo, jsonld)


# ---------------------------------------------------------------- /pratica-cittadinanza/
def punti_prefetture(G):
    """Cosa scrivono le Prefetture su decreto e giuramento (prefetture_locali.json, frasi controllate da prefetture.py --controlla)."""
    righe = []
    for sl, loc in sorted(G.PREF_LOC["prefetture"].items()):
        for p in loc["punti"]:
            if re.search(r"giurament|decreto", p["titolo"], re.I) and G.ha_pagina_pref(sl):
                nome = G.PREF[sl]["nome"]
                righe.append(f'<li><strong><a href="../cittadinanza/{G.pref_url(sl)}/">{escape(nome)}</a></strong>: {p["testo"]}'
                             f'<p class="citaz">«{escape(p["citazioni"][0])}»</p></li>')
    return "<ul>" + "".join(righe) + "</ul>", len(righe)


def pagina_pratica(G):
    v = G.data_breve(GUIDE["verificato_il"])
    po = G.CITT["polo_orienta"]
    pref_html, n_pref = punti_prefetture(G)
    letto_pref = G.data_breve(G.PREF_LOC["letto_il"])
    faq = [
        ("Come si consulta la pratica di cittadinanza?",
         "Online, con il servizio del Dipartimento per le libertà civili e l'immigrazione, usando le stesse credenziali con cui hai fatto la domanda. "
         f"Puoi anche chiamare il Polo Orienta al {po['telefono']} ({po['giorni']}) con il numero K10 o K10C e un documento d'identità.",
         "consulta la pratica cittadinanza"),
        ("Cos'è il numero K10 della pratica di cittadinanza?",
         "È il numero identificativo della domanda (K10 o K10C). Il Ministero chiede di scriverlo nell'oggetto di ogni PEC sulla pratica e di averlo pronto quando chiami il Polo Orienta.",
         "k10 cittadinanza"),
        ("Entro quando si fa il giuramento per la cittadinanza?",
         "Entro 6 mesi dalla notifica del decreto (art. 10 della legge 91/1992); il Vademecum del Ministero parla di 180 giorni dalla notifica. Se non giuri in tempo il decreto non ha effetto "
         "e la pratica passa a «decaduto per mancato giuramento»; la riammissione si chiede alla Prefettura via PEC.", "giuramento cittadinanza"),
        ("Come arriva il decreto di cittadinanza?",
         "Dal novembre 2023 i decreti delle domande presentate in Italia si notificano con la piattaforma SEND di PagoPA: al domicilio digitale o con una raccomandata che contiene "
         "solo l'Avviso di Avvenuta Ricezione. Il decreto si scarica entro 120 giorni dalla notifica; dopo, bisogna chiederlo alla Prefettura.", "decreto cittadinanza"),
        ("Quanto tempo ci vuole per la cittadinanza italiana?",
         "Per le domande presentate dal 20 dicembre 2020 il termine di legge è di 24 mesi, prorogabili fino a 36. È un termine massimo, non una previsione dei tempi reali.",
         "cittadinanza italiana tempi"),
    ]
    jsonld, faq_html = _faq(G, faq)
    corpo = f"""<section class="hero">
{G.briciole(("EsameB1", "../"), ("Pratica di cittadinanza", None))}
<span class="occhiello">{G.ic("edificio")}Ministero dell'Interno e legge 91/1992 · letti il {v}</span>
<h1>Stato della pratica di cittadinanza, decreto e giuramento</h1>
<p class="lead">Secondo il Ministero dell'Interno (pagina «Cittadinanza: consulta la pratica», letta il {v}), lo stato della domanda si controlla online con le stesse credenziali usate per la domanda;
il numero della pratica (K10 o K10C) serve per scrivere alla PEC del Ministero e per il Polo Orienta. Se la cittadinanza è concessa, il decreto arriva con la piattaforma SEND e il giuramento
va fatto entro 6 mesi dalla notifica (art. 10 della legge 91/1992).</p>
<div class="risposta">
<div class="slot"><div class="r-et">{G.ic("tel")}Polo Orienta</div><div class="r-data">{po["telefono"]}</div><div class="r-cosa">{po["giorni"]} · con il numero K10</div></div>
<div class="slot"><div class="r-et">{G.ic("cal")}Giuramento</div><div class="r-data">6 mesi <small>dalla notifica</small></div><div class="r-cosa">del decreto · poi il decreto non ha effetto</div></div>
<div class="r-piede"><a href="#giuramento">Decreto e giuramento {G.ic("freccia")}</a><span>{G.ic("doc")}Fonti: Ministero dell'Interno, legge 91/1992</span></div>
</div>
</section>
{G.avviso("Questa pagina riassume le fonti ufficiali. Lo stato della tua pratica lo vedi solo sul portale del Ministero: <strong>decidono la Prefettura e il Ministero</strong>. Questo sito non è del Ministero.")}
<section>
<h2 id="stato">{G.ic("web")}Come controllare lo stato della pratica</h2>
<ol class="passi">
<li><div><strong>Online</strong>: il servizio web del Dipartimento per le libertà civili e l'immigrazione, con le stesse credenziali con cui hai compilato la domanda.</div></li>
<li><div><strong>PEC</strong>: per scrivere sulla pratica usa <strong style="overflow-wrap:anywhere">{escape(G.CITT["pec_ministero"])}</strong>, con il numero K10/K10C nell'oggetto.</div></li>
<li><div><strong>Polo Orienta</strong>: telefono {po["telefono"]}, {po["giorni"]}; oppure <span style="overflow-wrap:anywhere">{escape(po["pec"])}</span>. Tieni pronti il numero K10 o K10C e un documento d'identità.</div></li>
</ol>
{_fonte(G, "consulta", "domanda")}
<p><strong>Quanto si aspetta?</strong> Per le domande presentate dal 20 dicembre 2020 il termine di legge è di 24 mesi, prorogabili fino a 36 (art. 9-ter della legge 91/1992):
è un termine massimo, non una previsione. <a href="../cittadinanza/">Come si presenta la domanda</a> · <a href="../cittadinanza-per-matrimonio/">cittadinanza per matrimonio</a>.</p>
{_fonte(G, "l91_art9ter")}
</section>
<section>
<h2 id="decreto">{G.ic("doc")}Il decreto: come arriva</h2>
<ul>
<li>Dal <strong>novembre 2023</strong> i decreti di cittadinanza (concessioni, rifiuti, inammissibilità) delle domande presentate in Italia per matrimonio o residenza si notificano con la
<strong>piattaforma SEND</strong> di PagoPA.</li>
<li>Senza domicilio digitale arriva una raccomandata con il solo <strong>Avviso di Avvenuta Ricezione</strong>: il decreto si stampa nei punti di ritiro SEND. La notifica è perfezionata il
10° giorno dopo la raccomandata, o prima se stampi il decreto.</li>
<li>Il decreto si scarica entro <strong>120 giorni</strong> dalla notifica: dopo, se non sono passati i 180 giorni per il giuramento, chiedilo alla Prefettura, che lo manda sul Portale Servizi (senza una nuova notifica).</li>
<li>Il Ministero chiede alle Prefetture di notificare il decreto di concessione entro 90 giorni da quando lo ricevono.</li>
</ul>
{_fonte(G, "vademecum")}
</section>
<section>
<h2 id="giuramento">{G.ic("ok")}Il giuramento</h2>
<p>Il decreto non ha effetto se, <strong>entro 6 mesi dalla notifica</strong>, non giuri «di essere fedele alla Repubblica e di osservare la Costituzione e le leggi dello Stato».
Con la sentenza n. 258 del 2017 la Corte costituzionale ha esonerato dal giuramento chi non può farlo per una grave e accertata condizione di disabilità.</p>
{_fonte(G, "l91_art10")}
<p>Il Vademecum del Ministero conta <strong>180 giorni</strong> dalla notifica: dopo, la pratica passa a «decaduto per mancato giuramento». La riammissione la decide la Prefettura:
si chiede con un'istanza alla PEC della Prefettura (e per conoscenza a quella del Ministero), con i documenti che spiegano perché non hai saputo della notifica.
Il Vademecum, che riguarda la cittadinanza per residenza, ricorda che i requisiti devono restare fino al giuramento.</p>
{_fonte(G, "vademecum")}
<h3 id="prefetture">Dove si giura: cosa scrivono le Prefetture</h3>
<p>Il giuramento si fissa con il Comune di residenza. Ecco cosa scrivono {n_pref} Prefetture sulla loro pagina «Cittadinanza» (lette il {letto_pref}):</p>
{pref_html}
</section>
<section>
<h2 id="domande">{G.ic("info")}Domande frequenti</h2>
{faq_html}
</section>
{_corpo_finale(G, "../", None)}"""
    G.pagina("pratica-cittadinanza/index.html",
             G.titolo_pagina("Pratica di cittadinanza: stato K10, decreto e giuramento"),
             G.descrizione_pagina("Come controllare lo stato della pratica di cittadinanza (K10, Polo Orienta), come arriva il decreto con SEND e "
                                  "il giuramento entro 6 mesi dalla notifica."), corpo, jsonld)


# ---------------------------------------------------------------- tre guide sul ricongiungimento familiare (14/11/2026)
def _cit_p(k, inizio):
    return f'<p class="citaz">{_q(k, inizio)}</p>'


def _faq_misurate(G, pagina, faq):
    RICERCHE[pagina] = [r for *_, r in faq]
    return _faq(G, faq)


def _soglie(G):
    """Importi del reddito dal calcolo già controllato del sito (dati/ricongiungimento.json, genera.py)."""
    righe = G.tabella_ricongiungimento()
    annuo = Decimal(G.RICONG["assegno_sociale"]["annuo"])
    return {"anno": G.RICONG["anno"], "annuo": annuo, "meta": annuo / 2, "doppio": annuo * 2, "uno": righe[0][1], "due": righe[1][1], "tre": righe[2][1]}


# ---------------------------------------------------------------- /ricongiungimento-familiare/
def pagina_ricongiungimento_guida(G):
    v = G.data_breve(GUIDE["verificato_il"])
    S = _soglie(G)
    anno, e = S["anno"], G.euro
    faq = [
        ("Cos'è il nulla osta al ricongiungimento familiare?",
         "È il documento che lo Sportello unico per l'immigrazione della Prefettura rilascia a chi vive regolarmente in Italia e vuole far venire un familiare: "
         "con il nulla osta il familiare chiede il visto d'ingresso al consolato italiano del suo Paese. La domanda si invia online; secondo l'art. 29 del Testo unico "
         "immigrazione il nulla osta è rilasciato entro 150 giorni dalla richiesta, oppure arriva un provvedimento di diniego.",
         "nulla osta al ricongiungimento familiare"),
        ("Come si controlla online il nulla osta per il ricongiungimento familiare?",
         "Secondo la Prefettura di Firenze tutte le comunicazioni sulla domanda si vedono solo nell'area riservata del Portale Servizi ALI del Ministero dell'Interno, "
         "nella sezione comunicazioni: si entra con SPID o CIE. Da lì si scarica anche, in PDF, la comunicazione del rilascio del nulla osta.",
         "controllo nulla osta ricongiungimento familiare online"),
        ("Quali sono i requisiti per il ricongiungimento familiare?",
         f"Secondo gli articoli 28 e 29 del Testo unico immigrazione: un permesso di soggiorno di durata non inferiore a 1 anno (o il permesso UE di lungo periodo), "
         f"2 anni di soggiorno legale in Italia senza interruzioni se chiedi il coniuge, i figli maggiorenni o i genitori, un alloggio idoneo e un reddito annuo "
         f"di almeno {e(S['uno'])} con 1 familiare nel {anno}, più {e(S['meta'])} per ogni altro familiare. Chi ha lo status di rifugiato non deve dimostrare alloggio e reddito.",
         "requisiti per ricongiungimento familiare"),
        ("Come si fa il ricongiungimento familiare per la moglie o il marito?",
         "Il coniuge si può ricongiungere se non è legalmente separato e ha almeno 18 anni. Dal testo in vigore dell'art. 28 del Testo unico, chi chiede il coniuge "
         "deve avere almeno 2 anni di soggiorno legale ininterrotto in Italia (non vale per chi ha la protezione internazionale). Servono alloggio idoneo e reddito; "
         "la domanda di nulla osta si invia online allo Sportello unico per l'immigrazione.",
         "ricongiungimento familiare moglie"),
        ("Si può fare il ricongiungimento familiare per i genitori?",
         "Sì, ma solo in due casi scritti nell'art. 29 del Testo unico: genitori a carico che non hanno altri figli nel Paese di origine o di provenienza, oppure genitori "
         "con più di 65 anni se gli altri figli non possono mantenerli per documentati, gravi motivi di salute. Per il genitore con più di 65 anni serve anche "
         "un'assicurazione sanitaria o l'iscrizione al Servizio sanitario nazionale.",
         "ricongiungimento familiare per genitori"),
        ("Come si fa la domanda di ricongiungimento familiare?",
         "Online, sul Portale Servizi ALI del Ministero dell'Interno, con SPID o CIE: la domanda di nulla osta va allo Sportello unico per l'immigrazione della Prefettura "
         "del luogo dove vivi, con i documenti su alloggio e reddito. Secondo la Prefettura di Firenze serve 1 marca da bollo da 16 € per domanda.",
         "domanda ricongiungimento familiare"),
        ("Quanto tempo ci vuole per il ricongiungimento familiare?",
         "La legge fissa solo dei termini: il nulla osta è rilasciato entro 150 giorni dalla richiesta (art. 29 del Testo unico) e il consolato rilascia il visto entro 30 giorni "
         "dalla richiesta di visto (art. 6 del DPR 394/1999). Sono termini di legge, non una previsione dei tempi reali: quanto dura la tua pratica lo sa solo lo Sportello unico.",
         "ricongiungimento familiare quanto tempo ci vuole"),
        ("Come si ottiene il visto per ricongiungimento familiare?",
         "Dopo il nulla osta, il familiare chiede il visto al consolato italiano del suo Paese, che controlla l'autenticità dei documenti su parentela, matrimonio, "
         "minore età o stato di salute. Secondo la Prefettura di Firenze il nulla osta vale 6 mesi e il visto 365 giorni, entro i quali il familiare deve entrare in Italia.",
         "visto per ricongiungimento familiare"),
        ("Il ricongiungimento familiare con un cittadino italiano si fa allo stesso modo?",
         "No. Secondo la Prefettura di Firenze il familiare non comunitario di un cittadino italiano o comunitario non deve chiedere il nulla osta allo Sportello unico: "
         "chiede un visto d'ingresso specifico al consolato italiano. Al familiare di un cittadino italiano che non ha esercitato la libera circolazione nell'Unione europea è rilasciato in Italia un permesso di soggiorno per motivi di famiglia, valido 5 anni (art. 23, comma 1-bis, del decreto legislativo 30/2007); negli altri casi il titolo di soggiorno lo indica la Questura.",
         "ricongiungimento familiare con cittadino italiano"),
    ]
    jsonld, faq_html = _faq_misurate(G, "ricongiungimento-familiare/", faq)
    tab = ('<div class="tab-wrap ris-tab"><table class="conf"><thead><tr><th scope="col">Familiari da far venire</th>'
           f'<th scope="col">Reddito minimo annuo {anno}</th></tr></thead><tbody>'
           + "".join(f'<tr><td><strong>{n} {"familiare" if n == 1 else "familiari"}</strong></td><td data-l="Reddito {anno}">{e(t)}</td></tr>'
                     for n, t in ((1, S["uno"]), (2, S["due"]), (3, S["tre"])))
           + f'<tr><td><strong>2 o più figli sotto i 14 anni</strong></td><td data-l="Reddito {anno}">almeno {e(S["doppio"])}</td></tr></tbody></table></div>')
    corpo = f"""<section class="hero">
{G.briciole(("EsameB1", "../"), ("Ricongiungimento familiare", None))}
<span class="occhiello">{G.ic("doc")}Testo unico immigrazione, Ministero e Prefettura · letti il {v}</span>
<h1>Ricongiungimento familiare: requisiti, nulla osta e domanda online</h1>
<p class="lead">Secondo l'art. 29 del Testo unico immigrazione (testo in vigore letto su Normattiva il {v}), lo straniero che vive regolarmente in Italia può chiedere il ricongiungimento
per il coniuge, i figli minori, i figli maggiorenni a carico con invalidità totale e, in alcuni casi, i genitori. La domanda di nulla osta si invia online allo Sportello unico per l'immigrazione
della Prefettura, con i documenti su alloggio e reddito; il nulla osta è rilasciato entro 150 giorni dalla richiesta.</p>
<div class="risposta">
<div class="slot"><div class="r-et">{G.ic("orologio")}Nulla osta</div><div class="r-data">150 giorni <small>termine di legge</small></div><div class="r-cosa">dalla richiesta allo Sportello unico · non è una previsione dei tempi reali</div></div>
<div class="slot"><div class="r-et">{G.ic("euro")}Reddito {anno}</div><div class="r-data">{e(S["uno"])} <small>l'anno</small></div><div class="r-cosa">con 1 familiare · + {e(S["meta"])} per ogni altro</div></div>
<div class="r-piede"><a href="#domanda">La domanda, passo per passo {G.ic("freccia")}</a><span>{G.ic("doc")}Fonti: Testo unico immigrazione, DPR 394/1999, Ministero dell'Interno, Prefettura di Firenze</span></div>
</div>
</section>
{G.avviso("Questa pagina riassume la legge e le pagine ufficiali. <strong>Decidono lo Sportello unico per l'immigrazione</strong> (nulla osta), <strong>il consolato</strong> (visto) <strong>e la Questura</strong> (permesso): per il tuo caso rivolgiti allo Sportello unico della tua Prefettura o a un patronato. Questo sito non è del Ministero e non dà consulenza.")}
<section>
<h2 id="chi">{G.ic("lista")}Chi può chiederlo (cittadini non comunitari)</h2>
<p>L'art. 28 del Testo unico riconosce il diritto all'unità familiare</p>
{_cit_p("tu28", "agli stranieri titolari")}
<p>e anche a chi ha un permesso per protezione internazionale, per studio, per motivi religiosi o per motivi familiari. Il Ministero dell'Interno lo riassume così: {_q("sui", "Il cittadino straniero che si trova")}.</p>
<h3 id="due-anni">I 2 anni di soggiorno legale</h3>
<p>Il testo dell'art. 28 in vigore dall'11 dicembre 2024 aggiunge una condizione: gli stranieri che chiedono il ricongiungimento, {_q("tu28", "ad esclusione dei titolari")},</p>
{_cit_p("tu28", "devono avere maturato")}
<p>Le lettere a), c) e d) sono il coniuge, i figli maggiorenni a carico e i genitori. I figli minori (lettera b) non sono in questo elenco.</p>
{_fonte(G, "tu28", "sui")}
<p class="small">La Prefettura di Firenze, nella pagina aggiornata il 3 novembre 2026, elenca tra i titoli il {_q("firenze_ric", "permesso di soggiorno della durata")} lavoro subordinato, lavoro autonomo, motivi familiari,
motivi religiosi, studio: le parole non sono quelle dell'art. 28 (permesso di durata non inferiore a 1 anno e 2 anni di soggiorno legale). Quale permesso e quale periodo valgono per te lo dice lo Sportello unico della tua Prefettura.</p>
{_fonte(G, "firenze_ric")}
</section>
<section>
<h2 id="familiari">{G.ic("ok")}Per quali familiari</h2>
<p>L'art. 29, comma 1, elenca quattro casi. Le frasi sono quelle della legge.</p>
<div class="fatti">
{_scheda(G, "ok", '<span id="moglie">Moglie o marito</span>', _q("tu29", "coniuge non legalmente separato") + ". Chi chiede il coniuge deve avere i 2 anni di soggiorno legale (vedi sopra).", "tu29")}
{_scheda(G, "ok", "Figli minori", _q("tu29", "figli minori, anche del coniuge") + ". Conta l'età al momento della domanda: " + _q("tu29", "si considerano minori") + ". " + _q("tu29", "I minori adottati") + ".", "tu29")}
{_scheda(G, "ok", "Figli maggiorenni a carico", _q("tu29", "figli maggiorenni a carico") + ".", "tu29")}
{_scheda(G, "ok", '<span id="genitori">Genitori</span>', _q("tu29", "genitori a carico") + ". Per il genitore con più di 65 anni la legge chiede anche un'assicurazione sanitaria o l'iscrizione al Servizio sanitario nazionale.", "tu29")}
</div>
<p>La legge non elenca altri parenti. Il ricongiungimento del coniuge e dei genitori non è consentito {_q("tu29", "quando il familiare di cui si chiede")}.
Se i rapporti di parentela non si possono provare con certificati sicuri, il consolato può rilasciare una certificazione {_q("tu29", "sulla base dell'esame del DNA")}.</p>
{_fonte(G, "tu29")}
<p><strong>Familiare di un cittadino italiano o dell'Unione europea?</strong> La procedura è un'altra: {_q("firenze_ric", "il familiare non comunitario")}.
<a href="../permesso-soggiorno-motivi-familiari/#cittadino-italiano">Il permesso per il familiare di un cittadino italiano</a>.</p>
{_fonte(G, "firenze_ric")}
</section>
<section>
<h2 id="requisiti">{G.ic("scudo")}I requisiti: alloggio e reddito</h2>
<p>Secondo l'art. 29, comma 3, chi chiede il ricongiungimento deve dimostrare di avere:</p>
<div class="fatti">
{_scheda(G, "edificio", "Un alloggio idoneo", _q("tu29", "di un alloggio conforme") + ". " + _q("tu29", "Nel caso di un figlio") + '. <a href="../idoneita-alloggiativa/">Il certificato di idoneità alloggiativa: parametri, costi, tempi</a>.', "tu29")}
{_scheda(G, "euro", f"Un reddito minimo: {e(S['uno'])} con 1 familiare", _q("tu29", "di un reddito minimo annuo") + f". Nel {anno} l'assegno sociale è {e(S['annuo'])} l'anno: la metà è {e(S['meta'])}. " + _q("tu29", "si tiene conto anche") + ".", "tu29")}
{_scheda(G, "info", "Per il genitore con più di 65 anni", _q("tu29", "di una assicurazione sanitaria") + ".", "tu29")}
</div>
<h3 id="reddito">Reddito minimo {anno}</h3>
{tab}
<p class="small">Importi calcolati con l'assegno sociale {anno} dell'INPS; sono gli stessi della tabella pubblicata dalla Prefettura di Firenze nel novembre 2026. Per due o più figli sotto i 14 anni la legge chiede
«in ogni caso» un reddito non inferiore al doppio dell'assegno sociale. <a href="../reddito-ricongiungimento-familiare/">Tabella completa da 1 a 5 familiari, al mese e all'anno, e come si calcola</a> ·
<a href="../ricongiungimento-familiare-documenti/#reddito">con quali documenti si dimostra</a>.</p>
{_fonte(G, "tu29", "firenze_doc")}
<h3 id="rifugiati">Rifugiati: senza requisiti di alloggio e reddito</h3>
<p>L'art. 29-bis dice: {_q("tu29bis", "Lo straniero al quale")}. {_q("tu29bis", "Non si applicano")} (il comma 3 è quello di alloggio e reddito). E ancora: {_q("tu29bis", "Il rigetto della domanda")}.
La Prefettura di Firenze scrive che {_q("firenze_doc", "ai titolari di riconoscimento")}.
Le regole dell'art. 29 non si applicano invece {_q("tu29", "quando il soggiornante chiede")}.</p>
{_fonte(G, "tu29bis", "tu29", "firenze_doc")}
</section>
<section>
<h2 id="domanda">{G.ic("web")}La domanda, passo per passo</h2>
<ol class="passi">
<li><div><strong>Domanda di nulla osta online</strong> sul {_a(G, "ali", "Portale Servizi ALI del Ministero dell'Interno")}, con SPID o CIE.
<p>La legge: {_q("tu29", "La domanda di nulla osta")}. La Prefettura di Firenze precisa che la domanda {_q("firenze_ric", "deve essere inviata esclusivamente")} e che serve 1 marca da bollo da 16 €.
<a href="../ricongiungimento-familiare-documenti/">Tutti i documenti da allegare</a>.</p></div></li>
<li><div><strong>Lo Sportello unico controlla</strong>: chiede il parere della Questura, verifica alloggio e reddito, poi {_q("tu29", "rilascia il nulla osta ovvero")}.
<p>Se manca qualcosa, a Firenze arriva sul portale {_q("firenze_doc", "un preavviso di rigetto")}.</p></div></li>
<li><div><strong>Visto al consolato</strong>: il nulla osta è mandato per via telematica al consolato italiano; il familiare chiede il visto d'ingresso nel suo Paese.
<p>Il rilascio del visto {_q("tu29", "è subordinato all'effettivo accertamento")}. Per il regolamento i consolati {_q("dpr394_6", "rilasciano il visto di ingresso")}.</p></div></li>
<li><div><strong>Arrivo in Italia</strong>: il permesso di soggiorno per motivi familiari si chiede attraverso lo Sportello unico che ha rilasciato il nulla osta (lo scrivono il Portale Immigrazione e Poste Italiane).
<p>La Prefettura di Firenze chiede di farsi sentire entro 8 giorni: {_q("firenze_ric", "Entro 8 giorni")} per avere l'appuntamento. <a href="#dopo">Cosa fare dopo l'arrivo</a>.</p></div></li>
</ol>
{_fonte(G, "tu29", "dpr394_6", "sui", "firenze_ric", "firenze_doc", "firenze_faq", "pi_famiglia", "poste")}
</section>
<section>
<h2 id="nulla-osta">{G.ic("orologio")}Il nulla osta: tempi, controllo online, validità</h2>
<h3 id="tempi">Entro quando arriva</h3>
<p>L'art. 29, comma 8 (testo in vigore dal 4 ottobre 2025): il nulla osta al ricongiungimento familiare è rilasciato entro <strong>150 giorni</strong> dalla richiesta («centocinquanta giorni»).
È un termine di legge, non una previsione: i tempi reali dipendono dallo Sportello unico. La Prefettura di Firenze scrive: {_q("firenze_ric", "Le domande saranno esaminate")}; l'esame anticipato si può chiedere solo
per gravi e comprovati motivi di salute, via PEC.</p>
<p class="small">L'art. 6 del regolamento (DPR 394/1999, testo in vigore dal 2005) scrive ancora {_q("dpr394_6", "entro novanta giorni")}: 90 giorni, non 150. I due testi non coincidono.
Nostra lettura: il Testo unico è la legge ed è stato modificato dopo il regolamento, e la Prefettura di Firenze nel novembre 2026 scrive 150 giorni; se il termine conta per il tuo caso, chiedi conferma allo Sportello unico.</p>
{_fonte(G, "tu29", "dpr394_6", "firenze_ric", "firenze_faq")}
<h3 id="controllo">Come si controlla online</h3>
<p>La Prefettura di Firenze: {_q("firenze_ric", "Tutte le comunicazioni")}. Quando il nulla osta è rilasciato, {_q("firenze_arrivo", "la comunicazione del rilascio")}.
Questa comunicazione va mandata al familiare all'estero: serve per chiedere l'appuntamento al consolato. Altre Prefetture possono dare indicazioni diverse: guarda la pagina dello Sportello unico della tua.</p>
{_fonte(G, "firenze_ric", "firenze_arrivo", "ali")}
<h3 id="validita">Quanto vale</h3>
<p>Secondo la Prefettura di Firenze {_q("firenze_ric", "Il nulla osta ha validità")}: in questo tempo il familiare deve chiedere il visto. Il consolato {_q("firenze_ric", "rilascerà un visto")}.
E ancora: {_q("firenze_faq", "non è possibile modificare")}; se i requisiti sono cambiati o il documento è scaduto serve una nuova domanda.
Queste durate (6 mesi e 365 giorni) sono scritte dalla Prefettura di Firenze, non nell'art. 29: per la tua pratica valgono le date scritte nel nulla osta e nel visto.</p>
{_fonte(G, "firenze_ric", "firenze_faq")}
</section>
<section>
<h2 id="dopo">{G.ic("pin")}Dopo l'arrivo in Italia</h2>
<ul>
<li><strong>Entro 48 ore</strong> (Prefettura di Firenze): la dichiarazione di ospitalità. {_q("firenze_ric", "Entro 48 ore")} alla Questura, al commissariato di polizia o in Comune.</li>
<li><strong>Entro 8 giorni</strong> (Prefettura di Firenze): il contatto con lo Sportello unico per l'appuntamento. Quel giorno, a Firenze, {_q("firenze_ric", "lo Sportello Unico provvederà")}; lì il familiare riceve anche il codice fiscale.</li>
<li><strong>Permesso di soggiorno per motivi familiari</strong>: è rilasciato a chi entra con il visto per ricongiungimento familiare; consente di lavorare e di studiare.
<a href="../permesso-soggiorno-motivi-familiari/">Permesso per motivi familiari: durata, rinnovo, documenti</a>.</li>
</ul>
{_fonte(G, "firenze_ric", "firenze_arrivo", "tu30")}
<p class="small">Indirizzi email, moduli e appuntamenti cambiano da una Prefettura all'altra: quelli scritti qui sono un esempio (Firenze). <a href="../ricongiungimento-familiare-documenti/#arrivo">Documenti per l'appuntamento dopo l'arrivo</a>.</p>
</section>
<section>
<h2 id="seguito">{G.ic("info")}Familiari al seguito</h2>
<p>Chi entra in Italia con un visto può portare con sé i familiari. L'art. 29, comma 4: {_q("tu29", "È consentito l'ingresso, al seguito")}, se ci sono i requisiti di alloggio e di reddito.
Per questa richiesta {_q("dpr394_6", "Ai fini della richiesta")}.</p>
{_fonte(G, "tu29", "dpr394_6")}
</section>
<section>
<h2 id="diniego">{G.ic("attenzione")}Se la domanda è respinta</h2>
<p>La legge prevede che {_q("tu29", "La richiesta di ricongiungimento familiare è respinta")}.
Sul diniego, l'art. 30, comma 6: {_q("tu30", "Contro il diniego")}. Come e quando farlo non è materia di questa pagina: rivolgiti a un avvocato o a un patronato.</p>
{_fonte(G, "tu29", "tu30")}
</section>
<section>
<h2 id="domande">{G.ic("info")}Domande frequenti</h2>
{faq_html}
</section>
<section>
<h2 id="guide-famiglia">{G.ic("lista")}Le altre pagine sul ricongiungimento</h2>
<div class="griglia link3"><a href="../ricongiungimento-familiare-documenti/">{G.ic("doc")}<span>Documenti<small>elenco, modelli S2 e S3, idoneità alloggiativa</small></span></a>
<a href="../reddito-ricongiungimento-familiare/">{G.ic("euro")}<span>Reddito minimo {anno}<small>tabella da 1 a 5 familiari</small></span></a>
<a href="../permesso-soggiorno-motivi-familiari/">{G.ic("scudo")}<span>Permesso per motivi familiari<small>durata, rinnovo, coesione familiare</small></span></a></div>
</section>
{_corpo_finale(G, "../", "ricongiungimento-familiare/")}"""
    G.pagina("ricongiungimento-familiare/index.html",
             G.titolo_pagina(f"Ricongiungimento familiare {anno}: requisiti e nulla osta", "Ricongiungimento familiare: requisiti e nulla osta"),
             G.descrizione_pagina(f"Ricongiungimento familiare: chi può chiederlo, per quali familiari, 2 anni di soggiorno, reddito {e(S['uno'])} nel {anno}, "
                                  "domanda online, nulla osta: 150 giorni per legge.",
                                  "Ricongiungimento familiare: chi può chiederlo, per quali familiari, 2 anni di soggiorno, reddito, domanda online, nulla osta: 150 giorni per legge."),
             corpo, jsonld)


# ---------------------------------------------------------------- /ricongiungimento-familiare-documenti/
def pagina_ricongiungimento_documenti(G):
    v = G.data_breve(GUIDE["verificato_il"])
    S = _soglie(G)
    anno, e = S["anno"], G.euro
    faq = [
        ("Quali documenti servono per il ricongiungimento familiare?",
         "Secondo l'art. 6 del DPR 394/1999: copia del permesso di soggiorno, documentazione del reddito, documentazione dell'alloggio (attestazione dell'ufficio comunale "
         "o certificato di idoneità igienico-sanitaria dell'ASL) e documentazione dei rapporti di parentela, della minore età e dello stato di famiglia. "
         "L'elenco di dettaglio lo pubblica ogni Prefettura: quella di Firenze chiede anche passaporti, codice fiscale e certificati di stato di famiglia.",
         "documenti per ricongiungimento familiare"),
        ("Cos'è il modello S2 per il ricongiungimento familiare?",
         "È la dichiarazione con cui il titolare dell'alloggio dà il consenso a ospitare anche i familiari ricongiunti. La Prefettura di Firenze lo chiede "
         "con il documento d'identità del titolare e scrive di non accettarlo in copia. Il modello si scarica dalla pagina dello Sportello unico della propria Prefettura.",
         "modello s2 ricongiungimento familiare"),
        ("Cos'è il modello S3 per il ricongiungimento familiare?",
         "È l'autocertificazione del datore di lavoro: dice che il rapporto di lavoro è in corso e quanto è la retribuzione mensile. La Prefettura di Firenze la chiede "
         "con data non anteriore di 1 mese e con il documento d'identità del datore di lavoro.",
         "modello s3 ricongiungimento familiare"),
        ("Cos'è il certificato di idoneità alloggiativa?",
         "È il documento del Comune che attesta che l'alloggio ha i requisiti igienico-sanitari e di idoneità abitativa chiesti dall'art. 29 del Testo unico immigrazione: "
         "gli uffici comunali verificano anche il numero degli occupanti e i requisiti del decreto del Ministro della sanità del 5 luglio 1975. "
         "In alternativa il regolamento ammette il certificato di idoneità igienico-sanitaria dell'ASL.",
         "certificato di idoneità alloggiativa"),
        ("Dove si richiede l'idoneità alloggiativa?",
         "Al Comune dove si trova l'alloggio: per la legge i requisiti sono accertati dai competenti uffici comunali. Modulo, costo e tempi li stabilisce ogni Comune: "
         "chiedi all'ufficio del tuo Comune. La Prefettura di Firenze chiede un certificato rilasciato per finalità di ricongiungimento familiare.",
         "richiesta idoneità alloggiativa"),
        ("Per il ricongiungimento familiare serve il CUD?",
         "Dipende dal lavoro e dalla Prefettura. Quella di Firenze, per i lavoratori dipendenti che lavorano da oltre un anno, chiede l'ultima dichiarazione dei redditi "
         "oppure l'ultimo CUD o modello unico e le ultime 3 buste paga; a chi lavora da meno di un anno chiede tutte le buste paga.",
         "cud per ricongiungimento familiare 2025"),
        ("Si può fare il ricongiungimento familiare senza reddito?",
         "Solo in un caso scritto nella legge: per chi ha lo status di rifugiato non si applicano i requisiti di alloggio e di reddito (art. 29-bis del Testo unico). "
         "La Prefettura di Firenze scrive che ai titolari di protezione internazionale non è richiesta la dimostrazione di alloggio e reddito. "
         "Negli altri casi il reddito minimo è un requisito; si può sommare il reddito dei familiari conviventi.",
         "ricongiungimento familiare senza reddito"),
    ]
    jsonld, faq_html = _faq_misurate(G, "ricongiungimento-familiare-documenti/", faq)
    lavori = [
        ("Lavoratori dipendenti", [_q("firenze_doc", "in caso di attività intrapresa da oltre"), _q("firenze_doc", "in caso di attività intrapresa da meno"),
                                   _q("firenze_doc", "contratto di lavoro/lettera"), _q("firenze_doc", "autocertificazione del datore di lavoro") + " (modello S3, non più vecchio di 1 mese)",
                                   "documento d'identità del datore di lavoro, firmato"]),
        ("Lavoratori domestici", ["ultima dichiarazione dei redditi, CUD o modello unico, dove previsti; tutte le buste paga se si lavora da meno di un anno",
                                  _q("firenze_doc", "comunicazione di assunzione"), _q("firenze_doc", "ultimi 3 bollettini") + ", dove previsti", "modello S3 e documento d'identità del datore di lavoro"]),
        ("Titolari di ditte individuali", [_q("firenze_doc", "visura camerale") + " (30 giorni)", _q("firenze_doc", "certificato di attribuzione"), "licenza comunale, dove prevista",
                                           "ultima dichiarazione dei redditi se l'attività ha più di un anno", _q("firenze_doc", "bilancino")]),
        ("Liberi professionisti", [_q("firenze_doc", "iscrizione all'albo"), "ultima dichiarazione dei redditi se l'attività ha più di un anno", "bilancino dell'anno in corso, firmato dal professionista che lo ha redatto"]),
    ]
    tab_lavori = ('<div class="tab-wrap ris-tab"><table class="conf"><thead><tr><th scope="col">Lavoro</th><th scope="col">Documenti chiesti dalla Prefettura di Firenze</th></tr></thead><tbody>'
                  + "".join(f'<tr><td><strong>{t}</strong></td><td data-l="Documenti"><ul>{"".join(f"<li>{x}</li>" for x in voci)}</ul></td></tr>' for t, voci in lavori)
                  + "</tbody></table></div>")
    corpo = f"""<section class="hero">
{G.briciole(("EsameB1", "../"), ("Ricongiungimento familiare", "../ricongiungimento-familiare/"), ("Documenti", None))}
<span class="occhiello">{G.ic("doc")}DPR 394/1999 e Prefettura di Firenze · letti il {v}</span>
<h1>Documenti per il ricongiungimento familiare: elenco, modelli S2 e S3, idoneità alloggiativa</h1>
<p class="lead">Secondo l'art. 6 del regolamento del Testo unico immigrazione (DPR 394/1999, letto su Normattiva il {v}), la domanda di nulla osta al ricongiungimento va presentata con: copia del permesso di soggiorno,
documentazione del reddito, documentazione dell'alloggio e documentazione dei rapporti di parentela. L'elenco di dettaglio lo pubblica ogni Prefettura: qui trovi quello della Prefettura di Firenze (novembre 2026), come esempio.</p>
<div class="risposta">
<div class="slot"><div class="r-et">{G.ic("doc")}Marca da bollo</div><div class="r-data">16 € <small>1 per domanda</small></div><div class="r-cosa">secondo la Prefettura di Firenze · fino a 5 familiari per pratica</div></div>
<div class="slot"><div class="r-et">{G.ic("web")}File da allegare</div><div class="r-data">2 MB <small>al massimo</small></div><div class="r-cosa">PDF o p7m, sul Portale Servizi ALI (Prefettura di Firenze)</div></div>
<div class="r-piede"><a href="#elenco">L'elenco dei documenti {G.ic("freccia")}</a><span>{G.ic("doc")}Fonti: DPR 394/1999, Testo unico immigrazione, Prefettura di Firenze</span></div>
</div>
</section>
{G.avviso("L'elenco di dettaglio è quello della <strong>Prefettura di Firenze</strong>: altre Prefetture possono chiedere documenti o moduli diversi. <strong>Decide lo Sportello unico per l'immigrazione</strong> della tua Prefettura: prima di inviare la domanda leggi la sua pagina o rivolgiti a un patronato. Questo sito non dà consulenza.")}
<section>
<h2 id="legge">{G.ic("lista")}Cosa chiede il regolamento</h2>
<p>L'art. 6, comma 1, del DPR 394/1999 dice che la domanda deve essere corredata da:</p>
<ul>
<li>{_q("dpr394_6", "copia della carta di soggiorno")};</li>
<li>{_q("dpr394_6", "documentazione attestante la disponibilità del reddito")};</li>
<li>documentazione dell'alloggio: {_q("dpr394_6", "l'interessato deve produrre")};</li>
<li>{_q("dpr394_6", "documentazione attestante i rapporti")};</li>
<li>{_q("dpr394_6", "documentazione attestante l'invalidità")}, per i figli maggiorenni e i genitori, {_q("dpr394_6", "rilasciata, a spese del richiedente")}.</li>
</ul>
<p>I documenti su parentela, salute e condizione economica dei familiari vengono dal Paese di origine: {_q("dpr394_6", "L'autorità consolare italiana provvede")}.</p>
{_fonte(G, "dpr394_6")}
</section>
<section>
<h2 id="elenco">{G.ic("doc")}L'elenco della Prefettura di Firenze: i documenti di base</h2>
<ol>
<li>{_q("firenze_doc", "pagine del passaporto")} (in un unico file);</li>
<li>{_q("firenze_doc", "permesso di soggiorno in corso")};</li>
<li>{_q("firenze_doc", "codice fiscale del richiedente")};</li>
<li>{_q("firenze_doc", "certificato di stato di famiglia del richiedente")};</li>
<li>{_q("firenze_doc", "certificato di stato di famiglia relativo")}.</li>
</ol>
{_fonte(G, "firenze_doc")}
</section>
<section>
<h2 id="alloggio">{G.ic("edificio")}I documenti dell'alloggio</h2>
<div class="fatti">
{_scheda(G, "edificio", "Casa in affitto", _q("firenze_doc", "contratto di affitto") + "; certificato di idoneità alloggiativa; modello S2 del titolare dell'appartamento con il suo documento d'identità firmato.", "firenze_doc")}
{_scheda(G, "edificio", "Casa in comodato o ospitalità", _q("firenze_doc", "dichiarazione di cessione fabbricato") + " (anche questo di almeno 6 mesi, registrato); certificato di idoneità alloggiativa; modello S2 e documento d'identità del titolare.", "firenze_doc")}
{_scheda(G, "edificio", "Casa di proprietà", _q("firenze_doc", "contratto di compravendita") + " e certificato di idoneità alloggiativa.", "firenze_doc")}
</div>
<p><strong>Un solo figlio sotto i 14 anni</strong>: {_q("firenze_doc", "in caso di ricongiungimento a favore di un solo minore")}. La legge dice: {_q("tu29", "Nel caso di un figlio")}.
Per due o più figli sotto i 14 anni, secondo la Prefettura di Firenze, {_q("firenze_faq", "per il ricongiungimento di due o più familiari")}.</p>
<p>Secondo la Prefettura di Firenze i familiari possono abitare in una casa diversa dalla tua: anche per quella casa chiede contratto, modello S2, idoneità alloggiativa e stato di famiglia di chi ci abita.</p>
{_fonte(G, "firenze_doc", "firenze_faq", "tu29")}
<h3 id="idoneita-alloggiativa">Il certificato di idoneità alloggiativa</h3>
<p>È il documento che prova il requisito dell'alloggio. L'art. 29, comma 3, lettera a), chiede la disponibilità {_q("tu29", "di un alloggio conforme")}.
Il regolamento indica due documenti possibili: {_q("dpr394_6", "l'interessato deve produrre")}.</p>
<ul>
<li><strong>Dove si chiede</strong>: al Comune dove si trova l'alloggio (la legge parla di «competenti uffici comunali»).</li>
<li><strong>Modulo, costo, tempi e durata</strong>: li stabilisce ogni Comune. <a href="../idoneita-alloggiativa/#comuni">Cosa scrivono i Comuni di Roma, Torino, Napoli, Bologna e Firenze</a>; per gli altri chiedi all'ufficio del tuo Comune.</li>
<li><strong>Quante persone</strong>: <a href="../idoneita-alloggiativa/#parametri">i metri quadri per persona del decreto del 5 luglio 1975</a>.</li>
<li><strong>Per quale scopo</strong>: la Prefettura di Firenze chiede un {_q("firenze_doc", "certificato di idoneità alloggiativa rilasciato")}.</li>
<li><strong>Se è un file firmato digitalmente</strong>: la Prefettura di Firenze chiede di {_q("firenze_doc", "allegare il file pdf originale")}.</li>
</ul>
{_fonte(G, "tu29", "dpr394_6", "firenze_doc")}
</section>
<section>
<h2 id="reddito">{G.ic("euro")}I documenti del reddito</h2>
<p>Il reddito minimo {anno} è {e(S["uno"])} l'anno con 1 familiare, più {e(S["meta"])} per ogni altro familiare (<a href="../reddito-ricongiungimento-familiare/">tabella completa</a>).
Con quali documenti si dimostra dipende dal lavoro. La Prefettura di Firenze chiede:</p>
{tab_lavori}
<p class="small">La tabella è una sintesi: l'elenco completo (per esempio i documenti d'identità di chi firma) è nel PDF della Prefettura di Firenze, che elenca documenti anche per chi ha redditi da partecipazione in società, collaborazioni coordinate e continuative e per i soci lavoratori di cooperative: sono nel PDF qui sotto.</p>
{_fonte(G, "firenze_doc")}
<h3 id="redditi-familiari">Sommare il reddito dei familiari</h3>
<p>La legge: {_q("tu29", "si tiene conto anche")}. La Prefettura di Firenze precisa: {_q("firenze_faq", "i redditi possono essere integrati")} (genitori, coniugi, figli, fratelli), con i documenti che provano la parentela
e gli stessi documenti di lavoro e reddito chiesti a chi fa la domanda.</p>
{_fonte(G, "tu29", "firenze_faq")}
<h3 id="figli-14">Due o più figli sotto i 14 anni: come conta la Prefettura di Firenze</h3>
<p>La legge chiede «in ogni caso» un reddito non inferiore al doppio dell'assegno sociale ({e(S["doppio"])} nel {anno}). La Prefettura di Firenze spiega il suo calcolo, basato sulla circolare del Ministero dell'Interno n. 11524 del 28 ottobre 2008:</p>
{_cit_p("firenze_doc", "per il calcolo delle soglie con 2 o più figli")}
<p>Il suo esempio: {_q("firenze_doc", "1 maggiorenne con 2 minori")}, cioè {e(S["doppio"])} + {e(S["meta"])} = 17.752,80 €. È il metodo scritto da una Prefettura: la tua può confermarlo o no, chiedi allo Sportello unico.</p>
{_fonte(G, "firenze_doc", "tu29")}
</section>
<section>
<h2 id="modelli">{G.ic("matita")}I modelli S1, S2 e S3</h2>
<div class="tab-wrap ris-tab"><table class="conf"><thead><tr><th scope="col">Modello</th><th scope="col">Cos'è (nome dato dalla Prefettura di Firenze)</th><th scope="col">Chi lo firma</th></tr></thead><tbody>
<tr><td><strong>S1</strong></td><td data-l="Cos'è">{_q("firenze_ric", "Modello S1")}: dichiarazione di ospitalità, al posto dell'idoneità alloggiativa, quando arriva un solo figlio sotto i 14 anni</td><td data-l="Chi lo firma">il titolare dell'alloggio</td></tr>
<tr><td><strong>S2</strong></td><td data-l="Cos'è">{_q("firenze_ric", "Modello S2")}: {_q("firenze_doc", "dichiarazione redatta dal titolare")}</td><td data-l="Chi lo firma">ogni proprietario e ogni conduttore dell'alloggio</td></tr>
<tr><td><strong>S3</strong></td><td data-l="Cos'è">{_q("firenze_ric", "Modello S3")}: dice che il rapporto di lavoro è in corso e quanto è la retribuzione mensile</td><td data-l="Chi lo firma">il datore di lavoro</td></tr>
</tbody></table></div>
<p>Originale o copia? La Prefettura di Firenze scrive: {_q("firenze_faq", "la prefettura non accetta")}; {_q("firenze_faq", "il modello S3, invece")}.
I moduli si scaricano dalla pagina dello Sportello unico della propria Prefettura: quelli di Firenze sono in fondo alla {_a(G, "firenze_ric", "pagina «Nulla osta al ricongiungimento familiare»")}.
Ogni Prefettura pubblica i propri: usa quelli della tua.</p>
{_fonte(G, "firenze_ric", "firenze_doc", "firenze_faq")}
</section>
<section>
<h2 id="over65">{G.ic("info")}Genitori con più di 65 anni</h2>
<p>La legge chiede la disponibilità {_q("tu29", "di una assicurazione sanitaria")}. A Firenze, all'appuntamento dopo l'arrivo, si porta {_q("firenze_arrivo", "per i genitori sopra i 65 anni")}.</p>
{_fonte(G, "tu29", "firenze_arrivo")}
</section>
<section>
<h2 id="invio">{G.ic("web")}Come si allegano e cosa succede se manca qualcosa</h2>
<ul>
<li><strong>Formato</strong>: {_q("firenze_faq", "possono essere caricati")} (2 MB per ogni documento).</li>
<li><strong>Quanti familiari</strong>: {_q("firenze_faq", "il numero dei familiari")}: 5 familiari al massimo; per gli altri serve una seconda pratica.</li>
<li><strong>Marca da bollo</strong>: {_q("firenze_faq", "la domanda di ricongiungimento familiare necessita")}.</li>
<li><strong>Documenti mancanti</strong>: arriva sul portale {_q("firenze_doc", "un preavviso di rigetto")}.</li>
</ul>
{_fonte(G, "firenze_faq", "firenze_doc")}
<p><a href="../ricongiungimento-familiare/#domanda">La domanda di nulla osta, passo per passo</a> · <a href="../ricongiungimento-familiare/#controllo">come si controlla online</a></p>
</section>
<section>
<h2 id="arrivo">{G.ic("pin")}I documenti dopo l'arrivo del familiare</h2>
<p>Per l'appuntamento allo Sportello unico, dove si chiede il permesso di soggiorno, la Prefettura di Firenze elenca:</p>
<ul>
<li>{_q("firenze_arrivo", "marca da bollo")};</li>
<li>{_q("firenze_arrivo", "fotocopia passaporto")};</li>
<li>il permesso di soggiorno di chi ha fatto la domanda;</li>
<li>{_q("firenze_arrivo", "comunicazione di cessione")} (va fatta entro 48 ore dall'arrivo);</li>
<li>{_q("firenze_arrivo", "idoneità alloggiativa in originale")}.</li>
</ul>
{_fonte(G, "firenze_arrivo")}
<p><a href="../permesso-soggiorno-motivi-familiari/">Il permesso di soggiorno per motivi familiari: durata, rinnovo, costi</a></p>
</section>
<section>
<h2 id="domande">{G.ic("info")}Domande frequenti</h2>
{faq_html}
</section>
{_corpo_finale(G, "../", None)}"""
    G.pagina("ricongiungimento-familiare-documenti/index.html",
             G.titolo_pagina("Documenti ricongiungimento familiare: elenco, S2, S3", "Documenti per il ricongiungimento familiare"),
             G.descrizione_pagina("Documenti per il ricongiungimento familiare: elenco dell'art. 6 DPR 394/1999 e della Prefettura di Firenze, modelli S1, S2, S3, "
                                  "idoneità alloggiativa.", "Documenti per il ricongiungimento familiare: elenco, modelli S1, S2 e S3, idoneità alloggiativa, reddito."),
             corpo, jsonld)


# ---------------------------------------------------------------- /permesso-soggiorno-motivi-familiari/
def pagina_motivi_familiari(G):
    v = G.data_breve(GUIDE["verificato_il"])
    S = _soglie(G)
    anno, e = S["anno"], G.euro
    faq = [
        ("Cos'è il permesso di soggiorno per motivi familiari?",
         "È il permesso previsto dall'art. 30 del Testo unico immigrazione. È rilasciato a chi entra in Italia con il visto per ricongiungimento familiare o al seguito di un familiare, "
         "a chi è regolarmente in Italia da almeno 1 anno e si sposa in Italia con un cittadino italiano, dell'Unione europea o con uno straniero regolarmente soggiornante, "
         "al familiare già regolarmente in Italia che ha i requisiti per il ricongiungimento e al genitore straniero di un minore italiano residente in Italia. Consente di lavorare e di studiare.",
         "permesso di soggiorno per motivi familiari"),
        ("Cos'è la coesione familiare?",
         "È il nome che il Portale Immigrazione usa per il caso dell'art. 30, comma 1, lettera c), del Testo unico: il familiare è già regolarmente in Italia con un altro permesso "
         "e ha i requisiti per il ricongiungimento, quindi il suo permesso viene convertito in permesso per motivi familiari. "
         "Sul Portale Immigrazione la conversione è il codice 10.",
         "coesione familiare"),
        ("Quali documenti servono per il permesso di soggiorno per motivi familiari?",
         "Secondo il Portale Immigrazione (codice 13): il modulo 1 compilato e firmato e la fotocopia di tutto il passaporto. Per il primo rilascio dopo il ricongiungimento "
         "il modulo 1 si compila allo Sportello unico che ha rilasciato il nulla osta. Per la conversione da un altro permesso (codice 10) servono anche i documenti anagrafici "
         "del legame familiare, la dichiarazione dei redditi del familiare e il certificato di idoneità alloggiativa.",
         "permesso di soggiorno per motivi familiari documenti"),
        ("Come si rinnova il permesso di soggiorno per motivi familiari?",
         "Secondo l'art. 30 del Testo unico il permesso è rinnovabile insieme a quello del familiare. Il Portale Immigrazione (codice 13) chiede, con la domanda di rinnovo, "
         "una dichiarazione del familiare che ha ottenuto il ricongiungimento, o con il quale è stata fatta la coesione familiare, di provvedere al sostentamento. "
         "Il rinnovo si presenta negli uffici postali Sportello Amico.",
         "permesso di soggiorno per motivi familiari rinnovo"),
        ("Quanto dura il permesso di soggiorno per motivi familiari?",
         "Secondo l'art. 30 del Testo unico ha la stessa durata del permesso di soggiorno del familiare straniero che ha i requisiti per il ricongiungimento. "
         "Il permesso per motivi di famiglia del familiare di un cittadino italiano che non ha esercitato la libera circolazione vale 5 anni (art. 23 del decreto legislativo 30/2007).",
         "durata permesso di soggiorno per motivi familiari"),
        ("Che permesso di soggiorno ha il familiare di un cittadino italiano?",
         "Secondo l'art. 23, comma 1-bis, del decreto legislativo 30/2007, al familiare non comunitario di un cittadino italiano che non ha esercitato il diritto alla libera circolazione "
         "è rilasciato il permesso di soggiorno per motivi di famiglia: vale 5 anni, è rinnovabile alla scadenza e si può convertire in permesso per lavoro. "
         "Sul Portale Immigrazione è il codice 34.",
         "permesso di soggiorno per familiare di cittadino italiano"),
        ("Come funziona la coesione familiare con un cittadino italiano?",
         "Il Portale Immigrazione scrive che per la coesione familiare con un cittadino italiano o di uno Stato dell'Unione europea è sufficiente la documentazione "
         "che attesta il rapporto di parentela. Per il permesso «familiare cittadino italiano» (codice 34) chiede anche, al primo rilascio, la dichiarazione dei redditi "
         "o altra documentazione del familiare italiano. La domanda si può presentare alla posta o direttamente in Questura.",
         "coesione familiare con cittadino italiano"),
    ]
    jsonld, faq_html = _faq_misurate(G, "permesso-soggiorno-motivi-familiari/", faq)
    corpo = f"""<section class="hero">
{G.briciole(("EsameB1", "../"), ("Permesso per motivi familiari", None))}
<span class="occhiello">{G.ic("scudo")}Testo unico immigrazione e Portale Immigrazione · letti il {v}</span>
<h1>Permesso di soggiorno per motivi familiari e coesione familiare</h1>
<p class="lead">Secondo l'art. 30 del Testo unico immigrazione (testo in vigore letto su Normattiva il {v}), il permesso di soggiorno per motivi familiari è rilasciato a chi entra con il visto per ricongiungimento familiare,
a chi è regolarmente in Italia da almeno 1 anno e si sposa in Italia, al familiare già regolarmente in Italia che ha i requisiti per il ricongiungimento (la «coesione familiare») e al genitore di un minore italiano.
Consente di lavorare e di studiare e dura quanto il permesso del familiare.</p>
<div class="risposta">
<div class="slot"><div class="r-et">{G.ic("orologio")}Durata</div><div class="r-data">come il familiare</div><div class="r-cosa">stessa durata del suo permesso, e si rinnova insieme (art. 30)</div></div>
<div class="slot"><div class="r-et">{G.ic("scudo")}Familiare di cittadino italiano</div><div class="r-data">5 anni</div><div class="r-cosa">se l'italiano non ha esercitato la libera circolazione nell'Unione europea · art. 23 del d.lgs. 30/2007</div></div>
<div class="r-piede"><a href="#documenti">Documenti e costi {G.ic("freccia")}</a><span>{G.ic("doc")}Fonti: Testo unico immigrazione, d.lgs. 30/2007, Portale Immigrazione, Poste</span></div>
</div>
</section>
{G.avviso("Questa pagina riassume la legge e le pagine ufficiali, ma <strong>decide la Questura</strong>. Questo sito non dà consulenza: per il tuo caso rivolgiti alla Questura, allo Sportello unico della Prefettura o a un patronato.")}
<section>
<h2 id="chi">{G.ic("lista")}A chi è rilasciato</h2>
<p>L'art. 30, comma 1, elenca quattro casi. Le frasi sono quelle della legge.</p>
<div class="fatti">
{_scheda(G, "ok", "Chi entra con il visto per ricongiungimento", _q("tu30", "allo straniero che ha fatto ingresso") + '. <a href="../ricongiungimento-familiare/">Come funziona il ricongiungimento familiare</a>.', "tu30")}
{_scheda(G, "ok", "Chi si sposa in Italia", _q("tu30", "agli stranieri regolarmente soggiornanti") + ". Questo permesso " + _q("tu30", "è immediatamente revocato") + ".", "tu30")}
{_scheda(G, "ok", "Il familiare già in Italia (coesione familiare)", _q("tu30", "al familiare straniero regolarmente soggiornante") + ". " + _q("tu30", "In tal caso il permesso") + ".", "tu30")}
{_scheda(G, "ok", "Il genitore di un minore italiano", _q("tu30", "al genitore straniero") + ": il permesso " + _q("tu30", "è rilasciato anche a prescindere") + ".", "tu30")}
</div>
</section>
<section>
<h2 id="coesione">{G.ic("info")}La coesione familiare</h2>
<p>«Coesione familiare» non è una parola dell'art. 30: la usa il Portale Immigrazione (Ministero dell'Interno e Poste) per il terzo caso, quello del familiare che è già regolarmente in Italia.
L'art. 30 non parla qui di nulla osta dello Sportello unico: dice che il permesso che il familiare ha già viene <strong>convertito</strong> in permesso per motivi familiari. Sul Portale Immigrazione è il codice 10.</p>
<p><strong>Documenti</strong> secondo il Portale Immigrazione (codice 10):</p>
<ul>
<li>{_q("pi_famiglia", "istanza compilata")};</li>
<li>{_q("pi_famiglia", "fotocopia di tutto il passaporto")};</li>
<li>{_q("pi_conversione", "documentazione anagrafica")} ({_q("pi_conversione", "se la documentazione anagrafica proviene")}, salvo accordi internazionali);</li>
<li>{_q("pi_conversione", "fotocopia della dichiarazione dei redditi")};</li>
<li>{_q("pi_conversione", "certificato di idoneità alloggiativa")} (<a href="../idoneita-alloggiativa/">come si chiede al Comune</a>).</li>
</ul>
<p><strong>Quando si chiede</strong>: la legge dice che la conversione può essere richiesta «entro un anno dalla data di scadenza del titolo di soggiorno originariamente posseduto dal familiare».
Il Portale Immigrazione aggiunge: {_q("pi_conversione", "cioè entro l'ultimo anno")}. Quando presentare la domanda nel tuo caso lo dice la Questura.
Se il familiare con cui si chiede la coesione è un rifugiato, la legge dice: {_q("tu30", "Qualora detto cittadino")}.</p>
<p><strong>Reddito</strong>: i requisiti sono quelli del ricongiungimento (art. 29): nel {anno} almeno {e(S["uno"])} l'anno con 1 familiare, più {e(S["meta"])} per ogni altro. <a href="../reddito-ricongiungimento-familiare/">Tabella del reddito</a>.</p>
<p class="small">Attenzione: la scheda del Portale Immigrazione (aggiornata il 4 novembre 2024) riporta ancora altri parametri: {_q("pi_conversione", "per 1 familiare")}.
Non sono quelli del testo dell'art. 29 in vigore (assegno sociale più la metà per ogni familiare): le due fonti non coincidono. Nostra lettura: vale il testo di legge; quale importo applica il tuo ufficio lo conferma la Questura.</p>
{_fonte(G, "tu30", "pi_conversione", "pi_famiglia", "tu29")}
</section>
<section>
<h2 id="cosa-consente">{G.ic("ok")}Cosa consente</h2>
<p>L'art. 30, comma 2: il permesso per motivi familiari {_q("tu30", "consente l'accesso")}.
Il Portale Immigrazione aggiunge che {_q("pi_famiglia", "può essere utilizzato anche")}.</p>
{_fonte(G, "tu30", "pi_famiglia")}
</section>
<section>
<h2 id="durata">{G.ic("orologio")}Durata e rinnovo</h2>
<p>L'art. 30, comma 3: il permesso per motivi familiari {_q("tu30", "ha la stessa durata")}.</p>
<p><strong>Rinnovo</strong>: il Portale Immigrazione (codice 13, scheda aggiornata il 22 luglio 2024) scrive che {_q("pi_famiglia", "la richiesta di rinnovo")}. La domanda si presenta negli uffici postali Sportello Amico.</p>
<p><strong>Se il legame finisce</strong>: {_q("tu30", "In caso di morte")}, fermi i requisiti minimi di età per lavorare. «Diciottesimo anno di età» vuol dire il compimento dei 18 anni.</p>
{_fonte(G, "tu30", "pi_famiglia")}
</section>
<section>
<h2 id="documenti">{G.ic("doc")}Documenti, dove si presenta e quanto costa</h2>
<ol class="passi">
<li><div><strong>Dopo il ricongiungimento</strong> (primo rilascio): {_q("pi_famiglia", "per la richiesta di rilascio")}.
<p>Poste Italiane scrive lo stesso: {_q("poste", "se hai il nullaosta")}.</p></div></li>
<li><div><strong>Negli altri casi</strong> (rinnovo, conversione, aggiornamento, duplicato): kit a banda gialla degli uffici postali, codice 13 «famiglia» (codice 14 «famiglia minore», codice 10 per la conversione), con {_q("pi_famiglia", "istanza compilata")} e {_q("pi_famiglia", "fotocopia di tutto il passaporto")}.</div></li>
<li><div><strong>Dopo la consegna alla posta</strong> ricevi, tra l'altro, {_q("poste", "Una lettera di convocazione")}: date e appuntamenti li decide la Questura.</div></li>
</ol>
{_fonte(G, "pi_famiglia", "poste")}
<div class="tab-wrap ris-tab"><table class="conf"><thead><tr><th scope="col">Costo (tabella del Portale Immigrazione)</th><th scope="col">Importo</th></tr></thead><tbody>
<tr><td><strong>Marca da bollo</strong></td><td data-l="Importo">16,00 €</td></tr>
<tr><td><strong>Produzione del permesso elettronico</strong> (bollettino)</td><td data-l="Importo">30,46 €</td></tr>
<tr><td><strong>Contributo</strong>, permesso di durata superiore a tre mesi e fino a un anno</td><td data-l="Importo">40,00 €</td></tr>
<tr><td><strong>Contributo</strong>, permesso di durata superiore a un anno e fino a due anni</td><td data-l="Importo">50,00 €</td></tr>
<tr><td><strong>Spedizione</strong>, all'ufficio postale</td><td data-l="Importo">30,00 €</td></tr>
</tbody></table></div>
<p class="small">Il contributo dipende dalla durata del permesso; per i minori di 18 anni la tabella del Portale Immigrazione indica il contributo come «non previsto», e lo stesso scrive per le richieste di aggiornamento, conversione e duplicato. Non facciamo la somma: prima di pagare controlla l'importo del bollettino all'ufficio postale o in Questura.</p>
{_fonte(G, "portale_costi")}
</section>
<section>
<h2 id="cittadino-italiano">{G.ic("scudo")}Familiare di un cittadino italiano</h2>
<p>Per i familiari non comunitari dei cittadini italiani le regole sono nell'art. 23 del decreto legislativo 30/2007 (testo in vigore dall'11 agosto 2023 secondo Normattiva), che distingue due casi:</p>
<ul>
<li><strong>Il cittadino italiano non ha esercitato la libera circolazione</strong> (non ha vissuto in un altro Paese dell'Unione europea secondo le regole europee): al familiare {_q("dlgs30_23", "è rilasciato il permesso")}.
{_q("dlgs30_23", "Il permesso di soggiorno per motivi di famiglia di cui")}. Sul Portale Immigrazione è il {_a(G, "pi_famita", "codice 34")}.</li>
<li><strong>Il cittadino italiano ha esercitato la libera circolazione</strong>: le regole del decreto legislativo 30/2007 sui familiari dei cittadini dell'Unione, se più favorevoli, {_q("dlgs30_23", "si applicano ai familiari")} {_q("dlgs30_23", "che hanno esercitato")}.</li>
</ul>
<p>La frase tra parentesi sulla libera circolazione è una nostra spiegazione breve: in quale dei due casi rientri lo valuta la Questura.</p>
<p><strong>Ingresso</strong>: secondo la Prefettura di Firenze {_q("firenze_ric", "il familiare non comunitario")}.</p>
<p><strong>Documenti</strong> secondo il Portale Immigrazione (codice 34): modulo 1, fotocopia di tutto il passaporto, {_q("pi_famita", "documentazione anagrafica")} e, per il primo rilascio, {_q("pi_famita", "fotocopia della dichiarazione dei redditi")}.
Per la coesione familiare con un cittadino italiano o dell'Unione la scheda del codice 10 scrive: {_q("pi_conversione", "per coesione familiare con cittadino italiano")}.</p>
<p><strong>Dove</strong>: Poste Italiane scrive: {_q("poste", "Se sei familiare straniero")}.</p>
{_fonte(G, "dlgs30_23", "pi_famita", "pi_conversione", "poste", "firenze_ric")}
<p class="small">Se un giorno chiederai la cittadinanza: <a href="../cittadinanza-per-matrimonio/">cittadinanza per matrimonio</a> · <a href="../carta-di-soggiorno/">permesso UE di lungo periodo (carta di soggiorno)</a>.</p>
</section>
<section>
<h2 id="diniego">{G.ic("attenzione")}Se il permesso è rifiutato o revocato</h2>
<p>L'art. 30, comma 6: {_q("tu30", "Contro il diniego")}. Come e quando farlo non è materia di questa pagina: rivolgiti a un avvocato o a un patronato.</p>
{_fonte(G, "tu30")}
</section>
<section>
<h2 id="domande">{G.ic("info")}Domande frequenti</h2>
{faq_html}
</section>
<section>
<h2 id="guide-famiglia">{G.ic("lista")}Le pagine sul ricongiungimento</h2>
<div class="griglia link3"><a href="../ricongiungimento-familiare/">{G.ic("ok")}<span>Ricongiungimento familiare<small>requisiti, nulla osta, domanda</small></span></a>
<a href="../ricongiungimento-familiare-documenti/">{G.ic("doc")}<span>Documenti<small>elenco, modelli S2 e S3, idoneità alloggiativa</small></span></a>
<a href="../reddito-ricongiungimento-familiare/">{G.ic("euro")}<span>Reddito minimo {anno}<small>tabella da 1 a 5 familiari</small></span></a></div>
</section>
{_corpo_finale(G, "../", None)}"""
    G.pagina("permesso-soggiorno-motivi-familiari/index.html",
             G.titolo_pagina("Permesso di soggiorno per motivi familiari e coesione", "Permesso di soggiorno per motivi familiari"),
             G.descrizione_pagina("Permesso di soggiorno per motivi familiari (art. 30): a chi spetta, coesione familiare, durata, rinnovo, documenti, costi, "
                                  "familiare di cittadino italiano."), corpo, jsonld)


# ---------------------------------------------------------------- /idoneita-alloggiativa/ (14/11/2026, sera)
# Tema «idoneità alloggiativa» (8.100 ricerche al mese). Legge nazionale da Normattiva; costi, tempi e validità solo dai Comuni
# di cui si legge la pagina ufficiale (Roma, Torino, Napoli, Bologna, Firenze). Il sito del Comune di Milano risponde
# «accesso negato» ai controlli: niente dati di Milano. Il testo del DM 5/7/1975 sulla Gazzetta Ufficiale è solo un'immagine:
# i numeri del decreto sono quelli riportati dal Comune di Firenze e dalla Città di Torino, e la pagina lo dice.
def pagina_idoneita(G):
    v = G.data_breve(GUIDE["verificato_il"])
    q = _q
    faq = [
        ("Cos'è l'idoneità alloggiativa?",
         "È il documento del Comune che dice per quante persone è idoneo un alloggio, in base ai vani e alla superficie. La legge sull'immigrazione chiede un alloggio "
         "conforme ai requisiti igienico-sanitari e di idoneità abitativa, accertati dagli uffici comunali, con i requisiti del decreto del Ministro della sanità del 5 luglio 1975. "
         "I Comuni lo chiamano attestato, attestazione o certificato di idoneità alloggiativa o abitativa.",
         "idoneità alloggiativa"),
        ("A cosa serve il certificato di idoneità alloggiativa?",
         "Serve al cittadino straniero in alcune pratiche con la Prefettura o la Questura: il nulla osta al ricongiungimento familiare, la coesione familiare, "
         "il permesso di soggiorno UE per soggiornanti di lungo periodo (carta di soggiorno) e le pratiche di lavoro subordinato. Quale documento vuole l'ufficio "
         "lo indica lo Sportello unico per l'immigrazione o la Questura.",
         "certificato di idoneità alloggiativa"),
        ("Dove si richiede l'idoneità alloggiativa?",
         "Al Comune dove si trova l'alloggio: per la legge i requisiti sono accertati dai competenti uffici comunali. L'ufficio cambia da città a città: a Roma è il Municipio, "
         "a Torino l'Ufficio idoneità alloggiativa, a Napoli un nucleo della Polizia Locale, a Bologna e Firenze si fa tutto online.",
         "richiesta idoneità alloggiativa"),
        ("Si può chiedere l'idoneità alloggiativa online?",
         "Dipende dal Comune. Secondo le loro pagine ufficiali: a Firenze la domanda si invia solo online con SPID, CIE o CNS; a Bologna online con SPID o CIE; "
         "a Roma il modulo si compila online sul sito della Prefettura e poi va al Municipio; a Napoli si invia per PEC; a Torino solo allo sportello, su appuntamento.",
         "idoneità alloggiativa online"),
        ("Serve l'idoneità alloggiativa per il permesso di soggiorno?",
         "Non per ogni permesso. La legge chiede un alloggio idoneo per il ricongiungimento familiare e, con parole diverse, per il permesso UE di lungo periodo (nella frase che riguarda i familiari) e per il contratto di soggiorno "
         "per lavoro subordinato; il Portale Immigrazione la elenca anche per la coesione familiare. Per il tuo caso decide la Questura o lo Sportello unico.",
         "idoneità alloggiativa per permesso di soggiorno"),
        ("Serve l'idoneità alloggiativa per il ricongiungimento familiare?",
         "Sì: l'art. 29 del Testo unico immigrazione chiede la disponibilità di un alloggio idoneo e il regolamento chiede l'attestazione dell'ufficio comunale oppure "
         "il certificato di idoneità igienico-sanitaria dell'ASL. Per un figlio sotto i 14 anni al seguito di un genitore basta il consenso del titolare dell'alloggio. "
         "A chi ha lo status di rifugiato il requisito dell'alloggio non si applica.",
         "idoneità alloggiativa per ricongiungimento familiare"),
        ("Serve l'idoneità alloggiativa per la carta di soggiorno?",
         "L'art. 9 del Testo unico parla di un alloggio idoneo nei parametri della legge regionale per le case popolari, oppure con i requisiti igienico-sanitari accertati dall'ASL, "
         "e lo scrive insieme al reddito per i familiari. Il Portale Immigrazione chiede la fotocopia del certificato nelle domande con i figli minori. "
         "Ai titolari di protezione internazionale la documentazione sull'alloggio non è richiesta. Se chiedi il permesso solo per te, chiedi alla Questura.",
         "idoneità alloggiativa per carta di soggiorno"),
        ("Quali documenti servono per l'idoneità alloggiativa?",
         "Li stabilisce ogni Comune. Nelle pagine dei cinque Comuni che abbiamo letto tornano quasi sempre: documento d'identità e permesso di soggiorno, contratto di affitto registrato "
         "o atto di proprietà, planimetria catastale, consenso del proprietario o di chi ospita. Roma, Torino, Napoli e Firenze chiedono anche una scheda o relazione firmata "
         "da un tecnico abilitato; Bologna no.",
         "documenti per idoneità alloggiativa"),
        ("Dove si trova il modulo per l'idoneità alloggiativa?",
         "Sul sito del Comune dove si trova l'alloggio: ogni Comune ha il suo. A Roma il modulo si compila online sul sito della Prefettura, a Torino si scarica dalla pagina del servizio, "
         "a Napoli la pagina del Comune elenca i modelli da scaricare, a Firenze e Bologna la domanda è un modulo online.",
         "modulo idoneità alloggiativa"),
        ("Idoneità alloggiativa per 5 persone: quanti metri quadri servono?",
         "Secondo i numeri che il Comune di Firenze indica applicando il decreto del 5 luglio 1975, servono 14 m² a persona per i primi 4 abitanti e 10 m² per ciascuno dei successivi: "
         "per 5 persone fa 66 m² di superficie abitabile (nostro calcolo). Non basta la superficie totale: contano anche le stanze da letto e il soggiorno, e ogni Comune può avere "
         "parametri propri. Il numero di persone lo decide il Comune.",
         "idoneità alloggiativa per 5 persone"),
        ("Come si rinnova l'idoneità alloggiativa?",
         "Dipende dal Comune e da quanto vale l'attestato. A Torino vale 1 anno e per un nuovo attestato sullo stesso alloggio il tecnico può dichiarare che nulla è mutato; "
         "a Firenze vale 6 mesi; a Napoli esiste una domanda di rinnovo, con diritti di istruttoria di 10,00 €; a Bologna l'attestato ha validità illimitata e si aggiorna solo se cambia qualcosa.",
         "rinnovo idoneità alloggiativa"),
        ("Come si chiede l'idoneità alloggiativa a Roma?",
         "Secondo Roma Capitale si compila il modulo online sul sito della Prefettura di Roma, si stampa e si consegna al Municipio con gli allegati; il termine del procedimento è di 30 giorni. "
         "Un avviso di Roma Capitale con l'indirizzo del Municipio XV indica una marca da bollo da 16 € e diritti di istruttoria di 60,00 €: chiedi conferma al tuo Municipio.",
         "idoneità alloggiativa roma"),
        ("Come si chiede l'idoneità alloggiativa a Milano?",
         "Non lo scriviamo: il sito del Comune di Milano ha negato l'accesso ai nostri controlli del 14 novembre 2026 e su questo sito mettiamo solo quello che leggiamo "
         "nelle fonti ufficiali. Vale la regola generale: l'idoneità si chiede al Comune dove si trova l'alloggio. Costi, tempi e moduli li trovi sul sito del Comune di Milano.",
         "idoneità alloggiativa milano"),
        ("Come si chiede l'idoneità alloggiativa a Torino?",
         "Secondo la Città di Torino la domanda si presenta solo allo sportello dell'Ufficio idoneità alloggiativa di via Orvieto 1/20/A, su appuntamento, con la scheda di un tecnico. "
         "Servono due marche da bollo da 16 €, una sulla domanda e una sull'attestato. La risposta arriva entro 120 giorni e l'attestato vale 1 anno.",
         "idoneità alloggiativa torino"),
    ]
    jsonld, faq_html = _faq_misurate(G, "idoneita-alloggiativa/", faq)

    persone = [(1, 14), (2, 28), (3, 42), (4, 56), (5, 66), (6, 76)]
    tab_persone = ('<div class="tab-wrap"><table class="conf"><thead><tr><th scope="col">Persone</th><th scope="col">Superficie abitabile minima</th><th scope="col">Come si arriva al numero</th></tr></thead><tbody>'
                   + "".join(f'<tr><td><strong>{n}</strong></td><td>{m} m²</td><td>{f"{n} × 14" if n <= 4 else f"56 + {n - 4} × 10"}</td></tr>' for n, m in persone)
                   + "</tbody></table></div>")
    comuni = [
        ("roma", "Roma", "ida_roma",
         "modulo online sul sito della Prefettura, poi stampa e consegna al Municipio",
         "marca da bollo da 16 € e diritti di istruttoria di 60,00 € (avviso con l'indirizzo del Municipio XV)",
         "30 giorni (termine del procedimento)", "non scritta nelle pagine lette"),
        ("torino", "Torino", "ida_torino",
         "solo allo sportello di via Orvieto 1/20/A, su appuntamento",
         "2 marche da bollo da 16 €: una sulla domanda, una sull'attestato",
         "entro 120 giorni; 10 giorni con un preavviso di rigetto di Prefettura o Questura", "1 anno dal rilascio"),
        ("napoli", "Napoli", "ida_napoli",
         "per PEC al nucleo della Polizia Locale, con i moduli compilati dal tecnico incaricato",
         "diritti di istruttoria: 20,00 € la nuova domanda, 10,00 € il rinnovo o il duplicato; in più l'imposta di bollo sulla domanda e sul certificato",
         "30 giorni dalla richiesta", "non scritta nella pagina letta"),
        ("bologna", "Bologna", "ida_bologna",
         "online, con SPID o CIE",
         "nessun costo",
         "entro 30 giorni; 2 giorni lavorativi per le richieste urgenti di Questura o Prefettura", "illimitata, da aggiornare se cambia qualcosa"),
        ("firenze", "Firenze", "ida_firenze",
         "solo online, con SPID, CIE o CNS",
         "imposta di bollo da 16 €",
         "entro 90 giorni dalla domanda completa", "6 mesi dall'emissione"),
    ]
    tab_comuni = ('<div class="tab-wrap ris-tab"><table class="conf"><thead><tr><th scope="col">Comune</th><th scope="col">Come si chiede</th><th scope="col">Costi scritti dal Comune</th>'
                  '<th scope="col">Tempi scritti</th><th scope="col">Validità</th></tr></thead><tbody>'
                  + "".join(f'<tr><td><strong><a href="#{a}">{n}</a></strong></td><td data-l="Come si chiede">{come}</td><td data-l="Costi">{costi}</td>'
                            f'<td data-l="Tempi">{tempi}</td><td data-l="Validità">{val}</td></tr>' for a, n, _, come, costi, tempi, val in comuni)
                  + "</tbody></table></div>")
    corpo = f"""<section class="hero">
{G.briciole(("EsameB1", "../"), ("Idoneità alloggiativa", None))}
<span class="occhiello">{G.ic("edificio")}Testo unico immigrazione e 5 Comuni · letti il {v}</span>
<h1>Idoneità alloggiativa: cos'è il certificato, a cosa serve, come si richiede</h1>
<p class="lead">Il certificato di idoneità alloggiativa (o abitativa) è il documento del Comune che dice per quante persone è idoneo un alloggio. Lo chiedono Prefettura e Questura ai cittadini stranieri
in alcune pratiche: ricongiungimento familiare, carta di soggiorno, lavoro. Qui trovi cosa dice la legge e cosa scrivono, sulle loro pagine ufficiali, i Comuni di Roma, Torino, Napoli, Bologna e Firenze su costi, tempi e documenti.</p>
<div class="risposta">
<div class="slot"><div class="r-et">{G.ic("edificio")}Chi lo rilascia</div><div class="r-data">Il Comune <small>dove si trova l'alloggio</small></div><div class="r-cosa">la legge parla di competenti uffici comunali · modulo, costo e tempi cambiano da Comune a Comune</div></div>
<div class="slot"><div class="r-et">{G.ic("lista")}La regola di base</div><div class="r-data">14 m² <small>a persona, per i primi 4 abitanti</small></div><div class="r-cosa">10 m² per ciascuno dei successivi: numeri del Comune di Firenze, che applica il decreto del 5 luglio 1975</div></div>
<div class="r-piede"><a href="#comuni">Costi e tempi in 5 Comuni {G.ic("freccia")}</a><span>{G.ic("doc")}Fonti: Normattiva, Portale Immigrazione, siti dei Comuni</span></div>
</div>
</section>
{G.avviso("Queste sono <strong>informazioni, non consulenza legale</strong>. Costi, tempi, moduli e validità li stabilisce <strong>il Comune dove si trova l'alloggio</strong>; quale documento serve nella tua pratica lo decide lo Sportello unico per l'immigrazione o la Questura. Prima di pagare un tecnico o una marca da bollo leggi la pagina del tuo Comune.")}
<section>
<h2 id="cose">{G.ic("info")}Cos'è l'idoneità alloggiativa</h2>
<p>La legge non usa un nome solo. L'art. 29, comma 3, lettera a), del Testo unico immigrazione chiede a chi vuole il ricongiungimento familiare la disponibilità {q("tu29", "di un alloggio conforme")}.
Il documento del Comune che lo attesta si chiama, secondo i Comuni, attestato, attestazione o certificato di idoneità alloggiativa (Roma, Torino, Firenze) o di idoneità abitativa (Bologna, Napoli).</p>
<div class="fatti">
{_scheda(G, "edificio", "Cosa dice", "Secondo il Comune di Firenze " + q("ida_firenze", "è un documento con il quale") + ". (La frase è scritta così nel documento del Comune.)", "ida_firenze")}
{_scheda(G, "lista", "Cosa conta", "Per la Città di Torino l'attestato " + q("ida_torino", "definisce quante persone") + ".", "ida_torino")}
{_scheda(G, "attenzione", "Cosa non è", "Secondo il Comune di Napoli il certificato " + q("ida_napoli", "non costituisce alcuna certificazione") + ".", "ida_napoli")}
</div>
</section>
<section>
<h2 id="quando">{G.ic("doc")}Quando serve</h2>
<p>Secondo la Città di Torino l'attestazione è chiesta dalla Prefettura (Sportello unico immigrazione) o dalla Questura (Ufficio immigrazione) per vari permessi e visti, tra cui: {q("ida_torino", "visto per ricongiungimento familiare")}.
Ecco cosa dice la legge, caso per caso.</p>
<h3 id="ricongiungimento">Ricongiungimento familiare</h3>
<p>È il caso scritto in modo più chiaro. Oltre all'art. 29 citato sopra, il regolamento (art. 6 del DPR 394/1999) dice che per l'alloggio {q("dpr394_6", "l'interessato deve produrre")}.
Per i familiari al seguito e per la coesione familiare il riferimento è lo stesso art. 29: il Portale Immigrazione, per la conversione in permesso per motivi familiari, elenca il {q("pi_conversione", "certificato di idoneità alloggiativa")}.</p>
{_fonte(G, "tu29", "dpr394_6", "pi_conversione")}
<p><a href="../ricongiungimento-familiare/">La guida al ricongiungimento familiare</a> · <a href="../ricongiungimento-familiare-documenti/#alloggio">i documenti dell'alloggio chiesti dalla Prefettura di Firenze</a> · <a href="../permesso-soggiorno-motivi-familiari/#coesione">la coesione familiare</a></p>
<h3 id="carta-di-soggiorno">Permesso UE per soggiornanti di lungo periodo (carta di soggiorno)</h3>
<p>Qui la legge usa parole diverse. L'art. 9, comma 1, del Testo unico parla della disponibilità {q("tu9", "di un alloggio idoneo")}, {q("tu9", "ovvero che sia fornito")}.
Lo scrive nella stessa frase del reddito per i familiari. Il regolamento (art. 16, comma 4, del DPR 394/1999), nel caso di richiesta relativa ai familiari, chiede la documentazione che prova {q("dpr394_16", "la disponibilità di un alloggio")}: {q("dpr394_16", "A tale fine")}.
Il Portale Immigrazione elenca la {q("portale_imm", "Fotocopia del certificato di idoneità alloggiativa")} tra i documenti per i figli minori. Se chiedi il permesso solo per te, chiedi alla Questura se vuole questo documento.</p>
{_fonte(G, "tu9", "dpr394_16", "portale_imm")}
<p><a href="../carta-di-soggiorno/">Carta di soggiorno: requisiti, documenti, costi</a></p>
<h3 id="lavoro">Contratto di soggiorno e lavoro subordinato</h3>
<p>L'art. 5-bis del Testo unico dice che il contratto di soggiorno per lavoro subordinato contiene {q("tu5bis", "la garanzia da parte del datore")} {q("tu5bis", "dal decreto del Ministro")}.
È il testo in vigore dal 18 dicembre 2025, letto su Normattiva. Per il nulla osta al lavoro l'art. 22 chiede al datore di lavoro {q("tu22", "idonea documentazione")}.
Il regolamento (art. 8-bis del DPR 394/1999, testo del 2005) parla di {q("dpr394_8bis", "un alloggio fornito")}.
Con quale documento si dimostra (l'attestato del Comune o altro) lo indica lo Sportello unico per l'immigrazione della Prefettura.</p>
{_fonte(G, "tu5bis", "tu22", "dpr394_8bis")}
<p><a href="../decreto-flussi-click-day/">Decreto flussi e click day</a></p>
</section>
<section>
<h2 id="parametri">{G.ic("lista")}I parametri: quanti metri quadri per quante persone</h2>
<p>La legge sul ricongiungimento rimanda ai requisiti del decreto del Ministro della sanità del 5 luglio 1975 (Gazzetta Ufficiale n. 190 del 18 luglio 1975). Il testo del decreto non siamo riusciti a leggerlo in una fonte ufficiale in formato testo (della Gazzetta del 1975 c'è solo l'immagine delle pagine stampate):
per questo riportiamo i numeri con le parole di due Comuni che li applicano. Il Comune di Firenze, alla domanda su quale legge si applica, risponde: {q("ida_firenze", "Decreto del Ministero della Sanità del 05/07/1975")}.</p>
<ul>
<li><strong>Superficie per persona</strong>: {q("ida_firenze", "Per ogni abitante")}.</li>
<li><strong>Stanze da letto</strong>: {q("ida_firenze", "Le stanze da letto")}.</li>
<li><strong>Soggiorno</strong>: {q("ida_firenze", "Ogni alloggio deve essere dotato")}.</li>
<li><strong>Monolocale</strong>: {q("ida_firenze", "L'alloggio monostanza")}.</li>
<li><strong>Vano utile</strong> (Firenze): {q("ida_firenze", "Un vano di altezza minima")}.</li>
<li><strong>Quale superficie si conta</strong>: {q("ida_firenze", "La superficie calpestabile")}.</li>
</ul>
{_fonte(G, "ida_firenze", "tu29")}
<h3 id="persone">Da 1 a 6 persone: la superficie minima</h3>
<p>Applicando la prima regola (14 m² per i primi 4 abitanti, 10 m² per ciascuno dei successivi) si ottiene questa tabella. È un nostro calcolo, serve per orientarsi:</p>
{tab_persone}
<p>La superficie totale da sola non basta. La Città di Torino spiega che il numero di persone si ricava {q("ida_torino_calc", "confrontando i valori")}: la superficie utile totale ({q("ida_torino_calc", "14 mq per i primi 4")})
e il numero di persone che può dormire nei singoli locali. Per un monolocale valgono i numeri propri: 28 m² per una persona, 38 m² per due. Secondo Firenze {q("ida_firenze", "Non è possibile richiedere")}.</p>
{_fonte(G, "ida_torino_calc", "ida_firenze")}
<h3 id="regionali">Parametri regionali e comunali</h3>
<p>Per la carta di soggiorno l'art. 9 rimanda alla legge regionale per gli alloggi di edilizia residenziale pubblica: i parametri cambiano da Regione a Regione e non li abbiamo letti uno per uno, quindi qui non ci sono.
Anche i Comuni hanno regole proprie: Torino parla di parametri definiti dal Comune, Firenze dei regolamenti comunali vigenti, Bologna cita tra le norme la {q("ida_bologna", "Delibera della Giunta comunale")} sui parametri edilizi minimi.
Per questo lo stesso alloggio può risultare idoneo per un numero diverso di persone in due Comuni diversi: il numero che vale è quello scritto sull'attestato.</p>
{_fonte(G, "tu9", "ida_torino", "ida_firenze", "ida_bologna")}
</section>
<section>
<h2 id="chi">{G.ic("edificio")}Chi lo rilascia e chi può chiederlo</h2>
<p><strong>Lo rilascia il Comune dove si trova l'alloggio.</strong> L'art. 29 parla di requisiti accertati dai competenti uffici comunali; il Comune di Bologna lo dice così: {q("ida_bologna", "se l'abitazione si trova in un altro comune")}.
In alternativa il regolamento ammette il certificato di idoneità igienico-sanitaria dell'ASL: chiedi allo Sportello unico se lo accetta.</p>
<p><strong>Chi può fare la domanda</strong> lo stabilisce il Comune. A Torino la presenta chi ha la disponibilità dell'alloggio: il proprietario, l'usufruttuario, {q("ida_torino", "il conduttore o il comodatario")}, con il consenso del proprietario, oppure l'assegnatario di un alloggio sociale.
A Bologna la domanda è sempre a nome della persona che ha bisogno dell'attestato, anche se la invia un'altra persona. A Napoli la domanda è compilata dal tecnico incaricato, con una delega.</p>
{_fonte(G, "tu29", "ida_bologna", "ida_torino", "ida_napoli")}
</section>
<section>
<h2 id="documenti">{G.ic("doc")}I documenti di solito richiesti</h2>
<p>Ogni Comune ha il suo elenco. Nelle cinque pagine lette tornano questi documenti:</p>
<ul>
<li><strong>documento d'identità</strong> di chi fa la domanda e, per i cittadini stranieri, il permesso di soggiorno;</li>
<li><strong>il titolo sull'alloggio</strong>: contratto di affitto o di comodato registrato, oppure atto di proprietà o visura catastale;</li>
<li><strong>il consenso del proprietario</strong> o di chi ospita, su un modulo del Comune, se chi chiede non è il proprietario;</li>
<li><strong>la planimetria catastale</strong>: a Firenze {q("ida_firenze", "planimetria catastale, aggiornata")}; a Roma, nell'avviso letto, {q("ida_roma15", "Planimetria in scala")} e {q("ida_roma15", "Visura catastale")};</li>
<li><strong>la scheda o relazione di un tecnico</strong>: a Firenze la {q("ida_firenze", "SCHEDA TECNICA DI VALUTAZIONE")}; a Torino una scheda di rilevamento tecnico ({q("ida_torino", "L'unico requisito obbligatorio")}) e l'{q("ida_torino", "esibizione delle dichiarazioni")};
a Napoli una {q("ida_napoli", "Relazione tecnica asseverata")}; a Roma una relazione tecnica {q("ida_roma15", "compilata ed asseverata")}. Bologna, nella sua scheda, non chiede la relazione di un tecnico: chiede {q("ida_bologna", "la planimetria catastale")};</li>
<li><strong>la marca da bollo</strong> e, dove previsti, i diritti di istruttoria (vedi sotto).</li>
</ul>
<p>Il compenso del tecnico non è un costo del Comune e non è in queste pagine. La Città di Torino pubblica un elenco di professionisti che hanno dichiarato la loro tariffa, ma scrive che non è obbligatorio sceglierne uno dell'elenco.</p>
{_fonte(G, "ida_firenze", "ida_torino", "ida_napoli", "ida_roma15", "ida_bologna")}
</section>
<section>
<h2 id="comuni">{G.ic("euro")}Costi, tempi e validità in 5 Comuni</h2>
<p>La tabella riporta solo quello che ogni Comune scrive sulla propria pagina ufficiale, letta il {v}. Negli altri Comuni costi, tempi e validità sono diversi: guarda il sito del tuo Comune. I tempi sono quelli dichiarati dal Comune, non una previsione.</p>
{tab_comuni}
<p class="small">Milano non è in tabella: il sito del Comune di Milano ha negato l'accesso ai nostri controlli del {v}, e qui scriviamo solo ciò che abbiamo letto nella fonte ufficiale.</p>
<h3 id="roma">Roma</h3>
<p>Roma Capitale descrive così il procedimento dei Municipi: {q("ida_roma", "Procedimento diretto ad ottenere")}. Si compila il modulo online sul sito della Prefettura di Roma: {q("ida_roma", "l'interessato inoltra la richiesta")}, poi deve {q("ida_roma", "stampare l'istanza")}.
Il termine indicato è: {q("ida_roma", "Termine 30 giorni")}. Sul ritiro: {q("ida_roma", "Non è più necessario ritirare")}. Per le pratiche di ricongiungimento familiare arriva {q("ida_roma", "anche una seconda mail")}.</p>
<p>Sui costi abbiamo letto un solo avviso di Roma Capitale, aggiornato il 6 luglio 2026, che riporta l'indirizzo PEC del protocollo del Municipio XV. Chiede di {q("ida_roma15", "apporre la marca da bollo")} e il
{q("ida_roma15", "Pagamento dei diritti di istruttoria")}. Lì la domanda si invia per PEC: {q("ida_roma15", "Non è necessario venire in Municipio")}. Chi vuole l'attestato in originale lo ritira {q("ida_roma15", "presentando un'ulteriore marca")}.
Gli altri Municipi possono avere modalità diverse: chiedi al Municipio dove si trova l'alloggio.</p>
{_fonte(G, "ida_roma", "ida_roma15")}
<h3 id="torino">Torino</h3>
<p>{q("ida_torino", "Puoi presentare la domanda unicamente")}. {q("ida_torino", "Non puoi presentare l'istanza")}. Costi: sulla domanda {q("ida_torino", "una prima marca da bollo")}; al ritiro {q("ida_torino", "una seconda marca da bollo")}.
Tempi: {q("ida_torino", "Entro 120 giorni")}; con un preavviso di rigetto della Prefettura o della Questura, {q("ida_torino", "considereremo urgente")} (10 giorni). L'attestato {q("ida_torino", "ha una validità di un anno")}, ma: {q("ida_torino", "La validità viene meno")}.
Per un nuovo attestato sullo stesso alloggio la dichiarazione che nulla è mutato {q("ida_torino", "può essere utilizzata dal tecnico")}. Il limite: {q("ida_torino", "Non è possibile ottenere l'attestazione")}.</p>
{_fonte(G, "ida_torino")}
<h3 id="napoli">Napoli</h3>
<p>Il Comune di Napoli scrive che il certificato {q("ida_napoli", "è richiesto nell'ambito")} per il lavoro subordinato o autonomo e per il ricongiungimento familiare. {q("ida_napoli", "Dal 01/02/2025")}, al nucleo di idoneità abitativa della Polizia Locale.
La domanda è una {q("ida_napoli", "Istanza redatta in bollo")}. Diritti di istruttoria: {q("ida_napoli", "Nuova istanza")}; {q("ida_napoli", "Rinnovo istanza")}; {q("ida_napoli", "Duplicato istanza")}. Il Comune chiede anche una {q("ida_napoli", "seconda imposta di bollo")}.
Tempi: {q("ida_napoli", "Il termine per il rilascio/rinnovo")}. Attenzione a come arriva agli uffici: i certificati portati dai privati allo Sportello unico o alla Questura {q("ida_napoli", "non saranno accettati")}. La pagina non spiega la sigla N.I.I.A. e aggiunge: {q("ida_napoli", "Per l'inoltro dei certificati agli Enti richiedenti")}. Come far partire questo inoltro chiedilo al nucleo della Polizia Locale: qui riportiamo solo le parole del Comune.</p>
{_fonte(G, "ida_napoli")}
<h3 id="bologna">Bologna</h3>
<p>A Bologna l'attestato si chiama idoneità abitativa e la domanda si fa online: {q("ida_bologna", "Devi avere un'identità SPID")}; chi non l'ha può far presentare la domanda a un'altra persona, con una delega, o a un CAF.
Costi: {q("ida_bologna", "Presentare domanda")}. Tempi: {q("ida_bologna", "Entro 30 giorni dalla domanda")}; se manca qualcosa {q("ida_bologna", "riceverai un'email")}.
{q("ida_bologna", "Per le richieste di rilascio urgente")} si indica nella domanda che il rilascio è urgente e si allega la richiesta scritta dell'ufficio. Validità: {q("ida_bologna", "L'attestato ha validità illimitata")}. {q("ida_bologna", "Devi aggiornarlo solo")} (per esempio un cambio di casa).</p>
{_fonte(G, "ida_bologna")}
<h3 id="firenze">Firenze</h3>
<p>{q("ida_firenze", "La domanda di Idoneità Alloggiativa")}, dal sito del Comune, con SPID, CIE o CNS. Tra gli allegati: {q("ida_firenze", "ricevuta di pagamento")}. Tempi: {q("ida_firenze", "L'attestazione viene rilasciata")}.
Validità: {q("ida_firenze", "6 mesi dalla data")}. Attenzione: {q("ida_firenze", "Nel caso la documentazione")}. Per chi chiede il ricongiungimento a Firenze, la Prefettura vuole un {q("firenze_doc", "certificato di idoneità alloggiativa rilasciato")}
e chiede di {q("firenze_doc", "allegare il file pdf originale")}.</p>
{_fonte(G, "ida_firenze", "firenze_doc")}
</section>
<section>
<h2 id="esenti">{G.ic("scudo")}Quando non serve</h2>
<div class="fatti">
{_scheda(G, "ok", "Un figlio sotto i 14 anni con un genitore", q("tu29", "Nel caso di un figlio") + ".", "tu29")}
{_scheda(G, "scudo", "Rifugiati e protezione internazionale", "Per il ricongiungimento chiesto da un rifugiato l'art. 29-bis dice: " + q("tu29bis", "Non si applicano") + " (alloggio e reddito). Per la carta di soggiorno " + q("tu9", "non è richiesta allo straniero titolare") + ".", "tu29bis", "tu9")}
{_scheda(G, "info", "Familiari di cittadini italiani o dell'Unione europea", "Il Comune di Bologna scrive: " + q("ida_bologna", "Le persone con cittadinanza") + '. Secondo la stessa scheda, ai familiari stranieri di cittadini italiani o di uno Stato UE si applica il d.lgs. 30/2007. <a href="../permesso-soggiorno-motivi-familiari/#cittadino-italiano">Familiare di cittadino italiano</a>.', "ida_bologna")}
</div>
</section>
<section>
<h2 id="domande">{G.ic("info")}Domande frequenti</h2>
{faq_html}
</section>
<section>
<h2 id="guide-famiglia">{G.ic("lista")}Le pagine collegate</h2>
<div class="griglia link3"><a href="../ricongiungimento-familiare/">{G.ic("ok")}<span>Ricongiungimento familiare<small>requisiti, nulla osta, domanda</small></span></a>
<a href="../ricongiungimento-familiare-documenti/">{G.ic("doc")}<span>Documenti<small>elenco, modelli S1, S2 e S3</small></span></a>
<a href="../reddito-ricongiungimento-familiare/">{G.ic("euro")}<span>Reddito minimo<small>tabella da 1 a 5 familiari</small></span></a>
<a href="../carta-di-soggiorno/">{G.ic("doc")}<span>Carta di soggiorno<small>requisiti, documenti, test A2</small></span></a>
<a href="../permesso-soggiorno-motivi-familiari/">{G.ic("scudo")}<span>Permesso per motivi familiari<small>durata, rinnovo, coesione familiare</small></span></a></div>
</section>
{_corpo_finale(G, "../", None)}"""
    G.pagina("idoneita-alloggiativa/index.html",
             G.titolo_pagina("Idoneità alloggiativa: certificato, costi, documenti", "Idoneità alloggiativa: certificato, costi e documenti"),
             G.descrizione_pagina("Certificato di idoneità alloggiativa: a cosa serve, metri quadri per persona, documenti, costi e tempi a Roma, Torino, Napoli, "
                                  "Bologna e Firenze.", "Certificato di idoneità alloggiativa: a cosa serve, metri quadri per persona, documenti, costi e tempi in 5 Comuni."),
             corpo, jsonld)


def genera(G):
    global GUIDE
    GUIDE = json.loads((G.DATI / "guide_cittadinanza.json").read_text(encoding="utf-8"))
    pagina_test_a2(G)
    pagina_carta(G)
    pagina_matrimonio(G)
    pagina_pratica(G)
    pagina_ricongiungimento_guida(G)
    pagina_ricongiungimento_documenti(G)
    pagina_motivi_familiari(G)
    pagina_idoneita(G)
    return list(PAGINE)


def controlli(G):
    """Ogni cifra di CIFRE deve stare nel <main> della pagina e nelle frasi citate (guide_cittadinanza.json o cittadinanza.json).
    Ogni domanda frequente del JSON-LD deve essere visibile in pagina. Si ferma al primo problema."""
    citazioni = _cit() + " " + " ".join(c["testo"] for c in G.CITT["citazioni"])
    errori = []
    for p, cifre in CIFRE.items():
        h = (G.SITO / p / "index.html").read_text(encoding="utf-8")
        main = h[h.find("<main"):h.find("</main>")]
        for in_pagina, in_fonte in cifre:
            if in_pagina not in main:
                errori.append(f"{p}: «{in_pagina}» non è più nella pagina")
            if in_fonte not in citazioni:
                errori.append(f"{p}: «{in_fonte}» non è nelle frasi citate (fonte cambiata?)")
        ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
        for q in json.loads(ld.group(1))["mainEntity"]:
            if escape(q["name"]) not in main or escape(q["acceptedAnswer"]["text"]) not in main:
                errori.append(f"{p}: domanda frequente non visibile: {q['name']}")
    # tre pagine del 14/11/2026: ogni testo tra «» è una frase citata (o un pezzo di frase citata) oppure il titolo di una fonte
    da_fonti = (_cit() + " " + " ".join(f["nome"] for f in GUIDE["fonti"].values())).lower()
    for p in RICERCHE:
        h = (G.SITO / p / "index.html").read_text(encoding="utf-8")
        main = unescape(re.sub(r"<[^>]+>", "", h[h.find("<main"):h.find("</main>")]))
        for frase in re.findall(r"«([^»]+)»", main):
            if frase.lower() not in da_fonti:
                errori.append(f"{p}: il testo tra virgolette «{frase}» non è tra le frasi citate")
    parole = json.loads((G.DATI / "parole_ricongiungimento.json").read_text(encoding="utf-8"))["parole"]
    parole = {**parole, **json.loads((G.DATI / "parole_idoneita.json").read_text(encoding="utf-8"))["parole"]}  # /idoneita-alloggiativa/
    for p, ricerche in RICERCHE.items():
        for r in ricerche:
            if not parole.get(r):
                errori.append(f"{p}: la ricerca «{r}» di una domanda frequente non è misurata (dati/parole_ricongiungimento.json, dati/parole_idoneita.json)")
    if errori:
        raise SystemExit("ERRORI NELLE GUIDE (genera_guide.py):\n" + "\n".join(errori))
    return len(CIFRE)
