"""Scarica le pagine ufficiali usate dalla sezione «Auto repair laws by state» e ritrova ogni frase citata in dati/officine-stati.json
(frasi dei fatti e voci delle checklist).

Uso (dalla radice del repository):
    python3 -I naics/raccolta/officine.py            # scarica solo i file che mancano in raccolta/_grezzi/officine/
    python3 -I naics/raccolta/officine.py --rete     # riscarica tutto (aggiornamento mensile)

Scrive dati/officine-fonti.json: per ogni fonte indirizzo, HTTP, byte, data di lettura, impronta delle frasi citate e, frase per frase,
se è stata ritrovata. Una frase non ritrovata (pagina cambiata, 403, pagina che ora vuole JavaScript) NON si corregge a mano:
si rilegge la pagina e si riscrive il fatto, oppure si toglie lo Stato. genera.py si ferma finché officine-fonti.json ha frasi non ritrovate.
Le pagine che rispondono 403 non si aggirano (il 19/11/2026: leginfo.legislature.ca.gov e nysenate.gov; vedi «non_letti»).
Confronto: senza spazi, virgolette e trattini uniformati, puntini di riempimento dei PDF tolti; i PDF si leggono con pdftotext -layout.
Pausa di 1 secondo tra le richieste. Nessun dato personale.
"""
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import date
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
GREZZI = RADICE / "raccolta" / "_grezzi" / "officine"
DATI = RADICE / "dati"
UA = "Mozilla/5.0 (compatible; naics-check/1.0)"


def stretto(t):
    """Testo per il confronto: virgolette, apostrofi e trattini uniformati, puntini di riempimento tolti, nessuno spazio."""
    t = unescape(t)
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("–", "-"), ("—", "-"), ("­", ""), ("​", "")):
        t = t.replace(a, b)
    t = re.sub(r"[.…]{3,}", " ", t)
    return re.sub(r"\s+", "", t)


def testo_di(percorso, tipo):
    if tipo == "pdf":
        return subprocess.run(["pdftotext", "-layout", str(percorso), "-"], capture_output=True, text=True, check=True).stdout
    s = percorso.read_text(encoding="utf-8", errors="replace")
    s = re.sub(r"(?is)<(script|style|svg|noscript)\b.*?</\1>", " ", s)
    s = re.sub(r"(?s)<!--.*?-->", " ", s)
    return unescape(re.sub(r"<[^>]+>", " ", s))


def scarica(url, dest):
    r = subprocess.run(["curl", "-sS", "-L", "-m", "60", "-A", UA, "-o", str(dest), "-w", "%{http_code}", url], capture_output=True, text=True)
    time.sleep(1)
    return int(r.stdout.strip() or 0) if r.returncode == 0 else 0


def main():
    rete = "--rete" in sys.argv
    GREZZI.mkdir(parents=True, exist_ok=True)
    stati = json.loads((DATI / "officine-stati.json").read_text(encoding="utf-8"))
    vecchio = json.loads((DATI / "officine-fonti.json").read_text(encoding="utf-8"))["fonti"] if (DATI / "officine-fonti.json").exists() else {}
    frasi = {}
    for s in stati["stati"]:
        for f in s["fatti"]:
            for c in f["citazioni"]:
                if c["testo"] not in frasi.setdefault(c["fonte"], []):
                    frasi[c["fonte"]].append(c["testo"])
        for g in s["checklist"]:
            for c in g["voci"]:
                if c["testo"] not in frasi.setdefault(c["fonte"], []):
                    frasi[c["fonte"]].append(c["testo"])
    out, mancanti = {}, 0
    for fid, f in stati["fonti"].items():
        dest = GREZZI / f"{fid}.{'pdf' if f['tipo'] == 'pdf' else 'html'}"
        prima = vecchio.get(fid, {})
        http, letto = prima.get("http", 0), prima.get("letto_il")
        if rete or not dest.exists() or not letto:
            http, letto = scarica(f["url"], dest), date.today().isoformat()
        testo = stretto(testo_di(dest, f["tipo"])) if dest.exists() and http == 200 else ""
        trovate = {t: stretto(t) in testo for t in frasi.get(fid, [])}
        mancanti += sum(1 for v in trovate.values() if not v)
        out[fid] = {"url": f["url"], "titolo": f["titolo"], "chi": f["chi"], "tipo": f["tipo"], "file": dest.name, "http": http,
                    "byte": dest.stat().st_size if dest.exists() else 0, "letto_il": letto,
                    "sha256_frasi": hashlib.sha256("\n".join(sorted(frasi.get(fid, []))).encode("utf-8")).hexdigest(),
                    "frasi": [{"testo": t, "trovata": v} for t, v in trovate.items()]}
        print(f"{fid}: HTTP {http}, {out[fid]['byte']} byte, frasi {sum(trovate.values())}/{len(trovate)}")
        for t, v in trovate.items():
            if not v:
                print("   NON RITROVATA:", t[:110])
    (DATI / "officine-fonti.json").write_text(json.dumps({
        "_nota": "Scritto da raccolta/officine.py. File grezzi in raccolta/_grezzi/officine/ (fuori da git). Le pagine HTML cambiano byte a ogni scarico: "
                 "fa fede sha256_frasi (le frasi citate alla lettera) e «trovata» per ogni frase; verifica.py le ricerca di nuovo nei file grezzi.",
        "fonti": out}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(out)} fonti, {sum(len(v) for v in frasi.values())} frasi citate, {mancanti} non ritrovate")
    sys.exit(1 if mancanti else 0)


if __name__ == "__main__":
    main()
