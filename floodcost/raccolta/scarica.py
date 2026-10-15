"""Scarica da OpenFEMA i dati grezzi di Flood Insurance Cost in floodcost/cache/ (fuori da git).

Uso (dalla radice del repository):
    python3 floodcost/raccolta/scarica.py            # scarica tutto (circa 15-25 minuti)
    python3 floodcost/raccolta/scarica.py --solo-meta

Cosa scarica (solo i campi utili, formato CSV, compresso gzip):
  1. NfipPolicies v3 (https://www.fema.gov/api/open/v3/NfipPolicies): polizze con decorrenza nei 12 mesi prima di due
     date di riferimento (RIF_ATTUALE e RIF_PRECEDENTE, un anno prima), un file per mese di decorrenza.
     Paginazione "a chiave": filtro sul mese + id gt <ultimo id>, ordinate per id, 10.000 righe per richiesta
     (niente $skip profondi, lenti e instabili).
  2. NfipClaims v3 (https://www.fema.gov/api/open/v3/NfipClaims): tutti i risarcimenti (circa 2,7 milioni), a blocchi per anno.
  3. NfipResidentialPenetrationRates v1: quota di case assicurate per contea (3.159 righe).
  4. Census Bureau national_county2020.txt: nomi delle contee per codice FIPS.
  5. OpenFEMA DataSets v1: versione, data di aggiornamento e numero di righe di ogni dataset (per le date sulle pagine).

I file completi (bulk CSV/parquet) di OpenFEMA rispondono 403 dal nostro proxy (Akamai), per questo si usa l'API.
Se un file di un mese esiste già ed è completo (file .ok accanto) non si riscarica: per ripartire da zero cancellare cache/.
Le versioni dei dataset sono controllate all'inizio: se FEMA cambia versione (come la v2 spenta il 15/10/2026) lo script si ferma.
"""
import csv
import gzip
import io
import json
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timezone
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
CACHE = RADICE / "cache"
API = "https://www.fema.gov/api/open"
# Data di riferimento: polizze in vigore alla fine di questo giorno. Da spostare a ogni aggiornamento mensile
# all'ultimo giorno del mese completo prima dell'asOfDate di NfipPolicies (vedi NOTE.md).
RIF_ATTUALE = "2026-08-31"
RIF_PRECEDENTE = "2025-08-31"
VERSIONI_ATTESE = {"NfipPolicies": 3, "NfipClaims": 3, "NfipResidentialPenetrationRates": 1}
CAMPI_POLIZZE = ["id", "propertyState", "reportedZipCode", "censusGeoid", "ratedFloodZone", "occupancyType", "policyCost",
                 "totalInsurancePremiumOfThePolicy", "totalBuildingInsuranceCoverage", "totalContentsInsuranceCoverage",
                 "policyCount", "policyEffectiveDate", "policyTerminationDate", "cancellationDateOfFloodPolicy",
                 "primaryResidenceIndicator", "condominiumCoverageTypeCode", "nfipCommunityName", "nfipRatedCommunityNumber",
                 "crsClassCode"]
CAMPI_SINISTRI = ["id", "state", "reportedZipCode", "countyCode", "censusGeoid", "yearOfLoss", "dateOfLoss", "ratedFloodZone",
                  "occupancyType", "amountPaidOnBuildingClaim", "amountPaidOnContentsClaim",
                  "amountPaidOnIncreasedCostOfComplianceClaim"]
PAGINA = 10000
LAVORATORI = 4


def leggi(url, tentativi=6):
    for i in range(tentativi):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "floodcost-data-refresh/1.0 (static site, monthly)"})
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read()
        except Exception as e:  # rete o 5xx: si riprova con attesa crescente
            if i == tentativi - 1:
                raise
            print(f"  riprovo ({e}) {url[:120]}", file=sys.stderr)
            time.sleep(5 * (i + 1))


def url_api(ds, ver, **par):
    q = "&".join(f"${k}={urllib.parse.quote(str(v), safe=',')}" for k, v in par.items())
    return f"{API}/v{ver}/{ds}?{q}"


def metadati():
    nomi = ["NfipPolicies", "NfipClaims", "NfipResidentialPenetrationRates", "NfipCommunityStatusBook"]
    filtro = " or ".join(f"name eq '{n}'" for n in nomi)
    d = json.loads(leggi(url_api("DataSets", 1, filter=filtro,
                                 select="name,version,title,lastRefresh,lastDataSetRefresh,recordCount,dataDictionary,landingPage")))
    out = {}
    for x in d["DataSets"]:
        if x["name"] in out and out[x["name"]]["version"] > x["version"]:
            continue
        out[x["name"]] = x
    for n, v in VERSIONI_ATTESE.items():
        if n not in out:
            raise SystemExit(f"OpenFEMA: dataset {n} non trovato. Controllare https://www.fema.gov/about/openfema/data-sets")
        if out[n]["version"] != v:
            raise SystemExit(f"OpenFEMA: {n} è ora alla versione {out[n]['version']} (attesa {v}). Aggiornare scarica.py prima di continuare.")
    out["_scaricato_il"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    out["_rif"] = {"attuale": RIF_ATTUALE, "precedente": RIF_PRECEDENTE}
    (CACHE / "metadati.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


def scarica_blocco(ds, ver, campi, filtro, dest):
    """Tutte le righe che rispettano filtro, a pagine da 10.000 ordinate per id; scrive dest (.csv.gz) e dest.ok."""
    ok = dest.with_suffix(dest.suffix + ".ok")
    if dest.exists() and ok.exists():
        return dest.name, int(ok.read_text()), True
    ultimo, righe = 0, 0
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    with gzip.open(tmp, "wt", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(campi)
        while True:
            u = url_api(ds, ver, filter=f"({filtro}) and id gt {ultimo}", orderby="id", top=PAGINA, format="csv",
                         metadata="off", select=",".join(campi))
            testo = leggi(u).decode("utf-8")
            r = list(csv.reader(io.StringIO(testo)))
            if not r:
                break
            intest, dati = r[0], r[1:]
            if intest != campi:
                raise SystemExit(f"Intestazione inattesa da {ds}: {intest}")
            if not dati:
                break
            w.writerows(dati)
            righe += len(dati)
            ultimo = dati[-1][0]
            if len(dati) < PAGINA:
                break
    tmp.replace(dest)
    ok.write_text(str(righe))
    return dest.name, righe, False


def mesi(fine_iso):
    """I 12 mesi (inizio, fine esclusa) che finiscono il giorno fine_iso (ultimo giorno di un mese)."""
    f = date.fromisoformat(fine_iso)
    y, m = f.year, f.month
    out = []
    for _ in range(12):
        ini = date(y, m, 1)
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        out.append((ini.isoformat(), date(ny, nm, 1).isoformat()))
        y, m = (y - 1, 12) if m == 1 else (y, m - 1)
    return out


def lavori_polizze():
    out = []
    for rif in (RIF_ATTUALE, RIF_PRECEDENTE):
        cart = CACHE / "polizze" / rif
        cart.mkdir(parents=True, exist_ok=True)
        for ini, fin in mesi(rif):
            filtro = f"policyEffectiveDate ge '{ini}' and policyEffectiveDate lt '{fin}'"
            out.append(("NfipPolicies", 3, CAMPI_POLIZZE, filtro, cart / f"{ini[:7]}.csv.gz"))
    return out


def lavori_sinistri():
    cart = CACHE / "sinistri"
    cart.mkdir(parents=True, exist_ok=True)
    out = [("NfipClaims", 3, CAMPI_SINISTRI, "yearOfLoss lt 1990", cart / "fino-1989.csv.gz")]
    for a in range(1990, date.today().year + 1):
        out.append(("NfipClaims", 3, CAMPI_SINISTRI, f"yearOfLoss eq {a}", cart / f"{a}.csv.gz"))
    # righe senza anno: si contano a parte (non entrano negli anni)
    return out


def extra():
    d = json.loads(leggi(url_api("NfipResidentialPenetrationRates", 1, top=10000)))
    (CACHE / "penetrazione.json").write_text(json.dumps(d["NfipResidentialPenetrationRates"]), encoding="utf-8")
    (CACHE / "contee-census.txt").write_bytes(leggi("https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt"))


def main():
    CACHE.mkdir(exist_ok=True)
    m = metadati()
    print("Metadati:", {k: (v["version"], v["lastDataSetRefresh"], v["recordCount"]) for k, v in m.items() if not k.startswith("_")})
    if "--solo-meta" in sys.argv:
        return
    extra()
    lavori = lavori_polizze() + lavori_sinistri()
    inizio = time.time()
    with ThreadPoolExecutor(LAVORATORI) as ex:
        fut = [ex.submit(scarica_blocco, *l) for l in lavori]
        for i, f in enumerate(as_completed(fut), 1):
            nome, n, gia = f.result()
            print(f"[{i}/{len(lavori)}] {nome}: {n} righe{' (già in cache)' if gia else ''} · {time.time() - inizio:.0f}s", flush=True)
    print("Fatto.")


if __name__ == "__main__":
    main()
