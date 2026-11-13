"""Diarie federali (per diem GSA, anni fiscali 2026 e 2027) e rimborso chilometrico (IRS e GSA): scarica i file grezzi,
li legge e scrive dati/perdiem.json; registra URL, data e SHA-256 di ogni file grezzo in dati/fonti.json (chiave "grezzi").

Uso (dalla radice del repository):
    python3 milpay/raccolta/perdiem.py            # scarica di nuovo i file e rilegge
    python3 milpay/raccolta/perdiem.py --offline  # rilegge i file già in dati/grezzi/

File grezzi (tutti pubblici, dominio pubblico, nessun blocco aggirato):
- GSA, file principali delle tariffe FY2026 e FY2027 (xlsx dalla pagina "Per diem files");
- GSA, API pubblica delle tariffe (chiave dimostrativa DEMO_KEY): alloggio mese per mese e tabella dei pasti, FY2026 e FY2027.
  Serve da secondo dato indipendente: ogni mese di ogni località dell'xlsx deve coincidere con l'API;
- GSA, pagina "Mileage reimbursements" (tariffe chilometriche per i viaggi ufficiali dei dipendenti federali);
- IRS, Notice 2026-10 (PDF) e Internal Revenue Bulletin 2026-29 (Announcement 2026-11, tariffe dal 1° luglio 2026).
Ogni cifra usata dal sito viene da qui; genera.py e verifica.py rileggono i file grezzi e confrontano.
"""
import hashlib
import html
import json
import re
import subprocess
import sys
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
DATI = RADICE / "dati"
GREZZI = DATI / "grezzi"
UA = {"User-Agent": "rete-siti-dati/1.0 (controllo delle fonti ufficiali)"}

FILE = {
    "gsa_fy2026.xlsx": "https://www.gsa.gov/system/files/FY2026_PerDiemMasterRatesFile.xlsx",
    "gsa_fy2027.xlsx": "https://www.gsa.gov/system/files/FY2027_PerDiemRates_Validated090126.xlsx",
    "gsa_api_lodging_2026.json": "https://api.gsa.gov/travel/perdiem/v2/rates/conus/lodging/2026?api_key=DEMO_KEY",
    "gsa_api_lodging_2027.json": "https://api.gsa.gov/travel/perdiem/v2/rates/conus/lodging/2027?api_key=DEMO_KEY",
    "gsa_api_mie_2026.json": "https://api.gsa.gov/travel/perdiem/v2/rates/conus/mie/2026?api_key=DEMO_KEY",
    "gsa_api_mie_2027.json": "https://api.gsa.gov/travel/perdiem/v2/rates/conus/mie/2027?api_key=DEMO_KEY",
    "gsa_mileage.html": "https://www.gsa.gov/travel/mileage-reimbursements",
    "irs_notice_2026-10.pdf": "https://www.irs.gov/pub/irs-drop/n-26-10.pdf",
    "irs_irb_2026-29.html": "https://www.irs.gov/irb/2026-29_irb",
    "irs_standard_mileage_rates.html": "https://www.irs.gov/tax-professionals/standard-mileage-rates",
}
# Conteggi attesi (letti il 13/11/2026): se GSA ripubblica un file con un numero diverso di righe, ci si ferma e si riguarda.
ATTESI = {"2026": {"righe": 649, "localita": 296}, "2027": {"righe": 641, "localita": 295}}
MESI_FY = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]  # ordine dell'anno fiscale
MESI_NOMI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
STATI = {"AL": "Alabama", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
         "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
         "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
         "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
         "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
         "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
         "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"}


def scarica():
    GREZZI.mkdir(parents=True, exist_ok=True)
    reg = {}
    for nome, url in FILE.items():
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
            b, http = r.read(), r.status
        if http != 200 or len(b) < 400:
            raise SystemExit(f"{nome}: HTTP {http}, {len(b)} byte")
        (GREZZI / nome).write_bytes(b)
        reg[nome] = {"url": url, "letto_il": date.today().isoformat(), "sha256": hashlib.sha256(b).hexdigest(), "byte": len(b), "http": http}
        print(f"{nome}: {len(b)} byte")
    return reg


def mese_da(txt):
    """'October 1' o 'October 1, 2026' -> indice nell'anno fiscale (0 = ottobre)."""
    m = re.match(r"([A-Za-z]+) (\d{1,2})(?:, (\d{4}))?$", txt.strip())
    if not m:
        raise SystemExit(f"data di stagione non leggibile: {txt!r}")
    return MESI_FY.index(m.group(1)[:3])


def leggi_xlsx(fy, percorso):
    import openpyxl
    ws = openpyxl.load_workbook(percorso, data_only=True).worksheets[0]
    righe = list(ws.iter_rows(values_only=True))
    titolo = righe[0][1] if fy == "2026" else righe[0][0]
    if f"FY{fy} Per Diem Rates - Effective October 1, {int(fy) - 1}" not in str(titolo):
        raise SystemExit(f"FY{fy}: titolo inatteso {titolo!r}")
    corpo = righe[2:]
    off = 1 if fy == "2026" else 0  # il file 2026 ha la colonna ID in testa
    std = corpo[0]
    if "Standard CONUS rate applies to all counties not specifically listed" not in str(std[off + 1]):
        raise SystemExit(f"FY{fy}: riga della tariffa standard non trovata")
    standard = {"alloggio": std[off + 5], "mie": std[off + 6]}
    loc, ordine = {}, []
    for r in corpo[1:]:
        st, dest, contee, ini, fine, allog, mie = (r[off + i] for i in range(7))
        if not isinstance(allog, int) or not isinstance(mie, int):
            raise SystemExit(f"FY{fy}: valori non interi {r}")
        dest, contee, st = str(dest).strip(), str(contee).strip(), str(st).strip()
        k = (st, dest, contee)
        if k not in loc:
            loc[k] = {"stato": st, "nome": dest, "contee": contee, "mie": mie, "stagioni": [], "id_gsa": r[0] if off else None}
            ordine.append(k)
        if loc[k]["mie"] != mie:
            raise SystemExit(f"FY{fy} {dest}: M&IE diverso tra stagioni")
        loc[k]["stagioni"].append({"da": str(ini or "").strip(), "a": str(fine or "").strip(), "alloggio": allog})
    out = []
    for k in ordine:
        L = loc[k]
        mesi = [None] * 12
        for s in L["stagioni"]:
            if not s["da"] and not s["a"]:
                a, b = 0, 11
            else:
                a, b = mese_da(s["da"]), mese_da(s["a"])
                gg_da = int(re.search(r" (\d{1,2})", s["da"]).group(1))
                if gg_da != 1:
                    raise SystemExit(f"FY{fy} {L['nome']}: stagione che non inizia il 1° del mese ({s['da']})")
            for i in range(a, b + 1):
                if mesi[i] is not None:
                    raise SystemExit(f"FY{fy} {L['nome']}: mese {MESI_FY[i]} in due stagioni")
                mesi[i] = s["alloggio"]
        if None in mesi:
            raise SystemExit(f"FY{fy} {L['nome']}: mesi senza tariffa {mesi}")
        L["mesi"] = mesi
        out.append(L)
    return {"titolo": str(titolo).strip(), "righe": len(corpo) - 1, "standard": standard, "localita": out}


def confronta_api(fy, dati, api):
    """Ogni mese di ogni località dell'xlsx = API GSA (secondo dato indipendente). Restituisce le differenze."""
    diff = []
    std = [x for x in api if x["City"] == "Standard Rate"]
    for x in std:
        if any(int(x[m]) != dati["standard"]["alloggio"] for m in MESI_FY) or int(x["Meals"]) != dati["standard"]["mie"]:
            diff.append(f"FY{fy} standard {x['State']}: API {x}")
    nsa = [x for x in api if x["City"] != "Standard Rate"]
    usati = set()
    for L in dati["localita"]:
        cand = [i for i, x in enumerate(nsa) if x["State"] == L["stato"] and norm_nome(x["City"]) == norm_nome(L["nome"]) and i not in usati]
        if len(cand) > 1:
            cand = [i for i in cand if norm_nome(nsa[i]["County"] or "") == norm_nome(L["contee"])] or cand[:1]
        if not cand:
            diff.append(f"FY{fy} {L['stato']} {L['nome']}: assente nell'API")
            continue
        i = cand[0]
        usati.add(i)
        x = nsa[i]
        mesi_api = [int(x[m]) for m in MESI_FY]
        if mesi_api != L["mesi"] or int(x["Meals"]) != L["mie"]:
            diff.append(f"FY{fy} {L['stato']} {L['nome']}: xlsx {L['mesi']} M&IE {L['mie']} / API {mesi_api} M&IE {x['Meals']}")
    # l'API ripete la riga di Washington DC sotto MD e VA (l'area comprende contee di quei due Stati): stessi valori della riga DC
    dc = next((L for L in dati["localita"] if L["stato"] == "DC"), None)
    for i, x in enumerate(nsa):
        if i in usati:
            continue
        if dc and x["City"] == "District of Columbia" and x["State"] in ("MD", "VA"):
            if [int(x[m]) for m in MESI_FY] != dc["mesi"] or int(x["Meals"]) != dc["mie"]:
                diff.append(f"FY{fy} riga DC ripetuta sotto {x['State']}: valori diversi")
    extra = [f"{nsa[i]['State']} {nsa[i]['City']}" for i in range(len(nsa)) if i not in usati]
    return diff, extra, len(std), len(nsa)


def norm_nome(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower().replace("’", "'")).strip()


def slug(s):
    s = s.lower().replace("’", "").replace("'", "").replace("&", " and ").replace(".", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def leggi_mie(api):
    return [{"totale": x["total"], "colazione": x["breakfast"], "pranzo": x["lunch"], "cena": x["dinner"], "extra": x["incidental"], "primo_ultimo": x["FirstLastDay"]} for x in api]


def testo_html(b):
    t = b.decode("utf-8", "replace")
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).replace("’", "'")


def leggi_chilometri():
    """Tariffe chilometriche: IRS (Notice 2026-10 fino al 30/6/2026, Announcement 2026-11 dal 1/7/2026) e GSA (viaggi ufficiali)."""
    n = subprocess.run(["pdftotext", str(GREZZI / "irs_notice_2026-10.pdf"), "-"], capture_output=True, text=True, check=True).stdout
    n = re.sub(r"\s+", " ", n)
    irb = testo_html((GREZZI / "irs_irb_2026-29.html").read_bytes())
    gsa = testo_html((GREZZI / "gsa_mileage.html").read_bytes())

    def cerca(rx, t, dove):
        m = re.search(rx, t)
        if not m:
            raise SystemExit(f"{dove}: frase non trovata {rx}")
        return float(m.group(1))

    irs = [
        {"dal": "2026-01-01", "al": "2026-06-30", "fonte": "irs_n2026_10",
         "business": cerca(r"standard mileage rate for transportation or travel expenses for 2026 is ([\d.]+) cents per mile for all miles of business use", n, "Notice 2026-10"),
         "charity": cerca(r"The standard mileage rate is (\d+) cents per mile for use of an automobile in rendering gratuitous services to a charitable organization", n, "Notice 2026-10"),
         "medical_moving": cerca(r"The standard mileage rate for 2026 is ([\d.]+) cents per mile for use of an automobile: \(1\) for medical care", n, "Notice 2026-10")},
        {"dal": "2026-07-01", "al": "2026-12-31", "fonte": "irs_a2026_11",
         "business": cerca(r"The revised standard mileage rates are: \(1\) Business ([\d.]+) cents per mile", irb, "Announcement 2026-11"),
         "medical_moving": cerca(r"\(2\) Medical and moving ([\d.]+) cents per mile", irb, "Announcement 2026-11"),
         "charity": cerca(r"charitable contributions is fixed under § 170\(i\) of the Internal Revenue Code at (\d+) cents per mile", irb, "Announcement 2026-11")},
    ]
    if "on or after July 1, 2026" not in irb or "Notice 2026-10 is modified" not in irb:
        raise SystemExit("Announcement 2026-11: date di validità non trovate")
    pov = {"dal": "2026-07-01",
           "auto": cerca(r"no government-owned automobile was authorized or available \$([\d.]+) per mile", gsa, "GSA mileage"),
           "auto_gov_disponibile": cerca(r"but you chose to drive your own automobile \$([\d.]+) per mile", gsa, "GSA mileage"),
           "moto": cerca(r"Motorcycle - \$([\d.]+) per mile", gsa, "GSA mileage"),
           "aereo": cerca(r"Airplane\* - \$([\d.]+) per mile", gsa, "GSA mileage"),
           "trasloco": cerca(r"Moving for the job or relocation \$([\d.]+) per mile", gsa, "GSA mileage")}
    if "Current mileage rates for official travel on or after July 1, 2026" not in gsa:
        raise SystemExit("GSA mileage: la pagina non parla più delle tariffe dal 1° luglio 2026")
    m = re.search(r"Jan\. 1, 2026 \$([\d.]+) \$([\d.]+) \$([\d.]+) \$([\d.]+)", gsa)
    pov_gen = {"dal": "2026-01-01", "al": "2026-06-30", "auto": float(m.group(1)), "auto_gov_disponibile": float(m.group(2)), "moto": float(m.group(3)), "aereo": float(m.group(4))}
    # storico IRS (pagina "Standard mileage rates"): anni interi 2023-2025, nell'ordine della pagina
    smr = testo_html((GREZZI / "irs_standard_mileage_rates.html").read_bytes())
    storico = []
    for anno in range(2025, 2022, -1):  # 2022 ha due periodi: non serve al sito
        m = re.search(rf" {anno}(?: TCJA)? ([\d.]+) (\d+) ([\d.]+) IR-", smr)
        if not m:
            raise SystemExit(f"storico IRS {anno}: riga non trovata")
        storico.append({"anno": anno, "business": float(m.group(1)), "charity": float(m.group(2)), "medical_moving": float(m.group(3))})
    if "2026 (July 1 – Dec. 31) 76 14 23.5" not in smr.replace("'", "'") or "2026 (Jan. 1 – June 30) 72.5 14 20.5" not in smr:
        raise SystemExit("pagina IRS: le righe 2026 non coincidono con Notice 2026-10 e Announcement 2026-11")
    return {"irs": irs, "gsa_pov": [pov_gen, pov], "irs_storico": storico}


def main():
    offline = "--offline" in sys.argv
    fonti_p = DATI / "fonti.json"
    fj = json.loads(fonti_p.read_text(encoding="utf-8"))
    if offline:
        reg = fj.get("grezzi", {})
        for nome in FILE:
            b = (GREZZI / nome).read_bytes()
            if reg.get(nome, {}).get("sha256") != hashlib.sha256(b).hexdigest():
                raise SystemExit(f"{nome}: impronta diversa da fonti.json")
    else:
        reg = scarica()
    out = {"_nota": "Diarie federali GSA (CONUS) FY2026 e FY2027 e tariffe chilometriche 2026, lette dai file grezzi in dati/grezzi/ (impronte in fonti.json, chiave grezzi). "
                    "Mesi nell'ordine dell'anno fiscale (ottobre … settembre). Generato da raccolta/perdiem.py: non modificare a mano.",
           "letto_il": max(v["letto_il"] for v in reg.values()), "mesi_fy": MESI_FY, "stati": STATI, "fy": {}, "mie_tabella": {}, "api": {}}
    for fy in ("2026", "2027"):
        d = leggi_xlsx(fy, GREZZI / f"gsa_fy{fy}.xlsx")
        api = json.loads((GREZZI / f"gsa_api_lodging_{fy}.json").read_text())
        diff, extra, n_std, n_nsa = confronta_api(fy, d, api)
        a = ATTESI[fy]
        if d["righe"] != a["righe"] or len(d["localita"]) != a["localita"]:
            raise SystemExit(f"FY{fy}: {d['righe']} righe e {len(d['localita'])} località, attese {a['righe']} e {a['localita']}")
        if diff:
            raise SystemExit("XLSX ≠ API:\n - " + "\n - ".join(diff))
        for L in d["localita"]:
            L["slug"] = slug(L["nome"])
        visti = {}
        for L in d["localita"]:
            k = (L["stato"], L["slug"])
            if k in visti:
                raise SystemExit(f"FY{fy}: due località con lo stesso indirizzo {k}")
            visti[k] = 1
        out["fy"][fy] = d
        out["mie_tabella"][fy] = leggi_mie(json.loads((GREZZI / f"gsa_api_mie_{fy}.json").read_text()))
        out["api"][fy] = {"standard_per_stato": n_std, "localita": n_nsa, "solo_api": extra}
        print(f"FY{fy}: {d['righe']} righe, {len(d['localita'])} località, standard {d['standard']}; API: {n_std} righe standard, {n_nsa} località, "
              f"{len(d['localita'])} uguali mese per mese; solo nell'API: {extra}")
    out["chilometri"] = leggi_chilometri()
    print("chilometri:", json.dumps(out["chilometri"]))
    (DATI / "perdiem.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    fj["grezzi"] = reg
    fonti_p.write_text(json.dumps(fj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
