"""Seme del registro dati/lastmod.json (25/11/2026): la data vera dell'ultimo cambio del testo principale di ogni pagina, da git.

Uso (dalla radice del repository, una volta sola, DOPO una generazione che ha scritto dati/lastmod.json):
    python3 beforeyoufly/raccolta/lastmod_seme.py            # stampa il rapporto e scrive il registro
    python3 beforeyoufly/raccolta/lastmod_seme.py --prova    # solo il rapporto

Vale per le pagine senza una data propria nei dati (quelle del registro: passaporti, misure del bagaglio, home, About, …).
Metodo: per ogni commit che ha toccato beforeyoufly/sito si legge il testo principale di ogni pagina (testo visibile di <main>, senza
date, come genera.impronta_contenuto) e lo si divide in frasi. Una frase è «di modello» se il suo scheletro (nomi propri e numeri
sostituiti da un segno) compare in almeno il 30 % delle pagine della stessa sezione in quel commit: riquadri aggiunti a tutte le
pagine, titoli riscritti in blocco, link tra sezioni. Le altre frasi sono il contenuto proprio della pagina (testo ufficiale citato,
risposta, regola). Un commit «cambia» una pagina solo se aggiunge o toglie una frase propria: così una rigenerazione di tutto il sito
non dà la stessa data a tutte le pagine. Data = ultimo commit che ha cambiato il contenuto proprio della pagina, o quello che l'ha
creata. L'impronta salvata è quella della pagina in HEAD: se la generazione di oggi la cambia, genera.py scrive la data di oggi.
"""
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
REPO = RADICE.parent
sys.path.insert(0, str(RADICE))
import genera as G  # noqa: E402

SOGLIA, MINIMO = 0.3, 10


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, check=True).stdout


def frasi(html):
    m = re.search(r'<main id="main">(.*?)</main>', html, re.S)
    t = m.group(1) if m else ""
    t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>|<svg.*?</svg>", " ", t)
    t = unescape(re.sub(r"<[^>]+>", " ", t))
    t = re.sub(r"\s+", " ", G._DATE_RE.sub("§", t)).strip()
    return frozenset(x.strip() for x in re.split(r"(?<=[.?!:·›]) ", t) if x.strip())


def scheletro(f):
    return re.sub(r"(?:§[ ,]*(?:and |of |the |de )*)+", "§ ", re.sub(r"\d+", "#", re.sub(r"\b[A-Z][\w'’.&-]*", "§", f)))


def main():
    reg = json.loads(G.REGISTRO_LASTMOD.read_text(encoding="utf-8"))
    pagine = sorted(reg["pagine"])
    file_di = {"beforeyoufly/sito/" + (u if u.endswith(".html") else u + "index.html"): u for u in pagine}
    commit = [r.split() for r in git("log", "--reverse", "--format=%H %cs", "--", "beforeyoufly/sito").decode().splitlines()]
    blob = []  # per commit: percorso -> blob
    for h, _ in commit:
        m = {}
        for riga in git("ls-tree", "-r", h, "--", "beforeyoufly/sito").decode().splitlines():
            meta, nome = riga.split("\t", 1)
            if nome in file_di:
                m[file_di[nome]] = meta.split()[2]
        blob.append(m)
    unici = sorted({b for m in blob for b in m.values()})
    out = subprocess.run(["git", "-C", str(REPO), "cat-file", "--batch"], input="\n".join(unici).encode() + b"\n", capture_output=True, check=True).stdout
    testo, pos = {}, 0
    for b in unici:
        fine = out.index(b"\n", pos)
        n = int(out[pos:fine].split()[2])
        testo[b] = out[fine + 1:fine + 1 + n].decode("utf-8", "replace")
        pos = fine + 1 + n + 1
    fr = {b: frasi(t) for b, t in testo.items()}
    sezione = lambda u: u.split("/")[0] if "/" in u else ""
    prima = {}                  # pagina -> (frasi, frasi proprie) al commit precedente in cui c'era
    eventi = defaultdict(list)  # pagina -> indici dei commit che l'hanno creata o ne hanno cambiato il contenuto proprio
    for i, m in enumerate(blob):
        conta, n_sez = defaultdict(Counter), Counter()
        for u, b in m.items():
            n_sez[sezione(u)] += 1
            conta[sezione(u)].update({scheletro(f) for f in fr[b]})
        for u, b in m.items():
            s_ = sezione(u)
            modello = {k for k, n in conta[s_].items() if n_sez[s_] >= MINIMO and n / n_sez[s_] >= SOGLIA}
            tutte = fr[b]
            proprie = frozenset(f for f in tutte if scheletro(f) not in modello)
            if u not in prima:
                eventi[u].append(i)
            elif (proprie - prima[u][0]) or (prima[u][1] - tutte):
                eventi[u].append(i)
            prima[u] = (tutte, proprie)
    date, testa = {}, blob[-1]
    for u in pagine:
        if u in testa:  # le pagine nate oggi le data genera.py
            date[u] = [commit[max(eventi[u])][1], G.impronta_contenuto(testo[testa[u]])]
    print(f"{len(commit)} commit, {len(unici)} versioni lette, {len(date)} pagine datate su {len(pagine)}")
    c = Counter(d for d, _ in date.values())
    print("date:", ", ".join(f"{d} × {n}" for d, n in sorted(c.items())))
    for s_ in sorted({sezione(u) for u in date}):
        print(f"  {s_ or '(radice)'}: " + ", ".join(f"{d} × {n}" for d, n in sorted(Counter(v[0] for u, v in date.items() if sezione(u) == s_).items())))
    if "--prova" not in sys.argv:
        for u, v in date.items():
            reg["pagine"][u] = v
        G.REGISTRO_LASTMOD.write_text(json.dumps(reg, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
        print("scritto", G.REGISTRO_LASTMOD)




def seme_dati(base="c16c0388b"):
    """Secondo seme (26/11/2026), per le pagine con una data propria nei dati che il 25/11 sono state solo rilette: `--dati`.
    Se il testo principale della pagina è uguale a quello pubblicato prima della rilettura (commit `base`), il lastmod non è la data
    della rilettura ma l'ultimo cambio vero: per «Available in» il `cambiato_il` della lista del servizio, per i liquidi il
    `controllato_il` di prima della rilettura; mai prima del commit che ha creato la pagina."""
    reg = json.loads(G.REGISTRO_LASTMOD.read_text(encoding="utf-8"))
    P = reg["pagine"]
    nate = {}
    data = None
    for riga in git("log", "--diff-filter=A", "--format=@%cs", "--name-only", "--", "beforeyoufly/sito/available-in", "beforeyoufly/sito/liquids").decode().splitlines():
        if riga.startswith("@"):
            data = riga[1:]
        elif riga.endswith("index.html"):
            nate[riga[len("beforeyoufly/sito/"):-len("index.html")]] = min(data, nate.get(riga[len("beforeyoufly/sito/"):-len("index.html")], data))
    srv = {S["slug"]: S["cambiato_il"] for S in G.SERVIZI_SRV}
    aer_prima = json.loads(git("show", f"{base}~1:beforeyoufly/dati/aeroporti.json").decode())
    liq = {A["slug"]: A["controllato_il"] for A in aer_prima["aeroporti"] + aer_prima["nazionali"]}
    prima, dopo, n = Counter(), Counter(), 0
    for u, v in P.items():
        if not (u.startswith("available-in/") or u.startswith("liquids/")):
            continue
        prima[v[0]] += 1
        r = subprocess.run(["git", "-C", str(REPO), "show", f"{base}:beforeyoufly/sito/{u}index.html"], capture_output=True)
        if r.returncode == 0 and G.impronta_contenuto(r.stdout.decode("utf-8", "replace")) == v[1]:
            pezzi = u.rstrip("/").split("/")
            if pezzi[0] == "liquids":
                d = liq.get(pezzi[1]) if len(pezzi) > 1 else max(liq.values())
            else:
                d = srv.get(pezzi[1]) if len(pezzi) > 1 else max(x for x in srv.values() if x < v[0])
            if d and d < v[0]:
                v[0] = max(d, nate.get(u, d))
                n += 1
        dopo[v[0]] += 1
    print(f"{n} pagine con il testo uguale a prima della rilettura: data riportata all'ultimo cambio vero")
    print("prima:", ", ".join(f"{d} × {k}" for d, k in sorted(prima.items())))
    print("dopo: ", ", ".join(f"{d} × {k}" for d, k in sorted(dopo.items())))
    G.REGISTRO_LASTMOD.write_text(json.dumps(reg, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")


if __name__ == "__main__":
    seme_dati() if "--dati" in sys.argv else main()
