"""Bagaglio da stiva per compagnia (riquadro «Checked bags and fees» nelle pagine cabin-bags/<compagnia>/ di Before You Fly).

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/stiva.py            ricontrollo: riapre le pagine ufficiali e cerca ogni frase citata
    python3 -I beforeyoufly/raccolta/stiva.py --domanda  misura i volumi di ricerca e riscrive dati/stiva_domanda.json

Ricontrollo. Per ogni compagnia di dati/stiva.json apre le pagine ufficiali con Chromium headless (stesso metodo di raccolta/bagagli.py:
Playwright in /opt, proxy da HTTPS_PROXY, user agent di un browser desktop, HTTP/2 spento, una pagina alla volta con una pausa, al massimo
due caricamenti per pagina) e controlla che ogni frase citata sia ancora sulla pagina, parola per parola (spazi normalizzati). Il testo
letto è salvato in raccolta/.cache/stiva/ (fuori dal repository): verifica.py, punto 38, ricontrolla le frasi su quelle copie.
Non modifica i dati: se una frase sparisce scrive [CAMBIATA?] o [DA CONTROLLARE A MANO] ed esce con 1; allora si apre la pagina, la si
rilegge e si aggiorna dati/stiva.json a mano (frasi, numeri, controllato_il). Nessun blocco anti-robot o geografico viene aggirato: una
pagina che non si legge resta non letta e la compagnia esce dal riquadro (voce "escluse").

Domanda. Volumi medi mensili di Google Ads da api.seodata.dev /v1/keyword. La chiave sta in /root/.config/seodata/key e viene letta SOLO
dentro la shell di curl ($(cat ...)): non passa da Python, non viene stampata né scritta.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
CACHE = RADICE / "raccolta" / ".cache" / "stiva"
DATI = RADICE / "dati" / "stiva.json"
DOMANDA = RADICE / "dati" / "stiva_domanda.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
JS = r"""
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const fs = require('fs');
(async () => { const pr = process.env.HTTPS_PROXY || process.env.https_proxy;
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', proxy: pr ? { server: pr } : undefined, args: ['--disable-http2'] });
  const ctx = await b.newContext({ locale: 'en-GB', viewport: { width: 1366, height: 900 }, userAgent: process.argv[3] });
  const urls = JSON.parse(fs.readFileSync(process.argv[2], 'utf8')); const out = {};
  for (const u of urls) { const p = await ctx.newPage(); out[u] = [0, ''];
    for (let t = 0; t < 2; t++) {
      try { const r = await p.goto(u, { waitUntil: 'domcontentloaded', timeout: 90000 }); await p.waitForTimeout(7000 + 4000 * t);
        await p.evaluate(() => document.querySelectorAll('details').forEach(d => d.open = true));
        const vis = await p.evaluate(() => document.body ? document.body.innerText : '');
        const tc = await p.evaluate(() => { const c = document.body.cloneNode(true); c.querySelectorAll('script,style,noscript').forEach(x => x.remove()); return c.textContent; });
        out[u] = [r ? r.status() : 0, vis + '\n' + tc]; } catch (e) { out[u] = [0, '']; }
      if (out[u][1].length > 1500) break; }
    await p.close(); await new Promise(r => setTimeout(r, 2000)); }
  await b.close(); fs.writeFileSync(process.argv[4], JSON.stringify(out)); })();
"""

# Frasi misurate: {n} = nome come lo si cerca (campo "cerca" di dati/stiva.json), Paese = mercato della compagnia
MODELLI = ["{n} baggage fees", "{n} checked bag", "{n} checked bag fee", "{n} checked baggage", "{n} baggage allowance", "{n} bag fees",
           "{n} checked bag size", "{n} checked bag weight limit", "{n} baggage policy"]
MODELLI_GB = ["{n} hold luggage", "{n} hold luggage size", "{n} luggage allowance", "{n} 23kg bag"]
# Compagnie della riga 3 del piano senza riquadro (pagina ufficiale non letta): misurate lo stesso, per sapere cosa resta fuori
SENZA_RIQUADRO = [("alaska-airlines", "alaska airlines", "us"), ("spirit", "spirit", "us")]


def norm(s):
    return re.sub(r"\s+", " ", s.replace("\xa0", " ").replace("​", "")).strip()


def nome_file(u):
    return re.sub(r"[^a-zA-Z0-9]+", "_", re.sub(r"^https?://", "", u))[:120] + ".txt"


def citazioni(C):
    """Tutte le citazioni di una compagnia: [{"f": chiave della fonte, "righe": [...]}, ...]."""
    out = []
    for v in C["voci"]:
        out += v["cit"]
    for t in C.get("tariffe", []):
        out += t["cit"]
    return out


def leggi_pagine(urls):
    with tempfile.TemporaryDirectory() as tmp:
        lista, uscita, script = Path(tmp) / "urls.json", Path(tmp) / "out.json", Path(tmp) / "leggi.js"
        lista.write_text(json.dumps(urls))
        script.write_text(JS)
        try:
            subprocess.run(["node", str(script), str(lista), UA, str(uscita)], timeout=150 * len(urls) + 120, check=False)
            return json.loads(uscita.read_text()) if uscita.exists() else {}
        except subprocess.TimeoutExpired:
            return {}


def ricontrollo():
    d = json.loads(DATI.read_text(encoding="utf-8"))
    voci = []
    for C in d["compagnie"]:
        for k, f in C["fonti"].items():
            voci.append((f"{C['slug']} ({k})", f["url"], sorted({norm(" ".join(c["righe"])) for c in citazioni(C) if c["f"] == k})))
    urls = sorted({u for _, u, _ in voci})
    CACHE.mkdir(parents=True, exist_ok=True)
    letti = leggi_pagine(urls)
    problemi = 0
    for etichetta, u, frasi in voci:
        s, t = letti.get(u, [0, ""])
        tn = norm(t)
        mancano = [q for q in frasi if q not in tn]
        if len(tn) < 500 or (s >= 400 and len(mancano) == len(frasi)):
            print(f"[DA CONTROLLARE A MANO] {etichetta}: pagina non leggibile o bloccata (HTTP {s}); rilanciare più tardi – {u}")
            problemi += 1
            continue  # la copia buona precedente NON viene sovrascritta da una pagina vuota o di blocco
        (CACHE / nome_file(u)).write_text(f"STATUS {s}\nURL {u}\n\n{t}", encoding="utf-8")
        if mancano:
            print(f"[CAMBIATA?] {etichetta}: {len(mancano)} frasi su {len(frasi)} non trovate – {u}")
            for q in mancano:
                print("     -", q[:140])
            problemi += 1
        else:
            print(f"[OK] {etichetta}: {len(frasi)} frasi presenti")
    print(f"\n{len(voci) - problemi} pagine invariate su {len(voci)}; {problemi} da controllare. Testi in {CACHE}")
    sys.exit(1 if problemi else 0)


def domanda():
    d = json.loads(DATI.read_text(encoding="utf-8")) if DATI.exists() else {"compagnie": []}
    elenco = [(C["slug"], C["cerca"], C["paese_domanda"]) for C in d["compagnie"]] + SENZA_RIQUADRO
    oggi = time.strftime("%Y-%m-%d")
    out = {"_nota": "Volumi di ricerca misurati per il bagaglio da stiva (riquadro «Checked bags and fees» nelle pagine cabin-bags/<compagnia>/). "
                    "Volume = media mensile di Google Ads nel Paese indicato; uno 0 vuol dire sotto le ~10 ricerche al mese. Le frasi nei titoli "
                    "e nelle descrizioni (genera.py, frase_stiva) devono essere qui con volume > 0. Riscritto da raccolta/stiva.py --domanda.",
           "fonte": "api.seodata.dev /v1/keyword (volume medio mensile Google Ads)", "misurato_il": oggi, "richieste": 0, "compagnie": {}}
    for slug, nome, paese in elenco:
        frasi = {}
        for m in MODELLI + (MODELLI_GB if paese == "gb" else []):
            x = m.format(n=nome)
            url = "https://api.seodata.dev/v1/keyword?q=" + urllib.parse.quote(x) + "&country=" + paese
            r = subprocess.run(["bash", "-c", 'curl -s -w "\\n%{http_code}" "$U" -H "Authorization: Bearer $(cat /root/.config/seodata/key)"'],
                               env={**os.environ, "U": url}, capture_output=True, text=True, timeout=60)
            corpo, _, codice = r.stdout.rpartition("\n")
            out["richieste"] += 1
            try:
                j = json.loads(corpo)
            except ValueError:
                j = {}
            if codice == "200" and "volume" in j:
                frasi[x] = {"volume": j.get("volume"), "cpc": j.get("cpc"),
                            "simili": [[s["keyword"], s["volume"]] for s in j.get("similar", [])]}
            else:
                frasi[x] = {"errore": int(codice) if codice.isdigit() else codice}
            time.sleep(0.3)
        out["compagnie"][slug] = {"cerca": nome, "paese": paese, "frasi": frasi}
        print(slug, {k: v.get("volume", v.get("errore")) for k, v in frasi.items()})
    DOMANDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("richieste:", out["richieste"])


if __name__ == "__main__":
    domanda() if "--domanda" in sys.argv else ricontrollo()
