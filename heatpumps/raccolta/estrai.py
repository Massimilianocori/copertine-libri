"""Estrae dagli xlsx ufficiali (raccolta/_grezzi/) le cifre usate dal sito e le scrive in dati/bus.json, dati/solare.json e dati/schemi.json.

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


def _norm(x):
    return re.sub(r"\s+", " ", str(x).replace("\xa0", " ")).strip().lower()


def foglio(wb, *nomi, contiene=None):
    """Foglio per nome (maiuscole, spazi e trattini bassi non contano; più nomi ammessi) oppure, se il nome è cambiato,
    il primo foglio il cui testo contiene tutte le frasi di `contiene`. Se non c'è si ferma: mai un foglio a caso."""
    chiave = lambda x: re.sub(r"[\s_]+", " ", str(x)).strip().lower()
    per_nome = {chiave(n): n for n in wb.sheetnames}
    for n in nomi:
        if chiave(n) in per_nome:
            return wb[per_nome[chiave(n)]]
    if contiene:
        for n in wb.sheetnames:
            t = _norm(testo_foglio(wb[n]))
            if all(_norm(c) in t for c in contiene):
                return wb[n]
    raise SystemExit(f"foglio {' / '.join(nomi)} non trovato (né per nome né per contenuto {contiene}); fogli presenti: {wb.sheetnames}")


def colonna(h, *schemi, senza=None, dove=""):
    """Indice dell'unica colonna la cui intestazione corrisponde a uno degli `schemi` (regex, senza maiuscole) e non a `senza`."""
    hn = [_norm(x) for x in h]
    for sc in schemi:
        k = [i for i, x in enumerate(hn) if x and re.search(sc, x, re.I) and not (senza and re.search(senza, x, re.I))]
        if len(k) == 1:
            return k[0]
        if len(k) > 1:
            raise SystemExit(f"{dove}: più colonne per «{sc}»: {[h[i] for i in k]}")
    raise SystemExit(f"{dove}: colonna «{' | '.join(schemi)}» non trovata; intestazioni: {[x for x in h if x]}")


OSCURATE = re.compile(r"^(N/?A|#|\^|\[[cx]\d?\])$")  # celle oscurate dichiarate nelle note dei file: restano testo, mai stimate


def numero(v, dove, vuoto=False):
    """Numero della cella. Un segno di cella oscurata resta com'è; una cella vuota è ammessa solo con vuoto=True (diventa None);
    qualsiasi altro testo ferma l'estrazione (colonna spostata o formato cambiato)."""
    v = pulisci(v)
    if isinstance(v, bool):
        raise SystemExit(f"{dove}: valore non numerico {v!r}")
    if isinstance(v, (int, float)):
        return v
    if v in (None, ""):
        if vuoto:
            return None
        raise SystemExit(f"{dove}: cella vuota dove serve un numero")
    if OSCURATE.match(str(v)):
        return str(v)
    raise SystemExit(f"{dove}: valore non numerico {v!r}")


def intero(v, dove):
    v = numero(v, dove)
    if not isinstance(v, int):
        raise SystemExit(f"{dove}: atteso un numero intero pubblicato, trovato {v!r}")
    return v


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
        # fino a ottobre 2026 (uscita di settembre): "confirmed funding ... up to 2029/30"; dall'uscita di ottobre 2026: "will maintain ... £400m in 2027/28"
        "fino": (data_in(sb, r"(The Government will maintain the current funding levels at £[\d,.]+ ?(?:m|million) in 20\d\d/\d\d, rising broadly in line with inflation thereafter\.)")
                 or data_in(sb, r"(The Government confirmed funding for further years up to 2029/30 through the Warm Homes Plan in January 2026\.)")),
        "aprile2026": data_in(sb, r"(28 April 2026: [^\n]+)"),
        "luglio2026": data_in(sb, r"(21 July 2026: [^\n]+)"),
        "ottobre2023": data_in(sb, r"(23 October 2023: [^\n]+)"),
        "maggio2024": data_in(sb, r"(8 May 2024: [^\n]+)"),
        "voucher_validi": data_in(sb, r"(AWHP, AAHP and biomass boiler vouchers are valid for 3 months while GSHP vouchers are valid for 6 months\.)"),
        "primo_arrivato": data_in(sb, r"(Vouchers are issued on a first come, first served basis[^\n]*)"),
        "prezzo_pagato": data_in(sb, r"(The price paid by the property owner is the total cost of the installation less the value of the grant\.)"),
    }
    manca = [k for k, v in out["frasi_scheda"].items() if not v]
    if manca or not (out["periodo"] and out["pubblicato"] and out["prossima"]):
        raise SystemExit(f"bus.xlsx: frasi citate non trovate in «Scheme background» {manca} oppure date di copertina mancanti "
                         f"({out['periodo']}, {out['pubblicato']}, {out['prossima']}): rileggere il foglio e correggere estrai.py e i testi")
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
    # colonne cercate dall'intestazione ("<stato>: <tecnologia>"), non per posizione: DESNZ ha già aggiunto una tecnologia (aria-aria)
    h, rr = tabella(wb["1.2A"])
    CAMPI_12A = {"domande": r"^voucher applications received: total$", "buoni": r"^vouchers issued: total$",
                 "pagati_totale": r"^redemptions paid: total$", "pagati_awhp": r"^redemptions paid: air-to-water heat pumps$",
                 "pagati_gshp": r"^redemptions paid: ground source heat pumps$", "pagati_biomassa": r"^redemptions paid: biomass boilers$"}
    k12 = {c: colonna(h, sc, dove="bus 1.2A") for c, sc in CAMPI_12A.items()}
    k12["nome"] = colonna(h, r"^country or region$", dove="bus 1.2A")
    k_pag = [i for i, x in enumerate(h) if re.match(r"^redemptions paid:", _norm(x)) and i != k12["pagati_totale"]]
    reg = {}
    for r in rr:
        if r[0] in REGIONI or r[0] in ("K04000001", "E92000001"):
            reg[r[0]] = {"nome_file": r[k12["nome"]]}
            reg[r[0]].update({c: intero(r[k12[c]], f"bus 1.2A {r[0]} {c}") for c in CAMPI_12A})
            if reg[r[0]]["pagati_totale"] != sum(intero(r[k], f"bus 1.2A {r[0]} pagati") for k in k_pag):
                raise SystemExit(f"bus 1.2A {r[0]}: «Redemptions paid: Total» non è la somma delle colonne per tecnologia: colonne da ricontrollare")
    if len(reg) != 12:
        raise SystemExit(f"bus 1.2A: attese 12 righe (Inghilterra e Galles, Inghilterra, 9 regioni, Galles), trovate {len(reg)}")
    # 1.2B: domestici per 10.000 famiglie (pagati, totale); stesse intestazioni di 1.2A, colonne cercate di nuovo sul suo foglio
    h, rr = tabella(wb["1.2B"])
    kb_pag = colonna(h, r"^redemptions paid: total$", dove="bus 1.2B")
    kb_dom = colonna(h, r"^voucher applications received: total$", dove="bus 1.2B")
    for r in rr:
        if r[0] in reg:
            reg[r[0]]["per10k_pagati"] = numero(r[kb_pag], f"bus 1.2B {r[0]} pagati")
            reg[r[0]]["per10k_domande"] = numero(r[kb_dom], f"bus 1.2B {r[0]} domande")
    if any("per10k_pagati" not in v for v in reg.values()):
        raise SystemExit("bus 1.2B: mancano righe presenti in 1.2A")
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
    # Q1.2 e A1.7 si aggiornano solo a gennaio, aprile, luglio e ottobre: il loro periodo (titolo del foglio) può essere più vecchio
    # di quello mensile della copertina. Il sito deve scrivere questo, non il mese della copertina, accanto alle cifre per council.
    out["periodo_la"] = data_in(testo_foglio(wb["Q1.2"]).split("\n")[0], r"May 2022 to ([A-Z][a-z]+ \d{4})")
    if not out["periodo_la"]:
        raise SystemExit("bus.xlsx Q1.2: periodo non trovato nel titolo del foglio")
    # colonne di Q1.2 e A1.7 dalle intestazioni
    q_reg, q_cont, q_distr = (colonna(h, sc, dove="bus Q1.2") for sc in (r"^country or region$", r"^county or unitary authority$", r"^local authority districts$"))
    q_pompe, q_bio = colonna(h, r"^heat pump technologies", dove="bus Q1.2"), colonna(h, r"^biomass boilers", dove="bus Q1.2")
    k_anni = [i for i, x in enumerate(ha) if re.match(r"^\d{4}/\d\d: heat pump technologies", _norm(x))]
    if len(k_anni) < 4 or colonna(ha, r"^local authority districts$", dove="bus A1.7") > k_anni[0]:
        raise SystemExit(f"bus A1.7: colonne degli anni finanziari non riconosciute: {[x for x in ha if x]}")
    anni_la = [ha[i].split(":")[0].strip() for i in k_anni]
    per_anno = {r[0]: [pulisci(r[i]) for i in k_anni] for r in ra if r[0]}
    aree, regione, contea = [], None, None
    for r in rr:
        if not r[0]:
            continue
        cod = r[0].strip()
        if r[q_reg]:
            regione = cod if cod in REGIONI else None
            contea = None
            continue
        livello = "C" if r[q_cont] else "D"
        nome = (r[q_cont] or r[q_distr]).strip()
        if livello == "C":
            contea = cod
        aree.append({"codice": cod, "nome_file": nome, "livello": livello, "regione": regione,
                     "contea": contea if livello == "D" else None, "cumulato": numero(r[q_pompe], f"bus Q1.2 {cod}"), "biomassa": numero(r[q_bio], f"bus Q1.2 {cod} biomassa"),
                     "anni": dict(zip(anni_la, per_anno.get(cod, [None] * len(anni_la))))})
    # una riga "C" seguita da righe "D" è un raggruppamento (contea a due livelli, contea metropolitana, Inner/Outer London)
    for k, a in enumerate(aree):
        a["ha_distretti"] = a["livello"] == "C" and k + 1 < len(aree) and aree[k + 1]["livello"] == "D"
    out["anni_la"] = anni_la
    out["aree"] = aree
    nazionale = {r[0]: intero(r[q_pompe], f"bus Q1.2 {r[0]}") for r in rr if r[0] in ("K04000001", "E92000001", "W92000004") or r[0] in REGIONI}
    out["cumulato_regioni_pompe"] = nazionale
    out["anni_regioni_pompe"] = {r[0]: dict(zip(anni_la, [intero(r[i], f"bus A1.7 {r[0]}") for i in k_anni])) for r in ra if r[0] in nazionale}
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


# ---------------------------------------------------------------- schemi (13/11/2026): GBIS, Warm Homes: Local Grant, ECO4
def _righe(ws):
    return [tuple(pulisci(c) for c in r) for r in ws.iter_rows(values_only=True)]


def _riga(righe, primo):
    """Prima riga la cui prima cella non vuota è `primo`."""
    for r in righe:
        v = [c for c in r if c not in (None, "")]
        if v and str(v[0]).strip() == primo:
            return v
    raise SystemExit(f"riga «{primo}» non trovata")


GBIS_TIPI = ["Cavity Wall Insulation", "Loft Insulation", "Heating Controls", "Other Insulation", "Solid Wall Insulation"]
WHLG_TIPI = ["Solar PV", "Batteries", "Loft Insulation", "Air Source Heat Pump", "Electric Storage Heating", "Park Home Insulation",
             "Cavity Wall Insulation", "Heating Controls", "Energy Efficient Windows and Doors", "Double or Triple Glazing",
             "External Solid Wall Insulation", "Internal Solid Wall Insulation", "Flat Roof Insulation", "Room in Roof Insulation", "Hybrid Heat Pump"]
ECO4_TIPI = ["Loft Insulation", "Boiler", "First Time Central Heating", "Solid Wall Insulation", "Cavity Wall Insulation", "Solar PV",
             "Air Source Heat Pumps", "Ground Source Heat Pumps", "Hybrid Heat Pumps", "Other Insulation", "Other Heating"]


def schemi():
    out = {}
    # Great British Insulation Scheme (DESNZ, dati Ofgem)
    wb = openpyxl.load_workbook(GREZZI / "gbis.xlsx", read_only=True, data_only=True)
    cont = _righe(wb["Contents"])
    out["gbis"] = {"pubblicato": str(_riga(cont, "Publication date:")[1])[:10], "periodo": _riga(cont, "Data Period:")[1]}
    t2 = _riga(_righe(wb["T2"]), "Total")
    out["gbis"]["famiglie"], out["gbis"]["famiglie_generali"], out["gbis"]["famiglie_basso_reddito"] = t2[1], t2[2], t2[3]
    r3 = _righe(wb["T3"])
    out["gbis"]["misure"] = _riga(r3, "Total number of measures")[1]
    out["gbis"]["tipi"] = {k: _riga(r3, k)[1] for k in GBIS_TIPI}
    out["gbis"]["regioni"] = {}
    for r in _righe(wb["T4"]):
        if r[0] and re.match(r"^[EWSK]\d{8}$", str(r[0])):
            out["gbis"]["regioni"][r[0]] = {"nome": r[1], "misure": r[2], "famiglie": r[4], "famiglie_totali": r[6], "per100k_famiglie": r[8]}
    # Warm Homes: Local Grant (DESNZ, dati dei council)
    wb = openpyxl.load_workbook(GREZZI / "whlg.xlsx", read_only=True, data_only=True)
    tit = testo_foglio(wb["Title"])
    w = {"fino_a": data_in(tit, r"Data covered in this release is to the end of ([A-Z][a-z]+ \d{4})"),
         "aggiornato": data_in(tit, r"This workbook was updated on: (\d{1,2} [A-Z][a-z]+ \d{4})"),
         "prossima": data_in(tit, r"The next update for these statistics is:\s*(\d{4}-\d\d-\d\d)")}
    # il foglio si chiamava "About this release" fino ad agosto 2026, "About this Release" da novembre 2026: si cerca per nome
    # senza badare alle maiuscole e, se cambia ancora, per contenuto
    ab = testo_foglio(foglio(wb, "About this release", contiene=["Warm Homes: Local Grant Background", "Data Completeness"])).replace("\xa0", " ")
    w["piano"] = data_in(ab, r"(The Government has published its Warm Homes Plan to upgrade up to [\d.]+ million homes by \d{4}\.)")
    w["parte_del_piano"] = data_in(ab, r"(The Warm Homes: Local Grant \(WH:LG\) is part of this plan\.)")
    # agosto 2026: "based on data submitted by 67 of these projects"; novembre 2026: "includes valid delivery data reported by 69 of these projects"
    m = re.search(r"There are (\d+) Warm Homes: Local Grant projects, representing (\d+) LAs.*?"
                  r"(?:based on data submitted by|data reported by)\s+(\d+) of these projects", ab, re.S)
    if not m or not all(w[k] for k in ("fino_a", "aggiornato", "prossima", "piano", "parte_del_piano")):
        raise SystemExit(f"WH:LG: frasi o date non trovate nei fogli Title / About this release: { {k: w.get(k) for k in w} }, progetti: {bool(m)}")
    w["progetti"], w["council"], w["progetti_con_dati"] = int(m.group(1)), int(m.group(2)), int(m.group(3))
    # T1: mesi e totale; colonne cercate per intestazione
    h1, r1 = tabella(foglio(wb, "T1"), "First installation month")
    k_m = colonna(h1, r"measures installed", senza=r"percentage|%", dove="WH:LG T1")
    k_f = colonna(h1, r"(households|homes) upgraded", senza=r"percentage|%", dove="WH:LG T1")
    w["mesi"] = {}
    for r in r1:
        r = [pulisci(c) for c in r]
        if r[0] == "Total":
            w["misure"], w["famiglie"] = intero(r[k_m], "WH:LG T1 Total misure"), intero(r[k_f], "WH:LG T1 Total famiglie")
        elif r[0] and re.match(r"^[A-Z][a-z]+ \d{4}$", str(r[0])):
            w["mesi"][r[0]] = {"misure": intero(r[k_m], f"WH:LG T1 {r[0]}"), "famiglie": intero(r[k_f], f"WH:LG T1 {r[0]}")}
    if "misure" not in w or not w["mesi"]:
        raise SystemExit("WH:LG T1: riga Total o mesi non trovati")
    if sum(v["misure"] for v in w["mesi"].values()) != w["misure"] or sum(v["famiglie"] for v in w["mesi"].values()) != w["famiglie"]:
        raise SystemExit("WH:LG T1: la somma dei mesi non dà il totale: colonne da ricontrollare")
    if list(w["mesi"])[-1] != w["fino_a"]:
        raise SystemExit(f"WH:LG: l'ultimo mese di T1 ({list(w['mesi'])[-1]}) non è il periodo della copertina ({w['fino_a']})")
    # T2: tipi di misura. Da novembre 2026 il costo medio è la 5ª colonna (era la 7ª) e le case la 6ª (era la 5ª): si legge l'intestazione.
    h2, r2 = tabella(foglio(wb, "T2"), "Measure group")
    k_tipo = colonna(h2, r"^measure type", dove="WH:LG T2")
    k_m = colonna(h2, r"measures installed", senza=r"percentage|%|cost|homes|households", dove="WH:LG T2")
    k_c = colonna(h2, r"average \(mean\) total measure cost", r"average.*cost", dove="WH:LG T2")
    k_f = colonna(h2, r"(homes|households) with measures installed", senza=r"percentage|%", dove="WH:LG T2")
    r2 = [[pulisci(c) for c in r] for r in r2]
    w["tipi"] = {}
    for k in WHLG_TIPI:
        for r in r2:
            if len(r) > max(k_tipo, k_m, k_c, k_f) and r[k_tipo] == k:
                w["tipi"][k] = {"misure": intero(r[k_m], f"WH:LG T2 {k} misure"), "famiglie": intero(r[k_f], f"WH:LG T2 {k} case"),
                                "costo_medio": numero(r[k_c], f"WH:LG T2 {k} costo")}
                break
        else:
            raise SystemExit(f"WH:LG: tipo {k} non trovato")
    tot2 = next((r for r in r2 if r[0] == "Total"), None)
    if not tot2:
        raise SystemExit("WH:LG T2: riga Total non trovata")
    w["costo_medio_tutte"] = numero(tot2[k_c], "WH:LG T2 Total costo")
    if not isinstance(w["costo_medio_tutte"], (int, float)):
        raise SystemExit(f"WH:LG T2: costo medio di tutte le misure non pubblicato ({w['costo_medio_tutte']!r})")
    if intero(tot2[k_m], "WH:LG T2 Total misure") != w["misure"] or intero(tot2[k_f], "WH:LG T2 Total case") != w["famiglie"]:
        raise SystemExit("WH:LG: i totali di T2 non coincidono con T1: colonne da ricontrollare")
    # T3: regioni
    h3, r3 = tabella(foglio(wb, "T3"), "Geographic region code")
    k_f = colonna(h3, r"^total households with at least one", senza=r"%|percentage", dove="WH:LG T3")
    k_p = colonna(h3, r"^average measures installed per household", dove="WH:LG T3")
    k_m = colonna(h3, r"^total .*measures installed", senza=r"%|percentage|households", dove="WH:LG T3")
    w["regioni"] = {}
    for r in r3:
        r = [pulisci(c) for c in r]
        if r[0] and re.match(r"^E1\d{7}$", str(r[0])):
            w["regioni"][r[0]] = {"nome": r[1], "famiglie": intero(r[k_f], f"WH:LG T3 {r[1]}"),
                                  "misure_per_famiglia": numero(r[k_p], f"WH:LG T3 {r[1]}"), "misure": intero(r[k_m], f"WH:LG T3 {r[1]}")}
    if (len(w["regioni"]) != 9 or sum(v["famiglie"] for v in w["regioni"].values()) != w["famiglie"]
            or sum(v["misure"] for v in w["regioni"].values()) != w["misure"]):
        raise SystemExit("WH:LG T3: le 9 regioni non sommano al totale di T1: colonne da ricontrollare")
    out["whlg"] = w
    # ECO4 (DESNZ, Household Energy Efficiency statistics, tabella 1.6)
    wb = openpyxl.load_workbook(GREZZI / "hee.xlsx", read_only=True, data_only=True)
    tit = testo_foglio(wb["Title"])
    e = {"fino_a": data_in(tit, r"Data covered in this release is for delivery to the end of ([A-Z][a-z]+ \d{4})"),
         "pubblicato": data_in(tit, r"were published at [\d:apm]+ [A-Z][a-z]+ (\d{1,2} [A-Z][a-z]+ \d{4})")}
    h, rr = tabella(wb["T1.6"], "Measure Types")
    col = next(i for i, x in enumerate(h) if x.startswith("Total number of Surplus Actions, ECO3 Interim and ECO4 measures delivered"))
    righe = {str(r[0]).strip(): pulisci(r[col]) for r in rr if r[0]}
    e["colonna"] = h[col]
    e["misure"] = righe["Total number of measures"]
    e["case"] = righe["Total number of unique properties"]
    e["tipi"] = {k: righe[k] for k in ECO4_TIPI}
    if not (e["fino_a"] and e["pubblicato"]):
        raise SystemExit(f"hee.xlsx: periodo o data di pubblicazione non trovati nel foglio Title ({e['fino_a']}, {e['pubblicato']})")
    for k, v in [("misure", e["misure"]), ("case", e["case"])] + list(e["tipi"].items()):
        intero(v, f"hee.xlsx T1.6 {k}")
    out["eco4"] = e
    return out


def main():
    b = bus()
    s = solare()
    (DATI / "bus.json").write_text(json.dumps(b, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    (DATI / "solare.json").write_text(json.dumps(s, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    sc = schemi()
    (DATI / "schemi.json").write_text(json.dumps(sc, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print(f"schemi.json: GBIS {sc['gbis']['famiglie']} famiglie, WH:LG a {sc['whlg']['fino_a']}, ECO4 a {sc['eco4']['fino_a']}")
    print(f"bus.json: {b['periodo']}, pubblicato {b['pubblicato']}, {len(b['aree'])} aree; solare.json: {len(s['la'])} enti locali, "
          f"ET 6.3 {s['et63_pubblicato']}, costi {s['costi_pubblicato']}")


if __name__ == "__main__":
    main()
