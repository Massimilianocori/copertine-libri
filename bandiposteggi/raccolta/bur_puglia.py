"""Raccolta degli avvisi sui posteggi dal BURP (Bollettino Ufficiale della Regione Puglia).

Fonte (verificata il 9/10/2026): portale Liferay burp.regione.puglia.it
  elenco numeri dell'anno: /bollettini?...SearchPortlet_bolanno=<anno>&..._cur=<p>&..._delta=60
  dettaglio numero:       /bollettini?...mvcRenderCommandName=/view-burp/bollettino/detail&..._burpId=<id>
  ogni atto nel dettaglio: <div class="doc-element"> con titolo (h2), oggetto (div.blocco), PDF dell'atto.

Uso:
  python3 -I bur_puglia.py <cartella_download> <file_json_uscita> [anno]
"""
import html
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune as C  # noqa: E402

P = "it_indra_regione_puglia_burp_web_SearchPortlet"
ELENCO = ("https://burp.regione.puglia.it/bollettini?p_p_id=" + P + "&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view"
          "&_" + P + "_bolanno={anno}&_" + P + "_cur={p}&_" + P + "_resetCur=false&_" + P + "_delta=60")
DETTAGLIO = ("https://burp.regione.puglia.it/bollettini?p_p_id=" + P + "&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view"
             "&_" + P + "_mvcRenderCommandName=%2Fview-burp%2Fbollettino%2Fdetail&_" + P + "_currentURL=%2F&_" + P + "_burpId={id}")
RX_FORTE = re.compile(r"posteggi|posteggio|commercio su aree? pubblic|ambulant|chiosc|edicol|spunt|\bfiera\b|mercato settimanale", re.I)


def pulisci(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def main():
    cartella, uscita = sys.argv[1], sys.argv[2]
    anno = sys.argv[3] if len(sys.argv) > 3 else "2026"
    t0 = time.time()
    numeri = {}
    for p in range(1, 6):
        st, _, dati = C.scarica(ELENCO.format(anno=anno, p=p))
        s = dati.decode("utf-8", "replace")
        # ogni voce: "Bollettino Ufficiale della Regione Puglia n° 80/2026 ..." vicino al link burpId
        nuovi = 0
        # ogni scheda: titolo "... n° 80/2026 [Supplemento 1]", data pubblicazione, poi il link con burpId
        for scheda in s.split('class="card card-burp')[1:]:
            t = re.search(r"n° (\d+)/(\d{4})( Supplemento \d+)?", pulisci(scheda[:1500]))
            d = re.search(r'class="data-news"\s*>([^<]+)<', scheda)
            b = re.search(r"burpId=(\d+)", scheda)
            if t and b and t.group(2) == anno and b.group(1) not in numeri:
                numeri[b.group(1)] = {"numero": t.group(1) + (t.group(3) or ""), "data": d.group(1).strip() if d else None}
                nuovi += 1
        print("elenco", p, st, nuovi, flush=True)
        if nuovi == 0:
            break
    risultati, log = [], []
    for bid, info in sorted(numeri.items()):
        url = DETTAGLIO.format(id=bid)
        st, _, dati = C.scarica(url, os.path.join(cartella, f"burp-{bid}.htm"))
        s = dati.decode("utf-8", "replace")
        atti = s.split('<div class="doc-element">')[1:]
        trovati = 0
        for a in atti:
            titolo = pulisci((re.search(r"<h2>(.*?)</h2>", a, re.S) or [None, ""])[1])
            ogg = pulisci((re.search(r'class="col-md-12 blocco">(.*?)</div>', a, re.S) or [None, ""])[1])
            pdf = re.search(r'href="(https://burp\.regione\.puglia\.it/documents/[^"]+?\.pdf[^"]*)"', a)
            if not RX_FORTE.search(titolo + " " + ogg) or C.ESCLUDI.search(titolo + " " + ogg):
                continue
            trovati += 1
            risultati.append({"burpId": bid, "numero_bu": info["numero"], "data_bu": info["data"], "ente": titolo,
                              "oggetto": ogg[:600], "pagina": url, "pdf": html.unescape(pdf.group(1)) if pdf else None})
        log.append({"burpId": bid, **info, "http": st, "atti": len(atti), "candidati": trovati})
        print(bid, info, st, len(atti), trovati, flush=True)
    with open(uscita, "w", encoding="utf-8") as f:
        json.dump({"fonte": "BURP Puglia", "anno": anno, "verificato_il": time.strftime("%Y-%m-%d"),
                   "secondi": round(time.time() - t0), "numeri": log, "candidati": risultati}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
