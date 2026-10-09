"""Raccolta degli avvisi sui posteggi dal BURT (Bollettino Ufficiale della Regione Toscana), Parte III
(avvisi di Comuni ed enti).

Fonte (verificata il 9/10/2026):
  indice: https://www.regione.toscana.it/burt/consultazione  -> link /documents/d/guest/parte-iii-n-<n>-del-<gg-mm-aaaa>
  ogni link scarica il PDF dell'intera Parte III del numero (da 30 a 400 pagine).

Uso:
  python3 -I bur_toscana.py <cartella_download> <file_json_uscita> [anno]

Metodo (seconda versione, 9/10/2026): la prima versione divideva tutto il testo del PDF sulle
intestazioni "COMUNE DI ..." e perdeva avvisi (13 trovati su 16). Ora:
  1) si leggono solo le prime 4 pagine di ogni PDF, che contengono il SOMMARIO
     ("COMUNE DI X (Prov) ... TITOLO ... pagina");
  2) si tengono le voci con parole chiave sui posteggi;
  3) per ogni voce si leggono 4 pagine a partire da quella indicata nel sommario e si estraggono
     tipo, numero posteggi e scadenza con le euristiche di comune.py.
I PDF già scaricati non vengono riscaricati.
"""
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune as C  # noqa: E402

INDICE = "https://www.regione.toscana.it/burt/consultazione"
BASE = "https://www.regione.toscana.it"
RX_FORTE = re.compile(r"posteg|commercio su aree? pubblic|commercio in area pubblica|ambulant|chiosc|edicol|spuntist|\bfiera\b", re.I)
RX_NO = re.compile(r"noleggio con conducente|\bNCC\b|errata corrige|rettifica", re.I)
RX_VOCE = re.compile(r"(?:COMUNE|UNIONE DEI COMUNI|UNIONE MONTANA|CITTÀ METROPOLITANA) D[IE'][^…]{2,60}?…\s*(.*?)\s*…\s*(\d{1,3})\b", re.S)


def pagine(percorso, da, a):
    import pdfplumber
    try:
        with pdfplumber.open(percorso) as pdf:
            n = len(pdf.pages)
            return "\n".join((pdf.pages[i].extract_text() or "") for i in range(max(0, da), min(n, a))), n
    except Exception:
        return "", 0


def voci_sommario(testo):
    t = re.sub(r"(?:\. ?){3,}", " … ", testo)
    t = re.sub(r"-\n", "", t).replace("\n", " ")
    out = []
    for blocco in re.split(r"(?=(?:COMUNE|UNIONE DEI COMUNI|UNIONE MONTANA|CITTÀ METROPOLITANA) D[IE'])", t):
        m = re.match(r"((?:COMUNE|UNIONE DEI COMUNI|UNIONE MONTANA|CITTÀ METROPOLITANA) D[IE']\s*[^…]{2,60}?)\s*…", blocco)
        if not m:
            continue
        ente = m.group(1).strip()
        # un ente può avere più atti: "TITOLO … pag TITOLO … pag"
        for tit, pag in re.findall(r"([^…]{15,400}?)\s*…\s*(\d{1,3})\b", blocco[m.end():]):
            tit = tit.strip()
            if re.match(r"^(?:[A-Z ]{3,}S\.P\.A|AZIENDA|ESTAR|CONSIGLIO|CONTRIBUTI|SVILUPPO)", tit):
                break
            out.append({"ente": ente, "titolo": tit, "pagina": int(pag)})
    return out


def comune_provincia(ente):
    m = re.match(r"COMUNE D[IE']\s*(.+?)(?:\s*\((.+?)\))?\s*$", ente)
    if not m:
        return ente, None
    return m.group(1).strip().title().replace(" Di ", " di ").replace(" Del ", " del ").replace(" A ", " a "), m.group(2)


def main():
    cartella, uscita = sys.argv[1], sys.argv[2]
    anno = sys.argv[3] if len(sys.argv) > 3 else "2026"
    t0 = time.time()
    st, _, dati = C.scarica(INDICE)
    link = sorted(set(re.findall(r'href="(/documents/d/guest/parte-iii-n-[^"]*?-' + anno + r'[^"]*)"', dati.decode("utf-8", "replace"))))
    print("indice", st, "parti III", len(link), flush=True)
    risultati, log = [], []
    for l in link:
        nome = l.rsplit("/", 1)[1]
        loc = os.path.join(cartella, nome + ".pdf")
        sp = 200
        if not os.path.exists(loc):
            sp, _, _ = C.scarica(BASE + l, loc)
        m = re.search(r"n-(\d+(?:-?bis)?)-del-(\d{2})-(\d{2})-(\d{4})", nome)
        data = f"{m.group(4)}-{m.group(3)}-{m.group(2)}" if m else None
        somm, n_pag = pagine(loc, 0, 4) if sp == 200 else ("", 0)
        voci = voci_sommario(somm)
        trovati = 0
        for v in voci:
            if not RX_FORTE.search(v["titolo"]) or RX_NO.search(v["titolo"]):
                continue
            trovati += 1
            corpo, _ = pagine(loc, v["pagina"] - 1, v["pagina"] + 3)
            # il corpo parte dal titolo dell'atto, se lo si ritrova
            chiave = re.sub(r"\W+", "", v["titolo"][:30]).lower()
            piatto = re.sub(r"\W+", "", corpo).lower()
            comune, prov = comune_provincia(v["ente"])
            risultati.append({
                "parte_iii": m.group(1) if m else nome, "data_bu": data, "ente": v["ente"], "comune": comune,
                "provincia_nome": prov, "oggetto": v["titolo"][:400], "pagina_bu": v["pagina"], "pdf": BASE + l,
                "titolo_ritrovato_nel_testo": chiave in piatto,
                "tipo_auto": C.estrai_tipo(v["titolo"] + "\n" + corpo),
                "posteggi_auto": C.estrai_numero(v["titolo"] + "\n" + corpo[:5000]),
                "scadenza_auto": C.estrai_scadenza(corpo[:8000]),
                "testo": C.normalizza(corpo[:3000]),
            })
        log.append({"parte_iii": nome, "url": BASE + l, "http": sp, "pagine_pdf": n_pag, "voci_sommario": len(voci), "avvisi": trovati})
        print(nome, sp, n_pag, len(voci), trovati, flush=True)
    with open(uscita, "w", encoding="utf-8") as f:
        json.dump({"fonte": "BURT Toscana - Parte III (dal sommario)", "anno": anno, "verificato_il": time.strftime("%Y-%m-%d"),
                   "secondi": round(time.time() - t0), "numeri": log, "avvisi": risultati}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
