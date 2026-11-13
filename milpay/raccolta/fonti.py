"""Rilegge le fonti ufficiali del sito e controlla le frasi esatte da cui vengono le cifre; scrive dati/fonti.json.

Uso (dalla radice del repository): python3 milpay/raccolta/fonti.py
Per ogni fonte: HTTP, SHA-256 del file, data di lettura, esito di ogni frase cercata (spazi normalizzati).
Nessun blocco aggirato: dfas.mil, militarypay.defense.gov, defense.gov, congress.gov e bls.gov (sito) rispondono 403 al
nostro server e non sono usati; il BLS si legge dalla sua API pubblica.
"""
import hashlib
import json
import re
import subprocess
import tempfile
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
DATI = RADICE / "dati"
UA = {"User-Agent": "rete-siti-dati/1.0 (controllo delle fonti ufficiali)"}

P26 = json.loads((DATI / "paga_2026.json").read_text())["fonte"]
P25 = json.loads((DATI / "paga_2025.json").read_text())["fonte"]
ST = json.loads((DATI / "storico.json").read_text())

FONTI = {
    "eo2026": {"titolo": f"Executive Order {P26['ordine_esecutivo']}, Adjustments of Certain Rates of Pay, Schedule 8 (Pay of the Uniformed Services)",
               "chi": f"Federal Register, {P26['citazione']}, published {P26['pubblicato_il']}", "url": P26["url"], "leggi": P26["pdf"], "pdf": True,
               "cerca": ["Schedule 8 is effective January 1, 2026", "rates of monthly basic pay (37 U.S.C. 203(a)) for members of the uniformed services",
                         "level II of the Executive Schedule in effect during calendar year 2026, which is $18,899.90", "level V of the Executive Schedule in effect during calendar year 2026, which is $15,408.30",
                         "basic pay for this grade is $11,166.90 per month", "cadet or midshipman pay authorized by 37 U.S.C. 203(c) is $1,452.90",
                         "credited with over 4 years of active duty service as an enlisted member or warrant officer", "at least 1,460 points",
                         "served 4 months or more on active duty", "served less than 4 months on active duty", "Computed Under 37 U.S.C. 205"]},
    "eo2025": {"titolo": f"Executive Order {P25['ordine_esecutivo']}, Adjustments of Certain Rates of Pay, Schedule 8",
               "chi": f"Federal Register, {P25['citazione']}, published {P25['pubblicato_il']}", "url": P25["url"], "leggi": P25["pdf"], "pdf": True,
               "cerca": ["Schedule 8 is effective January 1, 2025"]},
    "usc1009": {"titolo": "37 U.S.C. 1009, Adjustments of monthly basic pay", "chi": "United States Code, 2024 edition (govinfo.gov, U.S. Government Publishing Office)",
                "url": "https://www.govinfo.gov/content/pkg/USCODE-2024-title37/html/USCODE-2024-title37-chap19-sec1009.htm",
                "cerca": ["Effective on January 1 of each year, the rates of basic pay for members of the uniformed services",
                          "rounded to the nearest one-tenth of one percent", "the ECI for the base quarter of the year before the preceding year",
                          "Employment Cost Index (wages and salaries, private industry workers) published quarterly by the Bureau of Labor Statistics",
                          "the three-month period ending on September 30 of such year", "before September 1 of the preceding year a plan for such alternative pay adjustments",
                          "the basic allowance for subsistence", "the basic allowance for housing"]},
    "bls_eci": {"titolo": "Employment Cost Index: wages and salaries, private industry workers, 12-month percent change (series CIU2020000000000A)",
                "chi": "U.S. Bureau of Labor Statistics, public data API", "url": "https://api.bls.gov/publicAPI/v2/timeseries/data/CIU2020000000000A", "api_bls": True,
                "cerca": []},
    "budget2027": {"titolo": "Budget of the U.S. Government, Fiscal Year 2027, Appendix (Department of Defense, Military Personnel), PDF page 241",
                   "chi": "Office of Management and Budget, published on govinfo.gov", "url": "https://www.govinfo.gov/app/details/BUDGET-2027-APP",
                   "leggi": "https://www.govinfo.gov/content/pkg/BUDGET-2027-APP/pdf/BUDGET-2027-APP.pdf", "pdf": True,
                   "cerca": ["the Budget funds a military pay raise of 7 percent for all military personnel ranked E-5 and below, 6 percent for E-6 to O-3, and 5 percent for O-4 and above"]},
    "fr_search": {"titolo": "Federal Register search: presidential documents titled “Adjustments of Certain Rates of Pay”",
                  "chi": "Federal Register (National Archives), public API", "url": "https://www.federalregister.gov/documents/search?conditions%5Bterm%5D=%22Adjustments+of+Certain+Rates+of+Pay%22&conditions%5Btype%5D%5B%5D=PRESDOCU",
                  "leggi": "https://www.federalregister.gov/api/v1/documents.json?conditions%5Bterm%5D=%22Adjustments%20of%20Certain%20Rates%20of%20Pay%22&conditions%5Btype%5D%5B%5D=PRESDOCU&per_page=5&order=newest",
                  "cerca": ["2025-23844"]},
}
for anno, f in ST["fonti_tabelle"].items():
    FONTI[f"eo{anno}"] = FONTI.get(f"eo{anno}") or {
        "titolo": f"Executive Order {f['ordine_esecutivo']}, Adjustments of Certain Rates of Pay, Schedule 8 (effective January 1, {anno})",
        "chi": f"Federal Register, {f['citazione']}", "url": f["url"], "leggi": f["pdf"], "pdf": True, "cerca": []}


def norm(t):
    t = t.replace("—", "-").replace("–", "-").replace("’", "'").replace("ﬁ", "fi").replace("ﬂ", "fl")
    t = re.sub(r"-\s*\n\s*", "-", t)
    return re.sub(r"\s+", " ", t)


def leggi(fid, f):
    url = f.get("leggi", f["url"])
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
            b, http = r.read(), r.status
    except urllib.error.HTTPError as e:
        return {"http": e.code, "letto_il": date.today().isoformat()}
    if f.get("pdf"):
        with tempfile.NamedTemporaryFile(suffix=".pdf") as t:
            t.write(b)
            t.flush()
            testo = subprocess.run(["pdftotext", t.name, "-"], capture_output=True, text=True).stdout
    else:
        testo = b.decode("utf-8", "replace")
        testo = re.sub(r"<[^>]+>", " ", testo).replace("&amp;", "&").replace("&quot;", '"').replace("&#8212;", "-")
    es = {"http": http, "letto_il": date.today().isoformat(), "sha256": hashlib.sha256(b).hexdigest(), "byte": len(b)}
    if f.get("api_bls"):
        try:
            d = json.loads(b)
            es["api"] = d.get("status")
        except ValueError:
            es["api"] = "risposta non JSON"
    t = norm(testo)
    es["trovate"] = {c: norm(c) in t for c in f["cerca"]}
    return es


def main():
    esiti = {}
    for fid, f in FONTI.items():
        esiti[fid] = leggi(fid, f)
        e = esiti[fid]
        mancano = [c for c, ok in e.get("trovate", {}).items() if not ok]
        print(f"{fid}: HTTP {e['http']}" + (f" API {e['api']}" if "api" in e else "") + (f" MANCANO {mancano}" if mancano else ""))
    (DATI / "fonti.json").write_text(json.dumps({"definizioni": FONTI, "fonti": esiti}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
