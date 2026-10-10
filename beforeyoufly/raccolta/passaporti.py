"""Scarica le regole di validità del passaporto (passaporto britannico) dalle pagine FCDO "foreign travel advice"
tramite la GOV.UK Content API e scrive dati/passaporti.json.

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/passaporti.py            # scarica tutto (circa 226 richieste, 1-2 minuti)
    BYF_CACHE=/percorso/cartella python3 -I beforeyoufly/raccolta/passaporti.py
        # salva anche il JSON grezzo di ogni pagina in quella cartella (utile per i controlli)
    BYF_OFFLINE=1 BYF_CACHE=/percorso/cartella python3 -I beforeyoufly/raccolta/passaporti.py
        # rilegge i file grezzi già scaricati, senza rete

Fonte: GOV.UK Content API, https://www.gov.uk/api/content/foreign-travel-advice/<paese>
Licenza: Open Government Licence v3.0 (riuso consentito con attribuzione).

Regola di prudenza: la regola viene trasformata in un calcolo SOLO quando la frase ufficiale corrisponde esattamente
a uno degli schemi qui sotto. In tutti gli altri casi (stato "manuale") il sito mostra la frase ufficiale tra virgolette
e il calcolatore dice di leggerla: nessuna interpretazione.

Se meno di 200 pagine vengono lette correttamente, il file dati/passaporti.json NON viene sovrascritto (esce con 1).
Le differenze di testo rispetto al file precedente vengono aggiunte a dati/passaporti_cambi.json (storico dei cambi).
"""
import json
import os
import re
import sys
import time
import urllib.request
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
API = "https://www.gov.uk/api/content/foreign-travel-advice"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
CACHE = os.environ.get("BYF_CACHE")
OFFLINE = os.environ.get("BYF_OFFLINE") == "1"
MINIMO_PAGINE = 200


def scarica(url, nome_cache):
    if CACHE and OFFLINE:
        return json.loads(Path(CACHE, nome_cache).read_text(encoding="utf-8"))
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    for tentativo in range(3):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                corpo = r.read()
            if CACHE:
                Path(CACHE).mkdir(parents=True, exist_ok=True)
                Path(CACHE, nome_cache).write_bytes(corpo)
            return json.loads(corpo)
        except Exception:  # noqa: BLE001
            if tentativo == 2:
                raise
            time.sleep(2 + tentativo * 3)


# ------------------------------------------------------------------ HTML -> blocchi di testo
class Blocchi(HTMLParser):
    TAG = ("p", "li", "h2", "h3", "h4")

    def __init__(self):
        super().__init__()
        self.blocchi = []
        self.cur = None
        self.tag = None
        self.profondita = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.TAG:
            if self.cur is not None and tag in ("p", "li"):
                # blocco annidato (es. <p> dentro <li>): chiude quello aperto
                self._chiudi()
            self.cur, self.tag = [], tag

    def handle_endtag(self, tag):
        if tag == self.tag and self.cur is not None:
            self._chiudi()

    def _chiudi(self):
        testo = re.sub(r"\s+", " ", "".join(self.cur)).strip()
        if testo:
            self.blocchi.append({"t": self.tag if self.tag != "h4" else "h3", "x": testo})
        self.cur, self.tag = None, None

    def handle_data(self, data):
        if self.cur is not None:
            self.cur.append(data)


BOILERPLATE = re.compile(r"^(Check with your travel provider that your passport|You will be denied entry if you do not have a valid travel document|"
                         r"Renew your passport if you need to)", re.I)


def sezione(body):
    """Blocchi della sezione 'Passport validity requirements' (fino al titolo h2 successivo)."""
    p = Blocchi()
    p.feed(body)
    bb = p.blocchi
    idx = [i for i, b in enumerate(bb) if b["t"] == "h2" and "passport validity" in b["x"].lower()]
    titolo = None
    if not idx:
        idx = [i for i, b in enumerate(bb) if b["t"] == "h2" and "passport" in b["x"].lower()]
        if not idx:
            return None, []
    titolo = bb[idx[0]]["x"]
    out = []
    for b in bb[idx[0] + 1:]:
        if b["t"] == "h2":
            break
        out.append(b)
    return titolo, out


# ------------------------------------------------------------------ classificazione
NUMERI = {"one": 1, "two": 2, "three": 3, "four": 4, "six": 6}
NUM = r"(\d+|one|two|three|four|six)"
UNITA = r"(months?|days?)"
ARRIVO = r"(?:the (?:date|day) you (?:arrive|enter)|your date of entry|the date of arrival)"
PARTENZA = r"(?:the (?:date|day) you (?:plan to leave|leave|are leaving|intend to leave)|your planned departure date)"
SCHEMI = [  # (nome, regex, base)
    ("arrivo", re.compile(r"expiry date (?:that is |of )?(at least |more than )?" + NUM + " " + UNITA + " after " + ARRIVO), "arrivo"),
    ("arrivo", re.compile(r"valid for (at least )?" + NUM + " " + UNITA + " (?:from|after) " + ARRIVO), "arrivo"),
    ("partenza", re.compile(r"expiry date (?:that is |of )?(at least |more than )?" + NUM + " " + UNITA + " after " + PARTENZA), "partenza"),
    ("partenza", re.compile(r"valid for (at least )?" + NUM + " " + UNITA + " after " + PARTENZA), "partenza"),
    ("e_partenza", re.compile(r" and (\d+|one|two|three|six) " + UNITA + " after " + PARTENZA), "partenza"),
]
DOPO_PARTENZA = re.compile(r"expiry date after " + PARTENZA)
SOGGIORNO = re.compile(r"valid for the (?:proposed |planned )?(?:duration|length) of (?:your|their) (?:planned |proposed )?(?:stay|visit)")
EMISSIONE = re.compile(r"(date of issue less than 10 years before the date you (?:arrive|enter)|issued less than 10 years before the date you (?:arrive|enter)"
                       r"|issued within the previous 10 years)")
PARTENZA_10 = re.compile(r"(?:expiry date at least|validity must extend for at least) " + NUM + " " + UNITA + r" after the (?:date|day) you (?:plan|intend) to leave")
# frasi che riguardano altri gruppi (residenti, titolari di visto, transito): non sono la regola per chi visita
CONDIZIONALE = re.compile(r"^(if you(?:’re|'re| are)? (?:live|living|a resident|resident|have a residence|have a visa|have a long|apply|applying|travelling through|"
                          r"renew|also travelling)|if you’re (?:a resident|travelling through|applying|also travelling)|"
                          r"to enter [\w ]+ (?:as a resident|on a long-term visa)|many countries|the mexican embassy|some airlines)", re.I)
DUBBIO = re.compile(r"visa application|visa expires|visa’s expiry|visa's expiry|entry permit|recommend|up until|valid on entry|however|usually|plus an additional", re.I)
AVVISO = re.compile(r"recommend|airline|may refuse|many countries|refused boarding", re.I)
PAGINE = re.compile(r"(?:at least |have |with )?(\d+|one|two|three|four|a) (?:additional )?blank (?:consecutive )?pages?", re.I)


def norm(s):
    """Minuscole, senza virgolette o apostrofi, spazi singoli (solo per il confronto con gli schemi)."""
    s = re.sub(r"[‘’'“”]", "", s)
    return re.sub(r"\s+", " ", s.lower()).strip()


def frasi(testo):
    return [f.strip() for f in re.split(r"(?<=[.!?])\s+(?=[A-Z])", testo) if f.strip()]


def unisci(blocchi):
    """Unisce un paragrafo che finisce con ':' agli elementi di elenco che lo seguono (stessa frase)."""
    out, i = [], 0
    while i < len(blocchi):
        b = blocchi[i]
        if b["t"] in ("p", "li") and b["x"].rstrip().endswith(":"):
            parti = [b["x"].rstrip()]
            j = i + 1
            while j < len(blocchi) and (blocchi[j]["t"] == "li" or (blocchi[j]["t"] == "p" and re.match(r"^(have|an|a|be|valid|at least)\b", blocchi[j]["x"]))):
                parti.append(blocchi[j]["x"].rstrip(" .;"))
                j += 1
            out.append(parti[0] + " " + "; ".join(parti[1:]) + ".")
            i = j
        else:
            out.append(b["x"])
            i += 1
    return out


def condizione(m, base):
    g = m.groups()
    qual = (g[0] or "") if len(g) == 3 else ""
    n_txt = g[1] if len(g) == 3 else g[0]
    unita = g[2] if len(g) == 3 else g[1]
    n = int(n_txt) if n_txt.isdigit() else NUMERI[n_txt]
    return {"base": base, "n": n, "u": "m" if unita.startswith("month") else "g", "op": ">" if qual.strip() == "more than" else ">="}


def regole_in(frase_norm):
    """Tutte le condizioni riconosciute in una frase normalizzata (lista, vuota se nessuna)."""
    cond = []
    for nome, rx, base in SCHEMI:
        for m in rx.finditer(frase_norm):
            if nome == "e_partenza":
                n_txt, unita = m.group(1), m.group(2)
                n = int(n_txt) if n_txt.isdigit() else NUMERI[n_txt]
                cond.append({"base": "partenza", "n": n, "u": "m" if unita.startswith("month") else "g", "op": ">="})
            else:
                cond.append(condizione(m, base))
    if DOPO_PARTENZA.search(frase_norm):
        cond.append({"base": "partenza", "n": 0, "u": "g", "op": ">"})
    if SOGGIORNO.search(frase_norm):
        cond.append({"base": "partenza", "n": 0, "u": "g", "op": ">="})
    uniche = []
    for c in cond:
        if c not in uniche:
            uniche.append(c)
    return uniche


def classifica(blocchi):
    """Ritorna (regola o None, motivo se manuale, avvisi, pagine bianche)."""
    if not blocchi:
        return None, "The official page has no text under this heading.", [], None
    if blocchi[0]["t"] == "h3":
        return None, "The official page gives different rules for different territories.", [], None
    corpo = []
    for b in blocchi:
        if b["t"] == "h3":
            break
        corpo.append(b)
    righe = unisci(corpo)
    tutte = [f for r in righe for f in frasi(r)]
    avvisi = [f for f in tutte if AVVISO.search(f)]
    pagine = None
    for f in tutte:
        m = PAGINE.search(f)
        if m:
            pagine = m.group(0).strip()
            break
    testo_n = norm(" ".join(righe))
    # regola con data di emissione (Schengen e simili)
    if EMISSIONE.search(testo_n):
        m = PARTENZA_10.search(testo_n)
        if not m:
            return None, "Issue-date rule with an expiry condition we cannot read with confidence.", avvisi, pagine
        n = int(m.group(1)) if m.group(1).isdigit() else NUMERI[m.group(1)]
        cond = [{"base": "partenza", "n": n, "u": "m" if m.group(2).startswith("month") else "g", "op": ">="}]
        frase = next((f for f in tutte if "10 years" in f), tutte[0])
        return {"condizioni": cond, "emissione_anni": 10, "schengen": "schengen" in testo_n, "frase": frase}, None, avvisi, pagine
    principale = None
    for f in tutte:
        fn = norm(f)
        if "passport" in fn and ("valid" in fn or "expiry date" in fn) and not CONDIZIONALE.search(f.strip()):
            principale = f
            break
    if principale is None:
        return None, "No sentence states a validity period we can apply.", avvisi, pagine
    if DUBBIO.search(principale):
        return None, "The official sentence has conditions we do not turn into a calculation.", avvisi, pagine
    cond = regole_in(norm(principale))
    if not cond:
        return None, "The official sentence does not match a rule pattern we can apply with confidence.", avvisi, pagine
    # altre frasi con una regola diversa e non riferite ad altri gruppi -> manuale
    for f in tutte:
        if f is principale or CONDIZIONALE.search(f.strip()):
            continue
        altre = regole_in(norm(f))
        if altre and altre != cond:
            return None, "The official text contains more than one validity rule.", avvisi, pagine
    if any(c["u"] == "g" and c["n"] == 0 for c in cond) and len(cond) > 1:
        return None, "The official sentence combines rules we do not turn into a calculation.", avvisi, pagine
    return {"condizioni": cond, "emissione_anni": None, "schengen": False, "frase": principale}, None, avvisi, pagine


def solo_data(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc).date().isoformat()


def leggi_paese(slug, j):
    det = j["details"]
    nome = det.get("country", {}).get("name") or j["title"].replace(" travel advice", "")
    ent = [p for p in det.get("parts", []) if p["slug"] == "entry-requirements"]
    titolo, blocchi = sezione(ent[0]["body"]) if ent else (None, [])
    blocchi = [b for b in blocchi if not BOILERPLATE.match(b["x"])]
    regola, motivo, avvisi, pagine = classifica(blocchi) if titolo and "passport validity" in titolo.lower() else (
        None, "The official page has no 'Passport validity requirements' section." + (f" The text below is from '{titolo}'." if titolo else ""), [], None)
    storia = det.get("change_history", [])
    ingresso = [{"data": solo_data(c["public_timestamp"]), "nota": c["note"]} for c in storia if "entry requirements" in c["note"].lower()][:5]
    return {
        "slug": slug, "nome": nome, "url": "https://www.gov.uk/foreign-travel-advice/" + slug,
        "url_ingresso": "https://www.gov.uk/foreign-travel-advice/" + slug + "/entry-requirements",
        "api": API + "/" + slug,
        "aggiornata": solo_data(j["public_updated_at"]),
        "ultimo_cambio": {"data": solo_data(storia[0]["public_timestamp"]), "nota": storia[0]["note"]} if storia else None,
        "cambi_ingresso": ingresso,
        "titolo_sezione": titolo,
        "testo": blocchi,
        "regola": regola,
        "stato": "auto" if regola else "manuale",
        "motivo": motivo,
        "avvisi": avvisi,
        "pagine_bianche": pagine,
    }


def main():
    oggi = date.today().isoformat()
    indice = scarica(API, "_indice.json")
    figli = indice["links"]["children"]
    paesi, errori = [], []
    for c in figli:
        slug = c["base_path"].rsplit("/", 1)[-1]
        try:
            j = scarica(API + "/" + slug, slug + ".json")
            paesi.append(leggi_paese(slug, j))
        except Exception as e:  # noqa: BLE001
            errori.append(f"{slug}: {e}")
        if not OFFLINE:
            time.sleep(0.2)
    paesi.sort(key=lambda p: p["nome"].lower())
    print(f"Pagine lette: {len(paesi)} su {len(figli)}; errori: {len(errori)}")
    for e in errori:
        print("  ERRORE", e)
    if len(paesi) < MINIMO_PAGINE:
        print("Troppe pagine non lette: dati/passaporti.json NON aggiornato.")
        sys.exit(1)
    file = DATI / "passaporti.json"
    vecchio = json.loads(file.read_text(encoding="utf-8")) if file.exists() else None
    nuovo = {"fonte": "GOV.UK Content API – FCDO foreign travel advice", "fonte_url": API,
             "licenza": "Open Government Licence v3.0",
             "licenza_url": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
             "controllato_il": oggi, "pagine_indice": len(figli), "paesi": paesi}
    if vecchio:
        prima = {p["slug"]: p for p in vecchio["paesi"]}
        cambi_file = DATI / "passaporti_cambi.json"
        storico = json.loads(cambi_file.read_text(encoding="utf-8")) if cambi_file.exists() else {"cambi": []}
        nuovi = 0
        for p in paesi:
            q = prima.get(p["slug"])
            if q and [b["x"] for b in q["testo"]] != [b["x"] for b in p["testo"]]:
                storico["cambi"].insert(0, {"rilevato_il": oggi, "slug": p["slug"], "nome": p["nome"],
                                            "prima": [b["x"] for b in q["testo"]], "dopo": [b["x"] for b in p["testo"]]})
                nuovi += 1
        if nuovi:
            cambi_file.write_text(json.dumps(storico, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Testi cambiati rispetto al file precedente: {nuovi}")
    file.write_text(json.dumps(nuovo, ensure_ascii=False, indent=1), encoding="utf-8")
    auto = sum(1 for p in paesi if p["stato"] == "auto")
    print(f"Regole lette in automatico: {auto}; da leggere sulla frase ufficiale: {len(paesi) - auto}")
    for p in paesi:
        if p["stato"] != "auto":
            print(f"  manuale: {p['nome']}: {p['motivo']}")


if __name__ == "__main__":
    main()
