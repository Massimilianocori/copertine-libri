"""Sezione "prezzi del gasolio da riscaldamento e del propano per Stato" (USA), dai prezzi settimanali ufficiali dell'EIA.

Dati: dati/eia_prezzi.json, scritto da raccolta/eia.py dai due XLS dell'EIA (Weekly Heating Oil and Propane Prices, dollari per gallone,
tasse escluse, un prezzo per lunedì da ottobre a marzo, storia dal 1990). Pagine:
  /heating-oil-prices/            indice: Stati Uniti + tutti gli Stati rilevati, inverno in corso e scorso, storia, calcolatore del pieno
  /propane-prices/                lo stesso per il propano
  /heating-oil-prices/<stato>/    una pagina per Stato solo se la domanda misurata (dati/domanda.json, gruppo riscaldamento) è ≥ 100 al mese
  /propane-prices/<stato>/
Ogni prezzo stampato porta un attributo data-* che dice da quale serie, area e settimana viene (verifica.py lo rifà dall'XLS):
  data-p="comb|area|data"            prezzo EIA di quella settimana
  data-d / data-r="comb|area|d1|d0"  differenza in dollari / variazione percentuale tra due settimane
  data-m="comb|area|stagione"        media semplice delle settimane pubblicate di una stagione (ottobre-marzo): calcolo nostro, dichiarato
  data-mp="comb|area|stagione|cur" o "|prev"  media delle settimane dell'inverno in corso che hanno anche il prezzo di un anno prima (e di quelle)
  data-cpi="comb|area|stagione"      media della stagione × CPI-U ultimo mese ÷ CPI-U di gennaio di quell'inverno
  data-t="comb|area|data|decimi di gallone"   galloni × prezzo
Tutti i conti sono in millesimi di dollaro interi. Nessun consiglio (quando comprare), nessun fornitore. genera.py chiama genera(G).
"""
import json
import re
from datetime import date, timedelta
from pathlib import Path

RADICE = Path(__file__).resolve().parent
P = json.loads((RADICE / "dati" / "eia_prezzi.json").read_text(encoding="utf-8"))
SOGLIA = 100  # ricerche al mese: sotto, lo Stato resta solo nella tabella dell'indice
MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
COMB = {
    "oil": {"slug": "heating-oil-prices/", "nome": "heating oil", "Nome": "Heating oil", "Tit": "Heating Oil", "def": "gasolio", "tab": "eia_oil_tabella",
            "gal": 200, "chips": (100, 150, 200, 250), "faq_gal": (200, 250), "parole": r"heating oil|fuel oil|oil heat"},
    "propane": {"slug": "propane-prices/", "nome": "propane", "Nome": "Propane", "Tit": "Propane", "def": "propano", "tab": "eia_propane_tabella",
                "gal": 300, "chips": (100, 200, 300, 400), "faq_gal": (300, 500), "parole": r"propane"},
}
SIGLE = {"Connecticut": "CT", "Maine": "ME", "Massachusetts": "MA", "New Hampshire": "NH", "Rhode Island": "RI", "Vermont": "VT", "Delaware": "DE",
         "Maryland": "MD", "New Jersey": "NJ", "New York": "NY", "Pennsylvania": "PA", "Florida": "FL", "Georgia": "GA", "North Carolina": "NC",
         "Virginia": "VA", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Michigan": "MI", "Minnesota": "MN",
         "Missouri": "MO", "Nebraska": "NE", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "South Dakota": "SD", "Tennessee": "TN",
         "Wisconsin": "WI", "Alabama": "AL", "Arkansas": "AR", "Mississippi": "MS", "Texas": "TX", "Colorado": "CO", "Idaho": "ID", "Montana": "MT",
         "Utah": "UT", "District of Columbia": "DC"}
# sigle che sono anche parole inglesi o spagnole: contano solo subito dopo "prices" ("propane prices in" non è l'Indiana)
SIGLE_AMBIGUE = {"in", "me", "de", "ok", "oh", "al", "ar", "co", "id", "ma", "pa", "mo", "ms", "mt", "ne", "ut", "or", "hi", "la"}


# ---------------------------------------------------------------- serie
class Serie:
    def __init__(self, comb):
        x = P["combustibili"][comb]
        self.comb = comb
        self.date = [date.fromisoformat(d) for d in x["date"]]
        self.pos = {d: i for i, d in enumerate(self.date)}
        self.aree = x["aree"]
        self.mill = {cod: [None if v is None else round(v * 1000) for v in a["valori"]] for cod, a in x["aree"].items()}
        self.uscita = date.fromisoformat(x["uscita"])
        self.prossima = date.fromisoformat(x["prossima_uscita"])
        self.ultima = self.date[-1]

    def ultimo(self, cod):
        """Indice dell'ultima settimana con un prezzo per l'area."""
        v = self.mill[cod]
        return next((i for i in range(len(v) - 1, -1, -1) if v[i] is not None), None)

    def prima(self, cod, i, giorni):
        """Indice della settimana `giorni` prima (o la più vicina tra quelle ammesse) che ha un prezzo."""
        for g in giorni:
            j = self.pos.get(self.date[i] - timedelta(days=g))
            if j is not None and self.mill[cod][j] is not None:
                return j
        return None

    def anno_prima(self, cod, i):
        return self.prima(cod, i, (364, 371, 357))  # 52 settimane prima; se manca, 53 o 51

    def sett_prima(self, cod, i):
        return self.prima(cod, i, (7,))

    def stagioni(self, cod):
        """{anno d'inizio: [indici con prezzo]} per le settimane da ottobre a marzo."""
        out = {}
        for i, d in enumerate(self.date):
            s = stagione(d)
            if s is not None and self.mill[cod][i] is not None:
                out.setdefault(s, []).append(i)
        return out

    def attiva(self, cod):
        """L'area ha un prezzo in una delle ultime tre settimane pubblicate."""
        return any(x is not None for x in self.mill[cod][-3:])


def stagione(d):
    """Anno d'inizio della stagione di riscaldamento (ottobre-marzo) a cui appartiene la data; None da aprile a settembre."""
    return d.year if d.month >= 10 else d.year - 1 if d.month <= 3 else None


def nome_stagione(s):
    return f"{s}–{str(s + 1)[2:]}" if (s + 1) % 100 else f"{s}–{s + 1}"


def media(valori):
    """Media semplice in millesimi interi, mezzo millesimo per eccesso."""
    return (2 * sum(valori) + len(valori)) // (2 * len(valori))


def perc10(a, b):
    """Variazione percentuale da b ad a in decimi di punto, arrotondata al decimo più vicino (interi)."""
    return (2000 * (a - b) + b) // (2 * b)


def costo_pieno(gd, mill):
    """Decimi di gallone × millesimi di dollaro → centesimi (stile.TANK_MOTORE_JS è la copia)."""
    return (gd * mill + 50) // 100


SR = {c: Serie(c) for c in COMB}
LETTO = date.fromisoformat(P["letto_il"])
ULTIMA = SR["oil"].ultima
STAG = stagione(ULTIMA) if stagione(ULTIMA) is not None else ULTIMA.year - 1  # inverno in corso (o l'ultimo finito)
# L'inverno è «in corso» solo se l'ultimo prezzo è di ottobre-marzo, è stato letto da poco e anche il lunedì successivo cade in stagione:
# dopo l'ultimo lunedì di marzo non ci sono altre rilevazioni settimanali, e le pagine smettono da sole di dire «so far» e «next release»
# anche se nessuno rilancia raccolta/eia.py fino a ottobre.
IN_STAGIONE = stagione(ULTIMA) is not None and (LETTO - ULTIMA).days <= 14 and stagione(ULTIMA + timedelta(days=7)) is not None
FUORI = stagione(ULTIMA) is None  # l'ultimo prezzo è uno di quelli mensili che l'EIA raccoglie da aprile a settembre


# ---------------------------------------------------------------- formati
def dl(d):
    return f"{MESI[d.month - 1]} {d.day}, {d.year}"


def db(d):
    return f"{MESI[d.month - 1][:3]} {d.day}, {d.year}"


def p3(mill):
    return f"${mill / 1000:.3f}"


def usd_c(c):
    return f"${c / 100:,.2f}"


def segno_d(d):
    return ("+" if d > 0 else "−" if d < 0 else "") + p3(abs(d))


def segno_r(r10):
    return ("+" if r10 > 0 else "−" if r10 < 0 else "") + f"{abs(r10) / 10:.1f}%"


def slug(nome):
    return nome.lower().replace(" ", "-")


def gal_txt(gd):
    return f"{gd // 10:,}" if gd % 10 == 0 else f"{gd / 10:,.1f}"


# ---------------------------------------------------------------- celle etichettate (verifica.py le rifà tutte dall'XLS)
def el(attr, chiave, testo, tag="span", cls=""):
    return f'<{tag}{f" class=\"{cls}\"" if cls else ""} data-{attr}="{chiave}">{testo}</{tag}>'


def pz(comb, cod, i, tag="span", cls=""):
    s = SR[comb]
    return el("p", f"{comb}|{cod}|{s.date[i].isoformat()}", p3(s.mill[cod][i]), tag, cls)


def diff(comb, cod, i, j, tag="span", cls=""):
    s = SR[comb]
    return el("d", f"{comb}|{cod}|{s.date[i].isoformat()}|{s.date[j].isoformat()}", segno_d(s.mill[cod][i] - s.mill[cod][j]), tag, cls)


def var(comb, cod, i, j, tag="span", cls=""):
    s = SR[comb]
    return el("r", f"{comb}|{cod}|{s.date[i].isoformat()}|{s.date[j].isoformat()}", segno_r(perc10(s.mill[cod][i], s.mill[cod][j])), tag, cls)


def med(comb, cod, st, tag="span", cls=""):
    s = SR[comb]
    return el("m", f"{comb}|{cod}|{st}", p3(media([s.mill[cod][i] for i in s.stagioni(cod)[st]])), tag, cls)


def coppie(comb, cod, st):
    """Settimane della stagione che hanno anche il prezzo di un anno prima: [(i, j)]."""
    s = SR[comb]
    return [(i, s.anno_prima(cod, i)) for i in s.stagioni(cod).get(st, []) if s.anno_prima(cod, i) is not None]


def med_coppie(comb, cod, st, quale, tag="span", cls=""):
    s = SR[comb]
    cp = coppie(comb, cod, st)
    return el("mp", f"{comb}|{cod}|{st}|{quale}", p3(media([s.mill[cod][i if quale == "cur" else j] for i, j in cp])), tag, cls)


def cpi_valore(G, mill, st):
    """Media di una stagione in dollari dell'ultimo mese del CPI-U: × CPI ultimo ÷ CPI di gennaio di quell'inverno. None se gennaio non c'è ancora."""
    m = G.S["us"]["mensile"]
    if (st + 1, 1) not in m:
        return None
    return round(mill / 1000 * m[G.US_LU] / m[(st + 1, 1)], 2)


def vuota(cls="n vuoto"):
    return f'<td class="{cls}">–</td>'


# ---------------------------------------------------------------- domanda misurata → quali Stati hanno una pagina
def _stati_nella_frase(frase):
    parole = frase.split()
    out = set()
    for nome, sigla in SIGLE.items():
        n, a = nome.lower(), sigla.lower()
        if re.search(r"(?<![a-z])(?<!west )" + n + r"(?![a-z])", frase):
            out.add(nome)
        elif a not in SIGLE_AMBIGUE and a in (parole[0], parole[-1]):
            out.add(nome)
        elif a in SIGLE_AMBIGUE and parole[-1] == a and f"prices {a}" in frase:
            out.add(nome)
    return out


def domanda(G):
    """{(comb, Stato): (volume, frase)}: la frase più cercata tra quelle misurate (dati/domanda.json, gruppo riscaldamento, con le «simili»)
    che nomina il combustibile, «price» o «cost» e un solo Stato (per nome, o per sigla postale a inizio o fine frase)."""
    frasi = {}
    for r in G.DOMANDA["richieste"]:
        if r.get("gruppo") != "riscaldamento":
            continue
        for x in [r] + r["simili"]:
            frasi[x["frase"].lower()] = max(frasi.get(x["frase"].lower(), 0), x["volume"] or 0)
    out = {}
    for f, v in sorted(frasi.items()):
        if not re.search(r"price|cost", f) or re.search(r"kerosene|wholesale|compan|exchange|diesel", f):
            continue
        comb = next((c for c, k in COMB.items() if re.search(k["parole"], f)), None)
        stati = _stati_nella_frase(f)
        if comb and len(stati) == 1:
            k = (comb, stati.pop())
            if v > out.get(k, (0, ""))[0]:
                out[k] = (v, f)
    return out


def stati_attivi(comb):
    s = SR[comb]
    return sorted((a["nome"], cod) for cod, a in s.aree.items() if a["tipo"] == "stato" and s.attiva(cod))


def pagine_stato(G):
    """[(comb, codice, Stato, volume, frase)] per gli Stati con un prezzo corrente e domanda misurata ≥ SOGLIA."""
    dom = domanda(G)
    out = []
    for comb in COMB:
        for nome, cod in stati_attivi(comb):
            v, f = dom.get((comb, nome), (0, ""))
            if v >= SOGLIA:
                out.append((comb, cod, nome, v, f))
    return out


def percorso(comb, nome=None):
    return COMB[comb]["slug"] + (slug(nome) + "/" if nome else "")


# ---------------------------------------------------------------- grafici
def graf_inverni(G, comb, cod, aria, didascalia):
    """Due inverni a confronto (settimana per settimana, da ottobre a marzo): linea piena = inverno in corso, tratteggiata = quello prima."""
    s = SR[comb]
    st = s.stagioni(cod)
    serie = []
    for anno in (STAG - 1, STAG):
        serie.append([((s.date[i] - date(anno, 10, 1)).days, s.mill[cod][i] / 1000, s.date[i]) for i in st.get(anno, [])])
    tutti = [y for pts in serie for _, y, _ in pts]
    if not tutti:
        return ""
    tk = G.tacche(min(tutti), max(tutti))
    mn, mx = tk[0], tk[-1]
    X1 = 182
    sx = lambda x: x / X1 * 1000  # noqa: E731
    sy = lambda v: (1 - (v - mn) / ((mx - mn) or 1)) * 300  # noqa: E731

    def path(pts):
        d, prec = "", None
        for x, y, giorno in pts:
            d += f"{'L' if prec and (giorno - prec).days <= 21 else 'M'}{sx(x):.1f} {sy(y):.1f} "  # un buco di più di tre settimane spezza la linea
            prec = giorno
        return d.strip()
    g = "".join(f'<line class="gr" x1="0" x2="1000" y1="{sy(v):.1f}" y2="{sy(v):.1f}"/>' for v in tk)
    lab = "".join(f'<span class="gy" style="top:{sy(v) / 3:.1f}%">${v:.2f}</span>' for v in tk)
    if serie[0]:
        g += f'<path class="lin2" d="{path(serie[0])}"/>'
    if serie[1]:
        x, y, _ = serie[1][-1]
        g += f'<path class="lin" d="{path(serie[1])}"/><path class="dot" d="M{sx(x):.1f} {sy(y):.1f}h0.01"/>'
    mesi = "".join(f'<span class="gx{" first" if not i else ""}" style="left:{g0 / X1 * 100:.1f}%">{m}</span>'
                   for i, (m, g0) in enumerate((("Oct", 0), ("Nov", 31), ("Dec", 61), ("Jan", 92), ("Feb", 123), ("Mar", 151))))
    leg = (f'<ul class="leg"><li><i></i>{nome_stagione(STAG)}</li><li><i class="b"></i>{nome_stagione(STAG - 1)}</li></ul>')
    return (f'<figure class="graf alta" role="img" aria-label="{G.h(aria)}">{leg}<div class="graf-area"><svg viewBox="0 0 1000 300" preserveAspectRatio="none" '
            f'aria-hidden="true">{g}</svg>{lab}{mesi}</div><figcaption>{didascalia}</figcaption></figure>')


def graf_storia(G, comb, cod, nome):
    s = SR[comb]
    st = s.stagioni(cod)
    punti = [(a, media([s.mill[cod][i] for i in ix]) / 1000) for a, ix in sorted(st.items())]
    if len(punti) < 3:
        return ""
    return G.graf_linea(punti, lambda v: f"${v:.2f}", f"Average {COMB[comb]['nome']} price per winter, {nome}, {punti[0][0]} to {punti[-1][0]}",
                        f"Average of the weekly prices of each heating season (October to March), dollars per gallon, not adjusted for inflation. "
                        f"The year is the one in which the winter starts: {punti[-1][0]} is the winter of {nome_stagione(punti[-1][0])}"
                        + (", so far." if IN_STAGIONE else "."))


# ---------------------------------------------------------------- blocchi comuni
def tabella_settimane(G, comb, cod):
    """Inverno in corso e inverno prima, settimana per settimana (allineate a 52 settimane di distanza)."""
    s = SR[comb]
    st = s.stagioni(cod)
    righe = {}
    for i in st.get(STAG, []):
        righe[s.date[i]] = [i, s.anno_prima(cod, i)]
    usati = {j for _, j in righe.values() if j is not None}
    for j in st.get(STAG - 1, []):
        if j not in usati:
            righe.setdefault(s.date[j] + timedelta(days=364), [None, j])
    ult = s.ultimo(cod)
    corpo = ""
    for d in sorted(righe):
        i, j = righe[d]
        tr = ' class="evid"' if i is not None and i == ult else ""
        if i is not None:
            c1 = f'<td class="nw">{db(s.date[i])}</td>{pz(comb, cod, i, "td", "n")}'
        elif d > s.ultima and stagione(d) == STAG:
            c1 = f'<td class="nw futuro">{db(d)}</td>{vuota("n futuro")}'  # settimana non ancora pubblicata
        else:
            c1 = f'<td class="nw futuro">–</td>{vuota("n futuro")}'  # nessuna rilevazione dell'inverno in corso per quella settimana
        c2 = f'<td class="nw">{db(s.date[j])}</td>{pz(comb, cod, j, "td", "n")}' if j is not None else "<td>–</td>" + vuota()
        c3 = (diff(comb, cod, i, j, "td", "n") + var(comb, cod, i, j, "td", "n")) if i is not None and j is not None else vuota() + vuota()
        corpo += f"<tr{tr}>{c1}{c2}{c3}</tr>"
    return ('<div class="tab alta fissa"><table class="dati"><thead><tr>'
            f'<th scope="col">Week of</th><th scope="col" class="n">Winter {nome_stagione(STAG)}</th>'
            f'<th scope="col">Year earlier</th><th scope="col" class="n">Winter {nome_stagione(STAG - 1)}</th><th scope="col" class="n">Change</th><th scope="col" class="n">Change %</th>'
            f'</tr></thead><tbody>{corpo}</tbody></table></div>')


def tabella_stagioni(G, comb, cod):
    s = SR[comb]
    st = s.stagioni(cod)
    corpo = ""
    for a in sorted(st, reverse=True):
        ix = st[a]
        lo = min(ix, key=lambda i: (s.mill[cod][i], i))
        hi = max(ix, key=lambda i: (s.mill[cod][i], -i))
        corso = a == STAG and IN_STAGIONE
        corpo += (f'<tr{" class=\"evid\"" if a == STAG else ""}><td class="nw">{nome_stagione(a)}{" (so far)" if corso else ""}</td>{med(comb, cod, a, "td", "n")}'
                  f'<td class="nw">{db(s.date[lo])}</td>{pz(comb, cod, lo, "td", "n")}<td class="nw">{db(s.date[hi])}</td>{pz(comb, cod, hi, "td", "n")}<td class="n">{len(ix)}</td></tr>')
    return ('<div class="tab alta fissa"><table class="dati"><thead><tr><th scope="col">Winter</th><th scope="col" class="n">Average</th>'
            '<th scope="col">Lowest week</th><th scope="col" class="n">Price</th><th scope="col">Highest week</th><th scope="col" class="n">Price</th>'
            f'<th scope="col" class="n">Weeks published</th></tr></thead><tbody>{corpo}</tbody></table></div>')


def calcolatore(G, comb, cod_sel):
    """Costo del pieno: galloni × ultimo prezzo EIA dell'area scelta; a fianco lo stesso pieno al prezzo di un anno prima."""
    s, k = SR[comb], COMB[comb]
    aree = {}
    elenco = [("U.S. average", "NUS")] + stati_attivi(comb)
    for nome, cod in elenco:
        i = s.ultimo(cod)
        j = s.anno_prima(cod, i)
        aree[cod] = [nome, s.mill[cod][i], dl(s.date[i]), s.mill[cod][j] if j is not None else None, dl(s.date[j]) if j is not None else None]
    T = {"titolo": "{g} gallons of " + k["nome"] + ", {area}", "sotto": "at {p} per gallon, the EIA average for the week of {data}, before taxes",
         "prima": "the same gallons at the price a year earlier ({p}, {data})", "piu": "more than a year earlier", "meno": "less than a year earlier",
         "uguale": "difference from a year earlier", "errore": "Enter the gallons as a number between 1 and 10,000, for example 200 or 137.5.",
         "nota": "Gallons × the latest official average price, before taxes. It is an average for the whole area, not a quote: the price your supplier charges will differ."}
    gd = k["gal"] * 10
    a = aree[cod_sel]
    c = costo_pieno(gd, a[1])
    G_ = gal_txt(gd)
    i_sel = s.ultimo(cod_sel)
    stat = (f'<div class="ris-main"><span>{G.h(T["titolo"].replace("{g}", G_).replace("{area}", a[0]))}</span>'
            f'<b data-tank-costo data-t="{comb}|{cod_sel}|{s.date[i_sel].isoformat()}|{gd}">{usd_c(c)}</b>'
            f'<span>{G.h(T["sotto"].replace("{p}", p3(a[1])).replace("{data}", a[2]))}</span></div>'
            f'<p class="formula">{G_} gallons × {p3(a[1])} = {usd_c(c)}</p>')
    if a[3]:
        c0 = costo_pieno(gd, a[3])
        d = c - c0
        stat += (f'<ul class="mini due"><li><b data-tank-prima>{usd_c(c0)}</b><span>{G.h(T["prima"].replace("{p}", p3(a[3])).replace("{data}", a[4]))}</span></li>'
                 f'<li><b>{usd_c(abs(d))}</b><span>{G.h(T["piu"] if d > 0 else T["meno"] if d < 0 else T["uguale"])}</span></li></ul>')
    stat += f'<p class="small">{G.h(T["nota"])}</p>'
    opz = "".join(f'<option value="{cod}"{" selected" if cod == cod_sel else ""}>{G.h(nome)}</option>' for nome, cod in elenco)
    chips = "".join(f'<button type="button" data-g="{g}">{g} gal</button>' for g in k["chips"])
    form = f"""<form class="calc-in" data-tank novalidate>
<label><span class="lab">Gallons to be delivered</span><input type="text" name="g" inputmode="decimal" autocomplete="off" value="{k['gal']}" aria-label="Gallons to be delivered"></label>
<div class="chips" role="group" aria-label="Common amounts">{chips}</div>
<label><span class="lab">State</span><select name="s">{opz}</select></label>
</form>"""
    js = json.dumps({"comb": comb, "aree": aree, "t": T}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return (f'<section class="card calc" id="tank"><div class="calc-h"><h2>{G.ico("calc")}Cost to fill a tank: {k["nome"]}</h2>'
            f'<span class="pill">Week of {db(s.ultima)}</span></div><div class="calc-g">{form}<div class="calc-out" data-tank-out aria-live="polite">{stat}</div></div>'
            f'<p class="calc-f">Formula: gallons × the latest EIA average residential price for the state, rounded to the cent. Enter the gallons on your '
            f'delivery quote or ticket, not the size of the tank. Runs in your browser; nothing you type is sent anywhere.</p></section>'
            f'<script type="application/json" id="tank-dati">{js}</script>')


def nota_dati(G, comb):
    k, f = COMB[comb], G.FONTI["eia_definizioni"]["cerca"]
    s = SR[comb]
    mensili = ("From April through September the EIA collects one price a month, on the second Monday, instead of one a week; those monthly prices "
               "are not part of the winter averages or of the weekly tables on this page.")
    if IN_STAGIONE:
        agg = (f"The EIA collects these prices every Monday from October through March and publishes them the same week. This page shows the release of "
               f"{dl(s.uscita)}; the next release is scheduled for {dl(s.prossima)}. We download the new file after each release and update the page once our "
               f"checks pass. {mensili}")
    elif FUORI:
        agg = (f"The EIA collects these prices every week only from October through March. {mensili} The latest price on this page is the monthly "
               f"price for {dl(s.ultima)}, from the EIA release of {dl(s.uscita)}. Weekly prices start again in October.")
    else:
        agg = (f"The EIA collects these prices every week only from October through March. The figures here are from the last weekly release we read "
               f"({dl(s.uscita)}). {mensili} Weekly prices start again in October.")
    return ('<h2 id="about-the-data">What these prices are</h2><div class="testo">'
            f'<p>The figures come from the <strong>Weekly Heating Oil and Propane Prices</strong> of the U.S. Energy Information Administration (EIA), '
            f'collected with the state energy offices (State Heating Oil and Propane Program). The EIA defines the residential {k["nome"]} price as:</p></div>'
            f'<blockquote class="citaz">“{G.h(f[k["def"]])}.”<cite><a href="{G.h(G.FONTI["eia_definizioni"]["url"])}" rel="noopener">EIA, definitions, sources and '
            'explanatory notes</a></cite></blockquote>'
            '<div class="testo"><ul>'
            '<li><strong>Taxes are not included.</strong> The EIA table is headed “Dollars per Gallon Excluding Taxes”.</li>'
            '<li><strong>It is an average for a whole state</strong>, for one day (Monday) of each week. It is not the price of any supplier, town or '
            'contract.</li>'
            f'<li><strong>Revisions.</strong> The EIA notes: “{G.h(f["revisioni"])}.” When that happens the figures here change with the next update.</li>'
            '<li><strong>Averages per winter</strong> on this page are our own calculation: the simple average of the weekly prices published for the '
            'heating season (October to March). The EIA does not publish them.</li></ul>'
            f'<p><strong>Updates.</strong> {agg}</p></div>')


DISCL = ("<strong>General information, not financial or investment advice and not a price quote.</strong> The figures are average residential prices "
         "published by the U.S. Energy Information Administration (EIA) for a whole state, excluding taxes. The price you are offered depends on your "
         "supplier, your town, the amount delivered and your contract. We do not sell fuel, we do not list or rate suppliers and we do not say when to buy.")


def fonti(G, comb):
    return G.fonti_box([f"eia_{comb}_xls", COMB[comb]["tab"], "eia_update", "eia_definizioni", "eia_riuso"],
                       piede=("Every price comes from the EIA files above. During the heating season (October to March) we download them again after each "
                              'weekly release and check them before the pages change (<a href="/how-we-check/">how we check</a>).'))


def stats(voci):
    return '<div class="card stats">' + "".join(f'<div class="stat{" main" if i == 0 else ""}">{b}<span>{s}</span></div>' for i, (b, s) in enumerate(voci)) + "</div>"


def riassunto(G, comb, cod, dove):
    """Frase d'apertura e quattro numeri: ultima settimana, settimana prima, anno prima, media dell'inverno."""
    s, k = SR[comb], COMB[comb]
    i = s.ultimo(cod)
    w, y = s.sett_prima(cod, i), s.anno_prima(cod, i)
    t = (f'<div class="card risposta pull"><p>The average residential {k["nome"]} price {dove} was<span class="big">{pz(comb, cod, i)} per gallon</span>'
         f'on Monday, {dl(s.date[i])}, excluding taxes, in the {"weekly" if stagione(s.date[i]) is not None else "monthly off-season"} survey of the '
         'U.S. Energy Information Administration.')
    if w is not None:
        t += f' A week earlier it was {pz(comb, cod, w)} (change {diff(comb, cod, i, w)}, {var(comb, cod, i, w)}).'
    if y is not None:
        t += f' A year earlier, on {dl(s.date[y])}, it was {pz(comb, cod, y)} (change {diff(comb, cod, i, y)}, {var(comb, cod, i, y)}).'
    t += "</p></div>"
    voci = [(pz(comb, cod, i, "b"), f"per gallon, week of {db(s.date[i])}")]
    if y is not None:
        voci.append((var(comb, cod, i, y, "b"), f"change from a year earlier ({db(s.date[y])})"))
    cp = coppie(comb, cod, STAG)
    if cp:
        n = len(cp)
        voci.append((med_coppie(comb, cod, STAG, "cur", "b"), f"average of the {n} weeks of winter {nome_stagione(STAG)}" + (" so far" if IN_STAGIONE else "")))
        voci.append((med_coppie(comb, cod, STAG, "prev", "b"), "average of the same weeks a year earlier"))
    elif STAG in s.stagioni(cod):
        voci.append((med(comb, cod, STAG, "b"), f"average of winter {nome_stagione(STAG)}" + (" so far" if IN_STAGIONE else "")))
    return t + stats(voci[:4])


# ---------------------------------------------------------------- pagina di uno Stato
def pagina_stato(G, comb, cod, nome, con_pagina):
    s, k = SR[comb], COMB[comb]
    i = s.ultimo(cod)
    y = s.anno_prima(cod, i)
    st = s.stagioni(cod)
    primo = min(st)
    corpo = riassunto(G, comb, cod, f"in {nome}") + G.AD
    corpo += (f'<h2>{nome} {k["nome"]} prices this winter and last winter</h2><p>Weekly average price in {nome}, dollars per gallon excluding taxes. Each week of '
              f'winter {nome_stagione(STAG)} is next to the week 52 weeks before it. The highlighted row is the latest week published.</p>')
    corpo += graf_inverni(G, comb, cod, f"Weekly {k['nome']} price in {nome}, winter {nome_stagione(STAG)} compared with winter {nome_stagione(STAG - 1)}",
                          f"Dollars per gallon, excluding taxes; the vertical axis does not start at zero. Solid line: winter {nome_stagione(STAG)}"
                          f"{' so far' if IN_STAGIONE else ''}. Dashed line: winter {nome_stagione(STAG - 1)}. Source: EIA.")
    corpo += tabella_settimane(G, comb, cod)
    corpo += '<div style="margin-top:28px">' + calcolatore(G, comb, cod) + "</div>"
    corpo += (f'<h2>{nome} {k["nome"]} price history, winters {nome_stagione(primo)} to {nome_stagione(max(st))}</h2><p>One row per heating season (October to March) since the EIA series for '
              f'{nome} starts: the average of the weekly prices, the lowest and the highest week. '
              + ('Until the winter of 1999–2000 the survey was mostly every two weeks, so those winters have fewer prices. ' if primo < 2000 else '') +
              'Amounts are in the dollars of the time, not adjusted for inflation.</p>')
    corpo += graf_storia(G, comb, cod, nome) + tabella_stagioni(G, comb, cod)
    us = s.ultimo("NUS")
    corpo += (f'<p class="small">For comparison, the U.S. average for the week of {db(s.date[us])} was {pz(comb, "NUS", us)}. '
              f'<a href="/{k["slug"]}#in-todays-dollars">U.S. winter averages in today’s dollars</a> (adjusted with the Consumer Price Index) are on the '
              f'{k["nome"]} overview page.</p>')
    corpo += nota_dati(G, comb)
    # altri Stati e l'altro combustibile
    altro = "propane" if comb == "oil" else "oil"
    li = ""
    if (altro, nome) in con_pagina:
        j = SR[altro].ultimo(con_pagina[(altro, nome)])
        li += (f'<li><a href="/{percorso(altro, nome)}"><b>{pz(altro, con_pagina[(altro, nome)], j)}</b>{COMB[altro]["Nome"]} in {G.h(nome)}'
               f'<small>Week of {db(SR[altro].date[j])}</small></a></li>')
    li += f'<li><a href="/{k["slug"]}"><b>{pz(comb, "NUS", us)}</b>U.S. average and all states<small>{k["Nome"]} prices by state</small></a></li>'
    for (c2, n2), cod2 in sorted(con_pagina.items(), key=lambda x: x[0][1]):
        if c2 == comb and n2 != nome:
            j = s.ultimo(cod2)
            li += f'<li><a href="/{percorso(comb, n2)}"><b>{pz(comb, cod2, j)}</b>{G.h(n2)}<small>Week of {db(s.date[j])}</small></a></li>'
    corpo += f'<h2>{k["Nome"]} prices in other states</h2><ul class="griglia">{li}</ul>'
    corpo += fonti(G, comb)
    titolo = f'{nome} {k["Tit"]} Prices: {p3(s.mill[cod][i])}/Gallon, {db(s.date[i])}'
    if y is not None:
        r = perc10(s.mill[cod][i], s.mill[cod][y])
        cambio = f"{abs(r) / 10:.1f}% {'higher' if r > 0 else 'lower'} than" if r else "the same as"
        descr = (f"Official EIA weekly {k['nome']} price for {nome}: {p3(s.mill[cod][i])} per gallon on {db(s.date[i])}, {cambio} a year earlier. "
                 "Chart, winter averages, tank cost.")
    else:
        descr = (f"Official EIA weekly {k['nome']} price for {nome}: {p3(s.mill[cod][i])} per gallon on {db(s.date[i])}, excluding taxes. "
                 "Weekly chart, winter averages and tank cost.")
    if len(descr) > 160:  # nomi e variazioni lunghi: l'ultima frase si accorcia
        descr = descr[:descr.rindex(". ") + 2] + "Chart and winter averages."
    testata = G.banda(f"{k['Nome']} · {SIGLE[nome]}", f"{k['Nome']} prices in {nome}",
                      f"The official weekly average from the U.S. Energy Information Administration: <strong>{pz(comb, cod, i)} per gallon</strong> "
                      f"in the week of {dl(s.date[i])}, with last winter, the history since {primo} and the cost of a delivery.",
                      G.trust([("check", "Official EIA weekly survey"), ("calendar", f"Week of {db(s.date[i])}"), ("info", "No suppliers, no advice")]), icona="trend")
    G.pagina(percorso(comb, nome), titolo, descr, corpo, testata, "us",
             briciole=[("Home", ""), (f"{k['Nome']} prices", k["slug"]), (nome, percorso(comb, nome))], disclaimer=DISCL, script=G.TANK_SCRIPT)


# ---------------------------------------------------------------- indice di un combustibile
def tabella_stati(G, comb, con_pagina):
    s = SR[comb]
    us = s.ultimo("NUS")

    def riga(nome, cod, link):
        i = s.ultimo(cod)
        w, y = s.sett_prima(cod, i), s.anno_prima(cod, i)
        n = f'<a href="/{percorso(comb, nome)}">{G.h(nome)}</a>' if link else G.h(nome)
        data = "" if s.date[i] == s.date[us] else f' <span class="small">({db(s.date[i])})</span>'
        t = f'<tr{" class=\"evid\"" if cod == "NUS" else ""}><td class="area">{n}{data}</td>{pz(comb, cod, i, "td", "n")}'
        t += pz(comb, cod, w, "td", "n") if w is not None else vuota()
        t += (pz(comb, cod, y, "td", "n") + diff(comb, cod, i, y, "td", "n") + var(comb, cod, i, y, "td", "n")) if y is not None else vuota() * 3
        t += med(comb, cod, STAG, "td", "n") if STAG in s.stagioni(cod) else vuota()
        return t + "</tr>"
    corpo = riga("U.S. average", "NUS", False) + "".join(riga(nome, cod, (comb, nome) in con_pagina) for nome, cod in stati_attivi(comb))
    testa = (f'<thead><tr><th scope="col">State</th><th scope="col" class="n">{db(s.date[us])}</th><th scope="col" class="n">Week earlier</th>'
             f'<th scope="col" class="n">Year earlier</th><th scope="col" class="n">Change</th><th scope="col" class="n">Change %</th>'
             f'<th scope="col" class="n">Winter {nome_stagione(STAG)}{" so far" if IN_STAGIONE else ""}</th></tr></thead>')
    regioni = "".join(riga(a["nome"], cod, False)
                      for cod, a in s.aree.items() if a["tipo"] == "padd" and s.attiva(cod))
    return (f'<div class="tab fissa"><table class="dati">{testa}<tbody>{corpo}</tbody></table></div>'
            f'<h3>By region</h3><p class="small">The EIA groups states into Petroleum Administration for Defense Districts (PADD).</p>'
            f'<div class="tab fissa"><table class="dati">{testa.replace(">State<", ">Region<")}<tbody>{regioni}</tbody></table></div>')


def serie_finite(comb):
    """Frase sugli Stati che l'EIA non rileva più (serie nel file storico senza un prezzo nelle ultime tre settimane): nome e data dell'ultimo prezzo."""
    s = SR[comb]
    finite = sorted((a["nome"], s.date[s.ultimo(cod)]) for cod, a in s.aree.items() if a["tipo"] == "stato" and not s.attiva(cod) and s.ultimo(cod) is not None)
    if not finite:
        return ""
    voci = [f"{'the ' if nome.startswith('District') else ''}{nome} (last price: {dl(d)})" for nome, d in finite]
    elenco = voci[0] if len(voci) == 1 else ", ".join(voci[:-1]) + " and " + voci[-1]
    n = len(stati_attivi(comb))
    return (f'<p class="small">The EIA history file also contains {"one series that has" if len(voci) == 1 else f"{len(voci)} series that have"} ended: {elenco}. '
            f'{"It is" if len(voci) == 1 else "They are"} not counted among the {n} states and {"is" if len(voci) == 1 else "are"} not shown in the tables on this page.</p>')


def oggi_in_dollari(G, comb):
    """Medie nazionali per inverno, nei dollari di allora e in quelli dell'ultimo mese del CPI-U (calcolo dichiarato, con il link al calcolatore)."""
    s, k = SR[comb], COMB[comb]
    st = s.stagioni("NUS")
    m = G.S["us"]["mensile"]
    righe, esempio = "", None
    for a in sorted(st, reverse=True):
        mill = media([s.mill["NUS"][i] for i in st[a]])
        v = cpi_valore(G, mill, a)
        if v is None:
            continue
        righe += (f'<tr><td class="nw">{nome_stagione(a)}</td>{med(comb, "NUS", a, "td", "n")}<td class="n">{m[(a + 1, 1)]:.3f}</td>'
                  f'{el("cpi", f"{comb}|NUS|{a}", f"${v:.2f}", "td", "n")}</tr>')
        esempio = (a, mill, v)
    a, mill, v = esempio  # il primo inverno della serie
    ult = G.US_ULT_TXT
    return (f'<h2 id="in-todays-dollars">What {k["nome"]} cost in past winters, in today’s dollars</h2><div class="testo">'
            f'<p>The table converts the U.S. average of each winter into {ult} dollars with the Consumer Price Index for All Urban Consumers (CPI-U, all items), '
            f'the same index as our <a href="/">inflation calculator</a>. Formula: winter average × CPI-U of {ult} ({m[G.US_LU]:.3f}) ÷ CPI-U of the January '
            f'of that winter. Example: {med(comb, "NUS", a)} in the winter of {nome_stagione(a)} × {m[G.US_LU]:.3f} ÷ {m[(a + 1, 1)]:.3f} = {el("cpi", f"{comb}|NUS|{a}", f"${v:.2f}")} '
            f'(<a href="/?a={mill / 1000:.3f}&amp;f={a + 1}-1">open this example in the calculator</a>).</p>'
            f'<p><strong>What this does and does not show.</strong> The CPI-U measures the prices of everything households buy, not of {k["nome"]}. The adjusted '
            f'column therefore says how much general purchasing power a gallon cost in that winter; it is not an official “real” {k["nome"]} price and not a '
            f'forecast. The winter in progress is not in the table because the CPI-U for its January is not published yet.</p></div>'
            f'<div class="tab alta"><table class="dati stretta"><thead><tr><th scope="col">Winter</th><th scope="col" class="n">U.S. average, dollars of the time</th>'
            f'<th scope="col" class="n">CPI-U, January</th><th scope="col" class="n">In {ult} dollars</th></tr></thead><tbody>{righe}</tbody></table></div>')


def faq_indice(G, comb):
    s, k = SR[comb], COMB[comb]
    us = s.ultimo("NUS")
    d = s.date[us]
    sondaggio = "weekly" if stagione(d) is not None else "monthly off-season"
    stati = [(s.mill[cod][s.ultimo(cod)], nome, cod) for nome, cod in stati_attivi(comb) if s.ultimo(cod) == us]
    lo, hi = min(stati), max(stati)
    y = s.anno_prima("NUS", us)
    g1, g2 = k["faq_gal"]
    costo = lambda g: el("t", f"{comb}|NUS|{d.isoformat()}|{g * 10}", usd_c(costo_pieno(g * 10, s.mill["NUS"][us])))  # noqa: E731
    cp = coppie(comb, "NUS", STAG)
    q = {"oil": [("How much is heating oil per gallon?", "how much is heating oil per gallon"), ("What are heating oil prices today?", "heating oil prices today"),
                 ("How much does it cost to fill an oil tank?", "cost to fill oil tank"), ("What is the average heating oil price?", "average heating oil price")],
         "propane": [("How much is propane per gallon?", "how much is propane per gallon"), ("What are current propane prices?", "current propane prices"),
                     ("How much does it cost to fill a 500 gallon propane tank?", "cost to fill 500 gallon propane tank"),
                     ("What is the average propane price?", "average propane price")]}[comb]
    r = [
        (f'The U.S. average residential {k["nome"]} price was {pz(comb, "NUS", us)} per gallon on {dl(d)}, excluding taxes, in the {sondaggio} survey of the U.S. '
         f'Energy Information Administration (EIA). Among the {len(stati)} states surveyed that week, the state averages ranged from {pz(comb, lo[2], us)} in '
         f'{lo[1]} to {pz(comb, hi[2], us)} in {hi[1]}.'),
        (f'The EIA publishes one average price per week, for Monday; it does not publish a daily price. The latest is for {dl(d)}: {pz(comb, "NUS", us)} per gallon '
         f'for the U.S., released on {dl(s.uscita)}. ' + (f'The next release is scheduled for {dl(s.prossima)}. ' if IN_STAGIONE else
                                                         'Weekly prices are collected from October through March; from April through September the EIA '
                                                         'collects one price a month. ') +
         'The table on this page has the latest price for each state.'),
        (f'Multiply the gallons delivered by the price per gallon. At the latest U.S. average of {pz(comb, "NUS", us)} per gallon, {g1} gallons cost {costo(g1)} and {g2} '
         f'gallons cost {costo(g2)} before taxes. '
         + ('The size of a tank, 500 gallons for example, is not the amount delivered: the gallons to multiply are those on the supplier’s quote or ticket. '
            if comb == "propane" else 'The gallons delivered are those on the supplier’s quote or ticket, not the size of the tank. ') +
         'The calculator on this page does the same sum with the average price of each state.'),
        ((f'Over the {len(cp)} weeks of the winter of {nome_stagione(STAG)} published' + (' so far' if IN_STAGIONE else '') +
          f', the U.S. residential {k["nome"]} price averaged {med_coppie(comb, "NUS", STAG, "cur")} per gallon, against '
          f'{med_coppie(comb, "NUS", STAG, "prev")} in the same weeks a year earlier. ') if cp else '') +
        f'For the whole winter of {nome_stagione(STAG - 1)} (October to March) the average of the weekly prices was {med(comb, "NUS", STAG - 1)} per gallon. These averages '
        'are our own calculation from the weekly EIA prices, which exclude taxes.',
    ]
    return G.faq_blocco(k["slug"].strip("/"), [(dq, risposta, frase, "us") for (dq, frase), risposta in zip(q, r)])


def pagina_indice(G, comb, con_pagina):
    s, k = SR[comb], COMB[comb]
    us = s.ultimo("NUS")
    y = s.anno_prima("NUS", us)
    n_stati = len(stati_attivi(comb))
    primo = min(s.stagioni("NUS"))
    corpo = riassunto(G, comb, "NUS", "in the United States") + G.AD
    corpo += (f'<h2 id="states">{k["Nome"]} prices by state, week of {dl(s.date[us])}</h2><p>Average residential price in each of the {n_stati} states in the EIA '
              f'survey, dollars per gallon excluding taxes: the latest week, the week before, the week 52 weeks earlier and the average of the weekly prices of '
              f'winter {nome_stagione(STAG)}{" so far" if IN_STAGIONE else ""}. States with a link have their own page with the weekly history.</p>')
    corpo += tabella_stati(G, comb, con_pagina) + serie_finite(comb)
    corpo += (f'<h2>U.S. {k["nome"]} price this winter and last winter</h2>'
              + graf_inverni(G, comb, "NUS", f"Weekly U.S. average {k['nome']} price, winter {nome_stagione(STAG)} compared with winter {nome_stagione(STAG - 1)}",
                             f"U.S. average, dollars per gallon, excluding taxes; the vertical axis does not start at zero. Solid line: winter {nome_stagione(STAG)}"
                             f"{' so far' if IN_STAGIONE else ''}. Dashed line: winter {nome_stagione(STAG - 1)}. Source: EIA.")
              + tabella_settimane(G, comb, "NUS"))
    corpo += '<div style="margin-top:28px">' + calcolatore(G, comb, "NUS") + "</div>"
    corpo += (f'<h2>U.S. {k["nome"]} price history, winters {nome_stagione(primo)} to {nome_stagione(max(s.stagioni("NUS")))}</h2><p>One row per heating season (October to March): the average of '
              'the weekly U.S. prices, the lowest and the highest week. Until the winter of 1999–2000 the survey was mostly every two weeks, so those winters have fewer prices. '
              'Amounts are in the dollars of the time.</p>')
    corpo += graf_storia(G, comb, "NUS", "United States") + tabella_stagioni(G, comb, "NUS")
    corpo += oggi_in_dollari(G, comb)
    corpo += nota_dati(G, comb)
    altro = "propane" if comb == "oil" else "oil"
    ua = SR[altro].ultimo("NUS")
    corpo += (f'<h2>More</h2><ul class="griglia"><li><a href="/{COMB[altro]["slug"]}"><b>{pz(altro, "NUS", ua)}</b>{COMB[altro]["Nome"]} prices by state'
              f'<small>U.S. average, week of {db(SR[altro].date[ua])}</small></a></li>'
              '<li><a href="/"><b>CPI</b>US inflation calculator<small>What a past amount is worth today</small></a></li>'
              '<li><a href="/us/inflation-rate-by-year/"><b>%</b>US inflation rate by year<small>Every year since 1914</small></a></li></ul>')
    faq, ld = faq_indice(G, comb)
    corpo += faq + fonti(G, comb)
    titolo = f'{k["Tit"]} Prices by State: {p3(s.mill["NUS"][us])}/Gallon, {db(s.date[us])}'
    descr = (f"Official EIA residential {k['nome']} prices for the U.S. and {n_stati} states: {p3(s.mill['NUS'][us])} per gallon on {db(s.date[us])}. "
             f"Weekly table, year-ago change, history since {primo}.")
    testata = G.banda(f"{k['Nome']} · United States", f"{k['Nome']} prices by state",
                      f"Official weekly residential prices from the U.S. Energy Information Administration for the U.S. and {n_stati} states: "
                      f"<strong>{pz(comb, 'NUS', us)} per gallon</strong> in the week of {dl(s.date[us])}, with last winter and the history since {primo}.",
                      G.trust([("check", "Official EIA weekly survey"), ("calendar", f"Week of {db(s.date[us])}"), ("info", "No suppliers, no advice")]), icona="trend")
    G.pagina(k["slug"], titolo, descr, corpo, testata, "us", briciole=[("Home", ""), (f"{k['Nome']} prices", k["slug"])],
             jsonld=[ld] if ld else None, disclaimer=DISCL, script=G.TANK_SCRIPT)


def genera(G):
    ps = pagine_stato(G)
    con_pagina = {(comb, nome): cod for comb, cod, nome, _, _ in ps}
    for p in [k["slug"] for k in COMB.values()] + [percorso(comb, nome) for comb, _, nome, _, _ in ps]:
        G.LASTMOD[p] = LETTO.isoformat()  # sitemap: queste pagine cambiano a ogni lettura dell'EIA, non con gli indici mensili
    for comb in COMB:
        pagina_indice(G, comb, con_pagina)
    for comb, cod, nome, _, _ in ps:
        pagina_stato(G, comb, cod, nome, con_pagina)
    return ps
