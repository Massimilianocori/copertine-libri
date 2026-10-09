"""Ricerca degli avvisi sui posteggi nei Bollettini regionali che offrono un motore di ricerca
(o un'API) invece di un indice da scorrere numero per numero.

Fonti (verificate il 9/10/2026):
  - Emilia-Romagna (BURERT): POST https://bur.regione.emilia-romagna.it/risultati
      campi: key=<parole>, dal/al=gg/mm/aaaa, titolo=1 (ricerca nel titolo) oppure testo=1 (nel testo)
  - Lombardia (BURL): PUT https://www.consultazioniburl.servizirl.it/ConsultazioneBurl/api/ricercaAvanzata?offset=0&limit=100
      corpo JSON: {"oggetto": <parole>, "intervalloAnniPubblicazione": {"numeroMinimo": "2026", "numeroMassimo": "2026"}, ...}
  - Veneto (BURVET): POST ASP.NET https://bur.regione.veneto.it/BurvServices/pubblica/ricerca.aspx
      (si legge prima la pagina per __VIEWSTATE, poi paroleSuOggetto=<parole>, daData, aData, cercaSemplice)
  - Sardegna (BURAS): API Directus https://buras.regione.sardegna.it/api/items/inserzione?filter=<json>
  - Abruzzo (BURAT): ricerca Drupal https://bura.regione.abruzzo.it/search/node?keys=<parole>
  - Marche (BUR): solo PDF del numero intero https://bur.regione.marche.it/bur/PDF/<anno>/N<nn> del <data>.pdf
      (nessuna ricerca: si scarica un campione di numeri e si cerca nel testo)

Uso:
  python3 -I bur_altri.py <cartella_download> <file_json_uscita> [numeri_marche_da_campionare]

Il JSON riporta, per ogni fonte e parola chiave: HTTP status, numero di risultati e i risultati
pertinenti (titolo, data, link). Le pertinenze sono decise con l'espressione RX_FORTE: i risultati
vanno comunque riletti, perché i titoli dei BUR contengono spesso "aree pubbliche" in senso
demaniale (acque, derivazioni) o "mercato" in senso economico.
"""
import html
import http.cookiejar
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune as C  # noqa: E402

ANNO = "2026"
PAROLE = ["posteggi", "posteggio", "aree pubbliche", "ambulante", "spunta", "chioschi", "edicola", "fiera"]
RX_FORTE = re.compile(r"posteggi|posteggio|commercio su aree? pubblic|ambulant|chiosc|edicol|spuntist", re.I)
RX_NO = re.compile(r"acque|derivazion|demanial|idric|fotovolt|pozz", re.I)


def _testo(s):
    s = re.sub(r"<(script|style)[^>]*>.*?</(script|style)>", " ", s, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s)))


def _apri(opener, url, dati=None, metodo=None, json_body=None):
    """Richiesta con pausa e User-Agent di comune.py; restituisce (status, testo)."""
    attesa = C.PAUSA - (time.time() - C._ultimo[0])
    if attesa > 0:
        time.sleep(attesa)
    C._ultimo[0] = time.time()
    headers = {"User-Agent": C.UA}
    corpo = None
    if json_body is not None:
        corpo = json.dumps(json_body).encode()
        headers.update({"Content-Type": "application/json", "Accept": "application/json"})
    elif dati is not None:
        corpo = urllib.parse.urlencode(dati).encode()
    req = urllib.request.Request(url, data=corpo, headers=headers, method=metodo)
    try:
        with opener.open(req, timeout=90) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # timeout, reset
        return 0, str(e)


def emilia(op):
    out = []
    for p in PAROLE:
        for modo in ("titolo", "testo"):
            st, s = _apri(op, "https://bur.regione.emilia-romagna.it/risultati",
                          {"key": p, "dal": f"01/01/{ANNO}", "al": time.strftime("%d/%m/%Y"), modo: "1"})
            t = _testo(s)
            m = re.search(r"Trovat[oi] (\d+) document", t)
            voci = re.findall(r"(n\.\d+ del [\d.]+)[^A]*?\)(.*?)Anno (\d{4}) - Fascicolo (\d+)", t)
            pert = [{"numero": v[0], "titolo": v[1].strip()[:300]} for v in voci if RX_FORTE.search(v[1]) and not RX_NO.search(v[1])]
            out.append({"parola": p, "modo": modo, "http": st, "risultati": int(m.group(1)) if m else None, "pertinenti": pert})
    return out


def lombardia(op):
    url = "https://www.consultazioniburl.servizirl.it/ConsultazioneBurl/api/ricercaAvanzata?offset=0&limit=100"
    out = []
    for p in PAROLE + ["mercato"]:
        body = {"oggetto": p, "intervalloAnniPubblicazione": {"numeroMinimo": ANNO, "numeroMassimo": ANNO},
                "intervalloDateRichiestaPubblicazione": {"dataMinina": None, "dataMassima": None},
                "intervalloDateNumerazione": {"dataMinina": None, "dataMassima": None}}
        st, s = _apri(op, url, metodo="PUT", json_body=body)
        try:
            d = json.loads(s.replace("\\u0000", ""))
        except ValueError:
            d = {}
        lista = d.get("lista") or []
        pert = [{"data": x["dataPubblicazione"], "numero": x["numero"], "serie": x.get("serie"), "idBurl": x["idBurl"],
                 "titolo": x["titolo"].replace("\x00", "").strip()[:300]}
                for x in lista if RX_FORTE.search(x["titolo"]) and not RX_NO.search(x["titolo"])]
        out.append({"parola": p, "http": st, "risultati": d.get("conteggioTotale"), "pertinenti": pert})
    return out


def veneto(op):
    url = "https://bur.regione.veneto.it/BurvServices/pubblica/ricerca.aspx"
    out = []
    for p in PAROLE:
        st0, s = _apri(op, url)
        nascosti = dict(re.findall(r'<input type="hidden" name="([^"]+)" id="[^"]*" value="([^"]*)"', s))
        dati = dict(nascosti)
        dati.update({"paroleSuOggetto": p, "paroleSuTesto": "", "daData": f"01/01/{ANNO}",
                     "aData": time.strftime("%d/%m/%Y"), "cercaSemplice": "Cerca >", "js": "n"})
        st, s = _apri(op, url, dati)
        t = _testo(s)
        inizi = [m.start() for m in re.finditer(r"[A-Z][A-Z0-9 /'.-]{5,}?\(BUR n\. \d+S? del [\d/]+\)", t)]
        fine_lista = t.find(" Pagina di", inizi[-1]) if inizi else -1
        confini = inizi + [fine_lista if fine_lista > 0 else len(t)]
        voci = [t[a:min(b, a + 450)] for a, b in zip(confini, confini[1:])]
        nessuno = "Nessun atto trovato" in t
        pert = [v.strip() for v in voci if RX_FORTE.search(v) and not RX_NO.search(v)]
        out.append({"parola": p, "http": st, "risultati": 0 if nessuno else len(voci), "pertinenti": pert,
                    "nota": "la pagina dei risultati è paginata: si legge solo la prima pagina"})
    return out


def sardegna(op):
    out = []
    for p in PAROLE:
        filtro = {"_and": [{"subject": {"_icontains": p}}, {"actDate": {"_gte": f"{ANNO}-01-01"}}]}
        url = ("https://buras.regione.sardegna.it/api/items/inserzione?fields=id,publishedAt,type,actDate,subject,author"
               "&limit=200&filter=" + urllib.parse.quote(json.dumps(filtro)))
        st, s = _apri(op, url)
        try:
            d = json.loads(s).get("data", [])
        except ValueError:
            d = []
        pert = [{"id": x["id"], "data_atto": (x.get("actDate") or "")[:10], "autore": x.get("author"), "titolo": x["subject"][:300]}
                for x in d if RX_FORTE.search(x["subject"]) and not RX_NO.search(x["subject"])]
        out.append({"parola": p, "http": st, "risultati": len(d), "pertinenti": pert})
    return out


def abruzzo(op):
    out = []
    for p in PAROLE:
        st, s = _apri(op, "https://bura.regione.abruzzo.it/search/node?keys=" + urllib.parse.quote(p))
        voci = []
        for m in re.finditer(r'<h3[^>]*>\s*<a href="([^"]+)"[^>]*>(.*?)</a>(.*?)</li>', s, re.S):
            voci.append({"link": "https:" + m.group(1) if m.group(1).startswith("//") else m.group(1),
                         "titolo": _testo(m.group(2) + " | " + m.group(3))[:300]})
        pert = [v for v in voci if re.search(r"-" + ANNO + r"-", v["link"]) and RX_FORTE.search(v["titolo"]) and not RX_NO.search(v["titolo"])]
        out.append({"parola": p, "http": st, "risultati": len(voci), "risultati_anno": sum(1 for v in voci if "-" + ANNO + "-" in v["link"]),
                    "pertinenti": pert})
    return out


def marche(op, cartella, quanti):
    st, s = _apri(op, "https://www.regione.marche.it/Entra-in-Regione/BUR/Ricerca-BUR")
    pdf = re.findall(r'href="(https://bur\.regione\.marche\.it/bur/PDF/' + ANNO + r'/[^"]+\.pdf)"', s)[:quanti]
    out = []
    for u in pdf:
        loc = os.path.join(cartella, "marche", urllib.parse.unquote(u.rsplit("/", 1)[1]))
        sp, ct, _ = C.scarica(u, loc) if not os.path.exists(loc) else (200, "cache", b"")
        testo = C.testo_pdf(loc, max_pagine=400) if sp == 200 else ""
        frasi = sorted(set(m.group(0) for m in re.finditer(r"[^\n]{0,120}(?:posteggi|commercio su aree pubbliche)[^\n]{0,120}", testo, re.I)))
        out.append({"pdf": u, "http": sp, "caratteri": len(testo), "occorrenze": frasi[:10]})
    return {"http_indice": st, "numeri_letti": out}


def main():
    cartella, uscita = sys.argv[1], sys.argv[2]
    quanti_marche = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    os.makedirs(cartella, exist_ok=True)
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    t0 = time.time()
    ris = {}
    for nome, f in (("Emilia-Romagna", emilia), ("Lombardia", lombardia), ("Veneto", veneto),
                    ("Sardegna", sardegna), ("Abruzzo", abruzzo)):
        ris[nome] = f(op)
        print(nome, [(x["parola"], x.get("modo", ""), x["http"], x["risultati"], len(x["pertinenti"])) for x in ris[nome]], flush=True)
    ris["Marche"] = marche(op, cartella, quanti_marche)
    print("Marche", [(x["pdf"][-30:], x["http"], len(x["occorrenze"])) for x in ris["Marche"]["numeri_letti"]], flush=True)
    with open(uscita, "w", encoding="utf-8") as fo:
        json.dump({"descrizione": "Ricerche per parola chiave nei BUR con motore di ricerca/API, anno " + ANNO,
                   "verificato_il": time.strftime("%Y-%m-%d"), "secondi": round(time.time() - t0), "fonti": ris},
                  fo, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
