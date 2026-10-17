"""Legge le pagine HTML salvate da scarica.py e scrive i dati puliti in fhacondos/dati/.

Uso (dalla radice del repository):
    python3 fhacondos/raccolta/estrai.py                     # ultima edizione completa in cache/
    python3 fhacondos/raccolta/estrai.py --edizione 2026-10-17

Scrive:
  dati/condomini.json  tutti i condomini (approvati + scaduti/ritirati recenti), campi puliti, senza il testo libero
  dati/conteggi.json   totali dichiarati dal modulo HUD per Stato e tipo, data "as of", righe lette
Si ferma con errore se le righe lette non coincidono con i totali dichiarati dal modulo (pagina mancante o cambiata).

Cosa NON si pubblica: il testo libero "Composition of Project" e i commenti (possono contenere sigle di funzionari,
nomi di referenti o note interne). Dal testo libero si ricava solo il numero di unità, con regole prudenti
(vedi numero_unita): se il testo è ambiguo il numero resta vuoto.
"""
import argparse
import html
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scarica import CACHE, STATI  # noqa: E402

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"

RE_RIGA = re.compile(r'<tr>\s*<td width="10%" align="left" valign="top">(.*?)</tr>', re.S)
RE_CELLA = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
RE_ID = re.compile(r"\b([A-Z]\d{6})\b\s*(\d{3})?")
RE_ASOF = re.compile(r"as of (\d{2}/\d{2}/\d{4})")
RE_CITTA = re.compile(r"^(.*?),?\s+([A-Z]{2})\s+(\d{5})(?:-?\d{4})?$")
RE_CITTA_NOZIP = re.compile(r"^(.*?),\s*([A-Z]{2})\s*$")
# Numero seguito (al massimo dopo due parole descrittive) da "unit"/"units": "48 UNITS", "143 RESIDENTIAL CONDO UNITS",
# "ALL (160) UNITS". Le forme con "total" hanno la precedenza: "168 total units", "Total of 100 units",
# "TOTAL NUMBER OF UNITS IN PROJECT IS 204".
RE_UNITA = re.compile(r"(?<![\d,#/-])\(?(\d{1,3}(?:,\d{3})|\d{1,4})\)?(?:\s*-\s*|\s+)((?:[a-z.'/-]+\s+){0,2}?)units?\b(?!\s*(?:per|each|in each|/))",
                      re.I)
RE_TOTALE = [
    re.compile(r"(\d{1,4})\s+total\s+(?:[a-z.'/-]+\s+){0,3}?units?\b", re.I),
    re.compile(r"total\s+(?:of\s+)?(\d{1,4})\s+(?:[a-z.'/-]+\s+){0,3}?units?\b", re.I),
    re.compile(r"total\s+(?:number\s+of\s+)?units\s+(?:in\s+(?:the\s+)?project\s*)?(?:is|of|=|:)?\s*(\d{1,4})\b", re.I),
]
# parole che, subito prima del numero, indicano un numero di edificio/fase/lotto e non un conteggio ("BLDG 2 UNITS 101-108")
PAROLE_PRIMA_NO = {"bldg", "bldgs", "building", "buildings", "phase", "phases", "ph", "lot", "lots", "no", "number", "unit",
                   "units", "#", "suite", "apt", "to", "thru", "through", "tower", "id"}
# parole che non possono stare tra il numero e "units" (sono un altro conteggio: "9 buildings units")
PAROLE_IN_MEZZO_NO = {"building", "buildings", "bldg", "bldgs", "phase", "phases", "story", "stories", "lot", "lots", "per"}


def testo(cella):
    c = re.sub(r"<br\s*/?>", "\n", cella, flags=re.I)
    c = re.sub(r"<[^>]+>", " ", c)
    c = html.unescape(c).replace("\xa0", " ")
    righe = [re.sub(r"\s+", " ", r).strip() for r in c.split("\n")]
    return "\n".join(r for r in righe if r)


def data_iso(s):
    m = re.search(r"(\d{2})/(\d{2})/(\d{4})", s or "")
    if not m:
        return None
    return f"{m.group(3)}-{m.group(1)}-{m.group(2)}"


def numero_unita(comp):
    """Numero di unità dal testo libero, con regole prudenti (altrimenti None):
    1. se c'è una forma con "total" e dà un solo numero, si usa quello;
    2. altrimenti si usa il numero se nel testo c'è un solo numero distinto seguito da "units", non preceduto da parole come
       BLDG, PHASE, LOT (es. 'BLDG 2 UNITS 101-108' non dà 2) e non seguito da "per"/"each" ("12 units per building")."""
    if not comp:
        return None
    tot = {int(m.group(1)) for r in RE_TOTALE for m in r.finditer(comp)}
    tot = {n for n in tot if 1 <= n <= 5000}
    if len(tot) == 1:
        return tot.pop()
    trovati = set()
    for m in RE_UNITA.finditer(comp):
        prima = comp[:m.start()].split()
        if prima and prima[-1].lower() in PAROLE_PRIMA_NO:
            continue
        mezzo = {w.lower().strip(".,:") for w in m.group(2).split()}
        if mezzo & PAROLE_IN_MEZZO_NO:
            continue
        n = int(m.group(1).replace(",", ""))
        if 1 <= n <= 5000:
            trovati.add(n)
    if len(trovati) == 1:
        return trovati.pop()
    return None


def analizza_riga(r):
    # RE_RIGA cattura la riga dopo il primo <td ...>: lo si rimette per leggere tutte le celle
    celle = RE_CELLA.findall('<td width="10%" align="left" valign="top">' + r)
    if len(celle) < 13:
        raise ValueError(f"riga con {len(celle)} celle")
    nome = testo(celle[0]).split("\n")[0]
    m = RE_ID.search(testo(celle[1]))
    if not m:
        raise ValueError("ID mancante")
    indirizzo = testo(celle[2]).split("\n")
    via, citta, st, cap = "", "", "", ""
    ultima = indirizzo[-1] if indirizzo else ""
    mc = RE_CITTA.match(ultima) or None
    if mc:
        citta, st, cap = mc.group(1).strip(" ,"), mc.group(2), mc.group(3)
        via = " ".join(indirizzo[:-1])
    else:
        mn = RE_CITTA_NOZIP.match(ultima)
        if mn:
            citta, st = mn.group(1).strip(), mn.group(2)
            via = " ".join(indirizzo[:-1])
        else:
            via = " ".join(indirizzo)
    if cap == "00000":
        cap = ""
    comp = testo(celle[4]).replace("\n", " ")
    conc = testo(celle[6])
    mconc = re.search(r"(\d+(?:\.\d+)?)\s*%", conc)
    return {
        "id": m.group(1),
        "sub": m.group(2) or "",
        "nome_raw": nome,
        "via_raw": via,
        "citta_raw": citta,
        "stato_ind": st,
        "cap": cap,
        "contea_raw": testo(celle[3]),
        "unita": numero_unita(comp),
        "comp_raw": comp,  # solo per ricavare le unità e per i controlli: NON va in dati/ né nelle pagine
        "manufactured": testo(celle[5]),
        "fha_pct": float(mconc.group(1)) if mconc else None,
        "metodo": testo(celle[7]),
        "documenti": testo(celle[8]).replace("\n", " "),
        "stato": testo(celle[9]),
        "data_stato": data_iso(testo(celle[11])),
        "scadenza": data_iso(testo(celle[12])),
    }


def analizza_pagina(t):
    righe = [analizza_riga(r) for r in RE_RIGA.findall(t)]
    m = RE_ASOF.search(t)
    return righe, (data_iso(m.group(1)) if m else None)


def ultima_edizione():
    ed = sorted(p.name for p in CACHE.iterdir() if p.is_dir() and (p / "completo.json").exists())
    if not ed:
        sys.exit("Nessuna edizione completa in cache/: lanciare prima raccolta/scarica.py")
    return ed[-1]


def leggi_edizione(cartella, tipi=("A", "E", "W"), stati=None):
    condomini, conteggi, asof = [], {}, Counter()
    for tipo in tipi:
        for st in (stati or STATI):
            f = cartella / tipo / f"{st}.json"
            if not f.exists():
                raise SystemExit(f"Manca {f}: scarico incompleto")
            info = json.loads(f.read_text())
            righe = []
            for p in info["pagine"]:
                r, a = analizza_pagina((cartella / tipo / st / p).read_text(encoding="latin-1"))
                righe += r
                if a:
                    asof[a] += 1
            ids = [x["id"] for x in righe]
            if len(righe) != info["totale_dichiarato"] or len(set(ids)) != len(ids):
                raise SystemExit(f"{tipo} {st}: lette {len(righe)} righe ({len(set(ids))} ID distinti), "
                                 f"il modulo ne dichiara {info['totale_dichiarato']}")
            for x in righe:
                x["st"] = st
                x["tipo"] = tipo
            conteggi.setdefault(tipo, {})[st] = info["totale_dichiarato"]
            condomini += righe
    return condomini, conteggi, asof


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edizione", default="")
    a = ap.parse_args()
    ed = a.edizione or ultima_edizione()
    cartella = CACHE / ed
    condomini, conteggi, asof = leggi_edizione(cartella)
    # Un condominio approvato non deve comparire anche tra scaduti/ritirati (il modulo dà uno stato per progetto).
    approvati = {c["id"] for c in condomini if c["tipo"] == "A"}
    doppi = [c for c in condomini if c["tipo"] != "A" and c["id"] in approvati]
    condomini = [c for c in condomini if not (c["tipo"] != "A" and c["id"] in approvati)]
    data_hud = asof.most_common(1)[0][0]
    DATI.mkdir(exist_ok=True)
    # il testo libero serve solo a ricavare le unità: non si salva nemmeno in dati/ (resta nella cache, fuori da git)
    pubblici = [{k: v for k, v in c.items() if k != "comp_raw"} for c in condomini]
    (DATI / "condomini.json").write_text(json.dumps(pubblici, ensure_ascii=False, separators=(",", ":")))
    meta = {"edizione": ed, "hud_as_of": data_hud, "date_as_of_viste": dict(asof), "conteggi_modulo": conteggi,
            "righe_lette": len(condomini) + len(doppi), "doppi_tolti": len(doppi),
            "estratto_il": datetime.now().strftime("%Y-%m-%d %H:%M")}
    (DATI / "conteggi.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False))
    n = Counter(c["tipo"] for c in condomini)
    senza_unita = sum(1 for c in condomini if c["tipo"] == "A" and c["unita"] is None)
    print(f"Edizione {ed}, HUD as of {data_hud}: {n['A']} approvati, {n['E']} scaduti recenti, {n['W']} ritirati recenti "
          f"({len(doppi)} doppi tolti); approvati senza numero di unità: {senza_unita}")


if __name__ == "__main__":
    main()
