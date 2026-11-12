"""Ricerche vere (autocompletamento Google, hl=it gl=it) e volumi misurati: decidono le pagine «codice ATECO per mestiere»
e da dove nascono le FAQ.

Uso (dalla radice del repository):
    python3 -I ateco/raccolta/domanda.py          # legge solo le radici che mancano
    python3 -I ateco/raccolta/domanda.py --tutto  # rilegge tutto (ogni 3 mesi)

Una richiesta per radice, si salvano i suggerimenti in dati/domanda.json (chiave "radici").
I volumi mensili (Google Ads, tramite api.seodata.dev) NON si leggono qui: si scrivono a mano in dati/volumi.json con la
data della misura, perché la quota di ricerche è piccola e condivisa (la chiave sta fuori dal repository).
Nessun dato personale: si mandano solo parole di ricerca. Pausa di 0,5 secondi; alla prima risposta diversa da 200 lo
script si ferma e salva (niente tentativi di aggirare i limiti).
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
FILE = RADICE / "dati" / "domanda.json"
URL = "https://suggestqueries.google.com/complete/search?client=firefox&hl=it&gl=it&q="

GENERALI = [
    "codice ateco", "codice ateco ", "codici ateco", "codici ateco 2025", "codici ateco 2025 ", "ateco 2025", "nuovi codici ateco",
    "nuovi codici ateco 2025", "codici ateco 2025 elenco", "codice ateco cos'è", "codice ateco cosa", "codice ateco come",
    "codice ateco come trovarlo", "codice ateco partita iva", "codice ateco forfettario", "codice ateco per", "codice ateco per ",
    "codice ateco 2022", "codice ateco vecchio", "codice ateco vecchio e nuovo", "codici ateco 2022 2025", "tabella ateco 2022 2025",
    "conversione codici ateco", "corrispondenza codici ateco", "codice ateco cambiato", "cambio codice ateco", "variazione codice ateco",
    "coefficiente di redditività", "coefficiente di redditività ", "coefficiente di redditività forfettario", "coefficiente redditività ateco",
    "codice ateco secondario", "codice ateco prevalente", "codice ateco visura", "codice ateco agenzia entrate", "codici istat ateco",
    "ateco istat", "codice ateco significato", "quale codice ateco", "codice ateco attività", "codice ateco n.c.a.",
]
LETTERE = [f"codice ateco {c}" for c in "abcdefghilmnopqrstuvz"]
CIFRE = [f"codice ateco {c}" for c in "123456789"]
MESTIERI = [
    "parrucchiere", "barbiere", "estetista", "centro estetico", "onicotecnica", "idraulico", "elettricista", "fotografo", "videomaker",
    "b&b", "bed and breakfast", "affittacamere", "affitti brevi", "casa vacanze", "e-commerce", "ecommerce", "vendita online",
    "dropshipping", "amazon", "consulente", "consulenza", "consulente informatico", "consulente aziendale", "ristorante", "ristorazione",
    "pizzeria", "bar", "pasticceria", "gelateria", "food truck", "muratore", "edile", "imbianchino", "giardiniere", "manutenzione del verde",
    "autista ncc", "ncc", "taxi", "influencer", "content creator", "social media manager", "programmatore", "sviluppatore software",
    "web designer", "grafico", "copywriter", "traduttore", "formatore", "insegnante", "ripetizioni", "personal trainer", "istruttore",
    "psicologo", "fisioterapista", "osteopata", "infermiere", "nutrizionista", "architetto", "ingegnere", "geometra", "avvocato",
    "commercialista", "agente di commercio", "agente immobiliare", "amministratore di condominio", "tatuatore", "pulizie",
    "impresa di pulizie", "falegname", "meccanico", "agriturismo", "ambulante", "artigiano", "sarta", "colf", "babysitter",
    "dog sitter", "toelettatura", "wedding planner", "organizzazione eventi", "guida turistica", "musicista", "dj", "artista",
    "noleggio", "trasporto merci", "corriere", "logistica", "tabaccheria", "edicola", "fiorista", "farmacia", "ottico", "dentista",
]


def leggi(q):
    req = urllib.request.Request(URL + urllib.parse.quote(q), headers={"User-Agent": "Mozilla/5.0 (research script)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        if r.status != 200:
            raise RuntimeError(f"HTTP {r.status}")
        dati = json.loads(r.read().decode("utf-8", errors="replace"))
    return dati[1] if isinstance(dati, list) and len(dati) > 1 else []


def main():
    tutto = "--tutto" in sys.argv
    d = json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() and not tutto else {}
    d.setdefault("_nota", "Suggerimenti dell'autocompletamento di Google (hl=it, gl=it) per ogni radice. Scritto da raccolta/domanda.py.")
    d.setdefault("radici", {})
    radici = GENERALI + LETTERE + CIFRE + [f"codice ateco {m}" for m in MESTIERI]
    nuove = 0
    for q in radici:
        if q in d["radici"]:
            continue
        try:
            d["radici"][q] = leggi(q)
        except Exception as e:  # noqa: BLE001
            print(f"fermo su «{q}»: {e}", file=sys.stderr)
            break
        nuove += 1
        time.sleep(0.5)
    d["letto_il"] = date.today().isoformat()
    FILE.write_text(json.dumps(d, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    tot = sum(len(v) for v in d["radici"].values())
    print(f"{nuove} radici lette ora, {len(d['radici'])} in tutto, {tot} suggerimenti")


if __name__ == "__main__":
    main()
