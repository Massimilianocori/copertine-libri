"""Scarica le fonti ufficiali delle due sezioni "cifre che cambiano nel 2027" e le registra in dati/fonti.json.

  A. Regno Unito, cifre da aprile 2027 (pagine /uk/…): paga minima (GOV.UK e Low Pay Commission), pensione di Stato, sussidi e
     indennità di malattia (documento DWP «Proposed benefit and pension rates 2027 to 2028»).
  B. Tetti agli aumenti dell'affitto (pagine /rent-increase-cap/…): California (Attorney General, più gli indici BLS e DIR per
     rifare il conto), Oregon (DAS), Washington (Commerce), New York City (Rent Guidelines Board), Ontario, British Columbia, Saint Paul.

Uso (dalla radice del repository):
    python3 -I inflation/raccolta/regole2027.py

Solo pagine ufficiali che rispondono 200 al nostro server; nessun blocco aggirato (quelle che rispondono 403/404 sono elencate in
NON_LETTE e finiscono in fonti.json alla voce _non_lette). Per ogni fonte: URL, data di lettura, HTTP, SHA-256 e byte dell'originale,
testo estratto in dati/grezzi/regole2027/<id>.txt (quello su cui verifica.py cerca le frasi citate). Si tengono anche gli originali
che verifica.py rilegge per conto suo: le due pagine con le tabelle (DWP, Attorney General), il file Excel dell'Oregon e, per gli
indici BLS regionali, un CSV con la tabella della pagina dati.
Le cifre pubblicate stanno in dati/uk_2027.json e dati/affitti.json, ognuna con la fonte e la frase ufficiale da cui viene (scritte
dopo la lettura): questo script NON le cambia, ricontrolla solo che ogni frase sia ancora nel testo appena scaricato. Se una fonte
non risponde 200 o una frase non c'è più, esce con errore senza toccare fonti.json.
"""
import csv
import hashlib
import html
import io
import json
import re
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
CARTELLA = RADICE / "dati" / "grezzi" / "regole2027"
FONTI = RADICE / "dati" / "fonti.json"
DATI = (RADICE / "dati" / "uk_2027.json", RADICE / "dati" / "affitti.json")
UA = "Mozilla/5.0 (compatible; static-data-site-check/1.0)"
OGGI = date.today().isoformat()

OGL = "Contains public sector information licensed under the Open Government Licence v3.0."
GOVUK = "https://www.gov.uk"
BLS = "https://data.bls.gov/timeseries/{s}?years_option=all_years&include_graphs=false&annualAveragesRequested=true"

# id: (chi, titolo, url, tiene l'originale con questa estensione o None, attribuzione o None, data di pubblicazione scritta nella pagina o None)
ELENCO = {
    # ---- A. Regno Unito
    "uk27_nmw": ("GOV.UK", "National Minimum Wage and National Living Wage rates", GOVUK + "/national-minimum-wage-rates", None, OGL, None),
    "uk27_lpc": ("Low Pay Commission", "LPC recommendations take the National Living Wage to £13.21 (press release)",
                 GOVUK + "/government/news/lpc-recommendations-take-the-national-living-wage-to-1321", None, OGL, "28 October 2026"),
    "uk27_dwp_indice": ("Department for Work and Pensions", "Benefit and pension rates: 2027 to 2028 (publication page)",
                        GOVUK + "/government/publications/benefit-and-pension-rates-2027-to-2028", None, OGL, "11 November 2026"),
    "uk27_dwp": ("Department for Work and Pensions", "Proposed benefit and pension rates 2027 to 2028",
                 GOVUK + "/government/publications/benefit-and-pension-rates-2027-to-2028/proposed-benefit-and-pension-rates-2027-to-2028", "html", OGL,
                 "11 November 2026"),
    # guide GOV.UK: frasi di spiegazione (chi prende quale pensione, da che cosa dipende l'importo) e cifre in vigore, a conferma della colonna 2026-27
    "uk27_guida_nsp": ("GOV.UK", "The new State Pension: Eligibility", GOVUK + "/new-state-pension", None, OGL, None),
    "uk27_guida_nsp_importo": ("GOV.UK", "The new State Pension: What you'll get", GOVUK + "/new-state-pension/what-youll-get", None, OGL, None),
    "uk27_guida_bsp": ("GOV.UK", "The basic State Pension", GOVUK + "/state-pension", None, OGL, None),
    "uk27_guida_uc": ("GOV.UK", "Universal Credit: What you'll get", GOVUK + "/universal-credit/what-youll-get", None, OGL, None),
    "uk27_guida_ssp": ("GOV.UK", "Statutory Sick Pay (SSP): What you'll get", GOVUK + "/statutory-sick-pay/what-youll-get", None, OGL, None),
    # ---- B. affitti
    "rent_ca_oag": ("California Department of Justice, Office of the Attorney General", "Limits on Rent Increases", "https://oag.ca.gov/rentcaps", "html", None, None),
    "rent_ca_oag_inquilini": ("California Department of Justice, Office of the Attorney General", "Landlord-Tenant Issues", "https://oag.ca.gov/tenants", None, None, None),
    "rent_ca_dir": ("California Department of Industrial Relations", "California Consumer Price Index (1955-2026), all items",
                    "https://www.dir.ca.gov/OPRL/CPI/EntireCCPI.PDF", None, None, None),
    "rent_or_das": ("Oregon Department of Administrative Services, Office of Economic Analysis", "Rent Stabilization",
                    "https://www.oregon.gov/das/oea/pages/rent-stabilization.aspx", None, None, None),
    "rent_or_xlsx": ("Oregon Department of Administrative Services, Office of Economic Analysis", "Maximum Annual Rent Increase, 2027 (Excel file)",
                     "https://www.oregon.gov/das/oea/Documents/Oregon-Maximum-Annual-Rent-Increase-2027.xlsx", "xlsx", None, "30 September 2026"),
    "rent_wa_commerce": ("Washington State Department of Commerce", "HB 1217 Landlord Resource Center",
                         "https://www.commerce.wa.gov/housing-policy/hb1217-landlord-resource-center/", None, None, None),
    "rent_nyc_58": ("New York City Rent Guidelines Board", "2026-27 Apartment/Loft Order #58",
                    "https://rentguidelinesboard.cityofnewyork.us/2026-27-apartment-loft-order-58/", None, None, "25 June 2026"),
    "rent_nyc_57": ("New York City Rent Guidelines Board", "2025-26 Apartment/Loft Order #57",
                    "https://rentguidelinesboard.cityofnewyork.us/2025-26-apartment-loft-order-57/", None, None, None),
    "rent_on": ("Government of Ontario", "Residential rent increases", "https://www.ontario.ca/page/residential-rent-increases", None, None, None),
    "rent_bc": ("Government of British Columbia", "Rent increases",
                "https://www2.gov.bc.ca/gov/content/housing-tenancy/residential-tenancies/rent-rtb/rent-increases", None, None, None),
    "rent_stpaul": ("City of Saint Paul, Minnesota", "Rent Stabilization",
                    "https://www.stpaul.gov/departments/safety-inspections/rent-buy-sell-property/rent-stabilization", None, None, None),
}
# Indici BLS regionali (CPI-U, tutti i beni, non destagionalizzati): servono a rifare i tetti californiani e il conto dello Stato di Washington
SERIE_BLS = {
    "bls_cpi_la": ("CUURS49ASA0", "Los Angeles-Long Beach-Anaheim, CA"),
    "bls_cpi_sf": ("CUURS49BSA0", "San Francisco-Oakland-Hayward, CA"),
    "bls_cpi_riverside": ("CUURS49CSA0", "Riverside-San Bernardino-Ontario, CA"),
    "bls_cpi_sandiego": ("CUURS49ESA0", "San Diego-Carlsbad, CA"),
    "bls_cpi_seattle": ("CUURS49DSA0", "Seattle-Tacoma-Bellevue WA"),
}
LIC_BLS = {"nome": "Public domain (U.S. federal government work, 17 U.S.C. § 105)"}
NON_LETTE = {
    "uk_wms_uprating": {"url": "https://questions-statements.parliament.uk/written-statements/detail/2026-10-28/hcws427",
                        "motivo": "HTTP 403 (browser check) to our server; the DWP publication that lists the rates set out in this statement is read instead"},
    "ca_leginfo_1947_12": {"url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1947.12.",
                           "motivo": "HTTP 403 to our server; the rule and the regional figures are read on the California Attorney General's page"},
    "ca_sanjose_aro": {"url": "https://www.sanjoseca.gov/your-government/departments-offices/housing/renters-apartment-owners/apartment-rent-ordinance",
                       "motivo": "HTTP 403 to our server; the San Jose figure shown is the one in the Attorney General's chart"},
    "ca_la_rso": {"url": "https://housing.lacity.gov/residents/rso-overview",
                  "motivo": "page read (HTTP 200) but the yearly percentage is only in a linked PDF we did not find; the Los Angeles figure shown is the one in the Attorney General's chart"},
    "ca_sf_rentboard": {"url": "https://www.sf.gov/information--annual-allowable-rent-increases",
                        "motivo": "HTTP 404 on the address tried; the San Francisco figure shown is the one in the Attorney General's chart"},
}


def scarica(url):
    p = subprocess.run(["curl", "-s", "-L", "--max-time", "120", "-A", UA, "-w", "\n%{http_code}", url], capture_output=True)
    corpo, _, codice = p.stdout.rpartition(b"\n")
    return int(codice or 0), corpo


def normalizza(t):
    """Testo su cui si cercano le frasi: spazi unici, virgolette e trattini semplici (stessa regola di raccolta/irs.py)."""
    t = t.replace("­", "").replace("‑", "-").replace("‐", "-").replace(" ", " ").replace(" ", " ")
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    t = re.sub(r"[\x00-\x08\x0b\x0e-\x1f\x7f]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def _xlsx_testo(b):
    """Testo di un file xlsx senza librerie: stringhe condivise e valori di ogni foglio, nell'ordine delle celle."""
    z = zipfile.ZipFile(io.BytesIO(b))
    cond = [html.unescape("".join(re.findall(r"<t[^>]*>(.*?)</t>", si, re.S))) for si in
            re.findall(r"<si>(.*?)</si>", z.read("xl/sharedStrings.xml").decode("utf-8"), re.S)]
    out = []
    for nome in sorted(n for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$", n)):
        for attr, v in re.findall(r"<c\b([^>]*?)(?:/>|>(?:<f>.*?</f>|<f[^>]*/>)?<v>(.*?)</v></c>)", z.read(nome).decode("utf-8"), re.S):
            if v:
                out.append(cond[int(v)] if 't="s"' in attr else v)
    return " ".join(out)


def testo(b):
    if b.startswith(b"%PDF"):
        p = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", "-", "-"], input=b, capture_output=True)
        return normalizza(p.stdout.decode("utf-8", "replace"))
    if b.startswith(b"PK"):
        return normalizza(_xlsx_testo(b))
    t = b.decode("utf-8", "replace")
    t = re.sub(r"<(script|style|noscript)\b.*?</\1>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    m = re.search(r"<main\b.*?</main>", t, re.S | re.I)  # solo il contenuto della pagina, senza i menu (dove c'è <main>)
    t = m.group(0) if m else t
    return normalizza(html.unescape(re.sub(r"<[^>]+>", " ", t)))


def tabella_bls(b):
    """Righe [anno, gen…dic, media annua, 1° semestre, 2° semestre] della pagina dati BLS (celle vuote = mese non pubblicato)."""
    t = b.decode("utf-8", "replace")
    righe = []
    for m in re.finditer(r'<TH scope="row">(\d{4})</TH>(.*?)</TR>', t, re.S | re.I):
        celle = [html.unescape(re.sub(r"<[^>]+>", "", c)).replace("\xa0", "").strip() for c in re.findall(r"<TD[^>]*>(.*?)</TD>", m.group(2), re.S | re.I)]
        righe.append([m.group(1)] + (celle + [""] * 15)[:15])
    return righe


def frasi_citate():
    """{fonte: [frasi]} da dati/uk_2027.json e dati/affitti.json (ogni oggetto con «fonte» e «frase»)."""
    cerca = {}

    def giro(x):
        if isinstance(x, dict):
            if isinstance(x.get("fonte"), str) and isinstance(x.get("frase"), str):
                cerca.setdefault(x["fonte"], []).append(x["frase"])
            for v in x.values():
                giro(v)
        elif isinstance(x, list):
            for v in x:
                giro(v)
    for p in DATI:
        if p.exists():
            giro(json.loads(p.read_text(encoding="utf-8")))
    return cerca


def main():
    CARTELLA.mkdir(parents=True, exist_ok=True)
    fonti = json.loads(FONTI.read_text(encoding="utf-8"))
    errori, nuove, file_ = [], {}, {}
    for fid, (chi, titolo, url, tiene, attrib, pubbl) in ELENCO.items():
        http, b = scarica(url)
        if http != 200 or len(b) < 1000:
            errori.append(f"{fid}: HTTP {http} ({url})")
            continue
        t = testo(b)
        file_[CARTELLA / f"{fid}.txt"] = (t + "\n").encode("utf-8")
        if tiene:
            file_[CARTELLA / f"{fid}.{tiene}"] = b
        nuove[fid] = {"chi": chi, "titolo": titolo, "url": url, "http": http, "letto_il": OGGI, "sha256": hashlib.sha256(b).hexdigest(), "byte": len(b),
                      "testo": f"grezzi/regole2027/{fid}.txt", "originale": f"grezzi/regole2027/{fid}.{tiene}" if tiene else None}
        if attrib:
            nuove[fid]["attribuzione"] = attrib
            nuove[fid]["licenza"] = {"nome": "Open Government Licence v3.0", "url": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"}
        if pubbl:
            nuove[fid]["pubblicato"] = pubbl
        print(f"{fid}: {http}, {len(b)} byte, testo {len(t)} caratteri")
    for fid, (serie, area) in SERIE_BLS.items():
        url = BLS.format(s=serie)
        http, b = scarica(url)
        righe = tabella_bls(b) if http == 200 else []
        if len(righe) < 8 or area.split(",")[0].split("-")[0] not in b.decode("utf-8", "replace"):
            errori.append(f"{fid}: HTTP {http}, tabella BLS non trovata ({url})")
            continue
        buf = io.StringIO()
        w = csv.writer(buf, lineterminator="\n")
        w.writerow(["year", "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec", "annual", "half1", "half2"])
        w.writerows(righe)
        file_[CARTELLA / f"{fid}.csv"] = buf.getvalue().encode("utf-8")
        nuove[fid] = {"chi": "U.S. Bureau of Labor Statistics", "titolo": f"CPI for All Urban Consumers (CPI-U), {area}, all items, not seasonally adjusted (series {serie}), 1982-84=100"
                      if serie != "CUURS49CSA0" else f"CPI for All Urban Consumers (CPI-U), {area}, all items, not seasonally adjusted (series {serie})",
                      "url": url, "pagina": f"https://data.bls.gov/timeseries/{serie}", "file": f"grezzi/regole2027/{fid}.csv", "http": http, "letto_il": OGGI,
                      "sha256_pagina": hashlib.sha256(b).hexdigest(), "serie": serie, "licenza": LIC_BLS}
        print(f"{fid}: {http}, {len(righe)} anni")
    # frasi citate nei due file di dati: ancora nel testo appena scaricato?
    for fid, frasi in frasi_citate().items():
        if fid not in nuove:
            if fid in ELENCO or fid in SERIE_BLS:
                continue  # già in errore
            errori.append(f"{fid}: fonte citata nei dati ma non in ELENCO")
            continue
        p = CARTELLA / f"{fid}.txt"
        t = file_[p].decode("utf-8") if p in file_ else ""
        nuove[fid]["trovate"] = {f: (normalizza(f) in t) for f in dict.fromkeys(frasi)}
        mancano = [f for f, ok in nuove[fid]["trovate"].items() if not ok]
        if mancano:
            errori.append(f"{fid}: {len(mancano)} frasi non più nel testo, es. «{mancano[0][:90]}»")
    if errori:
        raise SystemExit("ERRORI (nessun file cambiato):\n" + "\n".join(errori))
    for p, b in file_.items():
        p.write_bytes(b)
    fonti.update(nuove)
    fonti["_non_lette"].update({k: dict(v, provato_il=OGGI) for k, v in NON_LETTE.items()})
    FONTI.write_text(json.dumps(fonti, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Scritto {FONTI}: {len(nuove)} fonti, {sum(len(v.get('trovate', {})) for v in nuove.values())} frasi ritrovate")


if __name__ == "__main__":
    sys.exit(main())
