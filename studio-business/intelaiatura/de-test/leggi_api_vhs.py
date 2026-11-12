"""Legge le date d'esame dal catalogo nazionale delle VHS (vhs-Kursfinder del Deutscher Volkshochschul-Verband).

Fonte: https://api.volkshochschule.de/3/veranstaltungen (JSON pubblico usato dalla pagina
www.volkshochschule.de/kursfinder; robots.txt senza divieti; nessuna chiave). Condizioni di riuso NON lette:
prima di pubblicare qualcosa con questi dati va chiesto al DVV.
Cerca "Einbürgerungstest", "Leben in Deutschland", "Deutsch-Test für Zuwanderer", "DTZ", "telc Deutsch B1",
tiene gli eventi futuri il cui titolo è un esame (non un corso di preparazione) e scrive
grezzi/api_vhs_<data>.json con: tipo (EBT o B1), VHS, luogo, data, prezzo, stato dei posti, pagina.
Nessun testo descrittivo viene salvato.  Uso: python3 -I leggi_api_vhs.py 2026-11-12
"""
import collections
import json
import pathlib
import re
import sys
import time

import requests

QUI = pathlib.Path(__file__).resolve().parent
OGGI = sys.argv[1]
B = "https://api.volkshochschule.de/3/veranstaltungen"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"}
RE_EBT = re.compile(r"einbürgerungstest|leben in deutschland", re.I)
RE_B1 = re.compile(r"\bdtz\b|deutsch-?test für zuwanderer|telc deutsch b1|telc b1|zertifikat deutsch|b1.*prüfung|prüfung.*b1", re.I)
RE_CORSO = re.compile(r"vorbereitung|vorkurs|training|kurs\b|orientierungskurs|übung|lernen|workshop|fit für", re.I)


def prendi(url, params=None):
    r = requests.get(url, params=params, headers=UA, timeout=30)
    time.sleep(0.5)
    return r.json()


eventi, conteggi = {}, {}
for parola in ["Einbürgerungstest", "Leben in Deutschland", "Deutsch-Test für Zuwanderer", "DTZ", "telc Deutsch B1"]:
    j = prendi(B, {"filter[text]": parola, "sort": "relevanz", "filter[vonDatum]": OGGI})
    conteggi[parola] = j.get("meta", {}).get("count")
    pagine = 1
    while True:
        for e in j["data"]:
            eventi[e["id"]] = e
        nxt = j.get("links", {}).get("next")
        if not nxt or pagine >= 40:
            break
        j = prendi(nxt)
        pagine += 1

righe = []
for e in eventi.values():
    a = e["attributes"]
    nome = re.sub(r"<[^>]+>", "", a.get("name") or "")
    tipo = "EBT" if RE_EBT.search(nome) else ("B1" if RE_B1.search(nome) else None)
    if not tipo or RE_CORSO.search(nome) or (a.get("beginnDatum") or "") < OGGI:
        continue
    righe.append({
        "tipo": tipo,
        "vhs": re.sub(r"\s*\|.*", "", (a.get("seo") or {}).get("description") or ""),
        "luogo": ((a.get("veranstaltungsort") or {}).get("adresse") or {}).get("ort") or "",
        "data": a["beginnDatum"],
        "prezzo": (a.get("preis") or {}).get("betrag"),
        "posti": (a.get("belegungsstatus") or {}).get("text"),
        "pagina": next((w["uri"] for w in a.get("webadressen") or []), ""),
    })
righe.sort(key=lambda r: (r["tipo"], r["luogo"], r["data"]))
(QUI / "grezzi" / f"api_vhs_{OGGI}.json").write_text(json.dumps(
    {"data_lettura": OGGI, "risultati_per_parola": conteggi, "eventi": righe}, ensure_ascii=False, indent=0))
for t in ("EBT", "B1"):
    r = [x for x in righe if x["tipo"] == t]
    print(t, "eventi futuri", len(r), "| VHS", len({x["vhs"] for x in r}), "| luoghi", len({x["luogo"] for x in r}),
          "| con prezzo > 0", sum(1 for x in r if x["prezzo"] and float(x["prezzo"]) > 0),
          "| con stato dei posti", sum(1 for x in r if x["posti"]), "| nel 2027", sum(x["data"] >= "2027" for x in r))
    print("  prezzi:", collections.Counter(x["prezzo"] for x in r).most_common(5))
