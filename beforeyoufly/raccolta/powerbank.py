"""Power bank per compagnia (riquadro «Power banks» nelle pagine cabin-bags/<compagnia>/ e indice cabin-bags/power-banks/ di Before You Fly).

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/powerbank.py            ricontrollo: riapre le pagine ufficiali e cerca ogni frase citata
    python3 -I beforeyoufly/raccolta/powerbank.py --domanda  misura i volumi di ricerca e riscrive dati/powerbank_domanda.json

Ricontrollo. Per ogni compagnia di dati/powerbank.json apre le pagine ufficiali con Chromium headless (stesso metodo di raccolta/stiva.py e
raccolta/bagagli.py: Playwright in /opt, proxy da HTTPS_PROXY, user agent di un browser desktop, HTTP/2 spento, una pagina alla volta con
una pausa, al massimo due caricamenti per pagina) e controlla che ogni frase citata sia ancora sulla pagina, parola per parola (spazi
normalizzati). Il testo letto è salvato in raccolta/.cache/powerbank/ (fuori dal repository): verifica.py, punto 39, ricontrolla le frasi
su quelle copie. Non modifica i dati: se una frase sparisce scrive [CAMBIATA?] o [DA CONTROLLARE A MANO] ed esce con 1; allora si apre la
pagina, la si rilegge e si aggiorna dati/powerbank.json a mano (frasi, riassunti, controllato_il). Nessun blocco anti-robot o geografico
viene aggirato: una pagina che non si legge resta non letta e la compagnia resta senza riquadro (voce "escluse").
Ricontrollo MENSILE obbligatorio: nel 2025-2026 molte compagnie hanno cambiato regola (numero massimo, divieto d'uso a bordo).

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
CACHE = RADICE / "raccolta" / ".cache" / "powerbank"
DATI = RADICE / "dati" / "powerbank.json"
DOMANDA = RADICE / "dati" / "powerbank_domanda.json"
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

# Frasi misurate: {n} = nome come lo si cerca. Paese = mercato della compagnia (CERCA).
MODELLI = ["{n} power bank", "power bank {n}", "can i bring a power bank on {n}", "{n} power bank rules", "{n} portable charger"]
GENERALI = [("power bank rules", "us"), ("power bank rules", "gb"), ("power bank on plane", "us"), ("power bank on plane", "gb"),
            ("can you bring a power bank on a plane", "us"), ("can you take a power bank on a plane", "gb"), ("power bank airline rules", "us"),
            ("power bank in hand luggage", "gb"), ("airline power bank rules", "us"), ("power bank flight rules", "us")]
# slug della pagina cabin-bags -> (nome come lo si cerca, Paese della misura). Tutte le 40 compagnie, anche quelle senza riquadro.
CERCA = {"ryanair": ("ryanair", "gb"), "easyjet": ("easyjet", "gb"), "wizz-air": ("wizz air", "gb"), "vueling": ("vueling", "gb"), "jet2": ("jet2", "gb"),
         "british-airways": ("british airways", "gb"), "lufthansa": ("lufthansa", "gb"), "klm": ("klm", "gb"), "air-france": ("air france", "gb"),
         "ita-airways": ("ita airways", "gb"), "iberia": ("iberia", "gb"), "tap": ("tap air portugal", "gb"), "norwegian": ("norwegian", "gb"),
         "eurowings": ("eurowings", "gb"), "volotea": ("volotea", "gb"), "pegasus": ("pegasus", "gb"), "virgin-atlantic": ("virgin atlantic", "gb"),
         "emirates": ("emirates", "gb"), "qatar-airways": ("qatar airways", "gb"), "qantas": ("qantas", "au"), "united": ("united airlines", "us"),
         "american-airlines": ("american airlines", "us"), "delta": ("delta", "us"), "southwest": ("southwest", "us"), "jetblue": ("jetblue", "us"),
         "frontier": ("frontier", "us"), "air-canada": ("air canada", "ca"), "westjet": ("westjet", "ca"), "alaska-airlines": ("alaska airlines", "us"),
         "avelo": ("avelo", "us"), "breeze": ("breeze airways", "us"), "condor": ("condor", "gb"), "tui": ("tui", "gb"), "air-india": ("air india", "in"),
         "indigo": ("indigo", "in"), "air-transat": ("air transat", "ca"), "porter": ("porter", "ca"), "jetstar": ("jetstar", "au"),
         "virgin-australia": ("virgin australia", "au"), "turkish-airlines": ("turkish airlines", "gb")}


def norm(s):
    return re.sub(r"\s+", " ", s.replace("\xa0", " ").replace("​", "")).strip()


def nome_file(u):
    return re.sub(r"[^a-zA-Z0-9]+", "_", re.sub(r"^https?://", "", u))[:120] + ".txt"


def citazioni(C):
    """Tutte le citazioni di una compagnia: [{"f": chiave della fonte, "righe": [...]}, ...]."""
    out = []
    for v in C["voci"]:
        out += v["cit"]
    return out + C.get("extra", [])


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


def misura(frase, paese):
    url = "https://api.seodata.dev/v1/keyword?q=" + urllib.parse.quote(frase) + "&country=" + paese
    r = subprocess.run(["bash", "-c", 'curl -s -w "\\n%{http_code}" "$U" -H "Authorization: Bearer $(cat /root/.config/seodata/key)"'],
                       env={**os.environ, "U": url}, capture_output=True, text=True, timeout=60)
    corpo, _, codice = r.stdout.rpartition("\n")
    try:
        j = json.loads(corpo)
    except ValueError:
        j = {}
    time.sleep(0.3)
    if codice == "200" and "volume" in j:
        return {"volume": j.get("volume"), "cpc": j.get("cpc"), "simili": [[s["keyword"], s["volume"]] for s in j.get("similar", [])]}
    return {"errore": int(codice) if codice.isdigit() else codice}


def domanda():
    oggi = time.strftime("%Y-%m-%d")
    out = {"_nota": "Volumi di ricerca misurati per i power bank (riquadro «Power banks» nelle pagine cabin-bags/<compagnia>/ e indice "
                    "cabin-bags/power-banks/). Volume = media mensile di Google Ads nel Paese indicato; 0 = sotto le ~10 ricerche al mese; "
                    "errore 404 = frase non presente nello strumento (contata 0). Le frasi nell'H2 del riquadro, nelle descrizioni e nel "
                    "titolo dell'indice (genera.py) devono essere qui con volume > 0. Riscritto da raccolta/powerbank.py --domanda.",
           "fonte": "api.seodata.dev /v1/keyword (volume medio mensile Google Ads)", "misurato_il": oggi, "richieste": 0, "generali": {}, "compagnie": {}}
    for frase, paese in GENERALI:
        out["generali"][f"{frase} [{paese}]"] = {"frase": frase, "paese": paese, **misura(frase, paese)}
        out["richieste"] += 1
    print({k: v.get("volume", v.get("errore")) for k, v in out["generali"].items()})
    for slug, (nome, paese) in CERCA.items():
        frasi = {}
        for m in MODELLI:
            x = m.format(n=nome)
            frasi[x] = misura(x, paese)
            out["richieste"] += 1
        out["compagnie"][slug] = {"cerca": nome, "paese": paese, "frasi": frasi}
        print(slug, {k: v.get("volume", v.get("errore")) for k, v in frasi.items()})
    DOMANDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("richieste:", out["richieste"])


if __name__ == "__main__":
    domanda() if "--domanda" in sys.argv else ricontrollo()
