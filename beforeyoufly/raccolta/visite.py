#!/usr/bin/env python3
"""Visite per pagina di Before You Fly da GoatCounter (API pubblica dell'account della rete), per la regola dello sfoltimento del 2/12/2026
(studio-business/BYF-PIANO-RILANCIO-2026-11-27.md, sezione 3.3) e per il blocco «Related» delle pagine di arrivo (azione P4).

    python3 -I beforeyoufly/raccolta/visite.py                # dal 17/10/2026 a ieri
    python3 -I beforeyoufly/raccolta/visite.py 2026-12-01     # dal 17/10/2026 al giorno dato (compreso)

Scrive dati/visite.json: percorso della pagina (come in genera.py: "cabin-bags/united/", "" = home) -> visite da qualunque sorgente,
somma del dominio nuovo e del vecchio indirizzo netlify.app. Il contatore parte il 17/10/2026. Gli eventi (/clic/) non contano.
Si legge un giorno alla volta: con una finestra lunga e più di 100 pagine la risposta dell'API è incompleta.
Non tocca dati/piu_usate.json (blocchi «Most used» già pubblicati). Se l'API non risponde esce con 1 e non scrive nulla."""
import datetime as dt
import json
import sys
import time
import urllib.request
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
GC = "https://rete-siti.goatcounter.com/api/v0/"
HOST = ("before-you-fly.com", "before-you-fly.netlify.app")
INIZIO = dt.date(2026, 10, 17)


def chiedi(u):
    for _ in range(5):
        try:
            return json.load(urllib.request.urlopen(GC + u, timeout=60))
        except Exception:
            time.sleep(5)
    return None


def giorno(g):
    """[(percorso GoatCounter, visite)] di un giorno, tutte le pagine (a blocchi di 100)."""
    righe = []
    while True:
        ex = ",".join(str(h["path_id"]) for h in righe)
        d = chiedi(f"stats/hits?start={g}T00:00:00Z&end={g}T23:59:59Z&limit=100" + (f"&exclude_paths={ex}" if ex else ""))
        if d is None:
            return None
        righe += d["hits"]
        time.sleep(0.2)
        if not d.get("more") or not d["hits"]:
            return [(h["path"], h["count"]) for h in righe if not h.get("event")]


def percorso(p):
    """"/before-you-fly.com/cabin-bags/united" -> "cabin-bags/united/"; None se non è una pagina di questo sito."""
    parti = p.lstrip("/").split("/", 1)
    if parti[0] not in HOST or "/clic/" in p:
        return None
    r = (parti[1] if len(parti) > 1 else "").split("?")[0].strip("/")
    if r.endswith("index.html"):
        r = r[:-len("index.html")].strip("/")
    return r if r.endswith(".html") or not r else r + "/"


def main():
    fine = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date.today() - dt.timedelta(days=1)
    visite, per_host, g = {}, {h: 0 for h in HOST}, INIZIO
    while g <= fine:
        righe = giorno(g.isoformat())
        if righe is None:
            sys.exit(f"GoatCounter non risponde per il {g}: nessun file scritto")
        for p, n in righe:
            u = percorso(p)
            if u is None:
                continue
            visite[u] = visite.get(u, 0) + n
            per_host[p.lstrip("/").split("/", 1)[0]] += n
        g += dt.timedelta(days=1)
    sito = RADICE / "sito"
    esiste = lambda u: (sito / (u if u.endswith(".html") else u + "index.html")).is_file()  # noqa: E731
    altre = {u: n for u, n in visite.items() if not esiste(u)}
    pagine = {u: n for u, n in visite.items() if esiste(u)}
    (RADICE / "dati" / "visite.json").write_text(json.dumps({
        "_nota": "Scritto da raccolta/visite.py: visite per pagina da GoatCounter (qualunque sorgente, dominio nuovo + vecchio indirizzo), "
                 "pagine fuori indice comprese. genera.py lo usa per la regola dello sfoltimento del 2/12 (spenta finché SFOLTIMENTO è "
                 "False) e per il blocco «Related» delle pagine di arrivo. Rimisurare l'1/12 prima di accendere la regola.",
        "periodo": f"{INIZIO} / {fine}", "letto_il": dt.date.today().isoformat(),
        "visite_totali": sum(pagine.values()), "pagine_con_visite": len(pagine), "per_host": per_host,
        "percorsi_non_del_sito": dict(sorted(altre.items())),
        "visite": dict(sorted(pagine.items(), key=lambda x: (-x[1], x[0])))}, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"Visite {INIZIO} / {fine}: {sum(pagine.values())} su {len(pagine)} pagine del sito ({per_host}); "
          f"{len(altre)} percorsi senza pagina ({sum(altre.values())} visite)")


if __name__ == "__main__":
    main()
