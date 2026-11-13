"""Scarica le serie ufficiali dei prezzi al consumo in inflation/dati/grezzi/ e scrive inflation/dati/fonti.json.

Uso (dalla radice del repository), una volta al mese dopo le uscite ufficiali:
    python3 -I inflation/raccolta/scarica.py          # BLS (pagina dati), ONS (5 CSV), Destatis (cartella di lavoro + tabella HTML)
    python3 -I inflation/raccolta/scarica.py --api    # in più: copia di controllo delle serie BLS dall'API pubblica (12 richieste)

Solo indirizzi pubblici che rispondono 200 al nostro server; nessun blocco aggirato (il file piatto download.bls.gov
risponde 403 e non si usa). Ogni file grezzo ha accanto in fonti.json: URL, data di lettura, HTTP, SHA-256, licenza.
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
from xml.etree import ElementTree as ET

RADICE = Path(__file__).resolve().parent.parent
GREZZI = RADICE / "dati" / "grezzi"
FONTI = RADICE / "dati" / "fonti.json"
UA = "Mozilla/5.0 (compatible; static-data-site-check/1.0)"
OGGI = date.today().isoformat()

LIC_BLS = {"nome": "Public domain (U.S. federal government work, 17 U.S.C. § 105)",
           "url": "https://www.bls.gov/opub/copyright-information.htm",
           "nota": "BLS: material on its website is in the public domain and may be reproduced without permission; citation requested."}
LIC_ONS = {"nome": "Open Government Licence v3.0", "url": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
           "attribuzione": "Source: Office for National Statistics licensed under the Open Government Licence v.3.0",
           "verificata_su": "https://www.ons.gov.uk/help/terms-conditions"}
LIC_DESTATIS = {"nome": "© Statistisches Bundesamt (Destatis); Vervielfältigung und Verbreitung, auch auszugsweise, mit Quellenangabe gestattet "
                        "(Inhalte von GENESIS-Online: Datenlizenz Deutschland – Namensnennung – Version 2.0, dl-de/by-2-0)",
                "url": "https://www.destatis.de/DE/Service/Impressum/_inhalt.html",
                "attribuzione": "Quelle: Statistisches Bundesamt (Destatis)",
                "dl_de": "https://www.govdata.de/dl-de/by-2-0"}

URL_BLS = "https://data.bls.gov/timeseries/CUUR0000SA0?years_option=all_years&include_graphs=false&annualAveragesRequested=true"
URL_BLS_API = "https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear={a}&endyear={b}"
URL_BLS_CALC = "https://data.bls.gov/cgi-bin/cpicalc.pl?cost1={c}&year1={d1}&year2={d2}"
ONS = {
    "d7bt": "CPI INDEX 00: ALL ITEMS 2015=100",
    "cdko": "Retail Prices Index: Long run series (Jan 1974=100)",
    "chaw": "RPI All Items Index: Jan 1987=100",
    "d7g7": "CPI ANNUAL RATE 00: ALL ITEMS 2015=100",
    "czbh": "RPI All Items: Percentage change over 12 months",
}
URL_ONS = "https://www.ons.gov.uk/generator?format=csv&uri=/economy/inflationandpriceindices/timeseries/{s}/mm23"
URL_ONS_PAGINA = "https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/{s}/mm23"
URL_DE_XLSX = ("https://www.destatis.de/DE/Themen/Wirtschaft/Preise/Verbraucherpreisindex/Publikationen/Downloads-Verbraucherpreise/"
               "statistischer-bericht-verbraucherpreisindex-lange-reihen-5611103.xlsx?__blob=publicationFile&v=29")
URL_DE_TAB = "https://www.destatis.de/DE/Themen/Wirtschaft/Preise/Verbraucherpreisindex/Tabellen/Verbraucherpreise-12Kategorien.html"
URL_DE_PAGINA = "https://www.destatis.de/DE/Themen/Wirtschaft/Preise/Verbraucherpreisindex/_inhalt.html"

# Casi letti dal calcolatore ufficiale del BLS (CPI Inflation Calculator): importo, mese di partenza, mese di arrivo
CASI_BLS = [("100.00", "197001", None), ("1.00", "195006", None), ("1000.00", "198001", "202509"), ("50.00", "200001", "202001"),
            ("100.00", "191301", "202412"),
            # aggiunti dal controllo indipendente del 13/11/2026 (altri decenni, importi non tondi, arrivo nel passato)
            ("100.00", "196501", "202609"), ("250.00", "199003", "201507"), ("1.00", "192001", "202610"), ("1000.00", "200806", "202601"),
            ("75.50", "194412", "198005")]

MESI_DE = {"Januar": 1, "Februar": 2, "März": 3, "April": 4, "Mai": 5, "Juni": 6, "Juli": 7, "August": 8, "September": 9,
           "Oktober": 10, "November": 11, "Dezember": 12}
MESI_DE_BREVI = {"Jan": 1, "Feb": 2, "Mär": 3, "Apr": 4, "Mai": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Okt": 10, "Nov": 11, "Dez": 12}


def scarica(url):
    """(http, contenuto in byte) con curl attraverso il proxy dell'ambiente."""
    p = subprocess.run(["curl", "-s", "-L", "--max-time", "90", "-A", UA, "-w", "\n%{http_code}", url], capture_output=True)
    corpo, _, codice = p.stdout.rpartition(b"\n")
    return int(codice or 0), corpo


def sha(b):
    return hashlib.sha256(b).hexdigest()


def testo_celle(riga):
    return [html.unescape(re.sub(r"<[^>]+>", "", c)).replace("\xa0", " ").strip() for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", riga, re.S | re.I)]


# ---------------------------------------------------------------- USA
def bls(fonti):
    http, b = scarica(URL_BLS)
    if http != 200:
        raise SystemExit(f"BLS: HTTP {http}")
    t = b.decode("utf-8", "replace")
    righe = []
    for m in re.finditer(r'<TH scope="row">(\d{4})</TH>(.*?)</TR>', t, re.S | re.I):
        celle = [html.unescape(re.sub(r"<[^>]+>", "", c)).replace("\xa0", "").strip() for c in re.findall(r"<TD[^>]*>(.*?)</TD>", m.group(2), re.S | re.I)]
        righe.append([m.group(1)] + celle[:13])
    if len(righe) < 100:
        raise SystemExit("BLS: tabella non trovata o incompleta")
    with open(GREZZI / "bls_cpiu.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["year", "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec", "annual"])
        for r in righe:
            w.writerow((r + [""] * 14)[:14])
    serie = re.search(r"Series Title:</TH>\s*<TD[^>]*>(.*?)</TD>", t, re.S | re.I)
    fonti["bls_cpiu"] = {"chi": "U.S. Bureau of Labor Statistics", "titolo": "CPI for All Urban Consumers (CPI-U), U.S. city average, all items, "
                         "not seasonally adjusted (series CUUR0000SA0), 1982-84=100", "url": URL_BLS, "pagina": "https://data.bls.gov/timeseries/CUUR0000SA0",
                         "file": "grezzi/bls_cpiu.csv", "http": http, "letto_il": OGGI, "sha256_pagina": sha(b),
                         "titolo_letto": html.unescape(re.sub(r"<[^>]+>", "", serie.group(1))).strip() if serie else None, "licenza": LIC_BLS}
    print(f"BLS: {len(righe)} anni ({righe[0][0]}-{righe[-1][0]})")


def bls_api(fonti):
    righe = []
    for a in range(1913, 2027, 10):
        b = min(a + 9, date.today().year)
        for _ in range(4):
            http, corpo = scarica(URL_BLS_API.format(a=a, b=b))
            d = json.loads(corpo or b"{}")
            if d.get("status") == "REQUEST_SUCCEEDED":
                break
        else:
            raise SystemExit(f"API BLS {a}-{b}: {d.get('message')}")
        for x in d["Results"]["series"][0]["data"]:
            righe.append((x["year"], x["period"], x["value"], "; ".join(f.get("text", "") for f in x.get("footnotes", []) if f)))
    righe.sort()
    with open(GREZZI / "bls_api_controllo.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["year", "period", "value", "footnote"])
        w.writerows(righe)
    fonti["bls_api"] = {"chi": "U.S. Bureau of Labor Statistics", "titolo": "BLS Public Data API v2, series CUUR0000SA0 (control copy)",
                        "url": URL_BLS_API.format(a="AAAA", b="AAAA"), "file": "grezzi/bls_api_controllo.csv", "http": 200, "letto_il": OGGI, "licenza": LIC_BLS}
    print(f"API BLS: {len(righe)} mesi")


def bls_calcolatore(fonti):
    """Legge alcuni risultati dal calcolatore ufficiale del BLS (per i controlli di verifica.py)."""
    ultimo = None
    with open(GREZZI / "bls_cpiu.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1):
                if re.fullmatch(r"\d+\.\d+", r[m] or ""):
                    ultimo = f"{r['year']}{i:02d}"
    casi = []
    for c, d1, d2 in CASI_BLS:
        d2 = d2 or ultimo
        url = URL_BLS_CALC.format(c=c, d1=d1, d2=d2)
        http, b = scarica(url)
        m = re.search(r'id="answer">\s*\$([\d,]+\.\d\d)', b.decode("utf-8", "replace"))
        casi.append({"importo": float(c), "da": f"{d1[:4]}-{d1[4:]}", "a": f"{d2[:4]}-{d2[4:]}", "risultato_ufficiale": float(m.group(1).replace(",", "")) if m else None,
                     "url": url, "http": http, "letto_il": OGGI})
    (RADICE / "dati" / "esempi_bls.json").write_text(json.dumps({"_nota": "Risultati letti dal CPI Inflation Calculator ufficiale del BLS (data.bls.gov/cgi-bin/cpicalc.pl).",
                                                                  "casi": casi}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    fonti["bls_calc"] = {"chi": "U.S. Bureau of Labor Statistics", "titolo": "CPI Inflation Calculator", "url": "https://data.bls.gov/cgi-bin/cpicalc.pl",
                         "http": casi[0]["http"], "letto_il": OGGI, "licenza": LIC_BLS}
    print("Calcolatore BLS:", [(x["importo"], x["da"], x["a"], x["risultato_ufficiale"]) for x in casi])


# ---------------------------------------------------------------- Regno Unito
def ons(fonti):
    for s, titolo in ONS.items():
        http, b = scarica(URL_ONS.format(s=s))
        if http != 200 or not b.startswith(b'"Title"'):
            raise SystemExit(f"ONS {s}: HTTP {http}")
        (GREZZI / f"ons_{s}.csv").write_bytes(b)
        meta = dict((r[0], r[1] if len(r) > 1 else "") for r in csv.reader(io.StringIO(b.decode("utf-8"))) if r and not re.match(r"\d{4}", r[0]))
        fonti[f"ons_{s}"] = {"chi": "Office for National Statistics", "titolo": f"{meta.get('Title', titolo)} ({s.upper()}, dataset MM23)",
                            "url": URL_ONS.format(s=s), "pagina": URL_ONS_PAGINA.format(s=s), "file": f"grezzi/ons_{s}.csv", "http": http, "letto_il": OGGI,
                            "sha256": sha(b), "uscita": meta.get("Release date"), "prossima_uscita": meta.get("Next release"), "licenza": LIC_ONS}
        print(f"ONS {s}: {meta.get('Title')} · uscita {meta.get('Release date')}")


# ---------------------------------------------------------------- Germania
def _xlsx_foglio(b, nome_foglio):
    """Righe (liste di valori) di un foglio di una cartella .xlsx, senza librerie esterne."""
    z = zipfile.ZipFile(io.BytesIO(b))
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
          "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
    condivise = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns):
            condivise.append("".join(t.text or "" for t in si.iter("{%s}t" % ns["m"])))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    mappa = {r.get("Id"): r.get("Target") for r in rels}
    for sh in wb.find("m:sheets", ns):
        if sh.get("name") == nome_foglio:
            target = mappa[sh.get("{%s}id" % ns["r"])].lstrip("/")
            target = target if target.startswith("xl/") else "xl/" + target
            break
    else:
        raise SystemExit(f"foglio {nome_foglio} assente")
    righe = []
    for row in ET.fromstring(z.read(target)).iter("{%s}row" % ns["m"]):
        r = []
        for c in row.findall("m:c", ns):
            v = c.find("m:v", ns)
            if v is None:
                isv = c.find("m:is", ns)
                r.append("".join(t.text or "" for t in isv.iter("{%s}t" % ns["m"])) if isv is not None else "")
            elif c.get("t") == "s":
                r.append(condivise[int(v.text)])
            else:
                r.append(v.text)
        righe.append(r)
    return righe


def destatis(fonti):
    http, b = scarica(URL_DE_XLSX)
    if http != 200 or not b.startswith(b"PK"):
        raise SystemExit(f"Destatis xlsx: HTTP {http}")
    titolo = " ".join(" ".join(r) for r in _xlsx_foglio(b, "Titel")[:3])
    impressum = " ".join(" ".join(r) for r in _xlsx_foglio(b, "Impressum"))
    tenere = {("Deutschland", "Verbraucherpreisindex"), ("Früheres Bundesgebiet", "Alle privaten Haushalte")}
    out = []
    for foglio, tipo in (("csv-611xx-01", "jahr_index"), ("csv-611xx-02", "jahr_rate"), ("csv-611xx-03", "monat_index")):
        righe = _xlsx_foglio(b, foglio)
        for r in righe[1:]:
            if len(r) < 7 or (r[1], r[3].strip()) not in tenere:
                continue
            if tipo == "monat_index":
                out.append([tipo, r[1], r[3].strip(), r[4], r[5], MESI_DE[r[6].strip()], r[7]])
            else:
                out.append([tipo, r[1], r[3].strip(), r[4], r[5], "", r[6]])
    with open(GREZZI / "destatis_lange_reihen.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["tabelle", "gebiet", "reihe", "einheit", "jahr", "monat", "wert"])
        w.writerows(out)
    fonti["destatis_lange_reihen"] = {"chi": "Statistisches Bundesamt (Destatis)", "titolo": "Statistischer Bericht – Verbraucherpreisindex für Deutschland – Lange Reihen ab 1948 "
                                      "(Tabellen 611xx-01, -02, -03; Ausgabe 10. Juli 2025)", "url": URL_DE_XLSX, "pagina": URL_DE_PAGINA,
                                      "file": "grezzi/destatis_lange_reihen.csv", "http": http, "letto_il": OGGI, "sha256": sha(b),
                                      "titolo_letto": titolo.strip(), "impressum_letto": impressum.strip()[-160:], "licenza": LIC_DESTATIS}
    print(f"Destatis lange Reihen: {len(out)} righe ({titolo.strip()[:80]})")

    http, b = scarica(URL_DE_TAB)
    if http != 200:
        raise SystemExit(f"Destatis tabella: HTTP {http}")
    t = b.decode("utf-8", "replace")
    out = []
    for tab in re.findall(r"<table.*?</table>", t, re.S | re.I)[:1] + re.findall(r"<table.*?</table>", t, re.S | re.I)[3:4] + \
            re.findall(r"<table.*?</table>", t, re.S | re.I)[6:7] + re.findall(r"<table.*?</table>", t, re.S | re.I)[9:10]:
        cap = html.unescape(re.sub(r"<[^>]+>", " ", (re.search(r"<caption[^>]*>(.*?)</caption>", tab, re.S) or [None, ""])[1]))
        cap = re.sub(r"\s+", " ", cap).strip()
        tipo = ("monat" if "Monat" in tab[:3000] else "jahr") + ("_rate" if "Veränderungsraten" in cap else "_index")
        anno = None
        for r in re.findall(r"<tr.*?</tr>", tab, re.S | re.I):
            c = testo_celle(r)
            if not c or not re.match(r"(\d{4}|[A-ZÄ][a-zä]{2})$", c[0]):
                continue
            if re.fullmatch(r"\d{4}", c[0]):
                anno = int(c[0])
                c = c[1:] if tipo.startswith("monat") else c
            if tipo.startswith("monat"):
                if c[0] not in MESI_DE_BREVI:
                    continue
                out.append([tipo, anno, MESI_DE_BREVI[c[0]], c[1].replace(",", ".")])
            else:
                out.append([tipo, anno, "", c[1].replace(",", ".")])
    visti, uniche = set(), []
    for r in out:
        k = tuple(r[:3])
        if k not in visti:
            visti.add(k)
            uniche.append(r)
    with open(GREZZI / "destatis_12kategorien.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["tabelle", "jahr", "monat", "wert"])
        w.writerows(uniche)
    stand = re.search(r"Stand(?::|&nbsp;|\s)\s*(\d{1,2}\.\s*[A-Za-zä]+\s+\d{4})", t)
    fonti["destatis_tabelle"] = {"chi": "Statistisches Bundesamt (Destatis)", "titolo": "Verbraucherpreisindex für Deutschland, 2020=100: Monate und Jahre, "
                                 "Index und Veränderungsraten (Tabelle „Verbraucherpreisindex: Deutschland, Monate, Kategorien“)", "url": URL_DE_TAB,
                                 "file": "grezzi/destatis_12kategorien.csv", "http": http, "letto_il": OGGI, "sha256": sha(b),
                                 "stand": html.unescape(stand.group(1)).strip() if stand else None, "licenza": LIC_DESTATIS}
    print(f"Destatis Tabelle: {len(uniche)} valori; Stand {fonti['destatis_tabelle']['stand']}")


# ---------------------------------------------------------------- pagine citate per una frase (controllo che la frase ci sia ancora)
FRASI = [
    ("fed_target", "Board of Governors of the Federal Reserve System", "Why does the Federal Reserve aim for inflation of 2 percent over the longer run?",
     "https://www.federalreserve.gov/faqs/economy_14400.htm",
     ["inflation of 2 percent over the longer run, as measured by the annual change in the price index for personal consumption expenditures"]),
    ("ecb_euro", "European Central Bank", "Our currency: the euro (irrevocable conversion rates)", "https://www.ecb.europa.eu/euro/intro/html/index.en.html",
     ["1 DEM 1.95583 (Deutsche Mark)", "Germany 1957 1999 (cash since 2002)"]),
    ("eurlex_2866", "Rat der Europäischen Union", "Verordnung (EG) Nr. 2866/98 des Rates über die Umrechnungskurse zwischen dem Euro und den Währungen "
     "der Mitgliedstaaten, die den Euro einführen", "https://eur-lex.europa.eu/legal-content/DE/TXT/PDF/?uri=CELEX:31998R2866", ["1,95583 Deutsche Mark"]),
    # Il calcolatore della Banca d'Inghilterra usa un altro indice prima del 1988 (stime CPI modellate): le pagine UK lo dicono, con il suo esempio
    ("boe_calc", "Bank of England", "Inflation calculator", "https://www.bankofengland.co.uk/monetary-policy/inflation/inflation-calculator",
     ["CPI estimates before 1988 are modelled based on data collected for the Retail Price Index (RPI)", "The price index for 1975 = 17.78",
      "The price index for 1985 = 44.6"]),
]
# Indirizzi provati e non letti (mai aggirati): restano scritti in fonti.json e nella pagina "How we check"
NON_LETTE = {
    "bls_flat": {"url": "https://download.bls.gov/pub/time.series/cu/cu.data.1.AllItems", "motivo": "HTTP 403 (Access Denied) to our server; we use the BLS data viewer instead"},
    "bls_copyright": {"url": "https://www.bls.gov/opub/copyright-information.htm", "motivo": "HTTP 403 to our server (www.bls.gov); public-domain status of U.S. federal works per 17 U.S.C. § 105"},
    "genesis_api": {"url": "https://genesis.destatis.de/genesisWS/rest/2020/data/tablefile", "motivo": "HTTP 401: the GENESIS-Online web service needs a registered account; we use the Destatis downloads instead"},
}


def testo_pagina(b, url):
    if b.startswith(b"%PDF"):
        p = subprocess.run(["pdftotext", "-", "-"], input=b, capture_output=True)
        t = p.stdout.decode("utf-8", "replace")
    else:
        t = b.decode("utf-8", "replace")
        t = re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S | re.I)
        t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t)


def frasi(fonti):
    for fid, chi, titolo, url, cerca in FRASI:
        http, b = scarica(url)
        t = testo_pagina(b, url)
        trovate = {c: c in t for c in cerca}
        fonti[fid] = {"chi": chi, "titolo": titolo, "url": url, "http": http, "letto_il": OGGI, "sha256": sha(b), "cerca": cerca, "trovate": trovate}
        print(f"{fid}: HTTP {http}, frasi trovate {sum(trovate.values())}/{len(cerca)}")
    fonti["_non_lette"] = {k: dict(v, provato_il=OGGI) for k, v in NON_LETTE.items()}


def main():
    GREZZI.mkdir(parents=True, exist_ok=True)
    fonti = json.loads(FONTI.read_text(encoding="utf-8")) if FONTI.exists() else {}
    frasi(fonti)
    bls(fonti)
    if "--api" in sys.argv:
        bls_api(fonti)
    bls_calcolatore(fonti)
    ons(fonti)
    destatis(fonti)
    FONTI.write_text(json.dumps(fonti, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Scritto {FONTI}")


if __name__ == "__main__":
    main()
