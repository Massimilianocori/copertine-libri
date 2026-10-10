"""Versione italiana di Italy Strikes Today, nella sezione /it/ dello stesso sito.

Chiamato da genera.py quando VERSIONE_IT_ATTIVA è True (o con ITALYSTRIKES_IT=1 per l'anteprima).
Stessi dati (dati/vista.json ha anche i campi *_it), stesso stile; testi del registro mostrati in italiano originale.
Stessa pubblicazione del sito inglese: nessun credito Netlify in più.
"""
import json
import re
from datetime import date, timedelta
from html import escape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
luoghi = json.loads((RADICE / "dati" / "luoghi.json").read_text(encoding="utf-8"))
CITTA_IT = luoghi["citta_it"]
EN_TO_IT_CITTA = {c["en"]: c["slug"] for c in CITTA_IT if c.get("en")}
IT_TO_EN_CITTA = {v: k for k, v in EN_TO_IT_CITTA.items()}
APT = luoghi["aeroporti"]
APT_EN_IT = {a["slug"]: a["slug_it"] for a in APT}
MESI_EN = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
MESI_IT = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
MES_IT = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]
GG_IT = ["lun", "mar", "mer", "gio", "ven", "sab", "dom"]
GIORNI_IT = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]

SETTORI_IT = {  # slug pagina it: (slug filtro, nome, titolo, testo)
    "treni": ("trains", "Treni", "Sciopero treni",
              "Scioperi di Trenitalia, Italo, Trenord e degli altri treni regionali. Gli scioperi nazionali del treno spesso iniziano alle 21:00 della sera prima e finiscono alle 21:00 del giorno di sciopero. Alcuni treni sono sempre garantiti."),
    "aerei": ("flights", "Aerei e aeroporti", "Sciopero aerei e aeroporti",
              "Scioperi del personale delle compagnie aeree, del controllo del traffico aereo (ENAV), dell'handling e della sicurezza negli aeroporti. I voli in programma dalle 7 alle 10 e dalle 18 alle 21 devono essere effettuati."),
    "mezzi-pubblici": ("local-transport", "Bus, metro e tram", "Sciopero mezzi pubblici: bus, metro e tram",
                       "Scioperi del trasporto pubblico locale, di solito di 4 o 24 ore. Ogni città ha le sue fasce di garanzia, decise dall'azienda di trasporto."),
    "traghetti": ("ferries", "Traghetti e porti", "Sciopero traghetti e porti",
                  "Scioperi del trasporto marittimo e dei porti. I collegamenti con le isole minori sono spesso garantiti."),
    "taxi": ("taxis", "Taxi", "Sciopero taxi", "Scioperi dei taxi e degli NCC, di solito locali."),
    "sciopero-generale": ("general-strikes", "Scioperi generali", "Sciopero generale",
                          "Uno sciopero generale può coinvolgere tutti i settori, compresi i trasporti. Il registro indica quali trasporti aderiscono e con quali orari."),
    "autostrade": ("motorways", "Autostrade", "Sciopero autostrade e soccorso stradale",
                   "Scioperi del personale dei caselli, del soccorso stradale o dei servizi autostradali. Di solito il traffico continua."),
    "merci": ("freight", "Merci", "Sciopero trasporto merci",
              "Scioperi degli autotrasportatori o del trasporto merci su ferro. Di solito non riguardano i passeggeri."),
}
SETT_EN_IT = {"trains": "treni", "flights": "aerei", "local-transport": "mezzi-pubblici", "ferries": "traghetti", "taxis": "taxi",
              "general-strikes": "sciopero-generale", "motorways": "autostrade", "freight": "merci"}
FINESTRE = {"today": "oggi", "tomorrow": "domani", "this-week": "questa-settimana", "next-week": "prossima-settimana"}
GUIDE_EN_IT = {"guides/strike-free-periods": "guida/periodi-di-franchigia", "guides/strike-rules-notice-duration": "guida/regole-degli-scioperi"}


def percorso_it(p):
    """Pagina inglese -> pagina italiana equivalente (None se non c'è)."""
    if p == "":
        return "it/"
    t = p.strip("/")
    if t in FINESTRE:
        return f"it/{FINESTRE[t]}/"
    m = re.fullmatch(r"(\d{4})/([a-z]+)", t)
    if m and m.group(2) in MESI_EN:
        return f"it/{m.group(1)}/{MESI_IT[MESI_EN.index(m.group(2))]}/"
    if t in SETT_EN_IT:
        return f"it/{SETT_EN_IT[t]}/"
    if t in EN_TO_IT_CITTA:
        return f"it/{EN_TO_IT_CITTA[t]}/"
    if t in GUIDE_EN_IT:
        return f"it/{GUIDE_EN_IT[t]}/"
    if t == "airports":
        return "it/aeroporti/"
    m = re.fullmatch(r"airports/([a-z-]+)", t)
    if m and m.group(1) in APT_EN_IT:
        return f"it/aeroporti/{APT_EN_IT[m.group(1)]}/"
    return None


def percorso_en(p_it):
    t = p_it.strip("/")[3:] if p_it.startswith("it/") else p_it
    if t == "":
        return ""
    inv = {v: k for k, v in FINESTRE.items()}
    if t in inv:
        return f"{inv[t]}/"
    m = re.fullmatch(r"(\d{4})/([a-z]+)", t)
    if m and m.group(2) in MESI_IT:
        return f"{m.group(1)}/{MESI_EN[MESI_IT.index(m.group(2))]}/"
    inv = {v: k for k, v in SETT_EN_IT.items()}
    if t in inv:
        return f"{inv[t]}/"
    if t in IT_TO_EN_CITTA:
        return f"{IT_TO_EN_CITTA[t]}/"
    inv = {v: k for k, v in GUIDE_EN_IT.items()}
    if t in inv:
        return f"{inv[t]}/"
    if t == "aeroporti":
        return "airports/"
    inv = {v: k for k, v in APT_EN_IT.items()}
    m = re.fullmatch(r"aeroporti/([a-z-]+)", t)
    if m and m.group(1) in inv:
        return f"airports/{inv[m.group(1)]}/"
    return None


def costruisci(g):
    d = g.d

    def breve(x):
        return f"{GG_IT[x.weekday()]} {x.day} {MES_IT[x.month - 1]} {x.year}"

    def interv(a, b):
        a, b = d(a), d(b)
        if a == b:
            return breve(a)
        if a.year == b.year and a.month == b.month:
            return f"{GG_IT[a.weekday()]} {a.day} – {GG_IT[b.weekday()]} {b.day} {MES_IT[b.month - 1]} {b.year}"
        return f"{breve(a)} – {breve(b)}"

    def filtra(nome, filtro):
        da, a = g.finestra(nome)
        out = []
        for v in g.VOCI:
            if v["fine"] < da.isoformat() or v["inizio"] > a.isoformat():
                continue
            if not nome.startswith("month:") and (v["stato"] == "concluso" or v["fine"] < g.OGGI.isoformat()):
                continue
            tipo, _, val = filtro.partition(":")
            if tipo == "city" and val not in v["citta_it"]:
                continue
            if tipo == "airport" and val not in v["aeroporti"]:
                continue
            if tipo == "sector" and val not in v["settori"]:
                continue
            if tipo == "passengers" and not any(x in g.PASSEGGERI for x in v["settori"]):
                continue
            out.append(v)
        return out

    # ---------------- JS: lo stesso del sito inglese, con testi e campi italiani
    js = g.JS
    sost = [
        ("var MES=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];",
         "var MES=['gen','feb','mar','apr','mag','giu','lug','ago','set','ott','nov','dic'];"),
        ("var GG=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];", "var GG=['lun','mar','mer','gio','ven','sab','dom'];"),
        ("if(t==='city'&&v.citta.indexOf(val)<0)return;", "if(t==='city'&&v.citta_it.indexOf(val)<0)return;"),
        (">Today</span>", ">Oggi</span>"), (">Whole of Italy</span>", ">Tutta Italia</span>"),
        ("esc(v.settore_en.charAt(0).toUpperCase()+v.settore_en.slice(1))", "esc(v.settore_it)"),
        (">No longer in the register</span>", ">Non più nel registro</span>"),
        (">Called off (register note)</span>", ">Revocato (nota del registro)</span>"), (">Ended</span>", ">Concluso</span>"),
        ("esc(v.dove)", "esc(v.dove_it)"), ("esc(v.titolo)", "esc(v.titolo_it)"),
        ("""h+='<div class="dett"><b>Hours:</b> '+(v.ore_en?esc(v.ore_en)+' <span class="it">(register: '+esc(v.ore)+')</span>':'<span lang="it">'+esc(v.ore)+'</span>')+'</div>';""",
         """h+='<div class="dett"><b>Orari:</b> '+esc(v.ore_it)+'</div>';"""),
        ("""h+='<div class="dett"><b>Who:</b> '+(v.chi?esc(v.chi)+' <span class="it" lang="it">('+esc(v.categoria)+')</span>':'<span lang="it">'+esc(v.categoria)+'</span>')+'</div>';""",
         """h+='<div class="dett"><b>Chi:</b> '+(v.chi_it?esc(v.chi_it)+' <span class="it">('+esc(v.categoria)+')</span>':esc(v.categoria))+'</div>';"""),
        ("v.nota_en", "v.nota_it"), ("<b>Register note:</b> <span lang=\"it\">", "<b>Nota del registro:</b> <span>"),
        ("No longer listed in the official register as of ", "Non più presente nel registro ufficiale dal "),
        (" (likely called off): check with the operator.", " (probabilmente revocato): verifica con il gestore del servizio."),
        ("Unions: ", "Sindacati: "), (" · announced ", " · proclamato il "), ("official register (MIT id ", "registro ufficiale (id MIT "),
        ("""var w={'today':'today ('+breve(r[0])+')','tomorrow':'tomorrow ('+breve(r[0])+')','thisweek':'for the rest of this week','nextweek':'next week ('+interv(r[0],r[1])+')'}[n]||'in this period';""",
         """var w={'today':'oggi ('+breve(r[0])+')','tomorrow':'domani ('+breve(r[0])+')','thisweek':'nel resto della settimana','nextweek':'la prossima settimana ('+interv(r[0],r[1])+')'}[n]||'in questo periodo';"""),
        ("""'<div class="vuoto"><strong>No strikes listed '+w+'</strong> in the official register for this selection. Strikes must be announced at least 10 days ahead, but check again before you travel.</div>'""",
         """'<div class="vuoto"><strong>Nessuno sciopero in elenco '+w+'</strong> nel registro ufficiale per questa selezione. Gli scioperi vanno proclamati almeno 10 giorni prima, ma controlla di nuovo prima di partire.</div>'"""),
        ("+' (Italy time)'", "+' (ora italiana)'"),
        ("'The end date must be after the start date'", "'La data di ritorno deve essere dopo quella di partenza'"),
    ]
    for a, b in sost:
        if a not in js:
            raise SystemExit(f"genera_it: testo JS non trovato (il JS inglese è cambiato?): {a[:70]}")
        js = js.replace(a, b)
    JS_IT = js

    def scheda(v):
        oggi = g.OGGI.isoformat()
        b = ""
        if v["inizio"] <= oggi <= v["fine"] and v["stato"] not in ("rimosso dal registro", "revocato"):
            b += '<span class="badge oggi">Oggi</span>'
        if v["ambito"] == "national":
            b += '<span class="badge naz">Tutta Italia</span>'
        b += f'<span class="badge">{escape(v["settore_it"])}</span>'
        if v["stato"] == "rimosso dal registro":
            b += '<span class="badge stato">Non più nel registro</span>'
        if v["stato"] == "revocato":
            b += '<span class="badge stato">Revocato (nota del registro)</span>'
        if v["fine"] < oggi or v["stato"] == "concluso":
            b += '<span class="badge">Concluso</span>'
        chi = (f'{escape(v["chi_it"])} <span class="it">({escape(v["categoria"])})</span>' if v["chi_it"] else escape(v["categoria"]))
        h = (f'<article class="sc{" naz" if v["ambito"] == "national" else ""}" id="s{v["id"]}"><div class="quando">{escape(interv(v["inizio"], v["fine"]))}'
             f'<small>{escape(v["dove_it"])}</small></div><div class="cosa">{b}<div class="tit">{escape(v["titolo_it"])}</div>'
             f'<div class="dett"><b>Orari:</b> {escape(v["ore_it"])}</div><div class="dett"><b>Chi:</b> {chi}</div>')
        if v["nota_it"]:
            h += f'<div class="dett">{escape(v["nota_it"])}</div>'
        if v["note"]:
            h += f'<div class="dett"><b>Nota del registro:</b> <span>{escape(v["note"])}</span></div>'
        if v["stato"] == "rimosso dal registro":
            h += (f'<div class="dett">Non più presente nel registro ufficiale dal {breve(d(v["rimosso_il"]))} '
                  '(probabilmente revocato): verifica con il gestore del servizio.</div>')
        h += (f'<div class="fonte">Sindacati: {escape(v["sindacati"])} · proclamato il {breve(d(v["proclamazione"]))} · '
              f'<a href="{g.URL_REGISTRO}" rel="noopener">registro ufficiale (id MIT {escape(v["id"])})</a></div></div></article>')
        return h

    def vuoto(nome):
        da, a = g.finestra(nome)
        w = {"today": f"oggi ({breve(da)})", "tomorrow": f"domani ({breve(da)})", "thisweek": "nel resto della settimana",
             "nextweek": f"la prossima settimana ({interv(da.isoformat(), a.isoformat())})"}.get(nome, "in questo periodo")
        return (f'<div class="vuoto"><strong>Nessuno sciopero in elenco {w}</strong> nel registro ufficiale per questa selezione. '
                'Gli scioperi vanno proclamati almeno 10 giorni prima, ma controlla di nuovo prima di partire.</div>')

    def blocco(nome, filtro="all", id_=""):
        lista = filtra(nome, filtro)
        contenuto = "".join(scheda(v) for v in lista) if lista else vuoto(nome)
        return f'<div class="lista"{f" id={chr(34)}{id_}{chr(34)}" if id_ else ""} data-finestra="{nome}" data-filtro="{filtro}">{contenuto}</div>'

    def riquadri(filtro, base):
        out = []
        for nome, etich, url in (("today", "Oggi", "oggi/"), ("tomorrow", "Domani", "domani/"), ("thisweek", "Questa settimana", "questa-settimana/")):
            n = len(filtra(nome, filtro))
            da, a = g.finestra(nome)
            out.append(f'<a class="riq{" si" if n else ""}" href="{base}{url}"><div class="t">{etich}</div>'
                       f'<div class="n" data-conta="{nome}" data-filtro="{filtro}">{n}</div>'
                       f'<div class="s"><span data-giorno="{nome}">{escape(interv(da.isoformat(), a.isoformat()))}</span> · scioperi in elenco</div></a>')
        return '<div class="riquadri">' + "".join(out) + "</div>"

    def fresco():
        return (f'<p class="fresco">Registro ufficiale aggiornato al <strong data-reg>{breve(d(g.AGGIORNATO))}</strong> · '
                f'controllato <span data-letto>{escape(g.LETTO)} (ora italiana)</span> · fonte: <a href="{g.URL_REGISTRO}" rel="noopener">registro scioperi del MIT</a></p>')

    AVVISO = ('<p class="avviso">Gli scioperi possono essere revocati o modificati all\'ultimo momento. Prima di partire verifica sempre '
              'con l\'azienda di trasporto, la compagnia aerea o il gestore del servizio.</p>')

    def modulo(rel):
        opz = '<option value="Tutta Italia">Tutta Italia</option>' + "".join(
            f'<option value="{escape(c["nome"])}">{escape(c["nome"])}</option>' for c in CITTA_IT) + "".join(
            f'<option value="Aeroporto {a["iata"]}">Aeroporto {escape(a["nome_it"])} ({a["iata"]})</option>' for a in APT)
        return f"""<section class="card" id="avvisi" style="margin-top:30px">
<h2 style="margin-top:0">Ricevi un'email se c'è sciopero nei giorni del tuo viaggio</h2>
<p class="small" style="margin-top:-4px">Gratis, niente spam. Controlliamo il registro ufficiale ogni giorno e ti scriviamo solo se c'è uno sciopero nelle tue date e nel tuo luogo.</p>
<form class="form ajax" name="alerts" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="alerts">
<input type="hidden" name="source" value="">
<p class="hp"><label>Non compilare <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>La tua email<input type="email" name="email" required autocomplete="email" placeholder="nome@esempio.it"></label>
<div class="due-campi"><label>Partenza<input type="date" name="from" required data-min-oggi></label>
<label>Ritorno<input type="date" name="to" required data-min-oggi></label></div>
<label>Dove<select name="place" required>{opz}</select></label>
<label class="check"><input type="checkbox" name="consent" value="yes" required>
<span>Accetto di ricevere via email avvisi sugli scioperi per queste date da {g.NOME}. Posso cancellarmi quando voglio. Ho letto l'<a href="{rel}it/privacy.html">informativa privacy</a>.</span></label>
<button class="btn" type="submit">Avvisami</button>
<p class="errore" data-errore hidden>Invio non riuscito. Riprova tra poco.</p>
</form>
<div class="ok" data-ok hidden><strong>Fatto!</strong> Ti scriveremo se c'è uno sciopero nelle date del tuo viaggio.</div>
</section>"""

    def griglia_citta(rel):
        return '<div class="griglia">' + "".join(
            f'<a href="{rel}it/{c["slug"]}/">{escape(c["nome"])}<small>{len(filtra("upcoming", "city:" + c["slug"]))} in programma</small></a>' for c in CITTA_IT) + "</div>"

    def griglia_settori(rel):
        return '<div class="griglia">' + "".join(
            f'<a href="{rel}it/{s}/">{escape(n)}<small>{len(filtra("upcoming", "sector:" + f))} in programma</small></a>'
            for s, (f, n, _, _) in SETTORI_IT.items()) + "</div>"

    def mesi():
        return [(y, m) for y, m in g.mesi_da_mostrare()]

    def griglia_mesi(rel):
        return '<div class="griglia">' + "".join(
            f'<a href="{rel}it/{y}/{MESI_IT[m - 1]}/">{MESI_IT[m - 1].capitalize()} {y}<small>{len(filtra(f"month:{y}-{m:02d}", "all"))} in elenco</small></a>'
            for y, m in mesi() if (y, m) >= (g.OGGI.year, g.OGGI.month)) + "</div>"

    def pagina(percorso, titolo, descr, corpo, briciole=None, con_dati=True):
        file = percorso if percorso.endswith(".html") else percorso + "index.html"
        rel = "/"
        url_pag = g.URL_SITO + "/" + percorso
        g.URLS.append(percorso)
        alt_en = percorso_en(percorso)
        alt = (f'<link rel="alternate" hreflang="it" href="{url_pag}"><link rel="alternate" hreflang="en" href="{g.URL_SITO}/{alt_en}">'
               f'<link rel="alternate" hreflang="x-default" href="{g.URL_SITO}/{alt_en}">') if alt_en is not None else ""
        ld = []
        if briciole:
            voci = [{"@type": "ListItem", "position": 1, "name": "Scioperi oggi", "item": g.URL_SITO + "/it/"}]
            for i, (n, p) in enumerate(briciole, start=2):
                voci.append({"@type": "ListItem", "position": i, "name": n, "item": g.URL_SITO + "/" + p})
            ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": voci})
            bc = f'<nav class="briciole" aria-label="Percorso"><a href="{rel}it/">Scioperi oggi</a>' + "".join(
                f' › <a href="{rel}{p}">{escape(n)}</a>' for n, p in briciole[:-1]) + f" › {escape(briciole[-1][0])}</nav>"
        else:
            bc = ""
        ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
        dati_html = ""
        if con_dati:
            dati = {"letto_il": g.LETTO, "registro_aggiornato_al": g.AGGIORNATO, "scioperi": g.recenti()}
            dati_html = '<script type="application/json" id="dati">' + json.dumps(dati, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>"
        verifica = f'<meta name="google-site-verification" content="{g.GOOGLE_VERIFICA}">' if g.GOOGLE_VERIFICA else ""
        en_link = f'<a href="{rel}{alt_en}" hreflang="en" lang="en">English</a>' if alt_en is not None else ""
        testo = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titolo)}</title>
<meta name="description" content="{escape(descr)}">
<link rel="canonical" href="{url_pag}">
{alt}
<meta property="og:title" content="{escape(titolo)}">
<meta property="og:description" content="{escape(descr)}">
<meta property="og:type" content="website">
<meta property="og:image" content="{g.URL_SITO}/og.png">
<meta property="og:url" content="{url_pag}">
<meta property="og:locale" content="it_IT">
<meta name="theme-color" content="#B3261E">
{verifica}
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%23B3261E'/%3E%3Ctext x='32' y='44' font-family='Arial' font-weight='700' font-size='30' text-anchor='middle' fill='white'%3E!%3C/text%3E%3C/svg%3E">
<style>{g.CSS}</style>
{ld_html}
</head>
<body>
<header class="top"><div class="wrap">
<a class="logo" href="{rel}it/">Scioperi <span>oggi</span></a>
<nav class="menu" aria-label="Menu">
<a href="{rel}it/oggi/">Oggi</a><a href="{rel}it/domani/">Domani</a><a href="{rel}it/questa-settimana/">Settimana</a><a href="{rel}it/#citta">Città</a><a href="{rel}it/aeroporti/">Aeroporti</a><a href="{rel}it/guida/">Guide</a>{en_link}
</nav>
</div></header>
<main class="wrap">
{bc}
{corpo}
</main>
<footer><div class="wrap">
<p><strong>{g.NOME}</strong> è un sito indipendente. I dati vengono dal <a href="{g.URL_REGISTRO}" rel="noopener">registro ufficiale degli scioperi del Ministero delle Infrastrutture e dei Trasporti (MIT)</a>, con licenza <a href="https://creativecommons.org/licenses/by/4.0/deed.it" rel="noopener">CC BY 4.0</a>; non siamo collegati al Ministero, ai sindacati o alle aziende di trasporto.
<strong>Gli scioperi possono essere revocati o modificati all'ultimo momento: verifica sempre con l'azienda di trasporto prima di partire.</strong> Le informazioni non sono consulenza legale.</p>
<p>Registro ufficiale aggiornato al <span data-reg>{breve(d(g.AGGIORNATO))}</span> · controllato <span data-letto>{escape(g.LETTO)} (ora italiana)</span><br>
<a href="{rel}it/privacy.html">Privacy</a> · <a href="{rel}it/contatti/">Contatti</a> · <a href="{rel}it/guida/">Guide</a> · <a href="{rel}">English version</a></p>
</div></footer>
{dati_html}
<script>{JS_IT}</script>
</body>
</html>
"""
        dest = g.SITO / file
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(testo, encoding="utf-8")

    AD = g.AD

    # ---------------- pagine
    rel = "/"
    pagina("it/", "Sciopero oggi e domani: treni, aerei, bus e metro – elenco ufficiale",
           "C'è sciopero oggi o domani? Tutti gli scioperi di treni, aerei, aeroporti, bus, metro e traghetti dal registro ufficiale del Ministero dei Trasporti. Aggiornato ogni giorno.",
           f"""<section class="hero"><h1>Scioperi oggi e domani in Italia</h1>
<p class="lead">Tutti gli scioperi dei trasporti dal registro ufficiale del Ministero: treni, aerei e aeroporti, bus e metro, traghetti e taxi. Aggiornato ogni giorno.</p>{fresco()}</section>
{riquadri("passengers", "/it/")}
{AVVISO}
{AD}
<h2>Oggi</h2>
<p class="small">Scioperi che riguardano chi viaggia (trasporto passeggeri e scioperi generali).</p>
{blocco("today", "passengers")}
<h3>Domani</h3>
{blocco("tomorrow", "passengers")}
<h2>Prossimi 30 giorni</h2>
<div class="filtri" data-per="prossimi" role="group" aria-label="Filtra per tipo">
<button type="button" data-filtro="passengers" aria-pressed="true">Tutti i trasporti passeggeri</button>
<button type="button" data-filtro="sector:trains" aria-pressed="false">Treni</button>
<button type="button" data-filtro="sector:flights" aria-pressed="false">Aerei</button>
<button type="button" data-filtro="sector:local-transport" aria-pressed="false">Bus e metro</button>
<button type="button" data-filtro="sector:general-strikes" aria-pressed="false">Scioperi generali</button>
<button type="button" data-filtro="all" aria-pressed="false">Tutto (anche merci)</button>
</div>
{blocco("days:30", "passengers", "prossimi")}
<h2 id="citta">Scioperi per città</h2>
{griglia_citta("/")}
<h2>Per tipo di trasporto</h2>
{griglia_settori("/")}
<h2>Per mese</h2>
{griglia_mesi("/")}
<h2>Aeroporti</h2>
<div class="griglia">{"".join(f'<a href="/it/aeroporti/{a["slug_it"]}/">{escape(a["nome_it"])}<small>{a["iata"]}</small></a>' for a in APT)}</div>
{modulo("/")}
<h2>Da sapere</h2>
<div class="testo"><p>Gli scioperi nei trasporti vanno proclamati almeno 10 giorni prima e sono pubblicati nel registro del Ministero delle Infrastrutture e dei Trasporti. Durante quasi tutti gli scioperi alcuni servizi sono garantiti: vedi <a href="/it/guida/fasce-di-garanzia/">fasce di garanzia di treni, aerei e mezzi pubblici</a> e <a href="/it/guida/come-funzionano-gli-scioperi/">come funzionano gli scioperi</a>.</p></div>
{AD}""")

    for slug, nome_f, h1, tit in (("oggi", "today", "Scioperi oggi", "Sciopero oggi: treni, aerei, bus e metro – elenco ufficiale"),
                                  ("domani", "tomorrow", "Scioperi domani", "Sciopero domani: treni, aerei, bus e metro – elenco ufficiale"),
                                  ("questa-settimana", "thisweek", "Scioperi questa settimana", "Scioperi questa settimana: treni, aerei, mezzi pubblici"),
                                  ("prossima-settimana", "nextweek", "Scioperi la prossima settimana", "Scioperi prossima settimana: treni, aerei, mezzi pubblici")):
        da, a = g.finestra(nome_f)
        pagina(f"it/{slug}/", tit,
               f"{h1}: tutti gli scioperi di treni, aerei, aeroporti, bus, metro e traghetti dal registro ufficiale del Ministero dei Trasporti.",
               f"""<section class="hero"><h1>{h1}</h1>
<p class="lead"><span data-giorno="{nome_f}">{escape(interv(da.isoformat(), a.isoformat()))}</span>. Scioperi del trasporto passeggeri e scioperi generali dal registro ufficiale.</p>{fresco()}</section>
{AVVISO}
{blocco(nome_f, "passengers")}
{AD}
<h2>Altri scioperi nel registro</h2>
<p class="small">Merci, servizi autostradali e altri scioperi che di solito non riguardano i passeggeri.</p>
{blocco(nome_f, "sector:freight")}
{blocco(nome_f, "sector:motorways")}
<h2>Controlla la tua città</h2>
{griglia_citta(rel)}
{modulo(rel)}""", briciole=[(h1, f"it/{slug}/")])

    for y, m in mesi():
        chiave = f"month:{y}-{m:02d}"
        nome = f"{MESI_IT[m - 1]} {y}"
        n = len(filtra(chiave, "all"))
        intro = (f"Tutti gli scioperi dei trasporti di {nome} dal registro ufficiale: date, orari, città e chi sciopera." if n else
                 f"Per {nome} non ci sono ancora scioperi in elenco. Gli scioperi vanno proclamati almeno 10 giorni prima: la pagina si aggiorna ogni giorno.")
        archivio = '<p class="small">Il nostro archivio parte dal 10 ottobre 2026: gli scioperi precedenti di ottobre non sono mostrati.</p>' if (y, m) == (2026, 10) else ""
        p = f"it/{y}/{MESI_IT[m - 1]}/"
        pagina(p, f"Scioperi {nome}: treni, aerei, bus e metro – calendario completo",
               f"Calendario degli scioperi di {nome}: treni, aerei, aeroporti, mezzi pubblici e traghetti, con date e orari dal registro ufficiale.",
               f"""<section class="hero"><h1>Scioperi {nome}</h1><p class="lead">{intro}</p>{fresco()}{archivio}</section>
{AVVISO}
<h2>Scioperi che riguardano chi viaggia</h2>
{blocco(chiave, "passengers")}
{AD}
<h2>Merci e altri scioperi</h2>
{blocco(chiave, "sector:freight")}
{blocco(chiave, "sector:motorways")}
<h2>Altri mesi</h2>
{griglia_mesi("/")}
{modulo("/")}""", briciole=[(f"Scioperi {nome}", p)])

    for slug, (filtro, nome, tit, testo) in SETTORI_IT.items():
        guida = {"treni": "guida/fasce-di-garanzia/", "aerei": "guida/fasce-di-garanzia/", "mezzi-pubblici": "guida/fasce-di-garanzia/"}.get(slug)
        extra = f'<p>Vedi anche: <a href="{rel}it/{guida}">fasce di garanzia</a>.</p>' if guida else ""
        pagina(f"it/{slug}/", f"{tit}: oggi, domani e prossime date",
               f"{tit}: tutte le prossime date dal registro ufficiale, con orari e chi sciopera. Aggiornato ogni giorno.",
               f"""<section class="hero"><h1>{escape(tit)}</h1><p class="lead">{escape(testo)}</p>{extra}{fresco()}</section>
{riquadri("sector:" + filtro, rel + "it/")}
{AVVISO}
<h2>Prossimi scioperi: {escape(nome.lower())}</h2>
{blocco("upcoming", "sector:" + filtro)}
{AD}
<h2>Altri trasporti</h2>
{griglia_settori(rel)}
{modulo(rel)}""", briciole=[(tit, f"it/{slug}/")])

    for c in CITTA_IT:
        ops = [o for o in g.link_operatori({"operatori": c["operatori"]})] if c["operatori"] else []
        apts = [a for a in APT if a["slug"] in c["aeroporti"]]
        utili = "".join(f"<li>Trasporto locale: {o}</li>" for o in ops)
        utili += "".join(f'<li>Aeroporto: <a href="{rel}it/aeroporti/{a["slug_it"]}/">{escape(a["nome_it"])}</a></li>' for a in apts)
        utili += f'<li><a href="{rel}it/guida/fasce-di-garanzia/">Fasce di garanzia di treni, aerei e mezzi pubblici</a></li>'
        pagina(f"it/{c['slug']}/", f"Sciopero {c['nome']} oggi e domani: mezzi pubblici, treni e aerei",
               f"C'è sciopero a {c['nome']} oggi o domani? Prossimi scioperi di bus, metro, tram, treni e aerei che riguardano {c['nome']}, dal registro ufficiale. Aggiornato ogni giorno.",
               f"""<section class="hero"><h1>Sciopero a {escape(c["nome"])}: oggi e prossime date</h1>
<p class="lead">Scioperi che possono riguardare {escape(c["nome"])}: scioperi nazionali di treni, aerei e scioperi generali, scioperi in {escape(c["regione"])} e scioperi locali di bus, metro e tram.</p>{fresco()}</section>
{riquadri("city:" + c["slug"], rel + "it/")}
{AVVISO}
<h2>Prossimi scioperi a {escape(c["nome"])}</h2>
{blocco("upcoming", "city:" + c["slug"])}
{AD}
<h2>Link utili</h2><ul>{utili}</ul>
<h2>Altre città</h2>
{griglia_citta(rel)}
{modulo(rel)}""", briciole=[(f"Sciopero {c['nome']}", f"it/{c['slug']}/")])

    pagina("it/aeroporti/", "Sciopero aeroporti: Roma, Milano, Venezia, Napoli e altri",
           "Prossimi scioperi negli aeroporti italiani, delle compagnie aeree e del controllo del traffico aereo, dal registro ufficiale.",
           f"""<section class="hero"><h1>Scioperi negli aeroporti italiani</h1>
<p class="lead">Scioperi del trasporto aereo per aeroporto. Gli scioperi nazionali (controllo del traffico aereo, compagnie) possono riguardare tutti gli aeroporti.</p>{fresco()}</section>
<div class="griglia">{"".join(f'<a href="{a["slug_it"]}/">{escape(a["nome_it"])}<small>{a["iata"]} · {len(filtra("upcoming", "airport:" + a["slug"]))} in programma</small></a>' for a in APT)}</div>
{AVVISO}
<h2>Tutti i prossimi scioperi del trasporto aereo</h2>
{blocco("upcoming", "sector:flights")}
{modulo(rel)}""", briciole=[("Aeroporti", "it/aeroporti/")])
    enac = g.L("enac_voli_garantiti")
    for a in APT:
        r2 = "/"
        u = g.L(a["link"])
        sito = f'<a href="{escape(u)}" rel="noopener">sito ufficiale dell\'aeroporto</a>' if u else "sito ufficiale dell'aeroporto"
        pagina(f"it/aeroporti/{a['slug_it']}/", f"Sciopero aeroporto {a['nome_it']} ({a['iata']}): oggi e prossime date",
               f"C'è sciopero all'aeroporto di {a['nome_it']} ({a['iata']})? Prossimi scioperi del controllo del traffico aereo, delle compagnie e del personale aeroportuale, dal registro ufficiale.",
               f"""<section class="hero"><h1>Scioperi all'aeroporto {escape(a["nome_it"])} ({a["iata"]})</h1>
<p class="lead">Scioperi che possono riguardare i voli di {escape(a["nome_it"])}: scioperi nazionali del controllo del traffico aereo e delle compagnie, e scioperi del personale che lavora in questo aeroporto.</p>{fresco()}</section>
{riquadri("airport:" + a["slug"], r2 + "it/")}
{AVVISO}
<h2>Prossimi scioperi</h2>
{blocco("upcoming", "airport:" + a["slug"])}
{AD}
<h2>Cosa fare</h2>
<ul><li>Controlla il tuo volo con la compagnia aerea e sul {sito}.</li>
<li>Durante gli scioperi del trasporto aereo i voli in programma dalle 7 alle 10 e dalle 18 alle 21 devono essere effettuati{f', insieme ai <a href="{escape(enac)}" rel="noopener">voli garantiti indicati dall' + "'" + 'ENAC</a>' if enac else ''}.</li></ul>
{modulo(r2)}""", briciole=[("Aeroporti", "it/aeroporti/"), (a["nome_it"], f"it/aeroporti/{a['slug_it']}/")])

    # guide
    def a_(chiave, testo):
        u = g.L(chiave)
        return f'<a href="{escape(u)}" rel="noopener">{testo}</a>' if u else testo
    r3 = "/"
    ops = "".join(f'<li><strong>{escape(c["nome"])}</strong>: {", ".join(g.link_operatori({"operatori": c["operatori"]}))}</li>'
                  for c in CITTA_IT if c["operatori"] and g.link_operatori({"operatori": c["operatori"]}))
    pagina("it/guida/fasce-di-garanzia/", "Fasce di garanzia durante gli scioperi: treni, aerei, bus e metro",
           "Quali treni, voli e mezzi pubblici sono garantiti durante gli scioperi: fasce orarie ufficiali e dove trovare gli elenchi.",
           f"""<section class="hero"><h1>Fasce di garanzia durante gli scioperi</h1><p class="lead">Cosa funziona durante uno sciopero: treni, voli e mezzi pubblici garantiti, con le fonti ufficiali.</p></section>
<div class="testo">
<h2>Treni</h2>
<ul><li>Treni regionali di Trenitalia: garantiti nei giorni feriali dalle 6 alle 9 e dalle 18 alle 21; nei festivi dalle 7 alle 10 e dalle 18 alle 21.</li>
<li>Alcuni treni a lunga percorrenza (Frecce, Intercity) sono sempre garantiti: sono nella tabella dei treni garantiti di Trenitalia.</li>
<li>I treni già in viaggio all'inizio dello sciopero di norma arrivano a destinazione se possono raggiungerla entro un'ora dall'inizio; dopo possono fermarsi in una stazione precedente.</li>
<li>Trenitalia avverte che il servizio può subire modifiche anche poco prima dell'inizio e dopo la fine dello sciopero.</li></ul>
<p>Fonte: {a_("trenitalia_garantiti", "Trenitalia, servizi minimi garantiti in caso di sciopero")} (verificato il 10 ottobre 2026). Italo pubblica l'elenco dei treni garantiti sulla {a_("italo_scioperi", "sua home page")} prima di ogni sciopero; Trenord nella {a_("trenord_scioperi", "pagina dedicata")}.</p>
<h2>Aerei</h2>
<ul><li>I voli in programma dalle <strong>7 alle 10</strong> e dalle <strong>18 alle 21</strong> devono essere effettuati.</li>
<li>È garantito anche un elenco di voli essenziali (per esempio verso le isole): vedi {a_("enac_voli_garantiti", "voli garantiti dell'ENAC")} (verificato il 10 ottobre 2026).</li></ul>
<h2>Bus, metro e tram</h2>
<p>Durante gli scioperi di 24 ore ogni azienda garantisce il servizio in due fasce, di solito al mattino e nel pomeriggio o sera; gli orari cambiano da città a città. Negli scioperi di 4 ore di solito non ci sono fasce garantite.</p>
<ul>{ops}</ul>
</div>{AD}{modulo(r3)}""", briciole=[("Guide", "it/guida/"), ("Fasce di garanzia", "it/guida/fasce-di-garanzia/")], con_dati=False)
    pagina("it/guida/come-funzionano-gli-scioperi/", "Come funzionano gli scioperi dei trasporti in Italia",
           "Preavviso di 10 giorni, servizi minimi, registro del Ministero e revoche: come funzionano gli scioperi nei trasporti in Italia.",
           f"""<section class="hero"><h1>Come funzionano gli scioperi dei trasporti</h1><p class="lead">Le regole che contano per chi viaggia.</p></section>
<div class="testo"><ul>
<li><strong>Preavviso di almeno 10 giorni.</strong> Nei servizi pubblici essenziali (treni, aerei, trasporto locale, traghetti) lo sciopero va proclamato almeno 10 giorni prima ({a_("legge_146_1990", "legge 146 del 1990")}). Se una settimana prima del viaggio uno sciopero non è nel registro, è difficile che ci sia.</li>
<li><strong>Servizi minimi.</strong> Alcuni servizi devono funzionare comunque: <a href="{r3}it/guida/fasce-di-garanzia/">fasce di garanzia</a>.</li>
<li><strong>Il registro ufficiale.</strong> Ogni sciopero proclamato è pubblicato dal Ministero delle Infrastrutture e dei Trasporti nel <a href="{g.URL_REGISTRO}" rel="noopener">registro degli scioperi</a>. Questo sito lo legge due volte al giorno.</li>
<li><strong>La Commissione di garanzia</strong> controlla il rispetto delle regole e può chiedere di spostare o ridurre uno sciopero.</li>
<li><strong>Revoche.</strong> Gli scioperi a volte vengono revocati o rinviati anche pochi giorni prima. Quando uno sciopero sparisce dal registro prima della data lo segnaliamo.</li>
<li><strong>Periodi di franchigia.</strong> Intorno a Natale, Pasqua, ai ponti di fine aprile, all'estate e a Ognissanti gli scioperi dei trasporti non sono ammessi; le date dipendono dal settore: vedi <a href="{r3}it/guida/periodi-di-franchigia/">periodi di franchigia</a>.</li>
<li><strong>Durata.</strong> Gli scioperi ferroviari di 24 ore devono iniziare alle 21: per questo uno sciopero "di venerdì" comincia di solito giovedì sera. Altre regole in <a href="{r3}it/guida/regole-degli-scioperi/">preavviso, durata e intervalli</a>.</li>
</ul></div>{AD}{modulo(r3)}""", briciole=[("Guide", "it/guida/"), ("Come funzionano", "it/guida/come-funzionano-gli-scioperi/")], con_dati=False)
    pagina("it/guida/periodi-di-franchigia/", "Periodi di franchigia: quando gli scioperi dei trasporti non sono ammessi",
           "Le date in cui in Italia non si può scioperare nei treni, negli aerei e nel trasporto pubblico locale: Natale, Pasqua, estate, Ognissanti ed elezioni.",
           f"""<section class="hero"><h1>Periodi di franchigia degli scioperi nei trasporti</h1><p class="lead">Le date in cui, secondo le regole di ogni settore, gli scioperi dei trasporti non sono ammessi. Il primo e l'ultimo giorno sono compresi.</p></section>
<div class="testo">
{g.tabella_franchigie("it")}
<p>Ci sono anche periodi di franchigia intorno alle elezioni politiche ed europee e ai referendum nazionali (dai tre giorni prima ai tre giorni dopo il voto) e, più brevi, intorno alle elezioni locali nelle zone che votano.</p>
<h2>Rischio più basso, non zero</h2>
<p>Queste sono le regole; il registro mostra cosa è stato davvero proclamato. A ottobre 2026, per esempio, il registro riportava uno sciopero generale nazionale, compresi i treni, il 30 ottobre, primo giorno del periodo di Ognissanti. Controlla sempre <a href="{r3}it/oggi/">oggi</a>, <a href="{r3}it/domani/">domani</a> o la tua <a href="{r3}it/#citta">città</a>.</p>
<h2>Fonti</h2>
<ul><li>Treni: accordo nazionale del 23 novembre 1999 sugli scioperi nel trasporto ferroviario (testo coordinato), punto 3.5.1.</li>
<li>Aerei: regolamentazione provvisoria della Commissione di garanzia, delibera 14/387 del 13 ottobre 2014, art. 8, pubblicata dall'<a href="{g.URL_ENAC_REGOLE}" rel="noopener">ENAC</a>.</li>
<li>Trasporto pubblico locale: accordo nazionale del 28 febbraio 2018, valutato idoneo con delibera 18/138, art. 4.</li></ul>
<p class="small">Testi letti il 10 ottobre 2026.</p>
</div>{AD}{modulo(r3)}""", briciole=[("Guide", "it/guida/"), ("Periodi di franchigia", "it/guida/periodi-di-franchigia/")], con_dati=False)
    pagina("it/guida/regole-degli-scioperi/", "Perché gli scioperi dei treni iniziano alle 21: preavviso, durata e intervalli",
           "Le regole degli scioperi nei trasporti: 10 giorni di preavviso (12 per gli aerei), scioperi ferroviari di 24 ore dalle 21, primo sciopero breve, intervalli minimi.",
           f"""<section class="hero"><h1>Preavviso, durata e intervalli degli scioperi</h1><p class="lead">Le regole che spiegano gli orari che vedi nel registro.</p></section>
<div class="testo">
<h2>Preavviso</h2>
<ul><li>Almeno <strong>10 giorni</strong> (<a href="{g.URL_LEGGE_146_ART2}" rel="noopener">legge 146/1990, art. 2</a>); per il trasporto aereo le regole del settore prevedono <strong>12 giorni</strong>.</li>
<li>Le aziende devono comunicare agli utenti come funzionerà il servizio <strong>almeno cinque giorni prima</strong> dello sciopero.</li>
<li>Il preavviso non si applica agli scioperi in difesa dell'ordine costituzionale o di protesta per gravi eventi lesivi dell'incolumità e della sicurezza dei lavoratori.</li></ul>
<h2>Durata</h2>
<ul><li><strong>Treni:</strong> al massimo 24 ore, e gli scioperi di 24 ore devono iniziare alle 21. Il primo sciopero di una vertenza dura al massimo otto ore, dalle 9.01 alle 17.59 oppure dalle 21.01 alle 5.59.</li>
<li><strong>Trasporto locale:</strong> il primo sciopero di una vertenza non supera le quattro ore.</li>
<li><strong>Aerei:</strong> il primo sciopero dura al massimo quattro ore; i successivi al massimo una giornata.</li></ul>
<h2>Intervalli tra uno sciopero e l'altro</h2>
<ul><li><strong>Trasporto locale:</strong> almeno 20 giorni tra due scioperi che riguardano lo stesso bacino di utenza.</li>
<li><strong>Aerei:</strong> almeno 15 giorni liberi; 30 per il controllo del traffico aereo.</li></ul>
<p class="small">Fonti: legge 146/1990; accordo ferroviario 1999, punti 3.3.1 e 3.3.2; regole del trasporto pubblico locale 2018, artt. 11 e 12; regolamentazione del trasporto aereo 14/387, artt. 4, 7, 16 e 17. Lette il 10 ottobre 2026.</p>
</div>{AD}{modulo(r3)}""", briciole=[("Guide", "it/guida/"), ("Preavviso e durata", "it/guida/regole-degli-scioperi/")], con_dati=False)
    pagina("it/guida/", "Guide sugli scioperi dei trasporti", "Guide pratiche sugli scioperi dei trasporti in Italia.",
           '<section class="hero"><h1>Guide</h1><p class="lead">Guide brevi e pratiche sugli scioperi dei trasporti.</p></section>'
           '<div class="griglia"><a href="fasce-di-garanzia/">Fasce di garanzia<small>treni, aerei, bus e metro</small></a>'
           '<a href="come-funzionano-gli-scioperi/">Come funzionano gli scioperi<small>preavviso, registro, revoche</small></a>'
           '<a href="periodi-di-franchigia/">Periodi di franchigia<small>quando non si può scioperare</small></a>'
           '<a href="regole-degli-scioperi/">Preavviso, durata e intervalli<small>perché i treni scioperano dalle 21</small></a></div>',
           briciole=[("Guide", "it/guida/")], con_dati=False)

    pagina("it/contatti/", f"Contatti | {g.NOME}", f"Contatta {g.NOME}.", f"""<section class="hero"><h1>Contatti</h1><p class="lead">Correzioni, domande o suggerimenti: scrivici qui.</p></section>
<section class="card"><form class="form ajax" name="contact" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="contact"><input type="hidden" name="source" value="">
<p class="hp"><label>Non compilare <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>La tua email<input type="email" name="email" required autocomplete="email"></label>
<label>Messaggio<textarea name="message" rows="6" required maxlength="4000"></textarea></label>
<label class="check"><input type="checkbox" name="consent" value="yes" required><span>Ho letto l'<a href="../privacy.html">informativa privacy</a>.</span></label>
<button class="btn" type="submit">Invia</button><p class="errore" data-errore hidden>Invio non riuscito. Riprova.</p></form>
<div class="ok" data-ok hidden><strong>Grazie.</strong> Ti risponderemo via email.</div></section>""", briciole=[("Contatti", "it/contatti/")], con_dati=False)

    pagina("it/privacy.html", f"Privacy | {g.NOME}", f"Informativa privacy di {g.NOME}.", f"""<section class="hero"><h1>Informativa privacy</h1><p class="small">Ultimo aggiornamento: ottobre 2026</p></section><div class="testo">
<h2>Chi tratta i dati</h2><p>Titolare del trattamento è Massimiliano Cori (Italia), che gestisce {g.NOME} come progetto indipendente. Puoi scriverci dalla <a href="contatti/">pagina contatti</a> o rispondendo a una nostra email.</p>
<h2>Quali dati raccogliamo</h2><p>Solo quello che scrivi nei moduli: per gli avvisi, email, date del viaggio e luogo; per i contatti, email e messaggio. Registriamo anche la pagina o il link da cui arrivi, per capire quali canali funzionano.</p>
<h2>Perché</h2><p>Per mandarti gli avvisi sugli scioperi nelle date del tuo viaggio e per rispondere ai tuoi messaggi. La base giuridica è il tuo consenso (art. 6.1.a GDPR), che puoi ritirare quando vuoi.</p>
<h2>Chi li gestisce per noi</h2><p>Il sito e i moduli sono ospitati da Netlify, Inc., che conserva i dati dei moduli per nostro conto e può trattarli fuori dall'UE con le garanzie previste dal GDPR (clausole contrattuali standard). Non vendiamo né cediamo i tuoi dati.</p>
<h2>Cookie</h2><p>Il sito non usa cookie di profilazione né strumenti di statistica. Se in futuro aggiungeremo pubblicità aggiorneremo questa informativa e chiederemo il consenso dove serve.</p>
<h2>Per quanto tempo</h2><p>I dati degli avvisi restano finché le date del viaggio sono passate e poi vengono cancellati entro 60 giorni, salvo tua richiesta di cancellarli prima.</p>
<h2>I tuoi diritti</h2><p>Puoi chiedere accesso, rettifica, cancellazione, limitazione, portabilità e opposizione (artt. 15-22 GDPR) e fare reclamo al Garante per la protezione dei dati personali (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>).</p></div>""", con_dati=False)
