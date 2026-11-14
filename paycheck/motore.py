"""Conti della busta paga in centesimi interi: copia riga per riga di app.js (busta, datore).

genera.py lo usa per gli esempi scritti nelle pagine; verifica.py confronta app.js con un calcolo INDIPENDENTE
(frazioni esatte, tabelle rilette dai PDF), non con questo file.
dati_js(regole) trasforma dati/regole.json nel JSON compatto che va nelle pagine: importi in centesimi,
aliquote in millesimi di punto percentuale (6,2 % = 6200).
"""


def c(x):
    return int(round(x * 100))


def m(x):
    return int(round(x * 100000))


def dati_js(g):
    fed = {lato: {k: [[c(r["da"]), c(r["base"]), r["pct"]] for r in v] for k, v in t.items()} for lato, t in g["federale"]["tabelle"].items()}
    out = {"anno": g["anno"], "P": g["periodi"], "g1": {k: c(v) for k, v in g["federale"]["riga_1g"].items()}, "fed": fed,
           "fica": {"ss": m(g["fica"]["ss"]), "ssBase": c(g["fica"]["ss_base"]), "med": m(g["fica"]["medicare"]), "addl": m(g["fica"]["addl"]), "addlSoglia": c(g["fica"]["addl_soglia"])},
           "futa": {"base": c(g["futa"]["base"]), "netta": m(g["futa"]["netta"]), "rid": {k: m(v) for k, v in g["futa"]["riduzione_credito"].items()}}, "st": {}}
    for sigla, s in g["stati"].items():
        o = {"nome": s["nome"], "suta": {"nome": s["suta"]["nome"], "nuovo": m(s["suta"]["nuovo"]), "base": c(s["suta"]["base"])}, "it": None}
        if "ett" in s["suta"]:
            o["ett"], o["ettBase"] = m(s["suta"]["ett"]), c(s["suta"]["ett_base"])
        if s.get("sdi"):
            o["sdi"] = m(s["sdi"]["aliquota"])
        it = s["imposta_reddito"]
        if it and it["metodo"] == "il":
            o["it"] = {"m": "il", "r": m(it["aliquota"]), "l1": c(it["riga1"]), "l2": c(it["riga2"])}
            o["itNota"] = "4.95% after IL-W-4 allowances"
        elif it and it["metodo"] == "nc":
            o["it"] = {"m": "nc", "r": m(it["aliquota_ritenuta"]), "p": {per: {k: [c(v["deduzione"]), c(v["esenzione"])] for k, v in d.items()} for per, d in it["periodi"].items()}}
            o["itNota"] = "4.09% withholding rate, rounded to the dollar"
        elif it and it["metodo"] == "ca":
            pass
        elif it and it["metodo"] == "ca_b":
            o["it"] = {"m": "ca", "es": {per: {k: c(v) for k, v in d.items()} for per, d in it["esenzione_basso_reddito"].items()},
                       "sd": {per: {k: c(v) for k, v in d.items()} for per, d in it["deduzione_standard"].items()},
                       "ed": {per: [c(v) for v in d] for per, d in it["deduzioni_stimate"].items()},
                       "cr": {per: [c(v) for v in d] for per, d in it["credito_esenzioni"].items()},
                       "tab": {per: {k: [[c(r["da"]), c(r["base"]), m(r["pct"] / 100)] for r in v] for k, v in d.items()} for per, d in it["scaglioni"].items()}}
            o["itNota"] = "EDD Method B"
        out["st"][sigla] = o
    return out


def mezzo(num, den):
    return 0 if num <= 0 else (2 * num + den) // (2 * den)


def quota(x, rate):
    return mezzo(x * rate, 100000)


def tra(x, lo, hi):
    return max(lo, min(hi, x))


def federale(R, i):
    P = R["P"][i["periodo"]]
    g1 = 0 if i.get("step2") else (R["g1"]["mfj"] if i["fs"] == "mfj" else R["g1"]["altro"])
    adj = max(0, i["lordo"] * P + i.get("a4", 0) - i.get("b4", 0) - g1)
    t = (R["fed"]["step2"] if i.get("step2") else R["fed"]["std"])[i["fs"]]
    r = t[0]
    for x in t[1:]:
        if adj >= x[0]:
            r = x
    anno100 = r[1] * 100 + (adj - r[0]) * r[2]
    h2, b3 = mezzo(anno100, 100 * P), mezzo(i.get("step3", 0), P)   # righe 2h e 3b, ognuna al centesimo come nel foglio
    return {"adj": adj, "da": r[0], "base": r[1], "pct": r[2], "tentativo": h2, "credito": b3, "ritenuta": max(0, h2 - b3) + i.get("c4", 0)}


def statale(R, i):
    S = R["st"][i["stato"]]["it"]
    o = {"imposta": 0}
    if not S:
        return o
    if S["m"] == "il":
        o["esenzioni"] = mezzo(i.get("il1", 0) * S["l1"] + i.get("il2", 0) * S["l2"], R["P"][i["periodo"]])
        o["imponibile"] = max(0, i["lordo"] - o["esenzioni"])
        o["imposta"] = quota(o["imponibile"], S["r"])
    elif S["m"] == "nc":
        p = S["p"][i["periodo"]]["hoh" if i.get("nc_fs") == "hoh" else "single"]
        o["deduzione"], o["esenzioni"] = p[0], i.get("nc_all", 0) * p[1]
        o["imponibile"] = max(0, i["lordo"] - p[0] - o["esenzioni"])
        o["imposta"] = mezzo(o["imponibile"] * S["r"], 10000000) * 100
    elif S["m"] == "ca":
        fs, reg, est = i.get("ca_fs") or "single", i.get("ca_reg", 0), i.get("ca_est", 0)
        col = ("married2" if reg >= 2 else "married01") if fs == "married" else fs
        o["soglia"] = S["es"][i["periodo"]][col]
        if i["lordo"] <= o["soglia"]:
            o["esente"] = True
            return o
        ed = S["ed"][i["periodo"]]
        o["stimate"] = 0 if est <= 0 else (ed[est - 1] if est <= 10 else est * ed[0])
        o["deduzione"] = S["sd"][i["periodo"]][col]
        o["imponibile"] = max(0, i["lordo"] - o["stimate"] - o["deduzione"])
        t = S["tab"][i["periodo"]][fs]
        r = t[0]
        for x in t[1:]:
            if o["imponibile"] > x[0]:
                r = x
        o["riga"] = r
        o["calcolata"] = r[1] + quota(o["imponibile"] - r[0], r[2])
        cr = S["cr"][i["periodo"]]
        o["credito"] = cr[reg] if reg <= 10 else reg * cr[1]
        o["imposta"] = max(0, o["calcolata"] - o["credito"])
    return o


def busta(R, i):
    ytd, F = i.get("ytd", 0), R["fica"]
    f, s = federale(R, i), statale(R, i)
    o = {"lordo": i["lordo"], "fed": f["ritenuta"], "fedDettaglio": f, "statoDettaglio": s, "stato": s["imposta"]}
    o["ssImponibile"] = tra(F["ssBase"] - ytd, 0, i["lordo"])
    o["ss"] = quota(o["ssImponibile"], F["ss"])
    o["medicare"] = quota(i["lordo"], F["med"])
    o["addlImponibile"] = max(0, ytd + i["lordo"] - F["addlSoglia"]) - max(0, ytd - F["addlSoglia"])
    o["addl"] = quota(o["addlImponibile"], F["addl"])
    o["sdi"] = quota(i["lordo"], R["st"][i["stato"]]["sdi"]) if R["st"][i["stato"]].get("sdi") else 0
    o["totale"] = o["fed"] + o["ss"] + o["medicare"] + o["addl"] + o["stato"] + o["sdi"]
    o["netto"] = i["lordo"] - o["totale"]
    return o


def datore(R, stato, lordo, ytd=0, aliquota=None):
    S, F = R["st"][stato], R["fica"]
    o = {"lordo": lordo}
    o["ss"] = quota(tra(F["ssBase"] - ytd, 0, lordo), F["ss"])
    o["medicare"] = quota(lordo, F["med"])
    o["futaAliquota"] = R["futa"]["netta"] + R["futa"]["rid"].get(stato, 0)
    o["futa"] = quota(tra(R["futa"]["base"] - ytd, 0, lordo), o["futaAliquota"])
    o["sutaAliquota"] = S["suta"]["nuovo"] if aliquota is None else aliquota
    o["suta"] = quota(tra(S["suta"]["base"] - ytd, 0, lordo), o["sutaAliquota"])
    o["ett"] = quota(tra(S["ettBase"] - ytd, 0, lordo), S["ett"]) if S.get("ett") else 0
    o["totale"] = o["ss"] + o["medicare"] + o["futa"] + o["suta"] + o["ett"]
    o["costo"] = lordo + o["totale"]
    return o
