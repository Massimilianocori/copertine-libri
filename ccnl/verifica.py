"""Controlli del sito Paga CCNL. Esce con errore se qualcosa non va.

Uso (dalla radice del repository):
    python3 ccnl/verifica.py              # dati, cifre, pagine, link, SEO, FAQ, monetizzazione, testi
    python3 ccnl/verifica.py --browser    # + Playwright: 6 pagine a 375 e 1280 px, tema chiaro e scuro, calcolo in pagina
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
# volumi misurati (Google Ads, Italia): file più recente di raccolta/volumi.py; frasi dirette con volume, poi le «simili» non già presenti
FILE_VOLUMI = sorted(DATI.glob("volumi-*.json"))[-1]
VOL = json.loads(FILE_VOLUMI.read_text(encoding="utf-8"))
MISURE = {}
for _q, _x in VOL["frasi"].items():
    if _x.get("volume") is not None:
        MISURE[_q] = _x["volume"]
for _x in VOL["frasi"].values():
    for _s, _v in (_x.get("simili") or {}).items():
        if _v is not None and _s not in MISURE:
            MISURE[_s] = _v
MIN_VOLUME = 100
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


RE_DAL = re.compile(r'<!--dal:(\d{4}-\d{2}-\d{2})-->(.*?)<!--/dal-->', re.S)


def visibile(html):
    # i pezzi tra <!--dal:AAAA-MM-GG--> e <!--/dal--> sono nascosti (hidden) fino a quella data: non sono testo visibile oggi.
    # Li controlla a parte controlla_scatto().
    t = RE_DAL.sub(" ", html)
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S | re.I)
    return norm(unescape(re.sub(r"<[^>]+>", " ", t)))


def controlla_scatto(pagina, html, att, div_o):
    """Prossima tranche del livello: la pagina deve contenere già, nascosto fino a quel giorno, il pezzo che il browser mostra
    da solo (stile.APP_JS). Tabella nuova pubblicabile: le cifre nuove in alto e la nota «Minimo aggiornato»; non pubblicabile:
    la nota «Cifra da aggiornare». Ogni pezzo deve essere davvero nascosto oggi (attributo hidden) e avere la data giusta."""
    fut = [x for x in att if x[0] > OGGI.isoformat()]
    pezzi = RE_DAL.findall(html)
    if not fut:
        if pezzi:
            errore(f"{pagina}: pezzi a data futura senza una tranche futura")
        return
    d2, ok, t2, _ = fut[0]
    if not pezzi or any(d != d2 for d, _ in pezzi):
        errore(f"{pagina}: manca il pezzo nascosto per la tabella del {d2} (o ha un'altra data)")
        return
    for d, pezzo in pezzi:
        if not re.match(rf'<\w+ data-dal="{d}" hidden[ >]', pezzo):
            errore(f"{pagina}: il pezzo del {d} non è nascosto con data-dal e hidden")
    testo = norm(unescape(re.sub(r"<[^>]+>", " ", " ".join(p for _, p in pezzi))))
    if ok:
        for x in (euro(t2), euro(arr(t2 / div_o)), "Minimo aggiornato dal"):
            if norm(x) not in testo:
                errore(f"{pagina}: nel pezzo del {d2} manca «{x}»")
        if f'data-fino="{d2}"' not in html:
            errore(f"{pagina}: le cifre di oggi non hanno data-fino={d2}")
    else:
        if "Cifra da aggiornare" not in testo or "quello in vigore oggi è più alto" not in testo:
            errore(f"{pagina}: nel pezzo del {d2} manca la nota «Cifra da aggiornare»")
        if 'data-fino="' in html:
            errore(f"{pagina}: cifre di oggi nascoste a una data in cui non c'è una cifra nuova pubblicabile")


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


def corrente(lista, cid, L, giorno=None):
    """(riga mostrata, righe sospese): stessa regola di genera.stato_livello, rifatta qui dagli estratti.
    Se la riga in vigore non è pubblicabile ma le sue voci sono confermate, la pagina resta sull'ultima riga verificata e lo dichiara.
    giorno (AAAA-MM-GG): lo stato in un altro giorno, per i passi a data futura dello strumento dell'annuncio."""
    pas = [x for x in lista if x[0] <= (giorno or OGGI.isoformat())]
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
        controlla_scatto(pagina, html, att, div_o)
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
                atteso = "https://pagaccnl.com/" + rel.replace("index.html", "")
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
            percorso = percorso.partition("?")[0]  # i riquadri dell'annuncio passano contratto e livello allo strumento (?c=…&l=…)
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
    if "Sitemap: https://pagaccnl.com/sitemap.xml" not in rb:
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
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]


def data_lunga(d):
    d = date.fromisoformat(d)
    return f"{'1°' if d.day == 1 else d.day} {MESI[d.month - 1]} {d.year}"


def rendi_faq(testo):
    """Riempie i segnaposto della risposta con cifre rifatte qui da estratti.json (non da genera.py).
    LookupError se la risposta non deve comparire: aumento futuro che non c'è più o livello con la riga in vigore sospesa."""
    def sost(mm):
        cid, lid, campo = mm.group(1), mm.group(2), mm.group(3)
        if cid == "domestico":
            anno_dom = max(date.fromisoformat(t["dal"]).year for L_ in RIS["domestico"]["livelli"] for t in L_["tranche"])
            if OGGI.year > anno_dom:
                raise LookupError("lavoro domestico: tabella dell'anno prima")
        if cid == "domestico" and lid == "unico":
            if campo == "e":
                return euro(EST["domestico"]["A"]["unico"]["E_mensile"])
            raise KeyError(campo)
        m = C[cid]
        L = next(x for x in m["livelli"] if x["id"] == lid)
        att = atteso_livello(cid, L)
        fissa = re.fullmatch(r"mensile_(\d{4})(\d\d)(\d\d)", campo)
        if fissa:
            # cifra di una data precisa: la riga di quella data, ricalcolata e pubblicabile
            x = next((x for x in att if x[0] == "-".join(fissa.groups()) and x[1]), None)
            if x is None or cid == "domestico":
                raise KeyError(f"{cid}/{lid}: nessuna cifra pubblicabile per {campo}")
            return euro(x[2])
        cur, sosp = corrente(att, cid, L)
        if not (cur and cur[1]):
            raise KeyError(f"{cid}/{lid}: nessuna cifra pubblicabile")
        if sosp:
            raise LookupError(f"{cid}/{lid}: riga sospesa")
        dt, _, tot, a = cur
        if campo == "dal":
            return data_lunga(dt)
        if cid == "domestico":
            oraria, conv = D(a["C_oraria"]), D(a["A_mensile"])
            ind = D(a.get("A_indennita") or 0)
            val = {"oraria": oraria, "conv": conv, "mensile": conv, "ind": ind, "conv_tot": conv + ind, "annuo_conv": (conv + ind) * 13,
                   "tab_b": a.get("B_mensile"), "d_auto": a.get("D_autosuff"), "d_non": a.get("D_non_autosuff")}
            if re.fullmatch(r"p\d+", campo):
                return euro(orario52(oraria, int(campo[1:])))
        else:
            dv, mens, ore = m["divisore_orario"]["valore"], m["mensilita"]["valore"], m["ore"]["valore"]
            val = {"mensile": tot, "oraria": arr(tot / dv), "annuo": tot * mens}
            if m.get("divisore_giornaliero"):
                val["giornaliera"] = arr(tot / m["divisore_giornaliero"]["valore"])
            if re.fullmatch(r"p\d+", campo):
                return euro(prorata(tot, int(campo[1:]), ore))
            fut = [x for x in att if x[0] > OGGI.isoformat() and x[1]]
            if campo.startswith("prossimo_"):
                if not fut:
                    raise LookupError(f"{cid}/{lid}: nessun aumento futuro")
                return data_lunga(fut[0][0]) if campo == "prossimo_dal" else euro(fut[0][2])
        if val.get(campo) is None:
            raise KeyError(campo)
        return euro(val[campo])
    return re.sub(r"\{([a-z]+)/([a-z0-9_]+):([a-z0-9_]+)\}", sost, testo)


def pagina_faq(pid):
    if pid == "home":
        return SITO / "index.html"
    if pid == "colf-badanti":
        return SITO / "colf-badanti" / "index.html"
    cid, _, lid = pid.partition("/")
    if not lid:
        return SITO / C[cid]["slug"] / "index.html"
    L = next(x for x in C[cid]["livelli"] if x["id"] == lid)
    return SITO / C[cid]["slug"] / L["slug"] / "index.html"


def controlla_faq():
    sugg = {s for v in DOM["radici"].values() if isinstance(v, list) for s in v}
    pagine_valide = {"home", "colf-badanti"} | set(C) | {f"{c}/{L['id']}" for c in C for L in C[c]["livelli"]}
    testi, n_mis, n_cit, n_rese = {}, 0, 0, 0
    for x in FAQ:
        if x["ricerca"] in sugg and "volume" not in x:
            pass
        elif MISURE.get(x["ricerca"], 0) >= MIN_VOLUME and x.get("volume") == MISURE[x["ricerca"]]:
            n_mis += 1
        elif x["ricerca"] in MISURE or "volume" in x:
            errore(f"FAQ «{x['q'][:40]}»: volume dichiarato {x.get('volume')} ma nel file {FILE_VOLUMI.name} è {MISURE.get(x['ricerca'])} (minimo {MIN_VOLUME})")
        else:
            errore(f"FAQ «{x['q'][:40]}»: la ricerca «{x['ricerca']}» non è tra i suggerimenti salvati né tra le frasi misurate")
        if x["pagina"] not in pagine_valide:
            errore(f"FAQ «{x['q'][:40]}»: pagina sconosciuta {x['pagina']}")
            continue
        if "{" in x["q"]:
            errore(f"FAQ con segnaposto nella domanda: {x['q']}")
        if re.search(r"\bnett[oa] (?:è|di|sono) \d|\d+,\d\d € nett", x["a"]):
            errore(f"FAQ «{x['q'][:40]}»: la risposta sembra indicare un netto")
        for c in x.get("citazioni", []):
            n_cit += 1
            if c["fonte"] not in x["fonti"]:
                errore(f"FAQ «{x['q'][:40]}»: citazione da {c['fonte']} che non è tra le fonti della risposta")
            if c["fonte"] not in testi:
                testi[c["fonte"]] = testo_fonte(c["fonte"])
            if norm(c["frase"]) not in testi[c["fonte"]]:
                errore(f"FAQ «{x['q'][:40]}»: citazione non trovata nel testo di {c['fonte']} («{c['frase'][:50]}»)")
        # risposta rifatta da zero e cercata nella pagina (o assente se non deve comparire)
        vis = visibile(leggi_html(pagina_faq(x["pagina"])))
        try:
            atteso = norm(rendi_faq(x["a"]))
        except LookupError:
            if norm(x["q"]) in vis:
                errore(f"FAQ «{x['q'][:40]}»: in pagina ma cita un aumento passato o una cifra sospesa")
            continue
        n_rese += 1
        if norm(x["q"]) not in vis or atteso not in vis:
            errore(f"FAQ «{x['q'][:40]}»: domanda o risposta (cifre ricalcolate) assente da {x['pagina']}")
    for p in pagine_html():
        if re.search(r"\{[a-z]+/[a-z0-9_]+:[a-z0-9_]+\}", leggi_html(p)):
            errore(f"{p}: segnaposto non sostituito")
    print(f"FAQ: {len(FAQ)} domande da ricerche vere ({len(sugg)} suggerimenti salvati il {DOM['letto_il']}; {n_mis} da frasi misurate in "
          f"{FILE_VOLUMI.name}); {n_rese} risposte ricalcolate e ritrovate in pagina, {n_cit} citazioni ritrovate nei testi ufficiali")


# titoli e h1 decisi dalle frasi misurate (dati/titoli_misurati.json, scritto da genera.py)
VUOTE = {"e", "di", "del", "della", "il", "la", "per", "a"}
# lavoro domestico: «badante» solo per i livelli che assistono persone, «colf» solo per quelli che non le assistono (declaratoria dell'art. 9)
def parole(t):
    t = t.lower().replace("°", " ").replace(":", " ").replace(",", " ")
    return {w for w in re.split(r"[\s()]+", t) if w and w not in VUOTE}


def controlla_titoli_misurati():
    tm = carica("titoli_misurati.json")
    if tm.get("file_volumi") != FILE_VOLUMI.name:
        errore(f"titoli_misurati.json scritto con {tm.get('file_volumi')}, il file dei volumi più recente è {FILE_VOLUMI.name}: rigenerare")
    n = 0
    for perc, x in tm["pagine"].items():
        f = SITO / perc / "index.html"
        if not f.exists():
            errore(f"titoli_misurati.json: pagina {perc} assente")
            continue
        html = leggi_html(f)
        t = unescape(re.search(r"<title>(.*?)</title>", html).group(1))
        h1 = norm(unescape(re.sub(r"<[^>]+>", "", re.search(r"<h1>(.*?)</h1>", html, re.S).group(1))))
        if t != x["titolo"] or h1 != norm(x["h1"]):
            errore(f"{perc}: titolo o h1 diversi da titoli_misurati.json")
        if x["frase"]:
            n += 1
            if MISURE.get(x["frase"]) != x["volume"] or x["volume"] < MIN_VOLUME:
                errore(f"{perc}: frase «{x['frase']}» con volume {x['volume']}, nel file {MISURE.get(x['frase'])} (minimo {MIN_VOLUME})")
            manca = parole(x["frase"]) - parole(t)
            if manca:
                errore(f"{perc}: il titolo non contiene le parole della frase misurata «{x['frase']}» ({', '.join(sorted(manca))})")
        for cid, m in C.items():
            for L in m["livelli"]:
                if perc != f"{m['slug']}/{L['slug']}/" or cid != "domestico":
                    continue
                assiste = bool(re.search(r"\bassiste\b", L["declaratoria"]["testo"]))
                if re.match(r"badante\b", t, re.I) and not assiste:
                    errore(f"{perc}: «badante» nel titolo ma il livello non assiste persone (art. 9)")
                if re.match(r"colf\b(?! e badanti)", t, re.I) and assiste:
                    errore(f"{perc}: «colf» nel titolo ma il livello assiste persone (art. 9)")
    print(f"Titoli: {n} pagine con titolo da una frase misurata (≥ {MIN_VOLUME} ricerche al mese)")


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


# ---------------------------------------------------------------- 8 bis. annuncio di lavoro, Pro, API (prova di domanda del 27/11/2026)
# Tutto rifatto qui senza genera.py e senza genera_annuncio.py: lo stato di ogni livello a ogni data viene da estratti.json
# (atteso_livello, corrente), la riga dell'annuncio è riscritta da capo (riga_attesa) e il codice del browser si esegue con node.
P_ANN = {"strumento": "annuncio-di-lavoro/", "guida": "annuncio-di-lavoro/cosa-scrivere/", "pro": "per-consulenti-e-aziende/", "api": "api/"}
EVENTI_ANN = {"calcolo": "pagaccnl.com/clic/annuncio-calcolo", "copia": "pagaccnl.com/clic/annuncio-copia", "pro": "pagaccnl.com/clic/pro-prezzo",
              "api": "pagaccnl.com/clic/api-chiave", "api_prezzo": "pagaccnl.com/clic/api-prezzo"}
RE_PAGAMENTO = re.compile(r"stripe|paypal|gumroad|lemonsqueezy|paddle\.|checkout|satispay|sumup|shopify|klarna|nexi|buy\.|/pay\b|/acquista|/carrello", re.I)
CASI_ANNUNCIO = []


def stato_annuncio(cid, L, att, giorno):
    """Cifre che lo strumento può dare per il livello nel giorno indicato, oppure None (riga sospesa, tabella del lavoro domestico
    dell'anno prima, cifra non pubblicabile): in quei giorni lo strumento non deve dare nessuna riga."""
    cur, sosp = corrente(att, cid, L, giorno)
    if not (cur and cur[1]) or sosp:
        return None
    if cid == "domestico":
        if date.fromisoformat(giorno).year > date.fromisoformat(cur[0]).year:
            return None
        a = cur[3]
        ind = D(a["A_indennita"]) if a.get("A_indennita") else Decimal(0)
        return {"m": int((D(a["A_mensile"]) + ind) * 100), "o": int(D(a["C_oraria"]) * 100), "ind": 1 if ind else 0, "t": data_lunga(cur[0])}
    return {"m": int(arr(cur[2]) * 100), "t": data_lunga(cur[0])}


def passi_attesi(cid, L, att):
    oggi = OGGI.isoformat()
    giorni = sorted({x[0] for x in att if x[0] > oggi} | ({date(OGGI.year + 1, 1, 1).isoformat()} if cid == "domestico" else set()))
    passi = []
    for g in [""] + giorni:
        st = stato_annuncio(cid, L, att, g or oggi)
        p = dict(st, dal=g) if st else {"dal": g, "no": 1}
        if passi and {k: v for k, v in passi[-1].items() if k != "dal"} == {k: v for k, v in p.items() if k != "dal"}:
            continue
        passi.append(p)
    return passi


def riga_attesa(cid, m, L, st, modo, n, fonte, off=0):
    """La riga dell'annuncio riscritta qui: (riga completa, centesimi al mese, centesimi l'anno, riga breve).
    off: retribuzione mensile offerta in centesimi, più alta del minimo: la riga dà la fascia «da… a…»."""
    mens = m["mensilita"]["valore"]
    e = lambda c: euro(Decimal(c) / 100)  # noqa: E731
    dopo = ""
    if cid == "domestico":
        if modo == "aore":
            mese = int(orario52(Decimal(st["o"]) / 100, n) * 100)
            testa = (f"{e(st['o'])} lordi l'ora; per {n} ore settimanali {e(mese)} lordi al mese per {mens} mensilità "
                     f"({e(mese * mens)} lordi l'anno), lavoratore non convivente.")
        else:
            mese = st["m"]
            testa = f"{e(mese)} lordi al mese per {mens} mensilità ({e(mese * mens)} lordi l'anno), lavoratore convivente; vitto e alloggio a parte."
            if st["ind"]:
                dopo = ", indennità di funzione compresa"
    else:
        ore = m["ore"]["valore"]
        if modo == "ore":
            mese, coda = int(prorata(Decimal(st["m"]) / 100, n, ore) * 100), f"part time di {n} ore settimanali su {ore}"
        elif modo == "pct":
            mese, coda = int(prorata(Decimal(st["m"]) / 100, n, 100) * 100), f"part time al {n}%"
        else:
            mese, coda = st["m"], f"tempo pieno ({ore} ore settimanali)"
        if modo != "pieno":
            dopo = ", riproporzionato all'orario"
        if off:
            testa = f"da {e(mese)} a {e(off)} lordi al mese per {mens} mensilità (da {e(mese * mens)} a {e(off * mens)} lordi l'anno), {coda}."
        else:
            testa = f"{e(mese)} lordi al mese per {mens} mensilità ({e(mese * mens)} lordi l'anno), {coda}."
    nome = L["nome"][0].lower() + L["nome"][1:]
    breve = f"Retribuzione iniziale: {testa} Inquadramento: {nome}, CCNL {m['nome']}, codice CNEL {m['codice_cnel']}."
    importo = f"minimo del contratto in vigore dal {st['t']}{dopo}"
    if off:
        importo = f"fascia dal {importo} alla retribuzione offerta dall'azienda"
    testo = f"{breve} Importo: {importo}. Fonte: {fonte}; cifre controllate il {data_lunga(CONTROLLO.isoformat())}."
    return testo, mese, mese * mens, breve


def _principale(html):
    """Parole del contenuto (senza moduli, script, stili e icone), contate qui come fa il cancello della pubblicità."""
    corpo = re.search(r"<main[^>]*>(.*?)</main>", html, re.S).group(1)
    corpo = re.sub(r"<(form|script|style|svg)\b.*?</\1>", " ", corpo, flags=re.S | re.I)
    return len(re.findall(r"\w+", unescape(re.sub(r"<[^>]+>", " ", corpo))))


def _campi_modulo(html, nome):
    m_ = re.search(rf'<form\b[^>]*\bname="{nome}"[^>]*>.*?</form>', html, re.S)
    return (m_.group(0), set(re.findall(r'<(?:input|select|textarea)\b[^>]*\bname="([^"]+)"', m_.group(0)))) if m_ else (None, set())


def impronta_pagina(testo):
    """Impronta del contenuto di una pagina, rifatta qui: titolo, descrizione, JSON-LD e <main>, senza il riquadro dell'annuncio,
    senza le date di controllo e di lettura delle fonti e senza i nomi con impronta dei file in /assets/."""
    import hashlib
    date_c = {CONTROLLO.isoformat(), data_lunga(CONTROLLO.isoformat())}
    for es in list(FJ["fonti"].values()) + list(FJ["pagine"].values()):
        date_c |= {es["letto_il"], data_lunga(es["letto_il"])}
    testo = re.sub(r"<!--annuncio-->.*?<!--/annuncio-->", "", testo, flags=re.S)
    testo = re.sub(r"(Controllato il|controllate il|Letto il|Ultimo aggiornamento:) (?:1°|\d{1,2}) [a-z]+ \d{4}", r"\1 {data}", testo)
    testo = re.sub(r"(/assets/[a-z]+)\.[0-9a-f]{10}\.", r"\1.", testo)
    for d_ in sorted(date_c, key=len, reverse=True):
        testo = testo.replace(d_, "{data}")
    pezzi = [(re.search(r"<title>(.*?)</title>", testo, re.S) or [0, ""])[1], (re.search(r'<meta name="description" content="(.*?)">', testo, re.S) or [0, ""])[1]]
    pezzi += re.findall(r'<script type="application/ld\+json">(.*?)</script>', testo, re.S)
    pezzi.append((re.search(r'<main id="main">(.*?)</main>', testo, re.S) or [0, ""])[1])
    return hashlib.sha256("\n".join(pezzi).encode("utf-8")).hexdigest()[:20]


def controlla_lastmod(nuove, data_nuove):
    """Sitemap con la data vera di ogni pagina: registro dati/lastmod.json = impronta rifatta qui = data nella sitemap."""
    sm = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    voci = dict(re.findall(r"<url><loc>https://pagaccnl\.com/([^<]*)</loc><lastmod>(\d{4}-\d{2}-\d{2})</lastmod></url>", sm))
    if sm.count("<url>") != len(voci):
        errore("sitemap: una voce senza lastmod")
    for u in nuove:
        if voci.get(u, "") < data_nuove:
            errore(f"sitemap: /{u} ha lastmod {voci.get(u)}, prima della sua pubblicazione ({data_nuove})")
    for u, d_ in voci.items():
        if not "2026-11-12" <= d_ <= OGGI.isoformat():
            errore(f"sitemap: /{u} ha una data impossibile ({d_})")
        t = leggi_html(SITO / u / "index.html")
        senza = re.sub(r"<!--annuncio-->.*?<!--/annuncio-->", "", t, flags=re.S).replace(f"Controllato il {data_lunga(CONTROLLO.isoformat())}", "Controllato il 3 marzo 2031")
        if impronta_pagina(t) != impronta_pagina(senza):
            errore(f"/{u}: il riquadro dell'annuncio o la data «Controllato il» entrano nell'impronta del lastmod")
    if len(set(voci.values())) < 2:
        errore("sitemap: tutte le pagine hanno la stessa data (lastmod non per pagina)")
    if os.environ.get("CCNL_OGGI"):
        return  # prova di una data futura: genera.py non riscrive il registro
    f = DATI / "lastmod.json"
    if not f.exists():
        errore("manca dati/lastmod.json")
        return
    reg = json.loads(f.read_text(encoding="utf-8"))["pagine"]
    if set(reg) != set(voci):
        errore(f"lastmod.json: pagine diverse dalla sitemap ({sorted(set(reg) ^ set(voci))[:5]})")
    for u, (d_, imp) in reg.items():
        if voci.get(u) != d_:
            errore(f"/{u}: lastmod {voci.get(u)} nella sitemap, {d_} nel registro")
        if (SITO / u / "index.html").exists() and impronta_pagina(leggi_html(SITO / u / "index.html")) != imp:
            errore(f"/{u}: l'impronta del registro non è quella della pagina (rigenerare)")
    print(f"Lastmod: {len(voci)} pagine con la data del loro contenuto ({len(set(voci.values()))} date diverse), registro = sitemap = impronta ricalcolata")


def controlla_annuncio():
    AN = carica("annuncio.json")
    legge, fr = AN["legge"], AN["legge"]["frammenti"]
    import hashlib
    import tempfile
    # 1. testi di legge: i frammenti salvati non sono stati ritoccati
    if hashlib.sha256(json.dumps(fr, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest() != legge["impronta_frammenti"]:
        errore("annuncio.json: i frammenti di legge sono cambiati rispetto all'impronta salvata (rileggere il testo ufficiale e aggiornare l'impronta)")
    if AN["eventi"] != EVENTI_ANN:
        errore("annuncio.json: nomi degli eventi diversi da quelli della scheda")
    if AN["prezzi"] != {"pro_anno": 149, "pro_mese": 19, "api_mese": 49, "in_vendita": False}:
        errore("annuncio.json: prezzi diversi dalla scheda, oppure la vendita risulta aperta")
    html = {}
    for k, perc in P_ANN.items():
        f = SITO / perc / "index.html"
        if not f.exists():
            errore(f"annuncio: pagina /{perc} assente")
            return
        html[k] = leggi_html(f)
    sm = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    vis = {k: visibile(t) for k, t in html.items()}
    for k, perc in P_ANN.items():
        t = html[k]
        if f"<loc>https://pagaccnl.com/{perc}</loc>" not in sm or 'name="robots" content="noindex"' in t:
            errore(f"/{perc}: non è nella sitemap o è noindex")
        # cancello della pubblicità: testo vero, almeno 400 parole fuori dai moduli, e il tag di AdSense presente
        if _principale(t) < 400:
            errore(f"/{perc}: solo {_principale(t)} parole di contenuto (minimo 400)")
        if MON.SEGNO_SENZA_ADSENSE in t:
            errore(f"/{perc}: pagina segnata senza pubblicità (non passa il cancello delle 400 parole)")
        if "verifica con il tuo consulente" not in vis[k]:
            errore(f"/{perc}: manca la frase «verifica con il tuo consulente»")
    # 2. citazioni di legge: ogni citazione in pagina è un frammento salvato, parola per parola
    n_cit = 0
    for k in ("strumento", "guida"):
        for chiave, testo in re.findall(r'<blockquote class="legge" data-frammento="([^"]+)"><p>«(.*?)»</p>', html[k], re.S):
            n_cit += 1
            if chiave not in fr or norm(unescape(testo)) != norm(fr[chiave]):
                errore(f"/{P_ANN[k]}: la citazione {chiave} non è uguale al frammento salvato")
        if html[k].count("<blockquote") != len(re.findall(r'<blockquote class="legge" data-frammento="[^"]+"><p>«', html[k])):
            errore(f"/{P_ANN[k]}: citazione senza il frammento di riferimento")
    for chiave in ("art5_c1", "art5_c2", "art5_c3", "art2_c1", "art2_c2", "art2_c3", "art13_c1", "art12_c1_p1", "art6_c2_p1"):
        if f'data-frammento="{chiave}"' not in html["guida"]:
            errore(f"guida: manca la citazione {chiave}")
    if 'data-frammento="art5_c1"' not in html["strumento"]:
        errore("strumento: manca il primo comma dell'art. 5")
    for x in (legge["gazzetta"], data_lunga(legge["in_vigore_dal"]), legge["direttiva"], "esclusi lavoro domestico e lavoro intermittente, art. 2 comma 2", "non c'è una regola transitoria",
              "non c'è una soglia di dipendenti", "Tutela giudiziaria", "è una nostra lettura"):
        if norm(x) not in vis["guida"]:
            errore(f"guida: manca «{x}»")
    # nessun importo di sanzione: la guida, tolti gli esempi di riga, non contiene cifre in euro; nessuna pagina del sito accosta «sanzione» a una cifra
    senza_esempi = visibile(re.sub(r'<p\b[^>]*class="riga-es".*?</p>', " ", html["guida"], flags=re.S))
    if re.search(r"\d\s*(€|euro)", senza_esempi):
        errore("guida: una cifra in euro fuori dagli esempi di riga (nessun importo di sanzione va scritto)")
    if "non è indicato un importo di sanzione" not in vis["guida"]:
        errore("guida: manca la frase che dice che l'importo della sanzione non è nelle fonti lette")
    for p in pagine_html():
        if re.search(r"sanzion[^.]{0,160}\d[\d.,]*\s*(€|euro)|\d[\d.,]*\s*(€|euro)[^.]{0,160}sanzion", visibile(leggi_html(p)), re.I):
            errore(f"{p.relative_to(SITO)}: un importo accanto a «sanzione»")
    for f in legge["fonti"]:
        if f'href="{f["url"]}"' not in html["guida"].replace("&amp;", "&"):
            errore(f"guida: manca il link alla fonte {f['id']}")
    # 3. moduli Netlify «pro» e «api»: attributo netlify, campo trappola, campi chiesti dalla scheda, consenso
    attesi = {"pro": ("pro", {"form-name", "bot-field", "nome", "ruolo", "tipo", "volume", "piano", "email", "contratti", "consenso"}),
              "api": ("api", {"form-name", "bot-field", "nome", "azienda", "email", "uso", "richieste", "contratti", "consenso"})}
    for k, (nome, campi) in attesi.items():
        modulo, trovati = _campi_modulo(html[k], nome)
        if not modulo:
            errore(f"/{P_ANN[k]}: modulo «{nome}» assente")
            continue
        testa = modulo[:modulo.index(">")]
        if 'data-netlify="true"' not in testa or 'netlify-honeypot="bot-field"' not in testa or 'method="POST"' not in testa:
            errore(f"modulo «{nome}»: manca data-netlify, il campo trappola o il metodo POST")
        if re.search(r'\baction="(?!/)', testa):
            errore(f"modulo «{nome}»: invia i dati fuori dal sito")
        if f'<input type="hidden" name="form-name" value="{nome}">' not in modulo:
            errore(f"modulo «{nome}»: manca il campo form-name")
        if trovati != campi:
            errore(f"modulo «{nome}»: campi {sorted(trovati ^ campi)} diversi da quelli attesi")
        if not re.search(r'<input type="email" name="email" required', modulo) or not re.search(r'<input type="checkbox" name="consenso" value="si" required', modulo):
            errore(f"modulo «{nome}»: email o consenso non obbligatori")
        if re.search(r'name="(carta|iban|card|cvv|pagamento)', modulo, re.I):
            errore(f"modulo «{nome}»: chiede dati di pagamento")
    if "Avvisami all'apertura" not in visibile(_campi_modulo(html["pro"], "pro")[0] or "") or "Chiedi una chiave di prova" not in vis["api"]:
        errore("moduli: mancano «Avvisami all'apertura» o «Chiedi una chiave di prova»")
    nomi = []
    for p in pagine_html():
        nomi += re.findall(r'<form\b[^>]*\bname="([^"]+)"', leggi_html(p))
    if sorted(nomi) != ["api", "pro", "segnalazioni"]:
        errore(f"moduli del sito: {sorted(nomi)} invece di api, pro, segnalazioni (uno per pagina)")
    # 4. eventi GoatCounter
    if f'data-ev-calcolo="{EVENTI_ANN["calcolo"]}"' not in html["strumento"] or f'data-ev-copia="{EVENTI_ANN["copia"]}"' not in html["strumento"]:
        errore("strumento: mancano gli eventi del calcolo o della copia")
    if not re.search(r"goatcounter\.count\(\{path:p,title:t,event:true\}\)", html["strumento"]) or "conta(box.getAttribute('data-ev-calcolo')" not in html["strumento"] \
            or "conta(box.getAttribute('data-ev-copia')" not in html["strumento"]:
        errore("strumento: il codice non invia gli eventi a GoatCounter")
    bott = re.findall(rf'<a class="btn"[^>]*data-goatcounter-click="{re.escape(EVENTI_ANN["pro"])}"[^>]*>(.*?)</a>', html["pro"])
    if len(bott) < 2 or any(b != "Mi interessa" for b in bott):
        errore(f"Pro: i pulsanti «Mi interessa» con l'evento pro-prezzo sono {bott}")
    bott = re.findall(rf'<a class="btn"[^>]*data-goatcounter-click="{re.escape(EVENTI_ANN["api"])}"[^>]*>(.*?)</a>', html["api"])
    if bott != ["Chiedi una chiave di prova"]:
        errore(f"API: il pulsante con l'evento api-chiave è {bott}")
    if len(re.findall(rf'<a class="btn" href="/api/" data-goatcounter-click="{re.escape(EVENTI_ANN["api_prezzo"])}"', html["pro"])) != 1:
        errore("Pro: il pulsante della scheda API non ha l'evento api-prezzo")
    # due righe (breve e completa), ognuna con il suo pulsante «Copia»; il campo della retribuzione offerta
    for x in ('data-riga-breve', 'data-copia="breve"', 'data-copia="completa"', 'name="offerta"', "Riga breve per l'annuncio", "Riga completa per il fascicolo",
              "Retribuzione offerta, se più alta del minimo"):
        if x not in html["strumento"]:
            errore(f"strumento: manca «{x}»")
    for p in pagine_html():
        for ev in re.findall(r'data-(?:goatcounter-click|ev-\w+)="([^"]+)"', leggi_html(p)):
            if ev not in EVENTI_ANN.values():
                errore(f"{p.relative_to(SITO)}: evento sconosciuto {ev}")
    # 5. nessuna vendita: niente link o moduli verso sistemi di pagamento, e la pagina lo dice
    for p in pagine_html():
        for u in re.findall(r'(?:href|src|action)="([^"]+)"', leggi_html(p)):
            if RE_PAGAMENTO.search(u):
                errore(f"{p.relative_to(SITO)}: link a un sistema di pagamento o di acquisto ({u[:80]})")
    n_liv = sum(1 for cid, m in C.items() for L in m["livelli"] if (lambda c: c and c[1])(corrente(atteso_livello(cid, L), cid, L)[0]))
    for k, frasi in {"pro": ["Non è ancora in vendita", f"5 contratti e {n_liv} livelli", "misuriamo l'interesse", "149 €", "19 €", "49 €", "Nessun pagamento oggi",
                             "in valutazione"],
                     "api": ["In valutazione", "oggi non c'è un servizio a cui collegarsi", f"5 contratti, {n_liv} livelli", "49 € al mese", "Non è in vendita",
                             "chiave senza trattativa, quando il servizio esiste", "non ancora attiva"],
                     "strumento": [f"{n_liv} livelli", "Non sono in vendita"]}.items():
        for x in frasi:
            if norm(x) not in vis[k]:
                errore(f"/{P_ANN[k]}: manca «{x}»")
    for k in ("pro", "api"):
        if re.search(r"in preparazione|chiave subito", vis[k], re.I) or "(non ancora attiva)" not in unescape(re.search(r"<title>(.*?)</title>", html["api"]).group(1)):
            errore(f"/{P_ANN[k]}: il servizio va detto «in valutazione» e «non ancora attivo», senza «in preparazione» o «chiave subito»")
        if not re.search(r"\(base giuridica: il tuo consenso; dettagli e tempi nella privacy ?\)", vis[k]):
            errore(f"/{P_ANN[k]}: la casella del consenso non dice la base giuridica")
    for p in pagine_html():
        if re.search(r"https?://api\.|api\.pagaccnl", leggi_html(p)):
            errore(f"{p.relative_to(SITO)}: indirizzo di un servizio API che non esiste")
    # 6. dati dello strumento = stato di ogni livello rifatto da estratti.json, oggi e a ogni data futura
    m_ = re.search(r'<script type="application/json" id="annuncio-dati">(.*?)</script>', html["strumento"], re.S)
    js_ = re.search(r'<script id="annuncio-js">(.*?)</script>', html["strumento"], re.S)
    if not m_ or not js_:
        errore("strumento: dati o codice assenti")
        return
    dati = json.loads(m_.group(1).replace("<\\/", "</"))
    if dati.get("ctrl") != data_lunga(CONTROLLO.isoformat()):
        errore("strumento: data del controllo diversa da contratti_meta.json")
    oggi = OGGI.isoformat()
    attese_oggi = {}
    for cid, m in C.items():
        dc = dati["c"].get(cid)
        if not dc:
            errore(f"strumento: manca il contratto {cid}")
            continue
        fonte = AN["fonte_breve"][cid]
        # l'etichetta breve della fonte cita solo numeri e date che stanno nei titoli delle due fonti del contratto
        titoli = FJ["definizioni"][m["fonte_a"]]["titolo"] + " " + FJ["definizioni"][m["fonte_b"]]["titolo"]
        if set(re.findall(r"\d+", fonte)) - set(re.findall(r"\d+", titoli)):
            errore(f"annuncio.json: la fonte breve di {cid} cita numeri che non sono nei titoli delle sue due fonti")
        ore = 40 if cid == "domestico" else m["ore"]["valore"]
        if (dc["n"], dc["k"], dc["s"], dc["mens"], dc["ore"], dc["f"], bool(dc["dom"])) != \
                (m["nome"], m["codice_cnel"], m["slug"], m["mensilita"]["valore"], ore, fonte, cid == "domestico"):
            errore(f"strumento: dati del contratto {cid} diversi da contratti_meta.json")
        pubblicati = []
        for L in m["livelli"]:
            att = atteso_livello(cid, L)
            cur = corrente(att, cid, L)[0]
            if cur and cur[1]:
                pubblicati.append((L, att))
        if [x["id"] for x in dc["l"]] != [L["id"] for L, _ in pubblicati]:
            errore(f"strumento: i livelli di {cid} non sono quelli pubblicati")
            continue
        for (L, att), dl in zip(pubblicati, dc["l"]):
            passi = passi_attesi(cid, L, att)
            if dl["p"] != passi or dl["n"] != L["nome"] or dl["s"] != L["slug"] or dl["g"] != L.get("gruppo_nome", ""):
                errore(f"strumento {cid}/{L['id']}: cifre o date diverse dal ricalcolo ({dl['p']} invece di {passi})")
                continue
            for p in passi:
                g = p["dal"] or oggi
                if p.get("no"):
                    CASI_ANNUNCIO.append((cid, L["id"], "conv" if cid == "domestico" else "pieno", 0, g, "NO", 0, 0, 0, ""))
                    continue
                if cid == "domestico":
                    casi = [("conv", 0)] + [("aore", n) for n in range(1, 41)]
                    fuori = [("aore", 0), ("aore", 41), ("aore", "20.5"), ("aore", "20,5"), ("aore", ""), ("aore", "1e1")]
                else:
                    casi = [("pieno", 0)] + [("ore", n) for n in range(1, ore)] + [("pct", n) for n in range(1, 100)]
                    fuori = [("ore", 0), ("ore", ore), ("pct", 0), ("pct", 100), ("ore", "20.5"), ("ore", "20,5"), ("ore", ""), ("pct", "50.5"), ("pct", "-5")]
                for modo, n in casi:
                    testo, mese, anno, breve = riga_attesa(cid, m, L, p, modo, n, fonte)
                    CASI_ANNUNCIO.append((cid, L["id"], modo, n, g, testo, mese, anno, 0, breve))
                    if g == oggi:
                        attese_oggi[(cid, L["id"], modo, n)] = testo
                    # retribuzione offerta: più alta del minimo -> fascia; uguale -> riga normale; più bassa -> rifiutata; lavoro domestico -> non prevista
                    if cid == "domestico":
                        if n in (0, 20):
                            CASI_ANNUNCIO.append((cid, L["id"], modo, n, g, "NULL", 0, 0, mese + 100, ""))
                    elif modo == "pieno" or n in (1, 20, 24, 50, 99):
                        for off in (mese + 1, mese + 12345, 1000000):
                            t2, _, _, b2 = riga_attesa(cid, m, L, p, modo, n, fonte, off)
                            CASI_ANNUNCIO.append((cid, L["id"], modo, n, g, t2, mese, anno, off, b2))
                        CASI_ANNUNCIO.append((cid, L["id"], modo, n, g, testo, mese, anno, mese, breve))
                        CASI_ANNUNCIO.append((cid, L["id"], modo, n, g, "BASSO", mese, 0, mese - 1, ""))
                for modo, n in fuori:
                    CASI_ANNUNCIO.append((cid, L["id"], modo, n, g, "NULL", 0, 0, 0, ""))
                # la riga a tempo pieno riporta le stesse cifre che si leggono nella pagina del livello
                if g == oggi:
                    vis_l = visibile(leggi_html(SITO / m["slug"] / L["slug"] / "index.html"))
                    _, mese, anno, _ = riga_attesa(cid, m, L, p, "conv" if cid == "domestico" else "pieno", 0, fonte)
                    for x in (euro(Decimal(mese) / 100), euro(Decimal(anno) / 100)):
                        if x not in vis_l:
                            errore(f"strumento {cid}/{L['id']}: la cifra {x} della riga non è nella pagina del livello")
    # 7. JS = Python: il codice del browser, eseguito con node, dà la stessa riga e le stesse cifre in ogni caso
    app = next((SITO / "assets").glob("app.*.js")).read_text(encoding="utf-8")
    prova = ("var fs=require('fs');var window={};var document={querySelector:function(){return null},querySelectorAll:function(){return []},getElementById:function(){return null}};\n"
             + app + "\n" + js_.group(1) + "\nvar x=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));var err=0;x.casi.forEach(function(c){"
             "var r=window.PagaAnnuncio.riga(x.D,c[0],c[1],{modo:c[2],n:String(c[3]),off:c[8]},c[4]);var ok;"
             "if(c[5]==='NULL')ok=r===null;else if(c[5]==='NO')ok=!!(r&&r.no===true&&!r.testo);else if(c[5]==='BASSO')ok=!!(r&&r.basso===true&&!r.testo&&r.mensile===c[6]);"
             "else ok=!!(r&&r.testo===c[5]&&r.breve===c[9]&&r.testo.indexOf(r.breve+' Importo: ')===0&&r.mensile===c[6]&&r.annuo===c[7]);"
             "if(!ok){err++;if(err<4)console.log(JSON.stringify(c),JSON.stringify(r));}});"
             "x.soldi.forEach(function(c){var r=window.PagaAnnuncio.centesimi(c[0]);if(!(r===c[1]||(c[1]===null&&r!==r))){err++;console.log('centesimi',c[0],r);}});"
             "console.log('ANNUNCIO_ERRORI='+err);")
    # il campo «retribuzione offerta»: scritture italiane e con il punto, e scritture sbagliate (None = rifiutata)
    soldi = [("", 0), ("2000", 200000), ("2.000", 200000), ("2.000,50", 200050), ("2000,5", 200050), ("2000.50", 200050), (" 1 950 € ", 195000),
             ("1.234.567,89", 123456789), ("2000,505", None), ("duemila", None), ("-2000", None), ("2,000.50", None), ("1e3", None)]
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "prova.js").write_text(prova, encoding="utf-8")
        (Path(tmp) / "casi.json").write_text(json.dumps({"D": dati, "casi": CASI_ANNUNCIO, "soldi": soldi}, ensure_ascii=False), encoding="utf-8")
        r = subprocess.run(["node", str(Path(tmp) / "prova.js"), str(Path(tmp) / "casi.json")], capture_output=True, text=True, timeout=120)
    if "ANNUNCIO_ERRORI=0" not in r.stdout:
        errore(f"strumento: la riga del browser è diversa da quella ricalcolata: {r.stdout[-600:]} {r.stderr[-300:]}")
    # 8. esempi di riga nelle pagine: quelli visibili sono la riga di oggi, quelli nascosti la riga del giorno indicato
    n_es = 0
    per_giorno = {(c, l, mo, n, g): t for c, l, mo, n, g, t, _, _, off, _ in CASI_ANNUNCIO if not off}
    for k in ("strumento", "guida"):
        nascosti = RE_DAL.findall(html[k])
        oggi_html = RE_DAL.sub(" ", html[k])
        for giorno, pezzo in [(oggi, oggi_html)] + nascosti:
            for chiave, testo in re.findall(r'<p\b[^>]*class="riga-es"[^>]*data-esempio="([^"]+)"[^>]*><small>.*?</small>(.*?)</p>', pezzo, re.S):
                cid, lid, modo, n = chiave.split("/")
                n_es += 1
                if norm(unescape(testo)) != norm(per_giorno.get((cid, lid, modo, int(n), giorno), "")):
                    errore(f"/{P_ANN[k]}: l'esempio {chiave} del {giorno} non è la riga ricalcolata")
        if "riga-es" not in oggi_html:
            errore(f"/{P_ANN[k]}: nessun esempio di riga visibile")
    # 9. esempio dell'API: JSON vero, uguale al file, con le cifre del livello rifatte da estratti.json
    cid, lid = AN["esempio_api"]["contratto"], AN["esempio_api"]["livello"]
    m, L = C[cid], next(x for x in C[cid]["livelli"] if x["id"] == lid)
    att = atteso_livello(cid, L)
    cur = corrente(att, cid, L)[0]
    try:
        es = json.loads(unescape(re.search(r'<code id="api-esempio">(.*?)</code>', html["api"], re.S).group(1)))
        if es != json.loads((SITO / "api" / "esempio.json").read_text(encoding="utf-8")):
            errore("API: l'esempio in pagina è diverso dal file /api/esempio.json")
        tot = arr(cur[2])
        div_o, mens = m["divisore_orario"]["valore"], m["mensilita"]["valore"]
        atteso = {"in_vigore_dal": cur[0], "minimo_mensile_lordo": f"{tot:.2f}", "mensilita": mens, "minimo_annuo_lordo": f"{tot * mens:.2f}",
                  "ore_settimanali": m["ore"]["valore"], "divisore_orario": div_o, "paga_oraria_lorda": f"{arr(tot / div_o):.2f}",
                  "prossimi_minimi": [{"dal": x[0], "minimo_mensile_lordo": f"{arr(x[2]):.2f}"} for x in att if x[0] > oggi and x[1]],
                  "riga_annuncio": attese_oggi.get((cid, lid, "pieno", 0)), "controllato_il": CONTROLLO.isoformat(), "valuta": "EUR"}
        for campo, val in atteso.items():
            if es.get(campo) != val:
                errore(f"API: campo {campo} = {es.get(campo)!r}, ricalcolo {val!r}")
        if sum(D(v["importo"]) for v in es["voci"]) != tot:
            errore("API: le voci dell'esempio non sommano al minimo")
        if (es["contratto"]["nome"], es["contratto"]["codice_cnel"], es["contratto"]["id"], es["livello"]["id"], es["livello"]["nome"]) != \
                (m["nome"], m["codice_cnel"], m["slug"], L["slug"], L["nome"]):
            errore("API: contratto o livello dell'esempio diversi dai dati")
        if [f["sha256"] for f in es["fonti"]] != [FJ["fonti"][m["fonte_a"]]["sha256"], FJ["fonti"][m["fonte_b"]]["sha256"]]:
            errore("API: le fonti dell'esempio non sono le due fonti del contratto")
    except (AttributeError, ValueError, KeyError, TypeError) as e:
        errore(f"API: esempio JSON assente o non leggibile ({e})")
    # 10. riquadro «Devi scrivere la paga nell'annuncio?»: uno per pagina livello, contratto e home, con il link giusto e senza cifre
    n_riq = 0
    attesi_riq = {SITO / "index.html": "/annuncio-di-lavoro/"}
    for cid, m in C.items():
        attesi_riq[SITO / m["slug"] / "index.html"] = f"/annuncio-di-lavoro/?c={cid}"
        for d in dati["c"].get(cid, {}).get("l", []):
            attesi_riq[SITO / m["slug"] / d["s"] / "index.html"] = f"/annuncio-di-lavoro/?c={cid}&amp;l={d['id']}"
    for p in pagine_html():
        t = leggi_html(p)
        riq = re.findall(r"<!--annuncio-->(.*?)<!--/annuncio-->", t, re.S)
        if p not in attesi_riq:
            if riq:
                errore(f"{p.relative_to(SITO)}: riquadro dell'annuncio in una pagina che non deve averlo")
            continue
        if len(riq) != 1:
            errore(f"{p.relative_to(SITO)}: {len(riq)} riquadri dell'annuncio invece di 1")
            continue
        n_riq += 1
        r = riq[0]
        if f'href="{attesi_riq[p]}"' not in r or "Devi scrivere la paga nell'annuncio?" not in r:
            errore(f"{p.relative_to(SITO)}: riquadro dell'annuncio senza titolo o con il link sbagliato")
        if "<table" in r or "<h2" in r or re.search(r"\d\s*€", r):
            errore(f"{p.relative_to(SITO)}: il riquadro dell'annuncio contiene tabelle, titoli o cifre")
        if ("lavoro-domestico" in p.parts) != ("non vale" in r):
            errore(f"{p.relative_to(SITO)}: il riquadro deve dire che l'obbligo non vale solo per il lavoro domestico")
    # 11. privacy: la frase sui due moduli
    priv = leggi_html(SITO / "privacy" / "index.html")
    if 'id="lista"' not in priv or "Avvisami all'apertura" not in visibile(priv) or "Chiedi una chiave di prova" not in visibile(priv) or "non è un acquisto" not in visibile(priv) \
            or "comunque entro il 31 marzo 2027 se non apriamo" not in visibile(priv) or f"Ultimo aggiornamento: {data_lunga(max(META['controllato_il'], AN['aggiornato_il']))}" not in visibile(priv):
        errore("privacy: manca la frase sui moduli «Avvisami all'apertura» e «Chiedi una chiave di prova»")
    controlla_lastmod(set(P_ANN.values()), AN["aggiornato_il"])
    print(f"Annuncio: {len(CASI_ANNUNCIO)} righe del browser = ricalcolo (ogni livello, tempo pieno, part time in ore e in percentuale, date future); "
          f"{n_cit} citazioni di legge uguali ai frammenti; {n_es} esempi; {n_riq} riquadri; moduli pro e api; nessun link di pagamento")


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


PAGINE_BROWSER = ["/", "/terziario-commercio/4-livello/", "/lavoro-domestico/livello-cs/", "/logistica-trasporto-merci/", "/metalmeccanici-industria/livello-c2/",
                  "/colf-badanti/", "/annuncio-di-lavoro/", "/annuncio-di-lavoro/cosa-scrivere/", "/per-consulenti-e-aziende/", "/api/"]


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
                    if u == "/annuncio-di-lavoro/":
                        # strumento dell'annuncio: la riga compare solo dopo «Crea la riga» ed è quella attesa per il livello scelto
                        if pg.locator("[data-esito]").is_visible():
                            errore(f"browser {u}: la riga è visibile prima del clic")
                        pg.select_option("[data-annuncio] [name=contratto]", "metalmeccanici")
                        pg.select_option("[data-annuncio] [name=livello]", "c3")
                        pg.click("[data-crea]")
                        visto = pg.input_value("[data-riga]")
                        atteso = next((t for c, l, mo, n, g, t, _, _, off, _ in CASI_ANNUNCIO if (c, l, mo, off) == ("metalmeccanici", "c3", "pieno", 0) and g == OGGI.isoformat()), None)
                        if not atteso or visto != atteso:
                            errore(f"browser {u}: riga «{visto[:60]}…» diversa da quella attesa")
                        pg.select_option("[data-annuncio] [name=orario]", "pct")
                        if pg.locator("[data-esito]").is_visible():
                            errore(f"browser {u}: cambiando l'orario la riga vecchia resta visibile")
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
    controlla_titoli_misurati()
    controlla_date()
    controlla_testi()
    controlla_monetizzazione()
    controlla_js()
    controlla_annuncio()
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
