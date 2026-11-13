"""Tabella della paga base in vigore dal 1° aprile 2025 (Public Law 118-159, sezione 601): testo ufficiale GPO, non immagini.

Uso (dalla radice del repository): python3 milpay/raccolta/aprile2025.py  ->  dati/paga_2025_aprile.json

Serve a due cose: (1) spiegare con una fonte perché le righe E-1…E-5 del 2026 superano di più del 3,8 % la tabella di
gennaio 2025 (la legge ha alzato quelle righe ad aprile 2025); (2) un controllo in più, indipendente dalla lettura ottica:
la tabella 2026 deve essere la tabella di aprile 2025 × 1,038 su TUTTE le righe (genera.controlla_tabella).
"""
import hashlib
import html
import json
import re
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
DATI, CACHE = RADICE / "dati", RADICE / "cache" / "fonti"
URL = "https://www.govinfo.gov/content/pkg/PLAW-118publ159/html/PLAW-118publ159.htm"
UA = {"User-Agent": "rete-siti-dati/1.0 (controllo delle fonti ufficiali)"}
ANNI = [2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40]  # colonne "Over N Years" (indice + 1)
CAT = {"Commissioned Officers With": "OE", "Commissioned Officers": "O", "Warrant Officers": "W", "Enlisted Members": "E"}


def scarica():
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / "PLAW-118publ159.htm"
    if not f.exists():
        with urllib.request.urlopen(urllib.request.Request(URL, headers=UA), timeout=180) as r:
            f.write_bytes(r.read())
    return f.read_bytes()


def leggi(b):
    t = html.unescape(re.sub(r"<[^>]+>", "", b.decode("utf-8", "replace")))
    fine = t.index("SEC. 602. ", t.index("Effective April 1, 2025, the rates of monthly basic pay"))
    s = t[t.rindex("SEC. 601.", 0, fine):fine]
    if "Effective April 1, 2025, the rates of monthly basic pay for members" not in re.sub(r"\s+", " ", s):
        raise SystemExit("sezione 601 non trovata")
    tab, cat, cols = {}, None, []
    for riga in s.splitlines():
        r = riga.strip()
        for nome, c in CAT.items():
            if r.startswith(nome):
                cat = c
                break
        intest = re.findall(r"2 Years or|Over (\d+) Years", riga)
        if intest and re.match(r"(Pay Grade|Over \d+ Years)", r):
            cols = [0 if a == "" else ANNI.index(int(a)) + 1 for a in intest]
            continue
        m = re.match(r"([EWO]-\d+E?)\.{5,}\s*(.*)$", r)
        if not m or cat is None:
            continue
        grado = m.group(1)
        valori = re.findall(r"\$?([\d,]+\.\d\d)", m.group(2))
        if len(valori) != len(cols):
            raise SystemExit(f"{grado}: {len(valori)} valori per {len(cols)} colonne ({cols})")
        dest = tab.setdefault(cat, {}).setdefault(grado, [None] * 22)
        for i, v in zip(cols, valori):
            x = float(v.replace(",", ""))
            dest[i] = x if x > 0 else None
    return tab, s


def main():
    b = scarica()
    tab, s = leggi(b)
    e1 = re.search(r"fewer than 4 months on active duty, the ?P?rate of basic pay is \$([\d,]+\.\d\d)", re.sub(r"\s+", " ", s))
    e9 = re.search(r"basic pay for this grade is \$([\d,]+\.\d\d) per month", re.sub(r"\s+", " ", s))
    righe = sum(len(v) for v in tab.values())
    importi = sum(1 for c in tab.values() for r in c.values() for v in r if v is not None)
    if {k: len(v) for k, v in tab.items()} != {"O": 10, "OE": 3, "W": 5, "E": 9} or not e1 or not e9:
        raise SystemExit(f"tabella di aprile 2025 letta male: {righe} righe, {importi} importi")
    out = {"effettiva_dal": "April 1, 2025",
           "fonte": {"titolo": "Servicemember Quality of Life Improvement and National Defense Authorization Act for Fiscal Year 2025, section 601",
                     "legge": "Public Law 118-159", "citazione": "138 Stat. 1924", "firmata_il": "2024-12-23", "url": URL,
                     "sha256": hashlib.sha256(b).hexdigest()},
           "letto_il": date.today().isoformat(), "righe": righe, "importi": importi,
           "E1_meno_di_4_mesi": float(e1.group(1).replace(",", "")), "E9_incarichi_speciali": float(e9.group(1).replace(",", "")),
           "tabelle": tab}
    (DATI / "paga_2025_aprile.json").write_text(json.dumps(out, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"aprile 2025: {righe} righe, {importi} importi, E-1 <4 mesi {out['E1_meno_di_4_mesi']}, E-9 incarichi {out['E9_incarichi_speciali']}")


if __name__ == "__main__":
    main()
