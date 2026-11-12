"""Estrae dai quattro xlsx ufficiali (raccolta/_grezzi/) le cifre usate dal sito e le scrive in dati/bus.json e dati/solare.json.

Uso (dalla radice del repository, dopo raccolta/fonti.py):
    python3 heatpumps/raccolta/estrai.py

Le celle oscurate dei file ufficiali ([c1], [c2], [c3], [x]) restano come testo: il sito non le stima mai.
verifica.py rilegge gli stessi xlsx con un codice suo e ricontrolla ogni cifra stampata.
"""
import json
import re
from pathlib import Path

import openpyxl

RADICE = Path(__file__).resolve().parent.parent
GREZZI = Path(__file__).resolve().parent / "_grezzi"
DATI = RADICE / "dati"

REGIONI = {  # codice ONS -> nome usato nel sito
    "E12000001": "North East", "E12000002": "North West", "E12000003": "Yorkshire and the Humber", "E12000004": "East Midlands",
    "E12000005": "West Midlands", "E12000006": "East of England", "E12000007": "London", "E12000008": "South East",
    "E12000009": "South West", "W92000004": "Wales", "S92000003": "Scotland", "N92000002": "Northern Ireland",
}
# nomi delle regioni nei vari file -> codice
NOMI_REGIONE = {
    "North East": "E12000001", "North West": "E12000002", "Yorkshire and the Humber": "E12000003", "Yorkshire and The Humber": "E12000003",
    "Yorkshire and Humber": "E12000003", "East Midlands": "E12000004", "West Midlands": "E12000005", "East": "E12000006",
    "East of England": "E12000006", "Eastern": "E12000006", "London": "E12000007", "South East": "E12000008", "South West": "E12000009",
    "Wales": "W92000004", "Scotland": "S92000003", "Northern Ireland": "N92000002",
}


def tabella(ws, prima="Area Codes", col=0):
    """Intestazione e righe di una tabella che inizia con la cella `prima` nella colonna `col`."""
    righe = list(ws.iter_rows(values_only=True))
    i = next(k for k, r in enumerate(righe) if r[col] is not None and str(r[col]).strip().startswith(prima))
    return [str(c).strip() if c is not None else "" for c in righe[i]], righe[i + 1:]


def pulisci(v):
    if isinstance(v, float) and v.is_integer():
        return int(v)
    if isinstance(v, str):
        return v.strip()
    return v


def testo_foglio(ws):
    return "\n".join(" ".join(str(c) for c in r if c is not None) for r in ws.iter_rows(values_only=True))


def data_in(testo, schema):
    m = re.search(schema, testo)
    return m.group(1) if m else None


MESI = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                                    "November", "December"], 1)}


def iso(gg, mese, anno):
    return f"{int(anno):04d}-{MESI[mese]:02d}-{int(gg):02d}"


def leggi_data(testo, prefisso):
    m = re.search(prefisso + r"\s+(?:[A-Z][a-z]+day\s+)?(\d{1,2})(?:st|nd|rd|th)?\s+([A-Z][a-z]+)\s+(\d{4})", testo)
    return iso(*m.groups()) if m else None


def bus():
    wb = openpyxl.load_workbook(GREZZI / "bus.xlsx", read_only=True, data_only=True)
    out = {}
    cop = testo_foglio(wb["Cover Sheet"])
    out["titolo"] = cop.split("\n")[0].replace("\n", " ")
    out["periodo"] = data_in(cop, r"England and Wales: ([A-Z][a-z]+ \d{4})")
    out["pubblicato"] = leggi_data(cop, r"These statistics were published on")
    out["prossima"] = leggi_data(cop, r"These statistics will next be published on")
    sb = testo_foglio(wb["Scheme background"])
    out["frasi_scheda"] = {
        "budget": data_in(sb, r"(The scheme is in its fifth year, with a budget of £400 million for 2026/27\.)"),
        "pagato": data_in(sb, r"(Across the first four years of the scheme, over £560 million was paid out through grants\.)"),
        "fino": data_in(sb, r"(The Government confirmed funding for further years up to 2029/30 through the Warm Homes Plan in January 2026\.)"),
        "aprile2026": data_in(sb, r"(28 April 2026: [^\n]+)"),
        "luglio2026": data_in(sb, r"(21 July 2026: [^\n]+)"),
        "ottobre2023": data_in(sb, r"(23 October 2023: [^\n]+)"),
        "maggio2024": data_in(sb, r"(8 May 2024: [^\n]+)"),
        "voucher_validi": data_in(sb, r"(AWHP, AAHP and biomass boiler vouchers are valid for 3 months while GSHP vouchers are valid for 6 months\.)"),
        "primo_arrivato": data_in(sb, r"(Vouchers are issued on a first come, first served basis[^\n]*)"),
        "prezzo_pagato": data_in(sb, r"(The price paid by the property owner is the total cost of the installation less the value of the grant\.)"),
    }
    com = testo_foglio(wb["Commentary"])
    out["commento"] = [r.strip() for r in com.split("\n") if re.match(r"^[a-z]\) ", r.strip())]

    # Tabella 1.1: totali per stato e tecnologia
    h, rr = tabella(wb["1.1"], "Status")
    t11 = {}
    for r in rr:
        if r[0] in ("Voucher applications received", "Vouchers issued", "Redemption applications received", "Redemptions paid") and r[0] not in t11:
            t11[r[0]] = {"awhp": r[1], "aahp": r[2], "gshp": r[3], "sgl": r[4], "biomassa": r[5], "totale": r[6]}
    out["t11"] = t11

    # M1.1: mesi, totali di Inghilterra e Galles
    h, rr = tabella(wb["M1.1"], "Voucher status")
    hm = [x.replace("\n", " ") for x in h]
    m11 = {}
    for r in rr:
        if r[0] and r[1]:
            m11.setdefault(r[0].strip(), {})[r[1].strip()] = {hm[k]: pulisci(r[k]) for k in range(2, len(hm))
                                                              if re.match(r"^[A-Z][a-z]{2} \d{4}$", hm[k])}
    out["m11"] = m11

    # 1.2A: regioni, tutte le tecnologie (domande, buoni emessi, pagati)
    h, rr = tabella(wb["1.2A"])
    reg = {}
    for r in rr:
        if r[0] in REGIONI or r[0] in ("K04000001", "E92000001"):
            reg[r[0]] = {"nome_file": r[1], "domande": r[7], "buoni": r[13], "pagati_totale": r[25], "pagati_awhp": r[20], "pagati_gshp": r[22],
                         "pagati_biomassa": r[24]}
    # 1.2B: domestici per 10.000 famiglie (pagati, totale)
    h, rr = tabella(wb["1.2B"])
    for r in rr:
        if r[0] in reg:
            reg[r[0]]["per10k_pagati"] = r[25]
            reg[r[0]]["per10k_domande"] = r[7]
    # M1.2: domande (pompe di calore) e pagati per mese e regione
    ws = wb["M1.2"]
    righe = list(ws.iter_rows(values_only=True))
    i = next(k for k, r in enumerate(righe) if r[0] == "Status")
    hm = [str(c).replace("\n", " ").strip() if c else "" for c in righe[i]]
    for r in righe[i + 1:]:
        if r[0] in ("Voucher applications received", "Redemptions paid") and r[1] in reg:
            serie = {hm[k]: r[k] for k in range(3, len(hm)) if hm[k] and re.match(r"^[A-Z][a-z]{2} \d{4}$", hm[k])}
            reg[r[1]]["mesi_" + ("domande" if r[0].startswith("Voucher") else "pagati")] = serie
    out["regioni"] = reg

    # A1.9: pagati per combustibile sostituito, regione e anno finanziario
    h, rr = tabella(wb["A1.9"], "Financial year")
    comb = {}
    for r in rr:
        if not r[0] or r[1] not in reg:
            continue
        d = {}
        for k in range(3, len(h)):
            if not h[k]:
                continue
            fuel = h[k].split(":")[0].strip()
            v = r[k]
            if isinstance(v, (int, float)):
                d[fuel] = d.get(fuel, 0) + v
        comb.setdefault(r[1], {})[r[0]] = d
    out["combustibile_regione"] = comb

    # 1.3 e 1.6: nazionali
    h, rr = tabella(wb["1.3"], "Fuel type displaced")
    out["t13"] = {r[0]: {"numero": r[11], "quota": r[12]} for r in rr if r[0] and r[0] != "Fuel type displaced" and isinstance(r[11], (int, float))}
    h, rr = tabella(wb["1.6"], "On/off gas grid")
    out["t16"] = {r[0]: {"numero": r[11], "quota": r[12]} for r in rr if r[0] and isinstance(r[11], (int, float))}

    # Q1.1A: costi trimestrali (nominali)
    h, rr = tabella(wb["Q1.1A"], "Technology type")
    trimestri = [x.replace("\n", " ") for x in h[2:] if x]
    costi = {}
    for r in rr:
        if not r[0] or not r[1]:
            continue
        costi.setdefault(r[0].strip(), {})[r[1].strip()] = dict(zip(trimestri, [pulisci(v) for v in r[2:2 + len(trimestri)]]))
    out["costi_trimestre"] = costi
    out["trimestri"] = trimestri
    # Q1.1B: reali
    h, rr = tabella(wb["Q1.1B"], "Technology type")
    tr_b = [x.replace("\n", " ") for x in h[2:] if x]
    reali = {}
    for r in rr:
        if r[0] and r[1]:
            reali.setdefault(r[0].strip(), {})[r[1].strip()] = dict(zip(tr_b, [pulisci(v) for v in r[2:2 + len(tr_b)]]))
    out["costi_reali"] = reali
    out["costi_reali_base"] = data_in(testo_foglio(wb["Q1.1B"]), r"in (20\d\d Q\d) prices")
    # A1.3A: per fascia di potenza e anno finanziario
    h, rr = tabella(wb["A1.3A"], "Technology type")
    fasce = {}
    anni = []
    for k in range(2, len(h), 2):
        if h[k]:
            anni.append(h[k].split(":")[0].strip())
    for r in rr:
        if not r[0] or not r[1]:
            continue
        d = {}
        for j, a in enumerate(anni):
            d[a] = {"mediana": pulisci(r[2 + 2 * j]), "numero": pulisci(r[3 + 2 * j])}
        fasce.setdefault(r[0].strip(), {})[r[1].strip()] = d
    out["costi_fasce"] = fasce
    out["anni_fasce"] = anni

    # Q1.2 (cumulato) e A1.7 (per anno finanziario): enti locali
    h, rr = tabella(wb["Q1.2"])
    ha, ra = tabella(wb["A1.7"])
    anni_la = [x.split(":")[0].strip() for x in ha[4:] if x]
    per_anno = {r[0]: [pulisci(v) for v in r[4:4 + len(anni_la)]] for r in ra if r[0]}
    aree, regione, contea = [], None, None
    for r in rr:
        if not r[0]:
            continue
        cod = r[0].strip()
        if r[1]:
            regione = cod if cod in REGIONI else None
            contea = None
            continue
        livello = "C" if r[2] else "D"
        nome = (r[2] or r[3]).strip()
        if livello == "C":
            contea = cod
        aree.append({"codice": cod, "nome_file": nome, "livello": livello, "regione": regione,
                     "contea": contea if livello == "D" else None, "cumulato": pulisci(r[4]), "biomassa": pulisci(r[5]),
                     "anni": dict(zip(anni_la, per_anno.get(cod, [None] * len(anni_la))))})
    # una riga "C" seguita da righe "D" è un raggruppamento (contea a due livelli, contea metropolitana, Inner/Outer London)
    for k, a in enumerate(aree):
        a["ha_distretti"] = a["livello"] == "C" and k + 1 < len(aree) and aree[k + 1]["livello"] == "D"
    out["anni_la"] = anni_la
    out["aree"] = aree
    nazionale = {r[0]: pulisci(r[4]) for r in rr if r[0] in ("K04000001", "E92000001", "W92000004") or r[0] in REGIONI}
    out["cumulato_regioni_pompe"] = nazionale
    out["anni_regioni_pompe"] = {r[0]: dict(zip(anni_la, [pulisci(v) for v in r[4:4 + len(anni_la)]])) for r in ra if r[0] in nazionale}
    return out


def solare():
    out = {}
    wb = openpyxl.load_workbook(GREZZI / "solare_la.xlsx", read_only=True, data_only=True)
    cop = testo_foglio(wb["Cover sheet"])
    out["la_pubblicato"] = leggi_data(cop, r"This data was published on")
    out["la_prossima"] = leggi_data(cop, r"The next publication will be on")
    note = testo_foglio(wb["Notes"])
    out["la_nota_12"] = data_in(note, r"Note 12 (Installations are assigned[^\n]+)")
    la = {}
    for anno in range(2014, 2026):
        for tipo, foglio in (("siti", f"LA - Sites {anno}"), ("mw", f"LA - Capacity, {anno}")):
            h, rr = tabella(wb[foglio], "Local Authority Code")
            k_sol = next(i for i, x in enumerate(h) if x.startswith("Solar PV"))
            for r in rr:
                if not r[0] or not str(r[0])[:1] in "ESWN" or not re.match(r"^[ESWN]\d{8}$", str(r[0]).strip()):
                    if r[0] and str(r[0]).startswith(("Unallocated", "Grand Total")):
                        la.setdefault(str(r[0]).split(" [")[0], {"nome": str(r[0]).split(" [")[0]}).setdefault(tipo, {})[anno] = pulisci(r[k_sol])
                    continue
                cod = str(r[0]).strip()
                d = la.setdefault(cod, {"nome": str(r[1]).strip(), "regione_file": str(r[2]).strip(), "paese": str(r[3]).strip()})
                if anno == 2025:
                    d["famiglie"] = pulisci(r[4])
                    d["nome"] = str(r[1]).strip()
                d.setdefault(tipo, {})[anno] = pulisci(r[k_sol])
    out["la"] = la

    wb = openpyxl.load_workbook(GREZZI / "solare_et63.xlsx", read_only=True, data_only=True)
    cop = testo_foglio(wb["Cover_sheet"])
    out["et63_titolo"] = cop.split("\n")[0]
    out["et63_pubblicato"] = leggi_data(cop, r"This data was published on")
    out["et63_prossima"] = leggi_data(cop, r"These tables will be updated on")
    righe = list(wb["Table_4_by_Region"].iter_rows(values_only=True))
    reg = {}
    blocco = None
    mesi = None
    for r in righe:
        if r[0] and str(r[0]).startswith("CUMULATIVE CAPACITY"):
            blocco, mesi = "mw", [str(x).replace("\n", " ").replace("  ", " ").strip() for x in r[1:] if x]
            continue
        if r[0] and str(r[0]).startswith("CUMULATIVE COUNT"):
            blocco, mesi = "numero", [str(x).replace("\n", " ").replace("  ", " ").strip() for x in r[1:] if x]
            continue
        if blocco and r[0] and str(r[0]).strip() in NOMI_REGIONE:
            cod = NOMI_REGIONE[str(r[0]).strip()]
            reg.setdefault(cod, {})[blocco] = dict(zip(mesi[-25:], [pulisci(v) for v in r[1:1 + len(mesi)]][-25:]))
        if blocco and r[0] and str(r[0]).strip() == "TOTAL":
            reg.setdefault("UK", {})[blocco] = dict(zip(mesi[-25:], [pulisci(v) for v in r[1:1 + len(mesi)]][-25:]))
    out["regioni_et63"] = reg
    com = testo_foglio(wb["Commentary"])
    out["et63_commento"] = [x.strip() for x in com.split("\n") if x.strip().startswith(("There are now", "During ", "Over the course of 2025", "The bulk of"))]

    wb = openpyxl.load_workbook(GREZZI / "solare_costi_tic.xlsx", read_only=True, data_only=True)
    cop = testo_foglio(wb["Cover sheet"])
    out["costi_titolo"] = cop.split("\n")[0]
    out["costi_pubblicato"] = leggi_data(cop, r"These data were published on")
    out["costi_prossima"] = leggi_data(cop, r"The next publication date is")
    h, rr = tabella(wb["Summary table (TIC)"], "Financial year")
    out["costi_sommario"] = {r[0]: {"mediana_0_4": r[1], "media_0_4": r[3], "mediana_4_10": r[5], "media_4_10": r[7], "mediana_10_50": r[9],
                                    "media_10_50": r[11]} for r in rr if r[0] and re.match(r"^\d{4}/\d\d$", str(r[0]))}
    h, rr = tabella(wb["Regional costs (TIC)"], "Financial year")
    rc = {}
    for r in rr:
        if r[0] and str(r[1]).strip() in NOMI_REGIONE:
            rc.setdefault(NOMI_REGIONE[str(r[1]).strip()], {})[r[0]] = {
                "n": r[2], "media_tutte": r[5], "n_0_4": r[6], "media_0_4": r[7], "n_4_10": r[8], "media_4_10": r[9], "n_10_50": r[10], "media_10_50": r[11]}
    out["costi_regioni"] = rc
    h, rr = tabella(wb["Domestic costs (TIC)"], "Financial year")
    out["costi_domestici"] = {f"{r[0]} {r[1]}": {"n": r[2], "media_tutte": r[5], "media_0_4": r[7], "media_4_10": r[9]} for r in rr if r[0]}
    return out


def main():
    b = bus()
    s = solare()
    (DATI / "bus.json").write_text(json.dumps(b, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    (DATI / "solare.json").write_text(json.dumps(s, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print(f"bus.json: {b['periodo']}, pubblicato {b['pubblicato']}, {len(b['aree'])} aree; solare.json: {len(s['la'])} enti locali, "
          f"ET 6.3 {s['et63_pubblicato']}, costi {s['costi_pubblicato']}")


if __name__ == "__main__":
    main()
