"""Quattro guide del 13/11/2026 (ricerca delle parole chiave: studio-business/intelaiatura/esameb1-parole-2026-11-13.md):

    /test-italiano-a2/            test di italiano A2 per il permesso UE di lungo periodo (domanda, prove, esito)
    /carta-di-soggiorno/          permesso UE per soggiornanti di lungo periodo (requisiti, documenti, costi, rinnovo)
    /cittadinanza-per-matrimonio/ cittadinanza per matrimonio (art. 5 legge 91/1992, B1, domanda, tempi)
    /pratica-cittadinanza/        stato della pratica (K10), decreto (SEND) e giuramento

Solo fatti letti nelle fonti ufficiali di dati/guide_cittadinanza.json (frasi controllate dal vivo con
raccolta/guide.py) e nei dati già controllati del sito (cittadinanza.json, ricongiungimento.json, prefetture_locali.json).
Le domande frequenti usano solo ricerche misurate (campo «ricerca» in FAQ, con il volume mensile in Italia del 13/11/2026).
Chiamato da main() di genera.py: genera(G) scrive le pagine e restituisce gli URL per la sitemap; controlli(G) ferma la
generazione se una cifra della pagina non è più nelle frasi citate."""
import json
import re
from decimal import Decimal
from html import escape

GUIDE = None  # dati/guide_cittadinanza.json, letto in genera()

PAGINE = ["test-italiano-a2/", "carta-di-soggiorno/", "cittadinanza-per-matrimonio/", "pratica-cittadinanza/"]

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
}


def _cit(fonte=None):
    return " ".join(c["testo"] for c in GUIDE["citazioni"] if fonte is None or c["fonte"] == fonte)


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
<a href="../esempi/">prove d'esempio ufficiali degli enti certificatori</a>: sono di livello B1, quindi più difficili dell'A2, e per ogni prova trovi i tempi.</p>
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
{_scheda(G, "edificio", "Un alloggio idoneo", "Un alloggio nei parametri della legge regionale per l'edilizia residenziale pubblica, oppure con l'idoneità igienico-sanitaria accertata dall'ASL. Il Portale Immigrazione chiede la fotocopia del certificato di idoneità alloggiativa nelle domande con i figli minori. Ai titolari di protezione internazionale la documentazione sull'alloggio non è richiesta. Nel testo dell'art. 9 l'alloggio è scritto insieme al reddito per i familiari: se chiedi il permesso solo per te, chiedi alla Questura se vuole questo documento.", "tu9", "portale_imm")}
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


def genera(G):
    global GUIDE
    GUIDE = json.loads((G.DATI / "guide_cittadinanza.json").read_text(encoding="utf-8"))
    pagina_test_a2(G)
    pagina_carta(G)
    pagina_matrimonio(G)
    pagina_pratica(G)
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
    if errori:
        raise SystemExit("ERRORI NELLE GUIDE DEL 13/11:\n" + "\n".join(errori))
    return len(CIFRE)
