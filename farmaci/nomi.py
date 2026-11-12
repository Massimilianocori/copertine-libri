"""Regole sui nomi usate da genera.py, verifica.py e raccolta/domanda.py (una sola definizione).

- di_fantasia(farmaco, pa): il nome commerciale NON comincia con il nome del principio attivo (es. AUGMENTIN per
  amoxicillina + acido clavulanico). È una regola sul nome, non dice chi ha inventato il farmaco: la pagina lo spiega.
- marchio(farmaco): la prima parola del nome commerciale, in minuscolo (per le ricerche e per i titoli).
- slug(pa): indirizzo della pagina del principio attivo.
"""
import re
import unicodedata


def _parole(s):
    s = unicodedata.normalize("NFD", s.upper())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.findall(r"[A-Z0-9]+", s)


def di_fantasia(farmaco, pa):
    w = _parole(farmaco)
    if not w:
        return False
    radici = {p[:5] for p in _parole(pa) if len(p) >= 4}
    return w[0][:5] not in radici


def marchio(farmaco):
    return _parole(farmaco)[0].lower()


def pa_ricerca(pa):
    return re.sub(r"\s+", " ", pa.lower().replace("+", " ")).strip()


def slug(testo):
    s = unicodedata.normalize("NFD", testo.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")
