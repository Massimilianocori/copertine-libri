"""Controlli del sito Paga CCNL. Esce con errore se qualcosa non va.

Uso (dalla radice del repository):
    python3 ccnl/verifica.py              # dati, cifre, pagine, link, SEO, FAQ, monetizzazione, testi
    python3 ccnl/verifica.py --browser    # + Playwright: pagine campione a 375 e 1280 px, tema chiaro e scuro, calcoli in pagina
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
from fractions import Fraction as Fraction_
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
    """Impronta del contenuto di una pagina, rifatta qui: titolo, descrizione, JSON-LD e <main>, senza i riquadri di rimando (annuncio di lavoro;
    preavviso e tredicesima), senza le date di controllo e di lettura delle fonti e senza i nomi con impronta dei file in /assets/."""
    import hashlib
    date_c = {CONTROLLO.isoformat(), data_lunga(CONTROLLO.isoformat())}
    for es in list(FJ["fonti"].values()) + list(FJ["pagine"].values()):
        date_c |= {es["letto_il"], data_lunga(es["letto_il"])}
    testo = re.sub(r"<!--(annuncio|inverno)-->.*?<!--/\1-->", "", testo, flags=re.S)
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
        senza = re.sub(r"<!--(annuncio|inverno)-->.*?<!--/\1-->", "", t, flags=re.S).replace(f"Controllato il {data_lunga(CONTROLLO.isoformat())}", "Controllato il 3 marzo 2031")
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


# ---------------------------------------------------------------- 8 ter. pacchetto d'inverno: preavviso e tredicesima (27/11/2026)
# Rifatto qui senza genera.py e senza genera_inverno.py. I giorni: ogni frase di dati/inverno.json si ritrova nel testo del
# contratto salvato (nell'articolo e sotto l'intestazione giusti) e i numeri si rileggono dalla frase. Gli euro: lo stato di
# ogni livello viene da estratti.json (atteso_livello, corrente), le formule sono riscritte qui e ogni tabella in pagina si
# confronta cella per cella, oggi e alla prossima data in cui un minimo cambia. Il calcolo del browser si esegue con node.
P_PRE, P_TRE = "preavviso/", "tredicesima/"
NUMERI_IT = {"un": 1, "uno": 1, "due": 2, "tre": 3, "quattro": 4, "cinque": 5, "sei": 6, "sette": 7, "otto": 8, "dieci": 10, "quindici": 15, "venti": 20, "trenta": 30}
PREDEF_INV = {"terziario": "iv", "metalmeccanici": "c3", "multiservizi": "2", "logistica": "c3", "domestico": "cs"}
BASI_DOM = {"lic25": [("Chi convive", "m"), ("A ore, 30 ore", 30)], "dim25": [("Chi convive", "m"), ("A ore, 30 ore", 30)],
            "meno25": [("A ore, 20 ore", 20)]}
CASI_INVERNO = []


def pulisci_cit(t):
    return re.sub(r"(\w)- (\w)", r"\1\2", t).replace("ﬁ", "fi").replace("ﬂ", "fl")


def leggi_termine(frase):
    """(mesi, giorni, unità) riletti dalla frase del contratto: «mesi due e quindici giorni», «60 giorni di calendario», «sei giorni lavorativi»."""
    t = frase.lower()
    for parola, n in NUMERI_IT.items():
        t = re.sub(rf"\b{parola}\b", str(n), t)
    m_ = re.search(r"\bmes[ei] (\d+)\b|\b(\d+) mes[ei]\b", t)
    g_ = re.search(r"\bgiorni (\d+)\b|\b(\d+) giorni\b", t)
    return (int(m_.group(1) or m_.group(2)) if m_ else 0, int(g_.group(1) or g_.group(2)) if g_ else 0,
            "lav" if "lavorativ" in t else ("cal" if "calendario" in t else "gg"))


def livelli_frase(cid, m, v):
    """I livelli che la frase (o l'etichetta della colonna) nomina, riletti qui; None se la frase vale per una qualifica intera."""
    fr = v["frase"]
    if cid == "terziario":
        romani = {"Quadri": "q", "I": "i", "Il": "ii", "II": "ii", "III": "iii", "IV": "iv", "V": "v", "VI": "vi", "VII": "vii"}
        return {romani[x] for x in re.findall(r"\b(Quadri|VII|VI|IV|V|III|II|Il|I)\b", fr.split(" Livello")[0])}
    if cid == "metalmeccanici":
        return {x.lower() for x in re.findall(r"\b[A-D]\d\b", v["et"])}
    if cid == "multiservizi":
        if "operai" in fr:
            return None
        if "dal 5° al 2°" in fr:
            return {"5", "4", "3", "2"}
        return set(re.findall(r"(\d)° livello", fr)) | ({"q"} if "Quadri" in fr else set())
    if cid == "logistica":
        if "qualifica" in fr:
            q_ = re.search(r"qualifica (\d) parametri ([A-F, ]+)", fr)
            return {f"{x.lower()}{q_.group(1)}" for x in re.findall(r"[A-F]", q_.group(2))}
        if "operai" in fr:
            return None
        if "altri livelli" in fr:
            return {L["id"] for L in m["livelli"] if L.get("gruppo_nome") == "Personale non viaggiante"} - {"q", "1", "2"}
        return set(re.findall(r"(\d)° livello", fr)) | ({"q"} if "quadri" in fr else set())
    return {L["id"] for L in m["livelli"]}


def tabelle_inv(pre):
    per_id = {t["id"]: t for t in pre["tabelle"]}
    out = []
    for t in pre["tabelle"]:
        if t.get("deriva"):
            t = dict(per_id[t["deriva"]], **t)
        out.append(dict(t, num=t.get("num", 1), den=t.get("den", 1)))
    return out


def voci_inv(tab):
    return [(v.get("banda") or g["banda"], v) for g in tab["gruppi"] for v in g["voci"]]


def termine_txt(v, num=1, den=1):
    pezzi = ([("1 mese" if v["mesi"] == 1 else f"{v['mesi']} mesi")] if v["mesi"] else []) + ([f"{v['giorni']} giorni"] if v["giorni"] else [])
    t = " e ".join(pezzi) + {"lav": " lavorativi", "cal": " di calendario"}.get(v["unita"], "")
    if (num, den) != (1, 2):
        return t
    # la metà si scrive anche in numero solo quando è intera: metà di 1 mese = 15 giorni, di 2 mesi = 1 mese, di 30 giorni = 15 giorni
    tot = v["mesi"] * 30 + v["giorni"]
    if tot % 2 or v["giorni"] % 2 or v["unita"] == "lav":
        return f"la metà di {t}"
    m2, g2 = divmod(tot // 2, 30)
    chiara = " e ".join(([("1 mese" if m2 == 1 else f"{m2} mesi")] if m2 else []) + ([f"{g2} giorni"] if g2 else []))
    return f"la metà di {t} ({chiara})"


def ind_attesa(mc, v, num, den, div=30, ratei=0):
    """Indennità in centesimi, riscritta con le frazioni: mensilità del contratto, giorni lavorativi ÷ 22 o 26, mese di 30 giorni."""
    from fractions import Fraction
    if v.get("mens"):
        x = Fraction(mc) * Fraction(v["mens"])
    elif v["unita"] == "lav":
        x = Fraction(mc * v["giorni"], div)
    else:
        x = Fraction(mc * (v["mesi"] * 30 + v["giorni"]), 30)
    c = int(x * num / den + Fraction(1, 2))
    return int(Fraction(c * ratei, 12) + Fraction(1, 2)) if ratei else c


def e_cent(c):
    return euro(Decimal(c) / 100)


def celle_tabella(pezzo):
    """Righe (intestazione compresa) della prima tabella di un pezzo di HTML, come testo."""
    t = re.search(r"<table\b.*?</table>", pezzo, re.S)
    if not t:
        return None
    return [[norm(unescape(re.sub(r"<[^>]+>", " ", c))) for c in re.findall(r"<t[hd]\b[^>]*>(.*?)</t[hd]>", r, re.S)] for r in re.findall(r"<tr\b[^>]*>(.*?)</tr>", t.group(0), re.S)]


def blocchi_pagina(html):
    """({nome: pezzo} visibile oggi, {nome: (data, pezzo)} nascosto fino a una data) dei blocchi con cifre <!--b:nome-->."""
    oggi = dict(re.findall(r"<!--b:([\w-]+)-->(.*?)<!--/b-->", RE_DAL.sub(" ", html), re.S))
    dopo = {}
    for d, pezzo in RE_DAL.findall(html):
        for nome, x in re.findall(r"<!--b:([\w-]+)-->(.*?)<!--/b-->", pezzo, re.S):
            dopo[nome] = (d, x, pezzo)
    return oggi, dopo


def stato_inv(cid, L, att, giorno):
    """Minimo del livello nel giorno, in centesimi, o None (riga sospesa o non pubblicabile). Per il lavoro domestico la tabella
    dell'anno prima resta in pagina con la nota: qui non si esclude (lo fa solo il calcolo del browser, con i suoi passi)."""
    cur, sosp = corrente(att, cid, L, giorno)
    if not (cur and cur[1]) or sosp:
        return None
    if cid == "domestico":
        a = cur[3]
        ind = D(a["A_indennita"]) if a.get("A_indennita") else Decimal(0)
        o = D(a["C_oraria"])
        return {"m": int((D(a["A_mensile"]) + ind) * 100), "p": {h_: int(orario52(o, h_) * 100) for h_ in (10, 20, 25, 30, 40)}, "dal": cur[0]}
    ore = C[cid]["ore"]["valore"]
    return {"m": int(arr(cur[2]) * 100), "p": {h_: int(prorata(arr(cur[2]), h_, ore) * 100) for h_ in sorted({20, 24, 30, ore})}, "dal": cur[0]}


def controlla_inverno():
    import tempfile
    INV = carica("inverno.json")
    CI_ = INV["contratti"]
    oggi = OGGI.isoformat()
    sm = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    date_sm = dict(re.findall(r"<url><loc>https://pagaccnl\.com/([^<]*)</loc><lastmod>(\d{4}-\d{2}-\d{2})</lastmod></url>", sm))
    if set(CI_) != set(C):
        errore("inverno.json: i contratti non sono i 5 del sito")
        return
    n_frasi = n_cit = n_celle = n_euro = 0
    # ---- A. dati = testo del contratto
    for cid, m in C.items():
        pre, tre = CI_[cid]["preavviso"], CI_[cid]["tredicesima"]
        if pre["fonte"] != m["testo"]["fonte"] or tre["fonte"] != m["testo"]["fonte"]:
            errore(f"inverno {cid}: la fonte non è il testo del contratto di contratti_meta.json")
        T = testo_fonte(pre["fonte"])
        ids = {L["id"] for L in m["livelli"]}
        for t in pre["tabelle"]:
            if t.get("deriva"):
                base_ = next((x for x in pre["tabelle"] if x["id"] == t["deriva"] and not x.get("deriva")), None)
                frase = norm(pre["cit"].get(t.get("cit"), {}).get("testo", ""))
                if not base_ or (t["num"], t["den"]) != (1, 2) or not re.search(r"ridotti (rispettivamente al 50%|del 50%|della metà)", frase) or "dimissioni" != t["caso"]:
                    errore(f"inverno {cid}/{t['id']}: tabella derivata senza la frase del contratto che dimezza i termini")
                continue
            i0 = T.find(norm(t["inizio"]))
            i1 = T.find(norm(t["fine"]), i0 + 1) if i0 >= 0 else -1
            if i0 < 0 or i1 < 0 or i1 - i0 > 12000:
                errore(f"inverno {cid}/{t['id']}: articolo non trovato nel testo ({t['dove']})")
                continue
            art = T[i0:i1]
            if t.get("intestazione"):
                if norm(t["intestazione"]) not in art or norm(t["intestazione"]) != "Anni di servizio " + " ".join(v["et"] for v in t["gruppi"][0]["voci"]):
                    errore(f"inverno {cid}/{t['id']}: intestazione della tabella diversa dal testo o dalle colonne")
            pos = 0
            inizi = []
            for g in t["gruppi"]:
                pg = art.find(norm(g["frase"]), pos)
                if pg < 0:
                    errore(f"inverno {cid}/{t['id']}: intestazione «{g['frase'][:50]}» non trovata nell'articolo, nell'ordine atteso")
                    break
                inizi.append(pg)
                pos = pg + 1
            else:
                inizi.append(len(art))
                for k, g in enumerate(t["gruppi"]):
                    if g.get("pre") is not None:
                        # tabella a matrice (metalmeccanici): la riga intera è nel testo e le celle sono i suoi pezzi, nell'ordine delle colonne
                        if norm(" ".join([g["pre"]] + [v["frase"] for v in g["voci"]])) != norm(g["frase"]) or \
                                norm(" ".join([g["pre"]] + [v["frase_mens"] for v in g["voci"]])) != norm(g["frase_mens"]) or norm(g["frase_mens"]) not in art:
                            errore(f"inverno {cid}/{t['id']}: la riga «{g['pre']}» non è quella del testo")
                    p_ = inizi[k]
                    for v in g["voci"]:
                        n_frasi += 1
                        pv = art.find(norm(v["frase"]), p_)
                        if pv < 0 or pv >= inizi[k + 1]:
                            errore(f"inverno {cid}/{t['id']}: la frase «{v['frase'][:60]}» non è nel testo sotto «{g['frase'][:40]}»")
                        p_ = max(p_, pv) + (1 if g.get("pre") is None else 0)
                        if leggi_termine(v["frase"]) != (v["mesi"], v["giorni"], v["unita"]):
                            errore(f"inverno {cid}/{t['id']}: «{v['frase'][:60]}» dice {leggi_termine(v['frase'])}, il dato dice {(v['mesi'], v['giorni'], v['unita'])}")
                        if v.get("mens") is not None:
                            letto = re.fullmatch(r"(\d+(?:,\d+)?) mensilità", v["frase_mens"])
                            if not letto or Decimal(letto.group(1).replace(",", ".")) != Decimal(v["mens"]):
                                errore(f"inverno {cid}/{t['id']}: mensilità {v['mens']} diverse dalla frase «{v['frase_mens']}»")
                        att_l = livelli_frase(cid, m, v)
                        if not set(v["livelli"]) <= ids or (att_l is not None and att_l != set(v["livelli"])):
                            errore(f"inverno {cid}/{t['id']}: i livelli {v['livelli']} non sono quelli nominati dalla frase «{v['frase'][:50]}» ({sorted(att_l or [])})")
                        if (v.get("banda") or g["banda"]) not in {b["id"] for b in t["bande"]}:
                            errore(f"inverno {cid}/{t['id']}: fascia di anzianità sconosciuta")
        gruppi_cit = [("preavviso", k, c) for k, c in pre["cit"].items()] + [("tredicesima", k, c) for k, c in tre["cit"].items()] + \
                     [("tredicesima", f"14:{k}", c) for k, c in ((tre["quattordicesima"] or {}).get("cit") or {}).items()]
        T_contratto = T
        for sez, k, c in gruppi_cit:
            n_cit += 1
            T = testo_fonte(c["fonte"]) if c.get("fonte") else T_contratto
            if c.get("fonte") and c["fonte"] not in FJ["definizioni"]:
                errore(f"inverno {cid}/{sez}/{k}: fonte sconosciuta {c['fonte']}")
            if norm(c["testo"]) not in T:
                errore(f"inverno {cid}/{sez}/{k}: la citazione non è nel testo del contratto")
            num_art = re.search(r"art\. (\d+)", c["dove"])
            if num_art and cid != "metalmeccanici":
                # la frase sta dopo il titolo del suo articolo (l'indice può stare in testa o in coda al file: basta un'occorrenza)
                tit = [x.start() for x in re.finditer(rf"Art(?:icolo|\.) {num_art.group(1)} ?[-–]", T)]
                if not any(0 <= T.find(norm(c["testo"]), a) - a < 30000 for a in tit):
                    errore(f"inverno {cid}/{sez}/{k}: la citazione non sta sotto l'{c['dove']}")
        T = T_contratto
        if bool(tre["quattordicesima"]) != (m["mensilita"]["valore"] == 14):
            errore(f"inverno {cid}: quattordicesima nei dati ma {m['mensilita']['valore']} mensilità in contratti_meta.json (o il contrario)")
        r_ = pre["ratei"]
        if r_ and (r_["mensilita"] != m["mensilita"]["valore"] or not re.search(r"13a e 14a mensilità|indennità sostitutiva di preavviso", norm(pre["cit"][r_["cit"]]["testo"]))):
            errore(f"inverno {cid}: ratei nell'indennità senza la frase del contratto")
    Tt = testo_fonte(CI_["terziario"]["preavviso"]["fonte"])
    a251, a253 = Tt.find("Art. 251 - Termini di preavviso in caso di licenziamento I termini"), Tt.find("Art. 253 - Trattamento di fine rapporto In ogni caso")
    a256, a257 = Tt.find("Art. 256 - Dimissioni e preavviso In caso"), Tt.find("Art. 257 - Dimissioni per matrimonio In conformità")
    a162, a169 = Tt.find("Art. 162 - Ferie"), Tt.find("Art. 169 -")
    if not (0 <= a251 < a253 < a256 < a257 and 0 <= a162 < a169 < a162 + 20000) or re.search(r"\bferie\b", Tt[a251:a253] + Tt[a256:a257], re.I) \
            or "preavviso" in Tt[a162:a169].lower() or "ferie" in CI_["terziario"]["preavviso"]["cit"]:
        errore("inverno terziario: la pagina dice che gli artt. 251, 252, 256 e 162-168 non parlano di ferie durante il preavviso, ma il testo sì")
    if re.search(r"Articolo (20|21|57) ?-", testo_fonte("cnel_234754")):
        errore("inverno multiservizi: l'ipotesi di rinnovo del 2025 riscrive un articolo che la pagina dice non modificato")
    proc = INV["procedura"]
    f_proc = GREZZI / proc["file"]
    if f_proc.exists():
        t_proc = norm(unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)\b.*?</\1>", " ", f_proc.read_text(encoding="utf-8", errors="replace"), flags=re.S))))
        for k, x in proc["frammenti"].items():
            if norm(x) not in t_proc:
                errore(f"inverno: il frammento «{k}» non è nella pagina salvata del Ministero sulle dimissioni")
    else:
        avviso(f"inverno: manca {proc['file']} in raccolta/_grezzi (pagina del Ministero sulle dimissioni): frammenti non ricontrollati")
    # ---- B. pagine
    pagine_nuove = [P_PRE, P_TRE] + [f"{P_PRE}{m['slug']}/" for m in C.values()] + [f"{P_TRE}{m['slug']}/" for m in C.values()]
    html = {}
    for perc in pagine_nuove:
        f = SITO / perc / "index.html"
        if not f.exists():
            errore(f"inverno: pagina /{perc} assente")
            return
        t = html[perc] = leggi_html(f)
        vis_ = visibile(t)
        if perc not in date_sm or 'name="robots" content="noindex"' in t:
            errore(f"/{perc}: non è nella sitemap o è noindex")
        elif date_sm[perc] < INV["aggiornato_il"]:
            errore(f"/{perc}: lastmod {date_sm[perc]} prima della pubblicazione ({INV['aggiornato_il']})")
        if _principale(t) < 400 or MON.SEGNO_SENZA_ADSENSE in t:
            errore(f"/{perc}: non passa il cancello della pubblicità ({_principale(t)} parole di contenuto, minimo 400)")
        if "verifica con il tuo consulente" not in vis_:
            errore(f"/{perc}: manca la frase «verifica con il tuo consulente»")
        if re.search(r"\bnett[oa]\b[^.]{0,60}\d[\d.,]*\s*€|\d[\d.,]*\s*€[^.]{0,40}\bnett[oia]\b|irpef|aliquot|detrazion", vis_, re.I):
            errore(f"/{perc}: sembra dare un netto o una stima fiscale")
        if "<form" in t or re.search(r'data-(?:goatcounter-click|ev-\w+)=', t):
            errore(f"/{perc}: modulo o evento non previsto")
        # citazioni: ogni blockquote è una frase salvata, parola per parola, del contratto della pagina
        if f"Letto il {data_lunga(INV['letto_il'])}" not in vis_:
            errore(f"/{perc}: manca la data in cui abbiamo letto gli articoli citati")
        cit = re.findall(r'<blockquote class="legge" data-cit="([^"/]+)/([^"/]+)/([^"]+)"><p>«(.*?)»</p>', t, re.S)
        cit_p = re.findall(r'<blockquote class="legge" data-proc="([^"]+)"><p>«(.*?)»</p>', t, re.S)
        if cit_p and perc != P_PRE:
            errore(f"/{perc}: citazione della procedura fuori dall'indice del preavviso")
        for k, testo in cit_p:
            if norm(unescape(testo)) != norm(proc["frammenti"].get(k, "")):
                errore(f"/{perc}: la citazione «{k}» non è il frammento salvato della pagina del Ministero")
        if perc == P_PRE and ({k for k, _ in cit_p} != {"telematiche", "revoca"} or f'href="{proc["url"]}"' not in t or ("SPID o CIE" in vis_) != ("SPID o CIE" in proc["frammenti"].get("spid", ""))):
            errore(f"/{perc}: manca il paragrafo sulla procedura online delle dimissioni con la fonte")
        if t.count("<blockquote") != len(cit) + len(cit_p):
            errore(f"/{perc}: citazione senza riferimento a dati/inverno.json")
        for cid, sez, k, testo in cit:
            nodo = CI_.get(cid, {}).get(sez, {})
            c = ((nodo.get("quattordicesima") or {}).get("cit", {}).get(k[3:]) if k.startswith("14:") else nodo.get("cit", {}).get(k))
            if not c or norm(unescape(testo)) != norm(pulisci_cit(norm(c["testo"]))):
                errore(f"/{perc}: la citazione {cid}/{sez}/{k} non è uguale alla frase salvata")
            elif C[cid]["slug"] not in perc and perc != P_PRE:
                errore(f"/{perc}: citazione di un altro contratto ({cid})")
    for cid, m in C.items():
        pre, tre = CI_[cid]["preavviso"], CI_[cid]["tredicesima"]
        tt = tabelle_inv(pre)
        liv = [(L, atteso_livello(cid, L)) for L in m["livelli"]]
        pubblicati = [(L, att) for L, att in liv if (lambda c: c and c[1])(corrente(att, cid, L)[0])]
        future = sorted({x[0] for L, att in pubblicati for x in att if x[0] > oggi})
        g2 = future[0] if future and cid != "domestico" else None
        # ogni pubblicato ha come prossimo scatto la prima data futura delle sue tranche: g2 è la più vicina tra i livelli
        if cid != "domestico":
            g2 = min((min(x[0] for x in att if x[0] > oggi) for L, att in pubblicati if any(x[0] > oggi for x in att)), default=None)
        giorni = [oggi] + ([g2] if g2 else [])
        attese_euro = set()

        def pubbl(g):
            return [(L, att) for L, att in liv if (lambda c: c and c[1])(corrente(att, cid, L, g)[0])]

        # --- preavviso
        perc = f"{P_PRE}{m['slug']}/"
        t = html[perc]
        vis_ = visibile(t)
        for k in ("indennita",):
            if f'data-cit="{cid}/preavviso/{k}"' not in t:
                errore(f"/{perc}: manca la citazione dell'indennità sostitutiva")
        for tab in tt:
            # termini: la tabella sotto il titolo ha le celle riscritte qui
            pezzo = t.split(f'<h3 id="t-{tab["id"]}">', 1)
            righe = celle_tabella(pezzo[1]) if len(pezzo) == 2 else None
            ets = list(dict.fromkeys(v["et"] for _, v in voci_inv(tab)))
            att_r = [["Chi"] + [b["et"] for b in tab["bande"]]]
            for et in ets:
                att_r.append([et] + [next((termine_txt(v, tab["num"], tab["den"]) for b_, v in voci_inv(tab) if b_ == b["id"] and v["et"] == et), "—") for b in tab["bande"]])
            n_celle += sum(len(r) - 1 for r in att_r[1:])
            if righe != att_r:
                errore(f"/{perc}: tabella dei termini «{tab['titolo']}» diversa dai dati ({righe} invece di {att_r})")
            if not tab.get("deriva"):
                righe_t = re.findall(rf'<li data-riga="{cid}/{tab["id"]}/(\d+)">«(.*?)»</li>', t, re.S)
                frasi_t = ([tab["intestazione"]] + [g["frase"] for g in tab["gruppi"]] + [g["frase_mens"] for g in tab["gruppi"]]) if tab.get("intestazione") \
                    else [v["frase"] for _, v in voci_inv(tab)]
                att_t = [(str(i), norm(pulisci_cit(norm(x)))) for i, x in enumerate(frasi_t)]
                if [(i, norm(unescape(x))) for i, x in righe_t] != att_t:
                    errore(f"/{perc}: le righe del contratto sotto «{tab['titolo']}» non sono quelle salvate")
        oggi_b, dopo_b = blocchi_pagina(t)
        attesi_b = {g: {} for g in giorni}
        for g in giorni:
            st = {L["id"]: stato_inv(cid, L, att, g) for L, att in pubbl(g)}
            for tab in tt:
                bande = tab["bande"]
                basi = BASI_DOM[tab["id"]] if cid == "domestico" else [("", "m")]
                lav = any(v["unita"] == "lav" for _, v in voci_inv(tab))
                ra = pre["ratei"]["mensilita"] if pre["ratei"] else 0
                cols = [(bn, bk, b, d) for bn, bk in basi for b in bande for d in ((22, 26) if lav else (30,))]
                una = len(basi) == 1 and cid != "domestico"
                intest = ["Livello"] + (["Minimo"] if una else [])
                for bn, _, b, d in cols:
                    # intestazione corta: le parole «di servizio», «compiuti», «anni» cadono, la fascia resta la stessa
                    corta = re.sub(r" di servizio| compiuti| con la stessa famiglia", "", b["et"]).replace("Oltre 5 e fino a 10 anni", "Oltre 5, fino a 10").replace("Oltre 10 anni", "Oltre 10")
                    et = f"Giornata ÷ {d}" if lav else corta
                    intest.append(f"{bn}: {et[0].lower() + et[1:]}" if bn else et)
                righe = [intest]
                for L, att in pubbl(g):
                    if not any(L["id"] in v["livelli"] for _, v in voci_inv(tab)):
                        continue
                    s = st[L["id"]]
                    r = [L["nome"]] + ([e_cent(s["m"]) if s else "da aggiornare"] if una else [])
                    for _, bk, b, d in cols:
                        v = next((v for b_, v in voci_inv(tab) if b_ == b["id"] and L["id"] in v["livelli"]), None)
                        if not v or not s:
                            r.append("—" if not v else "da aggiornare")
                            continue
                        mc_ = s["m"] if bk == "m" else s["p"][bk]
                        r.append(e_cent(ind_attesa(mc_, v, tab["num"], tab["den"], d)) + (f" con ratei {e_cent(ind_attesa(mc_, v, tab['num'], tab['den'], d, ra))}" if ra else ""))
                    righe.append(r)
                if len(righe) > 1:
                    attesi_b[g][f"euro-{tab['id']}"] = ("tab", righe)
            es = pre["esempio"]
            tab = next(x for x in tt if x["id"] == es["tabella"])
            s = st.get(es["livello"])
            v = next((v for b_, v in voci_inv(tab) if b_ == es["banda"] and es["livello"] in v["livelli"]), None)
            if s and v:
                div = 22 if v["unita"] == "lav" else 30
                frasi = [f"= {e_cent(ind_attesa(s['m'], v, tab['num'], tab['den'], div))} lordi", e_cent(s["m"]), f"in vigore dal {data_lunga(s['dal'])}", termine_txt(v, tab["num"], tab["den"])]
                if pre["ratei"]:
                    frasi.append(f"× {pre['ratei']['mensilita']} ÷ 12 = {e_cent(ind_attesa(s['m'], v, tab['num'], tab['den'], div, pre['ratei']['mensilita']))} lordi")
                attesi_b[g]["esempio"] = ("frasi", frasi)
        n_euro += controlla_blocchi(perc, t, oggi_b, dopo_b, attesi_b, giorni, attese_euro)
        # --- tredicesima
        perc = f"{P_TRE}{m['slug']}/"
        t = html[perc]
        for k in ["quanto", "prorata", "frazioni"] + ([] if cid == "domestico" else ["parttime"]) + [f"14:{x}" for x in ((tre["quattordicesima"] or {}).get("cit") or {})]:
            if f'data-cit="{cid}/tredicesima/{k}"' not in t:
                errore(f"/{perc}: manca la citazione {k}")
        vis_ = visibile(t)
        for x in [tre["quando_breve"], f"{m['mensilita']['valore']} mensilità", "senza assenze non retribuite"] + \
                ([tre["quattordicesima"]["quando_breve"], "30 giugno", "non quello di oggi"] if tre["quattordicesima"] else ["la quattordicesima nel contratto nazionale non c'è"]):
            if norm(x) not in vis_:
                errore(f"/{perc}: manca «{x}»")
        oggi_b, dopo_b = blocchi_pagina(t)
        attesi_b = {g: {} for g in giorni}
        attese_euro = set()
        for g in giorni:
            righe = [["Livello", "Tredicesima intera (12 mesi)", "1 mese", "3 mesi", "6 mesi", "9 mesi"]]
            orari = None
            righe_o = []
            for L, att in pubbl(g):
                s = stato_inv(cid, L, att, g)
                if not s:
                    righe.append([L["nome"]] + ["da aggiornare"] * 5)
                    continue
                righe.append([L["nome"], e_cent(s["m"])] + [e_cent(int((Fraction_(s["m"] * k, 12)) + Fraction_(1, 2))) for k in (1, 3, 6, 9)])
                orari = [h_ for h_ in s["p"] if cid == "domestico" or h_ != m["ore"]["valore"]]
                righe_o.append([L["nome"]] + [e_cent(s["p"][h_]) for h_ in orari])
            attesi_b[g]["tredicesima"] = ("tab", righe)
            if righe_o:
                attesi_b[g]["orari"] = ("tab", [["Livello"] + [f"{h_} ore a settimana" for h_ in orari]] + righe_o)
            if tre["quattordicesima"]:
                # quattordicesima di luglio: il minimo che le tabelle già note danno per il prossimo 30 giugno, visto dal giorno g
                dg = date.fromisoformat(g)
                g30 = date(dg.year if dg <= date(dg.year, 6, 30) else dg.year + 1, 6, 30).isoformat()
                righe_q = [["Livello", f"Quattordicesima intera di luglio {g30[:4]}", "Tabella in vigore dal"]]
                for L, att in pubbl(g):
                    s = stato_inv(cid, L, att, g30) if (lambda c: c and c[1])(corrente(att, cid, L, g30)[0]) else None
                    righe_q.append([L["nome"], e_cent(s["m"]), data_lunga(s["dal"])] if s else [L["nome"], "da aggiornare", "—"])
                attesi_b[g]["quattordicesima"] = ("tab", righe_q)
            Lp, attp = next((L, att) for L, att in liv if L["id"] == PREDEF_INV[cid])
            s = stato_inv(cid, Lp, attp, g) if (Lp, attp) in pubbl(g) else None
            if s:
                attesi_b[g]["esempio"] = ("frasi", [f"{e_cent(s['m'])} × 7 ÷ 12 = {e_cent(int(Fraction_(s['m'] * 7, 12) + Fraction_(1, 2)))} lordi", f"in vigore dal {data_lunga(s['dal'])}"])
        if cid == "domestico":
            attese_euro.add(euro(EST["domestico"]["A"]["BS"]["F_totale"]))
            if EST["domestico"]["A"]["BS"]["F_totale"] != EST["domestico"]["B"]["BS"]["F_totale"] or euro(EST["domestico"]["A"]["BS"]["F_totale"]) + " al giorno" not in vis_:
                errore(f"/{perc}: il valore di vitto e alloggio non è quello delle due tabelle ufficiali")
        n_euro += controlla_blocchi(perc, t, oggi_b, dopo_b, attesi_b, giorni, attese_euro)
    # indici: nessuna cifra in euro fuori dal calcolo; la tabella riassuntiva nomina i 5 contratti
    if "sotto cui la tredicesima non scende" in visibile(html[P_TRE]) or "con gli stessi mesi nel suo periodo" in html[P_TRE] or "t.c.q14" not in html[P_TRE]:
        errore(f"/{P_TRE}: il calcolo presenta la quattordicesima o il minimo in modo troppo largo")
    for perc in (P_PRE, P_TRE):
        if re.search(r"\d\s*€", visibile(html[perc])):
            errore(f"/{perc}: una cifra in euro nell'indice (le cifre stanno nelle pagine dei contratti)")
        for cid, m in C.items():
            dest = f"{perc}{m['slug']}/"
            if f'href="/{dest}"' not in html[perc]:
                errore(f"/{perc}: manca il link a /{dest}")
    for cid, m in C.items():
        if norm(CI_[cid]["tredicesima"]["quando_breve"]) not in visibile(html[P_TRE]) or norm(CI_[cid]["preavviso"]["decorre_breve"]) not in visibile(html[P_PRE]):
            errore(f"indici: manca la data della tredicesima o la decorrenza del preavviso di {cid}")
    # perché «15» e «45» nel commercio: le righe elencate sono tutte e sole quelle con quel numero di giorni
    vis_i = visibile(html[P_PRE])
    for g in (15, 45):
        n_att = sum(1 for tab in tabelle_inv(CI_["terziario"]["preavviso"]) for _, v in voci_inv(tab) if v["giorni"] == g and not v["mesi"])
        m_ = re.search(rf"{g} giorni di calendario vale per: (.*?)\.", vis_i)
        if not m_ or len(m_.group(1).split(";")) != n_att:
            errore(f"/{P_PRE}: l'elenco delle righe da {g} giorni del commercio non corrisponde ai dati")
    # ---- C. calcolo della tredicesima: dati = stato rifatto da estratti.json; JS = ricalcolo per ogni livello, mese e orario
    dati_json = None
    for perc in [P_TRE] + [f"{P_TRE}{m['slug']}/" for m in C.values()]:
        m_ = re.search(r'<script type="application/json" id="tredicesima-dati">(.*?)</script>', html[perc], re.S)
        js_ = re.search(r'<script id="tredicesima-js">(.*?)</script>', html[perc], re.S)
        if not m_ or not js_ or "data-tredicesima" not in html[perc]:
            errore(f"/{perc}: calcolo della tredicesima assente")
            return
        if dati_json is None:
            dati_json, js_calc = m_.group(1), js_.group(1)
        elif (m_.group(1), js_.group(1)) != (dati_json, js_calc):
            errore(f"/{perc}: dati o codice del calcolo diversi da quelli dell'indice")
    for perc in pagine_nuove:
        if perc.startswith(P_PRE) and ("data-tredicesima" in html[perc] or "<script id=" in html[perc]):
            errore(f"/{perc}: codice del calcolo in una pagina del preavviso")
    dati = json.loads(dati_json.replace("<\\/", "</"))
    if dati.get("ordine") != list(dati["c"]) or set(dati["c"]) != set(C):
        errore("tredicesima: contratti del calcolo diversi da quelli del sito")
    for cid, m in C.items():
        dc = dati["c"][cid]
        pubblicati = [(L, att) for L in m["livelli"] for att in [atteso_livello(cid, L)] if (lambda c: c and c[1])(corrente(att, cid, L)[0])]
        if bool(dc.get("q14")) != (m["mensilita"]["valore"] == 14) or (dc.get("q14") and not dc["q14"].startswith("Quattordicesima sul minimo di oggi (")):
            errore(f"tredicesima: la riga della quattordicesima di {cid} non dice che usa il minimo di oggi")
        if (dc["b"], dc["mens"], bool(dc["dom"]), dc["u"]) != (m["nome_breve"], m["mensilita"]["valore"], cid == "domestico", f"{P_TRE}{m['slug']}/"):
            errore(f"tredicesima: dati del contratto {cid} diversi da contratti_meta.json")
        if [x["id"] for x in dc["l"]] != [L["id"] for L, _ in pubblicati]:
            errore(f"tredicesima: i livelli di {cid} non sono quelli pubblicati")
            continue
        for (L, att), dl in zip(pubblicati, dc["l"]):
            passi = passi_attesi(cid, L, att)
            if dl["p"] != passi or dl["n"] != L["nome"] or dl["g"] != L.get("gruppo_nome", ""):
                errore(f"tredicesima {cid}/{L['id']}: cifre o date del calcolo diverse dal ricalcolo")
                continue
            for p in passi:
                g = p["dal"] or oggi
                if p.get("no"):
                    CASI_INVERNO.append([cid, L["id"], g, "conv" if cid == "domestico" else "pieno", 0, "NO"])
                    continue
                if cid == "domestico":
                    casi = [("conv", 0, p["m"])] + [("aore", n, int(orario52(Decimal(p["o"]) / 100, n) * 100)) for n in range(1, 41)]
                    fuori = [("aore", 0), ("aore", 41), ("aore", "20,5"), ("aore", ""), ("pieno", 0), ("pct", 50)]
                else:
                    casi = [("pieno", 0, p["m"])] + [("pct", n, int(prorata(Decimal(p["m"]) / 100, n, 100) * 100)) for n in range(1, 100)]
                    fuori = [("pct", 0), ("pct", 100), ("pct", "50.5"), ("pct", ""), ("conv", 0), ("aore", 20)]
                for modo, n, mese in casi:
                    tred = [int(prorata(Decimal(mese) / 100, k, 12) * 100) for k in range(1, 13)]
                    if tred[11] != mese:
                        errore(f"tredicesima {cid}/{L['id']}: 12 dodicesimi non danno la mensilità")
                    CASI_INVERNO.append([cid, L["id"], g, modo, n, mese, tred, m["mensilita"]["valore"] == 14, p["t"]])
                for modo, n in fuori:
                    CASI_INVERNO.append([cid, L["id"], g, modo, n, "NULL"])
                # la tredicesima intera a tempo pieno è la cifra della pagina del livello e della tabella della pagina del contratto
                if g == oggi:
                    x = e_cent(p["m"])
                    if x not in visibile(leggi_html(SITO / m["slug"] / L["slug"] / "index.html")) or x not in visibile(html[f"{P_TRE}{m['slug']}/"]):
                        errore(f"tredicesima {cid}/{L['id']}: {x} non è nella pagina del livello o nella tabella del contratto")
    app = next((SITO / "assets").glob("app.*.js")).read_text(encoding="utf-8")
    prova = ("var fs=require('fs');var window={};var document={querySelector:function(){return null},querySelectorAll:function(){return []},getElementById:function(){return null}};\n"
             + app + "\n" + js_calc + "\nvar x=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));var err=0,n=0;var F=window.PagaTredicesima.calcola;x.casi.forEach(function(c){"
             "function bad(k,r){err++;if(err<4)console.log(JSON.stringify(c).slice(0,200),k,JSON.stringify(r));}"
             "if(c[5]==='NO'){n++;var r=F(x.D,c[0],c[1],{mesi:'12',modo:c[3],n:String(c[4])},c[2]);if(!(r&&r.no===true&&r.tred===undefined))bad(12,r);return;}"
             "if(c[5]==='NULL'){n++;var r0=F(x.D,c[0],c[1],{mesi:'6',modo:c[3],n:String(c[4])},c[2]);if(r0!==null)bad(6,r0);return;}"
             "for(var k=1;k<=12;k++){n++;var r2=F(x.D,c[0],c[1],{mesi:String(k),modo:c[3],n:String(c[4])},c[2]);"
             "if(!(r2&&r2.mensile===c[5]&&r2.tred===c[6][k-1]&&r2.rateo===c[6][0]&&r2.quatt===(c[7]?c[6][k-1]:null)&&r2.dal===c[8]&&r2.mesi===k))bad(k,r2);}"
             "['0','13','6.5','6,5','','-3','1e1'].forEach(function(k2){n++;if(F(x.D,c[0],c[1],{mesi:k2,modo:c[3],n:String(c[4])},c[2])!==null)bad(k2,'mesi');});});"
             "console.log('INVERNO_CASI='+n);console.log('INVERNO_ERRORI='+err);")
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "prova.js").write_text(prova, encoding="utf-8")
        (Path(tmp) / "casi.json").write_text(json.dumps({"D": dati, "casi": CASI_INVERNO}, ensure_ascii=False), encoding="utf-8")
        r = subprocess.run(["node", str(Path(tmp) / "prova.js"), str(Path(tmp) / "casi.json")], capture_output=True, text=True, timeout=180)
    n_js = re.search(r"INVERNO_CASI=(\d+)", r.stdout)
    if "INVERNO_ERRORI=0" not in r.stdout or not n_js:
        errore(f"tredicesima: il calcolo del browser è diverso dal ricalcolo: {r.stdout[-600:]} {r.stderr[-300:]}")
    # ---- D. riquadro «Preavviso e tredicesima»: uno per pagina livello e per pagina contratto, con i due link giusti e senza cifre
    attesi_riq = {}
    for cid, m in C.items():
        attesi_riq[SITO / m["slug"] / "index.html"] = m["slug"]
        for d in dati["c"][cid]["l"]:
            L = next(x for x in m["livelli"] if x["id"] == d["id"])
            attesi_riq[SITO / m["slug"] / L["slug"] / "index.html"] = m["slug"]
    n_riq = 0
    for p in pagine_html():
        t = leggi_html(p)
        riq = re.findall(r"<!--inverno-->(.*?)<!--/inverno-->", t, re.S)
        if p not in attesi_riq:
            if riq:
                errore(f"{p.relative_to(SITO)}: riquadro del preavviso in una pagina che non deve averlo")
            continue
        if len(riq) != 1:
            errore(f"{p.relative_to(SITO)}: {len(riq)} riquadri del preavviso invece di 1")
            continue
        n_riq += 1
        r_ = riq[0]
        if f'href="/{P_PRE}{attesi_riq[p]}/"' not in r_ or f'href="/{P_TRE}{attesi_riq[p]}/"' not in r_ or len(re.findall(r"<a ", r_)) != 2:
            errore(f"{p.relative_to(SITO)}: riquadro del preavviso con i link sbagliati")
        if "<table" in r_ or "<h2" in r_ or re.search(r"\d\s*€", r_) or re.search(r"\d+ giorni", r_):
            errore(f"{p.relative_to(SITO)}: il riquadro del preavviso contiene tabelle, titoli o cifre")
        if ("quattordicesima" in r_) != (C[next(c for c, m in C.items() if m["slug"] == attesi_riq[p])]["mensilita"]["valore"] == 14):
            errore(f"{p.relative_to(SITO)}: il riquadro nomina la quattordicesima solo dove il contratto la prevede")
        # il riquadro non entra nell'impronta del lastmod
        if impronta_pagina(t) != impronta_pagina(re.sub(r"<!--inverno-->.*?<!--/inverno-->", "", t, flags=re.S)):
            errore(f"{p.relative_to(SITO)}: il riquadro del preavviso entra nell'impronta del lastmod")
    print(f"Inverno: {n_frasi} termini di preavviso riletti dalle frasi del contratto e ritrovati nel loro articolo, {n_cit} citazioni nel testo ufficiale; "
          f"{n_celle} celle di termini e {n_euro} importi in euro ricalcolati da estratti.json (oggi e prossima data); "
          f"calcolo tredicesima: browser = ricalcolo su {n_js.group(1) if n_js else 0} casi (ogni livello, 12 mesi, part time 1-99%, colf a ore); {n_riq} riquadri")


def controlla_blocchi(perc, t, oggi_b, dopo_b, attesi_b, giorni, attese_euro):
    """Blocchi con cifre di una pagina: quello visibile è quello di oggi; se alla prossima data cambia, c'è il pezzo nascosto con
    la data giusta e le cifre di quel giorno, altrimenti non c'è. Ogni cifra in euro della pagina è tra quelle ricalcolate."""
    oggi = giorni[0]
    g2 = giorni[1] if len(giorni) > 1 else None
    n = 0

    def uguale(nome, atteso, pezzo):
        tipo, val = atteso
        if tipo == "tab":
            return celle_tabella(pezzo) == val
        v_ = norm(unescape(re.sub(r"<[^>]+>", " ", pezzo)))
        return all(norm(x) in v_ for x in val)

    def cifre(atteso):
        tipo, val = atteso
        testo = " ".join(" ".join(r) for r in val) if tipo == "tab" else " ".join(val)
        return set(re.findall(r"\d[\d.]*,\d\d €", testo))
    for nome, att in attesi_b[oggi].items():
        n += len(cifre(att))
        attese_euro |= cifre(att)
        if nome not in oggi_b or not uguale(nome, att, oggi_b[nome]):
            errore(f"/{perc}: il blocco «{nome}» di oggi non ha le cifre ricalcolate")
    if set(oggi_b) - set(attesi_b[oggi]):
        errore(f"/{perc}: blocchi con cifre non previsti {sorted(set(oggi_b) - set(attesi_b[oggi]))}")
    cambia = set()
    if g2:
        for nome in set(attesi_b[oggi]) | set(attesi_b[g2]):
            if attesi_b[oggi].get(nome) != attesi_b[g2].get(nome):
                cambia.add(nome)
        for nome in cambia:
            att = attesi_b[g2].get(nome)
            if att is None:
                continue
            n += len(cifre(att))
            attese_euro |= cifre(att)
            if nome not in dopo_b or dopo_b[nome][0] != g2 or not uguale(nome, att, dopo_b[nome][1]):
                errore(f"/{perc}: manca il blocco «{nome}» del {g2}, nascosto fino a quel giorno, con le cifre ricalcolate")
            elif not re.match(rf'<div data-dal="{g2}" hidden class="a-data">', dopo_b[nome][2]):
                errore(f"/{perc}: il blocco «{nome}» del {g2} non è nascosto con data-dal e hidden")
    if set(dopo_b) != {x for x in cambia if g2 and attesi_b[g2].get(x) is not None}:
        errore(f"/{perc}: pezzi a data futura {sorted(dopo_b)} diversi da quelli che cambiano ({sorted(cambia)})")
    n_fino = len([x for x in cambia if x in attesi_b[oggi]])
    if t.count(f'<div data-fino="{g2}" class="a-data">') != n_fino or len(re.findall(r'data-fino="', t)) != n_fino:
        errore(f"/{perc}: i blocchi di oggi che cambiano alla prossima data non sono marcati con data-fino")
    corpo = re.search(r"<main[^>]*>(.*?)</main>", t, re.S).group(1)
    corpo = re.sub(r"<(script|style)\b.*?</\1>", " ", corpo, flags=re.S)
    trovate = set(re.findall(r"\d[\d.]*,\d\d €", norm(unescape(re.sub(r"<[^>]+>", " ", corpo)))))
    if trovate - attese_euro:
        errore(f"/{perc}: cifre in euro non ricalcolate {sorted(trovate - attese_euro)[:6]}")
    return n


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
                  "/colf-badanti/", "/annuncio-di-lavoro/", "/annuncio-di-lavoro/cosa-scrivere/", "/per-consulenti-e-aziende/", "/api/",
                  "/preavviso/", "/preavviso/terziario-commercio/", "/preavviso/logistica-trasporto-merci/", "/preavviso/lavoro-domestico/", "/tredicesima/", "/tredicesima/lavoro-domestico/"]


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
                    # tabelle in euro del preavviso: devono stare nella pagina senza scorrere di lato, anche sul telefono
                    strette = pg.evaluate("Array.from(document.querySelectorAll('.t-euro .tab')).filter(e=>e.offsetParent&&e.scrollWidth>e.clientWidth+1).length")
                    if strette:
                        errore(f"browser {w}px {tema} {u}: {strette} tabelle dell'indennità scorrono di lato")
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
                    if u == "/tredicesima/":
                        # calcolo della tredicesima: metalmeccanici C3, part time al 50%, 7 mesi = cifra ricalcolata; mesi sbagliati = nessuna cifra
                        box = "[data-tredicesima] "
                        pg.select_option(box + "[name=contratto]", "metalmeccanici")
                        pg.select_option(box + "[name=livello]", "c3")
                        pg.select_option(box + "[name=orario]", "pct")
                        pg.fill(box + "[name=quanto]", "50")
                        pg.fill(box + "[name=mesi]", "7")
                        caso = next((c for c in CASI_INVERNO if c[:5] == ["metalmeccanici", "c3", OGGI.isoformat(), "pct", 50]), None)
                        visto = pg.locator("[data-out-tred]").inner_text().replace("\u00a0", " ")
                        if not caso or visto != euro(Decimal(caso[6][6]) / 100):
                            errore(f"browser {u}: tredicesima {visto} diversa da quella attesa")
                        if pg.locator("[data-quatt]").is_visible():
                            errore(f"browser {u}: quattordicesima mostrata per un contratto che non la prevede")
                        pg.select_option(box + "[name=contratto]", "terziario")
                        if not pg.locator("[data-quatt]").is_visible() or pg.locator(box + "[name=quanto]").is_visible():
                            errore(f"browser {u}: cambiando contratto il calcolo non si aggiorna")
                        pg.fill(box + "[name=mesi]", "13")
                        if pg.locator("[data-esito]").is_visible() or not pg.locator("[data-err]").is_visible():
                            errore(f"browser {u}: con 13 mesi il calcolo mostra ancora una cifra")
                    if u == "/tredicesima/lavoro-domestico/":
                        box = "[data-tredicesima] "
                        if pg.input_value(box + "[name=contratto]") != "domestico" or pg.input_value(box + "[name=livello]") != "cs":
                            errore(f"browser {u}: il calcolo non parte dal contratto della pagina")
                        pg.select_option(box + "[name=orario]", "aore")
                        pg.fill(box + "[name=quanto]", "25")
                        pg.fill(box + "[name=mesi]", "6")
                        caso = next((c for c in CASI_INVERNO if c[:5] == ["domestico", "cs", OGGI.isoformat(), "aore", 25]), None)
                        visto = pg.locator("[data-out-tred]").inner_text().replace("\u00a0", " ")
                        if not caso or visto != euro(Decimal(caso[6][5]) / 100):
                            errore(f"browser {u}: tredicesima a ore {visto} diversa da quella attesa")
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
    controlla_inverno()
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
