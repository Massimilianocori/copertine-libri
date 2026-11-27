"""Regole comuni per le pagine «Sciopero <azienda>» e per le pagine dei giorni di sciopero nazionale.

Solo logica sui dati, nessun HTML: lo usano genera.py (campi az/az_gen di ogni sciopero, pagine in inglese),
pagine_aziende.py (pagine) e verifica.py (controlli). Dati: dati/aziende.json, dati/fasce.json.

- nominate(s): aziende nominate dal registro nello sciopero s (colonna «categoria»; la nota conta solo se non parla di
  esclusioni). Il nome da solo non basta: «ATM» è anche l'azienda di Messina, «AMAT» anche quella di Taranto, per questo
  ogni azienda locale ha le sue regioni.
- generici(...): aziende che lo sciopero può riguardare senza nominarle (sciopero generale, di tutto il settore, della
  rete ferroviaria, del controllo del traffico aereo) nel loro territorio.
- date_nazionali(voci, oggi): giorni con uno sciopero nazionale del trasporto passeggeri che hanno una pagina propria:
  dal giorno di partenza delle pagine (PRIMA_DATA) fino a 30 giorni da oggi. I giorni passati restano, come le pagine
  dei mesi: la pagina dice che lo sciopero è concluso.
"""
import json
import re
from datetime import date, timedelta
from pathlib import Path

DATI = Path(__file__).resolve().parent / "dati"
AZIENDE = json.loads((DATI / "aziende.json").read_text(encoding="utf-8"))["aziende"]
FASCE = json.loads((DATI / "fasce.json").read_text(encoding="utf-8"))["fasce"]
PER_SLUG = {a["slug"]: a for a in AZIENDE}

PRIMA_DATA = "2026-11-27"   # giorno in cui nascono le pagine per data: nessuna pagina per scioperi precedenti
GIORNI_AVANTI = 30          # pagine per data: scioperi nazionali entro 30 giorni; frase «nessuno sciopero nei prossimi 30 giorni»
PASSEGGERI = ("trains", "flights", "local-transport", "ferries", "taxis")
MESI_IT = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre",
           "novembre", "dicembre"]
MESI_EN = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november",
           "december"]

# Scioperi di settore che non nominano un'azienda sola ma tutto il comparto o la rete
TUTTO_SETTORE = r"SETTORE|COMPARTO|CATEGORIE|TUTT[EI]|AZIENDE|IMPRESE|AUTOFERROTRANVIER"
TUTTI_I_TRENI = r"ATTIVIT\S* FERROVIARI"
RETE_RFI = r"\bRFI\b|RETE FERROVIARIA|GRUPPO FS|\bFSI\b|FERROVIE DELLO STATO"  # solo per chi viaggia sulla rete RFI ("rete_rfi")
RETE_AEREI = r"\bENAV\b|TECHNO SKY|CONTROLLO DEL TRAFFICO"
SERVIZI_AEROPORTO = r"HANDLING|SECURITY|SICUREZZA|SICURITALIA|TOSCANA AEROPORTI|AEROPORTI DI ROMA|\bADR\b|\bSEA\b|GESTIONE AEROPORT"
STELLE = [(r"TPL|TRASPORTO PUBBLICO", "local-transport"), (r"FERROV", "trains"), (r"AERE", "flights")]


def _in_regione(a, regione):
    return not a["regioni"] or regione in a["regioni"] or regione.strip().upper() == "ITALIA"


def nominate(s):
    """Slug delle aziende nominate dal registro nello sciopero s (voce di dati/scioperi.json)."""
    cat = s["categoria"].upper()
    nota = s.get("note", "").upper()
    if "ESCLUS" in nota or "REVOCAT" in nota:
        nota = ""
    return [a["slug"] for a in AZIENDE
            if _in_regione(a, s["regione"]) and (re.search(a["re"], cat) or (nota and re.search(a["re"], nota)))]


def _territorio(a, s, ambito):
    """Lo sciopero copre il territorio dell'azienda?"""
    reg, prov = s["regione"], s["provincia"].strip()
    nazionale = reg.strip().upper() == "ITALIA"
    tutta = prov.upper() in ("TUTTE", "")
    if not a["regione"]:  # azienda nazionale: scioperi nazionali o di una regione intera (per gli aerei anche di un aeroporto)
        return ambito in ("national", "regional") or ("flights" in a["settori"] and ambito == "airport")
    return nazionale or (reg == a["regione"] and (tutta or not a["province"] or prov in a["province"]))


def generici(s, settori, ambito, gia):
    """Slug delle aziende che lo sciopero può riguardare senza nominarle. settori e ambito sono quelli calcolati da
    leggi() in genera.py (le esclusioni scritte nella nota sono già tolte); gia = aziende nominate."""
    cat = s["categoria"].upper()
    generale = s["settore"] in ("Generale", "Plurisettoriale")
    if "Appalti ferroviari" in (s["settore"], s.get("settore_cgsse")):
        return []
    # «*TPL ...» con la nota che comincia per asterisco: quella parte vale solo per le aziende elencate nella nota
    solo_elencate = set()
    if s.get("note", "").lstrip().startswith("*"):
        for pezzo in re.findall(r"\*\s*([^;/*]{2,40})", s["modalita"].upper()):
            solo_elencate.update(slug for rx, slug in STELLE if re.search(rx, pezzo))
    out = []
    for a in AZIENDE:
        if a["slug"] in gia or not _territorio(a, s, ambito):
            continue
        comuni = [x for x in a["settori"] if x in settori and x not in solo_elencate]
        if not comuni:
            continue
        if generale:
            out.append(a["slug"])
        elif "trains" in comuni and s["settore"] == "Ferroviario" and (
                re.search(TUTTI_I_TRENI + "|" + TUTTO_SETTORE, cat) or (a.get("rete_rfi") and re.search(RETE_RFI, cat))):
            out.append(a["slug"])
        elif "local-transport" in comuni and s["settore"] == "Trasporto pubblico locale" and re.search(TUTTO_SETTORE, cat):
            out.append(a["slug"])
        elif "flights" in comuni and s["settore"] == "Aereo" and re.search(
                RETE_AEREI + "|" + SERVIZI_AEROPORTO + "|" + TUTTO_SETTORE, cat) and "CARGO" not in cat:
            out.append(a["slug"])
    return out


# ---------------------------------------------------------------- pagine per data
def slug_data_it(iso):
    x = date.fromisoformat(iso)
    return f"sciopero-{x.day}-{MESI_IT[x.month - 1]}-{x.year}"


def slug_data_en(iso):
    x = date.fromisoformat(iso)
    return f"strike-{x.day}-{MESI_EN[x.month - 1]}-{x.year}"


def _da_slug(t, prefisso, mesi):
    m = re.fullmatch(prefisso + r"-(\d{1,2})-([a-z]+)-(\d{4})", t)
    if not m or m.group(2) not in mesi:
        return None
    try:
        return date(int(m.group(3)), mesi.index(m.group(2)) + 1, int(m.group(1))).isoformat()
    except ValueError:
        return None


def data_da_slug_it(t):
    return _da_slug(t, "sciopero", MESI_IT)


def data_da_slug_en(t):
    return _da_slug(t, "strike", MESI_EN)


def nazionale_passeggeri(v):
    # Gli scioperi degli appalti ferroviari (ditte in appalto) non fermano i treni: niente pagina per data
    return v["ambito"] == "national" and v["settore_it"] != "Appalti ferroviari" and any(x in PASSEGGERI for x in v["settori"])


def date_nazionali(voci, oggi):
    """Giorni (ISO) con una pagina propria, in ordine."""
    limite = (oggi + timedelta(days=GIORNI_AVANTI)).isoformat()
    return sorted({v["inizio"] for v in voci if nazionale_passeggeri(v) and PRIMA_DATA <= v["inizio"] <= limite})


def del_giorno(voci, iso):
    return [v for v in voci if v["inizio"] <= iso <= v["fine"]]


def attivo(v):
    return v["stato"] not in ("revocato", "rimosso dal registro")


def firma(lista):
    """Impronta di un elenco di scioperi, uguale a firma() nel JS: se quella calcolata nel browser con i dati più
    recenti è diversa, la frase di risposta scritta alla generazione viene nascosta («i dati sono cambiati»)."""
    return ";".join(f'{v["id"]}|{v["inizio"]}|{v["fine"]}|{"in programma" if v["stato"] == "concluso" else v["stato"]}|{v["ore"]}'
                    for v in lista)


# ---------------------------------------------------------------- fasce scritte dalle aziende
def fasce_azienda(slug, oggi):
    """Citazioni da mostrare nella pagina dell'azienda: regole stabili e avvisi per scioperi non ancora passati."""
    return [f for f in FASCE if f["azienda"] == slug and (not f["data"] or f["data"] >= oggi.isoformat())]


def fasce_giorno(iso):
    return [f for f in FASCE if f["data"] == iso]
