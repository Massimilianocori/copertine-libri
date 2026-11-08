"""Rilegge le fonti delle regole (dati/regole.json, voce "fonti") e scrive dati/fonti.json: codice HTTP, data, impronta
(sha256 del testo visibile, spazi normalizzati) e, per ogni frase di "cerca", se compare ancora nel testo letto.

Uso (dalla radice del repository):
    python3 solarebalcone/raccolta/fonti.py

Le fonti con "non_letta": true non si scaricano: in dati/fonti.json resta il motivo scritto. Le pagine di Normattiva
servono il testo dell'articolo solo dopo una prima visita (cookie di sessione): "url" apre la sessione, "sessione" è
l'indirizzo che restituisce il testo. I PDF si leggono con pdftotext (poppler-utils). Solo curl e libreria standard:
nessun aggiramento di blocchi o verifiche anti-robot.
"""
import hashlib
import html
import json
import re
import subprocess
import sys
import tempfile
import unicodedata
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
UA = "Mozilla/5.0 (X11; Linux x86_64) solarebalcone/1.0"


def normalizza(t):
    t = unicodedata.normalize("NFC", t)
    t = t.replace("’", "'").replace(" ", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", t).strip()


def testo_html(b):
    t = b.decode("utf-8", "replace")
    t = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", t, flags=re.S | re.I)
    return normalizza(html.unescape(re.sub(r"<[^>]+>", " ", t)))


def testo_pdf(b):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "f.pdf"
        p.write_bytes(b)
        r = subprocess.run(["pdftotext", "-enc", "UTF-8", str(p), "-"], capture_output=True)
        t = r.stdout.decode("utf-8", "replace")
    t = re.sub(r"-\n(?=\w)", "", t)  # parole spezzate a fine riga
    return normalizza(t)


def curl(url, cookie=None, tempo=90):
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "corpo"
        cmd = ["curl", "-sL", "--max-time", str(tempo), "-A", UA, "-o", str(out), "-w", "%{http_code}", url]
        if cookie:
            cmd[1:1] = ["-c", cookie, "-b", cookie]
        r = subprocess.run(cmd, capture_output=True, text=True)
        codice = int(r.stdout.strip() or 0) if r.stdout.strip().isdigit() else 0
        return codice, (out.read_bytes() if out.exists() else b"")


def leggi_fonte(f):
    if f.get("sessione"):
        with tempfile.TemporaryDirectory() as d:
            cj = str(Path(d) / "cookie")
            codice, _ = curl(f["url"], cj)
            if codice != 200:
                return codice, b""
            return curl(f["sessione"], cj)
    return curl(f["url"])


def main():
    regole = json.loads((RADICE / "dati" / "regole.json").read_text(encoding="utf-8"))
    dest = RADICE / "dati" / "fonti.json"
    out = {"_nota": ("Esito della lettura delle fonti di dati/regole.json (raccolta/fonti.py). http = codice letto; sha256 = "
                     "impronta del testo visibile normalizzato; trovate = frasi di 'cerca' presenti nel testo; motivo = perché "
                     "una fonte non è stata letta."), "letto_il": date.today().isoformat(), "fonti": {}}
    problemi = 0
    for fid, f in regole["fonti"].items():
        if f.get("non_letta"):
            out["fonti"][fid] = {"http": None, "motivo": f["motivo"], "letto_il": date.today().isoformat()}
            print(f"{fid}: non letta ({f['motivo']})")
            continue
        codice, corpo = leggi_fonte(f)
        voce = {"http": codice, "letto_il": date.today().isoformat(), "byte": len(corpo)}
        if codice == 200 and corpo:
            testo = testo_pdf(corpo) if (f.get("pdf") or corpo[:5] == b"%PDF-") else testo_html(corpo)
            voce["sha256"] = hashlib.sha256(testo.encode("utf-8")).hexdigest()
            voce["caratteri"] = len(testo)
            voce["trovate"] = {c: normalizza(c) in testo for c in f.get("cerca", [])}
            mancano = [c for c, ok in voce["trovate"].items() if not ok]
            if mancano:
                problemi += 1
                print(f"{fid}: HTTP 200 ma mancano {len(mancano)} frasi: {mancano}")
            else:
                print(f"{fid}: HTTP 200, {len(voce['trovate'])} frasi trovate")
        else:
            problemi += 1
            voce["motivo"] = f"HTTP {codice} l'{date.today().strftime('%d/%m/%Y')}: da rileggere"
            print(f"{fid}: HTTP {codice}")
        out["fonti"][fid] = voce
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Scritto {dest}. Problemi: {problemi}.")
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
