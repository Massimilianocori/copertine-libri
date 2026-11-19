"""Scarica i prezzi settimanali EIA del gasolio da riscaldamento e del propano (prezzo al consumo, per Stato) e scrive dati/eia_prezzi.json.

Uso (dalla radice del repository), ogni settimana da ottobre a marzo dopo l'uscita EIA (di norma il mercoledì; la data della prossima uscita
è in dati/eia_prezzi.json e in fondo alle tabelle EIA):
    python3 -I inflation/raccolta/eia.py            # scarica, controlla, aggiorna i file solo se tutti i controlli passano
    python3 -I inflation/raccolta/eia.py --locale   # non scarica: rilegge i file già in dati/grezzi/eia/ e riscrive dati/eia_prezzi.json
    python3 -I inflation/raccolta/eia.py --accetta-revisioni   # solo se l'EIA ha rivisto settimane più vecchie delle ultime due: le elenca e le accetta

Fonte: U.S. Energy Information Administration (EIA), "Weekly Heating Oil and Propane Prices" (State Heating Oil and Propane Program):
due file XLS con tutta la storia dal 1990 (dollari per gallone, tasse escluse), le due tabelle HTML con le ultime 6 settimane, la pagina
"Heating Oil and Propane Update" (variazione sulla settimana e sull'anno prima), la pagina delle definizioni e quella sul riuso (dominio pubblico).
Solo pagine di eia.gov che rispondono 200 al nostro server; nessun blocco aggirato. Per ogni file: URL, data di lettura, HTTP, SHA-256, byte in
dati/fonti.json; i file interi restano in dati/grezzi/eia/.

Se un controllo fallisce (foglio cambiato, unità diversa, date non di lunedì, un valore fuori scala, storia più corta di prima, tabella HTML
diversa dall'XLS) lo script esce con errore e NON tocca né i file grezzi né eia_prezzi.json: il sito resta alla settimana precedente.
Serve il pacchetto xlrd (lettura dei vecchi .xls).
"""
import hashlib
import html
import json
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

import xlrd

RADICE = Path(__file__).resolve().parent.parent
CARTELLA = RADICE / "dati" / "grezzi" / "eia"
FONTI = RADICE / "dati" / "fonti.json"
PREZZI = RADICE / "dati" / "eia_prezzi.json"
UA = "Mozilla/5.0 (compatible; static-data-site-check/1.0)"
OGGI = date.today().isoformat()
EIA = "https://www.eia.gov"
CHI = "U.S. Energy Information Administration"
LIC = {"nome": "Public domain (U.S. federal government work, 17 U.S.C. § 105)", "url": EIA + "/about/copyrights_reuse.php",
       "nota": "EIA: U.S. government publications are in the public domain and are not subject to copyright protection; citation requested."}

# combustibile → (codice prodotto EIA, nome nella riga 3 dell'XLS)
COMBUSTIBILI = {"oil": ("EPD2F", "No. 2 Heating Oil Residential Price"), "propane": ("EPLLPA", "Propane Residential Price")}
FILE = {
    "eia_oil_xls": ("Residential heating oil, weekly prices by state: series history (XLS)", "/dnav/pet/xls/PET_PRI_WFR_A_EPD2F_PRS_DPGAL_W.xls",
                    "/dnav/pet/pet_pri_wfr_a_EPD2F_prs_dpgal_w.htm", "heating_oil.xls"),
    "eia_propane_xls": ("Residential propane, weekly prices by state: series history (XLS)", "/dnav/pet/xls/PET_PRI_WFR_A_EPLLPA_PRS_DPGAL_W.xls",
                        "/dnav/pet/pet_pri_wfr_a_EPLLPA_prs_dpgal_w.htm", "propane.xls"),
    "eia_oil_tabella": ("Weekly Heating Oil and Propane Prices: residential heating oil (table)", "/dnav/pet/pet_pri_wfr_a_EPD2F_prs_dpgal_w.htm", None, "heating_oil.htm"),
    "eia_propane_tabella": ("Weekly Heating Oil and Propane Prices: residential propane (table)", "/dnav/pet/pet_pri_wfr_a_EPLLPA_prs_dpgal_w.htm", None, "propane.htm"),
    "eia_update": ("Heating Oil and Propane Update", "/petroleum/heatingoilpropane/", None, "update.htm"),
    "eia_definizioni": ("Weekly Heating Oil and Propane Prices: definitions, sources and explanatory notes", "/dnav/pet/TblDefs/pet_pri_wfr_tbldef2.asp", None, "definitions.htm"),
    "eia_riuso": ("Copyrights and reuse", "/about/copyrights_reuse.php", None, "copyrights_reuse.htm"),
}
# frasi che devono restare nelle pagine EIA: se cambiano, i testi delle nostre pagine vanno riletti
FRASI = {
    "eia_definizioni": {"tasse": "Prices do not include taxes paid by the consumer",
                        "gasolio": "The price charged for home delivery of No.2 heating oil, exclusive of any discounts such as those for prompt cash payment",
                        "propano": "The price charged for home delivery of consumer grade propane intended for use in space heating, cooking, or hot water heaters in residences",
                        "stagione": "collected weekly during the heating season which extends from October through March",
                        "fuori_stagione": "From April through September, heating oil and propane prices are collected on the second Monday of each month",
                        "fonte": "Residential prices are based on data collected by State Energy Offices",
                        "revisioni": "Values shown for the previous week may be revised to account for late submissions and corrections"},
    "eia_riuso": {"dominio_pubblico": "U.S. government publications are in the public domain and are not subject to copyright protection"},
    "eia_oil_tabella": {"unita": "(Dollars per Gallon Excluding Taxes)"},
    "eia_propane_tabella": {"unita": "(Dollars per Gallon Excluding Taxes)"},
    "eia_update": {"stagione": "only collected during the heating season, which extends from October through March"},
}
# aree che non sono Stati: Stati Uniti e regioni PADD (codice nella chiave della serie)
REGIONI = {"NUS": "us", "R10": "padd", "R1X": "padd", "R1Y": "padd", "R1Z": "padd", "R20": "padd", "R30": "padd", "R40": "padd", "R50": "padd"}


class Errore(Exception):
    pass


def scarica(url):
    p = subprocess.run(["curl", "-s", "-L", "--max-time", "120", "-A", UA, "-w", "\n%{http_code}", url], capture_output=True)
    corpo, _, codice = p.stdout.rpartition(b"\n")
    return int(codice or 0), corpo


def testo_html(b):
    t = b.decode("utf-8", "replace")
    t = re.sub(r"<(script|style|noscript)\b.*?</\1>", " ", t, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip()


def leggi_xls(b, comb):
    """XLS EIA → (date ISO, {codice area: {nome, chiave, tipo, valori}}, uscita, prossima uscita). Ogni anomalia è un Errore."""
    prodotto, descr = COMBUSTIBILI[comb]
    try:
        libro = xlrd.open_workbook(file_contents=b)
        foglio = libro.sheet_by_name("Data 1")
        indice = libro.sheet_by_name("Contents")
    except Exception as e:  # noqa: BLE001
        raise Errore(f"{comb}: XLS illeggibile ({e})") from e
    if foglio.cell_value(1, 0) != "Sourcekey" or foglio.cell_value(2, 0) != "Date":
        raise Errore(f"{comb}: intestazioni del foglio 'Data 1' cambiate")
    date_, aree = [], {}
    for r in range(3, foglio.nrows):
        c = foglio.cell(r, 0)
        if c.ctype != xlrd.XL_CELL_DATE:
            raise Errore(f"{comb}: riga {r + 1} senza data")
        d = xlrd.xldate_as_datetime(c.value, libro.datemode).date()
        if d.weekday() != 0:
            raise Errore(f"{comb}: {d} non è un lunedì")
        if date_ and d.isoformat() <= date_[-1]:
            raise Errore(f"{comb}: date non crescenti a {d}")
        date_.append(d.isoformat())
    for j in range(1, foglio.ncols):
        chiave, titolo = foglio.cell_value(1, j), foglio.cell_value(2, j)
        m = re.fullmatch(rf"W_{prodotto}_PRS_(NUS|R\w\w|S(\w\w))_DPG", chiave)
        t = re.fullmatch(rf"Weekly (.+?) {re.escape(descr)}\s+\(Dollars per Gallon\)", titolo)
        if not m or not t:
            raise Errore(f"{comb}: colonna {j} inattesa: {chiave!r} / {titolo!r}")
        codice = m.group(2) or m.group(1)
        nome = re.sub(r"^U\.S\. Weekly$", "U.S.", re.sub(r"^(Weekly )+", "", t.group(1)))  # alcune serie hanno «Weekly Weekly …» nel titolo
        nome = {"PADD 2": "Midwest (PADD 2)"}.get(nome, nome)  # nell'XLS del gasolio il Midwest è solo «PADD 2»; nelle tabelle EIA «Midwest (PADD 2)»
        valori = []
        for r in range(3, foglio.nrows):
            c = foglio.cell(r, j)
            if c.ctype == xlrd.XL_CELL_EMPTY or (c.ctype == xlrd.XL_CELL_TEXT and not c.value.strip()):
                valori.append(None)
            elif c.ctype == xlrd.XL_CELL_NUMBER and 0.3 < c.value < 15 and abs(c.value * 1000 - round(c.value * 1000)) < 1e-6:
                valori.append(round(c.value, 3))
            else:
                raise Errore(f"{comb}: {nome} {date_[r - 3]}: valore inatteso {c.value!r}")
        aree[codice] = {"nome": nome, "chiave": chiave, "tipo": REGIONI.get(m.group(1), "stato"), "valori": valori}
    righe = {str(indice.cell_value(r, 1)).strip(): indice.row_values(r) for r in range(indice.nrows)}
    try:
        uscita = datetime.strptime(righe["Release Date:"][2], "%m/%d/%Y").date().isoformat()
        prossima = datetime.strptime(righe["Next Release Date:"][2], "%m/%d/%Y").date().isoformat()
    except Exception as e:  # noqa: BLE001
        raise Errore(f"{comb}: date di uscita non lette nel foglio Contents ({e})") from e
    if "NUS" not in aree or aree["NUS"]["valori"][-1] is None:
        raise Errore(f"{comb}: manca il prezzo nazionale dell'ultima settimana")
    return date_, aree, uscita, prossima


def leggi_tabella(b):
    """Tabella HTML EIA (ultime 6 settimane) → (date ISO, {chiave della serie: [valori o None]})."""
    t = b.decode("latin-1")
    date_ = [datetime.strptime(x, "%m/%d/%y").date().isoformat() for x in re.findall(r'<th class="Series5">(\d\d/\d\d/\d\d)</th>', t)]
    righe = {}
    for pezzo in t.split('<tr class="DataRow">')[1:]:
        chiave = re.search(r"LeafHandler\.ashx\?n=PET&(?:amp;)?s=(\w+)&", pezzo)
        celle = [html.unescape(c).replace("\xa0", " ").strip() for c in re.findall(r'<td width="76" class="(?:DataB|Current2)">(.*?)</td>', pezzo, re.S)]
        if not chiave or len(celle) != len(date_) or any(not re.fullmatch(r"\d+\.\d{3}|NA|W|-|--|", c) for c in celle):
            raise Errore(f"tabella HTML: riga non letta ({celle})")
        righe[chiave.group(1)] = [float(c) if re.fullmatch(r"\d+\.\d{3}", c) else None for c in celle]
    return date_, righe


def controlla(nuovi, vecchio):
    """nuovi: {id: bytes}. Ritorna il contenuto di eia_prezzi.json; alza Errore se qualcosa non torna."""
    out = {"_nota": ("Scritto da raccolta/eia.py dai due XLS EIA in dati/grezzi/eia/ (non modificare a mano). Prezzi al consumo in dollari per "
                     "gallone, tasse escluse, lunedì di rilevazione; null = settimana non pubblicata per quell'area. verifica.py rilegge gli XLS "
                     "e le tabelle HTML e confronta ogni valore."),
           "unita": "USD per gallon, excluding taxes", "combustibili": {}}
    for comb in COMBUSTIBILI:
        date_, aree, uscita, prossima = leggi_xls(nuovi[f"eia_{comb}_xls"], comb)
        # la tabella HTML (ultime 6 settimane) deve dire le stesse cose dell'XLS
        d_tab, righe = leggi_tabella(nuovi[f"eia_{comb}_tabella"])
        if d_tab != date_[-len(d_tab):] or len(d_tab) != 6:
            raise Errore(f"{comb}: le settimane della tabella HTML {d_tab} non sono le ultime dell'XLS {date_[-6:]}")
        visti = 0
        if set(righe) != {a["chiave"] for a in aree.values()}:
            raise Errore(f"{comb}: le serie della tabella HTML non sono quelle dell'XLS")
        for a in aree.values():
            if righe[a["chiave"]] != a["valori"][-6:]:
                raise Errore(f"{comb}: {a['nome']}: tabella HTML {righe[a['chiave']]} ≠ XLS {a['valori'][-6:]}")
            visti += sum(v is not None for v in righe[a["chiave"]])
        # mai meno storia di prima; i valori già pubblicati possono cambiare solo nelle ultime due settimane (revisioni dichiarate dall'EIA)
        v = (vecchio or {}).get("combustibili", {}).get(comb)
        riviste = []
        if v:
            if date_[:len(v["date"])] != v["date"]:
                raise Errore(f"{comb}: le date già pubblicate sono cambiate o la storia è più corta")
            for cod, a in v["aree"].items():
                if cod not in aree:
                    raise Errore(f"{comb}: area {cod} sparita")
                for i, (x, y) in enumerate(zip(a["valori"], aree[cod]["valori"])):
                    if x != y:
                        if i < len(v["date"]) - 2 and "--accetta-revisioni" not in sys.argv:
                            raise Errore(f"{comb}: {a['nome']} {v['date'][i]}: valore vecchio cambiato da {x} a {y}. Se l'EIA ha davvero rivisto la storia "
                                         "(lo scrive nelle note della tabella), rilanciare con --accetta-revisioni")
                        riviste.append(f"{a['nome']} {v['date'][i]}: {x} → {y}")
        out["combustibili"][comb] = {"fonte": f"eia_{comb}_xls", "uscita": uscita, "prossima_uscita": prossima, "date": date_, "aree": aree}
        n = sum(x is not None for a in aree.values() for x in a["valori"])
        stati = [a for a in aree.values() if a["tipo"] == "stato" and a["valori"][-1] is not None]
        print(f"{comb}: {len(date_)} settimane {date_[0]} → {date_[-1]}, {len(aree)} serie, {n} valori, {len(stati)} Stati con il prezzo dell'ultima "
              f"settimana; tabella HTML = XLS su {visti} valori; uscita {uscita}, prossima {prossima}" + (f"; riviste: {riviste}" if riviste else ""))
    o, p = out["combustibili"]["oil"], out["combustibili"]["propane"]
    if o["date"][-1] != p["date"][-1] or o["uscita"] != p["uscita"]:
        raise Errore("gasolio e propano non hanno la stessa ultima settimana o la stessa uscita")
    return out


def main():
    locale = "--locale" in sys.argv
    fonti = json.loads(FONTI.read_text(encoding="utf-8"))
    vecchio = json.loads(PREZZI.read_text(encoding="utf-8")) if PREZZI.exists() else None
    nuovi, voci = {}, {}
    for fid, (titolo, percorso, pagina, nome) in FILE.items():
        if locale:
            b, http = (CARTELLA / nome).read_bytes(), fonti[fid]["http"]
        else:
            http, b = scarica(EIA + percorso)
            if http != 200 or len(b) < 2000:
                raise SystemExit(f"ERRORE: {EIA + percorso} → HTTP {http}, {len(b)} byte. Nessun file toccato.")
        nuovi[fid] = b
        voce = {"chi": CHI, "titolo": titolo, "url": EIA + percorso, "file": f"grezzi/eia/{nome}", "http": http,
                "letto_il": fonti[fid]["letto_il"] if locale else OGGI, "sha256": hashlib.sha256(b).hexdigest(), "byte": len(b), "licenza": LIC}
        if pagina:
            voce["pagina"] = EIA + pagina
        if fid in FRASI:
            t = testo_html(b)
            voce["cerca"] = FRASI[fid]
            voce["trovate"] = {k: f in t for k, f in FRASI[fid].items()}
            if not all(voce["trovate"].values()):
                raise SystemExit(f"ERRORE: {fid}: frasi non più presenti {[k for k, v in voce['trovate'].items() if not v]}. Nessun file toccato: rileggere la pagina EIA e i nostri testi.")
        voci[fid] = voce
    try:
        prezzi = controlla(nuovi, vecchio)
    except Errore as e:
        raise SystemExit(f"ERRORE: {e}. Nessun file toccato.") from e
    for comb in COMBUSTIBILI:
        voci[f"eia_{comb}_xls"]["rilascio"] = prezzi["combustibili"][comb]["uscita"]
        voci[f"eia_{comb}_xls"]["prossimo_rilascio"] = prezzi["combustibili"][comb]["prossima_uscita"]
        voci[f"eia_{comb}_xls"]["ultima_settimana"] = prezzi["combustibili"][comb]["date"][-1]
    prezzi["letto_il"] = voci["eia_oil_xls"]["letto_il"]
    CARTELLA.mkdir(parents=True, exist_ok=True)
    for fid, (_, _, _, nome) in FILE.items():
        (CARTELLA / nome).write_bytes(nuovi[fid])
    fonti.update(voci)
    FONTI.write_text(json.dumps(fonti, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    PREZZI.write_text(json.dumps(prezzi, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Scritti {PREZZI.name}, {len(FILE)} file in {CARTELLA} e {FONTI.name}. Ora: python3 inflation/genera.py && python3 inflation/verifica.py --browser")


if __name__ == "__main__":
    main()
