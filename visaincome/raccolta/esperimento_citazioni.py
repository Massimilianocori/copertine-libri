"""Esperimento A/B "pagine più facili da citare" sulle pagine Paese dei visti rifiutati (31/10/2026).

Piano completo, coppie, metrica, soglia e date: studio-business/intelaiatura/esperimento-citazioni-2026-10-31.md
Gruppi salvati in: visaincome/dati/esperimento_citazioni.json (lo legge genera.py: solo le pagine "trattate" ricevono
data visibile, dateModified, riquadro "Key figures", schema Dataset e data.csv).

Uso (dalla radice del repository):
    python3 visaincome/raccolta/esperimento_citazioni.py assegna            # UNA volta (fatto il 31/10/2026): coppie e gruppi
    python3 visaincome/raccolta/esperimento_citazioni.py misura --dal 2026-11-01 --al 2026-11-30
    python3 visaincome/raccolta/esperimento_citazioni.py impronte           # solo dopo un cambio voluto dei dati (vedi il piano)

Visite: API di GoatCounter (account rete-siti). La chiave in sola lettura è un segreto di rete dell'ambiente
(host rete-siti.goatcounter.com, percorsi /api/): il sistema la aggiunge da solo alle richieste, quindi qui non c'è
nessun token e non si manda l'intestazione Authorization (vedi .claude/skills/rete-siti/SKILL.md, sez. GoatCounter).
Le visite arrivate da un assistente si riconoscono dalla provenienza `ORIGINE` (il servizio aggiunge utm_source ai link
e GoatCounter la mostra come provenienza).
"""
import argparse
import hashlib
import json
import random
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RADICE))
FILE = RADICE / "dati" / "esperimento_citazioni.json"
API = "https://rete-siti.goatcounter.com/api/v0/"
HOST = "visa-income-checker.netlify.app"
ORIGINE = "chatgpt.com"   # provenienza misurata (nome come lo scrive GoatCounter)
SEME = 20261031           # seme fisso dell'assegnazione
INIZIO_CONTATORE = "2026-10-17"   # primo giorno con il contatore in linea
# Pagine Paese escluse: cambiate il 31/10/2026 (titolo, H1 e primo paragrafo) per la sezione "Schengen visa from the UK / from Dubai":
# le loro visite dopo il 31/10 non sono confrontabili con le altre, e quel contenuto revisionato non va toccato.
ESCLUSE = {"united-kingdom": "pagina cambiata il 31/10/2026 per la sezione Schengen visa from the UK (titolo e primo paragrafo)",
           "united-arab-emirates": "pagina cambiata il 31/10/2026 per la sezione Schengen visa from Dubai (titolo e primo paragrafo)"}


def chiedi(percorso, tentativi=4):
    for i in range(tentativi):
        try:
            r = urllib.request.Request(API + percorso, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(r, timeout=60) as f:
                return json.load(f)
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tentativi - 1:
                time.sleep(2 + 2 * i)
                continue
            raise SystemExit(f"GoatCounter: HTTP {e.code} su {percorso} (401 = segreto di rete mancante)")
        except (urllib.error.URLError, TimeoutError):
            if i == tentativi - 1:
                raise
            time.sleep(2)
    return None


def visite(dal, al):
    """{slug: [visite totali, visite con provenienza ORIGINE]} per le pagine Paese dei rifiuti, nel periodo (date incluse, UTC)."""
    inizio, fine = f"{dal}T00:00:00Z", f"{al}T23:00:00Z"
    righe, escl = [], []
    while True:
        q = f"stats/hits?start={inizio}&end={fine}&limit=100" + (("&exclude_paths=" + ",".join(map(str, escl))) if escl else "")
        d = chiedi(q)
        righe += d["hits"]
        escl += [h["path_id"] for h in d["hits"]]
        if not d.get("more"):
            break
        time.sleep(0.3)
    pref = f"/{HOST}/visa-refusal-rates/"
    out = {}
    for h in righe:
        resto = h["path"][len(pref):].strip("/") if h["path"].startswith(pref) else None
        if not resto or "/" in resto:
            continue   # solo /visa-refusal-rates/<slug> (le sottopagine "easiest" e gli Stati Schengen non entrano)
        time.sleep(0.3)
        refs = chiedi(f"stats/hits/{h['path_id']}?start={inizio}&end={fine}&limit=100")["refs"]
        da_origine = sum(r["count"] for r in refs if r["name"].lower().removeprefix("www.") == ORIGINE)
        v = out.setdefault(resto, [0, 0])
        v[0] += h["count"]
        v[1] += da_origine
    return out


def pagine_esperimento():
    """Pagine Paese della sezione (le stesse di genera.PAESI_RIF), meno le escluse: [(slug, nome, domande nell'ultimo anno)]."""
    import genera as G
    return [(G.SLUG_RIF[p], G.nome_paese(p), G.PER_PAESE[G.A1][p][0]) for p in G.PAESI_RIF if G.SLUG_RIF[p] not in ESCLUSE], G


def coppie_e_gruppi(pagine, linea_base, seme=SEME):
    """Ordina per visite dall'assistente, poi visite totali, poi domande (dimensione del Paese), poi slug; accoppia le vicine;
    in ogni coppia un generatore con seme fisso sceglie la pagina trattata. Stesso ingresso -> stesso risultato."""
    ordine = sorted(pagine, key=lambda x: (-linea_base.get(x[0], [0, 0])[1], -linea_base.get(x[0], [0, 0])[0], -x[2], x[0]))
    if len(ordine) % 2:
        raise SystemExit("numero dispari di pagine: decidere quale escludere")
    rng = random.Random(seme)
    coppie = []
    for i in range(0, len(ordine), 2):
        a, b = ordine[i], ordine[i + 1]
        t = a if rng.random() < 0.5 else b
        coppie.append({"n": i // 2 + 1, "pagine": [a[0], b[0]], "trattata": t[0]})
    return coppie


def impronte_controllo(G, slugs):
    out = {}
    for s in slugs:
        f = G.SITO / "visa-refusal-rates" / s / "index.html"
        t = f.read_text(encoding="utf-8")
        out[s] = {"contenuto": G.impronta_contenuto(t), "file_sha256": hashlib.sha256(t.encode("utf-8")).hexdigest()}
    return out


def assegna(args):
    if FILE.exists() and not args.rifai:
        raise SystemExit(f"{FILE} esiste già: l'assegnazione si fa una volta sola (--rifai solo prima della pubblicazione).")
    pagine, G = pagine_esperimento()
    al = args.al or date.today().isoformat()
    lb = visite(INIZIO_CONTATORE, al)
    coppie = coppie_e_gruppi(pagine, lb)
    info = {s: {"nome": n, "domande": d, "visite": lb.get(s, [0, 0])[0], "visite_assistente": lb.get(s, [0, 0])[1]} for s, n, d in pagine}
    trattate = sorted(c["trattata"] for c in coppie)
    controllo = sorted(s for c in coppie for s in c["pagine"] if s != c["trattata"])
    dati = {
        "_nota": ("Esperimento A/B sulle pagine Paese di /visa-refusal-rates/ (31/10/2026). Scritto da raccolta/esperimento_citazioni.py assegna: "
                  "non modificare a mano. Piano, metrica e soglia: studio-business/intelaiatura/esperimento-citazioni-2026-10-31.md."),
        "creato_il": date.today().isoformat(),
        "seme": SEME,
        "metodo": ("pagine ordinate per visite dall'assistente misurato, poi visite totali, poi domande di visto dell'ultimo anno, poi slug; "
                   "coppie di pagine vicine; in ogni coppia random.Random(seme).random() < 0.5 sceglie la prima pagina come trattata, altrimenti la seconda"),
        "linea_base": {"fonte": "GoatCounter stats/hits e stats/hits/{id}", "dal": INIZIO_CONTATORE, "al": al},
        "escluse": ESCLUSE,
        "pagine": info,
        "coppie": coppie,
        "trattate": trattate,
        "controllo": controllo,
        "impronte_controllo": impronte_controllo(G, controllo),
        "impronte_aggiornate": [],
    }
    FILE.write_text(json.dumps(dati, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(coppie)} coppie, {len(trattate)} trattate, {len(controllo)} di controllo; linea di base {INIZIO_CONTATORE} – {al}: "
          f"{sum(v[0] for v in lb.values())} visite, {sum(v[1] for v in lb.values())} dall'assistente. Scritto {FILE}")


def impronte(args):
    """Dopo un cambio VOLUTO dei dati (es. aggiornamento mensile di rifiuti_altri.json, uguale per i due gruppi): riscrive le impronte
    delle pagine di controllo, solo se nessuna ha elementi del trattamento, e annota la data e il motivo nel file."""
    import genera as G
    d = json.loads(FILE.read_text(encoding="utf-8"))
    for s in d["controllo"]:
        t = (G.SITO / "visa-refusal-rates" / s / "index.html").read_text(encoding="utf-8")
        if any(m in t for m in G.SEGNI_ESPERIMENTO):
            raise SystemExit(f"{s}: pagina di controllo con elementi del trattamento: correggere genera.py, non le impronte")
    d["impronte_controllo"] = impronte_controllo(G, d["controllo"])
    d["impronte_aggiornate"].append({"il": date.today().isoformat(), "motivo": args.motivo})
    FILE.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Impronte di {len(d['controllo'])} pagine di controllo riscritte ({args.motivo}).")


def mese_equivalente(n, giorni):
    return n * 30 / giorni


def controllo_di(c):
    return next(s for s in c["pagine"] if s != c["trattata"])


def esito(coppie, v, giorni):
    tt = sum(v.get(c["trattata"], [0, 0])[1] for c in coppie)
    tc = sum(v.get(controllo_di(c), [0, 0])[1] for c in coppie)
    rapporto = (tt / tc) if tc else float("inf")
    diff_mese = mese_equivalente(tt - tc, giorni)
    return tt, tc, rapporto, diff_mese, rapporto >= 1.5 and diff_mese >= 30   # controllo a 0: rapporto infinito, decide la differenza


def misura(args):
    d = json.loads(FILE.read_text(encoding="utf-8"))
    v = visite(args.dal, args.al)
    giorni = (date.fromisoformat(args.al) - date.fromisoformat(args.dal)).days + 1
    print(f"Visite con provenienza {ORIGINE}, {args.dal} – {args.al} ({giorni} giorni)")
    print(" n  trattata                     vis.  base   controllo                    vis.  base")
    for c in d["coppie"]:
        t, k = c["trattata"], controllo_di(c)
        print(f"{c['n']:>2}  {t:<28} {v.get(t, [0, 0])[1]:>4}  {d['pagine'][t]['visite_assistente']:>4}   "
              f"{k:<28} {v.get(k, [0, 0])[1]:>4}  {d['pagine'][k]['visite_assistente']:>4}")
    tt, tc, rapporto, diff_mese, ok = esito(d["coppie"], v, giorni)
    vinte = sum(1 for c in d["coppie"] if v.get(c["trattata"], [0, 0])[1] > v.get(controllo_di(c), [0, 0])[1])
    pari = sum(1 for c in d["coppie"] if v.get(c["trattata"], [0, 0])[1] == v.get(controllo_di(c), [0, 0])[1])
    print(f"\nTotale trattate {tt}, controllo {tc}; rapporto {rapporto:.2f}; differenza {tt - tc} (≈ {diff_mese:.0f} al mese). "
          f"Coppie vinte dalla trattata {vinte}, pari {pari}, perse {len(d['coppie']) - vinte - pari}.")
    print("1) Soglia (trattate ≥ 1,5 × controllo E ≥ 30 visite al mese in più): " + ("SUPERATA" if ok else "non superata"))
    # linea di base: le trattate partivano già sopra (coppia 1, Pakistan); il rapporto corretto toglie questo vantaggio di partenza
    bt = sum(d["pagine"][c["trattata"]]["visite_assistente"] for c in d["coppie"])
    bc = sum(d["pagine"][controllo_di(c)]["visite_assistente"] for c in d["coppie"])
    rb = bt / bc if bc else float("inf")
    print(f"2) Linea di base {d['linea_base']['dal']} – {d['linea_base']['al']}: trattate {bt}, controllo {bc}, rapporto {rb:.2f}; "
          f"rapporto corretto = {rapporto:.2f} ÷ {rb:.2f} = {rapporto / rb:.2f} (deve essere ≥ 1,5)")
    senza1 = esito([c for c in d["coppie"] if c["n"] != 1], v, giorni)
    print(f"3) Senza la coppia 1: trattate {senza1[0]}, controllo {senza1[1]}, rapporto {senza1[2]:.2f}, "
          f"≈ {senza1[3]:.0f} al mese in più: " + ("superata" if senza1[4] else "non superata"))
    # prova a permutazione sulle coppie (segni casuali delle differenze): quanto spesso il caso dà una differenza almeno così grande
    diffs = [v.get(c["trattata"], [0, 0])[1] - v.get(controllo_di(c), [0, 0])[1] for c in d["coppie"]]
    rng = random.Random(1)
    n = 20000
    p = sum(1 for _ in range(n) if sum(x if rng.random() < 0.5 else -x for x in diffs) >= sum(diffs)) / n
    print(f"4) Prova a permutazione sulle coppie (unilaterale, {n} giri): p ≈ {p:.3f}")
    print("Verdetto (piano): successo solo se 1) e 2) sono superate; 3) e 4) dicono quanto fidarsi.")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("assegna")
    a.add_argument("--al", help="ultimo giorno della linea di base (AAAA-MM-GG, default oggi)")
    a.add_argument("--rifai", action="store_true")
    m = sp.add_parser("misura")
    m.add_argument("--dal", required=True)
    m.add_argument("--al", required=True)
    i = sp.add_parser("impronte")
    i.add_argument("--motivo", required=True)
    args = ap.parse_args()
    {"assegna": assegna, "misura": misura, "impronte": impronte}[args.cmd](args)


if __name__ == "__main__":
    main()
