"""Sezione inglese di EsameB1 (/en/, dal 31/10/2026): 14 pagine guida + privacy per gli stranieri in Italia che leggono meglio
l'inglese (Pakistan, India, Bangladesh, Filippine, Nigeria, Sri Lanka, Ghana...). Fronte: studio-business/intelaiatura/
fronti-2026-10-31-lingue-immigrati.md (riga 1, voto 7,5; punto 7: solo pagine guida, niente traduzione delle pagine città).

Regole:
- ogni cifra e ogni data viene dai file in dati/ (gli stessi delle pagine italiane), mai scritta a mano: dove il dato è una frase
  italiana il numero si estrae con un'espressione regolare (num()) e, se la frase cambia, la generazione si ferma;
- ogni pagina ha la pagina italiana equivalente (hreflang it/en/x-default reciproci) oppure, se non esiste, nessun hreflang
  e i link alle sezioni italiane che usa (COPPIE, terzo campo);
- controlli() gira dopo la generazione: le cifre di ogni pagina /en/ devono comparire nelle pagine italiane di riferimento,
  gli hreflang devono essere reciproci, il calcolatore dei redditi deve essere identico a quello italiano.

Usato da genera.py (G = il modulo genera): genera(G, prossime) scrive le pagine e restituisce gli URL per la sitemap;
controlli(G) controlla il sito scritto. Nessuna dipendenza esterna.
"""
import json
import re
from datetime import date
from decimal import Decimal
from html import escape, unescape

# (pagina inglese, pagina italiana equivalente o None, pagine italiane di riferimento per le cifre)
COPPIE = [
    ("en/", "index.html", ["come-funziona/index.html", "costo/index.html", "reddito-minimo-cittadinanza/index.html", "esonero-test-italiano/index.html"]),
    ("en/italian-b1-exam-for-citizenship/", "come-funziona/index.html", ["costo/index.html", "esonero-test-italiano/index.html", "risultati/index.html", "index.html", "esenzioni-e-domande/index.html"]),
    ("en/b1-exam-dates/", None, ["index.html"]),
    ("en/b1-exam-cost/", "costo/index.html", ["come-funziona/index.html"]),
    ("en/b1-exam-results/", "risultati/index.html", ["risultati/cils/index.html", "risultati/celi/index.html", "risultati/plida/index.html", "risultati/cert-it/index.html"]),
    ("en/cils/", "ente/cils/index.html", ["risultati/cils/index.html", "esempi/cils/index.html"]),
    ("en/celi/", "ente/celi/index.html", ["risultati/celi/index.html", "esempi/celi/index.html"]),
    ("en/plida/", "ente/plida/index.html", ["risultati/plida/index.html", "esempi/plida/index.html"]),
    ("en/cert-it/", "ente/certit/index.html", ["risultati/cert-it/index.html", "esempi/certit/index.html"]),
    ("en/sample-papers/", "esempi/index.html", ["esempi/cils/index.html", "esempi/celi/index.html", "esempi/plida/index.html", "esempi/certit/index.html", "come-funziona/index.html"]),
    ("en/language-test-exemptions/", "esonero-test-italiano/index.html", []),
    ("en/income-requirement-italian-citizenship/", "reddito-minimo-cittadinanza/index.html", []),
    ("en/apply-italian-citizenship-by-residence/", "cittadinanza/index.html", ["reddito-minimo-cittadinanza/index.html"]),
    ("en/carta-di-soggiorno-requirements/", None, ["reddito-minimo-cittadinanza/index.html", "esonero-test-italiano/index.html"]),
    ("en/family-reunification-income/", "reddito-ricongiungimento-familiare/index.html", []),
    ("en/privacy/", "privacy.html", []),
]
# Pagina italiana → pagina inglese (letto da genera.pagina() per gli hreflang e per il link «English» del menu).
IT_EN = {it: en for en, it, _ in COPPIE if it}
# en/b1-exam-dates/ non ha un equivalente italiano a sé (in italiano il calendario è la home, già accoppiata a /en/):
# niente hreflang, link visibile al calendario italiano.

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
GIORNI_EN = {"lunedì": "Monday", "martedì": "Tuesday", "mercoledì": "Wednesday", "giovedì": "Thursday", "venerdì": "Friday", "sabato": "Saturday", "domenica": "Sunday"}
# Numeri scritti in lettere nelle fonti italiane (citazioni di legge): servono per leggere la cifra dalla frase, non per inventarla.
PAROLE_NUMERO = {"un": 1, "uno": 1, "tre": 3, "cinque": 5, "dieci": 10, "quattordici": 14, "ventiquattro": 24, "trentasei": 36, "sessanta": 60, "ottanta": 80}
NOME_EN = {"CILS": "University for Foreigners of Siena", "CELI": "University for Foreigners of Perugia",
           "PLIDA": "Società Dante Alighieri", "CERT.IT": "Roma Tre University"}
SLUG_EN = {"CILS": "cils", "CELI": "celi", "PLIDA": "plida", "CERT.IT": "cert-it"}
TITOLO_ENTE_EN = {"CILS": "CILS B1 Cittadinanza exam", "CELI": "CELI B1 citizenship exam (CELI 2 i)",
                  "PLIDA": "PLIDA B1 exam for citizenship", "CERT.IT": "CERT.IT B1 exam (Roma Tre)"}
PROVE_EN = {"ascolto": "listening", "lettura": "reading", "scrittura": "writing", "orale": "speaking"}
FRASE_AMAZON_EN = "As an Amazon Associate I earn from qualifying purchases."

PAGINE = []  # pagine scritte: {"en": percorso, "it": percorso o None, "rif": [...]} (per controlli())


# ---------------------------------------------------------------- dati → testo inglese
def num(testo, regola, gruppo=1):
    """La cifra (come stringa) letta dalla frase italiana di un file dati. Se la frase cambia la generazione si ferma:
    il testo inglese va riletto e aggiornato, non indovinato."""
    m = re.search(regola, testo or "")
    if not m:
        raise SystemExit(f"genera_en: dato cambiato, aggiornare il testo inglese: «{regola}» non trovato in «{(testo or '')[:160]}»")
    g = m.group(gruppo)
    return str(PAROLE_NUMERO[g]) if g in PAROLE_NUMERO else g


def d(iso):
    return date.fromisoformat(iso)


def data_en(iso):
    x = d(iso)
    return f"{x.day} {MONTHS[x.month - 1]} {x.year}"


def data_lunga_en(iso):
    x = d(iso)
    return f"{DAYS[x.weekday()]} {x.day} {MONTHS[x.month - 1]} {x.year}"


def giorno_mese_en(iso):
    x = d(iso)
    return f"{x.day} {MONTHS[x.month - 1]}"


def data_it_en(testo):
    """«9 dicembre 2010» → «9 December 2010» (si ferma se non trova una data)."""
    m = re.search(r"(\d{1,2}) (" + "|".join(MESI) + r") (\d{4})", testo or "")
    if not m:
        raise SystemExit(f"genera_en: nessuna data in «{(testo or '')[:120]}»")
    return f"{int(m.group(1))} {MONTHS[MESI.index(m.group(2))]} {m.group(3)}"


def eur(x, decimali=True):
    """Decimal o stringa → «€8,263.31» (o «€250» con decimali=False e importo intero)."""
    x = Decimal(str(x))
    if not decimali and x == x.to_integral_value():
        return f"€{int(x):,}"
    return f"€{x.quantize(Decimal('0.01')):,.2f}"


def eur_c(c):
    return eur(Decimal(c) / 100)


def tempo_en(t):
    """Tempi delle prove da enti.json (fatti.durata.prove) in inglese."""
    for regola, fmt in ((r"^(\d+(?:-\d+)?) min circa$", "about {} min"), (r"^(\d+) min \(con la grammatica\)$", "{} min (with grammar)"),
                        (r"^(\d+(?:-\d+)?) min$", "{} min"), (r"^(\d+) ore, lettura e scrittura insieme$", "{} hours (reading and writing together)"),
                        (r"^(\d+) min in tutto, le tre prove insieme$", "{} min in total (the three parts together)")):
        m = re.match(regola, t)
        if m:
            return fmt.format(m.group(1))
    raise SystemExit(f"genera_en: tempo non riconosciuto «{t}»: aggiornare tempo_en()")


def totale_en(t):
    m = re.match(r"^(circa )?(\d+) or[ae](?: e (\d+) min)? \((somma delle prove|dato ufficiale)\)$", t)
    if not m:
        raise SystemExit(f"genera_en: totale non riconosciuto «{t}»: aggiornare totale_en()")
    circa, ore, minuti, tipo = m.groups()
    testo = f"{'about ' if circa else ''}{ore} h{f' {minuti} min' if minuti else ''}"
    return testo + (" (sum of the parts)" if tipo == "somma delle prove" else " (official figure)")


def esame_en(x):
    return x.replace("(sessione A2/B1)", "(A2/B1 session)")


# ---------------------------------------------------------------- pezzi di pagina
JS_SOST = [  # testo italiano del JS comune → inglese (si ferma se il JS cambia)
    ("el.textContent=g===0?'oggi':g===1?'domani':'tra '+g+' giorni';", "el.textContent=g===0?'today':g===1?'tomorrow':'in '+g+' days';"),
    ("el.textContent=g===0?'scade oggi':'mancano '+g+(g===1?' giorno':' giorni');", "el.textContent=g===0?'closes today':g+(g===1?' day left':' days left');"),
    ("'termine nazionale passato: chiedi alla sede se accetta ancora iscrizioni'", "'national deadline passed: ask the centre if it still accepts registrations'"),
    ("'Mostra tutte le '+vis.length+' date'", "'Show all '+vis.length+' dates'"),
    ("(vis.length===1?' sessione':' sessioni')", "(vis.length===1?' session':' sessions')"),
    ("' per la cittadinanza'", "' for citizenship'"),
]


def js_en(G):
    js = G.JS
    for a, b in JS_SOST:
        if a not in js:
            raise SystemExit(f"genera_en: il JS di genera.py è cambiato, aggiornare JS_SOST: {a}")
        js = js.replace(a, b)
    return js


def ic(G, nome):
    return G.ic(nome)


def testo_conta(iso, modo, oggi):
    g = (d(iso) - oggi).days
    if modo == "esame":
        return "today" if g == 0 else "tomorrow" if g == 1 else f"in {g} days"
    return "closes today" if g == 0 else f"{g} {'day' if g == 1 else 'days'} left"


def nota_en(G, s):
    """Nota sulla scadenza in inglese, letta dalla nota italiana di sessioni.json (date comprese)."""
    n = s["nota_scadenza"]
    if s["ente"] == "CILS":
        num(n, r"(Università per Stranieri di Siena)")
        return "Deadline set by the University for Foreigners of Siena: exam centres may close registrations earlier."
    if s["ente"] == "CELI":
        num(n, r"(Università per Stranieri di Perugia)")
        return "Deadline set by the University for Foreigners of Perugia: exam centres may close registrations earlier."
    if s["ente"] == "PLIDA":
        num(n, r"(ogni centro PLIDA)")
        return "Each PLIDA centre sets its own deadline: ask the centre you choose."
    if s["ente"] == "CERT.IT":
        return (f"Registration opens on {data_it_en(num(n, r'Iscrizioni aperte dal?l?.?(\d{1,2} \w+ \d{4})'))} at the partner centres, which set the deadline. "
                "Confirm the exact day with the centre.")
    raise SystemExit(f"genera_en: ente sconosciuto {s['ente']}")


def nota_comune_en(G, s):
    return G.nota_comune(s)


def scheda_sessione(G, s):
    citt = s["tipo"] == "cittadinanza"
    badge = (f'<span class="tag citt">{G.ic("ok")}Citizenship exam</span>' if citt
             else f'<span class="tag">{G.ic("ok")}B1 valid for citizenship</span>')
    nota = "" if G.nota_comune(s) else f'<div class="nota">{escape(nota_en(G, s))}</div>'
    scad = (f'<span class="scad" data-scadenza="{s["scadenza"]}">{G.ic("orologio")}Register by <strong>{data_en(s["scadenza"])}</strong>'
            f'<span class="stato conta"></span></span>') if s.get("scadenza") else ""
    x = d(s["data"])
    tile = (f'<div class="tile" aria-hidden="true"><span class="tm">{MONTHS[x.month - 1][:3]}</span>'
            f'<span class="td">{x.day}</span><span class="ty">{x.year}</span></div>')
    return f"""<article class="sess" data-data="{s['data']}" data-ente="{escape(s['ente'])}" data-tipo="{s['tipo']}">
{tile}
<div class="cosa"><div class="testa">{G.eb(s['ente'])}<span class="nome">{escape(", ".join(esame_en(e) for e in s["esami"]))}</span>{badge}</div>
<div class="quando"><time datetime="{s['data']}">{data_lunga_en(s['data'])}</time>{scad}</div>
{nota}
<div class="fonte">{G.ic("doc")}<span>Source: <a href="{escape(s['fonte'])}" rel="noopener">official {escape(s['ente'])} calendar</a> · checked on {data_en(s['verificato_il'])}</span></div>
</div>
</article>"""


def lista_sessioni(G, lista, con_filtri=True):
    righe, viste = [], set()
    for e in G.ENTE:
        for s in lista:
            if s["ente"] == e and G.nota_comune(s) and s["nota_scadenza"] not in viste:
                viste.add(s["nota_scadenza"])
                righe.append(f'<li>{G.eb(e)}<span>{escape(nota_en(G, s))}</span></li>')
    note = f'<ul class="note-scad" aria-label="How to read the deadlines">{"".join(righe)}</ul>' if righe else ""
    filtri = ""
    if con_filtri:
        bottoni = ['<button type="button" data-filtro="tutti" aria-pressed="true">All</button>',
                   f'<button type="button" data-filtro="citt" aria-pressed="false">{G.ic("ok")}Citizenship only</button>']
        bottoni += [f'<button type="button" data-filtro="{e}" aria-pressed="false"><span class="pt" style="background:var(--{e.replace(".", "").lower()})"></span>{e}</button>'
                    for e in G.ENTE]
        filtri = (f'<div class="filtri chips" role="group" aria-label="Filter by exam body">{"".join(bottoni)}</div>'
                  '<p class="esito" aria-live="polite"></p>')
    return (f'<div data-elenco>{note}{filtri}<div class="sessioni">' + "\n".join(scheda_sessione(G, s) for s in lista)
            + '</div><button class="btn btn-2 mostra" type="button" hidden>Show all dates</button></div>')


def risposta(G, prossime, rel):
    """Scheda «Next exam / Registration still open», come quella italiana (il JS la tiene aggiornata)."""
    opz_e = []
    for i, s in enumerate(prossime[:12]):
        x = d(s["data"])
        opz_e.append(f"""<div data-fino="{s['data']}"{"" if i == 0 else " hidden"}>
<div class="r-data">{x.day} {MONTHS[x.month - 1]} <small>{x.year}</small></div>
<div class="r-cosa">{G.eb(s['ente'])}<span>{escape(", ".join(esame_en(e) for e in s['esami']))}</span></div>
<p style="margin:12px 0 0"><span class="conta {G.classe_conta(s['data'], 'esame')}" data-conta="{s['data']}" data-modo="esame">{testo_conta(s['data'], 'esame', G.OGGI)}</span></p>
</div>""")
    con_scad = sorted((s for s in prossime if s.get("scadenza")), key=lambda s: (s["scadenza"], s["data"]))
    opz_s, primo = [], True
    for s in con_scad:
        visibile = primo and d(s["scadenza"]) >= G.OGGI
        if visibile:
            primo = False
        opz_s.append(f"""<div data-fino="{s['scadenza']}"{"" if visibile else " hidden"}>
<div class="r-data"><small>by</small> {data_en(s['scadenza'])}</div>
<div class="r-cosa">for the {G.eb(s['ente'])} exam on <strong>{giorno_mese_en(s['data'])}</strong></div>
<p style="margin:12px 0 0"><span class="conta {G.classe_conta(s['scadenza'], 'scad')}" data-conta="{s['scadenza']}" data-modo="scad">{testo_conta(s['scadenza'], 'scad', G.OGGI)}</span></p>
<p class="r-nota">This is the national deadline: the centre may close earlier. Always ask for confirmation.</p>
</div>""")
    riserva = ('<p data-riserva class="r-nota"{}>No national deadline is open right now: for PLIDA and CERT.IT each centre sets the deadline. '
               'Ask the centre.</p>').format("" if primo else " hidden")
    return f"""<div class="risposta">
<div class="slot" data-slot><div class="r-et">{G.ic("cal")}Next exam</div>{"".join(opz_e)}</div>
<div class="slot" data-slot><div class="r-et">{G.ic("orologio")}Registration still open</div>{"".join(opz_s)}{riserva}</div>
<div class="r-piede"><a href="{rel}b1-exam-dates/">All dates {G.ic("freccia")}</a><span>{G.ic("info")}Exam dates are the same all over Italy.</span></div>
</div>"""


def modulo(G, rel):
    opzioni = "".join(f'<option value="{escape(c["nome"])}">{escape(c["nome"])}</option>' for c in sorted(G.citta, key=lambda c: c["nome"]))
    enti_opt = "".join(f'<option value="{e}">{e}</option>' for e in G.ENTE)
    return f"""<section class="card" id="avvisami">
<div class="modulo-testa"><span class="bolla">{G.ic("campana")}</span><div>
<h2>Email me when new dates come out</h2>
<p class="small" style="margin:4px 0 0">Free. We write when a new exam session is published or when a deadline is about to close in your city. Emails are in Italian.</p></div></div>
<form class="form avvisami" name="avvisami" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="avvisami">
<input type="hidden" name="source" value="">
<p class="hp"><label>Do not fill in <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Your email<input type="email" name="email" required autocomplete="email" placeholder="name@example.com"></label>
<label>City where you want to take the exam
<select name="citta" required><option value="">Choose a city</option>{opzioni}<option value="Altra città">Other city</option></select></label>
<label>Preferred exam body (optional)
<select name="ente"><option value="">No preference</option>{enti_opt}</select></label>
<label class="check"><input type="checkbox" name="consenso" value="si" required>
<span>I agree to receive emails from {G.NOME} about B1 exam dates. I can unsubscribe at any time. I have read the <a href="{rel}privacy/">privacy notice</a>.</span></label>
<button class="btn" type="submit">{G.ic("campana")}Notify me</button>
<p class="errore" data-errore hidden>Sending failed. Please try again in a moment.</p>
</form>
<div class="ok" data-ok hidden>{G.ic("ok")}<span><strong>Done!</strong> We will write when there is news for your city.</span></div>
</section>"""


def riquadro_preparati(G, rel):
    """Riquadro italki/Amazon in inglese (stessi link di dati/affiliati.json, con le frasi di trasparenza in inglese)."""
    url, amazon = G.url_affiliato("italki"), G.url_affiliato("amazon")
    if not url and not amazon:
        return ""
    italki_txt = " On italki you choose an Italian teacher, take one-to-one lessons and pay per lesson." if url else ""
    btn = (f'<a class="btn" href="{escape(url)}" rel="sponsored noopener" target="_blank">{G.ic("voce")}Find an Italian teacher on italki</a>' if url else "")
    libri = (f'\n<p class="prep-libri">{G.ic("libro")}<a href="{escape(amazon)}" rel="sponsored noopener" target="_blank">'
             f'Books to prepare for the B1 exam on Amazon.it</a></p>\n<p class="small aff-nota">{FRASE_AMAZON_EN}</p>' if amazon else "")
    return f"""<section class="card prep" id="preparati" aria-labelledby="preparati-titolo">
<span class="bolla">{G.ic("voce")}</span>
<div>
<h2 id="preparati-titolo">Prepare for the speaking test</h2>
<p>The speaking test is the part that worries many people. It helps to talk often with a native-speaker teacher, even online.{italki_txt}</p>
<div class="azioni">{btn}<a class="btn btn-2" href="{rel}sample-papers/">{G.ic("libro")}Free official sample papers</a></div>{libri}
{G.MON.nota_trasparenza("en")}
</div>
</section>"""


def avviso(G, testo):
    return G.avviso(testo)


def decide(G, chi="The Prefecture"):
    return avviso(G, f"This page summarises official sources in English; it is not legal advice. <strong>{chi} decides your case.</strong> "
                     "For your situation ask them or a patronato (free advice office).")


def nota_esame(G):
    """Avviso per le pagine sull'esame: le date le conferma la sede, sul certificato per la cittadinanza decide la Prefettura."""
    return avviso(G, "This site is independent and gives no legal advice. Exam centres confirm dates, prices and deadlines; "
                     "<strong>for your citizenship application, the Prefecture decides</strong> which certificate is valid.")


def briciole(G, *voci):
    parti = [f'<a href="{h}">{escape(t)}</a>' if h else f'<span aria-current="page">{escape(t)}</span>' for t, h in voci]
    return f'<nav class="briciole" aria-label="You are here">{" <span aria-hidden=\"true\">›</span> ".join(parti)}</nav>'


def in_italiano(G, it_href, testo):
    """Link visibile alla pagina italiana equivalente (con hreflang)."""
    return f'<p class="small lingua-alt">{G.ic("web")}<span lang="it">In italiano:</span> <a href="{it_href}" hreflang="it" lang="it">{escape(testo)}</a></p>'


def fonte(G, link, data_iso, parola="Source"):
    return f'<div class="fonte">{G.ic("doc")}<span>{parola}: {link} · checked on {data_en(data_iso)}</span></div>'


def a(url, testo):
    return f'<a href="{escape(url)}" rel="noopener">{escape(testo)}</a>'


def faq_blocco(G, faq):
    html_faq = "".join(G.domanda(q, t) for q, t in faq)
    return html_faq, {"@context": "https://schema.org"} | G.faq_jsonld(faq)


GUIDE = [  # (percorso relativo a /en/, icona, titolo, sottotitolo)
    ("b1-exam-dates/", "cal", "B1 exam dates", "all sessions, body by body"),
    ("italian-b1-exam-for-citizenship/", "lista", "The B1 exam for citizenship", "what it is, bodies, how long it lasts"),
    ("b1-exam-cost/", "euro", "How much the exam costs", "official prices, body by body"),
    ("b1-exam-results/", "ok", "Exam results", "when and where you see them"),
    ("sample-papers/", "libro", "Free sample papers", "official PDF and audio"),
    ("language-test-exemptions/", "scudo", "Exemptions from the language test", "B1 for citizenship, A2 for the carta"),
    ("income-requirement-italian-citizenship/", "euro", "Income requirement", "citizenship and carta di soggiorno, calculator"),
    ("apply-italian-citizenship-by-residence/", "edificio", "How to apply for citizenship", "ALI portal, fee, legal time limit"),
    ("carta-di-soggiorno-requirements/", "doc", "Carta di soggiorno requirements", "years, income, A2 test"),
    ("family-reunification-income/", "pin", "Family reunification income", "table by number of family members"),
    ("cils/", "scudo", "CILS (Siena)", "dates, cost, results"),
    ("celi/", "scudo", "CELI (Perugia)", "dates, cost, results"),
    ("plida/", "scudo", "PLIDA (Dante Alighieri)", "dates, cost, results"),
    ("cert-it/", "scudo", "CERT.IT (Roma Tre)", "dates, cost, results"),
]


def griglia_guide(G, rel, salta=None):
    return '<div class="griglia link3">' + "".join(
        f'<a href="{rel}{h}">{G.ic(i)}<span>{t}<small>{sm}</small></span></a>' for h, i, t, sm in GUIDE if h != salta) + "</div>"


# ---------------------------------------------------------------- struttura della pagina
def pagina_en(G, percorso, titolo, descrizione, corpo, it=None, jsonld=None):
    """Scrive sito/<percorso>index.html in inglese. it: percorso della pagina italiana equivalente (hreflang reciproci)."""
    voce = next((c for c in COPPIE if c[0] == percorso), None)
    if voce is None or voce[1] != it:
        raise SystemExit(f"genera_en: {percorso} non è in COPPIE o ha una pagina italiana diversa")
    if len(titolo) > G.MAX_TITOLO or len(descrizione) > G.MAX_DESC:
        raise SystemExit(f"{percorso}: titolo {len(titolo)}/{G.MAX_TITOLO} o description {len(descrizione)}/{G.MAX_DESC} troppo lunghi")
    profondita = percorso.count("/")
    rel_root = "../" * profondita  # radice del sito
    rel = "../" * (profondita - 1) or "./"  # radice di /en/
    canonico = G.URL_SITO + "/" + percorso
    alternati = ""
    it_href = f"{rel_root}{it[:-10] if it.endswith('index.html') else it}" if it else None
    if it:
        url_it = G.URL_SITO + "/" + (it[:-10] if it.endswith("index.html") else it)
        alternati = (f'\n<link rel="alternate" hreflang="it" href="{url_it}">\n<link rel="alternate" hreflang="en" href="{canonico}">'
                     f'\n<link rel="alternate" hreflang="x-default" href="{url_it}">')
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    avvisami = "#avvisami" if 'id="avvisami"' in corpo else f"{rel}#avvisami"
    lingua = it_href or f"{rel_root}"
    guide_piede = "".join(f'<li><a href="{rel}{h}">{t}</a></li>' for h, _, t, _ in GUIDE)
    verificato = data_en(max([s["verificato_il"] for s in G.sessioni] + [s["verificato_il"] for s in G.sedi]))
    testo = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titolo)}</title>
<meta name="description" content="{escape(descrizione)}">
<link rel="canonical" href="{canonico}">{alternati}
<meta property="og:title" content="{escape(titolo)}">
<meta property="og:description" content="{escape(descrizione)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_GB">
<meta property="og:image" content="{G.URL_SITO}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:url" content="{canonico}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0B6B4F">
<meta name="google-site-verification" content="{G.GOOGLE_VERIFICA}">{G.ADSENSE_HEAD}
<link rel="icon" href="{G.FAVICON}">
<link rel="preload" href="/fonts/figtree.woff2" as="font" type="font/woff2" crossorigin>
<style>{G.CSS}</style>
{ld}
</head>
<body>
{G.SPRITE}
<a class="salta" href="#contenuto">Skip to content</a>
<header class="top"><div class="wrap">
<a class="logo" href="{rel}" aria-label="{G.NOME} in English, home page">{G.MARCHIO}<span class="logo-testo">Esame<b>B1</b></span></a>
<nav class="menu" aria-label="Menu">
<a href="{rel}b1-exam-dates/">Dates</a><a href="{rel}#guides">Guides</a><a class="lingua" href="{lingua}" hreflang="it" lang="it"><span class="lungo">Italiano</span><span class="corto">IT</span></a><a class="nav-cta" href="{avvisami}" aria-label="Notify me">{G.ic("campana")}<span class="lungo">Notify me</span></a>
</nav>
</div></header>
<main class="wrap" id="contenuto">
{corpo}{G.MON.riga_trasparenza(corpo, "en")}
</main>
<footer class="piede"><div class="wrap">
<div class="piede-griglia">
<div>
<a class="logo" href="{rel}">{G.MARCHIO}<span class="logo-testo">Esame<b>B1</b></span></a>
<ul class="piede-link">
<li><a href="{rel}">EsameB1 in English</a></li>{guide_piede}<li><a href="{lingua}" hreflang="it" lang="it">Italiano</a></li><li><a href="{rel}privacy/">Privacy</a></li>
</ul>
</div>
<div>
<p><strong>{G.NOME}</strong> is an independent website, not affiliated with the exam bodies, the Ministry of the Interior, the Prefectures or the Questure. CILS, CELI, PLIDA and CERT.IT are trademarks of their owners.
Every figure comes from the official source shown next to it. <strong>Before you register or apply, always check with the exam centre, the Prefecture or the Questura: they decide.</strong>
This site gives no legal advice on citizenship or residence permits: see the <a href="https://www.interno.gov.it/it/temi/cittadinanza-e-altri-diritti-civili/cittadinanza" rel="noopener" hreflang="it">Ministry of the Interior page (in Italian)</a>.</p>
<p><span class="dati">{G.ic("scudo")}Data checked on {verificato}.</span></p>
</div>
</div>
<div class="piede-altri"><h2>Other free tools</h2><ul><li><a href="https://italy-strikes-today.netlify.app/" rel="noopener">Italy Strikes Today</a>: train, air and local transport strikes in Italy, from the official register of the Ministry. Another free, independent site by the same publisher.</li></ul></div>
</div></footer>
<script>{js_en(G)}</script>
{G.SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = G.SITO / percorso / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo)
    PAGINE.append({"en": percorso + "index.html", "it": it, "rif": voce[2]})


# ---------------------------------------------------------------- pagine
def fatti_brevi(G):
    """Cifre per ente prese da enti.json: costo, tempi, durata (ognuna con la sua frase italiana d'origine)."""
    E = G.ENTE
    certit = num(E["CERT.IT"]["fatti"]["costo"]["breve"], r"^(\d+) €")
    celi_t = E["CELI"]["fatti"]["costo"]["testo"]
    return {
        "cils": E["CILS"]["prezzo_eur"],
        "cils_url": E["CILS"]["prezzo_url"],
        "padova": num(E["CILS"]["fatti"]["costo"]["testo"], r"Padova costa (\d+) €"),
        "certit": certit,
        "celi_tot": num(celi_t, r"(\d+) € all'Università degli Studi di Milano"),
        "celi_tassa": num(celi_t, r"\((\d+) € di tassa d'esame"),
        "celi_spese": num(celi_t, r"\+ (\d+) € di spese amministrative"),
        "celi_data": data_it_en(num(celi_t, r"sessione del (\d{1,2} \w+ \d{4})")),
    }


def tabella_durata(G):
    righe = []
    for e in G.enti:
        p = e["fatti"]["durata"]["prove"]
        parti = "<br>".join(f'{", ".join(PROVE_EN[x] for x in q["prove"]).capitalize()}: {tempo_en(q["tempo"])}' for q in p["parti"])
        righe.append(f'<tr><td>{G.eb(e["sigla"])}</td><td data-l="Parts">{parti}</td><td data-l="In total"><strong>{totale_en(p["totale"])}</strong></td></tr>')
    v = max(e["fatti"]["durata"]["verificato_il"] for e in G.enti)
    fonti = " · ".join(a(f["url"], f["nome"]) for e in G.enti for f in e["fatti"]["durata"]["fonti"][:1])
    return (f'<div class="tab-wrap rc-tab"><table class="conf"><thead><tr><th scope="col">Exam</th><th scope="col">Parts and time</th><th scope="col">In total</th></tr></thead>'
            f'<tbody>{"".join(righe)}</tbody></table></div>{fonte(G, fonti, v, "Sources (in Italian)")}')


def tabella_prossime(G, prossime, rel):
    righe = []
    for e in G.ENTE:
        s = next((x for x in prossime if x["ente"] == e), None)
        sc = next((x for x in prossime if x["ente"] == e and x.get("scadenza") and d(x["scadenza"]) >= G.OGGI), None)
        prima = (f'<time datetime="{s["data"]}">{data_en(s["data"])}</time><br><span class="small">{escape(esame_en(s["esami"][0]))}</span>' if s
                 else "no new date published yet")
        scad = (f'by {data_en(sc["scadenza"])}<br><span class="small">for the exam on {giorno_mese_en(sc["data"])}</span>' if sc
                else "set by each centre" if e in ("PLIDA", "CERT.IT") else "no open national deadline")
        righe.append(f'<tr><td><a href="{rel}{SLUG_EN[e]}/">{G.eb(e)}</a><br><span class="small">{escape(NOME_EN[e])}</span></td>'
                     f'<td data-l="Next exam">{prima}</td><td data-l="Register by">{scad}</td></tr>')
    return ('<div class="tab-wrap rc-tab"><table class="conf"><thead><tr><th scope="col">Exam body</th><th scope="col">Next exam</th>'
            f'<th scope="col">National deadline</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>')


def hub(G, prossime):
    F = fatti_brevi(G)
    R = G.REDDITI["cittadinanza"]
    p = prossime[0]
    v_sess = max(s["verificato_il"] for s in G.sessioni)
    esoneri_v = G.esoneri["verificato_il"]
    faq = [
        ("Which Italian exam do I need for citizenship?",
         "You need an Italian language certificate at level B1 or higher from a recognised body. The 4 main bodies, with exam centres all over Italy, are "
         "CILS (University for Foreigners of Siena), CELI (University for Foreigners of Perugia), PLIDA (Società Dante Alighieri) and CERT.IT (Roma Tre University). "
         "The Ministry of the Interior's Vademecum also lists the University for Foreigners «Dante Alighieri» of Reggio Calabria. "
         '<a href="language-test-exemptions/">Who is exempt</a>.'),
        ("Can I take the B1 citizenship exam online?",
         'No. The exam is taken in person at an exam centre, with an identity document. <a href="italian-b1-exam-for-citizenship/#online">Official sources</a>.'),
        ("How much does the B1 exam cost?",
         f"CILS B1 Cittadinanza: {eur(F['cils'], False)}, the same fee everywhere. CERT.IT B1: {eur(F['certit'], False)} at Roma Tre. "
         f"CELI and PLIDA: each centre sets the price (for example {eur(F['celi_tot'], False)} for the CELI 2 i cittadinanza at the University of Milan). "
         '<a href="b1-exam-cost/">All prices, with sources</a>.'),
        ("Do I need the B1 exam if I have a carta di soggiorno?",
         "According to the law and the Ministry of the Interior, holders of the EU long-term residence permit (the carta di soggiorno) do not have to present the B1 certificate. "
         'The Prefecture decides. <a href="language-test-exemptions/">Exemptions, with sources</a>.'),
        ("Is there an income requirement for Italian citizenship?",
         f"Yes, for citizenship by residence: at least {eur(R['solo'])} a year of taxable income if you are alone, {eur(R['con_coniuge'])} with a dependent spouse, "
         f'plus {eur(R["per_figlio"])} for each dependent child. <a href="income-requirement-italian-citizenship/">Table and calculator</a>.'),
    ]
    faq_html, ld = faq_blocco(G, faq)
    corpo = f"""<section class="hero">
<span class="occhiello">{G.ic("scudo")}CILS · CELI · PLIDA · CERT.IT · in English</span>
<h1>Italian B1 exam for citizenship: dates and guides in English</h1>
<p class="lead">According to the official calendars of CILS, CELI, PLIDA and CERT.IT (checked on {data_en(v_sess)}), the next B1 exam in Italy is on {data_en(p["data"])} ({p["ente"]}).
These English guides explain the exam, the income requirement and the citizenship application, from the same official data as our Italian pages.</p>
{risposta(G, prossime, "")}
<div class="azioni"><a class="btn" href="b1-exam-dates/">{G.ic("cal")}All exam dates</a><a class="btn btn-2" href="#guides">{G.ic("lista")}Guides in English</a></div>
<ul class="cifre"><li>{G.ic("edificio")}<span><strong>{len(G.sedi)}</strong> exam centres in Italy</span></li>
<li>{G.ic("cal")}<span><strong>{len(prossime)}</strong> sessions scheduled</span></li>
<li>{G.ic("doc")}<span>data from official sources</span></li></ul>
</section>
{decide(G, "The Prefecture (citizenship) or the Questura (residence permits)")}
<div class="due">
<section id="dates">
<h2>{G.ic("cal")}Next date for each exam body</h2>
{tabella_prossime(G, prossime, "")}
<p class="small">Each exam centre may set an earlier deadline than the national one. <strong>Always ask the centre before you register.</strong> <a href="b1-exam-dates/">See all {len(prossime)} dates</a>.</p>
</section>
<aside>{modulo(G, "")}</aside>
</div>
<section id="guides">
<h2>{G.ic("lista")}Guides in English</h2>
{griglia_guide(G, "")}
<p class="small">Exam centres by city are listed in Italian: <a href="../#citta" hreflang="it" lang="it">sedi per città</a> (addresses, phone numbers, websites). The exemption rules were last read on {data_en(esoneri_v)}.</p>
</section>
{riquadro_preparati(G, "")}
<section>
<h2>{G.ic("info")}Frequently asked questions</h2>
{faq_html}
</section>
{in_italiano(G, "../", "Esame B1 cittadinanza: tutte le date")}"""
    titolo = G.titolo_pagina(f"Italian B1 citizenship exam {G.anni(prossime)}: next date {giorno_mese_en(p['data'])}",
                             f"Italian B1 citizenship exam: next date {giorno_mese_en(p['data'])}")
    descr = G.descrizione_pagina(
        f"Next Italian B1 exam on {data_en(p['data'])} ({p['ente']}). Dates, cost, results, exemptions, income requirement and how to apply for citizenship, in English.",
        f"Next Italian B1 exam on {data_en(p['data'])} ({p['ente']}). Dates, cost, income requirement and citizenship application, in English.")
    pagina_en(G, "en/", titolo, descr, corpo, it="index.html", jsonld=ld)


def pagina_date(G, prossime):
    v = max(s["verificato_il"] for s in G.sessioni)
    p = prossime[0]
    corpo = f"""<section class="hero">
{briciole(G, ("EsameB1 in English", "../"), ("B1 exam dates", None))}
<h1>Italian B1 citizenship exam dates {G.anni(prossime)}</h1>
<p class="lead">According to the official calendars of the four exam bodies (checked on {data_en(v)}), there are {len(prossime)} B1 exam sessions scheduled in Italy, starting on {data_en(p["data"])} ({p["ente"]}).
Exam dates are national: every centre of the same body holds the exam on the same day, but each centre may close registrations earlier.</p>
{risposta(G, prossime, "../")}
</section>
{avviso(G, "Each centre can have an earlier deadline than the national one. <strong>Before you register, always ask the centre for confirmation.</strong> For your citizenship application, the Prefecture decides.")}
<div class="due">
<section id="dates">
<h2>{G.ic("cal")}All upcoming dates</h2>
{lista_sessioni(G, prossime)}
</section>
<aside>{modulo(G, "../")}</aside>
</div>
<section>
<h2>{G.ic("info")}Before you register</h2>
<p>«Citizenship exam» marks the B1 exams designed for the citizenship application (CILS B1 Cittadinanza, CELI 2 i cittadinanza). The general B1 exams (CILS B1 standard, CELI 2, PLIDA B1, CERT.IT B1) are B1 certificates too.
You register at the exam centre, not on this site: <a href="../../#citta" hreflang="it" lang="it">find a centre in your city (in Italian)</a>.</p>
{griglia_guide(G, "../", salta="b1-exam-dates/")}
</section>
{in_italiano(G, "../../#date", "Prossime date d'esame (calendario in italiano)")}"""
    titolo = G.titolo_pagina(f"B1 exam dates in Italy {G.anni(prossime)}: CILS, CELI, PLIDA, CERT.IT",
                             f"B1 exam dates in Italy {G.anni(prossime)}", "B1 exam dates in Italy")
    descr = G.descrizione_pagina(
        f"All {len(prossime)} B1 exam sessions in Italy for citizenship, from {data_en(p['data'])}: CILS, CELI, PLIDA and CERT.IT dates and national registration deadlines.")
    pagina_en(G, "en/b1-exam-dates/", titolo, descr, corpo)


def online_fonti(G):
    fonti = []
    for e in G.enti:
        f = e.get("fatti", {}).get("nota" if e["sigla"] in ("PLIDA", "CERT.IT") else "documenti")
        if f:
            fonti.append(f["fonti"][0])
    return " · ".join(a(x["url"], x["nome"]) for x in fonti)


def pagina_esame(G, prossime):
    F = fatti_brevi(G)
    Fe = G.esoneri["fonti"]
    v = G.esoneri["verificato_il"]
    righe = "".join(
        f'<tr><td>{G.eb(e["sigla"])}<br><span class="small">{escape(NOME_EN[e["sigla"]])}</span></td>'
        f'<td data-l="Exam for citizenship">{escape(esame_en({"CILS": "CILS B1 Cittadinanza (also CILS B1 standard)", "CELI": "CELI 2 i cittadinanza, only in Italy (also CELI 2)", "PLIDA": "PLIDA B1", "CERT.IT": "CERT.IT B1 (sessione A2/B1)"}[e["sigla"]]))}</td>'
        f'<td data-l="Centres in Italy">{sum(1 for s in G.sedi if s["ente"] == e["sigla"])}</td>'
        f'<td data-l="Guide"><a href="../{SLUG_EN[e["sigla"]]}/">dates, cost, results</a></td></tr>' for e in G.enti)
    p = prossime[0]
    faq = [
        ("Who has to take the B1 Italian exam?",
         "People applying for Italian citizenship by residence or by marriage, unless they are exempt (for example holders of the EU long-term residence permit). "
         "A school qualification in Italian can replace the certificate. The Prefecture decides."),
        ("Is the CILS or the CELI easier?",
         "We do not rank the exams. They differ in length, structure and price: compare the parts in the table on this page and the sample papers of each body."),
        ("Can I take the exam online?",
         "No. All four bodies hold the exam in person at an exam centre."),
        ("Does the B1 certificate expire?",
         "The CELI and CILS certificates have no expiry date, according to their official pages. For your application, the Prefecture decides which certificate is valid."),
    ]
    faq_html, ld = faq_blocco(G, faq)
    corpo = f"""<section class="hero">
{briciole(G, ("EsameB1 in English", "../"), ("The B1 exam for citizenship", None))}
<h1>Italian B1 exam for citizenship: what it is, cost and exemptions</h1>
<p class="lead">According to art. 9.1 of Law 91/1992 and the Ministry of the Interior (sources read on {data_en(v)}), people who apply for Italian citizenship by residence or by marriage must show that they know Italian at level B1 or higher,
with a certificate from a recognised body or a school qualification. Here is how the exam works, in plain English.</p>
</section>
{decide(G)}
<h2>{G.ic("info")}Who has to take it, and who is exempt</h2>
<p>The B1 requirement applies to citizenship by <strong>residence</strong> and by <strong>marriage</strong>. According to the law and the Ministry, you do not have to present the certificate if you signed the integration agreement
(accordo di integrazione), if you hold the <strong>EU long-term residence permit</strong> (the carta di soggiorno), or if you have serious limitations in learning the language certified by a public health facility.
A school qualification taken in Italian can replace the certificate. <a href="../language-test-exemptions/">All exemptions, with sources</a>.</p>
{fonte(G, a(Fe["legge91"]["url"], Fe["legge91"]["nome"]) + " · " + a(Fe["vademecum"]["url"], Fe["vademecum"]["nome"]), v, "Sources (in Italian)")}
<h2>{G.ic("scudo")}The 4 main exam bodies</h2>
<div class="tab-wrap rc-tab"><table class="conf"><thead><tr><th scope="col">Body</th><th scope="col">Exam for citizenship</th><th scope="col">Centres in Italy</th><th scope="col">Guide</th></tr></thead>
<tbody>{righe}</tbody></table></div>
<p class="small">The Ministry of the Interior's Vademecum (2025) also lists a fifth body, the University for Foreigners «Dante Alighieri» of Reggio Calabria. Any certificate at B1 or higher from a recognised body is valid; the next exam is on {data_en(p["data"])} ({p["ente"]}): <a href="../b1-exam-dates/">all dates</a>.</p>
<h2>{G.ic("lista")}How to register</h2>
<ol class="passi">
<li><span>Choose a date from the <a href="../b1-exam-dates/">exam calendar</a>.</span></li>
<li><span>Choose an exam centre in your city: <a href="../../#citta" hreflang="it" lang="it">centres by city</a> (list in Italian, with addresses and contacts).</span></li>
<li><span>Contact the centre: it tells you the price, the documents and the last day to register. Some centres close registrations before the national deadline.</span></li>
<li><span>Pay and keep the receipt. On exam day bring a valid identity document.</span></li>
</ol>
<h2 id="duration">{G.ic("orologio")}How long the exam lasts</h2>
<p>First the written part (listening, reading, writing), then a short speaking test with an examiner, usually on the same day.</p>
{tabella_durata(G)}
<h2 id="online">{G.ic("attenzione")}Can you take the exam online?</h2>
<p><strong>No.</strong> The exam is taken in person at an exam centre: PLIDA says so in its official FAQ, CILS and CELI ask you to come with an identity document, and the CERT.IT speaking test is in person.
At Roma Tre the CERT.IT B1 written part is done on a computer, but always at the centre.</p>
<div class="fonte">{G.ic("doc")}<span>Sources (in Italian): {online_fonti(G)}</span></div>
<h2>{G.ic("euro")}Cost, results and sample papers</h2>
<p>The CILS B1 Cittadinanza costs {eur(F["cils"], False)} everywhere; the CERT.IT B1 costs {eur(F["certit"], False)} at Roma Tre; for CELI and PLIDA each centre sets the price.
<a href="../b1-exam-cost/">All prices</a> · <a href="../b1-exam-results/">When results arrive</a> · <a href="../sample-papers/">Free official sample papers</a>.</p>
{riquadro_preparati(G, "../")}
<section>
<h2>{G.ic("info")}Frequently asked questions</h2>
{faq_html}
</section>
<div class="due">
<section>
<h2>{G.ic("lista")}More guides</h2>
{griglia_guide(G, "../", salta="italian-b1-exam-for-citizenship/")}
</section>
<aside>{modulo(G, "../")}</aside>
</div>
{in_italiano(G, "../../come-funziona/", "Esame B1 cittadinanza: come funziona")}"""
    titolo = G.titolo_pagina("Italian B1 exam for citizenship: what it is, cost, exemptions")
    descr = G.descrizione_pagina(
        f"The Italian B1 citizenship test explained in English: the 4 main exam bodies, the parts, how long it lasts, cost (CILS {eur(F['cils'], False)}) and who is exempt.")
    pagina_en(G, "en/italian-b1-exam-for-citizenship/", titolo, descr, corpo, it="come-funziona/index.html", jsonld=ld)


def pagina_costo(G):
    F = fatti_brevi(G)
    E = G.ENTE
    v = max(e["fatti"]["costo"]["verificato_il"] for e in G.enti)

    def scheda(sigla, breve, testo):
        f = E[sigla]["fatti"]["costo"]
        fonti = " · ".join(a(x["url"], x["nome"]) for x in f["fonti"])
        return (f'<div class="fatto"><div class="f-et">{G.eb(sigla)}<span>{escape(NOME_EN[sigla])}</span></div><div class="f-breve">{breve}</div>'
                f'<p>{testo}</p>{fonte(G, fonti, f["verificato_il"], "Source (in Italian)")}</div>')

    schede = ('<div class="fatti">'
              + scheda("CILS", f"{eur(F['cils'], False)} (B1 Cittadinanza)",
                       f"CILS B1 Cittadinanza: {eur(F['cils'], False)}, the same fee in Italy and abroad. For the CILS B1 standard ask the centre (at the Language Centre of the University of Padua it costs {eur(F['padova'], False)}).")
              + scheda("CELI", "set by the centre",
                       f"Each exam centre sets the price, under its agreement with the University for Foreigners of Perugia. Example: CELI 2 i cittadinanza {eur(F['celi_tot'], False)} at the University of Milan "
                       f"({eur(F['celi_tassa'], False)} exam fee + {eur(F['celi_spese'], False)} administrative fee, session of {F['celi_data']}).")
              + scheda("PLIDA", "set by the centre", "Each PLIDA centre sets the price and tells you when you register.")
              + scheda("CERT.IT", f"{eur(F['certit'], False)} at Roma Tre",
                       f"B1: {eur(F['certit'], False)} at the Roma Tre University centre (Via Ostiense 123-129, Rome). At partner centres you register and pay at the centre, which tells you the price.")
              + "</div>")
    corpo = f"""<section class="hero">
{briciole(G, ("EsameB1 in English", "../"), ("Cost", None))}
<h1>How much does the B1 citizenship exam cost?</h1>
<p class="lead">According to the official websites of the four exam bodies (checked on {data_en(v)}), the CILS B1 Cittadinanza costs {eur(F["cils"], False)} everywhere,
the CERT.IT B1 costs {eur(F["certit"], False)} at Roma Tre, and for CELI and PLIDA each exam centre sets its own price.</p>
</section>
{nota_esame(G)}
{schede}
{avviso(G, f"Always ask the centre for the <strong>final price</strong> before you pay: some centres add administrative fees (at the University of Milan, for example, {eur(F['celi_spese'], False)} of the {eur(F['celi_tot'], False)} for the CELI 2 i cittadinanza).")}
<div class="due">
<section>
<h2>{G.ic("pin")}Find a centre and ask the price</h2>
<p>Exam centres are listed by city on our Italian pages, with address, phone, email and website: <a href="../../#citta" hreflang="it" lang="it">sedi per città</a>.</p>
<h2>{G.ic("info")}Other questions</h2>
{griglia_guide(G, "../", salta="b1-exam-cost/")}
</section>
<aside>{modulo(G, "../")}</aside>
</div>
{riquadro_preparati(G, "../")}
{in_italiano(G, "../../costo/", "Quanto costa l'esame B1 cittadinanza")}"""
    titolo = G.titolo_pagina(f"How much is the B1 citizenship exam? CILS {eur(F['cils'], False)}, CELI, PLIDA")
    descr = G.descrizione_pagina(
        f"Italian B1 exam for citizenship: CILS B1 Cittadinanza {eur(F['cils'], False)} everywhere, CERT.IT B1 {eur(F['certit'], False)} at Roma Tre, CELI and PLIDA priced by the centre. Official sources.")
    pagina_en(G, "en/b1-exam-cost/", titolo, descr, corpo, it="costo/index.html")


def risultati_en(G):
    """Per ogni ente: dove, cosa serve, tempi, punteggio, se non superi (cifre lette da risultati.json)."""
    T = {s: r["tabella"] for s, r in G.RISULTATI["enti"].items()}
    out = {}
    t = T["CILS"]
    out["CILS"] = ("Online, «Il mio risultato» page (University for Foreigners of Siena)", "candidate number (matricola) and date of birth, no account",
                   f"about {num(t['tempi'], r'circa (\d+) mesi')} months after the exam", "a pass in each skill: listening, reading, writing, speaking",
                   f"B1 Cittadinanza: you retake the whole exam. B1 standard: within {num(t['ripeti'], r'entro (\d+) mesi')} months you retake only the skills you failed.")
    t = T["CELI"]
    out["CELI"] = ("Online, CELI candidates' area (CVCL), or at the exam centre", "candidate number (matricola) and date of birth, no account",
                   f"about {num(t['tempi'], r'circa (\d+) giorni lavorativi')} working days after the papers reach Perugia",
                   f"CELI 2 i: written at least {num(t['superare'], r'scritto almeno (\d+/\d+)')}, speaking at least {num(t['superare'], r'orale almeno (\d+)')}, "
                   f"total at least {num(t['superare'], r'in tutto almeno (\d+/\d+)')}",
                   f"Within {num(t['ripeti'], r'Entro (\d+) anno')} year you retake only the part you failed (written or speaking), paying {num(t['ripeti'], r'(\d+)%')}% of the fee.")
    t = T["PLIDA"]
    if t["tempi"] is not None:
        raise SystemExit("genera_en: PLIDA ora scrive i tempi dei risultati: aggiornare risultati_en()")
    out["PLIDA"] = ("Online, on certificazioneplida.dante.global", "an account (your email and password)", "not stated by PLIDA",
                    f"at least {num(t['superare'], r'almeno (\d+/\d+)')} in each of the 4 skills",
                    f"Within {num(t['ripeti'], r'Entro (\d+) mesi')} months you can retake from {num(t['ripeti'], r'da (\d+) a \d+ abilità')} to {num(t['ripeti'], r'da \d+ a (\d+) abilità')} skills, also at another centre.")
    t = T["CERT.IT"]
    if t["tempi"] is not None:
        raise SystemExit("genera_en: CERT.IT ora scrive i tempi dei risultati: aggiornare risultati_en()")
    pc = num(t["superare"], r"(\d+)% dei punti nello scritto")
    out["CERT.IT"] = ("Not stated on the official website: ask your exam centre", "ask the centre", "not stated by CERT.IT",
                      f"{pc}% of the points in the written part (listening, reading, writing) and {num(t['superare'], r'e (\d+)% nell')}% in the speaking test",
                      "The website does not say for the B1: ask the centre.")
    return out


def pagina_risultati(G):
    R = risultati_en(G)
    v = G.RISULTATI["verificato_il"]
    righe = "".join(
        f'<tr><td><a href="../{SLUG_EN[s]}/">{G.eb(s)}</a></td><td data-l="Where">{escape(r[0])}</td><td data-l="You need">{escape(r[1])}</td>'
        f'<td data-l="When">{escape(r[2])}</td></tr>' for s, r in R.items())
    righe2 = "".join(f'<tr><td>{G.eb(s)}</td><td data-l="Pass mark">{escape(r[3])}</td><td data-l="If you fail">{escape(r[4])}</td></tr>' for s, r in R.items())
    bottoni = "".join(f'<a class="btn btn-2" href="{escape(G.RISULTATI["enti"][s]["bottone"]["url"])}" rel="noopener">{G.ic("ok")}{s} results page</a>'
                      for s in R)
    fonti = " · ".join(a(G.RISULTATI["enti"][s]["fonti"][G.RISULTATI["enti"][s]["fonte_risposta"]]["url"],
                         G.RISULTATI["enti"][s]["fonti"][G.RISULTATI["enti"][s]["fonte_risposta"]]["nome"]) for s in R)
    cils_m = num(G.RISULTATI["enti"]["CILS"]["tabella"]["tempi"], r"circa (\d+) mesi")
    celi_g = num(G.RISULTATI["enti"]["CELI"]["tabella"]["tempi"], r"circa (\d+) giorni lavorativi")
    corpo = f"""<section class="hero">
{briciole(G, ("EsameB1 in English", "../"), ("Results", None))}
<h1>B1 citizenship exam results: when and where to see them</h1>
<p class="lead">According to the official pages of the exam bodies (read on {data_en(v)}), CILS and CELI publish results online with your candidate number (matricola) and date of birth:
CILS about {cils_m} months after the exam, CELI about {celi_g} working days after the papers reach Perugia. PLIDA results are in your online PLIDA account; for CERT.IT ask your centre.</p>
<div class="azioni">{bottoni}</div>
</section>
{nota_esame(G)}
<h2>{G.ic("ok")}Quick answer, body by body</h2>
<div class="tab-wrap rc-tab"><table class="conf"><thead><tr><th scope="col">Body</th><th scope="col">Where you see the result</th><th scope="col">What you need</th><th scope="col">When</th></tr></thead>
<tbody>{righe}</tbody></table></div>
<h2>{G.ic("lista")}Pass mark and what to do if you fail</h2>
<div class="tab-wrap rc-tab"><table class="conf"><thead><tr><th scope="col">Body</th><th scope="col">To pass</th><th scope="col">If you fail</th></tr></thead>
<tbody>{righe2}</tbody></table></div>
{fonte(G, fonti, v, "Sources (in Italian)")}
<p class="small">«Not stated»: in the official pages we read, the body does not say it. More details, body by body, are on our Italian pages:
{", ".join(f'<a href="../../risultati/{G.SLUG_RISULTATI[s]}/" hreflang="it" lang="it">risultati {s}</a>' for s in R)}.</p>
<div class="due">
<section>
<h2>{G.ic("info")}After the exam</h2>
<p>With the certificate you can apply for citizenship: <a href="../apply-italian-citizenship-by-residence/">how to apply</a> and the <a href="../income-requirement-italian-citizenship/">income requirement</a>.</p>
{griglia_guide(G, "../", salta="b1-exam-results/")}
</section>
<aside>{modulo(G, "../")}</aside>
</div>
{in_italiano(G, "../../risultati/", "Risultati dell'esame B1 cittadinanza")}"""
    titolo = G.titolo_pagina(f"B1 citizenship exam results {G.OGGI.year}: CILS, CELI, PLIDA, CERT.IT",
                             f"B1 exam results {G.OGGI.year}: CILS, CELI, PLIDA, CERT.IT")
    descr = G.descrizione_pagina(
        f"Where to see your Italian B1 citizenship exam results: CILS about {cils_m} months, CELI about {celi_g} working days, PLIDA in your account. Pass marks and retakes.")
    pagina_en(G, "en/b1-exam-results/", titolo, descr, corpo, it="risultati/index.html")


def pagina_ente(G, e, prossime):
    sigla = e["sigla"]
    sue = [s for s in G.sedi if s["ente"] == sigla]
    date_ente = [s for s in prossime if s["ente"] == sigla]
    R = risultati_en(G)[sigla]
    F = fatti_brevi(G)
    p = date_ente[0] if date_ente else None
    dur = e["fatti"]["durata"]["prove"]
    costo = {"CILS": f"{eur(F['cils'], False)} for the CILS B1 Cittadinanza, the same everywhere",
             "CELI": f"set by the centre (example: {eur(F['celi_tot'], False)} at the University of Milan)",
             "PLIDA": "set by the centre", "CERT.IT": f"{eur(F['certit'], False)} at Roma Tre; partner centres set their own price"}[sigla]
    intro = {"CILS": "There is a dedicated exam, the CILS B1 Cittadinanza, with several sessions a year; the CILS B1 standard is valid too.",
             "CELI": "There is a dedicated exam, the CELI 2 i cittadinanza (B1), only at centres in Italy; the general CELI 2 (B1) is valid too.",
             "PLIDA": "For citizenship you take the PLIDA B1; dates are the same at all centres.",
             "CERT.IT": "For citizenship you take the B1 certificate (A2/B1 sessions)."}[sigla]
    num(e["cittadinanza"], {"CILS": r"(CILS B1 Cittadinanza)", "CELI": r"(CELI 2 i cittadinanza)", "PLIDA": r"(PLIDA B1)", "CERT.IT": r"(livello B1)"}[sigla])
    v = max(s["verificato_il"] for s in G.sessioni if s["ente"] == sigla)
    if p:
        prima = f"According to the official {sigla} calendar (checked on {data_en(v)}), the next {sigla} B1 exam is on {data_en(p['data'])}: {esame_en(p['esami'][0])}."
    else:
        prima = f"According to the official {sigla} website (checked on {data_en(v)}), no new B1 exam date has been published yet."
    es = e["fatti"]["esempi"]
    schede = f"""<div class="fatti">
<div class="fatto"><div class="f-et">{G.ic("euro")}<span>Cost</span></div><p>{escape(costo)}. <a href="../b1-exam-cost/">All prices</a>.</p></div>
<div class="fatto"><div class="f-et">{G.ic("orologio")}<span>How long it lasts</span></div><p>{escape("; ".join(f'{", ".join(PROVE_EN[x] for x in q["prove"]).capitalize()}: {tempo_en(q["tempo"])}' for q in dur["parti"]))}. In total {escape(totale_en(dur["totale"]))}.</p></div>
<div class="fatto"><div class="f-et">{G.ic("ok")}<span>Results</span></div><p>{escape(R[0] if R[1] == "ask the centre" else f"{R[0]}. You need: {R[1]}. When: {R[2]}")}. <a href="../b1-exam-results/">Results of all bodies</a>.</p></div>
<div class="fatto"><div class="f-et">{G.ic("lista")}<span>To pass, and if you fail</span></div><p>{escape(R[3][0].upper() + R[3][1:])}. {escape(R[4])}</p></div>
<div class="fatto"><div class="f-et">{G.ic("libro")}<span>Free sample paper</span></div><p>The official sample exam is free on the {sigla} website.</p><a class="btn btn-2" href="{escape(es["url"])}" rel="noopener">Open the sample paper {G.ic("freccia")}</a></div>
</div>
<div class="fonte">{G.ic("doc")}<span>Sources (in Italian): {a(e["sito"], "official " + sigla + " website")} · {a(e["pagina_date"], "official calendar")} · {a(e["pagina_sedi"], "official list of centres")}</span></div>"""
    corpo = f"""<section class="hero">
{briciole(G, ("EsameB1 in English", "../"), (sigla, None))}
<span class="occhiello">{G.ic("scudo")}{escape(NOME_EN[sigla])}</span>
<h1>{escape(TITOLO_ENTE_EN[sigla])}: dates, cost and results</h1>
<p class="lead">{escape(prima)} {escape(intro)} You register at the exam centre, which tells you the price and the documents.</p>
</section>
{nota_esame(G)}
<div class="due">
<section>
<h2 id="dates">{G.ic("cal")}Next {sigla} dates (level B1)</h2>
{lista_sessioni(G, date_ente, con_filtri=False) if date_ente else "<p>No future date published yet. We check the official calendar every week.</p>"}
</section>
<aside>{modulo(G, "../")}</aside>
</div>
<section>
<h2 id="in-brief">{G.ic("info")}{sigla} B1 in brief</h2>
{schede}
</section>
<section>
<h2 id="centres">{G.ic("edificio")}{len(sue)} {sigla} exam centres in Italy</h2>
<p>The full list by region, with addresses, phone numbers and emails, is on our Italian page: <a href="../../ente/{G.SLUG_ENTE[sigla]}/#sedi" hreflang="it" lang="it">sedi {sigla} in Italia</a>.
Contact the centre to register: some centres close registrations before the national deadline.</p>
{griglia_guide(G, "../", salta=f"{SLUG_EN[sigla]}/")}
</section>
{in_italiano(G, f"../../ente/{G.SLUG_ENTE[sigla]}/", G.NOME_RICERCA[sigla] + ": date, costo e sedi")}"""
    nome = TITOLO_ENTE_EN[sigla]
    corto = nome.split(" (")[0]
    if p:
        titolo = G.titolo_pagina(f"{nome}: next date {data_en(p['data'])}", f"{corto}: next date {data_en(p['data'])}",
                                 f"{corto}: next date {giorno_mese_en(p['data'])}")
    else:
        titolo = G.titolo_pagina(f"{nome}: dates, cost and results", f"{corto}: dates, cost and results")
    descr = G.descrizione_pagina(
        f"{(lambda s: s[0].upper() + s[1:])(prima.split(': ')[0].split('), ')[-1]) if p else 'No new date yet'}. {sigla} B1 for Italian citizenship: dates, deadlines, cost, results and {len(sue)} centres in Italy.",
        f"{sigla} B1 for Italian citizenship: dates, deadlines, cost, results and {len(sue)} centres in Italy, in English.")
    pagina_en(G, f"en/{SLUG_EN[sigla]}/", titolo, descr, corpo, it=f"ente/{G.SLUG_ENTE[sigla]}/index.html")


GLOSSE = [("specifiche", "exam specifications"), ("commentata", "writing test with comments"), ("certit_b1", "sample exam"), ("trascrizion", "audio transcript"), ("chiavi", "answer key"), ("criteri", "marking criteria"), ("foglio", "answer sheet"),
          ("fogli", "answer sheets"), ("sillabo", "syllabus"), ("produzione scritta", "writing task"), ("produzione orale", "speaking task"),
          ("input orale", "speaking test prompts"), ("descrizione", "exam description"), ("quaderno", "test booklet"), ("audio", "listening audio"),
          ("esempio", "sample exam"), ("parlato", "speaking test")]


def glossa(nome):
    """Traduzione breve del nome italiano del file ufficiale (il nome resta quello dell'ente)."""
    n = nome.lower()
    return next((g for k, g in GLOSSE if k in n), "")


def peso_en(byte):
    if byte < 1_000_000:
        return f"{round(byte / 1000)} KB"
    return f"{byte / 1_000_000:.1f} MB"


def pagina_esempi(G):
    v = G.esempi["verificato_il"]
    blocchi = []
    for e in G.esempi["enti"]:
        sigla = e["sigla"]
        righe = []
        for f in e["file"]:
            dim = (f'{f["numero"]} × ' if f.get("numero") else "") + peso_en(f["byte"])
            det = " · ".join([dim] + ([f'{f["pagine"]} {"page" if f["pagine"] == 1 else "pages"}'] if f.get("pagine") else []))
            nome = a(f["url"], f["nome"]) if f.get("url") else f'<span class="nome">{escape(f["nome"])}</span>'
            gl = glossa(f["nome"])
            nome += f' <span class="small">({gl})</span>' if gl else ""
            righe.append(f'<li><span class="fi">{G.ic(G.ICONA_FILE[f["formato"]])}</span><div>{nome}</div>'
                         f'<div class="meta"><strong>{f["formato"]}</strong><span>{escape(det)}</span></div></li>')
        nota = ("<p class=\"small\">Roma Tre's legal notes forbid deep links to its files from other sites, so we only link the official page: "
                "the files are at the bottom, under «Esempio di esame».</p>" if e.get("link_diretti") is False else "")
        dur = G.ENTE[sigla]["fatti"]["durata"]["prove"]["totale"]
        blocchi.append(f"""<section class="card es-card" id="{G.SLUG_ENTE[sigla]}">
<h2>{G.eb(sigla)} {escape(e["esame"])}</h2>
<p>{len(e["file"])} {"file" if len(e["file"]) == 1 else "files"} on the official page of {"" if sigla == "CERT.IT" else "the "}{escape(NOME_EN[sigla])}. Exam length: {escape(totale_en(dur))}.</p>
<div class="azioni"><a class="btn" href="{escape(e["pagina"]["url"])}" rel="noopener">{G.ic("web")}Official {sigla} page</a><a class="btn btn-2" href="../{SLUG_EN[sigla]}/">{sigla} dates and cost</a></div>
<ul class="file-lista">{"".join(righe)}</ul>
{nota}
</section>""")
    corpo = f"""<section class="hero">
{briciole(G, ("EsameB1 in English", "../"), ("Sample papers", None))}
<h1>Free official sample papers for the Italian B1 citizenship exam</h1>
<p class="lead">According to the official websites of CILS, CELI, PLIDA and CERT.IT (links checked on {data_en(v)}), each body publishes a free sample exam with audio and answer keys.
File names are in Italian, as on the official sites; the papers themselves are the real exam format.</p>
<div class="es-vai">{"".join(f'<a href="#{G.SLUG_ENTE[e["sigla"]]}">{G.eb(e["sigla"])}<small>{escape(e["esame"])}</small></a>' for e in G.esempi["enti"])}</div>
</section>
{nota_esame(G)}
{"".join(blocchi)}
<section>
<h2>{G.ic("lista")}How to practise</h2>
<ul>
<li>Do the sample paper with a timer, using the times in the <a href="../italian-b1-exam-for-citizenship/#duration">duration table</a>.</li>
<li>Listen to each audio file only as many times as the exam allows (the instructions are in the paper).</li>
<li>Check your answers with the official answer key, where there is one.</li>
<li>Practise the speaking test aloud: introduce yourself and talk about everyday topics.</li>
</ul>
<p class="small">The sample papers belong to the exam bodies: download them from their pages, do not copy them elsewhere.</p>
</section>
{riquadro_preparati(G, "../")}
<div class="due">
<section><h2>{G.ic("info")}More guides</h2>{griglia_guide(G, "../", salta="sample-papers/")}</section>
<aside>{modulo(G, "../")}</aside>
</div>
{in_italiano(G, "../../esempi/", "Prove d'esempio ufficiali dell'esame B1")}"""
    titolo = G.titolo_pagina("Italian B1 citizenship exam: free official sample papers")
    descr = G.descrizione_pagina("Free official sample papers for the Italian B1 citizenship exam: CILS, CELI, PLIDA and CERT.IT, with PDF, audio and answer keys, in English.")
    pagina_en(G, "en/sample-papers/", titolo, descr, corpo, it="esempi/index.html")


def cit(G, fonte_k, regola):
    """Cifra letta da una frase citata di esoneri.json."""
    testo = " ".join(c["testo"] for c in G.esoneri["citazioni"] if c["fonte"] == fonte_k)
    return num(testo, regola)


def a2_test(G):
    """Fatti del test A2 per la carta di soggiorno (DM 7/12/2021, Ministero, Prefettura di Lecco), cifre dalle citazioni."""
    return {
        "giorni_conv": cit(G, "dm2021", r"entro (sessanta) giorni"),
        "soglia": cit(G, "dm2021", r"almeno l'(ottanta) per cento"),
        "ripeti": cit(G, "minint_test", r"dopo (\d+) giorni"),
        "orale": cit(G, "lecco", r"comprensione orale \(durata (\d+) minuti\)"),
        "scritta": cit(G, "lecco", r"comprensione scritta \(durata (\d+) minuti\)"),
        "inter": cit(G, "lecco", r"interazione scritta \(durata (\d+) minuti\)"),
        "minori": cit(G, "dm2021", r"minori degli anni (quattordici)"),
        "dm": data_it_en(G.esoneri["fonti"]["dm2021"]["nome"]),
    }


def pagina_esoneri(G):
    Fe = G.esoneri["fonti"]
    v = G.esoneri["verificato_il"]
    A = a2_test(G)
    ce = data_it_en(cit(G, "vademecum", r"rilasciato dal (\d{1,2} dicembre \d{4})"))
    sent = num(Fe["corte25"]["nome"], r"sentenza n\. (\d+) del")
    sent_a = num(Fe["corte25"]["nome"], r"del (\d{4})")
    circ = num(Fe["vademecum"]["nome"], r"circolare n\. (\d+)")
    circ_d = data_it_en(Fe["vademecum"]["nome"])

    def src(*k):
        return fonte(G, " · ".join(a(Fe[x]["url"], Fe[x]["nome"]) for x in k), v, "Sources (in Italian)" if len(k) > 1 else "Source (in Italian)")

    def scheda(icona, titolo, testo, *k):
        return f'<div class="fatto"><div class="f-et">{G.ic(icona)}<span>{titolo}</span></div><p>{testo}</p>{src(*k)}</div>'

    tab = [("Integration agreement signed", "Exempt", "Takes the test, unless an A2 level is recognised in the agreement's credits"),
           ("EU long-term residence permit", "Exempt", "Not needed: it is the permit you already have"),
           ("Serious limitations certified by a public health facility", "Exempt", "Exempt"),
           ("A2 certificate from a recognised body", "Not enough: B1 or higher is needed", "Does not take the test"),
           ("B1 certificate from a recognised body", "Valid", "Does not take the test"),
           ("Italian lower or upper secondary school diploma", "Valid instead of the certificate (qualification in Italian)", "Does not take the test"),
           (f"Child under {A['minori']}", "Not covered in the sources we read", "Does not take the test"),
           ("EU citizen, or family member with a «carta di soggiorno per familiare»", "Must have the B1", "Not covered in the sources we read")]
    righe = "".join(f'<tr><td><strong>{escape(c)}</strong></td><td data-l="Citizenship (B1)">{escape(x)}</td><td data-l="Carta di soggiorno (A2)">{escape(y)}</td></tr>' for c, x, y in tab)
    cittad = ('<div class="fatti">'
              + scheda("ok", "You signed the integration agreement",
                       "You are excluded from the requirement if you signed the integration agreement (art. 4-bis of the Consolidated Immigration Act). The Ministry's Vademecum adds that these are people who came to Italy "
                       "through family reunification or family cohesion; they prove it with the Prefecture's certificate (Sportello unico) and write the agreement's details in the application.", "legge91", "vademecum")
              + scheda("ok", "You hold the EU long-term residence permit",
                       f"You are excluded if you hold the EU long-term residence permit (the «carta di soggiorno»). According to the Vademecum the old «CE» long-term permit also counts if it was issued from {ce}, when the Italian test came into force.",
                       "legge91", "vademecum")
              + scheda("info", "You have serious limitations in learning the language",
                       f"With judgment no. {sent} of {sent_a} the Constitutional Court exempted people with serious limitations in learning the language because of age, illness or disability. "
                       "You need a certificate from a <strong>public health facility</strong>: according to the Ministry a GP's certificate is not enough. If you live in Italy and have a foreign medical certificate, "
                       "add one from an Italian public health facility; if you live abroad, present the foreign certificate translated and legalised.", "corte25", "circ14605", "vademecum")
              + scheda("doc", "Instead of the certificate: a school qualification in Italian",
                       "If you are not exempt you can present, instead of the B1 certificate, a qualification from a recognised public or state-equivalent school, from lower secondary school (scuola media) upwards, "
                       "taken <strong>in Italian</strong>. For a public school a self-declaration with the details is enough; for a private or state-equivalent school you need a certified copy.", "legge91", "vademecum")
              + "</div>")
    corpo = f"""<section class="hero">
{briciole(G, ("EsameB1 in English", "../"), ("Exemptions", None))}
<span class="occhiello">{G.ic("scudo")}Law, decrees and Ministry · read on {data_en(v)}</span>
<h1>Exemptions from the Italian language test: citizenship (B1) and carta di soggiorno (A2)</h1>
<p class="lead">According to art. 9.1 of Law 91/1992 (in-force text read on Normattiva on {data_en(v)}) and the Ministry of the Interior's Vademecum (circular no. {circ} of {circ_d}), you do not need the B1 certificate for citizenship
if you signed the integration agreement, hold the EU long-term residence permit, or have serious limitations certified by a public health facility.
For the carta di soggiorno, the Prefecture's A2 test is not needed, for example, if you already have a certificate at A2 or higher or an Italian school diploma (decree of the Minister of the Interior of {A["dm"]}).</p>
</section>
{decide(G, "The Prefecture (citizenship) or the Questura (EU long-term permit)")}
<section>
<h2 id="summary">{G.ic("lista")}Summary: your case</h2>
<div class="tab-wrap rc-tab"><table class="conf"><thead><tr><th scope="col">Your case</th><th scope="col">Citizenship (B1 certificate)</th><th scope="col">Carta di soggiorno (A2 test)</th></tr></thead>
<tbody>{righe}</tbody></table></div>
{src("legge91", "vademecum", "dm2021")}
</section>
<section>
<h2 id="citizenship">{G.ic("scudo")}Citizenship: who does not need the B1 certificate</h2>
<p>People applying for citizenship by marriage or by residence (articles 5 and 9 of Law 91/1992) must know Italian at level B1 or higher. The law and the Ministry exclude these cases:</p>
{cittad}
<h3>Who still needs the B1</h3>
<p>According to the Ministry's Vademecum: citizens of the European Union; holders of the «carta di soggiorno» for family members of Italian or EU citizens (this is not the EU long-term residence permit);
British citizens and their family members with the Withdrawal Agreement («Brexit») residence card.</p>
<h3>Which certificates count</h3>
<p>A certificate at B1 or higher from a recognised body. The Vademecum lists: University for Foreigners of Siena (CILS), University for Foreigners of Perugia (CELI), Roma Tre University (CERT.IT), Società Dante Alighieri (PLIDA)
and the University for Foreigners «Dante Alighieri» of Reggio Calabria. You can also get the certificate at a CPIA (public adult education centre). Certificates from regional vocational training courses are not valid.</p>
{src("vademecum", "domanda")}
</section>
<section>
<h2 id="carta-di-soggiorno">{G.ic("doc")}Carta di soggiorno: the A2 Italian test</h2>
<p>To get the EU long-term residence permit (the «carta di soggiorno») you must pass an Italian language test (art. 9, paragraph 2-bis, of the Consolidated Immigration Act) at level <strong>A2</strong>:
understanding frequently used sentences and expressions. The rules are in the decree of the Minister of the Interior of {A["dm"]}.</p>
<ol class="passi">
<li><span>Apply online to the Prefecture of the province where you live, on the Ministry of the Interior's {a(Fe["portale"]["url"], "Portale Servizi")}.</span></li>
<li><span>The Prefecture calls you within {A["giorni_conv"]} days, with day, time and place.</span></li>
<li><span>The test is on a computer, or on paper if you ask. For example the Prefecture of Lecco describes three parts: listening ({A["orale"]} minutes), reading ({A["scritta"]} minutes) and written interaction ({A["inter"]} minutes).</span></li>
<li><span>To pass you need at least <strong>{A["soglia"]}%</strong> of the total score. The result goes to the Questura, which issues the permit if the other requirements are met.</span></li>
<li><span>If you fail you can apply again: according to the Ministry only {A["ripeti"]} days after the previous test.</span></li>
</ol>
{src("dm2021", "minint_test", "lecco")}
<h3 id="no-a2">Who does not take the A2 test</h3>
<ul>
<li>children under {A["minori"]} of the applicant and of the spouse;</li>
<li>people with serious learning limitations due to age, illness or disability, certified by a public health facility;</li>
<li>holders of a certificate at A2 or higher from a recognised body (so also the B1 taken for citizenship);</li>
<li>people with a final CPIA course certificate at A2 or higher, or with A2 recognised in the integration agreement's credits;</li>
<li>people with an Italian lower or upper secondary school diploma, students at an Italian university, or doing a PhD or university master's in Italy;</li>
<li>some workers (managers and highly qualified workers, university professors and researchers, translators and interpreters, accredited journalists: art. 27 of the Consolidated Immigration Act);</li>
<li>holders of international protection, and permits for research at universities and bodies supervised by the Ministry of University.</li>
</ul>
{src("dm2021", "tu9")}
<p>Income and other requirements for the carta: <a href="../carta-di-soggiorno-requirements/">carta di soggiorno requirements</a>.</p>
</section>
<div class="due">
<section><h2>{G.ic("info")}More guides</h2>{griglia_guide(G, "../", salta="language-test-exemptions/")}</section>
<aside>{modulo(G, "../")}</aside>
</div>
{in_italiano(G, "../../esonero-test-italiano/", "Chi è esonerato dal test di italiano")}"""
    titolo = G.titolo_pagina("Italian language test exemptions: citizenship B1, carta A2",
                             "Italian language test exemptions: B1 and A2")
    descr = G.descrizione_pagina(
        "Who is exempt from the B1 Italian test for citizenship and from the A2 test for the carta di soggiorno, according to the law and the Ministry.")
    pagina_en(G, "en/language-test-exemptions/", titolo, descr, corpo, it="esonero-test-italiano/index.html")


JS_REDDITI_UI_EN = """(function(){
  var f=document.getElementById('calc-redditi');if(!f)return;
  function eur(c){var n=Math.abs(c),e=Math.floor(n/100),d=String(n%%100).padStart(2,'0');return '\\u20ac'+e.toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g,',')+'.'+d;}
  function leggiEuro(t){t=String(t||'').replace(/[\\s\\u20ac]/g,'');if(!t)return null;
    if(/\\.\\d{1,2}$/.test(t)){t=t.replace(/,/g,'');}else if(/,\\d{1,2}$/.test(t)&&t.split(',').length===2){t=t.replace(/\\./g,'').replace(',','.');}else{t=t.replace(/[.,]/g,'');}
    var v=Number(t);return isFinite(v)&&v>=0?Math.round(v*100):null;}
  var out=document.getElementById('calc-esito');
  function riga(id,titolo,x,chi){var el=out.querySelector('[data-r="'+id+'"]');if(!el)return;
    el.hidden=false;el.className='c-riga '+(x.sopra?'si':'no');
    el.querySelector('.c-tit').textContent=titolo;
    el.querySelector('.c-soglia').textContent='Threshold: '+eur(x.soglia)+' a year';
    el.querySelector('.c-esito').textContent=x.sopra?('You are above the threshold by '+eur(x.differenza)+'.'):('You are below the threshold: '+eur(-x.differenza)+' short.');
    el.querySelector('.c-chi').textContent=chi;}
  function calcola(ev){if(ev)ev.preventDefault();
    var coniuge=f.coniuge.checked,figli=Math.max(0,Math.min(20,parseInt(f.figli.value,10)||0));
    var reddito=leggiEuro(f.reddito.value),err=f.querySelector('[data-errore]');
    if(reddito===null){err.hidden=false;out.hidden=true;return;}
    err.hidden=true;out.hidden=false;
    var r=calcolaRedditi(coniuge,figli,reddito);
    riga('cittadinanza','Italian citizenship by residence',r.cittadinanza,'The Prefecture decides: it looks at your IRPEF taxable income of the last 3 years.');
    riga('carta_solo','Carta di soggiorno (EU long-term permit), just for you',r.carta_solo,'The Questura decides.');
    var fam=out.querySelector('[data-r="carta_famiglia"]');
    if(r.familiari>0){riga('carta_famiglia','Carta di soggiorno also for '+(r.familiari===1?'1 family member':r.familiari+' family members'),r.carta_famiglia,'The Questura decides.');}else{fam.hidden=true;}
    out.querySelector('[data-quattordici]').hidden=figli<2;
  }
  f.addEventListener('submit',calcola);
  f.addEventListener('change',function(){if(f.reddito.value)calcola();});
})();"""


def js_calcolo(G, js_soglie):
    """Il blocco di calcolo è quello italiano (tra /*calcolo-inizio*/ e /*calcolo-fine*/), identico: cambiano solo i testi."""
    it = G.JS_REDDITI % js_soglie
    blocco = it[: it.index("/*calcolo-fine*/") + len("/*calcolo-fine*/")]
    return blocco + "\n" + (JS_REDDITI_UI_EN % ())


def pagina_redditi(G):
    c, ca = G.REDDITI["cittadinanza"], G.REDDITI["carta_soggiorno"]
    Fr = {**c["fonti"], **ca["fonti"]}
    A = G.RICONG["assegno_sociale"]
    anno = G.RICONG["anno"]
    cent = G.cent
    solo, con, fig = cent(c["solo"]), cent(c["con_coniuge"]), cent(c["per_figlio"])
    annuo = cent(A["annuo"])
    meta = annuo // 2
    v = min(f["verificato_il"] for f in Fr.values())
    anni_tre = num(" ".join(x["testo"] for x in G.REDDITI["citazioni"]), r"negli ultimi (tre) anni")
    anni_carta = num(" ".join(x["testo"] for x in G.REDDITI["citazioni"] if x["fonte"] == "tu9"), r"da almeno (cinque) anni")
    circ = num(A["fonte"], r"circolare n\. (\d+)")
    circ_d = data_it_en(A["fonte"])
    vad_d = data_it_en(Fr["vademecum"]["nome"])

    def src(*k, extra=""):
        return fonte(G, " · ".join(a(Fr[x]["url"], Fr[x]["breve"]) for x in k) + extra, max(Fr[x]["verificato_il"] for x in k), "Source (in Italian)")

    inps = f' · social allowance {anno}: {a(A["url"], f"INPS circular no. {circ} of {circ_d}")} ({a(A["url_allegato"], "table A")})'
    righe_c = "".join(
        f'<tr><td><strong>{n} dependent {"child" if n == 1 else "children"}</strong></td>'
        f'<td data-l="Without spouse">{eur_c(G.calcola_redditi(False, n, 0)["cittadinanza"]["soglia"])}</td>'
        f'<td data-l="With dependent spouse">{eur_c(G.calcola_redditi(True, n, 0)["cittadinanza"]["soglia"])}</td></tr>' for n in range(0, 5))
    tab_c = ('<div class="tab-wrap rc-tab"><table class="conf"><caption class="small">Minimum taxable income per year for citizenship by residence</caption>'
             '<thead><tr><th scope="col">Dependent children (or other family members)</th><th scope="col">Without spouse</th><th scope="col">With dependent spouse</th></tr></thead>'
             f'<tbody>{righe_c}</tbody></table></div>')
    tab_k = tabella_carta(G)
    ex3a, ex3b = G.calcola_redditi(True, 1, 0)["cittadinanza"]["soglia"], G.calcola_redditi(False, 2, 0)["cittadinanza"]["soglia"]
    ex4a = G.calcola_redditi(True, 2, 0)["cittadinanza"]["soglia"]
    js_soglie = json.dumps({"solo": solo, "conCon": con, "figlio": fig, "annuo": annuo})
    faq = [
        (f"What is the minimum income for Italian citizenship in {anno}?",
         f"For citizenship by residence you need at least {eur_c(solo)} a year of taxable income if you are alone, {eur_c(con)} with a dependent spouse, plus {eur_c(fig)} for each dependent child "
         f"or family member. These are the thresholds written by the Ministry of the Interior in the Vademecum of {vad_d}; they do not change every year."),
        ("Is the income for citizenship gross or net?",
         "What counts is the IRPEF taxable income declared in Italy. On the 730 tax return it is the «Reddito imponibile» in the «Prospetto di liquidazione», as the Prefecture explains. It is not your net pay."),
        ("How much income for citizenship for 3 or 4 people?",
         f"3 people: with spouse and 1 dependent child {eur_c(ex3a)}, or alone with 2 dependent children {eur_c(ex3b)}. 4 people (you, spouse and 2 dependent children): {eur_c(ex4a)}. Amounts per year."),
        ("Does my spouse's or partner's income count?",
         "Yes for the spouse, the civil partner and the other family members listed in art. 433 of the Civil Code. According to the Ministry's Vademecum the income of a partner with no legal tie does not count, "
         "even with children, nor that of a spouse living abroad. A partner with a cohabitation contract counts."),
        (f"How much income do I need for the carta di soggiorno in {anno}?",
         f"At least the {anno} social allowance (assegno sociale): {eur_c(annuo)} a year just for you. If you also apply for your family members, add half ({eur_c(meta)}) for each one: "
         f"for 4 people (you and 3 family members) {eur_c(annuo + meta * 3)}. The Questura decides."),
    ]
    faq_html, ld = faq_blocco(G, [(escape(q), escape(t)) for q, t in faq])
    corpo = f"""<section class="hero">
{briciole(G, ("EsameB1 in English", "../"), ("Income requirement", None))}
<span class="occhiello">{G.ic("euro")}Official sources · {data_en(v)}</span>
<h1>Income requirement for Italian citizenship and the carta di soggiorno {anno}</h1>
<p class="lead">According to the Ministry of the Interior's Vademecum of {vad_d} (read on {data_en(v)}), Italian citizenship by residence requires a taxable income of at least {eur_c(solo)} a year if you are alone,
{eur_c(con)} with a dependent spouse and {eur_c(fig)} more for each dependent child. For the carta di soggiorno you need at least the {anno} social allowance, {eur_c(annuo)} a year (art. 9 of the Consolidated Immigration Act).</p>
<div class="risposta">
<div class="slot"><div class="r-et">{G.ic("scudo")}Citizenship (Prefecture)</div>
<div class="r-data">{eur_c(solo)} <small>a year</small></div>
<div class="r-cosa">alone · {eur_c(con)} with dependent spouse · + {eur_c(fig)} per child</div></div>
<div class="slot"><div class="r-et">{G.ic("doc")}Carta di soggiorno (Questura)</div>
<div class="r-data">{eur_c(annuo)} <small>a year</small></div>
<div class="r-cosa">just for you · + {eur_c(meta)} for each family member</div></div>
<div class="r-piede"><a href="#calculate">Check your family's income {G.ic("freccia")}</a><span>{G.ic("doc")}Sources: Ministry of the Interior, Prefecture, Immigration Act, INPS</span></div>
</div>
</section>
{avviso(G, "This page compares your income with the official thresholds, but it is not legal advice. <strong>For citizenship the Prefecture decides; for the carta di soggiorno the Questura decides.</strong> For your case ask them or a patronato.")}
<section>
<h2 id="calculate">{G.ic("lista")}Calculator: are you above or below the thresholds?</h2>
<form class="form calc card" id="calc-redditi" novalidate>
<label class="check"><input type="checkbox" name="coniuge"><span>My spouse (or civil partner) is my tax dependant</span></label>
<p class="small">If your spouse has their own income and is not your dependant, leave the box unticked and add their taxable income to yours in the field below (the higher threshold applies only «in the presence of a dependent spouse», the Vademecum says).</p>
<label>Dependent children (or other family members)<input type="number" name="figli" min="0" max="20" value="0" inputmode="numeric"></label>
<label>Family taxable income per year, in euro<input type="text" name="reddito" inputmode="decimal" placeholder="for example 12,500" autocomplete="off"></label>
<button class="btn" type="submit">{G.ic("euro")}Compare with the thresholds</button>
<p class="errore" data-errore hidden>Write the income in euro, for example 12,500 or 12500.50.</p>
</form>
<div class="calc-esito" id="calc-esito" aria-live="polite" hidden>
<div data-r="cittadinanza" hidden><div class="c-tit"></div><div class="c-soglia"></div><div class="c-esito"></div><div class="c-chi small"></div></div>
<div data-r="carta_solo" hidden><div class="c-tit"></div><div class="c-soglia"></div><div class="c-esito"></div><div class="c-chi small"></div></div>
<div data-r="carta_famiglia" hidden><div class="c-tit"></div><div class="c-soglia"></div><div class="c-esito"></div><div class="c-chi small"></div></div>
<p class="small" data-quattordici hidden>With 2 or more children under 14, for family reunification the law asks for at least {eur_c(annuo * 2)} a year: for the carta di soggiorno ask the Questura whether this applies to you too.</p>
<p class="small">The calculator only uses the official thresholds. It cannot know whether your income is «taxable», which years it refers to, or whether your documents are fine: <strong>the Prefecture (citizenship) or the Questura (carta di soggiorno) decides</strong>.
To bring family members to Italy see the <a href="../family-reunification-income/">family reunification income</a>.</p>
</div>
<p class="small">The calculation stays in your browser: we save nothing.</p>
</section>
<section>
<h2 id="citizenship">{G.ic("scudo")}Citizenship by residence: how much income</h2>
<p>The Ministry of the Interior uses as thresholds the income limits for pensioners' exemption from health charges: <strong>{eur_c(solo)}</strong> if you are alone,
<strong>{eur_c(con)}</strong> with a dependent spouse and <strong>{eur_c(fig)} more</strong> for each dependent child or family member.</p>
{src("vademecum", "pdf_prefettura")}
{tab_c}
<p class="small">For 5 or more children: add {eur_c(fig)} per child. The figures in the table are the same as in the Prefecture's PDF.</p>
<h3 id="which-income">Which income counts: gross or net?</h3>
<p>Only <strong>IRPEF taxable income declared in Italy</strong> in the <strong>last {anni_tre} years</strong> counts; income earned abroad does not. On the 730 return it is the «Reddito imponibile» of the «Prospetto di liquidazione»;
for the «Redditi PF» return and the «Certificazione Unica» the Prefecture explains which lines to add up.</p>
{src("pdf_prefettura", "vademecum")}
<h3 id="family">Family income</h3>
<p>You can add the income of the family members listed in art. 433 of the Civil Code who are in your family register (stato di famiglia): spouse (or civil partner, or partner with a written cohabitation contract), children, parents, sons- and daughters-in-law, parents-in-law, brothers and sisters.
<strong>Not counted</strong>, according to the Vademecum: a partner with no legal tie (even with children together), a step-parent, a spouse living abroad.</p>
<h3 id="not-income">What does not count as income</h3>
<ul><li>the «reddito» or «pensione di cittadinanza»;</li><li>money in your bank account;</li><li>a pension received and taxed abroad;</li><li>unemployment benefit (NASpI), even though it is taxed.</li></ul>
<p>If your income drops in a single year, the Vademecum says the Prefecture may assess it «in via equitativa» (fairly). But an application with declared income below the thresholds can be <strong>rejected online straight away</strong>,
and the income must be <strong>kept until the oath</strong>.</p>
{src("vademecum")}
</section>
<section>
<h2 id="carta-di-soggiorno">{G.ic("doc")}Carta di soggiorno (EU long-term permit): how much income</h2>
<p>The law asks for at least <strong>{anni_carta} years</strong> with a residence permit and an income <strong>not lower than the social allowance</strong>: in {anno} that is <strong>{eur_c(annuo)} a year</strong>.
If you also apply for your family members, the income follows the family reunification rule: social allowance <strong>+ {eur_c(meta)} for each family member</strong>. Suitable housing is also required.</p>
{src("tu9", extra=inps)}
{tab_k}
<p class="small">«Per month» is only a help for comparing: the law speaks of yearly income. The Questura decides which documents and which income are valid. <a href="../carta-di-soggiorno-requirements/">All carta di soggiorno requirements</a>.</p>
</section>
<section>
<h2>{G.ic("info")}Frequently asked questions</h2>
{faq_html}
</section>
<div class="due">
<section>
<h2>{G.ic("lista")}Next steps</h2>
{griglia_guide(G, "../", salta="income-requirement-italian-citizenship/")}
</section>
<aside>{modulo(G, "../")}</aside>
</div>
{in_italiano(G, "../../reddito-minimo-cittadinanza/", "Reddito minimo per la cittadinanza e la carta di soggiorno")}
<script>{js_calcolo(G, js_soglie)}</script>"""
    titolo = G.titolo_pagina(f"Income requirement for Italian citizenship {anno}: calculator",
                             f"Italian citizenship income requirement {anno}")
    descr = G.descrizione_pagina(
        f"Minimum income for Italian citizenship {anno}: {eur_c(solo)} alone, {eur_c(con)} with spouse, + {eur_c(fig)} per child. Carta di soggiorno: {eur_c(annuo)}. Calculator.")
    pagina_en(G, "en/income-requirement-italian-citizenship/", titolo, descr, corpo, it="reddito-minimo-cittadinanza/index.html", jsonld=ld)


def tabella_carta(G):
    anno = G.RICONG["anno"]
    annuo = G.cent(G.RICONG["assegno_sociale"]["annuo"])
    meta = annuo // 2
    righe = "".join(
        f'<tr><td><strong>{"just for you" if n == 0 else ("you and 1 family member" if n == 1 else f"you and {n} family members")}</strong></td>'
        f'<td data-l="People">{n + 1} {"person" if n == 0 else "people"}</td><td data-l="Per year"><strong>{eur_c(annuo + meta * n)}</strong></td>'
        f'<td data-l="Per month, over 12">{eur_c(round((annuo + meta * n) / 12))}</td></tr>' for n in range(0, 6))
    return (f'<div class="tab-wrap rc-tab"><table class="conf"><caption class="small">Minimum income {anno} for the carta di soggiorno (EU long-term residence permit)</caption>'
            '<thead><tr><th scope="col">Who the carta is for</th><th scope="col">People</th><th scope="col">Minimum income per year</th><th scope="col">Per month, over 12 months</th></tr></thead>'
            f'<tbody>{righe}</tbody></table></div>')


def pagina_domanda(G):
    C = G.CITT
    Fc, po = C["fonti"], C["polo_orienta"]
    v = max(f["verificato_il"] for f in Fc.values())
    contrib = eur(C["contributo_eur"], False)
    citaz = " ".join(x["testo"] for x in C["citazioni"])
    m24 = num(citaz, r"(ventiquattro) mesi")
    m36 = num(citaz, r"massimo di (trentasei) mesi")
    dal = data_it_en(num(citaz, r"a partire dal (\d{1,2} \w+ \d{4})"))
    mb1 = num(citaz, r"dimensione di (\d+) MB")
    mb2 = num(citaz, r"complessivo di (\d+) ?MB")
    giorni = num(po["giorni"], r"^(.*) dalle")
    giorni_en = ", ".join(GIORNI_EN[x] for x in re.split(r", | e ", giorni))
    ore = re.findall(r"\d{1,2}\.\d{2}", po["giorni"])
    if len(ore) != 2:
        raise SystemExit("genera_en: orari Polo Orienta non letti")
    con_pagina = sorted((sl for sl in G.PREF if G.ha_pagina_pref(sl)), key=lambda x: G.PREF[x]["nome"])
    pref_link = ", ".join(f'<a href="../../cittadinanza/{G.pref_url(sl)}/" hreflang="it" lang="it">{escape(G.PREF[sl]["nome"])}</a>' for sl in con_pagina)
    faq = [
        ("Where do I apply for Italian citizenship?",
         "Only online, on the Ministry of the Interior's Portale Servizi (ALI Cittadinanza), with SPID or CIE. The application is then handled by the Prefecture of the province where you live."),
        ("How much does the citizenship application cost?",
         f"The fee (contributo) is {contrib}: you attach the payment receipt to the application. You also need the details of the electronic revenue stamp (marca da bollo telematica)."),
        ("How long does Italian citizenship take?",
         f"For applications from {dal} the law (art. 9-ter of Law 91/1992) sets a time limit of {m24} months, extendable up to a maximum of {m36} months from the date of application. "
         "It is a legal time limit, not a forecast for your application."),
        ("How do I check the status of my application?",
         f"Online, in the Ministry's service, with the same credentials you used to apply. There is also the Polo Orienta contact centre: {po['telefono']}, {giorni_en} from {ore[0]} to {ore[1]}, with your K10 application number."),
    ]
    faq_html, ld = faq_blocco(G, [(escape(q), escape(t)) for q, t in faq])
    corpo = f"""<section class="hero">
{briciole(G, ("EsameB1 in English", "../"), ("How to apply", None))}
<span class="occhiello">{G.ic("edificio")}After the B1 exam · sources read on {data_en(v)}</span>
<h1>How to apply for Italian citizenship by residence</h1>
<p class="lead">According to the Ministry of the Interior (page read on {data_en(v)}), you apply for Italian citizenship only online, on the Ministry's Portale Servizi (ALI Cittadinanza) with SPID or CIE, and the fee is {contrib}.
The Prefecture of the province where you live then handles the application.</p>
<div class="risposta">
<div class="slot"><div class="r-et">{G.ic("web")}Where</div><div class="r-data">Online <small>SPID or CIE</small></div><div class="r-cosa">Ministry of the Interior's Portale Servizi (ALI)</div></div>
<div class="slot"><div class="r-et">{G.ic("euro")}Fee</div><div class="r-data">{contrib} <small>contributo</small></div><div class="r-cosa">plus the electronic revenue stamp</div></div>
<div class="r-piede"><a href="#steps">The steps {G.ic("freccia")}</a><span>{G.ic("doc")}Sources: Ministry of the Interior and Prefectures</span></div>
</div>
</section>
{avviso(G, "This site does not belong to the Ministry or the Prefectures and gives no advice on your application. <strong>The Prefecture decides.</strong> For your case write to the citizenship office or ask a patronato.")}
<section>
<h2 id="steps">{G.ic("lista")}How to apply, step by step</h2>
<ol class="passi">
<li><div><strong>Apply online only</strong>, on the {a(Fc["portale"]["url"], "Ministry of the Interior's Portale Servizi")} (ALI Cittadinanza), with <strong>SPID or CIE</strong>.</div></li>
<li><div><strong>Documents to attach</strong>: identity document, birth certificate and criminal record certificate from your country of origin, Italian language certificate at <a href="../italian-b1-exam-for-citizenship/">B1</a> or higher (unless <a href="../language-test-exemptions/">exempt</a>), fee receipt, details of the electronic revenue stamp.</div></li>
<li><div><strong>Fee of {contrib}</strong>: attach the payment receipt.</div></li>
<li><div><strong>Income</strong>: you need at least the <a href="../income-requirement-italian-citizenship/">Ministry's thresholds</a> (for citizenship by residence).</div></li>
<li><div><strong>After sending</strong>: your application gets a K10 number; you check its status online with the same credentials.</div></li>
</ol>
{fonte(G, a(Fc["domanda"]["url"], Fc["domanda"]["nome"]) + " · " + a(Fc["consulta"]["url"], Fc["consulta"]["nome"]), max(Fc["domanda"]["verificato_il"], Fc["consulta"]["verificato_il"]), "Sources (in Italian)")}
<p>Who can apply by residence, and after how many years, depends on your situation: the {a(Fc["residenza"]["url"], "Department for Civil Liberties and Immigration")} lists the cases (in Italian). The Prefecture decides.</p>
</section>
<section>
<h2 id="after">{G.ic("orologio")}After applying: time limit and status</h2>
<ul>
<li><strong>Time limit:</strong> for applications from {dal} the law sets a time limit of <strong>{m24} months, extendable up to a maximum of {m36}</strong> from the date of application ({a(Fc["legge"]["url"], "art. 9-ter of Law 91/1992")}). It is a legal time limit, not a forecast: your application may take a different time.</li>
<li><strong>Status:</strong> online, with the same credentials you used to apply.</li>
<li><strong>Communications:</strong> the Ministry gives the PEC address <a href="mailto:{C["pec_ministero"]}">{C["pec_ministero"]}</a>, one application per message, with the K10 number in the subject; attachments in PDF, TIFF or JPEG up to {mb1} MB each and {mb2} MB in total.</li>
<li><strong>Polo Orienta</strong> (the Ministry's contact centre): tel. {po["telefono"]}, {giorni_en} from {ore[0]} to {ore[1]}, PEC <a href="mailto:{po["pec"]}">{po["pec"]}</a>. Keep your K10 number and an ID document ready.</li>
</ul>
{fonte(G, " · ".join(a(Fc[k]["url"], Fc[k]["nome"]) for k in ("legge", "residenza", "domanda", "consulta")), v, "Sources (in Italian)")}
</section>
<section>
<h2 id="prefectures">{G.ic("pin")}Your Prefecture</h2>
<p>The email and PEC addresses of the citizenship office of all {len(G.PREF)} Prefectures are listed on our Italian page: <a href="../../cittadinanza/#elenco" hreflang="it" lang="it">le {len(G.PREF)} Prefetture: contatti</a>.
For these Prefectures we also report what their own page says (contacts, opening hours, local rules), in Italian: {pref_link}.</p>
</section>
<section>
<h2>{G.ic("info")}Frequently asked questions</h2>
{faq_html}
</section>
<div class="due">
<section>
<h2 id="exam">{G.ic("cal")}No B1 certificate yet?</h2>
<p>See <a href="../b1-exam-dates/">all exam dates</a>, <a href="../b1-exam-cost/">how much it costs</a> and <a href="../language-test-exemptions/">who is exempt</a>.</p>
{griglia_guide(G, "../", salta="apply-italian-citizenship-by-residence/")}
</section>
<aside>{modulo(G, "../")}</aside>
</div>
{riquadro_preparati(G, "../")}
{in_italiano(G, "../../cittadinanza/", "Domanda di cittadinanza, prefettura per prefettura")}"""
    titolo = G.titolo_pagina(f"How to apply for Italian citizenship by residence: ALI, {contrib}",
                             "How to apply for Italian citizenship by residence")
    descr = G.descrizione_pagina(
        f"Italian citizenship application in English: online on the ALI portal with SPID or CIE, {contrib} fee, legal time limit {m24}-{m36} months, status check.")
    pagina_en(G, "en/apply-italian-citizenship-by-residence/", titolo, descr, corpo, it="cittadinanza/index.html", jsonld=ld)


def pagina_carta(G):
    ca = G.REDDITI["carta_soggiorno"]
    tu9 = ca["fonti"]["tu9"]
    A = G.RICONG["assegno_sociale"]
    anno = G.RICONG["anno"]
    annuo = G.cent(A["annuo"])
    meta = annuo // 2
    T = a2_test(G)
    Fe = G.esoneri["fonti"]
    anni_carta = num(" ".join(x["testo"] for x in G.REDDITI["citazioni"] if x["fonte"] == "tu9"), r"da almeno (cinque) anni")
    circ = num(A["fonte"], r"circolare n\. (\d+)")
    circ_d = data_it_en(A["fonte"])
    v = tu9["verificato_il"]
    corpo = f"""<section class="hero">
{briciole(G, ("EsameB1 in English", "../"), ("Carta di soggiorno", None))}
<h1>Carta di soggiorno requirements: years, income and A2 Italian test</h1>
<p class="lead">According to art. 9 of Italy's Consolidated Immigration Act (read on Normattiva on {data_en(v)}), the EU long-term residence permit, known as the «carta di soggiorno», requires at least {anni_carta} years with a valid residence permit,
an income not lower than the social allowance ({eur_c(annuo)} a year in {anno}) and a pass in an Italian language test (level A2, set by a decree of the Minister of the Interior).</p>
<div class="risposta">
<div class="slot"><div class="r-et">{G.ic("orologio")}Residence permit</div><div class="r-data">{anni_carta} years <small>at least</small></div><div class="r-cosa">with a valid permit</div></div>
<div class="slot"><div class="r-et">{G.ic("euro")}Income {anno}</div><div class="r-data">{eur_c(annuo)} <small>a year</small></div><div class="r-cosa">just for you · + {eur_c(meta)} per family member</div></div>
<div class="r-piede"><a href="#a2">The A2 test {G.ic("freccia")}</a><span>{G.ic("doc")}Sources: Immigration Act, INPS, Ministry of the Interior</span></div>
</div>
</section>
{decide(G, "The Questura")}
<section>
<h2 id="requirements">{G.ic("lista")}The requirements in short</h2>
<ul>
<li><strong>At least {anni_carta} years</strong> with a valid residence permit;</li>
<li><strong>income</strong> not lower than the yearly social allowance (assegno sociale); if you also apply for family members, the family reunification rule applies (+ half the allowance for each one);</li>
<li><strong>suitable housing</strong>;</li>
<li>a pass in the <strong>A2 Italian test</strong>, unless you are exempt.</li>
</ul>
{fonte(G, a(tu9["url"], "art. 9 of the Consolidated Immigration Act (Normattiva)"), v, "Source (in Italian)")}
</section>
<section>
<h2 id="income">{G.ic("euro")}Minimum income {anno}</h2>
<p>The social allowance {anno} is {eur_c(annuo)} a year ({a(A["url"], f"INPS circular no. {circ} of {circ_d}")}). For each family member included in the application add half: {eur_c(meta)}.</p>
{tabella_carta(G)}
<p class="small">«Per month» is only a help for comparing: the law speaks of yearly income. The Questura decides which documents and which income are valid. With 2 or more children under {T["minori"]}, ask the Questura whether the family reunification rule of double the allowance ({eur_c(annuo * 2)}) applies to you.
<a href="../income-requirement-italian-citizenship/#calculate">Income calculator</a>.</p>
</section>
<section>
<h2 id="a2">{G.ic("voce")}The A2 Italian test</h2>
<ol class="passi">
<li><span>Apply online to the Prefecture where you live, on the Ministry of the Interior's {a(Fe["portale"]["url"], "Portale Servizi")}.</span></li>
<li><span>The Prefecture calls you within {T["giorni_conv"]} days.</span></li>
<li><span>The test checks that you understand short texts and can interact; for example in Lecco: listening ({T["orale"]} minutes), reading ({T["scritta"]} minutes), written interaction ({T["inter"]} minutes).</span></li>
<li><span>You pass with at least <strong>{T["soglia"]}%</strong> of the score; if you fail, you can apply again only {T["ripeti"]} days after the previous test.</span></li>
</ol>
{fonte(G, a(Fe["dm2021"]["url"], Fe["dm2021"]["nome"]) + " · " + a(Fe["minint_test"]["url"], Fe["minint_test"]["nome"]) + " · " + a(Fe["lecco"]["url"], Fe["lecco"]["nome"]), G.esoneri["verificato_il"], "Sources (in Italian)")}
<p><strong>You do not take the test</strong> if, for example, you already have a certificate at A2 or higher from a recognised body (also the B1 for citizenship), an Italian school diploma, or serious learning limitations certified by a public health facility; children under {T["minori"]} are excluded too.
<a href="../language-test-exemptions/#carta-di-soggiorno">All A2 exemptions</a>.</p>
</section>
<section>
<h2 id="citizenship">{G.ic("scudo")}Carta di soggiorno and citizenship</h2>
<p>If you hold the EU long-term residence permit, you do not have to present the B1 certificate when you apply for citizenship (art. 9.1 of Law 91/1992): <a href="../language-test-exemptions/#citizenship">exemptions from the B1</a> ·
<a href="../apply-italian-citizenship-by-residence/">how to apply for citizenship</a>.</p>
</section>
<div class="due">
<section><h2>{G.ic("info")}More guides</h2>{griglia_guide(G, "../", salta="carta-di-soggiorno-requirements/")}</section>
<aside>{modulo(G, "../")}</aside>
</div>
<p class="small lingua-alt">{G.ic("web")}<span lang="it">In italiano:</span> <a href="../../reddito-minimo-cittadinanza/#carta-di-soggiorno" hreflang="it" lang="it">reddito minimo per la carta di soggiorno</a> ·
<a href="../../esonero-test-italiano/#carta-di-soggiorno" hreflang="it" lang="it">test di italiano A2 e chi è esonerato</a></p>"""
    titolo = G.titolo_pagina(f"Carta di soggiorno requirements {anno}: income and A2 test",
                             "Carta di soggiorno requirements: income and A2 test")
    descr = G.descrizione_pagina(
        f"EU long-term residence permit (carta di soggiorno) in English: {anni_carta} years with a permit, income from {eur_c(annuo)} a year in {anno}, A2 Italian test and exemptions.")
    pagina_en(G, "en/carta-di-soggiorno-requirements/", titolo, descr, corpo)


def pagina_ricongiungimento(G):
    R = G.RICONG
    A, r, sp = R["assegno_sociale"], R["regola"], R["sportello"]
    anno = R["anno"]
    annuo = Decimal(A["annuo"])
    righe_t = G.tabella_ricongiungimento()
    uno = righe_t[0]
    tre = next(x for x in righe_t if x[0] == 3)
    circ = num(A["fonte"], r"circolare n\. (\d+)")
    circ_d = data_it_en(A["fonte"])
    giorni_no = num(r["domanda"], r"nulla osta entro (\d+) giorni")
    over = num(sp["testo"], r"ultra (\d+)enni")
    anno_perm = num(sp["testo"], r"non inferiore a (un) anno")
    minori = num(r["testo"], r"agli anni (quattordici)")
    v = A["verificato_il"]
    righe = "".join(
        f'<tr><td><strong>{n} family {"member" if n == 1 else "members"}</strong></td><td data-l="People in the family">{n + 1} people</td>'
        f'<td data-l="Per year"><strong>{eur(tot)}</strong></td><td data-l="Per month, over 12">{eur(m12)}</td><td data-l="Per month, over 13">{eur(m13)}</td></tr>'
        for n, tot, m12, m13 in righe_t)
    doppio = annuo * 2
    righe += (f'<tr><td><strong>2 or more children under {minori}</strong></td><td data-l="People in the family">–</td><td data-l="Per year"><strong>{eur(doppio)}</strong></td>'
              f'<td data-l="Per month, over 12">{eur(doppio / 12)}</td><td data-l="Per month, over 13">{eur(doppio / 13)}</td></tr>')
    fonte_inps = a(A["url"], f"INPS circular no. {circ} of {circ_d}")
    fonte_tu = a(r["url"], "art. 29 of the Consolidated Immigration Act")
    corpo = f"""<section class="hero">
{briciole(G, ("EsameB1 in English", "../"), ("Family reunification income", None))}
<span class="occhiello">{G.ic("euro")}Official sources · {data_en(v)}</span>
<h1>Family reunification in Italy: income requirement {anno}</h1>
<p class="lead">According to {fonte_inps} and art. 29 of the Consolidated Immigration Act (checked on {data_en(v)}), in {anno} family reunification requires an income of at least {eur(uno[1])} a year with 1 family member,
plus {eur(annuo / 2)} for each additional family member. It is the {anno} social allowance ({eur(annuo)} a year) increased by half for each family member.</p>
<div class="risposta">
<div class="slot"><div class="r-et">{G.ic("pin")}With 1 family member</div><div class="r-data">{eur(uno[1])} <small>a year</small></div><div class="r-cosa">wife, husband or 1 child · about {eur(uno[2])} a month over 12 months</div></div>
<div class="slot"><div class="r-et">{G.ic("euro")}Each additional member</div><div class="r-data">+ {eur(annuo / 2)}</div><div class="r-cosa">half the {anno} social allowance ({eur(annuo)} a year)</div></div>
<div class="r-piede"><a href="#table">Table by number of family members {G.ic("freccia")}</a><span>{G.ic("doc")}Sources: INPS and Immigration Act</span></div>
</div>
</section>
{decide(G, "The Sportello unico per l'immigrazione (immigration desk) of the Prefecture")}
<section>
<h2 id="table">{G.ic("lista")}Table {anno}: minimum income by number of family members</h2>
<p>In the first column count only the family members you want to bring to Italy. The second column includes you: for example «4 people» are you, your wife and 2 children, so 3 family members to bring.</p>
<div class="tab-wrap rc-tab"><table class="conf"><thead><tr><th scope="col">Family members to bring</th><th scope="col">People in the family, with you</th><th scope="col">Minimum income per year</th><th scope="col">Per month, over 12</th><th scope="col">Per month, over 13</th></tr></thead>
<tbody>{righe}</tbody></table></div>
{fonte(G, f"social allowance {anno}: {fonte_inps} ({a(A['url_allegato'], 'annex 2, table A')}) · rule: {fonte_tu}", v, "Sources (in Italian)")}
<p class="small">The law speaks of <strong>yearly</strong> income: the «per month» columns only help you compare with your salary.
Example: wife and 2 children = 3 family members: {eur(annuo)} + 3 × {eur(annuo / 2)} = {eur(tre[1])} a year.</p>
</section>
<section>
<h2 id="rules">{G.ic("info")}The rules</h2>
<h3>Two or more children under {minori}</h3>
<p>The law adds: for the reunification of two or more children under {minori} an income of at least <strong>double the yearly social allowance</strong> is required «in any case»: {eur(doppio)} in {anno}.
If other family members come with the children, or there are 3 or more children, the Sportello unico decides how the two rules combine.</p>
<h3>What counts as income</h3>
<p>The law asks for a yearly income «from lawful sources» and adds the income of family members who already live with you. Which documents prove it, and for which year, is decided by the Sportello unico of your Prefecture.</p>
<h3>Who you can bring</h3>
<p>According to the Ministry of the Interior you can apply if you live legally in Italy with a residence permit valid for at least {anno_perm} year, for: your spouse (adult, not legally separated); unmarried minor children, with the other parent's consent;
adult dependent children who are totally disabled; dependent parents, if they have no other children in the country of origin, or parents over {over} whose other children cannot support them for serious health reasons.</p>
<h3>Where to apply</h3>
<p>The application for the nulla osta (clearance) is sent online to the Sportello unico per l'immigrazione of the Prefecture where you live, with documents on income and housing, on the {a(sp["portale_url"], "Ministry of the Interior's Portale Servizi")} with SPID or CIE.
By law the nulla osta must be issued within {giorni_no} days of the application. You also need suitable housing, checked by the municipality.</p>
{fonte(G, a(sp["url"], sp["nome"]) + " · " + fonte_tu, sp["verificato_il"], "Sources (in Italian)")}
</section>
<div class="due">
<section><h2>{G.ic("info")}More guides</h2>{griglia_guide(G, "../", salta="family-reunification-income/")}</section>
<aside>{modulo(G, "../")}</aside>
</div>
{in_italiano(G, "../../reddito-ricongiungimento-familiare/", "Reddito minimo per il ricongiungimento familiare")}"""
    titolo = G.titolo_pagina(f"Family reunification Italy {anno}: income requirement table",
                             f"Family reunification Italy {anno}: income table")
    descr = G.descrizione_pagina(
        f"Family reunification in Italy {anno}: at least {eur(uno[1])} a year with 1 family member, + {eur(annuo / 2)} for each extra member. Table, rules and sources.")
    pagina_en(G, "en/family-reunification-income/", titolo, descr, corpo, it="reddito-ricongiungimento-familiare/index.html")


def privacy(G):
    cookie = G.MON.privacy_cookie("en", G.SITO_ID, G.ci_sono_affiliati()) or (
        "<h2>Cookies and visit counter</h2><p>This site does not use profiling cookies. To count visits we use GoatCounter, which sets no cookies and keeps only aggregate numbers.</p>")
    amazon = ("<h2>Amazon Associates Programme</h2><p>We take part in the Amazon EU Associates Programme, an affiliate programme that lets sites earn advertising fees by advertising and linking to Amazon.it. "
              f"{FRASE_AMAZON_EN} Links to Amazon.it lead to book searches: prices and availability are shown only on Amazon and may change.</p>") if G.url_affiliato("amazon") else ""
    corpo = f"""<section class="hero">{briciole(G, ("EsameB1 in English", "../"), ("Privacy", None))}<h1>Privacy notice</h1><p class="small">Last updated: October 2026. This is an English summary; the <a href="../../privacy.html" hreflang="it" lang="it">Italian privacy notice</a> is the reference text.</p></section>
<h2>Who processes the data</h2><p>The data controller is the person who runs {G.NOME} as an independent project in Italy, named in the Italian privacy notice. You can write to us by replying to any email we send you.</p>
<h2>What data we collect</h2><p>Only if you fill in the «Notify me» form: your email, the city and exam body you choose, and the page or link you came from (to understand which channels work).</p>
<h2>Why</h2><p>To send you alerts about B1 exam dates and deadlines. The legal basis is your consent (art. 6.1.a GDPR), which you can withdraw at any time.</p>
<h2>Who handles it for us</h2><p>The site and the form are hosted by Netlify, Inc., which stores the form data on our behalf. Netlify may process data outside the EU with the safeguards required by the GDPR (standard contractual clauses). We do not sell or share your data.</p>
{cookie}{amazon}
<h2>How long</h2><p>As long as you are subscribed to the alerts. If you ask us to delete your data, we delete it.</p>
<h2>Your rights</h2><p>You can ask for access, correction, deletion, restriction, portability and object (Articles 15-22 GDPR), and you can complain to the Italian Data Protection Authority (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>).</p>
{in_italiano(G, "../../privacy.html", "Informativa privacy")}"""
    pagina_en(G, "en/privacy/", "Privacy | EsameB1", "Privacy notice of the EsameB1 website, in English.", corpo, it="privacy.html")


def genera(G, prossime):
    """Scrive le pagine /en/ e restituisce i loro URL (per la sitemap)."""
    PAGINE.clear()
    hub(G, prossime)
    pagina_date(G, prossime)
    pagina_esame(G, prossime)
    pagina_costo(G)
    pagina_risultati(G)
    for e in G.enti:
        pagina_ente(G, e, prossime)
    pagina_esempi(G)
    pagina_esoneri(G)
    pagina_redditi(G)
    pagina_domanda(G)
    pagina_carta(G)
    pagina_ricongiungimento(G)
    privacy(G)
    scritte = {p["en"][:-10] for p in PAGINE}
    attese = {c[0] for c in COPPIE}
    if scritte != attese:
        raise SystemExit(f"genera_en: pagine in COPPIE non scritte o in più: {sorted(scritte ^ attese)}")
    return [c[0] for c in COPPIE]


# ---------------------------------------------------------------- controlli dopo la generazione
RE_ALT = re.compile(r'<link rel="alternate" hreflang="([a-zA-Z-]+)" href="([^"]+)">')
RE_CANON = re.compile(r'<link rel="canonical" href="([^"]+)">')
RE_NUM = re.compile(r"\d+(?:[.,]\d+)*")
RE_EUR_EN = re.compile(r"€\s?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\d+(?:\.\d{2})?)")
RE_EUR_IT = re.compile(r"(\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?)\s?€|€\s?(\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?)")


def testo_main(html):
    """Testo visibile del solo <main> (senza script, stili e le opzioni del modulo)."""
    m = html[html.find("<main"): html.find("</main>")]
    m = re.sub(r"<(script|style|select)\b.*?</\1>", " ", m, flags=re.S | re.I)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", m)))


def cifre(testo):
    """Cifre di un testo, senza separatori: «8.263,31» e «8,263.31» diventano entrambe «826331»."""
    return {re.sub(r"\D", "", x) for x in RE_NUM.findall(testo)}


def euro_en(testo):
    return {Decimal(x.replace(",", "")) for x in RE_EUR_EN.findall(testo)}


def euro_it(testo):
    return {Decimal((x or y).replace(".", "").replace(",", ".")) for x, y in RE_EUR_IT.findall(testo)}


def date_en_testo(testo):
    """Date complete in un testo inglese («11 November 2026») come (anno, mese, giorno)."""
    return {(int(y), MONTHS.index(m) + 1, int(g)) for g, m, y in re.findall(r"\b(\d{1,2}) (" + "|".join(MONTHS) + r") (\d{4})\b", testo)}


def date_it_testo(testo, html):
    """Date nelle pagine italiane: «11 novembre 2026», «19/12/2025» e gli attributi datetime="2026-11-11"."""
    out = {(int(y), MESI.index(m) + 1, int(g)) for g, m, y in re.findall(r"\b(\d{1,2}) (" + "|".join(MESI) + r") (\d{4})\b", testo, re.I)}
    out |= {(int(y), int(m), int(g)) for g, m, y in re.findall(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", testo)}
    out |= {(int(y), int(m), int(g)) for y, m, g in re.findall(r'datetime="(\d{4})-(\d{2})-(\d{2})"', html)}
    return out


def controlli(G):
    """Dopo la generazione: (1) cifre e importi di ogni pagina /en/ presenti nelle pagine italiane di riferimento;
    (2) hreflang reciproci (ogni pagina con alternati li ha uguali a quelli della pagina indicata, sé stessa compresa);
    (3) calcolatore dei redditi identico all'italiano; (4) link visibili tra le due lingue; (5) prima frase con fonte e data."""
    errori = []
    sito = G.SITO
    leggi = lambda p: (sito / p).read_text(encoding="utf-8")  # noqa: E731
    for p in PAGINE:
        en = leggi(p["en"])
        rif = ([p["it"]] if p["it"] else []) + p["rif"]
        if not rif:
            continue
        t_en = testo_main(en)
        t_it = " ".join(testo_main(leggi(r)) for r in rif)
        if p["en"] == "en/privacy/index.html":  # testo legale comune (monetizzazione.py: «Art. 6(1)(a)»…), non cifre dei dati
            t_en = ""

        manca = sorted(cifre(t_en) - cifre(t_it), key=lambda x: (len(x), x))
        if manca:
            errori.append(f"{p['en']}: cifre assenti nelle pagine italiane {rif}: {manca}")
        html_it = " ".join(leggi(r) for r in rif)
        manca_d = sorted(date_en_testo(t_en) - date_it_testo(t_it, html_it))
        if manca_d:
            errori.append(f"{p['en']}: date assenti nelle pagine italiane {rif}: {manca_d}")
        manca_e = sorted(euro_en(t_en) - euro_it(t_it))
        if manca_e:
            errori.append(f"{p['en']}: importi in euro assenti nelle pagine italiane {rif}: {manca_e}")
        if "lang=\"en\"" not in en[:200]:
            errori.append(f"{p['en']}: manca lang=\"en\"")
        if p["it"] and not re.search(r'<main.*<a href="[^"]+" hreflang="it" lang="it">', en, re.S):
            errori.append(f"{p['en']}: manca il link visibile alla pagina italiana")
        if p["en"] != "en/privacy/index.html":
            lead = re.search(r'<p class="lead">(.*?)</p>', en, re.S)
            prima = re.split(r"(?<=[.])\s(?=[A-Z])", re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", lead.group(1)))).strip() if lead else "")[0]
            if not (lead and re.search(r"(According to|checked on|read on)", prima) and re.search(r"\b(" + "|".join(MONTHS) + r") \d{4}\b", prima)):
                errori.append(f"{p['en']}: la prima frase non dice fonte e data: «{prima[:120]}»")
            if not re.search(r"decides", testo_main(en)):
                errori.append(f"{p['en']}: manca «… decides» (Prefettura/Questura/Sportello)")
    # hreflang reciproci su tutto il sito
    per_url, alternati = {}, {}
    for f in sito.rglob("*.html"):
        t = f.read_text(encoding="utf-8")
        c = RE_CANON.search(t)
        if not c:
            continue
        per_url[c.group(1)] = f
        alt = RE_ALT.findall(t)
        if alt:
            alternati[c.group(1)] = dict(alt)
    for url, alt in alternati.items():
        lingua = "en" if "/en/" in url else "it"
        if alt.get(lingua) != url:
            errori.append(f"hreflang: {url} non indica sé stessa come «{lingua}»")
        if set(alt) != {"it", "en", "x-default"} or alt["x-default"] != alt["it"]:
            errori.append(f"hreflang: {url} deve avere it, en e x-default (= it): {alt}")
        for lg, dest in alt.items():
            if dest not in per_url:
                errori.append(f"hreflang: {url} → {dest} ({lg}) non esiste")
            elif alternati.get(dest) != alt:
                errori.append(f"hreflang: {url} → {dest} non reciproco")
    coppie_attese = {G.URL_SITO + "/" + en for en, it, _ in COPPIE if it}
    if {u for u in alternati if "/en/" in u} != coppie_attese:
        errori.append("hreflang: le pagine inglesi con alternati non corrispondono a COPPIE")
    for en, it, _ in COPPIE:
        if it:
            t = leggi(it)
            if f'href="' not in t or not re.search(r'<nav class="menu".*?hreflang="en"', t, re.S):
                errori.append(f"{it}: manca il link «English» nel menu")
    # calcolatore: stesso blocco di calcolo nelle due lingue
    blocco = lambda t: t[t.find("/*calcolo-inizio*/"): t.find("/*calcolo-fine*/")]  # noqa: E731
    b_it, b_en = blocco(leggi("reddito-minimo-cittadinanza/index.html")), blocco(leggi("en/income-requirement-italian-citizenship/index.html"))
    if not b_it or b_it != b_en:
        errori.append("calcolatore: il blocco di calcolo inglese è diverso da quello italiano")
    if errori:
        raise SystemExit("ERRORI NELLA SEZIONE /en/:\n" + "\n".join(errori))
    return len(PAGINE)
