"""Passaporto CANADESE: scarica dal Government of Canada (Global Affairs Canada) le sezioni "Entry and exit requirements"
di ogni destinazione e scrive dati/passaporti_ca.json.

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/passaporti_ca.py              # scarica le pagine nuove o più vecchie di 20 ore (circa 230 richieste)
    BYF_OFFLINE=1 python3 -I beforeyoufly/raccolta/passaporti_ca.py   # rilegge solo la cache, senza rete
    BYF_CACHE_ORE=0 python3 -I beforeyoufly/raccolta/passaporti_ca.py # riscarica tutto

Fonte (open data ufficiale, dataset "Country Travel Advice and Advisories" su open.canada.ca):
    indice:   https://data.international.gc.ca/travel-voyage/index-alpha-eng.json   (230 destinazioni, data di pubblicazione)
    paese:    https://data.international.gc.ca/travel-voyage/cta-cap-<ISO>.json      (campo eng.entry-exit = stessa sezione della pagina)
    pagina:   https://travel.gc.ca/destinations/<slug>                              (link mostrato sul sito)
Licenza: Open Government Licence – Canada 2.0 (https://open.canada.ca/en/open-government-licence-canada), riuso anche commerciale con
la frase "Contains information licensed under the Open Government Licence – Canada"; la licenza vieta di far credere a un'approvazione ufficiale.

Cache e ripresa: ogni JSON grezzo va in raccolta/.cache/ca/ (fuori dal repository, vedi beforeyoufly/.gitignore). Se lo script si interrompe,
al giro dopo riusa i file già scaricati da meno di BYF_CACHE_ORE ore (20 per default) e scarica solo gli altri.
Controllo minimo: se legge meno dell'80 % delle destinazioni dell'indice, dati/passaporti_ca.json NON viene sovrascritto (esce con 1).
Le differenze di testo rispetto al file precedente vanno in dati/passaporti_ca_cambi.json.

Riassunti (stessa prudenza del passaporto britannico, raccolta/passaporti.py, con le lezioni della revisione del 17/10/2026):
  - si salva SEMPRE il testo ufficiale parola per parola; il sito lo mostra tra virgolette;
  - validità: riassunto di una riga SOLO se la prima frase sotto "Regular Canadian passport" corrisponde per intero a uno di SCHEMI_VALIDITA
    e parla della destinazione della pagina; se il testo aggiunge altre frasi, il riassunto lo dice;
  - visto: riassunto SOLO se la prima riga della sezione "Visas" è "Tourist visa: not required for stays up to N days ..." / "Tourist visa: not
    required" / "Tourist visa: required" (SCHEMI_VISTO), senza parole di dubbio nella sezione ("until", "temporar", "suspend", asterischi che
    non siano la nota Schengen) e, se la sezione d'ingresso parla di eTA/ETA/eVisa/arrival card/moduli o registrazione online/tessera turistica/
    tassa d'ingresso, NESSUN riassunto (unica eccezione: ETIAS, solo se la sezione ETIAS dice che servirà, "You will be required to apply
    online and pay for an ETIAS before you travel", e "Applications are not yet open.": il riassunto dice entrambe le cose).
"""
import json
import os
import re
import sys
import time
import unicodedata
import urllib.request
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
CACHE = Path(os.environ.get("BYF_CACHE") or (RADICE / "raccolta" / ".cache" / "ca"))
OFFLINE = os.environ.get("BYF_OFFLINE") == "1"
CACHE_ORE = float(os.environ.get("BYF_CACHE_ORE", "20"))
BASE = "https://data.international.gc.ca/travel-voyage/"
INDICE = BASE + "index-alpha-eng.json"
PAGINA = "https://travel.gc.ca/destinations/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
QUOTA_MINIMA = 0.8
LICENZA = "Open Government Licence – Canada"
LICENZA_URL = "https://open.canada.ca/en/open-government-licence-canada"
DATASET_URL = "https://open.canada.ca/data/en/dataset/bef2ebb3-ca9a-485f-aaff-5dc36eb89426"


def scarica(url, nome):
    """JSON da url, con cache su disco (ripresa) e 4 tentativi."""
    f = CACHE / nome
    if f.exists() and (OFFLINE or time.time() - f.stat().st_mtime < CACHE_ORE * 3600):
        return json.loads(f.read_text(encoding="utf-8")), False
    if OFFLINE:
        raise FileNotFoundError(f"{nome} non è in cache")
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    for tentativo in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                corpo = r.read()
            j = json.loads(corpo)
            CACHE.mkdir(parents=True, exist_ok=True)
            f.write_bytes(corpo)
            return j, True
        except Exception:  # noqa: BLE001
            if tentativo == 3:
                raise
            time.sleep(3 + tentativo * 4)


# ------------------------------------------------------------------ HTML -> blocchi di testo
class Blocchi(HTMLParser):
    """Paragrafi, voci di elenco e titoli; un <br> dentro un paragrafo separa due righe (come sulla pagina, dove sono paragrafi distinti).
    Anche i <div> con testo sono righe: alcune pagine (Liberia, Saint-Barthélemy, Serbia, El Salvador) mettono lì le righe dei visti o una
    frase sul passaporto, che senza "div" andavano perse (revisione del 17/10/2026)."""
    TAG = ("p", "li", "h2", "h3", "h4", "h5", "div")

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocchi, self.cur, self.tag = [], None, None

    def handle_starttag(self, tag, attrs):
        if tag in self.TAG:
            if self.cur is not None:
                self._chiudi()
            self.cur, self.tag = [], tag
        elif tag == "br" and self.cur is not None:
            t = self.tag
            self._chiudi()
            self.cur, self.tag = [], t

    def handle_endtag(self, tag):
        if tag == self.tag and self.cur is not None:
            self._chiudi()

    def _chiudi(self):
        testo = re.sub(r"\s+", " ", "".join(self.cur).replace("\xa0", " ")).strip()
        if testo:
            self.blocchi.append({"t": {"h5": "h4", "div": "p"}.get(self.tag, self.tag), "x": testo})
        self.cur, self.tag = None, None

    def handle_data(self, data):
        if self.cur is not None:
            self.cur.append(data)


def blocchi(html):
    p = Blocchi()
    p.feed(html or "")
    if p.cur is not None:
        p._chiudi()
    return p.blocchi


def sezioni(bb):
    """[(titolo h3, [blocchi])]; i blocchi prima del primo h3 hanno titolo None."""
    out = []
    for b in bb:
        if b["t"] in ("h2", "h3"):
            out.append([b["x"], []])
            continue
        if not out:
            out.append([None, []])
        out[-1][1].append(b)
    return out


def sottosezione(bb, inizio):
    """Blocchi sotto il titolo h4 che comincia con `inizio`, fino al titolo h4 successivo."""
    out, dentro = [], False
    for b in bb:
        if b["t"] == "h4":
            if dentro:
                break
            dentro = b["x"].startswith(inizio)
            continue
        if dentro:
            out.append(b)
    return out


def frasi(testo):
    """Frasi di un paragrafo (non spezza dopo 'U.S.')."""
    t = testo.replace("U.S.", "U\u2024S\u2024")
    return [f.strip().replace("U\u2024S\u2024", "U.S.") for f in re.split(r"(?<=[.!?])\s+(?=[A-Z])", t) if f.strip()]


def piano(s):
    return re.sub(r"[‘’]", "'", s).replace("“", '"').replace("”", '"')


# ------------------------------------------------------------------ nome della destinazione nelle frasi
ALIAS = {  # nomi con cui il testo ufficiale chiama la destinazione (controllati a mano il 17/10/2026)
    "CD": ["DRC", "the Democratic Republic of the Congo"], "CG": ["the Republic of the Congo"], "TR": ["Türkiye"],
    "PS": ["Israel, the West Bank or the Gaza Strip"], "IL": ["Israel, the West Bank or the Gaza Strip"],
    "BS": ["The Bahamas", "the Bahamas"], "FM": ["Micronesia"], "US": ["the United States"], "GB": ["the United Kingdom"],
    "VI": ["the U.S. Virgin Islands"], "MP": ["the Northern Mariana Islands"], "CI": ["Côte d'Ivoire"], "GM": ["The Gambia", "the Gambia"],
    "TL": ["Timor-Leste"], "PM": ["Saint Pierre and Miquelon"], "VC": ["Saint Vincent and the Grenadines"], "KN": ["Saint Kitts and Nevis"],
    "MF": ["Saint Martin"], "BL": ["Saint Barthélemy"], "LC": ["Saint Lucia"], "SX": ["Sint Maarten"], "CV": ["Cabo Verde"],
    "GI": ["Gibraltar or the Schengen area"],
}
SCHENGEN = "the Schengen area"  # accettato come destinazione solo se la pagina ha la sezione "Schengen area"
GENERICI = ["the country"]  # "your date of entry into the country": parla della destinazione della pagina


def _n(s):
    s = unicodedata.normalize("NFKD", piano(s)).encode("ascii", "ignore").decode().strip().lower()
    return s[4:] if s.startswith("the ") else s


def nome_ok(x, nome, iso, schengen=False):
    if x is None:
        return False
    cand = [nome] + ALIAS.get(iso, []) + GENERICI + ([SCHENGEN] if schengen else [])
    return _n(x) in {_n(c) for c in cand}


# ------------------------------------------------------------------ validità del passaporto
NUM = r"(?P<n>\d+|one|two|three|six)"
UNI = r"(?P<u>months?|days?)"
QUAL = r"(?P<q>for at least |at least |for a minimum of |a minimum of |for )?"
X = r"(?P<x>[^.]+?)"
PAGINE_CODA = (r"(?P<coda>(?:,)? and (?:be in good condition|(?:have|must contain|contain|include|should have) (?:at least |a least )?(?:one|1|two|2|three|3) "
               r"(?:blank|empty) (?:visa )?pages?(?: for (?:an entry stamp|entry stamps|use by immigration officials|the placement of [^.]+))?))?")
SCHEMI_VALIDITA = [  # (nome, regex sulla prima frase intera, base: partenza / arrivo / soggiorno)
    ("dopo_partenza", re.compile(r"^Your passport must be valid " + QUAL + NUM + " " + UNI + r" (?:beyond|after) the date you expect to leave (?:from )?" + X + PAGINE_CODA + r"\.$"), "partenza"),
    ("dopo_partenza", re.compile(r"^Your passport must be valid " + QUAL + NUM + " " + UNI + r" beyond the date of expected departure from " + X + PAGINE_CODA + r"\.$"), "partenza"),
    ("da_arrivo", re.compile(r"^Your passport must be valid " + QUAL + NUM + " " + UNI + r" (?:beyond|after|from) (?:the date you (?:arrive in|enter)|your date of (?:arrival in|entry into|entry in)"
                             r"|the date of (?:your arrival in|entry into|entry to)) " + X + PAGINE_CODA + r"\.?$"), "arrivo"),
    ("da_arrivo", re.compile(r"^Your passport must be valid " + QUAL + NUM + " " + UNI + r" from (?:the|your) date of entry" + PAGINE_CODA + r"\.$"), "arrivo"),
    ("da_arrivo", re.compile(r"^Your passport must be valid " + QUAL + NUM + " " + UNI + r" (?:upon entry into|upon entering|at the time of arrival in) " + X + PAGINE_CODA + r"\.$"), "arrivo"),
    ("soggiorno", re.compile(r"^Your passport must be valid for (?P<al>at least )?the (?P<exp>expected )?duration of your stay(?: in " + X + r")?" + PAGINE_CODA + r"\.$"), "soggiorno"),
    ("oltre_partenza", re.compile(r"^Your passport must be valid beyond the date of expected departure from " + X + r"\.$"), "partenza"),
]
NUMERI = {"one": "1", "two": "2", "three": "3", "six": "6"}


def sintesi_validita(testo, nome, iso, schengen=False):
    """Ritorna (schema, sintesi, breve, frase, motivo) per i blocchi sotto 'Regular Canadian passport'."""
    if not testo:
        return None, None, None, None, "The Government of Canada page has no 'Regular Canadian passport' text."
    primo = testo[0]["x"]
    ff = frasi(primo)
    frase = ff[0] if ff else primo
    altro = len(ff) > 1 or len(testo) > 1
    for nome_schema, rx, base in SCHEMI_VALIDITA:
        m = rx.match(piano(frase))
        if not m:
            continue
        g = m.groupdict()
        if g.get("x") is not None and not nome_ok(g["x"], nome, iso, schengen):
            return None, None, None, frase, "The official sentence is not about this destination."
        x = g.get("x")
        if x and _n(x) in {_n(c) for c in GENERICI}:  # "the country" -> nome della destinazione, con l'articolo se serve (the Marshall Islands)
            x = ("the " + nome) if (nome.endswith(("Islands", "Isles")) or nome.startswith("United ")) and not nome.startswith("The ") else nome
        coda = (g.get("coda") or "").lstrip(",")
        if nome_schema == "soggiorno":
            s = f"Valid for {g.get('al') or ''}the {g.get('exp') or ''}duration of your stay" + (f" in {x}" if x else "")
            breve = "Valid for the whole stay"
        elif nome_schema == "oltre_partenza":
            s = f"Valid beyond the date you expect to leave {x}"
            breve = "Valid beyond departure"
        else:
            n = NUMERI.get(g["n"], g["n"])
            u = g["u"].rstrip("s") + ("" if n == "1" else "s")
            q = g.get("q") or ""  # "for at least", "at least", "for a minimum of"... come nella frase ufficiale
            if base == "partenza":
                s = f"Valid {q}{n} {u} beyond the date you expect to leave {x}"
                breve = f"{n} {u} after leaving the Schengen area" if _n(x) == _n(SCHENGEN) else f"{n} {u} after departure"
            else:
                s = f"Valid {q}{n} {u} from the date you enter" + (f" {x}" if x else "")
                breve = f"{n} {u} from arrival"
        if coda:
            s += "," + coda
        if altro:
            s += " (the official text adds more details)"
        s = s[0].upper() + s[1:]
        return nome_schema, s, breve, frase, None
    return None, None, None, frase, "The official sentence does not match a wording we summarise."


# ------------------------------------------------------------------ visti
V_PER = r"(?P<per> in any \d+-day period| in a \d+-day period| in a 180 day period| within any \d+-day period| within a \d+-day period)?"
SCHEMI_VISTO = [
    ("senza_visto_durata", re.compile(r"^Tourist visa: [Nn]ot required for (?:stays (?P<of>of )?)?(?P<q>up to a maximum of|up to|less than|fewer than) (?P<n>\d+|six) (?P<u>days|months|weeks)"
                                      + V_PER + r"(?P<ast>\*)?$")),
    ("senza_visto_durata", re.compile(r"^Tourist visa: [Nn]ot required for stays (?:of )?(?P<n>\d+) (?P<u>days|months) (?P<q2>or less)" + V_PER + r"(?P<ast>\*)?$")),
    ("senza_visto", re.compile(r"^Tourist visa: [Nn]ot required$")),
    ("visto_richiesto", re.compile(r"^Tourist visa: required$")),
]
# nella sezione "Visas": parole che rendono la riga non inequivocabile
MESE = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
DUBBIO_VISTO = re.compile(r"\buntil " + MESE + r"|\b(?:from|between|since|as of|starting|effective) " + MESE + r" \d|\b\d{1,2} " + MESE + r" \d{4}|temporarily (?:suspend|waive|exempt|extend|allow)"
                          r"|suspend|\bpilot\b|trial period|visa waiver (?:program|scheme) (?:is|has been) (?:extended|introduced)", re.I)
NOTA_SCHENGEN = "* The 90-day period begins upon initial entry into any country of the Schengen area. Stays are cumulative and include visits to any Schengen area country within any 180-day period."
# in TUTTA la sezione d'ingresso: autorizzazioni, visti elettronici, moduli e registrazioni prima dell'arrivo, tessere, tasse
AUTORIZZAZIONE = re.compile(r"\b(?:ETA|eTA|ESTA|NZeTA|K-ETA|ETIAS|EVW|ED Card)\b|travel authori[sz]ation|electronic (?:travel|visa|immigration|arrival)|\be-?visa|\beVisa"
                            r"|arrival card|e-arrival|arrival declaration|declaration form|immigration form|embarkation|landing card|tourist card|migration card"
                            r"|entry fee|entry tax|tourism fee|tourist tax|visitor permit|pre-?regist|pre-?arrival|register online|online registration|e-?Travel"
                            r"|online visa|visa online|application online|visa portal"
                            r"|(?:apply|register|fill out|complete|submit)[^.]{0,40}\bonline\b|online (?:form|application|platform|portal)|QR code|mandatory registration|Irembo", re.I)
ETIAS_NON_APERTO = "Applications are not yet open."
ETIAS_FUTURO = "You will be required to apply online and pay for an ETIAS before you travel"  # stessa sezione: ETIAS servirà, ma non è ancora aperto
ETIAS_CODA = "; ETIAS will be required, but “Applications are not yet open”, says the same page"
# "Tourist visa: required" ma il visto si ottiene all'arrivo (o il testo ne parla): il riassunto non lo direbbe, quindi niente riassunto
ALL_ARRIVO = re.compile(r"on arrival|upon arrival|at the airport|ports? of entry|points? of entry", re.I)
SENZA_DURATA = " (read the official text for how long you can stay)"


def testo_sezione(ss):
    return " ".join(b["x"] for _, bb in ss for b in bb) + " " + " ".join(t or "" for t, _ in ss)


def sintesi_visto(visti, ss):
    """Ritorna (schema, sintesi, frase, motivo). visti = blocchi della sezione 'Visas'; ss = tutte le sezioni d'ingresso."""
    if not visti:
        return None, None, None, "The Government of Canada page has no 'Visas' section."
    frase = visti[0]["x"]
    riga = piano(frase).strip()
    tutto_visti = " ".join(b["x"] for b in visti)
    for nome_schema, rx in SCHEMI_VISTO:
        m = rx.match(riga)
        if not m:
            continue
        g = m.groupdict()
        if DUBBIO_VISTO.search(tutto_visti):
            return None, None, frase, "The official visa text has a time limit or exception we do not summarise."
        schengen = False
        if g.get("ast"):
            if NOTA_SCHENGEN not in [b["x"] for b in visti]:
                return None, None, frase, "The official visa line has a footnote with conditions we do not summarise."
            schengen = True
        # autorizzazioni e moduli in tutta la sezione "Entry and exit requirements"; la sezione ETIAS è tolta dalla ricerca solo se dice
        # "Applications are not yet open." (e allora il riassunto lo dice)
        etias = [(t, b) for t, b in ss if t and "ETIAS" in t and any(ETIAS_NON_APERTO in x["x"] and ETIAS_FUTURO in x["x"] for x in b)]
        resto = [(t, b) for t, b in ss if (t, b) not in etias]
        if AUTORIZZAZIONE.search(testo_sezione(resto)):
            return None, None, frase, ("The official text also mentions an electronic travel authorization, e-visa, arrival card, "
                                       "online form or registration, tourist card or fee: read it in full.")
        if nome_schema == "visto_richiesto" and ALL_ARRIVO.search(tutto_visti):
            return None, None, frase, "The official visa text talks about getting a visa on arrival or at the border: read it in full."
        if etias and not nome_schema.startswith("senza_visto"):
            return None, None, frase, "The official text mentions ETIAS: read it in full."
        if nome_schema == "senza_visto_durata":
            if g.get("q2"):
                s = f"Tourist visa not required for stays of {g['n']} {g['u']} or less{g.get('per') or ''}"
            else:
                s = f"Tourist visa not required for stays {g.get('of') or ''}{g['q']} {g['n']} {g['u']}{g.get('per') or ''}"
            if schengen:  # nota Schengen: "... include visits to any Schengen area country within any 180-day period"
                s += ", counted across the whole Schengen area" if g.get("per") else " within any 180-day period, counted across the whole Schengen area"
        elif nome_schema == "senza_visto":
            s = "Tourist visa not required" + SENZA_DURATA
        else:
            s = "Tourist visa required"
        if etias:
            s += ETIAS_CODA
        return nome_schema, s, frase, None
    return None, None, frase, "The official visa text does not match a wording we summarise."


# ------------------------------------------------------------------ lettura di una destinazione
NON_MOSTRARE = re.compile(r"^(Children and travel|Yellow fever)$", re.I)
VISIBILI = re.compile(r"authori[sz]ation|ETIAS|\bETA\b|\be-?visa|arrival|declaration|immigration form|tourist card|migration card|ED Card|registration|"
                      r"entry stamp|length of stay|schengen|EES|fee|tax|permit|insurance|exit", re.I)


def data_friendly(s):
    """'October 13, 2026 14:27 EDT' -> '2026-10-13' (data come la mostra la pagina, ora di Ottawa)."""
    m = re.match(r"([A-Z][a-z]+) (\d{1,2}), (\d{4})", s or "")
    return datetime.strptime(" ".join(m.groups()), "%B %d %Y").date().isoformat() if m else None


TITOLO_VISTI = re.compile(r"^Visas?$|^Passport and visas$|^Visas and other entry requirements$")  # Guam: "Visas and other entry requirements"
TITOLO_GENERALE = "Passport"
MOTIVO_GENERALE = ("The Government of Canada page has no separate paragraph for regular Canadian passports: we quote its “Passport” section, "
                   "which gives the documents and validity by type of travel.")


def passaporto_generale(pas):
    """Pagine senza il sottotitolo "Regular Canadian passport" (Stati Uniti): i blocchi della sezione "Passport" fino a "Passport for official
    travel" (o ai sottotitoli comuni a tutte le pagine), senza gli elenchi "Useful links"."""
    out, salta = [], False
    for b in pas:
        if b["t"] == "h4":
            if b["x"].startswith(("Passport for official travel", "Passport with", "Other travel documents")):
                break
            salta = b["x"].strip().lower() == "useful links"
            if salta:
                continue
        elif salta and b["t"] == "li":
            continue
        else:
            salta = False
        out.append(b)
    return out


def calcola_validita(testo, titolo, nome, iso, schengen=False):
    """Come sintesi_validita, ma senza riassunto se il testo non è quello sotto "Regular Canadian passport" (verifica.py usa questa)."""
    if testo and titolo != "Regular Canadian passport":
        return None, None, None, None, MOTIVO_GENERALE
    return sintesi_validita(testo, nome, iso, schengen)


def leggi_paese(iso, j, voce_indice):
    e = j["data"]["eng"]
    nome = e["name"]
    bb = blocchi(e.get("entry-exit"))
    ss = sezioni(bb)
    pas = next((b for t, b in ss if t and t.lower().startswith("passport")), None)
    if pas is None:  # due pagine hanno i sottotitoli del passaporto senza il titolo "Passport"
        pas = next((b for t, b in ss if any(x["t"] == "h4" and x["x"].startswith("Regular Canadian passport") for x in b)), [])
    regolare = sottosezione(pas, "Regular Canadian passport")
    titolo_pas = "Regular Canadian passport"
    if not regolare and pas and not any(t and TITOLO_VISTI.match(t) for t, b in ss if b is pas):  # Antartide: "Passport and visas" è la sezione dei visti
        regolare, titolo_pas = passaporto_generale(pas), TITOLO_GENERALE
    schengen = any(t and t.strip().lower() == "schengen area" for t, _ in ss)
    v_schema, v_sint, v_breve, v_frase, v_motivo = calcola_validita(regolare, titolo_pas, nome, iso, schengen)
    visti = next((b for t, b in ss if t and TITOLO_VISTI.match(t)), [])
    s_schema, s_sint, s_frase, s_motivo = sintesi_visto(visti, ss)
    altre = [{"titolo": t, "testo": b, "visibile": bool(VISIBILI.search(t + " " + " ".join(x["x"] for x in b[:2]))) or bool(AUTORIZZAZIONE.search(" ".join(x["x"] for x in b)))}
             for t, b in ss if t and not TITOLO_VISTI.match(t) and not t.startswith("Passport") and not NON_MOSTRARE.match(t) and b]
    return {
        "iso": iso, "nome": nome, "slug_fonte": e["url-slug"], "url": PAGINA + e["url-slug"],
        "api": f"{BASE}cta-cap-{iso}.json",
        "aggiornata": data_friendly(e.get("friendly-date")) or voce_indice["date-published"]["date"][:10],
        "livello": e.get("advisory-text"),
        "passaporto": {"titolo_sezione": titolo_pas, "testo": regolare, "frase": v_frase, "schema": v_schema,
                       "sintesi": v_sint, "breve": v_breve, "motivo": v_motivo},
        "schengen": schengen,
        "visto": {"titolo_sezione": next((t for t, b in ss if b is visti), "Visas") if visti else None, "testo": visti, "frase": s_frase,
                  "schema": s_schema, "sintesi": s_sint, "motivo": s_motivo},
        "altre_sezioni": altre,
        "ingresso": bb,  # tutta la sezione "Entry and exit requirements", parola per parola (verifica.py ricalcola i riassunti da qui)
    }


def main():
    oggi = date.today().isoformat()
    indice, _ = scarica(INDICE, "_indice.json")
    voci = indice["data"]
    paesi, errori, scaricati = [], [], 0
    for iso, v in voci.items():
        try:
            j, nuovo = scarica(f"{BASE}cta-cap-{iso}.json", f"cta-cap-{iso}.json")
            scaricati += nuovo
            paesi.append(leggi_paese(iso, j, v))
            if nuovo:
                time.sleep(0.4)
        except Exception as e:  # noqa: BLE001
            errori.append(f"{iso}: {e}")
    paesi.sort(key=lambda p: p["nome"].lower())
    print(f"Destinazioni lette: {len(paesi)} su {len(voci)} (scaricate ora: {scaricati}, dalla cache: {len(paesi) - scaricati}); errori: {len(errori)}")
    for e in errori:
        print("  ERRORE", e)
    if len(paesi) < QUOTA_MINIMA * len(voci):
        print("Troppe destinazioni non lette: dati/passaporti_ca.json NON aggiornato.")
        sys.exit(1)
    file = DATI / "passaporti_ca.json"
    vecchio = json.loads(file.read_text(encoding="utf-8")) if file.exists() else None
    nuovo = {"fonte": "Government of Canada – Travel advice and advisories (Global Affairs Canada), open data",
             "fonte_url": INDICE, "dataset_url": DATASET_URL, "pagina_url": "https://travel.gc.ca/travelling/advisories",
             "licenza": LICENZA, "licenza_url": LICENZA_URL,
             "attribuzione": "Contains information licensed under the Open Government Licence – Canada.",
             "indice_generato": indice.get("metadata", {}).get("generated", {}).get("date"),
             "controllato_il": oggi, "pagine_indice": len(voci), "paesi": paesi}
    if vecchio:
        prima = {p["iso"]: p for p in vecchio["paesi"]}
        cambi_file = DATI / "passaporti_ca_cambi.json"
        storico = json.loads(cambi_file.read_text(encoding="utf-8")) if cambi_file.exists() else {"cambi": []}
        n = 0
        for p in paesi:
            q = prima.get(p["iso"])
            for sez in ("passaporto", "visto"):
                if q and [b["x"] for b in q[sez]["testo"]] != [b["x"] for b in p[sez]["testo"]]:
                    storico["cambi"].insert(0, {"rilevato_il": oggi, "iso": p["iso"], "nome": p["nome"], "sezione": sez,
                                                "prima": [b["x"] for b in q[sez]["testo"]], "dopo": [b["x"] for b in p[sez]["testo"]]})
                    n += 1
        if n:
            cambi_file.write_text(json.dumps(storico, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Testi cambiati rispetto al file precedente: {n}")
    file.write_text(json.dumps(nuovo, ensure_ascii=False, indent=1), encoding="utf-8")
    va = sum(1 for p in paesi if p["passaporto"]["sintesi"])
    vv = sum(1 for p in paesi if p["visto"]["sintesi"])
    print(f"Validità: {va} riassunti, {sum(1 for p in paesi if p['passaporto']['testo']) - va} solo citazione, "
          f"{sum(1 for p in paesi if not p['passaporto']['testo'])} senza testo")
    print(f"Visti: {vv} riassunti, {sum(1 for p in paesi if p['visto']['testo']) - vv} solo citazione, {sum(1 for p in paesi if not p['visto']['testo'])} senza sezione")


if __name__ == "__main__":
    main()
