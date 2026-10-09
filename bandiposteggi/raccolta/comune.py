"""Funzioni comuni per la raccolta degli avvisi sui posteggi (BandiPosteggi).

- `scarica(url, dest)`: richiesta HTTP educata (User-Agent identificabile,
  una richiesta ogni 1,5 secondi, 3 tentativi) con salvataggio su disco.
- `testo_pdf(percorso)`: estrae il testo di un PDF con pdfplumber.
- `estrai_campi(testo)`: euristiche (espressioni regolari) per tipo, numero
  posteggi e scadenza delle domande. Sono volutamente semplici: il test serve
  a misurare quanto rende un'estrazione automatica senza intervento umano.

I file scaricati sono dati non fidati: vanno salvati in una cartella dedicata
(fuori dal repository) e letti solo come testo.
"""
import os
import re
import time
import unicodedata
import urllib.parse
import urllib.request

UA = "BandiPosteggi-test/0.1 (ricerca di fattibilita' sugli avvisi pubblici; una richiesta ogni 1,5 s)"
PAUSA = 1.5
_ultimo = [0.0]


def scarica(url, dest=None, tentativi=3, timeout=60):
    """Scarica `url`; restituisce (status, content_type, bytes). Salva in `dest` se dato."""
    errore = None
    for n in range(tentativi):
        attesa = PAUSA - (time.time() - _ultimo[0])
        if attesa > 0:
            time.sleep(attesa)
        _ultimo[0] = time.time()
        req = urllib.request.Request(_quota(url), headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                dati = r.read()
                if dest:
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    with open(dest, "wb") as f:
                        f.write(dati)
                return r.status, r.headers.get("Content-Type", ""), dati
        except urllib.error.HTTPError as e:
            return e.code, e.headers.get("Content-Type", "") if e.headers else "", b""
        except Exception as e:  # reset di connessione, timeout
            errore = e
            time.sleep(3 * (n + 1))
    return 0, str(errore), b""


def _quota(url):
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit(p._replace(path=urllib.parse.quote(urllib.parse.unquote(p.path), safe="/%:@!$&'()*+,;=-._~")))


def testo_pdf(percorso, max_pagine=12):
    """Testo di un PDF (prime `max_pagine` pagine). Stringa vuota se illeggibile/scansione."""
    import pdfplumber
    try:
        with pdfplumber.open(percorso) as pdf:
            return "\n".join((p.extract_text() or "") for p in pdf.pages[:max_pagine])
    except Exception:
        return ""


def normalizza(t):
    t = unicodedata.normalize("NFKC", t or "")
    t = t.replace("’", "'").replace(" ", " ")
    return re.sub(r"[ \t]+", " ", t)


PAROLE_CHIAVE = re.compile(
    r"posteggi|posteggio|aree pubbliche|area pubblica|commercio ambulante|ambulant|"
    r"\bmercat[oi]\b|\bfier[ae]\b|chiosc|edicol|\bspunta|spuntist|sagr[ae]|food truck|"
    r"mercatin|banchi", re.I)
ESCLUDI = re.compile(r"indagine di mercato|prezzi di mercato|valore di mercato|edicola digitale|"
                     r"mercato elettronico|mercato del lavoro|alloggi", re.I)

MESI = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6, "luglio": 7,
        "agosto": 8, "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12}
_DATA = r"(\d{1,2})[./\-](\d{1,2})[./\-](\d{2,4})|(\d{1,2})°?\s+(" + "|".join(MESI) + r")\s+(\d{4})"
_RX_DATA = re.compile(_DATA, re.I)


def _data_iso(m):
    if m.group(1):
        g, me, a = int(m.group(1)), int(m.group(2)), int(m.group(3))
    else:
        g, me, a = int(m.group(4)), MESI[m.group(5).lower()], int(m.group(6))
    if a < 100:
        a += 2000
    if not (1 <= me <= 12 and 1 <= g <= 31 and 2025 <= a <= 2028):
        return None
    return f"{a:04d}-{me:02d}-{g:02d}"


_GIORNO = r"(?:(?:lunedi|lunedì|martedi|martedì|mercoledi|mercoledì|giovedi|giovedì|venerdi|venerdì|sabato|domenica)\s+)?"
_ORE = r"(?:(?:alle|delle|entro le|le)?\s*ore\s*\d{1,2}(?:[.:,]\d{2})?\s*(?:del|di)?\s*)?"
_D = r"(\d{1,2}[./\-]\d{1,2}[./\-]\d{2,4}|\d{1,2}°?\s+(?:" + "|".join(MESI) + r")\s+\d{4})"
_PREP = r"(?:il\s+|al\s+|giorno\s+|del\s+|data\s+)*"
# in ordine di affidabilità: la prima regola che trova una data vince
_REGOLE_SCAD = [
    re.compile(r"(?:entro|non oltre|scadenza|termine perentorio|termine ultimo|termine)[^.;]{0,90}?" + _ORE + _PREP + _GIORNO + _PREP + _D, re.I),
    re.compile(r"(?:fino|sino)\s+(?:a|al|alle)\s+" + _ORE + _PREP + _GIORNO + _PREP + _D, re.I),
    re.compile(r"dal\s+(?:giorno\s+)?" + _GIORNO + r"\d{1,2}[^.;]{0,30}?\s+al\s+" + _PREP + _GIORNO + _D, re.I),
]
_CONTESTO = re.compile(r"domand|istanz|candidatur|partecipaz|richiest|manifestazion|present|pervenir|inoltr|trasmess|invia", re.I)


def estrai_scadenza(testo):
    """Data di scadenza delle domande (ISO) o None.

    Cerca, in ordine: 'entro/non oltre/scadenza/termine ... <data>', 'fino al <data>',
    'dal <data> al <data>' (prende la seconda), purché nei dintorni si parli di domande.
    """
    t = normalizza(testo).replace("\n", " ")
    for rx in _REGOLE_SCAD:
        for m in rx.finditer(t):
            if not _CONTESTO.search(t[max(0, m.start() - 300): m.end() + 100]):
                continue
            d = _RX_DATA.search(m.group(1))
            iso = _data_iso(d) if d else None
            if iso:
                return iso
    return None


_NUM_PAROLE = {"uno": 1, "un": 1, "due": 2, "tre": 3, "quattro": 4, "cinque": 5, "sei": 6, "sette": 7,
               "otto": 8, "nove": 9, "dieci": 10, "undici": 11, "dodici": 12, "tredici": 13,
               "quattordici": 14, "quindici": 15, "venti": 20, "trenta": 30}
_RX_NUM = re.compile(
    r"(?:n\.?\s*|numero\s+)?(\d{1,4}|" + "|".join(_NUM_PAROLE) + r")\s*(?:\(\w+\)\s*)?"
    r"(?:nuovi\s+|ulteriori\s+)?(posteggi|posteggio|concessioni|chioschi|stalli|edicol[ae]|banchi|piazzole)", re.I)


_RX_NUM_DOPO = re.compile(r"\bposteggi\s+n\.?\s*(\d{1,3})\b", re.I)


def estrai_numero(testo):
    """Numero di posteggi messi a bando o None.

    1) primo 'N posteggi' / 'n. N posteggi' / 'tre posteggi' (anche concessioni, chioschi, stalli);
    2) altrimenti somma dei 'Posteggi n. N' (plurale = quantità; 'posteggio n. 12' è un identificativo).
    """
    t = normalizza(testo).replace("\n", " ")
    for m in _RX_NUM.finditer(t):
        v = m.group(1).lower()
        n = int(v) if v.isdigit() else _NUM_PAROLE.get(v)
        if n and 0 < n < 2000 and not re.search(r"(art|comma|legge|l\.r|d\.lgs)\.?\s*$", t[max(0, m.start() - 12): m.start()], re.I):
            return n
    dopo = [int(x) for x in _RX_NUM_DOPO.findall(t)]
    if dopo:
        return sum(dopo)
    return None


def estrai_tipo(testo):
    """Tipo prevalente: spunta, edicola, chiosco, fiera, isolato, mercato (in quest'ordine di priorità)."""
    t = normalizza(testo).lower()
    if re.search(r"spunt", t[:3000]):
        return "spunta"
    if re.search(r"edicol", t[:3000]):
        return "edicola"
    if re.search(r"chiosc", t[:3000]):
        return "chiosco"
    if re.search(r"posteggi[o]? isolat|fuori mercato|fuori dal mercato", t[:3000]):
        return "isolato"
    if re.search(r"\bfier[ae]\b|sagr[ae]|manifestazion|mercatin|evento", t[:3000]):
        return "fiera"
    if re.search(r"mercat", t[:3000]):
        return "mercato"
    return None
