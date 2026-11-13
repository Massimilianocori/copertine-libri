"""Legge le serie ufficiali grezze di inflation/dati/grezzi/ e le rende uniformi.

Ogni serie: {"annuale": {anno: indice}, "mensile": {(anno, mese): indice}, "mancanti": {(anno, mese): motivo}, ...}.
Nessuna cifra viene inventata: gli indici sono quelli pubblicati. L'unico valore calcolato da noi è la serie tedesca
"verkettet" prima del 1991 (indice della Germania Ovest × fattore di raccordo, dichiarato nelle pagine).
Usato da genera.py e verifica.py.
"""
import csv
import io
import json
import re
from pathlib import Path

RADICE = Path(__file__).resolve().parent
GREZZI = RADICE / "dati" / "grezzi"
FONTI = json.loads((RADICE / "dati" / "fonti.json").read_text(encoding="utf-8"))
MESI_ONS = {m: i for i, m in enumerate(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"], 1)}
DM_PER_EURO = 1.95583  # tasso di conversione irrevocabile (Regolamento (CE) n. 2866/98 del Consiglio)
ANNO_RACCORDO_DE = 1991


def _num(x):
    x = (x or "").strip()
    return float(x) if re.fullmatch(r"-?\d+(\.\d+)?", x) else None


def bls():
    s = {"annuale": {}, "mensile": {}, "mancanti": {}}
    note = {}
    with open(GREZZI / "bls_api_controllo.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["footnote"]:
                note[(int(r["year"]), int(r["period"][1:]))] = r["footnote"]
    with open(GREZZI / "bls_cpiu.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            a = int(r["year"])
            for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1):
                v = _num(r[m])
                if v is not None:
                    s["mensile"][(a, i)] = v
                elif r[m].strip():  # "-(X)": dato non raccolto
                    s["mancanti"][(a, i)] = note.get((a, i), "Data unavailable (BLS footnote X)")
            if _num(r["annual"]) is not None:
                s["annuale"][a] = _num(r["annual"])
    return s


def bls_api():
    out, mancanti = {}, {}
    with open(GREZZI / "bls_api_controllo.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            k = (int(r["year"]), int(r["period"][1:]))
            v = _num(r["value"])
            if v is None:
                mancanti[k] = r["footnote"]
            else:
                out[k] = v
    return out, mancanti


def ons(cdid):
    s = {"annuale": {}, "mensile": {}, "trimestrale": {}, "mancanti": {}, "meta": {}}
    testo = (GREZZI / f"ons_{cdid}.csv").read_text(encoding="utf-8")
    for r in csv.reader(io.StringIO(testo)):
        if not r:
            continue
        m = re.fullmatch(r"(\d{4})(?: (Q[1-4]|[A-Z]{3}))?", r[0])
        if not m:
            s["meta"][r[0]] = r[1] if len(r) > 1 else ""
            continue
        v = _num(r[1])
        if v is None:
            continue
        a = int(m.group(1))
        if m.group(2) is None:
            s["annuale"][a] = v
        elif m.group(2).startswith("Q"):
            s["trimestrale"][(a, int(m.group(2)[1]))] = v
        else:
            s["mensile"][(a, MESI_ONS[m.group(2)])] = v
    return s


def destatis():
    """VPI Deutschland (2020=100) da lange Reihen (fino a giugno 2025) + tabella attuale (da gennaio 2021);
    Germania Ovest "alle privaten Haushalte" (1995=100). Restituisce anche le variazioni pubblicate (per i controlli)."""
    vpi = {"annuale": {}, "mensile": {}, "mancanti": {}}
    west = {"annuale": {}, "mensile": {}, "mancanti": {}}
    rate_pubbl = {"vpi_jahr": {}, "west_jahr": {}, "vpi_monat": {}}
    lange = {"annuale": {}, "mensile": {}}
    with open(GREZZI / "destatis_lange_reihen.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            v = _num(r["wert"])
            if v is None:
                continue
            a = int(r["jahr"])
            ziel = vpi if r["gebiet"] == "Deutschland" else west
            if r["tabelle"] == "jahr_index":
                ziel["annuale"][a] = v
                if ziel is vpi:
                    lange["annuale"][a] = v
            elif r["tabelle"] == "monat_index":
                ziel["mensile"][(a, int(r["monat"]))] = v
                if ziel is vpi:
                    lange["mensile"][(a, int(r["monat"]))] = v
            elif r["tabelle"] == "jahr_rate":
                rate_pubbl["vpi_jahr" if ziel is vpi else "west_jahr"][a] = v
    tabelle = {"annuale": {}, "mensile": {}}
    with open(GREZZI / "destatis_12kategorien.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            v = _num(r["wert"])
            a = int(r["jahr"])
            if r["tabelle"] == "monat_index":
                tabelle["mensile"][(a, int(r["monat"]))] = v
            elif r["tabelle"] == "jahr_index":
                tabelle["annuale"][a] = v
            elif r["tabelle"] == "monat_rate":
                rate_pubbl["vpi_monat"][(a, int(r["monat"]))] = v
            elif r["tabelle"] == "jahr_rate":
                rate_pubbl["vpi_jahr"].setdefault(a, v)
    # la tabella attuale prevale (è la più recente); le sovrapposizioni sono controllate da verifica.py
    vpi["annuale"].update(tabelle["annuale"])
    vpi["mensile"].update(tabelle["mensile"])
    return vpi, west, rate_pubbl, lange, tabelle


def raccordo_de(vpi, west):
    """Serie unica per il calcolatore tedesco: VPI dal 1991; prima, Germania Ovest × (VPI 1991 / Ovest 1991)."""
    k = vpi["annuale"][ANNO_RACCORDO_DE] / west["annuale"][ANNO_RACCORDO_DE]
    s = {"annuale": dict(vpi["annuale"]), "mensile": dict(vpi["mensile"]), "mancanti": {}, "fattore": k}
    for a, v in west["annuale"].items():
        if a < ANNO_RACCORDO_DE:
            s["annuale"][a] = round(v * k, 3)
    for (a, m), v in west["mensile"].items():
        if a < ANNO_RACCORDO_DE:
            s["mensile"][(a, m)] = round(v * k, 3)
    return s


def ultimo_mese(s):
    return max(s["mensile"])


def tutte():
    us = bls()
    uk_cpi, uk_rpi, uk_rpi87 = ons("d7bt"), ons("cdko"), ons("chaw")
    vpi, west, rate_de, lange, tab_de = destatis()
    de = raccordo_de(vpi, west)
    return {"us": us, "uk_cpi": uk_cpi, "uk_rpi": uk_rpi, "uk_rpi87": uk_rpi87, "uk_cpi_rate": ons("d7g7"), "uk_rpi_rate": ons("czbh"),
            "de_vpi": vpi, "de_west": west, "de": de, "de_rate_pubbl": rate_de, "de_lange": lange, "de_tabelle": tab_de}


def continuita(s, nome, primo_mese=None, primo_anno=None):
    """Errori se mancano anni o mesi tra il primo e l'ultimo (i mesi in s['mancanti'] sono ammessi: dato non raccolto, con motivo)."""
    err = []
    anni = sorted(s["annuale"])
    a0 = primo_anno or anni[0]
    for a in range(a0, anni[-1] + 1):
        if a not in s["annuale"]:
            err.append(f"{nome}: manca l'anno {a}")
    mesi = sorted(set(s["mensile"]) | set(s.get("mancanti", {})))
    if mesi:
        a, m = primo_mese or mesi[0]
        fine = mesi[-1]
        while (a, m) <= fine:
            if (a, m) not in s["mensile"] and (a, m) not in s.get("mancanti", {}):
                err.append(f"{nome}: manca il mese {a}-{m:02d}")
            m += 1
            if m == 13:
                a, m = a + 1, 1
    for k, motivo in s.get("mancanti", {}).items():
        if not motivo:
            err.append(f"{nome}: mese {k} senza motivo")
    return err
