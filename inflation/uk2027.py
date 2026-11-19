"""Sezione «UK rates from April 2027» (pagine /uk/…): paga minima per età, pensione di Stato, sussidi, indennità di malattia.

Dati: dati/uk_2027.json (importi in pence; ogni voce con la fonte GOV.UK e la riga di tabella da cui viene; testi in
dati/grezzi/regole2027/, scaricati da raccolta/regole2027.py). Pagine decise dalla domanda misurata (dati/domanda.json, gruppo
uk_2027, country=gb, 18/11/2026):
  /uk/rates-april-2027/          indice: tutte le cifre a colpo d'occhio                 (frasi «2027» ancora a 0: pagina di raccordo)
  /uk/minimum-wage-2027/         paga minima per età + calcolatore della paga            («minimum wage uk» 165.000, «minimum wage for 18 year olds» 40.500)
  /uk/state-pension-2027/        pensione di Stato nuova e di base, Pension Credit       («state pension increase 2025» 90.500, «how much is state pension» 60.500)
  /uk/benefit-rates-2027/        Universal Credit, PIP, Attendance Allowance, DLA…       («pip rates» 74.000, «dla rates» 27.100, «attendance allowance rates» 22.200)
  /uk/statutory-sick-pay-2027/   SSP e gli altri pagamenti di legge (maternità ecc.)     («statutory sick pay» 90.500, «statutory maternity pay» 60.500)
Solo cifre annunciate: la paga minima è annunciata dal Governo (28/10/2026); le cifre DWP sono «proposed» e le pagine lo dicono.
Nessun consiglio. genera.py chiama genera(G) passando sé stesso.
"""
import json
import re
from pathlib import Path

RADICE = Path(__file__).resolve().parent
D = json.loads((RADICE / "dati" / "uk_2027.json").read_text(encoding="utf-8"))
GR = {g["id"]: g for g in D["gruppi"]}
V = {v["k"]: v for g in D["gruppi"] for v in g["voci"]}
V.update({v["k"]: v for v in D["paga_minima"]["voci"]})
PAGINE = {"indice": "uk/rates-april-2027/", "paga": "uk/minimum-wage-2027/", "pensione": "uk/state-pension-2027/",
          "sussidi": "uk/benefit-rates-2027/", "malattia": "uk/statutory-sick-pay-2027/"}
ORE_TABELLA = (160, 200, 300, 375, 400)  # ore la settimana × 10
PER = {"hour": "an hour", "week": "a week", "month": "a month", "once": "lump sum"}
A0, A1 = D["anno_prima"], D["anno_dopo"]  # «2026 to 2027», «2027 to 2028»
FONTI_UK = ["uk27_nmw", "uk27_lpc", "uk27_dwp", "uk27_dwp_indice"]
GUIDE_SP = ["uk27_guida_nsp", "uk27_guida_nsp_importo", "uk27_guida_bsp"]

DISCL = ("<strong>General information, not financial or investment advice, and not benefits, employment or legal advice.</strong> The figures are "
         "the rates published on GOV.UK by the Low Pay Commission and the Department for Work and Pensions, linked on each page. The benefit and pension "
         "rates for 2027 to 2028 are published as proposed rates. What a person is actually paid depends on their own circumstances and on rules that are "
         "not on this page. This is an independent site, not a government website. For your own case use GOV.UK or an adviser such as Citizens Advice.")


# ---------------------------------------------------------------- conti (stile.PAY_MOTORE_JS è la copia)
def paga(rate_p, ore_d):
    """Paga lorda in pence da una tariffa oraria (pence) e dalle ore settimanali × 10: settimana, mese (anno ÷ 12), anno (52 settimane). Mezzo penny per eccesso."""
    return {"sett": (rate_p * ore_d + 5) // 10, "mese": (rate_p * ore_d * 52 + 60) // 120, "anno": (rate_p * ore_d * 52 + 5) // 10}


def variazione(prima, dopo):
    """Variazione percentuale con una cifra decimale, in decimi di punto (mezzo decimo lontano da zero)."""
    d = (dopo - prima) * 1000
    return (2 * abs(d) + prima) // (2 * prima) * (1 if d >= 0 else -1)


# ---------------------------------------------------------------- formati
def gbp(p, dec=True):
    return f"£{p // 100:,}.{p % 100:02d}" if dec or p % 100 else f"£{p // 100:,}"


def pctx(d):
    return "no change" if d == 0 else f"{'+' if d > 0 else '−'}{abs(d) // 10}.{abs(d) % 10}%"


def diff(prima, dopo):
    d = dopo - prima
    return "no change" if d == 0 else ("+" if d > 0 else "−") + (gbp(abs(d)) if abs(d) >= 100 else f"{abs(d)}p")


def ore_txt(od):
    return f"{od // 10}" + (f".{od % 10}" if od % 10 else "")


PROP_TH = "<br>(proposed)"  # nelle intestazioni delle colonne 2027-28 che vengono dal documento DWP
PROP_FAQ = " The 2027 to 2028 figures are the proposed rates the DWP published on 11 November 2026."


def cella(k, campo, testo, cls="n"):
    return f'<td class="{cls}" data-uk="{k}|{campo}">{testo}</td>'


def righe(chiavi, evid=()):
    out = ""
    for k in chiavi:
        v = V[k]
        out += (f'<tr{" class=\"evid\"" if k in evid else ""}><td>{v["nome"]}</td>' + cella(k, "prima", gbp(v["prima"])) + cella(k, "dopo", gbp(v["dopo"]))
                + cella(k, "diff", diff(v["prima"], v["dopo"])) + cella(k, "pct", pctx(variazione(v["prima"], v["dopo"]))) + "</tr>")
    return out


def tabella(G, chiavi, periodo, evid=(), prima_col="Rate", proposto=True):
    """proposto: le cifre 2027-28 vengono dal documento DWP «Proposed…» (tutte le tabelle tranne la paga minima) e l'intestazione lo dice."""
    return (f'<div class="tab fissa c1"><table class="dati stretta"><thead><tr><th scope="col">{G.h(prima_col)}</th><th scope="col" class="n">{A0}</th>'
            f'<th scope="col" class="n">{A1}{PROP_TH if proposto else ""}</th><th scope="col" class="n">Change</th><th scope="col" class="n">%</th></tr></thead>'
            f'<tbody>{righe(chiavi, evid)}</tbody></table></div><p class="small">{G.h(periodo)}</p>')


def pulita(frase):
    """La frase come si stampa: uguale a quella registrata, senza lo spazio che l'estrazione del testo lascia prima della punteggiatura."""
    return re.sub(r"\s+([.,:;])", r"\1", frase)


def fonte_link(G, fid):
    f = G.FONTI[fid]
    return f'<a href="{G.h(f["url"])}" rel="noopener">{G.h(f["chi"])}, “{G.h(f["titolo"])}”</a>'


def quando(G, fid):
    f = G.FONTI[fid]
    return (f'published {f["pubblicato"]} · ' if f.get("pubblicato") else "") + f'read on {G.data_lunga(f["letto_il"])}'


def citaz(G, x, prima=""):
    """Frase o riga di tabella ufficiale, con la fonte, la data di pubblicazione (se scritta) e la data di lettura."""
    return f'<blockquote class="citaz">{prima}“{G.h(pulita(x["frase"]))}”<cite>{fonte_link(G, x["fonte"])} · {quando(G, x["fonte"])}</cite></blockquote>'


def testo(G, k):
    return citaz(G, D["testi"][k])


def righe_fonte(G, chiavi, titolo="The source rows, as published"):
    """Le righe delle tabelle ufficiali da cui vengono le cifre (chiuse in un <details>)."""
    voci = []
    for k in chiavi:
        v = V[k]
        if "sezione" in v:
            dove = f'{G.h(v["sezione"])}' + (f' › {G.h(v["intestazione"])}' if v["intestazione"] else "") + f' · columns “Rates {A0}” and “Rates {A1}”: '
            voci.append(citaz(G, v, f'<span class="small">{dove}</span><br>'))
        else:
            voci.append(citaz(G, D["paga_minima"]["tabella"], '<span class="small">Current rates table, columns and the two rows: </span><br>'))
            voci.append(citaz(G, v["annuncio"], '<span class="small">Announcement table, columns “NMW rate from April 2027”, “Increase (£)”, “Increase (%)”: </span><br>'))
    return f'<details class="irs"><summary>{G.h(titolo)}</summary>{"".join(dict.fromkeys(voci))}</details>'


def stato_box(G):
    """Che cosa è annunciato e che cosa è ancora «proposed», con le date."""
    f = G.FONTI
    return (f'<div class="nota info">{G.ico("info")}<p><strong>What is official, and since when.</strong> The minimum wage rates for April 2027 were announced by the '
            f'Government on {f["uk27_lpc"]["pubblicato"]}. The benefit and pension rates were published by the Department for Work and Pensions on '
            f'{f["uk27_dwp"]["pubblicato"]} under the title “{G.h(D["testi"]["dwp_titolo"]["frase"])}”: they are the rates set out in the ministerial statement of '
            f'28 October 2026 and stay proposed until the legislation that brings them into force is made. If a rate changes, this page changes with the source. '
            f'Sources read on {G.data_lunga(f["uk27_dwp"]["letto_il"])}.</p></div>')


def inflazione(G, k, cosa):
    """Confronto con l'ultimo tasso CPI a 12 mesi pubblicato dall'ONS (stessa serie delle pagine /uk/)."""
    v = V[k]
    a12 = G.CPI_RATE["mensile"][G.UK_LU]
    return (f'<h2>Compared with inflation</h2><div class="testo"><p>{cosa} rises by <strong data-uk="{k}|pct">{pctx(variazione(v["prima"], v["dopo"]))[1:]}</strong> '
            f'from {gbp(v["prima"])} to {gbp(v["dopo"])} {PER[v["periodo"]]}. The latest CPI 12-month rate published by the Office for National Statistics is '
            f'<strong data-cpi12>{G.pct(a12 / 100, 1, segno=False)}</strong> ({G.h(G.UK_ULT_TXT)}). The two figures measure different things over different '
            f'periods: the rate is fixed once for the year, the CPI changes every month. To see what an amount from another year is worth today, use the '
            f'<a href="/uk/">UK inflation calculator</a>.</p></div>')


def altre(G, tranne):
    voci = [("paga", "£/h", "Minimum wage April 2027", "Rates by age, weekly and yearly pay"),
            ("pensione", "SP", "State Pension 2027 to 2028", "New and basic State Pension, Pension Credit"),
            ("sussidi", "UC", "Benefit rates 2027 to 2028", "Universal Credit, PIP, Attendance Allowance, DLA"),
            ("malattia", "SSP", "Statutory Sick Pay 2027 to 2028", "SSP, maternity, paternity and adoption pay"),
            ("indice", "All", "All UK rates from April 2027", "Every figure on one page")]
    li = "".join(f'<li><a href="/{PAGINE[k]}"><b>{G.h(b)}</b>{G.h(t)}<small>{G.h(s)}</small></a></li>' for k, b, t, s in voci if k != tranne)
    return (f'<h2>More UK rates for 2027 to 2028</h2><ul class="griglia">{li}'
            '<li><a href="/uk/"><b>CPI</b>UK inflation calculator<small>ONS CPI and RPI, 1800 to today</small></a></li></ul>')


def stats(G, voci):
    return '<div class="card stats">' + "".join(f'<div class="stat{" main" if i == 0 else ""}"><b>{b}</b><span>{G.h(s)}</span></div>' for i, (b, s) in enumerate(voci)) + "</div>"


def faq(G, pid, voci):
    """Nelle pagine con cifre DWP ogni risposta dice che le cifre 2027-28 sono «proposed» (la risposta può essere letta da sola nei risultati di ricerca)."""
    if pid != "uk_paga":
        assert G.FONTI["uk27_dwp"]["pubblicato"] == "11 November 2026"
        voci = [(q, a if "proposed" in a else a + PROP_FAQ, ricerca) for q, a, ricerca in voci]
    return G.faq_blocco(pid, [(q, a, ricerca, "gb") for q, a, ricerca in voci])


def pubblica(G, chiave, titolo, descr, eyebrow, h1, sub, corpo, nome_bc, fonti, icona="coins", jsonld=None, script=""):
    corpo += G.fonti_box(fonti + ["ons_d7g7"], piede=(
        'Every rate on this page is copied from the GOV.UK pages above and checked against them before the page changes: each figure must appear in the '
        'quoted row of the official table (<a href="/how-we-check/">how we check</a>). The CPI rate comes from the ONS series, read every month.'))
    testata = G.banda(eyebrow, h1, sub, G.trust([("check", "Figures quoted from GOV.UK"), ("calendar", f"{A0} and {A1}"), ("info", "No advice, no products")]), icona=icona)
    bc = [("Home", ""), ("UK inflation calculator", "uk/"), ("UK rates from April 2027", PAGINE["indice"])]
    G.pagina(PAGINE[chiave], titolo, descr, corpo, testata, "uk", briciole=bc + ([(nome_bc, PAGINE[chiave])] if chiave != "indice" else []),
             jsonld=jsonld, disclaimer=DISCL, script=script)


# ---------------------------------------------------------------- pagine
NMW = ["nlw", "nmw_18_20", "nmw_u18", "nmw_app"]


def calcolatore_paga(G):
    fasce = {k: [V[k]["nome"], V[k]["prima"], V[k]["dopo"]] for k in NMW}
    T = {"titolo": "{h} hours a week at {r} an hour", "sett": "a week", "mese": "a month (yearly pay ÷ 12)", "anno": "a year (52 weeks)",
         "prima": "a year at the April 2026 rate ({r})", "piu": "more a year from April 2027", "uguale": "difference from the April 2026 rate",
         "errore": "Enter the hours as a number between 1 and 100, for example 37.5.",
         "nota": "Gross pay before tax, National Insurance and pension contributions. Hours × the minimum hourly rate; an employer can pay more."}
    od, k0 = 375, "nlw"
    p1, p0 = paga(V[k0]["dopo"], od), paga(V[k0]["prima"], od)
    stat = (f'<div class="ris-main"><span>{G.h(T["titolo"].replace("{h}", ore_txt(od)).replace("{r}", gbp(V[k0]["dopo"])))}</span>'
            f'<b data-pay-sett>{gbp(p1["sett"])}</b><span>{T["sett"]}</span></div>'
            f'<ul class="mini due"><li><b data-pay-mese>{gbp(p1["mese"])}</b><span>{G.h(T["mese"])}</span></li>'
            f'<li><b data-pay-anno>{gbp(p1["anno"])}</b><span>{G.h(T["anno"])}</span></li>'
            f'<li><b data-pay-prima>{gbp(p0["anno"])}</b><span>{G.h(T["prima"].replace("{r}", gbp(V[k0]["prima"])))}</span></li>'
            f'<li><b data-pay-diff>{gbp(p1["anno"] - p0["anno"])}</b><span>{G.h(T["piu"])}</span></li></ul>'
            f'<p class="small">{G.h(T["nota"])}</p>')
    opz = "".join(f'<option value="{k}"{" selected" if k == k0 else ""}>{G.h(V[k]["nome"])}</option>' for k in NMW)
    chips = "".join(f'<button type="button" data-h="{ore_txt(o)}">{ore_txt(o)} h</button>' for o in ORE_TABELLA)
    form = f"""<form class="calc-in" data-pay novalidate>
<label><span class="lab">Age band</span><select name="k">{opz}</select></label>
<label><span class="lab">Hours a week</span><input type="text" name="h" inputmode="decimal" autocomplete="off" value="{ore_txt(od)}" aria-label="Hours a week"></label>
<div class="chips" role="group" aria-label="Common hours">{chips}</div>
</form>"""
    js = json.dumps({"fasce": fasce, "t": T}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return (f'<section class="card calc" id="pay"><div class="calc-h"><h2>{G.ico("calc")}Minimum wage pay calculator</h2><span class="pill">From 1 April 2027</span></div>'
            f'<div class="calc-g">{form}<div class="calc-out" data-pay-out aria-live="polite">{stat}</div></div>'
            f'<p class="calc-f">Formula: hours a week × the minimum hourly rate for the age band; × 52 for a year, and the year ÷ 12 for a month, rounded to the '
            f'penny. Runs in your browser; nothing you type is sent anywhere.</p></section>'
            f'<script type="application/json" id="pay-dati">{js}</script>')


def tabella_paga(G):
    """Paga lorda alla tariffa di aprile 2027 per alcune settimane tipo (calcolo nostro: ore × tariffa)."""
    th = "".join(f'<th scope="col" class="n">{ore_txt(o)} h a week</th>' for o in ORE_TABELLA)
    corpo = ""
    for k in NMW:
        corpo += f'<tr><td>{V[k]["nome"]}<br><span class="small">{gbp(V[k]["dopo"])} an hour</span></td>' + "".join(
            f'<td class="n" data-uk="{k}|sett{o}">{gbp(paga(V[k]["dopo"], o)["sett"])}<br><span class="small" data-uk="{k}|anno{o}">{gbp(paga(V[k]["dopo"], o)["anno"])} a year</span></td>'
            for o in ORE_TABELLA) + "</tr>"
    return (f'<div class="tab fissa c1"><table class="dati"><thead><tr><th scope="col">From 1 April 2027</th>{th}</tr></thead><tbody>{corpo}</tbody></table></div>'
            '<p class="small">Our own calculation: hours × the hourly rate, a year counted as 52 weeks. Gross pay, before tax and National Insurance.</p>')


def ppaga(G):
    nlw, a18, u18 = V["nlw"], V["nmw_18_20"], V["nmw_u18"]
    al = D["paga_minima"]["alloggio"]
    fl = paga(nlw["dopo"], 375)
    corpo = '<div class="pull">' + calcolatore_paga(G) + "</div>" + G.AD
    corpo += stats(G, [(gbp(nlw["dopo"]), "National Living Wage, 21 and over, from 1 April 2027"), (pctx(variazione(nlw["prima"], nlw["dopo"])), f'on {gbp(nlw["prima"])} (April 2026)'),
                       (gbp(a18["dopo"]), "aged 18 to 20"), (gbp(u18["dopo"]), "under 18 and apprentices")])
    corpo += (f'<h2>Minimum wage rates from April 2027, by age</h2>' + tabella(G, NMW, "Hourly rates. The apprentice rate applies to apprentices aged under 19, or aged 19 "
              "or over and in the first year of their apprenticeship.", evid=("nlw",), prima_col="Age band", proposto=False)
              + '<div class="testo">' + testo(G, "lpc_annuncio") + testo(G, "lpc_altre") + testo(G, "lpc_accettato")
              + f'<p>The rate changes on one fixed day:</p>' + testo(G, "nmw_cambio")
              + f'<p>The accommodation offset, the most an employer can count towards minimum wage pay for accommodation it provides, rises by {al["aumento"]}p to '
              f'<span data-uk="alloggio|dopo">{gbp(al["dopo"])}</span> a day.</p>' + citaz(G, al) + "</div>")
    corpo += '<h2>Weekly and yearly pay at the April 2027 rates</h2>' + tabella_paga(G)
    st = [("From 1 April 2027", [V[k]["dopo"] for k in NMW], "dopo"), ("From 1 April 2026", [V[k]["prima"] for k in NMW], "prima")] + [
        (x["periodo"], x["valori"], f"storia{i}") for i, x in enumerate(D["paga_minima"]["storia"])]
    corpo += ('<h2>The rates since April 2024</h2><div class="tab"><table class="dati"><thead><tr><th scope="col">Period</th>'
              + "".join(f'<th scope="col" class="n">{G.h(V[k]["nome"].split(" (")[0])}</th>' for k in NMW) + "</tr></thead><tbody>"
              + "".join(f'<tr><td>{G.h(per)}</td>' + "".join(f'<td class="n" data-uk="{k}|{campo}">{gbp(x)}</td>' for k, x in zip(NMW, val)) + "</tr>" for per, val, campo in st)
              + '</tbody></table></div><p class="small">Hourly rates from the current and previous rates tables on GOV.UK.</p>')
    corpo += ('<h2>Who gets which rate</h2><div class="testo"><p>GOV.UK sets the age for the National Living Wage and says who gets the apprentice rate:</p>'
              + testo(G, "nmw_eta") + testo(G, "nmw_apprendisti") + testo(G, "nmw_apprendisti_dopo")
              + '<p>Who is entitled to the minimum wage at all (and who is not) is explained on '
              '<a href="https://www.gov.uk/national-minimum-wage/who-gets-the-minimum-wage" rel="noopener">GOV.UK</a>; this page only lists the rates.</p></div>')
    corpo += inflazione(G, "nlw", "The National Living Wage") + righe_fonte(G, NMW)
    f, ld = faq(G, "uk_paga", [
        ("What is the minimum wage for 18 year olds?",
         f'From 1 April 2027 the minimum wage for workers aged 18 to 20 is {gbp(a18["dopo"])} an hour, up from {gbp(a18["prima"])} (April 2026). At 37.5 hours a week that is '
         f'{gbp(paga(a18["dopo"], 375)["sett"])} a week before tax. Source: GOV.UK, National Minimum Wage and National Living Wage rates.', "minimum wage for 18 year olds"),
        ("What is the minimum wage for 16 year olds?",
         f'The rate for workers under 18 is {gbp(u18["dopo"])} an hour from 1 April 2027, up from {gbp(u18["prima"])}; the Low Pay Commission calls it the 16-17 year old rate. '
         f'GOV.UK says a worker must be at least school leaving age to get the National Minimum Wage.', "minimum wage for 16 year olds"),
        ("What is the apprentice minimum wage?",
         f'The apprentice rate is {gbp(V["nmw_app"]["dopo"])} an hour from 1 April 2027 ({gbp(V["nmw_app"]["prima"])} from April 2026). GOV.UK says it applies to apprentices aged '
         f'under 19, or aged 19 or over and in the first year of their apprenticeship; other apprentices get the minimum wage for their age.', "apprentice minimum wage"),
        ("What is the National Living Wage?",
         f'It is the name of the minimum wage for workers aged 21 and over: {gbp(nlw["dopo"])} an hour from 1 April 2027, up {diff(nlw["prima"], nlw["dopo"])[1:]} from '
         f'{gbp(nlw["prima"])}. The Government announced the rate on 28 October 2026, accepting the recommendation of the Low Pay Commission.', "national living wage"),
        ("What is the minimum wage as an annual salary?",
         f'There is no official yearly figure: the minimum wage is an hourly rate. At {gbp(nlw["dopo"])} an hour, 37.5 hours a week for 52 weeks comes to '
         f'{gbp(fl["anno"])} a year before tax ({gbp(paga(nlw["dopo"], 400)["anno"])} at 40 hours). The calculator above works it out for other hours and ages.',
         "minimum wage annual salary"),
        ("How much is the minimum wage increase in April 2027?",
         f'All four rates rise by 3.9%: the National Living Wage by {diff(nlw["prima"], nlw["dopo"])[1:]} to {gbp(nlw["dopo"])}, the 18 to 20 rate by '
         f'{diff(a18["prima"], a18["dopo"])[1:]} to {gbp(a18["dopo"])}, and the under-18 and apprentice rates by {diff(u18["prima"], u18["dopo"])[1:]} to {gbp(u18["dopo"])}.',
         "minimum wage increase"),
    ])
    corpo += f + altre(G, "paga")
    pubblica(G, "paga", f'Minimum Wage April 2027: {gbp(nlw["dopo"])} an Hour, Rates by Age',
             f'UK minimum wage from 1 April 2027: {gbp(nlw["dopo"])} (21 and over), {gbp(a18["dopo"])} (18 to 20), {gbp(u18["dopo"])} (under 18 and apprentices). Old and new rates, pay calculator, GOV.UK sources.',
             "United Kingdom · minimum wage", "Minimum wage from April 2027: rates by age",
             f'The National Living Wage rises to <strong>{gbp(nlw["dopo"])}</strong> an hour on 1 April 2027. Every rate by age, the change on 2026, and what it comes to a week and a year.',
             corpo, "Minimum wage 2027", ["uk27_nmw", "uk27_lpc"], jsonld=[ld] if ld else None, script=G.PAY_SCRIPT)


def multipli(G, chiavi):
    """Settimana → quattro settimane e anno (52 settimane): calcolo nostro, dichiarato."""
    r = "".join(f'<tr><td>{V[k]["nome"]}</td>' + cella(k, "dopo", gbp(V[k]["dopo"])) + cella(k, "x4", gbp(V[k]["dopo"] * 4)) + cella(k, "x52", gbp(V[k]["dopo"] * 52))
                + cella(k, "d52", diff(V[k]["prima"] * 52, V[k]["dopo"] * 52)) + "</tr>" for k in chiavi)
    return (f'<div class="tab fissa c1"><table class="dati stretta"><thead><tr><th scope="col">{A1} (proposed)</th><th scope="col" class="n">A week</th><th scope="col" class="n">Four weeks</th>'
            f'<th scope="col" class="n">52 weeks</th><th scope="col" class="n">Change over 52 weeks</th></tr></thead><tbody>{r}</tbody></table></div>'
            '<p class="small">Our own calculation: the published weekly rate × 4 and × 52. The DWP publishes the weekly rate only.</p>')


def ppensione(G):
    n, b = V["sp_new"], V["sp_basic"]
    SP = ["sp_new", "sp_basic", "sp_b_lower", "sp_cd"]
    PC = ["pc_single", "pc_couple"]
    corpo = stats(G, [(gbp(n["dopo"]), f"new State Pension, full rate, a week ({A1}, proposed)"), (pctx(variazione(n["prima"], n["dopo"])), f'on {gbp(n["prima"])} ({A0})'),
                      (gbp(b["dopo"]), "basic State Pension a week"), (gbp(n["dopo"] * 52), "full new State Pension over 52 weeks")]) + G.AD
    corpo += stato_box(G)
    corpo += ('<h2>State Pension rates, 2026 to 2027 and 2027 to 2028</h2>' + tabella(G, SP, "Weekly rates, as in the DWP document.", evid=("sp_new",))
              + '<div class="testo">' + testo(G, "dwp_stato") + testo(G, "dwp_settimanali") + "</div>")
    corpo += ('<h2>New or basic State Pension: who gets which</h2><div class="testo"><p>GOV.UK draws the line by date of birth:</p>' + testo(G, "nsp_chi") + testo(G, "bsp_nuova")
              + '<p>The table above gives the full rates. GOV.UK explains why a person’s own amount can be lower or higher:</p>' + testo(G, "nsp_importo") + testo(G, "nsp_35")
              + testo(G, "nsp_protetto") + '<p>A personal forecast is on <a href="https://www.gov.uk/check-state-pension" rel="noopener">GOV.UK</a>. '
              f'The rate GOV.UK gives as current, {gbp(n["prima"])} a week, is the {A0} rate in the DWP document.</p></div>')
    corpo += '<h2>What the weekly rate comes to</h2>' + multipli(G, ["sp_new", "sp_basic"])
    corpo += ('<h2>Pension Credit, standard minimum guarantee</h2>' + tabella(G, PC, "Weekly rates, as in the DWP document.")
              + inflazione(G, "sp_new", "The full new State Pension") + righe_fonte(G, SP + PC))
    f, ld = faq(G, "uk_pensione", [
        ("How much is the State Pension?",
         f'The full new State Pension is {gbp(n["prima"])} a week in {A0} and {gbp(n["dopo"])} a week in {A1}. The basic State Pension (men born before 6 April 1951, women born '
         f'before 6 April 1953) is {gbp(b["prima"])} and then {gbp(b["dopo"])} a week. These are full rates: GOV.UK says a person’s amount depends on their National Insurance record.',
         "how much is state pension"),
        ("How much is the State Pension increase?",
         f'For {A1} the full new State Pension rises by {diff(n["prima"], n["dopo"])[1:]} a week ({pctx(variazione(n["prima"], n["dopo"]))[1:]}), from {gbp(n["prima"])} to '
         f'{gbp(n["dopo"])}. The basic State Pension rises by {diff(b["prima"], b["dopo"])[1:]} a week, from {gbp(b["prima"])} to {gbp(b["dopo"])}. The Department for Work and '
         f'Pensions published these as proposed rates on {G.FONTI["uk27_dwp"]["pubblicato"]}.', "state pension increase"),
        ("What is the new State Pension?",
         f'It is the State Pension for men born on or after 6 April 1951 and women born on or after 6 April 1953. Its full rate is {gbp(n["dopo"])} a week in {A1} '
         f'({gbp(n["dopo"] * 52)} over 52 weeks), up from {gbp(n["prima"])}.', "new state pension"),
        ("What is the full State Pension?",
         f'“Full” means the highest standard weekly rate: {gbp(n["dopo"])} for the new State Pension and {gbp(b["dopo"])} for the basic State Pension in {A1}. '
         f'GOV.UK says the amount can differ with the number of National Insurance qualifying years, contracting out before 2016 and the Additional State Pension; '
         f'with a record that started after April 2016, 35 qualifying years are needed for the full rate.', "full state pension"),
    ])
    corpo += f + altre(G, "pensione")
    pubblica(G, "pensione", f'State Pension Increase April 2027: {gbp(n["dopo"])} a Week',
             f'Proposed State Pension rates for 2027 to 2028: new State Pension {gbp(n["dopo"])} a week (from {gbp(n["prima"])}), basic State Pension {gbp(b["dopo"])}. DWP source.',
             "United Kingdom · State Pension", "State Pension rates for 2027 to 2028",
             f'The full new State Pension goes from {gbp(n["prima"])} to a proposed <strong>{gbp(n["dopo"])}</strong> a week. New and basic State Pension and Pension Credit, old against new.',
             corpo, "State Pension 2027", ["uk27_dwp", "uk27_dwp_indice"] + GUIDE_SP, jsonld=[ld] if ld else None)


def gruppo(G, gid, periodo, titolo=None, evid=()):
    g = GR[gid]
    return f'<h2 id="{gid}">{G.h(titolo or g["titolo"])}</h2>' + tabella(G, [v["k"] for v in g["voci"]], periodo, evid)


def psussidi(G):
    uc, pip = V["uc_s_25"], V["pip_dl_enh"]
    corpo = stats(G, [(gbp(uc["dopo"]), f"Universal Credit standard allowance, single 25 or over, a month ({A1}, proposed)"), (pctx(variazione(uc["prima"], uc["dopo"])), f'on {gbp(uc["prima"])} ({A0})'),
                      (gbp(pip["dopo"]), "PIP daily living, enhanced, a week"), (gbp(V["ca"]["dopo"]), "Carer’s Allowance a week")]) + G.AD
    corpo += stato_box(G)
    corpo += (gruppo(G, "uc", "Monthly rates, as in the DWP document (section “Universal Credit (monthly rates)”).", "Universal Credit, monthly amounts", evid=("uc_s_25",))
              + '<div class="testo"><p>The standard allowance is one part of a Universal Credit payment. GOV.UK:</p>' + testo(G, "uc_dipende") + testo(G, "uc_una")
              + f'<p>The amounts for limited capability for work are the same in both years in the document, apart from the higher rate for the claimants it describes. '
              f'The standard allowance GOV.UK gives as current for a single person under 25, {gbp(V["uc_s_u25"]["prima"])}, is the {A0} rate in the DWP document.</p></div>')
    corpo += gruppo(G, "pip", "Weekly rates.") + gruppo(G, "aa", "Weekly rates.") + gruppo(G, "dla", "Weekly rates.")
    corpo += gruppo(G, "carers", "Weekly rate.") + gruppo(G, "jsa", "Weekly personal rates.") + gruppo(G, "bereavement", "Lump sums and monthly payments, for deaths on or after 6 April 2017.")
    corpo += ('<div class="testo"><p>The State Pension and Pension Credit are on the <a href="/' + PAGINE["pensione"] + '">State Pension page</a>; Statutory Sick Pay and the '
              'maternity, paternity and adoption payments are on the <a href="/' + PAGINE["malattia"] + '">statutory pay page</a>. Other parts of the DWP document '
              '(Housing Benefit, Income Support, Employment and Support Allowance, deductions, the benefit cap) are not copied here: read them in the document itself.</p>'
              + testo(G, "dwp_stato") + "</div>")
    tutte = [v["k"] for gid in ("uc", "pip", "aa", "dla", "carers", "jsa", "bereavement") for v in GR[gid]["voci"]]
    corpo += inflazione(G, "uc_s_25", "The Universal Credit standard allowance for a single person aged 25 or over") + righe_fonte(G, tutte)
    f, ld = faq(G, "uk_sussidi", [
        ("What are the PIP rates?",
         f'In {A1} the daily living component is {gbp(V["pip_dl_std"]["dopo"])} a week (standard) or {gbp(V["pip_dl_enh"]["dopo"])} (enhanced), and the mobility component is '
         f'{gbp(V["pip_mob_std"]["dopo"])} (standard) or {gbp(V["pip_mob_enh"]["dopo"])} (enhanced). In {A0} they are {gbp(V["pip_dl_std"]["prima"])}, {gbp(V["pip_dl_enh"]["prima"])}, '
         f'{gbp(V["pip_mob_std"]["prima"])} and {gbp(V["pip_mob_enh"]["prima"])}.', "pip rates"),
        ("How much is Universal Credit?",
         f'The monthly standard allowance in {A1} is {gbp(V["uc_s_u25"]["dopo"])} for a single person under 25, {gbp(uc["dopo"])} for a single person aged 25 or over, '
         f'{gbp(V["uc_c_u25"]["dopo"])} for joint claimants both under 25 and {gbp(V["uc_c_25"]["dopo"])} for joint claimants when one or both are 25 or over. GOV.UK says the payment '
         f'also depends on any extra amounts, any money taken off and earnings.', "how much is universal credit"),
        ("What are the DLA rates?",
         f'In {A1} the care component is {gbp(V["dla_care_low"]["dopo"])}, {gbp(V["dla_care_mid"]["dopo"])} or {gbp(V["dla_care_high"]["dopo"])} a week (lowest, middle, highest) and the '
         f'mobility component is {gbp(V["dla_mob_low"]["dopo"])} or {gbp(V["dla_mob_high"]["dopo"])} a week (lower, higher).', "dla rates"),
        ("What are the Attendance Allowance rates?",
         f'Attendance Allowance is {gbp(V["aa_low"]["dopo"])} a week at the lower rate and {gbp(V["aa_high"]["dopo"])} at the higher rate in {A1}, up from '
         f'{gbp(V["aa_low"]["prima"])} and {gbp(V["aa_high"]["prima"])} in {A0}.', "attendance allowance rates"),
        ("What is the Carer’s Allowance rate?",
         f'Carer’s Allowance is {gbp(V["ca"]["dopo"])} a week in {A1}, up from {gbp(V["ca"]["prima"])} in {A0} ({diff(V["ca"]["prima"], V["ca"]["dopo"])[1:]} more a week).',
         "carers allowance rate"),
    ])
    corpo += f + altre(G, "sussidi")
    pubblica(G, "sussidi", "Benefit Rates 2027 to 2028: Universal Credit, PIP and More",
             f'Proposed UK benefit rates for 2027 to 2028 against 2026 to 2027: Universal Credit standard allowance {gbp(uc["dopo"])} a month, PIP, Attendance Allowance, DLA.',
             "United Kingdom · benefits", "Benefit rates for 2027 to 2028",
             f'Universal Credit, PIP, Attendance Allowance, DLA, Carer’s Allowance and Jobseeker’s Allowance: the rate for {A0}, the proposed rate for {A1} and the change, from the DWP document.',
             corpo, "Benefit rates 2027", ["uk27_dwp", "uk27_dwp_indice", "uk27_guida_uc"], icona="doc", jsonld=[ld] if ld else None)


def pmalattia(G):
    s, m = V["ssp"], V["smp"]
    corpo = stats(G, [(gbp(s["dopo"]), f"Statutory Sick Pay, standard rate, a week ({A1}, proposed)"), (pctx(variazione(s["prima"], s["dopo"])), f'on {gbp(s["prima"])} ({A0})'),
                      (gbp(m["dopo"]), "Statutory Maternity Pay, standard rate, a week"), (gbp(V["ma"]["dopo"]), "Maternity Allowance, standard rate, a week")]) + G.AD
    corpo += stato_box(G)
    corpo += (gruppo(G, "statutory", "Weekly rates, as in the DWP document. The earnings threshold and the Maternity Allowance threshold are weekly earnings.",
                     "Statutory Sick Pay and other statutory payments", evid=("ssp",))
              + '<div class="testo"><p>These are the standard weekly rates the DWP lists. For Statutory Sick Pay the standard rate is a ceiling, not the amount everyone '
              'gets. GOV.UK, with the rate in force today:</p>' + testo(G, "ssp_regola") + testo(G, "ssp_datore")
              + '<p>Who qualifies is on <a href="https://www.gov.uk/statutory-sick-pay/eligibility" rel="noopener">GOV.UK</a>; for the maternity, paternity and adoption '
              'payments see <a href="https://www.gov.uk/maternity-pay-leave" rel="noopener">Maternity pay and leave</a>. The standard rate of the maternity, paternity '
              'and shared parental payments is an upper limit too: GOV.UK gives each as the weekly rate or 90% of average weekly earnings, whichever is lower.</p>' + testo(G, "dwp_stato") + testo(G, "dwp_settimanali") + "</div>")
    corpo += inflazione(G, "ssp", "The standard rate of Statutory Sick Pay") + righe_fonte(G, [v["k"] for v in GR["statutory"]["voci"]])
    f, ld = faq(G, "uk_malattia", [
        ("How much is Statutory Sick Pay?",
         f'The standard rate of Statutory Sick Pay is {gbp(s["prima"])} a week in {A0} and {gbp(s["dopo"])} a week in {A1}, a rise of {diff(s["prima"], s["dopo"])[1:]} '
         f'({pctx(variazione(s["prima"], s["dopo"]))[1:]}). The DWP published the {A1} figure as a proposed rate on {G.FONTI["uk27_dwp"]["pubblicato"]}.', "how much is statutory sick pay"),
        ("How much is SSP?",
         f'SSP is {gbp(s["dopo"])} a week at the standard rate in {A1} ({gbp(s["prima"])} in {A0}). GOV.UK says an eligible employee gets the weekly rate or 80% of '
         f'normal weekly earnings, whichever is lower, for up to 28 weeks.', "how much is ssp"),
        ("What is the SSP rate from April 2027?",
         f'The proposed standard rate for {A1} is {gbp(s["dopo"])} a week, against {gbp(s["prima"])} for {A0}.', "ssp rate"),
        ("How much is Statutory Maternity Pay?",
         f'The standard weekly rate of Statutory Maternity Pay is {gbp(m["dopo"])} in {A1}, up from {gbp(m["prima"])} in {A0}; the earnings threshold goes from '
         f'{gbp(V["smp_soglia"]["prima"])} to {gbp(V["smp_soglia"]["dopo"])} a week. Statutory Paternity, Adoption and Shared Parental Pay have the same standard rate.',
         "statutory maternity pay"),
        ("How much is Maternity Allowance?",
         f'The standard rate of Maternity Allowance is {gbp(V["ma"]["dopo"])} a week in {A1}, up from {gbp(V["ma"]["prima"])} in {A0}. The Maternity Allowance threshold '
         f'stays at {gbp(V["ma_soglia"]["dopo"])} a week.', "maternity allowance"),
    ])
    corpo += f + altre(G, "malattia")
    pubblica(G, "malattia", f'Statutory Sick Pay 2027: SSP Rate {gbp(s["dopo"])} a Week',
             f'Proposed Statutory Sick Pay for 2027 to 2028: {gbp(s["dopo"])} a week, up from {gbp(s["prima"])}. Also Statutory Maternity and Paternity Pay ({gbp(m["dopo"])}). DWP source.',
             "United Kingdom · statutory pay", "Statutory Sick Pay and statutory pay rates, 2027 to 2028",
             f'The standard rate of SSP goes from {gbp(s["prima"])} to a proposed <strong>{gbp(s["dopo"])}</strong> a week. SSP, maternity, paternity, adoption and neonatal care pay, old against new.',
             corpo, "Statutory Sick Pay 2027", ["uk27_dwp", "uk27_dwp_indice", "uk27_guida_ssp"], icona="shield", jsonld=[ld] if ld else None)


CHIAVE = ["nlw", "nmw_18_20", "nmw_u18", "nmw_app", "sp_new", "sp_basic", "pc_single", "uc_s_u25", "uc_s_25", "uc_c_25", "pip_dl_enh", "pip_mob_enh", "aa_high", "ca", "ssp", "smp"]


def pindice(G):
    nlw, n, s, uc = V["nlw"], V["sp_new"], V["ssp"], V["uc_s_25"]
    corpo = stats(G, [(gbp(nlw["dopo"]), "National Living Wage an hour, from 1 April 2027"), (gbp(n["dopo"]), f"new State Pension a week ({A1}, proposed)"),
                      (gbp(uc["dopo"]), "Universal Credit, single 25 or over, a month (proposed)"), (gbp(s["dopo"]), "Statutory Sick Pay a week (proposed)")]) + G.AD
    corpo += stato_box(G)
    r = ""
    for k in CHIAVE:
        v = V[k]
        gnome = "Minimum wage" if k in NMW else next(g["titolo"] for g in D["gruppi"] if v in g["voci"])
        r += (f'<tr><td>{gnome}<br><span class="small">{v["nome"]} · {PER[v["periodo"]]}</span></td>' + cella(k, "prima", gbp(v["prima"])) + cella(k, "dopo", gbp(v["dopo"]))
              + cella(k, "diff", diff(v["prima"], v["dopo"])) + cella(k, "pct", pctx(variazione(v["prima"], v["dopo"]))) + "</tr>")
    corpo += (f'<h2>The main rates, old and new</h2><div class="tab fissa c1"><table class="dati stretta"><thead><tr><th scope="col">Rate</th><th scope="col" class="n">{A0}</th>'
              f'<th scope="col" class="n">{A1}</th><th scope="col" class="n">Change</th><th scope="col" class="n">%</th></tr></thead><tbody>{r}</tbody></table></div>'
              '<p class="small">Minimum wage: hourly rates from 1 April 2026 and 1 April 2027. Benefits and pensions: the rates the DWP lists for each year; '
              'for 2027 to 2028 they are proposed rates. '
              'The percentage is our own calculation from the two published rates, to one decimal place.</p>')
    li = "".join(f'<li><a href="/{PAGINE[k]}"><b>{G.h(b)}</b>{G.h(t)}<small>{G.h(x)}</small></a></li>' for k, b, t, x in (
        ("paga", gbp(nlw["dopo"]), "Minimum wage April 2027", "All four rates by age, pay calculator"),
        ("pensione", gbp(n["dopo"]), "State Pension 2027 to 2028", "New and basic State Pension, Pension Credit"),
        ("sussidi", gbp(uc["dopo"]), "Benefit rates 2027 to 2028", "Universal Credit, PIP, Attendance Allowance, DLA, Carer’s Allowance"),
        ("malattia", gbp(s["dopo"]), "Statutory Sick Pay 2027 to 2028", "SSP, maternity, paternity and adoption pay")))
    corpo += f'<h2>Each set of rates in full</h2><ul class="griglia">{li}</ul>'
    corpo += ('<h2>What is not announced, or not shown here</h2><div class="testo"><ul>'
              f'<li><strong>Final benefit and pension rates.</strong> As of {G.data_lunga(G.FONTI["uk27_dwp"]["letto_il"])} the DWP document is titled “proposed”; '
              'the legislation that fixes the rates had not been read on GOV.UK by us, so the benefit and pension tables say proposed.</li>'
              '<li><strong>Rates that are not in the two documents read.</strong> Payments made by HMRC or by the Scottish Government, tax allowances and National Insurance '
              'thresholds are not listed in the DWP rates document or on the minimum wage page, so they are not shown.</li>'
              '<li><strong>The day each benefit rate starts.</strong> The DWP document gives the year (“2027 to 2028”) and not a start day for each payment; the minimum wage '
              'page gives 1 April.</li></ul>' + testo(G, "dwp_stato") + testo(G, "lpc_annuncio") + "</div>")
    corpo += inflazione(G, "nlw", "The National Living Wage") + righe_fonte(G, CHIAVE)
    corpo += ('<ul class="griglia"><li><a href="/uk/"><b>CPI</b>UK inflation calculator<small>ONS CPI and RPI, 1800 to today</small></a></li>'
              '<li><a href="/uk/inflation-rate-by-year/"><b>%</b>UK inflation rate by year<small>CPI since 1989, RPI since 1801</small></a></li></ul>')
    pubblica(G, "indice", "UK Rates from April 2027: Minimum Wage, Pension, Benefits",
             f'UK rates from April 2027: National Living Wage {gbp(nlw["dopo"])}, new State Pension {gbp(n["dopo"])} a week, Universal Credit, PIP and SSP {gbp(s["dopo"])} (proposed). GOV.UK sources.',
             "United Kingdom · April 2027", "UK rates from April 2027",
             f'Minimum wage, State Pension, benefits and Statutory Sick Pay: the rate now, the announced or proposed rate for {A1} and the change, each copied from its GOV.UK page.',
             corpo, "UK rates from April 2027", FONTI_UK, icona="calendar")


def genera(G):
    pindice(G)
    ppaga(G)
    ppensione(G)
    psussidi(G)
    pmalattia(G)
