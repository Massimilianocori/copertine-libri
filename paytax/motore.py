"""Motore di calcolo di riferimento (Python) della payroll tax per le 8 giurisdizioni australiane.

Il calcolatore del sito è in JavaScript (MOTORE_JS in genera.py) e deve dare gli stessi numeri: verifica.py esegue
il JS pubblicato con node su migliaia di casi e lo confronta con questo file, poi controlla gli esempi ufficiali
(dati/esempi_ufficiali.json). Le formule vengono dai testi ufficiali citati in dati/giurisdizioni.json:

  W = salari imponibili australiani totali (del datore o del gruppo); w = salari dello Stato; q = w / W;
  f = C / FY (giorni in cui si sono pagati salari in Australia / giorni dell'anno fiscale).

  NSW  soglia = 1.200.000 × q × f;  imposta = (w − soglia) × 5,45 %                         (Revenue NSW, esempi)
  VIC  D1 = 1.000.000 × f × q; se 3 < W ≤ 5 milioni D = D1 − (w − 3.000.000 × f × q) × 50 %;
       W > 5 milioni D = 0; imposta = (w − D) × 4,85 % (1,2125 % regionale);
       sovrattasse 1 % × (w − 10 mln × q × f) e altro 1 % × (w − 100 mln × q × f)           (SRO, 4 passi + esempi)
  QLD  AD = q × (K f − (W − K f) / 7), K = 1,3 milioni, AD ≥ 0;  imposta = (w − AD) × 4,75 % (4,95 % se W > 6,5 mln;
       −1 % regionale se W ≤ 350 mln); levy 0,25 % × (w − 10 mln × q × f) + 0,5 % × (w − 100 mln × q × f)
                                                                              (Payroll Tax Act 1971 s 29, QRO)
  WA   AAT = 1 mln × f, AUT = 7,5 mln × f; W ≤ AAT: 0; W ≥ AUT: w × 5,5 %;
       altrimenti D = (AAT − (W − AAT) × 2/13) × q, imposta = (w − D) × 5,5 %           (Assessment Act 2002 s 10, 13)
  SA   W ≤ 1,5 mln × f: 0; imposta = (w − q × 600.000 × f) × R; R = 4,95 % se W/f > 1,7 mln,
       altrimenti (W/f − 1,5 mln) / 200.000 × 4,95 %                                       (Payroll Tax Act 2009 sch 1)
  TAS  T1 = 1,25 mln × f, T2 = 2 mln × f; W ≤ T1: 0; W ≤ T2: (w − q T1) × 4 %;
       oltre: (T2 − T1) × q × 4 % + (w − q T2) × 6,1 %                                     (Payroll Tax Act 2008 sch 1)
  ACT  W ≤ 1,75 mln × f: 0; imposta = (w − q × 1,75 mln × f) × R, R dallo scaglione di W (6,75 % ... 8,75 %, su tutto);
       se W ≤ 1,75 mln ma > soglia ridotta (anno parziale) R non è definito: NON si calcola     (Act 2011 sch 1, DI2026-151)
  NT   ETA = 2,5 mln × f; W ≤ ETA: 0; AD = max(0, ETA − (W − ETA)/2); imposta = (w − q AD) × R;
       R = 6,5 % se W ≥ 100 mln, altrimenti 5,5 %                                           (Payroll Tax Act 2009 s 7A, sch 1)

Le operazioni sono scritte nello stesso ordine del JS, così i numeri in virgola mobile coincidono.
"""
import json
import math
from pathlib import Path

DATI = Path(__file__).resolve().parent / "dati"
ORDINE = ["nsw", "vic", "qld", "wa", "sa", "tas", "act", "nt"]


def carica_parametri():
    return json.loads((DATI / "giurisdizioni.json").read_text(encoding="utf-8"))["parametri"]


def r2(x):
    """Arrotondamento ai centesimi come Math.round del JS (mezzo centesimo verso l'alto)."""
    return math.floor(x * 100 + 0.5) / 100


def _pos(x):
    return x if x > 0 else 0


def calcola_stato(s, P, w, W, f, regionale_vic=False, regionale_qld=False):
    """Una giurisdizione. Restituisce un dizionario con: stato (ok | sotto | zero | non_calcolato), soglia (importo dedotto),
    imponibile, aliquota (frazione o None), tassa, extra (levy o sovrattasse), avvisi (codici)."""
    p = P[s]
    out = {"s": s, "w": w, "stato": "ok", "soglia": 0.0, "imponibile": 0.0, "aliquota": None, "tassa": 0.0, "extra": 0.0, "avvisi": []}
    if w <= 0:
        out["stato"] = "zero"
        return out
    q = w / W
    if s == "nsw":
        d = p["soglia"] * q * f
        out["soglia"] = d
        out["imponibile"] = _pos(w - d)
        out["aliquota"] = p["aliquota"] / 100
        out["tassa"] = out["imponibile"] * out["aliquota"]
    elif s == "vic":
        d1 = p["soglia"] * f * q
        if W <= p["phase_da"]:
            d = d1
        elif W <= p["phase_a"]:
            d = _pos(d1 - (w - p["phase_da"] * f * q) * (p["phase_quota"] / 100))
            out["avvisi"].append("vic_phase")
        else:
            d = 0.0
            out["avvisi"].append("vic_no_soglia")
        out["soglia"] = d
        out["imponibile"] = _pos(w - d)
        out["aliquota"] = (p["regionale"] if regionale_vic else p["aliquota"]) / 100
        out["tassa"] = out["imponibile"] * out["aliquota"]
        extra = 0.0
        for lim, al in p["sovrattasse"]:
            extra += _pos(w - lim * q * f) * (al / 100)
        out["extra"] = extra
        if extra > 0:
            out["avvisi"].append("vic_sovrattasse")
    elif s == "qld":
        kf = p["soglia"] * f
        ad = _pos(q * (kf - (W - kf) / p["rapporto"]))
        out["soglia"] = ad
        out["imponibile"] = _pos(w - ad)
        al = p["aliquota"] if W <= p["aliquota_alta_da"] else p["aliquota_alta"]
        if regionale_qld:
            if W <= p["regionale_max"]:
                al = al - p["sconto_regionale"]
            else:
                out["avvisi"].append("qld_regionale_oltre")
        out["aliquota"] = al / 100
        out["tassa"] = out["imponibile"] * out["aliquota"]
        extra = 0.0
        for lim, a in p["levy"]:
            extra += _pos(w - lim * q * f) * (a / 100)
        out["extra"] = extra
        if extra > 0:
            out["avvisi"].append("qld_levy")
    elif s == "wa":
        aat = p["soglia"] * f
        aut = p["soglia_superiore"] * f
        out["aliquota"] = p["aliquota"] / 100
        if W <= aat:
            out["soglia"] = w
            out["imponibile"] = 0.0
        elif W >= aut:
            out["soglia"] = 0.0
            out["imponibile"] = w
            out["avvisi"].append("wa_no_soglia")
        else:
            tv = p["soglia"] / (p["soglia_superiore"] - p["soglia"])
            d = (aat - (W - aat) * tv) * q
            out["soglia"] = d
            out["imponibile"] = _pos(w - d)
        out["tassa"] = out["imponibile"] * out["aliquota"]
    elif s == "sa":
        if W <= p["soglia"] * f:
            out["soglia"] = w
        else:
            tarw = W / f
            if tarw > p["piena_da"]:
                r = p["aliquota"] / 100
            else:
                r = (tarw - p["soglia"]) / (p["piena_da"] - p["soglia"]) * (p["aliquota"] / 100)
            d = q * p["deduzione"] * f
            out["soglia"] = d
            out["imponibile"] = _pos(w - d)
            out["aliquota"] = r
            out["tassa"] = out["imponibile"] * r
            if tarw <= p["piena_da"]:
                out["avvisi"].append("sa_variabile")
    elif s == "tas":
        t1 = p["soglia"] * f
        t2 = p["soglia2"] * f
        if W <= t1:
            out["soglia"] = w
        elif W <= t2:
            out["soglia"] = q * t1
            out["imponibile"] = _pos(w - q * t1)
            out["aliquota"] = p["aliquota1"] / 100
            out["tassa"] = out["imponibile"] * out["aliquota"]
        else:
            out["soglia"] = q * t1
            out["imponibile"] = _pos(w - q * t1)
            out["aliquota"] = None  # due aliquote: 4 % sulla fascia, 6,1 % sopra
            out["tassa"] = (t2 - t1) * q * (p["aliquota1"] / 100) + _pos(w - q * t2) * (p["aliquota2"] / 100)
            out["avvisi"].append("tas_due_fasce")
    elif s == "act":
        tac = p["soglia"] * f
        if W <= tac:
            out["soglia"] = w
        elif W <= p["soglia"]:
            out["stato"] = "non_calcolato"
            out["avvisi"].append("act_anno_parziale")
        else:
            r = None
            for lim, al in p["scaglioni"]:
                if lim is None or W <= lim:
                    r = al / 100
                    break
            d = q * tac
            out["soglia"] = d
            out["imponibile"] = _pos(w - d)
            out["aliquota"] = r
            out["tassa"] = out["imponibile"] * r
            out["avvisi"].append("act_su_tutto")
    elif s == "nt":
        eta = p["soglia"] * f
        if W <= eta:
            out["soglia"] = w
        else:
            ad = _pos(eta - (W - eta) / 2)
            r = (p["aliquota_alta"] if W >= p["aliquota_alta_da"] else p["aliquota"]) / 100
            out["soglia"] = q * ad
            out["imponibile"] = _pos(w - q * ad)
            out["aliquota"] = r
            out["tassa"] = out["imponibile"] * r
            if ad == 0:
                out["avvisi"].append("nt_no_soglia")
    else:
        raise ValueError(s)
    if out["stato"] == "ok" and out["tassa"] <= 0 and out["extra"] <= 0:
        out["stato"] = "sotto"  # sotto la soglia: nessuna imposta in questa giurisdizione
    return out


def calcola(P, salari, giorni=365, giorni_anno=365, regionale_vic=False, regionale_qld=False):
    """salari: {codice: importo} (codici di ORDINE e, facoltativo, "altro" = salari in Stati non calcolati).
    Restituisce {"W", "f", "righe": [...], "totale", "extra", "complessivo", "mensile", "non_calcolati"}."""
    W = 0.0
    for k, v in salari.items():
        W += v if v > 0 else 0
    g = min(max(giorni, 1), giorni_anno)
    f = g / giorni_anno
    righe = []
    tot = extra = 0.0
    non_calc = []
    for s in ORDINE:
        w = salari.get(s, 0)
        if not w or w <= 0:
            continue
        r = calcola_stato(s, P, w, W, f, regionale_vic, regionale_qld)
        righe.append(r)
        if r["stato"] == "non_calcolato":
            non_calc.append(s)
        else:
            tot += r["tassa"]
            extra += r["extra"]
    return {"W": W, "f": f, "righe": righe, "totale": tot, "extra": extra, "complessivo": tot + extra,
            "mensile": (tot + extra) / 12, "non_calcolati": non_calc}
