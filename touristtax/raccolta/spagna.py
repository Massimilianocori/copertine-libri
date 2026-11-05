"""Conteggi ufficiali per la sezione /spain-holiday-let-licence/ (Spagna, case per affitti turistici).

Scarica quattro fonti di dati aperti e scrive SOLO conteggi per Comune (mai righe, nomi, indirizzi, email o telefoni):

    touristtax/dati/spagna_numeri.json

1. INE, statistica sperimentale "Medición del número de viviendas turísticas en España y su capacidad", tabelle 39363
   (case turistiche, posti letto) e 39366 (% sulle abitazioni), ultimo periodo (maggio 2026), per Spagna, Comunità e Comune.
2. Generalitat Valenciana, dataset "tur-gestur-vt" (CC BY 4.0): registro delle viviendas de uso turístico. Conteggio per Comune
   (codice INE = cod_provincia + cod_municipio) e per mese di iscrizione (fecha_alta).
3. Junta de Andalucía, OPEN RTA (CC BY 4.0): il file contiene nomi dei titolari, email e telefoni. Lo script legge solo
   tipo di oggetto, provincia, Comune e data di iscrizione; conta e butta via il resto in memoria. Nessuna riga viene scritta.
   Il Comune è un nome (non un codice): si abbina al codice INE con il nome normalizzato dentro la provincia.
4. Generalitat de Catalunya, dataset t2h3-cgys (Registre de Turisme de Catalunya): solo un'aggregazione SoQL lato server
   (conteggio per codice IDESCAT dei "Habitatges d'ús turístic"): nessun dato personale scaricato.

Uso (dalla radice del repository):
    python3 -I touristtax/raccolta/spagna.py [--cache CARTELLA]

Il file andaluso pesa circa 330 MB (JSON): il download può richiedere 10 minuti. Le serie mensili coprono i Comuni elencati
in dati/spagna_licenze.json ("comuni") e il totale della Comunità; i conteggi per Comune coprono tutti i Comuni.
Attenzione nella lettura: i registri contengono le case iscritte OGGI; una casa iscritta nel 2025 e cancellata dopo non
compare. Il numero "iscrizioni al mese" è quindi il numero di case ancora iscritte con quella data di iscrizione.
"""
import csv
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
import urllib.parse
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
INE_API = "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/{}?nult=1&tip=AM"
GVA_PKG = "https://dadesobertes.gva.es/api/3/action/package_show?id=tur-gestur-vt"
RTA_JSON = "https://datos.juntadeandalucia.es/api/v0/openrta/all?format=json"
RTA_DATA = "https://datos.juntadeandalucia.es/api/v0/openrta/search/lastUpdateData"
CAT_META = "https://analisi.transparenciacatalunya.cat/api/views/t2h3-cgys.json"
CAT_SOQL = "https://analisi.transparenciacatalunya.cat/resource/t2h3-cgys.json?$query="
PROV_AND = {"ALMERÍA": "04", "CÁDIZ": "11", "CÓRDOBA": "14", "GRANADA": "18", "HUELVA": "21", "JAÉN": "23", "MÁLAGA": "29", "SEVILLA": "41"}
MESI_SERIE = 24  # mesi completi nella serie mensile


def scarica(url, dest=None, tentativi=3):
    """curl con -C - (riprende i download interrotti, il file andaluso è grande). Restituisce (http, byte o None)."""
    for _ in range(tentativi):
        args = ["curl", "-sS", "-L", "-m", "900", "-w", "%{http_code}"]
        if dest:
            args += ["-C", "-", "-o", str(dest)]
        r = subprocess.run(args + [url], capture_output=True)
        if dest:
            codice = r.stdout.decode()[-3:]
            if codice in ("200", "206", "416"):
                return 200, None
        else:
            corpo, codice = r.stdout[:-3], r.stdout[-3:].decode()
            if codice == "200":
                return 200, corpo
    raise SystemExit(f"download non riuscito: {url} ({r.stderr.decode()[:200]})")


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blocco in iter(lambda: f.read(1 << 20), b""):
            h.update(blocco)
    return "sha256:" + h.hexdigest()


def norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z0-9]+", " ", t).strip()


def varianti(nome):
    """'Ejido, El' -> {'EJIDO EL', 'EL EJIDO'}; 'Alacant/Alicante' -> anche le due metà."""
    out = set()
    for parte in [nome] + nome.split("/"):
        n = norm(parte)
        out.add(n)
        m = re.match(r"^(.*?),\s*(El|La|Los|Las|L'|Els|Les|Es|Sa|Ses|O|A)$", parte.strip())
        if m:
            out.add(norm(m.group(2) + " " + m.group(1)))
    return out


def mesi_ultimi(oggi, n):
    """Gli ultimi n mesi completi prima del mese di oggi, dal più vecchio: ['2024-11', ..., '2026-10']."""
    a, m = oggi.year, oggi.month
    out = []
    for _ in range(n):
        m -= 1
        if m == 0:
            a, m = a - 1, 12
        out.append(f"{a}-{m:02d}")
    return out[::-1]


def ine():
    out = {"periodo": None, "spagna": {}, "comunita": {}, "comuni": {}}
    for tab in ("39363", "39366"):
        _, corpo = scarica(INE_API.format(tab))
        for s in json.loads(corpo):
            md = s["MetaData"]
            liv, chi = md[0], md[1]["Nombre"]
            if not s["Data"]:
                continue
            dato = s["Data"][0]
            periodo = f"{dato['Anyo']}-{dato['T3_Periodo'][1:]}"
            out["periodo"] = out["periodo"] or periodo
            if periodo != out["periodo"]:
                raise SystemExit(f"INE: periodi diversi nelle tabelle ({periodo} / {out['periodo']})")
            chiave = {"Viviendas turísticas": "case", "Plazas": "posti", "Plazas por vivienda turística": None,
                      "Porcentaje de viviendas turísticas sobre el total de viviendas censadas": "pct"}.get(chi)
            if not chiave or dato["Valor"] is None:
                continue
            v = dato["Valor"]
            v = int(v) if chiave != "pct" else v
            if liv["T3_Variable"] == "Total Nacional":
                out["spagna"][chiave] = v
            elif liv["T3_Variable"] == "Comunidades y Ciudades Autónomas":
                out["comunita"].setdefault(liv["Codigo"], {"nome": liv["Nombre"]})[chiave] = v
            elif liv["T3_Variable"] == "Municipios":
                out["comuni"].setdefault(liv["Codigo"], {"nome": liv["Nombre"]})[chiave] = v
    return out


def gva(cache, mesi, scelti):
    _, corpo = scarica(GVA_PKG)
    pkg = json.loads(corpo)["result"]
    ris = next(r for r in pkg["resources"] if r["format"].upper() == "CSV")
    f = cache / "gva-viviendas-turisticas.csv"
    if f.exists():
        f.unlink()
    scarica(ris["url"], f)
    righe = csv.DictReader(io.StringIO(f.read_text(encoding="utf-8")), delimiter=";")
    per_comune, per_mese, mese_tot = Counter(), defaultdict(Counter), Counter()
    n = 0
    for r in righe:
        n += 1
        cod = r["cod_provincia"] + r["cod_municipio"]
        per_comune[cod] += 1
        fa = r["fecha_alta"]  # gg/mm/aaaa
        mese = f"{fa[6:10]}-{fa[3:5]}" if len(fa) == 10 else ""
        mese_tot[mese] += 1
        if cod in scelti:
            per_mese[cod][mese] += 1
    return {"dataset": "https://dadesobertes.gva.es/es/dataset/tur-gestur-vt", "file": ris["url"], "licenza": pkg.get("license_title"),
            "aggiornato": pkg["metadata_modified"][:10], "file_sha256": sha_file(f), "totale": n,
            "per_comune": dict(sorted(per_comune.items())),
            "per_mese_totale": {m: mese_tot.get(m, 0) for m in mesi},
            "per_anno_totale": {a: sum(v for k, v in mese_tot.items() if k.startswith(a)) for a in sorted({k[:4] for k in mese_tot if k})[-4:]},
            "per_mese": {c: {m: per_mese[c].get(m, 0) for m in mesi} for c in sorted(scelti)}}


def rta(cache, mesi, scelti, nomi_ine):
    _, corpo = scarica(RTA_DATA)
    agg = json.loads(corpo)["date"][:10]
    f = cache / "openrta.json"
    if f.exists():
        f.unlink()
    scarica(RTA_JSON, f)
    impronta = sha_file(f)
    dati = json.loads(f.read_text(encoding="utf-8"))
    f.unlink()  # contiene dati personali: non resta nella cache
    indice = defaultdict(dict)  # provincia -> nome normalizzato -> codice INE
    for cod, nome in nomi_ine.items():
        for v in varianti(nome):
            indice[cod[:2]][v] = cod
    per_comune, per_mese, mese_tot, senza = Counter(), defaultdict(Counter), Counter(), Counter()
    n = 0
    for x in dati:
        if x.get("objects_type_id") != "Vivienda de uso turístico":
            continue
        n += 1
        prov = PROV_AND.get((x.get("provinces") or "").strip())
        cod = indice.get(prov, {}).get(norm(x.get("municipalities"))) if prov else None
        if not cod:
            senza[(x.get("provinces") or "?") + " / " + (x.get("municipalities") or "?")] += 1
            continue
        d = (x.get("registration_date") or "").strip()  # AAAAMMGG
        mese = f"{d[:4]}-{d[4:6]}" if re.fullmatch(r"\d{8}", d) else ""
        per_comune[cod] += 1
        mese_tot[mese] += 1
        if cod in scelti:
            per_mese[cod][mese] += 1
    del dati
    return {"dataset": "https://www.juntadeandalucia.es/datosabiertos/portal/dataset/openrta", "file": RTA_JSON, "licenza": "CC BY 4.0",
            "aggiornato": agg, "file_sha256": impronta, "totale": n, "non_abbinate": sum(senza.values()),
            "non_abbinate_esempi": dict(senza.most_common(10)),
            "per_comune": dict(sorted(per_comune.items())),
            "per_mese_totale": {m: mese_tot.get(m, 0) for m in mesi},
            "per_mese": {c: {m: per_mese[c].get(m, 0) for m in mesi} for c in sorted(scelti)}}


def cat():
    _, corpo = scarica(CAT_META)
    meta = json.loads(corpo)
    q = ("SELECT codi_municipi_idescat, count(*) AS n WHERE tipus_establiment = \"Habitatges d'ús turístic\" "
         "GROUP BY codi_municipi_idescat ORDER BY n DESC LIMIT 5000")
    _, corpo = scarica(CAT_SOQL + urllib.parse.quote(q))
    per_comune = Counter()
    for r in json.loads(corpo):
        per_comune[(r.get("codi_municipi_idescat") or "")[:5]] += int(r["n"])  # IDESCAT a 6 cifre: le prime 5 = codice INE
    return {"dataset": "https://analisi.transparenciacatalunya.cat/d/t2h3-cgys", "licenza": "Generalitat de Catalunya open data terms",
            "aggiornato": date.fromtimestamp(meta["rowsUpdatedAt"]).isoformat(), "totale": sum(per_comune.values()),
            "per_comune": dict(sorted(per_comune.items()))}


def main():
    cache = Path(sys.argv[sys.argv.index("--cache") + 1]) if "--cache" in sys.argv else Path(tempfile.mkdtemp(prefix="touristtax-es-"))
    cache.mkdir(parents=True, exist_ok=True)
    conf = json.loads((DATI / "spagna_licenze.json").read_text(encoding="utf-8"))
    oggi = date.today()
    mesi = mesi_ultimi(oggi, MESI_SERIE)
    scelti_gva = {c["ine"] for c in conf["comuni"] if c["registro"] == "gva"}
    scelti_rta = {c["ine"] for c in conf["comuni"] if c["registro"] == "rta"}
    I = ine()
    print(f"INE {I['periodo']}: Spagna {I['spagna']}, {len(I['comuni'])} Comuni")
    G = gva(cache, mesi, scelti_gva)
    print(f"Generalitat Valenciana: {G['totale']} case iscritte (aggiornato {G['aggiornato']})")
    nomi_and = {c: v["nome"] for c, v in I["comuni"].items() if c[:2] in PROV_AND.values()}
    R = rta(cache, mesi, scelti_rta, nomi_and)
    print(f"Junta de Andalucía: {R['totale']} viviendas de uso turístico (aggiornato {R['aggiornato']}), non abbinate al codice INE: {R['non_abbinate']}")
    C = cat()
    print(f"Catalunya: {C['totale']} habitatges d'ús turístic (aggiornato {C['aggiornato']})")
    out = {"_nota": "Solo conteggi. Generato da raccolta/spagna.py: non modificare a mano.", "scaricato_il": oggi.isoformat(),
           "mesi": mesi, "ine": I, "gva": G, "rta": R, "cat": C}
    (DATI / "spagna_numeri.json").write_text(json.dumps(out, ensure_ascii=False, indent=0, sort_keys=False) + "\n", encoding="utf-8")
    print("scritto", DATI / "spagna_numeri.json")


if __name__ == "__main__":
    main()
