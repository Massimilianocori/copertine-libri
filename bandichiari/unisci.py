#!/usr/bin/env python3
"""Unisce i risultati della ricerca (dati/ricerca/*.json) in dati/bandi.json.
Le schede già presenti con lo stesso slug vengono sostituite dalla versione più recente."""
import json, pathlib
from datetime import date
BASE = pathlib.Path(__file__).resolve().parent
NOMI = {"Friuli-Venezia Giulia": "Friuli Venezia Giulia", "Valle d’Aosta": "Valle d'Aosta",
        "Trentino Alto Adige": "Trentino-Alto Adige", "Emilia Romagna": "Emilia-Romagna"}
bandi = {b["slug"]: b for b in json.loads((BASE / "dati/bandi.json").read_text(encoding="utf-8"))}
for f in sorted((BASE / "dati/ricerca").glob("*.json")):
    for b in json.loads(f.read_text(encoding="utf-8")):
        b["regioni"] = [NOMI.get(r, r) for r in b["regioni"]]
        b.setdefault("ultima_verifica", date.fromtimestamp(f.stat().st_mtime).isoformat())
        bandi[b["slug"]] = b
(BASE / "dati/bandi.json").write_text(json.dumps(list(bandi.values()), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(len(bandi), "bandi in dati/bandi.json")
