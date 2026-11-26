"""Seme del registro dati/lastmod.json (26/11/2026): data vera dell'ultimo cambio del testo principale di ogni pagina, da git.

Uso (dalla radice del repository, una volta sola, PRIMA di rigenerare con dati nuovi):
    python3 heatpumps/raccolta/lastmod_seme.py            # stampa il rapporto e scrive il registro
    python3 heatpumps/raccolta/lastmod_seme.py --prova    # solo il rapporto

Per ogni commit che ha toccato heatpumps/sito si calcola l'impronta di ogni pagina con genera.impronta_contenuto (testo di <main>
senza la riga delle date di controllo e con le date sostituite da un segno). La data di una pagina è quella dell'ultimo commit in
cui la sua impronta è cambiata (o in cui è nata): una rigenerazione di tutto il sito che cambia solo date, piè di pagina o <head>
non sposta nulla. L'impronta salvata è quella della pagina in HEAD: se la generazione successiva la cambia, genera.py scrive oggi.
"""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
REPO = RADICE.parent
sys.path.insert(0, str(RADICE))
import genera as G  # noqa: E402


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, check=True).stdout


def main():
    commit = [r.split() for r in git("log", "--reverse", "--format=%H %cs", "--", "heatpumps/sito").decode().splitlines()]
    ultimo, imp_prima, cambi = {}, {}, []
    for hh, giorno in commit:
        righe = [r.split("\t", 1) for r in git("ls-tree", "-r", hh, "--", "heatpumps/sito").decode().splitlines()]
        blob = {nome[len("heatpumps/sito/"):]: meta.split()[2] for meta, nome in righe if nome.endswith(".html")}
        out = subprocess.run(["git", "-C", str(REPO), "cat-file", "--batch"], input="\n".join(blob.values()).encode() + b"\n",
                             capture_output=True, check=True).stdout
        pos, ora, n = 0, {}, 0
        for nome in blob:
            fine = out.index(b"\n", pos)
            lung = int(out[pos:fine].split()[2])
            html_ = out[fine + 1:fine + 1 + lung].decode("utf-8", "replace")
            pos = fine + 1 + lung + 1
            if 'rel="canonical"' not in html_:
                continue
            u = nome[:-len("index.html")] if nome.endswith("index.html") else nome
            ora[u] = G.impronta_contenuto(html_)
            if imp_prima.get(u) != ora[u]:
                ultimo[u] = giorno
                n += 1
        cambi.append((hh[:9], giorno, n, len(ora)))
        imp_prima = ora
    for c in cambi:
        print("commit %s del %s: contenuto cambiato in %d pagine indicizzabili su %d" % c)
    reg = {u: [ultimo[u], imp] for u, imp in imp_prima.items()}
    print("distribuzione del seme:", dict(sorted(Counter(v[0] for v in reg.values()).items())))
    if "--prova" not in sys.argv:
        G.REGISTRO_LASTMOD.write_text(json.dumps({"_nota": "seme da git, vedi raccolta/lastmod_seme.py", "pagine": dict(sorted(reg.items()))},
                                                 ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
        print(f"scritto {G.REGISTRO_LASTMOD} ({len(reg)} pagine)")


if __name__ == "__main__":
    main()
