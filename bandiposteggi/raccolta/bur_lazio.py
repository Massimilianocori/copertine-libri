"""Raccolta degli avvisi sui posteggi dal BUR Lazio tramite le "Sintesi del Bollettino Ufficiale"
(pagine HTML dell'URP regionale che riportano per esteso gli avvisi di concorsi/selezioni, compresi
quelli dei Comuni e dei Municipi di Roma Capitale).

Fonte (verificata il 9/10/2026):
  elenco:   https://www.regione.lazio.it/urp/sintesi-concorsi-bur?pagina=<n>
  dettaglio: https://www.regione.lazio.it/urp/sintesi-concorsi-bur/sintesi-del-bollettino-ufficiale-n<NN>-del-<ggmmaaaa>

Uso:
  python3 -I bur_lazio.py <cartella_download> <file_json_uscita> [anno]

Ogni pagina di sintesi è divisa in blocchi per ente ("ENTI LOCALI - <ente>"); i blocchi che
contengono le parole chiave sui posteggi vengono salvati con i campi estratti da comune.py.
"""
import html
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune as C  # noqa: E402

ELENCO = "https://www.regione.lazio.it/urp/sintesi-concorsi-bur?pagina={p}"
RX_LINK = re.compile(r'href="(https://www\.regione\.lazio\.it/urp/sintesi-concorsi-bur/sintesi-del-bollettino-ufficiale-n-?(\d+)-del-(\d{2})(\d{2})(\d{4}))"')
RX_FORTE = re.compile(r"posteggi|posteggio|commercio su aree pubbliche|commercio su area pubblica|ambulant|chiosc|edicol|spunt", re.I)


def testo_html(dati):
    s = dati.decode("utf-8", "replace")
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>|</p>|</li>|</h\d>|</div>", "\n", s, flags=re.I)
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"[ \t ]+", " ", re.sub(r"\n\s*\n+", "\n", s))


def main():
    cartella, uscita = sys.argv[1], sys.argv[2]
    anno = sys.argv[3] if len(sys.argv) > 3 else "2026"
    t0 = time.time()
    pagine, visti = [], set()
    for p in range(1, 30):
        st, _, dati = C.scarica(ELENCO.format(p=p))
        nuovi = [(u, n, f"{a}-{m}-{g}") for u, n, g, m, a in RX_LINK.findall(dati.decode("utf-8", "replace"))]
        nuovi = [x for x in nuovi if x[0] not in visti]
        for x in nuovi:
            visti.add(x[0])
        pagine += [x for x in nuovi if x[2].startswith(anno)]
        print("elenco", p, st, len(nuovi), flush=True)
        if not nuovi or all(x[2] < anno for x in nuovi):
            break
    risultati, log = [], []
    for url, num, data in sorted(pagine, key=lambda x: x[2]):
        st, _, dati = C.scarica(url, os.path.join(cartella, f"sintesi-{data}-n{num}.htm"))
        t = testo_html(dati)
        blocchi = re.split(r"\n(?=\s*(?:ENTI LOCALI|AZIENDE|ALTRI ENTI|REGIONE LAZIO|ENTI PUBBLICI|UNIVERSIT|ENTI DEL SERVIZIO)[^\n]{0,80}\n)", t)
        trovati = 0
        for b in blocchi:
            if not RX_FORTE.search(b) or C.ESCLUDI.search(b[:300]):
                continue
            # un blocco può contenere più avvisi dello stesso ente: si separa sui punti elenco
            for avv in re.split(r"\n\s*•", b)[1:] or [b]:
                if not RX_FORTE.search(avv):
                    continue
                trovati += 1
                ente = b.strip().split("\n")[0].strip()
                righe = [r.strip() for r in avv.strip().split("\n") if r.strip()]
                titolo = " ".join(righe[1:3]) if len(righe) > 2 else " ".join(righe)
                risultati.append({
                    "numero_bu": int(num), "data_bu": data, "ente": ente, "pagina": url,
                    "oggetto": titolo[:400],
                    "tipo_auto": C.estrai_tipo(avv), "posteggi_auto": C.estrai_numero(avv),
                    "scadenza_auto": C.estrai_scadenza(avv), "testo": C.normalizza(avv[:3000]),
                })
        log.append({"numero": int(num), "data": data, "url": url, "http": st, "avvisi": trovati})
        print(num, data, st, trovati, flush=True)
    with open(uscita, "w", encoding="utf-8") as f:
        json.dump({"fonte": "BUR Lazio - Sintesi URP", "anno": anno, "verificato_il": time.strftime("%Y-%m-%d"),
                   "secondi": round(time.time() - t0), "pagine": log, "avvisi": risultati},
                  f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
