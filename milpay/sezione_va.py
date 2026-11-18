"""Sezione "VA disability" di Military Pay Chart: indennità di invalidità dei veterani (Department of Veterans Affairs).
Chiamata da genera.py (genera(G), dove G è il modulo genera).

Dati: dati/va.json (scritto da raccolta/va.py dai file grezzi in dati/grezzi/). Prima di scrivere qualsiasi pagina `controlla()` rilegge i file grezzi
(impronte, tabelle di va.gov = avvisi del VA nel Federal Register + 38 U.S.C. 1115(2), Table I del 38 CFR 4.25) e lo stato delle tabelle 2027.
Pagine:
  /va-disability-rates/                tabelle ufficiali in vigore (dal 1/12/2025, "2026"), confronto con il 2025, come si leggono, calcolatore
  /va-disability-rates/<n>-percent/    una per grado (10 … 100 %), solo se la ricerca misurata supera SOGLIA (dati/domanda_va.json)
  /va-disability-calculator/           grado (o più gradi da combinare con la Table I) + familiari -> importo mensile
  /va-disability-rates/2027/           aumento del 3,6 % dal 1/12/2026: che cosa è ufficiale e che cosa non è ancora uscito

REGOLA 2027: finché va.gov (o l'avviso del VA nel Federal Register) non pubblica gli importi dal 1/12/2026 il sito NON mostra importi 2027 calcolati.
La legge dà la percentuale e la regola dei familiari (38 U.S.C. 1115(2)), ma nessuna fonte ufficiale letta dice come si arrotonda al centesimo, e la
prova fatta sugli avvisi 2024-2026 non torna su tutti gli importi (vedi NOTE.md). Quando le tabelle escono `controlla()` ferma la generazione:
aggiornare raccolta/va.py (ANNI, FILE), raccolta/fonti.py (frasi di va_rates) e i testi qui sotto.
FAQ solo da ricerche misurate; JSON-LD = FAQ visibili (faq_blocco di genera.py). Nessun consiglio: informazione, non consulenza sui benefici.
"""
import hashlib
import importlib.util
import json
from datetime import date

SOGLIA = 300  # ricerche al mese misurate per avere una pagina di grado
ANNO, PRIMA = "2026", "2025"  # tabelle in vigore e tabelle precedenti (le chiama così va.gov)
MAX_FIGLI = 12

# pagine di grado: grado -> ricerca misurata (controlla() verifica volume >= SOGLIA)
GRADO_RICERCA = {100: "100 va disability pay", 90: "90 va disability pay", 80: "80 va disability", 70: "70 percent va disability", 60: "60 va disability pay",
                 50: "50 percent va disability", 40: "40 va disability pay", 30: "30 percent va disability", 20: "20 va disability pay", 10: "10 va disability"}
# etichette nostre per le 12 righe (l'ordine e il significato sono quelli della pagina va.gov)
STATO_NOME = {"alone": "Veteran alone (no dependents)", "spouse": "With spouse", "spouse_p1": "With spouse and 1 parent", "spouse_p2": "With spouse and 2 parents",
              "p1": "With 1 parent", "p2": "With 2 parents", "child": "With 1 child", "child_spouse": "With spouse and 1 child",
              "child_spouse_p1": "With spouse, 1 child and 1 parent", "child_spouse_p2": "With spouse, 1 child and 2 parents",
              "child_p1": "With 1 child and 1 parent", "child_p2": "With 1 child and 2 parents"}
AGG_NOME = {"child_u18": "Each additional child under 18", "child_school": "Each additional child over 18 in a qualifying school program",
            "spouse_aa": "Spouse receiving Aid and Attendance"}
SENZA_FIGLI = ["alone", "spouse", "spouse_p1", "spouse_p2", "p1", "p2"]
CON_FIGLI = ["child", "child_spouse", "child_spouse_p1", "child_spouse_p2", "child_p1", "child_p2"]

DISCLAIMER_VA = ("<strong>Independent site, not affiliated with the Department of Veterans Affairs, the Department of Defense or any other federal agency.</strong> "
                 "We show VA’s disability compensation rates exactly as published, plus our own arithmetic on them. This is general information, not benefits advice, "
                 "legal advice or financial advice. Only VA decides your rating, your dependents and what you are paid: your VA decision letter and VA.gov are the authority on your own payment.")
NOTA_FONTI = ('<p class="small">Rates are copied from the VA pages and Federal Register notices listed above; yearly amounts (× 12), differences, totals and calculator results are our arithmetic on those figures. '
              'See <a href="/how-we-check/#va-checks">how we check</a>.</p>')

G = None
VA = None


# ---------------------------------------------------------------- utilità
def usd(c):
    """Centesimi -> '$1,132.90'."""
    return f"${c // 100:,}.{c % 100:02d}"


def usd0(c):
    return f"${c // 100:,}" if c % 100 == 0 else usd(c)


def h(x):
    return G.h(x)


def giorno(iso):
    return G.data_lunga(iso)


def T(anno=None):
    return VA["anni"][anno or ANNO]


def slug_grado(g):
    return f"va-disability-rates/{g}-percent/"


def gradi_pagina():
    return [g for g in VA["gradi"] if g in GRADO_RICERCA]


# ---------------------------------------------------------------- calcolo (copia Python di stile.APP_JS vaCombina e vaPaga)
def dati_calcolo():
    t = T()
    return {"anno": ANNO, "base": t["base"], "righe": t["righe"], "agg": t["aggiunte"], "T": VA["combinati"]["righe"],
            "pagine": {str(g): slug_grado(g) for g in gradi_pagina()}}


def combina(D, lista):
    """Gradi singoli -> valore combinato con la Table I del 38 CFR 4.25 (sola lettura della tabella) e grado finale arrotondato alla decina (i 5 in su)."""
    if not isinstance(lista, list) or not lista or len(lista) > 20:
        return {"errore": "lista"}
    for x in lista:
        if not isinstance(x, int) or isinstance(x, bool) or x < 10 or x > 100 or x % 10:
            return {"errore": "grado"}
    ord_ = sorted(lista, reverse=True)
    v, passi = ord_[0], []
    for b in ord_[1:]:
        if v >= 95:
            break
        c = 19 if (v == 10 and b == 10) else D["T"][str(v)][b // 10 - 1]
        passi.append([v, b, c])
        v = c
    return {"ordinati": ord_, "passi": passi, "valore": v, "finale": min(100, (v + 5) // 10 * 10)}


def chiave_stato(coniuge, genitori, figlio):
    if figlio:
        return ("child_spouse" if coniuge else "child") + (f"_p{genitori}" if genitori else "")
    if coniuge:
        return "spouse" + (f"_p{genitori}" if genitori else "")
    return f"p{genitori}" if genitori else "alone"


def paga(D, g, coniuge, aa, genitori, u18, scuola):
    """Metodo scritto nella pagina va.gov: riga della tabella base + importi aggiunti. Tutto in centesimi interi."""
    ok = lambda x, lo, hi: isinstance(x, int) and not isinstance(x, bool) and lo <= x <= hi  # noqa: E731
    if not ok(g, 10, 100) or g % 10:
        return {"errore": "grado"}
    if not (ok(coniuge, 0, 1) and ok(aa, 0, 1) and ok(genitori, 0, 2) and ok(u18, 0, MAX_FIGLI) and ok(scuola, 0, MAX_FIGLI)):
        return {"errore": "dati"}
    if g < 30:
        return {"cent": D["base"][str(g)], "anno": D["base"][str(g)] * 12, "chiave": "alone", "base": D["base"][str(g)], "extra": [], "senza_familiari": 1 if (coniuge or genitori or u18 or scuola) else 0}
    if scuola and not u18:
        return {"errore": "scuola"}
    k = chiave_stato(coniuge, genitori, 1 if u18 else 0)
    base = D["righe"][k][str(g)]
    extra = []
    if u18 > 1:
        extra.append(["child_u18", u18 - 1, D["agg"]["child_u18"][str(g)]])
    if scuola:
        extra.append(["child_school", scuola, D["agg"]["child_school"][str(g)]])
    if coniuge and aa:
        extra.append(["spouse_aa", 1, D["agg"]["spouse_aa"][str(g)]])
    tot = base + sum(n * c for _, n, c in extra)
    return {"cent": tot, "anno": tot * 12, "chiave": k, "base": base, "extra": extra, "senza_familiari": 0}


# ---------------------------------------------------------------- controlli (prima di scrivere le pagine)
def _modulo_raccolta():
    spec = importlib.util.spec_from_file_location("raccolta_va", G.RADICE / "raccolta" / "va.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def stato_2027():
    """Che cosa dicono oggi le fonti sulle tabelle dal 1/12/2026. Ferma la generazione appena una di loro cambia (allora il sito va aggiornato a mano)."""
    E = G.ESITI
    va, leggi, fr = E.get("va_rates", {}), E.get("plaw119", {}), E.get("fr_va_search", {})
    if va.get("http") != 200 or not all(va.get("trovate", {}).values()):
        raise SystemExit("va.gov: la pagina delle tabelle non dice più «Effective December 1, 2025» o è cambiata: probabilmente sono uscite le tabelle 2027. "
                         "Aggiornare raccolta/va.py, raccolta/fonti.py e sezione_va.py (NOTE.md, sezione VA)")
    if "va_cola_2026" not in leggi:
        raise SystemExit("elenco delle leggi (plaw119) senza il controllo va_cola_2026: rilanciare raccolta/fonti.py --solo=plaw119")
    if leggi["va_cola_2026"]:
        raise SystemExit(f"La legge sull'aumento 2026 dell'indennità dei veterani è tra le leggi pubblicate ({leggi['va_cola_2026']}): riscrivere /va-disability-rates/2027/ (NOTE.md, sezione VA)")
    ultimo = (fr.get("avvisi") or [{}])[0]
    if fr.get("http") != 200 or ultimo.get("numero") != VA["avvisi_fr"][0]["numero"] or ultimo.get("numero") != "2026-02997":
        raise SystemExit(f"Federal Register: l'ultimo avviso del VA sugli importi non è più il 2026-02997 ({ultimo}): sono usciti gli importi nuovi? (NOTE.md, sezione VA)")
    return {"va_letto": va["letto_il"], "va_aggiornata": T()["pagina_aggiornata_il"], "leggi_letto": leggi["letto_il"], "ultima_legge": leggi["ultima_legge"],
            "fr_letto": fr["letto_il"], "avvisi": VA["avvisi_fr"][:3], "oggi": max(va["letto_il"], leggi["letto_il"], fr["letto_il"])}


def controlla():
    err = []
    R = _modulo_raccolta()
    reg = G._F.get("grezzi", {})
    for nome, url in R.FILE.items():
        f = G.DATI / "grezzi" / nome
        if not f.exists():
            err.append(f"manca il file grezzo {nome}")
            continue
        if reg.get(nome, {}).get("sha256") != hashlib.sha256(f.read_bytes()).hexdigest():
            err.append(f"{nome}: impronta diversa da fonti.json")
        if reg.get(nome, {}).get("url") != url:
            err.append(f"{nome}: URL diverso da fonti.json")
    if err:
        raise SystemExit("ERRORI NEI DATI VA:\n - " + "\n - ".join(err))
    riletto, n = R.costruisci()  # rilegge i file grezzi e rifà tutti i confronti (va.gov = avviso + 1115(2); Table I = va.gov = formula)
    riletto["letto_il"] = VA["letto_il"]
    if riletto != VA:
        err.append("dati/va.json diverso dai file grezzi riletti (rilanciare raccolta/va.py)")
    for fid in ("va_rates", "va_rates_2025", "va_fr_2026", "va_fr_2025", "ssa_cola_2027", "hr8552", "plaw119_42", "usc1115", "cfr4_25", "cfr4_26", "va_about", "fr_va_search", "plaw119"):
        es = G.ESITI.get(fid, {})
        if es.get("http") != 200 or not all(es.get("trovate", {}).values()):
            err.append(f"fonte {fid}: HTTP {es.get('http')} o frase mancante")
    for anno in (ANNO, PRIMA):
        t = T(anno)
        if sorted(t["base"], key=int) != [str(g) for g in VA["gradi"]] or any(t["base"][str(a)] >= t["base"][str(b)] for a, b in zip(VA["gradi"], VA["gradi"][1:])):
            err.append(f"{anno}: importi base non crescenti")
        for k in VA["stati"]:
            if any(t["righe"][k][str(g)] < t["base"][str(g)] for g in VA["gradi"][2:]):
                err.append(f"{anno}: riga {k} sotto l'importo del veterano solo")
    for g in VA["gradi"]:
        for k in ["base"]:
            if not T(ANNO)[k][str(g)] > T(PRIMA)[k][str(g)]:
                err.append(f"{g}%: il {ANNO} non supera il {PRIMA}")
    for g, ric in GRADO_RICERCA.items():
        if G.volume(ric) < SOGLIA:
            err.append(f"pagina del {g}%: ricerca «{ric}» sotto {SOGLIA} al mese ({G.volume(ric)})")
    # esempi scritti nella pagina va.gov (letti a mano il 15/11/2026): devono uscire uguali dal nostro calcolo
    D = dati_calcolo()
    if paga(D, 30, 1, 0, 0, 0, 0)["cent"] != 61747 or paga(D, 70, 1, 1, 0, 3, 0)["cent"] != 207445 + 2 * 7600 + 14100:
        err.append("gli esempi della pagina va.gov non tornano con il calcolo")
    c = combina(D, [60, 40, 20])
    if (c["valore"], c["finale"]) != (81, 80) or combina(D, [50, 30])["valore"] != 65 or combina(D, [50, 30])["finale"] != 70 or combina(D, [40, 20])["valore"] != 52 or combina(D, [10, 10])["valore"] != 19:
        err.append("gli esempi del 38 CFR 4.25 non tornano con il calcolo")
    if err:
        raise SystemExit("ERRORI NEI DATI VA:\n - " + "\n - ".join(err))
    return {"celle": n, "table_i": len(VA["combinati"]["righe"]) * 9, "stato_2027": stato_2027()}


# ---------------------------------------------------------------- pezzi comuni
def avviso_2027(S, rim, corto=True):
    t = (f'<div class="nota info">{G.ico("info")}<p><strong>2027 rates: 3.6% announced, VA table not published yet.</strong> '
         f'Social Security’s cost-of-living increase for December 2026 is 3.6%,{rim.ref("ssa_cola_2027")} and VA says it is “required by law to match the percentage of cost-of-living adjustments made to Social Security benefits”.{rim.ref("va_rates")} '
         f'On {giorno(S["va_letto"])} VA’s rate page still showed the tables effective December 1, 2025, the ones on this page.{rim.ref("va_rates")} '
         + ('<a href="/va-disability-rates/2027/">What is official so far for 2027 →</a>' if corto else "") + "</p></div>")
    return t


def tabella_base(rim, evidenzia=None):
    a, p = T(ANNO), T(PRIMA)
    righe = ""
    for g in VA["gradi"]:
        x, y = a["base"][str(g)], p["base"][str(g)]
        nome = f'<a href="/{slug_grado(g)}">{g}%</a>' if g in GRADO_RICERCA else f"{g}%"
        righe += (f'<tr{" class=\"qui\"" if evidenzia == g else ""}><th scope="row">{nome}</th><td class="n">{usd(x)}</td><td class="n">{usd(x * 12)}</td>'
                  f'<td class="n">{usd(y)}</td><td class="n">+{usd(x - y)}</td></tr>')
    return (f'<div class="tab"><table class="dati"><caption>Monthly VA disability compensation for a Veteran with no dependents, U.S. dollars. '
            f'Effective {giorno(a["decorrenza"])} (VA’s “2026” rates) and {giorno(p["decorrenza"])} (“2025”). Sources: VA{rim.ref("va_rates,va_rates_2025,va_fr_2026")}. Yearly amount and difference: our arithmetic.</caption>'
            '<thead><tr><th scope="col">Disability rating</th><th scope="col" class="n">2026, per month</th><th scope="col" class="n">2026, per year (× 12)</th>'
            '<th scope="col" class="n">2025, per month</th><th scope="col" class="n">Change</th></tr></thead>'
            f'<tbody>{righe}</tbody></table></div>')


def tabella_stati(chiavi, rim, anno=None, titolo=""):
    a = T(anno)
    gg = VA["gradi"][2:]
    testa = '<th scope="col">Dependent status</th>' + "".join(f'<th scope="col" class="n">{g}%</th>' for g in gg)
    righe = "".join(f'<tr><th scope="row">{h(STATO_NOME[k])}</th>' + "".join(f'<td class="n">{usd(a["righe"][k][str(g)])}</td>' for g in gg) + "</tr>" for k in chiavi)
    fonte = "va_rates,va_fr_2026" if (anno or ANNO) == ANNO else "va_rates_2025,va_fr_2025"
    return (f'<div class="tab"><table class="dati va"><caption>{titolo} Basic monthly rates in U.S. dollars, effective {giorno(a["decorrenza"])}. Source: VA{rim.ref(fonte)}.</caption>'
            f'<thead><tr>{testa}</tr></thead><tbody>{righe}</tbody></table></div>')


def tabella_aggiunte(rim, anno=None):
    a = T(anno)
    gg = VA["gradi"][2:]
    testa = '<th scope="col">Added amount</th>' + "".join(f'<th scope="col" class="n">{g}%</th>' for g in gg)
    righe = "".join(f'<tr><th scope="row">{h(AGG_NOME[k])}</th>' + "".join(f'<td class="n">{usd(a["aggiunte"][k][str(g)])}</td>' for g in gg) + "</tr>" for k in AGG_NOME)
    fonte = "va_rates,va_fr_2026,usc1115" if (anno or ANNO) == ANNO else "va_rates_2025,va_fr_2025"
    return (f'<div class="tab"><table class="dati va"><caption>Added monthly amounts in U.S. dollars, effective {giorno(a["decorrenza"])}: add them to the basic rate. Source: VA{rim.ref(fonte)}.</caption>'
            f'<thead><tr>{testa}</tr></thead><tbody>{righe}</tbody></table></div>')


def griglia_gradi(escludi=None):
    a = T()
    return ('<ul class="griglia">' + "".join(f'<li><a href="/{slug_grado(g)}"><b>{g}%</b><small>{usd(a["base"][str(g)])}</small></a></li>' for g in gradi_pagina() if g != escludi) + "</ul>")


def calcolatore_va(g=70, coniuge=1, aa=0, genitori=0, u18=1, scuola=0, titolo="VA disability calculator, 2026 rates", id_h="va-h"):
    D = dati_calcolo()
    r = paga(D, g, coniuge, aa, genitori, u18, scuola)
    op_g = "".join(f'<option value="{x}"{" selected" if x == g else ""}>{x}%</option>' for x in VA["gradi"])
    sp = 2 if (coniuge and aa) else coniuge
    op_s = "".join(f'<option value="{v}"{" selected" if v == sp else ""}>{t}</option>' for v, t in ((0, "No spouse"), (1, "Spouse"), (2, "Spouse receiving Aid and Attendance")))
    op_p = "".join(f'<option value="{v}"{" selected" if v == genitori else ""}>{t}</option>' for v, t in ((0, "None"), (1, "1 parent"), (2, "2 parents")))
    statico = (f'<div class="tot"><div class="main"><span>Monthly payment, 2026 rates</span><b>{usd(r["cent"])}</b></div><div><span>Per year (× 12)</span><b>{usd(r["anno"])}</b></div></div>')
    return f"""<section class="card calc" data-va aria-labelledby="{id_h}">
<div class="calc-h"><h2 id="{id_h}">{G.ico("calc")}{h(titolo)}</h2></div>
<div class="calc-g">
<form class="calc-in" onsubmit="return false">
<label>Combined disability rating<select name="g">{op_g}</select></label>
<label>Or enter each rating to combine them (optional)<input type="text" name="lista" inputmode="numeric" autocomplete="off" placeholder="For example 50, 30, 10" maxlength="80"></label>
<label>Spouse<select name="s">{op_s}</select></label>
<label>Dependent parents<select name="p">{op_p}</select></label>
<div class="due"><label>Children under 18<input type="number" name="u" value="{u18}" min="0" max="{MAX_FIGLI}" step="1" inputmode="numeric"></label>
<label>Children 18+ in school<input type="number" name="c" value="{scuola}" min="0" max="{MAX_FIGLI}" step="1" inputmode="numeric"></label></div>
<p class="small">Dependents are the ones VA has added to your award. A child over 18 counts only in a qualifying school program, as in VA’s table.</p>
</form>
<div class="calc-out" data-out aria-live="polite">{statico}</div>
</div>
<p class="calc-f"><strong>Method:</strong> the basic rate for your rating and dependent status in VA’s table, plus VA’s added amounts. Rates effective {giorno(T()["decorrenza"])}; the 2027 table is not published yet.
Ratings are combined with Table I of 38 CFR 4.25, without the bilateral factor. It runs in your browser: nothing you enter is sent to us.</p>
<script type="application/json" id="dati-va">{json.dumps(D, separators=(",", ":"))}</script>
</section>"""


def come_si_legge(rim):
    D = dati_calcolo()
    e1, e2 = paga(D, 30, 1, 0, 0, 0, 0), paga(D, 70, 1, 1, 0, 3, 0)
    a = T()["aggiunte"]
    return ('<h2 id="how-to-read">How to read the tables</h2><div class="testo">' + rim.t(
        '<p>VA: “We base your monthly payment amount on your disability rating and details about your dependent family members.”[[va_rates]] The steps below are VA’s own.</p>'
        '<ol><li><strong>10% or 20%:</strong> one amount for everyone. “If you have a 10% to 20% disability rating, you won’t receive a higher rate even if you have a dependent spouse, child, or parent.”[[va_rates]]</li>'
        '<li><strong>30% to 100%, basic rate:</strong> “Find the dependent status in the left column that best describes you. Then look for your disability rating in the top row. '
        'Your basic monthly rate is where your dependent status and disability rating meet.”[[va_rates]]</li>'
        '<li><strong>Added amounts:</strong> “If your spouse receives Aid and Attendance benefits or you have more than 1 child, you may qualify for additional monthly payment amounts as listed in the Added amounts table.”[[va_rates]] '
        'The basic rate “with 1 child” already pays for one child, so the added amount counts from the second child.</li></ol>'
        f'<p><strong>Two examples with the 2026 rates (VA gives the same ones on its page):</strong> 30% with a spouse and no children or parents: {usd(e1["cent"])} a month. '
        f'70% with a spouse and three children under 18, spouse receiving Aid and Attendance: {usd(e2["base"])} + 2 × {usd0(a["child_u18"]["70"])} + {usd0(a["spouse_aa"]["70"])} = {usd(e2["cent"])} a month.[[va_rates]]</p>'
        '<p>The whole-dollar steps in the 30% to 90% columns come from the law: for a partial rating each dependent amount is the same share of the 100% amount as the rating, and the law adds: '
        '“The amounts payable under this paragraph, if not a multiple of $1, shall be rounded down to the nearest dollar.”[[usc1115]]</p>') + "</div>")


def non_coperto(rim):
    return ('<h2 id="not-covered">What these tables do not cover</h2><div class="testo">' + rim.t(
        '<p>These are the basic compensation rates for Veterans by rating and dependents. VA publishes separate tables for special monthly compensation, special benefit allowances and birth defect compensation; '
        'they are not on this site.[[va_rates]] The site does not say who qualifies, how a rating is decided or whether a dependent counts: VA decides that.</p>') + "</div>")


# ---------------------------------------------------------------- pagine
def pagina_tabelle(S):
    rim = G.Rimandi()
    a, p = T(ANNO), T(PRIMA)
    corpo = (f'<section class="card stats pull" aria-label="Key figures">'
             f'<div class="stat main"><b>{usd(a["base"]["100"])}</b><span>100% rating, Veteran alone, per month{rim.ref("va_rates")}</span></div>'
             f'<div class="stat"><b>{usd(a["base"]["10"])}</b><span>10% rating, per month{rim.ref("va_rates")}</span></div>'
             f'<div class="stat"><b>{usd(a["righe"]["child_spouse"]["100"])}</b><span>100% with spouse and 1 child{rim.ref("va_rates")}</span></div>'
             f'<div class="stat"><b>+{a["aumento_pct"]}%</b><span>Increase over the 2025 rates{rim.ref("va_fr_2026")}</span></div>'
             f'<p class="asof">VA’s “2026” rates: effective {giorno(a["decorrenza"])}. VA’s page was last updated {giorno(a["pagina_aggiornata_il"])}; we read it on {giorno(S["va_letto"])}.</p></section>')
    corpo += avviso_2027(S, rim)
    corpo += ('<div class="azioni"><a class="btn" href="/va-disability-calculator/">' + G.ico("calc") + 'Open the calculator</a>'
              '<a class="btn sec" href="#with-dependents">Rates with dependents</a><a class="btn sec" href="/va-disability-rates/2027/">2027 status</a></div>')
    corpo += f'<h2 id="chart">VA disability pay chart 2026: Veteran with no dependents</h2>{tabella_base(rim)}'
    corpo += f'<h2 id="by-rating">Pay by rating</h2><p>Each rating has its own page with every dependent status, the yearly amount and last year’s rate.</p>{griglia_gradi()}'
    corpo += G.AD
    corpo += ('<h2 id="with-dependents">VA disability rates with dependents, 30% to 100%</h2>'
              '<p>On a phone, swipe the tables sideways.</p>'
              + tabella_stati(SENZA_FIGLI, rim, titolo="With a dependent spouse or parent, but no children.")
              + tabella_stati(CON_FIGLI, rim, titolo="With dependents, including children.") + tabella_aggiunte(rim))
    corpo += come_si_legge(rim)
    corpo += calcolatore_va(id_h="va-h")
    corpo += non_coperto(rim)
    D = dati_calcolo()
    voci = [("2026 va disability rates", "What are the VA disability rates for 2026?",
             f"From {usd(a['base']['10'])} a month at 10% to {usd(a['base']['100'])} at 100% for a Veteran with no dependents, effective {giorno(a['decorrenza'])}. "
             f"With a 30% rating or higher the rate rises with a dependent spouse, children or parents.", "va_rates"),
            ("how much is 100 va disability", "How much is 100% VA disability?",
             f"{usd(a['base']['100'])} a month for a Veteran alone, {usd(a['righe']['spouse']['100'])} with a spouse and {usd(a['righe']['child_spouse']['100'])} with a spouse and one child, at the rates effective {giorno(a['decorrenza'])}.", "va_rates"),
            ("va dependent pay", "Does VA disability pay more with dependents?",
             "With a rating of 30% or more, yes: the basic rate depends on a dependent spouse, children and parents. VA says that with a 10% to 20% rating you won’t receive a higher rate even if you have a dependent spouse, child, or parent.", "va_rates"),
            ("va cola increase", "What is the VA COLA increase for 2027?",
             f"Social Security's cost-of-living increase effective December 2026 is 3.6%, and VA says it is required by law to match that percentage. As of {giorno(S['oggi'])} VA had not published the 2027 rate tables.", "ssa_cola_2027,va_rates"),
            ("va disability pay chart", "Where does this VA disability pay chart come from?",
             "From VA's own rate page on VA.gov, checked cell by cell against VA's notice of the same amounts in the Federal Register.", "va_rates,va_fr_2026"),
            ("va aid and attendance rates", "How much is added for a spouse receiving Aid and Attendance?",
             f"In the disability compensation tables the added amount runs from {usd0(a['aggiunte']['spouse_aa']['30'])} a month at a 30% rating to {usd(a['aggiunte']['spouse_aa']['100'])} at 100%. "
             "Aid and Attendance paid for the Veteran's own needs is in VA's special monthly compensation tables, which are not on this site.", "va_rates")]
    fh, fld = G.faq_blocco(voci, rim)
    corpo += fh + rim.elenco(NOTA_FONTI)
    testata = G.banda(f"Effective {giorno(a['decorrenza'])}", "VA Disability Rates 2026",
                      f"VA’s official monthly compensation by disability rating, 10% to 100%, alone and with a spouse, children or parents. <strong>{usd(a['base']['100'])}</strong> a month at 100%.")
    G.pagina("va-disability-rates/", "VA Disability Rates 2026: Official Pay Chart by Rating",
             f"VA disability rates 2026 by rating, 10% to 100%: {usd(a['base']['10'])} to {usd(a['base']['100'])} a month, with spouse, children and parents. Official VA tables, plus a calculator.",
             corpo, testata, briciole=[("Home", ""), ("VA disability rates", "va-disability-rates/")], jsonld=[fld], disclaimer=DISCLAIMER_VA)


def pagina_grado(g, S):
    rim = G.Rimandi()
    a, p = T(ANNO), T(PRIMA)
    x, y = a["base"][str(g)], p["base"][str(g)]
    sg = str(g)
    if g >= 30:
        stats = (f'<div class="stat"><b>{usd(a["righe"]["spouse"][sg])}</b><span>With a spouse{rim.ref("va_rates")}</span></div>'
                 f'<div class="stat"><b>{usd(a["righe"]["child_spouse"][sg])}</b><span>With a spouse and 1 child{rim.ref("va_rates")}</span></div>')
    else:
        stats = (f'<div class="stat"><b>Same</b><span>With a spouse, child or parent: no higher rate{rim.ref("va_rates")}</span></div>'
                 f'<div class="stat"><b>{usd(y)}</b><span>2025 rate, per month{rim.ref("va_rates_2025")}</span></div>')
    corpo = (f'<section class="card stats pull" aria-label="Key figures">'
             f'<div class="stat main"><b>{usd(x)}</b><span>{g}% rating, Veteran alone, per month{rim.ref("va_rates")}</span></div>'
             f'<div class="stat"><b>{usd(x * 12)}</b><span>Per year (× 12, our arithmetic)</span></div>{stats}'
             f'<p class="asof">VA’s “2026” rates: effective {giorno(a["decorrenza"])}. Read on VA.gov on {giorno(S["va_letto"])}.</p></section>')
    corpo += avviso_2027(S, rim)
    if g >= 30:
        righe = ""
        for k in SENZA_FIGLI + CON_FIGLI:
            v, w = a["righe"][k][sg], p["righe"][k][sg]
            righe += (f'<tr><th scope="row">{h(STATO_NOME[k])}</th><td class="n">{usd(v)}</td><td class="n">{usd(v * 12)}</td><td class="n">{usd(w)}</td><td class="n">+{usd(v - w)}</td></tr>')
        corpo += (f'<h2 id="chart">{g}% VA disability pay with dependents</h2><div class="tab"><table class="dati va"><caption>Basic monthly rates at {"an" if g == 80 else "a"} {g}% rating, U.S. dollars. Effective {giorno(a["decorrenza"])} (“2026”) and '
                  f'{giorno(p["decorrenza"])} (“2025”). Sources: VA{rim.ref("va_rates,va_rates_2025")}. Yearly amount and difference: our arithmetic.</caption>'
                  '<thead><tr><th scope="col">Dependent status</th><th scope="col" class="n">2026, per month</th><th scope="col" class="n">2026, per year</th><th scope="col" class="n">2025, per month</th><th scope="col" class="n">Change</th></tr></thead>'
                  f'<tbody>{righe}</tbody></table></div>')
        righe = "".join(f'<tr><th scope="row">{h(AGG_NOME[k])}</th><td class="n">{usd(a["aggiunte"][k][sg])}</td><td class="n">{usd(p["aggiunte"][k][sg])}</td></tr>' for k in AGG_NOME)
        corpo += (f'<h2 id="added">Added amounts at {g}%</h2><div class="tab"><table class="dati va"><caption>Added monthly amounts at {"an" if g == 80 else "a"} {g}% rating, U.S. dollars: add them to the basic rate. Sources: VA{rim.ref("va_rates,va_rates_2025")}.</caption>'
                  '<thead><tr><th scope="col">Added amount</th><th scope="col" class="n">2026</th><th scope="col" class="n">2025</th></tr></thead>'
                  f'<tbody>{righe}</tbody></table></div>')
        D = dati_calcolo()
        es = paga(D, g, 1, 0, 0, 2, 0)
        corpo += ('<div class="testo">' + rim.t(
            f'<p><strong>Example (our arithmetic, VA’s method):</strong> {g}% with a spouse and two children under 18: {usd(es["base"])} for spouse and one child + {usd0(a["aggiunte"]["child_u18"][sg])} for the second child = {usd(es["cent"])} a month.[[va_rates]] '
            + ('For a partial rating the dependent amounts are whole dollars because the law rounds them down to the dollar.[[usc1115]]' if g < 100 else
               'At 100% the dependent amounts are the full figures set by law, cents included.[[va_fr_2026]]') + '</p>') + "</div>")
    else:
        corpo += (f'<h2 id="chart">{g}% VA disability pay</h2><div class="tab"><table class="dati"><caption>Monthly rate at {"an" if g == 80 else "a"} {g}% rating, U.S. dollars. Sources: VA{rim.ref("va_rates,va_rates_2025")}. Yearly amount and difference: our arithmetic.</caption>'
                  '<thead><tr><th scope="col">Rates</th><th scope="col" class="n">Per month</th><th scope="col" class="n">Per year (× 12)</th></tr></thead><tbody>'
                  f'<tr><th scope="row">2026 (effective {giorno(a["decorrenza"])})</th><td class="n">{usd(x)}</td><td class="n">{usd(x * 12)}</td></tr>'
                  f'<tr><th scope="row">2025 (effective {giorno(p["decorrenza"])})</th><td class="n">{usd(y)}</td><td class="n">{usd(y * 12)}</td></tr>'
                  f'<tr><th scope="row">Change</th><td class="n">+{usd(x - y)}</td><td class="n">+{usd((x - y) * 12)}</td></tr></tbody></table></div>')
        corpo += ('<div class="testo">' + rim.t('<p>VA: “If you have a 10% to 20% disability rating, you won’t receive a higher rate even if you have a dependent spouse, child, or parent.”[[va_rates]] '
                                                'Dependent amounts start at a 30% rating.[[usc1115]]</p>') + "</div>")
    corpo += G.AD
    corpo += calcolatore_va(g=g, coniuge=1 if g >= 30 else 0, u18=1 if g >= 30 else 0, titolo=f"Calculator: {g}% rating, 2026 rates")
    i = VA["gradi"].index(g)
    vicini = []
    if i > 0:
        vicini.append(f'<a class="btn sec" href="/{slug_grado(VA["gradi"][i - 1])}">← {VA["gradi"][i - 1]}%: {usd(a["base"][str(VA["gradi"][i - 1])])}</a>')
    if i < len(VA["gradi"]) - 1:
        vicini.append(f'<a class="btn sec" href="/{slug_grado(VA["gradi"][i + 1])}">{VA["gradi"][i + 1]}%: {usd(a["base"][str(VA["gradi"][i + 1])])} →</a>')
    corpo += f'<h2 id="other-ratings">Other ratings</h2><div class="azioni">{"".join(vicini)}<a class="btn sec" href="/va-disability-rates/">Full VA pay chart</a></div>{griglia_gradi(g)}'
    risposta = (f"{usd(x)} a month for a Veteran with no dependents, or {usd(x * 12)} a year, at the rates effective {giorno(a['decorrenza'])}. "
                + (f"With a spouse it is {usd(a['righe']['spouse'][sg])} a month, and with a spouse and one child {usd(a['righe']['child_spouse'][sg])}." if g >= 30
                   else "VA pays the same amount with or without dependents at this rating."))
    voci = [(GRADO_RICERCA[g], f"How much is {g}% VA disability in 2026?", risposta, "va_rates")]
    if g >= 30:
        voci.append(("va dependent pay", f"How much does a spouse add at {g}%?",
                     f"{usd0(a['righe']['spouse'][sg] - x)} a month: {usd(a['righe']['spouse'][sg])} with a spouse against {usd(x)} alone. "
                     f"If the spouse receives Aid and Attendance, VA adds {usd0(a['aggiunte']['spouse_aa'][sg])} more.", "va_rates"))
    fh, fld = G.faq_blocco(voci, rim)
    corpo += fh + rim.elenco(NOTA_FONTI)
    testata = G.banda(f"Effective {giorno(a['decorrenza'])}", f"{g}% VA Disability Pay 2026",
                      f"<strong>{usd(x)}</strong> a month for a Veteran with no dependents at {'an' if g == 80 else 'a'} {g}% rating"
                      + (", and every rate with a spouse, children or parents." if g >= 30 else ". VA pays the same with or without dependents at this rating."), corta=True)
    G.pagina(slug_grado(g), f"{g}% VA Disability Pay 2026: {usd(x)} a Month",
             (f"{g}% VA disability pay in 2026: {usd(x)} a month alone, {usd(a['righe']['spouse'][sg])} with a spouse, {usd(a['righe']['child_spouse'][sg])} with spouse and child. Official VA rates and 2025 rates."
              if g >= 30 else f"{g}% VA disability pay in 2026: {usd(x)} a month, {usd(x * 12)} a year, the same with or without dependents. Official VA rate, 2025 rate and calculator."),
             corpo, testata, briciole=[("Home", ""), ("VA disability rates", "va-disability-rates/"), (f"{g}%", slug_grado(g))], jsonld=[fld], disclaimer=DISCLAIMER_VA)


def tabella_combinati(rim):
    C = VA["combinati"]
    testa = '<th scope="col">Combined value so far</th>' + "".join(f'<th scope="col" class="n">{c}</th>' for c in C["colonne"])
    righe = "".join(f'<tr><th scope="row">{k}</th>' + "".join(f'<td class="n">{v}</td>' for v in C["righe"][k]) + "</tr>" for k in sorted(C["righe"], key=int))
    return (f'<details class="card piega"><summary>Show Table I, combined ratings table ({len(C["righe"])} rows)</summary><div class="tab"><table class="dati"><caption>Table I of 38 CFR 4.25: the higher rating or the combined value so far in the left column, '
            f'the next rating in the top row. Note of the table: 10 combined with 10 is 19. Source: Code of Federal Regulations{rim.ref("cfr4_25")}.</caption>'
            f'<thead><tr>{testa}</tr></thead><tbody>{righe}</tbody></table></div></details>')


def pagina_calcolatore(S):
    rim = G.Rimandi()
    a = T()
    D = dati_calcolo()
    c1, c2 = combina(D, [50, 30]), combina(D, [60, 40, 20])
    corpo = '<div class="pull">' + calcolatore_va(titolo="VA disability calculator, 2026 rates", id_h="va-h") + "</div>"
    corpo += avviso_2027(S, rim)
    corpo += ('<h2 id="how-it-works">How the calculator works</h2><div class="testo">' + rim.t(
        '<ol><li><strong>Rating.</strong> Pick your combined rating, the one in your VA decision. If you only know the single ratings, type them and the calculator combines them with VA’s table (below).</li>'
        '<li><strong>Basic rate.</strong> It reads the row of VA’s table for your dependent status: “Your basic monthly rate is where your dependent status and disability rating meet.”[[va_rates]]</li>'
        '<li><strong>Added amounts.</strong> It adds VA’s amounts for each child after the first and for a spouse receiving Aid and Attendance.[[va_rates]]</li></ol>'
        '<p>At 10% and 20% dependents change nothing: “If you have a 10% to 20% disability rating, you won’t receive a higher rate even if you have a dependent spouse, child, or parent.”[[va_rates]] '
        'The calculator does not work out a household whose only children are over 18 and in school: VA’s table lists that amount only as an addition for a further child.</p>') + "</div>")
    corpo += ('<h2 id="combined-rating">How VA combines ratings</h2><div class="testo">' + rim.t(
        '<p>VA: “Calculating your combined disability rating involves more than adding up your individual ratings.” “That’s why your combined rating may be different from the sum of your individual ratings.”[[va_about]] '
        'The rule is in the regulation: “the disabilities will first be arranged in the exact order of their severity, beginning with the greatest disability and then combined with use of table I”. '
        '“This combined value will then be converted to the nearest number divisible by 10, and combined values ending in 5 will be adjusted upward.”[[cfr4_25]]</p>'
        f'<ul><li>50% and 30%: the table gives {c1["valore"]}, converted to {c1["finale"]}%. The regulation’s own example.[[cfr4_25]]</li>'
        f'<li>60%, 40% and 20%: 60 and 40 give {c2["passi"][0][2]}; {c2["passi"][0][2]} and 20 give {c2["valore"]}, converted to {c2["finale"]}%. Also the regulation’s example.[[cfr4_25]]</li>'
        '<li>The rounding happens once, at the end: “The conversion to the nearest degree divisible by 10 will be done only once per rating decision”.[[cfr4_25]]</li></ul>'
        '<p><strong>Not included: the bilateral factor.</strong> For disabilities of both arms, both legs or paired skeletal muscles, “the ratings for the disabilities of the right and left sides will be combined as usual, '
        'and 10 percent of this value will be added” before the other ratings are combined.[[cfr4_26]] The calculator does not apply it, so with bilateral disabilities your VA combined rating can be higher than the one shown here.</p>') + "</div>")
    corpo += tabella_combinati(rim)
    corpo += G.AD
    corpo += f'<h2 id="chart">The rates the calculator uses</h2>{tabella_base(rim)}<p><a href="/va-disability-rates/#with-dependents">All rates with dependents, 30% to 100% →</a></p>'
    voci = [("va disability calculator", "How is the monthly VA disability payment calculated?",
             "VA's tables give a basic monthly rate for your disability rating and dependent status. If you have more than one child or your spouse receives Aid and Attendance, VA's added amounts are added to it.", "va_rates"),
            ("va combined rating calculator", "How does VA combine more than one rating?",
             "Not by adding them. The ratings are put in order of severity and combined with Table I of 38 CFR 4.25; the result is converted to the nearest number divisible by 10, and values ending in 5 go up.", "cfr4_25,va_about"),
            ("va disability math", "Why do 50% and 30% make 70%, not 80%?",
             f"Table I combines 50 and 30 into {c1['valore']}, and the regulation says 65 must be converted to 70. The table measures the second disability against the efficiency left after the first.", "cfr4_25"),
            ("va bilateral factor", "Does this calculator apply the bilateral factor?",
             "No. Under 38 CFR 4.26, ratings for both arms, both legs or paired skeletal muscles are combined and 10 percent of that value is added before the other combinations. The calculator leaves that step out.", "cfr4_26"),
            ("va disability rating calculator", "Which rates does the calculator use?",
             f"VA's rates effective {giorno(a['decorrenza'])}, the ones VA calls 2026 rates. As of {giorno(S['oggi'])} VA had not published the table for December 1, 2026.", "va_rates")]
    fh, fld = G.faq_blocco(voci, rim)
    corpo += fh + rim.elenco(NOTA_FONTI)
    testata = G.banda("Rating + dependents → monthly amount", "VA Disability Calculator",
                      "Pick your combined rating, or enter each rating and let VA’s combined ratings table do the math, then add your dependents. Official 2026 rates.", icona="calc")
    G.pagina("va-disability-calculator/", "VA Disability Calculator 2026: Rating and Dependents",
             "VA disability calculator with the official 2026 rates: combined rating or single ratings (38 CFR 4.25), spouse, children and parents. Monthly and yearly amount.",
             corpo, testata, briciole=[("Home", ""), ("VA disability rates", "va-disability-rates/"), ("Calculator", "va-disability-calculator/")], jsonld=[fld], disclaimer=DISCLAIMER_VA)


def pagina_2027(S):
    rim = G.Rimandi()
    a = T()
    ul = S["ultima_legge"]
    avv = S["avvisi"]
    corpo = (f'<section class="card stats pull" aria-label="2027 status">'
             f'<div class="stat main"><b>3.6%</b><span>Social Security cost-of-living increase, effective December 2026{rim.ref("ssa_cola_2027")}</span></div>'
             f'<div class="stat"><b>Dec 1, 2026</b><span>Effective date in the bill passed by Congress{rim.ref("hr8552")}</span></div>'
             f'<div class="stat"><b>Not yet</b><span>The bill among the published public laws{rim.ref("plaw119")}</span></div>'
             f'<div class="stat"><b>Not yet</b><span>VA’s table of the new amounts{rim.ref("va_rates,fr_va_search")}</span></div>'
             f'<p class="asof">Status as of {giorno(S["oggi"])}. Nothing on this page is a forecast: each line is what an official source says on that date.</p></section>')
    corpo += '<h2 id="official">What is official so far</h2><div class="testo">' + rim.t(
        '<p><strong>The percentage: 3.6%.</strong> The Social Security Administration’s notice in the Federal Register of October 26, 2026 says “there will be a 3.6 percent cost-of-living increase in Social Security benefits effective December 2026”.[[ssa_cola_2027]]</p>'
        '<p><strong>VA follows Social Security.</strong> VA writes on its rate page: “We’re required by law to match the percentage of cost-of-living adjustments made to Social Security benefits.” '
        '“These adjustments help to make sure that the purchasing power of your benefits keeps up with inflation.”[[va_rates]]</p>'
        '<p><strong>The law for this year.</strong> Each year’s increase comes from an act of Congress. For the rates in force now it was Public Law 119-42, approved on November 25, 2025.[[plaw119_42]] '
        'For the next ones the Government Publishing Office published on November 13, 2026 the enrolled bill H.R. 8552, the Veterans’ Compensation Cost-of-Living Adjustment Act of 2026: '
        'an enrolled bill is the final text as passed by both the House and the Senate. It says: “Each dollar amount described in subsection (b) shall be increased by the same percentage as the percentage by which '
        'benefit amounts payable under title II of the Social Security Act (42 U.S.C. 401 et seq.) are increased effective December 1, 2026”.[[hr8552]] '
        + (f'On {giorno(S["leggi_letto"])} the list of published public laws on govinfo.gov ran to Public Law {ul["numero"]} ({giorno(ul["data"])}) and did not include it yet.[[plaw119]]</p>' if ul else "</p>")
        + f'<p><strong>The amounts: not published.</strong> On {giorno(S["va_letto"])} VA’s rate page, last updated {giorno(S["va_aggiornata"])}, still showed the tables effective {giorno(a["decorrenza"])}.[[va_rates]] '
        'The bill also says: “The Secretary of Veterans Affairs shall publish in the Federal Register the amounts specified in section 2(b), as increased under that section”.[[hr8552]] '
        f'On {giorno(S["fr_letto"])} the newest such VA notice was still the one of {giorno(avv[0]["data"])}, with the amounts effective {giorno(a["decorrenza"])}; the two before it are dated {giorno(avv[1]["data"])} and {giorno(avv[2]["data"])}.[[fr_va_search,va_fr_2026]]</p>') + "</div>"
    corpo += G.AD
    corpo += ('<h2 id="no-estimates">Why there is no 2027 table here yet</h2><div class="testo">' + rim.t(
        '<p>We do not publish a “2027 VA pay chart” worked out from the percentage. The law sets the percentage and one rounding rule, for dependents at partial ratings: '
        '“The amounts payable under this paragraph, if not a multiple of $1, shall be rounded down to the nearest dollar.”[[usc1115]] '
        'No official source we could read says how each increased amount is rounded to the cent, and when we applied the announced percentage to VA’s published amounts for the last two years, '
        'the result did not match VA’s own figures in every case.[[va_fr_2026,va_fr_2025]] A table built that way could be a cent off, and it would not be VA’s table.</p>'
        f'<p>Until VA publishes the new amounts, the official rates are the <a href="/va-disability-rates/">2026 rates</a>, effective {giorno(a["decorrenza"])}. '
        'This page and the rate tables are updated when VA’s table changes.</p>') + "</div>")
    corpo += f'<h2 id="current">The rates in force now</h2>{tabella_base(rim)}'
    corpo += ('<div class="azioni"><a class="btn" href="/va-disability-rates/">Full 2026 pay chart</a><a class="btn sec" href="/va-disability-calculator/">' + G.ico("calc") + 'Calculator</a></div>')
    voci = [("va cola increase", "What is the VA COLA increase for 2027?",
             "3.6% is the Social Security cost-of-living increase effective December 2026, and VA says it is required by law to match that percentage. "
             f"As of {giorno(S['oggi'])} VA had not published the new rate tables.", "ssa_cola_2027,va_rates"),
            ("va disability increase", "When does the VA disability increase take effect?",
             "The bill passed by Congress, H.R. 8552, sets the increase to take effect on December 1, 2026. "
             + (f"On {giorno(S['leggi_letto'])} it was not yet in the list of published public laws." if ul else ""), "hr8552,plaw119"),
            ("va disability pay increase", "Will VA disability pay go up in 2027?",
             "The bill passed by Congress raises the rates from December 1, 2026 by the same percentage as Social Security benefits, which is 3.6%. "
             f"VA's table with the new amounts had not been published as of {giorno(S['oggi'])}.", "hr8552,ssa_cola_2027,va_rates"),
            ("va disability rates", "What are the VA disability rates right now?",
             f"The rates effective {giorno(a['decorrenza'])}: {usd(a['base']['10'])} a month at 10% up to {usd(a['base']['100'])} at 100% for a Veteran with no dependents.", "va_rates")]
    fh, fld = G.faq_blocco(voci, rim)
    corpo += fh + rim.elenco(NOTA_FONTI)
    testata = G.banda(f"Status on {giorno(S['oggi'])}", "2027 VA Disability Rates: What Is Official So Far",
                      "The 3.6% cost-of-living increase, the bill in Congress and VA’s rate table are different things. Here is what each official source says, with its date.", corta=True, icona="cal")
    G.pagina("va-disability-rates/2027/", "2027 VA Disability Rates: 3.6% COLA, What Is Official",
             "2027 VA disability rates: the 3.6% cost-of-living increase from December 1, 2026, the bill passed by Congress and whether VA's new table is out. Dated, sourced.",
             corpo, testata, briciole=[("Home", ""), ("VA disability rates", "va-disability-rates/"), ("2027", "va-disability-rates/2027/")], jsonld=[fld], disclaimer=DISCLAIMER_VA)


def come_controlliamo(G_, rim):
    """Paragrafo per /how-we-check/ (chiamato da genera.come_controlliamo)."""
    carica(G_)
    d = VA["combinati"]["differenze_va"]
    return ('<h2 id="va-checks">VA disability rates</h2><div class="testo"><ul>' + rim.t(
        '<li>The rate tables are copied from VA’s pages for the rates effective December 1, 2025 and December 1, 2024: 122 amounts each.[[va_rates,va_rates_2025]] '
        'We keep each page as downloaded, with its address, date and fingerprint (SHA-256).</li>'
        '<li>Second source: VA’s notices in the Federal Register give the amounts set by law for each rating and for dependents at a 100% rating.[[va_fr_2026,va_fr_2025]] '
        'From those amounts and the rule in the law for partial ratings (the same share as the rating, rounded down to the dollar)[[usc1115]] we rebuild every cell: all 244 match VA’s pages. One mismatch stops the build.</li>'
        '<li>The combined ratings table is Table I of 38 CFR 4.25, read from the official eCFR.[[cfr4_25]] Each of its 684 cells matches the method described in the text of the regulation. '
        + (f'VA’s online copy of the table differs in one cell (row {d[0][0]}, column {d[0][1]}: {d[0][3]} instead of {d[0][2]}); we use the regulation.[[va_about]]' if d else 'VA’s online copy of the table matches it.[[va_about]]') + '</li>'
        '<li>The calculator in your browser is checked against a separate calculation from the amounts in the Federal Register notice, on every rating and thousands of dependent combinations, and against the examples VA and the regulation give.</li>'
        '<li>The sentences we quote from VA, the law and the regulation are re-read at the source; a missing sentence stops the build. That is also how the site notices when VA publishes the next table.</li>'
        '<li>We do not publish estimated 2027 amounts: see <a href="/va-disability-rates/2027/#no-estimates">why</a>.</li>') + "</ul></div>")


# ---------------------------------------------------------------- entrata
def carica(G_):
    global G, VA
    G = G_
    VA = json.loads((G.DATI / "va.json").read_text(encoding="utf-8"))


def genera(G_):
    carica(G_)
    stat = controlla()
    S = stat["stato_2027"]
    pagina_tabelle(S)
    for g in gradi_pagina():
        pagina_grado(g, S)
    pagina_calcolatore(S)
    pagina_2027(S)
    return {"celle": stat["celle"], "table_i": stat["table_i"], "pagine": 3 + len(gradi_pagina()), "stato_al": S["oggi"]}
