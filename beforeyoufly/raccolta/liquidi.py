"""Ricontrollo mensile delle regole sui liquidi (dati/aeroporti.json).

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/liquidi.py
    BYF_BROWSER=1 python3 -I beforeyoufly/raccolta/liquidi.py   # usa anche un browser automatico (Playwright) per i siti che bloccano

Per ogni aeroporto scarica la pagina ufficiale e controlla che ogni frase citata sia ancora presente, parola per parola.
NON modifica i dati: stampa un rapporto. Se una frase manca, la regola può essere cambiata: aprire la pagina, leggerla,
aggiornare a mano dati/aeroporti.json (frasi, regola, data del controllo) e rigenerare il sito.
I siti che bloccano le richieste semplici (lettura "browser") vanno controllati con BYF_BROWSER=1 o a mano.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
PLAYWRIGHT = "/opt/node-tools/node_modules/playwright"
CHROMIUM = "/opt/pw-browsers/chromium"


def norm(s):
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def testo_html(h):
    h = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", h)
    return norm(unescape(re.sub(r"<[^>]+>", " ", h)))


def diretta(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-GB,en;q=0.9", "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.status, testo_html(r.read().decode("utf-8", "replace"))


def browser(urls):
    """Testo visibile delle pagine, letto con Chromium headless (se disponibile)."""
    if not shutil.which("node") or not Path(PLAYWRIGHT).exists():
        return {}
    js = """const { chromium } = require(%s);
(async () => { const proxy = process.env.HTTPS_PROXY || process.env.https_proxy;
  const b = await chromium.launch({ executablePath: %s, proxy: proxy ? { server: proxy } : undefined });
  const ctx = await b.newContext({ locale: 'en-GB', userAgent: %s }); const out = {};
  for (const u of %s) { const p = await ctx.newPage();
    for (let t = 0; t < 2; t++) {  // secondo tentativo se la pagina torna vuota
      try { const r = await p.goto(u, { waitUntil: 'domcontentloaded', timeout: 45000 }); await p.waitForTimeout(6000);
        out[u] = [r ? r.status() : 0, await p.evaluate(() => document.body ? document.body.innerText : '')]; }
      catch (e) { out[u] = [0, '']; }
      if (out[u][1].length > 500) break; }
    await p.close(); }
  await b.close(); console.log(JSON.stringify(out)); })();""" % (json.dumps(PLAYWRIGHT), json.dumps(CHROMIUM), json.dumps(UA), json.dumps(urls))
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(js)
    try:
        r = subprocess.run(["node", fh.name], capture_output=True, text=True, timeout=60 * len(urls) + 60)
        return {u: (s, norm(t)) for u, (s, t) in json.loads(r.stdout).items()}
    except Exception:  # noqa: BLE001
        return {}
    finally:
        os.unlink(fh.name)


def main():
    d = json.loads((RADICE / "dati" / "aeroporti.json").read_text(encoding="utf-8"))
    voci = []
    for a in d["aeroporti"] + d["nazionali"]:
        voci.append(a)
        if a.get("fonte2"):  # seconda pagina ufficiale citata (es. FAQ del gestore)
            voci.append({"iata": a.get("iata", "") + " (2)", "slug": a["slug"], "nome": a["nome"], "url": a["fonte2"]["url"], "lettura": "browser",
                         "citazioni": a["fonte2"].get("citazioni", [])})
    risultati, da_browser = {}, []
    for a in voci:
        try:
            s, t = diretta(a["url"])
            risultati[a["url"]] = (s, t)
        except Exception as e:  # noqa: BLE001
            risultati[a["url"]] = (getattr(e, "code", 0), "")
    if os.environ.get("BYF_BROWSER") == "1":
        da_browser = sorted({a["url"] for a in voci if not all(norm(q) in risultati[a["url"]][1] for q in a["citazioni"])})
        risultati.update(browser(da_browser))
    problemi = 0
    for a in voci:
        s, t = risultati[a["url"]]
        mancano = [q for q in a["citazioni"] + a.get("eccezioni", []) if norm(q) not in t]
        if a.get("lettura") == "browser" and os.environ.get("BYF_BROWSER") != "1" and (not t or mancano):
            print(f"[SERVE IL BROWSER] {a.get('iata', a['slug'])} {a['nome']}: pagina letta con il browser il {a.get('controllato_il')}; "
                  f"rilanciare con BYF_BROWSER=1 – {a['url']}")
            problemi += 1
        elif not t:
            print(f"[DA CONTROLLARE A MANO] {a.get('iata', a['slug'])} {a['nome']}: pagina non leggibile (HTTP {s}) – {a['url']}")
            problemi += 1
        elif mancano:
            print(f"[CAMBIATA?] {a.get('iata', a['slug'])} {a['nome']}: {len(mancano)} frasi non trovate – {a['url']}")
            for q in mancano:
                print("     -", q[:120])
            problemi += 1
        else:
            print(f"[OK] {a.get('iata', a['slug'])} {a['nome']}")
    print(f"\n{len(voci) - problemi} pagine invariate su {len(voci)}; {problemi} da controllare.")
    sys.exit(1 if problemi else 0)


if __name__ == "__main__":
    main()
