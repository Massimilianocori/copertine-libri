"""Scarica il dataset ufficiale DGFiP "Tarifs taxe de séjour - Delta" (Licence Ouverte 2.0) e la capacità
turistica INSEE 2026, tiene solo le tariffe con data d'effetto 2026 e scrive due JSON compatti:

    touristtax/dati/francia.json      tutte le comuni con tariffe 2026 (vettori di tariffe deduplicati)
    touristtax/dati/francia_top.json  le 150 comuni con più posti turistici (criterio INSEE, vedi sotto)

Uso (dalla radice del repository):
    python3 -I touristtax/raccolta/francia.py [--cache CARTELLA]

I file grezzi vanno nella cartella di cache (default: la variabile TOURISTTAX_CACHE oppure /tmp/touristtax-fr).
Nessuna dipendenza esterna. Lo script non interpreta nulla dei file scaricati oltre al CSV/JSON.

Criterio per le pagine comunali (scritto prima di guardare i risultati): le 150 comuni con il maggior numero
di "places" in hébergement touristique secondo INSEE 2026 (somma di camere d'hotel I551, unità in altri
alloggi turistici I552 e piazzole di campeggio I553), tra quelle che hanno righe DELTA 2026.
"""
import csv
import io
import json
import os
import sys
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
DATASET = "delta_deliberation_ts_tarif0"
API = "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/" + DATASET
PAGINA_DATASET = "https://data.economie.gouv.fr/explore/dataset/" + DATASET + "/"
INSEE_URL = "https://api.insee.fr/melodi/file/DS_TOUR_CAP/DS_TOUR_CAP_2026_CSV_FR"
INSEE_PAGINA = "https://www.insee.fr/fr/statistiques/2021703"
ANNO = 2026
N_TOP = 150
CAMPI = ["siren", "date_effet", "def_prov", "departement", "commune", "libelle_commune", "hebergement", "regime", "tarif",
         "unite", "tarif_total", "taxe_add_dep",
         "taxe_add_article_l_2531_18_du_code_general_des_collectivites_territoriales",
         "taxe_add_article_l_2531_17_du_code_general_des_collectivites_territoriales",
         "taxe_add_article_l_4332_4_du_code_general_des_collectivites_territoriales",
         "taxe_add_article_l_4332_5_du_code_general_des_collectivites_territoriales",
         "taxe_add_article_l_4332_6_du_code_general_des_collectivites_territoriales",
         "loyer_seuil_jour", "loyer_seuil_semaine", "loyer_seuil_mois",
         "periode_1", "periode_2", "periode_3", "periode_4", "periode_5", "periode_6"]

# Categorie DELTA -> (id breve, etichetta inglese). L'ordine è quello mostrato sul sito.
CATEGORIE = [
    ("Palaces", "palace", "Palace"),
    ("Hôtels de tourisme 5 étoiles", "h5", "Hotel 5 stars"),
    ("Hôtels de tourisme 4 étoiles", "h4", "Hotel 4 stars"),
    ("Hôtels de tourisme 3 étoiles", "h3", "Hotel 3 stars"),
    ("Hôtels de tourisme 2 étoiles", "h2", "Hotel 2 stars"),
    ("Hôtels de tourisme 1 étoile", "h1", "Hotel 1 star"),
    ("Résidences de tourismes 5 étoiles", "r5", "Tourist residence 5 stars"),
    ("Résidences de tourismes 4 étoiles", "r4", "Tourist residence 4 stars"),
    ("Résidences de tourismes 3 étoiles", "r3", "Tourist residence 3 stars"),
    ("Résidences de tourismes 2 étoiles", "r2", "Tourist residence 2 stars"),
    ("Résidences de tourisme 1 étoile", "r1", "Tourist residence 1 star"),
    ("Meublés de tourisme 5 étoiles", "m5", "Classified holiday rental (meublé) 5 stars"),
    ("Meublés de tourisme 4 étoiles", "m4", "Classified holiday rental (meublé) 4 stars"),
    ("Meublés de tourisme 3 étoiles", "m3", "Classified holiday rental (meublé) 3 stars"),
    ("Meublés de tourisme 2 étoiles", "m2", "Classified holiday rental (meublé) 2 stars"),
    ("Meublés de tourisme 1 étoile", "m1", "Classified holiday rental (meublé) 1 star"),
    ("Villages de vacances 4 et 5 étoiles", "v45", "Holiday village 4-5 stars"),
    ("Villages de vacances 1, 2 et 3 étoiles", "v123", "Holiday village 1-3 stars"),
    ("Chambres d’hôtes", "ch", "Chambre d'hôtes (B&B)"),
    ("Auberges collectives", "ac", "Hostel (auberge collective)"),
    ("Hébergements sans classement ou en attente de classement", "nc",
     "Unclassified accommodation (most Airbnb-type rentals)"),
    ("Terrains de camping et terrains de caravanage classés en 3, 4 et 5 étoiles", "c345", "Campsite 3-5 stars"),
    ("Terrains de camping et terrains de caravanage classés en 1 et 2 étoiles", "c12", "Campsite 1-2 stars"),
    ("Emplacements dans des aires de camping-cars", "cc", "Motorhome area (per 24 h)"),
    ("Ports de plaisance", "port", "Marina"),
]


def scarica(url, dest):
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=600) as r, open(dest, "wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)
    return dest


def cat_id(lib):
    for pref, cid, _ in CATEGORIE:
        if lib.startswith(pref[:40]):
            return cid
    return None


def numero(x):
    if x in (None, ""):
        return None
    try:
        return float(str(x).replace(",", "."))
    except ValueError:
        return None


def codice_insee(dep, com):
    dep = dep.strip()
    if len(dep) == 1:
        dep = "0" + dep
    com = com.strip()
    if len(dep) == 3:  # oltremare: 971 + 2 cifre
        return dep + com.zfill(3)[-2:]
    return dep.zfill(2) + com.zfill(3)


def main():
    cache = Path(os.environ.get("TOURISTTAX_CACHE", "/tmp/touristtax-fr"))
    if "--cache" in sys.argv:
        cache = Path(sys.argv[sys.argv.index("--cache") + 1])
    cache.mkdir(parents=True, exist_ok=True)

    meta = json.loads(urllib.request.urlopen(urllib.request.Request(API, headers={"User-Agent": UA}), timeout=60).read())
    modificato = meta["metas"]["default"].get("modified", "")[:10]
    licenza = meta["metas"]["default"].get("license", "")

    url_csv = (API + "/exports/csv?delimiter=%3B&select=" + "%2C".join(CAMPI) +
               "&where=year(date_effet)%3D" + str(ANNO))
    f_csv = scarica(url_csv, cache / f"delta_{ANNO}_{modificato}.csv")
    f_insee = scarica(INSEE_URL, cache / "insee_tour_cap_2026.zip")

    comuni = {}
    with open(f_csv, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f, delimiter=";"):
            cid = cat_id(r["hebergement"])
            if cid is None:
                print("categoria sconosciuta:", r["hebergement"], file=sys.stderr)
                continue
            code = codice_insee(r["departement"], r["commune"])
            c = comuni.setdefault(code, {"nome": r["libelle_commune"].strip(), "dep": r["departement"].strip(),
                                         "righe": {}, "def": set(), "siren": set()})
            c["def"].add(r["def_prov"])
            c["siren"].add(r["siren"])
            add = 0.0
            for k in ("taxe_add_dep", "taxe_add_article_l_2531_18_du_code_general_des_collectivites_territoriales",
                      "taxe_add_article_l_2531_17_du_code_general_des_collectivites_territoriales",
                      "taxe_add_article_l_4332_4_du_code_general_des_collectivites_territoriales",
                      "taxe_add_article_l_4332_5_du_code_general_des_collectivites_territoriales",
                      "taxe_add_article_l_4332_6_du_code_general_des_collectivites_territoriales"):
                add += numero(r.get(k)) or 0.0
            periodi = [r[f"periode_{i}"] for i in range(1, 7) if r.get(f"periode_{i}")]
            riga = {"t": numero(r["tarif"]), "u": "%" if r["unite"].strip() == "%" else "€", "tot": numero(r["tarif_total"]),
                    "add": round(add, 4), "reg": "F" if r["regime"].lower().startswith("forfait") else "R", "per": periodi}
            # campeggi: due righe con la stessa etichetta iniziale -> distinguere per testo
            if cid in ("c345", "c12"):
                cid = "c12" if "1 et 2" in r["hebergement"] else "c345"
            vecchia = c["righe"].get(cid)
            if vecchia and vecchia != riga:
                c.setdefault("conflitti", []).append(cid)
            c["righe"][cid] = riga

    # INSEE: posti turistici per comune (I551 + I552 + I553, PLACE, totale)
    posti, nomi, dipartimenti = {}, {}, {}
    with zipfile.ZipFile(f_insee) as z:
        nome_meta = [n for n in z.namelist() if n.endswith("_metadata.csv")][0]
        with z.open(nome_meta) as fb:
            for r in csv.DictReader(io.TextIOWrapper(fb, encoding="utf-8"), delimiter=";"):
                if r["COD_VAR"] == "GEO" and r["GEO_OBJECT"] == "COM":
                    nomi[r["COD_MOD"]] = r["LIB_MOD"]
                elif r["COD_VAR"] == "GEO" and r["GEO_OBJECT"] == "DEP":
                    dipartimenti[r["COD_MOD"]] = r["LIB_MOD"]
        nome = [n for n in z.namelist() if n.endswith("_data.csv")][0]
        with z.open(nome) as fb:
            for r in csv.DictReader(io.TextIOWrapper(fb, encoding="utf-8"), delimiter=";"):
                if (r["GEO_OBJECT"] == "COM" and r["ACTIVITY"] in ("I551", "I552", "I553") and r["UNIT_LOC_RANKING"] == "_T"
                        and r["L_STAY"] == "_T" and r["TOUR_MEASURE"] == "PLACE"):
                    posti[r["GEO"]] = posti.get(r["GEO"], 0) + float(r["OBS_VALUE"] or 0)

    ordine = [c[1] for c in CATEGORIE]
    vettori, indice, uscita = [], {}, {}
    for code, c in sorted(comuni.items()):
        v = []
        for cid in ordine:
            rr = c["righe"].get(cid)
            v.append(None if rr is None else [rr["t"], rr["u"], rr["tot"], rr["add"], rr["reg"], rr["per"]])
        chiave = json.dumps(v, separators=(",", ":"), ensure_ascii=False)
        if chiave not in indice:
            indice[chiave] = len(vettori)
            vettori.append(v)
        # P = solo righe provvisorie; C = righe diverse per la stessa categoria (non si mostra la tariffa)
        flag = "C" if c.get("conflitti") else ("P" if c["def"] == {"PROVISOIRE"} else "")
        uscita[code] = [c["nome"], c["dep"], indice[chiave], int(posti.get(code, 0)), flag, nomi.get(code, "")]

    oggi = date.today().isoformat()
    dati = {"fonte": PAGINA_DATASET, "api": API, "licenza": licenza, "dataset_modificato": modificato,
            "controllato_il": oggi, "anno": ANNO, "insee": INSEE_PAGINA,
            "categorie": [[cid, lab, fr] for fr, cid, lab in CATEGORIE],
            "campi_vettore": ["tarif", "unite", "tarif_total", "taxe_add_pct_totale", "regime(R=reel,F=forfait)", "periodes"],
            "campi_comune": ["nome DGFiP", "dipartimento", "indice vettore", "posti INSEE", "flag (C conflitto, P provvisorio)",
                             "nome INSEE"],
            "dipartimenti": dipartimenti, "vettori": vettori, "comuni": uscita}
    DATI.mkdir(exist_ok=True)
    (DATI / "francia.json").write_text(json.dumps(dati, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    candidati = sorted((code for code in uscita if uscita[code][3] > 0 and uscita[code][4] != "C"),
                       key=lambda k: -uscita[k][3])[:N_TOP]
    top = {"criterio": ("Le 150 comuni con più posti in hébergement touristique (INSEE 2026: camere d'hotel + unità "
                        "in altri alloggi turistici + piazzole di campeggio), tra quelle con tariffe DELTA 2026."),
           "insee": INSEE_PAGINA, "comuni": [[code, uscita[code][5] or uscita[code][0], uscita[code][1], uscita[code][3]] for code in candidati]}
    (DATI / "francia_top.json").write_text(json.dumps(top, ensure_ascii=False, indent=0), encoding="utf-8")
    conflitti = sum(1 for c in comuni.values() if c.get("conflitti"))
    print(f"DELTA {ANNO}: {len(comuni)} comuni, {len(vettori)} vettori di tariffe diversi; dataset modificato il {modificato}; "
          f"comuni con righe in conflitto: {conflitti}; top {len(candidati)} scritte.")


if __name__ == "__main__":
    main()
