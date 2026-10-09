"""Raccolta degli avvisi sui posteggi dal BURP (Bollettino Ufficiale della Regione Puglia).

Fonte (verificata il 9/10/2026): portale Liferay burp.regione.puglia.it
  elenco numeri dell'anno: /bollettini?...SearchPortlet_bolanno=<anno>&..._cur=<p>&..._delta=60
  dettaglio numero:       /bollettini?...mvcRenderCommandName=/view-burp/bollettino/detail&..._burpId=<id>
  ogni atto nel dettaglio: <div class="doc-element"> con titolo (h2), oggetto (div.blocco), PDF dell'atto.

Uso:
  python3 -I bur_puglia.py <cartella_download> <file_json_uscita> [anno]

Particolarità pugliese (L.R. 24/2015, art. 30): i Comuni inviano i bandi per i posteggi liberi alla
Regione entro il 30 aprile e il 30 settembre e la Regione li pubblica tutti insieme nel BURP in un
unico atto ("Bandi Comunali per la copertura dei Posteggi Liberi ... Prima/Seconda sessione").
Lo script scarica quel PDF e lo divide nei singoli bandi (cambio dell'intestazione "COMUNE DI" /
"CITTÀ DI"). Le scadenze sono quasi sempre relative ("entro 60 giorni dalla pubblicazione sul
BURP"): si calcolano con comune.scadenza_da_relativa().
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
# niente "fiera": a Bari la "Fiera del Levante" compare in decine di atti estranei (indirizzi, padiglioni)
RX_FORTE = re.compile(r"posteggi|posteggio|commercio su aree? pubblic|ambulant|chiosc|edicol|spunt|mercato settimanale", re.I)
RX_ENTE = re.compile(r"^\s*(?:COMUNE|CITTÀ|CITTA') D[IE']\s*([A-ZÀ-Ü' ]{3,40})\s*$", re.M)
MESI_IT = {m: i for i, m in enumerate(["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
                                       "settembre", "ottobre", "novembre", "dicembre"], 1)}


def data_iso(d):
    m = re.match(r"(\d{1,2}) (\w+) (\d{4})", d or "")
    return f"{m.group(3)}-{MESI_IT[m.group(2).lower()]:02d}-{int(m.group(1)):02d}" if m and m.group(2).lower() in MESI_IT else None


def dividi_raccolta(testo):
    """Divide l'atto regionale che raccoglie più bandi comunali: un pezzo per ogni cambio di Comune."""
    pezzi, corrente, inizio = [], None, 0
    for m in RX_ENTE.finditer(testo):
        nome = m.group(1).strip()
        if nome != corrente:
            if corrente:
                pezzi.append((corrente, testo[inizio:m.start()]))
            corrente, inizio = nome, m.start()
    if corrente:
        pezzi.append((corrente, testo[inizio:]))
    return pezzi


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
        loc_html = os.path.join(cartella, f"burp-{bid}.htm")
        if os.path.exists(loc_html):  # cache: i numeri pubblicati non cambiano
            st, dati = 200, open(loc_html, "rb").read()
        else:
            st, _, dati = C.scarica(url, loc_html)
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
            pdf_url = html.unescape(pdf.group(1)) if pdf else None
            testo = ""
            if pdf_url:
                loc = os.path.join(cartella, "pdf", f"{bid}-{trovati}.pdf")
                sp, _, _ = C.scarica(pdf_url, loc) if not os.path.exists(loc) else (200, "", b"")
                testo = C.testo_pdf(loc, max_pagine=80) if sp == 200 else ""
            dbu = data_iso(info["data"])
            pezzi = dividi_raccolta(testo) if re.search(r"Bandi Comunali", ogg, re.I) else [(None, testo)]
            for ente_c, t in pezzi:
                risultati.append({"burpId": bid, "numero_bu": info["numero"], "data_bu": dbu, "ente": titolo,
                                  "comune": ente_c.title() if ente_c else None, "da_raccolta_regionale": ente_c is not None,
                                  "oggetto": ogg[:600], "pagina": url, "pdf": pdf_url,
                                  "tipo_auto": C.estrai_tipo(ogg + "\n" + t), "posteggi_auto": C.estrai_numero(t[:6000] or ogg),
                                  "scadenza_auto": C.estrai_scadenza(t[:15000]) or C.scadenza_da_relativa(t, dbu),
                                  "scadenza_relativa_giorni": C.estrai_termine_relativo(t),
                                  "testo": C.normalizza(t[:3000])})
        log.append({"burpId": bid, **info, "http": st, "atti": len(atti), "candidati": trovati})
        print(bid, info, st, len(atti), trovati, flush=True)
    with open(uscita, "w", encoding="utf-8") as f:
        json.dump({"fonte": "BURP Puglia", "anno": anno, "verificato_il": time.strftime("%Y-%m-%d"),
                   "secondi": round(time.time() - t0), "numeri": log, "candidati": risultati}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
