"""Ricontrollo delle impronte delle fonti (campo "impronta" in dati/destinazioni.json, anche dentro "evento", e in dati/spagna_licenze.json).

Uso (dalla radice del repository):
    python3 -I touristtax/raccolta/impronte.py            # riscarica le fonti con impronta e dice quali sono cambiate
    python3 -I touristtax/raccolta/impronte.py URL        # stampa l'impronta di un solo indirizzo (per una fonte nuova)

Ricetta (la stessa usata il 4/11/2026 per scrivere i dati):
- impronta_di = "file": sha256 dei byte scaricati (PDF).
- impronta_di = "testo": pagina HTML decodificata in UTF-8; se c'è un elemento <main>...</main> si tiene solo quello
  (comune.napoli.it, poderjudicial.es), altrimenti tutta la pagina (boe.es e catedraldesantiago.es non hanno <main>);
  si tolgono i blocchi <script>, <style> e <form> (così il nonce degli script della Cattedrale e i token dei moduli non
  contano), poi tutti i tag; si sciolgono le entità HTML e ogni sequenza di spazi diventa uno spazio; sha256 del testo
  risultante in UTF-8. Un cambio di impronta vuol dire: rileggere la fonte, non per forza che la tariffa sia cambiata.
Nessuna scrittura: lo script legge e stampa soltanto.
"""
import hashlib
import html
import json
import re
import subprocess
import sys
from pathlib import Path

DATI = Path(__file__).resolve().parent.parent / "dati" / "destinazioni.json"


def scarica(url):
    r = subprocess.run(["curl", "-sS", "-L", "-m", "90", "-w", "\n%{http_code}", url], capture_output=True)
    corpo, _, codice = r.stdout.rpartition(b"\n")
    return int(codice or 0), corpo


def impronta(corpo):
    if corpo[:4] == b"%PDF":
        return "file", "sha256:" + hashlib.sha256(corpo).hexdigest()
    t = corpo.decode("utf-8", "replace")
    m = re.search(r"<main.*?</main>", t, re.S)
    t = m.group(0) if m else t
    t = re.sub(r"<script.*?</script>|<style.*?</style>|<form.*?</form>", "", t, flags=re.S)
    s = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip()
    return "testo", "sha256:" + hashlib.sha256(s.encode("utf-8")).hexdigest()


def main():
    if len(sys.argv) > 1:
        codice, corpo = scarica(sys.argv[1])
        print(codice, *impronta(corpo))
        return
    dest = json.loads(DATI.read_text(encoding="utf-8"))["destinazioni"]
    cambiate = 0
    for d in dest:
        for f in d["fonti"] + (d.get("evento") or {}).get("fonti", []):
            if not f.get("impronta"):
                continue
            codice, corpo = scarica(f["url"])
            tipo, imp = impronta(corpo)
            ok = codice == 200 and tipo == f["impronta_di"] and imp == f["impronta"]
            cambiate += not ok
            print(f"{'ok      ' if ok else 'CAMBIATA'} {d['slug']}: HTTP {codice} {f['url']}")
    # Spagna, licenza per affitti turistici (5/11/2026): fonti in dati/spagna_licenze.json. "url_impronta" = indirizzo letto per
    # l'impronta quando la pagina per le persone è un'applicazione JavaScript (tabelle INE, catalogo dati della Catalogna).
    spagna = json.loads((DATI.parent / "spagna_licenze.json").read_text(encoding="utf-8"))["fonti"]
    for k, f in spagna.items():
        codice, corpo = scarica(f.get("url_impronta", f["url"]))
        tipo, imp = impronta(corpo)
        ok = codice == 200 and tipo == f["impronta_di"] and imp == f["impronta"]
        cambiate += not ok
        print(f"{'ok      ' if ok else 'CAMBIATA'} spagna/{k}: HTTP {codice} {f.get('url_impronta', f['url'])}")
    print(f"Fonti con impronta cambiata o non leggibile: {cambiate}")


if __name__ == "__main__":
    main()
