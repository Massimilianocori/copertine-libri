"""Scarica le fonti ufficiali EOI in una cartella e scrive lo stato HTTP.

Uso: python3 scarica.py <cartella_grezzi>
- user-agent di un browser normale, una pausa tra le richieste;
- fino a 3 tentativi solo per gli errori di rete (000), mai per 403/429:
  un blocco del sito non si aggira;
- i PDF vengono convertiti in testo con `pdftotext -layout`.
Scrive <cartella_grezzi>/stato.json.
"""
import json, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fonti import FONTI

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def scarica(url, dest):
    for tentativo in range(3):
        r = subprocess.run(
            ["curl", "-sS", "-L", "-A", UA, "-m", "45", "-o", dest,
             "-w", "%{http_code} %{size_download} %{content_type}", url],
            capture_output=True, text=True)
        out = r.stdout.strip() or "000 0 -"
        codice = out.split()[0]
        if codice != "000":
            return out
        time.sleep(10)
    return out


def main(cartella):
    os.makedirs(cartella, exist_ok=True)
    stato = {}
    for nome, comunita, url, formato, ruolo in FONTI:
        dest = os.path.join(cartella, nome)
        out = scarica(url, dest)
        parti = out.split(" ", 2)
        codice, peso = parti[0], int(parti[1]) if len(parti) > 1 and parti[1].isdigit() else 0
        if codice == "200" and nome.endswith(".pdf") and peso > 0:
            subprocess.run(["pdftotext", "-layout", dest, dest[:-4] + ".txt"], capture_output=True)
        stato[nome] = {"comunita": comunita, "url": url, "http": codice, "byte": peso,
                       "tipo": parti[2] if len(parti) > 2 else "", "formato": formato, "ruolo": ruolo}
        print(f"{codice} {peso:>8} {comunita:<22} {nome}")
        time.sleep(1.5)
    with open(os.path.join(cartella, "stato.json"), "w", encoding="utf-8") as f:
        json.dump(stato, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
