"""Controllo di verità (soglia 4): elenco delle determine dalle pagine
"Amministrazione trasparente > Provvedimenti dirigenti" dei Comuni che usano la
piattaforma Maggioli JCityGov (<comune>.trasparenza-valutazione-merito.it).

La griglia degli atti è servita da Liferay: si apre la pagina (cookie di
sessione) e si sfoglia con POST all'azione "eseguiPaginazione"
(hidden_page_size=50, hidden_page_to=N). Il filtro per data della piattaforma
non risponde agli script, quindi si sfoglia dalla pagina 1 finché le date di
pubblicazione scendono sotto --da.

Da ogni riga si ricavano: tipo atto, anno/numero, oggetto, data di inizio
pubblicazione, ufficio proponente, link al dettaglio, e il CIG citato
nell'oggetto (se c'è). Non si scaricano allegati.

Uso:
    python3 -I atti_maggioli.py HOST --da 2026-07-01 --a 2026-08-31 --uscita atti.json
        [--griglia /web/trasparenza/papca-p/-/papca/igrid/NNN] [--max-pagine 60]
HOST è ad es. castelvetrano.trasparenza-valutazione-merito.it. Senza --griglia
la cerca nel menu ("Provvedimenti dirigenti").
"""
import argparse
import datetime as dt
import html
import json
import re
import subprocess
import tempfile
import time

UA = "Mozilla/5.0 (compatible; ChiLavoraColComune-test/0.1)"
P = "_jcitygovalbopubblicazioni_WAR_jcitygovalbiportlet"
RE_CIG = re.compile(r"C\.?\s?I\.?\s?G\.?\s*(?:N\.?|N°|NR\.?)?\s*[:.\-]?\s*([A-Z0-9]{10})", re.I)


def get(url, ck, data=None):
    cmd = ["curl", "-sSL", "--max-time", "60", "-A", UA, "-c", ck, "-b", ck]
    if data:
        cmd += ["--data", data]
    r = subprocess.run(cmd + [url], capture_output=True)
    time.sleep(1.5)
    return r.stdout.decode("utf-8", "replace")


def testo(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def trova_griglia(host, ck):
    for pagina in ("trasparenza", "menu-trasparenza"):
        t = get(f"https://{host}/web/trasparenza/{pagina}", ck)
        for res, url in re.findall(r'data-resource="([^"]*)"[^>]*data-mainurl="([^"]*)"', t):
            if "Provvedimenti dirigenti" in html.unescape(res) and "papca" in url:
                return url
    return None


def righe(pagina, host):
    out = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", pagina, flags=re.S):
        celle = [testo(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", r, flags=re.S)]
        if len(celle) < 5:
            continue
        m = re.search(r"(\d\d)/(\d\d)/(\d{4})", " ".join(celle[3:5]))
        if not m:
            continue
        link = re.findall(r'href="([^"]+/display/\d+[^"]*)"', r)
        ogg = celle[2]
        out.append({"tipo": celle[0], "numero": celle[1], "oggetto": ogg,
                    "data_pubblicazione": f"{m.group(3)}-{m.group(2)}-{m.group(1)}",
                    "proponente": celle[5] if len(celle) > 5 else "",
                    "cig": sorted({c.upper() for c in RE_CIG.findall(ogg)}),
                    "url": html.unescape(link[0]) if link else ""})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("host")
    ap.add_argument("--da", required=True)
    ap.add_argument("--a", required=True)
    ap.add_argument("--uscita", required=True)
    ap.add_argument("--griglia")
    ap.add_argument("--max-pagine", type=int, default=60)
    a = ap.parse_args()
    ck = tempfile.mktemp(suffix=".ck")
    griglia = a.griglia or trova_griglia(a.host, ck)
    if not griglia:
        raise SystemExit("griglia 'Provvedimenti dirigenti' non trovata")
    base = f"https://{a.host}{griglia}"
    get(base, ck)
    sezione = griglia.split("/-/")[0].rsplit("/", 1)[-1]  # papca-p o papca-g
    pag = (f"https://{a.host}/web/trasparenza/{sezione}?p_p_id=jcitygovalbopubblicazioni_WAR_jcitygovalbiportlet"
           f"&p_p_lifecycle=1&p_p_state=pop_up&p_p_mode=view&{P}_action=eseguiPaginazione")
    tutte, n_pag = [], 0
    for n in range(1, a.max_pagine + 1):
        rr = righe(get(pag, ck, f"hidden_page_size=50&hidden_page_to={n}"), a.host)
        n_pag = n
        if not rr:
            break
        tutte += rr
        if max(r["data_pubblicazione"] for r in rr) < a.da:
            break
    sel = [r for r in tutte if a.da <= r["data_pubblicazione"] <= a.a]
    out = {"host": a.host, "griglia": base, "pagine_lette": n_pag, "righe_lette": len(tutte),
           "periodo": [a.da, a.a], "atti_nel_periodo": len(sel),
           "atti_con_cig": sum(1 for r in sel if r["cig"]),
           "data_verifica": dt.date.today().isoformat(), "atti": sel}
    with open(a.uscita, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "atti"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
