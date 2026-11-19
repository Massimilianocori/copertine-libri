"""Controlli di US College Aid (collegeaid/sito/). Uso: python3 collegeaid/verifica.py [--browser]

Indipendenti dal costruttore: le cifre chiave sono TRASCRITTE A MANO qui sotto dai documenti ufficiali (tassi 2026-27 e storia dal 2013,
tetti, scaglioni del RAP, fasce del piano standard, date dei 10 Stati) e confrontate con dati/aiuti.json e con le pagine.
I calcolatori (app.js, eseguito con node) sono confrontati con un conto scritto a parte in questo file (Decimal, niente codice in comune).
Poi: impronte dei file grezzi e frasi alla lettera, ogni citazione in pagina = frase della fonte, voci FAFSA = testo del PDF riletto,
ogni importo in dollari e ogni percentuale delle pagine dentro l'insieme delle cifre trascritte o ricalcolate, titoli e descrizioni,
FAQ visibili = JSON-LD e solo da ricerche misurate, link, modulo senza dati personali, riquadro dei partner assente se spenti, nessuna chiave.
--browser: Playwright, tutte le pagine a 375 e 1280 px chiaro e scuro, calcolatori digitati con i casi attesi calcolati qui.
"""
import hashlib
import json
import os
import random
import re
import subprocess
import sys
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, getcontext
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
SITO = RADICE / "sito"
DATI = RADICE / "dati"
sys.path.insert(0, str(RADICE / "raccolta"))
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402
import testo as T  # noqa: E402

URL_SITO = "https://us-college-aid.netlify.app"
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"
DOMINI_UFFICIALI = {"studentaid.gov", "www.govinfo.gov", "fsapartners.ed.gov"}
getcontext().prec = 60
ERR = []


def err(m):
    ERR.append(m)


# ---------------------------------------------------------------- trascrizioni a mano dai documenti ufficiali
# Federal Register 2026-18493, Chart 1 (asta del 12/5/2026: 4,468 % arrotondato a 4,47 %): maggiorazione, massimo, tasso
M_TASSI = {"ug": ("2.05", "8.25", "6.52"), "grad": ("3.60", "9.50", "8.07"), "plus": ("4.60", "10.50", "9.07")}
# Chart 2: anno d'inizio -> (studenti dei corsi di laurea, laureati, PLUS)
M_STORIA = {2026: ("6.52", "8.07", "9.07"), 2025: ("6.39", "7.94", "8.94"), 2024: ("6.53", "8.08", "9.08"), 2023: ("5.50", "7.05", "8.05"), 2022: ("4.99", "6.54", "7.54"),
            2021: ("3.73", "5.28", "6.28"), 2020: ("2.75", "4.30", "5.30"), 2019: ("4.53", "6.08", "7.08"), 2018: ("5.05", "6.60", "7.60"), 2017: ("4.45", "6.00", "7.00"),
            2016: ("3.76", "5.31", "6.31"), 2015: ("4.29", "5.84", "6.84"), 2014: ("4.66", "6.21", "7.21"), 2013: ("3.86", "5.41", "6.41")}
# Chart 3: tassi dei prestiti dal 1/7/2006 al 30/6/2013
M_VECCHI = ["3.40", "4.50", "5.60", "6.00", "6.80", "6.80", "6.80", "7.90"]
# Manuale FSA 2025-26, vol. 8 cap. 4, tabelle 1A, 1B e 4; regola finale 2026-08556 (34 CFR 685.203); Public Law 119-21, sez. 81001
M_LIM = {"dip": [(5500, 3500), (6500, 4500), (7500, 5500)], "dip_tot": (31000, 23000), "ind": [(9500, 3500), (10500, 4500), (12500, 5500)], "ind_tot": (57500, 23000),
         "grad": (20500, 100000), "prof": (50000, 200000), "genitori": (20000, 65000), "vita": 257500, "prima": 138500}
# Public Law 119-21, sez. 82001: RAP (soglia superiore dello scaglione, percentuale; primo scaglione 120 $ l'anno) e piano standard
M_RAP = [(10000, None), (20000, 1), (30000, 2), (40000, 3), (50000, 4), (60000, 5), (70000, 6), (80000, 7), (90000, 8), (100000, 9), (None, 10)]
M_RAP_FISSO, M_RAP_DIP, M_RAP_MIN, M_RAP_RATE, M_RAP_QUOTA = 120, 50, 10, 360, 50
M_STD = [(25000, 10), (50000, 15), (100000, 20), (None, 25)]
# Modulo FAFSA 2027-28, pagine 1 e 2: date federali e date dei 10 Stati con una pagina
M_FAFSA = {"apertura": "2026-10-01", "federale": "2028-06-30"}
M_STATI = {"CA": ("california", ["2027-03-02", "2027-09-02"]), "TX": ("texas", ["2027-01-15"]), "FL": ("florida", ["2027-05-15"]), "MI": ("michigan", ["2027-07-01"]),
           "OH": ("ohio", ["2027-10-01"]), "NJ": ("new-jersey", ["2027-04-15", "2027-09-15", "2028-02-15"]), "IL": ("illinois", ["2026-10-01"]),
           "MA": ("massachusetts", ["2027-05-01"]), "IN": ("indiana", ["2027-04-15"]), "PA": ("pennsylvania", ["2027-05-01", "2027-08-01"])}
N_VOCI = 59   # 50 Stati, District of Columbia, 8 territori e Stati associati

MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
MESI_MODULO = {"Jan.": 1, "Feb.": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "Aug.": 8, "Sept.": 9, "Oct.": 10, "Nov.": 11, "Dec.": 12}


def lunga(iso):
    d = date.fromisoformat(iso)
    return f"{MESI[d.month - 1]} {d.day}, {d.year}"


def usd(n):
    return f"${n:,}"


def usdc(c):
    return f"${c // 100:,}.{c % 100:02d}"


# ---------------------------------------------------------------- conto di riferimento (Decimal, scritto a parte)
def cent(x):
    return int(Decimal(x).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def rif_anni(saldo_cent):
    dollari = Decimal(saldo_cent) / 100
    for sotto, anni in M_STD:
        if sotto is None or dollari < sotto:
            return anni


def rif_piano(saldo_cent, tasso_pc, mesi):
    """tasso_pc: stringa «6.52». Rata fissa arrotondata al centesimo; interesse mensile arrotondato al centesimo; l'ultima rata chiude."""
    r = Decimal(tasso_pc) / 1200
    rata = cent(Decimal(saldo_cent) / mesi) if r == 0 else cent(Decimal(saldo_cent) * r / (1 - (1 + r) ** (-mesi)))
    resto, pagato, interessi, n = saldo_cent, 0, 0, 0
    while resto > 0:
        i = cent(Decimal(resto) * Decimal(tasso_pc) / 1200)   # prima il prodotto, poi la divisione: i casi a metà centesimo restano esatti
        dovuto = resto + i
        paga = dovuto if (n == mesi - 1 or dovuto < rata) else rata
        resto, pagato, interessi, n = dovuto - paga, pagato + paga, interessi + i, n + 1
    return {"rata": rata, "mesi": n, "pagato": pagato, "interessi": interessi}


def rif_rap(reddito, carico):
    for su, pc in M_RAP:
        if su is None or reddito <= su:
            base = Decimal(M_RAP_FISSO) if pc is None else Decimal(reddito) * pc / 100
            break
    return max(cent(base * 100 / 12) - carico * M_RAP_DIP * 100, M_RAP_MIN * 100)


def rif_rap_mese(pagamento, saldo, tasso_pc):
    i = cent(Decimal(saldo) * Decimal(tasso_pc) / 1200)
    paga = min(pagamento, saldo + i)
    a_int = min(paga, i)
    a_cap = paga - a_int
    agg = 0
    if a_cap < M_RAP_QUOTA * 100:
        agg = max(0, min(min(M_RAP_QUOTA * 100, paga) - a_cap, saldo - a_cap))
    return {"interessi": i, "aInteressi": a_int, "aCapitale": a_cap, "nonAddebitati": i - a_int, "aggiunta": agg, "nuovoSaldo": saldo - a_cap - agg}


def rif_buco(costo, anni):
    righe, ts, tg = [], 0, 0
    for a in range(anni):
        tetto = M_LIM["dip"][min(a, 2)][0] * 100
        s = max(0, min(tetto, M_LIM["dip_tot"][0] * 100 - ts, costo))
        g = max(0, min(M_LIM["genitori"][0] * 100, M_LIM["genitori"][1] * 100 - tg, costo - s))
        ts, tg = ts + s, tg + g
        righe.append({"anno": a + 1, "costo": costo, "studente": s, "genitori": g, "resto": costo - s - g})
    return righe


# ---------------------------------------------------------------- lettura delle pagine
def leggi(p):
    return (SITO / p).read_text(encoding="utf-8")


def visibile(html_):
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", html_)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", unescape(s)).strip()


def principale(html_):
    return html_[html_.index('<main id="main">'):html_.index("</main>")]


def pagine_html():
    return sorted(p.relative_to(SITO).as_posix() for p in SITO.rglob("*.html") if not p.name.startswith("google"))


def controlla_dati():
    A = json.loads((DATI / "aiuti.json").read_text(encoding="utf-8"))
    F = json.loads((DATI / "fonti.json").read_text(encoding="utf-8"))["fonti"]
    # fonti: impronte e frasi alla lettera, rilette qui dai file grezzi
    n_frasi = 0
    for fid, f in F.items():
        grezzo = RADICE / f["file"]
        if not grezzo.exists():
            err(f"fonte {fid}: manca {f['file']}")
            continue
        t = T.testo_norm(grezzo)
        if f["impronta"] == "file" and hashlib.sha256(grezzo.read_bytes()).hexdigest() != f["sha256"]:
            err(f"fonte {fid}: sha256 del file diverso da quello registrato")
        if f["impronta"] == "frasi" and T.impronta_frasi(t, f["frasi"]) != f["sha256_frasi"]:
            err(f"fonte {fid}: impronta delle frasi diversa")
        if f["http"] != 200:
            err(f"fonte {fid}: HTTP {f['http']}")
        if not any(f["url"].startswith(f"https://{d}/") for d in DOMINI_UFFICIALI):
            err(f"fonte {fid}: {f['url']} non è su un dominio ufficiale")
        for k, frase in f["frasi"].items():
            n_frasi += 1
            if T.norm(frase) not in t:
                err(f"fonte {fid}: frase «{k}» non trovata nel file grezzo")
    # tassi
    ta = A["tassi"]
    if (ta["asta"], ta["asta_arrotondata"], ta["asta_data"], ta["dal"], ta["al"]) != ("4.468", "4.47", "2026-05-12", "2026-07-01", "2027-07-01"):
        err("aiuti.json: asta o periodo dei tassi diversi dalla trascrizione")
    for r in ta["righe"]:
        if (r["maggiorazione"], r["massimo"], r["tasso"]) != M_TASSI[r["chiave"]]:
            err(f"aiuti.json: tasso {r['chiave']} diverso dalla trascrizione")
    storia = {int(r["dal"][:4]): (r["ug"], r["grad"], r["plus"]) for r in ta["storia"]}
    if storia != M_STORIA:
        err(f"aiuti.json: storia dei tassi diversa dalla trascrizione: {set(storia.items()) ^ set(M_STORIA.items())}")
    if [r["tasso"] for r in ta["prima_del_2013"]] != M_VECCHI:
        err("aiuti.json: tassi 2006-2013 diversi dalla trascrizione")
    # tetti
    L = A["limiti"]
    letti = {"dip": [(x["totale"], x["sussidiato"]) for x in L["dipendente"]["anni"]], "dip_tot": (L["dipendente"]["totale"], L["dipendente"]["totale_sussidiato"]),
             "ind": [(x["totale"], x["sussidiato"]) for x in L["indipendente"]["anni"]], "ind_tot": (L["indipendente"]["totale"], L["indipendente"]["totale_sussidiato"]),
             "grad": (L["laureato"]["anno"], L["laureato"]["totale"]), "prof": (L["professionale"]["anno"], L["professionale"]["totale"]),
             "genitori": (L["genitori"]["anno"], L["genitori"]["totale"]), "vita": L["vita"], "prima": L["laureati_prima"]["totale"]}
    if letti != M_LIM:
        err(f"aiuti.json: tetti diversi dalla trascrizione: {letti}")
    # rimborso
    R = A["rimborso"]
    if [(s["fino_a"], s["pc"]) for s in R["rap"]["scaglioni"]] != M_RAP or R["rap"]["scaglioni"][0]["fisso_anno"] != M_RAP_FISSO:
        err("aiuti.json: scaglioni del RAP diversi dalla trascrizione")
    if (R["rap"]["per_dipendente_mese"], R["rap"]["minimo_mese"], R["rap"]["rate_cancellazione"], R["rap"]["quota_capitale_mese"]) != (M_RAP_DIP, M_RAP_MIN, M_RAP_RATE, M_RAP_QUOTA):
        err("aiuti.json: parametri del RAP diversi dalla trascrizione")
    if [(f["sotto"], f["anni"]) for f in R["standard"]["fasce"]] != M_STD:
        err("aiuti.json: fasce del piano standard diverse dalla trascrizione")
    # FAFSA: voci rilette dal PDF in un altro modo (tutta la pagina 2 in -raw, senza spazi e trattini: ogni voce deve esserci, e insieme devono coprirla)
    fa = A["fafsa"]
    if (fa["apertura"], fa["chiusura_federale"], fa["anno"]) != (M_FAFSA["apertura"], M_FAFSA["federale"], "2027–28"):
        err("aiuti.json: date federali FAFSA diverse dalla trascrizione")
    if len(fa["voci"]) != N_VOCI:
        err(f"aiuti.json: {len(fa['voci'])} voci FAFSA invece di {N_VOCI}")
    pdf = RADICE / F["fafsa_2728"]["file"]
    stretto = lambda s: re.sub(r"[\s-]+", "", s)  # noqa: E731
    pagina2 = stretto(T.pdf(pdf, prima=2, ultima=2, raw=True))
    layout = stretto(T.pdf(pdf, prima=2, ultima=2, layout=True))
    coperti = 0
    for v in fa["voci"]:
        intera = stretto(f"{v['nome']} ({v['sigla']}) {v['testo']}")
        if intera not in pagina2:
            err(f"FAFSA {v['sigla']}: la voce non si ritrova nella pagina 2 del PDF")
        coperti += len(intera)
        # le date: rilette qui dal testo e ritrovate anche nella lettura a colonne (-layout)
        mie = sorted({date(int(a), MESI_MODULO[m], int(g)).isoformat() for m, g, a in re.findall(r"(Jan\.|Feb\.|March|April|May|June|July|Aug\.|Sept\.|Oct\.|Nov\.|Dec\.) (\d{1,2}), (\d{4})", v["testo"])})
        if mie != v["date"]:
            err(f"FAFSA {v['sigla']}: date {v['date']} diverse da quelle rilette {mie}")
        for m, g, a in re.findall(r"(Jan\.|Feb\.|March|April|May|June|July|Aug\.|Sept\.|Oct\.|Nov\.|Dec\.) (\d{1,2}), (\d{4})", v["testo"]):
            if stretto(f"{m} {g}, {a}") not in layout:
                err(f"FAFSA {v['sigla']}: «{m} {g}, {a}» non è nella lettura a colonne della pagina")
    inizio = pagina2.index(stretto("the dates below refer to when the form must be received.")) + len(stretto("the dates below refer to when the form must be received."))
    resto = len(pagina2) - inizio
    if not (0 <= resto - coperti <= 40):   # avanzano solo il titolo laterale e il numero di pagina
        err(f"FAFSA: le voci coprono {coperti} caratteri su {resto} della pagina 2: qualcosa è rimasto fuori")
    voci = {v["sigla"]: v for v in fa["voci"]}
    for s, (_, date_) in M_STATI.items():
        if voci[s]["date"] != date_:
            err(f"FAFSA {s}: date {voci[s]['date']} diverse dalla trascrizione {date_}")
    return A, F, n_frasi


def controlla_pagine(A, F):
    dom = {r["frase"]: r["volume_mese"] for r in json.loads((DATI / "domanda.json").read_text(encoding="utf-8"))["ricerche"]}
    aff = json.loads((DATI / "affiliati.json").read_text(encoding="utf-8"))
    voci = {v["sigla"]: v for v in A["fafsa"]["voci"]}
    pagine = pagine_html()
    attese = (["index.html", "404.html", "fafsa-deadlines/index.html"] + [f"fafsa-deadlines/{sl}/index.html" for sl, _ in M_STATI.values()]
              + [f"{p}/index.html" for p in ("student-loan-interest-rates", "federal-student-loan-limits", "student-loan-payment-calculator", "repayment-assistance-plan", "parent-plus-loans", "how-we-check", "about", "privacy")])
    if sorted(attese) != pagine:
        err(f"pagine diverse da quelle attese: {set(attese) ^ set(pagine)}")
    titoli, descr, n_faq, n_cit, n_link = {}, {}, 0, 0, 0
    sitemap = re.findall(r"<loc>([^<]+)</loc>", leggi("sitemap.xml"))
    for p in pagine:
        html_ = leggi(p)
        url = f"{URL_SITO}/" + p.replace("index.html", "")
        t = re.search(r"<title>(.*?)</title>", html_)
        d = re.search(r'<meta name="description" content="(.*?)">', html_)
        if not t or not d:
            err(f"{p}: manca titolo o descrizione")
            continue
        tit, des = unescape(t[1]), unescape(d[1])
        indicizzata = p != "404.html"
        if indicizzata:
            if len(tit) > 65 or tit in titoli.values():
                err(f"{p}: titolo lungo {len(tit)} o doppio")
            if len(des) > 160 or len(des) < 70 or des in descr.values():
                err(f"{p}: descrizione lunga {len(des)} o doppia")
            titoli[p], descr[p] = tit, des
            if f'<link rel="canonical" href="{url}">' not in html_:
                err(f"{p}: canonical sbagliato")
            if url not in sitemap:
                err(f"{p}: non è nella sitemap")
        elif "noindex" not in html_:
            err(f"{p}: la 404 deve essere noindex")
        if len(re.findall(r"<h1[ >]", html_)) != 1:
            err(f"{p}: non ha un solo h1")
        if f'<meta name="google-site-verification" content="{GOOGLE_VERIFICA}">' not in html_:
            err(f"{p}: manca la verifica di Google")
        if "rete-siti.goatcounter.com/count" not in html_:
            err(f"{p}: manca il contatore")
        if '<html lang="en-US">' not in html_:
            err(f"{p}: lingua della pagina")
        if "Information, not financial advice." not in visibile(html_):
            err(f"{p}: manca la frase «Information, not financial advice»")
        if "data-partner" in html_ or 'rel="sponsored' in html_:
            err(f"{p}: riquadro dei partner o link sponsorizzato presente con i partner spenti")
        # citazioni alla lettera
        for fid, k, testo_ in re.findall(r'<blockquote class="cit" data-fonte="([^"]+)" data-frase="([^"]+)"><p>“<span data-cit>(.*?)</span>”', html_):
            n_cit += 1
            if fid not in F or k not in F[fid]["frasi"] or unescape(testo_) != F[fid]["frasi"][k]:
                err(f"{p}: citazione {fid}/{k} diversa dalla frase della fonte")
        for sig, testo_ in re.findall(r'<blockquote class="cit" data-voce="([A-Z]{2})"><p>“<span data-voce-testo>(.*?)</span>”', html_):
            n_cit += 1
            if unescape(testo_) != voci[sig]["testo"]:
                err(f"{p}: voce FAFSA {sig} diversa dal testo del modulo")
        if "<blockquote" in html_ and len(re.findall(r"<blockquote", html_)) != len(re.findall(r'<blockquote class="cit" data-(?:fonte|voce)=', html_)):
            err(f"{p}: citazione senza fonte")
        # FAQ: visibili = JSON-LD, ogni domanda da una ricerca misurata
        faq = re.findall(r'<div class="faq" data-ricerca="([^"]+)"><h3>(.*?)</h3><p>(.*?)(?:<sup class="ref">.*?</sup>)?</p></div>', html_)
        ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html_)]
        ld_faq = [x for x in ld if x.get("@type") == "FAQPage"]
        if faq:
            n_faq += len(faq)
            if len(ld_faq) != 1 or [(unescape(q), unescape(a)) for _, q, a in faq] != [(x["name"], x["acceptedAnswer"]["text"]) for x in ld_faq[0]["mainEntity"]]:
                err(f"{p}: FAQ visibili diverse dal JSON-LD")
            for ric, q, _ in faq:
                if dom.get(unescape(ric), 0) <= 0:
                    err(f"{p}: FAQ «{q}» senza ricerca misurata ({ric})")
        elif ld_faq:
            err(f"{p}: JSON-LD FAQ senza FAQ visibili")
        # rimandi alle fonti: ogni [n] ha la sua voce
        for n in set(re.findall(r'href="#f(\d+)"', html_)):
            if f'<li id="f{n}">' not in html_:
                err(f"{p}: rimando [{n}] senza voce nelle fonti")
        # link
        for href in re.findall(r'<a [^>]*href="([^"]+)"', html_):
            n_link += 1
            if href.startswith("/"):
                dest = href.split("#")[0]
                f = SITO / (dest.lstrip("/") + "index.html" if dest.endswith("/") else dest.lstrip("/"))
                if not f.exists():
                    err(f"{p}: link interno rotto {href}")
                anc = href.split("#")[1] if "#" in href else None
                if anc and f.exists() and f'id="{anc}"' not in f.read_text(encoding="utf-8"):
                    err(f"{p}: ancora inesistente {href}")
            elif href.startswith("#"):
                if f'id="{href[1:]}"' not in html_:
                    err(f"{p}: ancora inesistente {href}")
            elif not any(href.startswith(f"https://{d}/") for d in DOMINI_UFFICIALI | {"policies.google.com", "adssettings.google.com", "www.goatcounter.com", "www.netlify.com", "optout.aboutads.info", "www.aboutads.info", "www.youronlinechoices.com", "youronlinechoices.eu"}) and href not in ("https://adssettings.google.com", "https://policies.google.com/technologies/partner-sites"):
                err(f"{p}: link esterno non previsto {href}")
        if re.search(r"\{[a-z_]+\}|\[\[|None|nan\b", visibile(principale(html_))):
            err(f"{p}: segnaposto o «None» nel testo: {re.search(r'.{30}(?:\{[a-z_]+\}|\[\[|None|nan\b).{30}', visibile(principale(html_)))}")
    if sorted(sitemap) != sorted(f"{URL_SITO}/" + p.replace("index.html", "") for p in pagine if p != "404.html"):
        err("sitemap diversa dalle pagine indicizzabili")
    if f"Sitemap: {URL_SITO}/sitemap.xml" not in leggi("robots.txt"):
        err("robots.txt senza sitemap")
    if not (SITO / "b5a26a844a465f58552debee2c8a0114.txt").exists() or not (SITO / "assets" / "og.png").exists() or not (SITO / "netlify.toml").exists():
        err("manca la chiave IndexNow, og.png o netlify.toml")
    # partner: spenti e senza link
    for x in aff["partner"]:
        if x["attivo"] or x["link"]:
            err(f"affiliati.json: {x['id']} deve restare spento e senza link fino alla decisione di Massimiliano")
    # modulo delle correzioni
    hc = leggi("how-we-check/index.html")
    campi = re.findall(r'<(?:input|textarea)[^>]* name="([^"]+)"', hc[hc.index("<form"):hc.index("</form>")])
    if sorted(campi) != ["bot-field", "form-name", "message", "page", "source"] or 'netlify-honeypot="bot-field"' not in hc or 'data-netlify="true"' not in hc:
        err(f"modulo delle correzioni: campi {campi}")
    return n_faq, n_cit, n_link, len(pagine)


def importi(testo_):
    return {int(x.replace(",", "")) for x in re.findall(r"\$(\d[\d,]*)(?![\d,]*\.\d)", testo_)}


def controlla_cifre(A):
    """Le cifre delle pagine contro le trascrizioni a mano e il conto di riferimento."""
    n = 0
    voci = {v["sigla"]: v for v in A["fafsa"]["voci"]}
    # ---- indice delle scadenze: 59 righe, testo = modulo, date = quelle del testo
    ind = leggi("fafsa-deadlines/index.html")
    righe = re.findall(r'<tr data-nome="[^"]*" data-tipo="(\w+)" data-sigla="([A-Z]{2})">.*?<td class="uff" data-voce-testo>(.*?)</td><td class="d">(.*?)</td></tr>', ind)
    if len(righe) != N_VOCI or len({r[1] for r in righe}) != N_VOCI:
        err(f"indice delle scadenze: {len(righe)} righe invece di {N_VOCI}")
    for tipo, sig, testo_, celle in righe:
        v = voci[sig]
        if unescape(testo_) != v["testo"]:
            err(f"indice: testo di {sig} diverso dal modulo")
        attese = [d for d in v["date"] if d != M_FAFSA["apertura"]]
        if re.findall(r'data-giorni="([\d-]+)"', celle) != attese:
            err(f"indice: date di {sig} diverse da quelle del testo")
        for d in attese:
            g = date.fromisoformat(d)
            mod = next(k for k, m in MESI_MODULO.items() if m == g.month) + f" {g.day}, {g.year}"
            if f'<span class="chip">{mod}</span>' not in celle:
                err(f"indice: {sig} senza l'etichetta {mod}")
        t_atteso = "date" if attese else ("asap" if "soon as possible" in v["testo"] else "check")
        if tipo != t_atteso:
            err(f"indice: tipo di {sig} = {tipo}, atteso {t_atteso}")
        n += 1
    for pezzo in (lunga(M_FAFSA["federale"]), lunga(M_FAFSA["apertura"])):
        if pezzo not in visibile(ind):
            err(f"indice: manca {pezzo}")
    # ---- pagine degli Stati: le date mostrate sono quelle trascritte, più le due federali
    for s, (slug, date_) in M_STATI.items():
        h_ = leggi(f"fafsa-deadlines/{slug}/index.html")
        lista = h_[h_.index('<ul class="date-l">'):h_.index("</ul>", h_.index('<ul class="date-l">'))]
        mostrate = re.findall(r'data-giorni="([\d-]+)"', lista)
        attese = [d for d in date_ if d != M_FAFSA["apertura"]] + [M_FAFSA["apertura"], M_FAFSA["federale"]]
        if sorted(mostrate) != sorted(attese):
            err(f"{slug}: date mostrate {mostrate}, attese {attese}")
        vis = visibile(lista)
        for d in date_ + [M_FAFSA["federale"]]:
            if lunga(d) not in vis:
                err(f"{slug}: manca {lunga(d)} nell'elenco delle date")
        primo = [d for d in date_ if d != M_FAFSA["apertura"]]
        tit = unescape(re.search(r"<title>(.*?)</title>", h_)[1])
        if (lunga(primo[0]) if primo else "As Soon As Possible") not in tit or voci[s]["nome"] not in tit:
            err(f"{slug}: titolo senza la prima data: {tit}")
        # ogni data scritta per esteso nella pagina è una data del modulo per quello Stato, una federale, o la prima data di un altro dei 10 Stati
        ammesse = {lunga(d) for d in date_} | {lunga(M_FAFSA["apertura"]), lunga(M_FAFSA["federale"]), "July 1, 2026", "June 30, 2027"} | {lunga(d) for f in json.loads((DATI / "fonti.json").read_text(encoding="utf-8"))["fonti"].values() for d in [f["letto_il"]]}
        corpo = re.sub(r"(?s)<cite>.*?</cite>|<section class=\"fonti-box\".*?</section>|<h2 id=\"others\">.*?<h2 id=\"loans\">", " ", principale(h_))   # i titoli dei documenti hanno le loro date
        corpo = visibile(corpo).replace(voci[s]["testo"], " ")
        for m in re.findall(r"(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}", corpo):
            if m not in ammesse:
                err(f"{slug}: data non prevista nel testo: {m}")
        n += 1
    # ---- tassi: ogni percentuale della pagina è nella trascrizione
    ta = leggi("student-loan-interest-rates/index.html")
    vis = visibile(principale(ta))
    ammesse = {x for v in M_TASSI.values() for x in v} | {x for v in M_STORIA.values() for x in v} | set(M_VECCHI) | {"4.468", "4.47", "1.55", "1.00"}
    for pc in re.findall(r"(\d+\.\d+)(?:%| point)", vis):
        if pc not in ammesse:
            err(f"tassi: percentuale non prevista {pc}%")
        n += 1
    for anno, (ug, gr, pl) in M_STORIA.items():
        m = re.search(rf'<th scope="row">{anno}–{str(anno + 1)[2:]}<span class="conto">July 1, {anno} – June 30, {anno + 1}</span></th><td class="n forte">([\d.]+)%</td><td class="n">([\d.]+)%</td><td class="n">([\d.]+)%</td>', ta)
        if not m or m.groups() != (ug, gr, pl):
            err(f"tassi: riga {anno} della tabella storica diversa dalla trascrizione")
        n += 1
    for k, (add, mass, tasso) in M_TASSI.items():
        if f'<td class="n">4.47%</td><td class="n">+ {add}</td><td class="n">{mass}%</td><td class="n forte">{tasso}%</td>' not in ta:
            err(f"tassi: riga {k} della tabella 1 diversa dalla trascrizione")
    if [x for x in re.findall(r'<td class="n forte">([\d.]+)%</td></tr>', ta[ta.index('id="before-2013"'):ta.index('id="next"')])] != M_VECCHI:
        err("tassi: tabella 2006-2013 diversa dalla trascrizione")
    es = rif_piano(1000000, "6.52", 120)
    if usdc(es["rata"]) not in vis:
        err("tassi: esempio della rata diverso dal conto di riferimento")
    # ---- importi in dollari: ogni importo intero delle pagine è una cifra trascritta, una loro somma, o un esempio dichiarato
    base = {x for coppia in M_LIM["dip"] + M_LIM["ind"] for x in coppia} | set(M_LIM["dip_tot"]) | set(M_LIM["ind_tot"]) | set(M_LIM["grad"]) | set(M_LIM["prof"]) | set(M_LIM["genitori"]) | {M_LIM["vita"], M_LIM["prima"]}
    quattro = sum(M_LIM["dip"][min(i, 2)][0] for i in range(4))
    base |= {quattro, quattro + M_LIM["genitori"][1], 2 * M_LIM["genitori"][0]}
    rap = {su for su, _ in M_RAP if su} | {su + 1 for su, _ in M_RAP if su} | {M_RAP_FISSO, M_RAP_DIP, M_RAP_MIN}
    std = {su for su, _ in M_STD if su}
    esempi_rata, esempi_rap = {10000, 20000, 40000, 100000}, {20000, 35000, 50000, 65000, 80000, 100000, 150000, 30000, 30001}
    es_buco = rif_buco(3200000, 4)
    amm = {"federal-student-loan-limits": base, "parent-plus-loans": base | std | {32000, sum(r["resto"] for r in es_buco) // 100},
           "student-loan-payment-calculator": base | std | esempi_rata, "repayment-assistance-plan": rap | esempi_rap | {50}, "student-loan-interest-rates": {10000},
           "": base | std, "how-we-check": {50, 10}}
    for slug, date_ in list(M_STATI.values()):
        amm[f"fafsa-deadlines/{slug}"] = {M_LIM["dip"][0][0]}
    for cartella, ammessi in amm.items():
        h_ = leggi(f"{cartella}/index.html" if cartella else "index.html")
        corpo = principale(h_)
        corpo = re.sub(r'(?s)<div class="card calc.*?</form>', " ", corpo)   # i valori iniziali dei calcolatori sono esempi
        for x in importi(visibile(corpo)):
            n += 1
            if x not in ammessi:
                err(f"/{cartella}: importo non previsto ${x:,}")
    # ---- tetti: celle delle tabelle
    li = leggi("federal-student-loan-limits/index.html")
    for chi, k in (("Dependent", "dip"), ("Independent", "ind")):
        for (tot, sus), anno in zip(M_LIM[k], ("first year", "second year", "third year and beyond")):
            if f'<th scope="row">{chi}, {anno}</th><td class="n forte">{usd(tot)}</td><td class="n">{usd(sus)}</td>' not in li:
                err(f"tetti: riga {chi} {anno} diversa dalla trascrizione")
        if f'<th scope="row">{chi}, total debt allowed</th><td class="n forte">{usd(M_LIM[k + "_tot"][0])}</td><td class="n">{usd(M_LIM[k + "_tot"][1])}</td>' not in li:
            err(f"tetti: riga dei totali {chi} diversa dalla trascrizione")
    for nome, k in (("Graduate student (not professional)", "grad"), ("Professional student", "prof"), ("Parents, for each dependent student", "genitori")):
        if not re.search(rf'<th scope="row">{re.escape(nome)}</th><td>[^<]+</td><td class="n forte">{re.escape(usd(M_LIM[k][0]))}</td><td class="n forte">{re.escape(usd(M_LIM[k][1]))}</td>', li):
            err(f"tetti: riga {nome} diversa dalla trascrizione")
    if f'<td class="n">–</td><td class="n forte">{usd(M_LIM["vita"])}</td>' not in li:
        err("tetti: tetto a vita diverso dalla trascrizione")
    # ---- esempi della rata e del RAP contro il conto di riferimento
    ra = leggi("student-loan-payment-calculator/index.html")
    es = re.findall(r'<tr data-esempio="(\d+)"><th scope="row">([^<]+)</th><td class="n">(\d+) years</td><td class="n forte">([^<]+)</td><td class="n">([^<]+)</td><td class="n forte">([^<]+)</td><td class="n">([^<]+)</td></tr>', ra)
    if len(es) != 6:
        err(f"rata: {len(es)} esempi invece di 6")
    for c, saldo, anni, r1, i1, r2, i2 in es:
        c = int(c)
        nuovo, vecchio = rif_piano(c, "6.52", rif_anni(c) * 12), rif_piano(c, "6.52", 120)
        if (saldo, int(anni), r1, i1, r2, i2) != (usd(c // 100), rif_anni(c), usdc(nuovo["rata"]), usdc(nuovo["interessi"]), usdc(vecchio["rata"]), usdc(vecchio["interessi"])):
            err(f"rata: esempio {saldo} diverso dal conto di riferimento")
        n += 1
    for i, (su, anni) in enumerate(M_STD):
        if f'<td class="n forte">{anni} years</td><td class="n">{anni * 12}</td>' not in ra:
            err(f"rata: fascia {anni} anni mancante")
    rp = leggi("repayment-assistance-plan/index.html")
    celle = re.findall(r'data-rap="(\d+)-(\d+)">([^<]+)</td>', rp)
    if len(celle) != 28:
        err(f"RAP: {len(celle)} esempi invece di 28")
    for red, car, v in celle:
        if v != usdc(rif_rap(int(red), int(car))):
            err(f"RAP: esempio {red}/{car} = {v}, riferimento {usdc(rif_rap(int(red), int(car)))}")
        n += 1
    for i, (su, pc) in enumerate(M_RAP):
        base_ = "$120 a year" if pc is None else f"{pc}% of AGI"
        mese = usdc(rif_rap(su, 0)) if su else usdc(rif_rap(M_RAP[i - 1][0] + 1, 0)) + " and up"
        if f'<td class="forte">{base_}</td><td class="n">{mese}</td>' not in rp:
            err(f"RAP: riga dello scaglione {su} diversa dal riferimento")
    for testo_ in (usdc(rif_rap(30000, 0)), usdc(rif_rap(30001, 0)), usdc(rif_rap(50000, 0)), usdc(rif_rap(50000, 2))):
        if testo_ not in visibile(rp):
            err(f"RAP: manca {testo_}")
    pl = leggi("parent-plus-loans/index.html")
    es = re.findall(r'<tr data-esempio-plus="(\d+)"><th scope="row">([^<]+)</th><td class="n">(\d+) years</td><td class="n forte">([^<]+)</td><td class="n">([^<]+)</td></tr>', pl)
    if len(es) != 3:
        err(f"PLUS: {len(es)} esempi invece di 3")
    for c, saldo, anni, r1, i1 in es:
        c = int(c)
        x = rif_piano(c, "9.07", rif_anni(c) * 12)
        if (saldo, int(anni), r1, i1) != (usd(c // 100), rif_anni(c), usdc(x["rata"]), usdc(x["interessi"])):
            err(f"PLUS: esempio {saldo} diverso dal conto di riferimento")
        n += 1
    # regole passate ai calcolatori = trascrizioni
    reg = json.loads(unescape(re.search(r'data-calc="rata" data-regole="([^"]+)"', ra)[1]))
    if [(f["sotto"], f["anni"]) for f in reg["fasce"]] != M_STD:
        err("rata: regole del calcolatore diverse dalla trascrizione")
    reg = json.loads(unescape(re.search(r'data-calc="rap" data-regole="([^"]+)"', rp)[1]))["rap"]
    if [(s["fino_a"], s["pc"]) for s in reg["scaglioni"]] != M_RAP or (reg["per_dipendente_mese"], reg["minimo_mese"], reg["quota_capitale_mese"]) != (M_RAP_DIP, M_RAP_MIN, M_RAP_QUOTA):
        err("RAP: regole del calcolatore diverse dalla trascrizione")
    reg = json.loads(unescape(re.search(r'data-calc="buco" data-regole="([^"]+)"', pl)[1]))["limiti"]
    if [x["totale"] for x in reg["dipendente"]["anni"]] != [x[0] for x in M_LIM["dip"]] or reg["dipendente"]["totale"] != M_LIM["dip_tot"][0] or (reg["genitori"]["anno"], reg["genitori"]["totale"]) != M_LIM["genitori"]:
        err("buco: regole del calcolatore diverse dalla trascrizione")
    return n


def controlla_js(A):
    """app.js (pubblicato) contro il conto di riferimento su casi casuali e casi al limite."""
    js = next((SITO / "assets").glob("app.*.js"))
    if js.read_text(encoding="utf-8").strip() != (RADICE / "app.js").read_text(encoding="utf-8").strip():
        err("assets/app.js diverso da app.js")
    rnd = random.Random(20261119)
    tassi = ["6.52", "8.07", "9.07", "0", "2.75", "3.4", "5.5", "12.125"]
    casi_rata = [(s * 100, t, p) for s in (1, 100, 2499999 // 100, 24999, 25000, 49999, 50000, 99999, 100000, 257500, 1000000) for t in ("6.52", "9.07", "0") for p in ("nuovo", "vecchio")]
    casi_rata += [(2499999, "6.52", "nuovo"), (2500000, "6.52", "nuovo"), (9999999, "8.07", "nuovo")]
    casi_rata += [(rnd.randint(100, 30000000), rnd.choice(tassi), rnd.choice(["nuovo", "vecchio"])) for _ in range(1500)]
    casi_rap = [(r, c) for r in (0, 1, 9999, 10000, 10001, 20000, 20001, 30000, 30001, 40000, 40001, 50000, 50001, 60000, 60001, 70000, 70001, 80000, 80001, 90000, 90001, 100000, 100001, 250000) for c in (0, 1, 2, 5, 15)]
    casi_rap += [(rnd.randint(0, 400000), rnd.randint(0, 6)) for _ in range(1500)]
    casi_mese = [(rnd.choice([1000, 5000, 7500, 20000, 41667, 150000]), rnd.randint(100, 20000000), rnd.choice(tassi)) for _ in range(800)] + [(1000, 500, "6.52"), (5000, 5000, "0"), (100000, 3000, "9.07")]
    casi_buco = [(c * 100, a) for c in (0, 3000, 5500, 20000, 25500, 27500, 32000, 60000, 500000) for a in range(1, 7)] + [(rnd.randint(0, 9000000), rnd.randint(1, 6)) for _ in range(400)]
    regole = {"fasce": A["rimborso"]["standard"]["fasce"], "rap": A["rimborso"]["rap"], "limiti": {"dipendente": A["limiti"]["dipendente"], "genitori": A["limiti"]["genitori"]}}
    prog = """
const CA = require(process.argv[2]); const I = JSON.parse(require('fs').readFileSync(0, 'utf8')); const R = I.regole;
const mill = t => CA.millesimi(t);
const out = {
  rata: I.rata.map(([s, t, p]) => { const anni = p === 'nuovo' ? CA.anniStandard(s, R.fasce) : 10; return Object.assign({anni}, CA.piano(s, mill(t), anni * 12)); }),
  rap: I.rap.map(([r, c]) => CA.rapMese(r, c, R.rap)),
  mese: I.mese.map(([p, s, t]) => CA.rapUnMese(p, s, mill(t), R.rap)),
  buco: I.buco.map(([c, a]) => CA.buco(c, a, R.limiti).righe),
  fmt: [CA.usd(123456789), CA.usd(500, true), CA.usd(505, true), CA.centesimi('$27,000.5'), CA.centesimi('abc'), CA.millesimi('6.52%'), CA.millesimi('6,5'),
        CA.testoGiorni(CA.giorniA('2027-03-02', new Date(2026, 10, 19))), CA.testoGiorni(CA.giorniA('2026-10-01', new Date(2026, 10, 19))), CA.testoGiorni(0), CA.testoGiorni(1)]
};
console.log(JSON.stringify(out));
"""
    copia = RADICE / "cache" / "app_verifica.js"
    copia.parent.mkdir(exist_ok=True)
    copia.write_text(js.read_text(encoding="utf-8"), encoding="utf-8")
    prova = RADICE / "cache" / "prova_calcolatori.js"
    prova.write_text(prog, encoding="utf-8")
    r = subprocess.run(["node", str(prova), str(copia)], input=json.dumps({"regole": regole, "rata": casi_rata, "rap": casi_rap, "mese": casi_mese, "buco": casi_buco}), capture_output=True, text=True)
    if r.returncode:
        err("node: " + r.stderr[-400:])
        return 0
    out = json.loads(r.stdout)
    for (s, t, p), g in zip(casi_rata, out["rata"]):
        anni = rif_anni(s) if p == "nuovo" else 10
        rif = rif_piano(s, t, anni * 12)
        if g["anni"] != anni or {k: g[k] for k in rif} != rif:
            err(f"JS rata {s} {t} {p}: {g}, riferimento {anni} {rif}")
    for (r_, c), g in zip(casi_rap, out["rap"]):
        if g != rif_rap(r_, c):
            err(f"JS RAP {r_} {c}: {g}, riferimento {rif_rap(r_, c)}")
    for (p, s, t), g in zip(casi_mese, out["mese"]):
        if {k: g[k] for k in ("interessi", "aInteressi", "aCapitale", "nonAddebitati", "aggiunta", "nuovoSaldo")} != rif_rap_mese(p, s, t):
            err(f"JS mese RAP {p} {s} {t}: {g}, riferimento {rif_rap_mese(p, s, t)}")
    for (c, a), g in zip(casi_buco, out["buco"]):
        if g != rif_buco(c, a):
            err(f"JS buco {c} {a}: diverso dal riferimento")
    giorni = (date(2027, 3, 2) - date(2026, 11, 19)).days
    if out["fmt"] != ["$1,234,567.89", "$5", "$5.05", 2700050, None, 6520, 6500, f"in {giorni} days", f"passed {(date(2026, 11, 19) - date(2026, 10, 1)).days} days ago", "today", "tomorrow"]:
        err(f"JS formati: {out['fmt']}")
    # conti a mano (scritti qui, non calcolati): 10.000 $ al 6,52 % in 10 anni = 113,65 $ (r = 0,0054333; (1+r)^120 = 1,91599; 10.000 × r ÷ (1 − 1/1,91599)); RAP 45.000 $ = 4 % = 1.800 $/anno = 150 $ al mese; con 2 persone a carico 50 $
    if rif_piano(1000000, "6.52", 120)["rata"] != 11365:
        err(f"conto a mano: rata di 10.000 $ al 6,52 % = {rif_piano(1000000, '6.52', 120)['rata']}")
    if (rif_rap(45000, 0), rif_rap(45000, 2), rif_rap(8000, 0), rif_rap(12000, 3), rif_rap(120000, 1)) != (15000, 5000, 1000, 1000, 95000):
        err("conti a mano del RAP diversi dal riferimento")
    b = rif_buco(3200000, 4)
    if (sum(x["studente"] for x in b), sum(x["genitori"] for x in b), sum(x["resto"] for x in b)) != (2700000, 6500000, 3600000):
        err("conto a mano del buco diverso dal riferimento")
    return len(casi_rata) + len(casi_rap) + len(casi_mese) + len(casi_buco)


def controlla_segreti():
    # i modelli sono spezzati per non far scattare la ricerca di chiavi su questo stesso file
    modello = re.compile("|".join([r"pk\.ey" + "J", "sk_" + "live", "sk_" + "test", "AI" + "za", "gh" + "p_", "api" + "key=[A-Za-z0-9]{8}", "sd_" + "live"]))
    n = 0
    for f in RADICE.rglob("*"):
        if f.is_file() and "cache" not in f.parts and "__pycache__" not in f.parts and f.suffix != ".png":
            n += 1
            if f.suffix == ".pdf":
                continue
            if modello.search(f.read_text(encoding="utf-8", errors="replace")):
                err(f"possibile chiave in {f.relative_to(RADICE)}")
    return n


def attesi_browser():
    def piano_txt(s, t, p):
        anni = rif_anni(s) if p == "nuovo" else 10
        x = rif_piano(s, t, anni * 12)
        return {"rata": usdc(x["rata"]), "anni": f"{anni} years ({x['mesi']} payments)", "pagato": usdc(x["pagato"]), "interessi": usdc(x["interessi"])}
    rata = [{"saldo": str(s // 100), "tasso": t, "piano": p, "atteso": piano_txt(s, t, p)} for s, t, p in
            [(2700000, "6.52", "nuovo"), (2700000, "6.52", "vecchio"), (1000000, "6.52", "nuovo"), (2499900, "8.07", "nuovo"), (2500000, "8.07", "nuovo"), (5750000, "6.52", "nuovo"),
             (6500000, "9.07", "nuovo"), (10000000, "8.07", "nuovo"), (20000000, "8.07", "vecchio"), (500000, "0", "vecchio")]]
    rap = []
    for red, car, saldo, tasso in [(45000, 0, 3000000, "6.52"), (45000, 2, 3000000, "6.52"), (8000, 0, None, "6.52"), (30000, 0, 5000000, "8.07"), (30001, 0, 5000000, "8.07"),
                                   (100000, 1, 2000000, "6.52"), (150000, 3, 20000000, "8.07"), (12000, 3, 1000000, "6.52"), (65000, 1, None, "6.52"), (20000, 0, 100000, "6.52")]:
        m = rif_rap(red, car)
        a = {"rata": usdc(m)}
        if saldo:
            u = rif_rap_mese(m, saldo, tasso)
            a.update({"interessi": usdc(u["interessi"]), "ainteressi": usdc(u["aInteressi"]), "acapitale": usdc(u["aCapitale"]), "nonaddebitati": usdc(u["nonAddebitati"]), "aggiunta": usdc(u["aggiunta"]), "nuovosaldo": usdc(u["nuovoSaldo"])})
        rap.append({"reddito": f"{red:,}", "carico": car, "saldo": None if saldo is None else str(saldo // 100), "tasso": tasso, "atteso": a})
    buco = []
    for costo, anni in [(3200000, 4), (2000000, 4), (6000000, 4), (4500000, 6), (500000, 2), (2750000, 1)]:
        r = rif_buco(costo, anni)
        d = lambda c: usd(c // 100)  # noqa: E731
        buco.append({"costo": f"{costo // 100:,}", "anni": anni, "atteso": {"resto": d(sum(x["resto"] for x in r)), "studente": d(sum(x["studente"] for x in r)), "genitori": d(sum(x["genitori"] for x in r)), "costo": d(costo * anni),
                                                                         "righe": [[f"Year {x['anno']}", d(x["costo"]), d(x["studente"]), d(x["genitori"]), d(x["resto"])] for x in r]}})
    A = json.loads((DATI / "aiuti.json").read_text(encoding="utf-8"))
    tipi = {"date": [], "asap": [], "check": [], "tutti": []}
    for v in A["fafsa"]["voci"]:
        t = "date" if any(d != M_FAFSA["apertura"] for d in v["date"]) else ("asap" if "soon as possible" in v["testo"] else "check")
        tipi[t].append(v["sigla"])
        tipi["tutti"].append(v["sigla"])
    oggi = "2026-12-01"
    g = lambda iso: (date.fromisoformat(iso) - date.fromisoformat(oggi)).days  # noqa: E731
    return {"rata": rata, "tipi": [["6.52"], ["8.07"], ["9.07"]], "rap": rap, "buco": buco, "oggi": oggi,
            "scadenze": {"tipi": tipi, "cerca_new": [v["sigla"] for v in A["fafsa"]["voci"] if "new" in v["nome"].lower()],
                         "giorni": [["2027-01-15", f"in {g('2027-01-15')} days"], ["2028-06-30", f"in {g('2028-06-30')} days"], ["2026-10-01", f"passed {-g('2026-10-01')} days ago"]]}}


def main():
    if not SITO.exists():
        raise SystemExit("manca collegeaid/sito: lanciare prima genera.py")
    A, F, n_frasi = controlla_dati()
    n_faq, n_cit, n_link, n_pag = controlla_pagine(A, F)
    n_cifre = controlla_cifre(A)
    n_js = controlla_js(A)
    n_file = controlla_segreti()
    errori_mon, _info = MON.controlla_sito("collegeaid", SITO)
    for e in errori_mon:
        err("monetizzazione: " + e)
    print(f"{n_pag} pagine, {len(F)} fonti, {n_frasi} frasi alla lettera, {n_cit} citazioni in pagina, {n_faq} FAQ da ricerche misurate, {n_link} link, "
          f"{n_cifre} cifre confrontate con le trascrizioni a mano, {n_js} casi dei calcolatori (app.js = conto di riferimento), {n_file} file senza chiavi.")
    if "--browser" in sys.argv:
        r = subprocess.run(["node", str(RADICE / "verifica_browser.js")], env=dict(os.environ, ATTESI=json.dumps(attesi_browser())), capture_output=True, text=True)
        print(r.stdout.strip())
        if r.returncode:
            err("browser: vedi sopra" + (r.stderr[-300:] if r.stderr else ""))
    if ERR:
        print(f"\n{len(ERR)} ERRORI:")
        for e in ERR[:80]:
            print(" -", e)
        raise SystemExit(1)
    print("0 errori.")


if __name__ == "__main__":
    main()
