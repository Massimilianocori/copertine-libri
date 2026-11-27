"""Misura del formato «citabile» di EsameB1 (scheda studio-business/schede/2026-11-27-esameb1-citabile.md).

Uso (dalla radice del repository):
    python3 esameb1/raccolta/citabile.py --dal 2026-11-30 --al 2026-12-06      # una settimana, da lunedì a domenica

Conta le visite con provenienza chatgpt.com (GoatCounter, somma dei due host esameb1.eu ed esameb1.netlify.app) in quattro gruppi:
pagine trattate che entrano nel verdetto, pagine di controllo (tenute fuori dal formato), pagine trattate nate il 25/11 (contate a
parte) e resto del sito. Le riporta a 7 giorni e le confronta con la linea di base scritta in dati/citabile.json (13-26/11/2026).
Verdetto = crescita delle trattate ÷ crescita del controllo, tutte e due sulla stessa base. Stampa anche le visite da Google pagina
per pagina e i clic sui riquadri del libro e del Pass (eventi esameb1.eu/clic/...), per vedere subito un danno.
    python3 esameb1/raccolta/citabile.py --dal 2026-11-13 --al 2026-11-26 --base     # i numeri della linea di base, in JSON
Nessuna chiave nel codice: la chiave di sola lettura è un segreto di rete dell'ambiente (401 = segreto mancante). Non scrive niente.
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
API = "https://rete-siti.goatcounter.com/api/v0/"
HOST = ("esameb1.eu", "esameb1.netlify.app")  # il vecchio indirizzo porta al nuovo dall'8/11/2026, ma GoatCounter conta ancora qualche visita lì
VECCHI = {"esempi-esame-b1/": "esempi/"}  # vecchio percorso della pagina degli esempi (301)
# Clic sui riquadri del libro e del Pass (eventi GoatCounter). libro-esempi: indice e pagine degli enti di /esempi/; libro-livelli: A1, C1, C2,
# CILS B1 standard; pass-prezzo: pagine /esempi/ e prova gratis insieme (l'evento non dice la pagina).
CLIC = ("libro-esempi", "libro-livelli", "libro-ascolto", "libro-orale", "libro-celi2", "pass-prezzo")


def chiedi(percorso, tentativi=5):
    for i in range(tentativi):
        try:
            r = urllib.request.Request(API + percorso, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(r, timeout=60) as f:
                time.sleep(0.3)  # limite: 4 richieste al secondo
                return json.load(f)
        except urllib.error.HTTPError as e:
            if e.code in (429, 502) and i < tentativi - 1:
                time.sleep(2 + 2 * i)
                continue
            raise SystemExit(f"GoatCounter: HTTP {e.code} su {percorso} (401 = segreto di rete mancante)")
        except (urllib.error.URLError, TimeoutError):
            if i == tentativi - 1:
                raise
            time.sleep(2)


def visite(dal, al):
    """({percorso ("esempi/cils/"): [visite, da chatgpt.com, da Google]}, {evento di clic: numero}) nel periodo (date incluse, UTC),
    sommando i due host."""
    periodo = f"start={dal}T00:00:00Z&end={al}T23:00:00Z&limit=100"
    righe, escl = [], []
    while True:
        d = chiedi(f"stats/hits?{periodo}" + (("&exclude_paths=" + ",".join(map(str, escl))) if escl else ""))
        righe += d["hits"]
        escl += [h["path_id"] for h in d["hits"]]
        if not d.get("more") or not d["hits"]:
            break
    out, clic = {}, {}
    for h in righe:
        percorso = h["path"].lstrip("/")
        host = next((x for x in HOST if percorso == x or percorso.startswith(x + "/")), None)
        if not host:
            continue
        resto = percorso[len(host) + 1:]
        if h.get("event") or resto.startswith("clic/"):
            if resto.startswith("clic/"):
                clic[resto[5:]] = clic.get(resto[5:], 0) + h["count"]
            continue
        refs = {x["name"]: x["count"] for x in chiedi(f"stats/hits/{h['path_id']}?{periodo}")["refs"]}
        u = resto + "/" if resto and not resto.endswith(".html") else resto
        u = VECCHI.get(u, u)
        x = out.setdefault(u, [0, 0, 0])
        x[0] += h["count"]
        x[1] += refs.get("chatgpt.com", 0)
        x[2] += refs.get("Google", 0)
    return out, clic


def gruppi(C, v):
    """Visite da chatgpt.com per gruppo: trattate nel verdetto, controllo (tenute fuori), trattate nuove (nate il 25/11), resto del sito."""
    g = lambda lista: sum(v.get(u, [0, 0, 0])[1] for u in lista)  # noqa: E731
    verdetto = [u for u, x in C["pagine"].items() if x.get("nel_verdetto", True)]
    nuove = [u for u in C["pagine"] if u not in verdetto]
    note = set(C["pagine"]) | set(C["controllo"])
    return {"trattate": g(verdetto), "controllo": g(C["controllo"]), "nuove": g(nuove), "resto": sum(x[1] for u, x in v.items() if u not in note)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dal", required=True)
    p.add_argument("--al", required=True)
    p.add_argument("--base", action="store_true", help="stampa in JSON i numeri per la linea di base di dati/citabile.json (non scrive)")
    a = p.parse_args()
    C = json.loads((RADICE / "dati" / "citabile.json").read_text(encoding="utf-8"))
    giorni = (date.fromisoformat(a.al) - date.fromisoformat(a.dal)).days + 1
    v, clic = visite(a.dal, a.al)
    g = gruppi(C, v)
    if a.base:
        print(json.dumps({"dal": a.dal, "al": a.al, "sito_visite": sum(x[0] for x in v.values()), "sito_chatgpt": sum(x[1] for x in v.values()),
                          "sito_google": sum(x[2] for x in v.values()), **{k + "_chatgpt": n for k, n in g.items()},
                          "clic": {k: clic.get(k, 0) for k in CLIC},
                          "pagine": {u: v.get(u, [0, 0, 0]) for u in list(C["pagine"]) + list(C["controllo"])}}, ensure_ascii=False))
        return 0
    b = C["base"]
    g_base = (date.fromisoformat(b["al"]) - date.fromisoformat(b["dal"])).days + 1
    sett = lambda n, gg: n * 7 / gg  # noqa: E731
    print(f"Periodo {a.dal} – {a.al} ({giorni} giorni), host {' + '.join(HOST)}. Visite da chatgpt.com, riportate a 7 giorni (tra parentesi la base {b['dal']} – {b['al']}):")
    nomi = {"trattate": "trattate nel verdetto", "controllo": "controllo (senza formato)", "nuove": "trattate nate il 25/11 (fuori dal verdetto)", "resto": "resto del sito"}
    for k in ("trattate", "controllo", "nuove", "resto"):
        print(f"  {nomi[k]:44} {g[k]:4} = {sett(g[k], giorni):6.1f} la settimana  ({sett(b[k + '_chatgpt'], g_base):.1f})")
    c_t = sett(g["trattate"], giorni) / sett(b["trattate_chatgpt"], g_base)
    print(f"  crescita delle trattate sulla base: × {c_t:.2f}")
    if g["controllo"]:
        c_c = sett(g["controllo"], giorni) / sett(b["controllo_chatgpt"], g_base)
        print(f"  crescita del controllo sulla base:  × {c_c:.2f}")
        print(f"  VERDETTO: crescita trattate ÷ crescita controllo = {c_t / c_c:.2f} (soglia del sì 1,5; stop sotto 0,7 per 2 settimane)")
        print(f"  visite in più la settimana attribuibili al formato (trattate − base × crescita del controllo): {sett(g['trattate'], giorni) - sett(b['trattate_chatgpt'], g_base) * c_c:+.1f}")
    else:
        print("  VERDETTO: non calcolabile (controllo = 0 visite)")
    print("Pagina per pagina: visite, da chatgpt.com, da Google (tra parentesi chatgpt.com nei giorni di base)")
    for nome, lista in (("trattate", C["pagine"]), ("controllo", C["controllo"])):
        for u, voce in lista.items():
            x = v.get(u, [0, 0, 0])
            print(f"  {nome:10} {u:28} {x[0]:4} {x[1]:4} {x[2]:4}   ({voce['chatgpt_base']}){'' if voce.get('nel_verdetto', True) else '  fuori dal verdetto'}")
    print("Clic sui riquadri del libro e del Pass (tra parentesi nei giorni di base; pass-prezzo comprende la prova gratis):")
    for k in CLIC:
        print(f"  clic/{k:16} {clic.get(k, 0):4}   ({b.get('clic', {}).get(k, 0)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
