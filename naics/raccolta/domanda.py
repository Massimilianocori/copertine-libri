"""Real searches (Google autocomplete, hl=en gl=us): they decide which FAQ and which "NAICS code for ..." pages exist.

Usage (from the repository root):
    python3 -I naics/raccolta/domanda.py          # reads only the missing roots
    python3 -I naics/raccolta/domanda.py --tutto  # re-reads everything (every 3 months)

One request per root; suggestions are saved in dati/domanda.json (key "radici"). Monthly volumes (Google Ads, via
api.seodata.dev) are NOT read here: they are written by hand in dati/volumi.json with the date of the measurement (the key
lives outside the repository). No personal data: only search words are sent. 0.5 s pause; at the first non-200 answer the
script stops and saves (no attempt to get around limits).
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
FILE = RADICE / "dati" / "domanda.json"
URL = "https://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=us&q="

GENERALI = [
    "naics code", "naics code ", "naics codes", "naics code lookup", "naics code search", "naics code list", "naics code meaning",
    "what is naics code", "what is a naics code", "what is my naics code", "how to find naics code", "how to find my naics code",
    "naics code for", "naics code for ", "naics code vs sic code", "naics vs sic", "naics code 2022", "naics 2022", "naics 2017 vs 2022",
    "naics code changes 2022", "naics code example", "naics code how many digits", "naics code structure", "naics number",
    "naics code meaning digits", "is naics code required", "naics code for llc", "naics code for small business", "naics code on tax return",
    "sic code", "sic code ", "sic codes", "sic code lookup", "sic code list", "what is sic code", "what is a sic code", "sic code vs naics",
    "sic code to naics", "naics to sic", "sic code for", "sic code for ", "sic code naics crosswalk", "sic code 4 digit",
]
LETTERE = [f"naics code {c}" for c in "abcdefghilmnoprstw"]
CIFRE = [f"naics code {c}" for c in "123456789"]
ATTIVITA = [
    "consulting", "construction", "general contractor", "cleaning services", "cleaning business", "janitorial", "trucking", "real estate",
    "restaurant", "food truck", "ecommerce", "online retail", "landscaping", "lawn care", "it services", "software development",
    "computer programming", "marketing", "photography", "home health care", "staffing", "property management", "insurance agent",
    "hair salon", "beauty salon", "nail salon", "daycare", "child care", "accounting", "bookkeeping", "dental office", "medical office",
    "physical therapy", "personal trainer", "fitness", "event planning", "electrician", "plumbing", "hvac", "roofing", "painting",
    "handyman", "remodeling", "logistics", "freight", "courier", "delivery", "auto repair", "car wash", "nonprofit", "church",
    "rental property", "airbnb", "short term rental", "holding company", "investment", "graphic design", "web design", "tutoring",
    "education", "security", "transportation", "retail", "wholesale", "manufacturing", "farming", "bakery", "coffee shop", "bar",
    "catering", "notary", "credit repair", "mortgage", "engineering", "architect", "lawyer", "attorney", "dog grooming", "pet sitting",
]


def leggi(q):
    req = urllib.request.Request(URL + urllib.parse.quote(q), headers={"User-Agent": "Mozilla/5.0 (research script)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        if r.status != 200:
            raise RuntimeError(f"HTTP {r.status}")
        dati = json.loads(r.read().decode("utf-8", errors="replace"))
    return dati[1] if isinstance(dati, list) and len(dati) > 1 else []


def main():
    tutto = "--tutto" in sys.argv
    d = json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() and not tutto else {}
    d.setdefault("_nota", "Google autocomplete suggestions (hl=en, gl=us) for each root. Written by raccolta/domanda.py.")
    d.setdefault("radici", {})
    radici = GENERALI + LETTERE + CIFRE + [f"naics code for {a}" for a in ATTIVITA] + ["sic code for consulting", "sic code for construction"]
    nuove = 0
    for q in radici:
        if q in d["radici"]:
            continue
        try:
            d["radici"][q] = leggi(q)
        except Exception as e:  # noqa: BLE001
            print(f"stopped at «{q}»: {e}", file=sys.stderr)
            break
        nuove += 1
        time.sleep(0.5)
    d["letto_il"] = date.today().isoformat()
    FILE.write_text(json.dumps(d, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    tot = sum(len(v) for v in d["radici"].values())
    print(f"{nuove} roots read now, {len(d['radici'])} in all, {tot} suggestions")


if __name__ == "__main__":
    main()
