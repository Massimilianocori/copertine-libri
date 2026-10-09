"""Scarica e analizza gli avvisi pubblicati direttamente sui siti dei Comuni (Municipium e altri CMS).

Gli URL di partenza non si possono elencare da un indice centrale: si trovano con una ricerca web
("bando posteggi 2026 site:municipiumapp.it", "avviso assegnazione posteggi fiera 2026 <regione>") e si
salvano in un file TSV (url, comune, provincia, regione, trovato_con). Questo script:
  1) scarica ogni URL (una richiesta ogni 1,5 s, User-Agent identificabile);
  2) se è un PDF ne estrae il testo; se è una pagina HTML ne estrae il testo e scarica fino a 2 PDF
     allegati il cui nome contiene "avviso", "bando", "domanda" o "posteggi";
  3) estrae tipo, numero posteggi, scadenza e data di pubblicazione con le euristiche di comune.py.

Uso:
  python3 -I comuni_web.py <semi.tsv> <cartella_download> <file_json_uscita>
"""
import csv
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune as C  # noqa: E402

RX_ALLEGATO = re.compile(r'href="([^"]+?\.pdf[^"]*)"', re.I)
RX_UTILE = re.compile(r"avvis|bando|domand|posteg|fiera|graduator|spunt", re.I)
RX_PUBBL = [
    re.compile(r"(?:pubblicat[oa]|data di pubblicazione|data pubblicazione|data)\s*(?:il|:)?\s*(\d{1,2}[./-]\d{1,2}[./-]\d{4}|\d{1,2}\s+\w+\s+\d{4})", re.I),
]


def testo_html(dati):
    s = dati.decode("utf-8", "replace")
    s = re.sub(r"<(script|style|nav|footer|header)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>|</p>|</li>|</h\d>|</div>|</tr>", "\n", s, flags=re.I)
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"[ \t ]+", " ", re.sub(r"\n\s*\n+", "\n", s))


def data_pubblicazione(testo, url):
    for rx in RX_PUBBL:
        m = rx.search(testo)
        if m:
            d = C._RX_DATA.search(m.group(1))
            if d and C._data_iso(d):
                return C._data_iso(d)
    m = re.search(r"/(20\d\d)/(\d\d)/", url)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return None


def main():
    semi, cartella, uscita = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(cartella, exist_ok=True)
    t0 = time.time()
    out = []
    with open(semi, encoding="utf-8") as f:
        righe = list(csv.DictReader(f, delimiter="\t"))
    for r in righe:
        url = r["url"]
        nome = hashlib.sha1(url.encode()).hexdigest()[:12]
        st, ct, dati = C.scarica(url, os.path.join(cartella, nome + ".bin"))
        formato = "pdf" if (dati[:4] == b"%PDF") else ("html" if dati else "")
        testo, allegati = "", []
        if formato == "pdf":
            testo = C.testo_pdf(os.path.join(cartella, nome + ".bin"))
        elif formato == "html":
            testo = testo_html(dati)
            for a in RX_ALLEGATO.findall(dati.decode("utf-8", "replace")):
                a = urllib.parse.urljoin(url, html.unescape(a))
                if RX_UTILE.search(urllib.parse.unquote(a.rsplit("/", 1)[-1])) and a not in allegati:
                    allegati.append(a)
            for a in allegati[:2]:
                loc = os.path.join(cartella, hashlib.sha1(a.encode()).hexdigest()[:12] + ".pdf")
                sa, _, da = C.scarica(a, loc)
                if sa == 200 and da[:4] == b"%PDF":
                    testo += "\n\n[ALLEGATO " + a + "]\n" + C.testo_pdf(loc)
        out.append({**r, "http": st, "content_type": ct, "formato": formato, "allegati_pdf": allegati[:5],
                    "caratteri_testo": len(testo),
                    "tipo_auto": C.estrai_tipo(testo), "posteggi_auto": C.estrai_numero(testo),
                    "scadenza_auto": C.estrai_scadenza(testo), "pubblicazione_auto": data_pubblicazione(testo, url),
                    "testo_inizio": C.normalizza(testo[:1500])})
        print(st, formato, len(testo), r["comune"], url[:90], flush=True)
    with open(uscita, "w", encoding="utf-8") as f:
        json.dump({"fonte": "Siti comunali (URL trovati con ricerca web)", "verificato_il": time.strftime("%Y-%m-%d"),
                   "secondi": round(time.time() - t0), "avvisi": out}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
