"""Storico degli aumenti di gennaio della paga base militare, ricavato SOLO da fonti ufficiali:

1. le tabelle dello Schedule 8 degli ordini esecutivi "Adjustments of Certain Rates of Pay" (Federal Register, PDF su
   govinfo.gov): per ogni coppia di anni consecutivi si confrontano le stesse celle (grado × anzianità) lette dal livello
   di testo del PDF e si prende la mediana dei rapporti; l'aumento è quella mediana arrotondata allo 0,1 %;
2. la formula di legge (37 U.S.C. 1009(c)): aumento = variazione dell'ECI (salari, settore privato) tra i trimestri
   luglio-settembre di due e tre anni prima, arrotondata allo 0,1 %; i valori vengono dall'API pubblica del BLS.
3. lo stato del 2027: ricerca nel Federal Register di un ordine pubblicato dopo l'ultimo letto.

Scrive dati/storico.json. Uso: python3 milpay/raccolta/storico.py (dalla radice del repository).
"""
import json
import sys
import re
import statistics
import subprocess
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
CACHE = RADICE / "cache" / "fonti"
DATI = RADICE / "dati"
UA = {"User-Agent": "rete-siti-dati/1.0 (lettura delle tabelle ufficiali)"}

# anno di effetto (1° gennaio) -> documento del Federal Register con lo Schedule 8 di quell'anno
ORDINI = {2016: "2015-32582", 2017: "2016-31875", 2018: "2017-28160", 2019: "2019-00048", 2020: "2019-28286",
          2021: "2021-00040", 2022: "2021-28313", 2023: "2022-28474", 2024: "2023-28661", 2025: "2024-31466", 2026: "2025-23844"}
SERIE_ECI = "CIU2020000000000A"  # ECI, salari, settore privato, variazione percentuale su 12 mesi (BLS)
TOLLERANZA = 0.0006  # una cella "conferma" la mediana se il suo rapporto ne dista meno di 0,06 punti
MIN_CELLE = 40


def get(url, nome=None, dati=None):
    if nome and (CACHE / nome).exists():
        return (CACHE / nome).read_bytes()
    req = urllib.request.Request(url, data=dati, headers={**UA, **({"Content-Type": "application/json"} if dati else {})})
    with urllib.request.urlopen(req, timeout=120) as r:
        b = r.read()
    if nome:
        CACHE.mkdir(parents=True, exist_ok=True)
        (CACHE / nome).write_bytes(b)
    return b


RIGA = re.compile(r"^\s*([0OoWwEe])\s?[-–]\s?([0-9lI]{1,2})(E?)\*{0,4}\s+(.*)$")
NUM = re.compile(r"\$?\s?(\d{1,2},\d{3}\.\d0)")


def celle(testo):
    """{(grado, metà, k): valore} dal livello di testo: per ogni grado, la 1ª riga trovata è la metà 0 (fino a 18 anni), la 2ª la metà 1."""
    i = testo.find("Schedule 8")
    testo = testo[i:] if i >= 0 else testo
    visti, out = {}, {}
    for r in testo.splitlines():
        m = RIGA.match(r)
        if not m:
            continue
        g = ("O" if m.group(1) in "0Oo" else m.group(1).upper()) + "-" + m.group(2).replace("l", "1").replace("I", "1") + m.group(3)
        resto = re.sub(r"(\d),\s(\d{3}\.\d0)", r"\1,\2", m.group(4))
        tok = re.split(r"\s+", resto.strip())
        if len(tok) != 11:
            continue
        metà = visti.get(g, 0)
        visti[g] = metà + 1
        if metà > 1:
            continue
        for k, t in enumerate(tok):
            n = NUM.fullmatch(t)
            if n:
                out[(g, metà, k)] = float(n.group(1).replace(",", ""))
    return out


def testo_ocr(meta):
    """Per gli anni in cui il PDF non ha testo nelle tabelle: lettura ottica delle immagini dello Schedule 8
    (stesse funzioni di tabelle.py). Restituisce un testo con una riga per grado, come il livello di testo dei PDF."""
    import tabelle as T
    righe = []
    for iid in sorted(meta["images"]):
        if not iid.startswith("ED"):
            continue
        f = T.scarica(meta["images"][iid]["original_size"], f"{iid}.png")
        for ruota in (True, False):
            im = T.immagine(f, ruota)
            testa = T.tesseract([im.crop((0, 0, im.width, min(im.height, 600))).resize((im.width * 2 // 5, min(im.height, 600) * 2 // 5))], 6)[0]
            if "SCHEDULE 8" in testa.upper() and "MONTHLY BASIC PAY" in testa.upper():
                break
        else:
            continue
        if T.griglie(im):
            for tab in T.leggi_griglia(im, 0.4):
                righe += [" ".join(r) for r in tab]
        else:
            righe += T.leggi_per_righe(im)[0].splitlines()
    return "Schedule 8\n" + "\n".join(righe)


def main():
    oggi = date.today().isoformat()
    tabelle, fonti = {}, {}
    for anno, doc in ORDINI.items():
        meta = json.loads(get(f"https://www.federalregister.gov/api/v1/documents/{doc}.json", f"fr-{doc}.json"))
        get(meta["pdf_url"], f"{doc}.pdf")
        testo = subprocess.run(["pdftotext", "-layout", str(CACHE / f"{doc}.pdf"), "-"], capture_output=True, text=True, check=True).stdout
        eff = re.search(r"Schedule 8 is effective (\w+ \d+, ?\d{4})", re.sub(r"\s+", " ", testo))
        if not eff or not eff.group(1).replace(" ", "").endswith(str(anno)) or "January" not in eff.group(1):
            raise SystemExit(f"{doc}: lo Schedule 8 non risulta in vigore dal 1° gennaio {anno} ({eff.group(1) if eff else 'frase non trovata'})")
        tabelle[anno] = celle(testo)
        fonte_celle = "testo del PDF"
        if len(tabelle[anno]) < 100:
            tabelle[anno] = celle(testo_ocr(meta))
            fonte_celle = "lettura ottica delle immagini (il PDF non ha testo nelle tabelle)"
        fonti[anno] = {"ordine_esecutivo": meta["executive_order_number"], "firmato_il": meta["signing_date"], "citazione": meta["citation"],
                       "documento": doc, "url": meta["html_url"], "pdf": meta["pdf_url"], "celle_lette": len(tabelle[anno]), "celle_da": fonte_celle}
    # ECI dal BLS: variazione su 12 mesi del trimestre luglio-settembre (serie "A" = 12-month percent change).
    # Senza chiave il BLS dà al massimo 10 anni per richiesta e un numero limitato di richieste al giorno: si parte dai
    # valori già letti (dati/storico.json) e si aggiorna con quello che l'API restituisce oggi.
    prima = json.loads((DATI / "storico.json").read_text()) if (DATI / "storico.json").exists() else {}
    eci = {int(k): v for k, v in prima.get("eci", {}).get("q3_12_mesi", {}).items()}
    eci_letti_il = dict(prima.get("eci", {}).get("letti_il", {}))
    for url in (f"https://api.bls.gov/publicAPI/v2/timeseries/data/{SERIE_ECI}?startyear={date.today().year - 9}&endyear={date.today().year}",
                f"https://api.bls.gov/publicAPI/v2/timeseries/data/{SERIE_ECI}"):
        d = json.loads(get(url))
        if d.get("status") == "REQUEST_SUCCEEDED":
            for x in d["Results"]["series"][0]["data"]:
                if x["period"] == "Q03":
                    eci[int(x["year"])] = float(x["value"])
                    eci_letti_il[x["year"]] = oggi
            break
        print("BLS:", d.get("status"), d.get("message"))
    for anno_eci in range(min(ORDINI), max(ORDINI)):
        if anno_eci not in eci:
            raise SystemExit(f"ECI {anno_eci} Q3 mancante: rilanciare domani (limite giornaliero del BLS)")
    righe = []
    anni = sorted(tabelle)
    for a in range(anni[0] + 1, max(anni) + 2):
        r = {"anno": a}
        if a - 2 in eci:
            r["eci_formula"] = eci[a - 2]  # 37 U.S.C. 1009(c): trimestre base dell'anno prima del precedente
            r["eci_trimestre"] = f"{a - 2} Q3"
        if a in tabelle and a - 1 in tabelle:
            comuni = [k for k in tabelle[a] if k in tabelle[a - 1]]
            rapporti = [tabelle[a][k] / tabelle[a - 1][k] for k in comuni]
            if len(rapporti) >= MIN_CELLE:
                med = statistics.median(rapporti)
                conferme = sum(1 for x in rapporti if abs(x - med) < TOLLERANZA)
                if conferme >= MIN_CELLE:  # altrimenti la lettura non basta: si mostra solo la cifra della formula
                    r["tabelle"] = {"aumento": round((med - 1) * 100 + 1e-9, 1), "celle_confrontate": len(rapporti), "celle_alla_mediana": conferme,
                                    "celle_diverse": len(rapporti) - conferme}
        righe.append(r)
    # stato del 2027: c'è un ordine pubblicato dopo l'ultimo letto?
    q = urllib.parse.urlencode({"conditions[term]": '"Adjustments of Certain Rates of Pay"', "conditions[type][]": "PRESDOCU",
                                "conditions[publication_date][gte]": f"{max(anni)}-01-01", "per_page": 20})
    nuovi = json.loads(get("https://www.federalregister.gov/api/v1/documents.json?" + q))
    out = {
        "letto_il": oggi,
        "metodo": "aumento dalle tabelle = mediana dei rapporti cella per cella tra due Schedule 8 consecutivi (livello di testo dei PDF GPO), arrotondata allo 0,1 %",
        "fonti_tabelle": {str(k): v for k, v in fonti.items()},
        "eci": {"serie": SERIE_ECI, "descrizione": "Employment Cost Index, wages and salaries, private industry workers, 12-month percent change (BLS)",
                "url_api": f"https://api.bls.gov/publicAPI/v2/timeseries/data/{SERIE_ECI}", "q3_12_mesi": {str(k): v for k, v in sorted(eci.items())},
                "letti_il": eci_letti_il},
        "aumenti": righe,
        "ricerca_2027": {"data": oggi, "query": f"Adjustments of Certain Rates of Pay, Presidential Documents, published from {max(anni)}-01-01",
                         "risultati": nuovi.get("count", 0), "documenti": [r["document_number"] for r in nuovi.get("results", [])]},
    }
    (DATI / "storico.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for r in righe:
        print(r["anno"], r.get("tabelle", {}).get("aumento"), r.get("eci_formula"), r.get("tabelle", {}).get("celle_alla_mediana"), "/", r.get("tabelle", {}).get("celle_confrontate"))
    print("ricerca 2027:", out["ricerca_2027"]["risultati"])


if __name__ == "__main__":
    main()
