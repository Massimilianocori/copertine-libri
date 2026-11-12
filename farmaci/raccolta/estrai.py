"""Legge i file ufficiali AIFA scaricati da fonti.py e scrive i dati del sito in farmaci/dati/.

Uso (dalla radice del repository):
    python3 -I farmaci/raccolta/estrai.py

Scrive:
    dati/trasparenza.json   lista di trasparenza: una riga per confezione (AIC), prezzi come stringhe con 2 decimali
    dati/carenti.json       elenco completo dei farmaci carenti, con l'elenco AIFA in cui compare (equivalenti / alternativo)
    dati/classe_a.json      prezzo al pubblico in fascia A al 30/6 per AIC (solo per il confronto in verifica.py)

Nessun calcolo qui oltre alla lettura: le differenze sono quelle stampate da AIFA, e verifica.py le ricontrolla.
I file grezzi sono dati scaricati: si leggono come testo, nessun codice viene eseguito.
"""
import csv
import io
import json
import re
import sys
import zipfile
from decimal import Decimal
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
GREZZI = RADICE / "raccolta" / "_grezzi"
DATI = RADICE / "dati"


def sp(s):
    return re.sub(r"\s+", " ", (s or "").replace(" ", " ")).strip()


def prezzo(s):
    s = sp(s).replace("€", "").strip()
    if not s:
        return None
    return str(Decimal(s.replace(".", "").replace(",", ".")).quantize(Decimal("0.01")))


def aic9(s):
    s = re.sub(r"\D", "", s or "")
    return s.zfill(9) if s else ""


def data_iso(s):
    s = sp(s)
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}" if m else (s or None)


def leggi_csv(nome):
    t = (GREZZI / nome).read_bytes().decode("cp1252")
    return list(csv.reader(io.StringIO(t, newline=""), delimiter=";"))


def leggi_ods(nome):
    """Righe di un foglio ODS (primo foglio), con le celle ripetute espanse e le righe vuote tolte."""
    x = zipfile.ZipFile(GREZZI / nome).read("content.xml").decode("utf-8")
    foglio = re.search(r"<table:table [^>]*>(.*?)</table:table>", x, re.S).group(1)
    righe = []
    for r in re.findall(r"<table:table-row[^>]*>(.*?)</table:table-row>", foglio, re.S):
        celle = []
        for m in re.finditer(r"<table:table-cell([^>]*?)(?:/>|>(.*?)</table:table-cell>)", r, re.S):
            attr, cont = m.group(1), m.group(2) or ""
            rep = re.search(r'number-columns-repeated="(\d+)"', attr)
            n = min(int(rep.group(1)), 50) if rep else 1
            paragrafi = re.findall(r"<text:p[^>]*>(.*?)</text:p>", cont, re.S)
            testo = " ".join(re.sub(r"<[^>]+>", "", p) for p in paragrafi)
            testo = testo.replace("&apos;", "'").replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
            celle += [sp(testo)] * n
        while celle and not celle[-1]:
            celle.pop()
        if celle:
            righe.append(celle)
    return righe


def data_in_testo(righe, rx):
    for r in righe[:5]:
        m = re.search(rx, " ".join(r))
        if m:
            return data_iso(m.group(1))
    return None


CAMPI_CARENTI = ["Nome medicinale", "Codice AIC", "Principio attivo", "Forma farmaceutica e dosaggio", "Titolare AIC", "Data inizio",
                 "Fine presunta", "Equivalente", "Motivazioni", "Suggerimenti/Indicazioni AIFA", "Nota AIFA", "Classe di rimborsabilità", "Codice ATC"]


def righe_carenti(righe, fonte):
    i = next(k for k, r in enumerate(righe) if r and r[0] == "Nome medicinale")
    if righe[i][:13] != CAMPI_CARENTI:
        raise SystemExit(f"{fonte}: intestazione cambiata {righe[i]}")
    out = []
    for r in righe[i + 1:]:
        r = (r + [""] * 13)[:13]
        if not sp(r[1]):
            continue
        out.append({"aic": aic9(r[1]), "nome": sp(r[0]), "pa": sp(r[2]), "confezione": sp(r[3]), "titolare": sp(r[4]),
                    "inizio": data_iso(r[5]), "fine_presunta": data_iso(r[6]), "equivalente": sp(r[7]), "motivo": sp(r[8]),
                    "suggerimenti": sp(r[9]), "nota": sp(r[10]), "classe": sp(r[11]), "atc": sp(r[12])})
    return out


def main():
    fonti = json.loads((DATI / "fonti.json").read_text(encoding="utf-8"))["file"]
    # ---------------- lista di trasparenza
    r = leggi_csv("trasparenza.csv")
    intest = r[0]
    m = re.fullmatch(r"Prezzo Pubblico (\d+ \w+ \d{4})", intest[8])
    if intest[:8] != ["Principio attivo", "Confezione di riferimento", "ATC", "AIC", "Farmaco", "Confezione", "Ditta", "Prezzo riferimento SSN"] or not m:
        raise SystemExit(f"trasparenza.csv: intestazione cambiata {intest}")
    righe = []
    for x in r[1:]:
        if len(x) < 12 or not sp(x[3]):
            continue
        righe.append({"aic": aic9(x[3]), "pa": sp(x[0]), "conf_rif": sp(x[1]), "atc": sp(x[2]), "farmaco": sp(x[4]), "confezione": sp(x[5]),
                      "ditta": sp(x[6]), "rif": prezzo(x[7]), "prezzo": prezzo(x[8]), "diff": prezzo(x[9]), "nota": sp(x[10]), "gruppo": sp(x[11])})
    tr = {"fonte": "trasparenza", "pubblicato_il": fonti["trasparenza"]["pubblicato_il"], "colonna_prezzo": intest[8], "righe": righe}
    (DATI / "trasparenza.json").write_text(json.dumps(tr, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    # ---------------- farmaci carenti (CSV completo) + i due elenchi ODS
    rc = leggi_csv("carenti.csv")
    data_csv = data_in_testo(rc, r"aggiornato al (\d{2}/\d{2}/\d{4})")
    car = righe_carenti(rc, "carenti.csv")
    elenchi = {}
    date_ods = {}
    for k, nome, rx in (("equivalenti", "carenti_equivalenti.ods", r"disponibili equivalenti aggiornato al (\d{2}/\d{2}/\d{4})"),
                        ("alternativo", "carenti_alternativo.ods", r"trattamento alternativo aggiornato al (\d{2}/\d{2}/\d{4})")):
        ro = leggi_ods(nome)
        date_ods[k] = data_in_testo(ro, rx)
        for c in righe_carenti(ro, nome):
            elenchi.setdefault(c["aic"], []).append(k)
    for c in car:
        c["elenchi"] = sorted(set(elenchi.get(c["aic"], [])))
    fuori = sorted(set(elenchi) - {c["aic"] for c in car})
    ca = {"fonte": "carenti", "pubblicato_il": fonti["carenti"]["pubblicato_il"], "aggiornato_al_nel_file": data_csv,
          "elenchi_aggiornati_al": date_ods, "aic_negli_elenchi_ma_non_nel_completo": fuori, "righe": car}
    (DATI / "carenti.json").write_text(json.dumps(ca, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    # ---------------- fascia A al 30/6 (confronto)
    ra = leggi_csv("classe_a.csv")
    if [sp(v).replace(" €", "") for v in ra[0][:7]] != ["Principio attivo", "Descrizione gruppo", "Denominazione e Confezione", "Prezzo al pubblico", "Titolare AIC", "AIC", "Codice Gruppo Equivalenza"]:
        raise SystemExit(f"classe_a.csv: intestazione cambiata {ra[0]}")
    cla = {aic9(x[5]): {"prezzo": prezzo(x[3]), "gruppo": sp(x[6]), "denominazione": sp(x[2])} for x in ra[1:] if len(x) > 6 and sp(x[5])}
    (DATI / "classe_a.json").write_text(json.dumps({"fonte": "classe_a", "pubblicato_il": fonti["classe_a"]["pubblicato_il"], "aic": cla},
                                                   ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"trasparenza: {len(righe)} confezioni, {len({x['gruppo'] for x in righe})} gruppi, {len({x['pa'] for x in righe})} principi attivi")
    print(f"carenti: {len(car)} confezioni (file: aggiornato al {data_csv}); elenchi ODS {date_ods}; "
          f"negli elenchi ODS ma non nel completo: {len(fuori)}")
    print(f"fascia A: {len(cla)} confezioni")
    if data_csv != fonti["carenti"]["pubblicato_il"]:
        print(f"ATTENZIONE: data nel file carenti {data_csv} diversa dalla pagina {fonti['carenti']['pubblicato_il']}", file=sys.stderr)


if __name__ == "__main__":
    main()
