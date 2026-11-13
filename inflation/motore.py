"""Motore di riferimento del calcolatore (Python). stile.MOTORE_JS è la copia per il browser, con le stesse regole:

    valore = importo × indice(arrivo) / indice(partenza)

dove indice(anno) è la media annua pubblicata e indice(anno, mese) l'indice mensile pubblicato. Per la Germania, se la
partenza è prima del 2002 l'importo può essere in D-Mark: si divide per 1,95583 quando l'arrivo è dal 2002 in poi
(e si moltiplica nel caso opposto). verifica.py confronta questo motore con il JS pubblicato su migliaia di casi.
"""
DM_PER_EURO = 1.95583
ANNO_EURO = 2002


def compatta(s):
    """Serie -> formato compatto per il browser: {a0, a: [...], m0: [anno, mese], m: [... null], x: {"AAAA-MM": motivo}}."""
    anni = sorted(s["annuale"])
    mesi = sorted(set(s["mensile"]) | set(s.get("mancanti", {})))
    a0, m0 = anni[0], mesi[0]
    a = [s["annuale"].get(y) for y in range(a0, anni[-1] + 1)]
    m, (y, mm) = [], m0
    while (y, mm) <= mesi[-1]:
        m.append(s["mensile"].get((y, mm)))
        mm += 1
        if mm == 13:
            y, mm = y + 1, 1
    return {"a0": a0, "a": a, "m0": list(m0), "m": m, "x": {f"{k[0]}-{k[1]:02d}": v for k, v in s.get("mancanti", {}).items()}}


def indice(c, anno, mese=None):
    """Indice da una serie compatta; None se non pubblicato."""
    if mese:
        i = (anno - c["m0"][0]) * 12 + (mese - c["m0"][1])
        return c["m"][i] if 0 <= i < len(c["m"]) else None
    i = anno - c["a0"]
    return c["a"][i] if 0 <= i < len(c["a"]) else None


def fattore_valuta(da_anno, a_anno, in_dm):
    """Germania: conversione D-Mark/euro. in_dm = l'importo di partenza è in D-Mark (solo se da_anno < 2002)."""
    da_dm = in_dm and da_anno < ANNO_EURO
    a_dm = a_anno < ANNO_EURO
    if da_dm and not a_dm:
        return 1 / DM_PER_EURO
    if not da_dm and a_dm:
        return DM_PER_EURO
    return 1.0


def calcola(c, importo, da, a, valuta=None):
    """da, a = (anno, mese o None). valuta: None (USA, Regno Unito) oppure True/False = importo in D-Mark.
    Restituisce un dizionario con valore, indici, variazione cumulata e media annua, oppure None se manca un indice."""
    i0, i1 = indice(c, *da), indice(c, *a)
    if not i0 or not i1 or importo is None or importo < 0:
        return None
    f = fattore_valuta(da[0], a[0], valuta) if valuta is not None else 1.0
    t0 = da[0] + ((da[1] - 0.5) / 12 if da[1] else 0.5)
    t1 = a[0] + ((a[1] - 0.5) / 12 if a[1] else 0.5)
    anni = t1 - t0
    rapporto = i1 / i0
    media = rapporto ** (1 / anni) - 1 if abs(anni) >= 1 else None
    return {"valore": importo * rapporto * f, "i0": i0, "i1": i1, "rapporto": rapporto, "cumulata": rapporto - 1,
            "media": media, "anni": anni, "fattore_valuta": f}


def tasso_annuo(c, anno):
    """Variazione della media annua rispetto all'anno prima (in frazione), None se manca un anno."""
    i0, i1 = indice(c, anno - 1), indice(c, anno)
    return i1 / i0 - 1 if i0 and i1 else None


def tasso_dicembre(c, anno):
    """Variazione dicembre su dicembre."""
    i0, i1 = indice(c, anno - 1, 12), indice(c, anno, 12)
    return i1 / i0 - 1 if i0 and i1 else None


def tasso_12_mesi(c, anno, mese):
    i0, i1 = indice(c, anno - 1, mese), indice(c, anno, mese)
    return i1 / i0 - 1 if i0 and i1 else None
