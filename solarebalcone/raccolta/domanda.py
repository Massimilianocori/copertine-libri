"""Domanda vera dalle ricerche Google (autocompletamento), per decidere quali città hanno una pagina e da dove vengono le
domande frequenti. Scrive dati/domanda.json.

Uso (dalla radice del repository):
    python3 solarebalcone/raccolta/domanda.py      # circa 4 minuti (una richiesta ogni 0,25 s)

Per ogni lingua: le ricerche di base ("fotovoltaico balcone", "placas solares balcón", "panneau solaire balcon"...) e,
per ogni città del calcolatore (dati/citta.json), "<ricerca> <città>". Una città ha domanda vera se almeno un
suggerimento contiene sia la ricerca sia il nome della città (es. "fotovoltaico da balcone roma"). Nessun dato personale:
si salvano solo i suggerimenti pubblici. Servizio: suggestqueries.google.com, client=firefox, hl e gl del Paese.
"""
import json
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
RICERCHE_CITTA = {
    "it": ["fotovoltaico balcone", "fotovoltaico da balcone", "pannelli solari balcone", "pannello solare balcone"],
    "es": ["placas solares balcón", "kit solar balcón", "paneles solares balcon"],
    "fr": ["panneau solaire balcon", "panneaux solaires balcon", "kit solaire plug and play", "kit solaire balcon"],
}
RICERCHE_BASE = {
    "it": ["fotovoltaico balcone", "pannello solare balcone", "fotovoltaico da balcone", "pannelli solari balcone",
           "fotovoltaico plug and play", "comunicazione unica fotovoltaico"],
    "es": ["placas solares balcón", "kit solar balcón", "placas solares balcon", "placas solares enchufables",
           "autoconsumo sin excedentes"],
    "fr": ["panneau solaire balcon", "kit solaire plug and play", "panneaux solaires balcon", "kit solaire balcon",
           "panneau solaire plug and play"],
}


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn").replace("-", " ")


def suggerimenti(q, lingua):
    u = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode(
        {"client": "firefox", "hl": lingua, "gl": lingua, "q": q})
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    for n in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode("utf-8", "replace"))[1]
        except Exception:
            time.sleep(2 + 2 * n)
    return None


def main():
    citta = json.loads((RADICE / "dati" / "citta.json").read_text(encoding="utf-8"))
    out = {"_nota": ("Autocompletamento Google (suggestqueries.google.com, client=firefox, hl=gl=lingua), letto il giorno "
                     "indicato. 'base': ricerca -> suggerimenti. 'citta': slug -> {ricerca con città -> suggerimenti}; "
                     "'domanda' = suggerimenti che contengono ricerca e città (null = servizio non raggiungibile)."),
           "letto_il": date.today().isoformat(), "lingue": {}}
    for lingua in RICERCHE_CITTA:
        base = {q: suggerimenti(q, lingua) for q in RICERCHE_BASE[lingua]}
        per_citta = {}
        for c in citta[lingua]:
            voce = {"ricerche": {}, "domanda": []}
            for r in RICERCHE_CITTA[lingua]:
                q = f"{r} {c['q']}"
                s = suggerimenti(q, lingua)
                voce["ricerche"][q] = s
                for x in s or []:
                    nx = norm(x)
                    if norm(c["q"]) in nx and all(p in nx for p in norm(r).split()):
                        voce["domanda"].append(x)
                time.sleep(0.25)
            voce["domanda"] = sorted(set(voce["domanda"]))
            per_citta[c["slug"]] = voce
            if voce["domanda"]:
                print(f"{lingua} {c['slug']}: {voce['domanda']}")
        out["lingue"][lingua] = {"base": base, "citta": per_citta}
    dest = RADICE / "dati" / "domanda.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Scritto {dest}.")


if __name__ == "__main__":
    main()
