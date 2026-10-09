"""Raccolta degli avvisi sui posteggi dal Bollettino Ufficiale della Regione Piemonte.

Struttura della fonte (verificata il 9/10/2026):
  https://www.regione.piemonte.it/governo/bollettino/abbonati/<anno>/<nn, due cifre>/annunci/index.htm  (anche appalti/ e concorsi/)
    -> elenco HTML (ente nel title del link, oggetto nel <P> successivo)
    -> pagina di dettaglio 000000NN.htm -> link "Testo del documento" ../attach/<file>.pdf

Uso:
  python3 -I bur_piemonte.py <cartella_download> <file_json_uscita> [primo_numero] [ultimo_numero]

Passi: 1) scarica gli indici "annunci" e "appalti" dei numeri richiesti; 2) filtra gli annunci
per parole chiave; 3) per ogni annuncio candidato scarica il dettaglio e il PDF; 4) estrae
testo e campi con le euristiche di comune.py. Il JSON contiene anche i candidati scartati
con il motivo, per poter misurare il filtro.
"""
import html
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune as C  # noqa: E402

BASE = "https://www.regione.piemonte.it/governo/bollettino/abbonati/{anno}/{n:02d}/{sez}/"
PROVINCE = {"Alessandria": "AL", "Asti": "AT", "Biella": "BI", "Cuneo": "CN", "Novara": "NO",
            "Torino": "TO", "Verbano Cusio Ossola": "VB", "Vercelli": "VC", "Verbania": "VB"}
RX_VOCE = re.compile(r'<A\s+href="(\d+\.htm)"\s+title="([^"]*)">.*?</A>\s*<P>(.*?)</P>', re.S | re.I)
RX_DATA_BU = re.compile(r"n\.\s*\d+\s+del\s+(\d{1,2})\s+(\w+)\s+(\d{4})", re.I)
# oggetti certamente relativi ad aree pubbliche (il filtro largo di comune.py prende anche "mercato")
RX_FORTE = re.compile(r"posteggi|posteggio|aree pubbliche|area pubblica|ambulant|chiosc|edicol|spunt|"
                      r"fiera|fiere|sagr|mercatin|mercato settimanale|mercato (?:comunale|cittadino|rionale)", re.I)


def indice(anno, n, sez, cartella):
    url = BASE.format(anno=anno, n=n, sez=sez) + "index.htm"
    dest = os.path.join(cartella, f"{anno}-{n:02d}-{sez}.htm")
    st, ct, dati = C.scarica(url, dest)
    testo = dati.decode("latin-1", "replace")
    m = RX_DATA_BU.search(testo)
    data_bu = None
    if m and m.group(2).lower() in C.MESI:
        data_bu = f"{m.group(3)}-{C.MESI[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"
    voci = []
    for href, ente, ogg in RX_VOCE.findall(testo):
        ogg = html.unescape(re.sub(r"<[^>]+>", " ", ogg)).strip()
        voci.append({"href": href, "ente": html.unescape(ente).strip(), "oggetto": re.sub(r"\s+", " ", ogg)})
    return url, st, data_bu, voci


def comune_e_provincia(ente):
    m = re.match(r"\s*Comune di\s+(.+?)\s*(?:\((.+?)\))?\s*$", ente, re.I)
    if not m:
        return None, None
    nome = m.group(1).strip().title().replace("D'", "d'").replace(" Di ", " di ")
    prov = PROVINCE.get((m.group(2) or "").strip().title()) if m.group(2) else None
    if nome.lower() == "torino":
        prov = "TO"
    return nome, prov


def main():
    cartella, uscita = sys.argv[1], sys.argv[2]
    primo = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    ultimo = int(sys.argv[4]) if len(sys.argv) > 4 else 40
    anno = 2026
    t0 = time.time()
    risultati, log = [], []
    for n in range(primo, ultimo + 1):
        for sez in ("annunci", "appalti", "concorsi"):
            url, st, data_bu, voci = indice(anno, n, sez, cartella)
            cand = [v for v in voci if C.PAROLE_CHIAVE.search(v["oggetto"]) and not C.ESCLUDI.search(v["oggetto"])]
            log.append({"numero": n, "sezione": sez, "url": url, "http": st, "data_bu": data_bu,
                        "voci": len(voci), "candidati": len(cand)})
            print(n, sez, st, data_bu, len(voci), len(cand), flush=True)
            for v in cand:
                det_url = BASE.format(anno=anno, n=n, sez=sez) + v["href"]
                _, _, det = C.scarica(det_url)
                m = re.search(r'href="(\.\./attach/[^"]+\.pdf)"', det.decode("latin-1", "replace"), re.I)
                pdf_url = (BASE.format(anno=anno, n=n, sez=sez) + m.group(1)).replace(f"/{sez}/../", "/") if m else None
                testo = ""
                if pdf_url:
                    loc = os.path.join(cartella, "pdf", f"{n:02d}-{sez}-{v['href'].replace('.htm', '')}.pdf")
                    st_pdf, _, _ = C.scarica(pdf_url, loc)
                    testo = C.testo_pdf(loc) if st_pdf == 200 else ""
                nome, prov = comune_e_provincia(v["ente"])
                pertinente = bool(RX_FORTE.search(v["oggetto"]) or RX_FORTE.search(testo[:1500]))
                risultati.append({
                    "numero_bu": n, "sezione": sez, "data_bu": data_bu, "ente": v["ente"],
                    "comune": nome, "provincia": prov, "regione": "Piemonte",
                    "oggetto": v["oggetto"], "pagina": det_url, "pdf": pdf_url,
                    "pertinente_auto": pertinente,
                    "tipo_auto": C.estrai_tipo(v["oggetto"] + "\n" + testo),
                    "posteggi_auto": C.estrai_numero(v["oggetto"] + "\n" + testo),
                    "scadenza_auto": C.estrai_scadenza(testo),
                    "caratteri_testo": len(testo),
                    "testo_inizio": C.normalizza(testo[:600]),
                })
    with open(uscita, "w", encoding="utf-8") as f:
        json.dump({"fonte": "BUR Piemonte", "anno": anno, "verificato_il": time.strftime("%Y-%m-%d"),
                   "secondi": round(time.time() - t0), "indici": log, "candidati": risultati},
                  f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
