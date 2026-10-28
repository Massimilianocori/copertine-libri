"""Scarica e legge i dati ufficiali su "quanti [cittadini di un Paese] si sono trasferiti in [Paese]" e scrive
visaincome/dati/trasferimenti.json (sezione "Moved to" del sito, dal 28/10/2026).

Uso (dalla radice del repository):
    python3 visaincome/raccolta/trasferimenti.py            # scarica (o riusa i file già in raccolta/_grezzi/) e scrive il JSON
    python3 visaincome/raccolta/trasferimenti.py --nuovo    # riscarica sempre i file ufficiali

Fonti (vedi NOTE.md, sezione del 28/10/2026):
1. Eurostat, dataset migr_resfirst "First permits by reason, length of validity and citizenship" (API JSON-stat,
   https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/migr_resfirst). Primi permessi di soggiorno (validi
   almeno 3 mesi) rilasciati a cittadini non UE, in persone, per Paese UE/EFTA, cittadinanza, motivo (famiglia, studio,
   lavoro, altro) e durata. Riuso libero citando la fonte (avviso di copyright Eurostat; CC BY 4.0). Aggiornamento annuale
   (l'anno 2025 è stato caricato il 22/10/2026), con revisioni quando i Paesi correggono i dati.
   Controlli: totale = somma dei 4 motivi; totale = somma delle 3 durate; UE-27 = somma dei 27 Stati (per ogni cittadinanza e anno).
2. IRCC (Canada), "Permanent Residents – Monthly IRCC Updates", file "Canada – Permanent Residents by Country of Citizenship"
   (CSV separato da tabulazioni, mensile dal 2015; Open Government Licence – Canada). Numeri arrotondati a 5 da IRCC,
   "--" = da 0 a 5 (non pubblicati; nota IRCC sul catalogo). Si sommano i mesi di ogni anno.
3. Home Office (Regno Unito), "Entry clearance visa applications and outcomes detailed datasets" (lo stesso XLSX di
   rifiuti.py, foglio Data_Vis_D02; Open Government Licence v3.0): visti concessi ("Issued") per nazionalità, anno della
   decisione e gruppo (Work, Study, Family). Se il file non c'è in raccolta/_grezzi/ lo scarica come rifiuti.py.
   Controllo: per il 2025 Q1-Q4 e il 2026 Q1-Q2 i concessi coincidono con dati/rifiuti.json (stesso file, altro programma).

Se un controllo fallisce, il JSON esistente NON viene toccato (esce con codice 1).
I file grezzi stanno in raccolta/_grezzi/ (esclusi da git).
"""
import csv
import io
import json
import sys
import urllib.parse
from collections import defaultdict
from datetime import date
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rifiuti import GREZZI, RADICE, allegati_uk, impronta, scarica  # noqa: E402

USCITA = RADICE / "dati" / "trasferimenti.json"
ANNI = [str(a) for a in range(2019, 2026)]  # serie mostrata nelle pagine (2019-2025)

# Cittadinanze coperte: codice Eurostat -> (nome nel file IRCC, nome nel file del Home Office).
# Le 12 della richiesta del 28/10/2026 (comprendono le 8 indicate dal rapporto di ricerca dello stesso giorno).
CITTADINANZE = {
    "US": ("United States of America", "United States"),
    "UK": ("United Kingdom and Overseas Territories", None),          # destinazione Regno Unito: non ha senso
    "CA": (None, "Canada"),                                           # destinazione Canada: non ha senso
    "AU": ("Australia", "Australia"),
    "IN": ("India", "India"),
    "PK": ("Pakistan", "Pakistan"),
    "NG": ("Nigeria", "Nigeria"),
    "PH": ("Philippines", "Philippines"),
    "CN": ("China, People's Republic of", "China"),
    "BR": ("Brazil", "Brazil"),
    "ZA": ("South Africa, Republic of", "South Africa"),
    "NZ": ("New Zealand", "New Zealand"),
}

# ---------------------------------------------------------------- 1. Eurostat
API_EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/migr_resfirst"
PAGINA_EUROSTAT = "https://ec.europa.eu/eurostat/databrowser/view/migr_resfirst/default/table"
METADATI_EUROSTAT = "https://ec.europa.eu/eurostat/cache/metadata/en/migr_resval_esms.htm"
COPYRIGHT_EUROSTAT = "https://ec.europa.eu/eurostat/help/copyright-notice"
MOTIVI = ["TOTAL", "FAM", "EDUC", "EMP", "OTH"]
DURATE = ["M3-5", "M6-11", "M_GE12"]
STATI_UE = ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "EL", "ES", "FR", "HR", "IT", "CY", "LV", "LT", "LU", "HU", "MT", "NL", "AT",
            "PL", "PT", "RO", "SI", "SK", "FI", "SE"]
EFTA = ["IS", "LI", "NO", "CH"]
DESTINAZIONI = ["EU27_2020"] + STATI_UE + EFTA  # UK (fino al 2019) e Serbia esclusi: la sezione copre UE-27 + EFTA


def url_eurostat():
    q = [("format", "JSON"), ("lang", "EN"), ("unit", "PER"), ("freq", "A")]
    q += [("citizen", c) for c in CITTADINANZE] + [("time", a) for a in ANNI]
    q += [("reason", m) for m in MOTIVI] + [("duration", d) for d in ["TOTAL"] + DURATE] + [("geo", g) for g in DESTINAZIONI]
    return API_EUROSTAT + "?" + urllib.parse.urlencode(q)


def leggi_jsonstat(d):
    """JSON-stat 2.0 di Eurostat -> {(dim1, dim2, ...): (valore, stato)} con le chiavi nell'ordine di d['id']."""
    ids, size = d["id"], d["size"]
    cat = {k: d["dimension"][k]["category"]["index"] for k in ids}
    inv = {k: {i: c for c, i in cat[k].items()} for k in ids}
    out = {}
    for pos in set(d["value"]) | set(d.get("status", {})):
        p, chiave = int(pos), []
        for k, s in zip(reversed(ids), reversed(size)):
            chiave.append(inv[k][p % s])
            p //= s
        out[tuple(reversed(chiave))] = (d["value"].get(pos), d.get("status", {}).get(pos))
    return out


def eurostat(nuovo, errori):
    dest = GREZZI / "eurostat-migr_resfirst.json"
    b, meta = scarica(url_eurostat(), dest, nuovo)
    d = json.loads(b)
    if d.get("error"):
        raise SystemExit(f"Eurostat: errore {d['error']}")
    if d["id"] != ["freq", "reason", "citizen", "duration", "unit", "geo", "time"]:
        errori.append(f"Eurostat: dimensioni inattese {d['id']}")
        return None, None
    celle = leggi_jsonstat(d)
    etichette = d["dimension"]["reason"]["category"]["label"]
    if [etichette.get(m) for m in MOTIVI] != ["Total", "Family reasons", "Education reasons", "Employment reasons", "Other reason"]:
        errori.append(f"Eurostat: motivi inattesi {etichette}")
    stati_val = d.get("extension", {}).get("status", {}).get("label", {})
    # dati[cittadinanza][destinazione][anno] = [totale, famiglia, studio, lavoro, altro, 3-5 mesi, 6-11 mesi, 12+ mesi] (None = non disponibile)
    # note[cittadinanza][destinazione][anno] = {indice: codice di stato}, solo dove Eurostat mette un segno (u, b, p...)
    dati, note, avvisi = {}, {}, []
    for c in CITTADINANZE:
        for g in DESTINAZIONI:
            for a in ANNI:
                riga, segni = [], {}
                for i, (m, du) in enumerate([(m, "TOTAL") for m in MOTIVI] + [("TOTAL", x) for x in DURATE]):
                    v, s = celle.get(("A", m, c, du, "PER", g, a), (None, None))
                    riga.append(int(v) if v is not None else None)
                    if s:
                        segni[i] = s
                if any(x is not None for x in riga):
                    dati.setdefault(c, {}).setdefault(g, {})[a] = riga
                if segni:
                    note.setdefault(c, {}).setdefault(g, {})[a] = segni
                if riga[0] is not None and None not in riga[1:5] and sum(riga[1:5]) != riga[0]:
                    errori.append(f"Eurostat {c} {g} {a}: motivi {riga[1:5]} non sommano al totale {riga[0]}")
                if riga[0] is not None and None not in riga[5:8] and sum(riga[5:8]) != riga[0]:
                    # succede nei dati ufficiali (Liechtenstein 2019): le durate di quella casella non si usano
                    avvisi.append(f"{c} {g} {a}: durate {riga[5:8]} ≠ totale {riga[0]}")
                    riga[5:8] = [None, None, None]
                    dati[c][g][a] = riga
    # UE-27 = somma dei 27 Stati (dove il totale UE c'è e tutti gli Stati hanno un valore)
    controllati = 0
    for c, per_g in dati.items():
        for a in ANNI:
            ue = per_g.get("EU27_2020", {}).get(a)
            stati = [per_g.get(g, {}).get(a) for g in STATI_UE]
            if ue and ue[0] is not None and all(s and s[0] is not None for s in stati):
                for i in range(5):
                    if None in [s[i] for s in stati] or ue[i] is None:
                        continue
                    if sum(s[i] for s in stati) != ue[i]:
                        errori.append(f"Eurostat {c} {a}: UE-27 {MOTIVI[i]} {ue[i]} diverso dalla somma degli Stati {sum(s[i] for s in stati)}")
                controllati += 1
    if controllati < len(CITTADINANZE) * len(ANNI) - 2 * len(ANNI):  # i britannici non hanno 2019-2020 (cittadini UE)
        errori.append(f"Eurostat: solo {controllati} totali UE-27 controllati")
    agg = d.get("updated", "")[:10]
    fonte = {"titolo": "First permits by reason, length of validity and citizenship (migr_resfirst)", "editore": "Eurostat",
             "url": API_EUROSTAT, "pagina": PAGINA_EUROSTAT, "metadati": METADATI_EUROSTAT, "formato": "JSON-stat (API)",
             "aggiornato_il": agg, "scaricato_il": meta.get("scaricato_il", date.today().isoformat()), "byte": len(b), "sha256": impronta(b),
             "licenza": "Eurostat copyright notice (free re-use with acknowledgement; CC BY 4.0)", "licenza_url": COPYRIGHT_EUROSTAT,
             "segni": stati_val, "totali_ue_controllati": controllati, "durate_scartate": avvisi}
    nomi_c = d["dimension"]["citizen"]["category"]["label"]
    nomi_g = d["dimension"]["geo"]["category"]["label"]
    return {"dati": dati, "note": note, "nomi_cittadinanze": nomi_c, "nomi_destinazioni": {g: nomi_g[g] for g in DESTINAZIONI}}, fonte


# ---------------------------------------------------------------- 2. Canada (IRCC)
CSV_IRCC = "https://www.ircc.canada.ca/opendata-donneesouvertes/data/ODP-PR-Citz.csv"
PAGINA_IRCC = "https://open.canada.ca/data/en/dataset/f7e5498e-0ad8-4417-85c9-9b8aff9b9eda"
LIC_IRCC = ("Open Government Licence – Canada", "https://open.canada.ca/en/open-government-licence-canada")
MESI_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def canada(nuovo, errori):
    dest = GREZZI / "ca-pr-citizenship.csv"
    b, meta = scarica(CSV_IRCC, dest, nuovo)
    righe = list(csv.reader(io.StringIO(b.decode("utf-8-sig")), delimiter="\t"))
    attesa = ["EN_YEAR", "EN_QUARTER", "EN_MONTH", "FR_ANNEÉ", "FR_TRIMESTRE", "FR_MOIS", "EN_COUNTRY_OF_CITIZENSHIP", "FR_PAYS_DE_CITOYENNETÉ", "TOTAL"]
    if righe[0] != attesa:
        errori.append(f"IRCC: intestazioni inattese {righe[0]}")
        return None, None
    mesi = set()
    somme = defaultdict(lambda: defaultdict(int))     # nome -> anno -> somma dei mesi
    nascosti = defaultdict(lambda: defaultdict(int))  # nome -> anno -> mesi "--" (da 0 a 5, non pubblicati)
    tot_anno = defaultdict(int)
    nomi = set()
    for r in righe[1:]:
        if len(r) != 9 or not r[0].strip():
            continue
        anno, mese, nome, v = r[0].strip(), r[2].strip(), r[6].strip(), r[8].strip().replace(",", "")
        if mese not in MESI_EN:
            errori.append(f"IRCC: mese inatteso {mese!r}")
            continue
        mesi.add(f"{anno}-{MESI_EN.index(mese) + 1:02d}")
        nomi.add(nome)
        if v == "--":
            nascosti[nome][anno] += 1
        elif v.isdigit():
            somme[nome][anno] += int(v)
            tot_anno[anno] += int(v)
        else:
            errori.append(f"IRCC: valore inatteso {v!r} ({nome} {anno} {mese})")
    ultimo = max(mesi)
    pieni = [a for a in ANNI if sum(1 for m in mesi if m.startswith(a)) == 12]
    if pieni != ANNI:
        errori.append(f"IRCC: anni senza 12 mesi tra {ANNI}: pieni {pieni}")
    anno_ytd = ultimo[:4] if ultimo[5:] != "12" else None
    out = {}
    for c, (n_ca, _) in CITTADINANZE.items():
        if n_ca is None:
            continue
        if n_ca not in nomi:
            errori.append(f"IRCC: cittadinanza {n_ca!r} non trovata")
            continue
        out[c] = {"nome": n_ca, "anni": {a: somme[n_ca][a] for a in ANNI + ([anno_ytd] if anno_ytd else [])},
                  "mesi_nascosti": {a: nascosti[n_ca][a] for a in ANNI if nascosti[n_ca][a]}}
    # Controllo di plausibilità con il rapporto del 28/10/2026 (cittadini USA: 10.640 / 9.325 / 7.510)
    if out.get("US", {}).get("anni", {}).get("2025") != 7510:
        errori.append(f"IRCC: cittadini USA 2025 = {out.get('US', {}).get('anni', {}).get('2025')}, atteso 7.510 (lettura del 28/10/2026)")
    fonte = {"titolo": "Canada – Permanent Residents by Country of Citizenship (monthly)", "editore": "Immigration, Refugees and Citizenship Canada (IRCC)",
             "url": CSV_IRCC, "pagina": PAGINA_IRCC, "formato": "CSV", "byte": len(b), "sha256": impronta(b),
             "scaricato_il": meta.get("scaricato_il", date.today().isoformat()), "ultima_modifica": meta.get("last_modified", ""),
             "ultimo_mese": ultimo, "anno_in_corso": anno_ytd, "licenza": LIC_IRCC[0], "licenza_url": LIC_IRCC[1]}
    return {"cittadinanze": out, "totale": {a: tot_anno[a] for a in ANNI}}, fonte


# ---------------------------------------------------------------- 3. Regno Unito (Home Office)
GRUPPI = ["Work", "Study", "Family"]


def regno_unito(nuovo, errori):
    _agg, det, _sin = allegati_uk()
    dest = GREZZI / "uk-entry-clearance-outcomes.xlsx"
    meta_f = dest.with_suffix(dest.suffix + ".json")
    # rifiuti.py e questo script devono leggere lo stesso file: se GOV.UK ne ha uno nuovo, va riscaricato da rifiuti.py --nuovo
    rif = json.loads((RADICE / "dati" / "rifiuti.json").read_text(encoding="utf-8"))
    if det["url"] != rif["fonti"]["uk"]["url"]:
        errori.append("UK: GOV.UK ha un file più recente di quello di dati/rifiuti.json: lanciare prima rifiuti.py --nuovo")
        return None, None
    b, meta = scarica(det["url"], dest, nuovo)
    if impronta(b) != rif["fonti"]["uk"]["sha256"]:
        errori.append("UK: il file in _grezzi è diverso da quello usato per dati/rifiuti.json")
    wb = openpyxl.load_workbook(dest, read_only=True)
    ws = wb["Data_Vis_D02"]
    nomi = {v[1]: c for c, v in CITTADINANZE.items() if v[1]}
    per_anno = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))   # codice -> anno -> gruppo -> concessi
    per_trim = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))   # codice -> trimestre -> gruppo -> concessi
    trimestri = set()
    intest = None
    for r in ws.iter_rows(values_only=True):
        if intest is None:
            if r and r[0] == "Year" and r[1] == "Quarter":
                intest = list(r)
                if intest[2] != "Nationality" or intest[4] != "Visa type group" or intest[8] != "Case outcome" or intest[9] != "Decisions":
                    raise SystemExit(f"UK: intestazioni inattese {intest}")
            continue
        if not r[1]:
            continue
        trimestri.add(r[1])
        if r[8] != "Issued" or r[4] not in GRUPPI or r[2] not in nomi:
            continue
        c = nomi[r[2]]
        per_anno[c][str(r[0])][r[4]] += int(r[9] or 0)
        per_trim[c][r[1]][r[4]] += int(r[9] or 0)
    for a in ANNI:
        if sum(1 for q in trimestri if q.startswith(a)) != 4:
            errori.append(f"UK: l'anno {a} non ha 4 trimestri nel file")
    ultimo = max(trimestri)
    anno_ytd = ultimo[:4] if not ultimo.endswith("Q4") else None
    trim_ytd = sorted(q for q in trimestri if anno_ytd and q.startswith(anno_ytd))
    # controllo incrociato con dati/rifiuti.json (stesso file, letto da rifiuti.py): concessi per trimestre e gruppo
    confronti = 0
    for c, (_, n_uk) in CITTADINANZE.items():
        if not n_uk:
            continue
        for g in GRUPPI:
            for q in rif["uk"]["trimestri"]:
                mio = per_trim[c][q][g]
                loro = rif["uk"]["naz"].get(n_uk, {}).get(g, {}).get(q, [0])[0]
                if mio != loro:
                    errori.append(f"UK: {n_uk} {g} {q}: {mio} concessi qui, {loro} in rifiuti.json")
                confronti += 1
    out = {}
    for c, (_, n_uk) in CITTADINANZE.items():
        if not n_uk:
            continue
        anni = {a: [per_anno[c][a][g] for g in GRUPPI] for a in ANNI}
        if anno_ytd:
            anni[anno_ytd] = [sum(per_trim[c][q][g] for q in trim_ytd) for g in GRUPPI]
        out[c] = {"nome": n_uk, "anni": anni}
    cover = [str(r[0]) for r in wb["Cover_Sheet"].iter_rows(values_only=True) if r and r[0]]
    fonte = {"titolo": det["title"], "editore": "Home Office, Immigration System Statistics", "url": det["url"],
             "pagina": "https://www.gov.uk/government/statistical-data-sets/immigration-system-statistics-data-tables", "formato": "XLSX",
             "byte": len(b), "sha256": impronta(b), "scaricato_il": meta.get("scaricato_il", date.today().isoformat()),
             "pubblicato": next((x.split(":", 1)[1].strip() for x in cover if x.startswith("Published")), ""),
             "prossimo": next((x.split(":", 1)[1].strip() for x in cover if x.startswith("Next update")), ""),
             "ultimo_trimestre": ultimo, "anno_in_corso": anno_ytd, "trimestri_in_corso": trim_ytd, "gruppi": GRUPPI,
             "licenza": "Open Government Licence v3.0", "licenza_url": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
             "confronti_con_rifiuti": confronti}
    return {"cittadinanze": out}, fonte


# ---------------------------------------------------------------- principale
def main():
    nuovo = "--nuovo" in sys.argv
    errori = []
    ue, f_ue = eurostat(nuovo, errori)
    ca, f_ca = canada(nuovo, errori)
    uk, f_uk = regno_unito(nuovo, errori)
    if errori:
        print("ERRORI: il file dei dati NON è stato aggiornato")
        for x in errori[:40]:
            print(" -", x)
        sys.exit(1)
    uscita = {"_nota": "Generato da raccolta/trasferimenti.py: non modificare a mano. eurostat.dati: cittadinanza -> destinazione -> anno -> "
                       "[totale, famiglia, studio, lavoro, altro, validi 3-5 mesi, 6-11 mesi, 12 mesi o più] (primi permessi, persone; null = "
                       "non disponibile); eurostat.note: stessi indici -> segno Eurostat (u = poco affidabile, b = interruzione della serie). "
                       "canada: nuovi residenti permanenti, somma dei mesi (IRCC arrotonda ogni mese a 5). uk: visti concessi per anno della "
                       "decisione [Work, Study, Family].",
              "generato_il": date.today().isoformat(), "anni": ANNI,
              "fonti": {"eurostat": f_ue, "canada": f_ca, "uk": f_uk},
              "eurostat": ue, "canada": ca, "uk": uk}
    USCITA.write_text(json.dumps(uscita, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    us = ue["dati"]["US"]["EU27_2020"]
    print(f"Scritto {USCITA}: Eurostat aggiornato il {f_ue['aggiornato_il']}, {len(ue['dati'])} cittadinanze × {len(DESTINAZIONI)} destinazioni, "
          f"{ANNI[0]}-{ANNI[-1]} (USA nell'UE-27: 2024 {us['2024'][0]:,}, 2025 {us['2025'][0]:,}); {f_ue['totali_ue_controllati']} totali UE-27 = somma degli Stati; "
          f"IRCC fino al {f_ca['ultimo_mese']}; Home Office fino al {f_uk['ultimo_trimestre']} ({f_uk['confronti_con_rifiuti']} confronti con rifiuti.json).")


if __name__ == "__main__":
    main()
