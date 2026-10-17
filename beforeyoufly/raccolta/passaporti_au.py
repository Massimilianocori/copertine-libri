"""Passaporto AUSTRALIANO: legge da Smartraveller (Australian Government, Department of Foreign Affairs and Trade) la sezione "Travel"
di ogni destinazione (sottosezioni "Visas and border measures", "Other formalities", "Passport") e scrive dati/passaporti_au.json.

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/passaporti_au.py              # legge le pagine nuove o più vecchie di 20 ore (circa 180, 10-20 minuti)
    BYF_OFFLINE=1 python3 -I beforeyoufly/raccolta/passaporti_au.py   # rilegge solo la cache, senza rete
    BYF_CACHE_ORE=0 python3 -I beforeyoufly/raccolta/passaporti_au.py # rilegge tutto

Lettura: smartraveller.gov.au chiude le richieste semplici (curl, urllib) e a volte anche il browser in HTTP/2; si legge con un browser vero
(Playwright + Chromium in /opt, proxy da HTTPS_PROXY, user agent di un browser desktop, HTTP/2 spento, solo il documento HTML: immagini,
font, stili e script bloccati), una pagina ogni 2-3 secondi,
fino a 4 tentativi con attese crescenti. Le pagine HTML vanno in raccolta/.cache/au/ (fuori dal repository): se lo script si interrompe,
al giro dopo riusa quelle lette da meno di BYF_CACHE_ORE ore e legge solo le altre (ripresa).
Controllo minimo: se legge meno dell'80 % delle destinazioni dell'elenco, dati/passaporti_au.json NON viene sovrascritto (esce con 1).
Le differenze di testo rispetto al file precedente vanno in dati/passaporti_au_cambi.json.

Licenza (pagina https://www.smartraveller.gov.au/copyright, "Last Updated Friday, 17/11/2023", letta il 17/10/2026): tutto il materiale del sito,
salvo stemma, loghi, marchi e materiale indicato come di terzi, è sotto Creative Commons Attribution (ultima versione: CC BY 4.0,
https://creativecommons.org/licenses/by/4.0/). Attribuzione richiesta: "the Department of Foreign Affairs and Trade's Smartraveller website -
www.smartraveller.gov.au". Il sito la riporta in ogni pagina australiana, con il link alla licenza e la nota che i riassunti sono nostri.

Riassunti (più prudenti di quelli britannici e canadesi, perché Smartraveller scrive in prosa):
  - si salva SEMPRE il testo ufficiale parola per parola; il sito lo mostra tra virgolette;
  - validità: Smartraveller usa quasi ovunque un testo generico ("Many countries require your passport to be valid for at least 6 months...",
    riquadro "more-information" uguale per tutti): è salvato come generico e NON diventa una regola del Paese. Riassunto SOLO se una frase
    del Paese corrisponde per intero a SCHEMI_VALIDITA (es. "Your passport must be valid for at least 6 months from the date you arrive in X");
  - visto: riassunto SOLO se la prima frase del paragrafo "Visas" corrisponde per intero a SCHEMI_VISTO, senza parole di dubbio, e se nessuna
    parte della sezione parla di eVisa/ETA/eVisitor/arrival card/moduli o registrazioni online/tessere/tasse (altrimenti solo citazione).
"""
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time
import unicodedata
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
CACHE = Path(os.environ.get("BYF_CACHE") or (RADICE / "raccolta" / ".cache" / "au"))
OFFLINE = os.environ.get("BYF_OFFLINE") == "1"
CACHE_ORE = float(os.environ.get("BYF_CACHE_ORE", "20"))
SITO = "https://www.smartraveller.gov.au"
ELENCO = SITO + "/destinations"
QUOTA_MINIMA = 0.8
LICENZA = "Creative Commons Attribution 4.0 International (CC BY 4.0)"
LICENZA_URL = "https://creativecommons.org/licenses/by/4.0/"
COPYRIGHT_URL = SITO + "/copyright"
ATTRIBUZIONE = "the Department of Foreign Affairs and Trade's Smartraveller website - www.smartraveller.gov.au"

LETTORE_JS = r"""
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const fs = require('fs');
const lista = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const attesa = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const pr = process.env.HTTPS_PROXY || process.env.https_proxy;
  let b = null, ctx = null;
  const apri = async () => {
    if (b) { try { await b.close(); } catch (e) {} }
    b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', proxy: pr ? { server: pr } : undefined,
                                args: ['--disable-http2', '--disable-background-networking', '--disable-component-update'] });
    ctx = await b.newContext({ userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
                               locale: 'en-AU', viewport: { width: 1366, height: 900 } });
    // serve solo il documento HTML (il testo è già nella pagina): immagini, font, stili e script non si scaricano, una richiesta per pagina
    await ctx.route('**/*', r => r.request().resourceType() === 'document' ? r.continue() : r.abort());
  };
  await apri();
  for (const [url, file, segno] of lista) {
    let ok = false;
    for (let t = 0; t < 4 && !ok; t++) {
      const p = await ctx.newPage();
      try {
        const r = await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
        await p.waitForTimeout(1200);
        const html = await p.content();
        if (r && r.status() === 200 && html.includes(segno)) { fs.writeFileSync(file, html); ok = true; console.log('OK ' + url); }
        else console.log('KO ' + url + ' ' + (r && r.status()));
      } catch (e) { console.log('ERR ' + url + ' ' + String(e).split('\n')[0].slice(0, 120)); }
      try { await p.close(); } catch (e) {}
      if (!ok) { await attesa(5000 * (t + 1)); if (t >= 1) await apri(); }
    }
    await attesa(2000 + Math.floor(Math.random() * 1000));
  }
  await b.close();
})();
"""


def nome_file(url):
    return re.sub(r"[^a-z0-9-]+", "_", url.replace(SITO, "").strip("/").lower()) + ".html"


def fresco(f):
    return f.exists() and (OFFLINE or time.time() - f.stat().st_mtime < CACHE_ORE * 3600)


def leggi_con_browser(voci):
    """voci = [(url, segno che deve esserci nella pagina)]; scrive in CACHE le pagine non fresche. Ritorna quante ne ha lette."""
    da_fare = [[u, str(CACHE / nome_file(u)), s] for u, s in voci if not fresco(CACHE / nome_file(u))]
    if not da_fare or OFFLINE:
        return 0
    CACHE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        js, lista = Path(d, "lettore.js"), Path(d, "lista.json")
        js.write_text(LETTORE_JS, encoding="utf-8")
        lista.write_text(json.dumps(da_fare), encoding="utf-8")
        r = subprocess.run(["node", str(js), str(lista)], capture_output=True, text=True, timeout=7200)
    righe = r.stdout.splitlines()
    for x in righe:
        if not x.startswith("OK "):
            print("  ", x)
    if r.returncode != 0:
        print("  errore del browser:", r.stderr[-500:])
    return sum(1 for x in righe if x.startswith("OK "))


# ------------------------------------------------------------------ HTML -> blocchi
class Blocchi(HTMLParser):
    """Blocchi della pagina: titoli h3/h4 (con id), paragrafi, voci di elenco; segna i blocchi dentro <blockquote class="more-information">
    (riquadri generici di Smartraveller, uguali per tutte le destinazioni)."""
    TAG = ("p", "li", "h2", "h3", "h4", "h5")

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocchi, self.cur, self.tag, self.id = [], None, None, None
        self.gen = 0
        self.pila = []
        self.div = []  # classi dei <div> aperti: il titolo di una sottosezione sta in un div "field--name-field-title"

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "div":
            self.div.append(a.get("class") or "")
        if tag == "blockquote":
            g = "more-information" in (a.get("class") or "")
            self.pila.append(g)
            self.gen += g
        if tag in ("script", "style", "button"):
            self.pila.append(tag)
        if tag in self.TAG:
            if self.cur is not None:
                self._chiudi()
            self.cur, self.tag, self.id = [], tag, a.get("id")
            self.titolo_campo = bool(self.div) and "field--name-field-title" in self.div[-1]
        elif tag == "br" and self.cur is not None:
            t, i = self.tag, self.id
            self._chiudi()
            self.cur, self.tag, self.id = [], t, i

    def handle_endtag(self, tag):
        if tag == self.tag and self.cur is not None:
            self._chiudi()
        if tag == "div" and self.div:
            self.div.pop()
        if tag == "blockquote" and self.pila:
            g = self.pila.pop()
            self.gen -= g is True
        if tag in ("script", "style", "button") and self.pila and self.pila[-1] == tag:
            self.pila.pop()

    def _chiudi(self):
        testo = re.sub(r"\s+", " ", "".join(self.cur).replace("\xa0", " ")).strip()
        if testo:
            b = {"t": {"h5": "h4"}.get(self.tag, self.tag), "x": testo}
            if self.id:
                b["id"] = self.id
            if self.tag == "h4" and getattr(self, "titolo_campo", False):
                b["sottosezione"] = True
            if self.gen > 0:
                b["generico"] = True
            self.blocchi.append(b)
        self.cur, self.tag, self.id = None, None, None

    def handle_data(self, data):
        if self.cur is not None and not (self.pila and self.pila[-1] in ("script", "style")):
            self.cur.append(data)


def blocchi(html):
    p = Blocchi()
    p.feed(html)
    if p.cur is not None:
        p._chiudi()
    return p.blocchi


def sezione_travel(bb):
    """Blocchi della sezione 'Travel' di 'Full advice' divisi per sottosezione: {titolo: [blocchi]}. Le sottosezioni sono i titoli h4 nel campo
    "field-title" della pagina (con JavaScript attivo ricevono anche un id "subheading-N-M"); gli altri h4 sono titoli interni al testo."""
    pieno = next((k for k, b in enumerate(bb) if b["t"] == "h2" and b["x"] == "Full advice"), None)
    if pieno is None:
        return None
    i = next((k for k, b in enumerate(bb) if k > pieno and b["t"] == "h3" and b["x"] == "Travel"), None)
    if i is None:
        return None
    out, cur = {}, None
    for b in bb[i + 1:]:
        if b["t"] in ("h2", "h3"):
            break
        if b["t"] == "h4" and (b.get("sottosezione") or b.get("id", "").startswith("subheading-")):
            cur = b["x"]
            out[cur] = []
            continue
        if cur is not None:
            out[cur].append({k: v for k, v in b.items() if k not in ("id", "sottosezione")})
    return out


def date_pagina(html):
    """('Still current at', 'Updated') come date ISO, dal riquadro 'Latest update' della pagina."""
    def d(etichetta):
        m = re.search(r"<strong>" + etichetta + r":</strong></span><span class=\"right[^\"]*\">([^<]+)</span>", html)
        if not m:
            return None
        try:
            return datetime.strptime(m.group(1).strip(), "%d %B %Y").date().isoformat()
        except ValueError:
            return None
    return d("Still current at"), d("Updated")


def frasi(testo):
    t = testo.replace("U.S.", "U․S․")
    return [f.strip().replace("U․S․", "U.S.") for f in re.split(r"(?<=[.!?])\s+(?=[A-Z])", t) if f.strip()]


def piano(s):
    return re.sub(r"[‘’]", "'", s).replace("“", '"').replace("”", '"')


def _n(s):
    s = unicodedata.normalize("NFKD", piano(s)).encode("ascii", "ignore").decode().strip().lower()
    return s[4:] if s.startswith("the ") else s


ALIAS = {"democratic-republic-congo": ["the DRC", "DRC"]}  # slug Smartraveller -> altri nomi usati nelle frasi (controllati a mano)


def nome_ok(x, nome, slug):
    return x is not None and _n(x) in {_n(c) for c in [nome] + ALIAS.get(slug, [])}


# ------------------------------------------------------------------ validità
NUM = r"(?P<n>\d+|six|three)"
UNI = r"(?P<u>months?|days?)"
X = r"(?P<x>[A-Z][^.,]*?)"
SCHEMI_VALIDITA = [
    ("dopo_partenza", re.compile(r"^Your passport must be valid (?:for )?(?P<q>at least )?" + NUM + " " + UNI + r" beyond the date you expect to leave " + X + r"\.$"), "partenza"),
    ("da_arrivo", re.compile(r"^To enter " + X + r",? your passport must be valid for (?P<q>at least )?" + NUM + " " + UNI + r" from the date of arrival\.$"), "arrivo"),
    ("residua_ingresso", re.compile(r"^You need to have (?P<q>at least )?" + NUM + " " + UNI + r" validity remaining in your passport to enter " + X + r"\.$"), "residua"),
    ("dopo_partenza", re.compile(r"^Your passport (?:must|needs to) be valid for (?P<q>at least )?" + NUM + " " + UNI
                                 + r" (?:after|beyond|from) the (?:date|day) you (?:plan to |intend to )?(?:leave|depart(?: from)?) " + X + r"\.$"), "partenza"),
    ("da_arrivo", re.compile(r"^Your passport (?:must|needs to) be valid for (?P<q>at least )?" + NUM + " " + UNI
                             + r" (?:after|beyond|from) the (?:date|day) you (?:arrive in|enter) " + X + r"\.$"), "arrivo"),
    ("da_arrivo", re.compile(r"^Your passport (?:must|needs to) be valid for (?P<q>at least )?" + NUM + " " + UNI
                             + r" (?:after|from) (?:your|the) (?:date of )?(?:arrival|entry) in(?:to)? " + X + r"\.$"), "arrivo"),
]
NUMERI = {"six": "6", "three": "3"}


def sintesi_validita(sezioni, nome, slug):
    """Ritorna (schema, sintesi, breve, frase, motivo, testo_paese). Cerca una frase del Paese (non generica) in 'Passport' e 'Visas...'."""
    pas = sezioni.get("Passport", [])
    del_paese = [b for b in pas if not b.get("generico") and b["t"] != "h4"]
    candidate = []
    for sez in ["Passport", VISTI] + [k for k in sezioni if k.lower() == "other formalities"]:
        for b in sezioni.get(sez, []):
            if b.get("generico") or b["t"] == "h4":
                continue
            for f in frasi(b["x"]):
                if re.search(r"\bpassport\b", f, re.I) and re.search(r"\bvalid\b|\bvalidity\b", f, re.I):
                    candidate.append(f)
    if not candidate:
        return None, None, None, None, "Smartraveller gives only its general advice on passport validity for this destination.", del_paese
    for f in candidate:
        for nome_schema, rx, base in SCHEMI_VALIDITA:
            m = rx.match(piano(f))
            if not m:
                continue
            g = m.groupdict()
            if not nome_ok(g["x"], nome, slug):
                continue
            if len(candidate) > 1:
                return None, None, None, f, "The official text has more than one sentence on passport validity.", del_paese
            n = NUMERI.get(g["n"], g["n"])
            u = g["u"].rstrip("s") + ("" if n == "1" else "s")
            q = g.get("q") or ""
            if base == "residua":
                return nome_schema, f"At least {n} {u} of validity remaining when you enter {g['x']}", f"{n} {u} remaining on entry", f, None, del_paese
            if base == "partenza":
                return nome_schema, f"Valid for {q}{n} {u} after the date you leave {g['x']}", f"{n} {u} after departure", f, None, del_paese
            return nome_schema, f"Valid for {q}{n} {u} from the date you arrive in {g['x']}", f"{n} {u} from arrival", f, None, del_paese
    return None, None, None, candidate[0], "The official sentence does not match a wording we summarise.", del_paese


# ------------------------------------------------------------------ visti
V_NUM = r"(?P<n>\d+)"
V_UNI = r"(?P<u>days|months)"
SCHEMI_VISTO = [
    ("senza_visto_durata", re.compile(r"^You don't need a visa to (?:visit|enter|travel to) " + X + r" for (?P<q>up to |less than )?" + V_NUM + " " + V_UNI
                                      + r"(?P<pur> for tourism)?\.$")),
    ("senza_visto_durata", re.compile(r"^You can (?:visit|enter|travel to) " + X + r" without a visa for (?P<q>up to |less than )?" + V_NUM + " " + V_UNI + r"(?P<pur> for tourism)?\.$")),
    ("turisti_durata", re.compile(r"^Tourists can (?:visit|enter) " + X + r" for (?P<q>up to )?" + V_NUM + " " + V_UNI + r" without a visa\.$")),
    ("turisti_australiani", re.compile(r"^Australian tourists can (?:visit|enter) " + X + r" without a visa for (?P<q>up to )?" + V_NUM + " " + V_UNI + r"\.$")),
    ("soggiorno_durata", re.compile(r"^You can stay in " + X + r" for (?P<q>up to )?" + V_NUM + " " + V_UNI + r" without a visa\.$")),
    ("senza_visto", re.compile(r"^You don't need a visa to visit " + X + r"(?P<pur> for tourism| as a tourist)\.$")),
    ("visto_richiesto", re.compile(r"^(?:You|You'll|Australians) (?:need|must get|must have) a visa (?P<verbo>to (?:visit|enter|travel to)|before you enter) " + X + r"\.$")),
]
SENZA_DURATA = " (read the official text for how long you can stay)"
DUBBIO_VISTO = re.compile(r"usually|normally|until|from \d|discretion|however|unless|except|if you|\bmay\b|might|check|\bmost\b|either|some cases|eligible|scheme", re.I)
AUTORIZZAZIONE = re.compile(r"\b(?:ETA|eTA|ESTA|NZeTA|K-ETA|ETIAS|EVW|ED card)\b|eVisitor|electronic travel|travel authori[sz]ation|\be-?visa|\beVisa|electronic visa"
                            r"|arrival card|e-arrival|arrival declaration|declaration form|immigration form|embarkation|landing card|tourist card|migration card"
                            r"|entry fee|entry tax|tourism fee|tourist tax|levy|pre-?regist|pre-?arrival|register online|online registration|e-?Travel|online form"
                            r"|\bonline\b|\bfees?\b|QR code|visa on arrival|on arrival|at the airport", re.I)


def sintesi_visto(sezioni, nome, slug):
    """Ritorna (schema, sintesi, frase, motivo, testo). testo = blocchi del Paese di 'Visas and border measures' (generici esclusi)."""
    vis = sezioni.get(VISTI, [])
    testo = [b for b in vis if not b.get("generico")]
    # primo paragrafo del Paese (non generico) della sottosezione, sotto un eventuale titolo interno sui visti
    primo = next((b for b in vis if b["t"] == "p" and not b.get("generico")), None)
    if not testo:
        return None, None, None, "Smartraveller has no destination-specific visa text for this destination.", testo
    if primo is None:
        return None, None, None, "The official text has no 'Visas' paragraph we can start from.", testo
    ff = frasi(primo["x"])
    frase = ff[0] if ff else primo["x"]
    p = piano(frase)
    tutto = " ".join(b["x"] for b in testo) + " " + " ".join(b["x"] for k in sezioni if k not in ("Passport", VISTI)
                                                            for b in sezioni[k] if not b.get("generico"))
    for nome_schema, rx in SCHEMI_VISTO:
        m = rx.match(p)
        if not m:
            continue
        g = m.groupdict()
        if not nome_ok(g.get("x"), nome, slug):
            return None, None, frase, "The first official sentence is not about this destination.", testo
        if DUBBIO_VISTO.search(p) or (len(ff) > 1 and re.search(r"\bhowever\b|\bbut\b|\bunless\b|\bexcept\b", " ".join(ff[1:]), re.I)):
            return None, None, frase, "The official sentence has conditions we do not summarise.", testo
        if AUTORIZZAZIONE.search(tutto):
            return None, None, frase, ("The official text also mentions an eVisa, electronic travel authority, arrival card, online form or registration, "
                                       "visa on arrival, tourist card or fee: read it in full."), testo
        if nome_schema == "senza_visto_durata":
            s = f"You don't need a visa to visit {g['x']} for {g.get('q') or ''}{g['n']} {g['u']}{g.get('pur') or ''}"
        elif nome_schema == "turisti_durata":
            s = f"Tourists can visit {g['x']} for {g.get('q') or ''}{g['n']} {g['u']} without a visa"
        elif nome_schema == "turisti_australiani":
            s = f"Australian tourists can enter {g['x']} without a visa for {g.get('q') or ''}{g['n']} {g['u']}"
        elif nome_schema == "soggiorno_durata":
            s = f"You can stay in {g['x']} for {g.get('q') or ''}{g['n']} {g['u']} without a visa"
        elif nome_schema == "senza_visto":
            s = f"You don't need a visa to visit {g['x']}{g['pur']}{SENZA_DURATA}"
        else:
            s = f"You need a visa {g['verbo']} {g['x']}"  # stesso verbo della frase ufficiale
        return nome_schema, s, frase, None, testo
    return None, None, frase, "The first official sentence does not match a wording we summarise.", testo


# ------------------------------------------------------------------ lettura di una destinazione
def passaporto_di(sez):
    """La sottosezione sul passaporto si chiama 'Passport' o 'Passports'."""
    return next((v for k, v in sez.items() if k.strip().lower() in ("passport", "passports")), [])


VISTI = "Visas and border measures"  # nome interno della sottosezione dei visti (sulla pagina può chiamarsi anche "Visas", "Visa and border measures"...)
TITOLO_VISTI = re.compile(r"^visas?(?: and border measures)?$|^visa measures$", re.I)
# sottosezioni di "Travel" che non riguardano l'ingresso: non si salvano
NON_INGRESSO = re.compile(r"^(?:passports?|money|local travel|transport|working in .+)$", re.I)


def normalizza(sez):
    """{titolo originale: blocchi} -> (sezioni con i visti sotto VISTI e il passaporto sotto "Passport", titolo originale dei visti, altre sezioni).
    Revisione del 17/10/2026: prima si leggeva solo il titolo esatto "Visas and border measures", e 7 pagine (Uruguay, Eritrea, Azerbaijan,
    Bulgaria, Georgia, Panama, Turkmenistan) risultavano senza testo sui visti; si leggeva solo "Other formalities" e si perdevano
    "European Entry and Exit Systems" (27 pagine), "Border measures" e le altre sottosezioni sull'ingresso."""
    pulito = {re.sub(r"[\u200b\s]+", " ", k).strip(): v for k, v in sez.items()}
    tit_visti = [k for k in pulito if TITOLO_VISTI.match(k)]
    out = {"Passport": passaporto_di(pulito), VISTI: [b for k in tit_visti for b in pulito[k]]}
    altre = [(k, v) for k, v in pulito.items() if k not in tit_visti and not NON_INGRESSO.match(k) and v]
    for k, v in altre:
        out[k] = v
    return out, " / ".join(tit_visti) or VISTI, altre


def leggi_paese(url, html):
    bb = blocchi(html)
    h1 = re.search(r"<h1[^>]*data-destination-id[^>]*>([^<]+)</h1>", html)
    nome = re.sub(r"\s+", " ", h1.group(1)).strip() if h1 else None
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    sez, tit_visti, altre = normalizza(sezione_travel(bb) or {})
    corrente, aggiornata = date_pagina(html)
    v_schema, v_sint, v_breve, v_frase, v_motivo, pas_paese = sintesi_validita(sez, nome, slug)
    s_schema, s_sint, s_frase, s_motivo, vis_testo = sintesi_visto(sez, nome, slug)
    return {
        "slug_fonte": slug, "regione": url.rstrip("/").rsplit("/", 2)[-2], "nome": nome, "url": url,
        "aggiornata": aggiornata, "ancora_valida_il": corrente,
        "passaporto": {"titolo_sezione": "Passport", "testo": sez.get("Passport", []), "testo_paese": pas_paese, "frase": v_frase,
                       "schema": v_schema, "sintesi": v_sint, "breve": v_breve, "motivo": v_motivo},
        "visto": {"titolo_sezione": tit_visti, "testo": sez.get(VISTI, []), "testo_paese": vis_testo,
                  "frase": s_frase, "schema": s_schema, "sintesi": s_sint, "motivo": s_motivo},
        "altre_sezioni": [{"titolo": k, "testo": v} for k, v in altre],
    }


NON_DESTINAZIONI = {"crisis-alert"}  # link della pagina elenco che non sono destinazioni


def elenco_destinazioni(html):
    return sorted(set(SITO + h for h in re.findall(r'href="(/destinations/[a-z-]+/[a-z0-9-]+)"', html) if h.rsplit("/", 1)[-1] not in NON_DESTINAZIONI))


def main():
    oggi = date.today().isoformat()
    leggi_con_browser([(ELENCO, "/destinations/")])
    f_elenco = CACHE / nome_file(ELENCO)
    if not f_elenco.exists():
        print("Elenco delle destinazioni non letto: dati/passaporti_au.json NON aggiornato.")
        sys.exit(1)
    urls = elenco_destinazioni(f_elenco.read_text(encoding="utf-8"))
    print(f"Destinazioni nell'elenco Smartraveller: {len(urls)}")
    n_letti = leggi_con_browser([(u, ">Travel</h3>") for u in urls])
    paesi, errori = [], []
    for u in urls:
        f = CACHE / nome_file(u)
        if not f.exists():
            errori.append(u)
            continue
        p = leggi_paese(u, f.read_text(encoding="utf-8"))
        if not p["nome"] or not (p["passaporto"]["testo"] or p["visto"]["testo"]):
            errori.append(u + " (sezione Travel non trovata)")
            continue
        paesi.append(p)
    paesi.sort(key=lambda p: p["nome"].lower())
    print(f"Destinazioni lette: {len(paesi)} su {len(urls)} (lette ora nel browser: {n_letti}); errori: {len(errori)}")
    for e in errori:
        print("  ERRORE", e)
    if len(paesi) < QUOTA_MINIMA * len(urls):
        print("Troppe destinazioni non lette: dati/passaporti_au.json NON aggiornato.")
        sys.exit(1)
    file = DATI / "passaporti_au.json"
    vecchio = json.loads(file.read_text(encoding="utf-8")) if file.exists() else None
    nuovo = {"fonte": "Smartraveller – Australian Government, Department of Foreign Affairs and Trade", "fonte_url": ELENCO,
             "licenza": LICENZA, "licenza_url": LICENZA_URL, "copyright_url": COPYRIGHT_URL, "attribuzione": ATTRIBUZIONE,
             "controllato_il": oggi, "pagine_indice": len(urls), "paesi": paesi}
    if vecchio:
        prima = {p["slug_fonte"]: p for p in vecchio["paesi"]}
        cambi_file = DATI / "passaporti_au_cambi.json"
        storico = json.loads(cambi_file.read_text(encoding="utf-8")) if cambi_file.exists() else {"cambi": []}
        n = 0
        for p in paesi:
            q = prima.get(p["slug_fonte"])
            for sez in ("passaporto", "visto"):
                if q and [b["x"] for b in q[sez]["testo"]] != [b["x"] for b in p[sez]["testo"]]:
                    storico["cambi"].insert(0, {"rilevato_il": oggi, "slug": p["slug_fonte"], "nome": p["nome"], "sezione": sez,
                                                "prima": [b["x"] for b in q[sez]["testo"]], "dopo": [b["x"] for b in p[sez]["testo"]]})
                    n += 1
        if n:
            cambi_file.write_text(json.dumps(storico, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Testi cambiati rispetto al file precedente: {n}")
    file.write_text(json.dumps(nuovo, ensure_ascii=False, indent=1), encoding="utf-8")
    va = sum(1 for p in paesi if p["passaporto"]["sintesi"])
    vv = sum(1 for p in paesi if p["visto"]["sintesi"])
    print(f"Validità: {va} riassunti, {len(paesi) - va} solo citazione (di cui {sum(1 for p in paesi if not p['passaporto']['frase'])} con il solo testo generico)")
    print(f"Visti: {vv} riassunti, {len(paesi) - vv} solo citazione")


if __name__ == "__main__":
    main()
