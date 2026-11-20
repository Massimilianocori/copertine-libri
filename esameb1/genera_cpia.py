"""Pagine CPIA di EsameB1 (20/11/2026): prova di una pagina per CPIA, più l'indice /cpia/.
Idea n. 4 di studio-business/intelaiatura/fronti-2026-11-14-nostri-dati.md.

    /cpia/            indice: i CPIA con pagina, in ordine di ricerche misurate
    /cpia/<slug>/     una pagina per CPIA: nome e codice ufficiali, sedi e indirizzi, cosa offre agli stranieri
                      (corsi di italiano, test A2 della Prefettura, esami di certificazione), come iscriversi

Fonti, solo ufficiali: l'anagrafe delle scuole statali del Ministero (dati aperti, dati.istruzione.it) per nome, codice, sedi,
indirizzi ed email; il sito di ogni CPIA per tutto il resto. Ogni testo tra «» è una frase di dati/cpia.json copiata parola per
parola dalla pagina indicata, con la data di lettura. Quello che il sito del CPIA non scrive è detto in «Cosa non abbiamo trovato»:
la pagina non deduce niente. Le sedi d'esame B1 vengono da dati/sedi.json (elenchi ufficiali degli enti, già usati dalle pagine città).
Le ricerche misurate sono in dati/parole_cpia.json: ogni titolo comincia con la ricerca misurata di quel CPIA.
Chiamato da main() di genera.py: genera(G, prossime) e controlli(G)."""
import json
import re
from html import escape, unescape

D = None       # dati/cpia.json
PAROLE = None  # dati/parole_cpia.json
PAGINE = {}    # percorso → dati della pagina, per controlli()
CLIC_LIBRO = "libro-cpia"
TEMI = [
    ("corsi", "Corsi di italiano per stranieri", "lista",
     "una frase sui corsi di italiano per stranieri (livelli A1, A2, B1)"),
    ("test_a2", "Test di italiano A2 per la carta di soggiorno", "doc",
     "una frase sul test di italiano A2 della Prefettura (permesso UE per soggiornanti di lungo periodo)"),
    ("certificazioni", "Esami di certificazione (B1 per la cittadinanza)", "ok",
     "una frase sugli esami di certificazione di italiano (CILS, CELI, PLIDA, CERT.IT)"),
    ("iscrizione", "Come iscriversi", "info",
     "una frase su come ci si iscrive"),
]
NOTA = ("Informazioni, non consulenza: questa pagina riporta i dati dell'anagrafe delle scuole del Ministero e le frasi scritte dal CPIA sul suo sito. "
        "Non siamo il CPIA e non siamo collegati alla scuola: orari, date e posti li decide la scuola. Prima di andare, controlla sul sito ufficiale o chiama la segreteria.")


# ---------------------------------------------------------------- strumenti
def bello(testo):
    """L'anagrafe scrive tutto in maiuscolo: «VIA PONTANO 43» diventa «Via Pontano 43». Le sigle restano come sono."""
    def parola(m):
        p = m.group(0)
        if p in ("CPIA", "CTP", "IC", "SMS", "IIS", "ITIS", "IPSIA", "ITC", "II", "III", "IV", "VI", "VII", "VIII", "IX", "XI", "XX", "XXV", "XXIII", "XXIV"):
            return p
        return p[0] + p[1:].lower()
    return re.sub(r"[A-Za-zÀ-ÿ]+", parola, testo).replace(" Di ", " di ").replace(" Del ", " del ").replace(" Della ", " della ") \
        .replace(" Dei ", " dei ").replace(" E ", " e ").replace("C/O", "c/o").replace("C/o", "c/o")


def volume(c):
    return PAROLE["parole"][c["ricerca"]]


def cit(c, x):
    """Frase citata. 'pubblicata_il' (sulla frase): è un avviso con una data; 'nota' (sulla frase): avvertenza nostra, per esempio
    «avviso temporaneo, può cambiare»; 'revisione' (sulla fonte): data dell'ultima revisione scritta nella pagina del CPIA."""
    f = c["fonti"][x["fonte"]]
    prima = []
    if x.get("pubblicata_il"):
        prima.append(f"Avviso del {GD(x['pubblicata_il'])}")
    if x.get("nota"):
        prima.append(escape(x["nota"][0].upper() + x["nota"][1:]))
    etichetta = f'<strong>{" · ".join(prima)}</strong> · ' if prima else ""
    rivista = f' · la pagina dice: ultima revisione {GD(f["revisione"])}' if f.get("revisione") else ""
    return (f'<blockquote style="margin:10px 0;padding:10px 14px;border-left:4px solid var(--brand);background:var(--surface);border-radius:8px;min-width:0">'
            f'<p style="margin:0 0 6px;overflow-wrap:anywhere">«{escape(x["testo"])}»</p>'
            f'<footer class="small" style="overflow-wrap:anywhere">{etichetta}Dal sito del CPIA, {"" if f["nome"] == "pagina iniziale" else "pagina "}'
            f'<a href="{escape(f["url"])}" rel="noopener">{escape(f["nome"])}</a> · letta il {GD(f["letta_il"])}{rivista}</footer></blockquote>')


def indirizzo(s):
    """Indirizzo di una sede dell'anagrafe; il CAP si scrive solo se l'anagrafe lo ha (in alcune righe è «Non Disponibile»)."""
    return f'{bello(s["indirizzo"])}, {s["cap"] + " " if s.get("cap") else ""}{bello(s["comune"])}'


def a_capo(faq_html):
    """Le risposte delle domande frequenti possono contenere indirizzi web lunghi: a 375 px devono andare a capo."""
    return faq_html.replace("<p>", '<p style="overflow-wrap:anywhere">')


def GD(iso):
    return _G.data_breve(iso)


def fonte_anagrafe(G):
    a = D["anagrafe"]
    return (f'<div class="fonte">{G.ic("doc")}<span>Fonte: <a href="{escape(a["pagina"])}" rel="noopener">{escape(a["nome"])}</a>, '
            f'anno scolastico {escape(a["anno_scolastico"])} · letta il {G.data_breve(a["letta_il"])}</span></div>')


def sedi_esame(G, c):
    """Sedi d'esame degli enti (dati/sedi.json) che portano il nome di questo CPIA: [(sede, ...)]. Si ferma se una voce non c'è più."""
    trovate = []
    for v in c.get("sedi_esame", []):
        mie = [s for s in G.sedi if s["ente"] == v["ente"] and s["nome"] == v["nome"]]
        if not mie:
            raise SystemExit(f"genera_cpia: la sede d'esame «{v['nome']}» ({v['ente']}) di {c['slug']} non è più in dati/sedi.json")
        trovate.append(mie[0])
    return trovate


def riga_sede(s):
    return (f'<tr><td>{escape(bello(s["nome"]))}<br><small>codice {escape(s["codice"])}</small></td>'
            f'<td data-l="Indirizzo">{escape(indirizzo(s))}</td>'
            f'<td data-l="Tipo">{escape(s["tipo"])}</td></tr>')


def blocco_tema(G, c, chiave, titolo, icona, cosa):
    voci = c["citazioni"].get(chiave, [])
    if voci:
        corpo = '<p>Il sito del CPIA scrive:</p>' + "".join(cit(c, x) for x in voci)
    else:
        corpo = (f'<p>Nelle pagine del sito del CPIA che abbiamo letto il {GD(c["letto_il"])} non abbiamo trovato {cosa}. '
                 f'Non vuol dire che il servizio non c\'è: chiedi alla segreteria o guarda il <a href="{escape(c["sito"])}" rel="noopener">sito ufficiale</a>.</p>')
    return f'<section><h2 id="{chiave.replace("_", "-")}">{G.ic(icona)}{titolo}</h2>{corpo}{extra_tema(G, c, chiave)}</section>'


def extra_tema(G, c, chiave):
    if chiave == "test_a2":
        return ('<p class="small">Il test A2 si prenota con una domanda alla Prefettura, non al CPIA: nella nostra guida al '
                '<a href="../../test-italiano-a2/">test di italiano A2</a> trovi come funziona e chi non deve farlo '
                '(<a href="../../esonero-test-italiano/">esonero</a>); i requisiti della <a href="../../carta-di-soggiorno/">carta di soggiorno</a> sono in un\'altra guida.</p>')
    if chiave == "certificazioni":
        mie = sedi_esame(G, c)
        citta = f'<a href="../../citta/{c["citta_slug"]}/">esame B1 per la cittadinanza a {escape(c["citta"])}</a>'
        if mie:
            voci = "".join(
                f'<li>{G.eb(s["ente"])} {escape(s["nome"])}, {escape((s.get("indirizzo") or "indirizzo non scritto").rstrip(","))}, {escape(s["citta"])} · '
                f'<a href="{escape(s["fonte"])}" rel="noopener">elenco ufficiale {escape(s["ente"])}</a>, letto il {GD(s["verificato_il"])}</li>' for s in mie)
            return (f'<p>Negli elenchi ufficiali degli enti certificatori che usiamo per le pagine città, questo CPIA compare come sede d\'esame:</p><ul>{voci}</ul>'
                    f'<p class="small">Indirizzo come scritto nell\'elenco dell\'ente: può essere diverso da quello dell\'anagrafe. '
                    f'L\'elenco dice che è una sede dell\'ente, non in quali sessioni fa l\'esame B1 per la cittadinanza: chiedilo al CPIA. '
                    f'Tutte le sedi e le prossime date: {citta}.</p>')
        return (f'<p>Negli elenchi ufficiali degli enti certificatori che usiamo per le pagine città non abbiamo trovato una sede con il nome di questo CPIA. '
                f'Le sedi e le prossime date in zona: {citta}.</p>')
    if chiave == "iscrizione":
        return (f'<p><a class="btn" href="{escape(c["sito"])}" rel="noopener">{G.ic("freccia")}Vai al sito ufficiale del CPIA</a></p>')
    return ""


def domande(G, c):
    nome = c["nome"]
    centrale = c["sedi"][0]
    n = len(c["sedi"])
    q = [(f"Dov'è la sede del {nome}?",
          f"Nell'anagrafe delle scuole del Ministero (anno scolastico {D['anagrafe']['anno_scolastico']}) la sede centrale del {nome} è in "
          f"{indirizzo(centrale)}. Il codice della scuola è {c['codice']}. "
          + (f"Le sedi aperte al pubblico sono {n} in tutto: l'elenco con gli indirizzi è in questa pagina." if n > 1 else "Nell'anagrafe non ci sono altre sedi aperte al pubblico."))]
    for chiave, domanda in (("test_a2", f"Il {nome} fa il test di italiano A2 per la carta di soggiorno?"),
                            ("certificazioni", f"Al {nome} si può fare un esame di certificazione di italiano?"),
                            ("iscrizione", f"Come ci si iscrive al {nome}?")):
        voci = [x for x in c["citazioni"].get(chiave, []) if not x.get("nota")] or c["citazioni"].get(chiave, [])
        if voci:
            q.append((domanda, f"Il sito del CPIA scrive: «{voci[0]['testo']}» (pagina letta il {GD(c['fonti'][voci[0]['fonte']]['letta_il'])})."))
        else:
            q.append((domanda, f"Nelle pagine del sito del CPIA lette il {GD(c['letto_il'])} non abbiamo trovato una frase su questo. Chiedi alla segreteria della scuola."))
    return q


# ---------------------------------------------------------------- pagine
def pagina_cpia(G, c, prossime):
    a = D["anagrafe"]
    centrale = c["sedi"][0]
    n = len(c["sedi"])
    carc = c["sedi_carcerarie"]
    dove = indirizzo(centrale)
    faq = domande(G, c)
    jsonld, faq_html = G.faq_html_e_jsonld(faq)
    faq_html = a_capo(faq_html)
    mancano = [cosa for chiave, _, _, cosa in TEMI if not c["citazioni"].get(chiave)]
    non_scritto = "".join(f"<li>{escape(x[0].upper() + x[1:])}.</li>" for x in mancano + c.get("non_scritto", []))
    temi = "".join(blocco_tema(G, c, *t) for t in TEMI)
    contatti = [("Nome ufficiale", f'{escape(c["nome_anagrafe"])}<br><small>così è scritto nell\'anagrafe del Ministero</small>'),
                ("Codice della scuola", f'{escape(c["codice"])}<br><small>codice meccanografico</small>'),
                ("Sede centrale", escape(dove)),
                ("Sito ufficiale", f'<a href="{escape(c["sito"])}" rel="noopener">{escape(G.host(c["sito"]))}</a><br><small>{escape(c["sito_nota"])}</small>')]
    if c.get("email"):
        contatti.append(("Email della scuola", f'<a href="mailto:{escape(c["email"])}">{escape(c["email"])}</a><br><small>dall\'anagrafe del Ministero</small>'))
    schede = "".join(f'<div class="fatto"><div class="f-et">{G.ic("info")}<span>{t}</span></div><p>{v}</p></div>' for t, v in contatti)
    altri = "".join(f'<a href="../{x["slug"]}/">{escape(x["nome"])}</a>' for x in D["cpia"] if x["slug"] != c["slug"])
    corpo = f"""<section class="hero">
{G.briciole(("EsameB1", "../../"), ("CPIA", "../"), (c["nome"], None))}
<span class="occhiello">{G.ic("scudo")}Anagrafe del Ministero e sito del CPIA · letti il {GD(c["letto_il"])}</span>
<h1>{escape(c["titolo_h1"])}</h1>
<p class="lead">Il {escape(c["nome"])} (nome ufficiale «{escape(c["nome_anagrafe"])}», codice {escape(c["codice"])}) ha la sede centrale in {escape(dove)}.
Nell'anagrafe delle scuole del Ministero per l'anno scolastico {escape(a["anno_scolastico"])} ha {n} {"sede aperta" if n == 1 else "sedi aperte"} al pubblico{f" e {carc} {'sede' if carc == 1 else 'sedi'} in carcere" if carc else ""}.
Qui sotto: gli indirizzi e quello che il sito del CPIA scrive, o non scrive, su corsi di italiano, test A2, esami e iscrizioni.</p>
</section>
<section>
<h2 id="scheda">{G.ic("info")}Nome, codice e contatti ufficiali</h2>
<div class="fatti">{schede}</div>
{fonte_anagrafe(G)}
</section>
<section>
<h2 id="sedi">{G.ic("edificio")}Sedi e indirizzi del {escape(c["nome"])}</h2>
<p>{"La prima riga è la sede centrale. " if n > 1 else ""}«Centro territoriale» è il nome che l'anagrafe dà alle sedi dove si fanno i corsi (spesso dentro un'altra scuola).
{f"Le {carc} sedi dentro gli istituti penitenziari non sono in elenco: non sono aperte al pubblico." if carc > 1 else ("La sede dentro l'istituto penitenziario non è in elenco: non è aperta al pubblico." if carc else "")}</p>
<div class="tab-wrap ris-tab"><table class="conf"><thead><tr><th scope="col">Sede</th><th scope="col">Indirizzo</th><th scope="col">Tipo</th></tr></thead>
<tbody>{"".join(riga_sede(s) for s in c["sedi"])}</tbody></table></div>
{fonte_anagrafe(G)}
<p class="small">L'anagrafe non scrive orari e telefoni delle sedi, e l'elenco può essere diverso da quello del sito del CPIA (le sedi dei corsi cambiano durante l'anno):
controlla sul <a href="{escape(c["sito"])}" rel="noopener">sito ufficiale</a> prima di andare.</p>
</section>
{temi}
{G.libro_mini("../../", CLIC_LIBRO)}
<section>
<h2 id="non-scritto">{G.ic("attenzione")}Cosa non abbiamo trovato</h2>
{f'<ul>{non_scritto}</ul><p class="small">Abbiamo letto le pagine del sito elencate qui sotto, non tutto il sito: la segreteria del CPIA ha la risposta.</p>' if non_scritto else
 '<p>Per i quattro temi di questa pagina il sito del CPIA scrive almeno una frase. Orari, date dei corsi e posti liberi cambiano: chiedili alla segreteria.</p>'}
<p class="small">Pagine del sito del CPIA lette il {GD(c["letto_il"])}: {" · ".join(f'<a href="{escape(f["url"])}" rel="noopener">{escape(f["nome"])}</a>' for f in c["fonti"].values())}.</p>
</section>
<div class="due">
<section>
<h2 id="date">{G.ic("cal")}Le prossime date dell'esame B1 per la cittadinanza</h2>
{G.lista_sessioni(prossime[:6], con_filtri=False)}
<p><a href="../../citta/{c["citta_slug"]}/">Esame B1 per la cittadinanza a {escape(c["citta"])}: sedi e date</a> · <a href="../../#date">Tutte le date</a> ·
<a href="../../costo/">Quanto costa</a> · <a href="../../esempi/">Prove d'esempio ufficiali</a></p>
</section>
<aside>{G.modulo(c["citta"])}</aside>
</div>
<section>
<h2 id="domande">{G.ic("info")}Domande frequenti</h2>
{faq_html}
</section>
<section>
<p class="small">{NOTA}</p>
<h2>{G.ic("lista")}Altri CPIA</h2>
<div class="altre"><a href="../">Tutti i CPIA con pagina</a>{altri}</div>
<h2>{G.ic("info")}Altre guide</h2>
{G.link_guide("../../")}
</section>"""
    percorso = f"cpia/{c['slug']}/index.html"
    G.pagina(percorso, c["titolo"], c["descrizione"], corpo, jsonld)
    PAGINE[percorso] = c


def pagina_indice(G, prossime):
    a = D["anagrafe"]
    ordinati = sorted(D["cpia"], key=lambda c: (-volume(c), c["nome"]))
    si = lambda c, k: "scritto sul sito" if c["citazioni"].get(k) else "non trovato sul sito"

    def esami(c):
        enti = sorted({v["ente"] for v in c.get("sedi_esame", [])})
        return si(c, "certificazioni") + (f'<br><small>in elenco {"/".join(enti)}</small>' if enti else "")
    righe = "".join(
        f'<tr><td><a href="{c["slug"]}/"><strong>{escape(c["nome"])}</strong></a><br><small>codice {escape(c["codice"])}</small></td>'
        f'<td data-l="Sede centrale">{escape(bello(c["sedi"][0]["comune"]))}<br><small>{len(c["sedi"])} {"sede" if len(c["sedi"]) == 1 else "sedi"} in anagrafe</small></td>'
        f'<td data-l="Test A2">{si(c, "test_a2")}</td><td data-l="Esami di certificazione">{esami(c)}</td></tr>' for c in ordinati)
    faq = [("Che cos'è un CPIA?",
            "CPIA vuol dire Centro provinciale per l'istruzione degli adulti: è una scuola statale per adulti. "
            f"Nell'anagrafe delle scuole statali del Ministero per l'anno scolastico {a['anno_scolastico']} i CPIA sono {a['n_cpia']}, ognuno con il suo codice e con più sedi."),
           ("Come trovo il CPIA vicino a me?",
            f"In questa pagina ci sono i {len(ordinati)} CPIA più cercati, con tutte le sedi e gli indirizzi dell'anagrafe del Ministero. "
            "Per gli altri CPIA puoi cercare la scuola nel portale del Ministero «Scuola in Chiaro» o chiedere al tuo Comune."),
           ("Al CPIA si fa il test di italiano A2 per la carta di soggiorno?",
            "Il test A2 si prenota con una domanda alla Prefettura, che poi comunica dove e quando farlo. Molti CPIA scrivono sul loro sito che il test si svolge nelle loro sedi: "
            "nella tabella vedi per quali CPIA abbiamo trovato la frase, e nella pagina di ogni CPIA la leggi parola per parola."),
           ("Al CPIA si può fare l'esame B1 per la cittadinanza?",
            "Solo se quel CPIA è sede d'esame di uno degli enti certificatori (CILS, CELI, PLIDA, CERT.IT). Nella pagina di ogni CPIA trovi quello che scrive la scuola "
            "e le sedi che compaiono negli elenchi ufficiali degli enti.")]
    jsonld, faq_html = G.faq_html_e_jsonld(faq)
    faq_html = a_capo(faq_html)
    corpo = f"""<section class="hero">
{G.briciole(("EsameB1", "../"), ("CPIA", None))}
<span class="occhiello">{G.ic("scudo")}Anagrafe del Ministero e siti dei CPIA · letti il {GD(D["letto_il"])}</span>
<h1>CPIA: sedi, corsi di italiano, test A2 ed esami in {len(ordinati)} città</h1>
<p class="lead">Per {len(ordinati)} CPIA (Centri provinciali per l'istruzione degli adulti) trovi qui il nome e il codice ufficiali, tutte le sedi con l'indirizzo,
quello che la scuola scrive su corsi di italiano per stranieri, test A2 ed esami di certificazione, e come iscriversi.
I dati vengono dall'anagrafe delle scuole del Ministero (anno scolastico {escape(a["anno_scolastico"])}) e dal sito di ogni CPIA, letti il {GD(D["letto_il"])}.</p>
</section>
<section>
<h2 id="elenco">{G.ic("lista")}I CPIA con una pagina</h2>
<div class="tab-wrap ris-tab"><table class="conf"><thead><tr><th scope="col">CPIA</th><th scope="col">Sede centrale</th><th scope="col">Test A2</th><th scope="col">Esami di certificazione</th></tr></thead>
<tbody>{righe}</tbody></table></div>
{fonte_anagrafe(G)}
<p class="small">«Scritto sul sito» vuol dire che abbiamo trovato una frase sul sito del CPIA e la riportiamo nella sua pagina. «Non trovato sul sito» non vuol dire che il servizio non c'è.
«In elenco CILS/CELI/PLIDA» vuol dire che una sede con il nome di quel CPIA è nell'elenco ufficiale delle sedi d'esame di quell'ente.
Per ora {len(ordinati)} CPIA su {a["n_cpia"]}: abbiamo cominciato da quelli più cercati.</p>
</section>
{G.libro_mini("../", CLIC_LIBRO)}
<div class="due">
<section>
<h2 id="date">{G.ic("cal")}Le prossime date dell'esame B1 per la cittadinanza</h2>
{G.lista_sessioni(prossime[:6], con_filtri=False)}
<p><a href="../#date">Tutte le date</a> · <a href="../#citta">Le sedi d'esame città per città</a> · <a href="../test-italiano-a2/">Il test di italiano A2</a></p>
</section>
<aside>{G.modulo()}</aside>
</div>
<section>
<h2 id="domande">{G.ic("info")}Domande frequenti</h2>
{faq_html}
</section>
<section>
<p class="small">{NOTA}</p>
<h2>{G.ic("info")}Altre guide</h2>
{G.link_guide("../")}
</section>"""
    G.pagina("cpia/index.html", "CPIA: sedi, corsi di italiano e test A2 città per città",
             f"CPIA: per {len(ordinati)} centri nome e codice ufficiali, sedi e indirizzi, corsi di italiano, test A2, esami e iscrizione. Dati del Ministero e dei siti dei CPIA.",
             corpo, jsonld)


# ---------------------------------------------------------------- dati, generazione, controlli
_G = None


def carica(G):
    global D, PAROLE, _G
    _G = G
    D = json.loads((G.DATI / "cpia.json").read_text(encoding="utf-8"))
    PAROLE = json.loads((G.DATI / "parole_cpia.json").read_text(encoding="utf-8"))


def controlli_dati(G):
    """Prima di scrivere le pagine: i dati di dati/cpia.json sono completi e coerenti. Si ferma con l'elenco dei problemi."""
    e = []
    a = D["anagrafe"]
    for k in ("pagina", "file", "nome", "anno_scolastico", "letta_il", "n_cpia"):
        if not a.get(k):
            e.append(f"anagrafe: manca «{k}»")
    if not a.get("pagina", "").startswith("https://dati.istruzione.it/"):
        e.append("anagrafe: la fonte non è dati.istruzione.it")
    slug_citta = {c["slug"] for c in G.citta}
    visti = set()
    for c in D["cpia"]:
        p = c.get("slug", "?")
        for k in ("slug", "codice", "nome", "nome_anagrafe", "citta", "citta_slug", "ricerca", "sito", "sito_nota", "letto_il", "titolo", "titolo_h1", "descrizione", "sedi", "fonti", "citazioni"):
            if c.get(k) in (None, "", [], {}) and k != "citazioni":
                e.append(f"{p}: manca «{k}»")
        if p in visti or c["codice"] in visti:
            e.append(f"{p}: slug o codice doppio")
        visti |= {p, c["codice"]}
        if not re.fullmatch(r"[A-Z]{2}MM[0-9A-Z]{6}", c["codice"]):
            e.append(f"{p}: codice «{c['codice']}» non è un codice meccanografico di CPIA")
        if c["sedi"][0]["codice"] != c["codice"] or c["sedi"][0]["tipo"] != "sede centrale":
            e.append(f"{p}: la prima sede non è la sede centrale")
        for s in c["sedi"]:
            if not all(s.get(k) for k in ("codice", "nome", "indirizzo", "comune", "tipo")) or not re.fullmatch(r"\d{5}|", s.get("cap", "?")):
                e.append(f"{p}: sede incompleta o CAP non valido {s.get('codice')}")
            if "CARCER" in (s["nome"] + " " + s["indirizzo"]).upper():
                e.append(f"{p}: la sede {s['codice']} è in un carcere: non va tra le sedi aperte al pubblico")
        if c["citta_slug"] not in slug_citta:
            e.append(f"{p}: non esiste la pagina città «{c['citta_slug']}»")
        if not PAROLE["parole"].get(c["ricerca"]):
            e.append(f"{p}: la ricerca «{c['ricerca']}» non è misurata con volume maggiore di 0 (dati/parole_cpia.json)")
        if not c["titolo"].lower().startswith(c["ricerca"].lower()):
            e.append(f"{p}: il titolo non comincia con la ricerca misurata «{c['ricerca']}»")
        for tema, parola in (("test_a2", "test A2"), ("certificazioni", "esami"), ("corsi", "corsi di italiano"), ("iscrizione", "iscrizioni")):
            if not c["citazioni"].get(tema) and any(parola in c[k] for k in ("titolo", "titolo_h1", "descrizione")):
                e.append(f"{p}: titolo o descrizione promettono «{parola}» ma sul sito del CPIA non abbiamo trovato una frase")
        if not c["sito"].startswith("https://") or not c.get("codice_sul_sito"):
            e.append(f"{p}: sito non https o codice della scuola non ritrovato sul sito")
        for k, f in c["fonti"].items():
            if not f.get("url", "").startswith("https://") or not f.get("nome") or not re.fullmatch(r"\d{4}-\d\d-\d\d", f.get("letta_il", "")):
                e.append(f"{p}: fonte «{k}» senza indirizzo, nome o data di lettura")
            elif (G.host(f["url"]).removeprefix("www.") != G.host(c["sito"]).removeprefix("www.")
                  # alcuni CPIA tengono pagine su Google Sites dentro il loro dominio: sites.google.com/<dominio del CPIA>/...
                  and not f["url"].startswith("https://sites.google.com/" + G.host(c["sito"]).removeprefix("www.") + "/")):
                e.append(f"{p}: la fonte «{k}» non è sul sito del CPIA")
        for tema, voci in c["citazioni"].items():
            if tema not in {t[0] for t in TEMI}:
                e.append(f"{p}: tema sconosciuto «{tema}»")
            for x in voci:
                if x.get("pubblicata_il") and not re.fullmatch(r"\d{4}-\d\d-\d\d", x["pubblicata_il"]):
                    e.append(f"{p}: data dell'avviso non valida: {x['pubblicata_il']}")
                if x["testo"].rstrip().endswith(":"):
                    e.append(f"{p}: citazione che finisce con i due punti (frase a metà): {x['testo'][:50]}")
                if x["fonte"] not in c["fonti"] or len(x["testo"]) < 25 or "«" in x["testo"] or "»" in x["testo"]:
                    e.append(f"{p}: citazione senza fonte, troppo corta o con virgolette: {x['testo'][:50]}")
    if e:
        raise SystemExit("ERRORI NEI DATI DEI CPIA (dati/cpia.json):\n" + "\n".join(e))


def genera(G, prossime):
    carica(G)
    controlli_dati(G)
    PAGINE.clear()
    pagina_indice(G, prossime)
    urls = ["cpia/"]
    for c in D["cpia"]:
        pagina_cpia(G, c, prossime)
        urls.append(f"cpia/{c['slug']}/")
    return urls


def controlli(G):
    """Sulle pagine scritte: ogni testo tra «» è una frase citata di quel CPIA (o il suo nome ufficiale); ogni citazione e ogni sede
    dell'anagrafe sono in pagina; codice, fonte e data ci sono; il riquadro del libro ha l'etichetta giusta e nessun link sponsorizzato
    è stato aggiunto; le domande del JSON-LD sono visibili. Si ferma al primo problema."""
    e = []
    for percorso, c in PAGINE.items():
        h = (G.SITO / percorso).read_text(encoding="utf-8")
        main = h[h.find("<main"):h.find("</main>")]
        testo = re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", main)))
        ammesse = {x["testo"] for voci in c["citazioni"].values() for x in voci} | {c["nome_anagrafe"], "Centro territoriale"}
        for frase in re.findall(r"«([^»]+)»", testo):
            if frase not in ammesse:
                e.append(f"{percorso}: il testo tra virgolette «{frase[:60]}» non è tra le frasi citate")
        for voci in c["citazioni"].values():
            for x in voci:
                if re.sub(r"\s+", " ", x["testo"]) not in testo:
                    e.append(f"{percorso}: citazione non in pagina: {x['testo'][:60]}")
        for s in c["sedi"]:
            if s["codice"] not in testo or s["cap"] not in testo or "Non Disponibile" in testo:
                e.append(f"{percorso}: sede {s['codice']} non in pagina")
        t = unescape(re.search(r"<title>(.*?)</title>", h, re.S).group(1))
        if not t.lower().startswith(c["ricerca"].lower()):
            e.append(f"{percorso}: il titolo non comincia con «{c['ricerca']}»")
        if c["codice"] not in testo or "dati.istruzione.it" not in main or G.data_breve(D["anagrafe"]["letta_il"]) not in testo:
            e.append(f"{percorso}: manca il codice, la fonte del Ministero o la data di lettura")
        libro = re.findall(r'<a [^>]*data-libro-proprio="si"[^>]*>', main)
        if not libro or any(f'data-goatcounter-click="esameb1.eu/clic/{CLIC_LIBRO}"' not in x for x in libro):
            e.append(f"{percorso}: riquadro del libro assente o con un'altra etichetta")
        if "sponsored" in main:
            e.append(f"{percorso}: link sponsorizzato in una pagina CPIA (non previsto)")
        ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
        for q in json.loads(ld.group(1))["mainEntity"]:
            if escape(q["name"]) not in main or escape(q["acceptedAnswer"]["text"]) not in main:
                e.append(f"{percorso}: domanda frequente non visibile: {q['name']}")
    indice = (G.SITO / "cpia" / "index.html").read_text(encoding="utf-8")
    for c in D["cpia"]:
        if f'href="{c["slug"]}/"' not in indice or c["codice"] not in indice:
            e.append(f"cpia/index.html: manca {c['slug']}")
    if e:
        raise SystemExit("ERRORI NELLE PAGINE CPIA (genera_cpia.py):\n" + "\n".join(e))
    return len(PAGINE)
