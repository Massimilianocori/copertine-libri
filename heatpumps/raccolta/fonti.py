"""Scarica i file ufficiali e rilegge le pagine delle regole per Heat Pump Grants UK.

Uso (dalla radice del repository):
    python3 heatpumps/raccolta/fonti.py     # file grezzi in heatpumps/raccolta/_grezzi/ (fuori da git) + heatpumps/dati/fonti.json

Cosa fa:
1. Cerca con l'API dei contenuti di GOV.UK (www.gov.uk/api/content/...) l'ultima versione di ogni file statistico:
   Boiler Upgrade Scheme statistics (mensile), Renewable electricity by local authority (annuale), Solar PV cost data TIC
   (annuale), Solar photovoltaics deployment ET 6.3 (mensile). I nomi dei file cambiano a ogni uscita: l'indirizzo si legge
   sempre dall'API, mai a mano.
2. Scarica i quattro xlsx in raccolta/_grezzi/ con un nome fisso e ne calcola l'impronta SHA-256.
3. Rilegge le pagine delle regole (GOV.UK "Apply for the Boiler Upgrade Scheme" via API, due pagine Ofgem) e controlla che le
   frasi esatte usate nel sito ci siano ancora (campo "cerca" di DEFINIZIONI).
Scrive dati/fonti.json: definizioni + esito di ogni lettura (HTTP, data, impronta, frasi trovate). Nessun dato personale:
le richieste non portano nulla di nostro. Nessun blocco anti-robot viene aggirato.
"""
import hashlib
import html
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
GREZZI = Path(__file__).resolve().parent / "_grezzi"
FILE = RADICE / "dati" / "fonti.json"
UA = {"User-Agent": "Mozilla/5.0 (compatible; heatpumps-check/1.0)"}
API = "https://www.gov.uk/api/content/"

# File statistici: pagina GOV.UK da cui si legge l'indirizzo e regola per scegliere l'allegato
FILE_STAT = {
    "bus_xlsx": {"pagina": "government/collections/boiler-upgrade-scheme-statistics", "collezione": True,
                 "allegato": r"^Boiler Upgrade Scheme Statistics: .* \(Excel\)$", "nome": "bus.xlsx",
                 "titolo": "Boiler Upgrade Scheme statistics (Excel workbook)", "chi": "Department for Energy Security and Net Zero (DESNZ), data from Ofgem"},
    "solare_la_xlsx": {"pagina": "government/statistics/regional-renewable-statistics", "allegato": r"^Renewable electricity by local authority",
                       "nome": "solare_la.xlsx", "titolo": "Renewable electricity by local authority (Excel workbook)", "chi": "DESNZ, Energy Trends"},
    "solare_costi_xlsx": {"pagina": "government/statistics/solar-pv-cost-data", "allegato": r"TIC basis \(Excel\)$", "nome": "solare_costi_tic.xlsx",
                          "titolo": "Solar PV cost data, Total Installed Capacity basis (Excel workbook)", "chi": "DESNZ, data from the Microgeneration Certification Scheme (MCS)"},
    "solare_et63_xlsx": {"pagina": "government/statistics/energy-trends-section-6-renewables", "allegato": r"^Solar photovoltaics deployment \(Excel\)",
                         "nome": "solare_et63.xlsx", "titolo": "Solar photovoltaics deployment, Energy Trends table 6.3 (Excel workbook)", "chi": "DESNZ, Energy Trends"},
}

# Pagine delle regole: frasi esatte (dopo aver tolto i tag e normalizzato spazi e apostrofi)
PAGINE = {
    "gov_apply": {"url": "https://www.gov.uk/apply-boiler-upgrade-scheme", "api": "apply-boiler-upgrade-scheme",
                  "titolo": "Apply for the Boiler Upgrade Scheme", "chi": "GOV.UK",
                  "cerca": ["This scheme is open to people in England and Wales.",
                            "The Boiler Replacement Scheme in Northern Ireland is now closed.",
                            "If you live in Scotland",
                            "New build properties which the developer is still building are not eligible.",
                            "you or the original owner built it yourself or you paid a builder to build it",
                            "If you move into a finished new build with a fossil fuel boiler, you may be able to get a grant for a heat pump under the scheme.",
                            "your property is off the gas grid",
                            "your property is in a rural location",
                            "You can get one grant per property.",
                            "£7,500 towards an air source heat pump (sometimes called an air-to-water heat pump)",
                            "£7,500 towards a ground source heat pump (including water source heat pumps and those on shared ground loops)",
                            "£5,000 towards a biomass boiler",
                            "£2,500 towards an air-to-air heat pump",
                            "Until March 2027, you can get an additional £1,500 towards an air source heat pump or ground source heat pump if both:",
                            "your property is heated by oil or LPG",
                            "you do not have a mains gas connection at the property",
                            "You cannot get a grant for a hybrid heat pump system",
                            "45kWth for individual systems",
                            "You cannot get a grant to replace a low carbon heating system.",
                            "own the property you're applying for (including if it's a business, a second home, or a property you rent out to tenants)",
                            "be replacing fossil fuel heating systems - such as oil, gas, electric or LPG (liquefied petroleum gas)",
                            "You're still eligible if you've already had funding to make your property more energy efficient, for example by insulating it.",
                            "Your installer must commission and install the heat pump within 120 days of applying for the grant",
                            "most new build properties",
                            "social housing",
                            "a property that's already been given government funding or support for a heat pump or biomass boiler",
                            "it's never been owned by a business or organisation",
                            "Contact suitable MCS certified installers to get quotes for the work.",
                            "The installer will apply on your behalf on the Ofgem website.",
                            "The value of the grant will be taken off the amount you pay for installation."]},
    "ofgem_bus": {"url": "https://www.ofgem.gov.uk/environmental-and-social-schemes/boiler-upgrade-scheme-bus",
                  "titolo": "Boiler Upgrade Scheme (BUS): about the scheme", "chi": "Ofgem",
                  "cerca": ["This scheme is open in England and Wales.",
                            "£9,000 off the cost and installation of air-to-water or ground source heat pumps in eligible off-gas grid properties. This is available until 31 March 2027.",
                            "£7,500 off the cost and installation of air-to-water heat pumps, ground source heat pumps and water source heat pumps",
                            "£5,000 off the cost and installation of biomass boilers",
                            "£2,500 off the cost and installation of air-to-air heat pumps for residential properties only",
                            "The scheme is installer-led."]},
    "ofgem_owners": {"url": "https://www.ofgem.gov.uk/environmental-and-social-schemes/boiler-upgrade-scheme-bus/property-owners",
                     "titolo": "Boiler Upgrade Scheme: property owners", "chi": "Ofgem",
                     "cerca": ["(available from 21 July 2026 until 31 March 2027)",
                               "From 1 April 2022 to 31 March 2027, there is 0% VAT on the installation of energy-saving materials including heat pumps and biomass boilers.",
                               "The value of the grant for your chosen technology should be provided to you as an upfront discount on the quote provided to you by your installer.",
                               "As with all home improvements we recommend that you obtain quotes from multiple installers.",
                               "If we do not receive your confirmations of the above within 14 calendar days, we may reject the application.",
                               "your installer has three months from the moment the application is approved to complete the installation",
                               "(six months for ground source heat pumps)",
                               "The scheme is open to residential and non-residential properties in England and Wales.",
                               "non-residential buildings (where installing an air-to-air heat pump)",
                               "Hybrid heat pump systems, for example a combination of a fossil fuel boiler and an air source heat pump, are not eligible.",
                               "replace an existing fossil fuel or electric heating system",
                               "not replace an existing low-carbon heating system",
                               "can only be installed in rural properties",
                               "provided at lower than market value to people that could not have afforded it otherwise (including arrangements like shared ownership)",
                               "If your property has an Energy Performance Certificate (EPC), this will include a 'changes you could make' section",
                               "can only be installed in properties with no connection to the gas grid"]},
    "mcs_find": {"url": "https://mcscertified.com/find-an-installer/", "titolo": "Find an MCS certified installer", "chi": "Microgeneration Certification Scheme (MCS)",
                 "cerca": []},
}


def scarica(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.status, r.read()


def norm(t):
    t = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S | re.I)))
    t = t.replace("’", "'").replace("‘", "'").replace("\xa0", " ")
    return re.sub(r"\s+", " ", t)


def api(percorso):
    st, b = scarica(API + percorso)
    return json.loads(b.decode("utf-8"))


def trova_allegato(d):
    """Indirizzo, titolo e data di pubblicazione dell'allegato voluto; per le collezioni prima l'ultima uscita."""
    pag = api(d["pagina"])
    if d.get("collezione"):
        uscite = sorted(pag["links"]["documents"], key=lambda x: x.get("public_updated_at", ""), reverse=True)
        uscite = [u for u in uscite if "statistics-" in u["base_path"]]
        pag = api(uscite[0]["base_path"].lstrip("/"))
    for a in pag["details"].get("attachments", []):
        if re.search(d["allegato"], a.get("title", "")):
            data = pag.get("first_published_at") if d.get("collezione") else pag.get("public_updated_at")
            return a["url"], a["title"], data, "https://www.gov.uk" + pag["base_path"], pag.get("title")
    raise SystemExit(f"allegato {d['allegato']} non trovato in {d['pagina']}")


def main():
    GREZZI.mkdir(exist_ok=True)
    oggi = date.today().isoformat()
    definizioni, esiti = {}, {}
    for fid, d in FILE_STAT.items():
        url, titolo_all, pubblicato, pagina, titolo_pag = trova_allegato(d)
        st, b = scarica(url)
        (GREZZI / d["nome"]).write_bytes(b)
        definizioni[fid] = {"url": url, "pagina": pagina, "titolo": d["titolo"], "chi": d["chi"], "file": d["nome"], "titolo_allegato": titolo_all,
                            "uscita": titolo_pag, "tipo": "xlsx", "licenza": "Open Government Licence v3.0"}
        esiti[fid] = {"http": st, "letto_il": oggi, "sha256": hashlib.sha256(b).hexdigest(), "byte": len(b), "pubblicato": pubblicato}
        print(f"{fid}: {titolo_pag} -> {d['nome']} ({len(b):,} byte)")
    for pid, p in PAGINE.items():
        definizioni[pid] = {"url": p["url"], "titolo": p["titolo"], "chi": p["chi"], "tipo": "pagina", "cerca": p["cerca"]}
        try:
            if p.get("api"):
                dj = api(p["api"])
                corpo = " ".join(x.get("body", "") for x in dj["details"].get("parts", [])) or dj["details"].get("body", "")
                testo, st, agg = norm(corpo), 200, dj.get("public_updated_at")
            else:
                st, b = scarica(p["url"])
                testo, agg = norm(b.decode("utf-8", errors="replace")), None
            trovate = {c: (norm(c) in testo) for c in p["cerca"]}
            esiti[pid] = {"http": st, "letto_il": oggi, "aggiornata": agg, "sha256": hashlib.sha256(testo.encode("utf-8")).hexdigest(),
                          "trovate": trovate}
            manca = [c for c, ok in trovate.items() if not ok]
            print(f"{pid}: HTTP {st}, {len(trovate) - len(manca)}/{len(trovate)} frasi" + (f" MANCANO: {manca}" if manca else ""))
        except Exception as e:  # noqa: BLE001
            esiti[pid] = {"http": getattr(e, "code", str(e)[:80]), "letto_il": oggi, "trovate": {c: False for c in p["cerca"]}}
            print(f"{pid}: errore {e}", file=sys.stderr)
    FILE.write_text(json.dumps({"definizioni": definizioni, "fonti": esiti}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"-> {FILE}")


if __name__ == "__main__":
    main()
