"""Calcola i dati aggregati di Flood Insurance Cost da floodcost/cache/ e li scrive, compatti, in floodcost/dati/.

Uso (dalla radice del repository, dopo raccolta/scarica.py):
    python3 floodcost/raccolta/aggrega.py

Regole (spiegate anche nella pagina Methodology del sito e in NOTE.md):
- Polizza "in vigore" alla data di riferimento D: decorrenza <= D, scadenza (policyTerminationDate) > D,
  nessuna cancellazione (cancellationDateOfFloodPolicy) entro D. Si scartano le righe con policyCost nullo o <= 0
  (rimborsi, riscritture).
- Costo = policyCost di OpenFEMA (premio + reserve fund assessment + federal policy fee + surcharge HFIAA): quanto paga
  davvero l'assicurato in un anno. Mediana e percentili 25/75 con interpolazione lineare (come numpy/pandas).
- "Homes" (cifra principale) = occupancyType 11 (casa unifamiliare), 12 (edificio da 2-4 unità), 14 (casa mobile),
  16 (unità in un condominio), più i vecchi codici 1 e 2. Esclusi gli edifici interi da 5+ unità e le polizze dei
  condomini (13, 15) e i non residenziali (17, 18, 19, 4, 6), che hanno una tabella a parte.
- Celle con meno di MIN_CELLA (10) polizze o risarcimenti: non pubblicate (né il numero né gli importi).
- Nessun minimo, massimo o valore singolo: solo mediane, percentili, medie e conteggi di almeno 10 righe.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

import pandas as pd

RADICE = Path(__file__).resolve().parent.parent
CACHE = RADICE / "cache"
DATI = RADICE / "dati"
MIN_CELLA = 10
SOGLIA_CONTEA = 100   # polizze "homes" in vigore per avere una pagina di contea
SOGLIA_ZIP = 300      # polizze "homes" in vigore per avere una pagina di ZIP
ANNO_SINISTRI_DA = 1978

ZONE = ["VE", "AE", "A", "AO", "AH", "AR", "X", "D"]
OCC = {11: "sf", 1: "sf", 12: "mf", 2: "mf", 14: "mh", 16: "cu", 13: "rb", 15: "rb", 3: "rb",
       17: "nr", 18: "nr", 19: "nr", 4: "nr", 6: "nr"}
CASE = {"sf", "mf", "mh", "cu"}
STATI = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
    "PR": "Puerto Rico", "VI": "U.S. Virgin Islands", "GU": "Guam", "AS": "American Samoa", "MP": "Northern Mariana Islands"}


def gruppo_zona(z):
    z = (z or "").strip().upper()
    if not z:
        return None
    # A99 e AR prima della regola A1-A30: "A99" corrisponde anche a A\d{1,2} e finiva per errore in AE
    if z == "A99" or z.startswith("AR"):
        return "AR"
    if z == "AE" or re.fullmatch(r"A\d{1,2}", z):
        return "AE"
    if z == "A":
        return "A"
    if z in ("AO", "AOB"):
        return "AO"
    if z in ("AH", "AHB"):
        return "AH"
    if z in ("VE", "V") or re.fullmatch(r"V\d{1,2}", z):
        return "VE"
    if z in ("X", "B", "C"):
        return "X"
    if z == "D":
        return "D"
    return None


def leggi_polizze(rif):
    cart = CACHE / "polizze" / rif
    file = sorted(cart.glob("*.csv.gz"))
    if len(file) != 12:
        raise SystemExit(f"{cart}: attesi 12 file mensili, trovati {len(file)}. Rilanciare scarica.py.")
    df = pd.concat((pd.read_csv(f, dtype=str, keep_default_na=False) for f in file), ignore_index=True)
    righe = len(df)
    eff = df["policyEffectiveDate"].str[:10]
    term = df["policyTerminationDate"].str[:10]
    canc = df["cancellationDateOfFloodPolicy"].str[:10]
    costo = pd.to_numeric(df["policyCost"], errors="coerce")
    attiva = (eff <= rif) & (term > rif) & ((canc == "") | (canc > rif)) & (costo > 0)
    df = df[attiva].copy()
    df["cost"] = costo[attiva].astype(float)
    df["bcov"] = pd.to_numeric(df["totalBuildingInsuranceCoverage"], errors="coerce").fillna(0)
    df["ccov"] = pd.to_numeric(df["totalContentsInsuranceCoverage"], errors="coerce").fillna(0)
    df["units"] = pd.to_numeric(df["policyCount"], errors="coerce").fillna(1).clip(lower=1)
    df["zone"] = df["ratedFloodZone"].map(gruppo_zona)
    occ_num = pd.to_numeric(df["occupancyType"], errors="coerce")
    df["rr2"] = occ_num >= 11  # i codici a 2 cifre sono delle polizze Risk Rating 2.0 (dizionario dati FEMA)
    df["occ"] = occ_num.map(OCC)
    df["home"] = df["occ"].isin(CASE)
    df["st"] = df["propertyState"].str.strip().str.upper()
    z = df["reportedZipCode"].str[:5]
    df["zip"] = z.where(z.str.fullmatch(r"\d{5}") & (z != "00000"), "")
    g = df["censusGeoid"].str.strip()
    df["cty"] = g.str[:5].where(g.str.fullmatch(r"\d{11,12}"), "")
    df["comm"] = df["nfipCommunityName"].str.strip()
    print(f"{rif}: {righe:,} righe scaricate, {len(df):,} polizze in vigore con costo > 0", file=sys.stderr)
    return df[["st", "zip", "cty", "zone", "occ", "home", "cost", "bcov", "ccov", "units", "comm", "rr2"]]


def tondo(x):
    return None if x is None or pd.isna(x) else int(round(float(x)))


def stat(s):
    """[n, mediana, p25, p75, media] di una serie di costi, oppure None se meno di MIN_CELLA righe."""
    n = int(len(s))
    if n < MIN_CELLA:
        return None
    q = s.quantile([0.5, 0.25, 0.75])
    return [n, tondo(q.iloc[0]), tondo(q.iloc[1]), tondo(q.iloc[2]), tondo(s.mean())]


def blocco(df):
    """Statistiche di un'area (df già filtrato)."""
    h = df[df["home"]]
    out = {"n": int(len(df)), "u": int(df["units"].sum()), "h": stat(h["cost"])}
    if out["n"] < MIN_CELLA:
        return None
    if out["h"]:
        out["bcov"] = tondo(h["bcov"].median())
        out["ccov_pct"] = tondo(100 * (h["ccov"] > 0).mean())
        out["ccov"] = tondo(h.loc[h["ccov"] > 0, "ccov"].median()) if (h["ccov"] > 0).sum() >= MIN_CELLA else None
        zon = h["zone"].fillna("")
        out["sfha_pct"] = tondo(100 * zon.isin(["VE", "AE", "A", "AO", "AH", "AR"]).mean())
    out["z"] = {z: stat(h.loc[h["zone"] == z, "cost"]) for z in ZONE}
    out["z"] = {k: v for k, v in out["z"].items() if v}
    out["o"] = {}
    for o in ("sf", "mf", "mh", "cu", "rb", "nr"):
        s = stat(df.loc[df["occ"] == o, "cost"])
        if s:
            out["o"][o] = s
    return out


def prec(df):
    h = df[df["home"]]
    out = {"n": int(len(df)), "h": stat(h["cost"])}
    out["z"] = {z: stat(h.loc[h["zone"] == z, "cost"]) for z in ZONE}
    out["z"] = {k: v for k, v in out["z"].items() if v}
    return out


def per_gruppo(df, chiave, filtro=None):
    out = {}
    for k, g in df.groupby(chiave, sort=True):
        if not k or (filtro and k not in filtro):
            continue
        b = blocco(g)
        if b:
            out[k] = b
    return out


def per_gruppo_prec(df, chiave, filtro):
    return {k: prec(g) for k, g in df.groupby(chiave, sort=True) if k and k in filtro}


# ---------------------------------------------------------------- nomi
def nomi_contee():
    nomi = {}
    for riga in (CACHE / "contee-census.txt").read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
        p = riga.split("|")
        if len(p) >= 5:
            nomi[p[1] + p[2]] = p[4]
    for r in json.loads((CACHE / "penetrazione.json").read_text(encoding="utf-8")):
        f = r.get("fipsCode") or ""
        if f and f not in nomi and r.get("county"):
            nomi[f] = r["county"]
    return nomi


def pulisci_comunita(c):
    """'CAPE CORAL, CITY OF' -> 'Cape Coral'; 'LEE COUNTY *' -> 'Lee County (unincorporated areas)'."""
    c = (c or "").strip()
    if not c:
        return ""
    non_inc = c.endswith("*")
    c = c.rstrip("* ").strip()
    m = re.match(r"^(.*?),\s*(CITY|TOWN|VILLAGE|TOWNSHIP|BOROUGH|CITY AND COUNTY|CHARTER TOWNSHIP|PARISH|MUNICIPALITY|CONSOLIDATED GOVERNMENT|UNIFIED GOVERNMENT)\s+OF$", c)
    if m:
        c = m.group(1)

    def parola(w):
        if w.upper().startswith("MC") and len(w) > 2:
            return "Mc" + w[2:].capitalize()
        if w.upper() in ("OF", "AND", "THE", "DE", "LA", "DEL") and False:
            return w.lower()
        return w.capitalize() if not re.fullmatch(r"[IVX]+", w.upper()) else w.upper()

    c = " ".join("-".join(parola(x) for x in w.split("-")) for w in c.split())
    c = re.sub(r"\bSt\b\.?", "St.", c).replace("St..", "St.")
    return c + (" (unincorporated areas)" if non_inc else "")


def moda(df, chiave, campo):
    """Valore più frequente di campo per ogni chiave (a parità, il primo in ordine alfabetico)."""
    c = df.groupby([chiave, campo]).size().reset_index(name="n").sort_values([chiave, "n", campo], ascending=[True, False, True])
    return c.drop_duplicates(chiave).set_index(chiave)[campo].to_dict()


def conta_comunita(df, chiave):
    out = {}
    for (k, c), n in df[df["comm"] != ""].groupby([chiave, "comm"]).size().items():
        out.setdefault(k, []).append((int(n), c))
    return out


def comunita(tab, k, quante):
    """Comunità NFIP più frequenti tra le polizze dell'area (solo con almeno MIN_CELLA polizze)."""
    righe = sorted(tab.get(k, []), key=lambda x: (-x[0], x[1]))[:quante]
    return [[pulisci_comunita(c), n] for n, c in righe if n >= MIN_CELLA]


# ---------------------------------------------------------------- sinistri
def sinistri():
    file = sorted((CACHE / "sinistri").glob("*.csv.gz"))
    if not file:
        raise SystemExit("cache/sinistri vuota: rilanciare scarica.py")
    df = pd.concat((pd.read_csv(f, dtype=str, keep_default_na=False) for f in file), ignore_index=True)
    tot = sum(pd.to_numeric(df[c], errors="coerce").fillna(0) for c in
              ("amountPaidOnBuildingClaim", "amountPaidOnContentsClaim", "amountPaidOnIncreasedCostOfComplianceClaim"))
    out = pd.DataFrame({
        "st": df["state"].str.strip().str.upper(),
        "zip": df["reportedZipCode"].str[:5],
        "cty": df["censusGeoid"].str.strip().str[:5].where(df["censusGeoid"].str.strip().str.fullmatch(r"\d{11,12}"),
                                                            df["countyCode"].str.strip().where(df["countyCode"].str.strip().str.fullmatch(r"\d{5}"), "")),
        "anno": pd.to_numeric(df["yearOfLoss"], errors="coerce"),
        "paid": tot,
    })
    out["zip"] = out["zip"].where(out["zip"].str.fullmatch(r"\d{5}") & (out["zip"] != "00000"), "")
    out = out[out["anno"].notna()]
    out["anno"] = out["anno"].astype(int)
    out = out[out["anno"] >= ANNO_SINISTRI_DA]
    out["pagato"] = out["paid"] > 0
    print(f"sinistri: {len(df):,} righe, {len(out):,} con anno >= {ANNO_SINISTRI_DA}", file=sys.stderr)
    return out


def blocco_sinistri(g):
    """{'tot': [n, n pagati, totale pagato], 'y': [[anno, n, n pagati, totale pagato], ...]} con celle < 10 omesse."""
    n = int(len(g))
    if n < MIN_CELLA:
        return None
    pag = g[g["pagato"]]
    tot = [n, int(len(pag)), tondo(pag["paid"].sum())]
    if tot[1] < MIN_CELLA:
        tot[2] = None
    agg = g.groupby("anno").agg(n=("paid", "size"), np=("pagato", "sum"))
    somma = pag.groupby("anno")["paid"].sum()
    anni = []
    for a, r in agg.iterrows():
        if r["n"] < MIN_CELLA:
            continue
        np_ = int(r["np"])
        anni.append([int(a), int(r["n"]), np_ if np_ >= MIN_CELLA else None,
                     tondo(somma.get(a, 0)) if np_ >= MIN_CELLA else None])
    return {"tot": tot, "y": anni}


def sinistri_per(cl, chiave, filtro=None):
    out = {}
    for k, g in cl.groupby(chiave, sort=True):
        if not k or (filtro is not None and k not in filtro):
            continue
        b = blocco_sinistri(g)
        if b:
            out[k] = b
    return out


# ---------------------------------------------------------------- principale
def scrivi(nome, dati):
    (DATI / nome).write_text(json.dumps(dati, ensure_ascii=False, separators=(",", ":"), sort_keys=False), encoding="utf-8")


def main():
    meta = json.loads((CACHE / "metadati.json").read_text(encoding="utf-8"))
    rif, rif0 = meta["_rif"]["attuale"], meta["_rif"]["precedente"]
    DATI.mkdir(exist_ok=True)
    cur = leggi_polizze(rif)
    old = leggi_polizze(rif0)
    cl = sinistri()
    nomi_c = nomi_contee()
    pen = {r["fipsCode"]: r for r in json.loads((CACHE / "penetrazione.json").read_text(encoding="utf-8")) if r.get("fipsCode")}

    # ---- nazionale
    naz = blocco(cur)
    naz["prev"] = prec(old)
    naz["c"] = blocco_sinistri(cl)
    naz["rr2"] = [round(100 * float(old["rr2"].mean()), 1), round(100 * float(cur["rr2"].mean()), 1)]

    # ---- stati
    stati = per_gruppo(cur[cur["st"].isin(STATI.keys())], "st")
    prev_st = per_gruppo_prec(old, "st", stati)
    cl_st = sinistri_per(cl, "st", set(stati))
    for k, v in stati.items():
        v["nome"] = STATI[k]
        v["prev"] = prev_st.get(k)
        v["c"] = cl_st.get(k)

    # ---- contee (pagina se almeno SOGLIA_CONTEA polizze "homes"); le altre restano nell'indice di ricerca con i conteggi
    case_cty = cur[cur["home"] & (cur["cty"] != "")].groupby("cty").size()
    con_pagina = set(case_cty[case_cty >= SOGLIA_CONTEA].index)
    contee = per_gruppo(cur[cur["cty"].isin(con_pagina)], "cty")
    prev_c = per_gruppo_prec(old[old["cty"].isin(con_pagina)], "cty", contee)
    cl_c = sinistri_per(cl[cl["cty"].isin(con_pagina)], "cty", set(contee))
    comm_c = conta_comunita(cur[cur["home"] & cur["cty"].isin(con_pagina)], "cty")
    st_cty = moda(cur[cur["cty"] != ""], "cty", "st")
    for k, v in contee.items():
        v["nome"] = nomi_c.get(k, f"County {k}")
        v["st"] = st_cty.get(k, "")
        v["prev"] = prev_c.get(k)
        v["c"] = cl_c.get(k)
        p = pen.get(k)
        if p:
            v["pen"] = {"all": p.get("resPenetrationRate"), "sfha": p.get("resPenetrationRateSfha"),
                        "pif": p.get("resContractsInForce"), "pif_sfha": p.get("resContractsInForceSfha"),
                        "res": p.get("totalResStructures"), "res_sfha": p.get("totalResStructuresSfha"),
                        "asof": (p.get("asOfDate") or "")[:10]}
        v["comm"] = comunita(comm_c, k, 6)

    # ---- ZIP
    case_zip = cur[cur["home"] & (cur["zip"] != "")].groupby("zip").size()
    zip_pag = set(case_zip[case_zip >= SOGLIA_ZIP].index)
    zips = per_gruppo(cur[cur["zip"].isin(zip_pag)], "zip")
    prev_z = per_gruppo_prec(old[old["zip"].isin(zip_pag)], "zip", zips)
    cl_z = sinistri_per(cl[cl["zip"].isin(zip_pag)], "zip", set(zips))
    comm_z = conta_comunita(cur[cur["home"] & cur["zip"].isin(zip_pag)], "zip")
    sub = cur[cur["zip"] != ""]
    zip_cty = moda(sub[sub["cty"] != ""], "zip", "cty")
    zip_st = moda(sub, "zip", "st")
    for k, v in zips.items():
        v["st"] = zip_st.get(k, "")
        v["cty"] = zip_cty.get(k, "")
        v["prev"] = prev_z.get(k)
        v["c"] = cl_z.get(k)
        v["comm"] = comunita(comm_z, k, 4)

    # ---- indice di ricerca: ogni ZIP con almeno MIN_CELLA polizze "homes" -> [stato, contea, n, mediana, pagina sì/no]
    homes = cur[cur["home"] & (cur["zip"] != "")]
    agg = homes.groupby("zip")["cost"].agg(["size", "median"])
    indice_zip = {}
    for z, r in agg.iterrows():
        if r["size"] < MIN_CELLA:
            continue
        indice_zip[z] = [zip_st.get(z, ""), zip_cty.get(z, ""), int(r["size"]), tondo(r["median"]), 1 if z in zips else 0]
    # contee senza pagina con almeno MIN_CELLA polizze: per l'elenco nella pagina dello Stato e per la ricerca
    altre_c = {}
    hc = cur[cur["home"] & (cur["cty"] != "")]
    for k, g in hc.groupby("cty"):
        if k in contee or len(g) < MIN_CELLA:
            continue
        altre_c[k] = [st_cty.get(k, ""), nomi_c.get(k, f"County {k}"), int(len(g)), tondo(g["cost"].median())]

    # ---- zone per Stato (per le pagine delle zone): già in stati[*]["z"]
    fonti = {
        "rif": rif, "rif_prec": rif0, "scaricato_il": meta["_scaricato_il"][:10],
        "dataset": {k: {c: meta[k].get(c) for c in ("name", "version", "title", "lastRefresh", "lastDataSetRefresh", "recordCount", "dataDictionary")}
                    for k in ("NfipPolicies", "NfipClaims", "NfipResidentialPenetrationRates")},
        "soglie": {"min_cella": MIN_CELLA, "contea": SOGLIA_CONTEA, "zip": SOGLIA_ZIP},
        "anno_sinistri_da": ANNO_SINISTRI_DA,
        "generato_il": date.today().isoformat(),
    }
    scrivi("fonti.json", fonti)
    scrivi("nazionale.json", naz)
    scrivi("stati.json", stati)
    scrivi("contee.json", contee)
    scrivi("zip.json", zips)
    scrivi("indice.json", {"zip": indice_zip, "contee_altre": altre_c})
    print(f"Stati {len(stati)}, contee con pagina {len(contee)} (altre {len(altre_c)}), ZIP con pagina {len(zips)}, "
          f"ZIP nell'indice {len(indice_zip)}", file=sys.stderr)
    if "--distribuzione" in sys.argv:
        for s in (50, 100, 200, 300, 500):
            print(f"contee >= {s}: {(case_cty >= s).sum()}  ZIP >= {s}: {(case_zip >= s).sum()}", file=sys.stderr)


if __name__ == "__main__":
    main()
