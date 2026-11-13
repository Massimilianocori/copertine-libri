"""Sezione "limiti di contribuzione" (USA): 401(k)/403(b)/457(b)/TSP, IRA, Roth IRA (con calcolatore), SIMPLE IRA, HSA.

Dati: dati/limiti.json (cifre IRS per anno, ognuna con la fonte e la frase IRS da cui viene; testi in dati/grezzi/irs/, scaricati da
raccolta/irs.py). Pagine solo dove c'è domanda misurata (dati/domanda.json, gruppo limiti_pensione, 13/11/2026):
  /retirement-limits/      indice: anno in corso e prossimo, storia, limiti e inflazione (CPI-U)   ("401k limits by year", "... history")
  /401k-limit/             401(k), 403(b), 457(b), TSP, catch-up 50+ e 60-63, 415(c)              ("401k contribution limits 2025" 135.000)
  /ira-limit/              IRA e soglie di deducibilità                                            ("ira contribution limit 2025" 40.500, "max ira contribution" 18.100)
  /roth-ira-income-limit/  soglie Roth + calcolatore (Publication 590-A, Worksheet 2-2)             ("roth ira income limits" 90.500, "roth ira contribution calculator" 1.300)
  /hsa-limit/              HSA e HDHP                                                              ("hsa contribution limits 2025" 60.500)
  /simple-ira-limit/       SIMPLE IRA                                                              ("simple ira contribution limits 2025" 12.100)
Nessun consiglio: solo i limiti pubblicati e il metodo IRS. genera.py chiama genera(G) passando sé stesso (niente import circolari).
"""
import json
import re
from pathlib import Path

RADICE = Path(__file__).resolve().parent
LIM = json.loads((RADICE / "dati" / "limiti.json").read_text(encoding="utf-8"))
A = {int(y): v for y, v in LIM["anni"].items()}
ANNI = sorted(A)
PRIMO, ULTIMO = ANNI[0], ANNI[-1]
CORRENTE = ULTIMO - 1  # novembre 2026: il 2027 è già annunciato, l'anno d'imposta in corso è il 2026
STATI = {"single": "Single or head of household",
         "mfj": "Married filing jointly or qualifying surviving spouse",
         "mfs": "Married filing separately, lived with spouse during the year",
         "mfs_sep": "Married filing separately, lived apart all year"}  # mfs_sep usa la fascia single (Publication 590-A)
FASCIA_STATO = {"single": "single", "mfj": "mfj", "mfs": "mfs", "mfs_sep": "single"}
PAGINE = {"indice": "retirement-limits/", "401k": "401k-limit/", "ira": "ira-limit/", "roth": "roth-ira-income-limit/",
          "hsa": "hsa-limit/", "simple": "simple-ira-limit/"}


def v(anno, k):
    x = A[anno].get(k)
    return x["valore"] if x else None


# ---------------------------------------------------------------- motore Roth (stile.ROTH_MOTORE_JS è la copia)
def roth_dati(anno):
    return {"ira": v(anno, "ira"), "cu": v(anno, "ira_catchup"), "mfj": v(anno, "roth_mfj"), "single": v(anno, "roth_single"), "mfs": v(anno, "roth_mfs")}


def roth_limite(y, stato, magi_c, over50, comp_c=None, altre_c=0):
    """Publication 590-A, Worksheet 2-2, in centesimi interi. y = roth_dati(anno). Ritorna esito ('full'/'partial'/'none') e limite in centesimi."""
    L = (y["ira"] + (y["cu"] if over50 else 0)) * 100
    base = L if comp_c is None else min(L, comp_c)  # riga 6
    if stato == "mfj":
        lo, hi, W = y["mfj"][0], y["mfj"][1], 10000
    elif stato == "mfs":
        lo, hi, W = y["mfs"][0], y["mfs"][1], 10000
    else:
        lo, hi, W = y["single"][0], y["single"][1], 15000
    l10 = max(0, base - (altre_c or 0))  # riga 10
    if magi_c <= lo * 100:
        esito, l8 = "full", base
    elif magi_c >= hi * 100:
        esito, l8 = "none", 0
    else:
        Wc, d = W * 100, magi_c - lo * 100
        num, den = base * (Wc - d), Wc * 1000
        l8 = -(-num // den) * 1000  # riga 8: per eccesso ai 10 $
        if 0 < l8 < 20000:
            l8 = 20000  # «If the result is less than $200, enter $200»
        esito = "partial"
    lim = 0 if esito == "none" else min(l8, l10)  # riga 11
    return {"esito": esito, "limite": lim, "lo": lo, "hi": hi, "W": W, "L": L, "base": base, "l8": l8, "l10": l10}


# ---------------------------------------------------------------- formati
def usd(x):
    return f"${x:,}"


def fascia(x):
    return f"{usd(x[0])}–{usd(x[1])}"


def cella(anno, k, fmt=usd, idx=None):
    x = v(anno, k)
    if x is None:
        return f'<td class="n vuoto" data-k="{k}">–</td>'
    val = x[idx] if idx is not None else x
    testo = fascia(val) if isinstance(val, list) else fmt(val)
    return f'<td class="n" data-k="{k}{"" if idx is None else "." + str(idx)}">{testo}</td>'


def fonte_link(G, fid):
    f = G.FONTI[fid]
    nome = re.sub(r"^IRS news release ", "", f["chi"])
    if nome == "Internal Revenue Service":  # pagine e pubblicazioni senza numero: il nome è il titolo del documento
        nome = "IRS, “" + re.sub(r" \(prior years table\)$", "", f["titolo"]) + "”"
    return f'<a href="{G.h(f["url"])}" rel="noopener">{G.h(nome)}</a>'


def tabella(G, intest, righe_fn, anni=None, alta=False, fonte=True):
    anni = anni or list(reversed(ANNI))
    th = "".join(f'<th scope="col"{" class=\"n\"" if i and (i < len(intest) - 1 or not fonte) else ""}>{G.h(t)}</th>' for i, t in enumerate(intest))
    corpo = "".join(f'<tr data-anno="{y}"{" class=\"evid\"" if y == CORRENTE else ""}><td>{y}</td>{righe_fn(y)}</tr>' for y in anni)
    return f'<div class="tab{" alta" if alta else ""}"><table class="dati"><thead><tr>{th}</tr></thead><tbody>{corpo}</tbody></table></div>'


def citazioni(G, anno, chiavi, titolo=None):
    """Le frasi IRS esatte (da dati/limiti.json) per un anno: <details> chiuso."""
    voci = []
    for k in chiavi:
        x = A[anno].get(k)
        if not x:
            continue
        f = G.FONTI[x["fonte"]]
        voci.append(f'<blockquote class="citaz">“{G.h(x.get("mostra") or x["frase"])}.”<cite>{fonte_link(G, x["fonte"])} · read on {G.data_lunga(f["letto_il"])}</cite></blockquote>')
    tit = titolo or f"The IRS wording for {anno}"
    return f'<details class="irs"><summary>{G.h(tit)}</summary>{"".join(voci)}</details>'


def citazione_anno(G, anno, k):
    """Una sola frase d'anno (da dati/limiti.json) con la sua fonte."""
    x = A[anno][k]
    f = G.FONTI[x["fonte"]]
    return f'<blockquote class="citaz">“{G.h(x.get("mostra") or x["frase"])}.”<cite>{fonte_link(G, x["fonte"])} · read on {G.data_lunga(f["letto_il"])}</cite></blockquote>'


def testo_irs(G, k):
    x = LIM["testi"][k]
    return f'<blockquote class="citaz">“{G.h(x["frase"])}.”<cite>{fonte_link(G, x["fonte"])}</cite></blockquote>'


DISCL = ("<strong>General information, not financial or investment advice, and not tax advice.</strong> The figures are the annual limits "
         "published by the Internal Revenue Service (IRS), linked on each page. A plan can set lower limits, and other rules (your compensation, "
         "the type of plan, employer contributions, contributions to other plans) change what you personally may contribute. We do not promote "
         "any account, plan or product. Ask your plan administrator or a tax professional about your own situation.")


def briciole(nome, chiave):
    b = [("Home", ""), ("Retirement limits", PAGINE["indice"])]
    return b + ([(nome, PAGINE[chiave])] if chiave != "indice" else [])


def fonti_anni(G, chiavi_fonte):
    """Fonti della pagina: quelle dell'anno in corso e del prossimo; gli altri anni sono linkati riga per riga nella tabella."""
    ids = []
    for y in (ULTIMO, CORRENTE):
        for k in chiavi_fonte:
            x = A[y].get(k)
            if x and x["fonte"] not in ids:
                ids.append(x["fonte"])
    return ids


def altre_pagine(G, tranne):
    voci = [("401k", "401(k)", "401(k), 403(b), 457(b) and TSP limits", "Employee deferrals, catch-up at 50 and at 60–63"),
            ("ira", "IRA", "IRA contribution limits", "Traditional and Roth IRA limit, deduction income ranges"),
            ("roth", "Roth", "Roth IRA income limits", "Phase-out ranges and the contribution calculator"),
            ("hsa", "HSA", "HSA contribution limits", "Self-only, family, age 55 and HDHP amounts"),
            ("simple", "SIMPLE", "SIMPLE IRA limits", "Deferral limits and catch-up amounts"),
            ("indice", "All", "All retirement limits", f"Every account, {PRIMO}–{ULTIMO}")]
    li = "".join(f'<li><a href="/{PAGINE[k]}"><b>{G.h(b)}</b>{G.h(t)}<small>{G.h(s)}</small></a></li>' for k, b, t, s in voci if k != tranne)
    return f'<h2>Other limits</h2><ul class="griglia">{li}</ul>'


def due_anni(a, b, y0, y1, fmt=usd):
    """«$7,500 for 2026 and 2027» se uguali, altrimenti «$24,500 for 2026 and $25,500 for 2027»."""
    return f"{fmt(a)} for {y0} and {y1}" if a == b else f"{fmt(a)} for {y0} and {fmt(b)} for {y1}"


def faq(G, pid, voci):
    return G.faq_blocco(pid, [(q, a, ricerca, "us") for q, a, ricerca in voci])


def stats(G, voci):
    return '<div class="card stats">' + "".join(f'<div class="stat{" main" if i == 0 else ""}"><b>{b}</b><span>{G.h(s)}</span></div>' for i, (b, s) in enumerate(voci)) + "</div>"


def pubblica(G, chiave, titolo, descr, eyebrow, h1, sub, corpo, nome_bc, icona="coins", jsonld=None, script=""):
    testata = G.banda(eyebrow, h1, sub, G.trust([("check", "Figures quoted from IRS documents"), ("calendar", f"{PRIMO}–{ULTIMO}, including {ULTIMO}"),
                                                ("info", "No advice, no products")]), icona=icona)
    G.pagina(PAGINE[chiave], titolo, descr, corpo, testata, "us", briciole=briciole(nome_bc, chiave), jsonld=jsonld, disclaimer=DISCL, script=script)


# ---------------------------------------------------------------- pagine
def p401k(G):
    y1, y0 = ULTIMO, CORRENTE
    tot = lambda y: v(y, "k401") + v(y, "catchup")  # noqa: E731
    corpo = ('<div class="card risposta pull">'
             f'<p>In {y0} employees can defer up to<span class="big">{usd(v(y0, "k401"))}</span>into a 401(k), 403(b), governmental 457(b) plan or the '
             f'Thrift Savings Plan. For {y1} the IRS has raised the limit to <strong>{usd(v(y1, "k401"))}</strong>. From age 50 the catch-up adds '
             f'{usd(v(y0, "catchup"))} in {y0} and {usd(v(y1, "catchup"))} in {y1}; at ages 60 to 63 it is {usd(v(y0, "catchup_6063"))} and '
             f'{usd(v(y1, "catchup_6063"))}.</p></div>')
    corpo += stats(G, [(usd(v(y1, "k401")), f"employee limit {y1}"), (usd(tot(y1)), f"with the age-50 catch-up, {y1}"),
                       (usd(v(y1, "k401") + v(y1, "catchup_6063")), f"with the age 60–63 catch-up, {y1}"), (usd(v(y1, "dc415c")), f"all contributions, plans of one employer, {y1}")])
    corpo += G.AD
    corpo += (f'<h2>401(k) limits by year, {PRIMO}–{ULTIMO}</h2><p>The elective deferral limit is shared by 401(k), 403(b) and Thrift Savings Plan accounts; '
              'the limit for governmental 457(b) plans is set separately and has been the same amount in every year shown. Amounts in US dollars per person '
              f'per calendar year; the highlighted row is {y0}.</p>')
    corpo += tabella(G, ["Year", "Employee limit", "Catch-up 50+", "Catch-up 60–63", "Limit + catch-up 50+", "457(b) limit", "All contributions (415(c))", "IRS source"],
                     lambda y: cella(y, "k401") + cella(y, "catchup") + cella(y, "catchup_6063") + f'<td class="n" data-tot="{tot(y)}">{usd(tot(y))}</td>'
                     + cella(y, "k457") + cella(y, "dc415c") + f'<td class="src">{fonte_link(G, A[y]["k401"]["fonte"])}</td>')
    corpo += ('<p class="small">“All contributions” is the section 415(c) limit for defined contribution plans. The 60–63 catch-up applies instead of the '
              'age-50 catch-up for those ages; the IRS first published it for 2025.</p>')
    corpo += ('<h2>What the limits cover</h2><div class="testo">'
              '<p><strong>Employee limit.</strong> One limit per person per calendar year for elective deferrals, pre-tax and Roth together, however many plans '
              'you are in; a 457(b) plan has its own separate limit. The IRS explains:</p></div>'
              + testo_irs(G, "k401_somma") + testo_irs(G, "k401_457") + testo_irs(G, "k401_piano_limite")
              + '<div class="testo"><p><strong>Catch-up 50+.</strong> An extra amount for participants aged 50 or over at the end of the calendar year. '
              'In the words of the IRS:</p></div>' + testo_irs(G, "k401_catchup_piano")
              + '<div class="testo"><p><strong>Catch-up 60–63.</strong> A higher catch-up limit for employees who attain age 60, 61, 62 or 63 during the year '
              '(a change made in SECURE 2.0); the IRS sentences are under “The IRS wording” below.</p>'
              '<p><strong>All contributions (415(c)).</strong> The overall limit on what goes into your accounts in the plans of one employer. '
              'Catch-up contributions are not part of the total, as the IRS lists it:</p></div>' + testo_irs(G, "k401_415c")
              + f'<div class="testo"><p><strong>Roth catch-up wage threshold.</strong> The IRS notices set a wage threshold that decides whether catch-up '
              f'contributions must be designated as Roth contributions: {usd(v(y0, "roth_catchup_soglia"))} of {y0 - 1} wages for {y0} catch-up contributions '
              f'and {usd(v(y1, "roth_catchup_soglia"))} of {y0} wages for {y1} catch-up contributions. The wages are those from the employer that sponsors '
              'the plan.</p></div>' + testo_irs(G, "roth_catchup_salario"))
    corpo += citazioni(G, y1, ["k401", "k457", "catchup", "catchup_6063", "roth_catchup_soglia", "dc415c"])
    corpo += citazioni(G, y0, ["k401", "catchup", "catchup_6063", "roth_catchup_soglia", "dc415c"])
    corpo += (f'<p>How do these limits compare with prices? The <a href="/{PAGINE["indice"]}#inflation">retirement limits overview</a> puts the '
              f'{PRIMO} amounts in today\'s dollars with the CPI-U.</p>')
    f, ld = faq(G, "401k", [
        ("How much can I put in my 401(k)?",
         f'Up to {usd(v(y0, "k401"))} of your own deferrals in {y0} and {usd(v(y1, "k401"))} in {y1}, plus the catch-up if you are 50 or older and your plan '
         'permits it. The IRS notes that a plan\'s terms may impose a lower limit.', "how much can i put in my 401k"),
        ("What is the 401(k) catch-up contribution?",
         f'An extra amount for employees aged 50 or over: {usd(v(y0, "catchup"))} in {y0} and {usd(v(y1, "catchup"))} in {y1}, so up to {usd(tot(y0))} and '
         f'{usd(tot(y1))} in total deferrals.', "401k catch up"),
        ("What is the super catch-up for ages 60 to 63?",
         f'Under SECURE 2.0, employees who turn 60, 61, 62 or 63 during the year have a higher catch-up limit: {usd(v(2025, "catchup_6063"))} in 2025, '
         f'{usd(v(y0, "catchup_6063"))} in {y0} and {usd(v(y1, "catchup_6063"))} in {y1}, instead of the age-50 catch-up.', "super catch up 401k"),
        ("What are the 403(b) contribution limits?",
         f'The same as for a 401(k): {usd(v(y0, "k401"))} in {y0} and {usd(v(y1, "k401"))} in {y1}, with the same catch-up amounts. The IRS announces one '
         'limit for 401(k), 403(b), governmental 457 plans and the Thrift Savings Plan.', "403b contribution limits"),
    ])
    corpo += f + altre_pagine(G, "401k") + G.fonti_box(fonti_anni(G, ["k401", "catchup_6063"]) + ["irs_401k_limiti", "irs_piu_piani", "irs_catchup", "irs_cola_pagina"])
    pubblica(G, "401k", f"401(k) Contribution Limits {y0} & {y1}, Catch-Up and History",
             f"401(k), 403(b), 457(b) and TSP limits from the IRS: {usd(v(y0, 'k401'))} for {y0}, {usd(v(y1, 'k401'))} for {y1}, catch-up at 50 and at 60–63, every year since {PRIMO}.",
             "401(k) · 403(b) · 457(b) · TSP", f"401(k) contribution limits for {y0} and {y1}",
             f"Employee deferral limit, catch-up contributions and the total limit, as published by the IRS each year from {PRIMO} to {ULTIMO}.",
             corpo, "401(k) limits", jsonld=[ld] if ld else None)


def pira(G):
    y1, y0 = ULTIMO, CORRENTE
    corpo = ('<div class="card risposta pull">'
             f'<p>The IRA contribution limit is<span class="big">{usd(v(y0, "ira"))}</span>for {y0}, and {usd(v(y0, "ira") + v(y0, "ira_catchup"))} if you are 50 or '
             f'older. For {y1} it stays at <strong>{usd(v(y1, "ira"))}</strong> ({usd(v(y1, "ira") + v(y1, "ira_catchup"))} from age 50). It is one limit for all '
             'your traditional and Roth IRAs together.</p></div>')
    corpo += stats(G, [(usd(v(y1, "ira")), f"IRA limit {y1}"), (usd(v(y1, "ira_catchup")), f"catch-up at 50+, {y1}"),
                       (fascia(v(y1, "ded_single")), f"deduction phase-out, single, covered by a work plan, {y1}"),
                       (fascia(v(y1, "ded_mfj")), f"deduction phase-out, joint, covered by a work plan, {y1}")])
    corpo += G.AD
    corpo += f'<h2>IRA contribution limits by year, {PRIMO}–{ULTIMO}</h2>'
    corpo += tabella(G, ["Year", "IRA limit", "Catch-up 50+", "Limit at 50+", "IRS source"],
                     lambda y: cella(y, "ira") + cella(y, "ira_catchup") + f'<td class="n">{usd(v(y, "ira") + v(y, "ira_catchup"))}</td>'
                     + f'<td class="src">{fonte_link(G, A[y]["ira"]["fonte"])}</td>')
    corpo += ('<p class="small">The limit also cannot be more than your taxable compensation for the year. Roth IRA contributions are further limited by income: '
              f'see <a href="/{PAGINE["roth"]}">Roth IRA income limits</a> and the calculator.</p>')
    corpo += ('<h2>Traditional IRA deduction: income phase-out ranges</h2><div class="testo"><p>Anyone with taxable compensation can contribute to a traditional '
              'IRA. Whether the contribution is <em>deductible</em> depends on income when you or your spouse are covered by a retirement plan at work. Inside each '
              'range the deduction is reduced; above it there is no deduction. The IRS explains:</p></div>' + testo_irs(G, "ira_deduzione_regola")
              + '<p>Publication 590-A, on who can contribute to a traditional IRA:</p>' + testo_irs(G, "ira_eta"))
    corpo += tabella(G, ["Year", "Single or head of household, covered", "Married filing jointly, contributor covered", "Contributor not covered, spouse covered", "IRS source"],
                     lambda y: cella(y, "ded_single") + cella(y, "ded_mfj") + cella(y, "ded_spouse") + f'<td class="src">{fonte_link(G, A[y]["ded_mfj"]["fonte"])}</td>')
    corpo += ('<p class="small">Married filing separately and covered by a work plan: the range is $0 to $10,000 in every year shown (not adjusted for inflation). '
              'In the words of the IRS:</p>' + testo_irs(G, "ira_ded_mfs"))
    corpo += citazioni(G, y1, ["ira", "ira_catchup", "ded_single", "ded_mfj", "ded_spouse"])
    f, ld = faq(G, "ira", [
        ("What is the maximum IRA contribution?",
         f'{due_anni(v(y0, "ira"), v(y1, "ira"), y0, y1)}, or {due_anni(v(y0, "ira") + v(y0, "ira_catchup"), v(y1, "ira") + v(y1, "ira_catchup"), y0, y1)} '
         'if you are 50 or older, across all your traditional and Roth IRAs, and never more than your taxable compensation.', "max ira contribution"),
        ("What are the traditional IRA income limits?",
         'There is no income limit to contribute to a traditional IRA. Income limits apply to the deduction when you or your spouse are covered by a '
         f'workplace plan: for {y0}, {fascia(v(y0, "ded_single"))} for single filers and {fascia(v(y0, "ded_mfj"))} for joint filers who are covered; '
         f'{fascia(v(y0, "ded_spouse"))} when only the spouse is covered.', "traditional ira income limits"),
        ("What is the IRA contribution deadline?",
         'Contributions for a year can be made during that year or by the due date of the tax return for that year, not including extensions. The IRS '
         'notes that for most people the 2025 contributions had to be made by April 15, 2026.', "ira contribution deadline"),
    ])
    corpo += testo_irs(G, "ira_scadenza") + f + altre_pagine(G, "ira") + G.fonti_box(fonti_anni(G, ["ira", "ira_catchup"]) + ["irs_p590a"])
    pubblica(G, "ira", f"IRA Contribution Limits {y0} & {y1} and Deduction Income Limits",
             f"IRA limit from the IRS: {usd(v(y0, 'ira'))} for {y0} and {y1}, catch-up at 50, and the traditional IRA deduction income ranges for every year since {PRIMO}.",
             "Traditional and Roth IRA", f"IRA contribution limits for {y0} and {y1}",
             "One limit for all your traditional and Roth IRAs, the catch-up from age 50, and the income ranges for deducting traditional IRA contributions.",
             corpo, "IRA limits", jsonld=[ld] if ld else None)


def calcolatore_roth(G):
    y0 = CORRENTE
    ini = {"anno": y0, "stato": "single", "magi": 160000, "over50": False}
    r = roth_limite(roth_dati(y0), "single", ini["magi"] * 100, False)
    opz_anni = "".join(f'<option value="{y}"{" selected" if y == y0 else ""}>{y}</option>' for y in reversed(ANNI))
    opz_stati = "".join(f'<option value="{k}"{" selected" if k == "single" else ""}>{G.h(t)}</option>' for k, t in STATI.items())
    T = {"full": "In {anno} you can contribute the full amount", "partial": "In {anno} your contribution is reduced to",
         "none": "In {anno} you cannot contribute to a Roth IRA", "sotto": "Roth IRA limit for {anno}, before contributions you already made to other IRAs",
         "full_meno": "In {anno} your income does not reduce the limit. You can contribute up to",
         "sotto_altre": "Roth IRA limit for {anno}, after the contributions to other IRAs you entered",
         "fascia": "phase-out range for {anno}", "max": "full limit (under 50)", "max50": "full limit (50 or older)",
         "magi": "Enter your modified AGI, for example 150000.", "importo": "Amounts must be numbers, for example 7000 or 7,000.",
         "foglio": "Show the IRS worksheet lines", "r1": "Modified AGI", "r2": "Start of the phase-out range", "r3": "Line 1 minus line 2",
         "r4": "Width of the range", "r5": "Line 3 ÷ line 4 (exact)", "r6": "Lesser of the IRA limit and your compensation",
         "r8": "Line 6 minus line 6 × line 5, rounded up to $10 (at least $200)", "r10": "Line 6 minus contributions to other IRAs",
         "nota": "Reduced limit = the lesser of line 8 and line 10 (Publication 590-A, Worksheet 2-2)."}
    dati = {"anni": {str(y): roth_dati(y) for y in ANNI}, "stati": STATI, "t": T}
    tit = (T["full"] if r["esito"] == "full" else T["partial"] if r["esito"] == "partial" else T["none"]).replace("{anno}", str(y0))
    stat = (f'<div class="ris-main roth-{r["esito"]}"><span>{G.h(tit)}</span><b data-roth-limite>{usd(r["limite"] // 100)}</b>'
            f'<span>{G.h(T["sotto"].replace("{anno}", str(y0)))}</span></div>')
    js = json.dumps(dati, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    form = f"""<form class="calc-in" data-roth novalidate>
<label><span class="lab">Tax year</span><select name="y">{opz_anni}</select></label>
<label><span class="lab">Filing status</span><select name="s">{opz_stati}</select></label>
<label><span class="lab">Modified AGI for Roth IRA purposes</span><span class="campo" data-sym="$"><input type="text" name="m" inputmode="decimal" autocomplete="off" value="{ini['magi']:,}"></span></label>
<label class="spunta"><input type="checkbox" name="e"> Age 50 or older by the end of the year</label>
<label><span class="lab">Taxable compensation <span class="opz">(optional)</span></span><span class="campo" data-sym="$"><input type="text" name="c" inputmode="decimal" autocomplete="off" placeholder="leave empty if above the limit"></span></label>
<label><span class="lab">Already contributed to traditional IRAs this year <span class="opz">(optional)</span></span><span class="campo" data-sym="$"><input type="text" name="o" inputmode="decimal" autocomplete="off" placeholder="0"></span></label>
</form>"""
    return (f'<section class="card calc" id="calc"><div class="calc-h"><h2>{G.ico("calc")}Roth IRA contribution calculator</h2>'
            f'<span class="pill">{PRIMO}–{ULTIMO}</span></div><div class="calc-g">{form}<div class="calc-out" data-roth-out aria-live="polite">{stat}</div></div>'
            f'<p class="calc-f">Runs in your browser; nothing you type is sent anywhere. Method: IRS Publication 590-A, Worksheet 2-2.</p></section>'
            f'<script type="application/json" id="roth-dati">{js}</script>')


def proth(G):
    y1, y0 = ULTIMO, CORRENTE
    corpo = '<div class="pull">' + calcolatore_roth(G) + "</div>"
    corpo += stats(G, [(fascia(v(y0, "roth_single")), f"single and head of household, {y0}"), (fascia(v(y0, "roth_mfj")), f"married filing jointly, {y0}"),
                       (fascia(v(y1, "roth_single")), f"single and head of household, {y1}"), (fascia(v(y1, "roth_mfj")), f"married filing jointly, {y1}")])
    corpo += G.AD
    corpo += (f'<h2>Roth IRA income limits by year, {PRIMO}–{ULTIMO}</h2><p>Modified adjusted gross income (MAGI) ranges in which the Roth IRA contribution '
              'limit is phased out. Below the range you can contribute the full limit; inside it the limit is reduced; at or above the top you cannot contribute.</p>')
    corpo += tabella(G, ["Year", "Single, head of household", "Married filing jointly", "Married filing separately*", "Full limit (50+)", "IRS source"],
                     lambda y: cella(y, "roth_single") + cella(y, "roth_mfj") + cella(y, "roth_mfs")
                     + f'<td class="n">{usd(v(y, "ira"))} ({usd(v(y, "ira") + v(y, "ira_catchup"))})</td><td class="src">{fonte_link(G, A[y]["roth_mfj"]["fonte"])}</td>')
    corpo += ('<p class="small">* If you lived with your spouse at any time during the year. Married filing separately without living with your spouse uses the '
              'single range. A qualifying surviving spouse uses the joint range.</p>')
    corpo += ('<h2>How the reduced limit is calculated</h2><div class="testo"><p>The calculator follows the IRS worksheet for a reduced Roth IRA contribution '
              '(Publication 590-A, Worksheet 2-2) line by line: the part of your MAGI above the start of the range is divided by the width of the range '
              '($15,000 for single filers, $10,000 for joint filers and for married filing separately), that share of the limit is removed, and the result is '
              'rounded up to the next $10, with a minimum of $200 when it is above zero. The worksheet asks for the ratio “rounded to at least three places”; '
              'we use the exact ratio, so a result can be $10 away from one worked out by hand with the ratio rounded to three places.</p>'
              '<p>Worked example from the IRS worksheet (2025, single, MAGI $151,000, under 50): 1,000 ÷ 15,000 = 0.067; 7,000 − 469 = 6,531, rounded up to '
              f'<strong>$6,540</strong>. The calculator gives {usd(roth_limite(roth_dati(2025), "single", 15100000, False)["limite"] // 100)}.</p></div>')
    corpo += "".join(testo_irs(G, k) for k in ("roth_riga5", "roth_riga8", "roth_riga11"))
    corpo += citazioni(G, y1, ["roth_single", "roth_mfj", "roth_mfs", "ira", "ira_catchup"])
    corpo += citazioni(G, y0, ["roth_single", "roth_mfj", "roth_mfs", "ira", "ira_catchup"])
    f, ld = faq(G, "roth", [
        ("Can I contribute to a Roth IRA?",
         f'You can if you have taxable compensation and your modified AGI is below the top of the range for your filing status: for {y0}, under '
         f'{usd(v(y0, "roth_single")[1])} for single and head of household, under {usd(v(y0, "roth_mfj")[1])} for married filing jointly, and under '
         '$10,000 for married filing separately if you lived with your spouse. Inside the range the limit is reduced.', "can i contribute to a roth ira"),
        ("How much can you put in a Roth IRA?",
         f'Up to {due_anni(v(y0, "ira"), v(y1, "ira"), y0, y1)} '
         f'({due_anni(v(y0, "ira") + v(y0, "ira_catchup"), v(y1, "ira") + v(y1, "ira_catchup"), y0, y1)} from age 50), minus anything you put into traditional IRAs for the same year, and less if your income '
         'is inside the phase-out range.', "how much can you put in a roth ira"),
        ("What is the Roth IRA income limit for married filing separately?",
         'If you lived with your spouse at any time during the year, the phase-out range is $0 to $10,000 of modified AGI and it is not adjusted for '
         'inflation. If you did not live with your spouse at any time during the year, you use the single range.', "roth ira married filing separately"),
        ("What is the Roth IRA contribution deadline?",
         'Contributions for a year can be made during that year or by the due date of the tax return for that year, not including extensions.',
         "roth ira deadline"),
    ])
    corpo += testo_irs(G, "roth_chi") + f + altre_pagine(G, "roth") + G.fonti_box(fonti_anni(G, ["roth_mfj"]) + ["irs_p590a"])
    ld_app = G.jsonld_app("Roth IRA contribution calculator", f"{G.URL_SITO}/{PAGINE['roth']}", "en-US")
    pubblica(G, "roth", f"Roth IRA Income Limits {y0} & {y1} + Contribution Calculator",
             f"Roth IRA income phase-out ranges from the IRS for {PRIMO}–{ULTIMO} and a calculator for your reduced limit, line by line from the IRS worksheet.",
             "Roth IRA", f"Roth IRA income limits for {y0} and {y1}",
             "Check whether your income allows a full, reduced or no Roth IRA contribution, with the IRS phase-out ranges for every year.",
             corpo, "Roth IRA income limits", icona="calc", jsonld=[ld_app] + ([ld] if ld else []),
             script=f'<script src="/assets/{G.ROTH_FILE}" defer></script>')


def phsa(G):
    y1, y0 = ULTIMO, CORRENTE
    corpo = ('<div class="card risposta pull">'
             f'<p>For {y0} you can put up to<span class="big">{usd(v(y0, "hsa_self"))}</span>into a health savings account with self-only HDHP coverage, '
             f'or {usd(v(y0, "hsa_family"))} with family coverage. For {y1} the limits are <strong>{usd(v(y1, "hsa_self"))}</strong> and '
             f'<strong>{usd(v(y1, "hsa_family"))}</strong>. From age 55 the limit is {usd(v(y1, "hsa_catchup"))} higher in every year.</p></div>')
    corpo += stats(G, [(usd(v(y1, "hsa_self")), f"self-only coverage, {y1}"), (usd(v(y1, "hsa_family")), f"family coverage, {y1}"),
                       (usd(v(y1, "hdhp")[0]), f"minimum HDHP deductible, self-only, {y1}"), (usd(v(y1, "hdhp")[2]), f"HDHP out-of-pocket maximum, self-only, {y1}")])
    corpo += G.AD
    corpo += f'<h2>HSA contribution limits by year, {PRIMO}–{ULTIMO}</h2>'
    corpo += tabella(G, ["Year", "Self-only", "Family", "Extra at 55+", "IRS source"],
                     lambda y: cella(y, "hsa_self") + cella(y, "hsa_family") + cella(y, "hsa_catchup") + f'<td class="src">{fonte_link(G, A[y]["hsa_self"]["fonte"])}</td>')
    corpo += (f'<p class="small">Extra at 55+: the additional contribution is fixed by law at $1,000 for 2009 and every later year (Internal Revenue Code, '
              'section 223(b)(3)(B)) and is not adjusted for inflation: the cost-of-living adjustment of section 223(g) covers only the self-only and family '
              f'limits and the HDHP amounts. For {PRIMO}–2025 the source is the IRS Publication 969 of each year; the editions for {CORRENTE} and {ULTIMO} are not '
              'published yet, so for those two years the source is the statute itself. 2018: the IRS first lowered the family limit to $6,850 (Rev. Proc. 2018-18) and then '
              'allowed taxpayers to use the $6,900 originally published (Rev. Proc. 2018-27).</p>')
    corpo += (f'<h2>High deductible health plan (HDHP) amounts, {PRIMO}–{ULTIMO}</h2><p>To contribute to an HSA you need coverage under a high deductible '
              'health plan: a deductible at least as high as the minimum, and out-of-pocket expenses (not premiums) no higher than the maximum. From 2026 '
              'there is one exception to these amounts, for bronze and catastrophic plans offered as individual coverage through an Exchange; IRS Notice 2026-5 says:</p>'
              + testo_irs(G, "hsa_bronze"))
    corpo += tabella(G, ["Year", "Min. deductible, self-only", "Min. deductible, family", "Out-of-pocket max, self-only", "Out-of-pocket max, family", "IRS source"],
                     lambda y: cella(y, "hdhp", idx=0) + cella(y, "hdhp", idx=1) + cella(y, "hdhp", idx=2) + cella(y, "hdhp", idx=3)
                     + f'<td class="src">{fonte_link(G, A[y]["hdhp"]["fonte"])}</td>')
    corpo += citazioni(G, y1, ["hsa_self", "hsa_family", "hdhp"]) + citazioni(G, y0, ["hsa_self", "hsa_family", "hdhp"])
    corpo += ('<details class="irs"><summary>The wording for the age-55 contribution: Publication 969 (2025) and the statute</summary>'
              + citazione_anno(G, 2025, "hsa_catchup") + testo_irs(G, "hsa_55_legge") + citazione_anno(G, y1, "hsa_catchup")
              + testo_irs(G, "hsa_55_non_indicizzato") + '</details>')
    f, ld = faq(G, "hsa", [
        ("Is there a catch-up contribution for an HSA?",
         'Yes. If you are an eligible individual aged 55 or older at the end of your tax year, your HSA contribution limit is $1,000 higher '
         f'(Publication 969, editions {PRIMO}–2025). The amount is fixed by section 223(b)(3) of the Internal Revenue Code for 2009 and later years and is '
         f'not adjusted for inflation, so it is also $1,000 for {y0} and {y1}.', "hsa catch up contribution"),
        ("How much can I contribute to my HSA?",
         f'For {y0}: {usd(v(y0, "hsa_self"))} with self-only HDHP coverage or {usd(v(y0, "hsa_family"))} with family coverage. For {y1}: '
         f'{usd(v(y1, "hsa_self"))} and {usd(v(y1, "hsa_family"))}, plus $1,000 from age 55.', "how much can i contribute to my hsa"),
        ("What is the HSA contribution deadline?",
         'Publication 969 (2025) says that contributions to an HSA for 2025 can be made through April 15, 2026.', "hsa contribution deadline"),
    ])
    corpo += testo_irs(G, "hsa_scadenza") + f + altre_pagine(G, "hsa") + G.fonti_box(fonti_anni(G, ["hsa_self"]) + ["irs_p969_2025", "usc_223", "irs_n_hsa_obbba"])
    pubblica(G, "hsa", f"HSA Contribution Limits {y0} & {y1} (Self-Only, Family, 55+)",
             f"HSA limits from the IRS: {usd(v(y0, 'hsa_self'))} self-only and {usd(v(y0, 'hsa_family'))} family for {y0}, {usd(v(y1, 'hsa_self'))} and {usd(v(y1, 'hsa_family'))} for {y1}, plus HDHP amounts.",
             "Health savings account", f"HSA contribution limits for {y0} and {y1}",
             f"Self-only and family limits, the extra $1,000 from age 55 and the high deductible health plan amounts, from IRS revenue procedures since {PRIMO}.",
             corpo, "HSA limits", icona="shield", jsonld=[ld] if ld else None)


def psimple(G):
    y1, y0 = ULTIMO, CORRENTE
    corpo = ('<div class="card risposta pull">'
             f'<p>The SIMPLE IRA deferral limit is<span class="big">{usd(v(y0, "simple"))}</span>for {y0} and {usd(v(y1, "simple"))} for {y1}. Some plans of '
             f'certain eligible employers have a higher limit ({usd(v(y0, "simple_alto"))} in {y0}, {usd(v(y1, "simple_alto"))} in {y1}). From age 50 the catch-up '
             f'adds {usd(v(y0, "simple_catchup"))} in most plans.</p></div>')
    corpo += stats(G, [(usd(v(y1, "simple")), f"general limit, {y1}"), (usd(v(y1, "simple_alto")), f"higher limit for certain employers, {y1}"),
                       (usd(v(y1, "simple_catchup")), f"catch-up 50+, most plans, {y1}"), (usd(v(y1, "simple_catchup_6063")), f"catch-up at 60–63, {y1}")])
    corpo += G.AD
    corpo += f'<h2>SIMPLE IRA limits by year, {PRIMO}–{ULTIMO}</h2>'
    corpo += tabella(G, ["Year", "General limit", "Higher limit*", "Catch-up 50+", "Catch-up 50+, higher-limit plans*", "Catch-up 60–63", "IRS source"],
                     lambda y: cella(y, "simple") + cella(y, "simple_alto") + cella(y, "simple_catchup") + cella(y, "simple_catchup_alto")
                     + cella(y, "simple_catchup_6063") + f'<td class="src">{fonte_link(G, A[y]["simple"]["fonte"])}</td>')
    corpo += ('<p class="small">* SECURE 2.0 limits for SIMPLE retirement accounts maintained by certain eligible employers (section 408(p)(2)(E)(i)(I) or (II)); the '
              'IRS notices publish these amounts from 2025. The general limit and the catch-up amounts are also those of SIMPLE 401(k) plans, as the IRS sentences below say.</p>')
    corpo += citazioni(G, y1, ["simple", "simple_alto", "simple_catchup", "simple_catchup_alto", "simple_catchup_6063"])
    f, ld = faq(G, "simple", [
        ("What is the SIMPLE IRA max contribution?",
         f'Employee deferrals are limited to {usd(v(y0, "simple"))} in {y0} and {usd(v(y1, "simple"))} in {y1} in most plans, or {usd(v(y0, "simple_alto"))} and '
         f'{usd(v(y1, "simple_alto"))} in plans of certain eligible employers, plus the catch-up from age 50.', "simple ira max contribution"),
        ("What is the SIMPLE IRA catch-up contribution?",
         f'For employees aged 50 or over: {due_anni(v(y0, "simple_catchup"), v(y1, "simple_catchup"), y0, y1)} in most plans, '
         f'{usd(v(y1, "simple_catchup_alto"))} in the higher-limit plans, and {usd(v(y1, "simple_catchup_6063"))} for those who turn 60, 61, 62 or 63 during the year.',
         "simple ira catch up contribution"),
    ])
    corpo += f + altre_pagine(G, "simple") + G.fonti_box(fonti_anni(G, ["simple"]) + ["irs_cola_pagina"])
    pubblica(G, "simple", f"SIMPLE IRA Contribution Limits {y0} & {y1}, with Catch-Up",
             f"SIMPLE IRA limits from the IRS: {usd(v(y0, 'simple'))} for {y0}, {usd(v(y1, 'simple'))} for {y1}, the higher SECURE 2.0 limits and catch-up amounts since {PRIMO}.",
             "SIMPLE IRA", f"SIMPLE IRA contribution limits for {y0} and {y1}",
             f"Employee deferral limits, the higher limits for certain employers and the catch-up amounts, from the IRS notices for {PRIMO}–{ULTIMO}.",
             corpo, "SIMPLE IRA limits", jsonld=[ld] if ld else None)


def inflazione(G):
    """Limiti del primo anno ai prezzi dell'ultimo anno completo di CPI-U (medie annue BLS): solo fatti, nessun giudizio."""
    a0, a1 = PRIMO, G.ULTIMO_ANNO_US
    r = G.val("us", a1) / G.val("us", a0)
    righe = []
    for nome, k in (("401(k) employee limit", "k401"), ("IRA limit", "ira"), ("HSA, self-only", "hsa_self"), ("HSA, family", "hsa_family"), ("SIMPLE IRA limit", "simple")):
        x0, x1 = v(a0, k), v(a1, k)
        righe.append(f'<tr data-k="{k}"><td>{G.h(nome)}</td><td class="n">{usd(x0)}</td><td class="n" data-cpi>{G.soldi(x0 * r, "USD", 0)}</td>'
                     f'<td class="n">{usd(x1)}</td><td class="n">{G.pct(x1 / x0 - 1, 0)}</td><td class="n"><a href="/?a={x0}&amp;f={a0}&amp;t={a1}#calc">Calculate</a></td></tr>')
    return (f'<h2 id="inflation">Limits and inflation, {a0} to {a1}</h2><div class="testo"><p>The IRS adjusts most of these limits each year for the cost of '
            f'living and rounds them (the IRS notices speak of “the applicable rounding rules”), so they move in steps. Measured with the CPI-U annual averages, prices rose {G.pct(r - 1, 1, segno=False)} from {a0} '
            f'({G.idx(G.val("us", a0))}) to {a1} ({G.idx(G.val("us", a1))}). The table puts each {a0} limit in {a1} dollars next to the actual {a1} limit.</p></div>'
            f'<div class="tab"><table class="dati"><thead><tr><th scope="col">Limit</th><th scope="col" class="n">{a0}</th><th scope="col" class="n">In {a1} dollars</th>'
            f'<th scope="col" class="n">{a1} limit</th><th scope="col" class="n">Change</th><th scope="col" class="n">Calculator</th></tr></thead>'
            f'<tbody>{"".join(righe)}</tbody></table></div><p class="small">CPI-U annual averages from the U.S. Bureau of Labor Statistics, as used by the '
            '<a href="/">inflation calculator</a>. The IRS uses its own cost-of-living method and rounding rules, so the two do not move in step.</p>')


def storia_401k():
    """Frase sui periodi senza aumenti e sugli aumenti consecutivi, rifatta dai dati."""
    fermi = [y for y in ANNI[1:] if v(y, "k401") == v(y - 1, "k401")]
    sal = ULTIMO
    while sal - 1 > PRIMO and v(sal - 1, "k401") > v(sal - 2, "k401"):
        sal -= 1
    gruppi = []
    for y in fermi:
        if gruppi and gruppi[-1][1] == y - 1:
            gruppi[-1][1] = y
        else:
            gruppi.append([y - 1, y])
    parti = [f"{usd(v(a, 'k401'))} from {a} to {b}" if b - a > 1 else f"{usd(v(a, 'k401'))} in {a} and {b}" for a, b in gruppi]
    return f"It stayed at {' and at '.join(parti)}; it has risen every year since {sal}."


def pindice(G):
    y1, y0 = ULTIMO, CORRENTE
    righe = [("401(k), 403(b), TSP employee limit", "k401", None, "401k"), ("Catch-up 50+ (401(k), 403(b), 457(b), TSP)", "catchup", None, "401k"),
             ("Catch-up at ages 60–63", "catchup_6063", None, "401k"), ("All contributions, plans of one employer (415(c))", "dc415c", None, "401k"),
             ("IRA limit (traditional and Roth together)", "ira", None, "ira"), ("IRA catch-up 50+", "ira_catchup", None, "ira"),
             ("Roth IRA phase-out, single", "roth_single", None, "roth"), ("Roth IRA phase-out, married filing jointly", "roth_mfj", None, "roth"),
             ("SIMPLE IRA limit", "simple", None, "simple"), ("SIMPLE IRA catch-up 50+", "simple_catchup", None, "simple"),
             ("HSA, self-only coverage", "hsa_self", None, "hsa"), ("HSA, family coverage", "hsa_family", None, "hsa"), ("HSA, extra from age 55", "hsa_catchup", None, "hsa")]
    corpo_t = "".join(f'<tr data-riga="{k}"><td><a href="/{PAGINE[p]}">{G.h(n)}</a></td>{cella(y0, k)}{cella(y1, k)}</tr>' for n, k, _, p in righe)
    corpo = ('<div class="card risposta pull">'
             f'<p>For {y1} the IRS has raised the 401(k) limit to<span class="big">{usd(v(y1, "k401"))}</span>(from {usd(v(y0, "k401"))} in {y0}); the IRA limit '
             f'stays at {usd(v(y1, "ira"))} and the HSA limits rise to {usd(v(y1, "hsa_self"))} self-only and {usd(v(y1, "hsa_family"))} family.</p></div>')
    corpo += (f'<h2>{y0} and {y1} at a glance</h2><div class="tab"><table class="dati sintesi" data-sintesi><thead><tr><th scope="col">Limit</th><th scope="col" class="n">{y0}</th>'
              f'<th scope="col" class="n">{y1}</th></tr></thead><tbody>{corpo_t}</tbody></table></div>')
    corpo += G.AD
    corpo += (f'<h2>Contribution limits by year, {PRIMO}–{ULTIMO}</h2><p>The main limit of each account, every year. Each account page has the catch-up '
              'amounts, income ranges and the IRS document for every year.</p>')
    corpo += tabella(G, ["Year", "401(k)", "Catch-up 50+", "IRA", "Roth phase-out, single", "SIMPLE", "HSA self-only", "HSA family"],
                     lambda y: cella(y, "k401") + cella(y, "catchup") + cella(y, "ira") + cella(y, "roth_single") + cella(y, "simple")
                     + cella(y, "hsa_self") + cella(y, "hsa_family"), fonte=False)
    corpo += inflazione(G)
    corpo += ('<h2>Where the figures come from</h2><div class="testo"><p>Every amount is copied from the IRS document for that year: the annual notice on '
              'cost-of-living adjustments for retirement items (and the news release for 2015), the revenue procedure with the HSA amounts, and Publication 969 '
              f'for the age-55 HSA contribution (for {y0} and {y1}, the law that fixes it: section 223(b)(3) of the Internal Revenue Code). We keep the text of each document with its address, the date we read it and a SHA-256 fingerprint, and our checks '
              'confirm that every number on these pages appears in the quoted IRS sentence. See <a href="/how-we-check/">how we check</a>.</p></div>')
    f, ld = faq(G, "indice", [
        ("How have 401(k) contribution limits changed over time?",
         f'The employee limit was {usd(v(PRIMO, "k401"))} in {PRIMO}, {usd(v(2020, "k401"))} in 2020, {usd(v(y0, "k401"))} in {y0} and is '
         f'{usd(v(y1, "k401"))} for {y1}. ' + storia_401k(), "401k contribution limits history"),
    ])
    corpo += f + altre_pagine(G, "indice") + G.fonti_box(fonti_anni(G, ["k401", "hsa_self"]) + ["irs_cola_pagina", "irs_cola_tabella", "bls_cpiu"])
    pubblica(G, "indice", f"Retirement Contribution Limits {y0} & {y1}: 401(k), IRA, HSA",
             f"IRS contribution limits for 401(k), 403(b), 457(b), IRA, Roth IRA, SIMPLE IRA and HSA: {y0}, {y1} and every year since {PRIMO}, each with its IRS source.",
             "Retirement and HSA limits", f"Retirement contribution limits for {y0} and {y1}",
             f"401(k), IRA, Roth IRA, SIMPLE IRA and HSA limits in one place, from the IRS documents for {PRIMO}–{ULTIMO}, and how they compare with inflation.",
             corpo, "Retirement limits", jsonld=[ld] if ld else None)


def genera(G):
    pindice(G)
    p401k(G)
    pira(G)
    proth(G)
    phsa(G)
    psimple(G)
