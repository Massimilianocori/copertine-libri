"""Controllo a campione: 10 numeri pubblicati, ricalcolati da zero con richieste dirette all'API OpenFEMA.

Uso (dalla radice del repository, dopo aggrega.py):
    python3 floodcost/raccolta/controllo_api.py

Non usa la cache né aggrega.py: scarica dall'API solo le righe che servono, con filtri scritti qui, e rifà il calcolo
con la libreria standard (statistics.median). Stampa una tabella Markdown da copiare in NOTE.md.
Le aree controllate sono scelte qui sotto (CAMPIONE); si possono cambiare a ogni aggiornamento.
"""
import json
import statistics
import sys
import urllib.parse
import urllib.request
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
API = "https://www.fema.gov/api/open"
F = json.loads((DATI / "fonti.json").read_text())
NAZ = json.loads((DATI / "nazionale.json").read_text())
ST = json.loads((DATI / "stati.json").read_text())
CO = json.loads((DATI / "contee.json").read_text())
ZI = json.loads((DATI / "zip.json").read_text())
RIF, RIF0 = F["rif"], F["rif_prec"]
CASE = {11, 12, 14, 16, 1, 2}


def leggi(url):
    req = urllib.request.Request(url, headers={"User-Agent": "floodcost-spot-check/1.0"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())


def url(ds, ver, **p):
    return f"{API}/v{ver}/{ds}?" + "&".join(f"${k}={urllib.parse.quote(str(v), safe=',()')}" for k, v in p.items())


def tutte(ds, ver, filtro, sel):
    out, skip = [], 0
    while True:
        d = leggi(url(ds, ver, filter=filtro, select=sel, top=10000, skip=skip, orderby="id"))
        righe = d[ds]
        out += righe
        if len(righe) < 10000:
            return out
        skip += 10000


def conta(ds, ver, filtro):
    return leggi(url(ds, ver, filter=filtro, top=1, select="id", inlinecount="allpages"))["metadata"]["count"]


def in_vigore(area, rif):
    a = f"{int(rif[:4]) - 1}{rif[4:]}"
    righe = tutte("NfipPolicies", 3, f"{area} and policyEffectiveDate gt '{a}' and policyEffectiveDate le '{rif}'",
                  "id,policyCost,occupancyType,ratedFloodZone,policyEffectiveDate,policyTerminationDate,cancellationDateOfFloodPolicy")
    ok = []
    for r in righe:
        c = r.get("policyCost")
        term = (r.get("policyTerminationDate") or "")[:10]
        canc = (r.get("cancellationDateOfFloodPolicy") or "")[:10]
        if c is None or c <= 0 or not term > rif or (canc and canc <= rif):
            continue
        ok.append(r)
    return ok


def case(righe, zona=None):
    out = [r["policyCost"] for r in righe if r.get("occupancyType") in CASE]
    if zona:
        out = [r["policyCost"] for r in righe if r.get("occupancyType") in CASE and (r.get("ratedFloodZone") or "").strip() in zona]
    return out


def mediana(v):
    return round(statistics.median(v)) if v else None


def scegli_zip(min_n, max_n):
    return sorted((z for z, v in ZI.items() if min_n <= v["h"][0] <= max_n), key=lambda z: -ZI[z]["h"][0])[0]


def main():
    ris = []

    def riga(descr, pubblicato, api, query):
        ris.append((descr, pubblicato, api, "OK" if pubblicato == api else "DIVERSO", query))
        print(ris[-1], file=sys.stderr)

    z = scegli_zip(300, 420)
    area_z = f"startswith(reportedZipCode,'{z}')"
    r = in_vigore(area_z, RIF)
    c = case(r)
    riga(f"ZIP {z}: home policies in force on {RIF}", ZI[z]["h"][0], len(c), area_z)
    riga(f"ZIP {z}: median annual cost, homes", ZI[z]["h"][1], mediana(c), area_z)
    zt = max(ZI[z]["z"], key=lambda k: ZI[z]["z"][k][0])
    etich = {"AE": {"AE"} | {f"A{i:02d}" for i in range(1, 31)} | {f"A{i}" for i in range(1, 31)}, "X": {"X", "B", "C"}, "A": {"A"},
             "VE": {"VE", "V"} | {f"V{i:02d}" for i in range(1, 31)} | {f"V{i}" for i in range(1, 31)}, "AO": {"AO", "AOB"}, "AH": {"AH", "AHB"}}
    riga(f"ZIP {z}: median, homes in zone {zt}", ZI[z]["z"][zt][1], mediana(case(r, etich[zt])), area_z + f" + ratedFloodZone in {zt}")
    r0 = in_vigore(area_z, RIF0)
    riga(f"ZIP {z}: median a year earlier ({RIF0})", ZI[z]["prev"]["h"][1], mediana(case(r0)), area_z)
    for st in ("VT", "WY"):
        if st in ST:
            area_s = f"propertyState eq '{st}'"
            rs = in_vigore(area_s, RIF)
            riga(f"{st}: median annual cost, homes", ST[st]["h"][1], mediana(case(rs)), area_s)
            break
    cty = sorted((k for k, v in CO.items() if 150 <= v["h"][0] <= 300), key=lambda k: k)[0]
    area_c = f"startswith(censusGeoid,'{cty}')"
    rc = in_vigore(area_c, RIF)
    riga(f"County {cty} ({CO[cty]['nome']}, {CO[cty]['st']}): home policies", CO[cty]["h"][0], len(case(rc)), area_c)
    # risarcimenti
    zc = "33904" if "33904" in ZI and ZI["33904"].get("c") else z
    f1 = f"startswith(reportedZipCode,'{zc}') and yearOfLoss ge {F['anno_sinistri_da']}"
    riga(f"ZIP {zc}: flood claims since {F['anno_sinistri_da']}", ZI[zc]["c"]["tot"][0], conta("NfipClaims", 3, f1), f1)
    f2 = f"yearOfLoss ge {F['anno_sinistri_da']}"
    riga(f"United States: flood claims since {F['anno_sinistri_da']}", NAZ["c"]["tot"][0], conta("NfipClaims", 3, f2), f2)
    anno = max(ZI[zc]["c"]["y"], key=lambda x: x[1])
    f3 = f"startswith(reportedZipCode,'{zc}') and yearOfLoss eq {anno[0]}"
    cl = tutte("NfipClaims", 3, f3, "id,amountPaidOnBuildingClaim,amountPaidOnContentsClaim,amountPaidOnIncreasedCostOfComplianceClaim")
    tot = sum((x.get("amountPaidOnBuildingClaim") or 0) + (x.get("amountPaidOnContentsClaim") or 0) + (x.get("amountPaidOnIncreasedCostOfComplianceClaim") or 0) for x in cl)
    riga(f"ZIP {zc}: total paid on {anno[0]} claims ($)", anno[3], round(tot), f3)
    pc = "12071" if "12071" in CO else next(iter(CO))
    p = leggi(url("NfipResidentialPenetrationRates", 1, filter=f"fipsCode eq '{pc}'"))["NfipResidentialPenetrationRates"][0]
    riga(f"County {pc}: share of homes in high-risk zones with NFIP policy", CO[pc]["pen"]["sfha"], p["resPenetrationRateSfha"], f"fipsCode eq '{pc}'")
    print("| # | Number checked | Published | Recomputed from API | Result | API filter |")
    print("|---|---|---|---|---|---|")
    for i, (d, a, b, e, q) in enumerate(ris, 1):
        print(f"| {i} | {d} | {a} | {b} | {e} | `{q}` |")


if __name__ == "__main__":
    main()
