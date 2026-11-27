"""Pagine «Sciopero <azienda>: prossime date» (/it/sciopero-<azienda>/, indice /it/aziende/) e pagine dei giorni di
sciopero nazionale (/it/sciopero-4-dicembre-2026/ e /strike-4-december-2026/).

Tutto nasce per regola dai dati a ogni rigenerazione (regole in aziende.py):
- date, orari e stato vengono dal registro (dati/scioperi.json); gli orari sono sempre il testo della fonte, tra virgolette;
- le fasce di garanzia compaiono solo se le scrive una pagina ufficiale dell'azienda (dati/fasce.json), con link e data
  di lettura; i link alle aziende vengono solo da dati/link.json;
- la frase di risposta in cima è scritta alla generazione: porta data-firma, e il JS comune la nasconde se i dati più
  recenti (vista.json) non coincidono più; gli elenchi sotto si ridisegnano da soli come nel resto del sito;
- le pagine dei giorni passati restano online (come le pagine dei mesi) e dicono che lo sciopero è concluso.

Chiamato da genera.py (pagine in inglese, blocchi di link) e da genera_it.py (pagine in italiano).
"""
from datetime import date, timedelta
from html import escape

import aziende as AZ

GIORNI_IT = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
GIORNI_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MESI_EN = [m.capitalize() for m in AZ.MESI_EN]
SETT_TITOLO_IT = {"trains": "treni", "flights": "aerei", "local-transport": "bus e metro", "ferries": "traghetti", "taxis": "taxi"}
SETT_TITOLO_EN = {"trains": "trains", "flights": "flights", "local-transport": "buses and metro", "ferries": "ferries", "taxis": "taxis"}
SETT_PAGINA_IT = {"trains": "treni", "flights": "aerei", "local-transport": "mezzi-pubblici"}
ARCHIVIO_DAL = "10 ottobre 2026"   # primo giorno dell'archivio del sito (vedi pagina del mese di ottobre 2026)
CSS = """
.risposta{border-left:5px solid var(--accent);margin:0 0 20px}
.risposta.no{border-left-color:var(--ok)}
.risposta p{margin:0 0 10px}
.risposta ul{margin:0 0 10px;padding-left:20px}
.risposta li{margin:6px 0}
.risposta>div>:last-child,.risposta>p:last-child{margin-bottom:0}
.risposta .big{font-size:1.14rem;line-height:1.4}
.cit{margin:14px 0;padding:14px 16px;border-left:4px solid var(--line-2);background:var(--card);border-radius:0 12px 12px 0;max-width:760px}
.cit p{margin:0 0 8px}
.cit q{font-style:italic}
.cit .small{margin:0}
.storico{width:100%;text-align:left}
.storico-box{overflow-x:auto}
"""


# ---------------------------------------------------------------- testi comuni
def lunga_it(iso):
    x = date.fromisoformat(iso)
    return f"{GIORNI_IT[x.weekday()]} {x.day} {AZ.MESI_IT[x.month - 1]} {x.year}"


def corta_it(iso):
    x = date.fromisoformat(iso)
    return f"{x.day} {AZ.MESI_IT[x.month - 1]} {x.year}"


def lunga_en(iso):
    x = date.fromisoformat(iso)
    return f"{GIORNI_EN[x.weekday()]} {x.day} {MESI_EN[x.month - 1]} {x.year}"


def corta_en(iso):
    x = date.fromisoformat(iso)
    return f"{x.day} {MESI_EN[x.month - 1]} {x.year}"


def quando_it(v):
    if v["inizio"] == v["fine"]:
        return lunga_it(v["inizio"])
    return f"da {lunga_it(v['inizio'])} a {lunga_it(v['fine'])}"


def quando_en(v):
    if v["inizio"] == v["fine"]:
        return lunga_en(v["inizio"])
    return f"{lunga_en(v['inizio'])} to {lunga_en(v['fine'])}"


def fonte_it(v):
    return "dalla Commissione di garanzia" if v.get("fonte") == "cgsse" else "dal registro"


def stato_it(v):
    if v["stato"] == "revocato":
        return " <strong>Revocato.</strong>"
    if v["stato"] == "rimosso dal registro":
        return " <strong>Non più nel registro (probabilmente revocato).</strong>"
    return ""


def riga_it(v, con_data=True):
    """Uno sciopero in una frase: titolo, luogo, data, orari con le parole della fonte."""
    quando = f" – {quando_it(v)}" if con_data else ""
    return (f'<li data-sid="{escape(v["id"])}"><strong>{escape(v["titolo_it"])}</strong> ({escape(v["dove_it"])}){quando}. '
            f'Orari indicati {fonte_it(v)}: «{escape(v["ore_it"])}».{stato_it(v)}</li>')


def riga_en(v):
    ore = escape(v["ore_en"]) if v["ore_en"] else f'<span lang="it">«{escape(v["ore_it"])}»</span>'
    stato = (" <strong>Called off.</strong>" if v["stato"] == "revocato" else
             " <strong>No longer in the register (likely called off).</strong>" if v["stato"] == "rimosso dal registro" else "")
    return (f'<li data-sid="{escape(v["id"])}"><strong>{escape(v["titolo"])}</strong> ({escape(v["dove"])}). '
            f'Hours in the register: {ore}.{stato}</li>')


def firme(filtra, finestra, filtri):
    return "#".join(AZ.firma(filtra(finestra, f)) for f in filtri.split(","))


def citazioni_it(g, f, con_nome=False):
    """Riquadro con le frasi esatte di una pagina ufficiale (dati/fasce.json), link e data di lettura."""
    a = AZ.PER_SLUG[f["azienda"]]
    righe = "".join(f'<p><strong>{escape(c["etichetta"])}:</strong> {q_it(c)}</p>' for c in f["citazioni"])
    nome = f'<p><a href="/it/{a["pagina"]}/"><strong>{escape(a["nome_pagina"])}</strong></a></p>' if con_nome else ""
    return (f'<div class="cit" data-fasce="{escape(f["azienda"])}|{escape(f["data"])}">{nome}{righe}<p class="small">Fonte: '
            f'<a href="{escape(f["url"])}" rel="noopener">{escape(f["fonte"])}</a>, letta il {corta_it(f["letto_il"])}. '
            "L'azienda può cambiare l'avviso: controlla la pagina ufficiale prima di partire.</p></div>")


def q_it(c):
    """Frase citata; […] dove la frase della fonte è tagliata."""
    return f'{"[…] " if c.get("prima") else ""}<q>{escape(c["testo"])}</q>{" […]" if c.get("dopo") else ""}'


def guardia(firma, finestra, filtri, fino, dentro, cambiato, dopo, classe=""):
    """Blocco legato a uno sciopero: il JS lo nasconde se i dati di quello sciopero sono cambiati o il giorno è passato."""
    return (f'<div{f" class={chr(34)}{classe}{chr(34)}" if classe else ""} data-firma="{escape(firma)}" data-fin="{finestra}" data-fil="{filtri}" data-fino="{fino}">'
            f'<div data-vale>{dentro}</div><p data-cambiato hidden>{cambiato}</p><p data-dopo hidden>{dopo}</p></div>')


def adesioni_it(v):
    a = v.get("adesioni")
    if not a:
        return ""
    return (f'<p data-adesioni="{escape(v["id"])}">Sindacati secondo la Commissione di garanzia (scheda letta il {corta_it(a["letto_il"])}): '
            f'proclamano {escape(a["proclamanti"])}' + (f'; aderiscono {escape(a["aderenti"])}' if a["aderenti"] else "")
            + f'. <a href="{escape(a["url"])}" rel="noopener">Scheda della Commissione di garanzia</a>. '
            "Il registro del Ministero, fermo all'ultima lettura, può riportare un elenco più vecchio.</p>")


def adesioni_en(v):
    a = v.get("adesioni")
    if not a:
        return ""
    return (f'<p data-adesioni="{escape(v["id"])}">Unions according to the Strike Guarantee Commission (read on {corta_en(a["letto_il"])}): '
            f'called by {escape(a["proclamanti"])}' + (f'; joined by {escape(a["aderenti"])}' if a["aderenti"] else "")
            + f'. <a href="{escape(a["url"])}" rel="noopener">Commission record</a>. '
            "The Ministry register, frozen at its last reading, may show an older list.</p>")


def torri_it(g, altri):
    """Scioperi non nazionali dei controllori di volo (ENAV) in un aeroporto del sito: vanno nel titolo del giorno."""
    nomi = [g.APT[s]["nome_it"] for v in altri if "ENAV" in v["categoria"].upper() and 0 < len(v["aeroporti"]) <= 2 for s in v["aeroporti"]]
    return "controllori di volo a " + " e ".join(dict.fromkeys(nomi)) if nomi else ""


def torri_en(g, altri):
    nomi = [g.APT[s]["nome"] for v in altri if "ENAV" in v["categoria"].upper() and 0 < len(v["aeroporti"]) <= 2 for s in v["aeroporti"]]
    return "air traffic control at " + " and ".join(dict.fromkeys(nomi)) if nomi else ""


def treni_solo_di(coinvolte):
    """Aziende dei treni nominate quando Trenitalia non è coinvolta (es. sciopero del solo personale Italo)."""
    return [AZ.PER_SLUG[s] for s in coinvolte if "trains" in AZ.PER_SLUG[s]["settori"] and not AZ.PER_SLUG[s]["regione"]]


def link_azienda(g, a):
    """[(url, testo)] dei link ufficiali dell'azienda, solo quelli presenti e validi in dati/link.json."""
    return [(g.L(x["chiave"]), x["testo"]) for x in a["link"] if g.L(x["chiave"])]


# ---------------------------------------------------------------- blocchi di link per le pagine esistenti
def griglia_aziende_it(g, filtra, solo=None, escludi=None):
    out = []
    for a in AZ.AZIENDE:
        if a["slug"] == escludi or (solo is not None and a["slug"] not in solo):
            continue
        n = len([v for v in filtra("upcoming", "az:" + a["slug"]) if AZ.attivo(v)])
        m = len([v for v in filtra("upcoming", "azgen:" + a["slug"]) if AZ.attivo(v)])
        nota = f"{n} per l'azienda" if n else (f"{m} generali o di settore" if m else "nessuno in elenco")
        out.append(f'<a href="/it/{a["pagina"]}/"{" class=" + chr(34) + "si" + chr(34) if n or m else ""}>Sciopero {escape(a["nome_pagina"])}'
                   f"<small>{nota}</small></a>")
    return '<div class="griglia">' + "".join(out) + "</div>"


def aziende_del_settore(settore):
    return [a["slug"] for a in AZ.AZIENDE if settore in a["settori"]]


def aziende_della_citta(slug_citta):
    """Aziende da collegare dalla pagina di una città: quelle locali e i treni nazionali."""
    return [a["slug"] for a in AZ.AZIENDE if slug_citta in a["citta"] or (not a["regione"] and "trains" in a["settori"])]


def voci_citta_it(slug_citta):
    return "".join(f'<li>Per azienda: <a href="/it/{AZ.PER_SLUG[s]["pagina"]}/">sciopero {escape(AZ.PER_SLUG[s]["nome_pagina"])}: prossime date</a></li>'
                   for s in aziende_della_citta(slug_citta))


def voce_aeroporti_it():
    link = ", ".join(f'<a href="/it/{a["pagina"]}/">sciopero {escape(a["nome_pagina"])}</a>' for a in AZ.AZIENDE if a.get("aeroporti"))
    return f"<li>Scioperi per compagnia: {link}.</li>" if link else ""


def giorni_it(g, mese=None, escludi=None, futuri=True):
    """Griglia dei giorni di sciopero nazionale con una pagina: quelli da oggi in poi, o quelli di un mese (y, m)."""
    out = []
    for iso in AZ.date_nazionali(g.VOCI, g.OGGI):
        x = date.fromisoformat(iso)
        if iso == escludi or (mese and (x.year, x.month) != mese) or (futuri and not mese and iso < g.OGGI.isoformat()):
            continue
        naz = [v for v in AZ.del_giorno(g.VOCI, iso) if AZ.nazionale_passeggeri(v)]
        attivi = [v for v in naz if AZ.attivo(v)]
        nota = "concluso" if iso < g.OGGI.isoformat() else (titolo_breve_it(naz) if attivi else "revocato")
        out.append(f'<a href="/it/{AZ.slug_data_it(iso)}/"{" class=" + chr(34) + "si" + chr(34) if attivi and iso >= g.OGGI.isoformat() else ""}>'
                   f"{GIORNI_IT[x.weekday()].capitalize()} {x.day} {AZ.MESI_IT[x.month - 1]}<small>{escape(nota)}</small></a>")
    return '<div class="griglia">' + "".join(out) + "</div>" if out else ""


def giorni_en(g, rel, mese=None, escludi=None):
    out = []
    for iso in AZ.date_nazionali(g.VOCI, g.OGGI):
        x = date.fromisoformat(iso)
        if iso == escludi or (mese and (x.year, x.month) != mese) or (not mese and iso < g.OGGI.isoformat()):
            continue
        naz = [v for v in AZ.del_giorno(g.VOCI, iso) if AZ.nazionale_passeggeri(v)]
        attivi = [v for v in naz if AZ.attivo(v)]
        nota = "ended" if iso < g.OGGI.isoformat() else (titolo_breve_en(naz) if attivi else "called off")
        out.append(f'<a href="{rel}{AZ.slug_data_en(iso)}/"{" class=" + chr(34) + "si" + chr(34) if attivi and iso >= g.OGGI.isoformat() else ""}>'
                   f"{GIORNI_EN[x.weekday()]} {x.day} {MESI_EN[x.month - 1]}<small>{escape(nota)}</small></a>")
    return '<div class="griglia">' + "".join(out) + "</div>" if out else ""


def _settori_nazionali(naz):
    return [s for s in AZ.PASSEGGERI if any(s in v["settori"] for v in naz)]


def _generale(naz):
    return any("general-strikes" in v["settori"] for v in naz)


def _chi_unico(naz, campo):
    chi = {v[campo] for v in naz}
    return chi.pop() if len(chi) == 1 and "" not in chi else ""


def titolo_breve_it(naz):
    if _generale(naz):
        return "sciopero generale"
    chi = _chi_unico(naz, "chi_it")
    return ", ".join(SETT_TITOLO_IT[s] for s in _settori_nazionali(naz)) + (f" {chi}" if chi else "")


def titolo_breve_en(naz):
    if _generale(naz):
        return "general strike"
    chi = _chi_unico(naz, "chi")
    return (f"{chi} " if chi else "") + ", ".join(SETT_TITOLO_EN[s] for s in _settori_nazionali(naz))


# ---------------------------------------------------------------- pagine in italiano
def costruisci_it(g, k):
    """k: funzioni della versione italiana (pagina, scheda, blocco, filtra, fresco, modulo, AVVISO, AD)."""
    oggi = g.OGGI.isoformat()
    limite = (g.OGGI + timedelta(days=AZ.GIORNI_AVANTI)).isoformat()
    scritto = (f'<p class="small">Risposta scritta il {corta_it(oggi)} sui dati dell\'ultimo controllo; gli elenchi qui sotto '
               "si aggiornano da soli quando il registro cambia.</p>")
    cambiato = (f'<p data-cambiato hidden><strong>I dati sono cambiati dopo il {corta_it(oggi)}</strong>, giorno in cui abbiamo scritto '
                "questa risposta: vale l'elenco qui sotto, che si aggiorna da solo.</p>")
    enac = g.L("enac_voli_garantiti")

    # ---- indice
    k.pagina("it/aziende/", "Scioperi per azienda: Trenitalia, ATM, Trenord, GTT, ATAC e altre",
             "Prossimi scioperi azienda per azienda: Trenitalia, Italo, Trenord, ATM Milano, ATAC Roma, GTT Torino e altre. "
             "Date dal registro ufficiale, orari con le parole della fonte.",
             f"""<section class="hero"><h1>Scioperi per azienda di trasporto</h1>
<p class="lead">Una pagina per azienda: il prossimo sciopero in elenco, gli scioperi generali che la riguardano, le fasce di garanzia quando l'azienda le scrive, il link alla sua pagina ufficiale.</p>{k.fresco()}</section>
{griglia_aziende_it(g, k.filtra)}
{k.AVVISO}
<h2>Giorni di sciopero nazionale</h2>
{giorni_it(g) or '<p>Nessuno sciopero nazionale del trasporto passeggeri in elenco nei prossimi 30 giorni.</p>'}
<div class="testo"><h2>Come leggiamo i dati</h2>
<p>Ogni pagina mostra gli scioperi in cui il registro nomina l'azienda e, separati, gli scioperi generali o di tutto il settore che possono riguardarla. Gli orari sono sempre quelli scritti dalla fonte. Le fasce di garanzia compaiono solo quando le scrive l'azienda sulla sua pagina ufficiale: in quel caso le citiamo tra virgolette, con il link e la data in cui le abbiamo lette.</p></div>
{k.modulo("/")}""", briciole=[("Aziende", "it/aziende/")])

    # ---- una pagina per azienda
    for a in AZ.AZIENDE:
        nome, slug = a["nome"], a["slug"]
        filtri = f"az:{slug},azgen:{slug}"
        nominati = [v for v in k.filtra("upcoming", "az:" + slug) if AZ.attivo(v)]
        larghi = [v for v in k.filtra("upcoming", "azgen:" + slug) if AZ.attivo(v)]
        revocati = [v for v in k.filtra("upcoming", "az:" + slug) if not AZ.attivo(v)]
        fino = f"fino a {lunga_it(limite)}"
        if nominati:
            v0 = nominati[0]
            tipo = "si"
            testa = (f"Sì: oggi, {lunga_it(oggi)}, c'è uno sciopero {escape(nome)} in elenco." if v0["inizio"] <= oggi else
                     f"Sì: il prossimo sciopero {escape(nome)} in elenco è {lunga_it(v0['inizio'])}.")
            corpo_r = f'<p class="big"><strong>{testa}</strong></p><ul>{"".join(riga_it(v) for v in nominati[:5])}</ul>'
            if len(nominati) > 5:
                corpo_r += f"<p>Altri {len(nominati) - 5} nell'elenco qui sotto.</p>"
            if larghi:
                corpo_r += (f"<p>In elenco anche {len(larghi)} "
                            f"{'sciopero generale o di settore che può' if len(larghi) == 1 else 'scioperi generali o di settore che possono'} "
                            f"riguardare {escape(nome)}: il primo è {lunga_it(larghi[0]['inizio'])} (vedi sotto).</p>")
        elif larghi:
            tipo = "generale"
            v0 = larghi[0]
            cosa0 = v0["titolo_it"][0].lower() + v0["titolo_it"][1:]
            corpo_r = (f'<p class="big"><strong>{lunga_it(v0["inizio"]).capitalize()}: {escape(cosa0)} che può riguardare anche {escape(nome)}</strong> '
                       f"({escape(a['servizio'])}).</p><ul>{''.join(riga_it(v) for v in larghi[:3])}</ul>"
                       f"<p>Nessuno sciopero proclamato solo per {escape(nome)} nei prossimi {AZ.GIORNI_AVANTI} giorni ({fino}).</p>")
            if len(larghi) > 3:
                corpo_r += f"<p>Altri {len(larghi) - 3} nell'elenco qui sotto.</p>"
        else:
            tipo = "no"
            corpo_r = (f'<p class="big"><strong>Nessuno sciopero annunciato per {escape(nome)} nei prossimi {AZ.GIORNI_AVANTI} giorni</strong> ({fino}).</p>'
                       f"<p>Nelle fonti che leggiamo non ci sono scioperi proclamati per {escape(nome)} né scioperi generali o di settore che "
                       "la riguardino. Gli scioperi nei trasporti vanno proclamati almeno 10 giorni prima: controlla di nuovo qualche giorno prima di partire.</p>")
        for v in revocati[:3]:
            corpo_r += (f'<p data-sid="{escape(v["id"])}">Lo sciopero {escape(nome)} di {lunga_it(v["inizio"])} '
                        f'{"risulta revocato" if v["stato"] == "revocato" else "non è più nel registro (probabilmente revocato)"}.</p>')
        risposta = (f'<section class="card risposta{" no" if tipo == "no" else ""}" data-risposta="{tipo}" data-azienda="{slug}" '
                    f'data-firma="{escape(firme(k.filtra, "upcoming", filtri))}" data-fin="upcoming" data-fil="{filtri}">'
                    f"<div data-vale>{corpo_r}{scritto}</div>{cambiato}</section>")

        # fasce di garanzia: solo le frasi dell'azienda; altrimenti dove trovarle
        fasce = [f for f in AZ.fasce_azienda(slug, g.OGGI) if not f["data"] or any(
            AZ.attivo(v) for x in filtri.split(",") for v in k.filtra("day:" + f["data"], x))]   # avviso solo se quel giorno c'è ancora uno sciopero
        link = link_azienda(g, a)
        primo = f'<a href="{escape(link[0][0])}" rel="noopener">{escape(link[0][1])}</a>' if link else f"sito ufficiale di {escape(nome)}"
        if fasce:
            stabili = [f for f in fasce if not f["data"]]
            datati = [f for f in fasce if f["data"]]
            h_fasce = ""
            for f in datati:
                h_fasce += guardia(
                    firme(k.filtra, "day:" + f["data"], filtri), "day:" + f["data"], filtri, f["data"],
                    f"<h3>Per lo sciopero di {lunga_it(f['data'])}</h3>" + citazioni_it(g, f)
                    + ("" if stabili else f"<p>Queste fasce valgono solo per lo sciopero indicato: {escape(nome)} le comunica di volta in volta.</p>"),
                    f"Lo sciopero di {lunga_it(f['data'])} è cambiato dopo il {corta_it(oggi)}: l'avviso di {escape(nome)} che riportavamo qui potrebbe non valere più. Controlla la pagina ufficiale: {primo}.",
                    f"Lo sciopero di {lunga_it(f['data'])} è passato: l'avviso di {escape(nome)} per quel giorno non vale più.")
            if stabili:
                h_fasce += (f"<h3>In ogni sciopero</h3><p>Così scrive {escape(nome)} sulla sua pagina ufficiale:</p>" if datati else
                            f"<p>Così scrive {escape(nome)} sulla sua pagina ufficiale:</p>") + "".join(citazioni_it(g, f) for f in stabili)
        elif "flights" in a["settori"]:
            h_fasce = (f"<p>Non abbiamo una pagina ufficiale di {escape(nome)} con i voli garantiti. La regola generale del trasporto aereo: "
                       "i voli in programma dalle 7 alle 10 e dalle 18 alle 21 devono essere effettuati"
                       + (f', insieme ai <a href="{escape(enac)}" rel="noopener">voli garantiti indicati dall\'ENAC</a>' if enac else "")
                       + f". Per il tuo volo vale quello che comunica la compagnia: {primo}.</p>")
        elif "local-transport" in a["settori"]:
            h_fasce = (f"<p>Non riportiamo fasce orarie per {escape(nome)}: non abbiamo trovato una pagina ufficiale dell'azienda che le scriva in modo "
                       f"valido per tutti gli scioperi. {escape(nome)} le comunica prima di ogni sciopero: {primo}. "
                       'Come funzionano in generale: <a href="/it/guida/fasce-di-garanzia/">fasce di garanzia di treni, aerei e mezzi pubblici</a>.</p>')
        else:
            h_fasce = (f"<p>{escape(nome)} pubblica l'elenco dei treni garantiti prima di ogni sciopero: {primo}. "
                       'Come funzionano in generale: <a href="/it/guida/fasce-di-garanzia/">fasce di garanzia di treni, aerei e mezzi pubblici</a>.</p>')

        # storico: scioperi passati in cui il registro nomina l'azienda
        passati = sorted((v for v in g.VOCI if slug in v["az"] and (v["fine"] < oggi or v["stato"] == "concluso")),
                         key=lambda v: v["inizio"], reverse=True)
        if passati:
            righe = "".join(
                f'<tr data-sid="{escape(v["id"])}"><td>{corta_it(v["inizio"])}</td><td>{escape(v["dove_it"])}</td><td>«{escape(v["ore_it"])}»</td><td>{escape(v["sindacati"])}</td>'
                f'<td>{"Revocato" if v["stato"] == "revocato" else "Tolto dal registro prima della data" if v["stato"] == "rimosso dal registro" else "In elenco fino alla data"}</td></tr>'
                for v in passati)
            storico = (f'<div class="storico-box"><table class="storico"><tr><th>Data</th><th>Dove</th><th>Orari indicati dalla fonte</th><th>Sindacati</th><th>Esito</th></tr>{righe}</table></div>'
                       '<p class="small">«In elenco fino alla data»: lo sciopero risultava proclamato e non revocato all\'ultima lettura. '
                       "Non dice quanti lavoratori hanno aderito. Due righe nello stesso giorno sono due proclamazioni di sindacati diversi.</p>")
        else:
            storico = f"<p>Nel nostro archivio non ci sono scioperi passati in cui il registro nomina {escape(nome)}.</p>"

        utili = "".join(f'<li><a href="{escape(u)}" rel="noopener">{escape(t)}</a> (pagina ufficiale)</li>' for u, t in link)
        utili += "".join(f'<li><a href="/it/{c}/">Tutti gli scioperi a {escape(next(x["nome"] for x in g.CITTA_IT if x["slug"] == c))}</a></li>' for c in a["citta"])
        utili += "".join(f'<li><a href="/it/{SETT_PAGINA_IT[s]}/">Tutti gli scioperi: {SETT_TITOLO_IT[s]}</a></li>' for s in a["settori"] if s in SETT_PAGINA_IT)
        if a.get("aeroporti"):
            utili += '<li><a href="/it/aeroporti/">Scioperi per aeroporto</a></li>'
        utili += '<li><a href="/it/oggi/">Scioperi di oggi</a> e <a href="/it/domani/">di domani</a></li>'
        p = f"it/{a['pagina']}/"
        k.pagina(p, f"Sciopero {a['nome_pagina']}: prossime date e orari ufficiali",
                 f"Quando è il prossimo sciopero {a['nome_pagina']}? Date dal registro ufficiale degli scioperi, orari con le parole della fonte, "
                 f"scioperi generali che riguardano {nome} e link alla pagina ufficiale.",
                 f"""<section class="hero"><h1>Sciopero {escape(a["nome_pagina"])}: prossime date</h1>
<p class="lead">Scioperi che riguardano {escape(a["servizio"])}: date e orari dal registro ufficiale, con il link alla pagina ufficiale di {escape(nome)}.</p>{k.fresco()}</section>
{risposta}
{k.AVVISO}
<h2 id="next">Scioperi proclamati per {escape(nome)}</h2>
<p class="small">Scioperi in cui il registro nomina {escape(nome)}.</p>
{k.blocco("upcoming", "az:" + slug)}
<h2>Scioperi generali e di settore che possono riguardare {escape(nome)}</h2>
<p class="small">Scioperi generali, di tutto il settore o della rete nel territorio di {escape(nome)}: non nominano l'azienda, l'adesione dipende dai lavoratori.</p>
{k.blocco("upcoming", "azgen:" + slug)}
{k.AD}
<div class="testo">
<h2>Fasce di garanzia {escape(nome)}</h2>
{h_fasce}
<h2>Dove controllare</h2>
<ul>{utili}</ul>
<h2>Scioperi {escape(nome)} passati</h2>
<p class="small">Dal nostro archivio, che parte dal {ARCHIVIO_DAL}.</p>
{storico}
</div>
<h2>Altre aziende</h2>
{griglia_aziende_it(g, k.filtra, escludi=slug)}
{k.modulo("/")}""", briciole=[("Aziende", "it/aziende/"), (a["nome_pagina"], p)])

    # ---- una pagina per ogni giorno di sciopero nazionale
    for iso in AZ.date_nazionali(g.VOCI, g.OGGI):
        x = date.fromisoformat(iso)
        tutti = AZ.del_giorno(g.VOCI, iso)
        naz = [v for v in tutti if AZ.nazionale_passeggeri(v)]
        attivi = [v for v in naz if AZ.attivo(v)]
        altri = [v for v in tutti if v not in naz and AZ.attivo(v) and any(s in AZ.PASSEGGERI for s in v["settori"])]
        passato = iso < oggi
        generale = _generale(naz)
        cosa = "sciopero generale" if generale else "sciopero nazionale"
        torri = torri_it(g, altri)
        if generale:
            titolo = f"Sciopero generale {corta_it(iso)}: orari di treni, aerei, bus e metro"
            h1 = f"Sciopero generale di {lunga_it(iso)}"
        else:
            cosa_t = f"{titolo_breve_it(naz)} in tutta Italia" + (f", {torri}" if torri else "")
            titolo = f"Sciopero {corta_it(iso)}: {cosa_t}" + ("" if torri else " – orari")
            h1 = f"Sciopero di {lunga_it(iso)}: {cosa_t}"
        if not attivi:
            h1 += " (revocato)"
        elenco = "".join(riga_it(v, con_data=v["inizio"] != v["fine"]) for v in naz)
        if passato:
            tipo = "concluso"
            testa = f"Concluso. {lunga_it(iso).capitalize()} era in elenco {'uno ' + cosa + ' nazionale' if generale else 'uno ' + cosa}." \
                if attivi else f"Lo {cosa} di {lunga_it(iso)} era stato revocato."
        elif not attivi:
            tipo = "revocato"
            testa = f"Lo {cosa} di {lunga_it(iso)} risulta revocato."
        else:
            tipo = "si"
            n = len(attivi)
            quando = "Oggi, " + lunga_it(iso) + "," if iso == oggi else lunga_it(iso).capitalize()
            if generale:
                testa = f"{quando} è in programma uno sciopero generale nazionale{f' ({n} proclamazioni in elenco)' if n > 1 else ''}."
            elif n == 1:
                testa = f"{quando} è in programma uno sciopero nazionale."
            else:
                testa = f"{quando} sono in programma {n} scioperi nazionali."
        corpo_r = f'<p class="big"><strong>{testa}</strong></p><ul>{elenco}</ul>' + "".join(adesioni_it(v) for v in naz)
        if altri and not passato:
            corpo_r += (f"<p>Lo stesso giorno {'è in elenco anche 1 sciopero locale o di aeroporto' if len(altri) == 1 else f'sono in elenco anche {len(altri)} scioperi locali o di aeroporto'}"
                        ": sono nell'elenco qui sotto.</p>")
        vivo = iso >= (g.OGGI - timedelta(days=30)).isoformat()   # i dati incorporati nelle pagine coprono gli ultimi 35 giorni
        if passato:
            risposta = f'<section class="card risposta no" data-risposta="{tipo}" data-giorno-pagina="{iso}">{corpo_r}</section>'
        else:
            dopo = (f'<p data-dopo hidden><strong>Lo sciopero di {lunga_it(iso)} è passato.</strong> Vedi gli '
                    '<a href="/it/oggi/">scioperi di oggi</a> e i <a href="/it/questa-settimana/">prossimi</a>.</p>')
            risposta = (f'<section class="card risposta{" no" if tipo == "revocato" else ""}" data-risposta="{tipo}" data-giorno-pagina="{iso}" '
                        f'data-firma="{escape(firme(k.filtra, "day:" + iso, "all"))}" data-fin="day:{iso}" data-fil="all" data-fino="{iso}">'
                        f"<div data-vale>{corpo_r}{scritto}</div>{cambiato}{dopo}</section>")
        # cosa è garantito: regole scritte dalle fonti per i settori coinvolti
        sett = [s for s in AZ.PASSEGGERI if any(s in v["settori"] for v in (attivi or naz))]
        coinvolte = [s for s in dict.fromkeys(z for v in (attivi or naz) for z in v["az"] + v["az_gen"])]
        garantito = ""
        if "trains" in sett and "trenitalia" in coinvolte:
            tr = [f for f in AZ.FASCE if f["azienda"] == "trenitalia" and not f["data"]]
            garantito += ('<h3>Treni</h3><p>Negli scioperi dei treni restano garantiti alcuni treni a lunga percorrenza e, per i regionali, '
                          "i servizi nelle fasce scritte da ogni azienda.</p>" + "".join(citazioni_it(g, f, con_nome=True) for f in tr)
                          + '<p>Altre aziende: <a href="/it/sciopero-trenord/">Trenord</a>, <a href="/it/sciopero-italo/">Italo</a>.</p>')
        elif "trains" in sett and treni_solo_di(coinvolte):
            soli = treni_solo_di(coinvolte)
            nomi_soli = " e ".join(x["nome"] for x in soli)
            assenti = [x["nome"] for x in AZ.AZIENDE if x.get("rete_rfi") and x not in soli]
            garantito += (f"<h3>Treni</h3><p>Sciopera solo il personale di {escape(nomi_soli)}: {' e '.join(assenti)} non sono nominati. "
                          + " ".join(f'{escape(x["nome"])} pubblica l\'elenco dei treni garantiti prima di ogni sciopero: '
                                     f'<a href="/it/{x["pagina"]}/">sciopero {escape(x["nome_pagina"])}</a>.' for x in soli) + "</p>")
        if "flights" in sett or any("flights" in v["settori"] for v in altri):
            garantito += ("<h3>Aerei</h3><p>I voli in programma dalle 7 alle 10 e dalle 18 alle 21 devono essere effettuati"
                          + (f', insieme ai <a href="{escape(enac)}" rel="noopener">voli garantiti indicati dall\'ENAC</a>' if enac else "")
                          + '. Vedi gli <a href="/it/aeroporti/">scioperi per aeroporto</a>.</p>')
        if "local-transport" in sett:
            garantito += ("<h3>Bus, metro e tram</h3><p>Ogni azienda decide le sue fasce e le comunica prima dello sciopero: "
                          "sotto trovi quelle già pubblicate; per le altre apri la pagina dell'azienda.</p>")
        if "taxis" in sett and not generale:
            garantito += "<h3>Taxi</h3><p>Il registro non indica servizi garantiti per i taxi: vale l'orario scritto sopra.</p>"
        avvisi = AZ.fasce_giorno(iso)
        h_avvisi = ("".join(citazioni_it(g, f, con_nome=True) for f in avvisi) if avvisi else
                    "<p>Per ora non abbiamo letto avvisi ufficiali delle aziende per questo giorno.</p>")
        if coinvolte:
            h_avvisi += ("<p>Aziende che questo sciopero può riguardare, con la loro pagina: "
                         + ", ".join(f'<a href="/it/{AZ.PER_SLUG[s]["pagina"]}/">{escape(AZ.PER_SLUG[s]["nome_pagina"])}</a>' for s in coinvolte) + ".</p>")
        dentro = (f"<h2>Cosa resta garantito</h2>{garantito or '<p>Il registro non indica servizi garantiti per questo sciopero.</p>'}"
                  f"<h2>Cosa hanno comunicato le aziende</h2>{h_avvisi}")
        if not attivi:   # revocato: gli avvisi delle aziende per quel giorno non valgono più
            dettagli = ('<div class="testo"><h2>Cosa resta garantito</h2><p>Lo sciopero risulta revocato: le fasce e gli avvisi delle aziende '
                        "per questo giorno non servono più.</p></div>")
        elif passato:
            dettagli = f'<div class="testo">{dentro}</div>'
        else:
            dettagli = guardia(firme(k.filtra, "day:" + iso, "all"), "day:" + iso, "all", iso, dentro,
                               f"Gli scioperi di {lunga_it(iso)} sono cambiati dopo il {corta_it(oggi)}: le fasce e gli avvisi delle aziende che "
                               "riportavamo qui potrebbero non valere più. Vale l'elenco qui sopra; per le fasce apri la pagina dell'azienda.",
                               f"Lo sciopero di {lunga_it(iso)} è passato.", classe="testo")
        mese = f"it/{x.year}/{AZ.MESI_IT[x.month - 1]}/"
        nome_mese = f"{AZ.MESI_IT[x.month - 1]} {x.year}"
        altri_giorni = giorni_it(g, escludi=iso)
        p = f"it/{AZ.slug_data_it(iso)}/"
        k.pagina(p, titolo,
                 f"Sciopero del {corta_it(iso)}: chi sciopera e con quali orari, dal registro ufficiale. Treni, aerei e mezzi pubblici garantiti "
                 "con le parole delle aziende.",
                 f"""<section class="hero"><h1>{escape(h1)}</h1>
<p class="lead">Chi sciopera, con quali orari e cosa resta garantito: dal registro ufficiale degli scioperi e dalle pagine delle aziende.</p>{k.fresco()}</section>
{risposta}
{k.AVVISO}
<h2 id="next">Tutti gli scioperi del {corta_it(iso)} per chi viaggia</h2>
{k.blocco("day:" + iso, "passengers") if vivo else '<div class="lista">' + ("".join(k.scheda(v) for v in k.filtra("day:" + iso, "passengers")) or "<p>Nessuno sciopero in archivio.</p>") + "</div>"}
{k.AD}
{dettagli}
<h2>Altri giorni di sciopero nazionale</h2>
{altri_giorni or '<p>Nessun altro sciopero nazionale del trasporto passeggeri in elenco nei prossimi 30 giorni.</p>'}
<p>Vedi anche: <a href="/{mese}">tutti gli scioperi di {nome_mese}</a>, <a href="/it/aziende/">scioperi per azienda</a>.</p>
{k.modulo("/")}""", briciole=[(f"Scioperi {nome_mese}", mese), (f"{x.day} {AZ.MESI_IT[x.month - 1]}", p)], con_dati=vivo)


# ---------------------------------------------------------------- pagine in inglese (solo i giorni)
def costruisci_en(g):
    oggi = g.OGGI.isoformat()
    for iso in AZ.date_nazionali(g.VOCI, g.OGGI):
        x = date.fromisoformat(iso)
        rel = "../"
        tutti = AZ.del_giorno(g.VOCI, iso)
        naz = [v for v in tutti if AZ.nazionale_passeggeri(v)]
        attivi = [v for v in naz if AZ.attivo(v)]
        altri = [v for v in tutti if v not in naz and AZ.attivo(v) and any(s in AZ.PASSEGGERI for s in v["settori"])]
        passato = iso < oggi
        generale = _generale(naz)
        cosa = "general strike" if generale else "national strike"
        if generale:
            titolo = f"Italy general strike {corta_en(iso)}: train, flight and bus hours"
            h1 = f"General strike in Italy on {lunga_en(iso)}"
        else:
            torri = torri_en(g, altri)
            cosa_t = f"{titolo_breve_en(naz)} nationwide" + (f", {torri}" if torri else "")
            titolo = f"Italy strike {corta_en(iso)}: {cosa_t}" + ("" if torri else " – hours")
            h1 = f"Strike in Italy on {lunga_en(iso)}: {cosa_t}"
        if not attivi:
            h1 += " (called off)"
        elenco = "".join(riga_en(v) for v in naz)
        if passato:
            tipo = "concluso"
            testa = (f"Ended. A {cosa} was listed in Italy for {lunga_en(iso)}." if attivi else
                     f"The {cosa} listed for {lunga_en(iso)} was called off.")
        elif not attivi:
            tipo = "revocato"
            testa = f"The {cosa} listed for {lunga_en(iso)} has been called off."
        else:
            tipo = "si"
            n = len(attivi)
            testa = (f"Yes: a {cosa} is listed in Italy for {'today, ' if iso == oggi else ''}{lunga_en(iso)}"
                     f"{' (' + str(n) + ' strike calls in the register)' if n > 1 else ''}.")
        corpo_r = f'<p class="big"><strong>{testa}</strong></p><ul>{elenco}</ul>' + "".join(adesioni_en(v) for v in naz)
        if altri and not passato:
            corpo_r += (f"<p>{'One local or airport strike is' if len(altri) == 1 else str(len(altri)) + ' local or airport strikes are'} "
                        "also listed for the same day: see the list below.</p>")
        vivo = iso >= (g.OGGI - timedelta(days=30)).isoformat()
        if passato:
            risposta = f'<section class="card risposta no" data-risposta="{tipo}" data-giorno-pagina="{iso}">{corpo_r}</section>'
        else:
            risposta = (f'<section class="card risposta{" no" if tipo == "revocato" else ""}" data-risposta="{tipo}" data-giorno-pagina="{iso}" '
                        f'data-firma="{escape(firme(g.filtra, "day:" + iso, "all"))}" data-fin="day:{iso}" data-fil="all" data-fino="{iso}">'
                        f'<div data-vale>{corpo_r}<p class="small">Answer written on {corta_en(oggi)} from the latest check; the list below updates by itself when the register changes.</p></div>'
                        f'<p data-cambiato hidden><strong>The register has changed since {corta_en(oggi)}</strong>, when we wrote this answer: rely on the list below, which updates by itself.</p>'
                        f'<p data-dopo hidden><strong>The strike of {lunga_en(iso)} is over.</strong> See <a href="{rel}today/">today\'s strikes</a> and <a href="{rel}this-week/">this week</a>.</p></section>')
        sett = [s for s in AZ.PASSEGGERI if any(s in v["settori"] for v in (attivi or naz))]
        coinvolte = [s for s in dict.fromkeys(z for v in (attivi or naz) for z in v["az"] + v["az_gen"])]
        guide = []
        if "trains" in sett and "trenitalia" in coinvolte:
            guide.append(f'<li><a href="{rel}guides/guaranteed-trains/">Guaranteed trains during strikes</a></li>')
        elif "trains" in sett and treni_solo_di(coinvolte):
            soli = treni_solo_di(coinvolte)
            assenti = [x["nome"] for x in AZ.AZIENDE if x.get("rete_rfi") and x not in soli]
            for z in soli:
                u = link_azienda(g, z)
                dove = f'<a href="{escape(u[0][0])}" rel="noopener">{escape(z["nome"])} website</a>' if u else f'{escape(z["nome"])} website'
                guide.append(f'<li>Only {escape(z["nome"])} staff are on strike: {" and ".join(assenti)} are not named. '
                             f'{escape(z["nome"])} publishes its list of guaranteed trains before each strike: {dove}.</li>')
        if "flights" in sett or any("flights" in v["settori"] for v in altri):
            guide.append(f'<li><a href="{rel}guides/flights-during-strikes/">Flights during strikes: what must operate</a></li>')
        if "local-transport" in sett:
            guide.append(f'<li><a href="{rel}guides/local-transport-strike-hours/">Bus and metro guaranteed hours</a></li>')
        if generale:
            guide.append(f'<li><a href="{rel}guides/general-strikes/">How general strikes affect transport</a></li>')
        avvisi = AZ.fasce_giorno(iso)
        h_avvisi = ""
        if avvisi:
            h_avvisi = ("<h2>What transport operators have announced</h2><p>Quoted from the operators' official pages, in Italian. "
                        "Operators can change these notices: open the official page before you travel.</p>" + "".join(
                            f'<div class="cit" data-fasce="{escape(f["azienda"])}|{escape(f["data"])}"><p><strong>{escape(AZ.PER_SLUG[f["azienda"]]["nome_pagina"])}</strong></p>'
                            + "".join(f'<p lang="it"><strong>{escape(c["etichetta"])}:</strong> {q_it(c)}</p>' for c in f["citazioni"])
                            + f'<p class="small">Source: <a href="{escape(f["url"])}" rel="noopener"><span lang="it">{escape(f["fonte"])}</span></a>, read on {corta_en(f["letto_il"])}.</p></div>'
                            for f in avvisi))
        dentro = ("<h2>What still runs</h2><ul>" + "".join(guide) + "</ul>" if guide else "") + h_avvisi
        if not attivi:
            dettagli = ""
        elif passato or not dentro:
            dettagli = f'<div class="testo">{dentro}</div>'
        else:
            dettagli = guardia(firme(g.filtra, "day:" + iso, "all"), "day:" + iso, "all", iso, dentro,
                               f"The strikes listed for {lunga_en(iso)} have changed since {corta_en(oggi)}: the operator notices we quoted here may no "
                               "longer apply. Rely on the list above and on the operator's official page.",
                               f"The strike of {lunga_en(iso)} is over.", classe="testo")
        altri_giorni = giorni_en(g, rel, escludi=iso)
        p = f"{AZ.slug_data_en(iso)}/"
        mese = g.url_mese(x.year, x.month)
        nome_mese = f"{MESI_EN[x.month - 1]} {x.year}"
        lista = (g.blocco("day:" + iso, "passengers") if vivo else
                 '<div class="lista">' + ("".join(g.scheda(v) for v in g.filtra("day:" + iso, "passengers")) or "<p>No strikes in the archive.</p>") + "</div>")
        g.pagina(p, titolo,
                 f"Strike in Italy on {corta_en(iso)}: who is striking and at what hours, from the official Italian register, in English.",
                 f"""<section class="hero"><h1>{escape(h1)}</h1>
<p class="lead">Who is striking, at what hours and what still runs, from the official Italian strike register.</p>{g.fresco()}</section>
{risposta}
{g.AVVISO}
<h2 id="next">All strikes on {corta_en(iso)} that can affect travellers</h2>
{lista}
{g.box_affiliati()}
{g.AD}
{dettagli}
<h2>Other national strike days</h2>
{altri_giorni or "<p>No other national passenger transport strike is listed in the next 30 days.</p>"}
<p>See also: <a href="{rel}{mese}">all strikes in {nome_mese}</a>.</p>
{g.modulo(rel)}""", briciole=[(nome_mese, mese), (f"{x.day} {MESI_EN[x.month - 1]}", p)], con_dati=vivo)
