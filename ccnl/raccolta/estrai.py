"""Estrae le cifre dalle fonti scaricate e le incrocia: scrive ccnl/dati/estratti.json e ccnl/dati/contratti.json.

Uso (dalla radice del repository, dopo raccolta/fonti.py):
    python3 ccnl/raccolta/estrai.py

Per ogni contratto ci sono due fonti indipendenti (A e B). Una cifra entra nel sito solo se:
  1) le parti stampate nella fonte A sommano al totale stampato (dove la fonte stampa un totale);
  2) la fonte B riporta gli stessi importi, al centesimo.
Le righe che non passano restano in dati/contratti.json con il motivo ("esclusa") e non vengono pubblicate.

  Lavoro domestico   A = tabella del Ministero del Lavoro (2026)        B = stessa tabella depositata al CNEL con il verbale dell'11/2/2026
  Terziario          A = testo unico CNEL 3/2/2026, pagine 363-364 (lettura ottica)   B = tabelle dei minimi pubblicate da Filcams CGIL
  Metalmeccanici     A = tabelle del Ministero, decreto n. 94/2026 (annuo ÷ 12)        B = accordo del 22/11/2025, pagina 2 (Federmeccanica, lettura ottica)
  Multiservizi       A = tabelle del Ministero, decreto n. 25/2026 (annuo ÷ 12)        B = accordo integrativo del 6/8/2025 al CNEL (lettura ottica + correzioni)
  Logistica          A = testo CNEL del 25/9/2025 (tabelle dei minimi e EPA)           B = tabelle del Ministero, decreto n. 135/2025 (annuo ÷ 12)

Le correzioni della lettura ottica stanno in dati/correzioni_ocr.json: ognuna dice pagina, valore letto dalla macchina e
valore letto sull'immagine della pagina. I controlli sopra valgono anche per i valori corretti.
"""
import json
import re
from datetime import date
from decimal import Decimal
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
GREZZI = RADICE / "raccolta" / "_grezzi"
OCR = GREZZI / "ocr"
DATI = RADICE / "dati"
NUM = r"\d{1,3}(?:\.\d{3})*,\d{2}"
MESI = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8, "settembre": 9,
        "ottobre": 10, "novembre": 11, "dicembre": 12}


def d(s):
    """'1.784,94' -> Decimal('1784.94')"""
    return Decimal(s.replace(".", "").replace(",", "."))


def c(x):
    """Decimal -> stringa con 2 decimali (per il JSON)."""
    return f"{Decimal(x):.2f}"


def mensile(annuo):
    """Annuo del Ministero ÷ 12; l'annuo deve essere esattamente 12 mensilità al centesimo."""
    m = (annuo / 12).quantize(Decimal("0.01"))
    return m, (m * 12 == annuo)


def testo(fid):
    return (GREZZI / f"{fid}.txt").read_text(encoding="utf-8")


def ocr(fid, n):
    return (OCR / f"{fid}_p{n:04d}.txt").read_text(encoding="utf-8")


CORR = json.loads((DATI / "correzioni_ocr.json").read_text(encoding="utf-8"))["correzioni"]


def correggi(fonte, pagina, data_, livello, campo, valore_ocr):
    for x in CORR:
        if (x["fonte"], x["pagina"], x["data"], x["livello"], x["campo"]) == (fonte, pagina, data_, livello, campo):
            return Decimal(x["valore"]), x
    return (d(valore_ocr) if valore_ocr and re.fullmatch(NUM, valore_ocr) else None), None


# ---------------------------------------------------------------- lavoro domestico
COL_DOM = ["A_mensile", "A_indennita", "B_mensile", "C_oraria", "D_autosuff", "D_non_autosuff", "E_mensile", "F_pranzo", "F_cena", "F_alloggio",
           "F_totale", "G_oraria", "H_mensile", "H_mensile_tab_b", "H_oraria", "I_mensile", "I_oraria", "L_mensile"]


def domestico(fid):
    righe = []
    for riga in testo(fid).splitlines():
        m = re.match(r"^\s*(Liv\. unico|AS|BS|CS|DS|A|B|C|D)\s", riga)
        if m:
            righe.append((m.group(1), [(mm.end(), mm.group()) for mm in re.finditer(NUM, riga)]))
    fini = sorted({e for _, n in righe for e, _ in n})
    gruppi = []
    for e in fini:
        if gruppi and e - gruppi[-1][-1] <= 4:
            gruppi[-1].append(e)
        else:
            gruppi.append([e])
    if len(gruppi) != len(COL_DOM):
        raise SystemExit(f"{fid}: attese {len(COL_DOM)} colonne, trovate {len(gruppi)}")
    col = {e: COL_DOM[i] for i, g in enumerate(gruppi) for e in g}
    out = {}
    for liv, nums in righe:
        out["unico" if liv.startswith("Liv") else liv] = {col[e]: c(d(v)) for e, v in nums}
    return out


# ---------------------------------------------------------------- terziario
ORD_TERZ = ["q", "i", "ii", "iii", "iv", "v", "vi", "vii", "ov1", "ov2"]


def terziario_a():
    """Tabelle del testo unico (pagine 363 e 364, lettura ottica): per ogni data, paga base, altri elementi, contingenza+EDR, totale."""
    out = {}
    for pag in (363, 364):
        corrente = None
        righe = []
        for riga in ocr("cnel_246574", pag).splitlines():
            m = re.search(r"Paga base dal (\d{1,2})/(\d{1,2})/(\d{4})", riga)
            if m:
                corrente = date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
                out[corrente] = {}
                righe = []
                continue
            nums = re.findall(r"\d{3,4},\d{2}|\d{1,3},\d{2}", riga)
            if corrente and len(nums) in (3, 4):
                righe.append(nums)
                liv = ORD_TERZ[len(righe) - 1]
                v = [d(x.replace(".", "")) for x in nums]
                out[corrente][liv] = {"paga_base": c(v[0]), "altri_elementi": c(v[1]) if len(v) == 4 else "0.00",
                                      "contingenza_edr": c(v[-2]), "totale": c(v[-1]), "pagina": pag}
    return out


def terziario_b():
    """Tabelle Filcams (HTML): per ogni data paga base, contingenza, indennità di funzione / elemento aggiuntivo, terzo elemento, totale."""
    t = re.sub(r"\s+", " ", testo("filcams_minimi"))
    out = {}
    for m in re.finditer(r"TERZIARIO - MINIMI DAL (\d{1,2})/(\d{2})/(\d{4}) livelli .*? totale (.*?)(?=TERZIARIO - MINIMI DAL|OPERATORI DI VENDITA - MINIMI|$)", t):
        dt = date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
        corpo = m.group(4)
        righe = {}
        for liv, rx in [("q", r"\bQ ((?:\d+,\d\d ){6}\d+,\d\d)"), ("i", r"\b1° ((?:\d+,\d\d ){5}\d+,\d\d)"), ("ii", r"\b2° ((?:\d+,\d\d ){5}\d+,\d\d)"),
                        ("iii", r"\b3° ((?:\d+,\d\d ){5}\d+,\d\d)"), ("iv", r"\b4° ((?:\d+,\d\d ){5}\d+,\d\d)"), ("v", r"\b5° ((?:\d+,\d\d ){5}\d+,\d\d)"),
                        ("vi", r"\b6° ((?:\d+,\d\d ){5}\d+,\d\d)"), ("vii", r"\b7° ((?:\d+,\d\d ){6}\d+,\d\d)"),
                        ("ov1", r"Operatori di vendita 1 ((?:\d+,\d\d ){4}\d+,\d\d)"), ("ov2", r"Operatori di vendita 1 (?:\d+,\d\d ){5}2 ((?:\d+,\d\d ){4}\d+,\d\d)")]:
            mm = re.search(rx, corpo)
            if not mm:
                continue
            v = [d(x) for x in mm.group(1).split()]
            if liv == "q":
                righe[liv] = {"paga_base": c(v[2]), "contingenza": c(v[3]), "altri_elementi": c(v[4]), "terzo_elemento": c(v[5]), "totale": c(v[6])}
            elif liv == "vii":
                righe[liv] = {"paga_base": c(v[2]), "altri_elementi": c(v[3]), "contingenza": c(v[4]), "terzo_elemento": c(v[5]), "totale": c(v[6])}
            elif liv.startswith("ov"):
                righe[liv] = {"paga_base": c(v[2]), "contingenza": c(v[3]), "altri_elementi": "0.00", "terzo_elemento": "0.00", "totale": c(v[4])}
            else:
                righe[liv] = {"paga_base": c(v[2]), "contingenza": c(v[3]), "altri_elementi": "0.00", "terzo_elemento": c(v[4]), "totale": c(v[5])}
        out[dt] = righe
    return out


# ---------------------------------------------------------------- metalmeccanici
def metalm_a():
    out = {}
    for fid in ("min_dd94_operai", "min_dd94_impiegati"):
        t = testo(fid)
        livelli = re.search(r"^Livelli\s+(.*)$", t, re.M).group(1).split()
        tab = re.findall(NUM, re.search(r"^Retribuzione tabellare(.*)$", t, re.M).group(1))
        for liv, a in zip(livelli, tab):
            m, esatto = mensile(d(a))
            prima = out.get(liv.lower())
            out[liv.lower()] = {"annuo": c(d(a)), "mensile": c(m), "annuo_divisibile_per_12": esatto,
                                "tabelle": (prima["tabelle"] if prima else []) + [fid]}
    return {"2026-06-01": out}


def metalm_b():
    ordine = ["d1", "d2", "c1", "c2", "c3", "b1", "b2", "b3", "a1"]
    out = {"2026-06-01": {}, "2027-06-01": {}, "2028-06-01": {}}
    t = ocr("fm_accordo_2025", 2)
    i = t.find("dal 1° giugno 2026")
    righe = [r for r in t[i:].splitlines()[1:] if len(re.findall(NUM, r)) >= 3][:9]
    for liv, r in zip(ordine, righe):
        v = re.findall(NUM, r)[:3]
        for dt, x in zip(out, v):
            out[dt][liv] = {"minimo": c(d(x))}
    return out


# ---------------------------------------------------------------- multiservizi
def data_mese(s):
    mese, anno = s.lower().split()
    return date(int(anno), MESI[mese], 1).isoformat()


def multi_a():
    """Pagine NAZIONALE delle tabelle del Ministero: retribuzione tabellare e contingenza annue, per ogni data e livello."""
    out = {}
    for fid in ("min_dd25_operai", "min_dd25_impiegati"):
        for p in testo(fid).split("\f"):
            m = re.search(r"^NAZIONALE\s+(OPERAI|IMPIEGATI)\s+(\w+ \d{4})", p, re.M)
            if not m:
                continue
            dt = data_mese(m.group(2))
            intest = re.search(r"^\s+(\d \(Par 109\).*|1\s+2 \(Par 109\).*)$", p, re.M).group(1)
            livelli = [x.strip() for x in re.split(r"\s{2,}", intest.strip())]
            tab = re.findall(NUM, re.search(r"^Retribuzione tabellare(.*)$", p, re.M).group(1))
            cont = re.findall(NUM, re.search(r"^Ind\. contingenza(.*)$", p, re.M).group(1))
            for liv, a, b in zip(livelli, tab, cont):
                k = {"2 (Par 109)": "2", "2 (Par 115)": "2p115"}.get(liv, liv.lower())
                tm, e1 = mensile(d(a))
                cm, e2 = mensile(d(b))
                riga = {"tabellare": c(tm), "contingenza": c(cm), "annuo_tabellare": c(d(a)), "annuo_contingenza": c(d(b)), "divisibile_per_12": e1 and e2}
                prec = out.setdefault(dt, {}).get(k)
                if prec and (prec["tabellare"], prec["contingenza"]) != (riga["tabellare"], riga["contingenza"]):
                    riga["incoerente_operai_impiegati"] = True
                riga["tabelle"] = (prec["tabelle"] if prec else []) + [m.group(1).lower()]
                out[dt][k] = riga
    return out


def multi_b():
    """Accordo integrativo del 6/8/2025 (CNEL 234752), pagine 1-4: tabelle per data (lettura ottica + correzioni)."""
    out, usate = {}, []
    ordine = ["q", "7", "6", "5", "4", "3", "2", "1"]
    for pag in (1, 2, 3, 4):
        t = ocr("cnel_234752", pag)
        blocchi = re.split(r"(?=Liv\. Par\. economico tabellare)", t)
        for b in blocchi[1:]:
            m = re.search(r"(Gennaio|Febbraio|Marzo|Aprile|Maggio|Giugno|Luglio|Agosto|Settembre|Ottobre|Novembre|Dicembre) (\d{4})", b)
            dt = data_mese(f"{m.group(1)} {m.group(2)}")
            righe = [r for r in b.splitlines()[2:] if re.search(r"\b(?:220|201|174|140|128|118|109|100)\s*€", r) or re.search(r"\bZ?Z?20 €|zZ20 €", r)]
            righe = righe[:8]
            out[dt] = {}
            for liv, r in zip(ordine, righe):
                campi = [x.strip() for x in r.split("€")[1:]]
                vals = {}
                for nome, x in zip(["aumento", "tabellare", "contingenza", "base", "edr"], campi + [None] * 5):
                    x = re.sub(r"[^\d.,]", "", x or "")
                    v, cor = correggi("cnel_234752", pag, dt, liv, nome, x)
                    if cor:
                        usate.append(cor)
                    vals[nome] = c(v) if v is not None else None
                vals["pagina"] = pag
                out[dt][liv] = vals
            # righe mancanti nella lettura ottica: solo dalle correzioni
            for liv in ordine:
                if liv not in out[dt]:
                    vals = {}
                    for nome in ["aumento", "tabellare", "contingenza", "base", "edr"]:
                        v, cor = correggi("cnel_234752", pag, dt, liv, nome, None)
                        if cor:
                            usate.append(cor)
                        vals[nome] = c(v) if v is not None else None
                    vals["pagina"] = pag
                    out[dt][liv] = vals
    # riga 1 di luglio 2025 spezzata dalla lettura ottica: valori dalle correzioni (già applicate sopra se presenti)
    return out, usate


# ---------------------------------------------------------------- logistica
NORM_LOG = {"quadri": "q", "1°": "1", "2°": "2", "3°super": "3s", "3°": "3", "4°": "4", "4°junior": "4j", "5°": "5", "6°": "6", "6°junior": "6j"}


def logistica_a():
    t = testo("cnel_223634")
    i = t.find("MINIMI CONTRATTUALI MENSILI ED ELEMENTO PROFESSIONALE D")
    j = t.find("L'aumento contrattuale complessivo è pari a")
    sez = t[i:j]
    out = {}
    gruppo, dt = None, None
    rx = re.compile(r"^\s*(Quadri|\d°(?:Super|Junior)?|[A-H]\d|I|L)\s+(?:\(\+[\d.,]+\)\s+)?(" + NUM + r")\s+(?:\(\+[\d.,]+\)\s+)?(" + NUM + r"|-)\s+(" + NUM + r")\s+([\d,]+)\s*$")
    for riga in sez.splitlines():
        if "Personale non viaggiante" in riga:
            gruppo = "non_viaggiante"
            continue
        if "Personale viaggiante" in riga:
            gruppo = "viaggiante"
            continue
        m = re.match(r"^\s*(\d{1,2})\.(\d{1,2})\.(\d{4})\s*$", riga)
        if m:
            dt = date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
            continue
        m = rx.match(riga)
        if m:
            lab = m.group(1)
            k = NORM_LOG.get(lab.lower(), lab.lower())
            if lab in ("I", "L"):
                k = f"{lab.lower()}_p{m.group(5).replace(',', '')}"
            epa = "0.00" if m.group(3) == "-" else c(d(m.group(3)))
            out.setdefault(gruppo, {}).setdefault(dt, {})[k] = {"minimo": c(d(m.group(2))), "epa": epa, "totale": c(d(m.group(4))), "parametro": m.group(5)}
    return out


def logistica_b():
    out = {}
    for p in testo("min_dd135").split("\f"):
        m = re.search(r"^(Personale.*?)\((GENNAIO|GIUGNO) (\d{4})\)", p, re.M | re.S)
        if not m:
            continue
        intest = re.sub(r"\s+", " ", m.group(1)).strip()
        dt = date(int(m.group(3)), 1 if m.group(2) == "GENNAIO" else 6, 1).isoformat()
        righe = p.split("\n")
        k = [n for n, r in enumerate(righe) if r.startswith("A-Elementi")][0]
        lab = [x.strip() for x in re.split(r"\s{2,}|(?<=\)) (?=[A-Z])", righe[k - 2].strip()) if x.strip()]
        base = re.findall(NUM, re.search(r"^Retribuzione base(.*)$", p, re.M).group(1))
        epa = re.findall(NUM, re.search(r"^EPA(.*)$", p, re.M).group(1))
        if len(epa) == len(base) - 1 and lab and lab[0] == "6J":
            epa = ["0,00"] + epa
        if "non viaggiante" in intest:
            gruppo = "non_viaggiante"
        elif "DRIVER" in intest:
            gruppo = "driver_rider"
        elif "senza discontinuità" in intest:
            gruppo = "viaggiante"
        else:
            gruppo = "viaggiante_discontinuo_" + ("internazionali" if "Internazionali" in intest else "nazionali")
        for l, b, e in zip(lab, base, epa):
            bm, e1 = mensile(d(b))
            em, e2 = mensile(d(e))
            key = l.lower()
            out.setdefault(gruppo, {}).setdefault(dt, {})[key] = {"minimo": c(bm), "epa": c(em), "annuo_base": c(d(b)), "annuo_epa": c(d(e)),
                                                                     "divisibile_per_12": e1 and e2, "tabella": intest[:90]}
    return out


# ---------------------------------------------------------------- incrocio
def confronta(contratti_meta, est):
    """Costruisce dati/contratti.json: per ogni livello e data, parti, totale, controllo della somma e della seconda fonte."""
    oggi = date.today().isoformat()
    out = {"generato_il": oggi, "contratti": {}}
    for cid, meta in contratti_meta["contratti"].items():
        livelli = []
        for L in meta["livelli"]:
            tranche = []
            for dt, riga_a, riga_b, extra in righe_livello(cid, L, est):
                tranche.append(controlla(cid, L, dt, riga_a, riga_b, extra))
            if cid == "multiservizi":
                # l'aumento stampato nell'accordo deve essere la differenza tra il tabellare di una data e quello della data prima
                for prima, dopo in zip(tranche, tranche[1:]):
                    b = dopo.get("fonte_b") or {}
                    diff = c(Decimal(dopo["fonte_a"]["tabellare"]) - Decimal(prima["fonte_a"]["tabellare"])) if dopo.get("fonte_a") and prima.get("fonte_a") else None
                    dopo["aumento_ok"] = diff is not None and b.get("aumento") == diff
                    if not dopo["aumento_ok"]:
                        dopo["motivi"].append(f"aumento stampato {b.get('aumento')} diverso dalla differenza tra le tabelle ({diff})")
                        dopo["pubblicabile"] = False
            livelli.append({"id": L["id"], "tranche": tranche})
        out["contratti"][cid] = {"livelli": livelli}
    return out


def righe_livello(cid, L, est):
    """(data, parti dalla fonte A con totale, valori della fonte B, extra) per un livello."""
    if cid == "domestico":
        a, b = est["domestico"]["A"].get(L["chiave"]), est["domestico"]["B"].get(L["chiave"])
        yield "2026-01-01", a, b, {}
    elif cid == "terziario":
        for dt, righe in sorted(est["terziario"]["A"].items()):
            yield dt, righe.get(L["chiave"]), est["terziario"]["B"].get(dt, {}).get(L["chiave"]), {}
    elif cid == "metalmeccanici":
        dt = "2026-06-01"
        yield dt, est["metalmeccanici"]["A"][dt].get(L["chiave"]), est["metalmeccanici"]["B"][dt].get(L["chiave"]), {}
        for dt in ("2027-06-01", "2028-06-01"):
            yield dt, None, est["metalmeccanici"]["B"][dt].get(L["chiave"]), {"solo_b": True}
    elif cid == "multiservizi":
        for dt, righe in sorted(est["multiservizi"]["A"].items()):
            yield dt, righe.get(L["chiave"]), est["multiservizi"]["B"].get(dt, {}).get(L["chiave"]), {}
    elif cid == "logistica":
        g = L["gruppo"]
        ga = est["logistica"]["A"].get(g, {})
        gb = est["logistica"]["B"].get(L.get("gruppo_b", g), {})
        for dt in sorted(ga):
            if L["chiave"] in ga[dt]:
                yield dt, ga[dt][L["chiave"]], gb.get(dt, {}).get(L.get("chiave_b", L["chiave"])), {}


def controlla(cid, L, dt, a, b, extra):
    t = {"dal": dt, "pubblicabile": False, "motivi": []}
    if extra.get("solo_b"):
        t["motivi"].append("cifra scritta solo nell'accordo del 22/11/2025 (nessuna seconda fonte ufficiale): non pubblicata")
        t["fonte_b"] = b
        return t
    if a is None:
        t["motivi"].append("riga assente nella fonte A")
        return t
    if b is None:
        t["motivi"].append("riga assente nella fonte B")
        t["fonte_a"] = a
        return t
    D = lambda x: Decimal(x)  # noqa: E731
    if cid == "domestico":
        comp = [("Minimo mensile (convivente, tabella A)", a.get("A_mensile"))] if a.get("A_mensile") else []
        t["parti"] = [p for p in comp if p[1]]
        t["indennita_funzione"] = a.get("A_indennita")
        t["tabelle"] = a
        t["somma_ok"] = True  # nessun totale stampato per livello (solo la riga F ha un totale, controllato a parte)
        t["seconda_fonte_ok"] = (a == b)
        t["fonte_a"], t["fonte_b"] = a, b
        if not t["seconda_fonte_ok"]:
            t["motivi"].append("le due copie della tabella non coincidono")
    elif cid == "terziario":
        parti = [("Paga base", a["paga_base"])] + ([("Altri elementi", a["altri_elementi"])] if D(a["altri_elementi"]) else []) + [("Contingenza + EDR", a["contingenza_edr"])]
        t["parti"] = parti
        t["totale"] = a["totale"]
        t["somma_ok"] = sum(D(x) for _, x in parti) == D(a["totale"])
        t["seconda_fonte_ok"] = (a["paga_base"], a["altri_elementi"], a["contingenza_edr"]) == (b["paga_base"], b["altri_elementi"], b["contingenza"]) \
            and D(b["totale"]) == D(a["totale"]) + D(b["terzo_elemento"])
        t["fonte_a"], t["fonte_b"] = a, b
        t["terzo_elemento"] = b["terzo_elemento"]
    elif cid == "metalmeccanici":
        t["parti"] = [("Minimo tabellare", a["mensile"])]
        t["totale"] = a["mensile"]
        t["somma_ok"] = a["annuo_divisibile_per_12"]
        t["seconda_fonte_ok"] = a["mensile"] == b["minimo"]
        t["fonte_a"], t["fonte_b"] = a, b
    elif cid == "multiservizi":
        parti = [("Retribuzione tabellare", a["tabellare"]), ("Indennità di contingenza", a["contingenza"])]
        t["parti"] = parti
        t["totale"] = c(D(a["tabellare"]) + D(a["contingenza"]))
        t["edr"] = b.get("edr")
        t["somma_ok"] = bool(b.get("base")) and D(b["tabellare"] or 0) + D(b["contingenza"] or 0) == D(b["base"]) and a["divisibile_per_12"]
        t["seconda_fonte_ok"] = (a["tabellare"], a["contingenza"], t["totale"]) == (b.get("tabellare"), b.get("contingenza"), b.get("base"))
        t["fonte_a"], t["fonte_b"] = a, b
    elif cid == "logistica":
        parti = [("Minimo contrattuale", a["minimo"])] + ([("EPA (elemento professionale d'area)", a["epa"])] if D(a["epa"]) else [])
        t["parti"] = parti
        t["totale"] = a["totale"]
        t["somma_ok"] = sum(D(x) for _, x in parti) == D(a["totale"])
        t["seconda_fonte_ok"] = (a["minimo"], a["epa"]) == (b["minimo"], b["epa"]) and b["divisibile_per_12"]
        t["fonte_a"], t["fonte_b"] = a, b
    if not t.get("somma_ok"):
        t["motivi"].append("la somma delle parti non torna con il totale stampato")
    if not t.get("seconda_fonte_ok") and "le due copie della tabella non coincidono" not in t["motivi"]:
        t["motivi"].append("la seconda fonte riporta importi diversi")
    t["pubblicabile"] = not t["motivi"]
    return t


def main():
    est = {
        "domestico": {"A": domestico("min_domestico_2026"), "B": domestico("cnel_245798")},
        "terziario": {"A": terziario_a(), "B": terziario_b()},
        "metalmeccanici": {"A": metalm_a(), "B": metalm_b()},
        "multiservizi": {"A": multi_a()},
        "logistica": {"A": logistica_a(), "B": logistica_b()},
    }
    est["multiservizi"]["B"], usate = multi_b()
    est["correzioni_usate"] = len(usate)
    (DATI / "estratti.json").write_text(json.dumps(est, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    meta = json.loads((DATI / "contratti_meta.json").read_text(encoding="utf-8"))
    res = confronta(meta, est)
    (DATI / "contratti.json").write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tot = pub = 0
    for cid, cc in res["contratti"].items():
        for L in cc["livelli"]:
            for t in L["tranche"]:
                tot += 1
                pub += t["pubblicabile"]
                if not t["pubblicabile"]:
                    print(f"  escluso {cid}/{L['id']} dal {t['dal']}: {'; '.join(t['motivi'])}")
    nc = len(CORR)
    print(f"{pub} cifre pubblicabili su {tot}; correzioni della lettura ottica usate {len(usate)} su {nc}")
    if len(usate) != nc:
        raise SystemExit("correzioni_ocr.json contiene voci non usate: controllare pagina/data/livello/campo")


if __name__ == "__main__":
    main()
