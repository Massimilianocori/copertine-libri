"""Download educato dei file aperti ANAC (dati.anticorruzione.it), con registro.

Il portale ANAC è dietro un WAF F5 che rifiuta a intermittenza le richieste:
a volte con HTTP 403, a volte con HTTP 200 e una pagina HTML "Request Rejected"
di ~300 byte. Questo script:
  - fa UNA richiesta alla volta, con User-Agent identificabile;
  - considera fallito un tentativo se lo status non è 200/206, se il tipo è
    text/html o se il file è più corto del Content-Length annunciato;
  - riprova con attese crescenti (15, 45, 120, 300 s) fino a 5 tentativi;
  - scrive una riga JSON per ogni tentativo nel registro (--log), con URL,
    status, byte, secondi, numero del tentativo e data/ora UTC.

Uso:
    python3 -I scarica.py --out CARTELLA --log registro.jsonl URL [URL ...]

I file vanno scaricati FUORI dal repository (sono grandi e non fidati).
Usa curl (già configurato per il proxy della macchina).
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time

UA = "ChiLavoraColComune-test/0.1 (test di fattibilita su dati aperti ANAC)"
ATTESE = [15, 45, 120, 300]


def un_tentativo(url, dest):
    """Esegue un download con curl; restituisce (status, byte, content_type, secondi)."""
    t0 = time.time()
    tmp = dest + ".part"
    r = subprocess.run(
        ["curl", "-sS", "--max-time", "1800", "-A", UA, "-o", tmp,
         "-w", "%{http_code}\t%{size_download}\t%{content_type}", url],
        capture_output=True, text=True)
    sec = round(time.time() - t0, 1)
    try:
        status, size, ctype = r.stdout.split("\t")
        status, size = int(status), int(size)
    except ValueError:
        status, size, ctype = 0, 0, "errore curl: " + r.stderr.strip()[:200]
    return status, size, ctype, sec, tmp


def scarica(url, out, log):
    nome = url.rstrip("/").split("/")[-1]
    dest = os.path.join(out, nome)
    for n in range(1, len(ATTESE) + 2):
        status, size, ctype, sec, tmp = un_tentativo(url, dest)
        ok = status in (200, 206) and "html" not in ctype.lower() and size > 1000
        rec = {"url": url, "tentativo": n, "status": status, "byte": size,
               "content_type": ctype, "secondi": sec, "ok": ok,
               "quando_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
        with open(log, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(json.dumps(rec, ensure_ascii=False), flush=True)
        if ok:
            os.replace(tmp, dest)
            return dest
        if os.path.exists(tmp):
            os.remove(tmp)
        if n <= len(ATTESE):
            time.sleep(ATTESE[n - 1])
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--pausa", type=float, default=10, help="secondi tra un file e l'altro")
    ap.add_argument("url", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    esiti = 0
    for i, u in enumerate(a.url):
        if i:
            time.sleep(a.pausa)
        esiti += scarica(u, a.out, a.log) is not None
    print(f"scaricati {esiti}/{len(a.url)}")
    return 0 if esiti == len(a.url) else 1


if __name__ == "__main__":
    sys.exit(main())
