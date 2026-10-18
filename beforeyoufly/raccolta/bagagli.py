"""Ricontrollo mensile del bagaglio a mano (Before You Fly).

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/bagagli.py

Per ogni compagnia di dati/bagagli.json (e per le pagine ufficiali UE della regola sull'oggetto personale) apre la pagina ufficiale con
Chromium headless (Playwright in /opt, proxy da HTTPS_PROXY, user agent di un browser desktop, HTTP/2 spento, una pagina alla volta con
una pausa) e controlla che ogni frase citata sia ancora sulla pagina, parola per parola (spazi normalizzati). Il testo letto è salvato in
raccolta/.cache/bagagli/ (escluso da git). Non modifica i dati: se una frase sparisce scrive [CAMBIATA?] o [DA CONTROLLARE A MANO] e
esce con 1; allora si apre la pagina, la si rilegge e si aggiorna dati/bagagli.json (frasi, misure, controllato_il) a mano.
Ci vogliono 20-30 minuti (circa 40 s per pagina).
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
CACHE = RADICE / "raccolta" / ".cache" / "bagagli"
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


def norm(s):
    return re.sub(r"\s+", " ", s.replace("\xa0", " ").replace("​", "")).strip()


def nome_file(u):
    return re.sub(r"[^a-zA-Z0-9]+", "_", re.sub(r"^https?://", "", u))[:120] + ".txt"


def main():
    d = json.loads((RADICE / "dati" / "bagagli.json").read_text(encoding="utf-8"))
    voci = []  # (etichetta, url, [frasi])
    for C in d["compagnie"]:
        cits = [c for b in C["borse"] for c in b["cit"]] + [c for t in C["tariffe"] for c in t["cit"]] + C["avvisi"] + C.get("extra", [])
        for k, f in C["fonti"].items():
            voci.append((f"{C['nome']} ({k})", f["url"], sorted({norm(" ".join(c["righe"])) for c in cits if c["f"] == k})))
    U = d["ue"]
    for k, f in U["fonti"].items():
        frasi = {norm(" ".join(c["righe"])) for c in U["citazioni"] if c["f"] == k}
        if k == "oeil":
            frasi |= {f"{x['data'][8:10]}/{x['data'][5:7]}/{x['data'][:4]} {x['evento']}" for x in U["iter"]}
        voci.append((f"UE ({k})", f["url"], sorted(frasi)))
    urls = sorted({u for _, u, _ in voci})
    CACHE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        lista, uscita, script = Path(tmp) / "urls.json", Path(tmp) / "out.json", Path(tmp) / "leggi.js"
        lista.write_text(json.dumps(urls))
        script.write_text(JS)
        try:
            subprocess.run(["node", str(script), str(lista), UA, str(uscita)], timeout=150 * len(urls) + 120, check=False)
            letti = json.loads(uscita.read_text()) if uscita.exists() else {}
        except subprocess.TimeoutExpired:
            letti = {}
    for u, (s, t) in letti.items():
        (CACHE / nome_file(u)).write_text(f"STATUS {s}\nURL {u}\n\n{t}", encoding="utf-8")
    problemi = 0
    for etichetta, u, frasi in voci:
        s, t = letti.get(u, [0, ""])
        t = norm(t)
        mancano = [q for q in frasi if q not in t]
        if len(t) < 500 or (s >= 400 and len(mancano) == len(frasi)):  # es. 429 "You are being rate limited": non è un cambio della pagina
            print(f"[DA CONTROLLARE A MANO] {etichetta}: pagina non leggibile o bloccata (HTTP {s}); rilanciare più tardi – {u}")
            problemi += 1
        elif mancano:
            print(f"[CAMBIATA?] {etichetta}: {len(mancano)} frasi su {len(frasi)} non trovate – {u}")
            for q in mancano:
                print("     -", q[:140])
            problemi += 1
        else:
            print(f"[OK] {etichetta}: {len(frasi)} frasi presenti")
    print(f"\n{len(voci) - problemi} pagine invariate su {len(voci)}; {problemi} da controllare. Testi in {CACHE}")
    sys.exit(1 if problemi else 0)


if __name__ == "__main__":
    main()
