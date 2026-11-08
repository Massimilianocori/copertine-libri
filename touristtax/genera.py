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
    ("https://before-you-fly.com/", "Before You Fly", "Passport validity, airport liquid rules, cabin bag sizes"),
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
# Monetizzazione (30/10/2026): codice editore AdSense, elenco dei siti con la pubblicità e domini di affiliazione ammessi stanno
# in un solo file comune, studio-business/strumenti/monetizzazione.json (logica in monetizzazione.py). Con il codice vuoto o con
# questo sito fuori elenco non cambia nulla: niente script nel <head>, niente ads.txt, privacy di oggi.
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402
SITO_ID = "touristtax"  # nome del sito in monetizzazione.json ("adsense_siti")
ADSENSE_HEAD = MON.script_adsense(SITO_ID)  # "" con AdSense spento; altrimenti a capo + script ufficiale, subito dopo il meta di verifica Google


def ci_sono_affiliati():
    """True se il sito pubblica almeno un link di affiliazione (voce con "url" in dati/affiliati.json):
    accende la sezione privacy sui link di affiliazione. Domini ammessi in monetizzazione.json, controlli in verifica.py."""
    return any(isinstance(v, dict) and v.get("url") for v in AFFILIATI.values())  # anche le voci "_" (DiscoverCars, pagine Messico)


def riquadro_trasparenza(corpo, lingua="en"):
    """Riga di trasparenza sui link di affiliazione in fondo al contenuto della pagina ("Some links are affiliate links: ..."):
    vuota finché la pagina non ha link rel="sponsored" o se un riquadro di affiliazione la mostra già."""
    return MON.riga_trasparenza(corpo, lingua)


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
    "italy": "Italy", "japan": "Japan", "indonesia": "Indonesia", "iceland": "Iceland", "malta": "Malta", "portugal": "Portugal",
    "tunisia": "Tunisia", "mexico": "Mexico", "belgium": "Belgium"}
EUROPA = {"france", "spain", "greece", "netherlands", "germany", "austria", "czech-republic", "united-kingdom", "italy", "iceland", "turkey",
          "malta", "portugal", "belgium"}
VALUTE = {"EUR": ("€", "", 2), "GBP": ("£", "", 2), "JPY": ("¥", "", 0), "CZK": ("", " CZK", 0), "ISK": ("ISK ", "", 0),
          "IDR": ("IDR ", "", 0), "TRY": ("TRY ", "", 2), "TND": ("TND ", "", 2),
          "MXN": ("MXN ", "", 2), "USD": ("$", "", 2)}
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


# ---------------------------------------------------------------- Messico (30/10/2026): Visitax = 2,50 UMA
# dati/uma.json ha i valori ufficiali INEGI (uno per anno, in vigore dal 1° febbraio); raccolta/uma.py aggiunge quello nuovo a gennaio.
# Le destinazioni con "uma_moltiplicatore" ricevono qui le tariffe: una per anno, dal 1/2 al 31/1 dell'anno dopo. Senza il valore
# dell'anno dopo l'ultima tariffa finisce il 31/1 e il calcolatore dice che l'importo non è ancora ufficiale (nota_senza_importo).
UMA = json.loads((DATI / "uma.json").read_text(encoding="utf-8"))
MX = json.loads((DATI / "messico.json").read_text(encoding="utf-8"))
UMA_VALORI = sorted(UMA["valori"], key=lambda v: v["dal"])


def _giorno_prima(iso):
    return (date.fromisoformat(iso) - timedelta(days=1)).isoformat()


def al_peso(x):
    """Arrotondamento al peso per il pagamento (Código Fiscal del Estado de Quintana Roo, art. 18): da 1 a 50 centavos
    all'unità inferiore, da 51 a 99 all'unità superiore. Il portale Visitax il 30/10/2026 chiede MXN 293 a persona (293,275)."""
    base = math.floor(x + 1e-9)
    cent = round((x - base) * 100, 6)
    return float(base + (1 if cent > 50 else 0))


def tariffe_uma(molt):
    """Tariffe [{cat, dal, al, valore, esatto, uma, anno}]: esatto = molt × UMA giornaliera dell'anno, valore = esatto arrotondato
    al peso (al_peso), cioè l'importo che si paga."""
    out = []
    for i, v in enumerate(UMA_VALORI):
        al = _giorno_prima(UMA_VALORI[i + 1]["dal"]) if i + 1 < len(UMA_VALORI) else f"{int(v['dal'][:4]) + 1}-01-31"
        esatto = round(molt * v["diario"], 4)
        out.append({"cat": "all", "dal": v["dal"], "al": al, "valore": al_peso(esatto), "esatto": esatto, "uma": v["diario"], "anno": v["anno"]})
    return out


def nota_senza_importo(molt):
    ultima = tariffe_uma(molt)[-1]
    dopo = (date.fromisoformat(ultima["al"]) + timedelta(days=1)).isoformat()
    return (f"No official amount yet for arrivals from {data_lunga(dopo)}: it will be {molt:.2f} × the {dopo[:4]} UMA, "
            f"which INEGI publishes in January {dopo[:4]}.")


for _d in DEST:
    if _d.get("uma_moltiplicatore"):
        _d["tariffe"] = tariffe_uma(_d["uma_moltiplicatore"])
        _d["nota_senza_importo"] = nota_senza_importo(_d["uma_moltiplicatore"])
        _d["unita_viaggio"] = "due on entering Quintana Roo"


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
    if R.get("esente_da_notti") and notti >= R["esente_da_notti"]:
        out["note"].append(f"One booking of {R['esente_da_notti']} nights or more is not charged.")
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
            if t.get("bande_pct") and b:
                imp = pp * b / 100 * persone
                testo = f"{num(b)}% of {soldi(pp, val)} per person × {plur(persone, 'guest')}"
            else:
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
        pct = [(b[0], b[2]) for t in tt if t.get("bande_pct") for b in t["valore"] if b[2] > 0]
        if pct:
            return f"{num(pct[0][1])}% of the room-only price per person per night from {soldi(pct[0][0], val)}"
        vals = [b[2] for t in tt for b in t["valore"]]
        nz = [v for v in vals if v > 0]
        return f"{soldi(min(nz), val)}–{soldi(max(nz), val)} per person per night (by price band)"
    if tipo == "per_trip":
        return f"{soldi(tt[0]['valore'], val)} per person, {R.get('unita_viaggio', 'once per trip')}"
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
        if any(t.get("bande_pct") for t in R["tariffe"]):
            f += "; where the band is a percentage: percentage × price per person per night × guests × nights"
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
    if R.get("esente_da_notti"):
        extra.append(f"one booking of {R['esente_da_notti']} nights or more is not charged")
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
                importo = (f"{num(v)}% of the price per person" if t.get("bande_pct") else soldi(v, val)) if v else "no tax"
                righe.append(f"<tr><td>{fascia}</td><td><strong>{importo}</strong>{parti}</td></tr>")
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
.risposta{font-size:1.07rem;line-height:1.55;color:var(--ink);max-width:780px;margin:8px 0 6px;padding:2px 0 2px 14px;border-left:3px solid var(--sun)}
.callout.cambi-box{align-items:flex-start;margin-top:14px}
.cambi-box .ic,.cal-2027 .ic{background:var(--accent-2);color:var(--accent)}
.cambi-box ul{margin:4px 0 6px;padding-left:18px;font-size:.95rem;color:var(--ink-2)}
.cambi-box p{margin:0}
.cal-2027{margin-top:10px}
.sintesi{margin-top:18px}.sintesi td:first-child{white-space:nowrap}.jp-conf td:first-child{white-space:normal}
@media (max-width:640px){.tab.sintesi td,.tab.sintesi th{min-width:0;padding:9px 10px}.tab.sintesi td:first-child,.tab.sintesi th:first-child{min-width:0}}
.linea{list-style:none;margin:22px 0 0;padding:0;display:grid;gap:14px}
.vc{display:grid;grid-template-columns:96px minmax(0,1fr);background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-1);overflow:hidden}
.vc-data{background:linear-gradient(180deg,var(--accent-2),var(--card));border-right:1px solid var(--line);display:flex;flex-direction:column;align-items:center;padding:18px 8px;text-align:center}
.vc-g{font-family:var(--head);font-weight:700;font-size:2.2rem;line-height:1;color:var(--accent);font-variant-numeric:tabular-nums}
.vc-m{font-size:.76rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-2);margin-top:6px}
.vc-c{padding:16px 20px;min-width:0}
.vc-c h3{margin:0 0 10px;font-size:1.22rem}
.vc-c h3 a{color:var(--ink);text-decoration:none}
.vc-c h3 a:hover{color:var(--accent);text-decoration:underline}
.vc-c p{margin:0 0 8px;max-width:760px}
.vc-imp{font-weight:700;color:var(--ink)}
.vc-prima{font-size:.9rem;color:var(--ink-3)}
.vc-lab{display:inline-block;font-size:.68rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:2px 8px;border-radius:999px;margin-right:6px;vertical-align:.12em}
.vc-imp .vc-lab{background:var(--ok-2);color:var(--ok)}
.vc-prima .vc-lab{background:var(--mute);color:var(--ink-3);border:1px solid var(--line)}
.vc .fonte{margin-top:4px}
.vc-calc{display:inline-flex;align-items:center;gap:6px;font-weight:600;font-size:.9rem;text-decoration:none;margin-top:6px}
.vc-calc:hover{text-decoration:underline}
.faq-box{display:grid;gap:8px}
details.faq{background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:0 16px;box-shadow:var(--sh-1)}
details.faq summary{cursor:pointer;font-weight:700;padding:13px 0;list-style:none;display:flex;gap:10px;align-items:center;color:var(--ink)}
details.faq summary::-webkit-details-marker{display:none}
details.faq summary::after{content:"+";margin-left:auto;font-size:1.2rem;color:var(--accent)}
details.faq[open] summary::after{content:"–"}
details.faq p{margin:0 0 14px;color:var(--ink-2);max-width:760px}
@media (max-width:560px){.vc{grid-template-columns:1fr}.vc-data{flex-direction:row;align-items:baseline;gap:8px;border-right:0;border-bottom:1px solid var(--line);padding:10px 16px;background:var(--accent-2)}
.vc-g{font-size:1.45rem}.vc-m{margin-top:0}.vc-c{padding:14px 16px}.risposta{font-size:1rem}}
.us-tab td:first-child{white-space:normal;min-width:9em}
.calc .us-opzioni{display:grid;gap:8px}
.calc label.us-opz{display:flex;gap:10px;align-items:flex-start;font-weight:400;font-size:.9rem}
.calc label.us-opz input{width:auto;min-height:0;margin-top:3px;flex:none}
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
var VAL={"EUR":["€","",2],"GBP":["£","",2],"JPY":["¥","",0],"CZK":[""," CZK",0],"ISK":["ISK ","",0],"IDR":["IDR ","",0],"TRY":["TRY ","",2],"TND":["TND ","",2],"MXN":["MXN ","",2],"USD":["$","",2]};
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
  if(R.esente_da_notti&&notti>=R.esente_da_notti){out.note.push('One booking of '+R.esente_da_notti+' nights or more is not charged.');return out;}
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
    else if(tp==='bands'){var pp=persone?prezzo/persone:0;var b=banda(t.valore,pp);
      if(t.bande_pct&&b){imp=pp*b/100*persone;testo=num(b)+'% of '+soldi(pp,val)+' per person × '+plur(persone,'guest');}
      else{imp=b*persone;testo=soldi(b,val)+' per person (band for '+soldi(pp,val)+' per person) × '+plur(persone,'guest');}}
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
    f.querySelector('[data-lab=checkin]').textContent=R.etichetta_data||'Check-in date';
    var lp=f.querySelector('[data-lab=prezzo]');lp.textContent=(R.etichetta_prezzo||'Price per night')+' ('+R.currency+')';
    function aggiorna(){
      var tp=R.tipo,isNC=false;
      if(tp==='france'){var t=R.tariffe.filter(function(x){return x.cat===cat.value;})[0];isNC=t&&t.fr.u==='%';}
      vis('checkin',tp!=='per_trip'||!!R.chiedi_data);vis('notti',tp!=='per_trip');
      vis('paganti',tp!=='per_room'&&tp!=='percent');vis('esenti',!!eta&&tp!=='per_room'&&tp!=='percent');
      vis('stanze',tp==='per_room');vis('prezzo',tp==='percent'||tp==='bands'||isNC);
      var notti=Math.max(1,Math.min(365,parseInt(q('notti').value,10)||1));
      var pag=Math.max(0,parseInt(q('paganti').value,10)||0),es=Math.max(0,parseInt(q('esenti').value,10)||0);
      var st=Math.max(1,parseInt(q('stanze').value,10)||1),pr=Math.max(0,parseFloat(q('prezzo').value)||0);
      var ci=q('checkin').value||primaData(R);
      var zs=q('zona');vis('zona',!!(R.zone&&R.zone.length));
      var o=calcola(R,cat.value,ci,notti,pag,eta?es:0,st,pr,(R.zone&&zs)?zs.value:'');
      var cur=R.currency,nessuno=tp==='per_trip'&&!o.righe.length,tot=nessuno?'Not yet official':soldi(o.totale,cur);
      var h='<div class="r-lab">Estimated tax for this stay</div><div class="tot">'+tot+'</div>';
      var kv=[],tassate=o.righe.reduce(function(s,g){return s+(g[2]>0?g[1]:0);},0);
      if(tp!=='per_trip'){kv.push(['Taxed nights',tassate+' of '+notti]);kv.push(['Average per night',soldi(o.totale/notti,cur)]);}
      if((tp==='per_person'||tp==='france'||tp==='per_trip')&&pag>0&&!nessuno)kv.push([tp==='per_trip'?'Per traveller':'Per paying guest',soldi(o.totale/pag,cur)]);
      if(eta&&tp!=='per_room'&&tp!=='percent')kv.push(['Exempt (under '+eta+')',plur(es,'guest')]);
      if(tp==='per_room')kv.push(['Rooms or units',String(st)]);
      if(tp==='percent'||tp==='bands'||isNC)kv.push(['Price per night',soldi(pr,cur)]);
      h+='<dl class="r-dl">'+kv.map(function(x){return '<div><dt>'+esc(x[0])+'</dt><dd>'+esc(x[1])+'</dd></div>';}).join('')+'</dl><ul class="r-righe">';
      o.righe.forEach(function(g){h+='<li><span>'+(tp==='per_trip'?'':plur(g[1],'night')+' × ')+esc(g[0])+'</span><strong class="eq">= '+soldi(g[2],cur)+'</strong></li>';});
      if(R.tipo==='per_trip'&&!o.righe.length)h+='<li>'+esc(R.nota_senza_importo||'No verified amount.')+'</li>';
      if(o.escluse)h+='<li>'+plur(o.escluse,'night')+' beyond the maximum number of taxable nights: no tax.</li>';
      if(o.fuori)h+='<li>'+plur(o.fuori,'night')+' outside the collection period: no tax.</li>';
      if(o.prima)h+='<li>'+plur(o.prima,'night')+' before '+esc(R.in_vigore_testo||R.in_vigore_dal)+': no tax yet.</li>';
      if(o.sconosciute&&tp!=='per_trip')h+='<li>'+plur(o.sconosciute,'night')+' with no verified official rate for that date (not counted).</li>';
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
    voci_menu = [("", "Calculator"), ("tourist-taxes-europe-2026/", "Europe 2026"), ("france/", "France"), ("japan-accommodation-tax/", "Japan"), ("usa/", "USA"),
                 ("how-tourist-taxes-work/", "How it works"), ("about/", "Sources")]
    menu = "".join(f'<a href="{rel}{u}"{" aria-current=\"page\"" if u == percorso else ""}>{t}</a>' for u, t in voci_menu)
    testo = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="{GOOGLE_VERIFICA}">{ADSENSE_HEAD}
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
{corpo}{riquadro_trasparenza(corpo)}
</div>
</main>
<footer><div class="wrap">
<div class="f-grid"><div>
<a class="logo" href="{rel}">{MARCHIO}<span>Tourist Tax <b>Calculator</b></span></a>
<p><strong>{NOME}</strong> is an independent site, not affiliated with any government or tax authority. Every rate comes from an official source (law, ordinance, tax authority page or official open data) linked under the figure with the date we checked it.
<strong>Tourist taxes are set by local or national authorities and can change. Your accommodation collects the tax: check the exact amount with them.</strong> Nothing on this site is tax or legal advice.</p>
</div><div>
<h2>Explore</h2>
<ul><li><a href="{rel}about/">About and sources</a></li><li><a href="{rel}contact/">Contact</a></li><li><a href="{rel}privacy.html">Privacy</a></li><li><a href="{rel}how-tourist-taxes-work/">How tourist taxes work</a></li><li><a href="{rel}tourist-taxes-europe-2026/">Tourist taxes in Europe 2026</a></li><li><a href="{rel}tourist-tax-changes-2027/">Tourist tax changes in 2027</a></li><li><a href="{rel}usa/">Hotel tax in the USA</a></li><li><a href="{rel}contact/?ref=spotted-a-change">Spotted a change? Tell us</a></li></ul>
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
<label data-campo="checkin"><span class="lt">{ico("calendar")}<span data-lab="checkin">Check-in date</span></span><input type="date" name="checkin"></label>
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


CAMPI_MOTORE = ("name", "country", "slug", "currency", "tipo", "categorie", "tariffe", "esenti_sotto_eta", "max_notti", "max_soggiorno", "esente_da_notti",
                "riduzioni", "etichetta_prezzo", "cap", "prezzo_esempio", "esente_oltre_mesi", "in_vigore_dal", "in_vigore_testo",
                "zone", "supplementi", "chiedi_data", "etichetta_data", "nota_senza_importo")


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
            f'<p class="small" style="margin:0">{MON.RIGA_EN}</p></section>')  # riga di trasparenza comune (monetizzazione.py)


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


# ---------------------------------------------------------------- titoli, descrizioni e risposta diretta (26/10/2026)
# Tutte le cifre vengono da righe_correnti() e dalle tariffe dei dati alla data di generazione: qui ci sono solo i nomi
# usati nelle ricerche (titolo), il nome nell'H1 e un suffisso (il nome locale della tassa, già in official_name).
NOMI_SEO = {
    "mallorca": ("Majorca", "Mallorca (Majorca)", " (ecotasa)"),
    "ibiza": ("Ibiza", "Ibiza", " (ecotasa)"),
    "menorca": ("Menorca", "Menorca", " (ecotasa)"),
    "formentera": ("Formentera", "Formentera", " (ecotasa)"),
    "catalonia": ("Catalonia", "Catalonia (outside Barcelona)", ""),
    "cardiff": ("Cardiff (Wales)", "Cardiff (Wales)", ""),
    "malta": ("Malta", "Malta", ""),
    "edinburgh": ("Edinburgh", "Edinburgh", " (visitor levy)"),
}
CAMBI = json.loads((DATI / "cambi_2027.json").read_text(encoding="utf-8"))


def _riempi_cambio_uma(v):
    """Voce 'uma' della pagina 2027 (Visitax del Quintana Roo): importo dalla UMA dell'anno se l'INEGI l'ha già pubblicata
    (dati/uma.json), altrimenti la formula. 'prima' = importo dell'anno precedente, sempre dalla stessa formula."""
    m, anno = v["uma"]["moltiplicatore"], v["uma"]["anno"]
    tt = {t["anno"]: t for t in tariffe_uma(m)}
    prima = tt.get(anno - 1)
    v["prima"] = soldi(prima["valore"], "MXN") if prima else ""
    if anno in tt:
        t = tt[anno]
        v["importo"] = f"{soldi(t['valore'], 'MXN')} per foreign visitor ({m:.2f} × the {anno} UMA of {soldi(t['uma'], 'MXN')})"
        v["cosa"] = v["cosa"].split(" INEGI publishes")[0]
        v["importo_breve"] = f"{soldi(t['valore'], 'MXN')} (from {v['prima']})"
        v["verifica"] = [[d["slug"], v["dal"]] for d in DEST if d.get("uma_moltiplicatore")]
    else:
        v["importo"] = f"{m:.2f} × the {anno} UMA per foreign visitor (INEGI publishes the {anno} UMA in January {anno})"
        v["importo_breve"] = f"2.5 × UMA {anno} (now {v['prima']})"


for _v in CAMBI["voci"]:
    if _v.get("uma"):
        _riempi_cambio_uma(_v)
MESI_BREVI = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def data_breve(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {MESI_BREVI[d.month - 1]} {d.year}"


def soldi_breve(v, valuta):
    """€4 invece di €4.00, ma €0.50 e £1.30 restano con i decimali."""
    s = soldi(v, valuta)
    return s[:-3] + s[-3:].replace(".00", "") if ".00" in s[-7:] else s


def _vigenti(R, giorno):
    """Righe valide esattamente in quella data (vuoto se non ce ne sono: per esempio Cardiff prima del 1/4/2027)."""
    return [t for t in R["tariffe"] if (not t.get("dal") or t["dal"] <= giorno) and (not t.get("al") or giorno <= t["al"])]


def fascia_breve(R, righe):
    val, tipo = R["currency"], R["tipo"]
    if tipo == "percent":
        return " / ".join(f"{num(v)}%" for v in sorted({t["valore"] for t in righe}))
    if tipo == "bands":
        pct = [b[2] for t in righe if t.get("bande_pct") for b in t["valore"] if b[2] > 0]
        if pct:
            return f"{num(pct[0])}%"
        vals = [b[2] for t in righe for b in t["valore"] if b[2] > 0]
    else:
        vals = [t["valore"] for t in righe]
    lo, hi = min(vals), max(vals)
    return soldi_breve(lo, val) if lo == hi else f"{soldi_breve(lo, val)}–{soldi_breve(hi, val)}"


def unita(R, righe=None):
    if R["tipo"] == "bands" and righe and any(t.get("bande_pct") for t in righe):
        return "of the room price"
    return {"per_person": "per person per night", "per_room": "per room per night", "percent": "of the room price",
            "bands": "per person per night", "per_trip": "per person, once per trip"}[R["tipo"]]


def prossimo_cambio(R):
    """Prima data futura (entro il 2027) in cui cambiano le tariffe dei dati, o None."""
    oggi = OGGI.isoformat()
    for d in sorted({t["dal"] for t in R["tariffe"] if t.get("dal") and oggi < t["dal"] <= "2027-12-31"}):
        if _vigenti(R, oggi) and fascia_breve(R, _vigenti(R, d)) != fascia_breve(R, _vigenti(R, oggi)):
            return d
    return None


def anni(R):
    """'2026', '2026 and 2027' (se i dati hanno una tariffa o un cambio ufficiale che parte nel 2027) o '2027' (se la tassa parte nel 2027)."""
    inizi = [t.get("dal") or "" for t in R["tariffe"]]
    if all(i[:4] == "2027" for i in inizi):
        return "2027"
    date_27 = [t["dal"] for t in R["tariffe"] + R.get("supplementi", []) + R.get("cambi_annunciati", []) if (t.get("dal") or "")[:4] == "2027"]
    return f"{ANNO} and {ANNO + 1}" if date_27 else str(ANNO)


def breve(R, lungo=False):
    """Cifra per titolo e H1: '€1–€4 per person per night', '1% now, 2% from 1 Jan 2027', '£0.75–£1.30 per person per night from 1 Apr 2027'."""
    oggi = OGGI.isoformat()
    ora = _vigenti(R, oggi)
    if not ora:
        primo = min(t["dal"] for t in R["tariffe"] if t.get("dal"))
        righe = _vigenti(R, primo)
        return f"{fascia_breve(R, righe)} {unita(R, righe)} from {(data_lunga if lungo else data_breve)(primo)}"
    d = prossimo_cambio(R)
    if d:
        return f"{fascia_breve(R, ora)} now, {fascia_breve(R, _vigenti(R, d))} from {data_breve(d)}"
    return f"{fascia_breve(R, ora)} {unita(R, ora)}"


def nomi(R):
    t, h, suf = NOMI_SEO.get(R["slug"], (R["name"], R["name"], ""))
    return t, h, suf


def titolo_seo(R):
    t, _, suf = nomi(R)
    return f"{t} tourist tax {anni(R)} calculator: {R.get('breve_seo') or breve(R)}{suf}"


def h1_seo(R):
    _, h, _ = nomi(R)
    oggi = OGGI.isoformat()
    ora = _vigenti(R, oggi)
    d = prossimo_cambio(R)
    if ora and d:
        b = f"{fascia_breve(R, ora)} {unita(R, ora)}, {fascia_breve(R, _vigenti(R, d))} from {data_lunga(d)}"
    else:
        b = breve(R, lungo=True)
    return f"{h} tourist tax {anni(R)}: {b}"


def _prezzo_testo(R):
    e = R.get("etichetta_prezzo", "price per night").split(";")[0].replace(", all guests and rooms", "")
    e = re.sub(r"\s*\((all rooms booked|[^)]*rooms?[^)]*)\)$", "", e)
    return e[0].lower() + e[1:]


def risposta(R):
    """Risposta diretta in 1-3 frasi, solo con i dati della destinazione (o il campo 'risposta' dei dati, scritto dalle note ufficiali)."""
    if R.get("risposta"):
        return R["risposta"]
    val, tipo = R["currency"], R["tipo"]
    nome = nomi(R)[1] if R["slug"] != "catalonia" else "Catalonia outside Barcelona"
    oggi = OGGI.isoformat()
    ora = _vigenti(R, oggi)
    inizio = ""
    if not ora:
        primo = min(t["dal"] for t in R["tariffe"] if t.get("dal"))
        ora = _vigenti(R, primo)
        inizio = f"From {data_lunga(primo)}, "
    eta = R.get("esenti_sotto_eta")
    f = []
    rng = fascia_breve(R, ora).replace("–", " to ")
    tipi = len({t["cat"] for t in ora}) > 1
    if tipo == "per_person":
        chi = f"each guest aged {eta} or over" if eta else "each guest"
        s = f"{inizio}in {nome} you pay {rng} per night for {chi}"
        s = s[0].upper() + s[1:]
        f.append(s + (", depending on the type of accommodation." if tipi and " to " in rng else "."))
    elif tipo == "per_room":
        stag = {}
        for t in ora:
            stag.setdefault(t.get("stagione", ""), []).append(t)
        parti = [f"{k} {fascia_breve(R, v)}" for k, v in stag.items() if k]
        f.append(f"In {nome} you pay {rng} per room per night (not per person), depending on the type of accommodation"
                 + (f" and the season: {'; '.join(parti)}." if len(parti) > 1 else "."))
    elif tipo == "percent":
        x = sorted({t["valore"] for t in ora})[0]
        t0 = next(t for t in ora if t["valore"] == x)
        pe = R.get("prezzo_esempio", 150)
        imp = pe * t0.get("fattore_base", 1) * x / 100
        if inizio:
            f.append(f"{inizio}in {nome} the tax is {num(x)}% of the {_prezzo_testo(R)}.")
        else:
            f.append(f"In {nome} the tax is {num(x)}% of the {_prezzo_testo(R)}: on {soldi_breve(pe, val)} a night you pay {soldi(imp, val)} a night.")
    elif tipo == "bands":
        pct = [b for t in ora if t.get("bande_pct") for b in t["valore"] if b[2] > 0]
        if pct:
            f.append(f"In {nome} the tax is {num(pct[0][2])}% of the room-only price per person per night, from {soldi(pct[0][0], val)} per person.")
        else:
            nz = [b for t in ora for b in t["valore"] if b[2] > 0]
            soglia = min(b[0] for b in nz)
            f.append(f"In {nome} you pay {rng} per person per night, depending on the room-only price per person"
                     + (f" (no tax below {soldi(soglia, val)})." if soglia else "."))
    elif tipo == "per_trip":
        f.append(f"In {nome} each traveller pays {rng} once per trip.")
    extra = []
    if R.get("max_notti"):
        extra.append(f"only the first {R['max_notti']} nights of a stay are taxed")
    for rid in R.get("riduzioni", []):
        extra.append(rid["testo"].replace("low season (1 Nov - 30 Apr): -75%", "it is 75% lower from 1 November to 30 April")
                     .replace("9th day onwards: -50%", "it is halved from the 9th day"))
    if R.get("esente_da_notti"):
        extra.append(f"one booking of {R['esente_da_notti']} nights or more is not charged")
    if eta and tipo == "per_person":
        extra.append(f"children under {eta} pay nothing")
    if extra:
        s = ", ".join(extra[:-1]) + (" and " if len(extra) > 1 else "") + extra[-1]
        f.append(s[0].upper() + s[1:] + ".")
    d = prossimo_cambio(R)
    if d:
        riserva = next((t["nota"] for t in _vigenti(R, d) if "unless" in t.get("nota", "")), "")
        f.append(f"From {data_lunga(d)} it changes to {_riassunto(R, d)}" + (f" ({riserva[0].lower() + riserva[1:].rstrip('.')})." if riserva else "."))
    for c in R.get("cambi_annunciati", []):
        if c["dal"] > oggi:
            f.append(f"From {data_lunga(c['dal'])}: {c['testo'][0].lower() + c['testo'][1:]}")
    return " ".join(f)


def descrizione_seo(R):
    t, _, suf = nomi(R)
    r = risposta(R)
    frasi = re.split(r"(?<=\.) ", r)
    testo = frasi[0]
    for x in frasi[1:]:
        if len(testo) + len(x) < 150:
            testo += " " + x
    coda = " Official rates and calculator."
    if len(testo) + len(coda) > 158:
        # Google tronca intorno ai 155-160 caratteri: si taglia a fine parola.
        testo = testo[:158 - len(coda) - 1].rsplit(" ", 1)[0].rstrip(",;:–-") + "…"
    return testo + coda


def cambi_di(slug):
    """Voci della pagina 2027 che riguardano una destinazione."""
    return [v for v in CAMBI["voci"] if v["slug"] == slug or any(s == slug for s, _ in v["verifica"])]


def box_cambi(R, rel):
    vv = cambi_di(R["slug"])
    if not vv:
        return ""
    righe = "".join(f"<li><strong>{data_lunga(v['dal'])}:</strong> {escape(v['importo'])}</li>" for v in vv)
    return (f'<section class="card callout cambi-box" aria-label="Changes in 2027"><span class="ic">{ico("calendar")}</span>'
            f'<div><p><strong>What changes in 2027</strong></p><ul>{righe}</ul>'
            f'<p class="small"><a href="{rel}tourist-tax-changes-2027/">All tourist tax changes in 2027, with official sources</a></p></div></section>')


def box_evento(R):
    """Riquadro di un grande evento (4/11/2026: Anno Santo 2027 a Santiago, America's Cup 2027 a Napoli), solo con fatti e fonti ufficiali dei dati."""
    ev = R.get("evento")
    if not ev:
        return ""
    fonti = "; ".join(f'<a href="{escape(f["url"])}" rel="noopener">{escape(f["titolo"])}</a>, checked {data_lunga(f["controllato_il"])}' for f in ev["fonti"])
    return (f'<section class="card callout evento-box" aria-label="{escape(ev["titolo"])}"><span class="ic">{ico("calendar")}</span>'
            f'<div><p><strong>{escape(ev["titolo"])}</strong></p><p>{escape(ev["testo"])}</p>'
            f'<p class="small">Official source: {fonti}</p></div></section>')


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
    corpo = f"""<section class="hero">{h1_diviso(h1_seo(R))}
<p class="risposta">{escape(risposta(R))}</p></section>
<section class="card summary" aria-label="Summary">
<div><p class="cifra"><span class="lab">{ico("receipt")}{escape(R['name'])} {anni(R)}</span><span class="sr">: </span><strong>{escape(riassunto(R))}</strong></p>
{chips(R, paese)}</div>
<div><p class="lead">{escape(R['official_name'])}. The calculator below uses the official rates and rules: {escape(regole_testo(R))}.</p>
{fonte_breve(R)}</div>
</section>
{box_cambi(R, rel)}
{box_evento(R)}
{(jt_callout(rel) + jp_callout(rel)) if R["country_slug"] == "japan" else ""}
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
    pagina(f"{slug}/", titolo_seo(R), descrizione_seo(R), corpo,
           briciole=[(paese, f"country/{R['country_slug']}/"), (R["name"], f"{slug}/")])


def link_paese(s):
    """Percorso della pagina di un paese: Francia e Messico hanno una pagina propria, gli altri country/<slug>/."""
    return {"france": "france/", "mexico": "mexico/"}.get(s, f"country/{s}/")


# ---------------------------------------------------------------- pagine Messico (30/10/2026)
# Tutti gli importi del Visitax vengono da tariffe_uma() (2,50 × UMA di dati/uma.json); DNR, crociere e imposta sull'alloggio
# da dati/messico.json. verifica.py ricalcola gli importi dalla formula e li cerca nelle pagine.
MX_VIS = MX["visitax"]
MX_MOLT = MX_VIS["moltiplicatore_uma"]
MX_DEST = [d for d in DEST if d["country_slug"] == "mexico"]
MX_CHECK = data_lunga(max([MX_VIS["legge"]["controllato_il"], MX_VIS["portale"]["controllato_il"]] + [v["fonte"]["controllato_il"] for v in UMA_VALORI]))
AVVISO_MX = ('<p class="avviso"><strong>Not tax advice.</strong> These fees are set by Mexican federal and Quintana Roo state law and can change. '
             'The official Visitax portal shows the exact amount before you pay.</p>')


def mx_tariffe():
    return tariffe_uma(MX_MOLT)


def mx_ora():
    """Tariffa Visitax in vigore oggi (o l'ultima nota, se oggi è dopo la fine dei dati)."""
    oggi = OGGI.isoformat()
    tt = mx_tariffe()
    return next((t for t in tt if t["dal"] <= oggi <= t["al"]), tt[-1])


def mx_futura():
    oggi = OGGI.isoformat()
    return next((t for t in mx_tariffe() if t["dal"] > oggi), None)


def mx_anno():
    f = mx_futura()
    return str(f["anno"]) if f else str(mx_ora()["anno"])


def mx_soldi(v):
    return soldi(v, "MXN")


def mx_esatto(t):
    """2.50 × UMA senza arrotondare (293.275, 282.85)."""
    return "MXN " + (f"{t['esatto']:.4f}".rstrip("0").rstrip("."))


def mx_formula_testo(t):
    return f"{MX_MOLT:.2f} × {mx_soldi(t['uma'])} = {mx_esatto(t)}, rounded to {mx_soldi(t['valore'])}"


def mx_portale_prezzo(t):
    """Frase sul prezzo letto sul portale ufficiale, solo se è lo stesso importo dell'anno t."""
    pp = MX_VIS["portale"].get("prezzo_unitario")
    if pp and pp["valore"] == t["valore"] and pp["anno"] == t["anno"]:
        return f"the official portal charges {mx_soldi(pp['valore'])} per person (checked on {data_lunga(pp['controllato_il'])})"
    return ""


def mx_titolo(nome, extra=""):
    """Titolo ≤ 70 caratteri con l'anno e l'importo (il primo candidato che ci sta)."""
    a, o, f = mx_anno(), mx_ora(), mx_futura()
    imp = f"Visitax {mx_soldi(f['valore'])} from {data_breve(f['dal'])}" if f else f"Visitax {mx_soldi(o['valore'])} per person"
    cand = [f"{nome} tourist tax {a}: {imp}{extra} (calculator)", f"{nome} tourist tax {a}: {imp}{extra}",
            f"{nome} tourist tax {a}: {imp}", f"{nome} tourist tax {a}: {imp.replace('Visitax ', '')}"]
    return next(c for c in cand if len(c) <= 70)


def mx_crociere_ora():
    oggi = OGGI.isoformat()
    pp = MX["federali"]["crociere"]["periodi"]
    return next((p for p in pp if p["dal"] <= oggi <= p["al"]), None)


def mx_crociere_testo():
    """Frase sui crocieristi (decreto del 30/6/2025), dai periodi dei dati: periodo in corso e quelli dopo."""
    oggi = OGGI.isoformat()
    pp = [p for p in MX["federali"]["crociere"]["periodi"] if p["al"] >= oggi]
    if not pp:
        return ""
    parti = []
    for i, p in enumerate(pp):
        if i == 0 and p["dal"] <= oggi:
            parti.append(f"the peso equivalent of US${p['usd']} until {data_lunga(p['al'])}")
        elif i == len(pp) - 1:
            parti.append(f"US${p['usd']} from {data_lunga(p['dal'])} to {data_lunga(p['al'])}")
        else:
            parti.append(f"US${p['usd']} from {data_lunga(p['dal'])}")
    return ("Foreign cruise passengers pay Mexico's federal visitor fee at a reduced amount set by the decree of 30 June 2025: "
            + ", ".join(parti[:-1]) + (" and " if len(parti) > 1 else "") + parti[-1]
            + " (converted at the Banco de México exchange rate). Re-entering Mexico on the same cruise is free.")


def mx_risposta(nome_luogo, crociere=False):
    o, f = mx_ora(), mx_futura()
    s = (f"Foreign visitors to {nome_luogo} pay the Quintana Roo Visitax of {mx_soldi(o['valore'])} per person from {data_lunga(o['dal'])}: "
         f"2.50 UMA under article 51-Octies of the Quintana Roo Law on Fees, with the {o['anno']} UMA of {mx_soldi(o['uma'])} published by INEGI "
         f"(law and UMA checked on {MX_CHECK}). It is due when you enter the state, for every foreign visitor whatever their age.")
    if f:
        s += f" From {data_lunga(f['dal'])} it is {mx_soldi(f['valore'])} ({mx_formula_testo(f)})."
    else:
        dopo = (date.fromisoformat(o["al"]) + timedelta(days=1)).isoformat()
        s += f" From {data_lunga(dopo)} it will be 2.50 × the {dopo[:4]} UMA, which INEGI publishes in January {dopo[:4]}."
    if crociere:
        s += (f" Cruise passengers pay instead a state fee of US${MX['quintana_roo']['crociere_usd']}, charged with the cruise ticket "
              "(article 51-Nonies).")
    return s


def mx_avviso_ufficiale(rel):
    o = mx_ora()
    return (f'<section class="card callout mx-uff" aria-label="Official Visitax site"><span class="ic">{ico("shield")}</span>'
            f'<p><strong>Pay on the official site:</strong> <a href="{escape(MX_VIS["sito_ufficiale"])}" rel="noopener">{escape(MX_VIS["sito_ufficiale_nome"])}</a> '
            f'(Quintana Roo Tax Administration Service, SATQ). The official fee is {mx_soldi(o["valore"])} per person; third-party sites may charge a service fee.</p></section>')


def mx_tabella_anni():
    righe = "".join(f"<tr><td>{data_breve(t['dal'])} – {data_breve(t['al'])}</td><td>{mx_soldi(t['uma'])}</td>"
                    f"<td><strong>{mx_soldi(t['valore'])}</strong></td></tr>" for t in reversed(mx_tariffe()))
    ultima = mx_tariffe()[-1]
    dopo = (date.fromisoformat(ultima["al"]) + timedelta(days=1)).isoformat()
    righe = (f"<tr><td>From {data_breve(dopo)}</td><td>INEGI, January {dopo[:4]}</td><td>2.50 × UMA {dopo[:4]}</td></tr>" + righe)
    fonti = " · ".join(f'<a href="{escape(v["fonte"]["url"])}" rel="noopener">INEGI UMA {v["anno"]}</a>' for v in UMA_VALORI)
    return ('<div class="tab sintesi"><table><thead><tr><th>Arrival date</th><th>UMA (per day)</th><th>Visitax</th></tr></thead>'
            f'<tbody>{righe}</tbody></table></div><p class="fonte">Official sources: {fonti} · '
            f'<a href="{escape(MX_VIS["legge"]["url"])}" rel="noopener">Ley de Derechos del Estado de Quintana Roo, art. 51-Octies</a> · checked on {MX_CHECK}</p>')


def mx_formula_html():
    o = mx_ora()
    return (f'<details class="formula" open><summary>{ico("calc")}Formula used</summary><p>Visitax = 2.50 × UMA (daily value in force on your arrival date) × foreign travellers. '
            f'From {data_lunga(o["dal"])}: {mx_formula_testo(o)} per person. The Quintana Roo Fiscal Code (article 18) rounds amounts to the whole peso for payment '
            f'(1 to 50 centavos down, 51 to 99 up){"; " + mx_portale_prezzo(o) if mx_portale_prezzo(o) else ""}. The UMA is updated by INEGI every January and applies from 1 February, '
            'so the Visitax changes every 1 February. Children pay the same amount as adults.</p></details>')


def mx_altre_tasse(rel, crociere=True):
    """Altre tasse per i turisti stranieri: DNR, diritto in aeroporto all'uscita, crociere, imposta sull'alloggio del Quintana Roo."""
    fed, qr = MX["federali"], MX["quintana_roo"]
    al = qr["alloggio"]
    voci = [f"<li><strong>Federal non-resident fee (DNR): {mx_soldi(fed['dnr']['importo'])} in {fed['dnr']['anno']}.</strong> This is the fee for the visitor document "
            "of foreign tourists (article 8, fraction I, of the Ley Federal de Derechos). The law says that for visitors arriving by air the international airline "
            "collects it and pays it to the tax authority. Visitors arriving by land do not pay it if they stay no more than 7 days; for longer stays it is paid when they leave (article 11).</li>",
            f"<li><strong>Airport migration fee on departure: {mx_soldi(fed['uscita_aeroporto']['importo'])} in {fed['uscita_aeroporto']['anno']}</strong>, for passengers leaving "
            "Mexico on international flights; the law says the airline collects it (article 12).</li>"]
    if crociere:
        voci.append(f"<li><strong>Cruise passengers.</strong> {escape(mx_crociere_testo())} In Quintana Roo they also pay a state fee of US${qr['crociere_usd']} per passenger, "
                    "charged with the cruise ticket and only at the first Quintana Roo port of the trip; paying it exempts them from the Visitax (article 51-Nonies).</li>")
    voci.append(f"<li><strong>Quintana Roo lodging tax: {al['percento']}% of the lodging price</strong> ({al['percento_case']}% for houses, apartments and villas), "
                "on the room only, not on food and other services (Ley del Impuesto al Hospedaje, articles 4 and 8). It is due on the payment for the stay.</li>")
    return "<ul>" + "".join(voci) + "</ul>"


def mx_fonti_extra():
    fed, qr = MX["federali"], MX["quintana_roo"]
    righe = [(fed["dnr"]["titolo"], fed["dnr"]["url"], fed["dnr"]["formato"], fed["dnr"]["controllato_il"]),
             (fed["crociere"]["titolo"], fed["crociere"]["url"], fed["crociere"]["formato"], fed["crociere"]["controllato_il"]),
             (qr["crociere"]["titolo"], qr["crociere"]["url"], "PDF (Spanish)", qr["crociere"]["controllato_il"]),
             (qr["alloggio"]["titolo"], qr["alloggio"]["url"], qr["alloggio"]["formato"], qr["alloggio"]["controllato_il"]),
             (qr["codice_fiscale"]["titolo"], qr["codice_fiscale"]["url"], qr["codice_fiscale"]["formato"], qr["codice_fiscale"]["controllato_il"])]
    return "".join(f'<li><a href="{escape(u)}" rel="noopener">{escape(t)}</a> – {escape(fm)}, checked {data_lunga(c)}</li>' for t, u, fm, c in righe)


def mx_faq_comuni():
    o, f = mx_ora(), mx_futura()
    p = UMA["prossima"]
    fed = MX["federali"]["dnr"]
    q = [(f"How much is the Visitax in {o['anno']}?",
          f"From {data_lunga(o['dal'])} the Visitax is {mx_soldi(o['valore'])} per foreign visitor: 2.50 UMA under article 51-Octies of the Quintana Roo Law on Fees, "
          f"with the {o['anno']} UMA of {mx_soldi(o['uma'])} published by INEGI ({mx_formula_testo(o)})."),
         ("Do children pay the Visitax?",
          "Yes. The official Visitax portal says there is no adult or child rate: all foreign tourists must pay, whatever their age."),
         ("Is Visitax a scam?",
          f"No. The Visitax is a real fee set by the law of Quintana Roo, and the official portal is {MX_VIS['sito_ufficiale_nome']}, run by the state tax administration (SATQ). "
          f"The official fee is {mx_soldi(o['valore'])}; third-party sites may charge a service fee."),
         ("Who collects Mexico's non-resident fee (DNR)?",
          f"The DNR is {mx_soldi(fed['importo'])} in {fed['anno']}. The Ley Federal de Derechos says that for foreign visitors arriving by air, the international airline collects it "
          "and pays it to the tax authority. If you arrive by land and stay no more than 7 days, you do not pay it.")]
    if f:
        q.append((f"How much will the Visitax be in {f['anno']}?", f"From {data_lunga(f['dal'])}: {mx_soldi(f['valore'])} per person ({mx_formula_testo(f)})."))
    elif not any(v["anno"] == p["anno"] for v in UMA_VALORI):
        q.append((f"How much will the Visitax be in {p['anno']}?",
                  f"From {data_lunga(p['dal'])} it will be 2.50 × the {p['anno']} UMA. INEGI publishes the new UMA in January, and this page updates when it does. "
                  f"Until {data_lunga(_giorno_prima(p['dal']))} the amount stays at {mx_soldi(o['valore'])}."))
    return q


def mx_faq_html(faq):
    html = "".join(f'<details class="faq"><summary>{escape(a)}</summary><p>{escape(b)}</p></details>' for a, b in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": a, "acceptedAnswer": {"@type": "Answer", "text": b}} for a, b in faq]}
    return f'<h2>Questions</h2><div class="faq-box">{html}</div>', ld


def mx_box_cambi(rel):
    v = next((x for x in CAMBI["voci"] if x.get("uma")), None)
    righe = []
    if v:
        righe.append(f"<li><strong>{data_lunga(v['dal'])}:</strong> Visitax {escape(v['importo'])}</li>")
    for x in CAMBI["voci"]:
        if x["slug"] == "mexico" and not x.get("uma"):
            righe.append(f"<li><strong>{data_lunga(x['dal'])}:</strong> cruise passengers, {escape(x['importo'][0].lower() + x['importo'][1:])}</li>")
    return (f'<section class="card callout cambi-box" aria-label="Changes in 2027"><span class="ic">{ico("calendar")}</span>'
            f'<div><p><strong>What changes in 2027</strong></p><ul>{"".join(righe)}</ul>'
            f'<p class="small"><a href="{rel}tourist-tax-changes-2027/">All tourist tax changes in 2027, with official sources</a></p></div></section>')


def box_noleggio_mx():
    """Riquadro DiscoverCars (affiliati.json, voce _discovercars_messico), solo nelle pagine Messico e dopo le informazioni ufficiali."""
    v = AFFILIATI.get("_discovercars_messico") or {}
    url = (v.get("url") or "").strip()
    if not url:
        return ""
    return (f'<section class="card noleggio-mx" style="margin-top:22px"><h2 style="margin-top:0">{escape(v["titolo"])}</h2>'
            f'<p style="margin:0 0 8px"><a href="{escape(url)}" rel="sponsored noopener" target="_blank">{escape(v["nome"])}</a>: {escape(v["testo"])}</p>'
            f'<p class="small" style="margin:0">{MON.RIGA_EN}</p></section>')


def mx_griglia(rel, salta=""):
    return ('<div class="griglia">' + "".join(f'<a href="{rel}{d["slug"]}/">{escape(d["name"])}<small>Visitax {mx_soldi(mx_ora()["valore"])} per person</small></a>'
                                              for d in MX_DEST if d["slug"] != salta) + "</div>")


def pagina_messico_dest(R):
    slug = R["slug"]
    rel = "../"
    pg = MX["pagine"][slug]
    o = mx_ora()
    sub = {"crociere_usd": MX["quintana_roo"]["crociere_usd"], "alloggio": MX["quintana_roo"]["alloggio"]["percento"],
           "alloggio_case": MX["quintana_roo"]["alloggio"]["percento_case"], "crociere_federale": mx_crociere_testo()}
    faq = [(a.format(**sub), b.format(**sub)) for a, b in pg["faq"]] + mx_faq_comuni()
    faq_html, ld = mx_faq_html(faq)
    note = "".join(f"<li>{escape(n)}</li>" for n in [pg["luogo"]] + [n for n in R["note"] if "is in the state of Quintana Roo" not in n])
    esenzioni = "<ul>" + "".join(f"<li>{escape(e)}</li>" for e in R["esenzioni"]) + "</ul>"
    h1 = f"{R['name']} tourist tax {mx_anno()}: Visitax {mx_soldi(o['valore'])} per foreign visitor"
    corpo = f"""<section class="hero">{h1_diviso(h1)}
<p class="risposta">{escape(mx_risposta(R['name'], crociere=slug == "cozumel"))}</p></section>
<section class="card summary" aria-label="Summary">
<div><p class="cifra"><span class="lab">{ico("receipt")}Visitax {o['anno']}</span><span class="sr">: </span><strong>{escape(riassunto(R))}</strong></p>
{chips(R, "Mexico", "Quintana Roo")}</div>
<div><p class="lead">{escape(R['official_name'])}. The calculator below multiplies the official amount for your arrival date by the number of foreign travellers.</p>
{fonte_breve(R)}</div>
</section>
{mx_avviso_ufficiale(rel)}
{mx_box_cambi(rel)}
{modulo_calcolatore("regola", rel=rel, cat_default="all")}
{mx_formula_html()}
<p class="esempio">{esempio(R)}</p>
{AVVISO_MX}
{AD}
<h2>Visitax by year</h2>
{mx_tabella_anni()}
<h2>What to know in {escape(R['name'])}</h2>
<ul>{note}</ul>
<p><strong>Who collects it:</strong> {escape(R['chi_riscuote'])}</p>
<h2>Exemptions (official)</h2>
{esenzioni}
<h2>Other fees for foreign visitors to Mexico</h2>
{mx_altre_tasse(rel)}
{faq_html}
<h2>Official sources</h2>
{fonti_html(R)}<ul>{mx_fonti_extra()}</ul>
<p class="small">Spotted a change in the official amount? <a href="{rel}contact/?ref={slug}">Tell us</a>.</p>
{box_noleggio_mx()}
<h2>Other places in Quintana Roo</h2>
{mx_griglia(rel, slug)}
<p><a href="{rel}mexico/">All tourist taxes and fees in Mexico</a> · <a href="{rel}tourist-tax-changes-2027/">Tourist tax changes in 2027</a></p>
{blocco_dati("regola", [R])}"""
    descr = (f"{R['name']} tourist tax: the Quintana Roo Visitax is {mx_soldi(o['valore'])} per foreign visitor of any age (2.50 × UMA {mx_soldi(o['uma'])}). "
             "Official law and calculator.")
    pagina(f"{slug}/", mx_titolo(pg["titolo_nome"]), descr, corpo,
           briciole=[("Mexico", "mexico/"), (R["name"], f"{slug}/")], jsonld_extra=ld)


def pagina_messico():
    rel = "../"
    o = mx_ora()
    fed, qr = MX["federali"], MX["quintana_roo"]
    R = dict(MX_DEST[0], name="Quintana Roo (Visitax)", slug="mexico")
    faq = mx_faq_comuni()
    faq.insert(4, ("Do cruise passengers pay the Visitax?",
                   f"No, if they paid the Quintana Roo cruise passenger fee: US${qr['crociere_usd']} per passenger, charged with the cruise ticket (article 51-Nonies). "
                   + mx_crociere_testo()))
    faq_html, ld = mx_faq_html(faq)
    cr = mx_crociere_ora()
    tab = [("Visitax (Quintana Roo)", "Foreign visitors entering Quintana Roo, any age", f"<strong>{mx_soldi(o['valore'])}</strong> (2.50 × UMA {mx_soldi(o['uma'])})",
            f'Online on <a href="{escape(MX_VIS["sito_ufficiale"])}" rel="noopener">{escape(MX_VIS["sito_ufficiale_nome"])}</a> or through companies authorised by the SATQ'),
           ("Non-resident fee (DNR, federal)", "Foreign tourists (visitors without permission to work)", f"<strong>{mx_soldi(fed['dnr']['importo'])}</strong> ({fed['dnr']['anno']})",
            "Air: collected by the international airline (law). Land: free for stays of up to 7 days"),
           ("Airport migration fee (federal)", "Passengers leaving Mexico on international flights", f"<strong>{mx_soldi(fed['uscita_aeroporto']['importo'])}</strong> ({fed['uscita_aeroporto']['anno']})",
            "Collected by the airline (law)")]
    if cr:
        tab.append(("Cruise passengers (federal)", "Foreign cruise passengers, first entry", f"<strong>US${cr['usd']}</strong> in pesos until {data_lunga(cr['al'])}",
                    "Reduced DNR set by the decree of 30 June 2025"))
    tab += [("Cruise passengers (Quintana Roo)", "Passengers of cruise ships calling at a Quintana Roo port", f"<strong>US${qr['crociere_usd']}</strong>",
             "Charged with the cruise ticket; replaces the Visitax"),
            ("Lodging tax (Quintana Roo)", "Guests of hotels and rentals", f"<strong>{qr['alloggio']['percento']}%</strong> ({qr['alloggio']['percento_case']}% houses, apartments, villas)",
             "On the payment for the stay (room only)")]
    righe = "".join(f"<tr><td>{a}</td><td>{c}</td><td>{escape(b)}</td><td>{d}</td></tr>" for a, b, c, d in tab)
    altri = ", ".join(MX["luoghi_senza_pagina"])
    h1 = f"Mexico tourist tax {mx_anno()}: Visitax {mx_soldi(o['valore'])}, DNR {mx_soldi(fed['dnr']['importo'])} and cruise fees"
    risp = (mx_risposta("Quintana Roo (Cancún, Tulum, Playa del Carmen, Cozumel, Isla Mujeres, Holbox)")
            + f" Foreign tourists also pay Mexico's federal non-resident fee (DNR) of {mx_soldi(fed['dnr']['importo'])} in {fed['dnr']['anno']} "
            "(Ley Federal de Derechos, article 8): the airline collects it if you fly in, and it is not due for land arrivals staying up to 7 days.")
    corpo = f"""<section class="hero">{h1_diviso(h1)}
<p class="risposta">{escape(risp)}</p></section>
<h2 class="sr">At a glance</h2>
<div class="tab"><table><thead><tr><th>Fee</th><th>Amount</th><th>Who pays</th><th>How it is paid</th></tr></thead><tbody>{righe}</tbody></table></div>
<p class="fonte">Official sources: <a href="{escape(MX_VIS['legge']['url'])}" rel="noopener">Ley de Derechos del Estado de Quintana Roo</a> · <a href="{escape(UMA_VALORI[-1]['fonte']['url'])}" rel="noopener">INEGI UMA {UMA_VALORI[-1]['anno']}</a> · <a href="{escape(fed['dnr']['url'])}" rel="noopener">Ley Federal de Derechos</a> · <a href="{escape(fed['crociere']['url'])}" rel="noopener">decree of 30 June 2025</a> · checked on {MX_CHECK}</p>
{mx_avviso_ufficiale(rel)}
{mx_box_cambi(rel)}
<h2>Visitax calculator</h2>
{modulo_calcolatore("regola", rel=rel, cat_default="all")}
{mx_formula_html()}
<p class="esempio">{esempio(R)}</p>
{AVVISO_MX}
{AD}
<h2>Visitax by year</h2>
{mx_tabella_anni()}
<h2>Where the Visitax applies</h2>
<p>In the whole state of Quintana Roo. Pages with a calculator:</p>
{mx_griglia(rel)}
<p>The same fee applies in {escape(altri)} and every other place in Quintana Roo: it is a state fee with one amount for the whole state.</p>
<h2>Who pays and how</h2>
<ul><li>All foreign tourists who visit Quintana Roo pay it, children included: the official portal says there is no adult or child rate.</li>
<li>The law says it is due when you enter the state. The official portal asks for your arrival and departure dates and the passport of each traveller, and gives a QR code for each person; you can download it again with "Recover your receipt".</li>
<li>Exempt: foreign visitors entering through the state's southern border, and cruise passengers who paid the Quintana Roo cruise passenger fee.</li></ul>
<h2>Other fees for foreign visitors to Mexico</h2>
{mx_altre_tasse(rel)}
<h2>Not covered</h2>
<p>{escape(MX['non_coperti'])}</p>
{faq_html}
<h2>Official sources</h2>
{fonti_html(R)}<ul>{mx_fonti_extra()}</ul>
<p class="small">Spotted a change in an official amount? <a href="{rel}contact/?ref=mexico">Tell us</a>.</p>
{box_noleggio_mx()}
<p><a href="{rel}">Tourist tax calculator</a> · <a href="{rel}tourist-tax-changes-2027/">Tourist tax changes in 2027</a></p>
{blocco_dati("regola", [R])}"""
    descr = (f"Mexico tourist tax: Visitax {mx_soldi(o['valore'])} per person in Cancún and Quintana Roo, federal DNR {mx_soldi(fed['dnr']['importo'])}, "
             "cruise and hotel taxes. Official laws and a calculator.")
    pagina("mexico/", mx_titolo("Mexico", f", DNR {mx_soldi(fed['dnr']['importo'])}"), descr, corpo,
           briciole=[("Mexico", "mexico/")], jsonld_extra=ld)


# ---------------------------------------------------------------- Giappone: rimborso dell'imposta sui consumi dal 1/11/2026
# Pagina /japan-tax-free-refund/ (30/10/2026). Fatti da dati/giappone_rimborso.json (fonti ufficiali in inglese: Japan Tourism
# Agency, National Tax Agency, Japan Customs). Il calcolatore (JP_JS) e jp_rimborso() danno lo stesso risultato; verifica.py (punto 10)
# li confronta con un calcolo indipendente in frazioni esatte.
JP = json.loads((DATI / "giappone_rimborso.json").read_text(encoding="utf-8"))
JP_F = JP["fonti"]
JP_SLUG = "japan-tax-free-refund/"
JP_CHECK = data_lunga(JP["controllato_il"])


def jp_rimborso(a10, a8, incluse=True, soglia=None):
    """Rimborso massimo teorico negli acquisti di un giorno in un negozio. a10 = beni al 10 %, a8 = alimenti e bevande all'8 %,
    in yen interi; incluse = gli importi comprendono l'imposta (prezzo pagato dal 1/11/2026). Imposta arrotondata per difetto
    allo yen; soglia di 5.000 yen sul totale al netto dell'imposta (stessi passaggi di JP_JS)."""
    soglia = JP["soglia_yen"] if soglia is None else soglia
    a10, a8 = max(0, int(round(a10 or 0))), max(0, int(round(a8 or 0)))
    if incluse:
        t10, t8, n10, n8 = math.floor(a10 * 10 / 110), math.floor(a8 * 8 / 108), a10 * 100 / 110, a8 * 100 / 108
    else:
        t10, t8, n10, n8 = math.floor(a10 * 10 / 100), math.floor(a8 * 8 / 100), a10, a8
    netto = n10 + n8
    ok = netto >= soglia - 1e-9
    return {"netto": netto, "ok": ok, "t10": t10 if ok else 0, "t8": t8 if ok else 0, "tot": (t10 + t8) if ok else 0}


JP_JS = r"""
function jpRimborso(a10,a8,incl,soglia){a10=Math.max(0,Math.round(+a10||0));a8=Math.max(0,Math.round(+a8||0));var t10,t8,n10,n8;
  if(incl){t10=Math.floor(a10*10/110);t8=Math.floor(a8*8/108);n10=a10*100/110;n8=a8*100/108;}else{t10=Math.floor(a10*10/100);t8=Math.floor(a8*8/100);n10=a10;n8=a8;}
  var netto=n10+n8,ok=netto>=soglia-1e-9;return {netto:netto,ok:ok,t10:ok?t10:0,t8:ok?t8:0,tot:ok?t10+t8:0};}
"""

JP_APP_JS = r"""
(function(){var box=document.querySelector('[data-jp]');if(!box)return;var f=box.querySelector('form'),out=box.querySelector('[data-out]');
  var S=+box.dataset.soglia;function y(v){return '¥'+Math.floor(v+0.5+1e-9).toLocaleString('en-US');}
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function agg(){var a10=+f.a10.value||0,a8=+f.a8.value||0,incl=f.modo.value==='incl';var o=jpRimborso(a10,a8,incl,S);
    var h='<div class="r-lab">Maximum refund</div><div class="tot">'+y(o.tot)+'</div>';
    h+='<dl class="r-dl"><div><dt>Spent before tax</dt><dd>'+y(o.netto)+'</dd></div><div><dt>Minimum '+y(S)+'</dt><dd>'+(o.ok?'Reached':'Not reached')+'</dd></div></dl><ul class="r-righe">';
    if(!o.ok){h+='<li>Below '+y(S)+' before tax in one shop on one day: this purchase does not qualify for the tax-free refund.</li>';}
    else{if(a10>0)h+='<li><span>Goods at 10%: '+esc(y(Math.round(a10)))+(incl?' including tax':' before tax')+'</span><strong class="eq">= '+y(o.t10)+'</strong></li>';
      if(a8>0)h+='<li><span>Food and drink at 8%: '+esc(y(Math.round(a8)))+(incl?' including tax':' before tax')+'</span><strong class="eq">= '+y(o.t8)+'</strong></li>';}
    h+='<li>Theoretical maximum: the tax on your receipt. How it is paid, and whether the refund provider deducts anything, depends on the shop.</li></ul>';
    out.innerHTML=h;}
  f.addEventListener('input',agg);f.addEventListener('change',agg);f.addEventListener('submit',function(e){e.preventDefault();});agg();})();
"""


def yen(v):
    return soldi(v, "JPY")


def jp_link(chiave, testo=None):
    f = JP_F[chiave]
    return f'<a href="{escape(f["url"])}" rel="noopener">{escape(testo or f["titolo"])}</a>'


def jp_risposta():
    a = JP["aliquote"]
    return (f"From {data_lunga(JP['in_vigore_dal'])}, visitors to Japan pay the {a['standard']}% consumption tax ({a['ridotta']}% on food and drink) "
            f"at tax-free shops and get it back after Japan Customs checks the goods at the airport or seaport within {JP['giorni_dogana']} days of purchase, "
            f"if they spend at least {yen(JP['soglia_yen'])} before tax in one shop on one day (Japan Tourism Agency and National Tax Agency, checked on {JP_CHECK}). "
            f"Purchases made until {data_lunga(_giorno_prima(JP['in_vigore_dal']))} follow the old system, where the tax was taken off at the till.")


def jp_faq():
    a, p = JP["aliquote"], JP["tassa_partenza"]
    s, g = yen(JP["soglia_yen"]), JP["giorni_dogana"]
    es = jp_rimborso(33000, 0)
    aer = ", ".join(JP["aeroporti_vjw"][:-1]) + " and " + JP["aeroporti_vjw"][-1]
    return [
        ("How does tax-free shopping in Japan change in November 2026?",
         f"For purchases made from {data_lunga(JP['in_vigore_dal'])}, tax-free shops charge the consumption tax at the till. You get it back after Japan Customs "
         f"confirms at the airport or seaport, within {g} days of the purchase, that you are taking the goods out of Japan. Until "
         f"{data_lunga(_giorno_prima(JP['in_vigore_dal']))} the tax was taken off at the till."),
        ("What is the minimum spend for a tax refund in Japan?",
         f"{s} or more before tax, in the same shop on the same day. From {data_lunga(JP['in_vigore_dal'])} general goods and consumables (food, drinks, cosmetics) "
         "count together and there is no maximum amount, but you may only buy what you can carry out of Japan yourself."),
        ("What percentage is the Japan tax refund?",
         f"The refund is the consumption tax: {a['standard']}% of the price before tax for most goods, {a['ridotta']}% for food and drink (not alcohol or eating out). "
         f"On a price that includes tax, that is 10/110 (about 9.1%) or 8/108 (about 7.4%). For example, {yen(33000)} including tax gives back up to {yen(es['tot'])}."),
        ("Where do I get the tax refund at the airport in Japan?",
         "At a Tax Refund Kiosk (tax-free procedure terminal) in the international departure lobby, before you check in your luggage. You scan your passport: "
         "a green result means you are done, a red result means a customs officer checks your goods. "
         f"At {aer} airports you can also do it online with Visit Japan Web, on the dedicated Wi-Fi before the security check."),
        ("When and how do I get the money back?",
         "After the customs check. The tax-free shop, or the refund service provider it uses, pays you with the refund method you registered when you bought the goods. "
         "The official sources list bank transfer, credit card, app or cash at the port of departure after the customs check; methods vary by shop, so ask when you buy."),
        ("Can I eat or use tax-free items before leaving Japan?",
         "Not if you want the refund. Sealed packaging is no longer required, but food, drinks and cosmetics used in Japan are not eligible. Customs checks each receipt as a whole: "
         "if one item from a receipt is missing, nothing on that receipt is refunded. If you used something, tell a customs officer at the counter instead of using the kiosk."),
        ("Who can get the tax refund in Japan?",
         "Foreign nationals who do not live in Japan and have been in the country for less than six months since entry, for example as a Temporary Visitor, with their passport. "
         "Japanese nationals who have lived abroad for two years or more can also use it within six months of a temporary return, with a supporting document."),
        ("Is the Japan departure tax going up in 2026?",
         f"It already has. The International Tourist Tax is {yen(p['importo'])} per departure from Japan from {data_lunga(p['dal'])} (it was {yen(p['prima'])}). "
         f"Airlines and shipping companies collect it from passengers; children under {p['esenti_sotto_anni']} do not pay. If you bought your ticket before "
         f"{data_lunga(p['dal'])} for a fixed departure date, the old {yen(p['prima'])} usually applies. It is separate from the tax-free refund."),
    ]


def jp_callout(rel):
    """Riquadro di collegamento alla pagina del rimborso (home, pagina Giappone, pagine dei luoghi giapponesi)."""
    return (f'<section class="card callout jp-box" aria-label="Japan tax-free refund"><span class="ic">{ico("receipt")}</span>'
            f'<p><strong>Shopping in Japan?</strong> From {data_lunga(JP["in_vigore_dal"])} tax-free shops charge the {JP["aliquote"]["standard"]}% tax and refund it after a customs check when you leave. '
            f'<a href="{rel}{JP_SLUG}">Japan tax-free refund: rules and calculator</a></p></section>')


def pagina_giappone_rimborso():
    rel = "../"
    a, p, s, g = JP["aliquote"], JP["tassa_partenza"], yen(JP["soglia_yen"]), JP["giorni_dogana"]
    sc = JP["esempio_scadenza"]
    faq = jp_faq()
    faq_html = "".join(f'<details class="faq"><summary>{escape(q)}</summary><p>{escape(r)}</p></details>' for q, r in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]}
    e1, e2 = jp_rimborso(33000, 0), jp_rimborso(22000, 10800)
    confronto = [
        ("At the till", "Tax taken off: you paid the price before tax", f"You pay the price <strong>including tax</strong> and register a refund method"),
        ("Minimum spend", f"{s} before tax per shop per day", f"<strong>{s}</strong> before tax per shop per day (unchanged)"),
        ("Food, drinks, cosmetics", f"Separate category, maximum {yen(500000)}, sealed special packaging", "Same rules as other goods, <strong>no maximum</strong>, no special packaging"),
        ("How much you can buy", "Not for business use or resale", "Only what you can <strong>carry out of Japan yourself</strong>"),
        ("At departure", "Passport shown to customs", f"Passport at a kiosk <strong>within {g} days</strong> of purchase, before luggage check-in; goods may be inspected"),
        ("The money", "–", "Refunded by the shop or its refund provider <strong>after the customs check</strong>"),
    ]
    righe = "".join(f"<tr><td>{x}</td><td>{escape(y)}</td><td>{z}</td></tr>" for x, y, z in confronto)
    aer = ", ".join(JP["aeroporti_vjw"][:-1]) + " and " + JP["aeroporti_vjw"][-1]
    calc = f"""<div class="card calc" data-jp data-soglia="{JP['soglia_yen']}">
<div class="calc-grid">
<form autocomplete="off">
<div class="campi">
<label class="pieno"><span class="lt">{ico("tag")}Prices you enter</span><select name="modo"><option value="incl">Including tax (the price you pay)</option><option value="escl">Before tax</option></select></label>
<label><span class="lt">{ico("receipt")}Goods at {a['standard']}% (¥)</span><input type="number" name="a10" min="0" step="1" value="33000" inputmode="numeric"></label>
<label><span class="lt">{ico("receipt")}Food and drink at {a['ridotta']}% (¥)</span><input type="number" name="a8" min="0" step="1" value="0" inputmode="numeric"></label>
<p class="small pieno" style="margin:0">One shop, one day. {a['standard']}%: clothes, electronics, cosmetics, alcohol and most goods. {a['ridotta']}%: food and drinks, except alcohol.</p>
</div>
</form>
<div class="calc-out">
<div class="risultato" data-out aria-live="polite"><noscript>Turn on JavaScript to use the calculator. The formula and examples below show how the refund is worked out.</noscript></div>
</div>
</div>
</div>"""
    corpo = f"""<section class="hero">{h1_diviso(f"Japan tax-free shopping from {data_lunga(JP['in_vigore_dal'])}: you pay the tax, then get it back")}
<p class="risposta">{escape(jp_risposta())}</p>
<p class="fonte">Official sources: {jp_link("jta_viaggiatori", "Japan Tourism Agency (Refund Method, for travellers)")} · {jp_link("nta_rimborso", "National Tax Agency (FY2025 tax reform)")} · {jp_link("dogana", "Japan Customs")} · checked on {JP_CHECK}</p></section>
<h2>Before and after {data_lunga(JP['in_vigore_dal'])}</h2>
<div class="tab sintesi jp-conf"><table><thead><tr><th>What</th><th>Until {data_lunga(_giorno_prima(JP['in_vigore_dal']))}</th><th>From {data_lunga(JP['in_vigore_dal'])}</th></tr></thead><tbody>{righe}</tbody></table></div>
<p class="fonte">Official sources: {jp_link("jta_cambi", "Japan Tourism Agency, Changes to Tax-Free Goods")} · {jp_link("nta_rimborso", "National Tax Agency")} · checked on {JP_CHECK}</p>
<h2>Tax refund calculator</h2>
{calc}
<details class="formula" open><summary>{ico("calc")}Formula used</summary><p>Maximum refund = the consumption tax on the purchase. Prices before tax: {a['standard']}% × goods at {a['standard']}% + {a['ridotta']}% × food and drink at {a['ridotta']}%. Prices including tax: 10/110 × goods at {a['standard']}% + 8/108 × food and drink at {a['ridotta']}%, rounded down to the yen. No refund if the total before tax in one shop on one day is below {s}. Rates: {jp_link("nta_aliquote", "National Tax Agency, Consumption Tax rate")} (food and drink excluding alcohol and eating out at {a['ridotta']}%), checked on {JP_CHECK}.</p></details>
<p class="esempio">Examples: a jacket for {yen(33000)} including tax → up to <strong>{yen(e1['tot'])}</strong> back. {yen(22000)} of goods at {a['standard']}% and {yen(10800)} of snacks at {a['ridotta']}% in the same shop on the same day → {yen(e2['t10'])} + {yen(e2['t8'])} = <strong>{yen(e2['tot'])}</strong>.</p>
<p class="avviso"><strong>Not tax advice.</strong> This page explains the official rules for travellers. The refund itself comes from the tax-free shop or its refund service provider, which tells you how it is paid: check the details with the shop when you buy.</p>
{AD}
<h2>Who can get the refund</h2>
<ul><li><strong>Foreign nationals who do not live in Japan</strong> and have been in Japan for less than six months since entry, such as Temporary Visitors (most tourists). Show your passport. Diplomats and official visitors are also eligible.</li>
<li>People with a landing permit, for example cruise passengers (passport or a copy of it, with the landing permit), crew members, transit and port-of-call passengers.</li>
<li><strong>Japanese nationals living abroad</strong> for two years or more, within six months of a temporary return to Japan, with their passport and a supporting document (Residency Certificate, a copy of the Koseki no Fuhyō, or a My Number Card showing the move abroad).</li></ul>
<p class="fonte">Official source: {jp_link("jta_beneficiari")} · checked on {JP_CHECK}</p>
<h2>How to get the refund, step by step</h2>
<ol><li><strong>At the tax-free shop.</strong> Show your passport, spend at least {s} before tax that day in that shop, pay the price including tax and register how you want to be refunded (for example a credit card). Keep all the goods.</li>
<li><strong>At the airport or seaport, within {g} days of the purchase.</strong> Before you check in your luggage, scan your passport at a Tax Refund Kiosk in the international departure lobby. Green result: done. Red result: take the goods to the customs inspection area. At {aer} airports you can also do it online with Visit Japan Web, connected to the customs Wi-Fi before the security check. The {g} days start the day after the purchase: goods bought on {data_lunga(sc['acquisto'])} must be checked by {data_lunga(sc['ultimo_giorno'])}.</li>
<li><strong>After the customs check.</strong> The shop or its refund service provider sends the refund with the method you registered. Possible methods are bank transfer, credit card, app or cash at the port of departure; they vary by shop. Questions about the refund go to the shop.</li></ol>
<p class="fonte">Official sources: {jp_link("jta_viaggiatori", "Japan Tourism Agency")} · {jp_link("jta_faq", "Japan Tourism Agency FAQ for travellers")} · {jp_link("dogana", "Japan Customs")} · {jp_link("dogana_mappe", "kiosk locations at each airport and seaport")} · checked on {JP_CHECK}</p>
<h2>What can stop the refund</h2>
<ul><li><strong>Checking in your luggage first.</strong> You must have all the goods with you at the kiosk. Checked luggage cannot be taken back for the tax-free procedure, and neither the airline nor customs compensates you if you miss your flight because of it.</li>
<li><strong>One missing item.</strong> Customs checks each receipt as a whole: if one item from a receipt is missing (for example snacks you ate), nothing on that receipt is refunded. If you used something, do not use the kiosk: tell a customs officer at the counter.</li>
<li><strong>Using consumables in Japan.</strong> Food, drinks and cosmetics used in Japan are not eligible, even though sealed packaging is no longer required.</li>
<li><strong>Connecting flights.</strong> If you fly from a Japanese city to your international departure airport, do the procedure at the airport where you leave Japan.</li>
<li><strong>Items of {yen(JP['limite_un_milione_yen'])} or more</strong> before tax: customs may ask for a certificate of authenticity or a warranty, so keep it with the item.</li>
<li><strong>Not taking the goods out.</strong> If goods checked by customs do not leave Japan, the tax is collected and penalties apply.</li></ul>
<h2>What you cannot buy tax-free</h2>
<ul><li>Gold and platinum bullion, gold and platinum coins, and goods that are exempt from consumption tax.</li>
<li>More than you can carry out of Japan yourself at departure. Separate shipping by post of tax-free goods ended on 31 March 2025; some shops can ship abroad for you: ask the shop.</li></ul>
<p class="fonte">Official sources: {jp_link("nta_rimborso", "National Tax Agency")} · {jp_link("jta_faq", "Japan Tourism Agency FAQ")} · checked on {JP_CHECK}</p>
<h2>Departure tax: {yen(p['importo'])} from {data_lunga(p['dal'])}</h2>
<p>Japan's International Tourist Tax (the departure tax) went up from {yen(p['prima'])} to <strong>{yen(p['importo'])} per departure</strong> on {data_lunga(p['dal'])}. Airlines and shipping companies collect it from passengers. Children under {p['esenti_sotto_anni']} and some transit passengers who leave within 24 hours do not pay. Tickets bought before {data_lunga(p['dal'])} for a fixed departure date usually keep the old {yen(p['prima'])}, unless the departure date is changed after that day. This tax is not refunded by the tax-free system.</p>
<p class="fonte">Official source: {jp_link("nta_tassa_partenza")} · checked on {JP_CHECK}</p>
<p>Staying overnight? {sum(1 for e in JT["enti"] if e["stato"] == "in_vigore")} Japanese prefectures and cities also charge an accommodation tax, for example <a href="{rel}tokyo/">Tokyo</a>, <a href="{rel}kyoto/">Kyoto</a>, <a href="{rel}{JT_ENTI["osaka"]["pagina"]}">Osaka</a>, <a href="{rel}sapporo/">Sapporo</a> and <a href="{rel}{JT_ENTI["fukuoka"]["pagina"]}">Fukuoka</a>. See <a href="{rel}{JT_HUB}">the Japan accommodation tax in every place, with a calculator</a>.</p>
<h2>Questions</h2>
<div class="faq-box">{faq_html}</div>
<h2>Official sources</h2>
<ul>{"".join(f'<li><a href="{escape(f["url"])}" rel="noopener">{escape(f["titolo"])}</a> – {escape(f["formato"])}, checked {data_lunga(f["controllato_il"])}</li>' for f in JP_F.values())}</ul>
<p class="small">Spotted a change in the official rules? <a href="{rel}contact/?ref=japan-tax-free-refund">Tell us</a>.</p>
<p><a href="{rel}country/japan/">Tourist taxes in Japan</a> · <a href="{rel}">Tourist tax calculator</a> · <a href="{rel}tourist-tax-changes-2027/">Tourist tax changes in 2027</a></p>"""
    pagina(JP_SLUG, "Japan tax free refund from November 2026: rules and calculator",
           f"From {data_lunga(JP['in_vigore_dal'])} Japan refunds the {a['standard']}% consumption tax ({a['ridotta']}% on food) after a customs check at departure. "
           f"Minimum {s} per shop per day, {g} days. Calculator and official sources.",
           corpo, briciole=[("Japan", "country/japan/"), ("Tax-free refund from November 2026", JP_SLUG)], extra_js=JP_JS + JP_APP_JS, jsonld_extra=ld)


# ---------------------------------------------------------------- Giappone: tasse di soggiorno (宿泊税) in tutto il paese (31/10/2026)
# Dati: dati/giappone_tasse.json (49 enti in vigore e 18 approvati per il 2027, dall'elenco del Ministero degli Affari interni al
# 1/10/2026; tariffe dai consensi del Ministro e dalle pagine degli enti). Ogni ente è un "luogo" del calcolatore: per un Comune
# si sommano la tassa comunale e quella della Prefettura (con la tariffa della Prefettura dentro quel Comune, "pref_regole"); dove
# la percentuale comunale comprende già la tassa della Prefettura (Kutchan, Niseko dal 1/11/2026, Tomakomai, Kitahiroshima) la
# Prefettura non si aggiunge ("include_pref"). jt_calcola() e JT_JS danno lo stesso risultato (verifica.py, controllo 11).
JT = json.loads((DATI / "giappone_tasse.json").read_text(encoding="utf-8"))
JT_ELENCO = json.loads((DATI / "giappone_elenco_mic.json").read_text(encoding="utf-8"))
JT_ENTI = {e["id"]: e for e in JT["enti"]}
JT_PREF = {e["pref"]: e for e in JT["enti"] if e["livello"] == "prefecture"}
JT_HUB = "japan-accommodation-tax/"
JT_27 = "japan-accommodation-tax-2027/"
JT_CHECK = data_lunga(JT["controllato_il"])
JT_LISTA_AL = data_lunga(JT_ELENCO["alla_data"])
JT_PREZZO_LAB = "Room-only price per night for all guests (¥)"
JT_ESEMPIO = {"okinawa": 17000, "ishigaki": 17000, "miyakojima": 17000, "motobu": 17000, "onna": 17000, "chatan": 17000, "nago": 17000}
JT_FONTE_NOMI = [("soumu.go.jp", "Ministry of Internal Affairs and Communications"), ("hokkaido-shukuhakuzei.pref.hokkaido", "Hokkaido Government"),
                 ("pref.hokkaido.lg.jp", "Hokkaido Government"), ("town.niseko", "Niseko Town"), ("pref.fukuoka", "Fukuoka Prefecture"),
                 ("pref.okinawa", "Okinawa Prefecture"), ("pref.nagano", "Nagano Prefecture"), ("city.nagasaki", "Nagasaki City"),
                 ("kanazawa", "Kanazawa City"), ("tax.metro.tokyo", "Tokyo Bureau of Taxation"), ("city.kyoto", "Kyoto City"),
                 ("city.sapporo", "Sapporo City")]


def jt_nome_fonte(url):
    return next(n for k, n in JT_FONTE_NOMI if k in url)


def jt_luogo(e):
    """Luogo del calcolatore: componenti (tassa del Comune e della Prefettura) con le loro regole."""
    eta = lambda x: bool(x.get("eta_esente"))
    comp = [{"label": e["nome_tassa"], "regole": e["regole"], "eta": eta(e), "pref": False}]
    P = JT_PREF.get(e["pref"]) if e["livello"] == "municipality" else None
    if P:
        comp.append({"label": P["nome_tassa"], "regole": e.get("pref_regole", P["regole"]), "eta": eta(P), "pref": True})
    etichetta = JT["eta"][e["eta_esente"]]["label"] if e.get("eta_esente") else ""
    return {"id": e["id"], "nome": e["en"], "pref": (P or e)["en"] if e["livello"] == "municipality" and P else (e.get("pref_en") or e["en"]),
            "pagina": e["pagina"], "comp": comp, "eta_label": etichetta, "prezzo": JT_ESEMPIO.get(e["id"], 30000),
            "inizio_testo": e.get("inizio_testo") or (data_lunga(e["inizio"]) if e.get("inizio") else ""),
            "tariffe": e.get("inizio_nota") == "tariffe"}


JT_LUOGHI = [jt_luogo(e) for e in JT["enti"]]
JT_L = {x["id"]: x for x in JT_LUOGHI}


def jt_regola(regole, d):
    for r in regole:
        if (not r.get("dal") or r["dal"] <= d) and (not r.get("al") or d <= r["al"]):
            return r
    return None


def jt_quota(r, pp):
    """Imposta a persona per notte per un prezzo a persona pp (stessi passaggi di jtQuota nel JS)."""
    if r["tipo"] == "bande":
        for lo, hi, v in r["bande"]:
            if pp >= lo and (hi is None or pp < hi):
                return v
        return 0
    if pp < r.get("min", 0):
        return 0
    base = pp
    if r.get("arrot"):
        base = math.floor(base / r["arrot"]) * r["arrot"]
    if r.get("base_max"):
        base = min(base, r["base_max"])
    v = base * r["valore"] / 100
    if r.get("cap") is not None:
        v = min(v, r["cap"])
    return v


def jt_attive(L, d):
    """[(componente, regola)] valide nella data d, senza la Prefettura quando la percentuale comunale la comprende."""
    att = [(c, jt_regola(c["regole"], d)) for c in L["comp"]]
    salta = any(r and r.get("include_pref") for _, r in att)
    return [(c, r) for c, r in att if r and not (c["pref"] and salta)]


def jt_calcola(L, checkin, notti, prezzo, ospiti, bambini=0):
    """prezzo = prezzo della camera senza pasti per notte per tutti gli ospiti; le fasce usano prezzo / ospiti.
    {'totale', 'comp': [[etichetta, importo, notti tassate]], 'prima': notti senza nessuna tassa ancora in vigore, 'inclusa': notti in cui
    la tassa della Prefettura è compresa nella percentuale comunale}. Uguale a jtCalcola nel JS."""
    out = {"totale": 0, "comp": [[c["label"], 0, 0] for c in L["comp"]], "prima": 0, "inclusa": 0}
    if ospiti < 1 or notti < 1:
        return out
    pp = prezzo / ospiti
    bambini = max(0, min(bambini, ospiti))
    d0 = date.fromisoformat(checkin)
    for i in range(notti):
        d = (d0 + timedelta(days=i)).isoformat()
        att = [(k, jt_regola(c["regole"], d)) for k, c in enumerate(L["comp"])]
        if all(r is None for _, r in att):
            out["prima"] += 1
            continue
        salta = any(r and r.get("include_pref") for _, r in att)
        if salta and any(c["pref"] for c in L["comp"]):
            out["inclusa"] += 1
        for k, r in att:
            c = L["comp"][k]
            if r is None or (c["pref"] and salta):
                continue
            n = ospiti - (bambini if c["eta"] else 0)
            out["comp"][k][1] += jt_quota(r, pp) * n
            out["comp"][k][2] += 1
    out["totale"] = sum(x[1] for x in out["comp"])
    return out


JT_JS = r"""
function jtRegola(R,d){for(var i=0;i<R.length;i++){var r=R[i];if((!r.dal||r.dal<=d)&&(!r.al||d<=r.al))return r;}return null;}
function jtQuota(r,pp){if(r.tipo==='bande'){for(var i=0;i<r.bande.length;i++){var b=r.bande[i];if(pp>=b[0]&&(b[1]===null||pp<b[1]))return b[2];}return 0;}
  if(pp<(r.min||0))return 0;var base=pp;if(r.arrot)base=Math.floor(base/r.arrot)*r.arrot;if(r.base_max)base=Math.min(base,r.base_max);
  var v=base*r.valore/100;if(r.cap!==undefined&&r.cap!==null)v=Math.min(v,r.cap);return v;}
function jtCalcola(L,ci,notti,prezzo,ospiti,bambini){var out={totale:0,comp:L.comp.map(function(c){return [c.label,0,0];}),prima:0,inclusa:0};
  if(ospiti<1||notti<1)return out;var pp=prezzo/ospiti;bambini=Math.max(0,Math.min(bambini||0,ospiti));
  var haPref=L.comp.some(function(c){return c.pref;});
  for(var i=0;i<notti;i++){var d=addDays(ci,i);var att=L.comp.map(function(c){return jtRegola(c.regole,d);});
    if(att.every(function(r){return r===null;})){out.prima++;continue;}
    var salta=att.some(function(r){return r&&r.include_pref;});if(salta&&haPref)out.inclusa++;
    for(var k=0;k<att.length;k++){var r=att[k],c=L.comp[k];if(r===null||(c.pref&&salta))continue;
      var n=ospiti-(c.eta?bambini:0);out.comp[k][1]+=jtQuota(r,pp)*n;out.comp[k][2]+=1;}}
  out.totale=out.comp.reduce(function(s,x){return s+x[1];},0);return out;}
"""

JT_APP_JS = r"""
(function(){var box=document.querySelector('[data-jt]');if(!box)return;var D=JSON.parse(document.getElementById('jt-dati').textContent);
  var f=box.querySelector('form'),out=box.querySelector('[data-out]'),sel=f.querySelector('[name=luogo]'),link=box.querySelector('[data-link]');
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function y(v){return soldi(v,'JPY');}
  function oggi(){var x=new Date();return new Date(Date.UTC(x.getFullYear(),x.getMonth(),x.getDate())).toISOString().slice(0,10);}
  function primaData(L){var o=oggi();if(L.comp.some(function(c){return jtRegola(c.regole,o);}))return o;
    var ds=[];L.comp.forEach(function(c){c.regole.forEach(function(r){if(r.dal&&r.dal>o)ds.push(r.dal);});});ds.sort();return ds[0]||o;}
  if(sel){var gr={},ord=[];D.forEach(function(L,i){if(!gr[L.pref]){gr[L.pref]=[];ord.push(L.pref);}gr[L.pref].push(i);});
    sel.innerHTML=ord.map(function(p){return '<optgroup label="'+esc(p)+'">'+gr[p].map(function(i){return '<option value="'+i+'">'+esc(D[i].nome)+'</option>';}).join('')+'</optgroup>';}).join('');}
  function L(){return sel?D[+sel.value]:D[0];}
  function q(n){return f.querySelector('[name='+n+']');}
  function prepara(){var P=L();q('checkin').value=primaData(P);if(!box.dataset.prezzoToccato)q('prezzo').value=P.prezzo;
    var b=f.querySelector('[data-campo=esenti]');b.hidden=!P.eta_label;f.querySelector('[data-lab=esenti]').textContent=P.eta_label||'Children';
    if(link){link.href=link.dataset.base+P.pagina;link.querySelector('span').textContent='Rates, exemptions and official sources for '+P.nome;}}
  function agg(){var P=L();var notti=Math.max(1,Math.min(365,parseInt(q('notti').value,10)||1));var osp=Math.max(1,Math.min(50,parseInt(q('ospiti').value,10)||1));
    var bam=P.eta_label?Math.max(0,parseInt(q('bambini').value,10)||0):0;var pr=Math.max(0,parseFloat(q('prezzo').value)||0);var ci=q('checkin').value||primaData(P);
    var o=jtCalcola(P,ci,notti,pr,osp,bam);
    var h='<div class="r-lab">Estimated accommodation tax for this stay</div><div class="tot">'+y(o.totale)+'</div>';
    h+='<dl class="r-dl"><div><dt>Average per night</dt><dd>'+y(o.totale/notti)+'</dd></div><div><dt>Price per person per night</dt><dd>'+y(pr/osp)+'</dd></div></dl><ul class="r-righe">';
    o.comp.forEach(function(x,k){if(x[2]>0)h+='<li><span>'+esc(x[0])+', '+plur(x[2],'night')+'</span><strong class="eq">= '+y(x[1])+'</strong></li>';});
    if(o.inclusa)h+='<li>'+plur(o.inclusa,'night')+': the '+esc(P.comp[P.comp.length-1].label)+' is included in the percentage above.</li>';
    if(o.prima)h+='<li>'+plur(o.prima,'night')+(P.tariffe?' before the current rates ('+esc(P.inizio_testo)+'): not calculated, earlier rates applied.':(P.inizio_testo?' before the start ('+esc(P.inizio_testo)+')':'')+': no tax yet.')+'</li>';
    if(bam)h+='<li>'+plur(bam,'child','children')+' not counted where the age exemption applies.</li>';
    h+='</ul>';out.innerHTML=h;}
  if(sel)sel.addEventListener('change',function(){prepara();agg();});
  q('prezzo').addEventListener('input',function(){box.dataset.prezzoToccato='1';});
  f.addEventListener('input',function(e){if(e.target!==sel)agg();});f.addEventListener('change',function(e){if(e.target!==sel)agg();});
  f.addEventListener('submit',function(e){e.preventDefault();});prepara();agg();})();
"""


def jt_desc(r, breve_=False):
    """Una regola in parole: '¥200', '¥100–¥500 by price band', '3% of the price', '2% (max ¥2,000)'."""
    if r["tipo"] == "pct":
        s = f"{num(r['valore'])}%" + (f" (max {yen(r['cap'])})" if r.get("cap") is not None else "")
        return s if breve_ else s + " of the price" + (f" from {yen(r['min'])} per person" if r.get("min") else "")
    nz = [v for _, _, v in r["bande"] if v]
    if not nz:
        return "no tax"
    soglia = next((lo for lo, _, v in r["bande"] if v), 0)
    s = yen(min(nz)) if min(nz) == max(nz) else f"{yen(min(nz))}–{yen(max(nz))}" + ("" if breve_ else " by price band")
    return s + (f" (no tax below {yen(soglia)})" if soglia and not breve_ else "")


def jt_desc_lunga(r):
    """Una regola in una frase: '¥200 to ¥500 per person per night by price band, with no tax below ¥5,000'."""
    if r["tipo"] == "pct":
        return (f"{num(r['valore'])}% of the room-only price per person per night" + (f" from {yen(r['min'])} per person" if r.get("min") else "")
                + (f", up to {yen(r['cap'])}" if r.get("cap") is not None else "")
                + (f"; the price is rounded down to the nearest {yen(r['arrot'])}" if r.get("arrot") else ""))
    nz = [v for _, _, v in r["bande"] if v]
    soglia = next((lo for lo, _, v in r["bande"] if v), 0)
    s = (f"{yen(nz[0])} per person per night" if min(nz) == max(nz) else f"{yen(min(nz))} to {yen(max(nz))} per person per night by price band")
    return s + (f", with no tax below {yen(soglia)}" if soglia else "")


def jt_breve(L, d):
    """Cifra complessiva per titolo, H1 e tabelle in una data: '¥300–¥700', '3%', '2% (max ¥2,000)', '3.5% + ¥100'."""
    att = jt_attive(L, d)
    if not att:
        return ""
    pct = [r for _, r in att if r["tipo"] == "pct"]
    fisse = [r for _, r in att if r["tipo"] == "bande"]
    if pct and not fisse:
        tot = sum(r["valore"] for r in pct)
        cap = sum(r["cap"] for r in pct) if all(r.get("cap") is not None for r in pct) else None
        return f"{num(round(tot, 4))}%" + (f" (max {yen(cap)})" if cap is not None else "")
    if pct:
        return " + ".join(jt_desc(r, True) for r in pct + fisse)
    righe = jt_tabella(L, d)
    tot = [x[3] for x in righe if x[3]]
    return yen(min(tot)) if min(tot) == max(tot) else f"{yen(min(tot))}–{yen(max(tot))}"


def jt_unita(L, d):
    att = jt_attive(L, d)
    if att and all(r["tipo"] == "pct" for _, r in att):
        return "of the room price"
    return "per person per night"


def jt_tabella(L, d):
    """Fasce di prezzo a persona con l'importo di ogni componente e il totale (solo importi fissi): [(da, a, [importi], totale)]."""
    att = jt_attive(L, d)
    if not att or any(r["tipo"] == "pct" for _, r in att):
        return []
    punti = sorted({b[0] for _, r in att for b in r["bande"]})
    righe = []
    for i, lo in enumerate(punti):
        hi = punti[i + 1] if i + 1 < len(punti) else None
        v = [jt_quota(r, lo) for _, r in att]
        if righe and righe[-1][2] == v:
            righe[-1] = (righe[-1][0], hi, v, sum(v))
        else:
            righe.append((lo, hi, v, sum(v)))
    return righe


def jt_fascia_testo(lo, hi):
    if lo == 0 and hi is not None:
        return f"Up to {yen(hi - 1)}"
    if hi is None:
        return f"{yen(lo)} or more"
    return f"{yen(lo)} to {yen(hi - 1)}"


def jt_date_cambio(L):
    """Date future (dopo oggi) in cui cambia una regola del luogo."""
    oggi = OGGI.isoformat()
    ds = set()
    for c in L["comp"]:
        for r in c["regole"]:
            if r.get("dal") and r["dal"] > oggi:
                ds.add(r["dal"])
            if r.get("al") and r["al"] >= oggi:
                ds.add((date.fromisoformat(r["al"]) + timedelta(days=1)).isoformat())
    return sorted(ds)


def jt_giorno_rif(L):
    """Oggi se una tassa è già in vigore, altrimenti la prima data di partenza (None se la data non è fissata)."""
    oggi = OGGI.isoformat()
    if jt_attive(L, oggi):
        return oggi
    ds = jt_date_cambio(L)
    return ds[0] if ds else None


def jt_anni(L):
    rif = jt_giorno_rif(L)
    if rif is None:
        return "2027"
    if rif[:4] == "2027":
        return "2027"
    return f"{ANNO} and {ANNO + 1}" if any(d[:4] == "2027" for d in jt_date_cambio(L)) else str(ANNO)


def jt_nome_titolo(e):
    """Nome per titolo e H1: 'Osaka', 'Okinawa' (si cerca così); 'Fukuoka Prefecture' resta intero per non confonderlo con Fukuoka City."""
    if e["livello"] == "prefecture" and e["id"] != "fukuoka-prefecture":
        return e["en"].replace(" Prefecture", "")
    return e["en"].replace(" (Tomamu)", "")


def jt_rif_nuova(e, L):
    """Data di riferimento di titolo e risposta: per una tassa approvata la sua partenza, altrimenti jt_giorno_rif()."""
    if e["stato"] == "approvato" and e.get("inizio") and e["inizio"] > OGGI.isoformat():
        return e["inizio"]
    return jt_giorno_rif(L)


def jt_titolo(e, L):
    nome = jt_nome_titolo(e)
    rif = jt_rif_nuova(e, L)
    if rif is None:
        cifra = jt_desc({"tipo": "bande", "bande": e["bande_previste"]}, True)
        cand = [f"{nome} accommodation tax 2027: {cifra} per person per night", f"{nome} accommodation tax 2027: {cifra} per night"]
    else:
        b, u = jt_breve(L, rif), jt_unita(L, rif)
        da = f" from {data_breve(rif)}" if rif > OGGI.isoformat() else ""
        anni_ = "2027" if rif[:4] == "2027" else jt_anni(L)
        dopo = [d for d in jt_date_cambio(L) if d > rif and d[:4] <= "2027" and jt_breve(L, d) != b]
        ora = f"{b} now, {jt_breve(L, dopo[0])} from {data_breve(dopo[0])}" if dopo and not da else ""
        cand = ([f"{nome} accommodation tax {anni_}: {ora} (calculator)", f"{nome} accommodation tax {anni_}: {ora}"] if ora else []) + [
            f"{nome} accommodation tax {anni_}: {b} {u}{da} (calculator)", f"{nome} accommodation tax {anni_}: {b} {u}{da}",
            f"{nome} accommodation tax {anni_}: {b}{da} (calculator)", f"{nome} accommodation tax {anni_}: {b}{da}",
            f"{nome} accommodation tax {anni_}: {b}"]
    return next((t for t in cand if len(t) <= 70), f"{nome} accommodation tax {ANNO + 1 if rif is None else jt_anni(L)}")


def jt_fonti(e):
    """Fonti dell'ente e (per un Comune) della Prefettura, senza doppioni, nell'ordine dei dati."""
    out, visti = [], set()
    P = JT_PREF.get(e["pref"]) if e["livello"] == "municipality" else None
    for fo in e["fonti"] + (P["fonti"] if P else []):
        if fo["url"] not in visti:
            visti.add(fo["url"])
            out.append(fo)
    return out


def jt_composizione(e, L, d):
    """'Otaru City accommodation tax ¥200 + Hokkaido accommodation tax ¥100–¥500 by price band' nella data d."""
    att = jt_attive(L, d)
    if len(att) == 1 and att[0][1].get("include_pref"):
        P = JT_PREF[e["pref"]]
        return f"a single {jt_desc(att[0][1])}, which includes the {P['nome_tassa']}"
    return " plus ".join(f"{c['label']} {jt_desc(r)}" for c, r in att)


def jt_bande_frase(b):
    """Fasce in parole: '¥100 below ¥6,000, ¥300 from ¥6,000 and ¥500 from ¥20,000'."""
    righe = [f"{yen(v)} below {yen(hi)}" if lo == 0 else f"{yen(v)} from {yen(lo)}" for lo, hi, v in b]
    return ", ".join(righe[:-1]) + " and " + righe[-1] if len(righe) > 1 else righe[0]


def jt_nuove_fasce(L, prima, dopo):
    """Se nella data `dopo` la cifra breve è uguale a quella di `prima` ma cambiano le fasce di una sola tassa a fasce (Nagasaki 1/4/2027),
    le nuove fasce in parole; altrimenti ''."""
    if jt_breve(L, dopo) != jt_breve(L, prima):
        return ""
    att = jt_attive(L, dopo)
    if len(att) != 1 or att[0][1]["tipo"] != "bande":
        return ""
    return jt_bande_frase(att[0][1]["bande"])


def jt_fuori(e):
    """Per una Prefettura con Comuni tassati: ' outside Fukuoka City and Kitakyushu' (o una frase generica se sono molti)."""
    if e["livello"] != "prefecture":
        return ""
    mm = [x["en"] for x in JT["enti"] if x["pref"] == e["id"] and x["livello"] == "municipality" and x["stato"] == "in_vigore"]
    if not mm:
        return ""
    if len(mm) > 6:
        return " outside the towns and cities with their own tax (listed below)"
    return " outside " + (", ".join(mm[:-1]) + " and " + mm[-1] if len(mm) > 1 else mm[0])


def jt_risposta(e, L):
    """Prima frase: cifra, composizione, fonte e data del controllo."""
    fo = [jt_nome_fonte(f["url"]) for f in jt_fonti(e)]
    fonti = " and ".join(list(dict.fromkeys(fo))[:2])
    rif = jt_rif_nuova(e, L)
    nome = e["en"]
    if rif is None:
        b = e["bande_previste"]
        return (f"{nome} has approved an accommodation tax of {jt_desc({'tipo': 'bande', 'bande': b}, True).replace('–', ' to ')} per person per night, set by the "
                f"room-only price per person ({jt_bande_frase(b)}), starting in January 2027 or later ({fonti}, checked on {JT_CHECK}). "
                "The exact start date has not been set yet.")
    oggi = OGGI.isoformat()
    inizi = [r["dal"] for _, r in jt_attive(L, rif) if r.get("dal")]
    quando = f"From {data_lunga(rif)}, " if rif > oggi else (f"Since {data_lunga(max(inizi))}, " if inizi else "")
    b, u = jt_breve(L, rif), jt_unita(L, rif)
    att = jt_attive(L, rif)
    if len(att) == 1 and not att[0][1].get("include_pref"):
        s = f"{quando}the {att[0][0]['label']}{jt_fuori(e)} is {jt_desc_lunga(att[0][1])} ({fonti}, checked on {JT_CHECK})."
    else:
        s = (f"{quando}the accommodation tax in {nome}{jt_fuori(e)} is {b.replace('–', ' to ')} {u}: {jt_composizione(e, L, rif)} "
             f"({fonti}, checked on {JT_CHECK}).")
    s = s[0].upper() + s[1:]
    dopo = [d for d in jt_date_cambio(L) if d > rif]
    if dopo:
        d = dopo[0]
        nuove = jt_nuove_fasce(L, rif, d)
        if nuove:
            s += f" From {data_lunga(d)} the price bands change: {nuove}."
        else:
            s += f" From {data_lunga(d)} it changes to {jt_breve(L, d).replace('–', ' to ')} {jt_unita(L, d)}: {jt_composizione(e, L, d)}."
    if rif > oggi and jt_attive(L, oggi):
        s += (f" Until {data_lunga((date.fromisoformat(rif) - timedelta(days=1)).isoformat())} only the "
              f"{jt_composizione(e, L, oggi)} applies.")
    return s


def jt_tabella_html(e, L, d):
    att = jt_attive(L, d)
    righe = jt_tabella(L, d)
    if not att:
        return ""
    if not righe:
        li = "".join(f"<li><strong>{escape(c['label'])}:</strong> {escape(jt_desc(r))}"
                     + (f"; the base is the price per person rounded down to the nearest {yen(r['arrot'])}, counted up to {yen(r['base_max'])}" if r.get("arrot") else "")
                     + (" (includes the prefectural tax)" if r.get("include_pref") else "") + "</li>" for c, r in att)
        return f"<ul>{li}</ul>"
    th = "".join(f"<th>{escape(c['label'].replace(' accommodation tax', ''))}</th>" for c, _ in att) if len(att) > 1 else ""
    tr = "".join(f"<tr><td>{jt_fascia_testo(lo, hi)}</td>" + ("".join(f"<td>{yen(x)}</td>" for x in v) if len(att) > 1 else "")
                 + f"<td><strong>{yen(t)}</strong></td></tr>" for lo, hi, v, t in righe)
    return (f'<div class="tab sintesi"><table><thead><tr><th>Room-only price per person per night</th>{th}<th>{"Total " if len(att) > 1 else ""}per person per night</th>'
            f"</tr></thead><tbody>{tr}</tbody></table></div>")


def jt_periodi(L):
    """Periodi con regole diverse a partire da oggi (o dalla partenza): [(dal, al)]."""
    rif = jt_giorno_rif(L)
    if rif is None:
        return []
    ds = [rif] + [d for d in jt_date_cambio(L) if d > rif]
    return [(d, (date.fromisoformat(ds[i + 1]) - timedelta(days=1)).isoformat() if i + 1 < len(ds) else None) for i, d in enumerate(ds)]


def jt_esempio(L):
    rif = jt_giorno_rif(L)
    if rif is None:
        return ""
    o = jt_calcola(L, rif, 3, L["prezzo"], 2)
    return (f"Example: 2 guests, room-only price {yen(L['prezzo'])} per night ({yen(L['prezzo'] / 2)} per person), 3 nights from {data_lunga(rif)} → "
            f"<strong>{yen(o['totale'])}</strong> in total.")


def jt_calcolatore(luoghi, rel, con_scelta=False):
    scelta = (f'<label class="pieno"><span class="lt">{ico("pin")}City, town or prefecture</span><select name="luogo"></select></label>' if con_scelta else "")
    link = (f'<p class="calc-link"><a data-link data-base="{rel}" href="{rel}{luoghi[0]["pagina"]}"><span>Rates, exemptions and official sources</span>{ico("arrow")}</a></p>'
            if con_scelta else "")
    dati = json.dumps(luoghi, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f"""<div class="card calc" data-jt>
<div class="calc-grid">
<form autocomplete="off">
<div class="campi">
{scelta}
<label data-campo="checkin"><span class="lt">{ico("calendar")}Check-in date</span><input type="date" name="checkin"></label>
<label data-campo="notti"><span class="lt">{ico("moon")}Nights</span><input type="number" name="notti" min="1" max="365" value="3" inputmode="numeric"></label>
<label data-campo="paganti"><span class="lt">{ico("users")}Guests</span><input type="number" name="ospiti" min="1" max="50" value="2" inputmode="numeric"></label>
<label data-campo="esenti" hidden><span class="lt">{ico("child")}<span data-lab="esenti">Children</span></span><input type="number" name="bambini" min="0" max="50" value="0" inputmode="numeric"></label>
<label class="pieno" data-campo="prezzo"><span class="lt">{ico("tag")}{JT_PREZZO_LAB}</span><input type="number" name="prezzo" min="0" step="any" value="{luoghi[0]['prezzo']}" inputmode="decimal"></label>
</div>
</form>
<div class="calc-out">
<div class="risultato" data-out aria-live="polite"><noscript>Turn on JavaScript to use the calculator. The rate tables show every official amount.</noscript></div>
{link}
</div>
</div>
</div>
<script type="application/json" id="jt-dati">{dati}</script>"""


JT_FORMULA = ("Tax per night = for each tax that applies (city, town or village, and prefecture): the amount for the band of the room-only price per person "
              "(price per night ÷ guests), or the percentage of that price per person (Okinawa: rounded down to the nearest ¥1,000, counted up to ¥100,000, "
              "with a maximum per person), times the guests who pay. A tax counts only on nights from its start date. Children are left out only where "
              "the official rules exempt them by age. The accommodation may round the amounts: check the final figure with them.")


def jt_callout(rel):
    n_in = sum(1 for e in JT["enti"] if e["stato"] == "in_vigore")
    n_ap = sum(1 for e in JT["enti"] if e["stato"] == "approvato")
    return (f'<section class="card callout jt-box" aria-label="Japan accommodation tax"><span class="ic">{ico("bed")}</span>'
            f'<p><strong>Staying elsewhere in Japan?</strong> {n_in} prefectures and cities charge an accommodation tax and {n_ap} more start in 2027. '
            f'<a href="{rel}{JT_HUB}">Japan accommodation tax: every place, with a calculator</a> · <a href="{rel}{JT_27}">2027 start dates</a></p></section>')


def jt_link(e, rel):
    return f'<a href="{rel}{e["pagina"]}">{escape(e["en"])}</a>'


def jt_quando(e, corto=False):
    data_lunga = data_breve if corto else globals()["data_lunga"]
    if e["stato"] == "approvato":
        return f"Starts {data_lunga(e['inizio'])}" if e.get("inizio") else ("Jan 2027 or later" if corto else f"Starts {e.get('inizio_testo', '2027')}")
    if e.get("inizio") and e.get("inizio_da") == "mic":
        return f"Since {data_lunga(e['inizio'])}"
    if e.get("inizio") and e["inizio"] <= OGGI.isoformat():
        if e.get("inizio_nota") == "tariffe":
            return f"Current rates since {data_lunga(e['inizio'])}"
        if e.get("inizio_da") == "consenso":
            return f"Since {data_lunga(e['inizio'])}" + ("" if corto else " (start date planned in the Minister's consent)")
        return f"Since {data_lunga(e['inizio'])}"
    return "In force"


def jt_riga_sintesi(e, rel):
    L = JT_L[e["id"]]
    rif = jt_giorno_rif(L)
    if rif is None:
        cifra = jt_desc({"tipo": "bande", "bande": e["bande_previste"]}, True)
    else:
        cifra = jt_breve(L, rif) + (" of the room price" if jt_unita(L, rif) == "of the room price" else "")
    return f"<tr><td>{jt_link(e, rel)}<br><span class=\"small\">{escape(e['ja'])}</span></td><td>{escape(cifra)}</td><td>{escape(jt_quando(e, corto=True))}</td></tr>"


def jt_ordine_pref():
    """Prefetture in ordine geografico approssimativo (nord → sud) per raggruppare le tabelle."""
    ordine = ["hokkaido", "aomori", "iwate", "miyagi", "yamagata-pref", "tochigi", "tokyo", "kanagawa", "yamanashi", "nagano", "ishikawa", "gifu",
              "shizuoka", "aichi", "mie", "kyoto-pref", "osaka", "wakayama", "shimane", "hiroshima", "fukuoka-prefecture", "nagasaki-pref",
              "kumamoto-pref", "oita", "miyazaki-pref", "kagoshima-pref", "okinawa"]
    return ordine


def jt_gruppi(stati=("in_vigore", "approvato")):
    """{pref_id: [enti]} con la Prefettura prima dei suoi Comuni, nell'ordine geografico."""
    g = {}
    for e in JT["enti"]:
        if e["stato"] in stati:
            g.setdefault(e["pref"], []).append(e)
    for k in g:
        g[k].sort(key=lambda e: (e["livello"] != "prefecture", e["stato"] != "in_vigore", e["en"]))
    ordine = jt_ordine_pref()
    return [(k, g[k]) for k in sorted(g, key=lambda k: ordine.index(k) if k in ordine else 99)]


def jt_nome_pref(pid, enti):
    e = enti[0]
    return e["en"] if e["livello"] == "prefecture" else e.get("pref_en", pid)


def pagina_jt_luogo(e):
    L = JT_L[e["id"]]
    rel = "../../"
    P = JT_PREF.get(e["pref"]) if e["livello"] == "municipality" else None
    rif = jt_giorno_rif(L)
    titolo = jt_titolo(e, L)
    h1 = titolo.replace(" (calculator)", "")
    tabelle = ""
    for dal, al in jt_periodi(L):
        if dal <= OGGI.isoformat():
            intest = f"Rates now" + (f" (until {data_lunga(al)})" if al else "")
        else:
            intest = f"From {data_lunga(dal)}" + (f" to {data_lunga(al)}" if al else "")
        tabelle += f"<h3>{intest}</h3>{jt_tabella_html(e, L, dal)}"
    if rif is None:
        tabelle = "<h3>Approved rates (start date not fixed)</h3>" + jt_tabella_html(e, {"comp": [{"label": e["nome_tassa"], "regole": [{"tipo": "bande", "bande": e["bande_previste"]}], "eta": False, "pref": False}]}, OGGI.isoformat())
    ese = e["esenzioni"] + ([f"{P['en']} tax: {x[0].lower() + x[1:]}" for x in P["esenzioni"]] if P else [])
    esenzioni = ("<ul>" + "".join(f"<li>{escape(x)}</li>" for x in ese) + "</ul>") if ese else "<p>The official sources list no exemptions.</p>"
    note = e["note"] + ([n for n in P["note"]] if P and e["pref"] in ("hokkaido", "nagano", "okinawa", "fukuoka-prefecture", "miyagi") else [])
    sorelle = [x for x in JT["enti"] if x["pref"] == e["pref"] and x["id"] != e["id"]]
    stato = (f"In force: {e['ja']} is on the Ministry of Internal Affairs and Communications list of local taxes in force on {JT_LISTA_AL}."
             if e["stato"] == "in_vigore" else
             f"Approved, not yet in force: on the Ministry's list of {JT_LISTA_AL}, {e['ja']} has an ordinance and the Minister's consent, with the start "
             + (f"planned for {data_lunga(e['inizio'])}." if e.get("inizio") else f"planned for {e.get('inizio_testo')}."))
    cambi = [d for d in jt_date_cambio(L) if d > OGGI.isoformat()]
    box = ""
    if cambi:
        li = "".join(f"<li><strong>{data_lunga(d)}:</strong> " + escape(f"new price bands ({jt_nuove_fasce(L, OGGI.isoformat(), d)})" if jt_nuove_fasce(L, OGGI.isoformat(), d)
                                                                       else f"{jt_breve(L, d)} {jt_unita(L, d)}") + "</li>" for d in cambi[:3])
        box = (f'<section class="card callout cambi-box" aria-label="Upcoming changes"><span class="ic">{ico("calendar")}</span>'
               f'<div><p><strong>Upcoming changes</strong></p><ul>{li}</ul><p class="small"><a href="{rel}{JT_27}">Japan accommodation tax 2027: all new taxes and start dates</a></p></div></section>')
    pref_sez = ""
    if e["livello"] == "prefecture":
        mm = [x for x in JT["enti"] if x["pref"] == e["id"] and x["livello"] == "municipality"]
        if mm:
            inclusa = {"hokkaido": " (in Kutchan, Niseko, Tomakomai and Kitahiroshima a single percentage includes both)",
                       "okinawa": " (0.8% to the prefecture and 1.2% to the municipality, 2% in all)"}.get(e["id"], "")
            pref_sez = (f"<h2>Cities, towns and villages in {escape(e['en'])} with their own tax</h2><p>In these places you pay the local tax and the {escape(e['nome_tassa'])} "
                        f"together{inclusa}. The figures are the totals.</p>"
                        '<div class="tab sintesi"><table><thead><tr><th>Place</th><th>Total per person per night</th><th>Start</th></tr></thead><tbody>'
                        + "".join(jt_riga_sintesi(x, rel) for x in mm) + "</tbody></table></div>")
    fonti = "".join(f'<li><a href="{escape(f["url"])}" rel="noopener">{escape(f["titolo"])}</a> – {escape(f["formato"])}, checked {data_lunga(f["controllato_il"])}</li>'
                    for f in jt_fonti(e))
    f0 = jt_fonti(e)[0]
    calc = jt_calcolatore([L], rel) if rif is not None else (f'<p class="avviso"><strong>No calculator yet.</strong> The start date is not fixed; '
                                                                f'we will add it when {escape(e["en"])} publishes it.</p>')
    nome_p = (P["en"] if P else (e.get("pref_en") or e["en"]))
    corpo = f"""<section class="hero">{h1_diviso(h1)}
<p class="risposta">{escape(jt_risposta(e, L))}</p>
<p class="fonte">Official source: <a href="{escape(f0['url'])}" rel="noopener">{escape(f0['titolo'])}</a> · checked on {data_lunga(f0['controllato_il'])}</p></section>
{box}
{calc}
<details class="formula"><summary>{ico("calc")}Formula used</summary><p>{escape(JT_FORMULA)}</p></details>
{f'<p class="esempio">{jt_esempio(L)}</p>' if rif else ""}
{AVVISO}
{AD}
<h2>Official rates</h2>
<p>{escape(e['nome_tassa'])} (宿泊税, {escape(e['ja'])}){f" and {escape(P['nome_tassa'])} ({escape(P['ja'])})" if P and any(c['pref'] for c in L['comp']) else ""}, per person per night, by room-only price per person per night.</p>
{tabelle}
<p class="small">{escape(stato)}</p>
{pref_sez}
<h2>Practical notes</h2>
<ul>{"".join(f"<li>{escape(n)}</li>" for n in note)}<li>The price used for the bands is the room-only price per person per night. Most official explanations exclude meals and consumption tax: ask your accommodation what it includes.</li></ul>
<p><strong>Who collects it:</strong> the accommodation (hotel, ryokan, guesthouse or private lodging) collects the tax from guests and pays it to the local government (special collection, 特別徴収).</p>
<h2>Exemptions (official)</h2>
{esenzioni}
<h2>Official sources</h2>
<ul>{fonti}</ul>
<p class="small">Spotted a change in the official rate? <a href="{rel}contact/?ref=jp-{e['id']}">Tell us</a>.</p>
{f'<h2>Other places in {escape(nome_p)}</h2><div class="griglia">' + "".join(f'<a href="{rel}{x["pagina"]}">{escape(x["en"])}<small>{escape(jt_quando(x))}</small></a>' for x in sorelle) + "</div>" if sorelle else ""}
<p><a href="{rel}{JT_HUB}">Japan accommodation tax: all places</a> · <a href="{rel}{JT_27}">New taxes in 2027</a> · <a href="{rel}{JP_SLUG}">Japan tax-free refund</a></p>"""
    br = [("Japan accommodation tax", JT_HUB)] + ([(P["en"], P["pagina"])] if P and P["pagina"].startswith(JT_HUB) else []) + [(e["en"], e["pagina"])]
    rif = jt_rif_nuova(e, L)
    if rif is None:
        cifra = jt_desc({"tipo": "bande", "bande": e["bande_previste"]}, True) + " per person per night, start date not fixed yet"
    else:
        cifra = f"{jt_breve(L, rif)} {jt_unita(L, rif)}" + (f" from {data_lunga(rif)}" if rif > OGGI.isoformat() else "")
    descr = (f"{e['en']} accommodation tax ({e['ja']}): {cifra}. Rate table, exemptions, official sources and a calculator.")
    pagina(e["pagina"], titolo, descr, corpo, briciole=br, extra_js=JT_JS + JT_APP_JS)


def jt_faq():
    vv = [e for e in JT["enti"] if e["stato"] == "in_vigore"]
    ap = [e for e in JT["enti"] if e["stato"] == "approvato"]
    tk, ky, osk = JT_L["tokyo"], JT_L["kyoto"], JT_L["osaka"]
    oggi = OGGI.isoformat()
    return [
        ("Which places in Japan charge an accommodation tax?",
         f"On {JT_LISTA_AL}, {len(vv)} local governments: {sum(1 for e in vv if e['livello'] == 'prefecture')} prefectures "
         f"({', '.join(e['en'] for e in vv if e['livello'] == 'prefecture')}) and {sum(1 for e in vv if e['livello'] == 'municipality')} cities, towns and villages, "
         f"according to the Ministry of Internal Affairs and Communications. {len(ap)} more have been approved and start in 2027."),
        ("Do I pay both the prefecture and the city tax?",
         "Yes, where both charge one. In Hokkaido the prefectural tax is added to the town or city tax (except in Kutchan and, from 1 November 2026, Niseko, "
         "where one 3% covers both). In Fukuoka City and Kitakyushu the prefecture charges ¥50 on top of the city tax, in Sendai ¥100, and in the five Nagano "
         "municipalities with their own tax half the prefectural rate. The calculator adds them up."),
        ("How much is the accommodation tax in Tokyo, Kyoto and Osaka?",
         f"Tokyo: {jt_breve(tk, oggi)} per person per night now (no tax below ¥10,000), 3% from ¥13,000 per person from 1 April 2027. "
         f"Kyoto: {jt_breve(ky, oggi)} per person per night by price band. Osaka Prefecture: {jt_breve(osk, oggi)} per person per night, no tax below ¥5,000."),
        ("Do children pay the accommodation tax in Japan?",
         "Usually yes: most taxes have no age exemption. Some places exempt children: under 12 in Atami, Gero, Yugawara, Nasu and Shirahama; children up to primary-school age "
         "in Takayama, Gifu, Ibusuki and (town tax only) Toyako. School trips are exempt almost everywhere."),
        ("Is the price per room or per person?",
         "The tax is per person per night, and the band depends on the room-only price per person per night: the room price divided by the number of guests. "
         "Meals and consumption tax are usually left out; check with the accommodation."),
    ]


def pagina_jt_hub():
    rel = "../"
    vv = [e for e in JT["enti"] if e["stato"] == "in_vigore"]
    ap = [e for e in JT["enti"] if e["stato"] == "approvato"]
    oggi = OGGI.isoformat()
    importi = [x[3] for L in JT_LUOGHI for x in jt_tabella(L, oggi) if x[3]]
    pct = sorted({num(r["valore"]) for L in JT_LUOGHI for _, r in jt_attive(L, oggi) if r["tipo"] == "pct"}, key=float)
    risp = (f"On {JT_LISTA_AL}, {len(vv)} local governments in Japan charged an accommodation tax ({sum(1 for e in vv if e['livello'] == 'prefecture')} prefectures and "
            f"{sum(1 for e in vv if e['livello'] == 'municipality')} cities, towns and villages) and {len(ap)} more were approved to start in 2027, according to the "
            f"Ministry of Internal Affairs and Communications (list checked on {JT_CHECK}). Amounts range from {yen(min(importi))} to {yen(max(importi))} per person per night"
            + (f", or {pct[0] + '% to ' + pct[-1] if len(pct) > 1 else pct[0]}% of the room price" if pct else "")
            + "; where a prefecture and a city both tax, you pay both.")
    righe = ""
    for pid, enti in jt_gruppi(("in_vigore",)):
        righe += f'<tr class="grp"><th colspan="3">{escape(jt_nome_pref(pid, enti))}</th></tr>' + "".join(jt_riga_sintesi(e, rel) for e in enti)
    faq = jt_faq()
    faq_html = "".join(f'<details class="faq"><summary>{escape(q)}</summary><p>{escape(a)}</p></details>' for q, a in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    lista = JT["fonte_elenco"]
    altre = [JT_ENTI["hokkaido"]["fonti"][0], JT_ENTI["fukuoka-prefecture"]["fonti"][0], JT_ENTI["nagano"]["fonti"][0], JT_ENTI["okinawa"]["fonti"][0]]
    luoghi = sorted(JT_LUOGHI, key=lambda L: (jt_ordine_pref().index(JT_ENTI[L["id"]]["pref"]) if JT_ENTI[L["id"]]["pref"] in jt_ordine_pref() else 99,
                                              JT_ENTI[L["id"]]["livello"] != "prefecture", L["nome"]))
    luoghi = [L for L in luoghi if jt_giorno_rif(L) is not None]
    corpo = f"""<section class="hero">{h1_diviso(f"Japan accommodation tax {ANNO}: every prefecture and city, with a calculator")}
<p class="risposta">{escape(risp)}</p>
<p class="fonte">Official source: <a href="{escape(lista['url'])}" rel="noopener">{escape(lista['titolo'])}</a> · checked on {data_lunga(lista['controllato_il'])}</p></section>
<div class="card callout cal-2027"><span class="ic">{ico("calendar")}</span><p><strong>2027:</strong> <a href="{rel}{JT_27}">{len(ap)} new accommodation taxes with their start dates</a> – Okinawa and five more places on 1 February, Tokyo's new 3% and seven new city taxes on 1 April.</p></div>
<h2>Calculator</h2>
{jt_calcolatore(luoghi, rel, con_scelta=True)}
<details class="formula"><summary>{ico("calc")}Formula used</summary><p>{escape(JT_FORMULA)}</p></details>
{AVVISO}
{AD}
<h2>Accommodation tax by prefecture and city ({len(vv)} in force)</h2>
<p>Totals per person per night today, prefecture and city together. Each place has its own page with the rate table, the start date, the exemptions and the official sources.</p>
<div class="tab sintesi"><table><thead><tr><th>Place</th><th>Tax per person per night</th><th>Start</th></tr></thead><tbody>{righe}</tbody></table></div>
<h2>How prefecture and city taxes add up</h2>
<ul><li><strong>Hokkaido:</strong> the Hokkaido tax (¥100, ¥200 or ¥500 by price) is added to the tax of the town or city. Kutchan and, from 1 November 2026, Niseko charge one flat 3% that includes it; Tomakomai (April 2027) and Kitahiroshima (October 2027) will do the same.</li>
<li><strong>Fukuoka:</strong> ¥200 in the prefecture; in Fukuoka City and Kitakyushu the prefecture charges ¥50 and the city ¥150 (Fukuoka City ¥450 from ¥20,000).</li>
<li><strong>Miyagi:</strong> ¥300 in the prefecture; in Sendai ¥100 to the prefecture and ¥200 to the city.</li>
<li><strong>Nagano:</strong> ¥200 for the first three years (then ¥300); in Matsumoto, Karuizawa, Achi, Hakuba and Nozawa Onsen half that, plus the local tax.</li>
<li><strong>Okinawa (from 1 February 2027):</strong> 2% (max ¥2,000); in Ishigaki, Miyakojima, Nago, Motobu, Onna and Chatan 0.8% to the prefecture and 1.2% to the municipality.</li></ul>
<p class="fonte">Official sources: {" · ".join(f'<a href="{escape(f["url"])}" rel="noopener">{escape(jt_nome_fonte(f["url"]))}</a>' for f in altre)} · checked on {JT_CHECK}</p>
<h2>Questions</h2>
<div class="faq-box">{faq_html}</div>
<h2>How we check the rates</h2>
<p>The list of places comes from the Ministry of Internal Affairs and Communications (法定外税の状況, as of {JT_LISTA_AL}). Each rate comes from the Minister's consent to the tax (published by the Ministry) or from the official page of the prefecture or city, linked on each page with the date we checked it. We re-check the Ministry's list and its press releases every quarter.</p>
<p class="small">Spotted a change? <a href="{rel}contact/?ref=japan-accommodation-tax">Tell us</a>.</p>
<p><a href="{rel}country/japan/">Tourist taxes in Japan</a> · <a href="{rel}{JP_SLUG}">Japan tax-free refund</a> · <a href="{rel}tourist-tax-changes-2027/">All tourist tax changes in 2027</a></p>"""
    pagina(JT_HUB, f"Japan accommodation tax {ANNO}: all {len(vv)} places and calculator",
           f"Japan accommodation tax by prefecture and city: {len(vv)} taxes in force on {JT_LISTA_AL} and {len(ap)} approved for 2027. Official rates, start dates and a calculator.",
           corpo, briciole=[("Japan accommodation tax", JT_HUB)], extra_js=JT_JS + JT_APP_JS, jsonld_extra=ld)


def jt_bande_testo(L, d):
    """'¥100 / ¥300 / ¥500 per person per night (bands from ¥6,000 and ¥20,000)': per distinguere due tabelle con lo stesso minimo e massimo."""
    rr = jt_tabella(L, d)
    los = [yen(x[0]) for x in rr[1:]]
    return (" / ".join(yen(x[3]) for x in rr) + " per person per night"
            + (f" (bands from {', '.join(los[:-1]) + ' and ' + los[-1] if len(los) > 1 else los[0]})" if los else ""))


def jt_eventi_2027():
    """Calendario: nuove tasse (approvate) e cambi di tasse esistenti tra oggi e il 31/12/2027, con data, luogo, importo, fonte."""
    oggi = OGGI.isoformat()
    ev = []
    for e in JT["enti"]:
        L = JT_L[e["id"]]
        if e["stato"] == "approvato":
            if e.get("inizio"):
                cifra = f"{jt_breve(L, e['inizio'])} {jt_unita(L, e['inizio'])}"
                ev.append({"dal": e["inizio"], "e": e, "nuova": True, "cifra": cifra, "dett": jt_composizione(e, L, e["inizio"])})
            else:
                ev.append({"dal": None, "e": e, "nuova": True, "cifra": jt_desc({"tipo": "bande", "bande": e["bande_previste"]}, True) + " per person per night",
                           "dett": "start date not fixed yet (January 2027 or later)"})
            continue
        for d in jt_date_cambio(L):
            if d <= "2027-12-31" and d > oggi:
                prima = (date.fromisoformat(d) - timedelta(days=1)).isoformat()
                if [r for _, r in jt_attive(L, d)] != [r for _, r in jt_attive(L, prima)]:
                    dopo_, prima_ = f"{jt_breve(L, d)} {jt_unita(L, d)}", f"{jt_breve(L, prima)} {jt_unita(L, prima)}"
                    if dopo_ == prima_:
                        dopo_, prima_ = jt_bande_testo(L, d), jt_bande_testo(L, prima)
                    ev.append({"dal": d, "e": e, "nuova": False, "cifra": dopo_, "dett": jt_composizione(e, L, d), "prima": prima_})
    return sorted(ev, key=lambda x: (x["dal"] or "2027-01-00", x["e"]["livello"] != "prefecture", x["e"]["en"]))


def jt_faq_2027(ev):
    nuove = [x for x in ev if x["nuova"]]
    oki = JT_L["okinawa"]
    per_data = {}
    for x in nuove:
        per_data.setdefault(x["dal"], []).append(x["e"]["en"])
    elenco = "; ".join((data_lunga(d) if d else "January 2027 or later") + ": " + ", ".join(n) for d, n in per_data.items())
    return [
        ("Which new accommodation taxes start in Japan in 2027?",
         f"{len(nuove)} approved taxes, by start date: {elenco} (Ministry of Internal Affairs and Communications list of {JT_LISTA_AL})."),
        ("How much is the Okinawa accommodation tax?",
         f"From 1 February 2027, {jt_breve(oki, '2027-02-01')} of the room-only price per person per night, rounded down to the nearest ¥1,000. In Ishigaki, Miyakojima, Nago, "
         "Motobu, Onna and Chatan the same 2% is split between the prefecture (0.8%, max ¥800) and the municipality (1.2%, max ¥1,200)."),
        ("Is there an accommodation tax at Mount Fuji?",
         "Yes, from 1 April 2027 in Fujiyoshida and Fujikawaguchiko: ¥200 per person per night each, with school trips exempt."),
        ("Which existing taxes change in 2027?",
         "Tokyo moves to 3% of the room-only price per person per night from ¥13,000 (1 April 2027), and Nagasaki changes its bands to ¥100, ¥300 and ¥500 "
         "(1 April 2027). Niseko already moves to a flat 3% on 1 November 2026."),
    ]


def pagina_jt_2027():
    rel = "../"
    ev = jt_eventi_2027()
    nuove = [x for x in ev if x["nuova"]]
    righe = ""
    for x in ev:
        e = x["e"]
        quando = data_breve(x["dal"]) if x["dal"] else "Jan 2027 or later"
        L = JT_L[e["id"]]
        if x["nuova"]:
            cosa = "New: " + (jt_breve(L, x["dal"]) if x["dal"] else jt_desc({"tipo": "bande", "bande": e["bande_previste"]}, True))
        else:
            prima_ = (date.fromisoformat(x["dal"]) - timedelta(days=1)).isoformat()
            cosa = "Change: " + (jt_breve(L, x["dal"]) if jt_breve(L, x["dal"]) != jt_breve(L, prima_) else "new price bands")
        righe += f"<tr><td><strong>{escape(quando)}</strong></td><td>{jt_link(e, rel)}<br><span class=\"small\">{escape(e['ja'])}</span></td><td>{escape(cosa)}</td></tr>"
    schede = ""
    for x in ev:
        e = x["e"]
        fo = e["fonti"][0]
        d = x["dal"]
        g, m = (str(date.fromisoformat(d).day), f"{MESI_BREVI[date.fromisoformat(d).month - 1]} {d[:4]}") if d else ("Jan", "2027 or later")
        schede += f"""<li class="vc"><div class="vc-data"><span class="vc-g">{g}</span><span class="vc-m">{m}</span></div>
<div class="vc-c"><h3>{jt_link(e, rel)} <span class="small">{escape(e['ja'])}</span></h3>
<p class="vc-imp"><span class="vc-lab">{"New" if x["nuova"] else "Change"}</span> {escape(x['cifra'])}</p>
{f'<p class="vc-prima"><span class="vc-lab">Before</span> {escape(x["prima"])}</p>' if not x["nuova"] else ""}
<p>{escape(x['dett'][0].upper() + x['dett'][1:])}.</p>
<p class="fonte">Official source: <a href="{escape(fo['url'])}" rel="noopener">{escape(fo['titolo'])}</a> · checked on {data_lunga(fo['controllato_il'])}</p>
<a class="vc-calc" href="{rel}{e['pagina']}">{ico("calc")}Rates and calculator</a></div></li>"""
    per_data = {}
    for x in nuove:
        per_data.setdefault(x["dal"], []).append(x["e"]["en"])
    parti = []
    for d, n in per_data.items():
        nomi_ = ", ".join(n[:-1]) + " and " + n[-1] if len(n) > 1 else n[0]
        parti.append(f"{nomi_} {'on ' + data_lunga(d)[:-5] if d else 'from January 2027 or later'}")
    risp = (f"{len(nuove)} more Japanese local governments will charge an accommodation tax in 2027: " + "; ".join(parti)
            + f" (Ministry of Internal Affairs and Communications list as of {JT_LISTA_AL}, checked on {JT_CHECK}). Tokyo and Nagasaki also change their rates on 1 April 2027.")
    faq = jt_faq_2027(ev)
    faq_html = "".join(f'<details class="faq"><summary>{escape(q)}</summary><p>{escape(a)}</p></details>' for q, a in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    lista = JT["fonte_elenco"]
    corpo = f"""<section class="hero">{h1_diviso(f"Japan accommodation tax 2027: {len(nuove)} new taxes and the start dates")}
<p class="risposta">{escape(risp)}</p>
<p class="fonte">Official source: <a href="{escape(lista['url'])}" rel="noopener">{escape(lista['titolo'])}</a> · checked on {data_lunga(lista['controllato_il'])}</p></section>
<h2 class="sr">At a glance</h2>
<div class="tab sintesi"><table><thead><tr><th>From</th><th>Where</th><th>What</th></tr></thead><tbody>{righe}</tbody></table></div>
{AVVISO}
{AD}
<h2>Each change, with the official source</h2>
<ol class="linea">{schede}</ol>
<h2>Questions</h2>
<div class="faq-box">{faq_html}</div>
<p>We list a new tax only when the Ministry's list shows the ordinance and the Minister's consent. The rates come from the Minister's consent, published by the Ministry. Taxes still being discussed (for example in other prefectures) are not listed.</p>
<p><a href="{rel}{JT_HUB}">Japan accommodation tax: all places and calculator</a> · <a href="{rel}tourist-tax-changes-2027/">All tourist tax changes in 2027</a> · <a href="{rel}contact/?ref=japan-2027">Spotted a change? Tell us</a></p>"""
    pagina(JT_27, f"Japan accommodation tax 2027: {len(nuove)} new taxes, dates and rates",
           f"Japan accommodation tax 2027: {len(nuove)} new taxes approved (Okinawa, Ishigaki, Fujikawaguchiko, Kagoshima and more) with start dates, rates and official sources.",
           corpo, briciole=[("Japan accommodation tax", JT_HUB), ("2027", JT_27)], jsonld_extra=ld)


def pagine_jt():
    for e in JT["enti"]:
        if e["pagina"].startswith(JT_HUB):
            pagina_jt_luogo(e)
    pagina_jt_hub()
    pagina_jt_2027()


# ---------------------------------------------------------------- Spagna: licenza per affitti turistici (5/11/2026)
# Sezione /spain-holiday-let-licence/: indice, 6 pagine di Comunità autonoma e 20 pagine di Comune. Fatti e fonti (con impronta e data)
# in dati/spagna_licenze.json, scritto a mano leggendo i testi ufficiali; numeri in dati/spagna_numeri.json, scritto da
# raccolta/spagna.py (solo conteggi per Comune e mese: il registro andaluso contiene dati personali, che non vengono salvati).
# Nessuna consulenza legale, nessuna promessa, nessun link di affiliazione. verifica.py, punto 14.
ES = json.loads((DATI / "spagna_licenze.json").read_text(encoding="utf-8"))
ESN = json.loads((DATI / "spagna_numeri.json").read_text(encoding="utf-8"))
ES_SLUG = ES["slug"]
ES_F = ES["fonti"]
ES_REG = {r["id"]: r for r in ES["regioni"]}
ES_COMUNI = ES["comuni"]
ES_CHECK = data_lunga(ES["controllato_il"])
ES_SCARICATO = data_lunga(ESN["scaricato_il"])
ES_MESI = ESN["mesi"][-12:]          # ultimi 12 mesi completi
ES_MESI_PRIMA = ESN["mesi"][-24:-12]  # i 12 mesi prima
ES_INE_MESE = f"{MESI[int(ESN['ine']['periodo'][5:]) - 1]} {ESN['ine']['periodo'][:4]}"
ES_REGISTRI = {  # chiave in spagna_numeri.json -> (ente, nome del registro, fonte dei dati)
    "gva": ("Generalitat Valenciana", "Registro de Turismo de la Comunitat Valenciana", "cv_dati"),
    "rta": ("Junta de Andalucía", "Registro de Turismo de Andalucía", "and_dati"),
    "cat": ("Generalitat de Catalunya", "Registre de Turisme de Catalunya", "cat_dati"),
}
ES_TITOLI_REG = {
    "cv": "Valencia region tourist licence 2026: CV-VUT number and rules",
    "and": "Andalusia tourist licence 2026: VUT number, RTA and the rules",
    "cat": "Catalonia tourist licence 2026: HUT number and the 2028 deadline",
    "bal": "Balearic Islands tourist licence 2026: the number in every advert",
    "can": "Canary Islands holiday let licence 2026: Ley 6/2025 rules",
    "mad": "Madrid holiday let licence 2026: CIVUT and the regional register",
}
AVVISO_ES = ('<p class="avviso"><strong>Not legal advice.</strong> This page summarises official texts and open data; it does not tell you whether a '
             'particular home can be let or keep its registration. Town halls set their own planning rules and communities of owners can restrict tourist use: '
             'before you buy, let or advertise, check with the regional tourism department and the Ayuntamiento, or ask a professional.</p>')


ES_ARTICOLO = {"cv": "the ", "bal": "the ", "can": "the ", "mad": "the "}
ES_PREFISSI = {"04": "VUT/AL", "11": "VUT/CA", "14": "VUT/CO", "18": "VUT/GR", "21": "VUT/HU", "23": "VUT/JA", "29": "VUT/MA", "41": "VUT/SE",
               "08": "HUTB", "17": "HUTG", "25": "HUTL", "43": "HUTT", "03": "CV-VUT", "12": "CV-VUT", "46": "CV-VUT"}


def es_in(R):
    """Nome della Comunità con l'articolo quando serve: 'the Valencian Community', 'Andalusia'."""
    return ES_ARTICOLO.get(R["id"], "") + R["nome"]


def es_n(v):
    return f"{int(v):,}"


def es_mese(m, breve=False):
    a, mm = m.split("-")
    return f"{(MESI_BREVI if breve else MESI)[int(mm) - 1]} {a}"


def es_link(k, testo=None):
    f = ES_F[k]
    return f'<a href="{escape(f["url"])}" rel="noopener">{escape(testo or f["titolo"])}</a>'


def es_fonte(chiavi, etichetta="Official source"):
    """Riga fonte come nel resto del sito: 'Official source: <link> · checked on <data>'."""
    chiavi = list(dict.fromkeys(chiavi))
    data = data_lunga(max(ES_F[k]["controllato_il"] for k in chiavi))
    eti = etichetta + ("s" if len(chiavi) > 1 and etichetta.endswith("source") else "")
    return f'<p class="fonte">{eti}: ' + " · ".join(es_link(k) for k in chiavi) + f" · checked on {data}</p>"


def es_fonti_elenco(chiavi):
    out = []
    for k in dict.fromkeys(chiavi):
        f = ES_F[k]
        out.append(f'<li><a href="{escape(f["url"])}" rel="noopener">{escape(f["titolo"])}</a> – {escape(f["ente"])}, {escape(f["formato"])}, checked '
                   f'{data_lunga(f["controllato_il"])}' + (f'<br><span class="small">{escape(f["nota"])}</span>' if f.get("nota") else "") + "</li>")
    return "<ul>" + "".join(out) + "</ul>"


def es_ine(cod):
    """Dati INE di maggio 2026 per un Comune (5 cifre), una Comunità (2 cifre) o la Spagna ('')."""
    I = ESN["ine"]
    return I["spagna"] if cod == "" else (I["comunita"] if len(cod) == 2 else I["comuni"]).get(cod, {})


def es_pct(v):
    return f"{v:.2f}".rstrip("0").rstrip(".") + "%"


def es_serie(reg, cod=None):
    """Serie mensile (ultimi 24 mesi) delle case ancora iscritte, per data di iscrizione: Comune o totale della Comunità."""
    d = ESN[reg]
    return d["per_mese_totale"] if cod is None else d["per_mese"].get(cod, {})


def es_ultimo_mese_con(serie):
    m = [k for k in ESN["mesi"] if serie.get(k)]
    return m[-1] if m else None


def es_tabella_mesi(serie):
    righe = "".join(f"<tr><td>{es_mese(m)}</td><td>{es_n(serie.get(m, 0))}</td></tr>" for m in ES_MESI)
    a, b = sum(serie.get(m, 0) for m in ES_MESI), sum(serie.get(m, 0) for m in ES_MESI_PRIMA)
    righe += (f"<tr><td><strong>{es_mese(ES_MESI[0], True)} – {es_mese(ES_MESI[-1], True)}</strong></td><td><strong>{es_n(a)}</strong></td></tr>"
              f"<tr><td>{es_mese(ES_MESI_PRIMA[0], True)} – {es_mese(ES_MESI_PRIMA[-1], True)}</td><td>{es_n(b)}</td></tr>")
    return f'<div class="tab sintesi"><table><thead><tr><th>Month of registration</th><th>Homes</th></tr></thead><tbody>{righe}</tbody></table></div>'


ES_NOTA_SERIE = ("The register lists the homes that are registered today, with their registration date. A home registered in a month and removed later "
                 "is not counted, so these figures show homes added in each month that are still on the register.")
ES_NOTA_INE = ("INE (Spain's national statistics institute) counts tourist homes listed on the three most used accommodation platforms in Spain, by web scraping "
               "and removing duplicates; it publishes the count twice a year, with reference dates in May and November. It is a different measure from the regional register, "
               "which also includes homes that are not advertised.")


def es_ine_frase(cod, nome):
    d = es_ine(cod)
    if not d:
        return ""
    return (f"INE counted {es_n(d['case'])} tourist homes with {es_n(d['posti'])} bed places in {nome} in {ES_INE_MESE}"
            + (f", {es_pct(d['pct'])} of all dwellings" if d.get("pct") is not None else "") + ".")


ES_CHI_VERIFICA = {"bal": "the island Consell (the tourism administration of each island)", "can": "the island Cabildo"}


def es_chi(R):
    """A chi chiedere di controllare un numero quando non c'è una ricerca pubblica: isola solo dove vale (Baleari, Canarie)."""
    return ES_CHI_VERIFICA.get(R["id"], "the regional tourism administration")


def es_agg(reg):
    """', updated on …' per il registro catalano (data del dataset), vuoto per gli altri (aggiornati ogni giorno)."""
    return f", updated on {data_lunga(ESN['cat']['aggiornato'])}" if reg == "cat" else ""


def es_reg_totale(R):
    return ESN[R["dati"]]["totale"] if R.get("dati") else None


def es_numero_riga(R):
    return {"si": "Required in every advert", "contratto": "On the document given to guests (no advert rule found in the texts we read)",
            "annullato": "Advert rule annulled (Supreme Court, 2018)"}[R["annunci"]]


def es_verifica_html(R):
    if R["verifica"]:
        testo, k = R["verifica"]
        return es_link(k, testo)
    return "No official public search read by us"


def es_risposta():
    s = ES["sentenze"]
    con = [es_in(ES_REG[k]) for k in ("cv", "cat", "bal", "can")]
    return (f"In Spain the registration number for a holiday let comes from the regional tourism register: the Supreme Court annulled the national "
            f"Registro Único de Arrendamientos procedure in judgments of {data_lunga(s['date'][0])}, {data_lunga(s['date'][1])} and {data_lunga(s['date'][2])} "
            f"(published in the BOE on {data_lunga(s['bollettini'][0])[:-5]}, {data_lunga(s['bollettini'][1])[:-5]} and {data_lunga(s['bollettini'][2])}), and the laws of {', '.join(con[:-1])} and {con[-1]} require the regional number in every advert "
            f"(official texts on BOE, checked on {ES_CHECK}). "
            "Andalusia requires the registration code on the document given to guests; in the Madrid region the advert rule was annulled in 2018.")


def es_faq_indice():
    s = ES["sentenze"]
    reg_dati = [ES_REG[k] for k in ("cv", "and", "cat")]
    return [
        ("Do I need a tourist licence to rent out my property in Spain?",
         "Yes, for holiday lets to tourists. Each region regulates them: the owner or host files a declaration (declaración responsable) and the home is entered "
         "on the regional tourism register. Most regions also require a municipal urban-planning report or licence, and some limit new registrations to certain "
         "zones or municipalities. The regional pages below list the rules we read in the official texts."),
        ("Which registration number must appear in a Spanish holiday let advert?",
         "Where the regional law requires it, the regional tourism registration number: Valencian (Ley 15/2018, art. 19), Catalan (Ley 13/2002, art. 73.5), "
         "Balearic (Ley 8/2012, art. 28.3) and Canary (Ley 6/2025, art. 8.6) law require it in every advert; Andalusia requires the RTA code on the document "
         "given to guests and the Madrid rule was annulled in 2018. The national number from the Registro Único de Arrendamientos lost its legal basis when the "
         f"Supreme Court annulled that procedure in {s['date'][0][:4]}."),
        ("Is the Registro Único de Arrendamientos still in force?",
         f"No. Three Supreme Court judgments ({data_lunga(s['date'][0])}, {data_lunga(s['date'][1])} and {data_lunga(s['date'][2])}) annulled the single registration "
         "procedure of Royal Decree 1312/2024 and the obligation to register with the Property Register to obtain a number. The Ventanilla Única Digital de "
         "Arrendamientos, the national gateway through which platforms send data to the authorities, was not annulled."),
        ("How can I check a Spanish tourist licence number online?",
         "Three regions publish their register as open data or a public search: " +
         "; ".join(f"{R['nome']} ({ES_F[R['verifica'][1]]['ente']})" for R in reg_dati) +
         ". The links are in the table above. For the Balearic Islands, the Canary Islands and the Madrid region we did not find an official public search we could read."),
        ("How much does a tourist licence cost in Spain?",
         "The official texts we read set no single price. Registering with the region is done by a declaration; the costs come from the documents and reports each "
         "region and town hall asks for (for example the municipal urban-planning report in the Valencian Community or the CIVUT certificate in Madrid) and from "
         "municipal fees, which vary. Ask the Ayuntamiento before you start."),
        ("Can I still get a new tourist licence in Spain?",
         "It depends on the region and the town. In the Balearic Islands new declarations are only possible in zones declared suitable; in 262 Catalan municipalities "
         "tourist use needs a prior urban-planning licence; Andalusian town halls can limit the number of tourist homes by building or area; in the Valencian Community "
         "a favourable municipal compatibility report is required. The monthly figures on each town page show how many homes are still being added to the "
         "Valencian and Andalusian registers."),
    ]


def es_faq_html(faq):
    html_ = "".join(f'<details class="faq"><summary>{escape(q)}</summary><p>{escape(r)}</p></details>' for q, r in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]}
    return f'<div class="faq-box">{html_}</div>', ld


def es_titolo_nome(c):
    return c["nome"].split(" (")[0]


def es_titolo_comune(c):
    nome = es_titolo_nome(c)
    if c["registro"]:
        return f"{nome} tourist licence 2026: {es_n(ESN[c['registro']]['per_comune'].get(c['ine'], 0))} registered holiday lets"
    return f"{nome} tourist licence 2026: {es_n(es_ine(c['ine']).get('case', 0))} tourist homes (INE)"


def es_comune_numero(c):
    if c["registro"]:
        return ESN[c["registro"]]["per_comune"].get(c["ine"], 0)
    return es_ine(c["ine"]).get("case", 0)


def es_griglia_comuni(rel, regione=None, salta=""):
    out = []
    for c in ES_COMUNI:
        if (regione and c["regione"] != regione) or c["slug"] == salta:
            continue
        if c["registro"]:
            sub = f"{es_n(es_comune_numero(c))} on the {ES_REG[c['regione']]['nome_breve']} register"
        else:
            sub = f"{es_n(es_comune_numero(c))} tourist homes (INE)"
        out.append(f'<a href="{rel}{ES_SLUG}{c["slug"]}/">{escape(c["nome"])}<small>{escape(sub)}</small></a>')
    return '<div class="griglia">' + "".join(out) + "</div>"


def es_callout(rel):
    """Riquadro di collegamento all'indice (pagina Spagna)."""
    return (f'<section class="card callout es-box" aria-label="Spain holiday let licence"><span class="ic">{ico("door")}</span>'
            f'<p><strong>Letting a home in Spain?</strong> The national register was annulled in 2026: the number you need now comes from your region. '
            f'<a href="{rel}{ES_SLUG}">Spain holiday let licence: region by region</a></p></section>')


def pagina_es_indice():
    rel = "../"
    s = ES["sentenze"]
    righe = []
    for R in ES["regioni"]:
        d = es_ine(R["ine"])
        righe.append(f'<tr><td><a href="{rel}{ES_SLUG}{R["slug"]}/">{escape(R["nome"])}</a></td><td>{escape(R["registro"])}<br><span class="small">{escape(R["numero"])}</span></td>'
                     f'<td>{escape(es_numero_riga(R))}</td><td>{es_verifica_html(R)}</td><td>{es_n(d["case"])}</td></tr>')
    tot = es_ine("")
    serie_cv, serie_and = es_serie("gva"), es_serie("rta")
    righe_m = "".join(f"<tr><td>{es_mese(m)}</td><td>{es_n(serie_cv.get(m, 0))}</td><td>{es_n(serie_and.get(m, 0))}</td></tr>" for m in ES_MESI)
    faq_html, ld = es_faq_html(es_faq_indice())
    tutte = (s["fonti"] + ["rd1312", "ine_metodo", "ine_39363", "ine_39366"] + [k for R in ES["regioni"] for k in R["fonti"]])
    corpo = f"""<section class="hero">{h1_diviso("Spain holiday let licence 2026: the registration number you need")}
<p class="risposta">{escape(es_risposta())}</p>
{es_fonte(s["fonti"] + ["rd1312"])}</section>
<h2>Region by region</h2>
<div class="tab"><table><thead><tr><th>Region</th><th>Register and number</th><th>Number in adverts</th><th>Check a number</th><th>Tourist homes (INE, {ES_INE_MESE})</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>
<p class="small">Spain in total: {es_n(tot["case"])} tourist homes and {es_n(tot["posti"])} bed places in {ES_INE_MESE}, {es_pct(tot["pct"])} of all dwellings (INE). {escape(ES_NOTA_INE)}</p>
{es_fonte(["ine_39363", "ine_39366", "ine_metodo"])}
{AVVISO_ES}
{AD}
<h2>What the Supreme Court annulled, and what remains</h2>
<p>Royal Decree 1312/2024 created two things: a single national registration procedure (Registro Único de Arrendamientos), run through the Property Register, that gave each short-term rental a number to show on platforms, and the Ventanilla Única Digital de Arrendamientos, a national gateway for data between platforms and authorities. It took effect on 1 July 2025.</p>
<ul><li><strong>Annulled:</strong> the single registration procedure and the obligation to register with the Property Register (or the Movable Property Register) to obtain a number for short-term rentals offered on online platforms: {escape(s["articoli_annullati"])}. Judgments of {data_lunga(s["date"][0])} (appeal of the Generalitat Valenciana, BOE {data_lunga(s["bollettini"][0])}), {data_lunga(s["date"][1])} (Apartur and ATA, BOE {data_lunga(s["bollettini"][1])}) and {data_lunga(s["date"][2])} (Region of Murcia, BOE {data_lunga(s["bollettini"][2])}).</li>
<li><strong>Still in force:</strong> the Ventanilla Única Digital de Arrendamientos of the Ministry of Housing (art. 7), the monthly transmission of activity data by platforms through it (art. 6, except the references to the single registration procedure and number), official statistics (art. 11) and the designation of regional and local administrations as competent authorities for the sectoral rules on tourist lets (art. 12 d).</li>
<li><strong>What this means for hosts:</strong> the number that the regional laws require is the regional tourism registration number, set out region by region in the table above.</li></ul>
{es_fonte(s["fonti"] + ["rd1312"])}
<p class="small">{escape(s["nota_numero"])}</p>
<h2>Town by town</h2>
<p>Registered holiday homes from the official registers (Valencian Community, Andalusia, Catalonia) and INE counts, with the monthly number of new registrations where the register gives the date.</p>
{es_griglia_comuni(rel)}
<h2>New registrations per month</h2>
<p>Holiday homes on the Valencian and Andalusian registers by month of registration ({ES_REGISTRI["gva"][0]} and {ES_REGISTRI["rta"][0]} open data, downloaded on {ES_SCARICATO}).</p>
<div class="tab sintesi"><table><thead><tr><th>Month</th><th>Valencian Community</th><th>Andalusia</th></tr></thead><tbody>{righe_m}</tbody></table></div>
<p class="small">{escape(ES_NOTA_SERIE)}</p>
{es_fonte(["cv_dati", "and_dati"], "Official open data")}
<h2>Questions</h2>
{faq_html}
<h2>Official sources</h2>
{es_fonti_elenco(tutte)}
<p class="small">Spotted a change in the official rules? <a href="{rel}contact/?ref=spain-holiday-let-licence">Tell us</a>.</p>
<p><a href="{rel}country/spain/">Tourist taxes in Spain</a> · <a href="{rel}">Tourist tax calculator</a></p>"""
    pagina(ES_SLUG, "Spain holiday let licence 2026: the registration number you need",
           "After the Supreme Court annulled Spain's national rental register in 2026, the number you need comes from your region. Rules, official sources and counts.",
           corpo, briciole=[("Spain", "country/spain/"), ("Holiday let licence", ES_SLUG)], jsonld_extra=ld)


def es_risposta_regione(R):
    tot = es_reg_totale(R)
    reg = (f" {es_n(tot)} homes are on the register today ({ES_REGISTRI[R['dati']][0]} open data{es_agg(R['dati'])}, downloaded on {ES_SCARICATO})." if tot else "")
    return (f"{R['risposta']}, checked on {data_lunga(ES_F[R['annunci_fonte']]['controllato_il'])}). {R['annunci_testo']}{reg}")


def es_faq_regione(R):
    faq = []
    tot = es_reg_totale(R)
    d = es_ine(R["ine"])
    faq.append((f"How many tourist homes are there in {es_in(R)}?",
                (f"{es_n(tot)} homes are on the {R['registro']} ({ES_REGISTRI[R['dati']][0]} open data{es_agg(R['dati'])}, downloaded on {ES_SCARICATO}). " if tot else "") +
                f"INE counted {es_n(d['case'])} tourist homes listed on the main platforms in {ES_INE_MESE}."))
    faq.append((f"Does the registration number have to appear in adverts in {es_in(R)}?", R["annunci_testo"]))
    if R["verifica"]:
        faq.append((f"How do I check a tourist licence in {es_in(R)}?",
                    f"Search by town or registration number in the official source: {R['verifica'][0]}."))
    else:
        faq.append((f"How do I check a tourist licence in {es_in(R)}?",
                    "We did not find an official public search of the register that we could read. Ask the host for the registration number and check it with "
                    f"{es_chi(R)}."))
    faq.append(("Do I still need the national Registro Único de Arrendamientos number?",
                "No. The Supreme Court annulled the national single registration procedure in judgments of May and June 2026 (BOE). The rules that apply "
                "are the regional ones described on this page."))
    return faq


def pagina_es_regione(R):
    rel = "../../"
    slug = f"{ES_SLUG}{R['slug']}/"
    d = es_ine(R["ine"])
    tot = es_reg_totale(R)
    punti = "".join(f"<li>{escape(t)} <span class=\"small\">({es_link(k, ES_F[k]['ente'])})</span></li>" for t, k in R["punti"])
    serie = ""
    if R.get("dati") in ("gva", "rta"):
        sr = es_serie(R["dati"])
        serie = (f"<h2>New registrations per month in {escape(es_in(R))}</h2>{es_tabella_mesi(sr)}<p class=\"small\">{escape(ES_NOTA_SERIE)}</p>"
                 f"{es_fonte([ES_REGISTRI[R['dati']][2]], 'Official open data')}")
    cifra_reg = (f'<p class="cifra"><span class="lab">{ico("door")}On the {escape(R["registro"])}</span><span class="sr">: </span><strong>{es_n(tot)} homes</strong></p>' if tot else "")
    verifica = (f'<p>{es_link(R["verifica"][1], R["verifica"][0])}.</p>' if R["verifica"] else
                "<p>We did not find an official public search of this register that we could read. Ask the host for the registration number and check it with "
                f"{escape(es_chi(R))}.</p>")
    faq_html, ld = es_faq_html(es_faq_regione(R))
    comuni = [c for c in ES_COMUNI if c["regione"] == R["id"]]
    corpo = f"""<section class="hero">{h1_diviso(ES_TITOLI_REG[R["id"]])}
<p class="risposta">{escape(es_risposta_regione(R))}</p>
{es_fonte([R["annunci_fonte"]] + ([ES_REGISTRI[R["dati"]][2]] if tot else []))}</section>
<section class="card summary" aria-label="Summary"><div>
{cifra_reg}
<p class="cifra"><span class="lab">{ico("city")}Tourist homes listed online (INE, {ES_INE_MESE})</span><span class="sr">: </span><strong>{es_n(d["case"])}</strong></p>
</div><div><p class="lead">Register: {escape(R["registro"])}. Number: {escape(R["numero"])}.</p>
{es_fonte(["ine_39363", "ine_39366"])}</div></section>
{AVVISO_ES}
{AD}
<h2>What the regional rules say</h2>
<ul>{punti}</ul>
<h2>Check a registration number</h2>
{verifica}
{serie}
{f'<h2>Towns</h2>{es_griglia_comuni(rel, R["id"])}' if comuni else ""}
<h2>The national register</h2>
<p>The national single registration procedure (Registro Único de Arrendamientos) was annulled by the Supreme Court in 2026. See <a href="{rel}{ES_SLUG}">Spain holiday let licence: what was annulled and what remains</a>.</p>
<h2>Questions</h2>
{faq_html}
<h2>Official sources</h2>
{es_fonti_elenco(R["fonti"] + ["ine_39363", "ine_39366", "ine_metodo"])}
<p class="small">Spotted a change in the official rules? <a href="{rel}contact/?ref=spain-holiday-let-licence">Tell us</a>.</p>
<p><a href="{rel}{ES_SLUG}">Spain holiday let licence</a> · <a href="{rel}country/spain/">Tourist taxes in Spain</a></p>"""
    pagina(slug, ES_TITOLI_REG[R["id"]],
           (f"{R['nome']}: register, number and rules for holiday lets from the official texts, "
            f"{es_n(d['case'])} tourist homes (INE {ES_INE_MESE})" + (f", {es_n(tot)} on the register." if tot else ".")),
           corpo, briciole=[("Spain", "country/spain/"), ("Holiday let licence", ES_SLUG), (R["nome"], slug)], jsonld_extra=ld)


def es_risposta_comune(c):
    R = ES_REG[c["regione"]]
    nome = c["nome"]
    if c["registro"]:
        n = es_comune_numero(c)
        sr = es_serie(c["registro"], c["ine"]) if c["registro"] in ("gva", "rta") else {}
        ult = ES_MESI[-1]
        extra = (" and an urban-planning licence, since it is one of the 262 municipalities listed in Catalan Decreto-ley 3/2023" if c["regione"] == "cat" else "")
        mese = ""
        if c["registro"] in ("gva", "rta"):
            if sum(sr.get(m, 0) for m in ES_MESI):
                mese = f" and {es_n(sr.get(ult, 0))} were added in {es_mese(ult)}"
            else:
                ultimo = es_ultimo_mese_con(sr)
                mese = (f", none added between {es_mese(ES_MESI[0])} and {es_mese(ult)}"
                        + (f", the latest in {es_mese(ultimo)}" if ultimo else ""))
        agg = f", updated on {data_lunga(ESN['cat']['aggiornato'])}" if c["registro"] == "cat" else ""
        return (f"To let a home to tourists in {nome} you need a {ES_PREFISSI[c['ine'][:2]]} number from the {R['registro']}{extra}; "
                f"{es_n(n)} homes in {es_titolo_nome(c)} are on the register{mese} ({ES_REGISTRI[c['registro']][0]} open data{agg}, downloaded on {ES_SCARICATO}).")
    d = es_ine(c["ine"])
    if c["regione"] == "mad":
        prima = (f"To let a home to tourists in {nome} you file a declaración responsable with a CIVUT certificate to the Community of Madrid "
                 f"(Decreto 79/2014 as amended in 2019, checked on {ES_CHECK})")
    else:
        prima = (f"To let a home to tourists in {nome} you file a DRIAT and need the tourist registration number, which must appear in every advert "
                 f"(Ley 8/2012, art. 28.3, checked on {ES_CHECK})")
    return f"{prima}; INE counted {es_n(d['case'])} tourist homes in {es_titolo_nome(c)} in {ES_INE_MESE}."


def es_faq_comune(c):
    R = ES_REG[c["regione"]]
    nome = es_titolo_nome(c)
    d = es_ine(c["ine"])
    faq = []
    if c["registro"]:
        faq.append((f"How many tourist flats are there in {nome}?",
                    f"{es_n(es_comune_numero(c))} homes are on the {R['registro']} ({ES_REGISTRI[c['registro']][0]} open data{es_agg(c['registro'])}, downloaded on {ES_SCARICATO}). "
                    f"INE counted {es_n(d['case'])} tourist homes listed on the main platforms in {ES_INE_MESE}: the register also includes homes that are not advertised."))
    else:
        faq.append((f"How many tourist flats are there in {nome}?",
                    f"INE counted {es_n(d['case'])} tourist homes with {es_n(d['posti'])} bed places in {ES_INE_MESE}, listed on the main platforms."))
    if c["registro"] in ("gva", "rta"):
        sr = es_serie(c["registro"], c["ine"])
        a = sum(sr.get(m, 0) for m in ES_MESI)
        ult = es_ultimo_mese_con(sr)
        risposta_ = (f"{es_n(a)} homes registered between {es_mese(ES_MESI[0])} and {es_mese(ES_MESI[-1])} are on the register today"
                     + (f"; the most recent registration month is {es_mese(ult)}." if ult else "; none in the last 24 months.")
                     + " The register does not say whether a town hall has stopped new tourist homes: ask the Ayuntamiento.")
        faq.append((f"Are new tourist licences still being registered in {nome}?", risposta_))
    if R["verifica"]:
        faq.append((f"How do I check a tourist licence in {nome}?", f"Search for {nome} in the official source: {R['verifica'][0]}."))
    else:
        faq.append((f"How do I check a tourist licence in {nome}?",
                    "We did not find an official public search of the register that we could read. Ask the host for the registration number and check it with "
                    f"{es_chi(R)}."))
    faq.append((f"What are the rules for a holiday let in {nome}?",
                f"The rules of {es_in(R)} apply (see the regional page), plus the town hall's planning rules and, in a building, the community of owners."))
    return faq


def pagina_es_comune(c):
    rel = "../../"
    R = ES_REG[c["regione"]]
    slug = f"{ES_SLUG}{c['slug']}/"
    d = es_ine(c["ine"])
    nome = es_titolo_nome(c)
    blocco_reg = ""
    chiavi = ["ine_39363", "ine_39366"]
    if c["registro"]:
        n = es_comune_numero(c)
        k = ES_REGISTRI[c["registro"]][2]
        blocco_reg = f'<p class="cifra"><span class="lab">{ico("door")}On the {escape(R["registro"])}</span><span class="sr">: </span><strong>{es_n(n)} homes</strong></p>'
        chiavi = [k] + chiavi
    serie = ""
    if c["registro"] in ("gva", "rta"):
        sr = es_serie(c["registro"], c["ine"])
        serie = (f"<h2>New registrations per month in {escape(nome)}</h2>{es_tabella_mesi(sr)}<p class=\"small\">{escape(ES_NOTA_SERIE)}</p>"
                 f"{es_fonte([ES_REGISTRI[c['registro']][2]], 'Official open data')}")
    confronto = ""
    if c["registro"]:
        confronto = (f"<p>{es_n(es_comune_numero(c))} homes on the register against {es_n(d['case'])} counted by INE on the platforms: {escape(ES_NOTA_INE)}</p>")
    punti = "".join(f"<li>{escape(t)} <span class=\"small\">({es_link(k, ES_F[k]['ente'])})</span></li>" for t, k in R["punti"])
    if c["regione"] == "cat":
        punti = (f"<li>{escape(nome)} is in the list of 262 municipalities of Decreto-ley 3/2023 where tourist use of a home needs a prior urban-planning licence. "
                 f"<span class=\"small\">({es_link('cat_dl', ES_F['cat_dl']['ente'])})</span></li>") + punti
    verifica = (f'<p>{es_link(R["verifica"][1], R["verifica"][0])}: search for {escape(nome)}.</p>' if R["verifica"] else
                "<p>We did not find an official public search of this register that we could read.</p>")
    faq_html, ld = es_faq_comune(c), None
    faq_html, ld = es_faq_html(faq_html)
    corpo = f"""<section class="hero">{h1_diviso(es_titolo_comune(c))}
<p class="risposta">{escape(es_risposta_comune(c))}</p>
{es_fonte(chiavi[:1] + [R["annunci_fonte"]])}</section>
<section class="card summary" aria-label="Summary"><div>
{blocco_reg}
<p class="cifra"><span class="lab">{ico("city")}Tourist homes listed online (INE, {ES_INE_MESE})</span><span class="sr">: </span><strong>{es_n(d["case"])}</strong></p>
</div><div><p class="lead">{escape(es_ine_frase(c["ine"], nome))}</p>
{es_fonte(["ine_39363", "ine_39366"])}</div></section>
{AVVISO_ES}
{AD}
{serie}
{confronto}
<h2>The rules in {escape(es_in(R))}</h2>
<p><strong>Registration number:</strong> {escape(R["annunci_testo"])}</p>
<ul>{punti}</ul>
<p>The town hall of {escape(nome)} sets its own planning rules for tourist use: ask the Ayuntamiento (urbanismo) before you buy or start letting. Full details: <a href="{rel}{ES_SLUG}{R["slug"]}/">{escape(R["nome"])} holiday let licence</a>.</p>
<h2>Check a registration number</h2>
{verifica}
<h2>Questions</h2>
{faq_html}
<h2>Official sources</h2>
{es_fonti_elenco(chiavi + R["fonti"] + ["ine_metodo"])}
<p class="small">Spotted a change? <a href="{rel}contact/?ref=spain-holiday-let-licence">Tell us</a>.</p>
<h2>Other towns</h2>
{es_griglia_comuni(rel, salta=c["slug"])}
<p><a href="{rel}{ES_SLUG}">Spain holiday let licence</a> · <a href="{rel}{ES_SLUG}{R["slug"]}/">{escape(R["nome"])}</a></p>"""
    desc = re.split(r"(?<=\.) ", es_risposta_comune(c))[0]
    pagina(slug, es_titolo_comune(c), desc if len(desc) <= 300 else desc[:297] + "...",
           corpo, briciole=[("Spain", "country/spain/"), ("Holiday let licence", ES_SLUG), (R["nome"], f"{ES_SLUG}{R['slug']}/"), (nome, slug)], jsonld_extra=ld)


def pagine_es():
    pagina_es_indice()
    for R in ES["regioni"]:
        pagina_es_regione(R)
    for c in ES_COMUNI:
        pagina_es_comune(c)


# ---------------------------------------------------------------- USA: tassa sugli alberghi in Florida e Texas (7/11/2026)
# Dati: dati/usa.json, scritto da raccolta/usa.py dai file ufficiali (Florida Department of Revenue: DR-15TDT e DR-15DSS; Texas Comptroller:
# dataset data.texas.gov er34-v24h e pagine sulla Hotel Occupancy Tax; Census: contee di ogni città). Le pagine di città e contee sono
# solo quelle con ricerche vere nell'autocomplete (dati/usa.json -> pagine). Il calcolatore è una somma di percentuali sul prezzo della
# camera per notte, ognuna con le sue date (sovrimposte della Florida) e la sua soglia di prezzo (Texas: 15 $ per lo Stato, 2 $ per le
# tasse locali). Motore uguale in Python (us_calcola) e JS (US_JS): verifica.py li confronta.
US = json.loads((DATI / "usa.json").read_text(encoding="utf-8"))
US_F = US["fonti"]
US_FR = US["frasi"]
US_FL = US["florida"]
US_TX = US["texas"]
US_HUB = "usa/"
US_FLS = "usa/florida/"
US_TXS = "usa/texas/"
US_CHECK = data_lunga(US["controllato_il"])
US_FINE_DSS = f"{US_FL['dss_anno']}-12-31"
US_PREZZO = 200
US_ZONE = US_FL["zone"]
US_TX_AGG = data_lunga(US_F["tx_dati"]["aggiornato_il"])
AVVISO_US = ('<p class="avviso"><strong>Not tax advice.</strong> This page adds up the rates in official state files. Your hotel or host applies the '
             'taxes and may round them; some cities and districts charge taxes of their own that a state file does not show. '
             'Check the final amount on your booking.</p>')


def us_pct(v):
    """6 -> '6%', 12.5 -> '12.5%', 1.8 -> '1.8%'."""
    return ("%.4f" % v).rstrip("0").rstrip(".") + "%"


def us_usd(v):
    return soldi(v, "USD")


def tx_val(s):
    """Aliquota del file del Texas ('0.07') in percento (7.0)."""
    return round(float(s) * 100, 6) if s not in (None, "") else 0.0


def us_link(k, testo=None):
    f = US_F[k]
    return f'<a href="{escape(f["url"])}" rel="noopener">{escape(testo or f["titolo"])}</a>'


def us_fonte(chiavi, etichetta="Official sources"):
    ff = [US_F[k] for k in chiavi]
    data_ = data_lunga(max(f["controllato_il"] for f in ff))
    lab = etichetta if len(ff) > 1 else etichetta.rstrip("s")
    return (f'<p class="fonte">{lab}: ' + " · ".join(f'<a href="{escape(f["url"])}" rel="noopener">{escape(f["titolo"])}</a> ({escape(f["ente"])})'
                                                     for f in ff) + f" · checked on {data_}</p>")


def us_fonti_elenco(chiavi):
    out = []
    for k in dict.fromkeys(chiavi):
        f = US_F[k]
        extra = f", revision {f['revisione']}" if f.get("revisione") else ""
        if k == "tx_dati":
            extra = f", {f['righe']} rows, data updated {US_TX_AGG}"
        out.append(f'<li><a href="{escape(f["url"])}" rel="noopener">{escape(f["titolo"])}</a> – {escape(f["ente"])}, {escape(f["formato"])}{extra}, '
                   f'checked {data_lunga(f["controllato_il"])}</li>')
    return "<ul>" + "".join(out) + "</ul>"


# ---- Florida: contee, zone, componenti
US_FLC = {c["id"]: c for c in US_FL["contee"]}


def fl_slug(c):
    return f"{US_FLS}{slugify(c['nome'])}-county/"


def fl_nome(c):
    return {"Desoto": "DeSoto"}.get(c["nome"], c["nome"]) + " County"


def fl_zone(c):
    """Zone della contea (note del DR-15TDT): [(id, nome, aliquota)] o una sola zona senza nome."""
    zz = US_ZONE.get(c["id"])
    return [(z["id"], z["nome"], z["aliquota"]) for z in zz] if zz else [("", "", c["aliquota"])]


def fl_comp(c, aliquota, zona_nome=""):
    comp = [{"label": "Florida state sales tax", "pct": US_FL["stato"], "on": True}]
    for p in c["surtax"]["parti"]:
        comp.append({"label": f"{fl_nome(c)} discretionary sales surtax", "pct": p["aliquota"], "dal": p["dal"], "al": p["al"], "on": True})
    if aliquota > 0:
        lab = (f"Local option transient rental taxes ({zona_nome})" if c["id"] == "miami-dade" else f"{fl_nome(c)} local option transient rental tax")
        comp.append({"label": lab, "pct": aliquota, "on": True})
    return comp


def fl_luogo(c, nome=None, pagina=None, zone=None):
    zz = [z for z in fl_zone(c) if zone is None or z[0] in zone]
    return {"nome": nome or fl_nome(c), "gruppo": "Florida", "pagina": pagina or fl_slug(c), "regola": "fl", "fine": US_FINE_DSS,
            "zone": [{"id": i, "nome": n, "comp": fl_comp(c, a, n)} for i, n, a in zz]}


def fl_fine_surtax(c):
    """'the whole 1%' / '0.5% (of 1.5%)': parte della sovrimposta che il modulo dà in scadenza alla fine dell'anno del modulo."""
    fin = sum(p["aliquota"] for p in c["surtax"]["parti"] if p["al"] and OGGI.isoformat() <= p["al"] <= US_FINE_DSS)
    if not fin:
        return ""
    tot = fl_surtax(c)
    return f"the whole {us_pct(tot)}" if abs(fin - tot) < 1e-9 else f"{us_pct(fin)} (of {us_pct(tot)})"


def fl_surtax(c, d=None):
    d = d or OGGI.isoformat()
    return sum(p["aliquota"] for p in c["surtax"]["parti"] if (not p["dal"] or p["dal"] <= d) and (not p["al"] or d <= p["al"]))


# ---- Texas: righe del file, componenti
US_TXR = [r for r in US_TX["righe"]]
US_TXK = {r["nome"].lower(): r for r in US_TXR if r["tipo"] == "county"}
US_TXC = {r["nome"].lower(): r for r in US_TXR if r["tipo"] != "county"}
TX_HOUSTON = [("Harris County hotel tax", 2.0), ("Harris County - Houston Sports Authority tax", 2.0)]  # FAQ del Comptroller (frase "houston")


def tx_tot_locale(r):
    return tx_val(r["r351"]) + tx_val(r["r334"])


def tx_slug_citta(r):
    return f"{US_TXS}{slugify(r['nome'])}/"


def tx_slug_contea(r):
    return f"{US_TXS}{slugify(r['nome'])}-county/"


def tx_contee_righe(r):
    """Righe di contea del file per le contee in cui sta la città (Census)."""
    return [US_TXK[k.lower()] for k in r.get("contee", []) if k.lower() in US_TXK and tx_tot_locale(US_TXK[k.lower()]) > 0]


def tx_contee_venue(r):
    """Contee con una venue tax (capitolo 334): nel calcolo della città, casella accesa (revisione del 7/11/2026)."""
    return [k for k in tx_contee_righe(r) if tx_val(k["r334"]) > 0 and k["nome"] != "Harris"]


def tx_contee_nota(r):
    """Contee con una hotel occupancy tax di contea (capitolo 352): solo una nota, il file non dice se vale dentro la città."""
    return [k for k in tx_contee_righe(r) if tx_val(k["r351"]) > 0 and k["nome"] != "Harris"]


def tx_venue_frase(k):
    return f"{us_pct(tx_val(k['r334']))} {k['nome']} County venue tax where it applies (the file reports {k['r334']})"


def tx_comp_contea(k, on):
    out = []
    if tx_val(k["r351"]) > 0:
        out.append({"label": f"{k['nome']} County hotel occupancy tax (reported)", "pct": tx_val(k["r351"]), "min": US_TX["soglia_locale"], "on": on, "opz": True})
    if tx_val(k["r334"]) > 0:
        out.append({"label": f"{k['nome']} County venue tax (reported)", "pct": tx_val(k["r334"]), "min": US_TX["soglia_locale"], "on": on, "opz": True})
    return out


def tx_comp(r):
    comp = [{"label": "Texas state hotel occupancy tax", "pct": US_TX["stato"], "min": US_TX["soglia_stato"], "on": True}]
    if tx_val(r["r351"]) > 0:
        comp.append({"label": f"{r['nome']} city hotel occupancy tax", "pct": tx_val(r["r351"]), "min": US_TX["soglia_locale"], "on": True})
    if tx_val(r["r334"]) > 0:
        comp.append({"label": f"{r['nome']} venue tax", "pct": tx_val(r["r334"]), "min": US_TX["soglia_locale"], "on": True})
    if r["nome"] == "Houston":
        comp += [{"label": lab, "pct": p, "min": US_TX["soglia_locale"], "on": True} for lab, p in TX_HOUSTON]
    else:
        for k in tx_contee_venue(r):
            comp.append({"label": f"{k['nome']} County venue tax (reported)", "pct": tx_val(k["r334"]), "min": US_TX["soglia_locale"], "on": True, "opz": True})
    return comp


def tx_luogo(r):
    return {"nome": r["nome"], "gruppo": "Texas", "pagina": tx_slug_citta(r), "regola": "tx", "zone": [{"id": "", "nome": "", "comp": tx_comp(r)}]}


def tx_luogo_contea(k):
    comp = [{"label": "Texas state hotel occupancy tax", "pct": US_TX["stato"], "min": US_TX["soglia_stato"], "on": True}]
    if k["nome"] == "Harris":  # dalla FAQ del Comptroller (esempio di Houston); il 9 % del file non è coerente con l'esempio
        comp += [{"label": lab, "pct": p, "min": US_TX["soglia_locale"], "on": True} for lab, p in TX_HOUSTON]
    else:
        comp += tx_comp_contea(k, True)
    return {"nome": f"{k['nome']} County", "gruppo": "Texas", "pagina": tx_slug_contea(k), "regola": "tx", "zone": [{"id": "", "nome": "", "comp": comp}]}


# ---- motore (uguale al JS)
def us_attivo(c, d, prezzo):
    return (not c.get("dal") or c["dal"] <= d) and (not c.get("al") or d <= c["al"]) and prezzo >= c.get("min", 0)


def us_calcola(L, z, on, checkin, notti, prezzo):
    """Tassa del soggiorno: per ogni notte, ogni imposta accesa e in vigore quel giorno (e con il prezzo sopra la sua soglia) aggiunge
    prezzo × aliquota. Florida: oltre sei mesi le tasse locali non si applicano (DR-15TDT) e il calcolo si ferma. Texas: da 30 notti
    si paga sulle prime 30 se l'ospite non ha avvisato per iscritto prima (FAQ del Comptroller)."""
    Z = L["zone"][z]
    out = {"totale": 0.0, "righe": [], "fuori": False, "tassate": notti, "dopo": 0, "trenta": False}
    if L["regola"] == "fl" and _add(checkin, notti) > _piu_mesi(checkin, 6):
        out["fuori"] = True
        return out
    n = notti
    if L["regola"] == "tx" and notti >= 30:
        n, out["trenta"] = 30, True
    out["tassate"] = n
    g, ordine = {}, []
    for i in range(n):
        d = _add(checkin, i)
        if L.get("fine") and d > L["fine"]:
            out["dopo"] += 1
        for k, c in enumerate(Z["comp"]):
            if not on[k] or not us_attivo(c, d, prezzo):
                continue
            if c["label"] not in g:
                g[c["label"]] = [c["label"], 0.0, 0, None]
                ordine.append(c["label"])
            x = g[c["label"]]
            x[1] += prezzo * c["pct"] / 100
            if x[3] != d:
                x[2] += 1
                x[3] = d
    out["righe"] = [[x[0], x[1], x[2]] for x in (g[k] for k in ordine)]
    out["totale"] = sum(x[1] for x in out["righe"])
    return out


def _add(iso, n):
    return (date.fromisoformat(iso) + timedelta(days=n)).isoformat()


def us_on(Z):
    return [bool(c["on"]) for c in Z["comp"]]


def us_tot_pct(Z, d=None, tutte=False):
    """Somma delle aliquote accese (o tutte) in vigore al giorno d, per un prezzo sopra tutte le soglie."""
    d = d or OGGI.isoformat()
    return round(sum(c["pct"] for c in Z["comp"] if (tutte or c["on"]) and us_attivo(c, d, 10 ** 9)), 6)


US_JS = r"""
function usAttivo(c,d,p){return (!c.dal||c.dal<=d)&&(!c.al||d<=c.al)&&p>=(c.min||0);}
function usCalcola(L,z,on,ci,notti,prezzo){var Z=L.zone[z],out={totale:0,righe:[],fuori:false,tassate:notti,dopo:0,trenta:false};
  if(L.regola==='fl'&&addDays(ci,notti)>piuMesi(ci,6)){out.fuori=true;return out;}
  var n=notti;if(L.regola==='tx'&&notti>=30){n=30;out.trenta=true;}out.tassate=n;var g={},ord=[];
  for(var i=0;i<n;i++){var d=addDays(ci,i);if(L.fine&&d>L.fine)out.dopo++;
    for(var k=0;k<Z.comp.length;k++){var c=Z.comp[k];if(!on[k]||!usAttivo(c,d,prezzo))continue;
      if(!g[c.label]){g[c.label]=[c.label,0,0,null];ord.push(c.label);}var x=g[c.label];x[1]+=prezzo*c.pct/100;if(x[3]!==d){x[2]++;x[3]=d;}}}
  out.righe=ord.map(function(k){var x=g[k];return [x[0],x[1],x[2]];});out.totale=out.righe.reduce(function(s,x){return s+x[1];},0);return out;}
"""

US_APP_JS = r"""
(function(){document.querySelectorAll('[data-us]').forEach(function(box){var D=JSON.parse(box.querySelector('script[type="application/json"]').textContent);
  var f=box.querySelector('form'),out=box.querySelector('[data-out]'),sel=f.querySelector('[name=luogo]'),zs=f.querySelector('[name=zona]'),opz=box.querySelector('[data-opz]'),link=box.querySelector('[data-link]');
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function q(n){return f.querySelector('[name='+n+']');}
  function oggi(){var x=new Date();return new Date(Date.UTC(x.getFullYear(),x.getMonth(),x.getDate())).toISOString().slice(0,10);}
  function pc(v){return String(Math.round(v*1e4)/1e4)+'%';}
  if(sel){var gr={},ord=[];D.forEach(function(L,i){if(!gr[L.gruppo]){gr[L.gruppo]=[];ord.push(L.gruppo);}gr[L.gruppo].push(i);});
    sel.innerHTML=ord.map(function(g){return '<optgroup label="'+esc(g)+'">'+gr[g].map(function(i){return '<option value="'+i+'">'+esc(D[i].nome)+'</option>';}).join('')+'</optgroup>';}).join('');}
  function L(){return sel?D[+sel.value]:D[0];}
  function Z(){var P=L();return (zs&&P.zone.length>1)?(+zs.value||0):0;}
  function prepara(){var P=L();if(zs){zs.innerHTML=P.zone.map(function(z,i){return '<option value="'+i+'">'+esc(z.nome)+'</option>';}).join('');zs.closest('label').hidden=P.zone.length<2;}
    opzioni();if(link){link.href=link.dataset.base+P.pagina;link.querySelector('span').textContent='Breakdown, sources and questions for '+P.nome;}}
  function opzioni(){var C=L().zone[Z()].comp;var h='';C.forEach(function(c,k){if(c.opz)h+='<label class="us-opz"><input type="checkbox" data-k="'+k+'"'+(c.on?' checked':'')+'><span>Add '+esc(c.label)+', '+pc(c.pct)+'</span></label>';});
    opz.innerHTML=h;opz.hidden=!h;}
  function agg(){var P=L(),z=Z(),C=P.zone[z].comp;var on=C.map(function(c,k){if(!c.opz)return !!c.on;var cb=opz.querySelector('[data-k="'+k+'"]');return cb?cb.checked:!!c.on;});
    var notti=Math.max(1,Math.min(365,parseInt(q('notti').value,10)||1)),pr=Math.max(0,parseFloat(q('prezzo').value)||0),ci=q('checkin').value||oggi();
    var o=usCalcola(P,z,on,ci,notti,pr);var h;
    if(o.fuori){h='<div class="r-lab">Estimated tax for this stay</div><div class="tot">Not calculated</div><ul class="r-righe"><li>The local option taxes cover rentals for a term of six months or less (Florida Department of Revenue, form DR-15TDT). For a longer rental, ask the host or the county.</li></ul>';out.innerHTML=h;return;}
    var base=pr*notti;h='<div class="r-lab">Estimated tax for this stay</div><div class="tot">'+soldi(o.totale,'USD')+'</div>';
    h+='<dl class="r-dl"><div><dt>Room cost</dt><dd>'+soldi(base,'USD')+'</dd></div><div><dt>Room cost with tax</dt><dd>'+soldi(base+o.totale,'USD')+'</dd></div><div><dt>Tax as % of the room</dt><dd>'+(base?pc(o.totale/base*100):'–')+'</dd></div><div><dt>Average tax per night</dt><dd>'+soldi(o.totale/notti,'USD')+'</dd></div></dl><ul class="r-righe">';
    o.righe.forEach(function(x){h+='<li><span>'+esc(x[0])+', '+plur(x[2],'night')+'</span><strong class="eq">= '+soldi(x[1],'USD')+'</strong></li>';});
    if(!o.righe.length)h+='<li>No tax applies at this price.</li>';
    C.forEach(function(c,k){if(on[k]&&pr<(c.min||0))h+='<li>'+esc(c.label)+': not due below '+soldi(c.min,'USD')+' a night.</li>';});
    C.forEach(function(c,k){if(c.opz&&!on[k])h+='<li>Not included: '+esc(c.label)+', '+pc(c.pct)+' (tick it above if your bill shows it).</li>';});
    if(o.trenta)h+='<li>Stay of 30 nights or more: tax counted on the first 30 nights. A guest who tells the hotel in writing beforehand is exempt from the day of the notice (Texas Comptroller).</li>';
    if(o.dopo)h+='<li>'+plur(o.dopo,'night')+' after '+esc(P.fine.slice(0,4))+': the surtaxes follow the dates in the '+esc(P.fine.slice(0,4))+' form; the Department publishes the next form every November.</li>';
    h+='</ul>';out.innerHTML=h;}
  if(sel)sel.addEventListener('change',function(){prepara();agg();});
  if(zs)zs.addEventListener('change',function(){opzioni();agg();});
  opz.addEventListener('change',agg);
  f.addEventListener('input',function(e){if(e.target!==sel&&e.target!==zs)agg();});f.addEventListener('submit',function(e){e.preventDefault();});
  if(!q('checkin').value)q('checkin').value=oggi();prepara();agg();});})();
"""


def us_calcolatore(luoghi, rel, con_scelta=False):
    scelta = (f'<label class="pieno"><span class="lt">{ico("pin")}County or city</span><select name="luogo"></select></label>' if con_scelta else "")
    link = (f'<p class="calc-link"><a data-link data-base="{rel}" href="{rel}{luoghi[0]["pagina"]}"><span>Breakdown, sources and questions</span>{ico("arrow")}</a></p>'
            if con_scelta else "")
    dati = json.dumps(luoghi, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f"""<div class="card calc" data-us>
<div class="calc-grid">
<form autocomplete="off">
<div class="campi">
{scelta}
<label class="pieno" hidden><span class="lt">{ico("city")}Area</span><select name="zona"></select></label>
<label data-campo="checkin"><span class="lt">{ico("calendar")}Check-in date</span><input type="date" name="checkin" value="{OGGI.isoformat()}"></label>
<label data-campo="notti"><span class="lt">{ico("moon")}Nights</span><input type="number" name="notti" min="1" max="365" value="3" inputmode="numeric"></label>
<label class="pieno" data-campo="prezzo"><span class="lt">{ico("tag")}Room price per night before tax (USD)</span><input type="number" name="prezzo" min="0" step="any" value="{US_PREZZO}" inputmode="decimal"></label>
<div class="pieno us-opzioni" data-opz hidden></div>
</div>
</form>
<div class="calc-out">
<div class="risultato" data-out aria-live="polite"><noscript>Turn on JavaScript to use the calculator. The table below shows every rate.</noscript></div>
{link}
</div>
</div>
<script type="application/json">{dati}</script>
</div>"""


US_FORMULA = ("Tax = room price per night × nights × the sum of the percentages that apply. Each percentage counts only on the nights it is in force "
              "(Florida county surtaxes have start and end dates) and, in Texas, only when the price is at least $15 a night for the state tax and $2 a "
              "night for local taxes. Hotels apply the taxes to the room charge and may round each tax: check the final amount on your bill.")


def us_esempio(L, z=0):
    o = us_calcola(L, z, us_on(L["zone"][z]), OGGI.isoformat(), 3, US_PREZZO)
    zona = f" ({L['zone'][z]['nome']})" if L["zone"][z]["nome"] else ""
    return (f"Example: {us_usd(US_PREZZO)} a night, 3 nights from {data_lunga(OGGI.isoformat())}{escape(zona)} → <strong>{us_usd(o['totale'])}</strong> in tax, "
            f"{us_usd(US_PREZZO * 3 + o['totale'])} in total.")


def us_tabella(L, z=0, rel=""):
    """Tabella delle imposte di una zona: nome, aliquota oggi, chi la fissa e la fonte."""
    righe, oggi = [], OGGI.isoformat()
    vis = {}
    for c in L["zone"][z]["comp"]:
        if not us_attivo(c, oggi, 10 ** 9):
            continue
        k = c["label"]
        vis[k] = vis.get(k, 0) + c["pct"]
    for c in L["zone"][z]["comp"]:
        k = c["label"]
        if k not in vis:
            continue
        p = vis.pop(k)
        if L["regola"] == "fl":
            fonte = "fl_dss" if "surtax" in k else "fl_tdt"
            nota = ""
            if "surtax" in k:
                fine = sorted({x["al"] for x in L["zone"][z]["comp"] if x["label"] == k and x.get("al") and us_attivo(x, oggi, 1e9)})
                nota = f" (part ends {data_lunga(fine[0])})" if fine else ""
        else:
            fonte = "tx_faq" if (k in dict(TX_HOUSTON) or k.startswith("Texas")) else "tx_dati"
            nota = " (where it applies)" if c.get("opz") else ""
        righe.append(f"<tr><td>{escape(k)}{escape(nota)}</td><td>{us_pct(p)}</td><td>{us_link(fonte, US_F[fonte]['ente'].split(',')[0])}</td></tr>")
    tot = us_tot_pct(L["zone"][z])
    return (f'<div class="tab sintesi us-tab"><table><thead><tr><th>Tax</th><th>Rate today</th><th>Source</th></tr></thead><tbody>{"".join(righe)}'
            f'<tr><th>Total</th><th>{us_pct(tot)}</th><th></th></tr></tbody></table></div>')


def us_faq_html(faq):
    html_ = "".join(f'<details class="faq"><summary>{escape(q)}</summary><p>{escape(r)}</p></details>' for q, r in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]}
    return f'<div class="faq-box">{html_}</div>', ld


def us_sugg(*query):
    """Suggerimenti salvati dell'autocomplete (dati/usa.json -> domanda) per le query date."""
    return [s for q in query for s in (US["domanda"]["query"].get(q) or [])]


def us_ha(sugg, *parole):
    return any(re.search(p, s) for s in sugg for p in parole)


# ---- testi
def fl_tot(c, aliquota, d=None):
    return round(US_FL["stato"] + fl_surtax(c, d) + aliquota, 6)


def fl_parti_testo(c, aliquota, zona=""):
    s = fl_surtax(c)
    parti = [f"{us_pct(US_FL['stato'])} state sales tax"]
    if s:
        parti.append(f"{us_pct(s)} {fl_nome(c)} discretionary sales surtax")
    if aliquota:
        parti.append(f"{us_pct(aliquota)} " + ("local option transient rental taxes" if c["id"] == "miami-dade" else "local option transient rental tax"))
    return ", ".join(parti[:-1]) + " and " + parti[-1] if len(parti) > 1 else parti[0]


FL_FONTE_FRASE = (f"according to the Florida Department of Revenue (forms DR-15TDT, revision {US_F['fl_tdt']['revisione']}, and DR-15DSS for "
                  f"{US_FL['dss_anno']}, checked on {data_lunga(US_F['fl_tdt']['controllato_il'])})")


def fl_risposta(c, nome_luogo, zone=None):
    zz = [z for z in fl_zone(c) if zone is None or z[0] in zone]
    if len(zz) == 1:
        _, zn, a = zz[0]
        dove = f" ({zn})" if zn and zone is None else ""
        if a == 0:
            return (f"In {nome_luogo}{dove} a hotel stay pays {us_pct(fl_tot(c, 0))} of the room price: {fl_parti_testo(c, 0)}; the Department lists no "
                    f"local option transient rental tax there (0%), {FL_FONTE_FRASE}.")
        return f"The hotel tax in {nome_luogo}{dove} is {us_pct(fl_tot(c, a))} of the room price: {fl_parti_testo(c, a)}, {FL_FONTE_FRASE}."
    prima = zz[0]
    altre = [f"{us_pct(fl_tot(c, a))} in {n[0].lower() + n[1:] if n.startswith('Rest') else n}" + (" (no local option transient rental tax)" if a == 0 else "")
             for _, n, a in zz[1:]]
    return (f"The hotel tax in {nome_luogo} is {us_pct(fl_tot(c, prima[2]))} of the room price in {prima[1]} ({fl_parti_testo(c, prima[2])}), "
            + " and ".join(altre) + f", {FL_FONTE_FRASE}.")


def tx_parti_testo(L):
    cc = [c for c in L["zone"][0]["comp"] if c["on"]]
    nomi_ = []
    for c in cc:
        lab = (c["label"].replace("Texas state hotel occupancy tax", "state hotel occupancy tax")
               .replace(" city hotel occupancy tax", " city hotel tax"))
        nomi_.append(f"{us_pct(c['pct'])} {lab}")
    return ", ".join(nomi_[:-1]) + " and " + nomi_[-1]


def tx_risposta(r, L):
    tot = us_tot_pct(L["zone"][0])
    if r["nome"] == "Houston":
        return (f"The hotel tax in Houston, Texas is {us_pct(tot)} of the room price: 6% state tax, 7% city tax, 2% Harris County tax and 2% Harris County - "
                f"Houston Sports Authority tax, according to the Texas Comptroller of Public Accounts (hotel occupancy tax FAQs, checked on "
                f"{data_lunga(US_F['tx_faq']['controllato_il'])}); the City of Houston reported the same 7% for fiscal year {US_TX['anno_fiscale']}.")
    vv = tx_contee_venue(r)
    base = US_TX["stato"] + tx_tot_locale(r)
    if vv:
        citta = [c for c in L["zone"][0]["comp"] if c["on"] and "venue tax (reported)" not in c["label"]]
        s = (f"The hotel tax in {r['nome']}, Texas is {us_pct(base)}–{us_pct(tot)} of the room price: " + tx_parti_testo({"zone": [{"comp": citta}]})
             + ", plus " + " and ".join(tx_venue_frase(k) for k in vv)
             + f", as reported to the Texas Comptroller for fiscal year {US_TX['anno_fiscale']} (data updated {US_TX_AGG}, checked on "
             f"{data_lunga(US_F['tx_dati']['controllato_il'])}).")
        if any(k["nome"] == "Bexar" for k in vv):
            s += " Bexar County's own website did not answer when we checked (HTTP 429), so we could not compare the 1.8% with the county's own figure."
    else:
        s = (f"The hotel tax in {r['nome']}, Texas is {us_pct(tot)} of the room price: {tx_parti_testo(L)}, as reported by the city to the Texas Comptroller "
             f"for fiscal year {US_TX['anno_fiscale']} (data updated {US_TX_AGG}, checked on {data_lunga(US_F['tx_dati']['controllato_il'])}).")
    kk = tx_contee_nota(r)
    if kk:
        s += (" " + " and ".join(f"{k['nome']} County" for k in kk) + " also reported a county hotel occupancy tax ("
              + ", ".join(us_pct(tx_val(k["r351"])) for k in kk) + "): the data does not say whether it applies inside the city, so it is not counted.")
    return s


def tx_risposta_contea(k):
    if k["nome"] == "Harris":
        return (f"In Harris County, Texas the hotel tax is 10% of the room price outside a city with its own tax: 6% state tax, 2% Harris County tax and 2% "
                f"Harris County - Houston Sports Authority tax, as in the Texas Comptroller's example for Houston (hotel occupancy tax FAQs, checked on "
                f"{data_lunga(US_F['tx_faq']['controllato_il'])}); inside a city the city's tax is added (Houston: 7%, 17% in all). The Comptroller's "
                f"dataset reports {us_pct(tx_val(k['r351']))} and {us_pct(tx_val(k['r334']))} for Harris County for fiscal year {US_TX['anno_fiscale']}, "
                "which is not consistent with the Comptroller's example.")
    parti = []
    if tx_val(k["r351"]):
        parti.append(f"a {us_pct(tx_val(k['r351']))} county hotel occupancy tax")
    if tx_val(k["r334"]):
        parti.append(f"a {us_pct(tx_val(k['r334']))} venue tax")
    s = (f"{k['nome']} County, Texas reported " + " and ".join(parti) + f" to the Texas Comptroller for fiscal year {US_TX['anno_fiscale']} (data updated "
         f"{US_TX_AGG}, checked on {data_lunga(US_F['tx_dati']['controllato_il'])}), on top of the 6% state hotel occupancy tax: "
         f"{us_pct(US_TX['stato'] + tx_tot_locale(k))} in all where the county taxes apply; a hotel inside a city also pays that city's hotel tax.")
    return s


def us_tassa_parola(sugg, nome):
    return "tourist tax" if us_ha(sugg, rf"{re.escape(nome.lower())}.* tourist tax") and not us_ha(sugg, rf"{re.escape(nome.lower())}.* hotel tax") else "hotel tax"


def fl_faq(c, nome_luogo, sugg, zone=None, citta=False, nome_q=None):
    zz = [z for z in fl_zone(c) if zone is None or z[0] in zone]
    nome_q = nome_q or fl_nome(c)
    parola = us_tassa_parola(sugg, nome_q.replace(" County", ""))
    faq = [((f"What is the {nome_q} {parola} rate?" if us_ha(sugg, r"\brate\b") else f"How much is the {nome_q} {parola}?"), fl_risposta(c, nome_luogo, zone))]
    if us_ha(sugg + us_sugg("florida hotel tax"), r"taxes and fees|breakdown|tourist development tax|occupancy tax|lodging tax|room tax|tourism tax"):
        faq.append((f"What taxes are on a hotel bill in {nome_q}?",
                    "Three kinds, all as a percentage of the room price: the 6% Florida state sales tax, the county discretionary sales surtax "
                    f"({us_pct(fl_surtax(c))} in {fl_nome(c)} in {US_FL['dss_anno']}) and the local option transient rental tax, which according to form "
                    "DR-15TDT includes the tourist development tax, convention development tax, tourist impact tax and municipal resort tax: " + ("; ".join(f"{us_pct(a)} ({n})" for _, n, a in zz) if any(n for _, n, _ in zz) else f"{us_pct(zz[0][2])} in {fl_nome(c)}") + ". "
                    "The Department of Revenue's form says the local tax is in addition to the 6% state sales tax and any applicable discretionary sales surtax."))
    if us_ha(sugg, r"resort tax"):
        faq.append(("What is the Miami Beach resort tax?",
                    "A municipal resort tax that, according to the Florida Department of Revenue, only three municipalities in Miami-Dade County (Bal Harbour, "
                    "Miami Beach and Surfside) are eligible to impose: up to 4% on transient rental transactions and up to 2% on food and beverages consumed in "
                    "restaurants and bars. The Department's form DR-15TDT gives 7% as the local option transient rental tax rate for Miami Beach."))
    if us_ha(sugg, r"login|payment|pay |online|form\b|registration|application|filing|return|collector|certificate"):
        chi = c["riscossa_da"]
        faq.append((f"Who collects the {fl_nome(c)} tourist tax?",
                    (f"{fl_nome(c)} collects its local option transient rental tax itself: hosts report and pay it directly to the county, while the state sales "
                     f"tax and the surtax always go to the Florida Department of Revenue (form DR-15TDT). The Department says to contact the county to verify its rate."
                     if chi == "County" else
                     f"The Florida Department of Revenue: in {fl_nome(c)} the local option transient rental tax is filed and paid together with the 6% state sales "
                     "tax and the surtax (form DR-15TDT).") if chi != "N/A" else
                    f"Form DR-15TDT lists no local option transient rental tax for {fl_nome(c)}; the state sales tax and the surtax go to the Florida Department of Revenue."))
    faq.append((f"How do I calculate the hotel tax in {nome_q}?",
                f"Multiply the room price per night by the number of nights and by the total rate. For example, {us_usd(US_PREZZO)} a night for 3 nights at "
                f"{us_pct(fl_tot(c, zz[0][2]))} is {us_usd(US_PREZZO * 3 * fl_tot(c, zz[0][2]) / 100)} in tax. The calculator above does it for your dates: "
                "the county surtax can change on 1 January."))
    if not citta and us_ha(us_sugg("florida tourist tax"), r"on rentals"):
        faq.append((f"Does the {fl_nome(c)} tourist tax apply to vacation rentals?",
                    "Yes if the rental is for six months or less: form DR-15TDT says the local option tax applies to the rental or lease of living, sleeping, or "
                    "housekeeping accommodations for a term of six months or less, and the Department lists beach houses, condominiums and vacation houses among "
                    "the short-term rentals that must register to collect sales tax."))
    return faq[:5]


def tx_faq(r, L, sugg):
    tot = us_tot_pct(L["zone"][0])
    faq = [((f"What is the {r['nome']} hotel tax rate?" if us_ha(sugg, r"\brate\b") else f"How much is the hotel tax in {r['nome']}?"), tx_risposta(r, L))]
    faq.append((f"What makes up the hotel tax in {r['nome']}?",
                f"The 6% Texas state hotel occupancy tax plus the local taxes: "
                + "; ".join(f"{c['label']} {us_pct(c['pct'])}" for c in L["zone"][0]["comp"] if c["on"] and not c["label"].startswith("Texas"))
                + ". The Comptroller collects the state tax and cities and counties collect their own; according to the Comptroller, local hotel taxes are "
                "generally up to 7% and venue taxes up to 2% (Dallas County up to 3%)."))
    if us_ha(sugg, r"occupancy tax"):
        faq.append((f"Is the {r['nome']} hotel occupancy tax the same as the hotel tax?",
                    f"Yes: hotel occupancy tax is the official name of the hotel tax in Texas, for the state and for cities. In {r['nome']} the state and local hotel "
                    f"taxes add up to {us_pct(tot)} of the room price."))
    faq.append(("Who is exempt from hotel tax in Texas?",
                "According to the Comptroller, among others: the U.S. government and its employees traveling on official business, foreign diplomats with a "
                "tax exemption card, and permanent residents who occupy a room for at least 30 consecutive days. A guest who stays 30 days or more and tells "
                "the hotel in writing beforehand is exempt from the day of the notice; without notice, the tax is due on the first 30 days."))
    return faq[:5]


def tx_faq_contea(k, L, sugg):
    tot = us_tot_pct(L["zone"][0])
    faq = [((f"What is the {k['nome']} County hotel tax rate?" if us_ha(sugg, r"\brate\b") else f"How much is the {k['nome']} County hotel tax?"),
            tx_risposta_contea(k))]
    if us_ha(sugg, r"form|report"):
        faq.append((f"Who collects the {k['nome']} County hotel occupancy tax?",
                    "The county: the Comptroller collects only the 6% state hotel tax, while cities and counties are responsible for collecting their own local hotel taxes."))
    faq.append(("Who is exempt from hotel tax in Texas?",
                "According to the Comptroller, among others: the U.S. government and its employees traveling on official business, foreign diplomats with a "
                "tax exemption card, and permanent residents who occupy a room for at least 30 consecutive days. A guest who stays 30 days or more and tells "
                "the hotel in writing beforehand is exempt from the day of the notice; without notice, the tax is due on the first 30 days."))
    faq.append((f"How do I calculate the hotel tax in {k['nome']} County?",
                f"Multiply the room price per night by the nights and by the total rate: {us_usd(US_PREZZO)} a night for 3 nights at {us_pct(tot)} is "
                f"{us_usd(US_PREZZO * 3 * tot / 100)}. The state tax applies from $15 a night, local taxes from $2 a night."))
    return faq[:5]


# ---- elenco delle pagine
def us_pagine():
    """Luoghi con pagina: [(tipo, chiave, luogo, nome visibile, suggerimenti, extra)]."""
    out = []
    for p in US["pagine"]["fl_contea"]:
        c = US_FLC["miami-dade" if p["nome"] == "miami-dade" else slugify(p["nome"])]
        out.append(("fl_contea", c["id"], fl_luogo(c), f"{fl_nome(c)}, Florida", p["suggerimenti"], {"c": c}))
    for p in US["pagine"]["fl_citta"]:
        c = US_FLC[slugify(p["contee"][0])]
        nome = p["nome"].title().replace("St. ", "St. ")
        zone = None
        zz = [z[0] for z in fl_zone(c)]
        if c["id"] == "miami-dade":
            zone = ["miami-beach"] if nome == "Miami Beach" else ["resto"]
        L = fl_luogo(c, nome=nome, pagina=f"{US_FLS}{slugify(nome)}/", zone=zone)
        out.append(("fl_citta", slugify(nome), L, f"{nome} ({fl_nome(c)}, Florida)", p["suggerimenti"], {"c": c, "zone": zone, "nome": nome, "zz": zz}))
    for p in US["pagine"]["tx_citta"]:
        r = US_TXC[p["nome"]]
        out.append(("tx_citta", slugify(r["nome"]), tx_luogo(r), f"{r['nome']}, Texas", p["suggerimenti"], {"r": r}))
    for p in US["pagine"]["tx_contea"]:
        k = US_TXK[p["nome"]]
        out.append(("tx_contea", slugify(k["nome"]), tx_luogo_contea(k), f"{k['nome']} County, Texas", p["suggerimenti"], {"k": k}))
    return out


def us_titolo(tipo, L, extra):
    z0 = L["zone"][0]
    if tipo == "fl_contea":
        c = extra["c"]
        zz = fl_zone(c)
        nome = fl_nome(c).replace("Miami-Dade County", "Miami-Dade")
        if len(zz) == 1:
            t = f"{nome} tourist tax {ANNO}: {us_pct(zz[0][2])} ({us_pct(fl_tot(c, zz[0][2]))} hotel tax in total)"
            if zz[0][2] == 0:
                t = f"{nome} tourist tax {ANNO}: none ({us_pct(fl_tot(c, 0))} hotel tax in total)"
        else:
            aa = sorted({a for _, _, a in zz})
            tt = sorted({fl_tot(c, a) for _, _, a in zz})
            t = f"{nome} tourist tax {ANNO}: {us_pct(aa[0])}–{us_pct(aa[-1])} by area ({us_pct(tt[0])}–{us_pct(tt[-1])} in total)"
        return t
    if tipo == "fl_citta":
        c = extra["c"]
        tt = sorted({us_tot_pct(Z) for Z in L["zone"]})
        cifra = us_pct(tt[0]) if len(tt) == 1 else f"{us_pct(tt[-1])} in listed ZIP codes"
        t = f"{extra['nome']} hotel tax {ANNO}: {cifra} ({fl_nome(c)}, Florida)"
        return t if len(t) <= 70 else f"{extra['nome']} hotel tax {ANNO}: {cifra}"
    if tipo == "tx_citta":
        r = extra["r"]
        tot = us_tot_pct(z0)
        if r["nome"] == "Houston":
            return f"Houston hotel tax: {us_pct(tot)} (state, city, county, sports authority)"
        base = US_TX["stato"] + tx_tot_locale(r)
        if tx_contee_venue(r):
            t = f"{r['nome']} hotel tax: {us_pct(base)}–{us_pct(tot)} (state, city, county venue tax)"
            return t if len(t) <= 70 else f"{r['nome']} hotel tax: {us_pct(base)}–{us_pct(tot)}"
        t = f"{r['nome']} hotel tax: {us_pct(tot)} ({us_pct(US_TX['stato'])} state + {us_pct(tx_tot_locale(r))} city), calculator"
        return t if len(t) <= 70 else f"{r['nome']} hotel tax: {us_pct(tot)} (6% state + {us_pct(tx_tot_locale(r))} city)"
    k = extra["k"]
    if k["nome"] == "Harris":
        return "Harris County hotel tax (Texas): 2% county + 2% sports authority (10%)"
    parti = " + ".join(x for x in ((f"{us_pct(tx_val(k['r351']))} county" if tx_val(k["r351"]) else ""),
                                   (f"{us_pct(tx_val(k['r334']))} venue tax" if tx_val(k["r334"]) else "")) if x)
    return f"{k['nome']} County hotel tax (Texas): {parti}, reported"


def us_note_fl(c, zona_note=True):
    li = []
    if c.get("nota") and zona_note:
        li.append(f"Areas: form DR-15TDT, note ({c['nota']}): “{US_FL['note_tdt'][c['nota']]}”")
    chi = c["riscossa_da"]
    if chi == "County":
        li.append(f"Who collects it: {fl_nome(c)} collects its local option transient rental tax itself; form DR-15TDT: “{US_FR['fl_tdt']['contea']}” "
                  f"and “{US_FR['fl_tdt']['verifica']}”")
    elif chi == "DOR":
        li.append(f"Who collects it: in {fl_nome(c)} the local option transient rental tax is reported and paid to the Florida Department of Revenue, "
                  "with the 6% state sales tax and the surtax (form DR-15TDT).")
    li.append(f"What the local rate covers: form DR-15TDT says “{US_FR['fl_tdt']['include']}” The rate shown is the total for the county.")
    li.append(f"Cities and changes: form DR-15TDT says “{US_FR['fl_tdt']['ambito']}” and “{US_FR['fl_tdt']['non_tutte']}”")
    li.append("The surtax applies to transient rentals, and its $5,000 cap does not apply to them (Florida Department of Revenue, Discretionary Sales Surtax page).")
    fine = fl_fine_surtax(c)
    if fine:
        li.append(f"Surtax change: according to the {US_FL['dss_anno']} form, {fine} of the {fl_nome(c)} surtax ends on {data_lunga(US_FINE_DSS)}. "
                  "The Department publishes the next year's form every November; we update this page when it does.")
    return "<ul>" + "".join(f"<li>{escape(x)}</li>" for x in li) + "</ul>"


def us_note_tx(r=None, contea=False):
    li = [f"Price thresholds: {US_FR['tx_faq']['soglia_stato']} {US_FR['tx_faq']['soglia_locale']}",
          f"Rentals: {US_FR['tx_faq']['ambito']} {US_FR['tx_hot']['piattaforme']}",
          f"Who collects it: {US_FR['tx_faq']['chi']}",
          f"Long stays: {US_FR['tx_faq']['trenta']}",
          f"Other local taxes: {US_FR['tx_hot']['locali']} {US_TX['frasi']['mancanti']}",
          f"About the data: the city and county rates come from the Comptroller's Local Hotel Occupancy Tax Reporting for fiscal year {US_TX['anno_fiscale']} "
          f"(data updated {US_TX_AGG}). {US_TX['frasi']['non_verificati']}"]
    return "<ul>" + "".join(f"<li>{escape(x)}</li>" for x in li) + "</ul>"


def us_griglia(rel, voci, salta=""):
    return '<div class="griglia">' + "".join(f'<a href="{rel}{L["pagina"]}">{escape(L["nome"])}<small>{escape(sub)}</small></a>'
                                             for L, sub in voci if L["pagina"] != salta) + "</div>"


def us_voci_stato(stato):
    vv = []
    for tipo, _, L, _, _, extra in sorted(us_pagine(), key=lambda v: (v[0].endswith("contea"), v[2]["nome"])):
        if (stato == "fl") != tipo.startswith("fl"):
            continue
        tt = sorted({us_tot_pct(Z) for Z in L["zone"]})
        vv.append((L, (us_pct(tt[0]) if len(tt) == 1 else f"{us_pct(tt[0])}–{us_pct(tt[-1])}") + " hotel tax"))
    return vv


def us_callout(rel):
    return (f'<section class="card callout us-box" aria-label="Hotel tax in the USA"><span class="ic">{ico("percent")}</span>'
            f'<p><strong>Travelling to the USA?</strong> Hotel tax in Florida (all 67 counties) and Texas (state and city rates), with a calculator. '
            f'<a href="{rel}{US_HUB}">Hotel tax in the USA</a> · <a href="{rel}{US_FLS}">Florida</a> · <a href="{rel}{US_TXS}">Texas</a></p></section>')


def pagina_us_luogo(tipo, chiave_, L, nome_luogo, sugg, extra):
    rel = "../../../"
    pag = L["pagina"]
    titolo = us_titolo(tipo, L, extra)
    if tipo.startswith("fl"):
        c = extra["c"]
        risp = fl_risposta(c, nome_luogo, extra.get("zone"))
        faq = fl_faq(c, nome_luogo, sugg, extra.get("zone"), citta=tipo == "fl_citta", nome_q=extra.get("nome"))
        fonti = ["fl_tdt", "fl_dss"]
        note = us_note_fl(c, zona_note=extra.get("zone") is None)
        elenco = ["fl_tdt", "fl_dss", "fl_local", "fl_sales", "fl_disc"] + (["census"] if tipo == "fl_citta" else [])
        stato, stato_slug, stato_voci = "Florida", US_FLS, us_voci_stato("fl")
        zona_box = ""
        if len(L["zone"]) > 1:
            zona_box = (f'<section class="card callout" aria-label="Areas"><span class="ic">{ico("pin")}</span><p><strong>The rate depends on the area.</strong> '
                        f'{escape(US_FL["note_tdt"][c["nota"]])} (form DR-15TDT). Pick the area in the calculator; your booking shows the address and ZIP code.</p></section>')
        dove = ""
        if tipo == "fl_citta":
            ha_pag = any(L2["pagina"] == fl_slug(c) for t2, _, L2, _, _, _ in us_pagine() if t2 == "fl_contea")
            dove = (f"<p>{escape(extra['nome'])} is in {escape(fl_nome(c))} (2020 Census place-by-county file). The rates are the county's: the Department of "
                    "Revenue's form lists them by county, with the exceptions in its notes."
                    + (f' <a href="{rel}{fl_slug(c)}">{escape(fl_nome(c))} tourist tax</a>' if ha_pag else "") + "</p>")
    else:
        if tipo == "tx_citta":
            r = extra["r"]
            risp = tx_risposta(r, L)
            faq = tx_faq(r, L, sugg)
            kk = tx_contee_nota(r) if r["nome"] != "Houston" else []
            cn = r.get("contee", [])
            dove = (f"<p>{escape(r['nome'])} is in " + (f"{cn[0]} County" if len(cn) == 1 else ", ".join(cn[:-1]) + f" and {cn[-1]} counties")
                    + " (2020 Census place-by-county file)."
                    + (" " + " ".join(f"{escape(k['nome'])} County reported " + " and ".join(x for x in (
                        (f"a county hotel occupancy tax of {us_pct(tx_val(k['r351']))}" if tx_val(k['r351']) else ""),
                        (f"a venue tax of {us_pct(tx_val(k['r334']))}" if tx_val(k['r334']) else "")) if x) + "." for k in kk)
                       + " The data does not say whether a county hotel occupancy tax applies inside the city, so it is not in the calculator." if kk else "")
                    + "</p>") if r.get("contee") else ""
            fonti = ["tx_faq", "tx_dati"] if r["nome"] == "Houston" else ["tx_dati", "tx_hot"]
        else:
            k = extra["k"]
            risp = tx_risposta_contea(k)
            faq = tx_faq_contea(k, L, sugg)
            citta = sorted((x for x in US_TXR if x["tipo"] != "county" and k["nome"] in x.get("contee", []) and tx_tot_locale(x) > 0), key=lambda x: x["nome"])
            dove = ""
            if citta:
                if k["nome"] == "Harris":
                    agg, spiega = 4.0, ("“With county taxes” adds, for Houston, the 2% Harris County tax and the 2% Harris County - Houston Sports Authority "
                                        "tax of the Comptroller's example; the example covers Houston only, so the column is empty for the other cities.")
                elif tx_val(k["r334"]):
                    agg, spiega = tx_val(k["r334"]), (f"“With county taxes” adds the {us_pct(tx_val(k['r334']))} county venue tax, as on the city pages; "
                                                      "not the county hotel occupancy tax, because the data does not say whether it applies inside cities.")
                else:
                    agg, spiega = 0.0, ("“With county taxes” equals city + state: the data does not say whether the county hotel occupancy tax applies "
                                        "inside cities, so the city pages do not count it.")
                righe = "".join(f"<tr><td>{escape(x['nome'])}</td><td>{us_pct(tx_val(x['r351']))}</td><td>{us_pct(tx_val(x['r334'])) if tx_val(x['r334']) else '–'}</td>"
                                f"<td>{us_pct(US_TX['stato'] + tx_tot_locale(x))}</td><td>{'–' if k['nome'] == 'Harris' and x['nome'] != 'Houston' else us_pct(US_TX['stato'] + tx_tot_locale(x) + agg)}</td></tr>" for x in citta)
                dove = (f"<h2>Cities in {escape(k['nome'])} County with their own hotel tax</h2><p>Rates reported by each city for fiscal year {US_TX['anno_fiscale']}; "
                        f"cities from the 2020 Census place-by-county file. {escape(spiega)}</p>"
                        f'<div class="tab sintesi us-tab"><table><thead><tr><th>City</th><th>City tax</th><th>Venue tax</th><th>City + state</th><th>With county taxes</th></tr></thead><tbody>{righe}</tbody></table></div>')
            fonti = ["tx_dati", "tx_hot"] + (["tx_faq"] if k["nome"] == "Harris" else [])
        note = us_note_tx()
        elenco = ["tx_hot", "tx_faq", "tx_report", "tx_dati", "tx_storico", "census"]
        stato, stato_slug, stato_voci = "Texas", US_TXS, us_voci_stato("tx")
        zona_box = ""
    faq_html, ld = us_faq_html(faq)
    tabelle = "".join((f"<h3>{escape(Z['nome'])}</h3>" if len(L["zone"]) > 1 else "") + us_tabella(L, i) for i, Z in enumerate(L["zone"]))
    corpo = f"""<section class="hero">{h1_diviso(titolo)}
<p class="risposta">{escape(risp)}</p>
{us_fonte(fonti)}</section>
{zona_box}
{us_calcolatore([L], rel)}
<details class="formula"><summary>{ico("calc")}Formula used</summary><p>{escape(US_FORMULA)}</p></details>
<p class="esempio">{us_esempio(L)}</p>
{AVVISO_US}
{AD}
<h2>Taxes on a hotel room in {escape(nome_luogo.split(" (")[0])}</h2>
{tabelle}
{dove}
<h2>Good to know</h2>
{note}
<h2>Questions</h2>
{faq_html}
<h2>Official sources</h2>
{us_fonti_elenco(elenco)}
<p class="small">Spotted a change? <a href="{rel}contact/?ref=usa-{escape(chiave_)}">Tell us</a>.</p>
<h2>Other places in {stato}</h2>
{us_griglia(rel, stato_voci, salta=pag)}
<p><a href="{rel}{stato_slug}">{stato} hotel tax</a> · <a href="{rel}{US_HUB}">Hotel tax in the USA</a> · <a href="{rel}">Tourist tax calculator</a></p>"""
    desc = re.split(r"(?<!\bSt)(?<=[a-z0-9%)])\. ", risp)[0]
    desc = desc if len(desc) <= 300 else desc[:297] + "..."
    br = [("USA", US_HUB), (stato, stato_slug), (nome_luogo.split(" (")[0].replace(", Florida", "").replace(", Texas", ""), pag)]
    pagina(pag, titolo, desc, corpo, briciole=br, extra_js=US_JS + US_APP_JS, jsonld_extra=ld)


def fl_stat():
    cc = US_FL["contee"]
    con = [c for c in cc if c["aliquota"] > 0]
    aa = sorted({a for c in cc for _, _, a in fl_zone(c) if a > 0})
    tt = sorted({fl_tot(c, a) for c in cc for _, _, a in fl_zone(c)})
    ss = sorted({fl_surtax(c) for c in cc})
    return con, aa, tt, ss


def fl_risposta_stato():
    con, aa, tt, ss = fl_stat()
    return (f"Florida charges its 6% state sales tax on hotel rooms and other rentals of six months or less, plus the county discretionary sales surtax "
            f"({us_pct(ss[0])} to {us_pct(ss[-1])} in {US_FL['dss_anno']}) and, in {len(con)} of the 67 counties, a local option transient rental tax "
            f"(which includes the tourist development tax) of {us_pct(aa[0])} to {us_pct(aa[-1])}: {us_pct(tt[0])} to {us_pct(tt[-1])} of the room price in total, "
            f"{FL_FONTE_FRASE}.")


def fl_faq_stato():
    con, aa, tt, ss = fl_stat()
    zero = [fl_nome(c) for c in US_FL["contee"] if c["aliquota"] == 0]
    orl = US_FLC["orange"]
    return [
        ("Does Florida have a tourist tax?",
         f"Yes, county by county: {len(con)} of the 67 counties charge a local option transient rental tax, often called the tourist development tax, of "
         f"{us_pct(aa[0])} to {us_pct(aa[-1])} on rentals of six months or less. " + ", ".join(zero[:-1]) + f" and {zero[-1]} have none (0%) on form DR-15TDT. "
         "It comes on top of the 6% state sales tax and the county surtax."),
        ("What is the Florida hotel tax rate?",
         f"{us_pct(tt[0])} to {us_pct(tt[-1])} of the room price in {US_FL['dss_anno']}, depending on the county: 6% state sales tax, the county surtax "
         f"({us_pct(ss[0])} to {us_pct(ss[-1])}) and the tourist development tax. In Orange County (Orlando) it is {us_pct(fl_tot(orl, orl['aliquota']))}."),
        ("Do vacation rentals pay the Florida tourist tax?",
         "Yes for rentals of six months or less: the local option tax applies to the rental or lease of living, sleeping, or housekeeping accommodations for "
         "a term of six months or less (form DR-15TDT), and the Department of Revenue lists beach houses, condominiums, timeshare resorts and vacation "
         "houses among the short-term rentals that must register to collect sales tax."),
        ("What is the tourist development tax in each Florida county?",
         f"The table on this page lists all 67 counties from form DR-15TDT (revision {US_F['fl_tdt']['revisione']}): {us_pct(aa[0])} to {us_pct(aa[-1])}, "
         "with special rates by area in Bay, Miami-Dade, Nassau, Okaloosa and Walton counties. In counties marked “County” the county collects it and the "
         "Department advises contacting the county to verify the rate."),
        ("How do I calculate Florida hotel tax?",
         f"Add up the three rates for the county and apply them to the room price: in Orange County {us_usd(US_PREZZO)} a night for 3 nights at "
         f"{us_pct(fl_tot(orl, orl['aliquota']))} is {us_usd(US_PREZZO * 3 * fl_tot(orl, orl['aliquota']) / 100)} in tax. The calculator does it for any county and date."),
    ]


def pagina_us_florida():
    rel = "../../"
    pagine_fl = {L["pagina"] for t, _, L, _, _, _ in us_pagine() if t == "fl_contea"}
    righe = []
    for c in sorted(US_FL["contee"], key=lambda c: c["nome"]):
        nome = fl_nome(c)
        link = f'<a href="{rel}{fl_slug(c)}">{escape(nome)}</a>' if fl_slug(c) in pagine_fl else escape(nome)
        zz = fl_zone(c)
        tdt = " / ".join(us_pct(a) for _, _, a in zz) + (f" <span class=\"small\">(note {c['nota']})</span>" if c.get("nota") else "")
        tot = " / ".join(us_pct(fl_tot(c, a)) for _, _, a in zz)
        righe.append(f"<tr><td>{link}</td><td>{tdt}</td><td>{us_pct(fl_surtax(c))}</td><td>{tot}</td><td>{escape(c['riscossa_da'])}</td></tr>")
    note = "".join(f"<li>({k}) {escape(v)}</li>" for k, v in US_FL["note_tdt"].items())
    luoghi = [fl_luogo(c) for c in sorted(US_FL["contee"], key=lambda c: c["nome"])]
    fini = [f"{fl_nome(c)}: {fl_fine_surtax(c)}" for c in sorted(US_FL["contee"], key=lambda c: c["nome"]) if fl_fine_surtax(c)]
    faq_html, ld = us_faq_html(fl_faq_stato())
    citta = [(L, sub) for L, sub in us_voci_stato("fl") if not L["pagina"].endswith("-county/")]
    corpo = f"""<section class="hero">{h1_diviso(f"Florida hotel tax {ANNO}: every county, with a calculator")}
<p class="risposta">{escape(fl_risposta_stato())}</p>
{us_fonte(["fl_tdt", "fl_dss"])}</section>
<h2>Calculator</h2>
{us_calcolatore(luoghi, rel, con_scelta=True)}
<details class="formula"><summary>{ico("calc")}Formula used</summary><p>{escape(US_FORMULA)}</p></details>
{AVVISO_US}
{AD}
<h2>Cities</h2>
{us_griglia(rel, citta)}
<h2>Hotel tax by county ({US_FL['dss_anno']})</h2>
<p>Tourist tax = local option transient rental tax from form DR-15TDT ({escape(US_FR['fl_tdt']['include'][0].lower() + US_FR['fl_tdt']['include'][1:])}); surtax = discretionary sales surtax from form DR-15DSS; total = both plus the 6% state sales tax. “Collected by”: County = the county collects its tourist tax itself; DOR = the Florida Department of Revenue collects it.</p>
<div class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="Search a county" data-filtro="fl-contee" aria-label="Search counties"></div>
<div class="tab sintesi us-tab"><table><thead><tr><th>County</th><th>Tourist tax</th><th>Surtax</th><th>Total</th><th>Collected by</th></tr></thead><tbody id="fl-contee">{"".join(righe)}</tbody></table></div>
<p class="small">Notes of form DR-15TDT:</p><ul class="small">{note}</ul>
{us_fonte(["fl_tdt", "fl_dss"])}
<h2>How the Florida hotel tax adds up</h2>
<ul><li>{escape(US_FR['fl_tdt']['ambito'])} {escape(US_FR['fl_tdt']['in_aggiunta'])}</li>
<li>The discretionary sales surtax applies when the rental of living or sleeping accommodations (transient rentals) occurs in a county with a surtax; the $5,000 cap on the surtax does not apply to transient rentals (Discretionary Sales Surtax page).</li>
<li>{escape(US_FR['fl_tdt']['dor'])} {escape(US_FR['fl_tdt']['contea'])}</li>
<li>Cities: in Miami-Dade County the form gives 7% for Miami Beach and 4% for Surfside and Bal Harbour; {escape(US_FR['fl_local']['resort'][0].lower() + US_FR['fl_local']['resort'][1:])} (municipal resort tax, Local Option Taxes page).</li>
<li>{escape(US_FR['fl_tdt']['non_tutte'])} {escape(US_FR['fl_tdt']['verifica'])}</li></ul>
<h2>Surtax changes</h2>
<p>According to the {US_FL['dss_anno']} form, these surtaxes end on {data_lunga(US_FINE_DSS)}: {escape("; ".join(fini) or "none")}. The Department publishes the form for the next year every November; we update the rates when it does.</p>
<h2>Questions</h2>
{faq_html}
<h2>Official sources</h2>
{us_fonti_elenco(["fl_tdt", "fl_dss", "fl_local", "fl_sales", "fl_disc"])}
<p class="small">Spotted a change? <a href="{rel}contact/?ref=usa-florida">Tell us</a>.</p>
<p><a href="{rel}{US_HUB}">Hotel tax in the USA</a> · <a href="{rel}{US_TXS}">Texas hotel tax</a> · <a href="{rel}">Tourist tax calculator</a></p>"""
    pagina(US_FLS, f"Florida hotel tax {ANNO} by county: 6% state + surtax + tourist tax",
           re.split(r"(?<=[a-z%]): ", fl_risposta_stato())[0] + ". All 67 counties from the Department of Revenue, with a calculator.",
           corpo, briciole=[("USA", US_HUB), ("Florida", US_FLS)], extra_js=US_JS + US_APP_JS, jsonld_extra=ld)


def tx_stat():
    cc = [r for r in US_TXR if r["tipo"] != "county" and tx_tot_locale(r) > 0]
    kk = [r for r in US_TXR if r["tipo"] == "county" and tx_tot_locale(r) > 0]
    from collections import Counter
    moda = Counter(tx_val(r["r351"]) for r in cc if tx_val(r["r351"])).most_common(1)[0][0]
    return cc, kk, moda


def tx_risposta_stato():
    cc, kk, moda = tx_stat()
    return (f"Texas charges a 6% state hotel occupancy tax on rooms of $15 or more a night, and cities, some counties and venue projects add their own: "
            f"{len(cc)} cities and {len(kk)} counties reported a local rate to the Texas Comptroller for fiscal year {US_TX['anno_fiscale']}, most often "
            f"{us_pct(moda)} for the city (data updated {US_TX_AGG}, checked on {data_lunga(US_F['tx_dati']['controllato_il'])}).")


def tx_faq_stato():
    cc, kk, moda = tx_stat()
    hou = tx_luogo(US_TXC["houston"])
    return [
        ("What is the Texas hotel tax rate?",
         f"6% of the room price for the state, plus local taxes: cities generally up to 7% and venue projects up to 2% (Dallas County up to 3%), according to the "
         f"Comptroller. In the Comptroller's example for Houston the total is {us_pct(us_tot_pct(hou['zone'][0]))}: 6% state, 7% city, 2% Harris County and 2% "
         "Harris County - Houston Sports Authority."),
        ("What is the Texas state hotel occupancy tax?",
         "A 6% tax on the cost of a room, collected by the Texas Comptroller of Public Accounts from hotel owners, operators or managers, who collect it from "
         "guests. For the state tax it applies to sleeping accommodations of $15 or more per day; local hotel taxes apply from $2 per day."),
        ("Who is exempt from hotel tax in Texas?",
         "According to the Comptroller, among others: the U.S. government and its employees traveling on official business, foreign diplomats with a tax "
         "exemption card, certain Texas state officials with a hotel tax exemption card, and permanent residents who occupy a room for at least 30 consecutive "
         "days. Religious, charitable and educational organizations with a letter of exemption are exempt from the 6% state tax only."),
        ("Do I pay Texas hotel tax on a stay of 30 days or more?",
         "Not after 30 days: a guest who stays 30 or more days and notifies the hotel in writing beforehand is exempt from the day of notification; a guest who "
         "does not notify the hotel pays the tax for the first 30 days and is exempt thereafter (Comptroller FAQs)."),
        ("What taxes and fees are on a Texas hotel bill?",
         "The taxes are the 6% state hotel occupancy tax and the local hotel taxes of the city, the county and venue projects where they apply, all as a "
         "percentage of the room price. The official data lists taxes only, not hotel fees."),
    ]


def pagina_us_texas():
    rel = "../../"
    cc, kk, moda = tx_stat()
    pagine_tx = {L["pagina"] for t, _, L, _, _, _ in us_pagine() if t.startswith("tx")}
    righe = []
    for r in sorted(cc, key=lambda r: r["nome"]):
        nome = f'<a href="{rel}{tx_slug_citta(r)}">{escape(r["nome"])}</a>' if tx_slug_citta(r) in pagine_tx else escape(r["nome"])
        righe.append(f"<tr><td>{nome}</td><td>{us_pct(tx_val(r['r351']))}</td><td>{us_pct(tx_val(r['r334'])) if tx_val(r['r334']) else '–'}</td>"
                     f"<td>{us_pct(US_TX['stato'] + tx_tot_locale(r))}</td><td>{escape(', '.join(r.get('contee', [])) or '–')}</td></tr>")
    righe_k = []
    for k in sorted(kk, key=lambda r: r["nome"]):
        nome = f'<a href="{rel}{tx_slug_contea(k)}">{escape(k["nome"])} County</a>' if tx_slug_contea(k) in pagine_tx else escape(k["nome"] + " County")
        nota_k = (" <span class=\"small\">(reported in the dataset, not consistent with the Comptroller's example for Houston: 2% Harris County tax and "
                  "2% Harris County - Houston Sports Authority tax)</span>" if k["nome"] == "Harris" else "")
        righe_k.append(f"<tr><td>{nome}{nota_k}</td><td>{us_pct(tx_val(k['r351'])) if tx_val(k['r351']) else '–'}</td><td>{us_pct(tx_val(k['r334'])) if tx_val(k['r334']) else '–'}</td></tr>")
    luoghi = [L for t, _, L, _, _, _ in us_pagine() if t.startswith("tx")]
    faq_html, ld = us_faq_html(tx_faq_stato())
    corpo = f"""<section class="hero">{h1_diviso("Texas hotel occupancy tax: 6% state + local rates by city")}
<p class="risposta">{escape(tx_risposta_stato())}</p>
{us_fonte(["tx_hot", "tx_dati"])}</section>
<h2>Calculator</h2>
{us_calcolatore(luoghi, rel, con_scelta=True)}
<details class="formula"><summary>{ico("calc")}Formula used</summary><p>{escape(US_FORMULA)}</p></details>
{AVVISO_US}
{AD}
<h2>Cities and counties with a page</h2>
{us_griglia(rel, us_voci_stato("tx"))}
<h2>Hotel tax by city ({len(cc)} cities)</h2>
<p>City tax = municipal hotel occupancy tax (Tax Code chapter 351); venue tax = Local Government Code chapter 334; total = city taxes plus the 6% state tax, without county taxes. Rates as reported by each city for fiscal year {US_TX['anno_fiscale']}; counties from the 2020 Census place-by-county file.</p>
<div class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="Search a city" data-filtro="tx-citta" aria-label="Search cities"></div>
<div class="tab sintesi us-tab"><table><thead><tr><th>City</th><th>City tax</th><th>Venue tax</th><th>City + state</th><th>County</th></tr></thead><tbody id="tx-citta">{"".join(righe)}</tbody></table></div>
{us_fonte(["tx_dati"], "Official source")}
<h2>County hotel taxes ({len(kk)} counties)</h2>
<p>County hotel occupancy tax (Tax Code chapter 352) and venue tax, as reported for fiscal year {US_TX['anno_fiscale']}. The data does not say in which parts of a county each tax applies.</p>
<div class="tab sintesi us-tab"><table><thead><tr><th>County</th><th>County tax</th><th>Venue tax</th></tr></thead><tbody>{"".join(righe_k)}</tbody></table></div>
<h2>Good to know</h2>
{us_note_tx()}
<h2>Questions</h2>
{faq_html}
<h2>Official sources</h2>
{us_fonti_elenco(["tx_hot", "tx_faq", "tx_report", "tx_dati", "tx_storico", "census"])}
<p class="small">Spotted a change? <a href="{rel}contact/?ref=usa-texas">Tell us</a>.</p>
<p><a href="{rel}{US_HUB}">Hotel tax in the USA</a> · <a href="{rel}{US_FLS}">Florida hotel tax</a> · <a href="{rel}">Tourist tax calculator</a></p>"""
    pagina(US_TXS, "Texas hotel occupancy tax: 6% state + local rates by city",
           tx_risposta_stato().split(": ")[0] + f". Rates reported by {len(cc)} cities and {len(kk)} counties, with a calculator.",
           corpo, briciole=[("USA", US_HUB), ("Texas", US_TXS)], extra_js=US_JS + US_APP_JS, jsonld_extra=ld)


def us_risposta_hub():
    con, aa, tt, ss = fl_stat()
    cc, kk, moda = tx_stat()
    return (f"In Florida a hotel room pays {us_pct(tt[0])} to {us_pct(tt[-1])} of the price in tax, depending on the county (6% state sales tax, county "
            f"surtax and tourist development tax; Florida Department of Revenue, {US_FL['dss_anno']} forms); in Texas 6% state hotel occupancy tax plus city, "
            f"county and venue taxes ({len(cc)} cities reported a rate for fiscal year {US_TX['anno_fiscale']}; Texas Comptroller), checked on {US_CHECK}.")


def us_faq_hub():
    con, aa, tt, ss = fl_stat()
    hou = tx_luogo(US_TXC["houston"])
    orl = US_FLC["orange"]
    return [
        ("Is there tax on hotel rooms in the USA?",
         f"Yes in both states covered here so far. Florida: {us_pct(tt[0])} to {us_pct(tt[-1])} by county (Orange County, Orlando: "
         f"{us_pct(fl_tot(orl, orl['aliquota']))}). Texas: 6% state tax plus local taxes (Houston: {us_pct(us_tot_pct(hou['zone'][0]))}). "
         "Each state and city sets its own rates, so the total depends on where you stay."),
        ("What are hotel tax rates by state?",
         "This section covers Florida and Texas, from the official files of each state: the Florida Department of Revenue (forms DR-15TDT and DR-15DSS) and "
         "the Texas Comptroller of Public Accounts (state rate and the rates reported by cities and counties). Other states are not covered yet."),
        ("How do I calculate US hotel tax?",
         f"Add up the percentages that apply where you stay and multiply by the room price and the nights: {us_usd(US_PREZZO)} a night for 3 nights at "
         f"{us_pct(fl_tot(orl, orl['aliquota']))} is {us_usd(US_PREZZO * 3 * fl_tot(orl, orl['aliquota']) / 100)}. The calculator above does it for each county and city with a page."),
    ]


def pagina_us_hub():
    rel = "../"
    luoghi = [L for _, _, L, _, _, _ in us_pagine()]
    faq_html, ld = us_faq_html(us_faq_hub())
    con, aa, tt, ss = fl_stat()
    cc, kk, moda = tx_stat()
    corpo = f"""<section class="hero">{h1_diviso(f"Hotel tax in the USA: Florida {us_pct(tt[0])}–{us_pct(tt[-1])}, Texas 6% + local rates")}
<p class="risposta">{escape(us_risposta_hub())}</p>
{us_fonte(["fl_tdt", "fl_dss", "tx_hot", "tx_dati"])}</section>
<h2>Calculator</h2>
{us_calcolatore(luoghi, rel, con_scelta=True)}
<details class="formula"><summary>{ico("calc")}Formula used</summary><p>{escape(US_FORMULA)}</p></details>
{AVVISO_US}
{AD}
<h2>States</h2>
<div class="griglia"><a href="{rel}{US_FLS}">Florida<small>{us_pct(tt[0])}–{us_pct(tt[-1])} by county · all 67 counties</small></a><a href="{rel}{US_TXS}">Texas<small>6% state + local · {len(cc)} cities, {len(kk)} counties</small></a></div>
<h2>Florida: counties and cities</h2>
{us_griglia(rel, us_voci_stato("fl"))}
<h2>Texas: cities and counties</h2>
{us_griglia(rel, us_voci_stato("tx"))}
<h2>Questions</h2>
{faq_html}
<h2>Official sources</h2>
{us_fonti_elenco(["fl_tdt", "fl_dss", "fl_local", "tx_hot", "tx_faq", "tx_dati", "census"])}
<p class="small">Other states are not covered yet. Spotted a change? <a href="{rel}contact/?ref=usa">Tell us</a>.</p>
<p><a href="{rel}">Tourist tax calculator</a> · <a href="{rel}tourist-taxes-europe-2026/">Tourist taxes in Europe</a></p>"""
    pagina(US_HUB, f"Hotel tax in the USA: Florida {us_pct(tt[0])}–{us_pct(tt[-1])}, Texas 6% + local rates",
           f"Hotel tax in Florida ({us_pct(tt[0])}–{us_pct(tt[-1])} by county) and Texas (6% state + city and county rates), from the official state files, with a calculator.",
           corpo, briciole=[("USA", US_HUB)], extra_js=US_JS + US_APP_JS, jsonld_extra=ld)


def pagine_us():
    pagina_us_hub()
    pagina_us_florida()
    pagina_us_texas()
    for voce in us_pagine():
        pagina_us_luogo(*voce)


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
        "spain": "Spain has no national tourist tax. Catalonia (with a Barcelona city surcharge) and the Balearic Islands levy their own regional taxes, and Santiago de Compostela a municipal surcharge on the Galician tax, covered here.",
        "turkey": "Turkey's accommodation tax is national: a percentage of the accommodation price excluding VAT, the same everywhere.",
        "japan": "In Japan accommodation taxes are set by prefectures and cities. Some places have both (for example Hokkaido and Sapporo, Nagano and Hakuba). The Ministry of Internal Affairs and Communications publishes the official list of all of them.",
        "italy": "In Italy each city sets its own imposta (or contributo) di soggiorno per person per night, with its own maximum nights and age exemptions.",
        "belgium": ("In Belgium the Brussels-Capital Region and individual cities such as Ghent and Bruges set their own tourist tax. Brussels charges per room per night; Ghent and Bruges per "
                    "person aged 18 or over per night. Antwerp is not covered yet: the City's tax page does not open for automatic reading (HTTP 403). Bruges has "
                    "announced a charge for cruise and coach day visitors from 2027 (VRT News, March 2025), but we have not found an official regulation on brugge.be, "
                    "so we show no amount."),
    }.get(slug, "")
    tit, h1, risp = paese_seo(slug, dd)
    corpo = f"""<section class="hero">{h1_diviso(h1) if h1 else f"<h1>Tourist taxes in {escape(nome)} {ANNO}</h1>"}
{f'<p class="risposta">{escape(risp)}</p>' if risp else ""}
{"" if risp else f'<p class="lead">{escape(testo_extra) if testo_extra else f"Official tourist tax rates in {escape(nome)}, with a calculator for each destination."}</p>'}</section>
{f'<p class="small">What changes next: <a href="{rel}tourist-tax-changes-2027/">tourist tax changes in 2027</a>.</p>' if any(cambi_di(d["slug"]) for d in dd) else ""}
{(jt_callout(rel) + jp_callout(rel)) if slug == "japan" else ""}
{es_callout(rel) if slug == "spain" else ""}
<div class="tab"><table><thead><tr><th>Destination</th><th>Rate {ANNO}</th><th>Max taxable nights</th><th>Exempt</th></tr></thead><tbody>{righe}</tbody></table></div>
{AVVISO}
{AD}
<h2>Calculators</h2>
<div class="griglia">{''.join(f'<a href="{rel}{d["slug"]}/">{escape(d["name"])}<small>{escape(riassunto(d))}</small></a>' for d in dd)}</div>
<p><a href="{rel}tourist-taxes-europe-2026/">Tourist taxes in Europe {ANNO}</a> · <a href="{rel}">All destinations</a></p>"""
    pagina(f"country/{slug}/", tit or f"Tourist taxes in {nome} {ANNO}: rates and calculators",
           (re.split(r"(?<=\.) ", risp)[0] + " Official sources and calculators.") if risp else
           f"Official tourist tax rates in {nome} for {ANNO}, destination by destination, with calculators and official sources.",
           corpo, briciole=[(nome, f"country/{slug}/")])


def paese_seo(slug, dd):
    """Titolo, H1 e risposta diretta delle pagine paese che ricevono impressioni (Spagna, Grecia, Turchia), dai dati delle destinazioni."""
    by = {d["slug"]: d for d in dd}
    oggi = OGGI.isoformat()
    if slug == "spain":
        b, c, m = by["barcelona"], by["catalonia"], by["mallorca"]
        cd = prossimo_cambio(c)
        risp = (f"Spain has no national tourist tax; the best-known regional ones are in Catalonia and the Balearic Islands. In Barcelona you pay {fascia_breve(b, _vigenti(b, oggi)).replace('–', ' to ')} "
                f"per person per night, in the rest of Catalonia {fascia_breve(c, _vigenti(c, oggi)).replace('–', ' to ')}"
                + (f" ({fascia_breve(c, _vigenti(c, cd)).replace('–', ' to ')} from {data_lunga(cd)})" if cd else "")
                + f", and in Mallorca, Ibiza, Menorca and Formentera {fascia_breve(m, _vigenti(m, oggi)).replace('–', ' to ')} (the ecotasa, 75% lower from November to April). "
                f"Under-{b['esenti_sotto_eta']}s pay nothing in Catalonia and under-{m['esenti_sotto_eta']}s in the Balearic Islands."
                + (f" In Santiago de Compostela (Galicia) you pay {fascia_breve(by['santiago-de-compostela'], _vigenti(by['santiago-de-compostela'], oggi)).replace('–', ' to ')}"
                   " per person per night, for at most 5 nights." if "santiago-de-compostela" in by else ""))
        return (f"How much is the tourist tax in Spain? {ANNO} and {ANNO + 1} rates and calculator",
                f"Tourist tax in Spain {ANNO} and {ANNO + 1}: how much you pay in Barcelona, Catalonia and the Balearic Islands", risp)
    if slug == "greece":
        a = by["athens"]
        ora = _vigenti(a, oggi)
        alta = [t for t in ora if t.get("stagione") == "April-October"]
        bassa = [t for t in ora if t.get("stagione") == "November-March"]
        h4 = {t.get("stagione"): t["valore"] for t in ora if t["cat"] == "h4"}
        risp = (f"Greece charges one national fee, the climate crisis resilience fee, per room per night (not per person): {fascia_breve(a, alta)} from April to October "
                f"and {fascia_breve(a, bassa)} from November to March, depending on the type of accommodation (a 4-star hotel room: "
                f"{soldi_breve(h4['April-October'], 'EUR')} in high season, {soldi_breve(h4['November-March'], 'EUR')} in low season). "
                "It is the same in Athens, Santorini, Mykonos, Crete, Rhodes, Corfu and every other island.")
        return (f"Greece tourist tax {ANNO} calculator: {fascia_breve(a, ora)} per room per night (all islands)",
                f"Greece tourist tax {ANNO}: {fascia_breve(a, ora)} per room per night, the same on every island", risp)
    if slug == "turkey":
        t = by["turkey"]
        d = prossimo_cambio(t)
        risp = (f"Turkey's accommodation tax is national: {fascia_breve(t, _vigenti(t, oggi))} of the accommodation price excluding VAT"
                + (f" until {data_lunga((date.fromisoformat(d) - timedelta(days=1)).isoformat())}, then {fascia_breve(t, _vigenti(t, d))} from {data_lunga(d)} "
                   "(the rate in the law, unless a new Presidential decision changes it)" if d else "")
                + ". It is the same in Istanbul, Antalya, Bodrum and everywhere else; with board or all-inclusive, food and other services sold with the stay count too.")
        return (f"Tourist tax in Turkey {anni(t)}: {breve(t)} (calculator)",
                f"Tourist tax in Turkey {anni(t)}: {breve(t, lungo=True)}", risp)
    return "", "", ""


def n_regole():
    return len({d.get("gruppo") or d["slug"] for d in DEST})


def ultimo_controllo():
    date_ = [f["controllato_il"] for d in DEST for f in d["fonti"]] + [FR["controllato_il"]]
    return data_lunga(max(date_))


TIPI_HOME = [("users", "Per person per night", "Rome, Barcelona, Prague, Porto, Malta, most French towns"),
             ("door", "Per room per night", "Greece and Iceland"),
             ("percent", "% of the room price", "Amsterdam, Berlin, Vienna, Edinburgh, Turkey, Florida and Texas hotel tax"),
             ("bands", "Price bands", "Kyoto, Tokyo, Sapporo, Hakuba"),
             ("plane", "Once per trip", "Bali and Quintana Roo, Mexico (Cancún, Tulum, Playa del Carmen, Cozumel)")]


def home():
    gruppi = {}
    for d in DEST:
        gruppi.setdefault(d["country_slug"], []).append(d)
    griglia = "".join(f'<a href="{d["slug"]}/">{escape(d["name"])}<small>{escape(PAESI[d["country_slug"]])} · {escape(riassunto(d, seguito=False))}</small></a>' for d in DEST)
    griglia += "".join(f'<a href="{L["pagina"]}">{escape(L["nome"])}<small>United States · {escape(sub)}</small></a>'
                       for L, sub in us_voci_stato("fl") + us_voci_stato("tx") if not L["pagina"].endswith("-county/"))  # USA (7/11/2026): città con pagina
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
<div class="card callout cal-2027">{'<span class="ic">' + ico("calendar") + '</span>'}<p><strong>2027:</strong> <a href="tourist-tax-changes-2027/">{len(CAMBI['voci'])} tourist tax changes with an official date</a> – Turkey, Okinawa and 17 more Japanese places, Quintana Roo (Mexico), Cardiff, Catalonia, Barcelona, Tokyo, Vienna and Mexican cruise ports.</p></div>
{jt_callout('')}
{us_callout('')}
{jp_callout('')}
{AVVISO}
{AD}
<h2>What the calculator covers</h2>
<p class="lead">Official tourist tax rates on {len(DEST)} destination pages (based on {n_regole()} official rule sets, since Greece, Turkey and the Balearic Islands each have one rule for many places) and for {len(FR['comuni']):,} French towns, with a calculator that applies the real rules: rate by hotel category, percentage of the room price, price bands, seasons, maximum taxable nights and age exemptions. Every figure links to its official source.</p>
<ul class="tipi">{tipi}</ul>
<div class="sez-h"><h2>Find a destination</h2></div>
<div class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="Search a place" data-filtro="lista-dest" aria-label="Search destinations"></div>
<div class="griglia sez dest" id="lista-dest">{griglia}</div>
<p><a href="france/">All French towns</a> · <a href="{US_HUB}">Hotel tax in the USA (Florida, Texas)</a> · <a href="tourist-taxes-europe-2026/">Tourist taxes in Europe {ANNO}</a> · <a href="tourist-tax-changes-2027/">Changes in 2027</a> · <a href="how-tourist-taxes-work/">How tourist taxes work</a></p>
<h2>Countries</h2>
<div class="griglia">{''.join(f'<a href="{link_paese(s)}">{escape(PAESI[s])}<small>{plur(len(gruppi.get(s, [])) if s != "france" else len(FR_TOP["comuni"]), "destination page")}</small></a>' for s in PAESI)}<a href="{US_HUB}">United States<small>Florida and Texas hotel tax · {plur(len(us_pagine()) + 3, "page")}</small></a></div>
{box_affiliati()}
{blocco_dati('tutte', DEST)}"""
    pagina("", f"Tourist Tax Calculator {ANNO}: official rates per night for {len(DEST)} destination pages and 10,900 French towns",
           f"How much is the tourist tax? Official {ANNO} rates and a calculator for Mallorca, Barcelona, Greece, Turkey, Amsterdam, Malta, Porto, Tunisia, Paris and more, with sources and the 2027 changes.",
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
<p class="small">"Rate" shows the rates in force on the date this page was generated. Some places change rates during the year (for example Vienna on 1 July, Catalonia and Barcelona on 1 April, Turkey on 1 January): see each page and the <a href="{rel}tourist-tax-changes-2027/">tourist tax changes in 2027</a>.</p>
{AVVISO}
{AD}
<h2>Not covered yet</h2>
<p>We only publish a destination when we can read a complete official source. Not covered on the date we checked: Venice, Lisbon and the Algarve, Budapest, Croatia (Dubrovnik, Split), Cyprus, Glasgow, Antwerp. See <a href="{rel}about/">About and sources</a>.</p>"""
    pagina("tourist-taxes-europe-2026/", f"Tourist taxes in Europe {ANNO}: city by city table (official rates)",
           f"Tourist taxes in Europe {ANNO}: official rates for Paris, Barcelona, Mallorca, Greece, Amsterdam, Berlin, Vienna, Prague, Edinburgh, Cardiff, Rome, Florence, Milan, Malta, Porto, Iceland and Turkey.",
           corpo, briciole=[(f"Tourist taxes in Europe {ANNO}", "tourist-taxes-europe-2026/")])


def faq_2027():
    """3-4 domande della pagina 2027: risposte costruite dalle voci di dati/cambi_2027.json (uguali nel testo visibile e nel JSON-LD)."""
    vv = CAMBI["voci"]
    per = {v["slug"]: v for v in vv if v["slug"]}
    elenco = "; ".join(f"{v['luogo']} on {data_lunga(v['dal'])}" for v in vv)
    out = [("Which tourist taxes change in 2027?",
            f"{len(vv)} changes already have an official date: {elenco}. Each one is listed on this page with the new amount and the official source.")]
    if "cardiff" in per:
        v = per["cardiff"]
        out.append(("How much is the tourist tax in Cardiff from April 2027?",
                    f"From {data_lunga(v['dal'])} the Visitor Levy in Cardiff is {v['importo']}. {v['cosa']}"))
    if "tokyo" in per:
        v = per["tokyo"]
        out.append(("Is the Tokyo tourist tax changing in 2027?",
                    f"Yes. From {data_lunga(v['dal'])} Tokyo charges {v['importo']}, instead of {v['prima']}. {v['cosa']}"))
    if "vienna" in per:
        v = per["vienna"]
        out.append(("Does the Vienna tourist tax go up in 2027?",
                    f"Yes. From {data_lunga(v['dal'])} the Vienna Ortstaxe is {v['importo']}."))
    return out[:4]


def pagina_cambi_2027():
    rel = "../"
    vv = CAMBI["voci"]
    voci = []
    for v in vv:
        d = date.fromisoformat(v["dal"])
        f = v["fonte"]
        stato = "" if f["http"] == 200 else " (read by hand: the page does not open for automatic checks)"
        luogo = (f'<a href="{rel}{v["slug"]}/">{escape(v["luogo"])}</a>' if v["slug"] else escape(v["luogo"]))
        calc = (f'<a class="vc-calc" href="{rel}{v["slug"]}/">{ico("calc")}Calculator</a>' if v["slug"] else "")
        voci.append(f"""<li class="vc"><div class="vc-data"><span class="vc-g">{d.day}</span><span class="vc-m">{MESI_BREVI[d.month - 1]} {d.year}</span></div>
<div class="vc-c"><h3>{luogo}</h3>
<p class="vc-imp"><span class="vc-lab">New</span> {escape(v['importo'])}</p>
<p class="vc-prima"><span class="vc-lab">Before</span> {escape(v['prima'])}</p>
<p>{escape(v['cosa'])}{(' ' + escape(v['riserva'])) if v.get('riserva') else ''}</p>
<p class="fonte">Official source: <a href="{escape(f['url'])}" rel="noopener">{escape(f['titolo'])}</a> · checked on {data_lunga(f['controllato_il'])}{stato}</p>
{calc}</div></li>""")
    sintesi = "".join(f'<tr><td><strong>{data_breve(v["dal"])}</strong></td><td>{(f"<a href=\"{rel}{v["slug"]}/\">{escape(v["luogo"].split(" (")[0])}</a>") if v["slug"] else escape(v["luogo"].split(" (")[0])}</td>'
                      f'<td>{escape(v["importo_breve"])}</td></tr>' for v in vv)
    dopo = "".join(f'<li><strong>{data_lunga(x["dal"])}</strong> – <a href="{rel}{x["slug"]}/">{escape(x["luogo"])}</a>: {escape(x["cosa"])}</li>' for x in CAMBI["dopo"])
    faq = faq_2027()
    faq_html = "".join(f'<details class="faq"><summary>{escape(q)}</summary><p>{escape(a)}</p></details>' for q, a in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    primo, ultimo = vv[0]["dal"], vv[-1]["dal"]
    risp = (f"{len(vv)} tourist tax changes in 2027 already have an official date, from {data_lunga(primo)} to {data_lunga(ultimo)}: "
            "Turkey returns to 2%, Okinawa starts a new tax and the Quintana Roo Visitax (Mexico) follows the new UMA on 1 February, "
            "Wakkanai and Shirahama start new taxes on 1 March, "
            "Cardiff starts the Welsh visitor levy at £1.30, Catalonia, Barcelona and Tokyo change on 1 April, when Tomakomai, Yamagata, Fujiyoshida, Fujikawaguchiko, "
            "Unzen, Kagoshima and Ibusuki start new taxes and Nagasaki changes its bands, "
            "on 1 July Vienna goes to 8% and Mexico raises its fee for cruise passengers, and Kitahiroshima starts a new tax on 1 October.")
    corpo = f"""<section class="hero">{h1_diviso("Tourist tax changes in 2027: what changes, when and how much")}
<p class="risposta">{escape(risp)}</p>
<p class="small">We list a change only when an official act or tax authority page gives the date and the amount. List updated on {data_lunga(CAMBI['aggiornato_il'])}.</p></section>
<h2 class="sr">At a glance</h2>
<div class="tab sintesi"><table><thead><tr><th>From</th><th>Where</th><th>New amount</th></tr></thead><tbody>{sintesi}</tbody></table></div>
<div class="card callout cal-2027"><span class="ic">{ico("calendar")}</span><p><strong>Japan:</strong> <a href="{rel}{JT_27}">all {sum(1 for e in JT["enti"] if e["stato"] == "approvato")} new Japanese accommodation taxes in 2027, place by place</a>, with rates and start dates.</p></div>
<ol class="linea">{''.join(voci)}</ol>
{AVVISO}
{AD}
<h2>Later changes already decided</h2>
<ul>{dopo}</ul>
<h2>Not listed yet</h2>
<p>{escape(CAMBI['non_elencati'])}</p>
<h2>Questions</h2>
<div class="faq-box">{faq_html}</div>
<p><a href="{rel}">Tourist tax calculator</a> · <a href="{rel}tourist-taxes-europe-2026/">Tourist taxes in Europe {ANNO}</a> · <a href="{rel}contact/?ref=changes-2027">Spotted a change? Tell us</a></p>"""
    pagina("tourist-tax-changes-2027/", "Tourist tax changes 2027: new rates and start dates (official sources)",
           f"Tourist tax changes in 2027 with an official date: Turkey 2%, Okinawa and new Japanese taxes, Cancún Visitax, Cardiff £1.30, Catalonia, Barcelona, Tokyo 3%, Vienna 8%.",
           corpo, briciole=[("Tourist tax changes 2027", "tourist-tax-changes-2027/")], jsonld_extra=ld)


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
<p>Paid once, not per night. Examples: <a href="{rel}bali/">Bali</a> and the Visitax of Quintana Roo in Mexico (<a href="{rel}mexico/">Cancún, Tulum, Playa del Carmen, Cozumel</a>), which the law sets as 2.50 UMA, a reference value in pesos updated every February.</p>
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
<li>Wales (Cardiff): contains public sector information licensed under the <a href="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/" rel="noopener">Open Government Licence v3.0</a> (gov.wales, Welsh Revenue Authority).</li>
<li>Mexico: laws of the State of Quintana Roo (Congress of Quintana Roo), the Ley Federal de Derechos (Chamber of Deputies), the decree of 30 June 2025 (SIDOF) and the UMA values of INEGI are cited as facts with a link to the official text; the Visitax amounts are calculated by us from the formula in the law (2.50 UMA). See the <a href="{rel}mexico/">Mexico page</a> for all sources.</li>
<li>Japan accommodation tax: the list of taxes in force and approved comes from the Ministry of Internal Affairs and Communications (法定外税の状況); rates from the Minister's consents published by the Ministry and from prefecture and city pages, cited as facts with a link; see the <a href="{rel}{JT_HUB}">Japan accommodation tax page</a> and each place's page for all sources.</li>
<li>Japan tax-free refund: rules from the Japan Tourism Agency, the National Tax Agency and Japan Customs (Ministry of Finance), cited as facts with a link to each official page; see the <a href="{rel}japan-tax-free-refund/">Japan tax-free refund page</a> for all sources.</li>
<li>Spain, holiday let licences: counts from INE (experimental statistics on tourist homes, source: INE), the Generalitat Valenciana open data (CC BY 4.0), the Junta de Andalucía OPEN RTA (CC BY 4.0) and the Generalitat de Catalunya open data (Registre de Turisme de Catalunya); we publish only counts by municipality and month, never names, addresses or contact details. Laws on BOE, BOCM and the Junta de Andalucía site are cited as facts with a link. See the <a href="{rel}{ES_SLUG}">Spain holiday let licence page</a> for all sources.</li>
<li>United States (Florida and Texas hotel tax): rates from the Florida Department of Revenue (forms DR-15TDT and DR-15DSS) and from the Texas Comptroller of Public Accounts (hotel occupancy tax pages and the Local Hotel Occupancy Tax Reporting dataset on data.texas.gov, rates as reported by each city and county); counties of each city from the U.S. Census Bureau's 2020 place-by-county file (public domain). See the <a href="{rel}{US_HUB}">USA hotel tax page</a> for all sources.</li>
<li>Laws, ordinances and official decisions are cited as facts with a link to the official text; we do not reproduce the documents.</li></ul>
<h2>Destinations not published (official source not readable or incomplete)</h2>
<p>Venice, Lisbon, the Algarve, Budapest, Croatia (Dubrovnik, Split), Cyprus, Naples, Bologna, Glasgow, Antwerp, Egypt, Morocco and the Canary Islands. We will add them when we can verify a complete official source.</p>
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
    # Cookie, link di affiliazione e pubblicità: con AdSense acceso (monetizzazione.json) o con link di affiliazione, il testo
    # comune di monetizzazione.py (GoatCounter senza cookie, pubblicità con il consenso di Google); altrimenti il testo di oggi.
    cookie = MON.privacy_cookie("en", SITO_ID, ci_sono_affiliati()) or """<h2>Cookies and visit counter</h2><p>This site does not use profiling cookies. To count visits we use <a href="https://www.goatcounter.com/" rel="noopener">GoatCounter</a>, a privacy-friendly counter: it sets no cookies and stores nothing in your browser, builds no profiles and does not store your IP address, your full browser signature or any identifier. It keeps only aggregate numbers (page, hour or day, browser, country, screen width) on servers in the European Union and shares nothing with third parties; see <a href="https://www.goatcounter.com/help/privacy" rel="noopener">GoatCounter's privacy policy</a>. If we add advertising or affiliate links in the future, we will update this notice and ask for your consent where required before any advertising cookies are used.</p>"""
    corpo = f"""<section class="hero"><h1>Privacy notice</h1><p class="small">Last updated: October 2026</p></section><div class="testo">
<h2>Who is responsible</h2><p>The data controller is Massimiliano Cori (Italy), who runs {NOME} as an independent project. You can contact us through the <a href="contact/">contact form</a>.</p>
<h2>What we collect</h2><p>Only what you type in the contact form: your email, the destination and your message. We also record the page or link you came from, to understand which pages need corrections. The calculator runs in your browser: what you type in it is not sent to us.</p>
<h2>Why</h2><p>To answer your messages and correct the site. The legal basis is your consent (Art. 6(1)(a) GDPR), which you can withdraw at any time.</p>
<h2>Who processes data for us</h2><p>The site and its form are hosted by Netlify, Inc., which stores form data on our behalf and may process it outside the EU with the safeguards required by the GDPR (standard contractual clauses). We do not sell or share your data.</p>
{cookie}
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
    MON.scrivi_ads_txt(SITO_ID, SITO)  # sito/ads.txt solo con AdSense acceso (monetizzazione.json)
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
        (pagina_messico_dest if d["country_slug"] == "mexico" else pagina_destinazione)(d)
    pagina_messico()
    pagina_giappone_rimborso()
    pagine_jt()
    pagine_es()
    pagine_us()
    pagina_francia()
    for c in FR_TOP["comuni"]:
        pagina_francia_comune(c[0])
    for s in PAESI:
        if s not in ("france", "mexico"):
            pagina_paese(s)
    pagina_europa()
    pagina_cambi_2027()
    pagina_come_funziona()
    about()
    contatti()
    privacy()
    dati_francia_client()
    extra()
    cambi = sorted({x for d in DEST for t in d["tariffe"] + d.get("supplementi", []) for x in
                    ([t["dal"]] if t.get("dal") else []) + ([(date.fromisoformat(t["al"]) + timedelta(days=1)).isoformat()] if t.get("al") else [])
                    if x > OGGI.isoformat()} | {f"{ANNO + 1}-01-01"})
    cambi_jt = sorted({d for L in JT_LUOGHI for d in jt_date_cambio(L)})
    print("Date in cui rigenerare il sito (cambiano tariffe o titoli):", ", ".join(cambi))
    print("Giappone, tasse di soggiorno: rigenerare anche il", ", ".join(cambi_jt), "- e controllare le fonti ogni trimestre con python3 -I touristtax/raccolta/giappone.py")
    p = UMA["prossima"]
    if not any(v["anno"] == p["anno"] for v in UMA["valori"]):
        print(f"Messico: UMA {p['anno']} non ancora nei dati. Da inizio gennaio {p['anno']}: python3 -I touristtax/raccolta/uma.py, poi rigenerare "
              f"(Visitax dal {p['dal']}). Il 1/1/{p['anno']} controllare anche gli importi della Ley Federal de Derechos (DNR).")
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili; {len(DEST)} destinazioni, {len(FR_TOP['comuni'])} pagine comunali francesi, "
          f"{len(FR['comuni'])} comuni nella ricerca.")


if __name__ == "__main__":
    main()
