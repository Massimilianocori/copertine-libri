"""eSIM di viaggio (riquadro «Before you go», programmi Awin): legge dalle pagine ufficiali dei fornitori l'elenco dei Paesi per cui
vendono un piano e scrive dati/esim.json. Serve solo a due cose: mettere Vodafone per primo dove il suo elenco comprende la destinazione,
e scrivere «X lists plans for <Paese>» solo quando è vero (nessuna promessa su copertura, velocità o prezzi).

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/esim.py            # legge le due pagine e scrive dati/esim.json
    python3 -I beforeyoufly/raccolta/esim.py --cache    # come sopra ma senza rete, dalle copie in raccolta/.cache/esim/

Fonti (lette il 10/11/2026):
  - Vodafone Travel eSIM: https://travel.vodafone.com/our-destinations, scheda «Countries» (pagina in JavaScript: si legge con il browser,
    Playwright + Chromium in /opt come raccolta/passaporti_au.py, cookie «Reject All», una sola pagina). Ogni Paese ha «Plans from $…» o
    «See available plans». I nomi si portano ai codici ISO con dati/paesi_iso.json e ALIAS_VODAFONE (scritti a mano); i nomi che non sono
    un Paese ISO (es. «Netherlands Antilles») restano in 'non_mappati'.
  - Pocket eSIM: https://www.pocketesim.net/esim «Search eSIM Destinations» (HTML normale): ogni destinazione ha la bandiera
    flags/<codice>.svg (codice ISO a due lettere), il nome e «From … USD»; le offerte regionali e globali non hanno una bandiera di Paese.
Controllo minimo: se un elenco ha meno di MINIMO Paesi, dati/esim.json NON viene sovrascritto (esce con 1, restano i dati dell'ultima
lettura buona). Copie in raccolta/.cache/esim/ (escluse da git).
"""
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from datetime import date
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
CACHE = Path(__file__).resolve().parent / ".cache" / "esim"
FILE = DATI / "esim.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
MINIMO = 100
FONTI = {
    "vodafone": {"url": "https://travel.vodafone.com/our-destinations", "nome": "Vodafone Travel eSIM", "file": "vodafone.txt"},
    "pocket": {"url": "https://www.pocketesim.net/esim", "nome": "Pocket eSIM", "file": "pocket.html"},
}
# nomi della pagina Vodafone che non sono uguali al nome o a un alias di dati/paesi_iso.json (scritti a mano il 10/11/2026)
ALIAS_VODAFONE = {"UK": "GB", "United Kingdom (UK)": "GB", "USA": "US", "United States (USA)": "US", "UAE": "AE", "Bosnia": "BA",
                  "Ivory Coast": "CI", "Congo DR": "CD", "Salvador": "SV", "El Salvador": "SV", "Macau": "MO", "Republic of Congo": "CG",
                  "Palestine": "PS", "State of Palestine": "PS", "Republic Of Congo": "CG", "Guinea Bissau": "GW", "Turkey": "TR", "Czech Republic": "CZ", "South Korea": "KR", "Laos": "LA", "Moldova": "MD",
                  "Russia": "RU", "Vietnam": "VN", "Tanzania": "TZ", "Iran": "IR", "Syria": "SY", "Brunei": "BN", "Cape Verde": "CV",
                  "Saint Vincent": "VC", "Saint Kitts and Nevis": "KN", "Saint Lucia": "LC", "Micronesia": "FM", "Bolivia": "BO",
                  "Venezuela": "VE", "Taiwan": "TW", "Kosovo": "XK", "Reunion": "RE", "Curacao": "CW", "Eswatini": "SZ",
                  "Turks and Caicos": "TC", "British Virgin Islands": "VG", "Faroe Islands": "FO", "North Macedonia": "MK"}

LETTORE_JS = r"""
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const fs = require('fs');
(async () => {
  const pr = process.env.HTTPS_PROXY || process.env.https_proxy;
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', proxy: pr ? { server: pr } : undefined, args: ['--disable-http2'] });
  const ctx = await b.newContext({ userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
                                   locale: 'en-GB', viewport: { width: 1366, height: 900 } });
  const p = await ctx.newPage();
  const r = await p.goto(process.argv[2], { waitUntil: 'networkidle', timeout: 90000 });
  await p.waitForTimeout(2000);
  try { await p.getByText('Reject All', { exact: true }).first().click({ timeout: 5000 }); } catch (e) {}
  await p.waitForTimeout(800);
  await p.getByText('Countries', { exact: true }).first().click({ timeout: 20000 });
  await p.waitForTimeout(4000);
  fs.writeFileSync(process.argv[3], 'HTTP ' + (r ? r.status() : 0) + '\n' + await p.innerText('body'));
  await b.close();
})();
"""


def nomi_iso():
    m = {}
    for p in json.loads((DATI / "paesi_iso.json").read_text(encoding="utf-8"))["paesi"]:
        for n in [p["nome"]] + (p.get("alias") or []):
            m.setdefault(n.casefold(), p["iso2"])
    return m


def leggi_vodafone(rete):
    f = CACHE / FONTI["vodafone"]["file"]
    if rete:
        CACHE.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as d:
            js = Path(d, "lettore.js")
            js.write_text(LETTORE_JS, encoding="utf-8")
            r = subprocess.run(["node", str(js), FONTI["vodafone"]["url"], str(f)], capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            print("  Vodafone: errore del browser:", r.stderr[-400:])
    testo = f.read_text(encoding="utf-8")
    http = int(re.match(r"HTTP (\d+)", testo).group(1))
    righe = [x.strip() for x in testo.splitlines()]
    inizio = righe.index("Countries") + 1
    nomi = []
    for i in range(inizio, len(righe) - 2):
        if righe[i] and re.fullmatch(r"Plans from \S+|See available plans", righe[i + 1] if righe[i + 1] else righe[i + 2] if i + 2 < len(righe) else ""):
            nomi.append(righe[i])
        if righe[i].startswith("Vodafone Global Connect"):
            break
    return http, nomi, testo


def leggi_pocket(rete):
    f = CACHE / FONTI["pocket"]["file"]
    if rete:
        CACHE.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(FONTI["pocket"]["url"], headers={"User-Agent": UA, "Accept-Language": "en-GB,en;q=0.9",
                                                                      "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
        with urllib.request.urlopen(req, timeout=60) as r:
            http = r.status
            f.write_bytes(r.read())
    else:
        http = 200
    html = f.read_text(encoding="utf-8", errors="replace")
    voci = re.findall(r'<a href="/esim/([a-z0-9-]+)">\s*<div class="products__list__countries">.*?flags/([a-z]{2})\.svg.*?'
                      r'title="([^"]+)".*?From <span[^>]*>([\d.]+)</span> USD', html, re.S)
    return http, [(slug, cod.upper(), unescape(nome)) for slug, cod, nome, _ in voci], html


def main():
    rete = "--cache" not in sys.argv
    iso = nomi_iso()
    oggi = date.today().isoformat()
    vecchio = json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else {}
    out = {"_nota": "Paesi per cui i fornitori di eSIM del riquadro «Before you go» elencano un piano sulla loro pagina ufficiale delle "
                    "destinazioni, letti da raccolta/esim.py. Usato solo per l'ordine dei fornitori e per la frase «X lists plans for <Paese>». "
                    "Non modificare a mano: rilanciare lo script.", "letto_il": oggi, "fornitori": {}}
    problemi = []
    http, nomi, testo = leggi_vodafone(rete)
    paesi, non_mappati = {}, []
    for n in nomi:
        c = ALIAS_VODAFONE.get(n) or iso.get(n.casefold())
        if c:
            paesi[c] = n
        else:
            non_mappati.append(n)
    out["fornitori"]["vodafone"] = {"nome": FONTI["vodafone"]["nome"], "url": FONTI["vodafone"]["url"], "http": http, "letto_il": oggi,
                                    "paesi": dict(sorted(paesi.items())), "non_mappati": non_mappati,
                                    "impronta": hashlib.sha256("\n".join(nomi).encode()).hexdigest()[:16]}
    print(f"  vodafone: HTTP {http}, {len(nomi)} nomi, {len(paesi)} Paesi ISO, non mappati: {non_mappati}")
    if http != 200 or len(paesi) < MINIMO:
        problemi.append(f"vodafone: HTTP {http}, {len(paesi)} Paesi")
    http, voci, _ = leggi_pocket(rete)
    paesi = {}
    for slug, cod, nome in voci:
        if cod in {v for v in iso.values()}:
            paesi[cod] = nome
    out["fornitori"]["pocket"] = {"nome": FONTI["pocket"]["nome"], "url": FONTI["pocket"]["url"], "http": http, "letto_il": oggi,
                                  "paesi": dict(sorted(paesi.items())),
                                  "impronta": hashlib.sha256("\n".join(f"{c} {n}" for _, c, n in voci).encode()).hexdigest()[:16]}
    print(f"  pocket: HTTP {http}, {len(voci)} destinazioni con bandiera, {len(paesi)} Paesi ISO")
    if http != 200 or len(paesi) < MINIMO:
        problemi.append(f"pocket: HTTP {http}, {len(paesi)} Paesi")
    if problemi:
        print("NON SCRITTO dati/esim.json (restano i dati dell'ultima lettura buona):", problemi)
        sys.exit(1)
    for k, F in out["fornitori"].items():
        V = (vecchio.get("fornitori") or {}).get(k)
        if V and V["paesi"] != F["paesi"]:
            print(f"  {k}: CAMBIATO l'elenco: in più {sorted(set(F['paesi']) - set(V['paesi']))}, tolti {sorted(set(V['paesi']) - set(F['paesi']))}")
    FILE.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Scritto {FILE.relative_to(RADICE.parent)}")


if __name__ == "__main__":
    main()
