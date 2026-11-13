"""Testo dei file di legge salvati (usato da genera.py): HTML, PDF o XML -> una riga di testo normalizzato.

Normalizzazione: niente script/stili/tag, entità sciolte, spazi (anche a capo e spazi non separabili) ridotti a uno,
apostrofi e virgolette tipografiche resi diritti. Le citazioni in dati/norme.json devono comparire tali e quali in questo testo:
genera.py si ferma se una manca. verifica.py usa un estrattore suo, scritto a parte, per lo stesso controllo.
"""
import html
import json
import re
import subprocess
from functools import lru_cache
from pathlib import Path

RADICE = Path(__file__).resolve().parent
GREZZI = RADICE / "raccolta" / "_grezzi"
FONTI = json.loads((RADICE / "dati" / "fonti.json").read_text(encoding="utf-8"))

_SOST = {"’": "'", "‘": "'", "“": '"', "”": '"', " ": " ", " ": " ", " ": " ", "­": ""}


def normalizza(t):
    for a, b in _SOST.items():
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).strip()


def _da_html(grezzo):
    t = re.sub(r"(?is)<!--.*?-->", " ", grezzo)
    t = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", t)
    t = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h\d|tr|td|section|article)>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    return html.unescape(t)


@lru_cache(maxsize=None)
def testo(fid):
    voce = FONTI[fid]
    f = GREZZI / voce["file"]
    if not f.exists():
        raise SystemExit(f"manca il file grezzo {f}: lanciare python3 limits/raccolta/fonti.py")
    if f.suffix == ".pdf":
        t = subprocess.run(["pdftotext", "-raw", str(f), "-"], capture_output=True, text=True, check=True).stdout
    else:
        t = _da_html(f.read_text(encoding="utf-8", errors="replace"))
    return normalizza(t)


def contiene(fid, frammento):
    return normalizza(frammento) in testo(fid)
