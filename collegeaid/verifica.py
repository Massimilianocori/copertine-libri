"""Controlli di US College Aid (collegeaid/sito/). Uso: python3 collegeaid/verifica.py [--browser]

Indipendenti dal costruttore: le cifre chiave sono TRASCRITTE A MANO qui sotto dai documenti ufficiali (tassi 2026-27 e storia dal 2013,
tetti, scaglioni del RAP, fasce del piano standard, date dei 10 Stati) e confrontate con dati/aiuti.json e con le pagine.
I calcolatori (app.js, eseguito con node) sono confrontati con un conto scritto a parte in questo file (Decimal, niente codice in comune).
Poi: impronte dei file grezzi e frasi alla lettera, ogni citazione in pagina = frase della fonte, voci FAFSA = testo del PDF riletto,
ogni importo in dollari e ogni percentuale delle pagine dentro l'insieme delle cifre trascritte o ricalcolate, titoli e descrizioni,
schede delle università: ogni cella riletta dal file College Scorecard (dallo zip ufficiale se è in cache), anni trascritti a mano dal dizionario,
«buco» rifatto con un conto in forma chiusa e con quello anno per anno, scelta delle 200 ricontrollata sulle misure,
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
DOMINI_UFFICIALI = {"studentaid.gov", "www.govinfo.gov", "fsapartners.ed.gov", "collegescorecard.ed.gov", "ed-public-download.scorecard.network"}
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
M_STD_MIN = 50   # 34 CFR 685.208(b)(1)(ii), (b)(8)(ii) e (c)(1)(ii): pagamento di almeno 50 $ al mese
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


def rif_piano(saldo_cent, tasso_pc, mesi, minimo=M_STD_MIN * 100):
    """tasso_pc: stringa «6.52». Rata fissa arrotondata al centesimo, mai sotto il minimo di 50 $ (se si deve meno, si paga il dovuto);
    interesse mensile arrotondato al centesimo; l'ultima rata chiude."""
    r = Decimal(tasso_pc) / 1200
    calcolata = cent(Decimal(saldo_cent) / mesi) if r == 0 else cent(Decimal(saldo_cent) * r / (1 - (1 + r) ** (-mesi)))
    primo_dovuto = saldo_cent + cent(Decimal(saldo_cent) * Decimal(tasso_pc) / 1200)
    piccolo = saldo_cent < minimo            # saldo sotto 50 $: un solo pagamento, pari al dovuto (685.208)
    rata = primo_dovuto if piccolo else max(calcolata, minimo)
    resto, pagato, interessi, n = saldo_cent, 0, 0, 0
    while resto > 0:
        i = cent(Decimal(resto) * Decimal(tasso_pc) / 1200)   # prima il prodotto, poi la divisione: i casi a metà centesimo restano esatti
        dovuto = resto + i
        paga = dovuto if (n == mesi - 1 or dovuto < rata) else rata
        resto, pagato, interessi, n = dovuto - paga, pagato + paga, interessi + i, n + 1
    return {"rata": min(rata, primo_dovuto), "mesi": n, "pagato": pagato, "interessi": interessi, "minimo": not piccolo and rata > calcolata, "piccolo": piccolo}


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
    if R["standard"]["minimo_mese"] != M_STD_MIN:
        err("aiuti.json: pagamento minimo del piano standard diverso dalla trascrizione")
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
    scelte_uni = json.loads((DATI / "domanda_universita.json").read_text(encoding="utf-8"))["scelte"]
    attese += [f"{P_UNI}/index.html"] + [f"{P_UNI}/{sc_slug(x['nome'])}/index.html" for x in scelte_uni]
    dom.update({f["frase"]: f["volume_mese"] for x in scelte_uni for f in x["frasi"]})   # FAQ delle schede: frasi «<università> tuition» e «<università> cost»
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
        npc = set(re.findall(r'<a class="btn sec" href="([^"]+)" rel="nofollow noopener" data-npc>', html_)) if p.startswith(f"{P_UNI}/") else set()   # calcolatore dell'università: indirizzo del file, controllato in controlla_universita
        for href in re.findall(r'<a [^>]*href="([^"]+)"', html_):
            n_link += 1
            if href in npc:
                continue
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
           "student-loan-payment-calculator": base | std | esempi_rata | {M_STD_MIN}, "repayment-assistance-plan": rap | esempi_rap | {50}, "student-loan-interest-rates": {10000},
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
        if nuovo["minimo"] or vecchio["minimo"]:
            err(f"rata: l'esempio {saldo} è sotto il pagamento minimo")
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
    if [(f["sotto"], f["anni"]) for f in reg["fasce"]] != M_STD or reg["minimo_mese"] != M_STD_MIN:
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
    regole = {"fasce": A["rimborso"]["standard"]["fasce"], "minimo": A["rimborso"]["standard"]["minimo_mese"] * 100, "rap": A["rimborso"]["rap"], "limiti": {"dipendente": A["limiti"]["dipendente"], "genitori": A["limiti"]["genitori"]}}
    prog = """
const CA = require(process.argv[2]); const I = JSON.parse(require('fs').readFileSync(0, 'utf8')); const R = I.regole;
const mill = t => CA.millesimi(t);
const out = {
  rata: I.rata.map(([s, t, p]) => { const anni = p === 'nuovo' ? CA.anniStandard(s, R.fasce) : 10; return Object.assign({anni}, CA.piano(s, mill(t), anni * 12, R.minimo)); }),
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
    # minimo: 3.000 $ al 6,52 % in 10 anni darebbe 34,10 $ -> 50 $; 40 $ di saldo -> un solo pagamento di 40,22 $ (40 $ + 0,22 $ di interesse)
    m1, m2 = rif_piano(300000, "6.52", 120), rif_piano(4000, "6.52", 120)
    if (m1["rata"], m1["minimo"], m1["mesi"] < 120) != (5000, True, True) or (m2["rata"], m2["mesi"], m2["pagato"], m2["minimo"], m2["piccolo"]) != (4022, 1, 4022, False, True):
        err(f"conti a mano del pagamento minimo diversi dal riferimento: {m1} {m2}")
    if rif_piano(1000000, "6.52", 120)["rata"] != 11365:
        err(f"conto a mano: rata di 10.000 $ al 6,52 % = {rif_piano(1000000, '6.52', 120)['rata']}")
    if (rif_rap(45000, 0), rif_rap(45000, 2), rif_rap(8000, 0), rif_rap(12000, 3), rif_rap(120000, 1)) != (15000, 5000, 1000, 1000, 95000):
        err("conti a mano del RAP diversi dal riferimento")
    b = rif_buco(3200000, 4)
    if (sum(x["studente"] for x in b), sum(x["genitori"] for x in b), sum(x["resto"] for x in b)) != (2700000, 6500000, 3600000):
        err("conto a mano del buco diverso dal riferimento")
    return len(casi_rata) + len(casi_rap) + len(casi_mese) + len(casi_buco)


# ---------------------------------------------------------------- schede delle università (file College Scorecard)
# Trascritto a mano: indirizzo e data del file, anno di ogni colonna come lo scrive il foglio «Most_Recent_Inst_Cohort_Map» del dizionario
# ufficiale, e come deve comparire in pagina. Le fasce di reddito sono quelle dei nomi delle colonne nel dizionario.
M_SC_URL = "https://ed-public-download.scorecard.network/downloads/Most-Recent-Cohorts-Institution_11022026.zip"
M_SC_AGG = "2026-11-02"
M_SC_ANNI = {
    "TUITIONFEE_IN": ("AcadYr 2025-26, reported in IPEDS DCY2025-26", "2025–26"),
    "TUITIONFEE_OUT": ("AcadYr 2025-26, reported in IPEDS DCY2025-26", "2025–26"),
    "COSTT4_A": ("AcadYr 2024-25, reported in IPEDS DCY2025-26", "2024–25"),
    "NPT4": ("AcadYr 2024-25, reported in IPEDS DCY2025-26", "2024–25"),
    "ADM_RATE": ("Fall 2024, reported in IPEDS DCY2024-25", "fall 2024"),
    "UGDS": ("Fall 2024, reported in IPEDS DCY2024-25", "fall 2024"),
    "C150_4": ("Fall 2019 or AcadYr 2019-20 cohort (differs by institutional calendar), reported in IPEDS DCY2025-26", "2019–20 entering class"),
    "GRAD_DEBT_MDN": ("NSLDS FY2024, FY2025 pooled cohorts", "fiscal years 2024 and 2025"),
    "PLUS_DEBT_INST_MD": ("NSLDS AY2023-24, AY2024-25 pooled cohorts", "2023–24 and 2024–25"),
}
M_SC_FASCE = ["$0 to $30,000", "$30,001 to $48,000", "$48,001 to $75,000", "$75,001 to $110,000", "$110,000 or more"]
M_SC_TIPO = {"1": ("public", "Public"), "2": ("nonprofit", "Private nonprofit"), "3": ("forprofit", "Private for-profit")}
M_SC_MANCA = {"NA": "Not reported in the file", "PS": "Suppressed in the file (privacy)"}
N_UNIVERSITA = 200
P_UNI = "college-costs"


def sc_num(v):
    return re.fullmatch(r"-?\d+(\.\d+)?", v) is not None


def sc_usd(v):
    if not sc_num(v):
        return M_SC_MANCA[v]
    n = int(v)
    return "−$" + format(-n, ",") if n < 0 else "$" + format(n, ",")


def sc_pc(v):
    """«0.0365» -> «3.65%» spostando la virgola a mano (nessuna aritmetica in virgola mobile)."""
    if not sc_num(v):
        return M_SC_MANCA[v]
    intera, _, dec = v.partition(".")
    cifre = intera + dec.ljust(2, "0")
    a, b = cifre[:len(intera) + 2].lstrip("0") or "0", cifre[len(intera) + 2:].rstrip("0")
    return a + ("." + b if b else "") + "%"


def sc_slug(nome):
    out, prec = [], "-"
    for ch in nome.lower().replace("&", " and ").replace("'", ""):
        ch = ch if (ch.isascii() and ch.isalnum()) else "-"
        if ch != "-" or prec != "-":
            out.append(ch)
        prec = ch
    return "".join(out).strip("-")


def sc_gap(prezzo):
    """Quattro anni al prezzo annuo dato (dollari): quanto coprono al massimo i prestiti federali, con i tetti trascritti a mano.
    Conto in forma chiusa, diverso da quello delle pagine: studente = somma dei minimi tra tetto annuo e prezzo; genitori = il minimo tra
    il tetto totale e la somma, anno per anno, del minimo tra tetto annuo e ciò che resta dopo lo studente."""
    c = max(int(prezzo), 0)
    tetti = [M_LIM["dip"][min(i, 2)][0] for i in range(4)]
    s_anni = [min(t, c) for t in tetti]
    if sum(tetti) > M_LIM["dip_tot"][0]:
        raise SystemExit("i tetti annui dello studente superano il totale: il conto in forma chiusa non vale più")
    genitori = min(M_LIM["genitori"][1], sum(min(M_LIM["genitori"][0], c - s) for s in s_anni))
    out = {"quattro": 4 * c, "studente": sum(s_anni), "genitori": genitori, "resto": 4 * c - sum(s_anni) - genitori}
    passo = rif_buco(c * 100, 4)   # e il conto anno per anno deve dare lo stesso
    if (sum(x["studente"] for x in passo), sum(x["genitori"] for x in passo), sum(x["resto"] for x in passo)) != (out["studente"] * 100, out["genitori"] * 100, out["resto"] * 100):
        err(f"buco delle università: i due conti di riferimento non coincidono per {prezzo}")
    return out


def sc_file():
    """Le righe del file: dallo zip ufficiale se è in cache (e allora l'estratto deve essere identico), altrimenti dall'estratto registrato."""
    import csv
    import io
    import zipfile
    S = json.loads((DATI / "fonti_scorecard.json").read_text(encoding="utf-8"))
    f, d = S["fonti"]["scorecard"], S["fonti"]["scorecard_diz"]
    if f["url"] != M_SC_URL or f["aggiornato_il"] != M_SC_AGG or f["http"] != 200 or d["http"] != 200:
        err("Scorecard: indirizzo, data o stato HTTP diversi dalla trascrizione")
    for x in (f, d):
        if not any(x["url"].startswith(f"https://{dom}/") for dom in DOMINI_UFFICIALI) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", x["letto_il"]) or not re.fullmatch(r"[0-9a-f]{64}", x["sha256"]):
            err(f"Scorecard: registrazione incompleta della fonte {x['url']}")
    estratto = (RADICE / f["estratto"]).read_bytes()
    if hashlib.sha256(estratto).hexdigest() != f["estratto_sha256"]:
        err("Scorecard: sha256 dell'estratto diverso da quello registrato")
    diz = (RADICE / d["file"]).read_bytes()
    if hashlib.sha256(diz).hexdigest() != d["sha256"]:
        err("Scorecard: sha256 del dizionario diverso da quello registrato")
    righe_e = list(csv.DictReader(io.StringIO(estratto.decode("utf-8"), newline="")))
    per_id = {r["UNITID"]: r for r in righe_e}
    zip_ = RADICE / f["file"]
    origine = "estratto registrato (lo zip non è in cache)"
    if zip_.exists():
        grezzo = zip_.read_bytes()
        if hashlib.sha256(grezzo).hexdigest() != f["sha256"] or len(grezzo) != f["byte"]:
            err("Scorecard: sha256 dello zip diverso da quello registrato")
        dati = zipfile.ZipFile(io.BytesIO(grezzo)).read(f["csv"])
        if hashlib.sha256(dati).hexdigest() != f["csv_sha256"]:
            err("Scorecard: sha256 del CSV nello zip diverso da quello registrato")
        righe_z = list(csv.DictReader(io.StringIO(dati.decode("utf-8-sig"), newline="")))
        if len(righe_z) != f["istituti"] or len(righe_z) != len(righe_e):
            err(f"Scorecard: {len(righe_z)} righe nello zip, {len(righe_e)} nell'estratto, {f['istituti']} registrate")
        diverse = sum(1 for z, e in zip(righe_z, righe_e) if any(z[c] != e[c] for c in e))
        if diverse:
            err(f"Scorecard: {diverse} righe dell'estratto diverse dal file ufficiale")
        per_id = {r["UNITID"]: r for r in righe_z}
        origine = f"zip ufficiale ({len(righe_z)} righe, estratto identico cella per cella)"
    # anni: la trascrizione a mano = fonti_scorecard.json, e il testo è davvero nel dizionario (cercato nel file .xlsx, senza il lettore di raccolta/)
    import html as _html
    xml = "".join(zipfile.ZipFile(io.BytesIO(diz)).read(n).decode("utf-8", errors="replace") for n in zipfile.ZipFile(io.BytesIO(diz)).namelist() if n.endswith(".xml"))
    xml = _html.unescape(xml)
    for col, anno in S["anni"].items():
        chiave = "NPT4" if col.startswith("NPT4") else col
        if chiave in M_SC_ANNI and anno != M_SC_ANNI[chiave][0]:
            err(f"Scorecard: anno di {col} «{anno}» diverso dalla trascrizione")
    for col, (testo_, _) in M_SC_ANNI.items():
        if testo_ not in xml:
            err(f"Scorecard: «{testo_}» non si ritrova nel dizionario ufficiale")
    return S, per_id, origine


def controlla_universita():
    """Ogni cifra delle schede contro il file; il «buco» rifatto con un conto scritto a parte; scelta delle 200 contro le misure
    (domanda di un'università = volume della sua frase più cercata)."""
    S, righe, origine = sc_file()
    D = json.loads((DATI / "domanda_universita.json").read_text(encoding="utf-8"))
    scelte = D["scelte"]
    n = 0
    # ---- la scelta: 200, in ordine di domanda, ogni domanda = frase tuition migliore + frase cost migliore, misure = risposte conservate
    if len(scelte) != N_UNIVERSITA or len({s["unitid"] for s in scelte}) != N_UNIVERSITA:
        err(f"università: {len(scelte)} scelte invece di {N_UNIVERSITA}")
    if [s["domanda_mese"] for s in scelte] != sorted((s["domanda_mese"] for s in scelte), reverse=True) or D["domanda_totale_scelte"] != sum(s["domanda_mese"] for s in scelte):
        err("università: scelte non in ordine di domanda o totale sbagliato")
    fuori = max((a["domanda_mese"] for a in D["altre"]), default=0)
    senza = {e["unitid"] for e in D["escluse_senza_dati"]}
    if any(a["domanda_mese"] > scelte[-1]["domanda_mese"] and a["unitid"] not in senza for a in D["altre"]):
        err(f"università: una candidata rimasta fuori ha più domanda ({fuori}) dell'ultima scelta ({scelte[-1]['domanda_mese']})")
    cache = RADICE / "cache" / "domanda_universita"
    risposte = 0
    for s in scelte:
        vol = {f["frase"]: f["volume_mese"] for f in s["frasi"]}
        t = max((v for f, v in vol.items() if f.endswith(" tuition")), default=0)
        c = max((v for f, v in vol.items() if f.endswith(" cost")), default=0)
        if s["domanda_mese"] != max(t, c) or s["somma_tuition_cost"] != t + c or s["domanda_mese"] <= 0:
            err(f"università {s['nome']}: domanda {s['domanda_mese']} diversa dal massimo tra {t} e {c}")
        if vol.get(s["frase_titolo"], 0) <= 0 or vol[s["frase_titolo"]] != s["volume_titolo"] or s["volume_titolo"] != max(t, c):
            err(f"università {s['nome']}: la frase del titolo «{s['frase_titolo']}» non è la più cercata o non è misurata")
        if s["nome"] != righe[s["unitid"]]["INSTNM"]:
            err(f"università {s['unitid']}: nome diverso dal file")
        if cache.exists():
            for f, v in vol.items():
                g = cache / (hashlib.sha1(f.encode("utf-8")).hexdigest()[:16] + ".json")
                if g.exists():
                    risposte += 1
                    x = json.loads(g.read_text(encoding="utf-8"))
                    if x.get("keyword", "").lower() != f or (x.get("volume") or 0) != v:
                        err(f"università: «{f}» = {v} nel file, {x.get('volume')} nella risposta conservata")
    # ---- le pagine
    A_T, A_C, A_N = M_SC_ANNI["TUITIONFEE_IN"][1], M_SC_ANNI["COSTT4_A"][1], M_SC_ANNI["NPT4"][1]
    agg = lunga(M_SC_AGG)
    limiti = {x for coppia in M_LIM["dip"] for x in coppia[:1]} | {M_LIM["dip_tot"][0]} | set(M_LIM["genitori"])
    quattro = sum(M_LIM["dip"][min(i, 2)][0] for i in range(4))
    limiti |= {quattro, quattro + M_LIM["genitori"][1]}
    fasce_usd = {0, 30000, 30001, 48000, 48001, 75000, 75001, 110000}
    slug_di = {s["unitid"]: sc_slug(s["nome"]) for s in scelte}
    if len(set(slug_di.values())) != len(slug_di):
        err("università: slug doppi")
    npc_ammessi = set()
    for s in scelte:
        r = righe[s["unitid"]]
        p = f"{P_UNI}/{slug_di[s['unitid']]}/index.html"
        if not (SITO / p).exists():
            err(f"università {s['nome']}: manca la pagina {p}")
            continue
        html_ = leggi(p)
        main = principale(html_)
        suff = "PUB" if r["CONTROL"] == "1" else "PRIV"
        altro = "PRIV" if suff == "PUB" else "PUB"
        if any(r[f"NPT4{i}_{altro}"] != "NA" for i in ("", "1", "2", "3", "4", "5")):
            err(f"{p}: il file ha prezzi netti anche nelle colonne {altro}: la pagina ne mostra solo una serie")
        if f'data-universita="{s["unitid"]}"' not in main:
            err(f"{p}: UNITID mancante o diverso")
        # ogni cella con una colonna del file: il testo è quello del file
        celle = re.findall(r'<td class="[^"]*" (?:colspan="5" )?data-c="([A-Z0-9_]+)">([^<]*)</td>', main)
        viste = {}
        for col, testo_ in celle:
            n += 1
            atteso = (format(int(r[col]), ",") if col == "UGDS" else sc_pc(r[col]) if col in ("ADM_RATE", "C150_4") else sc_usd(r[col]))
            if unescape(testo_) != atteso:
                err(f"{p}: {col} = «{testo_}», nel file {r[col]} (atteso «{atteso}»)")
            viste[col] = viste.get(col, 0) + 1
        attese = {"TUITIONFEE_IN": 1, "TUITIONFEE_OUT": 1, "COSTT4_A": 2 if sc_num(r["COSTT4_A"]) else 1, "ADM_RATE": 1, "C150_4": 1, "GRAD_DEBT_MDN": 1, "PLUS_DEBT_INST_MD": 1, "UGDS": 1, f"NPT4_{suff}": 2}
        attese.update({f"NPT4{i}_{suff}": 2 for i in "12345"})
        if viste != attese:
            err(f"{p}: celle del file {viste}, attese {attese}")
        # l'anno accanto a ogni cifra
        for col, anno in re.findall(r'data-c="([A-Z0-9_]+)">[^<]*</td><td>([^<]*)</td></tr>', main):
            n += 1
            if anno != M_SC_ANNI[col][1]:
                err(f"{p}: anno di {col} «{anno}», atteso «{M_SC_ANNI[col][1]}»")
        vis = visibile(main)
        if len(re.findall(r'data-c="[A-Z0-9_]+">[^<]*</td><td>[^<]*</td></tr>', main)) != 8 or f"net price a year, {A_N}" not in vis or agg not in vis:
            err(f"{p}: manca l'anno di una cifra o la data del file")
        # etichette delle fasce di reddito, nell'ordine del file
        for tab_id in ("net-price", "gap"):
            pezzo = main[main.index(f'<h2 id="{tab_id}">'):]
            pezzo = pezzo[:pezzo.index("</table>")]
            etichette = re.findall(r'<th scope="row">([^<]*)</th><td class="[^"]*" (?:colspan="5" )?data-c="NPT4(\d)_', pezzo)
            if etichette != [(e, str(i)) for i, e in enumerate(M_SC_FASCE, 1)]:
                err(f"{p}: fasce di reddito della tabella {tab_id} diverse dal file: {etichette}")
        # il buco: ogni riga rifatta
        gap_num = set()
        righe_gap = re.findall(r'<tr(?: class="ora")? data-gap="([A-Z0-9_]+)"><th scope="row">[^<]*</th>(.*?)</tr>', main)
        cols_gap = [c for c, _ in righe_gap]
        if cols_gap != [f"NPT4{i}_{suff}" for i in "12345"] + [f"NPT4_{suff}"] + (["COSTT4_A"] if sc_num(r["COSTT4_A"]) else []):
            err(f"{p}: righe del buco {cols_gap}")
        for col, celle_ in righe_gap:
            n += 1
            if not sc_num(r[col]):
                if "data-g=" in celle_:
                    err(f"{p}: buco calcolato per {col}, che nel file manca")
                continue
            g = sc_gap(r[col])
            mostrato = dict(re.findall(r'data-g="(\w+)">([^<]*)</td>', celle_))
            if mostrato != {k: usd(v) for k, v in g.items()}:
                err(f"{p}: buco di {col} {mostrato}, riferimento {g}")
            gap_num |= set(g.values())
        medio = sc_gap(r[f"NPT4_{suff}"])
        if (usd(medio["resto"]) not in vis and medio["resto"] > 0) or f'four years at {s["nome"]} come to {usd(medio["quattro"])}' not in vis:
            err(f"{p}: la frase sul buco medio non ha le cifre del conto di riferimento")
        # ogni importo e ogni percentuale del testo: file, tetti trascritti, fasce, conto di riferimento
        corpo = re.sub(r'(?s)<blockquote class="cit" data-voce.*?</blockquote>|<section class="fonti-box".*?</section>|<h2 id="others">.*?</ul>', " ", main)
        ammessi = limiti | fasce_usd | gap_num | {abs(int(r[c])) for c in ["TUITIONFEE_IN", "TUITIONFEE_OUT", "COSTT4_A", "GRAD_DEBT_MDN", "PLUS_DEBT_INST_MD", f"NPT4_{suff}"] + [f"NPT4{i}_{suff}" for i in "12345"] if sc_num(r[c])}
        testa = " ".join(unescape(x) for x in re.findall(r'<title>(.*?)</title>|<meta (?:name="description"|property="og:(?:title|description)") content="(.*?)">', html_)[0:4] for x in x) + " " + " ".join(
            json.dumps(json.loads(x), ensure_ascii=False) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html_))
        for x in importi(visibile(corpo)) | importi(testa):   # anche titolo, descrizione e dati strutturati
            n += 1
            if x not in ammessi:
                err(f"{p}: importo non previsto ${x:,}")
        pc_ammesse = {sc_pc(r[c])[:-1] for c in ("ADM_RATE", "C150_4") if sc_num(r[c])} | {M_TASSI["ug"][2], M_TASSI["plus"][2], "150"}
        for x in re.findall(r"(\d+(?:\.\d+)?)%", visibile(corpo)):
            n += 1
            if x not in pc_ammesse:
                err(f"{p}: percentuale non prevista {x}%")
        # le altre università dello stesso Stato: nome e tasse dal file
        for sl, nome_, tasse in re.findall(r'<li><a href="/college-costs/([a-z0-9-]+)/"><b>([^<]*)</b><small>(\S+) tuition and fees', main):
            n += 1
            uid = next((k for k, v in slug_di.items() if v == sl), None)
            if not uid or unescape(nome_) != righe[uid]["INSTNM"] or tasse != sc_usd(righe[uid]["TUITIONFEE_IN"]) or righe[uid]["STABBR"] != r["STABBR"]:
                err(f"{p}: riquadro «altre università» sbagliato per {sl}")
        # titolo dalla frase misurata, nome ufficiale, Stato, link
        tit = unescape(re.search(r"<title>(.*?)</title>", html_)[1])
        piatto = lambda x: re.sub(r"\s+", " ", re.sub(r"[.\-:,]", " ", x.lower())).strip()  # noqa: E731  («St. John's» = «st john's»: la punteggiatura non conta in una ricerca)
        if not piatto(tit).startswith(piatto(s["frase_titolo"]) + " ") and piatto(tit) != piatto(s["frase_titolo"]):
            err(f"{p}: il titolo «{tit}» non comincia con la frase misurata «{s['frase_titolo']}»")
        h1 = unescape(re.search(r"<h1>(.*?)</h1>", html_)[1])
        if not h1.startswith(r["INSTNM"]):
            err(f"{p}: h1 senza il nome ufficiale")
        tipo = M_SC_TIPO[r["CONTROL"]][1]
        if f"{r['CITY']}, {r['STABBR']} · {tipo} ·" not in vis:
            err(f"{p}: città, Stato o tipo diversi dal file")
        fafsa = f"/fafsa-deadlines/{M_STATI[r['STABBR']][0]}/" if r["STABBR"] in M_STATI else "/fafsa-deadlines/"
        if f'<a class="btn sec" href="{fafsa}">' not in main or f'<blockquote class="cit" data-voce="{r["STABBR"]}">' not in main:
            err(f"{p}: manca il link alla scadenza FAFSA di {r['STABBR']} o la voce del modulo")
        for dest in ("/federal-student-loan-limits/", "/parent-plus-loans/", "/student-loan-interest-rates/", "/student-loan-payment-calculator/", f"/{P_UNI}/"):
            if f'href="{dest}"' not in main:
                err(f"{p}: manca il link a {dest}")
        if '<h2 id="read">How to read this page</h2>' not in main or "not a forecast and not advice" not in vis:
            err(f"{p}: manca la nota «come leggere» o l'avvertenza sul conto")
        if any(not sc_num(r[c]) for c in ("TUITIONFEE_OUT", "COSTT4_A", "ADM_RATE", "C150_4", "GRAD_DEBT_MDN", "PLUS_DEBT_INST_MD") + tuple(f"NPT4{i}_{suff}" for i in "12345")) and "Some figures are missing." not in vis:
            err(f"{p}: valori mancanti nel file senza la nota che lo dice")
        m = re.search(r'<a class="btn sec" href="([^"]+)" rel="nofollow noopener" data-npc>', main)
        v = r["NPCURL"].strip()
        atteso_npc = None if v in ("NA", "PS", "") or " " in v else (v if re.match(r"https?://", v, re.I) else "https://" + v)
        if (unescape(m[1]) if m else None) != atteso_npc:
            err(f"{p}: indirizzo del calcolatore «{m and m[1]}», nel file «{v}»")
        if atteso_npc:
            npc_ammessi.add(atteso_npc)
    # ---- indice
    ind = leggi(f"{P_UNI}/index.html")
    righe_i = re.findall(r'<tr data-nome="([^"]*)" data-tipo="(\w+)" data-sigla="(\d+)"><th scope="row"><a href="/college-costs/([a-z0-9-]+)/">([^<]*)</a>(.*?)</tr>', ind)
    if len(righe_i) != N_UNIVERSITA or {x[2] for x in righe_i} != set(slug_di):
        err(f"indice delle università: {len(righe_i)} righe invece di {N_UNIVERSITA}")
    oltre = 0
    for cerca, tipo, uid, sl, nome_, resto in righe_i:
        n += 1
        r = righe[uid]
        suff = "PUB" if r["CONTROL"] == "1" else "PRIV"
        g = sc_gap(r[f"NPT4_{suff}"])
        oltre += g["resto"] > 0
        celle = re.findall(r'data-c="([A-Z0-9_]+)">([^<]*)</td>', resto)
        if (sl != slug_di[uid] or unescape(nome_) != r["INSTNM"] or tipo != M_SC_TIPO[r["CONTROL"]][0] or r["INSTNM"].lower() not in unescape(cerca) or r["STABBR"].lower() not in unescape(cerca).split()
                or celle != [("TUITIONFEE_IN", sc_usd(r["TUITIONFEE_IN"])), ("TUITIONFEE_OUT", sc_usd(r["TUITIONFEE_OUT"])), (f"NPT4_{suff}", sc_usd(r[f"NPT4_{suff}"]))]
                or f'data-g="resto">{usd(g["resto"])}</td>' not in resto or f"{r['CITY']}, {r['STABBR']} · {M_SC_TIPO[r['CONTROL']][1]}" not in unescape(resto)):
            err(f"indice delle università: riga di {r['INSTNM']} diversa dal file o dal conto di riferimento")
    vis = visibile(principale(ind))
    if f"<b>{oltre}</b>" not in ind or agg not in vis or A_T not in vis or A_N not in vis:
        err("indice delle università: conteggio del buco, data del file o anni mancanti")
    for x in importi(vis):
        if x not in limiti and not any(x == abs(int(righe[u][c])) for u in slug_di for c in ("TUITIONFEE_IN", "TUITIONFEE_OUT", "NPT4_PUB", "NPT4_PRIV") if sc_num(righe[u][c])) and x not in {sc_gap(righe[u]["NPT4_PUB" if righe[u]["CONTROL"] == "1" else "NPT4_PRIV"])["resto"] for u in slug_di}:
            err(f"indice delle università: importo non previsto ${x:,}")
    return n, origine, D, npc_ammessi, risposte


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
        periodo = "1 payment: the balance you owe" if x["piccolo"] else (f"{x['mesi']} payment{'' if x['mesi'] == 1 else 's'} (${M_STD_MIN} minimum)") if x["minimo"] else f"{anni} years ({x['mesi']} payments)"
        return {"rata": usdc(x["rata"]), "anni": periodo, "pagato": usdc(x["pagato"]), "interessi": usdc(x["interessi"])}
    rata = [{"saldo": f"{s // 100}.{s % 100:02d}", "tasso": t, "piano": p, "atteso": piano_txt(s, t, p)} for s, t, p in
            [(2700000, "6.52", "nuovo"), (2700000, "6.52", "vecchio"), (1000000, "6.52", "nuovo"), (2499900, "8.07", "nuovo"), (2500000, "8.07", "nuovo"), (5750000, "6.52", "nuovo"),
             (6500000, "9.07", "nuovo"), (10000000, "8.07", "nuovo"), (20000000, "8.07", "vecchio"), (500000, "0", "vecchio"), (300000, "6.52", "nuovo"), (300000, "6.52", "vecchio"), (4000, "6.52", "nuovo"), (4990, "9.07", "vecchio"), (100000, "0", "vecchio")]]
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
    # università: filtro dell'indice (atteso dal file, non dalle pagine) e campione di schede per tutte le viste (le prime per domanda e quelle con dati mancanti)
    S_, righe_, _o = sc_file()
    scelte = json.loads((DATI / "domanda_universita.json").read_text(encoding="utf-8"))["scelte"]
    tipi_u = {"tutti": [x["unitid"] for x in scelte]}
    for k, (cod, _) in M_SC_TIPO.items():
        ids = [x["unitid"] for x in scelte if righe_[x["unitid"]]["CONTROL"] == k]
        if ids:
            tipi_u[cod] = ids
    nomi_stati = {v["sigla"]: v["nome"] for v in A["fafsa"]["voci"]}
    def trova(q):  # noqa: E306
        return [x["unitid"] for x in scelte if q in " ".join([x["nome"], righe_[x["unitid"]]["CITY"], nomi_stati[righe_[x["unitid"]]["STABBR"]], righe_[x["unitid"]]["STABBR"], x["frase_titolo"]]).lower()]
    manca = [x for x in scelte if any(righe_[x["unitid"]][c] in ("NA", "PS") for c in ("COSTT4_A", "ADM_RATE", "C150_4", "GRAD_DEBT_MDN", "PLUS_DEBT_INST_MD", "TUITIONFEE_OUT"))]
    lunghi = sorted(scelte, key=lambda x: -len(x["nome"]))[:2]
    campione = [f"/{P_UNI}/{sc_slug(x['nome'])}/" for x in {y["unitid"]: y for y in scelte[:4] + manca[:4] + lunghi}.values()]
    universita = {"tipi": tipi_u, "cerca": [[q, trova(q)] for q in ("ohio", "university of california", "harvard", "tx")], "campione": campione}
    return {"rata": rata, "tipi": [["6.52"], ["8.07"], ["9.07"]], "rap": rap, "buco": buco, "oggi": oggi, "universita": universita,
            "scadenze": {"tipi": tipi, "cerca_new": [v["sigla"] for v in A["fafsa"]["voci"] if "new" in v["nome"].lower()],
                         "giorni": [["2027-01-15", f"in {g('2027-01-15')} days"], ["2028-06-30", f"in {g('2028-06-30')} days"], ["2026-10-01", f"passed {-g('2026-10-01')} days ago"]]}}


def main():
    if not SITO.exists():
        raise SystemExit("manca collegeaid/sito: lanciare prima genera.py")
    A, F, n_frasi = controlla_dati()
    n_faq, n_cit, n_link, n_pag = controlla_pagine(A, F)
    n_cifre = controlla_cifre(A)
    n_uni, origine_uni, D_uni, _npc, n_risposte = controlla_universita()
    n_js = controlla_js(A)
    n_file = controlla_segreti()
    errori_mon, _info = MON.controlla_sito("collegeaid", SITO)
    for e in errori_mon:
        err("monetizzazione: " + e)
    print(f"{n_pag} pagine, {len(F)} fonti, {n_frasi} frasi alla lettera, {n_cit} citazioni in pagina, {n_faq} FAQ da ricerche misurate, {n_link} link, "
          f"{n_cifre} cifre confrontate con le trascrizioni a mano, {n_js} casi dei calcolatori (app.js = conto di riferimento), {n_file} file senza chiavi.")
    print(f"Università: {len(D_uni['scelte'])} schede + indice, {n_uni} cifre e righe confrontate con il file College Scorecard ({origine_uni}); buco rifatto con due conti di riferimento; "
          f"domanda misurata {D_uni['domanda_totale_scelte']:,} ricerche al mese su {D_uni['frasi_misurate']} frasi ({n_risposte} volumi riletti dalle risposte conservate).")
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
