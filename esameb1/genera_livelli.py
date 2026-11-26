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
Chiamato da main() di genera.py: genera(G, prossime) e controlli(G)."""
import json
import re
from html import escape, unescape

D = None  # dati/esempi_livelli.json
PAGINE = []  # percorsi generati, per controlli()
CLIC_LIBRO = "libro-livelli"  # etichetta propria delle 4 pagine (decisione del 25/11/2026), per misurarle a parte da /esempi/
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
    return G.data_breve(D["verificato_il"])


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
        dim = (f'{f["numero"]} file' if f.get("numero") else "") if not f.get("byte") else G.peso(f["byte"])
        dettagli = " · ".join(x for x in (dim, f'{f["pagine"]} pag.' if f.get("pagine") else "") if x)
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


def tabella_file(G, *gruppi):
    diretti = [x for x in gruppi if D["gruppi"][x].get("link_diretti", True)]
    n = sum(len(D["gruppi"][x]["file"]) for x in diretti)
    siti = " e ".join(dict.fromkeys(G.host(f["url"]) for x in diretti for f in D["gruppi"][x]["file"]))
    senza = {D["gruppi"][x]["ente"] for x in gruppi if not D["gruppi"][x].get("link_diretti", True)}
    nota_senza = (f" Per CERT.IT il link porta alla pagina ufficiale, non al file: le {A('certit_note', 'note legali di Roma Tre')} "
                  "vietano i link diretti da altri siti.") if "CERT.IT" in senza else ""
    nota_senza += (" Per CELI il link porta alla pagina del CVCL: i file stanno su www.unistrapg.it, che dal nostro server non si è aperto "
                   "(errore di certificato), e non mettiamo link a file che non abbiamo aperto.") if "CELI" in senza else ""
    return ('<div class="tab-wrap ris-tab liv-tab"><table class="conf"><thead><tr><th scope="col">Ente</th><th scope="col">Esame</th>'
            '<th scope="col">Parte</th><th scope="col">Formato</th><th scope="col">File ufficiale</th></tr></thead>'
            f'<tbody>{"".join(righe_file(G, x) for x in gruppi)}</tbody></table></div>'
            f'<div class="fonte">{G.ic("ok")}<span>Link controllati il {V(G)}: i {n} file con link diretto si aprono sul sito {escape(siti)} '
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


def scrivi(G, slug, briciola, occhiello, h1, lead, bottoni, blocchi, domande, altri, titolo, desc, prossime):
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
<p><a href="../../#date">Tutte le date B1</a>. Le date degli altri livelli sono nei calendari ufficiali degli enti.</p>
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


ALTRI = [("../", "Prove d'esempio B1"), ("../cils-b1-standard/", "CILS B1 standard"), ("../a1/", "Prove d'esempio A1"), ("../a2/", "Prove d'esempio A2"),
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
    return list(PAGINE)


def controlli(G):
    """Ogni testo tra «» delle 4 pagine è una frase citata o il nome di una fonte; ogni domanda del JSON-LD è visibile; ogni file con link
    diretto del gruppo è nella pagina e punta al sito dell'ente; il riquadro del libro c'è una volta sola, con l'etichetta dei clic giusta."""
    b1c = G.ES["CILS"]
    da_fonti = (" ".join(c["testo"].replace('"', "") for c in D["citazioni"]) + " " + " ".join(f["nome"] for f in D["fonti"].values())
                + " " + " ".join(c["testo"] for c in b1c.get("citazioni", [])) + " " + b1c["pagina"]["nome"] + " «Preparati all'esame» «Scarica i materiali»").lower()
    host_enti = ("cils.unistrasi.it", "cms.plida.dante.global")
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
        if len(libro) not in (1, 2) or any(f'data-goatcounter-click="esameb1.eu/clic/{CLIC_LIBRO}"' not in x for x in libro):
            errori.append(f"{p}: riquadro del libro assente, doppio o con un'altra etichetta dei clic")
        tab = main[main.find('liv-tab'):]
        for u in re.findall(r'href="(https?://[^"]+\.(?:pdf|mp3|zip))"', tab[:tab.find("</table>")], re.I):
            if G.host(unescape(u)) not in host_enti:
                errori.append(f"{p}: link a un file fuori dai siti degli enti: {u}")
    urls = {f["url"] for g in D["gruppi"].values() for f in g["file"] if f.get("url")}
    tutte = " ".join((G.SITO / p / "index.html").read_text(encoding="utf-8") for p in PAGINE)
    for u in urls:
        if escape(u) not in tutte:
            errori.append(f"file di dati/esempi_livelli.json non usato in nessuna pagina: {u}")
    if errori:
        raise SystemExit("ERRORI NELLE PAGINE DEGLI ESEMPI PER LIVELLO (genera_livelli.py):\n" + "\n".join(errori))
    return len(PAGINE)
