"""Sezione «Rent increase cap» (/rent-increase-cap/…): tetto legale all'aumento dell'affitto per luogo e periodo, con calcolatore.

Dati: dati/affitti.json (tetti in millesimi di punto percentuale; ogni periodo con la fonte ufficiale e la frase da cui viene; testi
in dati/grezzi/regole2027/, scaricati da raccolta/regole2027.py). Una pagina per luogo solo con una frase misurata ≥ 100 ricerche al
mese (dati/domanda.json, gruppo affitti, 18/11/2026):
  /rent-increase-cap/                    indice + calcolatore                    («how much can a landlord raise rent» 1.900, «rent increase calculator» 1.600)
  /rent-increase-cap/california/         AB 1482 per zona + tetti locali          («how much can a landlord raise rent in california» 3.600, «ab 1482» 3.600)
  /rent-increase-cap/new-york-city/      ordine del Rent Guidelines Board         («rent guidelines board» 2.400, «nyc rent increase» 1.300)
  /rent-increase-cap/washington/         HB 1217                                  («hb 1217» 880, «washington state rent control» 720)
  /rent-increase-cap/oregon/             ORS 90.324                               («oregon rent increase 2025» 320, «oregon rent control» 210)
  /rent-increase-cap/ontario/            guideline annuale                        («rent control ontario» 2.900 ca, «rent increase ontario» 1.900 ca)
  /rent-increase-cap/british-columbia/   limite annuale                           («bc rent increase» 2.900 ca)
  /rent-increase-cap/saint-paul/         3 % fisso                                («st paul rent control» 260)
Solo cifre lette sulla pagina ufficiale; dove la pagina di una città non si legge (Los Angeles, San José, San Francisco) la cifra è
quella della tabella dell'Attorney General della California, e la pagina lo dice. Nessun consiglio legale.
"""
import json
import re
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent
D = json.loads((RADICE / "dati" / "affitti.json").read_text(encoding="utf-8"))
L = {x["id"]: x for x in D["luoghi"]}
ORDINE = ["california", "nyc", "washington", "oregon", "ontario", "bc", "stpaul"]
BASE = "rent-increase-cap/"
SOGLIA = 100
# frase misurata che giustifica la pagina di ogni luogo (verifica.py controlla che in dati/domanda.json valga almeno SOGLIA)
DOMANDA_PAGINA = {"california": ("how much can a landlord raise rent in california", "us"), "nyc": ("rent guidelines board", "us"),
                  "washington": ("hb 1217", "us"), "oregon": ("oregon rent control", "us"), "ontario": ("rent control ontario", "ca"),
                  "bc": ("bc rent increase", "ca"), "stpaul": ("st paul rent control", "us")}
MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
MESI_CSV = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

DISCL = ("<strong>General information, not legal advice, and not financial or investment advice.</strong> The percentages are the limits "
         "published by the state, province or city on the official page linked next to each figure. Whether a limit applies to a home depends on "
         "exemptions, local rules and facts that are not on this page, and a city can set a lower limit than its state. The calculator multiplies the "
         "rent you enter by the published percentage: it does not tell you whether an increase is lawful. This is an independent site, not a "
         "government website. For your own case use the official page, the local rent board or housing agency, or a lawyer or legal aid service.")


def percorso(lid):
    return BASE + L[lid]["slug"] + "/"


# ---------------------------------------------------------------- conti (stile.RENT_MOTORE_JS è la copia)
def aumento(affitto_c, tetto_m):
    """Aumento massimo e affitto massimo in centesimi: affitto × tetto, arrotondato per difetto al centesimo (mai sopra il tetto)."""
    a = affitto_c * tetto_m // 100000
    return a, affitto_c + a


def cpi_variazione(prima_m, dopo_m):
    """Variazione di un indice (in millesimi) arrotondata a un decimo di punto, in decimi (mezzo decimo per eccesso)."""
    return (2 * (dopo_m - prima_m) * 1000 + prima_m) // (2 * prima_m)


# ---------------------------------------------------------------- formati
def pc(t):
    s = f"{t / 1000:.3f}".rstrip("0").rstrip(".")
    return s + "%"


def soldi(c):
    return f"${c // 100:,}.{c % 100:02d}"


def giorno(iso, anno=True):
    d = date.fromisoformat(iso)
    return f"{d.day} {MESI[d.month - 1]}" + (f" {d.year}" if anno else "")


def periodo_txt(p):
    if not p["da"]:
        return p["etichetta"]
    da, a = date.fromisoformat(p["da"]), date.fromisoformat(p["a"])
    if (da.month, da.day, a.month, a.day) == (1, 1, 12, 31) and da.year == a.year:
        return f"{da.year}"
    return f"{giorno(p['da'])} – {giorno(p['a'])}"


def periodo_breve(p):
    if not p["da"]:
        return "any 12 months"
    da, a = date.fromisoformat(p["da"]), date.fromisoformat(p["a"])
    if (da.month, da.day, a.month, a.day) == (1, 1, 12, 31) and da.year == a.year:
        return f"{da.year}"
    return f"{MESI[da.month - 1][:3]} {da.year} – {MESI[a.month - 1][:3]} {a.year}"


def ultimo(v):
    return v["periodi"][-1]


def pulita(frase):
    """La frase come si stampa: uguale a quella registrata, senza lo spazio che l'estrazione del testo lascia prima della punteggiatura."""
    return re.sub(r"\s+([.,:;])", r"\1", frase)


def fonte_link(G, fid):
    f = G.FONTI[fid]
    return f'<a href="{G.h(f["url"])}" rel="noopener">{G.h(f["chi"])}, “{G.h(f["titolo"])}”</a>'


def quando(G, fid):
    f = G.FONTI[fid]
    return (f'dated {f["pubblicato"]} · ' if f.get("pubblicato") else "") + f'read on {G.data_lunga(f["letto_il"])}'


def citaz(G, x, prima=""):
    return f'<blockquote class="citaz">{prima}“{G.h(pulita(x["frase"]))}”<cite>{fonte_link(G, x["fonte"])} · {quando(G, x["fonte"])}</cite></blockquote>'


def tt(G, lid, k):
    return citaz(G, L[lid]["testi"][k])


def cella(k, i, campo, testo, cls="n"):
    return f'<td class="{cls}" data-rent="{k}|{i}|{campo}">{testo}</td>'


def stats(G, voci):
    return '<div class="card stats">' + "".join(f'<div class="stat{" main" if i == 0 else ""}"><b>{b}</b><span>{G.h(s)}</span></div>' for i, (b, s) in enumerate(voci)) + "</div>"


def faq(G, pid, voci):
    return G.faq_blocco(pid, [(q, a, ricerca, paese) for q, a, ricerca, paese in voci])


# ---------------------------------------------------------------- indici per rifare i tetti (California) e il conto di Washington
def _csv(fid):
    import csv
    with open(RADICE / "dati" / G_FONTI[fid]["file"], encoding="utf-8") as f:
        return {int(r["year"]): r for r in csv.DictReader(f)}


G_FONTI = json.loads((RADICE / "dati" / "fonti.json").read_text(encoding="utf-8"))


def indice(fid, anno, mese):
    """Valore pubblicato di un indice regionale, in millesimi interi (stringa esatta della fonte); None se quel mese non c'è."""
    if fid == "rent_ca_dir":
        x = L["california"]["cpi_dir"].get(str(anno))
        return (int(x["valore"].replace(".", "")), x["valore"]) if x else None
    s = _csv(fid).get(anno, {}).get(mese, "")
    try:
        float(s)
    except ValueError:
        return None
    intero, _, dec = s.partition(".")
    return int(intero) * 1000 + int((dec + "000")[:3]), s


def california_conto(v, anno):
    """Tetto rifatto da noi per gli aumenti dal 1° agosto di «anno»: 5 % + variazione dell'indice (aprile o marzo su un anno prima), massimo 10 %."""
    c = v["cpi"]
    a, b = indice(c["fonte"], anno - 1, c["mese"]), indice(c["fonte"], anno, c["mese"])
    if not a or not b:
        return None
    var = cpi_variazione(a[0], b[0])
    return {"prima": a[1], "dopo": b[1], "var": var, "tetto": min(5000 + var * 100, 10000)}


# ---------------------------------------------------------------- calcolatore
def calcolatore(G, lid=None):
    """Affitto massimo = affitto × (1 + tetto pubblicato). lid = solo le voci di quel luogo; None = tutti i luoghi."""
    luoghi = [lid] if lid else ORDINE
    voci, gruppi = {}, ""
    for i in luoghi:
        x = L[i]
        opz = ""
        for v in x["voci"]:
            nome = v["nome"] if len(x["voci"]) == 1 else f'{x["nome"].split(" (")[0]}: {v["nome"]}'
            voci[v["k"]] = {"n": nome, "c": "Canadian dollars" if x["valuta"] == "CAD" else "US dollars", "f": G.FONTI[ultimo(v)["fonte"]]["chi"],
                            "p": [[periodo_txt(p), p["tetto"]] for p in v["periodi"]], "d": len(v["periodi"]) - 1}
            opz += f'<option value="{v["k"]}">{G.h(v["nome"] if len(x["voci"]) > 1 else x["nome"])}</option>'
        gruppi += f'<optgroup label="{G.h(x["nome"])}">{opz}</optgroup>' if len(x["voci"]) > 1 or not lid else opz
    k0 = L[luoghi[0]]["voci"][0]["k"]
    v0 = voci[k0]
    T = {"titolo": "Highest new rent under the cap, {luogo}", "sotto": "{pct} cap for {periodo}, in {valuta}", "zero": "0% for {periodo}: no increase under this guideline",
         "aumento": "highest increase a month", "fonte": "published by {fonte}", "errore": "Enter the current monthly rent as a number, for example 1850 or 1,850.50.",
         "nota": "Rent × the published percentage, rounded down to the cent. It assumes the cap applies to the home and that no lower local limit or exemption applies."}
    r0 = 200000
    p0 = v0["p"][v0["d"]]
    a, n = aumento(r0, p0[1])
    stat = (f'<div class="ris-main"><span>{G.h(T["titolo"].replace("{luogo}", v0["n"]))}</span><b data-rent-nuovo>{soldi(n)}</b>'
            f'<span>{G.h((T["sotto"] if p0[1] else T["zero"]).replace("{pct}", pc(p0[1])).replace("{periodo}", p0[0]).replace("{valuta}", v0["c"]))}</span></div>'
            f'<p class="formula">{soldi(r0)} × {pc(p0[1])} = {soldi(a)} · {soldi(r0)} + {soldi(a)} = {soldi(n)}</p>'
            f'<ul class="mini due"><li><b data-rent-aumento>{soldi(a)}</b><span>{G.h(T["aumento"])}</span></li>'
            f'<li><b data-rent-pct>{pc(p0[1])}</b><span>{G.h(T["fonte"].replace("{fonte}", v0["f"]))}</span></li></ul><p class="small">{G.h(T["nota"])}</p>')
    per_opz = "".join(f'<option value="{i}"{" selected" if i == v0["d"] else ""}>{G.h(p[0])}</option>' for i, p in enumerate(v0["p"]))
    form = f"""<form class="calc-in" data-rent novalidate>
<label><span class="lab">Where the home is</span><select name="v">{gruppi}</select></label>
<label><span class="lab">When the increase (or the lease) starts</span><select name="p">{per_opz}</select></label>
<label><span class="lab">Current monthly rent</span><input type="text" name="r" inputmode="decimal" autocomplete="off" value="2,000" aria-label="Current monthly rent"></label>
</form>"""
    js = json.dumps({"voci": voci, "t": T}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return (f'<section class="card calc" id="rent"><div class="calc-h"><h2>{G.ico("calc")}Maximum new rent calculator</h2><span class="pill">Official caps</span></div>'
            f'<div class="calc-g">{form}<div class="calc-out" data-rent-out aria-live="polite">{stat}</div></div>'
            f'<p class="calc-f">Formula: current rent × the percentage published for the place and period, rounded down to the cent, added to the rent. '
            f'Runs in your browser; nothing you type is sent anywhere.</p></section>'
            f'<script type="application/json" id="rent-dati">{js}</script>')


def tabella_periodi(G, lid):
    x = L[lid]
    th = "".join(f'<th scope="col" class="n">{G.h(periodo_breve(p) if p["da"] else periodo_txt(p))}</th>' for p in x["voci"][0]["periodi"])
    corpo = ""
    for v in x["voci"]:
        corpo += f'<tr><td>{G.h(v["nome"])}</td>' + "".join(cella(v["k"], i, "tetto", pc(p["tetto"])) for i, p in enumerate(v["periodi"])) + "</tr>"
    cosa = {"california": "Area (increase starts)", "nyc": "Lease (commencing)"}.get(lid, "Year the increase takes effect" if x["voci"][0]["periodi"][0]["da"] else "Period")
    contee = "".join(f'<li><strong>{G.h(v["nome"])}:</strong> {G.h(", ".join(v["contee"]))}</li>' for v in x["voci"] if v.get("contee"))
    return (f'<div class="tab"><table class="dati stretta"><thead><tr><th scope="col">{cosa}</th>{th}</tr></thead><tbody>{corpo}</tbody></table></div>'
            + (f'<ul class="testo small">{contee}</ul>' if contee else ""))


def esempi(G, lid):
    """Che cosa vuol dire il tetto su tre affitti tipo (calcolo nostro)."""
    x = L[lid]
    righe = ""
    for v in x["voci"]:
        i = len(v["periodi"]) - 1
        p = v["periodi"][i]
        righe += f'<tr><td>{G.h(v["nome"])}<br><span class="small">{pc(p["tetto"])}, {G.h(periodo_txt(p))}</span></td>' + "".join(
            f'<td class="n" data-rent="{v["k"]}|{i}|max{r}">{soldi(aumento(r * 100, p["tetto"])[1])}<br><span class="small" data-rent="{v["k"]}|{i}|inc{r}">+{soldi(aumento(r * 100, p["tetto"])[0])}</span></td>'
            for r in (1500, 2500, 3500)) + "</tr>"
    return ('<div class="tab fissa c1"><table class="dati"><thead><tr><th scope="col">Current monthly rent</th><th scope="col" class="n">$1,500</th><th scope="col" class="n">$2,500</th>'
            f'<th scope="col" class="n">$3,500</th></tr></thead><tbody>{righe}</tbody></table></div>'
            f'<p class="small">Our own calculation: rent × the published percentage, rounded down to the cent{", in Canadian dollars" if x["valuta"] == "CAD" else ""}. '
            'The highest new rent, and under it the highest increase.</p>')


def frasi_periodi(G, lid, titolo="The official wording for each figure"):
    voci = []
    for v in L[lid]["voci"]:
        for p in v["periodi"]:
            voci.append(citaz(G, p))
    return f'<details class="irs" open><summary>{G.h(titolo)}</summary>{"".join(dict.fromkeys(voci))}</details>'


def altri(G, tranne=None):
    li = ""
    for i in ORDINE:
        if i == tranne:
            continue
        x = L[i]
        v = x["voci"][0]
        li += f'<li><a href="/{percorso(i)}"><b>{pc(ultimo(v)["tetto"])}</b>{G.h(x["breve"])}<small>{G.h(periodo_breve(ultimo(v)))}</small></a></li>'
    if tranne:
        li += f'<li><a href="/{BASE}"><b>All</b>Rent increase caps and calculator<small>Every place on one page</small></a></li>'
    li += '<li><a href="/"><b>CPI</b>US inflation calculator<small>BLS CPI-U, 1913 to today</small></a></li>'
    return f'<h2>{"Other rent increase caps" if tranne else "Each place in detail"}</h2><ul class="griglia">{li}</ul>'


def pubblica(G, perc, titolo, descr, eyebrow, h1, sub, corpo, bc, fonti, jsonld=None, paese="us"):
    corpo += G.fonti_box(fonti, piede=(
        'Every percentage on this page is copied from the official pages above and checked against them before the page changes: each figure must appear in the '
        'quoted official sentence (<a href="/how-we-check/">how we check</a>). We read the pages again when a new figure is due.'))
    testata = G.banda(eyebrow, h1, sub, G.trust([("check", "Figures quoted from official pages"), ("calendar", "2026 and 2027 periods"), ("info", "No legal advice, no products")]), icona="shield")
    G.pagina(perc, titolo, descr, corpo, testata, paese, briciole=[("Home", ""), ("Rent increase caps", BASE)] + ([bc] if bc else []), jsonld=jsonld, disclaimer=DISCL,
             script=G.RENT_SCRIPT)


def intro_stats(G, lid, extra):
    v = L[lid]["voci"][0]
    p1 = ultimo(v)
    voci = [(pc(p1["tetto"]), f'{v["nome"] if len(L[lid]["voci"]) > 1 else "cap"}, {periodo_txt(p1)}')]
    return stats(G, voci + extra)


# ---------------------------------------------------------------- pagine dei luoghi
def p_california(G):
    x = L["california"]
    la = x["voci"][0]
    corpo = '<div class="pull">' + calcolatore(G, "california") + "</div>" + G.AD
    corpo += stats(G, [(pc(ultimo(la)["tetto"]), f'Los Angeles Area, {periodo_txt(ultimo(la))}'), (pc(ultimo(x["voci"][3])["tetto"]), "San Francisco Area"),
                       (pc(ultimo(x["voci"][2])["tetto"]), "San Diego Area"), (pc(ultimo(x["voci"][4])["tetto"]), "all other counties")])
    corpo += ('<h2>California rent increase cap by area</h2>' + tabella_periodi(G, "california")
              + '<div class="testo"><p>The statewide cap comes from the Tenant Protection Act (AB 1482). The California Attorney General states the rule and publishes '
              'the percentage for each area; the cap changes every 1 August:</p>' + citaz(G, x["regola"]) + tt(G, "california", "tabella") + tt(G, "california", "metodo") + "</div>")
    # controllo con gli indici
    righe = ""
    for v in x["voci"]:
        for i, anno in ((0, 2025), (1, 2026)):
            c = california_conto(v, anno)
            if not c:
                continue
            m = MESI[MESI_CSV.index(v["cpi"]["mese"])]
            righe += (f'<tr><td>{G.h(v["nome"])}<br><span class="small">{m} {anno - 1} → {m} {anno}</span></td><td class="n" data-ca="{v["k"]}|{anno}|prima">{c["prima"]}</td>'
                      f'<td class="n" data-ca="{v["k"]}|{anno}|dopo">{c["dopo"]}</td><td class="n" data-ca="{v["k"]}|{anno}|var">{c["var"] / 10:.1f}%</td>'
                      f'<td class="n" data-ca="{v["k"]}|{anno}|tetto">{pc(c["tetto"])}</td>' + cella(v["k"], i, "tetto", pc(v["periodi"][i]["tetto"])) + "</tr>")
    corpo += ('<h2>The same caps recalculated from the price indexes</h2><div class="tab fissa c1"><table class="dati"><thead><tr><th scope="col">Area and months compared</th>'
              '<th scope="col" class="n">Index before</th><th scope="col" class="n">Index after</th><th scope="col" class="n">Change</th><th scope="col" class="n">5% + change</th>'
              '<th scope="col" class="n">Attorney General</th></tr></thead><tbody>' + righe + '</tbody></table></div>'
              '<p class="small">Our own check, not an official calculation: the CPI-U for each metropolitan area from the Bureau of Labor Statistics (April, or March where April '
              'is not published) and, for all other counties, the April California CPI from the Department of Industrial Relations. The change rounded to one decimal place, '
              'plus 5 points, gives the percentage in the Attorney General’s chart in every row.</p>')
    corpo += ('<h2>Which homes the statewide cap covers</h2><div class="testo">' + tt(G, "california", "copre") + tt(G, "california", "nuovo_inquilino")
              + '<p>The notice a landlord must give is set separately:</p>' + citaz(G, x["preavviso"]) + "</div>")
    corpo += '<h2>What the cap means on a monthly rent</h2>' + esempi(G, "california")
    # tetti locali
    loc = D["california_locali"]["righe"]
    r = "".join(f'<tr data-loc="{i}"><td>{G.h(z["comune"])}</td><td>{G.h(z["massimo"])}</td><td>{G.h(z["periodo"] or "–")}</td></tr>' for i, z in enumerate(loc))
    corpo += ('<h2 id="local">Local rent caps in California cities</h2><div class="testo"><p>Many cities and counties have their own, lower limits. The Attorney General lists '
              f'{len(loc)} of them with the percentage each one currently allows. The list below copies the name, the maximum and the dates from that chart; the conditions '
              '(which buildings, banking of increases, exceptions) are in the chart itself and on each city’s page.</p>' + tt(G, "california", "locale") + tt(G, "california", "locale_esenti")
              + f'</div><div class="tab alta"><table class="dati"><thead><tr><th scope="col">City or county</th><th scope="col">Rent-increase maximum</th>'
              f'<th scope="col">Date range</th></tr></thead><tbody>{r}</tbody></table></div>'
              f'<p class="small">Copied from the chart “Local Rent Increase Caps” on {fonte_link(G, "rent_ca_oag")}, read on {G.data_lunga(G.FONTI["rent_ca_oag"]["letto_il"])}. '
              'We could not read the yearly figure on the cities’ own pages for Los Angeles (it is in a PDF we did not find), San José (the page refuses our server) and '
              'San Francisco (address not found), so for those three the figure is the Attorney General’s. Rows are copied as published: where a date range had already ended when we read the chart, '
              'the city has probably set a newer figure that the chart did not show yet.</p>')
    corpo += frasi_periodi(G, "california")
    la_c = next(z for z in loc if z["comune"] == "City of Los Angeles")
    sf_c = next(z for z in loc if "San Francisco" in z["comune"])
    sj_c = next(z for z in loc if z["comune"] == "San Jose")
    f, ld = faq(G, "rent_california", [
        ("How much can a landlord raise rent in California?",
         f'Under the statewide cap, by 5% plus the change in the cost of living, up to 10% in total, over 12 months. For increases that start between {giorno(ultimo(la)["da"])} and '
         f'{giorno(ultimo(la)["a"])} the Attorney General’s chart gives {pc(ultimo(la)["tetto"])} in the Los Angeles Area, {pc(ultimo(x["voci"][1])["tetto"])} in the Riverside Area, '
         f'{pc(ultimo(x["voci"][2])["tetto"])} in the San Diego Area, {pc(ultimo(x["voci"][3])["tetto"])} in the San Francisco Area and {pc(ultimo(x["voci"][4])["tetto"])} in all other '
         f'counties. A city can set a lower limit, and some homes are exempt.', "how much can a landlord raise rent in california", "us"),
        ("What is AB 1482?",
         'AB 1482 is the California Tenant Protection Act of 2019. The Attorney General describes its rent rule this way: annual rent increases are capped at 5% plus the '
         'percentage change in the cost of living, up to a maximum of 10%. It applies to most rental housing that is more than 15 years old.', "ab 1482", "us"),
        ("Does California have rent control?",
         'California has a statewide cap on yearly rent increases (the Tenant Protection Act) and, in addition, local rent stabilization laws in a number of cities and '
         f'counties: the Attorney General’s chart lists {len(loc)}. Where the local cap gives a lower increase than the state cap, the local rule applies.', "california rent control", "us"),
        ("What is the rent increase limit under Los Angeles rent control?",
         f'The Attorney General’s chart gives {la_c["massimo"]} for the City of Los Angeles for {la_c["periodo"]}, for the units covered by the city’s Rent Stabilization '
         f'Ordinance. Other homes in Los Angeles County fall under the statewide cap for the Los Angeles Area, {pc(ultimo(la)["tetto"])}, unless another local rule or an exemption applies.',
         "los angeles rent control", "us"),
        ("What is the San Francisco rent control increase?",
         f'The Attorney General’s chart gives {sf_c["massimo"]} for the City and County of San Francisco for {sf_c["periodo"]}, for the units covered by the city’s ordinance. '
         f'The statewide cap for the San Francisco Area is {pc(ultimo(x["voci"][3])["tetto"])}.', "san francisco rent control", "us"),
        ("What is the San Jose rent control limit?",
         f'The Attorney General’s chart gives {sj_c["massimo"]} ({sj_c["periodo"].lower()}) for the buildings covered by San Jose’s ordinance. San Jose is in Santa Clara County, '
         f'which is under “all other counties” for the statewide cap: {pc(ultimo(x["voci"][4])["tetto"])}.', "san jose rent control", "us"),
    ])
    corpo += f + altri(G, "california")
    pubblica(G, percorso("california"), "California Rent Increase Cap 2026–2027 by Area (AB 1482)",
             f'California rent cap from {giorno(ultimo(la)["da"])}: {pc(ultimo(la)["tetto"])} Los Angeles Area, {pc(ultimo(x["voci"][3])["tetto"])} San Francisco, '
             f'{pc(ultimo(x["voci"][2])["tetto"])} San Diego. All areas from the Attorney General’s chart, calculator.',
             "California · AB 1482", "California rent increase cap by area",
             f'The statewide limit is 5% plus inflation, up to 10%. From {giorno(ultimo(la)["da"])} to {giorno(ultimo(la)["a"])} that is '
             f'<strong>{pc(ultimo(la)["tetto"])}</strong> in the Los Angeles Area and {pc(ultimo(x["voci"][4])["tetto"])} in most other counties.',
             corpo, ("California", percorso("california")),
             ["rent_ca_oag", "rent_ca_oag_inquilini", "bls_cpi_la", "bls_cpi_sf", "bls_cpi_riverside", "bls_cpi_sandiego", "rent_ca_dir"], jsonld=[ld] if ld else None)


def p_semplice(G, lid, titolo, descr, eyebrow, h1, sub, blocchi, domande, fonti, extra_stats, paese="us"):
    corpo = '<div class="pull">' + calcolatore(G, lid) + "</div>" + G.AD + intro_stats(G, lid, extra_stats)
    corpo += blocchi + '<h2>What the cap means on a monthly rent</h2>' + esempi(G, lid) + frasi_periodi(G, lid)
    f, ld = faq(G, "rent_" + lid, domande)
    corpo += f + altri(G, lid)
    pubblica(G, percorso(lid), titolo, descr, eyebrow, h1, sub, corpo, (L[lid]["nome"].split(" (")[0], percorso(lid)), fonti, jsonld=[ld] if ld else None, paese=paese)


def p_nyc(G):
    x = L["nyc"]
    u, d = x["voci"]
    blocchi = ('<h2>Rent Guidelines Board increases for rent-stabilized apartments</h2>' + tabella_periodi(G, "nyc")
               + '<div class="testo"><p>The Rent Guidelines Board sets the adjustment for rent-stabilized apartments and lofts once a year; the current order was adopted on '
               '25 June 2026 and applies to leases that begin between 1 October 2026 and 30 September 2027:</p>' + tt(G, "nyc", "ordine") + citaz(G, x["regola"]) + tt(G, "nyc", "altri") + tt(G, "nyc", "frazioni")
               + '<p>These guidelines are for rent-stabilized apartments only. They are not a limit for market-rate apartments, and the order itself allows for other '
               'adjustments authorized by law. This page cannot tell you whether an apartment is rent stabilized or what its lawful rent is.</p></div>')
    p_semplice(G, "nyc", "NYC Rent Stabilized Increase 2026–27: Rent Guidelines Board",
               f'New York City rent-stabilized leases starting {giorno(ultimo(u)["da"])} to {giorno(ultimo(u)["a"])}: {pc(ultimo(u)["tetto"])} for one year, {pc(ultimo(d)["tetto"])} '
               f'for two years (RGB Order #58). Last year: {pc(u["periodi"][0]["tetto"])} and {pc(d["periodi"][0]["tetto"])}.',
               "New York City · Rent Guidelines Board", "NYC rent-stabilized increase, 2026–27",
               f'Order #58 sets <strong>{pc(ultimo(u)["tetto"])}</strong> for one-year leases and {pc(ultimo(d)["tetto"])} for two-year leases that begin between '
               f'{giorno(ultimo(u)["da"])} and {giorno(ultimo(u)["a"])}.', blocchi, [
        ("What did the Rent Guidelines Board vote for 2026–27?",
         f'On 25 June 2026 the board adopted Order #58: {pc(ultimo(u)["tetto"])} for one-year leases and {pc(ultimo(d)["tetto"])} for two-year leases of rent-stabilized apartments '
         f'that begin between {giorno(ultimo(u)["da"])} and {giorno(ultimo(u)["a"])}. The year before (Order #57) it was {pc(u["periodi"][0]["tetto"])} and {pc(d["periodi"][0]["tetto"])}.',
         "rent guidelines board", "us"),
        ("What is the NYC rent increase for stabilized apartments?",
         f'For a lease that starts between {giorno(ultimo(u)["da"])} and {giorno(ultimo(u)["a"])}: {pc(ultimo(u)["tetto"])} on a one-year lease and {pc(ultimo(d)["tetto"])} on a '
         f'two-year lease. For a lease that started between {giorno(u["periodi"][0]["da"])} and {giorno(u["periodi"][0]["a"])}: {pc(u["periodi"][0]["tetto"])} and {pc(d["periodi"][0]["tetto"])}.',
         "nyc rent increase", "us"),
        ("How does rent stabilization work in NYC?",
         'For the yearly increase: the Rent Guidelines Board sets a percentage for one-year and two-year leases, counted on the lawful rent charged on 30 September, and '
         'the order applies to leases that begin from 1 October to the next 30 September. Other rules of rent stabilization are outside this page.', "rent stabilization nyc", "us"),
        ("How much can a landlord raise rent in NYC?",
         f'For a rent-stabilized apartment, by the Rent Guidelines Board percentage: {pc(ultimo(u)["tetto"])} (one year) or {pc(ultimo(d)["tetto"])} (two years) for leases beginning '
         f'{giorno(ultimo(u)["da"])} to {giorno(ultimo(u)["a"])}, plus any other adjustment authorized by law. The board’s orders do not set a limit for apartments that are not '
         f'rent stabilized.', "how much can a landlord raise rent in nyc", "us"),
    ], ["rent_nyc_58", "rent_nyc_57"], [(pc(ultimo(d)["tetto"]), "two-year lease, same period"), (pc(u["periodi"][0]["tetto"]), f'one-year lease, {periodo_breve(u["periodi"][0])}'),
                                        (pc(d["periodi"][0]["tetto"]), f'two-year lease, {periodo_breve(d["periodi"][0])}')])


def p_washington(G):
    x = L["washington"]
    v = x["voci"][0]
    a, b = indice("bls_cpi_seattle", 2025, "jun"), indice("bls_cpi_seattle", 2026, "jun")
    grezzo = (b[0] - a[0]) * 100000 // a[0]  # variazione in millesimi di punto, per difetto
    blocchi = ('<h2>Washington State rent increase cap, 2026 and 2027</h2>' + tabella_periodi(G, "washington")
               + '<div class="testo"><p>House Bill 1217 (2025) limits rent increases for most residential tenancies and tells the Department of Commerce to publish the '
               'percentage for each calendar year:</p>' + citaz(G, x["regola"]) + tt(G, "washington", "primo_anno") + tt(G, "washington", "metodo") + tt(G, "washington", "uscita")
               + tt(G, "washington", "esenti") + "</div>"
               + '<h2>How the 2027 figure was worked out</h2><div class="testo"><p>Commerce shows its calculation. For 2027 the Seattle-area index rose enough that 7% plus the '
               'change is above 10%, so the 10% ceiling applies:</p>' + tt(G, "washington", "conto_2027_intero") + tt(G, "washington", "conto_2027")
               + f'<p>The two index values are the ones the Bureau of Labor Statistics publishes for Seattle-Tacoma-Bellevue (series CUURS49DSA0): <span data-wa="prima">{a[1]}</span> '
               f'for June 2025 and <span data-wa="dopo">{b[1]}</span> for June 2026, a rise of <span data-wa="var">{grezzo / 1000:.2f}%</span> by our own calculation; plus 7 points '
               f'that is <span data-wa="somma">{(grezzo + 7000) / 1000:.2f}%</span>, the figure Commerce shows before applying the ceiling (the formula as printed on its page leaves out the division by the first index; the result is the same). For 2026 the same sum was below 10%:</p>'
               + tt(G, "washington", "conto_2026") + "</div>")
    p_semplice(G, "washington", f'Washington State Rent Increase Cap 2027: {pc(ultimo(v)["tetto"])} (HB 1217)',
               f'Washington State maximum annual rent increase: {pc(ultimo(v)["tetto"])} for 2027 and {pc(v["periodi"][0]["tetto"])} for 2026 under HB 1217 (7% plus Seattle CPI, at most 10%). '
               'Official figures, calculator.',
               "Washington State · HB 1217", "Washington State rent increase cap for 2027",
               f'The Department of Commerce publishes <strong>{pc(ultimo(v)["tetto"])}</strong> for 1 January to 31 December 2027, after {pc(v["periodi"][0]["tetto"])} for 2026.', blocchi, [
        ("What is HB 1217 in Washington State?",
         f'HB 1217 is the 2025 law that caps residential rent increases in Washington. The Department of Commerce summarizes it: no increase in the first 12 months of a tenancy, '
         f'then up to 7% plus the Consumer Price Index or 10%, whichever is less, in any 12-month period. The published maximum is {pc(v["periodi"][0]["tetto"])} for 2026 and '
         f'{pc(ultimo(v)["tetto"])} for 2027.', "hb 1217", "us"),
        ("Does Washington State have rent control?",
         f'Since 2025 Washington has a statewide limit on yearly rent increases for tenancies under the Residential Landlord-Tenant Act, unless exempt: {pc(ultimo(v)["tetto"])} '
         f'for 2027 and {pc(v["periodi"][0]["tetto"])} for 2026. The percentage is published each year by the Department of Commerce.', "washington state rent control", "us"),
        ("What is the maximum rent increase in Washington State?",
         f'{pc(ultimo(v)["tetto"])} for increases between 1 January and 31 December 2027, and {pc(v["periodi"][0]["tetto"])} between 1 January and 31 December 2026, for properties '
         f'subject to the Residential Landlord-Tenant Act that are not exempt.', "rent increase washington state", "us"),
    ], ["rent_wa_commerce", "bls_cpi_seattle"], [(pc(v["periodi"][0]["tetto"]), "cap for 2026"), ("7% + CPI", "the formula, with a 10% ceiling"), ("1 Jan", "the day the yearly figure changes")])


def p_oregon(G):
    x = L["oregon"]
    v = x["voci"][0]
    blocchi = ('<h2>Oregon maximum annual rent increase, 2026 and 2027</h2>' + tabella_periodi(G, "oregon")
               + '<div class="testo"><p>Oregon law tells the Department of Administrative Services to publish the percentage for the next calendar year by 30 September. '
               'The department’s page:</p>' + tt(G, "oregon", "scadenza") + citaz(G, x["regola"]) + tt(G, "oregon", "grandi")
               + '<p>The department’s Excel file explains the index used and adds a rule on frequency:</p>' + tt(G, "oregon", "metodo") + tt(G, "oregon", "una_volta")
               + '<p>The same file notes that the October 2025 value of the index was not published and was estimated by the department for this calculation. Questions about '
               'how the limit is applied go to another agency:</p>' + tt(G, "oregon", "domande") + "</div>")
    p_semplice(G, "oregon", f'Oregon Rent Increase Cap 2027: {pc(ultimo(v)["tetto"])} Maximum',
               f'Oregon maximum annual rent increase: {pc(ultimo(v)["tetto"])} for 2027, after {pc(v["periodi"][0]["tetto"])} for 2026 (7% plus CPI, at most 10%). '
               'Official state figures with a calculator.',
               "Oregon · ORS 90.324", "Oregon rent increase cap for 2027",
               f'The state publishes <strong>{pc(ultimo(v)["tetto"])}</strong> as the maximum allowable rent increase for 2027; for 2026 it was {pc(v["periodi"][0]["tetto"])}.', blocchi, [
        ("Does Oregon have rent control?",
         f'Oregon has a statewide limit on yearly rent increases: the lesser of 10% or 7% plus the Consumer Price Index, published each September by the Department of '
         f'Administrative Services. It is {pc(ultimo(v)["tetto"])} for 2027 and was {pc(v["periodi"][0]["tetto"])} for 2026. A separate 6% figure applies to tenancies in facilities '
         f'with more than 30 spaces.', "oregon rent control", "us"),
        ("How much can a landlord raise rent in Oregon?",
         f'By at most {pc(ultimo(v)["tetto"])} in 2027 ({pc(v["periodi"][0]["tetto"])} in 2026) for the tenancies the limit covers, and the department’s file says only one rent increase '
         f'may be issued in any 12-month period. On a $1,500 rent, {pc(ultimo(v)["tetto"])} is {soldi(aumento(150000, ultimo(v)["tetto"])[0])} a month.',
         "how much can a landlord raise rent in oregon", "us"),
    ], ["rent_or_das", "rent_or_xlsx"], [(pc(v["periodi"][0]["tetto"]), "cap for 2026"), ("7% + CPI", "the formula, with a 10% ceiling"), ("30 Sep", "next year’s figure is published by")])


def p_ontario(G):
    x = L["ontario"]
    v = x["voci"][0]
    st = "".join(f'<tr><td>{s["anno"]}</td><td class="n" data-on="{s["anno"]}">{pc(s["tetto"])}</td></tr>' for s in x["storia"])
    blocchi = ('<h2>Ontario rent increase guideline, 2026 and 2027</h2>' + tabella_periodi(G, "ontario")
               + '<div class="testo">' + citaz(G, x["regola"]) + tt(G, "ontario", "dodici") + citaz(G, x["preavviso"])
               + '<p>The guideline does not cover every home. Among the exclusions the province lists:</p>' + tt(G, "ontario", "esenti") + tt(G, "ontario", "sopra")
               + '<p>How the percentage is set:</p>' + tt(G, "ontario", "metodo") + tt(G, "ontario", "massimo") + "</div>"
               + f'<h2>The guideline year by year</h2><div class="tab"><table class="dati stretta"><thead><tr><th scope="col">Year</th><th scope="col" class="n">Guideline</th></tr></thead>'
               f'<tbody>{st}</tbody></table></div><p class="small">From the table “Previous rent increase guidelines” on the Ontario page.</p>')
    p_semplice(G, "ontario", f'Ontario Rent Increase Guideline 2027: {pc(ultimo(v)["tetto"])}',
               f'Ontario rent increase guideline: {pc(ultimo(v)["tetto"])} for 2027, after {pc(v["periodi"][0]["tetto"])} for 2026. Who it covers, the 90-day notice, the last ten years '
               'and a calculator, from ontario.ca.',
               "Ontario · rent increase guideline", "Ontario rent increase guideline for 2027",
               f'The province sets the guideline at <strong>{pc(ultimo(v)["tetto"])}</strong> for 2027; it was {pc(v["periodi"][0]["tetto"])} for 2026.', blocchi, [
        ("What is the rent increase in Ontario for 2027?",
         f'The rent increase guideline for 2027 is {pc(ultimo(v)["tetto"])}; for 2026 it is {pc(v["periodi"][0]["tetto"])}. On a rent of $2,000 a month, {pc(ultimo(v)["tetto"])} is '
         f'{soldi(aumento(200000, ultimo(v)["tetto"])[0])}.', "rent increase ontario", "ca"),
        ("Does Ontario have rent control?",
         'For most private residential units covered by the Residential Tenancies Act, the yearly increase is limited to the guideline unless the Landlord and Tenant Board '
         'approves more. The province lists exclusions, among them units first occupied for residential purposes after 15 November 2018 and a new tenancy after a unit turns over.',
         "rent control ontario", "ca"),
        ("How much can a landlord raise rent in Ontario?",
         f'For most tenants, by no more than the guideline: {pc(ultimo(v)["tetto"])} in 2027. At least 12 months must have passed since the last increase or the start of the tenancy, '
         f'and the landlord must give written notice in the proper form at least 90 days before.', "how much can a landlord raise rent in ontario", "ca"),
        ("How is the Ontario rent increase guideline calculated?",
         'Ontario says it uses the Ontario Consumer Price Index from Statistics Canada, with data from June to May for the following year’s guideline, and that the guideline is '
         'capped at 2.5%.', "ontario rent increase guideline", "ca"),
    ], ["rent_on"], [(pc(v["periodi"][0]["tetto"]), "guideline for 2026"), ("2.5%", "the most the guideline can be"), ("90 days", "written notice before an increase")], paese="ca")


def p_bc(G):
    x = L["bc"]
    v = x["voci"][0]
    blocchi = ('<h2>British Columbia rent increase limit, 2026 and 2027</h2>' + tabella_periodi(G, "bc")
               + '<div class="testo">' + citaz(G, x["regola"]) + citaz(G, x["preavviso"]) + tt(G, "bc", "arrotonda") + tt(G, "bc", "utenze") + tt(G, "bc", "solo_anno")
               + '<p>The province’s page was last updated on 27 August 2026 and has its own calculator for the date an increase can take effect. Because landlords cannot round '
               'up, the calculator on this page rounds the increase down to the cent.</p></div>')
    p_semplice(G, "bc", f'BC Rent Increase 2027: {pc(ultimo(v)["tetto"])} Limit (British Columbia)',
               f'British Columbia rent increase limit: {pc(ultimo(v)["tetto"])} for 2027, after {pc(v["periodi"][0]["tetto"])} for 2026. Three full months’ notice, once every 12 months. '
               'Official wording and a calculator.',
               "British Columbia · Residential Tenancy Branch", "BC rent increase limit for 2027",
               f'The limit for residential tenancies is <strong>{pc(ultimo(v)["tetto"])}</strong> for 2027; for 2026 it is {pc(v["periodi"][0]["tetto"])}.', blocchi, [
        ("What is the BC rent increase for 2027?",
         f'The 2027 rent increase limit for residential tenancies in British Columbia is {pc(ultimo(v)["tetto"])}; the 2026 limit is {pc(v["periodi"][0]["tetto"])}. On a rent of '
         f'$2,000 a month, {pc(ultimo(v)["tetto"])} is {soldi(aumento(200000, ultimo(v)["tetto"])[0])}.', "bc rent increase", "ca"),
        ("Does BC have rent control?",
         'British Columbia limits increases for existing tenants: rent can only be increased once every 12 months, within the yearly limit set by the Residential Tenancy Branch, '
         'and with at least three full months’ notice.', "rent control bc", "ca"),
        ("How do I calculate a rent increase in BC?",
         f'Multiply the current rent by the yearly limit ({pc(ultimo(v)["tetto"])} for 2027) and do not round up: the province says landlords cannot round up when calculating the '
         f'allowable increase. The calculator on this page does that; the province’s own calculator also gives the earliest date.', "rent increase calculator bc", "ca"),
    ], ["rent_bc"], [(pc(v["periodi"][0]["tetto"]), "limit for 2026"), ("3 full months", "notice before an increase"), ("12 months", "between increases")], paese="ca")


def p_stpaul(G):
    x = L["stpaul"]
    v = x["voci"][0]
    blocchi = ('<h2>Saint Paul rent stabilization: the 3% limit</h2>' + tabella_periodi(G, "stpaul")
               + '<div class="testo"><p>Saint Paul’s limit is a fixed percentage, so it does not change with the year. The city’s summary:</p>' + citaz(G, x["regola"])
               + tt(G, "stpaul", "ritorno") + '<p>The exceptions the city lists, and the exemption added by the amended ordinance:</p>' + tt(G, "stpaul", "eccezioni")
               + tt(G, "stpaul", "nuove") + tt(G, "stpaul", "modifica") + "</div>")
    p_semplice(G, "stpaul", "Saint Paul Rent Control: 3% Cap and Exceptions",
               'Saint Paul, Minnesota limits residential rent increases to 3% in a 12-month period, with exceptions from 3% to 8% and more. '
               'City wording and a calculator.',
               "Saint Paul, Minnesota · Rent Stabilization Ordinance", "Saint Paul rent increase limit",
               f'The city’s ordinance limits residential rent increases to <strong>{pc(v["periodi"][0]["tetto"])}</strong> in a 12-month period, unless an exception applies.', blocchi, [
        ("What is the rent control limit in St. Paul?",
         'The City of Saint Paul’s Rent Stabilization Ordinance limits residential rent increases to no more than 3% in a 12-month period. The city lists exceptions: '
         'self-certification for 3% to 8%, CPI plus 8% after a just-cause vacancy, and staff determinations; newly constructed rental properties are exempt under the amended ordinance.',
         "st paul rent control", "us"),
    ], ["rent_stpaul"], [("3%–8%", "self-certification exception"), ("CPI + 8%", "after a just-cause vacancy"), ("12 months", "the period the limit is counted over")])


def p_indice(G):
    a, m, r12 = G.ultimo_12_mesi("us")
    corpo = '<div class="pull">' + calcolatore(G) + "</div>" + G.AD
    la, wa, on_, ny = L["california"]["voci"][0], L["washington"]["voci"][0], L["ontario"]["voci"][0], L["nyc"]["voci"][0]
    corpo += stats(G, [(pc(ultimo(la)["tetto"]), f'California, Los Angeles Area, {periodo_breve(ultimo(la))}'), (pc(ultimo(wa)["tetto"]), "Washington State and Oregon, 2027"),
                       (pc(ultimo(ny)["tetto"]), f'New York City stabilized, one-year lease, {periodo_breve(ultimo(ny))}'), (pc(ultimo(on_)["tetto"]), "Ontario guideline, 2027")])
    righe = ""
    for i in ORDINE:
        x = L[i]
        for v in x["voci"]:
            nome = x["nome"] if len(x["voci"]) == 1 else f'{x["nome"].split(" (")[0]}: {v["nome"]}'
            ps = v["periodi"]
            prec = cella(v["k"], 0, "tetto", f'{pc(ps[0]["tetto"])}<br><span class="small">{G.h(periodo_breve(ps[0]))}</span>') if len(ps) > 1 else '<td class="n">–</td>'
            n = len(ps) - 1
            righe += (f'<tr><td><a href="/{percorso(i)}">{G.h(nome)}</a><br><span class="small">Changes: {G.h(x["cambio"])}</span></td>{prec}'
                      + cella(v["k"], n, "tetto", f'<strong>{pc(ps[n]["tetto"])}</strong><br><span class="small">{G.h(periodo_breve(ps[n]))}</span>') + '</tr>')
    corpo += ('<h2>Rent increase caps for 2026 and 2027</h2><div class="tab"><table class="dati stretta"><thead><tr><th scope="col">Place</th><th scope="col" class="n">Earlier period</th>'
              f'<th scope="col" class="n">Latest period</th></tr></thead><tbody>{righe}</tbody></table></div>'
              '<p class="small">Each percentage is the one published on the official page of the state, province or city, linked from the page of each place. '
              'In California, Oregon and Washington the cap follows a formula with a consumer price index; New York City, Ontario and British Columbia publish a figure each year; '
              'Saint Paul’s is fixed.</p>')
    corpo += ('<h2>What these caps are, and are not</h2><div class="testo"><p>A rent increase cap limits how much the rent of a sitting tenant can go up in a year. Each one '
              'covers only some homes: the official pages list exemptions (newer buildings, for example), and California and Ontario say the landlord sets the rent when a new '
              'tenant moves in. A city can also have a lower limit than its state: the <a href="/' + percorso("california") + '#local">California page</a> lists the '
              'local caps published by the Attorney General.</p>'
              f'<p>For scale: the national CPI-U, the index behind this site’s <a href="/">inflation calculator</a>, rose <strong data-cpi-us>{G.pct(r12, 1, segno=False)}</strong> in the 12 '
              f'months to {G.h(G.mese_lungo(a, m))} (BLS). The caps in California, Oregon and Washington use regional indexes and fixed months, so they do not move with the '
              'national figure month by month.</p>'
              '<p><strong>Places not covered.</strong> Only places whose official page we have read are listed; a place that is missing is not a statement that it has no cap. '
              'For cities such as Los Angeles, San José and San Francisco we could not read the yearly figure on the city’s own page, so they appear only through the '
              'California Attorney General’s chart.</p></div>')
    f, ld = faq(G, "rent_indice", [
        ("How much can a landlord raise rent?",
         f'It depends on where the home is and whether a cap covers it. Among the places with a published limit: {pc(ultimo(la)["tetto"])} in the Los Angeles Area of California '
         f'(increases from {giorno(ultimo(la)["da"])}), {pc(ultimo(L["oregon"]["voci"][0])["tetto"])} in Oregon and {pc(ultimo(wa)["tetto"])} in Washington State for 2027, '
         f'{pc(ultimo(on_)["tetto"])} in Ontario and {pc(ultimo(L["bc"]["voci"][0])["tetto"])} in British Columbia for 2027. Where no cap applies, this page gives no figure.',
         "how much can a landlord raise rent", "us"),
        ("How do I calculate a rent increase?",
         f'Multiply the current rent by the percentage and add the result: $2,000 × {pc(ultimo(la)["tetto"])} = {soldi(aumento(200000, ultimo(la)["tetto"])[0])}, so the highest new rent '
         f'under that cap is {soldi(aumento(200000, ultimo(la)["tetto"])[1])}. The calculator above does this with the official percentage for the place and period you choose.',
         "rent increase calculator", "us"),
        ("How much can rent increase in a year?",
         'Under the caps listed here, between 0% (New York City rent-stabilized leases starting from 1 October 2026) and 10% (Oregon and Washington State in 2027), '
         'depending on the place, the period and the type of home.', "how much can rent increase", "us"),
    ])
    corpo += f + altri(G)
    fonti = ["rent_ca_oag", "rent_or_das", "rent_wa_commerce", "rent_nyc_58", "rent_nyc_57", "rent_on", "rent_bc", "rent_stpaul", "bls_cpiu"]
    corpo += G.fonti_box(fonti, piede=(
        'Every percentage is copied from the official pages above and checked against them before the page changes (<a href="/how-we-check/">how we check</a>). '
        'The national CPI-U comes from the BLS file read every month.'))
    testata = G.banda("Rent increase caps · 2027", "Rent increase cap 2027: calculator and limits by place",
                      'The legal limit on a yearly rent increase in California, Oregon, Washington State, New York City, Ontario, British Columbia and Saint Paul, '
                      'each with its official source, and the highest new rent it allows.',
                      G.trust([("check", "Figures quoted from official pages"), ("calendar", "2026 and 2027 periods"), ("info", "No legal advice, no products")]), icona="shield")
    G.pagina(BASE, "Rent Increase Cap 2027: Calculator and Limits by State",
             f'Rent increase caps for 2027 with a calculator: California {pc(ultimo(la)["tetto"])} (Los Angeles Area), Oregon and Washington 10%, '
             f'Ontario {pc(ultimo(on_)["tetto"])}, BC {pc(ultimo(L["bc"]["voci"][0])["tetto"])}, New York City. Sources.',
             corpo, testata, "us", briciole=[("Home", ""), ("Rent increase caps", BASE)], jsonld=[ld] if ld else None, disclaimer=DISCL, script=G.RENT_SCRIPT)


def genera(G):
    p_indice(G)
    p_california(G)
    p_nyc(G)
    p_washington(G)
    p_oregon(G)
    p_ontario(G)
    p_bc(G)
    p_stpaul(G)
