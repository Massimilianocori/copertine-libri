"""Prove d'esempio ufficiali per livello e per esame, dentro /esempi/ (25/11/2026).
Candidati n. 1-5 di studio-business/ricerca-2026-11-25-asset.md (parte 1.5).

    /esempi/cils-b1-standard/    i file ufficiali del CILS B1 standard (UNO-B1) e le differenze dal CILS B1 Cittadinanza
    /esempi/a1/  /esempi/c1/  /esempi/c2/    i file ufficiali di CILS e PLIDA e le pagine ufficiali CERT.IT, livello per livello

Stesso schema di /esempi/cils/ e /esempi/b2/: una frase d'apertura con il dato, la fonte e la data del controllo, poi la tabella dei
file (ente, esame, parte, formato, link), poi «cosa farne». Solo link: i file restano sui siti degli enti. I dati sono in
dati/esempi_livelli.json (file aperti uno per uno il 25/11/2026) e li ricontrolla raccolta/esempi_livelli.py. Ogni testo tra «» è una
frase di quel file presa con Q() parola per parola, oppure il nome di una fonte. CELI: le pagine del CVCL (cvcl.unistrapg.it) sono
lette e linkate, ma i file stanno su www.unistrapg.it, che dal nostro server dà un errore di certificato: non li abbiamo aperti,
quindi niente link diretti e niente descrizione del contenuto (la pagina lo dice).
CERT.IT: nessun link diretto ai file (note legali di Roma Tre sul deep linking), solo la pagina ufficiale.
Riquadro del libro: in alto solo nella pagina del B1 standard (contesto B1 e cittadinanza); in A1, C1 e C2 in basso, dopo la frase
che rimanda alle prove B1. Etichetta dei clic: esameb1.eu/clic/libro-livelli, solo per queste 4 pagine.

26/11/2026 (scheda studio-business/schede/2026-11-26-esameb1-ascolto-orale.md): due pagine sul B1 per la cittadinanza, stesso schema.
    /esempi/ascolto/        i file ufficiali della prova di ascolto dei 4 esami B1 (audio MP3, domande, trascrizioni, chiavi)
    /esempi/prova-orale/    cosa chiede l'orale di ogni ente, parte per parte, con i file ufficiali (tracce, criteri, specifiche)
Gruppi «asc_*» e «ora_*» di dati/esempi_livelli.json, con la loro data di controllo («verificato_il_prove»: file aperti il 26/11/2026).
Riquadro del libro subito sotto il titolo, etichette dei clic esameb1.eu/clic/libro-ascolto e esameb1.eu/clic/libro-orale.
CELI: link diretto solo al file servito da cvcl.unistrapg.it (esempio 2); i file su www.unistrapg.it non li abbiamo aperti.

26/11/2026 (scheda studio-business/schede/2026-11-26-esameb1-celi2.md): /esempi/celi-2/, i file che il CVCL elenca per il CELI 2 (B1)
e per il CELI 2 i cittadinanza (B1), uno per uno. Stessa data di controllo («verificato_il_prove»), gruppi «c2_*» e lo zip di «asc_celi2».
Link diretti solo ai 3 file serviti da cvcl.unistrapg.it (lo zip dell'esempio 2 del CELI 2 i, scaricato intero e aperto, e le due guide
del pre-test online); i 18 file su www.unistrapg.it non li abbiamo aperti e la pagina lo scrive riga per riga. Etichetta dei clic:
esameb1.eu/clic/libro-celi2.
Chiamato da main() di genera.py: genera(G, prossime) e controlli(G)."""
import json
import re
from html import escape, unescape

D = None  # dati/esempi_livelli.json
PAGINE = []  # percorsi generati, per controlli()
CLIC_LIBRO = "libro-livelli"  # etichetta propria delle 4 pagine (decisione del 25/11/2026), per misurarle a parte da /esempi/
CLIC_PAGINA = {"esempi/ascolto/": "libro-ascolto", "esempi/prova-orale/": "libro-orale", "esempi/celi-2/": "libro-celi2"}  # 26/11/2026: un'etichetta per pagina
DATA = "verificato_il"  # chiave della data di controllo usata da V(): le pagine del 26/11/2026 usano «verificato_il_prove»
NOTA = ("Informazioni, non consulenza: questa pagina riporta quello che gli enti pubblicano sulle loro pagine ufficiali. "
        "I file sono degli enti e sono protetti dal diritto d'autore: scaricali per studiare, non ricaricarli su altri siti.")


# ---------------------------------------------------------------- strumenti
def Q(k, inizio):
    """Frase citata parola per parola dalla fonte k: quella che comincia con «inizio». Se non c'è più, la generazione si ferma."""
    trovate = [c["testo"] for c in D["citazioni"] if c["fonte"] == k and c["testo"].lower().startswith(inizio.lower())]
    if len(trovate) != 1:
        raise SystemExit(f"genera_livelli: citazione di «{k}» che comincia con «{inizio}»: trovate {len(trovate)}")
    return "«" + escape(trovate[0].replace('"', "")) + "»"


def A(k, testo=None):
    f = D["fonti"][k]
    return f'<a href="{escape(f["url"])}" rel="noopener">{escape(testo or f["nome"])}</a>'


def V(G):
    return G.data_breve(D[DATA])


def fonte(G, *chiavi):
    una = len(chiavi) == 1
    return (f'<div class="fonte">{G.ic("doc")}<span>{"Fonte" if una else "Fonti"}: {" · ".join(A(k) for k in chiavi)} · '
            f'{"letta" if una else "lette"} il {V(G)}</span></div>')


def conta(gruppo):
    """«9 file (8 PDF e 1 MP3)» per un gruppo con link diretti."""
    f = D["gruppi"][gruppo]["file"]
    per = {}
    for x in f:
        per[x["formato"]] = per.get(x["formato"], 0) + 1
    parti = [f"{per[k]} {k}" for k in ("ZIP", "PDF", "MP3") if k in per]
    return f"{len(f)} file ({' e '.join(parti)})"


def righe_file(G, gruppo):
    """Le righe della tabella dei file di un gruppo: ente, esame, parte, formato, link."""
    g = D["gruppi"][gruppo]
    righe = []
    for f in g["file"]:
        dim = f.get("dim") or ((f'{f["numero"]} file' if f.get("numero") else "") if not f.get("byte") else G.peso(f["byte"]))
        dettagli = " · ".join(x for x in (dim, f'{f["pagine"]} pag.' if f.get("pagine") else "", f.get("durata", "")) if x)
        if g.get("link_diretti", True):
            link = f'<a href="{escape(f["url"])}" rel="noopener" data-file-ente="si">{escape(f["nome"])}</a>'
        else:
            link = f'{escape(f["nome"])}: {A(g["fonte"], "sulla pagina ufficiale " + g["ente"])}'
        righe.append(
            f'<tr><td>{G.eb(g["ente"])}</td><td data-l="Esame">{escape(g["esame"])}</td>'
            f'<td data-l="Parte">{escape(f["parte"])}</td>'
            f'<td data-l="Formato"><strong>{f["formato"]}</strong>{" · " + escape(dettagli) if dettagli else ""}</td>'
            f'<td data-l="File">{link}<span class="cosa">{escape(f["contenuto"][0].upper() + f["contenuto"][1:])}.</span></td></tr>')
    return "".join(righe)


def tabella_file(G, *gruppi, nota_celi=None, nota_certit=None):
    diretti = [x for x in gruppi if D["gruppi"][x].get("link_diretti", True)]
    n = sum(len(D["gruppi"][x]["file"]) for x in diretti)
    siti = list(dict.fromkeys(G.host(f["url"]) for x in diretti for f in D["gruppi"][x]["file"]))
    siti = " e ".join(siti) if len(siti) < 3 else ", ".join(siti[:-1]) + " e " + siti[-1]
    senza = {D["gruppi"][x]["ente"] for x in gruppi if not D["gruppi"][x].get("link_diretti", True)}
    # 26/11/2026 (revisione, deviazione autorizzata): anche in A1, C1 e C2 la frase delle note legali citata parola per parola
    nota_senza = (nota_certit or nota_certit_prove()) if "CERT.IT" in senza else ""
    nota_senza += (nota_celi or " Per CELI il link porta alla pagina del CVCL: i file stanno su www.unistrapg.it, che dal nostro server non si è aperto "
                   "(errore di certificato), e non mettiamo link a file che non abbiamo aperto.") if "CELI" in senza else ""
    return ('<div class="tab-wrap ris-tab liv-tab"><table class="conf"><thead><tr><th scope="col">Ente</th><th scope="col">Esame</th>'
            '<th scope="col">Parte</th><th scope="col">Formato</th><th scope="col">File ufficiale</th></tr></thead>'
            f'<tbody>{"".join(righe_file(G, x) for x in gruppi)}</tbody></table></div>'
            f'<div class="fonte">{G.ic("ok")}<span>Link controllati il {V(G)}: {"gli" if n in (8, 11) else "i"} {n} file con link diretto si aprono {"sui siti" if "," in siti else "sul sito"} {escape(siti)} '
            f'(stato 200), con il formato e la dimensione indicati.{nota_senza}</span></div>')


def scheda(G, s, titolo, corpo, fonte_k, bottone=None, ancora=None):
    return (f'<div class="es-card es-{s.replace(".", "")}" id="{ancora or G.SLUG_ENTE[s]}"><h3>{G.eb(s)} {escape(titolo)}</h3>{corpo}'
            f'<p><a class="btn btn-2" href="{escape(D["fonti"][fonte_k]["url"])}" rel="noopener">{G.ic("freccia")}{escape(bottone or "Pagina ufficiale " + s)}</a></p></div>')


def scheda_celi(G, corpo, *chiavi, bottone="Pagina ufficiale CELI (CVCL)"):
    """CELI: quello che la pagina del CVCL elenca, con il link alla pagina. I file non li abbiamo aperti: nessun link diretto."""
    v_b1 = G.data_breve(G.v_esempi(G.ES["CELI"]))
    return scheda(G, "CELI", corpo[0],
                  f"<p>{corpo[1]}</p>"
                  '<p class="ris-nota">I file stanno sul sito www.unistrapg.it, che dal nostro server non si è aperto (errore di certificato): '
                  "non li abbiamo aperti, quindi qui c'è solo il link alla pagina ufficiale del CVCL, dove li scarichi. "
                  f'L\'esempio CELI di livello B1, controllato il {v_b1}, è nella pagina <a href="../celi/">CELI 2 i cittadinanza</a>.</p>'
                  f"{fonte(G, *chiavi)}", chiavi[0], bottone)


def come_usare(G, extra=""):
    return f"""<section>
<h2 id="come-usare">{G.ic("matita")}Cosa farne</h2>
<ol class="passi">
<li><div><strong>Capisci se è il tuo livello</strong><p>Il Centro CILS scrive delle sue prove: {Q('cils_esempi', 'Puoi utilizzare queste prove')}</p></div></li>
<li><div><strong>Fai la prova intera con i tempi scritti nei file</strong><p>Stampa il quaderno, fai partire l'audio e non fermarlo. Poi correggi con le soluzioni, dove ci sono.</p></div></li>
<li><div><strong>Scrittura e orale: non c'è una risposta giusta</strong><p>I criteri di valutazione dicono come si danno i punti, ma il tuo testo non lo corregge nessun file: fallo leggere a un insegnante.</p></div></li>
</ol>
<p class="ris-nota">Un esempio non è l'esame: le prove cambiano a ogni sessione. Serve a capire il tipo di domande, i tempi e i punti.{extra}</p>
</section>"""


def libro_basso(G):
    """A1, C1, C2: il libro è sul B1. In basso, dopo una frase che lo dice."""
    return f"""<section>
<h2 id="b1">{G.ic("libro")}Ti serve il B1 per la cittadinanza?</h2>
<p>Per la cittadinanza italiana serve il livello B1, non questo. <a href="../">Le prove d'esempio B1 dei 4 enti</a> · <a href="../cils/">CILS B1 Cittadinanza: i file</a>.
Il nostro libro è sul B1:</p>
{G.libro_mini("../../", CLIC_LIBRO)}
</section>"""


def scrivi(G, slug, briciola, occhiello, h1, lead, bottoni, blocchi, domande, altri, titolo, desc, prossime,
           nota_date="Le date degli altri livelli sono nei calendari ufficiali degli enti."):
    jsonld, faq_html = G.faq_html_e_jsonld(domande)
    corpo = f"""<section class="hero">
{G.briciole(("EsameB1", "../../"), ("Prove d'esempio", "../"), (briciola, None))}
<span class="occhiello">{G.ic("libro")}{occhiello} · controllato il {V(G)}</span>
<h1>{escape(h1)}</h1>
<p class="lead">{lead}</p>
<div class="azioni">{bottoni}</div>
</section>
{blocchi}
<div class="due">
<section>
<h2 id="date">{G.ic("cal")}Le prossime date dell'esame B1</h2>
{G.lista_sessioni(prossime[:4], con_filtri=False)}
<p><a href="../../#date">Tutte le date B1</a>. {nota_date}</p>
</section>
<aside>{G.modulo()}</aside>
</div>
<section>
<h2 id="domande">{G.ic("info")}Domande frequenti</h2>
{faq_html}
</section>
<section>
<p class="small">{NOTA}</p>
<h2>{G.ic("libro")}Altri esempi</h2>
<div class="altre">{altri}</div>
<h2>{G.ic("info")}Altre guide</h2>
{G.link_guide("../../", salta="esempi/")}
</section>"""
    G.pagina(f"esempi/{slug}/index.html", G.titolo_pagina(*titolo), G.descrizione_pagina(*desc), corpo, jsonld)
    PAGINE.append(f"esempi/{slug}/")


ALTRI = [("../", "Prove d'esempio B1"), ("../ascolto/", "Ascolto B1: gli audio ufficiali"), ("../prova-orale/", "Prova orale B1: i file ufficiali"),
         ("../cils-b1-standard/", "CILS B1 standard"), ("../a1/", "Prove d'esempio A1"), ("../a2/", "Prove d'esempio A2"),
         ("../b2/", "Prove d'esempio B2"), ("../c1/", "Prove d'esempio C1"), ("../c2/", "Prove d'esempio C2"), ("../confronto/", "I 4 esami B1 a confronto")]


def altri(salta):
    return "".join(f'<a href="{h}">{t}</a>' for h, t in ALTRI if h != salta)


# ---------------------------------------------------------------- /esempi/cils-b1-standard/
def pagina_b1_standard(G, prossime):
    b1c = G.ES["CILS"]  # il B1 Cittadinanza: dati/esempi.json, con la sua data di controllo
    v_b1c = G.data_breve(G.v_esempi(b1c))
    prove_c = {p["nome"]: p for p in b1c["prove"]}
    lead = (f"Secondo la pagina ufficiale «Prove Liv. B1» del Centro CILS (Università per Stranieri di Siena), controllata il {V(G)}, "
            f"l'esempio d'esame del CILS B1 standard (UNO-B1) è gratis e si scarica senza registrazione: {conta('cils_b1')}, della sessione di giugno 2017. "
            'Non è il CILS B1 Cittadinanza, che è un altro esame con altri file: <a href="../cils/">i file del B1 Cittadinanza sono qui</a>.')
    differenze = [
        ("Abilità", "5: ascolto, lettura, analisi delle strutture di comunicazione (la grammatica, in una prova a parte), scrittura, orale",
         f"{len(b1c['prove'])}: ascolto, lettura con la grammatica dentro, scrittura, orale"),
        ("Punti", f"20 per abilità. {Q('cils_linee', 'Per superare una abilità')} {Q('cils_linee', 'Il punteggio totale massimo ottenibile è 100')}",
         f"{prove_c['Ascolto']['punti']} per abilità. Il minimo per la sufficienza non è scritto nelle pagine ufficiali che abbiamo letto"),
        ("Scrittura", f"2 testi in 1 ora e 10 minuti. Nell'esempio: {Q('cils_b1_ps1', 'Devi scrivere')} e {Q('cils_b1_ps2', 'Devi scrivere')}",
         f"1 email in {prove_c['Scrittura']['tempo']}: {Q('cils_b1c_sillabo', 'Da 80')}"),
        ("Tempi", "Scritti nel quaderno: lettura 50 minuti, analisi delle strutture 1 ora, scrittura 1 ora e 10 minuti. La durata dell'ascolto non è scritta nel quaderno",
         f"Scritti nel sillabo: ascolto {prove_c['Ascolto']['tempo']}, lettura e grammatica {prove_c['Lettura e grammatica']['tempo']}, scrittura {prove_c['Scrittura']['tempo']}"),
        ("Se non superi una parte", f"Rifai solo le abilità non superate. La pagina «La valutazione» scrive: {Q('cils_valutazione', 'Entro 18 mesi')} "
         f"Le Linee guida scrivono invece: {Q('cils_linee', 'Le abilità capitalizzate')} Chiedi alla sede quale termine vale",
         f"Rifai tutto l'esame. La pagina ufficiale scrive: {Q('cils_b1c', 'Per questo livello')}"),
        ("File d'esempio", f"{conta('cils_b1')}, sessione di giugno 2017", f'{len(b1c["file"])} file; il quaderno è un prototipo: <a href="../cils/">vai ai file</a>'),
    ]
    tab_diff = ('<div class="tab-wrap ris-tab"><table class="conf"><thead><tr><th scope="col">Cosa cambia</th><th scope="col">CILS B1 standard (UNO-B1)</th>'
                '<th scope="col">CILS B1 Cittadinanza</th></tr></thead><tbody>'
                + "".join(f'<tr><td><strong>{a}</strong></td><td data-l="B1 standard">{b}</td><td data-l="B1 Cittadinanza">{c}</td></tr>' for a, b, c in differenze)
                + "</tbody></table></div>")
    blocchi = f"""{G.riquadro_libro("../../").replace("clic/libro-esempi", "clic/" + CLIC_LIBRO)}
<section>
<h2 id="file">{G.ic("archivio")}I file ufficiali del CILS B1 standard</h2>
<p class="small">Ogni link apre il file sul sito dell'Università per Stranieri di Siena: qui non copiamo niente. La pagina «Esempi prove di esami» scrive:
{Q('cils_esempi', 'puoi scaricare')}.</p>
{tabella_file(G, 'cils_b1')}
{fonte(G, 'cils_prove_b1', 'cils_esempi')}
</section>
<section class="ris-sez">
<h2 id="differenze">{G.ic("lista")}B1 standard e B1 Cittadinanza: cosa cambia</h2>
<p>Sono due esami diversi dello stesso ente e dello stesso livello. Hanno prove, punti e file d'esempio diversi: se ti alleni con l'esempio sbagliato, ti prepari a un altro esame.</p>
{tab_diff}
<div class="fonte">{G.ic("doc")}<span>Fonti: {A('cils_linee')} · {A('cils_valutazione')} · {A('cils_b1_quaderno')} · {A('cils_b1_ps1')} · {A('cils_b1_ps2')} · lette il {V(G)}.
B1 Cittadinanza: {G.link_fonti(b1c["fonti_struttura"])} · controllato il {v_b1c}</span></div>
</section>
<section>
<h2 id="quale">{G.ic("info")}Quale dei due ti serve</h2>
<p>Per la domanda di cittadinanza serve un certificato di italiano di livello B1. Il Centro CILS ha un esame fatto apposta, il B1 Cittadinanza, più corto.
Nelle sue FAQ scrive del B1: {Q('cils_faq', 'richiesto anche')}. Se ti serve il certificato solo per la cittadinanza, guarda prima il
<a href="../cils/">B1 Cittadinanza</a>. Prima di iscriverti chiedi alla sede quale dei due esami organizza e quanto costa:
<a href="../../ente/cils/">date, costo e sedi CILS</a> · <a href="../../esonero-test-italiano/">chi è esonerato dal B1</a>.</p>
{fonte(G, 'cils_faq')}
</section>
{come_usare(G, " Se poi farai il B1 Cittadinanza, allenati con il suo esempio: le prove sono diverse.")}"""
    domande = [
        ("Dove trovo le prove d'esame CILS B1 in PDF?",
         "Sulla pagina ufficiale «Prove Liv. B1» del Centro CILS (Università per Stranieri di Siena): quaderno del candidato, trascrizioni, due fogli della produzione "
         "scritta, prove di produzione orale, soluzioni, criteri di valutazione e foglio delle risposte in PDF, più l'audio dell'ascolto in MP3. Sono della sessione di giugno 2017."),
        ("Il CILS B1 standard e il CILS B1 Cittadinanza sono lo stesso esame?",
         "No. Il B1 standard ha cinque abilità da 20 punti, con una prova di grammatica a parte e due testi da scrivere. Il B1 Cittadinanza ha quattro abilità da 12 punti "
         "e una sola email. Anche i file d'esempio sono diversi: stanno su due pagine ufficiali diverse."),
        ("Quanti punti servono per superare il CILS B1 standard?",
         "Secondo le Linee guida CILS ogni abilità vale al massimo 20 punti e si supera con almeno 11; il totale massimo è 100 e il minimo 55."),
        ("Ci sono prove CILS B1 di altre sessioni?",
         "Sulle pagine ufficiali che abbiamo controllato c'è una sola sessione per livello: giugno 2017 per il B1 standard e un prototipo per il B1 Cittadinanza. "
         "Prove di altre sessioni non ci sono tra i file gratuiti."),
    ]
    scrivi(G, "cils-b1-standard", "CILS B1 standard", "Università per Stranieri di Siena",
           "CILS B1 standard: l'esempio d'esame ufficiale, PDF e audio",
           lead,
           f'<a class="btn" href="#file">{G.ic("archivio")}I {len(D["gruppi"]["cils_b1"]["file"])} file ufficiali</a>'
           f'<a class="btn btn-2" href="#differenze">{G.ic("lista")}Differenze dal B1 Cittadinanza</a>',
           blocchi, domande, altri("../cils-b1-standard/") + '<a href="../cils/">CILS B1 Cittadinanza</a>',
           ("CILS B1 standard: prove d'esame PDF e audio ufficiali", "CILS B1 standard: prove d'esame PDF e audio"),
           (f"CILS B1 standard (UNO-B1): l'esempio d'esame ufficiale gratis, {conta('cils_b1')}, sessione giugno 2017. E cosa cambia dal CILS B1 Cittadinanza.",
            "CILS B1 standard (UNO-B1): l'esempio d'esame ufficiale gratis in PDF e MP3 e cosa cambia dal CILS B1 Cittadinanza."),
           prossime)


# ---------------------------------------------------------------- /esempi/a1/, /esempi/c1/, /esempi/c2/
def pagina_livello(G, liv, prossime):
    nome = liv.upper()
    certit_nota = "Per le note legali di Roma Tre non mettiamo link diretti ai file: li scarichi dalla pagina ufficiale."
    if liv == "a1":
        gruppi = ("cils_a1", "cils_a1i", "celi_a1", "celi_a1i", "plida_a1", "certit_a1")
        lead = (f"Secondo le pagine ufficiali di CILS, CELI, PLIDA e CERT.IT, controllate il {V(G)}, le prove d'esempio ufficiali di italiano A1 di CILS, PLIDA e CERT.IT sono gratis: "
                f"CILS A1 standard {conta('cils_a1')}, CILS A1 integrazione in Italia {conta('cils_a1i')}, PLIDA A1 {conta('plida_a1')}, con l'esempio del PLIDA Juniores, "
                "CERT.IT A1 uno zip e un audio sulla pagina dell'ente; CELI Impatto: due zip linkati dal CVCL, non aperti.")
        schede = [
            scheda(G, "CILS", "CILS A1 standard e A1 integrazione in Italia",
                   f"<p>Due esami A1 diversi. A1 standard, cinque abilità da 12 punti: {Q('cils_linee', 'Per superare un’abilità')} {Q('cils_linee', 'Il punteggio totale massimo ottenibile è 60')} "
                   f"A1 integrazione in Italia, quattro abilità, senza la prova di grammatica: {Q('cils_linee', 'Per superare le abilità di comprensione')}, "
                   f"e 7 punti in lettura e in scrittura. La pagina ufficiale dell'A1 integrazione scrive: {Q('cils_prove_a1i', 'Per questo livello')} "
                   "I file dell'A1 standard sono della sessione di giugno 2017; quelli dell'A1 integrazione non hanno una data scritta. "
                   "Il Centro CILS pubblica anche gli esempi A1 bambini e A1 adolescenti: qui non li elenchiamo, li trovi dalla pagina «Esempi prove di esami».</p>"
                   f'<p><a href="{escape(D["fonti"]["cils_prove_a1i"]["url"])}" rel="noopener">Pagina ufficiale CILS A1 integrazione in Italia</a></p>'
                   f"{fonte(G, 'cils_prove_a1', 'cils_prove_a1i', 'cils_linee')}", "cils_prove_a1", "Pagina ufficiale CILS A1 standard"),
            scheda(G, "PLIDA", "PLIDA A1: c'è solo l'esempio Juniores",
                   "<p>Nella pagina «Preparati all'esame», sezione «Scarica i materiali», livello A1, la prova d'esempio è quella del PLIDA Juniores: "
                   "nello zip ci sono il quaderno di ascolto e lettura con le soluzioni, la prova di scrittura, la prova orale e l'audio. "
                   "Un esempio del PLIDA A1 non Juniores lì non c'è. I due file dei criteri di valutazione sono del PLIDA A1 (lo stesso file vale per A1 e C2).</p>"
                   f"{fonte(G, 'plida_prepara')}", "plida_prepara", "Pagina ufficiale PLIDA: Preparati all'esame"),
            scheda(G, "CERT.IT", "CERT.IT A1 (Roma Tre)",
                   f"<p>{Q('certit_a1', 'In fondo alla pagina')} {Q('certit_a1', 'Le sezioni Ascolto')} {Q('certit_a1', 'La sezione Produzione orale')} "
                   f"Per superare: {Q('certit_a1', 'L’esame è superato')}. Quota a Roma Tre: {Q('certit_iscrizione', 'A1: 35')}.</p>"
                   f'<p class="ris-nota">{certit_nota}</p>{fonte(G, "certit_a1", "certit_iscrizione")}', "certit_a1"),
            scheda_celi(G, ("CELI Impatto (A1) e CELI Impatto i (A1, immigrati)",
                            f"Il CVCL ha due esami A1. Nella pagina «Esami CELI generici»: {Q('celi_generici', 'CELI Impatto')}, con {Q('celi_generici', 'prova d')}. "
                            f"Nella pagina «Esami CELI immigrati» c'è il CELI Impatto i, pensato anche per {Q('celi_immigrati', 'migranti che')}, "
                            f"con {Q('celi_immigrati', 'prova d')}. Le due pagine elencano anche la descrizione dell'esame e i criteri di valutazione in PDF."),
                        "celi_generici", "celi_immigrati"),
        ]
        usi = ('<p>L\'A1 è il primo livello: per i documenti di soggiorno e per la cittadinanza servono livelli più alti. '
               'Per il permesso di soggiorno UE per soggiornanti di lungo periodo serve l\'A2: <a href="../a2/">prove d\'esempio A2</a> · '
               '<a href="../../test-italiano-a2/">il test di italiano A2 in Prefettura</a>. Per la cittadinanza serve il B1: <a href="../">prove d\'esempio B1</a>.</p>')
        domande = [
            ("Dove trovo un esempio dell'esame di italiano A1 in PDF?",
             "Sul sito del Centro CILS (Università per Stranieri di Siena): le pagine «Prove Liv. A1 standard» e «Prove Liv. A1 integrazione in Italia» hanno quaderno, "
             "trascrizioni, tracce di scrittura e orale, criteri e foglio delle risposte in PDF, più l'audio in MP3. La Società Dante Alighieri pubblica l'esempio "
             "del PLIDA Juniores A1, CERT.IT il suo esempio in fondo alla pagina del livello A1. Il CVCL di Perugia linka due esempi in zip del CELI Impatto."),
            ("Le prove CILS A1 hanno le soluzioni e l'audio?",
             "L'esempio CILS A1 standard sì: c'è il PDF delle soluzioni e un file audio MP3. Nell'esempio CILS A1 integrazione in Italia la pagina ufficiale elenca "
             "quaderno, audio, trascrizioni, tracce e criteri di valutazione, senza un file di soluzioni."),
            ("Quanti punti servono per superare il CILS A1?",
             "Secondo le Linee guida CILS, nell'A1 standard servono almeno 7 punti su 12 in ogni abilità. Nel modulo A1 per l'integrazione in Italia servono almeno "
             "10 punti in ascolto e in produzione orale e almeno 7 in lettura e in scrittura."),
            ("L'esame A1 serve per la cittadinanza o per la carta di soggiorno?",
             "No. Per la cittadinanza serve il livello B1; per il permesso di soggiorno UE per soggiornanti di lungo periodo serve il livello A2."),
        ]
        titolo = ("Esame italiano A1: prove d'esempio ufficiali, PDF e audio",)
        desc = ("Esame di italiano A1: le prove d'esempio ufficiali di CILS (16 file PDF e MP3), PLIDA Juniores, CELI Impatto e CERT.IT, con audio e soluzioni.",)
        h1 = "Esame di italiano A1: le prove d'esempio ufficiali, con PDF e audio"
        bott = "I file CILS A1"
    elif liv == "c1":
        gruppi = ("cils_c1", "celi_c1", "plida_c1", "certit_c1")
        lead = (f"Secondo le pagine ufficiali di CILS, CELI, PLIDA e CERT.IT, controllate il {V(G)}, le prove d'esempio ufficiali di italiano C1 di CILS, PLIDA e CERT.IT sono gratis: "
                f"CILS TRE-C1 {conta('cils_c1')}, PLIDA C1 {conta('plida_c1')}, CERT.IT C1 uno zip e 3 MP3 sulla pagina dell'ente; CELI 4: due zip linkati dal CVCL, non aperti.")
        schede = [
            scheda(G, "CILS", "CILS TRE-C1",
                   f"<p>Cinque abilità da 20 punti. Le Linee guida scrivono: {Q('cils_linee', 'Per superare una abilità')} {Q('cils_linee', 'Il punteggio totale massimo ottenibile è 100')} "
                   "I file sono della sessione di giugno 2017. Nel quaderno i tempi scritti sono: lettura 1 ora e 10 minuti, analisi delle strutture di comunicazione "
                   "1 ora e 15 minuti, scrittura 1 ora e 30 minuti.</p>"
                   f"{fonte(G, 'cils_prove_c1', 'cils_linee')}", "cils_prove_c1", "Pagina ufficiale CILS C1"),
            scheda(G, "PLIDA", "PLIDA C1",
                   f"<p>Il Quaderno delle specifiche scrive: {Q('plida_c1_quaderno', 'Per superare')} Chi non supera una o più abilità {Q('plida_c1_quaderno', 'possono recuperarle')}. "
                   "Nello zip della prova d'esempio ci sono il quaderno di ascolto e lettura con le soluzioni e le trascrizioni, la prova di scrittura, "
                   "la prova orale e l'audio.</p>"
                   f"{fonte(G, 'plida_prepara', 'plida_c1_quaderno')}", "plida_prepara", "Pagina ufficiale PLIDA: Preparati all'esame"),
            scheda(G, "CERT.IT", "CERT.IT C1 (Roma Tre)",
                   f"<p>{Q('certit_c1', 'In fondo alla pagina')} Lì trovi l'esempio di esame e 3 file audio della prova di ascolto. "
                   f"Per superare: {Q('certit_c1', 'L’esame è superato')}. {Q('certit_c1', 'Laddove non venissero')} "
                   f"Quota a Roma Tre: {Q('certit_iscrizione', 'C1: 200')}.</p>"
                   f'<p class="ris-nota">{certit_nota}</p>{fonte(G, "certit_c1", "certit_iscrizione")}', "certit_c1"),
            scheda_celi(G, ("CELI 4 (C1)",
                            f"Nella pagina «Esami CELI generici» il CVCL elenca: {Q('celi_generici', 'CELI 4 (')}, con {Q('celi_generici', 'prova d')}, più competenze richieste, "
                            f"struttura e descrizione della prova, facsimile del foglio delle risposte, valutazione e punteggi in PDF. Scrive anche che per l'università "
                            f"{Q('celi_generici', 'il CELI 4 e il CELI 5')}."), "celi_generici"),
        ]
        usi = ('<p>Il C1 è un livello avanzato: di solito si chiede per studio o per lavoro. Per la cittadinanza basta il B1: '
               '<a href="../">le prove d\'esempio B1</a> · <a href="../b2/">prove d\'esempio B2</a> · <a href="../../esonero-test-italiano/">quali titoli esonerano dal B1</a>.</p>')
        domande = [
            ("Dove trovo le prove d'esame CILS C1 in PDF?",
             "Sulla pagina ufficiale «Prove Liv. C1» del Centro CILS (Università per Stranieri di Siena): quaderno del candidato, trascrizioni, prove di produzione orale, "
             "soluzioni, criteri di valutazione e fogli delle risposte in PDF, più l'audio dell'ascolto in MP3. Sono della sessione di giugno 2017."),
            ("Quanti punti servono per superare il CILS C1?",
             "Secondo le Linee guida CILS ogni abilità vale al massimo 20 punti e si supera con almeno 11; il totale massimo è 100 e il minimo 55."),
            ("Quanti punti servono per superare il PLIDA C1?",
             "Secondo il Quaderno delle specifiche PLIDA C1 serve un punteggio di almeno 18 su 30 in ognuna delle quattro abilità: Ascoltare, Leggere, Scrivere e Parlare."),
            ("L'esame di italiano C1 serve per la cittadinanza?",
             "No: per la cittadinanza è richiesto il livello B1."),
        ]
        titolo = ("Esame italiano C1: prove d'esempio ufficiali, PDF e audio",)
        desc = ("Esame di italiano C1: le prove d'esempio ufficiali di CILS TRE-C1 (10 file PDF e MP3), PLIDA C1 (5 file), CELI 4 e CERT.IT C1, con audio e soluzioni.",)
        h1 = "Esame di italiano C1: le prove d'esempio ufficiali, con PDF e audio"
        bott = "I file CILS C1"
    else:
        gruppi = ("cils_c2", "celi_c2", "plida_c2", "certit_c2")
        lead = (f"Secondo le pagine ufficiali di CILS, CELI, PLIDA e CERT.IT, controllate il {V(G)}, le prove d'esempio ufficiali di italiano C2 di CILS, PLIDA e CERT.IT sono gratis: "
                f"CILS QUATTRO-C2 {conta('cils_c2')}, PLIDA C2 {conta('plida_c2')}, CERT.IT C2 uno zip e 3 MP3 sulla pagina dell'ente; CELI 5: due zip linkati dal CVCL, non aperti.")
        schede = [
            scheda(G, "CILS", "CILS QUATTRO-C2",
                   f"<p>Cinque abilità da 20 punti. Le Linee guida scrivono: {Q('cils_linee', 'Per superare una abilità')} {Q('cils_linee', 'Il punteggio totale massimo ottenibile è 100')} "
                   "I file sono della sessione di giugno 2017. Nel quaderno i tempi scritti sono: lettura 1 ora e 20 minuti, analisi delle strutture di comunicazione "
                   "1 ora e 30 minuti, scrittura 1 ora e 30 minuti.</p>"
                   f"{fonte(G, 'cils_prove_c2', 'cils_linee')}", "cils_prove_c2", "Pagina ufficiale CILS C2"),
            scheda(G, "PLIDA", "PLIDA C2",
                   "<p>Nella pagina «Preparati all'esame», sezione «Scarica i materiali», livello C2, ci sono la prova d'esempio e i due file dei criteri di valutazione "
                   "(lo stesso file vale per A1 e C2). Nello zip ci sono il quaderno di ascolto e lettura con le soluzioni, la prova di scrittura, la prova orale e l'audio. "
                   "Per il C2 non c'è un quaderno delle specifiche tra i file.</p>"
                   f"{fonte(G, 'plida_prepara')}", "plida_prepara", "Pagina ufficiale PLIDA: Preparati all'esame"),
            scheda(G, "CERT.IT", "CERT.IT C2 (Roma Tre)",
                   f"<p>In fondo alla pagina del livello C2, sotto {Q('certit_c2', 'Esempio di esame')}, trovi l'esempio di esame e 3 file audio della prova di ascolto. "
                   f"Per superare: {Q('certit_c2', 'L’esame è superato')} {Q('certit_c2', 'Laddove non venissero')} "
                   f"Quota a Roma Tre: {Q('certit_iscrizione', 'C2: 200')}.</p>"
                   f'<p class="ris-nota">{certit_nota}</p>{fonte(G, "certit_c2", "certit_iscrizione")}', "certit_c2"),
            scheda_celi(G, ("CELI 5 (C2)",
                            f"Nella pagina «Esami CELI generici» il CVCL elenca: {Q('celi_generici', 'CELI 5 (')}, con {Q('celi_generici', 'prova d')}, più competenze richieste, "
                            f"struttura e descrizione della prova, facsimile del foglio delle risposte, valutazione e punteggi in PDF. Scrive anche che per l'università "
                            f"{Q('celi_generici', 'il CELI 4 e il CELI 5')}."), "celi_generici"),
        ]
        usi = ('<p>Il C2 è il livello più alto. Per la cittadinanza basta il B1: <a href="../">le prove d\'esempio B1</a> · '
               '<a href="../c1/">prove d\'esempio C1</a> · <a href="../../esonero-test-italiano/">quali titoli esonerano dal B1</a>.</p>')
        domande = [
            ("Dove trovo le prove d'esame CILS C2 in PDF?",
             "Sulla pagina ufficiale «Prove Liv. C2» del Centro CILS (Università per Stranieri di Siena): quaderno del candidato, trascrizioni, prove di produzione orale, "
             "soluzioni, criteri di valutazione e fogli delle risposte in PDF, più l'audio dell'ascolto in MP3. Sono della sessione di giugno 2017."),
            ("Quanti punti servono per superare il CILS C2?",
             "Secondo le Linee guida CILS ogni abilità vale al massimo 20 punti e si supera con almeno 11; il totale massimo è 100 e il minimo 55."),
            ("C'è una prova d'esempio del PLIDA C2?",
             "Sì. Nella pagina «Preparati all'esame» della Società Dante Alighieri, livello C2, c'è uno zip con le prove di ascolto e lettura con le soluzioni, "
             "la prova di scrittura, la prova orale e l'audio, più i criteri di valutazione delle prove Scrivere e Parlare."),
            ("L'esame di italiano C2 serve per la cittadinanza?",
             "No: per la cittadinanza è richiesto il livello B1."),
        ]
        titolo = ("Esame italiano C2: prove d'esempio ufficiali, PDF e audio",)
        desc = ("Esame di italiano C2: le prove d'esempio ufficiali di CILS QUATTRO-C2 (10 file PDF e MP3), PLIDA C2, CELI 5 e CERT.IT C2, con audio e soluzioni.",)
        h1 = "Esame di italiano C2: le prove d'esempio ufficiali, con PDF e audio"
        bott = "I file CILS C2"
    blocchi = f"""<section>
<h2 id="file">{G.ic("archivio")}I file ufficiali {nome}, ente per ente</h2>
<p class="small">Ogni link apre il file o la pagina sul sito dell'ente: qui non copiamo niente. I file con link diretto sono gratis e li abbiamo aperti senza registrazione.</p>
{tabella_file(G, *gruppi)}
</section>
<section>
<h2 id="enti">{G.ic("lista")}Cosa scrive ogni ente</h2>
{"".join(schede)}
</section>
<section class="ris-sez">
<h2 id="a-cosa-serve">{G.ic("info")}A cosa serve il livello {nome}</h2>
{usi}
</section>
{come_usare(G)}
{libro_basso(G)}"""
    scrivi(G, liv, f"Livello {nome}", "Fonti ufficiali degli enti", h1, lead,
           f'<a class="btn" href="#file">{G.ic("archivio")}{bott}</a><a class="btn btn-2" href="../">{G.ic("libro")}Prove d\'esempio B1</a>',
           blocchi, domande, altri(f"../{liv}/"), titolo, desc, prossime)


# ---------------------------------------------------------------- /esempi/ascolto/ e /esempi/prova-orale/ (26/11/2026)
NOTA_CELI_PROVE = (" Per CELI i file che stanno su www.unistrapg.it non hanno un link diretto: dal nostro server quel sito non si apre "
                   "(errore di certificato, visto il 25 novembre 2026), il 26 novembre 2026 non li abbiamo aperti e non mettiamo link a file "
                   "che non abbiamo aperto. Li scarichi dalla pagina del CVCL.")
NOTA_DATE_B1 = 'Quando chiudono le iscrizioni: <a href="../../iscrizione/">le scadenze, ente per ente</a>.'


def nota_certit_prove():
    """26/11/2026 (revisione): la frase delle note legali di Roma Tre, citata parola per parola, al posto di «vietano i link diretti»."""
    return (f" Per CERT.IT il link porta alla pagina ufficiale, non al file: le {A('certit_note', 'note legali di Roma Tre')} scrivono "
            f"{Q('certit_note', 'È vietato il cd. deep linking')}.")


CERTIT_TAGLIATI = ("non bastano per i «25 minuti circa» del fascicolo, e i file delle prove 1 e 2 finiscono mentre l'audio è ancora in corso")


def L(gruppo, i, testo=None):
    """Link diretto al file numero i di un gruppo (solo gruppi con link diretti)."""
    f = D["gruppi"][gruppo]["file"][i]
    return f'<a href="{escape(f["url"])}" rel="noopener" data-file-ente="si">{escape(testo or f["nome"])}</a>'


def tab(colonne, righe):
    """Tabella a schede sul telefono (ris-tab): la prima cella è l'ente, le altre portano il nome della colonna."""
    return ('<div class="tab-wrap ris-tab"><table class="conf"><thead><tr>' + "".join(f'<th scope="col">{c}</th>' for c in colonne) + "</tr></thead><tbody>"
            + "".join("<tr>" + f"<td>{r[0]}</td>" + "".join(f'<td data-l="{colonne[i]}">{c}</td>' for i, c in enumerate(r) if i) + "</tr>" for r in righe)
            + "</tbody></table></div>")


def celi_non_aperti(G):
    v_b1 = G.data_breve(G.v_esempi(G.ES["CELI"]))
    return ('<p class="ris-nota">Gli altri file CELI stanno su www.unistrapg.it, che dal nostro server non si apre (errore di certificato, visto il 25 novembre 2026): '
            f"il {V(G)} non li abbiamo aperti, quindi qui non scriviamo cosa contengono. Quello che avevamo letto in quei file il {v_b1} "
            'è nella pagina <a href="../celi/">CELI 2 i cittadinanza</a>, con la sua data.</p>')


def pagina_ascolto(G, prossime):
    gr = D["gruppi"]
    mp3_cils, zip_plida, zip_celi, mp3_certit = gr["asc_cils"]["file"][0], gr["asc_plida"]["file"][0], gr["asc_celi2"]["file"][0], gr["asc_certit"]["file"][0]
    lead = (f"Secondo le pagine ufficiali di CILS, PLIDA, CELI e CERT.IT, controllate il {V(G)}, gli audio ufficiali della prova di ascolto B1 si scaricano senza registrazione: "
            f"CILS B1 Cittadinanza 1 MP3 di {mp3_cils['durata']} con quaderno, trascrizione e chiavi in PDF; PLIDA B1 1 MP3 di {zip_plida['audio_durata']} "
            f"dentro lo zip della prova d'esempio, con trascrizioni e soluzioni; CELI 2 i cittadinanza {zip_celi['audio_n']} MP3 di {zip_celi['audio_durata']} dentro lo zip dell'esempio 2, "
            "con i testi dell'ascolto e le chiavi; "
f"CERT.IT B1 {mp3_certit['numero']} MP3 di {mp3_certit['audio_durata']} ciascuno sulla pagina dell'ente, che però sono incompleti: {CERTIT_TAGLIATI}.")
    confronto = tab(("Ente", "Prove di ascolto", "Durata scritta dall'ente", "Durata dell'audio d'esempio", "Quante volte si ascolta", "Punti"), [
        (f'{G.eb("CILS")} CILS B1 Cittadinanza', f"2 prove: {Q('cils_b1c_criteri', 'Test a scelta multipla composto da 6 item')} e {Q('cils_b1c_criteri', 'Test vero/Falso composto da 12 item')}",
         f"{Q('cils_b1c_sillabo', '30 minuti circa')} nel sillabo", f"{mp3_cils['durata']} (1 file)", Q('cils_b1c_sillabo', 'I testi sono fatti ascoltare due volte'),
         f"12 in tutto: {Q('cils_b1c_criteri', 'Punteggio massimo: punti 6')} per ogni prova"),
        (f'{G.eb("PLIDA")} PLIDA B1', f"4 parti, 20 domande: {Q('plida_b1_quaderno', '5 dialoghi con narrazioni')}, {Q('plida_b1_quaderno', '4 dialoghi')}, {Q('plida_b1_quaderno', '6 testi')}, {Q('plida_b1_quaderno', '5 dialoghi contenenti')}",
         "«40 minuti circa» nel Quaderno delle specifiche", f"{zip_plida['audio_durata']} (1 file nello zip)", f"Nell'esempio: {Q('plida_b1_quaderno', 'Ascolterai ogni dialogo')}",
         f"30; servono {Q('plida_b1_quaderno', 'almeno 18/30')}"),
        (f'{G.eb("CELI")} CELI 2 i cittadinanza', f"Le prove C: {Q('celi_immigrati', 'contenuto del secondo fascicolo')}. Nell'esempio 2 sono {zip_celi['prove_n']} prove, {zip_celi['domande_n']} domande",
         "Non scritta nella pagina del CVCL né nei file dell'esempio 2", f"{zip_celi['audio_durata']} (1 file nello zip)",
         f"Due volte: lo dicono le istruzioni di tutte e {zip_celi['prove_n']} le prove dell'esempio 2", f"Non scritti nella pagina del CVCL né nell'esempio 2; i criteri di valutazione non li abbiamo aperti il {V(G)}"),
        (f'{G.eb("CERT.IT")} CERT.IT B1', "3 prove: dialoghi, brevi notizie radiofoniche, brevi messaggi",
         f"{Q('certit_b1_fascicolo', '25 minuti circa')} nel fascicolo dell'esempio", f"{mp3_certit['audio_durata']} per file ({mp3_certit['numero']} file): audio incompleti",
         f"Nell'esempio, prova 1: {Q('certit_b1_fascicolo', 'Ascolterai l’audio')} Prova 2: {Q('certit_b1_fascicolo', 'Ascolterai le notizie')} Per la prova 3 non è scritto",
         "20 su 100: 8, 7 e 5 nelle tre prove"),
    ])
    schede = [
        scheda(G, "CILS", "CILS B1 Cittadinanza",
               f"<p>Il sillabo scrive della prova di ascolto: {Q('cils_b1c_sillabo', 'Scelta multipla (a 3 opzioni)')}; {Q('cils_b1c_sillabo', 'Testi registrati in studio')}; "
               f"{Q('cils_b1c_sillabo', 'nella registrazione sono compresi')} per fare le prove e per copiare le risposte. Nel quaderno c'è scritto {Q('cils_b1c_quaderno', 'Tempo a disposizione')}. "
               f"Nella trascrizione si leggono le pause: {Q('cils_b1c_trascr', 'Adesso hai due minuti')} E alla fine, per copiare le risposte nel foglio: {Q('cils_b1c_trascr', 'Hai tre minuti')}</p>"
               f"<p>File: {L('asc_cils', 0)} · {L('asc_cils', 1)} · {L('asc_cils', 2)} · {L('asc_cils', 3)} · {L('asc_cils', 4)}. "
               'Tutti i file dell\'esempio, anche scrittura e orale: <a href="../cils/">CILS B1 Cittadinanza</a>.</p>'
               f"{fonte(G, 'cils_b1c', 'cils_b1c_sillabo', 'cils_b1c_criteri', 'cils_b1c_trascr', 'cils_b1c_quaderno')}", "cils_b1c", "Pagina ufficiale CILS B1 Cittadinanza"),
        scheda(G, "PLIDA", "PLIDA B1",
               f"<p>Il Quaderno delle specifiche scrive: {Q('plida_b1_quaderno', 'La prova Ascoltare dura')} {Q('plida_b1_quaderno', 'Ogni risposta errata')} "
               f"I testi sono {Q('plida_b1_quaderno', 'dialoghi registrati in studio')}. Alla fine {Q('plida_b1_quaderno', 'avrete dieci minuti')} nel foglio delle risposte. "
               "Nello zip della prova d'esempio il PDF di ascolto e lettura ha in fondo le trascrizioni delle prove Ascoltare e le soluzioni.</p>"
               f"<p>File: {L('asc_plida', 0)} · {L('asc_plida', 1)}. "
               'Tutti i file dell\'esempio: <a href="../plida/">PLIDA B1</a>.</p>'
               f"{fonte(G, 'plida_prepara', 'plida_b1_quaderno')}", "plida_prepara", "Pagina ufficiale PLIDA: Preparati all'esame"),
        scheda(G, "CELI", "CELI 2 i cittadinanza (B1)",
               f"<p>La pagina «Esami CELI immigrati» del CVCL scrive che lo scritto ha tre componenti, tra cui la {Q('celi_immigrati', 'comprensione dell')}, e che l'ascolto è nel secondo fascicolo: "
               f"{Q('celi_immigrati', 'contenuto del secondo fascicolo')}. Elenca due esempi: {Q('celi_immigrati', 'prova d')}. L'esempio 2 è la sessione di maggio 2018 e lo serve il sito del CVCL: nello zip ci sono l'audio, il PDF delle prove C con "
               f"{zip_celi['prove_n']} prove e {zip_celi['domande_n']} domande, i testi dell'ascolto e le chiavi (questi due in formato Word .DOC). Nelle istruzioni di ogni prova c'è scritto che i testi si ascoltano due volte.</p>"
               f"<p>File: {L('asc_celi2', 0)}. Tutti i file CELI di livello B1, uno per uno: <a href='../celi-2/'>CELI 2 e CELI 2 i</a>.</p>"
               f"{celi_non_aperti(G)}{fonte(G, 'celi_immigrati')}", "celi_immigrati", "Pagina ufficiale CELI (CVCL)"),
        scheda(G, "CERT.IT", "CERT.IT B1 (Roma Tre)",
               f"<p>{Q('certit_b1', 'In fondo alla pagina')} Lì ci sono lo zip dell'esempio e 3 file audio, uno per ogni prova di ascolto. "
               f"L'ascolto è una {Q('certit_b1', 'Comprensione di testi orali')} con 3 prove e 20 punti; la seconda prova usa {Q('certit_b1', 'Brevi notizie radiofoniche')}. "
               f"{Q('certit_b1', 'Le sezioni Ascolto')} Nel fascicolo dell'esempio l'ascolto è indicato con {Q('certit_b1_fascicolo', '25 minuti circa')} e la prima prova dice: {Q('certit_b1_fascicolo', 'Ascolterai l’audio')} "
               f"I {mp3_certit['numero']} MP3 che abbiamo aperto il {V(G)} durano {mp3_certit['audio_durata']} ciascuno e hanno tutti la stessa dimensione: {CERTIT_TAGLIATI}. "
               "Con questi file non si fa la prova di ascolto intera. Nello zip ci sono le chiavi, non la trascrizione dell'audio.</p>"
               f'<p class="ris-nota">Le note legali di Roma Tre scrivono {Q("certit_note", "È vietato il cd. deep linking")}: non mettiamo link diretti ai file, li scarichi dalla pagina ufficiale. Com\'è fatto tutto l\'esame: <a href="../certit/">CERT.IT B1</a>.</p>'
               f"{fonte(G, 'certit_b1', 'certit_b1_fascicolo')}", "certit_b1"),
    ]
    blocchi = f"""{G.riquadro_libro("../../").replace("clic/libro-esempi", "clic/" + CLIC_PAGINA["esempi/ascolto/"])}
<section>
<h2 id="file">{G.ic("archivio")}I file ufficiali dell'ascolto B1, ente per ente</h2>
<p class="small">Ogni link apre il file o la pagina sul sito dell'ente: qui non copiamo niente. La durata degli audio l'abbiamo letta nei file, il {V(G)}.</p>
{tabella_file(G, 'asc_cils', 'asc_plida', 'asc_celi2', 'asc_celi1', 'asc_certit', nota_celi=NOTA_CELI_PROVE, nota_certit=nota_certit_prove())}
</section>
<section class="ris-sez">
<h2 id="confronto">{G.ic("lista")}La prova di ascolto nei 4 esami B1</h2>
<p>Quello che i documenti ufficiali scrivono della prova di ascolto, accanto alla durata dell'audio d'esempio. Negli esempi di CILS e PLIDA l'audio dura meno del tempo scritto dall'ente.</p>
<p>Per CERT.IT i {mp3_certit['numero']} MP3 della pagina ufficiale durano {mp3_certit['audio_durata']} ciascuno e hanno tutti la stessa dimensione: {CERTIT_TAGLIATI}. Con questi file non si fa la prova di ascolto intera.</p>
{confronto}
<div class="fonte">{G.ic("doc")}<span>Fonti: {A('cils_b1c_sillabo')} · {A('cils_b1c_criteri')} · {A('plida_b1_quaderno')} · {A('celi_immigrati')} · {A('certit_b1')} · {A('certit_b1_fascicolo')} · lette il {V(G)}</span></div>
</section>
<section>
<h2 id="enti">{G.ic("cuffie")}Cosa scrive ogni ente</h2>
{"".join(schede)}
</section>
<section>
<h2 id="come-usare">{G.ic("matita")}Cosa farne</h2>
<ol class="passi">
<li><div><strong>Fai partire l'audio e non fermarlo</strong><p>Nell'audio CILS le pause e il secondo ascolto sono già dentro la registrazione. Tieni davanti il quaderno o il fascicolo con le domande.</p></div></li>
<li><div><strong>Copia le risposte nel foglio delle risposte</strong><p>Il quaderno CILS scrive: {Q('cils_b1c_quaderno', 'DEVI SCRIVERE')}; nell'audio ci sono tre minuti alla fine per farlo. Il Quaderno PLIDA scrive: {Q('plida_b1_quaderno', 'Le risposte date')}</p></div></li>
<li><div><strong>Correggi con le chiavi, poi leggi la trascrizione</strong><p>Dove c'è la trascrizione, rileggi solo le parti che hai sbagliato e riascoltale.</p></div></li>
</ol>
<p class="ris-nota">Un esempio non è l'esame: le prove cambiano a ogni sessione. Serve a capire il tipo di domande, i tempi e i punti. Per le altre prove: <a href="../prova-orale/">la prova orale, con i file ufficiali</a> · <a href="../prova-scritta/">la prova scritta</a> · <a href="../simulazione/">la simulazione con il cronometro</a>.</p>
</section>"""
    domande = [
        ("Dove trovo l'audio ufficiale della prova di ascolto CILS B1 Cittadinanza?",
         f"Sulla pagina ufficiale «Prove Liv. B1 c» del Centro CILS (Università per Stranieri di Siena): un file MP3 di {mp3_cils['durata']}, il quaderno con le domande, "
         "la trascrizione dell'audio, le chiavi e il foglio delle risposte in PDF."),
        ("Quanto dura la prova di ascolto dell'esame B1?",
         "Dipende dall'ente. Il sillabo CILS B1 Cittadinanza scrive 30 minuti circa, il Quaderno delle specifiche PLIDA B1 40 minuti circa, "
         "il fascicolo d'esempio CERT.IT B1 25 minuti circa (ma i 3 audio d'esempio durano 1 min 15 s ciascuno e sono incompleti). Per il CELI 2 i cittadinanza la durata non è scritta nella pagina del CVCL né nei file dell'esempio 2: "
         f"l'audio di quell'esempio dura {zip_celi['audio_durata']}."),
        ("Quante volte si ascolta l'audio all'esame B1?",
         "Due volte al CILS B1 Cittadinanza: lo scrive il sillabo. Lo dicono anche le istruzioni delle prove d'esempio: tutte e 4 le parti del PLIDA B1, "
         "tutte e 4 le prove dell'esempio 2 del CELI 2 i, le prove 1 e 2 del CERT.IT B1."),
        ("Le prove di ascolto ufficiali hanno la trascrizione e le soluzioni?",
         "CILS B1 Cittadinanza: sì, due PDF separati, trascrizione e chiavi. PLIDA B1: sì, in fondo al PDF di ascolto e lettura dentro lo zip. "
         "CELI 2 i cittadinanza, esempio 2: sì, i testi dell'ascolto e le chiavi sono due file Word dentro lo zip. CERT.IT B1: nello zip ci sono le chiavi, non la trascrizione, e i 3 audio della pagina ufficiale sono incompleti."),
    ]
    n_mp3 = 1 + 1 + zip_celi["audio_n"]  # audio interi: CILS, PLIDA, CELI; i 3 di CERT.IT sono incompleti
    scrivi(G, "ascolto", "Ascolto B1", "File ufficiali dei 4 enti",
           "Ascolto B1 cittadinanza: gli audio MP3 ufficiali, con domande e chiavi", lead,
           f'<a class="btn" href="#file">{G.ic("cuffie")}Gli audio e i file ufficiali</a><a class="btn btn-2" href="#confronto">{G.ic("lista")}Durata e punti</a>',
           blocchi, domande, altri("../ascolto/"),
           ("Ascolto B1 cittadinanza: audio MP3 ufficiali e chiavi", "Ascolto B1 cittadinanza: audio MP3 ufficiali"),
           (f"Ascolto B1 per la cittadinanza: i {n_mp3} audio MP3 ufficiali di CILS, PLIDA e CELI con durata, domande e chiavi. CERT.IT: 3 MP3 di 1 min 15 s, incompleti.",
            f"Ascolto B1 cittadinanza: {n_mp3} audio MP3 ufficiali di CILS, PLIDA e CELI con domande e chiavi. CERT.IT: 3 MP3 incompleti."),
           prossime, nota_date=NOTA_DATE_B1)


def pagina_orale(G, prossime):
    gr = D["gruppi"]
    n_diretti = len({f["url"] for k in ("ora_cils", "ora_plida") for f in gr[k]["file"]})
    lead = (f"Secondo i documenti ufficiali di CILS, PLIDA, CERT.IT e CELI, letti il {V(G)}, la prova orale del B1 dura «10 minuti circa» al CILS B1 Cittadinanza, "
            "«circa 15 minuti» al PLIDA B1 e «10 minuti» al CERT.IT B1, e per tutti e tre c'è una traccia ufficiale d'esempio da scaricare: "
            f"{n_diretti} file con link diretto per CILS e PLIDA e lo zip sulla pagina di CERT.IT; per il CELI 2 i il CVCL elenca 3 PDF sull'orale, che non abbiamo aperto.")
    plida_file = f"{L('ora_plida', 0, 'Prova d' + chr(39) + 'esempio (zip)')} · {L('ora_plida', 1, 'Quaderno delle specifiche')}"
    certit_file = f"Zip «Certit_B1»: {A('certit_b1', 'sulla pagina ufficiale CERT.IT')}"
    parti = tab(("Ente", "Parte", "Durata", "Compito", "File ufficiale"), [
        (f'{G.eb("CILS")} CILS B1 Cittadinanza', "Breve presentazione personale", Q('cils_b1c_po', 'Durata della presentazione'),
         f"L'esaminatore fa alcune domande, per esempio {Q('cils_b1c_po', 'Come ti chiami?')} e {Q('cils_b1c_po', 'Che cosa fai nella vita')}; {Q('cils_b1c_po', 'non è necessario rivolgere')}",
         L('ora_cils', 0, 'Produzione orale (PDF)')),
        (f'{G.eb("CILS")} CILS B1 Cittadinanza', "Prova n. 1: conversazione", Q('cils_b1c_po', 'Durata della conversazione'),
         f"{Q('cils_b1c_po', 'L’esaminatore farà scegliere')} Nell'esempio sono 4, tra cui {Q('cils_b1c_po', 'Preferisci vivere')} e {Q('cils_b1c_po', 'Quali documenti ti servono')}",
         L('ora_cils', 0, 'Produzione orale (PDF)')),
        (f'{G.eb("PLIDA")} PLIDA B1', "Presentazione", "«2 minuti circa»",
         f"{Q('plida_b1_quaderno', 'L’intervistatore rivolge')} {Q('plida_b1_quaderno', 'Questa parte non è oggetto')}", L('ora_plida', 1, 'Quaderno delle specifiche (PDF)')),
        (f'{G.eb("PLIDA")} PLIDA B1', "Prima parte: interazione", Q('plida_b1_quaderno', 'minimo 3 / massimo 4'),
         f"{Q('plida_b1_quaderno', 'Interazione tra candidati')} Nell'esempio i due candidati si organizzano per la visita di un amico: {Q('plida_b1_quaderno', 'decidete chi di voi')}", plida_file),
        (f'{G.eb("PLIDA")} PLIDA B1', "Seconda parte: monologo", Q('plida_b1_quaderno', 'minimo 3 / massimo 4'),
         f"Un discorso su un tema, a partire da un testo o da un'immagine. Nell'esempio: {Q('plida_b1_quaderno', 'raccontare qual è il tuo hobby')}. {Q('plida_b1_quaderno', 'Alla fine del monologo')}", plida_file),
        (f'{G.eb("CERT.IT")} CERT.IT B1', "Parte A", Q('certit_b1_parlato', 'Durata della conversazione: circa'),
         f"{Q('certit_b1', 'Parte A')} L'esaminatore fa {Q('certit_b1_parlato', 'alcune domande personali')}", certit_file),
        (f'{G.eb("CERT.IT")} CERT.IT B1', "Parte B", Q('certit_b1_parlato', 'Durata della conversazione: 2'),
         f"Una simulazione di ruolo: l'esaminatore {Q('certit_b1_parlato', 'gli propone un role-play')}. In una di queste {Q('certit_b1_parlato', 'Il somministratore assume')}", certit_file),
        (f'{G.eb("CERT.IT")} CERT.IT B1', "Parte C", Q('certit_b1_parlato', 'Durata del messaggio'),
         f"Un monologo: l'esaminatore propone uno scenario {Q('certit_b1_parlato', 'a cui dovrà rispondere')}. Nell'esempio della pagina ufficiale: {Q('certit_b1', 'Mandi un vocale')}", certit_file),
        (f'{G.eb("CELI")} CELI 2 i cittadinanza', "Orale", "Non scritta nella pagina del CVCL", Q('celi_immigrati', 'L’esame orale'),
         f"3 PDF elencati {A('celi_immigrati', 'sulla pagina del CVCL')}, non aperti"),
    ])
    schede = [
        scheda(G, "CILS", "CILS B1 Cittadinanza",
               f"<p>Il sillabo descrive così l'orale: {Q('cils_b1c_sillabo', 'Dialogo con il somministratore')} personale, fatta con una lista di domande; durata del test {Q('cils_b1c_sillabo', '10 minuti circa')}, "
               f"{Q('cils_b1c_sillabo', 'durata del dialogo')}. La traccia d'esempio è della sessione di {Q('cils_b1c_po', 'Maggio 2019')} e scrive: {Q('cils_b1c_po', 'La prova ha le caratteristiche')} "
               f"{Q('cils_b1c_po', 'Le prove orali devono essere registrate')}</p>"
               f"<p>Punti, dai criteri di valutazione: {Q('cils_b1c_criteri', 'Punteggio massimo: punti 12')}, cioè {Q('cils_b1c_criteri', 'efficacia comunicativa: fino a punti 4')}, "
               f"{Q('cils_b1c_criteri', 'correttezza morfosintattica')}, {Q('cils_b1c_criteri', 'adeguatezza e ricchezza lessicale')}, {Q('cils_b1c_criteri', 'pronuncia e intonazione')}. "
               f"La pagina ufficiale scrive: {Q('cils_b1c', 'Per questo livello')}</p>"
               f"{fonte(G, 'cils_b1c_po', 'cils_b1c_sillabo', 'cils_b1c_criteri', 'cils_b1c')}", "cils_b1c", "Pagina ufficiale CILS B1 Cittadinanza"),
        scheda(G, "PLIDA", "PLIDA B1",
               f"<p>Il Quaderno delle specifiche scrive: {Q('plida_b1_quaderno', 'La prova Parlare dura')} {Q('plida_b1_quaderno', 'Solo la seconda e la terza parte')} "
               f"Nei tre minuti di preparazione {Q('plida_b1_quaderno', 'il candidato può prendere appunti')}. Per superare l'esame serve {Q('plida_b1_quaderno', 'almeno 18/30')}; "
               f"chi non supera una o più abilità, fino a tre, {Q('plida_b1_quaderno', 'possono recuperarle')} successivi.</p>"
               f"<p>La griglia ufficiale, {Q('plida_b1_parlare', 'Criteri di valutazione delle prove di produzione orale')}, ha 5 voci: {Q('plida_b1_parlare', 'EFFICACIA')}, "
               f"{Q('plida_b1_parlare', 'INTERAZIONE')}, {Q('plida_b1_parlare', 'LESSICO')}, {Q('plida_b1_parlare', 'GRAMMATICA')} e {Q('plida_b1_parlare', 'PRONUNCIA')}, ognuna con una scala da 1 a 10: {L('ora_plida', 2)}.</p>"
               f"{fonte(G, 'plida_prepara', 'plida_b1_quaderno', 'plida_b1_parlare')}", "plida_prepara", "Pagina ufficiale PLIDA: Preparati all'esame"),
        scheda(G, "CERT.IT", "CERT.IT B1 (Roma Tre)",
               f"<p>La pagina del livello B1 scrive: {Q('certit_b1', 'La sezione Produzione orale dura')} È una {Q('certit_b1', 'Comunicazione faccia a faccia')} con 3 prove e 30 punti, 10 per prova; "
               f"per superarla serve {Q('certit_b1', 'il 60% del punteggio nella sezione')}. La pagina «Indicazioni sullo svolgimento» aggiunge: {Q('certit_svolgimento', 'La sezione Parlato si svolge')} "
               f"Nel PDF della sezione Parlato, dentro lo zip dell'esempio: {Q('certit_b1_parlato', 'La sezione Parlato comprende')}</p>"
               f'<p class="ris-nota">Le note legali di Roma Tre scrivono {Q("certit_note", "È vietato il cd. deep linking")}: non mettiamo link diretti ai file, lo zip lo scarichi dalla pagina ufficiale, sotto {Q("certit_b1", "Esempio di esame")}.</p>'
               f"{fonte(G, 'certit_b1', 'certit_svolgimento', 'certit_b1_parlato')}", "certit_b1"),
        scheda(G, "CELI", "CELI 2 i cittadinanza (B1)",
               f"<p>La pagina «Esami CELI immigrati» del CVCL scrive: {Q('celi_immigrati', 'L’esame orale')} E degli esami CELI 1 i e CELI 2 i cittadinanza scrive che, "
               f"{Q('celi_immigrati', 'in particolare nella parte orale')}. Per l'orale del CELI 2 i elenca tre PDF: {Q('celi_immigrati', 'input orale celi 2 i')}, "
               f"{Q('celi_immigrati', 'vademecum celi 2 i')} e {Q('celi_immigrati', 'criteri di valutazione orale')}. La durata dell'orale nella pagina non è scritta.</p>"
               f"{celi_non_aperti(G)}{fonte(G, 'celi_immigrati')}", "celi_immigrati", "Pagina ufficiale CELI (CVCL)"),
    ]
    blocchi = f"""{G.riquadro_libro("../../").replace("clic/libro-esempi", "clic/" + CLIC_PAGINA["esempi/prova-orale/"])}
<section>
<h2 id="parti">{G.ic("voce")}L'orale B1, parte per parte, con il file ufficiale</h2>
<p class="small">Durata e compito sono frasi dei documenti ufficiali, tra virgolette. Ogni link apre il file o la pagina sul sito dell'ente: qui non copiamo niente.</p>
{parti}
<div class="fonte">{G.ic("doc")}<span>Fonti: {A('cils_b1c_po')} · {A('plida_b1_quaderno')} · {A('certit_b1')} · {A('certit_b1_parlato')} · {A('celi_immigrati')} · lette il {V(G)}</span></div>
</section>
<section>
<h2 id="file">{G.ic("archivio")}I file ufficiali dell'orale B1, ente per ente</h2>
{tabella_file(G, 'ora_cils', 'ora_plida', 'ora_certit', 'ora_celi', nota_celi=NOTA_CELI_PROVE, nota_certit=nota_certit_prove())}
</section>
<section class="ris-sez">
<h2 id="enti">{G.ic("lista")}Durata, punti e regole: cosa scrive ogni ente</h2>
{"".join(schede)}
</section>
<section>
<h2 id="come-usare">{G.ic("matita")}Cosa farne</h2>
<ol class="passi">
<li><div><strong>Leggi la traccia del tuo ente</strong><p>Le parti e i tempi cambiano da un ente all'altro: allenati con la traccia dell'esame che farai.</p></div></li>
<li><div><strong>Parla ad alta voce con il tempo scritto nel file</strong><p>Per il PLIDA usa anche i 3 minuti di preparazione, con gli appunti. Registrati e riascoltati.</p></div></li>
<li><div><strong>Guarda i criteri di valutazione</strong><p>Dicono cosa conta nei punti. Il tuo orale però non lo corregge nessun file: fallo sentire a un insegnante.</p></div></li>
</ol>
<p class="ris-nota">Un esempio non è l'esame: le tracce cambiano a ogni sessione. Per le altre prove: <a href="../ascolto/">l'ascolto, con gli audio ufficiali</a> · <a href="../prova-scritta/">la prova scritta</a> · <a href="../confronto/">i 4 esami a confronto</a>.</p>
</section>"""
    domande = [
        ("Quanto dura la prova orale dell'esame B1 per la cittadinanza?",
         "Dipende dall'ente: 10 minuti circa al CILS B1 Cittadinanza (sillabo), circa 15 minuti al PLIDA B1 (Quaderno delle specifiche), 10 minuti al CERT.IT B1 (pagina del livello B1). "
         "Per il CELI 2 i cittadinanza la durata non è scritta nella pagina del CVCL."),
        ("Cosa chiedono all'orale del CILS B1 Cittadinanza?",
         "Secondo la traccia ufficiale d'esempio, una breve presentazione personale di 1 minuto circa e poi una conversazione di 2-3 minuti circa su un argomento che il candidato "
         "sceglie tra quelli proposti dall'esaminatore."),
        ("All'orale del PLIDA B1 la presentazione viene valutata?",
         "No. Il Quaderno delle specifiche PLIDA B1 scrive che la presentazione non è oggetto di valutazione: si valutano solo l'interazione e il monologo."),
        ("Dove trovo un esempio ufficiale della prova orale B1?",
         "CILS B1 Cittadinanza: il PDF «Produzione orale» sulla pagina «Prove Liv. B1 c». PLIDA B1: il PDF della prova Parlare dentro lo zip della prova d'esempio e le tracce nel "
         "Quaderno delle specifiche. CERT.IT B1: il PDF della sezione Parlato dentro lo zip in fondo alla pagina del livello B1. CELI 2 i: i PDF elencati nella pagina «Esami CELI immigrati» del CVCL."),
    ]
    scrivi(G, "prova-orale", "Prova orale B1", "Documenti ufficiali dei 4 enti",
           "Prova orale B1 cittadinanza: cosa chiede ogni ente, con le tracce e i file ufficiali", lead,
           f'<a class="btn" href="#parti">{G.ic("voce")}L\'orale parte per parte</a><a class="btn btn-2" href="#file">{G.ic("archivio")}I file ufficiali</a>',
           blocchi, domande, altri("../prova-orale/"),
           ("Prova orale B1 cittadinanza: tracce e file ufficiali", "Prova orale B1 cittadinanza: file ufficiali"),
           ("Prova orale B1 per la cittadinanza: durata, parti e compiti di CILS, PLIDA, CERT.IT e CELI, con le tracce ufficiali d'esempio e i criteri di valutazione.",
            "Prova orale B1 per la cittadinanza: parti, durata e tracce ufficiali di CILS, PLIDA, CERT.IT e CELI."),
           prossime, nota_date=NOTA_DATE_B1)


# ---------------------------------------------------------------- /esempi/celi-2/ (26/11/2026)
def QE(k, testo):
    """Come Q(), ma la frase citata deve essere proprio «testo» (per le etichette corte dei link, che cominciano allo stesso modo)."""
    if not any(c["fonte"] == k and c["testo"] == testo for c in D["citazioni"]):
        raise SystemExit(f"genera_livelli: «{testo}» non è tra le frasi citate di «{k}»")
    return "«" + escape(testo) + "»"


def pagina_celi2(G, prossime):
    """CELI 2 (B1) e CELI 2 i cittadinanza (B1): tutti i file che le due pagine del CVCL elencano, uno per uno, con scritto quali abbiamo
    aperto il giorno del controllo (solo quelli serviti da cvcl.unistrapg.it) e quali no (quelli su www.unistrapg.it)."""
    gr = D["gruppi"]
    z = gr["asc_celi2"]["file"][0]
    dentro = z["contenuto_zip"]
    guide = gr["c2_pretest"]["file"]
    no_i, no_g = gr["c2_celi2i"]["file"], gr["c2_celi2"]["file"]
    n_aperti, n_no = 1 + len(guide), len(no_i) + len(no_g)
    v_b1 = G.data_breve(G.v_esempi(G.ES["CELI"]))
    lead = (f"Secondo le pagine ufficiali «Esami CELI generici» e «Esami CELI immigrati» del CVCL (Università per Stranieri di Perugia), controllate il {V(G)}, "
            f"il CVCL elenca {len(no_g)} file per il CELI 2 (B1) e {len(no_i) + 1} per il CELI 2 i cittadinanza (B1), ma dal sito del CVCL si apre una sola prova d'esame: "
            f"lo zip «esempio 2» del CELI 2 i ({G.peso(z['byte'])}, sessione di maggio 2018, con prove, audio e chiavi); gli altri {n_no} file stanno su www.unistrapg.it "
            f"e il {V(G)} non li abbiamo aperti.")

    def riga(esame, parte, formato, file):
        return (f'<tr><td>{G.eb("CELI")}</td><td data-l="Esame">{esame}</td><td data-l="Parte">{escape(parte)}</td>'
                f'<td data-l="Formato">{formato}</td><td data-l="File">{file}</td></tr>')

    def cosa(t):
        return f'<span class="cosa">{escape(t[0].upper() + t[1:])}.</span>'

    def non_aperto(k, f):
        nome = f"Prova d'esame: {escape(f['nome'])}" if f["formato"] == "ZIP" else QE(k, f["nome"])
        return riga(escape(gr["c2_celi2i" if k == "celi_immigrati" else "c2_celi2"]["esame"]), f["parte"], f'<strong>{f["formato"]}</strong> · non aperto',
                    f'{nome}: {A(k, "sulla pagina del CVCL")}<span class="cosa">Sta su www.unistrapg.it: il {V(G)} non l\'abbiamo aperto, quindi non scriviamo cosa contiene.</span>')

    cosa_zip = cosa(f"sessione di maggio 2018. Dentro ci sono {len(dentro)} file: due PDF con le prove, un audio MP3, i testi dell'ascolto e le chiavi in due file Word")
    righe = [riga("CELI 2 i cittadinanza (B1)", "Prova d'esame", f'<strong>ZIP</strong> · {G.peso(z["byte"])} · aperto', L("asc_celi2", 0) + cosa_zip)]
    righe += [riga("CELI 2 (B1) e gli altri CELI generici", f["parte"], f'<strong>PDF</strong> · {G.peso(f["byte"])} · {f["pagine"]} pag. · aperto',
                   f'{L("c2_pretest", i)}{cosa(f["contenuto"])}') for i, f in enumerate(guide)]
    righe += [non_aperto("celi_immigrati", f) for f in no_i] + [non_aperto("celi_generici", f) for f in no_g]
    tabella = ('<div class="tab-wrap ris-tab liv-tab"><table class="conf"><thead><tr><th scope="col">Ente</th><th scope="col">Esame</th>'
               '<th scope="col">Parte</th><th scope="col">Formato</th><th scope="col">File ufficiale</th></tr></thead>'
               f'<tbody>{"".join(righe)}</tbody></table></div>'
               f'<div class="fonte">{G.ic("ok")}<span>Link controllati il {V(G)}: i {n_aperti} file con link diretto si aprono sul sito cvcl.unistrapg.it (stato 200), '
               f"con il formato e la dimensione indicati. Lo zip l'abbiamo scaricato intero e aperto. Gli altri {n_no} link delle due pagine del CVCL portano a www.unistrapg.it: "
               f"dal nostro server quel sito non si apre (errore di certificato, visto il 25 novembre 2026), il {V(G)} non li abbiamo aperti e non mettiamo link a file che non abbiamo aperto. "
               "Li scarichi dalle due pagine del CVCL.</span></div>")

    def dettagli(f):
        return " · ".join(x for x in (G.peso(f["byte"]), f'{f["pagine"]} pag.' if f.get("pagine") else "", f.get("durata", "")) if x)

    tab_zip = tab(("File nello zip", "Parte", "Formato", "Cosa c'è"),
                  [(f"<strong>{escape(f['nome'])}</strong>", escape(f["parte"]), f"<strong>{f['formato']}</strong> · {escape(dettagli(f))}",
                    escape(f["contenuto"][0].upper() + f["contenuto"][1:]) + ".") for f in dentro])
    let, scr = z["lettura"], z["scrittura"]
    schede = [
        scheda(G, "CELI", "CELI 2 (B1), tra i CELI generici",
               f"<p>Nella pagina «Esami CELI generici» il CVCL scrive che i CELI generici sono {Q('celi_generici', 'rivolti ad adulti')} e li elenca per livello: {Q('celi_generici', 'CELI 2 (')}. "
               f"Del CELI 2 scrive: {Q('celi_generici', 'Il CELI 2 attesta')} E ancora: {Q('celi_generici', 'Al livello B1')}</p>"
               f"<p>Sotto «Documenti correlati» ci sono {len(no_g)} link: {QE('celi_generici', 'competenze richieste')}, {QE('celi_generici', 'struttura e descrizione della prova')}, "
               f"{QE('celi_generici', 'facsimile foglio delle risposte')}, {QE('celi_generici', 'valutazione e punteggi')}, {QE('celi_generici', 'tabella di conversione dei punteggi')}, "
               f"{QE('celi_generici', 'competenze e punteggi orale')}, {QE('celi_generici', 'competenze e punteggi scritto')} e {Q('celi_generici', 'prova d')}. "
               f"Tutti e {len(no_g)} portano a www.unistrapg.it: il {V(G)} non li abbiamo aperti. Per questo qui non scriviamo quante prove ha il CELI 2, quanto dura e quanti punti servono.</p>"
               f"{fonte(G, 'celi_generici')}", "celi_generici", "Pagina ufficiale CELI generici (CVCL)", ancora="celi-2"),
        scheda(G, "CELI", "CELI 2 i cittadinanza (B1), tra i CELI immigrati",
               f"<p>Nella pagina «Esami CELI immigrati» il CVCL scrive che gli esami CELI i sono per {Q('celi_immigrati', 'cittadini stranieri legati')}. "
               f"Del CELI 2 i scrive: {Q('celi_immigrati', 'Ogni esame è diviso')} Lo scritto ha due fascicoli: {Q('celi_immigrati', 'contenuto del primo fascicolo')} e "
               f"{Q('celi_immigrati', 'contenuto del secondo fascicolo')}. Dell'orale scrive: {Q('celi_immigrati', 'L’esame orale')} "
               f"E degli esami CELI 1 i e CELI 2 i cittadinanza scrive che, {Q('celi_immigrati', 'in particolare nella parte orale')}.</p>"
               f"<p>Sotto «Documenti correlati» ci sono {len(no_i) + 1} link: {QE('celi_immigrati', 'descrizione dell' + chr(39) + 'esame')}, {QE('celi_immigrati', 'criteri di valutazione')}, "
               f"{QE('celi_immigrati', 'criteri di valutazione scritto')}, {QE('celi_immigrati', 'criteri di valutazione orale')}, {QE('celi_immigrati', 'vademecum celi 2 i')}, "
               f"{Q('celi_immigrati', 'prova d')}, {QE('celi_immigrati', 'scheda d' + chr(39) + 'iscrizione')}, {QE('celi_immigrati', 'input orale celi 2 i')} e {QE('celi_immigrati', 'risposte celi 2 i')}. "
               f"Solo l'esempio 2 lo serve il sito del CVCL: {L('asc_celi2', 0)}. Gli altri {len(no_i)} portano a www.unistrapg.it.</p>"
               f"{celi_non_aperti(G)}{fonte(G, 'celi_immigrati')}", "celi_immigrati", "Pagina ufficiale CELI immigrati (CVCL)", ancora="celi-2-i"),
    ]
    blocchi = f"""{G.riquadro_libro("../../").replace("clic/libro-esempi", "clic/" + CLIC_PAGINA["esempi/celi-2/"])}
<section>
<h2 id="file">{G.ic("archivio")}I file CELI di livello B1 sul sito del CVCL, uno per uno</h2>
<p class="small">Ogni link apre il file o la pagina sul sito del CVCL: qui non copiamo niente. In ogni riga c'è scritto se il file l'abbiamo aperto il {V(G)} oppure no.</p>
{tabella}
{fonte(G, 'celi_generici', 'celi_immigrati', 'celi_pretest')}
</section>
<section class="ris-sez">
<h2 id="zip">{G.ic("lista")}Cosa c'è nello zip del CELI 2 i, file per file</h2>
<p>Lo zip dell'esempio 2 pesa {G.peso(z['byte'])} e contiene {len(dentro)} file della sessione di maggio 2018. Li abbiamo aperti tutti il {V(G)}.</p>
{tab_zip}
<p>Lettura: {let['prove_n']} prove, {let['domande_n']} domande. Scrittura: {scr['prove_n']} prove; nel fascicolo le parole richieste sono {scr['parole'][0]} nella prima prova,
{scr['parole'][1]} nella seconda e {scr['parole'][2]} nella terza. Ascolto: {z['prove_n']} prove, {z['domande_n']} domande, un audio di {z['audio_durata']}.</p>
<p>Nel file delle chiavi ci sono anche i punti. Lettura: 2 punti per ogni risposta giusta nella prova A.1, 1,5 nella A.2, 1 nella A.3 e nella A.4. Ascolto: 2 punti nelle prove C.1 e C.2,
1 nella C.3, 1,5 nella C.4. Scrittura: fino a 3 punti per ogni risposta della prova B.1, 15 punti per la B.2 e 20 per la B.3.
Il punteggio totale e quanti punti servono per superare l'esame nello zip non sono scritti.</p>
<p class="ris-nota">Nello zip non ci sono i fogli delle risposte, le tracce dell'orale e i criteri di valutazione: sono tra i file che non abbiamo aperto il {V(G)}.
Tempi, punti per superare e orale del CELI 2 i sono nella pagina <a href="../celi/">CELI 2 i cittadinanza</a>, controllata il {v_b1}.</p>
{fonte(G, 'celi_immigrati')}
</section>
<section>
<h2 id="enti">{G.ic("info")}CELI 2 e CELI 2 i: cosa scrive il CVCL</h2>
<p>Sono due esami di livello B1 dello stesso ente, su due pagine ufficiali diverse e con file d'esempio diversi. Quale vale per la tua domanda e dove si fa: <a href="../../ente/celi/">CELI: date, costo e sedi</a>.</p>
{"".join(schede)}
</section>
<section class="ris-sez">
<h2 id="pre-test">{G.ic("ok")}CELI 2: il pre-test online per chi è già iscritto</h2>
<p>Un avviso del CVCL del 27 febbraio 2026 scrive che dal 2 marzo {Q('celi_pretest', 'tutti i candidati iscritti')}. Per entrare {Q('celi_pretest', 'è necessario essere iscritti')}.
Vale per i CELI generici, quindi per il CELI 2; non per il CELI 2 i cittadinanza.</p>
<p>La guida per la navigazione scrive: {Q('celi_pretest_guida', 'nel pre-test online CELI sono presenti')}. Per il CELI 2 sono {Q('celi_pretest_guida', 'Parte A')} e {Q('celi_pretest_guida', 'Parte C')}:
lettura e ascolto. La guida scrive anche: {Q('celi_pretest_guida', 'POTRAI EFFETTUARE')}. E dei risultati scrive che {Q('celi_pretest_guida', 'non sono in nessun modo')}.</p>
<p>File: {L('c2_pretest', 0)} · {L('c2_pretest', 1)}. Sono due guide: spiegano come si entra e come ci si muove. Il pre-test non l'abbiamo aperto, perché serve il numero di matricola di un iscritto.</p>
{fonte(G, 'celi_pretest', 'celi_pretest_guida')}
</section>
<section>
<h2 id="manca">{G.ic("info")}Quello che manca, detto chiaro</h2>
<ul>
<li><strong>CELI 2 (B1):</strong> il {V(G)} non abbiamo aperto nessuna prova d'esame. I due esempi in zip e i 7 PDF sono su www.unistrapg.it. Li trovi {A('celi_generici', 'sulla pagina «Esami CELI generici»')}.</li>
<li><strong>CELI 2 i cittadinanza (B1):</strong> abbiamo aperto solo l'esempio 2. L'esempio 1 e gli altri {len(no_i) - 1} PDF sono su www.unistrapg.it. Li trovi {A('celi_immigrati', 'sulla pagina «Esami CELI immigrati»')}.</li>
<li><strong>L'esempio 2 è del 2018:</strong> è la sessione di maggio 2018. Di che sessione sono gli altri tre esempi non lo sappiamo, perché non li abbiamo aperti.</li>
<li><strong>I testi dell'ascolto e le chiavi sono file Word (.DOC):</strong> per aprirli serve un programma che legge i file Word.</li>
</ul>
</section>
<section>
<h2 id="come-usare">{G.ic("matita")}Cosa farne</h2>
<ol class="passi">
<li><div><strong>Controlla a quale esame sei iscritto</strong><p>CELI 2 e CELI 2 i cittadinanza hanno file d'esempio diversi. Se non lo sai, chiedilo alla sede dove ti sei iscritto.</p></div></li>
<li><div><strong>Fai l'esempio 2 del CELI 2 i senza fermare l'audio</strong><p>Stampa i due PDF. Per l'ascolto fai partire l'MP3 e non fermarlo: dura {z['audio_durata']}. Le istruzioni dicono che ogni testo si ascolta due volte.</p></div></li>
<li><div><strong>Correggi lettura e ascolto con le chiavi</strong><p>Il file delle chiavi non dà il punteggio totale né la soglia per superare l'esame: per i punteggi ufficiali vedi <a href="../celi/">CELI 2 i cittadinanza</a>. Per la scrittura non c'è una risposta giusta: fai leggere i tuoi testi a un insegnante.</p></div></li>
</ol>
<p class="ris-nota">Un esempio non è l'esame: le prove cambiano a ogni sessione. Serve a capire il tipo di domande. Per le altre prove: <a href="../ascolto/">gli audio ufficiali dell'ascolto B1</a> ·
<a href="../prova-orale/">la prova orale</a> · <a href="../prova-scritta/">la prova scritta</a> · <a href="../simulazione/">la simulazione con il cronometro</a>.</p>
</section>"""
    domande = [
        ("Dove trovo le prove d'esame del CELI 2 (B1)?",
         f"Sulla pagina «Esami CELI generici» del CVCL (Università per Stranieri di Perugia): alla voce CELI 2 ci sono due esempi in zip e 7 PDF. I file stanno su www.unistrapg.it: "
         f"il {V(G)} non li abbiamo aperti, quindi qui trovi il link alla pagina del CVCL e non ai file."),
        ("CELI 2 e CELI 2 i cittadinanza sono lo stesso esame?",
         "No. Sono due esami di livello B1 su due pagine diverse del CVCL: il CELI 2 è tra i CELI generici, il CELI 2 i cittadinanza tra i CELI immigrati. "
         "Hanno file d'esempio diversi."),
        ("Cosa c'è nell'esempio 2 del CELI 2 i cittadinanza?",
         f"Uno zip di {G.peso(z['byte'])} con {len(dentro)} file della sessione di maggio 2018: il PDF delle prove A e B (lettura e scrittura, {dentro[0]['pagine']} pagine), il PDF delle prove C "
         f"(ascolto, {dentro[1]['pagine']} pagine), l'audio MP3 di {z['audio_durata']}, i testi dell'ascolto e le chiavi in due file Word."),
        ("C'è un test online per prepararsi al CELI 2?",
         "Il CVCL ha un pre-test online per chi è già iscritto a un esame CELI generico: si entra con il numero di matricola e la data di nascita. "
         "Per il CELI 2 ci sono la lettura e l'ascolto. Non c'è per il CELI 2 i cittadinanza."),
    ]
    scrivi(G, "celi-2", "CELI 2 e CELI 2 i", "CVCL, Università per Stranieri di Perugia",
           "CELI 2 e CELI 2 i (B1): le prove d'esempio ufficiali, file per file", lead,
           f'<a class="btn" href="#file">{G.ic("archivio")}I file, uno per uno</a><a class="btn btn-2" href="#zip">{G.ic("lista")}Cosa c\'è nello zip</a>',
           blocchi, domande, altri("../celi-2/") + '<a href="../celi/">CELI 2 i cittadinanza: tempi e punti</a>',
           ("CELI 2 e CELI 2 i (B1): prove d'esempio ufficiali", "CELI 2 e CELI 2 i (B1): prove d'esempio"),
           (f"CELI 2 e CELI 2 i cittadinanza (B1): i file del CVCL uno per uno. Aperto il {V(G)}: lo zip dell'esempio 2 del CELI 2 i, con prove, audio e chiavi.",
            "CELI 2 e CELI 2 i cittadinanza (B1): i file del CVCL uno per uno, con lo zip dell'esempio 2 del CELI 2 i."),
           prossime, nota_date=NOTA_DATE_B1)


# ---------------------------------------------------------------- ingresso
def carica(G):
    global D
    D = json.loads((G.DATI / "esempi_livelli.json").read_text(encoding="utf-8"))


def genera(G, prossime):
    carica(G)
    PAGINE.clear()
    pagina_b1_standard(G, prossime)
    for liv in ("a1", "c1", "c2"):
        pagina_livello(G, liv, prossime)
    global DATA
    DATA = "verificato_il_prove"  # le due pagine del 26/11/2026 hanno la loro data di controllo
    try:
        pagina_ascolto(G, prossime)
        pagina_orale(G, prossime)
        pagina_celi2(G, prossime)  # scheda 2026-11-26-esameb1-celi2.md
    finally:
        DATA = "verificato_il"
    return list(PAGINE)


def controlli(G):
    """Ogni testo tra «» delle 4 pagine è una frase citata o il nome di una fonte; ogni domanda del JSON-LD è visibile; ogni file con link
    diretto del gruppo è nella pagina e punta al sito dell'ente; il riquadro del libro c'è una volta sola, con l'etichetta dei clic giusta."""
    b1c = G.ES["CILS"]
    da_fonti = (" ".join(c["testo"].replace('"', "") for c in D["citazioni"]) + " " + " ".join(f["nome"] for f in D["fonti"].values())
                + " " + " ".join(c["testo"] for c in b1c.get("citazioni", [])) + " " + b1c["pagina"]["nome"] + " «Preparati all'esame» «Scarica i materiali»").lower()
    host_enti = ("cils.unistrasi.it", "cms.plida.dante.global")
    host_prove = host_enti + ("cvcl.unistrapg.it",)  # 26/11/2026: l'esempio 2 del CELI 2 i è servito dal sito del CVCL
    errori = []
    for p in PAGINE:
        h = (G.SITO / p / "index.html").read_text(encoding="utf-8")
        main = h[h.find("<main"):h.find("</main>")]
        senza_libro = G._RE_LIBRO.sub("", main)
        testo = unescape(re.sub(r"<[^>]+>", "", senza_libro))
        for frase in re.findall(r"«([^»]+)»", testo):
            if frase.lower() not in da_fonti:
                errori.append(f"{p}: il testo tra virgolette «{frase}» non è tra le frasi citate")
        ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
        for q in json.loads(ld.group(1))["mainEntity"]:
            if escape(q["name"]) not in main or escape(q["acceptedAnswer"]["text"]) not in main:
                errori.append(f"{p}: domanda frequente non visibile: {q['name']}")
        libro = re.findall(r'<a [^>]*data-libro-proprio="si"[^>]*>', main)
        if len(libro) not in (1, 2) or any(f'data-goatcounter-click="esameb1.eu/clic/{CLIC_PAGINA.get(p, CLIC_LIBRO)}"' not in x for x in libro):
            errori.append(f"{p}: riquadro del libro assente, doppio o con un'altra etichetta dei clic")
        tab = main[main.find('liv-tab'):]
        for u in re.findall(r'href="(https?://[^"]+\.(?:pdf|mp3|zip))"', tab[:tab.find("</table>")], re.I):
            if G.host(unescape(u)) not in host_enti:
                errori.append(f"{p}: link a un file fuori dai siti degli enti: {u}")
        if p in CLIC_PAGINA:  # pagine del 26/11/2026: in tutta la pagina nessun link a www.unistrapg.it né ai file di Roma Tre; riquadro del libro in alto; data propria
            for u in re.findall(r'href="(https?://[^"]+)"', main):
                u = unescape(u)
                if "//www.unistrapg.it" in u or "uniroma3.it/wp-content" in u:
                    errori.append(f"{p}: link vietato (file non aperto o link diretto a un file di Roma Tre): {u}")
                if (re.search(r"\.(pdf|mp3|zip)$", u, re.I) or "StreamRisorsa" in u) and G.host(u) not in host_prove:
                    errori.append(f"{p}: link a un file fuori dai siti degli enti: {u}")
            if not 0 <= main.find('id="libro"') < main.find("<h2 id="):
                errori.append(f"{p}: il riquadro del libro non è subito sotto il titolo")
            if f'controllato il {G.data_breve(D["verificato_il_prove"])}' not in main:
                errori.append(f"{p}: manca la data di controllo delle pagine del 26/11/2026")
    urls = {f["url"] for g in D["gruppi"].values() for f in g["file"] if f.get("url")}
    tutte = " ".join((G.SITO / p / "index.html").read_text(encoding="utf-8") for p in PAGINE)
    for u in urls:
        if escape(u) not in tutte:
            errori.append(f"file di dati/esempi_livelli.json non usato in nessuna pagina: {u}")
    if errori:
        raise SystemExit("ERRORI NELLE PAGINE DEGLI ESEMPI PER LIVELLO (genera_livelli.py):\n" + "\n".join(errori))
    return len(PAGINE)
