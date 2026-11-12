"""Controlli del sito Paga CCNL. Esce con errore se qualcosa non va.

Uso (dalla radice del repository):
    python3 ccnl/verifica.py              # dati, cifre, pagine, link, SEO, FAQ, monetizzazione, testi
    python3 ccnl/verifica.py --browser    # + Playwright: 4 pagine a 375 e 1280 px, tema chiaro e scuro, calcolo in pagina
    python3 ccnl/verifica.py --rete       # + rilegge i link esterni (documenti ufficiali)

Le cifre si ricalcolano qui senza usare genera.py: si rileggono dati/estratti.json (valori letti dalle fonti), si rifanno
somma e confronto con la seconda fonte, poi si ricalcolano paga oraria, giornaliera, annuo e part time e si cercano nelle pagine.
"""
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
GREZZI = RADICE / "raccolta" / "_grezzi"
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402

ERR, AVV = [], []
OGGI = date.fromisoformat(os.environ["CCNL_OGGI"]) if os.environ.get("CCNL_OGGI") else date.today()  # come in genera.py: prova di una data futura


def errore(m):
    ERR.append(m)


def avviso(m):
    AVV.append(m)


def carica(n):
    return json.loads((DATI / n).read_text(encoding="utf-8"))


META = carica("contratti_meta.json")
C = META["contratti"]
RIS = carica("contratti.json")["contratti"]
EST = carica("estratti.json")
FJ = carica("fonti.json")
FAQ = carica("faq.json")["faq"]
DOM = carica("domanda.json")
CONTROLLO = date.fromisoformat(META["controllato_il"])
D = lambda x: Decimal(str(x))  # noqa: E731


def arr(x):
    return D(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def euro(x):
    x = arr(x)
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def norm(t):
    t = t.replace("’", "'").replace("‘", "'").replace(" ", " ")
    return re.sub(r"\s+", " ", t).strip()


def leggi_html(p):
    return p.read_text(encoding="utf-8")


def visibile(html):
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    return norm(unescape(re.sub(r"<[^>]+>", " ", t)))


# ---------------------------------------------------------------- 1. fonti
def controlla_fonti():
    for fid, es in FJ["fonti"].items():
        if es.get("http") != 200:
            errore(f"fonte {fid}: HTTP {es.get('http')}")
        if not re.fullmatch(r"[0-9a-f]{64}", es.get("sha256", "")):
            errore(f"fonte {fid}: impronta SHA-256 mancante")
        for c, ok in es.get("trovate", {}).items():
            if not ok:
                errore(f"fonte {fid}: frase non trovata «{c[:60]}»")
        f = GREZZI / (fid + (".html" if fid == "filcams_minimi" else ".pdf"))
        if f.exists():
            import hashlib
            if hashlib.sha256(f.read_bytes()).hexdigest() != es["sha256"]:
                errore(f"fonte {fid}: il file in _grezzi non ha l'impronta registrata")
        if (OGGI - date.fromisoformat(es["letto_il"])).days > 40:
            avviso(f"fonte {fid} letta il {es['letto_il']}: rileggere (raccolta/fonti.py --rete)")
    for pid, p in FJ["pagine"].items():
        if p.get("http") != 200:
            avviso(f"pagina ufficiale {pid}: HTTP {p.get('http')}")
    mon = carica("cnel_monitor.json")
    for cod in ("H501", "H011", "C011", "K511", "I100"):
        if cod not in mon["codici"]:
            errore(f"cnel_monitor.json: manca il codice {cod}")


# ---------------------------------------------------------------- 2. regole e citazioni nei testi
def testo_fonte(fid):
    t = ""
    for f in [GREZZI / f"{fid}.txt"] + sorted((GREZZI / "ocr").glob(f"{fid}_p*.txt")):
        if f.exists():
            t += " " + f.read_text(encoding="utf-8")
    return norm(t)


def controlla_regole():
    cache = {}
    for cid, m in C.items():
        for k in ("divisore_orario", "divisore_giornaliero", "mensilita", "ore"):
            r = m.get(k)
            if not r:
                continue
            fid = r["fonte"]
            if r["frase"] not in FJ["definizioni"][fid].get("cerca", []):
                errore(f"{cid}.{k}: la frase non è tra quelle controllate in raccolta/fonti.py")
            elif not FJ["fonti"][fid]["trovate"].get(r["frase"]):
                errore(f"{cid}.{k}: frase non trovata nella fonte {fid}")
            if k in ("divisore_orario", "divisore_giornaliero") and str(r["valore"]) not in r["frase"]:
                errore(f"{cid}.{k}: il valore {r['valore']} non è nella frase citata")
            if r.get("valore_alt"):
                if str(r["valore_alt"]) not in r["frase_alt"] or not FJ["fonti"][fid]["trovate"].get(r["frase_alt"]):
                    errore(f"{cid}.{k}: divisore alternativo {r['valore_alt']} non confermato dalla sua frase")
            if k == "mensilita" and r["valore"] not in (13, 14):
                errore(f"{cid}: mensilità {r['valore']} non ammessa")
        for L in m["livelli"]:
            dec = L.get("declaratoria")
            if not dec:
                continue
            fid = dec["fonte"]
            if fid not in cache:
                cache[fid] = testo_fonte(fid)
            if norm(dec["testo"]) not in cache[fid]:
                errore(f"{cid}/{L['id']}: citazione della declaratoria non trovata nel testo di {fid}")


# ---------------------------------------------------------------- 3. cifre: rifare somma e seconda fonte da estratti.json
def atteso_livello(cid, L):
    """Ritorna la lista di (dal, pubblicabile, totale, parti) rifatta da zero."""
    out = []
    if cid == "domestico":
        a, b = EST["domestico"]["A"][L["chiave"]], EST["domestico"]["B"][L["chiave"]]
        out.append(("2026-01-01", a == b, D(a["A_mensile"]), a))
    elif cid == "terziario":
        for dt in sorted(EST["terziario"]["A"]):
            a = EST["terziario"]["A"][dt].get(L["chiave"])
            b = EST["terziario"]["B"].get(dt, {}).get(L["chiave"])
            tot = D(a["totale"])
            ok = D(a["paga_base"]) + D(a["altri_elementi"]) + D(a["contingenza_edr"]) == tot and b is not None and \
                D(b["paga_base"]) == D(a["paga_base"]) and D(b["contingenza"]) == D(a["contingenza_edr"]) and \
                D(b["altri_elementi"]) == D(a["altri_elementi"]) and D(b["totale"]) == tot + D(b["terzo_elemento"])
            out.append((dt, ok, tot, a))
    elif cid == "metalmeccanici":
        a = EST["metalmeccanici"]["A"]["2026-06-01"][L["chiave"]]
        b = EST["metalmeccanici"]["B"]["2026-06-01"][L["chiave"]]
        m = arr(D(a["annuo"]) / 12)
        out.append(("2026-06-01", m * 12 == D(a["annuo"]) and m == D(b["minimo"]), m, a))
        for dt in ("2027-06-01", "2028-06-01"):
            out.append((dt, False, D(EST["metalmeccanici"]["B"][dt][L["chiave"]]["minimo"]), None))
    elif cid == "multiservizi":
        prec = None
        for dt in sorted(EST["multiservizi"]["A"]):
            a = EST["multiservizi"]["A"][dt][L["chiave"]]
            b = EST["multiservizi"]["B"][dt][L["chiave"]]
            t, c = arr(D(a["annuo_tabellare"]) / 12), arr(D(a["annuo_contingenza"]) / 12)
            ok = t * 12 == D(a["annuo_tabellare"]) and c * 12 == D(a["annuo_contingenza"]) and b["base"] and \
                D(b["tabellare"]) == t and D(b["contingenza"]) == c and D(b["base"]) == t + c
            if prec is not None:
                ok = ok and D(b["aumento"]) == t - prec
            prec = t
            out.append((dt, bool(ok), t + c, a))
    elif cid == "logistica":
        ga = EST["logistica"]["A"][L["gruppo"]]
        gb = EST["logistica"]["B"][L.get("gruppo_b", L["gruppo"])]
        for dt in sorted(ga):
            a = ga[dt].get(L["chiave"])
            if not a:
                continue
            b = gb.get(dt, {}).get(L.get("chiave_b", L["chiave"]))
            ok = D(a["minimo"]) + D(a["epa"]) == D(a["totale"]) and b is not None and \
                arr(D(b["annuo_base"]) / 12) == D(a["minimo"]) and arr(D(b["annuo_epa"]) / 12) == D(a["epa"]) and \
                arr(D(b["annuo_base"]) / 12) * 12 == D(b["annuo_base"]) and arr(D(b["annuo_epa"]) / 12) * 12 == D(b["annuo_epa"])
            out.append((dt, ok, D(a["totale"]), a))
    return out


def voci_confermate(cid, L, dt):
    """Riga non pubblicabile le cui voci sono però uguali nelle due fonti (logistica: minimo ed EPA = annuo del Ministero diviso 12, divisione esatta)."""
    if cid == "metalmeccanici":
        return dt > "2026-06-01"  # cifre scritte solo nell'accordo: la pagina resta sull'ultimo minimo confermato dal Ministero
    if cid != "logistica":
        return False
    a = EST["logistica"]["A"][L["gruppo"]].get(dt, {}).get(L["chiave"])
    b = EST["logistica"]["B"][L.get("gruppo_b", L["gruppo"])].get(dt, {}).get(L.get("chiave_b", L["chiave"]))
    return bool(a and b) and arr(D(b["annuo_base"]) / 12) == D(a["minimo"]) and arr(D(b["annuo_epa"]) / 12) == D(a["epa"]) and \
        arr(D(b["annuo_base"]) / 12) * 12 == D(b["annuo_base"]) and arr(D(b["annuo_epa"]) / 12) * 12 == D(b["annuo_epa"])


def corrente(lista, cid, L):
    """(riga mostrata, righe sospese): stessa regola di genera.stato_livello, rifatta qui dagli estratti.
    Se la riga in vigore non è pubblicabile ma le sue voci sono confermate, la pagina resta sull'ultima riga verificata e lo dichiara."""
    pas = [x for x in lista if x[0] <= OGGI.isoformat()]
    sosp = []
    while len(pas) > 1 and not pas[-1][1] and voci_confermate(cid, L, pas[-1][0]):
        sosp.insert(0, pas.pop())
    cur = pas[-1] if pas else None
    if not (cur and cur[1]):
        sosp = []
    return cur, sosp


AVVISI_SOSPESE = []


def controlla_cifre():
    n_ok = n_tot = 0
    for cid, m in C.items():
        ris = {L["id"]: L["tranche"] for L in RIS[cid]["livelli"]}
        for L in m["livelli"]:
            att = atteso_livello(cid, L)
            tr = ris[L["id"]]
            if [x[0] for x in att] != [t["dal"] for t in tr]:
                errore(f"{cid}/{L['id']}: date diverse tra estratti e contratti.json")
                continue
            for (dt, ok, tot, _), t in zip(att, tr):
                n_tot += 1
                n_ok += ok
                if ok != t["pubblicabile"]:
                    errore(f"{cid}/{L['id']} {dt}: il ricalcolo dice pubblicabile={ok}, contratti.json {t['pubblicabile']}")
                if ok and cid != "domestico" and D(t["totale"]) != tot:
                    errore(f"{cid}/{L['id']} {dt}: totale {t['totale']} diverso dal ricalcolo {tot}")
            # pagina del livello
            cur, sosp = corrente(att, cid, L)
            pagina = SITO / m["slug"] / L["slug"] / "index.html"
            if cur and cur[1]:
                if not pagina.exists():
                    errore(f"{cid}/{L['id']}: cifra pubblicabile ma pagina assente")
                    continue
                controlla_pagina_livello(cid, m, L, att, cur, pagina)
                vis_ = visibile(leggi_html(pagina))
                if sosp:
                    AVVISI_SOSPESE.append(f"{cid}/{L['id']}")
                    if "Cifra da aggiornare" not in vis_ or "Ultimo minimo verificato" not in vis_:
                        errore(f"{cid}/{L['id']}: la riga in vigore dal {sosp[-1][0]} è sospesa ma la pagina non lo dichiara")
                    if "(in vigore)" in vis_ or "Minimo in vigore dal" in vis_ or "FAQPage" in leggi_html(pagina):
                        errore(f"{cid}/{L['id']}: pagina con riga sospesa che presenta ancora la cifra come in vigore (testo o FAQ)")
                    if cid == "logistica" and euro(sosp[-1][2]) not in vis_:
                        errore(f"{cid}/{L['id']}: la nota non riporta il totale stampato della riga sospesa")
                elif "Cifra da aggiornare" in vis_ or "Ultimo minimo verificato" in vis_:
                    errore(f"{cid}/{L['id']}: nota di cifra sospesa senza motivo")
            elif pagina.exists():
                errore(f"{cid}/{L['id']}: pagina pubblicata con una cifra che non passa i controlli")
    print(f"Cifre: {n_ok} righe pubblicabili su {n_tot} ricalcolate da zero")
    if AVVISI_SOSPESE:
        avviso(f"{len(AVVISI_SOSPESE)} pagine mostrano l'ultimo minimo verificato con la nota «Cifra da aggiornare» (riga in vigore non pubblicabile): "
               + ", ".join(AVVISI_SOSPESE))
    # correzioni della lettura ottica: ognuna con pagina, valore letto e valore corretto
    for x in carica("correzioni_ocr.json")["correzioni"]:
        if not (x.get("letto_ocr") and x.get("valore") and x.get("motivo")):
            errore(f"correzione incompleta: {x}")


def prorata(mensile, ore, norm_):
    c = int(arr(mensile) * 100)
    return Decimal((2 * c * ore + norm_) // (2 * norm_)) / 100


def orario52(oraria, ore):
    c = int(arr(oraria) * 100)
    return Decimal((2 * c * ore * 52 + 12) // 24) / 100


CASI_JS = []


def controlla_pagina_livello(cid, m, L, att, cur, pagina):
    html = leggi_html(pagina)
    vis = visibile(html)
    dt, _, tot, a = cur
    attese = []
    if cid == "domestico":
        oraria, conv = D(a["C_oraria"]), D(a["A_mensile"])
        ind = D(a["A_indennita"]) if a.get("A_indennita") else Decimal(0)
        attese += [euro(oraria), euro(conv), euro((conv + ind) * 13), euro(arr((conv + ind) / 26))]
        for o in (10, 20, 25, 30, 40):
            attese.append(euro(orario52(oraria, o)))
        m_ = re.search(r'data-cent="(\d+)" data-ore-normali="40" data-mensilita="13"', html)
        if not m_ or int(m_.group(1)) != int(oraria * 100):
            errore(f"{pagina}: attributi del calcolo diversi dalla paga oraria")
        CASI_JS.append(("orario52", int(oraria * 100), 40, [(o, int(orario52(oraria, o) * 100)) for o in (1, 7, 13, 20, 33, 40)]))
    else:
        div_o = m["divisore_orario"]["valore"]
        mens = m["mensilita"]["valore"]
        ore = m["ore"]["valore"]
        attese += [euro(tot), euro(arr(tot / div_o)), euro(tot * mens), f"÷ {div_o}"]
        if m.get("divisore_giornaliero"):
            attese.append(euro(arr(tot / m["divisore_giornaliero"]["valore"])))
            if m["divisore_giornaliero"].get("valore_alt"):
                attese.append(euro(arr(tot / m["divisore_giornaliero"]["valore_alt"])))
        for o in sorted({20, 24, 30, ore}):
            attese.append(euro(prorata(tot, o, ore)))
            attese.append(euro(prorata(tot, o, ore) * mens))
        m_ = re.search(r'data-cent="(\d+)" data-ore-normali="(\d+)" data-mensilita="(\d+)"', html)
        if not m_ or (int(m_.group(1)), int(m_.group(2)), int(m_.group(3))) != (int(tot * 100), ore, mens):
            errore(f"{pagina}: attributi del calcolo diversi dai dati")
        CASI_JS.append(("prorata", int(tot * 100), ore, [(o, int(prorata(tot, o, ore) * 100)) for o in range(1, ore + 1)]))
        # aumenti futuri pubblicabili
        for (d2, ok, t2, _) in att:
            if d2 > OGGI.isoformat() and ok and euro(t2) not in vis:
                errore(f"{pagina}: manca il minimo futuro {euro(t2)} dal {d2}")
            if not ok and euro(t2) in vis and cid == "metalmeccanici":
                errore(f"{pagina}: pubblicato un minimo non verificato ({euro(t2)})")
    for x in attese:
        if x not in vis:
            errore(f"{pagina.relative_to(SITO)}: cifra attesa assente «{x}»")
    if "Controllato il" not in vis:
        errore(f"{pagina}: manca «Controllato il»")


# ---------------------------------------------------------------- 4. pagine, SEO, link
def pagine_html():
    return sorted(SITO.rglob("*.html"))


def controlla_pagine():
    titoli, descr, canon = {}, {}, set()
    pagine = pagine_html()
    file_esistenti = {str(p.relative_to(SITO)) for p in SITO.rglob("*") if p.is_file()}
    for p in pagine:
        rel = str(p.relative_to(SITO))
        if re.fullmatch(r"google[0-9a-f]+\.html", p.name):
            continue
        html = leggi_html(p)
        t = re.search(r"<title>(.*?)</title>", html)
        dsc = re.search(r'<meta name="description" content="([^"]*)"', html)
        if not t or not dsc:
            errore(f"{rel}: titolo o descrizione assenti")
            continue
        tt, dd = unescape(t.group(1)), unescape(dsc.group(1))
        noindex = 'name="robots" content="noindex"' in html
        if not noindex:
            if len(tt) > 65:
                errore(f"{rel}: titolo di {len(tt)} caratteri (max 65)")
            if not 70 <= len(dd) <= 160:
                errore(f"{rel}: descrizione di {len(dd)} caratteri (70-160)")
            if tt in titoli:
                errore(f"{rel}: titolo uguale a {titoli[tt]}")
            if dd in descr:
                errore(f"{rel}: descrizione uguale a {descr[dd]}")
            titoli[tt], descr[dd] = rel, rel
            c = re.search(r'<link rel="canonical" href="([^"]+)"', html)
            if not c:
                errore(f"{rel}: canonical assente")
            else:
                atteso = "https://paga-ccnl.netlify.app/" + rel.replace("index.html", "")
                if c.group(1) != atteso:
                    errore(f"{rel}: canonical {c.group(1)} invece di {atteso}")
                canon.add(c.group(1))
        if html.count("<h1") != 1:
            errore(f"{rel}: {html.count('<h1')} h1")
        if 'data-goatcounter="https://rete-siti.goatcounter.com/count"' not in html:
            errore(f"{rel}: manca il contatore GoatCounter")
        if '<html lang="it">' not in html:
            errore(f"{rel}: lingua della pagina non italiana")
        # link interni e ancore
        ids = set(re.findall(r'\bid="([^"]+)"', html))
        for href in re.findall(r'href="([^"]+)"', html):
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            if href.startswith("#"):
                if href[1:] and href[1:] not in ids:
                    errore(f"{rel}: ancora {href} inesistente")
                continue
            percorso, _, ancora = href.partition("#")
            if not percorso.startswith("/"):
                errore(f"{rel}: link relativo {href}")
                continue
            dest = percorso.lstrip("/")
            if dest == "" or dest.endswith("/"):
                dest += "index.html"
            if dest not in file_esistenti:
                errore(f"{rel}: link interno rotto {href}")
            elif ancora:
                if f'id="{ancora}"' not in leggi_html(SITO / dest):
                    errore(f"{rel}: ancora {href} inesistente")
        for src in re.findall(r'(?:src|href)="(/assets/[^"#]+)"', html):
            if src.lstrip("/") not in file_esistenti:
                errore(f"{rel}: risorsa assente {src}")
        # FAQ visibili = JSON-LD
        for blocco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
            ld = json.loads(blocco)
            if ld.get("@type") == "FAQPage":
                vis = visibile(html)
                for q in ld["mainEntity"]:
                    if norm(q["name"]) not in vis or norm(q["acceptedAnswer"]["text"]) not in vis:
                        errore(f"{rel}: FAQ JSON-LD diversa dal testo visibile ({q['name'][:40]})")
    sm = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    locs = set(re.findall(r"<loc>([^<]+)</loc>", sm))
    if locs != canon:
        errore(f"sitemap diversa dai canonical: {sorted(locs ^ canon)[:5]}")
    print(f"Pagine: {len(pagine)} file HTML, {len(canon)} indicizzabili, titoli e descrizioni unici")
    # file accessori
    rb = (SITO / "robots.txt").read_text(encoding="utf-8")
    if "Sitemap: https://paga-ccnl.netlify.app/sitemap.xml" not in rb:
        errore("robots.txt senza sitemap")
    chiave = "b5a26a844a465f58552debee2c8a0114"
    if (SITO / f"{chiave}.txt").read_text(encoding="utf-8") != chiave:
        errore("file chiave IndexNow assente o diverso")
    if 'ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."' not in (SITO / "netlify.toml").read_text(encoding="utf-8"):
        errore("netlify.toml senza la regola che evita pubblicazioni inutili")
    for f in ("assets/og.png", "404.html"):
        if not (SITO / f).exists():
            errore(f"manca {f}")
    # numero di pagine per contratto
    for cid, m in C.items():
        n = len([p for p in (SITO / m["slug"]).iterdir() if p.is_dir()])
        print(f"  {m['nome_breve']}: {n} pagine livello")


# ---------------------------------------------------------------- 5. FAQ e domanda
def controlla_faq():
    sugg = {s for v in DOM["radici"].values() if isinstance(v, list) for s in v}
    pagine_valide = {"home", "colf-badanti"} | set(C) | {f"{c}/{L['id']}" for c in C for L in C[c]["livelli"]}
    for x in FAQ:
        if x["ricerca"] not in sugg:
            errore(f"FAQ «{x['q'][:40]}»: la ricerca «{x['ricerca']}» non è tra i suggerimenti salvati")
        if x["pagina"] not in pagine_valide:
            errore(f"FAQ «{x['q'][:40]}»: pagina sconosciuta {x['pagina']}")
        if "{" in x["q"]:
            errore(f"FAQ con segnaposto nella domanda: {x['q']}")
    for p in pagine_html():
        if re.search(r"\{[a-z]+/[a-z0-9_]+:[a-z0-9_]+\}", leggi_html(p)):
            errore(f"{p}: segnaposto non sostituito")
    print(f"FAQ: {len(FAQ)} domande, tutte da ricerche vere ({len(sugg)} suggerimenti salvati il {DOM['letto_il']})")


# ---------------------------------------------------------------- 6. date
def controlla_date():
    if (OGGI - CONTROLLO).days > 45:
        avviso(f"controllato_il {CONTROLLO}: più di 45 giorni, rifare il giro mensile (NOTE.md)")
    anno_dom = max(date.fromisoformat(t["dal"]).year for L in RIS["domestico"]["livelli"] for t in L["tranche"])
    if OGGI.year > anno_dom:
        avviso(f"lavoro domestico: manca la tabella del {OGGI.year}; le pagine devono dichiararlo")
        for p in [SITO / "index.html", SITO / "colf-badanti" / "index.html"] + sorted((SITO / C["domestico"]["slug"]).rglob("index.html")):
            if f"Tabella {anno_dom}." not in visibile(leggi_html(p)) or "in vigore dal 1° gennaio" in visibile(leggi_html(p)):
                errore(f"{p.relative_to(SITO)}: la tabella del lavoro domestico è dell'anno prima ma la pagina non lo dichiara")
    for cid in RIS:
        for L in RIS[cid]["livelli"]:
            for t in L["tranche"]:
                date.fromisoformat(t["dal"])
    for cid, m in C.items():
        if date.fromisoformat(m["testo"]["scadenza"]) < OGGI:
            avviso(f"{cid}: contratto scaduto il {m['testo']['scadenza']} (resta in vigore fino al rinnovo; controllare i depositi CNEL)")


# ---------------------------------------------------------------- 7. testi: niente nomi di modelli, niente dati personali
VIETATE = re.compile(r"\b(claude|anthropic|openai|chatgpt|gpt-?\d|gemini|llama|mistral|copilot|opus|sonnet|haiku)\b", re.I)
TITOLARE = "Titolare del trattamento è Massimiliano Cori (Italia)"
PERSONALI = re.compile(r"massimiliano|\bcori\b|@gmail|@outlook|@libero", re.I)


def controlla_testi():
    files = [p for p in RADICE.rglob("*") if p.is_file() and "_grezzi" not in p.parts and "cache" not in p.parts and "__pycache__" not in p.parts
             and p.suffix in (".py", ".json", ".html", ".md", ".css", ".js", ".txt", ".xml", ".toml")]
    for p in files:
        t = p.read_text(encoding="utf-8", errors="replace")
        if p.name == "verifica.py":
            continue
        if VIETATE.search(t):
            errore(f"{p.relative_to(RADICE)}: nome di un modello o servizio di IA ({VIETATE.search(t).group(0)})")
        if p.name == "genera.py" or p.relative_to(RADICE).as_posix() == "sito/privacy/index.html":
            # convenzione della rete: la privacy nomina il titolare del trattamento, una volta sola e solo lì
            if t.count(TITOLARE) != 1:
                errore(f"{p.relative_to(RADICE)}: la frase sul titolare del trattamento deve comparire una volta")
            t = t.replace(TITOLARE, "")
        if PERSONALI.search(t) and p.name != "NOTE.md":
            errore(f"{p.relative_to(RADICE)}: possibile dato personale ({PERSONALI.search(t).group(0)})")
    note = RADICE / "NOTE.md"
    if note.exists() and re.search(r"@\w+\.\w+", note.read_text(encoding="utf-8")):
        errore("NOTE.md: indirizzo email")
    for p in pagine_html():
        v = visibile(leggi_html(p))
        if re.search(r"\bnetto (?:è|di) \d", v):
            errore(f"{p}: sembra indicare un netto")


# ---------------------------------------------------------------- 8. monetizzazione e motore JS
def controlla_monetizzazione():
    e, info = MON.controlla_sito("ccnl", SITO)
    for x in e:
        errore("monetizzazione: " + x)
    senza = sum(1 for p in pagine_html() if MON.SEGNO_SENZA_ADSENSE in leggi_html(p))
    print(MON.riepilogo("ccnl", info, e) + f"; pagine senza pubblicità (noindex o poco testo): {senza}")


def controlla_js():
    js = next((SITO / "assets").glob("app.*.js")).read_text(encoding="utf-8")
    prova = ("var window={};var document={querySelector:function(){return null},querySelectorAll:function(){return []}};"
             + js + "\nvar casi=" + json.dumps(CASI_JS) + ";var err=0;casi.forEach(function(c){c[3].forEach(function(x){"
             "var r=c[0]==='orario52'?window.PagaCCNL.orario52(c[1],x[0]):window.PagaCCNL.prorata(c[1],x[0],c[2]);if(r!==x[1]){err++;console.log(c[0],c[1],x[0],r,x[1]);}});});"
             "console.log('JS_ERRORI='+err);")
    r = subprocess.run(["node", "-e", prova], capture_output=True, text=True, timeout=60)
    if "JS_ERRORI=0" not in r.stdout:
        errore(f"calcolo del browser diverso dal Python: {r.stdout[-400:]} {r.stderr[-400:]}")
    else:
        print(f"JS: calcolo del browser = Python su {sum(len(c[3]) for c in CASI_JS)} casi")


# ---------------------------------------------------------------- 9. rete e browser
def controlla_rete():
    urls = set()
    for p in pagine_html():
        urls |= set(re.findall(r'href="(https://[^"]+)"', leggi_html(p)))
    for u in sorted(urls):
        if "goatcounter" in u:
            continue
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (compatible; ccnl-check/1.0)"}, method="GET")
            with urllib.request.urlopen(req, timeout=60) as r:
                if r.status != 200:
                    avviso(f"link esterno {u}: HTTP {r.status}")
        except Exception as e:  # noqa: BLE001
            avviso(f"link esterno {u}: {str(e)[:80]}")
    print(f"Rete: {len(urls)} link esterni riletti")


PAGINE_BROWSER = ["/", "/terziario-commercio/4-livello/", "/lavoro-domestico/livello-cs/", "/logistica-trasporto-merci/"]


def controlla_browser():
    import mimetypes
    from playwright.sync_api import sync_playwright
    shot = RADICE / "cache" / "screenshot"
    shot.mkdir(parents=True, exist_ok=True)

    def servi(route):
        url = route.request.url
        if not url.startswith("http://sito.test/"):
            return route.abort()  # niente richieste esterne: solo i file del sito
        p = url[len("http://sito.test"):].split("?")[0].split("#")[0]
        if p.endswith("/"):
            p += "index.html"
        f = SITO / p.lstrip("/")
        stato = 200
        if not f.is_file():
            f, stato = SITO / "404.html", 404
        route.fulfill(status=stato, body=f.read_bytes(), content_type=mimetypes.guess_type(str(f))[0] or "text/html")

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for w in (375, 1280):
            for tema in ("light", "dark"):
                ctx = b.new_context(viewport={"width": w, "height": 900}, color_scheme=tema)
                pg = ctx.new_page()
                errori_js = []
                pg.on("pageerror", lambda e: errori_js.append(str(e)))
                pg.route("**/*", servi)
                for u in PAGINE_BROWSER:
                    pg.goto("http://sito.test" + u)
                    pg.wait_for_load_state("load")
                    largo = pg.evaluate("document.documentElement.scrollWidth")
                    if largo > w + 1:
                        errore(f"browser {w}px {tema} {u}: scorrimento orizzontale ({largo}px)")
                    piccoli = pg.evaluate("""Array.from(document.querySelectorAll('main p, main li, main td, main span')).filter(e=>e.offsetParent&&e.textContent.trim()&&parseFloat(getComputedStyle(e).fontSize)<11).length""")
                    if piccoli:
                        errore(f"browser {w}px {tema} {u}: {piccoli} testi sotto 11px")
                    sfondo = pg.evaluate("getComputedStyle(document.body).backgroundColor")
                    scuro = sfondo in ("rgb(12, 18, 27)",)
                    if (tema == "dark") != scuro:
                        errore(f"browser {w}px {tema} {u}: sfondo {sfondo} non coerente con il tema")
                    if pg.locator("[data-calc]").count():
                        box = pg.locator("[data-calc]").first
                        modo = box.get_attribute("data-modo")
                        c = int(box.get_attribute("data-cent"))
                        on = int(box.get_attribute("data-ore-normali"))
                        box.locator("input[name=ore]").fill("24")
                        atteso = euro(orario52(Decimal(c) / 100, 24) if modo == "orario52" else prorata(Decimal(c) / 100, 24, on))
                        visto = box.locator("[data-out]").inner_text().replace(" ", " ")
                        if visto != atteso:
                            errore(f"browser {u}: calcolo a 24 ore {visto} invece di {atteso}")
                        box.locator(".chips button").first.click()
                        if box.locator(".chips button").first.get_attribute("aria-pressed") != "true":
                            errore(f"browser {u}: il pulsante delle ore non si attiva")
                    if u == "/":
                        pg.fill("[data-cerca]", "commercio 4 livello")
                        vis = pg.locator("[data-riga]:visible").count()
                        if vis != 1:
                            errore(f"browser: la ricerca «commercio 4 livello» mostra {vis} righe invece di 1")
                        pg.fill("[data-cerca]", "badante cs")
                        if pg.locator("[data-riga]:visible").count() < 1:
                            errore("browser: la ricerca «badante cs» non trova righe")
                        pg.fill("[data-cerca]", "")
                    nome = (u.strip("/").replace("/", "_") or "home")
                    pg.screenshot(path=str(shot / f"{nome}_{w}_{tema}.png"), full_page=True)
                # pulsante del tema
                pg.goto("http://sito.test/")
                prima = pg.evaluate("getComputedStyle(document.body).backgroundColor")
                pg.click("[data-tema]")
                dopo = pg.evaluate("getComputedStyle(document.body).backgroundColor")
                if prima == dopo:
                    errore(f"browser {w}px {tema}: il pulsante del tema non cambia lo sfondo")
                if errori_js:
                    errore(f"browser {w}px {tema}: errori JS {errori_js[:3]}")
                ctx.close()
        b.close()
    print(f"Browser: {len(PAGINE_BROWSER)} pagine × 375/1280 px × chiaro/scuro, screenshot in {shot}")


def main():
    controlla_fonti()
    controlla_regole()
    controlla_cifre()
    controlla_pagine()
    controlla_faq()
    controlla_date()
    controlla_testi()
    controlla_monetizzazione()
    controlla_js()
    if "--rete" in sys.argv:
        controlla_rete()
    if "--browser" in sys.argv:
        controlla_browser()
    for a in AVV:
        print("AVVISO:", a)
    for e in ERR:
        print("ERRORE:", e)
    print(f"\n{len(ERR)} errori, {len(AVV)} avvisi")
    sys.exit(1 if ERR else 0)


if __name__ == "__main__":
    main()
