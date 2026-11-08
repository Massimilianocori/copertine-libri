"""Produzione annua e mensile di un kit da balcone da 800 Wp per ogni città di dati/citta.json, dall'API PVGIS della
Commissione europea (Joint Research Centre). Scrive dati/pvgis.json.

Uso (dalla radice del repository):
    python3 solarebalcone/raccolta/pvgis.py            # tutte le città
    python3 solarebalcone/raccolta/pvgis.py --solo it  # un Paese

Due montaggi per città, entrambi rivolti a sud (aspect=0 in PVGIS):
    a35 = inclinato di 35° (supporto inclinato sul balcone o a terra)
    a90 = verticale (pannello appeso alla ringhiera)
Parametri fissi: peakpower=0.8 kWp, loss=14 % (perdite di sistema predefinite di PVGIS), tecnologia c-Si, banca dati
predefinita dell'API (oggi PVGIS-SARAH3), orizzonte calcolato dal modello del terreno (usehorizon=1, predefinito).
Licenza: "free for public use if the source is acknowledged (PVGIS © European Communities, 2001-2026)" (pagina
"Geospatial Data Download" del JRC, letta l'8/11/2026) e avviso legale della Commissione (CC BY 4.0).
Limite dell'API: 30 chiamate al secondo per indirizzo IP (pagina "API non-interactive service"): qui una ogni 0,2 s.
Solo libreria standard.
"""
import hashlib
import json
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path
from urllib.parse import urlencode

RADICE = Path(__file__).resolve().parents[1]
API = "https://re.jrc.ec.europa.eu/api/v5_3/PVcalc"
MONTAGGI = {"a35": 35, "a90": 90}
POTENZA_KWP = 0.8
PERDITE = 14


def url_pvgis(lat, lon, angolo):
    q = {"lat": f"{lat:.2f}", "lon": f"{lon:.2f}", "peakpower": POTENZA_KWP, "loss": PERDITE, "angle": angolo,
         "aspect": 0, "outputformat": "json"}
    return API + "?" + urlencode(q)


def leggi(url, tentativi=4):
    for n in range(tentativi):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "solarebalcone/1.0 (calcolatore pubblico, dati PVGIS)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, r.read()
        except Exception as e:  # rete lenta o 429: si riprova con calma
            if n == tentativi - 1:
                raise SystemExit(f"PVGIS non risponde per {url}: {e}")
            time.sleep(3 * (n + 1))


def estrai(corpo):
    d = json.loads(corpo)
    tot = d["outputs"]["totals"]["fixed"]
    mesi = d["outputs"]["monthly"]["fixed"]
    met = d["inputs"]["meteo_data"]
    return {
        "E_y": tot["E_y"], "E_m": [m["E_m"] for m in sorted(mesi, key=lambda m: m["month"])],
        "H_y": tot["H(i)_y"], "l_total": tot["l_total"],
        "elev": d["inputs"]["location"]["elevation"], "db": met["radiation_db"],
        "anni": f"{met['year_min']}-{met['year_max']}",
    }


def main():
    solo = sys.argv[sys.argv.index("--solo") + 1] if "--solo" in sys.argv else None
    citta = json.loads((RADICE / "dati" / "citta.json").read_text(encoding="utf-8"))
    dest = RADICE / "dati" / "pvgis.json"
    vecchio = json.loads(dest.read_text(encoding="utf-8")) if dest.exists() else {}
    out = {"_nota": ("Produzione PVGIS di un kit da 0,8 kWp rivolto a sud: a35 = inclinato 35°, a90 = verticale. E_y kWh/anno, "
                     "E_m kWh per mese (gen-dic), H_y irraggiamento annuo sul piano dei moduli (kWh/m²), l_total perdite totali %. "
                     "url = chiamata esatta all'API, sha256 = impronta della risposta JSON letta. Fonte: PVGIS © European "
                     "Communities, 2001-2026 (riuso libero citando la fonte)."),
           "api": API, "potenza_kwp": POTENZA_KWP, "perdite": PERDITE, "letto_il": date.today().isoformat(), "citta": {}}
    for paese, voci in citta.items():
        if paese.startswith("_"):
            continue
        for c in voci:
            chiave = f"{paese}/{c['slug']}"
            if solo and paese != solo:
                if chiave in vecchio.get("citta", {}):
                    out["citta"][chiave] = vecchio["citta"][chiave]
                continue
            voce = {"lat": c["lat"], "lon": c["lon"]}
            for m, ang in MONTAGGI.items():
                u = url_pvgis(c["lat"], c["lon"], ang)
                stato, corpo = leggi(u)
                if stato != 200:
                    raise SystemExit(f"PVGIS: HTTP {stato} per {chiave}")
                e = estrai(corpo)
                voce["elev"], voce["db"], voce["anni"] = e.pop("elev"), e.pop("db"), e.pop("anni")
                voce[m] = dict(e, url=u, http=stato, sha256=hashlib.sha256(corpo).hexdigest())
                time.sleep(0.2)
            out["citta"][chiave] = voce
            print(f"{chiave}: {voce['a35']['E_y']} kWh (35°), {voce['a90']['E_y']} kWh (90°)")
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Scritto {dest} ({len(out['citta'])} città).")


if __name__ == "__main__":
    main()
