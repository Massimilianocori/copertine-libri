"""Sezioni in più delle pagine aeroporto nate il 27/11/2026 (13 aeroporti, italiano e inglese).

I fatti di ogni aeroporto (gestore, dove si trova, handling, collegamenti) stanno in dati/aeroporti.json, con la fonte ufficiale
e la data di lettura; qui c'è solo il montaggio. Gli scioperi vengono dagli stessi dati del resto del sito (VOCI di genera.py):
niente qui decide se uno sciopero riguarda un aeroporto, lo decide leggi() in genera.py come per le pagine già esistenti.
Usato da genera.py (inglese) e genera_it.py (italiano). Le 9 pagine nate prima non hanno una scheda e restano com'erano.
"""
import json
import re
from html import escape
from pathlib import Path

import pagine_aziende as PA

DATI = Path(__file__).resolve().parent / "dati"
_FILE = json.loads((DATI / "aeroporti.json").read_text(encoding="utf-8")) if (DATI / "aeroporti.json").exists() else {}
SCHEDE = _FILE.get("aeroporti", {})
LETTO_IL = _FILE.get("letto_il", "")
COMUNI = _FILE.get("fonti_comuni", {})

CLASSE_IT = {"strategico": "aeroporto strategico", "interesse nazionale": "aeroporto di interesse nazionale"}
CLASSE_EN = {"strategico": "strategic airport", "interesse nazionale": "airport of national interest"}

CSS = """
.apt-scheda{width:100%;text-align:left;margin:0 0 14px}
.apt-scheda th{width:34%;font-weight:600;background:none;vertical-align:top;padding:6px 10px 6px 0}
.apt-scheda td{padding:6px 0;vertical-align:top;overflow-wrap:anywhere}
.apt-fonti{overflow-wrap:anywhere}
"""


def ha_scheda(a):
    return a["slug"] in SCHEDE


def collega(g, testo, rel):
    """[[percorso/|testo]] -> link interno; [[L:chiave|testo]] -> link ufficiale di dati/link.json (solo se valido)."""
    def uno(m):
        dove, scritto = m.group(1), m.group(2)
        if dove.startswith("L:"):
            u = g.L(dove[2:])
            return f'<a href="{escape(u)}" rel="noopener">{escape(scritto)}</a>' if u else escape(scritto)
        return f'<a href="{rel}{dove}">{escape(scritto)}</a>'
    parti = re.split(r"(\[\[[^\]|]+\|[^\]]+\]\])", testo)
    return "".join(re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", uno, p) if p.startswith("[[") else escape(p, quote=False) for p in parti)


def specifici(g, a):
    """Scioperi dei dati che riguardano questo aeroporto ma non tutti gli aeroporti del sito (nominato dal registro, oppure
    stessa provincia o regione)."""
    return [v for v in g.VOCI if a["slug"] in v["aeroporti"] and len(v["aeroporti"]) < len(g.AEROPORTI)]


def passati(g, a):
    oggi = g.OGGI.isoformat()
    return sorted((v for v in specifici(g, a) if v["fine"] < oggi), key=lambda v: v["inizio"], reverse=True)


def _province(a):
    return [p for p in [a.get("provincia", "")] + a.get("province", []) if p]


def _fonti(g, s, lingua):
    nome = "nome_it" if lingua == "it" else "nome_en"
    return ", ".join(f'<a href="{escape(f["url"])}" rel="noopener">{escape(f[nome])}</a>' for f in s["fonti"])


# ---------------------------------------------------------------- italiano
def sezioni_it(g, a):
    s = SCHEDE[a["slug"]]
    nome = a["nome_it"]
    u = g.L(a["link"]) if a.get("link") else None
    sito = f'<a href="{escape(u)}" rel="noopener">{escape(u.split("//")[1].split("/")[0])}</a>' if u else "non riportato: non abbiamo potuto leggerlo dal server"
    classi = COMUNI.get("enac_classi", {}).get("url", "")
    tabella = (f'<table class="apt-scheda"><tr><th scope="row">Nome ufficiale</th><td>{escape(s["uff_it"])}</td></tr>'
               f'<tr><th scope="row">Codice IATA</th><td>{a["iata"]}</td></tr>'
               f'<tr><th scope="row">Dove si trova</th><td>{escape(s["luogo_it"])}</td></tr>'
               f'<tr><th scope="row">Gestore</th><td>{escape(s["gestore"])}</td></tr>'
               f'<tr><th scope="row">Per l\'ENAC</th><td><a href="{escape(classi)}" rel="noopener">{CLASSE_IT[s["classe"]]}</a></td></tr>'
               f'<tr><th scope="row">Sito ufficiale</th><td>{sito}</td></tr></table>')
    prov = _province(a)
    parole = ", ".join(f"«{p}»" for p in a["parole"])
    come = (f"In questa pagina entrano gli scioperi nazionali del trasporto aereo e gli scioperi generali che non escludono gli aerei, "
            f"gli scioperi del trasporto aereo registrati per tutta la regione {escape(a['regione'])}"
            + (f", quelli registrati per la provincia di {escape(prov[0])}" if a.get("provincia") else "")
            + f" e quelli in cui la fonte scrive {parole} nel nome dello sciopero. Per gli scioperi che arrivano dal calendario della "
              f"Commissione di garanzia vale il luogo indicato dalla Commissione: se nomina un solo scalo, lo sciopero compare solo lì.")
    nota = f" {collega(g, s['nota_it'], '/')}" if s.get("nota_it") else ""
    pas = passati(g, a)
    if pas:
        storico = (f"<p>Scioperi già passati che riguardavano {escape(nome)} in particolare, dal più recente. Il nostro archivio parte dal "
                   f"10 ottobre 2026.</p><ul class=\"apt-storico\">{''.join(PA.riga_it(v) for v in pas)}</ul>")
    else:
        storico = (f"<p>Dal 10 ottobre 2026, quando parte il nostro archivio, nessuno sciopero già passato ha riguardato {escape(nome)} in particolare.</p>")
    isole = ("<li>Questo aeroporto è su un'isola: fuori dalle due fasce le compagnie devono garantire anche un collegamento al giorno da e per le isole, "
             "se lo hanno in orario.</li>" if s["isola"] else "")
    regole = (f'<li>Fuori dalle fasce 7-10 e 18-21 la direzione aeroportuale autorizza il 20% dei voli in orario e i servizi dell\'aeroporto '
              f'(arrivi, partenze, passeggeri e bagagli) devono funzionare almeno al 20%: lo prevedono le '
              f'<a href="{escape(COMUNI.get("enac_prestazioni", {}).get("url", ""))}" rel="noopener">prestazioni minime pubblicate dall\'ENAC</a>.</li>{isole}')
    sopra = f"""<h2>L'aeroporto di {escape(nome)} in breve</h2>
{tabella}
<div class="testo"><p>{collega(g, s["testo_it"][0], "/")}</p></div>
<h2>Arrivare all'aeroporto quando c'è sciopero</h2>
<div class="testo"><p>{collega(g, s["testo_it"][1], "/")}</p></div>"""
    sotto = f"""<h2>Quali scioperi mostra questa pagina</h2>
<div class="testo"><p>{come}{nota}</p></div>
<h2>Scioperi passati a {escape(nome)}</h2>
<div class="testo">{storico}</div>
<p class="small apt-fonti">Fonti sull'aeroporto: {_fonti(g, s, "it")}. Lette il {PA.corta_it(LETTO_IL)}.</p>"""
    return sopra, regole, sotto


def griglia_it(g, a=None):
    return '<div class="griglia">' + "".join(
        f'<a href="/it/aeroporti/{x["slug_it"]}/">{escape(x["nome_it"])}<small>{x["iata"]}</small></a>' for x in g.AEROPORTI if not a or x["slug"] != a["slug"]) + "</div>"


# ---------------------------------------------------------------- inglese
def sezioni_en(g, a, rel):
    s = SCHEDE[a["slug"]]
    nome = a["nome"]
    u = g.L(a["link"]) if a.get("link") else None
    sito = f'<a href="{escape(u)}" rel="noopener">{escape(u.split("//")[1].split("/")[0])}</a>' if u else "not listed: we could not read it from our server"
    classi = COMUNI.get("enac_classi", {}).get("url", "")
    tabella = (f'<table class="apt-scheda"><tr><th scope="row">Official name</th><td>{escape(s["uff_en"])}</td></tr>'
               f'<tr><th scope="row">IATA code</th><td>{a["iata"]}</td></tr>'
               f'<tr><th scope="row">Location</th><td>{escape(s["luogo_en"])}</td></tr>'
               f'<tr><th scope="row">Operator</th><td>{escape(s.get("gestore_en", s["gestore"]))}</td></tr>'
               f'<tr><th scope="row">ENAC status</th><td><a href="{escape(classi)}" rel="noopener">{CLASSE_EN[s["classe"]]}</a></td></tr>'
               f'<tr><th scope="row">Official website</th><td>{sito}</td></tr></table>')
    prov = _province(a)
    reg = g.REG_EN.get(a["regione"], a["regione"])
    parole = ", ".join(f"«{p}»" for p in a["parole"])
    come = (f"This page lists national air transport strikes and general strikes that do not exclude flights, air transport strikes filed "
            f"for the whole {escape(reg)} region"
            + (f", those filed for the province of {escape(g.PROV_EN.get(prov[0], prov[0]))}" if a.get("provincia") else "")
            + f" and those where the source writes {parole} in the name of the strike. For strikes taken from the Commissione di garanzia "
              f"calendar we follow the place it gives: if it names a single airport, the strike is shown only there.")
    nota = f" {collega(g, s['nota_en'], rel)}" if s.get("nota_en") else ""
    pas = passati(g, a)
    if pas:
        storico = (f"<p>Past strikes that concerned {escape(nome)} specifically, most recent first. Our archive starts on 10 October 2026.</p>"
                   f"<ul class=\"apt-storico\">{''.join(_riga_en(v) for v in pas)}</ul>")
    else:
        storico = (f"<p>Since 10 October 2026, when our archive starts, no past strike has concerned {escape(nome)} specifically.</p>")
    isole = ("<li>This airport is on an island: outside the two windows airlines must also operate one daily connection to and from the islands, "
             "if they have it in their schedule.</li>" if s["isola"] else "")
    regole = (f'<li>Outside the 07:00–10:00 and 18:00–21:00 windows the airport directorate authorises 20% of scheduled flights, and airport '
              f'services (arrivals, departures, passengers and baggage) must work at no less than 20%: see the '
              f'<a href="{escape(COMUNI.get("enac_prestazioni", {}).get("url", ""))}" rel="noopener">minimum services published by ENAC</a> (in Italian).</li>{isole}')
    sopra = f"""<h2>{escape(nome)} airport at a glance</h2>
{tabella}
<div class="testo"><p>{collega(g, s["testo_en"][0], rel)}</p></div>
<h2>Getting to the airport during a strike</h2>
<div class="testo"><p>{collega(g, s["testo_en"][1], rel)}</p></div>"""
    sotto = f"""<h2>Which strikes this page shows</h2>
<div class="testo"><p>{come}{nota}</p></div>
<h2>Past strikes at {escape(nome)}</h2>
<div class="testo">{storico}</div>
<p class="small apt-fonti">Airport facts from: {_fonti(g, s, "en")}. Read on {PA.corta_en(LETTO_IL)}.</p>"""
    return sopra, regole, sotto


def _riga_en(v):
    """Come PA.riga_en, con la data: nello storico serve sapere quando."""
    return PA.riga_en(v).replace("</strong> (", f"</strong> – {PA.quando_en(v)} (", 1)
