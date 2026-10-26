"""Genera il sito statico Tourist Tax Calculator in touristtax/sito/ da touristtax/dati/.

Uso (dalla radice del repository):
    python3 touristtax/genera.py

Dati:
    dati/destinazioni.json  una voce per destinazione, con tariffe, regole e fonti ufficiali (URL + data del controllo)
    dati/francia.json       tariffe 2026 di tutte le comuni francesi (raccolta/francia.py, dataset DGFiP DELTA)
    dati/francia_top.json   le 150 comuni con pagina propria (criterio INSEE, vedi raccolta/francia.py)
    dati/affiliati.json     riquadro affiliati (vuoto finché non ci sono URL)

Il calcolatore gira nel browser (JS in pagina, nessuno script esterno). La stessa logica è scritta qui in Python
(calcola) per gli esempi statici e per i controlli di verifica.py, che confronta Python e JS.
"""
import json
import math
import re
import shutil
import sys
import unicodedata
from datetime import date, timedelta
from html import escape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
URL_SITO = "https://tourist-tax-calculator.netlify.app"  # unico punto da cambiare se il nome del sito su Netlify è diverso
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console, aggiunto il 10/10/2026: non rimuoverlo

ALTRI_SITI = [  # blocco "Other useful tools for your trip" in fondo a ogni pagina (URL dai genera.py dei rispettivi siti)
    ("https://italy-strikes-today.netlify.app/", "Italy Strikes Today", "Transport strikes in Italy today and tomorrow, from the official register"),
    ("https://before-you-fly.netlify.app/", "Before You Fly", "Passport validity, airport liquid rules, cabin bag sizes"),
    ("https://visa-income-checker.netlify.app/", "Visa Income Checker", "Income requirements and refusal rates for visas"),
    ("https://cruise-health-scores.netlify.app/", "Cruise Health Scores", "CDC sanitation scores of every cruise ship"),
]


def blocco_altri(voci, titolo):
    """Blocco "Other useful tools for your trip" in fondo a ogni pagina (stesso modello di esameb1/esamidistato): un titolo piccolo e una riga
    per sito. Link normali (nessun nofollow), rel="noopener", mai a questo sito."""
    assert not any(u.startswith(URL_SITO) for u, _, _ in voci), "il blocco altri siti non deve linkare questo sito"
    li = "".join(f'<li><a href="{u}" rel="noopener">{escape(n)}</a> — {escape(d)}</li>' for u, n, d in voci)
    return f'<div class="f-altri"><h2>{escape(titolo)}</h2><ul>{li}</ul></div>'

# Contatore visite GoatCounter, account condiviso "rete-siti" della rete (nessun cookie, nessun dato personale conservato).
# Il percorso inviato comprende l'host (location.host + percorso), così nel cruscotto https://rete-siti.goatcounter.com
# ogni sito si distingue dagli altri. Da localhost, da file:// e dalle reti private count.js non invia nulla
# (allow_local resta spento): le prove in locale non contano come visite. Unico punto da cambiare per tutto il sito.
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
# IndexNow (Bing, Yandex, Naver, Seznam): chiave pubblica uguale per tutti i siti della rete. Il generatore scrive
# sito/<chiave>.txt (contenuto: la chiave) accanto a robots.txt; l'invio degli URL lo fa studio-business/strumenti/indexnow.py.
CHIAVE_INDEXNOW = "b5a26a844a465f58552debee2c8a0114"
NOME = "Tourist Tax Calculator"
ANNO = 2026
OGGI = date.today()

DEST = json.loads((DATI / "destinazioni.json").read_text(encoding="utf-8"))["destinazioni"]
FR = json.loads((DATI / "francia.json").read_text(encoding="utf-8"))
FR_TOP = json.loads((DATI / "francia_top.json").read_text(encoding="utf-8"))
AFFILIATI = json.loads((DATI / "affiliati.json").read_text(encoding="utf-8")) if (DATI / "affiliati.json").exists() else {}

PAESI = {  # slug paese -> (nome, aggettivo/nota breve)
    "france": "France", "spain": "Spain", "greece": "Greece", "turkey": "Turkey", "netherlands": "Netherlands",
    "germany": "Germany", "austria": "Austria", "czech-republic": "Czech Republic", "united-kingdom": "United Kingdom",
    "italy": "Italy", "japan": "Japan", "indonesia": "Indonesia", "iceland": "Iceland"}
EUROPA = {"france", "spain", "greece", "netherlands", "germany", "austria", "czech-republic", "united-kingdom", "italy", "iceland", "turkey"}
VALUTE = {"EUR": ("€", "", 2), "GBP": ("£", "", 2), "JPY": ("¥", "", 0), "CZK": ("", " CZK", 0), "ISK": ("ISK ", "", 0),
          "IDR": ("IDR ", "", 0), "TRY": ("TRY ", "", 2)}
MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


# ---------------------------------------------------------------- utilità
def r2(x):
    """Arrotondamento al centesimo, mezzo in su (uguale nel JS)."""
    return math.floor(x * 100 + 0.5 + 1e-9) / 100


def soldi(v, valuta):
    pre, post, dec = VALUTE[valuta]
    if dec == 0:
        testo = f"{int(math.floor(v + 0.5 + 1e-9)):,}"
    else:
        testo = f"{r2(v):,.2f}"
    return f"{pre}{testo}{post}"


def plur(n, uno, molti=None):
    """'1 paying guest' / '2 paying guests' (uguale nel JS)."""
    return f"{n} {uno if n == 1 else (molti or uno + 's')}"


def num(v):
    """Numero senza zeri inutili (12.5 -> 12.5, 3.0 -> 3)."""
    return ("%g" % v) if isinstance(v, (int, float)) else str(v)


def data_lunga(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {MESI[d.month - 1]} {d.year}"


def dep_nome(dep):
    dep = dep if len(dep) > 1 else "0" + dep
    return FR["dipartimenti"].get(dep, dep)


def slugify(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


# ---------------------------------------------------------------- Francia: voce "regola" per una comune
def fr_regola(code):
    nome_dgfip, dep, vi, posti, flag, nome_insee = FR["comuni"][code]
    vett = FR["vettori"][vi]
    nome = nome_insee or nome_dgfip.title()
    categorie, tariffe, cap = [], [], 0.0
    for (cid, lab, _fr), riga in zip(FR["categorie"], vett):
        if riga is None:
            continue
        t, u, tot, add, reg, per = riga
        if u == "€" and t is not None:
            cap = max(cap, t)
        categorie.append({"id": cid, "label": lab})
        tariffe.append({"cat": cid, "dal": f"{ANNO}-01-01", "al": f"{ANNO}-12-31",
                        "fr": {"t": t, "u": u, "tot": tot, "add": add, "reg": reg, "per": per}})
    return {"slug": "", "name": nome, "country": "France", "country_slug": "france", "currency": "EUR", "tipo": "france",
            "categorie": categorie, "tariffe": tariffe, "cap": cap, "esenti_sotto_eta": 18, "dep": dep,
            "dep_nome": dep_nome(dep), "code": code, "flag": flag,
            "nome_dgfip": nome_dgfip, "posti": posti,
            "etichetta_prezzo": "Price per night for the accommodation, excluding taxes (only for unclassified accommodation)"}


# ---------------------------------------------------------------- motore di calcolo (uguale al JS)
def _riga(R, cat, d_iso):
    m = int(d_iso[5:7])
    for t in R["tariffe"]:
        if t["cat"] != cat:
            continue
        if t.get("dal") and d_iso < t["dal"]:
            continue
        if t.get("al") and d_iso > t["al"]:
            continue
        if t.get("mesi") and m not in t["mesi"]:
            continue
        return t
    return None


def _in_periodo(periodi, d_iso):
    if not periodi:
        return True
    md = int(d_iso[5:7]) * 100 + int(d_iso[8:10])
    for p in periodi:
        mm = re.match(r"(\d\d)-(\d\d)\s*-\s*(\d\d)-(\d\d)", p)
        if not mm:
            return True
        a = int(mm.group(2)) * 100 + int(mm.group(1))
        b = int(mm.group(4)) * 100 + int(mm.group(3))
        if (a <= b and a <= md <= b) or (a > b and (md >= a or md <= b)):
            return True
    return False


def _banda(bande, pp):
    for i, (lo, hi, v) in enumerate(bande):
        if pp >= lo and (hi is None or pp < hi):
            return i, v
    return -1, 0


def _piu_mesi(iso, m):
    """Stessa data m mesi dopo (giorno ridotto all'ultimo del mese se non esiste). Uguale nel JS."""
    y, mo, d = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
    mo += m
    y += (mo - 1) // 12
    mo = (mo - 1) % 12 + 1
    ultimo = [31, 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mo - 1]
    return f"{y:04d}-{mo:02d}-{min(d, ultimo):02d}"


def _supplemento(R, zona, cat, d_iso):
    if not zona:
        return None
    for t in R.get("supplementi", []):
        if t["zona"] == zona and t["cat"] == cat and (not t.get("dal") or t["dal"] <= d_iso) and (not t.get("al") or d_iso <= t["al"]):
            return t
    return None


def calcola(R, cat, checkin, notti, paganti, esenti=0, stanze=1, prezzo=0.0, zona=""):
    """Restituisce {'totale', 'righe': [[testo, notti, importo]], 'escluse', 'sconosciute', 'fuori', 'prima', 'note'}."""
    val = R["currency"]
    out = {"totale": 0.0, "righe": [], "escluse": 0, "sconosciute": 0, "fuori": 0, "prima": 0, "note": []}
    gruppi = {}

    def aggiungi(testo, importo):
        g = gruppi.setdefault(testo, [testo, 0, 0.0])
        g[1] += 1
        g[2] += importo

    meta = {c["id"]: c for c in R["categorie"]}
    if R["tipo"] == "per_trip":
        t = _riga(R, cat, checkin)
        if t is None:
            out["sconosciute"] = 1
        else:
            imp = t["valore"] * paganti
            out["righe"] = [[f"{soldi(t['valore'], val)} × {plur(paganti, 'traveller')}, once per trip", 1, imp]]
            out["totale"] = imp
        return out
    if R.get("max_soggiorno") and notti + 1 > R["max_soggiorno"]:
        out["note"].append(f"This stay spans {notti + 1} calendar days (arrival day included): only stays of at most "
                           f"{R['max_soggiorno']} consecutive calendar days are subject to the fee.")
        return out
    if R.get("esente_oltre_mesi"):
        uscita = (date.fromisoformat(checkin) + timedelta(days=notti)).isoformat()
        if uscita > _piu_mesi(checkin, R["esente_oltre_mesi"]):
            out["note"].append(f"Stays of more than {R['esente_oltre_mesi']} months without interruption are exempt.")
            return out
    max_n = meta.get(cat, {}).get("max_notti") or R.get("max_notti")
    persone = paganti + esenti
    d0 = date.fromisoformat(checkin)
    for i in range(notti):
        d = (d0 + timedelta(days=i)).isoformat()
        n = i + 1
        if max_n and n > max_n:
            out["escluse"] += 1
            continue
        if R.get("in_vigore_dal") and d < R["in_vigore_dal"]:
            out["prima"] += 1
            continue
        t = _riga(R, cat, d)
        if t is None:
            out["sconosciute"] += 1
            continue
        tipo = R["tipo"]
        if tipo == "per_person":
            sup = _supplemento(R, zona, cat, d)
            v = t["valore"] + (sup["valore"] if sup else 0)
            imp = v * paganti
            testo = f"{soldi(v, val)} per person × {plur(paganti, 'paying guest')}"
            if sup:
                nz = next(z["label"] for z in R["zone"] if z["id"] == zona)
                testo += f" (incl. {soldi(sup['valore'], val)} {nz} surcharge)"
        elif tipo == "per_room":
            imp = t["valore"] * stanze
            testo = f"{soldi(t['valore'], val)} per room/unit × {plur(stanze, 'room/unit', 'rooms/units')}"
            if t.get("stagione"):
                testo += f" ({t['stagione']} rate)"
        elif tipo == "percent":
            f = t.get("fattore_base", 1)
            imp = prezzo * f * t["valore"] / 100
            testo = f"{num(t['valore'])}% of {soldi(prezzo, val)}" + (f" after a {num(round((1 - f) * 100, 4))}% deduction" if f != 1 else "")
        elif tipo == "bands":
            pp = prezzo / persone if persone else 0
            _, b = _banda(t["valore"], pp)
            imp = b * persone
            testo = f"{soldi(b, val)} per person (band for {soldi(pp, val)} per person) × {plur(persone, 'guest')}"
        elif tipo == "france":
            fr = t["fr"]
            if not _in_periodo(fr["per"], d):
                out["fuori"] += 1
                continue
            if fr["reg"] == "F":
                nf = "This category is taxed with the flat-rate scheme (taxe forfaitaire): the host pays it, it is not charged per guest."
                if nf not in out["note"]:
                    out["note"].append(nf)
                aggiungi("flat-rate scheme, paid by the host", 0.0)
                continue
            if fr["u"] == "€":
                per = fr["tot"]
                imp = per * paganti
                testo = f"{soldi(per, val)} per person ({soldi(fr['t'], val)} + {num(fr['add'])}% additional taxes) × {plur(paganti, 'paying guest')}"
            else:
                costo = prezzo / persone if persone else 0
                base = min(r2(fr["t"] / 100 * costo), R["cap"])
                per = r2(base * (1 + fr["add"] / 100))
                imp = per * paganti
                testo = (f"{soldi(per, val)} per person ({num(fr['t'])}% of {soldi(costo, val)} per person, capped at {soldi(R['cap'], val)}"
                         f", + {num(fr['add'])}% additional taxes) × {plur(paganti, 'paying guest')}")
        else:
            raise ValueError(tipo)
        for rid in R.get("riduzioni", []):
            if rid["tipo"] == "mesi" and int(d[5:7]) in rid["mesi"]:
                imp *= (1 - rid["percento"] / 100)
                testo += f", {rid['testo']}"
            elif rid["tipo"] == "dal_giorno" and n >= rid["giorno"]:
                imp *= (1 - rid["percento"] / 100)
                testo += f", {rid['testo']}"
        aggiungi(testo, imp)
    if out["prima"] and max_n:
        out["note"].append("For a stay that starts before the tax began, check with your accommodation how the maximum number of nights is counted.")
    out["righe"] = list(gruppi.values())
    out["totale"] = sum(g[2] for g in out["righe"])
    return out


# ---------------------------------------------------------------- testi derivati dalle regole
def righe_correnti(R, giorno=None):
    """Tariffe valide alla data indicata (o la prima data coperta, se la data è fuori)."""
    giorno = giorno or OGGI.isoformat()
    ok = [t for t in R["tariffe"] if (not t.get("dal") or t["dal"] <= giorno) and (not t.get("al") or giorno <= t["al"])]
    if not ok:
        future = sorted({t["dal"] for t in R["tariffe"] if t.get("dal") and t["dal"] > giorno})
        if future:
            ok = [t for t in R["tariffe"] if t.get("dal") == future[0]]
        else:
            ok = R["tariffe"]
    return ok


def riassunto(R, giorno=None, seguito=True):
    """Tariffa in vigore alla data di generazione; se scade, indica fino a quando e cosa viene dopo."""
    base = _riassunto(R, giorno)
    if not seguito:
        return base
    tt = righe_correnti(R, giorno)
    fine = {t.get("al") for t in tt}
    if len(fine) == 1 and None not in fine:
        al = fine.pop()
        dopo = (date.fromisoformat(al) + timedelta(days=1)).isoformat()
        if any(t.get("dal") == dopo for t in R["tariffe"]):
            return f"{base} until {data_lunga(al)}, then {_riassunto(R, dopo)}"
        return f"{base} until {data_lunga(al)}"
    return base


def _riassunto(R, giorno=None):
    val = R["currency"]
    tt = righe_correnti(R, giorno)
    tipo = R["tipo"]
    if tipo == "france":
        vals = [t["fr"]["tot"] for t in tt if t["fr"]["u"] == "€" and t["fr"]["reg"] == "R"]
        nc = [t for t in tt if t["fr"]["u"] == "%"]
        s = f"{soldi(min(vals), val)}–{soldi(max(vals), val)} per person per night" if vals else "flat-rate only"
        if nc:
            s += f"; unclassified: {num(nc[0]['fr']['t'])}% of the price"
        return s
    if tipo in ("per_person", "per_room"):
        vals = [t["valore"] for t in tt]
        unit = "per person per night" if tipo == "per_person" else "per room per night"
        if min(vals) == max(vals):
            return f"{soldi(min(vals), val)} {unit}"
        return f"{soldi(min(vals), val)}–{soldi(max(vals), val)} {unit}"
    if tipo == "percent":
        vals = sorted({t["valore"] for t in tt})
        return " / ".join(f"{num(v)}%" for v in vals) + " of the room price"
    if tipo == "bands":
        vals = [b[2] for t in tt for b in t["valore"]]
        nz = [v for v in vals if v > 0]
        return f"{soldi(min(nz), val)}–{soldi(max(nz), val)} per person per night (by price band)"
    if tipo == "per_trip":
        return f"{soldi(tt[0]['valore'], val)} per person, once per trip"
    return ""


def formula(R):
    tipo = R["tipo"]
    eta = R.get("esenti_sotto_eta")
    maxn = R.get("max_notti")
    pag = f"guests aged {eta} or over" if eta else "guests"
    if tipo == "per_person":
        f = f"Tax = rate per person per night × {pag} × taxable nights"
    elif tipo == "per_room":
        f = "Tax = rate per room (or unit) per night × rooms × nights"
    elif tipo == "percent":
        f = f"Tax = rate % × {R.get('etichetta_prezzo', 'price per night')[0].lower() + R.get('etichetta_prezzo', 'price per night')[1:]} × taxable nights"
    elif tipo == "bands":
        f = "Tax = band amount (from the price per person per night = room price ÷ guests) × guests × nights"
    elif tipo == "per_trip":
        f = "Levy = amount per person × travellers (once per trip)"
    else:
        f = ("Classified accommodation: tax = (municipal rate + additional taxes) × guests aged 18 or over × nights. "
             "Unclassified: rate % × (price per night excluding taxes ÷ all occupants), capped at the highest rate adopted by the town, "
             "+ additional taxes, × guests aged 18 or over × nights")
    extra = []
    if maxn:
        extra.append(f"maximum {maxn} taxable nights per stay")
    if any(c.get("max_notti") for c in R["categorie"]):
        extra.append("some categories have their own maximum (see the table)")
    for rid in R.get("riduzioni", []):
        extra.append(rid["testo"])
    if R.get("max_soggiorno"):
        extra.append(f"stays longer than {R['max_soggiorno']} consecutive calendar days, i.e. {R['max_soggiorno']} nights or more, are not covered")
    if R.get("esente_oltre_mesi"):
        extra.append(f"stays of more than {R['esente_oltre_mesi']} months without interruption are exempt")
    if R.get("in_vigore_dal"):
        extra.append(f"no tax on nights before {data_lunga(R['in_vigore_dal'])}, when it started")
    if R.get("zone"):
        extra.append("plus the municipal surcharge where one applies")
    return f + (" (" + "; ".join(extra) + ")" if extra else "") + "."


def tabella_tariffe(R):
    val = R["currency"]
    tipo = R["tipo"]
    cat = {c["id"]: c for c in R["categorie"]}
    if tipo == "bands":
        h = []
        for t in R["tariffe"]:
            per = periodo_testo(t)
            righe = []
            for i, (lo, hi, v) in enumerate(t["valore"]):
                fascia = f"{soldi(lo, val)} – {soldi(hi - 1, val)}" if hi else f"{soldi(lo, val)} or more"
                if lo == 0 and hi:
                    fascia = f"under {soldi(hi, val)}"
                parti = ""
                if t.get("parti_bande") and t["parti_bande"][i]:
                    parti = f' <span class="small">({" + ".join(escape(p) for p in t["parti_bande"][i])})</span>'
                righe.append(f"<tr><td>{fascia}</td><td><strong>{soldi(v, val) if v else 'no tax'}</strong>{parti}</td></tr>")
            nota = f'<p class="small">{escape(t["nota"])}</p>' if t.get("nota") else ""
            h.append(f'<h3>{escape(per)}</h3><div class="tab"><table><thead><tr><th>Price per person per night</th><th>Tax per person per night</th></tr></thead>'
                     f'<tbody>{"".join(righe)}</tbody></table></div>{nota}')
        return "".join(h)
    if tipo == "france":
        righe = []
        for t in R["tariffe"]:
            fr = t["fr"]
            lab = escape(cat[t["cat"]]["label"])
            if fr["u"] == "%":
                tassa = f"{num(fr['t'])}% of the price per person (cap {soldi(R['cap'], val)}) + {num(fr['add'])}%"
                tot = f"{num(fr['t'])}% × price, max {soldi(r2(R['cap'] * (1 + fr['add'] / 100)), val)}"
            else:
                tassa = f"{soldi(fr['t'], val)} + {num(fr['add'])}%"
                tot = soldi(fr["tot"], val)
            if fr["reg"] == "F":
                tot += ' <span class="small">(flat-rate: paid by the host)</span>'
            per = ", ".join(escape(p) for p in fr["per"]) if fr["per"] and fr["per"] != ["01-01 - 31-12"] else "all year"
            righe.append(f"<tr><td>{lab}</td><td>{tassa}</td><td><strong>{tot}</strong></td><td>{per}</td></tr>")
        return ('<div class="tab"><table><thead><tr><th>Accommodation</th><th>Municipal rate + additional taxes</th><th>Total per person per night</th>'
                f'<th>Collection period (day-month)</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>')
    # per_person, per_room, percent, per_trip: righe = categorie, colonne = periodi/stagioni
    colonne = []
    for t in R["tariffe"]:
        k = periodo_testo(t)
        if k not in colonne:
            colonne.append(k)
    unit = {"per_person": "per person per night", "per_room": "per room per night", "percent": "of the price", "per_trip": "per person"}[tipo]
    righe = []
    for c in R["categorie"]:
        celle = []
        for k in colonne:
            t = next((x for x in R["tariffe"] if x["cat"] == c["id"] and periodo_testo(x) == k), None)
            if t is None:
                celle.append("<td>–</td>")
                continue
            v = f"{num(t['valore'])}%" if tipo == "percent" else soldi(t["valore"], val)
            if t.get("parti"):
                v += ' <span class="small">(' + " + ".join(f"{escape(a)} {soldi(b, val)}" for a, b in t["parti"].items()) + ")</span>"
            if t.get("nota"):
                v += f' <span class="small">({escape(t["nota"])})</span>'
            celle.append(f"<td><strong>{v}</strong></td>")
        mx = f' <span class="small">(max {c["max_notti"]} nights)</span>' if c.get("max_notti") else ""
        righe.append(f"<tr><td>{escape(c['label'])}{mx}</td>{''.join(celle)}</tr>")
    testa = "".join(f"<th>{escape(k)}</th>" for k in colonne)
    return (f'<div class="tab"><table><thead><tr><th>Accommodation ({unit})</th>{testa}</tr></thead>'
            f'<tbody>{"".join(righe)}</tbody></table></div>')


def periodo_testo(t):
    if t.get("stagione"):
        return t["stagione"]
    a, b = t.get("dal"), t.get("al")
    if a and b:
        return f"{data_lunga(a)} – {data_lunga(b)}"
    if a:
        return f"From {data_lunga(a)}"
    if b:
        return f"Current rates (until {data_lunga(b)})"
    return "Current rate"


# ---------------------------------------------------------------- CSS e JS
CSS = """
@font-face{font-family:"Bricolage Grotesque";font-style:normal;font-weight:700;font-display:swap;src:url(/assets/fonts/bricolage-grotesque-700.woff2) format("woff2")}
:root{--bg:#FBF6EF;--band:#F6E9DA;--card:#FFFFFF;--ink:#1F1A17;--ink-2:#4A413B;--ink-3:#6A5F57;--line:#E8DCCD;--line-2:#D9C8B5;
--accent:#B23F1B;--accent-h:#962F10;--on-accent:#FFFFFF;--accent-2:#FCEADF;--sun:#F2B544;--sea:#0F6170;--sea-2:#E1F0F0;
--ok:#1C6B45;--ok-2:#E4F3EA;--warn:#8A4B00;--warn-2:#FFF1DC;--mute:#F5EDE3;--foot:#211A16;--foot-ink:#E9DDD2;--foot-ink-2:#B9AA9C;
--sh-1:0 1px 2px rgba(60,35,20,.06),0 1px 1px rgba(60,35,20,.04);--sh-2:0 18px 40px -18px rgba(120,55,25,.28),0 2px 8px rgba(60,35,20,.06);
--r:16px;--r-s:12px;--head:"Bricolage Grotesque",ui-rounded,"Segoe UI",system-ui,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#15110E;--band:#1E1712;--card:#211A15;--ink:#F6EEE7;--ink-2:#D8CABF;--ink-3:#AE9F93;
--line:#392D25;--line-2:#4A3B31;--accent:#FF9A72;--accent-h:#FFB495;--on-accent:#24130B;--accent-2:#3A2218;--sun:#F2B544;--sea:#7CCFD9;--sea-2:#15302F;
--ok:#82D5A8;--ok-2:#173226;--warn:#FFB867;--warn-2:#33250F;--mute:#2A211B;--foot:#0E0B09;--foot-ink:#E9DDD2;--foot-ink-2:#A89A8E;
--sh-1:0 1px 2px rgba(0,0,0,.4);--sh-2:0 18px 40px -18px rgba(0,0,0,.7),0 2px 8px rgba(0,0,0,.35)}}
:root[data-theme="dark"]{--bg:#15110E;--band:#1E1712;--card:#211A15;--ink:#F6EEE7;--ink-2:#D8CABF;--ink-3:#AE9F93;
--line:#392D25;--line-2:#4A3B31;--accent:#FF9A72;--accent-h:#FFB495;--on-accent:#24130B;--accent-2:#3A2218;--sun:#F2B544;--sea:#7CCFD9;--sea-2:#15302F;
--ok:#82D5A8;--ok-2:#173226;--warn:#FFB867;--warn-2:#33250F;--mute:#2A211B;--foot:#0E0B09;--foot-ink:#E9DDD2;--foot-ink-2:#A89A8E;
--sh-1:0 1px 2px rgba(0,0,0,.4);--sh-2:0 18px 40px -18px rgba(0,0,0,.7),0 2px 8px rgba(0,0,0,.35)}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;font-size:17px;line-height:1.6;overflow-wrap:break-word}
a{color:var(--accent);text-underline-offset:2px;text-decoration-thickness:1px}
a:hover{color:var(--accent-h)}
:focus-visible{outline:3px solid var(--accent);outline-offset:2px;border-radius:6px}
.skip{position:absolute;left:-9999px;top:8px;background:var(--card);color:var(--ink);padding:8px 14px;border-radius:10px;z-index:50}
.skip:focus{left:12px}
.ico{width:1.15em;height:1.15em;flex:none;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;vertical-align:-.2em}
.wrap{max-width:1040px;margin:0 auto;padding:0 16px}
header.top{background:var(--card);border-bottom:1px solid var(--line);position:relative;z-index:20}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:64px}
.logo{display:flex;align-items:center;gap:10px;font-family:var(--head);font-weight:700;font-size:1.13rem;color:var(--ink);text-decoration:none;letter-spacing:-.015em;white-space:nowrap}
.logo:hover{color:var(--ink)}
.logo svg{width:34px;height:34px;flex:none}
.logo b{color:var(--accent);font-weight:inherit}
nav.menu{display:flex;gap:4px;font-size:.93rem}
nav.menu a{color:var(--ink-2);text-decoration:none;padding:7px 11px;border-radius:999px;white-space:nowrap}
nav.menu a:hover{color:var(--accent);background:var(--accent-2)}
.nav-m{display:none}
.nav-m summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:8px;font-weight:600;font-size:.95rem;padding:9px 14px;border:1px solid var(--line-2);border-radius:999px;color:var(--ink);min-height:44px}
.nav-m summary::-webkit-details-marker{display:none}
.nav-m[open] summary{background:var(--accent-2);border-color:var(--accent)}
.nav-m nav{position:absolute;left:16px;right:16px;top:calc(100% - 4px);background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-2);padding:8px;display:grid}
.nav-m nav a{padding:12px 14px;border-radius:10px;color:var(--ink);text-decoration:none;font-weight:600}
.nav-m nav a:hover{background:var(--accent-2)}
.band{background:radial-gradient(1200px 380px at 85% -40%,rgba(242,181,68,.35),transparent 60%),linear-gradient(180deg,var(--band),var(--bg));border-bottom:1px solid var(--line)}
.band-in{position:relative;padding-top:34px;padding-bottom:30px}
.band-deco{position:absolute;right:0;top:18px;width:250px;height:170px;opacity:.9;pointer-events:none}
.hero{padding:26px 0 6px}
.home .hero{padding:0 0 20px;max-width:720px;position:relative}
h1,.sub{text-wrap:balance}
h1,h2,h3,.tot,.big{font-family:var(--head);font-weight:700}
h1{font-size:clamp(1.75rem,5vw,2.75rem);line-height:1.08;letter-spacing:-.025em;margin:0 0 10px}
h1 .h1-a{display:block;font-size:clamp(1.65rem,4.6vw,2.5rem)}
h1 .h1-b{display:block;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-weight:600;font-size:clamp(1rem,2.4vw,1.2rem);color:var(--ink-2);letter-spacing:0;margin-top:6px;line-height:1.35}
h1 .h1-b::first-letter{text-transform:uppercase}
.home h1 .h1-a{display:inline-block;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-size:.8rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);background:var(--card);border:1px solid var(--line-2);padding:5px 12px;border-radius:999px;margin-bottom:14px}
.home h1 .h1-b{font-family:var(--head);font-weight:700;color:var(--ink);font-size:clamp(2rem,6vw,3.1rem);letter-spacing:-.03em;line-height:1.04;margin:0}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.sub{font-size:1.1rem;color:var(--ink-2);margin:0 0 14px;max-width:600px}
.trust{display:flex;flex-wrap:wrap;align-items:center;gap:6px 14px;font-size:.88rem;color:var(--ink-2);margin:0}
.trust span{display:inline-flex;align-items:center;gap:6px}
.trust .ico{color:var(--ok)}
h2{font-size:1.45rem;line-height:1.2;margin:40px 0 14px;letter-spacing:-.015em}
h3{font-size:1.1rem;margin:22px 0 8px}
.lead{font-size:1.04rem;color:var(--ink-2);max-width:760px;margin:0 0 8px}
.small{font-size:.88rem;color:var(--ink-3)}
.avviso{position:relative;background:var(--warn-2);border:1px solid color-mix(in srgb,var(--warn) 25%,transparent);padding:12px 16px 12px 46px;border-radius:var(--r-s);font-size:.93rem;margin:18px 0;color:var(--ink)}
.avviso::before{content:"";position:absolute;left:16px;top:14px;width:20px;height:20px;background:var(--warn);-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cpath d='M12 16v-4M12 8h.01'/%3E%3C/svg%3E") center/contain no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cpath d='M12 16v-4M12 8h.01'/%3E%3C/svg%3E") center/contain no-repeat}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:20px;min-width:0;box-shadow:var(--sh-1)}
.cifra{font-size:1rem;margin:0 0 6px;color:var(--ink-2)}
.cifra strong{display:block;font-family:var(--head);font-size:clamp(1.35rem,3.6vw,1.75rem);line-height:1.2;color:var(--ink);letter-spacing:-.01em;margin-top:2px}
.fonte{font-size:.84rem;color:var(--ink-3);margin:8px 0 0;overflow-wrap:anywhere}
.fonte a{color:var(--ink-2)}
.summary{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,1fr);gap:18px 26px;padding:22px;margin-top:6px;position:relative;overflow:hidden}
.summary::before{content:"";position:absolute;inset:0 auto 0 0;width:5px;background:linear-gradient(var(--accent),var(--sun))}
.summary .lab{font-size:.78rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin:0 0 4px;display:flex;align-items:center;gap:6px}
.summary .lead{font-size:.95rem;margin:0}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 0;padding:0;list-style:none}
.chips li{display:inline-flex;align-items:center;gap:6px;font-size:.85rem;font-weight:600;color:var(--ink-2);background:var(--mute);border:1px solid var(--line);padding:5px 11px;border-radius:999px}
.chips .ico{color:var(--accent)}
.summary+.calc,.hero+.calc{margin-top:18px}
.calc{display:grid;gap:0;padding:0;overflow:hidden;box-shadow:var(--sh-2);border-color:var(--line-2)}
.calc-grid{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr)}
.calc form{padding:22px}
.calc .campi{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.calc label{display:grid;gap:6px;align-content:end;font-weight:600;font-size:.9rem;line-height:1.35;min-width:0;color:var(--ink-2)}
.calc .lt{display:flex;align-items:center;gap:7px}
.calc .lt .ico{color:var(--accent);width:1.05em;height:1.05em}
.calc input,.calc select,.cerca,.form input,.form select,.form textarea{font:inherit;font-size:1rem;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:10px 12px;width:100%;min-width:0;min-height:46px;transition:border-color .15s,box-shadow .15s}
.calc input:hover,.calc select:hover{border-color:var(--ink-3)}
.calc input:focus,.calc select:focus,.cerca:focus,.form input:focus,.form textarea:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 22%,transparent)}
.calc .pieno{grid-column:1/-1}
.calc-out{background:linear-gradient(160deg,var(--accent-2),var(--card) 85%);border-left:1px solid var(--line);padding:22px;display:flex;flex-direction:column;gap:10px;min-width:0}
.risultato{min-width:0;overflow-wrap:anywhere}
.r-lab{font-size:.78rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3)}
.risultato .tot{font-size:clamp(2.4rem,7vw,3.2rem);line-height:1;color:var(--accent);letter-spacing:-.03em;margin:6px 0 4px;font-variant-numeric:tabular-nums}
.r-righe{list-style:none;margin:12px 0 0;padding:0;font-size:.88rem;color:var(--ink-2);display:grid;gap:6px}
.r-righe li{background:color-mix(in srgb,var(--card) 70%,transparent);border:1px solid var(--line);border-radius:10px;padding:8px 12px}
.r-righe .eq{display:block;font-family:var(--head);font-size:1.02rem;margin-top:2px;font-variant-numeric:tabular-nums}
.r-dl{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1px;margin:14px 0 0;background:var(--line);border:1px solid var(--line);border-radius:12px;overflow:hidden}
.r-dl div{background:color-mix(in srgb,var(--card) 88%,var(--accent-2));padding:9px 12px;min-width:0}
.r-dl div:last-child:nth-child(odd){grid-column:1/-1}
.r-dl dt{font-size:.74rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-3)}
.r-dl dd{margin:2px 0 0;font-family:var(--head);font-weight:700;font-size:1.08rem;color:var(--ink);font-variant-numeric:tabular-nums}
.r-bar{position:fixed;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom));z-index:30;display:flex;align-items:center;gap:10px;font:inherit;text-align:left;cursor:pointer;background:#1F1A17;color:#F6EEE7;border:1px solid #4A3B31;border-radius:14px;padding:10px 16px;min-height:52px;box-shadow:0 12px 30px -8px rgba(0,0,0,.45)}
.r-bar-tot{font-family:var(--head);font-weight:700;font-size:1.3rem;font-variant-numeric:tabular-nums;white-space:nowrap}
.r-bar-info{flex:1;min-width:0;font-size:.88rem;opacity:.85;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.r-bar-go{display:inline-flex;align-items:center;gap:4px;font-weight:700;font-size:.88rem;color:var(--sun)}
.r-righe strong{color:var(--ink)}
.calc-link{margin:auto 0 0;font-size:.9rem;font-weight:600}
.calc-link a{display:inline-flex;align-items:center;gap:6px;text-decoration:none}
.calc-link a:hover{text-decoration:underline}
details.formula{font-size:.9rem;color:var(--ink-2);margin:14px 0 0;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:0 14px}
details.formula summary{cursor:pointer;font-weight:600;padding:11px 0;display:flex;align-items:center;gap:8px;list-style:none;color:var(--ink)}
details.formula summary::-webkit-details-marker{display:none}
details.formula summary::after{content:"+";margin-left:auto;font-size:1.2rem;color:var(--accent)}
details.formula[open] summary::after{content:"–"}
details.formula p{margin:0 0 12px}
.esempio{font-size:.9rem;color:var(--ink-2);margin:10px 0 0}
.tab{overflow-x:auto;-webkit-overflow-scrolling:touch;border:1px solid var(--line);border-radius:var(--r);background:var(--card);box-shadow:var(--sh-1)}
table{border-collapse:collapse;width:100%;font-size:.92rem}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:var(--mute);font-size:.78rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--ink-2)}
td strong{font-variant-numeric:tabular-nums}
tbody tr:hover td{background:color-mix(in srgb,var(--accent-2) 45%,transparent)}
tr:last-child td{border-bottom:0}
@media (max-width:640px){.tab td,.tab th{min-width:120px}.tab td:first-child,.tab th:first-child{min-width:150px}}
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px}
.griglia a{display:block;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:12px 14px;text-decoration:none;color:var(--ink);font-weight:700;min-width:0;overflow-wrap:anywhere;box-shadow:var(--sh-1);transition:border-color .15s,transform .15s,box-shadow .15s}
.griglia a small{display:block;font-weight:400;color:var(--ink-3);font-size:.84rem;line-height:1.45;margin-top:3px}
.griglia.dest>a{display:flex;flex-direction:column;overflow-wrap:normal;hyphens:manual}
.griglia.dest>a small{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.griglia .fr-card{grid-column:1/-1;display:flex;flex-direction:column;gap:6px;background:var(--sea-2);border:1px solid color-mix(in srgb,var(--sea) 30%,transparent);border-radius:var(--r-s);padding:12px 14px;min-width:0}
.griglia .fr-card>a{all:unset;cursor:pointer;display:flex;align-items:center;gap:8px;font-weight:700;color:var(--ink)}
.griglia .fr-card>a .ico{color:var(--sea)}
.griglia .fr-card>a:hover,.griglia .fr-card>a:focus-visible{text-decoration:underline;color:var(--ink)}
.fr-top{font-size:.86rem;color:var(--ink-3);line-height:1.6}
.fr-top a{all:unset;cursor:pointer;color:var(--ink-2);white-space:nowrap}.fr-top a:hover{text-decoration:underline;color:var(--ink)}
.griglia a:hover{border-color:var(--accent);transform:translateY(-1px);box-shadow:var(--sh-2);color:var(--ink)}
.cerca-box{position:relative}
.cerca-box .ico{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:var(--ink-3);pointer-events:none}
.cerca{padding-left:42px;background:var(--card);margin:0}
.sez{margin-top:12px}
.sez-h{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
.tipi{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin:0;padding:0;list-style:none}
.tipi li{background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:14px;font-size:.88rem;color:var(--ink-2);box-shadow:var(--sh-1)}
.tipi .ic{display:grid;place-items:center;width:40px;height:40px;border-radius:10px;background:var(--accent-2);color:var(--accent);margin-bottom:8px}
.tipi .ic .ico{width:22px;height:22px}
.tipi strong{display:block;color:var(--ink);font-size:.95rem}
.callout{display:flex;align-items:center;gap:14px;padding:14px 18px;margin-top:14px}
.callout .ic{display:grid;place-items:center;width:42px;height:42px;border-radius:12px;background:var(--sea-2);color:var(--sea);flex:none}
.callout p{margin:0}
.testo p,.testo li{max-width:760px}
.form{display:grid;gap:14px}
.form label{display:grid;gap:6px;font-weight:600;font-size:.95rem}
.form .check{display:flex;gap:10px;align-items:flex-start;font-weight:400;font-size:.9rem;color:var(--ink-2)}
.form .check input{width:auto;min-height:0;margin-top:4px}
.btn{font:inherit;font-weight:700;background:var(--accent);color:var(--on-accent);border:0;border-radius:var(--r-s);padding:12px 22px;cursor:pointer;min-height:46px;box-shadow:var(--sh-1)}
.btn:hover{background:var(--accent-h)}
.btn:disabled{opacity:.6;cursor:wait}
.hp{position:absolute;left:-9999px}
.ok{background:var(--ok-2);border:1px solid var(--ok);padding:14px;border-radius:var(--r-s)}
.errore{color:var(--warn);font-weight:600}
.ad-slot:empty{display:none}
.briciole{font-size:.85rem;color:var(--ink-3);margin-top:18px}
.briciole a{color:var(--ink-3)}
.risultati-fr{display:grid;gap:6px;margin:10px 0 0}
.risultati-fr button{font:inherit;text-align:left;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:10px 14px;color:var(--ink);cursor:pointer;min-height:44px}
.risultati-fr button:hover{border-color:var(--accent);background:var(--accent-2)}
#fr-cerca label{display:flex;align-items:center;gap:8px;margin-bottom:10px;font-family:var(--head);font-size:1.15rem}
#fr-cerca label .ico{color:var(--accent)}
#fr-dettaglio .calc{margin-top:16px}
footer{margin-top:64px;background:var(--foot);color:var(--foot-ink-2);font-size:.88rem;padding:40px 0 34px}
footer a{color:var(--foot-ink)}
footer a:hover{color:#fff}
footer .f-grid{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:28px}
footer .logo{color:#F6EEE7;margin-bottom:12px}
footer .logo:hover{color:#F6EEE7}
footer .logo b{color:#FF9A72}
footer p{margin:0 0 10px;max-width:640px}
footer strong{color:var(--foot-ink)}
footer ul{list-style:none;margin:0;padding:0;display:grid;gap:8px}
footer h2{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-size:.78rem;letter-spacing:.1em;text-transform:uppercase;color:var(--foot-ink-2);margin:4px 0 12px}
footer .f-base{border-top:1px solid rgba(255,255,255,.12);margin-top:26px;padding-top:18px;font-size:.82rem;max-width:none}
footer .f-altri{border-top:1px solid rgba(255,255,255,.12);margin-top:24px;padding-top:18px}
footer .f-altri h2{margin:0 0 10px}
footer .f-altri ul{gap:6px}
footer .f-altri li{max-width:660px}
footer .f-altri a{font-weight:600}
@media (min-width:861px){.r-bar{display:none!important}}
@media (max-width:860px){.calc-grid{grid-template-columns:1fr}.calc-out{border-left:0;border-top:1px solid var(--line)}.tipi{grid-template-columns:repeat(2,minmax(0,1fr))}.band-deco{display:none}.summary{grid-template-columns:1fr}}
@media (max-width:760px){nav.menu{display:none}.nav-m{display:block}header.top .wrap{min-height:60px}
.calc .campi{grid-template-columns:1fr 1fr}.calc .campi>label[data-campo=stanze]{grid-column:1/-1}
.calc .campi:not(:has([data-campo=esenti]:not([hidden]))) [data-campo=paganti]{grid-column:1/-1}
.griglia.dest{grid-template-columns:1fr;gap:0;background:var(--card);border:1px solid var(--line);border-radius:var(--r);overflow:hidden;box-shadow:var(--sh-1)}
.griglia.dest>a{border:0;border-bottom:1px solid var(--line);border-radius:0;box-shadow:none;padding:12px 16px}.griglia.dest>a:hover{transform:none;box-shadow:none}
.griglia.dest .fr-card{grid-column:auto;border:0;border-radius:0}
.calc form,.calc-out{padding:18px}footer .f-grid{grid-template-columns:1fr}.band-in{padding-top:22px;padding-bottom:22px}}
@media (max-width:420px){.calc .campi{gap:12px}.tipi li{padding:12px}.summary{padding:18px 18px 18px 22px}}
@media (prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
"""

ICONE = {
    "bed": '<path d="M2 20v-8a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v8"/><path d="M2 16h20"/><path d="M4 10V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v4"/><path d="M7 10V8.5A1.5 1.5 0 0 1 8.5 7h2A1.5 1.5 0 0 1 12 8.5V10"/>',
    "city": '<path d="M3 21h18"/><path d="M5 21V8l6-4v17"/><path d="M11 21V10l8 3v8"/><path d="M8 9v.01M8 12v.01M8 15v.01M15 15v.01M15 18v.01"/>',
    "moon": '<path d="M20.5 14.5A8.5 8.5 0 1 1 9.5 3.5a7 7 0 0 0 11 11z"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20v-.5A5.5 5.5 0 0 1 8 14h2a5.5 5.5 0 0 1 5.5 5.5v.5"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8"/><path d="M21.5 20v-.5a5.5 5.5 0 0 0-3.5-5.1"/>',
    "child": '<circle cx="12" cy="6" r="3"/><path d="M8 21v-5l-2-3 3-3h6l3 3-2 3v5"/>',
    "calendar": '<rect x="3" y="4.5" width="18" height="17" rx="2.5"/><path d="M16 2.5v4M8 2.5v4M3 10h18"/>',
    "door": '<path d="M5 21V4.5A1.5 1.5 0 0 1 6.5 3h11A1.5 1.5 0 0 1 19 4.5V21"/><path d="M2.5 21h19"/><path d="M15 12.5v.01"/>',
    "tag": '<path d="M20.6 13.4l-7.2 7.2a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
    "percent": '<path d="M19 5L5 19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
    "bands": '<path d="M4 20V14M10 20V9M16 20V5"/><path d="M2 20h20"/>',
    "plane": '<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>',
    "shield": '<path d="M12 22s8-3.5 8-10V5.5L12 2.5 4 5.5V12c0 6.5 8 10 8 10z"/><path d="M8.5 12l2.5 2.5 4.5-4.5"/>',
    "search": '<circle cx="11" cy="11" r="7.5"/><path d="M21 21l-4.5-4.5"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
    "globe": '<circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19"/><path d="M12 2.5c2.6 2.6 4 6 4 9.5s-1.4 6.9-4 9.5c-2.6-2.6-4-6-4-9.5s1.4-6.9 4-9.5z"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "book": '<path d="M4 19.5V5a2 2 0 0 1 2-2h14v15H6.5A2.5 2.5 0 0 0 4 20.5 2.5 2.5 0 0 0 6.5 23H20"/><path d="M8 7h8"/>',
    "calc": '<rect x="4.5" y="2.5" width="15" height="19" rx="2.5"/><path d="M8 7h8M8 12h.01M12 12h.01M16 12h.01M8 16h.01M12 16h.01M16 16h.01"/>',
    "receipt": '<path d="M5 2.5h14v19l-2.5-1.6-2.3 1.6-2.2-1.6-2.2 1.6-2.3-1.6L5 21.5z"/><path d="M9 7.5h6M9 11.5h6M9 15.5h3.5"/>',
    "info": '<circle cx="12" cy="12" r="9.5"/><path d="M12 16.5v-5M12 8h.01"/>',
    "clock": '<circle cx="12" cy="12" r="9.5"/><path d="M12 7v5l3 2"/>',
}


def ico(nome, cls="ico"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="#i-{nome}"/></svg>'


SPRITE = ('<svg xmlns="http://www.w3.org/2000/svg" style="display:none">' +
          "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONE.items()) + "</svg>")

# Marchio: tessera terracotta con letto e moneta (stesso disegno nel favicon e nell'immagine Open Graph)
MARCHIO = ('<svg viewBox="0 0 40 40" aria-hidden="true" focusable="false"><rect width="40" height="40" rx="11" fill="#B23F1B"/>'
           '<path d="M8 29v-8.5a2 2 0 0 1 2-2h20a2 2 0 0 1 2 2V29M8 25h24M11 18.5v-3a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v3" fill="none" stroke="#FFF7EE" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
           '<circle cx="29" cy="11.5" r="5" fill="#F2B544"/><circle cx="29" cy="11.5" r="2.3" fill="none" stroke="#B23F1B" stroke-width="1.6"/></svg>')
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E%3Crect width='40' height='40' rx='11' fill='%23B23F1B'/%3E"
           "%3Cpath d='M8 29v-8.5a2 2 0 0 1 2-2h20a2 2 0 0 1 2 2V29M8 25h24M11 18.5v-3a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v3' fill='none' stroke='%23FFF7EE' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'/%3E"
           "%3Ccircle cx='29' cy='11.5' r='5' fill='%23F2B544'/%3E%3Ccircle cx='29' cy='11.5' r='2.3' fill='none' stroke='%23B23F1B' stroke-width='1.6'/%3E%3C/svg%3E")
DECO = ('<svg class="band-deco" viewBox="0 0 250 170" aria-hidden="true" focusable="false"><circle cx="190" cy="62" r="40" fill="#F2B544" opacity=".55"/>'
        '<path d="M0 132c30-14 52-14 82 0s52 14 82 0 52-14 86 0" fill="none" stroke="#B23F1B" stroke-opacity=".28" stroke-width="3" stroke-linecap="round"/>'
        '<path d="M20 152c30-14 52-14 82 0s52 14 82 0 40-10 66-4" fill="none" stroke="#0F6170" stroke-opacity=".22" stroke-width="3" stroke-linecap="round"/>'
        '<path d="M96 116V70l20-12 20 12v46M106 116V96h20v20M112 76h8" fill="none" stroke="#B23F1B" stroke-opacity=".35" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/></svg>')


def h1_diviso(testo, home=False):
    """H1 identico nel testo (per i motori di ricerca), diviso in due righe visive al primo ': '."""
    if ": " not in testo:
        return f"<h1>{escape(testo)}</h1>"
    a, b = testo.split(": ", 1)
    return f'<h1><span class="h1-a">{escape(a)}</span><span class="sr">: </span><span class="h1-b">{escape(b)}</span></h1>'


# Motore di calcolo in JS: deve dare gli stessi risultati di calcola() (verifica.py li confronta).
MOTORE_JS = r"""
var VAL={"EUR":["€","",2],"GBP":["£","",2],"JPY":["¥","",0],"CZK":[""," CZK",0],"ISK":["ISK ","",0],"IDR":["IDR ","",0],"TRY":["TRY ","",2]};
function r2(x){return Math.floor(x*100+0.5+1e-9)/100;}
function grp(n,dec){var s=dec?r2(n).toFixed(2):String(Math.floor(n+0.5+1e-9));var p=s.split('.');p[0]=p[0].replace(/\B(?=(\d{3})+(?!\d))/g,',');return p.join('.');}
function soldi(v,c){var x=VAL[c];return x[0]+grp(v,x[2])+x[1];}
function num(v){var s=String(Math.round(v*1e6)/1e6);return s;}
function plur(n,uno,molti){return n+' '+(n===1?uno:(molti||uno+'s'));}
function riga(R,cat,d){var m=+d.slice(5,7);for(var i=0;i<R.tariffe.length;i++){var t=R.tariffe[i];if(t.cat!==cat)continue;
  if(t.dal&&d<t.dal)continue;if(t.al&&d>t.al)continue;if(t.mesi&&t.mesi.indexOf(m)<0)continue;return t;}return null;}
function inPeriodo(per,d){if(!per||!per.length)return true;var md=(+d.slice(5,7))*100+(+d.slice(8,10));
  for(var i=0;i<per.length;i++){var m=/(\d\d)-(\d\d)\s*-\s*(\d\d)-(\d\d)/.exec(per[i]);if(!m)return true;
    var a=(+m[2])*100+(+m[1]),b=(+m[4])*100+(+m[3]);if((a<=b&&a<=md&&md<=b)||(a>b&&(md>=a||md<=b)))return true;}return false;}
function banda(b,pp){for(var i=0;i<b.length;i++){if(pp>=b[i][0]&&(b[i][1]===null||pp<b[i][1]))return b[i][2];}return 0;}
function addDays(iso,n){var p=iso.split('-');var x=new Date(Date.UTC(+p[0],+p[1]-1,+p[2]+n));return x.toISOString().slice(0,10);}
function piuMesi(iso,m){var y=+iso.slice(0,4),mo=+iso.slice(5,7)+m,d=+iso.slice(8,10);y+=Math.floor((mo-1)/12);mo=(mo-1)%12+1;
  var bis=(y%4===0&&(y%100!==0||y%400===0));var ult=[31,bis?29:28,31,30,31,30,31,31,30,31,30,31][mo-1];
  function p(n,l){var s=String(n);while(s.length<l)s='0'+s;return s;}return p(y,4)+'-'+p(mo,2)+'-'+p(Math.min(d,ult),2);}
function supplemento(R,zona,cat,d){if(!zona)return null;var s=R.supplementi||[];for(var i=0;i<s.length;i++){var t=s[i];
  if(t.zona===zona&&t.cat===cat&&(!t.dal||t.dal<=d)&&(!t.al||d<=t.al))return t;}return null;}
function calcola(R,cat,checkin,notti,paganti,esenti,stanze,prezzo,zona){
  esenti=esenti||0;stanze=stanze||1;prezzo=prezzo||0;zona=zona||'';var val=R.currency;
  var out={totale:0,righe:[],escluse:0,sconosciute:0,fuori:0,prima:0,note:[]};var gruppi={},ordine=[];
  function agg(t,imp){if(!gruppi[t]){gruppi[t]=[t,0,0];ordine.push(t);}gruppi[t][1]+=1;gruppi[t][2]+=imp;}
  var meta={};R.categorie.forEach(function(c){meta[c.id]=c;});
  if(R.tipo==='per_trip'){var t0=riga(R,cat,checkin);if(!t0){out.sconosciute=1;return out;}
    var im=t0.valore*paganti;out.righe=[[soldi(t0.valore,val)+' × '+plur(paganti,'traveller')+', once per trip',1,im]];out.totale=im;return out;}
  if(R.max_soggiorno&&notti+1>R.max_soggiorno){out.note.push('This stay spans '+(notti+1)+' calendar days (arrival day included): only stays of at most '+R.max_soggiorno+' consecutive calendar days are subject to the fee.');return out;}
  if(R.esente_oltre_mesi){if(addDays(checkin,notti)>piuMesi(checkin,R.esente_oltre_mesi)){out.note.push('Stays of more than '+R.esente_oltre_mesi+' months without interruption are exempt.');return out;}}
  var maxN=(meta[cat]&&meta[cat].max_notti)||R.max_notti;var persone=paganti+esenti;
  for(var i=0;i<notti;i++){var d=addDays(checkin,i),n=i+1;
    if(maxN&&n>maxN){out.escluse++;continue;}
    if(R.in_vigore_dal&&d<R.in_vigore_dal){out.prima++;continue;}
    var t=riga(R,cat,d);if(!t){out.sconosciute++;continue;}
    var imp,testo,tp=R.tipo;
    if(tp==='per_person'){var sp=supplemento(R,zona,cat,d);var vv=t.valore+(sp?sp.valore:0);imp=vv*paganti;testo=soldi(vv,val)+' per person × '+plur(paganti,'paying guest');
      if(sp){var nz=R.zone.filter(function(z){return z.id===zona;})[0].label;testo+=' (incl. '+soldi(sp.valore,val)+' '+nz+' surcharge)';}}
    else if(tp==='per_room'){imp=t.valore*stanze;testo=soldi(t.valore,val)+' per room/unit × '+plur(stanze,'room/unit','rooms/units');if(t.stagione)testo+=' ('+t.stagione+' rate)';}
    else if(tp==='percent'){var f=(t.fattore_base===undefined)?1:t.fattore_base;imp=prezzo*f*t.valore/100;
      testo=num(t.valore)+'% of '+soldi(prezzo,val)+(f!==1?' after a '+num(Math.round((1-f)*100*1e4)/1e4)+'% deduction':'');}
    else if(tp==='bands'){var pp=persone?prezzo/persone:0;var b=banda(t.valore,pp);imp=b*persone;
      testo=soldi(b,val)+' per person (band for '+soldi(pp,val)+' per person) × '+plur(persone,'guest');}
    else if(tp==='france'){var fr=t.fr;if(!inPeriodo(fr.per,d)){out.fuori++;continue;}
      if(fr.reg==='F'){var nf='This category is taxed with the flat-rate scheme (taxe forfaitaire): the host pays it, it is not charged per guest.';
        if(out.note.indexOf(nf)<0)out.note.push(nf);agg('flat-rate scheme, paid by the host',0);continue;}
      if(fr.u==='€'){imp=fr.tot*paganti;testo=soldi(fr.tot,val)+' per person ('+soldi(fr.t,val)+' + '+num(fr.add)+'% additional taxes) × '+plur(paganti,'paying guest');}
      else{var costo=persone?prezzo/persone:0;var base=Math.min(r2(fr.t/100*costo),R.cap);var per=r2(base*(1+fr.add/100));imp=per*paganti;
        testo=soldi(per,val)+' per person ('+num(fr.t)+'% of '+soldi(costo,val)+' per person, capped at '+soldi(R.cap,val)+', + '+num(fr.add)+'% additional taxes) × '+plur(paganti,'paying guest');}}
    (R.riduzioni||[]).forEach(function(rd){if(rd.tipo==='mesi'&&rd.mesi.indexOf(+d.slice(5,7))>=0){imp*=(1-rd.percento/100);testo+=', '+rd.testo;}
      else if(rd.tipo==='dal_giorno'&&n>=rd.giorno){imp*=(1-rd.percento/100);testo+=', '+rd.testo;}});
    agg(testo,imp);}
  if(out.prima&&maxN)out.note.push('For a stay that starts before the tax began, check with your accommodation how the maximum number of nights is counted.');
  out.righe=ordine.map(function(k){return gruppi[k];});out.totale=out.righe.reduce(function(s,g){return s+g[2];},0);return out;}
"""

APP_JS = r"""
(function(){
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function oggi(){var x=new Date();return new Date(Date.UTC(x.getFullYear(),x.getMonth(),x.getDate())).toISOString().slice(0,10);}
  function primaData(R){var o=oggi();var ok=R.tariffe.some(function(t){return (!t.dal||t.dal<=o)&&(!t.al||o<=t.al);});
    if(ok||R.tipo==='per_trip')return o;var ds=R.tariffe.map(function(t){return t.dal;}).filter(function(x){return x&&x>o;}).sort();return ds[0]||o;}
  function monta(box,R){
    var f=box.querySelector('form');var q=function(n){return f.querySelector('[name='+n+']');};
    var vis=function(n,on){var el=f.querySelector('[data-campo='+n+']');if(el)el.hidden=!on;};
    var cat=q('cat');cat.innerHTML=R.categorie.map(function(c){return '<option value="'+esc(c.id)+'">'+esc(c.label)+'</option>';}).join('');
    if(box.dataset.cat&&R.categorie.some(function(c){return c.id===box.dataset.cat;}))cat.value=box.dataset.cat;
    vis('cat',R.categorie.length>1);
    var zsel=q('zona');if(zsel){zsel.innerHTML='<option value="">Other municipality (no municipal surcharge)</option>'+(R.zone||[]).map(function(z){return '<option value="'+esc(z.id)+'">'+esc(z.label)+'</option>';}).join('');}
    if(!q('checkin').value||box.dataset.reset){q('checkin').value=primaData(R);}
    if(!box.dataset.prezzoToccato||box.dataset.reset){q('prezzo').value=R.prezzo_esempio||150;}
    if(!box.dataset.legatoPrezzo){q('prezzo').addEventListener('input',function(){box.dataset.prezzoToccato='1';});box.dataset.legatoPrezzo='1';}
    var eta=R.esenti_sotto_eta;
    f.querySelector('[data-lab=paganti]').textContent=R.tipo==='per_trip'?'Travellers':(eta?'Guests aged '+eta+' or over':'Guests');
    f.querySelector('[data-lab=esenti]').textContent=eta?'Children under '+eta+' (exempt)':'';
    var lp=f.querySelector('[data-lab=prezzo]');lp.textContent=(R.etichetta_prezzo||'Price per night')+' ('+R.currency+')';
    function aggiorna(){
      var tp=R.tipo,isNC=false;
      if(tp==='france'){var t=R.tariffe.filter(function(x){return x.cat===cat.value;})[0];isNC=t&&t.fr.u==='%';}
      vis('checkin',tp!=='per_trip');vis('notti',tp!=='per_trip');
      vis('paganti',tp!=='per_room'&&tp!=='percent');vis('esenti',!!eta&&tp!=='per_room'&&tp!=='percent');
      vis('stanze',tp==='per_room');vis('prezzo',tp==='percent'||tp==='bands'||isNC);
      var notti=Math.max(1,Math.min(365,parseInt(q('notti').value,10)||1));
      var pag=Math.max(0,parseInt(q('paganti').value,10)||0),es=Math.max(0,parseInt(q('esenti').value,10)||0);
      var st=Math.max(1,parseInt(q('stanze').value,10)||1),pr=Math.max(0,parseFloat(q('prezzo').value)||0);
      var ci=q('checkin').value||primaData(R);
      var zs=q('zona');vis('zona',!!(R.zone&&R.zone.length));
      var o=calcola(R,cat.value,ci,notti,pag,eta?es:0,st,pr,(R.zone&&zs)?zs.value:'');
      var cur=R.currency,tot=soldi(o.totale,cur);
      var h='<div class="r-lab">Estimated tax for this stay</div><div class="tot">'+tot+'</div>';
      var kv=[],tassate=o.righe.reduce(function(s,g){return s+(g[2]>0?g[1]:0);},0);
      if(tp!=='per_trip'){kv.push(['Taxed nights',tassate+' of '+notti]);kv.push(['Average per night',soldi(o.totale/notti,cur)]);}
      if((tp==='per_person'||tp==='france'||tp==='per_trip')&&pag>0)kv.push([tp==='per_trip'?'Per traveller':'Per paying guest',soldi(o.totale/pag,cur)]);
      if(eta&&tp!=='per_room'&&tp!=='percent')kv.push(['Exempt (under '+eta+')',plur(es,'guest')]);
      if(tp==='per_room')kv.push(['Rooms or units',String(st)]);
      if(tp==='percent'||tp==='bands'||isNC)kv.push(['Price per night',soldi(pr,cur)]);
      h+='<dl class="r-dl">'+kv.map(function(x){return '<div><dt>'+esc(x[0])+'</dt><dd>'+esc(x[1])+'</dd></div>';}).join('')+'</dl><ul class="r-righe">';
      o.righe.forEach(function(g){h+='<li><span>'+(tp==='per_trip'?'':plur(g[1],'night')+' × ')+esc(g[0])+'</span><strong class="eq">= '+soldi(g[2],cur)+'</strong></li>';});
      if(R.tipo==='per_trip'&&!o.righe.length)h+='<li>No verified amount.</li>';
      if(o.escluse)h+='<li>'+plur(o.escluse,'night')+' beyond the maximum number of taxable nights: no tax.</li>';
      if(o.fuori)h+='<li>'+plur(o.fuori,'night')+' outside the collection period: no tax.</li>';
      if(o.prima)h+='<li>'+plur(o.prima,'night')+' before '+esc(R.in_vigore_testo||R.in_vigore_dal)+': no tax yet.</li>';
      if(o.sconosciute)h+='<li>'+plur(o.sconosciute,'night')+' with no verified official rate for that date (not counted).</li>';
      o.note.forEach(function(n){h+='<li>'+esc(n)+'</li>';});
      h+='</ul>';box.querySelector('[data-out]').innerHTML=h;
      var bar=box.querySelector('[data-bar]');if(bar){bar.querySelector('.r-bar-tot').textContent=tot;
        bar.querySelector('.r-bar-info').textContent=(tp==='per_trip'?plur(pag,'traveller'):plur(notti,'night'))+' · '+R.name;if(box.__obs)box.__obs();}}
    if(!f.dataset.legato){var ag=function(e){if(e&&e.target&&e.target.name==='dest')return;box.__aggiorna();};
      f.addEventListener('input',ag);f.addEventListener('change',ag);f.addEventListener('submit',function(e){e.preventDefault();});f.dataset.legato='1';}
    box.__aggiorna=aggiorna;aggiorna();barra(box);}
  function barra(box){var bar=box.querySelector('[data-bar]'),out=box.querySelector('.calc-out'),fm=box.querySelector('form');
    if(!bar||box.dataset.barra||!('IntersectionObserver' in window))return;box.dataset.barra='1';
    var vOut=true,vForm=false,mq=window.matchMedia('(max-width:860px)');
    function agg(){bar.hidden=!(mq.matches&&vForm&&!vOut);}
    var ob=new IntersectionObserver(function(e){vOut=e[0].intersectionRatio>0.9;agg();},{threshold:[0,0.9,1]});var obs=function(){var t=out.querySelector('.tot');ob.disconnect();ob.observe(t||out);};obs();box.__obs=obs;
    new IntersectionObserver(function(e){vForm=e[0].isIntersecting;agg();}).observe(fm);
    if(mq.addEventListener)mq.addEventListener('change',agg);
    bar.addEventListener('click',function(){out.scrollIntoView({behavior:'smooth',block:'center'});});}
  window.TTC_monta=monta;
  document.querySelectorAll('[data-calcolatore]').forEach(function(box){
    var D=JSON.parse(document.getElementById(box.dataset.calcolatore).textContent);
    var sel=box.querySelector('[name=dest]');
    if(sel){sel.innerHTML=D.map(function(R,i){return '<option value="'+i+'">'+esc(R.name+(R.country!==R.name?' ('+R.country+')':''))+'</option>';}).join('');
      var cur=function(){box.dataset.reset='1';box.dataset.cat='';var R=D[+sel.value];monta(box,R);
        var l=box.querySelector('[data-link]');if(l){l.href=l.dataset.base+R.slug+'/';l.querySelector('span').textContent='Full rules and official source for '+R.name;}};
      sel.addEventListener('change',cur);cur();}
    else monta(box,D[0]);});
  document.querySelectorAll('[data-filtro]').forEach(function(inp){var lista=document.getElementById(inp.dataset.filtro);
    inp.addEventListener('input',function(){var v=inp.value.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');
      [].forEach.call(lista.children,function(a){var t=a.textContent.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');a.hidden=v&&t.indexOf(v)<0;});});});
  var src=document.querySelectorAll('input[name=source]');var ref='';try{var qs=new URLSearchParams(location.search);ref=qs.get('ref')||document.referrer||'direct';}catch(e){ref='direct';}
  src.forEach(function(i){i.value=String(ref).slice(0,200);});
  document.querySelectorAll('form.ajax').forEach(function(form){form.addEventListener('submit',function(ev){ev.preventDefault();
    var err=form.querySelector('[data-errore]');err.hidden=true;if(!form.checkValidity()){form.reportValidity();return;}
    var bt=form.querySelector('button');bt.disabled=true;
    fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(new FormData(form)).toString()})
    .then(function(r){if(!r.ok)throw new Error(r.status);form.hidden=true;form.parentNode.querySelector('[data-ok]').hidden=false;})
    .catch(function(){err.hidden=false;bt.disabled=false;});});});
})();
"""

# Ricerca su tutte le comuni francesi: carica /data/fr.json solo quando serve.
FR_JS = r"""
(function(){
  var box=document.getElementById('fr-cerca');if(!box)return;
  var inp=box.querySelector('input[type=search]'),res=box.querySelector('.risultati-fr'),det=document.getElementById('fr-dettaglio');var DATA=null,caricando=false;
  function norm(s){return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,' ').trim();}
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  var attesa=null;
  function carica(cb){if(DATA)return cb();attesa=cb;if(caricando)return;caricando=true;res.innerHTML='<p class="small">Loading the list of 10,900 towns…</p>';
    fetch(box.dataset.url).then(function(r){return r.json();}).then(function(d){DATA=d;d.c.forEach(function(c){c.push(norm(c[1]));});if(attesa)attesa();})
    .catch(function(){res.innerHTML='<p class="errore">Could not load the list. Please try again.</p>';caricando=false;});}
  function regola(c){var v=DATA.v[c[3]],cats=[],tar=[],cap=0;
    DATA.cat.forEach(function(k,i){var r=v[i];if(!r)return;if(r[1]==='€'&&r[0]!==null)cap=Math.max(cap,r[0]);cats.push({id:k[0],label:k[1]});
      tar.push({cat:k[0],dal:DATA.anno+'-01-01',al:DATA.anno+'-12-31',fr:{t:r[0],u:r[1],tot:r[2],add:r[3],reg:r[4],per:r[5]}});});
    return {name:c[1],country:'France',currency:'EUR',tipo:'france',categorie:cats,tariffe:tar,cap:cap,esenti_sotto_eta:18,
      etichetta_prezzo:'Price per night for the accommodation, excluding taxes (only for unclassified accommodation)'};}
  function mostra(c){
    if(c[4]==='C'){det.innerHTML='<div class="card"><h2 style="margin-top:0">'+esc(c[1])+'</h2><p>The official file has conflicting lines for this town, so we do not show a rate. Please check with the town hall or tourist office.</p></div>';return;}
    var R=regola(c);var righe=R.tariffe.map(function(t){var lab=R.categorie.filter(function(x){return x.id===t.cat;})[0].label;var fr=t.fr;
      var tot=fr.u==='%'?(num(fr.t)+'% of the price per person (max '+soldi(r2(R.cap*(1+fr.add/100)),'EUR')+')'):soldi(fr.tot,'EUR');
      if(fr.reg==='F')tot+=' (flat-rate: paid by the host)';return '<tr><td>'+esc(lab)+'</td><td><strong>'+tot+'</strong></td></tr>';}).join('');
    det.innerHTML='<div class="card"><h2 style="margin-top:0">'+esc(c[1])+' ('+esc(DATA.dep[c[2]]||c[2])+') tourist tax 2026</h2>'+
      '<div class="tab"><table><thead><tr><th>Accommodation</th><th>Total per person per night (incl. additional taxes)</th></tr></thead><tbody>'+righe+'</tbody></table></div>'+
      '<p class="fonte">Source: <a href="'+esc(DATA.fonte)+'" rel="noopener">DGFiP open dataset "Tarifs taxe de séjour – DELTA"</a> (Licence Ouverte 2.0), 2026 rates, dataset updated '+esc(DATA.mod)+', checked '+esc(DATA.chk)+'.</p>'+
      '<div id="fr-calc"></div></div>';
    var tpl=document.getElementById('tpl-calc');var nodo=tpl.content.cloneNode(true);document.getElementById('fr-calc').appendChild(nodo);
    var cb=document.querySelector('#fr-calc [data-calc]');cb.dataset.cat=R.categorie.some(function(x){return x.id==='h3';})?'h3':'';window.TTC_monta(cb,R);
    det.scrollIntoView({behavior:'smooth',block:'start'});}
  function cerca(){var v=norm(inp.value);if(v.length<2){res.innerHTML='';return;}
    carica(function(){var out=[];for(var i=0;i<DATA.c.length&&out.length<12;i++){var c=DATA.c[i];if(c[c.length-1].indexOf(v)===0)out.push(c);}
      if(out.length<12)for(var j=0;j<DATA.c.length&&out.length<12;j++){var c2=DATA.c[j];if(c2[c2.length-1].indexOf(v)>0&&out.indexOf(c2)<0)out.push(c2);}
      res.innerHTML=out.length?'':'<p class="small">No town with 2026 rates in the official file matches "'+esc(inp.value)+'". It may not levy the tax, or its rate may date from an earlier year: check with the town hall.</p>';
      out.forEach(function(c){var b=document.createElement('button');b.type='button';b.textContent=c[1]+' ('+(DATA.dep[c[2]]||c[2])+')';b.addEventListener('click',function(){mostra(c);});res.appendChild(b);});});}
  inp.addEventListener('input',cerca);inp.addEventListener('focus',function(){carica(cerca);},{once:true});
})();
"""

URLS = []
AD = '<div class="ad-slot" aria-hidden="true"></div>'
AVVISO = ('<p class="avviso"><strong>Not tax advice.</strong> Tourist taxes are set by local or national authorities and can change. '
          'They are usually collected by your hotel or host, who applies the official rules: check the final amount with your accommodation.</p>')


def pagina(percorso, titolo, descrizione, corpo, briciole=None, indicizza=True, extra_js="", jsonld_extra=None, testata="", classe=""):
    file = percorso if percorso.endswith(".html") else (percorso + "index.html")
    profondita = file.count("/")
    rel = "../" * profondita or "./"
    url_pag = URL_SITO + "/" + (percorso if not percorso.endswith("index.html") else percorso[:-10])
    if indicizza:
        URLS.append(percorso)
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": NOME, "url": URL_SITO + "/"}] if percorso == "" else []
    bc = ""
    if briciole:
        voci = [{"@type": "ListItem", "position": 1, "name": "Home", "item": URL_SITO + "/"}]
        for i, (n, p) in enumerate(briciole, start=2):
            voci.append({"@type": "ListItem", "position": i, "name": n, "item": URL_SITO + "/" + p})
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": voci})
        bc = ('<nav class="briciole" aria-label="Breadcrumb"><a href="' + rel + '">Home</a>' +
              "".join(f' › <a href="{rel}{p}">{escape(n)}</a>' for n, p in briciole[:-1]) + f" › {escape(briciole[-1][0])}</nav>")
    if jsonld_extra:
        ld.append(jsonld_extra)
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    robots = "" if indicizza else '<meta name="robots" content="noindex">'
    alt = (f'<link rel="alternate" hreflang="en" href="{url_pag}"><link rel="alternate" hreflang="x-default" href="{url_pag}">'
           if indicizza else "")
    voci_menu = [("", "Calculator"), ("tourist-taxes-europe-2026/", "Europe 2026"), ("france/", "France"), ("country/japan/", "Japan"),
                 ("how-tourist-taxes-work/", "How it works"), ("about/", "Sources")]
    menu = "".join(f'<a href="{rel}{u}"{" aria-current=\"page\"" if u == percorso else ""}>{t}</a>' for u, t in voci_menu)
    testo = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="{GOOGLE_VERIFICA}">
<title>{escape(titolo)}</title>
<meta name="description" content="{escape(descrizione)}">
<link rel="canonical" href="{url_pag}">
{alt}
<meta property="og:title" content="{escape(titolo)}">
<meta property="og:description" content="{escape(descrizione)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url_pag}">
<meta property="og:site_name" content="{NOME}">
<meta property="og:image" content="{URL_SITO}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{NOME}: official tourist tax rates and a calculator">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#B23F1B" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#15110E" media="(prefers-color-scheme: dark)">
<meta name="color-scheme" content="light dark">
{robots}
<link rel="icon" href="{FAVICON}">
<link rel="preload" href="/assets/fonts/bricolage-grotesque-700.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS}</style>
{ld_html}
</head>
<body class="{classe}">
{SPRITE}
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
<a class="logo" href="{rel}">{MARCHIO}<span>Tourist Tax <b>Calculator</b></span></a>
<nav class="menu" aria-label="Menu">{menu}</nav>
<details class="nav-m"><summary aria-label="Open the menu">{ico("menu")}Menu</summary><nav aria-label="Menu">{menu}</nav></details>
</div></header>
<main id="main">
{testata}
<div class="wrap">
{bc}
{corpo}
</div>
</main>
<footer><div class="wrap">
<div class="f-grid"><div>
<a class="logo" href="{rel}">{MARCHIO}<span>Tourist Tax <b>Calculator</b></span></a>
<p><strong>{NOME}</strong> is an independent site, not affiliated with any government or tax authority. Every rate comes from an official source (law, ordinance, tax authority page or official open data) linked under the figure with the date we checked it.
<strong>Tourist taxes are set by local or national authorities and can change. Your accommodation collects the tax: check the exact amount with them.</strong> Nothing on this site is tax or legal advice.</p>
</div><div>
<h2>Explore</h2>
<ul><li><a href="{rel}about/">About and sources</a></li><li><a href="{rel}contact/">Contact</a></li><li><a href="{rel}privacy.html">Privacy</a></li><li><a href="{rel}how-tourist-taxes-work/">How tourist taxes work</a></li><li><a href="{rel}tourist-taxes-europe-2026/">Tourist taxes in Europe 2026</a></li><li><a href="{rel}contact/?ref=spotted-a-change">Spotted a change? Tell us</a></li></ul>
</div></div>
{blocco_altri(ALTRI_SITI, "Other useful tools for your trip")}
<p class="f-base">Official sources only · the calculator runs in your browser.</p>
</div></footer>
<script>{MOTORE_JS}{APP_JS}{extra_js}</script>
{SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")


def modulo_calcolatore(id_dati, con_destinazione=False, rel="", cat_default=""):
    sel = (f'<label class="pieno"><span class="lt">{ico("pin")}Destination</span><select name="dest"></select></label>' if con_destinazione else "")
    link = (f'<p class="calc-link"><a data-link data-base="{rel}" href="{rel}"><span>Full rules and official source</span>{ico("arrow")}</a></p>' if con_destinazione else "")
    return f"""<div class="card calc" data-calcolatore="{id_dati}" data-calc data-cat="{escape(cat_default)}">
<div class="calc-grid">
<form autocomplete="off">
<div class="campi">
{sel}
<label class="pieno" data-campo="cat"><span class="lt">{ico("bed")}Type of accommodation</span><select name="cat"></select></label>
<label class="pieno" data-campo="zona" hidden><span class="lt">{ico("city")}Municipality</span><select name="zona"></select></label>
<label data-campo="checkin"><span class="lt">{ico("calendar")}Check-in date</span><input type="date" name="checkin"></label>
<label data-campo="notti"><span class="lt">{ico("moon")}Nights</span><input type="number" name="notti" min="1" max="365" value="3" inputmode="numeric"></label>
<label data-campo="paganti"><span class="lt">{ico("users")}<span data-lab="paganti">Guests</span></span><input type="number" name="paganti" min="0" max="50" value="2" inputmode="numeric"></label>
<label data-campo="esenti"><span class="lt">{ico("child")}<span data-lab="esenti">Children</span></span><input type="number" name="esenti" min="0" max="50" value="0" inputmode="numeric"></label>
<label data-campo="stanze"><span class="lt">{ico("door")}Rooms or units</span><input type="number" name="stanze" min="1" max="50" value="1" inputmode="numeric"></label>
<label class="pieno" data-campo="prezzo"><span class="lt">{ico("tag")}<span data-lab="prezzo">Price per night</span></span><input type="number" name="prezzo" min="0" step="any" value="150" inputmode="decimal"></label>
</div>
</form>
<div class="calc-out">
<div class="risultato" data-out aria-live="polite"><noscript>Turn on JavaScript to use the calculator. The rate table below shows every official rate.</noscript></div>
{link}
</div>
<button type="button" class="r-bar" data-bar hidden><span class="r-bar-tot"></span><span class="r-bar-info"></span><span class="r-bar-go">Details{ico("arrow")}</span></button>
</div>
</div>"""


CAMPI_MOTORE = ("name", "country", "slug", "currency", "tipo", "categorie", "tariffe", "esenti_sotto_eta", "max_notti", "max_soggiorno",
                "riduzioni", "etichetta_prezzo", "cap", "prezzo_esempio", "esente_oltre_mesi", "in_vigore_dal", "in_vigore_testo",
                "zone", "supplementi")


def blocco_dati(id_, dati):
    dati = [dict({k: d[k] for k in CAMPI_MOTORE if k in d}, **({"in_vigore_testo": data_lunga(d["in_vigore_dal"])} if d.get("in_vigore_dal") else {}))
            for d in dati]
    return (f'<script type="application/json" id="{id_}">' +
            json.dumps(dati, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>")


def box_affiliati():
    """Riquadro affiliati: vuoto (non mostrato) finché dati/affiliati.json non ha URL."""
    voci = [v for k, v in AFFILIATI.items() if not k.startswith("_") and isinstance(v, dict) and v.get("url")]
    if not voci:
        return ""
    righe = "".join(f'<li><a href="{escape(v["url"])}" rel="sponsored noopener" target="_blank">{escape(v["titolo"])}</a> '
                    f'<span class="small">{escape(v.get("nome", ""))} {escape(v["testo"])}</span></li>' for v in voci)
    return (f'<section class="card" style="margin-top:22px"><h2 style="margin-top:0">Planning your stay</h2><ul style="margin:0 0 8px;padding-left:20px">{righe}</ul>'
            '<p class="small" style="margin:0">Some of these are affiliate links: if you book through them we may earn a small commission, at no extra cost to you.</p></section>')


def fonti_html(R):
    out = []
    for f in R["fonti"]:
        stato = "" if f["http"] == 200 else f" (the site blocks automated reading: HTTP {f['http']}; checked by hand)"
        out.append(f'<li><a href="{escape(f["url"])}" rel="noopener">{escape(f["titolo"])}</a> – {escape(f["formato"])}, checked {data_lunga(f["controllato_il"])}{stato}'
                   + (f'<br><span class="small">{escape(f["nota"])}</span>' if f.get("nota") else "") + "</li>")
    return "<ul>" + "".join(out) + "</ul>"


def fonte_breve(R):
    f = next((x for x in R["fonti"] if x["http"] == 200), R["fonti"][0])
    return (f'<p class="fonte">Official source: <a href="{escape(f["url"])}" rel="noopener">{escape(f["titolo"])}</a> · checked on '
            f'{data_lunga(f["controllato_il"])}</p>')


# ---------------------------------------------------------------- esempio statico (stesso motore)
def esempio(R):
    cat = R["categorie"][0]["id"]
    if R["tipo"] == "france":
        cat = "h3" if any(c["id"] == "h3" for c in R["categorie"]) else cat
    giorno = OGGI.isoformat()
    if not any((not t.get("dal") or t["dal"] <= giorno) and (not t.get("al") or giorno <= t["al"]) for t in R["tariffe"]):
        future = sorted(t["dal"] for t in R["tariffe"] if t.get("dal") and t["dal"] > giorno)
        giorno = future[0] if future else giorno
    prezzo = R.get("prezzo_esempio", 150)
    o = calcola(R, cat, giorno, 3, 2, 0, 1, prezzo)
    lab = next(c["label"] for c in R["categorie"] if c["id"] == cat)
    val = R["currency"]
    chi = {"per_room": "1 room", "percent": f"price {soldi(prezzo, val)} per night", "bands": f"2 guests, room price {soldi(prezzo, val)} per night",
           "per_trip": "2 travellers"}.get(R["tipo"], "2 adults")
    if R["tipo"] == "per_trip":
        return f"Example: 2 travellers pay <strong>{soldi(o['totale'], val)}</strong> in total."
    return (f"Example: {chi}, 3 nights from {data_lunga(giorno)}, {escape(lab)} → "
            f"<strong>{soldi(o['totale'], val)}</strong> in total.")


# ---------------------------------------------------------------- pagine
def titolo_dest(nome):
    return f"{nome} tourist tax {ANNO}: how much per night (calculator)"


def regole_testo(R):
    tipo = R["tipo"]
    parti = {"per_person": ["a fixed amount per person per night" + (" by accommodation type" if len(R["categorie"]) > 1 else "")],
             "per_room": ["a fixed amount per room per night by accommodation type"],
             "percent": ["a percentage of the price of the stay"],
             "bands": ["a fixed amount per person per night set by price band"],
             "per_trip": ["a one-off amount per traveller"]}[tipo]
    if any(t.get("mesi") for t in R["tariffe"]) or R.get("riduzioni"):
        parti.append("seasons and reductions")
    if len({(t.get("dal"), t.get("al")) for t in R["tariffe"]}) > 1 and tipo != "per_room":
        parti.append("rate changes by date")
    if R.get("max_notti") or any(c.get("max_notti") for c in R["categorie"]):
        parti.append("maximum taxable nights")
    if R.get("esenti_sotto_eta"):
        parti.append(f"exemption under {R['esenti_sotto_eta']}")
    if R.get("max_soggiorno") or R.get("esente_oltre_mesi"):
        parti.append("the limit on the length of stay")
    if R.get("zone"):
        parti.append("municipal surcharges")
    return ", ".join(parti)


def tabella_supplementi(R):
    if not R.get("supplementi"):
        return ""
    cat = {c["id"]: c["label"] for c in R["categorie"]}
    zone = {z["id"]: z["label"] for z in R["zone"]}
    righe = "".join(f"<tr><td>{escape(zone[t['zona']])}</td><td>{escape(cat[t['cat']])}</td><td>{escape(periodo_testo(t))}</td>"
                    f"<td><strong>{soldi(t['valore'], R['currency'])}</strong></td></tr>" for t in R["supplementi"])
    return ('<h2>Municipal surcharges (from 1 October 2026)</h2><p>Added per person per night on top of the rate above, in these municipalities only '
            '(official ATC table; a category not listed has no surcharge there).</p>'
            f'<div class="tab"><table><thead><tr><th>Municipality</th><th>Accommodation</th><th>Period</th><th>Surcharge</th></tr></thead><tbody>{righe}</tbody></table></div>')


TIPO_CHIP = {"per_person": ("users", "Per person per night"), "per_room": ("door", "Per room per night"),
             "percent": ("percent", "% of the room price"), "bands": ("bands", "Set by price band"),
             "per_trip": ("plane", "Once per trip"), "france": ("users", "Per person per night")}


def chips(R, paese, luogo=""):
    """Etichette rapide del riquadro di sintesi, ricavate dalle regole (nessun dato nuovo)."""
    i, t = TIPO_CHIP[R["tipo"]]
    out = [f"<li>{ico(i)}{t}</li>"]
    if R.get("max_notti"):
        out.append(f"<li>{ico('moon')}Max {R['max_notti']} taxable nights</li>")
    if R.get("esenti_sotto_eta"):
        out.append(f"<li>{ico('child')}Under {R['esenti_sotto_eta']}s exempt</li>")
    out.append(f"<li>{ico('pin')}{escape(luogo + ', ' if luogo else '')}{escape(paese)}</li>")
    return '<ul class="chips">' + "".join(out) + "</ul>"


def formula_html(R):
    return (f'<details class="formula"><summary>{ico("calc")}Formula used</summary><p>{escape(formula(R))}</p></details>')


def pagina_destinazione(R):
    slug = R["slug"]
    rel = "../"
    val = R["currency"]
    cat_def = R["categorie"][0]["id"]
    id_dati = "regola"
    paese = PAESI[R["country_slug"]]
    note = "".join(f"<li>{escape(n)}</li>" for n in R["note"])
    esenzioni = ("<ul>" + "".join(f"<li>{escape(e)}</li>" for e in R["esenzioni"]) + "</ul>") if R["esenzioni"] else \
        "<p>We list exemptions only when the official source states them: see the practical notes above, and ask your accommodation.</p>"
    sorelle = [d for d in DEST if d["country_slug"] == R["country_slug"] and d["slug"] != slug]
    link_sorelle = ""
    if sorelle:
        link_sorelle = (f'<h2>Other destinations in {escape(paese)}</h2><div class="griglia">' +
                        "".join(f'<a href="{rel}{d["slug"]}/">{escape(d["name"])}<small>{escape(riassunto(d))}</small></a>' for d in sorelle) + "</div>")
    corpo = f"""<section class="hero">{h1_diviso(titolo_dest(R['name']))}</section>
<section class="card summary" aria-label="Summary">
<div><p class="cifra"><span class="lab">{ico("receipt")}{escape(R['name'])} {ANNO}</span><span class="sr">: </span><strong>{escape(riassunto(R))}</strong></p>
{chips(R, paese)}</div>
<div><p class="lead">{escape(R['official_name'])}. The calculator below uses the official rates and rules: {escape(regole_testo(R))}.</p>
{fonte_breve(R)}</div>
</section>
{modulo_calcolatore(id_dati, rel=rel, cat_default=cat_def)}
{f'<p class="avviso">{escape(R["avviso_verifica"])}</p>' if R.get("avviso_verifica") else ""}
{formula_html(R)}
<p class="esempio">{esempio(R)}</p>
{AVVISO}
{AD}
<h2>Official rates</h2>
{tabella_tariffe(R)}
{fonte_breve(R)}
{tabella_supplementi(R)}
<h2>Practical notes</h2>
<ul>{note}</ul>
<p><strong>Who collects it:</strong> {escape(R['chi_riscuote'])}</p>
<h2>Exemptions (official)</h2>
{esenzioni}
<h2>Official sources</h2>
{fonti_html(R)}
<p class="small">Spotted a change in the official rate? <a href="{rel}contact/?ref={slug}">Tell us</a>.</p>
{box_affiliati()}
{link_sorelle}
<p><a href="{rel}country/{R['country_slug']}/">All tourist taxes in {escape(paese)}</a> · <a href="{rel}tourist-taxes-europe-2026/">Tourist taxes in Europe {ANNO}</a></p>
{blocco_dati(id_dati, [R])}"""
    descr = f"{R['name']} tourist tax {ANNO}: {riassunto(R)}. Official rates, rules and a calculator, with the official source and the date we checked it."
    pagina(f"{slug}/", titolo_dest(R["name"]), descr, corpo,
           briciole=[(paese, f"country/{R['country_slug']}/"), (R["name"], f"{slug}/")])


def fr_slug_map():
    m, usati = {}, set()
    for code, nome, dep, _ in FR_TOP["comuni"]:
        s = slugify(nome)
        if s in usati:
            s = f"{s}-{dep.lower()}"
        usati.add(s)
        m[code] = s
    return m


FR_SLUG = {}


def pagina_francia_comune(code):
    R = fr_regola(code)
    R["slug"] = "france/" + FR_SLUG[code]
    rel = "../../"
    dep = R["dep_nome"] or R["dep"]
    fonte = (f'<p class="fonte">Official source: <a href="{escape(FR["fonte"])}" rel="noopener">DGFiP open dataset "Tarifs taxe de séjour – DELTA"</a> '
             f'(Licence Ouverte 2.0), {ANNO} rates for {escape(R["nome_dgfip"])} (INSEE code {code}), dataset updated {data_lunga(FR["dataset_modificato"])}, '
             f'checked on {data_lunga(FR["controllato_il"])}</p>')
    vicini = [c for c in FR_TOP["comuni"] if c[2] == R["dep"] and c[0] != code][:8]
    link_vicini = ""
    if vicini:
        link_vicini = (f"<h2>Other towns in {escape(dep)}</h2><div class=\"griglia\">" +
                       "".join(f'<a href="{rel}france/{FR_SLUG[c[0]]}/">{escape(c[1])}</a>' for c in vicini) + "</div>")
    seas = any(t["fr"]["per"] and t["fr"]["per"] != ["01-01 - 31-12"] for t in R["tariffe"])
    corpo = f"""<section class="hero">{h1_diviso(titolo_dest(R['name']))}</section>
<section class="card summary" aria-label="Summary">
<div><p class="cifra"><span class="lab">{ico("receipt")}{escape(R['name'])} {ANNO}</span><span class="sr">: </span><strong>{escape(riassunto(R))}</strong></p>
{chips(R, "France", dep)}</div>
<div><p class="lead">Taxe de séjour in {escape(R['name'])} ({escape(dep)}), {ANNO}: the official municipal rates plus the additional departmental and regional taxes, from the French tax administration's open data.</p>
{fonte}</div>
</section>
{modulo_calcolatore('regola', rel=rel, cat_default='h3')}
{formula_html(R)}
<p class="esempio">{esempio(R)}</p>
{AVVISO}
{AD}
<h2>Official rates {ANNO}</h2>
{tabella_tariffe(R)}
{fonte}
<h2>Practical notes</h2>
<ul><li>The tax is charged per person and per night by the accommodation, on top of the room price{' during the collection period shown in the table' if seas else ''}.</li>
<li>Under-18s are exempt by law (art. L. 2333-31 of the General Code of Local Authorities), as are seasonal workers employed in the town and people in emergency or temporary housing.</li>
<li>For unclassified accommodation (most Airbnb-type rentals) the tax is a percentage of the price per person per night excluding taxes, capped at the highest rate adopted by the town ({soldi(R['cap'], 'EUR')} before additional taxes).</li>
<li>Additional taxes are set by the department and, in some regions, by the region or transport authority: they are already included in the totals.</li></ul>
<p class="small">How the cap and the per-person cost work is explained in the official guide of the French Directorate General for Local Authorities (<a href="https://www.collectivites-locales.gouv.fr/gerer-les-finances-publiques-locales/fiscalite-locale/fiscalite-indirecte-locale/taxe-de-sejour/guide-pratique-les-taxes-de-sejour" rel="noopener">guide pratique, fiches 4 and 6, June 2026</a>).</p>
<p class="small">Spotted a change? <a href="{rel}contact/?ref=fr-{code}">Tell us</a>.</p>
{box_affiliati()}
{link_vicini}
<p><a href="{rel}france/">Search all 10,900 French towns</a> · <a href="{rel}tourist-taxes-europe-2026/">Tourist taxes in Europe {ANNO}</a></p>
{blocco_dati('regola', [R])}"""
    descr = f"{R['name']} tourist tax (taxe de séjour) {ANNO}: {riassunto(R)}. Official DGFiP rates and a calculator."
    pagina(f"france/{FR_SLUG[code]}/", titolo_dest(R["name"]), descr, corpo,
           briciole=[("France", "france/"), (R["name"], f"france/{FR_SLUG[code]}/")])


def pagina_francia():
    rel = "../"
    top = FR_TOP["comuni"]
    griglia = "".join(f'<a href="{rel}france/{FR_SLUG[c[0]]}/">{escape(c[1])}<small>{escape(dep_nome(c[2]))}</small></a>' for c in top)
    parigi = fr_regola("75056")
    corpo = f"""<section class="hero">{h1_diviso(f"France tourist tax {ANNO}: rates for every town (taxe de séjour calculator)")}
<p class="lead">In France each town (or group of towns) sets its own taxe de séjour per person per night, within a national scale. Search any of the {len(FR['comuni']):,} towns with {ANNO} rates in the official DGFiP file, or open one of the {len(top)} towns with the most tourist accommodation places (INSEE 2026).</p>
<p class="fonte">Source: <a href="{escape(FR['fonte'])}" rel="noopener">DGFiP open dataset "Tarifs taxe de séjour – DELTA"</a> (Licence Ouverte 2.0, {ANNO} rates, updated {data_lunga(FR['dataset_modificato'])}), checked on {data_lunga(FR['controllato_il'])}.</p>
</section>
<section class="card" id="fr-cerca" data-url="{rel}data/fr.json" style="margin-top:18px;box-shadow:var(--sh-2)"><label for="fr-q">{ico("pin")}Find your town</label>
<div class="cerca-box">{ico("search")}<input id="fr-q" class="cerca" type="search" placeholder="Type a town name, e.g. Nice, Chamonix, Biarritz" autocomplete="off"></div>
<div class="risultati-fr" aria-live="polite"></div></section>
<div id="fr-dettaglio" style="margin-top:14px"></div>
<template id="tpl-calc">{modulo_calcolatore('regola-vuota')}</template>
{AVVISO}
{AD}
<h2>National scale {ANNO} (per person per night, before additional taxes)</h2>
<p>Towns choose a rate between the legal minimum and maximum for each category; unclassified accommodation pays 1% to 5% of the price per person, capped. In Île-de-France a 200% additional tax for public transport and a 15% tax for the Grand Paris projects apply on top, plus 10% for the department; other departments and regions may add their own.</p>
<p class="small">Official national scale: <a href="https://entreprendre.service-public.gouv.fr/vosdroits/F31635" rel="noopener">Service Public Entreprendre – Taxe de séjour touristique : quels sont les tarifs ? (verified 1 January 2026)</a>, checked on {data_lunga('2026-10-10')}.</p>
<h2>Example: Paris {ANNO}</h2>
{tabella_tariffe(parigi)}
<p><a href="{rel}france/paris/">Paris tourist tax {ANNO} with calculator</a></p>
<h2>The {len(top)} towns with the most tourist accommodation</h2>
<p class="small">{escape('Chosen with an official criterion: the towns with the most tourist accommodation places (hotel rooms, other tourist accommodation units and campsite pitches) in INSEE 2026 data, among those with 2026 rates in the DGFiP file.')}</p>
<div class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="Filter the list" data-filtro="fr-lista" aria-label="Filter the list of towns"></div>
<div class="griglia sez" id="fr-lista">{griglia}</div>
<h2>Towns not in the list</h2>
<p>Some large cities (for example Nice, Marseille and Toulouse) have no line with a {ANNO} effective date in the official DGFiP file: their rates were adopted in earlier years. We do not show those older rates; check with the town hall or tourist office.</p>
{blocco_dati('regola-vuota', [])}"""
    pagina("france/", f"France tourist tax {ANNO}: taxe de séjour by town (calculator)",
           f"Taxe de séjour {ANNO} for {len(FR['comuni']):,} French towns from the official DGFiP open data: search your town and calculate the tax.",
           corpo, briciole=[("France", "france/")], extra_js=FR_JS)


def pagina_paese(slug):
    rel = "../../"
    nome = PAESI[slug]
    dd = [d for d in DEST if d["country_slug"] == slug]
    righe = "".join(f'<tr><td><a href="{rel}{d["slug"]}/">{escape(d["name"])}</a></td><td>{escape(riassunto(d))}</td>'
                    f'<td>{d.get("max_notti") or "–"}</td><td>{("under " + str(d["esenti_sotto_eta"])) if d.get("esenti_sotto_eta") else "–"}</td></tr>' for d in dd)
    testo_extra = {
        "greece": "Greece has one national fee, the climate crisis resilience fee, charged per room per night with a high-season and a low-season rate. The amount is the same on every island and in Athens.",
        "spain": "Spain has no national tourist tax. Catalonia (with a Barcelona city surcharge) and the Balearic Islands levy their own regional taxes, covered here.",
        "turkey": "Turkey's accommodation tax is national: a percentage of the accommodation price excluding VAT, the same everywhere.",
        "japan": "In Japan accommodation taxes are set by prefectures and cities. Some places have both (for example Hokkaido and Sapporo, Nagano and Hakuba). The Ministry of Internal Affairs and Communications publishes the official list of all of them.",
        "italy": "In Italy each city sets its own imposta (or contributo) di soggiorno per person per night, with its own maximum nights and age exemptions.",
    }.get(slug, "")
    corpo = f"""<section class="hero"><h1>Tourist taxes in {escape(nome)} {ANNO}</h1>
<p class="lead">{escape(testo_extra) if testo_extra else f'Official tourist tax rates in {escape(nome)}, with a calculator for each destination.'}</p></section>
<div class="tab"><table><thead><tr><th>Destination</th><th>Rate {ANNO}</th><th>Max taxable nights</th><th>Exempt</th></tr></thead><tbody>{righe}</tbody></table></div>
{AVVISO}
{AD}
<h2>Calculators</h2>
<div class="griglia">{''.join(f'<a href="{rel}{d["slug"]}/">{escape(d["name"])}<small>{escape(riassunto(d))}</small></a>' for d in dd)}</div>
<p><a href="{rel}tourist-taxes-europe-2026/">Tourist taxes in Europe {ANNO}</a> · <a href="{rel}">All destinations</a></p>"""
    pagina(f"country/{slug}/", f"Tourist taxes in {nome} {ANNO}: rates and calculators",
           f"Official tourist tax rates in {nome} for {ANNO}, destination by destination, with calculators and official sources.",
           corpo, briciole=[(nome, f"country/{slug}/")])


def n_regole():
    return len({d.get("gruppo") or d["slug"] for d in DEST})


def ultimo_controllo():
    date_ = [f["controllato_il"] for d in DEST for f in d["fonti"]] + [FR["controllato_il"]]
    return data_lunga(max(date_))


TIPI_HOME = [("users", "Per person per night", "Rome, Barcelona, Prague, most French towns"),
             ("door", "Per room per night", "Greece and Iceland"),
             ("percent", "% of the room price", "Amsterdam, Berlin, Vienna, Edinburgh, Turkey"),
             ("bands", "Price bands", "Kyoto, Tokyo, Sapporo, Hakuba"),
             ("plane", "Once per trip", "Bali")]


def home():
    gruppi = {}
    for d in DEST:
        gruppi.setdefault(d["country_slug"], []).append(d)
    griglia = "".join(f'<a href="{d["slug"]}/">{escape(d["name"])}<small>{escape(PAESI[d["country_slug"]])} · {escape(riassunto(d, seguito=False))}</small></a>' for d in DEST)
    griglia += (f'<div class="fr-card"><a href="france/">{ico("search")}France: {len(FR["comuni"]):,} towns{ico("arrow")}</a>'
                f'<p class="fr-top" style="margin:0">' + " · ".join(f'<a href="france/{FR_SLUG[c[0]]}/">{escape(c[1])}</a>' for c in FR_TOP["comuni"][:24]) + '</p></div>')
    tipi = "".join(f'<li><span class="ic">{ico(i)}</span><strong>{t}</strong>{e}</li>' for i, t, e in TIPI_HOME)
    testata = f"""<div class="band"><div class="wrap band-in">{DECO}
<section class="hero">{h1_diviso(f"Tourist tax calculator {ANNO}: how much will you pay per night?")}
<p class="sub">Official {ANNO} rates for {len(DEST)} destinations and {len(FR['comuni']):,} French towns, applied to your stay.</p>
<p class="trust"><span>{ico("shield")}Official sources · last checked {ultimo_controllo()}</span><span>{ico("calc")}Runs in your browser</span></p></section>
{modulo_calcolatore('tutte', con_destinazione=True, rel='')}
</div></div>"""
    corpo = f"""<div class="card callout">{'<span class="ic">' + ico("search") + '</span>'}<p><strong>France:</strong> <a href="france/">search your town among {len(FR['comuni']):,} French towns</a>.</p></div>
{AVVISO}
{AD}
<h2>What the calculator covers</h2>
<p class="lead">Official tourist tax rates on {len(DEST)} destination pages (based on {n_regole()} official rule sets, since Greece, Turkey and the Balearic Islands each have one rule for many places) and for {len(FR['comuni']):,} French towns, with a calculator that applies the real rules: rate by hotel category, percentage of the room price, price bands, seasons, maximum taxable nights and age exemptions. Every figure links to its official source.</p>
<ul class="tipi">{tipi}</ul>
<div class="sez-h"><h2>Find a destination</h2></div>
<div class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="Search a place" data-filtro="lista-dest" aria-label="Search destinations"></div>
<div class="griglia sez dest" id="lista-dest">{griglia}</div>
<p><a href="france/">All French towns</a> · <a href="tourist-taxes-europe-2026/">Tourist taxes in Europe {ANNO}</a> · <a href="how-tourist-taxes-work/">How tourist taxes work</a></p>
<h2>Countries</h2>
<div class="griglia">{''.join(f'<a href="{"france" if s == "france" else "country/" + s}/">{escape(PAESI[s])}<small>{plur(len(gruppi.get(s, [])) if s != "france" else len(FR_TOP["comuni"]), "destination page")}</small></a>' for s in PAESI)}</div>
{box_affiliati()}
{blocco_dati('tutte', DEST)}"""
    pagina("", f"Tourist Tax Calculator {ANNO}: official rates per night for {len(DEST)} destination pages and 10,900 French towns",
           f"How much is the tourist tax? Official {ANNO} rates and a calculator for Barcelona, Mallorca, Greece, Turkey, Amsterdam, Rome, Kyoto, Paris and more, with sources.",
           corpo, testata=testata, classe="home")


def pagina_europa():
    rel = "../"
    righe = []
    for d in DEST:
        if d["country_slug"] not in EUROPA or d.get("gruppo") in ("greece", "turkey", "balearics") and d["slug"] not in ("athens", "turkey", "mallorca"):
            continue
        f = next((x for x in d["fonti"] if x["http"] == 200), d["fonti"][0])
        nome = {"athens": "Greece (all destinations)", "turkey": "Turkey (all destinations)", "mallorca": "Balearic Islands (Mallorca, Ibiza, Menorca, Formentera)"}.get(d["slug"], d["name"])
        righe.append(f'<tr><td><a href="{rel}{d["slug"]}/">{escape(nome)}</a></td><td>{escape(PAESI[d["country_slug"]])}</td><td>{escape(riassunto(d))}</td>'
                     f'<td>{d.get("max_notti") or "–"}</td><td>{("under " + str(d["esenti_sotto_eta"])) if d.get("esenti_sotto_eta") else "–"}</td>'
                     f'<td><a href="{escape(f["url"])}" rel="noopener">official</a>, {data_lunga(f["controllato_il"])}</td></tr>')
    parigi = fr_regola("75056")
    righe.insert(0, f'<tr><td><a href="{rel}france/paris/">Paris</a></td><td>France</td><td>{escape(riassunto(parigi))}</td><td>–</td><td>under 18</td>'
                    f'<td><a href="{escape(FR["fonte"])}" rel="noopener">official</a>, {data_lunga(FR["controllato_il"])}</td></tr>')
    corpo = f"""<section class="hero">{h1_diviso(f"Tourist taxes in Europe {ANNO}: rates by city and country")}
<p class="lead">The official {ANNO} tourist tax in the European destinations we cover, side by side. Each row links to a calculator and to the official source, with the date we checked it.</p></section>
<div class="tab"><table><thead><tr><th>Destination</th><th>Country</th><th>Rate {ANNO}</th><th>Max nights</th><th>Exempt</th><th>Source</th></tr></thead><tbody>{''.join(righe)}</tbody></table></div>
<p class="small">"Rate" shows the rates in force on the date this page was generated. Some places change rates during the year (for example Vienna on 1 July, Catalonia and Barcelona on 1 April, Turkey on 1 May 2026): see each page.</p>
{AVVISO}
{AD}
<h2>Not covered yet</h2>
<p>We only publish a destination when we can read a complete official source. Not covered on the date we checked: Venice, Lisbon, Porto and the Algarve, Budapest, Dubrovnik and Split, Glasgow. See <a href="{rel}about/">About and sources</a>.</p>"""
    pagina("tourist-taxes-europe-2026/", f"Tourist taxes in Europe {ANNO}: city by city table (official rates)",
           f"Tourist taxes in Europe {ANNO}: official rates for Paris, Barcelona, Mallorca, Greece, Amsterdam, Berlin, Vienna, Prague, Edinburgh, Rome, Florence, Milan, Iceland and Turkey.",
           corpo, briciole=[(f"Tourist taxes in Europe {ANNO}", "tourist-taxes-europe-2026/")])


def pagina_come_funziona():
    rel = "../"
    corpo = f"""<section class="hero"><h1>How tourist taxes work</h1>
<p class="lead">A tourist tax (city tax, visitor levy, taxe de séjour, imposta di soggiorno, accommodation tax) is a charge on overnight stays set by a city, region or country. The rules differ a lot from place to place. These are the main types, with real examples from this site.</p></section>
<div class="testo">
<h2>1. A fixed amount per person per night</h2>
<p>The most common type. The amount usually depends on the hotel category (stars) or the type of accommodation. Examples: <a href="{rel}rome/">Rome</a>, <a href="{rel}florence/">Florence</a>, <a href="{rel}milan/">Milan</a>, <a href="{rel}barcelona/">Barcelona</a>, <a href="{rel}prague/">Prague</a>, and most <a href="{rel}france/">French towns</a>.</p>
<h2>2. A fixed amount per room per night</h2>
<p>Charged per room or apartment, whatever the number of guests. Examples: <a href="{rel}athens/">Greece</a> (climate resilience fee) and <a href="{rel}iceland/">Iceland</a>.</p>
<h2>3. A percentage of the room price</h2>
<p>Usually calculated on the price before VAT and without breakfast. Examples: <a href="{rel}amsterdam/">Amsterdam</a> 12.5%, <a href="{rel}berlin/">Berlin</a> 7.5%, <a href="{rel}vienna/">Vienna</a> 5%, <a href="{rel}edinburgh/">Edinburgh</a> 5%, <a href="{rel}turkey/">Turkey</a> and <a href="{rel}kutchan-niseko/">Kutchan (Niseko)</a>. In France, unclassified accommodation pays a percentage of the price per person, capped.</p>
<h2>4. Price bands</h2>
<p>A fixed amount per person that depends on how much the room costs per person per night. Examples: <a href="{rel}kyoto/">Kyoto</a>, <a href="{rel}tokyo/">Tokyo</a>, <a href="{rel}sapporo/">Sapporo</a>, <a href="{rel}hakuba/">Hakuba</a>.</p>
<h2>5. A one-off levy per trip</h2>
<p>Paid once, not per night. Example: <a href="{rel}bali/">Bali</a>.</p>
<h2>Seasons, maximum nights and exemptions</h2>
<ul><li><strong>Seasons:</strong> lower rates in low season (Balearic Islands -75% from November to April; Greece November-March rates).</li>
<li><strong>Maximum nights:</strong> many places stop charging after a number of nights (Barcelona and Florence 7, Rome 10, Edinburgh 5); the Balearics halve the tax from the 9th day.</li>
<li><strong>Age:</strong> children are often exempt, but the age limit varies (Rome under 10, Florence under 12, Balearics under 16, Barcelona under 17, France, Milan and Prague under 18). Japan and Amsterdam have no age exemption.</li>
<li><strong>Two layers:</strong> sometimes a region and a city both charge (Barcelona: Catalan rate + city surcharge; Sapporo: city + Hokkaido; France: town + department, sometimes region).</li></ul>
<h2>Who collects it and when</h2>
<p>In most places the accommodation collects the tax from the guest: for example in the Balearic Islands it must be charged before the end of the stay, and in Greece after the stay and before departure. In Kyoto it may already be included in what you paid to a booking site or travel company. Bali is different: you pay the levy on the official Love Bali portal or through its authorised agents. Always check the final amount with your accommodation.</p>
<h2>How we check the rates</h2>
<p>Every rate on this site comes from an official source: a law, an ordinance, a tax authority page or official open data. We show the link and the date we checked it under the figure. We re-check every quarter and before 1 January and 1 April, when many rates change. If we cannot read an official source, we do not publish the destination.</p>
</div>
{AVVISO}
{AD}"""
    pagina("how-tourist-taxes-work/", "How tourist taxes work: per person, per room, percentage and price bands",
           "How tourist taxes are calculated around the world: fixed per person, per room, percentage of the price, price bands, seasons, maximum nights and age exemptions.",
           corpo, briciole=[("How tourist taxes work", "how-tourist-taxes-work/")])


def about():
    rel = "../"
    elenco = "".join(f'<h3><a href="{rel}{d["slug"]}/">{escape(d["name"])}</a></h3>{fonti_html(d)}' for d in DEST)
    corpo = f"""<section class="hero"><h1>About {NOME} and our sources</h1></section><div class="testo">
<p>{NOME} is an independent project that collects official tourist tax rates and turns them into a simple calculator. We are not affiliated with any government, tax authority, hotel or booking site.</p>
<h2>Rules we follow</h2>
<ul><li>Every rate comes from an official source (law, ordinance, municipal/regional/national tax authority page or official open data). The link and the date we checked it are printed under the figure.</li>
<li>No blogs or aggregators are used as sources. If we cannot read an official source, the destination is not published.</li>
<li>Rates are set by local authorities and can change. The accommodation collects the tax and applies the official rules: this site is information, not tax advice.</li></ul>
<h2>Licences and attributions</h2>
<ul><li>France: "Tarifs taxe de séjour – DELTA", Direction générale des Finances publiques (DGFiP), <a href="{escape(FR['fonte'])}" rel="noopener">data.economie.gouv.fr</a>, Licence Ouverte / Open Licence version 2.0 (Etalab). Dataset updated {data_lunga(FR['dataset_modificato'])}; we keep only rates with a {ANNO} effective date. Modified: rates are reorganised and the totals for unclassified accommodation are calculated by us.</li>
<li>France, choice of town pages: INSEE, <a href="{escape(FR['insee'])}" rel="noopener">Capacité des communes en hébergement touristique 2026</a>, Licence Ouverte / Open Licence.</li>
<li>Laws, ordinances and official decisions are cited as facts with a link to the official text; we do not reproduce the documents.</li></ul>
<h2>Destinations not published (official source not readable or incomplete)</h2>
<p>Venice, Lisbon, Porto, the Algarve, Budapest, Dubrovnik, Split, Osaka, Glasgow, Quintana Roo (Visitax), Okinawa (starts 1 February 2027), Egypt, Morocco and the Canary Islands. We will add them when we can verify a complete official source.</p>
<h2>Sources, destination by destination</h2>
<p>France: see the <a href="{rel}france/">France page</a>.</p>
{elenco}
<h2>Corrections</h2>
<p>Spotted a change or a mistake? <a href="{rel}contact/?ref=about">Tell us</a>.</p></div>"""
    pagina("about/", f"About and sources | {NOME}", "Where our tourist tax rates come from: official sources, check dates and licences.",
           corpo, briciole=[("About and sources", "about/")])


def contatti():
    rel = "../"
    corpo = f"""<section class="hero"><h1>Contact</h1><p class="lead">Spotted a change in a tourist tax, a mistake, or a destination you would like us to add? Write to us here.</p></section>
<section class="card"><form class="form ajax" name="contact" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="contact"><input type="hidden" name="source" value="">
<p class="hp"><label>Do not fill this in <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Your email<input type="email" name="email" required autocomplete="email"></label>
<label>Destination (optional)<input type="text" name="destination" maxlength="200"></label>
<label>Message<textarea name="message" rows="6" required maxlength="4000"></textarea></label>
<label class="check"><input type="checkbox" name="consent" value="yes" required><span>I have read the <a href="{rel}privacy.html">privacy notice</a>.</span></label>
<button class="btn" type="submit">Send</button><p class="errore" data-errore hidden>Sorry, it did not work. Please try again.</p></form>
<div class="ok" data-ok hidden><strong>Thank you.</strong> We will check the official source and reply by email.</div></section>"""
    pagina("contact/", f"Contact | {NOME}", f"Contact {NOME}: report a change in a tourist tax or ask for a destination.", corpo,
           briciole=[("Contact", "contact/")])


def privacy():
    corpo = f"""<section class="hero"><h1>Privacy notice</h1><p class="small">Last updated: October 2026</p></section><div class="testo">
<h2>Who is responsible</h2><p>The data controller is Massimiliano Cori (Italy), who runs {NOME} as an independent project. You can contact us through the <a href="contact/">contact form</a>.</p>
<h2>What we collect</h2><p>Only what you type in the contact form: your email, the destination and your message. We also record the page or link you came from, to understand which pages need corrections. The calculator runs in your browser: what you type in it is not sent to us.</p>
<h2>Why</h2><p>To answer your messages and correct the site. The legal basis is your consent (Art. 6(1)(a) GDPR), which you can withdraw at any time.</p>
<h2>Who processes data for us</h2><p>The site and its form are hosted by Netlify, Inc., which stores form data on our behalf and may process it outside the EU with the safeguards required by the GDPR (standard contractual clauses). We do not sell or share your data.</p>
<h2>Cookies and visit counter</h2><p>This site does not use profiling cookies. To count visits we use <a href="https://www.goatcounter.com/" rel="noopener">GoatCounter</a>, a privacy-friendly counter: it sets no cookies and stores nothing in your browser, builds no profiles and does not store your IP address, your full browser signature or any identifier. It keeps only aggregate numbers (page, hour or day, browser, country, screen width) on servers in the European Union and shares nothing with third parties; see <a href="https://www.goatcounter.com/help/privacy" rel="noopener">GoatCounter's privacy policy</a>. If we add advertising or affiliate links in the future, we will update this notice and ask for your consent where required before any advertising cookies are used.</p>
<h2>How long</h2><p>Messages are kept for up to 12 months after our last exchange.</p>
<h2>Your rights</h2><p>You can ask for access, correction, deletion, restriction, portability and objection (Articles 15–22 GDPR) and you can complain to the Italian data protection authority (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>) or the authority in your country.</p></div>"""
    pagina("privacy.html", f"Privacy | {NOME}", f"Privacy notice of {NOME}.", corpo)


def dati_francia_client():
    d = {"anno": ANNO, "fonte": FR["fonte"], "mod": data_lunga(FR["dataset_modificato"]), "chk": data_lunga(FR["controllato_il"]),
         "cat": [[c[0], c[1]] for c in FR["categorie"]], "v": FR["vettori"], "dep": FR["dipartimenti"],
         "c": sorted(([code, v[5] or v[0].title(), v[1] if len(v[1]) > 1 else "0" + v[1], v[2], v[4]] for code, v in FR["comuni"].items()),
                    key=lambda x: (-FR["comuni"][x[0]][3], x[1]))}
    (SITO / "data").mkdir(exist_ok=True)
    (SITO / "data" / "fr.json").write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def extra():
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n")
    (SITO / f"{CHIAVE_INDEXNOW}.txt").write_text(CHIAVE_INDEXNOW)  # file chiave IndexNow: non in sitemap, non linkato
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{OGGI.isoformat()}</lastmod></url>" for u in URLS)
    (SITO / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n')
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Deploy only when something changed in touristtax/sito.
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."

[[headers]]
  for = "/*"
  [headers.values]
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    X-Frame-Options = "DENY"
    Permissions-Policy = "camera=(), microphone=(), geolocation=()"

[[headers]]
  for = "/data/*"
  [headers.values]
    Cache-Control = "public, max-age=86400"

[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=604800"
""")
    pagina("404.html", f"Page not found | {NOME}", "Page not found.",
           '<section class="hero"><h1>Page not found</h1><p class="lead">Go to the <a href="/">tourist tax calculator</a>.</p></section>', indicizza=False)


def copia_grafica():
    """Font (licenza OFL inclusa) e immagine Open Graph da grafica/ a sito/assets/."""
    (SITO / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (RADICE / "grafica" / "fonts").iterdir():
        shutil.copy(f, SITO / "assets" / "fonts" / f.name)
    shutil.copy(RADICE / "grafica" / "og.png", SITO / "assets" / "og.png")


def controlli():
    errori = []
    for d in DEST:
        for k in ("slug", "name", "country_slug", "currency", "tipo", "categorie", "tariffe", "fonti", "chi_riscuote"):
            if not d.get(k):
                errori.append(f"{d.get('slug')}: manca {k}")
        if not any(f["http"] == 200 for f in d["fonti"]):
            errori.append(f"{d['slug']}: nessuna fonte ufficiale leggibile (200)")
        ids = {c["id"] for c in d["categorie"]}
        for t in d["tariffe"]:
            if t["cat"] not in ids:
                errori.append(f"{d['slug']}: tariffa per categoria sconosciuta {t['cat']}")
        for c in d["categorie"]:
            if not any(t["cat"] == c["id"] for t in d["tariffe"]):
                errori.append(f"{d['slug']}: categoria senza tariffa {c['id']}")
        if d["country_slug"] not in PAESI:
            errori.append(f"{d['slug']}: paese sconosciuto")
    if len({d["slug"] for d in DEST}) != len(DEST):
        errori.append("slug duplicati")
    if errori:
        raise SystemExit("ERRORI NEI DATI:\n" + "\n".join(errori))


def main():
    controlli()
    global FR_SLUG
    FR_SLUG = fr_slug_map()
    if SITO.exists():
        conserva = {p.name: p.read_bytes() for p in SITO.glob("google*.html")}
        shutil.rmtree(SITO)
    else:
        conserva = {}
    SITO.mkdir()
    for nome, contenuto in conserva.items():
        (SITO / nome).write_bytes(contenuto)
    copia_grafica()
    home()
    for d in DEST:
        pagina_destinazione(d)
    pagina_francia()
    for c in FR_TOP["comuni"]:
        pagina_francia_comune(c[0])
    for s in PAESI:
        if s != "france":
            pagina_paese(s)
    pagina_europa()
    pagina_come_funziona()
    about()
    contatti()
    privacy()
    dati_francia_client()
    extra()
    cambi = sorted({x for d in DEST for t in d["tariffe"] + d.get("supplementi", []) for x in
                    ([t["dal"]] if t.get("dal") else []) + ([(date.fromisoformat(t["al"]) + timedelta(days=1)).isoformat()] if t.get("al") else [])
                    if x > OGGI.isoformat()} | {f"{ANNO + 1}-01-01"})
    print("Date in cui rigenerare il sito (cambiano tariffe o titoli):", ", ".join(cambi))
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili; {len(DEST)} destinazioni, {len(FR_TOP['comuni'])} pagine comunali francesi, "
          f"{len(FR['comuni'])} comuni nella ricerca.")


if __name__ == "__main__":
    main()
